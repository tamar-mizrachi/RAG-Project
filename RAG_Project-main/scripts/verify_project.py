from pathlib import Path
import compileall
import sys


REQUIRED = [
    "app/main.py",
    "app/prepare.py",
    "rag/config.py",
    "rag/ingestion.py",
    "rag/vector_store.py",
    "rag/semantic_search.py",
    "rag/extraction.py",
    "rag/structured_search.py",
    "rag/router.py",
    "rag/workflow.py",
    "rag/ui.py",
    "rag/llm_answer.py",
    "scripts/create_pinecone_index.py",
    "scripts/extract_knowledge.py",
]


def main():
    missing = [p for p in REQUIRED if not Path(p).exists()]
    if missing:
        print("Missing files:", missing)
        sys.exit(1)

    ok = compileall.compile_dir(".", quiet=1)
    if not ok:
        sys.exit(1)

    print("Project structure and Python syntax: OK")


if __name__ == "__main__":
    main()
