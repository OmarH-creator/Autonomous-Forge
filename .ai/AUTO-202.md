# AUTO-202 — Bind live workflow status into verified push orchestration

## Objective

Reduce one meaningful caller-managed evidence handoff in the integrated guarded-maintenance workflow by allowing `forge verified-push-run` to collect workflow status for the exact verified created commit on explicit request, while preserving the existing supplied-status path and independent push confirmation.

## Repository inspection

Inspected README and command documentation; verified push/status/trust/commit implementation and focused tests; repository policy and configured CI; `.ai` roadmap/state/changelog/decisions; recent commits; open issues; all eight visible branches; recent pull requests; and the final AUTO-201 Actions result. AUTO-201 final head `26482e0e0bf75afb5f0fe2747e6e9a80d5565b5a` passed its push-triggered Test workflow. The seven non-main branches remain historical/diverged. Recent PRs are merged, closed, obsolete, or unrelated. Open issues #1, #6, and #9 are broader project/discussion requests rather than release blockers.

## Rationale

The push orchestration already consumed reviewed commit-status evidence, while a separate shipped command could explicitly collect bounded GitHub workflow status for one commit. Requiring callers to persist and reload that intermediate status-review JSON created avoidable stale-evidence friction in the end-to-end path. Reusing the existing collector in the push orchestrator materially advances workflow integration without adding another standalone command or granting new push authority.

An initially considered in-memory commit-trust acquisition path was not implemented because repository policy requires human approval before expanding product-code external-command execution. AUTO-202 instead reuses the already-established explicit live workflow-status boundary.

## Work completed

- Added mutually exclusive `--status-review` and `--live-status` inputs to `forge verified-push-run`.
- Live mode unwraps and verifies the change artifact before querying GitHub.
- The query is bound to the exact `created_commit` proven by verified commit evidence.
- The existing `collect_github_workflow_status_payload()` collector is reused and its output is converted through `build_commit_status_review_data()`.
- The resulting status review must still name the exact verified commit before entering push readiness.
- Supplied repository-local status-review JSON remains backward compatible.
- Added deterministic tests for exact SHA binding, refusal before verified commit evidence, and primary CLI exposure.
- Updated verified-push documentation and repository status records.

## Safety boundary

`--live-status` is explicit. It reuses the existing bounded GitHub workflow-list collector and does not rerun workflows, mutate checks, apply patches, create commits, authorize pushes, force-push, push tags, change remotes, or change branch protection. `--confirm-push` remains a separate required side-effect gate. Malformed, uncommitted, or unverified change evidence blocks before the live query.

Commit-trust and branch-protection evidence remain caller-supplied. Live workflow state does not prove validation sufficiency or signer identity.

## Branch and PR disposition

Work was performed directly on `main`. No branch, pull request, merge, or force update was created. Historical branches remain inspect-only evidence and no PR contained newer relevant implementation work.

## Validation

Targeted deterministic coverage was added for exact created-commit binding, refusal to query before a verified commit exists, backward-compatible supplied status input, and primary CLI help. Push-triggered GitHub Actions run `32804309834` on AUTO-202 head `40b924d7c05a5cfe3c25137ffb1eeb0c9e1cd52f` completed successfully. Python 3.10, 3.11, and 3.12 each passed package installation, source compilation, installed CLI smoke tests, roadmap validation, and pytest.

## Visuals

No new visual was warranted because the lifecycle topology is unchanged; this removes an intermediate evidence-file handoff inside the existing verified push stage.

## Next action

Continue the same integrated maintenance milestone with the next meaningful trust/protection evidence handoff reduction permitted by policy, or the next concrete cross-stage integrity defect. Any future CI failure takes priority.
