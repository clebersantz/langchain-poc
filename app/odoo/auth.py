"""Odoo authentication helpers."""

from app.odoo.client import odoo_client
from app.utils.logger import get_logger

logger = get_logger(__name__)


def test_connection() -> bool:
    """Test the Odoo XML-RPC connection by attempting authentication.

    Returns:
        bool: True if the connection and authentication succeed, False otherwise.
    """
    try:
        odoo_client.reset_auth()
        uid = odoo_client.authenticate()
        version = odoo_client.get_version()
        logger.info(
            "odoo_connection_ok",
            uid=uid,
            server_version=version.get("server_version"),
        )
        return True
    except Exception as exc:
        logger.warning("odoo_connection_failed", error=str(exc))
        return False
