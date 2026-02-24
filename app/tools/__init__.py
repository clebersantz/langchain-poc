"""LangChain tools package."""

from app.tools.kb_tools import search_knowledge_base
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
from app.tools.workflow_tools import list_available_workflows, run_workflow

__all__ = [
    "search_knowledge_base",
    "schedule_activity",
    "mark_activity_done",
    "list_lead_activities",
    "get_overdue_activities_tool",
    "search_crm_leads",
    "get_crm_lead",
    "create_crm_lead",
    "update_crm_lead",
    "mark_lead_won",
    "mark_lead_lost",
    "convert_lead_to_opportunity",
    "search_partners_tool",
    "get_partner_tool",
    "create_partner_tool",
    "get_pipeline_stages",
    "move_lead_to_stage",
    "get_pipeline_summary",
    "list_available_workflows",
    "run_workflow",
]
