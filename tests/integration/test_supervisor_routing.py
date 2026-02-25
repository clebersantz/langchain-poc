"""Integration tests for Supervisor Agent intent routing."""

from unittest.mock import MagicMock, patch



class TestSupervisorRouting:
    """Tests for SupervisorAgent.route() intent detection and delegation."""

    def _make_supervisor(self):
        """Build a SupervisorAgent with all sub-agents mocked."""
        with patch("app.agents.supervisor.ChatOpenAI"), \
             patch("app.agents.supervisor.KBAgent"), \
             patch("app.agents.supervisor.OdooAPIAgent"), \
             patch("app.agents.supervisor.WorkflowAgent"), \
             patch("app.agents.supervisor.get_session_history") as mock_history:

            from app.agents.supervisor import SupervisorAgent

            supervisor = SupervisorAgent.__new__(SupervisorAgent)
            supervisor.name = "supervisor"
            supervisor._uid = None

            # Mock LLM
            mock_llm = MagicMock()
            supervisor._llm = mock_llm

            # Mock sub-agents
            supervisor._kb_agent = MagicMock()
            supervisor._odoo_agent = MagicMock()
            supervisor._workflow_agent = MagicMock()

            # Mock history
            mock_hist = MagicMock()
            mock_hist.messages = []
            mock_history.return_value = mock_hist
            supervisor._get_history = mock_history

            return supervisor, mock_llm, mock_hist

    def test_kb_question_routes_to_kb_agent(self):
        """Messages classified as KB_QUESTION should be handled by KBAgent."""
        supervisor, mock_llm, mock_hist = self._make_supervisor()
        with patch("app.agents.supervisor.get_session_history", return_value=mock_hist):
            mock_llm.invoke.return_value = MagicMock(content="KB_QUESTION")
            supervisor._kb_agent.answer.return_value = "Here is the answer."

            response, agent_used = supervisor.route(
                "What is a CRM pipeline?", "session-123"
            )
            assert agent_used == "kb_agent"
            assert response == "Here is the answer."
            supervisor._kb_agent.answer.assert_called_once()

    def test_crm_query_routes_to_odoo_agent(self):
        """Messages classified as CRM_QUERY should be handled by OdooAPIAgent."""
        supervisor, mock_llm, mock_hist = self._make_supervisor()
        with patch("app.agents.supervisor.get_session_history", return_value=mock_hist):
            mock_llm.invoke.return_value = MagicMock(content="CRM_QUERY")
            supervisor._odoo_agent.run.return_value = "Found 3 leads."

            response, agent_used = supervisor.route(
                "Get all open leads from Acme Corp", "session-456"
            )
            assert agent_used == "odoo_api_agent"
            supervisor._odoo_agent.run.assert_called_once()

    def test_workflow_routes_to_workflow_agent(self):
        """Messages classified as WORKFLOW should be handled by WorkflowAgent."""
        supervisor, mock_llm, mock_hist = self._make_supervisor()
        with patch("app.agents.supervisor.get_session_history", return_value=mock_hist):
            mock_llm.invoke.return_value = MagicMock(content="WORKFLOW")
            supervisor._workflow_agent.invoke.return_value = "Workflow started."

            response, agent_used = supervisor.route(
                "Run the lead qualification workflow for lead 42", "session-789"
            )
            assert agent_used == "workflow_agent"
            supervisor._workflow_agent.invoke.assert_called_once()
