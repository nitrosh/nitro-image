"""Transform operations: rotate, flip, mirror."""

from __future__ import annotations

from typing import Callable

from PIL import Image as PILImage

Op = Callable[[PILImage.Image], PILImage.Image]


def rotate(degrees: float, *, expand: bool = True, fill: str = "white") -> Op:
    """Rotate the image by the given degrees (counter-clockwise)."""
    def _rotate(img: PILImage.Image) -> PILImage.Image:
        return img.rotate(degrees, expand=expand, fillcolor=fill, resample=PILImage.BICUBIC)
    return _rotate


def flip() -> Op:
    """Flip the image vertically (top to bottom)."""
    def _flip(img: PILImage.Image) -> PILImage.Image:
        return img.transpose(PILImage.FLIP_TOP_BOTTOM)
    return _flip


def mirror() -> Op:
    """Mirror the image horizontally (left to right)."""
    def _mirror(img: PILImage.Image) -> PILImage.Image:
        return img.transpose(PILImage.FLIP_LEFT_RIGHT)
    return _mirror


def grayscale() -> Op:
    """Convert the image to grayscale."""
    def _grayscale(img: PILImage.Image) -> PILImage.Image:
        return img.convert("L").convert("RGB")
    return _grayscale
