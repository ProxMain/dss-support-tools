from __future__ import annotations

from typing import Any

from dss_support_tool.application.mining_guidance_data import load_mining_guidance_data
from dss_support_tool.application.mining_preparation import build_mining_preparation
from dss_support_tool.infrastructure.snapshot_repository import SnapshotSummary

GUIDANCE = load_mining_guidance_data()
SHIP_CONFIG = GUIDANCE["shipConfig"]
SCAN_FREQUENCY_REFERENCE = GUIDANCE["scanFrequencyReference"]
DECISION_MATRIX = GUIDANCE["decisionMatrix"]


def build_mining_ship_index(snapshot: SnapshotSummary) -> dict[str, Any]:
    ships = [_build_ship_payload(ship_id, snapshot.payload or {}) for ship_id in ("golem", "prospector", "mole")]
    return {
        "updatedFrom": f"SCMDB mining snapshot {snapshot.version}" if snapshot.version else snapshot.source,
        "version": snapshot.version,
        "path": str(snapshot.path),
        "ships": [
            {
                "id": ship["id"],
                "label": ship["label"],
                "vehicle": ship["vehicle"],
                "summary": ship["summary"],
                "capability": ship["capability"],
            }
            for ship in ships
        ],
    }


def build_mining_ship_detail(
    snapshot: SnapshotSummary,
    ship_id: str,
    resource_name: str | None = None,
) -> dict[str, Any] | None:
    return _build_ship_payload(ship_id, snapshot.payload or {}, resource_name=resource_name)


def _build_ship_payload(
    ship_id: str,
    payload: dict[str, Any],
    *,
    resource_name: str | None = None,
) -> dict[str, Any] | None:
    config = SHIP_CONFIG.get(ship_id)
    if not config:
        return None

    resources = _collect_resources(payload)
    can_mine, conditional, avoid = _categorize_resources(resources, config["capability"])
    focused_resource = _build_focused_resource(resources, config["capability"], resource_name)
    return {
        "id": ship_id,
        "label": config["label"],
        "vehicle": config["vehicle"],
        "summary": config["summary"],
        "capability": config["capability"],
        "cargoScu": config["cargoScu"],
        "radar": config["radar"],
        "heads": config["heads"],
        "modules": config["modules"],
        "gadgets": config["gadgets"],
        "scanWorkflow": config["scanWorkflow"],
        "targetRocks": config["targetRocks"],
        "scanFrequencies": _build_scan_frequencies(config["targetRocks"]),
        "focusedResource": focused_resource,
        "cannotMine": config["cannotMine"],
        "recommendedResources": can_mine[:12],
        "conditionalResources": conditional[:12],
        "avoidResources": avoid[:12],
    }


def _collect_resources(payload: dict[str, Any]) -> list[dict[str, Any]]:
    resources: list[dict[str, Any]] = []
    for resource in payload.get("resources", []) or []:
        if not isinstance(resource, dict):
            continue
        if str(resource.get("family") or "").lower() != "mining":
            continue
        preparation = build_mining_preparation(resource)
        if not preparation:
            continue
        groups = {str(group_id) for group_id in resource.get("groupIds", []) or [] if group_id}
        resources.append(
            {
                "id": resource.get("id"),
                "name": resource.get("name"),
                "groups": groups,
                "difficulty": preparation["difficulty"]["level"],
                "rarity": str(resource.get("rarity") or "unknown"),
                "rawKind": str(resource.get("rawKind") or "unknown"),
                "scanSignature": _format_number(resource.get("stats", {}).get("scanSignature")),
                "groundScanSignature": _format_number(resource.get("stats", {}).get("groundScanSignature")),
                "locations": _summarize_locations(resource.get("locations") or []),
            }
        )
    return resources


def _categorize_resources(resources: list[dict[str, Any]], capability: str) -> tuple[list[str], list[str], list[str]]:
    can_mine: list[str] = []
    conditional: list[str] = []
    avoid: list[str] = []
    for resource in sorted(resources, key=lambda item: str(item.get("name") or "")):
        classification = _classify_resource(resource, capability)
        name = str(resource.get("name") or "Unknown")
        if classification == "can":
            can_mine.append(name)
        elif classification == "conditional":
            conditional.append(name)
        else:
            avoid.append(name)
    return can_mine, conditional, avoid


def _classify_resource(resource: dict[str, Any], capability: str) -> str:
    groups = resource["groups"]
    difficulty = resource["difficulty"]
    name = str(resource.get("name") or "").lower()

    if "fps-mining" in groups or "roc-mining" in groups:
        return "avoid"

    if capability == "starter":
        if difficulty == "standard" and "ship-mining-rare" not in groups:
            return "can"
        if difficulty == "advanced" and name not in {"quantainium", "quantanium"}:
            return "conditional"
        return "avoid"

    if capability == "solo":
        if difficulty == "standard":
            return "can"
        if difficulty == "advanced":
            return "can"
        return "conditional"

    if capability == "crew":
        return "can"

    return "avoid"


def _build_scan_frequencies(target_rocks: dict[str, list[str]]) -> list[dict[str, str]]:
    rock_types: list[str] = []
    for section in ("prioritize", "conditional", "avoid"):
        for value in target_rocks.get(section, []):
            if "-Type" not in value:
                continue
            if value not in rock_types:
                rock_types.append(value)

    frequencies: list[dict[str, str]] = []
    for rock_type in rock_types:
        meta = SCAN_FREQUENCY_REFERENCE.get(
            rock_type,
            {
                "signature": "Unknown",
                "note": "Unknown",
            },
        )
        frequencies.append(
            {
                "rockType": rock_type,
                "signature": meta["signature"],
                "note": meta["note"],
            }
        )
    return frequencies


def _build_focused_resource(
    resources: list[dict[str, Any]],
    capability: str,
    resource_name: str | None,
) -> dict[str, Any] | None:
    if not resource_name:
        return None

    wanted = _normalize_text(resource_name)
    resource = next(
        (
            item
            for item in resources
            if _normalize_text(item.get("name")) == wanted or _normalize_text(item.get("id")) == wanted
        ),
        None,
    )
    if not resource:
        return {
            "name": resource_name,
            "classification": "unknown",
            "label": "Unknown",
            "summary": "This resource is not present in the current mining snapshot.",
            "difficulty": "unknown",
            "rarity": "unknown",
            "rawKind": "unknown",
            "scanSignature": "Unknown",
            "groundScanSignature": "Unknown",
            "locations": [],
            "decision": {
                "stock": {"allowed": False, "label": "Unknown", "reason": "No mining snapshot match was found for this resource."},
                "modules": {"allowed": False, "label": "Unknown", "reason": "No mining snapshot match was found for this resource.", "items": [], "usage": "Unknown"},
                "gadgets": {"allowed": False, "label": "Unknown", "reason": "No mining snapshot match was found for this resource.", "items": [], "usage": "Unknown"},
                "verdict": "Unknown",
            },
        }

    classification = _classify_resource(resource, capability)
    label_map = {
        "can": "Good Fit",
        "conditional": "Conditional",
        "avoid": "Usually Skip",
    }
    summary_map = {
        "can": f"{resource['name']} is a practical target for this ship when the detailed scan confirms a clean rock.",
        "conditional": f"{resource['name']} can be mined with this ship, but only when the detailed scan and rock mass stay favorable.",
        "avoid": f"{resource['name']} is not a good planning target for this ship. Use a better-matched mining platform.",
    }
    return {
        "name": resource["name"],
        "classification": classification,
        "label": label_map.get(classification, "Unknown"),
        "summary": summary_map.get(classification, "Unknown"),
        "difficulty": resource["difficulty"],
        "rarity": resource["rarity"],
        "rawKind": resource["rawKind"],
        "scanSignature": resource["scanSignature"],
        "groundScanSignature": resource["groundScanSignature"],
        "locations": resource["locations"][:8],
        "decision": _build_resource_decision(ship_id=capability, difficulty=resource["difficulty"], classification=classification),
    }


def _normalize_text(value: Any) -> str:
    return str(value or "").strip().lower().replace(" ", "").replace("-", "").replace("_", "")


def _format_number(value: Any) -> str:
    if value is None:
        return "Unknown"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "Unknown"
    if number.is_integer():
        return str(int(number))
    return f"{number:.2f}".rstrip("0").rstrip(".")


def _summarize_locations(locations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for location in locations:
        if not isinstance(location, dict):
            continue
        location_id = str(location.get("locationId") or "")
        group_name = str(location.get("groupName") or "Unknown")
        key = f"{location_id}:{group_name}"
        composition_name = str(location.get("compositionName") or "").strip()

        if key not in grouped:
            grouped[key] = {
                "locationId": location_id,
                "locationName": str(location.get("locationName") or "Unknown"),
                "system": str(location.get("system") or "Unknown"),
                "locationType": str(location.get("locationType") or "Unknown"),
                "groupName": group_name,
                "groupProbabilityValue": _float_or_none(location.get("groupProbability")),
                "depositShareValue": _float_or_none(location.get("depositShare")),
                "minPercentValue": _float_or_none(location.get("minPercent")),
                "maxPercentValue": _float_or_none(location.get("maxPercent")),
                "compositions": [composition_name] if composition_name else [],
            }
            continue

        existing = grouped[key]
        existing["groupProbabilityValue"] = _max_float(
            existing.get("groupProbabilityValue"),
            _float_or_none(location.get("groupProbability")),
        )
        existing["depositShareValue"] = _max_float(
            existing.get("depositShareValue"),
            _float_or_none(location.get("depositShare")),
        )
        existing["minPercentValue"] = _min_float(
            existing.get("minPercentValue"),
            _float_or_none(location.get("minPercent")),
        )
        existing["maxPercentValue"] = _max_float(
            existing.get("maxPercentValue"),
            _float_or_none(location.get("maxPercent")),
        )
        if composition_name and composition_name not in existing["compositions"]:
            existing["compositions"].append(composition_name)

    summarized = [
        {
            "locationId": item["locationId"],
            "locationName": item["locationName"],
            "system": item["system"],
            "locationType": item["locationType"],
            "groupName": item["groupName"],
            "groupProbability": _format_percent(item.get("groupProbabilityValue")),
            "depositShare": _format_percent(item.get("depositShareValue")),
            "compositionName": ", ".join(item["compositions"]) if item["compositions"] else "Unknown",
            "minPercent": _format_percent(item.get("minPercentValue")),
            "maxPercent": _format_percent(item.get("maxPercentValue")),
        }
        for item in grouped.values()
    ]
    summarized.sort(
        key=lambda item: (
            _sort_number(item.get("groupProbability")),
            _sort_number(item.get("depositShare")),
            str(item.get("system") or ""),
            str(item.get("locationName") or ""),
        ),
        reverse=True,
    )
    return summarized


def _format_percent(value: Any) -> str:
    text = _format_number(value)
    return "Unknown" if text == "Unknown" else f"{text}%"


def _sort_number(value: Any) -> float:
    text = str(value or "")
    if text.endswith("%"):
        text = text[:-1]
    try:
        return float(text)
    except (TypeError, ValueError):
        return -1.0


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _max_float(left: float | None, right: float | None) -> float | None:
    if left is None:
        return right
    if right is None:
        return left
    return max(left, right)


def _min_float(left: float | None, right: float | None) -> float | None:
    if left is None:
        return right
    if right is None:
        return left
    return min(left, right)


def _build_resource_decision(*, ship_id: str, difficulty: str, classification: str) -> dict[str, Any]:
    if classification == "avoid":
        return DECISION_MATRIX["avoid"]

    if ship_id == "starter":
        return DECISION_MATRIX["starter"]["default"]

    if ship_id == "solo":
        if difficulty == "standard":
            return DECISION_MATRIX["solo"]["standard"]
        return DECISION_MATRIX["solo"]["default"]

    if ship_id == "crew":
        if difficulty == "extreme":
            return DECISION_MATRIX["crew"]["extreme"]
        return DECISION_MATRIX["crew"]["default"]

    return DECISION_MATRIX["unknown"]
