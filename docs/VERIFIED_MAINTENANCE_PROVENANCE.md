# Verified maintenance provenance

`forge maintenance-evidence-bundle` can preserve the newer verified commit/push/post-push chain inside the existing durable maintenance bundle instead of dropping that provenance at the archival boundary.

## Usage

The existing five evidence inputs remain required for backward compatibility. Add `--verified-push-handoff` when the push was produced by `forge verified-push-handoff` and the post-push report was produced from that verified wrapper:

```bash
forge maintenance-evidence-bundle \
  --root . \
  --patch-apply .ai/evidence/patch-apply.json \
  --post-apply-validation .ai/evidence/post-apply-validation.json \
  --commit-verify .ai/evidence/commit-verify.json \
  --push-handoff .ai/evidence/push-handoff.json \
  --verified-push-handoff .ai/evidence/verified-push-handoff.json \
  --post-push-verify .ai/evidence/post-push-verify.json \
  --bundle-id AUTO-150 \
  --output .ai/evidence/AUTO-150-bundle.json \
  --confirm-write \
  --history-link .ai/run-history/AUTO-150-link.json \
  --confirm-history-link \
  --require-complete \
  --require-written \
  --require-history-linked \
  --format json
```

## What is verified

When `--verified-push-handoff` is supplied, the bundle remains complete only when all of the following agree:

- the maintenance bundle is already complete under the existing patch, validation, commit, push, and post-push checks;
- the verified push wrapper proves an explicitly confirmed completed push with provenance preserved and no blockers;
- commit SHA, branch, remote, and reviewed paths match the maintenance bundle;
- the post-push report proves it consumed verified handoff evidence and preserved provenance;
- the post-push commit, branch, remote, and reviewed paths still match the bundle;
- verified validation commands in the push wrapper and post-push report are identical;
- those verified validation commands exactly match the validation steps retained by the maintenance bundle.

The verified wrapper is read only from a bounded repository-local UTF-8 JSON file. Its SHA-256 and byte count are retained under `verified_provenance.verified_push_source` for stale-input detection.

## Example output fragment

```json
{
  "bundle_status": "complete",
  "bundle_complete": true,
  "verified_provenance": {
    "status": "complete",
    "provenance_preserved": true,
    "verified_commit": "abc1234",
    "reviewed_paths": ["README.md"],
    "verified_validation_commands": ["python -m pytest"],
    "verified_push_source": {
      "path": ".ai/evidence/verified-push-handoff.json",
      "sha256": "<64 lowercase hex characters>",
      "bytes": 1234
    },
    "blockers": []
  }
}
```

If any provenance field drifts, the maintenance bundle is changed to `blocked`, `bundle_complete` becomes `false`, and the specific mismatch is appended to `bundle_blockers`. No file is written unless the existing explicit write gate is also satisfied.

## Safety boundary

This extension adds no new subprocess execution, Git operation, network access, push, force-push, remote mutation, or workflow mutation. It only reads bounded repository-local JSON, compares already produced evidence, and enriches the existing maintenance bundle. Existing explicit confirmation remains required for durable bundle and run-history writes.
