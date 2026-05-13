"""Tests for olapp Interface."""

import pytest
from olapp.interface import Interface
from olapp.components import Textbox, Slider, Number, Checkbox, Dropdown


class TestInterface:
    def test_simple_interface(self):
        def greet(name):
            return f"Hello, {name}"
        
        app = Interface(fn=greet, inputs="textbox", outputs="textbox", title="Test")
        assert app.title == "Test"
        assert len(app.input_components) == 1
        assert len(app.output_components) == 1
        assert isinstance(app.input_components[0], Textbox)

    def test_multiple_inputs(self):
        def add(a, b):
            return a + b
        
        app = Interface(fn=add, inputs=["number", "number"], outputs="number")
        assert len(app.input_components) == 2

    def test_component_instances(self):
        def identity(x):
            return x
        
        app = Interface(
            fn=identity,
            inputs=Slider(0, 100, label="Input"),
            outputs=Textbox(label="Output"),
        )
        assert isinstance(app.input_components[0], Slider)
        assert app.input_components[0].minimum == 0
        assert app.input_components[0].maximum == 100

    def test_list_inputs(self):
        def process(a, b, c):
            return f"{a}-{b}-{c}"
        
        app = Interface(
            fn=process,
            inputs=[Textbox(), Number(), Checkbox()],
            outputs="textbox",
        )
        assert len(app.input_components) == 3

    def test_config(self):
        def fn(x):
            return x
        
        app = Interface(fn=fn, inputs="textbox", outputs="textbox", title="My App")
        config = app.get_config()
        assert config["title"] == "My App"
        assert config["mode"] == "interface"
        assert "components" in config
        assert "inputs" in config["components"]
        assert "outputs" in config["components"]

    def test_description(self):
        def fn(x):
            return x
        
        app = Interface(fn=fn, inputs="textbox", outputs="textbox", description="A test app")
        config = app.get_config()
        assert config["description"] == "A test app"

    def test_invalid_fn(self):
        with pytest.raises(TypeError):
            Interface(fn="not a function", inputs="textbox", outputs="textbox")

    def test_empty_inputs(self):
        def fn():
            return "hello"
        
        app = Interface(fn=fn, inputs=[], outputs="textbox")
        assert len(app.input_components) == 0

    def test_empty_outputs(self):
        def fn(x):
            print(x)
        
        app = Interface(fn=fn, inputs="textbox", outputs=[])
        assert len(app.output_components) == 0

    def test_dropdown_interface(self):
        def classify(text, category):
            return f"{text} -> {category}"
        
        app = Interface(
            fn=classify,
            inputs=[
                Textbox(label="Text"),
                Dropdown(choices=["A", "B", "C"], label="Category"),
            ],
            outputs="textbox",
        )
        assert isinstance(app.input_components[1], Dropdown)
        assert app.input_components[1].choices == ["A", "B", "C"]

    def test_component_with_string(self):
        def fn(x):
            return x
        
        app = Interface(fn=fn, inputs="slider", outputs="number")
        from olapp.components import Slider, Number
        assert isinstance(app.input_components[0], Slider)
        assert isinstance(app.output_components[0], Number)
