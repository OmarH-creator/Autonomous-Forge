# AUTO-182 — Prevent duplicate preservation receipt evidence counts

## Objective

Protect reviewer-facing preservation receipt accounting from duplicate `--completeness` references while preserving the informational-only receipt contract introduced by AUTO-181.

## Inspection

Inspected README/docs/examples, reviewer and preservation source/tests, policy/config/CI, roadmap/state/changelog/decisions, recent commits, open issues, all visible branches, and recent pull requests. The seven non-main branches remain historical/diverged. Reviewed PRs are merged, closed, obsolete, or unrelated; no integration was warranted.

## Change

`forge maintenance-review-compare` now canonicalizes repeatable `--completeness` paths against `--root` and keeps the first occurrence of each canonical file. Equivalent forms such as `artifact.json`, `./artifact.json`, and the matching absolute path therefore reach receipt discovery once rather than multiplying verified/invalid receipt counts.

Focused tests cover canonical path collapse and the CLI-to-builder handoff. Dedicated documentation records the new evidence-accounting rule.

## Safety

Receipt evidence remains `informational_only`, does not affect comparison readiness or preservation candidate ranking, and grants no write, Git, workflow, remote, network, validation, or preservation authority. The change only narrows duplicate evidence accounting.

## Validation

Deterministic focused tests were added. Direct checkout/full pytest is unavailable in this runtime because `github.com` DNS resolution fails. The connected combined-status surface exposed no prior-head checks during inspection, so no unsupported Python 3.10/3.11/3.12 green claim is made for this new head until CI becomes observable.

## Diff / noise review

Intended AUTO-182 paths are limited to the comparison CLI, focused tests, dedicated documentation, README current status/evidence notes, autonomous state, and this run record. No workflow, secret, generated, branch, PR, force-push, remote, or protection change is part of the run.

## Next action

Inspect AUTO-182 CI when observable. Any failure takes priority. If green, continue the same preservation-review milestone only for a concrete integrity or usability defect.