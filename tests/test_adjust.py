"""Tests for adjustment operations: brightness, contrast, saturation, sharpen, blur."""

from __future__ import annotations


from nitro_img import Image


class TestBrightness:
    def test_brighten(self, sample_jpg):
        data = Image(sample_jpg).brightness(1.5).jpeg().to_bytes()
        assert len(data) > 0

    def test_darken(self, sample_jpg):
        data = Image(sample_jpg).brightness(0.5).jpeg().to_bytes()
        assert len(data) > 0

    def test_brightness_unchanged(self, sample_jpg):
        data = Image(sample_jpg).brightness(1.0).jpeg().to_bytes()
        assert len(data) > 0


class TestContrast:
    def test_increase_contrast(self, sample_jpg):
        data = Image(sample_jpg).contrast(1.5).jpeg().to_bytes()
        assert len(data) > 0

    def test_decrease_contrast(self, sample_jpg):
        data = Image(sample_jpg).contrast(0.5).jpeg().to_bytes()
        assert len(data) > 0


class TestSaturation:
    def test_saturate(self, sample_jpg):
        data = Image(sample_jpg).saturation(2.0).jpeg().to_bytes()
        assert len(data) > 0

    def test_desaturate(self, sample_jpg):
        data = Image(sample_jpg).saturation(0.0).jpeg().to_bytes()
        assert len(data) > 0


class TestSharpen:
    def test_sharpen(self, sample_jpg):
        data = Image(sample_jpg).sharpen(2.0).jpeg().to_bytes()
        assert len(data) > 0

    def test_sharpen_default(self, sample_jpg):
        data = Image(sample_jpg).sharpen().jpeg().to_bytes()
        assert len(data) > 0


class TestBlur:
    def test_blur(self, sample_jpg):
        data = Image(sample_jpg).blur(5.0).jpeg().to_bytes()
        assert len(data) > 0

    def test_blur_default(self, sample_jpg):
        data = Image(sample_jpg).blur().jpeg().to_bytes()
        assert len(data) > 0

    def test_blur_subtle(self, sample_jpg):
        data = Image(sample_jpg).blur(0.5).jpeg().to_bytes()
        assert len(data) > 0


class TestAdjustmentChaining:
    def test_full_adjustment_chain(self, sample_jpg):
        data = (
            Image(sample_jpg)
            .resize(400)
            .brightness(1.2)
            .contrast(1.1)
            .saturation(1.3)
            .sharpen(1.5)
            .jpeg()
            .to_bytes()
        )
        result = Image.from_bytes(data)
        assert result.width == 400

    def test_blur_then_sharpen(self, sample_jpg):
        data = (
            Image(sample_jpg)
            .blur(3.0)
            .sharpen(3.0)
            .jpeg()
            .to_bytes()
        )
        assert len(data) > 0
