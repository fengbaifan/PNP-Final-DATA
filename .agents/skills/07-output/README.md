# Output Skill 导航

本目录是导航分类，不是可运行 Skill。按输出目标调用叶子 Skill：

| 事件 | Skill | 边界 |
|---|---|---|
| 跨知识库查询 | `query` | 返回证据边界，不修改知识事实 |
| 写作提纲 | `compose` 的提纲模式 | 评估覆盖、证据边界并规划结构 |
| 结构化写作 | `compose` | 基于当前知识与不确定性生成输出 |
| 输出回流 | `retrospect` | 新发现进入 candidate ledger 和 file-back 状态 |

输出不是知识权威源；正式 KU、claim、relation、theme 或 hierarchy 写回必须回到相应类型化入口。
