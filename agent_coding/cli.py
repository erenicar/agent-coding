"""
Command Line Interface Entrypoint for Claude Coding Agent (Ubuntu CLI & Terminal Compatible).
"""

import sys
import argparse
import asyncio

from agent_coding.desktop import ClaudeDesktopWorkspace
from agent_coding.llm import ProviderType, LLMManager


def main():
    parser = argparse.ArgumentParser(description="Claude Desktop Coding Agent Environment (Ubuntu Terminal Compatible)")
    parser.add_argument("--prompt", type=str, help="Coding task or prompt to execute", default="Create a high-performance Python web crawler")
    parser.add_argument("--provider", type=str, help="Default LLM provider (anthropic, openai, gemini, ollama, mock)", default="mock")
    parser.add_argument("--list-free-models", action="store_true", help="Auto-discover and display all available free-tier models across providers")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive workspace UI")

    args = parser.parse_args()

    workspace = ClaudeDesktopWorkspace()

    if args.list_free_models:
        workspace.console.print(workspace.render_header())
        free_models = workspace.llm_manager.get_free_models(force_refresh=True)
        workspace.console.print(workspace.render_free_models_table(free_models))
        sys.exit(0)

    if args.interactive:
        workspace.console.print(workspace.render_header())
        user_input = input("Enter your coding task: ")
        asyncio.run(workspace.run_sample_pipeline(user_input if user_input.strip() else args.prompt))
    else:
        asyncio.run(workspace.run_sample_pipeline(args.prompt))


if __name__ == "__main__":
    main()
