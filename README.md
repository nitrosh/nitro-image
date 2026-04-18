# Nitro Image

Fast, friendly image processing for Python web apps and SaaS. Nitro Image wraps [Pillow](https://pillow.readthedocs.io/) with a chainable, lazy-evaluated pipeline so you can resize, convert, optimize, and generate responsive image sets with one fluent call.

[![PyPI](https://img.shields.io/pypi/v/nitro-image?color=green)](https://pypi.org/project/nitro-image/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nitro-image)](https://pypi.org/project/nitro-image/)
[![PyPI - License](https://img.shields.io/pypi/l/nitro-image)](https://pypi.org/project/nitro-image/)
[![image](https://img.shields.io/github/actions/workflow/status/nitrosh/nitro-image/test.yml?branch=main)](https://github.com/nitrosh/nitro-image/actions?query=branch%3Amain)

## Installation

```bash
pip install nitro-image
```

Optional extras:

```bash
pip install nitro-image[url]   # Load images from URLs (httpx)
pip install nitro-image[avif]  # AVIF format support
pip install nitro-image[blur]  # BlurHash generation
pip install nitro-image[all]   # Everything above
```

## Quickstart

```python
from nitro_img import Image

Image("photo.jpg").resize(800).webp(quality=80).save("photo.webp")
```

## Features

- **Chainable API** - Fluent, readable pipelines instead of verbose PIL boilerplate
- **Lazy Execution** - Operations queue up and only run on output (`.save()`, `.to_bytes()`, etc.)
- **Format Conversion** - JPEG, PNG, WebP, GIF, and optional AVIF
- **Smart Resizing** - `resize`, `thumbnail`, `cover`, `contain` with upscale control
- **Responsive Sets** - Generate multiple widths for `srcset` in one call
- **Placeholders** - LQIP data URIs, dominant colors, palettes, SVG, and BlurHash
- **Overlays** - Watermarks and text with position, opacity, and scale control
- **Batch Processing** - Glob-based batch with optional thread parallelism
- **Framework Integrations** - One-line response helpers for Django, Flask, and FastAPI
- **Presets** - Opinionated one-call helpers for thumbnails, avatars, OG images, and banners
- **Optimization** - Target-size encoding with automatic quality tuning

### AI Assistant Integration

Add Nitro Image knowledge to your AI coding assistant:

```bash
npx skills add nitrosh/nitro-image
```

This enables AI assistants like Claude Code to understand Nitro Image and generate correct `nitro_img` code.

## Why Nitro Image?

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

**With Nitro Image:**

```python
from nitro_img import Image

Image("photo.jpg").resize(800).webp(quality=80).save("photo.webp")
```

Operations queue up and only run when you call an output method like `.save()` or `.to_bytes()`, so a long chain still touches the pixels once.

## Resize and crop

```python
Image("photo.jpg").resize(800).save("resized.jpg")
Image("photo.jpg").thumbnail(200, 200).save("thumb.jpg")
Image("photo.jpg").cover(400, 400).save("square.jpg")
Image("photo.jpg").contain(400, 400).save("contained.jpg")
Image("photo.jpg").crop(500, 400, anchor="center").save("cropped.jpg")
```

## Format conversion

```python
Image("photo.jpg").webp(quality=80).save("photo.webp")
Image("photo.jpg").png().save("photo.png")
Image("photo.jpg").jpeg(quality=90).save("photo.jpg")
Image("photo.jpg").auto_format().save("photo.webp")  # picks best format
```

## Adjustments and effects

```python
Image("photo.jpg").brightness(1.2).contrast(1.1).save("enhanced.jpg")
Image("photo.jpg").sharpen(1.5).save("sharp.jpg")
Image("photo.jpg").blur(2.0).save("blurred.jpg")
Image("photo.jpg").grayscale().save("gray.jpg")
Image("photo.jpg").sepia().save("sepia.jpg")
Image("photo.jpg").rounded_corners(20).png().save("rounded.png")
```

## Watermarks and text overlays

```python
Image("photo.jpg").watermark("logo.png", position="bottom-right", opacity=0.5).save("watermarked.jpg")
Image("photo.jpg").text_overlay("Sample", font_size=48).save("labeled.jpg")
```

## Responsive images

```python
widths = Image("photo.jpg").responsive([400, 800, 1200, 1600])
# Returns {400: bytes, 800: bytes, 1200: bytes, 1600: bytes}

Image("photo.jpg").webp().save_responsive("output/", [400, 800, 1200], name="hero")
# Saves output/hero_400.webp, output/hero_800.webp, output/hero_1200.webp
```

## Placeholders

```python
Image("photo.jpg").lqip()            # Low-quality base64 data URI
Image("photo.jpg").dominant_color()  # "#3a6b8c"
Image("photo.jpg").color_palette(5)  # ["#3a6b8c", "#d4a574", ...]
Image("photo.jpg").svg_placeholder() # SVG with dominant color
Image("photo.jpg").blurhash()        # "LKO2:N%2Tw=w]~RBVZRi..."
```

## Optimization

```python
Image("photo.jpg").optimize(target_kb=200)
# Returns the encoded bytes, auto-tuning quality to hit the target size
```

## Presets

Presets are opinionated one-call helpers. They take a source (path, bytes, or file-like) and return encoded bytes.

```python
from nitro_img import presets, Image

presets.thumbnail("photo.jpg")                 # 200x200 WebP
presets.avatar("photo.jpg", size=128)          # 128px circle-cropped PNG
presets.og_image("photo.jpg")                  # 1200x630 JPEG social card
presets.banner("photo.jpg")                    # 1920x400 JPEG banner
presets.avatar_placeholder("SN")               # Initials avatar

# Presets are also available via Image.preset for convenience:
Image.preset.thumbnail("photo.jpg")
```

## Batch processing

```python
from nitro_img import BatchImage

BatchImage("photos/*.jpg").resize(800).webp().save("output/{name}.webp")
BatchImage("photos/*.jpg").resize(800).jpeg().save("output/{name}.jpg", parallel=True)
```

`{name}` in the save pattern is replaced with each source file's stem.

## Web framework responses

```python
# Django
return Image("photo.jpg").resize(400).webp().to_django_response()

# Flask
return Image("photo.jpg").resize(400).webp().to_flask_response()

# FastAPI / Starlette
return Image("photo.jpg").resize(400).webp().to_fastapi_response()
```

## Loading from anywhere

```python
Image("photo.jpg")                          # File path
Image.from_bytes(raw_bytes)                 # Bytes
Image.from_base64(b64_string)               # Base64 string
Image.from_url("https://example.com/img")   # URL (requires httpx)
Image.from_file(file_object)                # File-like object
```

## Output options

```python
img = Image("photo.jpg").resize(400).webp()

img.save("output.webp")       # Save to file
img.to_bytes()                # Raw bytes
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
    .png()
    .save("final.png")
)
```

## Configuration

```python
from nitro_img import config

config.update(
    default_jpeg_quality=85,
    default_webp_quality=80,
    default_png_compression=6,
    allow_upscale=False,
    auto_orient=True,
    strip_metadata=False,
    max_output_dimensions=10_000,
)
```

## Requirements

- Python 3.10+
- Pillow 10.0+

## Ecosystem

- **[nitro-ui](https://github.com/nitrosh/nitro-ui)** - Build HTML with Python, not strings
- **[nitro-cli](https://github.com/nitrosh/nitro-cli)** - Python-powered static site generator
- **[nitro-datastore](https://github.com/nitrosh/nitro-datastore)** - Schema-free JSON data store with dot notation access
- **[nitro-dispatch](https://github.com/nitrosh/nitro-dispatch)** - Framework-agnostic plugin system
- **[nitro-validate](https://github.com/nitrosh/nitro-validate)** - Dependency-free data validation

## License

This project is licensed under the BSD 3-Clause License. See the [LICENSE](LICENSE) file for details.
