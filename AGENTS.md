# 《赞助人与画家》知识系统 — Codex 总入口 v6.0.1

## 一、权威与范围

- 当前版本：v6.0.1（2026-09-09）。Codex 是本项目唯一执行客户端。
- 本文件规定目标、边界和入口；`.agents/pipeline.md` 规定阶段交接，`.agents/skills/` 是唯一 Skill 根。它们是同一系统的从属文件，不是独立客户端。
- 用户当前要求优先于项目规则；来源事实以原始材料为准，历史报告和自动记忆不授权改动。
- 权限由实际 Codex 运行环境决定，不维护另一份 allow/confirm/deny 清单；不把配置存在视为 Hook 生效。
- 中文沟通，语义分析为基础。直接阅读、分析和撰写；代码只在必要的定位、校验、受控写回、索引和页面实现中辅助，不替代语义判断。

## 二、工作目标

第一部分：知识元与知识图谱，按 **摄入 → 处理 → 知识元 → 对齐 → 补足 → 关系** 顺序执行。
第二部分：知识发现与知识呈现，后续开展发现、涌现和成果组织，最终形成页面展示。

当前执行第一部分。不得因新增 KU、图谱孤点、层级空缺或输出而自动启动第二部分。初期 Theme/Topic 挂载标为暂不开展，不为填字段制造主题。后续部分由用户明确启动。

各阶段先保存过程和结果再交接；已具备条件的对象可以继续，阻断对象单列。无新增也是可接受结果，需说明审查依据。阶段执行不自动增加逐步用户审批。

## 三、记录、目录和版本

- 每次收到本项目中实际可见的用户消息，先在 `06-runtime/governance/user-revisions.md` 追加原话；普通问答也记录，解释与处理结果另列，不把普通消息升级为规则。
- `06-runtime/governance/current-requirements.md` 汇总当前有效要求，引用原话编号；本文件只规定记录义务，不复制会话正文。
- 不声称记录未提供的其他任务或后台消息。文件无法写入时应说明，恢复后补记。
- 过程记录与阶段结果在相应业务目录分开保存，具体位置见 pipeline。每个对象沿用固定路径版本更迭，不按日期、轮次或“最终版”复制同用途文档。
- 结果报告指向唯一当前成果；历史原话、证据、裁决与来源版本保留，不以更新结果为由抹去。
- `02-sources/` 来源本体只追加，不改写、不删除；顶层登记文件可以更新、不能删除。
- 业务目录从 `01-domain/` 开始，保存领域约束与命名规范；编号表示内容职责，不等同于六个阶段。
- `03-processing/` 保存摄入与处理的过程、覆盖证据和结果；`04-knowledge/` 保存知识分析过程、知识元、关系、证据与成果状态；`05-outputs/` 保存呈现过程、定稿及页面。
- `06-runtime/` 保存用户记录、治理日志与必要机器状态，不代替业务阶段结果。

## 四、知识与执行边界

- KU 类型：person / institution / place / work / publication / term / procedure / event。claim 属于断言与证据层，不是 KU。
- 后续结构主轴：domain → dimension → theme → topic → KU；Cluster 仅为发现候选，不是正式结构节点。
- 来源阅读、候选、知识元成稿、对齐、补足、正式关系与语义验收分别记状态，不以文件存在或健康分数推导完成。
- 处理保留来源定位和覆盖证明；脚本不得代替完整语义阅读。证据不足保留待证，来源变化按指纹重开有效处理状态。
- 候选在写回前检索现有对象，判断重复与冲突。approved 不等于 applied；无变化记 no_delta，失败不记 completed。
- 外部补证先 collect → evidence JSONL，经过语义判断后用 `scripts/verify_apply_evidence.py` dry-run/apply 写回验证状态。身份对齐不等于事实全部验证。
- 正式关系须有有效端点、受控类型、方向及支持该具体关系的证据。共现、标签、正文链接与 weak_associations 不自动成为正式关系。
- 同一文件写回串行，整批验证写回先预检并原子提交；恢复先核对证据指纹。
- 只使用 main，不创建其他分支或 worktree。提交、推送需用户明确授权；本地完成与远程同步分别核验。
- 系统修订先处理权威契约及直接依赖，再按影响做必要检查。不把全套测试、刷新索引或外部采集变成每个语义步骤的固定动作。

## 五、Skills

| Skill | 职责 |
|---|---|
| ingest | 第一至第三阶段：来源登记、语义处理、知识元成稿，逐阶段留存结果 |
| verify | 第四阶段：身份和表述对齐、冲突处理；各阶段必要的证据验证 |
| enrich | 第五阶段：围绕已有知识元的明确缺口语义补足 |
| relate | 第六阶段：关系审查、证据绑定和正式写回 |
| synthesize | 第二部分：知识发现、涌现与结构演化；当前不自动启动 |
| compose | 第二部分：查询、成果组织、内容定稿和页面呈现 |
| inspector | 定向审阅、内容/编码/证据/系统检查；不重写规则 |
| system-upgrade | 已授权的规则、Skill 和系统重构 |

常规规则直接写在 SKILL.md；只有共享契约、长枚举或条件分支使用直接 reference。读取深度为 AGENTS → Skill → direct reference；无重复技能、隐式多层必读或独立规则副本。
Skill 固定路径为 `.agents/skills/<skill-name>/SKILL.md`，不使用历史阶段分类目录；阶段顺序由 pipeline 规定。

## 六、关键入口

- `.agents/pipeline.md`
- `01-domain/workflow-overrides.md`
- `01-domain/taxonomy-registry.md`
- `01-domain/naming-conventions.md`
- `06-runtime/governance/user-revisions.md`
- `06-runtime/governance/current-requirements.md`
- `06-runtime/governance/system-upgrade-log.md`
- `06-runtime/state/skill-registry.json`（派生导航，不是权威）

## 七、版本说明

当前版本：v6.0.1。升级过程、删除范围和验收证据只记入系统升级日志。当前文件代表规则已落地，不代表既有研究成果重新经过语义验收。
