# Copilot instructions for langchain-poc

## Project overview

`langchain-poc` is a multi-agent LangChain application that integrates with an Odoo 16 CRM instance via XML-RPC. It exposes a FastAPI HTTP API and a static chat frontend, enabling users to ask CRM knowledge-base questions, query/update Odoo data, and trigger automated CRM workflows through a single conversational interface.

## Technology stack

- **Language/runtime**: Python 3.11
- **API framework**: FastAPI
- **Agent framework**: LangChain ≥ 0.2
- **LLM**: OpenAI (GPT-4o / GPT-4o-mini)
- **Embeddings**: OpenAI `text-embedding-3-small`
- **Vector store**: ChromaDB (persistent on disk at `storage/chroma_db/`)
- **Persistent memory**: SQLite via `SQLChatMessageHistory` (`storage/sessions.db`)
- **Odoo transport**: XML-RPC (`/xmlrpc/2/object`)
- **Frontend**: Vanilla HTML/JS/CSS in `frontend/`, served at `/static`
- **Containerisation**: Docker + Docker Compose

## Directory structure

```
app/
  main.py          # FastAPI entry point; registers routers and mounts /static
  config.py        # Pydantic BaseSettings — all config from env / .env
  agents/          # SupervisorAgent, KBAgent, OdooAPIAgent, WorkflowAgent, BaseAgent
  api/routes/      # FastAPI routers: chat, workflows, kb, webhooks
  odoo/            # OdooClient XML-RPC wrapper (client.py, auth.py)
  memory/          # SQLite session history helpers
  tools/           # LangChain tool definitions used by agents
  workflows/       # WorkflowRegistry and BaseWorkflow; concrete workflow classes
  utils/           # Structured logger (structlog)
knowledge_base/    # Markdown documents ingested into ChromaDB
scripts/           # ingest_knowledge_base.py — run once to populate ChromaDB
tests/
  unit/            # Fast tests, no external services required
  integration/     # Tests requiring a running Odoo / LLM (skipped in CI by default)
frontend/          # Static HTML/JS/CSS chat UI
storage/           # Runtime data: chroma_db/ and sessions.db (git-ignored)
```

## Development setup

```bash
cp .env.example .env          # fill in OPENAI_API_KEY, ODOO_* values
pip install -r requirements.txt
python scripts/ingest_knowledge_base.py   # populate ChromaDB (one-time)
uvicorn app.main:app --reload             # start dev server on :8000
```

## Coding conventions

- **Line length**: 100 characters (enforced by `ruff`).
- **Formatter/linter**: `ruff` — run with `ruff check .` and `ruff format .`.
- **Type hints**: required on all public functions and class methods.
- **Docstrings**: Google-style; include `Args:` and `Returns:` sections for non-trivial functions.
- **Logging**: use `app/utils/logger.py` (`get_logger(__name__)`) with structured key-value pairs; never use `print()`.
- **Secrets**: never hard-code credentials; always read from `app/config.settings`.
- **Do not commit** `.env`, `storage/`, or any file with secrets.

## Agent patterns

All agents inherit from `app/agents/base_agent.py` (`BaseAgent`). To add a new agent:
1. Create `app/agents/<name>_agent.py` subclassing `BaseAgent`.
2. Pass `name`, `model` (from `settings`), `tools`, and `system_prompt` to `super().__init__()`.
3. Add the model name constant to `app/config.py` (`Settings`).
4. Wire the agent into `SupervisorAgent` in `app/agents/supervisor.py` and add a routing rule.

## Adding a new workflow

1. Create a class in `app/workflows/` that inherits `BaseWorkflow` and implements `execute(context)`.
2. Register it in `WorkflowRegistry` (see `app/workflows/registry.py`).
3. No changes to routing needed; the `WorkflowAgent` discovers registered workflows automatically.

## Adding a new API route

1. Create `app/api/routes/<name>.py` with an `APIRouter`.
2. Import and register the router in `app/main.py` with an appropriate prefix.

## Testing

```bash
pytest tests/unit          # fast, no external services
pytest tests/integration   # requires Odoo + OpenAI (set env vars first)
pytest                     # all tests
```

- Unit tests live in `tests/unit/` and must not require real LLM or Odoo connections.
- Use `unittest.mock.MagicMock` and module-level stubs for heavy optional dependencies (LangChain, OpenAI) — see `tests/unit/test_kb_agent.py` for the pattern.
- Integration tests live in `tests/integration/` and are expected to be skipped in CI unless credentials are provided.

## Environment variables (key ones)

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key |
| `ODOO_URL` | Odoo instance base URL (e.g. `http://localhost:8069`) |
| `ODOO_DB` | Odoo database name |
| `ODOO_USER` | Odoo login e-mail |
| `ODOO_API_KEY` | Odoo API key |
| `WEBHOOK_SECRET` | HMAC secret for webhook signature verification |

See `.env.example` for the full list and `app/config.py` for defaults.

## Important constraints

- No authentication on API endpoints — this is a POC; add API key/OAuth2 before production.
- Webhook signature verification is a TODO; see `app/api/routes/webhooks.py`.
- Odoo integration uses XML-RPC (v16); a REST API migration is planned for Odoo 18.
- The system prompt in `SupervisorAgent` supports both English and PT-BR; keep this bilingual behaviour when modifying prompts.
