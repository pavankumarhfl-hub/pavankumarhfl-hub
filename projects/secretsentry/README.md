# SecretSentry

A privacy-first defensive scanner that detects common accidental secrets in source trees without printing their values.

## Why

Leaked credentials often enter repositories through configuration files, copied snippets, or debug code. SecretSentry provides a small deterministic check suitable for local development and CI.

## Features

- AWS access-key pattern detection
- GitHub token pattern detection
- Private-key header detection
- Generic API key/password/token assignment detection
- Skips common dependency/cache directories
- Never prints matched secret values
- Human-readable and JSON output
- Non-zero exit code when findings exist

## Run

```bash
PYTHONPATH=src python src/secretsentry.py .
PYTHONPATH=src python src/secretsentry.py . --json
```

## Scope

This is a defensive pattern scanner, not a guarantee that a repository contains no secrets. Real deployments should combine it with secret-management controls and provider-side credential rotation.

## License

MIT
