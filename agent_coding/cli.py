"""
Command Line Interface Entrypoint for claudek (Claude Code Terminal & Web UI Agent).
Supports:
- `claudek` (Terminal TUI mode)
- `claudek -web` or `claudek --web` (Web UI mode)
- `claudek --list-free-models`
- `claudek --prompt "..."`
"""

import sys
import argparse
import asyncio

from agent_coding.desktop import ClaudeCodeTerminalTUI
from agent_coding.llm import ProviderType, LLMManager
from agent_coding.web import start_web_server


def main():
    # Pre-parse sys.argv to handle `-web` style flag cleanly alongside `--web`
    if "-web" in sys.argv:
        idx = sys.argv.index("-web")
        sys.argv[idx] = "--web"

    parser = argparse.ArgumentParser(description="claudek - Claude Code Terminal TUI & Web UI Coding Agent")
    parser.add_argument("--prompt", type=str, help="Coding task or prompt to execute", default="Create a high-performance Python web crawler")
    parser.add_argument("--provider", type=str, help="Default LLM provider (anthropic, openai, gemini, ollama, mock)", default="mock")
    parser.add_argument("--list-free-models", action="store_true", help="Auto-discover and display all available free-tier models across providers")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive workspace UI")
    parser.add_argument("--web", action="store_true", help="Launch claudek Web UI workspace mode")
    parser.add_argument("--port", type=int, help="Port for claudek Web UI server", default=8080)

    args = parser.parse_args()

    if args.web:
        start_web_server(port=args.port)
        return

    workspace = ClaudeCodeTerminalTUI()

    if args.list_free_models:
        workspace.console.print(workspace.render_claude_code_header())
        free_models = workspace.llm_manager.get_free_models(force_refresh=True)
        workspace.console.print(workspace.render_free_models_table(free_models) if hasattr(workspace, "render_free_models_table") else str(free_models))
        sys.exit(0)

    if args.interactive:
        workspace.console.print(workspace.render_claude_code_header())
        user_input = input("✳ claudek > Enter coding task: ")
        asyncio.run(workspace.run_pipeline(user_input if user_input.strip() else args.prompt))
    else:
        asyncio.run(workspace.run_pipeline(args.prompt))


if __name__ == "__main__":
    main()
