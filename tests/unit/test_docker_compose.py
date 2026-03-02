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


def test_agent_app_connects_to_odoo_dev_network() -> None:
    """agent-app must be connected to odoo-dev_default to reach doodba ODOO containers."""
    repo_root = Path(__file__).resolve().parents[2]
    compose_path = repo_root / "docker" / "docker-compose.yml"
    compose_data = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    top_level_networks = compose_data.get("networks", {})
    assert "odoo-dev_default" in top_level_networks, (
        "docker-compose.yml must define the 'odoo-dev_default' network"
    )
    assert (top_level_networks["odoo-dev_default"] or {}).get("external"), (
        "Network 'odoo-dev_default' must be marked as external=true"
    )

    agent_app = compose_data["services"]["agent-app"]
    agent_networks = agent_app.get("networks", [])
    assert "odoo-dev_default" in agent_networks, (
        "agent-app must be connected to 'odoo-dev_default' network to reach the doodba ODOO proxy"
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
