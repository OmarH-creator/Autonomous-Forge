# Verified maintenance run

`forge verified-maintenance-run` carries a successfully post-push-verified orchestration result into the existing canonical maintenance evidence and run-history contracts.

It is the durable-evidence continuation of `forge verified-push-run`. When that push run retained a committed `verified-change-apply-run`, Forge now derives the canonical patch, validation, and commit stages directly from the embedded provenance. Callers no longer need to split those stages back into three duplicate JSON files before preservation.

## Canonical example

```bash
forge verified-maintenance-run \
  --verified-push-run .ai/evidence/verified-push-run.json \
  --bundle-id AUTO-158 \
  --output .ai/evidence/AUTO-158-bundle.json \
  --confirm-bundle-write \
  --history-link .ai/run-history/AUTO-158.json \
  --confirm-history-link \
  --require-complete \
  --require-written \
  --require-history-linked \
  --format json
```

The verified push-run must retain `change_apply_run`, which in turn must preserve the guarded patch, every successful verified validation observation, ready commit evidence, and a successfully created and immediately verified local commit. Forge rechecks the canonical guarded-patch SHA-256 retained by commit readiness and by every validation observation before using the embedded stages.

## Legacy stage-file compatibility

Older verified push-run artifacts may not retain `change_apply_run`. For those artifacts, the historical three stage files remain supported, but they must be supplied together:

```bash
forge verified-maintenance-run \
  --patch-apply .ai/evidence/patch-apply.json \
  --post-apply-validation .ai/evidence/post-apply-validation.json \
  --commit-verify .ai/evidence/commit-verify.json \
  --verified-push-run .ai/evidence/verified-push-run.json \
  --bundle-id AUTO-155 \
  --format json
```

Supplying only part of the legacy triplet fails closed rather than mixing embedded and external stage evidence.

## Safety boundary

The command accepts only bounded repository-local UTF-8 JSON evidence. The verified push run must already report `post_push_verified`, prove an independently confirmed push, contain no blockers, and retain both the verified push handoff and post-push verification.

In embedded mode Forge additionally requires:

- a committed `verified-change-apply-run` with explicit apply, validation, and commit confirmations;
- a guarded patch that is applied, live-diff verified, and has closed patch authority;
- every required validation step to have a matching completed successful verified validation observation for the same target;
- every validation observation to bind to the same canonical guarded-patch SHA-256 and retain the same validation context;
- ready commit evidence whose retained patch SHA-256 and successful validation-command set match those observations;
- verified commit-creation evidence with the same successful validation-command set and the guarded target among the inspected commit paths.

Bundle persistence and history-link persistence remain deliberately separate authority gates:

- `--confirm-bundle-write` authorizes only the canonical bundle write.
- `--confirm-history-link` authorizes only the `.ai/run-history/` link after the bundle is written.

The command performs no patch application, validation execution, staging, commit creation, push, fetch, workflow polling, remote mutation, force-push, tag push, or branch-protection change. It reuses the existing durable-bundle and run-history writers.

In canonical embedded mode, the verified push-run file is fingerprinted once and truthfully referenced as the source for all five canonical maintenance stages. Downstream bundle verification can therefore detect later byte drift without requiring duplicate extracted evidence files.

## Limitations

This preserves the evidence Forge already verified; it does not independently acquire fresh GitHub commit-trust, workflow-status, branch-protection, or signer-identity proof. Hashes detect byte drift but are not signatures. Legacy stage-file mode remains for backward compatibility and necessarily keeps the older caller-managed evidence split.