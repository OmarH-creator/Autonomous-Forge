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

Before staging, Forge also records the exact parent `HEAD` that the reviewed commit is expected to build on. After `git add` and staged-byte verification, it re-resolves `HEAD` immediately before `git commit`. If another process advanced or rewound the branch during that window, Forge refuses to create a commit on the unreviewed parent.

After `git add`, Forge reads the exact staged target from the index with `git show :<target>`, applies the same 1 MB bound, computes its SHA-256, and requires it to equal the validated target digest. It also inspects the complete staged path set with NUL-delimited `git diff --cached --name-only -z --` and requires that set to exactly equal the reviewed paths.

Immediately before `git commit`, Forge performs both index checks a second time after the parent-HEAD check. The final staged target SHA-256 is recorded as `precommit_staged_target_sha256` and the final path set as `precommit_staged_paths`. If either differs from the validated target or reviewed paths, commit creation is blocked. This materially narrows the remaining index-race window and prevents a mutation that lands between the first index review and the pre-commit boundary from becoming a commit.

After Git reports the commit created, Forge reads the target back from the created commit with `git show <sha>:<target>`, computes the same bounded SHA-256, and requires it to equal the validated target digest before the commit can be marked verified. Forge also resolves `<sha>^` and requires that parent to equal the reviewed parent `HEAD`. The report retains `reviewed_parent_commit`, `precommit_parent_commit`, and `created_commit_parent` so the complete base-continuity check is reviewable.

These are fail-closed staleness and continuity checks rather than a shared Git index/ref lock. Another process can still race after the final index revalidation and before Git consumes the index. If Git nevertheless creates a commit on a different parent, with different target bytes, or with a different changed-path set, Forge reports it as `created_unverified`. A created-but-unverified commit is intentionally not rewritten or reset automatically and requires human handling.

The command reuses the existing `verified-validation-run`, `verified-commit-readiness`, and `verified-commit-create` contracts. It does not push, change remotes, poll workflows, force-push, or modify branch protections. Push and post-push stages remain separate reviewable commands.
