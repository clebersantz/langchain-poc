"""ChromaDB vector store singleton."""

from functools import lru_cache

from langchain_community.vectorstores import Chroma

from app.config import settings
from app.knowledge_base.embeddings import get_embeddings


@lru_cache
def get_vector_store() -> Chroma:
    """Return a cached ChromaDB Chroma instance backed by disk persistence.

    Returns:
        Chroma: LangChain Chroma vector store.
    """
    return Chroma(
        collection_name=settings.chroma_collection,
        embedding_function=get_embeddings(),
        persist_directory=settings.chroma_persist_dir,
    )
