import type { ExecutionTask } from '../types/index.ts';

export class ParallelExecutor {
  private concurrency: number;

  constructor(concurrency = 4) {
    this.concurrency = concurrency;
  }

  public async runTasks<T, R>(
    items: T[],
    taskFn: (item: T) => Promise<R>
  ): Promise<R[]> {
    const results: R[] = new Array(items.length);
    const executing = new Set<Promise<void>>();

    for (let i = 0; i < items.length; i++) {
      const p: Promise<void> = (async () => {
        results[i] = await taskFn(items[i]);
      })();

      executing.add(p);
      p.then(() => executing.delete(p)).catch(() => executing.delete(p));

      if (executing.size >= this.concurrency) {
        await Promise.race(executing);
      }
    }

    await Promise.all(executing);
    return results;
  }

  public async executeTasksParallel(
    tasks: ExecutionTask[],
    taskHandler: (task: ExecutionTask) => Promise<string>
  ): Promise<ExecutionTask[]> {
    const updatedTasks = [...tasks];
    return await this.runTasks(updatedTasks, async (task) => {
      task.status = 'running';
      task.startTime = Date.now();
      try {
        task.result = await taskHandler(task);
        task.status = 'completed';
      } catch (err) {
        task.status = 'failed';
        task.result = String(err);
      } finally {
        task.endTime = Date.now();
      }
      return task;
    });
  }
}
