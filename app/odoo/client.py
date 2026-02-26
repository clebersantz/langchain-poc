"""Odoo 16 JSON-RPC client.

Provides a thin wrapper around Odoo's JSON-RPC endpoint (``/jsonrpc``) for
authentication, metadata, and CRUD operations via ``execute_kw``.
"""

from __future__ import annotations

import uuid
from typing import Any

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

JSONRPC_TIMEOUT = 10.0
EXECUTE_KW_ARG_COUNT = 7


class OdooJSONRPCError(RuntimeError):
    """JSON-RPC error returned by Odoo."""

    def __init__(
        self,
        message: str,
        *,
        code: int | None = None,
        data: Any | None = None,
        http_status: int | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.data = data
        self.http_status = http_status


def _normalize_odoo_url(url: str) -> str:
    """Normalize the Odoo base URL by stripping API path suffixes.

    Args:
        url: Raw Odoo URL from settings.

    Returns:
        str: Base Odoo URL without XML/JSON-RPC suffixes.
    """
    normalized = url.strip().rstrip("/")
    for suffix in (
        "/jsonrpc",
        "/xmlrpc/2/common",
        "/xmlrpc/2/object",
        "/xmlrpc/2",
        "/xmlrpc/common",
        "/xmlrpc/object",
        "/xmlrpc",
    ):
        if normalized.endswith(suffix):
            normalized = normalized[: -len(suffix)]
            break
    return normalized.rstrip("/")


class OdooClient:
    """JSON-RPC client for Odoo 16.

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
        self._jsonrpc_endpoint = f"{self._url}/jsonrpc"
        self._transport = "jsonrpc"
        self._web_authenticated = False

    def _decode_json_response(self, response: httpx.Response) -> dict[str, Any]:
        """Decode a JSON response and raise a typed error if parsing fails."""
        try:
            return response.json()
        except ValueError as exc:
            raise OdooJSONRPCError(
                "Invalid JSON-RPC response",
                http_status=response.status_code,
                data=response.text,
            ) from exc

    def _post_web_json(self, endpoint: str, params: dict[str, Any]) -> Any:
        """Call a web JSON endpoint that returns a JSON-RPC-like envelope."""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": params,
            "id": uuid.uuid4().hex,
        }
        response = httpx.post(endpoint, json=payload, timeout=JSONRPC_TIMEOUT)
        response.raise_for_status()
        data = self._decode_json_response(response)
        if "error" in data:
            error = data.get("error") or {}
            raise OdooJSONRPCError(
                error.get("message", "JSON-RPC error"),
                code=error.get("code"),
                data=error.get("data"),
                http_status=response.status_code,
            )
        if "result" not in data:
            raise OdooJSONRPCError(
                "Malformed JSON-RPC response",
                http_status=response.status_code,
                data=data,
            )
        return data["result"]

    def _web_service_call(self, service: str, method: str, args: list[Any]) -> Any:
        """Fallback RPC transport via Odoo web JSON controllers."""
        if service == "common" and method == "version":
            return self._post_web_json(f"{self._url}/web/webclient/version_info", {})

        if service == "common" and method == "login":
            result = self._post_web_json(
                f"{self._url}/web/session/authenticate",
                {
                    "db": args[0],
                    "login": args[1],
                    "password": args[2],
                },
            )
            try:
                uid = int(result.get("uid") or 0)
            except (TypeError, ValueError):
                uid = 0
            if uid > 0:
                self._web_authenticated = True
            return uid

        if service == "object" and method == "execute_kw":
            if len(args) != EXECUTE_KW_ARG_COUNT:
                raise OdooJSONRPCError(
                    f"execute_kw requires exactly {EXECUTE_KW_ARG_COUNT} arguments, got {len(args)}",
                    data={"args_length": len(args)},
                )
            db, _uid_arg, _password_arg, model, model_method, method_args, method_kwargs = args
            if not self._web_authenticated:
                login_uid = self._web_service_call("common", "login", [db, self._user, self._api_key])
                if not login_uid:
                    logger.warning("odoo_web_authentication_failed", db=db, user=self._user)
                    raise ValueError("Odoo authentication failed — check ODOO_USER and ODOO_API_KEY")
            return self._post_web_json(
                f"{self._url}/web/dataset/call_kw/{model}/{model_method}",
                {
                    "model": model,
                    "method": model_method,
                    "args": method_args,
                    "kwargs": method_kwargs,
                },
            )

        raise OdooJSONRPCError(
            f"Unsupported Odoo service/method: {service}.{method}. "
            "Supported in web mode: common.version, common.login, object.execute_kw"
        )

    def _jsonrpc_call(self, service: str, method: str, args: list[Any]) -> Any:
        """Call an Odoo JSON-RPC service method.

        Args:
            service: Odoo service name (``common`` or ``object``).
            method: Service method to call.
            args: Positional arguments for the method.

        Returns:
            Any: The ``result`` field from the JSON-RPC response.

        Raises:
            OdooJSONRPCError: If the response contains a JSON-RPC error.
            httpx.HTTPError: If the HTTP request fails.
        """
        if self._transport == "web":
            return self._web_service_call(service, method, args)

        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {"service": service, "method": method, "args": args},
            "id": uuid.uuid4().hex,
        }
        try:
            response = httpx.post(
                self._jsonrpc_endpoint,
                json=payload,
                timeout=JSONRPC_TIMEOUT,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                self._transport = "web"
                logger.warning(
                    "odoo_jsonrpc_404_fallback_to_web",
                    jsonrpc_endpoint=self._jsonrpc_endpoint,
                    fallback_endpoint=f"{self._url}/web/session/authenticate",
                )
                return self._web_service_call(service, method, args)
            raise
        data = self._decode_json_response(response)
        if "error" in data:
            error = data.get("error") or {}
            raise OdooJSONRPCError(
                error.get("message", "JSON-RPC error"),
                code=error.get("code"),
                data=error.get("data"),
                http_status=response.status_code,
            )
        if "result" not in data:
            raise OdooJSONRPCError(
                "Malformed JSON-RPC response",
                http_status=response.status_code,
                data=data,
            )
        return data["result"]

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
        uid = self._jsonrpc_call(
            "common",
            "login",
            [self._db, self._user, self._api_key],
        )
        if not uid:
            raise ValueError("Odoo authentication failed — check ODOO_USER and ODOO_API_KEY")
        self._uid = uid
        logger.info("odoo_authenticated", uid=uid)
        return uid

    def reset_auth(self) -> None:
        """Clear the cached uid so the next call re-authenticates."""
        self._uid = None
        self._web_authenticated = False

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def get_version(self) -> dict:
        """Return the Odoo server version information."""
        return self._jsonrpc_call("common", "version", [])

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
        return self._jsonrpc_call(
            "object",
            "execute_kw",
            [self._db, uid, self._api_key, model, method, list(args), kwargs],
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
