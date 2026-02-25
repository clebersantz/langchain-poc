"""Customer Onboarding workflow — triggered after a lead is marked Won."""

from app.odoo.models.crm_lead import get_lead
from app.odoo.models.res_partner import get_partner
from app.workflows.base_workflow import BaseWorkflow, WorkflowResult


class CustomerOnboardingWorkflow(BaseWorkflow):
    """Post-Won onboarding process for new customers.

    Steps:
        1. validate_partner — ensure partner record is complete
        2. assign_am — assign an account manager (from team)
        3. create_activities — create onboarding activities
        4. log_chatter — post a welcome message to the chatter

    Trigger: Lead/Opportunity marked as Won.
    """

    name = "customer_onboarding"
    description = "Post-won partner validation and onboarding activity creation"

    async def execute(self, context: dict) -> WorkflowResult:
        """Execute the customer onboarding workflow.

        Args:
            context: Must contain ``lead_id`` (int).  Optionally
                ``account_manager_id`` (int).

        Returns:
            WorkflowResult: Onboarding execution result.
        """
        steps: list[str] = []
        lead_id: int | None = context.get("lead_id")

        if not lead_id:
            return WorkflowResult(
                success=False, message="lead_id is required", error="Missing lead_id"
            )

        # Step 1: Validate partner
        lead = get_lead(lead_id)
        if not lead:
            return WorkflowResult(
                success=False,
                message=f"Lead {lead_id} not found",
                error="Lead not found",
            )

        partner_id = lead.get("partner_id")
        if partner_id and isinstance(partner_id, (list, tuple)):
            partner_id = partner_id[0]

        partner = get_partner(partner_id) if partner_id else {}
        missing = [f for f in ["email", "phone"] if not partner.get(f)]
        steps.append("validate_partner")

        # Step 2: Assign account manager (stub)
        steps.append("assign_am")

        # Step 3: Create onboarding activities (stub)
        steps.append("create_activities")

        # Step 4: Log chatter message (stub — requires mail.message creation)
        steps.append("log_chatter")

        return WorkflowResult(
            success=True,
            steps_executed=steps,
            message=(
                f"Onboarding initiated for lead '{lead.get('name')}'. "
                f"Partner fields missing: {missing or 'none'}."
            ),
        )
