from rag.config import settings
from rag.ingestion import load_nodes
from rag.vector_store import build_index_from_nodes


def main():
    settings.require("cohere_api_key", "pinecone_api_key")
    nodes = load_nodes(settings.data_dir)
    print(f"Loaded and chunked {len(nodes)} nodes.")
    build_index_from_nodes(nodes, settings)
    print("Vector index successfully written to Pinecone.")


if __name__ == "__main__":
    main()
