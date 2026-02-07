"""Tests for crop operations."""

from __future__ import annotations


from nitro_img import Image


class TestCrop:
    def test_center_crop(self, sample_jpg):
        img = Image(sample_jpg).crop(400, 300)
        data = img.to_bytes()
        result = Image.from_bytes(data)
        assert result.width == 400
        assert result.height == 300

    def test_top_left_crop(self, sample_jpg):
        img = Image(sample_jpg).crop(200, 200, anchor="top-left")
        data = img.to_bytes()
        result = Image.from_bytes(data)
        assert result.width == 200
        assert result.height == 200

    def test_bottom_right_crop(self, sample_jpg):
        img = Image(sample_jpg).crop(200, 200, anchor="bottom-right")
        data = img.to_bytes()
        result = Image.from_bytes(data)
        assert result.width == 200
        assert result.height == 200

    def test_crop_larger_than_image(self, small_image):
        img = Image(small_image).crop(200, 200)
        data = img.jpeg().to_bytes()
        result = Image.from_bytes(data)
        # Should be clamped to original size
        assert result.width == 50
        assert result.height == 50
