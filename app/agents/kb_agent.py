"""KB Agent — RAG-powered Q&A over Odoo CRM documentation.

Stateless: context comes entirely from ChromaDB retrieval.
"""

from app.agents.base_agent import BaseAgent
from app.config import settings
from app.tools.kb_tools import search_knowledge_base
from app.utils.logger import get_logger

logger = get_logger(__name__)

_SYSTEM_PROMPT = """You are an expert on Odoo 16 CRM.
Answer questions using ONLY the information retrieved from the knowledge base.
If the knowledge base does not contain enough information, say so clearly.
Always cite the source document when possible.
Respond in the same language (English or PT-BR) as the user's question.
"""


class KBAgent(BaseAgent):
    """Stateless RAG agent for CRM knowledge base Q&A.

    Uses ChromaDB retrieval and ``text-embedding-3-small`` embeddings.
    """

    def __init__(self) -> None:
        super().__init__(
            name="kb_agent",
            model=settings.kb_agent_model,
            tools=[search_knowledge_base],
            system_prompt=_SYSTEM_PROMPT,
        )

    def answer(self, question: str) -> str:
        """Answer a knowledge base question.

        Args:
            question: The user's question about Odoo CRM.

        Returns:
            str: Grounded answer with source citations.
        """
        logger.info("kb_agent_answer", question=question[:80])
        return self.invoke(question)
