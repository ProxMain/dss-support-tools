from __future__ import annotations

from dss_support_tool.app_qt import run_qt_app


def main() -> int:
    return run_qt_app(start_minimized=False)


if __name__ == "__main__":
    raise SystemExit(main())
