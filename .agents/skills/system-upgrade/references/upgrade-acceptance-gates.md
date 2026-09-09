# Upgrade Acceptance Gates v2.0

验收按实际影响选择，不为纯文档或导航变更强制制造 health、backlog、Hook 或 runtime 更新。

## 通用门槛

| 门槛 | 检查方式 |
|---|---|
| `rule_landing` | 规则位于最近的 Skill/reference，其他位置只索引 |
| `entry_sync` | 受影响的 AGENTS、README、pipeline 或领域入口已同步 |
| `impact_logged` | system-upgrade-log 已记录影响面、删除边界、验收证据与未解决项 |
| `targeted_pass` | 与变更最近的行为测试或结构检查通过 |
| `drift_pass` | rule drift 与断链检查无 fail |
| `generated_clean` | 仅在存在生成投影时，刷新后相对 `HEAD` 无漂移 |

## 专项门槛

### Skill 增删、改名或角色变化

- 每个可运行 Skill 必须有唯一 `name`、显式 `kind` 和非空 `triggers`。
- router 必须声明有效 `routes_to`；leaf 不得声明路由。
- 分类入口使用 README，不用无职责聚合 `SKILL.md`。
- `python scripts/skill_registry.py` 必须通过：唯一 Skill 根、无重复触发词、无断裂或孤儿 reference、快照一致。
- frontmatter 重复键与 reference 引出的隐藏第二层必读规则必须 fail closed。
- 新增脚本时检查实际职责与调用关系；权限以 Codex 运行环境为准，不创建权限副本。

### 验证语义变化

- 明确 evidence schema、claim scope、apply 边界和回滚方式。
- collect 不写知识事实；apply 支持 dry-run。
- confidence/consensus 的唯一执行权威仍为 `verify/references/result-handling.md`。
- 来源数量、QID 或脚本分数不能自动晋级状态。

### 脚本或生成器变化

- 对应 Skill/reference 明确脚本职责、只读/apply 边界与失败方式。
- 增加或更新行为测试，不能只检查文件存在。
- 生成器必须幂等；受影响的投影在工作包末集中刷新一次。
- 只更新实际调用关系，不创建第二套客户端权限文件。

### 路由或全局规则变化

- `.agents/pipeline.md` 与相关 Skill 的职责无冲突。
- `AGENTS.md` 只保留摘要、边界和入口；README 只保留用户导航。
- 按用户确定的六阶段交接；禁止隐式启动第二部分或建立第二套阶段状态机。

### Processing 或知识 schema 变化

- 明确输入、覆盖证明、候选、写回与不完整状态。
- 评估历史 backfill，并区分机械迁移与语义复核。
- 只有此类变化实际影响知识健康输入时，才刷新 current-health/backlog。

## 未通过时

未通过项必须在升级日志中逐项记录。若关键行为门禁失败，不得标记完成；可修复项继续修复，外部依赖或授权阻断才标为 partial/blocked。不得用新增 backlog 项掩盖本应在当前工作包修复的回归。
