# Maintenance replay policy summary

`forge maintenance-replay-policy-summary` reads a persisted maintenance evidence bundle through the existing replay-summary verifier and reports a compact set of replay policy gates.

The command is local-first and read-only. It does not apply patches, run validation commands, stage files, create commits, push, change remotes, change branch protections, rerun workflows, poll remote status, or read environment variables.

The command is available through both installed entry points:

- primary surface: `forge maintenance-replay-policy-summary`
- compatibility script: `forge-maintenance-replay-policy-summary`

Both routes are covered by installed CLI smoke checks so releases do not ship a compatibility-only command without the primary `forge` route.

## Usage

```bash
forge maintenance-replay-policy-summary \
  --bundle .ai/bundles/AUTO-120.json \
  --root .
```

Use JSON output when another tool needs deterministic gate data:

```bash
forge maintenance-replay-policy-summary \
  --bundle .ai/bundles/AUTO-120.json \
  --root . \
  --format json
```

The compatibility script accepts the same arguments:

```bash
forge-maintenance-replay-policy-summary \
  --bundle .ai/bundles/AUTO-120.json \
  --root .
```

## Gates

The summary reports these gates in stable order:

1. `bundle_complete` — the bundle is complete and replay summary is replayable.
2. `source_reports_verified` — all source report hashes and byte counts still match.
3. `evidence_chain_complete` — all expected stages report expected statuses.
4. `reviewed_paths_present` — reviewed paths are present.
5. `validation_steps_present` — validation steps are present.
6. `validation_context_consistent` — retained validation context matches replay-critical evidence, or is advisory when missing from older bundles.

Overall `policy_status` is `passed` when all gates pass, `blocked` when any gate fails, and `advisory` when all required gates pass but optional validation context was not provided.
