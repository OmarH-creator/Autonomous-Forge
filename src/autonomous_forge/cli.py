"""Command-line interface for Autonomous Forge."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    """Build the Forge command parser."""
    parser = argparse.ArgumentParser(
        prog="forge",
        description=(
            "Run local-first, dry-run checks for safe autonomous "
            "repository maintenance loops."
        ),
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="show the installed Autonomous Forge version and exit",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the Forge CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        from autonomous_forge import __version__

        print(f"forge {__version__}")
        return 0

    parser.print_help()
    return 0
