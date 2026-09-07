from pathlib import Path

from repolens import run_checks, score


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
