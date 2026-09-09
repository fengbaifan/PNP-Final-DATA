# 脚本治理与规则沉淀规范

本文件回答一个系统问题：
哪些脚本应继续只是脚本，哪些脚本必须回写为 skills / pipeline 的规则、内容、方法、原则或格式？

## 0. Workflow-first 修订

本项目不是脚本工程。脚本治理必须服从仓库级 `.agents/pipeline.md` 路由契约：

```text
Agent / Skill / Pipeline / State Honesty
> scripts
```

脚本不得成为系统主入口，也不得定义知识蒸馏流程。脚本只能在工作流已经由 Skill Contract 定义后，作为受控工具执行机械任务。

系统修订的默认路径是：

```text
阅读现有架构
-> 定位工作流阶段
-> 修订 Skill / reference
-> 记录影响面
-> 必要时使用脚本做辅助状态信号
```

禁止默认路径变成：

```text
修改脚本
-> 生成 health/backlog
-> 反向解释为系统已修订
```

## 一、四类脚本

| 类型 | 特征 | 是否必须沉淀进 skills |
|---|---|---|
| `runtime` | 稳定参与主流程 | 仅沉淀边界与产物，不沉淀为主流程 |
| `governance` | 稳定参与审查、记录、治理 | 仅沉淀辅助信号边界 |
| `repair/backfill` | 一次性或阶段性修复 | 只沉淀方法与边界，不必全文照搬 |
| `legacy/experimental` | 已废弃或仅试验 | 不作为正式规则来源 |

## 二、可能需要沉淀的内容

当脚本确实属于 `runtime` 或 `governance`，且已经证明无法用文本规则和 Agent 工作流完成时，才考虑同步以下内容到 skill 系统：

1. 脚本在 pipeline 中的位置
2. 输入与输出产物
3. 必须遵守的安全规则
4. dry-run / apply 边界
5. 触发条件
6. 日志与状态同步要求

## 三、不必全文迁移的内容

以下内容不应逐行搬进 `SKILL.md`：

- 正则细节
- 临时修复策略
- 一次性 backfill 的实现代码
- 仅用于历史清理的 repair 脚本内部启发式

这些内容若有长期价值，只提炼成：

- 原则
- 方法
- 格式
- 风险边界

## 四、当前脚本治理判断

### 受控辅助工具

以下脚本只能作为受控辅助工具，不能定义知识蒸馏流程：

- `scripts/verify_collect_wikidata.py`
- `scripts/verify_collect_wikipedia.py`
- `scripts/verify_apply_evidence.py`
- `scripts/evidence_batch_runner.py`
- `scripts/audit_repo.py`
- `scripts/write_current_health.py`
- `scripts/generate_governance_backlog.py`
- `scripts/hierarchy_stress_test.py`
- `scripts/audit_system_upgrade_chain.py`

### 只需提炼方法与边界

- `repair_*.py`
- `backfill_*.py`
- `normalize_*.py`

### 不应再作为现行规则依据

- 已完成的一次性 repair/backfill、退役 provider 和 deprecated writer 不留在工作树中。
- 退役实现由 Git 历史和 `06-runtime/governance/system-upgrade-log.md` 保存 provenance，不在工作树建立第二套脚本归档代码库。
- 历史 work package 只保留 evidence、decision、plan、manifest、result 和 summary；一次性 `exact_apply.py`、`repair_*.py` 等批次代码在明确授权清理后由 Git 历史保存，不继续留作可执行入口。
- 如确需恢复旧方法，先从历史提交提取并重新经过权限、状态诚实和现行 schema 审查，不得直接恢复为活跃入口。

### 状态诚实的机械约束

- frontmatter 审计必须复用 BOM-safe 且只识别整行 `---` 分隔符的解析器；不得用任意子串切分。
- 列表输出可以限制 preview，但总量必须先在完整集合上计算并明确标注。
- 已迁移 writer 的默认入口必须 fail-closed；缺失或空输入不得覆盖仍在生效的 registry。
- partial coverage 属于 backlog 与 health 的真实缺口，不能只在覆盖率归零时暴露。
- “latest runtime artifact” 选择器必须发现权威 batch 下的嵌套 final/current ledger，并按外层日期与数字 batch 排序；不得因只扫描顶层文件而回退到旧快照。
- 生成式状态快照必须幂等：语义内容不变时保留原快照时间与文件字节；CI 发布门禁必须使用 `run_sync_closure.py --refresh-generated --full --check-generated` 拒绝未提交漂移。
- 依赖 live KU / relation 状态的 R2 机械投影必须输出 provenance manifest；必须散列每个显式 ledger 输入并聚合完整 KU 状态，且在新批次中使用仓库相对输入路径，避免 checkout 路径破坏重建。
- relation index 的 legacy `related` 与正文链接 fallback 必须服从 `weak_associations` 排除信号；机械重建不得推翻 Agent 已完成的弱关联裁决。
- 确定性内容审计只能报告结构、编码、占位、链接和状态一致性信号；不得用年份、标点数量、正文长度等代理指标裁决语义细节密度、事实充分性或知识价值。语义充分性必须路由到 Agent 复读或审查。
- Git 治理的文本来源指纹必须跨 checkout 稳定：只将 CRLF 规范为 LF 后计算 SHA-256，编码、BOM、孤立 CR 和其他内容变化仍触发漂移；不得把操作系统换行策略误判为来源变更。

## 五、执行要求

当新增或修改稳定脚本后，system-upgrade 应先检查是否真的需要脚本。只有必要时才继续检查：

1. 是否已有对应 skill / references
2. 若无，是否需要新增 references 文档
3. README、AGENTS 索引是否需要同步
4. 是否需要写入 `system-upgrade-log.md`

删除或退役脚本时，还必须同步 `.agents/settings.json`、测试引用、生成投影清单和最近 skill/reference；只删除文件而保留权限或文档入口不算完成。
