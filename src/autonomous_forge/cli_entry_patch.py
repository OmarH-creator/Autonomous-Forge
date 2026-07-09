"""Installed ``forge`` entry point router with compatibility extension commands."""

from __future__ import annotations

import sys

from autonomous_forge import __version__, cli_entry
from autonomous_forge.change_readiness_cli import main as _change_readiness_main
from autonomous_forge.commit_create_cli import main as _commit_create_main
from autonomous_forge.commit_proposal_preview_cli import main as _commit_proposal_preview_main
from autonomous_forge.commit_readiness_cli import main as _commit_readiness_main
from autonomous_forge.commit_status_review_cli import main as _commit_status_review_main
from autonomous_forge.commit_verify_cli import main as _commit_verify_main
from autonomous_forge.git_diff_review_cli import main as _git_diff_review_main
from autonomous_forge.maintenance_bundle_verify_cli import main as _maintenance_bundle_verify_main
from autonomous_forge.maintenance_evidence_bundle_cli import main as _maintenance_evidence_bundle_main
from autonomous_forge.patch_application_audit_cli import main as _patch_application_audit_main
from autonomous_forge.patch_application_preflight_cli import main as _patch_application_preflight_main
from autonomous_forge.patch_application_readiness_cli import main as _patch_application_readiness_main
from autonomous_forge.patch_apply_cli import main as _patch_apply_main
from autonomous_forge.patch_generation_preview_cli import main as _patch_generation_preview_main
from autonomous_forge.patch_proposal_draft_cli import main as _patch_proposal_draft_main
from autonomous_forge.patch_proposal_review_cli import main as _patch_proposal_review_main
from autonomous_forge.patch_text_preflight_cli import main as _patch_text_preflight_main
from autonomous_forge.patch_text_review_cli import main as _patch_text_review_main
from autonomous_forge.post_apply_validation_cli import main as _post_apply_validation_main
from autonomous_forge.post_push_verify_cli import main as _post_push_verify_main
from autonomous_forge.push_handoff_cli import main as _push_handoff_main
from autonomous_forge.push_readiness_cli import main as _push_readiness_main


_EXTENSION_COMMANDS = {
    "change-readiness": _change_readiness_main,
    "commit-create": _commit_create_main,
    "commit-proposal-preview": _commit_proposal_preview_main,
    "commit-readiness": _commit_readiness_main,
    "commit-status-review": _commit_status_review_main,
    "commit-verify": _commit_verify_main,
    "git-diff-review": _git_diff_review_main,
    "maintenance-bundle-verify": _maintenance_bundle_verify_main,
    "maintenance-evidence-bundle": _maintenance_evidence_bundle_main,
    "patch-application-audit": _patch_application_audit_main,
    "patch-application-preflight": _patch_application_preflight_main,
    "patch-application-readiness": _patch_application_readiness_main,
    "patch-apply": _patch_apply_main,
    "patch-generation-preview": _patch_generation_preview_main,
    "patch-proposal-draft": _patch_proposal_draft_main,
    "patch-proposal-review": _patch_proposal_review_main,
    "patch-text-preflight": _patch_text_preflight_main,
    "patch-text-review": _patch_text_review_main,
    "post-apply-validation": _post_apply_validation_main,
    "post-push-verify": _post_push_verify_main,
    "push-handoff": _push_handoff_main,
    "push-readiness": _push_readiness_main,
}


def main(argv: list[str] | None = None) -> int:
    """Run the installed Forge CLI, including primary-surface extension commands."""
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["--version"]:
        print(f"Autonomous Forge {__version__}")
        return 0
    if args and args[0] in _EXTENSION_COMMANDS:
        return _EXTENSION_COMMANDS[args[0]](args[1:])
    return cli_entry.main(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
