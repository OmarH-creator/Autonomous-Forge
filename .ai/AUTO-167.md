# AUTO-167 — Make validation-result attachment writes atomic

## Objective
Close a concrete durability gap in the end-to-end maintenance evidence path: the first confirmed `validation-result-write` attachment still rewrote the durable run-history JSON with a direct `Path.write_text`, so an I/O/process failure at that boundary could leave the record truncated even though logical replacement was already single-assignment.

## Repository and branch/PR assessment
The run inspected README/docs/examples, relevant source/tests/config/CI, `.forge/policy.md`, autonomous state/roadmap/changelog/decisions, recent commits, open issues, TODO-oriented code search, all visible branches, and recent pull requests. Historical feature and maintenance branches remain stale or superseded by `main`; reviewed PRs are merged, closed, obsolete, or unrelated. No branch or PR was created or merged.

## Change
`validation_result_writer` now writes the confirmed first attachment through a same-directory temporary file, flushes and `fsync`s it, and replaces the destination with `os.replace`. If the final replace fails, Forge removes the temporary file and raises a guarded `ValidationResultWriteError`, leaving the original record bytes intact.

The writer also snapshots the source bytes before building the attachment and rechecks them immediately before replacement. If another writer changed the selected history record during payload construction, Forge refuses the stale attachment and preserves the newer bytes.

## Tests
Focused deterministic coverage proves:

1. a simulated `os.replace` failure preserves the original run-history bytes and cleans the temporary sibling file; and
2. a source record changed during payload construction is detected before replacement and the concurrent bytes remain untouched.

## Safety rationale
This narrows write authority rather than expanding it. Existing run-history path confinement, JSON/schema/result checks, single-assignment validation evidence, retained validation context, and explicit `--confirm-write` remain intact. No network/external-service access, new external command, force-push, tag push, remote mutation, branch-protection change, or workflow change is introduced.

## Validation
The changed writer and focused regression tests were syntax-checked in the available scratch Python environment before publication. Full repository pytest depends on the push-triggered Python 3.10/3.11/3.12 CI becoming observable; no green matrix result is claimed without evidence.

## Limitation and next action
The pre-replacement byte comparison is not a shared multi-process lock, and the legacy command still mutates the selected history record on its first confirmed attachment. Inspect AUTO-167 CI first; if green, consider eliminating that remaining in-place mutation or close the next concrete provenance/persistence integrity gap in the same maintenance milestone.
