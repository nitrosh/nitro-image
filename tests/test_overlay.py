"""Tests for watermark and text overlay operations."""

from __future__ import annotations


import pytest
from PIL import Image as PILImage

from nitro_img import Image


@pytest.fixture
def watermark_img(fixtures_dir):
    """A small semi-transparent watermark image."""
    path = fixtures_dir / "watermark.png"
    wm = PILImage.new("RGBA", (100, 50), (255, 255, 255, 128))
    wm.save(path, "PNG")
    return path


class TestWatermark:
    def test_watermark_from_path(self, sample_jpg, watermark_img):
        data = (
            Image(sample_jpg)
            .watermark(str(watermark_img), position="bottom-right", opacity=0.5)
            .jpeg()
            .to_bytes()
        )
        result = Image.from_bytes(data)
        assert result.width == 800
        assert result.height == 600

    def test_watermark_from_pil_image(self, sample_jpg):
        wm = PILImage.new("RGBA", (80, 40), (255, 0, 0, 128))
        data = (
            Image(sample_jpg)
            .watermark(wm, position="center", opacity=0.3)
            .jpeg()
            .to_bytes()
        )
        result = Image.from_bytes(data)
        assert result.width == 800

    def test_watermark_positions(self, sample_jpg, watermark_img):
        for pos in ["center", "top-left", "top-right", "bottom-left", "bottom-right"]:
            data = (
                Image(sample_jpg)
                .watermark(str(watermark_img), position=pos, opacity=0.5)
                .jpeg()
                .to_bytes()
            )
            assert len(data) > 0

    def test_watermark_tiled(self, sample_jpg, watermark_img):
        data = (
            Image(sample_jpg)
            .watermark(str(watermark_img), position="tiled", opacity=0.2)
            .jpeg()
            .to_bytes()
        )
        result = Image.from_bytes(data)
        assert result.width == 800

    def test_watermark_with_scale(self, sample_jpg, watermark_img):
        data = (
            Image(sample_jpg)
            .watermark(str(watermark_img), scale=0.25, opacity=0.5)
            .jpeg()
            .to_bytes()
        )
        assert len(data) > 0


class TestTextOverlay:
    def test_text_overlay(self, sample_jpg):
        data = (
            Image(sample_jpg)
            .text_overlay("Hello World", position="center", font_size=36)
            .jpeg()
            .to_bytes()
        )
        result = Image.from_bytes(data)
        assert result.width == 800

    def test_text_overlay_positions(self, sample_jpg):
        for pos in ["center", "top-left", "bottom-right"]:
            data = (
                Image(sample_jpg)
                .text_overlay("Test", position=pos, color="red")
                .jpeg()
                .to_bytes()
            )
            assert len(data) > 0

    def test_text_overlay_with_opacity(self, sample_jpg):
        data = (
            Image(sample_jpg)
            .text_overlay("Faded", position="center", opacity=0.5)
            .jpeg()
            .to_bytes()
        )
        assert len(data) > 0

    def test_watermark_and_text_chain(self, sample_jpg):
        wm = PILImage.new("RGBA", (80, 40), (255, 255, 255, 128))
        data = (
            Image(sample_jpg)
            .resize(600)
            .watermark(wm, position="bottom-right", opacity=0.3)
            .text_overlay("Copyright", position="bottom-left", font_size=16)
            .jpeg()
            .to_bytes()
        )
        result = Image.from_bytes(data)
        assert result.width == 600
