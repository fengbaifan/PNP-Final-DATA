# v0.1 发布验证报告（第一章一次性转换）

## 统计

| 指标 | 值 |
|---|---|
| 有效知识元（KU） | 1019 |
| 正式关系边 | 1226 |
| 关系来源分布 | enrich=752；book=474 |
| 关系状态分布 | formal=1224；pending=2 |
| 对齐记录（chp-1） | 335（paired=164，unpaired=171） |
| 补足证据（chp-1） | 1370 |

## KU 按类型

| 类型 | 数量 |
|---|---|
| archive | 61 |
| event | 7 |
| family | 10 |
| institution | 140 |
| person | 387 |
| place | 152 |
| procedure | 10 |
| term | 34 |
| work | 218 |

## 关系按谓词（前 20）

| 谓词 | 数量 |
|---|---|
| located_at | 216 |
| created_by | 203 |
| held_by | 106 |
| has_subject | 93 |
| commissioned_by | 60 |
| member_of | 48 |
| supplied_by | 37 |
| authored_by | 37 |
| parent_of | 28 |
| trained_by | 26 |
| contributed_by | 26 |
| installed_at | 26 |
| employed_by | 21 |
| acquired_by | 21 |
| part_of | 20 |
| owned_by | 18 |
| intended_for | 18 |
| addressed_to | 18 |
| collaborated_with | 17 |
| supported_by | 17 |

## 约束检查

- 关系域值域违规（对照 relation-domain-range.yml v1）：**0**（应 0）。
- 弃用类型在途：见上方关系状态，`pending` 边不含 `associated_*`。

## 待补（不在本步）

- 实体召回率：待 step 4 解析原书索引后对照。
- 对齐/关系抽样精度：待人工分层抽样复核。
- 字段级补足事实（field→value→source）：在卡内正文表，需深解析，暂列来源级记录。
- front-matter 的 alignment/enrichment 证据（alignment-writeback.json 等）格式不同，另行转换。
