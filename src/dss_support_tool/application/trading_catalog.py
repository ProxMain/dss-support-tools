from __future__ import annotations

from typing import Any

from dss_support_tool.infrastructure.snapshot_repository import SnapshotSummary


def build_trading_family(snapshot: SnapshotSummary) -> dict[str, Any]:
    payload = snapshot.payload or {}
    commodities = payload.get("commodities", []) or []
    locations = payload.get("locations", []) or []
    item_types = payload.get("itemTypes", []) or []
    shops = payload.get("shops", []) or []
    listings = payload.get("crowdsourceListings", []) or []
    bounties = payload.get("bounties", []) or []

    resources = [
        {
            "id": commodity.get("id"),
            "name": commodity.get("name"),
            "family": "Trading",
            "rarity": "market",
            "rawKind": "commodity",
            "groupIds": _build_group_ids(commodity, shops, locations, bounties),
            "groupLabels": _build_group_labels(commodity, shops, locations, bounties),
            "locationCount": len(commodity.get("locationNames", []) or []),
            "depositCount": 0,
            "stats": {
                "crowdsourceListingCount": commodity.get("crowdsourceListingCount") or 0,
                "shopCount": len(commodity.get("shopNames", []) or []),
                "latestCrowdsourceTimestamp": commodity.get("latestCrowdsourceTimestamp"),
            },
            "qualityProfile": None,
            "locations": _build_location_refs(commodity, listings, shops, locations),
        }
        for commodity in commodities
        if isinstance(commodity, dict) and commodity.get("id") and commodity.get("name")
    ]

    groups = _build_groups(item_types, shops, locations, bounties, resources)
    return {
        "id": "trading",
        "label": "Trading",
        "summary": _build_summary(payload, commodities, shops, locations, listings),
        "groups": groups,
        "resources": sorted(resources, key=lambda item: str(item.get("name") or "")),
    }


def _build_summary(
    payload: dict[str, Any],
    commodities: list[Any],
    shops: list[Any],
    locations: list[Any],
    listings: list[Any],
) -> str:
    api_version = payload.get("apiVersion")
    version_suffix = f" API {api_version}" if api_version else ""
    return (
        f"{len(commodities)} commodities, {len(shops)} shops, {len(locations)} locations, and "
        f"{len(listings)} crowdsourced listings from SC Trade Tools{version_suffix}."
    )


def _build_groups(
    item_types: list[Any],
    shops: list[Any],
    locations: list[Any],
    bounties: list[Any],
    resources: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    shop_group = {
        "id": "shops",
        "label": "Shops",
        "shortLabel": "Shops",
        "icon": "store",
        "resourceCount": len([resource for resource in resources if "shops" in resource.get("groupIds", [])]),
    }
    location_group = {
        "id": "locations",
        "label": "Locations",
        "shortLabel": "Locations",
        "icon": "map-pin",
        "resourceCount": len([resource for resource in resources if "locations" in resource.get("groupIds", [])]),
    }
    bounty_group = {
        "id": "bounties",
        "label": "Bounties",
        "shortLabel": "Bounties",
        "icon": "target",
        "resourceCount": len([resource for resource in resources if "bounties" in resource.get("groupIds", [])]),
    }
    item_type_group = {
        "id": "commodity-types",
        "label": "Commodity Types",
        "shortLabel": "Types",
        "icon": "tags",
        "resourceCount": len([resource for resource in resources if "commodity-types" in resource.get("groupIds", [])]),
    }

    groups = [
        item_type_group if item_types else None,
        shop_group if shops else None,
        location_group if locations else None,
        bounty_group if bounties else None,
    ]
    return [group for group in groups if group]


def _build_group_ids(
    commodity: dict[str, Any],
    shops: list[Any],
    locations: list[Any],
    bounties: list[Any],
) -> list[str]:
    group_ids: list[str] = []
    if commodity.get("typeIds"):
        group_ids.append("commodity-types")
    if shops:
        group_ids.append("shops")
    if locations:
        group_ids.append("locations")
    if _commodity_has_bounty(commodity, bounties):
        group_ids.append("bounties")
    return group_ids


def _build_group_labels(
    commodity: dict[str, Any],
    shops: list[Any],
    locations: list[Any],
    bounties: list[Any],
) -> list[str]:
    labels: list[str] = []
    if commodity.get("typeIds"):
        labels.append("Commodity Types")
    if shops:
        labels.append("Shops")
    if locations:
        labels.append("Locations")
    if _commodity_has_bounty(commodity, bounties):
        labels.append("Bounties")
    return labels


def _build_location_refs(
    commodity: dict[str, Any],
    listings: list[Any],
    shops: list[Any],
    locations: list[Any],
) -> list[dict[str, Any]]:
    listing_refs = [
        {
            "locationId": listing.get("locationId"),
            "locationName": listing.get("locationName"),
            "system": None,
            "locationType": None,
            "groupName": "Crowdsource",
            "groupProbability": None,
            "depositShare": None,
            "compositionName": listing.get("transaction"),
            "compositionShare": listing.get("saturation"),
            "minPercent": None,
            "maxPercent": None,
            "qualityProfile": None,
        }
        for listing in listings
        if isinstance(listing, dict) and listing.get("commodityId") == commodity.get("id")
    ]
    if listing_refs:
        return listing_refs

    return [
        {
            "locationId": None,
            "locationName": location_name,
            "system": None,
            "locationType": None,
            "groupName": "Trading",
            "groupProbability": None,
            "depositShare": None,
            "compositionName": None,
            "compositionShare": None,
            "minPercent": None,
            "maxPercent": None,
            "qualityProfile": None,
        }
        for location_name in commodity.get("locationNames", []) or []
    ]


def _commodity_has_bounty(commodity: dict[str, Any], bounties: list[Any]) -> bool:
    commodity_locations = {str(location).strip() for location in commodity.get("locationNames", []) or [] if location}
    bounty_locations = {
        str(bounty.get("locationName")).strip()
        for bounty in bounties
        if isinstance(bounty, dict) and bounty.get("locationName")
    }
    return bool(commodity_locations & bounty_locations)
