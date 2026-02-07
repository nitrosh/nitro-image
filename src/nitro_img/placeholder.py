"""Placeholder generation: LQIP, dominant color, SVG placeholder."""

from __future__ import annotations

import base64
from collections import Counter

from PIL import Image as PILImage

from .output.encode import encode
from .types import Format


def lqip(img: PILImage.Image, width: int = 20) -> str:
    """Generate a Low Quality Image Placeholder as a base64 data URI.

    Creates a tiny, blurred version of the image for inline use.
    """
    orig_w, orig_h = img.size
    ratio = width / orig_w
    new_h = max(1, round(orig_h * ratio))
    small = img.resize((width, new_h), PILImage.LANCZOS)

    data = encode(small, Format.WEBP, quality=20)
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/webp;base64,{b64}"


def dominant_color(img: PILImage.Image, sample_size: int = 100) -> str:
    """Extract the dominant color as a hex string (#RRGGBB).

    Downscales the image then finds the most common color bucket.
    """
    small = img.copy()
    small.thumbnail((sample_size, sample_size), PILImage.LANCZOS)
    small = small.convert("RGB")

    pixels = list(zip(small.tobytes()[0::3], small.tobytes()[1::3], small.tobytes()[2::3]))
    # Quantize to reduce color space (bucket to nearest 16)
    quantized = [
        ((r >> 4) << 4, (g >> 4) << 4, (b >> 4) << 4)
        for r, g, b in pixels
    ]
    counter = Counter(quantized)
    most_common = counter.most_common(1)[0][0]
    return f"#{most_common[0]:02x}{most_common[1]:02x}{most_common[2]:02x}"


def color_palette(img: PILImage.Image, count: int = 5, sample_size: int = 100) -> list[str]:
    """Extract a color palette as a list of hex strings."""
    small = img.copy()
    small.thumbnail((sample_size, sample_size), PILImage.LANCZOS)
    small = small.convert("RGB")

    pixels = list(zip(small.tobytes()[0::3], small.tobytes()[1::3], small.tobytes()[2::3]))
    quantized = [
        ((r >> 4) << 4, (g >> 4) << 4, (b >> 4) << 4)
        for r, g, b in pixels
    ]
    counter = Counter(quantized)
    return [
        f"#{r:02x}{g:02x}{b:02x}"
        for (r, g, b), _ in counter.most_common(count)
    ]


def svg_placeholder(img: PILImage.Image, width: int | None = None, height: int | None = None) -> str:
    """Generate a lightweight SVG placeholder with the dominant color.

    Returns an SVG string that matches the image aspect ratio.
    """
    orig_w, orig_h = img.size
    w = width or orig_w
    h = height or orig_h
    color = dominant_color(img)

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<rect width="{w}" height="{h}" fill="{color}"/>'
        f'</svg>'
    )


def blurhash(img: PILImage.Image, components_x: int = 4, components_y: int = 3) -> str:
    """Generate a BlurHash string.

    Requires the `blurhash-python` package.
    Install with: pip install nitro-img[blur]
    """
    try:
        import blurhash as bh
    except ImportError:
        raise ImportError(
            "blurhash-python is required for BlurHash generation. "
            "Install with: pip install nitro-img[blur]"
        )

    small = img.copy()
    small.thumbnail((100, 100), PILImage.LANCZOS)
    small = small.convert("RGB")

    return bh.encode(small, components_x, components_y)
