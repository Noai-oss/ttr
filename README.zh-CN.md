# ttr

[English](README.md) | [简体中文](README.zh-CN.md)

`ttr` 是一个小型终端翻译工具，从命令行参数、标准输入或剪贴板读取文本，将译文写入标准输出，将错误和警告写入标准错误。

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

默认语言方向是 `en:zh`，省略的语言从配置取得，如上例所示。不支持自动检测语言（`auto`）。配置中的语言为空时视为未设置；缺少必需的语言时，命令会报错。

原语言和目标语言相同时，`ttr` 直接返回原文，不读取缓存或词表，也不调用翻译后端。

`--lines` 独立翻译每个非空行，保留译文之间的空行。配合 `--json` 时，如果所有行的结果来源相同，`backend` 显示该来源；来源不同时显示 `mixed`。只有所有非空行都来自缓存，`cached` 才为 `true`。空行不影响这两个字段。

## 安装

发行包名为 `ttr-cli`，命令名为 `ttr`。

通过 PyPI 安装（首次发布后可用）：

```bash
uv tool install ttr-cli
```

从本地源码安装：

```bash
# 在源码目录运行
uv sync
uv run ttr en:zh "hello"

# 安装为独立命令
uv tool install .
ttr en:zh "hello"
```

开发检查、构建和版本管理说明见[贡献指南](CONTRIBUTING.zh-CN.md)。

## 翻译后端

- `mymemory`：默认后端，无需 API 密钥。每次请求的输入最多 500 个 UTF-8 字节，超长报错，不自动拆分。
- `deepl`：使用 DeepL API，需要配置 API 密钥。

不支持自动选择后端。服务额度和官方参考链接见[服务限制](docs/limit.zh-CN.md)。

在线翻译调用选定的后端，默认将成功结果按后端分别写入缓存，不读取已有缓存。缓存写入失败时，仍然输出译文并成功退出，同时向标准错误输出警告。

## 离线模式

`--offline` 不调用翻译后端，先查询缓存，仅在未命中时读取词表，按整段输入精确匹配。两处都未命中或缓存读取失败时，命令会报错。

可选词表 `glossary.tsv` 与 `config.toml` 放在同一目录（见[配置](#配置)）。每行包含四个非空字段，以 Tab 分隔，依次为原语言、目标语言、原文和译文。空行和 `#` 注释会被忽略；格式错误会报告文件路径和行号。

```tsv
en	zh	repository	仓库
en	zh	cache	缓存
```

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

环境变量覆盖配置文件中的对应值；`--backend` 的优先级高于两者。

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
