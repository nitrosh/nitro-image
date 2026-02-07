"""Tests for resize operations."""

from __future__ import annotations


from nitro_img import Image


class TestResize:
    def test_resize_width_only(self, sample_jpg):
        img = Image(sample_jpg).resize(400)
        data = img.to_bytes()
        result = Image.from_bytes(data)
        assert result.width == 400
        assert result.height == 300  # 800x600 -> 400x300

    def test_resize_height_only(self, sample_jpg):
        img = Image(sample_jpg).resize(height=300)
        data = img.to_bytes()
        result = Image.from_bytes(data)
        assert result.width == 400
        assert result.height == 300

    def test_resize_both_dimensions_fit(self, sample_jpg):
        img = Image(sample_jpg).resize(400, 400)
        data = img.to_bytes()
        result = Image.from_bytes(data)
        # Should fit within 400x400, preserving aspect ratio (800x600 -> 400x300)
        assert result.width == 400
        assert result.height == 300

    def test_resize_no_upscale_by_default(self, small_image):
        img = Image(small_image).resize(200)
        data = img.jpeg().to_bytes()
        result = Image.from_bytes(data)
        assert result.width == 50  # Should not upscale from 50

    def test_resize_allow_upscale(self, small_image):
        img = Image(small_image).resize(200, allow_upscale=True)
        data = img.jpeg().to_bytes()
        result = Image.from_bytes(data)
        assert result.width == 200


class TestThumbnail:
    def test_thumbnail(self, sample_jpg):
        img = Image(sample_jpg).thumbnail(200, 200)
        data = img.to_bytes()
        result = Image.from_bytes(data)
        assert result.width <= 200
        assert result.height <= 200
        # 800x600 -> 200x150
        assert result.width == 200
        assert result.height == 150

    def test_thumbnail_no_upscale(self, small_image):
        img = Image(small_image).thumbnail(200, 200)
        data = img.jpeg().to_bytes()
        result = Image.from_bytes(data)
        assert result.width == 50


class TestCover:
    def test_cover_landscape(self, sample_jpg):
        img = Image(sample_jpg).cover(200, 200)
        data = img.to_bytes()
        result = Image.from_bytes(data)
        assert result.width == 200
        assert result.height == 200

    def test_cover_wide_image(self, wide_image):
        img = Image(wide_image).cover(300, 300)
        data = img.to_bytes()
        result = Image.from_bytes(data)
        assert result.width == 300
        assert result.height == 300


class TestContain:
    def test_contain_with_padding(self, sample_jpg):
        img = Image(sample_jpg).contain(400, 400)
        data = img.to_bytes()
        result = Image.from_bytes(data)
        # Canvas should be exactly 400x400
        assert result.width == 400
        assert result.height == 400

    def test_contain_png_rgba(self, sample_png):
        img = Image(sample_png).contain(400, 400)
        data = img.png().to_bytes()
        result = Image.from_bytes(data)
        assert result.width == 400
        assert result.height == 400
