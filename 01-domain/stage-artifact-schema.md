# S0–S7 阶段产出字段规范（草案 v1）

> 状态：**草案，供审**。本文件只定义各阶段唯一产出的列、放行条件与「不重跑」来源映射；不改变任何现有数据、规则或网页。S0–S7 尚未启用，仅作为重构目标。

## 已决事项（2026-09-25）

1. **关系域值域矩阵现在就建**：见 [relation-domain-range.yml](relation-domain-range.yml)，S6 放行时以 inverse 映射规范化后核对该矩阵。
2. **backlog 阈值 = 20**：同类型候选待办 ≥ 20 时提前批量 drain；关系阶段收口前硬性清空。
3. **删除 frontmatter relations**：迁移后 `relations.csv` 是正式边的唯一事实源，卡片关系表由它渲染；frontmatter.relations 与 `relation-index.yml` 手工维护版一并退役（详见 §S6）。

## 0. 跨产物公约

**0.1 稳定 ID**
- `segment_id` = `{chapter}:{section}:l{line_start}-{line_end}`（印刷页另作字段，不塞进 ID）
- `candidate_id` = `cand-{index_file}-{row}`（可回溯原书索引条目）
- `ku_id` = 沿用稳定路径 `units/{type}/{slug}.md`
- `statement_id` / `relation_id` / `enrichment_id` = `stmt-{n}` / `rel-{n}` / `enr-{n}`（连续号，不承载语义）

**0.2 `origin` 枚举（逐事实标注）**

| 值 | 含义 | 只出现在 |
|---|---|---|
| `book` | 原书陈述 | book-statements、relations 的书内边 |
| `align` | 身份映射（提及=实体+外部标识），不含内容事实 | alignment.csv |
| `enrich` | 外部内容事实 | enrichment.jsonl、relations 的外部边 |
| `infer` | Agent 语境解读 | statements/relations 的推断边 |

**0.3 `evidence_status`**：`confirmed`／`contested`／`uncertain`。

**0.4 `decision` 五档对齐决定**：`same`／`new`／`conflict`／`excluded`／`undecided`（`excluded` 与 `undecided` 附理由）。

**0.5 结构化 vs 散文分界（转换安全前提）**
- 结构化事实 → CSV/JSONL 唯一权威：名称/别名、类型、日期、外部 ID、对齐决定、补足事实、关系、提及的（主/谓/宾/限定/定位）。
- 散文 → 仍在 `units/*.md` 卡内人工维护：双语描述、「本章相关内容」、「原书转引评论」、原文引用。
- 卡片 = 结构化表由 CSV 渲染 + 散文段落原位；不追求「卡片 100% 由表生成」。

**0.6 关系域值域**：见 [relation-domain-range.yml](relation-domain-range.yml)。

---

## S0 来源规范化

| 文件 | 列 | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `segments.jsonl` | `segment_id` | string | ✅ | 主键 |
| | `chapter` | string | ✅ | `chp-1`、`front-matter`… |
| | `section` | string | ✅ | `intro`／`sec_i`… |
| | `page` | int\|null | | 印刷页 |
| | `line_start` / `line_end` | int | ✅ | OCR 行区间 |
| | `sha256` | string | ✅ | 段落内容哈希 |
| `sources.csv` | `source_id` | string | ✅ | 主键 |
| | `title`/`edition`/`year`/`isbn` | string | ✅ | 版本指纹 |

**放行条件**：只用分节文件一套切分；同章内 line 区间不重叠、覆盖率 100%；每个 source 有稳定 `source_id`+哈希。
**不重跑**：`02-Markdown/` 分节文件 + `scripts/_source_fingerprint.py`。

## S1 全书实体候选（原书索引为种子）

| 文件 | 列 | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `entity-candidates.csv` | `candidate_id` | string | ✅ | 主键 |
| | `index_entry_id` | string | ✅ | 回溯索引条目 |
| | `canonical_name` | string | ✅ | 索引规范名 |
| | `aliases` | string | | 分号分隔 |
| | `suggested_type` | string | ✅ | 九类之一 |
| | `index_page_range` | string | ✅ | 索引页码 |
| | `index_source_file` | string | ✅ | `A.csv`… |
| | `status` | string | ✅ | `open`／`excluded` |
| | `exclude_reason` | string\|null | | `excluded` 必填 |

**放行条件**：索引每条 → 候选或 `excluded` 附理由；覆盖 = 100%。
**不重跑**：`03-2-Index-CSV/*.csv` + `List_of_Plates` + `Bibliography`（首次解析，不靠 Agent 从零识别）。

## S2 书内语义处理（逐章）

| 文件 | 列 | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `mentions.csv` | `mention_id` | string | ✅ | 主键 |
| | `segment_id` | string | ✅ | FK |
| | `candidate_id` | string | ✅ | 提及→候选 |
| | `surface_form` | string | ✅ | 文中原形 |
| | `note` | string | | 消歧语境 |
| `book-statements.jsonl` | `statement_id` | string | ✅ | 主键 |
| | `segment_id` | string | ✅ | FK |
| | `subject_candidate_id` / `object_candidate_id` | string\|null | | 端点（可待决） |
| | `predicate` | string | ✅ | 关系或断言类型 |
| | `qualifiers` | object | ✅ | 转述/推测/否定/发言者/时间 |
| | `original_quote` | string | ✅ | 原句（仅内部，不发布） |
| | `origin` | string | ✅ | 恒 `book` |

**放行条件**：本章段落覆盖 100%；每条断言有锚点。
**不重跑**：已有章从 `results/stages.md` 抽取；新章直接读分节文件。

## S3 身份对齐（全局、按类型）

| 文件 | 列 | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `alignment.csv` | `alignment_id` | string | ✅ | 主键 |
| | `candidate_id` | string | ✅ | FK |
| | `ku_id` | string\|null | | `same`/`new` 必填 |
| | `external_source` | string | | Wikidata/VIAF/Treccani DBI… |
| | `external_id` / `external_url` | string\|null | | QID 等 |
| | `method` | string | ✅ | `wp-wd` 双向/国家辞典… |
| | `decision` | string | ✅ | 五档（§0.4） |
| | `evidence_ref` | string | ✅ | |
| | `accessed_date` | string | | |

**放行条件**：每候选恰一个决定且带证据；`same`/`new` 有外部锚点；`undecided`/`excluded` 附理由；只处理身份，不注入内容事实。
**不重跑**：`alignment-evidence.jsonl` + 对齐快照；`chp-1` 与 `front-matter` 共用这一张表。

## S4 KU 登记

| 文件 | 列 | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `ku-manifest.csv` | `ku_id` | string | ✅ | 主键（稳定路径） |
| | `type` | string | ✅ | 九类 |
| | `canonical_name` / `name_en` | string | ✅ | 中英 |
| | `source_task` | string | ✅ | 来源任务 |
| | `created` / `updated` | string | ✅ | |
| | `card_path` | string | ✅ | 散文卡路径 |

**放行条件**：S3 每个 `new` 有对应 `ku_id`；所有计数只从此清单算。
**不重跑**：`accepted.yml` 转换。

## S5 补足

| 文件 | 列 | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `enrichment.jsonl` | `enrichment_id` | string | ✅ | 主键 |
| | `ku_id` | string | ✅ | FK |
| | `field` | string | ✅ | 被补字段 |
| | `value` | string | ✅ | 事实 |
| | `origin` | string | ✅ | 恒 `enrich` |
| | `source` / `url` | string\|null | ✅ | 外部来源 |
| | `accessed_date` | string | ✅ | |
| | `source_independence_group` | string | | 防转引计为独立 |
| | `evidence_status` | string | ✅ | §0.3 |
| | `conflicting_values` | string\|null | | 异文并列 |

**放行条件**：每类实体预声明要补字段；每字段填完或标「缺口」附理由。
**不重跑**：`enrichment-evidence.jsonl`（27.8MB）只抽已采纳事实。

## S6 关系

| 文件 | 列 | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `relations.csv` | `relation_id` | string | ✅ | 主键 |
| | `subject_ku_id` / `object_ku_id` | string | ✅ | FK（须在 manifest 内） |
| | `predicate` | string | ✅ | 词表类型 |
| | `direction` | string | ✅ | 规范方向 |
| | `time` / `time_range` | string\|null | | |
| | `role` / `scope` | string\|null | | 限定 |
| | `origin` | string | ✅ | book/enrich/infer |
| | `status` | string | ✅ | `formal`/`pending`/`rejected` |
| | `evidence_ref` | string | ✅ | |

**放行条件**：主/客体类型通过 [relation-domain-range.yml](relation-domain-range.yml)（谓词先规范化到正向）；每条 `formal` 边 ≥1 证据；无断端点；`pending` 边进 backlog。
**迁移**：frontmatter.relations 与手工维护的 `relation-index.yml` 退役，`relations.csv` 为唯一事实源，卡片关系表由其渲染。
**不重跑**：KU frontmatter relations + `relation-review-rev065.jsonl` 转换。

## S7 发布与验证

| 文件 | 来源 |
|---|---|
| `release/vX/entities.csv` | ku-manifest + 选定结构化事实 |
| `release/vX/relations.csv` | S6 |
| `release/vX/evidence.csv` | 定位+事实（无原文） |
| `release/vX/provenance.csv` | 事实→origin→source→定位 |
| `release/vX/schema.md` | 九类 + 关系词表 + 字段契约 |
| `validation-report.md` | 召回率 vs 索引、抽样精度+置信区间+一致率、约束违规数 |
| 派生索引/网页数据 | relation-index / translation-index / current-health / 05-outputs |

**放行条件**：全部由 S0–S6 生成、不手改；打 tag 冻结；派生文件只在此步生成。

---

## 依赖顺序

```
S0(来源) → S1(候选) → S2(提及/断言) → S3(对齐) → S4(KU) → S5(补足) → S6(关系) → S7(发布)
                                              ↑________ backlog drain（阈值 20）________|
```

## 校验与跟踪

- 已对既有 `relation-index.yml` 的 1,227 条边做只读校验：0 弃用类型在途、0 未知谓词、0 非法类型。
- `relation-domain-range.yml` 已修到 v1（domain/range 覆盖当前实际用法）。
- `located_at` 语义过载（person/institution/archive/work → place/institution），标 `needs_split`，拆分去向待定。
- 数据修正 1 条：`gianfranco-torcellan.md` 的 `authored_by` 方向反了，已改回（archive 卡持 `authored_by`→person，person 卡改反向投影）。
- `commissioned_by` 的 `place→person`（建筑/教堂/祭坛被委托人委托建造）为合法用法，矩阵 domain 含 `place`。
- S0–S7 尚未启用；启用时按 system-upgrade 流程修订 pipeline 与各 Skill 交接，不在本文件外另建副本。
