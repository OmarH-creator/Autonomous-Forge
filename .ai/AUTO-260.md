# AUTO-260 — Bound change-readiness evidence ingestion

## Repository assessment

Started from AUTO-258 head `33dfb0b8b1101133aad5c5b54e5ea82cd8212046` after confirming the prior run had shipped and was green. Inspected README/docs/examples, source/tests/config/CI inventory, `.forge/policy.md`, autonomous plan/state/changelog/decisions, recent commits and Actions, all eight visible branches, open issues, TODO-oriented source search, and PR history.

Seven non-main branches remain historical/diverged. There are no open PRs requiring integration. Existing issues #1, #6, #9, and #15 remain open; issue #15 is a valid maintenance-history-link defect but could not be safely implemented through a whole-file replacement of the large bundle module from this runtime.

## Objective

Ship the next safe, concrete bounded-input repair in an existing workflow: `forge change-readiness` still used a pre-read `stat().st_size` check followed by `read_text()` for supplied review JSON files.

## Change

`read_change_readiness(...)` now reads each supplied `.json` review file through a single bounded binary snapshot. Forge reads at most 1,000,001 bytes for the 1,000,000-byte acceptance limit, rejects over-limit files at the actual read boundary, and decodes/parses JSON from the admitted bytes.

Existing repository confinement, symlink rejection, regular-file checks, `.json` enforcement, and read-only change-readiness semantics remain unchanged.

## Validation

Added deterministic regression coverage for:

- exact 1,000,001-byte sentinel read size on both supplied review files;
- oversized review-file refusal at the read boundary;
- invalid UTF-8 refusal before JSON parsing.

The strongest available validation is the repository GitHub Actions matrix on the exact final pushed `main` SHA.

## Diff and safety review

Changed paths are limited to policy-allowed areas: `src/**`, `tests/**`, `docs/**`, and `.ai/**`. No workflow, secret, generated, branch, remote, protection, or unrelated file was intentionally changed. README status was not rewritten because the available writer requires whole-file replacement and the README is large enough that reconstructing it would create unnecessary truncation risk.

## Limitations

A bounded snapshot guarantees that Forge consumes one internally consistent byte sequence for each input. It does not make the input files immutable or authenticate their author.

## Next action

Continue to issue #15 once a patch-capable checkout path is available, or inspect the next small execution/history/evidence reader with a confirmed split-read or pre-check/unbounded-read defect. Any fresh CI failure takes priority.
