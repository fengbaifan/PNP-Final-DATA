---
name: system-review
kind: leaf
triggers:
  - system-review
  - 规则审查
  - 系统审查
  - 架构审查
description: >
  系统规则与架构审查技能。用户要求规则合规、实现审查、系统审查或架构审查时使用；
  以 compliance 或 architecture 模式输出可定位 findings，不修改规则或知识。
---

# system-review

## 模式选择

- `compliance`：判断实现、数据和记录是否遵守现行规则。
- `architecture`：判断工作流闭环、恢复能力、扩展性和权威层是否自洽。
- 请求同时涉及两者时共用一次取证，只在 findings 中标注所属模式，不重复执行两套审查。

`inspector` 只报告当前状态和下一边界；本 Skill 解释规则或架构缺口。编码、单文档覆盖和置信度专项问题分别交给 `encoding-check`、`read-full` 和 `audit-confidence`。

## 权威输入

- `AGENTS.md`、`README.md`、`.agents/pipeline.md` 和相关 `SKILL.md`；
- `scripts/audit_repo.py`、直接相关的执行器和测试；
- `06-runtime/state/current-health.json` 与治理 backlog，作为有时间戳的机器信号；
- 被审查对象的直接调用方、依赖、工件和 Git 差异。

只读取与请求和发现直接相关的 references，不把全库 reference 复读作为固定步骤。

## 共享流程

1. 明确请求、成功标准、排除范围和审查模式。
2. 读取最近权威规则、当前状态和目标实现，区分实时事实与历史快照。
3. 运行或复核最近邻只读检查；无法运行的检查必须单列。
4. 抽样验证脚本输出、状态和磁盘事实是否一致。
5. 仅报告可落到文件、流程或规则点的 findings，按严重度排序。
6. 用户确认采纳后才路由 `system-upgrade`；本 Skill 不直接写回。

## Compliance 检查

- schema、枚举、目录、链接和 frontmatter 是否满足契约；
- collect/apply、candidate/knowledge、health/semantic acceptance 是否越层；
- `02-sources/` 只追加、验证原子写回、状态诚实等不变量是否实际成立；
- 实现是否保持最小范围、覆盖直接依赖并运行能捕获回归的验证；
- Git、临时工件、失败和跳过项是否诚实记录。

## Architecture 检查

- source -> processing -> candidate -> typed write-back -> knowledge -> output/file-back 是否闭环；
- 状态机、索引、当前投影与不可替代 provenance 的权威关系是否清晰；
- 机械自动化是否可重建，语义裁决是否仍由 Agent 承担；
- 恢复、并发、规模扩展和跨客户端配置是否有确定性边界；
- `AGENTS.md`、README、Skill、Hook 和脚本是否对同一行为给出一致说法。

## 输出

```markdown
## System Review — YYYY-MM-DD

### Findings
1. [严重][compliance|architecture] <事实、影响、证据位置>

### Unverified
- <未运行检查或无法确认的边界>

### Recommended Changes
- <按优先级排序，不冒充已实施>
```

无 findings 是合法结果，但必须说明已审查范围。未经确认不得把建议记为 implemented，也不得自动修改规则、知识或运行状态。

## 参考

- `../../00-coordination/system-upgrade/references/coding-execution-principles.md`
