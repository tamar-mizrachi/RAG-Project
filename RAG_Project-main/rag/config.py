from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = Field(default="")
    cohere_api_key: str = Field(default="")
    pinecone_api_key: str = Field(default="")

    pinecone_index_name: str = "agentic-coding-rag"
    pinecone_namespace: str = "agentic-coding"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"

    cohere_embed_model: str = "embed-english-v3.0"
    embedding_dimension: int = 1024

    openai_model: str = "gpt-4o-mini"

    top_k: int = 6
    similarity_cutoff: float = 0.35
    max_retrieval_retries: int = 1

    data_dir: Path = Path("data")
    structured_data_path: Path = Path("structured/knowledge.json")

    def require(self, *names: str) -> None:
        missing = [name for name in names if not getattr(self, name)]
        if missing:
            raise RuntimeError(
                "Missing required environment variables: "
                + ", ".join(missing)
                + ". Copy .env.example to .env and fill them in."
            )


settings = Settings()
