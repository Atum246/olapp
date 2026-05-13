"""Utility functions for olapp."""

import base64
import io
import json
import os
import tempfile
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


def generate_id() -> str:
    """Generate a unique ID for components."""
    return str(uuid.uuid4())[:8]


def get_static_dir() -> Path:
    """Get the static files directory."""
    return Path(__file__).parent / "static"


def get_templates_dir() -> Path:
    """Get the templates directory."""
    return Path(__file__).parent / "templates"


def encode_file_to_base64(file_path: str) -> str:
    """Encode a file to base64 string."""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def decode_base64_to_file(base64_str: str, file_path: str) -> str:
    """Decode a base64 string to a file."""
    # Handle data URLs
    if "," in base64_str:
        base64_str = base64_str.split(",", 1)[1]
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(base64_str))
    return file_path


def get_temp_file(suffix: str = ".tmp") -> str:
    """Get a temporary file path."""
    temp_dir = tempfile.gettempdir()
    return os.path.join(temp_dir, f"olapp_{generate_id()}{suffix}")


def format_value(value: Any, component_type: str) -> Any:
    """Format a value for a specific component type."""
    if value is None:
        return None
    if component_type == "number":
        try:
            if "." in str(value):
                return float(value)
            return int(value)
        except (ValueError, TypeError):
            return value
    if component_type == "slider":
        try:
            return float(value)
        except (ValueError, TypeError):
            return value
    if component_type == "checkbox":
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        return bool(value)
    if component_type == "dataframe":
        if isinstance(value, list):
            return value
        return value
    return value


def validate_function(fn: Callable) -> None:
    """Validate that the function is callable."""
    if not callable(fn):
        raise TypeError(f"Expected a callable function, got {type(fn)}")


def get_mime_type(filename: str) -> str:
    """Get MIME type from filename."""
    ext = Path(filename).suffix.lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".avi": "video/x-msvideo",
        ".pdf": "application/pdf",
        ".json": "application/json",
        ".csv": "text/csv",
        ".txt": "text/plain",
        ".html": "text/html",
        ".css": "text/css",
        ".js": "application/javascript",
    }
    return mime_types.get(ext, "application/octet-stream")


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy types."""

    def default(self, obj: Any) -> Any:
        try:
            import numpy as np
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, np.bool_):
                return bool(obj)
        except ImportError:
            pass
        return super().default(obj)
