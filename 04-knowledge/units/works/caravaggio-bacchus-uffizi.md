---
title: 《巴克斯》（Bacchus）
name_en: Bacchus
type: work
created: '2026-09-13'
updated: 2026-09-14
evidence_status: source_backed
relations:
- relation_type: created_by
  target: persons/caravaggio.md
  note: 具体对象页将Bacchus归于卡拉瓦乔；本边保留版本边界。
  evidence_ref:
    doc_id: created-by-persons-caravaggio-md
    source_file: https://www.uffizi.it/en/artworks/bacchus
    source_span: 本卡S2；有S4时并参对象字段
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  role: 创作者
  scope: 与《生病的巴克斯》及其他同题对象分开。
- relation_type: held_by
  target: institutions/uffizi-gallery.md
  note: 当前对象记录将Bacchus列由该机构保管；保管不自动等于产权。
  evidence_ref:
    doc_id: held-by-institutions-uffizi-gallery-md
    source_file: https://www.uffizi.it/en/artworks/bacchus
    source_span: 本卡S2；有S4时并参对象字段
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  time: 本轮来源访问时
  role: 保管机构
  scope: 现存
- relation_type: commissioned_by
  target: persons/francesco-maria-del-monte.md
  note: 来源明确该端点承担Bacchus的委托角色；不由委托推定当前所有权。
  evidence_ref:
    doc_id: commissioned-by-persons-francesco-maria-del-monte-md
    source_file: https://www.uffizi.it/en/artworks/bacchus
    source_span: 本卡S2；有S4时并参委托／历史段
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  time: 约1596
  role: 委托人／委托机构
  scope: 与《生病的巴克斯》及其他同题对象分开。
sources:
- citation: Wikipedia (en), Caravaggio, revision 1372526492. https://en.wikipedia.org/wiki/Caravaggio. Accessed 2026-09-11.
  location: 人物页具名对象清单第10项及相邻语境；全文REV-052已保存
  sentence_summary: 主页面将Bacchus列入具名作品、版本或归属讨论；不由此证明全部字段。
- citation: Wikipedia (en), Bacchus (Caravaggio), revision 1369810233. https://en.wikipedia.org/wiki/Bacchus_(Caravaggio). Accessed 2026-09-12.
  location: 全文语义阅读；正文、信息框、图注及注释／书目文本；外链页面另计
  sentence_summary: 区分Bacchus的对象、版本、年代、材料、流传、归属与当前状态。
- citation: Wikidata, Q2011510, https://www.wikidata.org/wiki/Q2011510. Accessed 2026-09-12.
  location: 双向sitelink／pageprops及P31、P170、P571、P195、P276、P127、P186、P217、尺寸、委托与适用引用
  sentence_summary: 仅采用与具体版本相符且不与馆方记录冲突的字段；聚合系列QID与具体实物QID分开。
- citation: Collection or site authority record. https://www.uffizi.it/en/artworks/bacchus. Accessed 2026-09-12.
  location: 对象字段及与身份、版本、保管、安置或委托有关的说明
  sentence_summary: 为Bacchus提供具体对象或安置记录；支持范围以正文逐项注明。
process_ref: 03-processing/patrons-and-painters-chp-1/process/knowledge.md#rev-072-works-caravaggio-bacchus-uffizi
---

## 内容

### 描述

**中文：** 《巴克斯》，年代为约1596。现存。

**English:** Bacchus is dated c. 1596. It survives.

### 题名、类型与基本信息

| 字段 | 内容 | 依据 |
|---|---|---|
| 中文规范题名 | 《巴克斯》 | S1–S2 |
| 英文规范题名 | Bacchus | S2 |
| 作品类型 | 绘画；具体载体与版本见下 | S2–S4（如有） |
| 创作者／归属 | 米开朗基罗·梅里西·达·卡拉瓦乔／Michelangelo Merisi da Caravaggio | S2–S4 |
| 创作年代 | 约1596 | S1–S4 |
| 媒介与材质 | 布面油画（oil on canvas） | S2–S4（如有） |
| 尺寸 | 未载 | S2 |
| 当前保管／状态 | 乌菲齐美术馆／Uffizi Gallery；现存 | S2–S4 |
| 馆藏标识 | 5312 | S3–S4 |

### 委托、版本、存世与流传

- **对象边界：** 与《生病的巴克斯》及其他同题对象分开。
- **版本／归属状态：** 现存。

### 题材与作品说明

## 关系与证据

### 关系记录
| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| → 创作者（`created_by`） | [卡拉瓦乔（Caravaggio）](../persons/caravaggio.md) | 具体对象页将Bacchus归于卡拉瓦乔；本边保留版本边界；角色：创作者；范围：与《生病的巴克斯》及其他同题对象分开。；证据：[来源](https://www.uffizi.it/en/artworks/bacchus)；created-by-persons-caravaggio-md；本卡S2；有S4时并参对象字段 |
| → 由其保管（`held_by`） | [乌菲齐美术馆（Uffizi Gallery）](../institutions/uffizi-gallery.md) | 当前对象记录将Bacchus列由该机构保管；保管不自动等于产权；时间：本轮来源访问时；角色：保管机构；范围：现存；证据：[来源](https://www.uffizi.it/en/artworks/bacchus)；held-by-institutions-uffizi-gallery-md；本卡S2；有S4时并参对象字段 |
| → 由其委托（`commissioned_by`） | [弗朗切斯科·玛丽亚·德尔·蒙特（Francesco Maria del Monte）](../persons/francesco-maria-del-monte.md) | 来源明确该端点承担Bacchus的委托角色；不由委托推定当前所有权；时间：约1596；角色：委托人／委托机构；范围：与《生病的巴克斯》及其他同题对象分开。；证据：[来源](https://www.uffizi.it/en/artworks/bacchus)；commissioned-by-persons-francesco-maria-del-monte-md；本卡S2；有S4时并参委托／历史段 |

### 身份与外部链接

- [Wikipedia（en）：Bacchus (Caravaggio)](https://en.wikipedia.org/wiki/Bacchus_(Caravaggio))
- [Wikidata Q2011510](https://www.wikidata.org/wiki/Q2011510)
- [对象／保管机构记录](https://www.uffizi.it/en/artworks/bacchus)
