"""CLI for compact replay policy summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from autonomous_forge.maintenance_replay_policy_summary import (
    build_maintenance_replay_policy_summary_from_bundle,
    format_maintenance_replay_policy_summary,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize replay policy gates for a persisted maintenance evidence bundle.")
    parser.add_argument("--bundle", required=True, type=Path, help="Path to the persisted maintenance evidence bundle JSON.")
    parser.add_argument("--root", default=Path("."), type=Path, help="Repository root used to bound bundle/source-report reads.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    data = build_maintenance_replay_policy_summary_from_bundle(args.bundle, root=args.root)
    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(format_maintenance_replay_policy_summary(data))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
