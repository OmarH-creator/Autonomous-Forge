# Autonomous Changelog

## 2026-07-07 — AUTO-015

- Task ID: AUTO-015
- Summary: Hardened the GitHub Actions test workflow to install the local package, invoke the installed `forge --version` console script, compile source, and run the suite without `PYTHONPATH=src`.
- Why it matters: The previous workflow tested source-tree imports only, so it could not detect broken package installation or console-script metadata.
- Validation completed: Reviewed the pinned action revisions, least-privilege `contents: read` permission, workflow structure, `pyproject.toml` console-script definition, and CLI version path through the GitHub repository API. Pull-request matrix validation on Python 3.10, 3.11, and 3.12 is pending.
- Commit hash: 45014d67deebc9540fefc0a3bbde72f26a70463f (implementation); documentation commits follow on `auto/ci-package-smoke`.
- Follow-up notes: Inspect and record the first workflow result before adding product behavior. The change adds no runtime dependency, network feature, or autonomous write capability.

## Prior history

Roadmaps v1 and v2, their completed tasks, and earlier run context are preserved in Git history and the decisions log. This changelog now retains the current actionable maintenance history to avoid duplicating a completed roadmap.
