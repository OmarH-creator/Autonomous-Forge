from autonomous_forge.planner import build_repository_plan_data
from autonomous_forge.proposal import build_change_proposal_data


POLICY = """## Allowed paths
- `src/**`

## Prohibited paths
- `.env`

## Human approval required
- None.

## Validation expectations
- Run pytest.
"""

PLAN = """### AUTO-999 — Preserve hidden paths
Priority: P1
Status: TODO
Goal: Preserve repository path tokens.
Why it matters: Policy review requires exact paths.
Scope: Keep hidden file names intact.
Expected files or areas: `src/example.py`, `.env`.
Acceptance criteria: Planned areas retain the leading period.
Validation: Run pytest.
Risks or assumptions: Output remains read-only.
"""


PLAN_TRAILING_COMMA = """### AUTO-998 — Handle trailing commas in file lists
Priority: P1
Status: TODO
Goal: Preserve tokens when the roadmap uses trailing commas.
Why it matters: Roadmap authors may use Oxford-style trailing commas.
Scope: Keep hidden file names intact.
Expected files or areas: `src/example.py`, `.env`,
Acceptance criteria: Planned areas retain the leading period.
Validation: Run pytest.
Risks or assumptions: Output remains read-only.
"""


def test_change_proposal_preserves_hidden_file_path(tmp_path):
    state = tmp_path / "state.md"
    state.write_text("# State\n", encoding="utf-8")
    plan_data = build_repository_plan_data(PLAN, POLICY, state_path=state, root=tmp_path)

    proposal = build_change_proposal_data(plan_data)

    assert proposal["planned_file_areas"] == ["src/example.py", ".env"]


def test_change_proposal_preserves_hidden_file_path_with_trailing_comma(tmp_path):
    state = tmp_path / "state.md"
    state.write_text("# State\n", encoding="utf-8")
    plan_data = build_repository_plan_data(
        PLAN_TRAILING_COMMA,
        POLICY,
        state_path=state,
        root=tmp_path,
    )

    proposal = build_change_proposal_data(plan_data)

    assert proposal["planned_file_areas"] == ["src/example.py", ".env"]
