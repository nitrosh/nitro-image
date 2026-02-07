# Nitro Image

Fast, friendly image processing for Python web apps and SaaS.

```python
from nitro_img import Image

Image("photo.jpg").resize(800).webp(quality=80).save("photo.webp")
```

## Install

```bash
pip install nitro-image
```

Optional extras:

```bash
pip install nitro-image[url]   # Load images from URLs (httpx)
pip install nitro-image[avif]  # AVIF format support
pip install nitro-image[blur]  # BlurHash generation
pip install nitro-image[all]   # Everything
```

### Claude Code Skill

Add NitroImage as a skill in [Claude Code](https://claude.ai/code) for AI-assisted image manipulation:

```bash
npx skills add nitrosh/nitro-image
```

## Why nitro-image?

**With Pillow alone:**

```python
from PIL import Image

img = Image.open("photo.jpg")
img = img.convert("RGB")
width, height = img.size
new_height = int(height * (800 / width))
img = img.resize((800, new_height), Image.LANCZOS)
img.save("photo.webp", "WEBP", quality=80)
```

**With nitro-image:**

```python
from nitro_img import Image

Image("photo.jpg").resize(800).webp(quality=80).save("photo.webp")
```

nitro-image wraps Pillow with a chainable API and lazy execution pipeline. Operations queue up and only run when you call an output method like `.save()` or `.to_bytes()`.

## Features

### Resize and crop

```python
Image("photo.jpg").resize(800).save("resized.jpg")
Image("photo.jpg").thumbnail(200).save("thumb.jpg")
Image("photo.jpg").cover(400, 400).save("square.jpg")
Image("photo.jpg").contain(400, 400).save("contained.jpg")
Image("photo.jpg").crop(100, 100, 500, 400).save("cropped.jpg")
```

### Format conversion

```python
Image("photo.jpg").webp(quality=80).save("photo.webp")
Image("photo.jpg").png().save("photo.png")
Image("photo.jpg").jpeg(quality=90).save("photo.jpg")
Image("photo.jpg").auto_format().save("photo.webp")  # picks best format
```

### Adjustments and effects

```python
Image("photo.jpg").brightness(1.2).contrast(1.1).save("enhanced.jpg")
Image("photo.jpg").sharpen(1.5).save("sharp.jpg")
Image("photo.jpg").blur(2.0).save("blurred.jpg")
Image("photo.jpg").grayscale().save("gray.jpg")
Image("photo.jpg").sepia().save("sepia.jpg")
Image("photo.jpg").rounded_corners(20).png().save("rounded.png")
```

### Watermark and text overlay

```python
Image("photo.jpg").watermark("logo.png", position="bottom-right", opacity=0.5).save("watermarked.jpg")
Image("photo.jpg").text_overlay("Sample", font_size=48).save("labeled.jpg")
```

### Responsive images

```python
widths = Image("photo.jpg").responsive([400, 800, 1200, 1600])
# Returns {400: bytes, 800: bytes, 1200: bytes, 1600: bytes}

Image("photo.jpg").save_responsive("output/{width}w.webp", [400, 800, 1200])
# Saves output/400w.webp, output/800w.webp, output/1200w.webp
```

### Placeholders

```python
Image("photo.jpg").lqip()           # Low-quality base64 data URI
Image("photo.jpg").dominant_color()  # "#3a6b8c"
Image("photo.jpg").color_palette(5)  # ["#3a6b8c", "#d4a574", ...]
Image("photo.jpg").svg_placeholder() # SVG with dominant color
Image("photo.jpg").blurhash()        # "LKO2:N%2Tw=w]~RBVZRi..."
```

### Optimization

```python
Image("photo.jpg").optimize(target_kb=200).save("optimized.jpg")
```

### Presets

```python
from nitro_img import Image

Image("photo.jpg").preset.thumbnail()     # 300px thumbnail
Image("photo.jpg").preset.avatar()        # 128px circle crop
Image("photo.jpg").preset.og_image()      # 1200x630 social card
Image("photo.jpg").preset.banner()        # 1920x400 banner

Image.preset.avatar_placeholder("SN")     # Initials avatar image
```

### Batch processing

```python
from nitro_img import BatchImage

BatchImage("photos/*.jpg").resize(800).webp().save("output/{name}.webp")
BatchImage("photos/*.jpg").resize(800).jpeg().save("output/{name}.jpg", parallel=True)
```

### Web framework responses

```python
# Django
return Image("photo.jpg").resize(400).webp().to_django_response()

# Flask
return Image("photo.jpg").resize(400).webp().to_flask_response()

# FastAPI
return Image("photo.jpg").resize(400).webp().to_fastapi_response()
```

### Loading from anywhere

```python
Image("photo.jpg")                          # File path
Image.from_bytes(raw_bytes)                 # Bytes
Image.from_base64(b64_string)              # Base64 string
Image.from_url("https://example.com/img")  # URL (requires httpx)
Image.from_file(file_object)               # File-like object
```

### Output options

```python
img = Image("photo.jpg").resize(400).webp()

img.save("output.webp")      # Save to file
img.to_bytes()                # Get raw bytes
img.to_base64()               # Base64 encoded string
img.to_data_uri()             # data:image/webp;base64,...
img.to_response()             # {"body": bytes, "content_type": str, "content_length": int}
```

## Chain everything

All operations are chainable and lazily evaluated:

```python
(
    Image("photo.jpg")
    .resize(800)
    .brightness(1.1)
    .contrast(1.05)
    .sharpen(1.2)
    .sepia()
    .rounded_corners(10)
    .png(optimize=True)
    .save("final.png")
)
```

## Configuration

```python
from nitro_img import config

config.update(
    jpeg_quality=85,
    webp_quality=80,
    png_optimize=True,
    max_width=4096,
    max_height=4096,
)
```

## Requirements

- Python 3.10+
- Pillow 10.0+

## Ecosystem

- **[nitro-ui](https://github.com/nitrosh/nitro-ui)** - Programmatic HTML generation
- **[nitro-datastore](https://github.com/nitrosh/nitro-datastore)** - Data loading with dot notation access
- **[nitro-dispatch](https://github.com/nitrosh/nitro-dispatch)** - Plugin system
- **[nitro-validate](https://github.com/nitrosh/nitro-validate)** - Data validation
- **[nitro-image](https://github.com/nitrosh/nitro-image)** - Friendly image processing

## License

This project is licensed under the BSD 3-Clause License. See the [LICENSE](LICENSE) file for details.
