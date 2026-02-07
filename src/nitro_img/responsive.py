"""Responsive image set generation."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image as PILImage

from .output.encode import encode
from .types import Format

if TYPE_CHECKING:
    pass


def generate_responsive(
    img: PILImage.Image,
    widths: list[int],
    *,
    fmt: Format = Format.WEBP,
    quality: int | None = None,
    allow_upscale: bool = False,
) -> dict[int, bytes]:
    """Generate multiple sizes of an image, returning {width: bytes}."""
    results: dict[int, bytes] = {}
    orig_w, orig_h = img.size

    for width in sorted(widths):
        if not allow_upscale and width > orig_w:
            # Use original size as max
            ratio = 1.0
        else:
            ratio = width / orig_w

        new_w = max(1, round(orig_w * ratio))
        new_h = max(1, round(orig_h * ratio))
        resized = img.resize((new_w, new_h), PILImage.LANCZOS)
        results[new_w] = encode(resized, fmt, quality=quality)

    return results


def save_responsive(
    img: PILImage.Image,
    widths: list[int],
    output_dir: str | Path,
    name: str = "image",
    *,
    fmt: Format = Format.WEBP,
    quality: int | None = None,
    allow_upscale: bool = False,
) -> dict[int, Path]:
    """Generate and save multiple sizes, returning {width: Path}."""
    from .utils import extension_for_format

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ext = extension_for_format(fmt)

    results: dict[int, Path] = {}
    sizes = generate_responsive(
        img, widths, fmt=fmt, quality=quality, allow_upscale=allow_upscale,
    )

    for width, data in sizes.items():
        out_path = output_dir / f"{name}_{width}{ext}"
        out_path.write_bytes(data)
        results[width] = out_path

    return results
