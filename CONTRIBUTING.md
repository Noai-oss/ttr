# Contributing

[English](CONTRIBUTING.md) | [简体中文](CONTRIBUTING.zh-CN.md)

## Development checks

Local development and all CI jobs use the default Python version from [.python-version](.python-version), which uv reads automatically. The supported version range is defined by `requires-python` in [pyproject.toml](pyproject.toml).

Install development dependencies, run checks, and build the source distribution and wheel:

```bash
uv sync --locked
uv run --no-sync python -m unittest discover -s tests -v
uv run --no-sync ruff check src tests
uv run --no-sync ruff format --check src tests
uv build
```

[GitHub Actions](.github/workflows/ci.yml) runs tests on Linux, Windows, and macOS for pull requests to `main` and pushes to `main`. It also checks lint, formatting, and installation of the built wheel. Tests do not require translation API keys.

## Versioning

Versions are derived from Git tags with `uv-dynamic-versioning`. A tag such as `v0.1.0` produces version `0.1.0`; commits after a version tag produce development versions of the next patch release. Before the first version tag, versions are derived from `0.0.0`.

Run `uv sync --locked` before running the source code or tests, and again after switching commits or adding version tags. It generates `src/ttr/_version.py`, which is included in distributions and ignored by Git. The CLI and package metadata use the same generated version; do not edit the generated file manually.
