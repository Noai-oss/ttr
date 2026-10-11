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

[GitHub Actions](.github/workflows/ci.yml) runs for pull requests to `main` and pushes to `main`. It first checks lint, formatting, builds, and installation of the built wheel on Ubuntu. Only after these checks pass do tests run on Linux, Windows, and macOS. Tests do not require translation API keys.

## Versioning

Versions are derived from Git tags with `uv-dynamic-versioning`. A tag such as `v0.0.2` produces version `0.0.2`; commits after a version tag produce development versions of the next patch release. Before the first version tag, versions are derived from `0.0.0`.

Run `uv sync --locked` before running the source code or tests, and again after switching commits or adding version tags. It generates `src/ttr/_version.py`, which is included in distributions and ignored by Git. The CLI and package metadata use the same generated version; do not edit the generated file manually.

## Publishing to PyPI

The PyPI distribution name is `ttr-cli`.

Create a [PyPI API token](https://pypi.org/manage/account/token/) and set it as `UV_PUBLISH_TOKEN` in your shell.

Replace `0.0.2` below with a new release version and use an empty output directory:

```bash
git tag -a v0.0.2 -m "v0.0.2"
uv build --out-dir dist/0.0.2
uv publish dist/0.0.2/*
git push origin v0.0.2
```

[`uv publish`](https://docs.astral.sh/uv/guides/package/#publishing-your-package) uploads the specified files to PyPI. The versioned directory keeps artifacts from older builds out of the upload.
