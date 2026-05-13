"""olapp Blocks — flexible layout system for building complex interfaces."""

from __future__ import annotations

import asyncio
import json
import logging
import threading
from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .components import (
    Component, Textbox, Number, Slider, Checkbox, Dropdown, Radio, Button,
    Image, Audio, Video, File, Dataframe, Markdown, HTML, Chatbot, State,
)
from .server import OlappServer
from .routes import RouteManager
from .utils import validate_function, NumpyEncoder

logger = logging.getLogger("olapp")

# Global context stack for auto-registering components
_context_stack: List["Block"] = []


def get_current_context() -> Optional["Block"]:
    """Get the current block context, if any."""
    return _context_stack[-1] if _context_stack else None


def push_context(block: "Block"):
    """Push a block onto the context stack."""
    _context_stack.append(block)


def pop_context():
    """Pop the current block from the context stack."""
    if _context_stack:
        _context_stack.pop()


class Block:
    """Base class for layout blocks."""

    def __init__(self, elem_id: str = None):
        from .utils import generate_id
        self.elem_id = elem_id or generate_id()
        self.children: List[Union[Block, Component]] = []
        self._parent = None

    def add(self, child: Union["Block", Component]) -> "Block":
        """Add a child to this block."""
        child._parent = self
        self.children.append(child)
        return self

    def get_layout(self) -> Dict[str, Any]:
        """Get the layout configuration."""
        children_configs = []
        for child in self.children:
            if isinstance(child, Block):
                children_configs.append(child.get_layout())
            elif isinstance(child, Component):
                children_configs.append(child.get_config())
        return {
            "type": self.__class__.__name__.lower(),
            "id": self.elem_id,
            "children": children_configs,
        }

    def get_components(self) -> List[Component]:
        """Get all components in this block."""
        components = []
        for child in self.children:
            if isinstance(child, Block):
                components.extend(child.get_components())
            elif isinstance(child, Component):
                components.append(child)
        return components


class Row(Block):
    """Horizontal row layout."""

    def __init__(self, equal_height: bool = True, elem_id: str = None):
        super().__init__(elem_id=elem_id)
        self.equal_height = equal_height

    def get_layout(self) -> Dict[str, Any]:
        layout = super().get_layout()
        layout["equal_height"] = self.equal_height
        return layout


class Column(Block):
    """Vertical column layout."""

    def __init__(self, scale: int = 1, min_width: int = 0, elem_id: str = None):
        super().__init__(elem_id=elem_id)
        self.scale = scale
        self.min_width = min_width

    def get_layout(self) -> Dict[str, Any]:
        layout = super().get_layout()
        layout["scale"] = self.scale
        layout["min_width"] = self.min_width
        return layout


class Group(Block):
    """Group container with optional border."""

    def __init__(self, visible: bool = True, elem_id: str = None):
        super().__init__(elem_id=elem_id)
        self.visible = visible


class Tab(Block):
    """Tab panel."""

    def __init__(self, label: str = "Tab", elem_id: str = None):
        super().__init__(elem_id=elem_id)
        self.label = label

    def get_layout(self) -> Dict[str, Any]:
        layout = super().get_layout()
        layout["label"] = self.label
        return layout


class Tabs(Block):
    """Tabbed container."""

    def __init__(self, elem_id: str = None):
        super().__init__(elem_id=elem_id)

    def add_tab(self, tab: Tab) -> "Tabs":
        """Add a tab."""
        self.add(tab)
        return self


class Accordion(Block):
    """Collapsible section."""

    def __init__(self, label: str = "Accordion", open: bool = False, elem_id: str = None):
        super().__init__(elem_id=elem_id)
        self.label = label
        self.is_open = open

    def get_layout(self) -> Dict[str, Any]:
        layout = super().get_layout()
        layout["label"] = self.label
        layout["open"] = self.is_open
        return layout


class Blocks:
    """Flexible Blocks API for building complex interfaces."""

    def __init__(
        self,
        title: str = "Olapp",
        theme: str = "default",
        css: str = None,
        **kwargs,
    ):
        self.title = title
        self.theme = theme
        self.css = css
        self.blocks: List[Union[Block, Component]] = []
        self.fns: Dict[str, Callable] = {}
        self.dependencies: List[Dict[str, Any]] = []
        self._context_stack: List[Block] = []
        self.server: Optional[OlappServer] = None

    def add(self, item: Union[Block, Component]) -> "Blocks":
        """Add a block or component to the layout."""
        if self._context_stack:
            self._context_stack[-1].add(item)
        else:
            self.blocks.append(item)
        return self

    @contextmanager
    def row(self, **kwargs):
        """Context manager for row layout."""
        row = Row(**kwargs)
        self.add(row)
        self._context_stack.append(row)
        push_context(row)
        yield row
        pop_context()
        self._context_stack.pop()

    @contextmanager
    def column(self, **kwargs):
        """Context manager for column layout."""
        col = Column(**kwargs)
        self.add(col)
        self._context_stack.append(col)
        push_context(col)
        yield col
        pop_context()
        self._context_stack.pop()

    @contextmanager
    def group(self, **kwargs):
        """Context manager for group."""
        group = Group(**kwargs)
        self.add(group)
        self._context_stack.append(group)
        push_context(group)
        yield group
        pop_context()
        self._context_stack.pop()

    @contextmanager
    def tab(self, label: str = "Tab", **kwargs):
        """Context manager for a tab panel."""
        tab = Tab(label=label, **kwargs)
        self.add(tab)
        self._context_stack.append(tab)
        push_context(tab)
        yield tab
        pop_context()
        self._context_stack.pop()

    @contextmanager
    def tabs(self, **kwargs):
        """Context manager for tabbed container."""
        tabs = Tabs(**kwargs)
        self.add(tabs)
        self._context_stack.append(tabs)
        push_context(tabs)
        yield tabs
        pop_context()
        self._context_stack.pop()

    def click(
        self,
        fn: Callable,
        inputs: Union[Component, List[Component]] = None,
        outputs: Union[Component, List[Component]] = None,
        api_name: str = None,
        **kwargs,
    ):
        """Register a click event handler."""
        if not isinstance(inputs, list):
            inputs = [inputs] if inputs else []
        if not isinstance(outputs, list):
            outputs = [outputs] if outputs else []

        from .utils import generate_id
        api_name = api_name or f"click_{generate_id()}"
        self.fns[api_name] = fn
        self.dependencies.append({
            "trigger": "click",
            "inputs": [c.elem_id for c in inputs if isinstance(c, Component)],
            "outputs": [c.elem_id for c in outputs if isinstance(c, Component)],
            "api_name": api_name,
            "fn": fn,
        })

    def change(
        self,
        fn: Callable,
        inputs: Union[Component, List[Component]] = None,
        outputs: Union[Component, List[Component]] = None,
        api_name: str = None,
        **kwargs,
    ):
        """Register a change event handler."""
        if not isinstance(inputs, list):
            inputs = [inputs] if inputs else []
        if not isinstance(outputs, list):
            outputs = [outputs] if outputs else []

        from .utils import generate_id
        api_name = api_name or f"change_{generate_id()}"
        self.fns[api_name] = fn
        self.dependencies.append({
            "trigger": "change",
            "inputs": [c.elem_id for c in inputs if isinstance(c, Component)],
            "outputs": [c.elem_id for c in outputs if isinstance(c, Component)],
            "api_name": api_name,
            "fn": fn,
        })

    def submit(
        self,
        fn: Callable,
        inputs: Union[Component, List[Component]] = None,
        outputs: Union[Component, List[Component]] = None,
        api_name: str = None,
        **kwargs,
    ):
        """Register a submit event handler."""
        if not isinstance(inputs, list):
            inputs = [inputs] if inputs else []
        if not isinstance(outputs, list):
            outputs = [outputs] if outputs else []

        from .utils import generate_id
        api_name = api_name or f"submit_{generate_id()}"
        self.fns[api_name] = fn
        self.dependencies.append({
            "trigger": "submit",
            "inputs": [c.elem_id for c in inputs if isinstance(c, Component)],
            "outputs": [c.elem_id for c in outputs if isinstance(c, Component)],
            "api_name": api_name,
            "fn": fn,
        })

    def get_all_components(self) -> List[Component]:
        """Get all components in the layout."""
        components = []
        for item in self.blocks:
            if isinstance(item, Block):
                components.extend(item.get_components())
            elif isinstance(item, Component):
                components.append(item)
        return components

    def get_component_by_id(self, elem_id: str) -> Optional[Component]:
        """Find a component by its ID."""
        for comp in self.get_all_components():
            if comp.elem_id == elem_id:
                return comp
        return None

    def get_config(self) -> Dict[str, Any]:
        """Get the full app configuration."""
        layout = []
        for item in self.blocks:
            if isinstance(item, Block):
                layout.append(item.get_layout())
            elif isinstance(item, Component):
                layout.append(item.get_config())

        deps = []
        for dep in self.dependencies:
            deps.append({
                "trigger": dep["trigger"],
                "inputs": dep["inputs"],
                "outputs": dep["outputs"],
                "api_name": dep["api_name"],
            })

        return {
            "title": self.title,
            "theme": self.theme,
            "mode": "blocks",
            "layout": layout,
            "dependencies": deps,
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
        """Launch the blocks app."""
        self.server = OlappServer(
            host=server_name,
            port=server_port,
            title=self.title,
            theme=self.theme,
        )
        self.server._get_config = self.get_config
        self.server._process_predict = self._handle_predict

        # Register dependency endpoints
        for dep in self.dependencies:
            api_name = dep["api_name"]
            fn = dep["fn"]
            self.server.add_route(
                f"/api/{api_name}",
                lambda data, _fn=fn: self._call_fn(_fn, data),
            )

        if prevent_thread_lock:
            thread = threading.Thread(target=self.server.run, daemon=True)
            thread.start()
            return f"http://{server_name}:{server_port}", None
        else:
            self.server.run()
            return f"http://{server_name}:{server_port}", None

    async def _handle_predict(self, data: Dict[str, Any]) -> Any:
        """Handle a generic prediction request."""
        api_name = data.get("api_name", "default")
        fn_data = data.get("data", {})

        if api_name in self.fns:
            fn = self.fns[api_name]
        else:
            # Try to find the first dependency
            if self.dependencies:
                fn = self.dependencies[0]["fn"]
            else:
                raise ValueError("No function registered")

        return self._call_fn(fn, fn_data)

    def _call_fn(self, fn: Callable, data: Any) -> Any:
        """Call a function with data."""
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        if not isinstance(data, list):
            data = [data]
        result = fn(*data)
        if not isinstance(result, (list, tuple)):
            result = [result]
        return result

    def close(self):
        """Close the server."""
        if self.server:
            asyncio.get_event_loop().run_until_complete(self.server.stop())

    def __enter__(self):
        push_context(self)
        return self

    def __exit__(self, *args):
        pop_context()
