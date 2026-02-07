"""Adjustment operations: brightness, contrast, saturation, sharpen, blur."""

from __future__ import annotations

from typing import Callable

from PIL import Image as PILImage, ImageEnhance, ImageFilter


def brightness(factor: float) -> Callable[[PILImage.Image], PILImage.Image]:
    """Adjust brightness. factor=1.0 is original, <1 darker, >1 brighter."""
    def _brightness(img: PILImage.Image) -> PILImage.Image:
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(factor)
    return _brightness


def contrast(factor: float) -> Callable[[PILImage.Image], PILImage.Image]:
    """Adjust contrast. factor=1.0 is original, <1 less contrast, >1 more."""
    def _contrast(img: PILImage.Image) -> PILImage.Image:
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(factor)
    return _contrast


def saturation(factor: float) -> Callable[[PILImage.Image], PILImage.Image]:
    """Adjust color saturation. factor=1.0 is original, 0 is grayscale, >1 vivid."""
    def _saturation(img: PILImage.Image) -> PILImage.Image:
        enhancer = ImageEnhance.Color(img)
        return enhancer.enhance(factor)
    return _saturation


def sharpen(factor: float = 2.0) -> Callable[[PILImage.Image], PILImage.Image]:
    """Sharpen the image. factor=1.0 is original, >1 sharper, <1 softer."""
    def _sharpen(img: PILImage.Image) -> PILImage.Image:
        enhancer = ImageEnhance.Sharpness(img)
        return enhancer.enhance(factor)
    return _sharpen


def blur(radius: float = 2.0) -> Callable[[PILImage.Image], PILImage.Image]:
    """Apply Gaussian blur with the given radius."""
    def _blur(img: PILImage.Image) -> PILImage.Image:
        return img.filter(ImageFilter.GaussianBlur(radius=radius))
    return _blur
