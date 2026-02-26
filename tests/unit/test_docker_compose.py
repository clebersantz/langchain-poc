"""Unit tests for Docker Compose runtime settings."""

from pathlib import Path


def test_agent_app_binds_to_all_interfaces() -> None:
    """Compose config must run Uvicorn on 0.0.0.0 for host accessibility."""
    repo_root = Path(__file__).resolve().parents[2]
    compose_text = (repo_root / "docker" / "docker-compose.yml").read_text(encoding="utf-8")

    assert 'command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]' in (
        compose_text
    )
