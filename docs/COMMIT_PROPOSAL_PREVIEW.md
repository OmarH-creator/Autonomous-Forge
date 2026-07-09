# Commit Proposal Preview

`forge commit-proposal-preview` prepares reviewable commit metadata from a ready `forge commit-readiness --format json` report. It is a metadata preview only: it does not stage files, create commits, push, inspect repository contents, or run validation.

## Usage

```bash
forge commit-proposal-preview \
  --root . \
  --commit-readiness commit-readiness.json \
  --summary "feat: add guarded commit preview" \
  --body-line "Summarize ready evidence before commit creation." \
  --require-ready \
  --format json > commit-proposal-preview.json
```

Compatibility entry point:

```bash
forge-commit-proposal-preview --help
```

## Inputs

- `--commit-readiness`: repository-local JSON produced by `forge commit-readiness --format json`.
- `--summary`: required one-line commit summary using a reviewable `<type>: <description>` style and capped at 72 characters.
- `--body-line`: optional commit body line; may be repeated. Blank lines are ignored, body lines are bounded, and simple secret-marker strings are refused.
- `--require-ready`: returns exit code `2` unless the preview status is `ready`.
- `--format`: `text` or `json`; default is `text`.

## Ready criteria

The preview is `ready` only when the supplied commit-readiness evidence is ready, was produced in read-only mode, contains reviewed paths and validation steps, has no readiness blockers, and keeps both `commit_allowed` and `commit_workflow_allowed` false.

## Output

JSON output includes `proposal_status`, `commit_summary`, `commit_body_lines`, `commit_message_preview`, reviewed paths, validation steps, status contexts, blocker details, and explicit `commit_allowed`, `commit_creation_allowed`, and `push_allowed` fields set to `false`.

## Safety boundary

This command reads supplied commit-readiness JSON and explicit commit metadata only. It does not inspect repository file contents, inspect raw diffs, run validation, collect workflow status, create commits, stage files, push, mutate saved history, read environment variables, or change repository files.
