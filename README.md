# ttr

[English](README.md) | [简体中文](README.zh-CN.md)

`ttr` is a small terminal translator for personal developer workflows.

It reads text from arguments, stdin, or the clipboard, writes translated text to stdout, and keeps diagnostics on stderr.

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

Language specs are predictable and never use language detection:

```text
en:zh     English -> Chinese
:zh       configured source -> Chinese
zh:       Chinese -> configured target
(no spec) configured source -> configured target
```

The default language pair is `en:zh`. An empty configured language is treated as unset; a partial language spec that needs it exits with a clear error. Language codes must be explicit; `auto` is not supported.

When the source and target languages are the same, `ttr` returns the input unchanged without reading the cache or glossary or calling a backend.

`--lines` translates each nonempty line independently and keeps blank lines between translated lines. With `--json`, `backend` names the backend used by all translated lines, or `mixed` when they differ. `cached` is true only when every nonempty line came from cache. Blank lines do not affect either field.

## Install

```bash
uv sync
uv run ttr en:zh "hello"

uv tool install .
ttr en:zh "hello"
```

For development checks, builds, and versioning, see [Contributing](CONTRIBUTING.md).

## Backends

- `mymemory`: default zero-key online backend using MyMemory.
- `deepl`: DeepL API, requires an API key.

There is no `auto` backend. The default is just the configured `backend`, which is `mymemory` unless changed.

Normal online translations always call the selected backend. On success, `ttr` writes the result to the local cache by default. It does not read cache during online translation, so stale cache entries cannot skip a backend request. Cache entries are backend-specific.

If writing the cache fails, the translation is still printed and the command succeeds, with a warning on stderr. Offline cache read errors are reported as errors; the cache is not automatically repaired or deleted.

## Offline

Offline mode never calls a translation backend:

```text
cache -> glossary
```

`ttr --offline` reads the local cache, then checks the glossary for an exact match of the entire input. It does not replace words inside a sentence. If neither has a match, it exits with an offline miss error. With `--lines`, each nonempty line is matched independently.

The glossary is read only after an offline cache miss. Each non-comment row must contain four nonempty tab-separated fields; malformed rows report the file and line number.

Optional glossary path:

- Windows: `%APPDATA%\ttr\glossary.tsv`
- macOS/Linux: `$XDG_CONFIG_HOME/ttr/glossary.tsv` or `~/.config/ttr/glossary.tsv`

Format:

```tsv
en	zh	repository	仓库
en	zh	cache	缓存
```

## MyMemory Limit

MyMemory requests are capped at 500 UTF-8 bytes. If the input is longer, `ttr` exits with an error instead of splitting it automatically. Split long text yourself or choose another backend.

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

Environment variables override config; `--backend` overrides both. Invalid field types and unrecognized boolean values are errors.

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
