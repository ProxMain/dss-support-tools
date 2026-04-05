from __future__ import annotations

import socket
import subprocess
import sys
import threading
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes
import trustme
import uvicorn

from .config import DEFAULT_CONFIG
from .service import app


@dataclass
class ServiceHandle:
    thread: threading.Thread | None = None
    server: uvicorn.Server | None = None
    secure_thread: threading.Thread | None = None
    secure_server: uvicorn.Server | None = None

    def is_running(self) -> bool:
        http_running = self.thread is not None and self.thread.is_alive()
        https_running = self.secure_thread is not None and self.secure_thread.is_alive()
        return http_running or https_running


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


def is_secure_service_live() -> bool:
    if not DEFAULT_CONFIG.https_enabled:
        return False
    return _can_connect(DEFAULT_CONFIG.host, DEFAULT_CONFIG.https_port)


def wait_for_service(timeout_seconds: float = 10.0) -> bool:
    started = time.time()
    while time.time() - started < timeout_seconds:
        if is_service_live():
            return True
        time.sleep(0.2)
    return False


def wait_for_secure_service(timeout_seconds: float = 10.0) -> bool:
    if not DEFAULT_CONFIG.https_enabled:
        return True

    started = time.time()
    while time.time() - started < timeout_seconds:
        if is_secure_service_live():
            return True
        time.sleep(0.2)
    return False


def _cert_root() -> Path:
    return Path.home() / "AppData" / "Local" / "DSS Support Tool" / "certs"


def _certificate_thumbprint(certificate_path: Path) -> str:
    certificate = x509.load_pem_x509_certificate(certificate_path.read_bytes())
    return certificate.fingerprint(hashes.SHA1()).hex().upper()


def _certutil_output(*args: str) -> str:
    completed = subprocess.run(
        ["certutil", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def _is_ca_trusted(ca_path: Path) -> bool:
    thumbprint = _certificate_thumbprint(ca_path)
    normalized_output = _certutil_output("-user", "-store", "Root").replace(" ", "").upper()
    return thumbprint in normalized_output


def _trust_ca_certificate(ca_path: Path) -> None:
    if sys.platform != "win32" or _is_ca_trusted(ca_path):
        return
    _certutil_output("-user", "-addstore", "Root", str(ca_path))


def get_ca_certificate_path() -> Path:
    return _cert_root() / "localhost-ca.pem"


def _ensure_https_certificate() -> tuple[Path, Path, Path]:
    cert_root = _cert_root()
    cert_root.mkdir(parents=True, exist_ok=True)
    cert_path = cert_root / "localhost-cert.pem"
    key_path = cert_root / "localhost-key.pem"
    ca_path = get_ca_certificate_path()
    if cert_path.exists() and key_path.exists() and ca_path.exists():
        return cert_path, key_path, ca_path

    ca = trustme.CA()
    issued_cert = ca.issue_cert("localhost", DEFAULT_CONFIG.host)
    issued_cert.cert_chain_pems[0].write_to_path(cert_path)
    issued_cert.private_key_pem.write_to_path(key_path)
    ca.cert_pem.write_to_path(ca_path)
    return cert_path, key_path, ca_path


def start_service() -> ServiceHandle:
    global _service_handle, _startup_error

    if is_service_live() and (not DEFAULT_CONFIG.https_enabled or is_secure_service_live()):
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
        secure_server: uvicorn.Server | None = None
        secure_thread: threading.Thread | None = None
        if DEFAULT_CONFIG.https_enabled:
            cert_path, key_path, ca_path = _ensure_https_certificate()
            try:
                _trust_ca_certificate(ca_path)
            except Exception as exc:
                _log_startup_error(f"Failed to trust local CA certificate: {exc!r}")
            secure_server = uvicorn.Server(
                uvicorn.Config(
                    app,
                    host=DEFAULT_CONFIG.host,
                    port=DEFAULT_CONFIG.https_port,
                    loop="asyncio",
                    http="h11",
                    ws="none",
                    lifespan="on",
                    log_config=None,
                    access_log=False,
                    log_level="warning",
                    ssl_certfile=str(cert_path),
                    ssl_keyfile=str(key_path),
                )
            )
            secure_thread = threading.Thread(
                target=_run_server,
                args=(secure_server,),
                name="dss-support-service-https",
                daemon=True,
            )
        _startup_error = None
        _service_handle = ServiceHandle(
            thread=thread,
            server=server,
            secure_thread=secure_thread,
            secure_server=secure_server,
        )
        thread.start()
        if secure_thread is not None:
            secure_thread.start()
        return _service_handle


def stop_service(handle: ServiceHandle) -> None:
    global _service_handle

    if handle.server is not None and handle.thread is not None:
        handle.server.should_exit = True
        handle.thread.join(timeout=5)
        if handle.thread.is_alive():
            handle.server.force_exit = True
            handle.thread.join(timeout=1)

    if handle.secure_server is not None and handle.secure_thread is not None:
        handle.secure_server.should_exit = True
        handle.secure_thread.join(timeout=5)
        if handle.secure_thread.is_alive():
            handle.secure_server.force_exit = True
            handle.secure_thread.join(timeout=1)

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
        return wait_for_service(timeout_seconds=timeout_seconds) and wait_for_secure_service(timeout_seconds=timeout_seconds)

    def start_service(self) -> ServiceHandle:
        return start_service()

    def stop_service(self, handle: ServiceHandle) -> None:
        stop_service(handle)

    def open_ui(self) -> None:
        open_ui()

    def get_startup_error(self) -> str | None:
        return get_startup_error()
