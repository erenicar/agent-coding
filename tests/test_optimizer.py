"""
Unit tests for Performance Profiler and Auto-Optimization Engine.
"""

import pytest
from agent_coding.optimizer import PerformanceOptimizer, PerformanceMetric


def test_performance_optimizer_caching():
    optimizer = PerformanceOptimizer()
    prompt = "Generate a python sorting algorithm"
    response = "def sort(arr): return sorted(arr)"

    assert optimizer.get_cached_response(prompt) is None

    optimizer.cache_response(prompt, response)
    cached = optimizer.get_cached_response(prompt)

    assert cached == response


def test_prompt_compression():
    optimizer = PerformanceOptimizer()
    long_prompt = "Line 1\n# TODO: ignore\n\nLine 2\nLine 3\n"
    compressed = optimizer.compress_prompt(long_prompt)

    assert "# TODO: ignore" not in compressed
    assert "Line 1" in compressed
    assert "Line 2" in compressed


def test_performance_analysis():
    optimizer = PerformanceOptimizer()
    optimizer.record_metric(
        PerformanceMetric(
            call_id="c1",
            component="Coder",
            provider="mock",
            latency_seconds=6.5,
            prompt_tokens=30000,
            completion_tokens=25000,
            total_tokens=55000
        )
    )

    report = optimizer.analyze_performance()

    assert report.total_calls == 1
    assert len(report.bottlenecks) >= 2
    assert any("latency" in b.lower() for b in report.bottlenecks)
    assert any("tokens" in b.lower() for b in report.bottlenecks)
