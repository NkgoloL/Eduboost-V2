import re
from datetime import datetime

# Database configuration
db_config = {
    "host": "localhost",
    "user": "redmine",
    "password": "",
    "database": "redmine"
}

def parse_backend_report(content):
    entries = []
    # Match ### [YYYY-MM-DD] <Title> ... ---
    pattern = re.compile(r"### \[(.*?)\] (.*?)\n(.*?)(?=\n###|\n---|\Z)", re.DOTALL)
    for match in pattern.finditer(content):
        date_str, title, body = match.groups()
        entries.append({
            "date": date_str,
            "title": title,
            "body": body.strip(),
            "source": "audits/recommendations/Backend_Report.md"
        })
    return entries

def parse_functional_report(content):
    entries = []
    # Match ## Implementation #<N>: <Title> ... ---
    pattern = re.compile(r"## Implementation #(\d+): (.*?)\n(.*?)(?=\n## Implementation|\n---|\Z)", re.DOTALL)
    for match in pattern.finditer(content):
        impl_id, title, body = match.groups()
        # Find date inside body
        date_match = re.search(r"### Date: (.*?)\n", body)
        date_str = date_match.group(1) if date_match else "2026-04-26"
        entries.append({
            "date": date_str,
            "title": f"Implementation #{impl_id}: {title}",
            "body": body.strip(),
            "source": "audits/recommendations/Functional_Implementations_Report.md"
        })
    return entries

def get_issue_id(title, body):
    # Mapping logic based on keywords
    text = (title + " " + body).lower()
    if "gamification" in text or "badge" in text or "xp" in text:
        return 1
    if "parent" in text or "guardian" in text or "consent" in text:
        return 2
    if "diagnostic" in text or "irt" in text or "item bank" in text:
        return 3
    if "study plan" in text or "plan_tasks" in text:
        return 4
    if "orchestrator" in text:
        return 9
    if "schema" in text or "orm" in text or "migration" in text:
        return 8
    if "audit" in text or "fourth estate" in text:
        return 10
    if "lesson" in text or "catalog" in text:
        return 11
    if "frontend" in text or "onboarding" in text or "learner" in text:
        return 12
    return None

def main():
    with open("/home/nkgolol/Dev/SandBox/edo-boost-main/edo-boost-main/audits/recommendations/Backend_Report.md", "r") as f:
        backend_content = f.read()
    with open("/home/nkgolol/Dev/SandBox/edo-boost-main/edo-boost-main/audits/recommendations/Functional_Implementations_Report.md", "r") as f:
        functional_content = f.read()

    entries = parse_backend_report(backend_content) + parse_functional_report(functional_content)

    print("USE redmine;")
    for entry in entries:
        issue_id = get_issue_id(entry["title"], entry["body"])
        if not issue_id:
            continue

        notes = f"### {entry['title']}\n**Date**: {entry['date']}\n**Source**: {entry['source']}\n\n{entry['body']}"
        notes_escaped = notes.replace("'", "''").replace("\\", "\\\\")
        
        query = f"INSERT INTO journals (journalized_id, journalized_type, user_id, notes, created_on) VALUES ({issue_id}, 'Issue', 5, '{notes_escaped}', NOW());"
        print(query)

if __name__ == "__main__":
    main()
