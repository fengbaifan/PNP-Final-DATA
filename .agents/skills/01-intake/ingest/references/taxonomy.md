# 知识元类型分类体系（Knowledge Unit Taxonomy）

> 完整定义以 `AGENTS.md` 与 `01-domain/` 为准。类型生命周期、新类型候选和晋升条件详见 `01-domain/taxonomy-registry.md`。

## 文件命名规范

知识元文件命名遵循以下规则（**必须严格遵守**）：

### 命名原则
英文优先、描述性、短横线分隔、目录自洽

### 各类型命名规则

```
# person（人物）：英文姓名转写（小写、短横线）
<firstname-lastname>.md
例：gian-lorenzo-bernini.md、urbano-viii.md、francesco-algarotti.md

# work（作品）：作品英文名 + 年份后缀（YYYY 或 YYYY-YYYY）
<work-title-dashed>-<year>.md
例：ecstasy-of-saint-teresa-1652.md、palazzo-barberini-ceiling-fresco-1639.md
规则：所有有日期的作品必须带年份后缀；无日期的抽象作品可省略

# publication（著作）：书名/文章名（无冗余后缀）
<title-dashed>.md
例：patrons-and-painters.md、le-vite-de-pittori.md
规则：目录已标识类型，文件名不得再带 -publication、-book、-article 等冗余后缀

# term（术语）：概念/术语定义
<english-term-dashed>.md
例：baroque.md、patronage.md、servitu-particolare.md
规则：抽象概念、通用类别名、理论标签。回答"这个术语是什么意思"。
与 procedure 的区别：term 描述"是什么"，procedure 描述"怎么做"。

# procedure（规程）：具体操作方法
<english-gerund-dashed>.md
例：fresco-painting.md、commission-contracting.md、art-restoration.md
规则：文件名优先使用动词/动作形式（mapping 非 map, engraving 非 engrave）。
包含明确操作步骤的技术方法。抽象类别名归入 term。

# event（事件）：单一历史发生项
<event-description-dashed>.md
例：1625-holy-year-jubilee.md、palazzo-barberini-inauguration-1633.md
规则：含日期的前置；可定位到特定时间、地点、参与者。
大型历史过程/运动谱系/案例组 → topic/theme/cluster。

# institution（机构）：组织实体
<english-name-dashed>.md
例：accademia-di-san-luca.md、jesuit-order.md、barberini-family.md
规则：教会、修会、学院、行会、宫廷、家族等。区别于 place（地理坐标点）。

# claim（断言）：不作为知识元目录
claim 存储在 quality/claim-registry.yml 索引中。
回答"A 关于 B 说了什么"。旧 claims/ 目录的条目迁移时逐条判断归属。

# place / institution（地点/机构）：英文地名
<english-place-name-dashed>.md
例：rome.md、venice.md
规则：不得与上级地点重复（如已有 rome.md，不得新建 rome-city.md）
```

### 命名禁忌（必须遵守）

```
1. 禁止使用 doc-id 前缀
   ❌ chp-2-gian-lorenzo-bernini.md
   ✅ gian-lorenzo-bernini.md

2. 禁止在 publications 目录使用 -publication 后缀
   ❌ vite-de-pittori-publication.md
   ✅ vite-de-pittori.md

3. 禁止使用中文拼音
   ❌ beiernini.md、HaskellFrancis.md

4. 禁止使用空格（用短横线 - 代替）
   ❌ Gian Lorenzo Bernini.md
   ✅ gian-lorenzo-bernini.md

5. 禁止使用特殊字符（只允许 a-z、0-9、连字符 -）
   ❌ 亚伯拉罕·林肯.md、data-vis.md

6. 禁止 type 值使用复数形式
   ❌ type: persons / works / techniques
   ✅ type: person / work / procedure

7. 禁止在 works 目录的文件名中包含 -work/-product 后缀
   （目录已表明类型）

8. 禁止在 procedures 目录的文件名中包含 -procedure/-method 后缀
   （目录已表明类型；动作型名称应优先使用 gerund，如 `fresco-painting.md`）

9. 禁止在 places 目录的文件名中包含 -place/-location 后缀
   （目录已表明类型）
```

### 同名区分规则

当同一概念出现在多个类型目录时，按以下规则区分：

| 类型组合 | 规则 | 示例 |
|---------|------|------|
| term + procedure 同名 | 从对象本体区分：术语名保留 noun，操作过程用 action/gerund | `fresco.md` (term) + `fresco-painting.md` (procedure) |
| term + place 同名 | place 用全地名或历史名消歧 | `rome.md` (place) |
| 同一 type 内同名 | 必须为不同实体 | `assumption-of-the-virgin-1601.md` (Carracci) vs `assumption-of-the-virgin-1650.md` (Guercino) |

### 年份后缀规则（works/events）

```
强制添加年份后缀：
  ✅ ecstasy-of-saint-teresa-1652.md
  ✅ calling-of-saint-matthew-1600.md
  ✅ palazzo-barberini-frescoes-1633-1639.md

可省略年份（仅限无具体日期的抽象作品）：
  ✅ barberini-faun.md（古代雕塑无确切日期）
  ✅ borghese-collection-inventory.md（无具体年代）

年份格式：
  - 精确年份：-1652
  - 年代范围：-1633-1639（不超过4位数字则用连字符分隔）
  - 世纪描述：17th-century-roman-art-market.md（用序数词非数字）
```

## 类型总览

```
Knowledge Units（8 类）
│
├── Person             ── 可被指认为个人的行动者（画家/赞助人/经纪人/学者/收藏家）
├── Institution        ── 具有组织结构、制度目标的实体（教会/修会/学院/行会/宫廷/家族）
├── Place              ── 地理坐标点或空间位置（城市/教堂/宫殿/区域）
├── Work               ── 可被观看/分析/复制的视觉与物质对象（绘画/雕塑/建筑/委托作品）
├── Publication        ── 具有书目身份的文本出版物（传记/文献/目录/理论著作）
├── Term               ── 稳定术语、概念名称、艺术史概念、赞助机制术语
├── Procedure          ── 可被执行/复用/传授的操作性知识（工艺/流程/委托惯例）
└── Event              ── 特定时间/地点/参与者的历史发生项

Structure Nodes（4 类）
│
├── Domain             ── 总问题域（Level 1）
├── Dimension          ── 分析维度（Level 2；当前 A–E 五个 pilot 维度）
├── Theme              ── 稳定问题群（Level 3；A.1/B.2 等代码）
└── Topic              ── 可研究问题（Level 4；组织多类 KU 材料）

> canonical hierarchy 为 domain -> dimension -> theme -> topic -> KU。
> Cluster 是发现候选，不是 structure node。
```

### 废弃类型映射

以下旧类型已完成迁移，不再作为当前 Knowledge Unit 类型：

| 旧 type | 新 type | 迁移日期 |
|---------|---------|---------|
| `concept` | `term` 或 `claim` | 2026-05-08 |
| `technique` | `procedure` 或 `term` | 2026-05-08 |
| `case` | `event` 或 `topic`/`theme`；Cluster 仅作 discovery candidate | 2026-05-08 |
| `idea` | `claim` 或 `term` | 2026-05-08 |

完整映射记录见 `06-runtime/governance/taxonomy-migration-map.json`。

---

## Person（人物）

```yaml
sub_type: painter | sculptor | architect | patron | collector | dealer | scholar | cleric | other
name_en: <标准英文名>
birth_death: <生卒年>
nationality: <国籍/文化背景>
period: <所属历史时期>
domain: [<专业领域>]
major_contributions:
  - <主要贡献1>
  - <主要贡献2>
key_works: [<代表作品链接>]
key_publications: [<代表著作链接>]
influences: [<影响了谁>]
influenced_by: [<受谁影响>]
```

---

## Institution（机构）

```yaml
sub_type: church | religious_order | academy | guild | court | family | civic_body | other
name_en: <标准英文名>
name_original: <原语言名>
language_original: <ISO 639-1>
name_zh: <中文名>
location: <国家/城市>
period_active: <存续时期>
associated_persons: []
associated_works: []
associated_publications: []
```

---

## Term（术语）

```yaml
sub_type: concept_name | art_historical_concept | patronage_term | theoretical_framework | methodology | other
name_en: <标准英文名>
term_original: <原文术语>
term_original_language: <ISO 639-1>
term_zh: <中文学术译名>
academic_translation_status: confirmed | provisional | disputed | machine_suggested
proposed_by:
  - ../units/persons/<person-id>.md
definition: >
  <核心定义（可多行）>
domain: [<适用领域>]
related_terms: [<相关术语>]
```

---

## Procedure（规程）

```yaml
sub_type: artistic_technique | conservation_method | contractual_practice | process | workflow | other
name_en: <英文名（优先使用 gerund 形式）>
period_developed: <发展时期>
developed_by: [<发明者>]
materials_used: [<所需材料/工具>]
process_steps:
  - step: 1
    description: <步骤描述>
    tools: [<所需工具>]
significance: <技术意义>
predecessor_procedures: [<前身工艺>]
successor_procedures: [<后续/替代工艺>]
```

---

## Event（事件）

```yaml
sub_type: historical_occurrence | commission | ceremony | conclave | exhibition | other
name_en: <标准英文名>
date_range: <时间范围或精确日期>
location:
  - <地点描述>
key_participants:
  - ../units/persons/<person-id>.md
cause: >
  <起因/背景（可多行）>
process: >
  <过程要点（可多行）>
outcome: >
  <结果/影响（可多行）>
```

---

## 作品（Work）

> 注意：works 的 `## 核心内容` **不使用 yaml code block**，而是用**粗体键值对列表**：

```markdown
## 核心内容

- **name_en**: <英文名>
- **creator**: [<创作者链接>]
- **date**: <年代/时期>
- **material_medium**: <材料/媒介>
- **dimensions**: <尺寸（如适用）>
- **current_location**: <现存位置>
- **cultural_context**: <文化背景>
- **academic_significance**:
  - <学术意义要点1>
  - <学术意义要点2>
- **artwork_analysis**: <作品分析要点（主题/风格/图像志）>
```

---

## 著作（Publication）

```yaml
sub_type: monograph | journal_article | manifesto | report | textbook | edited_volume
name_en: <标准英文书名/文章名>
author:
  - ../units/persons/<author-id>.md
year: <出版年>
publisher: <出版机构>
language: <原始语言>
doi: <DOI（如有）>
isbn: <ISBN（书籍）>
journal: <期刊名（论文）>
volume_issue: <卷期>
pages: <页码>
core_arguments:
  - <核心论点1>
  - <核心论点2>
methodology: <研究方法>
key_concepts_introduced:
  - <本著作首次提出/定义的概念>
impact: >
  <学界影响（可多行）>
citation_count: <引用数（来自 Google Scholar）>
related_ku:
  - ../units/<type>/<name>.md
apa_citation: >
  <完整 APA 7th 格式引用字符串>
chicago_citation: >
  <完整 Chicago 17th 格式引用字符串>
```

---

## 地点（Place）

```yaml
sub_type: city | church | palace | building | geographical_region | other
name_en: <标准英文名>
location_coords: <地理位置（国家/地区）>
period_active: <活跃/存续时期>
associated_persons: []
associated_cases: []
academic_significance: >
  <学术意义（可多行）>
```

> 注意：places 的 yaml block **内仍保留 sources 字段**（因为 places 通常没有独立的引用文献）。

---

## 通用规则

1. **`## 核心内容` 中的 yaml block 不包含 sources 字段**（sources 在 frontmatter 的 `sources:` 字段中声明）
2. **yaml block 中的链接路径**使用相对路径，如 `../units/persons/adam-dant.md`
3. **`evidence_ref.source_file` 字段**（推荐）：记录 `02-sources/<doc-id>/...` 下真实存在的来源文件；不得假定固定 `original.md` 路径
4. **多行文本**在 yaml 中使用 `>` 或 `|` 折叠标量
5. **列表项**在 yaml 中使用 `-` 前缀
6. **validation 状态**：对于无 Wikipedia 页面的主题，使用 `[UNVERIFIED (no wiki page)]`
