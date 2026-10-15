# 当前有效要求索引

索引核对日期：2026-10-15。历史用户原话及演变保留在已冻结的 [user-revisions.md](user-revisions.md)；后续规则变化及其用户原话记入 [CHANGELOG.md](CHANGELOG.md)。本文件只定位仍有效的要求，不复制研究报告或完整实施历史。

| 编号 | 当前要求 | 原话依据 | 权威入口 |
|---|---|---|---|
| R-01 | 语义分析为基础，尽量少用代码和脚本 | REV-001、002 | [AGENTS](../../AGENTS.md) |
| R-02 | 知识元与知识图谱／知识发现与知识呈现两部分 | REV-003 | [pipeline](../../.agents/pipeline.md) |
| R-03 | 第一部分按 S0–S7 建设知识元与知识图谱；发现与涌现后置，由用户明确启动 | REV-002、003、015；现行阶段规则 | AGENTS、pipeline |
| R-04 | 按 S0 来源→S1 候选→S2 语义处理→S3 身份对齐→S4 KU 登记→S5 补足→S6 关系→S7 发布交接；对齐只处理身份，详细信息在补足完善 | REV-002、026；现行阶段规则 | pipeline、verify、ingest、enrich |
| R-05 | 说明各阶段处理内容、成果、完成度与缺口 | REV-001、002、015、021 | pipeline 的过程/结果位置及任务 results |
| R-06 | 过程与当前结果分开，知识过程统一到 03 | REV-003、021 | [目录规则](../../01-domain/naming-conventions.md) |
| R-07 | 同一文献/对象沿固定路径迭代，不复制多份当前版本 | REV-003 | AGENTS；必要新对象按来源建立，原始来源保留 |
| R-08 | 修订原话与目的专门保留，历史日志冻结后由 CHANGELOG 记录新规则变化 | REV-001、002；当前治理规则 | user-revisions.md（只读历史）、CHANGELOG.md |
| R-09 | 后续最终有页面展示 | REV-003 | [compose](../../.agents/skills/compose/SKILL.md) |
| R-10 | 已从讨论进入实际重构 | REV-005 | [系统升级日志](system-upgrade-log.md) |
| R-11 | 用户修订记录与系统升级日志冻结为历史；新规则变化进 CHANGELOG，普通问答不逐条登记 | 当前治理规则 | [AGENTS](../../AGENTS.md)、[CHANGELOG](CHANGELOG.md) |
| R-12 | Codex 的 AGENTS 为唯一总入口，唯一 Skill 根，消除冗余系统 | REV-005、022 | AGENTS、[Skill 注册契约](../../.agents/skills/system-upgrade/references/skill-registry-schema.md) |
| R-13 | 业务目录从 01 开始，对应现行职责 | REV-006、007 | 目录规则 |
| R-14 | KU/关系→Topic→Theme→Dimension→Domain 自下而上涌现，无预设节点/数量/归属 | REV-009 | [synthesize](../../.agents/skills/synthesize/SKILL.md) |
| R-15 | 从空项目基线起步，不将继承文件或旧状态当新成果 | REV-010、015 | AGENTS、[有效登记](../../04-knowledge/accepted.yml) |
| R-16 | Skills 的功能、内容、产出及交接基本完备 | REV-010、022 | pipeline、八个实际 Skill |
| R-17 | 减少固定门禁、重复审查及冗余，按改动做必要检查；集中处理关联对象，合并独立检索和写回，不反复搜索无新线索项 | REV-011、022、091 | AGENTS、[必要检查](../../.agents/skills/system-upgrade/references/upgrade-acceptance-gates.md) |
| R-18 | 保留页面样式，未来按新数据适配；当前暂停刷新 | REV-011、013、015 | compose；页面是否更新以实际呈现任务为准 |
| R-19 | 曾要求先提交同步再精简；后续提交仍需明确授权 | REV-012 | 系统日志记录先行同步 d07965d；不等于后续改动已推送 |
| R-20 | 初始化项目不沿用过高版本 | REV-008 | 项目 0.1.0，规则不单独编号；既有机器格式版本与项目版本分开 |
| R-21 | 全书 S2 复用既有阅读、按书序补全正文与书后材料并核对第六章旧稿；全书交接前不推进 S3–S6。实际完成状态及下一阶段输入只由全书结果维护 | REV-013、014、015（历史范围）；2026-09-26 用户指令（全书范围） | [全书 S2 结果](../../04-knowledge/results/patrons-and-painters-full-book-s2.md)、[pipeline](../../.agents/pipeline.md) |
| R-22 | archive 包含所有文献；城市/政体、建筑/作品按指称区分；类型不足和遗漏须记录 | REV-016 | [类型规则](../../01-domain/taxonomy-registry.md) |
| R-23 | 对齐与补足按实体类型选择专业数据库、规范记录、保管机构、数字化原件及研究来源；Wikipedia／Wikidata是有准确对象时采用的可选身份链，QID不作为全部实体完成条件。人物纳入国家人物辞典与档案记录，文献纳入联合目录、手稿目录和Internet Archive等可核版本全文 | REV-017、027、028、056 | [verify](../../.agents/skills/verify/SKILL.md)、[按类型来源](../../.agents/skills/verify/references/type-verification.md)、[enrich](../../.agents/skills/enrich/SKILL.md)；记录每个来源支持范围与阅读程度 |
| R-24 | 标题与描述完整中英文对应，信件不混用外文人名与中文“致／信”；翻译不新增事实 | REV-018、028 | [元数据规则](../../.agents/skills/ingest/references/knowledge-unit-field-contract.md)、[内容规则](../../.agents/skills/ingest/references/body-template.md) |
| R-25 | 统一元数据＋按类型的内容＋关系与证据；全名优先，记录结构化属性与历史变化 | REV-019、020 | 同上；适用缺口明确待补，不填造事实 |
| R-26 | 全面核对入口与路径，落实渐进式读取和分布记录 | REV-022 | AGENTS 的渐进式读取与分布记录；pipeline 的阶段交接 |
| R-27 | 实体可有多个有据角色标签；先按第一批实际结果积累，后续再细调标签体系 | REV-028 | ingest 的 body-template；角色是内容属性，不自动造边或新类型 |
| R-28 | 来源注明章节、印刷页与句子摘要，保留原始定位；摘要是转述，网页按实际小节定位 | REV-030 | ingest 的 knowledge-unit-field-contract |
| R-29 | 从摄入与处理开始顺序收口，每阶段保存唯一当前定稿后清理过程，再交接下一阶段；不同时扩展未收口阶段 | REV-032 | pipeline 阶段收口规则；必要证据、裁决及用户原话保留，定稿不另建副本 |
| R-30 | 增加 family 家族类，区分成员、支系与家户／随从组织；同姓不推定同族 | REV-035、036 | [类型规则](../../01-domain/taxonomy-registry.md)、ingest 内容与关系契约 |
| R-31 | 九类实体统一按分组独立字段、多值条目及时间履历／沿革表达；事实、证据与处理过程分开 | REV-041、042 | [唯一正文模板](../../.agents/skills/ingest/references/body-template.md)；实际整理时原位采用，不以规则更新标记旧卡完成 |
| R-32 | 卡内直接展示实际适用的权威记录与稳定标识；QID、Wikipedia、人物辞典、档号／书目号、馆藏号及数字化全文均按对象选用，并与可点击关联知识元分开说明 | REV-046–049、056 | [唯一正文模板](../../.agents/skills/ingest/references/body-template.md)；身份记录在 alignment.csv、正式关系在 relations.csv，正文提供一致的阅读入口 |
| R-33 | 对已采纳内容中的具名独立对象建立或复用知识元，并全盘审查作品—创作者—委托／赞助—安置／存放，以及人物师承、合作、朋友、亲缘、家庭／家族成员和机构隶属等关系；时间、版本、角色与证据随关系保留，缺端点时不得宣称关系完整 | REV-062、063 | AGENTS、pipeline、[ingest正文模板](../../.agents/skills/ingest/references/body-template.md)、[enrich](../../.agents/skills/enrich/SKILL.md)、[relate](../../.agents/skills/relate/SKILL.md) |
| R-34 | 原书原语言摘录及精确定位随sources保存；实体保留事实、字段、关系和最小证据引用，重复来源导读、采集核验过程及待补说明另存03；事实不确定性保留在对应字段 | REV-072 | ingest的[元数据契约](../../.agents/skills/ingest/references/knowledge-unit-field-contract.md)与[正文模板](../../.agents/skills/ingest/references/body-template.md) |
| R-35 | 根目录专设论文建议目录，保存论文类型、写作与实验建议及投稿期刊；SCI／SSCI收录和中科院分区注明来源、年份与核验范围 | REV-076 | [论文写作建议](../../07-paper/README.md)、[期刊与分区依据](../../07-paper/journal-targets.md)；不新增业务阶段或复制实体结果 |
| R-36 | 原书语义处理同步记录关系候选、提及／指代和证据跨度；S3–S4 处理身份及 KU 映射，S5 区分外部补足，S6 统一裁决。旧六阶段叙述已由 S0–S7 产物契约替代 | REV-077–079；现行阶段规则 | [pipeline](../../.agents/pipeline.md)及ingest、verify、enrich、relate；S2候选在book-statements.jsonl、过程在03、正式边在relations.csv |

## 执行状态的唯一落点

第一章与章前材料的既有成果按各自任务范围保留；全书 S2 的当前状态、完成依据、交接限制与下一阶段输入以[全书结果](../../04-knowledge/results/patrons-and-painters-full-book-s2.md)为准。既有 S3–S6 记录不能代替本轮全书后续阶段的实际处理。知识涌现与页面仍须用户明确启动。

知识处理过程在 03-processing/<task-id>/process/knowledge.md，摄入处理过程在同包 stages.md；04-knowledge 保存成果和当前结果。新系统调整的详细证据只在 CHANGELOG.md，system-upgrade-log.md 为只读历史；纯系统任务不在 03/04 重复追加报告。

每次只更新受影响的要求行和对应权威规则；新规则变化连同原话及目的写入 CHANGELOG，历史裁决保留。仅改变实际当前结论，不按轮次复制要求文件。
