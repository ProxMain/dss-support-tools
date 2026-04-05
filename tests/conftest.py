from __future__ import annotations

from pathlib import Path

import pytest

from dss_support_tool.config import AppPaths


@pytest.fixture
def app_paths(tmp_path: Path) -> AppPaths:
    workspace_tools_root = tmp_path / "tools"
    scraper_data_root = workspace_tools_root / "tool-scraper" / "data"
    static_root = tmp_path / "static"
    packaged_langpack_dist_root = tmp_path / "packaged-dist"
    langpack_dist_root = workspace_tools_root / "langpack-browser" / "dist"

    scraper_data_root.mkdir(parents=True)
    static_root.mkdir(parents=True)
    (static_root / "index.html").write_text("<html>placeholder</html>", encoding="utf-8")

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
