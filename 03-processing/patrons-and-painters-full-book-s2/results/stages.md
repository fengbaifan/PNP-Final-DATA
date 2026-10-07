# 全书语义处理（S2）逐段结果记录

任务ID：`patrons-and-painters-full-book-s2`。本文件按源段保存已完成的语义阅读结果和局部裁决，不维护全书总状态或工作游标；当前范围、计数、未决项及下一步唯一见[全书S2当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。操作过程和判断依据见[过程记录](../process/stages.md)。

## 第十章印刷页324正文（2026-10-03）

对照`CHP-10.pdf`物理第57页处理`chp-10:10_CHP-10_sec_ii:l194-201`，新增1个候选（`cand-9777`，`term`）、16条精确提及和15条原书statement。记录Pascoli对Bamboccianti的早先论述、Gozzi比较Guido Reni/Cerquozzi与Tiepolo/Longhi、其对Longhi写生的评价及Haskell关于Longhi优于Tiepolo的推断。随后按文学寓言而非传记事实记录Gozzi故事中的哲人、图像、乡村生活和劳动者尊严；未把寓言中的画家、房屋、藏画或交易指认到现实对象。未名劳动阶层按类型`term`暂存为开放候选，不臆定其成员或正式名称。

页图校读仅记入S2、不改S0：印本页码应为324（OCR标记`[Page 24]`）；`hambocciafiti`校为`Bamboccianti`；`it is”still`校为`it is still`；`foreshortened, figures`删除误逗号；`country Use`校为`country life`。p.323索引交叉核对后，将比较语境中的单称“Tiepolo”映射为Giambattista Tiepolo（`cand-2569`），与Gian Domenico Tiepolo的Via Crucis（`cand-2626`）区分；相应修正p.323两条mention及一条statement对象引用，恢复副本后缀为`.bak-s2-chp10-p323-tiepolo-identity-20261003`。

p.324脚注1–4位于规范注释L325–328，仍待处理；L201末句关于夸张透视的判断续至p.325 L203–208，所以coverage为reviewed/partial。受控脚本`chp10_p324_migration.py`默认dry-run，核验Markdown/PDF/段哈希、表前态、提及跨度、statement引句和外键；应用前为四表保存`.bak-s2-chp10-p324-20261003`恢复副本。应用后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，当前826段为453 reviewed/complete、107 excluded、252 queued、14 reviewed/partial；候选9,764、提及20,672、statement 9,179。仍有两条既存enrichment `source_ref`警告。下一待处理段为p.325 `chp-10:10_CHP-10_sec_ii:l203-208`。

## 第十章印刷页325正文及p.324–325注释（2026-10-03）

对照`CHP-10.pdf`物理第58页处理`chp-10:10_CHP-10_sec_ii:l203-208`，新增12个候选（`cand-9778`–`cand-9789`）、53条精确提及和29条statement。p.325 L204闭合p.324跨页句；保留Haskell对寓言讽刺对象、Millet预示关系的判断性质。登记Gian Domenico与Giambattista Tiepolo父子关系、Villa Valmarana foresteria乡村生活场景、Maggiotto的科学兴趣与著作、Pisani改革及Gozzi公共艺术主张，同时保留未名对象、转述、推断和时间限定。L208对Pisani与Querini比较的句子在“increasingly”处续至p.326，故p.325仍为partial。

同步处理规范注释L325–332，迁入p.324注1–4与p.325注1–4的书内引证信息，并建立正文statement的`footnote_refs`链接；没有声称独立查阅这些被引来源。页图校读只记录于S2、不改S0：`soresteria`→`foresteria`、`rural Use`→`rural life`、`pass`→`past`，另校正注释中的`Longbi`→`Longhi`及`1808,1`→`1808, I`。

首次全表审计发现21条脚注mention偏移相对局部切片计数，已按整段L273–349偏移修复并留恢复副本。修复后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，无悬空脚注引用；定向测试13项通过。全账本826段：454 complete、107 excluded、250 queued、15 partial；候选9,776、提及20,725、statement 9,208。两条既存enrichment `source_ref`警告仍在。下一段为p.326 `chp-10:10_CHP-10_sec_ii:l210-222`。

## 第十章印刷页326–327正文及注释（2026-10-03）

p.326–327（`CHP-10.pdf`物理第59–60页）完成p.326正文L210–222，并处理p.327 L224–239至跨页续句处；新增40个候选（cand-9790–cand-9829）、79条提及、36条原书statement。记录Pisani与Inquisitori di Stato、Gozzi颂词/宣传品、Boscarati受托寓意画及政治绘画引发的审查和逮捕叙述；保留Haskell及被引作者的归属、推断和分期判断，不把名片符号读成固定意义。p.327末句L237续至p.328 L241，故p.327为partial。页脚分隔线下同一OCR行的脚注3续文单独归p.326注释。p.326–327注释对应规范L333–337及页图脚注续文，已链接正文；合并注释段仍partial，L274–324和L338以后待处理。页图校读仅记S2，未改S0；未独立查阅书内所引书籍、手稿及报告。

受控脚本`chp10_p326_327_migration.py`经dry-run后应用，四表恢复副本为`.bak-s2-chp10-p326-327-20261003`。更新后全账本826段：456 complete、107 excluded、248 queued、15 partial；候选9,816、提及20,804、statement 9,244。表审计`s2_missing=[]`、`errors=[]`，两条既存enrichment `source_ref`警告保留；定向测试13项通过。当前下一段为p.328 `chp-10:10_CHP-10_sec_ii:l241-246`。

## 第十章印刷页328正文及注释（2026-10-03）

p.328正文段`chp-10:10_CHP-10_sec_ii:l241-246`新增7个候选（cand-9830–cand-9836）、41条提及和22条statement，并闭合p.327“较温和的Pisani入城诗作”跨页句，将cand-9829更新为题名《Il Filosofo dell'Alpi》。记录诗作与Rousseau思想的关系及Haskell对Zuccarelli成功的判断；区分Zuccarelli、Smith的雇用/英国市场解释、Baretti与Biffi的赞誉、Biffi同Beccaria及Verri的友谊，以及Biffi日记中对Rousseau的评价。保留Haskell对Arcadia观念、后续自然主义绘画、Zais被忽视和绘画社会意义的分析，不当作无归属事实。Gozzi 1760年遭批评及其写作主题已记录；他随后提出的“这些代表……”未完句留待p.329 L249续接，故p.328为partial。

本页注释L338–342（注1–7）迁入合并注释段并与正文statement链接。注1称La Harpe的颂诗由Giuseppe Fossati改写为意大利诗体；注2为A.M. Zanetti致A.F. Gori书信，注5为Biffi致Vacchelli的1773年未刊信件；注4、6引用Venturi 1957，注7引Gazzetta Veneta。被引手稿及书刊均未独立查阅。页图校读只记S2：OCR页标`[Page 28]`对应印刷页328；正文`country house Use`校为`country house life`；注1题名、机构名连字及注2书页号按页图校读；注5 `Govcrnativa`、`fame...preggio`及注7 `Cazzetta`记录为印本`Governativa`、`farne...pregio`、`Gazzetta`，不改S0。

受控脚本`chp10_p328_migration.py`默认dry-run，核验Markdown/PDF及段哈希、表前态、mention跨度、statement引句/外键和脚注回链；应用前四表恢复副本后缀`.bak-s2-chp10-p328-20261003`。应用后p.327为complete，p.328为partial，合并注释覆盖L325–342并保持partial。全账本826段：457 complete、107 excluded、247 queued、15 partial；候选9,823、提及20,845、statement 9,266。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；两条既存enrichment `source_ref`警告保留；定向审计和源段测试13项通过。下一段为p.329 `chp-10:10_CHP-10_sec_ii:l248-256`。

## 第十章印刷页329正文及注释（2026-10-03）

对照`CHP-10.pdf`物理第62页处理`chp-10:10_CHP-10_sec_ii:l248-256`，并迁移注释L343–345。新增14个候选（`cand-9837`–`cand-9850`）、42条精确提及和22条statement；p.328末句在L249闭合，p.329末句续到p.330，coverage为partial。保留Gozzi对绘画社会价值的试探性论述、Zanetti关于实用艺术/教化作用/休憩功能的观点、1772年委员会复述的经济论证，以及威尼斯学院的成立、商业预期和题材等级；Haskell的评价和历史人物的论点分别归属，不新建正式关系。脚注引用文献题名只与仓库书目匹配，没有独立查阅。

页图校读仅记S2、不改S0：`value ofpaintings`→`value of paintings`、`subjectmatter`→`subject-matter`、`risorme`→`riforme`。受控脚本`chp10_p329_migration.py`默认dry-run，核验Markdown/PDF/段哈希、表前态、mention跨度、statement锚点、脚注回链和续句；应用前四表恢复副本后缀`.bak-s2-chp10-p329-20261003`。本页处理后826段为458 complete、107 excluded、246 queued、15 partial；候选9,837、提及20,887、statement 9,288。表审计`s2_missing=[]`、`errors=[]`；两条既存enrichment `source_ref`警告保留；定向测试13项通过。下一段p.330 `chp-10:10_CHP-10_sec_ii:l258-267`。

## 第十章印刷页330正文及注释（2026-10-03）

对照`CHP-10.pdf`物理第63页处理正文段`chp-10:10_CHP-10_sec_ii:l258-267`，注释段覆盖扩至L346–349。新增17个候选（`cand-9851`–`cand-9867`）、42条提及和15条原书statement；p.329关于艺术家社会地位的句子在L259闭合，p.330末句续到p.331 L270，故p.330仍为partial。记录Memmo在`Inquisitori alle Arti`行会重组语境下准备报告的查询、职业/税费问题、艺术自由引语和Haskell对其特殊性的评价；所有问句不写成已实施政策。Canaletto对应“C.”保留Haskell的“almost certainly”及其所述年代张力；Algarotti关于伟大艺术会吸引赞助人的观点明确归属Haskell的叙述。

脚注4总注和(i)位于合并注释L349，(ii) Martyn与(iii) `Nuova Gazzetta Veneta`位于正文L265–267；三处与展览statement相连。statement级复核发现L260脚注1正文回链缺项，已补齐；同时将Paris的statement候选映射改为城市候选`cand-4653`，不再误连到索引子条。两次修复各另存`book-statements.jsonl.bak-s2-chp10-p330-footnote1-linkfix-20261003`和`book-statements.jsonl.bak-s2-chp10-p330-candidate-linkfix-20261003`。Nunzio报告、Martyn、期刊和Haskell–Levey文章均未独立查阅；Nassi/Nazari与Foscarini肖像归属保持未决。页图校读仅记S2、不改S0：`Inquisitor! alle Arti`→`Inquisitori alle Arti`、`refers’to`→`refers to`、`Lise`→`Life`、`ku`→`fu`、`piu`→`più`、`Francesco" Algarotti`→`Francesco Algarotti`。受控脚本默认dry-run，锁定Markdown/PDF和段SHA、表前态、mention跨度、statement引句/外键、脚注和续句链接；四表恢复副本后缀`.bak-s2-chp10-p330-20261003`。应用后826段为459 complete、107 excluded、245 queued、15 partial；候选9,854、提及20,929、statement 9,303。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；两条既存enrichment `source_ref`警告保留；定向测试13项、脚本`py_compile`通过。下一段p.331 `chp-10:10_CHP-10_sec_ii:l269-271`。

## 第十章印刷页289表格及注1–2（2026-10-02）

按`CHP-10.pdf`物理第18页处理派生视觉表格L1–12、正文L234–238以及合并注释L543–544。新增39个候选（cand-9381–cand-9419）、82条精确提及和41条statement；完成正文脚注marker 1与2的注释链接。列示的艺术家不自动定为作品作者/执行者；问号、原书来源时点和Haskell的“probably”判断均保留，1741与Vertue名单不作版本合并。OCR `William HI`仍保留在来源跨度，另记录印本读作`William III`。p.289正文和派生转录complete，L492–634复合注释段覆盖至L544并保持partial。dry-run及`audit_tables.py`通过，结构错误为0；`tests/test_audit_tables.py`通过。下一位置为L545。

## 最近处理更新：第十章印刷页297正文（2026-10-02）

p.297（PDF物理第26页）规范段`chp-10:10_CHP-10_intro:l332-343`新增18个候选（cand-9137–cand-9154）、52条精确提及和17条原书statement。L333闭合p.296 Juvarra任Turin艺术总监并促成Sebastiano Ricci宫殿/教堂委托的跨页句；本页另记Ricci后期Turin作品及Haskell判断、Juvarra 1735年Madrid宫殿方案和各地画派名额、Amigoni与Tiepolo的Madrid宫廷任务、Tiepolo晚年Aranjuez祭坛画及Mengs替换作品，以及Rotari、Fontebasso和Guarana赴圣彼得堡/莫斯科的经历。区分未名宫殿、作品组、教堂、宫廷机构和艺术家群体，保留Haskell对西班牙反威尼斯态度的可能性限定。

页图校读只记S2、不改S0：`fist`→`list`、`fife`→`life`、`Guaraña`→`Guarana`。L343为注1 OCR摘句，和合并注释段L570重复，故不重复迁移；p.297保持partial，注1–6待合并注释段按源序处理。Juvarra/Ricci跨页句闭合后p.296转complete；下一段为p.298 `chp-10:10_CHP-10_intro:l345-352`。

受控脚本`chp10_p297_migration.py`默认dry-run，固定来源资产/段SHA、候选序号、索引候选、提及跨度、statement引句/外键与前态；写入前为候选、提及、statement、coverage四表保存`.bak-s2-chp10-p297-20261002`。全表审计首次发现Guarana句跨L341–342而statement范围仅记L342；修正为L341–342后复审。`audit_tables.py --summary`：824段中430 complete、62 excluded、330 queued、2 partial；候选9,141、提及18,569、statement 8,402；`s2_missing=[]`、`errors=[]`。仍有两条既存S5 `enrichment.source_ref`警告及全书S2未收口提示。定向审计测试11项通过；`git diff --check`退出码0（保留既存LF/CRLF提示）。

## 最近处理更新：第九章印刷页272正文（2026-10-01）

p.272（PDF物理第38页）新增11个候选、36条精确提及和26条statement。迁入Jesuit church的建筑表现、Fontebasso天顶题材、Dominican/Jesuit图像对照、Pietà旧址的慈善机构与赞助、1745年重建、1760年Gazzetta Veneta描述、Massari的建筑限制及Tiepolo《Triumph of the Faith》。不把“one family”推定为Manin；不把十四世纪的refuge与教堂建筑合并。印本校读S0 L55 `hi`→`In`、L58 `Unes`→`lines`，原OCR保留。

p.271句尾于p.272 L54闭合并转complete；p.272仍partial，因L58的Tiepolo句续至p.273 L63，L59–60的Professor Wilde注3续文须在合并注释段收口。p.272脚注1–6仍待后续处理。全账本820段：396 complete、61 excluded、361 queued、2 partial；候选8,720、提及17,158、statement 7,824。`audit_tables.py`无结构错误，审计测试11项通过，源段预览issues=0。下一段为p.273 `chp-9:09_CHP-9_sec_ii:l62-68`。详细记录见[过程记录](../process/stages.md)。

## 最近处理更新：第九章印刷页273正文（2026-10-01）

p.273（PDF物理第39页）规范段`chp-9:09_CHP-9_sec_ii:l62-68`新增22个候选（cand-8733–cand-8754）、65条精确提及和21条statement。记录Pietà圆顶作品所得500 zecchini、Tiepolo两年后向Pietà Governors出借6,000 ducats、五幅由Piazzetta学派画家创作且由私人捐款支付的祭坛画，以及Haskell对不同修会教堂绘画侧重点的比较。另记录Tiepolo与Ricci作品中炼狱火焰缺席、Tassis的请求、Piazzetta初稿中的骷髅、Scuola del Carmine的委托压力与两套天顶方案、第二方案采用/修改、后续竞赛及Zompini获采纳提案。身份、语气和事实范围依原书保留，脚注1–5仍待合并注释段处理。

扫描校读只记S2、不改S0：L64 `seem to.have`→`seem to have`、`Education os`→`Education of`；L65 `alhthere`→`all there`；L68 `inwhichartists`→`in which artists`。p.272 Tiepolo句于p.273 L63闭合，p.272转complete；p.273 L68提案句续至p.274 L71，coverage为reviewed/partial。受控脚本默认dry-run，核验来源/段哈希、候选顺序、提及跨度、statement引句/外键和coverage前态；应用前为四表留恢复副本`.bak-s2-chp9-p273-20261001`。

应用后全账本820段：397 complete、61 excluded、360 queued、2 partial；候选8,742、提及17,223、statement 7,845。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；两条既存`enrichment.source_ref`警告仍在。`python -m pytest tests/test_audit_tables.py -q`通过11项，`build_source_segments.py`预览820段、issues=0。严格阶段模式仍因待处理和partial段而未放行。下一规范段为p.274 `chp-9:09_CHP-9_sec_ii:l70-78`。

## 最近处理更新：第九章印刷页274正文（2026-10-01）

p.274（PDF物理第40页）规范段`chp-9:09_CHP-9_sec_ii:l70-78`新增15个候选（cand-8755–cand-8769）、52条精确提及和25条statement。闭合p.273 L68的Zompini提案句；记录Virgin typology、1743年匿名Jesuit sermon与Pietà governors择案，继而记录Flaminio Corner的宗教赞助和生平、Giuseppe Angeli的艺术评价与Corner在S. Canciano、S. Basilio、Pietà的委托。私用作品分成Four Evangelists绘画、Apostles系列和未名圣徒画。S. Basilio的“he”存在语法指代歧义，不断言Angeli属于贵族团体；Corner的遗物收藏缺少当前可用类型，保留type undecided，不强制归类。

扫描校读只记录于S2：法文`reputation`据印本补重音为`réputation`；印本在L75 `early paintings`后有注6，但S0 OCR遗漏标号。S0未改，p.274注1–6留给合并注释段。p.273转complete，p.274转complete。受控脚本`chp9_p274_migration.py`默认dry-run，检查OCR资产与段SHA-256、候选顺序、52条提及跨度、25条statement引句/外键、p.273跨页statement及coverage前态；应用前为候选、mentions、statements、coverage四表留存`.bak-s2-chp9-p274-20261001`。

应用后全账本820段：399 complete、61 excluded、359 queued、1 partial；候选8,757、提及17,275、statement 7,870。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，尚有两条既存enrichment `source_ref`警告；`python -m pytest tests/test_audit_tables.py -q`通过11项，`git diff --check`退出码0。S2仍未达到交接条件。下一规范段为p.275 `chp-9:09_CHP-9_sec_ii:l80-83`。

## 最近处理更新：第九章印刷页270–271正文（2026-10-01）

p.270–271（PDF物理第36–37页）共新增26个候选、99条提及和31条statement。p.270的1742年访客引语由p.271 L39–40闭合；p.271 L51页尾句续至p.272 L54。p.270脚注7续文仍待处理，该注标号与正文所述Gesuati资助、注文本身的Dominican内容存在页内错位；不据此强行绑定。p.271注1–6等待合并注释段处理。

当前820段：395 complete、61 excluded、362 queued、2 partial；候选8,709、提及17,122、statement 7,798。`audit_tables.py`为`errors=[]`、`s2_missing=[]`；审计测试11项通过，源段重建预览820段且issues=0。两条既存enrichment `source_ref`警告未涉及本批迁移。下一源段为p.272 `chp-9:09_CHP-9_sec_ii:l53-60`。详细判断见[过程记录](../process/stages.md)。

## 最近处理更新：第九章印刷页268–269正文（2026-10-01）

p.268–269（PDF物理第34–35页）新增24个候选、79条提及、39条原书statement，并闭合p.268起始的1743年观察者引语。两页coverage现均为reviewed/complete；第九章共有39段complete、7段排除、7段queued。p.269所涉注1–6仍待该节注释段处理。全账本820段：395 complete、61 excluded、364 queued、0 partial；候选8,683、提及17,023、statement 7,767。表审计`errors=[]`、`s2_missing=[]`，定向审计测试9项通过。下一规范段为p.270 `chp-9:09_CHP-9_sec_ii:l27-36`。详细判断及异常恢复过程见[过程记录](../process/stages.md)。

## 第九章印刷页262正文与注1–6（2026-10-01）

p.262规范段`chp-9:09_CHP-9_intro:l218-229`对照`CHP-9.pdf`物理第24页完成，新增27个候选（cand-8544–cand-8570）、79条精确提及和29条statement。p.261 L216末“and to”由p.262 L219续接并闭合；p.261转complete，p.262正文/页下注OCR范围转complete。合并脚注段扩至L413，仍因后续脚注未处理而partial；本页注1、3、4、5由对应页段/合并段锚定，注2以同版视觉转录补足，注6由p.262页OCR L228–229锚定。

事实范围包括Foscarini年收入转述、最低生计估算、Canaletto与Rosalba Carriera价格、外来竞争对高价的解释、Piazzetta《Angelo Custode》估值、Tiepolo两组作品及相应报酬；另记录新贵族入籍费用与当代画购置、Grassi收藏及可能的古老血统动机、Labia与Giovanelli收藏判断。Biffi 1773年对Palazzo Giovanelli藏画的意大利语引文保留为嵌套档案转引；“Paolo”“Palma”等不充分姓名保持未对齐。将《Angelo Custode》《Martyrdom of St John the Bishop》、Pietà圆顶壁画和Labia库存的`Ritratto con cristallo`、`Una Palla`作为不同作品候选，避免把库存描述当成已确认目录作品。引文所涉库存、档案、书目及Venturi微缩胶片均未独立查阅。

页图校读仅记S2、不改S0：OCR页码`[Page 202]`应为印刷p.262；`domeof`→`dome of`、`GuerCino`→`Guercino`、`art seemed, to stop`→`art seemed to stop`；Cignaroli后OCR注号6核为印本5，Giovanelli句末印本注6在OCR中漏失；MSS. locator标点据页图记录。

## 最近处理更新：第九章印刷页251–261（2026-10-01）

p.251正文L106–114及注释延续已迁入；p.252–258依次新增34、23、33、39、37、28、21个候选，107、68、82、74、85、65、53条提及，以及32、18、29、29、40、29、23条statement；p.255–260跨页句均已闭合。p.259正文L189–200及注1–6新增33个候选、67条提及和28条statement；Batoni《The Triumph of Venice》的藏所说法与前置Plate 45目录差异保留待复核。p.260正文L202–210及注1–9新增31个候选、74条提及和30条statement；L203闭合p.259句，p.260 L210由p.261 L213闭合；注8以派生视觉转录作唯一S2锚点。p.261正文L213–216及注1–6新增22个候选、47条提及和28条statement；匿名旅行引文及Gherardi致Muratori的1745年信均保留原书转引层次，Pisani的Zais赞助、两处宅邸及匿名绘画组分开记录，Haskell对衰退原因与财富情况的限定均保留。页图校读只记S2、不改S0；p.261 L216续至p.262 L218，合并注释已覆盖L409。详细判断与锚点见[过程记录](../process/stages.md)。全账本815段：375 reviewed/complete、60有理由排除、378 queued、2 partial；候选8,531、提及16,605、statement 7,571。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，定向测试11项通过，`git diff --check`通过；两条既存`enrichment.source_ref`警告仍在。下一正文段为p.262 `chp-9:09_CHP-9_intro:l218-229`，合并注释从L410继续。

## 前次近期处理更新：第八章印刷页231–237（2026-10-01）

p.231正文L238–249及注1–6（L409–414）新增21个候选、75条提及和20条statement，跨页句于p.232 L252–253闭合。p.232正文L251–257及注1–4（L415–418）新增38个候选、78条提及和25条statement；modelli续句由p.233 L272闭合，p.232转complete。Plate 37、38、40可读题注与Plate 38派生题头段完成，新增14条提及和10条caption statement。p.233正文及注1–5（L419–423）新增24个候选、86条提及、21条statement；末句于p.234 L282闭合，p.233转complete。p.234正文、页尾Langetti报告及注1–6（L424–429）新增17个候选、70条提及、15条statement；报告保留为二手转述并注明印本位置与转录标记缺失。p.235正文及注1–6新增33个候选、123条提及和18条statement；p.236正文及注1–3新增23个候选、71条提及和17条statement。p.236末句由p.237 L312–313闭合并转complete；p.237新增18个候选、80条提及、19条statement，正文句尾续至p.238 L328而保持partial。注释复合段覆盖L373–442并保持partial，L443–461待处理。当前结构账本errors=[]，406段queued、2段partial及两条既存source_ref警告。

## 第八章印刷页235正文与注1–6（2026-10-01）

对照`CHP-8.pdf`物理第41页迁入正文段`chp-8:08_CHP-8_sec_ii:l291-301`及后置脚注复合段L430–435。页末脚注6的意大利语引文从L435续到正文分节OCR L301；该行按脚注引用而非正文处理，并以`continued_from_segment_id`回链。p.235正文coverage转complete；复合脚注段扩为L373–435并保持partial，余下L436–461待处理。

记录Luca Giordano为Ferdinand绘制《The Flight into Egypt》玻璃画、1702年赴Livorno、1704年Ricci受托替换《Madonna delle Arpie》、Ricci的Florence短访与Cassana的市场信息职责、Marucelli兄弟雇佣、1706年装箱送画及Ricci—Marco侄甥关系、Poggio a Caiano拟议房间装饰与延期，以及毁佚的《Allegory of the Arts》和为Marucelli/Pitti完成的装饰。将Haskell的判断、`seems`推测、二手引述和关系候选分别保留；“this one exception”、两位晚期艺术家、最喜欢的别墅/画廊及S. Francesco de’ Macci身份不强行判定。Farsetti引文记为独立的天花寓意装饰，未与Ricci毁佚作品合并。

注1–6分别登记Letter 75、98、99、197、200及Fogolari/Farsetti/Martini转引；来源仅作书内引证定位，未声称独立查阅。页图校读只记S2、不改S0：L291页码`[Page 23]`→`[Page 235]`；L292删除`painted`后多余逗号；L296修复`Marucelli.of`；L297修复`Grand Princewhich`及`included`前杂点；L430修正`ibid..`和意大利语逗号；L432去除句尾OCR短横；L434 `No. zoo`→`No. 200`；L435脚注号8校为6。Haskell正文称Giordano从Spain返回，信件引文说从Naples返回；两者可能为连续行程阶段，未强行合并或消除差异。

受控脚本`chp8_p235_migration.py`默认dry-run，核验来源资产与段hash、候选自然键、123条提及精确跨度、18条statement锚点/原文/外键及coverage；应用前保存四表恢复副本`.bak-s2-chp8-p235-20261001`。应用后账本为812段：349 complete、1 partial、54有理由排除、408 queued；候选7,978、提及15,035、statement 7,052。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，保留2条既存enrichment `source_ref`警告；`python -m pytest tests/test_audit_tables.py -q`退出码0（11项通过）。下一正文段为p.236 `chp-8:08_CHP-8_sec_ii:l303-309`，脚注复合段下一范围L436–461。

## 第八章印刷页203–204（2026-09-30）

已处理`08_CHP-8_intro:l7-10`（p.203注1–4）及`08_CHP-8_sec_i:l3-12`（p.203正文与注5），并将生成标题和章标题段按来源性质排除。p.203新增34个候选（cand-7357–cand-7390）、75条提及、21条statement；包括Genoa/ Naples/ Bologna具名家族、B.109手稿、Biblioteca Comunale与Oretti。脚注引用作为书目定位记录，未将被引页声称为独立核验。扫描校读记入S2 qualifiers，S0转录未改。末句“this little”已由p.204 L15续为“group of enlightened merchants was certainly Giovanni Ricci”，p.203 coverage转complete。

p.204正文`08_CHP-8_sec_i:l14-21`新增10个候选（cand-7391–cand-7400）、44条提及、18条statement。分别记录Ricci/Crespi旅行与经销安排、Valletta与Giordano及Solimena、Haskell对罗马与省区艺术赞助的比较和跨地域收藏论证。`CHP-8.pdf`物理第2页确认S0中的替换字符、破折号占位和`hot only`应读作`not only`；来源未改。p.204注1–3在后置复合段L127–129，仍待迁入，故p.204保持partial。接续段为p.205 `l23-28`。

产物：[`s2-coverage.csv`](../../../04-knowledge/tables/s2-coverage.csv)、[`mentions.csv`](../../../04-knowledge/tables/mentions.csv)、[`book-statements.jsonl`](../../../04-knowledge/tables/book-statements.jsonl)。逐段理由见[过程记录](../process/stages.md)。

## 第八章印刷页205（2026-09-30）

规范段`chp-8:08_CHP-8_sec_i:l23-28`已完成语义阅读并迁入20个候选（cand-7401–cand-7420）、45条精确提及和21条statement。记录Gaspar Roomer的来源报告、行旅贸易、借贷、住宅、宗教捐赠、1647年事件、藏画与绘画收藏，并区分Ribera作品、Sandrart所述Cato图像及Haskell的审美评价。标题人物、匿名家属、未名地点和群体按来源保留边界；未将King of Spain或Cato身份强行对齐。扫描校读将`ofliis`记为`of his`、`heowned`记为`he owned`，原S0不改；Scandinavia后的微小印记不清，保留OCR，不做规范化。p.205注1–4尚在复合段L130–133，且L28的Carlo姓名及三幅作品陈述续至p.206，故coverage为reviewed/partial。写入后全账本805段中302 complete、2 partial、52有理由排除、449 queued；候选7,411、提及12,952、statement 6,360。`audit_tables.py --summary`为0 errors；`tests/test_audit_tables.py`执行退出码为0。这些机械检查不构成独立语义验收。

## 第八章印刷页206（2026-09-30）

规范段`chp-8:08_CHP-8_sec_i:l30-41`已完成正文语义阅读和迁移，新增19个候选（cand-7421–cand-7439）、55条精确提及和23条原书statement。记录Roomer所购画家、Falcone为其绘制的战争题材、弗兰德斯画家群与题材、Roomer引语及未识名书面来源、所列九位画家的藏画、Haskell对跨地域视觉文化和Roman/Venetian painting的比较、收藏和交易及两幅Van Dyck画作，并区分`Feast of Herod`的来源报告、相对年代、传播反响与图像人物。Valentin、Bassano保持姓氏级身份待S3；Herodias之女与持约翰头颅的高个女子分别保留候选，因为原句未明确二者同一。引语、图像内容、作者推论及“probably”“presumably”“perhaps”“almost”等限定均按来源层级登记，未转成正式关系。

对照`CHP-8.pdf`物理第4页校读`still Eves`→`still lives`、`very sine`→`very fine`、`van dor Bos`→`van der Bos`、`Naples-—thereafter`→`Naples—thereafter`；仅记入S2，S0未改。L32脚注号1后的短横暂不判断为文字或印记。p.206注1–2位于复合来源L134–135，仍未迁入；故本段partial。p.205的Carlo姓名由p.206 L31的Saraceni闭合。下一段为`chp-8:08_CHP-8_sec_i:l43-51`（p.207）。写入后总账805段中302 complete、3 partial、52有理由排除、448 queued；候选7,430、提及13,007、statement 6,383。`audit_tables.py --summary`为0 structural errors，审计测试11 passed；两条既存enrichment `source_ref`警告仍在。机械检查不替代全书语义召回核查。

## 第七章印刷页184正文L171–176迁移（2026-09-30）

逐行处理规范段`chp-7:07_CHP-7_sec_i:l170-176`，并对照`CHP-7.pdf`物理第18页。新增25个候选（cand-6809–cand-6833）、77条精确提及和18条原书断言。p.184 L171以独立续句statement闭合p.183 L167；p.184 L176末句止于“a few years”，仅核对p.185 L206“earlier.”以闭合该句，p.185其余正文待完成图版段后再处理。

记录Charles I面对未具名政治对手、其绘画收藏由Parliament出售、艺术珍品进入国际市场；复用cand-0654索引子项表示sale事件，将Parliament机构和Charles I picture gallery对象分开。Mazarin委托Everard Jabach购买前竞争者Duke of Mantua收藏中的绘画，前竞争者映射cand-6720，收藏映射cand-6721，人物身份留待S3。

记录Mazarin在1653年恢复权力及绝大多数绘画幸存、约500幅藏画、Old Masters与其年轻时在意大利熟悉的艺术家、Reni/Guercino的相对代表数量、Sacchi/Cortona作品、对意大利绘画新发展的有限关注，以及Salvator Rosa《Landscape with Apollo》作为1653–1661年间唯一由Mazarin在意大利时不认识的艺术家所作之购入作品。另区分赠画导致的趣味判断限制、直接委托中的世俗/情色倾向、敌方指控与Haskell评价。inventory文献候选cand-6814暂不定年：正文说“at once”，而p.184注3指向1661 inventory（复合段L356尚未按序迁移）；不把两者静默合并。

记录Brienne对La Vrillière与Mazarin画作的比较、三幅不明Correggio作品与Titian Venus例外、Mansart为La Vrillière建造的宫殿、Mazarin公寓及两处作品/艺术家群体的边界、La Vrillière偏爱的古代英雄题材，以及Reni《The Rape of Helen》与Marie de Medici此前购入该画的说法。作品标题候选与艺术家索引候选分开；未将Titian Venus、三幅Correggio作品或四幅Brienne偏爱的画作对应到具体实物。

PDF物理第18页核读；S0保持原样。校读包括L171、L172和L173的`ofhis`→`of his`，L172 `whomhehadbecomefamiliar`→`whom he had become familiar`、`always-easy`→`always easy`、`subject-matfer`→`subject-matter`，L174 `in bis palace`→`In his palace`及`La'Vrillière`→`La Vrillière`。脚注1–4在复合段L354–357待迁移；note 3的inventory日期限定仍待审。

迁移后总账为262段complete、8段partial、45段有理由排除、488段queued；候选6,824、提及11,201、原书断言5,515。`python scripts/audit_tables.py --summary`为0 errors，两条既存enrichment `source_ref`警告及8段partial/488段queued仍在。下一规范段`chp-7:07_CHP-7_sec_i:l178-179`是图版25说明；随后依次处理图版26–28段，再进入p.185正文。


## 当前交接判定

继续第7章至第22章材料的S2语义阅读与登记；下一段为`chp-7:07_CHP-7_sec_i:l178-179`（图版25说明）；之后依序处理图版26–28，再继续p.185正文。复合段`l293-389`按规范来源顺序迁移p.170–184脚注及p.172 L301正文续句；p.177注4跨正文段L100与复合段L322；p.179–182脚注分别位于L330–347；p.183注1–6位于L348–353，其中注2与正文段L168拆分。p.178注1对画作与邀请关联提出学术保留。

## 第二版导言 L174–198 的S2迁移

`l174-185`复用FM-S31–34逐行阅读，新增6个候选、40条提及和22条原书断言；`l187-188`新增2个候选、7条提及和4条引文定位断言；`l190-196`新增1个候选、24条提及和13条断言；`l198`新增4条提及和2条引文定位断言。四段均已完成迁移。Haskell叙述、Honour评论、Waterhouse批评与其转引的Wittkower论点分别记录；迁居来源不逐个配对，Crespi/Solimena的互斥情况不拆配到个人，作者评价保留发言者限定。脚注链接到对应引述判断、Poerson书信和San Clemente装饰事件。扫描版`CHP-0Cover.pdf`物理第14页确认Clement XI年代为1700–1721，物理第15页确认印刷页眉xviii；跨页句已接续，脚注来源仅作引文定位。


## 第5章印刷页126正文 L61–74（2026-09-29）

按页序核对`05_CHP-5_sec_i.md`与`CHP-5.pdf`物理第7页。页125 L57末句由页126 L61闭合，将页125段由partial改为complete；页126 L74的Jan Miel遗嘱引文止于“decorated”，由页127 L77续接，故本段为partial。新增8个来源型候选、33条精确提及和19条原书断言/引证。

正文覆盖Pantheon圣约瑟节年度展览、Congregazione dei Virtuosi的成立与慈善/艺术目的、展览的筛选及展示方式、Velasquez展出Pareja肖像和其机构成员身份、Rosa的1651/1652嵌套引语、展览声誉与现场销售的区别、部分观众的敬圣目的及Jan Miel遗嘱。保留Haskell的“it seems certain”“probably”、Rosa引语的发言层级和匿名画作不造实体；Velasquez的机构全名以及引述中的“picture”按规范源段真实换行锚定。

PDF核实L63的“a confraternity”及1764、L74的Jan Miel与1650；这些是OCR校读限定，不改S0。当前总账196段complete、2段partial、33段有理由排除、571段queued；候选6,034、提及7,953、原书断言4,012。`audit_tables.py --summary`结构errors为0，`tests/test_audit_tables.py`为11 passed；两条既存enrichment `source_ref`警告仍在。下一规范源段为`chp-5:05_CHP-5_sec_i:l76-83`，先闭合遗嘱引文并继续正文与注释。


## 第六章印刷页164–166正文、脚注及第七章结构段（2026-09-29）

p164 `chp-6:06_CHP-6_sec_v:l28-33`新增14个候选、39条提及和29条断言；闭合p163 L26至p164 L29的“most adventurous patron”句。记录Pietro Ottoboni艺术赞助、来源归属、匿名传记/诗歌及相关作品和委托；p164注1在正文行内已有记录，复合注释L61–64的注2–5现已链接。

p165 `l35-40`新增10个候选、59条提及和26条断言。分别记录Conca、Gaulli、Juvarra、Ricci、Diziani、Fra Galgario及匿名画家群的赞助、作品/舞台布景和迁徙；保留Haskell对Ricci故事的嵌套引述。复合注释L65–68注1–6现已回链，Corelli与Ottoboni的友谊、Europa绘画及未具名的Temanza手稿保持来源和身份边界。

p166 `l42-45`新增8个候选、23条提及和14条断言，记录Crespi、Solimena、六件圣事组画、赞助竞争、古典趣味和罗马的欧洲/意大利城市对手。注1定位L. Crespi并把“这些画作现藏德累斯顿”限定为紧邻的Crespi作品，不扩至Solimena；注2的三个例子分别记录Pallavicini/Piola、d’Adda—Gozzadini—Albani/Viani及Lazzarini，保留主办者与支持者关系。

复合脚注`chp-6:06_CHP-6_sec_v:l47-70`新增25个候选、63条提及和43条断言/定位记录。完成p162注1–7、p163注1–6、p164注2–5、p165注1–6及p166注1–2共25个脚注标记的回链。书目/档案定位不作外部事实核验；脚注中新增的藏址、墓址、收藏关系和历史例证单独建断言。将p162 L48的“Rothlisberger, s”校作印本Röthlisberger, I；p165 L65 OCR“Lores”按印本和书目校作Loret；p165 L68首个脚注编号印为5、OCR误为6；L66的Corelli拼写按扫描核对。S0原文保留，校勘理由记录于过程。

第七章intro及section i中的四段生成文件标题、页码和分部/章标题有理由排除，未生成实体或断言。迁移后全书为253段complete、0段partial、45段excluded、505段queued；候选6,587、提及10,190、原书断言5,103。审计0 errors，仍有两条既存enrichment source_ref警告。下一实际正文段为`chp-7:07_CHP-7_sec_i:l3-9`（印刷页3），之后将intro L11–15脚注按对应正文断言回链。



## 第七章印刷页3正文与脚注1–5（2026-09-29；历史记录，跨页句已于p.170收口）

据PDF物理第3页核对，p.3正文L3–9和脚注段07_CHP-7_intro.md L11–15中的印本注1–5已按编号迁移。OCR首字母与脚注5编号/年份差异均按扫描记录，S0原文未改；Rosa引文、赞助衰退、条件性风险、Forabosco／Ruffo交易状态、意大利艺术家群体及Crespi条件均保留发言层与限定。该正文段当时因句尾his跨页而标partial，现已由p.170续接改为complete；当前partial位于p.170末句“able”，下一段从p.171续接。

## 第七章印刷页170正文（2026-09-29）

已闭合p.169 Crespi条件句；p.170 L19末句仍跨页partial。新增9个候选、44条提及和22条断言/关系候选。脚注1 Vaes 1931 p.202将在脚注块L293-389按序处理。下一正文段为`chp-7:07_CHP-7_sec_i:l21-29`。


## 第七章印刷页176正文L77–89（2026-09-29）

`chp-7:07_CHP-7_sec_i:l76-89`新增14个候选、87条提及和34条断言。p.175 L74句尾“made”由L77续接闭合；p.176 L89末句“without Urban VIII,”续至下一规范段L91–100的L92，故p.176为partial。p.176注1–9仍待复合源段L314–318处理。

## 第七章印刷页177正文L92–99（2026-09-29）

`chp-7:07_CHP-7_sec_i:l91-100`新增19个候选、52条提及和27条原书断言。p.176 L89关于Urban VIII的句子由本页L92闭合；p.177 L99 Charles I向Guercino提出有利条件的句子仍partial，续至p.178 L103。p.177注1–5仍待复合段L319–323按源序迁移；注4的尾句在本段L100，须与复合段L322合读。扫描确认L95 OCR `osali`为印本`of all`，L98 `artisricpolicy`为`artistic policy`，只记校读、不改S0。身份不清的Duke of Mantua、Cardinal Barberini、Charles I的妻子及罗马宗教裁判所均保留待决；收藏类型因当前taxonomy没有collection类而留空。当前全书为261 complete、2 partial、45 excluded、495 queued；候选6,730、提及10,741、原书断言5,337。表审计0 errors，测试11 passed；下一规范段为`chp-7:07_CHP-7_sec_i:l102-111`。

## 第七章印刷页178正文L103–111（2026-09-29）

`chp-7:07_CHP-7_sec_i:l102-111`新增7个候选、53条提及和24条断言，正文coverage complete。p.177末句由p.178 L103闭合；p.177 coverage仍partial的唯一剩余内容是L100脚注4尾段。扫描确认p.178页脚有注1–6，复合段位置为L324–329；注5在S0 OCR中误作6，页图显示为5。注1提示有学者认为Semiramis与Charles I邀请无关，未先于源序处理复合段而改成已裁决事实。`1625/`和`rewarded.'`的脚注标记按页图定位，S0不改。当前下一规范段为`chp-7:07_CHP-7_sec_i:l113-126`。

## 第七章印刷页179正文L114–126（2026-09-30）

`chp-7:07_CHP-7_sec_i:l113-126`迁移L114–122、L124–126，新增17个候选、79条提及和27条断言；L123为分节版面标题。记录Arundel墓葬与Bernini胸像计划、Charles I的Van Dyck三人肖像、Baker胸像、1636年书信与浮雕提议、Caroselli委托、Reni作品、取消的巴黎安排、Gentileschi去世、时期判断和1648年和平条款。Francesco送信人与young sculptor Francesco分开；Italian amateur与Mazarin关联保留跨页推断；Little Tom、Cardinal Barberini、Urban VIII侄辈的身份或类型未决。p.179注1已回链，注2–6仍待复合段L330–334；末句由p.180 L129续接，故本段partial。扫描校读只记S2，不改S0。

下一规范源段为`chp-7:07_CHP-7_sec_i:l128-138`（印刷页180）。

## 第七章印刷页183正文（2026-09-30）

规范段`chp-7:07_CHP-7_sec_i:l160-168`迁入L161–168，新增14个候选、62条提及、20条断言，另以`st-chp7-p183-q01`记录p.182引语的续文，避免原书断言锚点跨规范段。L167句续至p.184 L171；p.183注2日期部分在L168，转让链在L349；注1、3–6位于L348、L350–353待迁移。p.183因此为reviewed/partial。PDF物理第17页核对发现L165印本为`need only be said`，S0 OCR未改。修正锚点后表审计0 errors，测试11 passed；当前262 complete、7 partial、45 excluded、489 queued，候选6,799、提及11,124、断言5,497。

## 第七章印刷页185正文（2026-09-30）

`chp-7:07_CHP-7_sec_i:l205-213`新增28个候选（`cand-6834`–`cand-6861`）、94条提及和30条断言。p.184 L176句尾由p.185 L206闭合；记录Mazarin购藏、La Vrillière系列及品味比较、晚年活动和Brienne绘画记述，保留Haskell的归属、解释和推测限定。页图校读将OCR差异记入过程，不改S0。p.185注1–5仍在复合段L358–360，法文引文续至p.186 L216–218，故本段为`reviewed/partial`。当前下一段为`chp-7:07_CHP-7_sec_i:l215-222`；写后审计0 errors。



## 第七章印刷页186正文（2026-09-30）

规范段`chp-7:07_CHP-7_sec_i:l215-222`新增25个候选、83条提及和21条断言。Brienne法文引文续页并闭合，已与p.185原statement互链。Haskell关于Mazarin死后艺术赞助、Theatines与St Anne-la-Royale、Guarini及建筑方案的叙述均按原文层级与限定记录；Fouquet、Colbert受雇于Mazarin的句子续至p.187 L225。p.186注1位于复合段L361待迁移，因此本段partial；p.185注1–5仍待L358–360。页图校读及未决身份见[过程记录](../process/stages.md)。当前S2为266 complete、10 partial、45 excluded、482 queued；6,877 candidates、11,398 mentions、5,580 statements。表审计0 errors，审计测试11 passed。下一规范段为`chp-7:07_CHP-7_sec_i:l224-230`。

## 第七章印刷页187正文迁移（2026-09-30）

p.187正文L225–230已完成语义阅读与结构迁移：新增21个候选、69条提及、29条原书断言/关系候选；闭合p.186 L222跨页句，保留p.187 L230引语向p.188的续接。p.187注1–6（复合段L362–367）仍待迁移，因此coverage为reviewed/partial。总账为266 complete、11 partial、45 excluded、481 queued；候选6,898、提及11,467、原书断言5,609。下一段：`chp-7:07_CHP-7_sec_i:l232-241`（p.188正文）。


## 第七章印刷页188正文迁移（2026-09-30）

p.188正文L233–241已完成语义阅读和结构迁移：新增17个候选、75条提及、34条原书断言/关系候选；p.187 L230引语由p.188 L233续完。p.188注1–2仍位于复合段L368–369，L241末句续至p.189 L244，因此本段reviewed/partial。全书当前266 complete、13 partial、45 excluded、479 queued；候选6,930、提及11,611、原书断言5,671。p.188 L241末句已由p.189 L244闭合；p.189注1–6待复合段L370–374迁移，当前下一段为chp-7:07_CHP-7_sec_i:l259-266（p.190正文）。


## 第七章印刷页189正文迁移（2026-09-30）

p.189正文L244–257已完成语义阅读和结构迁移：新增15个候选、69条提及、28条原书断言/关系候选；页图校正os为of及脚注印本号5（OCR误作6）；p.188末句由L244闭合。p.189注1–6位于复合段L370–374待迁移，因此coverage为reviewed/partial。全书当前266 complete、13 partial、45 excluded、479 queued；候选6,930、提及11,611、原书断言5,671。下一段为chp-7:07_CHP-7_sec_i:l259-266（p.190正文）。


## 第七章印刷页190正文迁移（2026-09-30）

p.190 L260–266已迁入：新增15个候选、97条提及、28条断言/关系候选；页末句续至p.191 L269。注1–5在复合段L375–378待迁移，故本段reviewed/partial。页图校读修正记录于process/stages.md；当前下一规范段为chp-7:07_CHP-7_sec_i:l268-280。


p.191正文L269–278已完成语义阅读和结构迁移：新增22个候选、86条提及、32条断言/关系候选。闭合p.190末句；p.191注5、9在本段L279–280已迁入，注1–4、6–8、10–11位于复合段L379–387待迁移；L278末句已由p.192 L283闭合；注释仍待迁移，因此coverage为reviewed/partial。p.192 L278末句已由L283闭合，注1–2在复合段L388–389待迁移；下一段为chp-7:07_CHP-7_sec_iv:l3-4。


第七章p.192正文L283–291已完成语义阅读和结构迁移：新增17个候选、51条提及和28条原书断言/关系候选。L283闭合p.191 L278的未完句，并建立statement互链。记录Del Carpio治理评价、赴马德里招募画家的尝试、Giordano 1692年赴西班牙、其风格与后续影响，以及对提香、鲁本斯和Velasquez的接受；身份不明的君主、作品组、宫殿、画藏和群体不合并或补造。PDF物理第30页校读：Niccolo→Niccolò、It-was→It was、thé→the、countryduring→country during、hve→live；S0 OCR保留原状。p.192注1、2在复合段L388–389待迁移，因此该段reviewed/partial。下一规范段为chp-7:07_CHP-7_sec_iv:l3-4（印刷页192第IV节引言）。

- p.192第IV节引言L3–4已完成：3个候选、6条提及、1条总结性断言；保留Haskell对Spain/France影响和HRE后至England赞助重心转移的比较判断，不推定具体继承者。下一规范段为`chp-7:07_CHP-7_sec_i:l293-389`（第七章p.170–192复合注释与正文续句）。

- 复合段`chp-7:07_CHP-7_sec_i:l293-389`已迁入L294–300：8条脚注引证statement及注6的3项作品/归属断言；新增9个候选、15条提及、11条statement。页图核实Passeri与`o£`→`of`，S0保持原文。该段当前reviewed/partial；L301正文续句及L302以后脚注待处理。


## 当前交接快照（2026-09-30）

p.172开篇续文L301及注1–4（L302–305）、p.173注1–3（L306–308）、p.174注1–4（L309–311）、p.175注1–2（L312–313）、p.176注1–9（L314–318）、p.177注1–5（L319–323）、p.178注1–6（L324–329）、p.179注2–6（L330–334）、p.180注1–4（L335–338）、p.181注1–4（L339–342）、p.182注1–5（L343–347）、p.183注1–6（L348–353）、p.184注1–4（L354–357）、p.185注1–5（L358–360）、p.186注1（L361）及p.187注1–6（L362–367）均已按书序迁入并回链。p.181–187正文现complete；复合段L293–389覆盖至L367，仍为partial。当前803段：278 complete、6 partial、45 excluded、474 queued；候选7,101、提及12,139、statement 5,926。下一子范围L368–369（p.188注1–2）。

## 第七章p.180脚注 L335–338（2026-09-30）

已迁移脚注1–4并与p.180正文标记回链。新增3个候选、10条提及、7条statement；复用并补全Prunières 1913和Blunt《Nicolas Poussin》目录候选。Haskell对1632年前委托的限定判断与Mahon购画年代建议分开记录；Louvre/Detroit馆藏映射以端点集合保留待决。p.180现complete；复合段覆盖L294–338、仍partial。当前账本271 complete、13 partial、45 excluded、474 queued；候选7,063、提及12,015、statement 5,857。下一子范围L339–342（p.181注1–4）。


本段迁移后检查：`python scripts/audit_tables.py --summary`为0 errors；仍有两条既存enrichment source_ref警告、474段queued及13段reviewed/partial。`python -m pytest tests/test_audit_tables.py -q`为11 passed。定向检查确认10条新提及的start/end均匹配S0原文，7条新statement、候选外键、正文脚注回链和p.180 complete状态有效。

## 第七章印刷页181脚注L339–342（2026-09-30）

新增`cand-7073`（1646-07-06 Romanelli致Francesco Barberini书信）、12条提及和8条statement；既有`cand-4359`据书目页433补明论文身份。脚注1拆分Brienne报告与Haskell解释；注2回链Brienne引语；注3定位Mazarin目录；注4记录信件作者、收件人与日期及Pollak p.52 locator。p.181正文i05/i06/i11/i26/i27/i28的pending说明已替换为显式footnote refs，全部4个印刷页脚注标记已回链。注4所述信件未被独立查阅，不作为正式关系。

覆盖从L294–338扩至L294–342，p.181正文段complete。全账本272 complete、12 partial、45 excluded、474 queued；候选7,064、提及12,027、statement 5,865。严格审计0 errors；两条既存enrichment source_ref警告及未收口状态仍在。测试：11 passed。

## 第七章印刷页182脚注L343–347（2026-09-30）

按书序迁移p.182脚注1–5，对照`CHP-7.pdf`物理第16页。注1分别登记Prunières 1913 p.68与Per Bjurström《Giacomo Torelli and Baroque Stage Design》（Stockholm, 1961）书目定位；复用候选`cand-4861`，新增Bjurström书籍和作者候选`cand-7075`、`cand-7076`。注2据书目登记Félibien《Entretiens…》Trévoux 1725六卷本，复用作者`cand-1015`，新增卷III来源候选`cand-7077`。注3、4分别定位Malvasia《Felsina Pittrice》卷II pp.264、327；`ibid.`回指注3，复用`cand-6933`。这些来源均作Haskell的书目定位，没有独立阅读被引页。

页图另校读L343–344的Prunières、Bjurström、Félibien变音符，S0原文不改。注5核对页图确认印本脚注号为5（S0 OCR为8），并校读Röthlisberger、卷号I；原文OCR不改。复用Claude作品候选`cand-0780`、Claude人物`cand-0767`、Mazarin `cand-1588`、Dresden `cand-0947`、Röthlisberger人物/出版物`cand-3502`/`cand-4577`；新增来源所称的未知买家M. Parasson `cand-7074`。分开记录画作在Dresden、Claude记录的买家、至1653年归Mazarin及“最可能通过代理为Mazarin绘制”四项；保留Haskell→Röthlisberger→Claude记录的转述链、买家身份未明、代理人未名和推测限定，不升格为已核实事实或S6正式边。

本段新增4个候选、16条提及和10条statement；补明Prunières、Malvasia和Röthlisberger既有候选的书目定位。p.182正文L151–158由reviewed/partial转为reviewed/complete；复合段覆盖扩至L294–347并仍partial，下一范围L348–353（p.183注1–6）。当前803段为273 complete、11 partial、45 excluded、474 queued；候选7,068、提及12,043、statement 5,875。

迁移后核验：`python scripts/audit_tables.py --summary`为0 errors；两条既存enrichment `source_ref`警告、474段queued及11段reviewed/partial保留。`python -m pytest tests/test_audit_tables.py -q`：11 passed。16条提及偏移以复合段L293–389为基准逐条核对S0；候选外键、10条statement和正文i10/i11/i12/i14/i17/i18到脚注1–5的双向链接有效。机械核验和书目识别不等于独立阅读或整体语义准确率验收。


## 第七章印刷页184脚注L354–357（2026-09-30）

新增10个候选、24条提及和11条statement；补明d’Aumale、Bonnaffé与Briganti的书目身份，并区分1653与1661年清单。p.184注1–4全部与正文标记回链；p.184正文coverage转complete。跨页修正p.185“Scene from the Life of Cato”的作品候选映射并连接p.184注4的现藏报告。复合段覆盖至L357，继续L358–360。


迁移后核验：audit_tables.py --summary errors=[]；保留两条既存enrichment source_ref警告、474段queued及9段reviewed/partial。tests/test_audit_tables.py：11 passed；git diff --check通过（仓库提示行尾转换，不构成检查失败）。24条新增提及锚点均与S0复合段匹配，11条statement、候选外键、脚注回链和p.184 complete状态有效。机械检查不是独立语义验收。

## 第七章印刷页185脚注L358–360（2026-09-30）

按源序迁入p.185注1–5并对照CHP-7.pdf物理第23页。注1复用de Cosnac《Les richesses du Palais Mazarin》及作者候选；注2确认Hautecœur《L’Histoire des Châteaux du Louvre et des Tuileries》pp.39–49；注3的ibid.回指同书，定位pp.84–89；注4依据书目对应Jean Alazard 1924年Strozzi研究；注5连接Brienne《Mémoires》卷III pp.88–90。引文页均未独立查阅，记录的是Haskell提供的书目定位。

p.185正文购藏i20–i22分别回链注1，Romanelli历史画i25、Vigarani剧场i26、织物取得i29、死前看画与Brienne引语i30分别回链注2–5。页图确认印本卷号III，S0 OCR为IH；保留S0并在注5 citation statement记校读差异。新增5个候选、9条提及和5条citation statement，7条正文标记链接完成；p.185 coverage由partial转complete，复合段覆盖扩至L294–360并继续partial。

迁移后核验：`python scripts/audit_tables.py --summary`为0 errors；警告仍为两条既存enrichment `source_ref`、474段queued和8段partial。`python -m pytest tests/test_audit_tables.py -q`：11 passed。9条新提及锚点逐项匹配S0拼接跨度；候选外键、citation statement、7条正文回链和coverage状态均核对通过。机械校验不代表独立审读被引页面或全书语义验收。



## 第七章印刷页186–187脚注L361–367（2026-09-30）

按源序迁入p.186注1、p.187注1–6并核对PDF物理第24–25页。p.186注1：Wittkower 1958 p.269；书目唯一对应Art and architecture in Italy 1600 to 1750。p.187注1–3：Alazard passim、Bonnaffé pp.68–69/113–115、Alazard p.110和Ruffo p.298；复用已识别出版物与cand-3555未定名Ruffo出处。注4的Pascoli卷I p.127定位Mola叙述，卷II p.124定位Canini两项原书陈述；Canini、Cardinal Chigi姓名不完整，保持S3待对齐。注5重用并补全Limentani 1950、de Rinaldis 1939书目候选，识别Bailly 1899目录；分别记录态度变化、献画者与未定作品、1697年Versailles至Paris转移和附随便笺。献画年份未明；1697只绑定后续调运。注6连接Blunt 1953、Wittkower 1958、Hautecœur及Chantelou书目条目。引用页未独立查阅，Ruffo书目身份未解决。

页图校读注2 `p. no.`→`p.110`、注3 `RufFo`→`Ruffo`、注6 Wittkower年份1938→1958；另记p.186–187正文L216、L225、L227、L230的视觉校读差异，来源保持不改。新增10个候选（cand-7101–7110）、39条提及、14条书目定位statement及6条脚注断言；7个既有出版物候选据本书书目补明。p.186与p.187正文statement分别回链注1及注1–6；p.187注4、5内容以新statement保留。全账本278 complete、6 partial、45 excluded、474 queued；候选7,101、提及11,936、statement 5,926。下一范围L368–369（p.188注1–2）。

迁移后核验：39条新提及的源跨度均逐项定位在复合段L293–389中；statement与候选外键、脚注标记及正文互链、coverage变更已作定向核查。机械校验不等于独立审读被引页面或全书语义验收。

## 第七章印刷页195正文迁移（2026-09-30）

p.195正文L39–46已完成语义处理，新增21个候选、76条mention、31条statement；闭合p.194引语，并建立新开放句至p.196的续页关系。页图校读、身份未决项和后置脚注待办见过程记录。`audit_tables.py --summary`为0 errors，审计测试11 passed；复合段及页尾脚注尚待后续coverage收口。

## 第七章印刷页188脚注L368–369迁移（2026-09-30）

按书序迁入p.188注1–2，并对照CHP-7.pdf物理第26页。注1以Wittkower作者候选cand-2818和《The Sculptures of Gian Lorenzo Bernini》（1955）出版物候选cand-4383记录pp.230–231；注2的ibid.回指注1同书，记录pp.234–236。两个脚注statement分别回链p.188正文i17与i21；新增3条精确提及、2条citation statement，不将引文页定位表述成独立核验。
p.188正文coverage转complete；复合段覆盖扩至L294–369并保持partial。audit重计mentions.csv为11,939条唯一提及，book-statements为5,928条；当前全书279 complete、5 partial、45有理由排除、474 queued。此前状态摘要所列提及12,139与主表写前行数11,936相差203；没有从现存材料确认差额来源，当前状态以主表和审计输出为准。下一范围p.189注1–6（L370–374）。

## 第七章印刷页189脚注L370–374迁移（2026-09-30）

按源序迁入p.189注1–6，对照CHP-7.pdf物理第27页。书目可识别Soprani/Ratti、Pascoli、Wittkower 1938–39文章、Montaiglon、Bellori 1942、Zanotti 1739、Alazard和De Dominici 1843；引文页均未独立阅读。注4除Zanotti、Montaiglon、Alazard定位外，另拆录Haskell关于1685年未具名罗马法国学院负责人试图请Luca Giordano作画及画家未履行义务的两条叙述；不将此人与正文询问Carlo Cignani的未具名负责人合并。
页图校读确认L373脚注印作5，S0将注号识作6；正文L255脚注标记同样由S0 OCR识作6、印本为5。S0保持原状，改正只记S2 `ocr_corrections`，正文statement的`footnote_marker`指向注5。新增7个候选、26条精确提及、12条statement；补充细化3个既有出版物候选。p.189正文coverage转complete，复合段扩至L294–374并保持partial。当前全书280 complete、4 partial、45有理由排除、474 queued；候选7,108、提及11,965、statement 5,940。`audit_tables.py --summary`为0 errors，11项审计测试通过；下一范围p.190注1–5（L375–378）。

## 第七章印刷页190脚注L375–378（2026-09-30）

新增12个候选、19条提及和10条statement；Harris两篇文章、Ghelli、Maclaren、Roma XIX、1677年Avviso、Society of Antiquaries及其相簿均已锚定。p.190五处脚注标记完成回链，p.190正文coverage转complete。页图校读记录`i960`→`1960`、`politics!`→`political`及正文L263、L264、L266误识；S0未改。相簿与p.191的三十卷绘画集保持分立。全账本281 complete、3 partial、45 excluded、474 queued；候选7,120、提及11,984、statement 5,950。审计0 errors，11项测试通过。下一范围L379–387（p.191注1–4、6–8、10–11）。



## 第七章p.191–194正文与脚注接续（2026-09-30）

p.191–192正文及注释复合段已迁入并闭合；p.193正文与注2、p.194正文与注2迁入。p.193跨页概述由p.194 L24续完；p.194末尾意大利引语仍续至p.195。p.193注1、3及p.194注1、3、4留待后置脚注L98–102处理。p.194新增17个候选、73条提及、35条statement。账本803段现为284 complete、2 partial、46 excluded、471 queued；候选7,177、提及12,195、statement 6,032。`audit_tables.py --summary`为0 errors；审计测试11 passed。下一源段为`chp-7:07_CHP-7_sec_iv:l38-46`（p.195正文）。

## 第七章印刷页196正文迁移（2026-09-30）

p.196正文L49–60及页内注2 L61已完成语义处理，新增23个候选、69条mention、25条statement；闭合p.195“A Sea triumph”描述。段落仍为partial：L60句子续至p.197，注1位于L107。PDF校读及作品/地点/政治实体区分记于过程记录。`audit_tables.py --summary`为0 errors，审计测试11 passed。

## 第七章印刷页199第V节正文迁移（2026-09-30）

p.199 L3–7完成语义阅读并迁移为10个候选、46条提及和14条原书statement。记录意大利赞助环境、罗马与北方中心、英德收藏者、意大利艺术家的跨城活动、Haskell对八位画家的群体评价，以及1683年Vienna与1684年Venice—Holy League叙述。跨页末句保持partial；页图校正Francéschini→Franceschini只存于S2，S0未改。前一节p.199页底脚注不重复迁移。详细判断见[过程记录](../process/stages.md)。


## 第八章印刷页207–208正文迁移（2026-09-30）

p.207规范段L43–51按S0顺序迁入，新增15个候选、53条提及和17条statement。页图校读仅记S2，S0不改；跨页反问在p.208 L54闭合，p.207脚注1–2仍待复合来源段L136–137迁入。

p.208规范段L53–60新增10个候选（cand-7455–cand-7464）、47条提及和23条statement。记录Roomer对Giordano的评议与支持、自然主义偏好、Codazzi/de Wael/Ruoppolo作品往来、南北文化影响及Rubens《Feast of Herod》的影响；分别记录Jan与Ferdinand van den Einden的商业/父子/继承/收藏/赞助关系、Preti三件题材及Giordano作品未识名的知识缺口。p.206的Jan Vandeneynde与本页Jan van den Einden的身份关系留待S3裁决。

对照`CHP-8.pdf`物理第5–6页：p.208页图确认OCR校读，并将L60注号8更正为印本6。10个新候选、47条精确跨度提及、23条statement通过来源哈希、引用复现、外键及跨度dry-run后写回；`audit_tables.py --summary`为0结构错误，`tests/test_audit_tables.py`为11 passed。当前805段为302 complete、5 partial、52 excluded、446 queued；总候选7,455、提及13,107、statement 6,423。仍有两条既存enrichment `source_ref`警告。下一段为p.209 `chp-8:08_CHP-8_sec_i:l62-70`。

## 第八章印刷页209正文迁移（2026-09-30）

p.209规范段`chp-8:08_CHP-8_sec_i:l62-70`新增11个候选（cand-7465–cand-7475）、43条精确跨度提及和21条原书statement。记录Don Antonio Ruffo的Messina背景、贸易和税收收入、1661年支持Messina城市特权后短暂被列为outlaw、艺术赞助及其宫殿/超过350幅藏画；记录约1646年开始收藏、母亲Duchess of Bagnara建宫、约三十年持续收购、出行范围和信息代理网络、当代艺术兴趣、尺寸/费用标准、对称陈列和成对委托，以及Guercino按Rembrandt《Aristotle contemplating the Bust of Homer》匹配作画和具体价格谈判。125 ducats/figure、100 scudi与后续100 ducats按原单位保留，未换算。

页图核对`CHP-8.pdf`物理第7页；S0 OCR误读`Use`、`Emnianuela`和`halfa`只在S2记为life、Emmanuela、half a。p.209 note 1位于`08_CHP-8.md` L135，尚未迁移；L70“representative collection”续至p.210 L73，本段coverage为reviewed/partial。dry-run通过来源哈希、提及跨度、引用复现及外键校验后写回。写回后805段总账为302 complete、6 partial、52有理由排除、445 queued；候选7,466、提及13,150、statement 6,444。`audit_tables.py --summary`为0 structural errors，审计测试11 passed；仍有两条既存enrichment `source_ref`警告。下一规范段为p.210 `chp-8:08_CHP-8_sec_i:l72-82`。

## 第八章印刷页210正文迁移（2026-09-30）

p.210规范段`chp-8:08_CHP-8_sec_i:l72-82`新增13个候选（cand-7476–cand-7488）、95条精确跨度提及和27条原书statement。闭合p.209代表性收藏句；逐项记录Ruffo对Rembrandt作品的购藏与反应、Abram Breughel报告、Guercino配对图与藏画数量、Neapolitan/South Italian艺术家及收藏计数、主题比例和189幅版画、画廊的地区影响评述，以及Florentine patrons、Via Chiara房屋和del Rosso兄弟。保留`probably`、`probably not being insincere`、`seems`、`must have been`、`undoubtedly`和`most`；不把“most of these”分配至具体画家，不把关系候选提前写成S6正式边。Novelli、Ribera及del Rosso三兄弟依据p.210索引页范围映射候选，最终身份仍待S3全局对齐。

对照`CHP-8.pdf`物理第8页，记录S0 OCR `desiderate`→印本`desiderare`、四处`Russo`→`Ruffo`、`picture`后的杂散引号和`he. also`中的句点；S0不改。p.210无印刷脚注；末句所列三兄弟的姓氏由p.211 L85续接，故coverage为reviewed/partial。迁移前dry-run核验来源资产/段落哈希、候选号、95条提及范围、27条原文引句和外键；迁移后`audit_tables.py --summary`为0 structural errors，`tests/test_audit_tables.py`为11 passed，`git diff --check`退出码0（仅报告仓库既有LF/CRLF提示）。总账为302 complete、7 partial、52有理由排除、444 queued；下一段为`chp-8:08_CHP-8_sec_i:l84-96`（p.211）。


## 第八章p.204脚注1–3（2026-09-30）

合并注释来源段`chp-8:08_CHP-8_sec_i:l126-157`的L127–129对照`CHP-8.pdf`物理第2页完成审阅并迁移。新增5个候选（cand-7578–cand-7582）、18条提及及9条statement；复用现有出版物、人物、地点和画家候选。p.204正文段转为reviewed/complete；合并注释段标为reviewed/partial，仅覆盖L127–129。引用页未独立核读，未名收藏者及Codazzi画组保留为未决候选。p.35与卷号III的OCR校读只写入S2，原S0不改。下一范围为L130–133（p.205注1–4）。

## 第八章p.206脚注1–2（2026-09-30）

复合注释段L134–135已迁入：新增Burchard 1953文章候选cand-7592、7条提及、2条citation statement；两条脚注分别链接Falcone–Roomer正文statement与Rubens《Feast of Herod》正文statement。页图校读记录`pp. 383— 387`→`pp. 383-387`，不改S0。p.206正文coverage转reviewed/complete；复合注释段coverage为L127–135，仍partial。L136–157尚未处理，须按实际印刷页映射并比对p.211视觉转录，避免重复写入。当前账本806段：308 complete、7 partial、52 excluded、439 queued；候选7,583、提及13,589、statement 6,566。审计errors=[]，11项审计测试通过。

## 第八章印刷页207脚注1–2（2026-10-01）

复合注释段L136–137已对照CHP-8.pdf物理第5页迁移，并回链p.207正文注1–2。新增6个候选、23条提及、11条statement；引文页未独立阅读，未具名女儿身份和多数画作来源链均保留限定。页图校读`imturn`→`in turn`只记S2。p.207正文coverage为reviewed/complete，复合注释段覆盖扩至L127–137、仍partial；下一范围为L138–144（p.208注1–7）。审计0结构错误，审计测试11项通过；全书S2仍有439段queued、6段partial。


p.208注1–7（复合段L138–144）已按物理页6迁入并回链，新增8条提及、8条原书statement，未新增候选。Ruffo 1916年文章候选已据本书书目补全；页图OCR校读只记S2且原始引句保持S0 OCR。当前coverage表为310 complete、5 partial、52 excluded、439 queued；下一待办是p.209注1（L145），随后去重核对L146–148与p.211视觉转录，再处理L149–157。


p.209注1（L145）已迁入并回链：V. Ruffo 1916年文章为整节提供书目指引，S. Slive 1953年著作为Ruffo–Rembrandt陈述提供pp.59 ff.定位；两项所引来源均未独立阅读。cand-3474据印本文字与本书书目补全为Vincenzo Ruffo，并与Don Antonio Ruffo分立；新增Slive作者和著作候选、4条提及及2条statement。p.209正文转complete，复合注释段覆盖到L145。全账本311 complete、4 partial、52 excluded、439 queued；下一步L146–148须与p.211视觉转录核对后复用，再处理L149–157。


p.211注释重叠L146–148已与视觉转录段对照并复用既有22条提及和8条statement，没有重复写入。页图将Gualandi II引用页码校正为pp.115–128（两份文本转录为113–28）；OCR原文保留，更正记录在S2。coverage扩至L127–148，统计数不变。下一待办L149–157（p.212–214），其中p.214注4需补页图转录。

## 第八章p.212–214正文脚注及补录（2026-10-01）

已完成p.212注1–5、p.213注1、p.214注1–4及`chp-8:08_CHP-8_sec_i:l126-157` L149–157；p.214补充视觉转录单列为新S0/S2段，补回漏录注2与注4截断续文。新增26个候选、73条提及、28条statement；关闭p.212、p.213、p.214正文和复合脚注4个partial coverage，并将视觉转录段登记为reviewed/complete。p.211重复段复用，不重复计数。全账本807段：316 complete、52 excluded、439 queued、0 partial；候选7,617、提及13,697、statement 6,615。结构审计errors=[]；审计测试11 passed；仍有两条既存enrichment `source_ref`警告。下一源段`chp-8:08_CHP-8_sec_ii:l1-1`。

## 第八章第二节p.214引言（2026-10-01）

排除生成分节标签`l1-1`；审阅`l3-9`正文L3–6并复用L7–9已处理的重复脚注。新增19条提及、6条statement，不新增候选。印本校读`Don Antonio Russo`为`Don Antonio Ruffo`只记S2。最后一句由p.215 L12续完，故引言段保持partial；p215规范段`chp-8:08_CHP-8_sec_ii:l11-19`为下一任务。账本807段：316 complete、53 excluded、437 queued、1 partial；候选7,617、提及13,716、statement 6,621。结构审计errors=[]；语义过程仍未完成。


## 第八章p.215–216正文与p.215注1–2迁移（2026-10-01）

对照CHP-8.pdf物理第13–14页完成p.215正文L12–19、p.216正文L22–35及p.215注1–2（后置复合段L373–374）。p.214 L6片语由p.215 L12闭合，p.215 L19的协商叙述由p.216 L22续接；p.216 L35止于thirteen，续至p.217 L70，故p.216仍reviewed/partial。脚注复合段L375–461尚未处理，coverage仍partial。

新增35个候选（cand-7627–cand-7661）、75条精确提及、30条statement；复用索引候选中的Campione、Ricchini、Cavagna、Storer、Procaccini、Magni、Cocchi、Guercino、Brusasorci、Massimo等。新增教堂及建筑构件/内部作品、圣母大殿装饰计划、四幅未识名绘画、Pesenti/Pinetti书目对象与Coggiola/Biblioteca Civica。将Venice city与作为统治者的Republic of Venice分开；Guercino提案与p.204已登记的另一幅Marriage at Cana分开；Padre Massimo具体画作与通用题材候选分开。计划、委托、已完成作品及未成功请求按原文分别限定，不生成正式关系。

将p.214既有statement的引句边界修到旅行者陈述结束处，并把p.214 L6的下一句片语交由p.215独立statement处理。注1的Pesenti仅凭书目定位到P. Pesenti 1938年专著；注2的Pinetti 1916年文章由本书书目补足题名、刊物和页码；两项引文均未独立核读。记录Haskell对文件来源、个人解释及对Dora Coggiola致谢的说明。

按页图仅在S2记录OCR校读：p.215 growup→grow up、Bcrgamasque→Bergamasque；p.216 die→the、cominittee→committee、tó→to、promise-of→promise of、facob’s→Jacob’s及 Guercino句尾残留“- .”。S0原文件和PDF均未改。写入前脚本dry-run核对来源哈希、候选序号、75个精确提及跨度、statement引句、脚注链接及外键；四表备份保留。应用后audit_tables.py --summary为0 errors，tests/test_audit_tables.py为11 passed，git diff --check为0（仅Git的LF/CRLF提示）。

当前总账807段：318 complete、53有理由排除、434 queued、2 partial；候选7,652、提及13,791、statement 6,651。另有两条既存enrichment source_ref警告。下一正文段为chp-8:08_CHP-8_sec_ii:l69-76（p.217）；脚注后置复合段在后续书序中继续。


## 第八章Plate 33–36图版页（2026-10-01）

按PDF物理页15–18核对并处理Plate 33–36。S0 OCR Plate 33a作者名与Plate 35页标按印本校记；Plate 35b漏失题注及旋转错序的Plate 36组题/题注以派生转录补录；编辑性组题不转成研究层级或关系。复用书前图版目录候选，新增22条提及、16条statement、0候选，新增4个可行号视觉转录段；原PDF和原OCR保持不变。

当前S0/S2范围811段：325 complete、2 partial、54有理由排除、430 queued；候选7,652、提及13,813、statement 6,667。`audit_tables.py --summary` errors=[]；两条既存`enrichment.source_ref`警告尚未修复，且全书S2显然未完成。下一段`chp-8:08_CHP-8_sec_ii:l69-76`（p.217），随后继续处理书后置脚注段未覆盖行及全书其余来源。

## 第八章印刷页217–218正文及两条脚注（2026-10-01）

p.217–218正文与p.217 n.1、p.218 n.1已迁入；p.217闭合p.216北耳堂方案句，Ferri请求在p.217/p.218之间闭合，p.218末句留待p.219续完。新增16个候选、60条提及、19条statement；OCR校读仅记S2。当前811段：326 complete、3 partial、54排除、428 queued；候选7,668、提及13,873、statement 6,686。`audit_tables.py --summary`无结构错误；审计测试通过。下一正文段`chp-8:08_CHP-8_sec_ii:l86-98`（p.219），其后继续后置脚注L377–461及全书余下queued段。

## 第八章印刷页219–220语义迁移（2026-10-01）

p.219正文及n.1–2迁入后，p.220 L101关闭Cignani备选句。p.220对照PDF物理页22处理完正文语义，并记录Cignani的穹顶工作及尺度/透视异议、Ludovico David的报价和评画方案、Franceschini谈判、Melanconici的Abraham试画。脚注OCR `Bonari`校为印本`Bottari`，原始S0保持不变。p.220末句续到p.221 L113，故该段partial；脚注合并段覆盖至L379。新增2个候选、34条提及、12条statement。最终审计errors=[]，`test_audit_tables.py`通过。811段当前为329 complete、2 partial、54 excluded、426 queued；候选7,684、提及13,964、statement 6,720。下一段p.221正文`chp-8:08_CHP-8_sec_ii:l112-124`。


## 第八章印刷页221正文与注1–2（2026-10-01）

p.221正文及n.1–2对照PDF物理页23迁入，新增10个候选、52条提及、16条statement。p.220试画句在p.221 L113闭合，p.220转complete；p.221 Ferrerio雕像句续至p.222 L127，保持partial。S2校读记录Russo→Ruffo、bom→born及两处OCR标点误识，来源文本未改。注1连接Pinetti 1920文章、注2连接Moroni卷69辞典，引文页均未独立阅读。审计发现后置注释里的作者名和作者-年份出版物span相交，现改为严格嵌套mention并保存恢复副本。最终`audit_tables.py --summary` errors=[]，审计测试11项通过。当前811段为330 complete、2 partial、54 excluded、425 queued；候选7,694、提及14,016、statement 6,736。下一正文段为`chp-8:08_CHP-8_sec_ii:l126-138`（p.222）；注释复合段尚有L382–461待读。


## 第八章印刷页222正文与注1–5（2026-10-01）

p.222正文、内嵌注4及复合段注1–3、5对照PDF物理页24迁入，新增18个候选、87条提及、25条statement。p.221 Ferrerio雕像句由L127闭合，p.221转complete；p.222 Ruffo—Creti句续至p.223 L140，保持partial。页图校读Russo→Ruffo、Clement XI、作品/引文OCR及注号只记S2，来源OCR未改。脚注报告涉及Baruffaldi手稿、Agnelli画廊清单、Breval引用、Juan de Pareja画作在1704展出与后续藏所、Crespi作品藏于Museo di Palazzo Venezia；引文与藏所未独立核验。The Finding of Moses与索引cand-0879不合并，留S3身份对齐。

应用后`audit_tables.py --summary` errors=[]，`test_audit_tables.py` 11 passed。当前811段：331 complete、2 partial、54 excluded、424 queued；候选7,712、提及14,103、statement 6,761。仍有两条既存enrichment `source_ref`警告。注释复合段覆盖L373–385，下一正文段`chp-8:08_CHP-8_sec_ii:l140-150`（p.223）。

## 第八章印刷页223正文与注1–5（2026-10-01）

p.223对照PDF物理页25迁入正文L140–150及复合注释L386–388，新增25个候选、79条提及、45条statement。p.222 Creti续句由p.223 L141闭合；p.222转complete。p.223 Buonaccorsi宫殿比较句续至p.224 L152，p.223保留partial。注2、注5在正文OCR段，注1、3、4在后置注释段。三封档案信、书目引文及致谢均只作Haskell的报告/来源定位，未独立核读。OCR更正只记S2。首次审计暴露candidate source-ref格式错误，已按schema改成精确单行引用；最终audit errors=[]，审计测试11 passed。当前811段为332 complete、2 partial、54 excluded、423 queued；候选7,737、提及14,182、statement 6,806。下一正文段p.224 `chp-8:08_CHP-8_sec_ii:l152-161`；注释复合段下一待读L389。


## 第八章印刷页224正文及注1–4（2026-10-01）

p.224（PDF物理第26页）完成语义迁移，新增18个候选、59条提及、20条statement。正文记录Buonaccorsi宫殿施工与Contini建筑师、Raimondo约1707年启动长廊装饰、《Aeneid》题材与壁画/架上画的区别、Rambaldi与Dardani的穹顶壁画、Garzi对Venus画作的限定归属，以及Solimena《Dido welcoming Aeneas to the Royal Hunt》的图像叙事与作者评价。p.223宫殿跨页句关闭；p.224末句续到p.225 L164，故p.224 partial。注1–4迁入，注4尾段L161随正文段保存；引文来源和档案信未独立核读。S2校读仅记`fight`、`iconographie`、引句及引文页码/OCR差异，未改S0。全账本811段：333 complete、2 partial、54有理由排除、422 queued；候选7,755、提及14,241、statement 6,826。下一正文段`chp-8:08_CHP-8_sec_ii:l163-177`（p.225），注释复合段从L392继续。

## 第八章印刷页225正文及注1–9（2026-10-01）

p.225（PDF物理第27页）正文段`l163-177`及脚注1–9完成语义迁移，新增19个候选、87条提及及26条statement。p.224关于Solimena画作引发兴趣的句子由L164闭合；Haskell关于Raimondo可能属于启蒙赞助人的推测续至p.226 L180，故正文段保持partial。后置脚注覆盖扩至L373–398，仍partial。账本811段现为334 complete、2 partial、54有理由排除、421 queued；候选7,774、提及14,328、statement 6,852。`audit_tables.py --summary` errors=[]，审计测试11项通过。下一正文段p.226 `chp-8:08_CHP-8_sec_ii:l179-188`，下一脚注范围L399–461。

## 第八章印刷页226正文及注1（2026-10-01）

p.226（PDF物理第28页）新增13个候选、59条提及及19条statement。正文闭合p.225关于Raimondo私人寓室的比较；处理Stefano Conti的97幅小型藏画、来源城市、履历、收藏过程与保存意图、购买和委托规则、Alessandro Marchesini的代理工作及Carlo Cignani学派。未把Conti与Raimondo、收藏与画廊、实际存世信件与“定期写信”混为一谈；父亲接受Lucchese贵族身份的年代保留为相对“早约四分之一世纪”，不伪造确年。将收藏类型和Cignani“school”的组织属性留待后续判断。p.226 L188付款句续至p.227 L190，故本段partial；后置注释覆盖至L399。

注1引Haskell, 1956为本节来源，并称其列有Lucca图书馆/档案馆手稿完整出处；未据此猜定出版物题名或逐项声称查阅相关手稿。页图校读只记S2、未改S0：L182 `lie`→`he`；L183 `Conti_was`→`Conti was`、`cloth,,`多余标点、`siom`→`from`、`silled`→`filled`；L184 `originals`→`original`；L187 `siom`→`from`。`audit_tables.py --summary` errors=[]；定向审计测试11项通过。全账本811段：335 complete、2 partial、54有理由排除、420 queued；候选7,787、提及14,387、statement 6,871。下一正文段p.227 `chp-8:08_CHP-8_sec_ii:l190-204`，后置注释下一范围L400–461。

p.227（PDF物理第29页）正文新增26个候选、71条提及及13条statement，并迁入注1–3（L400–402）。闭合p.226按画中人物数计价的续句；Franceschini提出的牧歌题材被接受但不视为已完成作品，Torelli题材画到达后仍被Conti追问其内容。记录Conti画廊的艺术家与风格评价、家庭肖像、Cassana水果/动物画、景观、Carlevarijs威尼斯景观及Mazza双胸像；Angiolo Trevisani不与Francesco Trevisani合并，争议题材归属及未具名作品保持限定。p.227末句续至p.228 L207，故coverage为partial；p.226转complete。注1、2所引MS.3299书信分别日期1705-02-17和1705-02-24，后者签署人未定；注3引Da Canal pp.40、58、59，均未独立核读。页图校读只记S2，不改S0。audit_tables.py errors=[]，定向测试11项通过。全账本811段：336 complete、2 partial、54有理由排除、419 queued；候选7,813、提及14,458、statement 6,884。下一正文段p.228 chp-8:08_CHP-8_sec_ii:l206-214，下一脚注范围L403–461。

p.228（PDF物理第30页）正文及注1已迁入：新增6个候选、47条精确提及、17条statement；闭合p.227 Carlevarijs引语（实际续句在L207，L206为页码标记），识别Canale/Canaletto和两组Ricci作品、Conti对Carriera及Crespi的购买/委托，以及Crespi改题《The Finding of Moses》的报告。注1只登记MS.3299与Zanotti II p.62引文定位，未声称独立查阅。页图确认OCR `Rosalba Garriera`应读作`Rosalba Carriera`，只修正S2记录。总账811段：338 complete、1 partial、54 excluded、418 queued；候选7,819、提及14,505、statement 6,901。结构审计errors=[]，定向测试11项通过。下一正文段p.229 `chp-8:08_CHP-8_sec_ii:l216-225`，后置注释L404–461。


p.229（PDF物理第31页）正文及注1–2已迁入：新增8个候选、38条精确提及、21条statement；记录Ferdinand的赞助与品味、家族关系及婚姻和继承语境，保留Haskell的心理/艺术史判断。OCR脚注标号、书目和脚注页图校读见过程记录；p.228 Medici指代已由p.229 L217解析。末句续至p.230 L228，保持open；后置注释覆盖至L404。总账811段：339 complete、1 partial、54 excluded、417 queued；候选7,827、提及14,543、statement 6,922。`audit_tables.py --summary` errors=[]，定向审计测试11项通过。下一段p.230 `chp-8:08_CHP-8_sec_ii:l227-236`，后置注释L405–461。


## 第八章印刷页230正文及注1–5（2026-10-01）

p.230（PDF物理第32页）正文及注1–5迁入，新增18个候选、46条精确提及及21条statement。正文记录Ferdinand的乡间居所、音乐与剧场、作家赞助、健康和去世，以及1696年威尼斯游历及其娱乐；继承句闭合p.229，末句续至p.231 L239。后置注释覆盖扩至L408；不确定的Regent、匿名当代引语作者和Ombrosi归属均保留待决/概率措辞，档案及被引文献未独立核读。OCR校读只记S2。`audit_tables.py --summary` errors=[]，`tests/test_audit_tables.py` 11 passed，迁移脚本`py_compile`通过。全账本811段：339 complete、2 partial、54有理由排除、416 queued；候选7,845、提及14,589、statement 6,943。下一正文段p.231 `chp-8:08_CHP-8_sec_ii:l238-249`，注释下一范围L409–461。

## 第八章印刷页231–241正文、图版与后置注释（2026-10-01）

p.231–234按印刷页和源段迁入正文与注释，处理Plate 37、38、40可读题注及Plate 38派生题头；各页跨页句均回到承载其续文的页段。新增100个候选、323条提及和91条statement。p.235–237继续处理Ricci、Crespi、Ferdinand及相关收藏、委托与往来记录，分别新增74个候选、274条提及和54条statement。引文与档案只按原书作来源定位；转述、推测、未识名作品、身份和行程不确定性均保留。

p.238（PDF物理第44页）处理正文`chp-8:08_CHP-8_sec_ii:l327-336`及后置注释L443–448，新增19个候选、98条提及和27条statement。p.237末句由L328闭合；分别记录Crespi与Ferdinand的联系、返回Bologna、Ricci和Pepoli往来、送画与委托等内容。正文日期为约数时保留约数；三条Pepoli通信与正文“两封信”的对应关系不确定，不强行逐封匹配。p.239正文`l338-348`及注释L449–451新增10个候选、66条提及和24条statement；不把Livio Mehus未具名之子实名化，并保留“this”所指作品未定。

p.240–241对照PDF物理第46–47页迁入正文`l350-359`、`l361-370`及后置注释L452–461，新增46个候选、175条提及和37条statement。p.239关于威尼斯绘画的未完句于p.240 L351闭合；L452虽处于合并注释OCR段，页图确认其为p.240正文续文，因此按`body continuation in consolidated OCR segment`保留文本层语境。p.240记录Livio Mehus作品与宫廷收藏、Ferdinand的展示和赞助政策及1706年展览；p.241记录展览借展、画家与作品、借展者及其后续影响。Marco Ricci四幅风景画的出借人保留为高概率判断；Cardinal Medici、Grand Duke、第一lunette的12幅画与肖像、del Rosso兄弟群体及特殊房间均未强行合并或实名化。脚注引文、档案与书目未独立核读；OCR校读只保留在S2，不改S0。

受控脚本`chp8_p240_241_migration.py`以dry-run预检来源哈希、候选与提及锚点、statement及外键，并在写入前为四张表创建备份。全账本更新为812段：356段reviewed/complete、54段有理由排除、402段queued、0段partial；候选8,094、提及15,525、statement 7,176。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；`tests/test_audit_tables.py` 11项通过，`git diff --check`通过（仅有既存LF/CRLF提示）。全书S2仍未完成。下一源段为`chp-9:09_CHP-9_intro:l1-1`；先判断该分节标题段的来源功能并按理由处置，再继续第九章实质文本。

## 第九章印刷页250正文与注释延续（2026-10-01）

p.250 `chp-9:09_CHP-9_intro:l90-104`完成语义迁移并闭合p.249 L86跨页句，新增33个候选、64条提及和15条statement；Zenobio、Widmann、Labia赞助人与宫殿/宅邸、Carlevarijs、Lazzarini、Dorigny、Tiepolo及库存题名均按原书断言范围登记，未把转述、约数或未识别作品升级为确定事实。p.249和p.250均转complete。全账本为814段：364 complete、60 excluded、390 queued、0 partial；候选8,206、提及15,817、statement 7,266。`audit_tables.py --summary` errors=[]，定向测试9项通过。下一源段为p.251 `chp-9:09_CHP-9_intro:l106-114`；全书S2仍未完成。

## 第九章印刷页251正文与页下注（2026-10-01）

p.251正文与页下注1–4新增24个候选、66条提及及19条statement；p.252 L117闭合p.251末句，故该正文段已转complete。p.252正文与注1–7新增34个候选、107条提及及32条statement；记录Ricci的雇佣分布、Tiepolo的题材/风格/赞助、Dolfin家族和成员、Aquileia职位、Dionisio在Udine的居住及图书馆。14处OCR/页图差异只在S2记录，S0未改。Da Canal等被引来源依本书书目辨认；注释仅为引用/报告定位，未独立核读。p.252末句续至p.253 L124–132，p.252保持partial；合并注释段覆盖至L359并保持partial。全账本814段：365 complete、60 excluded、387 queued、2 partial；候选8,264、提及15,990、statement 7,317。`audit_tables.py --summary` errors=[]，`tests/test_audit_tables.py` 11 passed；仍有两条既存enrichment `source_ref`警告。下一排队源段为p.253 `chp-9:09_CHP-9_intro:l124-132`。


## 第九章印刷页263–264正文与注释（2026-10-01）

p.263（PDF物理第25页）`chp-9:09_CHP-9_intro:l231-238`、p.264（物理第26页）`l240-249`及合并注释L414–427完成逐段语义迁移，新增35个候选、75条提及、31条statement。登记Sagredo家族与Zaccaria、Niccolò的公共/家族语境、收藏与交易、转引文献及遗嘱；保留来源层次、评价和不确定限定。p.263 note 6跨页引文在p.264 L245–248闭合；p.264 note 8 L427指向p.265 L295–296并保持partial。L428重复Plate 46题注，排除重复迁移。当前816段：380 complete、60 excluded、375 queued、1 partial；候选8,593、提及16,759、statement 7,631。结构审计errors=[]，审计测试11项通过；下一段为Plate 45 `chp-9:09_CHP-9_intro:l251-256`。


## 第九章Plate 45–46图版与视觉转录（2026-10-01）

Plate 45–46对照PDF物理第27–28页核读；两段倒置OCR保持不变，在既有视觉转录文件分别补入L6和L8–9。Plate 45确认Batoni《Triumph of Venice》；Plate 46题注确认Pellegrini《Pierre Motteux and his family》，并将“Venetian artists in England during the early years of the eighteenth century (see Plates 46 and 47)”保存为图版导航题头，不另造主题实体。两版共新增5条提及、3条statement，无新增候选。Plate 46的分组题头在合并注释L428重复，已排除重复OCR。当前818段：384 complete、60 excluded、373 queued、1 partial；候选8,593、提及16,764、statement 7,634。audit_tables.py --summary errors=[]，tests/test_audit_tables.py 11项通过。下一规范段为Plate 47 chp-9:09_CHP-9_intro:l279-285；注8续文待p.265 L295–296。

## 第十章印刷页278–279正文（2026-10-02）

p.278新增32个候选、72条提及和32条statement，闭合p.277跨页句；p.279新增26个候选、61条提及和24条statement，闭合p.278 Manchester委托句。记录德意志宫廷艺术购买与画家流动、Manchester及其英格兰宅邸、Lord Carlisle与Castle Howard、Fountaine与Narford Hall，以及Pellegrini、Marco Ricci、Sebastiano Ricci的赞助/风格关系。p.276“a year later”与p.278 1709年使馆时间仍未调和；p.279 Lord Portland句续至p.280 L52。页图校读只记S2，S0不改；p.278注1–6及p.279注1–3待合并注释源段处理。写入前四表均留有恢复副本；当前820段为405 complete、62 excluded、352 queued、1 partial，候选8,897、提及17,611、statement 8,041。audit_tables结构审计errors=[]、定向测试退出码0；下一段为p.280 `chp-10:10_CHP-10_intro:l51-61`。

## 第十章印刷页280正文（2026-10-02）

p.280新增30个候选、79条提及和25条statement，闭合p.279 Portland句；记录Portland—Pellegrini委托、Bentinck—William III及Orange cause背景、Portland肖像和Bulstrode Park chapel四件画作、Burlington—Ricci雇佣与Piccadilly室内布置、Chelsea Hospital壁画、Bellucci到英及John Sheffield的赞助/政治关系。p.280 Prince Eugene评价句在Plate 49–52之后的p.281正文规范L126续接，故p.280仍partial。OCR校读只在S2记录，不改S0；本页注1–8留待合并注释源段处理。写回时全账本820段：406 complete、62 excluded、351 queued、1 partial；候选8,927、提及17,690、statement 8,066。该时点后续源段指针已校正；当前游标见下节。

## 第十章Plate 49–52图版与续接指针校正（2026-10-02）

对照`CHP-10.pdf`物理页6–9，新建派生转录`10_CHP-10_intro_plates_visual-transcription.md`；四个图版OCR段保留不动，四个转录段补足旋转、倒序或错序题注。Plate 50只有组题和图版号，没有独立作品题注；其作品信息沿用图版目录，不从图像推断。Plate 49、51、52题注复用已有候选，新增21条精确提及及16条原书statement；三页题注限定均保留，P. van Bleek caption 中的McSwiney与目录的McSwiny异拼留待S3。

校正p.280 Prince Eugene statement的续接锚点：图版49–52先于p.281正文，句子在规范源文件L126续接。写回后账本824段：414 complete、62 excluded、347 queued、1 partial；候选8,927、提及17,711、statement 8,082。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；`tests/test_audit_tables.py`通过，源段预览75个来源文件、824段、issues=0。下一段为p.281正文`chp-10:10_CHP-10_intro:l125-139`；p.276–280脚注仍待按源序处理。全书S2未收口。

## 第十章印刷页286正文（2026-10-02）

p.286规范段`chp-10:10_CHP-10_intro:l190-204`对照`CHP-10.pdf`物理第15页完成本轮语义阅读。p.285 L188关于London、Düsseldorf与Paris为早期1720年代威尼斯绘画中心的句子由p.286 L191闭合。记录Galilei对英格兰偏好本土艺术家的嵌套抱怨，并保留Haskell“失意建筑师”与“有一定真实性”的双重限定；记录St Paul's dome及Queen's Bed Chamber的Thornhill/Ricci委托差异、Halifax关于Treasury付款的警告、Burlington从Vicenza返英后的建筑风格，以及Grand Tour惯常化与大型历史画接受变化的作者判断。

另记录Amigoni 1730年抵英及与Bellucci离英时间关系、Lord Tankerville的欢迎/政治身份与其楼梯画后来被拆、Powis House在Great Ormond Street的Seasons与Judith and Holofernes装饰、Lord Powis的政治履历与1715 Jacobite alarm、建筑被法国大使占用/焚毁并由法国国王出资重建、1722年复产及House of Lords席位、Styles与South Sea Bubble、Moor Park的建筑者和尚未闭合的装饰委托。将空间与作品分开；Queen's Bed Chamber和屋顶/穹顶等位置不与装饰作品合并；Lord Powis是否为赞助人仍作为条件关系候选；Prince of Wales、法国国王和法国大使的身份保持待定，不从语境猜定。

印本校读仅记S2，不改S0：L200 OCR `James H`校为`James II`；`King-of France`删多余连字符；L201 `house of Lords`核为`House of Lords`。第十章合并注释源段的p.286注1（Toesca）、注2（Vertue）和注3（Dictionary of National Biography、Wheatley）尚未按源序迁移或独立查阅，citation仅保留为待处理定位。句末“Styles gave the job to”在p.287 L207续接。

受控脚本`chp10_p286_migration.py`默认dry-run，锁定来源资产/源段SHA-256、候选顺序、提及跨度、statement原文和外键、相邻coverage前态；应用前四表留有`.bak-s2-chp10-p286-20261002`。首轮审计发现三条statement引用行号范围少覆盖跨行起始/续行，及两个提及偏移重复；脚本修正后由`chp10_p286_anchor_repair.py`受控移除一条重复提及并修复行号/偏移，另为mentions与statements留`.bak-s2-chp10-p286-anchorfix-20261002`。跨候选检查发现cand-8984与cand-8104重复，移除前者并重映射提及，净新增21个候选。p.286时点审计为824段：420 reviewed/complete、62 excluded、341 queued、1 reviewed/partial；候选8,991、提及18,031、statement 8,189。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；源段生成预览75个规范来源文件、824段、issues=0。queued和partial继续阻止S2交接。

## 第十章印刷页287正文（2026-10-02）

p.287正文`chp-10:10_CHP-10_intro:l206-216`已对照物理页图迁移，新增7个候选、30条提及、15条statement。闭合p.286 Moor Park委托句，Amigoni与Francesco Sleter接手；复用cand-9004描述四幅未具题名的《朱庇特与伊俄》画，没有为同一委托另建候选。记录Amigoni的肖像事业与带款传闻、英国威尼斯画家赞助概括、McSwiny舞台生涯和未实现的Van Dyck版画计划、约1711年离英赴欧、Lord March委托提案及Haskell的英格兰乐观叙事。所有提议、转述、作者评价及约数均保留限定；p.287末句未完，链接p.288 L219。注2原位录入，其出处未独立阅读；注1、3–6待合并注释段。

写入前受控脚本核对来源哈希、候选序号、提及精确跨度、statement引句/外键和覆盖前态，并为四表保存恢复副本。结构审计首先发现McSwiny职业陈述跨到L212而行号只到L211，已受控修正；复核后824段：421 complete、62 excluded、340 queued、1 partial；候选8,998、提及18,061、statement 8,204。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；`tests/test_audit_tables.py`通过，源段预览75个文件、824段、issues=0。仍有两条既存enrichment `source_ref`警告、340段queued及1段partial；下一段为p.288 `chp-10:10_CHP-10_intro:l218-227`。

## 第十章印刷页288正文（2026-10-02）

p.288正文`chp-10:10_CHP-10_intro:l218-227`已对照`CHP-10.pdf`物理第17页迁移，新增4个候选、42条提及和17条statement。p.287 L214 “wealth at home and peace in Europe...”续句在p.288 L219闭合；之后记录Haskell对McSwiny方案成功前景的判断、拟纪念的英国君主/指挥官/其他显要人物、初始名单不确定、纪念对象多数为Whigs但无严格政治纲领、Robert Harley及Marlborough的纳入、画幅格式、世俗爱国纪念与反宗教改革图像/历史画的比较、Locke与Newton等启蒙人物、 urn/家族纹章/纪念仪式等拟议图像符号，以及作者和艺术家分工。Robert Harley、Marlborough的具体纪念画另作作品候选，系列仍沿用p.287的cand-9007；匿名群体保留为term。候选cand-9007和cand-9009的描述据本页更新。

扫描校读仅记S2，不改S0：L226 OCR `die figures`校为印本`the figures`；L227 `Donato Cred`校为`Donato Creti`。嵌套引语中的“Saints”保留为修辞，不按宗教身份处理；“with one or two exceptions”保留未名，相关注2待章末合并注释段L541。p.288注1–3对应合并注释源段L540–542，仍待按源序迁移；注1 pamphlet、注2关于Solimena/Newton/Imperiali等的引文以及注3 Zanotti尚未当作独立阅读。L227末句“All four Venetian artists were beginning their”续至p.289 L230，故coverage保持partial。

受控脚本`chp10_p288_migration.py`默认dry-run，校验源资产/源段SHA-256、候选序号、42条精确提及、17条statement引文与外键、相邻coverage前态；应用前为四表保存`.bak-s2-chp10-p288-20261002`。p.288写入后的历史快照为824段：422 complete、62 excluded、339 queued、1 partial；候选9,002、提及18,103、statement 8,221。`audit_tables.py --summary`当时为`s2_missing=[]`、`errors=[]`；保留两条既存`enrichment.source_ref`警告和S2未收口警告；`build_source_segments.py`预览75个来源文件、824段、issues=0。p.288末句在p.289 L230闭合，详情与当前覆盖见下方p.289记录。

## 第十章印刷页289正文与脚注摘段（2026-10-02）

p.289规范段`chp-10:10_CHP-10_intro:l229-238`对照`CHP-10.pdf`物理第18页迁移正文。p.288 L227开启的“All four Venetian artists were beginning their careers”于p.289 L230闭合；更新`st-chp10-p288-venetian-careers-open`，保留原始前页引句并追加本页续句，确认Haskell说四位威尼斯画家当时刚开始职业生涯、Canaletto尚几乎无人知晓，p.288 coverage转complete。

本页正文新增15条提及、8条statement及2个候选：`cand-9016`为McSwiny系列中未具题名的Devonshire纪念画，另分别记录Marco Ricci与Sebastiano Ricci的合作关系候选、作品所纪念的公爵及注1待迁移；`cand-9017`为Haskell所用的晚十八世纪capricci绘画类型，明确与`cand-7746`的特定“Capriccio pittoresco”术语区分。复用索引情境候选`cand-2151`（Marco Ricci）、`cand-2171`（Sebastiano Ricci）、`cand-0918`（Duke of Devonshire）、`cand-2193`（Duke of Richmond）、McSwiny系列`cand-9007`和British Worthies群体`cand-9013`；未在S2解决标题人物或跨章身份。更新`cand-9007`与`cand-9009`的细节，写入恢复副本后再应用。

语义处理保留不同话语层：Haskell对Ricci兄弟“已成名”及“必需高价”的推断，不补金额或验证其“commoner”用语；“scheme began well”、1722年前已启动15幅及“大部分后来由Richmond公爵收购”均作为Haskell叙述，注2所述作品清单混乱仍待合并注释段核读。另记录Haskell称方案困难与McSwiny构想几乎不可分、虽有吸引力却完全未达到保存British Worthies记忆的声明目的；`capricci`及废墟/华服观者所引发的忧郁与picturesque比较属于作者艺术史判断。该句在p.290 L241以“Memento Mori”闭合，跨段引用已登记；本轮只核对这句续文，p.290其余内容未迁移。

页图校读仅记S2、不改S0：L230 OCR `wellestablished`校为印本`well-established`。p.289 L233–238是页下注1–2的摘段；完整注1艺术家/作品/收藏地点表及注2关于Constable、1741年清单、Vertue访问记录和Richmond收藏范围均位于合并注释源段L543–544，当前不重复登记，等待该源段按序迁移。故p.289正文已审但coverage保持partial；下一规范段为p.290 `chp-10:10_CHP-10_intro:l240-251`。

受控脚本`chp10_p289_migration.py`默认dry-run，固定来源资产SHA-256和源段SHA-256，检查候选序号、相邻三段coverage、候选依赖、15条提及精确跨度、statement源引文及跨页续文；应用前四表保存`.bak-s2-chp10-p289-20261002`。应用后全账本824段：423 reviewed/complete、62 excluded、338 queued、1 reviewed/partial；候选9,004、提及18,118、statement 8,229。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，保留两条既存`enrichment.source_ref`警告及S2未收口/1段partial警告；`tests/test_audit_tables.py`通过9项；`git diff --check`退出码0（保留仓库既有LF/CRLF提示）。

## 最近处理更新：第十章印刷页290–291（2026-10-02）

p.290（PDF物理第19页）正文新增14个候选（cand-9018–cand-9031）、45条精确提及和24条statement；闭合p.289 L232的跨页句，登记客户信、McSwiny作品版本、Goodwood陈列、图像说明、购藏及版画订阅计划。Brutus和Roman Admiral保留为未定类型图像角色。

p.291（PDF物理第20页）正文新增7个候选（cand-9032–cand-9038）、31条提及和12条statement。区分订阅计划与1741年实刊；记录18版、9座Richmond收藏墓葬、人物Characters、铭牌设计/镌刻及关于McSwiny、Smith、Carriera和Canaletto的文字。p.291末句续至p.292 L268，仍为partial。书信正文所称1727年与注3引出的1730年致John Conduitt信日期冲突；L551–553现已迁移并链接正文，但日期矛盾仍保留，且与p.290注4同日信件候选的身份待S3判断。页图确认`Carriera`和`siècle`，校读仅记S2。

跨页审查时将p.289 Duke of Richmond提及及断言从宽泛索引候选cand-2193改为页码289–291且子目为“and McSwiny's British Worthies”的cand-2194。当前824段：424 reviewed/complete、62 excluded、336 queued、2 reviewed/partial；候选9,025、提及18,194、statement 8,265。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；两条既存`enrichment.source_ref`警告仍在；`tests/test_audit_tables.py`退出码0，`git diff --check`退出码0（只有仓库既有LF/CRLF提示）。下一段为p.292 `chp-10:10_CHP-10_intro:l268-277`。

## 第十章印刷页291注1–3（2026-10-02）

对照PDF物理第20页，迁移L551–553并解除p.291正文3个脚注marker的pending。新增7个候选、17条提及和5条statement。注1区分Newton纪念碑、其铭牌及单独页面上的Newton medallion设计，记录Perrot的铭牌设计归属与Boucher的图像绘制说法；候选之间未合并。注2登记Malamani 1899 p.142、1753年致Carriera书信和McSwiny似未结账目的报告，保留发信人/账目性质未知及“apparently”限定。注3记录McSwiny致Conduitt、1730年9月27日信及印本交叉引用；正文1727年日期、p.290注4同日期候选与此处书信身份均留待后续比较。OCR校读仅记S2：`Garriera`→`Carriera`、`tom`→`from`、`Conduits`→`Conduitt`。应用后审计`s2_missing=[]`、`errors=[]`；当前全账本825段（433 complete、62 excluded、316 queued、14 partial），候选9,422、提及19,493、statement 8,701。下一注释位置L554。

## 第十章印刷页292注1–6（2026-10-02）

对照`CHP-10.pdf`物理第21页，迁移合并注释源段L554–557，并将脚注1–6链接到正文7条statement。新增10个候选（cand-9436–cand-9445）、15条精确提及和6条原书statement。注1–5分别为Canaletto市场、Burney、Beckford、Finberg及Zuccarelli履历的书内引证；注6以1935年展览图录和Bjurström 1967支持Tessin生涯/收藏叙述。所引页码/研究未独立查阅，内部书目匹配仍待书目S2核对。印本校读只记S2、不改S0：L556脚注号印作5（OCR为8）；L557年份印作1935（OCR为`193 5`），姓氏印作`Bjurström`（OCR为`Bjurstrôm`）。

受控脚本`chp10_p292_notes_migration.py`默认dry-run，锁定来源与L554–557哈希、候选序号、mention跨度、statement锚点/外键、正文marker状态和coverage前态；应用前为四表留恢复副本`.bak-s2-chp10-p292-notes-20261002`。应用后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全账本825段中433 complete、62 excluded、316 queued、14 partial；候选9,432、提及19,508、statement 8,707。两条既存S5 `source_ref`警告及S2未完成/partial提醒仍在。合并注释覆盖扩至L557，仍为partial；下一位置L558。

## 第十章印刷页293注1–4（2026-10-02）

对照`CHP-10.pdf`物理第22页，迁移p.293脚注2–4（合并注释L558–560），并补齐脚注1（页下注OCR摘录位于正文源段L290）。脚注1的Sirén引用原先已作为一个mention录在L290；本轮把作者与页码定位分开锚定并重用原候选，避免在合并注释段重复计数。新增7个候选（cand-9446–cand-9452）、29条提及和6条statement，链接正文marker 1–4的5条断言。注2登记Tessin致A. M. Zanetti、1737-03-12信及Biblioteca Marciana索书号；注3登记Francesco Algarotti致Bonomo、1749-09-05信及Treviso馆藏号；注4记录Pellegrini与Carriera行程、Ricci《酒神与阿里阿德涅》相对年代，以及Johann Philip Franz 1723年致Friedrich Karl Schönborn信的引述。相关档案/引文页面未独立查阅；作品、作者与引证身份仍按S2候选保留，不作S3合并。

印本校读只记S2、不改S0：L290 `Siren`→`Sirén`；L558–559 `Bibiioteca`→`Biblioteca`；L560 `Camera`→`Carriera`、`piZt A`→`p. 151`、`Diisseldorf`→`Düsseldorf`。受控脚本`chp10_p293_notes_migration.py`默认dry-run，固定来源资产/注释行哈希、候选序号、锚点、外键、marker状态和coverage前态；写入前保存四表恢复副本`.bak-s2-chp10-p293-notes-20261002`。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全账本825段中433 complete、62 excluded、316 queued、14 partial；候选9,439、提及19,537、statement 8,713。`tests/test_audit_tables.py`通过11项；两条既存S5 `source_ref`警告及全书S2未完成/partial提醒仍在。合并注释覆盖至L560；L561开始p.294注1，下一位置L561。

## 第十章印刷页300注1–7（2026-10-02）
处理合并注释L582–588并链接正文marker；注4续文L379、注7馆藏号续文L380并入原注。新增11个候选（cand-9495–cand-9505）、33条提及和11条statement。
## 第十章印刷页301注1–7（2026-10-02）
处理L589–594；新增13个候选（cand-9506–cand-9518）、41条提及和10条statement。页图确认注5印本为5、OCR L592误作6；Poleni—Smith书信和绘图请求保留为待审候选。可能书目匹配及引文未核读。
## 第十章印刷页302正文与注1–5（2026-10-02）
正文L391–399新增10个候选（cand-9186–cand-9195）、50条提及和16条statement；“Lady”按语境处理为Mary Wortley Montagu。末句续至p.303，coverage仍partial；L400注释摘句与L600去重。注释L595–599新增5个候选（cand-9519–cand-9523）、21条提及和7条statement，五个marker均已链接。
页图校读记录L595的“I am”（OCR作“1 am”）及L599印本注5（OCR作6）。L598漏转的意大利文引文另存为派生视觉转录，原OCR未改。更新后审计errors为空、s2_missing为空；定向测试9项通过。下一位置p.303注1（L600）。
## 第十章印刷页303正文与注1–6（2026-10-02）

正文L403–409与合并注释L600–604已迁移，新增10个候选、30条精确提及和8条原书statement，并链接正文marker 1–6。注5续文与注6均在规范OCR正文分节L409，不另造视觉转录。扫描校读记录L600 `D.D.P.`→`D.D.D.`及L409四处意大利文差异；源OCR不改。注3的账目只支持一条《四季》拟寄伦敦给Smith的1726-05-21记录，不含金额，不能单独证明付款或寄达。注5无日期信件留下两幅Winter先比较、再决定寄哪幅的未决语义，与正文“已寄出”叙述保持张力，朋友身份未知。候选、提及、statement和coverage经受控脚本dry-run后应用；修正两条指向错误段落的候选source_ref后，审计`s2_missing=[]`、`errors=[]`，定向测试退出码0。当前账本：826段中438 complete、62 excluded、316 queued、10 partial；9,520候选、19,762提及、8,784 statements。下一位置为p.305注1（L611）。
## 第十章印刷页304注1–7（2026-10-02）

合并注释L605–610新增11个候选（cand-9534–cand-9544）、31条精确提及和7条statement；p.304正文7个脚注marker均已解除pending。注1列三条威尼斯档案定位但未逐项对应租赁/购置；注2与5复用Chaloner刊物候选；注3引用Parker p.9起；注4的六月1730年引语与其内引“p.290 note 1”所指1729年信件之间保留未解差异；注6为Sirén p.107；注7为Christie's 1776-05-16拍卖目录和未具名14幅作品。印本校读记录L605 `f.84v`、`c.135v`、`c.306v`，L609 `Sirén`及L610 `Joseph`，不改S0。S2审计`s2_missing=[]`、`errors=[]`，定向测试退出码0。账本计数为9,531候选、19,793提及、8,791 statements；下一位置p.305注1（L611）。

## 第十章印刷页305注1与p.306注1校接（2026-10-02）

p.305脚注1只有`Constable, 1976.`；页图确认该标记只跟在Smith最早六幅Canaletto作品的叙述后。“get to know it”后的OCR撇号不是脚注标记，原先挂在Visentini出版与Tessin后续报告断言上的marker 2已移除。Constable身份、文献题名和被引页码均不推断。复核p.306整页确认注1标记跟在“Visentini”之后；Blunt与Croft-Murray第67页起的引文因OCR重排出现在L441，现链接到Smith保留Visentini原稿的断言。此前误连的Breval雕像marker已移除。新增1个候选、5条提及、2条citation statement；p.305正文和p.306正文仍因跨页/后续脚注保持partial。

当前全账本826段：438 complete、62 excluded、316 queued、10 partial；候选9,532、提及19,798、statement 8,793。`audit_tables.py --summary`的`s2_missing=[]`、`errors=[]`；`python -m pytest tests/test_audit_tables.py -q`通过11项，`git diff --check`退出码0（仅Git LF/CRLF提示）。S2尚未收口，下一位置为p.306注2（L612）。

## 第十章印刷页308–310注释与跨页coverage收口（2026-10-02）

合并注释L621–634及p.308页级OCR续文L466迁移完成，新增11个候选、45条提及和17条原书statement；p.307 marker1及p.308–310共15个marker均已链接。页图确认p.309 L628/L629与p.310 L634的OCR脚注号6/8分别对应印本注5/6。p.310 marker4仅支持Smith旅行计划引语，辞去领事职务statement上的误挂已移除。Vivian 1963 pp.157–162与本地书目pp.54–66不一致，引用保留未匹配；各页所引档案、书籍和信件未独立查阅。`chp10_p308_p310_notes_migration.py` dry-run/apply校验源文件和源段哈希、候选ID顺序、锚点、marker及外键，四表已保存恢复副本。

随后验证p.302–306的五组续句均已与下一页statement双向关联，将原partial覆盖改为complete：p.302 L399→p.303 L403、p.303 L408→p.304 L412、p.304 L421→p.305 L424、p.305 L433→p.306 L436、p.306 L441→p.307 L446。该处理后的阶段快照为826段：448 reviewed/complete、62 excluded、316 queued、0 partial；候选9,554、提及19,869、statement 8,820。`audit_tables.py --summary`无结构错误、`s2_missing=[]`；`tests/test_audit_tables.py`通过。余两条既存enrichment `source_ref`警告及316段queued提示。

## 第十章第二节文件标题与开篇段（2026-10-02）

文件标题`chp-10:10_CHP-10_sec_ii:l1-1`以行政章节元数据为由排除；L3–5副标题和开篇段新增4条提及、4条statement，无新候选。登记Schulenburg在威尼斯与Smith同期委托/收藏、Haskell对两人背景与审美的比较、“没有记录显示亲密往来”的限定，以及共享艺术家但收藏不同的说法；艺术家未具名，不建虚构关系端点。账本更新为826段：449 reviewed/complete、63 excluded、314 queued、0 partial；候选9,554、提及19,873、statement 8,824。`audit_tables.py --summary`结构错误为0，`s2_missing=[]`；`tests/test_audit_tables.py`通过。下一源段为`chp-10:10_CHP-10_sec_ii:l7-15`，全书S2尚未完成。


## 第十章图版55题注（2026-10-03）

规范段`chp-10:10_CHP-10_sec_ii:l58-60`对照PDF物理第44页完成；登记Canaletto与Marco Ricci两幅题注，共5条提及、2条statement，无新候选。

## 第十章图版56题注（2026-10-03）

规范段`chp-10:10_CHP-10_sec_ii:l62-70`对照PDF物理第45页完成；印本题注“Marieschi: Picture Exhibition at Church of S. Rocco”，新增6条提及、1条关系候选statement，无新候选。

## 第十章印刷页313正文（2026-10-03）

规范段`chp-10:10_CHP-10_sec_ii:l72-81`已阅读并迁移5个候选、74条提及、19条statement。L73闭合p.312正文句，L81续至p.314 L84；脚注1–4等待规范注释L284–287，故本段partial。经扫描复核撤销`melodramas`误标的OCR校正；剩余p.311、p.312与p.313三个partial段均待后续正文或注释收口。当前账本826段：453 reviewed/complete、63 excluded、307 queued、3 reviewed/partial；9,582候选、20,095提及、8,892 statements。下一段`chp-10:10_CHP-10_sec_ii:l83-93`。

## 第十章印刷页314正文（2026-10-03）

规范段`chp-10:10_CHP-10_sec_ii:l83-93`新增30个候选、79条提及和24条statement。L84闭合p.313延续句；保留两条牧歌画身份/地点映射未决、未具名收藏类型待决、Haskell的解释性限定。脚注1–4等待规范注释L288–291。L93送画至庄园的句子续至p.315 L95，因此本段partial；下一段为`chp-10:10_CHP-10_sec_ii:l95-106`。

## 第十章印刷页315正文（2026-10-03）

规范段`chp-10:10_CHP-10_sec_ii:l95-106`已迁移22个候选、59条提及和35条statement。L96的Germany闭合p.314送画目的地；p.315仍因脚注1–2待L292–293、L106句末续至p.316 L109而partial。修正Plate 53b坐像者/作者/肖像作品错映射；候选收藏和未具名群体保留类型待决。应用后826段为453 complete、63 excluded、305 queued、5 partial；表审计无结构错误、`s2_missing=[]`，定向审计测试通过。下一段`chp-10:10_CHP-10_sec_ii:l108-117`。

## 第十章印刷页316正文（2026-10-03）

规范段`chp-10:10_CHP-10_sec_ii:l108-117`新增37个候选、77条提及和33条statement。分别登记Canaletto景色、Streit生活场景组、节庆event、毁佚作品、肖像和收藏比较；相同题名/主题不强合并，Doge、未名团体及作品归属不从语境推断。p.315句在L109闭合；脚注1–4待L294–297，故p.316仍partial。应用后全账本为453 complete、63 excluded、304 queued、6 partial；9,671候选、20,310提及、8,984 statements。下一段`chp-10:10_CHP-10_sec_ii:l119-131`。

## 第十章印刷页317正文（2026-10-03）

规范段`chp-10:10_CHP-10_sec_ii:l119-131`新增20个候选、57条提及和20条statement。印本页眉实际标“Chapter 12, THE ENLIGHTENMENT”；项目继续按来源文件`10_CHP-10_sec_ii`登记。记录威尼斯的启蒙语境、欧洲知识交流、赞助变化、Arcadia及Galileo相关叙述，保持Haskell原有语气和未具名对象边界。L131末句续至p.318；脚注1–2等待L298–299，coverage为partial。OCR/印本校读只记S2，不改S0。应用后全账本为453 complete、63 excluded、303 queued、7 partial；9,691候选、20,367提及、9,004 statements。下一段`chp-10:10_CHP-10_sec_ii:l133-142`。

## 第十章印刷页318正文（2026-10-03）

规范段`chp-10:10_CHP-10_sec_ii:l133-142`新增17个候选、67条提及和21条statement。L134闭合p.317跨页句；移入Voltaire转述、意大利思想家及作品、威尼斯语境和Conti经历，并区分城市/政治实体、人物/著作以及Haskell评价/来源事实。p.318末尾Conti–Newton关系句已由p.319 L145续完；脚注1–4待L300–303，故coverage为partial。表审计曾发现跨页statement锚点越出p.318 segment，现已把引文锚定到本段L134，并用前页segment和continuation prefix保留连接。修复后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；定向测试通过10项。全账本826段：453 complete、63 excluded、302 queued、8 partial；9,708候选、20,434提及、9,025 statements。下一段`chp-10:10_CHP-10_sec_ii:l144-149`。

## 第十章印刷页319正文（2026-10-03）

规范段`chp-10:10_CHP-10_sec_ii:l144-149`新增11个候选、38条提及和21条statement。L145的“of them”补完p.318 Conti–Newton关系句；“建议Conti当选”保留为建议，未登记为已当选。区分Newton的未名机密笔记、Conti的未名作品、Shakespeare《Julius Caesar》与罗马人物；保留印本文字“Sasper”，记录OCR `Ke`与印本`he`的差异而不修改S0。Conti绘画幻想论述保留Haskell的推断和“写作时间未知”限定。脚注1–4等待规范注释L304–307，末尾引文于p.320闭合，故p.319仍为partial。应用后全账本为453 complete、63 excluded、301 queued、9 partial；9,719候选、20,472提及、9,046 statements。下一段`chp-10:10_CHP-10_sec_ii:l151-163`。

## 第十章印刷页320正文（2026-10-03）

规范段`chp-10:10_CHP-10_sec_ii:l151-163`新增10个候选、51条提及和32条statement；p.319引文在L152闭合。登记Conti、Algarotti、Zanetti、Bettinelli与Lodoli相关叙述，保留Haskell的限定/归因，并区分行程、教学、作品及社交关系。印本校读`Dell'entusiasmo`及L310脚注号3；S0不改。候选类型首次审计发现`concept`不在注册表，从预应用恢复副本还原四表后改为`term`并重新应用。脚注L308–310与L163→p.321续句待收口，故本段partial。当前全账本453 complete、63 excluded、300 queued、10 partial；9,729候选、20,523提及、9,078 statements。审计`s2_missing=[]`、`errors=[]`；定向测试通过。下一段`chp-10:10_CHP-10_sec_ii:l165-173`。

## 第十章印刷页321正文（2026-10-03）

规范段`chp-10:10_CHP-10_sec_ii:l165-173`新增16个候选、41条提及和27条statement；L166闭合p.320关于Lodoli直言不讳的句子。记录Lodoli有关贵族奢侈与工匠生计的引语、经同时代人转述的功能建筑观、对晚期巴洛克及新古典主义的拒绝、古代建筑/Pantheon评议、修会建筑改动、对Massari模型的逻辑批评、Gozzi与Algarotti相关叙述。分别保存Haskell陈述、转述引语和Massari在本地上下文中的发言归属；不把假设性建筑方案写成已发生的设计或委托。

页图校读只记于S2，不改S0：`linked.-`→`linked.—`、`Nothing'shocked`→`Nothing shocked`、`outside'S.`→`outside S.`、`tnodello`→`modello`、`logicalgrounds`→`logical grounds`、`five in houses`→`live in houses`。p.320的“but”句现由p.321 L166闭合；p.321脚注1–3待规范注释L311–313，L173未完句续至p.322 L176，故coverage为partial。受控脚本`chp10_p321_migration.py`默认dry-run，锁定来源及PDF/段哈希、表计数、候选ID、提及跨度、statement引句/外键和p.320续句状态；应用前四表恢复副本后缀`.bak-s2-chp10-p321-20261003`。应用后审计`s2_missing=[]`、`errors=[]`，定向审计测试通过。当前826段：453 complete、63 excluded、299 queued、11 partial；9,745候选、20,564提及、9,105 statements。下一段`chp-10:10_CHP-10_sec_ii:l175-178`。

## 第十章印刷页331正文（2026-10-03）

规范段`chp-10:10_CHP-10_sec_ii:l269-271`已完成，新增8个候选（`cand-9868`–`cand-9875`）、24条提及和12条statement。复用已有图版作品候选`cand-4056`记录正文Plate 56指针。p.330关于Piazza S. Marco的展览地点在L270续完；Church of S. Geminiano仅作为相邻地标处理。区分Scuola di S. Rocco的年度展示与1777年启动、至1787年停办的学院官方展览安排；游行与展览的起源关系保留“probably”，学院展览的确切末年不推定。L270段末多出的OCR撇号只记入S2校读，不改S0。p.330与p.331现为complete；合并注释段L274–324仍未迁移，故p.311–323的13个正文段和注释段仍为partial。当前账本826段：461 complete、107 excluded、244 queued、14 partial；9,862候选、20,953提及、9,315 statements。下一步先迁移合并注释L274–324，随后处理第13章起的queued段。

## 第十章印刷页313–314注释（2026-10-03）

p.313注释L284–287及p.314注释L288–291已对照PDF物理页46–47完成，8个正文脚注标记全部回链，p.313和p.314正文coverage由partial改为complete。新增14个候选（cand-9891–cand-9904）、33条mention和18条statement；复核并重映射p.313三条作品mention，单独登记p.314注4六位画家的数量。恢复副本为四表.bak-s2-chp10-p313-314-notes-20261003。初次审计发现两条六幅计数的claim自然键重复，使用受控修复脚本为每条计数补充画家姓名，statement恢复副本后缀.bak-s2-chp10-p313-314-unique-count-claims-20261003。修复后audit_tables.py --summary为s2_missing=[]、errors=[]；全账本826段：465 reviewed/complete、107 excluded、244 queued、10 reviewed/partial；9,891候选、21,011提及、9,344 statements。两条既存enrichment source_ref警告仍保留，S2未达到S3交接条件。下一待处理注释为p.315 L292–293。

## 第十章印刷页315注释（2026-10-03）

p.315注释L292–293已对照PDF物理页48迁移，脚注1、2分别回链至Schulenburg与Carriera关系statement，以及Streit比较statement；p.315正文coverage由partial改为complete。新增6个候选、11条mentions、4条statements。印本把年轻女画家名字视觉读作Griè，OCR的GriS保留在来源转录并记录校正，人物身份未决；信件定位与Rohrlach、Denina书目仅按Haskell转引登记，未独立查阅。恢复副本为四表.bak-s2-chp10-p315-notes-20261003。全表审计s2_missing=[]、errors=[]；826段：466 reviewed/complete、107 excluded、244 queued、9 reviewed/partial；9,897候选、21,022提及、9,348 statements。两条既存enrichment source_ref警告保留，S2仍未满足S3交接条件。下一待处理注释为p.316 L294–297。
## 第十章印刷页316注释（2026-10-03）

p.316脚注L294–297已对照印本完成并回链，正文coverage转complete。新增8个候选、24条mentions和7条statements。记录Zimmermann所刊Streit笔记、W. G. Constable对Canaletto作品的讨论与Moretti归属否定、Zimmermann报告的《Sala del Maggior Consiglio》归属、Amigoni访英/居威尼斯/赴西班牙的时序及Streit肖像日期，以及Hugh Honour出示照片的致谢。引用页未独立查阅；身份、归属及“these paintings”指代未决。当前826段：467 reviewed/complete、107 excluded、244 queued、8 partial；9,905候选、21,046 mentions、9,355 statements。审计无errors且`s2_missing=[]`；定向测试13项通过。下一范围为注释L298–324（p.317–323），随后完成S2交接审计。
## 第十章印刷页317注释（2026-10-03）

p.317注释L298–299已按印本完成并回链；Hazard保留为“Hazard, 1935”，Maugain保留姓氏定位，未补写书目或外部身份。新增4个候选、2条mentions和2条citation statements，正文coverage转complete。当前826段：468 reviewed/complete、107 excluded、244 queued、7 partial；9,909候选、21,048 mentions、9,357 statements。审计无errors且`s2_missing=[]`；定向测试13项通过。下一范围为L300–324（p.318–323注释）。
## 第十章印刷页318注释（2026-10-03）

p.318脚注L300–303已核印迁移并回链，正文coverage转complete。新增12个候选、14条mentions和6条citation statements。保留Natali、Pierantoni、Brol、Robertson、Moncallero的简写引文；“his Prose e Poesie”暂指Conti、待与书目核对。引文未独立查阅。当前826段：469 reviewed/complete、107 excluded、244 queued、6 partial；9,921候选、21,062 mentions、9,363 statements。审计无errors且`s2_missing=[]`；定向测试13项通过。下一范围为L304–324（p.319–323注释）。

## 第十章印刷页319注释（2026-10-03）

对照`CHP-10.pdf`物理页52核读L304–307四条注释，新增候选`cand-9935`–`cand-9946`、26条精确提及和9条statement。注1保留Manuel姓氏及页码定位；注2将Conti的长篇意大利语引文作为其转述记录，区分Leonardo手稿、未具名米兰图书馆、Newtonian色彩理论、未具名德国画家及其印刷画作、Antonio Zanetti、The Hague与Apelles，不推定画家、手稿或机构身份。保留“he assured me”的转述层级及“Se ciò è vero”“forse”的条件/推测语气。注3记录Conti关于camera ottica、Canaletto转移透视点及视觉效果的说法；注4将Conti卷II第278页回链至p.319正文绘画幻想引文。被引原著未独立查阅。

页图校读只记S2，不改S0：L305 `bell’ani`→`bell’arti`、`ne , conserva`→`ne conserva`；L306 `tutti fi trasferisca`→`tutti li trasferisca`。脚本默认dry-run，锁定规范Markdown/PDF哈希、表前态、注释边界、提及跨度、statement外键和四处正文脚注标记；应用前为四表创建`.bak-s2-chp10-p319-notes-20261003`恢复副本。四个p.319脚注标记已双向回链，正文coverage转complete；合并注释覆盖扩至L274–307及既有L325–349，L308–324仍待处理。当前826段：470 complete、107 excluded、244 queued、5 partial；9,933候选、21,088提及、9,372 statements。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；两条既存enrichment `source_ref`及244 queued、5 partial提示保留。`tests/test_audit_tables.py`与`tests/test_build_source_segments.py`共13项通过。下一范围为p.320–323脚注L308–324，并收口4个正文partial。

## 第十章印刷页320–323注释及尾段收口（2026-10-03）

对照`CHP-10.pdf`物理页53–56迁移规范注释L308–324，新增30个候选（`cand-9947`–`cand-9976`）、57条精确提及和19条statement；四页正文脚注全部回链，p.320–323正文与合并注释段L274–349均转complete。脚注引文只按Haskell书内指引登记，未声称独立查阅被引原作。

p.320注1–3分别定位Lorenzetti、Memmo《Elementi dell’architettura lodoliana》、Petrocchi、Vico《Autobiography》与Calogerà《Raccolta》及Fisch/Bergin引文；标题从p.320注2回补既有Memmo 1786候选`cand-8812`并解开p.309的标题待决。p.321注1–3连接Ortes致Algarotti书信与Temanza、Moschini、Gozzi《Dialogo》；p.322注1–4记录Kauffmann、Correr手稿、Previtali和Longhi肖像来源。注4称Portrait of Lodoli在Accademia，而List of Plates的Plate 48c标注Museo Correr；两条来源判断和对象候选均保留，未合并或裁决。p.323注1–7分别回链Goldoni引文、Dazzi、Gennari致Patriarchi书信、Paoletti、Visconti致Ligari书信和Gazzetta Veneta期号。注5的后半句由规范S0 L192承载，已与L322双向链接；未将匿名历史学家与Paoletti作身份合并。

页图校读仅记入S2，不改S0：L310注号OCR 8→印本3；L312 `G. AMoschini, 1815,1`→`G. A. Moschini, 1815, I`；L315 `Cotter`→`Correr`；L317 `Tlie`→`The`、`Longbi`→`Longhi`；L322 OCR注号6→印本5；L323 `horn`→`from`；L324 `No. 35`→印本`No. 55`。p.323高分辨率页图确认注5续句“who calls the artist ‘Antonio’ Longhi, does not seem wholly reliable.”位于同页脚注区，S0将其分置L192。迁移脚本dry-run校验所有提及跨度、候选外键、脚注前态及候选编号后应用；四表恢复副本后缀`.bak-s2-chp10-p320-323-notes-20261003`。

应用后全账本826段：475 complete、107 excluded、244 queued、0 partial；9,963候选、21,145提及、9,391 statements。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；保留两条既存enrichment `source_ref`警告和244 queued提示。`tests/test_audit_tables.py`与`tests/test_build_source_segments.py`共13项通过。下一源序位置为`chp-13:13_CHP-13_intro:l1-1`；全书S2仍未完成。

## 第十三章印刷页332正文（2026-10-03）

排除生成的Markdown文件名标题段`chp-13:13_CHP-13_intro:l1-1`，并对照`CHP-13.pdf`物理页1完成`l3-12`正文的S2迁移。新增来源派生候选`cand-9977`（Marieschi 1741年未题名组作）与`cand-9978`（二十年版权垄断机制）；新增35条提及和20条statement。脚注marker 1–5待处理书末注释段L179–251后回链，故p.332正文段仍为partial。S2页图校读记录首字母T跨行、标点/空格误差及`II`→`Il`；OCR原件不改。审计`s2_missing=[]`、`errors=[]`。全账本826段：475 complete、108 excluded、242 queued、1 partial；9,965候选、21,180提及、9,411 statements。下一源序段为p.333 `chp-13:13_CHP-13_intro:l14-19`。

## 第十三章印刷页333正文（2026-10-03）

按源序处理`chp-13:13_CHP-13_intro:l14-19`，对照`CHP-13.pdf`物理页2，新增7个候选、23条提及和17条statement。记录插图书的四种图像生产路径、出版商设施/雇用/委托与赞助、贵族仪式诗歌类出版物，以及Caterina Barbarigo于1765年经代理人传达的印制规格；不把一般模式外推为单项委托，不擅定家徽或Zorzi支系。正文Gaspara与索引Gasparo的姓名冲突保留分立候选；“Bundles of them”引文说话者未定并续至p.334，脚注1待L179–251。p.333 coverage为partial。

## 第十三章印刷页334正文（2026-10-03）

处理`chp-13:13_CHP-13_intro:l21-30`，对照物理页3，新增4个候选（cand-9986–cand-9989）、26条提及和18条statement。p.333引文在本页闭合，印本注1指向Saverio Bettinelli《Lettere inglesi》第二信；记录三位出版商及Albrizzi的出版、编辑、社群和教会联系、Bossuet版本及Piazzetta合作。身份和归属不明处保持未决；页注1–6待L179–251回链，故p.334为partial。

## 第十三章印刷页335正文（2026-10-03）

处理`chp-13:13_CHP-13_intro:l32-39`，对照物理页4，新增7个候选（cand-9990–cand-9996）、37条提及和21条statement；闭合p.334引文并据印本注1将说话者识别为《Novelle》1730年3月19日广告，广告提及的是拟议中的圣奥古斯丁作品版。新增关系候选仍留在原书statement，不直接建立正式边。页图校读修正 Schönbrunn、Carriera、图稿脚注3和Richard卷号；S0原件不改。p.335末句续至p.336 L41–50，印本注1–3待L192–194迁移回链，coverage保持partial。全账本826段：475 complete、108 excluded、239 queued、4 partial；9,983候选、21,266提及、9,467 statements。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，定向测试13项通过；下一段为p.336 `chp-13:13_CHP-13_intro:l41-50`。

## 第十三章印刷页336正文（2026-10-03）

处理`chp-13:13_CHP-13_intro:l41-50`，对照`CHP-13.pdf`物理页5，新增13个候选（cand-9997–cand-10009）、48条精确提及和36条原书statement。闭合p.335末句：Gerbault邀请订阅同样豪华的《Orlando Furioso》版，但计划未实现。记录Piazzetta的法式技艺、Platnerus外科教材扉页、Guardi兄弟对《Gerusalemme Liberata》图稿的挪用、Albrizzi为Piazzetta保存生平记忆、其印书铺和Robert Adam委托、收藏与赞助活动及Pasquali社交圈。Albrizzi在p.334记为1699年生、此处称1777年卒年85岁，保留书内冲突并互链原断言，不擅改年代。页图校读仅存S2：`Use`→`life`、`die`→`the`、`povertystricken`→`poverty-stricken`、`successful Use`→`successful life`；S0不改。

本页Gherardi–Muratori引文续至p.337；页注1–8需在合并注释L195–202按源序处理。cand-10008主锚点为已审阅正文L50，注8与信件身份的完整回链待L202。受控脚本`chp13_p336_migration.py`默认dry-run，校验源/PDF、表前态、候选编号、mention跨度、statement引句/外键和跨页状态；应用前保存恢复副本`.bak-s2-chp13-p336-20261003`。首次应用后审计发现cand-10008直接锚到未审阅的L202，已修正至BODY#L50并留候选表恢复副本`.bak-s2-chp13-p336-candidate-ref-fix-20261003`；L202仍留待脚注段处理。最终`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，保留两条既存enrichment `source_ref`警告；定向13项测试通过。当前826段：475 complete、108 excluded、238 queued、5 partial；候选9,996、提及21,314、statement 9,503。下一源序段为p.337 `chp-13:13_CHP-13_intro:l52-59`。

## 第十三章印刷页337正文（2026-10-03）

处理`chp-13:13_CHP-13_intro:l52-59`，对照`CHP-13.pdf`物理页6，新增3个描述性候选（cand-10010–cand-10012）、44条精确提及和30条statement。闭合p.336开头Gherardi–Muratori引文；记录Pasquali对Lodoli的敬仰、审查制度及1764年秘密发行Beccaria禁书的叙述、Joseph Smith对出版商号的控制、Dactylografa Smithiana版画集、Caime委托并资助的Piazzetta宗教书、Pasquali与Goldoni合作的17卷本及Goldoni对纸张、印刷和插图的意见。未具名英语文法书、Medusa扉页及Albrizzi的Zanetti宝石出版物保留描述性边界；相关候选不与相近索引对象预先合并。p.337注1–6待合并注释L203–208；Goldoni引文在本页闭合。页图校读仅记S2。受控脚本`chp13_p337_migration.py`默认dry-run，核对源/PDF哈希、前态、候选ID、精确提及跨度、statement原句/外键和跨页状态；dry-run +3/+44/+30后应用，恢复副本后缀`.bak-s2-chp13-p337-20261003`。全账本826段：475 complete、108 excluded、237 queued、6 partial；候选9,999、提及21,358、statement 9,533。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；两条既存enrichment `source_ref`警告保留。定向测试13项通过。下一段为p.338 `chp-13:13_CHP-13_intro:l61-68`。


## 第十三章印刷页338正文（2026-10-03）

按源序核读`chp-13:13_CHP-13_intro:l61-68`，对照`CHP-13.pdf`物理页7。记录Goldoni对常规扉页程式的批评，以及他建议每卷用一幕生活场景替代Muses、Apollos、面具、Satyrs或猿猴等陈套装饰；结合其自传记述的卷二场景和Plate 57b例证，说明Novelli插图呈现日常亲密关系及社会生活。Haskell将这些图像解释为十八世纪中叶威尼斯富裕专业阶层生活，与Longhi作品比较，并评价其精致程度、Albrizzi式华丽装帧的缺席及“启蒙资产阶级”的趣味；这些作为Haskell的解释与比较保留，不转换为客观阶层统计。Plate 57b复用已登记候选`cand-4079`。

随后记录Pasquali通过Nollet译著及插图传播实验科学、向Carlo Lodoli献呈Vignola版并支持Visentini对巴洛克建筑的批评；作者对这些出版活动的评价按其论述层级记录。Antonio Zatta部分区分其支持耶稣会、因此与反对耶稣会的当局冲突、曾提议出版攻击其敌手之书，以及作者对其个人社会活动和出版目录的描述。Zatta提出出版的攻击性著作及Portuguese government句由p.339 L71闭合。印本校读仅记S2、不改S0：`général`→`general`、`Pasquah’s`→`Pasquali’s`、`pubheations`→`publications`、`suture`→`future`。

新增候选`cand-10013`–`cand-10023`共11项、48条提及、23条statement；包括社会群体和观念术语、Nollet译著/实验科学插图出版、Vignola版及相关出版论述。未将作者概括扩展成具体的外部身份事实或无据委托关系。脚注1–2对应合并注释L209–210尚未按源序迁移并回链；Zatta句续至p.339，故本段为`reviewed/partial`。受控脚本`chp13_p338_migration.py`默认dry-run，核验源文件/PDF哈希、表前态、提及跨度、statement锚点/外键及续页状态；dry-run显示+11候选/+48提及/+23 statement后应用，四表恢复副本后缀`.bak-s2-chp13-p338-20261003`。应用后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全账本826段为475 complete、108 excluded、236 queued、7 partial，候选10,010、提及21,406、statement 9,556。两条既存enrichment `source_ref`警告保留。下一源序段为p.339 `chp-13:13_CHP-13_intro:l70-77`，先闭合Zatta跨页句并继续按源序处理。


## 第十三章印刷页339正文（2026-10-03）

按源序核读`chp-13:13_CHP-13_intro:l70-77`，对照`CHP-13.pdf`物理页8，新增13个候选（cand-10024–cand-10036）、59条精确提及和23条原书statement。L71的“government”闭合p.338跨页短语“the Portuguese government”；p.338 statement已更新为closed，p.339注1仍待L211–212核读。

本页记录Zatta作为耶稣会第三等级成员的同时代说法，并保留Haskell关于其社会生活与个人记录较少的限定。其序言中的喷泉—海豚图像与所谓耶稣会寓意明确按讽刺性拟声记录；“Accademia dei Cacadubbj”仅作讽刺名称，不登记为真实机构。另记录目录所示出版规模、插图书出版范围、1756年Petrarch版、1757年Dante插图版、后续经典出版及Haskell对Dante图像的判断。Fontebasso、Zompini与Novelli分别关联到本页讨论的不同插图工作；Metastasio插图始于1781年，七年后Novelli为Goldoni全集制作第二组图稿，保留来源相对时间。关于Goldoni喜剧所置社会世界的比较作为Haskell评价处理，不转写为不带限定的社会史事实。

Pinelli段记录其为国家出版书籍、私人收藏与赞助活动、个人图书馆及数百幅绘画。其图书馆和绘画收藏因现有类型表没有专门的个人收藏类型而保持type undecided；“the State”暂按来源原词登记为待辨认的政治实体，不合并为威尼斯共和国。印本校读仅登记S2、不改S0：L72“social Use”→“social life”；L77“thepublisher”→“the publisher”，印本脚注标记“pictures.6”校正OCR“pictures.8”。

正文迁移时脚注1–6尚未按源序迁移；现已从L211–216按印本回链，本段coverage转为complete。受控脚本`chp13_p339_migration.py`默认dry-run，锁定源/PDF哈希、表前态、候选编号、mention跨度、statement引句与外键，并在一笔写回中关闭p.338句子、更新两页coverage及生成13候选/59提及/23 statement。应用后保存四表恢复副本后缀`.bak-s2-chp13-p339-20261003`。审计为`s2_missing=[]`、`errors=[]`；全账本826段中475 complete、108 excluded、235 queued、8 partial，候选10,023、提及21,465、statement 9,579。两条既存enrichment `source_ref`警告保留。下一源序段为p.340 `chp-13:13_CHP-13_intro:l79-88`；后续仍按页注位置处理L179–251。


## 第十三章p.340（2026-10-03）

按源序处理`chp-13:13_CHP-13_intro:l79-88`并核对`CHP-13.pdf`物理页9，新增22个候选、72条提及和41条statement。记录Pinelli的收藏与Maggiotto为其制作的肖像/寓意作品；Tiepolo保留为未定名姓氏，旧大师作品保留归属限定，Maggiotto总督肖像组不与既有肖像组候选合并。记录Remondini在Bassano及威尼斯的业务、其版画市场与受众变化、竞争环境和所聘版画家；区分不同公众与国际客户。另记录Wagner、Viero及Furnaletto的版画业务；Canaletto受托绘制公爵仪典图稿、计划由Brustolon制版，不推定版画已完成。页注1–6现已从L217–222迁入并回链；脚注3的L219与L88书目片段分段保留、双向链接，本段coverage转为complete。页图校读只记S2，不改S0。最终表审计无结构错误或漏列coverage；全账本826段中475 complete、108 excluded、234 queued、9 partial，候选10,045、提及21,537、statement 9,620。下一源序段为p.341 `chp-13:13_CHP-13_intro:l90-96`。


## 第十三章p.341（2026-10-03）

按源序处理`chp-13:13_CHP-13_intro:l90-96`并核对`CHP-13.pdf`物理页10，新增18个候选、89条提及和26条statement。记录Zanetti的绘画训练、版画/收藏身份及其鉴赏家与艺术家网络；保留Marco Ricci、Crozat、Carriera、Mariette、Tessin友情/通信候选及Pellegrini与Carriera的姻亲关系。保留1720年巴黎行程、1716年Crozat来威尼斯、1736年购自Prince Eugene继承人的作品组，以及出版/购画/版画委托的实际语气。画廊作品、Arundel的Parmigianino图稿、Poussin、Castiglione与Crespi作品均未补造题名；姓氏和“The Regent”按索引暂作候选，留待S3。L223–226脚注1–4已迁移并回链；Plate 58a已按物理页15图注映射到既有肖像作品`cand-4048`，临时指针候选`cand-10059`已排除；末句续至p.342 L99。正文段coverage现为complete。页图校读只记S2、不改S0：L91 `number.of men`→`number of men`、`ani`→`and`。


## 第十三章p.342（2026-10-03）

处理`chp-13:13_CHP-13_intro:l98-105`并核对`CHP-13.pdf`物理页11。新增14个候选、78条提及和26条statement；闭合p.341末句，分别记录Tessin借助Zanetti、门生训练、向Tiepolo传信、绘画与版画购买、Gai雕塑委托及Tessin藏有的Bathsheba。记录Zanetti藏有Brand/Dietrich作品、现代法英作品“无证据”的限定、旧作影响、Sebastiano历史画、Marco Ricci风景画、Carriera粉彩/微型画，以及奖章、宝石和版画收藏；1752年引语保留第一人称与未完成的例外列表。Tessin与Zanetti身份复用现有候选，Giovanni da Bologna名字及未具名瑞典国王留待S3；雕塑只记预定题材和配对意图。L102、L104校读更正只留在S2。页注1–7对应L227–234待源序处理，末段续至p.343 L108，故本页coverage为partial。

受控迁移脚本`chp13_p342_migration.py`默认dry-run，校验来源/PDF/段落SHA、表前态、候选号、78条最终mention跨度、statement引句/外键、页注和跨页状态；四表恢复副本后缀`.bak-s2-chp13-p342-20261003`。首轮结构审计发现两条`those countries`提及同跨度，精确移除重复锚点后结构检查通过；修复脚本`chp13_p342_overlap_repair.py`保存mentions恢复副本`.bak-s2-chp13-p342-overlap-fix-20261003`。全账本826段：475 complete、108 excluded、232 queued、11 partial；候选10,077、提及21,704、statement 9,672。最终审计`s2_missing=[]`、`errors=[]`；两条既存enrichment `source_ref`警告不变。下一源序段为p.343 `chp-13:13_CHP-13_intro:l107-114`。


## 第十三章p.343（2026-10-03）

处理`chp-13:13_CHP-13_intro:l107-114`并核对`CHP-13.pdf`物理页12，新增13个候选、59条提及和23条statement。闭合p.342引语第二项为Marc’Antonio雕刻、配Aretino十四行诗的Giulio Romano版画，并单独记录Zanetti称自己从未见过这些版画。保存1752年引语中关于单幅精印、多重复制、剩余复制品交换的偏好；区分Zanetti偏爱的Mannerist/“picturesque”作品、Faldoni刻制的作品、购自海外的Rembrandt与Callot版画，以及1759年自行雕刻的Castiglione图稿。年轻A. M. Zanetti区分艺术家/鉴赏家与公众的版画偏好，按引述层级记录。另记Zanetti恢复多色chiaroscuro木刻技法、约50张木刻与献赠，Haskell关于rococo/neo-classical并置的判断、Tiepolo蚀刻版画及《Delle Antiche Statue Greche e Romane》的出版时间。Marc’Antonio、Aretino及未具名Prince of Liechtenstein身份未决；页注1–4映射L235–238待迁移。p.343 L114起句续至p.344 L116，故本段仍partial。

受控脚本`chp13_p343_migration.py`默认dry-run，核验源/PDF/段落SHA、表前态、候选号、mention跨度、statement引句/外键及脚注链接；四表恢复副本后缀`.bak-s2-chp13-p343-20261003`。表审计指出跨页续文须保留在各自segment内，故`chp13_p343_quote_repair.py`恢复p.342 statement的source-local `original_quote`，另存恢复副本`.bak-s2-chp13-p343-quote-repair-20261003`；跨页主张仍由断言与链接承接。全账本826段：475 complete、108 excluded、231 queued、12 partial；候选10,090、提及21,763、statement 9,695。最终`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；两条既存enrichment `source_ref`警告不变。下一源序段为p.344 `chp-13:13_CHP-13_intro:l116-122`。


## 第十三章p.343正文（2026-10-03）

处理正文段chp-13:13_CHP-13_intro:l107-114并对照CHP-13.pdf物理页12，新增13个候选、59条提及和23条statement。闭合p.342开放引语，区分Annibale碟画与Giulio Romano版画；保留Zanetti关于版画偏好、交换、木刻、Tiepolo蚀刻版画的自述和Haskell评价。Marc’Antonio、Aretino及Prince of Liechtenstein身份未决。注1–4映射合并注释L235–238待源序处理；末句续至p.344。该页迁移后的表状态：475 complete、108 excluded、231 queued、12 partial；候选10,090、提及21,763、statement 9,695。

## 第十三章p.344正文（2026-10-03）

处理正文段`chp-13:13_CHP-13_intro:l116-122`并对照`CHP-13.pdf`物理页13。新增10个候选、33条提及；本批净增29条statement并修订p.343的《Delle Antiche Statue Greche e Romane》出版断言。登记`Dactyliotheca Ant. M. Zanetti`、Gori拉丁评论、意大利语译本、拟议献辞对象、Zanetti自述及Haskell解释、Zompini受雇/作品和Felicita Sartori版画活动；个人收藏类型待决。p.344注1–8现从L239–246迁移，新增4个候选、20条精确提及和10条statement，回链按印本标记核对。L122是注5续文，所引1843年`Memorie`复用p.276的完整题名候选。印本校读只记录于S2：`p. 43 8`→`p. 438`、`sec`→`see`、`Félicita`→`Felicita`。最初判断p.344信引语在图版后缺失；复核PDF页序发现p.345为物理页18，L162续完引语，故p.344 coverage现为complete，并与现有p.345续引statement互链。

经过受控迁移和个人收藏类型修订后，表状态为475 complete、108 excluded、230 queued、13 partial；候选10,100、提及21,796、statement 9,724。结构审计为s2_missing=[]、errors=[]；两条既存enrichment source_ref警告不变。

## 第十三章p.336页注（2026-10-03）

按印本迁移L195–202注1–8并回链正文断言，新增11个候选、32条提及、10条statement。页图校正记录保留在S2；同行误挂的注1/注6从Platnerus及1770年展览断言移除，p.336正文段由partial转complete。Albrizzi个人绘画/素描收藏cand-10007与版画收藏cand-10163均留类型待决；Morazzoni、Moschini、Gradenigo等短引文均仅作书内引用定位，未独立查阅。Gherardi–Muratori书信和引文保持“经Haskell转引”的证据层级。表审计s2_missing=[]、errors=[]；830段：489 complete、108 excluded、223 queued、10 partial；候选10,150、提及21,948、statement 9,810。下一源范围为合并注释L203–208（p.337注1–6）。

## 第十三章p.337页注（2026-10-03）

按印本迁移合并注释L203–208，新增13个候选、27条页注提及和9条原书statement；另为p.337正文L53的Prato补录1条提及，合计28条提及。脚注1保留Lodoli职位和影响、Conti致Vico的1728年书信书目信息及Haskell关于Pasquali听取Lodoli意见的推断；脚注2登记Pasquali致Mazzoni书信及经Nuti转引的意大利语引文；脚注3校正印本记录folio为32v；脚注4连接Novelle 1736年9月8日一期和未具名英文文法书；脚注5连接Morazzoni页116；脚注6连接Goldoni 1761年第一卷序言页v–vi。被引资料均未独立查阅。校正同一OCR行脚注4误挂至Smith控制出版商号断言；注号仅回链印本实际标记对应内容。写回后p.337正文转complete，合并注释段仍partial，待L209–246及L247–248镜像题注。审计`s2_missing=[]`、`errors=[]`；830段：490 complete、108 excluded、223 queued、9 partial；候选10,163、提及21,976、statement 9,819。下一个源序范围为p.338注1–2（L209–210）。

## 第十三章p.338页注（2026-10-03）

迁移合并注释L209–210，新增3个候选、9条提及和4条statement。注1以Goldoni 1762年《Delle Commedie》第二卷页1为前置场景扉页提议的书内出处；注2登记Zatta致未具名公爵的书信与《Lettera Giustificativa》，并将“强烈支持耶稣会”保留为Haskell对这些材料的判断。OCR卷号`H`按印本校作`II`；保留Haskell对“In Fiorenza”的括注修正为Venice。移除同页行内误挂的注1/Vignola献辞和注2/拟议攻击性出版物标记，页下注分别只链接印本指明的正文断言。上述引用材料未独立查阅。p.338正文coverage转complete；合并注释段仍partial，待L211–246及L247–248镜像题注。审计`s2_missing=[]`、`errors=[]`；830段：491 complete、108 excluded、223 queued、8 partial；候选10,166、提及21,985、statement 9,823。下一范围为p.339注1–6（L211–216）。

## 第十三章p.339页注（2026-10-03）

按源序对照`CHP-13.pdf`物理页8，迁移合并注释L211–216的注1–6，新增8个archive候选、17条精确提及和7条原书statement；另移除1条把“His own prefaces”错误映射到单一书籍候选的mention。注1记录威尼斯`Inquisitori di Stato`535、页173（1759-06-18）及536、页41v（1760-11-19）两处档案定位，并回链p.338跨页statement；档案本身未查阅。注2分别保留Giovanni de Cattaneo的“terziario, a quel che pare”说法、`Nouvelles Ecclésiastiques`的“Jésuite du Tiers Ordre”描述及其经Neri 1899页109、114转引的层级；没有消掉“as it seems”的限定。注3引用Zatta 1761年致未具名公爵书信页23，并显式回指p.338注2；该书目与`cand-10024`“vignette载体书”候选之间的重复身份留待S3对齐。注4登记Zatta 1790年书目；注5登记仅以`G. da Venezia, 1934, pp.25–34`给出的短引文；注6登记Pinelli 1785年售画目录及Moschini 1806卷II页64。被引材料均未独立查阅。

扫描校读仅记S2、不改S0：L211 `Archi vio`→`Archivio`、`4IV`→`41V`；L212 `17Ó0`→`1760`；L213 `quel die`→`quel che`；L215目录题名`c italiani`/`efigli`→`e italiani`/`e figli`，并核实注4与注5虽同在L215但指向不同引用；L215页码`p.25–34`按印本为`pp.25–34`；L216 `Sec also`→`See also`。页图确认注3指向讽刺性图像解读、注4只指目录所支持的“most prolific”句、注5只指Metastasio插图整句；移除此前误挂到一般前言评价、意大利经典/Dante句及后续Goldoni插图句上的同行脚注。`chp13_p339_notes_migration.py`先dry-run再apply，检查源/PDF和注释段SHA、表前态、外键、原文引句和精确mention跨度；四表备份后缀`.bak-s2-chp13-p339-notes-20261003`。应用后全账本492 complete、108 excluded、223 queued、7 partial，候选10,174、提及22,001、statement 9,830；结构审计`s2_missing=[]`、`errors=[]`，两条既存enrichment `source_ref`警告不变。下一源序为p.340注1–6（L217–222）。

## 第十三章p.340页注（2026-10-03）

按源序对照`CHP-13.pdf`物理页9，迁移合并注释L217–222注1–6，新增4个archive候选、17条精确提及和6条原书statement。注1 Morelli卷V页348回链Pinelli图书馆、绘画收藏解散及当时反响；注2复用Berengo 1957短引文候选并登记`Mostra dei Remondini`（1958）；注3记录Pietro Longhi致Remondini的七封书信（1748–1752）及A. Rava（1911），L219的“published by A.”与正文segment L88的“Rava, 1911.”分别保持source-local锚点，通过statement交叉引用闭合；注4 Moschini 1924页132只链接Wagner“似乎很少委托新作”的断言；注5复用Gallo 1948页153–214候选中的页184，并连同Moschini页132链接Viero句；注6复用同一Gallo候选的页158、186，链接Furnaletto委托Canaletto及Brustolon制版的计划。引用页均未独立查阅。

页图校读仅记S2、不改S0：L218 `Bercngo`→`Berengo`并去除行尾多余OCR引号。印本标记位置确认注4不覆盖Wagner的德国身份、开店年份或店铺对印刷业的重要性，误挂标记已移除。`chp13_p340_notes_migration.py`默认dry-run，核验来源/PDF哈希、前态、候选外键、mention跨度、statement原句、脚注目标及L219/L88分段；四表备份后缀`.bak-s2-chp13-p340-notes-20261003`。p.340正文coverage转complete。

## 第十三章p.341页注L223–226（2026-10-03）

对照`CHP-13.pdf`物理页10，按源序迁移p.341注1–4。注1保留G. Lorenzetti（1917）与F. Borroni简式参考，未给F. Borroni的题名/年份。注2登记Marco Ricci为Zanetti绘制六幅未题名作品、1723年称Zanetti为`mio amico oltre misura`，以及Zanetti协助Ricci取得包括Federico Correr在内其他 patron 的委托；复用Bottari卷II并记录页128–130和Lorenzetti 1917页138定位，所引材料未查阅。六幅画组与其他段落所述六幅风景画保持分立，留S3对齐。注3记录Mariette在其`Abecedario`中写有Zanetti评述，以及Zanetti遗嘱将一幅Rosalba粉彩画遗赠给Mariette；Lorenzetti页145为书内引注，遗嘱及书目未查阅。注4记录Biblioteca Marciana MSS. Italiani, Cl. XI, Cod. CXVI, 7356的手稿定位、Zanetti所有权及卷内信件/索引摘要；并拆记1736年8月10日由Anne Marie de Savoye签署的收据，收据所载Poussin与Castiglione画作和15件未辨宝石/浮雕，以及Zanetti的`Memorie`提及Castiglione而未提Poussin、另记一幅由`lo Spagnolo di Bologna`作画的小型铜板田园画。该绰号不等同Crespi，签署人不推定为卖方，未把`Memorie`强判为独立卷册；手稿、收据和被引书均未独立查阅。

本批新增13个候选、44条提及和14条statement；四个印刷注号均回链至p.341实际标记处。印本校读仅记S2、不改S0：L225 `Ahecedario`→`Abecedario`、L226 `Pncipe`→`Principe`。脚本`chp13_p341_notes_migration.py`默认dry-run，核验来源/PDF SHA、表前态、候选ID、提及精确跨度、statement外键/引句、正文脚注目标及图版现状；应用前四表备份后缀`.bak-s2-chp13-p341-notes-20261003`。Plate 58a已由物理页15图注确认并映射到既有作品`cand-4048`；临时指针`cand-10059`排除。写回后p.341正文coverage转complete，注释总段推进到L180–226但继续保持partial。`audit_tables.py --summary`：830段中494 complete、108 excluded、223 queued、5 partial；候选10,191、提及22,062、statement 9,850；`s2_missing=[]`、`errors=[]`。尚有两条既存enrichment `source_ref`警告。下一源序为p.342注1–7（L227–234）；其后L235–238、L239–246及镜像题注L247–248仍待处理。

## 第十三章p.342页注（2026-10-03）

对照`CHP-13.pdf`物理页11，迁移p.342注1–7，新增9个候选、48条精确提及和11条原书statement。注1保留Marciana手稿中的七封Tessin信件及其日期、地点和印本`1743 (sic—but 1748)`校正；Strahlsund按印本拼写登记为待S3对齐的地点。注2保留首、三封信和画家身份不明；注3引用第三封信中Tessin询问Tiepolo、价格仍是障碍、愿提供食宿并加上国王津贴的法文原句；注4注明该Gai雕像叙述据第三封信并交叉指向第十章。注5识别Zanetti收藏的两幅Sebastiano Ricci作品，并将Pietro Monaco版画第41、84号分别映射至`Esther and Ahasuerus`及`The Presentation in the Temple`；另登记Carriera所绘Zanetti肖像用作1749年`Dactyliotheca`扉页。注6记录A. F. Gori 1752年12月22日来信在Biblioteca Marucelliana的架藏定位；注7保留Annibale碟画例外的意大利语短引及Kurz 1955页282–287书目。所引手稿、信件、版画及书目未独立查阅。S2只记页图校读，不改写S0：L227破折号，L228空格及`sic`，L230 `éloigné`→`éloigne`。p.342稀有版画statement仅保留Annibale碟画，后续Giulio Romano版画由p.343续文独立记录。正文coverage由partial转complete，合并注释coverage更新至L180–234且保持partial；S2仍不可交接S3。

## 第十三章p.345正文、页注及镜像题注收口（2026-10-03）

对照`CHP-13.pdf`物理页18完成正文`l161-171`及合并注释尾段L247–251。L247–248为反向/错序OCR题注片段，所载信息与Plate 57/58既有视觉转录段对应；按重复材料处理，不再新增提及或statement。p.345注1登记Pietro Monaco 112幅版画集短题名并与1763、1779两个现有版本候选保持未决；印本`di`校正OCR `Ji`只记于S2，不改S0。注2保留信件日期`4 February 1763/4`的印本歧义及British Museum架藏号`Add. MSS. 23,729, f. 49`，信件未查阅。注3登记Haskell所引Moschini 1924页167及其称信息源为P. A. Novelli撰写、藏于Seminario Patriarcale的Toni手稿生平；L171所载1790与1762年代均保持为Haskell报告，手稿与引用页未独立查阅。三条印刷脚注均按标记回链至p.345正文；L171的跨页句与p.346段保持连接。

本批新增3个候选、15条精确提及和3条statement。脚本`chp13_p345_notes_migration.py`默认dry-run，完成表前态、来源/PDF、mention跨度、statement引句、外键、脚注目标和既有图版段核验后应用；四表恢复副本后缀`.bak-s2-chp13-p345-notes-20261003`。应用后`audit_tables.py --summary`：830段中499 complete、108 excluded、223 queued、0 partial；候选10,208、提及22,160、statement 9,878；`s2_missing=[]`、`errors=[]`。两条既存enrichment `source_ref`警告不变；223段仍待语义处理。下一源序转入第14章。

## 第十三章p.343页注（2026-10-03）

对照`CHP-13.pdf`物理页12，迁移注1–4，新增1个候选、15条精确提及和4条原书statement。注1与注4复用Lorenzetti 1917来源候选，页码分别为122和55；注4只支持Tiepolo蚀刻版画“首次发表”断言，1743保留为Haskell所转述的可能年代，未写成确定年份。注2登记1760年`Varie Pitture a Fresco de' Principali Maestri Veneziani`序言为年轻A. M. Zanetti相关引文的出处；注3补录九名木刻赠页对象，不为其分派具体版画。p.342注6的1752年Gori来信定位同时回链p.343同一连续引语的四条statement；删除注4对前句风格判断的误挂。`de'Principali`印本留有空格，校读记录在S2、不改S0。引用页和书籍未独立查阅；正文coverage转complete，合并页注段推进至L180–238但仍partial。

## 第十三章p.342页注（2026-10-03）

对照`CHP-13.pdf`物理页11，迁移p.342注1–7，新增9个候选、48条精确提及和11条原书statement。注1保留Marciana手稿中的七封Tessin信件及其日期、地点和印本`1743 (sic—but 1748)`校正；Strahlsund按印本拼写登记为待S3对齐的地点。注2保留首、三封信和画家身份不明；注3引用第三封信中Tessin询问Tiepolo、价格仍是障碍、愿提供食宿并加上国王津贴的法文原句；注4注明该Gai雕像叙述据第三封信并交叉指向第十章。注5识别Zanetti收藏的两幅Sebastiano Ricci作品，并将Pietro Monaco版画第41、84号分别映射至`Esther and Ahasuerus`及`The Presentation in the Temple`；另登记Carriera所绘Zanetti肖像用作1749年`Dactyliotheca`扉页。注6记录A. F. Gori 1752年12月22日来信在Biblioteca Marucelliana的架藏定位；注7保留Annibale碟画例外的意大利语短引及Kurz 1955页282–287书目。所引手稿、信件、版画及书目未独立查阅。S2只记页图校读，不改写S0：L227破折号，L228空格及`sic`，L230 `éloigné`→`éloigne`。p.342稀有版画statement仅保留Annibale碟画，后续Giulio Romano版画由p.343续文独立记录。正文coverage由partial转complete，合并注释coverage更新至L180–234且保持partial；S2仍不可交接S3。


## 第十四章p.347开篇及注1–2（2026-10-03）

对照`CHP-14.pdf`物理页1，处理开篇正文`chp-14:14_CHP-14_intro:l3-12`与注释源段L169–170。新增18个候选、86条提及和12条statement。Algarotti个人收藏与Bonomo共同收藏不合并；Dresden王家画廊与已有候选保持身份待S3；“Zanotti brothers”保留集体指称；父亲未具名。脚注中的作品/文献只作Haskell书内引注记录，不声称独立查阅。页图校读记下L6、L7、L9的`It/eighteenth/48d/life`修正，不改S0；L12是脚注1跨段续文。p.347末句续至p.348，正文段partial；注释总段仅覆盖L169–170，也为partial。文件名标题段排除。写回后表审计`s2_missing=[]`、`errors=[]`；830段现为499 complete、109 excluded、220 queued、2 partial；下一段为p.348正文`l14-21`。


## 第十四章p.348正文及注1–3（2026-10-03）

按`CHP-14.pdf`物理页2处理正文`chp-14:14_CHP-14_intro:l14-21`及页注L171–173。新增14个候选、19条statement；初始mention审计发现四处同区间代词重复映射，修正后保留106条新提及。印刷页348 L15闭合页347 Bonomo跨页句，故p.347正文转complete。页348记录Algarotti早期艺术趣味、旅行、Palladio、佛罗伦萨/罗马观画、Bottari及同期学者关系；书信中的直接引文仍标注Haskell转述。注1–3均已按标记回链，所引信件/出版物未独立查阅。p.348 L21以“less than”截断并续至p.349 L23，故p.348正文partial；合并页注段迁移到L169–173后仍partial。审计`s2_missing=[]`、`errors=[]`；830段：500 complete、109 excluded、219 queued、2 partial；候选10,240、提及22,352、statement 9,909。下一源段为p.349正文`l23-33`。

## 第十四章p.349正文及注1–4（2026-10-03）

按`CHP-14.pdf`物理页3处理正文`chp-14:14_CHP-14_intro:l23-33`及页注L174–177。新增10个候选（cand-10254–cand-10263）、100条提及和27条statement。p.349 L24闭合p.348 L21未完句，故p.348正文转complete；L33末句继续至p.350 L35，p.349正文仍partial。录入Paris、London、Cirey、Venice、Milan、Turin、Dresden、Prussia、Bologna、Florence、Pisa、Rome、Berlin等地点及书信、出版物和人物；会面、同住、社会往来、宫廷服务、购画、著作和通信影响保留为关系候选，不升级为正式边。脚注1–4均回链；Halsband缺书目信息、引用文献未独立查阅。L177印本日期为1735，OCR的1733保留为锚点并在statement qualifiers校正；其他印本校读同样只记S2、不改S0。表审计`s2_missing=[]`、`errors=[]`；覆盖830段为501 complete、109 excluded、218 queued、2 partial。下一源段为p.350正文`chp-14:14_CHP-14_intro:l35-44`。

## 第十四章p.350正文及注1–3（2026-10-03）

按`CHP-14.pdf`物理页4处理正文`chp-14:14_CHP-14_intro:l35-44`及页注L178–179，新增7个候选、68条提及和18条statement。p.349的跨页句在p.350闭合；p.350 L44新句续至p.351 L46，正文仍partial。录入Algarotti 1741年柏林肖像书信、1737年威尼斯期间接触在世艺术家的证据限定、1742年后国际艺术界活动，以及Dresden王家画廊方案的历史陈列原则和在世艺术家委托设想。保留“没有证据”的限定、作者解释与计划语气；未具名艺术家群体及Lodoli收藏均不越界补造身份/类型。印本注1–3已回链至Bonomo书信、`Opere`卷VIII页351–388和第12章交叉引用；书信、引文未独立查阅。表审计通过，下一正文段为`chp-14:14_CHP-14_intro:l46-53`。

## 第十四章p.351正文及注1–2（2026-10-03）

按`CHP-14.pdf`物理页5处理正文`chp-14:14_CHP-14_intro:l46-53`及页注L180–181，新增8个候选、67条提及和23条statement。p.351 L47闭合p.350 L44句；p.351 L53止于“in a painting”，续文在p.352 L56，故本段partial。记录风格作为题材选择依据、三位画家的引述评价、历史画家分类与方案名单、艺术家题材建议、跨国合作、城市/区域名单、对罗马价值的作者评价、Algarotti不在场时信息来源的限定、回威尼斯实施计划及作品组的完成/遗失状态。候选题材与五幅已绘制后遗失的作品组分立；Haskell对艺术影响力的怀疑和所有引文出处的未独立查阅状态均保留。页注1–2分别回链Crespi的后续赞扬及五幅作品组；S0不变，印本校读仅记录于S2。表审计通过，下一正文段为`chp-14:14_CHP-14_intro:l55-61`。

## 第十四章p.352正文及注1–3（2026-10-03）

对照`CHP-14.pdf`物理页6，迁移正文`chp-14:14_CHP-14_intro:l55-61`及注1–3（L182–184）。净增4个候选（cand-10279–cand-10281、cand-10283）、73条提及及21条原书statement。记录Haskell所述《The Banquet of Cleopatra》与Algarotti/Tiepolo关系、Algarotti对Tiepolo的计划内评价及后续转变、1743年Tiepolo致Algarotti信、1744年拟向Count Brühl转送画作、Joseph Smith作为原委托人的“几乎可以肯定”判断，以及两件不同版本、图版61a/61b和各自场景差异。所有身份/归属仍保留原书限定；跨章候选cand-9162与Melbourne版本是否同一留待S3。注1–3仅登记书内引注及出版定位，不称独立查阅；注2保留“或许1737年在Milan相遇”及“1743年前没有真实证据”的限定，复用已登记的Morassi作者`cand-8257`和著作`cand-8258`。页图校读记于S2：OCR `1757?`校为印本`1737`并回链注2，`Cognacq-‘Jay`校为`Cognacq-Jay`，`fight`校为`light`，`theatrical;her`校为空格分隔；不改写S0。p.351末句由p.352 L56闭合并转complete；p.352 L61未完句续至p.353 L63，故正文段partial。首次全表审计发现三处同字符区间重复提及，按索引语境删除重复后净保留73条；另发现Morassi 1955著作在既有候选中已登记，改用既有作者/著作候选。最终审计无errors。下一段为p.353正文`chp-14:14_CHP-14_intro:l63-71`。

## 第十四章p.353正文及注1（2026-10-03）

按`CHP-14.pdf`物理页7迁移正文`chp-14:14_CHP-14_intro:l63-71`及合并页注段中的注1 L185。L64闭合p.352未完比较句；p.353 L71末尾“As in The”续至p.354 L74，因此正文和后续页注仍partial。新增15个候选、74条提及和24条statement，涵盖完成版与草稿的视觉差异、Pompeii/Herculaneum与Greek vase、Mark Antony、Isis/Serapis、Algarotti对原modello版画和Tiepolo构图的评价、罗马画派与威尼斯、古典主义比较、向Brühl委托两项题材及注1所列作品位置和来源。注1中的Leonardis Maecenas版画/Plate 68b独立于Banquet原modello版画；Haskell的版本位置和动机判断保留其报告层级。增加`canvas`和`Europe`的既有候选提及；引文范围首轮审计后扩至L69–70。印本校读记录L65 OCR残片、`parellel`、`may ell`和`whichdie`修正，未改S0；被引文献/书信未独立查阅。全表审计通过：830段为505 complete、109 excluded、214 queued、2 partial；候选10,284、提及22,734、statement 10,022。下一源段为p.354正文`chp-14:14_CHP-14_intro:l73-83`。

## 第十四章p.354正文及注1–5（2026-10-03）

按`CHP-14.pdf`物理页8迁移正文`chp-14:14_CHP-14_intro:l73-83`及页注L186–190。p.354 L74闭合p.353末句；p.354 L83以“demands of neo-classical”未完句续至p.355，故p.354正文保持partial。新增8个候选、71条提及和27条statement，记录Banquet构图判断、Algarotti本人委托《Bath of Diana》、Boucher/Paris风格比较、Algarotti色彩与Newton光学观念、Giorgione/Titian、Tiepolo与Algarotti相互影响、Oriental heads素描/蚀刻及后来对Tiepolo的总结。独立将Algarotti创作的素描/蚀刻组与索引中Tiepolo在p.260注的另一作品候选留作不同对象；不把Haskell对调色板的推断写成文献确证。五条页注均回链，所引论文、信件和著作未独立查阅；note 3另记录Haskell关于白底构想“刚刚出现”的转述并保留限定。印本校读只记S2、不改S0。最终审计：830段为506 complete、109 excluded、213 queued、2 partial；候选10,292、提及22,805、statement 10,049。下一源段为p.355正文`chp-14:14_CHP-14_intro:l85-95`。


## 第十四章p.355正文及注1–3（2026-10-03）

对照`CHP-14.pdf`物理页9处理正文`chp-14:14_CHP-14_intro:l85-95`及注1–3（L191–193）。新增20个候选（`cand-10307`–`cand-10322`、`cand-10324`–`cand-10327`）、87条提及和27条原书statement。p.355 L86闭合p.354 L83“neo-classical correctness”，p.354正文转complete；p.355 L95末句止于“still intensively”，续至p.356，故p.355正文仍partial。注释总段推进至L193、仍partial。

记录Algarotti的威尼斯文化认同与国际主义处境、其试图调和Tiepolo幻想与新古典规范的矛盾、Piazzetta受Algarotti委托为Augustus绘制《Caesar and the Corsairs of Cilicia》、该画与两幅后续古典题材画的关系、Newtonianismo首版扉页、家族绘画收藏的形成/扩充与规模、寄往Dresden的画作/草图复制品，以及Tiepolo在藏品中的约13幅绘画和116幅素描。单独登记未具名画作组、委托事件、具体作品和收藏对象；p.355失传委托不自动等同p.351五幅作品组，家族收藏不自动等同p.347个人/共同收藏。p.355 note 2列出两处作品地点但未明确分别对应，故不作逐件地点配对；Haskell“没有证据”Algarotti接触Canaletto的判断保留原有限定，不写成未接触的确定事实。

页注1–3均回链：Michelessi/`Opere`定位复用既有候选；Pallucchini 1956页41保留为未核引文；Selva书目保持未识别，Levey 1960论文复用p.354同一候选。页图校读记于S2、不改S0：note 1 `Ixii`→`lxii`，note 3 `i960`→`1960`；被引资料未独立查阅。迁移脚本`chp14_p355_s2_migration.py`默认dry-run并锁定来源/PDF SHA，四表备份后缀`.bak-s2-chp14-p355-20261003`。写回后审计`s2_missing=[]`、`errors=[]`；830段为507 complete、109 excluded、212 queued、2 partial；候选10,312、提及22,892、statement 10,076。两条既存enrichment `source_ref`警告不变。下一源段为p.356正文`chp-14:14_CHP-14_intro:l97-107`。

## 第十四章p.356正文及注1–7（2026-10-03）

p.356正文段`chp-14:14_CHP-14_intro:l97-105`新增24个候选、72条提及及27条statement；p.355 L95的Canaletto句已闭合，p.355正文coverage转complete。L98–103记录Consul Smith、Bonomo、1746–1753行程、Berlin/Potsdam活动、Frederick宫廷艺术计划、Marchiori委托、Bouchardon/Rode介绍信、Tiepolo对Rode影响的预测、Walpole礼赠设想、1764年Pitt遗赠、财务/市场动机及书内作者解释。L104–105记录neo-Palladianism、Chiswick住宅plans和Palladio图稿；p.356 L105末句仍续至p.357，故正文coverage partial。`their collection`保持未决；匿名画作、雕像、书信及建筑图稿不补造题名、完成状态或唯一指代。

合并注释段L194–200的注1–7均迁移并回链。注1所引Bonomo信中的`farli`无明确作品先行词；注2四封、注3两封、注7两封有具体日期的信件逐封列为archive候选，介绍信亦按Bouchardon/Rode两个收信人拆分；注4购画为价格适中时的条件性意见；注5为Treat转引Diderot；注6仅给1742年12月信件线索；注7复用既有`Opere`版次候选。所引信件、论文及Treat原书未独立查阅。印本校读记于S2、不改S0：`thistime`、`commision`、`T1`、`pretcnderebbe`、`fame`、`facilitate`、`1’esecuzione`、`Opéré`分别校读为`this time`、`commission`、`Il`、`pretenderebbe`、`farne`、`facilitare`、`l’esecuzione`、`Opere`。

脚本`chp14_p356_s2_migration.py`默认dry-run；受控写回后表审计`s2_missing=[]`、`errors=[]`。全库coverage：508 complete、109 excluded、211 queued、2 partial；候选10,336、提及22,964、book statements 10,103。两条既存enrichment来源警告仍在。下一源段为第十四章p.357正文`chp-14:14_CHP-14_intro:l107-116`；全书S2尚未满足S3交接条件。



按`CHP-14.pdf`物理页11处理第十四章p.357正文及注1–8。新增28个候选、75条提及和24条statement；闭合p.356末句，p.356转complete。p.357正文L115的理论委托句续至p.358，正文及合并页注段仍partial。页注已回链；Lazzarini人名/作品归属、Canaletto Rialto视图与已知候选的身份关系、Parma作品版本均留待后续阶段；被引书信和论文未独立查阅。印本校读修正注号、OCR拼写和遗漏的注7标记，只记S2、不改S0。全表审计`s2_missing=[]`、`errors=[]`；830段中509 complete、109 excluded、210 queued、2 partial，候选10,364、提及23,039、statement 10,127。下一源段为p.358正文`chp-14:14_CHP-14_intro:l118-124`。


按`CHP-14.pdf`物理页12处理第十四章p.358正文及注1–6。新增17个候选、52条提及和36条statement；闭合p.357理论方案句，p.357正文转complete。p.358 L124续至p.359 L127，故正文partial；页注已处理至L213。保持匿名Flemish画家、私人考古书库类型待定、书信档案机构未指明、‘this type of painting’指称范围未决；Pesci的索引候选与p.357新增候选留待S3核对。印本校读只记S2、不改S0。审计`s2_missing=[]`、`errors=[]`；830段中510 complete、109 excluded、209 queued、2 partial，候选10,381、提及23,091、statement 10,163。下一源段为p.359正文`chp-14:14_CHP-14_intro:l126-137`。

按`CHP-14.pdf`物理页13处理第十四章p.359正文及注1–4。新增18个候选、49条提及和24条statement；闭合p.358 L124限制句，p.358正文转complete。记录Tiepolo补加人物、为Pesci建筑背景加入的Titian式风景/船/白马、Tiepolo晚年小型委托、Algarotti对Tesi的依赖及与Tesi妻女的书内关系、复制与版画工作、1764年Pisa室内装饰、理论著作及Haskell对其新古典倾向和理论限定的评价。匿名人物身份、Dietrich与索引候选同一性、筹备中文集与后出十七卷本的关系均留待后续阶段；引文未独立查阅。页注1–4分别保存来源定位与Gabbrielli 1938/1939引文。后续印本复核未在p.359正文找到注4标记；p.360自己的注4是Leslie《Memoirs》，两者分立。p.359 Gabbrielli注4列为孤立标记审计项。S2校读不改S0：L128 `Use`→`life`及句首误点移除；L129 `confmed`→`confined`；L131 `himselff`→`himself`；L137 `picturesque.-He`→`picturesque.—He`；L215 `Opéré`→`Opere`。全表审计为`s2_missing=[]`、`errors=[]`；830段中511 complete、109 excluded、208 queued、2 partial，候选10,399、提及23,140、statement 10,187。p.359 L137续至p.360 L140。下一段为p.360正文`chp-14:14_CHP-14_intro:l139-146`；全书S2仍未达到S3交接条件。

按`CHP-14.pdf`物理页14迁移第十四章p.360正文及注1–4。新增8个候选（cand-10415–cand-10422）、39条提及和22条statement；闭合p.359末句，p.359–360正文均转complete，合并页注段补齐至L220。记录Algarotti的旧传统倾向、对Tiepolo/Tesi的态度、Haskell对其新古典阶段与性格的评价、Caylus引文、Constable阅读及Frederick纪念碑/铭文；保留各自说话层级和限定。注1–4分列Zanetti、Patriarchi、Halsband、Biffi、Nisard、Leslie来源，引用均未独立查阅；p.328注5仅作为原书交叉引用，不证明相同手稿。印本校读：L143去除`psychological`前误连字符；L146 `mortar`→`moriar`；L219 OCR注号`8`→印本`3`；均只记S2不改S0。p.359 Gabbrielli注4正文标记未定位，列为孤立注号审计项；p.360 Leslie注4独立回链。Plate 60只交叉引用图版目录，不断言版画等同实体纪念碑。首轮机械审计暴露一条跨页statement行定位超出S2段覆盖，锚点改为p.360 L140后通过：830段514 complete、109 excluded、207 queued、0 partial；候选10,407、提及23,179、statement 10,209；`s2_missing=[]`、`errors=[]`。下一段为p.361正文`chp-14:14_CHP-14_intro:l148-149`。

对照`CHP-14.pdf`物理页15–18完成图版61–64的S2视觉处理。新增11条提及、4条statement、无新候选。图版61早期/最终版本沿用图版目录中分立对象；图版62 Canaletto/Prà della Valle题注链接既有对象并记录OCR“Prato”与印本“Prà”差异；图版63截断题注只通过图版目录核对完整题名，不改S0；图版64倒序OCR校读为Francesco Guardi及John Strange别墅、Paese、Treviso，并链接既有题注。图版与来源核验后第十四章现有S2覆盖全部complete。全账本830段517 complete、109 excluded、204 queued、0 partial；候选10,407、提及23,190、statement 10,213；机械审计无错误。下一源包为第十五章开篇。


第十五章p.361（`CHP-15.pdf`物理页1）已完成章题与注1–2核读，以及Farsetti小节正文截至段尾。新增8个候选、53条提及和27条statement，记录绘画衰退评价、艺术家处境、主要藏品变化和启蒙语境中的新赞助方式。Smith余下画廊及未具名遗孀、Zanetti未指明藏画、Mariette的推测及“these men”指代均保持来源边界；引文未独立查阅。印本OCR校读仅记S2，S0未改。页码复核以物理第2页页眉“362”确认本页为p.361，已更正初次写入的页码和ID标签。p.361末句由p.362 L17闭合，正文段现为complete；下一源段为p.362正文`chp-15:15_CHP-15_sec_i:l16-25`。

第十五章p.362正文已迁移并与p.361跨页收口，新增19个候选、86条提及和42条statement；p.362注1–2已回链，引用来源未独立查阅。Farsetti在罗马如“English milord”的说法保留为Haskell修辞；“This”指代未决；四十二根柱子句续至p.363 L28，p.362正文仍partial，合并页注段只处理至L45并保持partial。页下注跳转复核确认`cand-2898`只是指向Rezzonico的索引交叉引用，不是第二个人；已把p.362两条姓名提及和statement改接既有`cand-2137`。迁移及修复分别保存独立备份。机械审计`s2_missing=[]`、`errors=[]`；全账本830段中520 complete、111 excluded、197 queued、2 partial，候选10,434、提及23,329、book statements 10,282；两条既存enrichment来源警告保留。下一源段为p.363正文`chp-15:15_CHP-15_sec_i:l27-36`；全书S2仍未达到S3交接条件。

第十五章p.363（`CHP-15.pdf`物理页3）已迁移，新增12个候选、86条提及和36条statement；闭合p.362关于四十二根柱子的跨页句。正文记别墅建筑/园林评价、百万ducats传闻及匿名引文、赞助影响、Canova与Daniele；注1、3–6已回链，注2定位于正文段L36。页图校读限定在S2、不改S0；所引书信、档案及文献未独立查阅。Daniele继续赞助当代艺术家的句子续至p.364 L39，p.363正文保持partial；合并页注段覆盖至L50也保持partial。机械审计`s2_missing=[]`、`errors=[]`；全账本830段中521 complete、111 excluded、196 queued、2 partial，候选10,446、提及23,415、book statements 10,318；两条既存enrichment来源警告保留。下一源段为p.364正文`chp-15:15_CHP-15_sec_i:l38-41`；全书S2未达到S3交接条件。

第十五章p.364 Farsetti段末（`chp-15:15_CHP-15_sec_i:l38-41`）及注1–2已完成，新增6个候选、38条提及、15条statement；闭合p.363 Daniele继续赞助当代艺术家的跨页句。Tommaso Giuseppe、家族史、个人书籍/手稿收藏、财产拆散与出售、Haskell对Farsetti影响的评价及新旧赞助模式分别记录；兄弟、举报等仅作为S2关系候选，藏品分类和家史书目身份不外推。注1档案定位、注2 Moschini 1806卷II页114按书内citation trail记录，原件和引文未独立查阅。p.363与p.364 Farsetti正文均转complete；合并页注coverage至L52仍partial，L53–56须随相邻Andrea Memmo正文`chp-15:15_CHP-15_sec_ii:l3-4`处理。全表审计`s2_missing=[]`、`errors=[]`；830段中523 complete、111 excluded、195 queued、1 partial；候选10,452、提及23,453、statement 10,333。全书S2未满足S3交接条件。

## 第十五章p.364 Andrea Memmo开篇及注3–6（2026-10-04）

正文段`chp-15:15_CHP-15_sec_ii:l3-4`新增10个候选、31条提及和19条statement；记录Memmo的Smith/Lodoli语境、政治改革、贵族交往与法国文化影响。注3–6分别链接Chapter 12、Molmenti/Torcellan书目线索、Chapter 11和Tabacco页32 ff.；所引文献未独立查阅。p.364段尾“and he”保留partial，印本核对将“chaste architecture”后的印本注5与OCR错读注6区分，并把真正的注6连至Tabacco。后由p.365 L7闭合。p.364合并页注段L44–56现complete。

## 第十五章p.365正文及注1–2（2026-10-04）

对照物理页5处理印刷页365，新增5个候选、50条提及和26条statement；闭合p.364 Andrea Memmo跨页句。迁移其政治任命、Padua农业集市、Prà della Valle改造和雕像方案，并保留Haskell评价限定、未查引文及名称/索引条目的待对齐状态。注1–2与正文标记回链；Radicchio 1786和Neu-Mayr 1807分别作为引文定位，均未独立查阅。印本校读只记S2、不改S0。p.365末句“to the”接续至p.366 L15；正文coverage partial，合并注释只处理L91–92。全表审计`s2_missing=[]`、`errors=[]`；830段为525 complete、111有理由排除、192 queued、2 partial；候选10,467、提及23,534、statement 10,378。两条既存enrichment `source_ref`警告仍在；全书S2未满足S3交接条件，下一段为`chp-15:15_CHP-15_sec_ii:l14-28`。


第十五章p.366正文及注1（2026-10-04）已对照`CHP-15.pdf`物理页6处理，新增20个候选（cand-10483–cand-10502）、85条提及和26条statement；闭合p.365表示资格句，p.365正文coverage转complete。登记雕像资格、质量/成本标准、Antenor及Azzo d’Este雕像、布伦瑞克家族、Padua所选祖先、Memmo赴君士坦丁堡后的募像活动、Subleyras图稿、捐助者与Piranesi版画、1786年Radicchio记述及雕像完成进度。未命名人物/机构保持未决；“another six in Rome”语义关系不外推。注1所列英国博物馆信件材料未独立查阅，保留Haskell引用链并链接公爵雕像statement。印本校读仅记S2、不改S0：`Prato`→`Prà`、`Memiiio’s`→`Memmo’s`、`dining`→`during`。p.366末句续至p.367，故p.366正文partial；合并页注段L93–113仍待后续处理。表审计`s2_missing=[]`、`errors=[]`；830段为526 complete、111 excluded、191 queued、2 partial；候选10,487、提及23,619、原书statement 10,404。两条既存enrichment `source_ref`警告保留。下一源段为p.367正文`chp-15:15_CHP-15_sec_ii:l30-36`；全书S2尚未达到S3交接条件。

第十五章p.367正文及注1–4已迁移（+9候选、64提及、29 statement），关闭p.366跨页句；p.367末句仍续至p.368 L39，注L97–113尚未处理。候选表面回查另补p.363术语`amateur`提及1条，更新既有statement的mentioned候选。当前审计：830段中527 complete、111 excluded、190 queued、2 partial；候选10,496、提及23,684、statement 10,433；`s2_missing=[]`、`errors=[]`，保留两条既存`source_ref`警告。S2未满足S3交接条件，下一段为p.368正文`chp-15:15_CHP-15_sec_ii:l38-47`。

第十五章p.368正文及注1–7已迁移（+15候选、49提及、24 statement），并闭合p.367的Prà della Valle跨页句；sec_ii L1生成式Markdown标题已按同章规则排除。p.368 L47关于State Inquisition权限的句子继续至p.369；注段已处理到L104。候选表面回查对p.368 Venice产生一个同名重复候选提示：该词的提及已连到cand-2719，另一候选cand-3401仍待S3做全局同一性裁决；不据字面提示增造重叠提及。注L105–113中的Europe、The Hague仍处queued范围。当前审计：830段中528 complete、112 excluded、188 queued、2 partial；候选10,511、提及23,733、statement 10,457；`s2_missing=[]`、`errors=[]`，保留两条既存`source_ref`警告。S2未满足S3交接条件，下一段为p.369正文`chp-15:15_CHP-15_sec_ii:l49-59`。

第十五章 p.369 已处理：新增18个候选、50条提及、32条statement；闭合p.368 Querini/State Inquisition跨页句，迁入p.369注1–4，p.369末句及合并注释L109–113继续待后页处理。页图校读确认标题“A NEW DIRECTION”被OCR漏掉，只记S2；该页传闻、作者评价、被引资料和关系候选均保留原有限定。全表审计 `s2_missing=[]`、`errors=[]`；830段中529 complete、112 excluded、187 queued、2 partial。下一正文段为 p.370 `chp-15:15_CHP-15_sec_ii:l61-67`。

第十五章 p.370正文及注1–2已处理：新增24个候选、48条提及、24条statement，闭合p.369末尾城市规划句；别墅陈设、园林、雕塑及引文关系均按书内叙述登记，保留作者解释和待决身份。页注L109–110已迁移，均未独立查阅。`audit_tables.py --summary`通过，`s2_missing=[]`、`errors=[]`；830段中531 complete、112 excluded、186 queued、1 partial。下一正文段为p.371 `chp-15:15_CHP-15_sec_ii:l69-83`。



## 第十五章p.371–372正文及注释（2026-10-04）

p.371–372正文及合并注释L111–113已迁移，闭合p.371跨页句。新增29个候选、72条提及和40条statement；另为p.371补登Naples、Renaissance两条漏记提及。主要记录Querini的艺术赞助、De Non活动、Canova所作Renier胸像、Querini掷像与异教遗址、Maffei/Winckelmann比较、Rousseau影响及心脏安葬；限定Haskell评价、身份推定和匿名传闻。注释书目、馆藏及建议均未独立核验。首轮跨段statement锚点问题已修复；表审计`s2_missing=[]`、`errors=[]`。当前830段中534 complete、112 excluded、184 queued、0 partial；候选10,582、提及23,903、statement 10,553。下一段为第十六章`chp-16:16_CHP-16_intro:l1-1`，全书S2尚未收口。

## 第十六章 p.373 开篇及注1–2（2026-10-04）

p.373开篇正文及注1–2已处理：新增10个候选、30条提及、16条statement；候选表面回查再补“art patrons”与注中Venice两条提及，并更新对应statement的候选清单。记录Haskell对威尼斯绘画传统与经销者的判断、Sasso的早期经历、John Strange往来与购画业务；姓名差异与未完句分别留待S3和p.374闭合。注释中的书目与馆藏线索未独立查阅。印本校读只记S2、不改S0，`[Page 2]`标记保留并记录其与连续页序推定的印刷页373不一致。

当前审计：830段中534 complete、113 excluded、181 queued、2 partial；候选10,592、提及23,935、statement 10,569；`s2_missing=[]`、`errors=[]`。候选表面回查余下14个提示均在未处理的合并注段L72以后；下一段为p.374正文`chp-16:16_CHP-16_intro:l16-22`。

## 第十六章 p.374 正文及注1–4

p.374已迁移（+9候选、52提及、19 statement），并闭合p.373购画列表；p.374 Sasso收藏清单续至p.375。正文保留经销过程、Guardi/ Tiepolo艺术偏好、Armanni对Poore的引述、Canova索取Tiepolo modello及被Haskell否定的“Sasso买尽”传闻。注1–4已回链，书信、档案及拍卖目录未独立查阅；印本校读只记S2、不改S0。当前审计：830段中535 complete、113 excluded、180 queued、2 partial；候选10,601、提及23,987、statement 10,588；`s2_missing=[]`、`errors=[]`。余下9个启发式提示在未处理的注释行L76以后。下一源段为p.375 `chp-16:16_CHP-16_intro:l24-36`，合并注段从L76继续。

## 第十六章 p.375 当前结果

p.375正文及注1–6已迁移，闭合p.374 Sasso收藏清单；新增12个候选、63条提及和20条statement。人物della Lena复用候选cand-1387；Sasso目录、其通信及手稿、della Lena致Ortes信分别保留文献候选；Haskell 1960与1967书目定位分别复用/新增对应候选，均未独立查阅。正文的Sasso经销、Worsley/Palmerston、della Lena生平、家族、收藏与审美观点均保留Haskell转述层级和限定。页图OCR校读只记S2，不改S0。当前审计：830段中537 complete、113 excluded、179 queued、1 partial；候选10,613、提及24,050、statement 10,608；`s2_missing=[]`、`errors=[]`。剩余2个表面提示位于待处理注L83–84；下一段为p.376正文`chp-16:16_CHP-16_intro:l38-46`及其后续脚注。

## 第十六章 p.376 当前结果

p.376正文与注1–3已迁移：新增17个候选、55条提及、29条statement；候选表面复核另补既有“old masters”术语候选cand-4288的提及及statement映射，合计56条提及。段落保留Vianello、Toninotto、del Pian和Swajer相关书内叙述及限定；Ricci、Chioggia Cathedral类型边界与无题作品身份待后续处理。印本校读记入S2，未修改S0。p.376正文末句与注3均跨页未完，保持partial并连至p.377 L49及L60–64。当前审计：830段中537 complete、113 excluded、178 queued、2 partial；候选10,630、提及24,106、statement 10,637；`s2_missing=[]`、`errors=[]`。第十六章5个已审段的候选表面启发式回查无未覆盖提示；下一源段为p.377正文`chp-16:16_CHP-16_intro:l48-64`。

第十六章p.377按印刷页图迁移，新增26个候选（cand-10647–cand-10672）、65条提及、34条statement；闭合p.376 Swajer跨页句和注3，并完成p.377合并注段。Celotti跨政权经销、作品与销售文案保持Haskell转述及引语层级；群体句保留为群体断言。p.378结论另增1个Venetian tradition候选、6条提及、3条statement，接续p.377群体语境，没有把回顾性“守护者”评价落实为制度身份。

第十七章p.379 folio i已迁移（+15候选、52提及、25 statement），Manfrin正文和注1–6按页图处理；正文尾句暂partial，并由p.380闭合。p.380正文及已到达注1–6迁移（+6候选、70提及、26 statement，含1条表面回查补记），关闭p.379 partial。保留Armanni引语、Manfrin画廊选择及作者评价，未独立查阅被引材料。分节OCR的p.380注5后半与正文L16–20重复，已由页图和整章OCR核实并由正文statement覆盖；S0不改。合并注段L26–35因L32–35属于p.381页注仍partial。当前审计：830段545 complete、115 excluded、169 queued、1 partial；候选10,678、提及24,299、statement 10,725；`s2_missing=[]`、`errors=[]`。第十七章候选表面扫描2个提示均位于未处理的p.381注L33、L35。下一源段为`chp-17:17_CHP-17_sec_i:l22-24`；全书S2尚未达到S3交接条件。

第十七章p.381 Manfrin正文、Correr正文及注1–5已按页图处理：新增12个候选、47条提及和29条statement；合并注段L26–35转complete。p.381 Correr末句续至p.382，`chp-17:17_CHP-17_sec_ii:l3-5`保持partial；生成式section-II标题排除。保留Moschini/Meschini与Bernardo/Bernardino来源拼写差异，补记OCR漏失的Archivio Correr 1468/10定位，并将四个候选表面提示按页码与题材语境裁决。审计：830段547 complete、116 excluded、166 queued、1 partial；候选10,690、提及24,346、statement 10,754；`s2_missing=[]`、`errors=[]`。下一源段为p.382正文`chp-17:17_CHP-17_sec_ii:l7-17`，全书S2尚未达到S3交接条件。

第十七章p.382正文L7–17及注1–3、5–6迁移完成；本页注4在正文L16–17。新增16个候选、60条提及、30条statement；页图校读差异保留于S2，不改S0。p.382 L8关闭p.381 partial；p.382正文L15续至p.383，仍partial；聚合注段L24–33只迁移L25–29，p.383注L30–33待处理。Renaissance术语复用cand-3578；四个p.381表面提示已按语境裁决，Biblioteca Correr命中属于尚未审读的p.383注L31。审计：830段548 complete、116 excluded、164 queued、2 partial；候选10,706、提及24,406、statement 10,784；`s2_missing=[]`、`errors=[]`。下一源段为p.383正文`chp-17:17_CHP-17_sec_ii:l19-22`。

第十七章p.383正文L19–22与书末注1–3已按印本完成；闭合p.382跨页句，新增10个候选、32条提及、19条statement。候选归属差异、Haskell评价、原件未查及Byron/Bonington身份待S3均保留限定；S2层记录Libertà、1960及1468/10 (9a)印本校读。当前全书830段：551 complete、116有理由排除、163 queued、0 partial；总账10,716候选、24,438提及、10,803条statement，机械审计无errors。下一段为结论部分`chp-18:18_CHP-18Conclusion:l1-1`，先裁定结构性材料，再续读正文。

第十八章结论：`l1-1`文件名标题已理由排除；p.384–385两个正文段按独立`CHP-18Conclusion.pdf`逐页核读并迁移，补齐p.384 L17→p.385 L20跨页句，无脚注。新增13候选、77提及、20 statements； OCR校读记S2、不改S0，引用材料未外部核验。审核后全书830段为553 complete、117 excluded、160 queued、0 partial；总账10,729候选、24,515提及、10,823 statements；机械审计无errors，结论段候选表面扫描无未映射提示。下一步处理附录`chp-19:19_CHP-19Appendix:l1-1`及后续段。

附录p.386–387已完成当前页的S2迁移：p.386三封Brandi信及OCR漏掉的8 March 1676日期/署名已完成；新补的收据开头与p.387结尾合读，登记28 March 1682的200 scudi全额结清及三幅画、`Volta`、修补和画家支出，未把该收据并入1675–1676 Novitiate委托。p.387另分别登记Maratti 22 September 1679的100 scudi预付款/一年完工承诺及19 September 1687的300 scudi终款，两张收据本身独立，付款者和条件按原文保留。附录二标题及Fondo Orsini 171, c. I信件L37–41已登记；匿名写信人、Giacomo Ant:o、Madonna模型、四模型、gioia、柄状构件、德国铸造者及家属、原料/工艺和四枚sapphires均按文本边界保存。跨章作品/人物身份留待S3；p.387末句续到p.388，因此段状态为partial。合计新增35候选、64提及、22 statements；覆盖账本为832段中556 complete、118 excluded、157 queued、1 partial。审计`errors=[]`、`s2_missing=[]`；p.386–387候选表面扫描当前0未映射提示，仅为启发式检查。下一段是`chp-19:19_CHP-19Appendix:l43-63`，先闭合p.387末句。

## 第十九章 p.388–389：附录二续信与附录三（2026-10-04）

p.388 c.140与173, c.2两封Domenico Pedini信分别记录未执行的铜铸计划、后续铸件及Bernini限制修整的命令；p.389的c.463署名读作Dom.o Fedini，闭合p.388起始信件并把原“未具名写信人”映射回Fedini局部候选。Fedini与Pedini两名书内候选及索引Fedini条目留待S3。Tacca 172,c.306书信记录马模型的运输安排和有条件的铜铸配件方案，不推断雕像已完成。附录三两封1705年信由第八章p.227注1–2回指：Franceschini列举备选题材但未说这些方案已获选；Giuseppe报告Felice选择特洛伊题材，但信件未证明作品完成。Tona [sic]保留原印本拼法；页图将Febee读作Felice，`all’in sù`后的框状字形记作图示而非文字。底层稿本未独立查阅。

该批新增6个候选、40条提及和7条statement，p.387–389均complete。首次审计发现两条委托说明statement的规范化claim重复；通过受控修正为Franceschini与Felice分别建立对象级claim后，`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`。候选表面扫描的唯一提示`modello`指向cand-3451“油画初稿”，与本段马雕塑模型cand-5555不同义，已作为误报记录。全书当前832段：559 complete、118有理由排除、155 queued、0 partial；候选10,781、提及24,662、statement 10,861。下一段为p.390 `chp-19:19_CHP-19Appendix:l86-107`。


## 第十九章 p.390：附录四（2026-10-04）

p.390 L91–99的两封1706年Ricci/Ferdinand信、L101–104的Crespi信均按页图迁移。记录两箱画的内容与交付、两处房间装饰计划及第二封信中的延期；各项均不表示房间或作品已完成。用第八章p.235回指确认Ricci侄子为Marco，但Canon Marucelli的名字仍不明。区分1706年随箱小画和1708年Crespi对画廊小画的作者自述；后者同时保留Tintoretto的转述归属，不据此作独立鉴定。Ranuzzi 1708年1月31日信于L105开始，档案定位为Filza 5897, No.183，L107的`Spagnuolo Pittore`身份待p.391续文，因此本段reviewed/partial。

第八章p.235物理页41与附录p.390物理页5均印8 May 1706信为No.500；原脚注OCR`zoo`此前被误解为200。当前cand-7976及脚注statement的claim、predicate和OCR校正已改为500，稳定statement主键与原OCR引句保留。p.390新增5候选、45提及、10 statements。S2迁移脚本首次审计发现coverage行范围多写一个`L`，修成契约格式`L87-107`后复审`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；两条既存enrichment source引用警告及1条partial/154 queued提示仍在。候选表面扫描7个已读段只提示既有异义`modello`，p.390没有新未映射提示。全书当前832段：559 complete、118有理由排除、154 queued、1 partial；10,786候选、24,707提及、10,871 statements。下一段p.391为`chp-19:19_CHP-19Appendix:l109-124`。

## 第十九章 p.391 当前结果

已处理附录四Ranuzzi书信续文及附录五开篇。p.391页边注与第八章p.237注2共同闭合p.390的`Spagnuolo Pittore`局部指代到既有Crespi候选；Caldari仍只按姓氏登记。Smith收藏部分区分1762售藏、1770清单、1761遗嘱与George III图书馆谈判；清单和刊本未独立查阅，关于1762年前后藏品流转的两种假说未裁决，约1755与1756两种谈判日期按各自来源保留。附录四段和附录五开篇均已完成语义迁移。

本段新增5个候选、40条提及和9条原书statement。覆盖审计`s2_missing=[]`、`errors=[]`；832段中561 complete、118有理由排除、153 queued、0 partial。表面扫描的唯一提示仍是此前已判定异义的`modello`，不能视作召回率或独立语义验收。下一源段为附录p.392 `chp-19:19_CHP-19Appendix:l126-138`。


## 第十九章 p.392 当前结果

已处理Haskell关于Smith售藏争议的补充证据，以及Volpato 1766年来信与Smith 1768年通信开篇。售藏与后续购藏没有被强行裁决；Haskell对经济处境、英国市场选择和1762年后少见购画的判断均保留为推论。Moschini页图读法与OCR/引用 spelling 的差异留待后续身份对齐，外部引文与档案原件未独立查阅。Smith对Gennari绘画、素描的收购只是有条件意向，匿名collection owner与匿名通信者分立；原信续至p.393，p.392为reviewed/partial。

本段新增8个候选、43条提及（含候选表面回查补3条）、10条原书statement。全书机械审计`s2_missing=[]`、`errors=[]`；832段中561 complete、118有理由排除、152 queued、1 partial。第十九章9个已审段的候选表面回查只留下既有异义`modello`提示（油画初稿与马雕塑模型不同义），不表示语义验收或全书召回评估。下一源段为p.393 `chp-19:19_CHP-19Appendix:l140-155`，优先闭合Smith来信并续处理附录五。
## 第十九章 p.393 当前结果

p.393（PDF物理页8）已按页图与规范OCR处理，闭合p.392起始的Smith 1768年4月9日来信。记录Smith关于买家减少、购得若干画作与版画、重抄Gennari清单的书信陈述；购买不等于个人收藏，匿名通信者和收藏所有者仍未识别。另记录Haskell关于Zais、Smith售藏解释、1776年两场Christie's销售列表、1789年匿名拍卖和作品归属的叙述，并保留推测、引述与“据称来自Smith收藏”等限定。没有把两场1776销售的作品组分配到具体日期，也没有将14幅Canaletto景观并入第十章16 May目录所述的另14幅作品。Mr Murray与索引John Murray不合并；Farinelli不补全名；Fetti/Feti拼法关系留待S3。

页图校正包括Meschini→Moschini、(/)→(f)、¿20,000→£20,000、fists→lists、Maneschi→Marieschi。L155关于Smith藏书史的句子未完，续到p.394，因此p.393为reviewed/partial；p.392已转reviewed/complete。新增14个候选、54条提及和11条原书statement。审计 s2_missing=[]、errors=[]；候选表面扫描覆盖第十九章10个已读段，仅余此前判定异义的modello提示。下一源段为p.394 chp-19:19_CHP-19Appendix:l157-183。

## 第十九章 p.394 当前结果

p.394（PDF物理页9）闭合p.393关于Smith藏书史的跨页句，并完成附录六准备性笔记全文。新增14个候选、60条提及和12条statement；新增候选包括未定年Smith向Caraboli/Pompeati售书事件、合同档案定位、两种身后书目、缩写“C. Veneziano”、Naples/Paris学院问题和Terra-ferma等源内对象。Memmo笔记逐条记录为研究问题；仅将“音乐教师及铜版雕刻师不纳税”保留为笔记内断言，没有将其提升为经外部验证的制度事实。p.330内部回指保持Canaletto识别为有时间疑点的假设，“our Academy”的身份也留待S3。

页图校读已记录在S2 statements，未改规范OCR。全书机械审计`s2_missing=[]`、`errors=[]`；当前832段中564 complete、118有理由排除、150 queued、0 partial。第十九章候选表面扫描覆盖11段，唯一命中仍是此前已判为异义的`modello`。下一源段为p.395 `chp-19:19_CHP-19Appendix:l185-208`。

## 第十九章 p.395 当前结果

p.395（PDF物理页10）完成附录六准备性问题笔记及附录七Manfrin致Edwards信的S2处理，新增6个候选、34条提及和9条原书statement。保留Memmo的调查问题、阅读标记、Carlo VI免税说法的未核状态，以及Manfrin委托选画和保密条件；不推断实际选画、购买或入藏。信件链接到第十七章p.380的摘要和注6出处。L210–211的附加`Footnotes` OCR已核为p.386 Brandi收据首段的重复摘录，已链接至先前视觉转录及p.387续文并排除，不作为独立脚注重复登记。

第二版后记的L1仅为Markdown文件名标题，已排除；印本文题从L3起。当前全书机械审计为`s2_missing=[]`、`errors=[]`；832段中565 complete、120有理由排除、147 queued、0 partial。下一源段按行序为`chp-20:20_CHP-20Postscript:l3-12`，开始处理第二版后记正文。

## 第二版后记 p.396（2026-10-04）

p.396（PDF物理页1）新增14个候选、38条提及和9条statement。记录Haskell对Lavin关于圣彼得大教堂交叉空间演变的转引、对Bernini直接设计归属的限定，以及Hibbard和近期Borromini研究对该判断的影响；未把原书转引提升为独立查阅结果。页末引文续至p.397，因此该段先标`partial`。页图读数、限定语、脚注和候选均有来源行锚点。迁移后全账本为565 complete、120有理由排除、146 queued、1 partial；全表结构无错误。

## 第二版后记 p.397（2026-10-04）

p.397（PDF物理页2）新增27个候选、48条提及和14条statement，并闭合p.396的Lavin引文。记录法国赠予Cardinal Francesco Barberini的挂毯与后来颂扬Urban VIII教宗任期的挂毯为不同组；Harris对Sacchi风格及图像解释的修订、Sforza Pallavicino可能影响、古典／巴洛克论争，以及Ludovisi和Del Monte的后续研究均保留原书归属和限定。Ludovico藏画清单年份据页图读作1633；Agucchi开篇句续至p.398，p.397仍为`partial`。

写入后的核查发现迁移脚本漏写48条mention行，已按p.397登记段哈希和精确字面跨度补齐，并保留专用恢复副本。全表审计为`s2_missing=[]`、`errors=[]`；第20章候选表面扫描覆盖2段，未覆盖跨度0。当前全账本832段：566 complete、120有理由排除、145 queued、1 partial；候选10,874、提及25,024、statement 10,945。下一段为`chp-20:20_CHP-20Postscript:l26-36`（印刷页398）。


## 第二版后记p.398及第3章开篇（2026-10-04）

p.398（PDF物理页3）新增29个候选、62条提及、14条statement，闭合p.397 Agucchi早期生涯更新。Haskell称d’Onofrio把Frascati Villa Aldobrandini描述归于Agucchi；其关于约四十幅Bolognese画作的说法明确是“委托或购入”的可能解释，且无决定性证据。另记Agucchi为Cardinal Aldobrandini藏画编目、为Lodovico Carracci委托《Erminia and the Shepherds》、Battisti刊出相关书信和Whitfield分析programme。Cardinal Aldobrandini身份、画作群体、书信与inventory版本均不超出原文确定度。

同段续入Giambattista Marino收藏研究、Guido Bentivoglio为Cardinal Borghese艺术顾问／经营者的文献转述，以及Van Dyck Cardinal Guido Bentivoglio肖像经清洁后更换书中照片。图版目录将Plate 4a明确对应Bentivoglio肖像，避免把“the Cardinal”误指为Borghese。第3章开篇记录Jesuits与艺术研讨会、Wittkower论断及Haskell保留、耶稣会与世俗赞助人的冲突，以及Ackerman关于Gesù工程的Borgia／Jesuit与Farnese两阵营。Borgia括注指Jesuit camp，不指Borgia家族；Farnese阵营最终胜出是Ackerman引文中的说法，不提升为独立事实。

脚注1–7目前只登记正文回链；脚注全文段仍queued。页图确认脚注OCR L223应为“5 Viola”、L224为“Jaffé”。Ackerman引文闭合，但Haskell紧接的评价跨至p.399，故p.398为partial。审计无结构错误，候选表面扫描未发现遗漏提示；下一段`chp-20:20_CHP-20Postscript:l38-44`。

## 第二版后记p.399（2026-10-04）

p.399新增14个候选、52条提及和9条原书statement，闭合p.398的Haskell—Hibbard跨页评述。记录Buser对耶稣会艺术史论争的挑战、Jerome Nadal默想书版画及其对礼拜堂和Circignani殉道图像在意图/形式层面的影响、S. Vitale壁画拟古风格的作者推测；保留Haskell对Enggass研究的评价与其从沉默作出的推论，并登记Lavin所支持的对Lanckorońska—Gaulli图稿说法的修正。Haskell明确撤回Quietism解释。页图校正仅记于statement：`osan`→`of an`、`Dusseldorf`→`Düsseldorf`、`Sangue dt Cristo`→`Sangue di Cristo`。脚注1–3已回链至仍queued的脚注段，不宣称全文已审。首次候选表面扫描后补入3条漏记的Jesuits机构提及；最终本章4个已审段未覆盖跨度为0。全表无结构错误，现为569 complete、120 excluded、143 queued、0 partial；下一正文段为p.400 `l46-57`。

## 第二版后记p.400（2026-10-04）

p.400新增23个候选、54条提及和10条原书statement，覆盖规范段`chp-20:20_CHP-20Postscript:l46-57`。记录Enggass、Casale及Ottonelli—Pietro da Cortona论著版本、Hess与Chiesa Nuova、Cardinal Cesi书信和Oratorian赞助、Cassiano dal Pozzo家族藏品目录与西行日记，以及两幅不同的失佚肖像。对未出版档案、二手研究转述、可能解释、目录日期与藏家对应关系均保留来源层级和不确定性。

页图校读在statement保留`kra book`→`a book`及`autonomy-that`→`autonomy—that`；mention锚点仍逐字对应S0 OCR，并记录跨行的Bonadonna Russo与Velasquez提及。p.400末句在“the”处续至印刷页401，故p.400为`partial`；脚注1–8只回链到尚未处理的注释段，脚注9–10在本页正文文件L57登记。PDF页序核验后确认L59–67是Plate 65图版说明；真正p.401正文位于L81–96，开放句的`continues_in_segment`已按恢复流程修正。

## 第二版后记Plate 65（2026-10-04）

图版段新增4个候选、12条提及和3条statement。Plate 65a的图注说明Mola与Simonelli的双人讽刺像；Plate 65b说明Masucci描绘Mola为Pope Alexander VII作肖像。因S0对竖排图注的OCR逆序并拆分人名，提及保留OCR原始字面锚点，校正读法只记于statement；未推断被画肖像完成或现存。审计为`errors=[]`、`s2_missing=[]`；全书570 complete、120 excluded、141 queued、1 partial。下一段为Plate 66 `l69-70`；p.400末句的实际闭合段为p.401 `l81-96`。

## 第二版后记Plate 66

图注确认Baldassare Franceschini作品《Fame carrying the name of Louis XIV to the Temple of Immortality》，复用第7章作品候选和前置图版目录中的寓意人物/场景候选；新增5条提及和1条statement，没有新增候选。以第7章commissioning statement作跨段证据入口。表审计`errors=[]`、`s2_missing=[]`；全书571 complete、120 excluded、140 queued、1 partial。下一段为Plate 67 `l72-76`。

## 第二版后记Plate 67

图注将G. M. Crespi的作品描述为Jupiter被Cybele交给Corybantes喂养。复用p.228索引作品候选和先前登记的神话人物/群体；以第8章关于同一委托的叙述交叉回链，同时保留index候选与p.222作品候选的身份待S3核对。S0旋转OCR行在提及中保持字面锚点，校读写入statement。新增7条提及、1条statement、无新增候选；全库572 complete、120 excluded、139 queued、1 partial。

## 第二版后记Plate 68

图注a复用三幅Doges肖像组候选并连接Maggiotto；不与Pinelli收藏的168幅肖像组预先合并。图注b区分Tiepolo的作品构想与Leonardis的版画，Tiepolo和Leonardis均保持姓氏级待对齐，标题中的Maecenas、Arts、Augustus复用前置图版目录候选。新增4个候选、9条提及、4条statement；全书573 complete、120 excluded、138 queued、1 partial。下一段p.401 `l81-96`闭合p.400的开放句。


## 第二版后记印刷页401

p.401（PDF物理页10）完成，新增12个候选、35条提及和13条statement；闭合p.400 Cassiano日记句，区分两件Bernini归属有争议的胸像版本，补录Plate 65a双人讽刺像的制作人与朋友关系，以及第6章有关经济史、档案、Alexander VII日记和Clement IX赞助的更新。限定和引文层级保留；脚注1–8仍指向queued注释段L231–234。页面候选表面扫描提示的“Duke of Bracciano”已补精确mention，独立候选身份留待S3。

全表审计errors=[]、s2_missing=[]；全书575 complete、120 excluded、137 queued、0 partial，候选10,960、提及25,260、statement 11,000。第20章候选表面扫描覆盖10段，未覆盖提示0（仅为启发式检查）。下一段p.402：chp-20:20_CHP-20Postscript:l98-108。

## 第二版后记印刷页402

p.402（PDF物理页11）最终净增16个候选、38条提及和9条原书statement。记录Queen Christina在罗马的赞助及1966年斯德哥尔摩展览研究资源、Bellori/Previtali新版研究与Turner—Ferrante Carlo—Lanfranco的学术关联、第7章范围说明、西班牙赞助和那不勒斯总督研究更新、Mazarin在法国引入意大利巴洛克艺术的政策，以及Laurain-Portemer研究对Haskell旧表述的扩展。未具名的艺术家保留为通用term，未具名作品群不另造work实体；Turner报告的断言端点定为Bellori对Lanfranco的评论与Ferrante Carlo的文字关系。Louis XIV寻求意大利艺术人才及Alazard受委托绘画的句子停在“a picture commissioned”，未推断作品或委托人，标`reviewed/partial`并回链p.403 `l110-121`。脚注1–7回链queued注释段L235–238。

保留扫描页与S0均读作的“volume or studies and documents”，暂不将其改成推测性“of”；statement记录Christina’s拼写、Laurain-Portemer断行姓名及脚注5的OCR序号校正。表面定位器提示Italian art候选`cand-4131`在L106漏挂，已补精确提及并把候选加到对应statement；随后删除不可独立识别的未具名作品群候选和冗余提及，并将Italian Baroque artists改为一般术语候选。最终覆盖为575 complete、120有理由排除、136 queued、1 partial；候选10,976、提及25,298、statement 11,009，`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`。第20章表面扫描11段未覆盖跨度0（启发式检查）。下一段为p.403 `chp-20:20_CHP-20Postscript:l110-121`。

## 第二版后记印刷页403

p.403闭合p.402 Alazard受委托绘画的跨页句，复用Plate 66作品`cand-6888`，不推定未具名委托者；记录Versailles为Haskell第二版时点陈述、Rosenberg发表归属及Prince Liechtenstein、Levey/Croft-Murray、Isham、Florentine Seicento、Medici、Campbell与Borea等更新。脚注1–10仍链接queued注释段；Borea末句跨页到p.404，故p.403为`reviewed/partial`。新增28候选、63提及、13 statements，移除p.402占位候选`cand-10994`并重映射其提及/断言。审计`errors=[]`、`s2_missing=[]`；全书576 complete、120 excluded、135 queued、1 partial，候选11,003、提及25,361、statement 11,022。下一段为p.404 `chp-20:20_CHP-20Postscript:l123-135`。

## 第二版后记印刷页404

p.404接续并闭合p.403末句，记录Cardinal Leopoldo展览与研究、Cosimo III与Florentine文化研究、Grand Prince Ferdinand—Magnasco赞助、1705/1706展览史、Gabbiani研究更新、Del Rosso及Buonaccorsi材料。保留Haskell的转述、修正和推测限定；《埃涅阿斯纪画廊》对象边界及未具名画作不预先定论。脚注1–19链接queued注释段L244–253。新增35候选、62提及、10 statements；p.403、p.404均为`reviewed/complete`。审计`errors=[]`、`s2_missing=[]`；全书578 complete、120 excluded、134 queued、0 partial，候选11,038、提及25,423、statement 11,032。下一段p.405 `chp-20:20_CHP-20Postscript:l137-148`。

## 第二版后记印刷页405–406（2026-10-04）

### p.405：`chp-20:20_CHP-20Postscript:l137-148`

按`CHP-20Postscript.pdf`物理页14核读p.405。记录Stefano Conti委托Crespi的《Jupiter among the Corybantes》及另题《The Finding of Moses》、Davis对威尼斯贵族政治经济处境的研究、Pallucchini编乡间别墅装饰研究、Zenobio家族赞助、Puppi对Valmarana与Cordellina赞助的研究、Croft-Murray关于威尼斯画家赴英工作的综述、Daniels的Sebastiano Ricci专著、Shipley对Amigoni敌意的研究，以及Mazza为Owen McSwiny纪念画所作的文献综述和目录。

保留来源层级和不确定性：Haskell明确更正自己此前把Valmarana壁画委托归给Leonardo Valmarana的说法，改为Conte Giustino Valmarana；这不等于否认Leonardo可能是家族首领。Cordellina在Vicenza建造的宫殿无正式名称，和p.258候选是否同一仍待核。Riccis及其他赴英威尼斯画家作为群体保留，不拆分未知成员。页图校正L140 `lastjahase`→`last phase`、L143 `seeling`→`feeling`；只写入statement，不改S0。脚注1–9回链queued注释L254–258。

受控迁移`chp20_p405_s2_migration.py`默认dry-run，核对源/PDF/S0哈希、覆盖前态、候选自然键、精确mention跨度、statement原句、外键、脚注和续句链接；应用时留四表恢复副本`.bak-s2-chp20-p405-20261004`。p.405新增22个候选、61条提及和10条statement，状态为`reviewed/partial`，末句在“all those at”处续至p.406。

### p.406：`chp-20:20_CHP-20Postscript:l150-162`

按PDF物理页15核读并闭合p.405 Mazza目录句：目录涵盖当时识别出的原作与复制品，另有四件可能尚待发现，并取代Haskell 1963年的摘要清单；Haskell还说Mazza、自己和McSwiny同时代人都不理解这批画的准确含义。脚注1映射queued注释L259。

记录Ivanov关于法国当代对十八世纪威尼斯艺术兴趣的综述；Garas对Pellegrini Banque Royale装饰的研究及其“影响被高估”的判断；Garas关于Pellegrini在Vienna工作的讨论，以及其德国文章对Haskell第一版说法的更正：Pellegrini确实绘制了Dresden Zwinger壁画。将“已执行的壁画”与早先“拟议的房间装饰”候选分别保留，待S3/来源审查对齐。Bellucci在Vienna的年代范围（1692–1704）仍是Haskell转述的“可能”判断。Tessin只按姓氏登记：p.406索引候选指向Nicodemus Tessin the Younger，而Bjurström文章候选指向Carl Gustaf Tessin，暂不裁定。

另记录十八世纪俄罗斯宫廷吸引威尼斯艺术家的研究、1948年Valeriani专著和两篇后续文章；Haskell把“Catherine the Great本人购买《Banquet of Cleopatra》”改述为过度自信的假设，不将其反转为“她没有购买”。新建独立作品候选，并保留与p.298原购藏statement及复合候选`cand-9162`的关联。Vivian关于Joseph Smith“second collection”的研究仍未解决：数百幅画在1770年Smith去世时被记在其宫殿内；Haskell转述Vivian及自己的倾向性解释，认为1762年出售可能只涉及部分藏品、后来持有的画可能更早取得。该概率判断与Appendix 5 p.391–394交叉链接，不作已证实结论。

页图校读记录L153 `eighteenthcentury`→`eighteenth-century`，L156 `Bjurstrom`→`Bjurström`，L162 OCR对Appendix 5附近的杂字符恢复为印本“Appendix 5)—i.e.”。脚注1–9映射queued注释L259–263，注释内容仍未审。L162末尾仅出现“Jeffrey Daniels”姓名，相关句子续至p.407；录入其mention并保留与p.405 surname-only Daniels分开的候选，故p.406为`reviewed/partial`。

受控迁移`chp20_p406_s2_migration.py`核验源/PDF/段哈希、p.405 partial与p.406/p.407前态、候选自然键、精确跨度、statement引句、外键、脚注和续页映射；dry-run通过后写入并保留四表恢复副本`.bak-s2-chp20-p406-20261004`。新增13个候选、52条提及和12条statement；p.405转complete，p.406转partial。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；832段中579 complete、120 excluded、132 queued、1 partial；候选11,073、提及25,536、statement 11,054。第20章候选表面扫描覆盖15段，未覆盖跨度0（启发式提示，不等同召回率或语义验收）。下一段为p.407 `chp-20:20_CHP-20Postscript:l164-172`。


## 第二版后记印刷页407

p.407闭合p.406的Jeffrey Daniels续句，区分Daniels对Smith—Ricci大型绘画来源的解释与Haskell所报的相反意见；将Smith—Canaletto财务细节标为不清，并把Constable/Links对1740年代初罗马之行的怀疑与Haskell第一版旧说区分。记录Levey对1751年改动Smith旧藏威尼斯景观的研究、Barcham对Smith Palladian overdoors的研究、Binion与Haskell关于Schulenburg鉴赏力的争论，以及Rossi对“minor genres”和地方画派的解释；学者判断均保留来源归属和限定，不提升为无条件事实。p.407新增14候选、46提及、8 statements，脚注1–6映射queued注释L264–266；印刷注5/6与OCR序号冲突待复核。漏掉的第四处Canaletto人物提及已按字符732–741补至`cand-0498`，复扫未覆盖跨度0。全书581 complete、120 excluded、131 queued、0 partial；下一段p.408 `chp-20:20_CHP-20Postscript:l174-185`。


## 第二版后记印刷页408

p.408记录威尼斯启蒙研究更新、Haskell对术语范围的限定、Byam Shaw识别Le Blon及彩色印刷发明、McCormick目录中的Boscarati画作与Pisani游行、Olivato对画作来源/展示意图及Boscarati证词的转述、Zanetti 350幅讽刺画册的发现与赠予、以及Pinelli—Maggiotto总督肖像系列重新发现。保留学者转述和概率，不将争议画作并入旧组，也不推断未明示的“two figures”身份。校正三个可由页图确认的OCR读法；脚注1–7链接queued注释L267–270。p.408新增16候选、43提及、11 statements；Parker版画来源句续至p.409，故本段partial。审计`errors=[]`、`s2_missing=[]`；全书581 complete、120 excluded、130 queued、1 partial。下一段p.409 `chp-20:20_CHP-20Postscript:l187-199`。


## 第二版后记印刷页409

p.409新增22个候选、52条提及和12条statement，闭合p.408 Parker版画来源句（p.408 L185，续文p.409 L188）；p.409末句关于Santifaller及Algarotti墓画的归属继续至p.410 L201–202，故p.409为partial。页图校读、脚注映射、学者转述、身份及作品版本不确定性已记入过程记录。写入后audit_tables.py --summary为errors=[]、s2_missing=[]；832段中582 complete、120 excluded、129 queued、1 partial，候选11,125、提及25,677、statement 11,085。第20章候选表面扫描覆盖18段、未覆盖跨度0（仅启发式提示）。下一段p.410 chp-20:20_CHP-20Postscript:l201-209。


## 第二版后记印刷页409–410

p.410闭合p.409的Santifaller/Rode跨页句，保留Roland-Michel提出“更可能为意大利画家”的不同归属意见。p.410新增10个候选、27条提及和11条statement；p.409、p.410均为reviewed/complete。脚注1–5回链queued注释L276–280，其中印本注5在OCR中误作6。补录候选表面扫描发现的p.410 L209 Venice地名提及后，第20章启发式扫描覆盖19段、未覆盖跨度0。最终表审计errors=[]、s2_missing=[]；832段中584 complete、120 excluded、128 queued、0 partial，候选11,135、提及25,704、statement 11,096。后记剩余注释段L211–280尚待审读；之后处理书目与索引。


## 第二版后记脚注p.401（2026-10-04）

p.401注1–8（规范源L231–234）已按页图逐条转录并链接正文：Harris/de Andrés；Pierre du Colombier；Wittkower 1966；Radcliffe 1978与Sotheby’s 1979；Petrocchi 1970 p.158；Garms；Krautheimer与Jones；Weil。新增14候选、17提及、9条引文statement；注4拆为两项出版物引用，注7连接两条正文statement。校正de Andrés与Garms的OCR读法但保留S0；短引未给出的书名、版本和人物完整身份留待书目与S3。全表审计errors=[]、s2_missing=[]；11,157候选、25,788提及、11,143 statements。注释段已审至L234，L235–280仍待处理。

## 第二版后记脚注p.402（2026-10-04）

p.402注1–7（规范源L235–238）已逐条转录并连接正文：Christina of Sweden展览目录、Von Platen、Bellori 1976、Turner、Perez Sanchez、Wethey、Laurain-Portemer。新增2候选、9提及、7条引文statement，7个正文statement共承接8个marker链接。页图确认印本注5为Perez Sanchez，S0 L237将其误作6；校正只记于注释statement，S0不改。全表审计errors=[]、s2_missing=[]；11,159候选、25,797提及、11,150 statements。注释段已审至L238，下一段p.403注释L239–243。

## 第二版后记脚注p.403（2026-10-04）

p.403注1–10（L239–243）已转录并回链正文；注5印本为Croft-Murray，OCR误读为8，校正仅记于注释statement。新增3候选、16提及、10条引文statement。全表审计errors=[]、s2_missing=[]；11,162候选、25,813提及、11,160 statements，注释覆盖至L243。

## 第二版后记脚注p.404（2026-10-04）

p.404注1–19（L244–253）已转录并回链正文；注5 Chiarini de Anna和注6 Bandera的印本号分别被OCR误作6和8，保留S0并在注释statement记录校读。注10中的Rudolph 1971与1973分开建引用记录；注15与18暂复用同一1972引文候选，待书目核实。新增15候选、32提及、20条引文statement。全表审计errors=[]、s2_missing=[]；11,177候选、25,845提及、11,180 statements，注释覆盖至L253。下一段p.405注释L254–258。

p.405脚注1–9迁移：Merriman与Aikema各新建一个短引出版物候选，其余候选复用正文；Puppi 1968两条脚注保留各自页码定位。逐条核对印刷p.405 / PDF物理页14，印本脚注号与S0一致。新增2候选、13提及、9 statements；9个正文marker解除pending。全表审计errors=[]、s2_missing=[]；覆盖推进至L258。下一段p.406注释L259–263。

## 第二版后记脚注p.409（2026-10-04）

p.409脚注1–9（L271–275）逐条审读并回链：注4分为Haskell 1958与Levey 1960两项引文。新增1候选、16 mentions、10条citation statements，链接14条正文statement。页图校正Matina、印本注2及1960年份OCR；S0不改写。覆盖推进至L275，恢复备份与前置校验见process记录。全表审计errors=[]、s2_missing=[]；11,190候选、25,911 mentions、11,223 statements，584 complete、120 excluded、127 queued、1 partial。下一段p.410注释L276–280。

## 第二版后记脚注p.410（2026-10-04）

p.410脚注1–5（L276–280）逐条审读并回链正文；Previtali 1964与Haskell 1967的具体书目身份分别保留为独立未决候选，不凭作者/年份短引合并；另三项复用p.410正文已登记的作品/作者候选。新增2候选、8 mentions、5条citation statements，为7条正文statement完成回链。页图确认印本注5而OCR误作6，校读存于statement且S0原文保留。注释段转为reviewed/complete。全表审计errors=[]、s2_missing=[]；11,192候选、25,919 mentions、11,228 statements，覆盖585 complete、120 excluded、127 queued、0 partial。下一步转入书目33段与索引94段，并在交接前完成5份旧版`*_intro.md`范围核对。

## 书目L3–45：范围说明与手稿保管机构目录（2026-10-04）

书目intro旧转录与规范分节文件比对：旧稿1303行、规范版1306行；差异以OCR/排版为主。旧稿未单独列出Noemi Gabrieli一条，但规范版和PDF物理页13均有，未发现旧稿独有印本文本；该旧稿不另计S0来源。后4个`*_intro.md`仍待同样核对。

书目L1纯文件名标题排除；L3–45逐读为编纂范围说明和手稿保管机构目录，按PDF物理页1校正两栏地点对应。新增11候选、34 mentions、2条bibliography statements，未将目录条目处理为正文历史断言，也未将每项列表误写成具体手稿的已核馆藏事实。全表审计`errors=[]`、`s2_missing=[]`；候选11,203、mentions 25,953、statements 11,230，覆盖586 complete、121 excluded、125 queued、0 partial。下一段为书目L47–85（PDF物理页2）。

## 书目L47–85（PDF物理页2，印刷p.412）

记录29条出版物条目、书目字段和页图校读；复用21个已有archive候选，新增8个候选，添加32条mentions及31条bibliography/cross-reference statements。保留Arrighi-Landini 1755与1757版本候选分立；Aikema、D’Arcais短引依同书目条目补全书目信息，著作内容未独立查阅。首轮审计提示的claim自然键与coverage范围格式已按契约修复。最终`audit_tables.py --summary`为`errors=[]`、`s2_missing=[]`；全书候选11,211、mentions 25,985、statements 11,261；587 complete、121 excluded、124 queued、0 partial。下一段L87–127；尚有30个书目段和94个索引段。

## 书目L87–127（PDF物理页3，印刷p.413）

处理27条出版物条目，复用18个archive候选、新增9个，添加27条mentions和statements。页图确认S0漏录Barozzi—Berchet条目后的“2 vols., 1877-8.”，并拆分Bartolozzi与Bartsch被OCR合并的条目；校正其余作者名、刊名、页码和年份。卷级出版物候选保留供S3比对。审计`errors=[]`、`s2_missing=[]`；候选11,220、mentions 26,012、statements 11,288；588 complete、121 excluded、123 queued、0 partial。下一段L129–163；尚有29个书目段和94个索引段。

## 书目L129–163（PDF物理页4，印刷p.414）

处理27条S0可锚定的出版物条目，复用20个archive候选、新增7个；写入27条mentions和27条书目statement。另以独立页图补记S0整体漏掉的Bellori 1664年《Nota delli Musei…》条目，复用`cand-4805`但不伪造S0 mention；Beckford条目缺失的卷数/出版信息及OCR误字、Betcherman页码误读均按页图写入statement限定，S0不改。Berengo等旧短引保持待S3身份核对，Bertolotti文章与期刊卷候选分开。审计`errors=[]`、`s2_missing=[]`；候选11,227、mentions 26,039、statements 11,316；589 complete、121 excluded、122 queued、0 partial。下一段书目L165–205；尚余28个书目段和94个索引段。

## 书目L165–205（PDF物理页5，印刷p.415）

处理25条S0可锚定的出版物条目，复用21个archive候选、新增4个（`cand-11249`–`cand-11252`），写入25条mentions及25条书目statement；把已存在的短引候选补齐到本地书目给出的标题、年份、版本或页码，避免与原作内容已读混淆。PDF页图确认四处OCR错误：Bialostocki 1954页码、1960年份、Binion页码和Blunt《The Annunciation by Nicolas Poussin》题名分词；S0保持不变。全页没有发现整条书目项漏录。审计`errors=[]`、`s2_missing=[]`；候选11,231、mentions 26,064、statements 11,341；590 complete、121 excluded、121 queued、0 partial。下一段书目L207–241；剩余27个书目段和94个索引段。

## 书目L207–241（PDF物理页6，印刷p.416）

处理28条出版物，复用17个archive候选、新增11个（`cand-11253`–`cand-11263`），添加30条mentions和29条原书statement。末尾的`Bracciano, Duca di: See Paolo Giordano`作为内部书目交叉索引，指向现存两个person候选，不升级为正式人物关系或身份合并。页图校正Bonadonna Russo第二期刊卷号、两处Borroni姓氏、Boyer页码；S0 L239把Boyer 1934与Bozzòla 1948条目粘连，已按精确字符跨度分别记录。审计`errors=[]`、`s2_missing=[]`；候选11,242、mentions 26,094、statements 11,370；591 complete、121 excluded、120 queued、0 partial。下一段书目L243–293；剩余26个书目段和94个索引段。

## 书目L243–293（PDF物理页7，印刷p.417）

处理30项出版物，复用16个archive候选、新增14个，添加30条mentions与30条bibliography statements；Brugnoli合并书目中的两篇文章分开登记并共享书目信息。页图校正OCR年份、作者名、卷号、页码及错序/脱落刊名，S0不改；Brienne、Burney集合级引用与卷级候选保持分立。审计`errors=[]`、`s2_missing=[]`；候选11,256、mentions 26,124、statements 11,400；592 complete、121 excluded、119 queued、0 partial。下一段书目L295–334；剩余25个书目段和94个索引段。

## 书目L295–334（PDF物理页8，印刷p.418）

处理29项出版物，复用23个候选并新增6个，另处理Carandini作者交叉索引；共新增31条mentions和30条statements。页图拆开S0中Canova/Cantalamessa粘连条目，校正年份、拼名和OCR杂符；集合级出版物与卷级/作者候选分开留待S3。首次全表检查捕获的提及跨度重叠已修复，最终`errors=[]`、`s2_missing=[]`；候选11,262、mentions 26,155、statements 11,430；593 complete、121 excluded、118 queued、0 partial。下一段书目L336–374；剩余24个书目段和94个索引段。

## 书目L336–374（PDF物理页9，印刷p.419）

处理28项出版物，复用15个archive候选、新增13个，添加28条mentions和28条bibliography statements。将两篇Coggiola-Pittoni文章分开登记，并按印本拆分S0 L371粘连的两条Constable记录；Cicogna、Cochin与Conti的集合级条目保留独立候选供S3核对。页图校正页码、重音、罗马数字、扫描杂点和跨行断词；S0保持不变。审计`errors=[]`、`s2_missing=[]`；候选11,275、mentions 26,183、statements 11,458；594 complete、121 excluded、117 queued、0 partial。下一段书目L376–418；剩余23个书目段和94个索引段。

## 书目L376–418（PDF物理页10，印刷p.420）

逐读L377–418并按印本处理30条出版物记录；复用12个archive候选、新增18个（`cand-11297`–`cand-11314`），登记32条精确mention和31条statement。另将L398“Croft-Murray, E. → Blunt and Croft-Murray”记为书目交叉索引，链接到L210已有联合出版物`cand-9340`；作者候选身份继续留待S3。`Crespi—Mostra celebrativa...`只记标题和书目栏目，不推断作者，也未将书目项转为正文历史事实。

页图校正L378的误入引号、L384/L412的页边尾横、L404 `191z`、L407 `cinquantanni`、L415 `II Grechetto`和L416 `l6ème`；印本分别为无引号、无尾横、1913、cinquant’anni、Il Grechetto及16ème siècle。S0保持原文；本页未发现整条书目漏录。被引原作未独立查阅。

受控迁移脚本先dry-run后apply，四表恢复副本为`.bak-s2-chp21-bibliography-l376-418-20261007`。审计`s2_missing=[]`、`errors=[]`；11,293候选、26,215 mentions、11,489 statements；595 complete、121 excluded、116 queued、0 partial。下段L420–459。

## 书目L420–459（PDF物理页11，印刷p.421）

按页图审读31条出版物记录，复用24个archive候选，新增7个（`cand-11315`–`cand-11321`），添加31条mentions和31条bibliography statements。补全16个已有书目候选的题名/出版信息；De Dominici四卷集与Evelyn六卷编辑本和卷页定位候选分列，供S3对齐。Faldi书目1954与正文脚注1955的差异仍保留。

在statement限定中校正S0 OCR和扫描杂点，涉及L423、426、432–433、441、455、458–459；S0不改，本页未发现整条遗漏。被引作品未独立查阅。审计`errors=[]`、`s2_missing=[]`；候选11,300、mentions 26,246、statements 11,520；596 complete、121 excluded、115 queued、0 partial。下一段书目L461–496。

## 书目L461–496（PDF物理页12，印刷p.422）

按页图处理29条书目/展览记录，复用20个archive候选，新增9个（`cand-11322`–`cand-11330`），写入29条mention和29条statement；补全13个既有候选，Ferrari 1882复用先前短引候选。Fantuzzi、Félibien、Fisch—Bergin和Fleming书目记录与已有卷页或短引候选分开，供S3核对；Fontanella括号作者身份待定，Les Français à Rome两处场地描述并存待核。

校读L466、473、476、478、480、484–488的省略号、撇号、页码缩写、行首引号、作者拼写、两处粘连记录边界及年份；来源S0保持不变。本页未发现整条书目遗漏，被引作品未独立查阅。审计`errors=[]`、`s2_missing=[]`；候选11,309、mentions 26,275、statements 11,549；597 complete、121 excluded、114 queued、0 partial。下一段L498–536。

## 书目L498–536（PDF物理页13，印刷p.423）

按页图处理L499–536的30条S0书目记录：Friedlaender；Frommel；Gabbrielli；Gabrieli, Giuseppe；Galassi Paluzzi两项；Galilei；Gallo两项；Galluzzi；Gamba；Gar；Garas三项；Garms；Ghelli；[Gherardi, P. E.]；Gibbon；Gigli；Giglioli两项；Gilmartin；Giussani；Giustiniani；Goering；Goethe；Goldoni；Golzio两项。另登记页图可见的Gabrieli, Noemi一项。L498页码标记不算书目记录。

复用18个archive候选、新增13个（cand-11331–cand-11343，其中Noemi为页图项），补全14个已有候选；写入30条精确S0 mentions、30条bibliography_lists_publication statements和1条bibliography_page_image_addendum。保留Gabbrielli双年页码、Gabrieli/Galilei/Gallo/Gigli/Giustiniani/Goethe/Goldoni卷级定位与书目版记录的S3比对关系，不在S2合并。Gherardi方括号归属原样保留。

页图校读记录L499多余句点、L500 Frühwerk/Kardinal断词、L508 Strà、L509页码153、L517页码285、L518作者名和editor标点、L528多余引号、L535页码缩写；S0不改。Noemi的OCR文本已确认实际存在于规范书目文件L1304；当前statement仅以L503–504为相邻锚点，cand-11333来源锚在本已审段L503，后续L1301–1306处理中已为Noemi补精确mention，并将Gabrieli卷数续行链接到cand-11332；两处均交叉引用既有statement，不重复登记出版物。被引作品未独立查阅。

迁移后audit_tables为s2_missing=[]、errors=[]；候选11,322、mentions 26,305、book-statements 11,580；832段中598 complete、121有理由排除、113 queued、0 partial。下一段L538–575；尚余19个书目段和94个索引段。语义范围和质量仍须在全书S2交接审计中核对。

## 书目L538–575（PDF物理页14，印刷p.424）

处理28条书目记录，复用17个archive候选、新增11个（`cand-11344`–`cand-11354`），补全10个既有候选，写入28条mention和28条书目statement。拆分L553粘连的两篇Griseri文章；Grosley“3 vols., Londres 1764.”的OCR续行位于L1305，后续只补精确mention、不重复statement。页图校读Notatori、Griseri分界、official及若干作者重音/年代/页码，S0不改；未见整条漏录。迁移脚本默认dry-run并有来源/PDF/段哈希及外键检查，四表恢复副本已保存。审计`errors=[]`、`s2_missing=[]`；候选11,333、mentions 26,333、statements 11,608；599 complete、121 excluded、112 queued、0 partial。下一段L577–614；余18个书目段和94个索引段。语义质量仍待全书S2交接审计。

## 书目L577–614（PDF物理页15，印刷p.425）

处理26条记录，复用25个archive候选、新增`cand-11355`，写入26条mention和26条statement并更新24个既有候选。拆开OCR将Hibbard 1973文章页码与Hinks下一条书目记录粘连的末行；校读作者、刊名、重音、页码和条目边界，S0不改。修复既有`cand-4864`误合并Hibbard 1961文章与1971专著的问题，将对应正文引文mention/statement移至`cand-5163`，保留S3身份核对。受控迁移脚本完成来源/PDF哈希与外键校验，四表恢复副本已保存。审计`errors=[]`、`s2_missing=[]`；候选11,334、mentions 26,359、statements 11,634；600 complete、121 excluded、111 queued、0 partial。下一段L616–656；余17个书目段和94个索引段。语义质量仍待全书S2交接审计。

## 书目L616–656（PDF物理页16，印刷p.426）

页图核对31条出版物／展览记录和2条作者指引，排除页码标记；复用19个已有记录候选、更新12个，新增12个本页候选，并为指向L1276的Jaffé指引先建目标候选`cand-11368`。写入33条mention和33条statement。按页图拆分S0 L631粘连的两篇Incisa文章，校读年份、题名拼写、页码和两条`See`指引；S0不改。King’s Pictures按展览event记录。短引与全书目候选保持分开，交S3对齐；L1276的完整页图复核及书目statement仍待其队列段处理。恢复副本和受控迁移脚本已保存。审计`errors=[]`、`s2_missing=[]`；候选11,347、mentions 26,392、statements 11,667；601 complete、121 excluded、110 queued、0 partial。下一段L658–699；余16个书目段和94个索引段。语义质量仍待全书S2交接审计。

## 书目L658–699（PDF物理页17，印刷p.427）

处理30条出版物及2条“See also”指引；复用并补全24个archive候选，新增6个出版物候选和2个贡献者候选，写入32条mention、32条statement。页图校读8处OCR差异，并确认印本`Florentinsche`拼写；S0不改。Levey 1955页码差异与Lavagnino卷次不足均保留候选链接、留待S3；两条指引分别定位到已处理的Haskell—Levey及Gradenigo书目项。审计`errors=[]`、`s2_missing=[]`；候选11,355、mentions 26,424、statements 11,699；602 complete、121 excluded、109 queued、0 partial。下一段L701–754；余15个书目段和94个索引段。

## 书目L701–754：出版物条目（2026-10-07）

已对照规范来源L701–754与`CHP-21Bibliography.pdf`物理页18（印刷p.428）处理完本页。L701为页码标记；L702–754共33条印刷记录，含两篇作品的L750记录，拆分后登记34个出版物候选/statement。复用22个archive候选，新增`cand-11377`–`cand-11388`共12个；写入35条精确mention与34条`bibliography_lists_publication` statement。全行覆盖，候选外键与mentions字符偏移经受控脚本核验。

页图确认并记录：四条独立Longhi的`Paragone`刊名被OCR移至相邻前行；L713的`Fanfulla della Domenica`、L719的`Capitolium`、Mahon各期刊名、L739的`Le Gallerie Nazionali Italiane`均回接对应条目；L719–720 Loret/Lotti两条粘连项分开；Longo L712的尾随OCR引号删除于规范引句而保留在原OCR；Lorenzetti 1914日期首字校为数字1；Mahon年份`i960`校为1960；`cand-7057`的既有期刊字段从错误的`Burlington Magazine`改为印本`Art Bulletin`；Malamani Canova行尾短横确认在印本中但不作为日期；Male题名罗马数字OCR校为XVII；L750的Lucchesino断词与`Commentari`错序依页图拆为两篇文章、两个页码范围，第二篇标题以两个精确不重叠mention记录。

短引与版本身份均未越过S2裁定：Longo卷I、Lorenzetti 1917/1956、Mahon 1962、Malvasia 1678与1841版本、Malamani 1899多处短引、Mancini卷页定位、Marabottini 1954/1963、Marcellino p.18 locator均保持各自候选并挂接S3比较入口。被引出版物未在本段独立阅读。

迁移脚本默认dry-run，锁定S0、PDF和段落哈希及迁移前计数；apply前为候选、mentions、statements、coverage四表生成`.bak-s2-chp21-bibliography-l701-754-20261007`恢复副本。写入后`audit_tables.py --summary`：`s2_missing=[]`、`errors=[]`；全表11,367候选、26,459 mentions、11,733 statements；832段中603 complete、121 excluded、108 queued、0 partial。下一段书目L756–806；仍有14个书目段及94个索引段待处理。结构审计不替代语义接收。

## 书目L756–806（PDF物理页19，印刷p.429）

已逐条对照规范源与页图登记本页28条书目项：复用17个archive候选并补全12个，新建`cand-11389`–`cand-11399`共11个archive候选；写入28条mention及28条`bibliography_lists_publication` statement。候选、statement外键及所有mention字符偏移均经迁移脚本复核。`cand-7044`是前文脚注已识别的1961年展览目录，直接复用；全段不新建event对象。

页图校读包括：恢复L758、L762、L770/L772、L781和L793/L795移位的期刊名；校正Mariette、Abecedario、Marrini、Mazzotti、Mellino等OCR拼写，修复日期范围、Mazza期号和Meloni 1975期号/页码；按印本保持`Marrini`并与`cand-7926`分立。L789的Mazza题名续文与期刊顺序、L804–806 Mezzetti期刊行的跨行错序均依页图还原。L801 Memmoli与Merriman在OCR中粘连，使用互不重叠的精确mention及各自引句拆开。原OCR文本未改写。

Marcheix、Marrini、Marucelli、Matina、Matteoli及Mariette相关短引分别留有S3比对链接；本段不据书目题名裁决跨章同一性，也不声称读过被列出版物。受控脚本锁定来源、PDF、段落哈希与迁移前表规模；apply前保存四表恢复副本。写入后表审计`errors=[]`、`s2_missing=[]`；全表11,378候选、26,487 mentions、11,761 statements；604 complete、121 excluded、107 queued、0 partial。下一段L808–844；余13个书目段与94个索引段。

## 书目L808–844（PDF物理页20，印刷p.430）

规范源与页图核对本段26条出版物记录和1条作者交叉指引；L808仅为页码标记。复用21个archive候选并补全其中19个，新建5个archive候选与Molinier作者heading person候选1个；写入28条mention、26条出版物statement及1条`bibliography_author_cross_reference` statement。候选和提及外键、source quote、字符偏移和mention不重叠均通过段级检查。

页图确认L813的两条Miller文章在OCR中粘连，拆为1960年Crespi书信条目和1963/1964年Macerata长廊条目；1964 p.113定位单独链接既有`cand-7758`供S3。L820的Molinier作者指引暂连候选`cand-4828`及排队中的L861目标，状态保留未复核。Mitchell页码、Montaiglon机构名、Morassi条目和Morelli题名省略号依页图校读。版本同一性、页码差异与短引均不在S2提前裁决。

受控迁移锁定来源/PDF/段落指纹并在apply前备份四表。写入后`audit_tables.py --summary`为`errors=[]`、`s2_missing=[]`；当前11,384候选、26,515 mentions、11,788 statements；605 complete、121 excluded、106 queued。下一段书目L846–881，另有94个索引段待处理。

## 书目L846–881（PDF物理页21，印刷p.431）

页图确认本段28条出版物记录；复用并补全24个archive候选，新建4个archive候选，登记28条publication statement与28条精确mention。对照页图补记OCR缺失的Moroni词典卷数/年代，校正L849的Moschini/Meschini误读，拆分L876粘连的Nicodemi/Nisser两条。Molinier条目在L861找到，先前L820作者指引现标为目标已核对；个人身份仍未裁决。Northall既有p.438候选通过独立受控补记补全为书目所列的Travels through Italy。跨章作者/版本同一性问题仍保留供S3。

写表备份已保存；段级外键、source quote、mention偏移和非重叠检查通过。audit_tables.py --summary为errors=[]、s2_missing=[]；当前11,388候选、26,543 mentions、11,816 statements；606 complete、121 excluded、105 queued。下一段书目L883–926，索引仍有94段待处理。

## 书目L883–926（PDF物理页22，印刷p.432）

处理31条书目记录，复用28个archive候选并补全27个，新增3个`cand-11410`–`cand-11412`，写入31条mention和31条`bibliography_lists_publication` statement。页图校读L896页码、L898/L914卷次、L911罗马数字与标点、L917扫描标记及L924–925重音；保留L889印本短横、Panciroli无给名形式与Paoletti印本名`Ermalao`。Nuti/Pasquali、Ottonelli两版及Palomino定位保留S3比对，不裁定同一性。段级精确引句、mention字符偏移、候选外键和非重叠检查通过；全表`errors=[]`、`s2_missing=[]`。当前11,391候选、26,574 mentions、11,847 statements；607 complete、121 excluded、104 queued。下一段书目L928–983。

## 书目L928–983（PDF物理页23，印刷p.433）

处理32条书目记录，复用并补全23个既有archive候选，新增9个`cand-11413`–`cand-11421`，写入32条mention和32条`bibliography_lists_publication` statement。页图校读Paolo Giordano II诗集题名、Parker重音、Passeri年代、Perez Sanchez的España、Pesenti行首点、Pignatti年份及Pietro da Cortona展览短横；恢复Patrignani、两项Pinetti、Pirri和Pisano在OCR中错排的期刊名片段。Pascoli、Pastor、Peiresc、Pellegrini和Pollak的卷次／版本或引文定位均保留S3比较，不预先合并。32段引句、外键、字符偏移和完整L929–983覆盖通过核验；全表`errors=[]`、`s2_missing=[]`。当前11,400候选、26,606 mentions、11,879 statements；608 complete、121 excluded、103 queued。下一段书目L985–1020。

## 书目L985–1020（PDF物理页24，印刷p.434）

处理29条书目记录，复用24个archive候选并补全其中19个，新建5个cand-11422–cand-11426，写入29条mention和29条bibliography_lists_publication statement。页图校正Pöllnitz法文题名、Ponte和Poussin年份、Pope-Hennessy题名空格、Pozzo页码、Presenzini拼写、Procacci作者名、Prunières与Puliti OCR以及Prota-Giurleo扫描标记。印本对两项Puppi文章分别拼作Lionelli和Lionello，保留两个形式供S3。

p.405的Puppi note 5与p.434 L1019的pp.211–250相合，note 6与L1020的题名和pp.212–216相合；两条脚注和对应正文候选入口从共享暂定候选cand-11066分别改接cand-11425及cand-11426。note 5的年份差异（1968／1967–8）及作者身份仍留待后续判断。Previtali 1959书目候选与p.301未定短引不作强行匹配。

受控dry-run/apply脚本锁定来源、PDF、分段哈希和表前态，并为四表留恢复副本。段级检查确认29条引句、外键、mention偏移和L986–1020覆盖完整；目标mention无重叠。全表audit_tables.py --summary为errors=[]、s2_missing=[]。当前11,405候选、26,635 mentions、11,908 statements；609 complete、121 excluded、102 queued。下一段书目L1022–1057，余8个书目段及94个索引段。

## 书目L1022–1057（PDF物理页25，印刷p.435）

处理25条出版物记录和1条作者See also指引。复用22个既有archive候选，其中18个补全书目字段；更新2个人物候选中印本可确认的作者形式／书目信息；新增3个archive候选`cand-11427`–`cand-11429`；写入26条mention、25条`bibliography_lists_publication`及1条`bibliography_author_cross_reference` statement。页图校正Puyvelde、Radcliffe页码，Radicchio题名省略号，Richa的`istoriche`与十卷本，Ricci卷数标点，Rinaldis和Roberti页码，Rinehart卷次与Robertson作者缩写；作者方括号及未明小型上标标记予以保留或记录为不确定。

L1049的Rinehart “See also”明确指向已审L596–597的Haskell与Rinehart条目，并映射至既有出版物候选`cand-5658`；它记录为书目交叉指引，不扩写为新作者关系。Rinehart 1961文章的页52引文定位落在印本页35–59范围内，但文章与被引页均未独立阅读。Rivani的印本方括号不消除身份不确定；Radicchio、Rapparini、de Rinaldis、Roberti、Robertson等跨章候选只添加对齐比较入口，不在S2合并。三项新出版物为Puyvelde论文、Rinehart的Poussin论文及Robertson 1923年专著；Robertson既有p.318短引与该书不预先判作同一来源。

审计确认25条出版物逐行覆盖L1023–1057，另有L1049交叉指引；26条mention的引句、偏移与候选外键有效，26条statement的来源与候选外键有效，交叉指引目标段已完成。全表当前11,408候选、26,661 mentions、11,934 statements；832段中610 complete、121 excluded、101 queued、0 partial。下一书目段L1059–1100；余7个书目段和94个索引段。机械闭合不代替最终S2语义交接审查。

## 书目L1059–1100（PDF物理页26，印刷p.436）

处理26条出版物记录；复用并补全23个既有出版物archive候选，另更新Salvino人物候选`cand-7506`与Rudolph语境候选`cand-11036`，新建3个archive候选`cand-11430`–`cand-11432`。登记26条精准mention和26条`bibliography_lists_publication` statement；L1059页码行排除于条目覆盖，L1060–1100全覆盖。书目记录与本段页图校读和OCR订正详见process/stages.md。

p.403所引Pierre Rosenberg条目由本页题名、期刊与页码补全；p.404 Rudolph条目对应一个含1971、1972两部分的书目项，但它与另一个1973短引的身份关系未裁定。Röthlisberger 1958文章、Salvino Salvini目录和Schudt专著新建为独立archive候选；Seilern no.170短引不因同一书目姓氏自动认定同条。著录只反映书目陈述，被列出版物未在此段独立阅读。

受控dry-run/apply以来源、PDF、段落哈希和迁移前表计数为条件，写入前备份四表。写入后段级引句、mention偏移、外键与行覆盖通过脚本核对；全表`audit_tables.py --summary`为`errors=[]`、`s2_missing=[]`。当前11,411候选、26,687 mentions、11,960 statements；832段中611 complete、121 excluded、100 queued、0 partial。下一段书目L1102–1139；余6个书目段和94个索引段。机械闭合不替代全书S2语义交接审查。

## 书目L1102–1139（PDF物理页27，印刷p.437）

本段已完成S2：25条出版物入口逐行覆盖L1103–1139，L1102页码行不作实体内容。复用21个既有archive候选，其中13个补全书目信息；更新4个人物候选的书目来源约束；新建4个archive候选cand-11433–cand-11436；登记25条精确mention和25条bibliography_lists_publication statement。扫描校读、候选映射、每条出处字段与未决比较详见process/stages.md。

主要修正为Sforza卷号与页码、Shipley页码、Skippon范围、Strocchi姓名及期号、Stuffmann页码、Sweetman页码等OCR误识。Spini、Sensier、Shaftesbury 1914 edition和Stuffmann新建独立archive；不将Shaftesbury edition等同于抽象work，不由书目生成正式作者关系或作品内容断言。Selva、Sforza、Shipley、Silhouette、Sirén、Skippon、Smith、Sotheby’s、Spezzaferro、Spon、Strocchi、Strong和Tabacco的旧短引映射按证据强度更新或留S3比较；Sotheby’s机构与展览出版物分开。

Stuffmann条目按本书页图记录为pp.11–144；NGA与BnF著录对文章页码范围存在差异，已记录外部依据但不覆盖本书印字，也不声称已独立阅读该文。无关系表变更。

写表前为entity-candidates、mentions、book-statements和s2-coverage保存恢复副本。受控迁移脚本的dry-run与apply均通过；段级引句唯一性、字符偏移、候选外键、S3关联外键及行覆盖检查通过。全表机械审计为errors=[]、s2_missing=[]；当前11,415候选、26,712 mentions、11,985 statements，612段complete、121段有理由排除、99段queued、0段partial。下一段为L1141–1177，剩余5个书目段与94个索引段。机械通过不等于全书S2语义交接完成。

## 书目L1141–1177（PDF物理页28，印刷p.438）

处理30条书目记录：复用25个既有archive候选并补全其中20个，更新Tamizey人物候选的来源形式，新增cand-11437–cand-11441五个archive候选；登记30条mention和30条`bibliography_lists_publication` statement。页图确认OCR将L1158 Tessier/Teti两条粘连，已拆分为同一源行中的两个独立、非重叠提及。校正L1159的`L’Œil`、L1160的1960、L1167的10卷及L1170的Venezia–Roma；保留页图确认的`Inig`和`illustiator`印字。Tamizey遗嘱引文、Tesi introduction边界、Toesca作者差异等仍待S3比对；未新增正式关系。段级检查及全表审计通过，`errors=[]`、`s2_missing=[]`；当前11,420候选、26,742 mentions、12,015 statements，613 complete、121 excluded、98 queued。下一段L1179–1218，余4个书目段和94个索引段。

## 书目L1179–1218（PDF物理页29，印刷p.439）

处理28条出版物记录：复用20个既有archive候选并补全其中13个，更新2个人物来源说明，新增8个archive候选cand-11442–cand-11449；登记28条mention和28条`bibliography_lists_publication` statement。页图校正Vaes 1924页码、1931条目尾随杂符、Villot行首标记、Vitzthum页码及Vivian尾随标点。Vertue记录明确区分6卷和单独索引。Ubaldi/Vaes、Venturi多卷本及Viola旧短引的跨章候选关系留S3核对；未新增正式关系。段级校验和全表审计通过，`errors=[]`、`s2_missing=[]`；当前11,428候选、26,770 mentions、12,043 statements，614 complete、121 excluded、97 queued。下一段L1220–1259，余3个书目段和94个索引段。

## 书目L1220–1259（PDF物理页30，印刷p.440）

处理28条书目记录：补全21个既有archive候选和7个人物的作者来源形式，新增4个archive候选cand-11450–cand-11453；登记28条mention与28条`bibliography_lists_publication` statement。页图确认L1225两条Voss记录被OCR粘连，现已拆开；修正年份、作者缩写、页码和扫描标记。照录Walpole印本1726及Watson印本pp.11–177；Vivian 1963页码差异留S3比较。Wilhelm的L1259题名在L1262–1263续行，下一段补全。段级校验和全表审计通过，`errors=[]`、`s2_missing=[]`；当前11,432候选、26,798 mentions、12,071 statements，615 complete、121 excluded、96 queued。下一段L1261–1299，另余1个书目段和94个索引段。


## 书目L1261–1299（PDF物理页31，印刷p.441）

处理23条书目记录，并以独立续接statement补完p.440 L1259的Wilhelm条目；更新20个既有archive和4个人物候选，新增4个archive候选cand-11454–cand-11457，登记24条mention和24条statement。页图确认Wittkower 1958、Jaffé拼写及Zimmermann期刊行OCR订正；Wynne-Rosenberg地点读作à Padoue，与候选旧值Venezia存在差异，保留待S3/来源核对。Wright、Zannandreis及Girolamo Zanetti的跨章引用不合并，留S3比对；所列出版物均未独立阅读。全表审计errors=[]、s2_missing=[]；当前11,436候选、26,822 mentions、12,095 statements，616 complete、121 excluded、95 queued。下一段L1301–1306，余1个书目段和94个索引段。

## 书目末尾错位 OCR L1301–1306

L1301为结构性`Footnotes`标签；L1302–1306内7段错位OCR已分别链接到p.413、414、423、424、431先前登记的书目statement/页图增补，不新增出版物或正式关系。完成7条精确mention、7条交叉引用statement和7项候选说明更新；未独立查阅所列文献。首次审计发现source_line_ranges格式错误后，恢复写前四表副本，修正为`L1302-1306`并重新写入；最终`s2_missing=[]`、`errors=[]`。当前11,436候选、26,829 mentions、12,102 statements；617 complete、121 excluded、94 queued、0 partial。下一段为首个queued索引段`chp-22:22_CHP-22Index:l1-1`。

## 索引开篇页（PDF物理页1；页码未印，推定p.443）

S0 L9–56与L64–109是同一未印页码索引页的左右栏OCR片段，后接可见p.444。L3的`[Page 24]`与印本不符，作为OCR来源页标排除。对照整页PDF与S1 A.csv#0–66，完成65个开放词头候选的类型标注（9 institution、55 person、1 event），两条see-under别名链接到已有目标；子项和页码保持索引导航，不作为历史断言或关系。L64–109复核既有右栏映射，不新增候选、mention或statement。coverage说明补入`no_semantic_content`后总表通过`errors=[]`、`s2_missing=[]`。当时619 complete、123 excluded、90 queued；索引尚有2,781个开放未分类候选，下一段`chp-22:22_CHP-22Index:l113-168`。

## 索引p.444左栏及页标（S0 L111、L113–168）

L111是印刷页码444的OCR定位行，排除；L113–168为p.444左栏，从Algarotti续项至Arcadia Society。对照PDF和A.csv#67–115，为49个开放候选标注类型（45 person、2 place、1 term、1 institution）；“Anti-papal satire in reign of Alexander VII”按历史文学政治主题归term，Alticchiero与Altieri palace归place，Arcadia Society归institution。索引子项只是定位导航，无新增mention、statement或关系。当前620 complete、124 excluded、88 queued；索引剩余2,732个开放未分类候选，下一段`chp-22:22_CHP-22Index:l170-224`。审计`errors=[]`、`s2_missing=[]`。

## 索引p.444右栏与p.445页标

完成`chp-22:22_CHP-22Index:l170-224`：对照PDF物理页2印刷p.444右栏与A.csv#116–154、B.csv#1，标注40个候选主词头（23 person、17 term）；候选、段锚点和结构审计通过。索引子项和页码保持导航用途；B.csv#0的Baciccio see-under别名继续维持排除，不加入关系。未新增mentions、book statements或relations。接着将`chp-22:22_CHP-22Index:l226-227`的页标及运行页眉按PDF物理页3印刷p.445确认为无语义页面结构，标记`excluded/complete`。

迁移后全表为11,436候选、26,829 mentions、12,102 statements；832段中621 complete、125有理由排除、86 queued、0 partial。开放未分类索引候选2,692。接续段为`chp-22:22_CHP-22Index:l229-338`。该快照仍仅为机械覆盖状态，不代表S2语义交接审计完成。
## 索引p.445两栏及p.446页标

完成`chp-22:22_CHP-22Index:l229-338`：对照印刷p.445页图和B.csv#2–91，89个开放候选标注为80 person、6 term、1 family、2 place；`cand-0159` Baglioni collection因当前类型表未定义collection且索引证据不足，类型保留待决。OCR `Bainboccianti`及B.csv Niccolò编码问题按页图校读，来源不改写。该索引段未新增mentions、book statements或relations。随后将`chp-22:22_CHP-22Index:l340-340`按PDF物理页4可见p.446确认为页标并排除。

更新后全表为11,436候选、26,829 mentions、12,102 statements；832段中622 complete、126有理由排除、84 queued、0 partial。开放未分类索引候选2,603，其中包含上述类型待决项。下一段`chp-22:22_CHP-22Index:l342-396`。该状态不代表S2语义交接审计完成。

## 索引p.446左栏（S0 L342–396）

完成`chp-22:22_CHP-22Index:l342-396`：对照印刷p.446页图和B.csv#92–140，为49个开放候选标注47 person、1 term、1 institution。`Barnabotti`归社会阶层词term，`Benedictines`归宗教修会institution；子项和页码仍作为索引导航，未新增mentions、book statements或relations。迁移后11,436候选、26,829 mentions、12,102 statements；832段中623 complete、126有理由排除、83 queued、0 partial；开放未分类索引候选2,554。下一段`chp-22:22_CHP-22Index:l398-452`。审计`errors=[]`、`s2_missing=[]`不代表S2语义交接审计完成。


## 索引p.446右栏及p.447页标

完成`chp-22:22_CHP-22Index:l398-452`：对照印刷p.446页图和B.csv#141–180，40个Bernini人物词头/子项中39项补标`person`，cand-0319此前已标。页图/S0的主词头`Bentveugels`与`Bergamo`未见于A/B CSV主词头或index-entry映射，列为待解决的S1种子范围差异；不据正文候选推断同一性。随后将L454 `[Page 447]`按PDF物理页5确认为页标并排除。未新增mentions、book statements或relations。现11,436候选、26,829 mentions、12,102 statements；832段中624 complete、127 excluded、81 queued、0 partial；开放未分类索引候选2,515。下一段`chp-22:22_CHP-22Index:l456-510`。机械审计`errors=[]`、`s2_missing=[]`不代表语义交接审计完成。

## 索引p.447左栏、右栏与p.448页标

完成`chp-22:22_CHP-22Index:l456-510`及`l512-566`：按PDF物理页5的实际双栏分别核读B.csv#181–227与#228–274，新增类型46项和46项；左栏47项均为person，右栏分类为42 person、3 place、1 term，cand-0387 Bonfiglioli collection保留待分类。B.csv的Niccolò及其他重音乱码依页图校正知识候选，不改S1来源CSV。索引导航未新增mentions、book statements或relations。再按物理页6印刷p.448排除L568页标。全表为11,436候选、26,829 mentions、12,102 statements；832段中626 complete、128有理由排除、78 queued、0 partial；开放未分类索引候选2,423。Bentveugels、Bergamo两个S1索引种子映射仍待全书S2交接审计解决。下一段`chp-22:22_CHP-22Index:l570-624`。机械审计不等同语义验收。

## 索引p.448左右栏

完成`chp-22:22_CHP-22Index:l570-624`与`l626-680`：左栏B.csv#275–323补标46 person，保留1项已有person、1项place及1条excluded交叉指引；右栏C.csv#0–43补标42 person，保留cand-0504/0505两个有p.277注5证据的work候选。页图校读OCR疑点，不改写来源资产；索引导航未新增mentions、book statements或relations。全表11,436候选、26,829 mentions、12,102 statements；832段中628 complete、128有理由排除、76 queued、0 partial；开放未分类索引候选2,335。下一queued段为p.449页标`chp-22:22_CHP-22Index:l682-682`。

## 索引p.449页标

完成`chp-22:22_CHP-22Index:l682-682`：核对PDF物理页7印刷p.449，排除生成页标，不新增候选、mentions、statements或relations。全表11,436候选、26,829 mentions、12,102 statements；832段中628 complete、129有理由排除、75 queued、0 partial；开放未分类索引候选2,335。下一段`chp-22:22_CHP-22Index:l684-738`。

## 索引p.449左栏

完成`chp-22:22_CHP-22Index:l684-738`：逐项核对PDF物理页7左栏与C.csv#44–91，补标44 person、2 institution，保留cand-0531为place及cand-0556为work。OCR混入的右栏片段留给下一段L740–794；索引子项和页码不新建断言、mentions或relations。全表11,436候选、26,829 mentions、12,102 statements；832段中629 complete、129有理由排除、74 queued、0 partial；开放未分类索引候选2,289。下一段`chp-22:22_CHP-22Index:l740-794`。

## 索引p.449右栏

完成`chp-22:22_CHP-22Index:l740-794`：核读PDF物理页7右栏与C.csv#92–139，补标46 person、1 event、1 institution；印本校正C.csv#117–124的Niccolò乱码，未修改来源CSV。索引导航未新增候选、mentions、statements或relations。全表11,436候选、26,829 mentions、12,102 statements；832段中630 complete、129有理由排除、73 queued、0 partial；开放未分类索引候选2,241。下一段为p.450页标`chp-22:22_CHP-22Index:l796-796`。

## 索引p.450页标

完成`chp-22:22_CHP-22Index:l796-796`：核对PDF物理页8印刷p.450，排除生成页标，不新增候选、mentions、statements或relations。全表11,436候选、26,829 mentions、12,102 statements；832段中630 complete、130有理由排除、72 queued、0 partial；开放未分类索引候选2,241。下一段`chp-22:22_CHP-22Index:l798-852`。

## 索引p.450左栏

完成`chp-22:22_CHP-22Index:l798-852`：核读PDF物理页8左栏及C.csv#140–190，补标50 person、1 work；第2章p.58明确称`Chi soffre, speri`为verse drama。按印本校读C.csv#172–173重音乱码，来源文件未改。索引导航不新增mentions、book statements或relations。全表11,436候选、26,829 mentions、12,102 statements；832段中631 complete、130有理由排除、71 queued、0 partial；开放未分类索引候选2,190。下一段`chp-22:22_CHP-22Index:l854-908`。

## 索引p.450右栏

完成`chp-22:22_CHP-22Index:l854-908`：核读PDF物理页8右栏与C.csv#191–226，补标13 person、1 term、22 place；Churches栏目中C#204为主题词，C#205–226为具体教堂/建筑性空间。索引导航不新增候选、mentions、statements或relations。全表11,436候选、26,829 mentions、12,102 statements；832段中632 complete、130有理由排除、70 queued、0 partial；开放未分类索引候选2,154。下一段为p.451页标`chp-22:22_CHP-22Index:l910-911`。

## 索引p.451页标与页眉

完成`chp-22:22_CHP-22Index:l910-911`：核对PDF物理页9，排除L910生成页标和L911运行页眉，不新增候选、mentions、statements或relations。全表11,436候选、26,829 mentions、12,102 statements；832段中632 complete、131有理由排除、69 queued、0 partial；开放未分类索引候选2,154。下一段`chp-22:22_CHP-22Index:l913-1022`。

## 索引p.451两栏、p.452页标及左栏

完成`chp-22:22_CHP-22Index:l913-1022`：对照p.451页图和C.csv#227–321，89个开放候选标注25 person、42 place、22 work，保留6个see-under排除项；校读Clément及Città di Castello拼写。随后按PDF物理页10排除p.452页标L1024；完成左栏`l1026-1080`，对照C.csv#322–371标注49个开放候选（32 person、4 place、5 work、6 term、1 family、1 institution），保留cand-0834既有person类型。三个段落均未增加mentions、book statements或relations。现11,436候选、26,829 mentions、12,102 statements；832段中634 complete、132有理由排除、66 queued、0 partial；开放未分类索引候选2,016。下一段为右栏`chp-22:22_CHP-22Index:l1082-1136`。

## 索引p.452右栏

完成`chp-22:22_CHP-22Index:l1082-1136`：对照印刷p.452右栏与C.csv#372–420，49行中43个开放候选补标21 person、19 work、3 family；4条see-under继续excluded，保留C#407既有person。C#388 cand-0858异质收藏因taxonomy无对应类型仍待决；C#390 Longhi绘画/素描主题依据p.382已登记的作品组cand-10712/10714归work。按印本将cand-0868“Créqui, Duc de”校正重音，来源文件不改。未新增mentions、book statements或relations。当前11,436候选、26,829 mentions、12,102 statements；832段中635 complete、132有理由排除、65 queued、0 partial；开放未分类索引候选1,973。下一段为`chp-22:22_CHP-22Index:l1140-1194`。

## 索引p.453页标

完成页标`chp-22:22_CHP-22Index:l1138-1138`：页图确认印刷p.453，L1138是生成定位符，已记excluded/complete。未新增候选分类、mentions、book statements或relations。当前11,436候选、26,829 mentions、12,102 statements；832段中635 complete、133有理由排除、64 queued、0 partial。下一段为p.453左栏`chp-22:22_CHP-22Index:l1140-1194`。

## 索引p.453左栏

完成`chp-22:22_CHP-22Index:l1140-1194`：根据p.453页图与C.csv#421–431、D.csv#0–36标注48个候选（34 person、7 work、1 term、1 procedure、1 archive、2 place、2 family）。源段OCR夹入右栏残片，已据页图将其与另段L1196–1249的右栏完整转录分开，避免重复。索引导航未产生mentions、book statements或relations。当前候选11,436、mentions 26,829、statements 12,102；832段中636 complete、133有理由排除、63 queued、0 partial；开放未分类索引候选1,925。下一段为p.453右栏`chp-22:22_CHP-22Index:l1196-1249`。

## 索引p.453右栏

完成`chp-22:22_CHP-22Index:l1196-1249`：对照p.453右栏，将D.csv#37–66、E.csv#0–15共46行对应的45个开放候选标注24 person、9 work、2 place、1 institution、9 term，保留cand-0955既有place并校正印本拼写为`Düsseldorf`。Domenichino页中各子项按已有正文语境区分作品、人物和建筑空间；Dominicans归institution，英文赞助/旅游/启蒙主题及Dutch artists泛称归term。OCR片段已与L1140–1194左栏覆盖分开，避免重复。索引导航未新增mentions、book statements或relations。当前候选11,436、mentions 26,829、statements 12,102；832段中637 complete、133有理由排除、62 queued、0 partial；开放未分类索引候选1,880。下一段为p.454页标`chp-22:22_CHP-22Index:l1251-1251`。

## 索引p.454页标

完成页标`chp-22:22_CHP-22Index:l1251-1251`：页图确认物理页12印刷p.454，生成定位符已记excluded/complete。未更改候选或新增mentions、book statements、relations。当前832段中637 complete、134有理由排除、61 queued、0 partial。下一段为p.454左栏`chp-22:22_CHP-22Index:l1253-1307`。

## 索引p.454左栏

完成`chp-22:22_CHP-22Index:l1253-1307`：对照印刷p.454左栏E.csv#16–20、F.csv#0–44分类；46个开放候选标注31 person、5 work、7 place、1 term、1 family、1 event，保留cand-1014既有person，保留E#19 see-under排除项。Farsetti casts与paintings两项collection无对应taxonomy类型，维持待决。以书内证据将Bentivoglio判为family、Ferrerio的Vigilance和楼梯灰泥装饰判为work；p.364叙明的收藏出售事件归event。页图栏分与来源页段校验通过，索引导航未新增mentions、book statements或relations。当前候选11,436、mentions 26,829、statements 12,102；832段中638 complete、134有理由排除、60 queued、0 partial；开放未分类索引候选1,834。下一段为p.454右栏`chp-22:22_CHP-22Index:l1309-1363`。
