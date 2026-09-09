# Infographic Knowledge Distillation

信息图表史知识蒸馏系统。仓库采用结构节点、知识元、断言与证据三层架构，并以工作流优先、证据可追溯和状态诚实为执行边界。

> 当前版本：v5.3.0（2026-08-07） | 结构健康、层级挂载与知识成熟度以 `06-runtime/state/current-health.json` 为准 | 运行批次导航见 `06-runtime/automation/index.md`

---

## 先看哪里

| 入口 | 路径 |
|---|---|
| 权威总纲 | `AGENTS.md` |
| 工作流路由 | `.agents/pipeline.md` |
| 自动化风险语义 | `.agents/guards/automation-risk-policy.md` |
| 可执行安全门禁 | `scripts/agent_guard.py`；`.codex/hooks.json`；`.claude/settings.json` |
| Skill 导航与契约 | `.agents/skills/`（18 leaf） |
| 领域覆盖规则 | `01-domain/workflow-overrides.md` |
| 摄入契约 | `.agents/skills/01-intake/ingest/references/distillation-system-contract.md` |
| KU 字段与存储规范 | `.agents/skills/01-intake/ingest/references/knowledge-unit-field-contract.md` |
| relation 治理 | `.agents/skills/05-quality/lint/references/relation-governance.md` |
| claim / evidence 治理 | `.agents/skills/05-quality/lint/references/claim-evidence-governance.md` |
| 当前机器状态 | `06-runtime/state/current-health.json` |
| 治理待办 | `06-runtime/governance/governance-backlog.md` |
| 运行批次索引 | `06-runtime/automation/index.md` |
| 运行工件保留策略 | `.agents/skills/00-coordination/system-upgrade/references/runtime-artifact-retention.md` |
| 系统升级日志 | `06-runtime/governance/system-upgrade-log.md` |

历史 automation 只保留 evidence、decision、plan、manifest、result 和 summary，不保留可误作现行入口的一次性 writer。R2 只有在 manifest 明确列出输出且哈希匹配时才成立；inventory/summary 默认按 R1 provenance 保留。

---

## 三层架构

```text
Layer 3 - Structure Nodes
  domains / dimensions / themes / topics
  目录: 04-knowledge/structure/

Layer 2a - Knowledge Units
  persons / institutions / places / works / publications
  terms / procedures / events
  目录: 04-knowledge/units/

Layer 2b - Assertion & Evidence
  claim-registry.yml / relation-index.yml
  目录: 04-knowledge/quality/
```

`claim` 不是 knowledge unit。structure node 用于组织多个知识元，不得与知识元类型混写。

层级主轴是 `domain -> dimension -> theme -> topic -> KU`。Theme 是必要的 Level 3 问题群，Topic 是具体研究问题，KU 以多对多 membership 提供材料。Cluster 可扫描 KU、Topic、Theme、Dimension 或 Domain，但只作为发现候选，不进入正式层级；当前 A–E 是五个 Level 2 维度，不是五个领域。

---

## 目录结构

```text
AGENTS.md                 权威总纲
CLAUDE.md                 Claude Code 对 AGENTS.md 的薄适配入口
.agents/                  workflow router、guards 和唯一 Skill 语义根
.codex/                   Codex 项目 Hook 配置
.claude/                  Claude Code Hook 与 Skill 发现适配
01-domain/                taxonomy、dimension、workflow 和命名规则
02-sources/               只读来源
03-processing/            摄入覆盖证明与处理中间产物
04-knowledge/             units、structure、quality 和 hierarchy
05-outputs/               查询、写作和展示输出
06-runtime/               当前派生状态、治理、work package 与评测
scripts/                  受控机械执行器
tests/                    自动化回归测试
```

---

## 工作流

```text
生产：source -> semantic processing -> candidate decision -> typed write-back -> knowledge
成长：knowledge/output/external signal -> discovery -> candidate -> typed write-back
治理：targeted check -> risk gate -> final closeout
```

任务按事件进入相关 Skill，不要求依次跑完固定阶段。候选决策必须筛查现有对象、重复与冲突；完整冲突裁决只在命中冲突信号时运行。Agent 负责语义阅读和裁决；脚本负责索引、校验、dry-run、状态刷新及已批准的机械写回。
仓库内只保留 `.agents/skills/` 一个 Skill 语义权威根；`.claude/skills/` 只含指向权威目录的 Git symlink。Windows 在 `core.symlinks=false` 时可能把它们物化为相对路径 stub，仓库审计只验证目标声明，不能据此声称 Claude 运行时已经发现 Skill。分类 README 只做导航，不能被当作可运行 Skill。常规执行规则直接写在 `SKILL.md`，只有共享、长篇或条件性契约才使用 direct reference，不允许隐藏的二次跳转。

Markdown guards 说明风险语义；Codex 和 Claude Code 的项目 Hook 统一调用 `scripts/agent_guard.py` 执行硬阻断。首次使用时必须在客户端确认项目与 Hook 已被信任；未检查实际加载状态时，不得把配置文件存在解释成门禁已运行。

---

## 常用命令

首次克隆后，先建立受管 Python 环境。项目要求 Python 3.10 或更高版本；完整验收还需要开发依赖。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

```bash
# 快速审计（结构健康与知识成熟度分开报告）
python scripts/audit_repo.py --summary

# 生成紧凑运行索引
python scripts/build_runtime_index.py

# 默认按 Git 变化集合运行最近邻只读门禁
python scripts/run_sync_closure.py

# 需要刷新生成投影时显式执行；每个工作包最多一次
python scripts/run_sync_closure.py --refresh-generated --full --check-generated

# 单主线同步检查
git fetch origin main
git rev-list --left-right --count origin/main...main

# evidence 批次机械编排，不替代语义判断
python scripts/evidence_batch_runner.py --batch-manifest <manifest.json>
```

正式验证写回必须走：

```text
collect -> evidence JSONL -> scripts/verify_apply_evidence.py --apply
```

禁止脚本自动提升 confidence、consensus 或 verification 状态，禁止用机械信号替代语义裁决。

Git 只保留 `main`。Codex、VS Code 和命令行均不得创建功能分支或额外 worktree；提交前门禁会拒绝单主线漂移。
