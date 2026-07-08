"""CLI for read-only patch text preflight gates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from autonomous_forge.patch_text_preflight import (
    PatchTextPreflightError,
    format_patch_text_preflight,
    read_patch_text_preflight_data,
)


def _build_parser() -> argparse.ArgumentParser:
    """Build the parser for the patch text preflight command."""
    parser = argparse.ArgumentParser(
        prog="forge patch-text-preflight",
        description="Check draft-ready evidence and explicit patch metadata without generating or applying patches.",
    )
    parser.add_argument("--draft", required=True, help="patch proposal draft JSON output inside the repository root")
    parser.add_argument("--root", default=".", help="repository root used to constrain draft input paths")
    parser.add_argument(
        "--path",
        action="append",
        default=[],
        help="explicit metadata path expected to receive patch text; repeat once per target path",
    )
    parser.add_argument(
        "--change-summary",
        action="append",
        default=[],
        help="explicit summary for the matching --path entry; repeat once per target path",
    )
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="return a failing exit code unless the patch text preflight is ready",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="patch text preflight format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the patch text preflight CLI."""
    parser = _build_parser()
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        data = read_patch_text_preflight_data(
            Path(args.draft),
            root=Path(args.root),
            declared_paths=list(args.path),
            change_summaries=list(args.change_summary),
        )
        if args.format == "json":
            print(json.dumps(data, indent=2, sort_keys=True))
        else:
            print(format_patch_text_preflight(data))
        if args.require_ready and data["preflight_status"] != "ready":
            return 2
    except FileNotFoundError as exc:
        print(f"Patch text preflight input not found: {exc.filename}")
        return 2
    except PatchTextPreflightError as exc:
        print(f"Patch text preflight refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Patch text preflight error: {exc}")
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
