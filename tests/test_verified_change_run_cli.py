from autonomous_forge.cli_entry_patch import main as forge_main
from autonomous_forge.verified_change_run_cli import build_parser


def test_verified_change_run_parser_keeps_side_effect_confirmations_separate():
    args = build_parser().parse_args([
        "--patch-apply", "patch.json",
        "--status-review", "status.json",
        "--summary", "fix: guarded change",
        "--confirm-validation",
    ])
    assert args.confirm_validation is True
    assert args.confirm_commit_create is False


def test_primary_router_exposes_verified_change_run_help(capsys):
    assert forge_main(["verified-change-run", "--help"]) == 0
    assert "validation" in capsys.readouterr().out.lower()
