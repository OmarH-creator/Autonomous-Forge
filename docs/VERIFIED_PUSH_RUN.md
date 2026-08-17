# Verified push run

`forge verified-push-run` continues a completed `forge verified-change-run` artifact through the existing verified push handoff and post-push verification contracts.

It deliberately does **not** collapse push authority into the earlier validation or commit confirmations. A committed verified-change artifact may be reviewed first with no push authority, then pushed only when `--confirm-push` is supplied.

```bash
forge verified-push-run \
  --change-run .ai/evidence/verified-change-run.json \
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

Without `--confirm-push`, the command can reach `ready_for_push` but does not invoke an authorized push. After an explicitly confirmed successful push, it runs the existing post-push remote verification; `--fetch-after-push` explicitly allows the verifier to refresh only the requested remote branch before checking reachability.

## Safety boundary

The command accepts only a `verified-change-run` artifact that finished in `committed` state with ready commit evidence and an immediately verified created commit. It then reuses the existing commit-trust, status-review, branch-protection, fast-forward-only push, and post-push verification contracts. It never force-pushes, pushes tags, changes remotes or branch protections, or treats earlier validation/commit confirmations as push authority.

The supplied trust, status, and branch-protection JSON remain caller-provided evidence. This command composes and cross-checks those existing contracts; it does not independently query GitHub or prove signer identity.
