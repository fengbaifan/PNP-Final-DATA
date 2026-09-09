---
name: retrospect
kind: leaf
triggers:
  - retrospect
  - 输出回溯
description: >
  对 query、essay、deck、graph、dashboard 等输出执行语义回溯，识别可回流候选并记录诚实的 file-back 状态。
---

# retrospect

## 触发边界

- 用户明确要求输出回溯；或
- 持久化 output 出现新的可检验 claim、关系、主题、研究问题或与现有知识冲突的解释。

纯格式转换、导航、可视化投影和现有知识重述不固定运行本 Skill；它们保留 `not_reviewed` 或按 output contract 记录不具备回流资格的 `rejected`。

## 流程

1. 读取 output artifact、metadata 与引用的 KU/claim/relation。
2. 区分已有知识重述、输出解释和真正的新候选。
3. 新候选按统一 candidate envelope 进入当前 work package。
4. 为候选绑定来源和不确定性；需要验证时交给 `verify`。
5. 更新 `output-registry.yml` 的 file-back 状态和候选引用。

## Output metadata 与 file-back 状态

每条 output record 记录 `output_id`、artifact refs、使用的 units/claims/relations、source refs、uncertainty、`candidate_refs` 和 `file_back_status`。合法状态仅为：

```text
not_reviewed
reviewed_no_candidates
candidates_deferred
candidates_ready
applied
rejected
blocked
```

`reviewed_no_candidates` 必须实际完成语义回溯且没有知识增量；`applied` 必须存在 candidate 和类型化写回证据。旧 `filed_back` 与四个 `new_candidate_*` 字段只读兼容。`candidate_refs` 指向 `06-runtime/state/candidate-index.jsonl` 中存在的 ID；Output Gallery 必须拒绝未知 ID，且不得制造空 apply plan。

可回流内容包括新建/可合并 KU、证据绑定的 claim/relation、新 source/evidence 或 Theme/Topic/Cluster 候选。版式、摘要、文风和无来源解释不进入知识层。

## 边界

- 不压缩或重写历史 log。
- 不把文风、版式或前端视觉分组回写为知识事实。
- 不把零候选输出标为 `applied` 或旧值 `filed_back`。
- 正式 KU/claim/relation/theme 写回仍走各自类型化入口。

## 参考

- `.agents/skills/00-coordination/system-upgrade/references/work-package-contract.md`
