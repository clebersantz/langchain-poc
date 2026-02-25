"""Unit tests for the workflow registry (app/workflows/registry.py)."""



class TestWorkflowRegistryRegistration:
    """Tests for WorkflowRegistry.register() and .get()."""

    def test_register_and_get_workflow(self):
        """A registered workflow should be retrievable by name."""
        from app.workflows.registry import WorkflowRegistry
        from app.workflows.base_workflow import BaseWorkflow, WorkflowResult

        class DummyWorkflow(BaseWorkflow):
            name = "dummy"
            description = "A test workflow"

            async def execute(self, context: dict) -> WorkflowResult:
                return WorkflowResult(success=True, message="done")

        registry = WorkflowRegistry()
        workflow = DummyWorkflow()
        registry.register(workflow)

        result = registry.get("dummy")
        assert result is workflow

    def test_get_nonexistent_workflow_returns_none(self):
        """get() should return None for an unregistered workflow name."""
        from app.workflows.registry import WorkflowRegistry

        registry = WorkflowRegistry()
        assert registry.get("does_not_exist") is None

    def test_list_all_returns_all_registered(self):
        """list_all() should return all registered workflows."""
        from app.workflows.registry import WorkflowRegistry
        from app.workflows.base_workflow import BaseWorkflow, WorkflowResult

        class WF1(BaseWorkflow):
            name = "wf1"
            description = "First"

            async def execute(self, context: dict) -> WorkflowResult:
                return WorkflowResult(success=True)

        class WF2(BaseWorkflow):
            name = "wf2"
            description = "Second"

            async def execute(self, context: dict) -> WorkflowResult:
                return WorkflowResult(success=True)

        registry = WorkflowRegistry()
        registry.register(WF1())
        registry.register(WF2())

        all_wf = registry.list_all()
        assert len(all_wf) == 2
        names = [w.name for w in all_wf]
        assert "wf1" in names
        assert "wf2" in names


class TestWorkflowRegistryPreregistered:
    """Tests for the module-level workflow_registry singleton."""

    def test_lead_qualification_is_registered(self):
        """lead_qualification workflow should be registered by default."""
        from app.workflows.registry import workflow_registry

        wf = workflow_registry.get("lead_qualification")
        assert wf is not None
        assert wf.name == "lead_qualification"

    def test_all_four_workflows_registered(self):
        """All 4 expected workflows should be pre-registered."""
        from app.workflows.registry import workflow_registry

        expected = [
            "lead_qualification",
            "opportunity_follow_up",
            "customer_onboarding",
            "lost_lead_recovery",
        ]
        for name in expected:
            assert workflow_registry.get(name) is not None, f"{name} not registered"

    def test_list_all_returns_at_least_four(self):
        """list_all() should return at least 4 workflows."""
        from app.workflows.registry import workflow_registry

        assert len(workflow_registry.list_all()) >= 4
