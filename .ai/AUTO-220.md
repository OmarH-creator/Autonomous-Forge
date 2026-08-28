# AUTO-220 — Bound authoritative preservation-completeness input

## Inspection

Reviewed README/docs/examples, preservation-receipt source and tests, `.forge/policy.md`, `.ai/AUTONOMOUS_PLAN.md`, `.ai/AUTONOMOUS_STATE.md`, `.ai/AUTONOMOUS_CHANGELOG.md`, `.ai/DECISIONS.md`, recent commits, current Actions, open issues, all eight visible branches, and recent PR history. The seven non-`main` branches remain historical/diverged; recent PRs are merged, closed, obsolete, or unrelated, so no branch or PR warranted integration.

## Objective and rationale

AUTO-219 bounded the potentially many receipt-directory candidates, but deliberately left the selected preservation-completeness artifact unbounded. That authoritative JSON is consumed by receipt preview/write, verification, and discovery, so a local caller could still force those paths to load an arbitrarily large file. Close that resource-integrity gap without changing preservation semantics or introducing another command.

## Work

- Added a fixed 1 MiB ceiling for preservation-completeness inputs used by receipt preview/write, verification, and discovery.
- Added a dedicated bounded completeness loader so oversize failures identify the authoritative preservation input clearly.
- Exposed `source_completeness_byte_limit` in discovery output for reviewability.
- Added deterministic tests covering oversized preview input, oversized discovery source, and source growth before receipt verification.
- Updated the existing receipt resource-bound documentation.

## Safety

The change is local and read-only until the existing explicitly confirmed receipt-write boundary. It adds no network access, external command execution, workflow action, Git mutation, push authority, overwrite path, or preservation gate. Receipt presence remains informational only. Existing path/symlink containment, no-clobber receipt persistence, exact byte/SHA-256 binding, receipt-candidate limits, and preservation-completeness requirements remain fail-closed.

## Validation

Product/test head `639a4a6fc08dc0571befe20dc27a17f81a885f99` passed GitHub Actions run `33137985466`: Python 3.10, 3.11, and 3.12 each passed checkout/install, source compilation, installed CLI smoke tests, roadmap validation, and pytest. The documentation/status heads are checked separately before final completion.

## Visuals

No visual update was warranted because this tightens a resource boundary inside the existing preservation-receipt stage without changing workflow topology.

## Limitations and next action

The 1 MiB completeness ceiling is a fixed local safety contract, not adaptive streaming validation. Unattributed malformed/oversized receipt-directory noise still requires operator cleanup. Inspect final-head CI; any failure takes priority. If green, continue only with another concrete end-to-end integrity defect or meaningful evidence-handoff reduction.
