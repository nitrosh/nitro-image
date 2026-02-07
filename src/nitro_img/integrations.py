"""Framework integration helpers for Django, Flask, and FastAPI."""

from __future__ import annotations

from .types import Format
from .utils import mime_type
from .output.encode import encode

from PIL import Image as PILImage


def to_django_response(
    img: PILImage.Image,
    fmt: Format,
    *,
    quality: int | None = None,
    filename: str | None = None,
) -> object:
    """Create a Django HttpResponse with the image.

    Requires Django to be installed.
    """
    try:
        from django.http import HttpResponse
    except ImportError:
        raise ImportError(
            "Django is required for to_django_response(). "
            "Install with: pip install django"
        )

    data = encode(img, fmt, quality=quality)
    response = HttpResponse(data, content_type=mime_type(fmt))
    if filename:
        response["Content-Disposition"] = f'inline; filename="{filename}"'
    return response


def to_flask_response(
    img: PILImage.Image,
    fmt: Format,
    *,
    quality: int | None = None,
    filename: str | None = None,
) -> object:
    """Create a Flask Response with the image.

    Requires Flask to be installed.
    """
    try:
        from flask import Response
    except ImportError:
        raise ImportError(
            "Flask is required for to_flask_response(). "
            "Install with: pip install flask"
        )

    data = encode(img, fmt, quality=quality)
    headers = {}
    if filename:
        headers["Content-Disposition"] = f'inline; filename="{filename}"'
    return Response(data, mimetype=mime_type(fmt), headers=headers)


def to_fastapi_response(
    img: PILImage.Image,
    fmt: Format,
    *,
    quality: int | None = None,
    filename: str | None = None,
) -> object:
    """Create a FastAPI/Starlette Response with the image.

    Requires starlette to be installed (included with FastAPI).
    """
    try:
        from starlette.responses import Response
    except ImportError:
        raise ImportError(
            "Starlette/FastAPI is required for to_fastapi_response(). "
            "Install with: pip install fastapi"
        )

    data = encode(img, fmt, quality=quality)
    headers = {}
    if filename:
        headers["Content-Disposition"] = f'inline; filename="{filename}"'
    return Response(content=data, media_type=mime_type(fmt), headers=headers)
