"""Type definitions and enums for nitro-img."""

from __future__ import annotations

from enum import Enum
from typing import Literal


class Format(str, Enum):
    """Image format identifier used throughout the public API.

    Members correspond to Pillow's format strings, so ``Format.JPEG.value``
    is ``"JPEG"``. Accept the enum or a plain string wherever a format
    argument is taken.

    Example:
        >>> from nitro_img import Image, Format
        >>> Image("photo.jpg").format(Format.WEBP).save("photo.webp")
    """

    JPEG = "JPEG"
    PNG = "PNG"
    WEBP = "WEBP"
    GIF = "GIF"
    BMP = "BMP"
    TIFF = "TIFF"


class Position(str, Enum):
    """Anchor position for crops, watermarks, and text overlays.

    Values are the same kebab-case strings accepted by the string-typed
    ``anchor`` / ``position`` parameters across the API, so either the
    enum or its string value can be passed.

    Example:
        >>> from nitro_img import Image, Position
        >>> Image("photo.jpg").crop(400, 400, anchor=Position.TOP_LEFT)
    """

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
    """How a resize operation fits the source into target dimensions.

    Most users invoke strategies by calling the dedicated ``Image``
    methods (``resize``, ``cover``, ``contain``); this enum exists for
    integrations that select a strategy dynamically.

    Members:
        FIT: Scale to fit within the box, preserving aspect ratio.
        COVER: Fill the box, centre-cropping any overflow.
        CONTAIN: Fit within the box, padding remaining space.
        EXACT: Resize to the exact dimensions, ignoring aspect ratio.
    """

    FIT = "fit"
    COVER = "cover"
    CONTAIN = "contain"
    EXACT = "exact"


Anchor = Literal[
    "center", "top-left", "top-right", "bottom-left", "bottom-right",
    "top", "bottom", "left", "right",
]
