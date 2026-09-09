# Growth Skill 导航

本目录是导航分类，不是可运行 Skill。成长事件直接路由到叶子 Skill：

| 事件 | Skill | 边界 |
|---|---|---|
| 构建层级快照 | `build-hierarchy` | 使用已批准对象，不自动创造事实 |
| 补足现有 KU 的外部语义 | `enrich` | 验证状态变化交给 verify |
| 发现跨来源模式 | `synthesize` | 先进入 candidate ledger |
| 结构输入变化需要重评 | `evolve-hierarchy` | hierarchy 变化必须记录影响 |

冲突裁决属于 `reconcile`。本目录不维护独立成长状态机、固定周期或比例型成熟度目标。
