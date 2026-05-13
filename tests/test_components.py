"""Tests for olapp components."""

import pytest
from olapp.components import (
    Component, Textbox, Number, Slider, Checkbox, Dropdown, Radio,
    Button, Image, Audio, Video, File, Dataframe, Markdown, HTML,
    Chatbot, State, get_component_class, COMPONENT_MAP,
)


class TestComponent:
    def test_base_component(self):
        comp = Component(label="Test", value="hello")
        assert comp.label == "Test"
        assert comp.value == "hello"
        assert comp.visible is True
        assert comp.interactive is True
        assert comp.elem_id is not None

    def test_component_config(self):
        comp = Component(label="Test", value="hello")
        config = comp.get_config()
        assert config["label"] == "Test"
        assert config["value"] == "hello"
        assert config["type"] == "component"
        assert config["visible"] is True

    def test_component_value_setter(self):
        comp = Component(label="Test", value="initial")
        comp.value = "updated"
        assert comp.value == "updated"

    def test_component_repr(self):
        comp = Component(label="Test")
        assert "Component" in repr(comp)
        assert "Test" in repr(comp)


class TestTextbox:
    def test_defaults(self):
        tb = Textbox()
        assert tb.label == "Textbox"
        assert tb.value == ""
        assert tb.lines == 1

    def test_multiline(self):
        tb = Textbox(lines=5, max_lines=20)
        assert tb.lines == 5
        assert tb.max_lines == 20

    def test_placeholder(self):
        tb = Textbox(placeholder="Enter text...")
        assert tb.placeholder == "Enter text..."

    def test_config(self):
        tb = Textbox(label="Name", lines=3, placeholder="Enter name")
        config = tb.get_config()
        assert config["type"] == "textbox"
        assert config["lines"] == 3
        assert config["placeholder"] == "Enter name"

    def test_preprocess(self):
        tb = Textbox()
        assert tb.preprocess("hello") == "hello"
        assert tb.preprocess(None) == ""
        assert tb.preprocess(42) == "42"

    def test_postprocess(self):
        tb = Textbox()
        assert tb.postprocess("hello") == "hello"
        assert tb.postprocess(None) == ""


class TestNumber:
    def test_defaults(self):
        n = Number()
        assert n.label == "Number"
        assert n.step == 1

    def test_with_bounds(self):
        n = Number(minimum=0, maximum=100, step=5)
        assert n.minimum == 0
        assert n.maximum == 100
        assert n.step == 5

    def test_preprocess_valid(self):
        n = Number(minimum=0, maximum=100)
        assert n.preprocess("50") == 50.0
        assert n.preprocess("3.14") == 3.14

    def test_preprocess_bounds(self):
        n = Number(minimum=0, maximum=10)
        assert n.preprocess("15") == 10
        assert n.preprocess("-5") == 0

    def test_preprocess_none(self):
        n = Number()
        assert n.preprocess(None) is None
        assert n.preprocess("") is None

    def test_preprocess_invalid(self):
        n = Number()
        assert n.preprocess("abc") is None

    def test_precision(self):
        n = Number(precision=2)
        assert n.preprocess("3.14159") == 3.14


class TestSlider:
    def test_defaults(self):
        s = Slider()
        assert s.minimum == 0
        assert s.maximum == 100
        assert s.step == 1

    def test_custom_range(self):
        s = Slider(minimum=-10, maximum=10, step=0.5, value=5)
        assert s.minimum == -10
        assert s.maximum == 10
        assert s.value == 5

    def test_default_value(self):
        s = Slider(minimum=0, maximum=10)
        assert s.value == 0

    def test_preprocess(self):
        s = Slider()
        assert s.preprocess("50") == 50.0
        assert s.preprocess(None) == 0


class TestCheckbox:
    def test_defaults(self):
        cb = Checkbox()
        assert cb.value is False

    def test_checked(self):
        cb = Checkbox(value=True)
        assert cb.value is True

    def test_preprocess_string(self):
        cb = Checkbox()
        assert cb.preprocess("true") is True
        assert cb.preprocess("false") is False
        assert cb.preprocess("1") is True
        assert cb.preprocess("0") is False

    def test_preprocess_bool(self):
        cb = Checkbox()
        assert cb.preprocess(True) is True
        assert cb.preprocess(False) is False


class TestDropdown:
    def test_defaults(self):
        dd = Dropdown(choices=["a", "b", "c"])
        assert dd.choices == ["a", "b", "c"]
        assert dd.value == "a"

    def test_custom_value(self):
        dd = Dropdown(choices=["a", "b", "c"], value="b")
        assert dd.value == "b"

    def test_empty_choices(self):
        dd = Dropdown()
        assert dd.choices == []

    def test_config(self):
        dd = Dropdown(choices=["x", "y"], label="Pick")
        config = dd.get_config()
        assert config["choices"] == ["x", "y"]
        assert config["multiselect"] is False

    def test_multiselect(self):
        dd = Dropdown(choices=["a", "b", "c"], multiselect=True)
        assert dd.multiselect is True
        assert dd.value == []

    def test_preprocess_multiselect(self):
        dd = Dropdown(choices=["a", "b"], multiselect=True)
        assert dd.preprocess("a") == ["a"]
        assert dd.preprocess(["a", "b"]) == ["a", "b"]


class TestRadio:
    def test_defaults(self):
        r = Radio(choices=["a", "b", "c"])
        assert r.choices == ["a", "b", "c"]
        assert r.value == "a"

    def test_custom_value(self):
        r = Radio(choices=["a", "b", "c"], value="c")
        assert r.value == "c"


class TestButton:
    def test_defaults(self):
        btn = Button()
        assert btn.label == "Submit"
        assert btn.variant == "primary"

    def test_custom(self):
        btn = Button(label="Click Me", variant="secondary")
        assert btn.label == "Click Me"
        assert btn.variant == "secondary"


class TestImage:
    def test_defaults(self):
        img = Image()
        assert img.label == "Image"
        assert img.sources == ["upload", "clipboard"]

    def test_postprocess_none(self):
        img = Image()
        assert img.postprocess(None) is None


class TestAudio:
    def test_defaults(self):
        audio = Audio()
        assert audio.label == "Audio"
        assert audio.sources == ["upload", "microphone"]

    def test_postprocess_none(self):
        audio = Audio()
        assert audio.postprocess(None) is None


class TestVideo:
    def test_defaults(self):
        video = Video()
        assert video.label == "Video"
        assert video.sources == ["upload"]


class TestFile:
    def test_defaults(self):
        f = File()
        assert f.label == "File"
        assert f.file_count == "single"


class TestDataframe:
    def test_defaults(self):
        df = Dataframe()
        assert df.label == "Dataframe"

    def test_postprocess_dict(self):
        df = Dataframe()
        result = df.postprocess({"headers": ["A", "B"], "data": [[1, 2]]})
        assert result["headers"] == ["A", "B"]
        assert result["data"] == [[1, 2]]

    def test_postprocess_list(self):
        df = Dataframe()
        result = df.postprocess([[1, 2], [3, 4]])
        assert result["data"] == [[1, 2], [3, 4]]

    def test_postprocess_none(self):
        df = Dataframe()
        result = df.postprocess(None)
        assert result == {"headers": [], "data": []}


class TestMarkdown:
    def test_postprocess(self):
        md = Markdown()
        assert md.postprocess("# Hello") == "# Hello"
        assert md.postprocess(None) == ""


class TestHTML:
    def test_postprocess(self):
        html = HTML()
        assert html.postprocess("<b>bold</b>") == "<b>bold</b>"
        assert html.postprocess(None) == ""


class TestChatbot:
    def test_defaults(self):
        cb = Chatbot()
        assert cb.label == "Chatbot"
        assert cb.value == []

    def test_postprocess_messages(self):
        cb = Chatbot()
        result = cb.postprocess([["hello", "hi"], ["bye", "goodbye"]])
        assert len(result) == 2
        assert result[0] == ["hello", "hi"]

    def test_postprocess_none(self):
        cb = Chatbot()
        assert cb.postprocess(None) == []

    def test_postprocess_dict_messages(self):
        cb = Chatbot()
        result = cb.postprocess([{"user": "hello", "bot": "hi"}])
        assert result[0] == ["hello", "hi"]


class TestState:
    def test_defaults(self):
        s = State(value={"key": "val"})
        assert s.value == {"key": "val"}
        assert s.visible is False

    def test_config(self):
        s = State(value=42)
        config = s.get_config()
        assert config["visible"] is False


class TestGetComponentClass:
    def test_valid_names(self):
        for name in COMPONENT_MAP:
            cls = get_component_class(name)
            assert cls is COMPONENT_MAP[name]

    def test_invalid_name(self):
        with pytest.raises(ValueError):
            get_component_class("nonexistent")

    def test_case_insensitive(self):
        cls = get_component_class("Textbox")
        assert cls is Textbox
        cls = get_component_class("TEXTBOX")
        assert cls is Textbox
