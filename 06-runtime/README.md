# 运行与治理记录

本目录不定义另一套流程。Codex 通过 AGENTS.md、.agents/pipeline.md 与唯一 Skill 根执行。

- [user-revisions.md](governance/user-revisions.md)：历史用户修订原话与处理记录；2026-09-25 起冻结，只读。
- [CHANGELOG.md](governance/CHANGELOG.md)：此后系统规则与维护变更的唯一记录入口。
- [current-requirements.md](governance/current-requirements.md)：当前有效要求，引用原话编号。
- [system-upgrade-log.md](governance/system-upgrade-log.md)：既往系统变更历史；2026-09-25 起冻结，只读。
- governance/governance-backlog.md：派生信号，不代替语义裁决。
- state/：必要机器快照；候选索引不等于已执行知识发现。
- automation/：既有 evidence、decision、plan、manifest、result、summary 与必要恢复状态。按同一工作对象关联业务阶段过程和结果，不另建同用途副本。
- eval/：既有评测证据。

研究过程统一在 03-processing 任务包；摄入处理结果在同包 results，知识成果与结果说明在 04-knowledge。历史证据默认保留；来源和不可替代裁决不删除。生成索引不改历史账本。
不另设全局 checkpoints/traces 目录；恢复状态沿用 automation 中既有工作包位置，阶段完成依据由业务目录的 process/results 保存。
检查按实际改动选择；刷新受影响的机器投影即可，不把全量生成、评分或与 HEAD 一致作为日常语义工作的条件。

当前阶段以 [第一章结果](../04-knowledge/results/patrons-and-painters-chp-1.md) 为准。机器快照中保留的历史处理包、候选和审计信号是磁盘清单，不代表阶段完成度或自动开工指令。有效成果按 04-knowledge/accepted.yml 登记。

原话、有效要求索引、系统改动分别维护，不在三处重复完整报告；研究细节只链接对应业务过程。根目录 workflow-copy-manifest.json 保存最初导入时的路径、哈希与数量，是历史证据，不是当前 Skills 注册表；其中旧客户端和旧路径不作为当前入口。
