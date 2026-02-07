"""Tests for framework integration helpers.

Since we don't install Django/Flask/FastAPI in test deps,
we test that the import errors are raised properly, and we
test the underlying encode paths that they use.
"""

from __future__ import annotations

import pytest

from nitro_img import Image


class TestDjangoResponse:
    def test_django_not_installed(self, sample_jpg):
        with pytest.raises(ImportError, match="Django"):
            Image(sample_jpg).jpeg().to_django_response()


class TestFlaskResponse:
    def test_flask_not_installed(self, sample_jpg):
        with pytest.raises(ImportError, match="Flask"):
            Image(sample_jpg).jpeg().to_flask_response()


class TestFastAPIResponse:
    def test_fastapi_not_installed(self, sample_jpg):
        with pytest.raises(ImportError, match="Starlette"):
            Image(sample_jpg).jpeg().to_fastapi_response()


class TestIntegrationEncoding:
    """Verify integration helpers encode correctly by testing the shared path."""

    def test_to_response_dict_has_correct_fields(self, sample_jpg):
        resp = Image(sample_jpg).resize(200).jpeg().to_response()
        assert isinstance(resp["body"], bytes)
        assert resp["content_type"] == "image/jpeg"
        assert resp["content_length"] == len(resp["body"])

    def test_to_response_webp(self, sample_jpg):
        resp = Image(sample_jpg).webp().to_response()
        assert resp["content_type"] == "image/webp"

    def test_to_response_png(self, sample_jpg):
        resp = Image(sample_jpg).png().to_response()
        assert resp["content_type"] == "image/png"
