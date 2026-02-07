"""Format detection, dimension helpers, and validators."""

from __future__ import annotations

import os
from pathlib import Path

from .types import Format

_EXT_TO_FORMAT: dict[str, Format] = {
    ".jpg": Format.JPEG,
    ".jpeg": Format.JPEG,
    ".png": Format.PNG,
    ".webp": Format.WEBP,
    ".gif": Format.GIF,
    ".bmp": Format.BMP,
    ".tiff": Format.TIFF,
    ".tif": Format.TIFF,
}

_PILLOW_TO_FORMAT: dict[str, Format] = {
    "JPEG": Format.JPEG,
    "PNG": Format.PNG,
    "WEBP": Format.WEBP,
    "GIF": Format.GIF,
    "BMP": Format.BMP,
    "TIFF": Format.TIFF,
    "MPO": Format.JPEG,
}

_FORMAT_TO_MIME: dict[Format, str] = {
    Format.JPEG: "image/jpeg",
    Format.PNG: "image/png",
    Format.WEBP: "image/webp",
    Format.GIF: "image/gif",
    Format.BMP: "image/bmp",
    Format.TIFF: "image/tiff",
}


def format_from_extension(path: str | Path) -> Format | None:
    ext = os.path.splitext(str(path))[1].lower()
    return _EXT_TO_FORMAT.get(ext)


def format_from_pillow(pillow_format: str | None) -> Format | None:
    if pillow_format is None:
        return None
    return _PILLOW_TO_FORMAT.get(pillow_format.upper())


def mime_type(fmt: Format) -> str:
    return _FORMAT_TO_MIME.get(fmt, "application/octet-stream")


def extension_for_format(fmt: Format) -> str:
    for ext, f in _EXT_TO_FORMAT.items():
        if f == fmt:
            return ext
    return ".bin"
