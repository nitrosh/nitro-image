"""Visual effects: sepia, rounded corners."""

from __future__ import annotations

from typing import Callable

from PIL import Image as PILImage, ImageDraw


def sepia() -> Callable[[PILImage.Image], PILImage.Image]:
    """Apply a warm sepia tone to the image."""
    def _sepia(img: PILImage.Image) -> PILImage.Image:
        was_rgba = img.mode == "RGBA"
        alpha = img.getchannel("A") if was_rgba else None

        rgb = img.convert("RGB")
        w, h = rgb.size
        raw = rgb.tobytes()
        pixels = []

        for i in range(0, len(raw), 3):
            r, g, b = raw[i], raw[i + 1], raw[i + 2]
            tr = min(255, int(0.393 * r + 0.769 * g + 0.189 * b))
            tg = min(255, int(0.349 * r + 0.686 * g + 0.168 * b))
            tb = min(255, int(0.272 * r + 0.534 * g + 0.131 * b))
            pixels.extend([tr, tg, tb])

        result = PILImage.frombytes("RGB", (w, h), bytes(pixels))

        if was_rgba and alpha is not None:
            result = result.convert("RGBA")
            result.putalpha(alpha)

        return result
    return _sepia


def rounded_corners(radius: int) -> Callable[[PILImage.Image], PILImage.Image]:
    """Apply rounded corners with the given radius.

    Converts the image to RGBA and makes corners transparent.
    """
    def _rounded(img: PILImage.Image) -> PILImage.Image:
        img = img.convert("RGBA")
        w, h = img.size

        mask = PILImage.new("L", (w, h), 255)
        draw = ImageDraw.Draw(mask)

        # Draw black corners (will become transparent)
        # Top-left
        draw.rectangle([0, 0, radius, radius], fill=0)
        draw.pieslice([0, 0, radius * 2, radius * 2], 180, 270, fill=255)
        # Top-right
        draw.rectangle([w - radius, 0, w, radius], fill=0)
        draw.pieslice([w - radius * 2, 0, w, radius * 2], 270, 360, fill=255)
        # Bottom-left
        draw.rectangle([0, h - radius, radius, h], fill=0)
        draw.pieslice([0, h - radius * 2, radius * 2, h], 90, 180, fill=255)
        # Bottom-right
        draw.rectangle([w - radius, h - radius, w, h], fill=0)
        draw.pieslice([w - radius * 2, h - radius * 2, w, h], 0, 90, fill=255)

        img.putalpha(mask)
        return img
    return _rounded
