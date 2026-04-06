from __future__ import annotations

import re
from typing import Any

from dss_support_tool.application.mining_preparation import build_mining_preparation
from dss_support_tool.infrastructure.snapshot_repository import SnapshotSummary


def build_crafting_data(
    snapshot: SnapshotSummary,
    mining_snapshot: SnapshotSummary | None = None,
) -> dict[str, Any]:
    payload = snapshot.payload or {}
    resource_map = {
        str(resource.get("id")): resource
        for resource in payload.get("resources", [])
        if isinstance(resource, dict) and resource.get("id")
    }
    mining_resource_map = _build_mining_resource_map(mining_snapshot.payload if mining_snapshot else {})

    grouped: dict[str, dict[str, Any]] = {}
    for blueprint in payload.get("blueprints", []) or []:
        if not isinstance(blueprint, dict):
            continue
        category_id = _map_crafting_category_id(blueprint.get("category"))
        category_label = _map_crafting_category_label(blueprint.get("categoryLabel") or blueprint.get("category"))
        category = grouped.setdefault(
            category_id,
            {
                "id": category_id,
                "label": category_label,
                "summary": f"{category_label} imported from SC Craft Tools snapshot {snapshot.version}.",
                "entries": [],
            },
        )
        category["entries"].append(
            {
                "id": blueprint.get("id"),
                "name": blueprint.get("name"),
                "manufacturer": _infer_brand(blueprint),
                "family": _infer_family(blueprint),
                "summary": _build_entry_summary(blueprint),
                "pieces": [],
                "variants": [],
                "itemType": blueprint.get("itemType"),
                "craftTimeSeconds": blueprint.get("craftTimeSeconds"),
                "ingredientSlots": _build_ingredient_slots(blueprint),
                "systems": blueprint.get("systems") or [],
                "blueprintSources": _build_blueprint_sources(blueprint),
                "alternativeSources": [],
                "resourceLeads": _build_resource_leads(blueprint, resource_map, mining_resource_map),
                "notes": _build_notes(blueprint),
            }
        )

    categories = sorted(grouped.values(), key=lambda item: str(item.get("label") or ""))
    for category in categories:
        category["entries"] = sorted(category["entries"], key=lambda item: str(item.get("name") or ""))

    return {
        "updatedFrom": f"SC Craft Tools normalized snapshot {snapshot.version}" if snapshot.version else snapshot.source,
        "version": snapshot.version,
        "path": str(snapshot.path),
        "categories": categories,
    }


def build_crafting_index(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "updatedFrom": data["updatedFrom"],
        "version": data.get("version"),
        "path": data.get("path"),
        "categories": [
            {
                "id": category["id"],
                "label": category["label"],
                "summary": category["summary"],
                "entryCount": len(category["entries"]),
            }
            for category in data["categories"]
        ],
        "blueprintCount": sum(len(category["entries"]) for category in data["categories"]),
    }


def _map_crafting_category_id(value: Any) -> str:
    text = str(value or "")
    return "armor" if text == "armour" else text


def _map_crafting_category_label(value: Any) -> str:
    text = str(value or "")
    return "Armor" if text == "Armour" else text


def _infer_family(blueprint: dict[str, Any]) -> str:
    category_label = blueprint.get("categoryLabel")
    subcategory = blueprint.get("subcategory")
    if category_label and isinstance(subcategory, list) and subcategory:
        return " / ".join([str(category_label), *[str(part) for part in subcategory if part]])
    if category_label:
        return str(category_label)
    if blueprint.get("itemType"):
        return str(blueprint["itemType"])
    return "Crafting"


def _infer_brand(blueprint: dict[str, Any]) -> str:
    name = str(blueprint.get("name") or "").strip()
    if not name:
        return "Unknown"

    quoted_prefix_match = re.match(r'^([A-Za-z0-9-]+)\s+"', name)
    if quoted_prefix_match:
        return quoted_prefix_match.group(1)

    token_match = re.match(r"^([A-Za-z0-9-]+)", name)
    if token_match:
        return token_match.group(1)
    return "Unknown"


def _build_entry_summary(blueprint: dict[str, Any]) -> str:
    ingredient_count = blueprint.get("totalIngredientCount") or len(blueprint.get("ingredientSlots", []) or [])
    mission_count = len(blueprint.get("missionRefs", []) or [])
    parts: list[str] = []

    if blueprint.get("itemType"):
        parts.append(f"{blueprint['itemType']} blueprint")
    if ingredient_count:
        parts.append(f"{ingredient_count} ingredient slots")
    if mission_count:
        parts.append(f"{mission_count} mission drops")
    if not parts:
        return "Normalized blueprint imported from the local SC Craft Tools snapshot."
    sentence = parts[0] if len(parts) == 1 else f"{parts[0]} with {' and '.join(parts[1:])}"
    return f"{sentence[:1].upper()}{sentence[1:]}."


def _build_blueprint_sources(blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    for mission in blueprint.get("missionRefs", []) or []:
        if not isinstance(mission, dict):
            continue
        system = " / ".join(
            [
                str(location.get("system"))
                for location in mission.get("locations", []) or []
                if isinstance(location, dict) and location.get("system")
            ]
        )
        requirements: list[str] = []
        if mission.get("missionType"):
            requirements.append(f"Mission type: {mission['missionType']}")
        if mission.get("dropChance"):
            requirements.append(f"Drop chance: {mission['dropChance']}")
        for location in (mission.get("locations", []) or [])[:3]:
            if not isinstance(location, dict):
                continue
            text = " / ".join([str(location.get(key)) for key in ("system", "planet", "name") if location.get(key)])
            if text:
                requirements.append(text)
        sources.append(
            {
                "title": mission.get("name") or "Unknown Mission",
                "issuer": mission.get("contractor") or "Unknown Contractor",
                "system": system or "Unknown",
                "reward": f"Blueprint drop for {blueprint.get('name') or 'Unknown Item'}",
                "requirements": requirements,
            }
        )
    return sources


def _build_resource_leads(
    blueprint: dict[str, Any],
    resource_map: dict[str, dict[str, Any]],
    mining_resource_map: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    leads: list[dict[str, Any]] = []
    for slot in blueprint.get("ingredientSlots", []) or []:
        if not isinstance(slot, dict):
            continue
        resource = resource_map.get(str(slot.get("primaryResourceId") or ""))
        if not isinstance(resource, dict):
            continue
        locations: list[str] = []
        for location in (resource.get("miningLocations") or [])[:10]:
            if not isinstance(location, dict):
                continue
            text = " / ".join([str(location.get(key)) for key in ("system", "planet", "name") if location.get(key)])
            if text:
                locations.append(text)
        mining_match = _lookup_mining_resource(mining_resource_map, resource)
        leads.append(
            {
                "material": resource.get("name") or "Unknown Resource",
                "type": resource.get("unit") or "resource",
                "locations": locations,
                "mining": _build_resource_mining_summary(mining_match),
            }
        )
    return leads


def _build_mining_resource_map(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    resource_map: dict[str, dict[str, Any]] = {}
    for resource in payload.get("resources", []) or []:
        if not isinstance(resource, dict):
            continue
        name = _normalize_resource_key(resource.get("name"))
        resource_id = _normalize_resource_key(resource.get("id"))
        if name:
            resource_map[name] = resource
        if resource_id and resource_id not in resource_map:
            resource_map[resource_id] = resource
    return resource_map


def _lookup_mining_resource(
    mining_resource_map: dict[str, dict[str, Any]],
    crafting_resource: dict[str, Any],
) -> dict[str, Any] | None:
    keys = [
        _normalize_resource_key(crafting_resource.get("name")),
        _normalize_resource_key(crafting_resource.get("id")),
        _normalize_resource_key(crafting_resource.get("guid")),
    ]
    for key in keys:
        if key and key in mining_resource_map:
            return mining_resource_map[key]
    return None


def _build_resource_mining_summary(resource: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(resource, dict):
        return None
    preparation = build_mining_preparation(resource)
    if not preparation:
        return None

    loadouts = {
        loadout.get("id"): loadout
        for loadout in preparation.get("recommendedLoadouts", []) or []
        if isinstance(loadout, dict) and loadout.get("id")
    }
    minimal = preparation.get("minimalRequired") or {}

    return {
        "minimal": minimal.get("vehicle") or minimal.get("tool") or "Unknown",
        "starter": _short_vehicle(loadouts.get("golem")) or _short_vehicle(minimal),
        "solo": _short_vehicle(loadouts.get("prospector")) or _short_vehicle(minimal),
        "crew": _short_vehicle(loadouts.get("mole")),
        "headline": preparation.get("scanning", {}).get("headline") or "Detailed scan the rock before you commit.",
    }


def _short_vehicle(loadout: dict[str, Any] | None) -> str | None:
    if not isinstance(loadout, dict):
        return None
    return str(loadout.get("vehicle") or "").strip() or None


def _normalize_resource_key(value: Any) -> str:
    text = str(value or "").strip().lower()
    return text.replace(" ", "").replace("-", "").replace("_", "")


def _build_notes(blueprint: dict[str, Any]) -> list[str]:
    notes = [
        f"Item type: {blueprint['itemType']}." if blueprint.get("itemType") else None,
        f"Craft time: {blueprint['craftTimeSeconds']} seconds." if blueprint.get("craftTimeSeconds") else None,
        f"Tier count: {blueprint['tiers']}." if blueprint.get("tiers") else None,
    ]
    output = [note for note in notes if note]
    return output or ["Normalized from the local SC Craft Tools snapshot."]


def _build_ingredient_slots(blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    for slot in blueprint.get("ingredientSlots", []) or []:
        if not isinstance(slot, dict):
            continue
        slots.append(
            {
                "slot": slot.get("slot") or "Unknown Slot",
                "primaryResourceName": slot.get("primaryResourceName") or "Unknown Resource",
                "quantity": slot.get("quantity"),
                "optionCount": len(slot.get("options", []) or []),
                "qualityEffectCount": len(slot.get("qualityEffects", []) or []),
            }
        )
    return slots
