"""Tests for Image.from_url and the URL streaming loader.

These tests stub httpx so no real network calls are made.
"""

from __future__ import annotations

import io
import sys
from types import SimpleNamespace

import pytest
from PIL import Image as PILImage

from nitro_img import Image, ImageLoadError, ImageSizeError, config


class _FakeResponse:
    def __init__(self, body: bytes, status_code: int = 200, headers: dict | None = None):
        self._body = body
        self.status_code = status_code
        self.headers = headers or {}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def iter_bytes(self):
        # Yield in two chunks so streaming behavior is exercised.
        mid = len(self._body) // 2
        if mid > 0:
            yield self._body[:mid]
        yield self._body[mid:]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def _png_bytes(w: int = 40, h: int = 30) -> bytes:
    img = PILImage.new("RGB", (w, h), (10, 20, 30))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


@pytest.fixture
def fake_httpx(monkeypatch):
    body_ref = {"body": _png_bytes(), "headers": {}}

    def fake_stream(method, url, **kwargs):
        return _FakeResponse(body_ref["body"], headers=body_ref["headers"])

    fake = SimpleNamespace(stream=fake_stream)
    monkeypatch.setitem(sys.modules, "httpx", fake)
    return body_ref


class TestFromUrlHappyPath:
    def test_loads_png_from_url(self, fake_httpx):
        img = Image.from_url("https://example.com/photo.png")
        assert img.width == 40
        assert img.height == 30

    def test_streaming_aggregates_chunks(self, fake_httpx):
        fake_httpx["body"] = _png_bytes(120, 80)
        img = Image.from_url("https://example.com/big.png")
        assert img.size == (120, 80)


class TestFromUrlSchemeAllowlist:
    def test_file_scheme_rejected(self, fake_httpx):
        with pytest.raises(ImageLoadError, match="scheme"):
            Image.from_url("file:///etc/passwd")

    def test_ftp_scheme_rejected(self, fake_httpx):
        with pytest.raises(ImageLoadError, match="scheme"):
            Image.from_url("ftp://example.com/photo.jpg")

    def test_custom_allowlist(self, fake_httpx, monkeypatch):
        original = config.url_allowed_schemes
        config.update(url_allowed_schemes=("http",))
        try:
            with pytest.raises(ImageLoadError, match="scheme"):
                Image.from_url("https://example.com/photo.png")
        finally:
            config.update(url_allowed_schemes=original)


class TestFromUrlSizeCap:
    def test_streaming_aborts_when_over_cap(self, fake_httpx):
        original = config.url_max_size
        config.update(url_max_size=10)
        try:
            with pytest.raises(ImageSizeError, match="aborted|exceeds"):
                Image.from_url("https://example.com/photo.png")
        finally:
            config.update(url_max_size=original)

    def test_content_length_header_short_circuits(self, fake_httpx):
        original = config.url_max_size
        config.update(url_max_size=50)
        try:
            fake_httpx["headers"] = {"Content-Length": "10000"}
            with pytest.raises(ImageSizeError, match="declares"):
                Image.from_url("https://example.com/photo.png")
        finally:
            config.update(url_max_size=original)


class TestFromUrlHttpxMissing:
    def test_missing_httpx_raises_clear_error(self, monkeypatch):
        # Make the import fail.
        monkeypatch.setitem(sys.modules, "httpx", None)
        with pytest.raises(ImageLoadError, match="httpx"):
            Image.from_url("https://example.com/photo.png")
