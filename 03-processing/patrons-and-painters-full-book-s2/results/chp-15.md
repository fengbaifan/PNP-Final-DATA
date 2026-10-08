# 第十五章候选表面提示裁决（2026-10-08）

定位器在17个reviewed/complete段中给出16条提示。逐项核对规范来源、前后文和候选边界后，9条映射、7条不写；扫描只匹配已有候选词形，不代表实体召回率或语义验收。

新增cand-11499记录匿名当代引文所说的Farsetti别墅‘collection of rarities’，类型、清单和与Farsetti其他藏品的边界均未确定；同时将原有villa评价statement补全为含该引文内容。其余映射复用Rome、Venice、Memmo家族宫殿、Querini被捕事件、Alticchiero书籍集合及Querini花园候选；‘reforming prince’回连到本句前文所述但身份未名的Grand Duke。未新增statement或S6正式关系。

字符跨度为拼接段文本的零起点、右开区间；行号回到规范来源。索引误撞、泛称、未界定对象和与已接纳跨度重叠的子词不另造mentions。

| 序号 | 来源定位 | 字符跨度 | 提示原文 | 裁决/候选 | 判断依据 |
|---:|---|---:|---|---|---|
| 1 | 15_CHP-15_sec_i.md#L28 | 541:551 | collection | 映射 cand-11499 (Collection of rarities associated with Farsetti's villa at S. Maria di Sala (p.363)) | The contemporary quotation identifies a collection of rarities associated with Farsetti's villa; its inventory and relation to his other holdings remain unspecified. |
| 2 | 15_CHP-15_sec_i.md#L8 | 1064:1073 | portraits | 不写入 | 'Portraits' describes a generic genre in which Alessandro Longhi worked, not Schulenburg's indexed portrait group. |
| 3 | 15_CHP-15_sec_i.md#L12 | 1793:1803 | collection | 不写入 | 'Forming a collection there' is a general statement about collecting interest in Venice, not an identified collection or collector. |
| 4 | 15_CHP-15_sec_ii.md#L20 | 1890:1897 | in Rome | 映射 cand-4490 (Rome) | Rome is the geographic setting in which Memmo continued urging friends to contribute statues; use the existing Rome place candidate. |
| 5 | 15_CHP-15_sec_ii.md#L41 | 1007:1013 | palace | 映射 cand-10517 (Andrea Memmo family palace, location unspecified in Haskell p.368) | 'This palace' refers back to the Memmo family palace named in the preceding sentence; use its existing place candidate. |
| 6 | 15_CHP-15_sec_ii.md#L44 | 1347:1353 | Venice | 映射 cand-2719 (Venice) | Venice is the city from which Querini emerged as a major patron; use the geographic place candidate. |
| 7 | 15_CHP-15_sec_ii.md#L51 | 418:424 | arrest | 不写入 | This single-word 'arrest' span is nested within the accepted event phrase 'arrest and detention' at prompt 8; a second mention would overlap the same event wording. |
| 8 | 15_CHP-15_sec_ii.md#L51 | 418:438 | arrest and detention | 映射 cand-2079 (Querini, Angelo — arrest and detention) | This is Querini's specific arrest and detention event indexed at p.369; accept the full phrase so the nested generic 'arrest' prompt is not duplicated. |
| 9 | 15_CHP-15_sec_ii.md#L9 | 2294:2301 | subject | 不写入 | 'Subject' means the topic of a statue chosen by a donor, not the Contracts index concept. |
| 10 | 15_CHP-15_sec_ii.md#L10 | 2918:2926 | churches | 不写入 | 'Churches' is a generic comparison class; no bounded group of pilgrimage churches is identified. |
| 11 | 15_CHP-15_sec_ii.md#L62 | 349:359 | collection | 映射 cand-10547 (Library at Alticchiero with classics and books on agriculture, philosophy, and theology) | The phrase names the subject-matter book collection in the Alticchiero library, already recorded as cand-10547. |
| 12 | 15_CHP-15_sec_ii.md#L64 | 1288:1294 | garden | 映射 cand-2081 (Querini, Angelo — garden) | This is the garden indexed under Querini at p.370 and described as part of the Alticchiero estate; retain the index-derived candidate pending S3 identity review. |
| 13 | 15_CHP-15_sec_ii.md#L70 | 40:51 | temperament | 不写入 | 'Temperament' is a general quality attributed to Querini, not either unrelated Algarotti index candidate. |
| 14 | 15_CHP-15_sec_ii.md#L74 | 736:742 | prince | 映射 cand-4302 (Grand Duke of Tuscany (individual not identified in this passage)) | The 'reforming prince' is the unnamed Grand Duke of Tuscany identified immediately before; reuse the same person candidate without inferring his individual identity. |
| 15 | 15_CHP-15_sec_ii.md#L75 | 1060:1066 | garden | 映射 cand-2081 (Querini, Angelo — garden) | The later possessive reference is to the same Querini garden described at p.370; use cand-2081. |
| 16 | 15_CHP-15_sec_ii.md#L76 | 1430:1439 | character | 不写入 | 'Character' refers to the restraint and lack of excess treated as a quality of the sculpture, not Pope Urban VIII. |

## 写回与核验

- 表格新增：1个候选、9条mentions；未新增statement；核对9条既有statement的候选引用，实际新增3个引用，并修订1条claim及限定语。
- 写后定位器剩余6条；prompt 7嵌套于已接纳的prompt 8，随完整事件跨度被覆盖。其余提示与no-write裁决逐跨度一致。定位器不证明召回完整。
- 严格S2审计：errors=[]; s2_missing=[]; candidates=11478; mentions=27356; statements=12262。
- 关系候选：2331条；本批没有新增关系候选或写入S6正式关系。
- 决策计划SHA-256：fae8f396c7f91d6bc6064a9ea6c698c5e5a6fd456fdc0b0115d7c2a3dd9d9c47；脚本SHA-256：963c2ad7fe2227822b8ae4bb05276f19a538dd3cd28e2bbc28d844f047015c1c。
- 写前表SHA-256：candidates 08661d2bd55ac80f82a314a013334e0203cc51d3ab6beda7a4d6a57ba7f73eab；mentions 459ecd81f77e97bef006dca8003aba7c3731f66e4fd30a30d93c420c33a10e14；statements 37ec0304b794b839157bfd00996330612a202ff84c96283c53dbb26921205949。
- 写后表SHA-256：candidates 78266078cf48f1ade43e79bcdb4378334328a3a7c29fad61680803e7a4e3653f；mentions 87aaea0cffe74f7b3057595911a11e954484b8ee292d6d330348a7d823c40a7e；statements 6f4769d0af0d52a375af1d0ee979a9c23d5accf147db2252ba57580b33b1b203。
- 恢复副本：C:\Users\001\AppData\Local\Temp\pnp-s2-chp15-surface-prompts-20261008-122515。

候选提示裁决不取代全书S2交接审计中的未登记实体、重复副本、跨页注释、指代、限定语、候选外键与全部关系候选复核。
