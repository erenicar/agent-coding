import type { ProfilerMetric } from '../types/index.ts';

export class Profiler {
  private metrics: ProfilerMetric[] = [];
  private startTimes: Map<string, number> = new Map();

  public start(label: string): void {
    this.startTimes.set(label, performance.now());
  }

  public end(label: string, metadata?: Record<string, any>): number {
    const startTime = this.startTimes.get(label);
    if (!startTime) return 0;

    const durationMs = performance.now() - startTime;
    this.startTimes.delete(label);

    const metric: ProfilerMetric = {
      name: label,
      durationMs,
      metadata,
      timestamp: Date.now()
    };

    this.metrics.push(metric);
    return durationMs;
  }

  public getMetrics(): ProfilerMetric[] {
    return [...this.metrics];
  }

  public clear(): void {
    this.metrics = [];
    this.startTimes.clear();
  }
}
