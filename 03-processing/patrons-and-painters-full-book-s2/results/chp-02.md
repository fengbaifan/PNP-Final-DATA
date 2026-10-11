# 第2章语义处理记录

状态：**第2章S2已完成；全书任务继续处理中**。第2章规范账本共75段：64段reviewed/complete、11段有理由排除、0段queued。第VII节L38–54注释、第VIII节L3–7和L9–14已完成迁移；生成式标题段第VIII节L1–1按版面导航有理由排除。Plate 5题注曾误按Plate 6错位OCR排除，已依据物理页22恢复迁移。脚注跨段回链和整章OCR差异核查已完成；跨章身份及未决映射保留到S3处理。

## 来源与校勘状态

- 主体OCR：所有已迁移片段均按segments.jsonl规范来源及行范围处理；旧第I节阅读稿映射不可靠的未复核段继续queued。第II节已迁移至L147–193；第IV节正文与脚注L190–245已迁移；第VII节L3–3、L5–19、L21–30、L32–36、L38–54及第VIII节L3–7、L9–14已迁移。印刷页59–62（PDF物理页48–51）已核对新迁入片段；整章OCR逐段差异对照已于2026-09-27收口；差异及处理见本文件末尾。
- 全章对照OCR：[02_CHP-2.md](../../../02-sources/02-Markdown/02_CHP-2.md)，976个物理行。整章文本已逐项与规范分节OCR及必要PDF图像对照；图版页题和组题缺录已补入派生转录，并保留本章差异记录。
- 原分节OCR共66段：章首intro 3段、sec_i 14段、sec_ii 18段、sec_iv 22段、sec_vii 6段、sec_viii 3段；另有9个视觉转录段，共75段。当前64段迁移完成、11段有理由排除、0段queued。逐段语义判断见本文件，过程及历史变更见任务过程记录。
- 第2章书页从24页起。已核对的第IV节正文印刷页43–56（PDF物理页28–41）及脚注印刷页44–58（PDF物理页29–47）覆盖相应迁移片段。脚注段L190–245现已完整登记，52条正文脚注关联已回链；脚注1印本续文、L228的Montagu/Vitzthum续引、L242的Bellori关于《Rest on the Flight into Egypt》续引均以校读限定保存，S0 OCR不改写。注号和Teti等OCR差异已核对；全章与整章OCR的逐段差异核对已完成。

当前载体指纹（SHA-256）：

| 来源 | 页数／行数 | SHA-256 |
|---|---:|---|
| `02-sources/01-book/CHP-2.pdf` | 51 PDF页 | `317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e` |
| `02_CHP-2_intro.md` | 7行 | `4e93f8f73b981ff35a8b95df2f379e787c55fce396fee21d971dd7831b192e74` |
| `02_CHP-2_sec_i.md` | 157行 | `5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6` |
| `02_CHP-2_sec_ii.md` | 193行 | `7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9` |
| `02_CHP-2_sec_iv.md` | 245行 | `9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf` |
| `02_CHP-2_sec_vii.md` | 54行 | `5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c` |
| `02_CHP-2_sec_viii.md` | 14行 | `95f938db89eb64a86bbc54065bf1e93e2d4849cd6ed5e6b02aedbe0f1e23350a` |
| `02_CHP-2.md` | 976行 | `637df5cda69629f5dce6e09502a160d097dfc28ffe874faebbc26a82d02594ca` |

## Plate 5题注错位纠正（2026-09-27）

规范段`chp-2:02_CHP-2_sec_ii:l106-107`此前被误判为Plate 6的错误OCR并排除。回看`CHP-2.pdf`物理第22页确认，此段实际对应Plate 5下方的“Bernini: Cardinal Borghese”；同页上方标题明确为“Cardinal Scipione Borghese and his Patronage”。据此将覆盖改为`reviewed/complete`、源行L107，新增3条嵌套提及和1条图注归属断言，复用`cand-4135`（版本未定的Bernini肖像）、`cand-0295`（Bernini）及`cand-3011`（Scipione Borghese）。原S0 OCR分号保留，印本冒号只作校读限定。该肖像仍与正文所述两件Scipione胸像保持分离。Plate 6的真实图注是Guglielmo Baur《View of Villa Borghese in 1630》，已由独立视觉转录段记录。此次修正将第2章状态更新为60段迁移、11段排除、0段queued；整章OCR对照和剩余未决项仍未完成。

## 旧版第I节阅读草稿（未映射行段不作覆盖证据）

> 这份旧表曾把章级阅读摘要绑定到分节文件的行号；复核发现绑定不可靠。当前已按规范S0逐段重读的段落详见下方迁移记录。其余旧表行只作检索线索：实际S0中，L9–10为图版I题注，L12–13为页码与反向OCR残片，L15–29与L31–42分别是图版III、IV的反向OCR残片，L44–53才是印刷页25正文。不得将旧行摘要或旧标记视为当前覆盖证据。

| 规范段 | 来源行 | 句意及语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_intro:l1-1` | 1 | 自动生成的OCR文件标题，不是原书文本。 | 依覆盖规则排除，不建提及或断言。 |
| `chp-2:02_CHP-2_intro:l3-4` | 3–4 | 原书第2章起于印刷页24。 | 仅为章节和页码定位。 |
| `chp-2:02_CHP-2_intro:l6-7` | 6–7 | 章首脚注给出Urban VIII与Barberini研究的通用参考：除非另有说明，参见Pastor第XIII卷和Pecchiai（1959）。 | 记作全章默认书目依据，不把引文当成独立事实；`Pastor`与`Pecchiai`的具体书目对象须对照书目表再映射。 |
| `chp-2:02_CHP-2_sec_i:l1-1` | 1 | 自动生成的分节标题，不属于原书语料。 | 依覆盖规则排除。 |
| `chp-2:02_CHP-2_sec_i:l3-7` | 3–7 | 旧稿摘要，内容不全且曾漏记本段后半的Sixtus V与罗马改造材料；现由下方逐段S2记录取代。 | 该行不作为当前提取或覆盖依据。 |
| `chp-2:02_CHP-2_sec_i:l9-10` | 9–10 | 旧摘要错挂；实际段是页码导航与Valentin图版I图注，具体迁移见下文。 | 旧摘要不作为当前S0映射或覆盖依据。 |
| `chp-2:02_CHP-2_sec_i:l12-13` | 12–13 | 旧摘要错挂；实际S0只有页码与反向OCR残片，图版II可读题注已转录到独立补充段。 | 旧摘要不作为当前S0映射或覆盖依据。 |
| `chp-2:02_CHP-2_sec_i:l15-29` | 15–29 | S0为图版III页眉和反向OCR题注残片。PDF物理第4页可读的Leoni／Cardinal Francesco Barberini及Maratta／Cardinal Antonio Barberini题注与书前图版清单重复。 | 覆盖有理由排除；题注内容已由书前清单承载，不重复制造提及或断言。 |
| `chp-2:02_CHP-2_sec_i:l31-42` | 31–42 | S0为图版IV页眉和反向OCR题注残片。PDF物理第5页可读题注已追加至独立视觉转录段`sec_i_visual-transcription:l6-9`。 | 该残片有理由排除；可读题注和Guido Bentivoglio全名已在视觉转录段迁入。 |
| `chp-2:02_CHP-2_sec_i:l44-53` | 44–53 | 印刷页25记Maffeo任Fano总督、约1595年肖像及Caravaggio patronage、1598年随Clement VIII赴Ferrara、Este艺术品被掠与三幅Titian作品返罗马，继而叙述叔父遗产异文及Barberini家族礼拜堂选址。末句关于大理石风格的“the same”跨段续接。 | 已完成迁移：11个候选、39条精确跨度提及、25条原书断言。保留肖像“thought to be”、两种遗产估值、Haskell对Ferrara事件的评价及未知掠取者；PDF物理第6页核校OCR `os/of` 与 `purpose.be/purpose, he`。脚注1–6待注释S0段迁入后交叉链接。 |
| `chp-2:02_CHP-2_sec_i:l55-69` | 55–69 | 旧草稿仅记录巴黎任职等后半段内容，覆盖不完整；现以本文件下方的逐段S2迁移记录为准。 | 旧摘要不作提及、断言或覆盖证据。 |
| `chp-2:02_CHP-2_sec_i:l71-80` | 71–80 | 旧阅读草稿仅作检索线索；该段已按S0来源逐段迁移，见下方“已完成迁移：第I节L71–80”。旧摘要不作为当前覆盖证据。 | — |
| chp-2:02_CHP-2_sec_i:l82-93 | 82–93 | Scipione收藏与Pincio别墅、Paul V去世后的赞助格局变化、Agucchi的理论及del Monte的身份描述。 | 已迁移52条提及和34条原书断言；旧摘要不作为覆盖或事实依据。 |
| `chp-2:02_CHP-2_sec_i:l95-106` | 95–106 | 旧读稿将Scipione与Pincio材料误配到此段；本段实际讨论del Monte晚年、Caravaggio与Andrea Sacchi，以及Vincenzo Giustiniani的宅邸、收藏和艺术趣味。旧摘要不作覆盖或事实依据。 | 按规范S0来源迁移34个候选、84条提及和51条原书断言；脚注1–4与后置注释段待交叉链接，脚注5只作书目指针。 |
| `chp-2:02_CHP-2_sec_i:l108-119` | 108–119 | 旧摘要误配到本规范行：其Paul V／Gregory XV与Agucchi叙述不对应当前S0 L108–119，保留为旧稿错位记录，不作为本段覆盖依据。当前语义处理见下方“已完成迁移：第 I 节 L108–119”。 | 旧行号草稿不得替代当前来源逐段阅读。 |
| `chp-2:02_CHP-2_sec_i:l121-121` | 121 | 过渡句提示除教皇及侄子外，罗马还有其他活跃赞助者。 | 章节结构，不构成新实体或独立关系。 |
| `chp-2:02_CHP-2_sec_i:l124-157` | 印刷页25–31脚注 | **旧映射更正**：此前把本规范段误记成del Monte、Giustiniani、Maffeo与Bernini正文；实际S0段是正文之后的脚注。逐注内容、原文校勘及其与正文行段的交叉链接见下方新增迁移记录及任务过程记录。 | 此段现已按脚注来源逐条迁移，不再沿用旧正文摘要；相关引述、书目定位与作者限定均保留在对应脚注断言中。 |

## 已完成迁移：第 I 节 L3–7（2026-09-27）

| 规范段 | 印刷页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_sec_i:l3-7` | 24 | 记述Maffeo Barberini的出生、家庭、教育、早期仕途与作者对其抱负的推测；随后转入Sixtus V时期罗马治理、教会制度和城市改造。圣斐理伯·内里预言为Haskell转述；“绝对独裁”和“Sistine Rome”是作者的评价/概括，不作独立核实事实。 | 新增6个开放候选（未名耶稣会学校、教廷、十四世纪祖先Francesco、Campagna、天主教会制度指称、Sistine Rome术语），写入29条精确跨度提及和24条原书断言。复用Maffeo/Urban VIII、Barberini家族、叔父Monsignor Francesco、Rome、Pisa、St Philip Neri、Sixtus V、Michelangelo、St Peter’s Basilica与Domenico Fontana候选；叔父与祖先Francesco分开。未建立正式关系边。 |

`CHP-2.pdf`物理第1页对应印刷页24。S0原文首行`AFFEO`漏掉装饰首字母M，下一行`Mand rich`含掉字母OCR残留；印本核实应为“Maffeo”与“and rich”，但原始S0及断言引句不改写，校正只记在限定中。家庭句脚注1交叉链接至已迁移的`intro:l6-7`；该脚注是一般书目提示，不充当该句的独立证据。旧第I节草稿将后续摘要错挂至行段，尤其把图版页导航/图注误作Sixtus V正文；这些旧稿已降级为检索线索，规范覆盖仍以队列逐段重读为准。

## 已完成迁移：第 I 节图版 I L9–10（2026-09-27）

| 规范段 | 印刷定位 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---|---|---|
| `chp-2:02_CHP-2_sec_i:l9-10` | PDF物理第2页，Plate I | S0包含页码`i`及题注`Valentin: Allegory of Rome`。图像和题注对应关系经PDF目视核实。 | 复用Valentin de Boulogne索引候选和《Allegory of Rome》既有KU候选，新增2条提及、1条图注归属断言；与书前图版目录相同文字保留为书中独立印刷位置，不据此验证作者身份或现藏。 |

## 图版 II：OCR残段排除与视觉转录迁移（2026-09-27）

规范段`chp-2:02_CHP-2_sec_i:l12-13`仅有`[Page 2]`及反向识别残片`)3 dna`，无可用的原书行内题注；该残段按版面/OCR残留排除。PDF物理第3页显示Plate 2及其组题、2a/2b题注。为使题注可精确引用，已将可见文字追加到来源派生文件`02_CHP-2_sec_i_visual-transcription.md`，由S0构建为`chp-2:02_CHP-2_sec_i_visual-transcription:l1-4`，原PDF及OCR文件未改写。

补充段迁入8条精确跨度提及和4条图注断言。复用书前图版清单已有的Caravaggio归属作品、Bernini作品、创作者与Maffeo Barberini候选；Plate 2a题注独有的“as young prelate”记为图注描述，且保留“Attributed to”的归属限定；Plate 2b的Pope Urban VIII身份与目录题注一致。组题“THE BARBERINI PATRONS”作为Barberini家族语境提及，不将图版标题当作历史断言。

## 已完成迁移：章首脚注 L6–7（2026-09-27）

| 规范段 | 印刷页 | 句意及语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_intro:l6-7` | 24 | 章首脚注1将Pastor第XIII卷与Pecchiai（1959）列为Barberini家族及Urban VIII相关内容的一般参考，除非另有说明。该文字是书目指引，不是对本章具体事实的独立证据。 | 写入6条精确跨度提及、2条引文定位断言和3个开放候选：Pastor第XIII卷（版本未指明）、作者P. Pecchiai（全名未明）、`I Barberini`（1959）。复用Barberini family索引候选、Urban VIII与Pastor作者候选；文献项通过本书书目相应条目作暂定映射，后续书目S2须复用而不重复建对象。未建立正式边或外部核验结论。 |

`CHP-2.pdf`物理第1页对应印刷页24；目视核对脚注，确认“Pastor, XIII, and Pecchiai, 1959”与S0 OCR一致，无需校正。书目S0第934–940行用于识别Pastor条目及Pecchiai的`I Barberini`条目；具体卷册版本、Pastor引文页码和Pecchiai全名仍未解决。脚注原文引句只保留对应缩称，各断言限定其一般参考性质。覆盖更新为`reviewed/complete`。

## 已完成迁移：第I节L44–53（2026-09-27）

| 规范段 | 印刷页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_sec_i:l44-53` | 25 | Haskell叙述Maffeo在1592年任Fano总督、约1595年委托Caravaggio绘制一幅被认为是其肖像的作品；并称Maffeo后来委托Caravaggio创作《The Sacrifice of Abraham》。1598年Maffeo随Clement VIII赴Ferrara接收城市，教廷掠取Este长期积累的艺术品；Cardinal Aldobrandini带三幅Titian作品回罗马。段落又记录叔父遗产估值异文、Maffeo筹建家族礼拜堂并选择S. Andrea della Valle，以及Matteo Castelli和抛光彩色大理石的风格描述。 | 新增11个开放候选，写入39条精确跨度提及和25条原书断言。Caravaggio肖像身份保留“thought to be”；Ferrara接管的描述与Haskell对“unscrupulous pressure”的评价保持作者归属；掠取者未指明；Titian三作分别建作品候选并记录返罗马叙述；遗产估值不合并为范围；家族礼拜堂与教堂分开。未生成正式关系边。 |

PDF印刷页25（`CHP-2.pdf`物理第6页）核对正文与页下注。印本确认S0 OCR `The Sacrifice os Abraham`及`Worship os Venus`中的`os`均为`of`，`For this purpose.be chose`为`For this purpose, he chose`；原OCR引句不改写，校勘只记入限定。Footnote 1–6仍须待对应注释S0段迁入后交叉链接。L53止于`the same`，下一规范段L55–69以`basilica`续句；本段未将下一段原文并入引句。

## 已读脚注与OCR待核

第I节的脚注涉及Caravaggio肖像归属/年代（Longhi、Bellori、Mahon、Hinks）、Este藏画、Barocci书信、Barberini家族礼拜堂、Scipione收藏、Agucchi理论、del Monte、Giustiniani收藏与旅行、Peiresc通信、Guido Reni书信及Bernini早期委托等。部分姓名与意大利语参考书目在OCR中变形（如 `Passed`/Passeri、`osa`/of a、`hfe`/life）；引文及书目项目待与PDF和书目表逐项校正，不把OCR错误直接登记为事实。

## 已完成迁移：第II节 L3–8（2026-09-27）

| 规范段 | 印刷页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_sec_ii:l3-8` | 31 | Haskell叙述Urban VIII当选后对亲属的枢机任命、其家族的艺术赞助、亲族任用及财富逻辑；随后讨论罗马自治衰退、封建家族承压和1624–1629年的三笔地产转让。使节引语、Haskell叙述和传闻分层；身份未明的“one papabile cardinal”侄子及威尼斯使节不具名；Lorenzo Magalotti的姻亲说法保留原文而不推定精确亲属链。 | 写入28条精确跨度提及、19条原书断言和5个来源衍生候选。分别记录Urban VIII对Francesco、年长Antonio、Lorenzo Magalotti及年轻Antonio的枢机任命；Taddeo的政治职位、财富与婚姻前景不补造授予者。Orsini家族—Monte Rotondo地产—Carlo Barberini、Colonna家族—Roviano城堡—同一买方，以及Colonna一支—Palestrina公国—Barberini家族的转让分开记录；不为未具名支系指定个人。 |

PDF印刷页31（`CHP-2.pdf`物理第12页）核对与整章OCR L232–241对照。印本确认“26-year-old”的跨行连字符、“one papabile”、“self-government”、“participating in the great”、“for a long time”及“all this,”；规范分节OCR保留原转录，校正写入断言限定。脚注标记1–5保留在相关断言中；脚注原文位于后续注释S0段，待迁移后链接到对应叙述。脚注5指出Prince Francesco Colonna的来信宣布Palestrina出售，但本段仍不指定具体出售支系或个人行为人。

## 已完成迁移：第II节 L10–18（2026-09-27）

| 规范段 | 印刷页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_sec_ii:l10-18` | 32–33 | Haskell叙述旧封建家族为新统治精英提供贵族婚配的社会角色，并称Anna Colonna（Contestabile之女）被选为Taddeo新娘；只记录选择，不推定婚姻完成。随后记录教皇领地收入估计、罗马自给能力、教廷财政赞助与高价出售官职；保留Haskell对Urban VIII建筑支出的推断，以及Pietro Contarini、Gregory XIII两层不同引述。Urban的三重角色及其对赞助范围的影响按作者框架记录，L18作为待续片段。 | 写入35条精确跨度提及、21条带行号断言及5个来源衍生候选。Contestabile保持身份未明；威尼斯使节群体与单一匿名使节分开；“Catholic world”与Catholic Church分开；Papal States的指称与Rome城市不混并。脚注1–5保留待对应注释段迁入后交叉链接。 |

PDF印刷页32（`CHP-2.pdf`物理第13页）及印刷页33（物理第14页）对照分节OCR和整章OCR核读；L18在下一规范段L20–28续接。句中Contarini的1623年引语与脚注5对Gregory XIII的身份说明均保留各自引述层级。L10–18完成时，第2章66段中2段迁移完成、64段仍queued；章首与第I节虽已有完整阅读记录，S2表迁移仍未完成。

## 已完成迁移：第II节 L20–28（2026-09-27）

| 规范段 | 印刷页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_sec_ii:l20-28` | 33 | 承接L18：Haskell称Urban VIII的三重角色有时造成不可化解的张力，随后分别讨论其时间／精神领导者身份面对的教廷威胁、法国与哈布斯堡帝国竞争、军事中立及其对法国联盟的依赖。作者把罗马的宗教危机、知识变化、镇压与秘密宽容、宗教建筑和巴洛克说服力串为解释链；Naudé引语经Haskell与Pintard转引。 | 新增7个候选、33条精确跨度提及和16条原书断言。复用Henri IV、白山战役、Richelieu、Accademia dei Lincei、Galileo、Rome、Italy及既有术语候选；France、Hapsburg Empire、Papacy、Roman Court、Protestant advance、spiritual crisis、persuasion登记为开放候选。L18前段与本段L21续句通过statement ID互链；脚注1–3待注释段迁入后交叉链接。 |

PDF印刷页33（`CHP-2.pdf`物理第14页）核对整页正文及脚注。分节OCR的“tire attention”按印本记录为“the attention”，但原书断言仍逐字保存OCR并在限定中注明；印本确为“Hapsburg”。脚注3指明匿名法国引述者为Gabriel Naudé（经Pintard转引）；该识别依据与引文层级均已记录。L20–28迁移后，全书账本为50段迁移完成、11段有理由排除、729段排队，提及1,492条、断言858条。

## 已完成迁移：第II节 L30–40（2026-09-27）

| 规范段 | 印刷页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_sec_ii:l30-40` | 34 | Haskell把Barberini风格的宏大、胜利与说服力归于Bernini，转引Passeri关于Urban VIII与博洛尼亚艺术群体的判断；记录Bernini出身的转述、其获得Urban青睐及Urban偏好托斯卡纳艺术家的叙述。随后记Bernini早期职位、Urban对圣彼得大殿的关注、Maderno立面、中央区装饰及Bernini于1624年启动巴尔达基诺工程。工程面对古墓和青铜障碍，Haskell分别称以考古调查/记录和剥取Pantheon青铜应对，称九年后完工。匿名批评和Urban赞语均保留引述及作者限定。 | 新增9个候选、42条精确跨度提及和20条原书断言。复用Urban VIII、Bernini、Paul V、St Peter’s Basilica、Michelangelo、Passeri、Baldinucci、Florence、Naples、Rome、Carlo Maderno（采用索引页34候选）与Farnese Palace。另登记Barberini style、Bolognese/Tuscan artists术语、Peter the Apostle、圣彼得大殿立面/穹顶、巴尔达基诺、被称作supposed tomb的地点及Pantheon。人物、建筑、建筑构件、作品和地点分开；不将未具名父母、引语观察者或早期墓葬强行具名。 |

印刷页34（`CHP-2.pdf`物理第15页）核对正文与脚注1–5。页下注分别支撑Passeri说法、Bernini父亲出身、Urban赞语、立面批评和工程文献定位；脚注原文所在S0段尚待迁入后交叉链接。OCR将印本`Cavaliere`识作`Cavalière`、将`his`识作`lais`，并在`problem was`间插入多余撇号；原书引句保留S0转录，校勘写入限定。本段迁移时全书账本为51段reviewed且迁移完成、12段有理由排除、727段queued；提及1,534条、原书断言878条。

## 当前限制与接续

全章原有66个规范S0段，新增5个图版页/题头视觉转录段后共71段。当前35段迁移完成、10段有理由排除、26段queued。第I节旧阅读稿行号错位的段须按规范来源重读；最近完成第IV节L31–43，下一段为L45–52。

接读位置：`02_CHP-2_sec_iv.md` 的L45–52。第IV节L31–43已核对印刷页46（PDF物理页31）；脚注6从第45页续入本段L39–43，并回链至前段L25的脚注标记。第46页脚注1–4的完整文字收在后置规范注释段L201–204，待该注释段迁移时回链，避免在本段重复登记。第I节旧阅读草稿未按规范段重读的部分仍保持queued；第II节与此前片段尚待注释交叉链接的项目按后置注释段逐项处理。

## 已完成迁移：第 I 节 L55–69（2026-09-27）

| 规范段 | 印刷页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_sec_i:l55-69` | 26 | 承接上一段末尾的“the same basilica”，随后记录Maffeo Barberini较早采用大理石装饰风尚、其礼拜堂规模与装饰评价；Barocci因年长无法绘制祭坛画，Maffeo另请其为私人寓所寄画；其后转向Passignani，记礼拜堂穹顶的装饰方案、穹顶壁画和窗间壁画；再叙Maffeo于1604年任驻巴黎使节、与Henri IV的往来、1606年获枢机身份、从法国返罗马所得赠礼与蜜蜂徽记、法国文化影响的作者解释及Renier Zeno的后见评价；末段记Maffeo在巴黎期间续办礼拜堂装饰、与兄弟Carlo购置并布置Via de’ Giubbonari附近宫殿，以及反对Paul V改变Michelangelo圣彼得大殿方案。 | 新增16个正文来源候选、45条精确跨度提及和23条原书断言。区分礼拜堂、教堂、穹顶空间与壁画作品；分别保留Barocci的祭坛画受限与未注明题目的私人绘画请求；Passignani提出的彩色马赛克/镀金灰泥方案仅为建议，实际委托与作品另记；法国支持群体未具名；Henri IV长子的身份不由相对年代推定；银器赠礼及“蜜蜂来自法国王室纹章”的说法仅按原书转述，后者留待外证；Renier Zeno身份据印刷页26脚注4识别，脚注跨段迁移待办；两个宫殿记为可能不同对象，暂不合并。 |

印刷页26（`CHP-2.pdf`物理第7页）核对正文与脚注1–4。原OCR中法语引文的`quatte`、`avoirs`依印本记为`quatre`、`avons`，原始S0引句不改写。脚注1–4在同一分节文件的后置行段中，尚未完成S2迁移和对应关系链接；本段只使用页下注4识别Renier Zeno为引语来源，并保留待交叉链接标记。段首`basilica`接续前段Paul V在同一大殿采用该风格的断言；末句在“as proposed by”处跨至下一S0段L71–80，当前不提前补入Carlo Maderno。迁移后全书账本为58段reviewed且迁移完成、18段excluded、716段queued；提及1,670条、原书断言961条、候选4,271个。`audit_tables.py`结构错误为0；全书语义审查仍未完成。

## 已完成迁移：第 I 节 L71–80（2026-09-27）

| 规范段 | 印刷页／PDF页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---|---|---|
| `chp-2:02_CHP-2_sec_i:l71-80` | 27／物理第8页 | 接续前段“as proposed by”，将圣彼得大殿加建中殿方案归于Carlo Maderno；叙述Maffeo Barberini离开罗马、任Spoleto主教、1611年赴Bologna任使节、1617年返回罗马常住。随后记Paul V及侄子Scipione Borghese在宫廷赞助、罗马建筑与收藏上的投入；并以S. Maria Maggiore礼拜堂、Quirinal Palace装饰及Pincio／Frascati别墅描述其文化环境。Haskell把Paul V时期的艺术概括为从克制功能主义转向表面、光影、色彩、题材和实验；另记Scipione的人格评价、没收d’Arpino画作、取走Raphael《Deposition》及Domenichino因遵守Aldobrandini委托而被监禁的叙述。段末“a wonderful”未完句跨到L82–93。 | 47条精确跨度提及、23条原书断言。新登记14个来源候选；立面复用既有`cand-4232`，不重复建候选。将“Borghese country houses”作为类型待决的复数地产组，避免映射成Scipione个人；Pincio与Frascati分别保留为地点。另拆录Scipione为Paul V侄子的明确称谓，以及Haskell“出身良好但学识有限”的评价；不把评价改写成外部核实事实。没收画作、夜间取画和监禁按不同主客体及行为分别记录，不合并成笼统赞助关系。 |

PDF印刷页27（物理第8页）核对确认分节OCR的`hfe`应为`life`，印本写作`Cavaliere d’Arpino`而非OCR的`Cavalière`；S0原文与断言引句保持原样，校勘记入对应限定。脚注1–4位于同一分节文件后段（L136–139），其中脚注2将威尼斯使节引语定位到Renier Zeno（1621–1623）；所有脚注仍待相应S0脚注段迁移后正式交叉链接。候选外键、提及跨度和断言行锚均通过当前表审计。迁移后总账：60段reviewed且迁移完成、18段有理由排除、714段queued；候选4,302、提及1,769、原书断言1,018。


## 已完成迁移：第 I 节 L82–93（2026-09-27）

| 规范段 | 印刷页／PDF页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---|---|---|
| chp-2:02_CHP-2_sec_i:l82-93 | 28／物理第9页 | 承接Scipione收藏的未完句，记录收藏类型、Pincio别墅与罗马社交生活；继而记Paul V于1621年去世、Gregory XV继位及Scipione失势，再说明Ludovico Ludovisi、Agucchi、Domenichino与Guercino在新赞助秩序中的位置。随后分层记录Agucchi的职务、艺术理论及其对自然模仿与理想的看法，并转入Cardinal del Monte。 | 新增17个候选、52条精确跨度提及、34条原书断言。保留Haskell对收藏、赞助和“classic”反应的评价，不转成无来源的客观分类；Agucchi对Caravaggio观点的批评仍标为原书归述；未具名Grand Duke、casino与del Monte住所均不推定为具体对象。Domenichino师承与Agucchi交往分开记录；Guercino风格变化保留为限定性作者判断。 |

印刷页28（CHP-2.pdf物理第9页）已目视核对。原OCR的longterm对应印本跨行long-term，proteges在印本为protégés；S0转录和原书引句保持不改。L93末尾“a living corpse . . .”引语跨到L95，后续段需接续并连到脚注1；本段脚注1–3标记尚待对应脚注S0段迁移后交叉链接。Farnese palace提及暂复用索引候选，但其索引页码范围不含印刷页28，保留供S3复核。当前审计通过，迁移后全书为60段reviewed/complete、18段excluded、714段queued；候选4,302、提及1,769、原书断言1,018。

## 已完成迁移：第 I 节 L95–106（2026-09-27）

| 规范段 | 印刷页／PDF页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---|---|---|
| chp-2:02_CHP-2_sec_i:l95-106 | 29／物理第10页 | 承接上一段所引“a living corpse”描述，转述del Monte早年生活、Caravaggio及Andrea Sacchi；随后叙述Vincenzo Giustiniani的父系背景、宅邸、收藏、对Caravaggio的支持和审美趣味。Haskell以模态语气比较Cambiaso与Caravaggio的用光，并推测一幅未具名Cupid画作体现Giustiniani与del Monte的共同兴趣。L103末句未完，续至L108–119。 | 新增34个候选、84条精确跨度提及、51条原书断言。关系候选包括patronage、household居住、雇用、委托获取、收藏持有、作品展示、作品作者及文献引证；均未升级为正式边。保留“first serious patron”“among”“may well have seemed”“only one to suggest”及“virtually unknown”等限定；不把未具名Cupid画作认作Caravaggio作品。 |

对照CHP-2.pdf印刷页29（物理第10页），确认OCR Frances!应读Francesi、proorictor应读proprietor、i960应读1960；S0来源与原书断言引句保留OCR原貌，校勘记在限定中。页内脚注1–4待接到sec_i:L143–146（规范段L124–157）。脚注5与书目行1081、996–997、266–268、462–463、1169建立暂定作者／年份映射；它们只是引证指针，不证明相关文章已读或支撑相关事实。书目条目后续仍须作为独立材料处理。

复用索引候选cand-0105、cand-1691、cand-0544、cand-0545、cand-2318、cand-0713、cand-0706、cand-1200、cand-1201、cand-1203、cand-1196、cand-0488、cand-2353、cand-1131、cand-3126、cand-3401及cand-3579中的适用项。St Peter's、S. Luigi dei Francesi和Genoa索引页码均未覆盖印刷页29，暂存候选映射供S3复核。Plate 17b前置图版说明将肖像主体映射到cand-3077，而本段使用索引候选cand-1200；不在S2合并。Italo Faldi候选与第一章未决cand-3516保持分开，等待S3身份判断。

本段完成后，全书为61段reviewed/complete、18段excluded、713段queued；候选4,336条、提及1,853条、原书断言1,069条。第2章为14段迁移、7段排除、47段queued。结构审计0错误；剩余警告与全书S2未完成状态保持不变。

## 已完成迁移：第 I 节 L108–119（2026-09-27）

| 规范段 | 印刷页／PDF页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---|---|---|
| `chp-2:02_CHP-2_sec_i:l108-119` | 30／物理第11页 | 承接L103对Vincenzo Giustiniani藏品与文字的比较，记录他对晚期十六世纪艺术变革的理解、其收藏对旧一代Mannerists与新改革者的取舍、1606年与Cristoforo Roncalli（Pomarancio）赴北欧之行，以及Haskell对其艺术文化的比较判断。随后转述Maffeo Barberini的家户、学术社交、Peiresc通信、宫殿绘画与委托；记Florentine雕塑家群及Pietro Bernini、Gian Lorenzo Bernini父子、St Sebastian委托和原置／留置地点；继而记录Paul V、Scipione Borghese与Ludovisi家族对Bernini创作的赞助、Maffeo的诗作和镜像轶事，以及Haskell对其未来计划的推测。 | 新增11个候选、67条精确跨度提及、41条原书断言。将未具名艺术家群与家族集体保留为独立候选；Maffeo和Vincenzo的宫殿分开；《Jacob and the Angel》只记录从Pomarancio处获得，不推定创作者；《St Sebastian》与圣人实体分开；跨章Bernini镜像轶事按原书叙述保留，并链接第一章对其仅具象征价值的限定。未写正式关系边。 |

全书S2关系候选复核（2026-10-10）：本段17条已有statement已回核并标记关系候选；Pietro Bernini成员关系端点校正为人物→未名雕塑家群。出行、共同访问/讨论、欢迎与居住、通信、委托/服务、群组装饰及作品原置/留置均保留来源限定，不生成正式关系边；逐项记录见[过程记录](../process/stages.md)。

印刷页30与`CHP-2.pdf`物理第11页已目视核对。OCR差异：L109 `Cavalière`→印本`Cavaliere`；L110、L115 `hi`→`in`；L117 `writhig`→`writing`。索引候选拼写`Passignani`与印本`Passignano`、索引异名`Pomerancio`与印本`Pomarancio`不在S2改写，留待S3对齐。来源正文与`original_quote`保留OCR原貌。脚注1–6对应`sec_i:l124-157` L147–152；上一段L95–106脚注1–4对应同段L143–146。Bernini举镜故事参照`chp-1:01_CHP-1_sec_ii:l129-135`（印刷页19）；第一章将其作为翻新轶事并指出象征价值，故本段记录不当作已证实事件。

本段迁移后全书为62段reviewed且迁移完成、18段excluded、712段queued；候选4,347条、提及1,920条、原书断言1,110条。第2章为15段迁移、7段有理由排除、46段queued；表审计0结构错误。

## 已完成迁移：第I节脚注 L124–157（2026-09-27）

按规范段`chp-2:02_CHP-2_sec_i:l124-157`逐注阅读，覆盖印刷页25–31（`CHP-2.pdf`物理第6–12页）。写入42个来源／实体候选（cand-4350–cand-4391）、81条精确跨度提及和57条原书断言；该段状态为`reviewed/complete`。此前旧摘要把该行段误映射为正文内容，本次已将结果表更正为脚注记录，旧读稿不再作该段覆盖依据。

脚注与正文锚点对应为：L126–131→`sec_i:l44-53`；L132–135→`sec_i:l55-69`；L136–139→`sec_i:l71-80`；L140–142→`sec_i:l82-93`；L143–146→`sec_i:l95-106`；L147–152→`sec_i:l108-119`；L153–157→`sec_ii:l3-8`。已将后六组相应脚注标记和书内来源说明交叉链接到对应脚注断言；脚注引述仍保留原发言者、转引层级及限定。脚注5的书目匹配继续作为待书目S2复核的定位，不当作事实证据。

PDF目视核对印刷页25–31，纠正S0识读用于限定记录：L127 `B.ellori`→`Bellori`；L132 `osa`→`of a`，并补录书信定位`Biblioteca Vaticana, Barb. Lat. 5820, cc.14 and 17`；L137 `c`→`e`；L143 `awiso`→`avviso`；L146 `Bellon`→`Bellori`；L148补记OCR遗漏的`Barb. Lat. 6502`；L151脚注标号印本为5（OCR为8）；L157 `Abbatc`→`Abbate`，完整定位为`Biblioteca Vaticana, Urb. Lat. 1100`，日期为1630年1月23日。L125为反向OCR图注残片，保留在复核范围内但不产生脚注语义。Maffeo来信身份和归属的“presumably”、Rubens在罗马是否临摹Titian作品的Walker判断、以及Mennemoli姓名疑读均按来源限定或留待S3，不外推为确定事实。

迁移后账本为全书63段reviewed/complete、19段excluded、710段queued；第2章16段迁移、8段有理由排除、44段queued；提及2,001条、断言1,167条。结构审计无错误。

## 已完成迁移：第II节 L42–50（2026-09-27）

| 规范段 | 印刷页／PDF页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---|---|---|
| `chp-2:02_CHP-2_sec_ii:l42-50` | 35／物理第16页 | Haskell先评述Bernini巴尔达基诺工程的视觉成功及其不遮挡大殿视线的效果，继而说明原拟以“复活的基督”雕像加冕、后改为十字架，并把意义转向基督受难。正文随后讨论扭柱与所称古代传统、Urban VIII及Barberini标志如何关联该建筑；再叙述造价、从Pantheon取青铜所引发的讽刺和抱怨，以及St Peter’s装饰委员会与1627年祭坛方案。第50行以“Bernini’s”未完句截断，下段才续述方案结果。 | 新增13个候选（cand-4392–cand-4404）、69条精确跨度提及和24条原书断言。候选包括未实施的Risen Christ方案与改为十字架的设计、扭柱、Solomon’s Temple、iconographic scheme、Barberini bee/sun/laurel标志、无名医生及其作的讽刺诗、计划中的祭坛、Spanish cause等；复用现有Bernini、Urban VIII、Jesus、St Peter、圣彼得大殿、委员会和Pantheon候选。正式关系未生成。保留“supposed”、Urban直接参与方案的“probably”、作者对政治与成本的叙述限定；脚注1–3待注释段处理。 |

对照`CHP-2.pdf`印刷页35（物理第16页）目视校读。S0 OCR将`200,000 scudi`误作`200,000 soldi`；另有`spécial`→`special`、`tire pillars`→`the pillars`以及脚注3标号误作问号等差异。来源转录和原书引句保持原样，校勘记录在断言限定和过程记录。L43 OCR将`toSt Peter`连写且印本对应标点有污损，语义不受影响。L50的未完Bernini句不与未读内容合并。脚注1–3定位到`sec_ii:l147-193`；引用暂作注释定位，不视为已处理的独立证据。

本段迁移后全书为64段reviewed/complete、19段excluded、709段queued；候选4,402、提及2,070、原书断言1,191。下一段按规范S0源序为`sec_ii:l52-60`。


## 当前新增迁移：第II节 L52–60、L62–69（2026-09-27）

| 规范段 | 印刷页／PDF页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---|---|---|
| `chp-2:02_CHP-2_sec_ii:l52-60` | 36／物理第17页 | 接续L50未完的“Bernini’s”：委员会接受Bernini方案，祭坛移至crypt，穹顶柱龛预留给四位圣人雕像；继续叙述相关雕塑家与圣人、阳台和圣物展示，Bernini的浮雕及Matilda墓，再转入Bernini—Urban VIII的整合装饰方案与Passeri讽刺引语。 | 新增29个候选、88条精确跨度提及和25条原书断言。旧段的“Bernini’s”已与本段方案获接受的断言交叉链接，并修订旧祭坛候选的细节；未具名雕塑家、未完全具名的四圣人、Matilda身份及墓葬浮雕均保持分开。Passeri引语在L60以“and”截断，待L63续接；脚注1–3待注释段迁移。 |
| `chp-2:02_CHP-2_sec_ii:l62-69` | 37／物理第18页 | L63续完Passeri对Bernini的讽刺引语；随后记录Urban VIII在世时Bernini的独占性地位、1623–1644年作品和委托格局、Scipione Borghese的两尊胸像、Charles I与Richelieu获准请求肖像，以及Nicholas Stone对Thomas Baker胸像和Van Dyck三人肖像传递事件的转述。段末转入Urban VIII交Bernini重建、装饰S. Bibiana，发现Saint遗体后重建教堂，以及Bernini所作圣人雕像和Haskell的审美判断。 | 新增13个候选（cand-4434–cand-4446）、78条精确跨度提及和15条原书断言。Scipione两尊胸像与Plate 5候选暂不合并；获准肖像只记许可，未据此断言已经完成；Stone引语保持Nicholas Stone→Haskell的层级，Cardinal Barberine身份待定。S. Bibiana建筑、重建工程、Saint遗体、圣人、雕像和High Altar分开；遗体候选类型未定。 |

印刷页36已核读：S0中`beplaced`、`butis`、`martyrdomofChrist`及L60引号残片按印本记录差异，原OCR引句不改。印刷页37已核读：`arcliitectural`校作印本`architectural`，`Tor`校作`For`；来源与断言引句保持S0原貌，校勘写入限定。L60 Passeri引语与L63续文已建立statement双向链接。两段脚注共1–5号均指向`sec_ii:l147-193`，仍待该注释段处理后交叉链接。

当前本章19段迁移完成、8段有理由排除、41段queued；全书S2为66段reviewed/complete、19段excluded、707段queued，含2,236条提及和1,231条原书断言。`audit_tables.py --summary`结构错误为0；全书语义处理尚未完成。下一段按规范S0源序为`chp-2:02_CHP-2_sec_ii:l71-78`。


## 已完成迁移：第II节 L71–78（2026-09-27）

| 规范段 | 印刷页／PDF页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_sec_ii:l71-78` | 38／物理第19页 | 记录Ciampelli受命绘制S. Bibiana圣人生平壁画、三个月后新画家获得左侧墙面，以及Pietro da Cortona被Marcello Sacchetti引见给Urban VIII。随后处理Sacchetti兄弟的父系、迁居罗马、宫殿／教堂礼拜堂／Ostia别墅与画廊、诗歌与社交联系；再记Marino的行程、作品和收藏、Marcello的绘画兴趣、Raphael《Galatea》复制品及其不明复制者；末尾记Pietro摹写Titian《圣家与圣凯瑟琳》的早期委托。 | 新增27个候选（cand-4447–cand-4473）、82条精确跨度提及和23条原书断言。将S. Bibiana壁画与三场景、原作《Galatea》与复制品、未具名复制者、Titian原作与Pietro的复制委托分别处理；不凭段落相邻把《Galatea》复制者认作Pietro。Marino收藏保持类型未定，Sacchetti父亲和社区成员边界保留未决。正式关系边未生成。 |

印刷页38（`CHP-2.pdf`物理第19页）已目视核对。L77末尾“which”续至下一规范段L80–89；本段不提前加入原作购藏信息。脚注1–4指向`sec_ii:l147-193`中的L172–175，待该注释段迁移后交叉链接。S0 L78将书目人名OCR作“Brigand”，印本确认为“Briganti”；原始S0和原书引句保持不改，校勘记入限定。

迁移后全书为67段reviewed/complete、19段excluded、706段queued；候选4,471、提及2,318、原书断言1,254。第2章20段迁移、8段排除、40段queued。`audit_tables.py --summary`结构错误为0；两条既有enrichment来源定位警告仍在。下一段按规范S0源序为`chp-2:02_CHP-2_sec_ii:l80-89`。


## 已完成迁移：第II节 L80–89（2026-09-27）

| 规范段 | 印刷页／PDF页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_sec_ii:l80-89` | 39／物理第20页 | 接续Titian《圣家与圣凯瑟琳》的购藏句，记录Cardinal Aldobrandini从Ferrara取得原作；随后记Marcello鼓励Pietro临摹Raphael与Titian及Haskell关于巴洛克绘画和艺术训练的解释，Pietro向赞助人询问题材、Marcello的文化性格及Haskell对Pietro、Domenichino和Annibale Carracci的风格比较。再登记为Sacchetti绘制的三幅大画、Sacchetti圈中的风格传播、Marcello委托装饰Castel Fusano乡间宅邸、Andrea Sacchi参与团队及各室装饰题材。后半记录Urban VIII即位后的Sacchetti职位变化、Giulio晋升枢机、Marcello的财务职务和Tolfa明矾矿特许权、矿区绘画委托、Marcello退居Naples并在那里去世、Sacchetti赞助影响的嵌套引语，最后回到S. Bibiana壁画。 | 新增16个候选（cand-4474–cand-4489）、63条精确跨度提及和35条原书断言。复用索引中Pietro的《Polyxena献祭》《酒神凯旋》候选，并为《萨宾妇人被劫》另建作品候选以免错合其他画家同题作。Castel Fusano乡间宅邸及其gallery可能对应L75的Sacchetti villa和gallery，标为待S3身份复核；区分建筑、装饰项目、礼拜堂、gallery和两组装饰题材。特许权、矿区及其绘画分别记录；匿名编年史作者与兄弟引语保留不同发言层级。Raphael原作与Pietro的Titian复制品经相邻源段交叉链接，原作不与复制品混淆。正式关系边未生成。 |

印刷页39（`CHP-2.pdf`物理第20页）已目视核对。S0 OCR `sables`校为印本`fables`；`ability 40 adapt`校为`ability to adapt`；Plate `ioa/rob/na/nb`校为`10a/10b/11a/11b`；`and.breadth`校为`and breadth`。原始S0与原书引句保持不改，差异只记入限定。L81购藏句承接L77在“which”处的未完句，两段statement已相互链接。脚注1–4现已分别链接至后置注释段`sec_ii:l147-193`的L176–179，并核对了正文与注释的双向链接；它们与p.38重复编号的L172–175区分。脚注2涉及Andrea Sacchi文献，尚不作外部事实核验。

本段语义复核新增1条Pietro受Marcello欢迎的原书断言及1条精确风格提及；补标既有明确关系断言后，本段共27条关系候选，5条因对象或角色端点未指明而保持开放。未生成S6正式关系边。`copying-as-training-generalization`的主体修正为泛指艺术家，清除误连Pietro的候选外键；跨段购藏句仍链接至前段，不把摹本当作原作。当前严格审计见全书结果记录；第2章后续段落及全书S2交接仍待完成。

迁移后全书为68段reviewed/complete、19段excluded、705段queued；候选4,487、提及2,381、原书断言1,289。第2章21段迁移、8段排除、39段queued。`audit_tables.py --summary`结构错误为0；两条既有enrichment来源定位警告仍在。下一段按规范S0源序为`chp-2:02_CHP-2_sec_ii:l91-104`。


## 已完成迁移：第II节 L91–104（2026-09-27）

| 规范段 | 印刷页／PDF页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_sec_ii:l91-104` | 40／物理第21页 | L91–94接续Pietro da Cortona在S. Bibiana的壁画与发展，记其success及加入Bernini成为Urban VIII的“special artist”；L95是节分隔符。L96起为第III节，记Urban VIII的性格、诗歌兴趣及语言、宗教诗歌主张、Castel Gandolfo别墅、委托侄子处理外交事务、Haskell对其治理与性格的评价、诗卷出版，以及Bernini制作的多尊教皇胸像和这些肖像的表现特征。 | 首轮迁移新增12个候选（cand-4490–cand-4501）、65条提及和23条原书断言；本轮语义拆分后为30条statement，撤销“his friends”误映射到诗歌候选的1条mention，现为64条mentions。Rome、Castel Gandolfo、别墅、附加其上的匿名中世纪城堡分开；诗歌作品与1631年诗卷分开；未具名侄子不猜身份；Bernini的多尊青铜/大理石胸像作为未细分作品组。跨章节候选身份留待S3；未生成正式关系。 |

L91–92补完前一规范段对Pietro壁画“grand manner”的句子，并与此前statement交叉链接。Haskell对Urban的性格、政治志向和Baroque/谄媚关系保留作者评价，不当作外部已证事实；“Baroque”宽泛文化类别不与前段较窄的Baroque painting候选合并。五条脚注已从`sec_ii:l147-193`的L180–184与正文双向链接；注1回链诗歌主题、别墅建造及别墅附着三条statement，注2–5各回链相应statement。L104末尾肖像描述在L119续接，已标待续，不以跨过的图版题注代填。印刷页40核实OCR`his.career`应为`his career`，L103前的短横线是扫描/OCR残迹；来源与原书引句均不改写。

迁移后全书为69段reviewed/complete、19段excluded、704段queued；候选4,499、提及2,446、原书断言1,312。结构审计错误为0；两条既有enrichment来源定位警告仍在。下一段按规范S0源序为`chp-2:02_CHP-2_sec_ii:l106-107`。

## 已完成迁移：第II节 Plate 7–8 题注 L109–116（2026-09-27）

| 规范段 | 印刷位置／PDF页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---|---|---|
| `chp-2:02_CHP-2_sec_ii:l109-113` | Plate 7／物理第24页 | 图版为Domenichino的《Hunt of Diana》。S0 OCR将题名与作者拆成反序行，扫描图版题注清晰显示“DOMENICHINO: Hunt of Diana”；L113独立的`D`不是题注内容。 | 复用人物`cand-3024`和作品`cand-4030`，新增2条提及、1条`caption_attribution`断言。该断言仅记录印刷图注归属，不作为独立作者鉴定；与书前图版目录及正文L71–80中同一作品候选复用。 |
| `chp-2:02_CHP-2_sec_ii:l115-116` | Plate 8／物理第25页 | 图注为“Matteo Castelli: Family chapel in S. Andrea della Valle”。书前图版清单将同一Plate 8称为Barberini Chapel；本段复用同一礼拜堂、Matteo Castelli和教堂候选，保留题注用语差异。 | 新增3条精确跨度提及、2条断言：图注将礼拜堂设计归于Castelli，并将该内部空间置于S. Andrea della Valle。没有将设计归属扩大到整个教堂或全部装饰，也未另建重复礼拜堂候选。 |

两页PDF均已目视核读。L109–113原始OCR及`original_quote`保留其断行和反序，印本顺序仅记入限定；L115–116的实体映射与Plate 8书前图版清单L48直接对应。新增段迁移后，全书为71段reviewed/complete、20段有理由排除、703段queued，候选4,499条、提及2,451条、原书断言1,315条；第2章为24段迁移、9段排除、37段queued。Plate 6正确题注及Plate 8分组题头的补录段仍在队列中，依源文件顺序须在主`sec_ii`文件读完后处理。`audit_tables.py --summary`结构错误为0；既有两条enrichment来源定位警告未变。下一段为`chp-2:02_CHP-2_sec_ii:l118-125`。

## 已完成迁移：第II节 L118–125（2026-09-27）

| 规范段 | 印刷页／PDF页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---|---|---|
| `chp-2:02_CHP-2_sec_ii:l118-125` | 41／物理第26页 | L119接续前段Urban VIII肖像外貌描述；随后记录教皇公共纪念物、Velletri青铜像、Roman Senate撤销1590年法令及委托大理石像、Urban VIII家族胸像、Carlo Barberini纪念牌和另一尊Capitol雕像。区分古代Julius Caesar躯干、Algardi改制、Bernini提供头部、Carlo所作《君主论》拉丁文提要及Haskell对纪念物的评价。L125记Urban VIII墓葬委托、预定位置、与其他教皇纪念物比较、Bernini受托、Angelo Giori监督与履历／艺术兴趣、Claude七幅未具名作品，以及墓葬初始工程、Paul III墓和跨页的Council of Trent。 | 新增18个候选（cand-4502–cand-4519）、69条精确跨度提及和29条原书断言。为青铜像、1590年法令、未确认是否完工的Capitol雕像、古代躯干、拉丁文提要、Urban VIII墓葬、利基及其他未具名对象保持独立候选；复用Plate 2b大理石像和既有Bernini、Carlo Barberini、Giori等候选。关系仍为S2原书断言候选，不生成正式边。 |

肖像续句与L103–104的statement已双向关联；句中对胸像心理表现的解释保留为Haskell的视觉判断。对照印刷页41记录OCR差异`pn`→`an`、`admireC`→`admirer`及`On`→`on`；不改写S0来源和`original_quote`。脚注1–6均登记指向`sec_ii:l147-193`，具体注释迁入后再逐条交叉链接。未把预定工程表述为已完工；保留雕像执行状态、亲属姓名和未具名画作的未决状态。迁移后全书为72段reviewed/complete、20段excluded、702段queued；候选4,517、提及2,520、原书断言1,344。第2章为25段迁移、9段排除、36段queued。表审计0 errors；两条既有enrichment来源定位警告仍在。下一段按S0源序为`chp-2:02_CHP-2_sec_ii:l127-139`。


## 已完成迁移：第II节 L127–139（2026-09-27）

| 规范段 | 印刷页／PDF页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_sec_ii:l127-139` | 42／物理第27页 | 在首轮迁移上对照印本复核：Paul III墓移入后殿左侧壁龛；Urban VIII墓像、1639复工、两次停工、1644完工尝试及1647年Justice完成；转入嘉布遣会教堂/修院工程、请愿和王族装饰争议。Antonio修会身份、性格评价和枢机身份拆开；教堂与修院邻接Ludovisi庄园分别建statement； Urban VIII对Bernini的其他委托与墓葬停工分开。L139注1作者尾段连回L191；Council跨页及L138动机续句链接保留。 | 复用cand-4520–cand-4536，不新增候选；62条mention（含Europe与Rome两个经偏移核验的定位），34条statement（首轮27条上新增7条）。26条关系候选，23条具两端点，3条对象未具名（泛称欧洲人物、Peretti计划对象、外国王族）；区分Antonio—Capuchins成员关系、Urban—Bernini委托、Urban撤回许可、家族流亡与Haskell评价。未生成正式关系。 |

2026-10-08语义复核确认：L134行首句点及L137行首短横线不见于印本；L137印本为`in-Roman`，原S0和`original_quote`继续保留OCR形式。`There for eight years`指向前段墓龛，现作双向statement链接而非误作关系端点；“Urban VIII overwhelmed Bernini”独立为Urban—Bernini关系候选。另拆出二次停工、Barberini被逐出Rome、Antonio身份/性格/枢机身份、Capuchin请愿与教皇撤回许可，并补充修院位置边。脚注1中L139的P. Domenico da Isnello与L191引文及研究归属statement互链；Council of Trent真实跨页句与L138→L142纹章动机续句保持双向连接。严格审计：34条statement、62条mention、26条关系候选（23端点齐全、3开放），无新增实体或S6正式边。

## 第II节 L141–145（首轮迁移及2026-10-08语义复核）

| 规范段 | 印刷页／PDF页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_sec_ii:l141-145` | 43／物理第28页 | 复核L142承接p.42纹章动机并记录装饰责任/木制礼拜堂方案；L143记录Cardinal S. Onofrio订制烛台与十字架、Capuchin退还、Urban坚持接收烛台及高坛争议、铜制圣体龛和金属枝形烛台方案、特许例外、材料妥协与Capuchin再次申诉；L144–145记录Pope/Antonio委托祭坛画、Reni作品、其他艺术家贡献及Ciarpi师承、Barberini侄辈参与。 | 沿用首轮9个候选（cand-4537–cand-4545）、38条mention；24条首轮statement复核为29条。25条S2关系候选，24条端点齐全、1条共同祭坛画委托的具体作品对象未明。分别记录木烛台/十字架退还、五名艺术家对未具名作品组的贡献及作品/教堂装饰关系，不把群组陈述伪装成逐件归属。Reni作品评价与L192 Malvasia注1双向互链；未生成正式关系。 |

印刷页43已目视核对：`pietrefine`印为`pietre fine`，L145末尾OCR单引号不见于印本，L144脚注1为`time`后的上标；S0和`original_quote`保留OCR形式。2026-10-08复核将首轮24条statement细化为29条、复用9个候选和38条mention；补标25条关系候选，24条端点齐全，1条共同委托的作品端点未明。将两组木制陈设的退还和五位艺术家对未具名作品组的贡献分别记录，不推定逐件归属。L192的Malvasia引用现与Reni作品评价双向互链。严格审计：全书12,300条statement、27,398条mention、2,512条关系候选（2,491端点齐全、21开放），`s2_missing=[]`、`errors=[]`。下一源段按顺序为已迁移的注释`sec_ii:l147-193`，需继续复核注释断言与关系覆盖。


## 已完成迁移：第II节 L147–193、视觉转录及第IV节标题核对（2026-09-27）

| 规范段 | 印刷页／PDF物理页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---|---|---|
| `chp-2:02_CHP-2_sec_ii:l147-193` | 32–40／13–21；41–43／26–28 | 完整处理本节脚注。保存Barozzi、Pastor、Passeri、Wittkower、Pollak等书目定位及ibid.链；区分直接引文、原书作者的转述、评价、冲突判断和内部交叉引用。记录Forge of Vulcan、未确认完成的挂毯与罗马防御寓意；Haskell对Ginnasi与Pastor说法的质疑；Fraschetti所引1633 avviso及Bernini制作Borghese大理石头像、报酬金额；Jan Niceo Eritreo对Marcello传记的归属；Urban VIII占星研究、Campanella协助及其在巴黎遭监视的转述，并把“监视与占星有关”限定为Haskell推论。L190保留Claude两幅Seaports分别涉及National Gallery和Louvre，但不将匿名画作逐一配馆。L191与L139的P. Domenico da Isnello尾注合并。L193书目指针前向链接到第IV节开头L3。 | 新增44个候选、88条精确跨度提及和80条原书断言；另为L190馆藏语境新增`cand-4590`，与仅作摄影来源的National Gallery候选分开。L171印本脚注标记5校正OCR 6；L190印本标记6校正OCR 0。PDF核对OCR错误：`tire`/`This`、`pietre fine`、`Vita di G. M. Bottalla`、`Briganti`、`Passeri`、`Gallery`、`complete`、`in Paris`及`pp.205 ff.`。印刷页41–43对应PDF物理页26–28；对应关系已反映到断言定位。引用来源作为引文入口，不表示已独立阅读或验证被引文献。 |
| `chp-2:02_CHP-2_sec_ii_visual-transcription:l1-3` | Plate 6／物理页23 | 目视转录Plate 6拉丁题字及Guglielmo Baur英文图注。图版目录已给出同题作品候选，故仅复用既有作品、画家和Villa Borghese候选；不把标题中的1630另写成独立制作年份。 | 新增4条提及及1条`caption_attribution`断言；无新实体候选。 |
| `chp-2:02_CHP-2_sec_ii_visual-transcription:l5-6` | Plate 8／物理页25 | 记录“BARBERINI PATRONAGE”分组题头与Plate 8、9、12、13的导航指针。 | 作为编辑编排信息完成处理；不建主题/层级实体，覆盖理由标记`no_semantic_content`。 |
| `chp-2:02_CHP-2_sec_ii_visual-transcription:l8-9` | 印刷页38／物理页19 | 视觉转录脚注4的本节书目续句。主S0段L78已有同一语句，但OCR把“Briganti”识为“Brigand”；视觉层保留印本拼写并与既有书目提及和脚注语句交叉链接。 | 复用已有Mostra di Pietro da Cortona与Briganti候选，新增2条提及及2条引文定位断言；不重复建书目对象。 |
| `chp-2:02_CHP-2_sec_iv:l1-1` | — | 仅为生成的`# 02 CHP-2 sec iv` Markdown标题，不是原书文本。脚注L193对应的开篇正文实际始于L3。 | 有理由排除。已修正脚注statement目标到`sec_iv:l3-4`。 |

当前全书账本为78段reviewed/complete、21段有理由排除、696段queued；候选4,588、提及2,712、原书断言1,478。第2章71段中31段完成迁移、10段排除、30段queued。结构审计0 errors；两条既有enrichment定位警告未变。下一段按源序为`chp-2:02_CHP-2_sec_iv:l3-4`。

## 已完成迁移：第IV节 L19–29（2026-09-27）

| 规范段 | 印刷页／PDF物理页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| chp-2:02_CHP-2_sec_iv:l19-29 | 45／30 | 接续L17未完的委员会名单与函件，记录del Monte为Vouet和Sacchi取得委托、Francesco加入委员会、Lanfranco申请Christ in the Boat画作的初步提议、Ginnasi对Guido Reni与主画作的安排、Reni来罗马后因其认为委员会控制屈辱而离开，以及Francesco提出并获采纳的两项改派。随后记录三位年轻画家在St Peter’s的首次重要亮相、对Capuchin church引入两位画家的预期、Francesco收藏的Samson与Death of Germanicus，以及为Capture of Jerusalem寻求第二版本和约十二年的相对年代。 |
| 迁移计数 | — | 新增7个候选（cand-4606–cand-4612）、68条提及和26条断言。主画、较小画和Lanfranco初议分别保留，未推断为同一委托；提议、获采纳和作品完成状态分开。Reni的屈辱判断归于其本人，离开原因保留“部分”；三位画家的群组成员按上下文推断并标待S3核对；Capuchin church暂按章内语境映射S. Maria della Concezione，仍待核对。Samson按作品候选记录，不与圣经人物混同；第二版本使用索引候选并链接前段来源候选。印刷页45核实OCR ferusalem应为Jerusalem；原S0和original_quote保持不改。 | 脚注1–6分别指向注释段L195–200，待该注释段迁移后回链。L17委员会列表续于L20；L29句末“Once again”续于L31。 |

本段完成后，全书为81段reviewed/complete、21段有理由排除、693段queued；候选4,610、提及2,877、原书断言1,551。第2章为34段迁移、10段排除、27段queued。表审计0结构错误，相关测试11项通过；两条既有enrichment来源定位警告不变。下一段按S0源序为sec_iv:l31-43。以上计数为机械状态，不代表全书语义质量已独立验收。

## 已完成迁移：第IV节 L31–43（2026-09-27）

- 逐行处理规范段`chp-2:02_CHP-2_sec_iv:l31-43`，核对印刷页46（`CHP-2.pdf`物理第31页）。记录Francesco把Poussin第二版《耶路撒冷陷落》转赠外国显贵、其审美倾向与Cassiano dal Pozzo的对照、Vouet与Valentin受Caravaggio影响及在Francesco patronage下采用较华丽的Baroque风格、Sacchi转向Raphael和Roman classicism、Vouet的事业与“grand manner”、Barberini圈对罗马艺术的影响，以及Sforza宫殿购买和转赠Taddeo的叙述。作者评价与宽泛因果判断保留为Haskell的说法。
- 页内续注L39–43是第45页脚注6的跨页延续，记录Poussin的两幅圣徒风景画、Blunt关于《四福音书》组画的假说、Spoleto圣母画对Francesco的可能委托，以及Poussin 1642年致Cassiano的信与温莎《Scipio and the pirates》素描间的可能关系。脚注6续文回链到前段L25的脚注标记；印刷页46脚注1–4的完整注释另收在规范脚注段L201–204，未在本段重复登记，后续处理该注释段时回链。
- 新增24个候选（cand-4613–cand-4636）、82条跨度提及和21条原书断言。未具名外国显贵、两幅不同风景画、未定名Scipio设计与温莎素描分别保留；柏林与芝加哥按原注以配对地点记录，未强行逐幅配馆。Sforza宫殿暂与既有Barberini palace候选分开，留待S3处理身份关系。
- PDF核对确认L35 `Plate i`应读作“Plate 1”，`represented rather , an awkward`应为“represented rather an awkward”；L38前的`- v -`是分隔符，正文从“Taddeo”开始。保留S0 OCR和`original_quote`不改。Taddeo的“lacked the”在L38截断，已指向下一段L45–52，暂不补写未读续文。
- 写入后`audit_tables.py --summary`为0结构错误；82段reviewed/complete、21段excluded、692段queued；候选4,634、提及2,959、原书断言1,572。第2章为35段迁移、10段有理由排除、26段queued。两条既有enrichment来源定位警告未变。下一段按S0源序为`chp-2:02_CHP-2_sec_iv:l45-52`。机械检查不代表全书语义验收。

## 已完成迁移：第IV节 L45–52（2026-09-27）

| 规范段 | 印刷页／PDF物理页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_sec_iv:l45-52` | 47／32 | 接续Taddeo性格与能力的跨页句；记录Urban VIII即位时Taddeo年龄及同时代对其“all sugar, all honey”的描述、街头斗殴与杀人事件、宽泛措辞的教皇赦免、Taddeo的婚姻和军职、Palestrina领地购买、Prefect of Rome头衔、礼仪优先权争议与公众角色。L51重述Francesco在1626年将Sforza宫殿交给Taddeo，并记家族其后出售Valmontone产业；L52记录Barberini新建更大宫殿、部分纳入旧结构的计划，以及Taddeo继续购地、接洽Maderno。句末建筑样式判断仍续至L54–63。 | 新增13个候选（cand-4637–cand-4649）、68条精确跨度提及、26条原书断言。未具名Colonna女儿与Taddeo之父保留为待识别人物；斗殴与杀人保留为可能分开的事件，赦免作为未具名文书候选；外邦使馆作范围未定的集体。Colonna、Della Rovere、Sforza家族与个人和房产分列。Prefecture of Rome和Papal armies暂列institution候选。旧Sforza宫殿与Barberini新宫殿分开，Maderno与较可能的匿名合作者保留为设计归属选项。 |

印刷页47／PDF物理页32确认OCR `lais character`应读`his character`、`onlyTestored S. Bibiana`应读`only restored S. Bibiana`；S0文本及断言`original_quote`均保持原样。页码标签L45仅作导航。正文脚注1–5链接到注释L205–209，待注释段统一迁入后回链；PDF确认注释L209的印本标号为5，OCR标为6。L38的“He lacked the”与本段L46–47互链；L52段末未完句链接到下一规范段L54–63。1625年购入旧宫殿与1626年转交Taddeo作为不同事件。

迁移后全书为83段reviewed/complete、21段有理由排除、691段queued；候选4,647、提及3,027、原书断言1,598。第2章为36段迁移、10段排除、25段queued。`audit_tables.py --summary`结构审计0错误，相关测试17项通过；两条既有enrichment来源定位警告未变。下一段为`chp-2:02_CHP-2_sec_iv:l54-63`。机械检查不代表全书语义验收。

## 已完成迁移：第IV节 L54–63（2026-09-27）

| 规范段 | 印刷页／PDF物理页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_sec_iv:l54-63` | 48／33 | 接续前段建筑设计归属的未完句，记录Barberini宫殿立面、前庭、拱廊与乡间别墅式特征、规模及作者关于家族权势的解释；记录Bernini接替Maderno、Borromini参与少量改动、1633年“几乎完成”的状态；Taddeo的艺术兴趣、Bentivoglio家族源流、Ferrara于1598年归入Papacy、Ippolito支持Cesare d’Este继承主张、Guido与Enzo的教会和外交经历、Van Dyck肖像及Haskell的评价。保留各自身份、行动关系、时间限定、转述层级和作者判断。 |
| 迁移计数 | — | 新增7个候选（cand-4650–cand-4656）、62条精确跨度提及和30条原书断言。Church与Papacy分开；两处未具名Pope分别保留，不猜定为Urban VIII或Clement VIII；Ippolito索引拼写异文保留；Guido未具名历史著作不虚构书目实体。L63生活方式句续至下一规范段L65–77。印本图像确认OCR `Use`应为`life`，仅记校勘、不改写S0或`original_quote`。脚注1–4映射注释L210–213，待该段迁移后回链。 |

本段完成后，全书84段reviewed/complete、21段有理由排除、690段queued；候选4,654、提及3,089、原书断言1,628。第2章为37段迁移、10段排除、24段queued。`audit_tables.py --summary`结构错误0，相关测试17项通过；既有两条enrichment来源定位警告不变。下一规范段为`chp-2:02_CHP-2_sec_iv:l65-77`。结构通过不表示全书语义验收完成。


## 已完成迁移：第IV节 L91–94（2026-09-27）

| 规范段 | 印刷页／PDF页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_sec_iv:l91-94` | 51／物理第36页 | L91为页眉与页码导航；L92补完《Divine Wisdom》中心女性形象的跨页句，记录太阳的双重象征、Barberini蜂与月桂标记、中心壁画的装饰friezes及拟人化智慧主题。L93记录壁画接受、Antonio的拥护、新principal reception-room/great hall对Camassei与Cortona的规划变化，以及Bracciolini的家族赞颂方案。L94记录Barberini家族处于鼎盛、Bracciolini方案由Cortona执行，并记其早年服务Maffeo及句末旅行续文。 | 新增18个候选（cand-4675–cand-4692）、78条精确跨度提及、36条原书断言。拟人化概念归term；Sun、bees、laurel跨作品候选暂不合并；Sacchi房间与新great hall分开；未名Jesuit advisers、chapel和Camassei小房间组保持来源边界。Haskell的评价保留发言者限定；未生成正式关系。 |

L92脚注1、L93脚注2分别映射到规范注释段`chp-2:02_CHP-2_sec_iv:l190-245`的L225、L226，待注释段迁移后回链。L89的Wisdom女性形象句已与本段识别Sun的statement互链；L94末句在“to”处未完，继续到下一段L96–104。PDF页图核实`usedas`→`used as`及`impheations`→`implications`；`and-also`按句法读作`and also`，但不改S0或`original_quote`。

准备本段时回检L79–89，发现作品《Divine Wisdom》的2条提及及10条断言误连艺术家索引候选`cand-2320`；已更正为作品候选`cand-4003`。该候选映射不等于全局S3身份对齐。

迁移后全书87段reviewed/complete、21段有理由排除、687段queued；候选4,690、提及3,286、原书断言1,717。第2章为40段迁移、10段排除、21段queued。下一段按S0源序为`chp-2:02_CHP-2_sec_iv:l96-104`。

## 已完成迁移：第 IV 节 L96–104（2026-09-27）

| 规范段 | 印刷页／PDF物理页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_sec_iv:l96-104` | 52／37 | L96是页码导航；L97补完Bracciolini随Maffeo赴巴黎的句子，随后叙述Bracciolini在Clement VIII去世后离开Maffeo、1623年后悔并向Barberini求情，以及出版《L’elettione di Urbano VIII》后所得荣誉。L99转入其后续诗作、Antonio Barberini兄弟的任职、Bracciolini在Sinigaglia的处境和返回罗马；同段记其与Cortona规划Barberini大厅天顶装饰。L99–102描述Cortona壁画中的家族徽记、天意与诸美德、拟人寓意及其政治阐释，并评价其作为巴洛克天顶装饰的构图与观者效果。L103–104为页52脚注2续文，回述Montagu所汇集的不同图像解释及Vitzthum书目线索。 |
| 迁移计数 | — | 新增36个开放候选（cand-4693–cand-4728）、94条精确跨度提及和34条原书断言。分别记录Bracciolini早年离开、后来的求情信与抱怨信；巴黎目的地由本段补全前段续句。区分年长Capuchin Antonio与年轻枢机Antonio；将Cortona天顶壁画、寓意人物、作品中的蜂与月桂徽记分开。Haskell转述的政治阐释与Montagu、Rosichino、Teti及匿名观察者的解释保留各自归属和不确定语气。Hercules作为图像人物保留未定类型，不并入历史人物。L228注释头部尚未迁移，暂不创建Montagu文章候选；本段只复用Jennifer Montagu人物候选。未生成正式关系边。 |

脚注1回链至规范注释段L227；脚注2回链至L228，当前段只含其续文，L228头部仍queued。页图核对`CHP-2.pdf`印刷页52（物理页37）：OCR `suture Pope`应为`future Pope`、`tire Fates`应为`the Fates`、`seventeenthcentury`在印本为`seventeenth-century`，L104页码范围后的OCR连字符在印本为句点。原S0与断言引句不改，校勘写入限定。L101–102关于巨人冲突的句子继续至L106–107；前段L94末尾的旅行续句已在本段L97以Paris完成。写入后全书账本为88段reviewed/complete、21段excluded、686段queued；候选4,726、提及3,380、原书断言1,751。审计0结构错误，相关测试17项通过；两条既有enrichment来源定位警告未变。下一段按S0源序为`chp-2:02_CHP-2_sec_iv:l106-112`。

## 已完成迁移：第 IV 节 L106–112（2026-09-27）

| 规范段 | 印刷页／PDF物理页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_sec_iv:l106-112` | 53／38 | L106是页码导航；L107完成上一段描写观者卷入教皇与邪恶力量冲突的壁画效果。L108–109称此类复杂题材在十七世纪教皇赞助中较新，并对照Borghese与Ludovisi较一般的历史／神话题材；随后比较Cortona与Sacchi天顶画的文学兴趣、Cortona的展示效果及其对后世宫廷画家的影响。L109–111称Cortona与Bracciolini的方案把王侯颂扬推得更远，并以“very likely”推测Cardinal Francesco受Rubens周期影响；Domenichino的意见明确是转述的传闻。L112转记Francesco雇用Romanelli、其装饰工作、Barberini挂毯工场、在Accademia di S. Luca的任职及学院教堂重建。 |
| 迁移计数 | — | 新增8个开放候选（cand-4729–cand-4736）、50条精确跨度提及和22条原书断言。分开Borghese家族、Urban VIII时期教廷宫廷、Renaissance humanists与后世court painters群体；另将Rubens周期、Barberini挂毯工场、学院教堂和Cortona的文学／展示综合分别建候选。Romanelli与Cortona的师徒关系及Barberini雇用和学院任职均保留为原书断言，未建正式关系边。教堂的具体身份和挂毯works的组织性质留待对齐；注释书目不提前建实体。 |

PDF印刷页53（物理页38）核对了L107跨页续句、专名和脚注标号。脚注1、2、3分别回链至后置注释段L229、L230、L231；这些注释仍queued。已更新前段巨人冲突statement，记录其由L107续完。全书账本为89段reviewed/complete、21段excluded、685段queued；候选4,734、提及3,430、原书断言1,773。审计0结构错误，相关测试17项通过；两条既有enrichment来源定位警告未变。下一段按S0源序为`chp-2:02_CHP-2_sec_iv:l114-125`。


## 已完成迁移：第 IV 节 L114–125（2026-09-27）

| 规范段 | 印刷页／PDF物理页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_sec_iv:l114-125` | 54／39 | L114为页码导航，L115为节标题；L116概括性判断气质与审美趣味的关系复杂且神秘。L117叙述Cardinal Francesco对Cortona与Romanelli的偏好、Sacchi对Raphael的敬畏及其依赖Antonio支持；随后记录Antonio的任命、Haskell对其资格的尖锐评价、职务收入比较及其野心受Francesco和Urban VIII阻挠。L119转述Antonio的外貌、风度及其对学习与艺术的兴趣；L119–122将1631年乌尔比诺继承背景、Urban VIII的领土主张、Francesco Maria della Rovere之死、Taddeo所继承的Prefect of Rome头衔和Antonio成为首任Legate分开记录。L123–124记Antonio希望从乌尔比诺绘画中扩充收藏、私人财物遗赠Vittoria、提香与Raphael作品已运往Florence；不猜作品题名或匿名Grand Duke身份。L125记录Studiolo肖像作者与送往Rome的叙述，并保留教皇“特别措施”句的未完状态。 |
| 迁移计数 | — | 新增16个开放候选（cand-4737–cand-4752）、62条精确跨度提及和30条原书断言。分开乌尔比诺城市与政治领土、Antonio的个人收藏与公爵绘画集合、作品群与建筑空间；Cardinal Borghese/Ludovisi和Grand Duke只按来源现有信息保留身份待决。Haskell的评价、集体反应和政策动机均保留作者归属，不据此建立正式关系边。 |

PDF印刷页54（`CHP-2.pdf`物理第39页）已核对正文、跨页句和脚注标号。脚注1指向注释段L232，脚注2、3指向L233，均待注释段迁移后回链。L125末句在“a special”处未完，续至规范段`chp-2:02_CHP-2_sec_iv:l127-137`。覆盖行已标为`reviewed/complete`、来源范围L116–125。迁移后全书S2为90段reviewed/complete、21段excluded、684段queued；候选4,750、提及3,492、原书断言1,803。`audit_tables.py --summary`结构错误0，相关审计与导出测试17项通过；两条既有enrichment来源定位警告不变。下一段按规范S0源序为`chp-2:02_CHP-2_sec_iv:l127-137`。机械检查不替代全书语义范围复核。
## 已完成迁移：第 IV 节 L139–152（2026-09-27）

| 规范段 | 印刷页／PDF页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---|---|---|
| chp-2:02_CHP-2_sec_iv:l139-152 | 56／41 | L140补完前段比武叙述并记Sacchi绘画；L141记Bentivoglio书籍插图。L142–143呈现Haskell对Barberini复兴罗马骑士传统、Taddeo任Prefect及Palestrina权利的解释和社会批评。L144–148转向1642年宫殿图册、绘画、天顶、古物、Cardinal Francesco图书室、剧场及1632年歌剧演出。L149–152为脚注2续文，含馆藏目录、旅行记录、1935年销售目录与资料致谢。 | 新增23个候选（cand-4770–cand-4792）、58条提及、19条断言。古物集合和未名画作群保留类型待决；Taddeo婚姻对象不从上下文推定；无正式关系边。 |

L137比武句续于L140；L148的Bouchard句续至L172。页56脚注1/2/3指向L237/L238/L239，脚注2续文L149–152已处理。页图OCR校正、覆盖范围及结构检查见过程记录。全书现为92段完成、21段排除、682段queued；下一段按S0顺序为chp-2:02_CHP-2_sec_iv:l154-155。

## 已完成迁移：第 IV 节脚注 L190–245（2026-09-27）

| 规范段 | 印刷页／PDF物理页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_sec_iv:l190-245` | 44–58／29–47 | 迁移第IV节正文后的脚注1–8：涵盖作品流传与失佚、作品位置、委托与宫殿历史、艺术家和赞助人叙述、图像解释争议、演出日期异说及Poussin作品年代讨论。区分Haskell的陈述、其所引文献及脚注作者的判断；引文定位不充当事实证明。 | 新增76个开放候选、148条精确跨度提及、107条原书断言（含引文定位）。52处脚注与正文断言交叉关联；未新增正式关系边。类型未定的Rospigliosi-Pallavicini collection保留为待决对象，作品组及未详书目不强行拆分或补全。 |

PDF核对保留了原S0 OCR：印刷脚注号与OCR不同处记入校勘限定；L208的`Giuho Pisano`不强行识别为人物；印本脚注1在OCR之后的Tassi、Gentileschi及宫殿所有权续文，L228 Montagu页码与Vitzthum续引，以及L242 Bellori关于《Rest on the Flight into Egypt》的续引，均作为可见印本证据单独标注，不伪装成S0 OCR原句。L243所述两件画作仍不与正文中的两幅素描合并。覆盖记为`reviewed/complete`，源行L191–245。全书S2为99段reviewed/complete、22段excluded、674段queued；第2章为52/11/8。`audit_tables.py --summary`结构错误0，仍有两条既存enrichment来源定位警告。下一段按规范源序为`chp-2:02_CHP-2_sec_vii:l3-3`。

## 已完成迁移：第 VII 节 L3–3、L5–19（2026-09-27）

| 规范段 | 印刷页／PDF物理页 | 句意与语义判断 | 提及、断言与关系线索 |
|---|---:|---|---|
| `chp-2:02_CHP-2_sec_vii:l3-3`、`l5-19` | 58–59／47–48 | L3记录1641年卡斯特罗战争爆发及Haskell对争端后果的评价；句末“of great”跨页接至L6的“importance”。L6–7记Barberini二十年统治引发的敌意、罗马危机、1644年屈辱和约与Urban VIII去世。L8–10记Pamfili当选、两位身份未指明的Barberini枢机支持Giulio Sacchetti未果、流亡与财产没收；L11–15分别处理流亡对艺术家的影响、Romanelli书信、Bernini及其对手、Barberini流亡中的影响力和挂毯制作。L16–19记Francesco回归、Antonio于1653年抵达后兄弟委托Cortona绘制Xenophon题材、剧场重开及 patronage 句的跨段未完片段。 | 新增11个候选（cand-4904–cand-4914）、81条跨度提及和22条原书断言。选举中的两位枢机作为身份未定的群体候选；1653年段落的“兄弟／枢机”依据近邻语境映射为Francesco与Antonio群体。Romanelli引文与Haskell叙述分层；作者评价和动机均保留归属，未生成正式关系边。 |

PDF印刷页59（物理第48页）核对确认OCR的`GiuEo`、`sailed`、`164.5`分别对应印本`Giulio`、`failed`、`1645`；`promote.the`中的印刷小标记按词间空格读取。原S0 OCR未改写，差异写入断言限定。L3与L6的跨页评价成对链接；脚注标记1–6分别指向仍queued的注释段L38–54，待该段迁移后回链。覆盖现为reviewed/complete（L3–3与L6–19）。迁移后全书S2为101段完成、22段排除、672段queued；第2章为54/11/6，候选4,912、提及3,957、原书断言2,037。表审计结构错误0；8,083个候选引用中无缺失或指向excluded的引用。两条既有enrichment来源定位警告仍在。下一规范源段为`chp-2:02_CHP-2_sec_vii:l21-30`。

## 已完成迁移：第VII节 L21–30（2026-09-27）

- 核读规范段chp-2:02_CHP-2_sec_vii:l21-30，核对印刷页60（CHP-2.pdf物理第49页）。迁移22个新候选、86条提及、24条原书断言；此前已登记的正文实体复用原候选。
- 保留Antonio对Sacchi的忠诚方向、Sacchi拒绝未执行壁画委托、Maratta接续《使徒》系列及多幅肖像与单幅版本的区分、Francesco可能委托Velasquez肖像的疑问，以及Romanelli画作与Titian同名画作的分离。将Urban VIII挂毯组与其草图、cartoons分开；L30无编号图注只说明Northumberland版本与前述肖像不同，版本身份仍待S3核对。
- 印本核校fellow-painters、his、life、The Marriage of Peleus和It；保留S0 OCR及原断言引文不改写，差异写入校读限定。承接L5–19的赞助叙述已回链；挂毯工期句在本段仍以“mainly”截断，待L32–36续接。脚注1–7待L38–54迁移后回链。
- 覆盖已更新为reviewed/complete，来源范围L22–30。全书S2为102段完成、22段排除、671段queued；候选4,934、提及4,043、原书断言2,061。结构审计0错误，两条既有enrichment来源定位警告未变。下一规范段为chp-2:02_CHP-2_sec_vii:l32-36。

## 已完成迁移：第VII节 L32–36（2026-09-27）

- 核读规范段chp-2:02_CHP-2_sec_vii:l32-36，核对印刷页61（CHP-2.pdf物理第50页）。新增5个候选、31条提及、13条原书断言。
- L33补全上一段挂毯工期续句：超过二十年的主要原因是Francesco坚持只使用自家羊群的羊毛，前段续文已标记完成。分别保存挂毯组对Urban VIII的最后一次纪念、Urban VIII对Baroque风格的推动、作者对委托象征意义的解释，以及Francesco的艺术活动、图书馆与通信、Bernini获得Barberini赞助和Maffeo为Taddeo之子等断言。把Haskell的文化判断与艺术史评价保留为作者观点。
- 纸本页确认脚注标记1–3分别指向后置注释L51、L52、L53，均待L38–54迁移后回链。纸本L51可见“MSS. Barb. Lat. 6463”；规范OCR漏掉该定位，暂不改S0，待注释段迁移时记录校勘。
- 覆盖更新为reviewed/complete（正文范围L33–36）。全书S2为103段完成、22段排除、670段queued；候选4,939、提及4,074、原书断言2,074。结构审计0错误，两条既有enrichment来源定位警告未变。下一规范段为chp-2:02_CHP-2_sec_vii:l38-54。

## 后置注释与第VIII节收尾迁移（2026-09-27）

规范段`chp-2:02_CHP-2_sec_vii:l38-54`已核读印刷页59–61（PDF物理页48–50），新增22个来源衍生候选、52条提及和22条原书断言；按页码区分17处脚注，回链至第VII节L21–30、L32–36中的正文注号。记录了印本与OCR差异：p59脚注号6/8差异，p60的Mezzetti/Mozzetti、Blunt and Cooke (1960)/i960，p61的Biblioteca Vaticana定位漏识及`S. Carlo alle`/`aile`。原始S0 OCR和original_quote均保留。

规范段`chp-2:02_CHP-2_sec_viii:l1-1`是自动生成的分节标题，不属于原书正文，按版面导航排除，不建提及或断言。`l3-7`核对印刷页61（物理页50），新增31条提及、15条断言；脚注号4回链至前置注释L54，接通“remarkable width of culture”的跨段句。校正印本artists及多余引号位置，保留S0。

规范段`chp-2:02_CHP-2_sec_viii:l9-14`核对印刷页62（物理页51），新增10个候选、30条提及、20条断言。迁移Bernini—Barberini文化赞助语境、宗教图像与幻觉主义、Cortona天顶画的作者评价、两组明确赞助关系及Urban VIII去世带来的叙述转折；未具名法国国王、学者/画家群体，以及“both men”等指代均按待决或语境状态记录，Borghese候选保持身份未决。三段完成后第2章覆盖为59段reviewed/complete、12段有理由排除、0段queued；全书为106/23/666，候选4,971、提及4,187、原书断言2,131。`audit_tables.py --summary`结构错误0；仍有两条既存enrichment来源定位警告。第2章整章OCR差异核对和未决项收口仍待完成。

## 第2章整章OCR差异收口与图版转录补齐（2026-09-27）

将976行`02_CHP-2.md`与规范分节来源逐段对照，并人工复核低重叠行及规范源独有残段。页眉、页码和标题导航归为版面信息；`sec_i:l125`是混入后置脚注段的Plate 2反向OCR残片，已排除且不覆盖脚注L126–157；整章副本L591断行的`Caravaggio`对应规范来源的完整正文；L856脚注对应规范`sec_iv:l240`；L959书影可见的`MSS. Barb. Lat. 6463`校正已记录于`sec_vii:l38-54`的覆盖和校勘过程。

PDF核验补齐先前分节S0遗漏的三组图版文本：

- Plate III：物理第4页两幅肖像的Leoni／Cardinal Francesco Barberini与Maratta／Cardinal Antonio Barberini题注；新增独立转录段，复用书前目录相同肖像候选，新增6条提及和4条图注断言。
- Plate 5：物理第22页组题“Cardinal Scipione Borghese and his patronage（see Plates 5, 6 and 7）”；独立记录Scipione提及。将组题与`sec_ii:l106-107`图注分开锚定，并以跨段来源指针记录“Cardinal Borghese”与Scipione的同页身份语境；新增1条caption depiction断言。
- Plate 10：物理第43页组题“Sacchetti Taste（see Plates 10 and 11）”；独立记录组题，将Sacchetti提及映射到Marcello候选，留待全局S3对齐；图注本身已在规范`sec_iv:l157-159`迁移。

原Plate III OCR段`sec_i:l15-29`仍因反向残片不可用而排除，旧“题注与书前目录重复”的排除依据已撤销。整章OCR副本继续仅作校勘副本，不计为第二份语料。第2章现有74个规范段，63段迁移、11段有理由排除、0段queued；整章文本差异、已发现的图版题注缺项及脚注回链均已收口。S2表审计0结构错误；本章未决身份与版本判断交S3处理。

## 正式章名来源段补录（2026-09-27）

首页PDF物理第1页可见正式章名“POPE URBAN VIII AND HIS ENTOURAGE”，整章OCR第8行有该标题，规范`02_CHP-2_intro.md`仅保留“Chapter 2”。新增独立标题转录段并复用`cand-3104`记录Urban VIII提及；标题作章级元数据，不增加原书事实断言。后续重复页眉和页码仍按版面元数据处理。

补录后第2章共有75个规范段，64段迁移完成、11段有理由排除、0段queued；全书S0为799段，S2为113 reviewed、25 excluded、661 queued，提及4,224条、原书断言2,147条。第2章本地S2与全章OCR差异核对已完成，全书S2继续按源序处理第3章。

## 第二章p.40语义复核与Plate 5题注（2026-10-08）

p.40正文及注1–5完成语义复核：30条原书statement、65条mentions；拆分作品创作、内容引导、任职、别墅建造/附着、占星和教廷目标等复合陈述，原将未具名朋友关系对象保留开放并纠正“his friends”误映射到诗歌作品；全书交接审计现补匿名群组候选cand-11558及精确mention m-chp2-secii-l91-104-0066（547:558），将对象端点连至来源限定群体，不推断成员、人数或其与相邻company of poets的同一性。补标12条正文关系候选，另把注4中仅称为“对Galileo的处置”的宽泛关系列为候选。脚注正反链接均已核实；注1支持诗歌主题及别墅建造/附着三条statement。

后续Plate 5题注复核确认页题将“Cardinal Borghese”指向Scipione Borghese；将印刷题注的作者归属与描绘关系列入S2候选，候选作品版本仍未定，不并入正文Bernini胸像组。该题注段有2条关系候选。全书当前2,428条关系候选、2,414条端点齐全、14条开放；严格审计`s2_missing=[]`、`errors=[]`，完整闭合测试303项及2个子测试通过。Plate 7题注随后已完成关系候选标注；下一段按S0来源顺序为Plate 8题注`chp-2:02_CHP-2_sec_ii:l115-116`。S2交接仍在进行。

## 第二章Plate 8题注与书前目录对读（2026-10-08）

对正文及书前图版目录的Barberini Chapel题注分别保留位置与设计署名statement，复用同一组礼拜堂、教堂和Castelli候选；四条caption陈述均列入关系候选，不将内部礼拜堂扩大为整座教堂。当前严格审计无错误，全书关系候选2,433条（2,419条端点齐全、14条开放）；下一段按来源顺序为`l118-125`。


## 第二章p.41正文及后置脚注（2026-10-08）

核读 chp-2:02_CHP-2_sec_ii:l118-125 并回核同页PDF物理第26页。35条原书statement、70条mention；补入papal land and sea forces候选及mention。分开Velletri铜像的委托与安装、Carlo的军职与修辞比较、Giori对Bernini/Sacchi分别的欣赏、兄弟关系、Paul III墓归属与Council of Trent召集。纠正一条比较陈述的端点，使Julius II比较对应Urban VIII而非墓葬作品。

28条关系statement保留为S2候选，其中3条缺具体作品端点；未生成正式关系。注1–6与相关正文statement双向链接，注6的两幅Seaports只关联到两机构集合，保留作品—机构对应未定；注引资料未独立查阅。L119续接L103–104，Council和墓龛语句续至L127–139。严格审计：12,288 statements、27,398 mentions、2,462条关系候选、2,445条端点齐全、17条开放；s2_missing=[]、errors=[]。下一段按来源顺序为 chp-2:02_CHP-2_sec_ii:l127-139。

## 第二章后置脚注L147–193语义与关系候选复核（2026-10-08）

对照分节来源、p.33、p.37、p.39页图及已迁移正文statement，对第二章后置注释`chp-2:02_CHP-2_sec_ii:l147-193`作全段复核。印本p.33确认Forge of Vulcan、为Barberini宫设计的挂毯及尚属计划的罗马防卫寓意；p.37确认1月8日1633年avviso转引的主语结构；同页正文将“Cardinal Borghese”局部解析为Scipione Borghese，但雕像与正文两尊胸像的版本关系仍未定；p.39确认Sacchetti collection与Pinacoteca Capitolina是藏品和机构两个端点。相关断言保持Haskell/avviso归属，未将引文当成独立核验。

修订6条statement、2条mention和1条候选说明。将avviso拆为Bernini制作、教皇委托、Scipione Borghese报酬三项关系候选；修正“Cardinal Borghese”mention至人物候选，另登记雕像短语与`Papa`嵌套/专名mention。补录Cortona壁画题材位置、挂毯的题材与预定宫殿位置、计划寓意所在宫墙；保留`cand-4583`与第VII节十二幅挂毯`cand-4935`为独立候选，待S3比较。补正Sacchetti collection地点端点、Domenico研究作者方向、p.60委托方向；p.61挂毯纪念Urban VIII列为关系候选。修正L154→L182、L176→第1章注释statement、L193→`sec_iv:l3-4`的引用目标；113条注释到正文的正向链接均已有对应反链。全段85条statement、93条mention，其中16条关系候选；未写入`relations.csv`。

严格阶段审计：1,019 KU、11,498 candidates、27,400 mentions、12,306 statements；S2关系候选statement 2,527条（2,506条两端齐全，21条开放），832段覆盖中678段reviewed/complete、154段excluded/complete。`s2_missing=[]`、`errors=[]`；两条既存enrichment `source_ref`警告及语义质量通用提示仍在。全书S2交接继续，未进入S3–S6。
## 第二章 p.38 关系端点交接复核（2026-10-09）

复核CHP-2.pdf印刷p.38／PDF物理页19及规范段chp-2:02_CHP-2_sec_ii:l71-78。把“scholars in many countries”登记为由Marcello的联系行为界定的匿名群体候选cand-11557，新增精确mention m-chp2-secii-l71-78-0083（1707:1733）；成员、人数和具体国家未载，Marino不推定为群体成员。依据同段上下文，将Galatea复制品的“the artist”按Haskell本段叙事映射为Pietro da Cortona候选cand-0342；注4说明此说来自Passeri且另有版本。排除原匿名画家占位候选cand-4468，复制品实体cand-4467仍未定位至存世作品。一般性“searching for new talent”没有有界对象，关系端点仍开放。新增1个候选、1条mention；无新增statement、KU或正式关系。

## 第二章 p.39–40 关系端点交接复核（2026-10-09）

p.39四条关系候选经印刷页39复核仍缺授予者、任期/任命者、具体赞助人群体或品味影响目标，均保留开放；p.39注3的“one chronicler”只按注3来源连到Soprani候选cand-3500。p.40“his friends”补录为匿名群体候选cand-11558，mention m-chp2-secii-l91-104-0066的精确跨度为[547,558)，对应Urban VIII劝告关系端点已连接该候选。群体类型、人数和个体成员均未知；不并入紧邻提到的诗人。全库11,536 candidates、27,469 mentions、12,644 statements；2,808条S2关系候选中2,784条端点齐备、24条开放。严格表审计通过；全量同步闭合303 passed、2 subtests passed，9/9检查通过，结构契约130/130；S2尚未交接。


## p.29–30 收藏画作组建模与关系端点复核（2026-10-10）

对照`02_CHP-2_sec_i.md`的p.29–30原文和PDF物理页10–11，按S0段落重建画作组端点。p.30旧大师画作以cand-11567登记为非穷尽作品组，五位具名艺术家各自连至该组；新增宫殿location_of候选。p.29“along with others by...”登记为另一个作品组cand-11568；Carracci集体cand-4318、匿名威尼斯大师集体cand-11569及Cambiaso分别作为creator_of候选，威尼斯艺术传统term cand-4319保持分立；补充大房间location_of及与绘画收藏cand-4313的part_of候选。两组的作品名、数量和完整成员不详；Carracci、威尼斯大师和collection类型仍待解决。

本轮新增3个候选、3条精确mentions、3条statement，改写8条原statement，新增11条S2关系候选；不新增KU或S6正式关系。source line及candidate source_ref经严格审计后校正。严格表审计通过，`errors=[]`、`s2_missing=[]`；全量同步闭合通过、结构契约130/130。全书S2仍未交接。

## p.29–30脚注引用候选规范化（2026-10-10）

本章42条具有双端候选的`footnote_citation` statement已按引用方向规范为《赞助人与画家》→被引archive的`cites`候选；不把脚注主题人物误作引用关系端点。其余缺一端或两端的引用语句仍待回查。全书范围及未解决数量见[全书S2结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)和[阶段记录](../process/stages.md)。

## 第二章p.59书信脚注引用候选（2026-10-10）

注1–3三条书信引文已规范为《赞助人与画家》→书信archive的cites候选，保留Pecchiai、Pollak、Lumbroso刊本定位、语境候选和正文回链；书信原件及被引版本未独立查阅。改写3条既有statement，不增候选、mention、statement或S6正式边。全库当前3,628条显式S2关系候选（3,614条端点齐备、14条开放），双端未分类statement 4,440条。

## 第二章p.60–61三条书目脚注引用（2026-10-10）

p.60注1 Passeri、注6 Pollak及p.61注2 Bellori均已规范为本书指向被引archive的cites候选，逐条保留准确刊本定位和正文回链；被引页面未独立查阅。只改写3条statement，无候选、mention、statement新增或S6正式边。当前全库3,631条显式S2关系候选（3,617条端点齐备、14条开放），双端未分类statement 4,439条。

## 第二章p.59注4–5书目引用（2026-10-10）

注4“Feliciangeli”由书内书目p.422补足出版物身份并保留原脚注无页码的边界；注5“U. Barberini, 1950”继续连到题名和定位未明的open archive候选。两条均以本书cites候选连接对应正文，未独立查阅被引内容。改写2条statement，不新增候选、mention、statement或S6正式边。当前关系候选3,633条（3,619条端点齐备、14条开放），双端未分类statement 4,439条。

## 第二章p.60注2 Bellori/Mezzetti引用拆分（2026-10-10）

复合注2现拆为两条本书cites候选：Bellori 1942 p.84与Mezzetti 1955 p.253；书内p.60印本和p.429书目支持将S0 OCR的Mozzetti校为Mezzetti，但cand-4948仍保持open。两条均回链Maratta使徒系列statement；被引内容未独立查阅。新增1条statement，候选与mention数不变，不生成S6正式边。当前关系候选3,635条（3,621条端点齐备、14条开放），双端未分类statement 4,438条。

## 第二章p.60注3位置、肖像归属与引用拆分（2026-10-10）

注3拆分为四条可区分记录：正文所述单幅肖像在Haskell出版时位于罗马Galleria Nazionale di Arte Antica；Cardinal Antonio的其他肖像群描绘Antonio；其中两幅由注释称为Nanteuil作品；本书引用Edoardo Lombardo 1959年第2页。画廊身份与当前保管状态、肖像群成员、Nanteuil身份及被引内容均未独立确认，均按来源限定保留。mention `the portrait` 从肖像群cand-4950改指正文所述作品cand-4922；正文两条marker 3记录均补齐四条注释statement反链。未新增候选、mention或KU，也未生成S6正式关系。

写后全库12,667条statement、3,639条关系候选（3,625条双端齐备、14条开放），双端未分类statement 4,436条；未分类`footnote-claim`降至12条（本章11条、第5章1条）。脚注引用候选累计115条。严格阶段审计`errors=[]`、`s2_missing=[]`；全量同步闭合9/9项通过（303 passed、2 subtests passed）。
## 第二章p.59注6失佚陈述与Briganti引用拆分（2026-10-10）

复核`02_CHP-2_sec_vii.md` L44、印刷p.59注6：“Briganti, 1962, p. 254. The picture has disappeared.” 将Haskell报告的Xenophon画作失佚状态与书目引用分开：原statement改为作品cand-4913的`reported_missing_by_book_publication`单端陈述，不将出版时的报告解释为现状核验；新增《赞助人与画家》cand-2962指向Briganti archive候选cand-4473的`cites`候选，保留p.254定位。被引页面未独立查阅。补录原句中的“The picture” mention `m-chp2-secvii-l38-54-0053`，并让正文marker 6同时回链失佚陈述和引用statement。没有新增候选或KU。

受控脚本`process/normalize_chp2_p59_note6_citation_20261010.py`按statement、mention、candidate和来源SHA及固定端点、原文行、mention跨度和正文回链执行dry-run/apply；恢复副本为`04-knowledge/tables/book-statements.jsonl.bak-s2-handoff-chp2-p59-note6-20261010`及`04-knowledge/tables/mentions.csv.bak-s2-handoff-chp2-p59-note6-20261010`。写后SHA-256：statement `97638a76da75dee567f8ec0306de06c5eab4ef2f800193cdff5b70ab46703cb5`，mentions `223072dfc14c44d6f1098c71653a2ea90230479e4af21d569eb14d4c25f84be4`。全库12,668条statement、27,487条mention；3,640条关系候选（3,626条双端齐备、14条开放），4,435条双端statement仍未标记relation_candidate，`footnote-claim`降至11条，`cites`关系候选108条。严格阶段审计`errors=[]`、`s2_missing=[]`；本次记录前全量同步闭合通过，后续仍需对文档变更复跑门禁。全书S2语义交接未完成。

## 第二章p.60注4法国部长评论与Hanotaux引文拆分（2026-10-10）

复核`02_CHP-2_sec_vii.md` L47、印刷p.60注4。原statement将Haskell转引的1654年法国部长评论和Hanotaux书目指引混为一条`footnote-claim`，且方向与France候选类型不准确。现改为`reported_critical_comments_about`：匿名法国部长群候选cand-4952→Francesco候选cand-0199，限定日期1654，保留“疑为法国所忌”及嫉妒、羡慕、报复、忘恩等被引评价；关系仅列S2候选，群体未识别，Hanotaux所引页面及原始部长文件均未独立查阅。另新增《赞助人与画家》cand-2962→Hanotaux archive候选cand-4953的`cites`记录，定位p.8及pp.12–13，并在正文marker 4双向回链两条statement。

按语义区分法国政体与地理位置：正文“sympathies moved away from France”及注4引文中的France两处mention由地理候选cand-4266改指既有政治实体候选cand-4221；正文statement对象同步修正。Maffeo往返法国的地理位置mentions仍保留cand-4266。未新增候选、KU或S6正式关系。

受控脚本`process/normalize_chp2_p60_note4_hanotaux_20261010.py`以四表/来源SHA、固定ID与类型、原文引句、mention跨度、正文端点及反向脚注链接作预检；默认dry-run后执行apply。statement恢复副本为`04-knowledge/tables/book-statements.jsonl.bak-s2-handoff-chp2-p60-note4-20261010`，mentions恢复副本为`04-knowledge/tables/mentions.csv.bak-s2-handoff-chp2-p60-note4-20261010`。写后SHA-256：statement `334eef0f81f03918311196131053020e6286af822a1a63e136ec294cbc32dbea`，mentions `ad57d10340723ec589285d0ad37a1ea0e5963a96360896febbe6e07abf5e31a9`。全库12,669条statement、27,487条mention；3,642条关系候选（3,628条双端齐备、14条开放），4,434条双端statement尚未显式分类，未分类`footnote-claim`降至10条，显式`cites`候选109条。全书S2交接未完成。

## 第二章p.60注5 Palomino归属、被描绘者、Haskell推断与引用拆分（2026-10-10）

复核02_CHP-2_sec_vii.md L48、印刷p.60注5。原注将Palomino对Antonio Barberini肖像的归属、被描绘者身份、Antonio返法时间和Haskell的纠正推断混在三个footnote-claim中；现按来源声音与主张类型拆分：

- 原...5a-palomino-attribution改为Palomino经Haskell转述的作品cand-4956→Velasquez cand-2709归属主张；新增...5a-sitter-identification记录Palomino称该作品描绘Antonio cand-0187。二者均为来源限定的S2关系候选；Haskell明确质疑被描绘者识别，未将Palomino主张当作事实。
- 原...5b-antonio-return-chronology改为关于Antonio于1653年后才从法国返回的单端时间陈述，保留France地理限定；不再把它编码为人物间关系。
- 原...5c-palomino-confusion-inference改为Haskell推断该肖像可能描绘Francesco cand-0199的来源限定候选关系；原注未证实此识别，可能作品cand-4929继续单独保留。
- 新增...5d-palomino-citation，连接本书cand-2962与Palomino著作archive候选cand-4955，定位vol. III, p.336；被引版本和页面未独立查阅。

正文marker 5现双向链接上述5条statement。未新增候选、mention、KU或S6正式边。

受控脚本process/normalize_chp2_p60_note5_palomino_20261010.py按固定statement/candidate ID、来源与表SHA、原文、定位和正文回链执行dry-run/apply。恢复副本为04-knowledge/tables/book-statements.jsonl.bak-s2-handoff-chp2-p60-note5-20261010。写前statement SHA-256为97638a76da75dee567f8ec0306de06c5eab4ef2f800193cdff5b70ab46703cb5，写后为f1947acaa6610e3a9a3d37be4b6556a95a208e82d5d84b9c7a81c6eefd2f04dd。本批改写4条既有statement、新增2条；全库12,671条statement、3,646条显式关系候选（3,632条端点齐备、14条开放），双端未分类statement 4,432条，未分类footnote-claim为7条，cites候选110条。卡片检查无待写文件。全书S2交接仍未完成。

## 第二章p.60注7挂毯状态、底稿位置、归属与引文拆分（2026-10-10）

复核02_CHP-2_sec_vii.md L50、印刷p.60注7，并查看CHP-2.pdf物理页49。原三条footnote-claim混合挂毯组状态、卡通底稿位置、艺术家建议归属、此前的壁画计划和四项书目指引，现分别记录：

- 原7a改为挂毯组cand-4935在Haskell 1962年出版时已分散的单端状态陈述；新建7a-location，记录卡通底稿cand-4936当时位于Palazzo Barberini cand-4957。出版时位置不等于当前保管，未独立复核。
- 原7b改为Blunt与Cooke经Haskell转述的Ciro Ferri建议归属。原注未明确“artist”指十二幅挂毯还是其卡通底稿，因此主语留空、保留两个可能作品端点，关系候选保持open，不作为正式关系。
- 原7c改为此前壁画计划cand-4961针对Barberini Salone cand-3556的planned_decoration_for候选；qualifier保留其仅为计划、未说明执行，并注明与挂毯题材相似。
- 新增本书cand-2962分别cites Cavallo 1957（cand-4958）、Calberg 1959（cand-4959）、Blunt and Cooke 1960 p.36（cand-4960）和Pastor XIII p.969（cand-4237）的四条记录。被引文章及页面未独立查阅；Pastor候选保留版本待决。
- 印本p.60明确作“Blunt and Cooke, 1960”，S0 OCR作“i960”；只在cites qualifier记录该校读，不改写来源资产。

正文marker 7的两条作品statement现双向连接8条脚注statement。未新增candidate、mention或KU，也未写入S6正式关系。

受控脚本process/normalize_chp2_p60_note7_citations_and_relations_20261010.py对statement、mentions、candidate及S0来源SHA，候选类型/状态、原文行、10处mention跨度和两条正文反链作预检；dry-run后apply。恢复副本为04-knowledge/tables/book-statements.jsonl.bak-s2-handoff-chp2-p60-note7-citations-20261010。初次写后statement SHA-256为e365f21672abb8ab72999882c03d8717ef90742347145bf18fe3d02bbad2768a。随后复核确认书目候选cand-11414只给出1943年而未提供卷号，不能将该年套用于卷XIII引文；已由correct_chp2_p60_note7_pastor_version_20261010.py按statement与candidate SHA执行dry-run/apply，移除year并保留cand-11414作为待对齐版本线索。校正恢复副本为04-knowledge/tables/book-statements.jsonl.bak-s2-handoff-chp2-p60-note7-pastor-version-20261010；最终statement SHA-256为ee57596eeafea9a5050ed5790a132d87882568b073b524d8ab0b542b4f2e6d60。本轮将全库statement增至12,676条，S2关系候选3,653条（3,638条端点齐备、15条开放），双端未分类statement 4,429条；未分类footnote-claim降至4条，cites候选114条，候选与mention总量不变。全书S2交接未完成。

## 第二章p.61注1、3、4档案定位、范围说明与建筑参与（2026-10-10）

复核02_CHP-2_sec_vii.md L51、L53–54及CHP-2.pdf物理页50（印刷p.61）。本批将三个footnote-claim拆分为档案定位、范围陈述、关系候选及书目引文：

- 注1原statement改为本书cand-2962 cites Vatican manuscript候选cand-4962，补录印本所见MSS. Barb. Lat. 6463；新增cand-4962 held_by Biblioteca Vaticana机构候选cand-4380的出版时点关系。Haskell所称“many other collections”未具名，不新增候选；手稿内容与当前保管均未独立核验。
- 注3改为关于全书概述遗漏许多Barberini赞助实例的范围说明，不作为家族关系；新增本书cites Baglione候选cand-4546 pp.177–183、Pastor卷XIII候选cand-4237 pp.903–1000。印本校正S0 OCR漏掉的页码连接符；卷XIII版本仍未解决，1943年书目候选cand-11414只保留为待对齐线索，不把年份赋给该卷。
- 注4改为Francesco候选cand-0199参与San Carlo alle Quattro Fontane建造的来源限定关系候选；“part”未说明具体角色，未推断为委托人、赞助人、建筑师、建造者或所有者。新增本书cites Pollak 1927, vol. I, p.45；印本alle拼写只记入S2 qualifier，S0不改。
- 正文marker 1、3、4分别回链档案引用/馆藏、范围说明及两项引文、建筑参与及Pollak引文。没有新增candidate、mention、KU或S6正式关系。

受控脚本normalize_chp2_p61_notes1_3_4_20261010.py对statement、mention、candidate、S0和PDF SHA、候选类型/状态、印本页码、原文、6处mention跨度及三处正文回链执行dry-run/apply。恢复副本为04-knowledge/tables/book-statements.jsonl.bak-s2-handoff-chp2-p61-notes1-3-4-20261010。写后statement SHA-256为637010822eb67c99c1a6c6c206f77ad6f7549744aef2a1c780d3622fd0b19205。本批新增4条statement并改写6条既有statement；全库12,680条statement、3,659条显式关系候选（3,644条端点齐备、15条开放），双端未分类statement 4,427条，未分类footnote-claim余1条（第5章），cites候选118条。全书S2交接仍未完成。

### 第二章 p.30 注1 日记、出版与通信关系（2026-10-10）

复核 `02_CHP-2_sec_i.md` L147及脚注上下文。将“Anna Banti published”校正为日记候选 cand-4378 → 出版者 Anna Banti 候选 cand-4379，移除冗余 publisher_candidate_id；新增“日记由 Bernardo Bizoni 保存”及“Vincenzo Giustiniani 是 Bizoni 之友”两条来源限定关系，并补录原文漏掉的 Giustiniani mention（cand-1200）。同时分类同注六条既有statement：Albani研究两幅Titian作品是Haskell的推断；Colonna售地书信与1605、1611及Reni书信保留来源转述、未具名作者/收件人和“presumably”限定。未把被引出版物当作独立查验，也未扩展人物关系或书信端点。

本批新增2条statement、1条mention，分类7条既有statement；全库为12,684条statement、27,490条mention、3,774条显式关系候选（3,758条双端、16条开放），双端未分类降至4,317条。未新增KU/candidate或S6正式关系。恢复副本：`book-statements.jsonl.bak-s2-chp2-p30-note1-relations-20261010`、`mentions.csv.bak-s2-chp2-p30-note1-relations-20261010`；写后SHA-256分别为 `1ade5faf6b6aa1c7cabb9efc772e6610b072b3ab80dae7b2bf2cc3c7c97e9c7c` 与 `10eb1687c3af1f4515cae4c68273a263f530dd3c8bb3613a3d2b26ddd9a54647`。全量同步闭合通过：9/9检查、303 passed与2个subtests；严格表审计errors=[]、s2_missing=[]，结构契约130/130。卡片预检1,019张、2,608张表、10,149行，files_to_write=0；git diff --check通过（仅有工作树LF/CRLF转换提示）。

### 第二章第一节 L44–53关系分类（2026-10-10）

18条既有双端statement完成逐条语义裁决：16条保留为关系候选、2条标为非关系。受控预检发现Ferrara事件候选`cand-4254`缺少本段mention，先补入原文短语`visit to Ferrara to take over the city`，再执行statement dry-run/apply。保留Haskell对继承金额、政治过程、作品影响、肖像身份和建筑样式的限定；不把Este王朝当作被掠夺的具体藏品，也不把三幅画的组级影响归给单幅作品。写后全库12,700条statement、27,493条mention，双端未分类4,161条；下一段为L55–69。完整SHA、备份与计数见[全书过程记录](../process/stages.md)。本批不生成S6正式关系。

### 第二章第一节 L55–69关系分类（2026-10-10）

22条既有双端statement完成语义裁决：20条作为S2关系候选、2条作为非关系陈述。Barocci的年龄评价不推断为已委托；明确请求私人房间画作另列。Renier Zeno的引语只保留为来源归属的描述，不构造人物关系。Paris三年对政治观的影响保留为Haskell的因果解释；法国只记作欢迎发生地。任命、作品、赠礼与建筑地点均按原文保留角色和范围。无candidate、mention、statement新增，无S6正式关系。写后全库双端未分类4,139条；下一段为L71–80，有18条待处理。详细裁决和恢复凭据见[全书过程记录](../process/stages.md)。
### 第二章第一节 L71–80 Scipione端点校正与关系分类（2026-10-10）

三条正文陈述原指向索引子目候选cand-0397，现按本段具名提及改连至cand-0394；索引候选保留，待S3对齐。18条双端statement分类为14条关系候选、4条非关系。将并列赞助人支出、未分配到单一人的资源、对象端点错误的艺术变化陈述和Zeno传述分别保留为非关系，避免虚构共同活动、个体资源归属、人物关系或错误端点。报告的委托、合同、作品转移、职务、居住及艺术史分期保留来源限定；入狱执行者仍未知。另4条单端statement保持开放。写后全库relation_candidate=true 3,954条（3,927双端、27开放）、false 1,814条；双端待分类4,121条。下一段为L82–93。详情、恢复副本和SHA见[全书过程记录](../process/stages.md)。

### 第二章第一节 L82–93关系端点校正与分类（2026-10-10）

18条未分类双端statement均有明确原文关系，全部保留为S2关系候选。核正Gregory XV与Ludovico Ludovisi共同赞助的主体范围：用无类型、开放群组`cand-11578`承接共同主语，避免将共同陈述拆成个人行为；为Scipione别墅所代表的未名社会群体补入`cand-11579`，不再把地点Rome误用为关系对象。新增两条精确mention，不创建KU或正式关系。全库关系候选3,972条（双端3,945、开放27）、非关系1,814条；双端待分类4,103条。下一段L95–106尚有24条双端statement待审。过程、SHA与恢复副本见[全书过程记录](../process/stages.md)。


### 第二章第一节 L95–106关系端点校正、mention补录与分类（2026-10-10）

24条未分类双端statement全部依据原文保留为S2关系候选。修正Giustiniani—del Monte共同兴趣推断的双人物端点，保留Cupid画作作为Haskell推论的证据语境；“Salerno与其他研究者无法追寻Hopf著作”以无类型、开放群组端点记录。补入四条已有statement缺失的mention及该研究者群组mention。所有评价、推断、未能追寻状态和未决身份继续带来源限定；未新增KU或正式关系。全库关系候选3,996条（双端3,969、开放27）、非关系1,814条；双端待分类4,079条。下一段L108–119有13条双端statement待审。详见[全书过程记录](../process/stages.md)。
### 第二章第一节 L108–119剩余双端关系裁决（2026-10-10）

对照规范段chp-2:02_CHP-2_sec_i:l108-119及印刷页30，复核剩余13条未分类双端statement：12条为原文关系候选，1条为非关系陈述。将Giustiniani注意力、对Bernini的评价与赞助机会、Mannerist群体的收藏呈现、作品与诗作、Rubens比较及Maffeo的未来委托推测保留为有来源限定的候选；“earlier works”是Apollo and Daphne与David作品的共同评价，不是两件作品间的关系。

修正三处端点：镜像轶事改为Maffeo→Bernini，David作为独立自画像statement及原文提及保留；“great household”从混合范围的Barberini家族及家户KU改接开放机构候选cand-11581；Paul V与Scipione Borghese的集体主语改接无类型开放候选cand-11582，Ludovisi 1621年后的阶段仍独立记录。四条单端叙述不纳入双端分类统计；本段双端未分类归零。

受控脚本classify_s2_chp2_l108_119_pending_relations_20261010.py完成哈希预检、dry-run和apply；新增2个candidate、1条mention并重定向1条既有mention。恢复副本：book-statements.jsonl.bak-s2-chp2-l108-119-pending-20261010、entity-candidates.csv.bak-s2-chp2-l108-119-pending-20261010、mentions.csv.bak-s2-chp2-l108-119-pending-20261010。statement/candidate/mention写前SHA-256为33c48449209a733ec376552998667f6068430db62737a8a30b09a8317c0276e1、b888e887179fcfeab5e94cf53537c8d190dfa4c1dc7d23243760e8fd5e917c4c、b06efbe0258fb9b7e25a83d28e909ca98ff73dec53c42ca6a2669ad55fbd7ad9；写后为08c146e353ae05454063f7cd33438fd5f0347a2606cf6e868b400df594036558、3643981fd7dc5829bfb4778a118f279acfe40a279cbd10b507fc82edbea3ca85、d16b5649889babf5c7e14cce2c089a95a197b2e6ac9d92dea9442cc5acda465a。写后双端关系候选3,981条、非关系450条、未分类4,066条；全书S2未完成。

### 第二章第一节 L124–157脚注观点分类（2026-10-10）

将Walker关于《The Andrians》与《The Worship of Venus》的两条意见分类为S2关系候选：关系记录的是Walker对具体作品的来源判断，保留“unlikely”、Haskell转述层级及Rubens作为争议复制者；不写成Rubens没有临摹原作的确定事实。无候选、mention或statement增删。受控脚本classify_s2_chp2_l124_157_walker_assessments_20261010.py完成dry-run/apply；恢复副本book-statements.jsonl.bak-s2-chp2-l124-157-walker-20261010。statement SHA-256由08c146e353ae05454063f7cd1c433686d3223bf90d7879edbc4cf1e47d887acf2变为ea9d509a5e0a8b88a7ba7cd1c433686d3223bf90d7879edbc4cf1e47d887acf2；本段双端未分类归零。

### 第二章第二节 L3–8解释性陈述分类（2026-10-10）

将Nepotism in Rome与Urban VIII之间的“亲属任亲密顾问”句标为非关系陈述。原文是Haskell关于教廷嫉妒背景下亲属任用可理解的解释，没有指明任何顾问，也没有说Urban VIII实际任用了某个特定亲属；两个候选只保留为语境。受控脚本classify_s2_chp2_sec_ii_l3_8_nepotism_interpretation_20261010.py完成dry-run/apply；恢复副本book-statements.jsonl.bak-s2-chp2-sec-ii-l3-8-nepotism-20261010。statement SHA-256由ea9d509a5e0a8b88a7ba7cd1c433686d3223bf90d7879edbc4cf1e47d887acf2变为1887cd1731e90f73de73d9d1a938da0d97ccc7bb509bc902404f2d4cdef1ed0c。

### 第二章第二节 L10–18关系端点校正与分类（2026-10-10）

5条未分类双端statement均保留为S2关系候选。Pietro Contarini的城市描写保留Papals States与Rome两个对象；“来自每个国家来罗马的people”不再错以引述者Contarini为行动主体，新增无类型开放群组cand-11583及mention m-chp2-secii-l10-18-0036（跨度[1995,2025)），将statement主语改为访客群、对象为Rome。Rome的“emporium”及tribute措辞保留为引语修辞，不写成财政事实。其余关系保留Haskell关于欧洲国家力量、罗马声望、教皇财务赞助范围和Urban VIII维持教皇国财富意图的作者限定。

受控脚本classify_s2_chp2_l10_18_relations_20261010.py完成dry-run/apply；新增1个candidate和1条精确mention。恢复副本：book-statements.jsonl.bak-s2-chp2-sec-ii-l10-18-20261010、entity-candidates.csv.bak-s2-chp2-sec-ii-l10-18-20261010、mentions.csv.bak-s2-chp2-sec-ii-l10-18-20261010。statement/candidate/mention写前SHA-256为1887cd1731e90f73de73d9d1a938da0d97ccc7bb509bc902404f2d4cdef1ed0c、3643981fd7dc5829bfb4778a118f279acfe40a279cbd10b507fc82edbea3ca85、d16b5649889babf5c7e14cce2c089a95a197b2e6ac9d92dea9442cc5acda465a；写后为6120db88ad9cbb35777d02c9afef22ac65df1cdf3ee705d8ec82dd34c0ed8f44、1a27c9033338194ff974db22bc9ceef63d15e8361ea47b770563d3ef9033f9f1、a2b203b54cb0ab0dc24e9c83367182748286d6366f224f1fca708feb0578944c。

### 第二章第二节 L20–28关系分类（2026-10-10）

8条未分类双端statement均保留为S2关系候选，涉及Counter Reformation与精神危机、智识变化对教廷的影响、Naudé引语、Urban VIII与法国联盟及Richelieu的利用，以及Baroque说服性、教皇地位威胁和罗马防御工事的历史解释。所有关系仍限定为Haskell或引述者所报告的内容；Naudé引语补列Rome、Italy两个附加参照，智识变化statement明确连接已出现的Accademia dei Lincei、Galileo与Renaissance候选，不把引语中的人口评价当作核实事实。

受控脚本classify_s2_chp2_l20_28_relations_20261010.py完成dry-run/apply，无候选或mention增删。恢复副本book-statements.jsonl.bak-s2-chp2-sec-ii-l20-28-20261010；statement SHA-256由6120db88ad9cbb35777d02c9afef22ac65df1cdf3ee705d8ec82dd34c0ed8f44变为c0225e1438119a5321de4f7f0a8cd29dced58e710a83e9aa02b23b2322642dbc。写后全库关系候选4,023条（双端3,996、开放27）、明确非关系1,816条；8,497条双端中4,447条已分类（52.3%）、4,050条未分类。下一段L30–40有15条双端statement待审；全书S2语义交接未完成。

### 第二章第二节 L30–40关系分类及墓葬端点校正（2026-10-10）

15条未分类双端statement均依据原文保留为S2关系候选。对照印刷页34，修正两条巴尔达基诺工程statement：原对象“圣彼得墓址”与风险对象不符，原文指地基可能扰动的复数早期基督教墓葬。新增无类型开放候选cand-11584及mention m-chp2-secii-l30-40-0043（[2583,2604)），两条statement均改接该墓葬群。对Bernini父母出身、Passeri引语、Urban任用/赞语、Bernini与巴尔达基诺、Maderno立面、匿名观察者批评、委员会/工程关系及“unlikely”规划判断均保留来源层级与语气。四条单端statement未纳入双端分类。无KU或S6正式边新增。

恢复副本与三表SHA、受控脚本和全库检查见[过程记录](../process/stages.md)。本批后双端关系候选4,011条、非关系451条、未分类4,035条；本章段内双端未分类归零。

### 第二章第二节 L42–50扭柱端点复核与关系分类（2026-10-10）

21条未分类双端statement均保留为S2关系候选。复核“the twisted column”上下文后，将通用建筑形式与巴尔达基诺实体构件区分：cand-11585（term）承接所罗门圣殿来源传统、古代大殿屏风形式及Raphael对该形式的欣赏；cand-11586（work）承接圣彼得大殿内被称作遗存的未名单柱及“Christ was supposed to have leant”传统。相应重映射三条mention并修正四条statement端点。全部保留Haskell对费用、家族与大殿关系、装饰、委员会/教皇角色的归属；“probably”“supposed”和方案先后关系不升级成确定事实。无KU或S6正式边新增。

本批后全库关系候选4,059条（双端4,032、非双端27）、双端明确非关系451条、双端未分类4,014条；8,497条双端中4,483条已分类（52.8%）。严格表审计通过，卡片预检files_to_write=0，全量闭合15/15与303 tests、2 subtests通过；全书S2尚未交接。下一段L52–60有25条双端statement待审。过程、SHA与恢复副本见[全书过程记录](../process/stages.md)。

## 第二章第二节 L52–60与L62–69关系分类（2026-10-10）

L52–60的25条未分类双端statement全部保留为S2关系候选。修正两条关于四位圣人遗物的对象端点，并新增开放候选cand-11587及mention m-chp2-secii-l52-60-0089（段内[683,730)）。L62–69的13条双端statement也全部保留为S2关系候选；维持Haskell判断、Passeri讽刺引语、Stone转引、肖像许可，以及S. Bibiana建筑与重建工程等不同对象的来源边界。两批均未新增KU或S6正式关系。恢复副本、SHA和逐条证据见[全书过程记录](../process/stages.md)。

写后全库11,565个candidate、27,504条mention、12,700条statement；8,497条双端statement中4,070条关系候选、451条非关系、3,976条未分类（53.2%已分类），另有27条开放端点关系候选。严格表审计`errors=[]`、`s2_missing=[]`；卡片预检`files_to_write=0`；全量闭合9/9、303 tests及2 subtests通过。下一段为`chp-2:02_CHP-2_sec_ii:l71-78`，有2条待裁决。S2交接仍未完成。

## 第二章第二节 L71–193及第四节 L3–17关系分类（2026-10-10）

补记第二章第二节L71–78、L80–89、L91–104、L118–125的2、5、9、6条关系候选，以及L127–139、L141–145、L147–193的2、1、2条关系候选。保留Marino返意与旅行、Pietro及Domenichino风格判断、Urban/Bernini肖像与艺术赞助叙述、Barberini流亡/王朝解释和经转引的Gregory XIII引文；所有作者判断、引语链与计划语气均按来源限定，不新增候选、mention、statement或正式关系。

第二章第四节L3–4裁决7条：6条关系候选，1条Francesco外貌属性。对照印刷p.43确认“artistic life”及“a little careworn”；外貌描述关联到Leoni肖像作品，但Plate 3a已有作品与被描绘者关系，故不重复建边。L6–17的26条双端statement均标为S2关系候选，覆盖巴黎/马德里使团、外交目标、随行者、艺术访问、挂毯与Rubens cartoons、法国文化往来、Poussin售画和罗马赞助语境。Marino—Poussin—Sacchetti三方角色、Poussin仅为售画者、战争的条件语气及Haskell的归属均保留。印刷p.44核对“The Life of Constantine”；S0 OCR差异未改写。

无candidate、mention或statement数量变化。全库当前11,565 candidates、27,504 mentions、12,700 statements；8,497条双端statement中4,129条关系候选、452条非关系、3,916条未分类（53.9%已分类），另有27条开放端点关系候选。下一段按书序为`chp-2:02_CHP-2_sec_iv:l19-29`，有21条双端statement待裁决；S2交接仍未完成。详细判据、恢复副本及SHA见[全书过程记录](../process/stages.md)。


## 第二章第四节 L19–29 关系候选分类（2026-10-10）

21条双端statement均按原文语义标为S2关系候选；限定委托、意图、试探性提议、转述请求、预期、风格解释和近似年代，不将它们转成S6正式关系。5条单端statement保留原状。核对印刷p.45及延续到p.46的“Once again”；OCR标题“ferusalem”只记作印本校勘，未改S0。未新增candidate、mention或statement。写前/写后SHA、备份与受控脚本见[全书过程记录](../process/stages.md)。本批后8,497条双端statement有4,602条已分类（54.2%），3,895条未分类；开放端点候选27条。下一段L31–43有20条待裁决，S2全书交接未完成。


## 第二章第四节 L31–43 关系候选分类（2026-10-10）

20条双端statement均按来源范围标为S2关系候选，保留转赠、影响、赞助、风格判断、来源/关联、假说与可能委托的原文限定。核对印刷p.46及L29–31跨页承接；未具名受赠人、Berlin/Chicago与单幅作品对应关系、宫殿身份仍待解决。未新增candidate、mention或statement。写前/写后SHA、备份和逐条限定见[全书过程记录](../process/stages.md)。当前8,497条双端statement有4,622条已分类（54.4%），3,875条未分类；另有27条开放端点候选。下一段L45–52有19条待裁决。


## 第二章第四节 L45–52 关系候选分类（2026-10-10）

19条双端statement中17条为关系候选、2条为人物属性，分别记录年龄与收入比较；边界判断保留“事件/比较范围不是人物关系端点”。核对印刷p.47，OCR“lais”“onlyTestored”只记作校字，未改S0及原始引文。17条候选的关系角色、时间和不确定性、写前/写后SHA及恢复副本见[全书过程记录](../process/stages.md)。当前双端statement有4,641条已分类（54.6%）、3,856条未分类；另有27条开放端点候选。下一段L54–63有18条待裁决。


## 第二章第四节 L54–63 关系候选分类（2026-10-10）

18条双端statement中17条为关系候选、1条规模属性。页下注1把正文Bentivoglio/Ferrara概括拆分为Bologna家族起源与Ferrara重要支系，保留此差别；页图校读OCR“Use”→“life”，未改S0或原文引句。逐条边界、备份和SHA见[全书过程记录](../process/stages.md)。当前双端statement有4,659条已分类（54.8%）、3,838条未分类；27条开放端点候选。下一段L65–77有18条待裁决。

## 第二章第四节 L65–77 关系分类（2026-10-10）

18条双端statement完成裁决：16条S2关系候选，2条为时间语境和归属史属性。页图核对印刷p.49；宫殿买方的正文/脚注差异按来源并存。修正Guido游览及装饰请求的statement端点为Guido—Giovanni da San Giovanni，信件保留为证据。无候选、mention或statement增删。写后严格阶段审计通过，卡片无待写回。当前双端statement已分类4,677/8,497（55.0%）；下一段L79–89有23条待裁决。详见过程记录及SHA/恢复副本。
## 第二章第四节 L79–89 关系分类（2026-10-10）

印刷p.50页图复核后，23条双端statement中22条列为关系候选，1条为两幅壁画的共同风格与接受属性，不表示两作品互相关系。保留来源归属、委托角色、图像解释及未名选择者/顾问，不新增或改动candidate、mention、statement端点。严格阶段审计通过，卡片预检无待写回。当前双端statement已分类4,700/8,497（55.3%）；下一段L91–94有24条待裁决。详见过程记录及恢复SHA。
## 第二章第四节 L91–94 关系分类（2026-10-10）

承接前段跨页描述，印刷p.51核对后，将本段剩余24条双端statement标为S2关系候选；三条既有徽记关系保留，总计27条。保留来源归属、象征/图像关系、赞助与职业关系、约略时间和审美评价边界，不修改候选、提及或端点。写后严格阶段审计通过，卡片无待写回；闭合检查结构契约130/130。当前双端statement已分类4,724/8,497（55.6%）；下一段L96–104有28条待裁决。全量测试本轮未运行。详见过程记录及恢复SHA。
## 第二章第四节 L96–104 关系分类（2026-10-10）

印刷p.52核图后，本段28条双端statement全部标记为S2关系候选；保留Bracciolini书信、任职、写作与赞助语境，Cortona天顶的寓意解释，以及Montagu脚注的多层转述和不确定性。S0中的future、Time校字只记入S2，不改原文；无候选、mention或statement端点增删。写后严格阶段审计通过，卡片无待写回。当前双端statement已分类4,752/8,497（55.9%）；下一段L106–112有19条待裁决。全量闭合及全量测试本批未重跑。详见过程记录及恢复SHA。

## 第二章第四节 L106–112 关系分类（2026-10-10）

印刷p.53（PDF物理p.38）核图后，将19条双端statement均标为S2关系候选；保留Haskell的比较和风格判断、Domenichino的传闻链，以及Francesco可能受Rubens周期启发的限定语。未新增candidate、mention、statement或S6正式关系。写后严格阶段审计通过，卡片预检`files_to_write=0`。当前双端statement已分类4,771/8,497（56.1%）；下一段L114–125有23条待裁决。SHA与备份见过程记录。

## 第二章第四节 L114–125 关系分类（2026-10-10）

印刷p.54（PDF物理p.39）核图后，将23条原有双端statement均标为S2关系候选；并把Antonio与Francesco的兄弟关系从原“侄子/兄弟”合并断言中拆出，新增一条Antonio—Francesco statement，复用已有mention。保留比较性收入判断、未定身份的Borghese、未具名的夺取执行者及Haskell的评价边界；未新增候选、mention或S6正式关系。写后严格阶段审计通过，卡片预检`files_to_write=0`。当前双端statement已分类4,795/8,498（56.4%）；下一段L127–137有22条待裁决。SHA与恢复副本见过程记录。


## 第二章第四节 L127–137 关系分类（2026-10-10）

印刷p.55（PDF物理p.40）核图后，将本段22条双端statement均列为S2关系候选；S0中的“Sacelli”按印本校读为“Sacchi”，只记S2、不改来源。无candidate、mention、statement或端点增删。严格阶段审计通过，卡片预检`files_to_write=0`。当前8,498条双端statement已分类4,817条（56.7%）；下一段L139–152有15条待裁决。SHA与恢复副本见过程记录。

## 第二章第四节 L139–152 关系分类（2026-10-10）

印刷p.56（PDF物理p.41）核图后，15条原有双端statement均标为关系候选；Cantalamessa脚注引文再规范为《赞助人与画家》→被引出版物，复用既有候选，使本段双端关系候选共16条；其余3条单端关系断言保留为开放端点候选，无新增candidate、mention或statement。未具名受众、旧家族群体和宫殿内容集合保持开放，不猜实体。全库8,499条双端statement中4,833条已分类（56.9%），3,666条待分类；关系候选共4,405条，其中30条开放端点。严格阶段审计无错误，卡片预检无待写文件；全量闭合`run_sync_closure.py --full`通过9/9检查（303 passed、2 subtests），结构契约130/130。下一段L171–179有22条双端statement待裁决。过程记录含逐项限定、SHA与恢复副本。


## 第二章第四节 L171–179 关系分类与复合断言拆分（2026-10-10）

印刷p.57（PDF物理p.46）核图后，复核22条待分类双端statement：21条原有断言为关系候选，1条评注出版年/作者年龄为属性。将“prelates admired the pages and castrati”拆成两条分别指向已有pages与castrati候选的关系候选；本段statement由30条增至31条，现有30条关系候选和1条非关系属性。未新增candidate或mention；两个年轻Barberini枢机身份保持未定，作者对Poussin主题的解释与Claude友谊推断保留来源限定。严格阶段审计`errors=[]`、`S2_missing=[]`；卡片预检`files_to_write=0`。全量同步闭合`run_sync_closure.py --full`通过9/9检查，303 passed、2 subtests，结构契约130/130且关系一致性错误项为0；`git diff --check`退出码0（仅Git提示LF/CRLF转换）。全库8,500条双端statement已分类4,856条（57.1%），4,397条关系候选、459条非关系、3,644条待分类；另有30条开放端点候选。下一段L181–188有18条待裁决，过程记录含SHA与恢复副本。

## 第二章第四节 L181–188 关系分类与端点复核（2026-10-10）

印刷p.58（PDF物理p.47）核图后，18条待分类双端statement中17条列为关系候选，1条Landi音乐审美评价为单端非关系属性；将其误连到Rospigliosi诗剧组的对象端点清除。观众反应的“演唱者与舞台景观”拆为两个标量候选；本段statement由19条增至20条，含此前已分类项共有19条关系候选、1条单端属性。无candidate或mention增删。另将匿名观众引文收窄至印本引号内的舞台效果，校记S0 L184“. nor”应读“nor”，不改S0。Bernini方案的质量判断、Pope accession、Rospigliosi职位/戏剧关系及观众叙述保留原文语气和身份边界。严格阶段审计`errors=[]`、`S2_missing=[]`；卡片预检`files_to_write=0`。全库8,500条双端statement中已分类4,874条（57.3%），4,415条关系候选、459条非关系、3,626条待分类；另有30条开放端点候选。下一段L190–245有23条待裁决；逐项理由、SHA与恢复副本见过程记录。

## 第二章第四节 L190–245 关系分类（2026-10-10）

对照印刷pp.58–61（PDF物理pp.47–50），23条待分类双端statement均确认存在明确的来源、归属、作品/收藏、出版/引证、任职或评价关系，全部标记为S2关系候选。保留原书对学者意见、来源链、日期分歧及未核文献的限定；不新增候选、mention、statement或正式关系边。严格阶段审计通过，卡片预检无待写文件。全量同步闭合本批复核通过9/9检查，303 passed、2 subtests；结构契约130/130、关系一致性错误项为0，git diff --check退出码0（Git提示LF/CRLF转换）。当前全库双端statement已分类4,897/8,500（57.6%）；下一段为chp-2:02_CHP-2_sec_vii:l3-3，1条待裁决。恢复副本、SHA和逐条记录见过程记录。

## 第二章第VII节 L3–36 关系分类（2026-10-10）

对照印刷pp.58–61（PDF物理pp.47–50），48条待分类双端statement均按原文关系语义标记为S2候选。保留跨页评价、相对日期、匿名群体、肖像版本、未定人物指代和作者推断的限定；无候选、mention、statement或端点增删，也未生成S6正式关系。写后严格表审计通过、卡片预检无待写回文件。当前全库双端statement已分类4,945/8,500（58.2%）；下一段为第三章导言L7–9，1条待裁决。
