"""Integration tests for AI-agent driven Odoo 16 CRM connectivity."""

import json
import os
import time

import pytest

from app.agents.odoo_api_agent import OdooAPIAgent
from app.odoo.client import OdooClient

NOTE_TEXT = "Hello! This is an CRM Bot automation test."

_last_updated_lead_id: int | None = None


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


def _extract_json_value(text: str, expected_type: type[dict] | type[list]) -> dict | list:
    start_token = "{" if expected_type is dict else "["
    start_index = text.find(start_token)
    assert start_index != -1, f"Agent response did not include JSON payload: {text}"
    decoder = json.JSONDecoder()
    parsed, _ = decoder.raw_decode(text[start_index:])
    assert isinstance(parsed, expected_type), f"Expected {expected_type.__name__} JSON payload: {text}"
    return parsed


def test_odoo_agent_connection():
    """Validate Odoo connection through the AI agent."""
    if not _odoo_agent_env_ready():
        pytest.skip(
            "Set ODOO_URL, ODOO_DB, ODOO_USER, ODOO_API_KEY and OPENAI_API_KEY "
            "to run AI-agent Odoo integration checks."
        )

    client = OdooClient()
    _wait_for_odoo_ready(client)
    version_info = client.get_version()
    server_version = str(version_info.get("server_version", ""))
    agent = OdooAPIAgent()
    response = agent.run(
        "Use your Odoo CRM tools to verify connectivity. "
        "Connect to ODOO, get ODOO version and reply exactly CONNECTED if version >= 16.0"
    )

    print(f"Odoo connection successful. Version: {server_version}")
    assert isinstance(response, str)
    assert "CONNECTED" in response.upper()
    assert server_version.startswith("16.0")


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
        "Call search_crm_leads with query '' and limit 3. Return only JSON array."
    )

    leads = _extract_json_value(response, list)
    assert isinstance(leads, list)
    assert len(leads) > 0, "Expected demo CRM leads, but agent returned none."
    assert len(leads) <= 3
    lead_names = [str(lead.get("name", "")).strip() for lead in leads]
    print(f"CRM leads read ({len(leads)}): {lead_names}")
    for lead in leads:
        assert "id" in lead
        assert "name" in lead


def test_odoo_agent_first_crm_lead_write_note():
    """Get first CRM lead and write an internal note through AI agent."""
    if not _odoo_agent_env_ready():
        pytest.skip(
            "Set ODOO_URL, ODOO_DB, ODOO_USER, ODOO_API_KEY and OPENAI_API_KEY "
            "to run AI-agent Odoo integration checks."
        )

    client = OdooClient()
    _wait_for_odoo_ready(client)
    agent = OdooAPIAgent()
    response = agent.run(
        "Get the first CRM lead. "
        "If there is no lead, create one minimal lead. "
        f"Then post an internal note with this exact text: {NOTE_TEXT} "
        "using add_note_to_crm_lead. After posting, reread that CRM lead and verify the posted "
        "note matches. Return only JSON object with lead_id and message_id."
    )

    result = _extract_json_value(response, dict)
    assert isinstance(result, dict)
    lead_id = int(result["lead_id"])
    message_id = int(result["message_id"])
    assert lead_id > 0
    assert message_id > 0

    global _last_updated_lead_id
    _last_updated_lead_id = lead_id

    lead_rows = client.search_read(
        "crm.lead",
        [["id", "=", lead_id]],
        ["id", "name", "message_ids"],
        limit=1,
    )
    assert len(lead_rows) == 1
    lead_message_ids = lead_rows[0].get("message_ids", [])
    assert isinstance(lead_message_ids, list)
    assert message_id in lead_message_ids

    messages = client.search_read(
        "mail.message",
        [["id", "=", message_id], ["model", "=", "crm.lead"], ["res_id", "=", lead_id]],
        ["id", "body"],
        limit=1,
    )
    assert len(messages) == 1
    note_body = str(messages[0].get("body", ""))
    print(f"Posted note for lead {lead_id}: {note_body}")
    assert NOTE_TEXT in note_body


def test_odoo_agent_verify_crm_lead_note():
    """Verify that the note posted in the previous test persists on the CRM lead."""
    if not _odoo_agent_env_ready():
        pytest.skip(
            "Set ODOO_URL, ODOO_DB, ODOO_USER, ODOO_API_KEY and OPENAI_API_KEY "
            "to run AI-agent Odoo integration checks."
        )

    if _last_updated_lead_id is None:
        pytest.skip("test_odoo_agent_first_crm_lead_write_note did not run or did not set lead_id.")

    client = OdooClient()
    _wait_for_odoo_ready(client)
    lead_id = _last_updated_lead_id

    messages = client.search_read(
        "mail.message",
        [["model", "=", "crm.lead"], ["res_id", "=", lead_id]],
        ["id", "body"],
        limit=100,
    )
    assert len(messages) > 0, f"No messages found for CRM lead {lead_id}."
    note_bodies = [str(msg.get("body", "")) for msg in messages]
    assert any(NOTE_TEXT in body for body in note_bodies), (
        f"Expected note '{NOTE_TEXT}' not found in messages of lead {lead_id}: {note_bodies}"
    )
    print(f"Note verified for lead {lead_id}.")
