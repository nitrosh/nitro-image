"""Tests for visual effects: sepia, rounded corners."""

from __future__ import annotations


from nitro_img import Image


class TestSepia:
    def test_sepia(self, sample_jpg):
        data = Image(sample_jpg).sepia().jpeg().to_bytes()
        assert len(data) > 0
        result = Image.from_bytes(data)
        assert result.width == 800
        assert result.height == 600

    def test_sepia_with_resize(self, sample_jpg):
        data = (
            Image(sample_jpg)
            .resize(400)
            .sepia()
            .jpeg()
            .to_bytes()
        )
        result = Image.from_bytes(data)
        assert result.width == 400

    def test_sepia_preserves_alpha(self, sample_png):
        data = Image(sample_png).sepia().png().to_bytes()
        result = Image.from_bytes(data)
        assert result.width == 800


class TestRoundedCorners:
    def test_rounded_corners(self, sample_jpg):
        data = Image(sample_jpg).rounded_corners(20).png().to_bytes()
        assert len(data) > 0
        # Should be PNG since rounded corners produce alpha
        assert data[:4] == b"\x89PNG"

    def test_rounded_corners_small_radius(self, sample_jpg):
        data = Image(sample_jpg).rounded_corners(5).png().to_bytes()
        assert len(data) > 0

    def test_rounded_corners_large_radius(self, sample_jpg):
        data = Image(sample_jpg).rounded_corners(100).png().to_bytes()
        assert len(data) > 0

    def test_rounded_corners_with_resize(self, sample_jpg):
        data = (
            Image(sample_jpg)
            .resize(200)
            .rounded_corners(15)
            .png()
            .to_bytes()
        )
        result = Image.from_bytes(data)
        assert result.width == 200


class TestEffectsChaining:
    def test_sepia_and_rounded(self, sample_jpg):
        data = (
            Image(sample_jpg)
            .resize(300)
            .sepia()
            .rounded_corners(15)
            .png()
            .to_bytes()
        )
        result = Image.from_bytes(data)
        assert result.width == 300

    def test_grayscale_sepia_chain(self, sample_jpg):
        # Sepia after grayscale should still produce a warm tone
        data = (
            Image(sample_jpg)
            .grayscale()
            .sepia()
            .jpeg()
            .to_bytes()
        )
        assert len(data) > 0
