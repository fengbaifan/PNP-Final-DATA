# Claim / Evidence 治理契约

claim 属于断言与证据层，不是 Knowledge Unit。claim 必须绑定来源跨度或保持
`needs_evidence`；脚本不得裁决 claim 真伪。

## Claim 类型

```text
factual_claim
interpretive_claim
synthetic_claim
evaluative_claim
contested_claim
historiographic_claim
```

## 当前 Evidence Envelope

```yaml
evidence_id: optional-on-collect        # apply 时如缺失则由输入与目标稳定派生
ku_path: 04-knowledge/units/<type>/<slug>.md
claim_id: optional
relation_id: optional
platform: string
source_type: string
source_authority: string
source_independence_group: string       # 共享生态使用同一组，例如 wikimedia
url: optional
source_span: optional
claim_scope: entity_identity_only | term_existence | event_identity_only | bibliographic_hint | basic_fact | bibliographic_fact | source_claim | domain_relevance | historiographic_claim | interpretive_claim | synthetic_claim | evaluative_claim | contested_claim
claim_target: string
match_quality: strong | medium | weak | none
match_score: number
verified_fields: []
conflicting_fields: []
blocking_reason: optional
recommended_changes: {}
reviewer: optional
notes: optional
```

`verification_level` 只使用 `L1`–`L7` 表示验证渠道级联；
`evidence_status` 使用 `unverified / source_backed / partially_verified /
externally_verified / model_supported`。两者不得再使用同名的两套枚举。

## 写回与日志

```text
collect -> evidence JSONL -> risk route -> dry-run -> atomic apply
```

- `verification-log.md` 只记录成功提交的 `evidence_id`、target、claim scope、verification level、outcome、reviewer 和 evidence file。
- blocked/failed 不进入成功日志，也不得把批次标记为 completed。
- Wikipedia 与 Wikidata 同属 `wikimedia`，不能互相充当独立第二来源。
- `confidence: high`、`consensus: confirmed` 和复杂 claim 的外部确认都需要 Agent 语义裁决；数量、QID 或脚本分数不授权晋升。
- `supports` 只绑定 evidence/claim；`supported_by` 只绑定 existing-KU 路径，不得混写。

confidence、consensus 与 claim scope 的执行裁决统一路由 `verify`，本文件不复制第二套阈值。
