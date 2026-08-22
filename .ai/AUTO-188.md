# AUTO-188 — Harden archive-package publication against races and partial final artifacts

## Inspection

Reviewed README/docs, archive package source/tests, repository policy/config/CI, current autonomous state, recent commits, open issues, all visible branches, and recent pull requests. AUTO-187 has no exposed final-head checks through the connected status/run surfaces. Historical non-main branches are stale/diverged and no PR contains newer applicable package-persistence work.

## Objective

Close the remaining time-of-check/time-of-use and partial-output integrity gap in `forge maintenance-archive-package`.

Before AUTO-188, Forge checked that the package destination did not exist and then opened that final path directly with tar/zip write mode. Another writer could create the path after preflight and be replaced, while a construction failure could leave a partial file at the final preservation path.

## Change

- build tar/zip output in a temporary file in the destination directory;
- close and fsync the completed temporary package;
- publish with an atomic no-clobber hard link;
- fsync the parent directory after publication;
- always clean the temporary name;
- fail closed if a racing writer creates the destination;
- never publish a partial final package when archive construction fails.

## Validation

- `python -m py_compile` passed for the changed implementation and focused regression test file;
- a focused executable smoke passed normal publication and simulated racing-writer refusal/preservation;
- deterministic regression tests cover race preservation, temporary cleanup, file/directory fsync, and construction-failure cleanup;
- full checkout/full pytest is unavailable because the runtime cannot resolve `github.com`;
- no Python 3.10/3.11/3.12 green claim is made until GitHub CI is observable.

## Safety and disposition

The existing ready-preview gate, explicit package confirmation, repository containment, supported-format checks, and no-overwrite behavior remain unchanged. No branch/PR, force-push, remote change, workflow mutation, network capability, or protection change was introduced. No visual update was needed because the architecture is unchanged.

## Next

Inspect AUTO-188 CI when observable. Any failure takes priority; if green, continue the same end-to-end persistence/provenance milestone only when a concrete defect or meaningful handoff reduction is identified.
