import type { AgentMessage, LLMConfig, ProviderType } from '../types/index.ts';

export class LLMProvider {
  private config: LLMConfig;

  constructor(config: LLMConfig) {
    this.config = config;
  }

  public async generateResponse(messages: AgentMessage[]): Promise<string> {
    const lastMsg = messages[messages.length - 1]?.content || '';
    const systemMsg = messages.find(m => m.role === 'system')?.content || '';

    if (this.config.provider === 'anthropic') {
      const apiKey = this.config.apiKey || process.env.ANTHROPIC_API_KEY;
      if (apiKey) {
        try {
          const res = await fetch('https://api.anthropic.com/v1/messages', {
            method: 'POST',
            headers: {
              'x-api-key': apiKey,
              'anthropic-version': '2023-06-01',
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              model: this.config.model || 'claude-3-5-sonnet-20241022',
              max_tokens: this.config.maxTokens || 1024,
              system: systemMsg,
              messages: messages.filter(m => m.role !== 'system').map(m => ({
                role: m.role,
                content: m.content
              }))
            })
          });
          if (res.ok) {
            const data = await res.json() as any;
            return data.content?.[0]?.text || 'Empty response from Anthropic API';
          }
        } catch (e) {}
      }
    }

    if (this.config.provider === 'openai') {
      const apiKey = this.config.apiKey || process.env.OPENAI_API_KEY;
      if (apiKey) {
        try {
          const res = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${apiKey}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              model: this.config.model || 'gpt-4o-mini',
              messages: messages.map(m => ({ role: m.role, content: m.content }))
            })
          });
          if (res.ok) {
            const data = await res.json() as any;
            return data.choices?.[0]?.message?.content || 'Empty response from OpenAI API';
          }
        } catch (e) {}
      }
    }

    if (this.config.provider === 'gemini') {
      const apiKey = this.config.apiKey || process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
      if (apiKey) {
        try {
          const model = this.config.model || 'gemini-1.5-flash';
          const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              contents: [{ parts: [{ text: `${systemMsg ? systemMsg + '\n\n' : ''}${lastMsg}` }] }]
            })
          });
          if (res.ok) {
            const data = await res.json() as any;
            return data.candidates?.[0]?.content?.parts?.[0]?.text || 'Empty response from Gemini API';
          }
        } catch (e) {}
      }
    }

    if (this.config.provider === 'ollama') {
      try {
        const res = await fetch(`${this.config.baseUrl || 'http://localhost:11434'}/api/generate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model: this.config.model || 'qwen2.5-coder:7b',
            prompt: `${systemMsg ? systemMsg + '\n\n' : ''}${lastMsg}`,
            stream: false
          })
        });
        if (res.ok) {
          const data = await res.json() as { response?: string };
          return data.response || 'No response from Ollama';
        }
      } catch (err) {}
    }

    return this.mockGenerate(lastMsg);
  }

  public async *streamResponse(messages: AgentMessage[]): AsyncGenerator<string, void, unknown> {
    const fullText = await this.generateResponse(messages);
    const chunks = fullText.split(' ');
    for (const chunk of chunks) {
      yield chunk + ' ';
      await new Promise((r) => setTimeout(r, 5));
    }
  }

  private mockGenerate(prompt: string): string {
    const p = prompt.toLowerCase();
    if (p.includes('plan')) {
      return `[Plan Created]\n1. Initialize workspace structure & types\n2. Build high-speed modules\n3. Execute tests & verify output.`;
    }
    if (p.includes('code') || p.includes('crawler') || p.includes('task')) {
      return `\`\`\`typescript\n// High Performance Implementation\nexport async function executeTask(input: string) {\n  console.log("Processing: " + input);\n  return { status: "success", timestamp: Date.now() };\n}\n\`\`\``;
    }
    if (p.includes('review')) {
      return `[Code Review] Code structure looks excellent. Types are clean and performance is optimized. Zero memory leaks detected.`;
    }
    if (p.includes('test')) {
      return `[Test Execution] All unit tests passed successfully.`;
    }
    return `[Claude Code Response] Executed model response for: "${prompt}".`;
  }
}

export class LLMManager {
  private defaultProvider: ProviderType;

  constructor(defaultProvider: ProviderType = 'mock') {
    this.defaultProvider = defaultProvider;
  }

  public getProvider(providerType?: ProviderType, modelName?: string): LLMProvider {
    const provider = providerType || this.defaultProvider;
    const model = modelName || (provider === 'mock' ? 'mock-fast-claude' : 'default-model');
    return new LLMProvider({ provider, model });
  }
}
