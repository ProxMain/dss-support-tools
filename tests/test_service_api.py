from __future__ import annotations

from fastapi.testclient import TestClient

from dss_support_tool.service import create_app

from tests.helpers import write_json


def test_api_returns_503_when_crafting_snapshot_is_missing(app_paths, sample_resource_payload) -> None:
    write_json(app_paths.scraper_data_root / "normalized-scmdb-mining-test.json", sample_resource_payload)
    client = TestClient(create_app(paths=app_paths))

    response = client.get("/api/crafting")

    assert response.status_code == 503
    assert "crafting snapshot" in response.json()["detail"]


def test_status_reports_dataset_errors(app_paths) -> None:
    client = TestClient(create_app(paths=app_paths))

    response = client.get("/api/status")
    payload = response.json()

    assert response.status_code == 200
    assert payload["crafting"]["ok"] is False
    assert payload["resources"]["ok"] is False
    assert payload["frontend"]["placeholder"] is True


def test_api_returns_resource_family_details(app_paths, sample_resource_payload) -> None:
    write_json(app_paths.scraper_data_root / "normalized-scmdb-mining-test.json", sample_resource_payload)
    client = TestClient(create_app(paths=app_paths))

    response = client.get("/api/resources/mining")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "mining"
    assert payload["resources"][0]["name"] == "Iron"
