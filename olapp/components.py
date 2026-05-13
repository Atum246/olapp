"""olapp Components — UI building blocks."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .utils import generate_id


class Component:
    """Base class for all olapp components."""

    def __init__(
        self,
        label: str = "",
        value: Any = None,
        visible: bool = True,
        interactive: bool = True,
        elem_id: Optional[str] = None,
        **kwargs,
    ):
        self.label = label
        self._value = value
        self.visible = visible
        self.interactive = interactive
        self.elem_id = elem_id or generate_id()
        self.type = self.__class__.__name__.lower()
        self.container = kwargs.get("container", True)
        self.scale = kwargs.get("scale", None)
        self.min_width = kwargs.get("min_width", None)

        # Auto-register with current block context if one exists (lazy import to avoid circular)
        try:
            from .blocks import get_current_context
            ctx = get_current_context()
            if ctx is not None:
                ctx.add(self)
        except ImportError:
            pass

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, val: Any):
        self._value = val

    def get_config(self) -> Dict[str, Any]:
        """Return the component config for the frontend."""
        return {
            "id": self.elem_id,
            "type": self.type,
            "label": self.label,
            "value": self._value,
            "visible": self.visible,
            "interactive": self.interactive,
        }

    def preprocess(self, x: Any) -> Any:
        """Process input from frontend before passing to function."""
        return x

    def postprocess(self, y: Any) -> Any:
        """Process output from function before sending to frontend."""
        return y

    def as_example(self) -> Any:
        """Return example input."""
        return self._value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(label='{self.label}', elem_id='{self.elem_id}')"


class Textbox(Component):
    """Multiline text input."""

    def __init__(
        self,
        lines: int = 1,
        max_lines: int = 20,
        placeholder: str = "",
        label: str = "Textbox",
        value: str = "",
        **kwargs,
    ):
        self.lines = lines
        self.max_lines = max_lines
        self.placeholder = placeholder
        super().__init__(label=label, value=value, **kwargs)

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        config.update({
            "lines": self.lines,
            "max_lines": self.max_lines,
            "placeholder": self.placeholder,
        })
        return config

    def preprocess(self, x: Any) -> str:
        return str(x) if x is not None else ""

    def postprocess(self, y: Any) -> str:
        return str(y) if y is not None else ""


class Number(Component):
    """Numeric input."""

    def __init__(
        self,
        minimum: Optional[float] = None,
        maximum: Optional[float] = None,
        step: float = 1,
        label: str = "Number",
        value: Optional[float] = None,
        precision: Optional[int] = None,
        **kwargs,
    ):
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
        self.precision = precision
        super().__init__(label=label, value=value, **kwargs)

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        config.update({
            "minimum": self.minimum,
            "maximum": self.maximum,
            "step": self.step,
            "precision": self.precision,
        })
        return config

    def preprocess(self, x: Any) -> Optional[float]:
        if x is None or x == "":
            return None
        try:
            val = float(x)
            if self.minimum is not None:
                val = max(self.minimum, val)
            if self.maximum is not None:
                val = min(self.maximum, val)
            if self.precision is not None:
                val = round(val, self.precision)
            return val
        except (ValueError, TypeError):
            return None

    def postprocess(self, y: Any) -> Optional[float]:
        if y is None:
            return None
        return float(y)


class Slider(Component):
    """Numeric slider input."""

    def __init__(
        self,
        minimum: float = 0,
        maximum: float = 100,
        step: float = 1,
        label: str = "Slider",
        value: Optional[float] = None,
        **kwargs,
    ):
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
        if value is None:
            value = minimum
        super().__init__(label=label, value=value, **kwargs)

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        config.update({
            "minimum": self.minimum,
            "maximum": self.maximum,
            "step": self.step,
        })
        return config

    def preprocess(self, x: Any) -> float:
        return float(x) if x is not None else self.minimum

    def postprocess(self, y: Any) -> float:
        return float(y) if y is not None else self.minimum


class Checkbox(Component):
    """Boolean checkbox input."""

    def __init__(
        self,
        label: str = "Checkbox",
        value: bool = False,
        **kwargs,
    ):
        super().__init__(label=label, value=value, **kwargs)

    def preprocess(self, x: Any) -> bool:
        if isinstance(x, str):
            return x.lower() in ("true", "1", "yes", "on")
        return bool(x)

    def postprocess(self, y: Any) -> bool:
        return bool(y)


class Dropdown(Component):
    """Dropdown selection input."""

    def __init__(
        self,
        choices: List[str] = None,
        label: str = "Dropdown",
        value: Optional[str] = None,
        multiselect: bool = False,
        max_choices: Optional[int] = None,
        **kwargs,
    ):
        self.choices = choices or []
        self.multiselect = multiselect
        self.max_choices = max_choices
        if value is None and self.choices:
            value = self.choices[0] if not multiselect else []
        super().__init__(label=label, value=value, **kwargs)

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        config.update({
            "choices": self.choices,
            "multiselect": self.multiselect,
            "max_choices": self.max_choices,
        })
        return config

    def preprocess(self, x: Any) -> Any:
        if self.multiselect:
            if isinstance(x, str):
                return [x]
            return x if isinstance(x, list) else [x]
        return x

    def postprocess(self, y: Any) -> Any:
        return y


class Radio(Component):
    """Radio button selection."""

    def __init__(
        self,
        choices: List[str] = None,
        label: str = "Radio",
        value: Optional[str] = None,
        **kwargs,
    ):
        self.choices = choices or []
        if value is None and self.choices:
            value = self.choices[0]
        super().__init__(label=label, value=value, **kwargs)

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        config.update({"choices": self.choices})
        return config


class Button(Component):
    """Clickable button."""

    def __init__(
        self,
        label: str = "Submit",
        value: str = "",
        variant: str = "primary",
        **kwargs,
    ):
        self.variant = variant
        super().__init__(label=label, value=value or label, **kwargs)

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        config.update({"variant": self.variant})
        return config


class Image(Component):
    """Image upload/display."""

    def __init__(
        self,
        label: str = "Image",
        value: Any = None,
        type: str = "filepath",
        height: int = None,
        width: int = None,
        sources: List[str] = None,
        **kwargs,
    ):
        self.image_type = type
        self.height = height
        self.width = width
        self.sources = sources or ["upload", "clipboard"]
        super().__init__(label=label, value=value, **kwargs)

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        config.update({
            "image_type": self.image_type,
            "height": self.height,
            "width": self.width,
            "sources": self.sources,
        })
        return config

    def preprocess(self, x: Any) -> Any:
        """Process base64 image from frontend."""
        return x

    def postprocess(self, y: Any) -> Any:
        """Process image for frontend display."""
        if y is None:
            return None
        if isinstance(y, str) and os.path.isfile(y):
            from .utils import encode_file_to_base64, get_mime_type
            mime = get_mime_type(y)
            b64 = encode_file_to_base64(y)
            return f"data:{mime};base64,{b64}"
        if isinstance(y, str) and y.startswith("data:"):
            return y
        if isinstance(y, bytes):
            import base64
            return f"data:image/png;base64,{base64.b64encode(y).decode()}"
        return y


class Audio(Component):
    """Audio upload/playback."""

    def __init__(
        self,
        label: str = "Audio",
        value: Any = None,
        type: str = "filepath",
        sources: List[str] = None,
        **kwargs,
    ):
        self.audio_type = type
        self.sources = sources or ["upload", "microphone"]
        super().__init__(label=label, value=value, **kwargs)

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        config.update({
            "audio_type": self.audio_type,
            "sources": self.sources,
        })
        return config

    def postprocess(self, y: Any) -> Any:
        if y is None:
            return None
        if isinstance(y, str) and os.path.isfile(y):
            from .utils import encode_file_to_base64, get_mime_type
            mime = get_mime_type(y)
            b64 = encode_file_to_base64(y)
            return f"data:{mime};base64,{b64}"
        return y


class Video(Component):
    """Video upload/playback."""

    def __init__(
        self,
        label: str = "Video",
        value: Any = None,
        sources: List[str] = None,
        **kwargs,
    ):
        self.sources = sources or ["upload"]
        super().__init__(label=label, value=value, **kwargs)

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        config.update({"sources": self.sources})
        return config

    def postprocess(self, y: Any) -> Any:
        if y is None:
            return None
        if isinstance(y, str) and os.path.isfile(y):
            from .utils import encode_file_to_base64, get_mime_type
            mime = get_mime_type(y)
            b64 = encode_file_to_base64(y)
            return f"data:{mime};base64,{b64}"
        return y


class File(Component):
    """File upload/download."""

    def __init__(
        self,
        label: str = "File",
        value: Any = None,
        file_types: List[str] = None,
        file_count: str = "single",
        **kwargs,
    ):
        self.file_types = file_types or []
        self.file_count = file_count
        super().__init__(label=label, value=value, **kwargs)

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        config.update({
            "file_types": self.file_types,
            "file_count": self.file_count,
        })
        return config


class Dataframe(Component):
    """Tabular data input/output."""

    def __init__(
        self,
        headers: List[str] = None,
        row_count: int = 3,
        col_count: int = 3,
        datatype: Union[str, List[str]] = "str",
        label: str = "Dataframe",
        value: Any = None,
        wrap: bool = False,
        **kwargs,
    ):
        self.headers = headers
        self.row_count = row_count
        self.col_count = col_count
        self.datatype = datatype
        self.wrap = wrap
        super().__init__(label=label, value=value, **kwargs)

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        config.update({
            "headers": self.headers,
            "row_count": self.row_count,
            "col_count": self.col_count,
            "datatype": self.datatype,
            "wrap": self.wrap,
        })
        return config

    def preprocess(self, x: Any) -> Any:
        return x

    def postprocess(self, y: Any) -> Any:
        if y is None:
            return {"headers": [], "data": []}
        if isinstance(y, dict) and "headers" in y:
            return y
        # Handle pandas DataFrame
        try:
            import pandas as pd
            if isinstance(y, pd.DataFrame):
                return {
                    "headers": list(y.columns),
                    "data": y.values.tolist(),
                }
        except ImportError:
            pass
        # Handle list of lists
        if isinstance(y, list) and y and isinstance(y[0], list):
            if self.headers:
                return {"headers": self.headers, "data": y}
            return {"headers": [f"Col {i}" for i in range(len(y[0]))], "data": y}
        return y


class Markdown(Component):
    """Markdown display."""

    def __init__(
        self,
        label: str = "",
        value: str = "",
        **kwargs,
    ):
        super().__init__(label=label, value=value, **kwargs)

    def postprocess(self, y: Any) -> str:
        return str(y) if y is not None else ""


class HTML(Component):
    """Raw HTML display."""

    def __init__(
        self,
        label: str = "",
        value: str = "",
        **kwargs,
    ):
        super().__init__(label=label, value=value, **kwargs)

    def postprocess(self, y: Any) -> str:
        return str(y) if y is not None else ""


class Chatbot(Component):
    """Chatbot message display."""

    def __init__(
        self,
        label: str = "Chatbot",
        value: List[List[str]] = None,
        height: int = 400,
        placeholder: str = "Type a message...",
        **kwargs,
    ):
        self.height = height
        self.placeholder = placeholder
        super().__init__(label=label, value=value or [], **kwargs)

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        config.update({
            "height": self.height,
            "placeholder": self.placeholder,
        })
        return config

    def preprocess(self, x: Any) -> Any:
        return x

    def postprocess(self, y: Any) -> List[List[str]]:
        if y is None:
            return []
        if isinstance(y, list):
            result = []
            for msg in y:
                if isinstance(msg, (list, tuple)) and len(msg) == 2:
                    result.append([str(msg[0]) if msg[0] else None, str(msg[1]) if msg[1] else None])
                elif isinstance(msg, dict):
                    result.append([
                        str(msg.get("user", "")),
                        str(msg.get("bot", ""))
                    ])
            return result
        return y


class State(Component):
    """Hidden state component for storing data between interactions."""

    def __init__(
        self,
        value: Any = None,
        **kwargs,
    ):
        super().__init__(label="", value=value, visible=False, **kwargs)
        self.type = "state"

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        config["visible"] = False
        return config


class ColorPicker(Component):
    """Color picker component."""

    def __init__(
        self,
        label: str = "Color",
        value: str = "#6366f1",
        **kwargs,
    ):
        super().__init__(label=label, value=value, **kwargs)

    def postprocess(self, y: Any) -> str:
        return str(y) if y is not None else "#6366f1"


class DateTime(Component):
    """Date and time picker."""

    def __init__(
        self,
        label: str = "Date & Time",
        value: str = "",
        include_time: bool = True,
        **kwargs,
    ):
        self.include_time = include_time
        super().__init__(label=label, value=value, **kwargs)

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        config["include_time"] = self.include_time
        return config


class Code(Component):
    """Code editor component."""

    def __init__(
        self,
        label: str = "Code",
        value: str = "",
        language: str = "python",
        lines: int = 10,
        **kwargs,
    ):
        self.language = language
        self.lines = lines
        super().__init__(label=label, value=value, **kwargs)

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        config.update({"language": self.language, "lines": self.lines})
        return config


class Gallery(Component):
    """Image gallery component."""

    def __init__(
        self,
        label: str = "Gallery",
        value: List[str] = None,
        columns: int = 3,
        height: int = 200,
        **kwargs,
    ):
        self.columns = columns
        self.height = height
        super().__init__(label=label, value=value or [], **kwargs)

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        config.update({"columns": self.columns, "height": self.height})
        return config

    def postprocess(self, y: Any) -> List[str]:
        if y is None:
            return []
        if isinstance(y, list):
            return [str(item) for item in y]
        return [str(y)]


class Label(Component):
    """Classification label display with confidence scores."""

    def __init__(
        self,
        label: str = "Prediction",
        value: Dict[str, float] = None,
        num_top_classes: int = 5,
        **kwargs,
    ):
        self.num_top_classes = num_top_classes
        super().__init__(label=label, value=value or {}, **kwargs)

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        config["num_top_classes"] = self.num_top_classes
        return config

    def postprocess(self, y: Any) -> Dict[str, float]:
        if y is None:
            return {}
        if isinstance(y, dict):
            return {str(k): float(v) for k, v in y.items()}
        if isinstance(y, str):
            return {y: 1.0}
        return {}


class HighlightedText(Component):
    """Text with highlighted spans for NER/sentiment."""

    def __init__(
        self,
        label: str = "Highlighted Text",
        value: List[Tuple[str, str]] = None,
        **kwargs,
    ):
        super().__init__(label=label, value=value or [], **kwargs)

    def postprocess(self, y: Any) -> List[Tuple[str, str]]:
        if y is None:
            return []
        if isinstance(y, list):
            result = []
            for item in y:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    result.append([str(item[0]), str(item[1])])
                elif isinstance(item, str):
                    result.append([item, ""])
            return result
        return []


class JSON(Component):
    """JSON display component."""

    def __init__(
        self,
        label: str = "JSON",
        value: Any = None,
        **kwargs,
    ):
        super().__init__(label=label, value=value or {}, **kwargs)

    def postprocess(self, y: Any) -> Any:
        return y if y is not None else {}


class Progress(Component):
    """Progress bar component."""

    def __init__(
        self,
        label: str = "Progress",
        value: float = 0.0,
        **kwargs,
    ):
        super().__init__(label=label, value=value, **kwargs)

    def postprocess(self, y: Any) -> float:
        if y is None:
            return 0.0
        try:
            return max(0.0, min(1.0, float(y)))
        except (ValueError, TypeError):
            return 0.0


# Component registry
COMPONENT_MAP = {
    "textbox": Textbox,
    "number": Number,
    "slider": Slider,
    "checkbox": Checkbox,
    "dropdown": Dropdown,
    "radio": Radio,
    "button": Button,
    "image": Image,
    "audio": Audio,
    "video": Video,
    "file": File,
    "dataframe": Dataframe,
    "markdown": Markdown,
    "html": HTML,
    "chatbot": Chatbot,
    "state": State,
    "colorpicker": ColorPicker,
    "color": ColorPicker,
    "datetime": DateTime,
    "code": Code,
    "gallery": Gallery,
    "label": Label,
    "highlightedtext": HighlightedText,
    "json": JSON,
    "progress": Progress,
}


def get_component_class(name: str) -> type:
    """Get component class by name."""
    name = name.lower()
    if name in COMPONENT_MAP:
        return COMPONENT_MAP[name]
    raise ValueError(f"Unknown component type: {name}. Available: {list(COMPONENT_MAP.keys())}")
