# Verified Full Maintenance Run

`forge verified-full-maintenance-run` composes the existing guarded maintenance stages into one command without collapsing their authority boundaries.

It can carry one reviewed replacement through:

1. a fresh in-memory patch preview generated immediately before apply, or a supplied legacy preview file;
2. confirmed patch application and mandatory target-scoped live-diff verification;
3. confirmed execution of every retained validation step;
4. separately confirmed verified local commit creation;
5. separately confirmed fast-forward-only guarded push;
6. post-push remote verification;
7. separately confirmed persistence of the verified push-run evidence;
8. separately confirmed durable maintenance-bundle persistence; and
9. separately confirmed `.ai/run-history/` linking.

The verified push result is persisted before durable-bundle construction because maintenance bundle verification later recomputes the source-report file hashes. This keeps the existing anti-drift contract intact instead of replacing it with unverifiable in-memory provenance.

## Fresh preview mode

The preferred invocation uses `--patch-readiness`. Forge reads the existing patch-application readiness JSON together with the current target and replacement, generates the same bounded unified-diff preview used by `forge patch-generation-preview`, and passes that preview directly into the existing guarded patch writer. The preview is generated immediately before the apply decision, reducing stale caller-managed evidence without adding another write.

Fresh preview generation is **not** apply authority. `--confirm-apply` is still required, and the same target/current/replacement reproduction checks, policy-aware target-scoped live-diff verification, and rollback-on-verification-failure behavior still apply.

For compatibility, `--preview` still accepts an existing repository-local patch-generation-preview JSON file. `--preview` and `--patch-readiness` are mutually exclusive.

## Example

```bash
forge verified-full-maintenance-run \
  --root . \
  --patch-readiness .ai/evidence/patch-application-readiness.json \
  --change-readiness .ai/evidence/change-readiness.json \
  --status-before-commit .ai/evidence/status-before-commit.json \
  --path README.md \
  --replacement .ai/evidence/README.replacement.md \
  --summary "auto: [AUTO-161] apply reviewed maintenance change" \
  --commit-trust .ai/evidence/commit-trust.json \
  --status-after-commit .ai/evidence/status-after-commit.json \
  --branch-protection .ai/evidence/branch-protection.json \
  --branch main \
  --remote origin \
  --push-evidence-output .ai/evidence/AUTO-161-verified-push-run.json \
  --bundle-id AUTO-161 \
  --bundle-output .ai/evidence/AUTO-161-bundle.json \
  --history-link .ai/run-history/AUTO-161.json \
  --confirm-apply \
  --confirm-validation \
  --confirm-commit-create \
  --confirm-push \
  --fetch-after-push \
  --confirm-push-evidence-write \
  --confirm-bundle-write \
  --confirm-history-link \
  --require-history-linked \
  --format json
```

Omit a confirmation to stop before that authority boundary. For example, a run may reach a verified local commit without permission to push, or reach `post_push_verified_unpersisted` without permission to write the push evidence artifact.

The result records `patch_preview_mode` as `generated-in-run` or `supplied-file` together with `patch_preview_source`, so durable callers can see which preview path was used.

## Safety boundary

The command reuses the existing guarded implementations rather than adding alternate write or Git paths. Fresh preview generation is read-only; it does not grant apply authority. The command never treats one confirmation as permission for a later stage. It does not force-push, push tags, mutate remotes, change branch protection, or rerun/poll workflows.

`--push-evidence-output` refuses an existing destination instead of silently overwriting evidence. The persisted push artifact remains the canonical source for the durable maintenance bundle so later `forge maintenance-bundle-verify` checks can recompute byte counts and SHA-256 hashes.

Commit-trust, workflow/status, and branch-protection inputs are still supplied repository-local JSON evidence. This command composes those existing contracts; it does not independently query GitHub or establish signer identity.