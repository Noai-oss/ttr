# 贡献指南

[English](CONTRIBUTING.md) | [简体中文](CONTRIBUTING.zh-CN.md)

## 开发检查

本地开发和所有 CI 任务统一使用 [.python-version](.python-version) 指定的默认 Python 版本，uv 会自动读取。项目支持的版本范围由 [pyproject.toml](pyproject.toml) 中的 `requires-python` 声明。

安装开发依赖、运行检查，并构建源码分发包和 wheel：

```bash
uv sync --locked
uv run --no-sync python -m unittest discover -s tests -v
uv run --no-sync ruff check src tests
uv run --no-sync ruff format --check src tests
uv build
```

向 `main` 提交 PR 或推送代码时，[GitHub Actions](.github/workflows/ci.yml) 会先在 Ubuntu 上检查代码规范、格式、构建以及 wheel 能否安装运行。全部通过后，才在 Linux、Windows 和 macOS 上运行测试。测试无需翻译 API 密钥。

## 版本管理

版本号由 `uv-dynamic-versioning` 从 Git 标签推导。`v0.1.0` 这样的标签对应版本 `0.1.0`；标签之后的提交生成下一个补丁版本的开发版本。尚无版本标签时，以 `0.0.0` 为基础推导版本。

运行源码或测试前先执行 `uv sync --locked`，切换提交或添加版本标签后也需要重新执行。它会生成 `src/ttr/_version.py`，该文件随分发包发布，但由 Git 忽略。命令行和包元数据使用同一个生成的版本号，请勿手动修改生成文件。
