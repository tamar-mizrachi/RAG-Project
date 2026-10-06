from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.retrievers import VectorIndexRetriever

from .config import Settings
from .vector_store import connect_existing_index


class SemanticSearcher:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.index = connect_existing_index(settings)

    def retrieve(self, query: str, top_k: int | None = None):
        query = query.strip()
        if not query:
            raise ValueError("Query cannot be empty.")

        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=top_k or self.settings.top_k,
        )
        nodes = retriever.retrieve(query)

        processor = SimilarityPostprocessor(
            similarity_cutoff=self.settings.similarity_cutoff
        )
        return processor.postprocess_nodes(nodes)
