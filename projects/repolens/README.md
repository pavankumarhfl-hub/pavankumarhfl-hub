# RepoLens

A zero-dependency Python CLI that checks a Git repository for high-signal engineering hygiene practices and produces a simple readiness score.

## Why it exists

A repository can contain working code and still be difficult to review, reuse, or maintain. RepoLens turns common quality signals into a fast, repeatable checklist.

## Checks

- README/documentation
- License
- `.gitignore`
- Safe environment template (`.env.example` or `.env.sample`)
- Test directory
- GitHub Actions CI workflow

## Run

```bash
python projects/repolens/src/repolens.py .
```

Example output:

```text
RepoLens — my-project
========================================
[PASS] README               Documented project
[PASS] License              License present
[MISS] Tests                Test directory present
----------------------------------------
Engineering readiness: 83%
```

## Test

```bash
python -m pytest projects/repolens/tests
```

## Design notes

RepoLens intentionally starts with filesystem-based checks rather than network calls. That keeps it fast, deterministic, privacy-friendly, and usable in CI.

The first version is deliberately small. Future iterations can add language-aware checks, source-control metadata, dependency hygiene, configurable scoring, and richer reports.

## Project quality

- Python standard library only at runtime
- Automated tests with pytest
- GitHub Actions CI
- MIT license
- Contribution and security guidance

## License

MIT
