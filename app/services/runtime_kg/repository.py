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
