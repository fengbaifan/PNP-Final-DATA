# Domain Workflow Overrides

本文件只保存“信息可视化史与信息图表史”实例的领域级覆盖规则。通用 workflow、编码执行、system-upgrade 与 Git 规则分别由 `.agents/pipeline.md`、相关 Skill 和治理 reference 定义，不在这里复制。

## 一、对象与层级

1. 当前基础对象为 8 类 KU、4 类 structure node 与 assertion/evidence 层；能用 `sub_type` 表达的问题不晋升为新类型。
2. canonical hierarchy 为 `domain -> dimension -> theme -> topic -> KU`。
3. 当前 Level 1 是“信息可视化的历史与理论”；A–E 是 Level 2 维度，不是五个 domain。
4. A.1/B.2 等稳定代码是 Level 3 Theme；Topic 是可研究问题，KU 可以通过多个 `topic_memberships` 支持多个 Topic。
5. Cluster 是带 `target_level`、`scope` 与 `basis` 的发现候选，可以跨任意层级，但不是 structure node。
6. 新 KU 或重构 KU 必须能映射完整五级字段；历史 KU 只能通过语义分批审查回填。

## 二、候选与冲突

1. 新来源使用 compact-v4；历史 legacy 包只读保留，不作为新任务模板。
2. 每个候选必须检索现有 KU、claim、relation 和权威索引，识别既有目标、潜在重复与潜在冲突。
3. 重复/冲突筛查是候选决策的一部分；完整 `reconcile` 仅由可复现冲突信号触发。
4. 无法归类的对象进入 type、dimension、topic 或其他相应候选账本，不得直接扩张正式 taxonomy。

## 三、维度演化

1. 先判断新知识是否可由现有 Topic 承载，再考虑新增 Topic；多个 Topic 形成稳定问题群时新增 Theme，最后才考虑新增 Dimension 或 Domain。
2. 新维度候选至少需要 5 个不可归类 KU，或至少 2 个长期跨 Theme 且无法由现有结构解释的成熟 Theme。
3. 新维度至少能稳定组织 2 个 Theme；每个 Theme 至少具有可操作 Topic 与可审查 KU/claim/evidence 支撑。
4. 正式变更必须记录 evidence、boundary test、hierarchy impact、迁移映射和 unresolved items。

## 四、状态诚实

1. health、backlog、hooks 与脚本输出只是运行信号，不替代语义阅读、类型判断、冲突裁决或层级挂载。
2. 覆盖证明、候选决策、正式写回、知识成熟度和 output file-back 必须分别记录。
3. 当前层级挂载缺口是研究债务；不得用自动分类或健康满分掩盖。
