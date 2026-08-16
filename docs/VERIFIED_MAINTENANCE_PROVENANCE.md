# Verified maintenance provenance

`forge maintenance-evidence-bundle` can preserve the verified commit/push/post-push chain inside the durable maintenance bundle without dropping that provenance at the archival boundary.

## Canonical verified usage

When the push was produced by `forge verified-push-handoff`, the verified wrapper is now sufficient for the push stage. A second standalone raw `push-handoff.json` file is no longer required:

```bash
forge maintenance-evidence-bundle \
  --root . \
  --patch-apply .ai/evidence/patch-apply.json \
  --post-apply-validation .ai/evidence/post-apply-validation.json \
  --commit-verify .ai/evidence/commit-verify.json \
  --verified-push-handoff .ai/evidence/verified-push-handoff.json \
  --post-push-verify .ai/evidence/post-push-verify.json \
  --bundle-id AUTO-151 \
  --output .ai/evidence/AUTO-151-bundle.json \
  --confirm-write \
  --history-link .ai/run-history/AUTO-151-link.json \
  --confirm-history-link \
  --require-complete \
  --require-written \
  --require-history-linked \
  --format json
```

The legacy `--push-handoff` form remains supported. Callers may also provide both raw and verified inputs; in that compatibility mode Forge builds the established raw bundle first and then applies the verified-provenance consistency checks.

## What is verified

In canonical verified mode, Forge refuses the bundle unless:

- the verified wrapper proves an explicitly confirmed completed push, reports no blockers, and says provenance was preserved;
- the wrapper contains the nested guarded push-handoff evidence produced by the existing push gate;
- wrapper and nested handoff agree on commit SHA, branch, remote, reviewed paths, push completion, and the no-force/no-remote-mutation boundary;
- the established maintenance-bundle checks still accept the nested guarded handoff against patch, validation, commit, and post-push evidence;
- the post-push report proves it consumed verified handoff evidence and preserved provenance;
- commit SHA, branch, remote, reviewed paths, and verified validation commands remain consistent through the durable bundle.

The verified wrapper is read only from a bounded repository-local UTF-8 JSON file. Its SHA-256 and byte count are retained under `verified_provenance.verified_push_source`. For downstream compatibility, the durable `source_reports` array keeps the historical `push_handoff` stage key, but that stage now fingerprints the canonical verified-wrapper file and the bundle records `push_evidence_source: "verified_push_handoff"`.

## Example output fragment

```json
{
  "bundle_status": "complete",
  "bundle_complete": true,
  "push_evidence_source": "verified_push_handoff",
  "summary": {
    "canonical_verified_push": true,
    "source_reports": 5
  },
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

The historical five-stage source-report schema is intentionally retained so existing bundle hash verification, history links, replay, and archive preservation do not need a parallel schema. The difference is that the push-stage fingerprint points at the verified wrapper rather than at a duplicate raw push JSON file.

If any provenance field drifts, canonical bundle construction fails closed or the maintenance bundle is marked `blocked`. No bundle or history link is written unless the existing explicit confirmation gates are also satisfied.

## Safety boundary

This change adds no subprocess execution, Git operation, network access, push, force-push, remote mutation, or workflow mutation. It only reads bounded repository-local JSON, validates the wrapper/nested handoff relationship, reuses established maintenance-bundle checks, fingerprints the canonical push evidence, and enriches the existing durable bundle. Existing explicit confirmation remains required for bundle and run-history writes.
