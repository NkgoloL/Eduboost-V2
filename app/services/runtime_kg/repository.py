"""Async persistence repository for runtime KG tables."""
from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.runtime_kg import LearnerKGNodeState, RuntimeKGEdge, RuntimeKGEvent, RuntimeKGGraphLoad, RuntimeKGNode
from app.services.runtime_kg.loader import RuntimeKGLoader
from app.services.runtime_kg.schemas import LearnerKGNodeProjection, RuntimeKGGraphInput


class RuntimeKGRepository:
    """Repository boundary for runtime KG persistence.

    The repository is intentionally thin: validation and projection rules stay in
    services, while this class owns idempotent table writes and active-graph
    lookups.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.loader = RuntimeKGLoader()

    async def get_active_graph(self, *, graph_version: str | None = None) -> RuntimeKGGraphLoad | None:
        stmt = select(RuntimeKGGraphLoad).where(RuntimeKGGraphLoad.status == "active")
        if graph_version:
            stmt = stmt.where(RuntimeKGGraphLoad.graph_version == graph_version)
        result = await self.db.execute(stmt.order_by(RuntimeKGGraphLoad.loaded_at.desc()).limit(1))
        return result.scalar_one_or_none()

    async def load_graph_idempotent(self, graph: RuntimeKGGraphInput) -> RuntimeKGGraphLoad:
        plan = self.loader.plan(graph)
        existing = await self.db.execute(select(RuntimeKGGraphLoad).where(RuntimeKGGraphLoad.graph_version == graph.graph_version))
        graph_load = existing.scalar_one_or_none()
        if graph_load:
            return graph_load
        graph_load = RuntimeKGGraphLoad(
            graph_version=graph.graph_version,
            curriculum_code=graph.curriculum_code,
            grade=graph.grade,
            subject_code=graph.subject_code,
            source_ref=graph.source_ref,
            source_sha256=graph.source_sha256,
            node_count=plan.node_count,
            edge_count=plan.edge_count,
            status="staged",
            loaded_by=graph.loaded_by,
            metadata_json={**graph.metadata, "idempotency_key": plan.idempotency_key},
        )
        self.db.add(graph_load)
        await self.db.flush()
        nodes_by_code: dict[str, RuntimeKGNode] = {}
        for node in graph.nodes:
            model = RuntimeKGNode(
                graph_load_id=graph_load.id,
                stable_code=node.stable_code,
                node_type=node.node_type,
                label=node.label,
                curriculum_code=node.curriculum_code,
                grade=node.grade,
                subject_code=node.subject_code,
                strand=node.strand,
                topic=node.topic,
                mastery_weight=node.mastery_weight,
                properties_json=node.properties,
            )
            self.db.add(model)
            nodes_by_code[node.stable_code] = model
        await self.db.flush()
        for edge in graph.edges:
            self.db.add(
                RuntimeKGEdge(
                    graph_load_id=graph_load.id,
                    from_node_id=nodes_by_code[edge.from_stable_code].id,
                    to_node_id=nodes_by_code[edge.to_stable_code].id,
                    edge_type=edge.edge_type,
                    weight=edge.weight,
                    properties_json=edge.properties,
                )
            )
        self.db.add(RuntimeKGEvent(graph_load_id=graph_load.id, event_type="graph_loaded", source="runtime_kg_repository", payload_json={"graph_version": graph.graph_version}))
        await self.db.flush()
        return graph_load

    async def activate_graph(self, graph_version: str) -> RuntimeKGGraphLoad | None:
        graph = await self.db.scalar(select(RuntimeKGGraphLoad).where(RuntimeKGGraphLoad.graph_version == graph_version))
        if graph is None:
            return None
        await self.db.execute(update(RuntimeKGGraphLoad).where(RuntimeKGGraphLoad.status == "active").values(status="superseded"))
        graph.status = "active"
        self.db.add(RuntimeKGEvent(graph_load_id=graph.id, event_type="graph_activated", source="runtime_kg_repository", payload_json={"graph_version": graph_version}))
        await self.db.flush()
        return graph

    async def upsert_learner_projection(self, *, learner_id: str, graph_node_id, projection: LearnerKGNodeProjection) -> LearnerKGNodeState:
        existing = await self.db.scalar(
            select(LearnerKGNodeState).where(
                LearnerKGNodeState.learner_id == learner_id,
                LearnerKGNodeState.graph_node_id == graph_node_id,
            )
        )
        if existing is None:
            existing = LearnerKGNodeState(learner_id=learner_id, graph_node_id=graph_node_id)
            self.db.add(existing)
        existing.mastery_score = projection.mastery_score
        existing.confidence = projection.confidence
        existing.evidence_count = projection.evidence_count
        existing.gap_open = projection.gap_open
        existing.last_evidence_source = "runtime_kg_projection"
        await self.db.flush()
        return existing


    async def get_active_nodes(self, *, graph_version: str | None = None, subject_code: str | None = None) -> tuple[RuntimeKGGraphLoad, list[RuntimeKGNode]] | None:
        """Return the active graph and nodes for runtime read/projection paths."""

        graph = await self.get_active_graph(graph_version=graph_version)
        if graph is None:
            return None
        stmt = select(RuntimeKGNode).where(RuntimeKGNode.graph_load_id == graph.id)
        if subject_code:
            stmt = stmt.where(RuntimeKGNode.subject_code == subject_code)
        result = await self.db.execute(stmt.order_by(RuntimeKGNode.stable_code))
        return graph, list(result.scalars().all())

    async def project_and_persist_evidence(
        self,
        *,
        learner_id: str,
        subject_code: str,
        evidence,
        graph_version: str | None = None,
    ):
        """Project diagnostic evidence onto the active runtime graph and persist states."""

        active = await self.get_active_nodes(graph_version=graph_version, subject_code=subject_code)
        if active is None:
            return None
        graph, nodes = active
        from app.services.runtime_kg.schemas import RuntimeKGNodeInput
        from app.services.runtime_kg.service import RuntimeKGProjectionService

        node_inputs = [
            RuntimeKGNodeInput(
                stable_code=node.stable_code,
                label=node.label,
                node_type=node.node_type,
                curriculum_code=node.curriculum_code,
                grade=node.grade,
                subject_code=node.subject_code,
                strand=node.strand,
                topic=node.topic,
                mastery_weight=node.mastery_weight,
                properties=node.properties_json,
            )
            for node in nodes
        ]
        projection = RuntimeKGProjectionService().project_from_evidence(
            learner_id=learner_id,
            subject_code=subject_code,
            graph_version=graph.graph_version,
            nodes=node_inputs,
            evidence=list(evidence),
        )
        nodes_by_code = {node.stable_code: node for node in nodes}
        for projected in projection.nodes:
            node = nodes_by_code.get(projected.stable_code)
            if node is not None:
                await self.upsert_learner_projection(learner_id=learner_id, graph_node_id=node.id, projection=projected)
        self.db.add(
            RuntimeKGEvent(
                learner_id=learner_id,
                graph_load_id=graph.id,
                event_type="learner_projection_updated",
                source="runtime_kg_route_integration",
                payload_json={"graph_version": graph.graph_version, "subject_code": subject_code, "evidence_count": len(list(evidence))},
            )
        )
        await self.db.flush()
        return projection

    async def get_learner_gap_focus(
        self,
        *,
        learner_id: str,
        subject_code: str,
        graph_version: str | None = None,
        limit: int = 5,
    ) -> list[dict]:
        """Return graph-backed study-plan focus items from persisted learner node states."""

        active = await self.get_active_nodes(graph_version=graph_version, subject_code=subject_code)
        if active is None:
            return []
        graph, nodes = active
        node_ids = [node.id for node in nodes]
        if not node_ids:
            return []
        result = await self.db.execute(
            select(LearnerKGNodeState, RuntimeKGNode)
            .join(RuntimeKGNode, LearnerKGNodeState.graph_node_id == RuntimeKGNode.id)
            .where(
                LearnerKGNodeState.learner_id == learner_id,
                LearnerKGNodeState.graph_node_id.in_(node_ids),
                LearnerKGNodeState.gap_open == True,  # noqa: E712
            )
            .order_by(LearnerKGNodeState.mastery_score.asc(), LearnerKGNodeState.confidence.desc())
            .limit(limit)
        )
        return [
            {
                "stable_code": node.stable_code,
                "focus": node.topic or node.label,
                "mastery_score": state.mastery_score,
                "confidence": state.confidence,
                "graph_version": graph.graph_version,
                "recommended_action": "targeted_practice" if state.confidence >= 0.5 else "diagnose_prerequisite",
            }
            for state, node in result.all()
        ]

    async def record_rollback(self, *, learner_id: str | None, graph_version: str | None, reason: str) -> None:
        """Record a runtime-KG rollback/fallback event without disrupting legacy flow."""

        graph = await self.get_active_graph(graph_version=graph_version) if graph_version else None
        self.db.add(
            RuntimeKGEvent(
                learner_id=learner_id,
                graph_load_id=getattr(graph, "id", None),
                event_type="rollback_to_legacy",
                source="runtime_kg_route_integration",
                payload_json={"graph_version": graph_version, "reason": reason},
            )
        )
        await self.db.flush()
