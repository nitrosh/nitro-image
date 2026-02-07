"""Type definitions and enums for nitro-img."""

from __future__ import annotations

from enum import Enum
from typing import Literal


class Format(str, Enum):
    JPEG = "JPEG"
    PNG = "PNG"
    WEBP = "WEBP"
    GIF = "GIF"
    BMP = "BMP"
    TIFF = "TIFF"


class Position(str, Enum):
    CENTER = "center"
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"


class ResizeStrategy(str, Enum):
    FIT = "fit"
    COVER = "cover"
    CONTAIN = "contain"
    EXACT = "exact"


Anchor = Literal[
    "center", "top-left", "top-right", "bottom-left", "bottom-right",
    "top", "bottom", "left", "right",
]
