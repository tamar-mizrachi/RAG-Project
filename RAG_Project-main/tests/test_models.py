from rag.models import KnowledgeItem, SourceInfo, StructuredKnowledge


def test_structured_schema():
    source = SourceInfo(tool="cursor", file=".cursor/README.md")
    item = KnowledgeItem(
        id="decision-1",
        type="decision",
        title="Test",
        summary="A decision",
        source=source,
    )
    knowledge = StructuredKnowledge(decisions=[item])

    assert knowledge.decisions[0].type == "decision"
    assert knowledge.decisions[0].source.tool == "cursor"
