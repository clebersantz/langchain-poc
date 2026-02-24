"""Supervisor Agent — entry point for all user messages.

Routes incoming messages to the appropriate sub-agent based on detected intent,
and maintains persistent conversation history via SQLite.
"""

from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.agents.base_agent import BaseAgent
from app.agents.kb_agent import KBAgent
from app.agents.odoo_api_agent import OdooAPIAgent
from app.agents.workflow_agent import WorkflowAgent
from app.config import settings
from app.memory.session_store import get_session_history
from app.utils.logger import get_logger

logger = get_logger(__name__)

_SYSTEM_PROMPT = """You are a helpful CRM assistant integrated with Odoo 16.
You can answer questions about CRM concepts, query and update Odoo data, and
run automated CRM workflows.

You communicate fluently in both English and Brazilian Portuguese (PT-BR).
Always respond in the same language the user writes in.

When routing, use these rules:
- If the user asks a general CRM question or how something works → KB Agent
- If the user wants to query, create, or update Odoo data → Odoo API Agent
- If the user wants to run a workflow (qualification, follow-up, etc.) → Workflow Agent

# TODO: v18 - update routing logic if Odoo 18 REST API tools are added
"""


class SupervisorAgent(BaseAgent):
    """Supervisor agent that routes messages and maintains conversation memory.

    Args:
        None — configuration is read from :mod:`app.config`.
    """

    def __init__(self) -> None:
        super().__init__(
            name="supervisor",
            model=settings.supervisor_model,
            tools=[],  # Supervisor does not call Odoo directly
            system_prompt=_SYSTEM_PROMPT,
        )
        self._kb_agent = KBAgent()
        self._odoo_agent = OdooAPIAgent()
        self._workflow_agent = WorkflowAgent()

    def route(self, message: str, session_id: str) -> tuple[str, str]:
        """Route a user message to the appropriate sub-agent.

        Determines intent by asking the LLM, then delegates to the correct
        sub-agent.  Conversation history is persisted to SQLite.

        Args:
            message: Raw user message (PT-BR or English).
            session_id: Unique identifier for the conversation session.

        Returns:
            tuple[str, str]: ``(response_text, agent_used)`` where
                ``agent_used`` is one of ``"kb_agent"``, ``"odoo_api_agent"``,
                ``"workflow_agent"``, or ``"supervisor"``.
        """
        logger.info("supervisor_route", session_id=session_id)

        # Simple intent classification via the LLM
        intent_prompt = (
            "Classify the following user message into exactly one category:\n"
            "KB_QUESTION, CRM_QUERY, WORKFLOW, OTHER\n\n"
            f"Message: {message}\n\nCategory:"
        )
        intent_result = self._llm.invoke(intent_prompt)
        intent = intent_result.content.strip().upper()

        if "KB_QUESTION" in intent:
            response = self._kb_agent.answer(message)
            agent_used = "kb_agent"
        elif "CRM_QUERY" in intent:
            response = self._odoo_agent.run(message)
            agent_used = "odoo_api_agent"
        elif "WORKFLOW" in intent:
            # Extract workflow name heuristically; default to supervisor response
            response = self._workflow_agent.invoke(message)
            agent_used = "workflow_agent"
        else:
            # General conversation — answer directly with history
            history = get_session_history(session_id)
            messages = history.messages
            full_prompt = _SYSTEM_PROMPT + f"\n\nUser: {message}"
            response = self._llm.invoke(full_prompt).content
            history.add_user_message(message)
            history.add_ai_message(response)
            agent_used = "supervisor"

        # Persist turn to history for intent-routed agents too
        if agent_used != "supervisor":
            history = get_session_history(session_id)
            history.add_user_message(message)
            history.add_ai_message(response)

        return response, agent_used
