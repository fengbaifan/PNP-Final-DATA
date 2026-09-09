# 知识元正文模板 v4.0

> 当前正文模板只适用于 8 类 KU：person / institution / place / work / publication / term / procedure / event。旧 ideas / concepts / techniques / cases 不再作为 KU 类型。

## 一、通用结构

所有 KU 正文至少包含：

1. `## 描述` 或 `## 定义`
2. `## 核心内容`
3. `## 在层级体系中的位置`
4. `## 相关知识元`
5. `## 验证状态`
6. `## 参考文献`

`## 相关知识元` 是兼容展示章节；正式关系以 `relation-index.yml` 与 frontmatter `relations` 镜像为准。

## 二、通用模板

```markdown
## 描述

<1-3 句中文精确描述，说明对象边界与本体系相关性。>

## 核心内容

<按类型填写专有字段；不得用空泛摘要替代对象内容。>

## 在层级体系中的位置

- primary_domain:
- primary_dimension:
- primary_theme:
- topic_memberships:
- role_in_theme:
- scope_note:

## 相关知识元

- [中文名（关系说明）](../<type>/<slug>.md)

## 验证状态

- evidence_status:
- verification_level:
- last_verified:
- no-data / external_lookup:
- limits:

## 参考文献

1. <Chicago 17th citation>
```

## 三、类型专有内容提示

### person

```markdown
## 核心内容

- **name_original**:
- **language_original**:
- **name_zh**:
- **birth_death**:
- **occupation**:
- **nationality**:
- **contribution_scope**:
- **representative_works**:
- **authority_sources**:
```

### institution

```markdown
## 核心内容

- **official_name**:
- **institution_type**:
- **location**:
- **active_period**:
- **parent_institution**:
- **collections**:
- **publishing_roles**:
```

### place

```markdown
## 核心内容

- **modern_name**:
- **historical_names**:
- **coordinates**:
- **spatial_scope**:
- **administrative_context**:
- **related_events**:
```

### work

```markdown
## 核心内容

- **title_original**:
- **creator**:
- **year**:
- **medium**:
- **format**:
- **collection**:
- **image_assets**:
- **visual_features**:
```

### publication

```markdown
## 核心内容

- **title_original**:
- **author**:
- **publication_year**:
- **publisher**:
- **doi**:
- **isbn**:
- **worldcat**:
- **archive_url**:
- **edition**:
```

### term

```markdown
## 定义

<术语定义、适用边界与本领域语境。>

## 核心内容

- **term_original**:
- **term_zh**:
- **definition**:
- **scope_note**:
- **broader_terms**:
- **narrower_terms**:
- **related_terms**:
- **academic_translation_status**:
```

### procedure

```markdown
## 描述

<说明这是可执行、可复用或可传授的操作性知识。>

## 核心内容

- **action_name**:
- **steps**:
- **inputs**:
- **outputs**:
- **constraints**:
- **example_works**:
- **historical_context**:
```

### event

```markdown
## 描述

<说明时间、地点、参与者与发生项边界。>

## 核心内容

- **date**:
- **location**:
- **participants**:
- **cause**:
- **result**:
- **associated_works**:
- **source_basis**:
```

## 四、易错清单

1. 禁止使用旧类型 ideas / concepts / techniques / cases。
2. 禁止把 claim 写成 KU 正文。
3. 禁止把 structure node 写成 KU 正文。
4. 禁止将 `related` 当作正式关系证据。
5. 禁止因 Wikipedia / Wikidata 无结果删除或否定 KU。
6. 禁止输出中的解释性概括直接回填为 KU 事实。

