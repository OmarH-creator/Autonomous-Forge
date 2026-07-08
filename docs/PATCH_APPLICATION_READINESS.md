# Patch Application Readiness Summary

`forge patch-application-readiness` is a read-only checkpoint after `forge patch-application-preflight` and `forge patch-application-audit`.

It combines two supplied JSON evidence files:

1. a ready patch-application preflight payload; and
2. a clear patch-application provenance audit payload.

The command confirms that both evidence files are read-only, objectives match, reviewed paths match, validation steps match, no preflight or audit blockers remain, and both upstream stages keep `patch_application_allowed` set to `false`.

```bash
forge patch-application-readiness \
  --root . \
  --preflight patch-application-preflight.json \
  --audit patch-application-audit.json \
  --require-ready \
  --format json
```

Compatibility route:

```bash
forge-patch-application-readiness \
  --root . \
  --preflight patch-application-preflight.json \
  --audit patch-application-audit.json \
  --require-ready \
  --format json
```

## Safety boundary

Patch-application readiness reads supplied preflight and audit JSON only. It does not read target file contents, inspect git diffs, generate patch text, apply patches, run commands, check workflow status, mutate saved history, commit, push, or change files. `patch_application_allowed` is always `false`.

A `ready` result is only advisory. It means the supplied preflight and audit evidence agree; it does not approve a patch, prove correctness, or permit repository mutation.
