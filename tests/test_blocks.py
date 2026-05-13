"""Tests for olapp Blocks."""

import pytest
from olapp.blocks import Blocks, Row, Column, Group, Tab, Tabs, Accordion
from olapp.components import Textbox, Slider, Button, Number, Checkbox, Markdown


class TestBlocks:
    def test_create_blocks(self):
        with Blocks(title="Test App") as app:
            txt = Textbox(label="Input")
            assert isinstance(txt, Textbox)

    def test_row_context(self):
        with Blocks() as app:
            with app.row():
                t1 = Textbox(label="A")
                t2 = Textbox(label="B")
        assert len(app.blocks) == 1
        assert isinstance(app.blocks[0], Row)
        assert len(app.blocks[0].children) == 2

    def test_column_context(self):
        with Blocks() as app:
            with app.column():
                t1 = Textbox(label="A")
                t2 = Textbox(label="B")
        assert len(app.blocks) == 1
        assert isinstance(app.blocks[0], Column)

    def test_nested_layout(self):
        with Blocks() as app:
            with app.row():
                with app.column():
                    Textbox(label="Left")
                with app.column():
                    Textbox(label="Right")
        row = app.blocks[0]
        assert isinstance(row, Row)
        assert len(row.children) == 2
        assert isinstance(row.children[0], Column)
        assert isinstance(row.children[1], Column)

    def test_click_handler(self):
        with Blocks() as app:
            btn = Button("Click")
            output = Textbox(label="Output")
            app.click(fn=lambda: "clicked!", inputs=[], outputs=output)

        assert len(app.dependencies) == 1
        assert app.dependencies[0]["trigger"] == "click"

    def test_change_handler(self):
        with Blocks() as app:
            inp = Textbox(label="Input")
            out = Textbox(label="Output")
            app.change(fn=lambda x: x.upper(), inputs=inp, outputs=out)

        assert len(app.dependencies) == 1
        assert app.dependencies[0]["trigger"] == "change"

    def test_submit_handler(self):
        with Blocks() as app:
            inp = Textbox(label="Input")
            out = Textbox(label="Output")
            app.submit(fn=lambda x: x, inputs=inp, outputs=out)

        assert len(app.dependencies) == 1
        assert app.dependencies[0]["trigger"] == "submit"

    def test_config(self):
        with Blocks(title="Config Test") as app:
            with app.row():
                Textbox(label="A")
                Textbox(label="B")
            btn = Button("Go")
            out = Textbox(label="Out")
            app.click(fn=lambda a, b: a + b, inputs=[], outputs=out)

        config = app.get_config()
        assert config["title"] == "Config Test"
        assert config["mode"] == "blocks"
        assert "layout" in config
        assert "dependencies" in config

    def test_get_all_components(self):
        with Blocks() as app:
            with app.row():
                t1 = Textbox(label="A")
                t2 = Textbox(label="B")
            t3 = Textbox(label="C")
        
        components = app.get_all_components()
        assert len(components) == 3

    def test_get_component_by_id(self):
        with Blocks() as app:
            t1 = Textbox(label="Find Me")
            target_id = t1.elem_id
        
        found = app.get_component_by_id(target_id)
        assert found is t1

    def test_group_context(self):
        with Blocks() as app:
            with app.group():
                Textbox(label="A")
                Textbox(label="B")
        assert isinstance(app.blocks[0], Group)


class TestRow:
    def test_create(self):
        row = Row()
        assert row.children == []

    def test_add_child(self):
        row = Row()
        t = Textbox(label="Test")
        row.add(t)
        assert len(row.children) == 1

    def test_layout(self):
        row = Row()
        row.add(Textbox(label="A"))
        layout = row.get_layout()
        assert layout["type"] == "row"
        assert len(layout["children"]) == 1


class TestColumn:
    def test_create(self):
        col = Column(scale=2)
        assert col.scale == 2

    def test_layout(self):
        col = Column(scale=3)
        layout = col.get_layout()
        assert layout["scale"] == 3


class TestTab:
    def test_create(self):
        tab = Tab(label="My Tab")
        assert tab.label == "My Tab"

    def test_layout(self):
        tab = Tab(label="Tab 1")
        layout = tab.get_layout()
        assert layout["label"] == "Tab 1"


class TestTabs:
    def test_add_tab(self):
        tabs = Tabs()
        tab = Tab(label="Tab 1")
        tabs.add_tab(tab)
        assert len(tabs.children) == 1


class TestAccordion:
    def test_create(self):
        acc = Accordion(label="Settings", open=True)
        assert acc.label == "Settings"
        assert acc.is_open is True

    def test_layout(self):
        acc = Accordion(label="More", open=False)
        layout = acc.get_layout()
        assert layout["label"] == "More"
        assert layout["open"] is False
