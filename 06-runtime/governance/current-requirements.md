# 当前有效要求索引

更新依据：REV-022（2026-09-09）。用户原话及演变保留在 [user-revisions.md](user-revisions.md)；本文件只定位有效要求与规则，不复制研究报告或完整实施历史。

| 编号 | 当前要求 | 原话依据 | 权威入口 |
|---|---|---|---|
| R-01 | 语义分析为基础，尽量少用代码和脚本 | REV-001、002 | [AGENTS](../../AGENTS.md) |
| R-02 | 知识元与知识图谱／知识发现与知识呈现两部分 | REV-003 | [pipeline](../../.agents/pipeline.md) |
| R-03 | 先做摄入和关系；发现与涌现后置，由用户明确启动 | REV-002、003、015 | AGENTS、pipeline |
| R-04 | 摄入—处理—知识元—对齐—补足—关系逐阶段执行 | REV-002 | pipeline |
| R-05 | 说明各阶段处理内容、成果、完成度与缺口 | REV-001、002、015、021 | pipeline 的过程/结果位置及任务 results |
| R-06 | 过程与当前结果分开，知识过程统一到 03 | REV-003、021 | [目录规则](../../01-domain/naming-conventions.md) |
| R-07 | 同一文献/对象沿固定路径迭代，不复制多份当前版本 | REV-003 | AGENTS；必要新对象按来源建立，原始来源保留 |
| R-08 | 修订原话与目的专门保留 | REV-001、002 | user-revisions.md |
| R-09 | 后续最终有页面展示 | REV-003 | [compose](../../.agents/skills/compose/SKILL.md) |
| R-10 | 已从讨论进入实际重构 | REV-005 | [系统升级日志](system-upgrade-log.md) |
| R-11 | 每条实际可见用户消息均记录，普通问答不自动升级为规则 | REV-005 | AGENTS、user-revisions.md |
| R-12 | Codex 的 AGENTS 为唯一总入口，唯一 Skill 根，消除冗余系统 | REV-005、022 | AGENTS、[Skill 注册契约](../../.agents/skills/system-upgrade/references/skill-registry-schema.md) |
| R-13 | 业务目录从 01 开始，对应现行职责 | REV-006、007 | 目录规则 |
| R-14 | KU/关系→Topic→Theme→Dimension→Domain 自下而上涌现，无预设节点/数量/归属 | REV-009 | [synthesize](../../.agents/skills/synthesize/SKILL.md) |
| R-15 | 从空项目基线起步，不将继承文件或旧状态当新成果 | REV-010、015 | AGENTS、[有效登记](../../04-knowledge/accepted.yml) |
| R-16 | Skills 的功能、内容、产出及交接基本完备 | REV-010、022 | pipeline、八个实际 Skill |
| R-17 | 减少固定门禁、重复审查及冗余，按改动做必要检查 | REV-011、022 | AGENTS、[必要检查](../../.agents/skills/system-upgrade/references/upgrade-acceptance-gates.md) |
| R-18 | 保留页面样式，未来按新数据适配；当前暂停刷新 | REV-011、013、015 | compose；页面是否更新以实际呈现任务为准 |
| R-19 | 曾要求先提交同步再精简；后续提交仍需明确授权 | REV-012 | 系统日志记录先行同步 d07965d；不等于后续改动已推送 |
| R-20 | 初始化项目不沿用过高版本 | REV-008 | 项目 0.1.0，规则不单独编号；既有机器格式版本与项目版本分开 |
| R-21 | 当前只测试第一章，逐行语义阅读、处理断行跨页；第六章后置 | REV-013、014、015 | [第一章结果](../../04-knowledge/results/patrons-and-painters-chp-1.md) |
| R-22 | archive 包含所有文献；城市/政体、建筑/作品按指称区分；类型不足和遗漏须记录 | REV-016 | [类型规则](../../01-domain/taxonomy-registry.md) |
| R-23 | Wikipedia—Wikidata 双重身份核对，Getty 及适用官方来源补足 | REV-017 | [verify](../../.agents/skills/verify/SKILL.md)、[enrich](../../.agents/skills/enrich/SKILL.md)；缺一侧保留未完成 |
| R-24 | 标题与描述中英文对应，不因翻译新增事实 | REV-018 | [元数据规则](../../.agents/skills/ingest/references/knowledge-unit-field-contract.md)、[内容规则](../../.agents/skills/ingest/references/body-template.md) |
| R-25 | 统一元数据＋按类型的内容＋关系与证据；全名优先，记录结构化属性与历史变化 | REV-019、020 | 同上；适用缺口明确待补，不填造事实 |
| R-26 | 全面核对入口与路径，落实渐进式读取和分布记录 | REV-022 | AGENTS 的渐进式读取与分布记录；pipeline 的阶段交接 |

## 执行状态的唯一落点

研究数量、对象清单、双语/三部分改写范围、外部补足及未决项以第一章 results 为准；此处不复写数字。第六章、知识涌现和页面仍暂停，规则升级不构成重新执行或验收。

知识处理过程在 03-processing/<task-id>/process/knowledge.md，摄入处理过程在同包 stages.md；04-knowledge 保存成果和当前结果。系统调整的详细证据只在 system-upgrade-log.md，纯系统任务不在 03/04 重复追加报告。

每次只更新受影响的要求行和对应权威规则；原话持续追加、历史裁决保留。仅改变实际当前结论，不按轮次复制要求文件。
