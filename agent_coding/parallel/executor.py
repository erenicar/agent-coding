"""
Parallel Execution Engine for DAG task graphs.
Provides concurrent task queue processing with dependency resolution.
"""

import asyncio
from typing import Dict, List, Set, Optional, Callable, Awaitable
from agent_coding.agent.roles import AgentTask, TaskStatus
from agent_coding.agent.orchestrator import AgentOrchestrator


class TaskDAGExecutor:
    """
    Parallel Task DAG Executor.
    Executes tasks concurrently as soon as their dependencies are completed.
    """
    def __init__(self, orchestrator: AgentOrchestrator, max_concurrency: int = 5):
        self.orchestrator = orchestrator
        self.max_concurrency = max_concurrency

    async def execute_dag(self, tasks: List[AgentTask], context: Optional[str] = None) -> Dict[str, AgentTask]:
        task_map: Dict[str, AgentTask] = {t.task_id: t for t in tasks}
        completed_tasks: Set[str] = set()
        failed_tasks: Set[str] = set()
        running_tasks: Dict[str, asyncio.Task] = {}
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def _run_single_task(task: AgentTask):
            async with semaphore:
                # Build contextual background from dependencies
                dep_contexts = []
                for dep_id in task.dependencies:
                    if dep_id in task_map and task_map[dep_id].result:
                        dep_contexts.append(f"Dependency [{dep_id}] output:\n{task_map[dep_id].result}")

                combined_context = (context or "") + ("\n\n".join(dep_contexts))
                return await self.orchestrator.dispatch_task(task, context=combined_context)

        while len(completed_tasks) + len(failed_tasks) < len(tasks):
            # Identify ready tasks
            ready_tasks = []
            for t in tasks:
                if t.task_id in completed_tasks or t.task_id in failed_tasks or t.task_id in running_tasks:
                    continue
                # Check if all dependencies are completed
                deps_satisfied = all(dep in completed_tasks for dep in t.dependencies)
                deps_failed = any(dep in failed_tasks for dep in t.dependencies)

                if deps_failed:
                    t.status = TaskStatus.FAILED
                    t.error = "Dependency failed."
                    failed_tasks.add(t.task_id)
                elif deps_satisfied:
                    ready_tasks.append(t)

            if not ready_tasks and not running_tasks:
                # Deadlock or broken dependency graph
                break

            # Schedule ready tasks
            for t in ready_tasks:
                async_task = asyncio.create_task(_run_single_task(t))
                running_tasks[t.task_id] = async_task

            if not running_tasks:
                break

            # Wait for any completed task
            done, _ = await asyncio.wait(
                running_tasks.values(), return_when=asyncio.FIRST_COMPLETED
            )

            # Process completed tasks
            for completed_async_task in done:
                res_task: AgentTask = completed_async_task.result()
                running_tasks.pop(res_task.task_id, None)
                if res_task.status == TaskStatus.COMPLETED:
                    completed_tasks.add(res_task.task_id)
                else:
                    failed_tasks.add(res_task.task_id)

        return task_map
