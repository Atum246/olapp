"""Installation and integration tests for olapp."""

import subprocess
import sys
import os


def test_package_importable():
    """Test that olapp can be imported."""
    import olapp
    assert hasattr(olapp, '__version__')
    assert hasattr(olapp, 'Interface')
    assert hasattr(olapp, 'Blocks')


def test_version():
    """Test version is a string."""
    from olapp.version import __version__
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_all_components_importable():
    """Test all components can be imported."""
    from olapp import (
        Component, Textbox, Number, Slider, Checkbox, Dropdown,
        Radio, Button, Image, Audio, Video, File, Dataframe,
        Markdown, HTML, Chatbot, State,
    )
    assert Component is not None
    assert Textbox is not None
    assert Number is not None
    assert Slider is not None
    assert Checkbox is not None
    assert Dropdown is not None
    assert Radio is not None
    assert Button is not None
    assert Image is not None
    assert Audio is not None
    assert Video is not None
    assert File is not None
    assert Dataframe is not None
    assert Markdown is not None
    assert HTML is not None
    assert Chatbot is not None
    assert State is not None


def test_blocks_layout_importable():
    """Test blocks layout components."""
    from olapp import Blocks, Row, Column, Group, Tab, Tabs, Accordion
    assert Blocks is not None
    assert Row is not None
    assert Column is not None
    assert Group is not None
    assert Tab is not None
    assert Tabs is not None
    assert Accordion is not None


def test_server_importable():
    """Test server can be imported."""
    from olapp import OlappServer
    assert OlappServer is not None


def test_utils():
    """Test utility functions."""
    from olapp.utils import generate_id, get_static_dir, get_templates_dir
    
    # generate_id returns unique strings
    ids = {generate_id() for _ in range(100)}
    assert len(ids) == 100  # All unique
    
    # directories exist
    assert get_static_dir().exists()
    assert get_templates_dir().exists()


def test_static_files_exist():
    """Test that static files exist."""
    from olapp.utils import get_static_dir, get_templates_dir
    
    static_dir = get_static_dir()
    assert (static_dir / "olapp.css").exists()
    assert (static_dir / "olapp.js").exists()
    
    templates_dir = get_templates_dir()
    assert (templates_dir / "index.html").exists()


def test_interface_creation():
    """Test creating an Interface."""
    from olapp import Interface
    
    def fn(x):
        return x
    
    app = Interface(fn=fn, inputs="textbox", outputs="textbox")
    config = app.get_config()
    assert config["mode"] == "interface"


def test_blocks_creation():
    """Test creating Blocks."""
    from olapp import Blocks, Textbox, Button
    
    with Blocks(title="Test") as app:
        txt = Textbox(label="Input")
        btn = Button("Go")
    
    config = app.get_config()
    assert config["mode"] == "blocks"


def test_package_structure():
    """Test package directory structure."""
    import olapp
    pkg_dir = os.path.dirname(olapp.__file__)
    
    # Check all required files exist
    assert os.path.isfile(os.path.join(pkg_dir, "__init__.py"))
    assert os.path.isfile(os.path.join(pkg_dir, "components.py"))
    assert os.path.isfile(os.path.join(pkg_dir, "interface.py"))
    assert os.path.isfile(os.path.join(pkg_dir, "blocks.py"))
    assert os.path.isfile(os.path.join(pkg_dir, "server.py"))
    assert os.path.isfile(os.path.join(pkg_dir, "routes.py"))
    assert os.path.isfile(os.path.join(pkg_dir, "utils.py"))
    assert os.path.isfile(os.path.join(pkg_dir, "version.py"))
    assert os.path.isdir(os.path.join(pkg_dir, "static"))
    assert os.path.isdir(os.path.join(pkg_dir, "templates"))


def test_component_config_roundtrip():
    """Test component config can be serialized."""
    import json
    from olapp import Textbox, Slider, Dropdown
    
    comps = [
        Textbox(label="Name", lines=3),
        Slider(0, 100, value=50),
        Dropdown(choices=["a", "b", "c"]),
    ]
    
    for comp in comps:
        config = comp.get_config()
        # Should be JSON serializable
        json_str = json.dumps(config)
        assert isinstance(json_str, str)
        # Should roundtrip
        parsed = json.loads(json_str)
        assert parsed["type"] == comp.type
