"""Integration test for Docker-based Odoo 16 CRM connectivity."""

import os
import time

import pytest

from app.odoo.client import OdooClient


NOTE_TEXT = "Hello! This is an CRM Bot automation test."


def _docker_odoo_env_ready() -> bool:
    required = ("ODOO_URL", "ODOO_DB", "ODOO_USER", "ODOO_API_KEY")
    return all(os.getenv(name) for name in required)


def _wait_for_odoo_ready(client: OdooClient, timeout_s: int = 60) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            client.get_version()
            return
        except Exception:
            time.sleep(2)
    pytest.fail("Odoo test container did not become ready in time")


def test_docker_odoo_connection():
    """Validate Odoo authentication and basic connection."""
    if not _docker_odoo_env_ready():
        pytest.skip(
            "Set ODOO_URL, ODOO_DB, ODOO_USER and ODOO_API_KEY "
            "to run Docker Odoo CRM integration checks."
        )

    client = OdooClient()
    _wait_for_odoo_ready(client)
    uid = client.authenticate()

    assert isinstance(uid, int)
    assert uid > 0


def test_docker_odoo_crm_leads_read_limit_3():
    """Read CRM leads using a maximum limit of 3 records."""
    if not _docker_odoo_env_ready():
        pytest.skip(
            "Set ODOO_URL, ODOO_DB, ODOO_USER and ODOO_API_KEY "
            "to run Docker Odoo CRM integration checks."
        )

    client = OdooClient()
    _wait_for_odoo_ready(client)
    leads = client.search_read("crm.lead", [], ["id", "name", "email_from"], limit=3)

    assert isinstance(leads, list)
    assert len(leads) <= 3
    if leads:
        assert "id" in leads[0]
        assert "name" in leads[0]


def test_docker_odoo_crm_first_lead_write_note():
    """Get the first CRM lead and write an internal note on it."""
    if not _docker_odoo_env_ready():
        pytest.skip(
            "Set ODOO_URL, ODOO_DB, ODOO_USER and ODOO_API_KEY "
            "to run Docker Odoo CRM integration checks."
        )

    client = OdooClient()
    _wait_for_odoo_ready(client)
    leads = client.search_read("crm.lead", [], ["id", "name"], limit=1)
    if not leads:
        lead_id = client.create("crm.lead", {"name": "CRM Bot Automation Lead", "type": "lead"})
    else:
        lead_id = leads[0]["id"]

    message_id = client.execute(
        "crm.lead",
        "message_post",
        [lead_id],
        body=NOTE_TEXT,
        message_type="comment",
        subtype_xmlid="mail.mt_note",
    )

    assert isinstance(lead_id, int)
    assert lead_id > 0
    assert isinstance(message_id, int)
    assert message_id > 0
