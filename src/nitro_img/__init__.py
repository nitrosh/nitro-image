"""nitro-img: Fast, friendly image processing for web apps and SaaS."""

from .image import Image
from .batch import BatchImage
from .config import config
from .presets import presets
from .errors import (
    NitroImgError,
    ImageFormatError,
    ImageLoadError,
    ImageOutputError,
    ImageProcessingError,
    ImageSizeError,
)
from .types import Format, Position, ResizeStrategy

__version__ = "0.3.0"

__all__ = [
    "Image",
    "BatchImage",
    "config",
    "presets",
    "Format",
    "Position",
    "ResizeStrategy",
    "NitroImgError",
    "ImageFormatError",
    "ImageLoadError",
    "ImageOutputError",
    "ImageProcessingError",
    "ImageSizeError",
]
