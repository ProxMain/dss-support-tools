from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dss_support_tool.config import AppPaths
from dss_support_tool.errors import SnapshotFormatError, SnapshotNotFoundError


@dataclass(frozen=True)
class SnapshotSummary:
    source: str
    version: str | None
    path: Path
    payload: dict[str, Any]


class SnapshotRepository:
    def __init__(self, paths: AppPaths) -> None:
        self._paths = paths

    @property
    def data_root(self) -> Path:
        return self._paths.scraper_data_root

    def latest_crafting_snapshot_path(self) -> Path:
        return self._latest_snapshot("normalized-*.json", "crafting", exclude_prefixes=("normalized-scmdb-",))

    def latest_resource_snapshot_path(self) -> Path:
        return self._latest_snapshot("normalized-scmdb-mining-*.json", "resource")

    def load_crafting_snapshot(self) -> SnapshotSummary:
        path = self.latest_crafting_snapshot_path()
        payload = self._read_json(path, "crafting")
        return SnapshotSummary(
            source="sc-craft.tools normalized export",
            version=payload.get("version"),
            path=path,
            payload=payload,
        )

    def load_resource_snapshot(self) -> SnapshotSummary:
        path = self.latest_resource_snapshot_path()
        payload = self._read_json(path, "resource")
        return SnapshotSummary(
            source="scmdb mining normalized export",
            version=payload.get("version"),
            path=path,
            payload=payload,
        )

    def _latest_snapshot(
        self,
        pattern: str,
        snapshot_name: str,
        exclude_prefixes: tuple[str, ...] = (),
    ) -> Path:
        if not self.data_root.exists():
            raise SnapshotNotFoundError(snapshot_name, self.data_root)

        matches = sorted(
            [
                item
                for item in self.data_root.glob(pattern)
                if not any(item.name.startswith(prefix) for prefix in exclude_prefixes)
            ],
            key=lambda item: item.stat().st_mtime_ns,
            reverse=True,
        )
        if not matches:
            raise SnapshotNotFoundError(snapshot_name, self.data_root)
        return matches[0]

    def _read_json(self, path: Path, snapshot_name: str) -> dict[str, Any]:
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            raise SnapshotFormatError(snapshot_name, path, str(exc)) from exc
