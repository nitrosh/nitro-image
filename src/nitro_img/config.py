"""Global configuration with sensible defaults."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Config:
    max_input_size: int = 50_000_000       # 50 MB
    max_output_dimensions: int = 10_000    # 10k px
    default_jpeg_quality: int = 85
    default_webp_quality: int = 80
    default_png_compression: int = 6
    allow_upscale: bool = False
    auto_orient: bool = True
    strip_metadata: bool = False
    url_timeout: float = 30.0
    url_max_size: int = 50_000_000         # 50 MB

    def update(self, **kwargs: object) -> None:
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise ValueError(f"Unknown config option: {key}")
            setattr(self, key, value)


config = Config()
