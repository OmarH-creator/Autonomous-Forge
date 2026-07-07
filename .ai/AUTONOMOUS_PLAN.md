# Autonomous Forge Roadmap

## Product vision

Autonomous Forge is a local-first Python CLI for safely inspecting repository-native maintenance plans, policies, and readiness signals before any future write or execution behavior is considered.

## Product scope and non-goals

The project reads local repository files and produces deterministic, human-readable output. It is not a hosted platform, dashboard, autonomous executor, deployment system, repository-permission manager, secret scanner, or telemetry product.

## Current architecture

The package lives in `src/autonomous_forge`; tests are in `tests/`; user-facing documentation is in `docs/`; policy and durable project memory are stored in `.forge/` and `.ai/`. The `forge` CLI exposes read-only commands for task parsing and selection, plan linting, report generation, policy inspection, run-summary preview, and repository inventory. GitHub Actions tests Python 3.10–3.12, installs the package, compiles source, smoke-tests the installed console script, and runs the test suite.

## Current implementation status

Roadmaps v1 and v2 are complete. They established the package, read-only command surface, policy parsing, plan linting, command contracts, run-summary preview, health inventory, contributor guidance, and a visual overview. Roadmap v3 begins with packaging-path validation in CI so the published `forge` entry point is exercised rather than only source-tree imports.

## Technical debt

The current CI workflow now validates the installed package path, but its first pull-request result from this maintenance branch has not yet been observed. The tool remains intentionally inspection-only: it does not persist run summaries, inspect diffs, execute external commands, alter repository files, call networks, or enforce policy decisions.

## Prioritized roadmap

## Roadmap v3

### AUTO-015 — Verify installed package behavior in CI
Priority: P1
Status: DONE

Goal: Make CI exercise the installed distribution and the `forge` console-script entry point.
Why it matters: Source-tree imports can pass while package metadata or entry-point wiring is broken for real users.
Scope: Install the local package alongside the pinned test runner, invoke `forge --version`, and run tests against the installed package on the existing Python version matrix.
Expected files or areas: `.github/workflows/test.yml`, README, roadmap, state, changelog, decisions.
Acceptance criteria: The workflow installs `.`; the installed `forge --version` command runs before tests; tests no longer rely on `PYTHONPATH=src`; action permissions remain read-only and pinned action revisions remain unchanged.
Validation: Reviewed workflow syntax and package metadata through the GitHub repository API; opened a pull request so the existing workflow can validate Python 3.10, 3.11, and 3.12. Final workflow outcome remains pending at record time.
Risks or assumptions: Dependency installation still requires the GitHub-hosted runner to access PyPI for the pinned `pytest` package; no runtime dependencies are introduced.
Notes: This is CI hardening only. It does not expand the CLI's safety boundary or autonomous behavior.

## Future ideas

- Observe the first AUTO-015 workflow result and record it before selecting another product increment.
- Add deterministic machine-readable output only after defining a stable schema and preserving read-only behavior.
- Consider hash-linked local run reports only after a dedicated persistence design and policy review.

## Do Not Change Without Explicit Human Approval

- Remote and branch settings.
- Repository visibility and access controls.
- Production infrastructure.
- Features that run external commands.
- Features that change repository files outside documented safe paths.
- Credential handling, telemetry, analytics, billing, or deployment behavior.
