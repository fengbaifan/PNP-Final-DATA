---
title: "威尼斯圣母纳匝肋堂（Church of S. Maria di Nazareth, Venice; Scalzi church）"
name_en: "Church of S. Maria di Nazareth, Venice; Scalzi church"
type: place
evidence_status: source_backed
sources:
  - citation: "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), index, C.csv #262."
    location: "本书索引 C.csv #262；子目列印刷页268–270。"
    sentence_summary: "索引将S. Maria di Nazareth作为Scalzi church的子目，定位到第9章印刷页268–270。"
    original_quotes:
      - source_span: "Index C.csv #262"
        text: "S. Maria di Nazareth (Scalzi church)"
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/03-Index/03-2-Index-CSV/C.csv
      source_span: "row 262"
  - citation: "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), ch. 9, printed p. 269."
    location: "第9章印刷页269，L21–23；PDF物理页35。"
    sentence_summary: "Haskell称Scalzi原教堂过小，Longhena和Sardi受聘建造新堂；他报告立面费用为74,000 ducats，由Conte Cavazza支付。"
    original_quotes:
      - source_span: "lines 21–23; printed p. 269"
        text: |-
          Such was their popularity that their original church became much too small, and Longhena and
          Sardi were employed to build a new one. Nobles quarrelled for the privilege of erecting the High Altar, and the façade, which cost 74,000 ducats, was paid for by a Conte
          Cavazza, who had been admitted to the patriciate in 1653.
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/09_CHP-9_sec_ii.md
      source_span: "lines 21–23; printed p. 269; PDF physical p. 35"
created: '2026-10-22'
updated: '2026-10-22'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp9-churches-artwork-endpoints-20261022
---

## 内容

### 描述

**中文：** 本卡记录Haskell第9章及其索引所指的威尼斯Scalzi新教堂；索引子目为S. Maria di Nazareth。该身份范围限于本书，不把教堂与Scalzi修会合并，也不推断现存建筑状态或现代身份。

**English:** This unit records the new Venetian Scalzi church identified by the Chapter 9 index subentry S. Maria di Nazareth. The identity is limited to Haskell's book; the building is distinct from the Scalzi religious order, and no present condition or modern identity is inferred.

### 名称

| 字段 | 值 | 证据 |
| --- | --- | --- |
| 索引子目名称 | S. Maria di Nazareth (Scalzi church) | 本书索引 C.csv #262。 |

### 基本信息

| 字段 | 值 | 证据 |
| --- | --- | --- |
| 地点性质 | 威尼斯Scalzi修会的新教堂；与修会机构及原教堂分别记录。 | 第9章印刷页269 L21–23；书内叙述与索引范围，不推断现代身份。 |
| 原教堂与新堂 | Haskell称修会受欢迎使原教堂过小，Longhena与Sardi受聘建造新堂。 | 第9章印刷页269 L21–22；建造角色分别列关系，不推断设计角色。 |
| 立面费用 | 74,000 ducats（Haskell所报）。 | 第9章印刷页269 L22–23；书内报告金额。 |
| 立面付款报告 | Haskell称Conte Cavazza支付了立面费用；付款人与委托人角色是否相同仍待证。 | 第9章印刷页269 L22–23；仅记录付款报告，S6关系保持pending。 |

### 本章相关内容

Haskell reports that the original church had become too small and that Longhena and Sardi were employed to build a replacement. He also reports a 74,000-ducat façade paid for by a Conte Cavazza. The building roles are recorded separately from the payment question; the latter remains pending S6 review.

## 关系与证据

### 身份与外部链接

仅采用本书索引和叙述形成的书内身份；未核对外部建筑目录。

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| → 委托其建造（`entrusted_to_build`） | [巴尔达萨雷·隆盖纳（Baldassare Longhena）](../persons/baldassare-longhena.md) | 角色：建造者；范围：Haskell says Longhena and Sardi were employed to build the replacement Scalzi church after the original church became too small. This records Longhena’s builder role only, not design or completion.；证据：[来源](../../../02-sources/02-Markdown/09_CHP-9_sec_ii.md)；haskell-1980-rev-ed；Chapter 9, printed p. 269, L21–22; S2 statement: st-chp9-p269-scalzi-replacement-church-longhena |
| → 委托其建造（`entrusted_to_build`） | [朱塞佩·萨尔迪（Giuseppe Sardi）](../persons/giuseppe-sardi.md) | 角色：建造者；范围：Haskell says Longhena and Sardi were employed to build the replacement Scalzi church after the original church became too small. This records Sardi’s builder role only, not design or completion.；证据：[来源](../../../02-sources/02-Markdown/09_CHP-9_sec_ii.md)；haskell-1980-rev-ed；Chapter 9, printed p. 269, L21–22; S2 statement: st-chp9-p269-scalzi-replacement-church-sardi |
| → 待证：由其委托（`commissioned_by`） | [卡瓦扎伯爵（Count Cavazza）](../persons/conte-cavazza.md) | 状态：待证；Direct payer attribution is supported; mapping it to commissioned_by would overstate the role.；角色：立面付款人（是否为委托人待证）；范围：Haskell directly says Conte Cavazza paid for the façade, but payment alone does not establish that he commissioned it. Keep pending until payer is distinct from commissioner in the controlled relation vocabulary.；证据：[来源](../../../02-sources/02-Markdown/09_CHP-9_sec_ii.md)；haskell-1980-rev-ed；Chapter 9, printed p. 269, L22–23; S2 statement: st-chp9-p269-cavazza-paid-facade |

### 关系候选入口

[本批逐项S3–S6裁决与边界](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp9-churches-artwork-endpoints-20261022)
