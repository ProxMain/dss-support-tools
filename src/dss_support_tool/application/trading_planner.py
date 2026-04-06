from __future__ import annotations

from typing import Any

from dss_support_tool.infrastructure.snapshot_repository import SnapshotSummary


def build_trading_overview(snapshot: SnapshotSummary) -> dict[str, Any]:
    payload = snapshot.payload or {}
    market_listings = sorted(
        [listing for listing in payload.get("marketListings", []) or [] if isinstance(listing, dict)],
        key=lambda listing: (
            str(listing.get("commodityName") or ""),
            str(listing.get("shopName") or ""),
            str(listing.get("operation") or ""),
        ),
    )
    commodities = [commodity for commodity in payload.get("commodities", []) or [] if isinstance(commodity, dict)]
    ships = sorted(
        [
            ship
            for ship in payload.get("ships", []) or []
            if isinstance(ship, dict) and _as_positive_number(ship.get("cargoScu")) is not None
        ],
        key=lambda ship: (_as_positive_number(ship.get("cargoScu")) or 0, str(ship.get("name") or "")),
    )

    return {
        "updatedFrom": str(snapshot.path.name),
        "source": snapshot.source,
        "summary": payload.get("summary", {}),
        "coverage": _build_coverage(payload, market_listings, ships),
        "ships": [
            {
                "id": ship.get("id"),
                "name": ship.get("name"),
                "cargoScu": _as_positive_number(ship.get("cargoScu")),
            }
            for ship in ships
        ],
        "commodities": _build_commodity_overview(commodities, market_listings),
        "shops": _build_shop_overview(payload.get("shops", []) or [], market_listings),
        "marketListings": market_listings,
        "missingShips": sorted(
            [
                ship
                for ship in payload.get("missingShips", []) or []
                if isinstance(ship, dict) and ship.get("id") and ship.get("name")
            ],
            key=lambda ship: str(ship.get("name") or ""),
        ),
    }


def build_trading_routes(
    overview: dict[str, Any],
    *,
    ship_id: str,
    budget: float,
    usable_scu: float | None = None,
    max_results: int = 20,
) -> dict[str, Any]:
    if budget <= 0:
        raise ValueError("Budget must be greater than zero.")

    ships = overview.get("ships", []) or []
    selected_ship = next((ship for ship in ships if ship.get("id") == ship_id), None)
    if not selected_ship:
        raise ValueError("Trading ship not found.")

    total_cargo_scu = _as_positive_number(selected_ship.get("cargoScu"))
    if total_cargo_scu is None:
        raise ValueError("Selected ship has no cargo capacity.")
    effective_cargo_scu = total_cargo_scu if usable_scu is None else _as_positive_number(usable_scu)
    if effective_cargo_scu is None:
        raise ValueError("Usable SCU must be greater than zero.")
    if effective_cargo_scu > total_cargo_scu:
        raise ValueError("Usable SCU cannot exceed the ship's total cargo capacity.")

    market_listings = [listing for listing in overview.get("marketListings", []) or [] if isinstance(listing, dict)]
    buy_listings = [listing for listing in market_listings if listing.get("operation") == "buy"]
    sell_listings = [listing for listing in market_listings if listing.get("operation") == "sell"]

    sell_by_commodity: dict[str, list[dict[str, Any]]] = {}
    for listing in sell_listings:
        sell_by_commodity.setdefault(str(listing.get("commodityId") or ""), []).append(listing)

    routes: list[dict[str, Any]] = []
    for buy_listing in buy_listings:
        commodity_id = str(buy_listing.get("commodityId") or "")
        for sell_listing in sell_by_commodity.get(commodity_id, []):
            if buy_listing.get("shopId") == sell_listing.get("shopId"):
                continue

            buy_price = _as_positive_number(buy_listing.get("price"))
            sell_price = _as_positive_number(sell_listing.get("price"))
            buy_scu = _as_positive_number(buy_listing.get("scu"))
            sell_scu = _as_positive_number(sell_listing.get("scu"))
            if buy_price is None or sell_price is None or buy_scu is None or sell_scu is None:
                continue
            if sell_price <= buy_price:
                continue

            affordable_scu = int(budget // buy_price)
            route_scu = min(int(effective_cargo_scu), affordable_scu, int(buy_scu), int(sell_scu))
            if route_scu <= 0:
                continue

            cost = round(route_scu * buy_price, 2)
            revenue = round(route_scu * sell_price, 2)
            profit = round(revenue - cost, 2)
            if profit <= 0:
                continue

            routes.append(
                {
                    "commodityId": commodity_id,
                    "commodityName": buy_listing.get("commodityName"),
                    "origin": {
                        "shopId": buy_listing.get("shopId"),
                        "shopName": buy_listing.get("shopName"),
                        "locationId": buy_listing.get("locationId"),
                        "locationName": buy_listing.get("locationName"),
                    },
                    "destination": {
                        "shopId": sell_listing.get("shopId"),
                        "shopName": sell_listing.get("shopName"),
                        "locationId": sell_listing.get("locationId"),
                        "locationName": sell_listing.get("locationName"),
                    },
                    "buyPrice": buy_price,
                    "sellPrice": sell_price,
                    "marginPerScu": round(sell_price - buy_price, 2),
                    "cargoScu": route_scu,
                    "shipCargoScu": int(total_cargo_scu),
                    "usableScu": int(effective_cargo_scu),
                    "cargoUtilizationPercent": round((route_scu / total_cargo_scu) * 100, 2),
                    "cost": cost,
                    "revenue": revenue,
                    "profit": profit,
                    "profitMarginPercent": round((profit / cost) * 100, 2) if cost else None,
                    "updatedAt": max(
                        str(buy_listing.get("updatedAt") or ""),
                        str(sell_listing.get("updatedAt") or ""),
                    )
                    or None,
                }
            )

    routes.sort(
        key=lambda route: (
            -(route.get("profit") or 0),
            -(route.get("marginPerScu") or 0),
            str(route.get("commodityName") or ""),
        )
    )

    limited_routes = routes[: max(1, max_results)]
    return {
        "ship": selected_ship,
        "budget": round(budget, 2),
        "usableScu": int(effective_cargo_scu),
        "routeCount": len(limited_routes),
        "routes": limited_routes,
    }


def _build_coverage(
    payload: dict[str, Any],
    market_listings: list[dict[str, Any]],
    ships: list[dict[str, Any]],
) -> dict[str, Any]:
    buy_count = len([listing for listing in market_listings if listing.get("operation") == "buy"])
    sell_count = len([listing for listing in market_listings if listing.get("operation") == "sell"])
    commodity_ids = {str(listing.get("commodityId") or "") for listing in market_listings if listing.get("commodityId")}
    shop_ids = {str(listing.get("shopId") or "") for listing in market_listings if listing.get("shopId")}
    return {
        "marketListingCount": len(market_listings),
        "buyListingCount": buy_count,
        "sellListingCount": sell_count,
        "commodityCoverageCount": len(commodity_ids),
        "shopCoverageCount": len(shop_ids),
        "routeShipCount": len(ships),
        "missingShipCount": len(payload.get("missingShips", []) or []),
        "latestMarketTimestamp": _latest_timestamp([listing.get("updatedAt") for listing in market_listings]),
        "localMarketUpdatedAt": payload.get("localMarketUpdatedAt"),
    }


def _build_commodity_overview(
    commodities: list[dict[str, Any]],
    market_listings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    listings_by_commodity: dict[str, list[dict[str, Any]]] = {}
    for listing in market_listings:
        commodity_id = str(listing.get("commodityId") or "")
        listings_by_commodity.setdefault(commodity_id, []).append(listing)

    overview: list[dict[str, Any]] = []
    for commodity in commodities:
        listings = listings_by_commodity.get(str(commodity.get("id") or ""), [])
        sell_prices = [
            price
            for price in (
                _as_positive_number(listing.get("price"))
                for listing in listings
                if listing.get("operation") == "sell"
            )
            if price
        ]
        lowest_buy = min(
            (_as_positive_number(listing.get("price")) for listing in listings if listing.get("operation") == "buy"),
            default=None,
        )
        highest_sell = max(sell_prices, default=None)
        overview.append(
            {
                "id": commodity.get("id"),
                "name": commodity.get("name"),
                "buyListingCount": len([listing for listing in listings if listing.get("operation") == "buy"]),
                "sellListingCount": len([listing for listing in listings if listing.get("operation") == "sell"]),
                "lowestBuyPrice": lowest_buy,
                "highestSellPrice": highest_sell,
                "spreadPerScu": round((highest_sell - lowest_buy), 2)
                if lowest_buy is not None and highest_sell is not None and highest_sell > lowest_buy
                else None,
                "latestMarketTimestamp": _latest_timestamp([listing.get("updatedAt") for listing in listings]),
            }
        )

    return sorted(
        [commodity for commodity in overview if commodity.get("buyListingCount") or commodity.get("sellListingCount")],
        key=lambda commodity: (
            -(commodity.get("spreadPerScu") or 0),
            str(commodity.get("name") or ""),
        ),
    )


def _build_shop_overview(shops: list[Any], market_listings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    listings_by_shop: dict[str, list[dict[str, Any]]] = {}
    for listing in market_listings:
        shop_id = str(listing.get("shopId") or "")
        listings_by_shop.setdefault(shop_id, []).append(listing)

    overview = []
    for shop in shops:
        if not isinstance(shop, dict):
            continue
        listings = listings_by_shop.get(str(shop.get("id") or ""), [])
        if not listings:
            continue
        overview.append(
            {
                "id": shop.get("id"),
                "name": shop.get("name"),
                "locationName": shop.get("locationName"),
                "buyListingCount": len([listing for listing in listings if listing.get("operation") == "buy"]),
                "sellListingCount": len([listing for listing in listings if listing.get("operation") == "sell"]),
                "latestMarketTimestamp": _latest_timestamp([listing.get("updatedAt") for listing in listings]),
            }
        )

    return sorted(overview, key=lambda shop: str(shop.get("name") or ""))


def _latest_timestamp(values: list[Any]) -> str | None:
    timestamps = sorted(str(value) for value in values if value)
    return timestamps[-1] if timestamps else None


def _as_positive_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number <= 0:
        return None
    return number
