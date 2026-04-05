from __future__ import annotations

from dss_support_tool.config import DEFAULT_CONFIG
from dss_support_tool.runtime import ServiceHandle, ServiceRuntime


class DesktopController:
    def __init__(self, runtime: ServiceRuntime) -> None:
        self._runtime = runtime
        self._handle = ServiceHandle()

    @property
    def base_url(self) -> str:
        return DEFAULT_CONFIG.base_url

    def is_service_live(self) -> bool:
        return self._runtime.is_service_live()

    def ensure_service_running(self) -> tuple[bool, str | None]:
        if self.is_service_live():
            return True, None

        self._handle = self._runtime.start_service()
        if self._runtime.wait_for_service(timeout_seconds=12):
            return True, None
        return False, self._runtime.get_startup_error()

    def stop_service(self) -> None:
        self._runtime.stop_service(self._handle)
        self._handle = ServiceHandle()

    def open_web_ui(self) -> None:
        self._runtime.open_ui()

    def status_message(self) -> str:
        if self.is_service_live():
            return f"Desktop UI connected to {self.base_url}"
        return "Webserver stopped"
