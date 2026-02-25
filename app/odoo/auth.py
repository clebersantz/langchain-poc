"""Odoo authentication helpers."""

import xmlrpc.client

import httpx

from app.odoo.client import odoo_client
from app.utils.logger import get_logger

logger = get_logger(__name__)

HTTP_PROBE_TIMEOUT = 5.0


def _log_connection_details() -> None:
    """Log the Odoo connection configuration for debugging."""
    logger.info(
        "odoo_connection_config",
        url=odoo_client._url,
        db=odoo_client._db,
        user=odoo_client._user,
        api_key=odoo_client._api_key,
        common_endpoint=odoo_client._common_endpoint,
        object_endpoint=odoo_client._models_endpoint,
    )


def _probe_http_connection() -> None:
    """Probe the base Odoo URL over HTTP for debugging visibility."""
    try:
        response = httpx.get(
            odoo_client._url,
            timeout=HTTP_PROBE_TIMEOUT,
            follow_redirects=True,
        )
        if response.status_code >= 400:
            logger.warning(
                "odoo_http_probe_failed",
                url=odoo_client._url,
                status_code=response.status_code,
                reason=response.reason_phrase,
            )
            return
        logger.info(
            "odoo_http_probe_ok",
            url=odoo_client._url,
            status_code=response.status_code,
            reason=response.reason_phrase,
        )
    except httpx.HTTPError as exc:
        logger.warning(
            "odoo_http_probe_failed",
            url=odoo_client._url,
            error=str(exc),
        )


def test_connection() -> bool:
    """Test the Odoo XML-RPC connection by attempting authentication.

    Returns:
        bool: True if the connection and authentication succeed, False otherwise.
    """
    _log_connection_details()
    _probe_http_connection()
    try:
        odoo_client.reset_auth()
        version = odoo_client.get_version()
        uid = odoo_client.authenticate()
        logger.info(
            "odoo_connection_ok",
            uid=uid,
            server_version=version.get("server_version"),
        )
        return True
    except xmlrpc.client.ProtocolError as exc:
        logger.warning(
            "odoo_connection_failed",
            error=str(exc),
            url=exc.url,
            status_code=exc.errcode,
            reason=exc.errmsg,
        )
        return False
    except Exception as exc:
        logger.warning("odoo_connection_failed", error=str(exc))
        return False
