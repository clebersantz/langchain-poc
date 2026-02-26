"""Webhook API route — POST /webhooks/odoo."""

from threading import Lock

from fastapi import APIRouter, BackgroundTasks

from app.agents.workflow_agent import WorkflowAgent
from app.api.schemas import WebhookPayload
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

_workflow_agent: WorkflowAgent | None = None
_workflow_agent_lock = Lock()


def _get_workflow_agent() -> WorkflowAgent:
    """Return a lazily initialized WorkflowAgent instance."""
    global _workflow_agent
    if _workflow_agent is None:
        with _workflow_agent_lock:
            if _workflow_agent is None:
                _workflow_agent = WorkflowAgent()
    return _workflow_agent

# Mapping of Odoo webhook events to workflow names
_EVENT_WORKFLOW_MAP: dict[str, str] = {
    "lead.won": "customer_onboarding",
    "lead.lost": "lost_lead_recovery",
    "lead.created": "lead_qualification",
}


# TODO: add webhook signature verification for production
@router.post("/odoo")
async def odoo_webhook(
    payload: WebhookPayload, background_tasks: BackgroundTasks
) -> dict:
    """Receive and process an Odoo webhook event.

    Maps the incoming event to a registered workflow and executes it as a
    background task.

    Args:
        payload: Webhook event payload from Odoo.
        background_tasks: FastAPI background task runner.

    Returns:
        dict: Immediate acknowledgement response.
    """
    logger.info(
        "webhook_received",
        event=payload.event,
        model=payload.model,
        record_id=payload.record_id,
    )

    workflow_name = _EVENT_WORKFLOW_MAP.get(payload.event)
    if workflow_name:
        context = {"lead_id": payload.record_id, **payload.data}
        background_tasks.add_task(
            _get_workflow_agent().execute, workflow_name, context, "webhook"
        )

    return {"status": "accepted", "event": payload.event}
