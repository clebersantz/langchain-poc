"""Workflows package."""

from app.workflows.base_workflow import BaseWorkflow, WorkflowResult
from app.workflows.customer_onboarding import CustomerOnboardingWorkflow
from app.workflows.lead_qualification import LeadQualificationWorkflow
from app.workflows.lost_lead_recovery import LostLeadRecoveryWorkflow
from app.workflows.opportunity_follow_up import OpportunityFollowUpWorkflow
from app.workflows.registry import WorkflowRegistry, workflow_registry

__all__ = [
    "BaseWorkflow",
    "WorkflowResult",
    "LeadQualificationWorkflow",
    "OpportunityFollowUpWorkflow",
    "CustomerOnboardingWorkflow",
    "LostLeadRecoveryWorkflow",
    "WorkflowRegistry",
    "workflow_registry",
]
