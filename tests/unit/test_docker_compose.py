"""Unit tests for Docker Compose runtime settings."""

from pathlib import Path

import yaml


def test_agent_app_binds_to_all_interfaces() -> None:
    """Compose config must run Uvicorn on 0.0.0.0 for host accessibility."""
    repo_root = Path(__file__).resolve().parents[2]
    compose_path = repo_root / "docker" / "docker-compose.yml"
    compose_data = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    agent_app = compose_data["services"]["agent-app"]
    command = agent_app["command"]

    assert command == ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
