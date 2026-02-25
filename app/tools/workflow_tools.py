"""LangChain tool wrappers for workflow execution."""

import json

from langchain_core.tools import tool

from app.workflows.registry import workflow_registry


@tool
def list_available_workflows() -> str:
    """List all registered CRM workflows.

    Returns:
        str: JSON list of workflow names and descriptions.
    """
    workflows = workflow_registry.list_all()
    result = [{"name": w.name, "description": w.description} for w in workflows]
    return json.dumps(result)


@tool
def run_workflow(workflow_name: str, context_json: str) -> str:
    """Run a named CRM workflow with the provided context.

    Args:
        workflow_name: The registered name of the workflow to run.
        context_json: JSON string containing workflow input context.

    Returns:
        str: JSON ``WorkflowResult`` with success, steps_executed, and message.
    """
    import asyncio

    context = json.loads(context_json)
    workflow = workflow_registry.get(workflow_name)
    if not workflow:
        return json.dumps(
            {"success": False, "error": f"Workflow '{workflow_name}' not found"}
        )
    result = asyncio.run(workflow.execute(context))
    return json.dumps(
        {
            "success": result.success,
            "steps_executed": result.steps_executed,
            "message": result.message,
            "error": result.error,
        }
    )
