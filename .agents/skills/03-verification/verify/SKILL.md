---
name: verify
kind: leaf
triggers:
  - verify
  - 验证知识元
  - multi-source
  - 多来源验证
description: >
  验证技能。执行单来源或多来源级联验证，并严格采用
  verify_collect_* -> evidence JSONL -> verify_apply_evidence.py 的两阶段工作流。
  被 ingest、enrich、reconcile 等流程调用，也可独立触发。
---

# verify 技能 v3.1

> 验证的目标不是“尽快改状态”，而是让证据和写回解耦，让每次状态提升都可回溯。

## 工作流

```text
collect
  -> scripts/verify_collect_wikidata.py
  -> scripts/verify_collect_wikipedia.py（REST Summary + Action Search collector）
  -> scripts/verify_collect_lcnaf.py（Person / Institution 的 LC/NACO 权威名称 collector）
  -> scripts/verify_collect_openlibrary.py（Work / Publication 的 Open Library 书目 collector）
  -> scripts/verify_collect_openalex.py（Term / Procedure 的 OpenAlex 学术语义候选 collector）
  -> browser / search / scholar / archive 证据
  -> evidence JSONL

apply
  -> scripts/verify_apply_evidence.py --dry-run
  -> scripts/verify_apply_evidence.py --apply
```

## 级联顺序

```text
L1 Wikipedia REST API
L2 Wikidata API
L3 浏览器与开放网页核验
L4 Google Search / Perplexity
L5 Google Scholar / CrossRef
L6 archive.org / 图书档案站点
L7 模型内部知识兜底
```

## 强制规则

1. collect 阶段只产出 evidence，禁止直接写知识元。
2. apply 阶段才允许更新 `last_verified`、`updated`、`evidence_status`、`verification_level` 和正文“验证状态”区块。
3. 单一 evidence 不能把 `confidence` 提升到 `high`。
4. `entity_identity_only` 的证据不能单独把 `consensus` 提升到 `confirmed`。
5. `source_count` 不得自动递增。
6. `L7` 只能作为 `source_backed` 或 `model_supported` 级别证据，不等于 external verification。
7. Wikipedia / Wikidata API 命中必须先判断 `claim_scope`；单一 `entity_identity_only`、`term_existence`、`event_identity_only` 或 `bibliographic_hint` evidence 最高只能推荐 `partially_verified`。

## 结果字段

- `evidence_status`
  - `unverified`
  - `source_backed`
  - `partially_verified`
  - `externally_verified`
  - `model_supported`
- `verification_level`
  - `L1` ~ `L7`
- 正文区块统一使用 `## 验证状态`

## 多来源交叉验证模式

当对象只有单一来源、多个来源可能互相依赖，或不同来源出现不一致时，在同一 verify 工作流内执行：

1. 明确待验证对象、claim/relation 范围和现有来源。
2. 区分独立来源、转引来源、身份锚点和语义证据；QID 默认只证明身份锚点。
3. 通过 collector 或受控浏览写入 evidence JSONL，标记支持、局部支持、冲突、无关或身份消歧。
4. `source_count` 从实际绑定且去重的来源派生，不使用 `+= 1`；来源数增加不自动提升 confidence、consensus 或 verification。
5. 冲突路由 `reconcile`，新对象路由 `ingest`；证据不足保留 `needs_evidence`、`deferred` 或冲突状态。

多来源验证没有独立 writer、状态机或运行目录，因此不是单独 Skill。

## 自动化风险路由

Evidence 自动化只允许：

```text
collect -> evidence JSONL -> risk route -> typed dry-run/apply -> change-aware closure
```

`scripts/_evidence_policy.py` 定义可执行分级，`.agents/guards/automation-risk-policy.md` 定义治理边界。`scripts/evidence_batch_runner.py` 可把混合 evidence 写成 `plan.json` 和非空队列；`--apply-low-risk` 必须配合 `--dry-run-apply`，且只处理 L1 existing-KU。L2 由 Agent 审查，L3 保持 deferred。该 runner 不创建 KU、不选择 relation/claim、不刷新生成状态，也不执行 Git 收尾。

## 运行记录

verify 的正式写回记录进入 `verification-log.md`；批次进度进入当前 work package 的 `runner-state.json`。恢复前必须核对 evidence 指纹。正式 apply 先整批预检，再原子提交 KU 与日志；blocked/failed 不得记录为 completed，也不得留下 `.bak`。

每条新 evidence 必须提供 `source_independence_group`。Wikipedia 与 Wikidata 均属于 `wikimedia`，不能仅因 `source_type` 不同就算两条独立来源。

## 当前脚本状态

- `scripts/verify_collect_wikidata.py`：生成候选、匹配质量、claim scope、independence group、阻断原因和建议字段；候选实体批量拉取、请求有界重试，`api_error` 可从历史 evidence 定向重跑且不改写原账本
- `scripts/verify_collect_wikipedia.py`：生成 REST/Search 证据、候选比较、redirect/disambiguation 与建议字段
- `scripts/verify_collect_lcnaf.py`：只为 Person / Institution 收集 LC/NACO 权威名称候选；名称歧义、类型不兼容与请求错误明确阻断，身份之外的贡献关系仍由 Agent 裁决
- `scripts/verify_collect_openlibrary.py`：只为 Work / Publication 收集书目候选；标题、初版年、作者、出版社与 ISBN 形成 evidence，年份冲突和同名异作者阻断，视觉解释与领域相关性仍由 Agent 裁决
- `scripts/verify_collect_openalex.py`：只为 Term / Procedure 收集论文题名与重建摘要中的语义候选；无摘要、弱术语匹配、缺少定义/方法语境与撤回记录明确阻断，提及不等于定义，最终写回仍须 Agent 逐对象裁决
- `scripts/verify_apply_evidence.py`：唯一验证写回入口；阻断越权状态、校验恢复指纹并原子提交

## 被调用关系

```text
ingest -> verify
enrich -> verify
reconcile -> verify
audit-confidence -> verify
```

## 参考文档

- `references/cascade.md`
- `references/type-verification.md`
- `references/api-verification.md`
- `references/result-handling.md`
- `references/no-data-and-browser-research.md`
- `.agents/skills/00-coordination/system-upgrade/references/runtime-state-machine.md`
