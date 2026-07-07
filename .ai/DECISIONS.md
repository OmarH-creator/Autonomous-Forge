# Autonomous Decisions

## DEC-002 — 2026-07-07 — Make policy inspection the Roadmap v2 foundation

Context: Roadmap v1 completed the local CLI, deterministic task parsing and selection, dry-run report, policy documentation, and contributor guidance. The repository now has documented policy boundaries but no code that can inspect them.
Decision: Roadmap v2 will begin with conservative, read-only parsing and reporting of `.forge/policy.md` before adding any higher-risk automation or write behavior.
Alternatives considered: Add a repository health scanner first, add external command execution, add GitHub issue import, or implement automatic file writes.
Consequences: Policy inspection strengthens safety and transparency before execution features, but it delays more visible automation features until the tool can explain repository boundaries clearly.
Human decision still required: No.

## DEC-001 — 2026-07-07 — Start with a Python CLI

Context: Roadmap v1 defines Autonomous Forge as a local-first developer tool that needs a stable command surface before planner behavior can be used.
Decision: Use a zero-runtime-dependency Python package with a `forge` console script as the initial implementation surface.
Alternatives considered: Shell-only scripts, a hosted service, or a JavaScript package.
Consequences: Python keeps the MVP small and testable, but packaging and CLI behavior must remain simple until the plan parser exists.
Human decision still required: No.