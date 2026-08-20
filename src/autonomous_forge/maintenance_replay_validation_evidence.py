"""Bind immutable external validation observations into maintenance replay summaries."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_evidence_bundle import MaintenanceEvidenceBundleError
from autonomous_forge.maintenance_replay_summary import (
    build_maintenance_replay_summary_data,
    format_maintenance_replay_summary,
)
from autonomous_forge.run_history_reader import RunHistoryReadError, read_run_history_record

_MAX_ATTACHMENT_BYTES = 1_000_000


def _clean_text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _validate_context_association(context: Any, evidence: dict[str, Any], *, label: str) -> str:
    """Refuse supplied retained context when it contradicts maintenance evidence."""
    if context in (None, {}):
        return "context_not_provided"
    if not isinstance(context, dict):
        raise MaintenanceEvidenceBundleError(f"{label} validation_context must be an object")

    retained_steps = context.get("validation_steps")
    if retained_steps is not None:
        if not isinstance(retained_steps, list):
            raise MaintenanceEvidenceBundleError(f"{label} validation_steps context must be a list")
        cleaned_steps = [_clean_text(item) for item in retained_steps if _clean_text(item)]
        if cleaned_steps != evidence.get("validation_steps", []):
            raise MaintenanceEvidenceBundleError(
                f"{label} validation_steps do not match maintenance bundle validation steps"
            )

    expected_changes = context.get("expected_file_changes")
    if expected_changes is not None:
        if not isinstance(expected_changes, list):
            raise MaintenanceEvidenceBundleError(f"{label} expected_file_changes context must be a list")
        cleaned_changes = [_clean_text(item) for item in expected_changes if _clean_text(item)]
        for path in evidence.get("reviewed_paths", []):
            if cleaned_changes and not any(path in change for change in cleaned_changes):
                raise MaintenanceEvidenceBundleError(
                    f"{label} expected_file_changes do not cover reviewed path: {path}"
                )
    return "consistent"


def _attachment_fingerprint(root: Path, label: str) -> tuple[str, int]:
    resolved_root = root.resolve()
    requested = resolved_root / label
    if requested.is_symlink():
        raise MaintenanceEvidenceBundleError("validation attachment path must not be a symlink")
    candidate = requested.resolve()
    try:
        candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise MaintenanceEvidenceBundleError("validation attachment path escaped repository root") from exc
    if not candidate.is_file():
        raise MaintenanceEvidenceBundleError("validation attachment path must be a regular file")
    size = candidate.stat().st_size
    if size > _MAX_ATTACHMENT_BYTES:
        raise MaintenanceEvidenceBundleError(
            f"validation attachment exceeds {_MAX_ATTACHMENT_BYTES} byte replay provenance limit"
        )
    raw = candidate.read_bytes()
    return hashlib.sha256(raw).hexdigest(), len(raw)


def collect_external_validation_evidence(
    maintenance_evidence: dict[str, Any],
    *,
    validation_record_path: Path,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Return verified advisory validation provenance for replay or durable bundles.

    This collector intentionally never changes bundle/replay readiness. Immutable
    attachments prove that external observations are bound to exact run-history
    bytes; they are not evidence that Forge executed a validation command.
    """
    try:
        record = json.loads(
            read_run_history_record(
                validation_record_path,
                root=root,
                output_format="json",
            )
        )
    except (RunHistoryReadError, json.JSONDecodeError) as exc:
        raise MaintenanceEvidenceBundleError(f"validation record could not be verified: {exc}") from exc

    association_statuses = [
        _validate_context_association(
            record.get("validation_context"), maintenance_evidence, label="validation record"
        )
    ]
    attachments: list[dict[str, Any]] = []
    for item in record.get("validation_attachments", []):
        if not isinstance(item, dict):
            raise MaintenanceEvidenceBundleError("validation attachment summary must be an object")
        label = _clean_text(item.get("path"))
        if not label:
            raise MaintenanceEvidenceBundleError("validation attachment summary lacks path")
        attachment_sha256, attachment_bytes = _attachment_fingerprint(root, label)
        association_statuses.append(
            _validate_context_association(
                item.get("validation_context"),
                maintenance_evidence,
                label=f"validation attachment {label}",
            )
        )
        attachments.append(
            {
                "path": label,
                "sha256": attachment_sha256,
                "bytes": attachment_bytes,
                "source_sha256": item.get("source_sha256"),
                "source_bytes": item.get("source_bytes"),
                "validation_execution": item.get("validation_execution", "unknown"),
                "validation_result": item.get("validation_result", "unknown"),
                "validation_note": item.get("validation_note"),
                "validation_context": item.get("validation_context", {}),
                "provenance_type": "externally_supplied_validation_observation",
                "executor_validation_equivalent": False,
            }
        )

    association_status = (
        "consistent" if "consistent" in association_statuses else "context_not_provided"
    )
    return {
        "source_record": record.get("source_path"),
        "association_status": association_status,
        "attachment_count": len(attachments),
        "attachments": attachments,
        "provenance_semantics": "externally_supplied_observation",
        "executor_validation_equivalent": False,
        "replay_gate_effect": "advisory_only",
        "bundle_gate_effect": "advisory_only",
    }


def build_maintenance_replay_with_validation_evidence_data(
    bundle_path: Path,
    *,
    validation_record_path: Path | None = None,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Build replay data plus optional verified external validation provenance."""
    replay = build_maintenance_replay_summary_data(bundle_path, root=root)
    replay["external_validation_evidence"] = {
        "source_record": None,
        "association_status": "not_requested",
        "attachment_count": 0,
        "attachments": [],
        "provenance_semantics": "none",
        "executor_validation_equivalent": False,
        "replay_gate_effect": "none",
        "bundle_gate_effect": "none",
    }
    replay["summary"]["external_validation_attachments"] = 0
    if validation_record_path is None:
        return replay

    evidence = collect_external_validation_evidence(
        replay,
        validation_record_path=validation_record_path,
        root=root,
    )
    replay["external_validation_evidence"] = evidence
    replay["summary"]["external_validation_attachments"] = evidence["attachment_count"]
    replay["replay_policy"]["gates"].append(
        {
            "name": "external_validation_observations",
            "status": "advisory",
            "severity": "advisory",
            "reason": (
                f"{evidence['attachment_count']} immutable external validation attachment(s) verified against the supplied "
                "run-history record; these observations do not replace executor-produced validation proof"
            ),
        }
    )
    replay["replay_policy"]["advisory"] += 1
    replay["summary"]["replay_policy_advisory"] = replay["replay_policy"]["advisory"]
    return replay


def format_maintenance_replay_with_validation_evidence(data: dict[str, Any]) -> str:
    """Format replay output while preserving the existing summary contract."""
    output = format_maintenance_replay_summary(data)
    evidence = data.get("external_validation_evidence")
    if not isinstance(evidence, dict) or evidence.get("source_record") is None:
        return output

    lines = [
        output,
        "External immutable validation observations:",
        f"- Source record: {evidence['source_record']}",
        f"- Association status: {evidence['association_status']}",
        f"- Attachments: {evidence['attachment_count']}",
        f"- Provenance semantics: {evidence['provenance_semantics']}",
        "- Executor validation equivalent: false",
        f"- Replay gate effect: {evidence['replay_gate_effect']}",
    ]
    for item in evidence["attachments"]:
        lines.append(
            f"- {item['path']}: {item['validation_result']} ({item['validation_execution']}), "
            f"sha256={item['sha256']}"
        )
    return "\n".join(lines)