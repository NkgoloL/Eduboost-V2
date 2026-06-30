"""Phase 4 IRT calibration, intervention, and rewrite governance."""
from __future__ import annotations

import hashlib
import json
import math
import uuid
from collections import Counter, defaultdict
from datetime import UTC, datetime
from typing import Any, Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.metrics import (
    irt_answer_position_bias,
    irt_calibration_runs_total,
    irt_item_interventions_total,
    irt_rewrite_requests_total,
)
from app.domain.irt_quality_schemas import (
    IRTCalibrationDecision,
    IRTCalibrationMetrics,
    IRTCalibrationObservation,
    IRTInterventionAction,
    IRTQualityPolicy,
    IRTQualityState,
)
from app.models.content_factory import (
    ContentArtifactStatus,
    ContentArtifactType,
    ContentGenerationArtifact,
    ContentLayer,
)
from app.models.diagnostic_item import DiagnosticItem, ReviewStatusEnum
from app.models.item_exposure import ItemExposure
from app.models.irt_quality import IRTCalibrationEvent, IRTCalibrationRun


class IRTQualityError(RuntimeError):
    pass


class IRTQualityConflict(IRTQualityError):
    pass


def _sigmoid(value: float) -> float:
    value = max(-35.0, min(35.0, value))
    return 1.0 / (1.0 + math.exp(-value))


def fit_two_parameter_logistic(
    observations: Sequence[IRTCalibrationObservation],
    *,
    initial_a: float = 1.0,
    initial_b: float = 0.0,
    guessing_c: float = 0.25,
    iterations: int = 300,
) -> tuple[float, float, float, bool]:
    """Fit a bounded 2PL curve using deterministic gradient ascent.

    Ability is a session-rest-score proxy supplied by the caller. Guessing is
    fixed to the item's approved value; only discrimination and difficulty are
    fitted. This routine intentionally has no random component, making evidence
    reproducible across CI and audit runs.
    """

    if not observations:
        return initial_a, initial_b, 1.0, False

    a = max(0.05, min(3.0, float(initial_a)))
    b = max(-3.0, min(3.0, float(initial_b)))
    d = 1.7
    converged = False
    previous_loss: float | None = None

    for step in range(iterations):
        grad_a = 0.0
        grad_b = 0.0
        loss = 0.0
        for observation in observations:
            logistic = _sigmoid(d * a * (observation.ability_proxy - b))
            probability = guessing_c + (1.0 - guessing_c) * logistic
            probability = max(1e-6, min(1.0 - 1e-6, probability))
            target = 1.0 if observation.is_correct else 0.0
            error = target - probability
            # Stable approximate gradients for the fixed-guessing 3PL form.
            adjustment = (1.0 - guessing_c) * logistic * (1.0 - logistic)
            score = error * adjustment / max(probability * (1.0 - probability), 1e-6)
            grad_a += score * d * (observation.ability_proxy - b)
            grad_b += score * (-d * a)
            loss -= target * math.log(probability) + (1.0 - target) * math.log(1.0 - probability)

        scale = 1.0 / len(observations)
        learning_rate = 0.035 / (1.0 + step / 100.0)
        a = max(0.05, min(3.0, a + learning_rate * grad_a * scale))
        b = max(-3.0, min(3.0, b + learning_rate * grad_b * scale))
        mean_loss = loss * scale
        if previous_loss is not None and abs(previous_loss - mean_loss) < 1e-8:
            converged = True
            break
        previous_loss = mean_loss

    squared_errors = []
    for observation in observations:
        p = guessing_c + (1.0 - guessing_c) * _sigmoid(
            d * a * (observation.ability_proxy - b)
        )
        target = 1.0 if observation.is_correct else 0.0
        squared_errors.append((target - p) ** 2)
    rmse = math.sqrt(sum(squared_errors) / len(squared_errors))
    return round(a, 4), round(b, 4), round(rmse, 4), converged


def decide_intervention(
    metrics: IRTCalibrationMetrics,
    *,
    previous_state: IRTQualityState,
    previous_strikes: int,
    policy: IRTQualityPolicy,
    override_active: bool = False,
) -> IRTCalibrationDecision:
    if not metrics.data_quality_passed:
        return IRTCalibrationDecision(
            previous_state=previous_state,
            next_state=previous_state,
            action=IRTInterventionAction.NONE,
            reason="insufficient_or_invalid_calibration_data: " + ", ".join(metrics.data_quality_reasons),
            strike_count=previous_strikes,
        )

    if override_active:
        return IRTCalibrationDecision(
            previous_state=previous_state,
            next_state=previous_state,
            action=IRTInterventionAction.NONE,
            reason="active manual override; automated intervention suppressed",
            strike_count=previous_strikes,
        )

    catastrophic = (
        metrics.discrimination_a <= policy.quarantine_discrimination_max
        or metrics.fit_rmse >= policy.quarantine_fit_rmse
        or metrics.accuracy <= policy.min_acceptable_accuracy
        or metrics.accuracy >= policy.max_acceptable_accuracy
    )
    weak = (
        metrics.discrimination_a < policy.monitor_discrimination_min
        or metrics.fit_rmse > policy.max_fit_rmse
    )
    monitor = metrics.discrimination_a < policy.healthy_discrimination_min

    if catastrophic:
        strikes = previous_strikes + 1
        if strikes >= policy.retire_after_strikes:
            return IRTCalibrationDecision(
                previous_state=previous_state,
                next_state=IRTQualityState.REWRITE_REVIEW,
                action=IRTInterventionAction.RETIRE,
                reason="persistent catastrophic calibration failure; retire and create governed rewrite",
                strike_count=strikes,
                create_rewrite=True,
            )
        return IRTCalibrationDecision(
            previous_state=previous_state,
            next_state=IRTQualityState.QUARANTINED,
            action=IRTInterventionAction.QUARANTINE,
            reason="catastrophic calibration threshold breached",
            strike_count=strikes,
        )

    if weak:
        return IRTCalibrationDecision(
            previous_state=previous_state,
            next_state=IRTQualityState.REVIEW_REQUIRED,
            action=IRTInterventionAction.REQUIRE_REVIEW,
            reason="weak discrimination or model fit requires educator/statistical review",
            strike_count=previous_strikes + 1,
        )

    if monitor:
        return IRTCalibrationDecision(
            previous_state=previous_state,
            next_state=IRTQualityState.MONITOR,
            action=IRTInterventionAction.MONITOR,
            reason="item is serviceable but below the healthy discrimination threshold",
            strike_count=max(0, previous_strikes - 1),
            update_parameters=True,
        )

    return IRTCalibrationDecision(
        previous_state=previous_state,
        next_state=IRTQualityState.HEALTHY,
        action=IRTInterventionAction.RETAIN,
        reason="item meets the approved calibration policy",
        strike_count=0,
        update_parameters=True,
    )


def correct_answer_position(item: DiagnosticItem) -> int | None:
    options = item.options or []
    for index, option in enumerate(options):
        if isinstance(option, dict):
            value = option.get("value", option.get("text", option.get("label")))
        else:
            value = option
        if str(value) == str(item.answer_key):
            return index
    return None


def answer_position_distribution(items: Iterable[DiagnosticItem]) -> dict[str, Any]:
    positions = [position for item in items if (position := correct_answer_position(item)) is not None]
    counts = Counter(positions)
    total = len(positions)
    shares = {str(position): count / total for position, count in sorted(counts.items())} if total else {}
    return {
        "sample_size": total,
        "counts": dict(counts),
        "shares": shares,
        "max_share": max(shares.values(), default=0.0),
    }


class IRTQualityService:
    def __init__(self, policy: IRTQualityPolicy | None = None) -> None:
        self.policy = policy or IRTQualityPolicy()

    async def run(
        self,
        db: AsyncSession,
        *,
        dry_run: bool = False,
        item_ids: Sequence[uuid.UUID] | None = None,
        idempotency_key: str,
        actor_id: str | None = None,
    ) -> dict[str, Any]:
        existing = await db.scalar(
            select(IRTCalibrationRun).where(IRTCalibrationRun.idempotency_key == idempotency_key)
        )
        if existing is not None:
            return {"run_id": str(existing.run_id), "status": existing.status, **(existing.summary or {})}

        run = IRTCalibrationRun(
            idempotency_key=idempotency_key,
            status="running",
            dry_run=dry_run,
            model_version=self.policy.model_version,
            policy_version=self.policy.policy_version,
            requested_by=actor_id,
            summary={},
        )
        db.add(run)
        await db.commit()
        run = await db.get(IRTCalibrationRun, run.run_id)
        if run is None:  # pragma: no cover - defensive persistence check
            raise IRTQualityError("calibration run could not be reloaded")

        query = select(DiagnosticItem).where(DiagnosticItem.review_status == ReviewStatusEnum.APPROVED)
        if item_ids:
            query = query.where(DiagnosticItem.item_id.in_(list(item_ids)))
        items = list((await db.scalars(query.order_by(DiagnosticItem.item_id))).all())

        position = answer_position_distribution(items)
        irt_answer_position_bias.set(float(position["max_share"]))
        summary: dict[str, Any] = {
            "evaluated": 0,
            "insufficient_data": 0,
            "healthy": 0,
            "monitor": 0,
            "review_required": 0,
            "quarantined": 0,
            "retired": 0,
            "rewrites_created": 0,
            "answer_position": position,
            "answer_position_bias_detected": (
                position["sample_size"] >= 20
                and position["max_share"] > self.policy.max_correct_position_share
            ),
        }

        try:
            for item in items:
                metrics = await self._calibrate_item(db, item)
                previous_state = IRTQualityState(str(getattr(item, "irt_quality_state", "uncalibrated")))
                override_until = getattr(item, "irt_manual_override_until", None)
                override_reason = getattr(item, "irt_manual_override_reason", None)
                override_active = bool(override_reason) and (
                    override_until is None or override_until > datetime.now(UTC)
                )
                decision = decide_intervention(
                    metrics,
                    previous_state=previous_state,
                    previous_strikes=int(getattr(item, "irt_strike_count", 0) or 0),
                    policy=self.policy,
                    override_active=override_active,
                )

                summary["evaluated"] += 1
                if not metrics.data_quality_passed:
                    summary["insufficient_data"] += 1
                else:
                    summary_key = {
                        IRTQualityState.HEALTHY: "healthy",
                        IRTQualityState.MONITOR: "monitor",
                        IRTQualityState.REVIEW_REQUIRED: "review_required",
                        IRTQualityState.QUARANTINED: "quarantined",
                        IRTQualityState.REWRITE_REVIEW: "retired",
                    }.get(decision.next_state)
                    if summary_key is not None:
                        summary[summary_key] += 1

                rewrite_artifact_id: uuid.UUID | None = None
                if not dry_run:
                    if decision.create_rewrite:
                        rewrite_artifact_id = await self._create_rewrite_artifact(db, item, run.run_id, metrics)
                        summary["rewrites_created"] += 1
                    self._apply_decision(item, run.run_id, metrics, decision, rewrite_artifact_id)
                    db.add(
                        IRTCalibrationEvent(
                            run_id=run.run_id,
                            item_id=item.item_id,
                            previous_state=previous_state.value,
                            next_state=decision.next_state.value,
                            action=decision.action.value,
                            reason=decision.reason,
                            metrics=metrics.model_dump(mode="json"),
                            policy_version=self.policy.policy_version,
                            model_version=self.policy.model_version,
                            actor_id=actor_id or "irt-watchdog",
                        )
                    )
                irt_item_interventions_total.labels(action=decision.action.value).inc()

            if summary["answer_position_bias_detected"]:
                summary["policy_warning"] = (
                    "correct-answer position distribution exceeds the approved threshold; "
                    "no automatic option mutation was performed"
                )

            run.status = "completed"
            run.summary = summary
            run.finished_at = datetime.now(UTC)
            await db.commit()
            irt_calibration_runs_total.labels(status="completed").inc()
            return {"run_id": str(run.run_id), "status": run.status, **summary}
        except Exception as exc:
            await db.rollback()
            failed = await db.get(IRTCalibrationRun, run.run_id)
            if failed is not None:
                failed.status = "failed"
                failed.error = {"type": exc.__class__.__name__, "message": str(exc)}
                failed.finished_at = datetime.now(UTC)
                await db.commit()
            irt_calibration_runs_total.labels(status="failed").inc()
            raise

    async def _calibrate_item(self, db: AsyncSession, item: DiagnosticItem) -> IRTCalibrationMetrics:
        exposures = list(
            (
                await db.scalars(
                    select(ItemExposure)
                    .where(ItemExposure.item_id == item.item_id)
                    .order_by(ItemExposure.served_at.desc())
                    .limit(self.policy.max_observations_per_item)
                )
            ).all()
        )
        answered = [
            exposure for exposure in exposures
            if exposure.is_correct is not None and exposure.session_id is not None
        ]
        observations = await self._build_observations(db, answered)
        response_count = len(exposures)
        answered_ratio = len(answered) / response_count if response_count else 0.0
        unique_learners = len({observation.learner_id for observation in observations})
        session_count = len({observation.session_id for observation in observations})
        reasons: list[str] = []
        if len(observations) < self.policy.min_responses:
            reasons.append(f"responses<{self.policy.min_responses}")
        if unique_learners < self.policy.min_unique_learners:
            reasons.append(f"unique_learners<{self.policy.min_unique_learners}")
        if session_count < self.policy.min_sessions:
            reasons.append(f"sessions<{self.policy.min_sessions}")
        if answered_ratio < self.policy.min_answered_ratio:
            reasons.append(f"answered_ratio<{self.policy.min_answered_ratio}")

        accuracy = (
            sum(1 for observation in observations if observation.is_correct) / len(observations)
            if observations else 0.0
        )
        a, b, rmse, converged = fit_two_parameter_logistic(
            observations,
            initial_a=float(item.discrimination_a or 1.0),
            initial_b=float(item.difficulty_b or 0.0),
            guessing_c=float(item.guessing_c or 0.25),
        )
        return IRTCalibrationMetrics(
            response_count=len(observations),
            unique_learners=unique_learners,
            session_count=session_count,
            answered_ratio=answered_ratio,
            accuracy=accuracy,
            difficulty_b=b,
            discrimination_a=a,
            guessing_c=float(item.guessing_c or 0.25),
            fit_rmse=rmse,
            converged=converged,
            data_quality_passed=not reasons,
            data_quality_reasons=reasons,
        )

    async def _build_observations(
        self, db: AsyncSession, target_exposures: Sequence[ItemExposure]
    ) -> list[IRTCalibrationObservation]:
        session_ids = {exposure.session_id for exposure in target_exposures if exposure.session_id}
        if not session_ids:
            return []
        all_exposures = list(
            (
                await db.scalars(
                    select(ItemExposure).where(
                        ItemExposure.session_id.in_(session_ids),
                        ItemExposure.is_correct.is_not(None),
                    )
                )
            ).all()
        )
        by_session: dict[uuid.UUID, list[ItemExposure]] = defaultdict(list)
        for exposure in all_exposures:
            if exposure.session_id is not None:
                by_session[exposure.session_id].append(exposure)

        observations: list[IRTCalibrationObservation] = []
        for exposure in target_exposures:
            if exposure.session_id is None:
                continue
            peers = [candidate for candidate in by_session[exposure.session_id] if candidate.item_id != exposure.item_id]
            if len(peers) < 3:
                continue
            correct = sum(1 for peer in peers if peer.is_correct)
            smoothed = (correct + 0.5) / (len(peers) + 1.0)
            theta = math.log(smoothed / (1.0 - smoothed))
            observations.append(
                IRTCalibrationObservation(
                    learner_id=exposure.learner_id,
                    session_id=exposure.session_id,
                    ability_proxy=max(-3.0, min(3.0, theta)),
                    is_correct=bool(exposure.is_correct),
                )
            )
        return observations

    def _apply_decision(
        self,
        item: DiagnosticItem,
        run_id: uuid.UUID,
        metrics: IRTCalibrationMetrics,
        decision: IRTCalibrationDecision,
        rewrite_artifact_id: uuid.UUID | None,
    ) -> None:
        item.irt_quality_state = decision.next_state.value
        item.irt_model_version = self.policy.model_version
        item.irt_policy_version = self.policy.policy_version
        item.irt_response_count = metrics.response_count
        item.irt_unique_learners = metrics.unique_learners
        item.irt_strike_count = decision.strike_count
        item.irt_last_calibrated_at = datetime.now(UTC)
        item.irt_last_run_id = run_id
        item.irt_intervention_reason = decision.reason
        item.irt_rewrite_artifact_id = rewrite_artifact_id
        item.irt_row_version = int(getattr(item, "irt_row_version", 1) or 1) + 1

        if decision.update_parameters:
            current_a = float(item.discrimination_a or 1.0)
            current_b = float(item.difficulty_b or 0.0)
            step = self.policy.max_parameter_step
            item.discrimination_a = max(0.5, min(2.5, current_a + max(-step, min(step, metrics.discrimination_a - current_a))))
            item.difficulty_b = max(-3.0, min(3.0, current_b + max(-step, min(step, metrics.difficulty_b - current_b))))
        if decision.next_state in {IRTQualityState.QUARANTINED, IRTQualityState.REWRITE_REVIEW}:
            item.safety_passed = False
        if decision.next_state == IRTQualityState.REWRITE_REVIEW:
            item.review_status = ReviewStatusEnum.RETIRED

    async def _create_rewrite_artifact(
        self,
        db: AsyncSession,
        item: DiagnosticItem,
        run_id: uuid.UUID,
        metrics: IRTCalibrationMetrics,
    ) -> uuid.UUID:
        artifact_json = {
            "phase4_rewrite_request": True,
            "source_item_id": str(item.item_id),
            "original": {
                "stem": item.stem,
                "options": item.options,
                "answer_key": item.answer_key,
                "explanation": item.explanation,
                "caps_ref": item.caps_ref,
            },
            "calibration_metrics": metrics.model_dump(mode="json"),
            "instructions": (
                "Rewrite this item to address the calibration failure. Preserve CAPS alignment and source grounding. "
                "The rewritten artifact must complete Phase 3 educator consensus before publication."
            ),
        }
        canonical = json.dumps(artifact_json, sort_keys=True, separators=(",", ":"))
        artifact_hash = hashlib.sha256(f"{item.item_id}:{run_id}:{canonical}".encode()).hexdigest()
        artifact = ContentGenerationArtifact(
            scope_id=f"irt-rewrite:{item.grade}:{item.language.value}",
            content_layer=ContentLayer.DIAGNOSTIC_ITEMS,
            artifact_type=ContentArtifactType.DIAGNOSTIC_ITEM,
            caps_ref=item.caps_ref,
            grade=item.grade,
            subject_code=item.subject.value,
            language=item.language.value,
            status=ContentArtifactStatus.PENDING_REVIEW,
            artifact_json=artifact_json,
            artifact_hash=artifact_hash,
            schema_version="phase4-rewrite-v1",
            version_number=1,
            row_version=1,
            created_by_actor_id="irt-watchdog",
            approval_count=0,
            review_policy_version="phase3-v1",
            rubric_version="1.0",
            publication_eligible=False,
            provider="phase4-irt-watchdog",
            model=self.policy.model_version,
            prompt_version="phase4-rewrite-v1",
            safety_status="pending_review",
            answer_key_verified=False,
        )
        db.add(artifact)
        await db.flush()
        irt_rewrite_requests_total.inc()
        return artifact.artifact_id

    async def manual_override(
        self,
        db: AsyncSession,
        *,
        item_id: uuid.UUID,
        state: IRTQualityState,
        reason: str,
        expires_at: datetime | None,
        actor_id: str,
    ) -> DiagnosticItem:
        item = await db.scalar(
            select(DiagnosticItem).where(DiagnosticItem.item_id == item_id).with_for_update()
        )
        if item is None:
            raise LookupError(f"diagnostic item {item_id} not found")
        previous = str(item.irt_quality_state)
        item.irt_quality_state = state.value
        item.irt_manual_override_until = expires_at
        item.irt_manual_override_reason = reason
        item.irt_intervention_reason = f"manual override by {actor_id}: {reason}"
        item.irt_row_version += 1
        synthetic_run = IRTCalibrationRun(
            idempotency_key=f"manual:{item_id}:{uuid.uuid4()}",
            status="completed",
            dry_run=False,
            model_version=self.policy.model_version,
            policy_version=self.policy.policy_version,
            requested_by=actor_id,
            summary={"manual_override": True},
            finished_at=datetime.now(UTC),
        )
        db.add(synthetic_run)
        await db.flush()
        db.add(
            IRTCalibrationEvent(
                run_id=synthetic_run.run_id,
                item_id=item.item_id,
                previous_state=previous,
                next_state=state.value,
                action=IRTInterventionAction.MANUAL_OVERRIDE.value,
                reason=reason,
                metrics={},
                policy_version=self.policy.policy_version,
                model_version=self.policy.model_version,
                actor_id=actor_id,
            )
        )
        await db.commit()
        return item

    async def clear_override(self, db: AsyncSession, *, item_id: uuid.UUID, actor_id: str) -> DiagnosticItem:
        item = await db.scalar(
            select(DiagnosticItem).where(DiagnosticItem.item_id == item_id).with_for_update()
        )
        if item is None:
            raise LookupError(f"diagnostic item {item_id} not found")
        previous = str(item.irt_quality_state)
        item.irt_quality_state = IRTQualityState.UNCALIBRATED.value
        item.irt_manual_override_until = None
        item.irt_manual_override_reason = None
        item.irt_intervention_reason = f"manual override cleared by {actor_id}"
        item.irt_row_version += 1
        synthetic_run = IRTCalibrationRun(
            idempotency_key=f"clear:{item_id}:{uuid.uuid4()}", status="completed", dry_run=False,
            model_version=self.policy.model_version, policy_version=self.policy.policy_version,
            requested_by=actor_id, summary={"manual_override_cleared": True}, finished_at=datetime.now(UTC)
        )
        db.add(synthetic_run)
        await db.flush()
        db.add(
            IRTCalibrationEvent(
                run_id=synthetic_run.run_id, item_id=item.item_id, previous_state=previous,
                next_state=IRTQualityState.UNCALIBRATED.value,
                action=IRTInterventionAction.CLEAR_OVERRIDE.value,
                reason="manual override cleared", metrics={},
                policy_version=self.policy.policy_version, model_version=self.policy.model_version,
                actor_id=actor_id,
            )
        )
        await db.commit()
        return item
