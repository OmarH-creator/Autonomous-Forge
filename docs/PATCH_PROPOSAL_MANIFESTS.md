# Patch Proposal Manifests

`forge patch-proposal-manifest` is a read-only handoff surface between described patch intent and any future patch generation work.

It consumes one `forge patch-intent-describe --format json` output plus explicit maintainer-supplied fields:

```bash
forge patch-proposal-manifest \
  --root . \
  --description patch-intent-description.json \
  --objective "Add a guarded parser for reviewed evidence." \
  --path src/autonomous_forge/example.py \
  --path tests/test_example.py \
  --validation "python -m pytest" \
  --require-ready \
  --format json
```

The command is intentionally conservative:

- it only reads the supplied patch-intent description JSON;
- it requires a non-empty objective;
- every requested path must be a safe repository-relative label;
- every requested path must already appear in the described candidate path list;
- at least one validation step must be supplied;
- duplicate candidate, requested path, or validation-step entries are refused;
- `--require-ready` returns exit code `2` unless the manifest is ready.

The manifest does **not** read repository file contents, inspect git diffs, generate patches, apply patches, run commands, approve implementation, enforce policy, mutate saved history, commit, push, or change files.

This gives future patch-generation work a narrow reviewed input shape: objective, paths, validation steps, blockers, and safety boundary, without allowing the tool to infer or fabricate a patch from vague intent.
