"""
Unit tests for Parallel Task DAG Executor.
"""

import pytest
from agent_coding.agent import AgentOrchestrator, AgentRole, AgentTask, TaskStatus
from agent_coding.parallel import TaskDAGExecutor


@pytest.mark.asyncio
async def test_parallel_dag_executor():
    orchestrator = AgentOrchestrator()
    executor = TaskDAGExecutor(orchestrator, max_concurrency=3)

    tasks = [
        AgentTask(task_id="t1", description="Task 1 Plan", assigned_role=AgentRole.PLANNER),
        AgentTask(task_id="t2", description="Task 2 Code A", assigned_role=AgentRole.CODER, dependencies=["t1"]),
        AgentTask(task_id="t3", description="Task 3 Code B", assigned_role=AgentRole.CODER, dependencies=["t1"]),
        AgentTask(task_id="t4", description="Task 4 Review", assigned_role=AgentRole.REVIEWER, dependencies=["t2", "t3"]),
    ]

    results = await executor.execute_dag(tasks)

    assert len(results) == 4
    for task_id, task in results.items():
        assert task.status == TaskStatus.COMPLETED
        assert task.result is not None
