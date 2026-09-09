# 运行与治理记录

本目录不定义另一套流程。Codex 通过 AGENTS.md、.agents/pipeline.md 与唯一 Skill 根执行。

- [user-revisions.md](governance/user-revisions.md)：每条本项目可见用户消息的原话、目的解释与处理结果，持续追加。
- [current-requirements.md](governance/current-requirements.md)：当前有效要求，引用原话编号。
- [system-upgrade-log.md](governance/system-upgrade-log.md)：系统变更的过程、最终结果与验证记录，固定文件版本更迭。
- governance/governance-backlog.md：派生信号，不代替语义裁决。
- state/：必要机器快照；候选索引不等于已执行知识发现。
- automation/：既有 evidence、decision、plan、manifest、result、summary 与必要恢复状态。按同一工作对象关联业务阶段过程和结果，不另建同用途副本。
- eval/：既有评测证据。

处理和知识的过程/结果保存在各自业务目录。历史证据默认保留；来源和不可替代裁决不删除。生成索引不改历史账本。
不另设全局 checkpoints/traces 目录；恢复状态沿用 automation 中既有工作包位置，阶段完成依据由业务目录的 process/results 保存。
Git 未授权时不提交；此时以重复生成的哈希稳定性核验幂等，发布前再执行基于 HEAD 的 --check-generated。
