import re
from .models import RouteDecision


STRUCTURED_PATTERNS = [
    r"\blist\b",
    r"\ball\b",
    r"\bevery\b",
    r"\bhow many\b",
    r"\blatest\b",
    r"\brecent\b",
    r"\blast (week|month|quarter)\b",
    r"\bwhat changed\b",
    r"\bwhich decisions\b",
    r"\bwhat rules\b",
    r"\bwhat warnings\b",
    r"\blatest rule\b",
    r"\bכל\b",
    r"\bרשימה\b",
    r"\bהחלטות\b",
    r"\bכללים\b",
    r"\bאזהרות\b",
    r"\bמה השתנה\b",
    r"\bעדכני\b",
]


def choose_route(query: str) -> RouteDecision:
    normalized = query.lower().strip()
    if not normalized:
        raise ValueError("Question cannot be empty.")

    for pattern in STRUCTURED_PATTERNS:
        if re.search(pattern, normalized):
            return RouteDecision(
                route="structured",
                reason="The question requests a list, latest/recent state, change history, or a typed collection.",
            )

    return RouteDecision(
        route="semantic",
        reason="The question is primarily conceptual and is best answered using semantic retrieval.",
    )
