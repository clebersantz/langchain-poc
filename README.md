# langchain-poc

**LangChain Multi-Agent Application integrated with Odoo 16 CRM (self-hosted)**

A proof-of-concept demonstrating a 4-agent LangChain architecture that can answer CRM knowledge-base questions, execute Odoo 16 CRUD operations via XML-RPC, and run pre-defined multi-step CRM workflows — all through a simple chat interface.

---

## Architecture

```
                         ┌─────────────────────────────────────────┐
                         │           FastAPI  (app/main.py)        │
                         │    POST /chat  |  GET/POST /workflows    │
                         │    POST /kb/ingest  |  POST /webhooks    │
                         └──────────────────┬──────────────────────┘
                                            │
                         ┌──────────────────▼──────────────────────┐
                         │         Supervisor Agent                │
                         │  • Routes intent (KB / CRM / Workflow)  │
                         │  • Persistent memory (SQLite)           │
                         │  • Bilingual (PT-BR / EN)               │
                         └────┬──────────────┬──────────────┬──────┘
                              │              │              │
               ┌──────────────▼──┐  ┌────────▼──────┐  ┌───▼────────────────┐
               │    KB Agent     │  │  Odoo API     │  │  Workflow Agent    │
               │  RAG over docs  │  │  Agent        │  │  Multi-step CRM    │
               │  ChromaDB +     │  │  XML-RPC CRUD │  │  workflows         │
               │  text-embed-3s  │  │  Stateless    │  │  Logs to SQLite    │
               └─────────────────┘  └───────────────┘  └────────────────────┘
                                            │
                         ┌──────────────────▼──────────────────────┐
                         │              Odoo 16 CRM                │
                         │         XML-RPC  /xmlrpc/2/object       │
                         └─────────────────────────────────────────┘
```

---

## Prerequisites

- Python 3.11+
- An Odoo 16 instance (self-hosted, API Key enabled)
- OpenAI API Key
- Docker & Docker Compose (optional)

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/clebersantz/langchain-poc.git
cd langchain-poc

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your Odoo URL, API key, and OpenAI key

# 5. Ingest knowledge base
python scripts/ingest_knowledge_base.py

# 6. Test Odoo connection
python scripts/test_odoo_connection.py

# 7. Run the application
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/static/index.html` in your browser.

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `ODOO_URL` | Odoo instance base URL (no `/xmlrpc/2` suffix) | `http://localhost:8069` |
| `ODOO_DB` | Odoo database name | `odoo` |
| `ODOO_USER` | Odoo login email | `admin@example.com` |
| `ODOO_API_KEY` | Odoo API Key (Preferences → Account Security) | — |
| `ODOO_VERSION` | Odoo major version | `16` |
| `OPENAI_API_KEY` | OpenAI API key | — |
| `SUPERVISOR_MODEL` | LLM for Supervisor Agent | `gpt-4o` |
| `KB_AGENT_MODEL` | LLM for KB Agent | `gpt-4o-mini` |
| `WORKFLOW_AGENT_MODEL` | LLM for Workflow Agent | `gpt-4o` |
| `ODOO_API_AGENT_MODEL` | LLM for Odoo API Agent | `gpt-4o-mini` |
| `DATABASE_URL` | SQLite URL for session memory | `sqlite:///./storage/sessions.db` |
| `CHROMA_PERSIST_DIR` | ChromaDB persistence directory | `./storage/chroma_db` |
| `CHROMA_COLLECTION` | ChromaDB collection name | `odoo_crm_kb` |
| `APP_ENV` | Application environment | `development` |
| `LOG_LEVEL` | Log level | `INFO` |
| `WEBHOOK_SECRET` | Webhook HMAC secret | — |

---

## Agents

### 1. Supervisor Agent
Entry point for all user messages. Detects intent and routes to the appropriate sub-agent. Maintains persistent conversation history via SQLite.

### 2. KB Agent
RAG-powered Q&A over Odoo CRM documentation. Uses ChromaDB vector store and `text-embedding-3-small` embeddings. Returns grounded answers with source citations.

### 3. Workflow Agent
Executes pre-defined multi-step CRM workflows. Reads workflow steps from the KB Agent and executes them via Odoo API Agent tools. Logs execution to SQLite.

### 4. Odoo API Agent
All direct Odoo 16 CRUD via XML-RPC. Exposes LangChain `@tool` functions for leads, partners, activities, pipeline stages, and teams.

---

## Available Workflows

| Workflow | Description |
|---|---|
| `lead_qualification` | Score a lead and assign it to the correct pipeline stage |
| `opportunity_follow_up` | Detect stale opportunities and schedule follow-ups |
| `customer_onboarding` | Post-won partner validation and activity creation |
| `lost_lead_recovery` | Re-engage lost leads that meet recovery criteria |

---

## Knowledge Base

```
knowledge_base/
├── odoo_crm/           # 9 comprehensive Odoo 16 CRM guides
├── workflows/          # 4 detailed workflow specifications
└── faq/                # Common questions and API troubleshooting
```

Re-ingest after adding documents:
```bash
python scripts/ingest_knowledge_base.py --rebuild
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/chat` | Send a chat message |
| `GET` | `/workflows` | List available workflows |
| `POST` | `/workflows/run` | Run a workflow |
| `POST` | `/kb/ingest` | Ingest knowledge base documents |
| `GET` | `/kb/status` | KB status and chunk count |
| `POST` | `/webhooks/odoo` | Receive Odoo webhook events |

---

## Frontend

A simple static HTML/JS chat UI served at `/static/index.html`. No JS framework required.

- Auto-generates a UUID session ID stored in `localStorage`
- Renders Markdown responses via `marked.js`
- Shows which agent handled the response

---

## Docker

```bash
# Start the application and ChromaDB
docker compose -f docker/docker-compose.yml up -d

# Ingest knowledge base inside the container
docker compose -f docker/docker-compose.yml exec agent-app python scripts/ingest_knowledge_base.py
```

---

## Running Tests

```bash
pytest tests/unit/
pytest tests/integration/
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes and add tests
4. Run `pytest` to verify
5. Open a Pull Request

---

> **Note**: No Odoo Docker setup is included in this repo — it is handled separately.
> **Note**: API endpoints have no authentication (POC only). Add auth before production use.
