"""olapp Routes — API route handlers for components."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import tempfile
import traceback
from typing import Any, Callable, Dict, List, Optional, Tuple

from aiohttp import web

from .components import Component, Chatbot, Image, Audio, Video, File
from .utils import NumpyEncoder, decode_base64_to_file, get_temp_file, get_mime_type

logger = logging.getLogger("olapp")


class RouteManager:
    """Manages API routes for an olapp application."""

    def __init__(self, server, components: List[Component], fn: Callable = None):
        self.server = server
        self.components = components
        self.fn = fn
        self._streaming = False

    def setup_routes(self, fn_map: Dict[str, Callable] = None):
        """Setup all necessary routes."""
        if fn_map:
            for endpoint, fn in fn_map.items():
                self.server.add_route(f"/api/{endpoint}", fn)

    async def process_prediction(
        self,
        fn: Callable,
        inputs: List[Any],
        input_components: List[Component],
        output_components: List[Component],
        request_id: str = None,
    ) -> Tuple[List[Any], Optional[str]]:
        """Process a prediction with proper pre/post processing."""
        processed_inputs = []
        for i, (val, comp) in enumerate(zip(inputs, input_components)):
            try:
                processed = comp.preprocess(val)
                processed_inputs.append(processed)
            except Exception as e:
                logger.warning(f"Preprocess error for component {i}: {e}")
                processed_inputs.append(val)

        # Call the function
        try:
            if asyncio.iscoroutinefunction(fn):
                result = await fn(*processed_inputs)
            else:
                result = fn(*processed_inputs)
        except Exception as e:
            logger.error(f"Function error: {e}\n{traceback.format_exc()}")
            raise

        # Normalize result to list
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(result)

        # Postprocess outputs
        processed_outputs = []
        for i, (val, comp) in enumerate(zip(result, output_components)):
            try:
                processed = comp.postprocess(val)
                processed_outputs.append(processed)
            except Exception as e:
                logger.warning(f"Postprocess error for component {i}: {e}")
                processed_outputs.append(val)

        # Pad or trim to match output components
        while len(processed_outputs) < len(output_components):
            processed_outputs.append(None)
        processed_outputs = processed_outputs[: len(output_components)]

        return processed_outputs, request_id

    async def handle_file_upload(self, request: web.Request) -> web.Response:
        """Handle file upload."""
        reader = await request.multipart()
        files = []
        field = await reader.next()
        while field:
            if field.filename:
                suffix = os.path.splitext(field.filename)[1]
                temp_path = get_temp_file(suffix)
                with open(temp_path, "wb") as f:
                    while True:
                        chunk = await field.read_chunk()
                        if not chunk:
                            break
                        f.write(chunk)
                files.append({
                    "name": field.filename,
                    "path": temp_path,
                    "mime": get_mime_type(field.filename),
                })
            field = await reader.next()
        return web.json_response({"files": files})

    def process_chatbot_message(
        self,
        message: str,
        history: List[List[str]],
        fn: Callable,
    ) -> Tuple[str, List[List[str]]]:
        """Process a chatbot message."""
        try:
            result = fn(message, history)
            if isinstance(result, tuple) and len(result) == 2:
                response, updated_history = result
            else:
                response = result
                updated_history = history + [[message, response]]
            return response, updated_history
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            return error_msg, history + [[message, error_msg]]
