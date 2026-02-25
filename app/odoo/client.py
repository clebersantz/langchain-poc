"""Odoo 16 XML-RPC client.

Provides a thin wrapper around Python's built-in ``xmlrpc.client`` to communicate
with an Odoo 16 instance using the two standard XML-RPC endpoints:

* ``/xmlrpc/2/common``  — version info and authentication
* ``/xmlrpc/2/object``  — model CRUD operations

# TODO: v18 - add native REST API support when migrating to Odoo 18
"""

import xmlrpc.client
from typing import Any

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _normalize_odoo_url(url: str) -> str:
    """Normalize the Odoo base URL by stripping XML-RPC path suffixes.

    Args:
        url: Raw Odoo URL from settings.

    Returns:
        str: Base Odoo URL without ``/xmlrpc/2`` suffixes.
    """
    normalized = url.strip().rstrip("/")
    for suffix in ("/xmlrpc/2/common", "/xmlrpc/2/object", "/xmlrpc/2"):
        if normalized.endswith(suffix):
            normalized = normalized[: -len(suffix)]
            break
    return normalized.rstrip("/")


def _build_server_proxy(endpoint: str) -> xmlrpc.client.ServerProxy:
    """Create a ServerProxy configured for Odoo XML-RPC calls.

    Args:
        endpoint: Full XML-RPC endpoint URL.

    Returns:
        xmlrpc.client.ServerProxy: Configured proxy instance.
    """
    return xmlrpc.client.ServerProxy(
        endpoint,
        allow_none=True,
        use_builtin_types=True,
    )


class OdooClient:
    """XML-RPC client for Odoo 16.

    Usage::

        from app.odoo.client import odoo_client

        uid = odoo_client.authenticate()
        leads = odoo_client.search_read("crm.lead", [], ["name", "email_from"])
    """

    def __init__(self) -> None:
        self._url = _normalize_odoo_url(settings.odoo_url)
        self._db = settings.odoo_db
        self._user = settings.odoo_user
        self._api_key = settings.odoo_api_key
        self._uid: int | None = None

        self._common_endpoint = f"{self._url}/xmlrpc/2/common"
        self._models_endpoint = f"{self._url}/xmlrpc/2/object"
        self._common = _build_server_proxy(self._common_endpoint)
        self._models = _build_server_proxy(self._models_endpoint)

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def authenticate(self) -> int:
        """Authenticate with Odoo and return (cached) user id.

        Returns:
            int: The Odoo uid for the authenticated user.

        Raises:
            ValueError: If authentication fails.
        """
        if self._uid is not None:
            return self._uid
        uid = self._common.authenticate(self._db, self._user, self._api_key, {})
        if not uid:
            raise ValueError("Odoo authentication failed — check ODOO_USER and ODOO_API_KEY")
        self._uid = uid
        logger.info("odoo_authenticated", uid=uid)
        return uid

    def reset_auth(self) -> None:
        """Clear the cached uid so the next call re-authenticates."""
        self._uid = None

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def get_version(self) -> dict:
        """Return the Odoo server version information.

        Returns:
            dict: Server version details from ``/xmlrpc/2/common``.
        """
        return self._common.version()

    # ------------------------------------------------------------------
    # Generic execute
    # ------------------------------------------------------------------

    def execute(self, model: str, method: str, *args: Any, **kwargs: Any) -> Any:
        """Execute an arbitrary method on an Odoo model.

        Args:
            model: Odoo model technical name (e.g. ``"crm.lead"``).
            method: Method name (e.g. ``"search_read"``, ``"write"``).
            *args: Positional arguments forwarded to ``execute_kw``.
            **kwargs: Keyword arguments forwarded to ``execute_kw``.

        Returns:
            Any: The return value of the Odoo method.
        """
        uid = self.authenticate()
        return self._models.execute_kw(
            self._db, uid, self._api_key, model, method, list(args), kwargs
        )

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def search_read(
        self,
        model: str,
        domain: list,
        fields: list[str],
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """Search for records and return selected fields.

        Args:
            model: Odoo model name.
            domain: Search domain (list of tuples).
            fields: Field names to return.
            limit: Maximum number of records.
            offset: Number of records to skip.

        Returns:
            list[dict]: Matching records with requested fields.
        """
        return self.execute(
            model,
            "search_read",
            domain,
            fields=fields,
            limit=limit,
            offset=offset,
        )

    def create(self, model: str, values: dict) -> int:
        """Create a new record.

        Args:
            model: Odoo model name.
            values: Field values for the new record.

        Returns:
            int: The id of the newly created record.
        """
        return self.execute(model, "create", values)

    def write(self, model: str, ids: list[int], values: dict) -> bool:
        """Update existing records.

        Args:
            model: Odoo model name.
            ids: List of record ids to update.
            values: Field values to write.

        Returns:
            bool: True on success.
        """
        return self.execute(model, "write", ids, values)

    def unlink(self, model: str, ids: list[int]) -> bool:
        """Delete records.

        Args:
            model: Odoo model name.
            ids: List of record ids to delete.

        Returns:
            bool: True on success.
        """
        return self.execute(model, "unlink", ids)


# Module-level singleton
odoo_client = OdooClient()
