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

对照`CHP-15.pdf`物理页2复核正文段`chp-15:15_CHP-15_sec_i:l16-25`。73条mention字符跨度均吻合，44条statement引文均可在指定S0段定位；印本`milord, employing`与S0 OCR连写`milord,employing`的差异记入S2校读，不改来源。补录6条定位明确的statement，细分别墅位置、拟容纳的收藏、柱群来源与Rome地理限定；增加Farsetti居住巴黎、威尼斯新古典运动角色及别墅/柱群关系候选。首次审阅将Lodoli启发“三位赞助人”的目标集合保留开放；该决定在全书交接审计中按本章三位赞助人小节标题复核并修正，见下方复核记录。修正`cand-10430`跨页说明与`cand-9206`使用范围；未新增候选、KU、mention或正式关系。全库12,405条statement、2,644条关系候选（23条开放）；下一项p.363正文与注释。

## 第十五章p.363正文与注释语义复审（2026-10-09）

对照`CHP-15.pdf`物理页3复核正文`chp-15:15_CHP-15_sec_i:l27-36`及注释`chp-15:15_CHP-15_sec_i:l43-56`。纠正注1误连：标记跟随教皇转移财产句，不属于million-ducats支出说法。把整段别墅赞誉归于匿名当代引文；注2所引Boscovich致Vallisnieri信件不证明赞誉作者身份。修正Canova study 与Palazzo Farsetti、花园与别墅的关系方向；不把“Venetian painting and sculpture”连到Venice地名。新增Canova创作两只首批花篮、花篮被放在宫邸楼梯、Algarotti的古典范式理论归属、注2信件作者和收信人四条statement。对正文和注释记录9项印本校读；S0与原始引文保持不变。正文段现35条statement、69条mention、23条关系候选（3条开放）；无新增candidate、KU、mention或正式关系。全库12,409条statement、2,659条关系候选（2,633条端点完整、26条开放）；引文锚点12,363条精确、46条空白归一、0条未匹配。详见[过程记录](../process/stages.md)与[全书当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。下一项为p.364 `chp-15:15_CHP-15_sec_i:l38-41`。

## 第十五章p.362正文与脚注语义复审（2026-10-09）

对照`CHP-15.pdf`物理页2复核`chp-15:15_CHP-15_sec_i:l16-25`。73条既有mention的字符跨度逐条复算无误；44条statement引文均可在S0段落内定位。印本“milord, employing”被S0 OCR连写为“milord,employing”，只在对应statement的`ocr_corrections`记录，不改原文或引文。p.362注1–2的印刷页号与页图一致，且仍与L17正文标记双向链接；p.362末句与p.363 L28的续接、注1的跨页关系保持链接。

本段原复核形成44条statement、73条mention。补录6条精确锚点statement：Farsetti别墅位于S. Maria di Sala家族产业；别墅拟容纳索引中分别列出的石膏像模与绘画收藏；石膏像模收藏在家族宫邸组建；42根多立克柱的来源为Dea Concordia神庙；来源文字称该庙位于Rome。首次将“洛多利是本章三位赞助人的直接启发者”列为一条开放S2关系候选；全书交接审计对照第十五章小节标题后，将目标解析为Farsetti `cand-1002`、Memmo `cand-1642`和Querini `cand-2075`。原组级statement保留原文与注脚上下文、取消其关系候选标记；新增三条逐人标量关系候选，以`parent_body_statement_ids`回链组级断言。现本段47条statement、73条mention；端点解析依据为书内标题，未做S3身份对齐，也未写入S6正式关系。另把Farsetti居住巴黎、其在威尼斯新古典运动中的角色、别墅与柱群关系补入S2候选。`cand-10430`的跨页说明和`cand-9206`的使用范围已按本页证据修正；无新增候选、KU或mentions。

全书现有1,019 KU、11,530候选、27,463 mentions、12,644 statements；S2关系候选2,808条，其中2,777条两端齐备、31条开放。p.362三条新增关系statement引文均精确落在L17；全段73条mention跨度保持吻合。严格阶段审计`errors=[]`、`s2_missing=[]`。两条既存`enrichment source_ref`警告保持不变。全书交接审计仍在进行；S2尚未交接。

## 第十五章 p.364 Farsetti 段复审（2026-10-09）

按印刷页图复核 p.364 L39–41 及 p.363→364 跨页句。正文21条 statement、30条 mention；原复合主张拆分并新增8条 statement。指代“This”明确为 Tommaso 举报 Anton 的事件，新增开放事件候选 cand-11525；note 1 所引 Inquisitori di Stato 档案未独立查阅。Tommaso 的书籍／手稿收藏 cand-10465 类型未定；家族记述作者候选 cand-10443 的同一性留待 S3；Anton 为 Tommaso 侄子作为关系候选记录。

“the collections”未绑定铸像或绘画收藏候选，所售项目仍未逐项识别；“the property”范围未定。Canova 从 Venice 崛起不推断出生或居住；同代人对复兴的希望不等于结果；新式公共服务赞助不专属于 Memmo。Farsetti 被未指名的诗歌和演说举例，作品端点开放。8条 S2 关系候选中7条端点齐备、1条开放；没有新建 KU 或正式关系。

S2 记录校正 L39 os→of、fife→life，L40 grëat→great，note 6 L56 pp. 32 if.→pp. 32 ff.；未改写 S0。note 1–2 已链接，notes 3–6 与下一段 Andrea Memmo 一并语义复审。全库严格表审计 errors=[]、s2_missing=[]；引文锚点 12,371 精确、46 空白归一化、0 未匹配。下一段：chp-15:15_CHP-15_sec_ii:l3-4。

## 第十五章 p.364 Andrea Memmo 段复审（2026-10-09）

对照印刷页图复核`chp-15:15_CHP-15_sec_ii:l3-4`及注释段L43–56。补入标题mention，拆分出生年/家族出身、Lodoli影响/传播思想/受影响、政治改革热情/打破贵族隔绝等复合陈述。新增4条statement、1条mention；本段18条statement、25条mention，8条关系候选端点齐备。校正注号5及`thé`的印本读法；核对注3–6而不将引文表述为独立查阅。p.364末尾恋情句已由p.365 L7闭合并与注1相连。全库12,421条statement、2,667条S2关系候选（27条开放）；下一段为p.365 `chp-15:15_CHP-15_sec_ii:l6-12`。详见[过程记录](../process/stages.md)及[全书当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。

## 第十五章 p.365 Andrea Memmo 正文及注1–2（2026-10-09）

对照`CHP-15.pdf`物理页5复核p.365正文和注1–2。正文由23条statement增至36条、由46条mention增至52条；新增13条statement、6条mention，无新增候选或KU。把Doge机会、赞助评价、到任与集市、Prà计划的实施和筹款、Bologna/Vicenza例证、雕像数量及代表资格拆分为单项主张；纠正“改造Prà”和“召请Cerato”的行动主体，并记录Memmo—Lodoli师承候选。五条S2关系候选端点均齐备，未生成正式关系。10项印本校读保存于S2，不改S0；注2只保留书内引注范围，未独立查阅。全段36条statement引文、52条mention跨度均核对通过；完整同步闭合通过。详见[逐项过程与裁决](../process/stages.md)及[全书当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。下一段按书序为p.366 `chp-15:15_CHP-15_sec_ii:l14-28`。

## 第十五章 p.366 正文与注1（2026-10-09）

对照`CHP-15.pdf`物理页6复审L14–24及注1 L25–28，并核对p.365资格句续接与p.367 Elementi续句。27条既有statement细化为54条（新增27），86条mention增至88条（新增2），候选净增4个。细化价格和雕像规范，拆分雕像题材/拟制作者、Padua提供祖先雕像、19座完成/外交任职、项目困难及注1书信线索；“another six in Rome”保持原文歧义。把“his friends”和“the councillors”从错误的人物/城市机构映射改为匿名群体；另记录匿名访客和未题名的Radicchio说明文。拆分Subleyras绘制计划、Memmo展示计划、访客捐像、波兰/瑞典君主订阅及雕像已立/索取图画等关系主张；书信和说明文未独立查阅。

印本确认`Prato`→`Prà`（L20、注1 L28）、`Memiiio’s`→`Memmo’s`（L22）、`dining`→`during`（L24），只登记于S2；S0不改。54条quote均逐字落在声明来源行，88条mention跨度全部匹配。p.366现32条S2关系候选、标量端点32/32；没有新增KU、S3对齐或S6正式边。写后全书12,461条statement、27,433条mention、2,687条关系候选（2,660条端点齐备、27条开放）；严格阶段审计`errors=[]`、`s2_missing=[]`，同步闭合5/5检查通过。当前下一段为p.367 `chp-15:15_CHP-15_sec_ii:l30-36`；S2尚未交接。详见[逐项过程与恢复信息](../process/stages.md)及[全书当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。

## 第十五章 p.367 Andrea Memmo 与 Prà della Valle（2026-10-09）

对照`CHP-15.pdf`物理页7复核正文L30–36及对应注释L90–97，并核对p.366/p.368跨页语境。正文38条statement，连同注释共46条statement、63条mention。按印本校读`Prà`、`must certainly`、`notable variations`及注释III、Vallotti、Procuratia、Zatta等；S0和原始引文不改。

修正Prà地点、Padua索引候选与Memmo计划的区分；分开《Apologhi》文本与出版事件；将两尊雕像建模为作品候选`cand-11530`、`cand-11531`，并校正panegyric候选`cand-10505`类型为archive。纠正作品/人物候选错配，删除两处泛词误提及。关系候选共29条，4条端点开放：未指名的待安置雕像、Waldstein可能资助的作品、Skala与Veith可能成为雕像题材。Memmo致Casanova仅记录单封书信；可能性不写成已委托、已资助或已制作，不生成S6正式关系。未新增KU或S3对齐。

写后全库1,019 KU、11,510 candidates、27,432 mentions、12,478 statements、2,711条S2关系候选（31条端点开放）。严格阶段审计`errors=[]`、`s2_missing=[]`；引文锚点12,432精确、46空白归一、0未匹配。p.367之后下一处按书序为p.368 `chp-15:15_CHP-15_sec_ii:l38-47`；全书S2仍未交接。详见[逐项过程与恢复信息](../process/stages.md)及[全书当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。

## 第十五章 p.368 Andrea Memmo 与 Querini（2026-10-09）

复核物理页8正文后，statement由16条调整为31条，mention由29条增至31条；新增15条statement、2条mention和3个候选。修复his brothers误映射，区分Farsetti与Memmo各自的公共服务主张，并拆开Memmo的社交活动、友谊/赞助与收藏权属、Lodoli纪念、Querini政治经历及1761年危机参与等复合主张。新增14条关系候选；正文与关联注释共23条，端点23/23齐备，不生成S6正式边。

页图校读与OCR缺标只登记于S2：脚注6标记见于印本而S0 OCR缺失；Prà、confined、private/lives及State Inquisition读数按印本记录。State Inquisition句延续至p.369，继续保留跨页statement链接。全库现1,019 KU、11,513 candidates、27,434 mentions、12,493 statements、2,725条S2关系候选（2,694条端点齐备、31条开放）；12,447条引文精确匹配、46条空白归一、0条未匹配。严格表审计`errors=[]`、`s2_missing=[]`，同步闭合5/5项检查通过。下一处为p.369 `chp-15:15_CHP-15_sec_ii:l49-59`；全书S2尚未交接。详见[过程记录](../process/stages.md)及[全书当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。

## 第十五章 p.369 Querini 与 Alticchiero（2026-10-09）

对照物理页9复核正文39条statement、36条mention及注1–4。新增13条statement、2条mention和事件候选cand-11535；纠正保守派胜利与Querini拘押事件的端点，拆出改革评议、政治退出、Querini/Voltaire勋章、Festari同行、别墅位置和陈设评价等内容。18条S2关系候选端点齐备，不写入正式关系。

将脚注、引文、OCR校读取证边界保留在S2；作者传闻仍为传闻。修正p.369对p.370浴室版画statement的重复，并把不同OCR校读挂到各自语句。全库现1,019 KU、11,514 candidates、27,436 mentions、12,506 statements、2,732条S2关系候选（2,701条端点齐备、31条开放）；引文锚点12,460精确、46空白归一、0未匹配。严格表审计`errors=[]`、`s2_missing=[]`，同步闭合5/5项检查通过。下一处为p.370 `chp-15:15_CHP-15_sec_ii:l61-67`；全书S2尚未交接。详见[过程记录](../process/stages.md)及[全书当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。

## 第十五章 p.370 Querini、Alticchiero 与花园陈设语义复审（2026-10-09）

对照`CHP-15.pdf`物理页10复核正文`chp-15:15_CHP-15_sec_ii:l61-67`及注释段L109–110。正文statement由22条调整至52条，mention由45条调整至53条；净增30条statement、5个候选和8条mention。将浴室、图书室、Querini书房和藏书集合分开；拆出Piranesi/Picart版画作者、Bacon胸像所描绘人物、`Daphnis and Chloe`版画组的底本/绘制/雕版角色，以及友谊祭坛、Epicurus与Phocion胸像、碑铭、友谊和花园理想等陈述。`Young’s Wood`改为完整地名跨度，另提及“the poet”；`Night Thoughts`作为独立作品，Edward Young身份仍留S3对齐。Fortune改映射为祭坛理想，不再误连Salvator Rosa作品。注1链接版画组，注2链接Mme Rosenberg友谊陈述；印本注号及相关OCR差异只记录于S2，未改S0。

本页37条关系候选中36条端点齐备；瑞士友谊未具名成员保持1条开放候选，不写入正式关系。正文52条statement、53条mention跨度通过S0行锚/字符偏移核对；写后全库1,019 KU、11,519 candidates、27,444 mentions、12,536 statements、2,757条关系候选（2,725条端点齐备、32条开放），引文锚点12,490精确、46空白归一、0未匹配。严格阶段审计`errors=[]`、`s2_missing=[]`；全书S2仍未交接。下一处按书序为p.371 `chp-15:15_CHP-15_sec_ii:l69-83`。详见[过程记录](../process/stages.md)及[全书当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。

## 第十五章 p.371 Querini 与 De Non 语义复审（2026-10-09）

对照`CHP-15.pdf`物理页11复核正文`chp-15:15_CHP-15_sec_ii:l69-83`及p.371注1–2（合并注释L111–112）；注释L113属于p.372，留待下一页。正文由23条statement重组为49条，51条mention均与源文跨度匹配。将Mme Rosenberg对Querini灵魂的转述与所报告信念分开；拆出祭坛奉献对象、浮雕描绘的三种拟人化恶德、浮雕与Apelles构图及Pliny记录关系；分开别墅访客、纪念碑、收藏/作者、De Non居留/交往、版画对De Non与Novelli的影响、Voltaire肖像制作者/对象/地点及Renier胸像的委托/制作/对象。男性肖像坐者仍待决，p.371–372竞选句保留互链。

修复候选语义：删除把Haskell证据限制误作实体的`cand-10575`；把“allegory”提及映射到新术语`cand-11542`，删除泛称“sculpture”的伪实体提及；将“Rosenberg’s book”映射到已有archive候选`cand-2825`。新增Apollo候选`cand-11541`和提及，补录Alticchiero别墅及`allegorised`提及，并把“花园寓意直白”的判断主语更正为Mme Rosenberg。38条正文关系候选端点全部齐备，无S6写入。印本读数仅保存在S2，S0未改。

受控dry-run及写入后最终严格审计`errors=[]`、`s2_missing=[]`；p.371 statement引文和mention跨度均逐条通过。全库1,019 KU、11,520 candidates、27,446 mentions、12,562 statements、2,783条S2关系候选（2,751条端点齐备、32条开放）；引文锚点12,516精确、46空白归一、0未匹配。同步闭合运行通过，结构契约健康130/130，语义成熟度未评分。恢复副本和受控脚本见[过程记录](../process/stages.md)。下一处按书序为p.372正文`chp-15:15_CHP-15_sec_ii:l85-88`及注释L113；全书S2尚未交接。

## 第十五章 p.372 Querini 与 Maffei 语义复审（2026-10-09）

对照`CHP-15.pdf`物理页12复核正文及注1。正文从9条statement细化为13条；注释3条，17条mention全部保留且跨度通过核验。分别记录异教遗址对Querini的意义及Haskell对学者群体的对比、Maffei的收藏与记录活动、Querini的政治退隐与回归理想过去，以及Winckelmann比较中的“洞见较少”限定。Renier竞选目标及1779年、其后政治妥协与胸像事件、Rousseau影响、心脏按请求安葬、1951年注释中的陶制胸像推定和仆役盥洗处传闻均保留来源归属与不确定性。

6条S2关系候选端点均齐全；没有新增KU、候选、mention或正式关系。p.371的跨页statement正确链接本页Doge断言。严格表审计通过，16条引文无未匹配。全书S2仍未交接；下一处重新复核第十六章p.373正文及注释。

## 第十五章 p.370 瑞士友谊匿名群体端点复核（2026-10-09）

对照印刷p.370页图及规范段`chp-15:15_CHP-15_sec_ii:l61-67`，将“those formed in Switzerland”登记为园林祭坛所纪念的来源界定匿名群体。新增无类型、status=open候选`cand-11560`和mention `m-chp15-p370-alticchiero-0049`，精确跨度`[2218,2245)`；将statement `st-chp15-p370-querini-swiss-friendships-open`的object连接到群组。成员、人数和名册均未知，不据周边材料推断Voltaire、Festari、Giustiniani或Mme Rosenberg为成员；无KU或S6正式关系新增。严格阶段审计通过（`errors=[]`、`s2_missing=[]`）；全量同步闭合303 passed、2 subtests passed，9/9检查及结构契约130/130通过。全书S2交接仍在进行。详见[过程记录](../process/stages.md)及[全书当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。

## 第十五章p.367单数雕像候选关系端点复裁（2026-10-10）

对照印刷p.367及规范段`chp-15:15_CHP-15_sec_ii:l30-36`，将“one”解析为Memmo所问的一尊可能雕像，新增开放作品候选`cand-11561`及mention `m-chp15-p367-memmo-0066`（`[1175,1178)`，source line L34）。Waldstein可能资助、Skala可能为题材、Veith作为备选题材三条关系statement均连接至同一作品候选；没有把疑问写成承诺、委托或完工。复数“further statues”仍未枚举，原关系对象保持开放，并与单数问题互链。

写后全库11,539 candidates、27,472 mentions、12,644 statements；2,808条S2关系候选中2,789条端点齐备、19条开放。严格阶段审计`errors=[]`、`s2_missing=[]`；两条既存enrichment `source_ref`警告仍在。全量同步闭合通过（303 passed、2 subtests passed，9/9闭合检查、结构契约130/130）；全书S2尚未交接。详见[过程记录](../process/stages.md)。


## 第十五章p.367复数雕像群组端点复裁（2026-10-10）

复核同段further statues needed to be installed及紧接的Waldstein单数雕像疑问。将复数表述登记为来源限定的开放作品群组cand-11562，精确mention m-chp15-p367-memmo-0067跨度[1001,1016)；更新st-chp15-p367-further-statues-still-needed对象端点。候选成员和数量未知；不推断单数候选cand-11561属于该组。严格审计errors=[]、s2_missing=[]；全库11,540 candidates、27,473 mentions、12,644 statements，2,808条关系候选中18条端点开放。详见过程记录及全书当前结果。

## 第十五章p.363艺术实践term端点补充复裁（2026-10-10）

将`Venetian painting and sculpture`作为来源限定的艺术实践term `cand-11563`，精确mention为`m-chp15-p363-0088`（`[1355,1386)`）；保留句内“Venetian”至Venice地点候选`cand-3401`的地域修饰映射，并用完整短语表达艺术实践对象。p.363关系statement的object端点接至该term，仍归属Haskell的评价。严格审计`errors=[]`、`s2_missing=[]`，全库关系候选2,808条中2,791条端点齐备、17条开放；不新增KU或正式关系。

## 第十五章p.363未名赞语作者端点复裁（2026-10-10）

将引述中的“one of them”登记为未名同时代人候选`cand-11564`，mention `m-chp15-p363-0089`跨度`[465,476)`，并连接赞语statement主语。注2提到Boscovich书信，但未独立查阅书信及原文，不据此确认作者。全书S2关系候选2,808条中2,792条端点齐备、16条开放；严格审计`errors=[]`、`s2_missing=[]`。

## 第十五章p.364诗歌与演说群组端点复裁（2026-10-10）

将原文“a flood of poems and speeches”登记为未名文本群候选`cand-11565`，mention `m-chp15-p364-poems-speeches-group-0001`跨度`[1180,1209)`，并连接Farsetti作为范例的关系statement对象端点。文本、作者、日期及准确数量均未知，且暂不定work或archive类型。严格审计`errors=[]`、`s2_missing=[]`；全书S2关系候选2,808条中2,793条端点齐备、15条开放。

## 2026-10-14：p.361 statement原子化复核与mentions恢复

从历史提交恢复p.361的54条mention锚点，并核对候选引用、字符跨度和重叠。复核后p.361正文27条statement为10 true、17 false；脚注4条为2 true、2 false，合计31条无unset。将Tiepolo在西班牙及Pittoni衰退等复合/漏标内容拆为原子裁决；“these men”促成威尼斯绘画复兴仍因指代端点不明而保留开放，不据名单或共现补猜。p.361当前结果与恢复证据见[过程记录](../process/stages.md)；全书S2仍在第十四章p.355推进。


## 2026-10-15：p.362正文与注1–2脚注完成语义裁决

复核正文段`chp-15:15_CHP-15_sec_i:l16-25`及同页注1–2。正文48条statement全部分类（41 true、7 false）；注1的Farsetti家族史、Paravia 1829 pamphlet、Sforza 1911文章及注2的Memmo 1786著作共4条均规范为《赞助人与画家》`cand-2962`→对应archive候选的`cites`关系候选。被引著作和页面均未独立查阅；注释内容不扩写为被引文献中的事实。

恢复正文73条历史mention并按S0重核跨度；新增14个来源限定候选、9条正文mention及4条脚注书目mention。修正`he`误落在`they`内部、Michelangelo与Sansovino的人/作品错映、Venetian文化修饰与城市地名混淆，以及别墅构件被映射到整体别墅的问题。印本p.362与S0页码标注不一致时，以页图保留S2校读，不改S0。脚注citation mention和新增statement引句逐项核对，mention无重复或交叉跨度。

受控脚本`classify_ch15_p362_remaining_20261015.py`和`classify_ch15_p362_footnote_citations_20261015.py`均先dry-run、锁定写前SHA并校验端点/跨度，再apply；恢复副本后缀分别为`.bak-s2-ch15-p362-semantic-review-20261015`与`.bak-s2-ch15-p362-footnote-citations-20261015`。写后全库15,060条statement（10,116 true、4,556 false、388 unset）、12,199 candidates、21,577 mentions。严格阶段审计`errors=[]`、`s2_missing=[]`；两条既存enrichment来源警告及通用语义提示仍在。下一未裁决段为p.363 `chp-15:15_CHP-15_sec_i:l27-36`，12条待裁决；全书S2未交接。

## 2026-10-15：p.364 Farsetti正文剩余statement完成裁决

此前13条unset现分类为8条关系候选、5条非关系；本段21条statement总计16 true、5 false。新增候选`cand-12222`–`cand-12226`及6条mention，分开记录家族传统、贵族艺术支持角色、未枚举的收藏群、威尼斯学者群和新赞助人群。关联使用已有贵族群`cand-10473`与收藏出售事件`cand-1012`；未将集合指定为铸像或绘画收藏，也未把Memmo当作新赞助人观念的唯一持有者。作者评价、叙述语气、类型学判断及范围不明的财产处置保留为原书claim，但不列图谱关系。

受控脚本`process/classify_ch15_p364_remaining_20261015.py`经dry-run、写前SHA和mention字符跨度核验后apply。写后全库15,060条statement（10,128 true、4,569 false、363 unset）、12,204 candidates、22,194 mentions；严格表审计`errors=[]`、`s2_missing=[]`。当前下一段为p.364合并注释`chp-15:15_CHP-15_sec_i:l43-56`，12条statement待裁决；外部书目未独立查阅，全书S2未交接。

## 2026-10-15：p.364合并注释引文与章内指引完成裁决

将p.363–364注释中11条已识别档案/书目引文统一规范为主书→archive候选的`cites`，并把p.363注1的De Tipaldo与Mazzotti拆成独立statement。Chapter 12与Chapter 11的内部交叉指引为非关系断言。所有被引来源未独立查阅；页码、注号及OCR更正保留S2证据，不改S0。写后本段17条statement（15 true、2 false）；全库15,061条statement（10,139 true、4,571 false、351 unset）、12,204 candidates、22,194 mentions。严格审计`errors=[]`、`s2_missing=[]`。下一段按源序为Andrea Memmo正文`chp-15:15_CHP-15_sec_ii:l3-4`（10条待裁决），全书S2仍未交接。

## 2026-10-15：p.364 Andrea Memmo开篇剩余statement完成裁决

将10条unset裁为5条关系候选、5条非关系，段内18条现为13 true、5 false。建筑理念、贵族成员关系、法国文化取向、政治改革兴趣及试图打破贵族隔绝保留为来源限定候选；“exceptional”不转作客观评价，cand-1648的索引子目身份留待S3。将内部回指、作者比较、出生年、未列举娱乐活动及未名恋情系列保留为claim，不增造关系边。p.364–365跨页句保持完整，脚注1–6回链和印本校读均保留。

写后全库15,061条statement（10,144 true、4,576 false、341 unset）、12,204 candidates、22,194 mentions；严格表审计`errors=[]`、`s2_missing=[]`。下一段按书序为p.365正文`chp-15:15_CHP-15_sec_ii:l6-12`（31条待裁决），全书S2未交接。

## 2026-10-15：p.367–370正文剩余statement完成裁决

p.367–369的残余项已按源序裁决：p.367段38条（30 true、8 false），p.368段31条（23/8），p.369段39条（24/15）。p.367新增cand-12235–cand-12236及3条mention；p.368新增cand-12237–cand-12239及3条mention；p.369新增cand-12240及2条mention。端点保留匿名群体和事件边界；“reforms”“downfall”等词不跨段合并为同一政治事件。

p.370对照物理页10复审，原15条未分类项全部裁决；Epicurus的法语称谓与其被“vulgar minds”误解、Phocion的法语称谓与其对抗“ignorant mob”分别拆开，段内由52条增至54条（48 true、6 false）。新增cand-12241–cand-12243及3条精确mention，表示Haskell所述的“the populace”及Wynne所思、所忆的两个观念。所述群体和文化判断仍带来源限定；未把Querini的“downfall”认定为拘押，也未将宽泛群众修辞扩成可识别成员名单。

受控脚本`process/classify_ch15_p370_remaining_20261015.py`经写前SHA、固定unset集合和来源短语跨度校验，dry-run后apply；恢复副本后缀`.bak-s2-ch15-p370-classification-20261015`。写后全库15,066条statement（10,212 true、4,637 false、217 unset）、12,221 candidates、22,208 mentions；严格审计`errors=[]`、`s2_missing=[]`。当前下一段为p.371 `chp-15:15_CHP-15_sec_ii:l69-83`（11条待裁决）；S2仍未交接。

## 2026-10-15：p.371正文剩余statement完成裁决

对照印刷p.371页图复核正文段；11条残余项裁为5条关系候选、6条非关系，段内49条现为43 true、6 false。保留Mme Rosenberg对Querini信念的转述、她对寓意的反应、Querini对古代艺术的审美理解及信念；Haskell的证据限制、De Non职业评价、适格性判断、别墅吸引注意力及由原子关系覆盖的综合句不转为独立关系。

新增候选`cand-12244`–`cand-12246`及3条精确mention。修正浮雕依据与Pliny记录作品的端点，统一指向未定名的阿佩莱斯作品候选；未从文献传统推定作品题名。恢复副本后缀为`.bak-s2-ch15-p371-classification-20261015`。写后全库15,066条statement（10,217 true、4,643 false、206 unset）、12,224 candidates、22,211 mentions；严格阶段审计`errors=[]`、`s2_missing=[]`。当前下一段为p.372正文`chp-15:15_CHP-15_sec_ii:l85-88`（9条待裁决）；S2仍未交接。

## 2026-10-15：p.372正文剩余statement完成裁决

p.372正文9条残余项裁为7条关系候选、2条非关系，段内13条现为11 true、2 false。新增cand-12247–cand-12250及4条精确mention：Renier妥协所指的匿名政治力量、Querini对异教圣所的观念、Maffei的古代雕塑收藏类别、以及其时代的大多数学者/古物学者群。保留“most”限定；Maffei所记录的历史证据没有被猜成具体作品或文献。`ideal world of the past`留作Haskell解释，不新造地点或时代实体。

受控脚本`process/classify_ch15_p372_remaining_20261015.py`经写前SHA、固定statement集合和S0跨度校验后dry-run/apply；恢复副本后缀`.bak-s2-ch15-p372-classification-20261015`。写后全库15,066条statement（10,224 true、4,645 false、197 unset）、12,228 candidates、22,215 mentions；严格审计`errors=[]`、`s2_missing=[]`。当前下一段为第十五章合并注释`chp-15:15_CHP-15_sec_ii:l90-113`（26条待裁决）；全书S2仍未交接。

## 2026-10-15：第十五章p.365–372合并注释完成裁决

合并注释段`chp-15:15_CHP-15_sec_ii:l90-113`现有63条statement，62条关系候选、1条非关系；按p.365、367–372各脚注归属逐项审理。新增`cand-12251`（Memmo所藏、艺术家多未注明的版画组）、`cand-12252`（未命名的Brenta防洪计划）及3条精确mention。区分Mengs绘画与版画收藏；将Querini所受指控的对象映射为计划而非河流；拆分档案编目、保管机构、编者、出版引文和未经独立核验的传闻。p.371注2的De Tipaldo映射已校正；外部引文未被宣称独立查阅。恢复副本后缀为`.bak-s2-ch15-notes-classification-20261015`。全库现15,094条statement（10,277 true、4,646 false、171 unset）、12,230 candidates、22,218 mentions；严格阶段审计`errors=[]`、`s2_missing=[]`。当前下一段为第十六章导言`chp-16:16_CHP-16_intro:l3-14`（19条待裁决）；全书S2尚未交接。
