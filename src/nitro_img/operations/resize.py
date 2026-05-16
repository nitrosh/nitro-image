"""Resize operations: resize, thumbnail, cover, contain."""

from __future__ import annotations

from typing import Callable

from PIL import Image as PILImage

from ..config import config
from ..errors import ImageSizeError

Op = Callable[[PILImage.Image], PILImage.Image]


def _check_output_dims(width: int, height: int) -> None:
    cap = config.max_output_dimensions
    if width > cap or height > cap:
        raise ImageSizeError(
            f"Output {width}x{height} exceeds max_output_dimensions={cap}"
        )


def resize_fit(
    width: int | None = None,
    height: int | None = None,
    *,
    allow_upscale: bool = False,
) -> Op:
    """Resize to fit within dimensions, preserving aspect ratio."""
    def _resize(img: PILImage.Image) -> PILImage.Image:
        orig_w, orig_h = img.size

        if width is None and height is None:
            return img

        if width is not None and height is not None:
            target_w, target_h = width, height
        elif width is not None:
            ratio = width / orig_w
            target_w = width
            target_h = round(orig_h * ratio)
        else:
            ratio = height / orig_h
            target_w = round(orig_w * ratio)
            target_h = height

        ratio_w = target_w / orig_w
        ratio_h = target_h / orig_h
        ratio = min(ratio_w, ratio_h)

        if not allow_upscale and ratio > 1.0:
            return img

        new_w = max(1, round(orig_w * ratio))
        new_h = max(1, round(orig_h * ratio))
        _check_output_dims(new_w, new_h)
        return img.resize((new_w, new_h), PILImage.LANCZOS)

    return _resize


def thumbnail(
    width: int,
    height: int,
    *,
    allow_upscale: bool = False,
) -> Op:
    """Generate a thumbnail that fits within width x height."""
    def _thumbnail(img: PILImage.Image) -> PILImage.Image:
        if not allow_upscale and img.size[0] <= width and img.size[1] <= height:
            return img
        _check_output_dims(width, height)
        img = img.copy()
        img.thumbnail((width, height), PILImage.LANCZOS)
        return img

    return _thumbnail


def cover(
    width: int,
    height: int,
    *,
    allow_upscale: bool = False,
) -> Op:
    """Resize to cover dimensions, then center-crop the overflow."""
    def _cover(img: PILImage.Image) -> PILImage.Image:
        orig_w, orig_h = img.size
        ratio_w = width / orig_w
        ratio_h = height / orig_h
        ratio = max(ratio_w, ratio_h)

        if not allow_upscale and ratio > 1.0:
            # Source is smaller than target on at least one axis. Crop from the
            # original at whatever size we can produce without enlarging.
            crop_w = min(width, orig_w)
            crop_h = min(height, orig_h)
            _check_output_dims(crop_w, crop_h)
            return _center_crop(img, crop_w, crop_h)

        new_w = max(1, round(orig_w * ratio))
        new_h = max(1, round(orig_h * ratio))
        _check_output_dims(width, height)
        img = img.resize((new_w, new_h), PILImage.LANCZOS)
        return _center_crop(img, width, height)

    return _cover


def contain(
    width: int,
    height: int,
    bg: str = "white",
    *,
    allow_upscale: bool = False,
) -> Op:
    """Resize to fit within dimensions, pad the remainder with bg color."""
    def _contain(img: PILImage.Image) -> PILImage.Image:
        orig_w, orig_h = img.size
        ratio_w = width / orig_w
        ratio_h = height / orig_h
        ratio = min(ratio_w, ratio_h)

        if not allow_upscale and ratio > 1.0:
            ratio = 1.0

        new_w = max(1, round(orig_w * ratio))
        new_h = max(1, round(orig_h * ratio))
        _check_output_dims(width, height)
        resized = img.resize((new_w, new_h), PILImage.LANCZOS)

        mode = "RGBA" if img.mode == "RGBA" else "RGB"
        canvas = PILImage.new(mode, (width, height), bg)
        offset_x = (width - new_w) // 2
        offset_y = (height - new_h) // 2

        if resized.mode == "RGBA":
            canvas.paste(resized, (offset_x, offset_y), resized)
        else:
            canvas.paste(resized, (offset_x, offset_y))

        return canvas

    return _contain


def _center_crop(img: PILImage.Image, width: int, height: int) -> PILImage.Image:
    img_w, img_h = img.size
    left = (img_w - width) // 2
    top = (img_h - height) // 2
    right = left + width
    bottom = top + height
    return img.crop((left, top, right, bottom))
