# Taxonomy Registry — 类型体系成长注册表 v4.0

本文件定义当前领域知识库的知识元类型注册规则。8 类基础类型沿用系统通用框架，本领域按其艺术史研究对象重新释义。

## 一、设计原则

1. **基础类型先行**：8 类 knowledge unit，4 类 structure node；Cluster 属于发现候选，不是结构类型。
2. **发现优先于预设**：新类型必须来自摄入、查询、审查中的反复结构性需求。
3. **类型晋升有证据**：候选类型必须证明现有类型无法清晰表达其语义角色。
4. **迁移可恢复**：新增、合并、弃用类型须保留映射记录（见 taxonomy-migration-map.json）。
5. **领域可替换**：不同垂直领域可扩展不同类型，但共享同一套生命周期和审查协议。

## 二、Knowledge Units（8 类基础类型）

| 目录 | type | 角色 |
|------|------|------|
| `persons/` | `person` | 自然人行动者（画家/赞助人/经纪人/学者/收藏家） |
| `institutions/` | `institution` | 组织实体（教会/修会/学院/行会/宫廷/家族） |
| `places/` | `place` | 地理坐标点（城市/教堂/宫殿/工作室） |
| `works/` | `work` | 视觉与物质对象（绘画/雕塑/建筑/委托作品） |
| `publications/` | `publication` | 书目身份文本（传记/文献/目录/理论著作） |
| `terms/` | `term` | 稳定术语/概念名称（赞助机制术语/艺术史概念） |
| `procedures/` | `procedure` | 可操作知识/流程/工艺（委托流程/合同惯例/技艺） |
| `events/` | `event` | 单一历史发生项（委托/庆典/艺术事件） |

## 三、Structure Nodes（4 类）

| 目录 | node_type | 角色 | 判断规则 |
|------|-----------|------|---------|
| `structure/domains/` | `domain` | Level 1 总问题域 | 当前项目《赞助人与画家》：巴洛克时期意大利艺术与社会 |
| `structure/dimensions/` | `dimension` | Level 2 分析维度 | 当前 A–E 五个 pilot 维度 |
| `structure/themes/` | `theme` | 稳定问题群 | hierarchy Level 3；A.1/B.2 等代码 |
| `structure/topics/` | `topic` | 可研究问题 | hierarchy Level 4；组织多类 KU 材料 |

> structure node 不是 knowledge unit。如果一个对象可包含多个 unit，应提升为 structure node。
> canonical hierarchy 为 domain -> dimension -> theme -> topic -> KU。Cluster 仅存在于 discovery candidate/work package，可对任意层级形成召回信号，但不能作为正式 structure node。

## 四、Assertion & Evidence 层

| 元素 | 存储 | 格式 |
|------|------|------|
| `claim` | `quality/claim-registry.yml` | YAML |
| `evidence` | `quality/` | JSON |
| `source` | 嵌入 claim/evidence | 内联 |
| `citation` | 嵌入 source | Chicago 17th |

> claim 不作为 knowledge unit 目录存在。旧 ideas/ 目录已归档至 claim-registry.yml。

## 五、废弃类型映射

| 旧 type | 新 type | 迁移日期 |
|---------|---------|---------|
| `concept` | `term` | 2026-05-08 |
| `technique` | `procedure` 或 `term` | 2026-05-08 |
| `case` | `event` 或 `topic`（structure node） | 2026-05-08 |
| `idea` | `claim-registry.yml` 或 `term` | 2026-05-08 |
| `theme` | structure node（非 knowledge unit） | 2026-05-08 |
| `conflict` | frontmatter `conflicts` 字段或 quality/ | 2026-05-08 |

完整映射见 `06-runtime/governance/taxonomy-migration-map.json`。
