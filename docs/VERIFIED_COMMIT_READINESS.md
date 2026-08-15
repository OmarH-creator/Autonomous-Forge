# Verified commit readiness

`forge verified-commit-readiness` carries the verified patch/validation evidence chain into the existing commit-readiness gate.

It is read-only. The command requires one repository-local guarded patch-apply JSON file, one or more repository-local `forge verified-validation-run --format json` results, and one commit-status-review JSON file. Every validation step retained by the patch evidence must have a successful verified validation result before readiness can become `ready`.

```bash
forge verified-commit-readiness \
  --root . \
  --patch-apply .ai/evidence/patch-apply.json \
  --verified-validation .ai/evidence/compile.json \
  --verified-validation .ai/evidence/tests.json \
  --status-review .ai/evidence/status.json \
  --require-ready \
  --format json
```

Example output excerpt:

```json
{
  "readiness": "ready",
  "target_path": "src/example.py",
  "verified_validation_commands": [
    "python -m compileall src",
    "python -m pytest"
  ],
  "missing_verified_validation_commands": [],
  "commit_allowed": false,
  "commit_workflow_allowed": false
}
```

The command fails closed on external, symlinked, oversized, malformed, target-mismatched, patch-source-mismatched, or unknown-command evidence. A failed or missing required validation does not count as successful. The existing final diff and commit-status gates are reused.

This command does **not** stage files, create a commit, push, poll workflows, modify remotes, force-push, or alter branch protections. A `ready` result is evidence for the separately confirmation-gated commit path; it is not commit authority by itself.
