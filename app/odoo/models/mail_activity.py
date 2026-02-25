"""Odoo 16 mail.activity model helpers.

Activities represent scheduled tasks (calls, e-mails, meetings) linked to any
Odoo record.  The ``mail.activity`` model is used across many modules but is
especially important in CRM for follow-up tracking.
"""

from app.odoo.client import odoo_client

FIELDS = [
    "id",
    "res_id",
    "res_model",
    "res_model_id",
    "res_name",
    "activity_type_id",
    "summary",
    "note",
    "date_deadline",
    "user_id",
    "state",  # "overdue", "today", "planned"
]


def create_activity(
    res_model: str,
    res_id: int,
    activity_type_id: int,
    summary: str,
    note: str,
    date_deadline: str,
) -> int:
    """Schedule a new activity on any Odoo record.

    Args:
        res_model: Technical model name (e.g. ``"crm.lead"``).
        res_id: The record id the activity is linked to.
        activity_type_id: ``mail.activity.type`` record id.
        summary: Short summary / title.
        note: Detailed note (HTML allowed).
        date_deadline: Due date in ``YYYY-MM-DD`` format.

    Returns:
        int: The id of the newly created activity.
    """
    values = {
        "res_model_id": odoo_client.execute(
            "ir.model", "search", [["model", "=", res_model]], limit=1
        )[0],
        "res_id": res_id,
        "activity_type_id": activity_type_id,
        "summary": summary,
        "note": note,
        "date_deadline": date_deadline,
    }
    return odoo_client.create("mail.activity", values)


def mark_done(activity_id: int, feedback: str = "") -> bool:
    """Mark an activity as done.

    Args:
        activity_id: The activity record id.
        feedback: Optional feedback text.

    Returns:
        bool: True on success.
    """
    try:
        odoo_client.execute(
            "mail.activity", "action_feedback", [activity_id], feedback=feedback
        )
        return True
    except Exception:
        return odoo_client.unlink("mail.activity", [activity_id])


def list_activities(res_model: str, res_id: int) -> list[dict]:
    """List all activities for a specific record.

    Args:
        res_model: Technical model name.
        res_id: The record id.

    Returns:
        list[dict]: Activity records.
    """
    domain = [["res_model", "=", res_model], ["res_id", "=", res_id]]
    return odoo_client.search_read("mail.activity", domain, FIELDS)


def get_overdue_activities(user_id: int | None = None) -> list[dict]:
    """Return overdue activities, optionally filtered by assigned user.

    Args:
        user_id: Filter to activities assigned to this user id.

    Returns:
        list[dict]: Overdue activity records.
    """
    domain: list = [["state", "=", "overdue"]]
    if user_id:
        domain.append(["user_id", "=", user_id])
    return odoo_client.search_read("mail.activity", domain, FIELDS)
