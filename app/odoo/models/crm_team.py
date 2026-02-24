"""Odoo 16 crm.team model helpers."""

from app.odoo.client import odoo_client

TEAM_FIELDS = ["id", "name", "user_id", "member_ids", "alias_email", "active"]
MEMBER_FIELDS = ["id", "name", "email", "login"]


def get_all_teams() -> list[dict]:
    """Return all active sales teams.

    Returns:
        list[dict]: Sales team records.
    """
    return odoo_client.search_read("crm.team", [["active", "=", True]], TEAM_FIELDS)


def get_team_members(team_id: int) -> list[dict]:
    """Return the members (res.users) of a sales team.

    Args:
        team_id: The sales team record id.

    Returns:
        list[dict]: User records for team members.
    """
    teams = odoo_client.search_read(
        "crm.team", [["id", "=", team_id]], ["member_ids"], limit=1
    )
    if not teams:
        return []
    member_ids: list[int] = teams[0].get("member_ids", [])
    if not member_ids:
        return []
    return odoo_client.search_read(
        "res.users", [["id", "in", member_ids]], MEMBER_FIELDS
    )
