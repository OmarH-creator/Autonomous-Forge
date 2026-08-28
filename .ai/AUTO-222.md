# AUTO-222 — Bound run-history validation attachment discovery

## Objective

Close a concrete resource-exhaustion gap in `forge run-history-read`: immutable validation-attachment discovery previously materialized and sorted every matching `*.json` path before enforcing the 100-file limit, and each candidate was read without a byte ceiling.

## Inspection

Inspected README/docs/examples, relevant source/tests/config/CI, `.forge/policy.md`, `.ai/AUTONOMOUS_PLAN.md`, `.ai/AUTONOMOUS_STATE.md`, `.ai/AUTONOMOUS_CHANGELOG.md`, `.ai/DECISIONS.md`, recent commits, open issues, all eight visible branches, and recent PR history. The seven non-main branches remain historical/diverged. Recent PRs are merged, closed, obsolete, or unrelated; nothing warranted integration.

## Work

- Replaced eager `glob("*.json")` materialization with incremental `os.scandir()` enumeration.
- Fail closed on the 101st direct JSON candidate.
- Fail closed on the 1,001st total direct directory entry, including non-JSON noise.
- Read each admitted attachment candidate through a 1 MiB ceiling before parsing and verification selection.
- Sort only the admitted candidate set for deterministic output.
- Added deterministic regression coverage and dedicated documentation.

## Safety

The reader remains local and read-only. The change does not execute validation, persist evidence, mutate Git, call networks, grant approvals, or promote externally supplied validation observations to Forge-executed proof. Existing path/symlink containment and cryptographic attachment verification remain intact.

## Validation

Final corrected product/docs head `91d61c21dbae5204611c0ca5c30ee468e3443980` passed GitHub Actions run `33166236674`. Python 3.10, 3.11, and 3.12 each passed checkout/install, source compilation, installed CLI smoke tests, roadmap validation, and pytest.

## Branch/PR disposition

Main-only. No branch or pull request was created or merged; no force-push or protection change was used.

## Next action

Continue only with another concrete end-to-end integrity defect or meaningful evidence-handoff reduction. Any fresh CI failure takes priority.
