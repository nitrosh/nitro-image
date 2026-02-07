"""Pre-built pipelines for common image tasks."""

from __future__ import annotations

from pathlib import Path
from typing import IO

from PIL import Image as PILImage, ImageDraw

from .types import Format
from . import loaders
from .operations.resize import resize_fit, cover
from .operations.metadata import strip_metadata as _strip_metadata_op
from .output.encode import encode
from .responsive import save_responsive


def _load(source: str | Path | bytes | IO[bytes]) -> tuple[PILImage.Image, Format | None]:
    if isinstance(source, bytes):
        img, fmt, _ = loaders.load_from_bytes(source)
    elif isinstance(source, (str, Path)):
        img, fmt, _ = loaders.load_from_path(source)
    else:
        img, fmt, _ = loaders.load_from_file(source)
    return img, fmt


class Presets:
    """Opinionated, one-call solutions for common image tasks."""

    @staticmethod
    def thumbnail(
        source: str | Path | bytes,
        width: int = 200,
        height: int = 200,
        *,
        fmt: Format = Format.WEBP,
        quality: int | None = None,
    ) -> bytes:
        """Generate a thumbnail that fits within width x height."""
        img, _ = _load(source)
        img = resize_fit(width, height)(img)
        img = _strip_metadata_op()(img)
        return encode(img, fmt, quality=quality)

    @staticmethod
    def avatar(
        source: str | Path | bytes,
        size: int = 128,
        *,
        fmt: Format = Format.PNG,
        quality: int | None = None,
    ) -> bytes:
        """Circle-crop, centered, square avatar."""
        img, _ = _load(source)
        # Cover to fill the square, then circle-mask
        img = cover(size, size, allow_upscale=True)(img)
        img = img.convert("RGBA")

        mask = PILImage.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size - 1, size - 1), fill=255)
        img.putalpha(mask)

        return encode(img, fmt, quality=quality)

    @staticmethod
    def avatar_placeholder(
        initials: str,
        size: int = 128,
        bg: str = "#4A90D9",
        text_color: str = "white",
        *,
        fmt: Format = Format.PNG,
    ) -> bytes:
        """Generate an avatar placeholder with initials."""
        img = PILImage.new("RGBA", (size, size), bg)
        draw = ImageDraw.Draw(img)

        # Circle mask
        mask = PILImage.new("L", (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, size - 1, size - 1), fill=255)
        img.putalpha(mask)

        # Draw initials
        font_size = size // 2
        try:
            font = __import__("PIL.ImageFont", fromlist=["ImageFont"]).truetype(
                "DejaVuSans-Bold.ttf", font_size
            )
        except OSError:
            font = __import__("PIL.ImageFont", fromlist=["ImageFont"]).load_default()

        bbox = draw.textbbox((0, 0), initials.upper(), font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (size - text_w) // 2
        y = (size - text_h) // 2 - bbox[1]  # Adjust for baseline offset
        draw.text((x, y), initials.upper(), fill=text_color, font=font)

        return encode(img, fmt)

    @staticmethod
    def og_image(
        source: str | Path | bytes,
        width: int = 1200,
        height: int = 630,
        *,
        fmt: Format = Format.JPEG,
        quality: int = 85,
    ) -> bytes:
        """Generate an Open Graph image (1200x630 by default)."""
        img, _ = _load(source)
        img = cover(width, height, allow_upscale=True)(img)
        img = _strip_metadata_op()(img)
        return encode(img, fmt, quality=quality)

    @staticmethod
    def banner(
        source: str | Path | bytes,
        width: int = 1920,
        height: int = 400,
        *,
        fmt: Format = Format.JPEG,
        quality: int = 85,
    ) -> bytes:
        """Generate a hero/banner crop."""
        img, _ = _load(source)
        img = cover(width, height, allow_upscale=True)(img)
        img = _strip_metadata_op()(img)
        return encode(img, fmt, quality=quality)

    @staticmethod
    def responsive(
        source: str | Path | bytes,
        widths: list[int] | None = None,
        output_dir: str | Path = ".",
        name: str = "image",
        *,
        fmt: Format = Format.WEBP,
        quality: int | None = None,
    ) -> dict[int, Path]:
        """Generate responsive image set and save to disk."""
        if widths is None:
            widths = [320, 640, 1024, 1920]
        img, _ = _load(source)
        img = _strip_metadata_op()(img)
        return save_responsive(img, widths, output_dir, name, fmt=fmt, quality=quality)


presets = Presets()
