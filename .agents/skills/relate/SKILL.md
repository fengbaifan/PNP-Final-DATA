---
name: relate
kind: leaf
phase: current
triggers:
  - relate
  - 关系关联
description: 负责第六阶段的关系分析和正式写回，承接原 lint 中关系与断言证据契约。
---

# relate

负责第六阶段的关系分析和正式写回，承接原 lint 中关系与断言证据契约。

## 输入与执行

读取知识元、对齐/补足结果和相关原始段落。Agent 审查端点是否同一对象、具体 relation_type、方向、时间/语境及证据责任。
正式关系由 KU frontmatter.relations 或 claim bindings 表达；relation-index.yml 是派生投影。受控关系词表来自 ingest/references/relation-types.yml。
共享标签、同章出现、相似度、正文链接、related 和 weak_associations 不自动成为正式关系。不为消除孤点凑边。
关系候选、证据、逐条决定先记录，再形成 exact apply plan 和可审阅 diff，受控写回后记录 applied/no_delta/blocked。同一文件串行；冲突或缺证交给 verify/source review，只回到必要环节。
反向关系仅按受控 inverse 规则生成索引，不反写知识事实，不自动补出间接关系。

## 过程、结果与完成

04-knowledge/process/<id>.md：逐关系分析、来源定位、方向/类型依据及不采纳理由。
04-knowledge/results/<id>.md：正式关系、待证关系、否决关系清单，关联唯一当前 KU/证据文件。无可确认关系是合法结果。
必要时运行 scripts/audit_relation_consistency.py、scripts/build_relation_index.py。正式图谱只包含有证据的关系；建成关系不自动启动 synthesize 或页面制作。

## 按需直接参考

- `references/claim-evidence-governance.md`
- `references/relation-governance.md`

- `.agents/skills/system-upgrade/references/work-package-contract.md`
