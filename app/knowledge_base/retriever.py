"""Knowledge base retriever factory."""

from langchain_core.vectorstores import VectorStoreRetriever

from app.knowledge_base.vector_store import get_vector_store


def get_retriever(k: int = 4) -> VectorStoreRetriever:
    """Return a LangChain retriever backed by ChromaDB.

    Args:
        k: Number of most-similar chunks to retrieve per query.

    Returns:
        VectorStoreRetriever: Configured retriever instance.
    """
    store = get_vector_store()
    return store.as_retriever(search_type="similarity", search_kwargs={"k": k})
