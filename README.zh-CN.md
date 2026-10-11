# ttr

[English](README.md) | [简体中文](README.zh-CN.md)

`ttr` 是一个小型终端翻译工具，适合个人开发中的日常翻译。

它从命令行参数、标准输入或剪贴板读取文本，将译文写入标准输出，将错误和警告写入标准错误。

管道输入和重定向输出使用 UTF-8 编码。通过管道连接的程序也应使用相同编码。

## 使用

```bash
ttr en:zh "This function mutates the original object."
ttr zh:en "这个错误应该是缓存过期导致的"
git show -1 --stat | ttr en:zh

ttr "hello"              # 使用配置中的原语言、目标语言和翻译后端
ttr :zh "hello"          # 原语言取配置，目标语言指定为中文
ttr zh: "你好"            # 原语言指定为中文，目标语言取配置

ttr --clip en:zh
ttr --clip --copy zh:en
ttr --offline en:zh "repository"
ttr --backend mymemory en:zh "hello"
ttr --backend deepl en:zh "hello"
ttr --json en:zh "hello"
ttr --lines --json en:zh "hello"
```

语言方向由参数和配置明确指定，不会自动检测：

```text
en:zh     英语 -> 中文
:zh       配置中的原语言 -> 中文
zh:       中文 -> 配置中的目标语言
不指定     配置中的原语言 -> 配置中的目标语言
```

默认语言方向是 `en:zh`。配置中的语言为空时，视为未设置；省略的语言若无法从配置取得，程序会明确报错。语言代码必须明确指定，不支持 `auto`。

原语言和目标语言相同时，`ttr` 直接返回原文，不读取缓存或词表，也不调用翻译后端。

`--lines` 独立翻译每个非空行，保留译文之间的空行。配合 `--json` 时，如果所有行的结果来源相同，`backend` 显示该来源；来源不同时显示 `mixed`。只有所有非空行都来自缓存，`cached` 才为 `true`。空行不影响这两个字段。

## 安装

```bash
uv sync
uv run ttr en:zh "hello"

uv tool install .
ttr en:zh "hello"
```

开发检查、构建和版本管理说明见[贡献指南](CONTRIBUTING.zh-CN.md)。

## 翻译后端

- `mymemory`：默认在线后端，使用 MyMemory，无需 API 密钥。
- `deepl`：使用 DeepL API，需要配置 API 密钥。

不提供 `auto` 后端。默认使用配置中的 `backend`，未修改配置时为 `mymemory`。

正常的在线翻译会调用选定的后端。成功后，`ttr` 默认将结果写入本地缓存。在线翻译不读取缓存，因此旧缓存不会跳过后端请求。不同后端的缓存条目分别保存。

缓存写入失败时，仍然输出译文并成功退出，同时向标准错误输出警告。离线读取缓存失败时会报错，不会自动修复或删除缓存。

## 离线模式

离线模式不会调用翻译后端，查询顺序为：

```text
缓存 -> 词表
```

`ttr --offline` 先查询本地缓存，再查询词表中与整段输入完全匹配的条目。它不会替换句子中的单个词。两处都未命中时，以离线未命中错误退出。使用 `--lines` 时，每个非空行分别匹配。

只有离线查询缓存未命中后才会读取词表。除空行和注释行外，每行必须包含四个非空字段，以 Tab 分隔；格式错误会报告文件路径和行号。

词表文件是可选的，路径为：

- Windows：`%APPDATA%\ttr\glossary.tsv`
- macOS/Linux：`$XDG_CONFIG_HOME/ttr/glossary.tsv` 或 `~/.config/ttr/glossary.tsv`

格式如下，四列依次为原语言、目标语言、原文和译文：

```tsv
en	zh	repository	仓库
en	zh	cache	缓存
```

## MyMemory 输入限制

本工具将每次 MyMemory 请求的输入限制为 500 个 UTF-8 字节，注意是字节而不是字符。超出时直接报错，不会自动拆分。请自行拆分长文本，或选择其他后端。

## 配置

配置文件是可选的，路径为：

- Windows：`%APPDATA%\ttr\config.toml`
- macOS/Linux：`$XDG_CONFIG_HOME/ttr/config.toml` 或 `~/.config/ttr/config.toml`

示例：

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

环境变量覆盖配置文件中的对应值；`--backend` 的优先级高于两者。字段类型错误或无法识别的布尔值都会报错。

```text
TTR_SOURCE_LANG
TTR_TARGET_LANG
TTR_BACKEND
TTR_MYMEMORY_EMAIL
TTR_DEEPL_API_KEY
TTR_DEEPL_URL
TTR_CACHE=0
```

`TTR_CACHE` 支持 `1/0`、`true/false`、`yes/no`、`on/off`，不区分大小写。TOML 中的 `cache.enabled` 必须使用布尔值 `true` 或 `false`。
