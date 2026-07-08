"""CLI for read-only patch-application preflight gates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from autonomous_forge.patch_application_preflight import (
    PatchApplicationPreflightError,
    format_patch_application_preflight,
    read_patch_application_preflight_data,
)


def _build_parser() -> argparse.ArgumentParser:
    """Build the parser for the patch-application preflight command."""
    parser = argparse.ArgumentParser(
        prog="forge patch-application-preflight",
        description=(
            "Check ready patch text review evidence and explicit patch provenance metadata "
            "without generating or applying patches."
        ),
    )
    parser.add_argument("--review", required=True, help="patch text review JSON output inside the repository root")
    parser.add_argument("--root", default=".", help="repository root used to constrain review input paths")
    parser.add_argument(
        "--path",
        action="append",
        default=[],
        help="explicit path with reviewed patch provenance; repeat once per reviewed path",
    )
    parser.add_argument(
        "--patch-source",
        action="append",
        default=[],
        help="explicit patch source label for the matching --path entry; repeat once per reviewed path",
    )
    parser.add_argument(
        "--expected-summary",
        action="append",
        default=[],
        help="expected reviewed patch summary for the matching --path entry; repeat once per reviewed path",
    )
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="return a failing exit code unless the patch-application preflight is ready",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="patch-application preflight format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the patch-application preflight CLI."""
    parser = _build_parser()
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        data = read_patch_application_preflight_data(
            Path(args.review),
            root=Path(args.root),
            provenance_paths=list(args.path),
            patch_sources=list(args.patch_source),
            expected_summaries=list(args.expected_summary),
        )
        if args.format == "json":
            print(json.dumps(data, indent=2, sort_keys=True))
        else:
            print(format_patch_application_preflight(data))
        if args.require_ready and data["preflight_status"] != "ready":
            return 2
    except FileNotFoundError as exc:
        print(f"Patch application preflight input not found: {exc.filename}")
        return 2
    except PatchApplicationPreflightError as exc:
        print(f"Patch application preflight refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Patch application preflight error: {exc}")
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
