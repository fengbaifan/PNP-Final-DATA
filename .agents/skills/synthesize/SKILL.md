---
name: synthesize
kind: leaf
phase: later
triggers:
  - synthesize
  - 知识发现
  - 涌现分析
description: 第二部分的知识发现、结构与主题涌现及结构演化技能。用户明确启动后才执行；初期知识元/关系变化不触发。
---

# synthesize

第二部分的知识发现、结构与主题涌现及结构演化技能。用户明确启动后才执行；初期知识元/关系变化不触发。

## 输入与分析

读取已有知识元、关系和证据，以及本次研究问题。原 query 的检索可直接在文件中完成；原 retrospect 的输出回看纳入本 Skill，不设独立自动循环。
Agent 比较跨对象模式、差异、断裂、反例和来源独立性；图指标或聚类只能辅助定位，不决定发现成立。
发现进入统一 candidate envelope，明确 supporting units/claims/relations/sources、边界、反例、不确定性。无候选时记录 reviewed_no_candidates，不创建空账本。
Cluster 是发现信号，不是 structure node；target_level、scope、basis、input_snapshot、members、boundary、counterexamples、stability_across_runs 按 work-package 契约记录。

## 涌现与结构演化

沿用 domain → dimension → theme → topic → KU，Level 3 theme 与具体可研究 Topic 分开，topic_memberships 支持多对多材料归属。
先判断现有 Topic 能否承载，再讨论 Topic/Theme，只有现有结构确实无法解释时考虑 Dimension/Domain。没有固定数量自动晋升规则。
逐项记录 evidence、boundary test、hierarchy impact、迁移映射与未解决项。经语义审查后按具体 change-set 更新 structure 和 membership；保留 ID/历史证据，不自动分类或覆盖未决冲突。
上述职责吸收原 evolve-hierarchy 与 build-hierarchy，不再调用并行技能链。

## 输出

过程与结果分别记录于 04-knowledge/process/<id>.md、04-knowledge/results/<id>.md；正式结构仅写入 structure，候选不冒充成熟知识。
后续呈现交给 compose，原始发现证据仍链接到本处，不复制到输出层。

- `.agents/skills/system-upgrade/references/work-package-contract.md`
