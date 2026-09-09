---
name: ingest
kind: leaf
phase: current
triggers:
  - ingest
  - 摄入来源
  - 语义处理
  - 知识元成稿
description: 负责第一部分的摄入、处理、知识元三个阶段，逐阶段保存过程与结果。不得自动接续知识发现。
---

# ingest

负责第一部分的摄入、处理、知识元三个阶段，逐阶段保存过程与结果。不得自动接续知识发现。

## 输入与阶段边界

输入为明确的来源、版本和本次范围，先读取 AGENTS.md 与 pipeline 的交接边界。不把三个阶段合并成一个 completed。

### 1 摄入

先读取 01-domain 的领域范围、类型与命名约束，再核对来源本体、版本、语言、章节及范围，来源只追加。登记来源定位、缺失材料、source_assets 指纹和 processing_scope。过程与阶段结果分别保存于 03-processing/<id>/process/stages.md 和同包 results/stages.md 的阶段 1；02-sources/source-registry.md 保存当前来源登记。已有来源历史记录保留，不在来源目录新增可迭代的过程文档。

### 2 处理

Agent 完整阅读范围内正文、标题、注释、表格及必要图像，判断跨页论述和语境，记录理解、取舍与不确定性。固定行数切块、关键词脚本不能代替阅读。
保留 compact-v4 的 source-map.jsonl、semantic-units.jsonl、candidate-ledger.jsonl、manifest.json、summary.md 接口；其中 summary 是兼容工件，不复制新的结果报告。来源行跨度并集须覆盖 processing_scope，无未读范围冒充完成。
manifest.fingerprint_mode 使用 text_crlf_to_lf_v1；source_assets 指纹与 processing_scope 范围分开，输入漂移使有效状态重开。
过程写入 03-processing/<id>/process/stages.md；结果写入同包 results/stages.md。历史已接受包不因改规则而重复阅读或改写旧验收。

### 3 知识元

从语义分析判断对象边界、KU 类型与正文内容。每个候选检索已有对象，payload.knowledge_match 记录 novel、existing_target、potential_duplicate、potential_conflict 或 undetermined 及目标引用。不能判明重复/冲突时暂缓对象；没有冲突信号时不运行完整冲突裁决。
只在来源足以支撑时写入知识元；claim 是证据支撑，不建立独立知识发现任务。候选 approved 后才执行具体写回，实际结果记 applied/no_delta/blocked，不以文件创建冒充验收。
过程写入 04-knowledge/process/<id>.md，阶段结果写入 04-knowledge/results/<id>.md，正文仅在 units 下维护当前版本。

## 完成与下一步

明确已读、已分析、已成稿对象及各自证据、未解决项；semantic_acceptance 必须记录 Agent、来源版本、复读边界和遗漏，不由脚本推导。初期 Theme/Topic 不强制补齐。成稿后交给 verify 做对齐，仍受阻的对象留下。
必要时使用 scripts/validate_processing_package.py 校验覆盖、引用和指纹；机械通过不等于语义接受。

## 按需直接参考

- `references/body-template.md`
- `references/citation.md`
- `references/distillation-system-contract.md`
- `references/hierarchy-field.md`
- `references/knowledge-unit-field-contract.md`
- `references/model-semantic-processing.md`
- `references/relation-types.md`
- `references/taxonomy.md`

- `.agents/skills/system-upgrade/references/work-package-contract.md`
