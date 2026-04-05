from __future__ import annotations

import sys
from ctypes import wintypes
import ctypes
from pathlib import Path

from PySide6.QtCore import QTimer, Qt, QUrl
from PySide6.QtGui import QAction, QColor, QGuiApplication, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu, QMessageBox, QStatusBar, QSystemTrayIcon, QToolBar

from .config import DEFAULT_CONFIG
from .desktop_controller import DesktopController
from .runtime import ServiceRuntime


ERROR_ALREADY_EXISTS = 183


class SingleInstanceGuard:
    def __init__(self, name: str) -> None:
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self.handle = self.kernel32.CreateMutexW(None, False, name)
        self.already_running = bool(self.handle) and ctypes.get_last_error() == ERROR_ALREADY_EXISTS

    def close(self) -> None:
        if self.handle:
            self.kernel32.CloseHandle(wintypes.HANDLE(self.handle))
            self.handle = None


def _icon_file() -> Path:
    package_root = Path(__file__).resolve().parent
    packaged_icon = package_root / "assets" / "app-icon.png"
    if packaged_icon.exists():
        return packaged_icon

    workspace_icon = package_root.parent.parent / "img" / "space-seals-app-icon.png"
    return workspace_icon


def _app_icon() -> QIcon:
    icon_file = _icon_file()
    if icon_file.exists():
        icon = QIcon(str(icon_file))
        if not icon.isNull():
            return icon

    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor("#0c1421"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(4, 4, 56, 56, 12, 12)
    painter.setBrush(QColor("#0f6b67"))
    painter.drawRoundedRect(10, 10, 44, 44, 10, 10)
    painter.setPen(QColor("#ecfffb"))
    font = painter.font()
    font.setBold(True)
    font.setPointSize(15)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "DSS")
    painter.end()
    return QIcon(pixmap)


class DesktopWindow(QMainWindow):
    def __init__(self, start_minimized: bool = False) -> None:
        super().__init__()
        self.start_minimized = start_minimized
        self.controller = DesktopController(ServiceRuntime())
        self.tray_icon: QSystemTrayIcon | None = None
        self.status = QStatusBar(self)
        self.setStatusBar(self.status)
        self.setWindowTitle(DEFAULT_CONFIG.app_name)
        self.setMinimumSize(1360, 900)

        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("PySide6 WebEngine is required for the desktop UI.") from exc

        self.web_view = QWebEngineView(self)
        self.setCentralWidget(self.web_view)

        self.timer = QTimer(self)
        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.refresh_status)

        self._build_toolbar()
        if self.start_minimized:
            self._build_tray()
        self.timer.start()

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Main", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        open_desktop_action = QAction("Open Desktop UI", self)
        open_desktop_action.triggered.connect(self.show_window)

        open_web_action = QAction("Open Web UI", self)
        open_web_action.triggered.connect(self.open_web_ui)

        start_action = QAction("Start Server", self)
        start_action.triggered.connect(self.start_server)

        stop_action = QAction("Stop Server", self)
        stop_action.triggered.connect(self.stop_server)

        reload_action = QAction("Reload UI", self)
        reload_action.triggered.connect(self.reload_ui)

        hide_action = QAction("Hide to Tray", self)
        hide_action.triggered.connect(self.hide_to_tray)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.quit_app)

        for action in (
            open_desktop_action,
            open_web_action,
            start_action,
            stop_action,
            reload_action,
            hide_action,
            exit_action,
        ):
            toolbar.addAction(action)

        menu = self.menuBar().addMenu("File")
        for action in (
            open_desktop_action,
            open_web_action,
            start_action,
            stop_action,
            reload_action,
            hide_action,
            exit_action,
        ):
            menu.addAction(action)

    def _build_tray(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        self.tray_icon = QSystemTrayIcon(_app_icon(), self)

        show_action = QAction("Open Desktop UI", self)
        show_action.triggered.connect(self.show_window)

        open_web_action = QAction("Open Web UI", self)
        open_web_action.triggered.connect(self.open_web_ui)

        start_action = QAction("Start Webserver", self)
        start_action.triggered.connect(self.start_server)

        stop_action = QAction("Stop Webserver", self)
        stop_action.triggered.connect(self.stop_server)

        reload_action = QAction("Reload UI", self)
        reload_action.triggered.connect(self.reload_ui)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.quit_app)

        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(open_web_action)
        tray_menu.addSeparator()
        tray_menu.addAction(start_action)
        tray_menu.addAction(stop_action)
        tray_menu.addAction(reload_action)
        tray_menu.addSeparator()
        tray_menu.addAction(exit_action)

        self.tray_icon.setToolTip(DEFAULT_CONFIG.app_name)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._handle_tray_activation)
        self.tray_icon.show()

    def bootstrap(self) -> None:
        self.start_server(show_errors=not self.start_minimized)
        self.reload_ui()
        self.refresh_status()

        if self.start_minimized and self.tray_icon and self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                DEFAULT_CONFIG.app_name,
                "Tray mode active. Use the tray icon to open the desktop UI or optional web UI.",
                QSystemTrayIcon.MessageIcon.Information,
                2500,
            )
        else:
            self.show()

    def start_server(self, show_errors: bool = True) -> None:
        started, details = self.controller.ensure_service_running()
        if not started:
            if show_errors:
                message = "The local DSS webserver did not start."
                if details:
                    message = f"{message}\n\n{details}"
                QMessageBox.critical(self, DEFAULT_CONFIG.app_name, message)
            self.refresh_status()
            return

        self.refresh_status()

    def stop_server(self) -> None:
        self.controller.stop_service()
        self.refresh_status()

    def reload_ui(self) -> None:
        if not self.controller.is_service_live():
            self.start_server()
        if self.controller.is_service_live():
            self.web_view.setUrl(QUrl(self.controller.base_url))

    def open_web_ui(self) -> None:
        if not self.controller.is_service_live():
            self.start_server()
        if self.controller.is_service_live():
            self.controller.open_web_ui()

    def refresh_status(self) -> None:
        self.status.showMessage(self.controller.status_message())

    def hide_to_tray(self) -> None:
        if not self.tray_icon or not self.tray_icon.isVisible():
            self.hide()
            return
        self.hide()
        self.tray_icon.showMessage(
            DEFAULT_CONFIG.app_name,
            "Desktop UI hidden. The optional webserver can still be managed from the tray.",
            QSystemTrayIcon.MessageIcon.Information,
            2000,
        )

    def show_window(self) -> None:
        self.reload_ui()
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _handle_tray_activation(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in {QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick}:
            self.show_window()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self.tray_icon and self.tray_icon.isVisible():
            event.ignore()
            self.hide_to_tray()
            return
        super().closeEvent(event)

    def quit_app(self) -> None:
        self.timer.stop()
        if self.tray_icon:
            self.tray_icon.hide()
        self.stop_server()
        QApplication.instance().quit()


def run_qt_app(start_minimized: bool = False) -> int:
    guard: SingleInstanceGuard | None = None
    if start_minimized:
        guard = SingleInstanceGuard("Local\\DSSSupportToolTray")
        if guard.already_running:
            guard.close()
            return 0

    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName(DEFAULT_CONFIG.app_name)
    icon = _app_icon()
    app.setWindowIcon(icon)
    QGuiApplication.setQuitOnLastWindowClosed(not start_minimized)
    if guard is not None:
        app.aboutToQuit.connect(guard.close)

    window = DesktopWindow(start_minimized=start_minimized)
    QTimer.singleShot(0, window.bootstrap)
    return app.exec()
