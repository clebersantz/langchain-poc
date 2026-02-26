"""Supervisor Agent — entry point for all user messages.

Routes incoming messages to the appropriate sub-agent based on detected intent,
and maintains persistent conversation history via SQLite.
"""


from typing import TypedDict

from app.agents.base_agent import BaseAgent
from app.agents.kb_agent import KBAgent
from app.agents.odoo_api_agent import OdooAPIAgent
from app.agents.workflow_agent import WorkflowAgent
from app.config import settings
from app.memory.session_store import get_session_history
from app.utils.logger import get_logger
from langgraph.graph import END, START, StateGraph

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
        self._graph = self._build_graph()

    class _State(TypedDict, total=False):
        message: str
        session_id: str
        intent: str
        response: str
        agent_used: str

    def _build_graph(self):
        graph = StateGraph(self._State)
        graph.add_node("classify_intent", self._classify_intent)
        graph.add_node("kb_agent", self._run_kb_agent)
        graph.add_node("odoo_api_agent", self._run_odoo_agent)
        graph.add_node("workflow_agent", self._run_workflow_agent)
        graph.add_node("supervisor", self._run_supervisor)
        graph.add_node("persist_history", self._persist_history)
        graph.add_edge(START, "classify_intent")
        graph.add_conditional_edges(
            "classify_intent",
            self._route_intent,
            {
                "kb_agent": "kb_agent",
                "odoo_api_agent": "odoo_api_agent",
                "workflow_agent": "workflow_agent",
                "supervisor": "supervisor",
            },
        )
        for node in ("kb_agent", "odoo_api_agent", "workflow_agent", "supervisor"):
            graph.add_edge(node, "persist_history")
        graph.add_edge("persist_history", END)
        return graph.compile()

    def _classify_intent(self, state: _State) -> _State:
        intent_prompt = (
            "Classify the following user message into exactly one category:\n"
            "KB_QUESTION, CRM_QUERY, WORKFLOW, OTHER\n\n"
            f"Message: {state['message']}\n\nCategory:"
        )
        intent_result = self._llm.invoke(intent_prompt)
        return {"intent": intent_result.content.strip().upper()}

    @staticmethod
    def _route_intent(state: _State) -> str:
        intent = state.get("intent", "")
        if "KB_QUESTION" in intent:
            return "kb_agent"
        if "CRM_QUERY" in intent:
            return "odoo_api_agent"
        if "WORKFLOW" in intent:
            return "workflow_agent"
        return "supervisor"

    def _run_kb_agent(self, state: _State) -> _State:
        return {
            "response": self._kb_agent.answer(state["message"]),
            "agent_used": "kb_agent",
        }

    def _run_odoo_agent(self, state: _State) -> _State:
        return {
            "response": self._odoo_agent.run(state["message"]),
            "agent_used": "odoo_api_agent",
        }

    def _run_workflow_agent(self, state: _State) -> _State:
        return {
            "response": self._workflow_agent.invoke(state["message"]),
            "agent_used": "workflow_agent",
        }

    def _run_supervisor(self, state: _State) -> _State:
        full_prompt = _SYSTEM_PROMPT + f"\n\nUser: {state['message']}"
        return {
            "response": self._llm.invoke(full_prompt).content,
            "agent_used": "supervisor",
        }

    @staticmethod
    def _persist_history(state: _State) -> _State:
        history = get_session_history(state["session_id"])
        history.add_user_message(state["message"])
        history.add_ai_message(state["response"])
        return {}

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
        result = self._graph.invoke({"message": message, "session_id": session_id})
        return result["response"], result["agent_used"]
