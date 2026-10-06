from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone

from .config import Settings


def build_embedding_model(settings: Settings):
    settings.require("cohere_api_key")
    return CohereEmbedding(
        api_key=settings.cohere_api_key,
        model_name=settings.cohere_embed_model,
        input_type="search_document",
    )


def connect_vector_store(settings: Settings):
    settings.require("pinecone_api_key")
    pc = Pinecone(api_key=settings.pinecone_api_key)
    pinecone_index = pc.Index(settings.pinecone_index_name)
    return PineconeVectorStore(
        pinecone_index=pinecone_index,
        namespace=settings.pinecone_namespace,
    )


def build_index_from_nodes(nodes, settings: Settings):
    embed_model = build_embedding_model(settings)
    vector_store = connect_vector_store(settings)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    return VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=True,
    )


def connect_existing_index(settings: Settings):
    embed_model = build_embedding_model(settings)
    vector_store = connect_vector_store(settings)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context,
        embed_model=embed_model,
    )
