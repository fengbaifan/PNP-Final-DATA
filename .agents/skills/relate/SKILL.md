---
name: relate
kind: leaf
phase: current
triggers:
  - relate
  - 关系关联
description: 负责 S6 关系；产物 `relations.csv`。逐候选裁决 formal/pending/rejected；主客体类型过 `relation-domain-range.yml`；缺端点写 backlog，不回知识元。
---

# relate

负责 S6 关系；产物 `relations.csv`。逐候选裁决 formal/pending/rejected；主客体类型过 `relation-domain-range.yml`；缺端点写 backlog，不回知识元。

## 输入与工作

输入：`ku-manifest.csv`；`book-statements.jsonl` 中的原书关系候选；`enrichment.jsonl` 中的外部关系候选；`candidate-backlog.csv`。
输出 `relations.csv`：每个候选裁决为 formal/pending/rejected；每条 formal 至少有一条证据；写入前按自然键（主语、谓词、宾语、限定）查重。

读取本次有效KU、原文及外部关系候选、对齐/补足结果；逐项交叉核对候选、卡内已采纳事实和现有`relations`，判断端点、relation_type、方向、时间／语境和支持该关系的具体证据。每个候选须形成正式、待证或否决去向；候选锚点提供判断追踪，不能单独代替事实证据。还要反查正文中的作品清单、履历、师承、合作、朋友、赞助、亲缘、家庭／家族成员、任职／隶属、创作、委托、所有权、安置及存放事实，避免候选记录本身的遗漏被掩盖。
具名且可独立识别的关系端点没有 KU 时，记入 `candidate-backlog.csv`，按 pipeline 的 backlog 规则批量执行 S1→S3→S4；相关关系保持 pending，不立即回环，也不递归接收其全部关联。师承、合作、朋友、赞助、亲缘、成员／雇佣、创作、委托、收藏所有权、机构保管、原定或历史安置分别表达，不能长期依赖 `associated_*` 的说明文字混合角色。时间、版本、地点角色和争议随边保留；同一对象不因先后馆藏变化生成互相覆盖的无时间位置事实。
同章共现、相似度、标签、正文链接、related、weak_associations 只是线索，不能自动转为正式关系；间接路径不直接成为事实关系。

## 产出与交接

03-processing/<task-id>/process/knowledge.md 引用候选锚点，保存端点映射、判断理由与来源；04-knowledge/results/<task-id>.md 列正式、待证、否决关系和未解决问题。原书与外部事实按具体 evidence locator 或 claim 证据分别归源；`origin` 与 `relation_source` 只描述事实来源，不能解释为“原书明确记载”。关系表记录写入 `relations.csv`，并由 CSV-backed renderer 生成卡片关系视图。既有 frontmatter.relations 暂作迁移对照，未完成预览审阅与获准写回前不删除。
关系裁决写入 `relations.csv`，随后检查来源、端点、方向、限定与域值域。旧 `apply_relation_plan.py --apply` 只写卡片 frontmatter，迁移期间已禁用；关系预览用 `build_cards.py --preview --ku <ku_id>`，在批量渲染获准前不写卡片。反向边仅按词表规则投影，不反写新事实。
身份有误回 verify，原文/覆盖不足回 ingest，具体缺口回 enrich。无可成立关系是合法结果；第一部分到此交付，不自动启动发现或页面制作。

## 按需直接参考

- `.agents/skills/ingest/references/body-template.md`：关系的阅读展示与内容关联边界；修改正式关系时同步受影响展示。
- `references/claim-evidence-governance.md`
- `references/relation-governance.md`
- `.agents/skills/system-upgrade/references/work-package-contract.md`
