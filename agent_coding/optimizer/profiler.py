"""
Performance Profiler and Auto-Optimization Engine.
Tracks API response times, token consumption, context windows, and detects execution bottlenecks.
"""

import time
import hashlib
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class PerformanceMetric(BaseModel):
    call_id: str
    component: str
    provider: str
    latency_seconds: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    timestamp: float = Field(default_factory=time.time)


class OptimizationReport(BaseModel):
    total_calls: int
    avg_latency: float
    p95_latency: float
    total_tokens_used: int
    bottlenecks: List[str]
    cache_hit_rate: float
    recommendations: List[str]


class PerformanceOptimizer:
    """
    Monitors system performance, manages context prompt caching, prunes redundant prompts,
    and identifies latency/token bottlenecks.
    """
    def __init__(self, max_cache_size: int = 100):
        self.metrics: List[PerformanceMetric] = []
        self.cache: Dict[str, str] = {}
        self.max_cache_size = max_cache_size
        self.cache_hits = 0
        self.cache_misses = 0

    def record_metric(self, metric: PerformanceMetric):
        self.metrics.append(metric)

    def get_cached_response(self, prompt: str) -> Optional[str]:
        prompt_hash = hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest()
        if prompt_hash in self.cache:
            self.cache_hits += 1
            return self.cache[prompt_hash]
        self.cache_misses += 1
        return None

    def cache_response(self, prompt: str, response: str):
        if len(self.cache) >= self.max_cache_size:
            # Evict oldest entry (LRU simple representation)
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        prompt_hash = hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest()
        self.cache[prompt_hash] = response

    def compress_prompt(self, prompt: str, max_chars: int = 4000) -> str:
        """
        Prunes excessive whitespace, duplicate comments, and truncates safely to optimize context window.
        """
        lines = prompt.splitlines()
        pruned_lines = [line for line in lines if line.strip() and not line.strip().startswith("# TODO: ignore")]
        compressed = "\n".join(pruned_lines)
        if len(compressed) > max_chars:
            head = compressed[: max_chars // 2]
            tail = compressed[-max_chars // 2 :]
            return f"{head}\n\n[... Context Pruned for Performance Optimization ...]\n\n{tail}"
        return compressed

    def analyze_performance(self) -> OptimizationReport:
        if not self.metrics:
            return OptimizationReport(
                total_calls=0,
                avg_latency=0.0,
                p95_latency=0.0,
                total_tokens_used=0,
                bottlenecks=[],
                cache_hit_rate=0.0,
                recommendations=["No metrics recorded yet."]
            )

        latencies = sorted([m.latency_seconds for m in self.metrics])
        avg_latency = sum(latencies) / len(latencies)
        p95_idx = int(len(latencies) * 0.95)
        p95_latency = latencies[min(p95_idx, len(latencies) - 1)]
        total_tokens = sum(m.total_tokens for m in self.metrics)

        bottlenecks = []
        recommendations = []

        # Bottleneck detection
        if p95_latency > 5.0:
            bottlenecks.append(f"High 95th percentile latency ({p95_latency:.2f}s)")
            recommendations.append("Enable streaming responses or switch to lower-latency models (e.g. gpt-4o-mini / claude-3-5-haiku).")

        if total_tokens > 50000:
            bottlenecks.append(f"High token consumption ({total_tokens} tokens)")
            recommendations.append("Apply aggressive prompt compression and context window pruning.")

        total_cache_requests = self.cache_hits + self.cache_misses
        cache_hit_rate = (self.cache_hits / total_cache_requests) if total_cache_requests > 0 else 0.0

        if cache_hit_rate < 0.2 and total_cache_requests > 10:
            recommendations.append("Increase caching reuse for system prompts and repetitive subtask queries.")

        if not recommendations:
            recommendations.append("System is operating within optimal parameters.")

        return OptimizationReport(
            total_calls=len(self.metrics),
            avg_latency=avg_latency,
            p95_latency=p95_latency,
            total_tokens_used=total_tokens,
            bottlenecks=bottlenecks,
            cache_hit_rate=cache_hit_rate,
            recommendations=recommendations
        )
