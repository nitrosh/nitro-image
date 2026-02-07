"""Test fixtures: generate test images programmatically."""

from __future__ import annotations

import io
import base64
from pathlib import Path

import pytest
from PIL import Image as PILImage

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _make_rgb_image(width: int = 200, height: int = 150, color: tuple = (255, 0, 0)) -> PILImage.Image:
    return PILImage.new("RGB", (width, height), color)


def _make_rgba_image(width: int = 200, height: int = 150, color: tuple = (0, 0, 255, 128)) -> PILImage.Image:
    return PILImage.new("RGBA", (width, height), color)


@pytest.fixture
def fixtures_dir():
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    return FIXTURES_DIR


@pytest.fixture
def sample_jpg(fixtures_dir):
    path = fixtures_dir / "sample.jpg"
    img = _make_rgb_image(800, 600)
    img.save(path, "JPEG", quality=90)
    return path


@pytest.fixture
def sample_png(fixtures_dir):
    path = fixtures_dir / "sample.png"
    img = _make_rgba_image(800, 600)
    img.save(path, "PNG")
    return path


@pytest.fixture
def sample_webp(fixtures_dir):
    path = fixtures_dir / "sample.webp"
    img = _make_rgb_image(800, 600, (0, 255, 0))
    img.save(path, "WEBP", quality=80)
    return path


@pytest.fixture
def wide_image(fixtures_dir):
    """A wide panoramic image (1200x400)."""
    path = fixtures_dir / "wide.jpg"
    img = _make_rgb_image(1200, 400, (0, 128, 255))
    img.save(path, "JPEG")
    return path


@pytest.fixture
def tall_image(fixtures_dir):
    """A tall portrait image (400x1200)."""
    path = fixtures_dir / "tall.jpg"
    img = _make_rgb_image(400, 1200, (255, 128, 0))
    img.save(path, "JPEG")
    return path


@pytest.fixture
def small_image(fixtures_dir):
    """A small image (50x50) to test no-upscale behavior."""
    path = fixtures_dir / "small.jpg"
    img = _make_rgb_image(50, 50, (128, 128, 128))
    img.save(path, "JPEG")
    return path


@pytest.fixture
def sample_bytes():
    img = _make_rgb_image(200, 150)
    buf = io.BytesIO()
    img.save(buf, "JPEG")
    return buf.getvalue()


@pytest.fixture
def sample_base64(sample_bytes):
    return base64.b64encode(sample_bytes).decode("ascii")


@pytest.fixture
def tmp_output(tmp_path):
    return tmp_path
