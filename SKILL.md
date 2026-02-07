# nitro-image (nitro_img) - LLM Reference

## What This Library Does

nitro-image is a Python image processing library that wraps Pillow with a chainable API and lazy execution pipeline. Operations are queued in a pipeline and only execute when an output method is called (`.save()`, `.to_bytes()`, etc.). The package is imported as `nitro_img` and installed as `nitro-image`.

```python
from nitro_img import Image

Image("photo.jpg").resize(800).webp(quality=80).save("output.webp")
```

## Core Concepts

### Lazy Execution

Every chainable method (resize, crop, brightness, etc.) queues an operation - nothing runs until you call an output method. This means you can build complex pipelines and the image is only processed once.

```python
img = Image("photo.jpg")
img.resize(400)        # queued, not executed
img.brightness(1.2)    # queued, not executed
img.webp()             # sets format, not executed
img.save("out.webp")   # NOW everything executes
```

### Format Resolution Chain

When an output method runs, the format is resolved in this priority:

1. Explicit format method (`.jpeg()`, `.png()`, `.webp()`, `.gif()`, `.format()`)
2. `.auto_format()` flag (picks best format for content)
3. Save path extension (only for `.save()`)
4. Source image format
5. Raises `ImageFormatError` if none of the above resolves

### Immediate vs Deferred Methods

Most methods are **deferred** (chainable, queue operations):
- resize, thumbnail, cover, contain, crop, rotate, flip, mirror, grayscale, strip_metadata
- watermark, text_overlay, brightness, contrast, saturation, sharpen, blur, sepia, rounded_corners
- jpeg, png, webp, gif, format, auto_format

Some methods **execute immediately** (run the pipeline and return a result):
- `save()`, `to_bytes()`, `to_base64()`, `to_data_uri()`, `to_response()`
- `to_django_response()`, `to_flask_response()`, `to_fastapi_response()`
- `responsive()`, `save_responsive()`, `optimize()`
- `lqip()`, `dominant_color()`, `color_palette()`, `svg_placeholder()`, `blurhash()`
- `get_metadata()`

---

## Import

```python
from nitro_img import Image                          # Core class
from nitro_img import BatchImage                     # Batch/glob processing
from nitro_img import config                         # Global configuration
from nitro_img import presets                         # Standalone preset functions
from nitro_img import Format, Position, ResizeStrategy  # Enums
from nitro_img import (                              # Errors
    NitroImgError, ImageLoadError, ImageFormatError,
    ImageSizeError, ImageProcessingError, ImageOutputError,
)
```

---

## Image Class - Full API

### Creating an Image

```python
# From file path
img = Image("photo.jpg")
img = Image(Path("photo.jpg"))

# From bytes
img = Image.from_bytes(raw_bytes)

# From base64 string (handles "data:image/...;base64," prefix automatically)
img = Image.from_base64(b64_string)

# From URL (requires: pip install nitro-image[url])
img = Image.from_url("https://example.com/photo.jpg")

# From file-like object
with open("photo.jpg", "rb") as f:
    img = Image.from_file(f)
```

### Properties

```python
img.width          # int - original image width in pixels
img.height         # int - original image height in pixels
img.size           # tuple[int, int] - (width, height)
img.source_format  # Format | None - detected source format
```

### Resize Operations

```python
# Fit within dimensions, preserve aspect ratio. At least one dimension required.
img.resize(width=800)
img.resize(height=600)
img.resize(width=800, height=600)
img.resize(800)                        # positional: width
img.resize(800, allow_upscale=True)    # allow enlarging small images

# Thumbnail - fit within a box
img.thumbnail(200, 200)
img.thumbnail(200, 200, allow_upscale=True)

# Cover - fill exact dimensions, center-crop overflow
img.cover(400, 400)
img.cover(400, 400, allow_upscale=True)

# Contain - fit within dimensions, pad with background color
img.contain(400, 400)
img.contain(400, 400, bg="black")
img.contain(400, 400, bg="#ff0000")
```

**Parameters:**
| Method | Params | Defaults |
|---|---|---|
| `resize(width, height, *, allow_upscale)` | `width: int\|None`, `height: int\|None`, `allow_upscale: bool\|None` | `None`, `None`, `None` (uses `config.allow_upscale`) |
| `thumbnail(width, height, *, allow_upscale)` | `width: int`, `height: int`, `allow_upscale: bool\|None` | -, -, `None` |
| `cover(width, height, *, allow_upscale)` | `width: int`, `height: int`, `allow_upscale: bool\|None` | -, -, `None` |
| `contain(width, height, bg, *, allow_upscale)` | `width: int`, `height: int`, `bg: str`, `allow_upscale: bool\|None` | -, -, `"white"`, `None` |

### Crop

```python
img.crop(400, 300)                    # center crop
img.crop(400, 300, anchor="top-left")
```

**Anchor values:** `"center"`, `"top-left"`, `"top-right"`, `"bottom-left"`, `"bottom-right"`, `"top"`, `"bottom"`, `"left"`, `"right"`

### Transform

```python
img.rotate(90)                         # counter-clockwise, expand canvas
img.rotate(45, expand=False)           # clip to original size
img.rotate(45, fill="black")           # fill exposed area
img.flip()                             # vertical flip (top ↔ bottom)
img.mirror()                           # horizontal flip (left ↔ right)
img.grayscale()                        # convert to grayscale
img.strip_metadata()                   # remove EXIF/IPTC/XMP
```

### Adjustments

```python
img.brightness(1.2)    # >1 brighter, <1 darker, 1.0 unchanged
img.contrast(1.1)      # >1 more contrast, <1 less, 1.0 unchanged
img.saturation(1.3)    # >1 more vivid, 0 grayscale, 1.0 unchanged
img.sharpen(1.5)       # >1 sharper, <1 softer, 1.0 unchanged (default: 2.0)
img.blur(3.0)          # Gaussian blur radius (default: 2.0)
```

### Effects

```python
img.sepia()              # warm sepia tone
img.rounded_corners(20)  # radius in pixels, produces alpha channel
```

### Watermark and Text

```python
# Image watermark
img.watermark("logo.png", position="bottom-right", opacity=0.3, scale=0.2, margin=10)
img.watermark("logo.png", position="tiled")  # repeating watermark

# Text overlay
img.text_overlay("Sample", position="center", font_size=48, color="white", opacity=0.8)
img.text_overlay("Hello", font_path="/path/to/font.ttf", font_size=36, color=(255, 0, 0))
```

**Watermark parameters:**
| Param | Type | Default | Notes |
|---|---|---|---|
| `source` | `str \| Path \| PILImage` | required | watermark image |
| `position` | `str` | `"bottom-right"` | any anchor value or `"tiled"` |
| `opacity` | `float` | `0.3` | 0.0–1.0 |
| `scale` | `float \| None` | `None` | fraction of base image width |
| `margin` | `int` | `10` | pixels from edge |

**Text overlay parameters:**
| Param | Type | Default |
|---|---|---|
| `text` | `str` | required |
| `position` | `str` | `"bottom-right"` |
| `font_path` | `str \| None` | `None` (system default) |
| `font_size` | `int` | `24` |
| `color` | `str \| tuple` | `"white"` |
| `opacity` | `float` | `1.0` |
| `margin` | `int` | `10` |

### Format Selection

```python
img.jpeg()              # JPEG format
img.jpeg(quality=90)    # with explicit quality
img.png()               # PNG format
img.webp()              # WebP format
img.webp(quality=80)    # with explicit quality
img.gif()               # GIF format
img.format("JPEG")      # by string name
img.format(Format.WEBP) # by enum
img.auto_format()       # auto-pick best format at output time
```

If no format is set, `.save()` will try the file extension, then fall back to the source format.

### Output Methods

All output methods trigger pipeline execution.

```python
# Save to file - returns Path
path = img.save("output.webp")
path = img.save(Path("output") / "photo.jpg")

# Raw bytes
data = img.to_bytes()

# Base64 string
b64 = img.to_base64()

# Data URI (for embedding in HTML/CSS)
uri = img.to_data_uri()  # "data:image/webp;base64,..."

# Framework-agnostic response dict
resp = img.to_response()
# {"body": bytes, "content_type": "image/webp", "content_length": 12345}
```

### Framework Integration

Requires the respective framework installed. Raises `ImportError` with a clear message if not.

```python
# Django - returns HttpResponse
return img.to_django_response()
return img.to_django_response(filename="photo.webp")

# Flask - returns Response
return img.to_flask_response()
return img.to_flask_response(filename="photo.webp")

# FastAPI/Starlette - returns Response
return img.to_fastapi_response()
return img.to_fastapi_response(filename="photo.webp")
```

### Responsive Images

```python
# Generate multiple sizes as bytes dict - executes immediately
widths = img.responsive([400, 800, 1200, 1600])
# Returns: {400: bytes, 800: bytes, 1200: bytes, 1600: bytes}

# With options
widths = img.responsive(
    [400, 800, 1200],
    fmt=Format.WEBP,
    quality=80,
    allow_upscale=False,  # default
)

# Default widths if omitted: [320, 640, 1024, 1920]
widths = img.responsive()

# Save responsive set to disk - executes immediately
paths = img.save_responsive("output/", [400, 800, 1200])
# Returns: {400: Path("output/photo_400.webp"), ...}

paths = img.save_responsive(
    "output/",
    [400, 800, 1200],
    name="hero",           # filename prefix (default: source filename stem)
    fmt=Format.WEBP,
    quality=80,
)
```

### Placeholders - All Execute Immediately

```python
# Low-quality image placeholder (tiny base64 data URI)
uri = img.lqip()           # 20px wide thumbnail as data URI
uri = img.lqip(width=30)   # custom width

# Dominant color
color = img.dominant_color()  # "#3a6b8c"

# Color palette
colors = img.color_palette()       # ["#3a6b8c", "#d4a574", ...] - 5 colors
colors = img.color_palette(count=8)

# SVG placeholder (dominant color rectangle)
svg = img.svg_placeholder()
svg = img.svg_placeholder(width=800, height=600)  # custom dimensions

# BlurHash (requires: pip install nitro-image[blur])
hash_str = img.blurhash()
hash_str = img.blurhash(components_x=4, components_y=3)
```

### Optimization

```python
# Binary-search quality to fit target size - executes immediately, returns bytes
data = img.optimize(target_kb=200)
data = img.optimize(target_kb=100, min_quality=20, max_quality=90)
```

### Metadata

```python
# Returns dict - executes immediately (reads from original, not pipeline)
meta = img.get_metadata()
# {
#     "width": 1920,
#     "height": 1080,
#     "mode": "RGB",
#     "format": "JPEG",
#     "exif": {...}   # present only if EXIF data exists
# }
```

### Presets

Presets are accessible as `Image.preset.*` (class-level) or via the standalone `presets` import. They accept a source (path, bytes, or file object) and return processed bytes or paths.

```python
from nitro_img import Image

# Thumbnail - 200x200 fit, WebP
data = Image.preset.thumbnail("photo.jpg")
data = Image.preset.thumbnail("photo.jpg", width=300, height=300, fmt=Format.JPEG)

# Avatar - circle-cropped, PNG
data = Image.preset.avatar("photo.jpg")
data = Image.preset.avatar("photo.jpg", size=256, fmt=Format.WEBP)

# Avatar placeholder - colored circle with initials
data = Image.preset.avatar_placeholder("SN")
data = Image.preset.avatar_placeholder("SN", size=256, bg="#E74C3C", text_color="white")

# Open Graph image - 1200x630 cover crop, JPEG
data = Image.preset.og_image("photo.jpg")
data = Image.preset.og_image("photo.jpg", width=1200, height=630, quality=90)

# Banner - 1920x400 cover crop, JPEG
data = Image.preset.banner("photo.jpg")
data = Image.preset.banner("photo.jpg", width=1920, height=400, quality=90)

# Responsive set - generates + saves multiple sizes
paths = Image.preset.responsive("photo.jpg", output_dir="output/", name="hero")
# Returns: {320: Path, 640: Path, 1024: Path, 1920: Path}
```

**Preset parameter details:**
| Preset | Key Params | Defaults |
|---|---|---|
| `thumbnail(source, width, height, fmt, quality)` | `width=200`, `height=200` | `fmt=WEBP`, `quality=None` |
| `avatar(source, size, fmt, quality)` | `size=128` | `fmt=PNG`, `quality=None` |
| `avatar_placeholder(initials, size, bg, text_color, fmt)` | `size=128` | `bg="#4A90D9"`, `text_color="white"`, `fmt=PNG` |
| `og_image(source, width, height, fmt, quality)` | `width=1200`, `height=630` | `fmt=JPEG`, `quality=85` |
| `banner(source, width, height, fmt, quality)` | `width=1920`, `height=400` | `fmt=JPEG`, `quality=85` |
| `responsive(source, widths, output_dir, name, fmt, quality)` | `widths=[320,640,1024,1920]` | `output_dir="."`, `name="image"`, `fmt=WEBP` |

---

## BatchImage Class

Process multiple images matching a glob pattern with the same pipeline.

```python
from nitro_img import BatchImage

# Basic batch processing
BatchImage("photos/*.jpg").resize(800).webp().save("output/{name}.webp")

# Parallel processing
BatchImage("photos/*.jpg").resize(800).jpeg(quality=80).save(
    "output/{name}.jpg",
    parallel=True,
    max_workers=4,
)

# Chain multiple operations
(
    BatchImage("uploads/*.png")
    .resize(600)
    .brightness(1.1)
    .contrast(1.05)
    .grayscale()
    .jpeg(quality=85)
    .save("processed/{name}.jpg", parallel=True)
)
```

### Constructor

```python
batch = BatchImage("photos/*.jpg")  # glob pattern string
batch.count   # int - number of matched files
batch.paths   # list[str] - matched file paths
```

Raises `ImageLoadError` if no files match the pattern.

### Save

```python
results = batch.save(
    "output/{name}.jpg",   # {name} = original filename stem
    parallel=False,        # default: sequential
    max_workers=None,      # default: min(count, 8) when parallel=True
)
# Returns: list[Path]
```

### Available Chainable Methods

BatchImage supports the same chainable methods as Image: `resize`, `thumbnail`, `cover`, `contain`, `crop`, `rotate`, `flip`, `mirror`, `grayscale`, `strip_metadata`, `watermark`, `text_overlay`, `brightness`, `contrast`, `saturation`, `sharpen`, `blur`, `sepia`, `rounded_corners`, `jpeg`, `png`, `webp`, `format`.

---

## Configuration

```python
from nitro_img import config

config.update(
    default_jpeg_quality=85,    # int, default: 85
    default_webp_quality=80,    # int, default: 80
    default_png_compression=6,  # int, default: 6
    allow_upscale=False,        # bool, default: False
    auto_orient=True,           # bool, default: True - auto-apply EXIF rotation on load
    strip_metadata=False,       # bool, default: False - auto-strip metadata on load
    max_input_size=50_000_000,  # int bytes, default: 50MB
    max_output_dimensions=10_000,  # int pixels, default: 10000
    url_timeout=30.0,           # float seconds, default: 30.0
    url_max_size=50_000_000,    # int bytes, default: 50MB
)
```

---

## Enums

### Format

```python
from nitro_img import Format

Format.JPEG   # "JPEG"
Format.PNG    # "PNG"
Format.WEBP   # "WEBP"
Format.GIF    # "GIF"
Format.BMP    # "BMP"
Format.TIFF   # "TIFF"
```

### Position

```python
from nitro_img import Position

Position.CENTER        # "center"
Position.TOP_LEFT      # "top-left"
Position.TOP_RIGHT     # "top-right"
Position.BOTTOM_LEFT   # "bottom-left"
Position.BOTTOM_RIGHT  # "bottom-right"
Position.TOP           # "top"
Position.BOTTOM        # "bottom"
Position.LEFT          # "left"
Position.RIGHT         # "right"
```

### ResizeStrategy

```python
from nitro_img import ResizeStrategy

ResizeStrategy.FIT      # "fit"
ResizeStrategy.COVER    # "cover"
ResizeStrategy.CONTAIN  # "contain"
ResizeStrategy.EXACT    # "exact"
```

---

## Errors

All errors inherit from `NitroImgError`.

```python
from nitro_img import (
    NitroImgError,       # Base - catch-all
    ImageLoadError,      # Cannot read or decode input image
    ImageFormatError,    # Unsupported/missing format
    ImageSizeError,      # Image exceeds size limits
    ImageProcessingError,  # Operation failed during pipeline
    ImageOutputError,    # Cannot write or encode output
)
```

---

## Optional Dependencies

| Extra | Package | Enables |
|---|---|---|
| `url` | httpx | `Image.from_url()` |
| `avif` | pillow-avif-plugin | AVIF format support |
| `blur` | blurhash-python | `.blurhash()` method |
| `all` | all of the above | everything |

Install with: `pip install nitro-image[all]`

---

## Common Patterns

### Web upload processing (Django)

```python
from nitro_img import Image

def handle_upload(request):
    file = request.FILES["photo"]
    img = Image.from_file(file)
    return img.resize(800).auto_format().to_django_response()
```

### Generate thumbnail + placeholder together

```python
from nitro_img import Image

img = Image("photo.jpg")
placeholder = img.lqip()          # tiny base64 for instant loading
thumb = img.resize(400).webp().to_bytes()  # actual thumbnail
```

### Batch resize with effects

```python
from nitro_img import BatchImage

(
    BatchImage("uploads/*.jpg")
    .resize(1200)
    .brightness(1.05)
    .sharpen(1.3)
    .webp(quality=82)
    .save("processed/{name}.webp", parallel=True)
)
```

### Social media images from one source

```python
from nitro_img import Image

img = Image("photo.jpg")
og = img.cover(1200, 630).jpeg(quality=85).to_bytes()
twitter = img.cover(1200, 675).jpeg(quality=85).to_bytes()
square = img.cover(1080, 1080).jpeg(quality=85).to_bytes()
```

### Optimize for target file size

```python
from nitro_img import Image

data = Image("photo.jpg").resize(1200).optimize(target_kb=200)
# Returns bytes fitting within ~200KB
```

### Responsive images with HTML

```python
from nitro_img import Image

img = Image("hero.jpg")
img.save_responsive("static/hero/", [400, 800, 1200, 1600], name="hero")

# Then in HTML:
# <img srcset="hero_400.webp 400w, hero_800.webp 800w, ..."
#      sizes="(max-width: 800px) 100vw, 800px"
#      src="hero_800.webp">
```

---

## Gotchas and Edge Cases

1. **JPEG doesn't support transparency.** If you apply `.rounded_corners()` or work with RGBA images, use `.png()` or `.webp()` - not `.jpeg()`. The library auto-converts RGBA to RGB for JPEG by compositing onto white.

2. **No upscale by default.** `resize(1600)` on an 800px image does nothing unless you pass `allow_upscale=True`. Same for `cover()`, `contain()`, and `thumbnail()`.

3. **Responsive no-upscale deduplication.** If `allow_upscale=False` (default), requesting widths `[800, 1200, 1600]` on an 800px image may return only `{800: bytes}` since all sizes clamp to 800.

4. **Pipeline runs once per output call.** Each call to `.save()`, `.to_bytes()`, etc. re-executes the full pipeline from the original image. The original is never mutated.

5. **Format required for byte output.** `.to_bytes()`, `.to_base64()`, etc. need a format set (via `.jpeg()`, `.webp()`, etc.). `.save()` can infer from the file extension.

6. **auto_format is deferred.** `.auto_format()` doesn't pick the format immediately - it resolves when an output method is called. Images with alpha get PNG; photographic images get WebP or JPEG (whichever is smaller).

7. **Presets are standalone.** `Image.preset.thumbnail("photo.jpg")` returns `bytes` directly - it doesn't return an `Image` instance. Presets load, process, and encode in one call.

8. **BatchImage records, doesn't chain Image instances.** Each operation on `BatchImage` records the method name and args. On `.save()`, it creates a fresh `Image` for each file and replays the recorded operations.
