# 第十三章候选表面提示裁决（2026-10-08）

定位器在24个reviewed/complete段中给出33条提示。逐条回到规范S0来源、现有statement和候选边界裁决后，18条映射、15条不写；其中第23条是第22条已接纳“private collection”跨度内的嵌套命中。扫描只覆盖当前有类型候选词形，不代表实体召回率或语义验收。

新增cand-11495记录Northall转引中“Signor Lanetti’s [sic]”所指dealer的多媒介收藏，类型、库存和边界均未确定；新增来源断言和一个待S6审查的关系候选。另补记Albrizzi参与威尼斯思想生活的独立评价。未新增KU或正式S6关系。

字符跨度是拼接段文本的零起点、右开区间；行号回到规范来源。索引误撞、普通泛称、未界定集合及与已接受跨度重叠的子词不另写mentions。

| 序号 | 来源定位 | 字符跨度 | 提示原文 | 裁决/候选 | 判断依据 |
|---:|---|---:|---|---|---|
| 1 | 13_CHP-13_intro.md#L117 | 133:139 | Venice | 映射 cand-2719 (Venice) | Venice is the city where the plates mark the arrival of neo-classical taste; use the place candidate, not the topical Venice index subentries. |
| 2 | 13_CHP-13_intro.md#L118 | 1122:1129 | amateur | 映射 cand-3570 (Amateur) | Clement's quoted amateur describes Zanetti as a social/collecting category; use the existing term candidate and preserve the attributed wording. |
| 3 | 13_CHP-13_intro.md#L120 | 2138:2145 | subject | 不写入 | Subject-matter is a generic description of content, not the Contracts > subject index concept. |
| 4 | 13_CHP-13_intro.md#L17 | 942:950 | drawings | 不写入 | Drawings is a generic medium among works that might be commissioned for reproduction; no bounded drawing group is identified. |
| 5 | 13_CHP-13_intro.md#L17 | 1219:1236 | illustrated books | 映射 cand-1310 (Illustrated books) | Illustrated books are the eighteenth-century publication category discussed in the publisher account; the existing index term matches this context. |
| 6 | 13_CHP-13_intro.md#L17 | 1301:1309 | drawings | 不写入 | Drawings is a generic category of material commissioned for illustrated books, not the Carracci person or a named work group. |
| 7 | 13_CHP-13_intro.md#L18 | 1690:1707 | illustrated books | 映射 cand-1310 (Illustrated books) | The phrase names the two broad categories of eighteenth-century Venetian illustrated books already distinguished in this statement. |
| 8 | 13_CHP-13_intro.md#L163 | 434:442 | drawings | 不写入 | The younger Zanetti's drawings and prints are described as a practice and linked to Varie Pitture; no separate, bounded set is identified here. |
| 9 | 13_CHP-13_intro.md#L167 | 1503:1513 | collection | 映射 cand-7618 (Raccolta di centododici stampe di pittura della storia sacra (Pietro Monaco, Venezia 1763)) | Such a collection refers to Monaco's 112-plate print publication discussed immediately before; keep its edition mapping unresolved against the separate 1779 candidate. |
| 10 | 13_CHP-13_intro.md#L183 | 420:426 | Venice | 映射 cand-2719 (Venice) | Venice is the geographic context of the footnote's account of eighteenth-century engraving; this is not a topical subentry. |
| 11 | 13_CHP-13_intro.md#L240 | 7932:7942 | collection | 映射 cand-11495 (Collection reported at Signor Lanetti's [sic] (contextually identified as A. M. Zanetti; scope unresolved)) | Northall's quoted report identifies a multi-medium collection at the dealer contextually identified as A. M. Zanetti; preserve the printed Lanetti spelling and unresolved inventory boundary. |
| 12 | 13_CHP-13_intro.md#L240 | 7959:7967 | drawings | 不写入 | Drawings is one medium in the dealer's reported collection, not an independently identified drawing set. |
| 13 | 13_CHP-13_intro.md#L22 | 229:239 | collection | 不写入 | The noble's collection is an unnamed instance of the commemorative-publication category; its owner and contents are not identified as a separate object. |
| 14 | 13_CHP-13_intro.md#L26 | 1509:1515 | Venice | 映射 cand-2719 (Venice) | Venice is the city named in the title and description of Albrizzi's guide; the statement already links the city candidate. |
| 15 | 13_CHP-13_intro.md#L26 | 1693:1699 | Venice | 映射 cand-2719 (Venice) | Venice is the setting for Haskell's separate assessment of Albrizzi's role in its intellectual life. |
| 16 | 13_CHP-13_intro.md#L9 | 1109:1126 | illustrated books | 映射 cand-1310 (Illustrated books) | Lavishly illustrated books are the publication category in Haskell's account of export-oriented publishers. |
| 17 | 13_CHP-13_intro.md#L12 | 1915:1923 | drawings | 不写入 | Drawings describes illustrations within the named Teatro delle Pitture publication; no independent drawing group is identified. |
| 18 | 13_CHP-13_intro.md#L12 | 2496:2505 | character | 不写入 | Out of character is an idiom about style, not the unrelated character index entry. |
| 19 | 13_CHP-13_intro.md#L33 | 1031:1042 | altarpieces | 不写入 | Altarpieces is a generic category of Piazzetta's religious work, not the Poussin index subentry. |
| 20 | 13_CHP-13_intro.md#L33 | 1359:1368 | portraits | 不写入 | Hieratic portraits is a generic image category in the Bossuet illustration discussion, not Schulenburg's portrait subentry or a bounded group. |
| 21 | 13_CHP-13_intro.md#L47 | 1028:1036 | drawings | 不写入 | The occasional drawings supplied by several artists for Albrizzi's firm are not a bounded or titled set. |
| 22 | 13_CHP-13_intro.md#L49 | 1339:1357 | private collection | 映射 cand-10007 (Giambattista Albrizzi’s private collection of drawings and paintings by Piazzetta) | Private collection identifies the bounded, type-unresolved Albrizzi holdings of Piazzetta drawings and paintings, not Albrizzi the person. |
| 23 | 13_CHP-13_intro.md#L49 | 1347:1357 | collection | 不写入 | This nested collection hit lies within the accepted private collection span at prompt 22; a second mention would overlap the same words. |
| 24 | 13_CHP-13_intro.md#L49 | 1396:1404 | drawings | 映射 cand-10007 (Giambattista Albrizzi’s private collection of drawings and paintings by Piazzetta) | The several hundred drawings are part of the same source-described Albrizzi collection; no individual sheets are inferred. |
| 25 | 13_CHP-13_intro.md#L53 | 900:917 | illustrated books | 映射 cand-1310 (Illustrated books) | The fine illustrated books are the eighteenth-century publication category in the Smith/Pasquali passage. |
| 26 | 13_CHP-13_intro.md#L55 | 1338:1350 | presentation | 不写入 | Presentation describes the comparative design of a book, not Solimena's Presentation work. |
| 27 | 13_CHP-13_intro.md#L64 | 955:961 | school | 不写入 | School is a generic educational setting in Perugia, not Padre Lodoli's school candidate. |
| 28 | 13_CHP-13_intro.md#L65 | 1557:1565 | drawings | 映射 cand-10013 (Novelli illustration program for Pasquali’s Goldoni edition) | The drawings are the specific Novelli illustration program for Pasquali's Goldoni edition, already represented by cand-10013. |
| 29 | 13_CHP-13_intro.md#L68 | 2570:2577 | Jesuits | 映射 cand-1321 (Jesuits) | Jesuits names the Society Zatta supported; reuse the institution candidate used by the existing statement. |
| 30 | 13_CHP-13_intro.md#L72 | 487:494 | Jesuits | 映射 cand-1321 (Jesuits) | The quoted phrase about finding Jesuits everywhere names the same institution; retain the satirical framing. |
| 31 | 13_CHP-13_intro.md#L83 | 1179:1190 | art patrons | 映射 cand-10045 (Print sellers as art patrons) | In this sentence the phrase describes print sellers' role as art patrons; use the source-local concept candidate, not the broad library subject heading. |
| 32 | 13_CHP-13_intro.md#L83 | 1327:1336 | Remondini | 映射 cand-2123 (Remondini) | Remondini refers to the publishing firm in the p.340 account; use the index candidate scoped to this chapter passage. |
| 33 | 13_CHP-13_intro_plates_visual-transcription.md#L3 | 159:165 | school | 不写入 | School is a generic setting in the Goldoni caption, not Padre Lodoli's institution. |

## 写回与核验

- 表格新增：1个类型待定候选、18条mentions、2条statement；另更新8条statement的候选引用。新增statement中1条记录Albrizzi评价，1条把Northall引文中的收藏主张与原有dealer识别拆开。
- 写后定位器剩余14条，等于未被已接纳跨度遮盖的no-write残余；另1条嵌套提示随父跨度消失。定位器不证明召回完整。
- 严格S2审计：errors=[]; s2_missing=[]; candidates=11474; mentions=27337; statements=12262。
- 关系候选：2331条；此批新增1条开放端点完整的来源关系候选，没有写入正式关系表。
- 决策计划SHA-256：51983375574b5b8aa3c857cdbd2a4aaa0e8a36957f56cdd4fd831257394184f8；脚本SHA-256：e7e76c8d2e30abd9b2a2afbf2748c0a39549a56f7017127fdf514e5f59c57306。
- 写前表SHA-256：candidates da4d8ff5b7e2ddaad15fa47fb83d48ab73071607d84b13e41885bb844e68ccda；mentions 69a9e8efad682814c6d6a18f4e4ed439cef7c9453a16875214cd2497206ee566；statements c1b5a0eea7d2d44c38c9b3965129ef9e9efd0019fe8bc3098177e18af3754445。
- 写后表SHA-256：candidates 14d110c7438e00699a4e9dbeb31c4987ab3475ed8cf756022cb9348bf70af134；mentions c75f88628b6450bcbc54566eb8a21c578fd65e7af2e7fd2e310c0038d55a78ae；statements 435bc84c80d9f49335084155e4231d36e8de62a769e6404d06a94edc951c32ef。
- 恢复副本：C:\Users\001\AppData\Local\Temp\pnp-s2-chp13-surface-prompts-20261008-120309。

候选提示裁决不取代全书S2交接审计中的未登记实体、重复副本、跨页注释、指代、限定语、外键与全部关系候选复核。
