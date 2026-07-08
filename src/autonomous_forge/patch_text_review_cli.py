"""CLI for read-only patch text review gates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from autonomous_forge.patch_text_review import (
    PatchTextReviewError,
    format_patch_text_review,
    read_patch_text_review_data,
)


def _build_parser() -> argparse.ArgumentParser:
    """Build the parser for the patch text review command."""
    parser = argparse.ArgumentParser(
        prog="forge patch-text-review",
        description="Review ready preflight evidence and explicit patch text summaries without generating or applying patches.",
    )
    parser.add_argument("--preflight", required=True, help="patch text preflight JSON output inside the repository root")
    parser.add_argument("--root", default=".", help="repository root used to constrain preflight input paths")
    parser.add_argument(
        "--path",
        action="append",
        default=[],
        help="explicit reviewed path expected to receive patch text; repeat once per target path",
    )
    parser.add_argument(
        "--patch-summary",
        action="append",
        default=[],
        help="explicit patch text summary for the matching --path entry; repeat once per target path",
    )
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="return a failing exit code unless the patch text review is ready",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="patch text review format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the patch text review CLI."""
    parser = _build_parser()
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        data = read_patch_text_review_data(
            Path(args.preflight),
            root=Path(args.root),
            reviewed_paths=list(args.path),
            patch_summaries=list(args.patch_summary),
        )
        if args.format == "json":
            print(json.dumps(data, indent=2, sort_keys=True))
        else:
            print(format_patch_text_review(data))
        if args.require_ready and data["review_status"] != "ready":
            return 2
    except FileNotFoundError as exc:
        print(f"Patch text review input not found: {exc.filename}")
        return 2
    except PatchTextReviewError as exc:
        print(f"Patch text review refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Patch text review error: {exc}")
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
