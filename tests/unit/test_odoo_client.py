"""Unit tests for the Odoo JSON-RPC client (app/odoo/client.py)."""

from unittest.mock import MagicMock, patch

import pytest


class TestOdooClientAuthenticate:
    """Tests for OdooClient.authenticate()."""

    def test_authenticate_returns_uid_on_success(self):
        """authenticate() should cache and return the uid on successful auth."""
        from app.odoo.client import OdooClient

        client = OdooClient.__new__(OdooClient)
        client._url = "http://localhost:8069"
        client._db = "odoo"
        client._user = "admin@test.com"
        client._api_key = "test_key"
        client._uid = None
        client._jsonrpc_call = MagicMock(return_value=42)

        uid = client.authenticate()
        assert uid == 42
        assert client._uid == 42
        client._jsonrpc_call.assert_called_once_with(
            "common",
            "login",
            ["odoo", "admin@test.com", "test_key"],
        )

    def test_authenticate_raises_on_failure(self):
        """authenticate() should raise ValueError when Odoo returns False."""
        from app.odoo.client import OdooClient

        client = OdooClient.__new__(OdooClient)
        client._url = "http://localhost:8069"
        client._db = "odoo"
        client._user = "wrong@test.com"
        client._api_key = "bad_key"
        client._uid = None
        client._jsonrpc_call = MagicMock(return_value=False)

        with pytest.raises(ValueError, match="authentication failed"):
            client.authenticate()

    def test_authenticate_uses_cache(self):
        """authenticate() should not re-authenticate if uid is already cached."""
        from app.odoo.client import OdooClient

        client = OdooClient.__new__(OdooClient)
        client._uid = 7
        client._jsonrpc_call = MagicMock()

        uid = client.authenticate()
        assert uid == 7
        client._jsonrpc_call.assert_not_called()


class TestOdooClientInit:
    """Tests for OdooClient initialization."""

    def test_init_strips_jsonrpc_suffixes(self) -> None:
        """__init__ should normalize JSON-RPC suffixes from the base URL."""
        with patch("app.odoo.client.settings") as mock_settings:
            mock_settings.odoo_url = " http://odoo:8069/jsonrpc "
            mock_settings.odoo_db = "odoo"
            mock_settings.odoo_user = "admin@test.com"
            mock_settings.odoo_api_key = "test_key"

            from app.odoo.client import OdooClient

            client = OdooClient()

            assert client._url == "http://odoo:8069"
            assert client._jsonrpc_endpoint == "http://odoo:8069/jsonrpc"


class TestOdooClientSearchRead:
    """Tests for OdooClient.search_read()."""

    def test_search_read_calls_execute_kw(self):
        """search_read() should call execute_kw with the correct arguments."""
        from app.odoo.client import OdooClient

        client = OdooClient.__new__(OdooClient)
        client._uid = 1
        client._db = "odoo"
        client._api_key = "key"
        client._jsonrpc_call = MagicMock(return_value=[{"id": 1, "name": "Test Lead"}])

        result = client.search_read("crm.lead", [], ["id", "name"], limit=10)

        assert result == [{"id": 1, "name": "Test Lead"}]
        client._jsonrpc_call.assert_called_once()
        call_args = client._jsonrpc_call.call_args
        assert call_args[0][1] == "execute_kw"


class TestOdooClientCreate:
    """Tests for OdooClient.create()."""

    def test_create_returns_new_id(self):
        """create() should return the id of the newly created record."""
        from app.odoo.client import OdooClient

        client = OdooClient.__new__(OdooClient)
        client._uid = 1
        client._db = "odoo"
        client._api_key = "key"
        client._jsonrpc_call = MagicMock(return_value=99)

        new_id = client.create("crm.lead", {"name": "Test", "type": "lead"})
        assert new_id == 99
