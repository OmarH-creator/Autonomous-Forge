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
Safety boundary: Executor-observation audit output only; ...
```

Expected JSON output includes `mode`, `history_dir`, `history_dir_status`, `summary`, `records`, `index_validation_guard`, and `safety_boundary`.

Exit codes:

- `0` when the audit is produced and `--require-clear` is not requested.
- `0` when `--require-clear` is requested and the aggregate status is `clear`.
- `2` when the audit is refused, input is unsafe, `--max-records` is invalid, or `--require-clear` is requested and the aggregate status is anything other than `clear`.

Safety limits: executor-observation-audit is an observation guard only. It does not run validation commands, poll workflows, verify commits, inspect diffs, read changed-file contents, generate patches, infer success beyond saved fields, approve execution, enforce policy decisions, mutate saved history, call networks, read environment variables, commit, push, or change repository files. `--require-clear` changes only the process exit code.
