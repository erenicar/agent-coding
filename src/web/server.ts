import { WorkspaceManager } from '../fs/workspace.ts';

export function startWebServer(port = 8080): void {
  const wsManager = new WorkspaceManager();
  const wsConfig = wsManager.getConfig();

  const server = Bun.serve({
    port,
    fetch(req) {
      const url = new URL(req.url);

      if (url.pathname === '/api/workspace') {
        return new Response(JSON.stringify(wsConfig), {
          headers: { 'Content-Type': 'application/json' }
        });
      }

      const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>claudek Web Workspace UI</title>
  <style>
    body { font-family: monospace; background: #0f172a; color: #f8fafc; padding: 2rem; }
    h1 { color: #38bdf8; }
    .card { background: #1e293b; padding: 1.5rem; border-radius: 8px; margin-top: 1rem; }
    .badge { background: #0284c7; color: white; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.8rem; }
  </style>
</head>
<body>
  <h1>✳ claudek - Web Workspace UI <span class="badge">TypeScript + Bun</span></h1>
  <div class="card">
    <h3>Current Workspace</h3>
    <p><strong>Path:</strong> ${wsConfig.currentDir}</p>
    <p><strong>Windows Path:</strong> ${wsConfig.windowsPath || 'N/A'}</p>
    <p><strong>Ubuntu Path:</strong> ${wsConfig.ubuntuPath || 'N/A'}</p>
  </div>
</body>
</html>`;

      return new Response(html, {
        headers: { 'Content-Type': 'text/html' }
      });
    }
  });

  console.log(`\x1b[1;32m🌐 claudek Web UI running at http://localhost:${server.port}\x1b[0m`);
}
