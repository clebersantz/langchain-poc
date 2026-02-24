"""Knowledge base package for ChromaDB-backed RAG."""

from app.knowledge_base.embeddings import get_embeddings
from app.knowledge_base.ingestor import ingest_knowledge_base
from app.knowledge_base.retriever import get_retriever
from app.knowledge_base.vector_store import get_vector_store

__all__ = [
    "get_embeddings",
    "ingest_knowledge_base",
    "get_retriever",
    "get_vector_store",
]
