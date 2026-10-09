import type { AgentMessage, AgentRoleConfig, ProviderType } from '../types/index.ts';
import { LLMManager } from '../llm/providers.ts';

export class BaseAgent {
  public config: AgentRoleConfig;
  protected llmManager: LLMManager;

  constructor(config: AgentRoleConfig, llmManager?: LLMManager) {
    this.config = config;
    this.llmManager = llmManager || new LLMManager(config.provider || 'mock');
  }

  public async execute(prompt: string, context?: string): Promise<string> {
    const messages: AgentMessage[] = [
      { role: 'system', content: this.config.systemPrompt },
      { role: 'user', content: context ? `Context:\n${context}\n\nTask:\n${prompt}` : prompt }
    ];

    const provider = this.llmManager.getProvider(this.config.provider, this.config.model);
    return await provider.generateResponse(messages);
  }
}

export class PlannerAgent extends BaseAgent {
  constructor(llmManager?: LLMManager) {
    super({
      name: 'PlannerAgent',
      role: 'planner',
      systemPrompt: 'You are an expert Software Architect. Break down user goals into clean, structured, modular steps.'
    }, llmManager);
  }
}

export class CoderAgent extends BaseAgent {
  constructor(llmManager?: LLMManager) {
    super({
      name: 'CoderAgent',
      role: 'coder',
      systemPrompt: 'You are a Senior TypeScript Developer. Write production-grade, highly-optimized TypeScript code with strict safety.'
    }, llmManager);
  }
}

export class ReviewerAgent extends BaseAgent {
  constructor(llmManager?: LLMManager) {
    super({
      name: 'ReviewerAgent',
      role: 'reviewer',
      systemPrompt: 'You are a Code Auditor. Review code for bugs, edge cases, type safety, and memory/performance bottlenecks.'
    }, llmManager);
  }
}

export class TesterAgent extends BaseAgent {
  constructor(llmManager?: LLMManager) {
    super({
      name: 'TesterAgent',
      role: 'tester',
      systemPrompt: 'You are a QA Automation Lead. Verify execution, run unit test suites, and report pass/fail metrics.'
    }, llmManager);
  }
}
