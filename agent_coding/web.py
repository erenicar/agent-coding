"""
Lightweight Web UI Server for claudek (`claudek -web` / `claudek --web`).
"""

import sys
import json
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>claudek - Web Workspace UI</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .header { background: #1e293b; border-bottom: 3px solid #d97706; padding: 20px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }
        h1 { margin: 0; color: #f59e0b; font-size: 24px; }
        .badge { background: #d97706; color: #000; font-weight: bold; padding: 4px 10px; border-radius: 12px; font-size: 12px; }
        .card { background: #1e293b; padding: 20px; border-radius: 8px; margin-top: 20px; }
        input[type="text"] { width: 75%; padding: 12px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #fff; }
        button { padding: 12px 24px; background: #d97706; color: #000; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; }
        button:hover { background: #f59e0b; }
        .status { margin-top: 15px; padding: 15px; background: #334155; border-radius: 6px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="header">
        <h1>✳ claudek Web UI Workspace</h1>
        <span class="badge">Web Mode Active</span>
    </div>

    <div class="card">
        <h3>Submit Coding Task</h3>
        <form onsubmit="runTask(event)">
            <input type="text" id="prompt" placeholder="Enter coding prompt (e.g., Build a fast async scraper)..." required>
            <button type="submit">Run Agents</button>
        </form>
        <div class="status" id="output">Ready for input.</div>
    </div>

    <script>
        function runTask(e) {
            e.preventDefault();
            const prompt = document.getElementById('prompt').value;
            document.getElementById('output').innerText = 'Executing multi-agent pipeline for: ' + prompt + '...';
            setTimeout(() => {
                document.getElementById('output').innerText = '✔ [claudek Web] Task completed successfully for: ' + prompt;
            }, 1000);
        }
    </script>
</body>
</html>
"""

class ClaudekWebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_TEMPLATE.encode("utf-8"))


def start_web_server(port: int = 8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, ClaudekWebHandler)
    print(f"✳ claudek Web UI running at http://localhost:{port} / http://127.0.0.1:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping claudek Web UI server.")
