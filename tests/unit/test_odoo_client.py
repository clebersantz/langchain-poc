"""Unit tests for the Odoo JSON-RPC client (app/odoo/client.py)."""

from unittest.mock import MagicMock, patch

import httpx
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


class TestOdooClientWebFallback:
    """Tests for /jsonrpc 404 fallback to web JSON endpoints."""

    def test_jsonrpc_404_falls_back_to_web_login(self) -> None:
        """Client should fallback to /web/session/authenticate when /jsonrpc is unavailable."""
        from app.odoo.client import OdooClient

        client = OdooClient.__new__(OdooClient)
        client._url = "http://localhost:8069"
        client._db = "odoo"
        client._user = "admin@test.com"
        client._api_key = "test_key"
        client._uid = None
        client._jsonrpc_endpoint = "http://localhost:8069/jsonrpc"
        client._transport = "jsonrpc"
        client._web_authenticated = False

        jsonrpc_request = httpx.Request("POST", client._jsonrpc_endpoint)
        web_auth_request = httpx.Request("POST", "http://localhost:8069/web/session/authenticate")
        jsonrpc_404 = httpx.Response(404, request=jsonrpc_request)
        web_auth_ok = httpx.Response(
            200,
            request=web_auth_request,
            json={"jsonrpc": "2.0", "id": "1", "result": {"uid": 7}},
        )
        with patch("app.odoo.client.httpx.post", side_effect=[jsonrpc_404, web_auth_ok]) as mock_post:
            uid = client._jsonrpc_call("common", "login", ["odoo", "admin@test.com", "test_key"])

        assert uid == 7
        assert client._transport == "web"
        assert client._web_authenticated is True
        assert mock_post.call_count == 2

    def test_web_transport_execute_kw_uses_call_kw_endpoint(self) -> None:
        """Web transport should route execute_kw to /web/dataset/call_kw."""
        from app.odoo.client import OdooClient

        client = OdooClient.__new__(OdooClient)
        client._url = "http://localhost:8069"
        client._db = "odoo"
        client._user = "admin@test.com"
        client._api_key = "test_key"
        client._uid = 7
        client._jsonrpc_endpoint = "http://localhost:8069/jsonrpc"
        client._transport = "web"
        client._web_authenticated = True

        call_kw_request = httpx.Request("POST", "http://localhost:8069/web/dataset/call_kw/crm.lead/search_read")
        call_kw_ok = httpx.Response(
            200,
            request=call_kw_request,
            json={"jsonrpc": "2.0", "id": "1", "result": [{"id": 1, "name": "Lead A"}]},
        )
        with patch("app.odoo.client.httpx.post", return_value=call_kw_ok) as mock_post:
            result = client._jsonrpc_call(
                "object",
                "execute_kw",
                ["odoo", 7, "test_key", "crm.lead", "search_read", [[]], {"fields": ["id", "name"]}],
            )

        assert result == [{"id": 1, "name": "Lead A"}]
        assert mock_post.call_args.args[0].endswith("/web/dataset/call_kw/crm.lead/search_read")
