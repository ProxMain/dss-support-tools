from __future__ import annotations

import argparse

import uvicorn

from .config import DEFAULT_CONFIG
from .desktop import main as desktop_main
from .service import app
from .tray import main as tray_main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dss-support-tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    service_parser = subparsers.add_parser("service", help="Run the local DSS webservice")
    service_parser.add_argument("--host", default=DEFAULT_CONFIG.host)
    service_parser.add_argument("--port", type=int, default=DEFAULT_CONFIG.port)

    subparsers.add_parser("desktop", help="Start the desktop shell and local service")
    subparsers.add_parser("tray", help="Start the Windows tray controller")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "service":
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")
        return 0
    if args.command == "desktop":
        return desktop_main()
    if args.command == "tray":
        return tray_main()

    parser.error(f"Unknown command: {args.command}")
    return 2

