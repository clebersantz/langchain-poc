"""Integration test for Docker-based Odoo 16 CRM connectivity."""

import os

import pytest

from app.odoo.client import OdooClient


def _docker_odoo_env_ready() -> bool:
    required = ("ODOO_URL", "ODOO_DB", "ODOO_USER", "ODOO_API_KEY")
    return all(os.getenv(name) for name in required)


def test_docker_odoo_crm_leads_read():
    """Read CRM leads from Odoo to validate the Docker test stack."""
    if not _docker_odoo_env_ready():
        pytest.skip(
            "Set ODOO_URL, ODOO_DB, ODOO_USER and ODOO_API_KEY "
            "to run Docker Odoo CRM integration checks."
        )

    client = OdooClient()
    count = client.execute("crm.lead", "search_count", [])
    leads = client.search_read("crm.lead", [], ["name", "email_from"], limit=5)

    assert isinstance(count, int)
    assert count >= 0
    assert isinstance(leads, list)
    if leads:
        assert "name" in leads[0]
