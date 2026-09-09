# Knowledge Unit 字段与存储契约 v2.0

本文件是 `04-knowledge/units/**/*.md` 的唯一字段与 frontmatter 存储权威。8 类 KU 为 `person`、`institution`、`place`、`work`、`publication`、`term`、`procedure`、`event`；structure node、claim 和 Cluster 不使用 KU `type`。

## 一、机械必需字段

以下字段与 `scripts/audit_repo.py` 的 `REQUIRED_FIELDS` 一致，缺失属于结构错误：

```yaml
title: 中文名（English Name）
name_en: English Name
type: person | institution | place | work | publication | term | procedure | event
sources:
  - <source-record>
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: low | medium | high
consensus: confirmed | disputed | tentative
source_count: 1
last_verified: YYYY-MM-DD
review_due: YYYY-MM-DD
version: 1
```

推荐字段为 `sub_type`、`tags` 和 `evidence_status`。`verification_level` 在 `consensus != tentative` 时必须存在。`primary_domain`、`primary_dimension`、`primary_theme` 与 `topic_memberships` 是五级层级的目标字段，但历史未回填属于研究债务，不冒充 P0 schema error。

## 二、可选字段组

可选字段只在有真实内容时写入；不得用空占位制造“完整”。空数组在 schema 明确允许集合值时合法。

```yaml
sub_type:
tags: []
disambiguation:
doc_id:

name_original:
language_original:
script_original:
name_latinized:
name_ascii:
name_zh:
aliases: []
authority_sources: []
translation_status:
translation_note:

evidence_status: unverified | source_backed | partially_verified | externally_verified | model_supported
verification_level: L1 | L2 | L3 | L4 | L5 | L6 | L7
verification_methods: []

primary_domain:
secondary_domains: []
primary_dimension:
secondary_dimensions: []
primary_theme:
secondary_themes: []
role_in_theme:
topic_memberships: []
hierarchy_scope_note:

relations: []
weak_associations: []
related: []              # 只作历史兼容，不是正式 relation 权威
conflicts: []            # 只作历史兼容；现行冲突记录在 work package
```

层级值与 membership role 见 `hierarchy-field.md`；正式 relation 类型见 `relation-types.md`。验证状态的晋级与写回只遵循 `.agents/skills/03-verification/verify/SKILL.md`，本文件不建立第二套状态裁决。

## 三、来源结构

`sources` 是来源绑定列表，`source_count` 必须等于实际去重后绑定的条目数，不使用增量猜测：

```yaml
sources:
  - citation: "Chicago 17th 可引用条目"
    location: "chapter / page / figure / source span"
    evidence_ref:
      doc_id: "2017-lima-book-of-circles"
      source_file: "02-sources/2017-lima-book-of-circles/05_Taxonomy_ZH.md"
      chapter_id: "05-taxonomy"
      chunk_id: null
```

- `evidence_ref.doc_id` 必须对应真实来源目录。
- `evidence_ref.source_file` 只能写真实存在的仓库路径，不得假设固定 `original.md`。
- 无法精确定位时不写伪路径，使用 `source_file_status: needs_precise_source_file` 并记录原因。
- citation 格式见 `citation.md`；文件路径不是来源主标识。

## 四、名称与身份

- `name_en` 优先取自原始来源或可审查权威来源；不得只根据 slug 静默推断。
- 来源确无英文名时，可由 Agent 明确转写，并在 `translation_note` 或工作包 decision 中记录依据与不确定性。
- `type` 是对象类别，不是唯一性依据；同一现实对象不得因类型标签差异重复建档。
- 文件命名、同名消歧和类型判断见 `taxonomy.md`。

## 五、类型专有内容

下列字段是语义建构提示，不是全库统一必需字段。只有来源支持时才写入；缺失默认是内容债务，不是机械结构故障。

| 类型 | 优先字段 |
|---|---|
| person | `birth_death`、`nationality`、`occupation`、`contribution_scope`、`representative_works`、`associated_institutions` |
| institution | `official_name`、`institution_type`、`location`、`active_period`、`parent_institution`、`collections` |
| place | `modern_name`、`historical_names`、`coordinates`、`spatial_scope`、`administrative_context`、`related_events` |
| work | `title_original`、`creator`、`year`、`medium`、`format`、`collection`、`image_assets`、`visual_features` |
| publication | `title_original`、`author`、`publication_year`、`publisher`、`doi`、`isbn`、`worldcat`、`archive_url`、`edition` |
| term | `term_original`、`term_zh`、`definition`、`scope_note`、`broader_terms`、`narrower_terms`、`related_terms` |
| procedure | `action_name`、`steps`、`inputs`、`outputs`、`constraints`、`example_works`、`historical_context` |
| event | `date`、`location`、`participants`、`cause`、`result`、`associated_works`、`source_basis` |

## 六、文件与正文边界

1. 每个 KU 只有一组起止 `---` frontmatter，文件编码为 UTF-8。
2. 字段推荐顺序为身份 -> 分类 -> 来源 -> 层级 -> relation -> 生命周期 -> 验证；不得为了重排而制造无语义 diff。
3. 正文从 `## 描述`、`## 定义` 或 `body-template.md` 允许的类型章节开始，不残留第二段 YAML。
4. 正文与 frontmatter 的验证状态不得冲突；`## 相关知识元` 不能覆盖 relation index 的权威口径。
5. 字段、来源路径和 relation 涉及不同语义，不使用通用 normalize writer 猜测；正式修订先形成 exact change-set，再跑最近邻门禁。

## 七、状态诚实

无人工工作流下，新建 KU 不得直接写为 `confirmed` 或 `externally_verified`。推荐初始状态为 `confidence: medium`、`consensus: tentative`、`evidence_status: source_backed`；证据不足时保留 `needs_evidence`、`external_not_found`、`unresolved` 或 `deferred`。单一来源、QID 或脚本分数不得自动晋级。

## 八、验收

- 必需字段、枚举、type/目录与 source path 通过 `python scripts/audit_repo.py --summary`。
- `source_count` 与真实绑定来源一致。
- `required_field_missing` 不新增；推荐字段和类型专有内容缺口进入研究债务。
- 层级映射、relation mirror 和验证正文不与各自权威索引冲突。
