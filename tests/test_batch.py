"""Tests for batch processing."""

from __future__ import annotations


import pytest
from PIL import Image as PILImage

from nitro_img import Image, ImageLoadError
from nitro_img.batch import BatchImage


@pytest.fixture
def batch_images(fixtures_dir):
    """Create several test images for batch processing."""
    for i in range(3):
        img = PILImage.new("RGB", (800, 600), (i * 80, 100, 200))
        img.save(fixtures_dir / f"batch_{i}.jpg", "JPEG")
    return str(fixtures_dir / "batch_*.jpg")


class TestBatchProcessing:
    def test_batch_load(self, batch_images):
        batch = BatchImage(batch_images)
        assert batch.count == 3

    def test_batch_no_match(self):
        with pytest.raises(ImageLoadError, match="No files matched"):
            BatchImage("/nonexistent/*.xyz")

    def test_batch_save(self, batch_images, tmp_output):
        results = (
            BatchImage(batch_images)
            .resize(400)
            .jpeg(quality=80)
            .save(str(tmp_output / "{name}.jpg"))
        )
        assert len(results) == 3
        for p in results:
            assert p.exists()
            reloaded = Image(p)
            assert reloaded.width == 400

    def test_batch_format_conversion(self, batch_images, tmp_output):
        results = (
            BatchImage(batch_images)
            .resize(200)
            .webp(quality=70)
            .save(str(tmp_output / "{name}.webp"))
        )
        assert len(results) == 3
        for p in results:
            assert p.suffix == ".webp"

    def test_batch_chain(self, batch_images, tmp_output):
        results = (
            BatchImage(batch_images)
            .resize(300)
            .grayscale()
            .strip_metadata()
            .jpeg()
            .save(str(tmp_output / "{name}_processed.jpg"))
        )
        assert len(results) == 3
