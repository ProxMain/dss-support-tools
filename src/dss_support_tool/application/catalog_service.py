from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from dss_support_tool.application.crafting_catalog import build_crafting_data, build_crafting_index
from dss_support_tool.application.resource_catalog import build_resource_data, build_resource_index
from dss_support_tool.infrastructure.snapshot_repository import SnapshotRepository


@dataclass
class _CacheEntry:
    path: Path
    mtime_ns: int
    value: dict[str, Any]


class CatalogService:
    def __init__(self, repository: SnapshotRepository) -> None:
        self._repository = repository
        self._crafting_cache: _CacheEntry | None = None
        self._resource_cache: _CacheEntry | None = None

    def get_crafting_data(self) -> dict[str, Any]:
        snapshot = self._repository.load_crafting_snapshot()
        self._crafting_cache = self._refresh_cache(self._crafting_cache, snapshot.path, lambda: build_crafting_data(snapshot))
        return self._crafting_cache.value

    def get_crafting_index(self) -> dict[str, Any]:
        return build_crafting_index(self.get_crafting_data())

    def get_resource_data(self) -> dict[str, Any]:
        snapshot = self._repository.load_resource_snapshot()
        self._resource_cache = self._refresh_cache(self._resource_cache, snapshot.path, lambda: build_resource_data(snapshot))
        return self._resource_cache.value

    def get_resource_index(self) -> dict[str, Any]:
        return build_resource_index(self.get_resource_data())

    @staticmethod
    def _refresh_cache(
        cache_entry: _CacheEntry | None,
        path: Path,
        factory: Callable[[], dict[str, Any]],
    ) -> _CacheEntry:
        mtime_ns = path.stat().st_mtime_ns
        if cache_entry and cache_entry.path == path and cache_entry.mtime_ns == mtime_ns:
            return cache_entry
        return _CacheEntry(path=path, mtime_ns=mtime_ns, value=factory())
