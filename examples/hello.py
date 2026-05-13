"""Simple hello world example."""

import olapp


def greet(name: str, excitement: float) -> str:
    """Greet someone with excitement."""
    exclamation = "!" * int(excitement)
    return f"Hello, {name}{exclamation}"


# Simple Interface
app = olapp.Interface(
    fn=greet,
    inputs=[
        olapp.Textbox(label="Your Name", placeholder="Enter your name..."),
        olapp.Slider(minimum=1, maximum=10, value=3, label="Excitement Level"),
    ],
    outputs=olapp.Textbox(label="Greeting"),
    title="👋 Hello Olapp",
    description="A simple greeting app built with Olapp",
)

if __name__ == "__main__":
    app.launch()
