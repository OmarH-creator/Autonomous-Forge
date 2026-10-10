# AUTO-262 — Exact commit verification integrity

Date: 2026-10-10
Branch: main
Milestone: guarded end-to-end maintenance integrity

## Inspection and rationale

Policy-aware planning and the guarded maintenance chain already exist. Previous AUTO-261 main head passed Python 3.10/3.11/3.12. Inspected README/docs/examples, source/tests/config/CI, policy, roadmap/state/changelog/decisions, recent commits, issues/TODOs, eight branches and nine historical PRs. Seven non-main branches are historical; all PRs closed, none appropriate to integrate.

Legacy commit-verify could report verified with matching SHA/paths but missing inspected summary/message, or when reviewed body lines occurred only as substrings of unreviewed text. It parsed line-delimited filenames and omitted root-commit paths.

## Implementation

Require summary and message, bind subject and compare exact ordered nonempty body lines; use git diff-tree --root -z with malformed-framing refusal; add adversarial deterministic and real root-commit tests, CLI docs, README, and engineering memory. Existing confirmation/side-effect boundaries are unchanged.

## Validation and limitations

Isolated real-Git root-commit NUL-path/message probe passed. Exact published SHA requires full supported-version CI. Verification does not attest authorship or file bytes; verified-commit-create supplies stronger index/parent/content checks.

## Next

Fix any CI regression; otherwise continue the same guarded milestone with a concrete legacy commit-creation staged-path integrity improvement.
