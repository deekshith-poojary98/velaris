"""filesystem capability providers (external stress-test plugin)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from velaris_core.sdk import Registry, Teardown, capability_observed, pop_emit

from filesystem.contract import Filesystem


class MemoryFilesystem:
    """In-memory path → content map."""

    def __init__(
        self,
        files: dict[str, str],
        emit: Callable[[object], None] | None = None,
    ) -> None:
        self._files = dict(files)
        self._emit = emit

    def read_text(self, path: str) -> str:
        if path not in self._files:
            raise FileNotFoundError(path)
        content = self._files[path]
        if self._emit is not None:
            self._emit(
                capability_observed(
                    "filesystem",
                    "read_text",
                    {"path": path, "bytes": len(content.encode("utf-8"))},
                )
            )
        return content

    def write_text(self, path: str, content: str) -> None:
        self._files[path] = content
        if self._emit is not None:
            self._emit(
                capability_observed(
                    "filesystem",
                    "write_text",
                    {"path": path, "bytes": len(content.encode("utf-8"))},
                )
            )


def create_memory_filesystem(options: dict[str, Any]) -> tuple[Filesystem, Teardown]:
    cleaned, emit = pop_emit(options)
    raw_files = cleaned.get("files", {})
    files: dict[str, str] = {}
    if isinstance(raw_files, dict):
        files = {str(path): str(content) for path, content in raw_files.items()}

    instance = MemoryFilesystem(files, emit=emit)

    def teardown() -> None:
        instance._files.clear()

    return instance, teardown


def register_filesystem_providers(registry: Registry) -> None:
    registry.register("filesystem", "memory", create_memory_filesystem)
