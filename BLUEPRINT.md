# BLUEPRINT — langchain-poc Architecture

## System Overview

`langchain-poc` is a multi-agent LangChain application that integrates with an Odoo 16 CRM instance via JSON-RPC. It exposes a FastAPI HTTP API and a static chat frontend, enabling users to ask CRM knowledge-base questions, query/update Odoo data, and trigger automated multi-step CRM workflows through a single conversational interface.

---

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.11 |
| API Framework | FastAPI |
| Agent Framework | LangChain ≥ 0.2 |
| LLM | OpenAI (GPT-4o / GPT-4o-mini) |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector Store | ChromaDB (persistent on disk) |
| Persistent Memory | SQLite via `SQLChatMessageHistory` |
| Odoo Transport | JSON-RPC (`/jsonrpc`) |
| Frontend | Vanilla HTML / JS / CSS |
| Containerisation | Docker + Docker Compose |

---

## Agent Properties

| Agent | Model | State | Primary Responsibility |
|---|---|---|---|
| Supervisor | GPT-4o | Stateful (SQLite) | Intent detection, routing, conversation history |
| KB Agent | GPT-4o-mini | Stateless | RAG Q&A over CRM documentation |
| Workflow Agent | GPT-4o | Stateless (logs to SQLite) | Multi-step CRM workflow execution |
| Odoo API Agent | GPT-4o-mini | Stateless | JSON-RPC CRUD on Odoo 16 |

---

## Message Flow Diagrams

### A — Knowledge Base Question

```
User → POST /chat
  → Supervisor (intent: KB_QUESTION)
    → KB Agent
      → ChromaDB retrieval (top-k chunks)
      → LLM generates grounded answer
    ← KB Agent response with citations
  ← Supervisor forwards response
← ChatResponse (agent_used: kb_agent)
```

### B — CRM Data Query

```
User → POST /chat
  → Supervisor (intent: CRM_QUERY)
    → Odoo API Agent
      → JSON-RPC call to Odoo 16
      → Format results
    ← Structured data response
  ← Supervisor formats natural-language reply
← ChatResponse (agent_used: odoo_api_agent)
```

### C — Workflow Execution

```
User → POST /chat  OR  POST /workflows/run
  → Supervisor / API route (intent: WORKFLOW)
    → Workflow Agent
      → WorkflowRegistry.get(name)
      → BaseWorkflow.execute(context)
        → Steps call Odoo API Agent tools
      → Log to workflow_log table
    ← WorkflowResult
  ← ChatResponse (agent_used: workflow_agent)
```

### D — Odoo Webhook

```
Odoo → POST /webhooks/odoo  {event, model, record_id, data}
  → webhooks route
    → map event → workflow name
    → WorkflowAgent.execute(workflow_name, context)
      → same as flow C above
← 200 OK
```

---

## Storage Schema

### `chat_history` (managed by LangChain `SQLChatMessageHistory`)

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| session_id | TEXT | Conversation session UUID |
| message | TEXT (JSON) | Serialised `BaseMessage` |

### `workflow_log`

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| workflow_name | TEXT | Name of the workflow |
| trigger | TEXT | `manual` / `webhook` / `agent` |
| context_json | TEXT | Input context as JSON |
| status | TEXT | `running` / `success` / `failed` |
| steps_json | TEXT | Executed steps as JSON array |
| started_at | DATETIME | Workflow start timestamp |
| completed_at | DATETIME | Workflow end timestamp (nullable) |

---

## Odoo 16 JSON-RPC Integration

All Odoo calls go through `app/odoo/client.py` (`OdooClient`).

- **Authentication**: `POST /jsonrpc` → `common.login(db, user, api_key)` → returns `uid`
- **Operations**: `POST /jsonrpc` → `object.execute_kw(db, uid, api_key, model, method, args, kwargs)`
- **Key models**: `crm.lead`, `crm.stage`, `crm.team`, `res.partner`, `mail.activity`

```
# TODO: v18 - add native REST API support when migrating to Odoo 18
```

---

## ChromaDB Knowledge Base

- Documents are loaded from `knowledge_base/**/*.md`
- Chunked with `RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)`
- Embedded with `text-embedding-3-small`
- Persisted to `storage/chroma_db/`
- Collection name: `odoo_crm_kb`
- Retrieval: top-4 chunks by cosine similarity

---

## API Reference

```
POST  /chat                   ChatRequest  → ChatResponse
GET   /workflows              → list of workflow names + descriptions
POST  /workflows/run          WorkflowRunRequest → WorkflowRunResponse
POST  /kb/ingest              → KBIngestResponse
GET   /kb/status              → {"status": "ok", "chunks": N}
POST  /webhooks/odoo          WebhookPayload → {"status": "accepted"}
GET   /static/index.html      Chat frontend
```

---

## Security Notes

- No authentication on API endpoints (POC only)
- Add API key / OAuth2 authentication before production use
- Webhook signature verification: `# TODO: add webhook signature verification for production`
- Secrets in `.env` — never commit `.env` to version control
