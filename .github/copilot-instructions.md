# Copilot instructions for langchain-poc

- Language/runtime: Python 3.11 with FastAPI + LangChain.
- Entry point: `app/main.py`; settings live in `app/config.py` via Pydantic `BaseSettings` and `.env` (do not commit secrets).
- Agent logic lives in `app/agents/` (supervisor, KB, workflow, Odoo API). Odoo XML-RPC client is in `app/odoo/`.
- Knowledge base documents live in `knowledge_base/`; ingestion is done via `scripts/ingest_knowledge_base.py`.
- Frontend is static HTML/JS/CSS in `frontend/`, served at `/static`.
- Tests use `pytest` (`tests/unit`, `tests/integration`). Lint/format with `ruff` (line length 100).
