# Verified push run

`forge verified-push-run` carries committed verified change evidence through the existing verified push handoff and post-push verification contracts.

It accepts either the historical standalone `verified-change-run` artifact or the newer `verified-change-apply-run` wrapper. Wrapper mode lets callers preserve the embedded guarded patch → live diff → validation → commit provenance without splitting the nested change-run back into another JSON file.

The push stage can obtain workflow status in either of two ways:

- `--status-review <file>` consumes an already reviewed repository-local status artifact.
- `--live-status` explicitly invokes Forge's existing bounded GitHub workflow-status collector for the exact verified created commit immediately before push readiness is evaluated.

```bash
forge verified-push-run \
  --change-apply-run .ai/evidence/verified-change-apply-run.json \
  --commit-trust .ai/evidence/commit-trust.json \
  --live-status \
  --branch-protection .ai/evidence/branch-protection.json \
  --branch main \
  --remote origin \
  --confirm-push \
  --fetch-after-push \
  --require-post-push-verified \
  --format json
```

For backward compatibility, replace `--change-apply-run` with `--change-run` when using a standalone verified-change artifact. The two inputs are mutually exclusive. Likewise, `--status-review` and `--live-status` are mutually exclusive so supplied and freshly collected workflow evidence cannot be silently mixed.

Without `--confirm-push`, the command can reach `ready_for_push` but does not invoke an authorized push. After an explicitly confirmed successful push, it runs the existing post-push remote verification; `--fetch-after-push` explicitly allows the verifier to refresh only the requested remote branch before checking reachability.

## Live workflow-status binding

`--live-status` reuses the already shipped `commit-status-review --from-github` collection boundary. It runs only after the change artifact proves a verified created commit, then queries workflow runs for that exact commit SHA and converts the result through the normal commit-status review contract.

Forge validates the returned workflow-run metadata before it becomes status-review evidence. Every collected workflow run must carry a non-empty `headSha` (normalized internally as `head_sha`) that exactly equals the verified created commit. A missing or mismatched per-run SHA fails closed before the status-review builder is invoked. The resulting review must also retain the exact verified commit SHA, providing a second independent binding check.

Live status also has a completeness gate. Forge reviews at most 20 workflow runs but asks `gh run list` for one additional sentinel result. If the sentinel is returned, the visible 20-run window may have omitted another failed, pending, or unknown run, so collection stops with `completeness is unknown` before push readiness. A successful collected payload therefore proves that the bounded workflow-run set was not truncated at the configured review limit.

Forge refuses to start the live query when the change artifact is malformed, uncommitted, or unverified. Each live `git`/`gh` subprocess has a 15-second timeout. The collector is bounded and read-only with respect to GitHub: it lists workflow runs and never reruns workflows, mutates checks, applies patches, commits, pushes, or changes repository settings.

This mode removes one caller-managed JSON handoff while keeping network access explicit at invocation time. Users who do not want a live GitHub query can continue supplying `--status-review` exactly as before.

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

Commit-trust and branch-protection evidence remain caller-provided. Workflow status can be caller-provided or explicitly collected live for the verified commit through the existing bounded collector. Live status collection does not rerun workflows and cannot itself authorize a push; `--confirm-push` remains mandatory for the side effect.