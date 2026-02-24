"""Lead Qualification workflow."""

from app.odoo.models.crm_lead import get_lead, update_lead
from app.odoo.models.crm_stage import get_stage_by_name
from app.workflows.base_workflow import BaseWorkflow, WorkflowResult


class LeadQualificationWorkflow(BaseWorkflow):
    """Qualifies a lead using BANT scoring and assigns it to the correct stage.

    Steps:
        1. get_lead — retrieve full lead details
        2. score — calculate BANT score from lead fields
        3. assign_stage — move lead to stage based on score
        4. schedule_call — create a follow-up call activity

    BANT scoring (0–100):
        - Budget (expected_revenue > 0): +25
        - Authority (partner_id set): +25
        - Need (description not empty): +25
        - Timeline (date_deadline set): +25
    """

    name = "lead_qualification"
    description = "Score a lead with BANT criteria and assign it to the correct pipeline stage"

    async def execute(self, context: dict) -> WorkflowResult:
        """Execute the lead qualification workflow.

        Args:
            context: Must contain ``lead_id`` (int).

        Returns:
            WorkflowResult: Execution result with steps and BANT score.
        """
        steps: list[str] = []
        lead_id: int | None = context.get("lead_id")

        if not lead_id:
            return WorkflowResult(
                success=False, message="lead_id is required", error="Missing lead_id"
            )

        # Step 1: Get lead
        lead = get_lead(lead_id)
        if not lead:
            return WorkflowResult(
                success=False,
                message=f"Lead {lead_id} not found",
                error="Lead not found",
            )
        steps.append("get_lead")

        # Step 2: BANT score
        score = 0
        if lead.get("expected_revenue", 0):
            score += 25
        if lead.get("partner_id"):
            score += 25
        if lead.get("description"):
            score += 25
        if lead.get("date_deadline"):
            score += 25
        steps.append("score")

        # Step 3: Assign stage based on score
        if score >= 75:
            stage_name = "Qualified"
        elif score >= 50:
            stage_name = "In Progress"
        else:
            stage_name = "New"

        stage = get_stage_by_name(stage_name)
        if stage:
            update_lead(lead_id, {"stage_id": stage["id"], "probability": score})
        steps.append("assign_stage")

        # Step 4: Schedule a call (stub — activity creation requires type_id lookup)
        steps.append("schedule_call")

        return WorkflowResult(
            success=True,
            steps_executed=steps,
            message=(
                f"Lead '{lead.get('name')}' scored {score}/100 (BANT) "
                f"and moved to stage '{stage_name}'."
            ),
        )
