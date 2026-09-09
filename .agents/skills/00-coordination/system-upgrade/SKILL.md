---
name: system-upgrade
kind: leaf
triggers:
  - system-upgrade
  - 系统升级
  - 规则修订
description: >
  系统升级官技能。把已确认的规则、Skill、事件路由与执行器变更写回最近的权威落点，
  同步入口、验证行为并记录历史影响。用于系统规则修订、架构简化和规则/实现漂移修复。
---

# system-upgrade 技能

## 职责

- 把已确认的经验或审查结论写入最近的 Skill/reference。
- 同步 `AGENTS.md`、`.agents/pipeline.md`、README 和必要领域覆盖。
- 修复规则、脚本、测试和磁盘事实之间的漂移。
- 在唯一的 `system-upgrade-log.md` 中记录影响面、验收证据与未解决项。

不负责知识内容批量 enrich，不裁决知识事实，也不把一次对话角色制度化为新 Skill/Hook。

## 四阶段执行

### 1. Scope

1. 读取 `AGENTS.md`、当前 Skill 和与本次变更直接相关的 references；不得把 reference 全量加载当作固定步骤。
2. 记录目标、允许写入范围、禁止事项和历史影响边界。
3. 判断变更属于规则、路由、执行器、状态、文档还是其组合。

### 2. Implement

1. 先修改最近的权威落点。
2. 机械重复优先用现有或最小执行器自动化；语义裁决保留给 Agent。
3. 同步直接依赖的代码、测试和入口，不全库扩散同一句规则。
4. 历史工件默认不改写；需要 backfill 时另立可审查任务。

### 3. Validate

1. 先跑与改动最近的定向检查。
2. 验证失败必须修复或写明真实 blocked 状态。
3. 工作包结束时最多刷新一次生成投影并跑一次完整 closure。
4. existence-only、health 分数或 Hook 数量不能单独证明升级有效。

### 4. Close out

1. 更新唯一的 `system-upgrade-log.md`；不得为同一次升级另建平行版本说明或 impact 文档。
2. 核对 `AGENTS.md`、README、路径与版本。
3. 仅在用户明确授权提交或推送时执行对应 Git 操作并验证远端一致性；未授权时报告本地改动和待执行边界。知识批次 runner 不承担 Git 操作。

## 核心原则

1. **Skill-first**：细则落在最近的 Skill/reference。
2. **Workflow-first**：从对象状态与事件路由设计，不从脚本数量设计。
3. **Automation-appropriate**：机械重复默认自动化，语义判断禁止自动化。
4. **One rule, one authority**：其他位置只做索引。
5. **State honesty**：未审查、无变化、证据不足和已应用必须区分。
6. **Proportional disclosure**：常规短规则留在 Skill；共享、长篇或条件性契约才下沉。
7. **History preservation**：来源证据、裁决、apply 结果等不可替代 provenance 默认保留；用户明确授权后，可删除 Git 可恢复且会冒充现行入口的旧脚本、旧快照和重复规范。
8. **Behavioral acceptance**：验收行为和结果，不以文件存在替代。

## 规则分发

| 修订类型 | 权威落点 |
|---|---|
| 全局边界与入口 | `AGENTS.md` |
| 跨 Skill 路由 | `.agents/pipeline.md` |
| 摄入与覆盖证明 | `.agents/skills/01-intake/ingest/` |
| 验证与 evidence 写回 | `.agents/skills/03-verification/verify/` |
| 质量、relation、claim | `.agents/skills/05-quality/` |
| discovery 与 hierarchy | `.agents/skills/06-growth/` |
| output 与 file-back | `.agents/skills/07-output/` |
| 系统升级细则 | `.agents/skills/00-coordination/system-upgrade/references/` |
| 运行记录 | `06-runtime/governance/system-upgrade-log.md` |

## 文档放置与阅读深度

`SKILL.md` 必须直接说明触发、输入、常规执行、权限边界、状态、产物和下一跳。仅在满足以下至少一项时新建 reference：

- 被两个或更多 Skill 共享；
- 是较长的 schema、模板、受控枚举或独立版本化契约；
- 只在少数条件分支、异常或专项审查中读取；
- 合并后会显著妨碍常规路径阅读。

短、单一调用方、每次执行都必读的规则并入 `SKILL.md`。活跃路径最多为 `AGENTS -> SKILL -> direct reference`；reference 可以交叉说明，但不得引入未由当前 Skill 直接登记的必读 reference。Skill 是否保留独立身份，取决于是否拥有不同触发、权限、状态或产物，不取决于文件行数。

## 反馈与治理债务

- 用户意见或审查发现先区分 `proposed`、`accepted`、`implemented`、`rejected`、`superseded`；未确认建议不得写成现行规则。
- `implemented` 必须指向权威落点和验收证据；历史修订只写系统升级日志，不维护第二份时间线或逐批 impact 文档。
- 治理债务只作状态信号：验证债务路由 `verify`，关系债务路由 relation governance，字段债务路由 `lint/enrich`，来源追踪债务路由 `ingest/reconcile`，发现债务路由 `synthesize`，输出回流债务路由 `retrospect`，规则或架构审查路由 `system-review`，已确认规则漂移路由 `system-upgrade`。
- `P0/P1/P2` 表示风险优先级，不是 Pipeline 阶段；同一根因只保留一个 active debt，health 恢复不能自动关闭语义债务。

## 升级记录最小内容

```markdown
### 方案审查结论
- 结论：可执行 / 可执行但有限制 / 暂缓 / 拒绝
- 主要质询：...
- 风险边界：...
- 自动化选择：...
- 历史影响：...
- 未解决问题：...
```

## 关键参考

- `references/work-package-contract.md`
- `references/index-layering-contract.md`
- `references/script-governance.md`
- `references/skill-registry-schema.md`
- `references/runtime-state-machine.md`
- `references/coding-execution-principles.md`
- `references/mainline-only-git-governance.md`
- `references/runtime-artifact-retention.md`
- `references/upgrade-acceptance-gates.md`

## 完成条件

- 最近权威落点、入口和直接依赖一致。
- 新旧状态没有被混写，历史影响已写入唯一升级日志。
- 定向测试与完整 closure 均通过，或未通过项被如实标为 partial/blocked。
- 用户授权了远端操作时，Git 远端一致性已单独核验；否则明确标记为未执行。
