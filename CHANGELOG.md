# Changelog

All notable changes to `dss-support-tool` are documented in this file.

## [0.2.0] - 2026-04-06

### Added

- Added SC Trade-based trading snapshot support to the DSS backend.
- Added developer-maintained local trading market data with ship cargo capacity and buy/sell listings.
- Added trading planner API endpoints:
  - `/api/trading`
  - `/api/trading/routes`
- Added route calculation based on selected ship cargo capacity and available aUEC.
- Added trading snapshot loading and planner logic in the application layer.
- Added dedicated Trading planner UI in the `langpack-browser` frontend.
- Added Trading dashboard visibility and review support through the local service.
- Added test coverage for trading overview and route planning API responses.
- Added technical design documentation for the trading feature.

### Changed

- Replaced the Trading `Soon™` placeholder in the frontend with a working planner flow.
- Extended the SC Trade normalization pipeline to merge local market seed data into the committed normalized snapshot.
- Updated the committed normalized SC Trade snapshot to include:
  - market listings
  - ship cargo capacities
  - trading coverage summary values
- Kept the runtime app snapshot-only so the shipped application does not depend on live SC Trade access.

## [0.1.0] - 2026-04-05

Initial release on Sunday, April 5, 2026.

### Added

- Added the FastAPI local webservice foundation.
- Added the native desktop launcher using `PySide6`.
- Added the Windows tray controller for local service lifecycle control.
- Added snapshot-backed crafting and resource API endpoints.
- Added snapshot loading from `tool-scraper/data`.
- Added the embedded `langpack-browser` frontend integration.
- Added PyInstaller build support.
- Added the Inno Setup installer scaffold.
- Added pytest coverage for snapshot loading, catalog transforms, and API failure paths.

