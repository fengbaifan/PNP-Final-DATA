# Quality Skill 导航

本目录是导航分类，不是可运行 Skill。按当前事件直接调用最小必要叶子 Skill：

| 事件 | Skill | 边界 |
|---|---|---|
| schema、链接、索引或关系结构检查 | `lint` | 只做确定性检查，不裁决置信度 |
| 置信度、证据状态与研究债务审计 | `audit-confidence` | 只读报告与队列，不自动 enrich 或写回 |
| 同一对象、断言或关系存在冲突 | `reconcile` | 语义裁决后走类型化写回 |

claim/evidence 与 relation 细则位于相应叶子 Skill 的 `references/`。本目录不定义第二套路由、状态机或自动调用链。
