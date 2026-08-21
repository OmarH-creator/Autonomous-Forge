# Maintenance review comparison

`forge maintenance-review-compare` compares multiple completed maintenance review handoffs from `.ai/run-history/` links.

It is intended for reviewers who need to compare completed maintenance runs without opening each raw bundle JSON. For every supplied link, the command builds the same read-only handoff produced by `forge maintenance-review-handoff`, then summarizes:

- ready and blocked handoff counts;
- failed handoff gate counts;
- failed linked replay-policy gate counts;
- linked bundle hash verification state;
- replay status;
- reviewed-path and validation-step counts;
- retained validation-context counts;
- ranked ready preservation candidates;
- the selected preservation candidate when at least one handoff is ready;
- optional immutable preservation-receipt review for candidates whose complete preservation artifacts are supplied;
- blocker summaries and next preservation guidance.

## Usage

```bash
forge maintenance-review-compare \
  --link .ai/run-history/AUTO-120-link.json \
  --link .ai/run-history/AUTO-121-link.json
```

To surface preservation receipts without reopening the lower-level receipt JSON files, add one or more complete preservation-completeness artifacts:

```bash
forge maintenance-review-compare \
  --link .ai/run-history/AUTO-120-link.json \
  --link .ai/run-history/AUTO-121-link.json \
  --completeness .ai/preservation/AUTO-120-completeness.json \
  --completeness .ai/preservation/AUTO-121-completeness.json
```

Each completeness artifact is independently required to be complete, then the command reuses the existing bounded `maintenance-preservation-receipt` discovery/verifier. Receipt reviews are matched to handoffs by commit SHA, remote, and branch. They are exposed in `preservation_receipt_reviews`, each handoff, and each preservation candidate.

Receipt information is **informational only**. Verified receipt presence, receipt absence, or an invalid/tampered matching receipt never changes `comparison_status`, `comparison_ready`, or the deterministic preservation score/rank. An invalid matching receipt is surfaced as `attention_required` so a reviewer can investigate it without rewriting preservation history.

Use `--require-all-ready` when the comparison should fail closed unless every linked handoff is ready:

```bash
forge maintenance-review-compare \
  --link .ai/run-history/AUTO-120-link.json \
  --link .ai/run-history/AUTO-121-link.json \
  --require-all-ready
```

Use JSON output for local dashboards or follow-on review tooling:

```bash
forge maintenance-review-compare \
  --link .ai/run-history/AUTO-120-link.json \
  --completeness .ai/preservation/AUTO-120-completeness.json \
  --format json
```

The JSON payload includes `preservation_candidates` and `selected_preservation_candidate`. Candidate ranking is deterministic and favors ready handoffs with verified linked-bundle replay, zero failed handoff or replay-policy gates, fewer blockers, more reviewed paths, more validation steps, and richer retained validation context. Blocked handoffs still remain visible in `handoffs` and `comparison_blockers`; they are not selected for preservation. Receipt review is deliberately absent from the ranking score.

The compatibility script is also available:

```bash
forge-maintenance-review-compare --help
```

## Safety boundary

The command reads repository-local history links and linked bundle evidence, recomputes bundle hashes through the underlying handoff workflow, and summarizes persisted replay evidence. Optional `--completeness` inputs reuse the existing bounded preservation-receipt discovery contract. Receipt review does not grant preservation readiness, change candidate rank, write receipts, or modify evidence. The command does not rerun validation, inspect live remotes, change files, stage, commit, push, poll workflows, write archive manifests, or verify signer identity.

## Exit codes

- `0`: the comparison was generated.
- `2`: an input was invalid, unsafe, unreadable, or `--require-all-ready` was supplied and one or more handoffs were blocked.