"""Custom exception hierarchy for nitro-img."""


class NitroImgError(Exception):
    """Base exception for all nitro-img errors."""


class ImageLoadError(NitroImgError):
    """Cannot read or decode the input image."""


class ImageFormatError(NitroImgError):
    """Unsupported or invalid image format."""


class ImageSizeError(NitroImgError):
    """Image exceeds configured size limits."""


class ImageProcessingError(NitroImgError):
    """An operation failed during pipeline execution."""


class ImageOutputError(NitroImgError):
    """Cannot write or encode the output image."""
