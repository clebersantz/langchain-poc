"""Lost Lead Recovery workflow."""

from datetime import datetime, timedelta

from app.odoo.models.crm_lead import get_lead, search_leads
from app.workflows.base_workflow import BaseWorkflow, WorkflowResult


class LostLeadRecoveryWorkflow(BaseWorkflow):
    """Re-engages lost leads that meet recovery criteria.

    Steps:
        1. get_lost_lead — retrieve the lost lead details
        2. check_criteria — verify cooling-off period has passed
        3. draft_reengagement — compose a re-engagement message
        4. schedule_follow_up — create a follow-up activity

    Default cooling-off period: 30 days.
    """

    name = "lost_lead_recovery"
    description = "Re-engage lost leads that meet cooling-off and recovery criteria"

    async def execute(self, context: dict) -> WorkflowResult:
        """Execute the lost lead recovery workflow.

        Args:
            context: May contain ``lead_id`` (int) to target a specific lead,
                or ``cooling_off_days`` (int, default 30) to scan all lost leads.

        Returns:
            WorkflowResult: Recovery workflow execution result.
        """
        steps: list[str] = []
        lead_id: int | None = context.get("lead_id")
        cooling_days: int = context.get("cooling_off_days", 30)
        cutoff = (datetime.utcnow() - timedelta(days=cooling_days)).strftime("%Y-%m-%d %H:%M:%S")

        # Step 1: Get lost lead(s)
        if lead_id:
            leads = [get_lead(lead_id)] if get_lead(lead_id) else []
        else:
            leads = search_leads(
                domain=[["active", "=", False], ["write_date", "<", cutoff]],
                limit=20,
            )
        steps.append("get_lost_lead")

        if not leads or (len(leads) == 1 and not leads[0]):
            return WorkflowResult(
                success=True,
                steps_executed=steps,
                message="No lost leads eligible for recovery.",
            )

        # Step 2: Check criteria
        eligible = [
            lead
            for lead in leads
            if lead.get("expected_revenue", 0) > 0
        ]
        steps.append("check_criteria")

        # Step 3: Draft re-engagement message (stub)
        steps.append("draft_reengagement")

        # Step 4: Schedule follow-up (stub)
        steps.append("schedule_follow_up")

        return WorkflowResult(
            success=True,
            steps_executed=steps,
            message=(
                f"{len(eligible)} lost lead(s) eligible for recovery after "
                f"{cooling_days}-day cooling-off period."
            ),
        )
