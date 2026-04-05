from __future__ import annotations

from pathlib import Path


class DSSSupportError(Exception):
    """Base application error."""


class SnapshotLoadError(DSSSupportError):
    """Raised when a required snapshot cannot be loaded."""


class SnapshotNotFoundError(SnapshotLoadError):
    def __init__(self, snapshot_name: str, search_root: Path) -> None:
        super().__init__(f"{snapshot_name} snapshot was not found in {search_root}")


class SnapshotFormatError(SnapshotLoadError):
    def __init__(self, snapshot_name: str, path: Path, reason: str) -> None:
        super().__init__(f"{snapshot_name} snapshot at {path} could not be parsed: {reason}")
