"""Tests for responsive image generation."""

from __future__ import annotations

from nitro_img import Image, Format


class TestResponsive:
    def test_responsive_returns_dict(self, sample_jpg):
        img = Image(sample_jpg)
        sizes = img.responsive(widths=[200, 400, 800])
        assert isinstance(sizes, dict)
        assert len(sizes) == 3
        for width, data in sizes.items():
            assert isinstance(width, int)
            assert isinstance(data, bytes)
            assert len(data) > 0

    def test_responsive_no_upscale(self, sample_jpg):
        # Image is 800px wide, 1600 should be capped to 800
        sizes = Image(sample_jpg).responsive(widths=[400, 800, 1600])
        widths = sorted(sizes.keys())
        assert widths[0] == 400
        assert widths[1] == 800
        # 1600 gets capped to 800 which already exists, so dict has 2 keys
        assert len(widths) == 2

    def test_responsive_with_format(self, sample_jpg):
        sizes = Image(sample_jpg).responsive(widths=[200], fmt=Format.JPEG)
        data = list(sizes.values())[0]
        assert data[:2] == b"\xff\xd8"  # JPEG magic

    def test_responsive_default_widths(self, sample_jpg):
        sizes = Image(sample_jpg).responsive()
        # Default widths: [320, 640, 1024, 1920]
        # Image is 800px wide, so 1024 and 1920 are capped to 800
        assert len(sizes) >= 2

    def test_responsive_with_pipeline(self, sample_jpg):
        sizes = (
            Image(sample_jpg)
            .grayscale()
            .strip_metadata()
            .responsive(widths=[200, 400])
        )
        assert len(sizes) == 2


class TestSaveResponsive:
    def test_save_responsive(self, sample_jpg, tmp_output):
        paths = Image(sample_jpg).save_responsive(
            tmp_output, widths=[200, 400], name="hero"
        )
        assert len(paths) == 2
        for width, path in paths.items():
            assert path.exists()
            assert "hero_" in path.name

    def test_save_responsive_auto_name(self, sample_jpg, tmp_output):
        paths = Image(sample_jpg).save_responsive(
            tmp_output, widths=[300]
        )
        # Should use source filename stem
        path = list(paths.values())[0]
        assert "sample_" in path.name

    def test_save_responsive_jpeg(self, sample_jpg, tmp_output):
        paths = Image(sample_jpg).save_responsive(
            tmp_output, widths=[200], fmt=Format.JPEG
        )
        path = list(paths.values())[0]
        assert path.suffix == ".jpg"
