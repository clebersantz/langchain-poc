"""LangChain tool wrapper for the knowledge base retriever."""

from langchain_core.tools import tool

from app.knowledge_base.retriever import get_retriever


@tool
def search_knowledge_base(question: str) -> str:
    """Search the Odoo CRM knowledge base for answers.

    Performs a semantic similarity search over ingested documentation and
    returns the most relevant chunks as a single string.

    Args:
        question: The question or topic to search for.

    Returns:
        str: Relevant knowledge base content joined by separators.
    """
    retriever = get_retriever(k=4)
    docs = retriever.invoke(question)
    if not docs:
        return "No relevant information found in the knowledge base."
    parts = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        parts.append(f"[Source: {source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)
