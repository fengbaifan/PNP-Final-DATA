---
name: synthesize
kind: leaf
phase: later
triggers:
  - synthesize
  - 知识发现
  - 涌现分析
description: 用户启动第二部分后，从已有知识及关系中发现新联系与解释，逐级形成研究结构。
---

# synthesize

用户启动第二部分后，从已有知识及关系中发现新联系与解释，逐级形成研究结构。

## 输入

指定研究范围中的有效 KU、关系、claim 与原始证据及各自状态。没有实际知识时不执行；不要求全库所有事项完成。输入可跨来源和任务，用稳定引用关联，不复制知识元。

## 涌现工作

1. KU/关系 → Topic：比较成员间联系、差异、共同问题和反例，说明它们共同呈现了什么单独阅读时不显明的问题或模式。
2. Topic → Theme：比较具体问题之间的联系和张力，形成有边界的问题群与主题。
3. Theme → Dimension：辨认主题之间形成的分析视角，说明解释意义、适用范围及交叉。
4. Dimension → Domain：说明维度如何共同构成较完整的问题体系，界定领域边界。

可以规定这些层次的表达规则，不预定其名称、数量和成员。不能优先维护预设 A–E 或因已有框架难以容纳才允许发现。既有结构也必须接受新证据、反例与替代解释的检验。
聚类/图指标仅辅助定位，Cluster 只是观察线索，不增加必经审批层。不得以共现、密度或数量直接证明 Topic/Theme 成立，也不得从高层标签倒推出原文事实。

## 产出与判断

每项候选或结论说明：问题/新增语义、下层成员及其关系、原始依据、边界与反例、不确定性、成立/暂缓/否决理由。没有候选可记录已审查无新增。
过程在 03-processing/<task-id>/process/knowledge.md，当前结果在 04-knowledge/results/<task-id>.md。成立节点在 04-knowledge/structure 各类目录维护，并在 accepted.yml 登记；不强制同时有上层节点。稳定 ID 不依赖父层编号，允许交叉归属与重组。
证据只支持 Topic 时就停在 Topic，不凑满五层；发现候选和已成立知识分开。输入变化时只重审受影响节点与下游呈现，保留拆分/合并/撤回理由。
缺出处/身份/事实/关系时分别回 ingest、verify、enrich、relate；可呈现内容与限制交 compose。批量结构写回才使用候选 envelope/change-set，普通语义研究不强制生成机器账本。

## 按需直接参考

- `.agents/skills/ingest/references/hierarchy-field.md`：实际形成结构或更新成员时读取字段规则。
- `.agents/skills/system-upgrade/references/work-package-contract.md`：仅批量机器写回或旧接口续接时读取。
