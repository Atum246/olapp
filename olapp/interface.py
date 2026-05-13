"""olapp Interface — simple function-to-UI interface."""

from __future__ import annotations

import asyncio
import json
import logging
import signal
import sys
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .components import (
    Component, Textbox, Number, Slider, Checkbox, Dropdown, Radio, Button,
    Image, Audio, Video, File, Dataframe, Markdown, HTML, Chatbot, State,
    get_component_class,
)
from .server import OlappServer
from .routes import RouteManager
from .utils import validate_function, NumpyEncoder

logger = logging.getLogger("olapp")


class Interface:
    """Simple Interface API — similar to Gradio's Interface."""

    def __init__(
        self,
        fn: Callable,
        inputs: Union[str, Component, List[Union[str, Component]]] = None,
        outputs: Union[str, Component, List[Union[str, Component]]] = None,
        title: str = "Olapp",
        description: str = "",
        examples: List[List[Any]] = None,
        live: bool = False,
        batch: bool = False,
        max_batch_size: int = 4,
        theme: str = "default",
        css: str = None,
        **kwargs,
    ):
        validate_function(fn)
        self.fn = fn
        self.title = title
        self.description = description
        self.examples = examples
        self.live = live
        self.batch = batch
        self.max_batch_size = max_batch_size
        self.theme = theme
        self.css = css

        # Normalize inputs/outputs
        self.input_components = self._normalize_components(inputs or [])
        self.output_components = self._normalize_components(outputs or [])

        self.server: Optional[OlappServer] = None
        self._running = False

    def _normalize_components(
        self, components: Union[str, Component, List[Union[str, Component]]]
    ) -> List[Component]:
        """Convert string component names to Component instances."""
        if not components:
            return []
        if not isinstance(components, list):
            components = [components]
        result = []
        for comp in components:
            if isinstance(comp, Component):
                result.append(comp)
            elif isinstance(comp, str):
                cls = get_component_class(comp)
                result.append(cls())
            else:
                raise TypeError(f"Expected Component or string, got {type(comp)}")
        return result

    def get_config(self) -> Dict[str, Any]:
        """Get the full app configuration."""
        return {
            "title": self.title,
            "description": self.description,
            "theme": self.theme,
            "mode": "interface",
            "live": self.live,
            "components": {
                "inputs": [c.get_config() for c in self.input_components],
                "outputs": [c.get_config() for c in self.output_components],
            },
            "examples": self.examples,
            "css": self.css,
        }

    def launch(
        self,
        server_name: str = "127.0.0.1",
        server_port: int = 7860,
        share: bool = False,
        prevent_thread_lock: bool = False,
        **kwargs,
    ):
        """Launch the interface."""
        self.server = OlappServer(
            host=server_name,
            port=server_port,
            title=self.title,
            theme=self.theme,
        )
        # Override config method
        self.server._get_config = self.get_config
        self.server._process_predict = self._handle_predict

        if prevent_thread_lock:
            thread = threading.Thread(target=self._run_server, daemon=True)
            thread.start()
            return f"http://{server_name}:{server_port}", None
        else:
            self._run_server()
            return f"http://{server_name}:{server_port}", None

    def _run_server(self):
        """Run the server (blocking)."""
        self._running = True
        try:
            self.server.run()
        except KeyboardInterrupt:
            self._running = False

    async def _handle_predict(self, data: Dict[str, Any]) -> Any:
        """Handle a prediction request."""
        inputs = data.get("data", [])
        if not isinstance(inputs, list):
            inputs = [inputs]

        route_manager = RouteManager(self.server, self.input_components, self.fn)
        result, _ = await route_manager.process_prediction(
            fn=self.fn,
            inputs=inputs,
            input_components=self.input_components,
            output_components=self.output_components,
        )
        return result

    def close(self):
        """Close the server."""
        if self.server:
            asyncio.get_event_loop().run_until_complete(self.server.stop())
        self._running = False
