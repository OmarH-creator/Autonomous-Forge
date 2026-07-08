"""CLI for read-only patch-application provenance audits."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from autonomous_forge.patch_application_audit import (
    PatchApplicationAuditError,
    format_patch_application_audit,
    read_patch_application_audit_data,
)


def _build_parser() -> argparse.ArgumentParser:
    """Build the parser for the patch-application audit command."""
    parser = argparse.ArgumentParser(
        prog="forge patch-application-audit",
        description=(
            "Audit ready patch-application preflight provenance evidence without generating or applying patches."
        ),
    )
    parser.add_argument("--preflight", required=True, help="patch-application preflight JSON output inside the repository root")
    parser.add_argument("--root", default=".", help="repository root used to constrain preflight input paths")
    parser.add_argument(
        "--require-clear",
        action="store_true",
        help="return a failing exit code unless the patch-application provenance audit is clear",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="patch-application provenance audit format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the patch-application provenance audit CLI."""
    parser = _build_parser()
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        data = read_patch_application_audit_data(Path(args.preflight), root=Path(args.root))
        if args.format == "json":
            print(json.dumps(data, indent=2, sort_keys=True))
        else:
            print(format_patch_application_audit(data))
        if args.require_clear and data["audit_status"] != "clear":
            return 2
    except FileNotFoundError as exc:
        print(f"Patch application audit input not found: {exc.filename}")
        return 2
    except PatchApplicationAuditError as exc:
        print(f"Patch application audit refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Patch application audit error: {exc}")
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
