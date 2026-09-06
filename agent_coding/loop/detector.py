"""
Error Loop Detector & Auto-Remediation Engine.
Detects infinite loops, repetitive error patterns, stagnant test failures, and applies self-correction/strategy switching.
"""

import hashlib
from typing import List, Dict, Optional, Any, Tuple
from pydantic import BaseModel, Field

from agent_coding.llm.providers import LLMConfig, ProviderType


class ExecutionFingerprint(BaseModel):
    task_id: str
    code_hash: str
    error_message: str
    attempt: int
    provider: ProviderType
    temperature: float


class RemediationAction(BaseModel):
    action_type: str  # "switch_provider", "adjust_temperature", "delegate_to_reviewer", "escalate"
    new_config: Optional[LLMConfig] = None
    prompt_modifier: Optional[str] = None
    description: str


class ErrorLoopDetector:
    """
    Monitors code generation and error logs to detect infinite loops or repeated errors.
    Provides auto-remediation actions when a loop is detected.
    """
    def __init__(self, loop_threshold: int = 3):
        self.loop_threshold = loop_threshold
        self.history: List[ExecutionFingerprint] = []

    def compute_hash(self, code_str: str, error_str: str) -> str:
        content = f"{code_str.strip()}|||{error_str.strip()}"
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def record_and_check(
        self,
        task_id: str,
        code_str: str,
        error_message: str,
        current_config: LLMConfig
    ) -> Tuple[bool, Optional[RemediationAction]]:
        """
        Records execution state and checks if an error loop threshold has been reached.
        Returns (is_loop_detected, suggested_remediation_action).
        """
        fp_hash = self.compute_hash(code_str, error_message)

        # Count identical failures in history
        similar_failures = [
            fp for fp in self.history
            if fp.task_id == task_id and (fp.code_hash == fp_hash or fp.error_message == error_message)
        ]

        attempt_count = len(similar_failures) + 1
        fingerprint = ExecutionFingerprint(
            task_id=task_id,
            code_hash=fp_hash,
            error_message=error_message,
            attempt=attempt_count,
            provider=current_config.provider,
            temperature=current_config.temperature
        )
        self.history.append(fingerprint)

        if attempt_count >= self.loop_threshold:
            # Loop detected! Formulate auto-remediation strategy
            action = self._determine_remediation(fingerprint, current_config, attempt_count)
            return True, action

        return False, None

    def _determine_remediation(
        self,
        fp: ExecutionFingerprint,
        current_config: LLMConfig,
        attempt_count: int
    ) -> RemediationAction:
        if attempt_count == 3:
            # First level remediation: Raise temperature slightly to increase variation or switch provider
            new_provider = ProviderType.ANTHROPIC if current_config.provider != ProviderType.ANTHROPIC else ProviderType.OPENAI
            new_cfg = LLMConfig(
                provider=new_provider,
                model="claude-3-5-sonnet-20241022" if new_provider == ProviderType.ANTHROPIC else "gpt-4o",
                temperature=min(1.0, current_config.temperature + 0.3)
            )
            return RemediationAction(
                action_type="switch_provider",
                new_config=new_cfg,
                prompt_modifier="CRITICAL NOTICE: Previous approach resulted in repeated error: " + fp.error_message[:200] + ". Take a completely different approach.",
                description=f"Error loop detected (Attempt {attempt_count}). Switched provider to {new_provider.value} and modified prompt."
            )
        else:
            # Second level remediation: Delegate to Reviewer Agent or Escalate
            return RemediationAction(
                action_type="delegate_to_reviewer",
                prompt_modifier="ROBUST REVIEW REQUIRED: The coding agent is stuck in an error loop. Please analyze the code and error log deeply before attempting fixes.",
                description=f"Persistent error loop detected (Attempt {attempt_count}). Delegating to Reviewer Agent for deeper inspection."
            )
