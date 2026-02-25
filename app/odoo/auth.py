"""Odoo authentication helpers."""

import httpx

from app.odoo.client import OdooJSONRPCError, odoo_client
from app.utils.logger import get_logger

logger = get_logger(__name__)

HTTP_PROBE_TIMEOUT = 5.0


def _serialize_jsonrpc_error_data(data: object | None) -> object | None:
    """Serialize JSON-RPC error data for structured logging.

    Args:
        data: JSON-RPC error payload from Odoo.

    Returns:
        object | None: Serializable error payload.
    """
    if data is None:
        return None
    if isinstance(data, (dict, list, str, int, float, bool)):
        return data
    return str(data)


def _log_connection_details() -> None:
    """Log the Odoo connection configuration for debugging."""
    logger.info(
        "odoo_connection_config",
        url=odoo_client._url,
        db=odoo_client._db,
        user=odoo_client._user,
        api_key=odoo_client._api_key,
        jsonrpc_endpoint=odoo_client._jsonrpc_endpoint,
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
    """Test the Odoo JSON-RPC connection by attempting authentication.

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
            jsonrpc_endpoint=odoo_client._jsonrpc_endpoint,
            api_key_present=bool(odoo_client._api_key),
            api_key_length=len(odoo_client._api_key),
        )
        phase = "version"
        version = odoo_client.get_version()
        logger.info(
            "odoo_version_ok",
            phase=phase,
            jsonrpc_endpoint=odoo_client._jsonrpc_endpoint,
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
    except OdooJSONRPCError as exc:
        logger.warning(
            "odoo_connection_failed",
            error=str(exc) or "JSON-RPC error",
            error_repr=repr(exc),
            error_type=exc.__class__.__name__,
            status_code=exc.http_status,
            jsonrpc_code=exc.code,
            jsonrpc_data=_serialize_jsonrpc_error_data(exc.data),
            jsonrpc_endpoint=odoo_client._jsonrpc_endpoint,
            phase=phase,
        )
        return False
    except httpx.HTTPError as exc:
        logger.warning(
            "odoo_connection_failed",
            error=str(exc),
            error_repr=repr(exc),
            error_type=exc.__class__.__name__,
            jsonrpc_endpoint=odoo_client._jsonrpc_endpoint,
            phase=phase,
        )
        return False
    except Exception as exc:
        logger.warning(
            "odoo_connection_failed",
            error=str(exc),
            error_repr=repr(exc),
            error_type=exc.__class__.__name__,
            jsonrpc_endpoint=odoo_client._jsonrpc_endpoint,
            phase=phase,
        )
        return False
