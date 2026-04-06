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
    assert payload["baseUrl"].startswith("http://")
    assert payload["httpsBaseUrl"].startswith("https://")
    assert payload["httpsCaCertificatePath"].endswith("localhost-ca.pem")


def test_api_returns_resource_family_details(app_paths, sample_resource_payload) -> None:
    write_json(app_paths.scraper_data_root / "normalized-scmdb-mining-test.json", sample_resource_payload)
    client = TestClient(create_app(paths=app_paths))

    response = client.get("/api/resources/mining")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "mining"
    assert payload["resources"][0]["name"] == "Iron"


def test_api_returns_trading_family_details(app_paths, sample_resource_payload, sample_trading_payload) -> None:
    write_json(app_paths.scraper_data_root / "normalized-scmdb-mining-test.json", sample_resource_payload)
    write_json(app_paths.scraper_data_root / "normalized-sc-trade-test.json", sample_trading_payload)
    client = TestClient(create_app(paths=app_paths))

    response = client.get("/api/resources/trading")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "trading"
    assert payload["resources"][0]["name"] == "Astatine"
    assert payload["groups"]


def test_api_returns_trading_overview(app_paths, sample_trading_payload) -> None:
    write_json(app_paths.scraper_data_root / "normalized-sc-trade-test.json", sample_trading_payload)
    client = TestClient(create_app(paths=app_paths))

    response = client.get("/api/trading")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ships"][0]["name"] == "Cutlass Black"
    assert payload["coverage"]["marketListingCount"] == 2
    assert payload["commodities"][0]["name"] == "Astatine"


def test_api_returns_trading_routes(app_paths, sample_trading_payload) -> None:
    write_json(app_paths.scraper_data_root / "normalized-sc-trade-test.json", sample_trading_payload)
    client = TestClient(create_app(paths=app_paths))

    response = client.get(
        "/api/trading/routes",
        params={"shipId": "cutlass-black", "budget": 1000, "usableScu": 10},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ship"]["id"] == "cutlass-black"
    assert payload["usableScu"] == 10
    assert payload["routes"][0]["commodityName"] == "Astatine"
    assert payload["routes"][0]["cargoScu"] == 10
    assert payload["routes"][0]["profit"] > 0


def test_dashboard_route_returns_snapshot_ui(app_paths) -> None:
    client = TestClient(create_app(paths=app_paths))

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "/api/resources/trading" in response.text
    assert "loadDashboard()" in response.text
