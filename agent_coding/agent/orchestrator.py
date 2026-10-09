"""
Multi-Agent Orchestrator.
Coordinates team of agents (Coordinator, Planner, Coder, Reviewer, Tester).
Integrated with Error Loop Detector and Auto-Remediation strategies.
"""

from typing import Dict, List, Optional
from agent_coding.agent.roles import (
    AgentRole,
    AgentTask,
    BaseAgent,
    CoordinatorAgent,
    PlannerAgent,
    CoderAgent,
    ReviewerAgent,
    CodeTesterAgent,
    TaskStatus,
)
from agent_coding.llm.providers import LLMManager, LLMConfig, ProviderType
from agent_coding.loop.detector import ErrorLoopDetector, RemediationAction


class AgentOrchestrator:
    """
    Orchestrates communication, task dispatch, and auto-remediation across multi-agents.
    """
    def __init__(self, llm_manager: Optional[LLMManager] = None, loop_detector: Optional[ErrorLoopDetector] = None):
        self.llm_manager = llm_manager or LLMManager()
        self.loop_detector = loop_detector or ErrorLoopDetector()
        self.agents: Dict[AgentRole, BaseAgent] = {
            AgentRole.COORDINATOR: CoordinatorAgent(self.llm_manager),
            AgentRole.PLANNER: PlannerAgent(self.llm_manager),
            AgentRole.CODER: CoderAgent(self.llm_manager),
            AgentRole.REVIEWER: ReviewerAgent(self.llm_manager),
            AgentRole.TESTER: CodeTesterAgent(self.llm_manager),
        }

    def register_agent(self, role: AgentRole, agent: BaseAgent):
        self.agents[role] = agent

    def get_agent(self, role: AgentRole) -> BaseAgent:
        if role not in self.agents:
            raise ValueError(f"Agent for role '{role}' is not registered.")
        return self.agents[role]

    async def dispatch_task(self, task: AgentTask, context: Optional[str] = None, max_retries: int = 3) -> AgentTask:
        agent = self.get_agent(task.assigned_role)
        task.status = TaskStatus.IN_PROGRESS

        current_config = agent.config
        current_context = context or ""

        for attempt in range(1, max_retries + 1):
            try:
                result = await agent.execute_task(task, context=current_context)
                task.result = result
                task.status = TaskStatus.COMPLETED
                return task
            except Exception as e:
                error_str = str(e)
                task.error = error_str

                # Check for loop & apply auto-remediation
                is_loop, action = self.loop_detector.record_and_check(
                    task_id=task.task_id,
                    code_str=task.result or "",
                    error_message=error_str,
                    current_config=current_config
                )

                if is_loop and action:
                    if action.new_config:
                        agent.config = action.new_config
                        current_config = action.new_config
                    if action.prompt_modifier:
                        current_context = f"{current_context}\n\n[REMEDIATION INSTRUCTION]: {action.prompt_modifier}"
                    if action.action_type == "delegate_to_reviewer":
                        agent = self.get_agent(AgentRole.REVIEWER)

        task.status = TaskStatus.FAILED
        return task
