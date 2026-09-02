# AUTO-251 — Bounded verified-push evidence reads

## Objective

Close a concrete TOCTOU memory-safety gap in the real `forge verified-push-run` execution path without adding any new command or authority surface.

## Repository assessment

Inspected README/docs/examples, source/tests/config/CI inventory, `.forge/policy.md`, `.ai/AUTONOMOUS_PLAN.md`, `.ai/AUTONOMOUS_STATE.md`, `.ai/AUTONOMOUS_CHANGELOG.md`, `.ai/DECISIONS.md`, recent commits and Actions, all eight visible branches, open issues, TODO-oriented source search, and recent PR history. The policy-aware `forge plan` milestone and the guarded maintenance chain are already shipped. Seven non-`main` branches remain historical/diverged; there are no open PRs. Issues #1, #6, and #9 are broader product/discussion requests rather than blockers for this execution-integrity repair.

## Defect

`src/autonomous_forge/verified_push_run.py::_read_json` checked `stat().st_size` against the 1,000,000-byte review limit and then used unbounded `read_text()`. A repository-local evidence file could grow after the size check and before/during the read, bypassing the intended memory bound in the push/post-push orchestration path.

## Change

The reader now opens the file in binary mode and performs one bounded read of `_MAX_JSON_BYTES + 1`. More than 1,000,000 bytes is rejected before UTF-8 decoding or JSON parsing. Existing repository confinement, symlink rejection, `.json` enforcement, UTF-8 validation, and JSON-object validation remain in force.

## Validation

Added deterministic tests for a valid bounded object, oversized input, exact sentinel read size, and invalid UTF-8. The repository's GitHub Actions matrix is the authoritative whole-repository validation because this automation environment cannot clone GitHub directly.

## Branch/PR disposition

Worked directly on `main`. No branch, PR, merge, force-push, remote mutation, workflow change, or protection change was used. Historical branches/PRs were not integrated because current `main` supersedes their relevant capabilities and no open PR exists.

## Visuals

None. The workflow topology is unchanged; this is an input-boundary hardening inside the existing verified push execution path.

## Limitations

The bounded read prevents unbounded memory consumption but does not make the evidence file immutable. Existing provenance, digest, commit-identity, trust/status, branch-policy, and post-push verification checks continue to determine whether evidence is authoritative.

## Next action

Continue through post-push verification into durable maintenance evidence and inspect commit/remote identity binding for a concrete stale-state defect. Any fresh CI failure takes priority.
