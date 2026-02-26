"""Integration tests for AI-agent driven Odoo 16 CRM connectivity."""

import json
import os
import re
import time

import pytest

from app.agents.odoo_api_agent import OdooAPIAgent
from app.odoo.client import OdooClient

NOTE_TEXT = "Hello! This is an CRM Bot automation test."


def _odoo_agent_env_ready() -> bool:
    required = ("ODOO_URL", "ODOO_DB", "ODOO_USER", "ODOO_API_KEY", "OPENAI_API_KEY")
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


def _extract_json_value(text: str, pattern: str) -> dict | list:
    match = re.search(pattern, text, re.DOTALL)
    assert match, f"Agent response did not include JSON payload: {text}"
    return json.loads(match.group(0))


def test_odoo_agent_connection():
    """Validate Odoo connection through the AI agent."""
    if not _odoo_agent_env_ready():
        pytest.skip(
            "Set ODOO_URL, ODOO_DB, ODOO_USER, ODOO_API_KEY and OPENAI_API_KEY "
            "to run AI-agent Odoo integration checks."
        )

    _wait_for_odoo_ready(OdooClient())
    agent = OdooAPIAgent()
    response = agent.run(
        "Use your Odoo CRM tools to verify connectivity. "
        "Call search_crm_leads with query '' and limit 1, then reply exactly CONNECTED."
    )

    assert isinstance(response, str)
    assert "CONNECTED" in response.upper()


def test_odoo_agent_read_crm_leads_limit_3():
    """Read CRM leads through AI agent with maximum of 3 records."""
    if not _odoo_agent_env_ready():
        pytest.skip(
            "Set ODOO_URL, ODOO_DB, ODOO_USER, ODOO_API_KEY and OPENAI_API_KEY "
            "to run AI-agent Odoo integration checks."
        )

    _wait_for_odoo_ready(OdooClient())
    agent = OdooAPIAgent()
    response = agent.run(
        "Read CRM leads using max limit 3 items. "
        "Return only the JSON array from the tool output."
    )

    leads = _extract_json_value(response, r"\[\s*.*?\s*\]")
    assert isinstance(leads, list)
    assert len(leads) <= 3
    if leads:
        assert "id" in leads[0]


def test_odoo_agent_first_crm_lead_write_note():
    """Get first CRM lead and write an internal note through AI agent."""
    if not _odoo_agent_env_ready():
        pytest.skip(
            "Set ODOO_URL, ODOO_DB, ODOO_USER, ODOO_API_KEY and OPENAI_API_KEY "
            "to run AI-agent Odoo integration checks."
        )

    _wait_for_odoo_ready(OdooClient())
    agent = OdooAPIAgent()
    response = agent.run(
        "Get the first CRM lead. If there is no lead, create one minimal lead. "
        f"Then post an internal note with this exact text: {NOTE_TEXT} "
        "using add_note_to_crm_lead. Return only JSON object with lead_id and message_id."
    )

    result = _extract_json_value(response, r"\{\s*.*?\s*\}")
    assert isinstance(result, dict)
    assert int(result["lead_id"]) > 0
    assert int(result["message_id"]) > 0
