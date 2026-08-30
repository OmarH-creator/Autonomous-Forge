# AUTO-235 — Roll back interrupted archive-manifest verification

## Inspection

Started from `main` at AUTO-234 (`38fd161a5852b7acf8458c3ae87371ddecdacbbd`) with GitHub Actions green. Inspected the roadmap, state, README/docs, archive-manifest source/tests, CI, repository policy, recent commits, all visible branches, open issues, and PR history. Seven non-main branches remain historical/diverged. Open issues #1, #6, and #9 are broader project requests rather than blockers. Existing PR work is merged, closed, obsolete, superseded, or unrelated, so no branch work was integrated.

## Objective and rationale

Continue the archive-manifest publication-integrity milestone. AUTO-234 made the installed confirmed archive-manifest path immediately verify a just-published manifest and roll it back on ordinary verification failure. The wrapper caught only `Exception`, so Python-level interruptions such as `KeyboardInterrupt` or `SystemExit` after publication could escape without running rollback and leave an unverified manifest behind.

## Change

`write_verified_maintenance_archive_manifest(...)` now treats any Python `BaseException` raised by immediate verification as a rollback condition. It performs the existing exact-output SHA-256 ownership check, removes only the manifest bytes published by that invocation, fsyncs the parent directory, and then re-raises the original interruption. If rollback itself detects that another process changed the output, it refuses to delete potentially foreign data.

Deterministic tests cover both `KeyboardInterrupt` and `SystemExit` during verification and require that the published manifest is removed. Existing success, integrity-failure rollback, and changed-output ownership tests remain intact.

## Validation

GitHub Actions run `33318761178` on product/test head `084b9a3b7f2313a2164035a6f0d5e6c4d1ba14cd` passed on Python 3.10, 3.11, and 3.12. Each matrix job passed installation, source compilation, installed CLI smoke tests, roadmap validation, and pytest.

## Safety and limitations

No new command, network behavior, Git authority, overwrite path, workflow control, branch, PR, force-push, remote mutation, or protection change was introduced. Abrupt termination that prevents Python cleanup entirely (for example SIGKILL, host failure, interpreter crash, or power loss) remains outside this guarantee. The historical core `write_maintenance_archive_manifest(...)` API also remains directly callable without the verified wrapper.

## Documentation and visuals

Added `docs/ARCHIVE_MANIFEST_INTERRUPTION_ROLLBACK.md` and updated autonomous state. No visual update was warranted because workflow topology did not change.

## Next action

Move immediate publication verification/rollback into the core archive-manifest writer without breaking direct-call compatibility, or address the next evidenced write-integrity race. A new CI failure takes priority.
