# Maintenance review handoff

`forge maintenance-review-handoff` builds one read-only reviewer handoff from a persisted `.ai/run-history/` maintenance bundle link.

The command is meant for the end of a completed maintenance cycle, after a bundle has been written and linked into run history. It combines:

- history-link quality gates;
- linked bundle SHA-256 verification;
- linked bundle replay status and compact replay policy counts;
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

## Safety boundary

The command reads one repository-local history link plus its linked bundle evidence. It recomputes the linked bundle hash and reuses maintenance replay summaries, but it does not rerun validation, inspect live remotes, change files, stage, commit, push, poll workflows, or verify signer identity.

## Exit codes

- `0`: the handoff was generated.
- `2`: input was invalid, unsafe, unreadable, or `--require-ready` was supplied and required handoff gates failed.
