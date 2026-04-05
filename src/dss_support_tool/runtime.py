from __future__ import annotations

import socket
import threading
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path

import uvicorn

from .config import DEFAULT_CONFIG
from .service import app


@dataclass
class ServiceHandle:
    thread: threading.Thread | None = None
    server: uvicorn.Server | None = None

    def is_running(self) -> bool:
        return self.thread is not None and self.thread.is_alive()


_service_lock = threading.Lock()
_service_handle = ServiceHandle()
_startup_error: str | None = None


def _log_startup_error(message: str) -> None:
    log_dir = Path.home() / "AppData" / "Local" / "DSS Support Tool" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    with (log_dir / "startup.log").open("a", encoding="utf-8") as handle:
        handle.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}\n")


def _run_server(server: uvicorn.Server) -> None:
    global _startup_error

    try:
        server.run()
    except BaseException as exc:  # pragma: no cover - packaged runtime path
        _startup_error = repr(exc)
        _log_startup_error(f"Embedded server failed: {exc!r}")
        raise


def _can_connect(host: str, port: int, timeout: float = 0.25) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, port)) == 0


def is_service_live() -> bool:
    return _can_connect(DEFAULT_CONFIG.host, DEFAULT_CONFIG.port)


def wait_for_service(timeout_seconds: float = 10.0) -> bool:
    started = time.time()
    while time.time() - started < timeout_seconds:
        if is_service_live():
            return True
        time.sleep(0.2)
    return False


def start_service() -> ServiceHandle:
    global _service_handle, _startup_error

    if is_service_live():
        return ServiceHandle()

    with _service_lock:
        if _service_handle.is_running():
            return _service_handle

        server = uvicorn.Server(
            uvicorn.Config(
                app,
                host=DEFAULT_CONFIG.host,
                port=DEFAULT_CONFIG.port,
                loop="asyncio",
                http="h11",
                ws="none",
                lifespan="on",
                log_config=None,
                access_log=False,
                log_level="warning",
            )
        )
        thread = threading.Thread(
            target=_run_server,
            args=(server,),
            name="dss-support-service",
            daemon=True,
        )
        _startup_error = None
        _service_handle = ServiceHandle(thread=thread, server=server)
        thread.start()
        return _service_handle


def stop_service(handle: ServiceHandle) -> None:
    global _service_handle

    if handle.server is None or handle.thread is None:
        return

    handle.server.should_exit = True
    handle.thread.join(timeout=5)
    if handle.thread.is_alive():
        handle.server.force_exit = True
        handle.thread.join(timeout=1)

    with _service_lock:
        if handle is _service_handle:
            _service_handle = ServiceHandle()


def open_ui() -> None:
    webbrowser.open(DEFAULT_CONFIG.base_url)


def get_startup_error() -> str | None:
    return _startup_error


class ServiceRuntime:
    def is_service_live(self) -> bool:
        return is_service_live()

    def wait_for_service(self, timeout_seconds: float = 10.0) -> bool:
        return wait_for_service(timeout_seconds=timeout_seconds)

    def start_service(self) -> ServiceHandle:
        return start_service()

    def stop_service(self, handle: ServiceHandle) -> None:
        stop_service(handle)

    def open_ui(self) -> None:
        open_ui()

    def get_startup_error(self) -> str | None:
        return get_startup_error()
