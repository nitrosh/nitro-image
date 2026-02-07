"""Crop operations: center, anchor-based, exact dimensions."""

from __future__ import annotations

from PIL import Image as PILImage

from ..types import Anchor


_ANCHOR_MAP: dict[str, tuple[float, float]] = {
    "center": (0.5, 0.5),
    "top-left": (0.0, 0.0),
    "top": (0.5, 0.0),
    "top-right": (1.0, 0.0),
    "left": (0.0, 0.5),
    "right": (1.0, 0.5),
    "bottom-left": (0.0, 1.0),
    "bottom": (0.5, 1.0),
    "bottom-right": (1.0, 1.0),
}


def crop(
    width: int,
    height: int,
    anchor: Anchor = "center",
) -> callable:
    """Crop to exact dimensions from the given anchor point."""
    def _crop(img: PILImage.Image) -> PILImage.Image:
        img_w, img_h = img.size
        crop_w = min(width, img_w)
        crop_h = min(height, img_h)

        ax, ay = _ANCHOR_MAP.get(anchor, (0.5, 0.5))

        left = int((img_w - crop_w) * ax)
        top = int((img_h - crop_h) * ay)
        right = left + crop_w
        bottom = top + crop_h

        return img.crop((left, top, right, bottom))

    return _crop
