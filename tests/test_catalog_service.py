from __future__ import annotations

from dss_support_tool.application.catalog_service import CatalogService
from dss_support_tool.infrastructure.snapshot_repository import SnapshotRepository

from tests.helpers import write_json


def test_catalog_service_builds_crafting_index(app_paths, sample_crafting_payload) -> None:
    write_json(app_paths.scraper_data_root / "normalized-test.json", sample_crafting_payload)
    service = CatalogService(SnapshotRepository(app_paths))

    payload = service.get_crafting_index()

    assert payload["version"] == "craft-v1"
    assert payload["blueprintCount"] == 1
    assert payload["categories"][0]["id"] == "armor"


def test_catalog_service_builds_resource_index(app_paths, sample_resource_payload) -> None:
    write_json(app_paths.scraper_data_root / "normalized-scmdb-mining-test.json", sample_resource_payload)
    service = CatalogService(SnapshotRepository(app_paths))

    payload = service.get_resource_index()

    assert payload["version"] == "mining-v1"
    assert payload["resourceCount"] == 1
    assert payload["families"][0]["id"] == "mining"


def test_catalog_service_appends_trading_family_when_snapshot_exists(
    app_paths,
    sample_resource_payload,
    sample_trading_payload,
) -> None:
    write_json(app_paths.scraper_data_root / "normalized-scmdb-mining-test.json", sample_resource_payload)
    write_json(app_paths.scraper_data_root / "normalized-sc-trade-test.json", sample_trading_payload)
    service = CatalogService(SnapshotRepository(app_paths))

    payload = service.get_resource_index()

    trading_family = next(family for family in payload["families"] if family["id"] == "trading")
    assert trading_family["resourceCount"] == 1
    assert trading_family["groupCount"] >= 1
