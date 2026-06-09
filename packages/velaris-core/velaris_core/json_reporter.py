"""JSON-lines event reporter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TextIO

from velaris_core.reporting import event_to_dict


class JsonReporter:
    def __init__(self, path: str | Path | None = None, stream: TextIO | None = None) -> None:
        if path is None and stream is None:
            raise ValueError("JsonReporter requires path or stream")
        self._path = Path(path) if path is not None else None
        self._stream = stream
        self._handle: TextIO | None = None

    def handle(self, event: object) -> None:
        line = json.dumps(event_to_dict(event), sort_keys=True)
        if self._stream is not None:
            self._stream.write(line + "\n")
            self._stream.flush()
            return
        if self._handle is None:
            assert self._path is not None
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._handle = self._path.open("w", encoding="utf-8")
        self._handle.write(line + "\n")
        self._handle.flush()

    def close(self) -> None:
        if self._handle is not None:
            self._handle.close()
            self._handle = None
