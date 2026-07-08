"""Installed ``forge`` entry point router with compatibility extension commands."""

from __future__ import annotations

import sys

from autonomous_forge import cli_entry
from autonomous_forge.patch_proposal_review_cli import main as _patch_proposal_review_main


def main(argv: list[str] | None = None) -> int:
    """Run the installed Forge CLI, including primary-surface extension commands."""
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] == "patch-proposal-review":
        return _patch_proposal_review_main(args[1:])
    return cli_entry.main(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
