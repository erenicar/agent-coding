"""
Desktop Terminal Workspace UI using Rich.
Provides a Claude Code / Claude Desktop style UI for managing multi-agents, multi-vendor LLM keys, free model lists, and real-time execution.
"""

import sys
import asyncio
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt

from agent_coding.llm import LLMManager, ProviderType, LLMConfig, FreeModelInfo
from agent_coding.agent import AgentOrchestrator, AgentRole, AgentTask, TaskStatus
from agent_coding.parallel import TaskDAGExecutor
from agent_coding.loop import ErrorLoopDetector
from agent_coding.optimizer import PerformanceOptimizer, PerformanceMetric


class ClaudeDesktopWorkspace:
    """
    Claude Desktop Style Terminal Workspace UI.
    """
    def __init__(self):
        self.console = Console()
        self.llm_manager = LLMManager()
        self.orchestrator = AgentOrchestrator(self.llm_manager)
        self.executor = TaskDAGExecutor(self.orchestrator)
        self.loop_detector = ErrorLoopDetector()
        self.optimizer = PerformanceOptimizer()

    def render_header(self) -> Panel:
        title = Text("Claude Desktop Coding Agent Workspace", style="bold magenta")
        subtitle = Text("Ubuntu CLI Compatible | Multi-Agent | DAG Parallel | Free Model Discovery | Auto-Optimizer", style="dim cyan")
        return Panel(
            Text.assemble(title, "\n", subtitle),
            title="[bold blue]Desktop Agent System[/bold blue]",
            border_style="magenta"
        )

    def render_free_models_table(self, models: Optional[List[FreeModelInfo]] = None) -> Table:
        if models is None:
            models = self.llm_manager.get_free_models()

        table = Table(title="Auto-Discovered Free Models List (Dynamic Refresh)", expand=True)
        table.add_column("Model ID", style="cyan", no_wrap=True)
        table.add_column("Display Name", style="yellow")
        table.add_column("Provider", style="green")
        table.add_column("Vision", style="magenta")
        table.add_column("Context Window", style="white")

        for m in models[:8]:  # Top 8 models for clean UI display
            table.add_row(
                m.model_id[:35],
                m.display_name,
                m.provider.value,
                "✓" if m.supports_vision else "x",
                f"{m.context_window:,} tokens"
            )

        return table

    def render_agent_status_table(self, tasks: Optional[List[AgentTask]] = None) -> Table:
        table = Table(title="Multi-Agent Status & Execution Tasks", expand=True)
        table.add_column("Task ID", style="cyan", no_wrap=True)
        table.add_column("Assigned Role", style="yellow")
        table.add_column("Description", style="white")
        table.add_column("Status", style="bold")

        if not tasks:
            table.add_row("N/A", "System", "No tasks in active DAG pipeline.", "[dim]Idle[/dim]")
            return table

        for task in tasks:
            status_style = {
                TaskStatus.PENDING: "[yellow]Pending[/yellow]",
                TaskStatus.IN_PROGRESS: "[blue]Executing...[/blue]",
                TaskStatus.COMPLETED: "[bold green]Completed[/bold green]",
                TaskStatus.FAILED: "[bold red]Failed[/bold red]",
            }.get(task.status, str(task.status))

            table.add_row(task.task_id, task.assigned_role.value, task.description[:40], status_style)

        return table

    def render_system_metrics_panel(self) -> Panel:
        report = self.optimizer.analyze_performance()
        metrics_text = (
            f"Total API Calls: [bold]{report.total_calls}[/bold]\n"
            f"Avg Latency: [bold]{report.avg_latency:.2f}s[/bold] | P95 Latency: [bold]{report.p95_latency:.2f}s[/bold]\n"
            f"Total Tokens Used: [bold]{report.total_tokens_used}[/bold]\n"
            f"Cache Hit Rate: [bold]{report.cache_hit_rate * 100:.1f}%[/bold]\n"
            f"Bottlenecks Detected: [bold red]{len(report.bottlenecks)}[/bold red]"
        )
        return Panel(metrics_text, title="[bold green]Performance & Bottleneck Profiler[/bold green]", border_style="green")

    async def run_sample_pipeline(self, user_prompt: str):
        self.console.print(Panel(f"[bold white]User Request:[/bold white] {user_prompt}", title="[bold yellow]New Task Input[/bold yellow]", border_style="yellow"))

        free_models = self.llm_manager.get_free_models(force_refresh=True)
        self.console.print(self.render_free_models_table(free_models))

        # Decompose task into multi-agent DAG
        tasks = [
            AgentTask(task_id="task_1_plan", description=f"Analyze and break down request: '{user_prompt}'", assigned_role=AgentRole.PLANNER),
            AgentTask(task_id="task_2_code", description="Implement core logic based on planner spec", assigned_role=AgentRole.CODER, dependencies=["task_1_plan"]),
            AgentTask(task_id="task_3_review", description="Review generated code for security & edge cases", assigned_role=AgentRole.REVIEWER, dependencies=["task_2_code"]),
            AgentTask(task_id="task_4_test", description="Generate unit tests and verify correctness", assigned_role=AgentRole.TESTER, dependencies=["task_2_code"]),
            AgentTask(task_id="task_5_coord", description="Aggregate results and generate final report", assigned_role=AgentRole.COORDINATOR, dependencies=["task_3_review", "task_4_test"]),
        ]

        layout = Layout()
        layout.split_column(
            Layout(name="header", size=4),
            Layout(name="body"),
            Layout(name="footer", size=8)
        )

        with Live(layout, refresh_per_second=4, console=self.console) as live:
            layout["header"].update(self.render_header())
            layout["body"].update(self.render_agent_status_table(tasks))

            # Start parallel DAG execution
            results = await self.executor.execute_dag(tasks, context=f"User request: {user_prompt}")

            # Record performance metrics
            for t_id, task_res in results.items():
                self.optimizer.record_metric(
                    PerformanceMetric(
                        call_id=t_id,
                        component=task_res.assigned_role.value,
                        provider="mock",
                        latency_seconds=0.1,
                        prompt_tokens=120,
                        completion_tokens=60,
                        total_tokens=180
                    )
                )

            layout["body"].update(self.render_agent_status_table(list(results.values())))
            layout["footer"].update(self.render_system_metrics_panel())

        self.console.print("\n[bold green]✓ Execution Completed Successfully![/bold green]")
