"""Tests for parallel batch processing."""

from __future__ import annotations


import pytest
from PIL import Image as PILImage

from nitro_img import Image
from nitro_img.batch import BatchImage


@pytest.fixture
def parallel_images(fixtures_dir):
    """Create 6 test images for parallel processing."""
    for i in range(6):
        img = PILImage.new("RGB", (400, 300), (i * 40, 100, 200))
        img.save(fixtures_dir / f"parallel_{i}.jpg", "JPEG")
    return str(fixtures_dir / "parallel_*.jpg")


class TestParallelBatch:
    def test_parallel_save(self, parallel_images, tmp_output):
        results = (
            BatchImage(parallel_images)
            .resize(200)
            .jpeg()
            .save(str(tmp_output / "{name}.jpg"), parallel=True)
        )
        assert len(results) == 6
        for p in results:
            assert p.exists()
            reloaded = Image(p)
            assert reloaded.width == 200

    def test_parallel_matches_sequential(self, parallel_images, tmp_output):
        seq_dir = tmp_output / "seq"
        par_dir = tmp_output / "par"
        seq_dir.mkdir()
        par_dir.mkdir()

        seq_results = (
            BatchImage(parallel_images)
            .resize(200)
            .jpeg(quality=80)
            .save(str(seq_dir / "{name}.jpg"), parallel=False)
        )
        par_results = (
            BatchImage(parallel_images)
            .resize(200)
            .jpeg(quality=80)
            .save(str(par_dir / "{name}.jpg"), parallel=True)
        )

        assert len(seq_results) == len(par_results)
        # Both should produce files with same names
        seq_names = sorted(p.name for p in seq_results)
        par_names = sorted(p.name for p in par_results)
        assert seq_names == par_names

    def test_parallel_with_max_workers(self, parallel_images, tmp_output):
        results = (
            BatchImage(parallel_images)
            .resize(100)
            .jpeg()
            .save(str(tmp_output / "{name}.jpg"), parallel=True, max_workers=2)
        )
        assert len(results) == 6

    def test_parallel_preserves_order(self, parallel_images, tmp_output):
        results = (
            BatchImage(parallel_images)
            .resize(200)
            .jpeg()
            .save(str(tmp_output / "{name}.jpg"), parallel=True)
        )
        # Results should be ordered by input order (parallel_0, parallel_1, ...)
        names = [p.stem for p in results]
        assert names == sorted(names)

    def test_parallel_with_effects(self, parallel_images, tmp_output):
        results = (
            BatchImage(parallel_images)
            .resize(200)
            .brightness(1.2)
            .contrast(1.1)
            .grayscale()
            .jpeg()
            .save(str(tmp_output / "{name}.jpg"), parallel=True)
        )
        assert len(results) == 6
