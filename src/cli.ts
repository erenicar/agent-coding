import { Orchestrator } from './agent/orchestrator.ts';
import { FreeModelDiscoverer } from './llm/freeModels.ts';
import { ClaudeCodeTerminalTUI } from './tui/terminal.ts';
import { startWebServer } from './web/server.ts';
import type { ProviderType } from './types/index.ts';
import * as readline from 'node:readline';

export async function main() {
  const args = Bun.argv.slice(2);
  const tui = new ClaudeCodeTerminalTUI();

  let prompt = 'Create a high-performance TypeScript web crawler';
  let provider: ProviderType = 'mock';
  let isWeb = false;
  let isInteractive = false;
  let listFreeModels = false;
  let port = 8080;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '-web' || arg === '--web') {
      isWeb = true;
    } else if (arg === '--prompt' && args[i + 1]) {
      prompt = args[++i];
    } else if (arg === '--provider' && args[i + 1]) {
      provider = args[++i] as ProviderType;
    } else if (arg === '--port' && args[i + 1]) {
      port = parseInt(args[++i], 10);
    } else if (arg === '--interactive' || arg === '-i') {
      isInteractive = true;
    } else if (arg === '--list-free-models') {
      listFreeModels = true;
    } else if (arg === '--help' || arg === '-h') {
      console.log(`
Usage: claudek [options]

Options:
  --prompt <task>         Coding task or prompt to execute
  --provider <provider>   LLM Provider (anthropic, openai, gemini, ollama, mock)
  --list-free-models      Auto-discover and display all available free-tier models
  --interactive, -i       Launch interactive CLI prompt mode
  --web, -web             Launch claudek Web UI workspace server
  --port <port>           Port for Web UI server (default: 8080)
  --help, -h              Show help menu
      `);
      return;
    }
  }

  if (isWeb) {
    startWebServer(port);
    return;
  }

  console.log(tui.renderHeader());

  if (listFreeModels) {
    const freeModels = await FreeModelDiscoverer.discoverFreeModels(true);
    console.log(tui.renderFreeModelsTable(freeModels));
    return;
  }

  if (isInteractive) {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    const userInput = await new Promise<string>((resolve) => {
      rl.question('✳ claudek > Enter coding task: ', (answer) => {
        rl.close();
        resolve(answer);
      });
    });
    if (userInput.trim()) {
      prompt = userInput.trim();
    }
  }

  console.log(`\x1b[1;36m▶ Running orchestrator for prompt: "${prompt}"\x1b[0m\n`);
  const orchestrator = new Orchestrator(provider);
  const result = await orchestrator.runPipeline(prompt, (task) => {
    console.log(`\x1b[38;5;244m[Task ${task.id}]\x1b[0m ${task.title}: \x1b[1;33m${task.status.toUpperCase()}\x1b[0m`);
  });

  console.log(tui.renderPipelineResult(result));
}
