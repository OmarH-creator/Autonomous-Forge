# Contributing to Autonomous Forge

Autonomous Forge is intentionally small, local-first, and repository-native. Contributions should make autonomous maintenance safer, easier to inspect, or easier to validate.

## Local setup

Use Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
forge --help
```

On Windows PowerShell, activate the virtual environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Run tests

Run the full test suite before proposing or committing a behavior change:

```bash
PYTHONPATH=src python -m pytest
```

When a change is documentation-only, review the affected Markdown files for consistency with the roadmap, README, and policy documentation.

## Task discipline

Keep each contribution focused on one coherent task.

- Prefer the smallest complete change that satisfies the acceptance criteria.
- Do not bundle unrelated refactors, formatting churn, and feature work.
- Update tests when behavior changes.
- Update documentation when user-facing commands, setup, policy, or workflow guidance changes.
- Keep roadmap and state files consistent when work is performed by the autonomous maintenance flow.

## Safe file handling

Before changing files, check the current roadmap and policy boundaries:

- `.ai/AUTONOMOUS_PLAN.md` for task scope and acceptance criteria.
- `.ai/AUTONOMOUS_STATE.md` for current status and blockers.
- `docs/POLICY.md` and `.forge/policy.md` for allowed paths, prohibited paths, approval boundaries, and validation expectations.

Do not commit secrets, credentials, `.env` files, private keys, certificates, personal data, generated caches, virtual environments, or unrelated local artifacts.

## Safety boundaries

Do not add network access, external command execution, deployment behavior, telemetry, repository-permission changes, or sensitive security functionality unless the roadmap and repository policy explicitly allow it.

If a task is ambiguous, unsafe, too large, or impossible to validate, record the blocker instead of guessing.

## Commit messages

For autonomous maintenance commits, use:

```text
auto: [AUTO-###] concise description
```

For human contributions, use a concise conventional-style message such as:

```text
docs: clarify local setup
```
