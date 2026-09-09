# 《赞助人与画家》知识蒸馏系统

**Patrons and Painters Knowledge Distillation** — 以 Francis Haskell《Patrons and Painters》（Yale University Press, 1980 修订版）为核心来源的证据可追溯知识蒸馏系统，研究巴洛克时期意大利艺术与社会。

## 系统概述

按任务事件进入生产、成长与治理三条循环：来源语义处理 → 候选决策 → 类型化写回 → 知识库；已有知识、外部研究与输出可触发新候选。Agent 负责语义判断，脚本负责机械检查与受控执行。现行路由见 `.agents/pipeline.md`。

- **权威入口**：`AGENTS.md`（总纲、边界、优先级与索引）
- **领域配置**：`01-domain/`（当前领域：《赞助人与画家》；A–E 五个 pilot 维度）
- **核心来源**：`02-sources/`（23 个章节 PDF + 79 个 OCR Markdown + 三格式索引）
- **18 个 Skills**：`.agents/skills/` 为唯一语义权威；`.claude/skills/` 仅作扁平发现链接
- **客户端门禁**：`scripts/agent_guard.py`（Codex/Claude Hook 硬阻断）

## 目录结构

```
01-domain/      领域配置（taxonomy / domain / dimension / overrides / naming）
02-sources/     原始来源（来源本体只追加；顶层登记文件可更新）
03-processing/  处理中间层（compact-v4 工作包）
04-knowledge/   知识库（units 8 类 / structure 4 类 / quality 断言与证据）
05-outputs/     输出产物（知识图谱 HTML、导出、草稿）
06-runtime/     运行状态（health、governance、automation、checkpoints）
scripts/        执行脚本（audit_/build_/collect_/validate_/apply_ 前缀权限表见 01-domain/naming-conventions.md）
tests/          回归测试
portable/       便携测试入口
```

## 全书结构（正文 17 章，三部）

- **Part I — Rome**（第 1–6 章）：赞助机制 / 乌尔班八世及其随从 / 修会 / 私人赞助人 / 更广泛的公众 / 罗马赞助的衰落
- **Part II — Dispersal**（第 7–8 章）：欧洲的介入 / 外省景象
- **Part III — Venice**（第 9–17 章）：国家贵族与教会 / 外国影响 / 外国侨民 / 启蒙运动 / 出版商与鉴赏家 / 弗朗切斯科·阿尔加罗蒂 / 新方向 / 画商与小资产阶级 / 最后的赞助人
- **书后材料**：结论 / 附录 / 第二版后记 / 参考书目 / 索引

详见 `02-sources/source-registry.md`。

## 当前状态

- 当前版本：v5.3.0
- 新领域初始化：2026-09-09。A–E 五个维度为 `pilot` 起始框架，首次全量摄入后经 `evolve-hierarchy` 重评晋升 `core`。
- 第一章试点已形成 10 个知识元与 5 个断言登记；候选账本仍为 approved。外部验证、Theme/Topic 挂载及写回状态收口仍待处理；同步检查不替代语义验收。
- 语言约定：KU 正文中文为主，人名/书名/术语附英文原文；引文保留英文原文（见 `01-domain/workflow-overrides.md`）。
- 旧领域（信息图表史）的任何数量、分数与验收结论均不随迁。

## 快速开始

```powershell
# 机械校验（只读）
python scripts\audit_repo.py --summary
python scripts\skill_registry.py

# 处理包校验（compact-v4）
python scripts\validate_processing_package.py 03-processing\<doc-id>

# 整体验收（依赖 Git 与领域结构，需先完成初始化）
python scripts\run_sync_closure.py --refresh-generated --full --check-generated

# 测试
python -X utf8 -B portable\run_tests.py
```

## 治理要点

- 单主线 Git：只保留 `main`，不创建分支或额外 worktree（细则见 `.agents/skills/00-coordination/system-upgrade/references/mainline-only-git-governance.md`）。
- commit、push 等外部状态变更必须由用户明确授权。
- `02-sources/` 来源本体只追加（顶层登记文件可更新、不可删除）；摄入必须保留覆盖证明；证据不足保留不确定状态。
- 健康分数、backlog 与脚本输出只是运行信号，不是知识裁决本体。
