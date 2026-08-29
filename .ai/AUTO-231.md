# AUTO-231 — Bind archive history-link bytes without changing provenance authority

## Objective

Close the remaining preservation integrity gap identified by AUTO-230: the selected `run_history_link` was preserved as an archive entry without an expected SHA-256, so later manifest/copy/package verification could detect byte-count drift but not same-size content drift.

## Repository inspection

The cycle started from AUTO-230 final head `0e2bdc45ad2d893ec130d4e9f5513cf4e05eb4fc`, whose Actions run `33270311329` was green. Inspection covered README/docs/examples, archive and preservation source/tests, package/config/CI, `.forge/policy.md`, `.ai/AUTONOMOUS_PLAN.md`, `.ai/AUTONOMOUS_STATE.md`, `.ai/AUTONOMOUS_CHANGELOG.md`, `.ai/DECISIONS.md`, recent commits, open issues, all eight visible branches, and recent/older PR history.

Seven non-main branches remain historical/diverged. The inspected PRs are merged, closed, obsolete, superseded, or unrelated to current `main`; nothing warranted integration. Open issues remain broader project requests rather than release blockers.

The roadmap already contains the shipped policy-aware planning milestone and the guarded end-to-end maintenance path, so this run continued the active preservation-integrity milestone instead of creating another standalone read-only command.

## Rationale and design

`maintenance_archive_manifest.py` already established expected SHA-256 values for the selected maintenance bundle and source reports, while the selected `run_history_link` carried only existence and byte count. That made the link's archive-integrity gate advisory and propagated a digest-less entry through archive-copy and archive-package stages.

AUTO-231 computes the selected link's SHA-256 at the archive-manifest boundary using the existing incremental 64 KiB hashing helper. The resulting expected digest is carried by the written manifest, so later written-manifest verification rejects same-size link drift and downstream copy/package stages inherit the same content binding.

The new digest has deliberately narrow semantics: it proves continuity of exact bytes selected for preservation. It does not prove that the link's claims are true, does not make external validation equivalent to executor validation, does not make retained live workflow status an archive gate, and does not prove signer identity. Legacy written manifests without an expected link digest stay compatible and retain their historical advisory behavior rather than receiving a fabricated digest.

## Changes

- `src/autonomous_forge/maintenance_archive_manifest.py`
  - computes an incremental SHA-256 for the selected run-history link during manifest construction;
  - records `sha256`, `current_sha256`, and `sha256_verified` on the link archive entry;
  - documents in the returned safety boundary that this is content binding only, not provenance promotion.
- `tests/test_archive_history_link_binding.py`
  - proves the link receives the exact current SHA-256 while external/live provenance semantics remain non-authoritative;
  - proves a same-size history-link mutation after manifest write is rejected by later manifest verification even though the byte count still matches.
- `tests/test_auto230_archive_package_streaming_write.py`
  - updates the prior AUTO-230 compatibility assertion from expecting a digest-less advisory package entry to requiring the now fully digest-bound current package-entry set, while preserving its no-whole-file-read streaming checks.
- `docs/MAINTENANCE_ARCHIVE_MANIFEST.md`
  - documents link-byte binding, downstream continuity, legacy-manifest compatibility, and the distinction between content integrity and provenance authority.
- `.ai/AUTONOMOUS_STATE.md`
  - records the completed objective, inspection, validation, safety boundary, and next task.
- README `Current Autonomous Status` is required to reflect AUTO-231 at the end of the cycle; no visual topology change is warranted.

## Validation

The first product commit `b293d93a34dc3ca1d428ed30e5ccd0a8b4d86772` reached the pytest stage on Python 3.10, 3.11, and 3.12 and failed one existing AUTO-230 assertion. The failure was useful evidence, not a product rollback signal: the assertion explicitly required at least one package entry to lack a SHA-256, which is exactly the condition AUTO-231 intentionally removes.

After updating that regression contract, corrected head `15c052c380b4e5d643805669fda2236a6d0ed360` passed GitHub Actions run `33280167293`. Across Python 3.10, 3.11, and 3.12, package installation, source compilation, installed CLI smoke checks, roadmap validation, and the complete pytest suite passed.

A direct local checkout was not available from this runtime because outbound DNS to `github.com` failed, so repository inspection and CI evidence used the GitHub repository/Actions APIs as the source of truth. No validation evidence is fabricated.

## Safety and diff review

All changed paths are inside policy-permitted `src/**`, `tests/**`, `docs/**`, README, and `.ai/**` areas. No workflows, secrets, generated artifacts, remotes, branch protections, or unrelated files were intentionally changed. No branch, PR, merge, force-push, or protection weakening was used.

The write-capable archive-manifest command retains explicit `--confirm-write`, repository containment, ready-manifest gating, no-clobber publication, and downstream verification. AUTO-231 adds no execution, commit, push, network, or workflow authority.

## Limitations

- SHA-256 proves byte continuity, not signer identity or semantic truth.
- Exact hashing still costs time and disk I/O proportional to evidence size, though the existing incremental helper bounds hashing memory.
- Legacy written manifests without the expected link digest cannot retroactively prove same-size history-link continuity and therefore remain advisory for that entry.

## Next highest-value opportunity

Inspect the remaining preservation metadata flow for any entry that still crosses manifest/copy/package boundaries without an expected digest or another concrete cross-stage integrity guarantee. A fresh CI failure takes priority over new feature work.
