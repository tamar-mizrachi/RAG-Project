import asyncio

from rag.config import settings
from rag.extraction import load_knowledge
from rag.llm_answer import build_synthesizer
from rag.semantic_search import SemanticSearcher
from rag.structured_search import StructuredSearcher
from rag.ui import build_ui
from rag.workflow import RAGWorkflow


async def answer_question(query: str):
    semantic = SemanticSearcher(settings)
    knowledge = load_knowledge(settings.structured_data_path)
    structured = StructuredSearcher(knowledge)
    synthesizer = build_synthesizer(settings)

    workflow = RAGWorkflow(
        semantic_searcher=semantic,
        structured_searcher=structured,
        synthesizer=synthesizer,
        timeout=120,
    )

    if hasattr(workflow, "run"):
        result = await workflow.run(query=query)
    else:
        raise RuntimeError("Workflow implementation does not expose run().")
    return result


def main():
    demo = build_ui(answer_question)
    demo.launch()


if __name__ == "__main__":
    main()
