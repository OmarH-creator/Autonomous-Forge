# Run-history attachment resource bounds

`forge run-history-read` discovers immutable validation-result sidecars under `.ai/run-history/validation-attachments/` without recursively walking the repository.

AUTO-222 makes that discovery resource-bounded before attachment verification:

- at most **100 direct JSON candidates** are admitted;
- at most **1,000 total direct directory entries** are enumerated;
- each admitted candidate is read through a **1 MiB ceiling** before it can be parsed or selected for verification;
- enumeration is incremental with `os.scandir()`, so Forge does not first materialize and sort an arbitrarily large directory;
- only admitted candidates are sorted for deterministic output.

If any ceiling is exceeded, the read fails closed instead of silently treating a partial directory view as complete.

These limits affect only discovery of immutable validation sidecars. They do not grant validation authority, execute commands, mutate history, or promote externally supplied validation observations into Forge-executed proof.
