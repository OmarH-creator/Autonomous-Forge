# Command Output Contracts

Autonomous Forge commands are currently read-only except for explicitly confirmed local persistence commands and the narrow opt-in local validation executor. They inspect local files, print human-readable summaries or structured previews, and do not modify repository files unless the command contract explicitly says so.

These contracts describe implemented behavior only. They are intentionally plain so contributors and future automation can rely on stable command purposes without assuming enforcement or execution features that do not exist yet.

## General expectations

- Commands write results to standard output.
- Commands return exit code `0` when the requested read-only inspection, explicitly confirmed local persistence action, or completed executor run succeeds as a command invocation.
- Commands return exit code `2` for missing required input files, malformed roadmap/policy/history input, refused write preconditions, refused executor preconditions, blocked executor runs, or explicitly requested fail-closed audit gates whose evidence is not clear or ready.
- Commands should not create, edit, delete, commit, push, call networks, read environment variables, scan secrets, or enforce policy decisions unless an explicit command contract narrowly allows a local file write or one exact no-shell validation command.
- Human-readable output may be extended conservatively, but existing status phrases should remain stable when practical.
- JSON output is intended for review and automation handoff; it must remain deterministic and must not imply approval.

## `forge change-readiness`

Purpose: combine clear supplied git-diff review JSON and clear supplied commit-status review JSON into one advisory change-readiness summary before any future patch-application workflow relies on the change.

Inputs:

- `--diff-review`: required repository-local `.json` file produced by `forge git-diff-review --format json`.
- `--status-review`: required repository-local `.json` file produced by `forge commit-status-review --format json`.
- `--root`: root used to constrain both supplied review input paths, defaulting to `.`.
- `--require-ready`: optional fail-closed gate; when present, the command returns exit code `2` unless the combined summary is `ready`.
- `--format`: `text` or `json`, defaulting to `text`.

Expected successful text output includes these stable lines:

```text
Autonomous Forge change readiness summary
Mode: read-only
Source: supplied git-diff review and commit-status review JSON
Readiness: ready|blocked
Change application allowed: false
Commit: ...
Reviewed paths:
Status contexts:
Summary:
Review checks:
Review blockers:
Safety boundary: Change-readiness reads supplied git-diff review JSON and commit-status review JSON only; ...
```

Expected JSON output includes `title`, `mode`, `source`, `readiness`, `change_application_allowed`, `commit_sha`, `reviewed_paths`, `status_contexts`, `summary`, `review_checks`, `review_blockers`, `next_step`, and `safety_boundary`.

Exit codes:

- `0` when the summary is produced and `--require-ready` is not requested.
- `0` when `--require-ready` is requested and readiness is `ready`.
- `2` when `--require-ready` is requested and readiness is `blocked`.
- `2` when an input is outside the configured root, missing, not a `.json` regular file, a symlink, malformed JSON, not a JSON object, too large, or an unsupported output format is requested.

Safety limits: change-readiness reads supplied git-diff review JSON and commit-status review JSON only. It does not call networks, poll GitHub, run workflows, run commands, read repository file contents, inspect raw diffs, generate patches, apply patches, approve implementation, enforce policy decisions, mutate saved history, read environment variables, commit, push, or change repository files. `--require-ready` changes only the process exit code.

## `forge commit-status-review`

Purpose: review supplied commit-status, check-run, or workflow-run JSON evidence before future patch application or change-readiness workflows rely on validation status.

Inputs:

- `--status`: required repository-local `.json` file containing supplied status evidence.
- `--root`: root used to constrain the status input path, defaulting to `.`.
- `--require-clear`: optional fail-closed gate; when present, the command returns exit code `2` unless all supplied status evidence is successful.
- `--format`: `text` or `json`, defaulting to `text`.

Expected successful text output includes these stable lines:

```text
Autonomous Forge commit status review
Mode: read-only
Source: supplied commit/workflow status JSON
Commit: ...
Review status: clear|blocked
Status contexts:
Summary:
Review blockers:
Requires attention: true|false
Safety boundary: Commit-status review reads supplied JSON status evidence only; ...
```

Expected JSON output includes `title`, `mode`, `source`, `commit_sha`, `review_status`, `status_reviews`, `summary`, `review_blockers`, `requires_attention`, `reason`, `next_step`, and `safety_boundary`.

Exit codes:

- `0` when the review is produced and `--require-clear` is not requested.
- `0` when `--require-clear` is requested and review status is `clear`.
- `2` when `--require-clear` is requested and review status is `blocked`.
- `2` when an input is outside the configured root, missing, not a `.json` regular file, a symlink, malformed JSON, not a JSON object, too large, or an unsupported output format is requested.

Safety limits: commit-status-review reads supplied JSON status evidence only. It does not call networks, poll GitHub, run workflows, run commands, inspect diffs, read repository file contents, infer correctness beyond supplied status fields, approve implementation, enforce policy decisions, mutate saved history, read environment variables, commit, push, or change repository files. `--require-clear` changes only the process exit code.

## `forge patch-text-review`

Purpose: review ready `forge patch-text-preflight --format json` output plus explicit per-path patch summaries before any future patch-text generation or apply workflow relies on that evidence.

Inputs:

- `--preflight`: patch-text preflight JSON output inside the configured root.
- `--root`: root used to constrain the review input path, defaulting to `.`.
- `--path`: reviewed repository-relative path label; repeat once per preflight target path.
- `--patch-summary`: explicit patch text summary for the matching `--path`; repeat once per reviewed path.
- `--require-ready`: optional fail-closed gate; when present, the command returns exit code `2` unless review status is `ready`.
- `--format`: `text` or `json`, defaulting to `text`.

Expected successful text output includes these stable lines:

```text
Autonomous Forge patch text review
Mode: read-only
Preflight source: ...
Review status: ready|blocked
Patch text review allowed: true|false
Objective: ...
Reviewed patch summaries:
Review blockers:
Safety boundary: Patch text review reads supplied patch-text-preflight JSON and explicit summary metadata only; ...
```

Expected JSON output includes `title`, `mode`, `preflight_source`, `review_status`, `patch_text_review_allowed`, `objective`, `preflight_target_count`, `reviewed_path_count`, `preflight_target_paths`, `reviewed_patch_summaries`, `validation_steps`, `review_checks`, `review_blockers`, `next_step`, and `safety_boundary`.

Exit codes:

- `0` when the review is produced and `--require-ready` is not requested.
- `0` when `--require-ready` is requested and review status is `ready`.
- `2` when `--require-ready` is requested and review status is `blocked`.
- `2` when an input is outside the configured root, missing, not a `.json` regular file, a symlink, malformed JSON, not a patch-text preflight payload, not read-only, has invalid preflight entries, contains unsafe path labels, or an unsupported output format is requested.

Safety limits: patch-text-review reads supplied patch-text-preflight JSON and explicit summary metadata only. It does not read repository file contents, inspect git diffs, generate patch text, apply patches, run commands, check workflow status, infer correctness, approve implementation, enforce policy decisions, mutate saved history, call networks, read environment variables, commit, push, or change repository files. `--require-ready` changes only the process exit code.

## `forge patch-intent-review`

Purpose: review one clear `forge diff-source-handoff --format json` output before future patch-intent or git-diff workflows rely on that evidence.

Inputs:

- `--diff-source`: diff-source handoff JSON output inside the configured root.
- `--root`: root used to constrain the review input path, defaulting to `.`.
- `--require-ready`: optional fail-closed gate; when present, the command returns exit code `2` unless readiness is `ready`.
- `--format`: `text` or `json`, defaulting to `text`.

Expected successful text output includes these stable lines:

```text
Autonomous Forge patch-intent review
Mode: read-only
Source: ...
Readiness: ready|blocked
Patch intent allowed: true|false
Compared path count: ...
Compared paths:
Review blockers:
Safety boundary: Patch-intent review reads supplied diff-source handoff JSON only; ...
```

Expected JSON output includes `mode`, `source`, `readiness`, `patch_intent_allowed`, `compared_path_count`, `compared_paths`, `required_evidence`, `review_blockers`, `next_step`, and `safety_boundary`.

Exit codes:

- `0` when the review is produced and `--require-ready` is not requested.
- `0` when `--require-ready` is requested and readiness is `ready`.
- `2` when `--require-ready` is requested and readiness is `blocked`.
- `2` when an input is outside the configured root, missing, not a `.json` regular file, a symlink, malformed JSON, not a diff-source handoff payload, not read-only, has invalid comparison entries, or an unsupported output format is requested.

Safety limits: patch-intent-review reads supplied diff-source handoff JSON only. It does not read repository file contents, inspect git diffs, generate patches, run commands, check workflow status, infer correctness, approve implementation, enforce policy decisions, mutate saved history, call networks, read environment variables, commit, push, or change repository files. `--require-ready` changes only the process exit code.

## `forge diff-source-handoff`

Purpose: compare two explicit `forge content-audit --format json` outputs before future patch or git-diff workflows rely on content-audit evidence.

Inputs:

- `--before`: earlier content-audit JSON output inside the configured root.
- `--after`: later content-audit JSON output inside the configured root.
- `--root`: root used to constrain audit-output paths, defaulting to `.`.
- `--require-clear`: optional fail-closed gate; when present, the command returns exit code `2` unless the comparison requires no attention.
- `--format`: `text` or `json`, defaulting to `text`.

Expected successful text output includes these stable lines:

```text
Autonomous Forge diff-source handoff
Mode: read-only
Source: explicit content-audit JSON outputs
Compared paths:
- ...: status=added|removed|changed|unchanged; changed_fields=...; before_review=...; after_review=...
Summary:
- added: ...
- removed: ...
- changed: ...
- unchanged: ...
Requires attention: true|false
Safety boundary: Diff-source handoff reads supplied content-audit JSON only; ...
```

Expected JSON output includes `mode`, `source`, `before`, `after`, `comparisons`, `summary`, `requires_attention`, `reason`, and `safety_boundary`.

Exit codes:

- `0` when the handoff is produced and `--require-clear` is not requested.
- `0` when `--require-clear` is requested and `requires_attention` is `false`.
- `2` when `--require-clear` is requested and `requires_attention` is `true`.
- `2` when an input is outside the configured root, missing, not a `.json` regular file, a symlink, malformed JSON, not a content-audit payload, not read-only, has invalid audited entries, has duplicate audited paths, or an unsupported output format is requested.

Safety limits: diff-source-handoff reads supplied content-audit JSON only. It does not read repository file contents, inspect git diffs, generate patches, run commands, check workflow status, infer correctness, approve implementation, enforce policy decisions, mutate saved history, call networks, read environment variables, commit, push, or change repository files. `--require-clear` changes only the process exit code.

## `forge content-audit`

Purpose: audit explicit repository-relative file contents before future patch or diff workflows without printing file content or changing files.

Inputs:

- `--policy`: policy Markdown path, defaulting to `.forge/policy.md`.
- `--root`: repository root used to constrain audited paths, defaulting to `.`.
- `--file`: repository-relative path to audit; repeat for multiple paths.
- `--format`: `text` or `json`, defaulting to `text`.

Expected successful text output includes these stable lines:

```text
Autonomous Forge changed-content audit
Mode: read-only
Audited paths:
- ...: policy=allowed|prohibited|unknown; content=readable|missing|directory|not-regular-file|non-utf8|too-large|invalid-path; lines=...; bytes=...; review=clear|blocked|needs-policy-review|needs-content-review|needs-secret-review
Summary:
- clear: ...
Safety boundary: Changed-content audit output only; ...
```

Expected JSON output includes `mode`, `source`, `audited_paths`, `summary`, `requires_attention`, `reason`, and `safety_boundary`.

Exit codes:

- `0` when the audit is produced.
- `2` when policy input is missing or malformed, output format is unsupported, or the audit is refused.

Safety limits: content-audit is a pre-patch review surface only. It reads file contents only to compute bounded metadata and configured secret-marker signals, never prints file contents, and does not inspect git diffs, generate patches, run commands, check workflow status, infer correctness, approve implementation, enforce policy decisions, mutate saved history, call networks, read environment variables, commit, push, or change repository files.

## `forge executor-observation-audit`

Purpose: audit aggregate saved executor observations across direct `.ai/run-history/*.json` records without changing files.

Inputs:

- `--root`: repository root containing `.ai/run-history/`, defaulting to `.`.
- `--max-records`: maximum number of direct JSON records to audit, defaulting to `20`.
- `--require-clear`: optional fail-closed gate; when present, the command returns exit code `2` unless the aggregate status is `clear`.
- `--format`: `text` or `json`, defaulting to `text`.

Expected successful text output includes these stable lines:

```text
Autonomous Forge executor-observation audit
Mode: read-only
Summary:
- observed clear: ...
- observed blocked: ...
- missing observation: ...
- needs review: ...
- overall status: clear|blocked|needs-review|needs-validation|no-records
```
