import json
import subprocess

from autonomous_forge.commit_trust_review import build_commit_trust_review_data, review_commit_trust_from_report


COMMIT_VERIFY_REPORT = {
    "title": "Autonomous Forge commit verification report",
    "mode": "local git commit verification",
    "verification_status": "verified",
    "expected_commit": "abc1234",
    "inspected_commit": "abc1234",
    "expected_summary": "feat: add commit trust review",
    "inspected_summary": "feat: add commit trust review",
    "expected_paths": ["README.md"],
    "inspected_paths": ["README.md"],
    "missing_paths": [],
    "unexpected_paths": [],
    "commit_verified": True,
    "push_allowed": False,
    "remote_changes_allowed": False,
    "verification_blockers": [],
}


class FakeRunner:
    def __init__(self, *, signature_code="G", signer="Ada", fingerprint="ABCDEF", commit="abc1234"):
        self.commands = []
        self.signature_code = signature_code
        self.signer = signer
        self.fingerprint = fingerprint
        self.commit = commit

    def __call__(self, command, **kwargs):
        self.commands.append(command)
        stdout = f"{self.commit}\0{self.signature_code}\0{self.signer}\0{self.fingerprint}\n"
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")


def test_build_commit_trust_review_blocks_unverified_commit():
    data = build_commit_trust_review_data({**COMMIT_VERIFY_REPORT, "verification_status": "blocked", "commit_verified": False})

    assert data["trust_status"] == "blocked"
    assert data["commit_trusted"] is False
    assert data["push_allowed"] is False
    assert "commit-verify report is not verified" in data["trust_blockers"]


def test_review_commit_trust_accepts_good_signature(tmp_path):
    report = tmp_path / "commit-verify.json"
    report.write_text(json.dumps(COMMIT_VERIFY_REPORT), encoding="utf-8")
    runner = FakeRunner(signature_code="G", signer="Ada Lovelace", fingerprint="ABCDEF123456")

    data = review_commit_trust_from_report(report, root=tmp_path, runner=runner)

    assert data["trust_status"] == "trusted"
    assert data["commit_trusted"] is True
    assert data["signature_code"] == "G"
    assert data["signer"] == "Ada Lovelace"
    assert data["key_fingerprint"] == "ABCDEF123456"
    assert data["push_allowed"] is False
    assert runner.commands[0][3] == "show"
    assert "push" not in " ".join(runner.commands[0])


def test_review_commit_trust_blocks_unsigned_commit(tmp_path):
    report = tmp_path / "commit-verify.json"
    report.write_text(json.dumps(COMMIT_VERIFY_REPORT), encoding="utf-8")

    data = review_commit_trust_from_report(report, root=tmp_path, runner=FakeRunner(signature_code="N", signer="", fingerprint=""))

    assert data["trust_status"] == "blocked"
    assert data["commit_trusted"] is False
    assert data["signature_description"] == "no signature"
    assert any("not trusted enough" in blocker for blocker in data["trust_blockers"])


def test_review_commit_trust_blocks_commit_mismatch(tmp_path):
    report = tmp_path / "commit-verify.json"
    report.write_text(json.dumps(COMMIT_VERIFY_REPORT), encoding="utf-8")

    data = review_commit_trust_from_report(report, root=tmp_path, runner=FakeRunner(commit="def5678"))

    assert data["trust_status"] == "blocked"
    assert "git trust inspection commit does not match commit-verify report" in data["trust_blockers"]


def test_review_commit_trust_blocks_bad_signature_even_with_metadata(tmp_path):
    report = tmp_path / "commit-verify.json"
    report.write_text(json.dumps(COMMIT_VERIFY_REPORT), encoding="utf-8")

    data = review_commit_trust_from_report(report, root=tmp_path, runner=FakeRunner(signature_code="B", signer="Mallory"))

    assert data["trust_status"] == "blocked"
    assert any("bad signature" in blocker for blocker in data["trust_blockers"])
    assert "unsigned or invalid signature status unexpectedly included signer metadata" in data["trust_blockers"]
