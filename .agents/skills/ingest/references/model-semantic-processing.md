# Compact Semantic Processing Protocol v4.2

## 一、source-map.jsonl

一行对应一个最小可审计 source block：

```json
{"block_id":"b001","source_file":"02-sources/doc/ch01/original.md","line_start":1,"line_end":8,"parallel_sources":[],"block_type":"body_argument","read_status":"read","continuity_refs":[],"semantic_unit_refs":["su001"],"candidate_refs":[],"no_candidate_reason":null,"notes":null}
```

`read_status`：`read`、`merged`、`excluded_with_reason`、`needs_review`。正式写回前不得存在 `needs_review`；排除项必须有理由。

## 二、semantic-units.jsonl

```json
{"semantic_unit_id":"su001","source_block_refs":["b001","b002"],"semantic_type":"historical_fact","summary":"...","continuity":{"type":"cross_page","reason":"..."},"loss_notes":[],"uncertainty":[]}
```

跨段、跨页、正文—图注和双语对齐在同一记录中表达，不再拆成 continuity map、stitch log、chunk 和 chunk meta 四套文件。

## 三、candidate-ledger.jsonl

使用 work package contract 的统一 envelope。`origin_ref` 指向 semantic unit 或 source block；类型专有内容放入 `payload`。同一候选可引用多个 source block，不复制候选。

来源候选还必须在 `payload` 中记录一次现有知识筛查：

```json
{"knowledge_match":{"status":"novel","target_refs":[],"notes":"No matching KU, claim or relation found."}}
```

`status` 只能是 `novel`、`existing_target`、`potential_duplicate`、`potential_conflict` 或 `undetermined`。脚本可以召回精确名称、slug、claim 主体和 relation 端点，但不得自动裁决语义重复或矛盾。`potential_conflict` 交给 `verify`；`undetermined` 只能保留为待证据或延期。

## 四、manifest.json

```json
{
  "processing_profile": "compact-v4",
  "doc_id": "YYYY-creator-short-title",
  "fingerprint_mode": "text_crlf_to_lf_v1",
  "source_assets": [
    {"path": "02-sources/doc/ch01/original.md", "sha256": "sha256:...", "role": "primary_text", "language": "en"}
  ],
  "input_fingerprint": "sha256:...",
  "coverage": {
    "source_blocks_total": 0,
    "source_blocks_reviewed": 0,
    "unread_blocks": 0,
    "blocks_without_candidate_review": 0
  },
  "candidate_counts": {},
  "status": "running",
  "semantic_acceptance": {
    "reread_status": "accepted_with_findings",
    "reviewer_kind": "agent",
    "reviewer_id": "agent-id",
    "reviewed_at": "ISO-8601",
    "source_version": "sha256:...",
    "omission_count": 1,
    "acceptance_boundary": "候选召回覆盖；不含知识写回和事实外部验证"
  },
  "output_hashes": {}
}
```

完成门禁要求两个覆盖差值均为 0，且 `semantic_acceptance` 字段完整。`status=completed` 只表示 processing 完整，不等于候选已全部写入知识库。

### 来源漂移与有效状态

- `fingerprint_mode` 必须显式为 `text_crlf_to_lf_v1`。
- `source_assets[*].sha256` 对仓库规范化文本字节计算：仅将 CRLF 规范为 LF，以消除 Windows/Linux Git checkout 差异；编码、BOM、孤立 CR 和其他内容字节不归一化。
- `input_fingerprint` 由 `fingerprint_mode` 与排序后的 `path + sha256` 聚合计算。
- 来源缺失、逐文件哈希变化或聚合指纹不一致时，声明状态原样保留，运行时 `effective_status` 自动转为 `reopened_source_drift`。
- 来源漂移同时使既有语义验收失效；不得改写旧 `reviewed_at` 或历史候选来伪装重新处理。

### 语义工件完整性与语义验收

- `semantic_artifact_integrity` 是有分机械指标，只证明 compact-v4 文件、跨度、引用和覆盖差值闭合。
- `semantic_acceptance` 是无分语义状态，只能由实际复读的 Agent 写入。
- `reread_status` 仅用 `accepted` 或 `accepted_with_findings`；前者要求 `omission_count = 0`。
- `acceptance_boundary` 必须明确是否包含全文、图注、双语对齐、候选召回、外部验证与知识写回。
- legacy 包不做批量伪回填；健康状态必须把缺少独立复读字段的历史包显式列为 `legacy_packages_without_acceptance`。

## 五、summary.md

只保留人类可读的范围、覆盖结果、重要候选、apply/defer/no-delta、异常与未解决问题，不复制 JSONL 全表。

## 六、自动化边界

- 脚本可校验 JSONL、计算覆盖差值、hash、去重和生成 summary 统计。
- Agent 必须阅读原文并判断 block 类型、semantic unit 边界、candidate 类型和 no-candidate reason。
- 图片无法用文本充分表达时必须视觉检查，不能因 OCR 存在而跳过。
