# 第十六章候选表面提示裁决（2026-10-08）

定位器在7个reviewed/complete段中给出11条提示。逐项核对S0来源、前后文、现有statement与候选边界后，6条写入提及、5条不写。扫描仅定位已有候选标签，不代表实体召回率或语义验收。

本批补入Sasso目录中“100 drawings”及Canaletto/Carlevarijs素描组，分别保留为工作组候选；复用Guardi一幅绘画加七幅素描组及Modelli术语。新增Toninotto收藏候选和其相似性断言，将“collection includes...”两条statement的subject改为该收藏候选。Sasso原有小型私人收藏说明更新为反映p.374–375后续记录，但未把目录未核实的完整清单写成事实。

| 序号 | 来源定位 | 提示跨度 | 提示原文 | 写入提及/裁决 | 判断依据 |
|---:|---|---:|---|---|---|
| 1 | 16_CHP-16_intro.md#L20 | 1044:1052 | drawings | drawings → cand-10611 (Unidentified Guardi drawings Strange wanted clear, finished, paired, and accurately coloured) | The request concerns the specifically described unidentified Guardi drawings Strange wanted clear, finished, paired, and accurately coloured; it is not Carracci's index subentry. |
| 2 | 16_CHP-16_intro.md#L22 | 2882:2890 | drawings | 100 drawings → cand-11500 (One hundred unidentified drawings in Giammaria Sasso's posthumous collection) | The exact count identifies a bounded group in Sasso's collection auctioned in 1803. No makers, titles, or present locations are supplied. |
| 3 | 16_CHP-16_intro.md#L22 | 2906:2913 | modelli | modelli → cand-1674 (Modelli) | Here modelli names the art-object category in Sasso's collection; reuse the indexed Modelli term, not the Andrea Sacchi index subentry. |
| 4 | 16_CHP-16_intro.md#L25 | 26:34 | drawings | drawings and sketches → cand-11501 (Drawings and sketches by Canaletto and Carlevarijs in Giammaria Sasso's auctioned collection) | The catalogue-list context identifies a distinct group of drawings and sketches by two named makers in Sasso's auctioned collection. Its count and individual works remain unspecified. |
| 5 | 16_CHP-16_intro.md#L25 | 103:111 | drawings | seven drawings → cand-10628 (One Guardi painting and seven Guardi drawings in Sasso's auctioned collection) | The source's full phrase identifies the already registered combined group of one Guardi painting and seven Guardi drawings. |
| 6 | 16_CHP-16_intro.md#L42 | 855:863 | drawings | 不写入 | Many drawings and paintings by four artists is an uncounted, unbounded plural description; the named artists and Haskell's collection statement are already represented. |
| 7 | 16_CHP-16_intro.md#L42 | 1012:1021 | portraits | 不写入 | Capricious bust portraits describes a popular genre, not Schulenburg's indexed portrait group or a separately identified set. |
| 8 | 16_CHP-16_intro.md#L44 | 2280:2290 | collection | collection → cand-11502 (Giuseppe Toninotto's art collection) | His collection refers to Toninotto's art collection described in the following inventory; it is not Cardinal Borghese's collection index subentry. |
| 9 | 16_CHP-16_intro.md#L59 | 2063:2073 | collection | 不写入 | Similar collection and patronage is a group-level comparison, not an independently identified collection. |
| 10 | 16_CHP-16_intro.md#L64 | 2631:2641 | collection | 不写入 | Own collection is a possessive reference within the existing claim about the Tiepolo letter; it does not identify a separately bounded collection. The letter's reported provenance is already recorded. |
| 11 | 16_CHP-16_intro.md#L74 | 1110:1118 | drawings | 不写入 | Prints and drawings is an unenumerated group in the note. The two 1805 Richardson auctions and Haskell's statement are already represented; no separate work group is identified. |

## 写回与核验

- 表格新增：3个候选、6条mentions和1条statement；核对4条既有statement的候选引用，实际新增5个引用；另更新1条候选detail、修正2条collection内容statement的subject候选。
- 写后定位器剩余5条，与5条no-write提示逐跨度一致。定位器不证明召回完整。
- 严格S2审计：errors=[]; s2_missing=[]; candidates=11481; mentions=27362; statements=12263。
- 关系候选：2331条；本批没有新增关系候选或写入S6正式关系。
- 决策计划SHA-256：5ac5b1e5a91c602856d3c3161e67d93e83bcd62ac9fd5d9d43e9fc9e80a4ddf4；脚本SHA-256：5961bcfe8f713aa0ad0d63a8515e4f5a5b6d045771ebbf2f935c20316934a8aa。
- 写前表SHA-256：candidates 78266078cf48f1ade43e79bcdb4378334328a3a7c29fad61680803e7a4e3653f；mentions 87aaea0cffe74f7b3057595911a11e954484b8ee292d6d330348a7d823c40a7e；statements 6f4769d0af0d52a375af1d0ee979a9c23d5accf147db2252ba57580b33b1b203。
- 写后表SHA-256：candidates 6023c8aa8fcc959e854a101728e655867417e0ba62b1d35f1915ad1030d77c83；mentions 79dae349284d081e8f5fe222eb2214dcd251bebd4c1025ff16c7a6dabfb57d3a；statements 39974e07b374feb299aa067cf1123f11e870f889e0059fdd2042668c0a4f50f2。
- 恢复副本：C:\Users\001\AppData\Local\Temp\pnp-s2-chp16-surface-prompts-20261008-124016。

候选提示裁决不取代全书S2交接审计中的未登记实体、重复副本、跨页注释、指代、限定语、候选外键与全部关系候选复核。

## 第十六章 p.373 Sasso 与新一代赞助人语义复审（2026-10-09）

对照`CHP-16.pdf`物理页1复核正文`chp-16:16_CHP-16_intro:l3-14`及合并注释L69–71中的注1–2。页图未显示印刷页码，依连续页序判为p.373。正文31条statement、注释11条statement；新增26条statement、3个候选和4条mention。将新赞助人及其趣味、较低社会地位画家的艺术传统、Guardi评价、代理人/收藏者形象与Sasso活动拆为独立断言；分开私人收藏、买卖、代理业务、书信/交往、写作、计划未完成著作、履历及与Strange的互动。采购句与p.374画家清单保持双向跨页链接。

注1分开Longhi人物、Sasso肖像、肖像说明与Bollettino引注；注2分开Strange与Sasso通信来源、Epistolario Moschini、Biblioteca Correr和Venice地点、Mauroner引信、回复缺失及英国博物馆所藏四封信。重映射Sasso、Longhi和Venice提及，避免把人物名映射到索引肖像作品候选。20条关系候选端点20/20齐备，仍为S2候选，没有KU、对齐或S6正式关系变动。

记录10处印本/OCR差异仅供S2使用，S0及PDF未改。42条statement引文均锚定来源，36条mention字符跨度和候选引用均通过；脚注与跨页链接通过。受控脚本为`process/chp16_p373_sasso_semantic_review.py`，写前dry-run检查来源、PDF和三表哈希；修正脚本基线哈希和跨行引文范围后才应用。恢复副本保存在`04-knowledge/tables/`，文件名后缀`.bak-s2-chp16-p373-semantic-review-20261009`。

写后严格审计`errors=[]`、`s2_missing=[]`。下一处按书序为p.374 `chp-16:16_CHP-16_intro:l16-22`及相应注释；本次复审不表示全书S2交接完成。

## 第十六章 p.374 Sasso 段与注1–4语义复审（2026-10-09）

对照`CHP-16.pdf`物理页2复核正文L17–22和注L72–75。首轮数据细化为33条正文statement、6条注释statement、50条正文mention及14条注释mention；净增20条statement、4个候选（cand-11546–11549）和9条mention。拆开暂存/可能出售、贸易条件、Guardi评价与Strange态度、收藏及审美、Armanni身份/旅行/引语、Canova的modello请求与被Haskell否定的收购说法，并分离1803年拍卖事件与藏品清单。注3的档案定位、Poore日期信件及拍卖记录各自成statement。11条关系候选端点齐备；无KU、对齐或正式关系新增。

印本校读8项仅记入S2，原始S0不变。注1–4按正文标记回链；p.373购画列表与p.374现代画家续句、p.374收藏清单与p.375续表的双向链接均已闭合。首轮严格审计报出续表`cross_reference_text_pending`，按已完成p.375 statement核实后单字段修正；最终`errors=[]`、`s2_missing=[]`，全量同步闭合303 passed、2 subtests passed。详细方法、证据及恢复副本见[过程记录](../process/stages.md)。全书S2交接仍未完成；下一顺序先核当前p.375结果，再到p.376 `chp-16:16_CHP-16_intro:l38-46`。

## 第十六章 p.376 语义复审（2026-10-09）

对照CHP-16.pdf物理页4复审印刷p.376正文L39–46及注1–3。当前正文40条statement、50条mention，注释3条statement；本次新增13条statement和1条mention，未新增候选或KU。将Vianello的出版、藏品、审美评价与身份不确定性分开；细化Toninotto和del Pian版画组/题材、古画、modelli及各艺术家作品组；分开Swajer传记、一般手稿收藏与秘密手稿可能散佚。19条正文关系候选端点齐备，仍为S2候选。

10项印本校读只记入S2，不改S0。脚注1回连1790年图录出版statement；p.376正文续至p.377，注3的8条续注statement也保持链接，待下一页复核。受控脚本process/chp16_p376_semantic_refine_20261009.py经dry-run及SHA校验后应用，43条本页statement引文锚点核验通过；恢复副本保留于04-knowledge/tables。严格表审计errors=[]、s2_missing=[]。全量同步闭合303 passed、2 subtests passed，结构契约130/130。下一处为p.377 chp-16:16_CHP-16_intro:l48-64及注3续文；本页复审不表示全书S2交接完成。详见过程记录。

## 第十六章 p.377–378 语义复审（2026-10-09）

p.377正文、p.376注3续文与p.377页下注1–5复核后共49条statement；本次新增15条statement、3个候选和3条mention。拆分Swajer手稿散佚焦虑与宗教裁判官收取手稿；区分Celotti的藏品、销售、城市活动与图录评价；分列注3的Christie's销售定位和Ottley描述；注5拆出两类1814年作品组销售、目录引注与手写增补说明。新候选cand-11550–11552分别表示Tiepolo销售组、Piazzetta销售组及两幅Tiepolo素描组。p.377正文印本标号6与页底注5保持`mismatched`，无强制回链。

p.378结论现为4条组级statement：经销者生计、收藏趣味变化、时间带来的回顾变化、Haskell的‘威尼斯传统守护者’隐喻。Sasso群体回指从错误的索引购买事件cand-2367改为人物cand-2364；其余五人端点亦逐一核对。未将组级判断转成正式个人关系。严格表审计`errors=[]`、`s2_missing=[]`；全库1,019 KU、11,530 candidates、27,463 mentions、12,641 statements、2,806条关系候选（2,774端点齐备、32开放）。无KU、alignment或S6关系新增。p.378完成后转入全书S2交接审计；S2仍未交接。详细依据及恢复副本见[过程记录](../process/stages.md)。
