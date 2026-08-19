# AUTO-169 — Immutable hash-bound validation attachments

## Inspection

Inspected README/docs/examples, relevant source/tests/config/CI, `.forge/policy.md`, `.ai/AUTONOMOUS_PLAN.md`, `.ai/AUTONOMOUS_STATE.md`, recent commits, open issues/TODO-oriented work, every visible branch, and recent/open/closed pull requests. `main` remains the source of truth. Historical feature/maintenance branches are stale or superseded; PR #8's overwrite concern was already integrated directly on main and the remaining reviewed PRs are merged, closed, obsolete, or unrelated.

## Objective

Close the remaining validation-history persistence integrity gap: a first supplied validation observation should be preservable without mutating the durable source run-history JSON.

## Change

Added `forge validation-result-attachment-write` and the corresponding Python API. The command writes one immutable JSON sidecar under `.ai/run-history/validation-attachments/`, binds it to the exact source record bytes with SHA-256 plus byte count, refuses overwrite/path escapes/symlinks/stale source bytes, and provides verification that fails if the source record later drifts.

The historical `forge validation-result-write` behavior remains available for backward compatibility; new workflows should prefer the immutable sidecar path.

## Validation

Changed product modules and the focused AUTO-169 test file were syntax-compiled in the available scratch environment before publication. A full checkout could not be cloned because this runtime could not resolve `github.com`; final GitHub status/workflow evidence is inspected after the direct-main commit when observable, and no green result is claimed without evidence.

## Safety

No network/external-service capability, force-push, tag push, remote mutation, branch-protection change, workflow mutation, or overwrite escape hatch was added. Attachment creation requires explicit confirmation and grants no validation/commit/push authority.

## Project memory

README and `AUTONOMOUS_STATE.md` are updated at the end of the run. The large append-only plan/changelog/decisions files were inspected; if the connected write surface cannot safely append their complete contents without whole-file replacement, this run record plus state/README remain the authoritative AUTO-169 record rather than risking destructive truncation.

## Next

Verify AUTO-169 CI. If green, integrate immutable attachment verification into the durable maintenance evidence/history consumer path so validation sidecars can be discovered or supplied without weakening the existing `run-history/v1` compatibility boundary.
