"""Unit tests for Docker Compose runtime settings."""

from pathlib import Path

import yaml


def test_agent_app_exposes_localhost_port_8000() -> None:
    """Compose config must publish app port on localhost directly on agent-app."""
    repo_root = Path(__file__).resolve().parents[2]
    compose_path = repo_root / "docker" / "docker-compose.yml"
    compose_data = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    agent_app = compose_data["services"]["agent-app"]
    command = agent_app["command"]
    ports = agent_app["ports"]

    assert command == ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    assert ports == ["127.0.0.1:8000:8000"]


def test_agent_app_no_external_network_required() -> None:
    """Compose config must NOT require any external network so agent-app starts standalone."""
    repo_root = Path(__file__).resolve().parents[2]
    compose_path = repo_root / "docker" / "docker-compose.yml"
    compose_data = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    top_level_networks = compose_data.get("networks", {})
    for net_name, net_cfg in (top_level_networks or {}).items():
        assert not (net_cfg or {}).get("external"), (
            f"Network '{net_name}' is marked external=true which prevents standalone startup"
        )


def test_agent_app_has_host_gateway_extra_host() -> None:
    """agent-app must add host.docker.internal so Odoo is reachable via host port on Linux."""
    repo_root = Path(__file__).resolve().parents[2]
    compose_path = repo_root / "docker" / "docker-compose.yml"
    compose_data = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    agent_app = compose_data["services"]["agent-app"]
    extra_hosts = agent_app.get("extra_hosts", [])

    assert "host.docker.internal:host-gateway" in extra_hosts, (
        "agent-app must include 'host.docker.internal:host-gateway' in extra_hosts "
        "so Odoo is reachable from inside the container on Linux hosts"
    )
