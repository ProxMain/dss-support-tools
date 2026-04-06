from __future__ import annotations

from typing import Any

from dss_support_tool.application.trading_catalog import build_trading_family
from dss_support_tool.infrastructure.snapshot_repository import SnapshotSummary


def build_resource_data(
    snapshot: SnapshotSummary,
    trading_snapshot: SnapshotSummary | None = None,
) -> dict[str, Any]:
    payload = snapshot.payload or {}
    group_map = {
        str(group.get("id")): group
        for group in payload.get("groups", [])
        if isinstance(group, dict) and group.get("id")
    }
    family_map = {
        str(family.get("id")): family
        for family in payload.get("groupFamilies", [])
        if isinstance(family, dict) and family.get("id")
    }
    grouped_families: dict[str, dict[str, Any]] = {}

    for family in payload.get("groupFamilies", []) or []:
        if not isinstance(family, dict):
            continue
        family_id = str(family.get("id"))
        grouped_families[family_id] = {
            "id": family_id,
            "label": family.get("label") or family_id.title(),
            "summary": f"{family.get('label') or family_id.title()} routes and locations from SCMDB {snapshot.version}.",
            "groups": [],
            "resources": [],
        }

    for resource in payload.get("resources", []) or []:
        if not isinstance(resource, dict):
            continue
        family_id = str(resource.get("family") or "other")
        family_meta = family_map.get(family_id, {"label": family_id.title(), "id": family_id})
        family = grouped_families.setdefault(
            family_id,
            {
                "id": family_id,
                "label": family_meta.get("label") or family_id.title(),
                "summary": f"{family_meta.get('label') or family_id.title()} routes and locations from SCMDB {snapshot.version}.",
                "groups": [],
                "resources": [],
            },
        )
        group_ids = [str(group_id) for group_id in resource.get("groupIds", []) or [] if group_id]
        family["resources"].append(
            {
                "id": resource.get("id"),
                "name": resource.get("name"),
                "family": family.get("label"),
                "rarity": resource.get("rarity") or "unknown",
                "rawKind": resource.get("rawKind") or "unknown",
                "groupIds": group_ids,
                "groupLabels": [group_map.get(group_id, {}).get("label") or group_id for group_id in group_ids],
                "locationCount": resource.get("locationCount") or len(resource.get("locationIds", []) or []),
                "depositCount": resource.get("depositCount") or 0,
                "stats": resource.get("stats") or {},
                "qualityProfile": resource.get("qualityProfile"),
                "locations": resource.get("locations") or [],
            }
        )

    for family in grouped_families.values():
        group_ids = _dedupe([group_id for resource in family["resources"] for group_id in resource.get("groupIds", [])])
        family["groups"] = sorted(
            [
                {
                    "id": group_id,
                    "label": group_map.get(group_id, {}).get("label") or group_id,
                    "shortLabel": group_map.get(group_id, {}).get("shortLabel")
                    or group_map.get(group_id, {}).get("label")
                    or group_id,
                    "icon": group_map.get(group_id, {}).get("icon") or "hexagon",
                    "resourceCount": len(
                        [resource for resource in family["resources"] if group_id in resource.get("groupIds", [])]
                    ),
                }
                for group_id in group_ids
            ],
            key=lambda item: str(item.get("label") or ""),
        )
        family["resources"] = sorted(family["resources"], key=lambda item: str(item.get("name") or ""))

    if trading_snapshot is not None:
        grouped_families["trading"] = build_trading_family(trading_snapshot)

    families = sorted(grouped_families.values(), key=lambda item: str(item.get("label") or ""))
    return {
        "updatedFrom": f"SCMDB mining snapshot {snapshot.version}" if snapshot.version else snapshot.source,
        "version": snapshot.version,
        "path": str(snapshot.path),
        "families": families,
    }


def build_resource_index(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "updatedFrom": data["updatedFrom"],
        "version": data.get("version"),
        "path": data.get("path"),
        "families": [
            {
                "id": family["id"],
                "label": family["label"],
                "summary": family["summary"],
                "resourceCount": len(family["resources"]),
                "groupCount": len(family["groups"]),
            }
            for family in data["families"]
        ],
        "resourceCount": sum(len(family["resources"]) for family in data["families"]),
        "locationCount": sum(len(resource.get("locations", [])) for family in data["families"] for resource in family["resources"]),
    }


def _dedupe(values: list[str] | None) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values or []:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        output.append(text)
    return output
