from __future__ import annotations

import pytest

from dss_support_tool.errors import SnapshotFormatError, SnapshotNotFoundError
from dss_support_tool.infrastructure.snapshot_repository import SnapshotRepository

from tests.helpers import write_json


def test_repository_raises_when_snapshot_missing(app_paths) -> None:
    repository = SnapshotRepository(app_paths)

    with pytest.raises(SnapshotNotFoundError):
        repository.load_crafting_snapshot()


def test_repository_raises_when_snapshot_is_invalid_json(app_paths) -> None:
    repository = SnapshotRepository(app_paths)
    invalid_path = app_paths.scraper_data_root / "normalized-test.json"
    invalid_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(SnapshotFormatError):
        repository.load_crafting_snapshot()


def test_repository_picks_latest_snapshot(app_paths, sample_crafting_payload) -> None:
    old_path = app_paths.scraper_data_root / "normalized-old.json"
    latest_path = app_paths.scraper_data_root / "normalized-new.json"
    write_json(old_path, {**sample_crafting_payload, "version": "old"})
    write_json(latest_path, {**sample_crafting_payload, "version": "new"})

    repository = SnapshotRepository(app_paths)

    snapshot = repository.load_crafting_snapshot()

    assert snapshot.version == "new"
    assert snapshot.path == latest_path


def test_repository_loads_latest_trading_snapshot(app_paths, sample_trading_payload) -> None:
    old_path = app_paths.scraper_data_root / "normalized-sc-trade-old.json"
    latest_path = app_paths.scraper_data_root / "normalized-sc-trade-new.json"
    write_json(old_path, {**sample_trading_payload, "apiVersion": "10.0.0"})
    write_json(latest_path, sample_trading_payload)

    repository = SnapshotRepository(app_paths)

    snapshot = repository.load_trading_snapshot()

    assert snapshot.version == "11.0.0"
    assert snapshot.path == latest_path
