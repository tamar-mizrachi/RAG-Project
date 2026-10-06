from dataclasses import dataclass, field
from typing import Any

try:
    from llama_index.core.workflow import (
        Workflow,
        StartEvent,
        StopEvent,
        Event,
        step,
    )
    LLAMAINDEX_WORKFLOW_AVAILABLE = True
except Exception:
    LLAMAINDEX_WORKFLOW_AVAILABLE = False

from .models import WorkflowResult
from .router import choose_route


@dataclass
class WorkflowState:
    query: str
    route: str = ""
    reason: str = ""
    evidence: list[Any] = field(default_factory=list)
    confidence: float = 0.0
    retry_count: int = 0


def _node_score(node) -> float:
    score = getattr(node, "score", None)
    try:
        return max(0.0, min(1.0, float(score))) if score is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


if LLAMAINDEX_WORKFLOW_AVAILABLE:
    class RetrievalEvent(Event):
        query: str
        route: str
        retry_count: int = 0


    class EvidenceEvent(Event):
        query: str
        route: str
        evidence: list
        confidence: float
        retry_count: int = 0


    class RAGWorkflow(Workflow):
        def __init__(self, semantic_searcher, structured_searcher, synthesizer, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.semantic_searcher = semantic_searcher
            self.structured_searcher = structured_searcher
            self.synthesizer = synthesizer

        @step
        async def start(self, ev: StartEvent) -> RetrievalEvent:
            query = str(getattr(ev, "query", "")).strip()
            if not query:
                raise ValueError("Question cannot be empty.")
            decision = choose_route(query)
            return RetrievalEvent(
                query=query,
                route=decision.route,
            )

        @step
        async def retrieve(self, ev: RetrievalEvent) -> EvidenceEvent:
            if ev.route == "structured":
                evidence = self.structured_searcher.search(ev.query)
                confidence = 1.0 if evidence else 0.0
            else:
                evidence = self.semantic_searcher.retrieve(ev.query)
                confidence = (
                    sum(_node_score(x) for x in evidence) / len(evidence)
                    if evidence else 0.0
                )

            return EvidenceEvent(
                query=ev.query,
                route=ev.route,
                evidence=evidence,
                confidence=confidence,
                retry_count=ev.retry_count,
            )

        @step
        async def synthesize(self, ev: EvidenceEvent) -> StopEvent:
            if not ev.evidence:
                return StopEvent(
                    result=WorkflowResult(
                        answer="I could not find enough evidence in the project documentation to answer this question safely.",
                        route=ev.route,
                        confidence=0.0,
                        sources=[],
                    )
                )

            answer, sources = await self.synthesizer(ev.query, ev.evidence)
            return StopEvent(
                result=WorkflowResult(
                    answer=answer,
                    route=ev.route,
                    confidence=ev.confidence,
                    sources=sources,
                )
            )
else:
    class RAGWorkflow:
        """Fallback implementation for environments where the Workflow API is unavailable."""

        def __init__(self, semantic_searcher, structured_searcher, synthesizer, *args, **kwargs):
            self.semantic_searcher = semantic_searcher
            self.structured_searcher = structured_searcher
            self.synthesizer = synthesizer

        async def run(self, query: str) -> WorkflowResult:
            query = query.strip()
            if not query:
                raise ValueError("Question cannot be empty.")
            decision = choose_route(query)

            if decision.route == "structured":
                evidence = self.structured_searcher.search(query)
                confidence = 1.0 if evidence else 0.0
            else:
                evidence = self.semantic_searcher.retrieve(query)
                confidence = (
                    sum(_node_score(x) for x in evidence) / len(evidence)
                    if evidence else 0.0
                )

            if not evidence:
                return WorkflowResult(
                    answer="I could not find enough evidence in the project documentation to answer this question safely.",
                    route=decision.route,
                    confidence=0.0,
                )

            answer, sources = await self.synthesizer(query, evidence)
            return WorkflowResult(
                answer=answer,
                route=decision.route,
                confidence=confidence,
                sources=sources,
            )
