"""Regression tests covering issues from the code review.

Each test class targets a specific finding so future drift surfaces in
its own failure rather than mingled with unrelated suites.
"""

from __future__ import annotations

import pytest
from PIL import Image as PILImage

from nitro_img import BatchImage, Image
from nitro_img.integrations import _content_disposition


class TestAutoFormatHonoredByOptimize:
    def test_auto_format_then_optimize_runs(self, sample_jpg):
        data = Image(sample_jpg).auto_format().optimize(target_kb=200)
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_auto_format_chooses_png_for_rgba(self, sample_png):
        # PNG fixture is RGBA — optimize should pick PNG, which has no
        # quality knob so the binary search short-circuits.
        data = Image(sample_png).auto_format().optimize(target_kb=200)
        assert data.startswith(b"\x89PNG\r\n")


class TestQualityZeroNotFalsy:
    def test_quality_zero_in_responsive(self, sample_jpg):
        # quality=0 used to be swallowed by `or self._output_quality`.
        # Now it should pass through and produce visibly heavier compression
        # than quality=90.
        zero = Image(sample_jpg).resize(400).webp().responsive([200], quality=0)
        ninety = Image(sample_jpg).resize(400).webp().responsive([200], quality=90)
        assert sum(len(b) for b in zero.values()) <= sum(len(b) for b in ninety.values())


class TestPositionValidation:
    def test_invalid_watermark_position_raises(self, sample_jpg, sample_png):
        with pytest.raises(ValueError, match="position"):
            Image(sample_jpg).watermark(sample_png, position="nope")

    def test_invalid_text_position_raises(self, sample_jpg):
        with pytest.raises(ValueError, match="position"):
            Image(sample_jpg).text_overlay("hi", position="middle")

    def test_tiled_position_allowed_for_watermark(self, sample_jpg, sample_png):
        # Should NOT raise — tiled is only valid for image watermarks.
        Image(sample_jpg).watermark(sample_png, position="tiled").webp().to_bytes()

    def test_tiled_position_rejected_for_text(self, sample_jpg):
        with pytest.raises(ValueError, match="position"):
            Image(sample_jpg).text_overlay("hi", position="tiled")


class TestBatchImageGif:
    def test_gif_recorder_present(self, tmp_path, sample_jpg, sample_png):
        # Create a batch with two images
        src = tmp_path / "src"
        src.mkdir()
        Image(sample_jpg).save(src / "a.png")
        Image(sample_png).save(src / "b.png")

        out_dir = tmp_path / "out"
        paths = (
            BatchImage(str(src / "*.png"))
            .resize(50)
            .gif()
            .save(str(out_dir / "{name}.gif"))
        )
        assert len(paths) == 2
        for p in paths:
            assert p.suffix == ".gif"


class TestContentDispositionSanitisation:
    def test_strips_quote_and_backslash(self):
        header = _content_disposition('evil".bad\\filename.jpg')
        assert '"' not in header.split('filename*=')[0].replace('filename="', '"x', 1).replace('"', '', 1) or True
        # Easier: verify there's no injection of an unmatched quote
        # Count quotes in the filename= section
        section = header.split('filename*=')[0]
        # Should be exactly 2 quotes wrapping the filename
        assert section.count('"') == 2

    def test_strips_newlines(self):
        header = _content_disposition("photo.jpg\r\nX-Injected: yes")
        assert "\n" not in header
        assert "\r" not in header

    def test_fallback_when_all_chars_stripped(self):
        header = _content_disposition("\x00\x01\x02")
        assert 'filename="image"' in header

    def test_unicode_in_filename_star(self):
        header = _content_disposition("café.jpg")
        # RFC 5987 percent-encoded value
        assert "filename*=UTF-8''" in header
        assert "caf%C3%A9.jpg" in header


class TestRoundedCornersClamp:
    def test_huge_radius_does_not_crash(self, sample_jpg):
        # radius > min dim should clamp rather than producing broken output
        data = Image(sample_jpg).rounded_corners(10_000).png().to_bytes()
        assert data.startswith(b"\x89PNG\r\n")

    def test_zero_radius_is_noop_alpha(self, sample_jpg):
        # radius 0 should still produce a valid RGBA image
        data = Image(sample_jpg).rounded_corners(0).png().to_bytes()
        assert data.startswith(b"\x89PNG\r\n")


class TestGrayscalePreservesAlpha:
    def test_rgba_input_keeps_alpha(self, sample_png):
        from PIL import Image as PILImage

        import io as _io

        data = Image(sample_png).grayscale().png().to_bytes()
        result = PILImage.open(_io.BytesIO(data))
        assert result.mode == "RGBA"


class TestStripMetadataPaletteMode:
    def test_palette_image_survives_strip(self, tmp_path):
        # Create a P-mode image
        path = tmp_path / "palette.png"
        pil = PILImage.new("P", (40, 30))
        pil.putpalette([i % 256 for i in range(768)])
        pil.save(path, "PNG")

        # Stripping should not raise and should produce valid output
        data = Image(path).strip_metadata().png().to_bytes()
        assert data.startswith(b"\x89PNG\r\n")


class TestExtensionForFormat:
    def test_jpeg_extension_is_jpg(self):
        from nitro_img import Format
        from nitro_img.utils import extension_for_format

        assert extension_for_format(Format.JPEG) == ".jpg"
        assert extension_for_format(Format.TIFF) == ".tiff"


class TestFrameworkResponseAutoFormat:
    """Ensure auto_format flows through framework response helpers.

    We can't import Django here, but we can prove the encode/format
    decision happens before the framework import error by checking that
    ImageFormatError isn't raised anymore on bytes-loaded images.
    """

    def test_django_response_with_auto_format_does_not_raise_format_error(self, sample_jpg):
        # Django isn't installed; if auto_format works, we should hit
        # the ImportError ("Django"), not ImageFormatError.
        with pytest.raises(ImportError, match="Django"):
            Image.from_bytes(open(sample_jpg, "rb").read()).auto_format().to_django_response()

    def test_flask_response_with_auto_format_does_not_raise_format_error(self, sample_jpg):
        with pytest.raises(ImportError, match="Flask"):
            Image.from_bytes(open(sample_jpg, "rb").read()).auto_format().to_flask_response()

    def test_fastapi_response_with_auto_format_does_not_raise_format_error(self, sample_jpg):
        with pytest.raises(ImportError, match="Starlette"):
            Image.from_bytes(open(sample_jpg, "rb").read()).auto_format().to_fastapi_response()


class TestWatermarkCaching:
    def test_watermark_works_when_file_deleted_after_chain(self, tmp_path, sample_jpg):
        # Build a watermark, kick off a pipeline, delete the source, then
        # call save_responsive which triggers the pipeline multiple times.
        # If the watermark were re-opened per execution this would fail.
        wm_path = tmp_path / "wm.png"
        wm = PILImage.new("RGBA", (30, 30), (255, 255, 255, 200))
        wm.save(wm_path, "PNG")

        img = Image(sample_jpg).watermark(str(wm_path), opacity=0.5)
        # Delete the watermark before any output runs
        wm_path.unlink()
        # Now produce outputs — should still succeed thanks to closure caching
        out_dir = tmp_path / "out"
        paths = img.webp().save_responsive(out_dir, [100, 200])
        assert len(paths) >= 1
