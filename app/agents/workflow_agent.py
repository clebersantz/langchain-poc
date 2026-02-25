"""Workflow Agent — executes pre-defined multi-step CRM workflows."""

from app.agents.base_agent import BaseAgent
from app.config import settings
from app.memory.workflow_log import log_workflow_complete, log_workflow_start
from app.tools.odoo_activity_tools import schedule_activity
from app.tools.odoo_crm_tools import (
    convert_lead_to_opportunity,
    get_crm_lead,
    mark_lead_lost,
    mark_lead_won,
    search_crm_leads,
    update_crm_lead,
)
from app.tools.odoo_pipeline_tools import get_pipeline_stages, move_lead_to_stage
from app.tools.workflow_tools import list_available_workflows, run_workflow
from app.utils.logger import get_logger

logger = get_logger(__name__)

_SYSTEM_PROMPT = """You are a CRM workflow automation agent integrated with Odoo 16.
Execute the requested workflow step by step using the available tools.
Always confirm each step's result before proceeding to the next.
Log any errors clearly and continue where possible.
Respond in the same language (English or PT-BR) as the user's request.
"""


class WorkflowAgent(BaseAgent):
    """Agent that executes pre-defined multi-step CRM workflows.

    Workflows are registered in :mod:`app.workflows.registry` and executed
    asynchronously.  Each run is logged to the SQLite ``workflow_log`` table.
    """

    def __init__(self) -> None:
        super().__init__(
            name="workflow_agent",
            model=settings.workflow_agent_model,
            tools=[
                list_available_workflows,
                run_workflow,
                get_crm_lead,
                search_crm_leads,
                update_crm_lead,
                mark_lead_won,
                mark_lead_lost,
                convert_lead_to_opportunity,
                move_lead_to_stage,
                get_pipeline_stages,
                schedule_activity,
            ],
            system_prompt=_SYSTEM_PROMPT,
        )

    def execute(
        self,
        workflow_name: str,
        context: dict,
        session_id: str = "system",
    ) -> str:
        """Execute a named workflow with the provided context.

        Args:
            workflow_name: Registered workflow name.
            context: Input context dict for the workflow.
            session_id: Session identifier for audit logging.

        Returns:
            str: Natural-language summary of the workflow execution.
        """
        log_id = log_workflow_start(workflow_name, "agent", context)
        logger.info("workflow_execute", name=workflow_name, log_id=log_id)

        instruction = (
            f"Run the '{workflow_name}' workflow with the following context:\n"
            f"{context}\n\n"
            "Use the run_workflow tool to execute it, then summarise the result."
        )
        response = self.invoke(instruction, session_id=session_id)

        log_workflow_complete(log_id, steps=[], status="success")
        return response
