"""
EduBoost V2 Load Test — Locust

Run against local Docker Compose stack:
    docker-compose up -d
    locust -f locust/locustfile.py --host=http://localhost:8000

Run against staging/production (DO NOT run load tests without permission):
    locust -f locust/locustfile.py --host=https://api.eduboost.co.za

For distributed load (multiple workers):
    locust -f locust/locustfile.py --master
    locust -f locust/locustfile.py --worker --master-host=<master-ip>

Target Metrics:
- 500 concurrent users
- p50 < 500ms
- p95 < 2s
- Error rate < 1%
"""

import random
import string
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner

# ── Test Configuration ───────────────────────────────────────────────────────

API_BASE = "/api/v2"
TEST_LEARNER_EMAIL = f"loadtest_{''.join(random.choices(string.ascii_lowercase, k=8))}@test.za"


# ── Helper Functions ─────────────────────────────────────────────────────────

def random_grade():
    return random.choice([4, 5, 6, 7])


def random_subject():
    return random.choice(["mathematics", "english", "afrikaans", "natural_sciences"])


def random_topic():
    return random.choice(["algebra", "geometry", "fractions", "reading", "writing"])


# ── Learner User Scenario ───────────────────────────────────────────────────

class LearnerUser(HttpUser):
    """Simulates a learner completing a full journey: login → diagnostic → lesson"""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    token = None

    def on_start(self):
        """Called when a simulated user starts. Register + login."""
        # Register a new learner (or use existing test account)
        email = f"learner_{random.randint(1000, 9999)}@test.za"
        password = "TestPassword123!"

        register_resp = self.client.post(
            f"{API_BASE}/auth/register",
            json={
                "email": email,
                "password": password,
                "password_confirm": password,
                "role": "learner",
                "first_name": "Load",
                "last_name": "Test",
            },
            catch_response=True,
        )

        if register_resp.status_code in (200, 201):
            register_resp.success()
            self.token = register_resp.json().get("access_token")
        elif register_resp.status_code == 409:  # Already exists
            register_resp.success()
            # Try to login
            login_resp = self.client.post(
                f"{API_BASE}/auth/login",
                json={"email": email, "password": password},
                catch_response=True,
            )
            if login_resp.status_code == 200:
                self.token = login_resp.json().get("access_token")
                login_resp.success()
            else:
                login_resp.failure(f"Login failed: {login_resp.status_code}")
        else:
            register_resp.failure(f"Registration failed: {register_resp.status_code}")

    @task(3)
    def get_diagnostics(self):
        """View available diagnostic assessments"""
        if not self.token:
            return

        self.client.get(
            f"{API_BASE}/diagnostics",
            headers={"Authorization": f"Bearer {self.token}"},
            name="/diagnostics [GET]",
        )

    @task(2)
    def start_diagnostic_session(self):
        """Start a new diagnostic session"""
        if not self.token:
            return

        self.client.post(
            f"{API_BASE}/diagnostics/sessions",
            json={"subject": "mathematics", "grade": random_grade()},
            headers={"Authorization": f"Bearer {self.token}"},
            name="/diagnostics/sessions [POST]",
        )

    @task(5)
    def get_study_plan(self):
        """View study plan (most common read operation)"""
        if not self.token:
            return

        self.client.get(
            f"{API_BASE}/study-plans",
            headers={"Authorization": f"Bearer {self.token}"},
            name="/study-plans [GET]",
        )

    @task(2)
    def request_lesson_generation(self):
        """Request a new lesson (async job)"""
        if not self.token:
            return

        with self.client.post(
            f"{API_BASE}/lessons/generate",
            json={
                "learner_id": "00000000-0000-0000-0000-000000000001",  # Use existing test learner
                "subject": random_subject(),
                "topic": random_topic(),
                "language": "en",
            },
            headers={"Authorization": f"Bearer {self.token}"},
            catch_response=True,
            name="/lessons/generate [POST]",
        ) as resp:
            if resp.status_code == 202:  # Accepted (queued)
                resp.success()
            elif resp.status_code == 429:  # Rate limited
                resp.failure("Rate limited")
            else:
                resp.failure(f"Unexpected: {resp.status_code}")


# ── Parent User Scenario ───────────────────────────────────────────────────

class ParentUser(HttpUser):
    """Simulates a parent/guardian checking learner progress"""

    wait_time = between(2, 5)

    def on_start(self):
        email = "parent@test.za"
        password = "TestPassword123!"

        with self.client.post(
            f"{API_BASE}/auth/login",
            json={"email": email, "password": password},
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                self.token = resp.json().get("access_token")
                resp.success()
            else:
                resp.failure(f"Parent login failed: {resp.status_code}")
                self.token = None

    @task(3)
    def get_learners(self):
        """View linked learners"""
        if not self.token:
            return
        self.client.get(
            f"{API_BASE}/learners",
            headers={"Authorization": f"Bearer {self.token}"},
            name="/learners [GET]",
        )

    @task(2)
    def get_consent_status(self):
        """Check consent status for linked learners"""
        if not self.token:
            return
        self.client.get(
            f"{API_BASE}/consent/status",
            headers={"Authorization": f"Bearer {self.token}"},
            name="/consent/status [GET]",
        )


# ── Anonymous User Scenario ───────────────────────────────────────────────

class AnonymousUser(HttpUser):
    """Simulates unauthenticated users hitting public endpoints"""

    wait_time = between(1, 2)

    @task(10)
    def health_check(self):
        """Public health endpoint (no auth)"""
        self.client.get("/health", name="/health [GET]")

    @task(5)
    def openapi_docs(self):
        """API documentation access"""
        self.client.get("/docs", name="/docs [GET]")

    @task(2)
    def openapi_json(self):
        """OpenAPI schema"""
        self.client.get("/openapi.json", name="/openapi.json [GET]")


# ── Events & Reporting ─────────────────────────────────────────────────────

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print(f"Load test starting against {environment.host}")
    if isinstance(environment.runner, MasterRunner):
        print("Running in distributed mode")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("Load test complete")
    print(f"Total requests: {environment.stats.total.num_requests}")
    print(f"Total failures: {environment.stats.total.num_failures}")