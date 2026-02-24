"""Odoo API Agent — executes direct Odoo 16 CRUD operations via XML-RPC."""

from app.agents.base_agent import BaseAgent
from app.config import settings
from app.tools.odoo_activity_tools import (
    get_overdue_activities_tool,
    list_lead_activities,
    mark_activity_done,
    schedule_activity,
)
from app.tools.odoo_crm_tools import (
    convert_lead_to_opportunity,
    create_crm_lead,
    get_crm_lead,
    mark_lead_lost,
    mark_lead_won,
    search_crm_leads,
    update_crm_lead,
)
from app.tools.odoo_partner_tools import (
    create_partner_tool,
    get_partner_tool,
    search_partners_tool,
)
from app.tools.odoo_pipeline_tools import (
    get_pipeline_stages,
    get_pipeline_summary,
    move_lead_to_stage,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

_SYSTEM_PROMPT = """You are a precise Odoo 16 CRM data operations agent.
Execute CRUD operations on Odoo using the available tools.
Always confirm operation results and return structured information.
Never invent data — only use what the tools return.
Respond in the same language (English or PT-BR) as the user's instruction.

# TODO: v18 - update tool set if Odoo 18 REST API tools are added
"""


class OdooAPIAgent(BaseAgent):
    """Stateless agent for all direct Odoo 16 XML-RPC operations.

    Exposes tools for leads, partners, activities, pipeline stages, and teams.
    """

    def __init__(self) -> None:
        super().__init__(
            name="odoo_api_agent",
            model=settings.odoo_api_agent_model,
            tools=[
                search_crm_leads,
                get_crm_lead,
                create_crm_lead,
                update_crm_lead,
                mark_lead_won,
                mark_lead_lost,
                convert_lead_to_opportunity,
                search_partners_tool,
                get_partner_tool,
                create_partner_tool,
                schedule_activity,
                mark_activity_done,
                list_lead_activities,
                get_overdue_activities_tool,
                get_pipeline_stages,
                move_lead_to_stage,
                get_pipeline_summary,
            ],
            system_prompt=_SYSTEM_PROMPT,
        )

    def run(self, instruction: str) -> str:
        """Execute an Odoo data operation described in natural language.

        Args:
            instruction: Natural-language instruction (e.g.
                "Get all open leads from Acme Corp").

        Returns:
            str: Formatted result of the Odoo operation.
        """
        logger.info("odoo_api_agent_run", instruction=instruction[:80])
        return self.invoke(instruction)
