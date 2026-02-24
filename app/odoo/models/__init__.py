"""Odoo model helpers package."""

from app.odoo.models.crm_lead import (
    convert_to_opportunity,
    create_lead,
    get_lead,
    mark_lost,
    mark_won,
    search_leads,
    update_lead,
)
from app.odoo.models.crm_stage import get_all_stages, get_stage_by_name
from app.odoo.models.crm_team import get_all_teams, get_team_members
from app.odoo.models.mail_activity import (
    create_activity,
    get_overdue_activities,
    list_activities,
    mark_done,
)
from app.odoo.models.res_partner import (
    create_partner,
    get_partner,
    search_partners,
    update_partner,
)

__all__ = [
    # crm_lead
    "search_leads",
    "get_lead",
    "create_lead",
    "update_lead",
    "convert_to_opportunity",
    "mark_won",
    "mark_lost",
    # crm_stage
    "get_all_stages",
    "get_stage_by_name",
    # crm_team
    "get_all_teams",
    "get_team_members",
    # res_partner
    "search_partners",
    "get_partner",
    "create_partner",
    "update_partner",
    # mail_activity
    "create_activity",
    "mark_done",
    "list_activities",
    "get_overdue_activities",
]
