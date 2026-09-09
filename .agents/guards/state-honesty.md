# State Honesty Policy v1.1

> 系统可以无人值守地推进机械流程，但不得伪造确定性。

## 一、不确定性标记

当证据不足时，必须写入以下标记之一，不得默认视为 confirmed：

| 标记 | 含义 |
|---|---|
| `needs_evidence` | 关系 / claim 可能成立，但缺少形式化证据 |
| `weak_inference` | 模型推断，无直接证据 |
| `source_backed_only` | 仅有原始来源证据，无外部交叉验证 |
| `external_not_found` | 外部搜索无结果 |
| `model_supported` | 仅模型知识支持 |
| `unresolved` | 存在分歧，未解决 |
| `deferred` | 推迟判断 |
| `tentative` | 暂定，待更多证据 |

## 二、禁止推断

- 禁止把“没有人反对”解释为 `confirmed`。
- 禁止把“脚本检查通过”解释为知识成立。
- 禁止把“Wikipedia 有页面”解释为 `verified`。
- 禁止把“Wikidata 有 QID”解释为 `confirmed`。
- 禁止把“多个来源字段相似”直接解释为 `verified`。
- 禁止把 `model_supported` 包装成 `externally_verified`。

## 三、无人工作流状态

Agent 可以推进 candidate、在证据充分时写入 apply gate、defer / reject / 标记 unresolved。
Agent 不能把“没有人工阻止”解释为 confirmed。

## 四、自动化状态诚实

可控自动化系统可以无人值守地完成扫描、风险分级、dry-run、低风险 apply 和门禁检查，但其输出必须标记为运行状态：

- `plan.json` = 执行计划，不是知识裁决。
- `apply_candidates.jsonl` = 低风险候选，不是已确认事实。
- `review_queue.jsonl` = 需要 Agent 复核，不是已完成。
- `defer_queue.jsonl` = 需要语义判断或证据不足，不是失败。
- `gate_results` = 健康信号，不是工作流完成本体。

自动化不得把 `event_ku_decision=defer`、`review_queue` 或 `L3` 项解释为已完成。
