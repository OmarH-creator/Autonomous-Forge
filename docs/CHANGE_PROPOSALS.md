# Change Proposals

`forge propose` is the read-only bridge between a selected roadmap task and future implementation behavior.

It consumes the same roadmap and policy inputs as `forge plan`, then prints a reviewable proposal for the next eligible task. The output is intentionally conservative: it describes intended file areas, high-level operations, validation steps, approval-required policy items, risk notes, and blockers.

## Command

```bash
forge propose \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root .
```

## Output contract

Successful output starts with:

```text
Autonomous Forge change proposal
Mode: read-only
Source: forge plan structured data
Selected task: AUTO-### [P#/TODO] <title>
Reason: highest-priority eligible TODO task; ties preserve roadmap source order.
Goal: <roadmap goal>
```

The proposal then includes these sections:

```text
Planned file areas:
- <area from roadmap expected files>
Planned operations:
- Review and update <area> if needed for the selected task.
Validation steps:
- <policy validation expectation>
Task validation: <roadmap validation>
Policy allowed paths:
- <path>
Policy prohibited paths:
- <path>
Approval-required items:
- <approval item>
Risk notes:
- <roadmap risk>
Blocked items:
- none
Safety boundary: Proposal output only; no files are changed, commands are run, patches are generated, approvals are granted, or policy decisions are enforced.
```

If no eligible TODO task exists, the command reports `Selected task: none` and lists the missing task as a blocker.

## Safety limits

`forge propose` does not:

- create, edit, delete, commit, or push files;
- write a proposal artifact to disk;
- generate patches or inspect diffs;
- run validation commands;
- approve policy exceptions;
- enforce allowed or prohibited paths;
- call networks, read environment variables, scan credentials, or execute external commands.

The command is intentionally a review surface only. Future implementation work should add structured proposal output or validation orchestration before any write or execution behavior is considered.
