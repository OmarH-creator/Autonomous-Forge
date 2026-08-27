# AUTO-219 — Bound preservation receipt discovery resources

## Inspection and rationale

The run began with a broad inspection of README/docs/examples, preservation receipt source/tests, `.forge/policy.md`, `.ai` roadmap/state/changelog/decisions, recent commits, open issues, all eight visible branches, and recent pull-request history. The seven non-`main` branches remain historical/diverged, and recent PRs are merged, closed, obsolete, or unrelated; no branch or PR warranted integration.

AUTO-218 fixed attribution of malformed receipt-directory noise, but the discovery implementation still described itself as bounded while allowing direct Python callers to raise `max_receipts` without a hard ceiling. Candidate receipt files were also read with `read_bytes()` and therefore had no per-file byte ceiling. A local receipt directory could consequently turn a nominally bounded read-only review into unbounded file-count or memory work.

## Change

- Added a hard discovery ceiling of 100 direct JSON candidates. Callers may request a smaller limit but cannot raise the safety cap.
- Added a 1 MiB (1,048,576-byte) ceiling for every candidate receipt read during discovery.
- Matching receipts are re-verified through the same byte ceiling so a candidate cannot pass the first bounded read and then grow into an unbounded second read before verification.
- Discovery output now exposes `scan_hard_limit` and `candidate_byte_limit` for reviewability.
- Oversized receipt files are surfaced as unattributed invalid evidence unless a safe source binding can already be established; receipt evidence remains informational only.

## Validation

GitHub Actions run `33125205937` passed on Python 3.10, 3.11, and 3.12. Each matrix job passed checkout/install, source compilation, installed CLI smoke tests, roadmap validation, and pytest.

Focused deterministic coverage includes refusal of `max_receipts=101` and bounded handling of an oversized receipt candidate without downgrading preservation completeness.

## Safety and policy

The change is confined to policy-allowed `src/**`, `tests/**`, `docs/**`, README, and `.ai/**` areas. No workflow, secret, credential, network, external-command, Git mutation, push, force-push, remote, branch-protection, or telemetry capability was added. Receipt discovery remains read-only and `informational_only` with no preservation-gate effect.

## Limitations

The selected preservation-completeness artifact remains a single authoritative input and is not subject to the receipt-candidate byte ceiling; AUTO-219 specifically bounds the potentially many directory candidates. Oversized or otherwise unreadable receipt files whose source binding cannot be safely established remain unattributed cleanup items.

## Next action

Continue only with another concrete end-to-end preservation/provenance integrity defect or a meaningful evidence-handoff reduction. Any fresh CI failure takes priority.
