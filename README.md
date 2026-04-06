# DSS Support Tool

Python-first scaffold for a Windows desktop + local webservice support tool based on the `langpack-browser` prototype.

Release history is tracked in [CHANGELOG.md](C:/dev/StarCitizen/tools/dss-support-tool/CHANGELOG.md).

## Included pieces

- FastAPI local webservice
- native desktop launcher using `PySide6` with the embedded `langpack-browser` UI
- Windows tray controller using Qt system tray for optional webserver control
- snapshot-backed API endpoints for crafting and resources
- PyInstaller build script
- Inno Setup installer scaffold

## Layout

- `src/dss_support_tool/service.py`
  FastAPI composition root and HTTP routes
- `src/dss_support_tool/application/`
  Catalog normalization and cached application services
- `src/dss_support_tool/infrastructure/snapshot_repository.py`
  Snapshot discovery and JSON loading from `../tool-scraper/data`
- `src/dss_support_tool/app_qt.py`
  Native Qt shell that hosts the same gameplay-first frontend used by `langpack-browser`
- `src/dss_support_tool/desktop_controller.py`
  Desktop-facing controller for service lifecycle orchestration
- `src/dss_support_tool/desktop.py`
  Desktop entrypoint that opens the Qt shell
- `src/dss_support_tool/tray.py`
  Tray-first entrypoint that starts minimized
- `scripts/build.ps1`
  PyInstaller build entrypoint
- `installer/dss-support-tool.iss`
  Inno Setup installer template
- `tests/`
  Pytest coverage for snapshot loading, catalog transforms, and API failure paths

## Install

```powershell
cd C:\dev\StarCitizen\tools\dss-support-tool
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[build]
```

## Run

Start the webservice only:

```powershell
dss-support-tool service
```

Start the desktop shell:

```powershell
dss-support-tool desktop
```

This opens the embedded desktop version of the `langpack-browser` UI.

Start the Windows tray controller:

```powershell
dss-support-tool tray
```

Tray mode keeps the webserver optional. You can expose the localhost web UI from the tray when needed.

## Current data sources

- crafting: latest `normalized-*.json` from `tool-scraper\data`
- resources: latest `normalized-scmdb-mining-*.json` from `tool-scraper\data`

The current scaffold exposes those through:

- `/api/health`
- `/api/status`
- `/api/crafting`
- `/api/resources`

## Build

```powershell
pwsh .\scripts\build.ps1
```

That script builds:

- `DSSSupportDesktop.exe`
- `DSSSupportTray.exe`

If Inno Setup is installed, `installer\dss-support-tool.iss` can package those into a Windows installer.
