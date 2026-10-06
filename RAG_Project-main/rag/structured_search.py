from datetime import datetime, timezone
from .models import StructuredKnowledge, KnowledgeItem


class StructuredSearcher:
    def __init__(self, knowledge: StructuredKnowledge):
        self.knowledge = knowledge

    def search(
        self,
        query: str,
        item_type: str | None = None,
        tool: str | None = None,
    ) -> list[KnowledgeItem]:
        q = query.lower().strip()
        if not q:
            return []

        groups = (
            [item_type]
            if item_type in {"decision", "rule", "warning", "change"}
            else ["decision", "rule", "warning", "change"]
        )

        results: list[KnowledgeItem] = []
        for group in groups:
            for item in getattr(self.knowledge, f"{group}s"):
                haystack = " ".join(
                    [item.title, item.summary, " ".join(item.tags)]
                ).lower()
                if tool and item.source.tool != tool:
                    continue
                if any(token in haystack for token in q.split()):
                    results.append(item)

        # Newest observations first for update/latest questions.
        results.sort(
            key=lambda x: x.source.observed_at or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
        return results
