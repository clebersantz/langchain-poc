"""Unit tests for Docker Compose runtime settings."""

from pathlib import Path

import yaml


def test_agent_app_exposes_localhost_port_8000() -> None:
    """Compose config must publish app port on localhost through proxy."""
    repo_root = Path(__file__).resolve().parents[2]
    compose_path = repo_root / "docker" / "docker-compose.yml"
    compose_data = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    agent_app = compose_data["services"]["agent-app"]
    agent_proxy = compose_data["services"]["agent-proxy"]
    command = agent_app["command"]
    ports = agent_proxy["ports"]

    assert command == ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    assert "ports" not in agent_app
    assert agent_proxy["environment"] == {"PORT": "8000", "TARGET": "agent-app"}
    assert ports == ["127.0.0.1:8000:8000"]
