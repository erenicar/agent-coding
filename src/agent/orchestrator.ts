import type { ExecutionTask, PipelineResult, ProviderType } from '../types/index.ts';
import { CoderAgent, PlannerAgent, ReviewerAgent, TesterAgent } from './roles.ts';
import { LLMManager } from '../llm/providers.ts';
import { Profiler } from '../optimizer/profiler.ts';
import { ParallelExecutor } from '../parallel/executor.ts';

export class Orchestrator {
  private planner: PlannerAgent;
  private coder: CoderAgent;
  private reviewer: ReviewerAgent;
  private tester: TesterAgent;
  private profiler: Profiler;
  private parallelExecutor: ParallelExecutor;

  constructor(providerType: ProviderType = 'mock') {
    const llmManager = new LLMManager(providerType);
    this.planner = new PlannerAgent(llmManager);
    this.coder = new CoderAgent(llmManager);
    this.reviewer = new ReviewerAgent(llmManager);
    this.tester = new TesterAgent(llmManager);
    this.profiler = new Profiler();
    this.parallelExecutor = new ParallelExecutor(2);
  }

  public async runPipeline(
    prompt: string,
    onTaskUpdate?: (task: ExecutionTask) => void
  ): Promise<PipelineResult> {
    const startTime = Date.now();
    this.profiler.start('pipeline');

    const tasks: ExecutionTask[] = [
      { id: '1', title: 'Architecture Planning', description: 'Formulate execution plan', role: 'planner', status: 'pending' },
      { id: '2', title: 'Code Generation', description: 'Write TypeScript code solution', role: 'coder', status: 'pending' },
      { id: '3', title: 'Code Review', description: 'Audit performance and type safety', role: 'reviewer', status: 'pending' },
      { id: '4', title: 'Automated Testing', description: 'Run test suite and verify build', role: 'tester', status: 'pending' },
    ];

    const updateTask = (idx: number, status: ExecutionTask['status'], result?: string) => {
      tasks[idx].status = status;
      if (status === 'running') tasks[idx].startTime = Date.now();
      if (status === 'completed' || status === 'failed') tasks[idx].endTime = Date.now();
      if (result) tasks[idx].result = result;
      if (onTaskUpdate) onTaskUpdate(tasks[idx]);
    };

    // 1. Planning
    this.profiler.start('planning');
    updateTask(0, 'running');
    const plan = await this.planner.execute(`Create plan for task: ${prompt}`);
    updateTask(0, 'completed', plan);
    this.profiler.end('planning');

    // 2. Coding
    this.profiler.start('coding');
    updateTask(1, 'running');
    const code = await this.coder.execute(`Write solution for: ${prompt}`, plan);
    updateTask(1, 'completed', code);
    this.profiler.end('coding');

    // 3 & 4. Run Review and Testing in Parallel using ParallelExecutor
    this.profiler.start('review_and_testing');
    updateTask(2, 'running');
    updateTask(3, 'running');

    const [review, testResult] = await Promise.all([
      this.reviewer.execute(`Review this code`, code),
      this.tester.execute(`Test code against task specifications`, code)
    ]);

    updateTask(2, 'completed', review);
    updateTask(3, 'completed', testResult);
    this.profiler.end('review_and_testing');

    const totalTimeMs = Date.now() - startTime;
    this.profiler.end('pipeline');

    return {
      prompt,
      plan,
      code,
      review,
      testResult,
      totalTimeMs,
      success: true,
      tasks
    };
  }
}
