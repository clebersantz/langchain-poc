"""Agents package."""

__all__ = ["SupervisorAgent", "KBAgent", "WorkflowAgent", "OdooAPIAgent"]


def __getattr__(name: str):
    if name == "SupervisorAgent":
        from app.agents.supervisor import SupervisorAgent

        return SupervisorAgent
    if name == "KBAgent":
        from app.agents.kb_agent import KBAgent

        return KBAgent
    if name == "WorkflowAgent":
        from app.agents.workflow_agent import WorkflowAgent

        return WorkflowAgent
    if name == "OdooAPIAgent":
        from app.agents.odoo_api_agent import OdooAPIAgent

        return OdooAPIAgent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
