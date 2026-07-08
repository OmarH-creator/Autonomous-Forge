"""CLI for read-only patch-application readiness summaries."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from autonomous_forge.patch_application_readiness import (
    PatchApplicationReadinessError,
    format_patch_application_readiness,
    read_patch_application_readiness_data,
)


def _build_parser() -> argparse.ArgumentParser:
    """Build the parser for the patch-application readiness command."""
    parser = argparse.ArgumentParser(
        prog="forge patch-application-readiness",
        description=(
            "Summarize ready patch-application preflight and clear audit evidence without applying patches."
        ),
    )
    parser.add_argument("--preflight", required=True, help="patch-application preflight JSON output inside the repository root")
    parser.add_argument("--audit", required=True, help="patch-application audit JSON output inside the repository root")
    parser.add_argument("--root", default=".", help="repository root used to constrain evidence input paths")
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="return a failing exit code unless the patch-application readiness summary is ready",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="patch-application readiness format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the patch-application readiness summary CLI."""
    parser = _build_parser()
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        data = read_patch_application_readiness_data(Path(args.preflight), Path(args.audit), root=Path(args.root))
        if args.format == "json":
            print(json.dumps(data, indent=2, sort_keys=True))
        else:
            print(format_patch_application_readiness(data))
        if args.require_ready and data["readiness_status"] != "ready":
            return 2
    except FileNotFoundError as exc:
        print(f"Patch application readiness input not found: {exc.filename}")
        return 2
    except PatchApplicationReadinessError as exc:
        print(f"Patch application readiness refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Patch application readiness error: {exc}")
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
