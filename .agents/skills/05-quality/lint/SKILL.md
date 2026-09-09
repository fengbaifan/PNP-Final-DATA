---
name: lint
kind: leaf
triggers:
  - lint
  - lint-frontmatter
  - 结构检查
  - frontmatter检查
description: >
  知识库确定性结构检查技能。检查 schema、命名、链接、索引和关系/断言结构，
  只输出机械发现与修复队列，不执行置信度裁决、enrich 或 output 回溯。
---

# lint

## 输入

- `04-knowledge/units/`、`04-knowledge/structure/` 与 `04-knowledge/quality/`。
- 当前 taxonomy、字段、relation 与 claim/evidence 契约。
- 用户指定的文件、目录或检查范围；未指定时使用与变化集相邻的最小范围。

## 检查

1. frontmatter 是否可解析，必填字段、枚举、类型与目录是否一致。
2. 文件名、内部链接、索引和 hierarchy 引用是否有效。
3. 空页面、明显占位内容、孤立对象和断链是否存在。
4. relation、claim 与 evidence 的结构是否满足各自契约。
5. 把确定性问题、研究债务和需要语义审查的问题分开报告。

## 输出

- 可复现的结构检查结果；
- 可机械修复项与需要 Agent 审查项的分离队列；
- 已运行和未运行检查的明确说明。

## 边界

- 不定义或执行 `audit-confidence`。
- 不自动触发 `enrich`、`verify`、`retrospect` 或任何知识写回。
- 不压缩、改写或汇总历史日志。
- 不以目标比例判断知识成熟度，不自动修改 `confidence`、`consensus` 或验证状态。
- 修复任务只有在用户授权后才进入相应 Skill 或 `system-upgrade`。

## 参考

- `references/relation-governance.md`
- `references/claim-evidence-governance.md`
