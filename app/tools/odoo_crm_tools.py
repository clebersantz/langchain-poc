"""LangChain tool wrappers for Odoo CRM operations."""

import json

from langchain_core.tools import tool

from app.odoo.models.crm_lead import (
    add_lead_note,
    convert_to_opportunity,
    create_lead,
    get_lead,
    mark_lost,
    mark_won,
    search_leads,
    update_lead,
)


@tool
def search_crm_leads(query: str, limit: int = 10) -> str:
    """Search CRM leads and opportunities by name or description.

    Args:
        query: Text to search for in lead names.
        limit: Maximum number of results (default 10).

    Returns:
        str: JSON list of matching lead records.
    """
    domain = [["name", "ilike", query]]
    results = search_leads(domain=domain, limit=limit)
    return json.dumps(results, default=str)


@tool
def get_crm_lead(lead_id: int) -> str:
    """Get the full details of a single CRM lead or opportunity.

    Args:
        lead_id: The Odoo record id of the lead.

    Returns:
        str: JSON representation of the lead record.
    """
    return json.dumps(get_lead(lead_id), default=str)


@tool
def create_crm_lead(
    name: str,
    email: str,
    contact_name: str,
    description: str = "",
) -> str:
    """Create a new CRM lead.

    Args:
        name: Lead title / name.
        email: Contact e-mail address.
        contact_name: Full name of the contact person.
        description: Optional additional notes.

    Returns:
        str: JSON with the new lead id, e.g. ``{"id": 42}``.
    """
    values = {
        "name": name,
        "email_from": email,
        "contact_name": contact_name,
        "description": description,
        "type": "lead",
    }
    new_id = create_lead(values)
    return json.dumps({"id": new_id})


@tool
def update_crm_lead(lead_id: int, values_json: str) -> str:
    """Update fields on an existing CRM lead.

    Args:
        lead_id: The Odoo record id to update.
        values_json: JSON string of field-value pairs to write.

    Returns:
        str: JSON result ``{"success": true/false}``.
    """
    values = json.loads(values_json)
    ok = update_lead(lead_id, values)
    return json.dumps({"success": bool(ok)})


@tool
def mark_lead_won(lead_id: int) -> str:
    """Mark a CRM opportunity as Won.

    Args:
        lead_id: The Odoo record id.

    Returns:
        str: JSON result ``{"success": true/false}``.
    """
    ok = mark_won(lead_id)
    return json.dumps({"success": bool(ok)})


@tool
def mark_lead_lost(lead_id: int, reason: str = "") -> str:
    """Mark a CRM opportunity as Lost.

    Args:
        lead_id: The Odoo record id.
        reason: Optional text reason for losing the opportunity.

    Returns:
        str: JSON result ``{"success": true/false}``.
    """
    ok = mark_lost(lead_id)
    return json.dumps({"success": bool(ok), "reason": reason})


@tool
def convert_lead_to_opportunity(lead_id: int) -> str:
    """Convert a lead to an opportunity in the CRM pipeline.

    Args:
        lead_id: The Odoo record id of the lead.

    Returns:
        str: JSON result ``{"success": true/false}``.
    """
    ok = convert_to_opportunity(lead_id)
    return json.dumps({"success": bool(ok)})


@tool
def add_note_to_crm_lead(lead_id: int, note: str) -> str:
    """Post an internal note to a CRM lead/opportunity.

    Args:
        lead_id: The Odoo record id.
        note: Note text to post.

    Returns:
        str: JSON result ``{"message_id": 123}``.
    """
    message_id = add_lead_note(lead_id, note)
    return json.dumps({"message_id": int(message_id)})
