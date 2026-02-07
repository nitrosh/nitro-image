"""Tests for output/export functionality."""

from __future__ import annotations

import base64


from nitro_img import Image


class TestSave:
    def test_save_jpeg(self, sample_jpg, tmp_output):
        out = tmp_output / "out.jpg"
        result = Image(sample_jpg).resize(400).save(out)
        assert result.exists()
        assert result.stat().st_size > 0

    def test_save_png(self, sample_jpg, tmp_output):
        out = tmp_output / "out.png"
        Image(sample_jpg).resize(400).save(out)
        assert out.exists()

    def test_save_webp(self, sample_jpg, tmp_output):
        out = tmp_output / "out.webp"
        Image(sample_jpg).resize(400).save(out)
        assert out.exists()

    def test_save_creates_directories(self, sample_jpg, tmp_output):
        out = tmp_output / "sub" / "dir" / "out.jpg"
        Image(sample_jpg).save(out)
        assert out.exists()

    def test_save_with_explicit_format(self, sample_jpg, tmp_output):
        out = tmp_output / "out.bin"
        Image(sample_jpg).webp(quality=70).save(out)
        assert out.exists()


class TestToBytes:
    def test_to_bytes_jpeg(self, sample_jpg):
        data = Image(sample_jpg).jpeg().to_bytes()
        assert isinstance(data, bytes)
        assert len(data) > 0
        # JPEG magic bytes
        assert data[:2] == b"\xff\xd8"

    def test_to_bytes_png(self, sample_jpg):
        data = Image(sample_jpg).png().to_bytes()
        assert data[:4] == b"\x89PNG"

    def test_to_bytes_webp(self, sample_jpg):
        data = Image(sample_jpg).webp().to_bytes()
        assert data[:4] == b"RIFF"


class TestToBase64:
    def test_to_base64(self, sample_jpg):
        b64 = Image(sample_jpg).jpeg().to_base64()
        assert isinstance(b64, str)
        # Should be valid base64
        data = base64.b64decode(b64)
        assert data[:2] == b"\xff\xd8"


class TestToDataUri:
    def test_to_data_uri_jpeg(self, sample_jpg):
        uri = Image(sample_jpg).jpeg().to_data_uri()
        assert uri.startswith("data:image/jpeg;base64,")

    def test_to_data_uri_webp(self, sample_jpg):
        uri = Image(sample_jpg).webp().to_data_uri()
        assert uri.startswith("data:image/webp;base64,")


class TestToResponse:
    def test_to_response(self, sample_jpg):
        resp = Image(sample_jpg).jpeg().to_response()
        assert "body" in resp
        assert resp["content_type"] == "image/jpeg"
        assert resp["content_length"] > 0
        assert isinstance(resp["body"], bytes)
