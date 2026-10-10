import { describe, expect, test } from 'bun:test';
import { WorkspaceManager } from '../src/fs/workspace.ts';
import { LoopDetector } from '../src/loop/detector.ts';
import { Profiler } from '../src/optimizer/profiler.ts';
import { Orchestrator } from '../src/agent/orchestrator.ts';
import { ParallelExecutor } from '../src/parallel/executor.ts';
import { FreeModelDiscoverer } from '../src/llm/freeModels.ts';

describe('claudek TS Bun Engine Test Suite', () => {
  test('WorkspaceManager resolves paths correctly', () => {
    const manager = new WorkspaceManager('/mnt/c/Users/dev/project');
    const config = manager.getConfig();
    expect(config.windowsPath).toBe('C:\\Users\\dev\\project');
    expect(config.ubuntuPath).toBe('/mnt/c/Users/dev/project');
  });

  test('LoopDetector detects duplicate repetitions', () => {
    const detector = new LoopDetector();
    expect(detector.analyze('test').isLoop).toBe(false);
    expect(detector.analyze('test').isLoop).toBe(false);
    expect(detector.analyze('test').isLoop).toBe(true);
  });

  test('Profiler records execution latency', () => {
    const profiler = new Profiler();
    profiler.start('test-op');
    const duration = profiler.end('test-op');
    expect(duration).toBeGreaterThanOrEqual(0);
    expect(profiler.getMetrics().length).toBe(1);
  });

  test('FreeModelDiscoverer discovers models', async () => {
    const models = await FreeModelDiscoverer.discoverFreeModels();
    expect(models.length).toBeGreaterThan(0);
  });

  test('ParallelExecutor handles tasks concurrently', async () => {
    const executor = new ParallelExecutor();
    const results = await executor.runTasks([1, 2, 3], async (n) => n * 2);
    expect(results).toEqual([2, 4, 6]);
  });

  test('Orchestrator runs full pipeline in mock mode', async () => {
    const orchestrator = new Orchestrator('mock');
    const result = await orchestrator.runPipeline('Create TypeScript API');
    expect(result.success).toBe(true);
    expect(result.tasks.length).toBe(4);
  });
});
