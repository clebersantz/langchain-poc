"""OpenAI embeddings configuration."""

from functools import lru_cache

from langchain_openai import OpenAIEmbeddings

from app.config import settings


@lru_cache
def get_embeddings() -> OpenAIEmbeddings:
    """Return a cached OpenAIEmbeddings instance using text-embedding-3-small.

    Returns:
        OpenAIEmbeddings: Configured embeddings object.
    """
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=settings.openai_api_key,
    )
