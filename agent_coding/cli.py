"""
Command Line Interface Entrypoint for Claude Coding Agent.
"""

import sys
import argparse
import asyncio

from agent_coding.desktop import ClaudeDesktopWorkspace
from agent_coding.llm import ProviderType


def main():
    parser = argparse.ArgumentParser(description="Claude Desktop Coding Agent Environment")
    parser.add_argument("--prompt", type=str, help="Coding task or prompt to execute", default="Create a high-performance Python web crawler")
    parser.add_argument("--provider", type=str, help="Default LLM provider (anthropic, openai, gemini, ollama, mock)", default="mock")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive workspace")

    args = parser.parse_args()

    workspace = ClaudeDesktopWorkspace()

    if args.interactive:
        workspace.console.print(workspace.render_header())
        user_input = input("Enter your coding task: ")
        asyncio.run(workspace.run_sample_pipeline(user_input if user_input.strip() else args.prompt))
    else:
        asyncio.run(workspace.run_sample_pipeline(args.prompt))


if __name__ == "__main__":
    main()
