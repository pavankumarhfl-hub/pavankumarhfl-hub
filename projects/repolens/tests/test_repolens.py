import json
from pathlib import Path

from repolens import main, result, run_checks, score


def make_repo(tmp_path: Path, *paths: str) -> Path:
    for item in paths:
        target = tmp_path / item
        if "." not in target.name:
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("placeholder", encoding="utf-8")
    return tmp_path


def test_all_checks_pass(tmp_path: Path):
    root = make_repo(
        tmp_path,
        "README.md",
        "LICENSE",
        ".gitignore",
        ".env.example",
        "tests",
        ".github/workflows",
    )
    checks = run_checks(root)
    assert all(check.passed for check in checks)
    assert score(checks) == 100


def test_partial_score(tmp_path: Path):
    root = make_repo(tmp_path, "README.md", ".gitignore")
    checks = run_checks(root)
    assert score(checks) == 33
    assert not all(check.passed for check in checks)


def test_result_is_machine_readable(tmp_path: Path):
    root = make_repo(tmp_path, "README.md")
    report = result(root)
    encoded = json.dumps(report)
    decoded = json.loads(encoded)
    assert decoded["score"] == 17
    assert len(decoded["checks"]) == 6


def test_json_cli_output(tmp_path: Path, capsys, monkeypatch):
    root = make_repo(tmp_path, "README.md", ".gitignore")
    monkeypatch.setattr("sys.argv", ["repolens", str(root), "--json"])
    assert main() == 0
    output = capsys.readouterr().out
    report = json.loads(output)
    assert report["repository"] == root.name
    assert report["score"] == 33
