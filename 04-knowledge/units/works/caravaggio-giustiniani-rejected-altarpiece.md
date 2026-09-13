---
title: 《圣马太与天使》（第一版）（Saint Matthew and the Angel (first version)）
name_en: Saint Matthew and the Angel (first version)
type: work
created: 2026-09-09
updated: 2026-09-14
evidence_status: source_backed
relations:
- relation_type: created_by
  target: persons/caravaggio.md
  note: 柏林绘画馆对象记录确认第一版作者为卡拉瓦乔；本章退画经购藏链与该对象对应，不与后替代版本合并。
  evidence_ref:
    doc_id: smb-der-evangelist-matthaus-870411
    source_file: https://id.smb.museum/object/870411
    source_span: 本卡 S6；对象字段及对象说明全文
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
- relation_type: acquired_by
  target: persons/marchese-giustiniani-ch1.md
  note: 柏林绘画馆记录文琴佐·朱斯蒂尼亚尼购入被拒的第一版；他不是该画初始委托人。
  evidence_ref:
    doc_id: smb-der-evangelist-matthaus-870411
    source_file: https://id.smb.museum/object/870411
    source_span: 本卡 S6；对象字段及对象说明全文
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  time: 约1602后
  role: 退画购入者
  scope: 购入第一版；不是初始委托人
- relation_type: intended_for
  target: places/contarelli-chapel.md
  note: 第一版原为孔塔雷利礼拜堂祭坛而作，后被拒并由朱斯蒂尼亚尼购入。
  evidence_ref:
    doc_id: intended-for-places-contarelli-chapel-md
    source_file: https://id.smb.museum/object/870411
    source_span: 对象说明全文
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  time: 约1602
  role: 原定安置地点
  scope: 第一版；未实际长期安置
- relation_type: held_by
  target: institutions/gemaeldegalerie-berlin.md
  note: 1815年入柏林收藏，战后失踪并被馆方推测1945年毁失。
  evidence_ref:
    doc_id: held-by-institutions-gemaeldegalerie-berlin-md
    source_file: https://id.smb.museum/object/870411
    source_span: 对象说明全文
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  time: 1815–1945
  role: 历史保管机构
  scope: 第一版；现已失踪／推测毁失
sources:
- citation: 'Francis Haskell, Patrons and Painters, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), ch. 1, pp. 10.'
  location: 第一章；印刷页 10；OCR L349–353
  sentence_summary: 一幅因不适于原定地点而被拒的祭坛画，Giustiniani 为画廊购入。该段未命名，不擅定为卡拉瓦乔某一著名退画；须保持对象待精确消歧。
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/01_CHP-1.md
    source_span: lines 349–353; print pp. 10
  original_quotes:
  - source_span: "lines 349–353"
    text: |2-
      very beginning of the century the Marchese Giustiniani, whose taste is discussed in a
      later chapter, was such a wholehearted admirer of Caravaggio that, when an altarpiece
      by that artist had been rejected as unsuitable for its intended location, he acquired it for
      his gallery and hung it among a series of pictures which had been assembled far more
      for their affinities of style than for any consistency of subject-matter.2 And some ninety
- citation: Wikipedia (en), Saint Matthew and the Angel, revision 1368793918. https://en.wikipedia.org/wiki/Saint_Matthew_and_the_Angel. Accessed 2026-09-10.
  location: 导言身份段；REV-034 初步对齐，非全文补足
  sentence_summary: 《圣马太与天使》Q577248 为具体退画候选；章中未具画题，本次读到的页段未完成 Giustiniani 收购链核对，不把候选改成既定题名。
- citation: Wikidata, Q577248, revision 2388333497. https://www.wikidata.org/wiki/Q577248. Accessed 2026-09-10.
  location: labels／descriptions／P31／适用身份字段及 enwiki sitelink；判断范围见正文
  sentence_summary: 《圣马太与天使》Q577248 为具体退画候选；章中未具画题，本次读到的页段未完成 Giustiniani 收购链核对，不把候选改成既定题名。
- citation: Wikipedia (en), Saint Matthew and the Angel, revision 1368793918. https://en.wikipedia.org/wiki/Saint_Matthew_and_the_Angel. Accessed 2026-09-11.
  location: 全文语义阅读：正文、信息框、图注及注释／书目；不包含全部外链
  sentence_summary: 全文5174字符；1602退画与第二版分开，尺寸及风格段有版本混入风险；不采整页为单一无冲突对象说明。
- citation: Wikidata Q577248, revision 2388333497. https://www.wikidata.org/wiki/Q577248. Accessed 2026-09-11.
  location: 双向 sitelink／pageprops 与适用字段；含 rank、限定词、时间精度、单位及引用状态
  sentence_summary: 作者Q42207、年份1602、柏林馆号365；WD尺寸232×183厘米与馆记录不同，馆藏与原设礼拜堂亦须分清。
- citation: Staatliche Museen zu Berlin, Gemäldegalerie, Der Evangelist Matthäus, Ident. 365, ObjID 870411. https://id.smb.museum/object/870411. Record updated 2025-12-15; accessed 2026-09-11.
  location: 对象字段及对象说明全文；页面其余推荐藏品不属于此对象
  sentence_summary: 1602 年前后 Contarelli 礼拜堂退画，由 Vincenzo Giustiniani 收购，1815 年随藏品入柏林；馆记223×183厘米，战后失踪且推测1945年毁于弗里德里希斯海因防空塔。
process_ref: 03-processing/patrons-and-painters-chp-1/process/knowledge.md#rev-072-works-caravaggio-giustiniani-rejected-altarpiece
---

## 内容

### 描述

**中文：** 本章朱斯蒂尼亚尼购入的卡拉瓦乔退画，现可由柏林绘画馆对象记录对应为《圣马太与天使》第一版。该画约1602年为罗马Contarelli礼拜堂制作，后入朱斯蒂尼亚尼收藏，1815年随藏品入柏林；馆方记战后失踪，推测1945年毁于防空塔。（S1、S4–S6）

**English:** Berlin’s collection record identifies the rejected Caravaggio altarpiece bought by Giustiniani in this chapter as the first Saint Matthew and the Angel. Made around 1602 for Rome’s Contarelli Chapel, it entered the Giustiniani collection and was acquired for Berlin in 1815. The museum records it as missing since the war and probably destroyed in a flak tower in 1945. (S1, S4–S6)

### 作品字段

| 字段 | 内容 | 依据 |
|---|---|---|
| 规范题名 | 圣马太与天使（第一版）／Saint Matthew and the Angel (first version) | S4；第一版为区分标记 |
| 馆藏题名 | Der Evangelist Matthäus／The Evangelist Matthew | S6 |
| 创作者 | 米开朗基罗·梅里西·达·卡拉瓦乔／Michelangelo Merisi da Caravaggio | S5 P170、S6 |
| 时间 | 约1602；S6结构字段vor1602，说明正文写1602，两者差异保留 | S4–S6；WD P571年精度，不造1月1日 |
| 创作／原设地点 | 罗马法国圣路易堂Contarelli礼拜堂祭坛 | S4、S6 |
| 媒介 | 布面油画／oil on canvas | S4–S6；WD油彩、画布及support限定分开 |
| 尺寸 | **223×183厘米，以柏林本对象记录为当前采用值** | S6；WD232×183，WP295×195均保留为异文 |
| 馆藏标识 | 柏林绘画馆365；ObjID870411 | S5–S6 |
| 当前状态 | 馆方记战后失踪；推测1945年5月毁于柏林Friedrichshain防空塔 | S6；不写成可在展厅观看 |
| 图像描述 | 天使靠近圣马太、引导其书写，圣人赤足；现存照片可见构图，现代上色图不证明原作准确颜色 | S4、S6 |

### 委托、收藏及流传

- **原委托语境：** Contarelli礼拜堂祭坛；馆方结构字段列Matteo Contarelli，但其1585已卒，不能写作他本人1602亲自下单。（S6）
- **退画与购入：** 馆方记教会团体拒收，Vincenzo Giustiniani买入，并以给予画家另绘版本机会为条件。购买者不是该画原始委托人。（S6）
- **1815：** 随朱斯蒂尼亚尼收藏购入柏林；年份来自本对象收购字段。（S6）
- **1945及其后：** 馆方推测毁于防空塔，保留“推测”与“失踪”措辞；现存礼拜堂第二版不能填作本画如今存放地。（S6）

### 评价与研究线索

馆方以当时对使徒尊严和表现方式的要求解释拒收，同时指出Baglione传记叙述带有立场；这不等于已经找到完整拒收决定原件。百科风格段出现第一、第二版混写，未据其为本画扩写风格结论。（S4、S6）

## 关系与证据

### 关系记录
| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| → 创作者（`created_by`） | [卡拉瓦乔（Caravaggio）](../persons/caravaggio.md) | 柏林绘画馆对象记录确认第一版作者为卡拉瓦乔；本章退画经购藏链与该对象对应，不与后替代版本合并；证据：[来源](https://id.smb.museum/object/870411)；smb-der-evangelist-matthaus-870411；本卡 S6；对象字段及对象说明全文 |
| → 由其购入（`acquired_by`） | [文琴佐·朱斯蒂尼亚尼（Vincenzo Giustiniani）](../persons/marchese-giustiniani-ch1.md) | 柏林绘画馆记录文琴佐·朱斯蒂尼亚尼购入被拒的第一版；他不是该画初始委托人；时间：约1602后；角色：退画购入者；范围：购入第一版；不是初始委托人；证据：[来源](https://id.smb.museum/object/870411)；smb-der-evangelist-matthaus-870411；本卡 S6；对象字段及对象说明全文 |
| → 拟用于（`intended_for`） | [孔塔雷利礼拜堂（Contarelli Chapel）](../places/contarelli-chapel.md) | 第一版原为孔塔雷利礼拜堂祭坛而作，后被拒并由朱斯蒂尼亚尼购入；时间：约1602；角色：原定安置地点；范围：第一版；未实际长期安置；证据：[来源](https://id.smb.museum/object/870411)；intended-for-places-contarelli-chapel-md；对象说明全文 |
| → 由其保管（`held_by`） | [柏林绘画馆（Gemäldegalerie Berlin）](../institutions/gemaeldegalerie-berlin.md) | 1815年入柏林收藏，战后失踪并被馆方推测1945年毁失；时间：1815–1945；角色：历史保管机构；范围：第一版；现已失踪／推测毁失；证据：[来源](https://id.smb.museum/object/870411)；held-by-institutions-gemaeldegalerie-berlin-md；对象说明全文 |

### 身份与外部链接

- [Wikipedia：Saint Matthew and the Angel](https://en.wikipedia.org/wiki/Saint_Matthew_and_the_Angel)
- [Wikidata Q577248](https://www.wikidata.org/wiki/Q577248)
