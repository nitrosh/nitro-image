"""Custom exception hierarchy for nitro-img."""


class NitroImgError(Exception):
    """Base class for every exception raised by nitro-img.

    Catch this to handle any library-originated failure in one except
    clause while letting unrelated exceptions propagate.
    """


class ImageLoadError(NitroImgError):
    """Raised when the source image cannot be read or decoded.

    Covers missing files, unreadable bytes, unsupported containers, and
    failed network fetches in ``Image.from_url``.
    """


class ImageFormatError(NitroImgError):
    """Raised when the output format is missing, invalid, or unsupported.

    Typically raised by output methods when no explicit format was set
    and none could be inferred from the save path or source image.
    """


class ImageSizeError(NitroImgError):
    """Raised when an image exceeds a configured size limit.

    Limits are controlled by ``config.max_input_size``,
    ``config.max_output_dimensions``, and ``config.url_max_size``.
    """


class ImageProcessingError(NitroImgError):
    """Raised when a queued pipeline operation fails during execution.

    Wraps the underlying exception so callers can distinguish operation
    failures from load/encode failures while retaining the cause chain.
    """


class ImageOutputError(NitroImgError):
    """Raised when the processed image cannot be written or encoded.

    Covers disk write errors, unsupported encoder combinations, and
    framework response construction failures.
    """
