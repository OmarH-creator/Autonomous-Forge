# Maintenance review handoff

`forge maintenance-review-handoff` builds one read-only reviewer handoff from a persisted `.ai/run-history/` maintenance bundle link.

The command is meant for the end of a completed maintenance cycle, after a bundle has been written and linked into run history. It combines:

- history-link quality gates;
- linked bundle SHA-256 verification;
- linked bundle replay status and compact replay policy counts;
- run-history pointer versus linked-bundle consistency for reviewed paths, validation steps, and retained validation context;
- reviewed paths, validation steps, retained validation context, blockers, and preservation guidance.

## Usage

```bash
forge maintenance-review-handoff \
  --link .ai/run-history/AUTO-120-link.json \
  --require-ready
```

Use JSON output when another local tool needs stable machine-readable evidence:

```bash
forge maintenance-review-handoff \
  --link .ai/run-history/AUTO-120-link.json \
  --format json
```

The compatibility script is also available:

```bash
forge-maintenance-review-handoff --help
```

## Context consistency

A ready handoff now requires the small run-history pointer and the replayed linked bundle to agree on replay-critical review context:

- `reviewed_paths` must match;
- `validation_steps` must match;
- retained `validation_context.expected_file_changes`, `implementation_steps`, `validation_steps`, and `risk_register` must match the linked bundle replay summary.

This catches stale or manually edited history pointers that still reference a hash-valid bundle but no longer describe the same reviewed change.

## Compare multiple handoffs

`forge maintenance-review-compare` compares multiple run-history links by building the same read-only handoff for each link and summarizing the set.

```bash
forge maintenance-review-compare \
  --link .ai/run-history/AUTO-120-link.json \
  --link .ai/run-history/AUTO-121-link.json \
  --require-all-ready
```

The comparison reports ready/blocked counts, failed handoff gates, failed replay-policy gates, replay/hash status, blocker counts, reviewed-path counts, validation-step counts, context-consistency mismatches, and the next preservation action for the group. JSON output is available for local dashboards or further review tooling:

```bash
forge maintenance-review-compare \
  --link .ai/run-history/AUTO-120-link.json \
  --format json
```

The compatibility script is also available:

```bash
forge-maintenance-review-compare --help
```

## Safety boundary

Both commands read repository-local history links plus linked bundle evidence. They recompute linked bundle hashes and reuse maintenance replay summaries, but they do not rerun validation, inspect live remotes, change files, stage, commit, push, poll workflows, or verify signer identity.

## Exit codes

- `0`: the handoff or comparison was generated.
- `2`: input was invalid, unsafe, unreadable, or a strict readiness flag was supplied and required gates failed.
