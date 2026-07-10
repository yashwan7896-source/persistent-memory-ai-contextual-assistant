"""
Central config for MemoryAI.
Loads from .env at project root. Every later part (API, memory, nlp)
imports `settings` from here instead of reading os.environ directly.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    app_name: str = "MemoryAI"
    app_env: str = "development"
    debug: bool = True

    # --- LLM (Part 6) ---
    anthropic_api_key: str = ""

    # --- Vector DB (Part 3) ---
    chroma_persist_dir: str = "./data/chroma_store"
    chroma_collection_name: str = "memoryai_memories"

    # --- Embeddings (Part 3 / 5) ---
    embedding_model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"

    # --- Server (Part 2) ---
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Singleton instance — import this everywhere else.
settings = Settings()
