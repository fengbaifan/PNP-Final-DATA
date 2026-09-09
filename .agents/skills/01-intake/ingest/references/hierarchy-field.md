# hierarchy 字段规范 v2.0

## 一、五级主干

```text
Domain -> Dimension -> Theme -> Topic -> KU
```

- Domain 是总问题域，可以随证据增长新增、拆分或合并。
- Dimension 是 Domain 内的分析轴。
- Theme 是必要的 Level 3 稳定问题群；A.1/B.2 等历史稳定代码迁移到本层。
- Topic 是 Level 4 可研究、可回答的问题，必须 materialize 为 `structure/topics/*.md`。
- KU 是 Level 5 原子知识材料；同一 KU 可用不同 role 支持多个 Topic。

Cluster 不属于主干。它是可作用于任意层级的 discovery candidate，不写入 `04-knowledge/structure/`。

## 二、KU 顶层字段

```yaml
primary_domain: patrons-and-painters
secondary_domains: []
primary_dimension: A
secondary_dimensions: []
primary_theme: A.2
secondary_themes: []
role_in_theme: representative_work
topic_memberships:
  - topic: topics/commission-contracts-rome.md
    role: representative_work
    primary: true
    scope_note: "该作品用于检验十七世纪罗马委托合同的条款惯例。"
hierarchy_scope_note: "A.2 提供主导航；该 KU 仍可在其他 Topic 中承担不同角色。"
```

以上字段必须位于 frontmatter 顶层。`topic_memberships` 是多对多关系，不得压缩为一个排他性的 `parent_topic`。

## 三、字段语义

| 字段 | 类型 | 说明 |
|---|---|---|
| `primary_domain` | string | 主导航 Domain slug |
| `secondary_domains` | list | 跨 Domain 辅助归属 |
| `primary_dimension` | string | 主导航 Dimension code |
| `secondary_dimensions` | list | 其他分析维度 |
| `primary_theme` | string | Level 3 Theme code，例如 `B.7` |
| `secondary_themes` | list | 其他 Theme code |
| `role_in_theme` | enum | KU 在主 Theme 中的宽层角色；历史 `role_in_parent` 迁移到此字段 |
| `topic_memberships` | list<object> | KU 支持的一个或多个 materialized Topic 及逐项 role |
| `hierarchy_scope_note` | string | 主导航选择、跨层边界和未解决项 |

Topic 文件必须声明：

```yaml
node_type: topic
primary_domain: information-visualization-history-and-theory
primary_dimension: B
parent_theme: B.7
secondary_themes: []
```

Theme 文件必须声明 `node_type: theme`、唯一 `theme_code`、`primary_domain` 与 `primary_dimension`。关系执行器通过 `theme_code` 解析 materialized Theme 文件，不把代码拼接成虚假路径。

## 四、role 受控词表

`role_in_theme` 与每个 `topic_memberships[].role` 共用以下词表：

| 值 | 含义 |
|---|---|
| `term_anchor` | 核心术语 |
| `representative_work` | 代表作品 |
| `key_person` | 关键人物 |
| `key_institution` | 关键机构 |
| `geographical_context` | 地理上下文 |
| `source_publication` | 来源出版物 |
| `procedure` | 操作规程 |
| `evidence_event` | 证据事件 |
| `historical_context` | 历史上下文 |
| `counterexample` | 反例 |
| `boundary_case` | 边界案例 |
| `supporting_source` | 支撑来源 |
| `contested_claim` | 争议断言的载体 |

## 五、完整性与迁移

- 完整五级挂载要求三个主导航字段和至少一个同时含 `topic`、`role` 的 membership。
- `primary_theme` 只证明 KU 已映射到问题群，不证明 Topic 语义审查完成。
- 旧 `primary_topic: A.1/B.2` 机械迁移为 `primary_theme`；旧 `role_in_parent` 迁移为 `role_in_theme`。
- 旧 `parent_theme`、`parent_cluster` 空字段停止使用；不得从旧空字段推断任何归属。
- 历史 KU 的 Topic membership 必须逐对象语义审查，不得按 tag、Cluster、文件名或共现自动回填。
- Topic、Theme 或 KU 名称相同且边界相同视为重复，必须合并或记录明确的上位/下位差异。
