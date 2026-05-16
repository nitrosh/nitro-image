"""Framework integration helpers for Django, Flask, and FastAPI.

The public entry points are :meth:`Image.to_django_response`,
:meth:`Image.to_flask_response`, and :meth:`Image.to_fastapi_response`.
Helpers in this module accept already-encoded bytes plus the chosen
:class:`Format` so the ``auto_format`` decision can flow through to the
response Content-Type without re-encoding the image.
"""

from __future__ import annotations

from urllib.parse import quote

from .types import Format
from .utils import mime_type


def _content_disposition(filename: str) -> str:
    """Build a safe ``Content-Disposition`` header value (RFC 6266).

    Strips control characters and quote/backslash from the ASCII
    fallback, and pairs it with an RFC 5987 ``filename*`` so non-ASCII
    names round-trip without breaking the header.
    """
    cleaned = "".join(
        ch for ch in filename if 32 <= ord(ch) < 127 and ch not in '"\\'
    )
    if not cleaned:
        cleaned = "image"
    encoded = quote(filename, safe="")
    return f'inline; filename="{cleaned}"; filename*=UTF-8\'\'{encoded}'


def _build_response_for_django(
    data: bytes,
    fmt: Format,
    *,
    filename: str | None = None,
) -> object:
    try:
        from django.http import HttpResponse
    except ImportError:
        raise ImportError(
            "Django is required for to_django_response(). "
            "Install with: pip install django"
        )
    response = HttpResponse(data, content_type=mime_type(fmt))
    if filename:
        response["Content-Disposition"] = _content_disposition(filename)
    return response


def _build_response_for_flask(
    data: bytes,
    fmt: Format,
    *,
    filename: str | None = None,
) -> object:
    try:
        from flask import Response
    except ImportError:
        raise ImportError(
            "Flask is required for to_flask_response(). "
            "Install with: pip install flask"
        )
    headers = {}
    if filename:
        headers["Content-Disposition"] = _content_disposition(filename)
    return Response(data, mimetype=mime_type(fmt), headers=headers)


def _build_response_for_fastapi(
    data: bytes,
    fmt: Format,
    *,
    filename: str | None = None,
) -> object:
    try:
        from starlette.responses import Response
    except ImportError:
        raise ImportError(
            "Starlette/FastAPI is required for to_fastapi_response(). "
            "Install with: pip install fastapi"
        )
    headers = {}
    if filename:
        headers["Content-Disposition"] = _content_disposition(filename)
    return Response(content=data, media_type=mime_type(fmt), headers=headers)
