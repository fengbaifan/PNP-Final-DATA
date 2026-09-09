# 摄入的证据边界

普通语义任务：明确来源和范围，完整阅读，形成可定位分析，判断对象及断言，保存过程/结果，成稿后交接。证据不足保留待证，不预设层级，不从共现制造关系。
候选与正式对象分开，成稿与对齐/验证分开。来源本体只追加；登记可更新。判断由 Agent 负责，脚本只辅助机械工作。

使用 compact-v4 机器接口时，source block、semantic unit、candidate 和正式对象之间保留可追踪引用，覆盖和来源指纹按 model-semantic-processing.md 核验。接口中的 payload.knowledge_match 区分新对象、既有对象、重复、冲突和未知，approved 不等于 applied，失败或无变化按实记状态。
既有包保留历史声明，不伪回填。本项目接收成果依据实际新阶段结果，在 accepted.yml 登记引用；文件存在或旧包 completed 不等于本项目已执行。
