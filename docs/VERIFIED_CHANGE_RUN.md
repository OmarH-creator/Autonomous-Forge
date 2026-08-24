# Verified change run

`forge verified-change-run` is the first orchestration surface for the already-proven guarded maintenance chain. It composes a live-diff-verified patch with all validation steps retained by that patch, verified commit readiness, and optional verified local commit creation.

```bash
forge verified-change-run \
  --patch-apply .ai/evidence/patch-apply.json \
  --status-review .ai/evidence/status-review.json \
  --summary "fix: apply reviewed maintenance change" \
  --confirm-validation \
  --confirm-commit-create \
  --require-committed \
  --format json
```

The command does not introduce a single all-powerful confirmation. Validation execution is gated by `--confirm-validation`; commit creation is separately gated by `--confirm-commit-create`. If validation fails, later validation commands are not run and commit creation is not attempted. If validations pass but commit confirmation is omitted, the result stops at `ready_for_commit`.

After every retained validation command passes, Forge hashes the exact current bytes of the reviewed target and stores that SHA-256 in verified commit-readiness evidence. Immediately before any Git staging operation, verified commit creation re-hashes the target and requires an exact match. A file edited after validation therefore fails closed before staging instead of allowing stale or unvalidated bytes into the commit. The target hash is bounded to the same 1 MB review envelope and must resolve to a regular non-symlink file inside the repository root.

Verified commit creation now stages through a private temporary Git index initialized from the reviewed `HEAD`, rather than consuming the repository's shared staging area. If a reviewed path is already staged in the shared index, Forge refuses the commit so it cannot overwrite caller-owned staging. Unrelated staged paths are not present in the private index and therefore cannot enter the Forge commit.

Before private staging, Forge records the exact shared-index entries for reviewed paths and the exact parent `HEAD` that the reviewed commit is expected to build on. Inside the private index, Forge reads the exact staged target with `git show :<target>`, applies the same 1 MB bound, computes its SHA-256, and requires it to equal the validated target digest. It also inspects the complete private staged path set with NUL-delimited `git diff --cached --name-only -z --` and requires that set to exactly equal the reviewed paths.

Immediately before `git commit`, Forge re-resolves `HEAD`, then performs both private-index checks a second time. The final staged target SHA-256 is recorded as `precommit_staged_target_sha256` and the final path set as `precommit_staged_paths`. If the parent, target bytes, or staged path set drift, commit creation is blocked.

After Git reports the commit created, Forge reads the target back from the created commit with `git show <sha>:<target>`, computes the same bounded SHA-256, and requires it to equal the validated target digest before the commit can be marked verified. Forge also resolves `<sha>^` and requires that parent to equal the reviewed parent `HEAD`, and it requires the commit's exact changed-path set to equal the reviewed paths.

A successful private-index commit moves `HEAD`, so Forge then verifies that the shared-index entries for reviewed paths are still exactly the entries captured before staging. If they are unchanged, Forge synchronizes only those reviewed paths to the new `HEAD` with `git reset --quiet HEAD -- <reviewed paths>`. This prevents staged reversions while preserving unrelated caller staging. If the reviewed entries changed concurrently, Forge refuses the synchronization and downgrades the created commit to `created_unverified` for human inspection rather than overwriting the newer shared-index state.

These are fail-closed continuity checks rather than a compare-and-swap branch-ref update. A sufficiently narrow concurrent `HEAD` movement can still race with commit creation, and the shared-index synchronization is a separate Git transaction. Existing post-commit parent, target-byte, and exact-path verification remains defense in depth; a created-but-unverified commit is intentionally not rewritten or reset automatically.

The command reuses the existing `verified-validation-run`, `verified-commit-readiness`, and verified-commit creation contracts. It does not push, change remotes, poll workflows, force-push, or modify branch protections. Push and post-push stages remain separate reviewable commands.
