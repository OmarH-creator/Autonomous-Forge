# Maintenance evidence bundle

`forge maintenance-evidence-bundle` links the completed local maintenance evidence chain into one durable report:

1. `forge patch-apply --format json`
2. `forge post-apply-validation --format json`
3. `forge commit-verify --format json`
4. `forge push-handoff --format json`
5. `forge post-push-verify --format json`

The command is intended for the end of a safe maintenance loop, after the patch has been applied, validation has passed, the created commit has been verified, the non-force push handoff has completed, and post-push verification has confirmed remote reachability.

## Example

```bash
forge maintenance-evidence-bundle \
  --root . \
  --patch-apply patch-apply.json \
  --post-apply-validation post-apply-validation.json \
  --commit-verify commit-verify.json \
  --push-handoff push-handoff.json \
  --post-push-verify post-push-verify.json \
  --bundle-id AUTO-099 \
  --require-complete \
  --format json > maintenance-evidence-bundle.json
```

To persist a durable bundle directly, provide an output path and explicit write confirmation:

```bash
forge maintenance-evidence-bundle \
  --root . \
  --patch-apply patch-apply.json \
  --post-apply-validation post-apply-validation.json \
  --commit-verify commit-verify.json \
  --push-handoff push-handoff.json \
  --post-push-verify post-push-verify.json \
  --bundle-id AUTO-099 \
  --output .ai/run-history/AUTO-099-bundle.json \
  --confirm-write \
  --require-written \
  --format json
```

## Safety boundary

The command reads only repository-local JSON reports under `--root`, validates safe reviewed path labels, and checks that the same commit and reviewed paths flow through commit verification, push handoff, and post-push verification. It writes one bounded JSON file only when `--output` and `--confirm-write` are supplied and the bundle is complete.

It does not apply patches, run validation commands, stage files, create commits, push, force-push, change remotes, change branch protections, rerun workflows, or read environment variables.

## Completion rules

A bundle is `complete` only when:

- patch-apply evidence shows an applied file change and has closed patch application authority;
- post-apply validation shows a passed validation result for the same target path;
- commit verification is verified and reports reviewed changed paths;
- push handoff is pushed, non-force, and references the verified commit;
- post-push verification is verified for the same commit and reviewed paths.

When any stage is missing, stale, unsafe, or inconsistent, the command reports `bundle_status: blocked` and lists blockers. Use `--require-complete` or `--require-written` when automation should fail closed.
