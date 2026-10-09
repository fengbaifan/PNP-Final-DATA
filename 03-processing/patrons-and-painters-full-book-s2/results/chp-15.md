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

## 第十五章p.361正文与脚注交接复审（2026-10-09）

对照`CHP-15.pdf`物理页1复核`chp-15:15_CHP-15_sec_i:l3-14`正文，并跨文件检查`chp-15:15_CHP-15_intro:l7-9`脚注。补入此前遗漏的章节内人名标题`FILIPPO FARSETTI`（`m-chp15-p361-0054`，`cand-1002`，跨度0:16）；跨章身份保留待S3。更正注1、注2断言中的印刷页号，从p.362改为p.361。根据注2明载的信件收发人，新增`cand-10426`→Mariette（`cand-1547`）`authored_by`及→Temanza（`cand-2546`）`addressed_to`两条S2关系候选；信件与刊本未独立查阅，未生成S6边。

本段候选词形定位器没有提示`FILIPPO FARSETTI`，因为索引名为倒置词序；该漏项由印本标题与S0复核发现。p.361完成后下一项是p.362正文`chp-15:15_CHP-15_sec_i:l16-25`。全书交接计数和未决项以[全书当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)为准。

## 第十五章p.362正文语义复审（2026-10-09）

对照`CHP-15.pdf`物理页2复核正文段`chp-15:15_CHP-15_sec_i:l16-25`。73条mention字符跨度均吻合，44条statement引文均可在指定S0段定位；印本`milord, employing`与S0 OCR连写`milord,employing`的差异记入S2校读，不改来源。补录6条定位明确的statement，细分别墅位置、拟容纳的收藏、柱群来源与Rome地理限定；增加Farsetti居住巴黎、威尼斯新古典运动角色及别墅/柱群关系候选。Lodoli启发“三位赞助人”的对象集合保持开放。修正`cand-10430`跨页说明与`cand-9206`使用范围；未新增候选、KU、mention或正式关系。全库12,405条statement、2,644条关系候选（23条开放）；下一项p.363正文与注释。

## 第十五章p.363正文与注释语义复审（2026-10-09）

对照`CHP-15.pdf`物理页3复核正文`chp-15:15_CHP-15_sec_i:l27-36`及注释`chp-15:15_CHP-15_sec_i:l43-56`。纠正注1误连：标记跟随教皇转移财产句，不属于million-ducats支出说法。把整段别墅赞誉归于匿名当代引文；注2所引Boscovich致Vallisnieri信件不证明赞誉作者身份。修正Canova study 与Palazzo Farsetti、花园与别墅的关系方向；不把“Venetian painting and sculpture”连到Venice地名。新增Canova创作两只首批花篮、花篮被放在宫邸楼梯、Algarotti的古典范式理论归属、注2信件作者和收信人四条statement。对正文和注释记录9项印本校读；S0与原始引文保持不变。正文段现35条statement、69条mention、23条关系候选（3条开放）；无新增candidate、KU、mention或正式关系。全库12,409条statement、2,659条关系候选（2,633条端点完整、26条开放）；引文锚点12,363条精确、46条空白归一、0条未匹配。详见[过程记录](../process/stages.md)与[全书当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。下一项为p.364 `chp-15:15_CHP-15_sec_i:l38-41`。

## 第十五章p.362正文与脚注语义复审（2026-10-09）

对照`CHP-15.pdf`物理页2复核`chp-15:15_CHP-15_sec_i:l16-25`。73条既有mention的字符跨度逐条复算无误；44条statement引文均可在S0段落内定位。印本“milord, employing”被S0 OCR连写为“milord,employing”，只在对应statement的`ocr_corrections`记录，不改原文或引文。p.362注1–2的印刷页号与页图一致，且仍与L17正文标记双向链接；p.362末句与p.363 L28的续接、注1的跨页关系保持链接。

复核后本段为44条statement、73条mention。补录6条精确锚点statement：Farsetti别墅位于S. Maria di Sala家族产业；别墅拟容纳索引中分别列出的石膏像模与绘画收藏；石膏像模收藏在家族宫邸组建；42根多立克柱的来源为Dea Concordia神庙；来源文字称该庙位于Rome。将“洛多利是本章三位赞助人的直接启发者”列为一条S2关系候选，但目标集合未逐名列出，保持开放。另把Farsetti居住巴黎、其在威尼斯新古典运动中的角色、别墅与柱群关系补入S2候选；不生成S6正式关系。`cand-10430`的跨页说明和`cand-9206`的使用范围已按本页证据修正；未增加候选、KU或mentions。

全库现有1,019 KU、11,503候选、27,425 mentions、12,405 statements；S2关系候选2,644条，其中2,621条两端齐全、23条开放。严格阶段审计`errors=[]`、`s2_missing=[]`；本段44条statement引文全部在指定S0段内精确定位，73条mention跨度全部吻合。两条既存`enrichment source_ref`警告保持不变。p.362完成后下一项按书序为p.363正文`chp-15:15_CHP-15_sec_i:l27-36`及其跨页注释。

## 第十五章 p.364 Farsetti 段复审（2026-10-09）

按印刷页图复核 p.364 L39–41 及 p.363→364 跨页句。正文21条 statement、30条 mention；原复合主张拆分并新增8条 statement。指代“This”明确为 Tommaso 举报 Anton 的事件，新增开放事件候选 cand-11525；note 1 所引 Inquisitori di Stato 档案未独立查阅。Tommaso 的书籍／手稿收藏 cand-10465 类型未定；家族记述作者候选 cand-10443 的同一性留待 S3；Anton 为 Tommaso 侄子作为关系候选记录。

“the collections”未绑定铸像或绘画收藏候选，所售项目仍未逐项识别；“the property”范围未定。Canova 从 Venice 崛起不推断出生或居住；同代人对复兴的希望不等于结果；新式公共服务赞助不专属于 Memmo。Farsetti 被未指名的诗歌和演说举例，作品端点开放。8条 S2 关系候选中7条端点齐备、1条开放；没有新建 KU 或正式关系。

S2 记录校正 L39 os→of、fife→life，L40 grëat→great，note 6 L56 pp. 32 if.→pp. 32 ff.；未改写 S0。note 1–2 已链接，notes 3–6 与下一段 Andrea Memmo 一并语义复审。全库严格表审计 errors=[]、s2_missing=[]；引文锚点 12,371 精确、46 空白归一化、0 未匹配。下一段：chp-15:15_CHP-15_sec_ii:l3-4。
