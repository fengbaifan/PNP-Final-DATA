---
name: encoding-check
kind: leaf
triggers:
  - encoding-check
  - 编码检查
description: >
  文件编码审查技能。诊断乱码、UnicodeDecodeError、UnicodeEncodeError、UTF-8 BOM、
  CRLF/LF 和终端显示问题；修复前必须区分文件字节损坏与终端解码错误。
---

# encoding-check v2.0

## 边界

- 默认只读检查；不得因屏幕乱码直接改写文件。
- `02-sources/` 来源本体只追加，编码修复不得借机改写来源语义。
- 批量修复必须列出精确文件、原始编码证据和 dry-run 差异；没有独立通用 writer。
- UTF-8 BOM 可由读取器兼容；是否移除由对应文件契约决定，不把 BOM 本身当作语义错误。

## 诊断顺序

1. 以二进制方式检查 BOM、非法 UTF-8 字节和换行符。
2. 用显式 `encoding="utf-8"` 或 `utf-8-sig` 读取，确认错误是否可复现。
3. 区分文件内容错误、PowerShell/终端输出编码错误和错误的二次转码。
4. 只对已确认的文件制定逐文件修复；无法确认原始编码时标记 `blocked`。

Windows/PowerShell 下可用只读检查：

```powershell
Format-Hex -LiteralPath <path> -Count 4
Get-Content -LiteralPath <path> -Raw -Encoding UTF8 | Out-Null
```

Python 代码必须显式指定编码；中文 JSONL 使用 UTF-8，读取历史 BOM 文件时使用 `utf-8-sig`。

## 验收

- 修复前后文本语义和记录数一致。
- 目标文件可被当前解析器读取。
- `git diff --check` 和对应最近邻测试通过。
- 报告明确区分“文件已修复”“仅终端显示异常”“无法安全判断”。
