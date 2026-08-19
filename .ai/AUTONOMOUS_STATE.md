# Autonomous State

- Current roadmap version: v3
- Current task ID: AUTO-170 — Consume immutable validation attachments in run-history reads
- Current task status: DONE
- Current branch: main
- Last run timestamp: 2026-08-20T03:04:00+04:00
- Latest run summary: Enhanced the existing `forge run-history-read` path so it automatically discovers bounded immutable validation sidecars under `.ai/run-history/validation-attachments/`, verifies matching attachments against the selected source record's exact bytes/SHA-256, and surfaces them in text/JSON without rewriting legacy `run-history/v1` validation fields.
- Safety: Discovery is read-only, non-recursive, capped at 100 JSON candidates, rejects a symlinked attachment directory, ignores unrelated sidecars, and fails closed when an attachment that explicitly names the selected record no longer verifies. Legacy record fields remain authoritative rather than being silently overwritten or inferred from sidecars.
- Repository assessment: README/docs, source/tests/config/CI, autonomous memory, recent commits, open issues, visible branches, and PR history were inspected. Historical branches remain stale or superseded; reviewed PRs are merged, closed, obsolete, or unrelated. No branch or PR was created or merged.
- Branch and PR disposition: Work stayed on `main`; no stale branch or PR contained newer relevant work.
- Validation: The AUTO-170 reader implementation and focused tests syntax-compiled locally before publication. Deterministic tests cover verified attachment discovery, text/JSON exposure, unrelated-sidecar exclusion, fail-closed source drift, and the existing primary `forge run-history-read` CLI route. Full local pytest remains unavailable because this runtime cannot resolve github.com. GitHub status visibility will be checked on the pushed head and no green matrix result will be claimed without evidence.
- Current blockers: Fresh GitHub commit-trust, workflow-status, and branch-protection acquisition remains policy-gated because `.forge/policy.md` requires human approval for new network/external-service access.
- Known risks and assumptions: Attachment discovery deliberately does not merge multiple observations into one inferred validation result. Malformed/unrelated sidecars are ignored unless they explicitly identify the selected source record. Replay and maintenance-bundle consumers still do not treat sidecars as executor-produced validation evidence.
- Visuals: None; this is an evidence-consumption enhancement within the existing durable-history stage and the README lifecycle diagram remains accurate.
- Project-memory note: README, this state file, and `.ai/AUTO-170.md` contain the authoritative AUTO-170 record. Large append-only plan/changelog/decisions histories were inspected but are not destructively replaced when the connected write surface cannot safely append their complete contents.
- Recommended next task: If AUTO-170 CI is green, carry verified attachment evidence into replay/maintenance evidence consumption with explicit provenance rules, without collapsing externally supplied observations into executor-produced proof.
