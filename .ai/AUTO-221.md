# AUTO-221 — Bound preservation-receipt directory enumeration

## Objective

Close the remaining resource-exhaustion gap in preservation-receipt discovery. AUTO-219/220 bounded admitted JSON receipts and bytes, but `Path.glob("*.json")` still materialized and sorted the complete matching directory set before enforcing the candidate limit.

## Repository assessment

- Baseline `main` head at cycle start: `17aa57febcf2c8f3d13e0d651f43a5718fddf96a` (AUTO-220), with Actions run `33138118748` green.
- Inspected README/docs/examples, preservation-receipt source/tests, `.forge/policy.md`, `.ai` roadmap/state/changelog/decisions, recent commits and Actions, open issues, all eight visible branches, and recent PR history.
- Seven non-main branches remain historical/diverged; recent PRs are merged, closed, obsolete, or unrelated. No branch or PR warranted integration.
- Open issues #1, #6, and #9 are broader project/discussion requests and do not outrank the concrete end-to-end resource-bound defect.

## Change

- Replace unbounded `glob("*.json")` materialization with incremental `os.scandir()` enumeration.
- Fail closed immediately on the first JSON candidate beyond the configured receipt limit.
- Add a hard bound of 1,000 direct directory entries, including non-JSON entries, so unrelated cleanup noise cannot force an unbounded scan before the receipt limit is reached.
- Sort only the admitted candidate list.
- Expose observed directory-entry count and the hard entry limit in discovery evidence.

## Safety

Receipt discovery remains read-only and informational only. No preservation gate, Git authority, workflow/network capability, push authority, overwrite path, or external-command execution was added. Existing completeness, candidate-count, candidate-byte, path/symlink, receipt-attribution, and SHA-256 checks remain fail-closed.

## Validation

The first focused regression head exposed an assertion-format mismatch in the new test (`1,000` vs runtime `1000`), not a product defect. The assertion was corrected. Final Python 3.10/3.11/3.12 matrix status is recorded in `AUTONOMOUS_STATE.md` and README after the corrected head completes.

## Visuals

None. This tightens resource bounds inside the existing receipt-discovery stage and does not change workflow topology.

## Next

If the corrected matrix is green, continue only with another concrete end-to-end integrity defect or meaningful evidence-handoff reduction. Any CI failure takes priority.
