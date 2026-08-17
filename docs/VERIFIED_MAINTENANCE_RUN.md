# Verified maintenance run

`forge verified-maintenance-run` carries a successfully post-push-verified orchestration result into the existing canonical maintenance evidence and run-history contracts.

It is the durable-evidence continuation of `forge verified-push-run`: callers no longer need to export the embedded verified push handoff and post-push verification into two extra JSON files before preserving the run.

## Example

```bash
forge verified-maintenance-run \
  --patch-apply .ai/evidence/patch-apply.json \
  --post-apply-validation .ai/evidence/post-apply-validation.json \
  --commit-verify .ai/evidence/commit-verify.json \
  --verified-push-run .ai/evidence/verified-push-run.json \
  --bundle-id AUTO-155 \
  --output .ai/evidence/AUTO-155-bundle.json \
  --confirm-bundle-write \
  --history-link .ai/run-history/AUTO-155.json \
  --confirm-history-link \
  --require-complete \
  --require-written \
  --require-history-linked \
  --format json
```

## Safety boundary

The command accepts only bounded repository-local UTF-8 JSON evidence. The verified push run must already report `post_push_verified`, prove an independently confirmed push, contain no blockers, and retain both the verified push handoff and post-push verification.

Bundle persistence and history-link persistence are deliberately separate authority gates:

- `--confirm-bundle-write` authorizes only the canonical bundle write.
- `--confirm-history-link` authorizes only the `.ai/run-history/` link after the bundle is written.

The command performs no patch application, validation execution, staging, commit creation, push, fetch, workflow polling, remote mutation, force-push, tag push, or branch-protection change. It reuses the existing durable-bundle and run-history writers.

The verified push-run file is fingerprinted once and truthfully referenced as the source for both embedded push and post-push stages. Downstream bundle verification can therefore detect later byte drift without requiring duplicate extracted evidence files.

## Limitations

This preserves the evidence Forge already verified; it does not independently acquire fresh GitHub commit-trust, workflow-status, branch-protection, or signer-identity proof. Hashes detect byte drift but are not signatures.
