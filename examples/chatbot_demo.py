"""Chatbot example with state."""

import olapp
import random


RESPONSES = [
    "That's interesting! Tell me more.",
    "I understand. How does that make you feel?",
    "Great point! What else?",
    "Hmm, let me think about that...",
    "I appreciate you sharing that!",
    "Can you elaborate on that?",
    "That's a wonderful perspective!",
    "I see what you mean. Go on...",
]


def chat_respond(message: str, history: list) -> tuple:
    """Simple chatbot that echoes with varied responses."""
    if not message.strip():
        return "", history

    # Simple response logic
    msg_lower = message.lower()
    if "hello" in msg_lower or "hi" in msg_lower:
        response = "Hey there! 👋 How can I help you today?"
    elif "bye" in msg_lower:
        response = "Goodbye! Have a great day! 👋"
    elif "help" in msg_lower:
        response = "I'm a simple demo chatbot. Just type anything and I'll respond!"
    elif "olapp" in msg_lower:
        response = "⚡ Olapp is a modern alternative to Gradio! Built with love."
    elif "?" in message:
        response = "That's a great question! Unfortunately, I'm just a demo bot. 😅"
    else:
        response = random.choice(RESPONSES)

    history = history + [[message, response]]
    return "", history


with olapp.Blocks(title="🤖 Chatbot Demo") as demo:
    olapp.Markdown("## 🤖 Olapp Chatbot\nA simple chatbot demo with Olapp's Chatbot component.")

    chatbot = olapp.Chatbot(label="Chat", height=400, placeholder="Type a message...")
    msg_input = olapp.Textbox(label="Your Message", placeholder="Say something...", lines=1)
    with olapp.Row():
        send_btn = olapp.Button("Send 💬", variant="primary")
        clear_btn = olapp.Button("Clear 🗑️", variant="secondary")

    demo.submit(fn=chat_respond, inputs=[msg_input, chatbot], outputs=[msg_input, chatbot])
    demo.click(fn=chat_respond, inputs=[msg_input, chatbot], outputs=[msg_input, chatbot])


if __name__ == "__main__":
    demo.launch()
