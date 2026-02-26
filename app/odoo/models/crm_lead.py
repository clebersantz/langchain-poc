"""Odoo 16 crm.lead model helpers.

Provides CRUD and workflow operations for the ``crm.lead`` model.
Both leads and opportunities share this model in Odoo 16 — the
``type`` field distinguishes them (``"lead"`` vs ``"opportunity"``).

# TODO: v18 - verify field names remain compatible with Odoo 18 crm.lead
"""

from app.odoo.client import odoo_client

# Important crm.lead fields for Odoo 16
FIELDS = [
    "id",
    "name",
    "type",  # "lead" or "opportunity"
    "stage_id",
    "kanban_state",
    "user_id",
    "team_id",
    "partner_id",
    "partner_name",
    "contact_name",
    "email_from",
    "phone",
    "mobile",
    "street",
    "city",
    "country_id",
    "description",
    "probability",
    "expected_revenue",
    "recurring_revenue",
    "date_deadline",
    "date_conversion",
    "date_closed",
    "active",
    "priority",
    "tag_ids",
    "lost_reason_id",
    "company_id",
    "create_date",
    "write_date",
]


def search_leads(domain: list | None = None, limit: int = 20) -> list[dict]:
    """Search for CRM leads/opportunities.

    Args:
        domain: Odoo search domain. Defaults to all records.
        limit: Maximum number of records to return.

    Returns:
        list[dict]: Matching lead records with :data:`FIELDS`.
    """
    return odoo_client.search_read("crm.lead", domain or [], FIELDS, limit=limit)


def get_lead(lead_id: int) -> dict:
    """Return a single lead by id.

    Args:
        lead_id: The Odoo record id.

    Returns:
        dict: The lead record, or an empty dict if not found.
    """
    results = odoo_client.search_read("crm.lead", [["id", "=", lead_id]], FIELDS, limit=1)
    return results[0] if results else {}


def create_lead(values: dict) -> int:
    """Create a new lead.

    Args:
        values: Field values for the new lead.

    Returns:
        int: The id of the new record.
    """
    return odoo_client.create("crm.lead", values)


def update_lead(lead_id: int, values: dict) -> bool:
    """Update an existing lead.

    Args:
        lead_id: Record id to update.
        values: Fields to write.

    Returns:
        bool: True on success.
    """
    return odoo_client.write("crm.lead", [lead_id], values)


def convert_to_opportunity(
    lead_id: int,
    partner_id: int | None = None,
    team_id: int | None = None,
) -> bool:
    """Convert a lead to an opportunity.

    Args:
        lead_id: The lead record id.
        partner_id: Optional partner to link.
        team_id: Optional sales team to assign.

    Returns:
        bool: True on success.
    """
    values: dict = {"type": "opportunity"}
    if partner_id:
        values["partner_id"] = partner_id
    if team_id:
        values["team_id"] = team_id
    return odoo_client.write("crm.lead", [lead_id], values)


def mark_won(lead_id: int) -> bool:
    """Mark a lead/opportunity as Won.

    Args:
        lead_id: Record id.

    Returns:
        bool: True on success.
    """
    try:
        odoo_client.execute("crm.lead", "action_set_won", [lead_id])
        return True
    except Exception:
        # Fall back to direct write if the method is unavailable
        return odoo_client.write("crm.lead", [lead_id], {"probability": 100})


def mark_lost(lead_id: int, lost_reason_id: int | None = None) -> bool:
    """Mark a lead/opportunity as Lost.

    Args:
        lead_id: Record id.
        lost_reason_id: Optional crm.lost.reason record id.

    Returns:
        bool: True on success.
    """
    values: dict = {"active": False}
    if lost_reason_id:
        values["lost_reason_id"] = lost_reason_id
    try:
        odoo_client.execute("crm.lead", "action_set_lost", [lead_id])
        if lost_reason_id:
            odoo_client.write("crm.lead", [lead_id], {"lost_reason_id": lost_reason_id})
        return True
    except Exception:
        return odoo_client.write("crm.lead", [lead_id], values)


def add_note(lead_id: int, note: str) -> int:
    """Post an internal note on a CRM lead/opportunity.

    Args:
        lead_id: Record id.
        note: Note body to post.

    Returns:
        int: Created ``mail.message`` id.
    """
    return odoo_client.execute(
        "crm.lead",
        "message_post",
        [lead_id],
        body=note,
        message_type="comment",
        subtype_xmlid="mail.mt_note",
    )
