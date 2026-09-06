"""
Unit tests for claudek CLI and Web mode launcher.
"""

import pytest
import sys
from unittest.mock import patch

from agent_coding.desktop import ClaudeCodeTerminalTUI
from agent_coding.cli import main


def test_claudek_tui_initialization():
    tui = ClaudeCodeTerminalTUI()
    assert tui.console is not None
    assert tui.llm_manager is not None


@patch("sys.argv", ["claudek", "--prompt", "Test coding task"])
def test_claudek_cli_prompt_mode():
    with patch("asyncio.run") as mock_run:
        main()
        assert mock_run.called
