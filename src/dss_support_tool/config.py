from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent.parent
WORKSPACE_TOOLS_ROOT = PROJECT_ROOT.parent
IS_FROZEN = bool(getattr(sys, "frozen", False))


@dataclass(frozen=True)
class AppPaths:
    workspace_tools_root: Path
    bundle_root: Path
    scraper_data_root: Path
    static_root: Path
    packaged_langpack_dist_root: Path
    langpack_dist_root: Path


@dataclass(frozen=True)
class FrontendAssets:
    directory: Path
    source: str
    is_placeholder: bool = False


@dataclass(frozen=True)
class AppConfig:
    host: str = os.environ.get("DSS_SUPPORT_HOST", "127.0.0.1")
    port: int = int(os.environ.get("DSS_SUPPORT_PORT", "8765"))
    https_enabled: bool = os.environ.get("DSS_SUPPORT_HTTPS_ENABLED", "1").strip().lower() not in {"0", "false", "no"}
    https_port: int = int(os.environ.get("DSS_SUPPORT_HTTPS_PORT", "8766"))
    app_name: str = "DSS Support Tool"

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def secure_base_url(self) -> str | None:
        if not self.https_enabled:
            return None
        return f"https://{self.host}:{self.https_port}"


def build_default_paths() -> AppPaths:
    static_root = PACKAGE_ROOT / "static"
    bundle_root = Path(getattr(sys, "_MEIPASS", PACKAGE_ROOT.parent))
    packaged_langpack_dist_root = PACKAGE_ROOT / "langpack_dist"
    scraper_data_root = bundle_root / "tool-scraper" / "data" if IS_FROZEN else WORKSPACE_TOOLS_ROOT / "tool-scraper" / "data"
    return AppPaths(
        workspace_tools_root=WORKSPACE_TOOLS_ROOT,
        bundle_root=bundle_root,
        scraper_data_root=scraper_data_root,
        static_root=static_root,
        packaged_langpack_dist_root=packaged_langpack_dist_root,
        langpack_dist_root=WORKSPACE_TOOLS_ROOT / "langpack-browser" / "dist",
    )


def resolve_frontend_assets(paths: AppPaths) -> FrontendAssets:
    if paths.langpack_dist_root.exists():
        return FrontendAssets(directory=paths.langpack_dist_root, source="workspace-langpack")
    if IS_FROZEN and paths.packaged_langpack_dist_root.exists():
        return FrontendAssets(directory=paths.packaged_langpack_dist_root, source="packaged-langpack")
    return FrontendAssets(directory=paths.static_root, source="placeholder-static", is_placeholder=True)


DEFAULT_CONFIG = AppConfig()
DEFAULT_PATHS = build_default_paths()
