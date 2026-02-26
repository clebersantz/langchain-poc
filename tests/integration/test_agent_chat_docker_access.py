"""Integration checks for host access to chat endpoint in Docker-based CI runs."""

import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pytest

CHAT_ENDPOINT_URL = os.getenv("AGENT_CHAT_URL")


def _wait_for_chat_endpoint(url: str, timeout_s: int = 60) -> None:
    deadline = time.time() + timeout_s
    last_error = "unreachable"
    while time.time() < deadline:
        request = Request(
            url,
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=5) as response:
                if response.status in (200, 422):
                    return
                last_error = f"unexpected status {response.status}"
        except HTTPError as error:
            if error.code == 422:
                return
            last_error = f"http {error.code}"
        except URLError as error:
            last_error = str(error.reason)
        except Exception as error:  # pragma: no cover - defensive branch
            last_error = str(error)
        time.sleep(2)

    pytest.fail(f"Chat endpoint not reachable from host at {url}: {last_error}")


def test_chat_endpoint_reachable_from_host_in_ci() -> None:
    """Ensure host machine can reach POST /chat in CI docker runs."""
    if not CHAT_ENDPOINT_URL:
        pytest.skip("Set AGENT_CHAT_URL to run host-to-container chat connectivity checks.")

    _wait_for_chat_endpoint(CHAT_ENDPOINT_URL)
