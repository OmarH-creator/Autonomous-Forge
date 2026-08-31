# AUTO-243 — Bound executor-handoff persistence input

## Objective

Close a concrete resource-safety gap in the existing executor-to-validation-history write bridge. `executor_handoff_persistence._load_executor_output()` previously used `Path.read_text()` after repository/path validation, so an unexpectedly large or concurrently expanded repository-local JSON file could be materialized without a byte bound before schema checks or the guarded validation-result writer were reached.

## Repository inspection

Started from AUTO-242 final `main` head `95b80d0baca52f48b49b5a02b69196cc87e59650`, whose Actions run `33429126840` was green. Inspected README, docs/examples, source/tests/config/CI, `.forge/policy.md`, `.ai/AUTONOMOUS_PLAN.md`, `.ai/AUTONOMOUS_STATE.md`, `.ai/AUTONOMOUS_CHANGELOG.md`, `.ai/DECISIONS.md`, recent commits and Actions, all eight visible branches, open issues, and PR history. The policy-aware `forge plan` milestone and the later live-diff/guarded-apply/validation/commit/push/evidence chain are already shipped, so duplicating the requested planning command would violate the feature-delivery rule.

The seven non-`main` branches remain historical/diverged. No open PR requires integration. Open issues #1, #6, and #9 are broader product/discussion requests rather than blockers for this repair. Work stayed directly on `main`; no branch, PR, merge, force-push, workflow edit, remote change, or protection change was used.

## Change

- Added `_MAX_EXECUTOR_OUTPUT_BYTES = 1_000_000` to the existing executor-handoff persistence module.
- Replaced the unbounded text read with a shared binary bounded reader that reads at most 1,000,001 bytes and rejects overflow before UTF-8 decoding or JSON parsing.
- Added an explicit invalid-UTF-8 failure instead of allowing a raw decode exception to escape.
- Kept repository confinement, symlink/directory checks, `.json` enforcement, handoff consistency, explicit `--confirm-write`, and downstream validation-result persistence semantics unchanged.
- Updated `docs/EXECUTOR_HANDOFF_PERSISTENCE.md` and README to describe the bounded-input contract and make clear that the size limit is resource protection, not a trust signal.

## Validation

Added `tests/test_auto243_executor_handoff_input_bounds.py` with deterministic regression coverage for:

1. a payload larger than 1,000,000 bytes being rejected before JSON parsing; and
2. invalid UTF-8 being rejected through the same bounded read path.

The product/test head `d91c44b61ca0fce6e7f3e3c86ed9a57426d7509a` passed GitHub Actions run `33449547892`, covering package installation, source compilation, installed CLI smoke tests, roadmap validation, and pytest across Python 3.10, 3.11, and 3.12. A final `main` Actions run is required after README/state/run-record completion before AUTO-243 is reported complete.

A checkout-capable local test environment was not available in this run, so GitHub Actions is the authoritative full-suite validation rather than fabricated local results.

## Safety and policy

All changed paths are permitted by `.forge/policy.md`: `src/**`, `tests/**`, `docs/**`, `README.md`, and `.ai/**`. No `.github/workflows/**`, secret/token/key/PEM path, generated artifact, or unrelated file was changed.

The new bound reduces memory exposure only. It does not authenticate executor output, infer validation success, expand write authority, run commands, create commits, push, or weaken any existing validation-history safety gate.

## Visuals

No visual update was warranted. The repository's existing workflow diagram remains accurate because this change tightens the input boundary on an existing executor-handoff persistence stage without changing workflow topology.

## Limitations

The size bound does not authenticate the JSON source and does not eliminate all filesystem time-of-check/time-of-use races. The durable history write still relies on the existing validation-result writer's downstream ownership and durability protections. Forge remains explicitly human-in-the-loop.

## Next objective

Return to the durability-integrity milestone and inspect/harden the shared maintenance-evidence bundle/history-link no-clobber publication helper if its post-hard-link parent-directory `fsync` ambiguity remains reproducible. Any fresh CI failure takes priority.
