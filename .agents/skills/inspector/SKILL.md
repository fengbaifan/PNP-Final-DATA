---
name: inspector
kind: leaf
phase: support
triggers:
  - inspector
  - 系统审阅
  - 编码检查
  - 内容检查
description: 统一负责内容、来源覆盖、编码、证据状态、规则和系统结构的定向检查。吸收原 read-full、encoding-check、audit-confidence 与 system-review；不构成额外生产阶段。
---

# inspector

统一负责内容、来源覆盖、编码、证据状态、规则和系统结构的定向检查。吸收原 read-full、encoding-check、audit-confidence 与 system-review；不构成额外生产阶段。

## 执行

先明确问题和范围，直接阅读相关文件。语义质量需实质审阅；统计、文件存在、结构分数不能代替事实与关系判断。
编码问题先检查原始字节和显式解码，区分文件损坏与终端显示；没有证据不改文件。来源本体仍只追加。
证据检查区分 source_backed、外部身份锚点、语义支持和独立多来源；不以数量或分数宣布 confirmed。
系统检查核对 AGENTS.md、pipeline、唯一 Skill 根、阶段边界及过程/结果位置。不假定任何客户端 Hook 已生效。

## 工具与结果

按问题选择 scripts/audit_content_quality.py、scripts/audit_repo.py、scripts/audit_rule_drift.py 或处理包校验。禁止默认把所有脚本跑一遍当语义审查。
结果说明已完成、仅机械通过、待证、受阻和暂不开展。初期 hierarchy 缺口保留可见状态，但不列成要求立即开展知识发现的任务。
知识审阅过程与结果写入 04-knowledge 对应过程/结果文件；系统审阅写入现有升级日志的过程部分。具体修复在已有授权内进行，规则改造交给 system-upgrade。
