"""Workflows API routes — GET /workflows, POST /workflows/run."""

from fastapi import APIRouter, HTTPException

from app.api.schemas import WorkflowRunRequest, WorkflowRunResponse
from app.workflows.registry import workflow_registry
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("")
async def list_workflows() -> list[dict]:
    """Return all registered workflow names and descriptions.

    Returns:
        list[dict]: Each item has ``name`` and ``description`` keys.
    """
    return [
        {"name": w.name, "description": w.description}
        for w in workflow_registry.list_all()
    ]


@router.post("/run", response_model=WorkflowRunResponse)
async def run_workflow(request: WorkflowRunRequest) -> WorkflowRunResponse:
    """Execute a named workflow with the provided context.

    Args:
        request: Workflow run request with ``workflow_name`` and ``context``.

    Returns:
        WorkflowRunResponse: Execution result with success flag and steps.

    Raises:
        HTTPException: 404 if the workflow name is not registered.
    """
    workflow = workflow_registry.get(request.workflow_name)
    if not workflow:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow '{request.workflow_name}' not found",
        )
    logger.info("workflow_run_request", name=request.workflow_name)
    result = await workflow.execute(request.context)
    return WorkflowRunResponse(
        success=result.success,
        message=result.message,
        steps=result.steps_executed,
    )
