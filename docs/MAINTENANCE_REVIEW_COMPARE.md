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
- blocker summaries and next preservation guidance.

## Usage

```bash
forge maintenance-review-compare \
  --link .ai/run-history/AUTO-120-link.json \
  --link .ai/run-history/AUTO-121-link.json
```

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
  --format json
```

The JSON payload includes `preservation_candidates` and `selected_preservation_candidate`. Candidate ranking is deterministic and favors ready handoffs with verified linked-bundle replay, zero failed handoff or replay-policy gates, fewer blockers, more reviewed paths, more validation steps, and richer retained validation context. Blocked handoffs still remain visible in `handoffs` and `comparison_blockers`; they are not selected for preservation.

The compatibility script is also available:

```bash
forge-maintenance-review-compare --help
```

## Safety boundary

The command reads repository-local history links and linked bundle evidence, recomputes bundle hashes through the underlying handoff workflow, and summarizes persisted replay evidence. It does not rerun validation, inspect live remotes, change files, stage, commit, push, poll workflows, write archive manifests, or verify signer identity.

## Exit codes

- `0`: the comparison was generated.
- `2`: an input was invalid, unsafe, unreadable, or `--require-all-ready` was supplied and one or more handoffs were blocked.
