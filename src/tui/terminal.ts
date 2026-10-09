import type { FreeModel, PipelineResult } from '../types/index.ts';
import { WorkspaceManager } from '../fs/workspace.ts';

export class ClaudeCodeTerminalTUI {
  private workspace: WorkspaceManager;

  constructor() {
    this.workspace = new WorkspaceManager();
  }

  public renderHeader(): string {
    const ws = this.workspace.getConfig();
    return `
\x1b[1;38;5;208m
  ╭─────────────────────────────────────────────────────────────╮
  │                                                             │
  │   \x1b[1;36m✳ CLAUDE CODE TERMINAL TUI\x1b[1;38;5;208m  [TypeScript + Bun Engine]    │
  │   \x1b[38;5;244mClaude Agent Workspace | High Performance Execution\x1b[1;38;5;208m     │
  │                                                             │
  ╰─────────────────────────────────────────────────────────────╯
\x1b[0m
  \x1b[1;34m📁 Workspace:\x1b[0m ${ws.currentDir}
  \x1b[1;33m💻 Windows Path:\x1b[0m ${ws.windowsPath || 'N/A'}
  \x1b[1;32m🐧 Ubuntu Path:\x1b[0m  ${ws.ubuntuPath || 'N/A'}
`;
  }

  public renderFreeModelsTable(models: FreeModel[]): string {
    let out = `\n\x1b[1;35mAVAILABLE FREE-TIER LLM MODELS:\x1b[0m\n`;
    out += `\x1b[38;5;242m┌───────────────┬────────────────────────────┬─────────────────────┬─────────┐\x1b[0m\n`;
    out += `\x1b[38;5;242m│\x1b[1;37m Provider      \x1b[38;5;242m│\x1b[1;37m Model                      \x1b[38;5;242m│\x1b[1;37m Limits              \x1b[38;5;242m│\x1b[1;37m Speed   \x1b[38;5;242m│\x1b[0m\n`;
    out += `\x1b[38;5;242m├───────────────┼────────────────────────────┼─────────────────────┼─────────┤\x1b[0m\n`;

    for (const m of models) {
      const p = m.provider.padEnd(13);
      const mod = m.model.padEnd(26);
      const lim = (m.limits || 'Unlimited').padEnd(19);
      const spd = `${m.speedRating || 100}%`.padEnd(7);
      out += `\x1b[38;5;242m│\x1b[36m ${p} \x1b[38;5;242m│\x1b[32m ${mod} \x1b[38;5;242m│\x1b[33m ${lim} \x1b[38;5;242m│\x1b[35m ${spd} \x1b[38;5;242m│\x1b[0m\n`;
    }

    out += `\x1b[38;5;242m└───────────────┴────────────────────────────┴─────────────────────┴─────────┘\x1b[0m\n`;
    return out;
  }

  public renderPipelineResult(result: PipelineResult): string {
    let out = `\n\x1b[1;32m✔ PIPELINE EXECUTION COMPLETED (${result.totalTimeMs}ms)\x1b[0m\n\n`;

    out += `\x1b[1;34m📋 User Task:\x1b[0m ${result.prompt}\n\n`;

    if (result.plan) {
      out += `\x1b[1;33m1. Architecture Plan:\x1b[0m\n${result.plan}\n\n`;
    }

    if (result.code) {
      out += `\x1b[1;36m2. Generated Code:\x1b[0m\n${result.code}\n\n`;
    }

    if (result.review) {
      out += `\x1b[1;35m3. Code Review & Safety Audit:\x1b[0m\n${result.review}\n\n`;
    }

    if (result.testResult) {
      out += `\x1b[1;32m4. Test Verification:\x1b[0m\n${result.testResult}\n\n`;
    }

    out += `\x1b[38;5;242m─────────────────────────────────────────────────────────────\x1b[0m\n`;
    return out;
  }

  public print(message: string): void {
    console.log(message);
  }
}
