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
