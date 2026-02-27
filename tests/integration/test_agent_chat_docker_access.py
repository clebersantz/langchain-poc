"""Integration checks for host access to static frontend in Docker-based CI runs."""

import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pytest

STATIC_FRONTEND_URL = os.getenv("AGENT_STATIC_URL", "http://localhost:8000/static/index.html")


def _wait_for_static_frontend(url: str, timeout_s: int = 60) -> None:
    deadline = time.time() + timeout_s
    last_error = "unreachable"
    while time.time() < deadline:
        request = Request(url, method="GET")
        try:
            with urlopen(request, timeout=5) as response:
                body = response.read().decode("utf-8", errors="ignore")
                if response.status == 200 and "CRM Assistant" in body:
                    return
                last_error = f"unexpected status {response.status}"
        except HTTPError as error:
            last_error = f"http {error.code}"
        except URLError as error:
            last_error = str(error.reason)
        except Exception as error:  # pragma: no cover - defensive branch
            last_error = str(error)
        time.sleep(2)

    pytest.fail(f"Static frontend not reachable from host at {url}: {last_error}")


def test_static_frontend_reachable_from_host_in_ci() -> None:
    """Ensure host machine can reach /static/index.html in CI docker runs."""
    if not os.getenv("RUN_DOCKER_STATIC_TEST"):
        pytest.skip("Set RUN_DOCKER_STATIC_TEST=1 to run host-to-container connectivity checks.")

    _wait_for_static_frontend(STATIC_FRONTEND_URL)
