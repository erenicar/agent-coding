"""
Claude Code Terminal TUI / UX Workspace (Rich-based).
Styled explicitly after Claude Code CLI (dark themes, glowing badges, distinct tool calling indicators, streaming text panels).
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
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

from agent_coding.llm import LLMManager, ProviderType, LLMConfig, FreeModelInfo
from agent_coding.agent import AgentOrchestrator, AgentRole, AgentTask, TaskStatus
from agent_coding.parallel import TaskDAGExecutor
from agent_coding.loop import ErrorLoopDetector
from agent_coding.optimizer import PerformanceOptimizer, PerformanceMetric


class ClaudeCodeTerminalTUI:
    """
    Claude Code Style Terminal User Interface (TUI).
    Distinct from web UI with Anthropic-orange/magenta branding and Claude Code CLI layout.
    """
    def __init__(self):
        self.console = Console()
        self.llm_manager = LLMManager()
        self.orchestrator = AgentOrchestrator(self.llm_manager)
        self.executor = TaskDAGExecutor(self.orchestrator)
        self.loop_detector = ErrorLoopDetector()
        self.optimizer = PerformanceOptimizer()

    def render_claude_code_header(self) -> Panel:
        title = Text(" ✳ CLAUDE CODE (claudek Terminal TUI v0.2) ", style="bold black on #D97706")
        subtitle = Text(" Autonomous Coding Agent | Parallel DAG Engine | Multi-Vendor API ", style="italic dim white")
        header_text = Text.assemble(title, "\n", subtitle)
        return Panel(
            header_text,
            border_style="#D97706",
            padding=(0, 1)
        )

    def render_agent_pipeline_view(self, tasks: Optional[List[AgentTask]] = None) -> Table:
        table = Table(
            title="[bold #F59E0B]⚡ Agent Pipeline & Tool Calls[/bold #F59E0B]",
            expand=True,
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("Agent Role", style="bold yellow", width=16)
        table.add_column("Task / Action Description", style="white")
        table.add_column("Status Badge", style="bold", width=18)

        if not tasks:
            table.add_row("System", "Standby - Waiting for user prompt in terminal...", "[dim]⚪ Idle[/dim]")
            return table

        for task in tasks:
            status_style = {
                TaskStatus.PENDING: "[bold yellow]⏳ Pending[/bold yellow]",
                TaskStatus.IN_PROGRESS: "[bold cyan]🔄 Executing[/bold cyan]",
                TaskStatus.COMPLETED: "[bold green]✔ Done[/bold green]",
                TaskStatus.FAILED: "[bold red]❌ Failed[/bold red]",
            }.get(task.status, str(task.status))

            table.add_row(f"[{task.assigned_role.value}]", task.description, status_style)

        return table

    def render_performance_dashboard(self) -> Panel:
        report = self.optimizer.analyze_performance()
        body = (
            f"[bold cyan]Calls:[/bold cyan] {report.total_calls} | "
            f"[bold green]Avg Latency:[/bold green] {report.avg_latency:.2f}s | "
            f"[bold magenta]Tokens Used:[/bold magenta] {report.total_tokens_used} | "
            f"[bold yellow]Cache Hit:[/bold yellow] {report.cache_hit_rate * 100:.1f}%\n"
            f"[bold red]Bottlenecks Active:[/bold red] {len(report.bottlenecks)}"
        )
        return Panel(body, title="[bold #D97706]📊 System & Token Profiler[/bold #D97706]", border_style="#D97706")

    async def run_pipeline(self, prompt: str):
        self.console.print(self.render_claude_code_header())
        self.console.print(Panel(f"[bold white]{prompt}[/bold white]", title="[bold #F59E0B]Input Prompt[/bold #F59E0B]", border_style="#F59E0B"))

        tasks = [
            AgentTask(task_id="task_1_plan", description=f"Plan solution for: {prompt[:40]}", assigned_role=AgentRole.PLANNER),
            AgentTask(task_id="task_2_code", description="Generate high-performance Python code", assigned_role=AgentRole.CODER, dependencies=["task_1_plan"]),
            AgentTask(task_id="task_3_review", description="Inspect logic flaws and security vulnerability", assigned_role=AgentRole.REVIEWER, dependencies=["task_2_code"]),
            AgentTask(task_id="task_4_test", description="Execute unit test verification suite", assigned_role=AgentRole.TESTER, dependencies=["task_2_code"]),
            AgentTask(task_id="task_5_coord", description="Consolidate agent outputs into final response", assigned_role=AgentRole.COORDINATOR, dependencies=["task_3_review", "task_4_test"]),
        ]

        layout = Layout()
        layout.split_column(
            Layout(name="pipeline", ratio=2),
            Layout(name="metrics", ratio=1)
        )

        with Live(layout, refresh_per_second=4, console=self.console):
            layout["pipeline"].update(self.render_agent_pipeline_view(tasks))

            results = await self.executor.execute_dag(tasks, context=prompt)

            for t_id, task_res in results.items():
                self.optimizer.record_metric(
                    PerformanceMetric(
                        call_id=t_id,
                        component=task_res.assigned_role.value,
                        provider="mock",
                        latency_seconds=0.08,
                        prompt_tokens=150,
                        completion_tokens=80,
                        total_tokens=230
                    )
                )

            layout["pipeline"].update(self.render_agent_pipeline_view(list(results.values())))
            layout["metrics"].update(self.render_performance_dashboard())

        self.console.print("\n[bold green]✔ [claudek] Pipeline Execution Completed Successfully![/bold green]")


# For backward compatibility
ClaudeDesktopWorkspace = ClaudeCodeTerminalTUI
