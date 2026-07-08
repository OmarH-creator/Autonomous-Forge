"""Command-line entry point for explicitly confirmed guarded patch apply."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.patch_apply import PatchApplyError, apply_patch_from_preview, format_patch_apply


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the guarded patch-apply command."""
    parser = argparse.ArgumentParser(
        prog="forge patch-apply",
        description="Apply one replacement file after generated preview and change-readiness evidence pass.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain all inputs")
    parser.add_argument("--preview", required=True, help="patch-generation-preview JSON inside the configured root")
    parser.add_argument("--change-readiness", required=True, help="change-readiness JSON inside the configured root")
    parser.add_argument("--path", required=True, help="repository-relative target path to replace")
    parser.add_argument("--replacement", required=True, help="repository-local UTF-8 file containing replacement text")
    parser.add_argument(
        "--confirm-apply",
        action="store_true",
        help="required explicit confirmation before the target file is overwritten",
    )
    parser.add_argument(
        "--require-applied",
        action="store_true",
        help="return exit code 2 unless the target file was changed",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="patch-apply report format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the guarded patch-apply CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = apply_patch_from_preview(
            Path(args.preview),
            change_readiness_path=Path(args.change_readiness),
            target_path=args.path,
            replacement_path=Path(args.replacement),
            root=Path(args.root),
            confirm_apply=args.confirm_apply,
        )
    except FileNotFoundError as exc:
        print(f"Patch apply input not found: {exc.filename}")
        return 2
    except PatchApplyError as exc:
        print(f"Patch apply refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Patch apply error: {exc}")
        return 2

    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(format_patch_apply(data))
    if not data["file_changed"]:
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
