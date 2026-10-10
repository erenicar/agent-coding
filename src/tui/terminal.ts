import type { FreeModel, PipelineResult, ProviderType } from '../types/index.ts';
import { WorkspaceManager } from '../fs/workspace.ts';
import { FreeModelDiscoverer } from '../llm/freeModels.ts';
import { Orchestrator } from '../agent/orchestrator.ts';
import { LoopDetector } from '../loop/detector.ts';
import * as readline from 'node:readline';

export class ClaudeCodeTerminalTUI {
  private workspace: WorkspaceManager;
  private loopDetector: LoopDetector;

  constructor() {
    this.workspace = new WorkspaceManager();
    this.loopDetector = new LoopDetector();
  }

  public renderHeader(): string {
    const ws = this.workspace.getConfig();
    return `
\x1b[1;38;5;208m  ╭─────────────────────────────────────────────────────────────╮
  │                                                             │
  │   \x1b[1;36m✳ CLAUDE CODE TERMINAL TUI\x1b[1;38;5;208m  [TypeScript + Bun Engine]    │
  │   \x1b[38;5;244mClaude Agent Workspace | High Performance Execution\x1b[1;38;5;208m     │
  │                                                             │
  ╰─────────────────────────────────────────────────────────────╯\x1b[0m

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

  public async startInteractiveLoop(provider: ProviderType = 'mock'): Promise<void> {
    console.clear();
    console.log(this.renderHeader());
    console.log(`\x1b[1;32mWelcome to Claude Code Terminal TUI!\x1b[0m`);
    console.log(`\x1b[38;5;244mType your prompt or slash commands (\x1b[1;37m/help\x1b[38;5;244m, \x1b[1;37m/models\x1b[38;5;244m, \x1b[1;37m/clear\x1b[38;5;244m, \x1b[1;37m/exit\x1b[38;5;244m)\x1b[0m\n`);

    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: '\x1b[1;36m✳ claudek > \x1b[0m'
    });

    const orchestrator = new Orchestrator(provider);

    rl.prompt();

    for await (const line of rl) {
      const input = line.trim();

      if (!input) {
        rl.prompt();
        continue;
      }

      const loopCheck = this.loopDetector.analyze(input);
      if (loopCheck.isLoop) {
        console.log(`\n\x1b[1;31m⚠️ Loop Detected:\x1b[0m ${loopCheck.reason}\n`);
        rl.prompt();
        continue;
      }

      if (input === '/exit' || input === '/quit') {
        console.log('\x1b[1;33mBye!\x1b[0m');
        rl.close();
        break;
      }

      if (input === '/clear') {
        console.clear();
        console.log(this.renderHeader());
        rl.prompt();
        continue;
      }

      if (input === '/help') {
        console.log(`
\x1b[1;36mClaude Code TUI Slash Commands:\x1b[0m
  \x1b[1;33m/models\x1b[0m     List available free-tier models
  \x1b[1;33m/workspace\x1b[0m  Show active workspace paths
  \x1b[1;33m/clear\x1b[0m      Clear screen
  \x1b[1;33m/help\x1b[0m       Show this help message
  \x1b[1;33m/exit\x1b[0m       Exit interactive TUI
`);
        rl.prompt();
        continue;
      }

      if (input === '/models') {
        const models = await FreeModelDiscoverer.discoverFreeModels();
        console.log(this.renderFreeModelsTable(models));
        rl.prompt();
        continue;
      }

      if (input === '/workspace') {
        const ws = this.workspace.getConfig();
        console.log(`\n\x1b[1;34mDirectory:\x1b[0m ${ws.currentDir}`);
        console.log(`\x1b[1;33mWindows:\x1b[0m   ${ws.windowsPath}`);
        console.log(`\x1b[1;32mUbuntu:\x1b[0m    ${ws.ubuntuPath}\n`);
        rl.prompt();
        continue;
      }

      // Execute prompt task
      console.log(`\n\x1b[1;36m▶ Running orchestrator for prompt: "${input}"\x1b[0m\n`);
      const result = await orchestrator.runPipeline(input, (task) => {
        console.log(`\x1b[38;5;244m[Task ${task.id}]\x1b[0m ${task.title}: \x1b[1;33m${task.status.toUpperCase()}\x1b[0m`);
      });

      console.log(this.renderPipelineResult(result));
      rl.prompt();
    }
  }

  public print(message: string): void {
    console.log(message);
  }
}
