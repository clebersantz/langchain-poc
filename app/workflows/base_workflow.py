"""Abstract base class and result dataclass for CRM workflows."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class WorkflowResult:
    """Result object returned by every workflow execution.

    Attributes:
        success: Whether the workflow completed without fatal errors.
        steps_executed: List of step names that were run.
        message: Human-readable summary of the outcome.
        error: Error message if the workflow failed, otherwise None.
    """

    success: bool
    steps_executed: list[str] = field(default_factory=list)
    message: str = ""
    error: str | None = None


class BaseWorkflow(ABC):
    """Abstract base class for all CRM workflows.

    Subclasses must define :attr:`name`, :attr:`description`, and implement
    :meth:`execute`.
    """

    name: str
    description: str

    @abstractmethod
    async def execute(self, context: dict) -> WorkflowResult:
        """Execute the workflow asynchronously.

        Args:
            context: Input context dictionary (lead_id, partner_id, etc.)

        Returns:
            WorkflowResult: Outcome of the workflow execution.
        """
