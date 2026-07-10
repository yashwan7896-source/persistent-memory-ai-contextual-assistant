"""
Part 1 smoke test — just confirms settings load without crashing
and defaults are sane. Run with: pytest tests/test_settings.py -v
"""

from src.config.settings import settings


def test_settings_load():
    assert settings.app_name == "MemoryAI"


def test_settings_have_defaults():
    assert settings.port == 8000
    assert settings.chroma_collection_name == "memoryai_memories"


if __name__ == "__main__":
    print(f"App: {settings.app_name}")
    print(f"Env: {settings.app_env}")
    print(f"Chroma dir: {settings.chroma_persist_dir}")
    print(f"Embedding model: {settings.embedding_model_name}")
    print("✅ Config loaded successfully — Part 1 skeleton is working.")
