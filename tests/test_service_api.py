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
    assert payload["resources"][0]["preparation"]["minimalRequired"]["vehicle"] == "MISC Prospector"
    assert any(
        loadout["label"] == "Solo Prospector"
        for loadout in payload["resources"][0]["preparation"]["recommendedLoadouts"]
    )


def test_api_returns_mining_ship_detail(app_paths, sample_resource_payload) -> None:
    write_json(app_paths.scraper_data_root / "normalized-scmdb-mining-test.json", sample_resource_payload)
    client = TestClient(create_app(paths=app_paths))

    response = client.get("/api/mining-ships/prospector", params={"resource": "Iron"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["vehicle"] == "MISC Prospector"
    assert "Helix I Mining Laser" in payload["heads"][0]
    assert payload["recommendedResources"]
    assert payload["scanFrequencies"]
    assert payload["scanFrequencies"][0]["signature"]
    assert payload["focusedResource"]["name"] == "Iron"
    assert payload["focusedResource"]["scanSignature"] == "Unknown"
    assert payload["focusedResource"]["locations"]


def test_api_deduplicates_focused_resource_locations(app_paths, sample_resource_payload) -> None:
    resource_payload = {
        **sample_resource_payload,
        "resources": [
            {
                **sample_resource_payload["resources"][0],
                "locations": [
                    sample_resource_payload["resources"][0]["locations"][0],
                    {
                        **sample_resource_payload["resources"][0]["locations"][0],
                        "minPercent": 20,
                        "maxPercent": 50,
                        "compositionName": "Dense Rock",
                    },
                ],
            }
        ],
    }
    write_json(app_paths.scraper_data_root / "normalized-scmdb-mining-test.json", resource_payload)
    client = TestClient(create_app(paths=app_paths))

    response = client.get("/api/mining-ships/prospector", params={"resource": "Iron"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["focusedResource"]["locations"]) == 1
    assert payload["focusedResource"]["locations"][0]["compositionName"] == "Rock, Dense Rock"
    assert payload["focusedResource"]["locations"][0]["minPercent"] == "1%"
    assert payload["focusedResource"]["locations"][0]["maxPercent"] == "50%"


def test_api_returns_crafting_material_mining_summary(
    app_paths,
    sample_crafting_payload,
    sample_resource_payload,
) -> None:
    write_json(app_paths.scraper_data_root / "normalized-live.json", sample_crafting_payload)
    write_json(app_paths.scraper_data_root / "normalized-scmdb-mining-test.json", sample_resource_payload)
    client = TestClient(create_app(paths=app_paths))

    response = client.get("/api/crafting/armor")

    assert response.status_code == 200
    payload = response.json()
    lead = payload["entries"][0]["resourceLeads"][0]
    assert lead["material"] == "Iron"
    assert lead["mining"]["minimal"] == "MISC Prospector"
    assert lead["mining"]["solo"] == "MISC Prospector"


def test_api_returns_trading_family_details(app_paths, sample_resource_payload, sample_trading_payload) -> None:
    trading_payload = {
        **sample_trading_payload,
        "commodities": [
            {
                **sample_trading_payload["commodities"][0],
                "locationNames": ["Orison", "Lorville"],
            }
        ],
    }
    write_json(app_paths.scraper_data_root / "normalized-scmdb-mining-test.json", sample_resource_payload)
    write_json(app_paths.scraper_data_root / "normalized-sc-trade-test.json", trading_payload)
    client = TestClient(create_app(paths=app_paths))

    response = client.get("/api/resources/trading")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "trading"
    assert payload["resources"][0]["name"] == "Astatine"
    assert payload["groups"]
    assert len(payload["resources"][0]["locations"]) == 2


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
