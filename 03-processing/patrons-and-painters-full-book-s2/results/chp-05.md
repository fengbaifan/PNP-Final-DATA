# 第5章语义处理结果

任务：patrons-and-painters-full-book-s2。第5章共41个规范段。按当前覆盖账本，35段reviewed、6段excluded，queued/partial均为0；41段的migration_status均为complete。当前计数以`04-knowledge/tables/s2-coverage.csv`为准，全书状态见`04-knowledge/results/patrons-and-painters-full-book-s2.md`，后续逐段记录见同任务`results/stages.md`。

## 早期逐段处理记录（保留当时状态）

下表和随后进度叙述记录阶段性处理过程，不是当前覆盖清单；其中旧的partial、queued和“下一段”记录均为历史快照。

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
| `chp-5:05_CHP-5_sec_iii:l12-18` | reviewed / complete | 印刷页133正文新增17个候选、29条精确提及和17条断言。闭合页132的Rome街巷描写；记录意大利农民的贫困、饥荒与粮荒、1648年以赦免换粮提议、乞丐群体、疫病、台伯河洪水、教皇去世与临时治理、纪念雕像、罗马骚乱、法国/西班牙使馆群体紧张，以及Haskell对Bamboccianti作品“宁静窗口”与社会抗议的判断。Michael Sweerts、Le Nain、Velasquez与Doni的发言层级分别记录；未名人物和群体保留限定。PDF物理页14核实L16印本为“we find”，S0 OCR“wesind”不改。脚注1指向待处理注释L129；页134 L21闭合L18的Doni引语。
| `chp-5:05_CHP-5_sec_iii:l20-26` | reviewed / complete | 印刷页134正文新增6个候选、23条精确提及和14条原书断言/引证。闭合页133 L18的Doni引语；记录Rosa诗句及Haskell译文对贫者图像的限制、Passeri关于Van Laer小尺幅人物的引述、背景扩张使乞丐与牧人变为如画附加物、Van Laer与Bamboccianti的新题材、Bassano/Caravaggio与Bellori的关联、Caravaggio作品中贫者的呈现，以及Annibale Carracci的《豆食者》和未具名劳动题材素描。嵌套引述、作者判断和“也许”等限定保留；未名追随者、Colonna gallery的具体空间和未题名素描保持待决。扫描核实Passeri处“one palmo (22½ cm.)”、hills、himself、ordinary、Annibale等OCR差异，只记校勘不改S0；提及锚点仍精确对应S0 OCR原串。脚注1–4待与后置注释L130–133迁移后回链。L26末句“But these”由页135 L29闭合。 |
| `chp-5:05_CHP-5_sec_iii:l28-34` | reviewed / complete | 印刷页135正文新增8个候选、29条精确跨度提及和20条原书断言/引证。闭合页134关于Annibale Carracci作品的跨页句，并记录Haskell所谓“无真正先驱”的艺术史判断；处理Van Laer于1625年抵罗、Haarlem成长背景与写实传统、schildersbent社群、非官方赞助处境、集市和画商销售、30/35 scudi要价与昂贵声誉、买家难以确认；记录画家群体对其作品的赞誉、Swanevelt拥有两幅、Testa与早期bamboccianti的联系、罗马赞助人谨慎关注、Simonelli短暂持有并交换两画、Giustiniani购藏两幅不寻常作品，以及Cassiano可能收藏一幅Van Laer画作。另记录Van Laer约离罗前三年将八幅动物版画献给Don Ferdinando。保留Passeri转述、作者推测及价格/所有权语气；具体画作依索引子目映射，Schildersbent与Bentvueghels的身份留待S3，赠献对象的全名已由页136 L37补全为Afan de Ribera（那不勒斯总督）。扫描核对印本拼写与S0差异；后置注释L134–138（页135脚注1–5）待迁移回链。 |
| `chp-5:05_CHP-5_sec_iii:l36-43` | reviewed / partial | 印刷页136正文新增9个候选、41条精确跨度提及和23条原书断言/引证。补完Don Ferdinando Afan de Ribera那不勒斯总督头衔；记录西班牙人与bamboccianti成功的关联、Van Laer处于社会边缘及其匿名中等身份客户群、其对罗马与欧洲绘画的影响和约1639年的市场需求。后转Cerquozzi：罗马出身、低价向画商售画后获鉴赏家注意、意大利身份与赞助人联系优势、其现实主义受贵族社会限制；再记录其艺术家友人及对年轻人的支持、职业阶层赞助人Marchesi/Neri、Plate 22a、与Spanish Embassy及Velasquez/Monterey的可能关系、Colonna与Hispanophil clans、Cerquozzi的西班牙关联。所有“probably / possible / some evidence / more likely”保持原有限定。姓名复用索引候选，未知官方、使馆、匿名群体和作品组各自待决；脚注1–4待与L139–141迁移回链。扫描确认S0 L42的`1630?`是印本1630加脚注3，L43 OCR粘连需按印本校正但不改S0。L43句尾“and until his later years”续于插入图版后的下一正文段，本段partial。

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
