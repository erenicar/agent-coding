"""
Unit tests for Multi-Agent roles and Orchestrator.
"""

import pytest
from agent_coding.agent import (
    AgentOrchestrator,
    AgentRole,
    AgentTask,
    TaskStatus,
    CoordinatorAgent,
    PlannerAgent,
    CoderAgent,
    ReviewerAgent,
    TesterAgent,
)


@pytest.mark.asyncio
async def test_agent_orchestrator_initialization():
    orchestrator = AgentOrchestrator()
    assert orchestrator.get_agent(AgentRole.COORDINATOR) is not None
    assert orchestrator.get_agent(AgentRole.PLANNER) is not None
    assert orchestrator.get_agent(AgentRole.CODER) is not None
    assert orchestrator.get_agent(AgentRole.REVIEWER) is not None
    assert orchestrator.get_agent(AgentRole.TESTER) is not None


@pytest.mark.asyncio
async def test_dispatch_task():
    orchestrator = AgentOrchestrator()
    task = AgentTask(
        task_id="t1",
        description="Write a hello world function",
        assigned_role=AgentRole.CODER
    )

    updated_task = await orchestrator.dispatch_task(task)

    assert updated_task.status == TaskStatus.COMPLETED
    assert updated_task.result is not None
    assert "Mock Agent Response" in updated_task.result
