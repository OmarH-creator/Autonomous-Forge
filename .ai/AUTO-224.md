# AUTO-224 — Bound authoritative run-history reads

Status: DONE
Date: 2026-08-28
Branch: `main`

## Objective

Close the remaining resource-exhaustion gap in the primary durable-history review path by bounding the selected authoritative `run-history/v1` record before decoding and JSON parsing.

## Inspection and rationale

The cycle inspected README/docs/examples, relevant source/tests/config/CI, `.forge/policy.md`, `.ai` plan/state/changelog/decisions, recent commits, open issues, all visible branches, recent PR history, and the current Actions baseline. AUTO-223 was green in Actions run `33183865639`. The seven non-main branches remain historical/diverged, recent PRs are merged, closed, obsolete, or unrelated, and open issues are broader project requests rather than blockers.

`forge run-history-read` already bounded immutable validation-sidecar discovery and verification, but the selected authoritative history file itself still used unbounded `Path.read_text()`. That allowed an oversized local record to consume unbounded memory before schema checks ran.

## Change

- Added a fixed 1 MiB ceiling for the authoritative history record.
- The reader consumes at most one sentinel byte beyond the ceiling before refusing oversized input.
- UTF-8 decoding and JSON parsing happen only after the byte bound passes.
- Invalid UTF-8, malformed JSON, and non-object top-level payloads continue to fail closed.
- Existing path/symlink confinement and bounded immutable-sidecar discovery remain unchanged.
- Added deterministic library and CLI coverage for oversized-record refusal plus a normal-record compatibility case.
- Updated `docs/RUN_HISTORY_READS.md` and README status/safety documentation.

## Validation

Product/test/docs head `5ea68333bd400738674aebf3bd4ef7b35ec36daf` passed GitHub Actions run `33202515294`. Python 3.10, 3.11, and 3.12 each passed package installation, source compilation, installed CLI smoke tests, roadmap validation, and pytest.

## Safety boundary

This is a local read-only hardening change. It adds no validation execution, persistence, Git mutation, workflow mutation, network access, push authority, remote mutation, branch-protection mutation, or approval authority. Records larger than 1 MiB are intentionally refused instead of streamed.

## Branch and PR disposition

Work stayed directly on `main`. No branch or PR was created, merged, or force-updated. Historical branches and PRs contained no newer applicable work.

## Visuals

No visual change was warranted because the maintenance lifecycle topology did not change.

## Next action

Inspect the remaining run-history write/result-update input paths for the same concrete unbounded authoritative-read class, or select another meaningful cross-stage integrity defect. Any fresh CI failure takes priority.
