# AUTO-107 — Branch-policy push handoff review

This run added a reusable local branch-policy review for the push-handoff boundary.

## Why

AUTO-106 made `forge push-readiness` branch-protection aware, but the final push-capable boundary still needs an explicit reusable check that those branch-policy fields are present, clear, strict, and aligned with the requested branch before any confirmed push can execute.

## Added

- `src/autonomous_forge/push_handoff_policy.py`
- `tests/test_push_handoff_policy.py`
- `docs/PUSH_HANDOFF_POLICY.md`

## Validation

Scratch syntax compilation passed for the new module. Focused scratch pytest passed 5 tests for clear policy, unclear policy, branch mismatch, missing observed context, and malformed evidence.

## Next

Wire the policy review directly into `forge push-handoff` so a confirmed push cannot run unless this policy review is clear.
