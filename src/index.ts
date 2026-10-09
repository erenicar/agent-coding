import { main } from './cli.ts';

main().catch((err) => {
  console.error('Execution error:', err);
  process.exit(1);
});
