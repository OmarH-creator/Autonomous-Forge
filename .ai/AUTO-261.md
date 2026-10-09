# AUTO-261 — Single-snapshot guarded patch preview and strict CLI gate

## Confirmed user-facing defect

The patch-generation preview accepted readiness JSON through an unbounded read and target/replacement text through a pre-read stat check followed by unbounded text reads. The --require-generated CLI option reopened all inputs after printing its first preview, so a concurrent change could make the displayed preview and exit status disagree.

## Coherent implementation

Read each of the three repository-confined inputs once with a 1,000,001-byte binary sentinel, reject any observed input beyond 1,000,000 bytes, and decode/parse from that snapshot. Derive both output and strict exit code from the same in-memory preview object. Keep the guarded patch applier's independent target revalidation.

## Inspection and branch/PR disposition

Inspected README/docs/examples, source/tests/config/CI, policy and .ai records, recent commits, all eight branches, all nine visible PRs, and open issues. Seven non-main branches are historical; no open PR requires integration. AUTO-259 already shipped with green CI; issue #15 closure was blocked by connector safety checks.

## Tests and acceptance

A local isolated probe passed five bounded-read/gate checks. Repository regression tests cover bounded reads of all three inputs, exact boundary acceptance, oversized refusal, read-time growth, invalid UTF-8, and single-snapshot strict gating. Acceptance requires green Actions install, compile, CLI smoke, plan lint, and pytest on Python 3.10/3.11/3.12 for the exact pushed SHA.

## Safety, limitations, and next step

No new command, network, subprocess, write, commit, push, or workflow authority. Existing flowchart remains accurate; no visual change. Snapshot ingestion does not prove signer identity or prevent later mutation. Continue the same guarded maintenance workflow milestone, prioritizing a fresh CI failure or a proven execution/history defect.
