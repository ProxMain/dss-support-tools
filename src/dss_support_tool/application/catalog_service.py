from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from dss_support_tool.application.crafting_catalog import build_crafting_data, build_crafting_index
from dss_support_tool.application.mining_ship_catalog import build_mining_ship_detail, build_mining_ship_index
from dss_support_tool.application.resource_catalog import build_resource_data, build_resource_index
from dss_support_tool.application.trading_planner import build_trading_overview, build_trading_routes
from dss_support_tool.errors import SnapshotNotFoundError
from dss_support_tool.infrastructure.snapshot_repository import SnapshotRepository


@dataclass
class _CacheEntry:
    signature: tuple[tuple[str, int], ...]
    value: dict[str, Any]


class CatalogService:
    def __init__(self, repository: SnapshotRepository) -> None:
        self._repository = repository
        self._crafting_cache: _CacheEntry | None = None
        self._mining_ship_cache: _CacheEntry | None = None
        self._resource_cache: _CacheEntry | None = None
        self._trading_cache: _CacheEntry | None = None

    def get_crafting_data(self) -> dict[str, Any]:
        snapshot = self._repository.load_crafting_snapshot()
        try:
            mining_snapshot = self._repository.load_resource_snapshot()
        except SnapshotNotFoundError:
            mining_snapshot = None
        self._crafting_cache = self._refresh_cache(
            self._crafting_cache,
            [snapshot.path, mining_snapshot.path] if mining_snapshot else [snapshot.path],
            lambda: build_crafting_data(snapshot, mining_snapshot),
        )
        return self._crafting_cache.value

    def get_crafting_index(self) -> dict[str, Any]:
        return build_crafting_index(self.get_crafting_data())

    def get_resource_data(self) -> dict[str, Any]:
        snapshot = self._repository.load_resource_snapshot()
        trading_snapshot = self._repository.maybe_load_trading_snapshot()
        self._resource_cache = self._refresh_cache(
            self._resource_cache,
            [snapshot.path, trading_snapshot.path] if trading_snapshot else [snapshot.path],
            lambda: build_resource_data(snapshot, trading_snapshot),
        )
        return self._resource_cache.value

    def get_resource_index(self) -> dict[str, Any]:
        return build_resource_index(self.get_resource_data())

    def get_mining_ship_index(self) -> dict[str, Any]:
        snapshot = self._repository.load_resource_snapshot()
        self._mining_ship_cache = self._refresh_cache(
            self._mining_ship_cache,
            [snapshot.path],
            lambda: build_mining_ship_index(snapshot),
        )
        return self._mining_ship_cache.value

    def get_mining_ship_detail(self, ship_id: str, resource_name: str | None = None) -> dict[str, Any]:
        snapshot = self._repository.load_resource_snapshot()
        self._mining_ship_cache = self._refresh_cache(
            self._mining_ship_cache,
            [snapshot.path],
            lambda: build_mining_ship_index(snapshot),
        )
        payload = build_mining_ship_detail(snapshot, ship_id, resource_name)
        if payload is None:
            raise ValueError(f"Unknown mining ship '{ship_id}'")
        return {
            "updatedFrom": self._mining_ship_cache.value["updatedFrom"],
            "version": self._mining_ship_cache.value.get("version"),
            "path": self._mining_ship_cache.value.get("path"),
            **payload,
        }

    def get_trading_overview(self) -> dict[str, Any]:
        snapshot = self._repository.load_trading_snapshot()
        self._trading_cache = self._refresh_cache(
            self._trading_cache,
            [snapshot.path],
            lambda: build_trading_overview(snapshot),
        )
        return self._trading_cache.value

    def get_trading_routes(
        self,
        *,
        ship_id: str,
        budget: float,
        usable_scu: float | None = None,
        max_results: int = 20,
    ) -> dict[str, Any]:
        return build_trading_routes(
            self.get_trading_overview(),
            ship_id=ship_id,
            budget=budget,
            usable_scu=usable_scu,
            max_results=max_results,
        )

    @staticmethod
    def _refresh_cache(
        cache_entry: _CacheEntry | None,
        paths: list[Path],
        factory: Callable[[], dict[str, Any]],
    ) -> _CacheEntry:
        signature = tuple(sorted((str(path), path.stat().st_mtime_ns) for path in paths))
        if cache_entry and cache_entry.signature == signature:
            return cache_entry
        return _CacheEntry(signature=signature, value=factory())
