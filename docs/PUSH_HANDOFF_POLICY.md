# Push handoff policy review

`autonomous_forge.push_handoff_policy.review_push_handoff_policy` is a reusable local policy review for the final push-capable boundary.

It checks supplied `forge push-readiness --format json` evidence before a push handoff is allowed to execute:

- the reported branch and protected branch must match the requested push branch;
- branch protection status must be `clear`;
- strict/up-to-date required status checks must be present;
- at least one required status context must exist;
- every required context must have been observed;
- no required contexts may be missing.

The function performs no git calls, network calls, pushes, remote mutation, branch-protection mutation, staging, commits, shell execution, or environment reads. It is designed to be integrated into `forge push-handoff` so branch-protection-aware push-readiness cannot be dropped at the final confirmed push boundary.
