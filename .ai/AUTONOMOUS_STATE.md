# Autonomous State

- Current roadmap version: v3
- Current task ID: AUTO-261 — Single-snapshot guarded patch preview and strict gate
- Current task status: IMPLEMENTED; exact-head CI is the acceptance gate
- Current branch: main
- Last run date: 2026-10-09
- Latest run summary: Bounded readiness JSON, target text, and replacement text at the actual read (1,000,001-byte sentinel for 1,000,000-byte limit). CLI --require-generated now uses the same generated preview object that it prints, closing a split-read gate mismatch.
- Repository assessment: Inspected README/docs/examples, source/tests/config/CI, policy, roadmap/state/changelog/decisions, recent commits, issues/TODOs, eight branches, and all nine visible PRs. AUTO-259 main head 3d3b125711c79b126a2f2a5e0ad30836afb67a15 passed the Python 3.10/3.11/3.12 matrix. Issue #15 remains open despite the shipped fix because the issue-close connector was blocked.
- Branch and PR disposition: Seven historical non-main branches remain inspect-only. Nine visible PRs are merged or closed, none open. No branch, PR, merge, force-push, workflow change, remote change, or protection change.
- Validation: Five-check isolated local probe passed. Deterministic repository tests cover one bounded read per input, oversized readiness, exact-limit and oversized text, read-time growth, invalid UTF-8, and one-snapshot strict CLI gating. Exact-head Actions matrix must pass before completion is claimed.
- Safety: Existing repository containment, symlink refusal, text marker checks, and downstream explicit patch confirmation remain. No new network, external command, write, commit, push, or remote authority.
- Current blockers: Issue #15 close operation is denied by connector safety checks; this does not block product operation. Final exact-head CI is the acceptance gate.
- Known limitations: Input snapshots do not authenticate authors or prevent later file changes; patch apply revalidates target bytes independently.
- Visuals: None; the current maintenance flowchart remains accurate.
- Project-memory note: AUTO-261 task, changelog, decisions, README, focused patch-preview docs, and deterministic tests record this slice.
- Recommended next objective: Resolve any CI regression first; otherwise continue the existing guarded maintenance milestone with a concrete patch/commit/execution/history defect or material workflow capability.
