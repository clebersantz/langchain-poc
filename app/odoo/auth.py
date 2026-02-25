"""Odoo authentication helpers."""

import xmlrpc.client

import httpx

from app.odoo.client import odoo_client
from app.utils.logger import get_logger

logger = get_logger(__name__)

HTTP_PROBE_TIMEOUT = 5.0


def _serialize_xmlrpc_headers(headers: object | None) -> dict[str, str] | None:
    """Serialize XML-RPC HTTP headers for structured logging.

    Args:
        headers: Headers from xmlrpc.client.ProtocolError.

    Returns:
        dict[str, str] | None: Header mapping for logs, if available.
    """
    if not headers:
        return None
    try:
        return {key: headers.get(key) for key in headers.keys()}
    except Exception:
        return {"raw": str(headers)}


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
                final_url=str(response.url),
                redirects=[str(item.url) for item in response.history],
                server=response.headers.get("server"),
            )
            return
        logger.info(
            "odoo_http_probe_ok",
            url=odoo_client._url,
            status_code=response.status_code,
            reason=response.reason_phrase,
            final_url=str(response.url),
            redirects=[str(item.url) for item in response.history],
            server=response.headers.get("server"),
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
    phase = "prepare"
    try:
        odoo_client.reset_auth()
        logger.info(
            "odoo_auth_attempt",
            db=odoo_client._db,
            user=odoo_client._user,
            common_endpoint=odoo_client._common_endpoint,
            object_endpoint=odoo_client._models_endpoint,
            api_key_present=bool(odoo_client._api_key),
            api_key_length=len(odoo_client._api_key),
        )
        phase = "version"
        version = odoo_client.get_version()
        logger.info(
            "odoo_version_ok",
            phase=phase,
            common_endpoint=odoo_client._common_endpoint,
            server_version=version.get("server_version"),
            protocol_version=version.get("protocol_version"),
        )
        phase = "authenticate"
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
            error=str(exc) or "ProtocolError",
            error_repr=repr(exc),
            error_type=exc.__class__.__name__,
            url=exc.url,
            status_code=exc.errcode,
            reason=exc.errmsg,
            headers=_serialize_xmlrpc_headers(exc.headers),
            common_endpoint=odoo_client._common_endpoint,
            object_endpoint=odoo_client._models_endpoint,
            phase=phase,
        )
        return False
    except Exception as exc:
        logger.warning(
            "odoo_connection_failed",
            error=str(exc),
            error_repr=repr(exc),
            error_type=exc.__class__.__name__,
            common_endpoint=odoo_client._common_endpoint,
            object_endpoint=odoo_client._models_endpoint,
            phase=phase,
        )
        return False
