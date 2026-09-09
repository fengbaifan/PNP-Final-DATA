---
name: query
kind: leaf
triggers:
  - query
  - 知识库查询
description: >
  跨知识库查询技能。综合知识元、层级、主题、索引和当前验证状态，返回带证据边界的答案。
---

# query 技能 v2.0

## query 流程

```text
1. 解析问题与目标类型
2. 优先搜索 04-knowledge/units/、04-knowledge/structure/ 与 04-knowledge/quality/ 的权威索引；需要快速导航时再读取 05-outputs/index/
3. 读取命中的知识元，检查 confidence / consensus / evidence_status
4. 综合回答，并显式说明来源和不确定边界
5. 如发现事实冲突，回流 verify / reconcile，而不是在 query 中直接改库
```

## 验收

- `06-runtime/eval/query-eval-set.jsonl` 在同一记录内保存 query、预期目标、必含/禁止边界和最近一次 Agent replay；不另建平行结果文件。
- Agent replay 必须复读记录中的 `expected_units` 与 `supporting_targets`，写明验收边界和知识状态 digest。
- `audit_rule_drift.py` 只检查 replay 是否完整且仍对应当前知识字节；它不能替代 Agent 对答案召回、事实和不确定边界的语义验收。
- 目标知识变化后 digest 失效，发布门禁要求重新执行对应 query replay，不能只修改时间戳。

## 输出规则

- `low` 或 `disputed` 信息必须显式标注
- 若答案依赖蒸馏报告，应注明其为历史快照
- 若答案依赖 L7，应注明它不是外部验证
