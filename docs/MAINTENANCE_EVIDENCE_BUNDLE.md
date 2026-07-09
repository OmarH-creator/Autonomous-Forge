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
  --bundle-id AUTO-108 \
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
  --bundle-id AUTO-108 \
  --output .ai/run-history/AUTO-108-bundle.json \
  --confirm-write \
  --require-written \
  --format json
```

## Link a persisted bundle into run history

After the bundle has been written, the same command can write a small run-history pointer:

```bash
forge maintenance-evidence-bundle \
  --root . \
  --patch-apply patch-apply.json \
  --post-apply-validation post-apply-validation.json \
  --commit-verify commit-verify.json \
  --push-handoff push-handoff.json \
  --post-push-verify post-push-verify.json \
  --bundle-id AUTO-108 \
  --output .ai/run-history/AUTO-108-bundle.json \
  --confirm-write \
  --history-link .ai/run-history/AUTO-108-link.json \
  --confirm-history-link \
  --require-complete \
  --require-written \
  --require-history-linked \
  --format json
```

The link file uses schema `maintenance-bundle-history-link/v1` and records the bundle ID, persisted bundle path, bundle SHA-256, bundle byte count, commit SHA, remote branch, reviewed paths, validation steps, and source-report fingerprints. The link refuses to overwrite an existing file and must stay under `.ai/run-history/`.

## Verify a persisted bundle

`forge maintenance-bundle-verify` reads a persisted bundle and recomputes the byte count and SHA-256 digest for every repository-local source report listed in the bundle's `source_reports` array:

```bash
forge maintenance-bundle-verify \
  --root . \
  --bundle .ai/run-history/AUTO-108-bundle.json \
  --require-verified \
  --format json
```

The command reports `verification_status: verified` when all five source reports still match. If a source report was edited, swapped, regenerated, deleted, moved outside the repository root, or no longer has the expected byte count/hash, it reports blockers and exits non-zero when `--require-verified` is supplied.

## Replay a verified persisted bundle

`forge maintenance-replay-summary` first performs the same source-report verification as `forge maintenance-bundle-verify`, then summarizes whether the persisted bundle is still internally complete and replayable:

```bash
forge maintenance-replay-summary \
  --root . \
  --bundle .ai/run-history/AUTO-108-bundle.json \
  --require-replayable \
  --format json
```

A replayable bundle must still verify all source-report hashes, report `bundle_status: complete`, include the expected patch, validation, commit, push, and post-push stages, preserve at least one reviewed path and validation step, and keep the target path inside the reviewed-path set. The command does not rerun the evidence chain; it gives maintainers a compact replay decision from persisted evidence.

## Hash-linked source reports

Each bundle records a `source_reports` array with the stage name, repository-local input path, byte count, and SHA-256 digest for every source JSON report. This makes the durable bundle easier to audit later: if any source report is edited, replaced, or regenerated, maintainers can recompute the digest and detect that the preserved bundle no longer matches the report bytes used at bundle creation time.

The hashes are provenance fingerprints for stale-report detection. They do not prove author identity, validate commit signatures, rerun workflows, or replace human review.

## Safety boundary

The bundle builder reads only repository-local JSON reports under `--root`, validates safe reviewed path labels, checks that the same commit and reviewed paths flow through commit verification, push handoff, and post-push verification, and records bounded SHA-256 source-report fingerprints. It writes one bounded JSON file only when `--output` and `--confirm-write` are supplied and the bundle is complete.

The optional history link writes only one small repository-local JSON pointer under `.ai/run-history/` when `--history-link` and `--confirm-history-link` are supplied, the bundle has already been written, and the output does not already exist. It does not rewrite the bundle or run replay verification.

The verifier reads only one repository-local persisted bundle and the repository-local source reports named by that bundle. It never writes files and does not apply patches, run validation commands, stage files, create commits, push, force-push, change remotes, change branch protections, rerun workflows, or read environment variables.

The replay summary reads only one repository-local persisted bundle and the source reports needed for hash verification. It never writes files and does not apply patches, run validation commands, stage files, create commits, push, force-push, change remotes, change branch protections, rerun workflows, poll remote status, or read environment variables.

## Completion rules

A bundle is `complete` only when:

- patch-apply evidence shows an applied file change and has closed patch application authority;
- post-apply validation shows a passed validation result for the same target path;
- commit verification is verified and reports reviewed changed paths;
- push handoff is pushed, non-force, and references the verified commit;
- post-push verification is verified for the same commit and reviewed paths;
- all provided source-report hash entries are valid lowercase SHA-256 fingerprints for the expected evidence stages.

When any stage is missing, stale, unsafe, or inconsistent, the command reports `bundle_status: blocked` and lists blockers. Use `--require-complete` or `--require-written` when automation should fail closed.

A persisted bundle verifies only when all five source-report entries are present, point to regular repository-local files, and the observed byte count and SHA-256 digest exactly match the preserved bundle metadata. Use `--require-verified` when automation should fail closed on drift.

A persisted bundle is replayable only when it verifies, is complete, preserves the expected evidence stages and statuses, has safe reviewed paths, keeps the target inside those reviewed paths, and records validation steps. Use `--require-replayable` when automation should fail closed on replay blockers.
