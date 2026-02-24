"""Workflow registry — registers and looks up CRM workflows."""

from app.workflows.base_workflow import BaseWorkflow


class WorkflowRegistry:
    """Central registry for all available CRM workflows.

    Usage::

        from app.workflows.registry import workflow_registry

        workflow = workflow_registry.get("lead_qualification")
        result = await workflow.execute({"lead_id": 42})
    """

    def __init__(self) -> None:
        self._registry: dict[str, BaseWorkflow] = {}

    def register(self, workflow: BaseWorkflow) -> None:
        """Register a workflow instance.

        Args:
            workflow: A :class:`BaseWorkflow` instance with a unique
                :attr:`name`.
        """
        self._registry[workflow.name] = workflow

    def get(self, name: str) -> BaseWorkflow | None:
        """Return a registered workflow by name.

        Args:
            name: The workflow's registered name.

        Returns:
            BaseWorkflow | None: The workflow instance, or None if not found.
        """
        return self._registry.get(name)

    def list_all(self) -> list[BaseWorkflow]:
        """Return all registered workflows.

        Returns:
            list[BaseWorkflow]: All registered workflow instances.
        """
        return list(self._registry.values())


# Module-level singleton, pre-populated with all workflows
workflow_registry = WorkflowRegistry()

# Import here to avoid circular imports
from app.workflows.customer_onboarding import CustomerOnboardingWorkflow  # noqa: E402
from app.workflows.lead_qualification import LeadQualificationWorkflow  # noqa: E402
from app.workflows.lost_lead_recovery import LostLeadRecoveryWorkflow  # noqa: E402
from app.workflows.opportunity_follow_up import OpportunityFollowUpWorkflow  # noqa: E402

workflow_registry.register(LeadQualificationWorkflow())
workflow_registry.register(OpportunityFollowUpWorkflow())
workflow_registry.register(CustomerOnboardingWorkflow())
workflow_registry.register(LostLeadRecoveryWorkflow())
