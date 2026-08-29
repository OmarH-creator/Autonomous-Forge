# AUTO-227 — Stream archive-copy verification hashing

## Objective

Remove whole-file memory materialization from the read-only copied-archive verification boundary while preserving all existing verification semantics and authority gates.

## Repository assessment

- Started from green `main` head `71e647fd6fa299b976e64b23af2a3e1c92c0bb13` (AUTO-226), whose Actions run `33230603580` completed successfully.
- Inspected README/docs/examples, archive-copy verification source/tests, repository policy/config/CI, `.ai` plan/state/changelog/decisions, recent commits, open issues, all eight visible branches, and PR history.
- The seven non-main branches remain historical/diverged; recent PRs are merged, closed, obsolete, or unrelated. No branch or PR warranted integration.
- The highest-value concrete defect was `maintenance_archive_copy_verify._file_sha256()` using `Path.read_bytes()`, which materialized each copied preservation artifact wholly in memory during verification.

## Change

- Replaced whole-file SHA-256 with incremental 64 KiB reads in `maintenance_archive_copy_verify.py`.
- Kept byte-count and digest comparison behavior unchanged.
- Updated the verification safety text and command documentation to describe bounded-memory hashing.
- Added deterministic tests that disable `Path.read_bytes()` for the target helper and reject whole-file reads specifically inside the copied archive root during the real verification path.

## Safety

Archive-copy verification remains read-only. Written-manifest verification, repository/archive-root containment, missing-file checks, byte-count drift checks, SHA-256 drift checks, advisory external-validation provenance, and informational live workflow-status provenance remain unchanged. No persistence, Git mutation, validation execution, workflow mutation, push, network, remote, or branch-protection authority was added.

## Validation

The first regression head exposed one test-scoping mistake: globally disabling `Path.read_bytes()` also broke upstream archive-manifest verification before the copied-root verifier ran. The test was narrowed to the copied archive root without changing product behavior. Corrected head `a40f1f2e5ff24e7ddd31eff4519837c8238696bc` passed Actions run `33240113217`; Python 3.10, 3.11, and 3.12 all passed installation, source compilation, installed CLI smoke tests, roadmap validation, and pytest.

## Limitations

Streaming bounds memory, not total verification time or I/O; every byte still contributes to SHA-256. `maintenance_archive_package_verify.py` still contains whole-file and whole-member materialization paths and is the next concrete bounded-memory candidate.

## Next action

Harden package verification to stream both package-file hashing and member hashing without changing verification semantics; any fresh CI failure takes priority.
