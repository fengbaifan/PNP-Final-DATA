---
name: ingest
kind: leaf
triggers:
  - ingest
  - 摄入来源
description: >
  Coverage-Proven Semantic Ingest v4.3。Agent 完整阅读新来源，以紧凑 JSONL 证明 source span 覆盖、语义压缩、候选召回与决策；脚本不得替代语义阅读。
  触发词：ingest、scan-sources、新来源摄入。
---

# ingest v4.3

## 目标

把只读来源转化为可追踪的 semantic units 与统一候选，在不制造微步骤和重复文件的前提下保留覆盖证明。

## 五步执行

### 1. Register

- 把来源追加到 `02-sources/<doc-id>/`，记录 citation、hash、语言和原始资产。
- `02-sources/` 不改写、不删除。
- `doc-id` 使用 `YYYY-author-keyword`，网页捕获使用 `web-YYYY-keyword`；仓库文本使用 UTF-8 无 BOM 与 LF，摄入不得为格式统一覆盖原文。
- `manifest.json.fingerprint_mode` 必须为 `text_crlf_to_lf_v1`；`source_assets` 逐文件记录仓库规范化 SHA-256：只将 Git checkout 的 CRLF 规范为 LF，编码、BOM 和其他内容字节保持敏感。任何缺失、算法标识异常或实际内容哈希变化都使有效状态自动转为 `reopened_source_drift`，但不覆盖历史工件。
- `source_assets` 表示参与来源版本指纹的资产；`processing_scope.assets` 表示本包实际接受语义验收的资产。二者不得混写，补审包允许 scope 是 source assets 的真子集。

### 2. Read and map

- Agent 逐段阅读正文、标题、图注、表格、脚注、参考文献和必要图片。
- 每个 source block 写入 `source-map.jsonl`，记录 span、类型、read status、连续性和排除理由。
- 校验器必须以所有 scope 资产的行跨度并集证明无缺口；块数相等不能代替 `coverage = 100%`。`unread = 0` 才能进入候选构造。

### 3. Build semantic units

- 跨页、跨段、正文—图注关系直接压缩为 `semantic-units.jsonl`。
- 每个 semantic unit 反查 source block，并记录 loss note 与 uncertainty。
- 固定行数切块或正则抽取不能替代语义单元判断。

### 4. Build and decide candidates

- unit、claim、relation、evidence、structure 候选共用 work package candidate envelope，写入 `candidate-ledger.jsonl`。
- 每个 source block 必须关联候选或 `no_candidate_reason`。
- 每个候选先检索现有 KU、claim、relation 与权威索引，在 `payload.knowledge_match` 记录 `novel`、`existing_target`、`potential_duplicate`、`potential_conflict` 或 `undetermined`，以及命中的对象引用。
- 精确匹配和候选召回可由脚本辅助；名称、翻译、类型、合并、重复与矛盾语义由 Agent 裁决。
- `potential_conflict` 路由 `reconcile`；没有冲突信号时不运行完整冲突裁决。证据不足用 `needs_evidence` / `deferred`。

### 5. Typed write-back and closeout

- 仅 `approved` 候选进入类型化写回。
- evidence 交给 `verify`；冲突交给 `reconcile`；theme/hierarchy 交给 growth。
- `summary.md` 记录覆盖、候选、apply/no-delta/defer 和未解决项。
- `manifest.json` 记录 profile、逐来源 hash、processing scope、聚合输入 hash、输出 hash、声明状态和基线。
- `semantic_acceptance` 单独记录 Agent 复读状态、来源版本、遗漏数和验收边界；不得由机械工件完整性推导。

## 新来源的紧凑工件

```text
03-processing/<doc-id>/
  source-map.jsonl
  semantic-units.jsonl
  candidate-ledger.jsonl
  manifest.json
  summary.md
```

不得为每章固定生成 14 个 Markdown 文件。只有内容规模、并发审查或恢复边界确实需要时，才按 chapter 分片同一种 JSONL；manifest 记录分片。

### Processing profile 选择

- 新来源包使用 `compact-v4`，即上述五类工件；`manifest.json` 记录 profile、来源指纹、覆盖计数、状态和四类逻辑输出哈希。
- 文件只在规模或恢复边界确有需要时分片，manifest 必须记录顺序和哈希；分片不得重建空 chapter 目录。
- 旧 `legacy-chapter` 目录只作为历史 provenance，不是活跃 profile，也不得作为新任务模板；现行摄入与补审统一使用 compact-v4。
- 当前已有三个通过机械验证和 Agent 语义验收的 compact-v4 包；不得为“升级格式”重复摄入已接受范围。

机械校验入口：`python scripts/validate_processing_package.py 03-processing/<doc-id>`。

## 门禁

- 原始来源 hash 可验证。
- `processing_scope.assets` 全部属于 `source_assets`，且 source-map/parallel spans 对每个 scope 资产逐行无缺口覆盖；scope 外资产不得冒充本包已复读内容。
- `input_fingerprint` 与当前 `source_assets` 一致；漂移包的有效状态必须为 `reopened_source_drift`。
- source block 覆盖率 100%，未读块为 0。
- semantic unit 均有 source block 引用。
- 每个 source block 有候选引用或明确的 no-candidate reason。
- 每个候选已完成现有知识的重复/冲突筛查；`undetermined` 不得直接写回。
- 正式写回能反查 candidate、decision、evidence 与 apply 结果。
- 机械校验通过不等于语义覆盖已被接受。
- “语义工件完整性”只检查覆盖工件；真正的语义验收必须有 Agent、来源版本、遗漏数与验收边界。

## 历史边界

chapter-based processing 只供追溯；当前健康检查可读取其 provenance，但不得把旧模板、旧完成字段或旧报告要求重新路由到新摄入。

## 参考

- `references/distillation-system-contract.md`
- `references/model-semantic-processing.md`
- `references/knowledge-unit-field-contract.md`
- `references/body-template.md`
- `references/citation.md`
- `references/taxonomy.md`
- `references/hierarchy-field.md`
- `references/relation-types.md`
- `.agents/skills/00-coordination/system-upgrade/references/work-package-contract.md`
