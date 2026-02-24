"""API schemas — Pydantic models for request/response validation."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for POST /chat."""

    session_id: str = Field(..., description="Unique conversation session UUID")
    message: str = Field(..., min_length=1, description="User message text")


class ChatResponse(BaseModel):
    """Response body for POST /chat."""

    session_id: str = Field(..., description="Echo of the session_id")
    response: str = Field(..., description="Agent's textual response")
    agent_used: str = Field(
        ..., description="Which agent handled the request (e.g. 'kb_agent')"
    )


class WorkflowRunRequest(BaseModel):
    """Request body for POST /workflows/run."""

    workflow_name: str = Field(..., description="Registered workflow name")
    context: dict = Field(default_factory=dict, description="Workflow input context")


class WorkflowRunResponse(BaseModel):
    """Response body for POST /workflows/run."""

    success: bool
    message: str
    steps: list[str] = Field(default_factory=list)


class WebhookPayload(BaseModel):
    """Payload for POST /webhooks/odoo."""

    event: str = Field(..., description="Event type (e.g. 'lead.won')")
    model: str = Field(..., description="Odoo model (e.g. 'crm.lead')")
    record_id: int = Field(..., description="Odoo record id")
    data: dict = Field(default_factory=dict, description="Additional event data")


class KBIngestResponse(BaseModel):
    """Response body for POST /kb/ingest."""

    chunks_ingested: int
    status: str
