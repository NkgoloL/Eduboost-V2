"""Idempotent runtime KG graph validation and load planning."""
from __future__ import annotations

from dataclasses import dataclass

from app.services.runtime_kg.schemas import RuntimeKGGraphInput


class RuntimeKGLoadError(ValueError):
    """Raised when a runtime KG load cannot be accepted."""


@dataclass(frozen=True)
class RuntimeKGLoadPlan:
    graph_version: str
    node_count: int
    edge_count: int
    stable_codes: tuple[str, ...]
    idempotency_key: str


class RuntimeKGLoader:
    """Validate graph-load payloads before persistence.

    This class is deliberately DB-free.  The repository persists a validated
    plan; the loader guarantees duplicate loads resolve to the same idempotency
    key and rejects malformed graph payloads before they can touch the database.
    """

    def plan(self, graph: RuntimeKGGraphInput) -> RuntimeKGLoadPlan:
        if not graph.graph_version.strip():
            raise RuntimeKGLoadError("graph_version is required")
        if len(graph.source_sha256) != 64:
            raise RuntimeKGLoadError("source_sha256 must be a 64 character SHA-256 hex digest")
        stable_codes = [node.stable_code.strip() for node in graph.nodes]
        if not stable_codes:
            raise RuntimeKGLoadError("at least one runtime KG node is required")
        if any(not code for code in stable_codes):
            raise RuntimeKGLoadError("node stable_code cannot be blank")
        if len(stable_codes) != len(set(stable_codes)):
            raise RuntimeKGLoadError("node stable_code values must be unique within a graph load")
        code_set = set(stable_codes)
        for edge in graph.edges:
            if edge.from_stable_code not in code_set or edge.to_stable_code not in code_set:
                raise RuntimeKGLoadError("all edges must reference nodes in the same graph load")
            if edge.from_stable_code == edge.to_stable_code:
                raise RuntimeKGLoadError("runtime KG self-edges are not allowed")
            if edge.weight < 0:
                raise RuntimeKGLoadError("edge weight must be non-negative")
        idempotency_key = f"{graph.graph_version}:{graph.source_sha256}:{len(graph.nodes)}:{len(graph.edges)}"
        return RuntimeKGLoadPlan(
            graph_version=graph.graph_version,
            node_count=len(graph.nodes),
            edge_count=len(graph.edges),
            stable_codes=tuple(sorted(stable_codes)),
            idempotency_key=idempotency_key,
        )
