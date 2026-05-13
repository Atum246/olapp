"""Tests for olapp routes."""

import pytest
import asyncio
from olapp.routes import RouteManager
from olapp.server import OlappServer
from olapp.components import Textbox, Number, Slider


class TestRouteManager:
    def test_create(self):
        server = OlappServer()
        components = [Textbox(), Number()]
        rm = RouteManager(server, components)
        assert rm.server is server
        assert len(rm.components) == 2

    def test_create_with_fn(self):
        server = OlappServer()
        rm = RouteManager(server, [], fn=lambda x: x)
        assert rm.fn is not None


@pytest.mark.asyncio
async def test_process_prediction():
    """Test prediction processing."""
    server = OlappServer()
    input_comps = [Textbox(), Number()]
    output_comps = [Textbox()]
    
    def fn(name, num):
        return f"{name} x{int(num)}"
    
    rm = RouteManager(server, input_comps, fn)
    result, req_id = await rm.process_prediction(
        fn=fn,
        inputs=["hello", 3],
        input_components=input_comps,
        output_components=output_comps,
    )
    assert result == ["hello x3"]
    assert req_id is None


@pytest.mark.asyncio
async def test_process_prediction_with_request_id():
    """Test prediction with request ID."""
    server = OlappServer()
    input_comps = [Textbox()]
    output_comps = [Textbox()]
    
    def fn(x):
        return x.upper()
    
    rm = RouteManager(server, input_comps, fn)
    result, req_id = await rm.process_prediction(
        fn=fn,
        inputs=["hello"],
        input_components=input_comps,
        output_components=output_comps,
        request_id="test-123",
    )
    assert result == ["HELLO"]
    assert req_id == "test-123"


@pytest.mark.asyncio
async def test_process_prediction_multiple_outputs():
    """Test prediction with multiple outputs."""
    server = OlappServer()
    input_comps = [Textbox()]
    output_comps = [Textbox(), Number()]
    
    def fn(x):
        return x, len(x)
    
    rm = RouteManager(server, input_comps, fn)
    result, _ = await rm.process_prediction(
        fn=fn,
        inputs=["hello"],
        input_components=input_comps,
        output_components=output_comps,
    )
    assert result == ["hello", 5]
