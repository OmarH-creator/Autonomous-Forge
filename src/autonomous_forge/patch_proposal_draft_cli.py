"""Standalone CLI for read-only patch proposal draft previews."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from autonomous_forge.patch_proposal_draft import PatchProposalDraftError, read_patch_proposal_draft


def _build_parser() -> argparse.ArgumentParser:
    """Build the parser for the standalone patch proposal draft command."""
    parser = argparse.ArgumentParser(
        prog="forge-patch-proposal-draft",
        description="Preview a patch proposal draft from ready proposal-review evidence without generating patches.",
    )
    parser.add_argument("--review", required=True, help="patch proposal review JSON output inside the repository root")
    parser.add_argument("--root", default=".", help="repository root used to constrain review input paths")
    parser.add_argument(
        "--require-draft-ready",
        action="store_true",
        help="return a failing exit code unless the draft preview is ready",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="patch proposal draft format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the standalone patch proposal draft CLI."""
    parser = _build_parser()
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        output = read_patch_proposal_draft(
            Path(args.review),
            root=Path(args.root),
            output_format=args.format,
        )
        print(output)
        if args.require_draft_ready:
            gate_data = json.loads(
                read_patch_proposal_draft(
                    Path(args.review),
                    root=Path(args.root),
                    output_format="json",
                )
            )
            if gate_data["draft_status"] != "draft-ready":
                return 2
    except FileNotFoundError as exc:
        print(f"Patch proposal draft input not found: {exc.filename}")
        return 2
    except PatchProposalDraftError as exc:
        print(f"Patch proposal draft refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Patch proposal draft error: {exc}")
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
