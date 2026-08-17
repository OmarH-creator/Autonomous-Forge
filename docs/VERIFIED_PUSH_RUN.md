# Verified push run

`forge verified-push-run` carries committed verified change evidence through the existing verified push handoff and post-push verification contracts.

It accepts either the historical standalone `verified-change-run` artifact or the newer `verified-change-apply-run` wrapper. Wrapper mode lets callers preserve the embedded guarded patch → live diff → validation → commit provenance without splitting the nested change-run back into another JSON file.

```bash
forge verified-push-run \
  --change-apply-run .ai/evidence/verified-change-apply-run.json \
  --commit-trust .ai/evidence/commit-trust.json \
  --status-review .ai/evidence/commit-status.json \
  --branch-protection .ai/evidence/branch-protection.json \
  --branch main \
  --remote origin \
  --confirm-push \
  --fetch-after-push \
  --require-post-push-verified \
  --format json
```

For backward compatibility, replace `--change-apply-run` with `--change-run` when using a standalone verified-change artifact. The two inputs are mutually exclusive.

Without `--confirm-push`, the command can reach `ready_for_push` but does not invoke an authorized push. After an explicitly confirmed successful push, it runs the existing post-push remote verification; `--fetch-after-push` explicitly allows the verifier to refresh only the requested remote branch before checking reachability.

## Wrapper verification

Before using embedded commit evidence, wrapper mode requires the change-apply run to prove:

- committed workflow status;
- explicit patch-apply, validation, and commit confirmations;
- retained embedded patch evidence with the expected guarded-patch title;
- successful guarded patch application and live-diff verification;
- closed push/remote-change authority;
- a nested verified-change-run whose workflow status and commit confirmation agree with the wrapper;
- an exact canonical SHA-256 match between the wrapper's embedded patch evidence and the `patch_apply_sha256` retained by verified commit readiness.

The digest check prevents a valid committed nested change-run from being paired with a different or tampered wrapper patch report. The verified-push-run result retains the accepted `change_apply_run` wrapper so downstream durable evidence can preserve the full provenance chain rather than reconstructing it from separate files.

## Safety boundary

Push authority remains independent from patch, validation, and commit confirmations. Forge reuses the existing commit-trust, status-review, branch-protection, fast-forward-only push, and post-push verification contracts. It never force-pushes, pushes tags, changes remotes or branch protections, or treats earlier confirmations as push authority.

The supplied trust, status, and branch-protection JSON remain caller-provided evidence. This command composes and cross-checks those existing contracts; it does not independently query GitHub or prove signer identity.
