# AUTO-228 — Stream archive-package verification hashing

## Inspection

- Started from green `main` head `c6197551f7ab3a0808e0d076ba8849aa8c309ae3`; Actions run `33240184361` completed successfully.
- Inspected README/docs/examples, package verification source/tests, policy/config/CI, `.ai` plan/state/changelog/decisions, recent commits, open issues, all eight visible branches, and recent PR history.
- Seven non-main branches remain historical/diverged. Recent PRs are merged, closed, obsolete, or unrelated; no branch or PR warranted integration.
- Repository policy allows `src/**`, `tests/**`, `docs/**`, README, and `.ai/**`; workflow/secret paths remained untouched.

## Objective

Remove whole-file and whole-member memory materialization from `forge maintenance-archive-package-verify` while preserving exact package and member byte-count/SHA-256 verification semantics.

## Work

- Replaced package-file `Path.read_bytes()` SHA-256 with incremental 64 KiB reads.
- Added a shared streaming hash helper that returns both byte count and SHA-256.
- Replaced tar-member `extractfile(...).read()` with chunked streaming through the extracted member handle.
- Replaced `ZipFile.read()` with `ZipFile.open()` plus chunked streaming.
- Preserved expected-path, extra/missing-entry, byte-count, and SHA-256 drift checks.
- Added deterministic regression coverage that forbids whole-package `Path.read_bytes()` and `ZipFile.read()` during successful package verification.
- Updated package-verification documentation and autonomous status records. No new visual was warranted because workflow topology did not change.

## Validation

- Product/test head `f68340e1128a1a5c088b483b2c7b8256effd9d21` passed GitHub Actions run `33249312132`.
- Python 3.10, 3.11, and 3.12 passed package installation, source compilation, installed CLI smoke checks, roadmap validation, and pytest.
- Final status/documentation head is rechecked before the run is reported complete.

## Safety and limitations

- Read-only package verification remains read-only and receives no persistence, Git, push, workflow, network, remote, or branch-protection authority.
- External validation remains advisory-only and live workflow status remains informational-only.
- Hash verification still intentionally reads/decompresses every byte; memory is bounded, but runtime and I/O remain proportional to package size.
- No package-size ceiling or streaming archive-index parser was introduced.

## Next action

Inspect downstream preservation/package consumers for the next concrete whole-file materialization or cross-stage integrity defect. Any fresh CI failure takes priority.
