# 第十四章候选表面提示裁决（2026-10-08）

定位器在18个reviewed/complete段中给出24条提示。逐项核对规范来源、上下文断言和候选边界后，10条映射、14条不写；定位器只覆盖现有候选词形，不代表实体召回率或语义验收。

新增3个来源候选：Mead在伦敦的绘画收藏（类型未定）、Treviso保存的Algarotti—Bonomo书信群（archive）及Augustus III扩充的古代大师收藏（类型未定）。前两组的具体边界分别缺少藏品清单和档案fonds信息；第三组与Dresden royal gallery的关系未定。未新增KU、statement或S6正式关系。

字符跨度为拼接段文本的零起点、右开区间；行号回到规范来源。索引误撞、泛称、未界定媒介组及身份未决的代词不强行写入。

| 序号 | 来源定位 | 字符跨度 | 提示原文 | 裁决/候选 | 判断依据 |
|---:|---|---:|---|---|---|
| 1 | 14_CHP-14_intro.md#L111 | 762:772 | collection | 映射 cand-11496 (Dr Richard Mead's collection of paintings seen by Algarotti in London (p.357)) | The phrase refers to Dr Richard Mead's identifiable London art collection; preserve its unspecified holdings and keep its type unresolved. |
| 2 | 14_CHP-14_intro.md#L123 | 2742:2749 | in Rome | 映射 cand-4490 (Rome) | Rome is the geographic location of Piranesi's parallel creations; use the existing Rome place candidate, not the unrelated index phrases 'in Rome'. |
| 3 | 14_CHP-14_intro.md#L140 | 11:17 | battle | 不写入 | 'Battle' is a metaphor for conflict between styles, not Salvator Rosa or a titled work. |
| 4 | 14_CHP-14_intro.md#L145 | 1526:1532 | winter | 不写入 | 'Winter' describes the season of Constable's evenings and does not identify Rosalba Carriera. |
| 5 | 14_CHP-14_intro.md#L174 | 1072:1082 | collection | 映射 cand-11497 (Large Treviso collection of letters from Francesco Algarotti to Bonomo (p.349 n.1)) | The note identifies a larger Treviso-held correspondence group, within which the separately recorded Paris letters are a subset; keep fonds and boundary unresolved. |
| 6 | 14_CHP-14_intro.md#L188 | 2860:2867 | subject | 不写入 | 'The subject' means the topic of Algarotti's ideas, not the Contracts index concept. |
| 7 | 14_CHP-14_intro.md#L192 | 3541:3547 | Venice | 映射 cand-2719 (Venice) | Venice is the city containing the two named picture locations; use the place candidate, not the topical Venice index entries. |
| 8 | 14_CHP-14_intro.md#L206 | 5966:5975 | Canaletto | 映射 cand-0499 (Canaletto) | Canaletto is named as the painter in the possessive phrase; the referenced view is separately identified in the main-text statement. |
| 9 | 14_CHP-14_intro.md#L219 | 7508:7514 | Venice | 映射 cand-2719 (Venice) | Venice is where Biffi arrived in 1773; use the geographic city candidate. |
| 10 | 14_CHP-14_intro.md#L33 | 2957:2968 | temperament | 不写入 | 'Temperament' is a general personal quality in Haskell's interpretation, not a separately identified person or work. |
| 11 | 14_CHP-14_intro.md#L6 | 95:106 | art patrons | 映射 cand-4129 (Art patrons) | 'Art patrons' is the social category in Haskell's description of Algarotti; the existing term candidate has the same category meaning. |
| 12 | 14_CHP-14_intro.md#L7 | 451:466 | artistic tastes | 不写入 | 'Artistic tastes' describes Algarotti's critical quality; it is not Joseph Smith or an independently bounded entity. |
| 13 | 14_CHP-14_intro.md#L8 | 1044:1055 | temperament | 不写入 | 'Temperament' is a general quality attributed to Algarotti, not either person candidate returned by the index matcher. |
| 14 | 14_CHP-14_intro.md#L8 | 1184:1193 | character | 不写入 | 'Receptive character' is a description of Algarotti, not Maffeo Barberini. |
| 15 | 14_CHP-14_intro.md#L39 | 1259:1284 | scholarly approach to art | 不写入 | The scholarly approach is an attributed interpretive quality, not the person candidate's index subentry or a separate work. |
| 16 | 14_CHP-14_intro.md#L50 | 1297:1304 | subject | 不写入 | 'Subject' means the generic topic assigned to a history painting, not the Contracts term. |
| 17 | 14_CHP-14_intro.md#L52 | 2979:2990 | old masters | 映射 cand-4288 (Old masters) | 'Old masters' names the broad art-historical category in the contrast with Algarotti's promotion of modern artists. |
| 18 | 14_CHP-14_intro.md#L60 | 2405:2411 | garden | 不写入 | The Italian garden is a generic pictorial setting in the sketch, not an independently identified place. |
| 19 | 14_CHP-14_intro.md#L61 | 2833:2839 | garden | 不写入 | This is the same generic garden setting described as absent from the large version; no bounded garden is identified. |
| 20 | 14_CHP-14_intro.md#L68 | 2374:2384 | collection | 映射 cand-11498 (Augustus III's collection of old masters (p.353)) | The source identifies Augustus III's collection of old masters as an object he sought to enlarge; its identity in relation to the Dresden royal gallery remains unresolved. |
| 21 | 14_CHP-14_intro.md#L68 | 2602:2618 | Italian painting | 不写入 | The 'tradition of Italian painting' is a broad historical characterization; cand-11017 refers to Italian painting as the subject of a specific catalogue, not this tradition. |
| 22 | 14_CHP-14_intro.md#L93 | 2513:2521 | drawings | 不写入 | The large number of drawings is an unbounded medium group within the collection; no separate drawing set or individual sheets are identified here. |
| 23 | 14_CHP-14_intro.md#L95 | 2885:2891 | Venice | 映射 cand-2719 (Venice) | Venice is the city of the visit discussed in this statement; use the place candidate. |
| 24 | 14_CHP-14_intro.md#L102 | 1828:1838 | collection | 不写入 | The pronoun 'their' is explicitly unresolved among the p.347 personal/joint collections, the p.355 family collection, or another group; preserve the existing identity question without forcing a mapping. |

## 写回与核验

- 表格新增：3个候选、10条mentions；未新增statement，补齐10条既有statement的候选引用。
- 写后定位器剩余14条，与14条no-write裁决逐跨度一致。定位器不证明召回完整。
- 严格S2审计：errors=[]; s2_missing=[]; candidates=11477; mentions=27347; statements=12262。
- 关系候选：2331条；本批没有写入S6正式关系。
- 决策计划SHA-256：2d584101fb48fc104d39982ecd9a83705105fd9cdd45142817946a534815d461；脚本SHA-256：69ef779da463b937d8196d49329303f843e1133b402b491b4284b31cc27a8ce6。
- 写前表SHA-256：candidates 14d110c7438e00699a4e9dbeb31c4987ab3475ed8cf756022cb9348bf70af134；mentions c75f88628b6450bcbc54566eb8a21c578fd65e7af2e7fd2e310c0038d55a78ae；statements 435bc84c80d9f49335084155e4231d36e8de62a769e6404d06a94edc951c32ef。
- 写后表SHA-256：candidates 08661d2bd55ac80f82a314a013334e0203cc51d3ab6beda7a4d6a57ba7f73eab；mentions 459ecd81f77e97bef006dca8003aba7c3731f66e4fd30a30d93c420c33a10e14；statements 37ec0304b794b839157bfd00996330612a202ff84c96283c53dbb26921205949。
- 恢复副本：C:\Users\001\AppData\Local\Temp\pnp-s2-chp14-surface-prompts-20261008-121411。

候选提示裁决不取代全书S2交接审计中的未登记实体、重复副本、跨页注释、指代、限定语、候选外键与全部关系候选复核。
