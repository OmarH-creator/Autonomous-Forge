# Verified change apply run

`forge verified-change-apply-run` removes the manual patch-apply JSON handoff between a reviewed replacement and `forge verified-change-run`.

It composes existing safety contracts in this order:

1. guarded replacement application;
2. mandatory target-scoped policy-aware live Git diff verification;
3. every validation step retained by the patch preview;
4. verified commit readiness;
5. optional local commit creation and immediate commit verification.

Patch application, validation execution, and commit creation remain separate authority gates. The command never pushes or changes remotes.

## Example

```bash
forge verified-change-apply-run \
  --preview .ai/evidence/patch-generation-preview.json \
  --change-readiness .ai/evidence/change-readiness.json \
  --status-review .ai/evidence/commit-status-review.json \
  --target src/autonomous_forge/example.py \
  --replacement .ai/evidence/example.replacement.py \
  --summary "auto: [AUTO-156] update example" \
  --confirm-apply \
  --confirm-validation \
  --confirm-commit-create \
  --require-committed \
  --format json
```

Omit `--confirm-apply` to keep the target unchanged. `--confirm-validation` cannot grant patch-write authority, and `--confirm-commit-create` cannot grant either patch-write or validation authority.

## Evidence continuity

The guarded patch report is embedded directly in the orchestration result. Each validation observation includes a deterministic SHA-256 of the canonical structured patch report. Verified commit readiness checks that hash before accepting an in-memory validation result, so callers no longer need to write and then reread an intermediate patch-apply JSON file merely to preserve evidence identity.

Existing file-based `verified-validation-run`, `verified-commit-readiness`, and `verified-change-run` workflows remain supported. Older validation evidence without the new hash continues to use the existing repository-local patch-file identity check.

## Safety boundary

- patch application still uses the existing preview/readiness/current-target/replacement consistency checks;
- live-diff verification is mandatory in this orchestration and rolls the target back if that verification fails;
- validation still uses the exact-command executor contract with `shell=False` and a bounded timeout;
- commit creation still stages only reviewed paths and verifies the resulting commit;
- hash drift between embedded patch evidence and validation observations fails closed;
- no push, force-push, remote mutation, workflow polling, branch-protection mutation, or hidden combined confirmation is added.

The current limitation is that the downstream durable-maintenance path still accepts the patch report as a separate input. A later integration slice can consume the embedded patch report from this orchestration artifact without weakening the persistence gates.
