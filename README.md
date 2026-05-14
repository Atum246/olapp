<p align="center">
  <img src="logo-horizontal.png" alt="olapp" width="400">
</p>

<p align="center">
  <strong>A modern alternative to Gradio. Build ML demos and web apps with Python.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/olapp/"><img src="https://img.shields.io/pypi/v/olapp?style=flat-square" alt="PyPI"></a>
  <a href="https://pypi.org/project/olapp/"><img src="https://img.shields.io/pypi/pyversions/olapp?style=flat-square" alt="Python"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"></a>
  <a href="https://github.com/Atum246/olapp/actions"><img src="https://img.shields.io/badge/tests-114%20passed-brightgreen?style=flat-square" alt="Tests"></a>
</p>

---

<p align="center">
  <img src="screenshot.png" alt="Olapp UI Screenshot" width="100%" style="border-radius: 12px; box-shadow: 0 4px 24px rgba(0,0,0,0.1);">
</p>

## Table of Contents

- [Why Olapp?](#why-olapp)
- [Install](#install)
- [Quick Start](#quick-start)
- [Tutorial: Build a Text Classifier UI](#tutorial-build-a-text-classifier-ui)
- [Tutorial: Build an Image Generator UI](#tutorial-build-an-image-generator-ui)
- [Tutorial: Build a Chatbot UI](#tutorial-build-a-chatbot-ui)
- [Tutorial: Build a Data Dashboard](#tutorial-build-a-data-dashboard)
- [HuggingFace Spaces Deployment](#huggingface-spaces-deployment)
- [Interface API](#interface-api)
- [Blocks API](#blocks-api)
- [All 25 Components](#all-25-components)
- [Color Theme](#color-theme)
- [Layout System](#layout-system)
- [Events & Interactivity](#events--interactivity)
- [Streaming & Real-time](#streaming--real-time)
- [Advanced Usage](#advanced-usage)
- [API Reference](#api-reference)
- [Development](#development)
- [License](#license)

---

## Why Olapp?

- **Clean, professional UI** — not generic AI styling. Looks like a real product.
- **Simple API** — `Interface` for quick demos, `Blocks` for complex layouts
- **25 components** — Textbox, Slider, Image, Chatbot, Code, Gallery, and more
- **Real-time streaming** — SSE-based live updates
- **Dark/light themes** — built-in, no config needed
- **HuggingFace Spaces compatible** — drop in `app.py` and go
- **Mobile responsive** — works on any screen size
- **Production ready** — 114 tests, proper error handling

---

## Install

```bash
pip install olapp
```

Requirements: Python 3.8+, aiohttp

---

## Quick Start

```python
import olapp

def greet(name, excitement):
    return f"Hello, {name}{'!' * int(excitement)}"

app = olapp.Interface(
    fn=greet,
    inputs=[
        olapp.Textbox(label="Name", placeholder="Enter your name"),
        olapp.Slider(minimum=1, maximum=10, value=3, label="Excitement"),
    ],
    outputs=olapp.Textbox(label="Greeting"),
    title="Greeter",
)
app.launch()
```

Open http://127.0.0.1:7860 and you have a working UI.

---

## Tutorial: Build a Text Classifier UI

This tutorial shows how to wrap any NLP model (sentiment analysis, spam detection, etc.) in a web UI.

### Step 1: Your Model Function

```python
import olapp

# Replace this with your actual model
def classify_text(text):
    """Classify text sentiment."""
    # Example: simple keyword-based (replace with your ML model)
    positive_words = ["good", "great", "awesome", "love", "excellent"]
    negative_words = ["bad", "terrible", "hate", "awful", "horrible"]

    text_lower = text.lower()
    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)

    if pos_count > neg_count:
        return {"Positive": 0.85, "Neutral": 0.10, "Negative": 0.05}
    elif neg_count > pos_count:
        return {"Negative": 0.80, "Neutral": 0.15, "Positive": 0.05}
    else:
        return {"Neutral": 0.60, "Positive": 0.20, "Negative": 0.20}
```

### Step 2: Create the Interface

```python
app = olapp.Interface(
    fn=classify_text,
    inputs=olapp.Textbox(
        label="Input Text",
        placeholder="Type something to classify...",
        lines=3,
    ),
    outputs=olapp.Label(label="Prediction", num_top_classes=3),
    title="Text Classifier",
    description="Classify text sentiment using ML",
)
```

### Step 3: Launch

```python
app.launch()  # Opens at http://127.0.0.1:7860
```

### Full Example with Real Model (Transformers)

```python
import olapp
from transformers import pipeline

# Load model once at startup
classifier = pipeline("sentiment-analysis")

def predict(text):
    result = classifier(text)[0]
    return {result["label"]: result["score"]}

app = olapp.Interface(
    fn=predict,
    inputs=olapp.Textbox(label="Text", lines=4, placeholder="Enter text..."),
    outputs=olapp.Label(label="Sentiment"),
    title="Sentiment Analysis",
    description="Powered by HuggingFace Transformers",
)
app.launch()
```

---

## Tutorial: Build an Image Generator UI

Wrap any image generation model (Stable Diffusion, DALL-E, etc.) in a web UI.

### Step 1: Define Your Function

```python
import olapp
from PIL import Image
import numpy as np

def generate_image(prompt, style, seed):
    """Generate an image. Replace with your actual model."""
    # Example: create a gradient image (replace with your model)
    np.random.seed(int(seed))
    width, height = 512, 512
    img = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    return Image.fromarray(img)
```

### Step 2: Build the UI with Blocks

```python
with olapp.Blocks(title="Image Generator") as app:
    olapp.Markdown(value="# Image Generator\nEnter a prompt and generate images.")

    with olapp.Row():
        with olapp.Column():
            prompt = olapp.Textbox(label="Prompt", placeholder="A beautiful sunset...", lines=3)
            style = olapp.Dropdown(
                label="Style",
                choices=["Realistic", "Anime", "Oil Painting", "Watercolor", "Pixel Art"],
                value="Realistic",
            )
            seed = olapp.Number(label="Seed", value=42, minimum=0, maximum=999999)
            btn = olapp.Button("Generate", variant="primary")

        with olapp.Column():
            output = olapp.Image(label="Generated Image")

    btn.click(fn=generate_image, inputs=[prompt, style, seed], outputs=output)
```

### Step 3: Launch

```python
app.launch()
```

### Full Example with Stable Diffusion

```python
import olapp
from diffusers import StableDiffusionPipeline
import torch

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
).to("cuda")

def generate(prompt, steps, guidance):
    image = pipe(
        prompt,
        num_inference_steps=int(steps),
        guidance_scale=guidance,
    ).images[0]
    return image

with olapp.Blocks(title="Stable Diffusion") as app:
    with olapp.Row():
        with olapp.Column():
            prompt = olapp.Textbox(label="Prompt", lines=3)
            steps = olapp.Slider(label="Steps", minimum=1, maximum=100, value=30)
            guidance = olapp.Slider(label="Guidance Scale", minimum=1, maximum=20, value=7.5)
            btn = olapp.Button("Generate")
        with olapp.Column():
            img = olapp.Image(label="Output")

    btn.click(fn=generate, inputs=[prompt, steps, guidance], outputs=img)

app.launch(server_name="0.0.0.0", server_port=7860)
```

---

## Tutorial: Build a Chatbot UI

Create a conversational AI interface.

### Step 1: Define Chat Function

```python
import olapp

def chat(message, history):
    """Process a chat message. Replace with your LLM."""
    # Simple echo bot (replace with your model)
    response = f"You said: {message}"
    history = history + [[message, response]]
    return history
```

### Step 2: Build the UI

```python
with olapp.Blocks(title="Chatbot") as app:
    olapp.Markdown(value="# AI Chatbot\nAsk me anything!")

    chatbot = olapp.Chatbot(label="Conversation", height=400)
    msg = olapp.Textbox(label="Your Message", placeholder="Type here...")

    with olapp.Row():
        send = olapp.Button("Send", variant="primary")
        clear = olapp.Button("Clear", variant="secondary")

    def send_message(message, history):
        if not message:
            return "", history
        response = chat(message, history)
        return "", response

    send.click(fn=send_message, inputs=[msg, chatbot], outputs=[msg, chatbot])
    msg.submit(fn=send_message, inputs=[msg, chatbot], outputs=[msg, chatbot])
    clear.click(fn=lambda: ("", []), outputs=[msg, chatbot])

app.launch()
```

### Full Example with OpenAI

```python
import olapp
from openai import OpenAI

client = OpenAI()

def chat(message, history):
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    for user_msg, bot_msg in history:
        messages.append({"role": "user", "content": user_msg})
        if bot_msg:
            messages.append({"role": "assistant", "content": bot_msg})
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
    )
    reply = response.choices[0].message.content
    return history + [[message, reply]]

with olapp.Blocks(title="AI Chat") as app:
    chatbot = olapp.Chatbot(label="Chat", height=500)
    msg = olapp.Textbox(label="Message", placeholder="Ask anything...")

    with olapp.Row():
        send = olapp.Button("Send", variant="primary")
        clear = olapp.Button("Clear")

    send.click(fn=chat, inputs=[msg, chatbot], outputs=chatbot)
    msg.submit(fn=chat, inputs=[msg, chatbot], outputs=chatbot)
    clear.click(fn=lambda: [], outputs=chatbot)

app.launch()
```

---

## Tutorial: Build a Data Dashboard

Create interactive data exploration tools.

```python
import olapp
import pandas as pd

def analyze_data(file, filter_col, filter_val):
    """Analyze uploaded CSV data."""
    if file is None:
        return None, "No file uploaded"

    df = pd.read_csv(file)

    if filter_col and filter_val:
        df = df[df[filter_col].astype(str).str.contains(filter_val)]

    summary = df.describe().to_html()
    return {"headers": list(df.columns), "data": df.head(20).values.tolist()}, summary

with olapp.Blocks(title="Data Explorer") as app:
    olapp.Markdown(value="# Data Explorer\nUpload a CSV and explore your data.")

    with olapp.Row():
        with olapp.Column():
            file = olapp.File(label="Upload CSV", file_types=[".csv"])
            col = olapp.Textbox(label="Filter Column", placeholder="column_name")
            val = olapp.Textbox(label="Filter Value", placeholder="search term")
            btn = olapp.Button("Analyze", variant="primary")

        with olapp.Column():
            table = olapp.Dataframe(label="Data Preview")
            stats = olapp.HTML(label="Statistics")

    btn.click(fn=analyze_data, inputs=[file, col, val], outputs=[table, stats])

app.launch()
```

---

## HuggingFace Spaces Deployment

Deploy your olapp app to HuggingFace Spaces in 3 steps.

### Step 1: Create Your App

Create `app.py`:

```python
import olapp

def predict(text):
    """Your model function."""
    return text[::-1]  # Example: reverse text

app = olapp.Interface(
    fn=predict,
    inputs=olapp.Textbox(label="Input", placeholder="Enter text..."),
    outputs=olapp.Textbox(label="Output"),
    title="Text Reverser",
    description="A simple text reverser built with olapp",
)

app.launch(server_name="0.0.0.0", server_port=7860)
```

### Step 2: Create requirements.txt

```
olapp
```

Add any other dependencies your model needs:

```
olapp
transformers
torch
```

### Step 3: Create README.md for Spaces

Add this YAML frontmatter to your Spaces README.md:

```yaml
---
title: My Olapp Demo
emoji: 🚀
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
---
```

### Step 4: Push to HuggingFace

```bash
# Install huggingface_hub
pip install huggingface_hub

# Login
huggingface-cli login

# Create space
huggingface-cli space create my-olapp-demo --sdk docker

# Push your files
git add app.py requirements.txt README.md
git commit -m "Initial olapp demo"
git push
```

### Dockerfile for Spaces

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860
CMD ["python", "app.py"]
```

### Example: Deploy a Sentiment Model to Spaces

```python
# app.py
import olapp
from transformers import pipeline

classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def predict(text):
    result = classifier(text)[0]
    return {result["label"]: round(result["score"], 4)}

app = olapp.Interface(
    fn=predict,
    inputs=olapp.Textbox(label="Text", lines=3, placeholder="Enter text to analyze..."),
    outputs=olapp.Label(label="Sentiment", num_top_classes=2),
    title="Sentiment Analysis",
    description="Powered by DistilBERT + olapp",
)

app.launch(server_name="0.0.0.0", server_port=7860)
```

---

## Interface API

The simplest way to create a UI. Just define a function, inputs, and outputs.

```python
import olapp

def my_function(input1, input2):
    return output

app = olapp.Interface(
    fn=my_function,
    inputs=[component1, component2],
    outputs=[component3],
    title="My App",
    description="What this app does",
)
app.launch()
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fn` | Callable | required | The function to wrap |
| `inputs` | Component/str/list | `[]` | Input components |
| `outputs` | Component/str/list | `[]` | Output components |
| `title` | str | `"Olapp"` | App title |
| `description` | str | `""` | App description |
| `theme` | str | `"default"` | Theme name |
| `live` | bool | `False` | Update on every input change |

### String Shorthand

```python
# These are equivalent:
olapp.Interface(fn=f, inputs="textbox", outputs="textbox")
olapp.Interface(fn=f, inputs=olapp.Textbox(), outputs=olapp.Textbox())
```

---

## Blocks API

For complex layouts with rows, columns, tabs, and events.

```python
import olapp

with olapp.Blocks(title="My App") as app:
    # Add components
    text = olapp.Textbox(label="Input")
    output = olapp.Textbox(label="Output")
    btn = olapp.Button("Run")

    # Wire events
    btn.click(fn=lambda x: x.upper(), inputs=text, outputs=output)

app.launch()
```

### Context Managers

```python
with olapp.Blocks() as app:
    with olapp.Row():
        with olapp.Column():
            left = olapp.Textbox(label="Left")
        with olapp.Column():
            right = olapp.Textbox(label="Right")

    with olapp.Group():
        btn = olapp.Button("Submit")

    with olapp.Tabs():
        with olapp.Tab("Tab 1"):
            olapp.Markdown(value="Content 1")
        with olapp.Tab("Tab 2"):
            olapp.Markdown(value="Content 2")
```

---

## All 25 Components

### Input Components

| Component | Key Args | Description |
|-----------|----------|-------------|
| `Textbox` | `label`, `placeholder`, `lines`, `value` | Single/multi-line text |
| `Number` | `label`, `value`, `minimum`, `maximum`, `step` | Numeric input |
| `Slider` | `label`, `minimum`, `maximum`, `value`, `step` | Range slider |
| `Checkbox` | `label`, `value` | Boolean toggle |
| `Dropdown` | `label`, `choices`, `value`, `multiselect` | Selection dropdown |
| `Radio` | `label`, `choices`, `value` | Radio buttons |
| `Button` | `label`, `variant` (`primary`/`secondary`) | Click button |
| `Image` | `label`, `value` | Image upload/display |
| `Audio` | `label`, `value` | Audio upload/playback |
| `Video` | `label`, `value` | Video upload/playback |
| `File` | `label`, `file_types` | File upload |
| `ColorPicker` | `label`, `value` | Color picker |
| `DateTime` | `label`, `include_time` | Date/time picker |
| `Code` | `label`, `language`, `lines` | Code editor |

### Output Components

| Component | Key Args | Description |
|-----------|----------|-------------|
| `Textbox` | (same as input) | Text display |
| `Image` | (same as input) | Image display |
| `Dataframe` | `label`, `headers`, `value` | Table display |
| `Markdown` | `value` | Markdown renderer |
| `HTML` | `value` | Raw HTML |
| `Chatbot` | `label`, `value`, `height` | Chat interface |
| `Label` | `label`, `num_top_classes` | Classification labels |
| `HighlightedText` | `label`, `value` | Text with highlights |
| `JSON` | `label`, `value` | JSON viewer |
| `Gallery` | `label`, `columns`, `value` | Image grid |
| `Progress` | `label`, `value` | Progress bar |

### Utility Components

| Component | Description |
|-----------|-------------|
| `State` | Hidden state between interactions |

---

## Color Theme

Olapp uses a clean, professional palette:

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| Primary | `#6366f1` | `#818cf8` | Buttons, links, accents |
| Success | `#059669` | `#059669` | Success states |
| Warning | `#d97706` | `#d97706` | Warning states |
| Error | `#dc2626` | `#dc2626` | Error states |
| Background | `#ffffff` | `#030712` | Page background |
| Surface | `#ffffff` | `#111827` | Card backgrounds |
| Border | `#e5e7eb` | `#1f2937` | Borders and dividers |
| Text | `#111827` | `#f9fafb` | Primary text |
| Text Secondary | `#4b5563` | `#9ca3af` | Secondary text |

---

## Layout System

### Row

Side-by-side layout:

```python
with olapp.Row():
    left = olapp.Textbox(label="Left")
    right = olapp.Textbox(label="Right")
```

### Column

Vertical layout with scaling:

```python
with olapp.Column(scale=2):  # Takes 2x space
    big = olapp.Textbox(label="Big")
with olapp.Column(scale=1):  # Takes 1x space
    small = olapp.Textbox(label="Small")
```

### Group

Bordered container:

```python
with olapp.Group():
    olapp.Textbox(label="Inside group")
    olapp.Button("Also inside")
```

### Tabs

Tabbed interface:

```python
with olapp.Tabs():
    with olapp.Tab("Tab 1"):
        olapp.Markdown(value="Content 1")
    with olapp.Tab("Tab 2"):
        olapp.Markdown(value="Content 2")
```

### Accordion

Collapsible sections:

```python
with olapp.Accordion(label="Advanced Settings", open=False):
    olapp.Slider(label="Threshold", minimum=0, maximum=1, value=0.5)
    olapp.Checkbox(label="Enable caching")
```

---

## Events & Interactivity

### Click

Trigger on button click:

```python
btn.click(fn=my_function, inputs=[input1, input2], outputs=output)
```

### Change

Trigger on value change:

```python
slider.change(fn=update_preview, inputs=slider, outputs=preview)
```

### Submit

Trigger on form submit (Enter key):

```python
textbox.submit(fn=process, inputs=textbox, outputs=result)
```

### Chaining Events

```python
with olapp.Blocks() as app:
    inp = olapp.Textbox(label="Input")
    step1 = olapp.Textbox(label="Step 1")
    step2 = olapp.Textbox(label="Step 2")
    out = olapp.Textbox(label="Output")

    inp.submit(fn=preprocess, inputs=inp, outputs=step1)
    step1.submit(fn=transform, inputs=step1, outputs=step2)
    step2.submit(fn=postprocess, inputs=step2, outputs=out)
```

---

## Streaming & Real-time

For long-running operations, use streaming:

```python
import olapp
import time

def slow_function(text):
    """Simulate a slow process."""
    result = ""
    for char in text:
        result += char
        time.sleep(0.1)
    return result

app = olapp.Interface(
    fn=slow_function,
    inputs=olapp.Textbox(label="Input"),
    outputs=olapp.Textbox(label="Output"),
    title="Streaming Demo",
)
app.launch()
```

---

## Advanced Usage

### Custom CSS

```python
app = olapp.Interface(
    fn=my_fn,
    inputs="textbox",
    outputs="textbox",
    css="""
    .olapp-card { border-radius: 16px; }
    .olapp-btn-primary { background: #10b981; }
    """,
)
```

### Pre/Post Processing

Components can preprocess inputs and postprocess outputs:

```python
class MyTextbox(olapp.Textbox):
    def preprocess(self, x):
        return x.strip().lower()  # Clean input

    def postprocess(self, y):
        return y.upper()  # Format output
```

### Multiple Outputs

```python
def analyze(text):
    return text.upper(), len(text), text.split()

app = olapp.Interface(
    fn=analyze,
    inputs=olapp.Textbox(label="Input"),
    outputs=[
        olapp.Textbox(label="Uppercase"),
        olapp.Number(label="Length"),
        olapp.JSON(label="Words"),
    ],
)
```

### Launch Options

```python
app.launch(
    server_name="0.0.0.0",  # Listen on all interfaces
    server_port=8080,        # Custom port
    prevent_thread_lock=True, # Non-blocking (for notebooks)
)
```

---

## API Reference

### Endpoints

Every olapp app exposes these HTTP endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Web UI |
| `GET` | `/api/config` | App configuration |
| `POST` | `/api/predict` | Run prediction |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/queue/join` | SSE stream |

### Predict API

```bash
curl -X POST http://localhost:7860/api/predict \
  -H "Content-Type: application/json" \
  -d '{"data": ["Hello", 5]}'
```

Response:
```json
{"data": ["Hello!!!!!"]}
```

---

## Development

```bash
git clone https://github.com/Atum246/olapp.git
cd olapp
pip install -e ".[dev]"
python -m pytest tests/ -v
```

### Project Structure

```
olapp/
├── olapp/
│   ├── __init__.py       # Package exports
│   ├── components.py     # 25 UI components
│   ├── interface.py      # Simple Interface API
│   ├── blocks.py         # Flexible Blocks API
│   ├── server.py         # aiohttp web server
│   ├── routes.py         # API route handlers
│   ├── utils.py          # Utilities
│   ├── static/
│   │   ├── olapp.css     # Styles
│   │   └── olapp.js      # Frontend logic
│   └── templates/
│       └── index.html    # HTML template
├── tests/                # 114 tests
├── examples/             # Example apps
├── app.py                # HuggingFace Spaces demo
└── pyproject.toml        # Package config
```

---

## License

MIT — see [LICENSE](LICENSE).
