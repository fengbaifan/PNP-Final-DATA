---
name: relate
kind: leaf
phase: current
triggers:
  - relate
  - 关系关联
description: 负责阶段 6 的关系分析，形成可追溯的正式关系与图谱。
---

# relate

负责阶段 6 的关系分析，形成可追溯的正式关系与图谱。

## 输入与工作

读取本次有效 KU、对齐/补足结果及原始段落；判断端点、relation_type、方向、时间/语境和支持该关系的证据。词表见 `.agents/skills/ingest/references/relation-types.yml`，不能为填词表或消除孤点制造边。
同章共现、相似度、标签、正文链接、related、weak_associations 只是线索，不能自动转为正式关系；间接路径不直接成为事实关系。

## 产出与交接

03-processing/<task-id>/process/knowledge.md 保存判断理由与来源；04-knowledge/results/<task-id>.md 列正式、待证、否决关系和未解决问题。正式断言仅在 KU frontmatter.relations 或 claim bindings 维护，relation-index.yml 为派生索引；卡内按 ingest 正文模板展示可点击的关联知识元及对应语境，不用“见元数据”代替可读结果。
单对象编辑直接原位更新并检查证据、端点和方向；批量机器写回使用 exact apply plan、dry-run diff 及适用执行接口，同一文件串行，实际结果记 applied/no_delta/blocked。反向边仅按词表规则投影，不反写新事实。
身份有误回 verify，原文/覆盖不足回 ingest，具体缺口回 enrich。无可成立关系是合法结果；第一部分到此交付，不自动启动发现或页面制作。

## 按需直接参考

- `.agents/skills/ingest/references/body-template.md`：关系的阅读展示与内容关联边界；修改正式关系时同步受影响展示。
- `references/claim-evidence-governance.md`
- `references/relation-governance.md`
- `.agents/skills/system-upgrade/references/work-package-contract.md`
