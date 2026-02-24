"""LangChain tool wrappers for Odoo partner operations."""

import json

from langchain_core.tools import tool

from app.odoo.models.res_partner import (
    create_partner,
    get_partner,
    search_partners,
)


@tool
def search_partners_tool(query: str) -> str:
    """Search for Odoo partners (customers/vendors) by name or e-mail.

    Args:
        query: Search string.

    Returns:
        str: JSON list of matching partner records.
    """
    results = search_partners(query)
    return json.dumps(results, default=str)


@tool
def get_partner_tool(partner_id: int) -> str:
    """Get full details of a partner by id.

    Args:
        partner_id: Odoo record id.

    Returns:
        str: JSON partner record.
    """
    return json.dumps(get_partner(partner_id), default=str)


@tool
def create_partner_tool(name: str, email: str, phone: str = "") -> str:
    """Create a new partner (contact) in Odoo.

    Args:
        name: Partner full name or company name.
        email: E-mail address.
        phone: Optional phone number.

    Returns:
        str: JSON with the new partner id, e.g. ``{"id": 7}``.
    """
    values: dict = {"name": name, "email": email}
    if phone:
        values["phone"] = phone
    new_id = create_partner(values)
    return json.dumps({"id": new_id})
