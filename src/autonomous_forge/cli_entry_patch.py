"""Installed ``forge`` entry point router with compatibility extension commands."""

from __future__ import annotations

import sys

from autonomous_forge import cli_entry
from autonomous_forge.patch_proposal_draft_cli import main as _patch_proposal_draft_main
from autonomous_forge.patch_proposal_review_cli import main as _patch_proposal_review_main
from autonomous_forge.patch_text_preflight_cli import main as _patch_text_preflight_main
from autonomous_forge.patch_text_review_cli import main as _patch_text_review_main


_EXTENSION_COMMANDS = {
    "patch-proposal-draft": _patch_proposal_draft_main,
    "patch-proposal-review": _patch_proposal_review_main,
    "patch-text-preflight": _patch_text_preflight_main,
    "patch-text-review": _patch_text_review_main,
}


def main(argv: list[str] | None = None) -> int:
    """Run the installed Forge CLI, including primary-surface extension commands."""
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] in _EXTENSION_COMMANDS:
        return _EXTENSION_COMMANDS[args[1:])
    return cli_entry.main(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
