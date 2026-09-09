# Domain Registry — 领域演化注册规则

Domain 是五级主干的 Level 1，总结一套能够独立提出问题、组织分析维度并持续吸收来源的研究领域。当前 materialize 的 Domain 为“《赞助人与画家》：巴洛克时期意大利艺术与社会”，处于 `pilot` 状态，首次全量摄入后复核晋升。

## 一、层级关系

```text
Domain -> Dimension -> Theme -> Topic -> KU
```

- Domain 定义总问题域和纳入/排除边界。
- 一个 Domain 必须能够稳定组织多个 Dimension。
- 跨 Domain 的 KU 或 Topic 使用关系与辅助归属表达，不复制知识元。

## 二、Domain Candidate 条件

只有同时满足以下条件，才可提出新 Domain：

1. 新知识无法在不稀释现有 Domain 边界的情况下自然归入；
2. 已形成独立核心研究问题，而不只是一个新 Theme 或 Dimension；
3. 能稳定组织至少 2 个 Dimension，每个 Dimension 已有 Theme、Topic 与 KU/claim/evidence 支撑；
4. 得到多个独立来源持续支持，并通过反例与边界测试；
5. 已说明与现有 Domain 的重叠、迁移、跨域关系和查询价值。

Cluster 密度、共享标签或来源数量只能召回 Domain Candidate，不能自动创建 Domain。

## 三、生命周期

```text
candidate -> needs_evidence -> ready_for_review -> approved
         -> pilot -> active | merged | split | deprecated
```

审批与结构迁移由 `evolve-hierarchy` 执行。历史 Domain 标识必须保留映射，KU 不因 Domain 调整而复制。

## 四、当前 Domain

| slug | 名称 | 状态 |
|---|---|---|
| `patrons-and-painters` | 《赞助人与画家》：巴洛克时期意大利艺术与社会 | pilot |

晋升条件：完成首次全量摄入、5 个 pilot 维度经重评后至少 3 个晋升 `core`，且 Domain 边界通过反例与边界测试（由 `evolve-hierarchy` 记录 evidence 与 unresolved items）。

## 五、变更记录

- 2026-09-09：新领域初始化。废弃旧领域 `information-visualization-history-and-theory`（信息可视化的历史与理论，active，旧项目历史状态不随迁），新建 `patrons-and-painters` 并标为 `pilot`。
