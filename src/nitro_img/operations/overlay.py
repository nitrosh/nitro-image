"""Watermark and text overlay operations."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from PIL import Image as PILImage, ImageDraw, ImageFont


_VALID_POSITIONS: frozenset[str] = frozenset({
    "center",
    "top-left", "top-right", "bottom-left", "bottom-right",
    "top", "bottom", "left", "right",
})

_VALID_WATERMARK_POSITIONS: frozenset[str] = _VALID_POSITIONS | {"tiled"}


def _validate_position(position: str, valid: frozenset[str]) -> None:
    if position not in valid:
        raise ValueError(
            f"Invalid position '{position}'. Expected one of: {sorted(valid)}."
        )


def _calculate_position(
    base_size: tuple[int, int],
    overlay_size: tuple[int, int],
    position: str,
    margin: int,
) -> tuple[int, int]:
    base_w, base_h = base_size
    over_w, over_h = overlay_size

    positions = {
        "center": ((base_w - over_w) // 2, (base_h - over_h) // 2),
        "top-left": (margin, margin),
        "top-right": (base_w - over_w - margin, margin),
        "bottom-left": (margin, base_h - over_h - margin),
        "bottom-right": (base_w - over_w - margin, base_h - over_h - margin),
        "top": ((base_w - over_w) // 2, margin),
        "bottom": ((base_w - over_w) // 2, base_h - over_h - margin),
        "left": (margin, (base_h - over_h) // 2),
        "right": (base_w - over_w - margin, (base_h - over_h) // 2),
    }
    return positions[position]


def _load_watermark(
    source: str | Path | PILImage.Image,
) -> PILImage.Image:
    if isinstance(source, PILImage.Image):
        wm = source.copy()
    else:
        wm = PILImage.open(source)
        wm.load()
    if wm.mode != "RGBA":
        wm = wm.convert("RGBA")
    return wm


def watermark(
    watermark_source: str | Path | PILImage.Image,
    position: str = "bottom-right",
    opacity: float = 0.3,
    scale: float | None = None,
    margin: int = 10,
) -> Callable[[PILImage.Image], PILImage.Image]:
    """Apply an image watermark at the given position with opacity."""
    _validate_position(position, _VALID_WATERMARK_POSITIONS)

    # Load and pre-process the watermark once. Scaling that depends on the base
    # image still happens inside the closure, but the disk read does not.
    cached_wm = _load_watermark(watermark_source)
    if opacity < 1.0:
        r, g, b, a = cached_wm.split()
        a = a.point(lambda x: round(x * opacity))
        cached_wm = PILImage.merge("RGBA", (r, g, b, a))

    def _watermark(img: PILImage.Image) -> PILImage.Image:
        wm = cached_wm
        if scale is not None:
            new_w = max(1, round(img.size[0] * scale))
            ratio = new_w / wm.size[0]
            new_h = max(1, round(wm.size[1] * ratio))
            wm = wm.resize((new_w, new_h), PILImage.LANCZOS)

        base = img.convert("RGBA") if img.mode != "RGBA" else img.copy()

        if position == "tiled":
            for y in range(0, base.size[1], wm.size[1] + margin):
                for x in range(0, base.size[0], wm.size[0] + margin):
                    base.paste(wm, (x, y), wm)
        else:
            pos = _calculate_position(base.size, wm.size, position, margin)
            base.paste(wm, pos, wm)

        if img.mode == "RGB":
            return base.convert("RGB")
        return base

    return _watermark


def text_overlay(
    text: str,
    position: str = "bottom-right",
    font_path: str | None = None,
    font_size: int = 24,
    color: str | tuple = "white",
    opacity: float = 1.0,
    margin: int = 10,
) -> Callable[[PILImage.Image], PILImage.Image]:
    """Add a text overlay at the given position."""
    _validate_position(position, _VALID_POSITIONS)

    def _text_overlay(img: PILImage.Image) -> PILImage.Image:
        base = img.convert("RGBA") if img.mode != "RGBA" else img.copy()

        txt_layer = PILImage.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(txt_layer)

        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", font_size)
            except OSError:
                font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        pos = _calculate_position(base.size, (text_w, text_h), position, margin)

        if isinstance(color, str):
            from PIL import ImageColor
            rgba = ImageColor.getrgb(color)
            if len(rgba) == 3:
                rgba = (*rgba, round(255 * opacity))
            else:
                rgba = (*rgba[:3], round(rgba[3] * opacity))
        else:
            if len(color) == 3:
                rgba = (*color, round(255 * opacity))
            else:
                rgba = (*color[:3], round(color[3] * opacity))

        draw.text(pos, text, font=font, fill=rgba)
        result = PILImage.alpha_composite(base, txt_layer)

        if img.mode == "RGB":
            return result.convert("RGB")
        return result

    return _text_overlay
