export type ProviderType = 'anthropic' | 'openai' | 'gemini' | 'ollama' | 'mock';

export interface LLMConfig {
  provider: ProviderType;
  model: string;
  apiKey?: string;
  baseUrl?: string;
  temperature?: number;
  maxTokens?: number;
}

export interface FreeModel {
  provider: ProviderType;
  model: string;
  isFree: boolean;
  limits?: string;
  speedRating?: number;
}

export interface AgentMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
  timestamp?: number;
}

export interface AgentRoleConfig {
  name: string;
  role: 'planner' | 'coder' | 'reviewer' | 'tester';
  systemPrompt: string;
  provider?: ProviderType;
  model?: string;
}

export interface ExecutionTask {
  id: string;
  title: string;
  description: string;
  role: 'planner' | 'coder' | 'reviewer' | 'tester';
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: string;
  startTime?: number;
  endTime?: number;
}

export interface PipelineResult {
  prompt: string;
  plan?: string;
  code?: string;
  review?: string;
  testResult?: string;
  totalTimeMs: number;
  success: boolean;
  tasks: ExecutionTask[];
}

export interface WorkspaceConfig {
  currentDir: string;
  windowsPath?: string;
  ubuntuPath?: string;
  linkedDirs: string[];
}

export interface LoopDetectionResult {
  isLoop: boolean;
  reason?: string;
  repeatedPattern?: string;
  similarityScore: number;
}

export interface ProfilerMetric {
  name: string;
  durationMs: number;
  metadata?: Record<string, any>;
  timestamp: number;
}
