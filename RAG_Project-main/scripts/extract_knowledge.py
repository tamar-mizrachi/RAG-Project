from rag.config import settings
from rag.extraction import extract_structured_knowledge, save_knowledge


def main():
    knowledge = extract_structured_knowledge(settings)
    save_knowledge(knowledge, settings.structured_data_path)

    print(
        "Extracted: "
        f"{len(knowledge.decisions)} decisions, "
        f"{len(knowledge.rules)} rules, "
        f"{len(knowledge.warnings)} warnings, "
        f"{len(knowledge.changes)} changes."
    )


if __name__ == "__main__":
    main()
