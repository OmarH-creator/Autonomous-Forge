# Verified Full Maintenance Run

`forge verified-full-maintenance-run` composes the existing guarded maintenance stages into one command without collapsing their authority boundaries.

It can carry one reviewed replacement through:

1. confirmed patch application and mandatory target-scoped live-diff verification;
2. confirmed execution of every retained validation step;
3. separately confirmed verified local commit creation;
4. separately confirmed fast-forward-only guarded push;
5. post-push remote verification;
6. separately confirmed persistence of the verified push-run evidence;
7. separately confirmed durable maintenance-bundle persistence; and
8. separately confirmed `.ai/run-history/` linking.

The verified push result is persisted before durable-bundle construction because maintenance bundle verification later recomputes the source-report file hashes. This keeps the existing anti-drift contract intact instead of replacing it with unverifiable in-memory provenance.

## Example

```bash
forge verified-full-maintenance-run \
  --root . \
  --preview .ai/evidence/patch-preview.json \
  --change-readiness .ai/evidence/change-readiness.json \
  --status-before-commit .ai/evidence/status-before-commit.json \
  --path README.md \
  --replacement .ai/evidence/README.replacement.md \
  --summary "auto: [AUTO-159] apply reviewed maintenance change" \
  --commit-trust .ai/evidence/commit-trust.json \
  --status-after-commit .ai/evidence/status-after-commit.json \
  --branch-protection .ai/evidence/branch-protection.json \
  --branch main \
  --remote origin \
  --push-evidence-output .ai/evidence/AUTO-159-verified-push-run.json \
  --bundle-id AUTO-159 \
  --bundle-output .ai/evidence/AUTO-159-bundle.json \
  --history-link .ai/run-history/AUTO-159.json \
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

## Safety boundary

The command reuses the existing guarded implementations rather than adding alternate write or Git paths. It never treats one confirmation as permission for a later stage. It does not force-push, push tags, mutate remotes, change branch protection, or rerun/poll workflows.

`--push-evidence-output` refuses an existing destination instead of silently overwriting evidence. The persisted push artifact remains the canonical source for the durable maintenance bundle so later `forge maintenance-bundle-verify` checks can recompute byte counts and SHA-256 hashes.

Commit-trust, workflow/status, and branch-protection inputs are still supplied repository-local JSON evidence. This command composes those existing contracts; it does not independently query GitHub or establish signer identity.
