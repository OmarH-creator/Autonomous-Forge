import json

from autonomous_forge.commit_status_review import (
    build_commit_status_review_data,
    format_commit_status_review_payload,
)


def _live_payload(**overrides):
    payload = {
        "sha": "abc1234",
        "source": "gh run list",
        "workflow_runs": [
            {
                "name": "CI",
                "status": "completed",
                "conclusion": "success",
                "head_sha": "abc1234",
                "html_url": "https://example.invalid/actions/runs/1",
            }
        ],
        "workflow_run_limit": 20,
        "workflow_run_collection_complete": True,
        "workflow_run_commit_binding_complete": True,
    }
    payload.update(overrides)
    return payload


def test_live_collection_guarantees_survive_status_review_boundary():
    review = build_commit_status_review_data(_live_payload())

    assert review["review_status"] == "clear"
    assert review["requires_attention"] is False
    assert review["live_collection_evidence"] == {
        "source": "gh run list",
        "requested_commit": "abc1234",
        "workflow_run_limit": 20,
        "collection_complete": True,
        "commit_binding_complete": True,
    }


def test_live_status_review_blocks_when_collection_completeness_proof_is_missing():
    review = build_commit_status_review_data(
        _live_payload(workflow_run_collection_complete=False)
    )

    assert review["review_status"] == "blocked"
    assert review["requires_attention"] is True
    assert "live workflow status evidence does not prove bounded collection completeness" in review["review_blockers"]


def test_live_status_review_blocks_when_commit_binding_proof_is_missing():
    review = build_commit_status_review_data(
        _live_payload(workflow_run_commit_binding_complete=False)
    )

    assert review["review_status"] == "blocked"
    assert review["requires_attention"] is True
    assert "live workflow status evidence does not prove per-run commit binding" in review["review_blockers"]


def test_live_status_review_blocks_invalid_collection_limit():
    review = build_commit_status_review_data(_live_payload(workflow_run_limit=21))

    assert review["review_status"] == "blocked"
    assert "live workflow status evidence lacks a valid bounded collection limit" in review["review_blockers"]


def test_supplied_non_live_status_evidence_remains_backward_compatible():
    review = build_commit_status_review_data(
        {
            "sha": "abc1234",
            "statuses": [{"context": "ci/test", "state": "success"}],
        }
    )

    assert review["review_status"] == "clear"
    assert review["live_collection_evidence"] is None


def test_live_collection_guarantees_are_exposed_in_json_and_text_output():
    json_data = json.loads(format_commit_status_review_payload(_live_payload(), output_format="json"))
    text = format_commit_status_review_payload(_live_payload(), output_format="text")

    assert json_data["live_collection_evidence"]["collection_complete"] is True
    assert json_data["live_collection_evidence"]["commit_binding_complete"] is True
    assert "Live collection evidence:" in text
    assert "collection complete: true" in text
    assert "commit binding complete: true" in text
