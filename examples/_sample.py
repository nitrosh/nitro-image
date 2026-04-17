"""Shared helpers for examples: generate sample images and output paths.

Every example imports from this module so none of them need checked-in image
binaries. Run any example from the repo root:

    python examples/01_basics.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image as PILImage, ImageDraw

ROOT = Path(__file__).resolve().parent
SAMPLES = ROOT / "samples"
OUTPUT = ROOT / "output"


def ensure_dirs() -> None:
    SAMPLES.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)


def _gradient(width: int, height: int) -> PILImage.Image:
    img = PILImage.new("RGB", (width, height))
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            pixels[x, y] = (
                int(255 * x / width),
                int(255 * y / height),
                int(255 * (1 - x / width)),
            )
    return img


def photo(width: int = 1600, height: int = 1200) -> Path:
    """A colorful gradient that stands in for a JPEG photo."""
    ensure_dirs()
    path = SAMPLES / f"photo_{width}x{height}.jpg"
    if not path.exists():
        _gradient(width, height).save(path, "JPEG", quality=90)
    return path


def logo(size: int = 200) -> Path:
    """A transparent PNG with a circle — used for watermark examples."""
    ensure_dirs()
    path = SAMPLES / f"logo_{size}.png"
    if not path.exists():
        img = PILImage.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((10, 10, size - 10, size - 10), fill=(255, 80, 80, 230))
        draw.text((size // 2 - 10, size // 2 - 8), "N", fill="white")
        img.save(path, "PNG")
    return path


def out(name: str) -> Path:
    """Resolve an output path inside examples/output/ and ensure the dir exists."""
    ensure_dirs()
    path = OUTPUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def banner(title: str) -> None:
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)
