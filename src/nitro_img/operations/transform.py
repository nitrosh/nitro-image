"""Transform operations: rotate, flip, mirror."""

from __future__ import annotations

from PIL import Image as PILImage


def rotate(degrees: float, *, expand: bool = True, fill: str = "white") -> callable:
    """Rotate the image by the given degrees (counter-clockwise)."""
    def _rotate(img: PILImage.Image) -> PILImage.Image:
        return img.rotate(degrees, expand=expand, fillcolor=fill, resample=PILImage.BICUBIC)
    return _rotate


def flip() -> callable:
    """Flip the image vertically (top to bottom)."""
    def _flip(img: PILImage.Image) -> PILImage.Image:
        return img.transpose(PILImage.FLIP_TOP_BOTTOM)
    return _flip


def mirror() -> callable:
    """Mirror the image horizontally (left to right)."""
    def _mirror(img: PILImage.Image) -> PILImage.Image:
        return img.transpose(PILImage.FLIP_LEFT_RIGHT)
    return _mirror


def grayscale() -> callable:
    """Convert the image to grayscale."""
    def _grayscale(img: PILImage.Image) -> PILImage.Image:
        return img.convert("L").convert("RGB")
    return _grayscale
