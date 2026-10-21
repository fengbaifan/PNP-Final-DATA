# 第5章语义处理结果

任务：patrons-and-painters-full-book-s2。第5章共41个规范段。按当前覆盖账本，35段reviewed、6段excluded，queued/partial均为0；41段migration_status均为complete。按源序，第5章p.143–145正文及合并注释L39–54已完成语义分类，章内relation_candidate unset为0；全书当前下一未分类项为第6章p.146章首`chp-6:06_CHP-6_intro:l3-5`。coverage与migration登记不等于全书语义交接。当前全书状态见`04-knowledge/results/patrons-and-painters-full-book-s2.md`，逐项裁决见同任务`process/stages.md`。

## 早期逐段处理记录（保留当时状态）

下表和随后进度叙述保留早期处理记录，不是当前覆盖清单；其中旧的partial、queued和“下一段”记录均为历史状态。此前p.135、p.136待分类的statement已在后续复核中处理；当前第5章正文和脚注statement均无relation_candidate unset。

| 规范段 | 状态 | 结果 |
|---|---|---|
| `chp-5:05_CHP-5_intro:l1-1` | excluded | Markdown文件名标题标记，不属于原书内容。 |
| `chp-5:05_CHP-5_intro:l3-5` | excluded | 印刷页码、章号及章节标题，仅作导航元数据。 |
| `chp-5:05_CHP-5_intro:l7-9` | reviewed / complete | 印刷页120脚注1–3已迁移：记录St Erasmus祭坛画、Poussin与St Peter’s、modello/Ottawa及两条书目定位。脚注1在同页还有Annunciation判断，转录于sec_i L7，随该段处理回链。 |
| `chp-5:05_CHP-5_sec_i:l1-1` | excluded | Markdown分节文件标题，不属于原书内容；正文从L3开始。 |
| `chp-5:05_CHP-5_sec_i:l3-7` | reviewed / complete | 印刷页120正文、脚注1续文及OCR校读迁移；L6末句由下一段闭合。Annunciation来源仍按原文保留为传统说法且证据不确。 |
| `chp-5:05_CHP-5_sec_i:l9-15` | reviewed / complete | 印刷页121正文及页底注4迁移；L9为页码导航。注1–3、5–7完整书目注释在本文件后段，后续处理并回链。 |
| `chp-5:05_CHP-5_sec_i:l17-26` | reviewed / complete | 印刷页122正文迁移；L26句子在p.123 L29闭合。保留Peri—Gaulli、Carlone债务、de Wael经营、Urban VIII/Innocent X经济语境、Rossi—Preti用工、作品出口、Ottini—Brandi委托及de Stael 1663引语；脚注1–6记入对应断言，注释正文待后段迁移。 |
| `chp-5:05_CHP-5_sec_i:l28-33` | reviewed / complete | 印刷页123 L29–33迁移；L33 “As a doctor he was said to be”由页124 L36闭合。扫描核实原文“I agreed”，OCR稿误为“T agreed”，未改来源。脚注1–4的注释正文待后部注释段处理并回链。 |
| `chp-5:05_CHP-5_sec_i:l35-49` | reviewed / complete | 首次迁移登记7个正文候选、41条提及和18条断言/引证；后续S2语义复核重做21条既有statement分类并新增29条原子断言、6个开放群体候选和8条精确提及。p.124印刷页只有注1：起始于后置注释L142，续文在本段L43–49；原“注2–6”全部归回注1。人物Luigi Scaramuccia改接`cand-2390`，印刷品使用`cand-6018`，索引作品候选`cand-2391`保持独立待S3对齐。L42由页125 L52闭合；PDF物理页5核实Niccolò、Annibale及1960等OCR差异，只记校勘不改S0。 |
| `chp-5:05_CHP-5_sec_i:l51-58` | reviewed / complete | 印刷页125迁移，新增7个候选、24条提及和18条断言/引证。L53分节符“– II –”在OCR中并入正文，且“we generally”误合成“wegenerally”；PDF物理页6已核实，来源不改。L57末句由页126 L61闭合；页125脚注1的L58续文与后置注释L143回链。 |
| `chp-5:05_CHP-5_sec_i:l60-74` | reviewed / complete | 印刷页126迁入8个来源型候选、33条精确提及和19条原书断言/引证。页125 L57比较句由本段L61闭合。记录Pantheon展览、Congregazione制度与目的、Velasquez/Pareja、Rosa引语和Jan Miel遗嘱；引述、作者判断与限定分层，匿名作品不造候选。跨行机构名及Velasquez叙述按源段换行定位。PDF物理页7核实“a confraternity”、1764、Jan Miel和1650；L74遗嘱引文由页127 L77续接并闭合，OCR源文不改。 |
| chp-5:05_CHP-5_sec_i:l76-83 | reviewed / complete | 印刷页127迁入12个来源型候选、47条精确跨度提及和31条原书断言/引证。续接并闭合页126 L74的Jan Miel遗嘱引文；本段涉及Pantheon展览、S. Giovanni Decollato年度展览及赞助、Gentileschi与Baglione绘画竞争、Sacchetti/Rospigliosi组织展览、Compagnia della Misericordia、Queen Christina借展和Rosa宣传。保留嵌套引述、Haskell评语和限定；匿名人物与作品不臆造身份。PDF物理页8核实L79印本“Decollato”、OCR“Decollate”，不改S0；页127 L83引语由页128 L86–87闭合。 |
| `chp-5:05_CHP-5_sec_i:l85-97` | reviewed / complete | 印刷页128迁入12个候选、53条精确提及和26条原书断言/引证。页127 L83引语由L86–87闭合；记录Medici展览、1736年展览与图录、S. Salvatore in Lauro组织及Pio/Ruspoli展陈，L97 Ruspoli句由页129 L100闭合。PDF物理页9核对年份、数量与场所；L88与L96的模糊标记在印本页底没有对应注释，保留为未链接OCR/版面标记，不强配脚注。 |
| chp-5:05_CHP-5_sec_i:l99-106 | reviewed / complete | 印刷页129新增15条精确跨度提及和20条原书断言/引证，无新增候选。L100续接并闭合页128的Ruspoli句：只展其194幅画的要求经Ghezzi建议后允许Olivieri另挂23幅。记录旧大师的突出与重复展出、现代绘画可及性、Ottoboni/Trevisani与Grimani/Molinari例、1704年宣传借展请求、四次年度展览与偶发展览、展览的装饰及公共性、艺术家可见性和外来文化语境；保留匿名Pope/王后、转述语气、Haskell评估和泛指范围，不将“these exhibitions”误连到单个展览候选。PDF物理页10核实印本“fit”（OCR作“sit”）及“primary aim”（OCR作“primary.aim”），校勘记入限定，不改S0；L106末句由页130 L109闭合。 |
| `chp-5:05_CHP-5_sec_i:l108-113` | reviewed / complete | 印刷页130新增4个候选、23条精确提及和19条原书断言/引证。L109续接并闭合页129 L106句；记录鉴赏观与鉴赏者形成、题材变化、Caravaggio转述、Mancini购画/陈设建议、匿名公众及Sassoferrato归属假说。PDF物理页11核实“the price”及“copied”前无双引号，不改S0。脚注1–2现已分别与后置注释L144–145回链；L113的“A prolific painter”由页131 L116–123闭合。 |

| `chp-5:05_CHP-5_sec_i:l115-123` | reviewed / complete | 印刷页131正文新增10个候选、62条提及和26条原书断言/引证；闭合页130 L113的“A prolific painter”句。区分1636年未成交与1643年替代作品，保留作者推测、传闻和评价。PDF物理页12核实tire/the、Pamftli/Pamfili、163 6/1636、GigE/Gigli、diEgently/diligently，均记校勘而不改S0。脚注1–4随后在注释段L146–147迁移并回链。 |
| `chp-5:05_CHP-5_sec_i:l125-147` | reviewed / complete | 页121–125及130–131的后置注释L126–147全部迁移；新增19个来源型候选、56条精确跨度提及和35条断言/引证。页124注1/L142与页125注1/L143、页130注1–2/L144–145、页131注1–4/L146–147均已回链；页124此前partial已关闭。PDF物理页2–6、12核实che/alla、sold、Annibale、1960及Galleria Nazionale等OCR差异。页128的两个模糊标记在印本无对应注释，仍不强配。 |
| `chp-5:05_CHP-5_sec_iii:l1-1` | excluded | 自动生成的Markdown分节标题，不属于印本正文。 |
| `chp-5:05_CHP-5_sec_iii:l3-3` | reviewed / complete | 印刷页131页底的新节总论句，新增3个术语候选、3条提及和1条断言。保留Haskell关于self-made man、统治精英价值与既有艺术规范的概括；PDF物理页12核实established，S0 OCR不改。 |
| `chp-5:05_CHP-5_sec_iii:l5-10` | reviewed / complete | 印刷页132 L6–10语义完成，新增3个候选、16条提及和15条断言；涵盖自制人士与非精英赞助、bambocciate支持的社会来源、Bamboccianti题材、Passeri转述、Erminia和John the Baptist的日常化场景及Rome/campagna表象。Erminia保留待S3定型。页132 L10末句由页133 L13闭合；该段脚注1–2仍待注释L127–128迁移。PDF物理页13确认L7行首孤点为扫描污点。 |
| `chp-5:05_CHP-5_sec_iii:l12-18` | reviewed / complete (2026-10-12 semantic re-review) | p.133的17条既有statement全部分类，并新增12条原子statement；全段29条（16条S2关系候选、13条非关系陈述）。新增5个来源限定候选、7条精确mention；拆分使馆群体张力、反复骚乱与教皇武装警察镇压困难，区分结社军队保护枢机/王公、参加骚乱与常规警察冲突，并单列临时治理、纪念像、潜在破坏威胁、贫民阶层和Arcadian评论。注1/L129既有Gigli引文候选复核后回链到三条使馆骚乱断言。页图确认L16印本为“we find”，S0 OCR“wesind”保持不改；Doni引语由p.134 L21闭合。未写S6正式关系。
| `chp-5:05_CHP-5_sec_iii:l20-26` | reviewed / complete (2026-10-12 semantic re-review) | 印刷页134原有14条statement全部分类，并新增13条原子statement，正文共27条（16条S2关系候选、11条非关系陈述）；脚注L130新增Doni引文候选statement。区分Van Laer与其未名追随者、Caravaggio早期/晚期作品组、Caravaggio追随者及其作品；分别处理Bassano/Caravaggio可能先例、Bellori文本关联、审美评价与picaresque比较。脚注L130–133均有对应分类与回链；OCR校读仅记S2，不改S0，不写S6正式关系。 |
| `chp-5:05_CHP-5_sec_iii:l28-34` | migration complete; semantic review pending | 早期提取记录保留：印刷页135有20条statement及29条mention，涵盖Van Laer抵罗、Haarlem背景、schildersbent、赞助与销售、画家群体评价、收藏及版画献赠等。当前20条statement的`relation_candidate`均未分类；p.134复核完成后按书序处理。既有OCR校读、跨页句与后置注释L134–138定位供复核使用。
| `chp-5:05_CHP-5_sec_iii:l36-43` | migration complete; semantic review pending | 早期提取记录保留：印刷页136有23条statement及41条mention，涉及Van Laer、Cerquozzi、匿名赞助群及多个可能关系。当前23条statement的`relation_candidate`均未分类；L43句尾续于后续正文段，须按书序复核并保持跨页限定。原OCR校读及脚注L139–141定位保留供复核使用。

| `chp-5:05_CHP-5_sec_iii:l45-57` | reviewed / complete | 印刷页137的Plate 21a/b图注新增4条精确跨度提及和2条题注归属断言，复用既有作品及艺术家候选。PDF物理第18页确认竖排题注：a为“Madonna of the Rosary with Saints”，b为“Madonna and Child”。S0倒排字符保持不改，提及锚定OCR原串；a图注未写出Dominic、Catherine，未从图版目录扩写本图注。题注归属不作为独立作者身份验证。 |
| `chp-5:05_CHP-5_sec_iii:l59-61` | reviewed / complete | 印刷图版Plate 22a/b新增5条精确跨度提及和2条题注归属断言，复用既有作品、艺术家及Masaniello候选。PDF物理第19页核实图版题注与图版清单一致；题注记录不作为独立作者身份验证，也不从a题名中的泛称扩写具名人物。 |
第5章35个已审段、6个有理由排除段均已迁移完成；queued/partial均为0。候选表面提示复核新增7个候选、26条mentions并链接10条既有statement；25/69条映射，其余44条均有记录理由且写后扫描吻合。全书当前状态及后续依赖见[全书S2结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)，逐项裁决见[过程记录](../process/stages.md)。

## 第5章脚注引用候选规范化（2026-10-10）

本章5条具有双端候选的`footnote_citation` statement已规范为`cites`候选。p.145的Passeri引用接至既有archive候选`cand-4376`；被引p.396尚未独立查阅，因此该对应仍是S2引用候选，不表示版本或页码已外部核实。详见[全书阶段记录](../process/stages.md)。

## p.142–145 Rosa书信脚注复核（2026-10-10）

另复核8条带书信指向的脚注statement：6条落到新建archive候选`cand-11571`–`cand-11576`，2条保留为对刊本的引用。每封信分别记录Rosa作者端点与Ricciardi收信人端点；p.145收信人由正文回链确认，非脚注明示。12 May 1651和21 May 1664的OCR/印本差异单独保留，书信与刊本均未独立查阅。至此本章13条双端脚注引用已规范为`cites`候选；全书S2交接仍未完成，详见[阶段记录](../process/stages.md)和[全书当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。

## 第5章p.120–123语义交接复核（2026-10-11）

coverage表中的p.120–123正文段此前已标记reviewed/complete；本次补充的是双端statement语义分类和原子化。p.120批次连同p.121跨页续文复核28条目标statement，新增12条statement、9个候选、14条mention；p.121另拆分Accademia禁令与税务事项。p.122将12条旧statement拆为17条，新增12个候选、13条mention。p.123复核8条正文和6条脚注旧statement，新增44条statement、5个开放候选、8条mention；按来源拆分Carlo任职、交往、偏好、委托、争执和Valguarnera交易，另分出Mancini的传述与关系。Dumesnil、Borzelli、Fraschetti、Eritreo引文与现有书目候选对齐；Jane Costello全名引用接至`cand-7016`，保留仅见姓氏的`cand-3509`，不在本阶段合并。

p.123页图核实OCR “T agreed”在印本为“I agreed”；仅记录校读和归属限定，不改S0。严格表审计`errors=[]`、`s2_missing=[]`，关系一致性五类硬错误为0，卡片预检`files_to_write=0`。当前全书双端未分类断言2,350条；下一游标为p.124正文L47的`st-chp5-p124-castiglione-dedication-interpretation`。全书S2交接未完成，见[全书当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)和[过程记录](../process/stages.md)。

## 第5章p.124正文及注释语义复核（2026-10-11）

对照规范正文段`chp-5:05_CHP-5_sec_i:l35-49`、注释段`chp-5:05_CHP-5_sec_i:l125-147`、`CHP-5.pdf`物理第5页及`p124_page_review_20261011.png`。复核21条既有statement，新增29条原子statement（18条关系候选、11条非关系陈述）；合计50条均已分类，其中29条为关系候选、21条为非关系主张。新增开放群体候选`cand-11709`–`cand-11714`及8条精确mention。拆分Mancini的病人赠画建议、患者难以拒绝、相对画商的优势和撰写Treatise所需知识；分开Simonelli的任职、管家评价、鉴赏名声、艺术建议、收藏组建/内容、偏好、艺术家接触与具体交往；拆开Monconys赴罗马、参观画室、两次引介、售画及Haskell对其他访客的推断。将三人共同特征、文书职业、不属于教会、友谊与赞助分开，保留“all”对三人的分配范围。Passeri、Scaramuccia、Testa、Chigi档案和Castiglione注释均按注1续文记录；引文定位不升级成独立查阅，未造未识别画作。

页图确认p.124只有一个正文上标注1，位于Simonelli姓名后；注释段L142为注1起始，源段L43–49为续文，不能视为印刷注2–6。Scaramuccia人名mention`m-chp5-p124-0027`从作品候选`cand-2391`改接人物候选`cand-2390`，相关版画接`cand-6018`；不在S2合并两个作品候选。受控脚本`classify_s2_chp5_p124_20261011.py`默认dry-run，校验来源、PDF、页图、两个分段及四张表的SHA-256，检查旧目标均未分类、候选/statement/mention ID唯一、关系端点有效和mention来源跨度；apply时为四表分别保留恢复副本`.bak-s2-chp5-p124-20261011`。写前statement/candidate/mention/coverage表SHA-256分别为`06e56489ae0136e1a00512c3f34f58762eef6a1834566d840d006f6b65cbc777`、`846dcd41f560846c52057da29e0f94cb9fe9e83a1c6763c8316699fc2daf1a1d`、`61103eb1409046d9d6409f0b3953b68f7dd0a99ee0073e7157dffd7e0b7b6426`、`1211ffbc9d99f39ee53b132b2585d316452384efa7577fc904e63b8e2775b260`；写后分别为`0e0cb51c776cf027f5adb373aa8b863dce550e084c5081a531e3858b5aa066eb`、`bb2bbb083346defcdc080fecd0853376489e3ae47bf69d58ec3a64cc2f8b1eef`、`544f4b1f7f996c750325052e94d47178a8a79889454ff6aa4aa0b704d5517cab`、`54486e616f6cf92da135f2dc899bee0ff87453b7a67ea30edb47e8c2a0c65213`。

写后全库13,271条statement、11,692个candidate、27,645条mention；`relation_candidate`为true 6,238、false 2,297、unset 4,736；9,037条双端statement中6,162 true、534 false、2,341 unset，76条true候选仍缺至少一个端点。严格表审计`errors=[]`、`s2_missing=[]`，仍有两条既存enrichment来源引用警告；关系一致性五类硬错误均为0，卡片预检`files_to_write=0`。第五章候选表面提示中与p.124相关的唯一未覆盖命中为泛词“drawings”碰到既有错类型候选`cand-0578`，属启发式误报，不新增实体。当前游标为p.125正文L52的`st-chp5-p125-three-figures-professional-label`；全书S2语义交接尚未完成。


## 第五章p.124注释1引用修订（2026-10-11）

印本注1的Monconys与Bellori引证分别规范为Haskell著作`cand-2962`到被引出版物`cand-11403`、`cand-4805`的`cites`候选。新增一条Bellori statement，保留原Monconys记录；被引来源未独立查阅。对应过程及写前/写后哈希见[全书过程记录](../process/stages.md)。

## 第五章p.125正文及注释续文语义复核（2026-10-11）

页125段`chp-5:05_CHP-5_sec_i:l51-58`复核19条既有statement并新增23条原子statement；新增25个开放候选`cand-11715`–`cand-11739`和27条精确mention，另将两条已有地点mention改接精确场所候选。42条目标陈述中32条为S2关系候选、10条为非关系标量/评价。分类覆盖展览和宗教日历、公众接触、画家群体、Sinigaglia轶闻、Claude与Wals、1607年Caravaggio《圣母之死》展示、Bergamasque社群展览、两处圣巴托洛梅奥场所，以及Ghezzi档案与Museo di Roma。传闻、作者推断、匿名群体、起始年代未明和观察者的不确定判断均保留限定；不创建S6正式边。页图确认OCR分节符、`we generally`、`general effect`及注释年份差异，未改S0。初次写回的两条重复地点跨度已删除，保留原mention并更新说明。

写后`audit_tables.py --strict-stage --summary`为`errors=[]`、`s2_missing=[]`；关系一致性五类硬错误为0。第5章表面定位器43条提示中，p.125正文和脚注段为0条未覆盖提示（仅为既有候选词面启发式）。当时全库双端未分类2,335条；下一游标为p.126正文L62 `st-chp5-p126-pantheon-annual-exhibition`。S2全书语义交接未完成。

## 第五章印刷页126正文（2026-10-11）

复核20条既有statement，新增38条原子statement、14个开放候选（`cand-11740`–`cand-11753`）和14条精确mention。58条本页statement全部分类：35条关系候选、23条非关系陈述。校正p.125 S. Bartolomeo展览的艺术家群端点，纠正Rosa画作—Simonelli见证关系的作品端点，并把“old masters”mention改接作品组。页图校读只记S2、不改S0；跨页的Miel遗嘱义务续句接回p.127。严格表审计、关系一致性审计和全卡预检均通过；全库双端未分类2,326条，下一项为p.127 L77 `st-chp5-p127-pantheon-1680-seizure`。完整裁决与SHA/恢复副本见[过程记录](../process/stages.md)。


## 第五章印刷页127正文（2026-10-11）

31条既有statement复核后新增15条原子statement，共46条全部分类（40条S2关系候选、6条非关系陈述）；新增14个开放候选及11条精确mention。修正1680年命令与实际扣押的区别、1662/1668展览实例、相应作品群和未名端点；分别记录Orazio和Baglione的竞争、画作地点、Cortona家族角色、Sacchetti旧大师借展、画廊所有者与Rosa支持者。p.128 L86–87引语闭合和Haskell对宣传效果的判断已接回。未修改S0来源或创建S6正式边。严格表审计errors=[]、s2_missing=[]；关系一致性硬错误为0；卡片预检files_to_write=0。全书下一游标为p.128 L88；详见全书S2过程记录与当前结果。

## 第五章印刷页128正文（2026-10-12）语义复核

对照规范来源`05_CHP-5_sec_i.md`（SHA-256 `8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee`）、段`chp-5:05_CHP-5_sec_i:l85-97`（SHA-256 `9c8360e14542de083d5e2414f7fdbf81b4f52f087f158d9d62239bcc023278d7`）、`CHP-5.pdf`物理第9页及页图`process/p128_page_review_20261011.png`（SHA-256 `b5d9f076776b10f2581345f7ecb6ad85b67cb844515e4b96d7216b3acd50f652`）。保留源OCR，不改S0。

复核24条未分类statement并新增15条原子statement；段内41条现全部分类：26条S2关系候选、15条非关系陈述、0条未分类。新增13个开放候选`cand-11768`–`cand-11780`及10条精确mention`m-chp5-p128-0054`–`m-chp5-p128-0063`，并把4条既有展览mention改接具体年度实例。分别登记S. Giovanni Decollato的1675与1736实例、S. Salvatore in Lauro的1675与1697实例；将系列与实例分开，拆分展品、挂毯、内部房间、Prince Pio及其他藏家的未名作品组、来自Marche的出借家族、St Peter’s传道者和枢机群体。Ghezzi的展览管理、学院职务、来源地及作者对其努力的评价分别记录。1736年教皇出价仅为希望；1697年St Peter’s是传道者来源而非展览地点；Ruspoli的1708句首与p.129完整陈述交叉链接。未生成S6正式关系。

受控脚本`process/classify_s2_chp5_p128_20261012.py`先按来源、段及写前三表SHA执行dry-run，再写回并保留三份恢复副本。写前statement/candidate/mention表SHA-256为`6f4042b9b027e6edea62a4e1ba58b9be112ca726eb2b177ecbc6a6651f1ee3a0`、`714c522c6c846612167ef934d16bba0eb2bdd9aadcd091322228cc778b154bba`、`6daa57037f79fb3eca85207b04091c710928d183f68dfc63afd4fb3fefd4b899`；恢复副本为`book-statements.jsonl.bak-s2-chp5-p128-20261012`、`entity-candidates.csv.bak-s2-chp5-p128-20261012`、`mentions.csv.bak-s2-chp5-p128-20261012`。写后SHA-256分别为`4076c417cd3429dfebb087d9ef414fd9b8f8a3af904549f2a94595054ff8905b`、`93e29fc48ff4de524a7649eb6029a6bc0bef7be751b2d2b5d9be86a52403e6f6`、`d8858ebe1c83e0cfd6138ff404d435f28a7d104018010c1e109bb35fde78d066`。JSONL保留原文件无BOM编码。

写后全库13,363条statement、11,758个candidate、27,707条mention；`relation_candidate`为true 6,369、false 2,350、unset 4,644；9,116条双端statement中6,293 true、537 false、2,286 unset；76条true候选仍缺至少一端。严格表审计`errors=[]`、`s2_missing=[]`，仅保留两条既存enrichment `source_ref`警告；关系一致性五类硬错误均为0。卡片预检`files_to_write=0`；全量同步闭合9/9通过（303 tests、2 subtests；结构契约130/130）。全书下一复核游标为p.129 L100 `st-chp5-p129-1708-ruspoli-condition-and-concession`。完整过程和后续全量闭合状态见[过程记录](../process/stages.md)与[全书当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。

## 第五章印刷页129正文（2026-10-12）

复核20条既有statement并新增14条原子statement，合计34条全部分类：21条关系候选、13条非关系陈述、0条未分类。新增开放候选`cand-11781`–`cand-11794`和15条p.129精确mention；更新Roman collectors既有mention，并给p.128的1708跨页桥句增加事件年份mention。页图确认印本“a fit”“primary aim”，OCR差异记入S2而不改S0。将1708年Ruspoli事件、其194幅作品、Olivieri获准悬挂的23幅作品及Ghezzi促成的条件分别记录；将Ottoboni雇用Trevisani与展示其作品拆开；分列Grimani送展的23幅Molinari作品、作者、相对死亡时间和罗马收藏者认知。1704年宣传例分别记录King John的未名胜利组、未名遗孀及拟借肖像/战役画的劝借关系，保留教皇身份仅为索引提示、实际借展未证。另记录四次定期展览、装饰媒介、旅行者与商人、外国赞助者及其本国艺术家、迁居罗马的外国艺术家群与外来文化艺术等关系；保留作者限定、推测和评价。所有边仍为S2候选，不写S6正式关系。下一游标为p.130 L109 `st-chp5-p130-aesthetic-view-and-connoisseurs`。详细证据、逐项裁决、恢复副本及表哈希见[全书S2过程记录](../process/stages.md)。

## 第五章印刷页130（2026-10-12）

复核19条既有statement，6条为S2关系候选、13条为非关系陈述，全部分类；新增来源限定的年轻艺术家群候选`cand-11795`及3条mention，纠正其与匿名购画公众之间的候选端点，保留Haskell的推断限定。页图核正`theprice`与`copied`前引号两处OCR差异，仅记S2；页下注1、2均链接到注释statement。全页26条mention跨度精确；全量同步闭合9/9通过（303 tests、2 subtests），结构契约130/130，项目规则契约4/4。所有关系仍为S2候选，S2全书交接未完成。详见[过程记录](../process/stages.md)。

## 第五章印刷页131正文与脚注（2026-10-12）

p.131正文26条既有statement全部分类，拆出8条原子statement，页内共34条（28条S2关系候选、6条非关系陈述）。新增`cand-11796`–`cand-11798`及2条mention；将Sassoferrato的未知赞助人、Holy Family作品群和未名clerics分开，修正赞助人群与p.130匿名公众的错误合并。核图校正OCR中的`tire`、`163 6`、`Pamftli`、`Giacinto GigE`、`diEgently`，只记S2，不改S0。

p.131注释段4条既有statement均已分类；新增3条原子关系断言和3条精确文献mention。Pollak卷I、Berthier及Gigli引用分别连至已有archive候选；肖像所描绘人物、书中所报馆藏机构及Prati在Benevento/Viterbo的职务拆开记录。`Galleria Nazionale di Arte Antica`复用已采纳机构KU；Pollak卷I候选保留卷次定位并关联书目识别线索，未独立查阅所引文献。

严格表审计`errors=[]`、`s2_missing=[]`；关系一致性硬错误0；卡片预检1,019卡、2,608表、10,149行、`files_to_write=0`。候选来源定位初审发现后修正为有效单行锚点；全书S2未完成。下一游标为第5章p.132开篇L3 `st-chp5-sec-iii-l3-self-made-taste`，其后正文p.132 L5–10有15条既有statement待复核。详见[全书过程记录](../process/stages.md)和[当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。

## 第五章印刷页132正文与脚注（2026-10-12）

p.132开篇L3与正文段`chp-5:05_CHP-5_sec_iii:l5-10`共16条既有statement全部完成分类；新增3条原子statement，正文合计19条（8条S2关系候选、11条非关系陈述）。新增来源限定的“最高阶层支持者”及“迎合非精英赞助人口味的艺术家”两个开放群组候选`cand-11799`、`cand-11800`及2条精确mention。保留Haskell对bambocciate最初支持来源的推断限定；将其后来自社会最高阶层的支持另列；区分作者关于影响力导致谴责的一般论断与艺术家迎合赞助人口味的条件关系。Bamboccianti命名、Passeri评语、罗马/乡间场景及1630–40年代语境分别保留；“campagna”地理范围未定。

p.132注释段n1–2中2条既有statement全部分类，并新增1条原子statement。Passeri引文保留其对Van Laer绘画的引述归属，不声称已独立查阅所引版本；“Passeri”原mention映射的是被引archive，与人物端点不重复叠加同一跨度。n2保留Haskell指向1950年展览目录的一般性书目指引，并另记Giulio Briganti撰写展览目录引言的关系候选；页图核正S0中的`Brigand`为印本`Briganti`，不改写来源OCR。新增脚注关系仍只是S2候选，不写入`relations.csv`。

受控脚本`process/classify_s2_chp5_p132_20261012.py`先dry-run再写回；`classify_s2_chp5_p132_notes_20261012.py`记录脚注分类。脚注首次写回后，严格审计发现人物mention与已有archive mention跨度重叠；受控修正`process/fix_s2_p132_note_mention_overlap_20261012.py`撤回仅由本次新增的重复行，保留原archive mention。最终statement/candidate/mention SHA-256为`817794cfddab7e9e02d0f1531584d2b437e795588e1995304e2ca9bdd53ee5da`、`012efa6759909bc8a1e9b7c16929f331b0b0c065279090c488810b00b25c8df4`、`665ebc1635b2af8282feba756bffe34d609786bea45c3f2f937f90a3b235681a`。最终严格表审计`errors=[]`、`s2_missing=[]`；p.133下一游标为`chp-5:05_CHP-5_sec_iii:l12-18`，有17条既有statement待分类。详见[全书过程记录](../process/stages.md)与[当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。


p.132写回后全量同步闭合9/9通过：303 tests与2个subtests、结构契约130/130、Skill注册8/8、项目规则契约4/4。严格审计仍保留两条既存enrichment source_ref警告；语义质量仍需独立检查。

## 第五章印刷页134正文与注释（2026-10-12）

p.134正文复核14条既有statement并新增13条原子statement，27条现全部分类（16条S2关系候选、11条非关系陈述）。另将note 1的Doni书目指引拆为独立`cites`候选statement；L130–133对应5条statement均已分类（3条关系候选、2条非关系）。新增6个来源限定候选`cand-11806`–`cand-11811`和5条精确mention；更新2条既有mention，并将`cand-6121` Colonna gallery标为place。将Caravaggio追随者群与其作品群分开，作品群再与picaresque novel建立候选比较关系；Doni、Rosa、Passeri引文均保持来源边界，未将Haskell引述当作独立核验。

受控写回脚本`process/classify_s2_chp5_p134_20261012.py`校验来源、PDF、页图、段及写前三表哈希后dry-run并写回。首轮严格审计发现新Doni候选的`candidate_origin`不符合枚举；已按schema修为`body-mention`并复审通过。写后全库13,418条statement（true 6,474、false 2,420、unset 4,524）、11,789 candidates、27,745 mentions；严格表审计`errors=[]`、`s2_missing=[]`，仍有两条既存enrichment来源引用警告；关系审计硬错误0；卡片预检1,019卡、2,608表、10,149行、`files_to_write=0`。按书序下一段为p.135 `chp-5:05_CHP-5_sec_iii:l28-34`，有20条statement待分类；全书S2交接未完成。详细来源哈希、表哈希、恢复副本和裁决见[全书过程记录](../process/stages.md)。


## 第5章第IV节p.142–143关系端点复核续记（2026-10-15）

将Rosa所在的“brilliant society”与p.143续句共用开放群候选`cand-12321`；把Rosa抱怨的客户群接到本段Haskell明示的Roman connoisseurs候选`cand-6218`，保留两种叙述立场；另为Bamboccianti艺术家与追随者的未名赞助人建立独立群候选`cand-12322`。反事实的权威枢机、未实现公共委托和理想赞助人仍保持开放。没有登记KU或S6正式关系。全库严格阶段审计通过，见[全书过程记录](../patrons-and-painters-full-book-s2/process/stages.md)。


规范段复核范围：`chp-5:05_CHP-5_sec_iv:l3-12`、`chp-5:05_CHP-5_sec_iv:l14-21`。

## 2026-10-15 p.144–145 开放端点复核

p.144新增候选 cand-12323 和精确mention m-chp5-p144-derossi-small-pictures，将De’ Rossi取得的Rosa小幅作品组与其私人博物馆及礼拜堂祭坛画分开；具体题名、数量未给出。p.145新增 cand-12324–cand-12327，分别表示De Dominici所述Giordano受众类别、Passeri所述作品出现的住所组、Rosa所抨击的conventional patronage，以及Haskell所述contemporary patronage的outer circles。四项均只按原文范围建模；前一引文不转归Rosa，住所不推定具体地址，社会成员身份不外推。“no one would take seriously”没有可界定受众，继续开放。无新增KU或S6正式关系。

写后严格阶段表审计通过：12,305 candidates、26,500 mentions、15,118 statements，开放端点481；errors=[]、s2_missing=[]。SHA-256及恢复副本见全书S2过程记录。


## 定点S2独立复核补充（2026-10-22）

第5章 p.138 `chp-5:05_CHP-5_sec_iii:l82-93` 的36条statement已逐条核读；31条既有mention跨度精确，补入4条缺失候选mention。为跨章确认同一死亡事件，第6章 p.146另补1条Urban VIII之死的精确mention，不把该局部修复记为整段复核。此项不代表第5章或全书接收；逐项依据见[S2复核记录](../process/s2-independent-review-chp5-20261022.md#s2-review-chp5-p138-battle-discussion-20261022)及[跨阶段批次](../process/knowledge.md#s3-s4-s5-s6-chp5-p138-cerquozzi-battle-discussion-20261022)。
