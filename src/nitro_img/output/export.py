"""Export functions: save, to_bytes, to_base64, to_data_uri, to_response."""

from __future__ import annotations

import base64
from pathlib import Path

from PIL import Image as PILImage

from ..errors import ImageOutputError
from ..types import Format
from ..utils import format_from_extension, mime_type
from .encode import encode


def save(
    img: PILImage.Image,
    path: str | Path,
    fmt: Format | None = None,
    *,
    quality: int | None = None,
) -> Path:
    """Save image to disk. Format detected from extension if not specified."""
    path = Path(path)

    if fmt is None:
        fmt = format_from_extension(path)
    if fmt is None:
        raise ImageOutputError(
            f"Cannot determine output format for '{path}'. "
            "Specify format explicitly or use a recognized extension."
        )

    data = encode(img, fmt, quality=quality)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    except Exception as e:
        raise ImageOutputError(f"Cannot save to '{path}': {e}") from e
    return path


def to_bytes(
    img: PILImage.Image,
    fmt: Format,
    *,
    quality: int | None = None,
) -> bytes:
    """Encode image and return raw bytes."""
    return encode(img, fmt, quality=quality)


def to_base64(
    img: PILImage.Image,
    fmt: Format,
    *,
    quality: int | None = None,
) -> str:
    """Encode image and return base64 string."""
    data = encode(img, fmt, quality=quality)
    return base64.b64encode(data).decode("ascii")


def to_data_uri(
    img: PILImage.Image,
    fmt: Format,
    *,
    quality: int | None = None,
) -> str:
    """Encode image and return a data URI."""
    b64 = to_base64(img, fmt, quality=quality)
    mime = mime_type(fmt)
    return f"data:{mime};base64,{b64}"


def to_response(
    img: PILImage.Image,
    fmt: Format,
    *,
    quality: int | None = None,
) -> dict:
    """Return a framework-agnostic HTTP response dict."""
    data = encode(img, fmt, quality=quality)
    return {
        "body": data,
        "content_type": mime_type(fmt),
        "content_length": len(data),
    }
