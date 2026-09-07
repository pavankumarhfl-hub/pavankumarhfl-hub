from pathlib import Path
from secretsentry import scan

def test_detects_and_redacts_secret(tmp_path: Path):
    (tmp_path / "app.py").write_text('API_KEY = "super-secret-value"\n', encoding="utf-8")
    findings = scan(tmp_path)
    assert len(findings) == 1
    assert findings[0].rule == "Generic secret assignment"
    assert findings[0].snippet == "[REDACTED]"

def test_skips_git_and_binary_files(tmp_path: Path):
    git = tmp_path / ".git"
    git.mkdir()
    (git / "config").write_text('token="hidden-secret"', encoding="utf-8")
    (tmp_path / "image.bin").write_bytes(b"\xff\xfe\x00")
    assert scan(tmp_path) == []
