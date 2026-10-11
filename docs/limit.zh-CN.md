# 翻译服务官方限制

[English](limit.md) | [简体中文](limit.zh-CN.md)

整理日期：2026-10-11。服务额度与限制可能调整，以对应官方页面为准。

## MyMemory

以下数值是此前官方公开规则。

| 项目 | 限制 | 官方链接 |
| --- | --- | --- |
| 匿名使用额度 | 5,000 字符/天 | [每日额度说明](https://mymemory.translated.net/doc/usagelimits.php) |
| 提供有效邮箱后的额度 | 请求中通过 `de` 参数提供有效邮箱：50,000 字符/天 | [每日额度说明](https://mymemory.translated.net/doc/usagelimits.php) |
| 单次文本长度 | 待翻译文本最多 500 个 UTF-8 字节，约 166 个常见汉字 | [API 技术规范](https://mymemory.translated.net/doc/spec.php) |

每日额度按字符描述，单次文本长度按字节限制，两者不是同一个单位。

## DeepL

以下内容已按整理日期核对官方文档。

| 项目 | 限制 | 官方链接 |
| --- | --- | --- |
| Developer 免费额度 | 共 100 万字符，一次性额度，不重置；用完需要升级 Growth | [API 套餐说明](https://support.deepl.com/hc/en-us/articles/360021200939-DeepL-API-plans) |
| 旧 API Free 免费额度 | 50 万字符/月，已停止新购 | [API 套餐说明](https://support.deepl.com/hc/en-us/articles/360021200939-DeepL-API-plans) |
| 文本翻译请求大小 | 最多 128 KiB（131,072 字节） | [大小与用量限制](https://developers.deepl.com/docs/resources/usage-limits) |
| 请求头大小 | 最多 16 KiB（16,384 字节） | [大小与用量限制](https://developers.deepl.com/docs/resources/usage-limits) |
| 请求频率 | 没有固定公开的每秒请求数，服务动态限流；请求过快返回 `429` / `529` | [限流与错误说明](https://developers.deepl.com/docs/best-practices/error-handling) |
| 达到用量限制 | 返回 `456`；可能是套餐字符额度、费用控制、密钥用量或词汇表数量达到限制 | [限流与错误说明](https://developers.deepl.com/docs/best-practices/error-handling) |

字符额度按原文的 Unicode 码点数计算，例如普通汉字“深”和英文字母“A”都各算 1 个字符。请求大小则按字节计算。参见[官方计数规则](https://developers.deepl.com/docs/resources/usage-limits)。
