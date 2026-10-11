# ttr

[English](README.md) | [简体中文](README.zh-CN.md)

`ttr` is a small terminal translator. It reads text from arguments, stdin, or the clipboard, writes translations to stdout, and keeps diagnostics on stderr.

Piped input and redirected output use UTF-8. Programs connected through a pipe should use the same encoding.

## Usage

```bash
ttr en:zh "This function mutates the original object."
ttr zh:en "这个错误应该是缓存过期导致的"
git show -1 --stat | ttr en:zh

ttr "hello"              # uses configured source/target/backend
ttr :zh "hello"          # source from config, target from CLI
ttr zh: "你好"            # source from CLI, target from config

ttr --clip en:zh
ttr --clip --copy zh:en
ttr --offline en:zh "repository"
ttr --backend mymemory en:zh "hello"
ttr --backend deepl en:zh "hello"
ttr --json en:zh "hello"
ttr --lines --json en:zh "hello"
```

The default language pair is `en:zh`; omitted languages come from configuration, as shown above. Language detection (`auto`) is not supported. Empty configured languages count as unset; if a required language is missing, the command fails.

When the source and target languages are the same, `ttr` returns the input unchanged without reading the cache or glossary or calling a backend.

`--lines` translates each nonempty line independently and keeps blank lines between translated lines. With `--json`, `backend` names the backend used by all translated lines, or `mixed` when they differ. `cached` is true only when every nonempty line came from cache. Blank lines do not affect either field.

## Install

The distribution is named `ttr-cli`; the command is `ttr`.

From PyPI (available after the first release):

```bash
uv tool install ttr-cli
```

From a local checkout:

```bash
# Run from this checkout
uv sync
uv run ttr en:zh "hello"

# Install as a standalone command
uv tool install .
ttr en:zh "hello"
```

For development checks, builds, and versioning, see [Contributing](CONTRIBUTING.md).

## Backends

- `mymemory`: default backend, requires no API key. Input is limited to 500 UTF-8 bytes per request; longer input is rejected without automatic splitting.
- `deepl`: DeepL API, requires an API key.

Automatic backend selection is not supported. For service quotas and official references, see [Service limits](docs/limit.md).

Online translations call the selected backend and, by default, cache successful results separately for each backend. They never read cached results. Cache write failures produce a warning on stderr while still returning the translation successfully.

## Offline

`--offline` never calls a backend. It checks the cache first and only reads the glossary on a cache miss, matching the entire input exactly. A miss in both sources or a cache read error causes the command to fail.

Place the optional `glossary.tsv` beside `config.toml` (see [Configuration](#configuration)). Each entry has four nonempty tab-separated fields: source language, target language, original text, and translation. Blank lines and `#` comments are ignored; malformed rows report the file and line number.

```tsv
en	zh	repository	仓库
en	zh	cache	缓存
```

## Configuration

Optional config file:

- Windows: `%APPDATA%\ttr\config.toml`
- macOS/Linux: `$XDG_CONFIG_HOME/ttr/config.toml` or `~/.config/ttr/config.toml`

Example:

```toml
source = "en"
target = "zh"
backend = "mymemory"

[mymemory]
email = "you@example.com"

[deepl]
api_key = ""
# url = "https://api-free.deepl.com/v2/translate"

[cache]
enabled = true
```

Environment variables override config; `--backend` overrides both.

```text
TTR_SOURCE_LANG
TTR_TARGET_LANG
TTR_BACKEND
TTR_MYMEMORY_EMAIL
TTR_DEEPL_API_KEY
TTR_DEEPL_URL
TTR_CACHE=0
```

`TTR_CACHE` accepts `1/0`, `true/false`, `yes/no`, or `on/off` (case-insensitive). In TOML, `cache.enabled` must be a boolean.
