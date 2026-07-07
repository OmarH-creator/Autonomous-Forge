import pytest

from autonomous_forge.plan import (
    PlanParseError,
    PlanSelectionError,
    parse_plan_tasks,
    select_eligible_task,
)


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


def test_select_eligible_task_uses_priority_before_source_order():
    tasks = parse_plan_tasks(
        """### AUTO-001 — Later priority
Priority: P2
Status: TODO

### AUTO-002 — Higher priority
Priority: P1
Status: TODO
"""
    )

    selected = select_eligible_task(tasks)

    assert selected is not None
    assert selected.task_id == "AUTO-002"


def test_select_eligible_task_preserves_source_order_for_same_priority():
    tasks = parse_plan_tasks(
        """### AUTO-001 — First P1
Priority: P1
Status: TODO

### AUTO-002 — Second P1
Priority: P1
Status: TODO
"""
    )

    selected = select_eligible_task(tasks)

    assert selected is not None
    assert selected.task_id == "AUTO-001"


def test_select_eligible_task_excludes_non_todo_tasks():
    tasks = parse_plan_tasks(
        """### AUTO-001 — Done task
Priority: P0
Status: DONE

### AUTO-002 — Todo task
Priority: P3
Status: TODO
"""
    )

    selected = select_eligible_task(tasks)

    assert selected is not None
    assert selected.task_id == "AUTO-002"


def test_select_eligible_task_returns_none_when_no_todo_exists():
    tasks = parse_plan_tasks(
        """### AUTO-001 — Done task
Priority: P1
Status: DONE
"""
    )

    assert select_eligible_task(tasks) is None


def test_select_eligible_task_rejects_unknown_priority():
    tasks = parse_plan_tasks(
        """### AUTO-001 — Unknown priority
Priority: PX
Status: TODO
"""
    )

    with pytest.raises(PlanSelectionError, match="unsupported priority"):
        select_eligible_task(tasks)
