"""Unit tests for Odoo auth helpers."""

from unittest.mock import patch

import httpx

from app.odoo import auth


def test_connection_runs_http_probe_and_authentication() -> None:
    """test_connection should probe HTTP and authenticate successfully."""
    response = httpx.Response(
        200,
        request=httpx.Request("GET", "http://odoo:8069"),
    )
    with (
        patch("app.odoo.auth.httpx.get", return_value=response) as mock_get,
        patch("app.odoo.auth.odoo_client") as mock_client,
    ):
        mock_client._url = "http://odoo:8069"
        mock_client._db = "odoo"
        mock_client._user = "user@example.com"
        mock_client._api_key = "secret-key"
        mock_client._common_endpoint = "http://odoo:8069/xmlrpc/2/common"
        mock_client._models_endpoint = "http://odoo:8069/xmlrpc/2/object"
        mock_client.reset_auth.return_value = None
        mock_client.get_version.return_value = {"server_version": "16.0"}
        mock_client.authenticate.return_value = 7

        assert auth.test_connection() is True

        mock_get.assert_called_once_with(
            "http://odoo:8069",
            timeout=auth.HTTP_PROBE_TIMEOUT,
            follow_redirects=True,
        )
        mock_client.reset_auth.assert_called_once()
        mock_client.get_version.assert_called_once()
        mock_client.authenticate.assert_called_once()
