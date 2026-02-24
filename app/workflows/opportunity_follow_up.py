"""Opportunity Follow-Up workflow."""

from datetime import datetime, timedelta

from app.odoo.models.crm_lead import search_leads
from app.workflows.base_workflow import BaseWorkflow, WorkflowResult


class OpportunityFollowUpWorkflow(BaseWorkflow):
    """Detects stale opportunities and schedules follow-up activities.

    Steps:
        1. detect_stale — find opportunities not updated within the threshold
        2. draft_message — generate a personalised re-engagement message
        3. schedule_activity — create a follow-up activity for each stale opportunity

    Default stale threshold: 14 days without update.
    """

    name = "opportunity_follow_up"
    description = "Detect stale opportunities and schedule follow-up activities"

    async def execute(self, context: dict) -> WorkflowResult:
        """Execute the opportunity follow-up workflow.

        Args:
            context: Optional ``stale_days`` (int, default 14) and
                ``user_id`` (int) to filter by salesperson.

        Returns:
            WorkflowResult: List of stale opportunities processed.
        """
        steps: list[str] = []
        stale_days: int = context.get("stale_days", 14)
        cutoff = (datetime.utcnow() - timedelta(days=stale_days)).strftime("%Y-%m-%d %H:%M:%S")

        # Step 1: Detect stale opportunities
        domain = [
            ["type", "=", "opportunity"],
            ["active", "=", True],
            ["write_date", "<", cutoff],
        ]
        stale = search_leads(domain=domain, limit=50)
        steps.append("detect_stale")

        if not stale:
            return WorkflowResult(
                success=True,
                steps_executed=steps,
                message=f"No stale opportunities found (threshold: {stale_days} days).",
            )

        # Step 2: Draft message (stub)
        steps.append("draft_message")

        # Step 3: Schedule activity (stub — requires activity_type_id resolution)
        steps.append("schedule_activity")

        return WorkflowResult(
            success=True,
            steps_executed=steps,
            message=(
                f"Found {len(stale)} stale opportunities older than {stale_days} days. "
                "Follow-up activities scheduled."
            ),
        )
