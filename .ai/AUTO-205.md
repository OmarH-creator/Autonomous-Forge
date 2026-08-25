# AUTO-205 — Refuse truncated live workflow-status evidence

## Repository assessment

Inspected README/docs/examples, relevant source/tests/config/CI, `.forge/policy.md`, roadmap/state/changelog/decisions, recent commits, open issues, all eight visible branches, recent PR history, TODO/FIXME/XXX search, and the pre-run Actions result. The seven non-main branches remain historical/diverged; recent PRs are merged, closed, obsolete, or unrelated. Open issues #1, #6, and #9 are broader product/discussion requests rather than blockers. No old branch or PR contained newer work that should be integrated.

## Objective and rationale

Harden the existing `commit-status-review --from-github` / `verified-push-run --live-status` path against incomplete evidence caused by `gh run list --limit N`. A bounded result set can contain exactly N visible workflow runs while additional runs exist outside the window; without a completeness probe, a failed, pending, or unknown run could be omitted from status review and push readiness.

## Change

- Keep the admitted review limit at 20 workflow runs.
- Query one additional sentinel row (`limit + 1`).
- Fail closed with `completeness is unknown` when the sentinel is present.
- Record `workflow_run_limit` and `workflow_run_collection_complete=true` only on successful bounded collection.
- Keep AUTO-203 per-run `headSha` binding and AUTO-204 15-second subprocess timeouts intact.
- Document the same completeness boundary in commit-status and verified-push command documentation and README.

## Validation

The pre-run AUTO-204 head `228af26cd1bc99a932e8b8a2b22cbfb93aee31e9` passed Actions run `32841036136` on Python 3.10, 3.11, and 3.12. AUTO-205 deterministic coverage verifies that the default 20-run review asks GitHub CLI for 21 rows, successful payloads record completeness metadata, and a 2-run review receiving the third sentinel row is refused even when the omitted row could contain a failure. Final-head Actions is inspected before completion is reported.

## Safety and policy

This tightens an already-approved external-status capability and adds no new external command, external service, push authority, workflow rerun, force-push/tag-push behavior, remote/protection mutation, workflow permission, or secret handling. The sentinel is never admitted into successful evidence. All changed paths are within policy-approved `src/**`, `tests/**`, `docs/**`, README, and `.ai/**` areas; `.github/workflows/**` and secret paths remain untouched.

## Project-memory disposition

Roadmap direction is unchanged and this is an implementation-level fail-closed hardening of the existing live-status decision, so `AUTONOMOUS_PLAN.md` and `DECISIONS.md` require no semantic rewrite. `AUTONOMOUS_CHANGELOG.md` was inspected, but the connector exposes no safe append primitive that guarantees preservation of the complete historical file; this dedicated immutable run record plus README/state/docs provide the factual AUTO-205 changelog without risking destructive replacement.

## Next action

Inspect AUTO-205 final-head CI first. Any failure takes priority. If green, continue the integrated guarded-maintenance milestone with another concrete cross-stage integrity defect or a policy-permitted evidence-handoff reduction rather than another isolated read-only command.