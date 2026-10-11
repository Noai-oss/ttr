# Official Translation Service Limits

[English](limit.md) | [简体中文](limit.zh-CN.md)

Compiled on 2026-10-11. Quotas and limits may change; consult the linked official pages for the current rules.

## MyMemory

The figures below reflect previously published official rules.

| Item | Limit | Official reference |
| --- | --- | --- |
| Anonymous usage quota | 5,000 characters per day | [Daily usage limits](https://mymemory.translated.net/doc/usagelimits.php) |
| Quota with a valid email address | 50,000 characters per day when a valid email address is supplied through the `de` request parameter | [Daily usage limits](https://mymemory.translated.net/doc/usagelimits.php) |
| Text length per request | Up to 500 UTF-8 bytes of text, approximately 166 common Chinese characters | [API specifications](https://mymemory.translated.net/doc/spec.php) |

The daily quota is expressed in characters, while the text length per request is limited in bytes. These are different units.

## DeepL

The following limits were checked against the official documentation on the compilation date.

| Item | Limit | Official reference |
| --- | --- | --- |
| Developer free quota | A one-time allowance of 1,000,000 characters that does not reset; upgrade to Growth once it is exhausted | [API plans](https://support.deepl.com/hc/en-us/articles/360021200939-DeepL-API-plans) |
| Legacy API Free quota | 500,000 characters per month; no longer available for new subscriptions | [API plans](https://support.deepl.com/hc/en-us/articles/360021200939-DeepL-API-plans) |
| Text translation request size | Up to 128 KiB (131,072 bytes) | [Usage and limits](https://developers.deepl.com/docs/resources/usage-limits) |
| Header size | Up to 16 KiB (16,384 bytes) | [Usage and limits](https://developers.deepl.com/docs/resources/usage-limits) |
| Request rate | No fixed published requests-per-second limit; the service adjusts its limits dynamically and returns `429` / `529` for too many requests | [Error handling and throttling](https://developers.deepl.com/docs/best-practices/error-handling) |
| Usage limit reached | Returns `456`; possible causes include the plan's character allowance, Cost Control, API key usage limits, or the glossary count limit | [Error handling and throttling](https://developers.deepl.com/docs/best-practices/error-handling) |

Character usage is measured by the number of Unicode code points in the source text. For example, the Chinese character “深” and the Latin letter “A” each count as one character. Request size is measured in bytes. See the [official counting rules](https://developers.deepl.com/docs/resources/usage-limits).
