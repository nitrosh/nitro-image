"""Lazy execution pipeline engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from PIL import Image as PILImage

from .errors import ImageProcessingError


@dataclass
class Operation:
    name: str
    fn: Callable[[PILImage.Image], PILImage.Image]
    kwargs: dict[str, Any] = field(default_factory=dict)


class Pipeline:
    def __init__(self) -> None:
        self._operations: list[Operation] = []

    def add(self, name: str, fn: Callable[[PILImage.Image], PILImage.Image], **kwargs: Any) -> None:
        self._operations.append(Operation(name=name, fn=fn, kwargs=kwargs))

    def execute(self, img: PILImage.Image) -> PILImage.Image:
        for op in self._operations:
            try:
                img = op.fn(img)
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
