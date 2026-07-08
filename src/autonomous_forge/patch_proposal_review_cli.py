"""Standalone CLI for read-only patch proposal review evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from autonomous_forge.patch_proposal_review import PatchProposalReviewError, read_patch_proposal_review


def _build_parser() -> argparse.ArgumentParser:
    """Build the parser for the standalone patch proposal review command."""
    parser = argparse.ArgumentParser(
        prog="forge-patch-proposal-review",
        description="Review a ready patch proposal manifest against fresh content-audit evidence without generating patches.",
    )
    parser.add_argument("--manifest", required=True, help="patch proposal manifest JSON output inside the repository root")
    parser.add_argument("--content-audit", required=True, help="fresh changed-content audit JSON output inside the repository root")
    parser.add_argument("--root", default=".", help="repository root used to constrain review input paths")
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="return a failing exit code unless the patch proposal review is ready",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="patch proposal review format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the standalone patch proposal review CLI."""
    parser = _build_parser()
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        output = read_patch_proposal_review(
            Path(args.manifest),
            Path(args.content_audit),
            root=Path(args.root),
            output_format=args.format,
        )
        print(output)
        if args.require_ready:
            gate_data = json.loads(
                read_patch_proposal_review(
                    Path(args.manifest),
                    Path(args.content_audit),
                    root=Path(args.root),
                    output_format="json",
                )
            )
            if gate_data["review_status"] != "ready":
                return 2
    except FileNotFoundError as exc:
        print(f"Patch proposal review input not found: {exc.filename}")
        return 2
    except PatchProposalReviewError as exc:
        print(f"Patch proposal review refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Patch proposal review error: {exc}")
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
