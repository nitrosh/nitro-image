"""Tests for the lazy pipeline and chaining."""

from __future__ import annotations


from nitro_img import Image


class TestChaining:
    def test_full_chain(self, sample_jpg, tmp_output):
        out = tmp_output / "chained.webp"
        result = (
            Image(sample_jpg)
            .resize(400)
            .strip_metadata()
            .grayscale()
            .webp(quality=75)
            .save(out)
        )
        assert result.exists()

    def test_chain_resize_crop(self, sample_jpg):
        data = (
            Image(sample_jpg)
            .resize(600)
            .crop(200, 200)
            .jpeg()
            .to_bytes()
        )
        result = Image.from_bytes(data)
        assert result.width == 200
        assert result.height == 200

    def test_chain_transforms(self, sample_jpg):
        data = (
            Image(sample_jpg)
            .flip()
            .mirror()
            .grayscale()
            .jpeg()
            .to_bytes()
        )
        result = Image.from_bytes(data)
        assert result.width == 800
        assert result.height == 600

    def test_chain_rotate(self, sample_jpg):
        data = (
            Image(sample_jpg)
            .rotate(90)
            .jpeg()
            .to_bytes()
        )
        result = Image.from_bytes(data)
        # Rotated 90 degrees with expand, so dimensions swap
        assert result.width == 600
        assert result.height == 800


class TestLazyExecution:
    def test_operations_not_executed_until_output(self, sample_jpg):
        img = Image(sample_jpg)
        img.resize(400).grayscale()
        # Original should still be 800x600 (pipeline hasn't run)
        assert img.width == 800

    def test_pipeline_runs_on_save(self, sample_jpg, tmp_output):
        out = tmp_output / "lazy.jpg"
        img = Image(sample_jpg)
        img.resize(400)
        img.save(out)
        reloaded = Image(out)
        assert reloaded.width == 400
