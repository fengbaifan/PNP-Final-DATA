# 涌现结构与归属字段

第一部分不填写预设层级。生成方向为 KU 及关系 → Topic → Theme → Dimension → Domain；展示可反向导航。每个具体节点必须有下层成员、关系依据、新增语义、边界和不确定性。

## 稳定对象

结构文件位于 structure/topics、themes、dimensions、domains，node_type 分别为 topic、theme、dimension、domain。使用稳定 slug，不由上层编码计算身份。具体问题、名称、数量和归属事先不设定。
节点只有在语义判断成立后才在 accepted.yml 登记；父层未形成合法。不要要求 Topic 创建时已有 Theme、Dimension 和 Domain。

```yaml
node_type: topic
title: 实际形成的问题表述
members:
  - ref: 04-knowledge/units/实际类型/实际对象.md
    role: supporting_case
basis: 说明成员联系以及共同呈现的意义
```

示例中的占位符不能直接写入成果。Theme 引用实际 Topic，Dimension 引用实际 Theme，Domain 引用实际 Dimension；过程/证据以稳定链接追溯。

## 归属与兼容导航

topic_memberships 支持同一 KU 以不同 role 支持多个 Topic，不设排他 parent_topic。主导航字段 primary_theme、primary_dimension、primary_domain 及 secondary_* 只有真实节点存在且已判断归属时才写，不决定事实或发现方向。
既有 theme_code/dimension_code/code 只作稳定兼容标识，不要求 A.1 或 B.7 格式。role 可描述支撑、反例、边界案例等真实角色，不以角色标签证明关系。

拆分、合并、改名或撤回时保存原 ID 与映射依据，标记受影响下游待复核。新结构可以跨越已有边界，不以先适配旧结构为前提。不得按标签、相似度、文件名或共现自动回填。
