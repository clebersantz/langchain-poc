"""Unit test for static frontend availability without OpenAI configuration."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_static_frontend_available_without_openai_key() -> None:
    """Application should still serve /static/index.html without OPENAI_API_KEY."""
    repo_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env.pop("OPENAI_API_KEY", None)

    code = """
from fastapi.testclient import TestClient
from app.main import app

response = TestClient(app).get('/static/index.html')
raise SystemExit(0 if response.status_code == 200 else 1)
"""
    # Run in a subprocess so app imports with a clean environment (no OPENAI_API_KEY).
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
