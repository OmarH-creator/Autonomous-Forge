# Validation Preview Contract

`forge validation-preview` is a read-only bridge between validation planning and any future validation execution behavior.

It consumes the same roadmap, policy, state, and root inputs used by `forge validate-plan`, then classifies documented validation steps into command-preview metadata.

## What it reports

- selected roadmap task
- validation execution status, always `not run`
- command allowance status, always `false`
- one command-candidate record per validation step
- candidate command text when a step is phrased as `Run ...`
- conservative eligibility: `eligible preview`, `blocked`, `unknown`, or `not recognized`
- reason for each classification
- blockers, risks, and the no-execution safety boundary

## Conservative command-preview rules

The preview allowlist is intentionally narrow. A candidate can only be marked `eligible preview` when it starts with a documented local Python validation prefix such as:

- `python -m pytest`
- `PYTHONPATH=src python -m pytest`

Candidates containing shell control, expansion, or redirection syntax are marked `blocked`.

All other command-like candidates are marked `unknown` until a future, explicitly approved validation runner defines a safe execution contract.

## Safety limits

`forge validation-preview` does not run commands, read environment variables, inspect git diffs, scan secrets, write files, approve policy exceptions, enforce policy decisions, call networks, generate patches, commit, or push.

Its output is advisory review metadata only.
