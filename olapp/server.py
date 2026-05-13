"""olapp HTTP Server — lightweight aiohttp-based server with SSE support."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import traceback
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from aiohttp import web

from .utils import get_static_dir, get_templates_dir, NumpyEncoder

logger = logging.getLogger("olapp")


class OlappServer:
    """Lightweight HTTP server for serving olapp interfaces."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 7860,
        title: str = "Olapp",
        theme: str = "default",
    ):
        self.host = host
        self.port = port
        self.title = title
        self.theme = theme
        self.app = web.Application()
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
        self.sse_clients: Set[web.StreamResponse] = set()
        self.routes_list: List[Dict[str, Any]] = []
        self._setup_routes()

    def _setup_routes(self):
        """Setup HTTP routes."""
        self.app.router.add_get("/", self._handle_index)
        self.app.router.add_get("/api/config", self._handle_config)
        self.app.router.add_post("/api/predict", self._handle_predict)
        self.app.router.add_post("/api/queue/push", self._handle_queue_push)
        self.app.router.add_get("/api/queue/join", self._handle_queue_join_sse)
        self.app.router.add_post("/api/queue/cancel", self._handle_queue_cancel)
        self.app.router.add_get("/api/health", self._handle_health)
        self.app.router.add_get("/static/{path:.*}", self._handle_static)

    def add_route(self, path: str, endpoint: Callable, methods: List[str] = None):
        """Add a custom API route."""
        methods = methods or ["POST"]
        self.routes_list.append({"path": path, "endpoint": endpoint, "methods": methods})
        for method in methods:
            if method.upper() == "POST":
                self.app.router.add_post(path, self._wrap_endpoint(endpoint))
            elif method.upper() == "GET":
                self.app.router.add_get(path, self._wrap_endpoint(endpoint))

    def _wrap_endpoint(self, endpoint: Callable):
        """Wrap an endpoint to handle errors and JSON."""
        async def handler(request: web.Request) -> web.Response:
            try:
                data = {}
                if request.method == "POST":
                    try:
                        data = await request.json()
                    except Exception:
                        data = {}
                result = endpoint(data)
                if asyncio.iscoroutine(result):
                    result = await result
                return web.json_response(
                    {"data": result},
                    dumps=lambda obj: json.dumps(obj, cls=NumpyEncoder),
                )
            except Exception as e:
                logger.error(f"Endpoint error: {e}\n{traceback.format_exc()}")
                return web.json_response(
                    {"error": str(e)},
                    status=500,
                )
        return handler

    async def _handle_index(self, request: web.Request) -> web.Response:
        """Serve the main HTML page."""
        template_path = get_templates_dir() / "index.html"
        if template_path.exists():
            html = template_path.read_text(encoding="utf-8")
            html = html.replace("{{ title }}", self.title)
            html = html.replace("{{ theme }}", self.theme)
            return web.Response(text=html, content_type="text/html")
        return web.Response(text="<h1>Olapp</h1><p>Template not found</p>", content_type="text/html")

    async def _handle_config(self, request: web.Request) -> web.Response:
        """Return the app configuration."""
        config = self._get_config()
        return web.json_response(
            config,
            dumps=lambda obj: json.dumps(obj, cls=NumpyEncoder),
        )

    def _get_config(self) -> Dict[str, Any]:
        """Get the app configuration. Override in subclasses."""
        return {"title": self.title, "theme": self.theme, "components": []}

    async def _handle_predict(self, request: web.Request) -> web.Response:
        """Handle a prediction request."""
        try:
            data = await request.json()
            result = await self._process_predict(data)
            return web.json_response(
                {"data": result},
                dumps=lambda obj: json.dumps(obj, cls=NumpyEncoder),
            )
        except Exception as e:
            logger.error(f"Predict error: {e}\n{traceback.format_exc()}")
            return web.json_response({"error": str(e)}, status=500)

    async def _process_predict(self, data: Dict[str, Any]) -> Any:
        """Process a prediction request. Override in subclasses."""
        raise NotImplementedError

    async def _handle_queue_push(self, request: web.Request) -> web.Response:
        """Push a request to the processing queue."""
        try:
            data = await request.json()
            request_id = data.get("request_id", "default")
            result = await self._process_predict(data.get("data", {}))
            # Notify SSE clients
            event_data = json.dumps(
                {"request_id": request_id, "output": result, "completed": True},
                cls=NumpyEncoder,
            )
            dead_clients = set()
            for client in self.sse_clients:
                try:
                    await client.write(f"data: {event_data}\n\n".encode())
                    await client.drain()
                except Exception:
                    dead_clients.add(client)
            self.sse_clients -= dead_clients
            return web.json_response({"request_id": request_id})
        except Exception as e:
            logger.error(f"Queue push error: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def _handle_queue_join_sse(self, request: web.Request) -> web.StreamResponse:
        """SSE endpoint for real-time updates."""
        response = web.StreamResponse(
            status=200,
            reason="OK",
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            },
        )
        await response.prepare(request)
        self.sse_clients.add(response)
        try:
            # Send initial connection event
            await response.write(b'data: {"connected": true}\n\n')
            await response.drain()
            # Keep connection alive
            while True:
                await asyncio.sleep(15)
                try:
                    await response.write(b': keepalive\n\n')
                    await response.drain()
                except Exception:
                    break
        except (asyncio.CancelledError, ConnectionResetError):
            pass
        finally:
            self.sse_clients.discard(response)
        return response

    async def _handle_queue_cancel(self, request: web.Request) -> web.Response:
        """Cancel a queued request."""
        return web.json_response({"status": "cancelled"})

    async def _handle_health(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        return web.json_response({"status": "ok"})

    async def _handle_static(self, request: web.Request) -> web.Response:
        """Serve static files."""
        file_path = request.match_info["path"]
        static_dir = get_static_dir()
        full_path = static_dir / file_path
        if full_path.exists() and full_path.is_file():
            content_type = "text/plain"
            if file_path.endswith(".css"):
                content_type = "text/css"
            elif file_path.endswith(".js"):
                content_type = "application/javascript"
            elif file_path.endswith(".html"):
                content_type = "text/html"
            elif file_path.endswith(".png"):
                content_type = "image/png"
            elif file_path.endswith(".svg"):
                content_type = "image/svg+xml"
            return web.Response(
                text=full_path.read_text(encoding="utf-8"),
                content_type=content_type,
            )
        raise web.HTTPNotFound()

    async def start(self):
        """Start the server."""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        url = f"http://{self.host}:{self.port}"
        logger.info(f"Olapp server running at {url}")
        print(f"\n🚀 Olapp is running at: {url}\n")
        return url

    async def stop(self):
        """Stop the server."""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()

    def run(self):
        """Run the server (blocking)."""
        url = f"http://{self.host}:{self.port}"
        print(f"\n🚀 Olapp is running at: {url}\n")
        try:
            web.run_app(self.app, host=self.host, port=self.port, print=lambda x: None)
        except KeyboardInterrupt:
            pass
