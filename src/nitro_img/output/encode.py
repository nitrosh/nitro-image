"""Format encoding: JPEG, PNG, WebP."""

from __future__ import annotations

import io

from PIL import Image as PILImage

from ..config import config
from ..errors import ImageOutputError
from ..types import Format


_FORMAT_SAVE_PARAMS: dict[Format, dict] = {
    Format.JPEG: {"format": "JPEG"},
    Format.PNG: {"format": "PNG"},
    Format.WEBP: {"format": "WEBP"},
    Format.GIF: {"format": "GIF"},
    Format.BMP: {"format": "BMP"},
    Format.TIFF: {"format": "TIFF"},
}


def encode(
    img: PILImage.Image,
    fmt: Format,
    *,
    quality: int | None = None,
) -> bytes:
    """Encode a PIL Image to bytes in the specified format."""
    params = dict(_FORMAT_SAVE_PARAMS.get(fmt, {"format": fmt.value}))

    if fmt == Format.JPEG:
        if img.mode == "RGBA":
            img = img.convert("RGB")
        elif img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        params["quality"] = quality or config.default_jpeg_quality

    elif fmt == Format.WEBP:
        params["quality"] = quality or config.default_webp_quality

    elif fmt == Format.PNG:
        params["compress_level"] = config.default_png_compression
        # PNG supports RGBA natively, no conversion needed

    buf = io.BytesIO()
    try:
        img.save(buf, **params)
    except Exception as e:
        raise ImageOutputError(f"Failed to encode as {fmt.value}: {e}") from e
    return buf.getvalue()
