import type { FreeModel, ProviderType } from '../types/index.ts';

export class FreeModelDiscoverer {
  private static cachedModels: FreeModel[] | null = null;

  public static async discoverFreeModels(forceRefresh = false): Promise<FreeModel[]> {
    if (this.cachedModels && !forceRefresh) {
      return this.cachedModels;
    }

    const freeModels: FreeModel[] = [
      { provider: 'anthropic', model: 'claude-3-5-haiku-free-tier', isFree: true, limits: '50 req/day', speedRating: 98 },
      { provider: 'gemini', model: 'gemini-1.5-flash-free', isFree: true, limits: '15 RPM / 1M TPM', speedRating: 95 },
      { provider: 'openai', model: 'gpt-4o-mini-free', isFree: true, limits: 'Rate limited', speedRating: 90 },
      { provider: 'ollama', model: 'qwen2.5-coder:7b', isFree: true, limits: 'Unlimited local', speedRating: 99 },
      { provider: 'ollama', model: 'deepseek-r1:1.5b', isFree: true, limits: 'Unlimited local', speedRating: 100 },
      { provider: 'mock', model: 'mock-fast-claude', isFree: true, limits: 'Unlimited instant', speedRating: 100 },
    ];

    this.cachedModels = freeModels;
    return freeModels;
  }
}
