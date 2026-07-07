import pytest

from autonomous_forge.plan import PlanParseError, parse_plan_tasks


VALID_PLAN = """# Roadmap

### AUTO-001 — First task
Priority: P1
Status: TODO

Goal: Do one thing.

### AUTO-002 — Done task
Priority: P2
Status: DONE
"""


def test_parse_valid_task_blocks():
    tasks = parse_plan_tasks(VALID_PLAN)

    assert [task.task_id for task in tasks] == ["AUTO-001", "AUTO-002"]
    assert tasks[0].title == "First task"
    assert tasks[0].priority == "P1"
    assert tasks[0].status == "TODO"


def test_parse_empty_plan_returns_no_tasks():
    assert parse_plan_tasks("# Empty roadmap\n") == []


def test_malformed_task_reports_missing_field():
    with pytest.raises(PlanParseError, match="AUTO-009.*Status"):
        parse_plan_tasks(
            """### AUTO-009 — Missing status
Priority: P1
"""
        )
