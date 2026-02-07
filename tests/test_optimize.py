"""Tests for optimization and auto-format."""

from __future__ import annotations


from nitro_img import Image


class TestOptimize:
    def test_optimize_hits_target(self, sample_jpg):
        data = Image(sample_jpg).jpeg().optimize(target_kb=10)
        assert isinstance(data, bytes)
        assert len(data) <= 10 * 1024 + 512  # Allow small margin

    def test_optimize_large_target(self, sample_jpg):
        # If target is bigger than the image, should return max quality
        data = Image(sample_jpg).jpeg().optimize(target_kb=5000)
        assert len(data) > 0

    def test_optimize_webp(self, sample_jpg):
        data = Image(sample_jpg).webp().optimize(target_kb=10)
        assert data[:4] == b"RIFF"

    def test_optimize_with_pipeline(self, sample_jpg):
        data = (
            Image(sample_jpg)
            .resize(400)
            .grayscale()
            .jpeg()
            .optimize(target_kb=5)
        )
        assert len(data) <= 5 * 1024 + 512


class TestAutoFormat:
    def test_auto_format_opaque_image(self, sample_jpg):
        data = Image(sample_jpg).auto_format().to_bytes()
        assert isinstance(data, bytes)
        # Should pick JPEG or WebP for an opaque image
        assert data[:2] == b"\xff\xd8" or data[:4] == b"RIFF"

    def test_auto_format_transparent_image(self, sample_png):
        data = Image(sample_png).auto_format().to_bytes()
        # PNG has actual alpha, should stay PNG
        assert data[:4] == b"\x89PNG"

    def test_auto_format_data_uri(self, sample_jpg):
        uri = Image(sample_jpg).auto_format().to_data_uri()
        assert uri.startswith("data:image/")

    def test_auto_format_response(self, sample_jpg):
        resp = Image(sample_jpg).auto_format().to_response()
        assert "body" in resp
        assert resp["content_type"] in ("image/webp", "image/jpeg")

    def test_auto_format_save(self, sample_jpg, tmp_output):
        out = tmp_output / "auto_out"
        path = Image(sample_jpg).auto_format().save(out)
        assert path.exists()
        assert path.stat().st_size > 0
