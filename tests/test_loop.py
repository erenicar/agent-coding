"""
Unit tests for Error Loop Detector and Auto-Remediation.
"""

import pytest
from agent_coding.llm import LLMConfig, ProviderType
from agent_coding.loop import ErrorLoopDetector, RemediationAction


def test_error_loop_detection():
    detector = ErrorLoopDetector(loop_threshold=3)
    config = LLMConfig(provider=ProviderType.OPENAI, temperature=0.2)

    code = "def add(a, b): return a - b"
    error = "AssertionError: 1 + 1 != 0"

    # Attempt 1
    is_loop, action = detector.record_and_check("task_1", code, error, config)
    assert not is_loop
    assert action is None

    # Attempt 2
    is_loop, action = detector.record_and_check("task_1", code, error, config)
    assert not is_loop
    assert action is None

    # Attempt 3 (Threshold hit)
    is_loop, action = detector.record_and_check("task_1", code, error, config)
    assert is_loop
    assert action is not None
    assert isinstance(action, RemediationAction)
    assert action.action_type == "switch_provider"
    assert action.new_config is not None
    assert action.new_config.provider == ProviderType.ANTHROPIC
