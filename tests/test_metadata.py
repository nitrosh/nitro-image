"""Tests for metadata operations."""

from __future__ import annotations


from nitro_img import Image


class TestGetMetadata:
    def test_get_metadata(self, sample_jpg):
        img = Image(sample_jpg)
        meta = img.get_metadata()
        assert meta["width"] == 800
        assert meta["height"] == 600
        assert meta["mode"] == "RGB"


class TestStripMetadata:
    def test_strip_metadata(self, sample_jpg):
        data = (
            Image(sample_jpg)
            .strip_metadata()
            .jpeg()
            .to_bytes()
        )
        result = Image.from_bytes(data)
        assert result.width == 800
        assert result.height == 600
