"""Odoo 16 crm.stage model helpers."""

from app.odoo.client import odoo_client

FIELDS = ["id", "name", "sequence", "probability", "fold", "team_id", "requirements"]


def get_all_stages(team_id: int | None = None) -> list[dict]:
    """Return all pipeline stages, optionally filtered by sales team.

    Args:
        team_id: If provided, filter to stages used by this team.

    Returns:
        list[dict]: Stage records.
    """
    domain: list = []
    if team_id:
        domain = [["team_id", "=", team_id]]
    return odoo_client.search_read("crm.stage", domain, FIELDS)


def get_stage_by_name(name: str) -> dict | None:
    """Return the first stage whose name matches (case-insensitive).

    Args:
        name: Stage name to search for.

    Returns:
        dict | None: The matching stage record, or None if not found.
    """
    results = odoo_client.search_read(
        "crm.stage", [["name", "ilike", name]], FIELDS, limit=1
    )
    return results[0] if results else None
