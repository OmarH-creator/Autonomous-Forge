# In-memory Change Readiness for Verified Full Maintenance

`forge verified-full-maintenance-run` can now derive the existing change-readiness contract in memory for generated-preview modes instead of requiring callers to persist a separate `change-readiness.json` handoff.

This applies when the patch preview is generated from either `--preflight` plus `--audit`, or `--patch-readiness`. Forge combines the generated unified diff with `.forge/policy.md` and the supplied `--status-before-commit` review, then reuses the existing policy-aware git-diff review and change-readiness builders. The derived readiness must review exactly the requested target and must be `ready` before the guarded writer can proceed.

## Preferred example

```bash
forge verified-full-maintenance-run \
  --root . \
  --preflight .ai/evidence/patch-application-preflight.json \
  --audit .ai/evidence/patch-application-audit.json \
  --status-before-commit .ai/evidence/status-before-commit.json \
  --path README.md \
  --replacement .ai/evidence/README.replacement.md \
  --summary "auto: [AUTO-163] apply reviewed maintenance change" \
  --commit-trust .ai/evidence/commit-trust.json \
  --status-after-commit .ai/evidence/status-after-commit.json \
  --branch-protection .ai/evidence/branch-protection.json \
  --push-evidence-output .ai/evidence/AUTO-163-verified-push-run.json \
  --format json
```

The example intentionally omits side-effect confirmations. Add `--confirm-apply`, `--confirm-validation`, `--confirm-commit-create`, `--confirm-push`, and the evidence-persistence confirmations only after reviewing the evidence for each separate authority boundary.

## Compatibility

`--change-readiness` remains available for callers that already persist the readiness artifact. Legacy supplied `--preview` mode still requires `--change-readiness`, because that mode intentionally consumes the historical pair of reviewed JSON artifacts rather than reconstructing one from a fresh generated preview.

## Safety boundary

In-memory readiness derivation is read-only and grants no patch authority. Prohibited or unknown paths, malformed/empty patch evidence, unclear or failed pre-commit status evidence, or a reviewed-path mismatch block before the target is written. Confirmed application still uses the existing target/current/replacement reproduction checks and mandatory target-scoped policy-aware live-diff verification with rollback on verification failure.

No new network access, external-service call, force-push, tag push, remote mutation, branch-protection mutation, or workflow mutation is introduced by this handoff reduction.
