from autonomous_forge.report import build_repository_report


def test_build_repository_report_counts_task_states():
    report = build_repository_report(
        """### AUTO-010 — Todo task
Priority: P2
Status: TODO

### AUTO-011 — Done task
Priority: P1
Status: DONE

### AUTO-012 — Blocked task
Priority: P0
Status: BLOCKED

### AUTO-013 — Skipped task
Priority: P3
Status: SKIPPED
""",
        state_text="# State\n",
    )

    assert "Plan tasks: 4" in report
    assert "TODO tasks: 1" in report
    assert "DONE tasks: 1" in report
    assert "BLOCKED tasks: 1" in report
    assert "SKIPPED tasks: 1" in report
    assert "Next eligible task: AUTO-010 [P2/TODO] Todo task" in report
    assert "State file: present" in report


def test_build_repository_report_handles_missing_state_file():
    report = build_repository_report(
        """### AUTO-010 — Todo task
Priority: P2
Status: TODO
"""
    )

    assert "State file: missing" in report
