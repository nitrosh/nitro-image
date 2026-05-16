"""Lazy execution pipeline engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PIL import Image as PILImage

from .errors import ImageProcessingError, NitroImgError


@dataclass
class Operation:
    name: str
    fn: Callable[[PILImage.Image], PILImage.Image]


class Pipeline:
    def __init__(self) -> None:
        self._operations: list[Operation] = []

    def add(self, name: str, fn: Callable[[PILImage.Image], PILImage.Image]) -> None:
        self._operations.append(Operation(name=name, fn=fn))

    def execute(self, img: PILImage.Image) -> PILImage.Image:
        for op in self._operations:
            try:
                img = op.fn(img)
            except NitroImgError:
                # Library-level errors (size caps, validation, etc.) carry
                # their own meaning - don't disguise them as pipeline failures.
                raise
            except Exception as e:
                raise ImageProcessingError(
                    f"Operation '{op.name}' failed: {e}"
                ) from e
        return img

    def __len__(self) -> int:
        return len(self._operations)

    def __repr__(self) -> str:
        ops = ", ".join(op.name for op in self._operations)
        return f"Pipeline([{ops}])"
