"""Framework integration helpers.

Each of these lazily imports the framework it needs, so you only pay for
the integration you actually use. This file shows how you'd call them —
not every framework is installed here, so we guard each call.

    Image("photo.jpg").resize(400).webp().to_django_response()
    Image("photo.jpg").resize(400).webp().to_flask_response()
    Image("photo.jpg").resize(400).webp().to_fastapi_response()
"""

from __future__ import annotations

from nitro_img import Image

from _sample import banner, photo


def _try(label: str, fn) -> None:
    try:
        result = fn()
        print(f"{label}: {type(result).__module__}.{type(result).__name__}")
    except ImportError as exc:
        print(f"{label}: skipped - {exc.name} not installed")
    except Exception as exc:
        # Django needs a settings module; Flask needs an app context, etc.
        # The helper itself ran — we just can't instantiate the response.
        print(f"{label}: framework present but not configured ({exc.__class__.__name__})")


def main() -> None:
    banner("14 - Framework integrations")
    src = photo()

    base = Image(src).resize(400).webp()
    _try("Django  ", lambda: base.to_django_response(filename="photo.webp"))
    _try("Flask   ", lambda: base.to_flask_response(filename="photo.webp"))
    _try("FastAPI ", lambda: base.to_fastapi_response(filename="photo.webp"))

    # For a framework-agnostic path, .to_response() returns a plain dict
    # that any web stack can turn into a response.
    generic = Image(src).resize(400).webp().to_response()
    print(
        "Generic to_response(): "
        f"content_type={generic['content_type']}, "
        f"content_length={generic['content_length']}"
    )


if __name__ == "__main__":
    main()
