# AUTO-183 — Enforce preservation receipt deduplication in the comparison core

## Objective

Close the remaining AUTO-182 integrity gap by enforcing canonical preservation-completeness input deduplication inside the comparison builder itself, not only in the CLI wrapper.

## Inspection

Inspected README/docs/examples, comparison and preservation source/tests, policy/config/CI, roadmap/state/changelog/decisions, recent commits, open issues, every visible branch, and recent pull requests. The seven non-main branches remain historical/diverged. Open issues are broader product/discussion requests. Reviewed PRs are merged, closed, obsolete, or unrelated; no integration was warranted.

## Change

`build_maintenance_review_compare_data()` now resolves each completeness input against the configured repository root, keeps the first occurrence of each canonical artifact, and performs receipt discovery once per canonical file. Direct library callers therefore receive the same duplicate-evidence protection as the CLI.

Focused regression coverage calls the builder directly with relative, dotted-relative, and absolute references to one artifact and asserts one receipt review, one verified receipt count, and one candidate match. Dedicated documentation records the direct-caller contract.

## Safety

Receipt evidence remains `informational_only`, does not affect comparison readiness or preservation ranking, and grants no write, Git, workflow, remote, network, validation, or preservation authority. The change only narrows duplicate evidence accounting.

## Validation

The canonicalization helper was exercised independently and the new focused regression is deterministic. Direct checkout/full pytest remains unavailable because `github.com` DNS resolution fails in this runtime. The connected combined-status surface exposed no AUTO-182 checks during inspection, so no unsupported Python 3.10/3.11/3.12 green claim is made until AUTO-183 CI becomes observable.

## Diff / noise review

Intended AUTO-183 paths are limited to the comparison core, focused tests, dedicated documentation, README current status/evidence notes, autonomous state, and this run record. No workflow, secret, generated, branch, PR, force-push, remote, or protection change is part of the run.

## Next action

Inspect AUTO-183 CI when observable. Any failure takes priority. If green, continue only with a concrete preservation-review or end-to-end integrity/usability defect.
