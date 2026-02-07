"""Resize operations: resize, thumbnail, cover, contain."""

from __future__ import annotations

from PIL import Image as PILImage


def resize_fit(
    width: int | None = None,
    height: int | None = None,
    *,
    allow_upscale: bool = False,
) -> callable:
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

        # Maintain aspect ratio — fit within the box
        ratio_w = target_w / orig_w
        ratio_h = target_h / orig_h
        ratio = min(ratio_w, ratio_h)

        if not allow_upscale and ratio > 1.0:
            return img

        new_w = max(1, round(orig_w * ratio))
        new_h = max(1, round(orig_h * ratio))
        return img.resize((new_w, new_h), PILImage.LANCZOS)

    return _resize


def thumbnail(
    width: int,
    height: int,
    *,
    allow_upscale: bool = False,
) -> callable:
    """Generate a thumbnail that fits within width x height."""
    def _thumbnail(img: PILImage.Image) -> PILImage.Image:
        if not allow_upscale and img.size[0] <= width and img.size[1] <= height:
            return img
        img = img.copy()
        img.thumbnail((width, height), PILImage.LANCZOS)
        return img

    return _thumbnail


def cover(
    width: int,
    height: int,
    *,
    allow_upscale: bool = False,
) -> callable:
    """Resize to cover dimensions, then center-crop the overflow."""
    def _cover(img: PILImage.Image) -> PILImage.Image:
        orig_w, orig_h = img.size
        ratio_w = width / orig_w
        ratio_h = height / orig_h
        ratio = max(ratio_w, ratio_h)

        if not allow_upscale and ratio > 1.0:
            ratio = max(ratio_w, ratio_h)
            if ratio > 1.0:
                # Can't cover without upscaling — crop from center at original size
                return _center_crop(img, min(width, orig_w), min(height, orig_h))

        new_w = max(1, round(orig_w * ratio))
        new_h = max(1, round(orig_h * ratio))
        img = img.resize((new_w, new_h), PILImage.LANCZOS)
        return _center_crop(img, width, height)

    return _cover


def contain(
    width: int,
    height: int,
    bg: str = "white",
    *,
    allow_upscale: bool = False,
) -> callable:
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
