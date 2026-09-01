# AUTO-247 — Archive manifest durability rollback

## Repository assessment

Started from `main` at AUTO-246 head `737f12ebfd38ddde3abc09870592e07e7ef589eb`. Inspected README/docs/examples, relevant source/tests/config/CI, `.forge/policy.md`, autonomous plan/state/changelog/decisions, recent commits and Actions, all eight visible branches, open issues, PR history, and TODO/FIXME markers. The requested policy-aware `forge plan` milestone and the later guarded end-to-end maintenance chain are already shipped. Seven non-main branches remain historical/diverged and no open PR requires integration. Open issues #1, #6, and #9 are broader product/discussion requests rather than blockers for this repair.

## Objective

Close the confirmed archive-manifest post-publication durability gap without creating another read-only command. The core writer could successfully hard-link the final manifest and then fail parent-directory `fsync`, returning an error while leaving ambiguous evidence at the destination.

## Change

`_persist_text_no_clobber(...)` now SHA-256 binds the exact UTF-8 payload before publication and records when the final hard link has succeeded. If a later persistence `OSError` occurs, Forge invokes the existing ownership-checked manifest rollback and removes the destination only while its bytes still match this invocation. Changed destination bytes are preserved rather than deleted.

Added deterministic tests for rollback after a synthetic directory-sync failure and preservation of a destination changed during that failure window. Added focused documentation and updated README/status memory.

## Safety and policy

All changed files stay within policy-allowed `src/**`, `tests/**`, `docs/**`, `README.md`, and `.ai/**` areas. No `.github/workflows/**`, secret-bearing path, network access, external command authority, overwrite capability, force-push behavior, branch protection, visibility, licensing, or access-control changes were introduced.

## Validation

The automation runtime cannot obtain a checkout-capable network path, so GitHub Actions on pushed `main` is the authoritative supported-version validation. Final validation must include package installation, source compilation, installed CLI smoke testing, roadmap validation, and pytest across Python 3.10, 3.11, and 3.12.

## Limitations

Python cleanup cannot execute after `SIGKILL`, host/interpreter failure, or power loss. A second parent-directory durability-sync failure during rollback leaves filesystem durability uncertain. Without a shared filesystem lock, there remains a narrow mutation race after the final ownership digest check.

## Next action

Inspect the remaining no-clobber/durable evidence writers for another confirmed post-publication durability ambiguity, prioritizing authoritative evidence paths. Any fresh CI failure takes priority over further hardening.
