"""HuggingFace Spaces demo for olapp."""

import olapp


def greet(name: str, enthusiasm: float) -> str:
    """Simple greeting function."""
    return f"Hello, {name}{'!' * int(enthusiasm)}"


def reverse_text(text: str) -> str:
    """Reverse the input text."""
    return text[::-1]


def upper_lower(text: str, mode: str) -> str:
    """Convert text to upper or lower case."""
    if mode == "UPPER":
        return text.upper()
    return text.lower()


# Create a multi-function demo
with olapp.Blocks(title="⚡ Olapp Demo", theme="default") as demo:
    olapp.Markdown("""
# ⚡ Welcome to Olapp!
A modern alternative to Gradio with stunning UI.
    """)

    with olapp.Tabs():
        with olapp.Tab("Greeter"):
            with olapp.Row():
                with olapp.Column():
                    name_input = olapp.Textbox(label="Your Name", placeholder="Enter your name...")
                    enthusiasm = olapp.Slider(1, 10, value=5, label="Enthusiasm Level")
                    greet_btn = olapp.Button("Greet Me! 👋", variant="primary")
                with olapp.Column():
                    greet_output = olapp.Textbox(label="Greeting", interactive=False)
            demo.click(fn=greet, inputs=[name_input, enthusiasm], outputs=greet_output)

        with olapp.Tab("Text Tools"):
            with olapp.Row():
                with olapp.Column():
                    text_input = olapp.Textbox(label="Input Text", lines=3, placeholder="Type something...")
                    mode = olapp.Dropdown(choices=["UPPER", "lower"], label="Mode", value="UPPER")
                    tool_btn = olapp.Button("Transform! ✨", variant="primary")
                with olapp.Column():
                    tool_output = olapp.Textbox(label="Result", lines=3, interactive=False)
            demo.click(fn=upper_lower, inputs=[text_input, mode], outputs=tool_output)

        with olapp.Tab("Reverser"):
            with olapp.Row():
                with olapp.Column():
                    rev_input = olapp.Textbox(label="Text to Reverse", placeholder="Enter text...")
                    rev_btn = olapp.Button("Reverse! 🔄", variant="primary")
                with olapp.Column():
                    rev_output = olapp.Textbox(label="Reversed", interactive=False)
            demo.click(fn=reverse_text, inputs=rev_input, outputs=rev_output)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
