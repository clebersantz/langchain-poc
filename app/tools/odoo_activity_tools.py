"""LangChain tool wrappers for Odoo activity scheduling."""

import json

from langchain_core.tools import tool

from app.odoo.client import odoo_client
from app.odoo.models.mail_activity import (
    create_activity,
    get_overdue_activities,
    list_activities,
    mark_done,
)

# Default activity type ids for Odoo 16 (may vary per instance)
_ACTIVITY_TYPE_MAP = {
    "email": 4,
    "call": 2,
    "meeting": 1,
    "todo": 4,
}


def _resolve_activity_type_id(activity_type: str) -> int:
    """Resolve an activity type name to its Odoo id.

    Args:
        activity_type: Human-readable type name (e.g. "call", "email").

    Returns:
        int: The ``mail.activity.type`` record id.
    """
    results = odoo_client.search_read(
        "mail.activity.type",
        [["name", "ilike", activity_type]],
        ["id", "name"],
        limit=1,
    )
    if results:
        return results[0]["id"]
    return _ACTIVITY_TYPE_MAP.get(activity_type.lower(), 4)


@tool
def schedule_activity(
    lead_id: int,
    activity_type: str,
    summary: str,
    due_date: str,
    note: str = "",
) -> str:
    """Schedule an activity on a CRM lead or opportunity.

    Args:
        lead_id: CRM lead record id.
        activity_type: Type name such as "call", "email", or "meeting".
        summary: Short title of the activity.
        due_date: Deadline in YYYY-MM-DD format.
        note: Optional detailed note.

    Returns:
        str: JSON with the new activity id.
    """
    type_id = _resolve_activity_type_id(activity_type)
    act_id = create_activity("crm.lead", lead_id, type_id, summary, note, due_date)
    return json.dumps({"id": act_id})


@tool
def mark_activity_done(activity_id: int, feedback: str = "") -> str:
    """Mark an activity as done.

    Args:
        activity_id: The activity record id.
        feedback: Optional feedback text.

    Returns:
        str: JSON result ``{"success": true/false}``.
    """
    ok = mark_done(activity_id, feedback)
    return json.dumps({"success": bool(ok)})


@tool
def list_lead_activities(lead_id: int) -> str:
    """List all activities scheduled for a CRM lead.

    Args:
        lead_id: CRM lead record id.

    Returns:
        str: JSON list of activity records.
    """
    results = list_activities("crm.lead", lead_id)
    return json.dumps(results, default=str)


@tool
def get_overdue_activities_tool() -> str:
    """Return all overdue activities across the CRM.

    Returns:
        str: JSON list of overdue activity records.
    """
    results = get_overdue_activities()
    return json.dumps(results, default=str)
