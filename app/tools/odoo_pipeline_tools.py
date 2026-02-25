"""LangChain tool wrappers for Odoo pipeline stage operations."""

import json

from langchain_core.tools import tool

from app.odoo.models.crm_lead import search_leads, update_lead
from app.odoo.models.crm_stage import get_all_stages, get_stage_by_name


@tool
def get_pipeline_stages() -> str:
    """Return all CRM pipeline stages configured in Odoo.

    Returns:
        str: JSON list of stage records (id, name, sequence, probability).
    """
    stages = get_all_stages()
    return json.dumps(stages, default=str)


@tool
def move_lead_to_stage(lead_id: int, stage_name: str) -> str:
    """Move a CRM lead or opportunity to a named pipeline stage.

    Args:
        lead_id: CRM lead record id.
        stage_name: Human-readable stage name (e.g. "Qualified", "Won").

    Returns:
        str: JSON result ``{"success": true/false, "stage_id": N}``.
    """
    stage = get_stage_by_name(stage_name)
    if not stage:
        return json.dumps({"success": False, "error": f"Stage '{stage_name}' not found"})
    ok = update_lead(lead_id, {"stage_id": stage["id"]})
    return json.dumps({"success": bool(ok), "stage_id": stage["id"]})


@tool
def get_pipeline_summary() -> str:
    """Return a high-level summary of the CRM pipeline by stage.

    Returns:
        str: JSON mapping of stage names to opportunity counts.
    """
    stages = get_all_stages()
    summary = {}
    for stage in stages:
        count_results = search_leads(
            domain=[["stage_id", "=", stage["id"]], ["type", "=", "opportunity"]],
            limit=1000,
        )
        summary[stage["name"]] = len(count_results)
    return json.dumps(summary)
