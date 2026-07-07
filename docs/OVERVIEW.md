# Autonomous Forge overview

Autonomous Forge is a local-first CLI for inspecting a repository's maintenance plan before automation is allowed to act.

```mermaid
flowchart LR
    A[Repository files] --> B[forge]
    B --> C[Roadmap and next task]
    B --> D[Policy readiness]
    B --> E[Run-summary preview]
    B --> F[Health inventory]
    C --> G[Human review]
    D --> G
    E --> G
    F --> G
```

## Current boundary

Every implemented command is read-only. The CLI does not call an AI model, edit source files, run shell commands, create commits, push changes, scan secrets, or access the network.

## First commands to try

```text
forge report
forge tasks --next
forge policy
forge inventory --root .
```

The tool is pre-alpha. It is an inspection layer for safer future AI-assisted maintenance, not an autonomous coding agent.
