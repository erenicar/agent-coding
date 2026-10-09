import type { ExecutionTask, PipelineResult, ProviderType } from '../types/index.ts';
import { CoderAgent, PlannerAgent, ReviewerAgent, TesterAgent } from './roles.ts';
import { LLMManager } from '../llm/providers.ts';

export class Orchestrator {
  private planner: PlannerAgent;
  private coder: CoderAgent;
  private reviewer: ReviewerAgent;
  private tester: TesterAgent;

  constructor(providerType: ProviderType = 'mock') {
    const llmManager = new LLMManager(providerType);
    this.planner = new PlannerAgent(llmManager);
    this.coder = new CoderAgent(llmManager);
    this.reviewer = new ReviewerAgent(llmManager);
    this.tester = new TesterAgent(llmManager);
  }

  public async runPipeline(
    prompt: string,
    onTaskUpdate?: (task: ExecutionTask) => void
  ): Promise<PipelineResult> {
    const startTime = Date.now();
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
    updateTask(0, 'running');
    const plan = await this.planner.execute(`Create plan for task: ${prompt}`);
    updateTask(0, 'completed', plan);

    // 2. Coding
    updateTask(1, 'running');
    const code = await this.coder.execute(`Write solution for: ${prompt}`, plan);
    updateTask(1, 'completed', code);

    // 3. Reviewing
    updateTask(2, 'running');
    const review = await this.reviewer.execute(`Review this code`, code);
    updateTask(2, 'completed', review);

    // 4. Testing
    updateTask(3, 'running');
    const testResult = await this.tester.execute(`Test code against task specifications`, code);
    updateTask(3, 'completed', testResult);

    const totalTimeMs = Date.now() - startTime;

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
