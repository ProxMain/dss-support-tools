from __future__ import annotations

from pathlib import Path

import pytest

from dss_support_tool.config import AppPaths, PACKAGE_ROOT


@pytest.fixture
def app_paths(tmp_path: Path) -> AppPaths:
    workspace_tools_root = tmp_path / "tools"
    scraper_data_root = workspace_tools_root / "tool-scraper" / "data"
    static_root = PACKAGE_ROOT / "static"
    packaged_langpack_dist_root = tmp_path / "packaged-dist"
    langpack_dist_root = workspace_tools_root / "langpack-browser" / "dist"

    scraper_data_root.mkdir(parents=True)

    return AppPaths(
        workspace_tools_root=workspace_tools_root,
        bundle_root=tmp_path / "bundle",
        scraper_data_root=scraper_data_root,
        static_root=static_root,
        packaged_langpack_dist_root=packaged_langpack_dist_root,
        langpack_dist_root=langpack_dist_root,
    )

@pytest.fixture
def sample_crafting_payload() -> dict:
    return {
        "version": "craft-v1",
        "resources": [
            {
                "id": "iron",
                "guid": "iron",
                "name": "Iron",
                "unit": "ore",
                "miningLocations": [{"system": "Stanton", "planet": "Daymar", "name": "Cave"}],
            }
        ],
        "blueprints": [
            {
                "id": "bp-1",
                "name": 'Klaus "Scout" Helmet',
                "category": "armour",
                "categoryLabel": "Armour",
                "itemType": "Helmet",
                "craftTimeSeconds": 30,
                "tiers": 2,
                "ingredientSlots": [
                    {
                        "slot": "Core",
                        "primaryResourceId": "iron",
                        "primaryResourceName": "Iron",
                        "quantity": 2,
                        "options": [],
                        "qualityEffects": [],
                    }
                ],
                "missionRefs": [
                    {
                        "name": "Scout Recovery",
                        "contractor": "Crusader Security",
                        "missionType": "Contract",
                        "dropChance": "12%",
                        "locations": [{"system": "Stanton", "planet": "Daymar", "name": "Bunker"}],
                    }
                ],
                "systems": ["Stanton"],
            }
        ],
    }


@pytest.fixture
def sample_resource_payload() -> dict:
    return {
        "version": "mining-v1",
        "groupFamilies": [{"id": "mining", "label": "Mining"}],
        "groups": [{"id": "ship-mining", "label": "Ship Mining", "shortLabel": "Ship", "icon": "ship"}],
        "resources": [
            {
                "id": "iron",
                "name": "Iron",
                "family": "mining",
                "rarity": "common",
                "rawKind": "ore",
                "groupIds": ["ship-mining"],
                "locationCount": 1,
                "depositCount": 2,
                "stats": {"density": 1.2},
                "qualityProfile": {"min": 1, "max": 9, "mean": 4, "stddev": 1.1},
                "locations": [
                    {
                        "locationId": "loc-1",
                        "locationName": "Aaron Halo",
                        "system": "Stanton",
                        "locationType": "belt",
                        "groupName": "Ship Mining",
                        "groupProbability": 0.5,
                        "depositShare": 0.3,
                        "compositionName": "Rock",
                        "compositionShare": 0.6,
                        "minPercent": 1,
                        "maxPercent": 9,
                        "qualityProfile": {"min": 1, "max": 9, "mean": 4, "stddev": 1.1},
                    }
                ],
            }
        ],
    }


@pytest.fixture
def sample_trading_payload() -> dict:
    return {
        "apiVersion": "11.0.0",
        "localMarketUpdatedAt": "2026-04-06T10:00:00Z",
        "summary": {
            "commodityCount": 1,
            "shopCount": 2,
            "locationCount": 2,
            "listingCount": 1,
            "marketListingCount": 2,
            "itemTypeCount": 0,
            "factionCount": 0,
            "securityLevelCount": 0,
            "shipCount": 2,
            "routeShipCount": 1,
            "bountyCount": 1,
        },
        "commodities": [
            {
                "id": "astatine",
                "name": "Astatine",
                "typeIds": [],
                "typeLabels": [],
                "crowdsourceListingCount": 1,
                "marketListingCount": 2,
                "buyListingCount": 1,
                "sellListingCount": 1,
                "latestCrowdsourceTimestamp": "2026-04-06T07:55:28.395Z",
                "latestMarketTimestamp": "2026-04-06T08:05:00Z",
                "shopNames": [
                    "Stanton > Crusader > Orison > Admin",
                    "Stanton > Hurston > Lorville",
                ],
                "locationNames": ["Orison"],
            }
        ],
        "shops": [
            {
                "id": "stanton-crusader-orison-admin",
                "name": "Stanton > Crusader > Orison > Admin",
                "locationId": "orison",
                "locationName": "Orison",
                "transactionSupport": "local-snapshot",
                "marketListingCount": 1,
                "buyListingCount": 1,
                "sellListingCount": 0,
                "latestMarketTimestamp": "2026-04-06T08:05:00Z",
            },
            {
                "id": "stanton-hurston-lorville",
                "name": "Stanton > Hurston > Lorville",
                "locationId": "lorville",
                "locationName": "Lorville",
                "transactionSupport": "local-snapshot",
                "marketListingCount": 1,
                "buyListingCount": 0,
                "sellListingCount": 1,
                "latestMarketTimestamp": "2026-04-06T08:05:00Z",
            }
        ],
        "locations": [
            {
                "id": "orison",
                "name": "Orison",
                "type": "City",
                "listingCount": 2,
                "marketListingCount": 1,
                "latestListingTimestamp": "2026-04-06T07:55:28.395Z",
            },
            {
                "id": "lorville",
                "name": "Lorville",
                "type": "City",
                "listingCount": 1,
                "marketListingCount": 1,
                "latestListingTimestamp": "2026-04-06T07:55:28.395Z",
            }
        ],
        "itemTypes": [],
        "factions": [],
        "locationTypes": [{"id": "city", "name": "City"}],
        "securityLevels": [],
        "ships": [
            {"id": "cutlass-black", "name": "Cutlass Black", "cargoScu": 46},
            {"id": "gladius", "name": "Gladius", "cargoScu": None},
        ],
        "bounties": [{"locationId": "orison", "locationName": "Orison", "multiplier": 2}],
        "crowdsourceListings": [
            {
                "commodityId": "astatine",
                "commodityName": "Astatine",
                "locationId": "orison",
                "locationName": "Orison",
                "transaction": "SELLS",
                "price": 10.5,
                "quantity": 20,
                "saturation": 0.4,
                "boxSizesInScu": [1],
                "batchId": "batch-1",
                "timestamp": "2026-04-06T07:55:28.395Z",
            }
        ],
        "marketListings": [
            {
                "id": "astatine:stanton-crusader-orison-admin:buy",
                "commodityId": "astatine",
                "commodityName": "Astatine",
                "shopId": "stanton-crusader-orison-admin",
                "shopName": "Stanton > Crusader > Orison > Admin",
                "locationId": "orison",
                "locationName": "Orison",
                "operation": "buy",
                "price": 10.5,
                "scu": 20,
                "status": "live",
                "updatedAt": "2026-04-06T08:05:00Z",
            },
            {
                "id": "astatine:stanton-hurston-lorville:sell",
                "commodityId": "astatine",
                "commodityName": "Astatine",
                "shopId": "stanton-hurston-lorville",
                "shopName": "Stanton > Hurston > Lorville",
                "locationId": "lorville",
                "locationName": "Lorville",
                "operation": "sell",
                "price": 15.25,
                "scu": 50,
                "status": "live",
                "updatedAt": "2026-04-06T08:05:00Z",
            },
        ],
    }
