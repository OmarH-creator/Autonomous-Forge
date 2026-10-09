# AUTO-259 — Bounded durable maintenance history-link snapshots

## Objective and confirmed defect

Issue #15 identified an integrity defect in `write_maintenance_history_link()`:
`bundle_sha256` came from an unbounded `read_bytes()` while `bundle_bytes`
came from a separate `stat().st_size`. A concurrently changing bundle could
produce a history pointer with inconsistent fingerprints or bypass the
1,000,000-byte input boundary.

## Implemented slice

Read the already-confined bundle once using `open("rb").read(1_000_001)`;
reject more than 1,000,000 observed bytes before publishing; compute both
the digest and size from the admitted snapshot. Preserve existing
confirmation, path containment, no-clobber, and rollback behavior.

Deterministic tests exercise the exact sentinel read, different on-disk versus
opened snapshot, exact boundary acceptance, oversized input refusal, and
growth visible only at the read boundary.

## Inspection and branch disposition

Inspected README/docs/examples, source/test/config/CI inventory, policy,
roadmap/state/changelog/decisions, recent commits, open issues, eight branches,
and all visible PR history. Seven non-main branches remain historical; there
are no open PRs. Older PR work is merged, closed, or superseded; no branch
or PR integration is warranted.

## Validation and safety

An isolated local Python probe passed three bounded-read checks before
repository mutation. The full supported Python 3.10/3.11/3.12 Actions matrix
must be checked on the exact final pushed SHA before claiming completion.
The change adds no network access, subprocess execution, new write authority,
workflow permission, remote change, or branch-protection change.

No visual change is needed: the evidence chain is unchanged; only the
fingerprint's byte-observation integrity boundary is tightened.

## Limitations and next objective

A single bounded snapshot does not make evidence immutable or authenticate
its author. Continue the existing guarded maintenance workflow milestone,
prioritizing any failing CI and then a demonstrable remaining end-to-end
execution/history integrity defect or concrete user-facing workflow gap.
