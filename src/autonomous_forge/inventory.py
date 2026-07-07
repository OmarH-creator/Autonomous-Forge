"""Build read-only repository health inventory summaries."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


_INVENTORY_PATHS = (
    ".ai/AUTONOMOUS_PLAN.md",
    ".ai/AUTONOMOUS_STATE.md",
    ".ai/AUTONOMOUS_CHANGELOG.md",
    ".ai/DECISIONS.md",
    ".forge/policy.md",
    ".github/workflows/test.yml",
    "README.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "pyproject.toml",
    "src/",
    "tests/",
    "docs/",
)


@dataclass(frozen=True)
class InventorySignal:
    """A read-only file-presence signal for repository maintenance readiness."""

    path: str
    present: bool


def _path_matches_expected_type(root: Path, path: str) -> bool:
    """Return whether a required inventory path exists as the documented path type."""
    candidate = root / path
    if path.endswith("/"):
        return candidate.is_dir()
    return candidate.is_file()


def collect_inventory_signals(
    root: Path = Path("."),
    required_paths: tuple[str, ...] = _INVENTORY_PATHS,
) -> list[InventorySignal]:
    """Return deterministic typed file-presence signals without reading file contents."""
    return [
        InventorySignal(path=path, present=_path_matches_expected_type(root, path))
        for path in required_paths
    ]


def build_repository_inventory(root: Path = Path(".")) -> str:
    """Return a conservative repository health inventory without changing files."""
    signals = collect_inventory_signals(root)
    lines = [
        "Repository health inventory",
        "Mode: read-only",
        "Scope: typed file-presence signals only",
    ]
    lines.extend(
        f"{signal.path}: {'present' if signal.present else 'missing'}"
        for signal in signals
    )
    lines.extend(
        [
            "Health score: not calculated",
            (
                "Notes: Inventory does not enforce policy, perform credential scanning, read "
                "environment variables, call networks, or run external commands."
            ),
        ]
    )
    return "\n".join(lines)
