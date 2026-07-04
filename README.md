# ttr

`ttr` is a small terminal translator for personal developer workflows.

It reads text from arguments, stdin, or the clipboard, writes translated text to stdout, and keeps diagnostics on stderr.

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
ttr --backend libre en:zh "hello"
ttr --json en:zh "hello"
```

Language specs are predictable and never use language detection:

```text
en:zh     English -> Chinese
:zh       configured source -> Chinese
zh:       Chinese -> configured target
(no spec) configured source -> configured target
```

If a partial language spec is missing a configured value, `ttr` exits with a clear error.

## Install

```bash
uv sync
uv run ttr en:zh "hello"

uv tool install .
ttr en:zh "hello"
```

## Backends

- `mymemory`: default zero-key online backend using MyMemory.
- `deepl`: DeepL API, requires an API key.
- `libre`: local LibreTranslate service, explicit only.

There is no `auto` backend. The default is just the configured `backend`, which is `mymemory` unless changed.

Normal online translations always call the selected backend. On success, `ttr` writes the result to the local cache by default. It does not read cache during online translation, so stale cache entries cannot skip a backend request. Cache entries are backend-specific.

## Offline

Offline mode never calls a translation backend:

```text
cache -> glossary
```

`ttr --offline` reads the local cache, then checks the glossary. If neither has a match, it exits with an offline miss error.

Optional glossary path:

- Windows: `%APPDATA%\ttr\glossary.tsv`
- macOS/Linux: `~/.config/ttr/glossary.tsv`

Format:

```tsv
en	zh	repository	仓库
en	zh	cache	缓存
```

## MyMemory Limit

MyMemory requests are capped at 480 UTF-8 bytes. If the input is longer, `ttr` exits with an error instead of splitting it automatically. Split long text yourself or choose another backend.

## Local LibreTranslate

Install and start a local service:

```bash
uv tool install libretranslate
libretranslate --load-only en,zh --disable-web-ui
```

Then use:

```bash
ttr --backend libre en:zh "hello"
```

The default URL is `http://127.0.0.1:5000`.

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

[libre]
url = "http://127.0.0.1:5000"

[cache]
enabled = true
```

Environment variables override config:

```text
TTR_SOURCE_LANG
TTR_TARGET_LANG
TTR_BACKEND
TTR_MYMEMORY_EMAIL
TTR_DEEPL_API_KEY
TTR_DEEPL_URL
TTR_LIBRE_URL
TTR_CACHE=0
```


