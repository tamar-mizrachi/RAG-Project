from rag.config import settings
from pinecone import Pinecone, ServerlessSpec


def main():
    settings.require("pinecone_api_key")
    pc = Pinecone(api_key=settings.pinecone_api_key)

    existing = {x["name"] if isinstance(x, dict) else x.name for x in pc.list_indexes()}
    if settings.pinecone_index_name in existing:
        print(f"Index already exists: {settings.pinecone_index_name}")
        return

    pc.create_index(
        name=settings.pinecone_index_name,
        dimension=settings.embedding_dimension,
        metric="cosine",
        spec=ServerlessSpec(
            cloud=settings.pinecone_cloud,
            region=settings.pinecone_region,
        ),
    )
    print(f"Created Pinecone index: {settings.pinecone_index_name}")


if __name__ == "__main__":
    main()
