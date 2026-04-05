from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .application.catalog_service import CatalogService
from .config import DEFAULT_CONFIG, DEFAULT_PATHS, AppPaths, FrontendAssets, resolve_frontend_assets
from .errors import SnapshotLoadError
from .infrastructure.snapshot_repository import SnapshotRepository


def create_app(
    *,
    catalog_service: CatalogService | None = None,
    paths: AppPaths = DEFAULT_PATHS,
) -> FastAPI:
    app = FastAPI(title="DSS Support Tool", version="0.1.0")
    service = catalog_service or CatalogService(SnapshotRepository(paths))
    frontend = resolve_frontend_assets(paths)

    @app.exception_handler(SnapshotLoadError)
    async def snapshot_error_handler(_, exc: SnapshotLoadError) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    static_dir = frontend.directory
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/api/health")
    def health() -> dict[str, bool]:
        return {"ok": True}

    @app.get("/api/status")
    def status() -> dict[str, object]:
        return {
            "app": DEFAULT_CONFIG.app_name,
            "baseUrl": DEFAULT_CONFIG.base_url,
            "frontend": _frontend_status(frontend),
            "crafting": _attempt(service.get_crafting_index),
            "resources": _attempt(service.get_resource_index),
        }

    @app.get("/api/crafting")
    def crafting() -> dict[str, object]:
        return service.get_crafting_index()

    @app.get("/api/crafting/{category_id}")
    def crafting_category(category_id: str) -> dict[str, object]:
        payload = service.get_crafting_data()
        for category in payload["categories"]:
            if category["id"] == category_id:
                return {"updatedFrom": payload["updatedFrom"], **category}
        raise HTTPException(status_code=404, detail="Crafting category not found")

    @app.get("/api/resources")
    def resources() -> dict[str, object]:
        return service.get_resource_index()

    @app.get("/api/resources/{family_id}")
    def resource_family(family_id: str) -> dict[str, object]:
        payload = service.get_resource_data()
        for family in payload["families"]:
            if family["id"] == family_id:
                return {"updatedFrom": payload["updatedFrom"], **family}
        raise HTTPException(status_code=404, detail="Resource family not found")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str) -> FileResponse:
        candidate = static_dir / full_path
        if candidate.exists() and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(static_dir / "index.html")

    return app


def _attempt(loader) -> dict[str, object]:
    try:
        return {"ok": True, **loader()}
    except SnapshotLoadError as exc:
        return {"ok": False, "error": str(exc)}


def _frontend_status(frontend: FrontendAssets) -> dict[str, object]:
    return {
        "source": frontend.source,
        "path": str(frontend.directory),
        "placeholder": frontend.is_placeholder,
    }


app = create_app()
