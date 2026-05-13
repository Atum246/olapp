# ⚡ Olapp — A Modern Alternative to Gradio

<p align="center">
<strong>Build beautiful ML demos and web apps with Python — in minutes, not hours.</strong>
</p>

<p align="center">
<a href="https://pypi.org/project/olapp/"><img src="https://img.shields.io/pypi/v/olapp?color=7c3aed&style=flat-square" alt="PyPI"></a>
<a href="https://pypi.org/project/olapp/"><img src="https://img.shields.io/pypi/pyversions/olapp?color=7c3aed&style=flat-square" alt="Python"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-7c3aed?style=flat-square" alt="License"></a>
</p>

---

## ✨ Why Olapp?

- **🎨 Stunning UI** — Premium SaaS-quality design with glassmorphism, smooth animations, dark/light mode
- **⚡ Lightning Fast** — Built on aiohttp with SSE real-time streaming
- **🧩 Simple API** — Familiar Interface & Blocks API, just like Gradio but better
- **📱 Responsive** — Works beautifully on desktop and mobile
- **🔧 Full Component Suite** — Textbox, Slider, Image, Chatbot, Dataframe, and more

## 🚀 Quick Start

### Installation

```bash
pip install olapp
```

### Simple Interface

```python
import olapp

def greet(name, enthusiasm):
    return f"Hello, {name}{'!' * int(enthusiasm)}"

app = olapp.Interface(
    fn=greet,
    inputs=["textbox", olapp.Slider(1, 10, label="Enthusiasm")],
    outputs="textbox",
    title="👋 Greeter",
)
app.launch()
```

### Blocks API

```python
import olapp

with olapp.Blocks(title="My App") as app:
    with olapp.Row():
        inp = olapp.Textbox(label="Input")
        out = olapp.Textbox(label="Output")
    btn = olapp.Button("Run", variant="primary")
    app.click(fn=lambda x: x.upper(), inputs=inp, outputs=out)

app.launch()
```

## 📦 Components

| Component | Description |
|-----------|-------------|
| `Textbox` | Text input (single/multi line) |
| `Number` | Numeric input with +/- buttons |
| `Slider` | Range slider |
| `Checkbox` | Boolean toggle |
| `Dropdown` | Selection dropdown |
| `Radio` | Radio button group |
| `Button` | Clickable button |
| `Image` | Image upload/display |
| `Audio` | Audio upload/playback |
| `Video` | Video upload/playback |
| `File` | File upload |
| `Dataframe` | Tabular data |
| `Markdown` | Markdown renderer |
| `HTML` | Raw HTML display |
| `Chatbot` | Chat interface |
| `State` | Hidden state storage |

## 🎨 UI Features

- **Dark mode** by default with light mode toggle
- **Glassmorphism** cards with backdrop blur
- **Smooth 60fps** animations and transitions
- **Responsive** design for all screen sizes
- **Toast notifications** for errors
- **Gradient branding** with deep purple (#7c3aed) primary

## 🤖 HuggingFace Spaces

Create an `app.py` at the root:

```python
import olapp

def predict(text):
    return text[::-1]

app = olapp.Interface(fn=predict, inputs="textbox", outputs="textbox", title="🔄 Reverser")
app.launch(server_name="0.0.0.0", server_port=7860)
```

Add `requirements.txt`:
```
olapp
```

## 📄 License

MIT License — see [LICENSE](LICENSE).
