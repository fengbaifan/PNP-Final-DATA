# Knowledge Distillation - 按需披露总纲 v5.3.0

本文件是系统权威入口，只保留总纲、边界、优先级与索引。
流程细节、字段清单、模板、异常分支和历史运行记录必须下沉到最近的 skill、reference 或 runtime 索引。

---

## 一、文件角色

- `AGENTS.md`：总纲、架构边界、执行优先级、规则分发表、关键入口。
- `.agents/skills/**/SKILL.md`：技能触发、输入、执行、权限、状态、产物与下一跳。
- `.agents/skills/{05-quality,06-growth,07-output}/README.md`：分类导航，不是可运行 Skill。
- `.agents/skills/**/references/*.md`：共享契约、长 schema/模板或条件分支；不是短规则的默认存放处。
- `.codex/hooks.json`、`.claude/settings.json`、`CLAUDE.md`、`.claude/skills/`：客户端薄适配；只调用共享门禁或链接权威 Skill，不另存语义规则。
- `01-domain/*.md`：taxonomy、命名和 workflow override。
- `06-runtime/automation/index.md`：自动生成的运行批次索引。
- `06-runtime/governance/system-upgrade-log.md`：正式系统升级记录。

### 按需披露规则

1. `AGENTS.md` 只保留摘要规则、决策边界和路径索引。
2. `SKILL.md` 必须足以完成常规路径；不得把每次执行必读的短规则拆成 reference。
3. 只有跨 Skill 共享、篇幅较长、独立版本化或仅在条件分支读取的 schema、模板、枚举和异常规则才下沉。
4. 活跃规则的最大阅读深度为 `AGENTS -> SKILL -> direct reference`；不得用 reference 再引出未在 Skill 直接登记的必读 reference。
5. 短、单一调用方、与 Skill 合并后仍可快速阅读的细则必须并入 `SKILL.md`；Skill 是否独立由触发、权限、状态和产物边界决定，不由行数决定。
6. 系统升级先更新最近权威落点，再同步必要入口；历史 batch 不得逐条追加到 `AGENTS.md` 或 `README.md`。
7. 用户级 AGENTS/CLAUDE 指令和自动记忆只作非权威背景；可变事实必须以当前 checkout、实时检查和带时间戳状态为准，记忆不得授权写入、删除、提交或推送。

---

## 二、三层架构

```text
Layer 3 - Structure Nodes
  domain / dimension / theme / topic
  目录: 04-knowledge/structure/

Layer 2a - Knowledge Units
  person / institution / place / work / publication / term / procedure / event
  目录: 04-knowledge/units/

Layer 2b - Assertion & Evidence
  claim / source / citation / evidence
  目录: 04-knowledge/quality/
```

判断边界：

- 能自然容纳多个 knowledge unit 的对象属于 structure node。
- `claim` 属于断言与证据层，不是 knowledge unit 类型。
- 禁止恢复或新建 `ideas/`、`propositions/`、`arguments/`、`concepts/`、`techniques/`、`cases/`。

---

## 三、系统总原则

1. 中文优先；正式报告、审查结论、治理记录与交付总结默认使用中文。仅代码、路径、字段名、标准名称及无可靠译名的术语保留英文，必要时首次出现附中文说明。
2. workflow-first：中心是 Agent + Skill Contract + Event Routing + State Honesty，不是脚本集合。
3. 来源只读：`02-sources/` 只追加，不改写、不删除。
4. 摄入必须保留覆盖证明；禁止用脚本替代语义阅读。
5. enrich 以网页语义补写为核心，外部链接只是导航锚点。
6. 验证走 `collect -> evidence JSONL -> apply` 两阶段；正式写回入口为 `scripts/verify_apply_evidence.py`。
7. 证据不足必须保留不确定状态，不得伪装成人工确认完成。
8. health、backlog 和脚本输出只是运行信号，不是知识裁决本体。
9. `AGENTS.md` 与 `README.md` 必须与磁盘事实同步。
10. 编码执行遵循最小改动、先读后写、状态诚实和显式验证；细则见 `.agents/skills/00-coordination/system-upgrade/references/coding-execution-principles.md`。
11. Git 采用单主线治理：Codex、VS Code 和命令行均不得创建分支或额外 worktree；只保留 `main`，细则见 `.agents/skills/00-coordination/system-upgrade/references/mainline-only-git-governance.md`。
12. work package 的 evidence、decision、plan、manifest、result 与 summary 默认保留；批次内旧执行器、重复规范和过时快照在明确授权后由 Git 历史保存，不在工作树维护第二套现行系统。细则见 `.agents/skills/00-coordination/system-upgrade/references/runtime-artifact-retention.md`。
13. 生成式状态快照必须幂等；发布门禁使用 `--check-generated` 阻断未提交的索引或状态漂移。
14. `weak_associations` 是正式关系图的排除信号；relation index 的 legacy `related` 与正文链接 fallback 不得将其重新升级为 `relations`。
15. R2 可重建投影必须由 provenance manifest 明确列出，并记录有效输入、生成器、参数、KU 状态摘要与匹配的输出哈希；未列出、缺失或哈希不符时按 R1 保留，窄范围生成态信号另标 `review_required`。
16. 一个用户目标原则上只建立一个 work package；checkpoint 留在包内，机械重复默认自动化，语义裁决不得自动化。
17. 仓库内唯一 Skill 根为 `.agents/skills/`；Skill 角色与触发词必须在无重复键的 frontmatter 显式声明，注册表只作派生快照，并拒绝隐藏的多层 reference。
18. 层级主轴为 `domain -> dimension -> theme -> topic -> KU`；A.1/B.2 等稳定代码现表示 Level 3 theme，Topic 是可研究问题，KU 通过多对多 `topic_memberships` 提供材料。Cluster 是可作用于任意层级的发现候选，不是 structure node，也不得自动晋升层级。
19. compact-v4 必须分开记录 `source_assets` 指纹范围与 `processing_scope` 复读范围；scope 资产须由跨度并集逐行无缺口覆盖，来源漂移自动重开有效摄入状态。`semantic_artifact_integrity` 不替代 Agent 语义验收。
20. 验证写回必须整批预检并原子提交；blocked/failed 不得记 completed。长任务恢复只使用 work package 内状态，并在跳过 processed item 前核对 evidence 指纹。
21. candidate index 同时保留完整 inventory 与派生 `lifecycle_class`；backlog 只统计 active，不把 terminal 或 historical non-replay 伪装为待办。
22. Markdown guard 只解释治理边界；Codex 与 Claude Code 的硬阻断统一由 `scripts/agent_guard.py` 执行，且只有客户端识别并信任 Hook 后才算生效。
23. commit、push 等外部状态变更必须由用户明确授权；Skill、历史惯例和自动记忆不能替代当次授权。

---

## 四、规则分发

| 规则主题 | 权威落点 |
|---|---|
| 摄入流程与覆盖证明 | `.agents/skills/01-intake/ingest/SKILL.md` |
| 系统契约 | `.agents/skills/01-intake/ingest/references/distillation-system-contract.md` |
| KU 字段与存储 | `.agents/skills/01-intake/ingest/references/knowledge-unit-field-contract.md` |
| taxonomy | `.agents/skills/01-intake/ingest/references/taxonomy.md` |
| 层级字段 | `.agents/skills/01-intake/ingest/references/hierarchy-field.md` |
| relation 治理 | `.agents/skills/01-intake/ingest/references/relation-types.md`；`.agents/skills/05-quality/lint/references/relation-governance.md` |
| claim / evidence 治理 | `.agents/skills/05-quality/lint/references/claim-evidence-governance.md` |
| 验证级联 | `.agents/skills/03-verification/verify/references/` |
| 编码执行与升级 | `.agents/skills/00-coordination/system-upgrade/references/` |
| Git 单主线治理 | `.agents/skills/00-coordination/system-upgrade/references/mainline-only-git-governance.md` |
| 运行工件保留治理 | `.agents/skills/00-coordination/system-upgrade/references/runtime-artifact-retention.md` |
| 批次状态边界 | `.agents/skills/00-coordination/system-upgrade/references/runtime-state-machine.md` |
| 领域规则 | `01-domain/` |
| Domain 演化 | `01-domain/domain-registry.md` |
| 自动化风险语义 | `.agents/guards/automation-risk-policy.md` |
| 客户端硬门禁 | `scripts/agent_guard.py`；`.codex/hooks.json`；`.claude/settings.json` |
| 运行状态 | `06-runtime/README.md` |

---

## 五、执行优先级

1. `AGENTS.md`
2. `01-domain/taxonomy-registry.md`
3. `01-domain/workflow-overrides.md`
4. `01-domain/naming-conventions.md`
5. `.agents/guards/`
6. `scripts/agent_guard.py` 的确定性阻断结果
7. 对应 skill 的 `SKILL.md`
8. 对应 skill 的 `references/*.md`
9. `README.md` 与其他导航文档

---

## 六、关键入口

### Workflow Router

- `.agents/pipeline.md`
- `.agents/guards/automation-risk-policy.md`
- `scripts/agent_guard.py`；`.codex/hooks.json`；`.claude/settings.json`

### Domain

- `01-domain/taxonomy-registry.md`
- `01-domain/domain-registry.md`
- `01-domain/workflow-overrides.md`
- `01-domain/naming-conventions.md`

### Skills

- `.agents/skills/01-intake/ingest/SKILL.md`
- `.agents/skills/03-verification/verify/SKILL.md`
- `.agents/skills/05-quality/README.md`
- `.agents/skills/06-growth/README.md`
- `.agents/skills/07-output/README.md`
- `.agents/skills/08-inspection/inspector/SKILL.md`
- `.agents/skills/08-inspection/system-review/SKILL.md`

### Governance

- `06-runtime/automation/index.md`
- `06-runtime/state/current-health.json`
- `06-runtime/governance/governance-backlog.md`
- `06-runtime/governance/system-upgrade-log.md`

---

## 七、版本说明

- 当前版本：v5.3.0（2026-08-07）
- 本次修订：增加 Codex/Claude 项目适配与共享可执行门禁；合并重叠的 review/sys-audit，移除 inspection router；收紧记忆、外部写入和 Skill 路由边界。
- 完整升级记录：`06-runtime/governance/system-upgrade-log.md`
