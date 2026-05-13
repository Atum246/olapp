"""Image processing example."""

import olapp


def process_image(image_data):
    """Simple image processing — returns the image info."""
    if image_data is None:
        return "No image provided"
    # Just pass through for demo
    return image_data


def create_thumbnail_info(image_data):
    """Get info about an uploaded image."""
    if image_data is None:
        return "No image uploaded yet. Upload an image to see it here!"
    return f"✅ Image received! (Base64 data length: {len(str(image_data))} chars)"


with olapp.Blocks(title="🖼️ Image Demo") as demo:
    olapp.Markdown("## 🖼️ Image Upload Demo\nUpload an image and see the preview!")

    with olapp.Row():
        with olapp.Column():
            img_input = olapp.Image(label="Upload Image", sources=["upload", "clipboard"])
            process_btn = olapp.Button("Process Image ⚡", variant="primary")
        with olapp.Column():
            img_output = olapp.Image(label="Output Image")
            info_output = olapp.Textbox(label="Image Info", interactive=False)

    demo.click(fn=process_image, inputs=img_input, outputs=img_output)
    demo.change(fn=create_thumbnail_info, inputs=img_input, outputs=info_output)


if __name__ == "__main__":
    demo.launch()
