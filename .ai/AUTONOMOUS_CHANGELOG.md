# Autonomous Changelog

## 2026-07-07 — AUTO-015

- Task ID: AUTO-015
- Summary: Added `forge run-summary --format json`, a machine-readable preview that uses the same semantic fields as the default text output.
- Validation completed: Added deterministic CLI coverage that parses the JSON payload and checks every documented field. Static review confirmed that text and JSON share one preview-data builder. Pull-request CI has not yet been observed.
- Commit hash: pending pull-request validation and merge.
- Follow-up notes: Observe CI before further behavior changes. A local persistence feature requires a separate policy-aware roadmap task.

## Historical record

Earlier autonomous maintenance entries remain available in repository history. This changelog is now continued from AUTO-015 with the current, reviewable execution record.