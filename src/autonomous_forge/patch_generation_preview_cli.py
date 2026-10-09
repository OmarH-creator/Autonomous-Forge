"""Command-line entry point for guarded patch-generation previews."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.patch_generation_preview import (
    PatchGenerationPreviewError,
    format_patch_generation_preview,
    read_patch_generation_preview_data,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the patch-generation preview command."""
    parser = argparse.ArgumentParser(
        prog="forge patch-generation-preview",
        description="Generate a bounded unified diff preview from ready evidence and explicit replacement text.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain all inputs")
    parser.add_argument("--readiness", required=True, help="patch-application-readiness JSON inside the configured root")
    parser.add_argument("--path", required=True, help="repository-relative target path already present in readiness evidence")
    parser.add_argument("--replacement", required=True, help="repository-local UTF-8 file containing replacement text for the target")
    parser.add_argument(
        "--require-generated",
        action="store_true",
        help="return exit code 2 unless a non-empty patch preview is generated",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="patch-generation preview format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the guarded patch-generation preview CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = read_patch_generation_preview_data(
            Path(args.readiness),
            target_path=args.path,
            replacement_path=Path(args.replacement),
            root=Path(args.root),
        )
        output = (
            json.dumps(data, indent=2, sort_keys=True)
            if args.format == "json"
            else format_patch_generation_preview(data)
        )
    except FileNotFoundError as exc:
        print(f"Patch-generation preview input not found: {exc.filename}")
        return 2
    except PatchGenerationPreviewError as exc:
        print(f"Patch-generation preview refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Patch-generation preview error: {exc}")
        return 2

    print(output)
    if args.require_generated and not data["patch_generation_allowed"]:
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
