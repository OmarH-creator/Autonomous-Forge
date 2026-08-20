# Autonomous State

- Current roadmap version: v3
- Current task ID: AUTO-171 — Preserve immutable validation provenance in maintenance replay
- Current task status: DONE
- Current branch: main
- Last run timestamp: 2026-08-20T07:03:52+04:00
- Latest run summary: Extended the existing `forge maintenance-replay-summary` path with optional `--validation-record` input so verified immutable validation sidecars can be carried into replay output as fingerprinted external advisory provenance without rewriting source history or being promoted to executor-produced validation proof.
- Safety: Matching sidecars are discovered through the existing bounded run-history reader, remain source-byte/SHA-256 verified, are fingerprinted themselves with a 1 MB bound, reject symlink/path escapes, and must not contradict retained bundle validation steps or expected-file-change context. External observations are explicitly marked `executor_validation_equivalent: false` and `replay_gate_effect: advisory_only`; they never change replay blockers or rescue a blocked bundle.
- Repository assessment: README/docs/examples, source/tests/config/CI, policy, autonomous memory, recent commits, open issues, TODO/FIXME/XXX search, all visible branches, and recent PR history were inspected. Historical branches remain stale or superseded; reviewed PRs are merged, closed, obsolete, or unrelated. No branch or PR was created or merged.
- Branch and PR disposition: Work stayed on `main`; no stale branch or PR contained newer relevant implementation work.
- Validation: The new replay-provenance module, updated replay CLI, and focused AUTO-171 regression tests syntax-compiled in the scratch environment. Tests cover successful advisory provenance, sidecar fingerprinting, contradictory validation-step refusal, and JSON CLI exposure. The configured CI still targets Python 3.10/3.11/3.12 with install, compile, installed CLI smoke, roadmap validation, and pytest. GitHub's combined-status endpoint currently exposes no checks for the AUTO-171 pushed SHA, so no green final-matrix claim is recorded without evidence.
- Current blockers: Fresh GitHub commit-trust, workflow-status, and branch-protection acquisition remains policy-gated because `.forge/policy.md` requires human approval for new network/external-service access. CI visibility through the available status surface is incomplete for the newest head.
- Known risks and assumptions: Immutable attachments prove exact byte binding and preserve an externally supplied observation; they do not prove that Forge executed a validation command or that the supplied result is truthful. Replay refuses retained-context contradictions but does not infer correctness from external observations.
- Visuals: None; this is a provenance enhancement inside the existing replay/durable-evidence stage and the README lifecycle diagram remains accurate.
- Project-memory note: README and this state file contain the authoritative AUTO-171 record. Large append-only plan/changelog/decisions histories were inspected but are not destructively replaced when the connected write surface cannot safely append their complete contents.
- Recommended next task: Inspect AUTO-171 CI when observable; if green, carry the same explicit external-observation provenance class into maintenance-bundle/history consumption without allowing it to satisfy executor-validation readiness.
