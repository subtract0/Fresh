"""
Simple browser-based monitor for Fresh.

Provides:
- GET /status  → JSON snapshot (uses ai.monitor.status.get_status)
- GET /stream  → Server-Sent Events (SSE) streaming JSON snapshots
- GET /ui      → Minimal HTML page subscribing to /stream

Note: This reads in-process status (activity detector, agency view). For a
separate process running agents, use the live terminal monitor or start this
server within that process for the richest view. Cross-process production
monitoring should use a shared sink (e.g., persistent store/metrics/logs).
"""
from __future__ import annotations
import asyncio
import json
from typing import AsyncGenerator

from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route
from sse_starlette.sse import EventSourceResponse

from ai.monitor.status import get_status


async def status(request):  # type: ignore
    data = get_status(limit=int(request.query_params.get("limit", 10)))
    return JSONResponse(data)


async def stream(request):  # type: ignore
    async def event_gen() -> AsyncGenerator[str, None]:
        while True:
            if await request.is_disconnected():
                break
            data = get_status(limit=int(request.query_params.get("limit", 10)))
            yield json.dumps(data)
            await asyncio.sleep(2)

    return EventSourceResponse(event_gen())


HTML = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Fresh Monitor</title>
    <style>
      body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 16px; }
      pre { background: #111; color: #0f0; padding: 12px; border-radius: 8px; overflow:auto; }
      .meta { color: #444; font-size: 12px; }
    </style>
  </head>
  <body>
    <h1>Fresh Monitor</h1>
    <div class="meta">Streaming from <code>/stream</code> every ~2s</div>
    <pre id="out">connecting...</pre>
    <script>
      const out = document.getElementById('out');
      const evt = new EventSource('/stream');
      evt.onmessage = (e) => {
        try { out.textContent = JSON.stringify(JSON.parse(e.data), null, 2); }
        catch { out.textContent = e.data; }
      };
      evt.onerror = () => { out.textContent = 'disconnected'; };
    </script>
  </body>
</html>
"""


async def ui(request):  # type: ignore
    return HTMLResponse(HTML)


routes = [
    Route("/status", status),
    Route("/stream", stream),
    Route("/ui", ui),
]

app = Starlette(debug=False, routes=routes)
