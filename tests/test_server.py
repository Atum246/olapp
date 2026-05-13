"""Tests for olapp server."""

import pytest
import asyncio
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, TestServer, TestClient

from olapp.server import OlappServer


class TestOlappServer:
    def test_create_server(self):
        server = OlappServer(host="127.0.0.1", port=7860, title="Test")
        assert server.host == "127.0.0.1"
        assert server.port == 7860
        assert server.title == "Test"

    def test_default_values(self):
        server = OlappServer()
        assert server.host == "127.0.0.1"
        assert server.port == 7860
        assert server.title == "Olapp"

    def test_theme(self):
        server = OlappServer(theme="dark")
        assert server.theme == "dark"

    def test_sse_clients_empty(self):
        server = OlappServer()
        assert len(server.sse_clients) == 0


@pytest.fixture
def server():
    s = OlappServer(host="127.0.0.1", port=17860, title="Test")
    return s


@pytest.mark.asyncio
async def test_server_start_stop(server):
    """Test that server can start and stop."""
    await server.start()
    assert server.site is not None
    await server.stop()


@pytest.mark.asyncio
async def test_health_endpoint(server):
    """Test health endpoint."""
    await server.start()
    from aiohttp import ClientSession
    async with ClientSession() as session:
        async with session.get("http://127.0.0.1:17860/api/health") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["status"] == "ok"
    await server.stop()


@pytest.mark.asyncio
async def test_config_endpoint(server):
    """Test config endpoint."""
    await server.start()
    from aiohttp import ClientSession
    async with ClientSession() as session:
        async with session.get("http://127.0.0.1:17860/api/config") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert "title" in data
    await server.stop()


@pytest.mark.asyncio
async def test_index_endpoint(server):
    """Test index endpoint serves HTML."""
    await server.start()
    from aiohttp import ClientSession
    async with ClientSession() as session:
        async with session.get("http://127.0.0.1:17860/") as resp:
            assert resp.status == 200
            text = await resp.text()
            assert "Olapp" in text or "<!DOCTYPE html>" in text
    await server.stop()


@pytest.mark.asyncio
async def test_static_css(server):
    """Test static CSS file serving."""
    await server.start()
    from aiohttp import ClientSession
    async with ClientSession() as session:
        async with session.get("http://127.0.0.1:17860/static/olapp.css") as resp:
            assert resp.status == 200
            text = await resp.text()
            assert "olapp" in text.lower()
    await server.stop()


@pytest.mark.asyncio
async def test_static_js(server):
    """Test static JS file serving."""
    await server.start()
    from aiohttp import ClientSession
    async with ClientSession() as session:
        async with session.get("http://127.0.0.1:17860/static/olapp.js") as resp:
            assert resp.status == 200
            text = await resp.text()
            assert "olapp" in text.lower() or "function" in text
    await server.stop()
