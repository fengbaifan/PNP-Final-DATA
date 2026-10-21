# 第七章脚注段 S2 独立语义复核

更新：2026-10-22。各局部复核范围与状态见下文；第七章整体仍未接收。

## 范围与方法

独立复核登记段 `chp-7:07_CHP-7_sec_iv:l97-119`，逐条核对当前 `book-statements.jsonl` 的31条 statement（印刷页193–199，PDF物理页31–37），并核对56条 mention span 与 S0 文本。其中30条 `relation_candidate=true`、1条 `false`、0条未分类。校读依据为对应 PDF 印本页。脚注所引作品、手稿及馆藏目录未因此视为独立查阅。

## 发现、修订与裁决去向

| Statement | 发现与当前去向 |
|---|---|
| `st-chp7-p195-n1-prince-taste-comment` | 当前记录已是 Haskell 的 `authorial_interpretation`，对象端点为空且 `relation_candidate=false`；保留“even in sacred pictures”限定，不连到 Wilhelm 或未识别作品。本次无改动。 |
| `st-chp7-p195-n1-wilhelm-citation` | 注1的 “ibid., pp. 89 and 92” 回指注4中的 Wilhelm 引文；当前书→文献引用、定位和同篇文章候选相符。此条在前次30条清单中漏列，现计入31条总数。 |
| `st-chp7-p194-n3-cite-von-freeden` | 原始 OCR 引文保留；已补印本校读 `8 Hantsch und Schers`→`3 Hantsch und Scherf`，并与同注的 Hantsch–Scherf 记录使用相同校读依据（PDF物理页32）。独立复核指出 claim 重复了完整书名；已精简为一次书名，并保留其与 Hantsch–Scherf 同注并列的语境。 |
| `st-chp7-p195-n3-da-canal` | 印本注3为 “especially pp. 71–3”；claim 已改为 pp.71–73。候选 `cand-6593` 在其他章节出现 p.69 的定位仍独立保留，不把其页码带入本注。 |
| `st-chp7-p196-n1-gennari-evidence` | 在保留手稿 `cand-7262` 为被引档案端点的同时，为 Whinney and Millar `cand-7066` p.182 与 Zanotti `cand-7115` vol.I pp.170–171 保留两条书目 `citations`；手稿定位 `MS B.344` 移至独立的顶层 `shelfmark`，馆藏机构 `cand-7263` 保留在顶层 `repository_candidate_id`。引文数组不再混入档案定位；独立审阅者已复核通过，所引材料仍未独立查阅。 |
| `st-chp7-p197-n4-isham-pictures-lamport`、`st-chp7-p197-n5-exeter-pictures-burghley` | S2 保留画作组位置陈述；S6 均裁为 `rejected`（仅否决图谱边）。当前人物→地点端点无法表达未识别的画作组，且不等于人物居住、拥有或当前馆藏。逐项理由见[关系裁决记录](knowledge.md#s6-chp7-collective-picture-location-notes-20261021)。 |

其余条目未发现需要改变事实方向、书目对象或来源限定的实质问题；56条 mention span 均与本登记段 S0 文本对应。原始 OCR 保留，必要读法以 `ocr_corrections` 记录。

## 接收与覆盖统计

改动项已由独立审阅者复核，Gennari 的两条书目 citation 与顶层 shelfmark／repository 分离清楚；S6 两条裁决和端点边界均通过。本段接收仅限 `chp-7:07_CHP-7_sec_iv:l97-119`，章节其他范围尚未完成，故第七章仍不接收。当前结果快照记录第七章1,009/1,239条；本记录先不增加汇总分子，待按 statement ID 去重后再归并至全书9,400/15,167统计。

该批之后的下一游标为 `chp-7:07_CHP-7_sec_v:l3-7`；页码标记段 `l1-1` 无 statement。后续接续记录见下节。

## 第七章 p.199 第V节当前ID独立语义复核

逐条核读登记段 `chp-7:07_CHP-7_sec_v:l3-7` 的14条 statement（印刷p.199、PDF物理页37），并对照S0及46条 mention span。12条 `relation_candidate=true`、2条 `false`、0条未分类；46条span均精确对应登记源段。p.199的“Roman art”原被误映到Rome地点候选 `cand-4490`；按同一“Roman art”艺术生产领域的跨章语义，改映到既有term候选 `cand-4631`（其来源已含第2章和第7章p.173），并把相应 statement 主语同步改为该term。两个明确的城市提及仍映到 `cand-4490`；Maratta、Trevisani两条mention中的旧待S3备注同步为当前 `same` 决定。S3既有 `new` 身份组决定不变，不新增候选或身份组。

本段14条按 statement ID 去重后计入全书独立复核：第七章1,023/1,239，全书9,414/15,167（62.1%）。接收范围仅限本登记段，第七章及全书仍未接收。下一游标为p.200 `chp-7:07_CHP-7_sec_v:l9-18`。

## 第七章 p.200 正文 S2 独立语义复核

审读登记段 `chp-7:07_CHP-7_sec_v:l9-18` 的原有28条 statement，并对照印刷p.200、PDF物理页38的原书页图；原有70条 mention span 均与登记源段文本精确对应。修订后该段共32条 statement、71条 mention；新增的 `m-chp7-p200-v-daun-portrait` 精确锚定 `his portrait`（字符偏移2625–2637），指向仍未识别的作品候选 `cand-7302`。本段有限接收不表示第七章整体接收。

| Statement／对象 | 发现与处理 |
|---|---|
| `st-chp7-p200-v-treaties-confirm-changes-and-patronage-counterpart` | “These changes”不是《乌得勒支和约》的指代。主体改为空，保留和约为确认政治变化的语境；以 `related_statement_ids` 指向前文萨伏依及奥地利征服两条 statement。政治变化仍无单一候选端点，不强造实体。 |
| `st-chp7-p200-v-contemporary-painting-interest-at-versailles` | 主体改为空；“This”回指前句德斯特雷介绍保罗·德·马泰斯一事。保留意大利绘画、年轻艺术爱好者和凡尔赛宫“官方”风格为该断言的宾语／语境，不把受众误作激发兴趣的主语。 |
| `st-chp7-p200-v-noailles-secures-de-ferrari-at-marseilles`；`st-chp7-p200-v-destrees-introduces-paolo-to-nobles-bankers`；`st-chp7-p200-v-destrees-visits-naples-with-philip-v` | 分别把端点改为被说服的画家 Gregorio de Ferrari、被引见的 Paolo de Matteis、以及同行者 Philip V。马赛、那不勒斯仍作地点语境，未具名贵族与银行家仍保留为引见对象群体；不推定后续委托。 |
| `st-chp7-p200-v-daun-first-viceroy-and-patronage` | 拆分为 Daun 于1707年成为未具名新政权首任总督，以及他在意大利艺术赞助上可与未具名西班牙前任相比两项断言。第一项保留在原ID，第二项新增独立 statement；原注6的四条引注和 portrait statement 均与新拆出的比较断言保持双向关联。 |
| `st-chp7-p200-v-paolo-works-for-binchs-and-daun` | 拆分为 Paolo de Matteis 在那不勒斯陷落后先后为 Admiral “Binchs”与 Count Daun 工作。原ID保留 Binchs 断言，新增 Daun 断言；两者均不推定为正式委托。 |
| `st-chp7-p200-v-painters-make-canvases-for-daun-palace` | 按原文“all produced”拆为 Solimena、Giacomo del Po、Paolo de Matteis 三条个人断言；作品仍是未识别的画布组，无标题或单件归属。另更正候选 `cand-7301` 的旧mention备注：Haskell注5已将来源拼写“Binchs”识别为 Admiral Byng，现行 S3 组决定已完成。 |
| `st-chp7-p200-v-victor-amadeus-breaks-from-louis-xiv` | 增补印本校读：S0 OCR “tortuous' manoeuvres”对照物理页38读作“tortuous manoeuvres”；原始引用保留，OCR不回写来源。 |

新增四条关系候选（Daun比较赞助、Paolo为Daun工作、del Po制作画布、Paolo制作画布）已逐条记入 [S6 pending裁决](knowledge.md#s6-chp7-p200-atomic-relations-20261021)。Daun、未具名前任和画布组等端点仍未映射到可用KU，故没有写入正式关系表。纠正端点不改变S3决定；`cand-7296`作为既有 `new` 组成员因本段新增端点而进入S4直接关系端点队列。

本段32条按 statement ID 去重后计入统一复核：第七章1,055/1,243，全书9,446/15,171（62.3%）。修订后全书有10,406条 `relation_candidate=true`；其中335条至少缺一个候选端点ID（仅缺subject 45、仅缺object 218、两端均缺72）。第七章与全书尚未接收。下一游标为第七章p.200 `chp-7:07_CHP-7_sec_v:l39-40`（Plate 32a，3条statement）。

## 第七章 p.200 Plate 32a–32b 图版簇 S2 语义复核

对照 `CHP-7.pdf` 物理页42（印刷p.200）复核两条独立登记来源：`chp-7:07_CHP-7_sec_v:l39-40` 的Plate 32a，以及视觉转录段 `chp-7:07_CHP-7_sec_v_visual-transcription:l3-3` 的Plate 32b。页图显示32a为 Ribera 的 *Drunken Silenus*，caption称其“painted for Gaspar Roomer”；32b为 Paolo de Matteis 的 *The Choice of Hercules*，caption称其“painted for Lord Shaftesbury”。两段共6条statement、8条mention，8个mention span均与各自S0登记文本精确对应。

S3现行决定将32a作品、Ribera和Roomer分别复用至 `units/works/ribera-the-drunken-silenus`、`units/persons/ribera` 和 `units/persons/gaspar-roomer`；32b的图版作品候选 `cand-4071` 与p.198正文候选 `cand-7245` 均映射至 `units/works/paolo-de-matteis-the-choice-of-hercules`，Paolo de Matteis与Shaftesbury也各自复用既有人物KU。故更正32b qualifier中过时的“later alignment／no identity merge”表述及Roomer旧 mention note；不改变S3决定或身份组。Silenus `cand-4161` 与Hercules `cand-4162` 仍为类型／身份待决，未强制分类。

两条作者归属候选已存在匹配的formal `created_by` 关系（`rel-0948`、`rel-0866`），本批不复制关系行；图版caption作为来源证据是否并入现有边，随S6核对证据范围。两条“painted for”候选不升级为委托或所有权，且受控谓词是否足以准确表达该措辞仍待S6裁决；两个神话人物subject候选因端点类型／KU未决也待S6处理。本批不新增或删除statement、mention或relation记录，S4登记不变；S2逐条复核计数增加6条至第七章1,061/1,243、全书9,452/15,171（62.3%）。本段复核不表示第七章或全书接收。下一游标为p.201 `chp-7:07_CHP-7_sec_v:l42-55`，随后p.202 `l57-60`及p.200脚注 `l62-76`。


## 第七章 p.201 正文 S2 独立语义复核

对照 `CHP-7.pdf` 物理页43（印刷p.201）复核 `chp-7:07_CHP-7_sec_v:l42-55`。原段37条statement经复核后为38条，97条mention；36条为关系候选、2条为非关系判断。mention跨度由表审计对照登记文本核对。现存OCR文本未回写；已记录的印本校读继续保存在各statement的 `ocr_corrections`。

| Statement／对象 | 发现与处理 |
|---|---|
| `st-chp7-p201-v-italian-commanders-furnish-palaces` | 作为p.200高意大利裔军官句的续句，补充 `continuation_of_statement_id` 与反向关联。对本段“their”两处指代（`[11,16)`、`[53,58)`）新增mention，均指回 `cand-7303` 指代的同一军官群；不扩大为具名个人。 |
| `st-chp7-p201-v-eugene-no-interest-in-venetian-manner` | claim仅保留Eugene“似乎”不关注较轻盈的Venetian风格；将同句中许多Venetian画家赴Vienna为其他赞助人工作的内容与既有statement互链，避免重复复述。风格term不与画家群等同。 |
| `st-chp7-p201-v-pozzo-garden-palace-ceiling-1704`、`st-chp7-p201-v-pozzo-summoned-by-emperor` | 将“Pozzo受皇帝召见”与“1704年开始绘制Liechtenstein园邸大厅天顶”拆成两条原子statement。前者主语为Andrea Pozzo `cand-2033`，对象为未具名皇帝 `cand-4531`；后者对象为S3 `new` 的未识别作品候选 `cand-7320`，不声称完成或正式委托。两者共享原书局部引文并互链。 |
| 其他第七章p.201 statements | 核对Eugene的意大利／奥地利忠诚比较、赞助判断、收藏散佚、绘画与雕塑群、Martinelli建筑及Vienna文化语境；保留作者评价、群体范围和“开始/意图”状态，不将集合叙述扩成未证实的个人作品或完成委托。既有 `Bologna¹`、`fine arts`、`Galli-Bibiena` 等校读不改写S0。 |

Pozzo ceiling与summons两条关系候选分别裁为S6 `pending`：作品候选尚未登记为KU；皇帝候选仍是S3 `undecided`，且来源不明示召见的时间和目的。没有新formal边，S4直接端点队列计数不变（`cand-7320`此前已在队列）。全书关系候选数增至10,407，缺S2候选端点仍335；S6累计裁决213/10,407（143 formal、61 pending、9 rejected），尚余10,194。S3决定记录与S5字段数不变。

本段38条按statement ID去重后计入统一复核：第七章1,099/1,244、全书9,490/15,172（62.5%）。第七章及全书仍未接收。下一段为p.202 `chp-7:07_CHP-7_sec_v:l57-60`，随后核对p.200脚注 `l62-76`。

## 第七章 p.202 正文 S2 逐条语义复核

对照 S0 登记段 `chp-7:07_CHP-7_sec_v:l57-60` 与 `CHP-7.pdf` 印刷p.202、物理页44，复核现有13条statement和15条mention。段落偏移从源文件L57的`[Page 202]`页眉起算；15个mention跨度均与S0逐字符相符，statement原文范围与页图对应。S0文本保留不改写；已有校读`“scries”→“series”`、`“makejhejourney”→“make the journey”`由印本确认。

语义检查保留以下边界：Baroque的“last conquest”是Haskell的历史解释；Savoy战后转变与胜利伴随艺术繁荣分别记录，未补造具体胜利；Turin建筑的历史地位、绘画赞助的评价、地方人才稀少及外地画家招募失败分别保留；公爵的狩猎／军事兴趣和“似乎听天由命”分开，并保留`seemed`限定；Victor Amadeus与Juvarra作为复数行动主体保留，`“artistic dictator”`仅作Haskell措辞，不推定正式官职；“leading painters, or at least their pictures”保持原文二择范围，未命名来源城市、画家和作品不拆成具名对象；较小省镇保持未识别群体和叙述前指。

| statement_id | 复核结果 |
|---|---|
| `st-chp7-p202-v-baroque-conquest-transition` | 保留为带作者归属的解释性断言。 |
| `st-chp7-p202-v-savoy-transformed-after-war`、`st-chp7-p202-v-savoy-victory-flowering-arts` | 两个相邻断言分开；脚注1反向链接仍指向 Claretta 引注候选。 |
| `st-chp7-p202-v-savoy-dukes-preferred-hunting-and-military`、`st-chp7-p202-v-dukes-resigned-to-patronage-situation` | 保留未具名群体、比较语气和“seemed”。 |
| `st-chp7-p202-v-turin-architecture-and-painting-patronage`、`st-chp7-p202-v-turin-painting-patronage-futility`、`st-chp7-p202-v-turin-local-artists-rare`、`st-chp7-p202-v-turin-recruitment-failures` | 分别表达建筑、绘画赞助评价、地方人才与招募结果；不把评价写成量化事实。 |
| `st-chp7-p202-v-victor-amadeus-and-juvarra-change-turin`、`st-chp7-p202-v-turin-attracted-painters-or-pictures`、`st-chp7-p202-v-victor-juvarra-follow-other-centres` | Juvarra协同行动、吸引画家／作品的二择和比较先例均保留在限定范围。 |
| `st-chp7-p202-v-smaller-towns-anticipated-turin` | 不为未具名省镇补造城市身份；前指仅表示后文将转入讨论。 |

本段未新增或修订S2 statement／mention。发现`cand-2663`将城市Turin误列为`term`，已在对应S3记录中修正为`place`并复用既有 `units/places/turin`；Savoy作为政治实体归`institution`符合本项目类型表。该S3更正不改变原书断言，也未提前写入S6关系。本段13条计入逐条复核后，第七章为1,112/1,252、全书为9,503/15,182（62.6%）；第七章与全书仍未接收。下一游标为复合脚注段 `chp-7:07_CHP-7_sec_v:l62-76`，其中含p.202注1；该脚注内容将在该段统一复核，不在此重复计数。
