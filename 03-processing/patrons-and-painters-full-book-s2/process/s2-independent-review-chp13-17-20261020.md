# 第13–17章及结论、附录 S2 独立语义复核记录

更新：2026-10-20。状态：进行中。此记录按当前工作树逐条复核 S2；源表、候选表与知识卡保持只读。未逐条审完的章节/附录不作接收结论。`s2-coverage.csv` 的 complete/reviewed 仅为迁移状态，不等于本次语义验收。

## 方法与当前游标

对照 `02-sources/02-Markdown/` 登记分节、`04-knowledge/tables/segments.jsonl`、statement/mention 当前行与对应 PDF；逐条检查 claim、原子性、主客体端点类型及方向、`mentioned_candidate_ids`、说话者/文本层、时间/语气/来源限定、开放端点和 `relation_candidate`。编号顺序以章节及印刷页/源行排序，不以 statement ID 字符串排序。历史复核数须由当前版本核实后才计入覆盖。

| 范围 | 当前总量 | 本记录逐条语义复核 | 未覆盖 | 状态 |
|---|---:|---:|---|---|
| 第13章正文 `13_CHP-13_intro.md` | 559（true 390 / false 169） | 559/559；先前批次1–439，本批440–559；当前定位 p.332 L6 至 p.346 L176 | 0 | 不接收；有下列未修问题 |
| 第13章 plates visual transcription | 20（true 20） | 20/20；4个视觉转录段，plates 57a–60 | 0 | 不接收；statement 有来源 mention 锚点缺口及一处端点类型错误 |
| 第14章正文 `14_CHP-14_intro.md` | 502（true 314 / false 188） | 502/502；p.347–364及未分页caption；正文、注释与图版caption均逐条复核 | 0 | 不接收；有下列未修问题 |
| 第15章（3个分节文件） | 551（true 434 / false 117） | 551/551；p.361–372，正文至 p.372 L88、注释至 L113 | 0 | 全章不接收；有下列未修问题 |
| 第16章 `16_CHP-16_intro.md` | 210（true 133 / false 77） | 206/210；p.373–378；新增4条S2端点statement未计入复核分子 | 4 | 不接收；有下列未修问题 |
| 第17章（3个分节文件） | 142（true 96 / false 46） | 142/142；folio i、p.380–383 | 0 | 不接收；有下列未修问题 |
| 结论 `18_CHP-18Conclusion.md` | 24（true 14 / false 10） | 24/24；p.384–385 | 0 | 不接收；有下列未修问题 |
| 附录 `19_CHP-19Appendix.md`及receipt visual transcription | 116（true 82 / false 34） | 116/116；p.386 L3 至 p.395 L208 | 0 | 不接收；有下列未修问题 |

第13章累计覆盖 579/579。此次复核快照哈希：`book-statements.jsonl` `a3379b08ef8323b8e2b169c80bc138641729917fd378de6380500f4ae58d678d`；`mentions.csv` `0de98420707e874d4828467b6177680ad41428cadf77aa22bffd9d1d60e1e3ee`；正文源 `13_CHP-13_intro.md` `c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8`；视觉转录源 `13_CHP-13_intro_plates_visual-transcription.md` `73d5fad85a4b84f11508ef0cad9590bded516b69ed2ce203dc3afaf3079906bd`。复核后哈希若变化，须对差异行重新核对，不能沿用本覆盖数。

### 2026-10-23：第16章 p.373 注2定向修复补记

补录John Strange在注2源段的两处局部mention（segment字符270–277、483–490），并将印本所见 `Correr` 记录为OCR `Cotter` 的校读。另新增四条书信发信人/收信人原子statement，服务于已确定S3身份组的S4登记和S6裁决；这四条是定向增补，不属于本独立复核记录的审阅分子。因此第16章记录为206/210，整章仍不接收，原有待修项继续有效。

## 第13章待修发现

下列 statement 均已对照正文转录；主要页码为书内印刷页，L 为源文件行。建议去向是待写回的表/元数据，不代表本代理已修改。

| Statement ID | 锚点 | 当前问题 | 建议去向 |
|---|---|---|---|
| `st-chp13-p332-publishers-european-ties-and-patronage` | p.332 L6–7 | 一条断言合并欧洲联系与艺术赞助，当前 publisher→Europe 端点无法表达“赞助与国际品味相协调”。 | 拆分/改写为两个有据的广义主张；不要以 Europe 地理候选代替赞助对象。 |
| `st-chp13-p332-conditional-lax-censorship` | p.332 L7 | 原句“and this helped”承接较宽松审查制度；当前 subject=Venetian publishers、object=Venice，主客体均不对应其指代。 | 改为制度/审查语境的宽泛因果表述，或保留开放端点。 |
| `st-chp13-p332-copyright-effects-on-local-and-export-books` | p.332 L10–11 | 20年垄断对威尼斯本地书籍质量下降与英/法/德市场奢华版获益两项结果被合为一条；当前垄断→出版社不覆盖结果端点。 | 拆开本地市场和出口奢华版结果，使用来源支持的书籍类别或不强配端点。 |
| `st-chp13-p334-bossuet-interest-and-heresy-context` | p.334 L29 | “对 Bossuet 兴趣复起”被映为 Bossuet 人物直接关联异端传播，错把人物作为兴趣主体。 | 使用“兴趣/接受”类概念作主项或保持无实体关系断言。 |
| `st-chp13-p334-albrizzi-member-and-guardiano-at-san-rocco` | p.334 L28 | 将成员地位和“晚年成为 Guardiano”合在一项。 | 拆开成员与职务任命/担任，保留 late-life 时间限定。 |
| `st-chp13-p335-bossuet-audience-central-europe-monasteries`；`st-chp13-p335-illustrations-for-central-european-readers` | p.335 L33–34 | 原文说插图帮助读者理解 Bossuet 著作；predicate “intended for”将受益/效果升级为预定用途。 | 改为“帮助/使……易于理解”，保留 archbishops 与富裕修道院的对象范围。 |
| `st-chp13-p335-piazzetta-monopoly-and-cooperation` | p.335 L33 | 近乎垄断与合作留下印记两项事实压在一个 Albrizzi→Piazzetta 端点下。 | 分别表达 Albrizzi 对 Piazzetta 插图工作的近乎垄断及双方合作的出版影响。 |
| `st-chp13-p335-gerusalemme-1745-edition-and-patronage-climax` | p.335 L35–36 | 合并赞助高潮、Haskell 的“最著名”评价和1745出版事实，当前仅建出版端点。 | 拆分出版事实与作者评价/赞助解释；“最著名”明确归于 Haskell。 |
| `st-chp13-p335-piazzetta-pastoral-compositions-boucher-comparison` | p.335 L37 | 当前只记录与 Boucher 的比较，漏掉“Piazzetta 的世界不那么人工化”的对比限定。 | 扩展或拆分评价，同时保留比较语气。 |
| `st-chp13-p336-zais-pictures-shown-at-1770-exhibition` | p.336 L49 | 原文是把两幅画带到展览；predicate `shown_at` 超出“taken to”的可证事实。 | 改为“带至展览”，不推定公开展出。 |
| `st-chp13-p337-goldoni-promised-increased-production-attention`；`st-chp13-p337-goldoni-said-paper-and-printing-economised` | p.337 L57–58 | “commercial”一词与后续 “My dear friend, I reply…” 才是原文明确引号；节纸/印刷和“更多关注”是 Haskell 的间接叙述，不是 Goldoni 直接引语。 | 将说话者/文本层改为 Haskell 转述 Goldoni；注6仅定位至1761序言，未独立查阅。 |
| `st-chp13-p337-note1-lodoli-influenced-publishers-booksellers` | p.337 n.1 L203 | 正文说 Lodoli 影响 publishers and booksellers，statement 的 `mentioned_candidate_ids` 漏掉 publisher 候选 `cand-2068`。 | 补齐该候选的 mention 映射；泛称 booksellers 不补造身份。 |
| `st-chp13-p338-novelli-over-hundred-drawings-reproduced` | p.338 L63 | 原文为 Goldoni 版需要百余幅图、由刻工复制；当前以 Novelli 绘图项目为主语、Goldoni版为宾语，主客体/谓词方向不合。 | 以该版为主项，指向绘图组/数量范围；刻工未具名，不补身份。 |
| `st-chp13-p337-pasquali-employed-piazzetta-for-officium` | p.337 L57 | predicate “employed Piazzetta”但 object 为 *Officium* 作品；人物 Piazzetta 只在 mention。 | 以 Piazzetta 人物为受聘端点，作品保留为委托语境或 reify 委托。 |
| `st-chp13-p338-pasquali-dedicated-vignola-edition-to-lodoli` | p.338 L65 | dedicated-to 的宾语当前为 Vignola 版；原文受赠/题献对象是 Lodoli。 | Lodoli 作受赠对象，版次作上下文；补核相应 mention。 |
| `st-chp13-p339-zatta-range-of-illustrated-books` | p.339 L75 | 断言范围大致正确，但 object `cand-2068` 是 Venetian publishers，不是 Zatta 涉及的图书类别。 | 更换为合适的书籍类别，或去掉无关端点。 |
| `st-chp13-p339-note6-pinelli-catalogues` | p.339 n.8 L216 | statement ID/说明称 note 6，但来源印刷脚注号是8。 | 修正脚注编号、ID/注释链接所指；保留书目题名的 OCR 校读。 |
| `st-chp13-p340-canaletto-drawings-depicted-principal-ducale-ceremonies`；`st-chp13-p340-canaletto-drawings-intended-for-engraving-by-brustolon`；`st-chp13-p340-furnaletto-commissioned-twelve-canaletto-drawings-in-1766` | p.340 L87 | 三项所述主体均为12幅 Canaletto 图纸组，现用 `cand-0503`（Canaletto 人物）代替作品组；事件、描绘和预定雕版关系因此错端点。 | 建立/使用有证据支持的图纸组；不补造组名或单幅身份。 |
| `st-chp13-p341-zanetti_bought_arundel_parmigianino_drawings` | p.341 L93 | 宾语 `cand-0142` 是 Lord Arundel 人物，predicate 暗示从其购买；原文是购买 Arundel 所藏 Parmigianino 图纸。 | 用已提及图纸组 `cand-10066` 作宾语；不推断卖方。 |
| `st-chp13-p344-delle_antiche_statue-scholarship` | p.344 L117 | “subordinated fantasy…”承接 Zanetti 的创作；当前主体是书/档案候选 `cand-10104`，把出版物当行动者。 | Zanetti 作行动主体；书作为内容/语境，或重述为书中呈现的命题。 |
| `st-chp13-p344-dactyliotheca-catalogue` | p.344 L117 | claim 说 Zanetti 自己的收藏，但 `mentioned_candidate_ids` 漏掉同一行已有 mention `m-s2-ch13-p344-008` 对应 `cand-2838`。 | 补入人物候选；collection 候选 `cand-10113` 类型未定，应保留 S3 边界待决。 |
| `st-chp13-p344-zanetti-1752-incomplete_letter_fragment`；`st-chp13-p345-zanetti-1752-quote-continuation` | p.344 L121、p.345 L162 | Zanetti 引文被映射为意大利全境 patrons/amateurs；Haskell 紧接明确限定“The situation was Venetian rather than Italian”。 | 让 Zanetti 引文范围对应 Venice/Venetian 语境；保留跨页同一引文，Haskell 的修正单独归属。 |
| `st-chp13-p345-monaco-collection-advertised-dealer`；`st-chp13-p345-monaco-pittoni-works-reproduced`；`st-chp13-p345-monaco-three-works-reproduced`；`st-chp13-p345-monaco-tiepolo-works-reproduced`；`st-chp13-p345-monaco-patronage-interpretation` | p.345 L167 | “the plates / such a collection”指代较宽的 Monacо 收藏/版组；当前几条一律绑定1763 edition `cand-7618`，但来源没有把广告、全部复制作品或推测赞助身份限定为该版。 | 指向收藏/系列组或保持具体版次开放；保留 “almost certainly”“might well” 的推测语气。surface mention `m-s2-ch13-surface-baf7da19399563b6` 也不应单选1763版。 |
| `st-chp13-p345-toni-adviser-and-patron-to-novelli`；`st-chp13-p345-toni-patron-of-novelli`；`st-chp13-p345-toni-collections-left-to-novelli-1748`；`st-chp13-p345-toni-discussions-may-have-shaped-novelli` | p.345 L169–170 | Novelli 端点 `cand-1760` 类型为作品（Pasquali/Goldoni 插图组），不是人物；“may have”因果语气需保留。 | 改用已有人物候选 `cand-1758`；两条 Novelli mention (`m-s2-ch13-p345-049`, `-051`) 与注3作者 `manuscript_author_candidate_id` 一并更正到人物。 |
| `st-chp13-p344-plate57b-attribution` | plates 57b 源 L3 | caption attribution 的 Novelli 也错映射至作品 `cand-1760`。 | 改为人物 `cand-1758`；caption 仍只作为图版署名事实。 |
| 20条 plates visual transcription statements | plates 57a–60，各caption源 L1–14 | 4个视觉源段均已读取，但 `mentions.csv` 没有这些 caption 源段的局部 mention 行；statement 里的 ID 列表不能代替精确 mention 锚。`cand-10114` 有视觉 L2 candidate_source_ref，却在 mention 表无对应记录。 | 补局部 mention/source anchor，或明确复用前置 List of Plates mention 并记载精确链接；维持视觉转录声明与正文断言的区别。 |

## 第14章全文复核（p.347–364及未分页caption）

当前逐条游标：p.364 L166及未分页caption末项；全章502/502均已逐条复核（true 314 / false 188 的全章机械计数不代表语义通过）。源文按印刷页与源行排序；另核对注释和图版视觉转录、对应PDF。第14章源表/源文未改。以下发现跨此前批次汇总；“其余审读行无实质缺陷”仅指本次所查语义，不等于全章可接收。

| Statement ID | 锚点 | 当前问题 | 建议去向 |
|---|---|---|---|
| `st-chp14-p347-education` | p.347 L9 | claim 并入罗马一年教育、1726年后博洛尼亚学习及学科；当前仅结构化到 Bologna，Roma 段没有分别表示。 | 拆分两个教育地点/阶段；分别连到 Rome、Bologna，保留“父亲去世后”和1726年时间限定。 |
| `st-chp14-p348-palladio-quote-and-prussia` | p.348 L17 | 把 Algarotti 1732年写信称赞 Palladio 与后来的 Prussia 传播“崇拜”合在一个谓词/端点中。 | 拆分原信评价及后来的传播主张；保留各自时间、说话者和 Haskell 叙述层。 |
| `st-chp14-p348-raphael-titian-bartolommeo` | p.348 L18 | 比较 Raphael 的 *St John the Baptist* 与 Bologna 的 *S. Cecilia*；结构只链接 `cand-10242` 一个作品。 | 增补第二作品端点或将两件作品作为有据比较组；不要只留一侧。 |
| `st-chp14-p349-correspondence-and-theoretical-influence-canaletto`；`st-chp14-p349-correspondence-and-theoretical-influence-tiepolo` | p.349 L32 | 复合“给艺术家写信”与“理论著作改变艺术意见气候”两事，当前 predicate 和人物端点将后一项收窄成对各画家的直接影响；source qualifier 已承认个体影响未单独证实。 | 拆成明确通信边与环境/意见变化的作者解释；后者不建立直接 artist influence，保留 ill-health 时间及 Haskell 归属。 |
| `st-chp14-p351-crespi-omission-and-later-praise` | p.351 L51 | 一个谓词把 Crespi 未列入1742年画廊方案与 Algarotti 后来特别称赞他并列为同一关系。 | 拆成当时遗漏和后来的评价，分别保留时间顺序与 Haskell 对“later”来源的注释。 |
| `st-chp14-p354-algarotti-attracted-to-tiepolo-brio-fantasy` | p.354 L81 | 原文对象是 Tiepolo 艺术中的 brio/fantasy，当前 relation object `cand-3781` 是 Tiepolo 本人；claim/谓词不是说 Algarotti 被 Tiepolo 本人吸引。 | 改指有据的艺术/风格对象，或保留开放端点；不要把对作品特质的评价写成对艺术家的直接关系。 |
| `st-chp14-p355-algarotti-internationalist-dilemma` | p.355 L88 | 同一 claim 合并 Algarotti国际主义/外部联系、以新标准衡量Tiepolo、赞赏Tiepolo并劝其节制诗性幻想，predicate只用“平衡国际与威尼斯取向”。 | 拆成作者的艺术立场与对Tiepolo的评价/劝告，分别保留Haskell归属和限定。 |
| `st-chp14-p355-royal-commissions-lost` | p.355 L89 | 合并皇家委托作品已经失佚与赞助影响仍可从其他同期作品看出两项。 | 拆为失佚事实和影响解释，后者保留其他作品的来源范围。 |
| `st-chp14-p355-algarotti-piazzetta-ownership` | p.355 L90 | 合并 Haskell 对 Algarotti 未特别欣赏 Piazzetta 的评价与他拥有一幅小画的事实。 | 分开保留评价和所有权事实；所有权对象仍为具名小画/有据作品组。 |
| `st-chp14-p355-piazzetta-classical-works` | p.355 L90 | 合并“古典历史画不合 Piazzetta 才能”、Algarotti委托后另有两幅同类作品、总计仅三件三项。 | 分拆艺术评价与作品数量/委托时间；总数仍限于来源说的 Piazzetta oeuvre。 |
| `st-chp14-p355-no-evidence-of-algarotti-canaletto-contact` | p.355 L94–95 | 一个 claim 把“本次访威期间无接触证据”“德累斯顿Canaletto作品似乎未由Algarotti经手”“无证据显示他写过送画意图”三项压入单一谓词；`relation_candidate=true` 也与 p.352 对“no evidence of contact”设为 false 不一致。 | 拆分三个来源限定主张；保留 `no evidence`/`seems`，均不写成发生了联系或明确的不存在关系；关系分类按各拆分行的语义判断。 |
| `st-chp14-p356-adviser-frederick-berlin-arts-plans` | p.356 L100–101 | claim 说 Algarotti 同时是 Frederick 与其 courtiers 的顾问，但结构对象仅为 Frederick。 | 把 Frederick 的已知端点与未具名 courtiers 群体拆开；若无合法群体端点，后者保留开放范围或将 claim 收窄至 Frederick。 |
| `st-chp14-p358-directed-pesci-from-rough-sketches`；`st-chp14-p358-directed-tesi-from-rough-sketches` | p.358，源文对应 L118–119 | claim 写 Algarotti 指导 Pesci/Tesi 依草图作画，但当前对象端点为草图组，画家仅为 mention，不能表示指导/受指导的两端。 | 以画家人物作受指导端点，草图组作创作语境；如谓词无法表达则拆为指导事件，补齐人物候选映射。 |
| `st-chp14-p358-flemish-painter-selected-subjects` | p.358，源文对应 L120–121 | 原文将 subject 选择归于 Algarotti、绘制者明确为未具名 Flemish painter；当前端点仅表达 Algarotti→subject group，且 `mentioned_candidate_ids` 漏掉同段未具名画家候选 `cand-10381`。 | 将“选题”与“由 Flemish painter 绘制”分开；补入画家 mention，绘制 claim 采用可用的人物/开放端点。 |
| `st-chp14-p358-piranesi-parallel-and-admiration` | p.358，源文对应 L122 | 把 Piranesi 与 Algarotti 的相似处及 Algarotti 对其作品的赞赏合并；一个关系不能保留比较和评价两层。 | 拆分比较判断与 Algarotti 的赞赏，保持来源评价层及其具体作品/风格对象。 |
| `st-chp14-p359-note4-gabbrielli-general-discussion` | p.359 n.4，源 L217 | 脚注谈 Gabbrielli 1938、1939 年研究，但 p.359 正文相邻段落没有可见上标4；p.360 的脚注4是 Leslie，不能据编号相同跨页挂接。 | 保留为未锚定脚注/来源待证项；检查原版版面或更完整底本前，不将其链接到 p.359 任一 claim，也不连接 p.360 note4。 |
| `st-chp14-p360-constable-studied-works` | p.360，源文对应 L141–143 | claim 说 Constable 研究 Algarotti 的作品，当前 object `cand-0050` 是 Algarotti 人物，不是作品。 | 使用有证据支持的 Algarotti 著作/作品组；若无法确定具体作品，采用作品类开放端点并保留复数范围。 |

该批其余已读statement的主体/端点大体与本段原文对应；`st-chp14-p349-stay-between-venice-and-milan` 与 `st-chp14-p349-brief-visit-1760` 已显式保留来源未给出的地点端点和 `open_endpoint_reason`，不将两者当成错误，也不擅自补定地点。 p.349 法国洛可可影响 statement 保留 “must have been powerful” 的 Haskell 推测；不当成已证因果。

截至 p.353 L71 逐条核读66条（p.352 31条、p.353 35条），新增未修实质发现0。PDF phys.6 校读证实 p.352 “previous stay in Venice in 1737”后为上标注2；S0 OCR 的 `1757?` 已由 `st-chp14-p352-no-evidence-prior-venice-contact` 的 `ocr_corrections` 正确记录为 `1737.²`，statement 的“no evidence”限定和注2链接亦正确。`st-chp14-p353-bruhl-possessions-in-the-pictures` 的 endpoint虽留空，但 qualifier说明原文未将两件物与两幅画逐一配对，并列出两幅画候选问题及 p.354 续文；该开放端点处理符合证据边界，不作为缺陷。

截至 p.357 L116 / 注 L207 再核读147条（p.354 28、p.355 27、p.356 34、p.357 58），该段新增7项待修发现；其余审读行未发现足以阻断的主体、端点、限定或来源锚不一致。p.356 的 `st-chp14-p356-veronese-for-walpole-conditional-1738` 已明确引用 note 4 的价格条件并留有“未证实购买/交付”的限定；note5的 Lazzarini 两画分别保留 Fantuzzi 对 Frederick 的报告与 Haskell 根据后续信件/库存提出“可能为 Algarotti 而非国王”的相反推测，未静默消解冲突。

随后核读 p.358–360 的83条，再核 p.361–364 与未分页视觉caption的8条，至全章502/502。新增或确认以下问题：p.358 的 Pesci/Tesi 指导关系将画家漏作端点；“未具名 Flemish painter”候选 `cand-10381` 未列入 `mentioned_candidate_ids`；Piranesi 比较与赞赏复合；p.360 Constable claim 把“Algarotti 的作品”映为 Algarotti 人物。p.359 n.4 Gabbrielli 是未锚定来源项，未擅自与 p.360 note4 合并。图版 statement `st-chp14-p361-heading-algarotti-impact`、`st-chp14-p361-plate61-version-sequence`、`st-chp14-p362-plate62-depicted-site`、`st-chp14-p362-plate62-site-in-padua`、`st-chp14-p362-plate62-canaletto-caption`、`st-chp14-p363-plate63-cerato-caption-fragment`、`st-chp14-p364-plate64-view-of-villa`、`st-chp14-p364-plate64-guardi-caption` 与图版转录和PDF实物版面相符；p.363 源转录确为跨页裁切片段，完整题名仅由 List of Plates 另行提供，未把外部补全冒充转录原文。未发现这8条新增语义缺陷。第14章全量已读但不建议接收：本表所列端点、复合断言、遗漏 mention 与脚注锚定问题仍需修订/待证处理后复核。

## 第15章当前批次（p.361–367）

当前逐条游标：p.372 L88及注释L113；已复核551/551条（p.361 31、p.362 52、p.363 41、p.364 46、p.365 40、p.366 56、p.367 49、p.368 47、p.369 54、p.370 60、p.371 59、p.372 16）。分章依 `segments.jsonl.chapter`、`source_file`、当前表 segment_id 和印刷页字段映射，不按 ID 前缀推定。第15章三份源文件的当前内容哈希：`15_CHP-15_intro.md` `015d35e467ad4cca8a4029d62aeb9469e49b4619e8c0c6916f46b0e0e019830b`、`15_CHP-15_sec_i.md` `798e2903ab45c8a90ac5be9746c43964007426d3b2e2723baa20332665d11624`、`15_CHP-15_sec_ii.md` `eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f`。本批逐项对照了当前 statement/mention/candidate 行、登记分节与相应来源文字；PDF physical pp.3–7用于核对印本字词、页间接句及脚注。此前页级处理脚本和 stages 过程记录只用于定位，不计独立接收。

| Statement ID | 锚点 | 当前问题 | 建议去向 |
|---|---|---|---|
| `st-chp15-p361-new-history-painters-imitation` | p.361 L5–6 | 原文是“new generation of history painters”这一未尽列群体（仅以 Fontebasso、Zugno、Guarana 举例）在增加的内容中几乎只有模仿；当前端点把 Fontebasso→Zugno 当成该谓词两端，claim 又提及 Guarana，无法表示原断言主项/判断对象。 | 用来源限定的画家群体及其继承/模仿判断，或保留开放对象；若拆分具名人物，只保留原文确实分别归属的事实，不把比较对象写成人物端点。 |
| `st-chp15-p361-guardi-unknown-to-great-patrons-different-public` | p.361 L7 | 同一 statement 将“几乎不为大赞助人所知”与“服务于完全不同的公众”两项判断压入单一谓词；great patrons 与 different public 都未具名。 | 拆分两个评价/受众主张，保留 `virtually` 与 Haskell 的后文指引；受众端点若无合法候选则开放或只保留断言。 |
| `st-chp15-p361-tiepolo-no-desire-to-return-to-italy` | p.361 L4–5 | claim 再次写入“Tiepolo 当时在 Spain”，但这已由相邻 `st-chp15-p361-tiepolo-in-spain-no-desire-return` 单独建模；本条 predicate 只表达不想回 Italy，`mentioned_candidate_ids` 又漏掉 claim 中的 Spain 候选。 | 将 claim 收窄至“无意返回意大利”，把在西班牙的地点事实只保留于对应独立 statement；或明确添加 Spain mention 并说明其只是情境，避免重复成双重事实。 |
| `st-chp15-p361-men-encouraged-revival-venetian-painting` | p.361 L12 | 原文“these men”前指未定；当前主语为空、对象为复兴term、`relation_candidate=true`，但未写 `open_endpoint_reason`，也没有可追溯的主项候选。 | 保留明确开放主项理由，或使用来源限定的未具名群体候选；不得从临近提及者拼组名单。 |
| `st-chp15-p361-enlightenment-different-patronage-partial` | p.361 L13–14；续 p.362 L17 | 将启蒙如何进入威尼斯、少数杰出人士显示的新赞助可能性、他们转离绘画三层含在一条中；当前 term→term 主客体把作者原句改写成启蒙直接提出赞助，`relation_candidate=false`，且“转离绘画”与 p.362 独立 statement 重复。 | 原位保留 Haskell 对新赞助可能性的解释，拆出群体转离绘画的后续陈述；按来源句法判断是否建立 term/群体到赞助实践的关系，避免重复claim。 |
| `st-chp15-p362-farsetti-family-rich-and-patrician-status-1664` | p.362 L17 | claim 同时声称出身家庭“极富”与1664才获得贵族身份；当前谓词只编码取得身份。 | 拆分财富评价与身份/时间断言；保留 `exceedingly`、`only` 和来源主体是家庭而非 Filippo 的限定。 |
| `st-chp15-p362-lodoli-direct-inspirer-of-three-patrons`、`st-chp15-p362-lodoli-direct-inspirer-of-farsetti`、`st-chp15-p362-lodoli-direct-inspirer-of-memmo`、`st-chp15-p362-lodoli-direct-inspirer-of-querini` | p.362 L17 | 来源明确说 Lodoli 是“本章三位 patrons”的直接启发者；聚合行将 `relation_candidate=false` 且无对象端点，随后拆成三条 true关系。拆分 Memmo/Querini依赖章节标题而非本句局部名称，`mentioned_candidate_ids` 仍只有本句出现的 Lodoli/Farsetti。 | 统一聚合与拆分行的关系分类及证据链；明确三人 referent resolution 是依章节结构解析的群体指代，确保派生出的两条个体 claim 不伪装成局部 mention。若保留标量边，保留父 statement 与章节标题证据的可追溯链。 |
| `st-chp15-p362-few-contemporaries-in-paintings` | p.362 L22 | 原文说绘画收藏中仅少数同代人被代表，除不可避免的 Zuccarelli；当前端点直接是画家人物，可能将“收藏有其作品”错误简化为“收藏代表画家本人”。 | 若断言对象是收藏中的画作，改用 Zuccarelli 作品/有据作品组或表达“作品由该画家创作/归属”；保留 `few` 与 `apart from`，不能推造画作数目。 |
| `st-chp15-p362-country-villa-wings-and-pavilions` | p.362 L24 | claim 包含主楼、连接翼楼及两端 pavilion 三类组成，但关系只接主楼与 pavilion；候选 `cand-12219` 的 lower wings 未进入端点。 | 拆成主楼—翼楼—pavilion 的部件关系，或把翼楼作为显式中介并保留“两层/两端”限定。 |
| `st-chp15-p363-farsetti-said-spent-million-ducats` | p.363 L28；PDF physical p.3 | 一条 claim 合并据称花费百万杜卡特装饰别墅、几乎使家族破产、以及令同时代人大为惊叹三层；当前端点只连接 Farsetti 与 villa。S0 OCR `Iris family` 与PDF印本 `his family` 不同，statement claim 已改作“his family”但当前未见相应 `ocr_corrections` 证据。 | 拆出支出、家族影响、同时代反响；在该 statement 的校读记录注明 L28 `Iris`→`his`、CHP-15.pdf physical p.3，不把被动/传闻语气改成经证事实。 |
| `st-chp15-p363-garden-columns-temples-towers` | p.363 L28–29；PDF physical p.3 | 原文“its great botanical rarities… and it was decorated”跨“gardens / house itself”后，末尾 `it` 指代不够明确；当前直接把柱、庙、塔归于 gardens。 | 核对原页更完整上下文或保留指代开放；不要在无法确认时把装饰对象固定为花园。 |
| `st-chp15-p363-palace-centre-for-classical-model-theories` | p.363 L32；PDF physical p.3 | 原文说 palace 是“all those who were absorbing”相关理论者的中心，当前对象却是 theories；把参与者群体转成理论本身作为中心对象。 | 用来源限定的学习者/吸收理论群体作对象，或保留开放端点；把 Algarotti 等人的理论保留为背景，不将此行与下一条理论归属混为一谈。 |
| `st-chp15-p363-daniele-cousin-amateur-painter` | p.363 L35；PDF physical p.3 | 一条 claim 合并 Daniele 与 Filippo 的 cousin 关系、1725–1787生卒年和业余画家身份；谓词也并列了多种属性。 | 分出亲属、日期与身份断言，保留来源语气；OCR的年份连字符校正已在qualifier说明。 |
| `st-chp15-p365-padua-authorities-request-fair-assistance` | p.365 L8；PDF physical p.5 | 原文只称“municipal authorities”；当前主体是跨章候选 `cand-8406`（Padua civic body），身份/职能并不等同于本处的具体未具名 authorities，且 claim 仍明确说其未具名。 | 保留为来源限定的市政官员群体或明确开放主体；若继续复用 `cand-8406`，S3需证明其与本处 authorities 同一，不能从城市地点直接推为市政府。 |
| `st-chp15-p365-dealers-needed-suitable-stall-site` | p.365 L8；PDF physical p.5 | claim 是为交易商摊位找“合适地点”的规划需要；当前是 fair event→dealers endpoint，没有表示所需地点/筹备事项，且本句后文紧接唯一可见候选地点 Prà marshland。 | 表达待定摊位地点的规划需求事件；核对是否可由下句 Prà 地点承接，但不得把未明确边界写成实际摊位已设。 |
| `st-chp15-p365-memmo-reclamation-canal-island` | p.365 L8；PDF physical p.5 | 一条 claim 把避免洪水、收复 marsh、建 canal、中央 island供商人使用合并；当前仅 Memmo→Prà地点，缺少 canal/island及计划状态的分解。 | 拆为有计划限定的土地整治、运河与中央岛设计/用途；分别使用现有或待证端点，不把决定和设计写成竣工事实。 |
| `st-chp15-p365-statues-as-civic-virtue-gallery` | p.365 L9；PDF physical p.5 | 原文谓 statues 将作教导 civic virtue 的 public gallery，并称该目的符合 Enlightenment opinion；当前 endpoint 是 Enlightenment term，predicate/claim却把它当“教导 civic virtue”的对象，未结构化 civic virtue。 | 将雕像系列/计划与 civic virtue 教化目的表达清楚；Enlightenment opinion只保留为来源限定背景，不能充当 civic virtue endpoint。 |
| `st-chp15-p365-memmo-representation-eligibility-partial` | p.365 L11，续 p.366 L15 | claim 列出两种可被代表者：贵族及给城市带来特别荣誉者；当前端点仅有贵族，第二类被放在 `open_endpoint_reason` 而未作为可追踪端点。 | 可保留第二类别的明确开放端点并建立待证候选，或拆为两类资格声明；不要把“被塑像者”与后续“有权以自己名义献像者”混作一条。 |

本批其余已读行未发现足以报告的 claim 原意、日期/语气限定或脚注链接缺失。p.362 四座现代雕塑已逐项连到各自雕像；收藏、临时Padua建造计划、S. Maria di Sala别墅、42根立柱及注释分别建模，未把书内引证当作已独立核验的事实。PDF physical pp.3–5确认脚注和statement中的多处校读；`st-chp15-p363-farsetti-regular-allowance-to-algarotti`、`st-chp15-p363-daniele-continued-patronage-partial`、`st-chp15-p364-tommaso-embittered-by-nephew`、`st-chp15-p364-contemporaries-hoped-cultural-revival`、`st-chp15-p364-memmo-learned-chaste-architecture` 与 p.365 的多个OCR校正均已结构化记录。唯一在本批已确认但需补校读依据的是 `st-chp15-p363-farsetti-said-spent-million-ducats` 的 `Iris`→`his`。以上为暂定的语义读数；本章尚未完整，不作接收结论。


### p.366–367 逐条复核（105条）

已逐条核对 p.366 的56条与 p.367 的49条，包括注释 statement；对照 `15_CHP-15_sec_ii.md` 对应段落、当前 mentions/candidate 映射及 PDF physical pp.6–7。下列两项不建议接收：

| Statement ID | 锚点 | 当前问题 | 建议去向 |
|---|---|---|---|
| `st-chp15-p366-subleyras-plans-displayed` | p.366 L20，源段 `l14-28`；PDF physical p.6 | claim 将 Memmo 把 Subleyras plans 挂在寓所与贵族/杰出访客在那里欣赏两项事实合在一起；predicate 和端点只表达 Memmo→plans 的展示，未将欣赏者作为行动主体。相关群体 mention 已存在于当前候选映射中，故问题是关系/断言结构未表达，不是 mention 缺失。 | 展示 statement 保留 Memmo→plans/寓所；另以来源定义的贵族与杰出访客群体表达对 plans 的欣赏，或说明受众仅为原文语境而不作为 formal relation。不要补推个人身份。 |
| `st-chp15-p367-note4-memmo-friends-citations` | p.367 n.4，源段 `l90-113` L96；PDF physical p.7 | claim 同时记录 Molmenti《Un nobil huomo》pp.143–144 与 Torcellan (1963) 作为 Memmo 友人通信例证的指引；同一行 endpoint 只指向 Molmenti（`cand-10475`），`mentioned_candidate_ids` 也没有 Torcellan（`cand-10476`），而独立的 `st-chp15-p367-note4-cites-torcellan-1963` 已另行记录后半条指引。 | 将本行 claim/quote 范围收窄到 Molmenti；让 Torcellan 独立 statement 保持其 citation endpoint 与 mention。两条只表示 Haskell 的书目指引，不表示已独立查阅或证实引文内容。 |

p.366 的 `st-chp15-p366-pope-and-visitors-contribute` 未发现缺少 Pope mention：claim 中未具名 Pope 对应 `cand-10493`，该候选已在 `mentioned_candidate_ids`，且 mentions 中有 p.366 L21 “the Pope” 的精确锚。p.367 对 Canova statue、Ferrari 作者、Venier 委托对象、Skala/Veith 备选方案、日期与推测语气的分项表达均与源文相符；不将最初疑虑误记为问题。其余本批语义读数未发现足以报告的主体/端点方向、限定或来源锚错误。**当时本批结束时**全章尚有236条未审，故该批不作接收结论；其余部分已在本记录后续段落复核。


### p.368–372 逐条复核（236条；第15章完成）

已逐条核对 p.368–372 正文及至 p.372 n.1 的 statement，并按 `segments.jsonl.chapter`、登记 `source_file`、`segment_id`、印刷页与局部 mentions 映射；PDF physical pp.8–12用于核对原文与 OCR 校读。对应 `s2-coverage.csv` 各正文/注释分节标为 reviewed/complete，但该迁移状态只说明内部归档，不构成本次语义接收。当前 statement/mention 表哈希仍为本记录基线（statement `a3379b08ef8323b8e2b169c80bc138641729917fd378de6380500f4ae58d678d`；mentions `0de98420707e874d4828467b6177680ad41428cadf77aa22bffd9d1d60e1e3ee`）。新增一项待修：

| Statement ID | 锚点 | 当前问题 | 建议去向 |
|---|---|---|---|
| `st-chp15-p370-querini-study-daphnis-chloe-print-series` | p.370 L62；`chp-15:15_CHP-15_sec_ii:l61-67`；PDF physical p.10 | claim 同时称 Daphnis and Chloe 版画组存于 Querini 书房并“意在舒缓其过度劳累的心绪”，但 subject/object/predicate 只表达版画组 `located_at` 书房；后半是来源明确的设计目的，当前无独立断言/目的端点。相关 Querini、版画组和书房候选均已 mention。 | 位置 claim 保持 `print group → study`；另记“版画设计用于舒缓 Querini 心绪”的作者报告，必要时以目的/功能开放端点表示，避免把意图写成经证实效果；或将本行 claim 收窄至位置并把目的另行保留。 |

p.368–372 其余已读行的端点类型/方向、原文时序与推测限定总体相符。特别核对：p.368 “private life”及 `confmed` 校读依据已在 `st-chp15-p368-querini-private-art-public-interest` 以 PDF physical p.8 记录；p.369《Dei delitti e delle pene》的 `dette`→`delle` 校读已记录于对应 statement，且“rumour”未升级为作者身份事实；p.370 两位设计/雕刻者、Bacon 与 Lodoli 的两项断言及 Young’s Wood/Night Thoughts 候选拆分均已有独立行；p.371 De Non→Novelli 的 principal-pupil 关系与 Rembrandt prints 对两者的不同影响已分开；p.372 将 Renier 折衷、Querini投掷胸像、Querini心脏而非全身的安葬及脚注中的推测性胸像认定保留各自语气。未发现其他足以报告的新增错配。第15章虽已全量复核，但 p.361–367 与 p.370 的未修项仍阻断接收。

## 已完成与未决边界

本次实际读取了第13章正文p.332–346所有559条statement、4个plates视觉转录段及20条statement；正文对应21个登记段（20个正文段、1个排除标题段），视觉转录另4段。PDF抽查包括 p.337、p.343–345 及 physical pp.14–17 plates captions。上述段落状态/迁移 complete 不构成语义接收。当前建议第13章不接收：端点错配、statement 复合范围、来源说话者和局部mention锚仍需处理并复核；collections/plate groups 与未具名 engraving groups 等边界待 S3 判定。

## 第16章全文复核（p.373–378；206/206）

### 覆盖与版本

按 `segments.jsonl` 的 `chapter=chp-16`、登记 `source_file=02-sources/02-Markdown/16_CHP-16_intro.md` 逐条映射；除生成文件标题排除段外，已核读7个正文/注释分节中的206条statement。印刷页计数：p.373 42、p.374 39、p.375 27、p.376 43、p.377 51、p.378 4；范围覆盖正文、注释以及跨页续句。对照S0全文和 `mentions.csv`，并视觉核读 `CHP-16.pdf` physical pp.1–6。S0哈希 `ee8516e7868b0036a753da731e10a7e201faafa45314615b45ae024c6c7507ff`；本次检查时 statement/mention 哈希分别为 `a3379b08ef8323b8e2b169c80bc138641729917fd378de6380500f4ae58d678d`、`0de98420707e874d4828467b6177680ad41428cadf77aa22bffd9d1d60e1e3ee`。`s2-coverage.csv` 将7个内容分节标为 reviewed/complete，只证明迁移/内部记录状态，不构成语义接收。

### 不建议接收的具体项

| Statement ID | 原文锚点与当前不一致 | 建议修订/去向 |
|---|---|---|
| `st-chp16-p373-lower-status-men-and-their-painting-attracted-little-attention` | p.373 L8；claim同时说低社会地位的人及他们欣赏、鼓励的绘画在当时少受注意，但唯一subject是 `cand-11543`（Haskell所述“Venetian art tradition”术语），并将两类对象压入一条predicate。 | 分开记录人物群体与绘画类型；现无具名/列举群体时保持开放端点，不用艺术传统术语代替主体。 |
| `st-chp16-p373-patron-taste-distinct-from-venetian-tradition` | p.373 L8，原文 `tbe taste ... bore little relation to ... tradition`。当前subject只有传统候选 `cand-11543`，claim却比较新赞助人推动的趣味与既有传统；两侧未完整建模。该行也没有记录S0 `tbe`→PDF `the` 的校读。 | 将新趣味和传统作为两个比较项，必要时保持抽象项开放；在相应statement的 `ocr_corrections` 记录 physical p.1 的 `tbe`→`the`。不要将传统单独充作全部claim的subject。 |
| `st-chp16-p373-note2-strange-sasso-letters-in-epistolario`；`st-chp16-p373-note2-sasso-replies-mostly-missing`；`st-chp16-p373-note2-mauroner-quotes-letters`；`st-chp16-p373-note2-four-sasso-letters-british-museum`；`st-chp16-p373-note2-sasso-wrote-four-letters-to-strange` | p.373 n.2，源段 `chp-16:16_CHP-16_intro:l69-89` L71。各行 `mentioned_candidate_ids` 含 John Strange (`cand-2517`)，但该注释段的 `mentions.csv` 没有 Strange 的局部mention；原注明确出现“letters from Strange to Sasso”及“from him to Strange”。 | 在注释源锚补录 Strange 的精确mention；不能用正文p.373 L12的同名mention替代注释行锚。 |
| `st-chp16-p374-strange-pictures-list-and-custody`；`st-chp16-p374-refine-picture-sale-qualification` | p.374 L17；当前复用 `cand-2367`（候选表明为Sasso替J. Strange购画的event），但“the pictures / These pictures”指代的是画作集合；后者还把event列为mentioned候选，`mentions.csv` 在p.374段没有此局部mention。 | 将购画event与画作组分开；不把event当作品组。必要时为未逐件列举的画作组保留开放候选/端点并补足指代mention；sale行继续保留“sold—or would have been”的反事实，不推断交易已完成。 |
| `st-chp16-p374-refine-picture-storage` | p.374 L17，claim称这些画作暂存于Strange的Treviso乡间住宅“或”伦敦寓所；当前两端点均空，未有对应画作组候选/mention。其 `open_endpoint_reason` 已准确记录组未列举、地点为二选一，不应误报为错误确定端点。 | 保留该开放状态；若需可追踪映射，给“These pictures”补明确的来源级作品组mention并连接至p.373购画上下文，勿复用event `cand-2367`。 |
| `st-chp16-p374-strange-collects-guardi-and-venetian-colour` | p.374 L20；一条关系claim并入Strange欣赏Guardi、拥有其多件作品、偏爱威尼斯色彩/brio、与伦敦/巴黎/罗马新潮及新古典作品疏离；同页已有分别表达这些点的statement，当前端点却只为Strange→Guardi。 | 收窄至Guardi欣赏/所有权，或去除冗余汇总行；其余趣味、地域比较和新古典态度留在已拆分的对应statement中。 |
| `st-chp16-p375-strange-introduces-worsley-to-sasso` | p.375 L26–27；原文关系为Strange把介绍信交给Sasso，以介绍继任者Worsley；claim又并入信中对Sasso品味及寻作能力的赞语。现端点Strange→Worsley没有表示信件交付的收件人Sasso。 | 拆出Strange→Sasso的交信/介绍事件及信中关于Worsley、Sasso的内容；保留“信由Haskell转述、未直接查阅”的来源限定。 |
| `st-chp16-p375-sasso-finds-works-for-worsley` | p.375 L27–28；主体关系是Sasso替Worsley找到作品，但同一claim又称Worsley随后将一件Guardi作品送给Lady Palmerston；当前端点只有Sasso→Worsley。 | 保留找作品statement；另建Worsley→Lady Palmerston的赠与/呈献断言，Guardi作品未具名则保持开放。 |
| `st-chp16-p375-sasso-reputation-and-removal-of-masterpieces` | p.375 L28–29；同一claim合并“英国商人依赖Sasso的信任与知识”及Haskell称其工作导致大量杰作离开城市的评价；subject仅Sasso、无作品端点，`relation_candidate=false`，无法呈现这两种不同范围。 | 拆分依赖关系与Haskell关于作品外流的集体解释；未具名商人/作品和交易继续作为来源级开放端点，不将Haskell评价升级为独立证实的因果事实。 |
| `st-chp16-p375-della-lena-moschini-friendship-and-records` | p.375 L30；Della Lena→Moschini friendship关系claim同时称Moschini是拯救许多威尼斯记录的古物学家；predicate和端点只表示友谊。 | 友谊关系与Moschini保存记录的断言分开，后者以Moschini为主体；记录不具名时不补造对象身份。 |
| `st-chp16-p375-della-lena-life-and-venice-office` | p.375 L31；一个predicate/端点把Della Lena在威尼斯居住大半生、任西班牙副领事、1807年在此去世并作一条Della Lena→Venice关系。 | 拆为居住时段、未定任期的职务及死亡日期/地点；保留任职日期未明，不把副领事塑造成另一个已识别实体。 |
| `st-chp16-p375-della-lena-private-collection-and-guardi-paintings` | p.375 L33；claim涵盖几件Canaletto、未具名小画家作品及32幅Guardi画，object却只有 `cand-10623`（32幅Guardi组）。 | 把整体收藏与32幅Guardi子组的范围分开；不要让Guardi子组代表全部收藏。Canaletto及其他作品仍按原文未具名范围处理。 |
| `st-chp16-p376-vianello-dealer-and-picture-catalogue` | p.376 L41；claim只说Haskell不确定Vianello是否经销商，当前object却链接其1790年目录 `cand-10630`；目录作为依据已在独立的disposal-inference行出现。 | 从dealer-uncertainty行移除目录端点；将目录仅留在“目录出版→Haskell推测愿意出售藏品”的对应statement。 |
| `st-chp16-p376-vianello-artists-and-preferred-works` | p.376 L42；claim只列Rosalba、Ricci、Piazzetta、Tiepolo的作品；predicate却追加“偏好素描及半身像”，该信息另在 `st-chp16-p376-vianello-sketch-and-bust-preference` 表达。Ricci仍只能按姓氏保留未决身份，当前 `cand-10645` 注释已注明该边界。 | 将本行predicate收窄至作品组；偏好只保留在单独statement。Ricci不因相邻段落而强行选定Marco或Sebastiano。 |
| `st-chp16-p376-swajer-biography-and-manuscripts` | p.376 L46；一个predicate把德国商人/富裕身份、在威尼斯居住大部分时间及1792年在此去世并列；`relation_candidate=false`。 | 拆成身份/职业、长期居住及带年份的死亡/地点断言；保留来源仅提供有限传记信息。 |
| `st-chp16-p377-swajer-inquisitors-conclusion` | p.377 L49，续p.376 L46；原文是“可能散佚”使国家宗教裁判官感到焦虑。当前subject却是Swajer (`cand-2534`)，而claim明确把反应归于Inquisitors；可能散佚的事件也未表示。紧随其后的获取全部手稿statement已另行记录。 | 将受影响主体改为Inquisitors候选 `cand-10524`，或以可能散佚事件作开放主项；保持“possible”以及“anxiety”，不要与随后取得手稿的事实合并。 |
| `st-chp16-p377-swajer-in-touch-with-gian-domenico-tiepolo`；`st-chp16-p377-canova-painted-swajer-portrait` | p.377 L49–50；Gian Domenico联系行的claim又包含Giambattista（另有独立联系行）；同句还明说Swajer与Canova有联系，但当前只有Canova为他作肖像的statement，未覆盖contact主张。 | Gian Domenico行收窄到Gian Domenico；保留Giambattista独立行；另记Swajer与Canova联系，不能用“Canova画肖像”自动替代接触关系。 |
| `st-chp16-p377-celotti-tiepolo-friendship-as-catalogue-wording` | p.377 L56–57；法文 `Tiepolo, son ami` 被建成Celotti→Tiepolo friendship。就本句结构，`son ami`最直接回指前文“cet habile Peintre”（Canaletto）；它位于称四幅Canaletto画作及其人物的目录语句中，不能据此确认Celotti与Tiepolo为友。 | 不保留Celotti→Tiepolo身份关系。复核法文指代；若按Canaletto回指，则把友人关系候选指向Canaletto；若上下文仍不足，保留目录用语及未决，不作人物关系裁决。 |
| `st-chp16-p377-celotti-four-canalettos-with-tiepolo-figures` | p.377 L56–57；predicate/端点是四幅Canaletto作品附有Tiepolo人物，claim却还包括目录对构图、描绘/执行的评价。 | 将目录审美评价和“Tiepolo人物丰富四幅画作”的作品关系分开；评价继续归于1807目录引文，不转成已独立核验的作品属性。 |
| `st-chp16-p377-haskell-infers-celotti-salesmanship-and-taste` | p.377 L56；predicate写入salesmanship与taste相似两项，但claim只陈述与较朴素商人相似的个人趣味；salesmanship已有独立行。 | 从本行predicate去掉salesmanship范围；保持Haskell明示的推论与“部分较朴素商人”的未枚举范围。 |

其余逐条核读行未发现足以另行报告的断言方向、身份类型或来源限定问题。特别核实p.374 `hot`→`not`校读已在 `st-chp16-p374-strange-drawing-instructions-via-sasso` 有physical p.2依据；p.376 `Pietrp`→`Pietro`、`alia`→`alla`、`tnodelli`→`modelli`均有physical p.4校读；p.377 Swajer焦虑句已校正S0逗号，且p.377 body marker 6与footer note 5不一致已显式标为mismatched，未强行链接。p.378三条“they”群体综合断言的 `referent_statement_ids`/候选均回指p.377所列六位商人，限制为Haskell群体综合，未外推成每人的正式关系。

本章当前结论：206/206已逐条核读，建议不接收；以上问题需修订并重新核对。第13、14章虽已读完但各有未修问题；第15章551/551已读完但存在未修问题，均不建议接收。**当时阶段快照**：尚未复核范围为第17章142条、结论24条、附录116条，共282条；这些范围已在本记录下文逐项完成，当前覆盖以文末累计段为准。旧审阅状态不替代本次核读。

## 第17章全文复核（folio i、p.380–383；142/142）

### 覆盖、版本与游标

按 `segments.jsonl` 的 chapter/source_file 及当前 statement 的 segment/source_file 映射复核三份登记 S0：`17_CHP-17_intro.md`（8条，SHA `5252c5d3f0a9b52661b0e95d7a12c6f51aef46a6e7faa391794b356da7043e66`）、`17_CHP-17_sec_i.md`（66条，SHA `cbcb4e8f0eb163564f0b0c8e060c79f1a48981db45072a772c3ea16642ad3ca4`）及 `17_CHP-17_sec_ii.md`（68条，SHA `d23af9f50ab9ac84fb250f5c7c5c260908096616ca83773a647977b8e07f4ff3`）。按印刷定位逐条覆盖：folio i 28、p.380 30、p.381 33、p.382 31、p.383 20；当前 statement 哈希 `a3379b08ef8323b8e2b169c80bc138641729917fd378de6380500f4ae58d678d`、`mentions.csv` 哈希 `0de98420707e874d4828467b6177680ad41428cadf77aa22bffd9d1d60e1e3ee`。对应 PDF physical pp.1–5 已视觉核读。游标至 p.383 n.1 L30 / statement `st-chp17-p383-note1-ridotto-attribution`；逐条核对原文、当前predicate/端点、mentions 与 qualifier。登记范围没有第17章 plates visual-transcription 源文件；第13章的20条 plates visual transcription（plates 57a–60）在本记录前文已另列20/20，不能计入第17章正文计数。

### 未修发现与建议去向

| Statement ID | 原文锚点及问题 | 建议修订/待证去向 |
|---|---|---|
| `st-chp17-pi-feeling-reached-patrons-and-collectors`；`st-chp17-pi-feeling-affected-patrons-collectors` | p.379 folio i L4。第一条原文仅称时代感受在政治演说和文学中“countless references”；谓词扩大到艺术收藏，候选 `cand-4129` 是前置目录术语而非此处有界的赞助人/收藏者群体。第二条把该感受对 patrons and picture collectors 的影响也挂到同一术语候选，缺少来源限定群体端点。 | 第一条收窄为Haskell对文本中反复提及该感受的概述；第二条另保留未具名的 patrons/picture collectors 群体或开放端点，不以目录主题词替代源文群体。 |
| `st-chp17-p380-painters-portraits-volume-followed` | p.380 L11。原文只说1785版后两年出现一册画家肖像集；subject `cand-1513` 为 Manfrin collection，不能充当该出版序列的主项；版本候选虽在mention中但未用于表达先后关系。 | 以1785版与未具名1787肖像卷的出版序列/间隔表达；若未确认卷名及版本身份，保持来源级未具名端点。 |
| `st-chp17-p380-manfrin-delegated-picture-selection` | p.380 L14–15。引文明确由 Manfrin 委托 Edwards 与 Sig. Gio. Battista Mingardi 挑选、鉴定和剔除画作；当前关系端点只列 Manfrin→Edwards，Mingardi `cand-1670` 仅在 mentions 中。对 letter 的局部提及也未作为该 statement 的 mention 呈现。 | 把 Mingardi 纳入共同受托端点/群体，并核对 letter mention 与本地源锚；保留这是 Haskell 引述 Manfrin 私信、原信未独立查阅的限定。 |
| `st-chp17-p381-correr-portrait-traits` | p.381 L3。这里是 Haskell根据肖像推断 Correr “elegant and rather withdrawn”；当前 Correr→portrait 关系候选容易将人物特征解释写成正式人物—肖像关系，虽 qualifier 已正确声明是肖像解释且 `relation_candidate=false`。 | 保持为带说话者限定的肖像解释，不转成形式关系边；portrait→sitter 识别事实留在独立 statement。 |
| `st-chp17-p381-manfrin-competitions`；`st-chp17-p381-competitions-aroused-history-painters` | p.381 L24。`cand-0817` 是索引抽出的 generic term “Competitions”，但本段指 Manfrin 所组织、以其自拟主题的画家竞赛（事件/活动），并称其令缺少委托的历史画家群体感到振奋。 | 把泛词候选与本处事件/实践区别；使用来源限定事件或保持开放。历史画家群体仍未具名，不枚举成员；不可推断竞赛画作已完成。 |
| `st-chp17-p381-correr-republic-context`；`st-chp17-p383-correr-acquired-after-republic-collapse` | p.381 L3、p.383 L22。候选 `cand-8572` 为威尼斯共和国政治实体；“downfall/collapsed”在两句中是终结事件/时间背景，而不是 Correr 所关联/购画对象。 | p.381 将政治实体与其终结事件分别表达；p.383 将共和国崩溃作为获取画作的时间限定，不建成购画关系宾语。保留共和国身份与S3对齐待裁决。 |
| `st-chp17-p382-correr-longhi-and-view-painters` | p.382 L13。把 Correr 对 Pietro Longhi 纪实场景的兴趣，与 Haskell 认为他未关注风景画家“奇怪”的解释并成一条 Correr→Longhi 关系。 | 分开收藏/兴趣陈述与对未关注风景画家的作者评述；两项均保留 Haskell 归属，后者不制造具名画家群体。 |
| `st-chp17-p382-correr-awareness-of-venice-change` | p.382 L13。原文 `It almost seems` 是 Haskell 对 Correr 心态的推测；predicate 又并入“因为城市景观未变、生活方式变化所以不收藏风景画”的因果解释，超出该句明确猜测的内容。 | predicate 限定于带“almost seems”的推测；删去或另行表达原因/不收藏主张，不能写作 Correr 自述动机。 |
| `st-chp17-p383-note1-parlatorio-attribution`；`st-chp17-p383-note1-ridotto-attribution` | p.383 n.1 L30。原注称两件画在1859年由Lazari编为Longhi作品，但Correr时代被认为是Guardi作品。当前两条分别使用Guardі为客体，虽claim说出两套历史归属，却未将“Lazari目录归属”与“Correr时代归属”分别作为来源/时期限定的竞合判断呈现。 | 对每件作品分别表示两种有归属来源与时间的历史判断；不把候选作者当唯一已解决作者。被引目录与研究未独立查阅，保留来源层边界。 |

其余核读行未发现需要报告的新增实质错配。PDF physical pp.1–5 对 `Ffeeling`→`feeling`、p.381 competition主题及 p.383 `i960`→`1960` 的校读支持均已结构化记录；“apparently”、`it almost seems`、引文说话者以及未具名群体限制不得从claim中删除。第17章142/142已覆盖，但以上问题尚未修订，不建议接收。本批未改 statement、mention、candidate 或知识卡。

## 结论全文复核（p.384–385；24/24）

### 覆盖、版本与游标

按已登记的 `18_CHP-18Conclusion.md` 两个内容分节及当前 statement `segment_id` 核读 p.384 14条、p.385 10条；游标至 p.385 L23 / `st-chp18-conclusion-p385-bourgeois-painting-no-roots-in-italy`。源转录 SHA `a3d40952beead96ac48136610fa3fa15f1dcdfcd1a354ef9f2c2262343aeff14`；核对 `CHP-18Conclusion.pdf` physical pp.1–2。当前 `book-statements.jsonl`、`mentions.csv` 哈希仍为本记录前述值。逐条检查了24条statement的断言、谓词、端点、mentions、限定与说话者；`Mme Geofirin`→`Mme Geoffrin` 的校读已有对应 statement 及 PDF 依据。该范围已完整逐条审读，但以下问题阻断接收。

### 未修发现与建议去向

| Statement ID | 原文锚点及问题 | 建议修订/待证去向 |
|---|---|---|
| `st-chp18-conclusion-p384-artists-serving-patrons`；`st-chp18-conclusion-p385-opportunities-and-patrons` | p.384 L7、p.385 L22。两条把原文“great patrons / liberal patrons”作为关系端点使用 `cand-4129`；该候选来自书目目录的 LoC subject heading “Art patrons”，不是这两处分别定义的来源群体。 | 使用局部来源定义的“great patrons”及“liberal patrons”群体候选，或开放端点；不要把目录主题词当作本段人物/群体身份。保留仅为群体层级主张、未指明具体 patron–artist 对的限定。 |
| `st-chp18-conclusion-p384-social-demands-and-originality` | p.384 L10–11。predicate把“社会要求压埋新颖艺术路径”的作用挂在 `cand-3461` Italy（place）上；原文是讨论 Italian art 中的案例，Italy只是地理/文化范围，不是施压行动者。claim还含“天赋偶然分布”的可能解释及寻找超出 `national character` 的论证转折。 | 改为来源定义的艺术实践/社会要求概念之间的主张，或保留开放断言；将 Italy 作为语境限定，不作行动主体。保持 Haskell 的假设与论证层级。 |
| `st-chp18-conclusion-p384-bamboccianti` | p.384 L11。claim/predicate描述 Bamboccianti 由接近新现实主义转向田园感伤主义；object `cand-10735` 是“意大利艺术与文学中的社会顺从”概念，并非该转向的结果端点。 | 移除该概念作为对象；如有来源定义的 sentimentality 端点可使用，否则把轨迹写为来源层陈述。段落把它用作 conformity 的例证可保留在解释语境，不将语境误作关系目标。 |
| `st-chp18-conclusion-p384-crespi-and-medici-prince` | p.384 L11–12。一个predicate/statement合并 Crespi 带动一位未具名 Medici 王子，以及 Crespi 未放弃其幽默、未提升 genre painting 地位两项判断；当前端点仅 Crespi→王子。 | 拆分王子与 Crespi 的相互影响描述和关于 genre painting 的作者评价；保留王子身份未定及 Haskell 评价语气，不能从后文 Grand Prince Ferdinand 倒推身份。 |
| `st-chp18-conclusion-p385-no-specific-pressure-or-doctrine` | p.385 L20。当前一条含三项：上文所述艺术家没有因具体压力偏离路径；意大利没有正统学院或主导宗教组织施加艺术教条；“unorthodoxy was killed with kindness”的总结判断。 | 拆成对应的来源层断言，保留前两项的全称否定范围与第三项修辞/解释语气；无具名机构或压力来源时保持开放，不从概括句补出实体。 |
| `st-chp18-conclusion-p385-france-england-and-fall-of-venice` | p.385 L23。单条statement把法国、英国绘画随教会和封建贵族衰退而重获发展，与威尼斯陷落象征意大利艺术屈辱性终结两种地域判断合并；谓词/端点 Venice→Italy无法完整表达前半句及其时间、因果范围。 | 拆为法国/英国绘画变化与威尼斯陷落/意大利艺术终结两项；将教会及封建贵族衰退保留为来源限定的时代背景，不泛化为单一主体。 |

其余核读项的候选提及总体能够回到本段局部mentions；历史人物身份、匿名社会群体以及“may have / surely / almost any”限定均保留为 Haskell 的论断或评价，不作为外部验证事实。`st-chp18-conclusion-p384-lodoli` 的未具名政府职务虽无 object ID，但 `open_endpoint_reason` 已明确说明职位与任命政府均未给出，因此接受其开放状态、不列为缺陷。结论24/24已审，以上问题未修前不建议接收；本批未改源表或知识卡。

## 附录全文复核（p.386–395；116/116）

### 覆盖与版本

逐条核对登记 S0 `19_CHP-19Appendix.md`、分节登记及当前 statements/mentions；附录 receipt visual transcription `19_CHP-19Appendix_p386_receipt_visual-transcription.md` 单独对照 `CHP-19Appendix.pdf` physical p.1。附录正文按印刷页覆盖 p.386 8条、p.387 14条、p.388 9条、p.389 7条、p.390 10条、p.391 9条、p.392 10条、p.393 27条、p.394 12条、p.395 10条；总计116条（82 true、34 false），当前游标至 p.395 L208 / `st-chp19-p395-manfrin-letter-closure-and-signature`。PDF physical pp.1–10均已视觉核读。p.386 receipt 转录的8 Mar 1676签名及收据开头在physical p.1得到核实；该来源对应附录当前2条statement，不与第13章plates visual transcription的20条混算。附录 S0 SHA `725dc16a2983bec379ce2a8b608542ab3defe348d2b2f2a336632ac4905388f1`；receipt视觉转录 SHA `4fa4f3d98471fbdaff06490217fee4a416e71ee8b1df9385c5b279846c3be550`；PDF SHA `2a1c29e6c2864527482d231a85c4252e55524b436ae4dff5b0d55d9d5a67a9eb`。当前 statement/mention 表哈希分别为 `a3379b08ef8323b8e2b169c80bc138641729917fd378de6380500f4ae58d678d`、`0de98420707e874d4828467b6177680ad41428cadf77aa22bffd9d1d60e1e3ee`。本复核只检查 Haskell 转录及其PDF印本文字；引述的档案和研究文献未独立调阅。

### 未修发现与建议去向

| Statement ID | 原文锚点 | 当前问题 | 建议修订/待证去向 |
|---|---|---|---|
| `st-chp19-p386-appendix-archive-locator` | p.386 L5–6；PDF physical p.1 | 标题中的 Carlo Maratta 人名表面在局部 mention 映到 `cand-1532`（archive，指S. Andrea祭坛画档案候选），而人物候选 `cand-1533` 为 Carlo Maratta。 | 将人名 mention 指向人物候选；档案仍可作为本行 locator 的对象。维持S3对人物身份/映射的裁决边界，不以档案候选代替人物。 |
| `st-chp19-p387-maratti-1679-advance`；`st-chp19-p387-maratti-1679-promise-and-refund-terms`；`st-chp19-p387-maratti-1687-final-payment` | p.387 L26–32；PDF physical p.2 | S0转录写 Carlo Maratti，但印本收据签名可见 Carlo Maratta，与页眉“Receipts signed by Maratta”一致。当前三行沿用 OCR 字形作为签署人，未记录这处校读差异。 | 在各自 source locator 记录 Maratti→Maratta 的印本校读；保留签署人为人物的候选映射待S3，不因异拼建立/合并新身份。三条分别保留1679预付款、附条件承诺与1687最终收款/完工自述。 |
| `st-chp19-p387-orsini-letter-model-transfer` | p.387 L38；PDF physical p.2 | claim 合并“Bernini将Madonna模型交给写信人”与“写信人次晨将模型带给Giacomo Ant:o并留下”；当前端点只表达写信人→Giacomo Ant:o，未表达Bernini→写信人的转交。 | 拆为两段交接或把模型交接重构为有角色的事件；保留未知写信人/收信人边界及第二次交付的既有约定，不补造身份。 |
| `st-chp19-p387-orsini-letter-model-handle` | p.387 L39；PDF physical p.2 | claim说需要把模型固定于可手持的柄/接头，但当前 object `cand-10780` 是“Modello della gioia”模型，柄候选 `cand-10778` 仅为mention，端点对象类型与原文关系不符。 | 把模型和手柄分别作为端点（或将安装关系保留为开放的制作/装配断言）；保留 OCR `Manichette` 与印本似为 `Manichetto` 的校读及词形不确定性。 |
| `st-chp19-p388-c140-portrait-and-caster-praise` | p.388 L50–51；PDF physical p.3 | claim同时称 Bernini肖像令Duke满意、铸工Bastiano Sebastiani希望展示勤勉与技艺；当前端点只表达 Bernini→Duke 的肖像关系，遗漏铸工的独立动机。 | 拆开肖像及满意度报告、铸工的自我展示意愿；后者以铸工为主体，保留由Pedini转述且Duke在信中未具名。 |
| `st-chp19-p388-c173-cast-result-and-instructions` | p.388 L56–57；PDF physical p.3 | 一个predicate把铸件成功/表面评价与Bernini命令铸工仅切除浇口、不得再锉削两项行动并列，主客体不一。 | 拆为Pedini所报告的铸造结果及Bernini对铸工的加工指令；保留“reported by Pedini”与未经独立评价的来源限定。 |
| `st-chp19-p388-c173-foundry-and-transfer-request` | p.388 L57–59；PDF physical p.3 | 合并铸造地点、铸工可能因邻近祭坛工程而抗拒搬运的推测、Pedini请求Duke下令移至Bernini住所；请求没有证据表明已执行。 | 分开地点事实、可能的阻力与未完成的移送请求；保留 `might/could` 不确定性，不能将请求改写成已转移。 |
| `st-chp19-p388-c463-baldi-recommendation` | p.388 L62–63；PDF physical p.3 | Bernini请求写信人陪同Baldi，并向Duke权力推荐Baldi；当前端点只表示Bernini→Duke，缺写信人、Baldi及不同请求角色。 | 拆分陪同请求和推荐，或将请求建模为包含请求者、受托者、受益者的事件；保留未证明陪同完成、Baldi仅为私人事务赴行。 |
| `st-chp19-p389-franceschini-subject-options` | p.389 L78–81；PDF physical p.4 | object `cand-7801` 是档案信件，predicate/claim实际表达 Franceschini 为画作提出的多项备选题材；不能把信件当题材端点。 | 以来源明确的主题/备选组或开放端点表示；信件只作为证据锚。保留选项并列、`Tona [sic]`及未选定/未完成状态。 |
| `st-chp19-p389-giuseppe-reports-felice-trojan-subject` | p.389 L82–84；PDF physical p.4 | 句中是 Giuseppe 向 Marchesini 报告，选择题材的行动者则是其兄 Felice；当前主体是 Giuseppe，predicate说他报告Felice已找到题材，关系候选容易将报告者当选择者。 | 以Felice为题材选择主体，另保留Giuseppe为报告者/说话者；或将claim明确限定为Giuseppe报告Felice的选择。题材尚属拟议，不表示已完成绘画。 |
| `st-chp19-p390-ricci-small-picture-figures` | p.390 L94；PDF physical p.5 | 当前claim正确保留“Ricci画小画中的人物，其他部分由风景画家完成”，但一条复合作者断言包含不同作品部分及作者；“the others”的对象范围原文未明。 | 若结构化，拆分人物与其余部分的作者主张；继续保留“the others”指代不明，不因第8章交叉引用把所有其余部分都指定给某一画家。 |
| `st-chp19-p390-ferdinand-received-crates` | p.390 L98；PDF physical p.5 | 收到两只箱子及其作品内容，与Ferdinand命令把Canon Marucelli的两幅sfondi交付给Canon合并；当前object为Ferdinand→画作组，不表达交付目的地/收件人。 | 将箱件到达/内容与后续交付拆分；第二项明确Canon Marucelli为收件方。保留小画作者未明、作品映射待S3及所引信件语境。 |
| `st-chp19-p390-crespi-claims-small-picture` | p.390 L102；PDF physical p.5 | 将不明人士所称Tintoretto作与Crespi自称亲笔两项竞争作者判断纳入一个Crespi→画作关系。 | 分开有明确来源/说话者的前述归属与Crespi自我归属；两者均为信中报告，不据此裁定作品作者。 |
| `st-chp19-p391-smith-1761-will-and-collection-classes`；`st-chp19-p391-smith-1761-expectation-and-1762-sale` | p.391 L122–124；PDF physical p.6 | `cand-2476` 是索引抽出的 will archive 候选、S3未决；`cand-8651` 是Smith遗嘱文本候选。当前statement使用遗嘱/文件作为Smith的行动主体或重复的will端点，不能充分表达Smith、遗孀与收藏类别的角色。 | 分开遗嘱文本作为来源、Smith的愿望、遗孀获准售藏及Smith对类别保持完整的期望；遗孀不具名。保留该引述经Haskell转述、遗嘱未独立调阅。 |
| `st-chp19-p391-smith-1762-sale-to-george-iii` | p.391 L117–118；PDF physical p.6 | 一条claim合并1762售出大量绘画/素描、现藏于Royal Collection、Smith编目及作品可辨认/可追踪等交易与后续目录/馆藏性质。 | 保留“very large number”而不补精确数量；交易与Royal Collection现状/编目/可辨识性拆分。避免把编目与交易说成同一个关系。 |
| `st-chp19-p392-smith-1761-relocation-and-reports`；`st-chp19-p392-adam-1760-financial-report`；`st-chp19-p392-smith-disposal-and-purchase-inferences`；`st-chp19-p392-moschini-conflicting-widow-account`；`st-chp19-p392-post1762-source-scarcity-and-inference`；`st-chp19-p392-volpato-1766-letter`；`st-chp19-p392-smith-1768-letter-dealing`；`st-chp19-p392-smith-conditional-gennari-collection-offer` | p.392 L128–138；PDF physical p.7 | 该源段明确出现Smith人名（其中Volpato OCR为“Smit”），但这8行无对应局部的 `cand-2447` Smith mention；当前使用/叙述Smith的行需局部可追溯锚。 | 为明示人名处补本段局部mention并关联相应statement；首人称书信或前句代词若无本行人名，则用稳定的referent/source cross-reference，不能伪造文本mention。保留Venetian reports、James Adam转引、Moschini冲突说法、Volpato信和Haskell推论各自的来源/推测层级。 |
| `st-chp19-p392-transition-only-certain-knowledge` | p.392 L126–127；PDF physical p.7 | “That is our only certain knowledge”是承接前文Smith的指代句；不应为了把Smith列为mentions而声称该句有局部人名表面。 | 保持断言指代与p.391内容的referent/source链接；不添加不真实的局部文本mention。 |
| `st-chp19-p393-smith-own-collection-remark` | p.393 L147–148；PDF physical p.8 | 一条claim合并Smith关于类似收藏无法再建立的引语与Haskell对其1762年所得£20,000的评论；两处说话者/命题不同。 | 拆分Smith引述和Haskell评论，保留各自说话者与引证层；金额留在Haskell原文表述范围。 |
| `st-chp19-p393-zais-and-1762-sale-uncertainty` | p.393 L144–146；PDF physical p.8 | 同行合并Haskell报告Zais曾为Smith工作且其画未出现在1762年售画中，与两种竞争解释（英国代理未选其画，或Zais在1762年后才为Smith工作）。 | 把来源报告与Haskell的开放问题/备选解释分开；两种解释均不裁为事实，作品与时间边界保留待证。 |
| `st-chp19-p393-smith-1768-letter-continuation` | p.393 L141；PDF physical p.8 | 一条statement合并买主减少、市场上有画/版画待售、Smith买入若干、未来可能给通信者观看等不同时间和行为；购买并不必然为Smith自藏。 | 分开市场描述、已报告的购买和将来可能展示；保留未知收信人及条件语气，不推断购买用途。 |
| `st-chp19-p394-memmo-sheet-source-and-date`；`st-chp19-p394-memmo-liberal-arts-query`；`st-chp19-p394-c-veneziano-exemption-query`；`st-chp19-p394-professional-tax-comparisons`；`st-chp19-p394-academies-and-associates`；`st-chp19-p394-terra-ferma-academies`；`st-chp19-p394-paris-academy-privileges-and-teaching`；`st-chp19-p394-academy-emblem-name-query`；`st-chp19-p395-academy-secretaries-status` | p.394 L157–183；p.395 L189–191；PDF physical pp.9–10 | Appendix 6文书标题在p.394明确提 Andrea Memmo，但本地segment内相关statement所用 `cand-1642`/`cand-9857` 缺此文书/人物mention锚；p.395 continuation转入新segment，亦无本地表面。另 `Così del Diretore` 可表示“Director也同样查询”，不能单独证明该Director在世。 | 在p.394记录文书标题和Memmo的本地source mention；p.395续页使用前页文书的稳定跨segment referent，不伪造本地文字mention。秘书的“in vita”保留为原文明确答案；director状态记录为延续的查询/含混内容，不升级为已确认在世。 |
| `st-chp19-p395-manfrin-selection-criteria-and-experts` | p.395 L199–201；PDF physical p.10 | Manfrin委托Edwards与Gio. Batta Mingardi共同选择、鉴定并剔除画作；当前端点只列Manfrin→gallery，选择专家只在mentions中，未作为行动角色表示。 | 将Edwards与Mingardi明确建为共同受托选择者/事件角色；保留这是私信中委托及判断标准，不表示画作已选、购入或入藏。 |

上述问题覆盖端点角色/类型、复合断言、来源说话者、mention锚点与OCR校读；各statement均已逐条对照，但本附录仍有未修项，故不建议接收。作品身份、档案原件、引述研究及匿名写信人等不能由本次转录审阅解决的事项继续标为S3未决或待证，不据此补造事实。

## 当前累计与未覆盖范围

截至本次记录，当前表版本已逐条核读第13章正文559条及20条plates visual transcription、第14章502条、第15章551条、第16章206条、第17章142条、结论24条、附录116条，累计 **2120/2120**；按当前分配范围没有剩余statement未审。第13–19章各范围均有待修/待证项，均不建议接收。第13章plates转录与附录receipt转录是不同来源，分别计20条和附录内2条，不重复计数。当前总表哈希为 `book-statements.jsonl` `a3379b08ef8323b8e2b169c80bc138641729917fd378de6380500f4ae58d678d`、`mentions.csv` `0de98420707e874d4828467b6177680ad41428cadf77aa22bffd9d1d60e1e3ee`。后续如哈希变化，仅对受影响差异行重核，不沿用旧版本覆盖数。本次只写入本审阅过程记录，未修改源文、statement、mention、candidate或知识卡。
<a id="s2-repair-chp15-p370-daphnis-print-series-20261022"></a>

## 2026-10-22：p.370 Daphnis and Chloe print-series 复合 statement 定向修复

针对上表记录的 `st-chp15-p370-querini-study-daphnis-chloe-print-series`，回读第15章 p.370 L62 及 CHP-15.pdf physical p.10。将原 claim 限定为“版画组在 Querini 书房”，新增 `st-chp15-p370-querini-print-series-intended-to-lighten-mind` 单独记录“设计用于舒缓其过度劳累的心绪”。新 claim 保留 Haskell 的目的语气，不推论实际效果。因该版画组 `cand-10549` 仍无稳定身份边界，且无精确受控谓词表达目的，相关五条S6候选均记 pending；不建系列KU，不改 S3 `undecided`。此项是对已覆盖段的定向修订，不增加独立复核计数；p.361–367仍有待修/复核项，故第15章不接收。

逐项 S4/S5/S6 记录见[知识过程](knowledge.md#s3-s4-s5-s6-chp15-cabane-inscription-huber-20261022)。
