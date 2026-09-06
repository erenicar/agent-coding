"""
Agent Roles and Definitions.
Includes Coordinator, Planner, Coder, Reviewer, and CodeTester agents.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from agent_coding.llm.providers import LLMConfig, Message, LLMResponse, LLMManager, ProviderType


class AgentRole(str, Enum):
    COORDINATOR = "Coordinator"
    PLANNER = "Planner"
    CODER = "Coder"
    REVIEWER = "Reviewer"
    TESTER = "Tester"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentTask(BaseModel):
    task_id: str
    description: str
    assigned_role: AgentRole
    dependencies: List[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseAgent:
    def __init__(self, role: AgentRole, system_prompt: str, llm_manager: Optional[LLMManager] = None, config: Optional[LLMConfig] = None):
        self.role = role
        self.system_prompt = system_prompt
        self.llm_manager = llm_manager or LLMManager()
        self.config = config or LLMConfig(provider=ProviderType.MOCK)

    async def execute_task(self, task: AgentTask, context: Optional[str] = None) -> str:
        prompt = f"Role: {self.role.value}\nTask ID: {task.task_id}\nTask: {task.description}"
        if context:
            prompt += f"\n\nContext:\n{context}"

        messages = [
            Message(role="system", content=self.system_prompt),
            Message(role="user", content=prompt)
        ]

        response: LLMResponse = await self.llm_manager.generate(messages, config=self.config)
        return response.content


class CoordinatorAgent(BaseAgent):
    def __init__(self, llm_manager: Optional[LLMManager] = None):
        super().__init__(
            role=AgentRole.COORDINATOR,
            system_prompt="You are the Coordinator Agent. You manage task delegation, monitor agent progress, and aggregate final results.",
            llm_manager=llm_manager
        )


class PlannerAgent(BaseAgent):
    def __init__(self, llm_manager: Optional[LLMManager] = None):
        super().__init__(
            role=AgentRole.PLANNER,
            system_prompt="You are the Planner Agent. You break complex user requests into structured, parallelizable subtasks with clear dependencies.",
            llm_manager=llm_manager
        )


class CoderAgent(BaseAgent):
    def __init__(self, llm_manager: Optional[LLMManager] = None):
        super().__init__(
            role=AgentRole.CODER,
            system_prompt="You are the Coder Agent. You write clean, high-quality, efficient Python/TypeScript code and fix bugs.",
            llm_manager=llm_manager
        )


class ReviewerAgent(BaseAgent):
    def __init__(self, llm_manager: Optional[LLMManager] = None):
        super().__init__(
            role=AgentRole.REVIEWER,
            system_prompt="You are the Reviewer Agent. You perform code reviews, check security standards, and inspect logic flaws.",
            llm_manager=llm_manager
        )


class CodeTesterAgent(BaseAgent):
    def __init__(self, llm_manager: Optional[LLMManager] = None):
        super().__init__(
            role=AgentRole.TESTER,
            system_prompt="You are the Tester Agent. You generate unit tests, execute test suites, and verify code correctness.",
            llm_manager=llm_manager
        )


# Alias for backward compatibility
TesterAgent = CodeTesterAgent
