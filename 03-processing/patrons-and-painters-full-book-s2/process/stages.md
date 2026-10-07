# 全书语义处理（S2）过程



任务 ID：`patrons-and-painters-full-book-s2`。当前按用户指令推进本书从书前材料到索引的S2处理；832个规范段及交接审计完成前不交S3，也不启动S3–S6。



## 范围和证据



- 规范来源、PDF对应和重复OCR处理见[来源登记](../../../02-sources/source-registry.md#全书文本与-pdf-范围s0s2)。共23份PDF，包含书前、17章正文和5类书后材料。

- 当前S0 `segments.jsonl` 有832段，来自79个规范来源文件，其中42段为派生视觉转录。CHP-11/12与CHP-10同版扫描对应的44段重复OCR已在coverage标为excluded；该数与视觉转录段数不是同一口径。Markdown目录另有22个未登记校勘副本：17个整章OCR和5个书后旧版`*_intro.md`；书后5份旧版OCR均已完成范围比对，17份整章OCR的核对进度见本过程文件后续条目及当前结果。比较OCR不一致时以印本PDF页面核对，不静默略过独有内容。

- 正文和脚注均须完整阅读；跨页接续、叙述者/转述者、否定/推测/传闻、时间和语境限定照原文保留。必要图像回到PDF页检查。

- 索引只作定位与候选线索，书目条目只作来源/被引文献线索；两者本身不作为正文断言或事实支持。



## 执行顺序与复用



1. 书前材料：复用既有完整阅读记录；把其中提及、断言和关系候选迁入当前S2账本，逐项映射规范段。

2. 第一章：复用已完成的逐行语义阅读与S2账本，不重做无变化的判断。

3. 第2–5章：按章节编号依次处理规范分节，比较整章OCR的差异。

4. 第6章：保留并迁移既有全文阅读、候选及判断；对应规范段逐段核对，补足缺失提及和断言。

5. 第7–17章：按章节编号依次处理并比较整章OCR。

6. 结论、附录、第二版后记、书目、索引：按各自文本功能处理，比较平行OCR副本。

7. 全书交接：逐段核对覆盖、迁移状态、脚注、未映射候选外键、断言限定、关系候选及来源定位，形成可供S3使用的完整输入。



不得只以覆盖行数、候选数、索引命中数或脚本成功作为语义完成证据。每章的逐段分析、OCR/PDF校勘、提及/断言及未决项记录在同目录 `results/chp-*.md`；本文件只维护任务方法、执行顺序和有影响的过程判断。





## 本轮书前材料迁移记录（2026-09-26）



- 00_04_Contents 的L1与00_05_List_of_Plates的L1是OCR分节文件自动生成的标题，按格式元数据排除；两行不作为印本内容。

- 00_04_Contents的L3是目录标题，00_05_List_of_Plates的L3–30列章节标题和页码；均保留为书籍结构元数据，不转成实体提及或历史断言。

- 第一版序言00_03_Preface_1st_Ed的L19–29复用章前完整逐行解读，迁入34条有精确跨度的提及和24条带原文限定的断言。人物、机构与地点均复用既有accepted-KU候选；匿名友人及未具名职员仍作为群体陈述，不造人物端点。Elizabeth Oma按OCR跨度映射至既有Elizabeth Orna候选，并保留PDF校读更正；末尾签署地点和日期作为序言署记，不误作出版日期。

- 当前书前材料28段中20段迁移完成、8段有理由排除、0段pending。详细语义判断和原句仍见[章前结果](../../patrons-and-painters-front-matter/results/stages.md)。



- `00_05_List_of_Plates` L67–68 对应印刷页xiii的页码标识和“plate following page”栏标题，按书籍版面元数据处理；没有实体提及或历史断言，覆盖记为 `reviewed/complete`，理由保存在 `s2-coverage.csv`。



### 图版清单 L70–81 第一批迁移（2026-09-26）



- 规范段 `front-matter:00_05_List_of_Plates:l70-81` 已迁入图版17a–18b，共18条精确跨度提及、12条断言；复用既有作品／人物／机构候选，仅新增标题身份未定的 `cand-4143`（Duke of Rutland）。该段覆盖为 `reviewed/partial`，图版19a–28b仍待迁移。

- 图版17a的“104”经 `CHP-0Cover.pdf` 印刷页xiii（物理PDF第10页）确认属于“following page”栏，不能并入 Museum Boymans—van Beuningen 名称；OCR断行和页码污染均留在原引句中并加校勘说明。图版18b复用已有《婚姻》候选，但保留短题名的版本未决状态；Rutland按爵号开放候选，不强并至具体公爵。图注中的地点／馆藏只记录为本版关联。



### 图版清单图版 I–XVI 迁移（2026-09-26）



- 在规范段 `front-matter:00_05_List_of_Plates:l32-65` 中，将图版 I–XVI 的创作者、作品／空间、题名人物及图注中的机构／地点标签迁入账本，共100条精确跨度提及和62条断言；复用已有候选并新增9个开放候选。候选外键均可回溯至已接收对象或本段原文锚点。

- 保留图版2a的 `Attributed to Caravaggio` 限定；图版2a与2b的肖像对象分开，2b中的 Maffeo Barberini 与 Pope Urban VIII 归于既有同一人物候选；图版3b的 Duke of Northumberland 身份未定；图版4a的 `Pitti` 保留为原书简称，馆／宫粒度待决；图版5不并入已有 Leoni 肖像或任何一件 Bernini 胸像。图版6的1630限定为景观年代；图版7及10–11的神话／圣经标题不被当作历史事件证据；Joseph（son of Jacob）与第一章的 St Joseph 分开。

- 图版8、16分别登记为礼拜堂和教堂内部空间，不误作绘画；图版9区分卷首图、承载书、作者、出版信息和宫殿图像；图版15保留 modello 与壁画的对象边界，Galleria Nazionale 机构身份待核。括号中的收藏及地点仅记录为本版图注关联，不推断委托、法律所有权或当前保管。

- 对照 `CHP-0Cover.pdf` 印刷页xii（物理PDF第9页）：确认图版11a编号；登记L46“ofVilla”漏空格及L52括号被OCR读作花括号，保留原OCR引句并记录图像校勘。图版后随页的24、40、56、72作为导航页码，不转为对象或日期。覆盖现为 `reviewed/complete`；审计无结构错误，100条提及跨度和62条断言引句均通过核对。



### 图版清单 L70–81 第二批迁移（2026-09-26）



- 完成图版19a–28b，并将规范段 `front-matter:00_05_List_of_Plates:l70-81` 从partial更新为 `reviewed/complete`。本段17a–28b累计94条精确跨度提及、71条带原文限定的断言；本批新增15个开放候选（`cand-4144`–`cand-4158`），其余端点复用既有候选。提及偏移依据规范段L70–81实际拼接文本计算并与原句逐字复核。

- P19b的短称Claude暂映射到索引主候选Claude Lorrain（`cand-0767`），留给S3做全局身份判断；Robert A. Waller Fund只作为未定类型的馆藏／基金标签，不推为赞助人。P20明确区分Camillo Massimi肖像对象与Ralph Bankes收藏者；Ralph Bankes两个已有同名知识元不凭此图注选定。Duke of Beaufort仅保留爵号候选。

- P21a将Dominic、Catherine保留为图像题名人物，不补圣人具体身份；S. Sabina与Rome作为印本位置。P21b的Madonna and Child与P21a分开，Galleria Nazionale复用未定机构标签。P22a不把“artist with friends”升级为已证自画像，也不为匿名朋友造人物；P22b只记录题名中的Masaniello，不把图注当作起义史实证据。

- P23a的Incisa della Rocchetta保留为类型／角色待定标签，并与第一章脚注中的同名书目作者候选分开；P23b将Regulus作为题名人物，Williams Fund只记未定基金标签，不推成赞助关系。P24的Fortune留在作品题名内，不另造拟人实体；Duke of Beaufort身份待决。P25保留寓意作品边界。

- P26a的“his Gallery”不命名为Palais Mazarin；P26b单列Bibliothèque Nationale与former Palais Mazarin语境，并以顶画局部记录Romulus、Remus，不扩大为整幅天花／整体装饰。P27a区分Charles I肖像对象与Miss Daphne Ionides收藏者；P27b记录Louis XIV与Versailles的图注关联。P28a只记Cleopatra题名人物；P28b把舞台设计与歌剧 `La Monarchia Latina Trionfante` 分作两个作品候选，保留Vienna 1678但不臆定年份所指。

- 对照 `CHP-0Cover.pdf` 印刷页xiii（物理PDF第10页）：所有19a–28b图注及其馆藏／地点按版面核读。OCR行74的“126”对应印本“136”，两者均在独立“FOLLOWING PAGE”栏而不属于21a／21b图注；25旁“184”同样为分页导航。引文原样保留OCR转录，校正只记入断言限定与覆盖说明。

- 当前表审计通过：本批写入15个候选、76条提及和59条断言；提及字符跨度、断言原文及行号、候选外键均通过机械检查。语义是否召回全部有意义对象仍须随整书S2人工复核；S3身份决定尚未执行。



### 图版清单 L83–118 迁移（2026-09-27）



- 完成图版29–44，并将规范段 `front-matter:00_05_List_of_Plates:l83-118` 更新为 `reviewed/complete`。新增17个开放候选、134条精确跨度提及和109条带证据锚点的原书断言；该批的候选、提及和断言均已通过当前外键及原文跨度审计。

- P29只将 Her Majesty the Queen 记录为复制许可说明中的未识别人物，不推断为作品委托人。P30a保留 Jerome Bankes 与收藏者 Ralph Bankes 的角色区别及同名候选未决；P31a只保留未识别的 Earl of Ilchester 爵号，P31b将Thomas Isham与Gyles Isham区分，`Bt`只解释为爵位缩写。收藏、馆藏和地点图注均不扩写成委托、所有权或现藏断言。

- 题名中的Silenus、Hercules、Dido、Aeneas、Herod、Europa、Pan、Syrinx、Venus、Adonis、Zechariah和Neptune保留为图像／题名指称，不将题名当作历史事件证据；Herod身份、The Painter’s Family成员及Piovano Arlotto等仍为开放候选。Tiepolo图版42a中的拟人化Venice与括注中的Venice城市分别映射，42b另行记录题名中的寓意对象。

- 对照 `CHP-0Cover.pdf` 印刷页xiv（物理PDF第11页）：确认200、216、232、248属于独立的following-page栏，不属于相邻图注；校读 L91 Lamport Hall 的断行／句点、L92 Naples 后OCR多余撇号、L112图版41a前逗号，以及L116–117 Ca’ Rezzonico 的跨行和OCR撇号遗漏。来源OCR文本保留原样，校勘与语义判断通过断言限定记录。

- 本批完成后，书前材料28段中13段迁移完成、8段有理由排除、7段图版清单仍待迁移；全书账本为40段reviewed且迁移完成、7段reviewed但迁移未完成、11段excluded、732段queued。全书S2仍未达到S3交接条件。



### 图版清单 L120–121 导航段处理（2026-09-27）



- 规范段 `front-matter:00_05_List_of_Plates:l120-121` 只含印刷页码 xv 与 “plate following page” 栏目标题，是版面导航元数据，不含实体提及或原书断言；将其迁移状态由 pending 更新为 complete。



### 图版清单 L123–138 迁移（2026-09-27）



- 图版45–60已迁入规范段 `front-matter:00_05_List_of_Plates:l123-138`：复用已有作品、创作者、人物、机构和地点候选，新增8个开放候选，写入125条精确跨度提及和102条原书断言。全段覆盖更新为 `reviewed/complete`。

- 主要语义边界：图版45的Venice是标题中的寓意对象，与城市地点分开；图版46不补 Pierre Motteux 未具名家人；图版48a、48b的“from”和图版55b的“engraved”角色原样保留；图版49a的Crown Prince身份未决；图版50的顶画局部与所指整幅壁画分开；图版52b只记三位并列署名者和纪念对象，不把寓意墓断为真实建筑；图版53a把Castello Sforzesco记作建筑地点，不代填其馆藏机构；图版57a为Albrizzi出版者和画像对象创建两个未对齐候选；图版60区分版画、被描绘墓葬和被纪念者，悼念者匿名。

- 对照 `CHP-0Cover.pdf` 印刷页xv（物理PDF第12页）：264、280、312、344均在独立的FOLLOWING PAGE栏。OCR将264插入North Carolina之间、将printed “of”识作“os”、漏掉Bayerischen Staatsgemäldesammlungen与Würzburg的变音符，并把Gerusalemme Liberata断为“Liber ata”；来源OCR原样保留，校勘记录随对应断言保存。

- 当前表结构审计0错误；`tests/test_audit_tables.py` 与 `tests/test_export_dataset.py` 共17项通过。该机械检查不替代全书S2语义范围复核。



### 图版清单 L140–172 迁移（2026-09-27）



- 将图版61a–68b及“Photographic Sources”名单迁入规范段 `front-matter:00_05_List_of_Plates:l140-172`：新增18个开放候选、97条精确跨度提及和145条带来源行锚点的原书断言，覆盖状态更新为 `reviewed/complete`。表审计确认候选外键、原文跨度、断言引句与来源行范围有效。

- 图版61a、61b分别保留科涅克—杰与维多利亚国家美术馆版本；Felton Bequest作为图注来源/收藏标签。图版62、63的OCR `Prato`按印本校为`Prà`，但保留原始OCR引句；62是帕多瓦景观，63是整治方案，不推作已经建成。图版64记录John Strange别墅、Paese/Treviso场景与未具名伦敦私人收藏，OCR中的`ofjohn`按PDF记录为`of John`。

- 图版65a记录Mola与Simonelli的共同署名及被描绘角色，并将Vitale Bloch限为旧藏；65b保留Masucci创作、画中Mola为Alexander VII作像的图像叙述，不当作已证历史事件。图版66将Fame、Louis XIV与Temple of Immortality按寓意题名记录，后者不当作现实地点；67的Jupiter、Cybele、Corybantes只作神话图像角色。图版68a另建“三幅总督肖像”候选；它与既有168幅Maggiotto肖像组（`cand-3352`）关系未决，不合并也不拆造三件具名作品。68b明确区分Tiepolo原设计与Leonardis刻印。

- 摄影来源名单新增13个位置标签及80条明确供片图版记录；`Royal Academy`与National Gallery of Victoria对61b的图注/供片角色分开。OCR `rob`校为10b、`ioa`校为10a、`Malborough`校为Marlborough、`Steam and Son`校为Stearn and Son、`Wiirzburg`校为Würzburg；`Docu`后的软连字符及跨行保留原引句并对照PDF。`National Gallery`分支身份留待S3；复合署名Mansell-Alinari与Mansell-Anderson不拆分。图版55的供片记录没有a/b标识，保留图版级待决端点。摄影供片不推作原作创作、委托、所有权或现藏关系；“未另注明由各馆提供”的文字只记为通用规则，不复制到每件作品。

- PDF校读使用`CHP-0Cover.pdf`印刷页xvi（物理PDF第13页）：360和400均属独立的`FOLLOWING PAGE`栏。全书账本更新为44段迁移完成、3段待迁移、11段有理由排除、732段queued；当前共1,361条提及、783条断言。



### 第二版导言 L174–185 迁移（2026-09-27）



- 复用章前逐行阅读FM-S31–34，将规范段 `front-matter:00_05_List_of_Plates:l174-185` 迁入：新增6个开放候选（`cand-4202`–`cand-4207`）、40条精确跨度提及和22条带行号的原书断言；覆盖由 `reviewed/pending` 更新为 `reviewed/complete`。本段迁入后总账为44段完成、3段待迁移、11段排除、732段排队，提及1,361条、断言783条。

- 将Haskell的叙述、Honour评论、Waterhouse对Haskell的批评、Waterhouse转引Wittkower论点分层记录。群体迁居不把Naples/Tuscany分别配给Conca、Giaquinto、Batoni；P. G. Piola、Viani、Lazzarini、Guido和Crespi保持身份未决；“未为罗马主要教堂和宫殿创作重要作品／只以游客身份访问”保留为群体析取，不分配到Crespi或Solimena。Conca优劣比较保留为Haskell的判断，1707及七年后首项公共委托只记录为原书陈述。

- Innocent XI和Clement XI的两条引文保留为引述判断，脚注3、4的来源名不提前写入本段；脚注1–4及其书目锚点由下一规范段L187–188迁移。对照`CHP-0Cover.pdf`物理第14页，确认OCR `Clement XI (17001721)` 漏掉连接号，印本为1700–1721；引文原文仍精确引用S0文本，校读差异写入断言限定。L185末句只到“Rome as a centre of”，按不完整句处理，待L190–196续读，不补造断言。





### 第二版导言脚注 L187–188 迁移（2026-09-27）



- 完成规范段 `front-matter:00_05_List_of_Plates:l187-188`，新增2个开放候选（`cand-4208`、`cand-4209`）、7条精确跨度提及和4条引文定位断言；覆盖更新为 `reviewed/complete`。

- 将脚注1–4分别链接到Apollo 1963年12月Hugh Honour书评、Waterhouse 1971年评论、Conforti对Innocent XI的评述及Pastor对Clement XI的评述。引文仅作前文判断的来源定位，不扩写成独立历史事实；Conforti的引文责任者及书目片段保持身份待决。



### 第二版导言续文 L190–196 迁移（2026-09-27）



- 完成规范段 `front-matter:00_05_List_of_Plates:l190-196`，新增1个开放候选（`cand-4210`）、24条精确跨度提及和13条带行号的原书断言；覆盖更新为 `reviewed/complete`。

- 本段承接L185末句。对照 `CHP-0Cover.pdf` 物理第15页确认印刷页眉为xviii；S0行L190的`[Page 1708]`是错误导航标记。French Academy主管Poerson的信件作为Haskell转引保存；“Mgr”收信人未明，编辑插入语和Haskell的推断均保留限定。区分Clement XI、San Clemente教堂及其守护圣人，不把七位列名艺术家分配到具体作品。



### 第二版导言脚注 L198 迁移（2026-09-27）



- 完成规范段 `front-matter:00_05_List_of_Plates:l198-198`，新增4条精确跨度提及和2条引文定位断言；覆盖更新为 `reviewed/complete`。

- 将Montaiglon卷III与Gilmartin的脚注线索映射到前文Poerson书信和San Clemente装饰事件的引文链，复用已有候选。书前材料28段现为20段迁移完成、8段有理由排除、0段pending；全书账本共47段迁移完成、11段排除、732段queued，含1,396条提及和802条原书断言。上述总量是结构状态，不能替代全书语义复核。





### 第2章第II节 L10–18 迁移（2026-09-27）



- 完成规范段 `chp-2:02_CHP-2_sec_ii:l10-18`，写入5个开放候选、35条精确跨度提及和21条原书断言，覆盖状态更新为 `reviewed/complete`。提及、断言原句与行锚通过表审计。

- 旧封建家族的群体性社会角色未分配到单一Colonna或Orsini家族。Anna Colonna被选为Taddeo新娘不等于婚姻完成；其父仅称Contestabile，身份未猜定。威尼斯使节群体与单一匿名使节分开保留；使节对领地收入和罗马自给能力的说法维持归属与评价语气。

- 保留Haskell对教廷官职售卖、Urban VIII建筑支出、罗马美化、欧洲国家体系与罗马声望关系的叙述/推断；Pietro Contarini的1623年引语、脚注5所指Gregory XIII的建筑论述分别归入不同发言层。Catholic world作为概念与Catholic Church机构区分；Papal States不与Rome城市合并。

- 对照 `CHP-2.pdf` 印刷页32–33（物理第13–14页）核读OCR；脚注1–5标记留待后续注释段迁入交叉链接。L18句未完并延续到下一段L20–28，当前只锚定并保留片段，不提前并入未读文本。

- 迁移后全书S2账本为49段reviewed且迁移完成、11段有理由排除、730段queued；共1,458条提及、842条原书断言。机械审计仅检查结构和锚点，不代表整书S2语义完成。





### 第2章第II节 L20–28 迁移（2026-09-27）



- 完成规范段 `chp-2:02_CHP-2_sec_ii:l20-28`，新增7个开放候选、33条精确跨度提及和16条原书断言；覆盖为 `reviewed/complete`。前段L18的patronage scope片段已与本段L21续句建立双向过程关联。

- 复用既有Henri IV、白山战役、Richelieu、Accademia dei Lincei、Galileo、Rome、Italy、Baroque、Counter Reformation及Renaissance候选；新建法国和哈布斯堡帝国、Papacy、Roman Court及三项文本概念候选。France的政治联盟与法国文化修饰语分别保留；Papacy、Roman Court、Urban VIII及Rome不合并。

- 逐层保存Haskell的历史解释、对Urban VIII的推断、匿名French disbeliever的引语；印刷脚注3识别其为Gabriel Naudé并注明转引自Pintard。脚注1与2也已标记待迁移交叉链接，未将其注释材料提前混入正文段。

- 对照 `CHP-2.pdf` 印刷页33（物理第14页）核读。OCR `tire attention`在印本为`the attention`，S2原引句保留OCR原貌并在限定中说明校勘；Hapsburg拼写与印本一致。原书中的1621日期仅作为Haskell的陈述记录。

- 当前全书S2账本为50段reviewed且迁移完成、11段有理由排除、729段queued；共1,492条提及、858条原书断言。章节仍未完成，整章OCR/PDF对照待后续收口。



### 第2章第II节 L30–40 迁移（2026-09-27）



- 完成规范段 `chp-2:02_CHP-2_sec_ii:l30-40`：新增9个开放候选（`cand-4228`–`cand-4236`）、42条精确跨度提及和20条原书断言；覆盖为 `reviewed/complete`。复用当前已接收人物与地点候选，并将 Carlo Maderno 绑定到原书索引中页码包含34的候选 `cand-1478`。

- 候选新增 Barberini style、Passeri所称Bolognese艺术群体、Urban偏好的Tuscan artists群体、Peter the Apostle、圣彼得大殿立面及穹顶、巴尔达基诺作品、被称作“supposed tomb”的地点和Pantheon。明确拆分圣彼得人物、大殿建筑、构件、作品及地点；未具名父母、匿名批评者、早期墓葬和临时替代罩篷未被强行命名。Urban VIII、Bernini、Paul V、Michelangelo、Passeri、Baldinucci、Florence、Naples、Rome等复用现有候选。

- 将Passeri回顾性评语、Haskell转述的Bernini父母出身、作者关于赞助偏好的判断、据Baldinucci转引且被Haskell称可能为伪托的Urban赞语、匿名观察者对立面铭刻的批评分别分层。脚注1–5仍需等注释S0段迁入后交叉链接；作品工程日期按原文保存，不从“九年后”推算日历年份。

- 对照 `CHP-2.pdf` 印刷页34（物理第15页）核读正文与页下注。OCR `Cavalière`在印本为`Cavaliere`、`lais`为`his`，且`problem'was`中的撇号为OCR误入；原引句保留S0文本，校勘置于断言限定。所有新增外键、提及字符跨度、断言引句与来源行范围预检通过。首次总审计发现4个候选来源定位用了不符合字段契约的行范围，已修为单行定位；复审后结构审计0错误。

- 本段迁移后全书S2账本为51段reviewed且迁移完成、12段有理由排除、727段queued；共1,534条提及、878条原书断言。第2章66段中4段已迁移、1段有理由排除、61段queued；下一正文段为 `sec_ii:l42-50`。第2章其余正文与脚注、整章OCR/PDF对照仍待完成，S2未达到S3交接条件。

- 同步将 `book-statements.jsonl` 中既有858条记录的双CR行尾规范为单一CRLF；逐行JSON解析仍为878条，记录内容未改。



### 第2章第II节分节标题 L1–1 排除（2026-09-27）



- 复核待处理队列时发现 `chp-2:02_CHP-2_sec_ii:l1-1` 为自动生成的Markdown文件标题 `# 02 CHP-2 sec ii`，仅用于导航，不属于原书语料；覆盖由 `queued/pending` 更新为 `excluded/complete`，保留排除理由，不生成提及或断言。





### 2026-09-27 S0源序复核与第2章队列修正



- 复核`s2-coverage.csv`后发现，章首与第I节已有阅读记录，但其三个正文/注释段仍未迁入S2表；此前把第II节L42–50标作下一段不符合源序。

- 将章首文件标题`intro:l1-1`、仅含页码/章名导航的`intro:l3-4`、第I节文件标题`sec_i:l1-1`更新为有理由排除；均不生成提及或断言。保留`intro:l6-7`章首脚注及第I节正文为待迁移。

- 该次队列复核时全书账本为51段reviewed且迁移完成、15段excluded、724段queued；提及1,534条、原书断言878条不变。第2章为4段迁移完成、4段有理由排除、58段queued。当时下一步按源序迁入`intro:l6-7`，继而处理第I节，再接回第II节L42–50。





### 第2章章首脚注 L6–7 迁移（2026-09-27）



- 将规范段`chp-2:02_CHP-2_intro:l6-7`迁入S2表：新增候选`cand-4237`（Pastor第XIII卷，版本未指明）、`cand-4238`（P. Pecchiai，首名未明）和`cand-4239`（`I Barberini`，1959）；复用Barberini family、Urban VIII与Pastor作者候选，新增6条原文跨度提及和2条`footnote_citation`断言。

- 将脚注限定为本章一般书目指引。印刷页24（`CHP-2.pdf`物理第1页）目视确认OCR引文准确。按本书书目第934–940行映射Pastor条目及Pecchiai的1959年作品；不推定Pastor的具体版次/页码，不补Pecchiai全名，不把转引书目作为已核事实。书目段仍依全书顺序待S2处理，后续复用这些候选。

- 迁移后全书账本为52段reviewed且迁移完成、15段excluded、723段queued；提及1,540条、原书断言880条。第2章现为5段迁移、4段有理由排除、57段queued；下一段按源序为`sec_i:l3-7`。





## 2026-09-27：第2章第I节 L3–7 迁移与来源映射复核



- 按`segments.jsonl`实际来源完成`chp-2:02_CHP-2_sec_i:l3-7`：新增6个开放候选、29条提及和24条原书断言；覆盖更新为`reviewed/complete`。人物、教育、仕途、作者推断、Sixtus V治理评价和罗马城市改造均按具体发言层次拆分，未写入正式关系边。

- `CHP-2.pdf`物理第1页（印刷页24）核对装饰首字母及跨行OCR：S0的`AFFEO`缺M、`Mand rich`应读作`and rich`。原OCR引句保留，校勘写入断言限定；家庭句脚注1交叉链接到已迁移的`intro:l6-7`，书目提示不当作该句的直接证据。

- 复核发现旧第I节阅读表从L3–7之后与规范分节文件内容错位：`sec_i:l9-10`实际为页导航和Valentin图注，L12–13为页2及反向OCR片段，L15–29为图版页文字。旧摘要降级为检索草稿；未重读的规范段保持queued。下一段按源序为`sec_i:l9-10`。

- 迁移后总账：53段reviewed且迁移完成、15段excluded、722段queued；1,569条提及、904条原书断言、4,244个候选。`audit_tables.py`为0 errors；两条旧source_ref警告及全书S2未完成警告仍存在。





## 2026-09-27：Plate 2题注转录及OCR残段复核



- 物理第2页Plate I的题注位于规范段`sec_i:l9-10`；复用既有Valentin与《Allegory of Rome》候选，新增2条提及及1条图注归属断言。该独立印刷位置与书前图版清单同文，保留其来源出现但不据此验证作者身份或现藏。

- 物理第3页Plate 2的分节OCR段`sec_i:l12-13`只含页码与反向残片；目视复核发现2a题注较书前目录多出“as young prelate”。为使该短语具备可复现行号，新增派生文本`02_CHP-2_sec_i_visual-transcription.md`（同一书源ID），用现有构建器生成S0补充段并写入2a/2b的8条提及、4条断言。原PDF和原OCR均保持不变；原反向残段有理由排除，不另造无锚点表行。

- S0现791段。S2总账更新为55段reviewed/complete、16段excluded、720段queued；候选4,244，提及1,579，原书断言909。`build_source_segments.py`预览和写入均为58个文本文件、791段、0 issues；Plate 2补充段的行哈希、提及偏移和断言引句可复现。下一段按正文源序为`chp-2:02_CHP-2_sec_i:l15-29`。



### 2026-09-27：第2章图版OCR复核与第I节L44–53迁移



- 对照`CHP-2.pdf`物理第4页，`sec_i:l15-29`是Plate III页眉及反向OCR题注碎片；两条可辨题注与书前图版清单重复，故有理由排除。物理第5页的Plate IV题注可读内容追加至派生转录文件，规范段为`sec_i_visual-transcription:l6-9`；原`sec_i:l31-42`只有页眉和反向OCR残片，记录为有理由排除。视觉转录现有Plate II和Plate IV两个可引用段；原PDF与OCR资产未改。

- 完成`chp-2:02_CHP-2_sec_i:l44-53`，新增11个开放候选、39条提及和25条原书断言，覆盖为`reviewed/complete`。印刷页25（PDF物理第6页）核对`os/of`与`purpose.be/purpose, he`等OCR疑点；保留Caravaggio肖像识别的推测语气、遗产金额两种估值、Haskell对Ferrara接管的评价和未指明的掠取者。脚注1–6待注释段迁入后交叉链接；L53句尾与下一段L55–69续接。

- 当前S0有792段；S2总账为57段reviewed/complete、18段excluded、717段queued；候选4,255、提及1,625、原书断言938。第2章共68段，10段完成迁移、7段排除、51段queued；下一段为`chp-2:02_CHP-2_sec_i:l55-69`。`audit_tables.py`为0 errors；两条既存字段来源警告及全书尚有717段未处理的警告仍在。



### 2026-09-27：第2章第I节 L55–69 迁移



- 按S0规范段逐行读取`02_CHP-2_sec_i.md`的L55–69，并与`CHP-2.pdf`印刷页26（物理第7页）核对。修正旧阅读草稿对本段内容范围的缩减；本段涵盖Barberini礼拜堂装饰、Barocci与Passignani、驻巴黎使节职务、赠礼、引语及圣彼得大殿计划。

- 新增16个来源候选、45条精确跨度提及、23条原书断言；更新覆盖为`reviewed/complete`。保留Passignani穹顶装饰建议与实际壁画委托的差异、French backing匿名性、Henri IV长子未名、银器引语和“蜜蜂来自法国王室纹章”的未核状态、Renier Zeno脚注定位，以及两座宫殿可能重合但尚不合并的状态。

- PDF核对确认原OCR法语引文`quatte`、`avoirs`分别应读为`quatre`、`avons`；OCR原文不改写，校勘保存在断言限定。脚注1–4在本文件后置注释段中，待其对应S0段S2迁移后交叉链接。`basilica`承接上一段；末句跨到下一段`l71-80`，不提前补入Carlo Maderno。

- 迁移后全书账本为58段reviewed/complete、18段excluded、716段queued；候选4,271、提及1,670、原书断言961。`audit_tables.py`结构错误为0；两条旧`source_ref`警告及全书S2未完成警告仍在。下一段为`chp-2:02_CHP-2_sec_i:l71-80`。





## 2026-09-27：第2章第I节 L71–80 迁移与当前账本校正



- 按规范S0来源重读`02_CHP-2_sec_i.md` L71–80，并对照`CHP-2.pdf`印刷页27（物理第8页）。完成上一段关于Carlo Maderno的跨段提及；分开记录Maffeo赴Spoleto、Bologna使节任职和返回Rome的时间／地点语境；对Scipione与Paul V的亲属称谓单独记为原书关系断言。

- 写入47条精确跨度提及和23条原书断言，净增14个候选。发现此前为St Peter’s façade新建的`cand-4286`与`cand-4232`自然键相同，遂删除重复行并将本段“façade”提及及建筑构件限定复用`cand-4232`；ID不回收。新增`cand-4287`记录未具名的Borghese country houses复数地产组，类型暂留空；更正该提及与断言端点，Pincio、Frascati仍分别作为地点候选。

- 补录Scipione为Paul V侄子的明确关系候选及Haskell对其出身／学识的作者评价，和威尼斯使节的引述分层保存。d’Arpino画作没收、Raphael《Deposition》移取、Domenichino监禁与Aldobrandini委托分别表达，不从“赞助”一词推导正式关系。

- PDF核对印刷页27（物理第8页）：`hfe`校读为`life`；印本姓名为`Cavaliere d’Arpino`。保留S0转录，不改写来源引句。脚注1–4对应分节文件L136–139，脚注2识别使节Renier Zeno（1621–1623）；脚注正文尚未迁移，交叉链接待后续脚注段完成。

- 当前表审计0 errors；总账为59段reviewed/complete、18段excluded、715段queued；候选4,285、提及1,717、原书断言984。第2章为12段迁移完成、7段排除、49段queued。下一段按S0源序为`chp-2:02_CHP-2_sec_i:l82-93`。





## 2026-09-27：第2章第I节 L82–93 迁移



- 逐行阅读规范段chp-2:02_CHP-2_sec_i:l82-93，并对照CHP-2.pdf印刷页28（物理第9页）。补完L71–80末尾的收藏句，迁入17个候选、52条精确跨度提及和34条原书断言；保留Paul V—Gregory XV继替、Scipione失势、Ludovico与Agucchi赞助语境、Agucchi的艺术理论以及del Monte转场。

- 身份和语气边界：将Caravaggio及其追随者的自然模仿观点记录为Haskell归述的观点；Agucchi的理论来源限定为原书所述；Domenichino的师承与Agucchi交往分列；Grand Duke、Reni壁画所处casino和del Monte的官邸均未被推定为具体对象。Farnese palace复用候选的索引页码不含印刷页28，留待S3核对。

- PDF确认L90 OCR的longterm对应印本跨行long-term，L88印本为protégés；保留S0原文，不改写锚定引句。末句引语在L93不完整并于L95续接；脚注1–3仍待相应脚注段迁移后交叉链接。

- audit_tables.py结构错误为0；账本现为60段reviewed/complete、18段excluded、714段queued，候选4,302、提及1,769、断言1,018。第2章13段迁移、7段有理由排除、48段queued；下一段按源序为sec_i:l95-106。



### 2026-09-27：第2章第I节 L95–106 迁移



- 按S0段chp-2:02_CHP-2_sec_i:l95-106逐行阅读，并对照CHP-2.pdf印刷页29（物理第10页）。新增34个来源候选、84条精确跨度提及和51条原书断言，覆盖更新为reviewed/complete。嵌套实体跨度、候选外键、断言引文和来源行锚通过审计。

- 承接L93未完引语及del Monte叙述，记录其早年生活、Caravaggio与Andrea Sacchi；再处理Giustiniani的父系、宅邸、收藏、Caravaggio关系、艺术品群、未具名Cupid图像与审美观点。候选分别表达未具名的Caravaggio画作组、委托委员会、赌场、宫殿/乡间住宅、藏品与房间、13幅画作组、Caravaggio北方追随者、Carracci集体称谓、未具名Cupid画作及其图像人物、Giustiniani文章。未强行指定Cupid画作作者/标题，也不把group称谓拆成未经命名的个人。

- 记录del Monte对委员会施加影响与为Sacchi取得委托，限定委员会为中介；分别记录Vincenzo和Benedetto支持Caravaggio，保留“among”；将Cambiaso预示Caravaggio用光的说法保留may-well-have-seemed的推测语气；将“largest group”“virtually unknown”“only one to suggest”及“wide and catholic taste”标为Haskell评述或推断。L103末句续至L108–119。

- 注释脚注1–4实际位于sec_i:L143–146（规范段sec_i:l124-157），尚待该段迁移后正式交叉链接。脚注5的作者／年份暂与书目Salerno条目L1081、Portoghesi L996–997、Brugnoli L266–268（两条）、Faldi L462–463、Toesca L1169匹配；对应标题记录为书目候选，匹配仍待书目S2处理核定，书目指针不作为事实证据。Plate 17b前置图版主体cand-3077与正文索引候选cand-1200留待S3对齐；Faldi Italo候选与第一章cand-3516不合并。

- 印刷页校勘：S. Luigi dei Frances!读作Francesi；proorictor读作proprietor；i960读作1960。S0 OCR和original_quote均未改写，校勘放入断言限定。更新后全书为61段reviewed/complete、18段excluded、713段queued，4,336候选、1,853提及、1,069断言；第2章为14段迁移、7段排除、47段queued。结构审计0错误。



### 2026-09-27：第2章第I节 L108–119 迁移



- 按S0规范段`chp-2:02_CHP-2_sec_i:l108-119`逐行读取，并对照`CHP-2.pdf`印刷页30（PDF物理第11页）。新增11个候选（cand-4339–cand-4349）、67条精确跨度提及和41条原书断言；将覆盖更新为`reviewed/complete`。

- 完成本段承接L103的句意；分别记录Vincenzo Giustiniani的艺术判断、旧一代Mannerists与Caravaggio／Carracci艺术家群；1606年与Cristoforo Roncalli（Pomarancio）北行、与Peiresc通信、Maffeo Barberini宫廷和收藏、Guido Reni及Pomarancio作品、Bernini父子关系、St Sebastian、Paul V／Scipione／Ludovisi对Bernini委托格局、Maffeo诗作和镜像轶事。未将未具名群体强行指认为正式机构，也未把购得的《Jacob and the Angel》直接判作Pomarancio创作。

- 分开Vincenzo与Maffeo两座原文仅称“his palace”的空间；新候选的Maffeo宫殿仍待身份对齐。将“the Ludovisi”作为家族集体，将《St Sebastian》《Apollo and Daphne》按Bernini作品建候选；David复用现有Bernini《大卫》KU候选，避免与圣经人物David混同。

- 印本确认OCR误识：L109 `Cavalière`按印本读作`Cavaliere`；L110、L115 `hi`读作`in`；L117 `writhig`读作`writing`。印本读作`Passignano`，索引为`Passignani`，保留源文拼写并交S3核对；印本别名为`Pomarancio`，与索引`Pomerancio`也保留差异待对齐。OCR来源和断言引句均未改写，校勘记入限定。

- 本段脚注1–6的印刷页下注在S0规范段`sec_i:l124-157`的L147–152；前段L95–106的脚注1–4在同段L143–146。修复前段7条statement中的错误目标`sec_iv:l139-152`，全部改指正确的后置注释段。两处脚注内容仍待该规范段处理后分别交叉链接。

- 对Bernini持镜故事，记录本段Haskell叙述，同时链接第一章规范段`chp-1:01_CHP-1_sec_ii:l129-135`（印刷页19）对同一故事“翻新逸事／象征价值”的限定；事件保持未核，不生成正式关系。

- 写入前预检通过；写入后`audit_tables.py --summary`为0结构错误。当前全书62段reviewed且迁移完成、18段excluded、712段queued；候选4,347条、提及1,920条、断言1,110条。第2章为15段迁移、7段排除、46段queued。下一段为`sec_i:l121-121`。



- 第2章第I节规范段`chp-2:02_CHP-2_sec_i:l121-121`只有OCR页码标记`[Page 31]`，对照`CHP-2.pdf`物理第12页确认它是页面导航，无独立正文；正文标题与文本按后续`sec_ii`来源切分。该段按有理由排除记为`excluded/complete`，不生成提及或断言。

### 2026-09-27：第2章第I节脚注 L124–157 迁移



- 按规范S0段`chp-2:02_CHP-2_sec_i:l124-157`逐注阅读印刷页25–31，对照`CHP-2.pdf`物理第6–12页。写入42个候选（cand-4350–cand-4391）、81条精确跨度提及和57条书内断言；更新为`reviewed/complete`。L125为反向OCR图注残片，无独立脚注语义。

- 脚注正文映射：L126–131→正文L44–53；L132–135→L55–69；L136–139→L71–80；L140–142→L82–93；L143–146→L95–106；L147–152→L108–119；L153–157→第II节L3–8。已建立对应脚注引用的双向过程关联；L95–106及L108–119的相关原书断言分别引用L143–146和L147–152的注释证据。

- PDF校读并记录主要OCR差异：L127 Bellori；L132 “of a”及`Biblioteca Vaticana, Barb. Lat. 5820, cc.14 and 17`；L137 `e`；L143 `avviso`；L146 Bellori；L148补录`Barb. Lat. 6502`；L151印刷脚注号为5、OCR误作8；L157 Abbate及`Biblioteca Vaticana, Urb. Lat. 1100`（1630-01-23）。脚注4中Walker关于Rubens未必临摹Titian的意见保留为有归属的限定判断；Maffeo写信身份为“presumably”；Mennemoli姓名保留疑读，均不外推为确定事实。

- 原有旧结果表把本规范段描述为del Monte等正文，已标记为旧映射错误并更正，不删除该修订痕迹。正文段L95–106脚注1–4、L108–119脚注1–6现均连到后置注释段；脚注5书目匹配仍待书目S2处理。

- 覆盖更新后全书63段reviewed/complete、19段有理由排除、710段queued；第2章16段迁移、8段排除、44段queued；候选4,389、提及2,001、断言1,167。`audit_tables.py --summary`结构错误为0；针对表审计与数据导出测试通过。下一段按S0源序为`chp-2:02_CHP-2_sec_ii:l42-50`。



### 2026-09-27：第2章第II节 L42–50 迁移



- 按规范段`chp-2:02_CHP-2_sec_ii:l42-50`逐行读取，并目视核对`CHP-2.pdf`印刷页35（物理第16页）。新增13个候选（cand-4392–cand-4404）、69条精确跨度提及和24条原书断言，覆盖更新为`reviewed/complete`。

- 语义记录区分了巴尔达基诺作为整体、扭柱构件、未实施的“复活的基督”雕像方案及替代十字架方案；复用Jesus、St Peter本人、圣彼得大殿、穹顶、Raphael、Urban VIII、Bernini、Barberini家族、Pantheon及已记录的无名圣彼得大殿委员会。Solomon’s Temple、Jerusalem、扭柱传统、Barberini蜂／日／月桂标志作为各自候选；提及不等于身份或历史说法获外部验证。

- 记为Haskell的判断与限定：巴尔达基诺的视觉接受、Urban VIII可能直接参与方案但确保其与本人关联、扭柱“supposed”与Christ曾倚靠的传说、Ginnasi的形象和西班牙倾向、200,000 scudi造价及年收入比例、Bernini建议从Pantheon取青铜。脚注1–3分别关联讽刺诗、Ginnasi的政治评价和祭坛方案文献，目标均为尚未处理的`sec_ii:l147-193`；不把注释定位当作已读的独立支持。未建立正式关系边。

- PDF校正S0差异：`200,000 soldi`实际印为`200,000 scudi`；`spécial`印为`special`；`tire pillars`印为`the pillars`；L50在`dome.`后有脚注3，OCR误识为问号。L43中`toSt`的间距／印刷标点有污损，不改变St Peter指称。S0文本与original_quote保持原貌，校勘置于限定。该段L50以`Bernini’s`不完整结束，下一规范段继续；未提前写入Bernini方案获选的结论。

- 写入后`audit_tables.py --summary`为0结构错误；`test_audit_tables.py`与`test_export_dataset.py`通过。当前全书64段reviewed/complete、19段excluded、709段queued；提及2,070条、断言1,191条；下一段为`chp-2:02_CHP-2_sec_ii:l52-60`。





### 2026-09-27：第2章第II节 L52–60、L62–69 迁移



- L52–60：按规范段逐行阅读，对照`CHP-2.pdf`印刷页36（物理第17页），新增29个候选、88条精确跨度提及和25条原书断言。承接L50的未完“Bernini’s”，记录Bernini方案获接受、祭坛移入crypt、柱龛留给四位高崇圣人雕像，并把原段委员会待选断言与本段结论连起。保留匿名雕塑家、未全名列出的圣人、石制圣物复制品及其图像内容不明；把Countess Matilda与其墓、墓上浮雕、Henry IV、Gregory VII和Canossa场景分开。Bernini浮雕的预定室内位置和当时portico位置分开。Passeri引语截在“and”，已留续文锚点。

- L52–60页图校勘：`beplaced`→`be placed`、`butis`→`but is`、`martyrdomofChrist`→`martyrdom of Christ`，并核实“was given”前的多余引号；S0及original_quote保持不改。脚注1–3待`sec_ii:l147-193`迁移。

- L62–69：对照印刷页37（物理第18页），新增13个候选（cand-4434–cand-4446）、78条精确跨度提及和15条断言。L63续完L60的Passeri讽刺引语；记录Haskell关于Bernini在Urban VIII在世时保持不可撼动、1623–1644年几乎只承接Barberini委托的叙述与动机推断。将Scipione Borghese两尊胸像作为未细分版本的作品组，与Plate 5工作候选暂不合并。Charles I与Richelieu获准请求Bernini肖像只表示许可，不推断完成或形式；Nicholas Stone引语保留其原发言者、Haskell转引层次、Thomas Baker胸像、Van Dyck三人肖像及身份未明的Cardinal Barberine。

- L62–69下半段将S. Bibiana建筑与Bernini重建／装饰工程分开，保留Saint遗体候选的类型待定状态，并分别记录Saint Bibiana、Bernini雕像和High Altar。Haskell关于作品“restrained yet emotional”及其作为绘画语言转译的说法记录为审美判断，不作独立事实。页图校读确认S0 `arcliitectural`应为`architectural`、`Tor`应为`For`，原OCR与原书引句均保持不改。脚注1–5待后置注释段迁移后链接。

- 更新后全书S2为66段reviewed/complete、19段有理由排除、707段queued；候选4,444、提及2,236、原书断言1,231。结构审计0错误；两条旧enrichment来源定位警告仍在。下一段为`chp-2:02_CHP-2_sec_ii:l71-78`。





### 2026-09-27：第2章第II节 L71–78 迁移



- 按规范来源逐行处理L72–78，对照`CHP-2.pdf`印刷页38（物理第19页）。新增27个候选（cand-4447–cand-4473）、82条精确跨度提及和23条原书断言。将Ciampelli的壁画系列、Pietro da Cortona受分配的三场景、Sacchetti兄弟相关建筑空间、Marino文艺活动、Titian原作与Pietro复制委托分开建模；新建Raphael《Galatea》原作、独立复制品及未具名复制者，避免把索引中的Raphael人物条目或相邻的Pietro叙述错作作品/复制者身份。Marino收藏内容与类型不明，保持开放候选。

- L77末尾“which”续至下一规范段L80–89；不提前纳入其后的原作购藏叙述。正文脚注1–4分别定位至后置注释段`sec_ii:l147-193` L172–175，当前保留待交叉链接。印刷页38确认L78书目指针为“Briganti, 1962”，S0 OCR作“Brigand”；原文和S0不改写，校勘记在限定字段。

- 写入前`--dry-run`通过；写入后`audit_tables.py --summary`为0结构错误，相关审计/导出测试通过。全书现为67段reviewed/complete、19段excluded、706段queued；候选4,471、提及2,318、原书断言1,254。两条既有enrichment `source_ref`警告未变。下一段为`chp-2:02_CHP-2_sec_ii:l80-89`。





### 2026-09-27：第2章第II节 L80–89 迁移



- 按规范段处理L81–89，对照`CHP-2.pdf`印刷页39（物理第20页）。新增16个候选（cand-4474–cand-4489）、63条精确跨度提及和35条原书断言。L81延续L77在“which”处截断的Titian《圣家与圣凯瑟琳》句，现补录Cardinal Aldobrandini从Ferrara购得原作，并与上一段Pietro的复制委托双向建立statement引用；保留原作、复制品和复制者的边界。

- 复用索引候选记录Pietro为Marcello绘制的《Polyxena献祭》《酒神凯旋》，为索引中未匹配到Pietro条目的《萨宾妇人被劫》新建作品候选。新增巴洛克绘画、模仿训练、Sacchetti艺术圈、processional style、Castel Fusano、乡间宅邸装饰项目、礼拜堂及两组装饰题材、Tolfa和矿区／特许权／矿区绘画、grand manner等候选。L75所述villa及gallery与当前Castel Fusano乡间宅邸／gallery可能同一，记录待S3核定；不把商业特许权等同矿山所有权。

- 保留Marcello/Urban VIII、Giulio任枢机与Marcello papal treasurer的不同状态；疾病导致Marcello退居Naples及其死亡另立断言。关于Sacchetti保护艺术家的编年史引语及兄弟扶助Pietro的转述分开记录，发言来源分别待脚注3、4核对。Andrea Sacchi团队参与和Sacchetti影响其声誉不自动生成正式边。

- 页图校勘：S0 OCR `sables`→印本`fables`；`ability 40 adapt`→`ability to adapt`；Plate `ioa/rob/na/nb`→`10a/10b/11a/11b`；`and.breadth`→`and breadth`。S0与original_quote保持原样。脚注1–4分别对应`sec_ii:l147-193`的L172–175，待该注释段迁入后交叉链接。

- 写入前`--dry-run`通过；写入后`audit_tables.py --summary`为0结构错误，定向审计和导出测试通过。全书现为68段reviewed/complete、19段excluded、705段queued；候选4,487、提及2,381、原书断言1,289。两条既有enrichment `source_ref`警告未变。下一段为`chp-2:02_CHP-2_sec_ii:l91-104`。





### 2026-09-27：第2章第II节 L91–104 迁移



- 按规范段核读L91–104，对照`CHP-2.pdf`印刷页40（物理第21页）。L91–94续完Pietro da Cortona在S. Bibiana的壁画与事业叙述，L95为第III节分隔符，L96–104开始Haskell对Urban VIII的性格、诗歌、政治抱负与Bernini肖像的论述。新增12个来源衍生候选（cand-4490–cand-4501）、65条精确跨度提及和23条原书断言。

- 将Rome、Castel Gandolfo、Urban VIII的别墅及附加其上的匿名中世纪城堡分开；诗歌作品与1631年诗集文献分开；未具名侄子保持身份待决；Bernini的多尊青铜与大理石胸像作为未细分版本的作品组。Urban VIII、Pietro、Bernini、Jesuits与papacy复用候选，不在S2裁决其跨章节索引/来源候选身份。把Baroque文化范畴与flattery概念分别记录，不将其强行映射为前段的Baroque painting。

- 记录Urban VIII的诗歌语言及宗教内容偏好、对朋友诗歌题材的劝导、乡村诗题与Castel Gandolfo、外交事务交侄处理、Haskell对Urban性格及教皇政治目标的评价、1631诗卷的制作/插图信息，以及Bernini肖像中的自我呈现、年代变化、庄严姿态与外貌。以上是原书陈述和关系候选，不生成正式关系边。脚注1–5均指向尚待处理的`sec_ii:l147-193`，分别关联乡村生活/别墅、外交听政、占星、对Galileo的处置及肖像文献；不把页下注引证当作已核独立证据。

- L104肖像句在“long moustaches and beard”处被规范段截断，已与后续`sec_ii:l118-125`的L119续文建立待接续标记；其间L106–107、L109–113、L115–116为独立图版题注，按源序处理。页图显示L101 OCR`his.career`应作`his career`，L103 OCR前置短横线为扫描/OCR残迹；S0和`original_quote`均保持原样，校勘记入断言限定。

- 写入前校验候选外键、65条提及的Unicode偏移/原形、允许的嵌套跨度及23条引文锚点；因覆盖范围字符串最初误写`L91-L104`，修正为契约形式`L91-104`后通过。`audit_tables.py --summary`错误为0；`tests/test_audit_tables.py`与`tests/test_export_dataset.py`共17项通过。当前全书为69段reviewed/complete、19段有理由排除、704段queued；提及2,446条、原书断言1,312条、候选4,499行。两条既有enrichment来源定位警告未变。下一段按S0源序为`chp-2:02_CHP-2_sec_ii:l106-107`。



### 2026-09-27：Plate 6 OCR纠偏、Plate 8题头补录及第II节 L109–116 迁移



- 初次对照`CHP-2.pdf`物理第23页时，将`sec_ii:l106-107`的“Bernini; Cardinal Borghese”误当作Plate 6错位题注而排除；现已查明该段对应物理第22页Plate 5，历史误判及更正见本文件后文。物理第23页才是Guglielmo Baur《View of Villa Borghese in 1630》，准确题注仍由派生视觉转录`sec_ii_visual-transcription:l1-3`记录。

- 对照物理第25页发现Plate 8上方印有分组题头“BARBERINI PATRONAGE (see Plates 8, 9, 12 and 13)”，此行未见于现有S0 OCR。将题头和交叉指针补录为同一视觉转录文件的独立段`sec_ii_visual-transcription:l5-6`，现置于queued；不据分组标题预设主题层级或派生实体。

- `build_source_segments.py`预览与应用结果均为59个分节文本文件、794个规范段、0 issues。覆盖账本增补该题头段；旧OCR错误段与新准确转录段分别保留不同状态和来源定位。

- 按源序阅读`chp-2:02_CHP-2_sec_ii:l109-113`，并对照Plate 7物理第24页。视觉图注明确为“Domenichino: Hunt of Diana”；S0将作者和作品标题分拆倒序，L113尾部`D`不在印本图注中。沿用`cand-3024`与`cand-4030`，新增2条精确跨度提及和1条`caption_attribution`断言；保留OCR原引句，印本顺序与非独立作者核验说明置于断言限定。

- 阅读`chp-2:02_CHP-2_sec_ii:l115-116`并核对Plate 8物理第25页。图注明载“Matteo Castelli: Family chapel in S. Andrea della Valle”；按该图版号和地点与书前图版目录L48相连，复用`cand-3837`（Castelli）、`cand-3904`（Barberini Chapel）和`cand-3129`（教堂），不新建同一空间候选。新增3条提及，以及礼拜堂设计署名、礼拜堂位于教堂内两条断言；将设计署名限于礼拜堂，不扩大到整座教堂或所有装饰。

- 两段均完成`reviewed/complete`迁移；写入后全书S2为71段迁移完成、20段有理由排除、703段queued，含2,451条提及、1,315条原书断言和4,499个候选。第2章为24段迁移、9段排除、37段queued。结构审计0错误；两条既有enrichment来源定位警告未变。下一段为`chp-2:02_CHP-2_sec_ii:l118-125`；Plate 6正确题注及Plate 8分组题头仍依源文件顺序待处理。



### 2026-09-27：第2章第II节 L118–125 迁移



- 逐行阅读规范段`chp-2:02_CHP-2_sec_ii:l118-125`，并核对`CHP-2.pdf`印刷页41（物理第26页）。新增18个来源候选（cand-4502–cand-4519）、69条精确跨度提及和29条原书断言；覆盖更新为`reviewed/complete`。候选端点与来源锚经审计通过，未在S2建立正式关系边。

- L119接续L103–104对Urban VIII肖像的外貌描述，并与前段statement建立双向续接。其后记录Urban VIII对公共纪念物的态度、Velletri青铜像、Roman Senate撤销1590年法令及委托Plate 2b大理石像、家族胸像、Carlo Barberini纪念牌与另一尊尚不能确认是否完成的Capitol雕像。区分古代Julius Caesar躯干、Algardi的改制、Bernini提供的头部、Carlo的拉丁文《君主论》提要，以及Haskell对纪念物的艺术与家族抱负评价。

- L125记录Urban VIII墓葬的委托和预定位置、与Julius II／Sixtus V／Paul V纪念物的比较、Bernini受托、Angelo Giori监督及其生平和艺术兴趣、Claude七幅未具名作品的所有权，末尾记新墓工程、利基和Paul III墓／Council of Trent的跨页句。未把计划写成完工事实，未替未具名亲属、雕像执行状态或作品题名补造身份；作者判断和“rather mean”等评价保留为来源表述。

- 本段脚注1–6均已在断言限定中登记，目标注释段为`sec_ii:l147-193`；具体脚注内容尚未迁入，待该段处理后逐条交叉链接。印刷页OCR差异记为`pn`→`an`、`admireC`→`admirer`、`On`→`on`；S0来源文本和`original_quote`保持OCR原貌。

- 迁移后全书为72段reviewed/complete、20段有理由排除、702段queued；候选4,517、提及2,520、原书断言1,344。第2章为25段迁移、9段排除、36段queued。`audit_tables.py --summary`结构错误为0；仍有两条既有enrichment来源定位警告和全书S2未完成／需过程记录复核警告。下一段按S0源序为`chp-2:02_CHP-2_sec_ii:l127-139`。





### 2026-09-27：第2章第II节 L127–139 迁移



- 按S0规范段逐行处理`chp-2:02_CHP-2_sec_ii:l127-139`，核对印刷页42（`CHP-2.pdf`物理第27页），新增17个来源候选、60条精确跨度提及和27条原书断言。L128续完Paul III墓与Council of Trent句，记录墓葬从中央柱移至后殿左侧对应壁龛，并与Urban VIII墓右侧壁龛区分；青铜教皇像、墓葬停工八年、1639复工、Charity、Death、May 1644未能及时完工及1647年Justice完成均分项记录。未把墓整体写成1647年完工，也未臆断雕像制作者。

- L131–138按原书叙述记录Antonio Barberini、嘉布遣会教堂和修院、Cardinal Ludovisi庄园、无名建筑师与方案、皇帝及Magalotti礼拜堂请求、Peretti未具名计划、教皇介入和Capuchin反装饰请愿。Cardinal Ludovisi和Prince Peretti身份不在S2消歧；请求、物资筹备、已开工与建成状态分开。L138纹章动机句保持片段，并与下一段L142续文建立链接。L139只记脚注1末尾的人名P. Domenico da Isnello，不从残尾新造被引研究对象；待L191脚注开头迁入后接合。

- PDF校勘：印本L134无OCR行首句点；L137行首短横线不见于印本，`in'Roman`印为`in Roman`。S0与原书引句不改。



### 2026-09-27：第2章第II节 L141–145 迁移



- 按S0规范段处理L141–145并核对印刷页43（`CHP-2.pdf`物理第28页），新增9个候选、38条精确跨度提及和24条原书断言。L142续完Urban VIII不愿其他王族纹章与Barberini纹章并列的归因判断，并另记装饰责任和木制礼拜堂的约定；只保留为Haskell转述的动机与协议，不推定后续实际陈设。

- L143记录Cardinal S. Onofrio订制木制烛台和十字架、Capuchin退还陈设、教皇坚持接收烛台及高坛的类似争议；分开S. Maria della Concezione的铜制圣体龛与金属枝形烛台方案、S. Andrea della Valle Barberini家族礼拜堂作为比较地点、其青铜烛台与铁栅栏、Capuchin简单装饰规则、请愿和最终材质妥协。木制物件退回、烛台接受、圣体龛改为pietre fine、枝形烛台可省略各记不同状态。

- L144–145记录Urban VIII与Antonio Barberini的祭坛画委托、Guido Reni《践踏魔鬼的圣弥额尔》、Haskell对作品格调及接受度的判断、Domenichino、Lanfranco、Pietro da Cortona、Baccio Ciarpi和Andrea Sacchi参与的未具名画作群，以及未具名Barberini侄辈参与装饰。复用指向印刷页43的索引候选；个人身份不在S2合并。脚注1指向`sec_ii:l147-193`的Malvasia引文，待注释段处理。

- PDF校勘：OCR L143 `pietrefine`合词，印本为`pietre fine`；L145末尾单引号不见于印本；L144脚注1在印本为time后的上标。原OCR来源与original_quote均不改。

- 两段迁移后`audit_tables.py --summary`结构错误0；两条既有enrichment来源定位警告仍在。全书当前74段reviewed/complete、20段有理由排除、700段queued；候选4,543、提及2,618、原书断言1,395。第2章为27段迁移、9段排除、34段queued。`test_audit_tables.py`和`test_export_dataset.py`共17项通过；下一段按S0源序为注释`chp-2:02_CHP-2_sec_ii:l147-193`。





### 2026-09-27：第2章第II节注释、视觉转录及第IV节标题核对



- 按源序处理`chp-2:02_CHP-2_sec_ii:l147-193`，核读注释印刷页32–43：物理页13–21为印刷页32–40，插入图版后物理页26–28为印刷页41–43。新增44个候选、88条提及和80条原书断言；另为L190“National Gallery”馆藏地点建立独立于摄影供片来源的机构候选`cand-4590`，复用已有Claude Seaports、Louvre等候选。记录Baglione/Orbaan嵌套转引、Pietro壁画与未完成的设计、Haskell对Pastor关于Ginnasi的质疑、1633 avviso的转述、Urban VIII占星与Campanella监视说法及Haskell的推论、Claude两幅Seaports的跨馆分布而不把画作逐一配馆。L139脚注尾段与L191开头链接；L193 Barozzi引文指向下一节正文L3。页码字段已按实际扫描物理页校正，印刷页41–43对应物理26–28。

- 依据`CHP-2.pdf`物理页23迁移Plate 6图版视觉转录`sec_ii_visual-transcription:l1-3`，复用Guglielmo Baur、作品和Villa Borghese候选，新增4条提及和1条caption attribution；不将1630标题年份当作独立制作年。物理页25的`l5-6`仅记录“BARBERINI PATRONAGE”及图版交叉指针，作为编辑导航处理，不建立知识层级或主题实体。物理页19脚注4续句的`l8-9`复核“Briganti, 1962”；OCR同句已在主S0段L78出现作“Brigand”，故记为视觉校勘层，不重复建候选。

- 第IV节L1仅为生成的Markdown章节标题，排除并说明；印刷页43注释2实际对应第IV节正文L3，已更正注释statement目标。下一段为`chp-2:02_CHP-2_sec_iv:l3-4`。

- 当前全书覆盖为795段：78段reviewed/complete、21段有理由排除、696段queued；候选4,588、提及2,712、断言1,478。第2章71段：31段迁移、10段排除、30段queued。`audit_tables.py --summary`为0结构错误；两条既有enrichment来源定位警告不变。



## 2026-09-27 第2章第IV节 L19–29 语义迁移



- 按segments.jsonl逐行阅读sec_iv L19–29，并核对CHP-2.pdf印刷页45（物理第30页）；原OCR与original_quote保持原样，ferusalem→Jerusalem只记作印本校勘。

- 新增7个开放候选、68条精确跨度提及和26条原书断言。发言和作者评价保留；委托、提议、获采纳、实际完成分别记录；作品、版本、匿名行动者与推断群组不被合并。

- L17委员会名单与L20续文双向关联；L29“Once again”接下段L31。脚注1–6映射注释L195–200，等该段迁移后回链。

- 账本现为81段reviewed/complete、21段excluded、693段queued；候选4,610、提及2,877、原书断言1,551。审计0结构错误，表审计测试11项通过；既有两条enrichment source_ref警告未变。下一段按源序sec_iv:l31-43。



## 2026-09-27 第2章第IV节 L31–43 语义迁移



- 按规范来源逐行处理`sec_iv:l31-43`，核对`CHP-2.pdf`印刷页46（PDF物理页31）。正文延续L29的“Once again”至L32；新增断言记Francesco把第二版《耶路撒冷陷落》转赠未具名外国显贵。前段第二版本断言现指向本段转赠陈述，保留“再次”的叙事承接。

- 记录Francesco对Cassiano审美的对照、Vouet和Valentin受Caravaggio影响、朋友 patronage 与较华丽 Baroque 风格、Sacchi的风格转向、Vouet的事业走向、Barberini圈影响及Sforza宫殿的购买/赠与。作品、机构、建筑、艺术风格和作者评价分开，未把同名候选提前合并。

- L39–43是印刷页45脚注6跨至页46的续注，并非本段末尾的页46脚注1–4。将Poussin两幅风景画、Blunt的系列假说、可能的Francesco委托和1642年Poussin信件及素描联系纳入本段；前段L25脚注6与本段L39–43互链。页46脚注1–4的完整文字在后置S0注释段L201–204，后续在该段迁移时单独登记，避免同一注释重复计数。

- PDF校勘：L35 OCR`Plate i`为印本`Plate 1`，`represented rather , an awkward`为`represented rather an awkward`；L38 OCR将分隔符`- v -`粘连至Taddeo段首。原S0及`original_quote`保持不变；“He lacked the”与下一规范段L45–52相接，当前只登记续段锚点。

- 新增24个候选（cand-4613–cand-4636）、82条提及、21条原书断言。覆盖改为reviewed/complete；全书账本为82段已迁移、21段有理由排除、692段queued；候选4,634、提及2,959、原书断言1,572。`audit_tables.py --summary`结构审计0错误；`test_audit_tables.py`与`test_export_dataset.py`共17项测试通过。两条既有enrichment来源定位警告不变。下一段`sec_iv:l45-52`。



## 2026-09-27：第2章第IV节 L45–52 语义迁移



- 逐行阅读规范段`chp-2:02_CHP-2_sec_iv:l45-52`，目视核对`CHP-2.pdf`印刷页47（PDF物理页32）。L45为页码导航，语义正文从L46开始；L46–47续完L38“Taddeo lacked the…”句，并将页间续句回链到`st-chp2-seciv-l31-43-taddeo-characterization`。L52段末“Maderno or—more likely—some brilliant collaborator or adviser”的句子未完，已链接到下一规范段L54–63。

- 记录Haskell对Taddeo性格、暴力事件与宽泛赦免、他人替其开脱、预定Barberini家族角色、1627婚姻、军职继承、购买Palestrina领地、1631年Prefect of Rome任命、外交礼仪冲突和公共角色的叙述。未具名妻子与父亲分别列候选，父亲身份留待全局对齐；街头斗殴和杀人事件分开保留，文本未决定其为同一事件还是两个事件。Prefecture复权句为被动语态，未将行为归给前句中的教皇。Colonna、Sforza与Della Rovere作为家族记录；未将家族与个人或家族宫殿合并。

- 区分1625年Francesco购入Quirinal旧宫殿与1626年交给Taddeo两件事；L51重述转交并提供1626年。Sforza宫殿（`cand-4620`）与Barberini新宫殿（`cand-0240`）仍作不同候选，部分旧结构将纳入新方案只记作原书计划；设计者保留Maderno与“更可能”的匿名合作者／顾问两个选项。`Papal armies`和Prefecture of Rome按当前类型暂记机构候选，类型与身份仍可在后续对齐时复核。

- 新增13个候选（`cand-4637`–`cand-4649`）、68条精确跨度提及和26条原书断言。印本校正S0 OCR：L48 `lais character`应为`his character`；L52 `onlyTestored`应为`only restored`。原S0与`original_quote`未改写。印刷页47正文脚注1–5分别指向规范注释段L205–209；页图确认L209的印本脚注标号为5，注释OCR误读为6，后续迁移注释时校正交叉链接。L208注释文字保留待该注释段核对。

- 更新前页续接指针并登记脚注和前后段链接。覆盖行改为`reviewed/complete`，源行范围为`L46-52`。`audit_tables.py --summary`结构错误0；`test_audit_tables.py`与`test_export_dataset.py`共17项通过。两条既有enrichment来源定位警告未变。全书账本为83段reviewed/complete、21段有理由排除、691段queued；候选4,647、提及3,027、原书断言1,598。第2章为36段迁移、10段排除、25段queued。下一段按S0源序为`chp-2:02_CHP-2_sec_iv:l54-63`。结构检查不替代全书S2语义验收。



## 2026-09-27：第2章第IV节 L54–63 语义迁移



- 按规范段`chp-2:02_CHP-2_sec_iv:l54-63`逐行审阅，核对印刷页48（`CHP-2.pdf`物理页33）。L54为页码导航；L55接续前段关于Maderno或更可能的匿名合作者／顾问偏离十六世纪罗马宫殿传统的未完句，并记录Barberini宫殿前庭、立面、拱廊、开放式loggia、乡间别墅式观感、规模及Haskell对Barberini家族金钱型权势的解释。更新前段设计statement的续接statement链接。

- L56记录Maderno于1629年去世后由Bernini接替、Borromini作为Maderno助手参与少量修改、总体平面主线保留，以及宫殿到1633年“几乎完成”而装饰已展开；不改写为全部竣工。L57–58记录Taddeo对艺术兴趣有限、Bentivoglio家族出身Ferrara、Ippolito支持Cesare d’Este继承主张、Guido和Enzo支持Church一方及其受益关系。Guido、Enzo与Ippolito的兄弟关系分别记录；正文“Church’s cause”与“Papacy”分列，避免把宗教机构、政权与城市合并。

- L59–61记录Guido在教会任职、1621年任Cardinal、此前十四年在Flanders与Paris担任Nunzio及其使馆对品味、政治倾向和历史写作的影响；记录Enzo从Ferrara赴Rome担任带引号的“ambassador”及职位由未具名Pope特别创设。为两处身份未明的Pope保留不同候选，不从上下文猜并为Urban VIII或Clement VIII。L62两位兄弟的艺术兴趣分别归属；L63 Van Dyck于1623年初绘Guido肖像及Haskell对肖像的评论分开记录。

- 印刷页图像确认L63 OCR `Use`应读作`life`；保留S0原文及`original_quote`，仅在校勘限定中记录差异。L63关于Guido生活相对简朴的句子止于本段，脚注4链接到注释段L213，并续至规范段`l65-77`。脚注1–4分别指向注释L210–213，待该注释段迁移后回链。

- 新增7个候选（`cand-4650`–`cand-4656`）、62条精确跨度提及、30条原书断言。新增对象为Cesare d’Este、Bentivoglio家族、Flanders、Paris、Church机构，以及两位身份未明且不预设为同一人的Pope；候选`cand-0293`保留索引拼写“Ippotilo”，本段提及注记正文拼写“Ippolito”。未具名历史写作不拆成虚构书目对象，宫殿立面构件作为建筑属性处理。

- 覆盖行改为`reviewed/complete`，范围`L55-63`。迁移后全书84段reviewed/complete、21段有理由排除、690段queued；候选4,654、提及3,089、原书断言1,628。`audit_tables.py --summary`结构错误0；`test_audit_tables.py`与`test_export_dataset.py`共17项通过。两条既有enrichment来源定位警告未变。下一段按规范源序为`chp-2:02_CHP-2_sec_iv:l65-77`；这些机械检查不替代全书语义范围复核。



## 2026-09-27：第2章第IV节 L65–77 语义迁移



- 按规范段`chp-2:02_CHP-2_sec_iv:l65-77`逐行处理，核对印刷页49（`CHP-2.pdf`物理页34）。L66–74是正文，L75–77为脚注1续文；L65仅为页码导航。将上一段L63关于Guido相对简朴的未完句续接至本段L66。

- 新增8个候选（`cand-4657`–`cand-4664`）、66条跨度提及和24条原书断言。记录Guido居于Borghese宫、收藏与Claude早期 patronage、Urban VIII委托、Giovanni da San Giovanni装饰宫殿及三幅场景、Enzo与Bentivoglio家族的赞助及艺术品采购，以及Tassi与Gentileschi壁画的时间和归属争议。分别记录正文“被迫出售”与脚注“售予Lante”，不推断出售日期；保留Haskell的“deliberate trickery”“despoil”评价和Urban可能希望画家作写实记录的限定。

- 页图确认L72 OCR`court Use`应为`court life`、L73`BentivogUo`应为`Bentivoglio`，仅记校勘，S0及`original_quote`保持原样。Cardinal Bentivoglio与Scipione Borghese跨行姓名按各自行内精确跨度锚定。脚注1–7标记对应规范注释段L214–221；脚注1的L75–77续文已在当前段记录，注释段正文待后续迁入再回链。

- 写入前干跑检查通过；写入后`audit_tables.py --summary`结构错误0，`test_audit_tables.py`与`test_export_dataset.py`共17项通过。当前账本为85段reviewed/complete、21段有理由排除、689段queued；候选4,662、提及3,155、原书断言1,652。第2章为38段迁移、10段排除、23段queued。另有两条既有enrichment来源定位警告，全书S2仍未完成。下一段按S0源序为`chp-2:02_CHP-2_sec_iv:l79-89`。



## 2026-09-27：第2章第IV节 L79–89 语义迁移



- 按规范段`chp-2:02_CHP-2_sec_iv:l79-89`逐行处理，核对印刷页50（`CHP-2.pdf`物理页35）。L79为页码导航，正文范围为L80–89。L89从女性Wisdom形象的胸部开始描述光辉，句子未完，已指向下一规范段`l91-94`。

- 新增10个候选（`cand-4665`–`cand-4674`）、53条跨度提及和29条原书断言。记录Camassei受雇并居于Borghese宫、Filippo Napoletano向未具名Marchese推荐Camassei、Cupid与Psyche房间装饰、Bentivoglio向Barberini推荐及Camassei为Sacchetti工作；随后分列两幅Barberini宫天顶壁画及其图像解释。Apollo类型与Roman theologians/artist’s advisers两组成员保持待决，后两者不预设为同一群体；另分别记录Wisdom概念、Wisdom of Solomon文本、Sacchi的Divine Wisdom作品、Raphael未具名壁画群和Vatican Stanze空间。

- L83页图确认Apollo与Muses之间的引号为OCR误识；原S0和`original_quote`均保留，校勘写入断言限定。脚注1–3分别映射至规范注释段L222、L223、L224，注释正文待其S2段迁入后回链。

- 写入前干跑检查通过；写入后`audit_tables.py --summary`结构错误0，`test_audit_tables.py`与`test_export_dataset.py`共17项通过。当前账本为86段reviewed/complete、21段有理由排除、688段queued；候选4,672、提及3,208、原书断言1,681。第2章为39段迁移、10段排除、22段queued。另有两条既有enrichment来源定位警告，全书S2仍未完成。下一段按S0源序为`chp-2:02_CHP-2_sec_iv:l91-94`。





### 2026-09-27：第2章第IV节 L91–94 迁移及前段候选外键校正



- 按规范段 `chp-2:02_CHP-2_sec_iv:l91-94` 逐行语义处理，核对印刷页51（`CHP-2.pdf`物理第36页）。L91是页眉和页码导航，正文范围为L92–94。L92续完前段对Sacchi《Divine Wisdom》的中心女性形象描述，明确其胸前迸出的为Sun；记录Sun同时作为Wisdom常用象征和Barberini家族标识的双重意义，并分列bees与laurel在绘画/灰泥friezes中的位置。Eternity、Sanctity、Purity、Love、Fear、Lust和Wrath按拟人寓意术语处理，不转成历史人物；“and so on”保留为未穷尽列表，Love/Fear与Lust/Wrath不作一一配对。

- 将本段里的friezes与中心壁画分开；Sacchi此前的主接待室与新建的principal reception-room/great hall分别建为place。另为Bracciolini的装饰方案、Cortona的大天顶壁画、未名chapel及其未定名壁画组、未名Jesuit advisers和此前Camassei小房间组分别登记候选；Jesuit advisers类型留空，不冒充Society of Jesus正式单位。复用Urban VIII/Maffeo、Cardinal Francesco、Antonio、Taddeo、Camassei、Bracciolini、Pietro da Cortona与Barberini palace等候选。跨作品的Sun、bees、laurel仍分开留待S3身份对齐。

- 记录Haskell对Sacchi用色、构图、象征含义、接受状况及其对Camassei和Bracciolini的评价，并将相应判断保留为作者归属而非外部事实。Bracciolini为Maffeo服务及随行的关系分别记录；L94在“to”处未完，续至下一规范段L96–104。正文脚注1映射至注释段L225（Guy de Tervarant, column 356），脚注2映射L226（Briganti, 1962）；注释正文待该段迁移后回链。

- 页图核对：L92 OCR `usedas`按印本读作`used as`，`impheations`校为`implications`。L93 OCR `and-also`按句法解读为`and also`，因页图有疑似短横线/扫描痕迹，来源与`original_quote`均保持原样并标明判断。S0文本不改，校勘写入断言限定。

- 追随L89→L91–94续句时检查前段外键：索引候选`cand-2320`的规范名为Sacchi, Andrea，虽带Divine Wisdom子目，仍是艺术家索引候选；作品实际对应现存接受候选`cand-4003`。据此将前段2条作品提及及10条断言中的相关端点改至`cand-4003`，并把“Sun itself”的续句statement双向链接；S2计数不变。此修正不等于S3身份对齐。

- 本段新增18个候选（`cand-4675`–`cand-4692`）、78条跨度提及和36条原书断言。覆盖改为reviewed/complete，源行范围L92–94。迁移后全书87段reviewed/complete、21段有理由排除、687段queued；候选4,690、提及3,286、原书断言1,717；第2章40段迁移、10段排除、21段queued。下一段按S0源序为`chp-2:02_CHP-2_sec_iv:l96-104`。脚注回链和全章OCR差异核对仍未收口，全书S2仍不能交S3。



### 第2章第IV节 L96–104 迁移（2026-09-27）



- 按规范段`chp-2:02_CHP-2_sec_iv:l96-104`逐行阅读，核对印刷页52（`CHP-2.pdf`物理页37）。L96为导航；L97–102为正文；L103–104为脚注2续文。正文补全Bracciolini陪同Maffeo赴Paris的前段续句，记录其离开Maffeo、1623年求情及后来在Sinigaglia和罗马的经历，并转入Cortona Barberini天顶画及其寓意解释。保留Haskell的叙述、政治阐释和观者效果判断，以及Montagu经Haskell转述的多种解释，不提升为定论。

- 新增36个候选（`cand-4693`–`cand-4728`）、94条精确跨度提及和34条原书断言。区分两位Antonio Barberini及不同作品中的家族蜂／月桂标记；Hercules按未定类型图像人物暂存。脚注1回链至L227，脚注2回链至L228；L228头部尚未处理，因此Montagu文章候选留待该注释段建立。无正式关系边。

- 页图确认OCR `suture Pope`应为`future Pope`、`tire Fates`应为`the Fates`、`seventeenthcentury`应为`seventeenth-century`，且L104页码范围末尾的连字符在印本为句点。保留S0与`original_quote`原貌，校勘记入限定。L101–102句续至L106–107；L94末尾旅行句在本段Paris完成。

- 覆盖更新为`reviewed/complete`，源行范围L97–104；全书账本88段reviewed/complete、21段excluded、686段queued，候选4,726、提及3,380、原书断言1,751。`audit_tables.py --summary`结构错误0，相关测试17项通过；仍有两条既有enrichment来源定位警告。下一段按规范源序为`chp-2:02_CHP-2_sec_iv:l106-112`。机械检查不等于全书语义验收。

### 第2章第IV节 L106–112 迁移（2026-09-27）



- 阅读规范段`chp-2:02_CHP-2_sec_iv:l106-112`，核对印刷页53（PDF物理页38）。L106为页码导航，L107补完L101–102的壁画巨人句。L108–109记录Haskell对教皇赞助题材变化、Borghese/Ludovisi历史与神话题材、两幅天顶画的文学兴趣、Cortona的展示效果和后世接受的判断；L109–111将其对Barberini方案影响的因果关系保留为“very likely”，并将Domenichino评论保留为“from what he had heard”的转述意见。

- L112记录Cardinal Francesco雇用Romanelli、后者承担教堂祭坛／天顶绘画并管理Barberini tapestry works、1638年获Accademia di S. Luca Principe职位、Francesco对学院的控制及其资助学院教堂重建等断言。新增8个候选（`cand-4729`–`cand-4736`）、50条提及和22条断言；文学／展示综合与天顶画iconographic programme分开，未具名学院教堂与学院机构分开。挂毯works的组织性质未定。无正式边。

- 脚注1–3分别指向后置注释段L229–231，后续迁移时再核其书目信息。前段statement `st-chp2-seciv-l96-104-giants-conflict-continuation` 已标记由L107接通，并记录续句原文；L101–102的原引句范围保持原样。

- 覆盖更新为`reviewed/complete`、源行范围L107–112。迁移后全书89段reviewed/complete、21段有理由排除、685段queued；候选4,734、提及3,430、原书断言1,773。审计结构错误0，相关测试17项通过；仍有两条既有enrichment来源定位警告。下一段按规范源序为`chp-2:02_CHP-2_sec_iv:l114-125`。机械检查不等于全书语义验收。



### 第2章第IV节 L114–125 迁移（2026-09-27）



- 阅读规范段`chp-2:02_CHP-2_sec_iv:l114-125`，核对印刷页54（`CHP-2.pdf`物理页39）。L114为页码导航，L115为节标题，正文L116–125完整迁移。判断气质与审美趣味的作者概括；分录Francesco对Cortona/Romanelli的选择、Sacchi的自我定位与Antonio赞助、Antonio的任命和Haskell的褒贬、Antonio的审美兴趣、Urban VIII对乌尔比诺的主张、della Rovere继承与教皇控制、Taddeo的头衔及Antonio的Legate身份，以及乌尔比诺绘画转移与Studiolo肖像经历。

- 新增16个候选（`cand-4737`–`cand-4752`）、62条跨度提及和30条原书断言。分开乌尔比诺城市／政治领土、私人收藏／公爵绘画集合、未识别作品群／建筑空间；Cardinal Borghese、Cardinal Ludovisi与Grand Duke均不在S2猜定身份。Haskell对Antonio品格、Conclave反应和政治动机的表述均保留来源归属。未生成正式关系边。

- 页54脚注1指向后置注释L232，脚注2、3指向L233，注释段`chp-2:02_CHP-2_sec_iv:l190-245`仍queued，待后续迁移时回链。L125 “There the Pope issued a special”是截断片段，已链接到下一规范段L127–137。

- 写入前干跑核对候选自然键与外键、62条提及原形和Unicode偏移、30条断言引文锚点及coverage状态；通过后先备份再写入。写入后覆盖为`reviewed/complete`、来源范围`L116-125`。全书90段reviewed/complete、21段有理由排除、684段queued；候选4,750、提及3,492、原书断言1,803。`audit_tables.py --summary`结构错误0，`tests/test_audit_tables.py`及`tests/test_export_dataset.py`共17项通过；两条既有enrichment来源定位警告未变。下一段为`chp-2:02_CHP-2_sec_iv:l127-137`。结构检查不代表独立语义验收。

### 第2章第IV节 L139–152 语义迁移（2026-09-27）



- 核读规范段chp-2:02_CHP-2_sec_iv:l139-152及印刷页56（CHP-2.pdf物理页41）。L140补完前段比武仿古叙述为获得欣然赞同，并记Sacchi绘画；L141记Sacchi为Cardinal Guido Bentivoglio的比武记述绘制插图。L142保留Haskell对Barberini关联罗马骑士传统的解释。L143分列Taddeo任Prefect仪式、Tassi奉命绘制该场景、Taddeo婚姻与Palestrina权利，以及作者对Barberini耗财与复古策略的批评；本段未指名其婚姻对象，不作身份推定。

- L144–148记宫殿馆藏、1642年图册、图书室与剧场、1632年歌剧演出及Pietro da Cortona建造专门剧场；后续迁移时间保留probably限定。古物集合和未名画作群的类型待决；Temple of the Muses按比喻处理。Bouchard出席“first...”的句子续至L171–179的L172。

- L149–152为脚注2在页56的续文，记录Lavin、Orbaan、Tessin、Cantalamessa、1935年目录及Montagu、Waterhouse的资料协助。脚注1/2/3分别指向注释段L237/L238/L239；脚注2头部Teti待注释段迁移后回链。

- 页56图像确认OCR 3ooo、Lavili、ofthe、193 5及L238 Teri分别应作3000、Lavin、of the、1935、Teti；S0和original_quote不改。

- 新增23个候选（cand-4770–cand-4792）、58条提及、19条断言；无正式关系边。覆盖改为reviewed/complete，行范围L140–152。全书92段完成、21段排除、682段queued；候选4,790、提及3,601、断言1,846；第2章45段完成、10段排除、16段queued。审计结构错误0、相关测试17项通过；两条既有enrichment来源定位警告仍在。下一段为chp-2:02_CHP-2_sec_iv:l154-155。



- 2026-09-27：第2章第IV节脚注段`chp-2:02_CHP-2_sec_iv:l190-245`完成迁移（76个新候选、148条提及、107条原书断言），印刷页44–58（PDF物理页29–47）核对注号、OCR差异及脚注续文；原OCR保留，印本独有续文记入校读限定。覆盖更新后全书为99段reviewed/complete、21段excluded、675段queued；第2章为52/10/9。下一规范源段为第VII节L1标题。

- 2026-09-27：规范段`chp-2:02_CHP-2_sec_vii:l1-1`核实为OCR自动生成的节标题，不是原书内容，按规则记为`excluded/complete`，不建提及或断言。全书仍为99段reviewed/complete、22段excluded、674段queued；第2章为52/11/8。

- 2026-09-27：第VII节规范段`l3-3`与`l5-19`完成语义迁移。印刷页58–59（PDF物理页47–48）确认句子跨页续接，并核校Giulio Sacchetti、failed、1645；OCR中的promote.the按印本标记及上下文作词间空格读取，S0不改。新增11个候选、81条提及、22条原书断言；保留两个选举枢机身份未定、1653年Francesco/Antonio兄弟群体及叙述者限定，新增的群体候选不替代成员KU。脚注1–6待注释段L38–54迁移后回链。结构审计0错误，8,083个候选引用无缺失或excluded外键；全书当前为101/22/672，第2章54/11/6，下一段为`l21-30`。两条既有enrichment来源定位警告未变。



### 第2章第VII节 L21–30 迁移（2026-09-27）



- 核读规范段chp-2:02_CHP-2_sec_vii:l21-30及印刷页60（CHP-2.pdf物理页49）。新增22个候选、86条提及和24条原书断言；复用已有候选并保留未执行的壁画委托、匿名机构、作品版本和题名人物边界。Urban VIII挂毯组与草图/cartoons分开，Velasquez是否为Francesco作肖像仍保留疑问。

- 印本核校fellow-painters、his、life、The Marriage of Peleus、It；S0原OCR与original_quote不改。脚注1–7回链到仍queued的注释段L38–54。L5–19的Francesco赞助叙述已接通；挂毯工期“more than twenty years mainly”留作待续片段，下一规范段L32–36负责解释。

- 覆盖更新为reviewed/complete（L22–30）。全书为102段reviewed/complete、22段有理由排除、671段queued；候选4,934、提及4,043、原书断言2,061。结构审计0错误；两条既有enrichment来源定位警告未变。下一段为chp-2:02_CHP-2_sec_vii:l32-36。



### 第2章第VII节 L32–36 迁移（2026-09-27）



- 核读规范段chp-2:02_CHP-2_sec_vii:l32-36及印刷页61（CHP-2.pdf物理页50）。新增5个候选、31条提及和13条原书断言；将baroque风格、Francesco个人图书馆与未具名群体分别建候选。

- L33续完前段挂毯工期句，保留超过二十年及Francesco坚持使用自家羊毛为主要原因；此前pending的工期片段回链完成。拆分纪念Urban VIII、风格推动、委托的象征意义、Francesco文化角色、Bernini受Barberini赞助与Maffeo/Taddeo亲子关系等断言。对“his family”作上下文限定：可能指Barberini家族，但所有格先行词并未明说，后续关系阶段仍须核实。

- 印刷页核对正文与脚注标记1–3。标记1/2/3分别回链后置注释L51/L52/L53，相关注释仍queued。纸本L51能辨“MSS. Barb. Lat. 6463”，OCR漏掉定位，原文保留至注释迁移时作校勘记录。

- 覆盖更新为reviewed/complete，源行范围L33–36。全书103段完成、22段有理由排除、670段queued；候选4,939、提及4,074、原书断言2,074。结构审计0错误；两条既有enrichment来源定位警告不变。下一段为后置注释L38–54。



### 第2章第VII节注释 L38–54 迁移及第VIII节收尾（2026-09-27）



- `chp-2:02_CHP-2_sec_vii:l38-54`核对印刷页59–61（PDF物理页48–50），新增22个候选、52条提及和22条原书断言。按页码判读17处脚注，并与正文L21–30、L32–36的脚注标记双向回链。印本校勘记录包括p59的脚注号6/8、p60的Mezzetti/Mozzetti与Blunt and Cooke (1960)/i960、p61的Biblioteca Vaticana定位漏识及`S. Carlo alle`/`aile`；S0和original_quote不改。

- `chp-2:02_CHP-2_sec_viii:l1-1`为OCR自动生成的分节标题，非原书内容，按版面导航排除；无提及或断言。`l3-7`核对印刷页61（物理页50），写入31条提及、15条断言；脚注号4回链至注释L54，接通跨段的“remarkable width of culture”。印本校正artists及L6多余开引号，S0不改。

- `chp-2:02_CHP-2_sec_viii:l9-14`核对印刷页62（物理页51），新增10个候选、30条提及和20条断言。保留Bernini与Barberini文化赞助语境、宗教图像/幻觉主义、Cortona天顶画上的Haskell评价、明确点名的赞助关系，以及Urban VIII去世的叙述转折；“both men”、Cardinal Borghese和未具名群体不强行消歧。跨页/跨段内容已接续。

- 三段迁移后第2章为59段reviewed/complete、12段有理由排除、0段queued；全书S2为106/23/666，候选4,971、提及4,187、原书断言2,131。`audit_tables.py --summary`结构错误0；仍有两条既存enrichment来源定位警告。第2章账本覆盖完整，但整章OCR逐段对照和未决项收口仍待处理；全书首个queued源段为`chp-3:03_CHP-3_intro:l1-1`。



### 第3章开篇脚注与首段正文迁移记录（2026-09-27）



- 复核当前表后补存第3章已实施的两个规范段迁移：`chp-3:03_CHP-3_intro:l7-9`写入5条提及、3条断言，来源行L8–9；`chp-3:03_CHP-3_sec_i:l3-14`写入20条提及、7条断言，来源行L3–14。各提及跨度、候选外键与断言锚点以当前机器表为准，逐段语义结果见[chp-03.md](../results/chp-03.md)。

- `03_CHP-3.md`只作并行整章OCR对照，不重复计数。`CHP-3.pdf`物理第1页（印刷页i）核实章题、正文开头和脚注：S0 `URING`/`Dwhich`对应印本`DURING`/`which`；S0 `1620?`中的问号是脚注标记2。原OCR及original_quote保留，差异记在断言限定中。

- 记录并保留Haskell叙述、Grey Brydges嵌套引述与脚注编辑性身份说明的不同话语层级；“it is inferred”保持推测限定。`Discourse of Rome`与脚注所引`Horae Subsecivae`暂不合并；`Galassi Paluzzi, 1951`与书目第506行的匹配暂定，候选`cand-4974`与`cand-4975`留待书目段和后续全局对齐复核。句尾“and yet”续至`chp-3:03_CHP-3_sec_i:l16-24`。

- 两个迁移段入账后，全书当前为108段reviewed/complete、26段有理由排除、661段queued；候选4,973、提及4,212、原书断言2,141。审计结构错误0，仍有两条既有enrichment来源定位警告。第2章整章OCR对照仍待收口；因此下一项仍先收口第2章，再从上述第3章续段开始。



### 第2章整章OCR对照中纠正Plate 5误排除（2026-09-27）



- 对照`02_CHP-2.md`、规范分节来源和`CHP-2.pdf`物理页22–23时，发现旧记录把物理页23 Plate 6的错误OCR“Bernini; Cardinal Borghese”误挂至`sec_ii:l106-107`并排除。物理页22实际为Plate 5，题注为“Bernini: Cardinal Borghese”；页首组题指明Scipione Borghese。物理页23才是Guglielmo Baur《View of Villa Borghese in 1630》，其准确转录保留在视觉转录段`l1-3`。

- 恢复`chp-2:02_CHP-2_sec_ii:l106-107`为`reviewed/complete`（范围L107），新增嵌套caption/work、艺术家和人物提及，以及caption attribution断言；复用`cand-4135`、`cand-0295`、`cand-3011`，没有新增候选。S0的分号保留，冒号校正写入限定。

- 复核后第2章为60段reviewed/complete、11段有理由排除、0段queued；全书为109/25/661，候选4,973、提及4,215、断言2,142。`audit_tables.py --summary`结构错误0；两个enrichment来源定位警告仍在。第2章其余全章OCR差异与未决项尚未收口。



### 2026-09-27：第2章整章OCR差异收口与图版组题补录



- 将整章对照OCR `02_CHP-2.md` 的976个物理行与规范分节源、已建视觉转录逐段对照。低词组重叠项逐条核查后，确认主要是页眉/页码、跨行拆词、反向图版OCR及图版页题。原规范段`sec_i:l124-157`的覆盖范围从L126开始，L125反向Plate 2残片已有明确排除记录；正文末尾脚注行L240对应整章副本L856，已迁入；整章副本L959的`MSS. Barb. Lat. 6463`印本校正见`sec_vii:l38-54`覆盖注和本章脚注过程记录。

- 发现并补录三项先前未进入分节S0的可读图版文本：Plate III（整章副本L52–63；PDF物理第4页）两条正文题注；Plate 5（整章副本L454–455；PDF物理第22页）组题；Plate 10（整章副本L827–828；PDF物理第43页）组题。新增独立派生转录文件，保留原PDF、规范OCR与既有视觉转录不改。Plate III的两条肖像题注复用书前图版候选；Plate 5组题的Scipione实体提及单独锚定，原`Cardinal Borghese`图注提及以跨段组题作身份语境；新增caption depiction断言并保留跨段来源指针。Plate 10组题映射至Marcello Sacchetti候选，不另建未经论证的实体或事实。

- 修正Plate III旧排除理由：`sec_i:l15-29`仅将不可用的反向OCR残段排除，正文图注另由视觉转录覆盖；此前“与目录重复故整段排除”的理由已被新记录取代。Plate 5与Plate 10组题分别新增规范源段；已有Plate 5图注的OCR分号仍原样保留。

- `build_source_segments.py`预览确认新增3个段、无既有段删除或哈希变化，应用后S0共798段、来源段构建0 issues。S2总账112 reviewed、25 excluded、661 queued；第2章74段中63段迁移、11段有理由排除、0段queued；提及4,223条、原书断言2,147条、候选4,973条。`audit_tables.py --summary`结构错误0，2条既存enrichment来源定位警告不变。

- 第2章S2及整章OCR差异收口完成。跨章身份、候选边界及外部来源判断保留给S3/S5；下一段按书序为`chp-3:03_CHP-3_sec_i:l16-24`。



### 2026-09-27：第2章正式章名补入来源账本



- 首页PDF物理第1页印有正式章名“POPE URBAN VIII AND HIS ENTOURAGE”，整章OCR第8行也保留该标题；规范`intro`源只记录“Chapter 2”。将章名另存为派生转录`02_CHP-2_intro_title_visual-transcription.md`，避免把正式标题并入重复页眉排除项；新增段只记录标题语境及Urban VIII提及，不建立历史断言，复用`cand-3104`。

- 生成器预览仅新增该段，无既有段变化；应用后S0共800段、构建0 issues。S2现113 reviewed、25 excluded、661 queued；第2章75段为64 reviewed、11 excluded、0 queued；提及4,224条、断言2,147条。第2章的规范来源、题注差异和正式章名均已核对；下一段为`chp-3:03_CHP-3_sec_i:l16-24`。



### 2026-09-27：第3章 I 节 L16–24 语义迁移



- 逐行处理规范段`chp-3:03_CHP-3_sec_i:l16-24`并核对`CHP-3.pdf`物理第2页（印刷页64）。L16为页码导航，实际来源范围L17–24。L17承接上一段的“and yet”：培养追随者的虔敬及其可能产生的其他领域影响，语法主语为前文的小型宗教团体；不归到随后提及的Oratorians。上一段的早期组织叙述以此续完。L22末的“their superiority”在下一规范段`l26-33`续接。

- 录入Oratorians可能鼓励Caravaggio反传统宗教绘画的推测；Bentivoglio在1600年来罗马前获匿名人士建议联络Oratorians；Paul V与Jesuits友好；Gregory XV及其侄子受Jesuits教育。书内索引`L.csv#114`在印刷页64列出Ludovico Ludovisi，因此侄子依书内索引映射至`cand-1456`，未使用外部身份推断。

- 录入Gregory XV对Ignatius、Francis Xavier和Philip Neri的canonisation及其后续仪式和画像；复用Van Dyck索引候选，同时以`cand-4977`独立记录两幅作品组。主文把画像归于Van Dyck并称其当时在Rome；脚注3续文记录Leo van Puyvelde的Rubens归属与1608年推测，Haskell则说缺乏文献证据且认为其不大可能。归属争议保持并存，不作裁决。

- 录入Urban VIII延续相似政策、发布未注明对象的canonisation bull、本人及家族对宗教团体的同情、1639与1640年两次访问Gesù；复用已有Jesuit statutes候选`cand-4760`，新建来源局部的访问/庆典事件候选。Antonio Barberini作为Jesuit Society特别赞助人及由Andrea Sacchi绘制一次访问场景分别记录；未推断是哪次访问、作品题名或委托形式。

- 录入Jesuits of Antwerp出版`Imago primi saeculi`、Haskell对该书的评价与对宗教团体社会整合和艺术影响的双向判断、Ottonelli为Pietro da Cortona向Barberini进言、两人合作撰写绘画说服力论著、Gian Paolo Oliva与Bernini的友谊，以及宗教团体教堂装饰的迟滞、财政短缺和对罗马权势家族的依赖。将“the Barberini”与未具名的罗马统治家族类别分开；未具名宫殿不并入Palazzo Barberini。

- 印本核对校正了OCR显示：`Ges��`为`Gesù`，`Imago primi saettili`为`Imago primi saeculi`，`Padre Ottonefli`为`Padre Ottonelli`。原S0与`original_quote`均不改，差异留在提及或断言限定中。L18侄子前的孤立句点按印本视为OCR杂点。脚注3正文续文在L23–24、脚注头在同文件L38；待脚注段迁移后连接两处。脚注1、2、4、5同样待其注释段迁移。

- 新增10个候选（`cand-4976`–`cand-4985`）、68条精确跨度提及和35条原书断言；覆盖范围记为`L17-24`。S2总账更新为114段reviewed/complete、25段有理由排除、660段queued；候选4,983、提及4,292、原书断言2,182。第3章46段中3段reviewed、3段排除、40段queued。`audit_tables.py --summary`结构错误0，两条既有enrichment来源定位警告不变。下一段为`chp-3:03_CHP-3_sec_i:l26-33`。



### 第3章 I节 L26–33迁移（2026-09-27）



- 处理规范段`chp-3:03_CHP-3_sec_i:l26-33`，核对`CHP-3.pdf`物理第3页（印刷页65）。L26仅为页码导航；正文范围L27–33。L27续完L16–24以“their superiority”开启的句子，并将其法律与财政基础展开为富裕贵族群体促使罗马重建的征用权、对不愿建房邻地及不合作宗教机构的处置权。授予权力的主体与法律文书未明，不补造。L27中“this tendency”联系到宗教团体的赞助及其教堂建筑/装饰，随后以圣人创立者的精神权威和有钱赞助人之间的冲突解释空间装饰；保留从敌对到几乎不可察觉的连续程度。

- L28–30将艺术家稀缺、教皇及宫廷赞助的私人渠道、第一流艺术家可工作的场所，与Urban VIII时期Bernini、Pietro da Cortona未为Gesù创作重要作品的说法分开；“nothing significant”不改写为完全没有创作。两位艺术家与Jesuits的密切关系分别记断言。只有当全能赞助来源暂时枯竭时，宗教团体尤其Jesuits才得以召请伟大艺术家的条件关系保留；“only when/temporarily/especially”均未删去。

- 保留世俗诸侯优先权的笼统表述。Duchess of Savoy对Ciro Ferri的聘用意愿、她关于其仅有修女相关 engagements 的引语、以及她不认为这些 engagements 会阻止Ferri赴Turin的看法分为三条；job和相关修女团体不具名，不推断正式委托或Ferri最终赴任。脚注1与2分别附在相应正文断言，待后续注释段建立双向链接。

- 新增候选`cand-4986`–`cand-4990`五项，覆盖未具名邻地产权人、贵族征用权、教皇/宫廷赞助群体、世俗诸侯和相关修女群体；新增39条精确跨度提及及19条原书断言。复用既有Roman、religious-order、church、Urban VIII、Bernini、Pietro da Cortona、Gesù、Savoy Duchess、Ciro Ferri与Turin候选，不创建正式关系边。

- 页图校核确认S0中的`St Peter��s`及`Ges��`为OCR乱码，印本分别为St Peter’s和Gesù；`Chiesa Nuova`跨越L32–33。S0及原书引文保持原样，校勘写入记录。L27 OCR连接号乱码对应印本破折号；L30–31的引号/行首杂字符及L29–30的断行不改写原始引文。脚注1、2位于后续注释段L35–43；该段未处理前保持pending。

- 覆盖更新为reviewed/complete，来源范围L27–33。全书变为115段reviewed、25段excluded、659段queued；候选4,988条、提及4,331条、原书断言2,201条。第3章为4段迁移、3段排除、39段queued。结构审计无错误；仍有两条既存enrichment来源定位警告及全书未完成/语义质量待核警告。下一段为`chp-3:03_CHP-3_sec_i:l35-43`。



### 2026-09-27：第3章I节注释与II节开篇迁移



- `chp-3:03_CHP-3_sec_i:l35-43`核对印刷页64–65，迁移p64脚注1–5及p65脚注1–3，共新增6个书目/出版物候选、25条提及和12条原书断言。将Cozzi对相关观点的“有力但未必决定性”反驳保留限定；Van Dyck/Rubens归属和年代判断分层；Bentivoglio、Pastor、Delumeau、Claretta等只作书内引文定位，不当作外部核验。脚注对既有正文断言回链，印本显示与OCR差异保留在校勘记录。

- p65脚注3（Pecchiai, 1952）对应下一节L3建堂句，已完成跨节回链；脚注所引作品标题和版本仍未核实。

- `chp-3:03_CHP-3_sec_ii:l1-1`为自动生成的节标题，排除且不建提及或断言。`l3-4`核对印刷页65，新增候选`cand-4997`（仅称Clelia，身份细节待决）及`cand-4998`（未具名的Farnese家族宫殿）；复用Gesù、Jesuits、Alessandro Farnese、Rome、Vignola和Counter Reformation候选，写入18条精确跨度提及与7条原书断言。

- L3–4保留Haskell对Farnese权势的描述、1568年赞助开始时的正面预期及随后出现的缺点；“把教堂视作私产”记录为作者表述，不断言法律所有权。对“最美的三件物品”明确标成未具名说法，宫殿尚未与索引的Farnese Palace合并；“spiritual confusion”为Haskell的解释。段末停在“as”，不补写后文。

- 迁移后全书S2为117段reviewed/complete、26段有理由排除、656段queued；候选4,996条、提及4,374条、原书断言2,220条；第3章为6段reviewed、4段排除、36段queued。`audit_tables.py --summary`结构错误0；两条既存enrichment来源定位警告不变。下一规范段为`chp-3:03_CHP-3_sec_ii:l6-17`。







### 第3章II节 L6–17 语义迁移（2026-09-27）



- 逐行核读规范段`chp-3:03_CHP-3_sec_ii:l6-17`，核对`CHP-3.pdf`物理第4页（印刷页66）。L6为页码导航，L7–16为正文，L17为页66脚注1的尾句。L7–8续完前段“as”引出的让步结构；把Muziano受托为Gesù高祭坛绘制《Circumcision》、de Vecchi壁画组及原计划的后殿马赛克分开记录。保留Haskell对“grandiose”的判断，以及Farnese于1589年去世、装饰工程几乎未开始的叙述时序。

- 逐项记录Farnese死后工程停止、家族为侧堂预留的权利与后嗣同意要求、后嗣兴趣不足和Jesuits数代无法推进装饰；不把家族保留权改写为已经发生的所有权转移。记录女性虔敬者及Caetani、Mellini等家族提供资金、Jesuits选择装饰题材和邀请艺术家的分工；区分老罗马家族与新兴财富群体。Pulzone、Ciampelli、Zuccari、Valeriano等引入过程与Haskell关于Valeriano节省开支、借此营造“mystery and power”的解释分开。

- 保留Baglione抱怨Gesù装饰方案的叙述层级：其向未具名教皇陈情，并转述教皇以财政不足和既有承诺作答；不猜定教皇身份或将引语当作逐字档案记录。关于1623或1663年访客、缺少Bolognese作品、装饰效果“a little bleak”及Gesù面向公众礼拜/Jesuit novitiate与传教任务的对照，均保留原作者的假设、限定及评价。复用已有Jesuits、Rome、Farnese、Muziano、de Vecchi、Orsini、Pulzone、Ciampelli、Zuccari、Valeriano、Baglione、S. Stefano Rotondo和Gesù候选；新增`cand-4999`–`cand-5016`共18个候选，写入56条提及、26条原书断言。

- 页图校核确认OCR表面形`Meliini`、`Ciampelh`、`men Eke`、`estabEshed`、`fmancial`、`halfcompleted`对应印本`Mellini`、`Ciampelli`、`men like`、`established`、`financial`、`half-completed`。保留原始S0及`original_quote`，将规范读法用于实体和校勘说明。

- L16末尾“which they had been”在L20“allotted by Gregory XIII”续接，关联断言已跨段链接；因此本段仍为`reviewed/partial`，待L19–31处理并闭合句子。L17脚注1尾句“Spirito: Rom. 143, f. 251.”须与注释段`l144-179`的L145注头相接；页66脚注2、3分别在L146–147，相关正文标记均暂列待回链。复核后全书S2为117段complete、1段partial、26段excluded、655段queued；候选5,014、提及4,430、原书断言2,246。结构审计错误0，两条既有enrichment来源定位警告未变。下一段按序为`chp-3:03_CHP-3_sec_ii:l19-31`。





### 第3章II节 L19–31 语义迁移（2026-09-27）



- 逐行核读规范段`chp-3:03_CHP-3_sec_ii:l19-31`，对照整章OCR `03_CHP-3.md`及`CHP-3.pdf`物理第5页（印刷页67）。L19仅为页码导航，正文L20–31；整章OCR主文与分节S0相符，重复脚注不从整章副本另行迁移。印本确认L22姓名为`Nicolò Circignani dalle Pomarance`（分节OCR为`Nicolo`，书内索引候选写作`Niccolò`）；在S2中保留原OCR表面形，将标准拼写交身份阶段核定。`Giovanni Battista Fiammeri`在S0跨L25–26断行，提及拆分为可复现的两段跨度。

- 记录S. Stefano Rotondo句子在上一段L16开启、于本段L20完成；句中“they”承接Jesuits。分别记录Gregory XIII对该教堂的分配和随后所称“given to the German college”，不补写受赠者、授予者或转移时间的历史关系。Rector被写为匿名候选；Circignani受托创作的未具名殉道壁画组作为work登记，画中殉道大多发生于late Roman empire的说法保留“mostly”限定。Venetian High Renaissance仅作为Haskell对题材的解释性评价。

- 记录Jesuits计划在S. Vitale采用S. Stefano Rotondo的处理方式；分别登记Clement VIII将S. Vitale交给Society、Fiammeri主持装饰、General Claudio Aquaviva直接控制并提出建议。酷刑题材的比例、与前代装饰之间的宽松氛围、初看似田园风景的效果、十九世纪Gaspard Poussin归属、树上殉道者/远谷受刑士兵，以及仅在choir中显示的精细刑具描绘分为独立断言；Poussin仅作为历史归属记录，不视作本书确认的作者。

- 记录Jesuit赞助贡献有限及经费短缺的作者判断，S. Andrea al Quirinale和S. Vitale装饰受阻、Aquaviva通信谈筹款（卖珠宝、募赠款）的陈述分别落账。“austerity could, if necessary, be turned to good account”保留条件语气。L30–31记Louis Richeôme于1611年写书并题献Aquaviva；L31止于“about the”，论题留待L33–38续接。六个页67脚注标记均待L144–179注释段核对和回链。

- 新增8个候选（`cand-5017`–`cand-5024`）、36条提及与26条断言。`l6-17`的未完句已与本段L20相连，但其p66脚注1尾段仍未闭合；本段L31及脚注未完，覆盖状态为`reviewed/partial`。全书当前117段complete、2段partial、26段excluded、654段queued；候选5,022、提及4,466、原书断言2,272。下一段`chp-3:03_CHP-3_sec_ii:l33-38`。





### 第3章II节 L33–38 语义迁移（2026-09-27）



- 核读规范段`chp-3:03_CHP-3_sec_ii:l33-38`，对照整章OCR及`CHP-3.pdf`物理第6页（印刷页68）。L33为页码导航，L34–38为正文；平行OCR没有需另行摄入的独有主文。L34的“paintings in S. Andrea and S. Vitale”补完L31“about the”，已更新Richeôme书候选为1611年、题献Aquaviva、论及两处教堂绘画的未具名著作。p68脚注1、2仍在规范脚注段L144–179等待处理。

- Richeôme对浮华装饰的反对、法文引文所称建筑构件和装饰不触及虔敬、专注壁画题材并将其如布道般阅读的主张，分别记录为被Haskell转引或概述的观点。Haskell把这种立场写成Counter Reformation较严峻时期的“last, lonely voice”，并认为它能为不受欢迎的简朴辩护，却不太可能成为Urban VIII宽裕、放松时期的主流教义；不把这些评价改成未经限定的客观结论。

- 记录Haskell对17世纪前二十年Oratorians与Jesuits艺术贡献的比较，以及Oratorian选人/启发带来的品味与崇高感；同时保留他对Jesuit领导者缺少审美细腻度、St Philip Neri敏锐响应绘画音乐、吸引cultivated spirits并热心参与教堂装饰的对照判断。区分St Philip Neri的旧S. Maria della Vallicella与被拆除后重建、常称Chiesa Nuova的较大建筑。

- 旧教堂1575年由Gregory XIII交给Philip Neri；位置、空间不足及拆建分别记录。早期传记把拆教堂而无筹款把握说成对神意的信任、并把民众捐献写作回应；Haskell称故事并非完全准确，指出严重财务困难及Cardinal Farnese因嫉妒潜在竞争者而阻挠。传记故事、作者校正、对新教堂不依赖单一赞助人的解释分开，不将慈善故事全部判真或判假。

- 记录Philip与Oratorians选定的Matteo da Castello合作、Chiesa Nuova与Gesù大致沿同一总体建筑线索、1575年Alessandro de’ Medici以Florence Archbishop及未具名Grand Duke使节身份奠基，以及初期施工进展快。L38句末“However, the usual financial”未完，后续困难不提前迁入，待L40–52闭合。

- 印本校核并记录S0 OCR差异：`simphcity`→`simplicity`、`Efe`→`life`、`reEgious`→`religious`、`S. Maria deUa Vallicclla`→`S. Maria della Vallicella`、`budding`→`building`、`caUed`→`called`、`unEmited`→`unlimited`、`goodwiE`→`goodwill`、`aU-powerful`→`all-powerful`、`St PhiEp`→`St Philip`。不改原OCR和`original_quote`。新增5个候选（`cand-5025`–`cand-5029`）、53条提及及23条断言；覆盖仍是`reviewed/partial`，正文尾句和p68脚注1–2待续/回链。此前L19–31的书目句现已闭合，但p67脚注1–6仍待L144–179。全书现为117段complete、3段partial、26段excluded、653段queued；候选5,027、提及4,519、原书断言2,295。下一段`chp-3:03_CHP-3_sec_ii:l40-52`。





### 第3章II节 L40–52 语义迁移（2026-09-27）



- 逐行核读规范段`chp-3:03_CHP-3_sec_ii:l40-52`，对照整章OCR `03_CHP-3.md`及`CHP-3.pdf`物理第7页（印刷页69）。L40为页码导航，L41–52为正文；整章OCR主文与规范S0相符。L38的“However, the usual financial”在L41续为“difficulties soon intervened”，更新上一段断言的跨段指针，并记录困难使Oratorians转向赞助人。

- 区分Pier Donato Cesi受Farnese影响、出资完成Chiesa Nuova并要求比照Gesù的权利、Cesi arms展示和家庭在Congregation中的特权条款、条款被接受及Cesi对工程介入较少。记录Angelo Cesi（Bishop of Todi）在兄长1586年去世数年后继续家族赞助；另记Oratorians仍大体掌握教堂事务。保留作者对影响、嫉妒及介入程度的叙述层级。

- 登记Martino Longhi the Elder替代Matteo da Castello；主结构在1590年完成，Fausto Rughesi立面另迟十六年建成；Philip Neri要求墙面与拱顶只刷白、不做灰泥装饰，审美或经济动机不明。将高坛与横堂祭坛分开，分别连接圣母诞生、圣母奉献和圣母加冕等奉献主题。

- 记录1582年Oratorians委托Barocci为Visitation chapel创作未具名祭坛画，原文仅说四年后到达Rome，不计算到达年份。Haskell对画作质感及其对Philip的吸引力保留为作者评价；“We hear that”引出的ecstasy及驱离观看妇女等内容记作转述/叙事，未当作独立证实的心理史实。另区分未能从Barocci取得的《圣母加冕》祭坛画与实际委托的《圣殿献耶稣》，不推断前者是否另有版本。

- 记录Pomerancio受Congregation欢迎、其Philip肖像和Domitilla祭坛画；Nereus、Achilleus为独立人物候选，Baronio的titular church仍保留未识别身份。记录匿名富有家族负责chapel装饰、Haskell对其影响Chiesa Nuova“Oratorian taste”的解释、许多新赞助人的Florentine身份及画作有时具有较高水准。L52的“Some years ago”开启Animuccia引文但本段未识别其作者，待l54-60续读。印本页69在L50的“open,”后有脚注1，S0 OCR未识别标号；待L144–179核对并回链，不预设注释行。

- 新增21个候选（`cand-5030`–`cand-5050`）、63条提及和37条原书断言。覆盖记为`reviewed/partial`（L41–52）：正文末句未完成，p69脚注1未链接。L33–38财务句已续完，但p68脚注1–2待L144–179；p66/p67脚注仍待同一注释段处理。全书为117段complete、4段partial、26段excluded、652段queued；候选5,048、提及4,582、原书断言2,332。`audit_tables.py --summary`结构错误0；仍有两条既存enrichment来源定位警告。下一段为`chp-3:03_CHP-3_sec_ii:l54-60`。



### 第3章II节 L54–60 语义处理（2026-09-27）



- 以分节S0 03_CHP-3_sec_ii.md为规范文本，逐行阅读L54–60；对照印刷页70／PDF物理第8页及整章OCR。页码行L54不迁实体。L55接续L52“wrote the”后完成Animuccia引文。印本为Laudi，分节OCR为Landi；以页图确认校读，但保留S0原文和提及表面跨度。区分Animuccia对两本未具名Laudi书的描述、其创作限制与Haskell的解释；不推断书目版本或具体出版日期。

- L56–57记录Vittrice约1601年委托Caravaggio《基督下葬》、未识别的家族礼拜堂及其与St Philip Neri未具名密友的侄甥关系。S0把作品题名识为“The Entombment os / Christ”；印本确认“The Entombment of / Christ”。分别记录Haskell关于Oratorians可能欢迎作品、Caravaggio似乎调整处理方式及委托情况未厘清的语气，不改写为确定心理或委托事实。

- L58记录高坛奉献、Cesi承诺装饰、约1605年多数Oratorians决定移动旧教堂所存的“miraculous” Madonna and Child像、款项被立面支出吸收及Cesi于1606年去世。保留“决定”与“已完成移动”的区别；“its decoration”暂指高坛并明确记为待核指代。S3再核Cardinal Angelo Cesi与L44候选的同一性。

- L59–60记录Serra接触Oratorians、推广Rubens及有条件的300 scudi提议；印本明确为bonus，不改成语义上可能预期的balance。Offer是否被接受、Rubens必须画什么以及完成/安装情况都留给原文续段l144-179 L159；印刷页70脚注1–3分别待与该文件L156–158连接。

- 共新增9候选、55提及、21断言。覆盖为reviewed/partial，来源行范围L55-60。上一段L40–52的音乐引文现已接续，p69脚注1仍未闭合；本段L60句尾和p70脚注未闭合，因此未将跨段承诺或脚注标为完成。下一段按序为chp-3:03_CHP-3_sec_ii:l62-72。



### 2026-09-27 第3章II节 L54–60 与 L62–72



逐段核读正文、对照分节OCR与CHP-3.pdf印刷页70–71（物理页8–9），并保留S0原文和引句。L54–60的Animuccia引文由L52续入，确认印本为“Laudi”；p70脚注1–3待核。L60的“But Serra”待L144–179 L159续接。新增cand-5051–5059、55条提及、21条断言。



L62–72核对了1582年遗赠、Theatines受赠旧址及新建教堂、Gesualdo指定建筑师、Peretti-Montalto接手工程与Maderno进场。教堂身份保持未决，不与S. Andrea della Valle合并；被提议的建筑师不猜名。PDF印刷页71确认正文与脚注定位。新增cand-5060–5063、54条提及、19条断言。L72“work proceeded”已在L74–75续接；p71脚注1–2仍待L160–161核对回链。两段均保留partial状态，尚有脚注链未闭合。



### 2026-09-28 第3章II节 L74–81



核读L75–81并核对印刷页72/PDF物理第10页。保留S0 OCR原貌，在断言限定中记录印本1621、their、enough的校读；L72句尾由L75续完。迁入礼拜堂赞助、委托竞争、艺术家分工、穹顶及后殿图像和Haskell的评价；图像内容与作品、空间分开。脚注1–3仍待l144–179核对，因此覆盖为reviewed/partial。常规表审计0结构错误，仍有既存两条enrichment source_ref警告；阶段未达到S3交接条件。





### 2026-09-28 第3章图版13图注



S0段`l83-84`对应CHP-3.pdf物理第11页图版13。印本确认作品题注在“Glorification”后无逗号；沿用章前图版表已登记的作品/艺术家/题名人物候选，避免重复对象。覆盖已完成，下一段依源序为l86-87。



### 2026-09-28 第3章II节图版14–16题注 L86–100



逐段核对S0分节文本、整章OCR及`CHP-3.pdf`物理页12–14。L86–87印本为Plate 14，题注读作“Gaulli: Triumph of Name of Jesus on nave of Gesù”；S0中的Gaulle及紧连题名为OCR差异。印本另有“JESUIT PATRONAGE OF THE ARTS”组题和“see Plates 14, 15 and 16”交叉提示，作为版面导航元数据，不增作历史断言。沿用作品、艺术家、Jesus及Gesù候选，仅新增Gesù中殿空间；5条提及、3条断言，complete。



L89–90为Plate 15。印本题注为“Andrea Pozzo: Modello for fresco on vault of S. Ignazio, Rome”；S0将`of`识作`o£`。复用Pozzo、modello、S. Ignazio与Rome候选，另建实际壁画候选以保持设计模型与执行作品边界；不由图注推定壁画作者。5条提及、4条断言，complete。索引子项“work in S. Ignazio”留待S3按身份核对。



L92–100对应竖排Plate 16题注，核对印本物理页14后复原为“Bernini: Interior of S. Andrea al Quirinale”。复用Bernini、建筑内部空间与教堂建筑候选，分别登记内部和建筑；本题注不含Rome，地点只在已经处理的图版目录中出现。3条提及、2条断言，complete。



### 2026-09-28 第3章II节正文印刷页73–74 L102–123



L102–113核对`CHP-3.pdf`物理页15及整章OCR，迁入Ludovisi生平与政治位置、1623年教皇选举、Guercino《Aurora》与Pincio赌场、1622年S. Ignazio建堂和选址变更、耶稣会权力、建筑竞赛及不同来源的异说。新增`cand-5075`–`cand-5085`共11个候选、48条提及、25条断言。Bellori引文从L111起未完，连接到下一段L116；印刷页73脚注1–5未在此规范段完整出现，保留partial并待L144–179逐注核对。



L115–123核对`CHP-3.pdf`物理页16／印刷页74。印本读作L119 `life`（S0为`Use`），L121–122 `Collegio`（S0为`Coliegio`）；S0及`original_quote`不改。Bellori叙述的几幅图稿、Domenico提出的两个模型，与匿名十八世纪记载所说Domenichino提交的两份设计分开登记；“Jesuit sources”也单列为未识别文献候选，不映射成耶稣会机构。Jesuit sources与匿名十八世纪记载在是否提及Domenichino及Grassi方案选择过程上并不相同，分别保留。



同段记录Ludovisi继续关注建造、要求建筑师委员会审查Grassi方案、以名义和资金而非实质控制为主的作者判断，以及临终前再留给Society 100,000 ducats；区分Gesù的设计影响、S. Ignazio面向Collegio Romano学生、侧堂由耶稣会承接赞助和节约开支。记录Pierre de Lattre来自St Omer、1626年进入S. Andrea初院、两年后进入Collegio Romano并于1683年去世；其讣告归属、1638年起的账簿记录、圣器室穹顶壁画、六幅侧堂画、后殿内墙仿祭坛及Haskell对存世作品的评价分别保留。新增`cand-5086`–`cand-5105`共19个候选、52条提及和27条断言。



印刷页74脚注1引Soprani；注2引Gerolamo Nappi手稿及Bricarelli；注3涉及Pollak、Libro Mastro A、Jesuit Archives和Hibbard；注4再引Libro Mastro A及Galassi Paluzzi。来源内容先记录以供注释段对照，正式文献映射与脚注回链待L144–179处理。L123止于“and”，公共开放及未完成状态续于L125–135，故本段为partial；未生成正式关系边。



### 2026-09-28 第3章II节印刷页67脚注1–6（L148–153）



逐行核读注释L148–153并对照`CHP-3.pdf`物理第5页。脚注1的Armellini卷I第160页回链至Gregory XIII将S. Stefano Rotondo分配给Jesuits的正文断言。脚注2的Jesuit Archives MSS. Rom. 185, f.25讣文题为P. Michele Lauretano，注记作者P. Fabio de Fabiis及1610年8月6日，并引述其关于教堂殉道图像、说明文字和S. Stefano Rotondo的说法；印本读`altri`，S0 OCR误作`akri`。同注另引Rom.188, I, ff.81–82匿名拉丁传记，称同一堂区长的做法被其他Jesuit churches沿用。Haskell写作“same rector”将该指代连到正文未具名的German College rector及Lauretano；作为书内身份回指保存，外部身份仍交S3核定。



脚注3仅引Huetter e Golzio，链接到Clement VIII将S. Vitale交给Society的句子；出版物完整身份待书目段确认。脚注4为Aquaviva致Fiammeri、1599年8月22日信，称由Pirri 1952年第4页刊布，分别记录信件与刊布来源并回链至Aquaviva介入装饰方案的断言。脚注5引P. Ottavio Novaroli在Jesuit Archives的Historia Domus Professae Romae记述（Rom.162, ff.2–184；写作约1606–1612），并记录其称先前的小S. Andrea被拆除以建Bernini教堂；将两座建筑分开表示，不推定正式题名或奉献连续性。脚注6引同档案机构MSS. Med. 22，S0页叶串`f. I432`与页图末尾上标样标记未能可靠判读，保持未决。



迁入7个引文/档案候选、2个人物候选与1个替代教堂候选，共11个候选；18条提及与12条断言写入S2表。对提及字符偏移、源行原文、候选外键和正文断言ID逐项核验；清除L19–31内脚注1–6的pending标记后将该段改为complete。L144–179混合段仅新增已处理源行范围L148–153，仍因L154–158及L160–179未处理而保持partial。



### 2026-09-28 第3章II节印刷页68脚注1–2（L154–155）



对照`CHP-3.pdf`物理第6页核读注释L154–155。脚注1引Richeôme第21页，并限定这些教堂面向Jesuit novices而非一般公众；分别链接至S. Andrea与S. Vitale的用途断言，复用既有Richeôme、两处教堂和Jesuit novices候选。脚注2说明Haskell的Chiesa Nuova早期史叙述取自Strong及Ponnelle and Bordet两部有充分原始来源注释的研究；登记两个来源作品候选，不从注释补造题名。



新增2个候选（`cand-5150`–`cand-5151`）、5条提及和6条原书断言；核对提及字符偏移、候选外键和断言链接。p.68脚注1–2闭合正文段`l33-38`的脚注标记，该段由partial改为reviewed/complete。混合注释段`l144-179`的已处理行范围扩展至L145–155、L159及L166；L156–158、L160–165及L167–179仍待逐条处理并回链。



### 2026-09-28 第3章II节印刷页69–70脚注1–3（L156–158）



对照`CHP-3.pdf`物理页7–8。p.69正文在Cardinal Baronio titular church所藏Domitilla祭坛画描述后确认有脚注标记1；该注释文本印在p.70页底，列Friedlaender第187页与Cozzi第51页，且p.70 Caravaggio委托未明一处也标1。注释没有说明两条书目各自支持哪一段，故将两条引文都链接至这些正文断言并保留未分配的范围；Friedlaender复用已有Caravaggio来源候选，Cozzi按当前仅有的姓氏与页码建立候选，留待书目阶段核同。



p.70脚注2仅写Jaffé，链接至同页高坛圣像迁置决定和装饰经费被立面成本吸收的断言；题名和年份未补写。脚注3称Monsignor Giacomo Serra也是年轻Guercino的赞助人，引用Mahon 1947年第67–71页；复用既有Mahon 1947来源候选、Serra和Guercino实体候选，记录一条书内关系候选，明确未独立查验被引研究，也未生成S6正式边。



新增2个来源候选（`cand-5152`–`cand-5153`）、6条提及和5条原书断言。核对源行、字符偏移、候选外键、脚注链接和所连正文断言；清除L40–52脚注1与L54–60脚注1–3的pending标记，两正文段均由partial转为reviewed/complete。`l144-179`已处理范围扩展为L145–159及L166，L160–165、L167–179仍待处理。





### 第3章印刷页71–73脚注补录与回链（2026-09-28）



对照`CHP-3.pdf`物理页9、10、15并逐行核读规范源L160–167。页71脚注1引Cozzi第46页及Ponnelle and Bordet第343页；S0 OCR为“Formelle”，印本确认“Ponnelle”，仅在校勘和引文说明中修正，不改写来源转录。页71脚注2引Ortolani及Hibbard（1961）第289–318页。页72脚注1引1608年4月30日Avviso（经Orbaan 1920，第107–108页转引），脚注2引Passeri第45及148页，脚注3引Pastor第XIII卷第965页注3。页73脚注1引Pastor第XIII卷第445页，并以Felici指向Ludovisi收藏资料。以上均作为原书引文定位，不视为独立查证；对应正文断言均已链接。



印刷页73脚注5实际标号为5；S0 L167的OCR误识为8，保留源转录并记录印本校读。该注引Bellori第350页，并称Pope-Hennessy（1948，第121页、第1741号）刊出一幅Domenichino素描，Haskell认为它可能与S. Ignazio项目有关。新增Bellori未定版本来源、Pope-Hennessy 1948来源和独立素描三个候选；素描与Bellori所述多幅图及十八世纪记载的两份设计保持区分。该“可能关联”保留为原书关系候选，不生成正式边。



共新增3个候选、6条提及和3条断言；逐项核对L160–167的源行、字符偏移、候选外键及正文断言链接。p.71脚注1–2闭合L62–72，p.72脚注1–3闭合L74–81；p.73脚注5及视觉转录的脚注2–4闭合L102–113，包括跨段Bellori引文。混合注释段L144–179现处理至L167，L168–179仍待处理。全书当前为130段complete、4段partial、26段excluded、640段queued；结构审计错误0，另有两条既存enrichment source_ref警告。





## 第3章页74–76脚注与第IV节开篇（2026-09-28）



处理L168–179全部脚注并将注释回链到对应正文断言；L179注3跨到sec. IV L3，故与该段一并迁入。纸本页74–76用于核对档案题名、引文、页码及Gesù拼写；校勘写入断言限定和候选说明，未改写S0文本。L177 Sapienza appointment保留为Borromini正式委任的一条具体补充，不消解作者关于其整体上较少获得官方委托的概括。L179把比较范围、其他修会教堂、S. Carlo ai Catinari装饰、Cardinal Borghese及未具名Guido Reni pupil分层记录，相关身份和关系保持待对齐/待裁决。



sec. IV L3–6迁入并区分Urban VIII去世时点、三座耶稣会教堂的装饰状态、Capuchins接受Barberini赞助、Oratorian/Jesuit比较、Pietro的sacristy fresco、委托受阻、Pitti/Florence背景及1646年请假与Medici承诺。句尾“cupola of the”跨至L9，覆盖保留partial，下一处理段为L8–14。新增23个候选、67条提及、41条断言；扫描校读未覆盖或改写原OCR。





## 第3章印刷页77正文（2026-09-28）



核对CHP-3.pdf物理页19。L9续完第IV节L3–6的句子，确认Pietro于1646年11月为Chiesa Nuova穹顶开始绘制cartoons，并据此闭合前段。逐条登记1651年未完成状态、Lanfranco先例、Innocent X宫殿委托与1654年复工、四先知、后殿《圣母升天》、Alexander VII干预、1664年nave vault及其图像构成和Haskell对Pietro的艺术评价；约1700年Padre Sebastiano Resta选择画家完成15幅椭圆场景。区分穹顶、pendentives、apse、nave vault、具体作品和场景组。L14句首另行保留为跨段时间锚点，等待L16–24补完。页77脚注1–2见L190–191，暂待正文/注释回链后收口。新增14个候选、54条提及和26条原书断言。



## 第3章印刷页78正文（2026-09-28）



核对`CHP-3.pdf`物理页20，逐行迁移规范段`chp-3:03_CHP-3_sec_iv:l16-24`的L17–24。L17续完前段L14的时间从句：Haskell说S. Andrea della Valle后来又有装饰；被动句没有把该轮装饰归给Pietro。更新前段`st-chp3-seciv-l8-14-resumption-fragment`并链接本段断言。约1650年Donna Olimpia说服Theatines委托Mattia Preti绘制后殿；记录三部分构图与殉道场景、Domenichino和Lanfranco此前壁画被视为经典，以及Haskell将Preti风格受贬和被迫离开罗马归因于罗马画家的地方偏见。美学评价和因果判断均保留为作者论述。



继续记录1665年Gesù装饰状况与1589年Cardinal Farnese去世的比较、其为家族保留tribune及High Altar装饰、规划未及展开和继承人不积极。Alessandro“the great captain”另存为身份未解候选，不与Cardinal Farnese合并；其子与孙未具名，不猜身份。迁入Gian Paolo Oliva于1661年当选Jesuit General、Courtois/Giacomo Borgognone入会、从Dijon来意大利时年15、与Guido Reni和Michelangelo Cerquozzi交往、军旅及战画声名、妻子约1654年去世和谋杀传闻。传闻保留传闻状态。保留其接洽Siena学院院长、被送信引荐至罗马General、铜版女性肖像转为救世主的第一人称引述、终愿及Jesuit居所。Goswin Nickel与Oliva的General/Vicar身份分别记录；“Oliva把握机会”保留为Haskell明示的推断。



源OCR L20读作`lais son`，印刷页图读作`his son`；L22 OCR读作`Pis tro da Cortona`，印刷页图读作`Pietro da Cortona`。只在断言和候选映射中据图校读，`original_quote`保留OCR字面，未改写02来源。L24以“a series of”截断，内容续至L26–33；页78脚注1–3位于L192–194，均待相应注释段迁入并回链；脚注1只链接Preti风格受贬与被迫离开罗马的断言，不链接约1650年委托句。新增11个候选（`cand-5197`–`cand-5207`）、54条提及和22条原书断言。另据候选表面启发式审计，补记三个既有段落中的提及：L3–4的`Renaissance`及L40–52、L54–60的`Oratorians`；第3章已审段本轮扫描的未覆盖类型候选词面从3处降至0处。该启发式结果只作漏项提示。表结构审计错误0；全书仍有636段queued、2段partial，以及两条既存enrichment source_ref警告。



### 第3章印刷页79正文与L24续句闭合（2026-09-28）



按规范段`chp-3:03_CHP-3_sec_iv:l26-33`逐行阅读L27–33，并对照`CHP-3.pdf`物理页21（印刷页79）；L26仅为页码导航。页79正文转录与扫描页相符，本段不需OCR校改。L27补完L24“painting in the Casa Professa a series of”，把原句连接至新断言；L24–27续句现闭合。



语义迁移区分了Courtois在Casa Professa绘制的圣母主题lunettes/frescoes与基督教战役场景组；Courtois和兄弟Guglielmo为Oliva作画分别记录，另保留继续接受私人委托及将收入交给Society的鼓励，但不推定鼓励者或实际转款。Gesù tribune装饰作为未完成的大型work候选；Jesuit全堂计划与tribune装饰项目分开。保留1671年向Duke Ranuccio开启谈判、许可/资助条件、未具名Duchess与其偏好的未具名艺术家、30,000 scudi支出同意、dome/ribs安全异议、拖延及其“not ready”说法。所有金额、提议、宣称和作者评语按原文限定，未写成项目获批或完工。



Oliva对Courtois的聘用主张、“our brother”引语及Joshua止日题材图稿分别建立断言。Joshua人物、圣经事件、图稿作为不同候选；后文“preliminary sketches”与Joshua图稿的同一性不确定。Jesuits提出将St Ignatius遗骸从High Altar移至左横堂内未具名礼拜堂仅为条件性谈判方案；遗骸是独立物件但当前taxonomy无对应类型，保留未分类候选`cand-5220`，不转成Saint本人或work。另建未具名Duchess、其偏好艺术家、耶稣会书信、十六世纪殉道场景及Haskell所称“Jesuit policy towards the arts”候选，后续对齐和类型判断不在本轮完成。未生成S6正式边。



印刷页79脚注1对应规范注释L195（Pecchiai, 1952, p. 109，关于这些及后续谈判）；脚注2对应L196（Joshua止日题材与Perugia Jesuit教堂Carlone所选题材相同）。两注尚未迁入表，关联断言保持pending；不带名字的Carlone不在此处映射至现有具体人物候选。L8–14和L16–24也仍分别等待L190–191、L192–194注释回链。新增15个候选（`cand-5208`–`cand-5222`）、61条提及和30条断言。覆盖从800段中更新为135 complete、3 partial、27 excluded、635 queued；候选5,220、提及5,265、断言2,676。下一段按来源序为`chp-3:03_CHP-3_sec_iv:l35-46`。





### 第3章印刷页80正文 L36–46（2026-09-28）



逐行核读规范段`chp-3:03_CHP-3_sec_iv:l35-46`的L36–46，L35为页码导航；对照`CHP-3.pdf`物理第22页。印本与S0正文基本相符；S0 L40的`some.trouble`在印本为`some trouble.`，只在校读与断言限定中记录，保持来源转录和`original_quote`不变。



记录Oliva在与Duke of Parma的艰难谈判期间寻找耶稣会完全掌权区域的装饰画家，最初考虑Maratta、Ferri与Brandi；Haskell从风格差异推断Oliva没有预设风格。Oliva见到Gaulli在S. Marta的未具名壁画后把他列为可能人选；Bernini此前曾让Gaulli参与其未具名装饰工作并表示热情。两人同来自Genoa，1672年8月签约。可能人选、此前装饰工作、S. Marta壁画和Gesù工程分别登记，不把“considered”写成委托或完成。



Gaulli生于1639年及其肖像画声誉按Haskell叙述记录。S. Agnese in Piazza Navona的 pendentive figures 因未具名Prince Pamfili的Jesuit confessor认为裸体“lascivious”而被匆忙加衣；Prince与confessor均保持未识别。印本印作“some trouble”，校读不改S0。



Gaulli受托的大型Gesù装饰工程与此前Courtois的tribune工程分开。核实工程空间为dome（含lantern和已由Giovanni de’ Vecchi frescoed的pendentives）、主vault（含window recesses）及两座transept vault（位于St Ignatius和St Francis Xavier礼拜堂上方）；唯一排除的是保留给Borgognone的tribune vault。此处将p.79的“the vault”重映射为该tribune vault，并把`cand-5218`细化为Gesù dome；p.79 Duchess的偏好空间补充指向`cand-5223`，Duke关于dome/ribs的异议仍指向dome。工程范围不混同于已有的de’ Vecchi frescoes或Courtois commission。



按合同语气分别记录Gaulli自付大面积绘画与镀金成本、穹顶两年内完成及其余绘画/镀金/灰泥工作于1682年底前完成的期限、专家认为不完美时免费修正的承诺，以及“if all went well”才支付14,000 scudi并另付脚手架等费用的条件。未将承诺、期限或条件性金额写成实际支付和完工事实。



记录穹顶于1675年4月前ready、四年后主vault完成；受邀专家的私人预展不热情与Haskell所述公众对绘画及灰泥布置的普遍赞赏分别保留。Haskell说Oliva在推进工程时野心增加，并于1679年9月恢复与Duke谈判tribune装饰；其信件引文在L46止于“removed the scaffolding”，续至`l48-56`，此处登记为待续archive引文，不补全文或结论。



本段新增16个候选、57条提及与36条原书断言；来源范围为L36–46。p.80脚注1–6在规范注释段L197–199，尚未迁入并回链，故覆盖保持reviewed/partial；下段按源序为`chp-3:03_CHP-3_sec_iv:l48-56`。未生成S6正式边。机械审计错误0；候选表面启发式扫描28个已审阅段，未发现未登记的已类型化候选词面；此项不代表语义召回或独立验收。





### 第3章印刷页81正文与脚注1（2026-09-28）



核对`CHP-3.pdf`物理第23页。正文L49–54迁入`chp-3:03_CHP-3_sec_iv:l48-56`；页码导航L48不作事实提取。Oliva信件续文与页80 L46片段闭合；将书信中的教堂创设、祖先赞助、tribune权利和完成请求保留为带说话者限定的引述。Gaulli进一步装饰tribune的1679提议、Ranuccio的聘用答复及3,000 scudi（仅报价，为所求十分之一）、未完成的tribune/High Altar、vault上小范围及apse conch绘画、1685年左横堂St Ignatius altar上方绘画、St Francis Xavier chapel未具名装饰者分别记录。区分1672年Gesù合同、Courtois先行tribune方案、建筑空间与作品对象。



Haskell关于三人分工未知、无programme的说法，与口头安排的推测、Bernini角色在史学中的接受、Oliva份额可从iconography推知分别记录；推断保留其语气。关于1670年代Roman Church/Jesuit争论，记录Oliva的General身份、Molinos 1664年到达且目的地未说明、追随者与两项教义，以及Jesuit反对。L54句尾延续至L58–67，保持partial。



脚注1（L55–56）登记未具名avviso及Roma XVIII（1940）第238页引文定位；逐项记录Jesuit dome unveiling报告、Bernini设计、“Baccici Fiorentino [sic]”执行署名与virtuosi批评。S0转录中的“p. 23 8”及印本中的Baccici原样保留，页图支持页码校读但不把被引avviso当成独立核验。Enggass 1957暂作原书引用定位。页81脚注2实际位于L200–201，已标为待处理和回链。



新增14候选、58提及、27断言；关闭页80信件续文指针。coverage为reviewed/partial，源范围L49–56。应用前保留四张S2表的字节级备份。第一次写入检查发现JSONL被输出为数组，立即从备份恢复四表；修正为逐行JSON对象后重写。结构审计错误0、既存enrichment source_ref警告2条；第3章候选表面启发式审计未发现未覆盖类型词面。





### 第3章印刷页82正文（2026-09-28）



核对`CHP-3.pdf`物理第24页，处理规范段`chp-3:03_CHP-3_sec_iv:l58-67`中的L59–67；L58仅为印刷页导航。L59闭合页81 L54“those very spheres”的句子，记录Haskell对Jesuit影响范围、反应及Oliva转向Gesù装饰的解释，保留“no doubt”与“must have weighed”限定。罗马贵族社会群体暂不强定类型；前文明确把争论置于1670年代，该语境下的Papal court候选与既有cand-4241可能同一，留S3身份对齐判断。L60记录争议问题并非完全截然分明；L61区分双方共有观念背景与细部争辩，并记录Molinos尤为看重、但并非新创的Blood of Christ主题。L61–62的`Guida Spirituale`引文保留其作者、被引著作和Haskell转述层级，脚注1待注释段L202回链。



L62–64记录Haskell无法确定Bernini是否从Molinos得知该观念；Bernini关于基督之血力量的说法是经Baldinucci转引，脚注2待L202回链。L63 S0 OCR作“wafs Bernini”，对照扫描页读作“was Bernini”；源文本和原书引文未改写，校读明确附在断言限定中。约1668年Bernini聘人复制一幅血流入无尽海洋的素描：分别登记原素描与版画作品，未识别的etcher仅在断言中保留为行动者，不建立虚构人物候选。



L65记Haskell推测Bernini先建议Gaulli把该主题用于Gesù穹顶，并说相关素描几乎可以肯定与计划有关、现存但未被采用；其脚注3所述Berlin、Düsseldorf图稿及Lanckoronska引文待L203回链。对主题与Molinos关联过深、Jesuits回避神秘主义，以及穹顶可能不适合该主题三种解释分别记录，保持“perhaps”“more likely”等语气；把Haskell对版画与quietism的解释记作作者判断。Gaulli最终穹顶方案的Duplex Intercessio与未采用的Blood of Christ方案分开登记，同时保留二者的图像联系。L65–67记录跪姿Virgin与Christ向上帝为受苦人类求情、十字架由天使承载、Adam和Eve加入祈祷，以及周围圣人与君王敬拜；脚注4关于图像传统的讨论待L204回链，不据此把图像叙述当作历史事件。



本段新增12个候选（`cand-5254`–`cand-5265`）、36条精确跨度提及及19条原书断言；复用Bernini、Gaulli、Molinos、Oliva、Jesuits、Christ、Gesù dome等既有候选。复核所有提及范围、候选外键、19条引文跨度及跨行跨度；L48–56的Molinos prestige句子续接指针由本段L59断言关闭。页82脚注1–4尚未迁入，故本段为reviewed/partial；页81脚注2仍待L200–201回链。应用前为四张受影响S2表保存字节级备份。`audit_tables.py --summary`错误0；两条既存enrichment `source_ref`警告不变。第三章30个已审段的候选表面启发式扫描未发现未登记的已类型化名称词面；此项不代表语义召回或独立验收。全书现为135段complete、6段partial、27段excluded、632段queued，候选5,263、提及5,416、断言2,758；下段按来源序为`chp-3:03_CHP-3_sec_iv:l69-73`。





### 第3章印刷页83–84正文（2026-09-28）



页83核对`CHP-3.pdf`物理第25页，迁移L70–73。记录罗马穹顶悬垂部的圣像群、Gesù中殿壁画的耶稣会传教主题、Gaulli向Pietro da Cortona的Barberini宫殿天顶借鉴、IHS光线构图及十六尊传教区域灰泥像。人物群、图像母题、建筑空间和作品分开记录；Ethiopia、Peru、China、Mexico只是Haskell列举的传教区域，不推广为全体耶稣会传教范围。页图确认L72脚注号为上标1，OCR误作普通`1 :`；L73的`emotionalTcontact`应读作`emotional contact`，区域列举处的连接号按印本理解。保留S0原文，只在证据限定中记录校读。新增19个候选、47条提及及16条原书断言；页83脚注1–2位于L205–206，尚待注释段迁入和回链。



页84核对`CHP-3.pdf`物理第26页，迁移L76–81。分别登记Gesù后殿空间、Gaulli《羔羊的崇拜》后殿壁画、S. Prassede与S. Maria Maggiore的既有马赛克、受难荣耀主题、具体圣像母题、右横堂礼拜堂、Baglione祭坛画、Van Dyck圣人图像及Pietro da Cortona的祭坛图稿。两种解释保持为Haskell提出的可能原因，不互相合并；对中世纪回声、耶稣会内部权力、Negroni的权威和建筑方案的判断保留作者归属。Haskell所说1623年canonisation照录为来源陈述；Duke Ranuccio的“great ancestor”未识别，不猜姓名。页图确认OCR中`ofGaulli`缺空格、`wliich`误识及`The chapel, in the right transept`多余逗号；L80关于1669年逝世后的逗号和连接词与印本相符。S0转录未改。新增15个候选、47条提及及29条原书断言；L81句子续至L83–94，脚注1–4位于L207–210，故本段保持partial。未生成正式关系边。



当前全书S2账本为135段reviewed/complete、8段reviewed/partial、27段有理由排除、630段queued；候选5,298条、提及5,510条、原书断言2,803条。下一段为`chp-3:03_CHP-3_sec_iv:l83-94`。



### 第3章印刷页85正文 L83–94（2026-09-28）



对照`CHP-3.pdf`物理第27页核读规范段`chp-3:03_CHP-3_sec_iv:l83-94`的正文L85–94；L83–84为页码与页眉。L85续完前段L81末尾的“Clement”，确认完整姓名为Clement IX，并与同句的Innocent XI分开链接；前段补入对应的`Clement`提及。记录Negroni令石匠在祭坛正面刻两位教皇徽章、致Oliva信中称已命石匠制作纪念记录；保留引文发言者和“record”未必已完成的状态。记录Negroni后来为Gaulli肖像画坐像、拒绝由Gaulli装饰礼拜堂并改选Gianandrea Carlone和Carlo Maratta，及Oliva在压力下勉强同意；不推定两位画家的作品均已完成。Negroni关于圣髑礼拜开放、奉献者享有礼拜堂权利、耶稣会士负责维护的引语，与Haskell所述耶稣会士愤怒、Negroni固执及其 patron-rights 解释分开；神圣遗物身份依脚注4待迁入。



后半记录耶稣会重建S. Andrea al Quirinale初学院教堂、Haskell对Bernini建筑权威及其与耶稣会理想相契的叙述；分别记录Bernini协助未具名父亲制作Cardinal Bellarmine纪念碑、参与Urban VIII拉丁诗集插图版、其子Domenico关于每周到Gesù的说法，以及Oliva与Bernini的友谊、艺术建议、布道集插图和外交用途。父亲保持未具名；Domenico的姓氏不从亲属关系推定；每周访问与“四十年”保留为Domenico的说法。新增14个候选（`cand-5303`–`cand-5316`）、55条提及和25条原书断言；将`Clement`提及补入L75–81。L85印本为“of the altar”“implications”，L92为“life”，L94为“edition of his sermons”；S0 OCR中的`os`、`impheations`、`Efe`及`ofhis`保持原样，仅在校勘记录中说明。p.85脚注1–6位于L211–216，待注释段迁入后逐项回链；本段为reviewed/partial，不生成正式关系边。



写入后`audit_tables.py --summary`无结构错误；全书135段complete、9段partial、27段有理由排除、629段queued，候选5,312、提及5,566、原书断言2,828。第3章候选表面启发式审计覆盖33段、2,084个词面模式，未发现未覆盖提示；这不是语义召回或准确率验收。下一queued段为`chp-3:03_CHP-3_sec_iv:l96-104`。



### 第3章印刷页86正文 L97–104（2026-09-28）



对照`CHP-3.pdf`物理第28页，迁移规范段`chp-3:03_CHP-3_sec_iv:l96-104`的正文L97–104；L96为印刷页导航。记录Bernini在法国探访耶稣会教堂并表达对耶稣会思想的同情、Oliva对Bernini理解灵性事务的转述、现代历史学家关于Bernini作品符合耶稣会理想的评价，以及Bernini于1658年开始建造S. Andrea novitiate church和他本人对该作的评价。Bernini引语保持第一人称引述，发言者与Haskell叙述分开；其子仅依前段局部语境映射为Domenico，脚注2仍待回链。



分别记录旧Quirinal初学院建筑到1642年据称几乎无法使用、Bandino拒绝出售周边土地、未具名Pope反对遮挡宫殿视线、该限制阻止Ludovisi在该址创立S. Ignazio、Bandino地产取得后禁令仍执行，以及Ceva在1649年同意新建教堂和宿舍并选择Borromini。Borromini图稿与新建项目分开；Innocent X禁止执行图稿。七年后初学院Rector向Alexander VII申诉，后者在确认视线不受影响后批准并鼓励随从出资。未具名Pope、宫殿、Rector和Camillo之子分别保留待识别，不从年代或亲属关系推定身份。将Cardinal Ludovisi希望建造S. Ignazio的未指明场址单列为`cand-5325`，不与Quirinal viewpoint、旧初学院或Bandino地产自动合并。记录Prince Camillo Pamfili与Innocent X的甥舅关系、最大额捐助、家族赞助、其竞争性意图及持续至1665年去世的履行；引语中的宏大承诺保留为意图而非结果证明。



印刷页图确认L100 OCR字面`Tliis`应读为`This`；原S0和`original_quote`保持不改，仅记录校读。新增9个开放候选（`cand-5317`–`cand-5325`）、48条提及及24条原书断言；p.86脚注1–7位于注释段L217–223，尚待迁入并分别回链。L104句末未完，续至下一规范段L106–116的L107；本段保持reviewed/partial，不生成正式关系边。



写入后`audit_tables.py --summary`结构错误0；全书为135段complete、10段partial、27段有理由排除、628段queued，候选5,321、提及5,614、原书断言2,852。第3章候选表面启发式扫描34个已审段、2,093个已类型化词面模式，未覆盖提示为0；此启发式不代表语义召回或独立验收。下一queued段为`chp-3:03_CHP-3_sec_iv:l106-116`。



### 第3章印刷页87正文与脚注5（2026-09-28）



对照`CHP-3.pdf`物理第29页，迁入规范段`chp-3:03_CHP-3_sec_iv:l106-116`的正文L107–113及脚注5的L114–116；L106为页码导航。页图确认S0 OCR的`Pamfdi`为印本`Pamfili`，脚注中的`100 saldi`为`100 scudi`；来源转录与断言`original_quote`保持原样，校勘只记入限定。L107闭合p.86 L104的续句；L113的Guglielmo Borgognone姓名跨行，提及跨度保留规范源段中的换行，并续至下一段L118–128的L119“Giacomo”。



记录Haskell用Camillo Pamfili 1663年探访在建教堂说明工程财务与艺术家权威，Camillo发现费用将高于预期后留下1,000 scudi，其关于遵从Bernini命令的语句保留为条件性引语。Bernini逐项审查账单与合同、监督工人、作为项目实际赞助者并拒绝报酬；Giacomo Borgognone战画及Mattia de’ Rossi以酒、战画和两块旧彩釉陶盘获酬分别保留。陶盘“据说”为Raphael或其学派作品、曾估价50 scudi但可能过高、尚未售出，均保留Haskell的传闻、评价与作者第一人称限定。



记录Haskell对S. Andrea al Quirinale大理石、椭圆平面、Bernini艺术表达和耶稣会用途的建筑解释；St Andrew形象、穹顶采光与鼓座金光的象征、金色putti进入主礼拜堂、阳光照亮穹顶格室的视觉效果分别表达，作者诠释不写成客观测量。页内`Plate 16`只作为插图交叉引用写入教堂描述断言，指向既有室内空间候选`cand-3928`，不新造“图版实体”。St Andrew形象与putti群因具体媒介和可否作为独立作品不清，保留未分类候选。



主结构完成后，Jesuits开始考虑祭坛画并直接安排艺术家；Bernini“必定提供过建议”保留为Haskell推断。作者说艺术家由1667年去世的Prince Pamfili之继承人付款，未具名继承人不推作完整家族。Guglielmo Borgognone于1668年受命为High Altar绘制《圣安德鲁殉难》，此前已与其耶稣会兄弟Giacomo在novitiate工作；Guglielmo使用索引含同作子目的既有候选`cand-0402`，兄弟身份/亲缘仍留给全局对齐和关系阶段核实。



页87脚注5引Jesuit Archives、Fondo di Gesù、N. 865-13，Haskell转述Gaulli经Father Francesco Scaramuccia领取novitiate自有资金100 scudi，并打算向Prince Pamfili收回。新建相应档案候选`cand-5338`和Father Francesco候选`cand-5339`；被引档案未独立查阅，因此只记为原书的档案转引，不当作外部核验。脚注1–4的文本在同一规范注释段L224–227，尚待迁入与回链。



新增14个候选（`cand-5326`–`cand-5339`）、43条精确跨度提及和31条原书断言；p.86末句已闭合，p.87 L113句仍待下一段闭合。本段保持`reviewed/partial`，不生成正式关系边。写后`audit_tables.py --summary`无结构错误：全书135段complete、11段partial、27段有理由排除、627段queued；候选5,335、提及5,657、断言2,883。严格阶段审计仍因全书未完成迁移、partial及queued段而阻止S2交接；该门槛未被绕过。第3章候选表面启发式扫描35个已审段、2,104个已类型化词面模式，未覆盖提示为0；这不是语义召回或独立验收。下一queued段为`chp-3:03_CHP-3_sec_iv:l118-128`。





### 第3章印刷页88正文（2026-09-28）



核对`CHP-3.pdf`物理第30页，迁移规范段`chp-3:03_CHP-3_sec_iv:l118-128`中的正文L119–128；L118为页码导航。L119闭合页87 L113关于Guglielmo Borgognone祭坛画的句子。页图校正L120、L122、L125、L127的OCR粘连/误读，并确认L126脚注号为5而非OCR的6。正文新增23个候选、57条提及和42条原书断言；页88脚注1–5待注释L228–232迁入回链。本段为reviewed/partial。



### 第3章印刷页89正文（2026-09-28）



核对`CHP-3.pdf`物理第31页，迁移`chp-3:03_CHP-3_sec_iv:l130-139`的L131–139。记录圣依纳爵旧居走廊装饰、Jesuit General与Savoy公爵对Pozzo离任的分歧、S. Ignazio穹顶方案与实际帆布幻觉、Mattia de' Rossi的建议，以及Pozzo随后在tribune和apse所作的壁画循环。未具名人物与作者评价保留原范围；较晚传记和转引者不当作独立核验。页图校正L136的`where`；L139比较句续至页90 L142并交叉标引。新增14个候选、64条提及和31条断言；页89脚注1–4待L233–236迁入回链。本段为reviewed/partial。



### 第3章印刷页90正文（2026-09-28）



核对`CHP-3.pdf`物理第32页，迁移`chp-3:03_CHP-3_sec_iv:l141-150`的L142–150；L141为页码导航。L142闭合页89 L139的比较句。记录Pozzo壁画与Gaulli《羔羊的崇拜》的异同、作者对Jesuit接受原因的析取解释、四个pendentive场景及其被报告的含义、早期穹顶方案的形成和Pozzo对穹顶壁画的说明。被引传记作者未具名，脚注仅作待处理引文定位。页图确认L143、L147、L149–150多处OCR差异并保留原始S0；新增19个候选、63条提及和25条断言。脚注1–3待L237–239迁入回链；L149句于L150闭合。本段为reviewed/partial。



### 第3章印刷页91正文（2026-09-28）



核对`CHP-3.pdf`物理第33页，迁移`chp-3:03_CHP-3_sec_iv:l152-163`的L153–163；L152为页码导航。分别记录Savelli继承人持有的St Ignatius礼拜堂、未完成的della Porta祭坛、Ignatius遗骸及Van Dyck为1622年封圣所作图像、Algardi urn、Pietro da Cortona新祭坛、1646年General Congregation纪念方案及其备忘录、Peru遗产与Vizcaya学院计划、Nickel提议和相关传闻，以及Oliva、Noyelle、Tirso Gonzalez时期的纪念工程方案变化。保留“presumably”“seem”“evidently”、匿名传闻来源、未识别的Parma公爵及相对时间；未将计划写成已建成，也未生成正式关系边。页图确认OCR L162 `hot`应为`not`、`Noy elle`为`Noyelle`，L158多余撇号不见于印本。新增19个候选、69条提及和24条断言。页91脚注1–2待L240–241迁入回链；L163未完句续至页92 L166。本段为reviewed/partial。



本次写入后结构审计错误0；两条既存enrichment `source_ref`警告不变。全书S2为135段complete、15段partial、27段excluded、623段queued，候选5,412、提及5,910、断言3,005。第3章为24段complete、15段partial、5段excluded、3段queued；下一queued段`chp-3:03_CHP-3_sec_iv:l165-177`。这只是机械结构检查，不能替代语义召回或准确率的独立评估。





## 2026-09-28：第3章印刷页92正文迁移



对照`CHP-3.pdf`物理第34页，按S0规范段`chp-3:03_CHP-3_sec_iv:l165-177`逐行阅读正文L166–177。L166闭合p.91 L163的句子；L177“the life and”续至p.93 L180。记录礼拜堂工地归属及Savelli家族 patronage 让渡的叙述，区分Jesuit建造权、祭坛位置争议和Pozzo设计方案；将匿名来信的投诉作为转述指控，而非事实；保留Tirso Gonzalez决策、Legros与Théodon雕塑方案、弃置的Doctors of the Church计划及作者评价。未具名皇帝、Jesuit父亲、Parma公爵和法国国王不作身份推定。



PDF页图确认唱词印作“Monsù Le Gros”、姓名印作“Théodon”，L175句首OCR破折号不属于印本正文；来源转录未改。p.92脚注1位于L174，注释L242待迁入并回链。新增22个候选、63条提及、25条原书断言，均锚定规范段；移除p.91 L163断言错误指向当前段的`continuation_to`，改由p.92 L166断言记录`continuation_from`，并将L177续句指向下一段L179–187。写后`audit_tables.py --summary`结构错误0；全书S2为135段complete、16段partial、27段excluded、622段queued；候选5,434、提及5,973、原书断言3,030。第3章为24段complete、16段partial、5段excluded、2段queued；下一queued段为`chp-3:03_CHP-3_sec_iv:l179-187`。两条既存enrichment `source_ref`警告未变；上述结构通过不构成语义独立验收。



## 2026-09-28：第3章印刷页93正文迁移



对照`CHP-3.pdf`物理第35页，按S0规范段`chp-3:03_CHP-3_sec_iv:l179-187`阅读L180–187。L180闭合p.92 L177未完句。保留Haskell的作者判断、匿名旅行者和被引观众的发言层次；记录Legros的Stanislas Kostka卧像、耶稣会对教义装饰和幻觉式艺术的论述、Missionary身份及恩宠/得救主题，以及Chiesa Nuova与Gesù、S. Ignazio天顶的“私密奇迹／普遍主题”对照。页图核实nineteenth-century的行末连字符被S0合并，原始转录不改。脚注1在L181，指向L243待处理注释。



页93底部L185–187位于编号脚注之后的较小文字区，未见单独编号；按原书文本完整记录1697 Pozzo祭坛及Legros浮雕、1749右横堂Annunciation relief、Fabrini引指、1710 Legros墓碑和所引Jesuit Archives档案号，不推断缺失的脚注编号。新增21个候选、50条提及、29条原书断言；50条跨度及候选外键、29条原文锚点均通过写前预检。p.92 L177的续接指针由页码导航L179校正到实际文字L180。写后`audit_tables.py --summary`结构错误0；全书135段complete、17段partial、27段excluded、621段queued，候选5,455、提及6,023、断言3,059；第3章24段complete、17段partial、5段excluded、1段queued。



## 2026-09-28：第3章印刷页77–93集中脚注收口



将规范段chp-3:03_CHP-3_sec_iv:l189-243按印刷页顺序迁移L190–243，新增38个来源衍生候选、100条精确跨度提及和74条原书断言/脚注记录。页77脚注1–2（L190–191）、页78脚注1–3（L192–194）、页79脚注1–2（L195–196）、页80脚注1–6（L197–199）、页81脚注2（L200–201）、页82脚注1–4（L202–204）、页83–93各页全部脚注（L205–243）均链接到正文断言；页81脚注1及页87脚注5此前已迁入并保留原链接。



核对页77物理第19页，确认印本为Briganti与Letter，保留S0的Brigand、I-etter原转录并在限定中记校读；核对页83物理第25页，确认Daniello Bartoli及Della vita e dell'istituto di S. Ignatio，同样不改写来源转录。引文与档案架藏号只作为Haskell的原书引证，不称作独立核验。Oliva早年拟请Pier Francesco Mola装饰、引文所述avviso对Gaulli画作的批评、Bernini/Gaulli Blood of Christ图稿的图像学解释及Duplex Intercessio改编、Carlone在Perugia的身份限制、St Francis Xavier手臂圣髑与跨章指针均分别保留语境。Carlone仍待S3身份对齐；圣髑保持未分类；第6章和附录交叉引用按书内指引记录，不提前补造实体事实。



第3章正文段L8–187现均为reviewed/complete或有理由排除；集中脚注段L189–243为reviewed/complete。写后audit_tables.py --summary无结构错误；全书153段reviewed/complete、0段partial、27段有理由排除、620段queued，候选5,493、提及6,123、原书断言3,133。当前下一queued段为chp-4:04_CHP-4_intro:l1-1。常规结构审计不替代对本批候选召回和断言解释的人工语义验收。



## 第4章开篇 L1、L3–8 语义处理（2026-09-28）



- chp-4:04_CHP-4_intro:l1-1是自动生成的分节文件标题，按格式元数据排除；PDF物理第1页显示原书Chapter 4及章节题名，因此仅排除Markdown文件名，不排除原书题名。

- 顺序阅读l3-8。L3页序标记、L4–5原书章号与题名作为结构元数据保留；L6–8为完整正文段。PDF扫描及整章OCR确认分节OCR的HERE应为THERE，Torders应为orders；不改写S0。

- 新增宗教团体赞助、泛称virtuosi及罗马私人收藏者三个term候选；复用既有Rome、papal court、Amateur、Foreign travellers、Jacopo Ghibbesio与Pietro da Cortona候选。按精确Unicode跨度迁入16条提及，包括religious换行Torders跨行OCR跨度及两处指向Rome的the city。

- 迁入7条原书断言，分别保留Haskell的章节框架、群体概括、收藏趣味、人物例证及重要赞助人的评价标准；未具名的画作和素描不虚构为作品KU。Ghibbesio收藏Pietro作品的表述保存为S2关系候选，因作品未具名不生成正式边。

- 正文L7脚注1标记已随人物描述保留；注释段l10-13尚未迁入，故该段暂记reviewed/partial。下一步按源序处理脚注，分别与Ghibbesio及随后Giustiniani正文回链。



## 第4章开篇脚注迁移（2026-09-28）



按`04_CHP-4_intro.md`规范段`chp-4:04_CHP-4_intro:l10-13`顺序处理脚注1–3，并排除下一分节文件自动标题`chp-4:04_CHP-4_sec_i:l1-1`。脚注1的“him”指向前段Jacopo Ghibbesio，已把Bertolotti/Skippon比较作为Haskell的书目判断记录并链接至人物描述。脚注2复用Salerno条目；扫描页确认印本为1960，S0 OCR字样i960不改。脚注3登记Bottari VI、Michele Giustiniani III和Longhi 1951重印的来源候选，分别记录Haskell报告的首次出版、1630年代假定、Longhi将Romanelli改为Pomarancio的校改、Nicolson关于抄写讹误的口头假说，以及Haskell“可能早于1620”的重估。全程区分文本读法、校改、口述假说与作者推断。



新增7个候选、25条精确跨度提及、10条原书断言；对应表为`entity-candidates.csv`、`mentions.csv`、`book-statements.jsonl`。intro L3–8由partial更新为complete；注释L10–13为reviewed/partial，等待sec_i L3–4的脚注2–3正文锚点。当前全书覆盖154 complete、1 partial、29 excluded、616 queued；候选5,503、提及6,164、断言3,150。下一段为`chp-4:04_CHP-4_sec_i:l3-4`。本次`audit_tables.py --summary`结构错误0；两条既存enrichment source_ref警告未变，另提示全书未完成及该注释段部分迁移。





## 第4章 sec_i L3–4 与页95–96正文迁移（2026-09-28）



- 补记规范段 `chp-4:04_CHP-4_sec_i:l3-4`：对照`CHP-4.pdf`物理第1页（印刷页94）与物理第2页（印刷页95），确认段落跨页。迁入表中的23条精确跨度提及和8条原书断言分别记录Giustiniani收藏、政治归属、趣味形成、致Dirk Ameyden的信和`di maniera`/直接依模作画的对照；脚注2–3来自intro注释L11–13，现已链接到收藏与书信判断。L4末尾的`the Cavaliere`由下一段L7的`d'Arpino`接续，未重复建人。

- 对规范段`chp-4:04_CHP-4_sec_i:l6-18`补做候选词面检查，补录未覆盖的`Europe`、`Duke of Bracciano`和`amateur`，总计现为101条提及、23条断言；前段L15的斯堪的纳维亚旅程句由L21续完，但脚注2–3仍待源注释L43–44回链。

- 对照`CHP-4.pdf`物理第3页（印刷页96），迁入规范段`chp-4:04_CHP-4_sec_i:l20-24`，新增19个正文候选、57条精确跨度提及和17条原书断言。新增未对齐人物/群体/地点/作品及术语均保持open；复用既有Paolo Giordano II Orsini、Monteverdi、Milton、Marino、Urban VIII、Rome、Europe、Jesuits、Ottavio Leoni、Bernini等候选。未将异名或候选重复在S2擅自合并，也未把书内关系写为S6正式边。

- 本段分别记录挪威王位传闻及作者的`probably inaccurate`限定、对Monteverdi的友谊、Baroni诗集、Rosidra乐器、Paolo II诗集、Orsini家族和西班牙派关系、Montegiordano与Bracciano地理、精英通信/任用惯例及作者的推测性评价。Jesuit戏剧引语保留作者、Vallicelliana通信者、轶事中的无名gentleman三层发言；通用群体和未知人物不补造身份。

- PDF核读确认S0 `[Page 9]`实际为印刷页96；L23 `head ofone`应读`head of one`，引语中的`ration di stato`应读`ragion di stato`；L22诗集脚注号印本为5、OCR误作6。原来源文本不改写，以上校勘和不确定性写入限定。p.96脚注1–8位于L45–52，已标记各自关联判断但还没有迁入；其中第3注为Leonora Baroni诗集，第5注识别Paolo II的1649年诗集，第6–7注涉及Fondo Orsini材料与匿名署名，第8注为Leoni蚀刻引证。

- 两个partial段的状态保留：L6–18待脚注2–3回链；L20–24的蜡塑句续至L27，且脚注1–8未迁移。当前下一queued为`chp-4:04_CHP-4_sec_i:l26-33`。写后`audit_tables.py --summary`报错0；第4章typed-candidate surface启发式未覆盖命中0。该启发式不等同召回率或语义验收。

## 第4章印刷页97正文与脚注片段（2026-09-28）



按来源顺序处理规范段`chp-4:04_CHP-4_sec_i:l26-33`，对照`CHP-4.pdf`物理第4页。新增23个来源候选、60条精确跨度提及和23条原书断言；关联L20–24的Bernini蜡塑句续接，并将Christina引文指针连接到下一正文段L35。候选与引文限定保留原文中的“perhaps”、rumours、未识别身份和作品状态，不创建正式关系边。



记录Bernini执导的青铜铸造、奖章及Giulio della Greca的可能归属、Paolo II与Isabella的半身像、Simon Vouet肖像及Haskell外貌评价。Arundel段拆分为1636年写给William Petty的信（身份据脚注5暂连、须随L56迁移确认）、关于Paolo II负债的传闻、以及取得vaso的建议；传闻和建议均未写成已证事实。其余正文涉及Tacca骑马像方案与modello、Claude的《A Storm at Sea》及其格言关联推测、Podestà的Bacchanal版画、Aldobrandini Titians、Jan van den Hecke、十二幅动物蚀刻、奖章收藏、庄园教堂装饰及Paolo II与Queen Christina的往还。Christina的引文跨段至L35，画廊类型保持未定。



L32为脚注1跨注释段续文，另述附录2的四封Bernini相关未刊信；脚注4 L33已链接未识别肖像。脚注1前句在L53，脚注2–3、5–12位于L42–67，均待后续迁移回链。页图核实印本`wrote`对应S0 `wnote`，`Podestà`重音缺失，以及L33脚注号4被OCR误识；S0来源文本不改。写后表格审计错误0，第4章已读段的候选表面启发式检查未发现未覆盖跨度；该检查不替代语义验收。当前全书状态156 complete、3 partial、29 excluded、612 queued；候选5,565、提及6,406、断言3,221。下一queued段为`chp-4:04_CHP-4_sec_i:l35-40`。

## 第4章印刷页98正文迁移（2026-09-28）



按源序处理规范段`chp-4:04_CHP-4_sec_i:l35-40`，对照`CHP-4.pdf`物理第5页。新增17个开放候选、44条精确跨度提及和23条原书断言。闭合前段Queen Christina信件引文；对接续段L36保留女王本人对画廊作品、德国艺术家与Raphael作品的偏好陈述，不把她的主观估价转换成核验藏品清单。扫描确认S0 `Alberto Diirer`对应印本`Alberto Dürer`；原始转录不改，校读写入提及限定。



继续记录Paolo Giordano II向Christina转述Pietro da Cortona、Guercino、Algardi与Bernini的消息；把Paolo报告的艺术家意见与Haskell的叙述分开，把“二人愿为女王工作”保留为作者称作奉承的暗示。记录Christina 1655年来意大利、途经Bracciano赴Rome并过夜，Paolo以音乐会款待、六个月内去世，以及其无名侄辈后来向Don Livio Odescalchi出售Bracciano城堡和地产；未推算具体日期，城堡与p.96湖畔祖堡暂作待核的同一地点候选。



L40分别记录Haskell对Paolo收藏规模的概率判断、未具名宫殿的社交功能、virtuosi/诗人/歌者群体、Barberini侄辈和Marcello Sacchetti的业余艺术家例证、其祖先早数代参与血仇，以及作者关于艺术进入贵族生活、礼仪软化和赞助影响艺术的概括。未把未具名祖先、宫殿、收藏或血仇强行并入已知对象；脚注1–3在后续L64–66，分别待为Christina来访与音乐会、艺术家身份/收藏判断、祖辈血仇补迁回链。页图与OCR相符的其他文字不改写。



本段现为reviewed/complete；脚注L64–66已迁入并与对应断言回链。扫描未发现其他需改写S0的正文差异。



## 第4章页95–98脚注段 L42–67 迁移（2026-09-28）



- 按源序逐条处理25条脚注：页95 L43–44、页96 L45–52、页97 L53–63（脚注4已在正文段L33处理）、页98 L64–67。对照`CHP-4.pdf`物理第2–5页；新增40个来源/文献候选、60条精确跨度提及和28条原书断言/引证记录，并将32个已有脚注引用回链到注释记录。此前页95、96、97、98四段partial均已完成。

- 记录Boyer与Borsari、Solerti、Crescimbeni/Litta与de Bildt、Prunières、Mandosio、Croce/Ferrero等书目指向；不把书目提及当作已读或独立核验。挪威王位故事保留早期记载与de Bildt反驳，不下事实结论。

- 处理Fondo Orsini关于来往信件、1623年匿名通讯与署名、奖章及教堂装饰的档案定位；档案原件未独立检查。扫描校正S0 OCR中的`plorie`→印本`glorie`、`Fonda`→`Fondo`、`II`→`Il`及`Rdthlisberger`→`Röthlisberger`，不改写S0原文。

- L56确认Arundel写给William Petty的信、Ratisbon、1636年9月8日及Hervey页码；这确认代理人身份，不把债务传闻和建议购得vaso升级为事实。L58的《A Storm at Sea》依Haskell所引Röthlisberger说法记为已失、在`Liber Veritatis`第33号有记录、年代可能为1638–39。

- 区分L55两项不同对象的判断：Faldi脚注引作1955、书目列1954，并将Paolo II与Isabella半身像定于约1630；Wittkower说Simon Vouet的Isabella肖像以工作室制作为主、建议年代接近1635。后者不是对半身像年代的直接反驳，Faldi年份异文保留待核。

- L60的Mulier雇主只记作“Duke of Bracciano”，按注释连到Paolo Giordano II的后代身份，不把该公爵认作Paolo II或添加正式关系。L66记录Paolo Giordano I对Isabella de’ Medici的谋杀说法及其启发《The White Devil》的文学说法，均保持为Haskell脚注陈述。L67记Haskell对Cassiano dal Pozzo研究文献的评价并链接Lumbroso书目；目标正文`sec_ii L3–8`尚未处理，故本段保持partial。

- L53的脚注1在S0中分成跨段片段：前段L32保存附录2四封Bernini相关未刊信的续句，L53记青铜失佚及此前未见Bernini文献记载，使用回链而不重复计作另一条事实。另排除`sec_ii:l1-1`自动生成标题；原书第二节正文自L3开始。

- 写后`audit_tables.py --summary`为0 errors，另报告2条既存enrichment source_ref警告、609个queued及1个partial段。当前账本为160 complete、1 partial、30 excluded、609 queued；候选5,622、提及6,510、原书断言3,272。下一段为`chp-4:04_CHP-4_sec_ii:l3-8`。





## 第4章印刷页98第二节开篇 L3–8（2026-09-28）



按源序处理`chp-4:04_CHP-4_sec_ii:l3-8`，对照`CHP-4.pdf`物理第5页。新增3个开放候选、27条精确跨度提及和9条原书断言；复用Cassiano dal Pozzo、Urban VIII、Galileo Galilei、Rome、Turin、Bologna与Florence的现有候选。新候选包括身份未详的Cassiano叔辈（文中称Pisa Archbishop）、Pisa，以及成员未详且被Haskell称作多为Tuscan的Cassiano友人群体。



分别记录Haskell对Cassiano在Urban VIII时期的艺术影响评价、1623年Urban即位、Cassiano在Rome约居住十二年及其知识圈角色、出生和部分教育地、Pisa早年生活、Tuscan身份与友人、从政取向与科学考察，以及与Galileo的友谊。`probably`、`or`、`about`与作者评价均保留；Florence/Pisa不选定为首次相遇地，叔辈不补名，不把S2关系候选写入正式边。Lumbroso脚注L67已连到本段Cassiano居住及知识活动断言，前一脚注段L42–67由partial改为complete。



PDF图像确认印刷页98第二节标题后正文从L3开始；L8以“and in 1621 the”跨页断开，p.99 L11续为科学知识追求对Cassiano其他兴趣的影响。当前段正文已读并迁移可完整判断部分，coverage记reviewed/partial，待下一规范段L10–13闭合该从句。`audit_tables.py --summary`复核0 errors；仍有2条既存enrichment source_ref警告、608个queued段及本段1个partial。





## 第4章印刷页99续文的OCR位置复核（2026-09-28）



PDF物理第6页复核发现，`04_CHP-4_sec_ii.md` L8以“and in 1621 the”结束后，印刷页99实际先续为Accademia dei Lincei组织者提名Cassiano入会及该学会的科学活动两段；规范分节OCR却将这两段放在`Footnotes:`标题下L233，晚于页99后续正文L10–13。整章OCR亦保留正文顺序；故这不是内容缺失，也不新建或改写S0资产，而是分节OCR顺序/分区错位。



先处理L232–236：L233按扫描作为正文续文迁入，L234–236三条引用作为脚注定位迁入；共新增15个候选、34条提及和18条原书断言。记录Cesi与Academy的关系、Cassiano的Lincei提名/入会、自然史材料与科学出版赞助、会员资格规则及该机构与教会冲突的作者论述；保留Haskell的评价与引述限定。扫描校正候选/断言注记保留S0的`Ids`、`pubheation`、`bur` OCR表面，不修改原文件。引文只作为书目定位，不表示已阅读或外部验证。



此前sec_ii L3–8已迁入的段落现可经L233闭合1621年从句，coverage改为complete。当前大段`sec_ii:l232-308`仅reviewed/partial，覆盖L232–236；L237–308尚待脚注语义迁移。`audit_tables.py --summary`为0 errors；第4章候选表面启发式出现12条命中，逐一定位在未审L242、L247、L250–251、L255、L278–279、L301–308，不属于已审跨度，不作漏召判断。



## 第4章印刷页99正文 L10–13 与脚注4–5迁移（2026-09-28）

对照04_CHP-4_sec_ii.md与CHP-4.pdf物理第6页，逐行迁移规范段chp-4:04_CHP-4_sec_ii:l10-13，新增7个来源候选、25条提及和12条原书断言；L13末尾“He was enthusiastically”尚缺L15–22 L16，故该段记reviewed/partial。记录Cassiano对科学研究的兴趣影响、宗教观念的限定判断、赞助活动评价、Alessandro Orsini与Francesco Barberini友谊、Alessandro与身份未定的Paolo Giordano亲缘、Maffeo/Francesco升任后的优待、Barberini家户任职与收益、父亲的婚姻/职业建议及其引语、Cassiano对职位的态度与估计收入。Haskell的评价、seem、estimated、时代标准和匿名亲属均保留限定；不创建正式关系边。

同批迁入原有脚注段L237–238：L237为Lumbroso p.137及1617-08-27信件的书目定位，脚注4继续链接正文父亲引语；L238的Naudaeana et Patiniana (Amsterdam, 1703), p.29及法文注释，新增11条提及和6条断言/引证。PDF确认印本脚注号为5，OCR误作6；法文评论中的地名、年龄、年收入、亲属和婚姻状态均作为Haskell转引的评论记录，不升级为独立核实。Lumbroso p.137候选与脚注2的passim候选分立；未将身份未定的Pisa大主教与L6的Cassiano叔父合并。

补正前段st-chp4-sec-ii-l3-8-cassiano-scientific-investigation的错误续句标记：该句在L8已于scientific investigation结束；L8真正续入L233的是Galileo初识地点句之后的1621年Lincei提名从句。前者解除续接，后者沿用已建立的闭合回链。新增段及更新coverage后，audit_tables.py --summary为0 errors，两个既存enrichment source_ref警告保留；candidate-surface启发式12条命中均在尚待读L242、L247、L250–251、L255、L278–279、L301–308。



## 第4章印刷页100正文 L15–22 与脚注1–3迁移（2026-09-28）

审读sec_ii L15–22及同页脚注L239–241，新增14个候选、54条提及和26条断言/引证；正文18条、脚注8条。页99 L13末句“He was enthusiastically”在页100 L16闭合，因此L10–13从partial改为complete；页100 L22末句止于“embryonic university”，L25仍续“designed as an instrument of study and research”，故L15–22保持partial。记录Peiresc引语、Cassiano性格与肖像描述、1625/1626赴巴黎/马德里任务、Leonardo作品及Fontainebleau观画、Cassiano对绘画的评论、Via Chiavari住所、与Carlo Antonio及Teodora同住、Carlo Antonio受限的赞助评价，以及藏书/博物馆收藏构成与Haskell的大学隐喻。脚注中Dati前页肖像、Haskell/Rinehart inventory条目和Munich drawing分立；Varotari与Leoni两种“Padovano”解释并列，所有作者判断及may/likely限定保留。

页100 PDF物理第7页用于核对脚注3的印刷年份1885（S0 OCR作188$）；Haskell/Rinehart年份印本1960（S0 OCR作i960）。修正本次新增3条脚注提及曾因重复名称而定位到前一注释段的offset，重新锚定到L239–241；此前L232–238的提及与断言行未改。审计后audit_tables.py --summary为0 errors，计数为候选5,661、提及6,661、原书断言3,344；启发式命中仍只落在未读L242–308，不视为当前段漏召。



## 第4章印刷页101正文 L24–31 与脚注 L242–245（2026-09-28）



按源序对照`04_CHP-4_sec_ii.md`与`CHP-4.pdf`物理第8页，新增33个来源候选、49条正文提及、16条脚注提及及24条原书断言（含页100末句闭合断言）。页100 L22的“embryonic university”句由本页L25闭合，故L15–22从partial改为complete；本页L29末句“new precision”续到页102 L34，故L24–31保持partial。



正文记录大陆学者与dilettanti给Cassiano通信、转送自然异闻及地方古物报告；西班牙“腹部长菜”、米兰瘟疫药膏说法和佛罗伦萨出土两尊青铜角斗士均作为转述报告，不写成核实事实，米兰来信“半信半疑”的限定保留。Provence的临摹者、被发掘的卧像与Epicurean铭文、Porta Pia附近S. Agnese的Priapic idol，以及Cassiano从金匠处救回的西塞罗与塞涅卡手稿均按原文登记，未具名对象和地点不补身份。L29–31分别记录Haskell对Cassiano考古严肃性与收藏能力的评价、古物作为历史线索的解释、雇佣年轻绘图者记录罗马遗存、超过23卷的纸上博物馆、现代musée imaginaire类比，以及Vermeule、Blunt、Cooke、Vitzthum对温莎绘画群的研究和归属意见；作者判断与被引学者的归属没有升级为已验证事实。



脚注L242–245迁入三条书目/引证断言并与手稿、Giustiniani财富及纸上博物馆正文回链。L244–245的Dati“23卷”和Carlo Antonio经Lumbroso称“更多”分立为不同报告；引文只作定位，不表示外部核验。页图确认L30印本Blunt and Cooke年份为1960（S0 OCR作i960），脚注印作“Museum Chartaceum”（S0 OCR作“Chartacewn”），不改写S0来源。



页101新增候选33、提及65、断言24；启发式候选表面审计的11处未覆盖命中全部位于未读L247及之后，L242–245无未覆盖命中。`audit_tables.py --summary`结构错误0；仍有2条既存enrichment source_ref警告、604段queued和2段partial。下一queued段为`chp-4:04_CHP-4_sec_ii:l33-44`。



## 第4章印刷页102正文 L33–44 与脚注 L246–249（2026-09-28）



对照`04_CHP-4_sec_ii.md`、`CHP-4.pdf`物理第9页和相邻段账本，按句迁移页102正文并闭合页101 L29末句：新增20个开放候选，记52条正文提及、24条正文原书断言；脚注L246–249另记16条提及和7条引证/关系候选断言。页101 L29的Cassiano获“new precision”判断在L34闭合，故前段L24–31改为complete；页102 L44末尾“When still”在页103 L47续接，当前段维持partial。L232–308脚注段推进至L249，仍为partial。



Baldinucci引文按Haskell嵌套转述记录，涵盖Cassiano五卷纸上博物馆按题材分类与各卷内容；引号中的`[of the ancients]`保留为编辑补充。分别登记梵蒂冈Virgil/Terence古抄本群、Fortune神庙位置、未识别马赛克和明确互指的Preneste/Palestrina，不补手稿号、作品身份或外部地点史。后文保留当代绘画偏好、Simon Vouet在Cassiano处受雇与约1614年到罗马、其作为Caravaggio追随者的声誉、Cassiano支持和作品收藏、约十四幅画作及Caravaggio归属未定画作；Pieter van Laer画作与Viviano Codazzi两幅建筑画分别作候选。Cassiano的“evidently”、Vouet藏画“some fourteen”、Caravaggio归属“attributed”等限定保留。



涉及古典审美的L44拆分为Haskell关于Galileo科学态度的解释、Galileo对Cigoli的“最喜欢的画家”和“偶尔合作者”两项独立关系候选，以及Cigoli引领Florentine artists离开晚期Mannerist style的作者描述；“rational”“naturalistic”保持描述性风格用语，不提升为正式流派。所有正文关系仍是book statement候选，未写S6正式边。



脚注1给出Baldinucci卷页定位；脚注2记录1621年Vouet致Cassiano书信组，并分别记录archive的`authored_by`和`addressed_to`候选；Bottari I及Demonts p.322保留为书目定位，未声称独立核读。Demonts p.322暂与既有p.314候选关联但身份仍待全局对齐。脚注3只给Panofsky姓氏与1954年份；脚注4只以“A. Matteoli”标编辑者，Carteggio与编辑者分立，并保留`edited_by`候选。脚注不作为外部事实核验。



扫描核对印刷页102的`triclinia;`及“to his”前一处印刷横线（S0 OCR拆成`- -`）；保留OCR资产原样并在断言限定中记校读。批量写入前预览通过，写入后`audit_tables.py --summary`为0 errors。第4章候选表面启发式共10条未覆盖命中，均位于尚未处理的注释L250–308；当前正文段未发现该启发式命中。此项只作为定位线索，不等同召回率或语义验收。另有两条既存enrichment `source_ref`警告不属于本批。下一个queued正文段为`chp-4:04_CHP-4_sec_ii:l46-51`。



## 第4章印刷页103正文 L46–51 与脚注 L250–252（2026-09-28）



对照`04_CHP-4_sec_ii.md`和`CHP-4.pdf`物理第10页，迁入页103正文60条提及和22条断言、注释L250–252的9条提及和5条引证/关系候选断言；新增15个开放候选。页102 L44的“When still”由L47闭合，前段L33–44由partial改为complete。页103 L51的Cassiano引语以“Departing”中断，指向L53续文，当前L46–51保持partial。



正文分别记录Galileo的嵌套引语、Haskell对Galileo美学立场的解释、Mannerist群体判断、Haskell所称的1620年代艺术家群体、Cassiano对艺术家的集体性赞助与偶有雇佣、Bernini半身像和素描、Pietro da Cortona绘画、作品费用及Haskell的艺术风格解释。将Cassiano偶尔雇用该群体与教皇/其侄辈的集体性服务陈述拆开，不据此建立每位艺术家与特定雇主的一对一边；两件泛称绘画、未具名叔父和半身像、作品归属、古典建筑评述及各层发言者均保留原文的范围和限定。



脚注1记录Mancini页码及Haskell/Rinehart来源定位；脚注2建立Pietro写给Cassiano的信件组和Bottari卷页，并分别保留作者、收信人；脚注3保留Carlo Dati引文来源。S0显示“Carlo Dari”，PDF印本读作“Dati”；原始S0不改，来源身份和被引作品仍未解决。脚注引证不作为外部独立核验。



写入前预览通过；apply后`python scripts/audit_tables.py --summary`为0结构错误。总账更新为166段complete、2段partial、30段有理由排除、602段queued；候选5,729、提及6,863、原书断言3,427。第4章候选表面启发式扫描15个已读段、2,484个类型化词面模式，8处未覆盖命中全部位于尚未处理的脚注L253–308；该启发式用于定位，不代表语义召回率或独立验收。下一queued正文段为`chp-4:04_CHP-4_sec_ii:l53-63`。



## 第4章印刷页104正文L53–63与脚注L253–254（2026-09-28）



对照`04_CHP-4_sec_ii.md`、`CHP-4.pdf`物理第11页及前后段，处理页104正文和注释1–3。新增21个开放候选、62条正文提及、18条脚注提及和42条原书断言/引证记录；脚注段覆盖推进至L254。页103 L46–51的Cassiano引语末尾“Departing”在页104 L54闭合，前段改为complete；本段L53–63因L63“later in his”续至图版之后L80–81，保持partial。原书对Poussin、Bernini、Sacchi、鸟画及Cassiano收藏的说明按作者判断、来源转述与具体作品分别记载。脚注1–3保留Lumbroso、Passeri和P. Olina引文的来源层级；Skippon关于Cassiano收藏及未署名鸟画的观察不作为独立核验。



本次结构审计错误0；另有2条既存enrichment `source_ref`警告。第4章启发式候选表面审计的8处命中均位于尚未处理的脚注L255–308；该扫描只用于定位，不代表语义召回或独立验收。完成页104后总账为167段complete、2段partial、30段排除、601段queued；候选5,750、提及6,943、断言3,469。下一queued正文段为`chp-4:04_CHP-4_sec_ii:l65-67`。



## 第4章印刷图版Plate 17（PDF物理第12页；2026-09-28）



先核对`04_CHP-4_sec_ii.md`L65–67与`CHP-4.pdf`物理第12页，再迁移图版17a–c题注。a为Bernini对Cassiano dal Pozzo的讽刺像，连接前文已登记的作品cand-5655，并保留图版目录cand-4008供S3核对；b在本页只写“Mellan”，依据同一Plate 17的图版目录将其映射到Claude Mellan候选cand-3749及作品cand-4028；c连接本章正文已登记的Leoni蚀刻肖像cand-5545与Paolo Giordano II cand-0428，同时保留图版目录候选cand-4069、cand-3855等用于S3身份对齐。三项署名均记录为印刷题注陈述，不作为独立作者或肖像身份核验。



新增9条精确跨度提及（每项图像对象、作者、被描绘人物各一条）和6条题注断言（3条caption attribution、3条caption subject），未新增候选。写入前预览验证了全部字符跨度；`audit_tables.py --summary`无结构错误，另有2条既存来源定位警告、600段queued及2段partial。覆盖总账现为168段complete、2段partial、30段排除、600段queued；候选5,750、提及6,952、原书断言3,475。第4章当前15段complete、2段partial、3段排除、18段queued；启发式表面审计为17个已读段、2,505个类型化词面模式、8处未覆盖命中，全部仍在未读脚注L255–308。下一queued源段为`chp-4:04_CHP-4_sec_ii:l69-71`。



## 第4章图版18–20、页105正文及组题补录（2026-09-28）



按源序处理第4章后续图版与印刷页105，并据PDF校对。Plate 18–20题注段L69–78共迁入16条精确跨度提及和11条题注断言，复用现有候选；Plate 19b的S0 OCR“C”依图版页读为Claude，Plate 18b较图版目录多出“The Sacrament of”，作为同图版题名异文保留，不另造作品。图版组题不指派给单件作品，也不转成赞助关系。



印刷页105、PDF物理第16页L80–89新增22个正文来源候选、55条提及及25条原书断言。该段L81补全页104 L63的“later in his life…”句，前段由partial转complete；L89以“do we have”中断并续至L91–99，因此页105段记partial。Haskell关于Cassiano/Poussin、Jean Lemaire、Podestà、Titian、Varotari及作品 subject list 的判断，按作者解释、二手引语、约数、possible/probable和未识别对象分别记录。约50幅是一般估计；Maria-Caterina的身份及“his”所指不确定；旅人提及的Sacrifice不与Sacrifice of Noah合并；Bacchanals不判作者或藏属；landscapes中的神话人物保留为可能性。脚注1–3分别指向尚未迁移的L255–257，当前记为待回链。



扫描校读确认正文OCR的“Cassiano s”“MariaCaterina”“eventhough”“didown”“ir”分别应按印本读为“Cassiano’s”“Maria-Caterina”“even though”“did own”“it”；S0来源文本保持不变。Andrea Podesta的重音依印本记为Podestà。



规范分节OCR未包含PDF物理第13页Plate 18组题及第14页Plate 19–20组题；依既有图版组题补录惯例，新增`04_CHP-4_sec_ii_visual-transcription.md`两个独立S0段。两标题按editorial navigation处置，不建主题实体或与所示作品之间的patronage边。



本次应用后S0共802段（含12个视觉转录段）；S2为174段complete、2段partial、30段excluded、596段queued，候选5,772、提及7,023、断言3,511。`audit_tables.py --summary`结构错误0；2条既存enrichment `source_ref`警告未变。第4章候选表面扫描8处未覆盖命中均在尚未处理的L255–308脚注，仅作定位，不表示语义验收。下一queued段为`chp-4:04_CHP-4_sec_ii:l91-99`。





## 第4章印刷页106正文L91–99及脚注L255–259（2026-09-28）



按源序迁入印刷页106 L91–99及脚注L255–259。正文新增30个来源候选、47条提及和24条断言；脚注新增21条提及和8条引证/断言。页106 L92闭合页105末句，故L80–89由partial改为complete；页106 L99以“Both the”中断，保持partial并续至L101–107。脚注段扩展至L259，页105注1–3现回链L255–257，页106注1–2链接L258–259。



正文与PDF物理第17页对照，限定Poussin的引语、Haskell的解释及二手文献层级；“约”“apparently”“does not seem”不提升为确定判断。保留拟议的Marriage of Peleus主题与Romanelli同名作品分立、两幅未识别肖像及对Mona Lisa副本身份的限定、Cassiano各版本/图稿与寄存馆藏的报告属性，不创建正式关系边。校读os/of、plus pleine d’invention、Trattato della pittura、fine、gauches及1960；S0文本不改。



`audit_tables.py --summary`为0 errors；另有两条既存enrichment source_ref警告、595个queued和2个partial。第4章表面启发式扫描仍有8个注释段定位提示，需随L260–308阅读逐项裁决；该提示不等同遗漏或语义验收。当前总账175 complete、2 partial、30 excluded、595 queued；候选5,802、提及7,091、原书断言3,543。下一queued段为`chp-4:04_CHP-4_sec_ii:l101-107`。



## 第4章印刷页107正文L101–107与脚注L260–264（2026-09-28）



按源序对照规范OCR `04_CHP-4_sec_ii.md` 与 `CHP-4.pdf` PDF物理第18页。页106 L99 的 “Both the” 由页107 L102 的 “general subject…” 闭合，故页106段改为 complete；页107 L107 以 “those” 中断，续至页108 L110，当前段保留 partial。新增5个正文来源候选、25条正文提及和20条正文断言；页107脚注1–5（L260–264）新增7个来源候选、15条提及和6条引证/断言记录。全书累计候选5,814、提及7,131、原书断言3,569。



正文记录 Haskell 对《七件圣事》题材及普桑处理方式的评价、意大利较早组画的单一先例及对 Roberto Oderisi 的保留归属；“Jansenism?”和“Some schismatic sect? Possibly.”保持疑问/可能性，不建未具名教派候选。Cassiano 的创意来源“beyond any reasonable doubt”、较可能参与发展、与 French libertins 的友谊、是否属于该群体“不大可能”及“几乎可以肯定知道其信念”分作不同断言；知情不等于认同。Barberini 的 immediate entourage 与既有更宽泛的艺术/知识圈候选分开。Cassiano 的 jottings 和 Bouchard 的 private papers 作为未具名 archive 候选保存，不据此写正式关系边。



脚注1–5分别回链Blunt 1967页177–207、Pintard书第2章、Naudaeana页8、Peiresc致Monsieur de Saint-Saulveur（1635-01-09）引文及Haskell解释、Lumbroso页207。Pintard书暂复用已有题名未详的出版物候选；Naudaeana复用既有书目候选并保留本注p.8定位。Peiresc引文中的 Cassiano 文稿/Bacon作品关系、`paroles assez libertines`归属均未独立核实；Haskell关于“politically suspect”和Cassiano愿冒教皇海关/警察不悦的解释保留为作者推论。Lumbroso评论仍是Haskell转引。新增未具名信件、出版卷次和文稿均以开放候选交后续身份对齐，不递推出事实或外部核验。



PDF校读：L102 OCR `veryrare` 对应印本跨行的 `very rare`；L107 `cruditissimo` 校作 `eruditissimo`；L263 `datcd'9` 校作 `dated 9`；L264 `aile chiese` 校作 `alle chiese`。只在断言限定中记录，不改S0。页107五条脚注均已和正文断言回链。候选表面启发式的8处未覆盖命中位于L278–279、L295、L301–303及L307–308，均在未处理的L265–308范围内；仅作为后续定位提示。



应用后 `python scripts/audit_tables.py --summary` 为0 errors；`python -m pytest tests/test_audit_tables.py -q` 通过。仍有两条既存enrichment `source_ref`警告、594段queued及2段partial。下一queued段为 `chp-4:04_CHP-4_sec_ii:l109-119`；脚注续按印刷页映射处理L265–308。



## 第4章印刷页108 S2批次（2026-09-28）



对照S0分节 `04_CHP-4_sec_ii.md`、S0片段哈希与`CHP-4.pdf`物理第19页，处理正文L109–119及脚注L265–268。正文L110闭合L107末句，更新前段continuation为resolved、覆盖为complete；本段因L119续至L122保持partial。L112的句首句点、`Continue`大写和行尾连字符按扫描校读；L265的`composites`、`impresses`和尾随引号也记录校读，不改S0。



本批新增17个来源候选，覆盖Carthusian Order、Dupuy未具名兄弟及其书信、所示诗文材料、Bouchard图书馆、Galileo来信/肖像、Arcetri、Inquisition、alchemy/atheism、Naudé题铭肖像组、Bouchard遗嘱及其1886年刊布、Galilei XVIII卷等；随后补入Galileo定罪事件候选。开放候选保留未识别的组织分支、匿名收信人、未定文本及具体作品身份，交S3处理。发现页107的“his library”此前没有独立提及，补候选并在原段锚定。共新增53条提及（含该回补）、28条原书断言/引证记录。



语义上分开保留Dupuy叙述的情绪与Haskell对Cassiano反应的未知/推测；不从“知道”或“友谊”推出信仰认同。Galileo受审、约一年后的友好通信、1641年Arcetri来信及来信所说的图书馆肖像分成独立断言。Dati对Cassiano正统观及反炼金术的论述保留作者“over-shrill”评价和Dati的嵌套修辞；Naudé只作为Haskell提出的另一反应。页108脚注1并列遗嘱转述、Dupuy经Pintard转述与Haskell推测，未据这些不同层次裁定私稿所有权/转让；脚注2–4链接对应的Dupuy、Galilei和Dati陈述。未创建正式关系边。



表格应用前预检来源哈希、字符跨度、ID唯一性和外键；写入前为四张表保存`s2-chp4-p108-20260928`备份。应用后累计候选5,832、提及7,184、原书断言3,597；覆盖为177 complete、2 partial、30 excluded、593 queued。`audit_tables.py --summary`结构errors为0，剩余两条既存enrichment `source_ref`警告；`tests/test_audit_tables.py`为11 passed。第4章候选表面扫描8处命中位于尚未阅读的注释L278–279、L295、L301–303、L307–308，仅作为待读定位。下一正文段为`chp-4:04_CHP-4_sec_ii:l121-128`，注释续读L269–308。





## 第4章印刷页109正文 L121–128 与脚注 L269–274（2026-09-28）



按源序核对`04_CHP-4_sec_ii.md`、S0分段哈希与`CHP-4.pdf`物理第20页。p.109 L122闭合p.108 L119开始的肖像句，故页108正文段由partial改为complete；本段L128以“fundamental”结束，续至p.110 L131，记reviewed/partial。迁入18个开放候选、39条正文提及和19条正文断言；脚注1–6另迁入15条提及及6条引证/断言记录，合计54条提及。新增候选包括1641年《Epigrammata》印本及印刷者、Cassiano—Gaudenzi通信与两个Urb. Lat.档号、Gaudenzi肖像副本及Saracini原作、其早期教会史、所引Lumbroso/Pintard页码、Cassiano绘图卷册和Petau版Julian著作；均保留开放状态，不在S2合并身份或建立正式关系。



正文分别记录Cassiano索取及确认肖像、来信中的Saracini原作归属、Gaudenzi被称作前Calvinist/Grison出身、其对Baronio与Jesuits的态度、教会史结论和教皇宫廷赞助困难，以及Haskell关于Cassiano宗教兴趣、古物图像和绘图卷册的叙述。Cassiano与Gaudenzi书信声音及Haskell叙述分开；Petau序言由Haskell概述，Cassiano卷册目的保留直接引语层级；“no doubt”为作者推断。L128未闭合的“fundamental” inquiry statement明确指向下一段，暂不补出其对象。



页图确认S0 OCR差异：L122 `as'well`→`as well`，L123 `nc`→`ne`，L127 `T would`→`I would`；注L269 `quaes`→`quas`，L273印刷注号为5（S0 OCR作6）。所有校读只写入对应断言限定，未改来源。表格审计`audit_tables.py --summary`为0 errors；两条既存enrichment `source_ref`警告未变；`tests/test_audit_tables.py`通过11项。第4章候选表面启发式仍有8条提示，全部落在未处理脚注L275–308，仅作后续定位。应用后总账为178 complete、2 partial、30 excluded、592 queued；候选5,850、提及7,238、断言3,622。下一正文段为`chp-4:04_CHP-4_sec_ii:l130-137`，脚注续读L275–308。





## 第4章印刷页110正文 L130–137 与脚注 L275–276（2026-09-28）



按源序核对`04_CHP-4_sec_ii.md`、分段哈希与`CHP-4.pdf`物理第21页。L131闭合p.109 L128的“fundamental”句，故p.109段由partial改为complete；本段L137末尾“Yet the”续至L140，状态为reviewed/partial。新增24个开放候选、49条正文提及、19条正文断言；脚注1–2另迁9条提及和2条书目断言。新对象涵盖Poussin宗教作品中的主题、Testa《Flight into Egypt》印本及其未识别的圣经人物/图像对象、Massacre picture与Spada Gallery地点，以及Zeri、Mitchell、Voss的未详引文；所有引用保持开放身份，不由同题或相同作者自动合并。



语义判断保留Haskell的多层限定：Cassiano的“probably sincere if not ardent” Christianity、“libertin” connections；Poussin以历史好奇解释准确性的“probably”；严重/净化图像更合Cassiano的“perfectly possible”；Testa主题是否由Cassiano选择的明确“no proof”；Cassiano是接收者而非积极启发者的“assume”；印本令人联想到西班牙较常见神秘主义的艺术判断。图像细节、Counter-Reformation主题互涉和Testa的Massacre picture分别记录；没有把dedication推成commission，也未创建正式关系边。



PDF校读：L131 `a-kind`→`a kind`，L133 `behed`→`belied`、`rehgious`→`religious`，L134 `Egyptwith`→`Egypt with`，L137行首OCR污点`- -`不属印本文字；只写入断言`ocr_corrections`，S0不改。脚注L275 Bartsch XX p.216连到Testa版画；L276 Zeri 1954、Mitchell 1938与Voss 1957保留为书目定位，未做外部核验。表格审计`audit_tables.py --summary`为0 errors；仍有两条既存enrichment `source_ref`警告。`tests/test_audit_tables.py` 11项通过。第4章候选表面启发式有8条提示，均属于未处理注释L277–308。应用后总账为179 complete、2 partial、30 excluded、591 queued；候选5,874、提及7,296、断言3,643。下一正文段为`chp-4:04_CHP-4_sec_ii:l139-149`，脚注续读L277–308。



## 第4章印刷页111–112正文与脚注迁移（2026-09-28）



页111正文L139–147新增20个正文候选、59条提及和29条断言；脚注L277–279新增10个注释候选、17条提及和3条引证记录。PDF物理第22页确认源OCR L148–149位于脚注区域，是脚注2的续文/评论而非正文；两条相关断言保留原OCR段锚点，改记footnote commentary并回链至注释L278。L147“appeal to”由页112 L152 “Cassiano’s learned circle”闭合，页110 L137 “Yet the”由页111 L140闭合；页110与页111正文均改为complete。



页112正文L152–159及脚注L280–286新增10个开放候选、44条提及和31条原书断言/引证。正文分别记录Testa的未具名Treatise、S. Martino ai Monti后殿装饰计划及其未实现状态、无云图像主张与Haskell的Baroque解释、古典化人物和版画主题、成功与大型绘画失意、自杀叙述及1650年日期、Cassiano对Testa绘画的持有和评价、Cassiano声誉、Urban VIII病逝记载、匿名Cardinal Barberini离任/复职、Innocent X时期仪式退离和1655年Fabio Chigi当选。嵌套引述、发言者、作者判断与“probably/appears”限定分别保留；不据此建立正式关系。



PDF物理第23页校读确认L152 “are based”而非OCR “arc based”、L153行首无多余句点、L159为跨行“Reluc- / tantly”。脚注6的印刷编号为6（OCR作8），读作“famiglia”，完整架号为Biblioteca Vaticana, Barb. Lat. 5635；该档案仅作Haskell引证线索，未实际查阅。页112 L159 “but by now”续至规范段L161–170，故正文与脚注总覆盖仍各有待续。



应用后总账为181段reviewed/complete、2段reviewed/partial、30段excluded、589段queued；候选5,914、提及7,416、原书断言3,706。`audit_tables.py --summary`结构errors为0；`tests/test_audit_tables.py`为11 passed。第4章表面启发式扫描的6处未覆盖命中定位在未读注释L295、L301–303、L307–308（Leningrad、Bellori、Claretta、Rothlisberger、Bottari词面），仅作下一批次定位，不等同遗漏结论或语义验收。下一正文段为`chp-4:04_CHP-4_sec_ii:l161-170`，注释续读L287–308。



## 第4章印刷页113正文 L162–170 与脚注 L287–290（2026-09-28）



先对照04_CHP-4_sec_ii.md与CHP-4.pdf物理第24页。页112 L159的“but by now”由页113 L162闭合；正文本段L170的“or the”续至下一规范段页114 L173“religious Orders”，故分别将页112改为complete、将页113记partial。迁入9个开放候选、26条正文提及和24条原书断言；脚注L287–290迁入3个开放候选、16条提及及5条引证/断言。



正文分别记录Cassiano健康状况与1657年去世、Carlo Antonio存活超过三十年、赞助随政治地位衰退、Urban VIII去世后少有作品可定年、学术与科学活动持续但收藏增长几近停止、古物绘图继续丰富其paper museum，以及Poussin 1642年自巴黎返罗后主要为该行程结识的法国朋友和委托人工作。后文只说“one…picture”表明约束数量，不能把它转成确数；Leonardo《Trattato》及Cassiano早年研究委托、暴风雨的嵌套引文与画作识别、前景悲剧解释、Dughet影响的perhaps、Poussin与Cassiano继续见面但友谊可能冷却，均分层保留Haskell叙述和作者判断。1646年来信者只称Tarso总主教；未完成肖像与“两人”之关系不补身份。



脚注1报告Mahon关于两幅ex-Leon landscapes在Poussin赴巴黎前完成的意见并回指页111注2；脚注2仅回指页106注2；脚注3记录Lumbroso p.314与Haskell/Rinehart 1960；脚注4区分Museum Chartaceum的后续研究与绘画收藏在Carlo Antonio 1689年去世后可能散佚的说法。集合类型不在taxonomy中，不强制归档或作品类型；引证仅作书目定位，不表示已读原刊。扫描核字：正文L162 OCR lais、印本his，L165 grand passage、印本grand paysage；脚注L287 p. in、印本p. 111，L289–290 i960、印本1960。OCR源文件不改。



apply后audit_tables.py --summary无结构错误，tests/test_audit_tables.py 11项通过。候选表面启发式审计共扫描第4章31个已读段及2,673个类型化词面模式，6处提示均位于尚未处理注释L295、L301–303、L307–308，仅作为后续定位。更新当前账本：182段complete、2段partial、30段有理由排除、588段queued；候选5,926、提及7,458、断言3,735。下一步按源序处理页114正文L172–178及注释L291–308。



## 第4章印刷页114正文 L173–178 与脚注 L291–292（2026-09-28）



对照04_CHP-4_sec_ii.md与CHP-4.pdf物理第25页。页113 L170末句由页114 L173“religious Orders”闭合；页114 L178开始列举Massimi所委托的Poussin作品，第一标题的列表/描述续至页115 L181，因此本段为partial。迁入6个正文候选、43条正文提及与22条正文断言/关系候选；脚注L291–292另迁入9个候选、19条提及及5条引证/断言。



正文保留Haskell关于Cassiano趣味不能简化为“classical”或反Baroque、Francesco Angeloni的友谊/考古身份/收藏、对Baroque立场的评价、Cassiano信念和欧洲文化可能影响Poussin、Poussin对Cassiano的承认与收藏评价。约50幅Poussin作品作为集合数量陈述；其他业余收藏者所藏的Vouet、Cortona、Testa作品不拆成未知个体。Castiglione群组图稿及可能来自paper museum的判断，Mola的浪漫风景与Titian审美，Bellori/Félibien后续将Poussin教条化，以及Haskell提出的工作压力/绘画风格两种赞助变化解释分别记录，不把猜测提升为事实。Tempest委托、Poussin的浪漫主义与学识、约两三幅1648–1651年英雄风景复制品单独保留；页114转入Poussin为Massimi绘制两幅作品及Moses trampling on Pharaoh’s Crown标题。



脚注1引用Lumbroso、Correspondance与Mahon 1947，并交叉提示第6章；脚注2引用Rinehart 1961，分别提及Ottawa的Landscape with Woman washing her Feet、Lord Plymouth collection的Funeral of Phocion、National Gallery London的可能Man killed by Serpent版本及其或与Montreal所称原作Man fleeing from Serpent混淆。全部保持Haskell转引层级；群组收藏与Lord Plymouth个人身份未决。扫描核字bythe→by the、Felibien→Félibien、Funeral ofPhocion→Funeral of Phocion、pp.144 if.→pp.144 ff.，不改S0。



表结构审计0 errors；11项audit测试通过。候选表面提示6处均落在本段未处理的后续脚注L295、L301–303、L307–308。当前总账更新为183 complete、2 partial、30 excluded、587 queued；候选5,941、提及7,520、断言3,762。下一步按源序处理页115正文L180–189并继续注释L293–308。

## 第4章印刷页115正文与脚注 L293–294（2026-09-28）



按源序处理规范段`chp-4:04_CHP-4_sec_ii:l180-189`及注释段`chp-4:04_CHP-4_sec_ii:l232-308`中的L293–294；同时闭合页114段L173–178的标题清单。对照`CHP-4.pdf`物理第26页（印刷页115）。页114 statement `st-chp4-sec-ii-p114-moses-title` 的 continuation 已解析到本段第二件作品标题；第一件作品与Plate 19a的上下文保持原候选，第二件另登记正文候选`cand-5946`，不预先与索引候选`cand-2017`合并。



本批新增19个候选、71条精确跨度提及和33条原书断言/引证记录：规范正文段中有12个来源候选、50条提及和28条statement（其中包括L186脚注1及L187–189脚注2的版面延续）；注释段L293–294另有8个候选、21条提及和5条statement。完整新对象及锚点见`entity-candidates.csv`、`mentions.csv`与`book-statements.jsonl`。跨章身份和同名权威留给S3。



语义处理分别记录两件Poussin作品的风格评价与题材评价；第一件Moses trampling on Pharaoh’s Crown的稀见题材、Josephus叙事来源、Poussin未为Cassiano绘制Moses题材作品，以及Haskell由该题材推断特殊赞助人并在上下文中指向Massimi。Massimi的出生、教育、承继和亲缘信息按elder/younger Camillo拆分；Vincenzo关系分成nephew、companion、testamentary executor及经祖母较远亲缘，未推定更具体的亲属称谓。两幅画与Massimi的commission关系各自作为原书断言候选，保留“must have been”的推断及1644政治背景，不填写单件委托日期。Cassiano可能是Marino遗嘱中未具名友人的说法保持不确定，relation endpoint留空；Félibien引文仍作为Haskell转引。Massimi的遗产继承语句不强行确定“distinguished ancestor”的指代。



注释脚注2的书目更正中，“Moroni误称的Massimi传记”与Haskell指出的“献给Massimi的Cardinal Bona传记”作为同一本书`cand-5956`记录，不拆成两个文献；Moroni人物`cand-5954`与未识别出版物`cand-5955`分开。Capponi Lat. 260原始inventory与Warburg Institute摄影副本分别建候选，复制件不等同原件。新建Bible来源候选和Innocent X时期“new court”机构候选；后者不指派具体建筑，均待全局对齐。



注释段L293为脚注2、L294为脚注3；脚注2另在规范正文段L180–189的L187–189续出。已将该版面片段按footnote speaker/text layer标注，与L293的注释2statement回链，没有重复计入。正文L182的脚注1回链L186书目定位；正文L183脚注2链接L293及L187–189片段；正文L186脚注3链接L294的Blunt转引。L295–308属于后续印刷页，仍待与相关正文按源序处理。



扫描确认S0 OCR校勘：L181 `Aaron s Rod`→`Aaron’s Rod`；L182 `very. rare`→`very rare`；L183 `ne Carlo`→`né Carlo`；L186 `Felibien`→`Félibien`；L187印本为`Capponi Lat. 260`（OCR漏`Lat. 260`）；L189 `Archivio di State`→`Archivio di Stato`；L294 `sec Blunt`→`see Blunt`。校正只记入对应statement qualifiers及过程，来源OCR资产未改。书目、档案和年表均为原书引注，未据此声称独立核验。



首次写入后的结构审计指出本批三个coverage行的`source_line_ranges`格式多写了第二个`L`，导致既有statement和候选source ref被误报越界；按表契约修正为`L173-178`、`L180-189`、`L232-294`后重跑审计，结果0 errors。`tests/test_audit_tables.py`为11 passed，`git diff --check`通过；表文件沿用既有UTF-8/LF格式。当前全书为185段complete、1段partial、30段excluded、586段queued；候选5,961、提及7,591、原书断言3,795。两条既存enrichment `source_ref`警告、586段queued与1段partial均仍在，不能交S3。第4章为32段complete、1段partial、3段excluded、4段queued。下一正文段为`chp-4:04_CHP-4_sec_ii:l191-205`；后续继续按对应印刷页处理注释L295–308。





## 第4章印刷页116–119正文与脚注收口（2026-09-29）



按源序完成规范正文段L191–230及注释段L232–308，核对对应印刷页并闭合页间续句；第4章40个规范段现为37段reviewed/complete、3段有理由排除，0段partial或queued。四页批次合计新增46个候选、175条提及和120条原书断言/引证。



页117记录四幅肖像组及法国／威尼斯抗议等政治语境，按断言拆分行为主体，并复用已有France与Lumbroso候选；身份未明的人物肖像不补姓名。页118区分Apollo and Daphne绘画与Bernini雕塑，拆分古抄本、图书馆、收藏和个别作品，保留来源归属与地点未决；扫描核对并记录`os`→`of`、`ceding`→`ceiling`、`fllustrations`→`illustrations`等OCR差异。页119闭合页118末句，区分Massimi与Vincenzo Giustiniani的未说明关系、Massimi与Cassiano的友谊及Haskell对古典古代、当代绘画与学术启发的论述；不把共现或未说明关系转为正式边。所有OCR校读只记录于断言限定，不改来源资产。



注释L295–308已完成迁移和回链。全书账本现为190段reviewed/complete、30段有理由排除、582段queued、0段partial；候选6,007、提及7,766、原书断言3,915。`audit_tables.py --summary`为0 errors，仍报告两条既存enrichment `source_ref`警告和S2未完成提示。下一工作范围为第5章，S2全书覆盖后再进行交接审计，不提前交S3。





## 第5章印刷页120章前脚注L8–9（2026-09-29）



先按源序处理`05_CHP-5_intro.md`：文件名标题段L1及页码/章节标题段L3–5属于导航元数据，分别有理由排除；脚注段L8–9完成迁移。对照`CHP-5.pdf`物理第1页（印刷页120），记录Haskell关于《The Martyrdom of St Erasmus》在其写作时位于Vatican Gallery、作为Poussin为St Peter’s绘制的唯一意大利教堂祭坛画（1628–9）、以及为该画制作preparatory modello并将其定位于Ottawa的说法。作品、St Erasmus题名人物、Vatican Gallery与未识别modello分别建候选或复用索引候选；地点和馆藏仅按原文，未与相似机构自动合并。



脚注2的Friedlaender p.101和脚注3的Mancini I p.249记录为书目定位，未声称已核对被引页。PDF还显示脚注1续有Annunciation来源判断；OCR转录位于下一规范段`05_CHP-5_sec_i.md` L7，故该判断随该段处理并回链，未在本段重复迁移。页图确认脚注中的`anltalianchurch`应读作“an Italian church”；校读只记录在对应statement限定，不改S0。



本批S2表新增3个候选、11条提及、6条原书断言/引证。`audit_tables.py --summary`结构errors为0；全书账本更新为191段reviewed/complete、33段有理由排除、578段queued、0段partial。第5章导言脚注已收口，下一源段为`chp-5:05_CHP-5_sec_i:l3-7`；该段末句续至页121，须保留partial直至下一段闭合。



## 第5章印刷页120–121正文L3–15及脚注续文（2026-09-29）



按源序迁入`05_CHP-5_sec_i.md` L3–7及L9–15，并核对`CHP-5.pdf`物理第1–2页。页120记录Haskell对Poussin的地位与职业范围、独立赞助人和艺术发展、罗马政治文化环境及画商兴起的论述；Caravaggio经法国画商Valentin结识Cardinal del Monte、Ribera初抵罗马按日为画商作画等叙述保留来源层级。L7为脚注1续文：Poussin《Annunciation》据称来自Alexander VII在Castel Gandolfo的礼拜堂，Haskell以铭文认为“可能正确”但明确证据不确，未写成确定来源。



页121闭合L6关于Salvator Rosa的跨页句，分别记录Claude因仿作冒充原作而登记作品、Guidiccioni“可能”受骗及其所购可疑归属、Accademia di S. Luca的引语和行规、1633年税权、画商兼业、税收抗拒及1674年人数/地点/群体描述。书内候选关系仍为候选，不写入`relations.csv`。索引已包含Cardinal del Monte、Ribera、Rosa等对象；为引文中被称作可疑作品作者的Perino del Vaga新建`cand-6015`，具体作品不明。



PDF校读只记入断言限定：L3 `OUSSIN`实为`POUSSIN`，L4 `Pfresco`实为`fresco`，L7 OCR `Vil`实为`VII`；Accademia名称跨源行，按扫描连读。脚注1–3、5–7的完整书目文本位于本文件后部注释段，当前只记录正文脚注指向；L15页底注4的Hoogewerff引文作书目定位，不表示已读被引文献。两段共新增1个候选、32条提及、16条原书断言/引证。表审计0 errors，仍有两条既存enrichment来源警告及S2未完成提示；当前总账193 complete、33 excluded、576 queued。下一段为印刷页122 L17–26。



## 第5章印刷页122–123：正文、跨页续句与候选断言（2026-09-29）



按源序处理 `05_CHP-5_sec_i.md` L18–26 与 L29–33，分别对应 PDF 物理页3、4（印刷页122、123）。PDF核对 Peri、Carlone、de Wael、Urban VIII、Innocent X、Rossi、Preti、Ottini、Brandi、de Stael、Ferrante Carlo、Sfondrato、Borghese、Bernini、Cassiano dal Pozzo、Lanfranco、Valguarnera 与 Mancini 等正文对象。页122 L26 的 dealer 句跨页续至页123 L29并闭合；页123 L33 “As a doctor he was said to be”续于页124 L36，故该段保留 `partial`，下一源段为 `chp-5:05_CHP-5_sec_i:l35-49`。



语义处理中保留Haskell的报告语气、“must have known”“apparently”“seemed”“very doubtful”等限定，以及Carlo关于Bernini的嵌套转述和议价事件。对不明画作不另造作品候选；France复用地理地点候选，Spain采用地点候选而不映射到政治实体，England沿用realm候选以待S3消歧；Pasquino雕像新增 `cand-6016`。Innocent X采用索引中页122“effect of economic retrenchment on artists”子目 `cand-1822`；Cardinal Borghese依页123索引候选 `cand-0394`，身份统一留待S3。关系仅记作S2断言候选。



扫描显示页123 Carlo叙述中的“I agreed”被OCR转录为“T agreed”；在对应statement记录校勘说明，保持来源OCR文件原样。新增1个来源型候选、46条精确跨度提及和20条带原文锚点的statement。`audit_tables.py --summary`无结构错误；仍报告两条既存 enrichment `source_ref` 警告、574个queued段和本段partial。`tests/test_audit_tables.py`：11 passed。





## 第5章印刷页124：正文L35–42、注释片段L43–49（2026-09-29）



按源序处理规范段`chp-5:05_CHP-5_sec_i:l35-49`，对照`CHP-5.pdf`物理第5页（印刷页124）。页123 L33 Mancini句在本页L36闭合，因此将上一段改为reviewed/complete。页124 L42第一句记录Carlo、Mancini与Simonelli的共同履历及艺术赞助；第二句止于“these”，续到下一规范段页125 L52，本段保留partial。



本段新增7个来源型候选、41条精确跨度提及和18条原书断言/引证。新增对象包括Chigi household、Chigi archives、两件由正文与脚注分别描述的版画、Testa在Windsor的未题名素描及其背面书信，以及来源括注识别的出版者Gian Domenico Rossi。已有页码索引候选保留为独立对齐线索，留待S3映射；“Treatise”只作一般称呼，索引中`Considerazioni sulla Pittura`的对应关系暂不确定。



断言区分Mancini以行医身份向时髦病人索取绘画礼物及其获得的经销优势；Simonelli的行政服务、Chigi household职务、收藏、Rosa/Testa关系、Castiglione版画题献及对Monconys的接待；“No doubt he did the same for other visitors”保留为Haskell推论。脚注逐项记录Passeri对Simonelli鉴赏家声誉的说法、Scaramuccia《Venus and Adonis》题献、Testa书信“seems to show”欠款的限定、Golzio书目定位，以及Haskell对Diogenes版画题献的解释。引文层级保留，不将Testa欠款写成确定关系；题献中的“Alessandro”不消歧。



PDF核字确认OCR中的Niccolò Simonelli及`i960`应分别读作Niccolò与1960；S0文本原样保留，校勘写入限定。页124注释与后置注释段L125–147（尤其L142）存在待核交叉，后续按源序核对并避免重复计入。`audit_tables.py --summary`结构errors为0；`tests/test_audit_tables.py`：11 passed。当前总账195段complete、1段partial、33段excluded、573段queued；候选6,019、提及7,896、原书断言3,975。下一规范源段为`chp-5:05_CHP-5_sec_i:l51-58`（印刷页125）。





## 第5章印刷页125：页间续句、展览与脚注（2026-09-29）



按源序处理规范段`chp-5:05_CHP-5_sec_i:l51-58`，对照`CHP-5.pdf`物理第6页（印刷页125）。L52闭合页124 L42“三人共有职业与赞助”后的转折句；页124正文续句现已闭合，但页124 Simonelli脚注1仍需将本段L43–49与后置注释L142合并回链。页125 L57末句“...were far more dignified”续于下一段页126 L61，本段保留partial。



本段新增7个候选、24条精确跨度提及和18条原书断言/引证。候选包括Corpus Domini节日、1607年身份未明的Mantua公爵、Caravaggio《Death of the Virgin》、在罗马组织展览的Bergamasque community、其主保圣人St Bartholomew、Giuseppe Ghezzi的相关档案材料及Museo di Roma。索引候选保留为S3对齐线索；Mantua公爵不与书中其他同称候选合并，教堂/地点与组织身份也不混同。



正文记录展览扩大艺术家公众接触、宗教节日与游行、展览地点未定、参展者的社会画像、展览吸引鉴赏家，以及Sinigaglia集市和Claude观看Goffredo Wals风景的不同叙述。Claude受Wals影响的说法保留“is supposed to”，1607年展览的出席人数保留“apparently”，其“influence and emancipation”作为Haskell解释；Bergamasque展览的日期、场地、Guardiano支付、装饰目的、匿名观察者、起始时间不确定及1650年前已兴盛分别记录。页57仅迁移“为艺术家提供展示作品的机会”完整分句，把“比普通节庆集市更体面”的比较留待L61续文。



PDF核实L53的分节符“– II –”与正文被OCR粘连，`we generally`被识为`wegenerally`；不改S0。印本页下注释1含两句：本段L58为Ghezzi papers/Museo di Roma说明，关于Haskell《Studi Secenteschi》(1960)的书目定位见后置注释L143；两处合为一条脚注并避免重复断言。`audit_tables.py --summary`结构errors为0；`tests/test_audit_tables.py`：11 passed。当前总账195段complete、2段partial、33段excluded、572段queued；候选6,026、提及7,920、原书断言3,993。下一规范源段为`chp-5:05_CHP-5_sec_i:l60-74`（印刷页126）。





## 第5章印刷页127正文 L77–83（2026-09-29）



按源序处理`chp-5:05_CHP-5_sec_i:l76-83`，对照`CHP-5.pdf`物理第8页。页126 L74的Jan Miel遗嘱条件由本段L77“with pictures…”续接并闭合；对应引文继续分段锚定在p126与p127两条statement中，将页126 coverage从partial改为complete。页127 L83结尾的Rosa支持者引语续于页128 L86，本段保留partial。新增12个来源型候选、47条精确提及和31条原书断言/引证。



逐项记录Pantheon展览的宗教目的及早期展品范围、1680年两幅画的查禁和Haskell对“indecency”指控的保留态度、未具名Cardinal的辩护；另记S. Giovanni Decollato的年度展览、29 August节日、贵族家族赞助和1620年记录及约1600年的较早迹象。Orazio Gentileschi的1603年证词、Archangel Michael画作的展示位置、Baglione《Divine Love》与Caravaggio《Earthly Love》的竞争分别建为候选/断言；“exhibition was intended for rivalry”被Haskell否定，宗教装饰目的保留“Almost certainly”。



1662年Sacchetti组织展览、Pietro da Cortona的突出位置、旧大师借展；1668年Rospigliosi家族的奢华布置、Camillo与四名未具名儿子入Compagnia della Misericordia为novices、Queen Christina借画、只展旧大师及Rosa的反应分别记录。未具名Pope、Cardinal、avviso与画作不补身份；avviso作为archive候选保留，但其题名、作者、日期和定位未明。四子人数和展陈地点列表保留在原书断言，不制造个体或合并地点实体。Index候选cand-0133、cand-0157、cand-0548、cand-0678与书内实体候选分别保留，待S3对齐。



PDF物理第8页确认印本为“S. Giovanni Decollato”，而S0 L79 OCR为“Decollate”；校勘写入statement/candidate限定，不改来源。其余本页未见需要纠正的OCR差异。当前总账197段complete、2段partial、33段有理由排除、570段queued；候选6,046、提及8,000、原书断言4,043。`audit_tables.py --summary`结构errors为0，`tests/test_audit_tables.py`为11 passed；两条既存enrichment `source_ref`警告仍在。下一源段`chp-5:05_CHP-5_sec_i:l85-97`（印刷页128），先闭合页127 L83引语，再处理本页展览及后续内容。



## 第5章印刷页128正文 L86–97（2026-09-29）



按源序处理chp-5:05_CHP-5_sec_i:l85-97，核对CHP-5.pdf物理第9页。页127 L83的Rosa支持者引语由页128 L86–87续接并闭合，故页127 coverage由partial改为complete；页128 L97的1708年Ruspoli句子在页129 L100续接，本段标记partial。新增12个候选、53条精确跨度提及和26条原书断言/引证。



语义记录覆盖Holy Year 1675的Medici展览、200余幅作品与教堂外布幔/内部展陈；展览商业化倾向、1736年212幅新旧作品、未具名图录及“希望教皇竞价”的报告；S. Salvatore in Lauro教堂、回廊、Marchigian colony、Azzolini在1669年购堂、Loreto Holy House纪念日展览，以及1675年声誉、装饰/出借者目的和组织评估。另记录Ghezzi自1682年负责筹办及其学院职务/出身、借展联络/运输/警卫/照明安排、Madonna居首与展品类型、推荐画幅数量和年度变化；1697年Prince Pio的独占出借条件、loggia与上层回廊分区展陈、社交仪式，以及1708年Ruspoli叙述开头。保留说话者、作者评估、“was said to”等转述、匿名端点和未完句；the Carracci与first-name-only Guido仍待S3身份裁决，作品姓名作画作转喻时不造具体作品。



PDF核对确认本页年份、数量和地点。S0 L88在Carracci.后含OCR双引号，印本对应一处疑似上标；L96 fore.后的OCR撇号也对应疑似上标，具体注号待后置注释段核实，不改S0。页124脚注1仍待与L142合并，页125脚注1来源定位L143待按原记录回链。当前总账198段complete、2段partial、33段有理由排除、569段queued；候选6,058、提及8,053、原书断言4,069。audit_tables.py --summary结构errors为0，保留两条既存enrichment source_ref警告；本段下一步为页129 L99–106，先闭合Ruspoli句，再按书序处理正文及后置注释。





## 第5章印刷页129正文 L99–106（2026-09-29）



按源序迁入`chp-5:05_CHP-5_sec_i:l99-106`，对照`CHP-5.pdf`物理第10页。页128 L97的1708年Ruspoli句由本页L100续接并闭合：Ruspoli先要求仅展其194幅画，后接受Ghezzi建议，允许Monsignor Olivieri另挂23幅。页129 L106关于艺术家变得更可见的末句续于页130 L109，因此本段标记partial。



本批新增15条精确跨度提及和20条原书断言/引证，无新增候选。逐项记录旧大师在展览中的突出与重复陈列、当代绘画可及性、Ottoboni展示Trevisani作品、Grimani于1707年送展Molinari作品及其在罗马收藏家中的认知状况、展览的宣传用途；1704年匿名Pope鼓励John of Poland遗孀出借肖像与战役画，只记录鼓励出借而不宣称实际出借。另记录四次年度展览、偶发展览、展新作并非常规展览的首要目的、展览的装饰与公共功能、非正式展示的艺术意义、定期赞助/祭坛画陈列未被显著改变，以及商人、旅行者、外国赞助与艺术家聚落所形成的城市文化语境。Haskell的概率、概括和评价均保留；“these exhibitions”按前文复数范围处理，没有错误映射到两个具体展览候选。



PDF物理页10确认印本为“in a fit of patriotic enthusiasm”，而S0 OCR L101作“sit”；印本为“primary aim”，OCR L104作“primary.aim”，疑似行首标记作为校勘说明保留；不改S0。页124脚注1与后置注释L142、页125脚注1与L143的来源说明仍待回链，页128疑似上标待后置注释核实。表级审计0 errors；`tests/test_audit_tables.py`为11 passed，`git diff --check`通过。当前总账199段reviewed/complete、2段reviewed/partial、33段有理由排除、568段queued；候选6,058、提及8,068、原书断言4,089。下一规范源段为`chp-5:05_CHP-5_sec_i:l108-113`（印刷页130）。





## 第5章印刷页130正文 L109–113（2026-09-29）



按源序处理`chp-5:05_CHP-5_sec_i:l108-113`，对照`CHP-5.pdf`物理第11页。页129 L106关于艺术家可见性的句子由L109“of the colourful life…”续接并闭合；页130 L113新句首词“A”续至页131 L116，因此本段标记partial。新增4个来源型候选、23条精确跨度提及和19条原书断言/引证；跨段前一引句与该段后续语境分别记录。



记录艺术家观看并描绘周围生活、Bentvueghels入会仪式；审美鉴赏观与鉴赏者群体形成、subject-matter相对失去原有优先性、该态度的时代限定及Giustiniani/Caravaggio例证；静物画、风景画和此前不受重视题材的兴起及Haskell对其历史重要性的评价。再记录公众兴趣增长、匿名赞助人、Mancini的Treatise与引导买画/挂画的规则、Mancini所引用的社会阶层区分、议价和估算画家劳动所得的建议、住宅房间与题材陈设建议；最后处理大众拥有图像的类型、年轻艺术家来罗马后的生计推论及Sassoferrato为非精英赞助人作画的疑问。Haskell的引述层级、因果解释和不确定性均保留；Treatise标题与匿名群体身份未被过早确定。



本页脚注标记1（Caravaggio引语）和2（Mancini段落）分别对应后置注释L144、L145，待按源序处理注释后回链。扫描确认印本L110为“the price”，OCR作“theprice”；L113“copied”前无双引号，OCR多出引号；两处均只记校勘，不改S0。页131首句继续L113的“A prolific painter”，后续关系与事实随下一源段处理。`audit_tables.py --summary`结构errors为0，`tests/test_audit_tables.py`为11 passed；`git diff --check`通过。当前总账200段reviewed/complete、2段reviewed/partial、33段有理由排除、567段queued；候选6,062、提及8,091、原书断言4,108。下一规范源段为`chp-5:05_CHP-5_sec_i:l115-123`（印刷页131）。



## 第5章页131–132正文与注释（2026-09-29）



### 印刷页131正文 L115–123



按源序处理chp-5:05_CHP-5_sec_i:l115-123，对照CHP-5.pdf物理第12页。页130 L113的“A prolific painter”由L116续接并闭合，原partial关闭。新增10个候选、62条提及和26条原书断言/引证。保留Sassoferrato委托、职业群体推断及Gigli日记叙述中的作者推测、间接引述和评价；将1636年未成交作品与1643年更换作品分开，不将Foot/Visconti二手信息改写为无条件事实。PDF核对tire/the、Pamftli/Pamfili、163 6/1636、GigE/Gigli、diEgently/diligently，均作为限定说明，不改S0。



### 页121–131后置注释 L125–147



处理chp-5:05_CHP-5_sec_i:l125-147，完整迁入L126–147注释文字，新增19个来源型候选、56条精确跨度提及和35条断言/引证。页124注1的L142与既有注释L43–49合并回链，关闭页124段partial；页125注1/L143的来源定位、页130注1–2/L144–145及页131注1–4/L146–147均连回各自正文断言。书目条目仅作来源定位，不提升为已核事实。页128印刷页底没有与L88、L96两个OCR模糊标记对应的注释，故保留未链接，不猜配。印本物理页2–6、12确认L129 che/alla、L131 sold、L142 Annibale、L143 1960及L147 Galleria Nazionale等转录差异；S0保持原样。



### 印刷页131页底的新节开句与印刷页132 L6–10



自动生成的chp-5:05_CHP-5_sec_iii:l1-1标题段以理由排除；按源序读取页131页底的L3新节总论句，新增3个术语候选、3条提及和1条断言。对照物理页12核实estabhshed的印本为established，只记校勘。



随后处理chp-5:05_CHP-5_sec_iii:l5-10，对照印刷页132/PDF物理第13页，新增3个候选、16条提及和15条断言。记录自制人士影响力及其遭受的批评、bambocciate支持者的社会来源假说、跨文化的如画趣味、Bamboccianti名称与Passeri的转述、劳作/休闲/暴力/哀悼场景、将历史题材处理成日常生活背景，以及Rome与campagna的年代和城市描写。Erminia作为文学角色保留待S3类型审查，不临时归为历史人物；脚注1、2分别指向L127、L128，当前状态为等待对应注释段迁移。PDF确认L7开头的孤立点是扫描污点，不是原文标点。L10末尾关于罗马街巷的句子续于L13，因此该段语义为partial，下一规范段为chp-5:05_CHP-5_sec_iii:l12-18。



本次后表审计python scripts/audit_tables.py --summary为0 errors；两条既存enrichment source_ref警告、562段queued及语义质量审查提示仍在。python -m pytest tests/test_audit_tables.py -q通过。当前账本205段reviewed/complete、1段reviewed/partial、34段有理由排除、562段queued；候选6,097、提及8,228、原书断言4,185。下一步闭合页132末句并按源序继续本章。



## 第5章印刷页133 L13–18（2026-09-29）



按源序处理chp-5:05_CHP-5_sec_iii:l12-18，对照CHP-5.pdf物理第14页。L13闭合页132 L10关于罗马街巷、纪念物和商业活动的句子，并继续描写农民群体向城市无产阶级的过渡。新增17个来源型候选、29条精确跨度提及和17条原书断言/引证。候选包括1648年赦免换粮提议及其未名对象、罗马乞丐群体、未具名教皇和纪念雕像、临时治理者、两组士兵、与法国/西班牙使馆相关的未名群体、Le Nain集体归属、Arcadian sentiment及社会阶层词项；缺乏可靠类型/身份的对象保留空类型或限定，不猜造姓名和机构。



逐项记录农民极端贫困、饥馑和粮荒、1648年对campagna bandits的有条件赦免提议、仪式化组织的乞丐群体、拥挤居所与疫病、台伯河水患；接续罗马长期不满在教皇去世及临时治理条件下激化、纪念雕像受 mob 威胁、守卫雕像和护送枢机/亲王的士兵参与骚乱、与常规警察冲突、法国和西班牙使馆群体长期紧张并发生暴力冲突。footnote 1标记链接至该段后置注释L129，注释尚未迁移。保留Haskell对“谄媚行政”、作者概括和事件范围的责任限定，不为未名教皇指定身份。



后段讨论当代日记记录的苦难与留存Bamboccianti作品所呈现的宁静之间的落差；将Haskell对画作题材、作品损失、反对者说法、非社会抗议解释及Sweerts/Le Nain/Velasquez比较分开记录。L18开始的Doni引语属于嵌套引述，句子延至页134 L21，故本段标记partial。印本物理页14核实L16 OCR “wesind”实为“we find”；仅写入校勘说明，不改S0。



更新当前S2记录后，audit_tables.py --summary为0 errors；保留两条既存enrichment source_ref警告、561段queued及语义质量审查提示。当前账本206段reviewed/complete、1段reviewed/partial、34段有理由排除、561段queued；候选6,114、提及8,257、原书断言4,202。下一段为chp-5:05_CHP-5_sec_iii:l20-26，先续完Doni引语。



## 第5章印刷页134正文 L21–26（2026-09-29）



按源序处理`chp-5:05_CHP-5_sec_iii:l20-26`，对照`CHP-5.pdf`物理第15页。L21闭合页133 L18开始的Doni引语；页134 L26的“But these”续于页135 L29，因此本段为partial，页133原partial相应关闭。新增6个候选、23条精确跨度提及和14条原书断言/引证。



逐项记录Salvator Rosa关于“欢迎”bambocciate的意大利诗句、Haskell英译及“within limits”的限制；Haskell以“good poor”解释被小尺幅控制的贫者形象，并引用Passeri关于Van Laer画中人物尺度的说明。再记录后来的风景背景压过乞丐和牧人、贫者成为如画布景；Van Laer与追随者为意大利绘画引入的新题材；Bassano与Caravaggio作为Bellori批评对象的可能先例；Caravaggio对日常劳动者、贫者和农民的不同呈现；其意大利追随者较少延续日常生活描绘；以及Annibale Carracci《豆食者》和劳动者素描的例证。嵌套引述归于Doni、Rosa和Passeri，作者翻译、判断、比较和历史解释分别标注；“perhaps”“rarely”“for the first time”等范围限定不提升为无条件事实。未名追随者、Colonna gallery的具体空间、未题名素描及“good poor”等解释性词项保持来源型待决候选，不预断身份或类型边界。



物理页15核实S0 OCR中`on e palmo (221 cm.)`为印本`one palmo (22½ cm.)`、`Mils`为`hills`，并核对`Mmself`、`pamting`、`ordmary`、`Ms`、`witMn`、`tMs`、`fife`、`grotesque`、`Anfflbale`等误识。S0原文及提及跨度不作静默改写；对`Ms followers`、`Ms drawings`、`Anfflbale Carracci`等提及按OCR原串定位，印本读法写入校勘限定。页134脚注1–4分别指向后置注释L130–133，待该注释段迁移后回链；页132脚注1–2与页133脚注1同在待处理L127–133范围。



当前总账207段reviewed/complete、1段reviewed/partial、34段有理由排除、560段queued；候选6,120、提及8,280、原书断言4,216。`audit_tables.py --summary`为0 errors；两条既存enrichment `source_ref`警告和S2未完成/需核语义质量提示保留。下一源段为`chp-5:05_CHP-5_sec_iii:l28-34`（印刷页135）。



## 第5章印刷页135正文 L29–34（2026-09-29）



按源序处理`chp-5:05_CHP-5_sec_iii:l28-34`，对照`CHP-5.pdf`物理第16页。L29续完页134关于Annibale Carracci的作品只属较正统职业旁支的句子，并转入Haskell对Bamboccianti缺乏真正先驱、艺术家脱离既有绘画分类所遇困难的判断。新增8个来源型候选、29条精确跨度提及和20条原书断言/引证。



记录Pieter Van Laer 1625年来罗、当时31岁；其在新教城市Haarlem成长，以及Haskell所述当地写实绘画传统；Van Laer在罗马加入新成立的schildersbent并过其成员式“bohemian”生活。宗教与社会处境使他至少数年远离官方赞助，他未依附亲王或大使家户，靠出售农民和动物小景维生；Corpus Domini集市是作者提出的可能渠道，画商则是其较确定提及的买家。记录30/35 scudi的要价、昂贵画家声誉及买家难以确认；其他画家、北方同乡对其作品的赞誉，Hermann Swanevelt拥有两幅作品，以及Pietro Testa虽晚年轻视写实却与早期bamboccianti圈子往来、可能拥有相关作品。后续记录罗马重要赞助人的谨慎关注、Niccolò Simonelli短暂持有并交换两幅题材各异的Van Laer画作、Vincenzo Giustiniani保护Caravaggio北方追随者并购藏两幅不寻常作品但未装框、Cassiano dal Pozzo似曾考虑并拥有一幅Van Laer画作。末句记录Van Laer约离罗前三年将八幅动物版画献给Don Ferdinando；受赠者全名在页136 L37续出。



引述和语气按原层次保留：其他画家赞赏语由Haskell经Passeri转述；30/35 scudi带脚注的1636年32 scudi佐证待核；Swanevelt的所有权、Testa可能持有及Cassiano收藏均保留来源和不确定限定；Giustiniani的两件作品分别映射到Van Laer索引子目“Landscape with Figures and Animals”和“St Eustace Hunting”。`schildersbent`单列为组织候选，并注明与前章Bentvueghels的身份在S3再对齐；Haarlem、写实传统、未具名画家群、罗马赞助人群、Simonelli两件未题名画作及动物版画组分别登记。姓名沿用现有索引候选；全名尚未在本段出现的Don Ferdinando映射到既有候选，但其身份仍留给S3核对。



页135脚注1–5分别指向后置注释L134–138，仍待注释段迁移回链。L138注还补充Van Laer的另一位朋友Bernardino Lorca，留待后续注释语义处理。印本核对确认S0 L30 `of‘realistic’`的排印空格以及L32人名印作“Niccolò Simonelli”，均只记校勘、不改S0；页物理扫描未发现需要把作者限定改成确定事实的依据。L34结尾姓名未完，故本段semantic partial；页134 L26在本段L29关闭。



当前总账208段reviewed/complete、1段reviewed/partial、34段有理由排除、559段queued；候选6,128、提及8,309、原书断言4,236。`audit_tables.py --summary`为0 errors；保留两条既存enrichment `source_ref`警告与S2未完成/需核语义质量提示。下一源段为`chp-5:05_CHP-5_sec_iii:l36-43`（印刷页136），先补全Don Ferdinando身份表述并继续Van Laer相关叙述。



## 第5章印刷页136正文 L37–43（2026-09-29）



按源序处理`chp-5:05_CHP-5_sec_iii:l36-43`，对照`CHP-5.pdf`物理第17页。页135 L34分开的受赠者在L37补全为Don Ferdinando Afan de Ribera、那不勒斯总督；该人名身份仍待S3外部对齐。新增9个候选、41条精确跨度提及和23条原书断言/引证。



记录Haskell所称西班牙人与Bamboccianti成功始终紧密相关；Van Laer尽管影响显著，却可能处在社会边缘，其主要客户被推定为匿名的“uomini di stato mediocre”，而非显贵和学者赞助人。作者将Van Laer约1639年离罗时已经形成的大量、可获利题材需求解释为时代标志，并指出有多人准备利用这一市场。继而处理Michelangelo Cerquozzi：罗马出生、可能先低价向画商售画再获鉴赏家注意；作者以其意大利身份和社会处境解释其比外来者Van Laer更接近赞助人的可能；其生活与作品被用来说明贵族社会容许现实主义表达的边界。记录Cerquozzi受同业赞赏、与Domenico Viola和Giacinto Brandi的密切友谊、与Pietro da Cortona的交往、对年轻人及Giacomo Borgognone的支持；其重要赞助/欣赏者来自职业阶层，包括律师Raffaele Marchesi（获遗赠若干作品）和医生Vincenzo Neri（与其他友人在Plate 22a作品中被描绘）。



后段记录Cerquozzi受不同于Barberini圈的罗马贵族家族接纳，其最初成功作品据称为西班牙使馆官员所绘；他可能曾在Velasquez于1630年作为Monterey大使客人停留期间任职使馆。另有证据但仍属作者判断：Cerquozzi与Velasquez都曾为Colonna绘制bambocciate，较可能发生于Velasquez第二次访问期间。保留“apparently”“possible”“some evidence”“more likely”等限定；Cerquozzi与西班牙及罗马西班牙支持网络的联系、穿西班牙服饰之句分开记录，未把未完的“and until his later years”补写为事实。



脚注1–4分别指向注释L139–141，待后置注释段迁移后回链。扫描确认L42的S0 `1630?`实际为印本1630加脚注标记3；L43 `her.supporters, in . Rome`按印本读作“her supporters in Rome”，校勘限定保留、不改S0。当前段标记partial；其后依源序为Plate 21（L45–57）、Plate 22（L59–61）、Plate 23（L63–65）、Plate 24（L67–68），正文在L70–80恢复并续完L43句子。



当前总账209段reviewed/complete、1段reviewed/partial、34段有理由排除、558段queued；候选6,137、提及8,350、原书断言4,259。`audit_tables.py --summary`为0 errors；两条既存enrichment `source_ref`警告和S2未完成/需核语义质量提示仍在。





## 第5章印刷图版Plate 21（2026-09-29）



处理规范段`chp-5:05_CHP-5_sec_iii:l45-57`，核对`CHP-5.pdf`物理第18页。图版页展示Plate 21a/b：b为“Sassoferrato: Madonna and Child”；a为“Sassoferrato: Madonna of the Rosary with Saints”。图注竖排，S0将每个词倒序并按反向行序抽取；提及跨度严格锚在未改写的OCR行L46–57，印本读法只记入限定。复用既有Sassoferrato与两件作品候选`cand-3880`、`cand-4094`、`cand-4095`；a图注自身只写“With Saints”，不把独立图版目录及页131正文中的Dominic、Catherine扩写进本图注。登记4条提及、2条`caption_attribution`断言；记录题注归属而非作者身份的独立验证。该段reviewed/complete，未新增候选。



页136 L43的末句仍待闭合；下一规范段`chp-5:05_CHP-5_sec_iii:l63-65`为Plate 23，之后L67–68为Plate 24，再由L70–80正文续接。



当前语义进度211段完整、1段跨页未闭合、34段有理由排除、556段queued；候选6,137、提及8,359、原书断言4,263。覆盖表中212段reviewed且迁移完成（其中1段语义跨页未闭合）、34段排除、556段queued。`audit_tables.py --summary`结构errors为0；两条既存enrichment `source_ref`警告与S2未完成/需核语义质量提示仍在。





## 第5章印刷图版Plate 22（2026-09-29）



处理规范段`chp-5:05_CHP-5_sec_iii:l59-61`，核对`CHP-5.pdf`物理第19页。Plate 22a题注为“Cerquozzi: The artist with a group of friends”，Plate 22b为“Cerquozzi: The revolt of Masaniello”。两条题注与图版清单一致；复用作品候选`cand-4059`、`cand-4060`及艺术家候选`cand-3084`，另记录b题名中的Masaniello候选`cand-4150`。新增5条精确跨度提及、2条`caption_attribution`断言，不把a题名中的泛称扩写为具名人物，也不把题注归属当作独立作者身份验证。该段reviewed/complete，未新增候选。



下一规范段`chp-5:05_CHP-5_sec_iii:l63-65`为Plate 23a/b；随后L67–68是Plate 24，L70–80正文续接页136 L43。



当前语义进度211段完整、1段跨页未闭合、34段有理由排除、556段queued；候选6,137、提及8,359、原书断言4,263。覆盖表中212段reviewed且迁移完成（其中1段语义跨页未闭合）、34段排除、556段queued。`audit_tables.py --summary`结构errors为0；两条既存enrichment `source_ref`警告与S2未完成/需核语义质量提示仍在。



## 第5章印刷图版Plate 23–24（2026-09-29）



按源序处理`chp-5:05_CHP-5_sec_iii:l63-65`与`l67-68`，分别对照`CHP-5.pdf`物理第20、21页。Plate 23a/b印本题注为“Cerquozzi: Women's bath”与“Salvator Rosa: The death of Regulus”；Plate 24为“Salvator Rosa: Fortune”。S0在23b将Salvator Rosa识为“S R :”，保留OCR跨度，印本更正只记限定。



复用23a作品与Cerquozzi候选`cand-4061`、`cand-3084`，23b作品、Rosa与Regulus候选`cand-4093`、`cand-3099`、`cand-4152`，Plate 24作品与Rosa候选`cand-4033`、`cand-3099`。合计新增7条精确跨度提及、3条`caption_attribution`断言，不将图注归属当作独立作者核验，也不从题名扩写人物或历史情节。两个源段均reviewed/complete，无新增候选。



## 第5章印刷页137正文L70–80（2026-09-29）



处理规范段`chp-5:05_CHP-5_sec_iii:l70-80`，对照`CHP-5.pdf`物理第22页。L71续完页136 L43的句子，读取为“and until his later years nearly all his more important patrons were within the Spanish sphere of influence”；保留时间范围和“nearly all”，将页136原partial关闭。页137 L79关于勤勉工作者的句子在“careful and conscientious in his”处继续至页138 L83，本段语义仍为partial、表迁移已完成。



本段新增8个来源型候选`cand-6142`–`cand-6149`、47条精确跨度提及和20条原书断言。候选分别容纳1655年教宗选举会议、其中未具体指明的法国参与群体、风格比较中的未名宏大历史画家、威尼斯色彩理想、作者所说的反西班牙平民、支持西班牙的未名群体、相关罗马赞助家族群，以及Rapaccioli所藏未题名Cerquozzi画作。复用Strada与《De Bello Belgico》索引项、Miel、Borgognone、Farnese、Rapaccioli、Raggi、Carandini、Carpegna、Dughet、Rosa、Van Laer等候选；区分Bamboccianti画家群与bambocciate题材。



断言记录覆盖1647年协作插图与第二卷内容、Rapaccioli藏画/去世/在1655年会议遭抵制、Raggi与Carandini的西班牙政治立场、相关赞助家族与Barberini圈的审美对照、他们偏好的风景及日常题材、Carpegna/Carandini/Raggi对该类作品的收藏、Cerquozzi早期小幅通俗题材和经画商售出、后期转向大型委托作品及题材扩大，以及作者对赞助压力、艺术家价值吸收和私生活矛盾的限定判断。原文的“nearly all”“most”“it seems”“not much reason”“may not be extravagant”均保留；L79句子未闭合部分标为待L83续读，不推断完整对照。



PDF物理第22页核实印刷页137及脚注排版；S0“private fife”印本为“private life”，“antiSpanish”印作跨行“anti-Spanish”，只将校勘记入断言限定，不改来源。L80是注2尾段，在后置脚注L143中重复出现；coverage说明去重，不重复建提及/断言。正文脚注1–4分别待与L142–145后置注释迁移后回链；L80的完整脚注语义也随L143处理。



当前总账214段complete、1段partial、34段有理由排除、553段queued；候选6,145、提及8,413、原书断言4,286。`audit_tables.py --summary`为0 errors；`tests/test_audit_tables.py`为11 passed，`git diff --check`通过。两条既存enrichment `source_ref`警告与全书S2未完成/语义质量仍需核验提示保留。下一规范段为`chp-5:05_CHP-5_sec_iii:l82-93`；全书未收口前不交S3。



## 第5章印刷页138正文 L82–93（2026-09-29）



处理规范段`chp-5:05_CHP-5_sec_iii:l82-93`，对照`CHP-5.pdf`物理第23页。页137 L79的“careful and conscientious in his”由L83续完，前段partial关闭；本段L93以“when”结束，语义partial，须在印刷页139 L96续读。迁入10个候选、31条精确提及和16条原书断言。



逐层记录Cerquozzi的工作与言语反差、临终食用洋蓟及其“返回”通俗生活的象征解释、圣路加学院主持葬礼与Haskell对古典理想主义的评价；贵族接纳与描绘穷人的限度；有人物静物画、马西米枢机所藏四幅乡村生活画、色彩质感及作品想象性；Cerquozzi对战画的专长、Fritz Saxl“无英雄的战斗场景”分析、战斗图景的社会吸引力、意大利作为欧洲战争旁观者的作者判断，以及与Stendhal的滑铁卢描写比较。保留Haskell的“almost”“presumably”“seemed”“perhaps”“may have occurred”“about”等限定，区分Passeri转述、Saxl分析和作者解释；未把匿名作品组拆成单件，未将多义的西班牙党派强行并入其他同名集团。



页138扫描核实印刷文本`life`（S0误作`Use`）、`lit up`（S0误作`fit up`）、`battle-fields`及Waterloo句末；L92句末之后的OCR点线噪声不入语义记录，来源OCR不改。脚注标记1–4分别指向同文件后置注释L146–149，待按源序迁移回链。



本段完成后总账为215段complete、1段partial、34段有理由排除、552段queued；候选6,155、提及8,444、原书断言4,302。覆盖表216段reviewed且迁移完成。`audit_tables.py --summary`为0 errors，定向测试11项通过，`git diff --check`通过；保留两条既存enrichment `source_ref`警告和全书S2未完成/语义质量仍待核验提示。下一规范段为`chp-5:05_CHP-5_sec_iii:l95-101`（印刷页139）。



## 第5章印刷页139正文 L95–101（2026-09-29）



处理规范段`chp-5:05_CHP-5_sec_iii:l95-101`，对照`CHP-5.pdf`物理第24页。L96续完页138 L93“可能约在1648年发生危机时”，但保留作者“probably”所述《马萨涅洛起义》绘画时间；前一跨页statement关闭。L100对Cardinal Flavio Chigi的称述止于“the most influential”，由页140 L104的“patron in Rome”续接，本段因此为partial。新增8个候选、44条精确提及和19条原书断言。



记录《马萨涅洛起义》的转折意义、当时绘制现实事件画的罕见性、委托人未明及晚17世纪Spada收藏归属；Cardinal Bernardino可能委托及其政治意义仍属条件判断，区分其收藏、巴黎教廷使节经历与法国阵营立场。迁入Mazarin要求法国支持者在Innocent X死后选举Spada及西班牙人使用否决的叙述；保留Cerquozzi的亲西班牙立场与绘制西班牙败局的反差、作品中性／反英雄和Haskell所称的客观性，并与Micco Spadaro双重描绘Masaniello的画作比较。另记与建筑画家Viviano Codazzi的合作、其1647年末从Naples到Rome及可能提供目击叙述的限定，以及合作所确认的题材转变；不把未名叙述或西班牙行动者强行并入其他群体。



脚注3正文位于同段L101，扫描确认印本为“Leman, pp. 13 ff., and Hanotaux, p. 9.”；S0的“if”按原样保留，引用已回链至L97否决叙述。脚注1、2、4、5、6后置注释分别在L150、L151、L152、L152、L153，待后续迁移。其余扫描文本与OCR差异未改变语义，不改写S0。当前总账216段complete、1段partial、34段有理由排除、551段queued；候选6,163、提及8,488、原书断言4,321。覆盖表217段reviewed且迁移完成。`audit_tables.py --summary`为0 errors，`tests/test_audit_tables.py`为11 passed，`git diff --check`通过；保留两条既存enrichment `source_ref`警告和全书S2未完成/语义质量待核验提示。下一规范段为`chp-5:05_CHP-5_sec_iii:l103-113`（印刷页140）。





## 第5章印刷页140正文 L103–113（2026-09-29）



处理规范段chp-5:05_CHP-5_sec_iii:l103-113，对照CHP-5.pdf物理第25页。L104闭合页139 L100对Cardinal Flavio Chigi的未完描述；L113以“now bereft of”结束，关于罗马旧贵族家族的句子待印刷页141 L116续读。本段迁入12个候选、39条精确跨度提及和19条原书断言。



新增《The Arrival at the Palace》作品候选，并将既有cand-6164由“未名画作组”更新为题名已部分识别的Haskell关联画作组，保留脚注1对委托/归属的待核限定；再区分罗马浴场stufe、未定范围的East、假设性的罗马写实绘画学派、贵族赞助、理论反对、艺术民主化与Bambocciante绘画方式；另分别保留新富/parvenus、增长中的公众和旧贵族家族等未名群体。复用Cerquozzi、Codazzi、Cardinal Flavio Chigi、《Women’s Bath》、Rome、Italy、Van Laer、Bamboccianti和Jan Miel。没有把画中未名人物写成现实身份，也没有把“travellers’ tales”当作已识别文献。



断言覆盖两件Chigi相关作品的题材判断及其与意大利现实的差异、Codazzi构想的虚构宫殿与被描绘人物/农民、浴场场景、Haskell对stufe或东方旅行叙事的不同程度推测、贵族赞助和理论敌意的作用、Bamboccianti的社会位置、Cerquozzi对历史画家的未实现向往、Miel在两类绘画方式间的张力，以及艺术民主化和公众扩大的解释。嵌入式Chigi语句按Haskell转述处理，不当成Chigi原话；保留“must surely”“perhaps”“predominantly”“not the only”“to a large extent”等限定。页140脚注1、2分别指向后置注释L154、L155，仍待迁移回链；扫描已确认注2标出Ferdinando Raggi报告经Achille Neri转引，正文断言不先做独立事实背书。PDF核实S0的“Two os”应读印本“Two of”、“Women s Bath”印作“Women’s Bath”、L111“and. later”印作“and later”，且图版指向Plate 23a；S0未改写。



同步修正了相邻三条跨页断言的链接状态：页137 L79片段由页138完整statement闭合，页138 L93片段由页139的《The Revolt of Masaniello》判断闭合，页139 L100片段由本段L104的Chigi/罗马赞助人判断闭合。之前覆盖和过程文字虽已记闭合，但book-statements.jsonl仍留pending_source_migration；本次改为closed并记录续接statement与segment，页140 L113的未完片段保持pending，续于下一段L116。



复核逐章覆盖数后更正上一段全书完成数少计1：页139处理后应为216段complete、1段partial。本段处理后总账为217段complete、1段partial、34段有理由排除、550段queued；候选6,175、提及8,527、原书断言4,340。覆盖表218段reviewed且迁移完成。audit_tables.py --summary为0 errors，tests/test_audit_tables.py为11 passed，git diff --check退出码0（报告仓库配置的LF/CRLF规范化提示）；两条既存enrichment source_ref警告与全书S2未完成/语义质量待核验提示保留。下一规范段为chp-5:05_CHP-5_sec_iii:l115-121（印刷页141）。



## 第5章印刷页141正文 L115–121（2026-09-29）

处理规范段`chp-5:05_CHP-5_sec_iii:l115-121`，对照`CHP-5.pdf`物理第26页。页140 L113的“now bereft of”由L116续完并闭合旧贵族家族断言；页141正文在L121结束完整。本段迁入32条精确跨度提及和22条原书断言，无新增候选。单独的L123 `[Page 142]`仅为分页定位标记，按无实体、无断言的版面元数据排除。

语义处理覆盖新富与旧贵族之间的阶层关系、反对Bamboccianti的话语如何诉诸势利与公众/鉴赏家区分、Cerquozzi成功与较自由鉴赏趣味的联系、圣路加学院早期接纳所显示的1630年代态度、攻击在1640–50年代的高峰、经济萧条与低价竞争，以及Guido Reni的敌意经Passeri传记叙述时可能混入传记作者自身态度。另记录1651年Andrea Sacchi与Albani通信、其所称的“新现象”其实已持续约四分之一世纪、六或八scudi说法及Malvasia可能篡改通信的判断。保留Haskell的“seem”“no doubt”“reasonably clear”“quite possible”等不同强度；没有把Albani的身份、通信原貌或Reni原话写成已独立证实事实。

正文脚注1–4分别回链到后置注释L156–159，随statement记录为`pending_source_migration`；注释主体按S0源序在下一段统一迁移。PDF物理页26确认S0中`baniboccianti`应读作印本`bamboccianti`，L121 `relatively'late`印作`relatively late`；只记录校勘，不改S0。

处理后总账为219段complete、0段partial、35段有理由排除、548段queued；候选6,175、提及8,559、原书断言4,362。覆盖表中219段reviewed且迁移完成，35段排除。`python scripts/audit_tables.py --summary`为0 errors；现有两条enrichment `source_ref`警告和S2未完成/语义质量待核验提示保留。`python -m pytest tests/test_audit_tables.py -q`为11 passed；`git diff --check`退出码0，仅有仓库LF/CRLF规范化提示。下一规范段为`chp-5:05_CHP-5_sec_iii:l126-165`，先迁移并回链页132–141脚注，再按序进入第六章并映射旧阅读稿。




## 脚注覆盖状态复核（2026-09-29）

检查源段`chp-5:05_CHP-5_sec_iii:l126-165`时发现：覆盖账本仍标为`queued/pending`，且该源段在`mentions.csv`与`book-statements.jsonl`中均无本段记录；正文中有37条`footnote_link_status=pending_source_migration`的引用，目标位于L127–159。此前当前结果摘要所称“页121–131注释已迁移并回链”与规范覆盖账本及脚注状态不符，现已更正为整段注释待处理；不将旧摘要当作语义迁移证据。页139 L101的脚注3是正文段内已处理的独立例外。下一步从L127开始按源序处理注释本身，逐条核实正文挂点并完成回链，再处理第5章section iv。

## 第5章后置注释与印刷页142–145（2026-09-29）

按当前覆盖账本与主表复核，前节记录的`chp-5:05_CHP-5_sec_iii:l126-165`已由`queued/pending`推进为`reviewed/complete`：注释段迁入38个候选、134条精确提及和62条注释断言/引证；正文页132–141的37个脚注挂点均已与相应注释statement双向回链。此前“继续从L127处理”的进度文字是迁移前快照，现由本记录更新，不覆盖当时的检查依据。

继续按源序完成section iv的`l3-12`、`l14-21`、`l23-31`、`l33-37`及脚注`l39-54`。正文分别记录Rosa对bamboccianti的争论、Stoicism与 patronage 的自我定位、De’ Rossi收藏、面向Ricciardi的委托/书信及风景描述、Passeri对作品传播的转述和Haskell借Luca Giordano所作的类比。嵌套引述、Haskell评价、Rosa书信、Passeri/De Dominici转引及其语气边界分别保留；未识别的小幅绘画、匿名 connoisseurs、未决Borgognone身份和Chantilly未具名画作不强配到特定对象。section iv正文4段合计新增21个候选实体（Second Characters复用注释段已建立的cand-6220）、101条提及和79条断言；`l39-54`新增1个候选、22条提及和16条注释statement，回链17个正文statement。此前p143脚注5和p144脚注2漏挂点已补入；p144脚注3目标行由错误的L27校正为L47。至此第5章全部41段已处置：35段迁移完成、6段按理由排除、0段queued，正文脚注无pending。

对照`CHP-5.pdf`物理页27–30，校记OCR而不改写S0：页142 L6、L8、L12的引号/“his”/“a”；页143 L14–21的“self-control”、1667及De’ Rossi利息标点；页144 L23–31的“live up”“Georgics”“future”；页145 L33–37的“much-loved”“bamboccianti”。注释页143–145另核实L45的139、L49的1651及L51的21 May 1664。页128两个模糊标记在印本没有对应脚注，继续保持未链接。关闭页116 `st-chp4-sec-ii-p116-court-meeting-1655`上的遗留continuation状态，并链接到同段后续绘画statement；目前已迁移语料不再有`partial` continuation标记。

主表审计`python scripts/audit_tables.py --summary`为0 errors；两条既存enrichment `source_ref`警告和全书S2未完成/语义质量需检查提示仍在。`python -m pytest tests/test_audit_tables.py -q`为11 passed；`git diff --check`无空白错误，仅报告工作树既有LF/CRLF规范化提示。当前全书S2为225段reviewed/complete、36段排除、541段queued，候选6,235、提及8,816、原书断言4,519。第5章完成；下一规范段为`chp-6:06_CHP-6_intro:l1-1`。先按源序映射第6章既有阅读稿并核漏，再处理第6–17章和书后材料；全书S2未收口前不交S3。



## 第六章印刷页146–147（2026-09-29）



### 第六章旧稿与规范源段映射



REV-013/014已完整阅读第六章OCR 1–420行及21页PDF，留下49份未接收草稿（含10份旧卡原位修订）。这些成果用于核对论述、候选与疑点；当前迁移严格按`02-sources/02-Markdown/`规范分节源段逐段进行，整章OCR副本不另计覆盖。旧稿不能代替本账本的S2迁移，也不作为KU、关系或完成数量证据。



### 印刷页146：标题、首页注释与正文



排除`chp-6:06_CHP-6_intro:l1-1`及`chp-6:06_CHP-6_sec_i:l1-1`两个Markdown分节标题；迁移`intro:l3-5`（章节标题框架）、`intro:l7-11`（四条注释）及`sec_i:l3-11`（正文）。本批新增并复用共30个候选、61条提及、22条断言：标题1提及/1断言，注释7提及/4引证定位断言，正文53提及/17断言。四条首页注释均回链正文：Poussin书信与Correspondance；Passeri页301及Haskell 1959引文定位；Castro战争的Pastor第XIII卷；Gigli第203–240页。引文只记录书目定位，不冒充已读引文来源；著作题名、版本待书目段S2核对。



正文保留Haskell转述Poussin书信的发言层级；Innocent X选举、法国利益及作者提出的艺术 patronage 多因素解释；Castro战争、财政争议、法国/Tuscany/Venice/Modena政治联盟、Barberini领地计划、Taddeo指挥失败、外国军队、1527类比、税收/银器征收、1644年3月和约与Urban VIII死亡、混乱教宗选举、罗马市政当局与枢机团，以及Haskell对Innocent X赞助动机的评价。未具名军队、守卫、暴民、利益集团和个人保持匿名；作者对罗马人的概括标为修辞评价。正文脚注1–4均已挂接相应断言。



对照`CHP-6.pdf`物理第1页（印刷页146），核正OCR差异但不改S0：L3 `N August`印作`IN August`；L4 `Iwrote`为`I wrote`；L5 `earher`为`earlier`；L7 `the,panic`为`the panic`；L8 execration前的撇号不见于印本；首页注释L8 `CorresponJance`印作`Correspondance`。第6章将Castro战争写作“some three years”早于1645年8月，第二章p58则明记1641年；两种表达并存，S2收口时再判断作者是否为近似表述，不静默改年。L11“only one nephew”已由下一规范段L14的Camillo闭合；对应statement保留原始p146锚点并记录闭合位置。



### 印刷页147：`chp-6:06_CHP-6_sec_i:l13-24`



按L14–24逐行迁移，新增8个候选（Avignon、未具名Camillo之妻、Cornaro Chapel建筑空间、St Theresa作品提及、Time unveiling Truth组、St Peter’s首个campanile、未具名特别委员会、Borromini主持的Lateran改造工程）、74条精确跨度提及和26条原书断言。候选类型区分place与内部work；Rainaldi规划的Piazza Navona宫殿、St John Lateran建筑与Borromini改造工程分别保留，不将教堂建筑等同于内部作品。未将未具名外来国务卿、未具名妻子或委员会成员补成已知身份。



断言覆盖Camillo的教宗侄辈身份及政治权力方案、军事/行政任命、国务秘书任命、阿维尼翁使节职务、实际权力保留、1647年辞枢与婚姻；Donna Olimpia对Camillo的鼓励/阻挠、宫廷位置、作者评价及婚后驱逐；Barberini家族因调查威胁而离开、Francesco Maidalchini取代Camillo的安排；Innocent X对建筑及前朝艺术家的赞助选择；Pietro da Cortona与Oratorians；Bernini的Cornaro Chapel委托、Time unveiling Truth、campanile拆除决定，以及Rainaldi/Borromini取代其首席建筑师位置；Rainaldi宫殿、Lateran改造与Haskell“reactionary”评价。作者的“unfashionable”“hated rival”等措辞保留为Haskell评价，不作独立人格事实。正式关系未写入S6，原书关系事实保留为候选断言。



`CHP-6.pdf`物理第2页确认印刷页147，并校记L17 `17-y earold`→`17-year-old`、L20 `oflhe`→`of the`、`leading, architect`→`leading architect`；S0和`original_quote`均保留OCR原样。页147脚注1为“Besides Pastor, XIV, see Ciampi and Brigante Colonna”，挂点已登记在Camillo及其妻被排除于Rome的断言，待规范注释段`chp-6:06_CHP-6_sec_i:l120-157`迁移后回链。L24句末“reactionary in”未补全；L26–36从“character”续接，断言保持partial。



本次迁移后，全书覆盖为229段reviewed/complete、38段有理由排除、535段queued；候选6,273、提及8,951、原书断言4,567。`python scripts/audit_tables.py --summary`为0 errors；两条既存enrichment `source_ref`警告、535段未处理和语义质量待检查提示仍在。`python scripts/audit_s2_candidate_surfaces.py --chapter chp-6`扫描4个已迁移段，未发现未覆盖候选表面（启发式提示，不代表召回率或独立语义验收）；`python -m pytest tests/test_audit_tables.py -q`为11 passed。下一规范段为`chp-6:06_CHP-6_sec_i:l26-36`。



## 第六章印刷页148：`chp-6:06_CHP-6_sec_i:l26-36`（2026-09-29）



按S0规范源段L27–36逐行迁移印刷页148；L26为页码标记。对照`CHP-6.pdf`物理第3页核实正文与脚注。页147 L24“reactionary in”由L27“character”闭合；原statement `st-chp6-p147-major-works-reactionary-partial`已标为closed，并链接到本段 `st-chp6-p148-reactionary-continuation`。本段L36关于“some of the most beautiful and familiar achievements of the Roman Baroque”的句子未完，statement保留partial并指向下一规范段`chp-6:06_CHP-6_sec_i:l38-46`的L39“were created”。



本段新增3个候选：`cand-6278`为Gentile da Fabriano与Pisanello绘制、后被毁的Lateran壁画组（不虚构单件标题）；`cand-6279`为Algardi在St Peter’s未逐件指明的重要委托；`cand-6280`为Camillo Pamfili雇用的Antonio del Grande。复用现有候选记录Algardi、Bernini、Gentile da Fabriano、Pisanello、Pietro da Cortona、Camillo Astalli、Prince Camillo Pamfili、Donna Olimpia、Lateran basilica、Piazza Navona、St Peter’s、Pamfili palace、villa、Collegio Romano及Rome。Astalli与Prince Camillo分开；Piazza Navona教宗宫殿与Collegio Romano对面的Prince宅邸分开；Algardi别墅按书后索引暂映至Prince Camillo的别墅，留待S3核对。



本段新增64条精确提及、27条断言。断言分别记录：Innocent X时期对Rainaldi宫殿与Borromini教堂方案的评价；Lateran原壁画毁坏、旧结构保留及木顶改建穹顶计划因财政问题未能实现；Bernini被Algardi取代、两位艺术家作品与委托及风格评价、Four Rivers fountain使Bernini重获青睐但未复得完全权威；Cortona于1651年末获Piazza Navona教宗宫殿画廊顶棚壁画委托；Astalli受配宫殿、其亲缘和Pamfili名号；真正的Camillo Pamfili回罗马、艺术兴趣及赞助、Algardi建造其别墅、Camillo建造Collegio Romano对面宫殿并雇用Antonio del Grande。作者的“reactionary”“daring”“disillusioned”以及对人物兴趣、品味和流亡处境的评价保留为Haskell的措辞或解释；“may, perhaps”保留推测强度。



页148脚注1（L122）对应财政约束句，脚注2（L123）补充Bernini从Innocent X所得委托，二者均待规范注释段`l120-157`迁移后回链；此前页147脚注1（注释L121）也仍待处理。印本核对只记录校勘、不改S0：L29 ` ' basilica`前的OCR撇号印本没有；L32 `savour`印作`favour`；L34 `choice ofPietro`应读作`choice of Pietro`、`CamiUo`应读作`Camillo`；L36行首`- -`为OCR杂符，印本无对应字符；L36 `Use`印作`life`。引号和换行按印本保留。


迁移后全书为230段reviewed/complete、38段有理由排除、534段queued；候选6,276、提及9,015、原书断言4,594。`python scripts/audit_tables.py --summary`为0 errors；两条既存enrichment `source_ref`警告、534段未处理和语义质量待检查提示保留。`python -m pytest tests/test_audit_tables.py -q`为11 passed；章6候选表面审计扫描5个已迁移段，未发现未覆盖表面跨度（启发式结果，不代表召回率或语义验收）。
## 第六章印刷页149：规范段 l38-46（2026-09-29）

对照 CHP-6.pdf 物理第4页，迁移L39–46（含正文、分节符和本页脚注1），新增11个候选 cand-6281–cand-6291、57条提及和25条断言。页148 L36关于 Roman Baroque 成就的未完句由p149 L39“were created”闭合，statement st-chp6-p148-artistic-life-revival-partial 已连接至 st-chp6-p149-artistic-achievements-identified。L39分别指 Cortona 的 Aeneid 壁画与 Borromini 的 S. Agnese 穹顶/立面；L40记录 Camillo Pamfili 的赞助评价、Passeri 嵌套引语、Valmontone 的 Mola/Preti 未具名壁画、Baratta/Ferrata争议及 Bernini 的 S. Andrea al Quirinale 委托。作者评价和引述层级均保留，未把匿名争论者补成具名人物。

L41转入罗马财政困境并含章节分隔符；L42–43记录 Urban VIII 留下的国库债务、Innocent X 时期的财政措施、旱灾、第二次 Castro 战争与意大利经济衰退解释。L43末句“In Rome itself, where”保留 partial，并指向下一规范段p150 L49；本段结束后唯一未闭合断言为p149 L43→p150 L49。页149脚注1在本段L44–46迁入，支持 Cortona 壁画年代及 Borromini于1653年接手 S. Agnese 建筑项目；脚注2–7位于后置注释段 L124–129，尚待迁移后回链。该注释段L127的脚注编号需对照印本核定。

PDF核校只记录差异、不改S0：L43 OCR 的“under.Innocent”“To”分别依印本读作“under Innocent”“to”；L44 “di Cortona”印本为“da Cortona”，书名/人名 Brigand 校为 Briganti，并清理撇号、空格与大小写差异。表审计当时0 errors；语义账本计数以当前状态快照为准。

## 第六章印刷页150：规范段 l48-57（2026-09-29）

对照 CHP-6.pdf 物理第5页并查看物理第6页的续文，迁移L49–57，新增9个候选 cand-6292–cand-6300、44条提及和25条断言。关闭p149 L43“in Rome itself, where”至本段L49的局部经济叙述续接：Haskell称罗马贸易与工业规模有限、受意大利经济衰退的影响间接，并将海外贡赋减少归因于重商主义发展。1660年威尼斯使节关于各国阻止教会俸禄外流的概括明确保留为嵌套引语；其匿名身份未与书中其他威尼斯使节合并。

本段记录对临时税收、公共怨愤、Piazza Navona重建期间石块上出现的匿名意大利语诗句、教宗纪念性工程与小型项目所受经济压力的叙述；诗句脚注引Gigli p.233，未把引文定位冒充已读原始出处。Accademia di S. Luca在1648年的困境、未具名院长的改革提议、Mattia Preti见到艺术家失业、画商角色上升及对bamboccianti相对成功的抱怨分别建断言。引述层级、群体匿名性和作者的评价判断均保留。

页150 L56–57记录 Donna Olimpia 与 Prince Camillo拒付 Innocent X 棺木费用及争执葬费的说法，并区分 Haskell 的叙述、归于母子的引语和 Pastor 书目定位；Fabio Chigi/Alexander VII 的即位、Agostino “il Magnifico” 的身份、与 Raphael 的“legendary”友谊、Fabio 撰写 Agostino 生平，以及在 Cologne 任教宗使节13年均按原文限定记录。新候选包括匿名使节、重商主义、教会俸禄、匿名诗句、未具名学院院长、葬礼争议、即位事件、生平文本和 Cologne 地名；不从脚注推断尚未核读的事实。p150 L57止于“the intimate friend of”，statement st-chp6-p150-alexander-friendship-partial 指向下一规范段 l59-67 的 L60；当前唯一未闭合句为p150 L57→p151 L60。

p150脚注1–6分别在注释段L130–135，涉及使节引语、Gigli诗句、学院院长引语、Preti报告、母子对话及Agostino生平；均待该注释段迁移后链接。p147脚注1、p148脚注1–2、p149脚注2–7也仍待处理，p149脚注1已迁入。PDF校核记录 L57 的 OCR “faibiilou’sly”与“fife”分别印作“fabulously”与“life”；L54院长引语的撇号及标点按印本辨读，S0和original_quote保留OCR原样。

迁移后全书为232段reviewed/complete、38段有理由排除、532段queued；候选6,296、提及9,116、原书断言4,644。python scripts/audit_tables.py --summary 为0 errors；两条既存 enrichment source_ref警告、532段未处理及语义质量待检查提示仍在。python -m pytest tests/test_audit_tables.py -q 为11 passed。python scripts/audit_s2_candidate_surfaces.py --chapter chp-6 扫描7段，未提示未覆盖候选表面跨度；该启发式不表示召回率或语义验收。下一规范段为 chp-6:06_CHP-6_sec_i:l59-67。

## 第六章印刷页151：规范段 l59-67（2026-09-29）

对照`CHP-6.pdf`物理第6页及续页物理第7页，迁移规范源段L60–67。新增16个候选（cand-6301–cand-6316）、56条精确提及和20条原书断言；提及扫描发现并补记已有候选“意大利艺术”（cand-4131）的L65跨度，复扫未再提示遗漏。p150 L57“the intimate friend of”由p151 L60接续，关闭`st-chp6-p150-alexander-friendship-partial`并连接`st-chp6-p151-alexander-circle-friendship`。新断言分别记录Alexander VII与Urban VIII宫廷知识圈的关系、Alexander对Bernini的委托与复任赞助、圣彼得大教堂宝座和建筑/雕塑项目、教宗墓与Urban VIII纪念碑、Bernini门廊/广场/Scala Regia/Constantine像、Quirinal画廊装饰工程及Cortona的Santa Maria della Pace修复和未具名祭坛画；匿名艺术家群体、作品标题和日期不作补造，Haskell的风格判断、修辞和推测保留为其发言层。L67“despite the tremendous drains on the”尚未完句，建partial statement指向下一规范段`l69-76`的p152 L70“Pope’s finances”。

本页脚注1–4位于后置注释规范段`l120-157`的L136–139，挂点分别记录为pending，待该段迁移后回链。依据印本记录OCR差异而不改S0：L66 `painteda`印作“painted a”，`niahy`印作“many”，并清除句尾印本不存在的杂符；提及跨度仍严格保留规范源文本。L65“triumphal monument to Urban”与L66行首“VIII”按跨行跨度锚定同一候选。

全书覆盖更新为233段reviewed/complete、38段有理由排除、531段queued；候选6,312、提及9,172、原书断言4,664。`python scripts/audit_tables.py --summary`为0 errors，保留两条既存enrichment `source_ref`警告、531段未处理及语义质量待检查提示；第六章候选表面启发式复扫8段、未覆盖提示0条（不表示召回率或语义验收）；`python -m pytest tests/test_audit_tables.py -q`为11 passed。下一规范段为`chp-6:06_CHP-6_sec_i:l69-76`。

## 第六章印刷页152：规范段 l69-76（2026-09-29）

对照`CHP-6.pdf`物理第7页逐行迁移L70–76，新增4个候选（cand-6317–cand-6320）、38条提及和9条原书断言。p151 L67“tremendous drains on the”由L70“Pope’s finances”闭合，将`st-chp6-p151-economic-drains-partial`更新为closed。新候选分别登记Querini引语中的Leonine City、1656年罗马瘟疫、Haskell所概括的罗马独立艺术家群体，以及Sagredo所说的Corso；复用已建候选记录Bernini/圣彼得柱廊、Niccolò Sagredo、Giacomo Querini、Alexander VII、Quirinal、Salvator Rosa和相应地点。Sagredo的1661报告、Querini的政治性批评、Haskell对Querini夸张和真实衰败的区分、瘟疫及经济后果、Rosa 1662与1664两次引述分别按说话层记录；Querini关于列柱数、马拉里亚、居住状况及百万scudi的判断保持为其引语，不作为已验证结果。Rosa原文只称其写作，未识别收件人或文书标题，未新造书信对象。

页152脚注1–5的挂点记录为pending，后置注释规范段`l120-157`目标分别为L140–144。原始转录保留，按印本记校：L71行首多出的撇号不存在；L75 `òf`印作“of”；L76引语末OCR注号`6`印作上标5；注释L144的OCR编号`3`印作5，支持Rosa引文。此页未留下新的跨页partial statement。候选表面启发式提示Europe（cand-3462），已补跨度并复扫清零。

全书覆盖更新为234段reviewed/complete、38段有理由排除、530段queued；候选6,316、提及9,210、原书断言4,673。`python scripts/audit_tables.py --summary`为0 errors，保留两条既存enrichment `source_ref`警告、530段未处理及语义质量待检查提示；第六章候选表面启发式复扫9段、未覆盖提示0条（不表示召回率或语义验收）；`python -m pytest tests/test_audit_tables.py -q`为11 passed。下一规范段为`chp-6:06_CHP-6_sec_i:l78-89`。

## 第六章印刷页153：规范段 l78-89（2026-09-29）

对照`CHP-6.pdf`物理第8页迁移L79–89，新增3个候选（cand-6321–cand-6323）、56条提及和11条原书断言；候选表面启发式发现并补记已有术语候选“canvas”（cand-3571），复扫未提示遗漏。此前p152已闭合p151 L67“tremendous drains on the”至L70“Pope’s finances”。本段把法国外交危机、Alexander VII在1648年和约中的抗议、1662年Créqui事件与Avignon威胁、Bernini重建Louvre方案和赴巴黎、Jesuit General Oliva施压、罗马对Bernini留法的担忧、教宗权威/声望下降及Alexander VII时期反教权讽刺分别建断言。未具名教宗侄辈、廷臣、街头斗殴者及其他建筑师不补身份；Duc de Créqui只保留原文头衔与姓氏；将Haskell叙述、引语和评价分层。复用Rosa的La Fortuna候选并单独登记寓意人物Fortune；画作句在L89止于“a gathering of”，partial statement指向下一规范段`l91-100`的p154 L92。

p153脚注1–2位于注释段`l120-157`的L145–146，仍待回链；脚注1含对Treaty of Pisa条款的转述及反证提示，未将脚注书目定位当作已核史实。原始转录保留并据印本校记：L87 `principal-courtiers`无连字符；L88 `Alexander Vil’s`印作`Alexander VII’s`；L89 Pope前的杂引号及`institution os 'thé pdpacy`为OCR噪声，印作“institution of the papacy”；注释L145的`Satnek Ludovici`印作“Samek Ludovici”。

全书覆盖更新为235段reviewed/complete、38段有理由排除、529段queued；候选6,319、提及9,266、原书断言4,684。`python scripts/audit_tables.py --summary`为0 errors，保留两条既存enrichment `source_ref`警告、529段未处理及语义质量待检查提示；第六章候选表面启发式复扫10段、未覆盖提示0条（不表示召回率或语义验收）；`python -m pytest tests/test_audit_tables.py -q`为11 passed。下一规范段为`chp-6:06_CHP-6_sec_i:l91-100`。

## 第六章印刷页154：规范段 l91-100（2026-09-29）

对照`CHP-6.pdf`物理第9页迁移L92–100，新增8个候选（cand-6324–cand-6331）、52条提及和14条原书断言。L92的动物列表闭合p153 L89“a gathering of”，更新`st-chp6-p153-rosa-fortune-painting-partial`为closed。按来源区分Haskell对Rosa政治动机的保留、嫉妒对手的颠覆性解读、Baldinucci引述的入狱危机与Don Mario干预、Flavio委托Mei绘制Fortune under Virtue壁画、公众对Chigi财富的Fortune/Virtue解释、家族召回与致富引发的敌意、Flavio与Bernini合作重修SS. Apostoli宫殿、建筑内外评价、Mei寓意画、Ariccia肖像收藏及Canini/Gaulli装饰。Chigi家族、Virtue寓意角色与道德概念、Fortune图像与财富解释、画作与36人肖像组各自区分；借用索引中Colonna palace、Mei的Justice and Peace/Youth、Fortune画作及艺术家候选，不为未识别肖像、装饰画或古代雕像补题名。L99“iii”是节标题；L100句止于“first-rate”，partial statement指向下一规范段`l102-110`的p155 L103“artists”。

页154脚注1–4分别位于后置注释段`l120-157`的L147–150，均待迁移后回链；注释1的Getty Museum现藏说法也不当作已核验的独立来源。校记不改S0：L94句末OCR多出的短横线无印本对应；L98行首`-`亦为OCR杂符，印本直接作“is not a distinguished one”。

全书覆盖更新为236段reviewed/complete、38段有理由排除、528段queued；候选6,327、提及9,318、原书断言4,698。`python scripts/audit_tables.py --summary`为0 errors，保留两条既存enrichment `source_ref`警告、528段未处理及语义质量待检查提示；第六章候选表面启发式复扫11段、未覆盖提示0条（不表示召回率或语义验收）；`python -m pytest tests/test_audit_tables.py -q`为11 passed。下一规范段为`chp-6:06_CHP-6_sec_i:l102-110`。

## 第六章印刷页155：规范段 l102-110（2026-09-29）

对照`CHP-6.pdf`物理第10页，迁移L103–110；L102为页码标记，L110是脚注4续文。新增7个候选（cand-6332–cand-6338）、62条提及和26条原书断言。新增候选包括Kingdom of Naples及Grand Constable称号、Colonna家族图像收藏（类型暂未确定）、神话题材、风景画及其装饰实践、Resta引述中的风景画家群体、以及题名未明的Bellori 1942引文对象。复用索引候选Colonna家族、两处相邻但不同的宫殿、Filippo与Cardinal Girolamo Colonna、Palestrina、Barberini、Lorenzo Onofrio、Maria Mancini、Mazarin、Louis XIV、Queen Christina，以及Grimaldi、Rosa、Dughet、Maratta、Claude、Resta、Pascoli和Bellori。未识别的画作和collection清单不补造，个体画作赞助事实与风景画中Maratta人物画的限定分别表达。

p154 L100未完句“first-rate”由p155 L103 “artists”闭合：`st-chp6-p154-flavio-limited-interest-partial`改为closed，新statement记录Alexander VII时期Bernini重建宫殿的相对时间，并未推出绝对年份。本段继续记录Haskell关于赞助人数量/水平下降、经济与教宗政策、Colonna家族相对连续购画、家族宫殿重建、Palestrina售予Barberini、Lorenzo Onofrio的头衔与赞助、1661年婚姻、Maria Mancini在罗马社交地位、Colonna图像收藏、艺术家雇用和风景装饰偏好的叙述。Resta对风景画家与bamboccianti的批评保持嵌套引语；“seems”“at least partly”“helped to launch, or at least to confirm”“sometimes”等限定保留。p155 L109句末“take any note”建立partial statement，指向下一段p156 L113 “of the complaints of scholars or pedants”。

页155脚注1–5对应后置注释段L151–155，均待L120–157迁移后回链；脚注4文本在当前页OCR L110续接，引用Pascoli volume I和题名未明的Bellori 1942出版物，仅作为书目定位，不视为对Colonna patronage的独立验证。脚注5指向Bottari II，pp.115–116。按印本核对但不改S0：L109 `earher'days`印作“earlier days”，`hot much`印作“not much”；断词`bamboc- / " cisti.. .`印作`bamboc- / cianti...`；L110 `Bcllori`印作“Bellori”。

覆盖更新为237段reviewed/complete、38段有理由排除、527段queued；候选6,334、提及9,379、原书断言4,724。`python scripts/audit_tables.py --summary`为0 errors，保留两条既存enrichment `source_ref`警告、527段未处理及语义质量待检查提示；`python -m pytest tests/test_audit_tables.py -q`为11 passed；第六章候选表面启发式复扫12段、未覆盖提示0条（不代表召回率或独立语义验收）。下一规范段为`chp-6:06_CHP-6_sec_i:l112-118`。

## 第六章印刷页156：规范段 l112-118（2026-09-29）

对照`CHP-6.pdf`物理第11页迁移L113–118；L112为页码标记。新增9个候选（cand-6339–cand-6347）、49条提及和21条原书断言。新候选包括Claude受委托创作的八件神话题材组画、身份未明的Colonna家族地产、`separatione di letto`术语、Lorenzo Onofrio未注明日期的西班牙短访、Lepanto战役、Colonna宫殿大画廊、未具正式题名的战役壁画方案、Haskell称作“bold Venetian colouring”的风格术语及其用于比较的威尼斯贵族群体。复用索引候选《埃及之旅中的风景》《魔法城堡》、Claude最后一幅画《Ascanius shooting the Stag of Sylvia》、Marc’Antonio Colonna、Coli、Gherardi、Gaulli、Maratta；复用Ashmolean、Gesu、Altieri palace、Spain地理候选及Colonna家族/宫殿。画作组与作品单件、宫殿与画廊空间分开；作者对Lorenzo参与创作的“suggest”判断不升级为正式创作者关系，手稿未给出的具体estate和作品题名不补造。

p155 L109 “take any note”由本段L113 “of the complaints of scholars or pedants”闭合。记录Lorenzo对Claude持续近二十年的雇用、1662年购入《埃及之旅中的风景》、委托八件神话组画、有关家族寓意和Lorenzo参与创作的作者推断；Maria要求`separatione di letto`、Lorenzo的infidelities及她于1672离开；西班牙短访、公共生活退出与1689年死亡；“十四年前”相对时间下雇用Coli和Gherardi；Lepanto战役壁画在家族大画廊的安置、视觉/风格特征及Haskell对家族地位和威尼斯贵族类比的解释。没有从“十四年前”计算公历年份，也没有从作者的修辞推演未具名家族成员。

页156脚注1对应后置注释段L156，待L120–157迁移后回链。按印本记录OCR差异、不改S0：L117 `public Use`印作“public life”；L118 `Gesu`印作“Gesù”。本段末句完整；p155 partial关闭后，截至已迁移段没有待接续partial。`python scripts/audit_tables.py --summary`为0 errors，保留两条既存enrichment `source_ref`警告、526段未处理及语义质量待检查提示；`python -m pytest tests/test_audit_tables.py -q`为11 passed；第六章候选表面启发式复扫13段、未覆盖提示0条（不代表召回率或独立语义验收）。下一段为本节后置注释`chp-6:06_CHP-6_sec_i:l120-157`。


## 第六章合并注释 L120–157（2026-09-29）

按源序迁移第六章后置注释段`chp-6:06_CHP-6_sec_i:l120-157`。新增39个来源衍生候选、96条提及和37条注释/注释断言记录；复用前文已经迁移的p155注4续文，不重复建行。将第147–155页对应正文脚注全部回链，并链接p156注1至Claude相关断言。p156注2关于Antonio degli Effetti的引文已登记，但其sec_iv正文段`l3-5`尚未迁移，维持`pending_body_migration`。

L123单独记录Bernini在Innocent X时期的重要委托；L128记录Haskell对Brusoni诗歌内容的转述；L145区分Samek Ludovici的二手条款说法与Haskell对已出版条约版本的反证；L147将Paul Getty Museum位置限制为Haskell写作时的记载，不表述为当前馆藏事实。未把引文定位升级为独立验证。

逐行保留引文作者与出处不确定性，不扩展未识别作品题名。印本核图及S0校记：L127的脚注号印作5而OCR作6；L129`situarion`印作`situation`；L137`Alexander Vil`印作`Alexander VII`；L139`i960`印作`1960`；L144的脚注号印作5而OCR作3；L145`Satnek Ludovici`印作`Samek Ludovici`且页码`pp. in ff.`印作`pp. 111 ff.`。L155正文标注注5，页脚注标签印作1；根据Bottari II pp.115–116的内容对应，链接至Resta的引语并保留编号差异。均未改写S0。

覆盖状态更新为239段reviewed/complete、38段有理由排除、525段queued；候选6,382、提及9,524、原书断言4,782。表审计errors为0，两条既存enrichment `source_ref`警告和语义质量待核提示保留；`python -m pytest tests/test_audit_tables.py -q`为11 passed；第六章候选表面启发式检查14个已迁移段，未覆盖提示0条（不表示召回率或语义验收）。下一段`chp-6:06_CHP-6_sec_iv:l1-1`先按结构标题核对；随后处理sec_iv正文并回链注2。


## 全书S2精确锚点修复与第六章印刷页157（2026-09-29）

对mentions.csv逐条重算S0片段切片。132条既有提及的surface_form省略了OCR段硬换行，但start_char/end_char仍覆盖换行；132项在删除换行后均与旧表面形式一致，没有其他字符偏移类别。依字段契约将表面形式改为精确S0切片，偏移保持不变；备份为mentions.csv.bak-s2-anchor-linebreak-normalization-20260929。审计从132条字符切片错误降为0。

按印刷页序处理规范段chp-6:06_CHP-6_sec_iv:l55-72的L56–58：L56是印刷页157开头及正文，L57–58是该页脚注1–2；L55只是OCR生成的Footnotes结构标题，L59–72属于印刷页158–161脚注，暂留待对应正文审阅后回收。逐页扫描对照CHP-6.pdf物理第12页。新增候选cand-6390–cand-6405共16项、34条精确提及、21条原书断言/关系候选。新增或复用内容包括The Table/Pinax文本、Cebes署名异议、Socrates、Mascardi及Rome University、Antonio的Studiolo与gallery（作为不同空间候选保留）、入口处的Pinax图像复本、Antonio自编目录、Spon–Wheler旅行文献及其作者，以及King Midas、The Feast of Cleopatra、Armida、Danae和The Judgement of Paris五件题名作品。作品作者、媒材、年代、版本和现存状态均未见于此段，未补造；已索引的Poussin—King Midas条目、Tiepolo—Banquet of Cleopatra条目、神话人物Cleopatra均未据题名自动合并。Rome University候选与cand-5169 Sapienza保持待S3消歧。

本段关闭p156 st-chp6-p156-seciv-effetti-taste-fragment：p157 L56补全“Antonio品味只能从其自编目录得知”的句意；p156原句片段与p157续句分别按各自行号保存并互相链接。第157页注1扫描印作Wheler，S0 OCR为Wilder；书目L1128给出Spon与Wheler的旅行书目，故以引用定位记录，不视为独立事实核验。注2更正正文所报Cebes作者归属，实际作者未名，年代仅称probably first century A.D.。扫描还确认indiscriminately- / ransacked跨行连字符，S0 OCR粘连处保留并记校，不改来源文件。第157页脚注1、2分别回链到旅人对Studiolo描述和文本作者归属校正；第156页脚注2原有的Antonio资料引注维持独立链接。

覆盖台账现为240段reviewed/complete、1段reviewed/partial、39段excluded、522段queued；候选6,399、提及9,563、断言4,808。python scripts/audit_tables.py --summary返回0 errors；两条既存enrichment source_ref警告、全书未完成及1个部分迁移提示保留。下一规范段为chp-6:06_CHP-6_sec_iv:l7-10；L59–72脚注在页158–161正文迁移后回收。

## 第六章印刷页158：规范段 l12-26 与注释 L59-62（2026-09-29）

按源序处理印刷页158正文及同页脚注。正文段l12-26与脚注复合段l55-72分开锚定：迁入正文全部内容，并回收脚注L59-62的注1–4；复合脚注段仍partial，L63-72属p159–161脚注，待对应正文迁移后回收。新增候选cand-6408–cand-6423共16项、78条提及和40条断言／引文定位记录。保留Marucelli引介由p157 L9至本页L13闭合；分别记录Marucelli图书馆的未名目录与脚注提及的Mare Magnum，不预设两者同一。Adami 1667年的写作不假定为书信；Lord Essex、Francesco Drach身份未明；Bellori图纸候选与此前候选cand-5932的同一性留给S3。扫描核对CHP-6.pdf物理第13页：校记L13 “lais”/“his”、L14多余撇号、L15 “fdled”/“filled”、L18 Francesco Drach断行与缺空格、L23 “felt”前多余句点及rôle重音；均记录而不改S0。Bellori的Lives句在L26以“when he published”待p159续接。

## 第六章印刷页159：规范段 l28-38 与注释 L63-65（2026-09-29）

按印刷页序处理正文段 chp-6:06_CHP-6_sec_iv:l28-38 和复合注释段 chp-6:06_CHP-6_sec_iv:l55-72 中的L63-65。新增候选16项、正文提及90条、断言27条、脚注提及11条和注释记录5条。第158页Bellori写作《Lives》的跨页句由L29闭合：Haskell称其1672年出版，并把早年讲座收入为序言。

正文逐句记录Bellori的批评立场、Vasari/Baglione传统、Ideal及Agucchi、文艺复兴后mannerism的评价、Carracci圈子的复兴作用、naturalism与mannerism两端的风险、Caravaggio/Domenichino/Poussin、对Algardi/Bernini/Sacchi/Cortona/Maratta的差异化评价、1652委托、Bellori肖像、Chiari咨询和Raphael崇拜。嵌套引语中的Raphael评价归于Bellori所攻击的批评者；Haskell的解释、限定和引述层级分别保存。未命名的Maratta委托、肖像、两组壁画保留来源型候选，不补题名或现藏；Schlosser Magnino、Bellori 1942和Pascoli卷一仅作脚注书目定位。

扫描对照 CHP-6.pdf 物理第14页；S0原文不改。校记：L30 OCR archistorical，印作 art-historical；L34 OCR Use of Andrea Sacchi，印作 Life of Andrea Sacchi；L36-37 the'Vatican、the'cult的多余撇号不见于印本。L38页末“preparing the way for neo-classicism”续至下一段 chp-6:06_CHP-6_sec_iv:l40-50 的p.160 L41，相关断言保留partial。注释L66-72仍待p.160-161正文迁移后回收。

## 第六章印刷页160：规范段l40-50与注释L66-69（2026-09-29）

对照CHP-6.pdf物理第15页迁移规范正文段chp-6:06_CHP-6_sec_iv:l40-50的L41–50，并从复合脚注段chp-6:06_CHP-6_sec_iv:l55-72回收L66–69。新增19个候选、正文提及75条、原书断言20条及12条脚注提及、4条脚注定位记录。L40页码标记仅作版面导航。

闭合p159 L38 neo-classicism未完句：既有st-chp6-p159-prepares-neoclassicism-partial改为complete并关联本段续句。Haskell称Bellori反对以brio、unfinished、sketchy和belle matière为特征的竞争趣味，并称该趣味在罗马少有追随者“partly owing”于Bellori的影响；“in fact”“partly”及延后至另一章论证的限定均保留。风格和观念候选不与第2、5章的Ideal、古典主义及Baroque候选预先合并。

分别记录Bellori追随者将其观点硬化为教条、Maratta绘画与古典理想及高巴洛克的比较、Gaulli在Gesù的无题壁画所受敌意评价、对Bellori古典化影响的部分归因、Gaulli后续作品风格变化，以及来自其他城市（尤其Naples）的艺术家在罗马受轻视并被迫调整风格。vault评价作为Haskell转引的匿名艺术家集体发言，不为其成员补名。Jacomo di Castro的1670年引文与Haskell随后“部分是事实、部分反映批评家受到更多注意”的解释分开记录；没有把“critics”说成艺术衰退的原因。

Bellori 1671年任Accademia di S. Luca秘书、其后任Queen Christina图书馆员和古物学家，与Christina的年龄、1655年来罗马、游历、1689年逝世、社会文化影响及收藏分别建断言。转换发生时间未由“age 28”倒推。Christina在Palazzo Riario on the Lungara展示的藏画和父亲Gustavus Adolfus从Prague掠得的说法保留为Haskell陈述；画家名按绘画的转喻表达处理，不补作品题名。候选cand-5565（收藏）不与cand-1289（Hapsburg collections from Prague）直接合并；cand-5560在此处的Aldobrandini Titians可能与其先前版画模型语境相同，留S3对齐。Christina对Mola的判断止于L50“the most genuine heir to the”，续接p161 L53，不预补后续论断。

脚注L66–69分别记录avvisi/Roma XIX (1941) p.392、Jacomo di Castro致Don Antonio Ruffo的1670-09-20信及V. Ruffo 1916 p.290、Skippon p.676与Misson 1717 II p.167、Bildt 1904 pp.989–1003。信件、被引出版物及作者分开登记；标题或作者全名未在此处补造。脚注定位分别回链至Gaulli接收、Jacomo引文、Christina引语和收藏断言，不声称已读这些来源。复合脚注L70–72（p161）仍pending。

印本校勘记于过程，不改S0：L43 Maratta前多出的逗号不见于印本；L48–49印本为Correg- / gio，OCR在下一行额外生成- -；L48 OCR作Gustavus Adolfus，扫描作Gustavus Adolphus。mentions.surface_form仍严格对应S0，包括跨行原形。

迁移后全书为244段reviewed/complete、1段reviewed/partial、39段有理由排除、518段queued；候选6,451条、提及9,843条、原书断言4,910条。下一段为chp-6:06_CHP-6_sec_iv:l52-53（p161）；之后处理复合脚注L70–72。全书尚有queued/partial，不交S3。

语义复核补记：将Christina在Palazzo Riario展示收藏与Gustavus Adolphus从Prague掠得藏画拆为两个断言，避免把陈列关系与来源叙述混为一行；Bildt 1904作者候选与既有1906作者候选分开，留待S3裁决是否同一人；补录Bellori影响逐年增长这一独立判断。脚注4现同时回链到收藏陈列与来源陈述。

## 第六章印刷页161：第IV节末段及脚注交接（2026-09-29）

完成`chp-6:06_CHP-6_sec_iv:l52-53`逐行阅读，闭合p160 L50关于Christina赞赏Mola的未完句。对照CHP-6.pdf物理第16页，新增1个事件候选、16条正文提及和8条原书断言；正文涉及Mola与Gherardi的师生及Venetian colour、Bellori对Christina的引导与Canini赞助、Canini与Domenichino/Bellori的关系、Christina绘画赞助和Arcadia形成。保留Haskell的评价、限定和相对时间，不倒推年份或把赞助扩成委托。p161注1（复合段L70）已回链；先前误挂在p159 IDs下的p161注1、3、4提及按印刷页重标，删除本轮生成的两条重复跨度。

校记：OCR将`of little`连作`oflittle`，句号后多出逗号，并漏掉`protégé`重音；S0原文本不改。物理页脚注2已在第V节规范OCR L12，早先追加的单行视觉转录因此作为重复段有理由排除；第V节结构标题L1同样按版面元数据排除。p161注2–4的语义迁移及回链待第V节L3–12处理。

全书S2现为803段：245 complete、1 partial、41 excluded、516 queued；候选6,453、提及9,860、原书断言4,921。审计errors为0，下一段为`chp-6:06_CHP-6_sec_v:l3-12`。


## 第六章印刷页161第V节正文及注2–4迁移（2026-09-29）

完成规范段chp-6:06_CHP-6_sec_v:l3-12，并在复合注释段chp-6:06_CHP-6_sec_iv:l55-72中迁移p161注3、注4。第V节增加23个局部候选（cand-6461–cand-6483）、48条提及；注3增加5条提及；合计53条精确跨度提及、22条正文断言及4条引文定位statement。脚注2（L12）定位至前文Jesuits indignation判断；脚注3（L71）分别记录Bellori 1942 pp.91–94与A. Clark 1961 pp.190–193的定位，并登记文中仅由脚注识别的Berrettoni作品；脚注4（L72）定位到未完成装饰方案。脚注定位不作为独立事实核验。脚注1（L70）此前已回链。

核对CHP-6.pdf物理第16页：印刷页161第IV节末段与第V节之间分节；p161正文与脚注2位于第V节L3–12，脚注1、3、4位于复合段L70–72。扫描确认OCR的“Clement IXin”在印本为“Clement IX in”，“The'fresco”印为“The fresco”，“osa Barberini”印为“a Barberini”；S0和original_quote维持原始OCR。p161最后一句续至p162 L15的“or a Chigi”，以continuation_status=pending保留；候选cand-6482与cand-4813、fresco cand-6466与cand-1528/cand-5990均留待S3身份对齐。

更新后全书S2为803段：247段reviewed/complete、0段reviewed/partial、41段有理由排除、515段queued；候选6,476条、提及9,913条、原书断言4,947条。audit_tables.py --summary结构errors为0；保留两条既存enrichment source_ref警告及全书未完成/语义质量复核提示。下一段按来源顺序为chp-6:06_CHP-6_sec_v:l14-19（印刷页162）。

## 第六章印刷页162第V节正文迁移（2026-09-29）

逐行处理规范段`chp-6:06_CHP-6_sec_v:l14-19`，对照`CHP-6.pdf`物理第17页。新增候选cand-6484–cand-6513共30项、55条正文提及及25条原书断言。p161 L11关于Don Gasparo奢侈程度的未完比较由p162 L15“or a Chigi”闭合；更新既有statement `st-chp6-p161-v1-22`为complete，并将Chigi作为局部候选保留待S3对齐。

记录Claude的两幅作品及“his father”指代歧义；不将未具名父亲指认为Gasparo或Claude。威尼斯使节引文按Haskell转述、使节引述treasurers、treasurers谈其官员追债的层级分开，保留相对时间“three years earlier”、地区比较及奢侈批评的转述属性。其余正文分别记录Clement IX未实施的圣母大殿改造与葬所计划、家族和教士的反应、罗马市政当局据称拟议的反Bernini决议、Innocent XI继位与对土耳其进军的转述、Maratta为Guido Reni画作局部遮盖、严厉时期的戏剧/狂欢管控，以及Haskell转述法国使节关于Basadonna卧室的说法。把决议内容保留为嵌套指控，把Haskell“not wholly true”和“if we are to believe”限定保留；p162末尾“another witness”另作未名候选，不与法国使节混并。身份及跨章候选对应留待S3，不由共名预先合并。

印本校记不回写S0：扫描确认L16 `earlier`后为句点及脚注1标号，OCR误为问号且漏脚注标号；L18 `made worse by`被OCR连作`madeworseby`；L18末尾`Cardinal`与L19开头`Basadonna’s`跨行，mention按原始换行锚定。p162 L19法文引句未完，续至p163 L22的“1685?”，statement `st-chp6-p162-v1-25`保留pending。页内脚注1–7分别指向后续复合注释段`chp-6:06_CHP-6_sec_v:l47-70`的L48–54；注2、3、4、5分别链接覆盖其转引范围的多条相关断言，均先标pending，待该注释段按源序处理后再回链。

迁移后全书S2为803段：248段reviewed/complete、0段reviewed/partial、41段有理由排除、514段queued；候选6,506条、提及9,968条、原书断言4,972条。`python scripts/audit_tables.py --summary`返回0 errors；两条既存enrichment source_ref警告、514段未处理及语义质量复核提示仍在。下一规范段为`chp-6:06_CHP-6_sec_v:l21-26`（印刷页163），闭合p162末尾法文引句后继续正文；之后按源序处理p162注1–7所在的复合注释段。

## 第六章印刷页163正文迁移（2026-09-29）

处理规范段`chp-6:06_CHP-6_sec_v:l21-26`，对照`CHP-6.pdf`物理第18页并查看p164物理第19页确认续句。新增候选cand-6514–cand-6537共24项、38条提及及19条原书断言。先闭合p162末尾由另一位见证人说出的法文引句：印本为“1685.”并有脚注1标记，p162 statement `st-chp6-p162-v1-25`更新为complete并链接脚注L55。脚注所述法国反教宗情绪作为来源限定保留；该见证人与Basadonna段落中的法国使节仍分开。

正文记录Innocent XI对建造与永久纪念的态度、拒绝St Peter’s chapter的第三廊柱提案；Jesuits从西班牙国王获款、希望装饰Gesù tribune、申请使用教廷铸造设施，以及教宗要求保留资金和匿名编年者关于百名工匠可维持至少三年的反事实估计。外部身份未由职衔和日期推定。记录Maratta的委托减少、失业风险与罗马评论者教条化对外地画家迁居的影响，以及仍存赞助人、Barberini传统、晚期建造装饰并未停止、衰退与华丽成果并存等互相限定的作者论断。分别记录Clement XI在意大利各地委托、Haskell所引“若非Charles II之死和欧洲战事本可做得更多”的说法，以及Lateran Basilica工程由其他权势者承担大部分费用（其中包括Schönborn家族）；不把集体付款量独归该家族。末句引出未名的“most adventurous patron”，待p164续段识别，statement `st-chp6-p163-v1-19`保持pending。

注1–6分别对应后续复合注释段`chp-6:06_CHP-6_sec_v:l47-70`的L55–60，仍pending。扫描确认OCR的`1685?`为印本`1685.`且漏脚注1；S0不改写。p163 L26未完句由p164 L29“patron of the time”续接。迁移后全书S2为803段：249段reviewed/complete、0段reviewed/partial、41段有理由排除、513段queued；候选6,530条、提及10,006条、原书断言4,991条。`python scripts/audit_tables.py --summary`返回0 errors；两条既存enrichment source_ref警告、513段queued及语义质量复核提示仍在。下一段为`chp-6:06_CHP-6_sec_v:l28-33`（印刷页164）；之后按源序处理p162注1–7及p163注1–6所在的复合注释段。


## 第六章印刷页164–166、复合脚注L47–70与第七章结构排除（2026-09-29）

p164 L28–33按段落逐行迁入，对照物理页19。闭合p163 L26未完句；Ottoboni“most adventurous patron”处保留具体主语和赞助语境，未把其卡片/收藏或受赞助者关系提前归并。`Rothlisberger`等索引/接受对象只按具体语境复用，未补外部验证。该段新增14候选、39提及和29断言。p165 L35–40对照物理页20，新增10候选、59提及、26断言；作品、舞台布景、朋友关系与拒绝迁居分别记录，Mariette的法文叙述仍是嵌套转引。p166 L42–45对照物理页21，新增8候选、23提及、14断言；保留“financial uncertainty”“classical taste”“rivals”等作者解释，并区分欧洲列强与未具名的意大利其他城市。p166脚注1的“these pictures”按L. Crespi引用及紧邻上下文指向The Confession与六件Sacraments，不延伸到Solimena所送的未名画作；若后续材料产生冲突，仅回修该组藏址断言。

复合注释L47–70对照物理页17–21。逐项处理p162注1–7、p163注1–6、p164注2–5、p165注1–6、p166注1–2。Röthlisberger I p369、Barozzi e Berchet II p360、Pastor XIV p558、Roma 1670/1679 avvisi、Bellori 1942、Michaud I、Pascoli I/II、Hantsch/Scherf、Ottoboni库存手稿、Rava、Pascoli MS 1383、Waterhouse、Loret、V&A DT.33.b、Cametti、Mariette、Temanza MS 796、Tassi II、L. Crespi、Soprani II、Guidalotti Franchini及da Canal等均作为书内引用定位登记；除原书脚注的陈述外，不声称已读/验证这些被引来源。复用既有候选Barozzi e Berchet II、Pastor XIV、Bellori 1942、Pascoli I/II、Soprani II等，不以不同页码重复建档。

把脚注中的实质信息与引用定位分开：Bernini持续受攻击、法国报告的偏见警示、Basadonna墓及其所在教堂、Ottoboni的图画清册、Trevisani肖像现藏Bowes Museum、Juvarra设计稿收藏、Corelli与Ottoboni关系及Europa所有、Crespi作品藏址，以及p166的招募失败例证均各记为原书注释断言。未把法国使节与另一位匿名见证人合并；“Lazzarini the Venetian”依索引候选保留身份对齐待S3；“Europa by Ricci”不与另一个Europa题名候选强并；d’Adda作为引入Viani的主导者、Gozzadini与Albani作为支持者；施压Lazzarini的具体人未明，留空。

校勘不改S0：p162 L48 OCR的“Rothlisberger, s”据印本校为“Röthlisberger, I”；p165 L65“Lores”据印本与书目校为“Loret”；p165 L68 Temanza前脚注号印为5、OCR读作6，Tassi前的6无误；p165 L66 Corelli字形据扫描确认。注2/3在L66 OCR连排、p165两条注释按印刷脚注号拆开。

另外，`chp-7:07_CHP-7_intro:l1-1`和`l3-5`、`l7-9`，以及`chp-7:07_CHP-7_sec_i:l1-1`分别只是生成的文件标题、页码/分部标题和章标题；覆盖账本置为`excluded`并写明理由。下一段实际正文为`chp-7:07_CHP-7_sec_i:l3-9`（p3）；intro的L11–15保留排队，等p3正文标记与候选关系明确后按脚注编号回链。

历史快照（第七章p.3处理前，2026-09-29）：803段中253 complete、45 excluded、505 queued、0 partial；当前状态见下方p.3和p.170后续记录。


## 全书来源范围核对及第七章印刷页3正文／脚注1–5（2026-09-29）

### 全书范围与去重核对

- 复核source-registry登记的23份PDF：书前CHP-0Cover、正文CHP-1至CHP-17、结论／附录／第二版后记／书目／索引CHP-18至CHP-22。
- build_source_segments.py预览为66份规范Markdown、803个段，issues=0。88份Markdown中，17份01–17整章OCR和5份书后*_intro.md平行OCR不计入规范S0段；它们留作OCR差异核对入口，不与分节或书后规范文件重复计数。
- 13个视觉转录段来自第2–6章；第6章印刷页161重复脚注转录已在S2有理由排除。00_05_List_of_Plates.md覆盖书前图版目录、图版说明和图片来源；PDF原页仍是图注、图像对应及OCR疑点的核对来源。书目按引用来源处理，索引按候选定位处理，两者均不当作正文事实证据。范围清点只核定输入来源和去重，不代表这些材料的S2语义阅读已完成。

### 印刷页3正文

据CHP-7.pdf物理第3页核对规范OCR 07_CHP-7_sec_i.md L3–9。扫描版开头为带跨行下沉首字母的“In 1669”；OCR将I错序到下一行，形成“N 1669”与“Ipatron”。S0原文未改，S2语义按印本读作“In 1669”。正文及脚注2迁入17个正文候选、41条正文提及和17条正文断言／关系候选；复合脚注部分另增16条脚注提及、6条脚注断言／定位记录。全段新增17个候选、57条提及、23条断言／引用记录。

记录Rosa致G. B. Ricciardi的通信及其日常拒绝欧洲委托的自述；把罗马财政／政治衰落与教皇赞助困难、外部赞助者承接、经济衰退的条件性风险和未具名foreign intervention分别表达。保留“might well have”的反事实限定。Forabosco段区分Ruffo求画、Haskell所报等待两年和80 doppie的预期条件，以及Forabosco称欧洲王侯争相求画的转述；不称已付款、已交付，也不把two half-length figures扩成两件作品。广义艺商断言保留few、some、others的原有范围；Blackmail为Haskell评价。Crespi拒绝与建筑画家合作是完整表达的第一项条件，但行末his引出后续条件，故本段标partial，待下一段续接。

索引页码可局部映射Rosa、Ricciardi、Ruffo、Forabosco、Crespi及Liechtenstein王子候选；重复索引条目和跨章身份仍留S3处理。原文只称Prince of Liechtenstein而未给名字；索引候选cand-1405覆盖p.169，但不能据此在S2确认Prince Wenzel。未命名的维也纳王宫单列cand-6604；不并入可能相关的cand-1407。recession、foreign intervention、艺术家／赞助群体和未命名作品均保留范围限定，不补造具体成员或地点。

### 印刷页3脚注

物理第3页印本脚注为1–5。脚注1（Rosa信，1669-06-08；De Rinaldis 1939, p.221）、脚注2（Haskell 1959，已在正文源段L9）、脚注3（Ruffo, p.289）、脚注4（Gualandi I, p.38，Albani／Leopardi例及意大利语引文）、脚注5（Miller 1960, p.530）均作为书内定位分别记录并回链；不把书目定位当外部事实核验。07_CHP-7_intro.md L15把脚注5识为6 Miller, i960，据扫描校正为印本5／1960，原S0文本保留。

脚注4仅称Albani一例reported to Don Cesare Leopardi d’Osimo；引文没有给出报告者或确切文献类型。暂记未识别的报告／通信候选cand-6609，并标记其可能与既有cand-3545（1647年Berlingete Gessi致Leopardi书信）重合；不合并，交S3和书目核对。cand-6605至cand-6608只表达注释给出的De Rinaldis、Haskell、Miller、Gualandi定位，书名、版本和作者身份未从外部补定。

历史状态（第七章p.3处理后、p.170处理前，2026-09-29）：p.3脚注段`chp-7:07_CHP-7_intro:l11-15`为complete，p.3正文段`chp-7:07_CHP-7_sec_i:l3-9`为partial；全书为254 complete、1 partial、45 excluded、503 queued。p.170脚注1 Vaes, 1931, p.202在源文件L294，当前待脚注块`chp-7:07_CHP-7_sec_i:l293-389`按序处理。该状态已由本文件后续p.170记录更新。

## 第七章印刷页170正文迁移（2026-09-29）

按规范段`chp-7:07_CHP-7_sec_i:l11-19`逐行处理，并对照`CHP-7.pdf`物理第4页（印刷页170）。p.169 L8末尾Crespi的条件清单由p.170 L12续接；新增9个来源型候选、44条精确提及和22条原书断言/关系候选。更新p.169的Crespi条件statement续接指针并将前段由partial改为complete。

记录Crespi差旅费、仆人费用、住宿和每个空间的200西班牙金币要求，但不把条件写成已接受或履行；将他个人的成功评价与Haskell对供需机制的评价分开。外来王侯与未具名同等水平画家的court interest失败分别保留，Barberini家族衰落前后的罗马机会结构及教皇赞助变化不推广到未命名个体。

本段继续Haskell关于意大利艺术优势、16世纪François I／Charles V／Philip II收藏、Titian与Michelangelo身后声誉、Raphael比较和现代画家地位的论述。Van Mander嵌套引语单独记录：将Carracci仅按p.170索引主项映射；Cardinal Farnese不补名字；其无题壁画长廊不合并任何已知建筑或作品；Caravaggio姓名跨S0两行，提及跨度保留换行。评价中区分Van Mander引语与其内层“people say”转述。

L16 Amsterdam后的印本脚注1指向源文件L294 `Vaes, 1931, p.202`；在Van Mander statement中先记录到脚注段`chp-7:07_CHP-7_sec_i:l293-389`的待处理回链，不提前把该段登记为reviewed。p.170 L19末尾“able”续至下一规范段`chp-7:07_CHP-7_sec_i:l21-29`，故当前段保留partial；“one power”及其身份待续文确认，不在此段推定。

更新后全书S2为803段：255段reviewed/complete、1段reviewed/partial、45段有理由排除、502段queued；候选6,613条、提及10,291条、原书断言5,148条。`python scripts/audit_tables.py --summary`为0 errors；两条既存enrichment `source_ref`警告、502段queued及1段partial仍在。下一段为`chp-7:07_CHP-7_sec_i:l21-29`。


## 第七章印刷页171正文迁移（2026-09-29）

按规范段`chp-7:07_CHP-7_sec_i:l21-29`逐行处理，并对照`CHP-7.pdf`物理第5页。新增24个局部候选、58条精确提及和24条原书断言。p.170 L19的未名“one power”由p.171 L22“the Spaniards”闭合，更新`st-chp7-p170-i22`并链接至`st-chp7-p171-i01`；p.170原证据跨度仍限于L19。

记录西班牙人在四城委托及其在那不勒斯的活动、总督治理、意大利人文主义者与西班牙picaresque文化对绘画的对照，以及Ribera与追随者的“philosophers”作品。将总督群体、Ribera追随者、地方画家集体、匿名作品、建筑空间分别保留；不补未名人物或作品题名。蒙特雷伯爵段记录其与Olivarez的姻亲/影响关系、1630年欢迎Velasquez、购入Raphael/Titian作品、Titian两作在Aldobrandini与Ludovisi收藏间的转移及其后购买、当地反应；“两作为King取得”保留被动语态，不补执行者或King姓名。

记录Domenichino寻求总督保护及Monterey要求其违约转为替自己工作、Lanfranco的那不勒斯教堂壁画与后续宫殿画和萨拉曼卡祭坛画、Finelli自罗马来此工作。Domenichino合同作为未定位文献候选登记，但不声称原件存世。p.171 L29“work in the”仍为partial，待`chp-7:07_CHP-7_sec_i:l31-35`续接；下一段应继续处理p.172。

扫描核对确认p.171印刷注1–6对应源文件L295–300，分别在statement中链接到脚注段`chp-7:07_CHP-7_sec_i:l293-389`；这些脚注与p.170注1（L294）仍待该复合脚注段按序迁移，未提前标记complete。S0 OCR的“Neapohtan”按扫描记录为印本“Neapolitan”，原始来源及提及跨度保持不改。

迁移后全书S2为803段：256段reviewed/complete、1段reviewed/partial、45段有理由排除、501段queued；候选6,637条、提及10,349条、原书断言5,172条。`python scripts/audit_tables.py --summary`返回0 errors；仍有两条既存enrichment `source_ref`警告、501段queued及1段partial。下一正文段为`chp-7:07_CHP-7_sec_i:l31-35`。

## 第七章印刷页172正文L31–35迁移与复合源段边界校正（2026-09-29）

按规范段`chp-7:07_CHP-7_sec_i:l31-35`逐行处理，并对照`CHP-7.pdf`物理第6页。新增10个局部候选、34条精确提及和12条原书断言。初看三个索引候选的`canonical_name`似乎与作品/宫殿不符；核对完整候选行后确认，`cand-2125`的`sub_entry`为“Abduction of Helen”、`cand-1263`为“Death of Dido”、`cand-1483`为“Palace of Buen Retiro”，原提及与断言映射本来正确。撤销误按主名称拆出的3条重复候选并恢复原始关联。复用Philip IV、Rubens、Velasquez、Guido Reni、Guercino、Annibale Carracci、Domenichino、Claude、Jan Both、Nicolas Poussin及地点/类型候选。区分未名使节与未名代理、委托事件、作品组、Jeronymites修道院遗址和宗教团体；相对时间、外交混乱、作者对构图类型的历史叙述及“probably”“almost”“mainly”“to a lesser extent”等限定均按原文保留。核查说明：S1候选可能由`canonical_name`与`sub_entry`共同标识索引项，不能只看主名称判断是否错配。

扫描确认p.172 L31–35是菲利普四世转向罗马艺术家及风景画系列的完整后半页正文，脚注3、4分别引用L304–305。L35 OCR把“make names for themselves”“and it was”“Spain now”粘连；扫描核读后，提及/断言按可见行和原文跨度登记，S0来源文本不改。该段不是p.171 Finelli句的续文，故p.171仍为partial。

进一步核对规范源文件发现，复合段`chp-7:07_CHP-7_sec_i:l293-389`虽从L293脚注标题起，但L301包含印刷页172页眉及正文，续接p.171 L29的“work in the”；p.172脚注1–4在L302–305。p.170注1在L294，p.171注1–6在L295–300。whole-chapter OCR文件`07_CHP-7.md`中的相同p.172正文是重复副本，不另计S2段。已将p.171续接指针改为该复合段L301，并在queued覆盖说明中标明其混合内容及规范来源边界；不提前完成该段。

本段迁移后全书S2为803段：257段reviewed/complete、1段reviewed/partial、45段有理由排除、500段queued；候选6,647条、提及10,383条、原书断言5,184条。`python scripts/audit_tables.py --summary`为0 errors；两条既存enrichment `source_ref`警告及1段partial仍在。下一规范段为`chp-7:07_CHP-7_sec_i:l37-43`；复合段L293–389以后按源序处理并闭合p.171续句。

## 第七章印刷页173正文L37–43迁移（2026-09-29）

按规范段`chp-7:07_CHP-7_sec_i:l37-43`逐行处理，并对照`CHP-7.pdf`物理第7页。新增12个局部候选、53条提及和27条原书断言。索引候选按`canonical_name`与`sub_entry`整体识别：复用Giovanni Battista与Pietro Paolo Crescenzi、Claude、Poussin、Henry IV、Marie de Medici、Toussaint du Breuil、Ambroise Dubois等候选；`Gonzaga`索引项指向Mantua公爵条目，本段只读到“she was the niece”，故将Gonzaga与Mantua提及留待p.174，不预先写入本段。

新增未名威尼斯使节、Crescenzi家族、两兄弟未具名宫殿、Claude壁画组、法国政治/赞助群体、Henry IV巴黎建筑计划及执行群体、后期Mannerist装饰群体、巴黎的意大利艺术影响，以及Claude隐士系列之外的其他风景画和Poussin一或两件未识别的早期风景画。Rothlisberger的论证、威尼斯使节的嵌套转述与Haskell对其“过度怀疑”的反驳分层记录；两位Crescenzi对Claude的赞助和对西班牙事业的倾向拆成有据的个人关系候选。景观系列委托者保留为“Crescenzi本人或其兄弟”的不确定二选一，不生成正式边。法国段落区分Henry IV引语、作者对建筑计划的阐释、法国建筑师与工匠群体、绘画领域的Mannerist装饰评价，以及Marie de Medici与巴黎意大利影响之间的作者解释。

印刷脚注1–3分别在源文件L306–308；已将引文/判断链接到仍queued的复合段`l293-389`，不提前标记脚注完成。末句在L43止于“she was the niece”，statement `st-chp7-p173-i27`保留续接指针至`chp-7:07_CHP-7_sec_i:l45-59`的L46–47，故本段为reviewed/partial。扫描核对确认OCR差异：`Rothlisberger`印作`Röthlisberger`、`véry`为`very`、委托者二选一应为`or his brother`（S0作`of`）、`queje`应分写`que je`、`Mannerists`跨行断字，及`patriotic programme`的引号/断行；均只记校读说明，不改S0。

迁移后全书S2为803段：257段reviewed/complete、2段reviewed/partial、45段有理由排除、499段queued；候选6,659条、提及10,436条、原书断言5,211条。`python scripts/audit_tables.py --summary`为0 errors；保留两条既存enrichment `source_ref`警告、499段queued及2段partial；`tests/test_audit_tables.py`为11 passed。下一规范段为`chp-7:07_CHP-7_sec_i:l45-59`，将闭合p.173 Marie de Medici亲缘句并继续p.174正文；p.171 Finelli续句仍待复合段L293–389的L301。

## 第七章印刷页174正文L45–59迁移（2026-09-29）

按规范段`chp-7:07_CHP-7_sec_i:l45-59`逐行阅读并对照`CHP-7.pdf`物理第8页；扫描图确认本段为印刷页174。仅以分节OCR为规范来源，整章OCR副本不重复计入。新增23个候选（cand-6668–cand-6690）、82条提及和33条原书断言/关系候选。该段将上一段p.173 L43的Marie de Medici亲缘句闭合：Marie是Grand Duke Ferdinand的外甥女，未具名姐妹嫁给Mantua的Duke Vincenzo；cand-6668、cand-6670和cand-6671保持身份未决，不并入指向Ferdinando II的cand-1608或其他Mantua公爵。原书明确将Gonzaga称作家族，因此新增cand-6669；索引重定向cand-2906保留为不同候选，待S3对齐。

记录Marie于1601抵达Paris、对Louvre的反应及短住Gondi宫；Gondi家族的佛罗伦萨出身和约五十年前迁居、Gondi宫花园及Pietro Francavilla制作的Orpheus喷泉分别成候选。Henri IV被喷泉打动后召Francavilla到Paris；Francesco Bordoni是其助手和未来女婿。印刷注1在复合源段L309，尚未迁入，已给相关断言保留pending回链。

记录1604年Marie促使Grand Duke Ferdinand委托Giambologna制作Henri IV骑马像、拟置Pont Neuf；将此像与Grand Duke本人已有的骑马纪念像区分。Marie要求拆取后一像的马匹并说明可日后替换，但请求未获准。前一纪念像由Pietro Tacca和Francavilla完成，十年后才到达；印刷注2位于复合段L310，仍待处理。扫描核实OCR`Pont Neus`为印本`Pont Neuf`，S0不改。

随后Marie将艺术关注转向Mantua，召Franz Pourbus the Younger至Paris；他于1609年抵达并绘制Marie与宫廷的多幅肖像。Henri IV在世时，她的艺术兴趣主要限于珠宝、银器和其他工艺；1610年Henri遇刺后，Marie野心增长，摄政时期状况恶化。1611年她命Salomon de Brosse在购自未名Duke of Luxembourg的旧宅址建造新宫。印刷索引在p.174列有`Luxembourg, Palais du`，故新宫映射至cand-1461；旧宅和卖方分别用cand-6683与cand-6684保存，不作实体合并。Marie向未名姨母Grand Duchess索取Palazzo Pitti图样并希望仿建；实际方案不同，工程又因她卷入的内部问题延误。印刷注3在L311，保持pending。

还记录Marie于1620年前后重新掌权并欲彰显胜利；1621年Rubens被接洽为新宫两条长廊绘制描绘Marie及Henri IV生平的寓意场景。是否因Rubens与Mantua宫廷的关系而获选仅为原书的probably；分开保留宫廷、两条建筑长廊和绘画周期。周期沿用cand-4733，但其与既有跨章作品身份暂不强并。Haskell说明该项目重要但本章将多谈很快进入Marie宫廷的托斯卡纳画家Orazio Gentileschi；印刷注4在L311，仍pending。末句L59止于`and`，按L175 L62“stayed for less than two years”设置continuation，当前段migration_status=partial。

扫描记录不改S0：L49 OCR`was-so`印为`was so`；L53 OCR`Pont Neus`印为`Pont Neuf`；L57 OCR`due du Luxembourg`印为`duc du Luxembourg`，`ofhis`印为`of his`；L58 `artists,„more`印为`artists, more`。p.173 L43已由本段L46–47接续，原statement保持p.173来源锚点并记continuation resolved，不跨段改写原文引句。

迁移后全书S2为803段：258 complete、2 partial、45 excluded、498 queued；候选6,682条、提及10,518条、原书断言5,244条。表审计errors为0；两条既存enrichment `source_ref`警告、498段queued及两个reviewed但未完整迁移的段仍在。下一规范段为`chp-7:07_CHP-7_sec_i:l61-74`；p.171 Finelli续句仍待复合段L293–389的L301。

## 第七章印刷页175正文L61–74迁移（2026-09-29）

按规范段`chp-7:07_CHP-7_sec_i:l61-74`逐行阅读并对照`CHP-7.pdf`物理第9页；扫描确认印刷页175。S0分节OCR是唯一规范源，整章OCR副本不重复计数。本段新增15个候选（cand-6691–cand-6705）、84条实体提及和32条原书断言/关系候选。p.174 L59 Gentileschi句由本段L62闭合：Orazio在1623年到达后的停留不足两年，Haskell把原因推测为他可能因Rubens受到的欢迎而受挫；原句锚点仍留在p.174，续接记入`st-chp7-p175-i01`。

记录Gentileschi绘画对Louis Le Nain、Laurent de la Hyre和Philippe de Champaigne风格的影响（这是Haskell转述的研究判断，不等于直接师承）；索引候选`cand-1136`对应《Public Felicity triumphant over Dangers》，其委托关系与图像描述分别记录。Marie的新宫复用`cand-1461`，不与别处新建宫殿混淆。

第175页将1624年Ferdinando、Mantua公爵追求法国宫廷称其为“Altesse”与画作馈赠联系起来：保留未具名驻巴黎大使及其来往通信候选，记录Baglione从罗马带来的十幅Apollo与Muses画作、Marie对裸体/情色程度的请求，以及接受状态未知。不同画作不并入Gentileschi的《Public Felicity》；“proposed sending”不写成已送达或已受赠。`cand-6670`的Duke Vincenzo在相邻页被再次称作Ferdinando之父；当地关系支持该同一候选，具体统治者身份仍留待S3。

另记录Cardinal Richelieu对意大利艺术的代理采集、Ferdinando所用的未名意大利画家群、Richelieu欲引入巴黎的画家群，并复用候选`cand-6667`；Isabella d’Este的studiolo作为place，与Perugino、Mantegna、Lorenzo Costa和Correggio的未指名画作组分开。原文将画作列为Richelieu所求masterpieces的例子，不据此断言他取得了具体作品。保留“must have”“no doubt”等推测，区分French court机构、France政治实体与地理France；Château de Richelieu、其所在地和Cardinal Richelieu分别建模。Bonnaffé引文保留匿名引述层级，不把脚注当作已核实的历史事实。

印刷页脚注1、2在复合源段L312–313，现仍以pending回链保存：L312为Baudson和《Il Seicento Europeo》定位，L313为Bonnaffé p.269。复合段尚未处理，不能因此标完成。

扫描校读只记入S2，不改写S0：L62 OCR在“the”前多出连字符；L64 `Duke ofMantua`应读为`Duke of Mantua`，`was ” told`无引号；L65法文`tout á fait núes`按印本为`tout à fait nues`；L67 `Alustre`应读作`illustre`、`agents.of`为`agents of`；L72 `avaflable`为`available`；L73 OCR `protege`漏掉印本重音`protégé`。本段L74止于“made”，续至p.176规范段L76–89的L77“a cardinal”，故coverage为reviewed/partial；p.171 Finelli续句仍待复合段L301。

迁移后全书S2为803段：259 complete、2 partial、45 excluded、497 queued；候选6,697条、提及10,602条、原书断言5,276条。`python scripts/audit_tables.py --summary`为0 errors；`python -m pytest tests/test_audit_tables.py -q`为11 passed。两条既存enrichment `source_ref`警告、497段queued及两个partial段仍在。下一规范段为`chp-7:07_CHP-7_sec_i:l76-89`；p.171 Finelli续句仍待复合段L293–389的L301。


## 第七章印刷页176正文L77–89迁移（2026-09-29）

按规范段`chp-7:07_CHP-7_sec_i:l76-89`逐行阅读并对照`CHP-7.pdf`物理第10页；扫描确认印刷页176。S0分节OCR为唯一规范源，未把整章OCR副本重复计入。新增14个候选（cand-6706–cand-6719）、87条提及和34条断言。复用Mazarin、Richelieu、Poussin、Jean Lemaire、Duquesnoy、Paul-Fréart de Chantelou、Pietro da Cortona、Guercino、Stefano della Bella、Bernini、Philippe de Champaigne、Algardi、Urban VIII等既有索引候选；新候选承载未具名信件、未名官员/使节、群体、Livorno地点、Bernini学生、未识别的Champaigne三人肖像、招募中的胁迫机制及Poussin妻子等，不越界推定身份。

正文记录Mazarin受任法国利益代表赴科隆会议、Richelieu促其赴法、Poussin致Jean Lemaire书信及其对意大利画家招募的预测；将Haskell对Mazarin发起招募政策的推断、Poussin被引述的贬抑判断和招募结果分层。Chantelou奉命赴罗马带回Poussin并招募其他艺术家，Cortona与Guercino只是希望招募对象；“everyone concerned”不拆分归责，少数被带回的次级画家保持未名。威胁至贿赂被记录为Haskell对招募手段的叙述，不补造行为人和具体交易。

另记录Stefano della Bella在一位未具名佛罗伦萨使节服务下到巴黎并居留工作十年；Barberini家族准许Bernini及未名学生制作Richelieu胸像；未识别的Champaigne三人肖像被Haskell称作胸像几乎确定的来源，保留其推断性质。Richelieu死后招募计划延续，Poussin回罗马被Haskell称为以取妻为由，Duquesnoy在Livorno即将启航时去世；Mazarin随后以高额薪俸招Bernini赴法的尝试止于Urban VIII句首，L92续文未处理。

p.175 statement `st-chp7-p175-i32`由p.176 L77续接闭合，保留原句在p.175的来源锚点，并关联p.176续接断言`st-chp7-p176-i01`、`i02`。p.176末句记录为`st-chp7-p176-i33`，continuation指向`chp-7:07_CHP-7_sec_i:l91-100` L92。印刷脚注1–9分别回链至复合源段L314–318，均保持pending，未把书目定位当成独立事实核验。

扫描校读只记S2、不改S0：L79 `pokey`为`policy`；L81 `reaksed`为`realised`；L83 `earker`为`earlier`；L84 `deka Bella`为`della Bella`、`chmate`为`climate`、`briUiant`为`brilliant`；L85 `akies`为`allies`、`Phikppe`为`Philippe`；L89 `Richekeu`为`Richelieu`。p.176处理后、p.177迁移前的阶段快照为260 complete、2 partial、45 excluded、496 queued；候选6,711、提及10,689、原书断言5,310。p.176 L89句随后由p.177 L92闭合；p.171 Finelli续句与p.176脚注1–9仍待处理。

## 第七章印刷页177正文L92–99迁移（2026-09-29）

据规范段`chp-7:07_CHP-7_sec_i:l91-100`逐行阅读，并对照`CHP-7.pdf`物理第11页（印刷页177）。处理正文L92–99；本段L100是脚注4在印刷页上的续尾，暂不把残句当作完整脚注证据。L99在“if he would”处跨页至下一规范段`l102-111` L103，故coverage为reviewed/partial，下一步应先闭合该句。

新增19个候选、52条精确行内提及和27条断言。复用Urban VIII、Bernini、Rome、Lord Arundel、Charles I、Rubens、Van Dyck、Naudé、Guercino、Italy、England、connoisseurship等既有候选。新候选覆盖：未具名的Mantua公爵及其画作收藏（收藏类型目前不在九类taxonomy中，type留空）；Barberini regime；Charles I未具名的courtier、agents及招募对象；未具名妻子与Cardinal Barberini；Inquisition；Counter-Reformation、Catholic humanism、Puritan court objection、England-Rome政治缓和及其1642年破裂；复用索引候选cand-1271指向Guercino的Semiramis画作；审美价值与再现内容的区分；Charles I的艺术政策和英格兰对当代意大利文化的尊重。语境不足的身份不从常识补齐。

断言分层记录：Urban VIII在临终时仍掌握Bernini的 patronage authority，其“Rome is made for you”一语是Haskell报告的说法；Urban VIII去世后Bernini遭遇“bad days”保留原文概括，不扩写事件。欧洲诸国的努力未能匹敌Barberini regime但未具名；英格兰招募意大利艺术家的效果被称为类似不佳。记录Arundel、Charles I及少数courtier的艺术热情、Charles I购入Mantua公爵画作收藏及其对欧洲统治者的影响、Naudé对Arundel的嵌套引述；区分Charles I雇用Rubens/Van Dyck与他此前反复招募意大利艺术家失败。保留Haskell对Charles I看法不同的推断，不把引文写成外部验证的事实。

另记录Charles I及其minister改善英格兰与Rome隔绝关系的努力；妻子和courtier的天主教身份、未指名的改宗、penal laws仍在但执行减弱、英格兰人赴Rome的旅行与外交往来。Cardinal Barberini具体身份、Inquisition审理机关均未指定。Catholic humanism、connoisseurship与审美/再现区分、有限的court elite、Puritan opposition及1642年的政治宗教平衡破裂分别入断言，保留Haskell的因果和评价措辞。

脚注标记1–5回链至复合段L319–323，均为pending；脚注4还保留本段L100尾句定位，待与L322前文合并。L95 OCR `osali`经扫描确认应为`of all`；L98 OCR `artisricpolicy`印本为`artistic policy`。S0不改写，校读只登记在本阶段。没有写入正式关系，候选边留到S6审查。

本次迁移后全书S2为803段：261 complete、2 partial、45 excluded、495 queued；候选6,730条、提及10,741条、原书断言5,337条。`python scripts/audit_tables.py --summary`为0 errors；`python -m pytest tests/test_audit_tables.py -q`为11 passed。尚有两条既存enrichment `source_ref`警告，p.171与p.177两个partial及495个queued段。下一正文段为`chp-7:07_CHP-7_sec_i:l102-111`；复合段`l293-389`仍待按源序处理。

## 第七章印刷页178正文L103–111迁移（2026-09-29）

逐行核对规范段`chp-7:07_CHP-7_sec_i:l102-111`与`CHP-7.pdf`物理第12页。L102为页码导航，语义处理L103–111，新增7个候选、53条精确提及和24条断言。p.177 statement `st-chp7-p177-i27`由L103的“settle at his court”闭合；p.177正文已结束，但该段L100仍包含脚注4尾句，coverage继续partial，等复合段L322。

复用Guercino、Albani、Charles I、Pietro Tacca、Ferdinando II de’ Medici、Orazio Gentileschi、Duke of Buckingham、Rubens、Inigo Jones、Veronese、Francesco Fanelli、Giambologna、Francavilla、Duke of Newcastle、Charles II为Prince of Wales及作品索引候选。新候选为Queen’s house（未给地点）、Muses/Virtues画布组、Venice的Libreria、Divine Right of Kings、Caravaggist influence、Fanelli未逐件识别的小型青铜作品组，以及Charles I欲聘Tacca创作两匹马但被Grand Duke拒绝授权的未成事件。London、Paris、Venice、Florence等地点按同一地理实体复用。Tacca事件只记愿望与拒绝，不推成正式发包或作品完成；“Albano”保留在信件转引的拼法，正文后文作Albani；她的拒绝原因明确保留未知。

正文断言按语气和对象拆分：Guercino的拒绝及所引理由是“we are told”的转述；Charles I邀请Albani的时间为“可能紧接”，不得改成确定时间；Pietro Tacca赴伦敦未获授权。Charles I最终聘用的画家、雕塑家分别指向Orazio Gentileschi和Francesco Fanelli；Gentileschi在Paris的风格演变、英国宫廷欢迎、宗教题材画作及政治性大型委托分开记录。Stuart宣传、Rubens的更强画笔与Gentileschi画作“政治无害”均保留Haskell的判断。Queen’s house位置及Queen身份未据常识补齐；画布与Libreria的关系记作风格回望，不说成复制。画作磨损、是否曾出色、人物疲惫思乡和画家排名保留评价/概率措辞。

Fanelli部分分开记录其佛罗伦萨来源及雕塑训练传统、英格兰小型青铜作品与马/肖像题材、Duke of Newcastle的赞助兴趣、其任Charles Prince of Wales监护人及骑马兴趣、Fanelli用文献抬高马主题、以及Charles II小像和Charles I胸像。胸像审美评价保持Haskell评论，不写作客观测量。

扫描校读：L106 `1625/`是句点与脚注4标记，不是斜线；L110 `rewarded.'`的撇号状符号是脚注6；页脚OCR把注5号码录成6，页图可见注5为Orazio之女Artemisia赴英的说明，下一条才是注6。p.178注1–6的正文行引用分别为复合段L324–329，均暂置pending；注1的Mahon评论认为Semiramis与Charles I邀请可能无关，待复合段按源序处理后更新`st-chp7-p178-i02`和p.177邀请断言的限定。脚注引用没有在本次正文迁移中当成已读事实。

本次写入后S2为803段：262 complete、2 partial、45 excluded、494 queued；候选6,737、提及10,794、原书断言5,361。审计0 errors；`tests/test_audit_tables.py`为11 passed。当前partial为p.171 Finelli句与p.177脚注4尾段。下一规范段`chp-7:07_CHP-7_sec_i:l113-126`（印刷页179）；复合段`l293-389`仍按源序待处理。

## 第七章印刷页179正文L114–126迁移（2026-09-30）

逐行阅读规范段`chp-7:07_CHP-7_sec_i:l113-126`并核对`CHP-7.pdf`物理第13页。L123为分节版面标题，不作为正文；迁移L114–122、L124–126，新增17个候选、79条提及和27条原书断言。记录Fanelli与Arundel的墓葬计划、Charles I的Bernini胸像及Van Dyck三人肖像、Baker胸像、Arundel 1636年11月书信与另议浮雕、Caroselli委托、未具名Cardinal Barberini赠予Somerset House chapel的Reni《Bacchus and Ariadne》、取消委托及Fanelli赴巴黎、Gentileschi去世、1640/50年代分期、Mazarin和1648年和平条款。引文、作者评价、未成委托与实际作品/关系分别记录。

身份和类型保持边界：L118的Francesco（送信人）与L119的young sculptor Francesco分开；“Italian amateur”与Mazarin的关联须结合p.180续文理解，暂保留跨页推断；Little Tom及其关系未决；Urban VIII nephews保留集体指称，未强塞个人类型；p.179的未具名Cardinal Barberini不与p.177候选合并。p.179注1回链至Queen's bust plan；注2–6仍在复合段L330–334待处理。L125末句止于“and”，由p.180 L129续接，因此本段coverage为reviewed/partial。

扫描校读只记录于S2，不改S0：`-record`、`T send`、`bye me`、`sine taste`等处以页图校正OCR误识，破折号亦按印本辨读。写入后全书S2为803段：262 complete、3 partial、45 excluded、493 queued；候选6,754、提及10,873、原书断言5,388。修正5条候选来源锚点后，`python scripts/audit_tables.py --summary`为0 errors；仍有两条既存enrichment `source_ref`警告、493段queued及3段reviewed/partial；`tests/test_audit_tables.py`为11 passed。下一规范段为`chp-7:07_CHP-7_sec_i:l128-138`（印刷页180）。

## 第七章印刷页180正文L129–138迁移（2026-09-30）

逐行处理规范段`chp-7:07_CHP-7_sec_i:l128-138`，并核对`CHP-7.pdf`物理第14页。L128为页码标记，迁移正文L129–138；新增13个候选（cand-6764–cand-6776）、78条精确提及和35条原书断言/关系候选。p.179 L125跨页句由本段L129闭合，p.179 coverage仍因注2–6在复合段L330–334待处理而保持partial。新增法国政治实体候选cand-6764，并将p.179“French affairs”的提及和断言从地理候选修正到该政治实体；不改变另一个“French hands”地理/控制语境。

记录Mazarin接掌法国政府、出生于Abruzzi未具名村庄、耶稣会教育、Colonna家族服务与Valtellina军事/外交经历；Giovanni Francesco与Giulio、Marcello Sacchetti的兄弟关系及Mazarin成为Sacchetti家族protégé；Bentivoglio支持、Mazarin在Cardinal Antonio Barberini之下活动、法西Mantua继承战争及Urban VIII相关外交叙述。保留作者将教宗指向Urban VIII的上下文推断。国家/地区区分地理西班牙与战争中的西班牙政治实体，区分Mantua城市与继承争端中的公国；Puritans保留为未定类型的集体称谓，regiment、Mazarin父亲及其出生村庄不补造身份。

记录Leonora Baroni、Mazarin的交往与收藏判断、Bentivoglio“apparently lent”款项、Laterano canonry及其收入，保留“most reports”的转述层。委托Poussin一事保留“first seems”、价格“doubtless”、Barberini圈可接近性等推测；Inspiration du Poète与Diana and Endymion作为具名作品候选，保留“may have painted”和审美评价，不据正文断言具体版本。L138比较句止于“and the”，已设p.181 L141续接，故p.180 coverage为reviewed/partial。

扫描核读与S0分开保存：L129印作“art just”，OCR粘连为“artjust”；L134的protégé断行和连字符依页图记录；L136 `operatic ‘stardom’`及破折号按印本；L138题名为“Inspiration du Poète”。脚注1–4位于复合段L335–338，均未提前标为已迁移；注3对委托年代提出限定，注4涉及作品收藏地点，后续应分别连接/修订对应断言。

迁移后全书S2为803段：262段reviewed/complete、4段reviewed/partial、45段有理由排除、492段queued；候选6,767条、提及10,951条、原书断言5,423条。`python scripts/audit_tables.py --summary`为0 errors；两条既存enrichment `source_ref`警告仍在；`python -m pytest tests/test_audit_tables.py -q`为11 passed；`git diff --check`通过（仅提示仓库现有行尾转换）。下一规范源段为`chp-7:07_CHP-7_sec_i:l140-148`（印刷页181），用于闭合L138比较句；复合段L293–389仍待按其混合正文/脚注内容处理。

## 第七章印刷页181正文L141–148迁移（2026-09-30）

逐行处理规范段`chp-7:07_CHP-7_sec_i:l140-148`，并核对`CHP-7.pdf`物理第15页。L140为页码，迁移L141–148；新增10个候选、49条精确提及和29条原书断言。L141闭合p.180 L138的Poussin画作比较句；同页L148末句“ It was also”续至p.182 L151，因此p.181正文段仍partial。p.181脚注1–4分别位于复合段L339–342，尚未迁移。

分别记录Haskell对Poussin两画与Giorgione、年轻Titian的比较、未确定画作主题、古典抒情诗与神话题材，以及Mazarin不再关注Poussin职业生涯；Brienne多年后的评述作为Haskell的嵌套转述保存，既保留其对Mazarin品味的批评，也保留Haskell认为该描述整体可信的判断。Mazarin画像中“we can visualise”的部分明确是作者想象，而非有出处的具体场景；法文引语标作Brienne被Haskell转引。随后记录Mazarin在巴黎定居、获枢机身份、Richelieu与Louis XIII去世后的艺术赞助条件，以及其招募Bernini、意大利音乐家和其他意大利艺术家的尝试、Romanelli回到罗马后的处境、宫殿上层画廊的装饰计划。未把提议的Roman histories写成已完成作品；区分宫殿与上层画廊；保留Ovid《变形记》相较历史题材的选择、作者判断和Mazarin与Poussin关系的“probable”限定。候选中未枚举群体及古典诗歌/神话表达按既有S2候选惯例保存为待裁决对象；本段不写正式关系边，留待S6审查。

页图核读作为S2校勘记录，未改写S0：OCR中的“bathed, in”校读为“bathed in”，“the-first”校读为“the first”，“vid”校读为“Ovid”，“comforming”校读为“conforming”；法文引语页图首词为“Son Eminence”，规范源段OCR的“JSon Eminence”仍作为原文跨度保留。p.181注1补充Brienne说Mazarin并无Poussin作品、但很可能特指后期作品，直接限定正文“忽视成熟作品”的转述；注2指向Brienne原文页码，注3引用Mazarin一书第xxxiii页，注4为Romanelli致Francesco Barberini的1646年7月6日信件。各注待复合段按页序迁移后再修订对应断言，不提前使用脚注内容。

写入后全书S2为803段：262段reviewed/complete、5段reviewed/partial、45段有理由排除、491段queued；候选6,777条、提及11,000条、原书断言5,452条。`python scripts/audit_tables.py --summary`为0 errors；两条既存enrichment `source_ref`警告、491段queued及5段reviewed但迁移未完整仍在；`python -m pytest tests/test_audit_tables.py -q`为11 passed；`git diff --check`通过（仅提示仓库现有行尾转换）。下一规范段为`chp-7:07_CHP-7_sec_i:l150-158`（印刷页182），用于闭合p.181 L148；复合段L293–389仍须处理p.170–181脚注与p.172 L301正文续句。

## 第七章印刷页182正文L151–158迁移（2026-09-30）

逐行处理规范段`chp-7:07_CHP-7_sec_i:l150-158`，并核对`CHP-7.pdf`物理第16页。L150为页码，处理L151–158；新增8个候选、62条提及和24条原书断言。p.181 L148 “It was also”续句由本段L151闭合；p.182 L158的引语在“so many promises,”处未完，续至p.183 L161。p.182注1–5位于复合段L343–347，待按复合段既定源序迁移。

记录Romanelli在Mazarin上层画廊的题材倾向、对画廊空间与壁画格局的判断、分隔壁画的嵌板结构及Haskell关于法国趣味和意大利巴洛克的评价；题材逐项复用Romanelli索引候选，不与其他同名作品合并。记录Mazarin治下意大利艺术在巴黎的扩散、Giacomo Torelli于1645年由身份未明的Duke of Parma派往巴黎及其布景/技术评价、Giovanni Francesco Grimaldi于1648年为Cardinal画廊补绘风景。匿名potentates送画、Marchese Bentivoglio于1639年委托Guercino《Carità Romana》、Mazarin购入Guercino三件画作及1647年向Claude订画，均与作品对象分别成句；“Bentivoglio”“Duke of Parma”不据年代、家族或头衔猜定个人。Algardi谈判和梵蒂冈政策阻碍保留Haskell的时间、因果与评价限定；把未具名侄子、Pamfili court和Barberini court建为独立待对齐候选，暂不合并为Camillo Pamfili、具体宗族机构或正式关系。Claude画作的购买记录、Mazarin所有权及经代理人绘制等注释限定尚未迁入，当前只记录正文说法并标注脚注待核。

页图校读只写入本S2过程，不改S0：印本为“in the niches”，OCR粘连`theniches`；标题为`Carità Romana`（OCR `Caritd`并跨L154–155），`Death of Adonis`有空格（OCR `ofAdonis`），`of some six years earlier`被OCR误作`0's`；Claude句后的印刷脚注号为5，OCR录为6。页图另核实Romanelli的Romulus and Remus对应Plate 26b，图版清单称其为Bibliothèque Nationale（旧Palais Mazarin）画廊天顶细部；候选与既有Romulus-and-Remus知识元的同一性仍交S3处理。

首次表审计发现本段62条提及的字符偏移共同漏计段首L150 `[Page 182]`，而审计器按规范段L150–158全文计算。以页码行和换行合计11个字符修正所有偏移，并逐条确认`segment_text[start:end] == surface_form`；修正后结构审计0 errors。全书当前803段：262段reviewed/complete、6段reviewed/partial、45段有理由排除、490段queued；候选6,785条、提及11,062条、原书断言5,476条。`python scripts/audit_tables.py --summary`为0 errors；两条既存enrichment `source_ref`警告、490段queued及6段reviewed但迁移未完整仍在；`python -m pytest tests/test_audit_tables.py -q`为11 passed；`git diff --check`通过（仅提示仓库现有行尾转换）。下一规范段为`chp-7:07_CHP-7_sec_i:l160-169`（印刷页183），闭合p.182 L158引语；复合段L293–389仍待迁移p.170–182脚注及p.172 L301正文续句。

## 第七章印刷页183正文（2026-09-30）

规范段`chp-7:07_CHP-7_sec_i:l160-168`已迁移L161–168，新增14个候选、62条提及、20条正文/注释断言；另增p.183续引statement `st-chp7-p183-q01`，与p.182 `st-chp7-p182-i24`分段锚定并互链，p.182引语标记closed。候选包含未具名Pope、Bentivoglio palace、SS. Vincenzo ed Anastasio立面、First Fronde、无题讽刺短文及身份不明的Jesuit seminary；未将身份推断提前到S2。

L162记录Mazarin在法政治局与罗马、Bentivoglio宫殿、计划接待法国来客及Reni为Scipione Borghese创作《Aurora》；L163–164记录通过Maccarani委托Martino Longhi the Younger设计教堂立面、工程延误及致Maccarani引语；L165–166记录First Fronde对Mazarin意大利艺术家用人安排的冲击及Torelli、Stefano della Bella、Grimaldi经历。L167末句续至p.184 L171，故本段保留partial。L168是p.183注2日期部分；注2转让链在复合段L349，注1、3–6在L348、L350–353待按源序迁移。

扫描核对PDF物理第17页：L165 OCR`need only.be said`按印本应为`need only be said`，校读只记录于S2、不改S0。表审计修复跨页引语锚点后为0 errors；全书262 complete、7 partial、45 excluded、489 queued；候选6,799、提及11,124、断言5,497。`tests/test_audit_tables.py`为11 passed；两条既有enrichment `source_ref`警告仍在。

## 第七章印刷页184正文 L171–176迁移（2026-09-30）

逐行阅读规范段`chp-7:07_CHP-7_sec_i:l170-176`，核对`CHP-7.pdf`物理第18页；未把整章OCR副本计作另一来源。新增25个body-mention候选（cand-6809–cand-6833）、77条精确提及、18条原书断言。p.183 L167末句的`alternating with vital new purchases`作为p.184独立续句保存，并回填p.183原statement的continuation状态。p.184 L176末句以“a few years”止于行尾；只查读p.185 L206首词“earlier.”来确认本句闭合，p.185正文其余句子不提前迁移。

逐句记录：
- Charles I的对手仍匿名；其处决后Parliament出售picture gallery并使珍贵绘画进入国际市场。复用Charles I索引子项cand-0654表示sale语境，另将Parliament机构与gallery/collection对象拆开；未补出售卖机构的具体构成。
- Mazarin委托Everard Jabach购买前竞争者（由上文指向Duke of Mantua，cand-6720）收藏中的绘画（cand-6721）。候选身份不在S2中进一步对齐。
- 1653恢复权力、绝大多数绘画幸存、inventory、约500幅作品、Old Masters、意大利旧识画家、Reni/Guercino的相对代表数量、Sacchi与Cortona、对意大利绘画发展/地域的取舍、Rosa《Landscape with Apollo》、赠画对品味判断的限制、直接委托中的世俗/情色题材，以及敌方指控与Haskell评价均分别登记；“some”“vast majority”“nearly always”及敌方/作者发言层级保留。
- inventory候选cand-6814不定年：正文说1653恢复权力后“at once”编制；页图note 3引用1661 inventory，但该脚注在复合段L356，尚未按当前源序迁移。保留日期疑点，不合并为已裁决事实。
- 对比段分开记录La Vrillière gallery、宫殿、公寓、画作群、雇用画家群、未具名四幅偏爱画作、三幅Correggio与Titian Venus。`The Rape of Helen`建work候选cand-6826，不复用Guido Reni索引子项cand-2131；Rosa索引子项cand-2246亦与新建work候选cand-6832分开。Marie de Medici此前购画的说法保留为原书陈述，确切间隔未知。

页图校读不改S0：L171、172、173的`ofhis`为`of his`；L172 `whomhehadbecomefamiliar`为`whom he had become familiar`、`always-easy`为`always easy`、`subject-matfer`为`subject-matter`；L174 `in bis palace`印作`In his palace`、`La'Vrillière`印作`La Vrillière`。当前OCR原形仍保留在提及偏移与original_quote中，校读另记。页图显示p.184脚注1–4；复合源段L354–357待前序脚注处理后迁入，其中note 3日期说明和note 4 Guercino相关引证均尚未成statement。

覆盖账本：p.184标记reviewed/partial（L171–176）；p.183仍partial，因为注释未全迁。全书为262 complete、8 partial、45 excluded、488 queued；6,824 candidates、11,201 mentions、5,515 statements。`python scripts/audit_tables.py --summary`：0 errors；两条既存enrichment `source_ref` warnings、488 queued及8 partial均保留。恢复快照：`%TEMP%\PNP-Final-DATA-s2-p184-before-20260930.zip`。下一规范段为`chp-7:07_CHP-7_sec_i:l178-179`（图版25说明），不得跳过后续l181-182、l184-200、l202-203图版段直达p.185。

## 第七章图版25–28说明迁移（2026-09-30）

按规范源段处理l178–179、l181–182、l184–200、l202–203，分别核对CHP-7.pdf物理第19–22页及已处理的书前图版目录00_05_List_of_Plates.md L78–81。四段新增20条提及、14条原书断言；复用图版目录已有工作、作者、人物、机构、地点候选，未新建候选，也未将图版所在页组标题推断成赞助、所有权或现藏事实。四个规范段由reviewed/queued更新为reviewed/complete。segments.jsonl中release_excluded只限制发布范围，不影响本次S2语义处理。

- Plate 25：页图确认Gentileschi: Public Felicity triumphant over Dangers，图版目录明确作者全名Orazio Gentileschi；以既有作品与人物候选记录页图提及和署名。Louvre只出现于图版目录，不把它补写成此页图说明中的文字。
- Plate 26：a图复用Nanteuil作品候选，页图简称The Cardinal，按图版目录回指Cardinal Mazarin；b图为Romanelli的Romulus and Remus顶画局部，S0将作者OCR作R，页图及图版目录确认Romanelli。位置分别记录gallery与Palais Mazarin，后者不与p.26a肖像中的his gallery混同；gallery候选cand-6781与p.181–182所述新建上层画廊在语境上相合，最终身份映射留S3。
- Plate 27：PDF物理第21页的扫描版面旋转，S0转写将行内字符与行序反向，故保留S0不改；mention偏移精确锚定反向原串，statement限定记录页图读法。页图为a. Francesco Fanelli: Charles I与b. Bernini: Louis XIV，复用相应作品、作者和肖像人物候选。页组标题只作版面上下文，不推断人物国籍或关系。
- Plate 28a：页图确认Guido Cagnacci的Death of Cleopatra；作品、作者和题名人物复用已有候选。PDF物理第22页另印28b说明，但分节转写仅收录28a；28b已在书前图版目录L81逐项迁入，因此把页图出现而分节转写缺项的对应记在结果/过程，不重复新增S2源段或提及。

本次对图版25–28批量迁移前创建恢复快照%TEMP%\PNP-Final-DATA-s2-plates25-28-before-20260930.zip。dry-run验证20条mention切片与canonical S0完全相等、14条statement原文行及候选外键有效。首次覆盖写入因换行格式处理差异中止在账本更新前；只补齐4条coverage后复审。python scripts/audit_tables.py --summary为0 errors；全书266段complete、8段partial、45段excluded、484段queued；候选6,824、提及11,221、原书断言5,529。python -m pytest tests/test_audit_tables.py -q为11 passed。仍有两条既存enrichment source_ref警告，S2尚未收口。

当时下一规范段为chp-7:07_CHP-7_sec_i:l205-213（印刷页185正文）。p.183注释与p.184注1–4等仍位于复合段L293–389，应按规范来源序迁移；不能把正文后按序处理误写成脚注已完成。

## 第七章印刷页185正文L206–213（2026-09-30）

规范段`chp-7:07_CHP-7_sec_i:l205-213`按PDF物理第23页核读并迁入。新增28个候选（`cand-6834`–`cand-6861`）、94条提及和30条原书断言；所有提及切片、断言引句、候选外键和提及自然键在写入前通过干跑核对。跨页末句修订既有`st-chp7-p184-i17`的限定：p.184原始引句仍锚定原段，只记录句尾由p.185 L206 `earlier.`闭合，不推算间隔。

本页记录Mazarin对Guercino《Cato》题材作品的委托、1637年向Poussin订购Camillus作品及Haskell所述Livy故事；保留作品题名、作者归属与历史评价的来源层级。La Vrillière在1640年代增加的画作组按本页列出的Guercino、Pietro da Cortona和Alessandro Turchi作品分别记录，Maratta的Augustus题材画作作为较晚的系列完成项；“ten”沿用Haskell数量表述，不按单页列名重算。随后分别记录La Vrillière与Mazarin的文化趣味对照、新兴银行家/律师/商人赞助群体及Haskell所述“reticence and classicism”倾向；将该段视作作者的时代解释，不提升为普遍社会事实。1653年购藏及其或与晚年赞助减退有关的说法保留`Perhaps`推测；Romanelli奉Queen Mother之命、九年前被拒的Roman histories、Vigarani未能在Mazarin宫殿建成剧场，以及Fronde或有影响等，均按原文叙述层次记录。Brienne首访绘画的法文引文只录至p.185原段末，不提前补写p.186续文。

图像与OCR对读记录：页图为`La Vrillière`，OCR为`La Vrilliere`；`The Death of Cleopatra`无尾随撇号（S0 OCR多出撇号）；页图为`Charles I`、`Louis XIV`，S0分别误作`Charles 1`、`Louis XTV`。这些校读仅入过程和断言限定，S0源文保持不改。题名中仅给出的Cato、Camillus、Coriolanus、Sibyl、Caesar、Queen Mother及M. de Bordeaux等不预先扩展身份；Roman histories与p.181所述方案的可能对应保留为S3前候选，不建正式关系。

p.185注1–5分别位于复合段L358–360（注1–2 L358，注3–4 L359，注5 L360），尚未迁移；Brienne法文引文由p.185 L213续至p.186 L216–218。因此p.185覆盖标为`reviewed/partial`，不将正文迁移误报为页面及脚注收口。写入后`python scripts/audit_tables.py --summary`为0 errors；当前S2账本为266段reviewed/complete、9段reviewed/partial、45段excluded、483段queued，候选6,852、提及11,315、原书断言5,559。`python -m pytest tests/test_audit_tables.py -q`为11 passed。全量`--strict-stage --summary`报告492项未闭合，其中9段partial、483段queued；没有其他阶段错误，符合尚未达到S2收口门槛的状态。现有两条enrichment `source_ref`警告不由本批写入引起。下一规范源段为`chp-7:07_CHP-7_sec_i:l215-222`（印刷页186正文）；之后仍须按源序处理复合脚注，覆盖p.170–185注释及相关跨页正文续段。




## 第七章印刷页186正文 L216–222迁移（2026-09-30）

逐行处理规范段`chp-7:07_CHP-7_sec_i:l215-222`，并核对`CHP-7.pdf`物理第24页。p.185 L213起的Brienne法文回忆在本页L216–218续完；将原statement `st-chp7-p185-i30` 标记为由 `st-chp7-p186-q01` 续接且已闭合。新增25个候选（cand-6862–cand-6886）、83条精确提及和21条原书断言/关系候选。新候选的来源锚点逐条落到其首次提及的原书行号；候选来源、提及字符偏移、statement引文锚点均经过写入前核对。

L216–218记录Mazarin在Brienne叙述中的最后告别及其对离开收藏的遗憾；分别保留宫殿新公寓、小画廊、Scipio挂毯、Saint-André元帅、M. de Bordeaux来信、`Cortège`、Titian的Venus及Antoine Carrache的Deluge。引文嵌套关系、第一人称指代和转述身份按Brienne记载；Scipio、Saint-André、Carrache的身份以及几件作品的确切版本仍待S3，不在S2合并。Mazarin图书馆和仅称“Roi”的对象亦按原文粒度登记，不推断具体空间或身份。

L219–220记录Haskell关于Mazarin死后意大利艺术赞助、1644年召请Theatines赴巴黎、在塞纳河岸定居、遗嘱拨款重建St Anne-la-Royale并指定安葬其心脏、Theatines于1662年召Guarino Guarini、工程中断和约五十年后完成的叙述。将教堂与建筑方案、曲面立面、穹顶/拱顶分别记录；Borromini参照、与当时法国实践的比较、“巴黎孤立的意大利巴洛克实例”以及可能阻遏后续实验均保留为Haskell判断或推测，不转成外部核实事实。Mazarin的心脏因现有分类无合适类型而留空类型。L221–222记录Fouquet被捕、Colbert接替，以及两人曾受雇于Mazarin；句子在`had been employed by Mazarin,`后续至p.187 L225，因此相关statement和本段保持partial。

页图校读只记入S2、不修改S0：OCR的`Je sis un grand soupir`按页图读为`Je fis un grand soupir`；`SaintAndré`按印本断行读作`Saint- / André`；`S. Carlo aile Quattro Fontane`按页图为`S. Carlo alle Quattro Fontane`；`isolated-example`按印本为`isolated example`。原始S0字符串仍用于来源锚定，校读与其分开记录。

覆盖账本将p.186标为reviewed/partial：注1在复合段L361待迁移，且L222续句待p.187闭合；p.185仍因注1–5位于L358–360待迁移而partial，Brienne引文的续页缺口已闭合。写入后全书803段：266 complete、10 partial、45 excluded、482 queued；候选6,877、提及11,398、原书断言5,580。修正候选source_ref格式后，`python scripts/audit_tables.py --summary`为0 errors；仍有两条既存enrichment source_ref警告、482段queued及10段partial；`python -m pytest tests/test_audit_tables.py -q`为11 passed。下一规范源段为`chp-7:07_CHP-7_sec_i:l224-230`（p.187正文），随后按S0源序继续；全书S2未收口，不交S3。

## 第七章印刷页187正文 L225–230（2026-09-30）

规范段`chp-7:07_CHP-7_sec_i:l224-230`按PDF物理第25页核读并迁入。新增21个候选（`cand-6887`–`cand-6907`）、69条提及和29条原书断言/关系候选。提及字符偏移、候选来源锚点、断言原文范围、脚注指针和候选外键均经写入前预检；`st-chp7-p186-i19`与`-i20`分别链接至p.187关于Fouquet、Colbert收藏意大利艺术的续接断言。

本页L225闭合p.186 L222“had been employed by Mazarin,”之后的并列句；记录Fouquet与Colbert收藏意大利艺术、Louis XIV面向意大利招募艺术家及Baldassare Franceschini受托绘制Fame寓意画。L226记录Ciro Ferri为Louis XIV工作、Pier Francesco Mola受邀赴巴黎而在启程前去世、Salvator Rosa拒绝1665年邀请及其信中对法国访客求购作品的说法，并记录Haskell将Louvre方案界定为法国热情的高潮与危机。L227–228记录Louis XIV与Colbert考虑王宫东立面、Colbert对Le Vau的态度、转向意大利设计及提交图样的提议；均保留提议/邀请状态，不写为方案已实施。L229–230记录Haskell对民族主义、法国对意大利艺术敌意的解释及对Bernini、Pietro da Cortona、Carlo Rainaldi、Candiani方案的转述批评；保留说话层级、评价与限定，并记录Bernini先被拒、后获邀提交新方案及赴巴黎。L230末尾Bernini直接引语未完，续至p.188。

页图校读只记录于S2、不改写S0：`os`读为`of`；`eastern’front`读为`eastern front`；`Baroque1`为引号/OCR混淆；`Rainaldirs`读为`Rainaldi’s`；`Modem opinion`读为`Modern opinion`；`triumphantprogress`跨印刷断行，为`trium- / phant progress`。p.187注1–6分别位于复合段L362–367，尚未迁移，故p.187为reviewed/partial；p.186跨页句已闭合，但p.186注1在L361待迁移，故仍partial。写入后账本为266 complete、11 partial、45 excluded、481 queued；候选6,898、提及11,467、原书断言5,609。下一规范段为`chp-7:07_CHP-7_sec_i:l232-241`（印刷页188正文）。


## 第七章印刷页188正文 L233–241（2026-09-30）

规范段 chp-7:07_CHP-7_sec_i:l232-241 按PDF物理第26页核读并迁入。新增17个候选（cand-6908–cand-6924）、75条提及和34条原书断言/关系候选；提及精确切片、断言原文范围、候选外键和提及自然键均在写入前核对。

L233闭合p.187 L230的Bernini引语，保留其沿途所见主权诸侯宫殿及为法国国王提出更宏伟建筑的说法；同段记录Colbert的行政考量。L234分别记录Bernini对法国君主制与教皇更替方式的理解、Louis XIV希望保存前任作品的解释，以及Haskell对Bernini激起反对的因果判断。L235–236记录宫廷派系、国王仍支持、Bernini十月返罗马途中、计划不会实施的判断和Haskell对其巴黎停留的评价。

L237–238记录Bernini受托制作Louis XIV大理石胸像、从真人刻画世俗君主的机会、胸像的个人君主制意象及专制主义评价，以及骑马像订制、开工时间和1684年抵达巴黎的叙述。未从被动语态补造委托人；“four years”不换算为绝对年份。脚注1、2分别位于复合段L368、L369待迁移。

L239–240记录Haskell对Gallican原则、国教自主意图、雕像不合意、以Constantine雕像为蓝本、ultramontane claims、意大利式繁饰、Louis XIV想砸毁后将雕像安置于凡尔赛园地、Girardon改造及Marcus Curtius称谓的叙述；按原文限定和对象边界记录。页图确认Vatican跨行续接，S0原文不改。

L241记录Bernini失败被说成意大利艺术在法国声望崩塌的标志，以及法国自信增长时对意大利艺术批评和敌意增强的作者判断；末句“It is also true that, with the full support”由p.189 L244续完；前后断言statement互链。页图脚注1为Wittkower 1955页码引文，脚注2为ibid.页码引文；两注仍待复合段L368–369迁入。p.187注1–6在L362–367仍待迁移；p.187、p.188均保持partial。


## 第七章印刷页189正文 L244–257（2026-09-30）

规范段chp-7:07_CHP-7_sec_i:l243-257按PDF物理第27页核读并迁入。新增15个候选（cand-6925–cand-6939）、69条提及和28条原书断言/关系候选；跨行人名、提及字符切片、来源锚点、候选外键与statement引文写入前逐项核对。

L244闭合p.188 L241句，记录Louis XIV在Bernini支持下于1666年创立罗马法国学院；区分学院所宣称的训练法国艺术家研究意大利杰作并最终取代意大利艺术家的目标与已发生结果。L245记录意大利参与凡尔赛大型建筑/装饰工程的程度、仍持续赴意大利延聘艺术家的做法。L246记录Francesco Borzone受召至巴黎并受雇至1679年、Louis选择Domenico Guidi制作凡尔赛园林雕塑群、Le Brun供图、雕塑群的Fame与Time寓意、抵法后取代Bernini骑马像，以及Louis对其衣褶的法语评价。

同页记录Carlo Maratta受托绘制《Apollo and Daphne》、优厚报酬和peintre du roi称号；未从被动语态补造委托者。罗马法国学院未具名负责人后来询问Carlo Cignani是否愿赴巴黎，Cignani为Louis画过两幅未具名作品；行程未推进的理由记为Cignani素描能力被认为不足，评价者未明确。Haskell把这例解释为意大利绘画与严格法国趣味的差异，并称Louis对意大利艺术家的赞助远少于其期待、意大利画家常向巴黎求援。

L252–255记录Bellori 1672年著作题献Colbert、Malvasia 1678年《Felsina Pittrice》题献Louis XIV、博洛尼亚艺术家吸引法国注意的努力，以及Cignani、Benedetto Gennari、Luigi Quaini、Donato Creti对Louis XIV的仰慕。怀疑这些仰慕并非完全无私属于Haskell的推测。页图确认p.189 L255脚注印本为5，S0该处OCR误作6；复合段L373 OCR编号6与印本版面不一致，脚注仍待迁移。

L255–257记录Mattia Preti拟赠Louis XIV的寓意肖像、法西敌对行动爆发时Preti在Malta的处境使赠礼显得不审慎，以及其后将画卖往他处；冲突未具体指认或定年。末句称Spain仍欢迎意大利画家及其作品，句意完整。页图校正L244 OCR os为印本of、L249 OCR大写Considered为印本小写considered，S0文本保持不改。p.189脚注1–6分别位于复合段L370–374待迁移，故coverage为reviewed/partial。


## 第七章印刷页190正文 L260–266（2026-09-30）

规范段chp-7:07_CHP-7_sec_i:l259-266按PDF物理第28页核读并迁入。新增15个候选（cand-6940–cand-6954）、97条提及和28条原书断言/关系候选。候选、来源锚点、提及切片、指代及statement引文写入前逐项核对。

L260记录尼泊尔艺术家受那不勒斯总督雇用、总督为马德里宫廷或收藏家办事，以及Velasquez 1649年第二次赴意大利、为Alcazar购画/雕塑并在威尼斯重点看画。保留招募一位能恢复西班牙湿壁画实践的画家的需求与Velasquez在此事上的不成功。

L261记录请Pietro da Cortona赴马德里未果（其在罗马受奥拉托利会雇用）、Velasquez在摩德纳向Angelo Michele Colonna和Agostino Mitelli作未成功的初次接洽、带回旧大师作品却未找到合适壁画家，以及Finelli、Algardi和其他雕塑家为西班牙王室收藏制作古代摹本和原创作品。另记录Colonna与Mitelli最终于1658年抵达马德里并受雇；这与前述初次失败分开表达。

L262–264依原文登记Don Gasparo de Haro y Guzman在意大利被称为Marchese del Carpio、1677年任驻罗马大使时48岁、年轻时因涉嫌牵连刺杀一位未具名国王的企图而入狱两年、对绘画的热爱，以及其至1651年拥有Velasquez《Toilet of Venus》（又称Rokeby Venus）。保留Haskell关于该画是西班牙艺术杰作及其意大利性的评价，也保留“must have welcomed”的推断语气；不推断未具名国王的身份。

L265–266记录Del Carpio三个月内参观Carlo de Rossi的画廊、停留一小时半以上，De Rossi是Salvator Rosa的朋友；Cardinal Camillo Massimi负债去世后其继承人被迫处置财产，Del Carpio大规模购入两幅Velasquez肖像及大量计划雕版的古物。本页末句仅录至“Indeed he clearly”，statement链接到p.191 L269续句。页图核正L263年龄48后的印本脚注号为2（OCR作问号）、L263的Hs校为印本His，L264 have welcomed被OCR连写为havewelcomed、L266 compelled前连字符为OCR残留；S0不改。脚注1、2、3、4、5分别在复合段L375、L376、L377、L377、L378待迁移，所以coverage为reviewed/partial。


## 第七章印刷页191正文 L269–278（2026-09-30）

规范段chp-7:07_CHP-7_sec_i:l268-280按PDF物理第29页核读并迁入：新增22个候选、86条提及、32条原书断言/关系候选。p.190 L266的句首由本页L269续完，statement互链；本页末句L278仅到‘local artists’，续文位于p.192 L283。

L269记录Del Carpio对Massimi古典趣味的亲近感、其三十卷素描集及最喜爱的Carlo Maratta；L270–272记录其对Bernini的欣赏、拥有四河喷泉小型版本、从Domenico Bernini取得Bernini自画像素描，以及在那不勒斯传言愿以30,000 scudi购入Louis XIV骑马像但报价未获接受。Piazza Navona是原喷泉所在处，不据此把小型版本定位于广场。

L273记录其每周多次拜访Niccolo Berrettoni、Giuseppe Ghezzi和Giovanni Francesco Grimaldi的画室；记录Berrettoni师从Maratta、Ghezzi后来任圣路加学院常务秘书、Grimaldi为风景画家，以及他发现Paolo de Matteis在圣彼得大殿临摹祭坛画后推动其事业。保留原书对那不勒斯画家失去保护者的引语和Haskell关于无本土意大利人表现同等热忱的概括。L274–278记录Del Carpio的那不勒斯赞助、画藏数量由1100增至1800、Pinacci负责画藏且是专家修复师、宫殿陈设、Luca Giordano取代Maratta成为首席画家并装饰教堂和宫殿、1687年去世、画作与古代雕像运往马德里后裔收藏，以及城市变化和关于其文化贡献的未完评述。群体、收藏与建筑保持原文限定，不据此合并身份。

页图校读：确认Niccolo应为Niccolò；L274的‘1800/’为数字1800后的脚注7而非斜线；L277–278 OCR的‘picturesand’印本为‘pictures and’。脚注5和9分别在当前分节L279、L280并已连同引文回链；注1、2、3、4、6、7、8、10、11位于复合段L379–387待迁移。L383末尾OCR残留符号及L384西班牙语书名OCR错字已按页图记录，S0不改。

## 第七章印刷页192正文L283–291（2026-09-30）

规范段chp-7:07_CHP-7_sec_i:l282-291按PDF物理第30页核读并迁入：新增17个候选、51条提及、28条断言/关系候选。L283闭合p.191 L278未完句并与st-chp7-p191-i32互链；记录Monterey任内治理危机与Del Carpio改革的原书评价、其在罗马招募画家赴马德里的尝试、Luca Giordano 1692年赴西班牙及其近十年活动、风格描述和对后世艺术家的影响。King身份、未具名画作、建筑、画藏和群体保持原文边界。页图核对：Niccolo应为Niccolò，It-was应为It was，thé应为the，countryduring应为country during，hve应为live；这些校读记于S2，不改S0。注1、2分别位于复合段L388、L389待迁移，故coverage为reviewed/partial。


## 第七章印刷页192第IV节引言 L3–4（2026-09-30）

规范段`chp-7:07_CHP-7_sec_iv:l3-4`完成S2阅读与迁移。新增3个候选（cand-6994–cand-6996）、6条提及和1条原书总结性断言。复用Spain地理候选cand-5120、France地点候选cand-5317及England地理候选cand-6809；另建Holy Roman Empire政治实体候选，以及意大利艺术家、伟大赞助人两个未具名群体候选。原句把西班牙/法国影响与十七世纪后期赞助重心转移连成一项Haskell的总结性判断；保留“increasingly”“then”表达的趋势和次序，不推定具体继承者或赞助人。此段无脚注，无需OCR校读。下一段为`chp-7:07_CHP-7_sec_i:l293-389`（第七章p.170–192复合注释与正文续句）。


## 执行顺序校正（2026-09-30）

复核`04-knowledge/tables/s2-coverage.csv`的规范段顺序后发现，`chp-7:07_CHP-7_sec_i:l293-389`仍queued，且位于第IV节之后续段之前；它包含p.170–192复合脚注及p.172 L301正文续句。此前将已迁入的第IV节引言列为下一段时漏过此较早源段。已完成的`chp-7:07_CHP-7_sec_iv:l3-4`保留为已审阅，不撤销；接续先处理复合段，再按账本顺序继续第七章后文。



## 第七章p.170–171脚注 L294–300（2026-09-30）

按源段`chp-7:07_CHP-7_sec_i:l293-389`先迁移L294–300。p.170注1引用Vaes 1931 p.202，回链Van Mander在Amsterdam写作的statement；p.171注1–5分别引用Colapietra、Capecelatro、Bouchard—Marcheix、J. Walker和Passeri，按脚注位置回链到旧金山伯爵／Monterey及Domenichino相关断言。注6的`ibid.`沿用注5的Passeri出版物，另引用Trapier；原注还称一组为西班牙国王绘制的古罗马场景现藏Prado（Nos.234–236），其中仅一部分归Lanfranco。新增9个候选、15条提及和11条statement；新建不具名作品组、未具名西班牙国王和Prado机构候选，身份不由上下文猜定。

对照CHP-7.pdf物理第5页（印刷页171）脚注图像：印本为`Passeri`，PDF内嵌文字层误读`Passed`；S0的`o£`按图像校为`of`。校勘只记录于S2，S0不改。L301正文续句与p.172注1–4（L302–305）尚未迁移；覆盖行当前为`reviewed/partial`，源行范围`L294-300`。


## 第七章p.172正文续句与脚注L301–305（2026-09-30）

按规范复合段`chp-7:07_CHP-7_sec_i:l293-389`迁移p.172开篇正文续句L301及脚注L302–305，并对照`CHP-7.pdf`物理第6页。L301从“Cathedral”接续p.171 L29 Finelli句尾“in the”，明确其从罗马来此工作的目的地为那不勒斯主教座堂；新增statement `st-chp7-p172-cont-i01`、`i02`闭合旧statement `st-chp7-p171-i24`，确认Viceroy为上下文中的Monterey。原句中该段仅止于“there might well be worse to come”；p.172后续Philip IV与风景画讨论由规范段L31–35完整覆盖，复合段中不重复迁移。

新增13个候选（cand-7006–cand-7018）、46条提及和22条statement，其中17条为正文断言/关系候选，5条为脚注引文定位。登记Monterey委托的两幅未具名等身肖像及未具名妻子；保持Naples Cathedral及其未具名管理者、Finelli扩大装饰份额、Cosimo Fanzago反对之间的语境。另记录Monterey对罗马旧识及那不勒斯画派的赞助、Ribera为未识别的Augustinian church绘制的一组祭坛画，以及新巴洛克构图/较轻色调可能迎合Monterey对Roman与Venetian绘画的欣赏。Augustinian church以cand-7009单列，不并入cand-6643（Salamanca教堂）；“possible”保留为Haskell的推测。Monterey于1637年携四十船掠获物离开、Neapolitans的复杂感受、为三十年战争中的西班牙事业从其省份征取人力财物、Haskell对其奢靡与艺术刺激作用的评价，以及“后面可能更糟”的推测分别记录；未推断路线、目的地、物品清单、具体军事行动或继任者。

L302–305分别为Passeri p.251、Trapier p.72、Costello p.247、Röthlisberger 1961 vol.I pp.155–160及Blunt 1959 pp.389–390。前两项复用相应的来源候选并依书目补足Trapier出版物；Costello文章据书目登记为候选，另建Jane Costello人物候选，并保留与cand-3509的跨章身份比较至S3。Röthlisberger出版物复用cand-4577，人物候选沿用已处理p.173中出现的cand-3502；Blunt文章与作者分别连接到新archive候选及索引人物cand-0379。所有citation statement仅表示Haskell脚注中的书目定位，不称被引文献内容已独立阅读或核实。页图确认L305印本为卷号罗马数字`I`和页码`155–60`；S0 OCR中的`1`、`15 5-60`及Blunt页码内空格均保留，校读只记S2。

将p.170–172现有脚注ref状态和引文回链更新为`linked`；p.172正文L31–35的注3、注4也分别连到L304、L305。覆盖账本中p.171 L21–29由partial转为complete，复合段更新为`reviewed/partial`、`L294-305`；p.172正文L31–35保持complete。当前803段为268 complete、16 partial、45 excluded、474 queued；候选7,009、提及11,912、statement 5,793。`python scripts/audit_tables.py --summary`为0 errors，仍有两条既存enrichment source_ref警告及未处理段落警告；`python -m pytest tests/test_audit_tables.py -q`为11 passed。下一子范围为复合段L306–308（p.173注1–3）。


## 第七章p.173脚注L306–308（2026-09-30）

p.173脚注1–3按源序迁入复合段`chp-7:07_CHP-7_sec_i:l293-389`，并对照`CHP-7.pdf`物理第7页。注1为Barozzi e Berchet卷I第242页，复用已有出版物候选`cand-4365`；依据书目全名分别新增Niccolò Barozzi、Guglielmo Berchet人物候选。注2为René Crozet《La vie artistique en France au XVII siècle, 1598–1661: les artistes et la société》第49页；注3列Louis Batiffol《La vie intime d’une reine de France au XVIIème siècle》及V. L. Tapié《La France de Louis XIII et de Richelieu》第67页。书目仅用于识别书目项和作者；脚注只作为定位，不代表已阅读或核实所引作品内容。注3未把第67页错误赋给Batiffol。

新增8个候选、9条提及和4条脚注定位statement；3条正文脚注标记现均回链到L306、L307、L308，并记录相应正文锚点。p.173正文段保持complete；复合注释段仍为reviewed/partial，覆盖范围扩至L294–308。当前803段为268 complete、16 partial、45 excluded、474 queued；候选7,017、提及11,921、原书断言/定位statement 5,797。`python scripts/audit_tables.py --summary`及相关审计测试随后执行。下一子范围为L309–311（p.174注1–4）。


## 第七章p.174脚注L309–311（2026-09-30）

p.174脚注1–4按源序迁入复合段`chp-7:07_CHP-7_sec_i:l293-389`，并对照`CHP-7.pdf`物理第8页。注1分别定位Baldinucci、Desjardins第49页和Dhanens；注2定位Desjardins第50页；注3定位Batiffol第430页；注4定位C. Sterling《Gentileschi in France》第112–120页。书目用于识别书目项，不表示已读所引文献。Baldinucci注的“IV, 1688”与书目所列Notizie第VI卷（1728）未精确吻合，保留为待来源核对项。

注2还记录正文的实质信息：已登记的Henri IV骑马像于1792年毁损；Catherine de’ Medici于1559年委托Michelangelo制作Henri II骑马像，但该项目未执行；另立Pietro Tacca为Philip III of Spain制作的未具名骑马纪念像，并以“similar”保持与前两像仅类比关系。S0将Henri II OCR为“Henri ll”，页图校读为“Henri II”，不改S0。Michelangelo沿用cand-1660作本处锚点，cand-1661同名索引项留待S3核对。

本段新增12个候选、21条提及和12条statement（6条脚注定位、6条脚注事实/关系候选）；p.174正文注1–4均已双向回链。复合段仍为reviewed/partial，覆盖范围扩至L294–311。当前803段为268 complete、16 partial、45 excluded、474 queued；候选7,029、提及11,942、statement 5,809。结构审计 errors为0，既有两条enrichment `source_ref`警告和S2未收口警告保持；`tests/test_audit_tables.py`为11 passed。下一子范围为L312–313（p.175注1–2）。


## 第七章p.175脚注L312–313（2026-09-30）

p.175脚注1–2按源序迁入复合段`chp-7:07_CHP-7_sec_i:l293-389`，并对照`CHP-7.pdf`物理第9页。注1引Baudson《Apollon et les Neuf Muses du Palais du Luxembourg》第28–33页及1956年《II Seicento Europeo》第64页；注2引Edmond Bonnaffé《Dictionnaire des amateurs français au XVII siècle》第269页。书目用于识别出处；被引文本未在本次工作中独立阅读。图像与书目核实注2应为Bonnaffé，S0 OCR省略重音；S0保持原样。

新增5个候选、5条提及和3条脚注定位statement；p.175正文L64、L67的脚注1–2均回链并更新限定。p.175段仍保持complete；跨页未完句续至p.176 L77。复合段仍为reviewed/partial，覆盖范围扩至L294–313。当前803段为268 complete、16 partial、45 excluded、474 queued；候选7,034、提及11,947、statement 5,812。下一子范围为L314–318（p.176注1–9）。


## 第七章p.176脚注L314–318（2026-09-30）

p.176脚注1–9按源序迁入复合段`chp-7:07_CHP-7_sec_i:l293-389`，并对照`CHP-7.pdf`物理第10页。共登记10条书目定位：Mazarin 1961（书目识别为Bibliothèque Nationale展览目录）；Poussin《Correspondance》同版pp.15、31 note 2、36–37及188；Briganti 1962 p.142；Malvasia《Felsina Pittrice》vol.II p.264；Blunt 1954 p.89（书目未找到精确条目，出版物身份保留未决）；Wittkower 1955 p.202；Passeri p.115。能由书目辨认的条目只用于定位，不表示所引内容已另行阅读。复用cand-4634、cand-4473、cand-6933、cand-4383、cand-4376并据书目补明版次；Blunt 1954另保留开放来源候选。

页图校读将S0 L315的“Brigand”辨为“Briganti”，将L318页码“p.11$”辨为“p.115”；只记校勘，不改S0。新增4个候选、16条提及和10条脚注定位statement；p.176正文15处脚注引用全部回链，L89末句已由p.177 L92闭合。p.176正文段保持complete，复合段仍为reviewed/partial，覆盖范围扩至L294–318。当前803段为268 complete、16 partial、45 excluded、474 queued；候选7,038、提及11,963、statement 5,822。下一子范围为L319–323（p.177注1–5）。


## 第七章p.177脚注L319–323（2026-09-30）

按源序迁移p.177脚注1–5，核对CHP-7.pdf物理第11页。注1复用Baldinucci 1948出版物cand-4548；书目明确为Sergio Samek Ludovici编《Vita del Cavaliere Gio. Lorenzo Bernini》（Milan, 1948）。注2分别登记L. Stone《The market for Italian art》（Past and Present, 1959）及L. R. Betcherman《Balthazar Gerbier in seventeenth century Italy》（History Today, 1961），作者仅保留书目首字母；注3登记Alessandro Luzio《La galleria dei Gonzaga venduta all’Inghilterra nel 1627–38》（Milan, 1913）；注5登记G. H. J. Albion《Charles I and the Court of Rome》（Louvain, 1935）。这些引文只表示Haskell的书目定位，不表示所引内容已独立阅读。

注4分开处理Lumbroso p.369与A. Venturi p.252。复用cand-5683、cand-5626，并据书目确认《Notizie sulla vita di Cassiano dal Pozzo》（Torino, 1874）；保留其与既有p.137引用候选的分立，待S3核对。复用cand-4354并据书目确认Venturi《La R. Galleria Estense in Modena》（Modena, 1883）；新建作者候选A. Venturi，不与Professor Franco Venturi合并。注4报告1645年Gabriele Balestrieri致Modena公爵书信，并经Venturi引录意大利语句；新建书信archive候选，复用索引候选cand-0170及cand-1675。书信作者、收件人和引文内容分别记为原书关系/内容候选，不登记正式边，也不声称已查阅原件。

本段新增9个候选、17条提及和10条statement（7条脚注定位、3条书信作者/收件人/引文内容候选）。p.177正文标记1–5均回链至对应脚注；p.177 L100是注4意大利引文尾段，现与L322合读并记录在同一脚注statement中，p.177 L91–100覆盖转为complete。当前803段为269 complete、15 partial、45 excluded、474 queued；候选7,047、提及11,980、statement 5,832。复合段仍为reviewed/partial，覆盖扩至L294–323。下一子范围为L324–329（p.178注1–6）。

`python scripts/audit_tables.py --summary`：0 errors；两条既存enrichment `source_ref`警告及15段reviewed但未完全迁移、474段queued仍在。`python -m pytest tests/test_audit_tables.py -q`：11 passed。17条本次新增mention偏移逐条与源段文本核对，p.177脚注1–5的正文回链、L100/L322拆分引文及覆盖状态均通过定向检查。该机械核验不等于独立语义验收。

## 第七章p.178脚注L324–329（2026-09-30）

按源序迁移p.178脚注1–6，对照CHP-7.pdf物理第12页。注1复用Malvasia《Felsina Pittrice》cand-6933（书目对应Bologna 1841两卷版，保留原作1678年信息），另登记Denis Mahon 1949年关于Guercino《Semiramis》的论文；Haskell报告Mahon认为画作与Charles I邀请之间没有关联。该意见作为被引作者判断单独记录，并回修p.177 statement及p.178拒绝故事限定，不把任何一方提升为项目结论。注2登记Walpole《Anecdotes of Painting in England》卷II p.51；脚注所引1762与书目列出的1726不一致，版本日期保持未决。Haskell对该故事“不可靠但大体可信”的评价另记为作者评语。注3 Baldinucci卷V（1702）p.361未在书目中精确找到对应卷本，保留未决，不并入卷VI（1728）。

注4分别登记Crinò 1954年《Rivista d’Arte》论文和J. Hess 1952年关于Queen’s House绘画的论文，复用相应正文人物候选。注5为实质信息：Haskell称Artemisia Gentileschi是Orazio之女，并于约1638年来英一两年；亲缘与赴英断言分别记录，时间和时长保留近似限定。注6登记Pope-Hennessy 1953年Fanelli论文及Whinney、Millar《English Art, 1625–1714》（1957）；作者首字母按书目保留。被引文献均只作书目定位，未在本次S2迁移中独立阅读。

新增12个候选（cand-7057–cand-7068）、20条提及和12条statement（8条脚注定位、2条被引/作者评议、2条关于Artemisia的原书断言/关系候选）。p.178正文标记1–6均回链至L324–329。页图确认L328、L329印本脚注号分别为5、6，S0 OCR误作6、8；S0不改。并据注1保留Mahon对Semiramis邀请因果联系的不同解释，据注2保留Haskell对Walpole证据可信度的判断。复合段覆盖扩至L294–329，下一子范围L330–334（p.179注2–6）。

当前803段为269 complete、15 partial、45 excluded、474 queued；候选7,059、提及12,000、statement 5,844。
迁移后验证：scripts/audit_tables.py --summary 为0 errors；警告保留两条既存 enrichment source_ref（enr-06678、enr-06937），以及 S2 未收口的474段queued、15段reviewed/partial。tests/test_audit_tables.py：11 passed。p.178定向检查通过：20条新增提及锚点匹配S0，12条statement外键有效，6个正文脚注标记回链至L324–329，覆盖范围L294–329。
## 第七章p.179脚注L330–334（2026-09-30）

按源序迁移p.179脚注2–6，并对照CHP-7.pdf物理第13页。此前页内注1位于正文规范段L126，本次补齐对应的footnote_citation statement及正文反向statement链接；该注与注2均引用Wittkower 1955年《The Sculptures of Gian Lorenzo Bernini》p.201，注2的ibid.按注1解析。注3的Hervey p.391由书目对应到M. F. S. Hervey 1921年Thomas Howard传记，并复用此前p.386引用候选；注4 Passeri p.191复用Jacob Hess 1934年版候选，注5 Albion p.395复用《Charles I and the Court of Rome》，注6 Guido Reni p.109登记为1954年展览目录。各项仅作书目定位，未独立阅读引文来源；作者身份保留首字母，交S3再对齐。

将p.179正文标记1–6全部回链至L126及L330–334，新增1个目录候选、5条提及和6条citation statement。Wittkower、Hervey、Passeri、Albion、Guido Reni的作品/作者提及分别连接既有候选；Hervey 1921年题名补明，未与索引中的Sir Robert或Lord Hervey合并。p.179正文规范段L113–126由reviewed/partial转complete；复合段覆盖扩至L294–334。下一子范围L335–338（p.180注1–4）。
迁移后验证：scripts/audit_tables.py --summary为0 errors；保留两条既存enrichment source_ref警告及S2未收口状态（474段queued、14段reviewed/partial）。tests/test_audit_tables.py：11 passed。定向核验通过：5个非重叠提及锚点与S0匹配，6条citation statement定位有效，11个正文脚注引用全部回链；覆盖计数与账本一致。


## 第七章印刷页180脚注 L335–338（2026-09-30）

复合源段`chp-7:07_CHP-7_sec_i:l293-389`按书序迁入L335–338，并核对`CHP-7.pdf`物理第14页（印刷页180）。页图读作：1 Prunières, 1913, p.41；2 Brienne, vol.I, p.315；3 Haskell认为Mazarin不太可能在1632年前委托任何重要作品，并称Mahon曾把Mazarin购买“两件Poussin作品”的日期建议为1632；4 两件作品列于Louvre与Institute of Arts, Detroit，并引《Nicolas Poussin》目录页46、65。S0保留L335 `Prunidres`、L337 `i960`等OCR；校勘仅记本过程。

逐条回链：注1作为Prunières 1913 p.41书目定位，连至`st-chp7-p180-i22`（Baroni）；物理书目页434确认条目为H. Prunières, *L’opéra italien en France avant Lulli* (Paris, 1913)，复用`cand-4861`并补全书目身份，作者复用`cand-5597`。注2作为Brienne《Mémoires》卷I p.315定位，连至`st-chp7-p180-i27`（Bentivoglio“apparently lent”）；物理书目页417确认Paul Bonnefon编三卷本、Paris 1916–19，新增archive候选`cand-7071`，作者连接索引候选`cand-0452`。这些引文只作Haskell的来源定位，不代表独立阅读被引著作。

注3新增Mahon文章archive候选`cand-7070`；物理书目页428确认“‘Mazarin and Poussin’ in Burlington Magazine, 1960, pp.352–354”。独立记录Haskell对1632年前重要委托的“most unlikely”评估，以及Haskell转述Mahon把1632建议为Mazarin购买“两件Poussins”的日期。购买日期不等同委托日期；“two Poussins”与L138两件具名作品的关联保留为语境推断，不把建议日期改成确定事实。正文标记3回链`st-chp7-p180-i30`与`i34`。

注4复用作品候选`cand-6773`、`cand-6774`及Louvre机构候选`cand-4589`，复用目录archive候选`cand-4633`并据书目物理页434补全Blunt展览目录身份；新增`Institute of Arts, Detroit`机构候选`cand-7072`。页图只给两件作品与两处馆藏的成组陈述，并引用目录pp.46、65，未明确逐件配对；以`st-chp7-p180-n4-pair-location`保存端点集合及未决映射，留S6审查，未写正式关系。正文标记4回链`st-chp7-p180-i34`。

本段新增3个候选、10条提及和7条statement；修订2个既有bibliographic候选。p.180正文段由reviewed/partial改为reviewed/complete；复合段覆盖扩为L294–338并仍为reviewed/partial。当前803段为271 complete、13 partial、45 excluded、474 queued；候选7,063、提及12,015、statement 5,857。下一子范围L339–342（p.181注1–4）。


## 第七章印刷页181脚注L339–342（2026-09-30）

按书序迁移p.181脚注1–4，核对`CHP-7.pdf`物理第15页。注1拆分Brienne经Haskell转述的“Mazarin不拥有一件Poussin”与Haskell“几乎可以肯定指后期作品”的解释；前者不记为独立核实的所有权事实，后者保留作者概率判断。分别连接Brienne《Mémoires》卷I p.302、人物Brienne、Mazarin与Poussin候选，并回链p.181正文i05/i06。注2定位Brienne卷I pp.293–294，连接嵌套法文引语i11；所引原书页未另行阅读。注3 `Mazarin, p. xxxiii`匹配书目已登记的1961年展览目录，作为Romanelli上层画廊与历史题材叙述i26/i27的书目定位，不声称目录已查阅。

注4登记Haskell脚注所述1646-07-06 Romanelli致Francesco Barberini书信候选`cand-7073`；作者和收件人分别复用`cand-2208`、`cand-0203`。Pollak, 1913, p.52只作为转引定位。按书目页433将既有Pollak来源候选`cand-4359`补明为“意大利艺术家巴洛克时期书信”论文（原题 *Italienische Künstlerbriefe aus der Barockzeit*），但没有独立检查论文或信件。注4与正文i28回链。原书脚注将信件归于Romanelli并注明收信人与日期；这些是S2来源断言，仍非S6正式关系。

本段新增1个档案候选、12条提及和8条statement，并细化既有Pollak书目候选。p.181正文段由reviewed/partial转为reviewed/complete；复合段覆盖扩至L294–342并仍为partial，下一子范围为L343–347（p.182注1–5）。当前803段为272 complete、12 partial、45 excluded、474 queued；候选7,064、提及12,027、statement 5,865。

迁移后核验：`python scripts/audit_tables.py --summary`为0 errors；保留两条既存enrichment `source_ref`警告、474段queued和12段reviewed/partial状态。`python -m pytest tests/test_audit_tables.py -q`为11 passed。12条提及偏移以复合段L293–389为基准，逐条与S0切片核对；候选外键、8条statement及正文脚注互链有效。书目对应与机械检查不等于独立阅读被引材料或整体语义验收。


## 第七章印刷页182脚注L343–347（2026-09-30）

按书序迁移p.182脚注1–5并核对PDF物理第16页。注1的Prunières, 1913, p.68与Bjurström 1961条目分别由书目确认；后者为Per Bjurström, *Giacomo Torelli and Baroque Stage Design* (Stockholm, 1961)。注2书目对应André Félibien《Entretiens…》Trévoux 1725六卷本卷III p.530；注3 Malvasia卷II p.264与注4 `ibid., II, p.327`回指同一《Felsina Pittrice》；以上仅作Haskell的引文定位，未独立阅读引文页。

页图同时校读L343–344的Prunières、Bjurström、Félibien变音符；S0保留原OCR。注5页图印作脚注号5、Röthlisberger, 1961, I, p.274；S0把脚注号误读为8、姓氏丢失变音符、罗马数字I识别成数字1，均只记校勘。新增未知买家M. Parasson候选，并复用Claude《Flight into Egypt》作品、Dresden、Mazarin及Röthlisberger来源候选。分开记录“现藏Dresden”、Claude记录的买家、Röthlisberger所述画作至1653年属于Mazarin，以及“最可能通过代理为Mazarin绘制”的解释；后一项保留原文概率，匿名agent不立具体人名。上述出处未经直接查阅，仍是Haskell脚注中的报告/转述，不作为已核实关系。

p.182正文i10/i11、i12、i14、i17、i18分别与脚注1、2、3、4、5双向回链。新增4个候选、16条提及、10条statement；更新Prunières、Malvasia与Röthlisberger既有候选。p.182正文段转complete，复合段L294–347仍partial，下一范围L348–353（p.183注1–6）。全书账本273 complete、11 partial、45 excluded、474 queued；候选7,068、提及12,043、statement 5,875。


## 第七章印刷页183脚注L348–353（2026-09-30）

按源序迁入p.183注1–6，并核对`CHP-7.pdf`物理第17页。注1 Passeri p.210定位p.182–183关于Algardi辞去赴法合同的跨页引语。注2的L168与L349分属正文规范段和复合注释段：保留交易日期不确切但必须早于1647的限定，另记Bentivoglio→Lante→Mazarin转让链；d’Aumale p.8、Callari p.298仅作书目定位。注3分别保留1646年avviso（Roma 1938, p.477）、Benedetti p.5、Mazarin《Epistolario inedito》p.119所引1650-06-03致Maccarani信、Mazarin《Lettres pendant son ministère》IX p.693所引1661-03-06致Maccarani信、立面铭文及Maccarani在1675年拥有雕像与绘画陈列的报告。新建未识别avviso、来源出版物、1650年信件和未定类型画廊候选；复用1661年信件候选。注4–6分别以Prunières 1913 p.149、Baldinucci VI (1728) p.245、Pascoli I p.47定位Torelli、Stefano della Bella、Grimaldi叙述。页图校正L350 `Roma, 19 3 8`→`Roma, 1938`、`fletter osò March 1661`→`letter of 6 March 1661`、`Span`→`Spon`，并确认L353印本脚注号为6（OCR为8）；S0原文未改。所引页与档案均未独立阅读，相关内容保持Haskell的引文/转述层级，不建S6正式边。新增8个候选、净增24条提及、15条statement；9条正文statement完成脚注回链。p.183正文覆盖转complete；复合段范围扩至L294–353并保持partial，下一范围L354–357。全账本803段为274 complete、10 partial、45有理由排除、474 queued；候选7,076、提及12,067、statement 5,890。

迁移后检查：`python scripts/audit_tables.py --summary`为0 errors；仍有两条既存enrichment `source_ref`警告、474段queued、10段reviewed/partial。`python -m pytest tests/test_audit_tables.py -q`为11 passed。S0跨度、候选外键、跨段note 2、脚注标记和正文回链均通过核对。


## 第七章印刷页184脚注L354–357（2026-09-30）

按书序迁入p.184注1–4并核对CHP-7.pdf物理第18页。注1页图读作de Cosnac（S0为de Còrnac）和Taylor, p.332（S0把句点误作逗号）；注2去除pp.293 ff.后的OCR连字符。注1的de Cosnac p.144与Taylor p.332仅为Mazarin购入Charles I藏画的来源定位；注2的d’Aumale条目经书目确认是1653年Mazarin清单。注3另指de Cosnac item 1240中的1661年清单，记录Podesta作为编制者之一，并记录Haskell所称此前未被注意的Podesta–Mazarin联系；具体关系性质未知，不形成正式边。复用Podesta、Blunt作者、Revue des Arts、Bonnaffé与Briganti候选；书目将Briganti 1962识别为Pietro da Cortona，但作者仅列G.，身份留S3。书目同时识别Blunt 1958年Revue des Arts文章及Hoog 1960年Attributions anciennes à Valentin，未独立阅读引文页。

注4称Guercino的Cato现藏Marseilles，并引Hoog pp.270 ff.。将其与p.185正文“Scene from the Life of Cato”映射到同一源内作品候选cand-7092；修正p.185原mention与statement把作品标题错挂到Guercino画家候选的问题。位置为原书报告，馆藏地与实物身份尚未独立核实。新增10个候选、24条提及和11条statement；p.184正文段转complete，复合段覆盖扩至L294–357并仍partial。下一子范围L358–360（p.185注1–2）。


迁移后核验：audit_tables.py --summary errors=[]；保留两条既存enrichment source_ref警告、474段queued及9段reviewed/partial。tests/test_audit_tables.py：11 passed；git diff --check通过（仓库提示行尾转换，不构成检查失败）。24条新增提及锚点均与S0复合段匹配，11条statement、候选外键、脚注回链和p.184 complete状态有效。机械检查不是独立语义验收。

## 第七章印刷页185脚注L358–360（2026-09-30）

按书序迁入p.185注1–5。CHP-7.pdf物理第23页确认：注1 de Cosnac pp.169 ff.；注2 Hautecœur pp.39–49；注3 ibid. pp.84–89，明确回指注2同书；注4 Alazard pp.18–28及55–86；注5 Brienne, III, pp.88–90。书目核对分别复用cand-7086/cand-7087并新建Hautecœur作者/出版物cand-7096/7097、Alazard作者/出版物cand-7098/7099、Brienne《Mémoires》vol.III cand-7100。所引页均未独立阅读；不把脚注locator当作外部核实。

页图校读p.185注5印本为III，而S0 L360识作IH；更正只记入新citation statement的ocr_corrections，不改来源。p.185购藏相关i20–i22接注1，i25接注2，i26接注3，i29接注4，i30接注5；各citation statement同时记录linked_body_statement_ids。为复合源段L293–389新增9条mention，偏移按S0行293–389以LF拼接的字符索引计算；author与publication有意共享同一姓名跨度，ibid.仅锚定被回指出版物。

新增5个候选、9条提及、5条citation statement；p.185正文coverage从reviewed/partial改complete，复合段source_line_ranges扩至L294–360并保留partial。全账本为276 complete、8 partial、45 excluded、474 queued；候选7,091、提及12,100、statement 5,906。下一范围L361–367（p.186注1及p.187注1–6）。

## 第七章印刷页186–187脚注L361–367（2026-09-30）

沿复合段源序迁入p.186注1、p.187注1–6。页图校读OCR差异：L363 `p. no.`→`p.110`；L364 `RufFo`→`Ruffo`；L367 `Wittkower, 1938`→`Wittkower, 1958`。另在已迁正文statement记录视觉核读到的`Je sis`→`Je fis`、`es`→`et`、`Name os`→`Name of`、`eastern’front`→`eastern front`、`Baroque1`→`Baroque`、`Rainaldirs`→`Rainaldi’s`、`Modem`→`Modern`、`triumphantprogress`→`triumphant progress`；仅更正S2校读字段，S0保持原样。

注1 Wittkower p.269据书目唯一匹配其1958年Art and architecture in Italy；注1–3另以Alazard、Bonnaffé定位赞助与Ciro Ferri叙述，Ruffo来源未由书目定题。注4沿Pascoli两卷引用分别回链Mola叙述和Canini的两项脚注事实；Canini及Cardinal Chigi身份留待S3。注5沿Limentani、De Rinaldis和Bailly引用拆分Haskell对Louis XIV/Rosa关系变化的判断、无名Papal Nunzio对作品的先前呈献、未定名Rosa Battle于1697年从Versailles运往Paris、以及附随法文便笺。献画日期未明，1697仅属后续调运。注6把Blunt 1953、Wittkower 1958、Hautecœur和Chantelou连至书目相符出版物。引文定位不代表独立查阅相关页面。

新增10个候选（cand-7101–7110）、39条提及、14条书目定位statement及6条脚注内容statement；补明已有Wittkower、Limentani、de Rinaldis、Pascoli两卷、Bonnaffé及Ruffo候选。p.186–187正文分别回链脚注1和脚注1–6；全账本278 complete、6 partial、45 excluded、474 queued。下一范围L368–369（p.188注1–2）。



## 第七章印刷页188脚注L368–369（2026-09-30）

对照`CHP-7.pdf`物理第26页按源序迁入注1–2。注1为Wittkower, 1955, pp.230–231, with bibliography；按本书书目复用作者候选cand-2818及《The Sculptures of Gian Lorenzo Bernini》（London, 1955）出版物候选cand-4383。注2 `ibid.`回指注1同一出版物，locator为pp.234–236。引文页未独立阅读。两条citation statement分别回链`st-chp7-p188-i17`和`st-chp7-p188-i21`；新增3条mention：注1作者及作品定位共锚于原文跨度，注2锚定ibid.页码引文。
p.188正文L233–241及其注释现complete；复合段source_line_ranges扩为L294–369并保持partial。写入后当前账本为803段中279 complete、5 partial、45有理由排除、474 queued；候选7,101、mentions 11,939、book-statements 5,928。`audit_tables.py --summary`为0 errors，11项审计测试通过。
计数勘误：旧状态摘要曾报告12,139条提及；写入前以mentions.csv直接读取及audit复核均为11,936条唯一ID，本批增加3条后为11,939。两个数相差203；当前材料未能确认旧报告差额来源，S2进度按实际主表计数。
下一源序范围为p.189注1–6（L370–374）。页图显示复合段L373的注号为5，S0 OCR误作6；后续记录在citation statement的`ocr_corrections`中，不修改S0来源转录。

## 第七章印刷页189脚注L370–374（2026-09-30）

对照`CHP-7.pdf`物理第27页按源序迁入注1–6。出版物依据本书书目对应：Soprani/Ratti《Vite de’ Pittori, Scultori ed Architetti Genovesi》二版全2卷，Pascoli卷I，Wittkower〈Domenico Guidi and French classicism〉，Montaiglon《Correspondance des Directeurs...》卷I，Bellori《Le Vite inedite》（1942），Zanotti《Storia dell’Accademia Clementina》（1739），Alazard《L’Abbé Luigi Strozzi...》，De Dominici《Vite dei pittori...》卷IV。书目只用于识别出版物，不把引文页当作独立核验。
注4还含叙述性材料，单独记录1685年未具名罗马法国学院负责人试图请Luca Giordano为Louis XIV作画，以及Haskell称画家未履行义务；工作、负责人和义务细节未补造。该负责人独立于正文询问Cignani的未具名负责人，待S3对齐。
页图确认L373与正文L255脚注号均印作5，而S0 OCR识作6；仅在S2 statement记录校读，不改写来源。新增7个候选、26条mention、12条statement，细化既有Soprani、Bellori及De Dominici候选；p.189转complete，复合段source_line_ranges扩至L294–374并仍partial。全账本280 complete、4 partial、45 excluded、474 queued；候选7,108、mentions 11,965、statements 5,940。audit 0 errors，测试11 passed；下一范围L375–378（p.190注1–5）。

## 第七章印刷页190脚注L375–378（2026-09-30）

按源序迁入p.190注1–5，对照`CHP-7.pdf`物理第28页。注1拆分Harris 1960年《La misión de Velazquez in Italia》（pp.109–136）与1961年Colonna/Mitelli文章（pp.101–105）；1961年来自注释本身，书目条目未列年份。注2以书目识别M. E. Ghelli的《Il viceré marchese del Carpio (1683–1687)》（1933、1934两部分）；注3识别N. Maclaren《The Spanish School》p.76；注4分别登记1677-06-12 Avviso与其Roma XIX (1941), p.308发布定位；注5以Harris 1957文章定位、分别登记其所述Society of Antiquaries相簿、题铭所称购藏及Haskell对Harris的致谢。引文页均未独立查阅；题铭和相簿不作为独立核实的外部事实。

新增12个候选、19条非重叠精确提及及10条statement。复用cand-1292 Harris、cand-0573 Del Carpio、cand-4490 Rome、cand-6953 antiques。题铭中的Gasparo名字按p.190 i13的源内明确同名映射到cand-0573；相簿candidate cand-7129不与p.191三十卷绘画集cand-6955合并，Society未推断城市或分馆。p.190正文注1–5现全部回链；p.190 coverage转complete，复合段覆盖扩为L294–378并保持partial。

页图确认脚注L375 `i960`为`1960`，L376 `politics!`为`political`；正文L263 `48?`是脚注号2且`Hs`为`His`，L264 `havewelcomed`应分为`have welcomed`，L266 `- - compelled`属于OCR噪声。结构化校读附在statement `ocr_corrections`，原书S0不改。题铭末尾`Helicce`拼写在页图中不够确定，保留原转录、不作规范化。

当前账本803段为281 complete、3 partial、45有理由排除、474 queued；候选7,120、提及11,984、statement 5,950。`audit_tables.py --summary`为0 errors；11项审计测试通过。19条本批mention偏移逐条与复合段核对，候选外键、citation及关系候选、正文回链、p.190 coverage均通过。下一范围为L379–387（p.191注1–4、6–8、10–11），随后L388–389。



## 第七章p.191–192脚注L379–389（2026-09-30）

按源序迁入p.191注1–4、6–8、10–11（L379–387）及p.192注1–2（L388–389），分别对照PDF物理第29、30页。p.191注1复用Bellori 1942《Le Vite inedite》出版物；注2复用Society of Antiquaries相簿及Pacichelli卷I，避免与注9重复建候选；注3将Domenico Bernino与题名未给出的p.28引文对象分开；注4登记1684-07-27 Duc d’Estrées致Louis XIV书信及Montaiglon卷VI；注6、10复用De Dominici卷IV，注10另记录Haskell对Del Carpio那不勒斯素描的指引及Saxl文章；注7登记1924年Duque de Berwick y de Alba公开受礼演说、所涉Academia与具名人物；注8复用Bottari卷II并登记Orlandi《Abecedario Pittorico》；注11登记1683–1687经那不勒斯运往西班牙的清单MS El Escorial &-IV-25及Warburg Institute的影印本位置。出版物和所引页仅按本书书目及脚注定位，均未独立阅读；题名、馆藏号及引文事实保持Haskell报告层级。

p.192注1复用Pascoli卷I、II；注2登记Griseri 1956、Longhi 1954、Zanotti卷I引文，并将“Giordano的赴西邀请在Franceschini拒绝后发生”单列为Haskell转述Zanotti的原书陈述。原文没有给出邀请发起者、日期或确切安排，不补造关系端点或时间。

页图校读仅写入S2：p.191 L383末尾OCR残符删除；L384 `ame`→`ante`、`Exento`→`Excmo.`；L385 `Et`→`II`；L387 `da Nápoles`→`de Nápoles`；p.192 L388 `Pascoíi`→`Pascoli`。S0不改。新增15个候选、46条精确提及和19条statement；12条正文脚注待办全部回链，p.191、p.192正文coverage及复合注释段均转complete。另将第IV节L1文件名标题按非原书内容排除。全账本803段为284 complete、0 partial、46有理由排除、473 queued；候选7,135、提及12,030、statement 5,969。`audit_tables.py --summary`为0 errors，`tests/test_audit_tables.py`为11 passed；引用页未直接查阅的边界不因机械校验而解除。

接续段核查：`chp-7:07_CHP-7_sec_iv:l6-21`覆盖印刷页193正文及注2；同页注1、注3分别在后置脚注复合段`l97-119`的L98、L99，仍待迁入。L20跨页句已在后续段p.194 L24闭合并互链；下一段按coverage顺序为p.195正文。


## 第七章印刷页193–194正文迁移（2026-09-30）

按S0顺序处理`chp-7:07_CHP-7_sec_iv:l6-21`与`chp-7:07_CHP-7_sec_iv:l23-36`，分别对照`CHP-7.pdf`物理第31、32页。p.193正文及注2已迁入；p.193注1、3在L98–99仍待后置脚注段处理。p.194正文与本段注2已迁入，注1、3、4分别在L100–102，仍待迁入。S0原文未改。

p.193 L20“make up for the”由p.194 L24续为“glories of the Renaissance … all turned southwards”。保留原p.193开放statement的原文跨度，并以`st-chp7-p194-cross-page-renaissance`在p.194锚定续句、建立反向ID链接；不把南向擅自收窄为特定目的地或委托对象。

p.194记录Johann Georg III聘用Stefano Cadani、Arrighini为Georg Wilhelm建剧院、Carlone等画家工匠家族迁往德国宫廷、德意志诸邦吸引意大利画家、德意志赞助对意大利绘画的重要性、Liechtenstein家族的42幅委托，以及Schönborn家族从8名意大利画家订画等陈述。另按Haskell原文层级记录罗马与维也纳、Pommersfelden、Vaduz的收藏比较，保留其对赞助、创作题材及情色倾向的评价语气；8条艺术家委托记录保留正文所列的城市关联，不推定作品的实际创作地点。

新增17个候选、73条精确提及、35条原书断言／关系候选。复用p.194索引候选及既有城市、家族、艺术家候选；新建未具名的剧院、家族/艺术家集体、政治实体集合、作品组、书信、主题词与F. Wilhelm文献候选。Carlone家族不与索引中的Carlo或Gianandrea个人合并；原文只称“Prince of Liechtenstein”，虽索引p.194列Wenzel，本段仍把实名身份留待S3。正式关系不在S2提前生成。

PDF校读记入S2：L29 `Schônborn`→`Schönborn`；L33 `Pommersfclden`→`Pommersfelden`、`could'now`→`could now`；L35 `tire Prince`→`the Prince`。L25、L27、L32行首符号及L32–33引号为版面/OCR残痕，引用时不当作词语。脚注2依据本书书目识别Zanotti《Storia dell’Accademia Clementina》及F. Wilhelm文章；被引页未独立阅读，记为引文定位而非事实核验。

p.194 L35末尾“Tutte le pitture che intrano questa”保持开放状态，待p.195 L38–46补读和归属。p.193的注1、3和p.194的注1、3、4均位于复合脚注段L98–102，尚未处理。跨章身份与候选去重留待S3；当前所有关系仍是S2原书陈述候选。

## 第七章印刷页195正文迁移（2026-09-30）

按源序阅读`chp-7:07_CHP-7_sec_iv:l38-46`并对照`CHP-7.pdf`物理第33页。新增21个候选、76条精确提及、31条statement。p.194 Prince of Liechtenstein引语由L35续至p.195 L39并归于1691年；分别记录画廊“世俗”评价及其所列画作，不据索引的Wenzel条目提前确定称号指向的具体人物。Cignani、Maratta、Baccinelli、Piola、Loth、Fumiani、Strudel作品依引语层级记载；姓氏与个别作品身份未决。对Carlo Loth与索引Johann Karl Loth保持区分。Schönborn致信内容保留原法文、意大利文及书中转译语境，不将其概括扩大为所有德国赞助人的证据。

另记录德国赞助与女性裸体题材的Haskell概括及其比较语气、Cagnacci由Romagna至Venice及1657年被召至Vienna的叙述、Lazzarini与Cignani的评价引语、英格兰赞助对意大利艺术的前后期比较、Charles II尝试收回仍可取得的Charles I旧藏、Verrio入英路径与身份自称。p.195末句“A Sea triumph, being”留待p.196续读；Prince的实名、未具名Ambassador及受聘画作身份留给S3或后续对象级判断。p.195脚注1–5位于后置复合段L103–106，尚待按源序迁入。

页图校读只登记于S2：L40 `Schonborn`→`Schönborn`、`abhallten`→`abhalten`；L45 `fdial piety`→`filial piety`；L46 `Gentilcschi`→`Gentileschi`，并确认`1675`后的符号为上标脚注5。S0来源原文未改。脚注2仅依本书书目定位Zanotti及F. Wilhelm文献，不视为独立核查被引页。写入后`audit_tables.py --summary`为0 errors，11项审计测试通过；总账803段中284 complete、3 partial、46有理由排除、470 queued，候选7,198、mentions 12,271、statements 6,063。下一规范段为p.196的`chp-7:07_CHP-7_sec_iv:l48-61`。

## 第七章印刷页196正文与页内注2迁移（2026-09-30）

按源序阅读`chp-7:07_CHP-7_sec_iv:l48-61`，对照`CHP-7.pdf`物理第34页。新增23个候选、69条精确提及、25条statement。p.195开放的“A Sea triumph”由L49续明为一幅含Charles II的大型画作；保留Haskell对其谄媚及与王权无关的评价，并闭合前页statement。另记录Verrio在Windsor的壁画系列、晚期Stuart专制论的图像计划、其从法国学习后在英格兰引入巴洛克装饰类型及其视觉/风格评语。

Gennari部分区分其与Verrio的同期入英、Guercino亲属关系、巴黎经历、年薪£500与王室委托、神话题材画及其情色评价、将Elizabeth Felton描绘为Cleopatra的作品、Danaë题材及后转祭坛画、1685年后James II宗教政策下的需求、Whitehall未名教堂装饰合作，以及1688年离英后经法国返意的叙述。未名王后不与Queen Anne混同。Verrio段分别登记离开宫廷、乡间宅邸工作、新政权在Hampton Court用人、取材Julian the Apostate writings的William III胜利寓意画，以及其在Louis XIV/William III两端服务、Shaftesbury肖像主题和Queen Anne年金；不把评语转为外部事实。

页内注2 `Wind, 1939–40, pp.127–137`依本书书目识别为E. Wind的〈Julian the Apostate at Hampton Court〉，只记引文定位，未核读该文。注1在后置复合段L107，仍待源序迁入。PDF校读差异登记于S2：L53缺失£符号（印本为£500）、`couldscarcelyfulfd`→`could scarcely fulfil`；L55 `James H’s`→`James II’s`、`CathoEcism`→`Catholicism`；L59 `à complex`→`a complex`、`Wifliam III`→`William III`；L61 `a Wind`实际为上标注号2后接Wind。S0原文未改。France作为地理地点与其在反William III政治力量中的角色分开建候选；Whitehall/Hampton Court及教堂空间与具体装饰作品分别登记。

p.196 L60的Verrio—Cassana句续至p.197 L63；注1待L107，因此该段为reviewed/partial。p.195句子已闭合，但注1–5仍在L103–106，故p.195继续partial。迁入后`audit_tables.py --summary` errors=[]，审计测试11 passed，`git diff --check`通过（仅报告仓库行尾转换提示）。总账803段中284 complete、4 partial、46有理由排除、469 queued；候选7,221、mentions 12,340、statements 6,088。下一规范段为`chp-7:07_CHP-7_sec_iv:l63-75`（p.197正文）。

## 第七章印刷页199第V节正文 L3–7（2026-09-30）

按S0顺序处理`chp-7:07_CHP-7_sec_v:l3-7`，对照`CHP-7.pdf`物理第37页。新增10个候选（cand-7272–cand-7281）、46条提及和14条statement。行3–6按Haskell的作者综合论述分别记录意大利艺术赞助环境变化、教宗声望下降与意大利化欧洲的悖论、权力分散和“省区中心”、罗马艺术声望及英德收藏者的替代选择、地方政权限制下艺术家的活动与作品外传、所列画家的“European favourites”评价，以及复杂战争和意大利重返国际政治。保留totally、indirectly、could and often did、nearly等限定；没有将群体性评价改写成逐人逐城的事实。

地名复用既有候选：Italy、Rome、England、Germany、Bologna、Venice（城市）、Naples、London、Paris、Vienna、Munich、Stockholm、Madrid、Europe；具名画家复用索引候选。新增Italianising of Europe、未具名画家群体及其未识别作品组、英德潜在收藏者群体、未枚举复杂战争、未具体界定的意大利“isolation”、作为外交主体的Venice、Holy League及未具名King of Poland。L4 Venice映射城市cand-3401，L7 Venice映射政治行动者cand-7278；不在S2中合并城市与政体。King of Poland不预判为索引候选John Sobieski；Holy Roman Empire复用cand-6994。教宗复数指称保留为集体候选，不映射到单一教宗。跨章身份与联盟规范名留待S3。

页图确认印本为Franceschini；S0 OCR作Francéschini。更正仅登记在该段S2 statement，来源未改。p.199页底Sweetman注1属前一节正文，本段无自己的注号；前一节的脚注已在复合段L97–119处理。L7末尾“Then came the”保持开放并指向下一规范段`chp-7:07_CHP-7_sec_v:l9-18`，未提前登记完整的战争事件。

覆盖状态为reviewed/partial。写入后全账本803段中292 complete、1 partial、47有理由排除、463 queued；候选7,272、提及12,561、原书statement 6,192。`python scripts/audit_tables.py --summary`为0 errors；`python -m pytest tests/test_audit_tables.py -q`为11 passed。仍有2条既存enrichment `source_ref`警告，以及463段queued和1段partial；机械检查不替代全书语义质量核查。

## 第七章印刷页200图版页及视觉补录（2026-09-30）

按S0源序核对`CHP-7.pdf`物理第40–42页。物理第40页的Plate 30页上方印有分组题头“ENGLISH VISITORS OF THE SEVENTEENTH CENTURY AND ITALIAN ARTISTS (see Plates 30 and 31)”，规范OCR `l20-21`仅留下页码和反向残片；按既有做法追加同版派生转录`07_CHP-7_sec_v_visual-transcription.md`，作为编辑性图版导航处理，不据此建立主题、实体或知识层级。物理第41页的Plate 31横置题注OCR与书前图版清单L90–91重复，没有增加独立断言，故`l23-37`有理由排除，保留原图和OCR。

规范OCR `l39-40`保留Plate 32a题注，迁入Ribera、作品《Drunken Silenus》、Silenus及“painted for Gaspar Roomer”四项信息，分别复用`cand-3876`、`cand-4089`、`cand-4161`和`cand-2223`。物理第42页同时印有Plate 32b题注，规范OCR漏掉该行；在派生视觉转录补录“Paolo de Matteis: The Choice of Hercules painted for Lord Shaftesbury”，迁入艺术家、图版作品、题名人物Hercules和Lord Shaftesbury四项提及，复用`cand-3214`、`cand-4071`、`cand-4162`和`cand-2426`。两条图注与书前图版目录及p.198正文交叉定位；保留S2候选边界，不作身份合并或正式关系裁决。未新增候选。

本批覆盖：两段OCR残段有理由排除，Plate 32a原段和两段视觉转录均为reviewed/complete；新增8条精确提及（含Silenus与Hercules的嵌套题名跨度）和6条caption statement。`build_source_segments.py`预检后重建为805段，既有803段无差异，仅新增上述两段；`audit_tables.py --summary`为0 errors，测试`tests/test_audit_tables.py`为11 passed。当前全书805段为296 complete、1 partial、49 excluded、459 queued；候选7,296、提及12,639、statement 6,226。两条既存enrichment `source_ref`警告和全书S2未完成状态保留。下一规范源段`chp-7:07_CHP-7_sec_v:l42-55`为p.201正文；它将闭合p.200 L17的“furnishing”。p.200脚注1–5、7仍待后置复合段L62–76，不能据正文续句闭合便将p.200段改为complete。

## 第七章印刷页201–202正文与p.200–202脚注收口（2026-09-30）

按S0源序完成`chp-7:07_CHP-7_sec_v:l42-55`（p.201正文）及`l57-60`（p.202正文），前者闭合p.200 L17的“furnishing”。正文迁移新增41个候选、105条精确提及和41条原书statement；完成跨页、脚注标记和正文回链。印本校读更正只记于S2，S0 OCR保持不变。

随后迁入复合段`chp-7:07_CHP-7_sec_v:l62-76`中的p.200注1–5、7，p.201注1–6及p.202注1；p.200注6此前已由L18登记，本次保留并与印本编号核对。新增10个候选（cand-7347–cand-7356）、44条精确提及和33条statement，含引文定位及脚注所述事实；所有正文脚注标记回链完成。p.200 L67印本注号为5（OCR误为6），不与L18原有注6合并。L69倒置图版残段与书前图版清单重复，按coverage说明处理，不新增提及或断言。

对照`CHP-7.pdf`物理第38、43–44页，校记p.200 `tbe`、`ofPeterborough`、脚注编号及漏引号，p.201 `H`/`4$`/`Ug`，p.202 `i893`等OCR差异；来源文本未改。body与footnote迁移分别由`p201_p202_body_migration.py`和`p200_p202_footnotes_migration.py`以默认dry-run及备份写回。coverage核对后，第七章55段为47 reviewed/complete、8 excluded；p.200、p.201、p.202正文及后置脚注均已收口。

更新后的全书账本为805段：300 reviewed/complete、49 excluded、456 queued；候选7,347、提及12,788、原书statement 6,300。`python -X utf8 scripts/audit_tables.py --summary`为0 structural errors，`python -X utf8 -m pytest tests/test_audit_tables.py -q`为11 passed；审计仍提示两条既存enrichment `source_ref`无法解析，并要求后续人工检查S2语义质量。下一源段为`chp-8:08_CHP-8_intro:l1-1`。这组机械检查不替代语义质量验收。

## 第八章印刷页205正文迁移（2026-09-30）

按S0顺序迁移`chp-8:08_CHP-8_sec_i:l23-28`，逐段阅读并对照`CHP-8.pdf`物理第3页。新增20个候选（cand-7401–cand-7420）、45条提及和21条statement。把Gaspar Roomer的传记报告分成来源可定位的断言：来源地、1634年前定居Naples、航运与贸易、借贷、在Naples接待贵族、Carmelite捐赠与女儿入修院、1647年Masaniello起义中的避险、1656年瘟疫后康复、死亡与遗产。Haskell关于“half the nobility”、五百万ducats和1500余幅画作的表达按原文口径保留，不变成已独立核实的数量。

作品与人物内容分别记录：复用索引p.205 Roomer主项及Carmelites、Masaniello起义、Caravaggists、怪诞趣味等子项；复用《The Drunken Silenus》图版候选，并对《The Flaying of Marsyas》和Sandrart回忆中的未识名Cato图像分别建开放候选。Apollo、St Peter、Silenus、Marsyas及群像作为作品内容保留，不把神话描绘写成历史事件；Cato具体身份与King of Spain身份留待S3。涉及收藏家与画家、捐赠对象、家属及修院的原书关系保留为S2 statement候选，尚未形成正式边。

PDF页图确认L25 `ofliis`应读为`of his`、L28 `heowned`为`he owned`；只在S2 statement校记，S0不改。`Scandinavia`后的微小印记辨认不清，保留OCR字串，不猜测它是标点或脚注号。脚注1–4位于复合段L130–133，尚待按源序迁移；L28以Carlo中断，Saraceni续于p.206 L31，三幅画的claim保持open。故本段coverage为reviewed/partial；p.204仍因注1–3待迁移而partial。下一段为`chp-8:08_CHP-8_sec_i:l30-41`。

写入后`python -X utf8 scripts/audit_tables.py --summary`为0 structural errors；全书805段中302 complete、2 partial、52有理由排除、449 queued，候选7,411、提及12,952、statement 6,360。`python -X utf8 -m pytest tests/test_audit_tables.py -q`退出码为0。审计仍提示两条既存enrichment `source_ref`警告；本批机械通过不替代语义验收。

## 第八章印刷页206正文迁移（2026-09-30）

按S0顺序处理规范段`chp-8:08_CHP-8_sec_i:l30-41`，对照`CHP-8.pdf`物理第4页。新增19个候选（cand-7421–cand-7439）、55条精确跨度提及和23条原书statement。迁入Saraceni以闭合p.205 L28的Carlo姓名及“三幅画”statement；保留跨段回链，未重复打开已闭合的claim。

记录Roomer购入Valentin、Simon Vouet与David de Haen的作品；其对安全观看的战争题材及对Masaniello逃险的Haskell式解释；Roomer对Aniello Falcone的偏好及其绘制的无英雄战争图；小幅风景、海上风暴、动物和静物等弗兰德斯画家题材、临时迁居Rome的群体；Roomer引语中的画作评价、inventory请求及Jan Vandeneynde/Brussels。为这段未识名的书面引语保留archive候选，但不声称底层信件或inventory原件已识别。记录九位画家及数百幅画作的报告、Haskell关于Antwerp与Naples文化混合的评价、Roman painting与Venetian colour比较，并保留“perhaps”“almost”对Bassano八幅动物画的限制。

记录Roomer长期购藏、信息来源不足、向Low Countries运送Neapolitan paintings（以Bartolommeo Passante作品为例）、推测中的反向交换，以及两幅Van Dyck作品“probably acquired locally”。Valentin和Bassano在正文只给姓氏，保留独立候选待S3；已有p.206索引候选并不自动替代身份判断。Rubens《Feast of Herod》约1640年抵达Roomer宫殿、作品成熟期和约六年前创作均按Haskell的陈述层级记录。图像说明分录宴会空间、无名女孩、Herodias之女及Herod；因正文未明确无名女孩与Herodias之女是否同一，候选保持分开，描绘和人物心理仅作图像内容/作者解释。

页图核读差异只记S2：L33 `still Eves`→`still lives`、`very sine`→`very fine`；L36 `van dor Bos`→`van der Bos`；L38 `Naples-—thereafter`→`Naples—thereafter`。S0未改。L32脚注号1后的短横暂不规范化。p.206注1–2仍在复合段L134–135，故coverage为reviewed/partial；p.204注1–3及p.205注1–4也仍待同一后置脚注源段按序处理。下一规范段为`chp-8:08_CHP-8_sec_i:l43-51`（p.207）。

写入前通过默认dry-run核对来源资产/段落哈希、精确提及跨度、断言原文范围、候选外键和预期coverage；应用后`python -X utf8 scripts/audit_tables.py --summary`无结构错误，`python -X utf8 -m pytest tests/test_audit_tables.py -q -o addopts=''`为11 passed。当前账本805段中302 complete、3 partial、52有理由排除、448 queued；候选7,430、提及13,007、原书statement 6,383。仍有两条既存enrichment `source_ref`警告；S2全书语义召回尚未审完。

## 第八章印刷页203–204正文与注释迁移（2026-09-30）

p.203来源段`08_CHP-8_intro:l7-10`（注1–4）与`08_CHP-8_sec_i:l3-12`（正文和注5）完成迁移，新增34个候选（cand-7357–cand-7390）、75条提及和21条statement。记录Genoa、Naples、Bologna的家族及赞助群体，B.109手稿、Biblioteca Comunale、Oretti和被引书目定位；家族按来源语境分别保留，未把脚注书目定位当成已独立核验的事实。`CHP-8.pdf`物理第1页校读差异只写入S2，不改S0；末句由p.204 L15闭合，p.203现为reviewed/complete。

p.204规范段`08_CHP-8_sec_i:l14-21`迁入正文，新增10个候选（cand-7391–cand-7400）、44条提及和18条statement。记录Ricci/Crespi旅行、经销安排，Valletta、Giordano与Solimena，以及Haskell关于罗马/省区赞助与跨地域收藏的论述；保留原文的论述层级和限定，不将模糊人物指称预先并入具体实体。对照PDF物理第2页，确认替换字符、破折号占位和OCR `hot only`应读作`not only`，校读不写回S0。p.204注1–3位于复合来源段L127–129，尚待按源序迁入，因此该正文段仍为reviewed/partial。下一规范段为`chp-8:08_CHP-8_sec_i:l23-28`（p.205）。

写入后`audit_tables.py --summary`为0 structural errors；当前805段中302 complete、1 partial、52有理由排除、450 queued，候选7,391、提及12,907、statement 6,339。审计仍提示两条既存enrichment `source_ref`警告及S2未收口；本次未把结构审计表述为语义验收。


## 第八章印刷页207–208正文迁移（2026-09-30）

p.207规范段`chp-8:08_CHP-8_sec_i:l43-51`迁入15个候选（cand-7440–cand-7454）、53条提及和17条statement。记录Roomer的购藏倾向、可能经佛兰德中介购画、Preti《Marriage Feast at Cana》、Giordano关系与未识名作品、de Dominici转述及艺术赞助证据缺口。页图校读只记S2；末尾关于Roomer是否对Preti的“Venetian”画不满的反问保留未决，待下一页闭合。注1–2仍位于`08_CHP-8.md` L136–137。

p.208规范段`chp-8:08_CHP-8_sec_i:l53-60`新增10个候选（cand-7455–cand-7464）、47条精确跨度提及和23条原书statement。p.208 L54闭合p.207的反问，同时记录Haskell称证据不足，未把“此后未再委托Preti”当作事实。记录Roomer对Giordano的批评与支持、自然主义倾向、Codazzi场景、de Wael农民生活版画、Ruoppolo静物画外运、佛兰德静物画对那不勒斯画家的影响及Rubens《Feast of Herod》的传播评价；记录Jan与Ferdinand van den Einden的合伙、父子、财富/藏画继承、Ferdinand的赞助与Preti委托，并将Van den Einden与Roomer的“brutal realism”保持为Haskell推断。p.206的Jan Vandeneynde与本页Jan van den Einden身份关系留待S3；Ferdinand所藏Giordano作品按原文保留为未识名知识缺口。

对照`CHP-8.pdf`物理第5–6页，S0 OCR差异只记入S2校读，其中p.208 L60注号8按印本改读为6。p.208脚注1–7位于`08_CHP-8.md` L114–120，仍待按源序迁移；故p.207、p.208 coverage均为reviewed/partial。dry-run校验来源/段落哈希、提及跨度、原文引用及候选外键后写回。写回后805段总账为302 complete、5 partial、52有理由排除、446 queued；候选7,455、提及13,107、statement 6,423。`audit_tables.py --summary`为0 structural errors，审计测试11 passed；仍有两条既存enrichment `source_ref`警告。下一规范段为p.209 `chp-8:08_CHP-8_sec_i:l62-70`。


## 第八章印刷页209正文迁移（2026-09-30）

按S0顺序处理`chp-8:08_CHP-8_sec_i:l62-70`，对照`CHP-8.pdf`物理第7页。新增11个候选（cand-7465–cand-7475）、43条提及和21条statement。记录Don Antonio Ruffo的Messina出身、贸易与税收收入、1661年短暂outlaw经历及其城市特权背景；其艺术赞助、宫殿建置、超过350幅藏画、约1646年起持续约三十年的收藏、代理网络、当代艺术兴趣、收藏陈列规则及Guercino/Rembrandt配对作品和议价过程均按Haskell的叙述层次拆录。`must have been`、`seems`、`probably`及`almost`保留为限定；125 ducats/figure、100 scudi与后续100 ducats保持原单位。

对照页图后，`Use`→`life`、`Strada Emnianuela`→`Strada Emmanuela`、`halfa figure`→`half a figure`只记录在S2，S0未改。p.209注1在`08_CHP-8.md` L135待迁；L70的“representative collection”由p.210 L73续接，因此本段partial。写回前dry-run校验来源和段落哈希、精确提及、原文引用及候选外键；写回后审计0 structural errors，测试11 passed。总账805段中302 complete、6 partial、52有理由排除、445 queued；候选7,466、提及13,150、statement 6,444；仍有两条既存enrichment `source_ref`警告。下一段为`chp-8:08_CHP-8_sec_i:l72-82`（p.210）。

## 第八章印刷页210正文迁移（2026-09-30）

按S0源序处理`chp-8:08_CHP-8_sec_i:l72-82`，对照`CHP-8.pdf`物理第8页。迁入13个候选（cand-7476–cand-7488）、95条提及及27条statement；闭合p.209“representative collection”跨页句。记录Ruffo对Rembrandt作品的收购、Rembrandt在意大利的接受、Breughel转述、对《The Blind Homer》的保留与赞赏、Guercino配对画、藏画数量及继承限定、Polidoro作品和版画、藏画散佚、画廊影响及那不勒斯绘画声望。保留“most of these”等范围词，不将群体判断分摊到个别画家；关系候选作为S2 statement保存，不提前写正式边。

页图校读只写入S2：`desiderate`→`desiderare`、四处`Russo`→`Ruffo`、清除`picture`后的OCR引号及`he. also`中的多余句点，S0不改。p.210无印刷脚注标记；末尾三兄弟的名字由p.211补全，本段当时标记partial。dry-run校验来源哈希、候选序号、提及跨度、原文引句与外键；处理后本段于p.211续接关闭。

## 第八章印刷页211正文与后置注补录（2026-09-30）

按S0源序处理`chp-8:08_CHP-8_sec_i:l84-96`，对照`CHP-8.pdf`物理第9页。p.211首句补全p.210列出的del Rosso三兄弟姓名，迁入家庭/谱系材料、佛罗伦萨面粉专卖权、作品与收藏、书信/遗嘱及档案和出版物引文定位；来源报告的死亡、继承与家族信息保留原书转述层级，不把所引资料写成已独立核验，也不预先转为S6正式关系。

分节OCR L90–96只保存脚注1尾段；整章OCR独有的脚注1开头及注2–3经PDF物理第9页核对，记入派生文件`02-sources/02-Markdown/08_CHP-8_sec_i_notes_p211_visual-transcription.md`。转录不复制已在分节OCR中的脚注1尾段。印本注号为3，整章OCR误识为8。新增31个候选（cand-7489–cand-7519）、77条精确提及及25条statement；`chp8_p211_migration.py`的dry-run先核对来源/段落哈希、候选序号、提及跨度、statement原文与候选外键，再执行写回。

覆盖状态：p.210现为reviewed/complete；p.211正文为reviewed/partial，因为“their grandfather”句续至p.212 L99；补充视觉转录段为reviewed/complete。重建来源段后账本共806段，304 complete、7 partial、52 excluded、443 queued；候选7,510、提及13,322、statement 6,496。`audit_tables.py --summary`为0结构错误，审计测试11项通过；两条既存enrichment `source_ref`警告仍待S5处理。下一queued段为`chp-8:08_CHP-8_sec_i:l98-106`（p.212）。

## 第八章印刷页212正文迁移（2026-09-30）

按S0源序处理`chp-8:08_CHP-8_sec_i:l98-106`，对照`CHP-8.pdf`物理第10页。p.212 L99闭合p.211“their grandfather”，所指为较年长的Andrea（cand-2279），与后文较年轻的Andrea和Lorenzo分开。新增33个候选（cand-7520–cand-7552）、91条提及和24条statement；补回p.211收藏品提及及脚注定位，另将p.211已映射为Del Rosso家族的“their collection”改指一个单独、暂未分类的收藏对象。p.212提到的Gaspar Roomer collection复用p.205已有候选cand-7407，未再建重复对象。

记录Theatine教堂及家族小堂、Vannini壁画和祭坛画、四幅旧约题材画、Del Rosso家庭其他藏画、那不勒斯绘画群和收藏来源、Luca Giordano与家族的购藏联系、1613年大公致西班牙总督的信、Giordano 1679年访佛罗伦萨、Corsini小堂委托以及Riccardi宫壁画等。保留“probably”“perfectly possible”“may well”等原文限定；不把可能中介角色改成正式关系。未名收藏、书信端点与作品组保留当前身份边界，关系均只作S2 statement候选。L105 `given.the`及L103 “heirs ' of”按物理页图校正，S0不改；PDF显示引号后无撇号，S0中的单引号属于OCR误识。旧约作品中的Susanna主题与已有Van Dyck同题候选分开。

默认dry-run核对段落/来源哈希、精确提及跨度、原文引用和外键后应用。p.212 L106末句在“one”处保持open，期待下一规范段`chp-8:08_CHP-8_sec_i:l108-118`（p.213）；本页注1–5在后置来源段待迁。写入后全账本806段：305 reviewed/complete、7 reviewed/partial、52有理由排除、442 queued；候选7,543、提及13,413、原书statement 6,520。`audit_tables.py --summary` errors=[]；`tests/test_audit_tables.py`为11 passed；`git diff --check`无空白错误，仅提示既有行尾转换。仍有两条既存enrichment `source_ref`警告；S2全书语义处理未完成。下一queued段为p.213 `chp-8:08_CHP-8_sec_i:l108-118`。

## 第八章印刷页213正文迁移（2026-09-30）

按S0源序处理`chp-8:08_CHP-8_sec_i:l108-118`，对照`CHP-8.pdf`物理第11页。L109接续p.212的Giordano情色画句并闭合“one of which”；迁入一幅未识名画中的`ignudo`描写、Deianira and Nessus、Galatea and Tritons、The Rape of Proserpina等神话题材，以及Giordano宗教画、虔敬画和祭坛画modelli。记录Del Rosso兄弟对未完成笔触的偏好、Haskell关于其经Giordano介入而收藏François Nomé作品的可能性、Nomé／Monsù Desiderio名称、库存标签“Lorenese”、11幅废墟画及Callot印版；Babylon、Temple of Solomon和Callot《La Fiera dell'Impruneta》复用既有索引候选，未另建重复实体。印刷品与所称原始版画板分开，后者因当前类型表无印版类型暂留未分类。

继续记录Del Rosso收藏以Naples为重、忽视Rome、从Florentine disegno转向colore及其潜在文化影响；Haskell将Giordano介入Corsini chapel和Palazzo Riccardi装饰的说法保留为条件句。Livio Mehus的创作能力评价与其画作在1677年及12年后去向分别保存；“特殊赞助或受经济利益驱动”只记作Haskell的疑虑，未写成事实。L117–118转入Genoa的Marchese Girolamo Durazzo及其家族收藏，句尾“as was”续至p.214，保持open。脚注1位于稍后的规范脚注段待回链。

页图校读只记在S2，不改S0：L109 `os which`读为`of which`；L111 `François Nome`读为`François Nomé`；L112 `dellTmpruneta`读为`dell'Impruneta`；L116 `Been`读为`been`。新增21个候选（cand-7553–cand-7573）、85条提及及19条statement；复用p.211的1689年清单cand-7500、p.205既有Roomer collection cand-7407及p.212建立的Del Rosso收藏、Giordano作品和委托候选。默认dry-run核对来源资产及分段哈希、逐条提及偏移、statement引文和外键后写入。

写入后全账本806段：305 reviewed/complete、8 reviewed/partial、52有理由排除、441 queued；候选7,564、提及13,498、原书statement 6,539。`audit_tables.py --summary` errors=[]；`tests/test_audit_tables.py`为11 passed；`git diff --check`无空白错误，仅提示既有行尾转换。仍有两条既存enrichment `source_ref`警告；S2全书语义处理未完成。下一queued段为p.214 `chp-8:08_CHP-8_sec_i:l120-124`。

## 第八章印刷页214正文迁移（2026-09-30）

按S0源序处理`chp-8:08_CHP-8_sec_i:l120-124`，对照`CHP-8.pdf`物理第12页。p.214 L121“usual enough), but also to Naples”闭合p.213 L117–118的Durazzo/Bologna句。按紧邻先行语，将“the family”解析为Girolamo Durazzo家族，而非此前的Del Rosso家族；复用p.213预留的cand-7573 Giordano画作组，并细化为四幅画组，另复用八个具名作品索引候选：Giordano的四幅（Sophronia and Olindo、The Death of Seneca、Queen Jezebel torn to pieces by Dogs、Perseus and Andromeda），Durazzo语境的两幅Solimena旧约历史画（Judith with the Head of Holofernes、Deborah and Barach），以及Baglioni收藏中两幅Solimena画（Jacob and Rebecca、Rebecca and Eliezer）。Tasso复用现有索引候选，但来源只写姓氏；Baglioni威尼斯出版家族与Perugia语境cand-4279分立，待S3处理身份问题。

新增4个候选（cand-7574–cand-7577）、39条提及及7条原书statement；候选分别表示Durazzo语境两幅Solimena画、威尼斯Baglioni家族、Baglioni收藏中的Giordano/Solimena绘画组及该段的Neapolitan art概念。记录Solimena约1704年“added two further vast histories”的时间与续段语境限定，不把暗示扩写为确定委托；Baglioni末句`whose influence`的先行项保持未决，不把影响逐幅分配给两画家或两作品。页图确认印本文字为`Old Testament—Judith`（S0为连字符），只在S2记录校读；页图与S0均读`Deborah and Barach`，索引候选拼作`Deborah and Barak`，保留差异不规范化。

写入前dry-run核验段落及来源哈希、39条提及偏移、7条statement引句与候选外键；写入后`python -X utf8 scripts/audit_tables.py --summary`为0 structural errors，既有2条enrichment `source_ref`警告仍在；`tests/test_audit_tables.py`为11 passed，`git diff --check`退出码0。p.214正文coverage记为reviewed/partial，因注1–4仍待复合注释段迁入。另发现该合并段L157的p.214注4 S0 OCR止于“Nos.”，但物理页12可见完整续文；须在处理该注释段时建立带页图依据的补充视觉转录，再闭合相应coverage。下一S0段为`chp-8:08_CHP-8_sec_i:l126-157`。


## 第八章印刷页204注1–3迁移（2026-09-30）

按当前全书S2接续要求，处理复合注释来源段`chp-8:08_CHP-8_sec_i:l126-157`的L127–129，对照`CHP-8.pdf`物理第2页。注1引Zanotti卷II p.35及未能由短引文展开的L. Crespi pp.204、244；注2记录约1686年、当时在Chicago的《The Marriage at Cana》及Haskell所说的Veronese、Barocci影响；注3记录De Dominici卷IV p.141、Bologna pp.181/203以及Haskell转述的Valletta帮助Giordano处理图像题材问题、从另一收藏者购入Codazzi建筑画（人物由Cerquozzi、Micco Spadaro绘制）。所有引文页只作定位，未独立阅读。

复用Zanotti（cand-7115）、De Dominici（cand-4835）、Bologna（cand-7348）、Chicago及索引画家候选；新增cand-7578–cand-7582，分别表示身份未明的L. Crespi引文作品、van der Rohe引文作品、独立的Marriage at Cana作品、未具名售画收藏者及未识名Codazzi建筑画组。索引中的cand-0881是Crespi人物及其Marriage at Cana子项，不与作品合并；待S3处理作品/归属身份。未名卖方和作品仅作为关系候选端点，未写正式关系。页图校读将S0 OCR的`p. 3 5`读为`p. 35`、`Ill`读为`III`，只记录在S2；S0不改。

本次增加18条精确跨度提及和9条原书statement，其中脚注引用statement与内容断言分开，并回链p.204正文对应的三个脚注标记。p.204正文段现为reviewed/complete；复合脚注段仅覆盖L127–129、状态reviewed/partial，L130–157仍待处理，下一范围为L130–133（p.205注1–4）。写入由`chp8_p204_notes_migration.py`先dry-run再apply，并保留表备份。写后`audit_tables.py --summary`为`errors=[]`；`tests/test_audit_tables.py`为11 passed。仍有2条既存enrichment `source_ref`警告及全书439段queued、9段partial；本批结构检查不代表全书S2完成或事实外核。

## 第八章印刷页206脚注1–2迁移（2026-09-30）

复合注释源段`chp-8:08_CHP-8_sec_i:l126-157`的L134–135已对照`CHP-8.pdf`物理第4页迁移。注1仅记录Haskell对Saxl p.80的书目指引，并链接p.206关于Aniello Falcone为Gaspar Roomer绘制战争场景的正文statement；该注未说明关系细节，Saxl原文页未独立阅读。注2指向L. Burchard pp.383–387，按全书书目识别为1953年Rubens《Feast of Herod at Port Sunlight》文章，仍只作定位；“this picture”回指Rubens《Feast of Herod》，National Gallery of Scotland沿用既有机构候选。页图确认S0 OCR `pp. 383— 387`应读为`pp. 383-387`，校读只登记在S2。

新增候选cand-7592、7条精确跨度提及、2条citation statement。p.206正文的两个脚注标记分别回链；该正文coverage现为reviewed/complete。复合注释coverage扩为L127–135，L136–157仍待处理。对照p.207扫描与正文标记，L136为p.207注1（正文L44），L137为p.207注2（正文L50）；L138–144对应p.208注1–7，L145对应p.209注1。后续L146–148与已完成的p.211补充视觉转录有重叠，需按原文和印本逐条核对后复用已有记录，避免重复写入。下一批为L136–137（p.207注1–2）。

`chp8_p206_notes_migration.py`默认dry-run后以`--apply`写入，预先核对来源哈希、脚注原文、正文marker、候选序号和外键，并保留四张表的恢复备份。写后`audit_tables.py --summary`为0 errors，`tests/test_audit_tables.py`为11 passed；全账本806段中308段reviewed/complete、7段reviewed/partial、52段有理由排除、439段queued；7,583候选、13,589提及、6,566条statement。该检查不等于全书语义质量验收。

## 第八章印刷页207脚注1–2迁移（2026-10-01）

复合注释来源段`chp-8:08_CHP-8_sec_i:l126-157`的L136–137对照`CHP-8.pdf`物理第5页迁入，分别对应p.207注1–2，并回链正文L44、L50的两个脚注标记。新增6个候选（cand-7593–cand-7598）、23条精确跨度提及和11条statement；Ferdinando Colonna pp.29–32及De Dominici卷III、IV页码作为Haskell的引文定位，未独立阅读所引页。记录Roomer向Ferdinand van den Einden遗赠70幅画、Ferdinand向三女儿各留三分之一、一位未具名女儿与Don Giuliano Colonna结婚及Luca Giordano于1688年编制两人收藏目录；不臆定该女儿姓名或三份遗赠的个别归属。Haskell对“许多画”经Van den Einden、最初经Roomer流入Colonna收藏的判断保留其非结论性限定，并与两幅Codazzi画明确经过三组收藏的说法分开。其他Colonna画的证据缺口及Haskell不接受Vaes对其来源的确定性均单独记录。p.207注2仅登记引文定位，未从De Dominici页补造内容。页图将S0 OCR的`imturn`校读为`in turn`，只记S2、不改S0。

`chp8_p207_notes_migration.py` dry-run核对来源及段落哈希、原文行、候选ID、提及跨度、正文marker和外键后写入；审计为0 structural errors，`tests/test_audit_tables.py` 11 passed。p.207正文coverage转reviewed/complete；复合脚注段覆盖扩至L127–137，仍partial，下一范围L138–144（p.208注1–7）。全账本806段：309 complete、6 partial、52 excluded、439 queued；7,589候选、13,612提及、6,577条statement。仍有两条既存enrichment `source_ref`警告；本批通过结构校验不代表全书语义验收。


## 第八章印刷页208脚注1–7迁移（2026-10-01）

复合注释来源段chp-8:08_CHP-8_sec_i:l126-157的L138–144对照CHP-8.pdf物理第6页完成阅读和迁移，并回链p.208正文脚注标记。新增8条精确跨度提及和8条原书statement，不新增候选；复用De Dominici卷IV、Ruffo 1916年文章、Bartsch、British Museum、Bologna、Vaes 1925年文章及de Wael版画组候选。注3仅登记Haskell报告该组版画在British Museum，不表示已查馆藏目录；脚注引文页均未独立阅读。依据本书书目细化Ruffo文章候选为V. Ruffo 1916年刊文，并补齐p.208正文注2标记与脚注statement链接。页图校读rune→tutte、tn→There、ibid,→ibid.,只记S2；original_quote保留S0 OCR逐字内容。迁移后复核三处original_quote与S0，audit_tables.py --summary为0 errors，tests/test_audit_tables.py为11 passed。合并脚注段覆盖扩至L127–144，仍partial；全账本806段为310 complete、5 partial、52 excluded、439 queued，候选7,589、提及13,620、statement 6,585。仍有两条既存enrichment source_ref警告。下一范围为p.209注1（L145）；L146–148须与p.211视觉转录核对去重，p.214注4（L157）需按页图补录截断续文。


## 第八章印刷页209脚注1迁移（2026-10-01）

复合注释来源段chp-8:08_CHP-8_sec_i:l126-157的L145对照CHP-8.pdf物理第7页迁入。Haskell的第一条指引将p.209–214的Don Antonio Ruffo段落整体指向V. Ruffo 1916年文章；复用archive候选cand-6454，并将人物候选cand-3474从缩写V. Ruffo解析为Vincenzo Ruffo，依据印本文字及本书书目，且与作为传记主题的Don Antonio Ruffo cand-2297区分。第二条指引将Ruffo与Rembrandt关系指向S. Slive《Rembrandt and his critics 1630-1730》（The Hague, 1953）pp.59 ff.；新建作者cand-7599和archive cand-7600，不扩写作者名，也未独立查阅被引页。新增4条精确跨度提及、2条citation statement；第一条回链至p.209–214的115条正文statement，第二条仅回链至8条含Rembrandt候选的p.209–210 statement。按CHP-8.pdf物理第7页校正S0的Vincenzo Russo→Vincenzo Ruffo、Russo’s→Ruffo’s、Slivc→Slive；S0和original_quote保持原样，校读记入S2 qualifiers。p.209正文coverage转complete，复合注释coverage扩至L127–145并仍partial。audit_tables.py --summary为0 errors；全账本806段为311 complete、4 partial、52 excluded、439 queued，候选7,591、提及13,624、statement 6,587；仍有两条既存enrichment source_ref警告。tests/test_audit_tables.py为11 passed，git diff --check退出码0（仅有既存LF/CRLF转换提示）。恢复备份见表文件后缀.bak-s2-chp8-p209-note-20261001。下一范围为L146–148（p.211注1–3），须与既有视觉转录核对去重；随后L149–157，其中p.214注4需依物理页12补足OCR截断。


## 第八章p.211注释重叠核对（2026-10-01）

合并脚注段L146–148与派生视觉转录段chp-8:08_CHP-8_sec_i_notes_p211_visual-transcription:l1-4逐项对照CHP-8.pdf物理第9页。注1拆在视觉转录L1–2、注2为L3、注3为L4；此前视觉转录段已完成语义处理并包含22条mention、8条statement，故将合并段coverage扩至L127–148而不新建重复提及或断言。页图还显示注1引Gualandi卷II的印本页码为pp.115–28；分节OCR和既有视觉转录均误记pp.113–28。S0与已保存视觉转录文件均保留原文，在现有主statement的S2 qualifiers中记录两处文本校正、按印本更新citation至pp.115–128，并更正cand-7500、cand-7501及对应mention说明。另为分节OCR L148的注号8→印本3、i960→1960增加校读记录。dry-run确认已有覆盖、22条提及及8条statement，无重复行；写入后audit_tables.py --summary为0 errors，tests/test_audit_tables.py为11 passed。计数不变：806段、311 complete、4 partial、52 excluded、439 queued；候选7,591、提及13,624、statement 6,587。下一范围L149–157（p.212–214注释）；p.214注4须按物理页12补录OCR截断内容。

## 第八章p.212–214正文脚注与视觉补录迁移（2026-10-01）

对照`CHP-8.pdf`物理页10–12，完成p.212正文脚注1–5、p.213脚注1、p.214脚注1–4，以及合并OCR段`chp-8:08_CHP-8_sec_i:l126-157`的L149–157。新建派生转录`08_CHP-8_sec_i_notes_p214_visual-transcription.md`，补出S0遗漏的p.214注2并续完在“Nos.”处截断的注4；同时以印本校核注1–4。S0原OCR与PDF均保持不变。L146–148继续复用已完成的p.211视觉转录，不重复建立提及和statement。

迁入26个候选（cand-7601–cand-7626）、73条精确提及和28条statement。脚注引用与历史断言分开；Richa、Longhi、Bilivert、未识名画作组、Mediceo档案信件、Giovanelli家族、Monaco版画、Valéry所引Palazzo Contarini画作组等均按书内表述记录。未识明的书目作者、匿名通信人、具体画作、宫殿身份和收藏者分配保持开放；Del Rosso、Durazzo及Venice收藏语境未合并；所有外部引文页仅作Haskell的引文定位，没有写成独立核实。

初次dry-run发现两处提及跨度并非原文表面文本（Ciro Ferri作品组的联合短语、Valéry著作的页码锚点）及一条将同一“Mattia Loret”表面重复映射为作者与作品的提及；据S0与书目语境修正为逐字锚定的联合作品短语与“I, p. 342”，并删除重复作者/作品mention。随后source hash、段落范围、提及跨度、statement原文、外键、footnote marker及已有ID预检全部通过后写入；四份表保留恢复备份。复核`audit_tables.py --summary`为0 structural errors；S2 coverage为807段：316 complete、52有理由排除、439 queued、0 partial；7,617候选、13,697提及、6,615 statement。审计测试11项通过，`git diff --check`无空白错误（Git仅提示既存LF/CRLF行尾转换）。尚有两条既存enrichment `source_ref`警告；全书S2仍未完成。下一源序段为`chp-8:08_CHP-8_sec_ii:l1-1`。

## 第八章第二节引言（印刷页214）迁移（2026-10-01）

核对`08_CHP-8_sec_ii.md`与`CHP-8.pdf`物理第12页：L1为生成的分节文件标签，按非原书内容排除；L3–6是p.214新节正文；L7是前一分节S0漏录的p.214注2，L8–9重复注4尾段，均复用p.214视觉转录中的记录，不重复建立提及或statement。新增19条精确提及、6条statement；未新增候选。正文对Rome与地方收藏作比较，保留“all except”“in most cases”“usually”“almost exclusively”“some”“might have found”等范围和模态；“Crespi”复用页码包含214的索引候选cand-0871，城市和画家复用现有候选。页图确认S0 `Don Antonio Russo`应为`Don Antonio Ruffo`；更正写在S2限定中，原OCR引句不改。

L6末尾“Indeed, the most striking”续至p.215 L12，故`chp-8:08_CHP-8_sec_ii:l3-9`目前为reviewed/partial，覆盖L3–6；p.215闭合后再更新完整覆盖。L11–19是下一规范段；其含页码导航、正文和后置脚注标记，脚注全文在同节末端，迁移正文时应先排除导航标记并为脚注1–2保留回链。


## 第八章印刷页215–216语义处理与p.215注1–2溯源（2026-10-01）

### p.214引言句闭合与p.215概述

`chp-8:08_CHP-8_sec_ii:l3-9`仍只覆盖S0正文L3–6；L6的Indeed, the most striking是下一句开头，不属于“旅人或会在地方城市见到画作”的前句。已从前句original_quote中确认此边界，并在新statement `st-chp8-p215-provincial-collections-neglect-roman-painting`与p.215 L12分别处理完整后一判断；p.214段因此转complete。

p.215 L12按Haskell的论证次序分为数项书内陈述：地方收藏的显著特征是疏离Roman painting；classicising doctrines/institutions据Haskell说压制或排斥许多赴罗马的画家，但在偏远城市缺席，促成不同的评价标准；地方收藏“probably not many”，但他认为实际数量应多于已记录少数；至少一例被判断为高度有影响力；收藏发展史在Haskell论述中展示一种重要但特殊的赞助机制，涉及其“demolition of Roman values”命题。此段是作者概述/评价，不把“Roman values”改写为独立可证事件，也不把估数变成数量事实。p.214末句的句首片语和p.215续文仍可从两个规范段定位。

### Santa Maria Maggiore建筑和内装层次

p.215 L13–15称Bergamo的Santa Maria Maggiore自1137年开始施工、历经数世纪间歇推进；1355年Giovanni da Campione建Gothic portico（面对Palazzo della Ragione、由一对石狮支撑），数年后另建南入口。随后加入Renaissance部分；campanile于1425年完工，15世纪末增建Bramantesque sacristy。Haskell称内部改动更大：仍存Gothic frescoes痕迹；16世纪中叶起整体装饰改变；地方与Venetian artists的祭坛画开始出现；Ricchini于1612年规划dome，内侧铺有厚重stucco装饰；1614年Giampaolo Cavagna与两名未具名地方画家完成天使和先知壁画。把教堂（place）、campanile/sacristy（place）、portico/南入口/石狮及壁画/祭坛画/穹顶和灰泥装饰（works）分开；后续S3可重审具体身份和建筑边界。两名合作画家、壁画单幅标题和祭坛画身份均未造名。

### 1653计划及1654–1659委托

p.215 L16–19说明Haskell认为至17世纪中期内装呈现不同时期未完饰层互相竞争的混杂景象。1653年Consiglio del Consorzio（原文称教堂管理者）决定开始大规模装饰，主要为central crossing提供画作，另任命无名committee订购油画。Haskell叙述：委员会认为当地已无达到其要求水准的Bergamasque artist，因此要找外地人；Bergamo自1430年受Venice统治、距Milan约30英里，地方艺术受两地影响，委员会自然转向这两个关联中心。相对失败引发意大利多地谈判，p.216 L22续称其结果没有真正杰作且有价值的画很少，但给历史学家留下小城赞助人所遇困难的生动材料。政治统治的Venice与两地文化参照中的Venice city分开；距离、价值判断、效果与“great value”均作Haskell报告或评价。

p.216 L23–35按句记录委托变化：首选瑞士画家Cristoforo Storer（Ercole Proccaccini的学生，原文如此拼写；已用索引Procaccini候选，不能据此做外部身份核验），且其先前与Bergamo重要家族有密切接触。1654年2月受托为南耳堂拱顶和lunettes十三幅预定画作之一绘《The Levites》；Haskell说画最终完成，但Storer拖延，1655年4月委员会考虑用较快壁画替换原计划；数月后派两名成员到一名未具名地方贵族乡间住宅察看另一位未具名艺术家的壁画，作适任评估。1656年恢复原方案，委托当时服务Mantua侯爵的那不勒斯画家Pietro Magni先试作一幅，并以是否满意为后续整体委托的条件；Haskell称其显然未能通过。1657年Cremonese画家Ottavio Cocchi主动提议画一幅，获准后另被要求加画四幅；“比较次要艺术家”一语保留为Haskell判断。

p.216 L27–29记委员会曾一致选择Guercino承接三幅大门上画布中的一幅，派信使往Bologna；原定subject先为The Story of Esther，数月后改为Marriage at Cana；作者只说Guercino当时委托繁重、这件事似乎未能引起兴趣，不能说作品已创作或正式被拒。新candidate作为同一项未完成提案，和p.204注2的另一幅Marriage at Cana区分。Guercino尝试失败后，委员会转托Padre Massimo绘《Massacre of the Innocents》置于南耳堂右墙；他是Brusasorci的Capuchin pupil，曾在Veneto绘祭坛画。Haskell把此画批为对Paolo Veronese的有力但再造式变体；管理者很满意，曾以高额施舍请求Capuchins临时放人让Massimo在Bergamo继续作画，但未成。随后来自Milan及周边的未具名艺术家受托绘《The Killing of Sisera》《The Sacrifice of Isaac》《Jacob’s Ladder》《The Murder of Cain》，Haskell说第一阶段到1659年完成。L35开启北耳堂拱顶的下一阶段，仅记录十三幅这一未完成句首；p.217 L70将续接。候选分别指向可辨绘画、试作、Cocchi五幅未具名画组与未完成Guercino提案，不把题材自动识别为既有同名作品；具名历史中的委托/完成/失败仍是原书statement，不写入relations.csv。

### 脚注、校勘和迁移证据

物理p.215脚注1“Pesenti”据本书书目对应P. Pesenti, La basilica di Santa Maria Maggiore in Bergamo（1938）；正文只给姓氏且未给页码，被引书未独立阅读。注2称除另有说明外本节档案文件主要取自Angelo Pinetti 1916年文章，解释为Haskell本人、虽紧随Pinetti；本书书目补全文章题名La decorazione pittorica seicentesca di S. Maria Maggiore、刊物和pp.113–142，未独立阅读该文。另照录作者感谢Dora Coggiola及Biblioteca Cívica, Bergamo，未推断其职位或把该馆名扩成其他机构。该全局来源说明按原文的here和unless specially indicated限定在本地文件材料，不当作外部核验。notes复合段目前只覆盖L373–374；L375–461尚未逐条审阅。

`CHP-8.pdf`物理第13页核定L12 `growup`→`grow up`、L14 `Bcrgamasque`→`Bergamasque`；第14页核定`die country house`→`the country house`、`cominittee`→`committee`、`tó`→`to`、`promise-of`→`promise of`、`facob’s Ladder`→`Jacob’s Ladder`及Guercino句末OCR残留`- .`。所有更正仅在statement qualifiers/process中，S0和PDF未改。迁移脚本为`chp8_p215_216_migration.py`；默认dry-run核验后才apply，应用前保存四表恢复副本。p.215页文本段转complete，p.216正文L22–35因L35续句保留partial。


## 第八章Plate 33–36图版页语义迁移（2026-10-01）

覆盖账本按规范来源顺序显示，p.216正文之后、p.217正文之前尚有四个队列段：`l37-39`、`l41-43`、`l45-46`与`l48-67`。逐页对照`CHP-8.pdf`物理页15–18，分别为Plate 33、34、35和旋转的Plate 36；这些图版页虽在扫描顺序中插入p.216与p.217之间，仍是全书S2来源，不能因图版目录已有相同文字而整段跳过。

- Plate 33（物理页15）：图像题注为`a. Solimena: Dido and Aeneas`及`b. The gallery of the Palazzo Buonaccorsi, Macerata`。分节OCR把Solimena误作`Soumena`，只在S2限定记录`Soumena`→`Solimena`。复用书前图版目录的作品、Solimena、Dido、Aeneas、Gallery of Palazzo Buonaccorsi、Palazzo Buonaccorsi和Macerata候选；题注本身没有“formerly”，因此未把图版目录中的旧藏信息转写为此页断言。
- Plate 34（物理页16）：页面组题“FOREIGN MASTERPIECES IN ITALIAN SEVENTEENTH-CENTURY COLLECTIONS (see Plates 34 and 35)”作为编辑导航，不推导研究主题或层级；图注`Velasquez: Juan de Pareja`记录作品、作者和肖像对象，未将仅见于图版目录的Metropolitan Museum/New York信息复制到物理页题注。
- Plate 35（物理页17）：`a. Rembrandt: Aristotle contemplating the Bust of Homer`在S0可辨，记录作者、作品、Aristotle和Homer；S0页标`[Page 3]`在S2校为Plate 35。`b. Rubens: The Feast of Herod`的物理页图注在规范分节OCR中漏失，因此新建并登记派生视觉转录，只补这条图注，不改写PDF、规范OCR或整章对照。
- Plate 36（物理页18）：图像在PDF中旋转，规范OCR L48–67为逆序乱码；保留原OCR并以有理由排除记录其不可用状态。派生视觉转录恢复组题`GRAND PRINCE FERDINAND AND HIS PATRONAGE (see Plates 36–40)`以及`a. Francesco Petrucci: Grand Prince Ferdinand`、`b. G. M. Crespi: Girl at her toilet`。组题仅作编辑导航，不生成patronage关系。图版目录把Petrucci作品题名写作“Grand Prince Ferdinand of Tuscany”，物理页实际省略“of Tuscany”；quote保持物理页原文，身份仍复用目录候选供S3整体对齐。

共复用已有图版目录候选，新增22条精确跨度mention和16条`origin=book` statement，无新增候选；所有image-page claims均有各自图版标签、物理页码和图版目录行交叉定位，不据共现生成正式关系，也不从目录说明扩入图像页未载的藏所事实。新增派生资产`08_CHP-8_sec_ii_plates_visual-transcription.md`及来源登记已完成。机器迁移由`chp8_plates33_36_migration.py`控制，默认dry-run检查来源hash、段落范围、精确mention跨度、statement引句、候选外键和覆盖完整性；写入时保存恢复副本。

迁移后覆盖账本811段：325 complete、2 partial、54有理由排除、430 queued；候选7,652、提及13,813、statement 6,667。`audit_tables.py --summary`：errors=[]；仅保留两条既存enrichment `source_ref`告警、430段队列和两条reviewed/partial提醒。下一源段为`chp-8:08_CHP-8_sec_ii:l69-76`（p.217正文），先闭合p.216 L35的thirteen句。

## 第八章印刷页217–218语义处理（2026-10-01）

对照`CHP-8.pdf`物理页19–20迁移p.217正文L70–76、p.218正文L79–84，以及复合脚注段L375–376。p.217 L70闭合p.216 L35关于北耳堂下一阶段数量与位置的跨页句；p.217末句关于Ferri不能离开Florence和寄送尺寸/题材的请求续至p.218 L79；p.218末页句止于`richly`并续至p.219，故p.217、p.218 coverage均为reviewed/partial。

p.217记录北耳堂13幅、内墙1幅及主北/南门上2幅的计划；委员会转向Venice后于1660年与Pietro Liberi签约承绘16幅、约3,800 ducats并预付500。七个月后首幅《The Flood》抵达Bergamo，委员会要求重绘并暂停其他画作和付款；Liberi重绘后作品置于南门上。第二幅《The Last Judgement》仅送草图，委员会认为各方面均不足并取消合同。Haskell明言原因不可确知，并把Liberi的情色裸像可能冒犯地方趣味作为推测；保持“more likely / most probable”限定，不把推测写成委员会事实。委员会随后选Ciro Ferri接替；“Pietro da Cortona最忠实的追随者”保留为Haskell的风格描述，不升级为师承关系。

p.218记录Ferri延迟后于1665年9月到Bergamo、12月签订16幅油画与湿壁画合同；私信称其高兴但壁画位置偏小，并把门上大画的主题定为《Crossing of the Red Sea》。Haskell报告其两年半工期估计、1666年4幅加6幅壁画进度、1667年6月十三个壁画隔间和一幅大油画完成、第二幅尚待完成；“T ana working day and night”按物理页20校读为“I am working day and night”，S0不改。1667年9月委员会质疑侧门画作并征询意见，Ferri离开时合同未完。其后3幅待画、Zanchi受聘绘《Moses striking the Rock》，合同条件、Venice作画、四个月完成、接受及825 ducats均逐项登记；不把两幅未名门画补成具名作品，也不推断Ferri两幅油画中哪幅对应《Crossing of the Red Sea》。

两条注1已按页图回链：p.217 n.1列Bottari II pp.47–56及III pp.352–4；p.218 n.1列III pp.355–6。页图分别校正OCR `H`→`II`、`HI`→`III`，以及p.218正文脚注标记`RockJ`→注1；引用页及书信未独立查阅。新增16个候选（cand-7662–cand-7677）、60条精确跨度提及和19条statement；恢复备份为四表`.bak-s2-chp8-p217-218-20261001`。`audit_tables.py --summary` errors=[]，候选7,668、提及13,873、statement 6,686；811段中326 complete、3 partial、54有理由排除、428 queued。审计测试通过。下一正文段`chp-8:08_CHP-8_sec_ii:l86-98`（p.219）；注释复合段仍有L377–461未处理。



## 第八章印刷页219语义处理（2026-10-01）

对照CHP-8.pdf物理页21逐行处理规范段chp-8:08_CHP-8_sec_ii:l86-98及同一脚注复合段L377–378。p.219 L87补完Zanchi受纳画作的“richly coloured”句，关闭p.218跨页statement；p.218的续接目标先前误指不存在的l87-95规范段，现改为真实段l86-98。另关闭p.217 Ferri邀请句在p.218 L79的续接。p.219 L98“Perhaps Cignani would”仍未完，链接到p.220 L101；因此p.217、p.218转complete，p.219保持partial。脚注复合段覆盖扩至L373–378，后续L379–461未读，仍为partial。

正文迁入14个候选（cand-7678–cand-7691）、57条精确跨度提及和19条body statement，另有3条脚注statement。1677年《The Sacrifice of Noah》竞争单列为Santa Maria Maggiore画作和竞赛事件；记录Ferri未名失败尝试、Colleoni chapel门址、三位参赛者、Cervelli获胜、到Bergamo改画及370 ducats。该作不与Poussin的同题画合并。Pietro Negri在Scuola di San Rocco为1630年瘟疫止息所作的无名画及瘟疫事件分别建候选；Cavaliere Perugino与King of Savoy按本页称号保留为身份未决对象，分别不并入Pietro Perugino cand-1883及早先King of Savoy cand-3586。Scuola使用既有索引候选，Turin、Milan、Venice、Bergamo沿用现存地点候选，缺失的Como候选补录。

将p.219“third of the large oil paintings—The Crossing of the Red Sea”承接到p.218已建Ferri计划画作cand-7668，并把其说明从错误填写的exclude_reason迁回detail；按Haskell叙述，1682年题材交Giordano，另记他当时在Naples、画面描述、100 scudi礼金加700 ducats承诺，以及未能接下教堂其余装饰。脚注1记载一篇未名Bergomum 1947年文章报告画面实为Hymn of Liberation after the Crossing；此项保留为未核转引，不替代正文题材，也不声称读过文章。

中央中殿的14幅需求另建工作组和place，与先前耳堂/门区16幅计划cand-7663区分。逐项记录1681年Tencala接洽未果、1682年Ceresa的modello与Haskell对“very beautiful and precious”措辞的解释、资金承压；Cignani的名望仍带probably限定，保留其报价/协商失败。Giordano被报先索6,000、后减至5,000 ducats并要求本人、助手及仆人的食宿；签约后被报未履行。十幅湿壁画与四幅油画、速度声誉、拖延回信、意大利与欧洲宫廷成功成为委托障碍、条件后来转硬均保留原书归述。新建的Giordano合同仅是Haskell报告的archive候选；Tassi I, p.265按脚注定位建候选，作品身份与引文页均未核。

页图校读仅记在S2 qualifiers，S0不改：protege→protégé、Bcrgamasque→Bergamasque、setidi→scudi、tnodello→modello、OCR多出的“should”前引号删除、Giordano’s.success→Giordano’s success。p.219 n.1连到Giordano画作与subject statements；n.2连到10幅湿壁画/4幅油画协商及签约statement。两条脚注均仅作为原书引证/转述链，不作外部核实。

控制迁移脚本为chp8_p219_migration.py，默认dry-run；应用前保存四表备份，候选/提及/statement ID、源文件hash、精确span、原文引句、外键及续句状态均经预检。应用后全账本811段：328 reviewed/complete、2 reviewed/partial、54有理由排除、427 queued；候选7,682、提及13,930、原书statement 6,708。audit_tables.py --summary errors=[]；tests/test_audit_tables.py 11项通过；git diff --check仅报告工作树LF/CRLF转换提示。仍有既存enr-06678与enr-06937 source_ref警告，S2未完成。下一段按源序为chp-8:08_CHP-8_sec_ii:l100-110（p.220正文）；其后继续复合脚注L379–461。

## 第八章印刷页220正文与注1（2026-10-01）

对照CHP-8.pdf物理页22处理正文段chp-8:08_CHP-8_sec_ii:l100-110及后置脚注复合段L379。p.220 L101“prove more satisfactory after all”闭合p.219关于Cignani可能接手的未完句，故p.219转reviewed/complete。p.220末句称Melanconici的试画很快到达，但“and met with approval”续至p.221 L113，保留为open continuation，p.220为reviewed/partial。

新增2个候选（cand-7692–cand-7693）、34条精确提及、11条正文statement和1条脚注citation statement。分别记录Cignani于Forlì Cathedral绘制穹顶并意图与Correggio在Parma的穹顶作品竞争；Haskell转述Cignani 1692年书信中对画幅、仰视尺度及透视条件的异议；Ludovico David对十四幅委托的工期/费用报价、对自费且不满意不付的安排之反对、公开比较画作及由Florence/Bologna/Venice未名画家行会评选的反提案；委员会改询Marcantonio Franceschini及其降价过晚；Niccolò Melanconici自费试画Abraham。提议、实施与接受分开，行会仅建一个集合候选并明示其指三个地方性机构，不推断正式名称或提议已执行。匿名的David同事、潜在竞争者和方案中未名画家未补造身份。

脚注1为“Bottari, III, pp. 361–9”，脚注OCR误作“Bonari”；页图校读只记于S2 qualifier，S0未改。复用Bottari III的既有书目候选cand-5461。该页码仅作Haskell引文定位，未独立核读。

控制迁移脚本chp8_p220_migration.py默认dry-run，核对源文件hash、分段范围、候选序号和自然键、mention精确跨度、statement行锚点/引句/候选外键、p.219续句及coverage。应用前保存四表恢复备份`.bak-s2-chp8-p220-20261001`。首次写入后审计发现p.219/p.220 reviewed coverage的source_line_ranges为空；按审计错误补为L87–98与L101–110后复审通过。`audit_tables.py --summary`最终errors=[]；`tests/test_audit_tables.py`通过；S2总账811段为329 complete、2 partial、54有理由排除、426 queued；候选7,684、提及13,964、statement 6,720。既存两条enrichment source_ref警告未改变。下一源段为chp-8:08_CHP-8_sec_ii:l112-124（p.221正文）；后置脚注L380–461仍待按书序处理。


## 第八章印刷页221正文与注1–2（2026-10-01）

对照CHP-8.pdf物理第23页处理规范段`chp-8:08_CHP-8_sec_ii:l112-124`及后置脚注复合段L380–381。p.221 L113闭合p.220 Melanconici试画“很快到达”的续句，p.220 coverage转reviewed/complete；p.221末句关于Ferrerio所作Vigilance雕像续至p.222 L127，因此p.221保持reviewed/partial。

新增10个候选（cand-7694–cand-7703）、52条精确span提及及16条statement。记录Santa Maria Maggiore装饰截至1695年完成、委员会14幅画委托、Melanconici油画/壁画工作、Ruffo家庭来源与履历、教会职务/教廷任命、Ferrara任职和画廊、Cibo palace及Rome居住、Tommaso Mattei所建Ferrara Archbishop’s Palace，以及未名Cathedral和Ferrerio雕像。Haskell的评价、日期和转述层级均保留；“same great southern family”不扩展成具体亲属关系；Cibo卖方不实名，未名Cathedral不补正式名称。Ruffo的任命、居所、死亡和作品委托保留为书内报告，不提前写成正式关系。

注1转录S. Paolo d’Argan雇佣跨城画家的报告，并连接Angelo Pinetti 1920文章；文章题名依本书书目识别，未独立阅读。注2连接Moroni卷69页215–216；书目可识别辞典，但引文页未核读。注释事实及引文定位分开保存。页图校读Russo→Ruffo、bom→born、`1710'by`→`1710 by`、`the' piano`→`the piano`，S0来源文件和PDF均未改。

迁移脚本`chp8_p221_migration.py`先dry-run核对来源hash、候选序号/自然键、提及跨度、statement引句和外键，应用前保存四表备份`.bak-s2-chp8-p221-20261001`。写后机械审计发现注释复合段中Pinetti作者跨度与作者-年份引文相交；现将作者surname作为作者-年份全span的严格嵌套mention，并保存`mentions.csv.bak-s2-p221-mention-overlap-fix-20261001`恢复副本。最终`audit_tables.py --summary` errors=[]；`tests/test_audit_tables.py`通过（11 passed）。总账811段：330 complete、2 partial、54有理由排除、425 queued；候选7,694、提及14,016、statement 6,736。尚有2条既存enrichment `source_ref`警告。注释复合段覆盖至L381，下一源序正文段为p.222 `chp-8:08_CHP-8_sec_ii:l126-138`。


## 第八章印刷页222正文与注1–5（2026-10-01）

对照CHP-8.pdf物理第24页处理规范段`chp-8:08_CHP-8_sec_ii:l126-138`及后置脚注复合段L382–385。p.222 L127闭合p.221关于Ferrerio雕像的句子，p.221 coverage转reviewed/complete；p.222关于Ruffo喜爱Creti的句尾未完，连接至p.223 L140，故p.222保持reviewed/partial。脚注4正文嵌入分节OCR L136–138，其余n.1–3、5在复合注释段。

新增18个候选（cand-7704–cand-7721）、87条精确span提及及25条statement。记录Ferrerio师承Mazza、阶梯灰泥装饰与六位教宗肖像、Bigari的天花板寓意壁画、Ruffo的绘画收藏和Breval的藏画评价、Velasquez《Juan de Pareja肖像》及1704年罗马展览、Crespi四幅收藏及两幅具名委托、Creti风格比较。Carracci群体、Bigari壁画、四幅Castiglione组画、Masanella [sic]原作、Crespi四作组等不扩张成无据题名或作者确认；The Finding of Moses与索引cand-0879保持分立供S3对齐。Ruffo参与设计与收藏保存为原书报告，未前置生成正式关系。

脚注1记录Haskell所引Collezione Antonelli MS. 610及其中关于Ruffo离开Ferrara、携画赴Rome的意大利文转引，手稿和引文未独立查阅。注2识别Agnelli 1734画廊图录；注3识别Breval 1738卷I；注4记载该Pareja画送展及Haskell所报Met藏所、Hamilton藏史；注5将两件Crespi作品与Museo di Palazzo Venezia及Zanotti、L. Crespi、Santangelo书目引文关联。所有引文页未独立核读，图录命中不作为其事实支持证明。

页图校读仅记于S2，不改S0：os→of，删`in`后的OCR引号，Clement XL→Clement XI，rctrospect→retrospect，Italianjmasters→Italian masters，Masanella [sir]→Masanella [sic]，Presenti→Presents，sound→found；L136 `11 Ritratto`→`Il Ritratto`、`Ri serv.re`→`fu serv.re`；L382 Calleria→Galleria、L383 Russo’s→Ruffo’s、L384 1738,1→1738, I、L385脚注标记6→5。另校正L128、130、131、133、134、135的Russo→Ruffo（L130出现两次）。

控制迁移脚本`chp8_p222_migration.py`默认dry-run，核对源资产/段落hash、自然键及候选序号、精确跨度、statement锚点/引句/候选外键、续句与coverage；应用前保存四表备份`.bak-s2-chp8-p222-20261001`。应用后`audit_tables.py --summary` errors=[]；`tests/test_audit_tables.py` 11项通过。全账本811段：331 complete、2 partial、54有理由排除、424 queued；候选7,712、提及14,103、statement 6,761。既存两条enrichment `source_ref`警告仍在。注释复合段覆盖L373–385；下一源序正文为p.223 `chp-8:08_CHP-8_sec_ii:l140-150`。

## 第八章印刷页223正文与注1–5（2026-10-01）

对照`CHP-8.pdf`物理第25页，逐行处理`chp-8:08_CHP-8_sec_ii:l140-150`，并将后置脚注复合段L386–388按印刷页回链。p.223 L141闭合p.222关于Ruffo喜爱Creti、每日长时间观看其作画的未完句；p.222转reviewed/complete。p.223 L148末尾对Buonaccorsi宫殿的“finest in this little hill town”比较句续至p.224 L152，故p.223保持reviewed/partial。后置脚注段覆盖扩至L373–388，仍partial；p.223注2与注5在正文段L149–150，复合段L386–388容纳注1、注3和注4。

新增25个候选（cand-7722–cand-7746）、79条精确提及及45条statement。记录Creti的Solomon题材藏画、Dance of Nymphs及被报告的Cavaliere dello speron d'oro荣衔；Ruffo委托Cignani、Franceschini（after 1720）、dal Sole和Gambarini的作品；Giordano送出的四幅画及《Hebrew Women singing after crossing the Red Sea》与其Santa Maria Maggiore工作的可能关联；Solimena的Nativity与Presentation；Salvi建造的S. Lorenzo in Damaso礼拜堂及Conca、Giaquinto装饰；Raimondo Buonaccorsi的履历、婚姻、子女、Macerata宫殿与有限书信背景。作品组不补造题名；Simone只按正文所给名字保留候选对齐；家族和“the Church”的指称不扩写成确定谱系或组织；Haskell对Roman artists的判断、性格描写及“may well”“must have”等推测保留原有语气。

注1–3定位Zanotti、L. Crespi、De Dominici、Moroni与Pascoli引文，并记录Ruffo委托Andrea Pozzo肖像的脚注报告；引用页未独立核读。注4是Haskell对Count Orlando Buonaccorsi、Dwight Miller和Silvio Ubaldi的致谢与资料来源说明；Memoria手稿和画廊照片未独立查阅。注5列三封信：Raimondo Buonaccorsi致Tiberio Cenci（1705-02-23），以及Alessandro Borgia致Raimondo（1737-09-13、1742-12-07），按印本录入Vat. Lat. 9041 c.39及Borg. Lat. 236 c.87、c.125；仅为Haskell的馆藏/引文定位，不是本次档案查验。

页图校读记录在S2、未改S0：L142 `Russo`→`Ruffo`；L145 `Cbnca`→`Conca`；L147 `Church?`→`Church.`；L149脚注号前OCR破折号删除；L150注号`s`→`5`、`oflittle`→`of little`，并补回Vat./Borg. Lat.馆藏号。迁移脚本`chp8_p223_migration.py`核验来源哈希、79条新mention精确跨度、45条statement锚点/引句、候选外键、前后续句和覆盖；应用前保存四表备份`.bak-s2-chp8-p223-20261001`。首次审计发现25个新增候选的source-ref须符合单行定位和`body-mention`来源值；已按schema逐行修复，修复前候选表恢复副本为`.bak-s2-chp8-p223-refrepair-20261001`。最终`audit_tables.py --summary` errors=[]；`tests/test_audit_tables.py` 11 passed；迁移脚本`py_compile`通过。全账本811段：332 complete、2 partial、54有理由排除、423 queued；候选7,737、提及14,182、statement 6,806。既存两条enrichment `source_ref`警告不变。下一正文段为`chp-8:08_CHP-8_sec_ii:l152-161`（p.224）；后置脚注下一待读L389。


## 第八章印刷页224正文及注1–4（2026-10-01）

对照`CHP-8.pdf`物理第26页迁入规范段`chp-8:08_CHP-8_sec_ii:l152-161`及复合脚注段L389–391。p.223关于Buonaccorsi宫殿的跨页句由L153闭合，原先“finest in this little hill town”中的地点由“States of the Church”补足；“an earlier one”按上下文作为未识别的早期宫殿/建筑处理，不误判为教堂。登记Contini为宫殿建筑师，Raimondo约在1707年开始装饰长廊；区分宫殿整体与长廊空间、穹顶壁画和独立画作。

本页记录长廊现存状态（“today”仅指Haskell写作时）、穹顶单幅壁画、窗户/采光/材料、画布尺寸与陈列范围、不同地区画家风格及《Aeneid》统一题材。Haskell关于装饰在意大利罕见、其价值来自图像统一与风格差异而非画作内在优点的判断作为作者评价保留。1707年Raimondo召集Rambaldi和Dardani绘《Apotheosis of Aeneas》；之后委托《Aeneid》单一情节画。Rome与Papal States分作城市和政治实体；Raimondo对罗马绘画兴趣有限的描述，与其只选一幅《Venus in the Forge of Vulcan》（“apparently”由Luigi Garzi绘制）及对Naples、Bologna、Venice的关注分开记录，没有把选择写成直接委托。

Solimena的《Dido welcoming Aeneas to the Royal Hunt》被Haskell称为组画杰作，且属于最早抵达的作品；保留“among the first”而不补具体日期。画中Juno、风暴、Cupid之箭、Aeneas与Dido均记为神话叙事的再现，未写成历史事件。p.224末句“greatest enthusiasm and”续至p.225 L164，故本段为reviewed/partial。

注1 Amico Ricci, II, p.436；注2 Zanotti, I, pp.396、418；注3 D. Miller, 1963、1964；注4 De Dominici, IV, p.428。注4还转述三幅其他Solimena画作、Raimondo于1714-07-06记录Dido画作抵达的家族档案信，以及一条以“Bologna (Plate 209)”为引文标识的复制品记录。引文页、信件、保管档案和复制品均未独立核读；“Bologna (Plate 209)”按身份未决的文献引用处理，不映射到正文中的Bologna城市；Scholz-Forni collection保留为类型待决对象。

按页图仅在S2记录OCR校读：L155 `fight`→`light`、`iconographie`→`iconographic`；L159引句`The dies ... Causa suit`→印本`Ille dies ... Causa fuit`；L389 `H`→`II`；L160 `L PP396`→`I, pp.396`；L390末尾OCR连字符删除。S0原文未改。受控迁移脚本校验源资产/段落哈希、候选号、提及跨度、语句原文和外键；应用前为四张表保存`.bak-s2-chp8-p224-20261001`副本。


## 第八章印刷页225正文及注1–9（2026-10-01）

对照`CHP-8.pdf`物理第27页处理正文段`chp-8:08_CHP-8_sec_ii:l163-177`及后置脚注段L392–398。p.224 Solimena画作引发兴趣的未完句由p.225 L164闭合；末段关于Raimondo可能属于启蒙时代赞助人的推测在L175中途结束，续至p.226 L180，故p.225保持reviewed/partial。n.1、n.4–9由脚注复合段承载，n.2–3位于正文OCR相应行；引文只作Haskell的定位/报告，未独立核读。

正文区分dal Sole闻讯后坚持前往Buonaccorsi宫殿观看Solimena《Dido》、其自作Andromache画布及Haskell据此提出的Rome文化交换中心判断。Gambarini、Franceschini、Lazzarini、Balestra的《Aeneid》题材画作组和Haskell对其笨拙、不够有说服力的评价分别记录；未具名的其他房间画作仅作为集合候选，并保留Haskell“更有趣”“现代”的评价，以及Raimondo“必定”理解其特质这一推断。Crespi四幅寓言画只以组候选记录，Leto turning the Shepherds into Frogs是Haskell所称的唯一存世作品；Gambarini的异教题材画作、两位画家的风格差异及古典/基督教题材转向风俗画的说法均保留为作者的艺术史判断。另记收藏记录稀少、Giaquinto被报告曾为Buonaccorsi工作但几乎无痕、藏画在家族成员间分散且无库存清单；没有由“未见记录”推断作品从未存在。

注释新增Franceschini《Mercury awaking Aeneas》、Libro dei Conti的1000里拉付款报告；Lazzarini为Buonaccorsi作的《The Death of Dido》《The Battle of Aeneas and Mezentius》及其他未名画作；Pascoli未刊Balestra生平中的未名《Aeneid》寓言画；Crespi的Leto画作被报藏于Bologna Pinacoteca Nazionale；Haskell亲访收藏后称未见可归Giaquinto之画，以及d'Orsi所限Giaquinto在Macerata的工作范围。来源定位和二手转述均未误作独立验证；D. Miller、d'Orsi书目身份留S3对齐。页图校读只记S2、未改S0：L164 `own. canvas`→`own canvas`；L171 `in-some`→`in some`；L175 `forthe`→`for the`；L176 `2D. Miller`→`2 D. Miller`；L177脚注号/Franceschini及`Libra`→`Libro`；L394 `Balcstra`→`Balestra`、`Use`→`life`及受损的Biblioteca字样；L395 `11`→`II`；L398受损的d'Orsi撇号。OCR中弯引号有损编码，相关提及只采用可精确匹配的原文子串。

受控脚本`chp8_p225_migration.py`默认dry-run，核验源资产及段落hash、候选编号/自然键、87条提及span、statement锚点/引文/候选外键、续句及coverage；应用前保存四表恢复副本`.bak-s2-chp8-p225-20261001`。dry-run通过后应用19个候选、87条提及和26条statement。`audit_tables.py --summary`为`errors=[]`；保留两条既存enrichment `source_ref`告警，新增421段queued和2段partial状态告警；`tests/test_audit_tables.py` 11项通过；`git diff --check`退出码0（仅提示工作树LF/CRLF转换）。全账本811段：334 complete、2 partial、54有理由排除、421 queued；候选7,774、提及14,328、statement 6,852。下一正文段为p.226 `chp-8:08_CHP-8_sec_ii:l179-188`，后置脚注下一范围L399–461。

## 第八章印刷页226正文及注1（2026-10-01）

对照`CHP-8.pdf`物理第28页处理正文段`chp-8:08_CHP-8_sec_ii:l179-188`与脚注复合段L399。L180闭合p.225关于Raimondo私人寓室的跨页比较。随后转入Stefano Conti：Haskell称其来自Lucca，藏画97幅且多为小尺寸；由于其出生地与地方艺术环境，藏画来源扩至Bologna、Venice。记录Crespi、Sebastiano Ricci、Canaletto等画家，Conti的1654年出生、父亲较其出生早约四分之一世纪进入Lucchese nobility、丝绸/布料贸易、婚姻和子嗣、1739年去世及85岁年龄。父亲姓名与准确准入年份、妻子和独子姓名均未补造。

独立区分Conti的藏画集合与其委托兴建的明亮画廊；本页只说本地建筑师、未提供姓名和建筑定位。记录其于1704年底旅行后开始收藏、随后约三年在两城有目的地购画、拒绝出售并在遗嘱中试图保持收藏整体。Haskell所述委托惯例包括价格上限、作品须为专为Conti创作的原作、题材选择自由但尺寸受限，以及每件作品须附精确题名与日期保证。以上均为书内陈述，不前置写入正式关系。Marchesini被任命为代理人，所述职责包含催促迟延者、定期向Conti报告、交付预付款、推荐新画家及提议修改资深画家的作品。将“定期写信”登记为沟通惯例，不推成现存信件；Cignani的“school”不擅自定作正式机构。Haskell对Marchesini才华有限却适任的评价保留为作者判断。

L188“按画中人物数计价”以open continuation保存，待p.227 L190续读后闭合。脚注复合段只迁入本页n.1：Haskell 1956作为该节综述来源，说明其载有Lucca馆藏手稿详细出处；出版物题名与版次未识别，未声称查阅该书或相关手稿。`cand-7790`为待识别出版物候选，作者复用已有Haskell候选。

页图核校仅记于S2，S0原文不改：L182 `lie managed`→`he managed`；L183 `Conti_was`→`Conti was`、`cloth,,`多余逗号、`siom`→`from`、`silled`→`filled`；L184 `originals`→`original`；L187 `siom`→`from`。受控迁移脚本`chp8_p226_migration.py`默认dry-run，核验来源资产及段落hash、候选编号/自然键、精确提及span、statement行锚点/引文/候选外键、续句和coverage；应用前保存四表恢复副本`.bak-s2-chp8-p226-20261001`。dry-run通过后写入13个候选、59条提及及19条statement，并关闭p.225开放续句。`audit_tables.py --summary` errors=[]；仍有两条既存enrichment `source_ref`警告，420段queued和2段partial状态告警；`tests/test_audit_tables.py` 11项通过；`git diff --check`退出码0（仅提示工作树LF/CRLF转换）。全账本811段：335 complete、2 partial、54有理由排除、420 queued；候选7,787、提及14,387、statement 6,871。下一正文段为p.227 `chp-8:08_CHP-8_sec_ii:l190-204`，后置脚注下一范围L400–461。
## 第八章印刷页227正文及注1–3（2026-10-01）

对照CHP-8.pdf物理第29页处理正文段chp-8:08_CHP-8_sec_ii:l190-204与脚注复合段L400–402。p.226关于按画中人物数计价的开放断言由p.227 L191闭合：Haskell称该做法有时造成问题，并转述Marcantonio Franceschini抱怨很难找到适合“两个人物与putti”的历史/寓言题材，希望由Conti本人选题。Franceschini提出的fanciful pastoral被接受，但不据此断言画作已完成。Felice Torelli提出的特洛伊题材画作后来到达，Conti再次询问画作内容，具体识别仍不确定。

记录威尼斯画家的题材判断及Lazzarini六幅旧约/新约作品；将“less imaginative”“impeccable morality”“academic”“correct drawing”“blond tonality”及对tenebrosi的对照保留为Haskell评价。艺术家名册明确是Angiolo Trevisani，不与索引中的Francesco Trevisani合并。记录Bombelli为Conti、其妻和儿子所作肖像；Franchi“被认为足以为三位女儿作画”保留为资格评价，不扩大成已完成委托。另记录Cassana七幅水果/动物画、未名风景画、Carlevarijs三幅威尼斯景观和Mazza的Diana/Endymion双胸像。

Conti近二十年只购买三幅作品，其中Christ in the Garden of Olives的Correggio归属保留引号；之后于1725年重启收藏，试图取得两幅额外Carlevarijs景观及Francesco Bassi的一幅风景画，不写成已经成交。L204关于Carlevarijs的评价续至p.228 L207，因此p.227为reviewed/partial。后置注1–2定位1705年2月17日、2月24日的Lucca Biblioteca Governativa MS.3299书信；注2不推定签署人。注3定位Da Canal pp.40、58、59，复用既有出版物候选；引文页与档案均未独立核读。

页图校读仅记S2，不改S0：L191 “curio so .”校为“curioso.”；L192 “Acliilles”校为“Achilles”；L193 “evenLazzarini”校为“even Lazzarini”；L195去除学术外观一词前的多余引号；L203去除1725前的OCR破折号。Chalchas及Antinorus按页图原样保留，不擅自校正。

受控脚本chp8_p227_migration.py默认dry-run，核验来源资产与段落哈希、26个候选自然键、71条提及跨度、13条statement锚点/引句/候选外键、跨页续句与coverage；应用前保存四表恢复副本.bak-s2-chp8-p227-20261001。应用后p.226转complete，p.227转partial，注释覆盖扩至L402。audit_tables.py --summary errors=[]；tests/test_audit_tables.py 11 passed；py_compile通过；git diff --check退出码0，仅有工作树LF/CRLF转换提示。全账本811段：336 complete、2 partial、54有理由排除、419 queued；候选7,813、提及14,458、statement 6,884。既存两条enrichment source_ref警告不变。下一正文段p.228 chp-8:08_CHP-8_sec_ii:l206-214，后置注释下一范围L403–461。
续句锚点复核：p.227来源段L190为页面标记，正文实际从L191开始。迁移后检查发现p.226开放statement的continued_to_source_line误记为190，已根据原始行将其修正为191，同时修正p.226 coverage note；修正前分别保存book-statements.jsonl与s2-coverage.csv副本，后缀为.bak-s2-p227-continuation-linkfix-20261001。重新运行audit_tables.py --summary仍为errors=[]，tests/test_audit_tables.py为11 passed。

## 第八章印刷页228正文及注1（2026-10-01）

对照`CHP-8.pdf`物理第30页迁入正文段`chp-8:08_CHP-8_sec_ii:l206-214`及后置注释复合段L403。p.227关于Carlevarijs作品的引述在L207续完；L206只是`[Page 228]`页码标记，跨页续句锚点和p.227 coverage说明均指向实际正文L207。脚注复合段扩至L403并保持partial，余下L404–461继续按印刷页和注号审查。

本页按语境区分Marchesini转述的Canale/Canaletto与Marco Ricci景观评价、Conti分两批委托Canaletto共四幅作品、Marco Ricci五幅遗址景观及Sebastiano插绘人物、Sebastiano拟作而未成的两幅Alexander题材历史画。记录Carriera为Emmanuela肖像画家及1728年Conti直接委托Crespi；后者题名从《The Infant Jupiter handed over by Cybele to the Corybantes to be fed》改为《The Finding of Moses》，保留Haskell关于降低关税动机的报告。p.228对照页图，OCR中的`Rosalba Garriera`校读为印本`Rosalba Carriera`，只记入S2。p.228 L214的Medici人物由下一页L217的Grand Prince Ferdinand语境确认；不把书内作者判断升级为外部事实。

新增6个候选（cand-7824–cand-7829）、47条精确提及和17条原书statement；注1记录Lucca Biblioteca Governativa MS.3299与Zanotti II p.62的引文定位，手稿和所引页未独立核读。页面与源序覆盖通过dry-run后应用，应用前四表恢复副本后缀`.bak-s2-chp8-p228-20261001`。dry-run发现两条相同的`Marchesini`提及跨度；页文中此处仅有一次姓名，已删除重复的候选mention，而非改写来源。续句closed、p.227与p.228转reviewed/complete，脚注段仅延至L403。`audit_tables.py --summary` errors=[]；定向审计测试11项通过，迁移脚本`py_compile`通过，`git diff --check`退出码0（仅有既存LF/CRLF转换提示）。全账本811段：338 complete、1 partial、54有理由排除、418 queued；候选7,819、提及14,505、statement 6,901。下一正文段为p.229 `chp-8:08_CHP-8_sec_ii:l216-225`，注释下一范围L404–461。


## 第八章印刷页229正文及注1–2（2026-10-01）

对照`CHP-8.pdf`物理第31页处理规范正文段`chp-8:08_CHP-8_sec_ii:l216-225`；该段包括正文L217–223及页底注2的OCR续文L224–225。后置注释复合段L404为本页注1。p.228 L214的“Medici”人物由本页L217明确为Grand Prince Ferdinand，回填上下文解析；p.229 L223“other members of the family were called upon to try where the Grand Prince”续至p.230 L228“had failed”，保留open statement，待下一段语义迁入后关闭。

逐句记录Haskell对Florence短期艺术复兴、Ferdinand赞助及17至18世纪趣味变化的判断；出生年份、父母、叔父Francesco Maria、兄弟Gian Gastone、教育者Viviani/Lorenzini/Redi、婚姻协商、Violante和1696年单身赴Venice等分别建断言。家庭心理、宫廷行为与品味陈述保留Haskell评价，不将未具名谈判对象、父母动机或未名当代引语补成确定事实。Galluzzi、Pieraccini、Giuseppe Conti和Harold Acton的书目身份依本书书目记录为四个archive候选；未把书目定位表述成已读或外部验证。候选cand-7830–cand-7837新增Marguerite d’Orléans、Violante of Bavaria、Montmartre、Portugal polity和四种书目；Portugal与Florence的宫廷候选保留后续身份/边界复核。

页图校读只进入S2、未改S0：L217 `sine arts`→`fine arts`；L219/L220 `fife`→`life`；L220 `surroundings,. a`去除OCR多余标点；L404 `Zanotti, n, p.50`中的卷号核为`II`。图像也确认页底注2标号为2，正文OCR注释L224–225据此回链；注1的Zanotti页与注2四种家族史文献均未独立核读。受控脚本`chp8_p229_migration.py`默认dry-run，核验来源与段落哈希、候选自然键、38条提及跨度、statement锚点/引句和外键；应用前四表备份后缀`.bak-s2-chp8-p229-20261001`。`audit_tables.py --summary` errors=[]；`tests/test_audit_tables.py` 11 passed；脚本`py_compile`通过。全账本811段：339 complete、1 partial、54有理由排除、417 queued；候选7,827、提及14,543、statement 6,922。下一正文段p.230 `chp-8:08_CHP-8_sec_ii:l227-236`，下一后置注释L405–461。


## 第八章印刷页230正文及注1–5（2026-10-01）

对照`CHP-8.pdf`物理第32页，处理正文规范段`chp-8:08_CHP-8_sec_ii:l227-236`及后置注释复合段L405–408；正文内注1、5分别位于L235、L236。p.229关于家族成员尝试确保继承人的句子由p.230 L228闭合；p.230关于威尼斯记忆及佛罗伦萨代理人记录的末句续至p.231 L239，故保留open continuation。

记录Ferdinand退居Poggio a Caiano与Pratolino、音乐和歌剧活动、Scarlatti、Pratolino剧场与Bibbiena成员、作家赞助和Redi版本资助、健康与1713年去世、Cosimo III仍在位四十三年，以及Ferdinand赴威尼斯的娱乐、礼物和回访意图。将“apparently”因果说法、Haskell的评价与比较、匿名当代引语及脚注所说Ombrosi“probably”身份保持限定；Regent不由类比擅自实名。Castellani、Nicolotti登记为类型待定的狂欢团体，不预设其组织属性。脚注登记Scarlatti书信系列、Fabbri/Puliti、Sgrilli、1714年Elogio与期刊卷、Maffei信件、Ombrosi可能著作和Archivio Mediceo定位；引文、手稿及档案均未独立核读。

页图校读只记入S2、不改S0：L230 `pubheation`→`publication`；L405 `Scarlattito`→`Scarlatti to`；L407 `XVH`→`XVII`、`$903`→`5905`、`su Serenissimo`→`fu Serenissimo`；L408 `Cran`→`Gran`。L236页图显示档案定位为`Filza 3050 D`，S0字串为`Filza 3050`，在限定中记录补出的D，不改来源转录。

受控脚本`chp8_p230_migration.py`默认dry-run，核验源资产与段落哈希、候选自然键、46条提及跨度、21条statement锚点/引句/外键、继承句关闭与coverage；dry-run通过后应用18个候选、46条提及和21条statement，应用前四表恢复副本后缀`.bak-s2-chp8-p230-20261001`。`python scripts/audit_tables.py --summary`返回`errors=[]`，总账811段：339 complete、2 partial、54排除、416 queued；候选7,845、提及14,589、statement 6,943。保留2条既存enrichment `source_ref`警告。`python -m pytest tests/test_audit_tables.py -q`为11 passed；`py_compile`通过；`git diff --check`退出码0（仅工作树LF/CRLF提示）。第八章候选表面启发式未在p.230正文段报告未覆盖跨度；该工具不代表召回率或语义验收。下一正文段为p.231 `chp-8:08_CHP-8_sec_ii:l238-249`，注释下一范围L409–461。

## 第八章印刷页231正文及注1–6（2026-10-01）

对照`CHP-8.pdf`物理第33页处理规范段`chp-8:08_CHP-8_sec_ii:l238-249`及后置注释L409–414。新增21个候选（cand-7856–cand-7876）、75条提及和20条statement。p.230 L236末句在p.231 L238–239闭合；本段末句在p.232 L252–253闭合。逐条区分Ferdinand对Gabbiani等画家的赞助与艺术家身份、实际作品、赠画/委托/模特等角色；保留Haskell的“loyalty”解释及评价语气，不将其推成正式关系。脚注仅登记来源定位和书内报告，未独立核读所引资料。扫描校读只记S2；原始OCR未改。受控脚本`chp8_p231_migration.py`写入前核验来源hash、候选自然键、精确提及span、statement锚点/外键和续句，备份四表后应用。应用后p.231转complete，p.232已有开放续句指针指向L252–253。`audit_tables.py --summary` errors=[]，`tests/test_audit_tables.py` 11 passed；全账本811段为340 complete、2 partial、54 excluded、415 queued；候选7,866、提及14,664、statement 6,963。

## 第八章印刷页232正文及注1–4（2026-10-01）

对照`CHP-8.pdf`物理第34页处理规范段`chp-8:08_CHP-8_sec_ii:l251-257`及后置注释L415–418。新增38个候选（cand-7877–cand-7914）、78条提及和25条statement；关闭p.231开放statement并将续句锚定至p.232 L252–253。候选提及覆盖艺术家、作品、赞助、宫廷职务和文献定位；身份含糊者保持本地候选，不凭相似拼写并入S1索引候选。页图校读按p.232扫描记录Niccolò、`1698.`及意大利语引句、脚注日期/年份修正；仅S2记校，不改S0。句末`modelli`由p.233 L272续接，故p.232正文保持partial；后置注释复合段覆盖L373–418、仍partial。受控迁移脚本`chp8_p232_migration.py`核验来源及段落hash、候选顺序/自然键、精确span、statement外键和续句；应用前保存恢复副本`.bak-s2-chp8-p232-reviewed-20261001`，后修复的两处正文span也保留了修订前副本。应用后`audit_tables.py --summary`显示811段覆盖齐全、errors=[]；341 complete、2 partial、54 excluded、414 queued；候选7,904、提及14,742、statement 6,988。审计测试11 passed，迁移脚本`py_compile`通过，`git diff --check`通过（仅CRLF提示）；两条既存enrichment source_ref警告未变。接下来按源序处理图版题注L259–269，随后p.233正文L271–279、脚注L419–461。

图版页复核：查看CHP-8.pdf物理第35–38页。Plate 37a/b题注在OCR中；c题注被扫描页下缘截断，目录已有完整条目。Plate 38扫描页显示OCR遗漏题头“Frescoes by Sebastiano Ricci”，应从PDF制作派生视觉转录。Plate 39只有图像和页号、无独立题注，完整作品题注已在图版目录处理。Plate 40a题注在OCR中，b题注被扫描页边缘截断，图版目录有完整条目；不得把目录内容写成图版页的直接转录。

## 第八章p.232 Plate 37–40题注迁入（2026-10-01）

对照`CHP-8.pdf`物理第35–38页处理规范OCR段`chp-8:08_CHP-8_sec_ii:l259-261`、`l263-266`、`l268-269`。Plate 37a/b登记画家一家与《波焦阿卡亚诺集市》题注；保留scan所示`(detail)`，不从图版目录导入地点。Plate 38 OCR只保留地点行与a/b题名，扫描页可辨题头“FRESCOES BY SEBASTIANO RICCI”，据此追加派生视觉转录段；复用既有图版目录候选，迁入Rape of Europa、Pan and Syrinx的标题指涉及Pitti Palace/Florence位置。Plate 40a迁入Gabbiani《A group of musicians》的印刷署名。Plate 37c和Plate 40b题注被扫描页边缘截断；Plate 39只有图像和页号，无独立题注，不将图版目录信息伪装成图版页直接题注。

先新增`08_CHP-8_sec_ii_plates_p232_visual-transcription.md`并追加来源登记；`build_source_segments.py`dry-run显示71个分节资产、812段、0问题，备份旧`segments.jsonl`后由构建器登记新段。受控脚本`chp8_p232_plates_migration.py`默认dry-run，核验四个目标段与图版目录资产hash、候选外键、14条提及精确span、10条statement原文锚点及四段coverage；dry-run通过后应用，新增0候选、14提及、10条caption statement。应用前为mentions、book-statements和s2-coverage保存独立恢复副本。

应用后`audit_tables.py --summary`：812段，345 complete、2 partial、54 excluded、411 queued；候选7,904、提及14,756、statement 6,998；`s2_missing=[]`、`errors=[]`。两条既存enrichment source_ref警告仍在；两段partial分别为p.232正文跨页句与后置脚注复合段。`tests/test_audit_tables.py` 11 passed；`build_source_segments.py`重跑预览仍为812段、0问题；迁移脚本`py_compile`通过；`git diff --check`退出码0（显示的仅是LF/CRLF提示）。下一步处理p.233 `l271-279`，关闭p.232末句，再继续后置脚注L419–461。


## 第八章印刷页233正文及注1–5（2026-10-01）

对照CHP-8.pdf物理第39页，处理正文段chp-8:08_CHP-8_sec_ii:l271-279及后置脚注复合段L419–423。p.232 L257关于Ferdinand坚持查看modelli的开放statement由p.233 L272闭合；p.232正文转complete。p.233末句在L279开始，续至p.234 L282，故p.233仍为reviewed/partial。

本页区分Ferdinand检查模型稿的审美及内容准确性、其观看画家工作并讨论颜色和画布厚度的习惯；记录他长期雇用Gabbiani、对Bassi的忠诚可能性、以Gabbiani表达其威尼斯绘画抱负的Haskell解释及1699年赴威尼斯改进色彩的报告。Sacconi的父亲未具名；经济支持、在Cassana指导下工作、三项绘画指令、色彩进步、Corpus Domini展出及Haskell对结果的评价均分别保留。Loth为Ferdinand绘画的时间从1691年至其约七年后去世；“初访时相识”保留must have推断，第二次威尼斯之行的日期未补。Ferdinand曾努力取得Loth擅长的半身人物画，但不据此声称已购得；p.234关于Giannantonio Fumiani的相邻叙述用于注明“响应压力的艺术家”与Fumiani的语境联系，身份未在p.233单独写明。

注1报告Trevisani将《Anthony and Cleopatra之宴》的modello送给Ferdinand，成画为Cardinal Fabrizio Spada-Varallo所作；Pascoli手稿按已有MS 1383候选复用，作者只记录姓氏。注2记录Archivio Mediceo, Guardaroba 1055及Dandini、Foggini、Franchi、Botti、Pinacci、Panfi、Monari和Abate Orazio Martini。注3、4定位Fogolari (1937) Letter 83及Letters 6、12、28、60、71。注5记录Loth 1691年信件、拟作Titian《St Peter Martyr》摹本、1693年自画像、Pitti所藏《Death of Abel》及1716年清单中的六幅画，并保留Fogolari Letters 22/77、Ewald 1965和p.239 n.5为二手书目定位；所引档案、书信、目录均未独立核读。注2–5各自与正文脚注标号逐条回链。

页图校读只记入S2，S0 OCR未改：L275 artistic'ambitions校为artistic ambitions、protege校为protégé；L276 Niccolo校为Niccolò；L419 ofhis校为of his、0/校为of；L420 OCR注号8按页图校为印本2。正文和脚注段精确跨度依源OCR保存，校读只作限定记录。

受控脚本chp8_p233_migration.py默认dry-run，核验来源资产与四段hash、候选编号和自然键、86条mention跨度、21条statement锚点/原文/外键、p.232续句关闭及coverage；应用前保存四表副本.bak-s2-chp8-p233-20261001。应用后audit_tables.py --summary errors=[]；全账本812段：346 complete、2 partial、54有理由排除、410 queued；候选7,928、提及14,842、statement 7,019。两条既存enrichment source_ref警告仍在。定向审计测试已重新运行，11项通过。下一正文段p.234 chp-8:08_CHP-8_sec_ii:l281-289，脚注复合段下一范围L424–461。

## 第八章印刷页234正文及注1–6（2026-10-01）

对照CHP-8.pdf物理第40页（页图留存于process/p234_page_review.png），迁入chp-8:08_CHP-8_sec_ii:l281-289及后置脚注L424–429。p.233 L279行末的The与p.234 L282的relations闭合为一句，p.233由partial转complete；p.234正文及页尾注释转complete，注释复合段扩至L373–429并保持partial，L430–461待处理。

正文记录Fumiani与Grand Prince Ferdinand的关系及Haskell对其“幻想”的解释；复用p.232的未识名Fumiani composition候选cand-7893，不另造同一作品。将Domenichino未识名参照画单独保留；记录建筑背景、guards、David祈祷、Cassana/Fumiani分担人物、modello审阅和增添运动的建议，未将建议写成已执行。Ferdinand改变主题后，Haskell把遗失指令推定为《The Stoning of Zechariah》；本页注3另报1716清单与Uffizi藏址，并记载目录误题，不独立核验。Niccolò Cassana作为画家兼顾问、Florence往返与Venice寄画、1707年《Portrait of a Cook》、其余未识名的Bacchanal和Venus/Cupid，以及《Conspiracy of Catiline》分别记录。Langetti段在页尾注释区，记录Ratti二手报告、Haskell基于1676年卒年与Ferdinand年龄的反驳；文本未带注号，故注明定位不确定，不当作已确认正文段。

注1列Fogolari (1937) Letters 45、47、48、49、50、53、54、55、56、57、59、61、63；注2定位II Samuel xxiv,12；注3定位II Chronicles xxiv,21、1716 inventory、La Pittura del Seicento a Venezia误题和Fogolari note34；注4引Soprani/Ratti及Fogolari Letter120；注5称《Conspiracy of Catiline》可能摹自仅以Rosa姓氏指称的作品，藏于Pitti no.111，并指向Jahn-Rusconi；页尾Langetti引文的Letter92日期由L429续完。所引书信、目录和档案未独立核读。Uffizi与Medici collection的类型/所指尚待S3判定；Pitti此处保留建筑与馆藏角色的区分疑点。

页图校读只记S2 qualifiers，S0来源不改：L282 Giannaritonio→Giannantonio、ns→us；L284 lais sceptre→his sceptre；L285 Niccolo→Niccolò；L286 Portrait os a Cook→Portrait of a Cook；L424 1699..→1699.；L426 IT Chronicles→II Chronicles并去除catalogue ' ' of OCR噪声；L428 No. in→No. 111。复核p.233已写入断言后，移除了L272正确破折号与L277正确弯引号被误记为OCR错误的两条qualifier，备份表为book-statements.jsonl.bak-s2-chp8-p233-audit-fix-20261001。

受控脚本chp8_p234_migration.py默认dry-run，核验来源与段hash、预期coverage、候选自然键、70条mention跨度、15条statement引文/行号/外键、p.233跨页关闭及coverage；应用前保存四表副本.bak-s2-chp8-p234-20261001。迁入17个候选、70条提及、15条statement。应用后audit_tables.py --summary：812段，348 complete、1 partial、54 excluded、409 queued；候选7,945、提及14,912、statement 7,034；s2_missing=[]、errors=[]。仍有2条既存enrichment source_ref警告、409段queued及1段partial。tests/test_audit_tables.py 11 passed；p.233/p.234迁移脚本py_compile通过；git diff --check退出码0（仅LF/CRLF提示）。下一范围为p.235 chp-8:08_CHP-8_sec_ii:l291-301，并继续复合脚注L430–461。
### 外键与最终测试复核（2026-10-01）

表后检查补齐脚注2、3的经文候选外键：st-chp8-p234-note2-samuel关联II Samuel 24:12候选cand-7954，st-chp8-p234-note3-stoning-record关联II Chronicles 24:21候选cand-7955；不改变断言数量。随后verbose定向测试报告11 passed in 30.21s；最终audit仍为s2_missing=[]、errors=[]。

## 第八章印刷页235正文与注1–6（2026-10-01）

对照`CHP-8.pdf`物理第41页，处理正文段`chp-8:08_CHP-8_sec_ii:l291-301`与后置脚注复合段L430–435。新增33个候选（cand-7956–cand-7988）、123条精确跨度提及和18条statement。p.235正文段覆盖L291–301转reviewed/complete；复合注释段由L373–429扩至L373–435并保持reviewed/partial，余下L436–461按源序待处理。

正文记录Luca Giordano为Ferdinand绘制《The Flight into Egypt》玻璃画、May 1702于Livorno会见Grand Prince并在其返程时受雇；Haskell称其 patronage 仅有“this one exception”及末期两位艺术家达到要求的概述，未在此页提前认定两位艺术家。Ricci的接触史标为不清；记录1704年《Crucifixion with the Madonna, St John and St Charles Borromeo》委托替换《Madonna delle Arpie》、Ricci前往Florence现场作画和协助Cassana通报Venetian market、Marucelli兄弟委托装饰、1706年两箱绘画及Marco Ricci作为Sebastiano侄子的报告、Poggio a Caiano未来画室计划与Ferdinand因病延期，以及后续《Allegory of the Arts》毁佚和Ricci为Marucelli/Pitti完成的装饰。分别保留候选关系与事实，不据弱关联生成正式边。

脚注1–6逐项登记并回链：Letter 75 (1702-05-26)、Fogolari Letters 98/99 (1704)、未编号Ricci来函报告、Archivio Mediceo Filza 5903 Letters 197/200 (1706)、Orazio Marucelli展出的Flora，以及Farsetti经Fogolari转引的Poggio房间/天花叙述；引文仅按Haskell脚注作来源定位，未声称独立查阅。脚注6尾行位于正文分节OCR L301，作为`footnote quotation continuation`回链至复合段L435，而不计为正文叙事。Farsetti描述的Sister Arts天花装饰与正文称毁佚的Ricci《Allegory of the Arts》分立，二者身份关系未决。正文的Spain返程与信函引文所说Naples返程可能是连续旅程环节，保留各自来源语境。S. Francesco de’ Macci、Galleria、Ferdinand favourite gallery/villa等身份或类型不确定项保持开放。

页图校读只在S2 qualifiers记录，不改S0：L291 `[Page 23]`→`[Page 235]`；L292移除painted后的OCR逗号；L296 `Marucelli.of`→`Marucelli, of`；L297 `Grand Princewhich`→`Grand Prince which`并移除`included`前杂点；L430修复`ibid..`及`è , qui`；L432移除`others.`后的OCR短横；L434 `No. zoo`→`No. 200`；L435脚注号8校为印本6。校读依据为`process/p235_page_review.png`。

受控脚本`chp8_p235_migration.py`默认dry-run；核验来源资产和段落hash、候选ID/自然键、123条提及跨度、18条statement锚点/原文/外键及coverage。应用前为四表保存副本`.bak-s2-chp8-p235-20261001`。应用后总账812段：349 complete、1 partial、54有理由排除、408 queued；候选7,978、提及15,035、statement 7,052。`audit_tables.py --summary`返回`s2_missing=[]`、`errors=[]`，仅保留2条既存enrichment `source_ref`警告；`python -m pytest tests/test_audit_tables.py -q`退出码0（11个测试均通过），`git diff --check`退出码0，仅提示既有LF/CRLF转换。下一段为p.236正文`chp-8:08_CHP-8_sec_ii:l303-309`，脚注复合段下一范围L436–461。

## 第八章印刷页236正文与注1–3（2026-10-01）

对照`CHP-8.pdf`物理第42页（页图留存于`process/p236_page_review.png`），处理正文段`chp-8:08_CHP-8_sec_ii:l303-309`及复合注释段L436–438。新增23个候选（cand-7989–cand-8011）、71条精确跨度提及和17条statement。正文将Ferdinand对Ricci Pitti装饰的参与保留为Haskell的推论，并将Gherardi报告另列为嵌套引述；分别记录Venus/Adonis天花场景、Diana/Callisto、Pan/Syrinx、Europa/Bull、Diana/Actaeon墙面场景、角落人物胸像和主门上方的Medici徽章构图。区分Pitti整体装饰与各场景，保留Rococo、Florence、Paris及Italy之间的风格评价为Haskell判断。Ricci的小人物/建筑背景画组、未名合作者和macchiette术语单独建候选，p.236末尾Ricci于1708年写信的未完句暂不补写。

注1报告Gherardi匿名记述及Consul Smith的藏画；注2称该壁画草图藏于Orleans Museum，但未核当前馆名或持藏；注3的Fogolari Letter 106只记其引用及Haskell对画作归属的未决判断，再单独记录1716 inventory所报Saluzzi建筑画中有Ricci人物、位于Lucca并署记1706。没有把该建筑画等同于Letter 106里作者不明的画作。Gherardi和Consul Smith继续使用页236n索引候选，留待S3身份审查。

页图校读只记S2 qualifiers、S0 OCR不改：L304 `avantgarde`→`avant-garde`；L305 `ofsun`→`of sun`、`air��a`→`air—a`；L306 Plate 39后的脚注号校为2；L308 `little suture`→`little future`；L309修复意大利语引文引号与重音；复合脚注L436 OCR号3按页图校为印本注1。引用文本和脚注分别链接到对应正文断言。

受控脚本`chp8_p236_migration.py`默认dry-run，核验S0资产与segment hash、候选ID/自然键、71条提及跨度、17条statement行锚点/原文/外键和coverage；应用前为四表保存副本`.bak-s2-chp8-p236-20261001`。应用后覆盖账本812段：349 complete、2 partial、54有理由排除、407 queued；候选8,001、提及15,106、statement 7,069。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，仍有2条既存enrichment `source_ref`警告；`python -m pytest tests/test_audit_tables.py -q`退出码0（11项通过）。下一正文段为p.237 `chp-8:08_CHP-8_sec_ii:l311-325`；后置脚注L439–461仍待处理。

## 第八章印刷页237正文与注1–5（2026-10-01）

对照`CHP-8.pdf`物理第43页（页图留存于`process/p237_page_review.png`），处理正文页段`chp-8:08_CHP-8_sec_ii:l311-325`与后置注释复合段L439–442。新增18个候选（cand-8012–cand-8029）、80条精确跨度提及和19条statement。p.236 L309的句子由本页L312–313闭合，故p.236 coverage转complete；本页正文L321末尾“but he”续至p.238 L328，因此p.237保持partial。

正文记录Ricci返威尼斯后一年赴英、至1716年仍在国外；Crespi于1708年2月返回Bologna并致信Ferdinand称自己也为Ricci的精神所打动；两位艺术家在Ferdinand宫廷错过会面两三个月、共同打破晚期巴洛克惯例及风格比较；Ferdinand鼓励Crespi展示《Massacre of the Innocents》，随后委托两幅身份未定的静物画。保留Haskell关于赞助与Crespi职业转向的判断。注2将Massacre原委托方明确记为Don Carlo Silva，并分别保留正文抵Florence与注释赴Livorno的表述，不补造两地之间行程。记录Crespi与Silva纠纷、Ferdinand介入、相关档案信件定位；现有候选身份待S3。

注1定位26 February 1708信件；注2定位介绍信、Zanotti及1948年展览目录，并记录Silva违约与后续Litigation报告；注3保留Crespi可能早年已受雇的限定，分别记录《Ecstasy of St Margaret》、被其取代的Lanfranco作品、S. Maria Nuova与Cortona Diocesan Museum；同注后续无重复编号段落列出Graziani、Santi、dal Sole及两封1708年信件。该段根据页图位置及内容判作注3续文，未另造注号。注4为Luigi Crespi书目定位，注5称Crespi最迟于26 February 1708已回Bologna并回指注1。被引信件、书籍和目录页均未独立查阅。

页图校读只记入S2，不改S0：L317 `had'much`→`had much`；L322 `letters-between`→`letters between`；L323 `sec letters`→`see letters`；L325 `26,1708`→`26, 1708`；L440 `Mostra Celebration`→`Mostra Celebrativa`。Crespi对Ricci的风格判断、可能早期雇用、Silva委托与违约及Lanfranco作品关系按原书语气、转述层级及身份边界记录。

受控脚本`chp8_p237_migration.py`默认dry-run，核验来源资产与段hash、候选ID/自然键、80条提及跨度、19条statement行锚点/引文/外键与coverage；应用前四表副本后缀`.bak-s2-chp8-p237-20261001`。该页写入时总账为812段：350 complete、2 partial、54有理由排除、406 queued；候选8,019、提及15,186、statement 7,088。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，仍有2条既存enrichment `source_ref`警告；`python -m pytest tests/test_audit_tables.py -q`为11 passed。后续页段已续办如下。

## 第八章印刷页238正文与注1–6（2026-10-01）

对照`process/p238_page_review.png`处理`chp-8:08_CHP-8_sec_ii:l327-336`及后置脚注L443–448，新增19个候选（cand-8030–cand-8048）、98条精确提及和27条statement。p.237末句由L328闭合；记录Crespi与Ferdinand的赞助往来、返抵Bologna、书信及赠画，并分别处理Ricci/Pepoli通信、画作和作品在Pisa的报告。跨页延续只按实文建立回链。三条Pepoli通信与正文所述两封信的映射未定；Gabinetto di Pisa的具体机构/空间类型未强定。原书所引信件和文献未独立核读，校读只记S2，S0不改。p.238末句续至p.239 L339，保持partial。

## 第八章印刷页239正文与注1（2026-10-01）

处理`chp-8:08_CHP-8_sec_ii:l338-348`及后置脚注L449–451，新增10个候选（cand-8049–cand-8058）、66条提及和24条statement。p.238跨页句由L339闭合；正文关于Livio Mehus、Ferdinand及其赞助终止的叙述与注释引文分别锚定。Mehus之子未具名；Ricci收画的具体作品、`this`的所指及部分艺术群体归属不作强行身份合并。页末“Venetian pictures”句延续到p.240 L351，故p.239保持partial。相关引文仍只作原书来源定位。

## 第八章印刷页240–241正文与注1–5（2026-10-01）

核对`process/p240_page_review.png`与`process/p241_page_review.png`（PDF物理页46–47），迁入p.240正文`l350-359`、p.241正文`l361-370`及后置注释L452–461，新增46个候选、175条提及和37条statement。p.239未完句由p.240 L351闭合；p.240记录Mehus作品进入Ferdinand收藏、当代罗马绘画评价、赞助展示政策与1706年St Luke节展览；p.241记录展览借展、画家与作品组合、Ferdinand借展及后续影响。脚注与正文具体claim分别回链，不把展览描述泛化为正式关系。

关键文本层映射：L452处于合并OCR注释段，但图像显示它是p.240正文“About 250 pictures...”续文；statement保留`body continuation in consolidated OCR segment`限定，避免误标脚注。Marco Ricci四幅风景画的借展只记为Haskell的高概率判断；未具名cardinal、Grand Duke、首个lunette的12幅作品与肖像、del Rosso兄弟集体和Poggio特殊房间保持未决。p.241注释L457–461按物理页和注号回链；引用书信及出版物未独立核读，OCR校读只存于S2。

受控迁移脚本`chp8_p240_241_migration.py`默认dry-run，写入前核验来源与段hash、候选自然键、精确mention跨度、statement引文/外键及coverage，并先备份四张表。完成后812段中356 reviewed/complete、54有理由排除、402 queued、0 partial；候选8,094、提及15,525、statement 7,176。`audit_tables.py --summary`为`s2_missing=[]`、结构错误0；`tests/test_audit_tables.py` 11项通过，`git diff --check`通过（仅提示LF/CRLF转换）。两条既存enrichment `source_ref`警告仍在，且全书S2远未完成。下一源段为`chp-9:09_CHP-9_intro:l1-1`，其为Markdown文件标题行，先按来源功能处理后继续第九章正文。

## 第九章开篇结构段处置（2026-10-01）

源序首两段`chp-9:09_CHP-9_intro:l1-1`（自动生成的Markdown文件名）与`l3-5`（印刷页码、Part III和VENICE分部导航）均无正文实体或事实内容，已按来源性质记为`excluded/complete`。受控脚本`chp9_intro_structure_exclusions.py`默认dry-run，核对源资产哈希、段哈希和原始coverage状态；应用前保存coverage恢复副本。应用后812段为356 reviewed/complete、56有理由排除、400 queued、0 partial；候选、提及与statement数量未变。`audit_tables.py --summary`为`s2_missing=[]`、结构错误0。下一个待处理段为`chp-9:09_CHP-9_intro:l7-16`（印刷p.245正文及脚注1尾段）。

## 第九章印刷页245–246正文与脚注尾段迁移（2026-10-01）

对照`p245_page_review.png`、`p246_page_review.png`及`CHP-9.pdf`物理页3–4，迁入`chp-9:09_CHP-9_intro:l7-16`、`l18-25`。新增24个候选（cand-8105–cand-8128）、64条提及和25条statement。记录威尼斯城市与政府/国家行动主体的区别、旅游与孤立政策、外客接触、审查/政治异端、旅行法、威尼斯衰退与中立、帕萨罗维茨和科孚事件、旧仪式、国家艺术委托及Tiepolo—Veronese关系。脚注1尾部L15–16链接至合并注释段L324；p.246脚注1的引用尾部L25链接至L328。p.245的`though there`由p.246 L19闭合；de Brosses、Molmenti及M. S[ilhouette]引文均保留转引/身份未决状态，不声称独立核读。OCR校读`Aeighteenth`→`eighteenth`、`against’`→`against`、`Uve`→`live`仅记在S2 qualifiers，S0未改。

受控脚本`chp9_p245_246_migration.py`默认dry-run，核验源资产与段哈希、候选自然键、64条精确提及跨度、statement行锚点/引文/外键及原coverage状态，写入前备份四表。应用后812段为358 reviewed/complete、56有理由排除、398 queued、0 partial；候选8,118、提及15,589、statement 7,201。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；`tests/test_audit_tables.py`为11 passed。下一待处理段为p.247 `chp-9:09_CHP-9_intro:l27-36`。

## 第九章印刷页247正文、注释尾段与跨页关联（2026-10-01）

对照p247_page_review_hi.png、p248_page_review.png及CHP-9.pdf物理页5–6，处理段chp-9:09_CHP-9_intro:l27-36。新增19个候选（cand-8129–cand-8147）、62条精确提及和20条原书statement。正文分别记录国家行政由贵族掌握、宪制受到外部批评、贵族财富与贫富家族分化、较富贵族垄断职位与较贫的patrician家庭反对扩大政治基础、新家族经购买进入贵族阶层、教会对国家的服从、资产阶级缺乏政治权力和自主文化，以及国家艺术赞助衰退后由有财力家庭承接。Goldoni离开威尼斯与Gasparo Gozzi依附贵族的表述按Haskell的社会判断记录。

p.247 L31止于“and may”，已保留到p.248 L39的续接并将本段置为reviewed/partial；p.248 L39闭合前不补写未完断言。页底L32–34是p.246注4的续文，链接合并注释段L331：区分Tiepolo画作在Palazzo Ducale的定位、Antichiesetta寓意壁画、Bambini等人的其他壁画、1782年Guardi为教宗来访绘制的四幅未识别作品及未具名Academy。L35–36在印本中没有可辨认注号，作为未编号页下注单独记录，保留Renier 1767引语、Marcellino p.30 n.78定位及OCR校读，不推断缺失注号或教宗身份。编号注1–3仍由独立合并注释段L332–334承载，待按源序审阅。

受控脚本chp9_p247_migration.py默认dry-run，核验资产与段哈希、候选自然键、提及跨度、statement锚点/引句/外键和原coverage状态；应用前备份四张表。应用后812段为358 reviewed/complete、1 reviewed/partial、56有理由排除、397 queued；候选8,137、提及15,651、原书statement 7,221。audit_tables.py --summary为s2_missing=[]、errors=[]；保留两条既存enrichment source_ref警告、397段队列和1段partial提示。tests/test_audit_tables.py为11 passed；git diff --check退出码0，仅有行尾转换提示。下一排队源段为p.248 chp-9:09_CHP-9_intro:l38-46。

## 第九章印刷页248–249与图版41–44（2026-10-01）

按`CHP-9.pdf`物理页6、7、9、10、11核对p.248–249正文与图版。p.248正文L38–46新增21个候选、56条提及、13条statement；其末句“devoid”由p.249 L78的“of a single religious symbol”闭合，p.248转complete。图版页核读发现Plate 41a、41b及Plate 43 OCR倒置；派生转录`09_CHP-9_intro_plates_visual-transcription.md`只补录这三条可读题注，保留Plate 41a的Barbaro家族肖像信息及Plate 43印本题注措辞。Plate 42、44可读题注已与书前图版目录语义重复，图版OCR段有理由排除；图像检查仍完成。视觉转录加入后S0为814个段（24个派生视觉转录段）。

按p.249印刷页物理页11迁入规范段`chp-9:09_CHP-9_intro:l77-88`，新增14个候选、37条精确提及和12条statement。记录Barbaro在Candia战争中的遭遇、与Morosini冲突及遗嘱定位；宪制作者与外国观察者对限制单一贵族权力的观察；威尼斯财富、贵族准入和新旧家族地位；Leonardo Pesaro、其叔父Giovanni Pesaro纪念碑、Pesaro宫、Niccolo Bambini及《Triumph of Venice》；旧家族政治特权与新商人阶层赞助。五个脚注标记分链至p.249 L87、合并注释L339–342及p.249 L88的注4续文。引用只作书内来源定位，不表述为独立核验。印本确认L78 OCR `os`应读作`of`；S0不改。p.249 L86末尾“At”续至p.250 L91，故p.249保持partial。

迁移脚本`chp9_p249_migration.py`默认dry-run，核对来源资产及段哈希、候选自然键、精确提及span、statement原文/候选外键、脚注指针和coverage；应用前为四表保留`.bak-s2-chp9-p249-20261001`。写后按语义位置修正两条候选描述、Barbaro遗嘱statement的脚注1映射，以及商人阶层断言的主客体。最终`audit_tables.py --summary`显示814段、362 complete、1 partial、60 excluded、391 queued；候选8,173、提及15,753、statement 7,251；`s2_missing=[]`、结构错误0。`tests/test_audit_tables.py`通过；`py_compile`与`git diff --check`退出码0（后者仅报告既有LF/CRLF提示）。两条既存enrichment `source_ref`警告未变。下一段为p.250 `chp-9:09_CHP-9_intro:l90-104`。

## 第九章印刷页250正文、注释延续与跨页闭合（2026-10-01）

对照`CHP-9.pdf`物理页12及`p250_page_review.png`，完成`chp-9:09_CHP-9_intro:l90-104`，并闭合p.249 L86止于“At”的句子。新增33个候选、64条提及和15条statement；p.249、p.250均转为reviewed/complete。正文记录Zenobio家族及其宫殿、Carlevarijs风景系列、Lazzarini的Ceres/Bacchus天花画、Tiepolo相关叙述、Widmann家族及其宫殿和Bagnoli乡间宅邸、Labia家族的Lazzarini委托，以及Giordano访问和库存记录。p.250注8续列的画作题名按条目分别记录，不推定确切作品身份或目录编号；Cochin引述只保留原书转述和题名范围。

页图校读只记在S2，S0不改：`socalled`→`so-called`、`i68os`→`1680s`、`trionso`→`trionfo`及`138139-`→`138-139.`；印本的`Quadi [sic]`保留原样。修正本次迁移脚本和mentions.csv中5条因重复后缀产生的mention_id冲突，保留全部提及记录并为每次出现分配唯一ID。

当前账本814段为364 reviewed/complete、60 excluded、390 queued、0 partial；候选8,206、提及15,817、statement 7,266。`audit_tables.py --summary`显示`s2_missing=[]`、`errors=[]`；`python -m pytest -q tests/test_audit_tables.py`通过（9项）。两条既存enrichment `source_ref`警告仍待后续S5处理。下一源段为p.251 `chp-9:09_CHP-9_intro:l106-114`。

## 第九章印刷页251正文与页下注1–4（2026-10-01）

对照`CHP-9.pdf`物理第13页完成`chp-9:09_CHP-9_intro:l106-114`。新增24个候选（cand-8217–cand-8240）、66条精确提及、19条原书statement。记录Manin家族（来自Friuli）在威尼斯及Passeriano的宅邸赞助、Bernini圣彼得大教堂柱廊对乡间宅邸双翼的参照、1708年匿名通信者对Manin宫殿及其藏物装饰的描述、Cignani与Mazza作品、Rossi和Dorigny的反复合作、Florio诗句所述装饰、Manin风格、成功画家与较具冒险性的画家群体。Rialto相邻地标的具体所指、未名画作、匿名通信作者及收信人均保持待定；Haskell的审美评价与通信者/诗人的引语分层记录。

页下注1–4位于合并脚注段`chp-9:09_CHP-9_intro:l323-445`的L349–352，已按注号与正文L107–113回链，故该合并段转reviewed/partial，仅标记L349–352；其余脚注仍待完整语义处理。注1指向p.268 n.5，尚待p.268材料处理后解析到具体段落。页图确认注2的书名印作`Le Grazie`（S0 OCR作`Le Crazie`），只在S2记录校正，S0未改。L114末句停在“despite the admiration”，续至p.252 L117，故p.251保持reviewed/partial；不为未完句提前登记断言。

受控迁移脚本`chp9_p251_migration.py`默认dry-run；预检来源哈希、候选ID与自然键、精确提及跨度、statement外键及coverage后应用，并为四张表保存`.bak-s2-chp9-p251-20261001`。全账本814段：364 reviewed/complete、60 excluded、388 queued、2 reviewed/partial；候选8,230、提及15,883、statement 7,285。`audit_tables.py --summary`显示`s2_missing=[]`、`errors=[]`；`python -m pytest -q tests/test_audit_tables.py` 11项通过。仍有两条既存enrichment `source_ref`警告。下一排队源段为p.252 `chp-9:09_CHP-9_intro:l116-122`。

## 第九章印刷页252正文与页下注1–7（2026-10-01）

对照`CHP-9.pdf`物理第14页完成正文段`chp-9:09_CHP-9_intro:l116-122`及合并注释段L353–359。p.252 L117闭合p.251 L114关于Sebastiano Ricci在威尼斯的雇佣情况，因此p.251转`reviewed/complete`。新增34个候选（cand-8241–cand-8254、cand-8257–cand-8276；复用Da Canal人物/作品候选cand-7781、cand-6593）、107条精确提及和32条statement。正文记录Ricci受雇分布、Tiepolo 1720年代的风格与早期题材、Corner家族及1722年前合作、威尼斯与奥斯曼战争的作者性解释、Tiepolo为Dolfin绘制的十幅Florus题材作品；并记录Dolfin家族、Daniele III与IV、Dionisio、Aquileia宗主教职位及Udine居住、图书馆和Bambini壁画。Daniele III遗嘱引语保留Haskell转述和条件遗赠语气；家族成员关系与个人关系分开记录，仍为S2关系候选。

页下注1–7按页码核对并逐条迁入L353–359。注3将Leningrad/Vienna的作品分布、Morassi等人对Vienna画作的旧识别、Haskell改读为《Brutus killing Arruns》，以及Udine图书馆房间内作者和年代不明的顶棚壁画分别记录；没有把该顶棚画归给Bambini或Tiepolo。注5涉及Palazzo Vendramin-Calergi的另一组罗马史题材画，归属只记为对Niccolo Bambini的既有归属说法。注2–3复用Vincenzo da Canal的既有作品候选；Dolfin、Morassi、Ivanov、de Renaldis、Madrisio、Biasutti等引文依本书书目辨认。注释仅作Haskell的引用或报告定位，未独立阅读被引页/档案。页图确认L357印作注5而S0 OCR误作6；共14处印本文字/号码校读记录在S2，未改S0。

本页末句记为“Dionisio约十八年后召来Tiepolo；其在威尼斯某家族宫殿刚完成的工作”这一已表达部分，委托目的续至p.253，暂不补写。受控脚本`chp9_p252_migration.py`默认dry-run；来源哈希、候选自然键、精确提及跨度、statement外键及既有coverage均预检后应用。原四张表分别留有`.bak-s2-chp9-p252-20261001`备份；随后修正statement续页指针至下一源段`l124-132`，并单独备份statement表。

应用后全账本814段：365 reviewed/complete、60 excluded、387 queued、2 reviewed/partial；候选8,264、提及15,990、statement 7,317。`audit_tables.py --summary`为`s2_missing=[]`、结构错误0；`python -m pytest -q tests/test_audit_tables.py` 11项通过。仍有两条既存S5 `enrichment.source_ref`警告；387段queued及2段partial表示S2未收口。下一排队源段为p.253 `chp-9:09_CHP-9_intro:l124-132`。

## 第九章印刷页253正文与注1–4（2026-10-01）

对照`CHP-9.pdf`物理第15页，完成p.253正文`chp-9:09_CHP-9_intro:l124-132`及合并注释L360–363。新增23个候选（cand-8277–cand-8299）、68条精确提及和18条原书statement。p.252 L122的Tiepolo委托句在p.253 L125闭合，p.252转complete；p.253 L132“this situation”续到p.254 L135，故p.253保持partial。合并注释段扩至L349–363，后续注释仍待处理。

正文分别记录Dionisio Dolfin的Udine Cathedral/Archiepiscopal Palace委托、楼梯顶棚与Abraham场景、印本题为《The Justice of Solomon》的法庭画及Tiepolo风格变化；不与注1中Daniele Dolfin在1759年召回Tiepolo父子的Cappella della Purità委托合并。索引写作“Judgment of Solomon”的作品身份留待S3。另记Haskell关于Tiepolo在Venice以外工作的解释、Antonio Barbaro与一位Daniele Dolfin所代表的政治往昔、两名未具名Dolfin家族成员入狱或流亡、Venice中立、Tiepolo的赞助理想与贵族阶层变化；1761年British Resident关于Zen继任人选的引语保留未具名报告者及Haskell转述层级。独立群体、地点和作品分别建候选，未把年代挂到人物，也未将政治性“Venice”强制改作正式国家实体。

注1–4分别记1759年后续委托、1762年《Nuova Veneta Gazzetta》对Tiepolo言论的意大利语报告、Public Record Office档案定位和Berengo 1955年引文；被引档案和书页未独立查阅。页图校读只记S2：确认L125–126跨行标题、L361意大利语变音字符，以及L363 `i$>55. P-14-`应读为`1955, p. 14`；S0未改。受控脚本`chp9_p253_migration.py`默认dry-run，预检来源资产/段哈希、候选、提及跨度、statement锚点和coverage；应用前保留四表恢复副本`.bak-s2-chp9-p253-offsetfix-20261001`。首次审计指出跨行提及偏移基准多计，已从本次前置恢复副本恢复四表、修正脚本并重放。最终`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；`python -m pytest -q tests/test_audit_tables.py` 11项通过。全账本814段：366 complete、60有理由排除、386 queued、2 partial；候选8,287、提及16,058、statement 7,335。两条既存S5 `enrichment.source_ref`警告仍在。下一正文段为p.254 `chp-9:09_CHP-9_intro:l134-146`，先闭合p.253 L132与合并注释段后续范围。

## 第九章印刷页254正文与注1–7（2026-10-01）

对照`CHP-9.pdf`物理第16页完成正文段`chp-9:09_CHP-9_intro:l134-146`中L135–146、合并注释段L364–369。p.253 L132于L135闭合，p.253 coverage转`reviewed/complete`；p.254 L145以“and”收尾并于p.255 L149续句，因此p.254仍为`reviewed/partial`。合并注释段现覆盖L349–369并仍为partial。

新增33个候选（cand-8300–cand-8332）、82条精确提及和29条原书statement。分别记录Faustina Savorgnan与Lodovico Rezzonico的婚姻、Rezzonico家族的Genoese来源/1687年晋贵/财富与政治地位、Aurelio Rezzonico的父子关系和Procuratore职位、向Bon家族购置未名Venetian palace、Carlo当选Clement XIII，以及Tiepolo为Pope侄辈绘制的Rezzonico婚礼壁画。Plate 43 caption作为既有段与KU候选交叉引用，不重复建作品。后半页记录贵族寓意壁画群、四家族apotheoses、Pietro Novelli/Collalto、Pietro Barbarigo及《Strength protecting Wisdom》、Tiepolo离威前的《Apotheosis of the Pisani》、Stra乡间宅邸和宫殿评价。所有关系仍是S2断言候选；不把四家族壁画统归Tiepolo，不把p.254的Pisani作品/地点强行对齐到索引或既有KU。

页下注1、3–7迁入合并段；注2留在正文OCR L146。记录注2的Molmenti归属报告：注释称其把Grassi fresco归于Fabio Canal；该报告没有独立核读，也不等于Haskell接受这一归属。页下注1–7各引文只作本书引用定位，未独立查阅。对照页图在S2记录`a scries`→`a series`、`everyday Use`→`everyday life`、破损撇号、`Mohnenti`→`Molmenti`、注3/5的OCR号8→印本号3/5，以及`i960`→`1960`和L145破损破折号；未改S0来源。

受控脚本`chp9_p254_migration.py`默认dry-run，先核验来源/资产哈希、coverage前态、候选ID及自然键、精确提及跨度、statement外键和跨页指针；应用前为候选、mentions、statements和coverage四表留存`.bak-s2-chp9-p254-20261001`。应用后全账本814段：367 reviewed/complete、60有理由排除、385 queued、2 reviewed/partial；候选8,320、提及16,140、statement 7,364。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；`python -m pytest -q tests/test_audit_tables.py` 11项通过。两条既存S5 `enrichment.source_ref`警告仍在。下一正文段为p.255 `chp-9:09_CHP-9_intro:l148-155`，闭合L145续句；合并注释从L370起继续处理。


## 第九章印刷页259正文与注1–6（2026-10-01）

对照CHP-9.pdf物理第21页处理正文段chp-9:09_CHP-9_intro:l188-200中的L189–200，以及合并脚注段L389–394。p.258 L186的“Angelo”于p.259 L189闭合为“Angelo Querini”；p.259 L200“other pictures”承接至p.260 L202，故本段记reviewed/partial。页下注1–6迁入合并脚注段。

新增33个候选（cand-8458–cand-8490）、67条精确提及和28条原书statement。开篇分别记录Querini的1762年改革、Foscarini成为Doge的方式“open to suspicion”、同时代人如何将他与integrity and learning等旧威尼斯德性联系，以及其本人风格与赞助趣味；上述为Haskell评价与报告，不扩写改革内容或晋位疑点。记录Foscarini宫殿与威尼斯Carmini教堂的位置，Pietro Visconti 1749年“富有家族”引述及年收入/画廊估值，并通过注3标明该话语来源。宫内前任主人Pietro Foscarini与Marco Foscarini分开；七幅Tintoretto画及其他威尼斯古典画以未名作品组保留，类型暂空，等待后续对象描述和S3裁决。Marco Foscarini的图书馆作为文献集合候选，区别于实体建筑；Batoni为其绘制的肖像与《The Triumph of Venice》分别处理，后者复用前置Plate 45对应的现有作品候选。Haskell关于Venice恢复、共和国、Doge Lionardo Loredano和图像构成的陈述拆分记录；城市Venice与共和国候选分开，Mercury、Neptune、Minerva、History、Fame等画中角色归term，不冒充现实人物KU。注释中遗嘱与画作目录分列，Foscarini图书馆出售和藏于Hofbibliothek分开作为两条关系候选。

页图校读：13 0,000→130,000、Eke→like、Triumph 0/→Triumph of、Repubhc→Republic、Doge Loredan→Doge Loredano、die Austrian→the Austrian、PP2Z2-6→pp.232-6，以及行首分隔短横清除；S0 OCR未改。脚注1为Querini章节互见；注2为未解全名/书名的Fontana页291定位；注3为Pietro Visconti致Gian Pietro Ligari的信、Arslan 1952第63页定位；注4定位Pietro Foscarini遗嘱及画作目录；注5报告藏书于1800年售予奥地利政府、现存Hofbibliothek；注6定位A. Clark 1959页232–236。引证对象未独立查阅。p.259注6称画作“now in the Kress Foundation at New York”，而前置Plate 45目录另称North Carolina Museum of Art、Raleigh及Samuel H. Kress Collection；两者保留为本书内部位置/馆藏表述差异，不在S2裁定。

受控脚本chp9_p259_migration.py默认dry-run，核验p.259正文段和原书资产SHA-256、coverage前态、候选自然键、67条提及跨度、28条statement锚点与外键，并闭合p.258续句；应用前为候选、mentions、statements和coverage四表保存.bak-s2-chp9-p259-20261001。应用后全账本814段：372 reviewed/complete、60有理由排除、380 queued、2 reviewed/partial；候选8,478、提及16,484、statement 7,513。全表审计s2_missing=[]、errors=[]，定向测试11项通过，git diff --check退出码0；两条既存S5 enrichment.source_ref警告和覆盖未完成警告仍在。下一正文段为p.260 chp-9:09_CHP-9_intro:l202-210（闭合本页L200），合并脚注从L395继续。
## 第九章印刷页255正文、脚注1续文与注2–4（2026-10-01）

对照`CHP-9.pdf`物理第17页处理正文源段`chp-9:09_CHP-9_intro:l148-155`的L149–154、脚注1续文L155，以及合并脚注段`chp-9:09_CHP-9_intro:l323-445`的L370–373。新增39个候选（cand-8333–cand-8371）、74条精确提及和29条原书statement。p.254 L145的“for it”由p.255 L149闭合，p.254 coverage转`reviewed/complete`。p.255 L154止于“The Sandi, who had been”，由p.256 L158续接，故本段保持`reviewed/partial`。L155是印刷页底部脚注1续文，不是正文第二段；coverage表记连续范围L149–155，并在说明中区分正文与脚注，以满足行范围审计；它与合并段L370的注1起首互链。注2–4分别位于合并段L371–373。

正文记录Tiepolo为Pisani宅邸设计家族寓意画、在世Pisani成员肖像、Almorò与未具名母亲、Fatherland与Virgin、神学美德、Wisdom及Fame；Plate 44与书前图版目录L118互引，保留p.254“Apotheosis of the Pisani”、图版目录“Glorification of the Pisani family”及本页“family allegory”等原书称谓，题名/对象对齐留待S3。页图读Almorò，S0 OCR作Almorô。Fame传播家族声望的四洲范围、1762年时代背景及英格兰夺取Canada和India的说法按Haskell原文记录；不在S2作外部史实核验。

其后分别记录艺术家有时主动选择题材、家族奉承画的赞助条件、Time寓意、旧/新贵族的历史叙事、1700年Corner委托Lazzarini表现一位未具名家族成员、Soderini历史重构及Contarini在1574年迎接Henri III等内容。把“社会声望高于军事功绩”保留为Haskell的解释。L153 OCR作`Sodcrini`，按页图校读为`Soderini`；其家族、历史题材周期和未名别墅分别保留候选，注3的“The villa”只按邻近语境关联，不强判建筑身份。Mira保留原书地名。注4“Musée Jacquemart-André, Paris”作为短位置标签登记，未据此声称当前馆藏或正式保管关系。

注1 L370称十八世纪Venice世俗装饰合同几乎缺失、委托人与画家之间应有相当协商，继而转述Zannandreis对Francesco Lorenzi向Tiepolo提供西班牙国王寓意方案的说法。续文L155称故事可能是展示Lorenzi博学的杜撰，但仍提示艺术家有一定自由；随后转述Novelli《Memoirs》p.62关于由其本人选择Collalto题材，并概括十八世纪多数威尼斯画家向赞助人展示modelli、成品与方案差异很少的惯例。各层均保留为Haskell的转述或推论。Zannandreis、Novelli《Memoirs》、Da Canal p.57和Battistella 1903只作为原书引证/报告定位，本次未独立查阅。注3按印本记作3（S0 OCR误作8），原书报告别墅在第一次世界大战中被毁；不补出建筑实名。

本次只修正表内锚点和coverage，不改写02来源OCR。页图校读记在S2：`Almorô`→`Almorò`、`Sodcrini`→`Soderini`、`ofconsultation`→`of consultation`、注号`8`→`3`。同时关闭p.254遗留的Pisani跨页statement；把“家族寓意画并非唯一奉承方式、题材有时更含蓄”登记为p.255完整判断，不再误标为跨页续句。受控脚本`chp9_p255_migration.py`默认dry-run，预检源段与资产哈希、候选ID/自然键、74条提及的原OCR精确跨度、statement外键及coverage前态；应用前为候选、提及、statement和coverage四表分别保存`.bak-s2-chp9-p255-20261001`。

应用后全账本814段：368 reviewed/complete、60有理由排除、384 queued、2 reviewed/partial；候选8,359、提及16,214、statement 7,393。最终`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，`python -m pytest -q tests/test_audit_tables.py`通过11项，`git diff --check`退出码0。审计仍列两条既存S5 `enrichment.source_ref`警告、384段queued和2段partial；机械通过不构成语义完整性验收。下一正文段为p.256 `chp-9:09_CHP-9_intro:l157-165`，合并注释从L374继续。

## 第九章印刷页256正文与注1–7（2026-10-01）

对照`CHP-9.pdf`物理第18页处理正文源段`chp-9:09_CHP-9_intro:l157-165`中的L158–165及合并脚注段L374–379。新增37个候选（cand-8372–cand-8408）、85条精确提及和40条原书statement。p.255 L154的Sandi句由p.256 L158闭合，p.255 coverage转`reviewed/complete`；p.256 L165以Antonio Longo回忆录的引入语收尾，内容尚未闭合，待p.257 L168接续，故p.256仍为`reviewed/partial`。脚注段扩至L379并保持partial；p.255 L155的注1续文仍与合并段L370的注1入口互链。

正文先记录Sandi家族于1685年晋贵、较早雇用Tiepolo、家族财富与法律职业的关联，以及以古代故事为题的“Powers of Eloquence”宫殿顶棚。Goldoni《Memoirs》被Haskell用来支持十八世纪Venice律师地位仅次于贵族的比较；注明这是Haskell的引证陈述，未独立查阅Goldoni。其后分别记录Carlo Cordellina作为当时首要辩护律师、拒绝无用奢华却主张盛大生活、在Vicenza和Montecchio建宅、召Tiepolo装饰乡间宅邸；Tiepolo虽对大量宴饮不满，仍绘制《The Continence of Scipio》《The Family of Darius before Alexander the Great》及《The Triumph of the Arts》。将“壁画清楚影射赞助人宽宏”保留为Haskell解释。另记录希腊/罗马故事在十六、十七世纪被编为表现贵族美德的 repertory，并保留Haskell关于其可能具有更具体含义的“probable / may often”限定；不补写未明示的解释。

对后文分别记录许多patrician families声称罗马血统（原文是家族的声称，不视作谱系核实）、国家官员惯常被比作罗马英雄、1724年Pietro Loredan离开中立的Venice赴任其指挥的Legnano堡垒及演说者援引Mucius Scaevola；Antonio Loredan离开Padua总督职位与Pompey的比较仅称“大约同一时期”，不将未注明年份的注7演说强行定年。随后记录Sacrifice题材的流行及其戏剧性/权力责任含义、古代题材的振奋作用、Tiepolo与追随者频繁绘制《The Banquet of Antony and Cleopatra》，以及Haskell对Cleopatra/Antony对照、Venice政策暗示和贵族奢华/新政治经济理论之间张力的解读。`surely`、`frequently`和`at about the same time`等措辞均留在断言限定中；Carlo Gozzi仅作为Haskell所称某些作品的“文学对应”，不增补作品名。

合并脚注L374–379按印刷注号登记：注1的Correr谱系手稿引用；注2 Morassi 1955年页4–12及其四则顶棚故事清单（Amphion建Thebes城墙、Hercules与被缚的Cecrops、Orpheus寻Eurydice、Perseus骑Pegasus杀海怪）；注3 Goldoni《Memoirs》卷I第23章；注4方括号内的`[G. B. Fontanella]`，不扩展其身份/作用；注5 Tiepolo致Francesco Algarotti的1743年10月26日信件，经Fogolari 1942年页34转引；注6 1724年Pietro Loredan离开Venice的演说；注7以Padua名义为Antonio Loredan离任所作的无日期演说。上述均作为Haskell的来源定位或报告，不声称独立查阅原件/被引文本；未把Correr手稿或演说定位当作对相应断言的独立验证。

页图校读保留在S2、不改写S0：正文`Eke`→`like`、`beHeved`→`believed`、`famihar`→`familiar`、`famines`→`families`、`pohey`→`policy`、`symboEsed`→`symbolised`、`Eterary`→`literary`；注释校正L376 Mémoires前多余句点、L377印本注号5（OCR作8）与`1942`（OCR作`1.942`）、L378 `veto`→`vero`和`Proweditore`→`Provveditore`、L379 `magnifica Città`（OCR作`magnificá Citd`）。候选/提及保留源OCR精确跨度，标准读法及页图依据作为S2校勘元数据保存。

受控脚本`chp9_p256_migration.py`先默认dry-run，核验来源资产和段hash、当前coverage、候选ID/自然键、85条提及跨度、40条statement外键及跨页指针；应用前分别留存候选、mentions、statements、coverage四表备份`.bak-s2-chp9-p256-20261001`。应用后全账本814段：369 reviewed/complete、60有理由排除、383 queued、2 reviewed/partial；候选8,396、提及16,299、statement 7,433。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；`tests/test_audit_tables.py`通过；`git diff --check`通过。仍有两条既存S5 `enrichment.source_ref`警告、383段queued和2段partial。下一正文段为p.257 `chp-9:09_CHP-9_intro:l167-177`（闭合本页L165），合并注释从L380继续。

## 第九章印刷页257正文与注1–7（2026-10-01）

对照`CHP-9.pdf`物理第19页处理正文源段`chp-9:09_CHP-9_intro:l167-177`中的L168–177，以及合并脚注段L380–386。新增28个候选（cand-8409–cand-8436）、65条精确提及和29条原书statement。p.256 L165对Antonio Longo回忆录的未完引入由p.257 L168闭合，p.256 coverage转complete；p.257 L177在“and”处跨页接至p.258 L180，故p.257保持`reviewed/partial`。复合脚注段扩至L386并继续保持partial；p.255 L155脚注1续文仍回链至L370。

正文记录Longo回忆录被Haskell用于说明贵族曾竞争提供最昂贵宴席；Labia宫拥有Tiepolo最宏大的《Banquet》版本且家族以奢华闻名；Maria Labia作为家族女性长辈、珠宝收藏及她与Cleopatra珍珠赌约的对应。把“Tiepolo意在恭维”与“Maria能将自己认同为埃及女王”保留为Haskell的解释/推断，不改写成有独立证词的意图或自述。后文记录Haskell关于威尼斯贵族相对法国同等阶层掌握国家实际权力、使历史画继续兴盛的宏观解释；Paolo Renier于1772年对君主臣属与自由共和国成员身份的引语；法国中产阶级推动历史画复兴并以David为修辞高点、威尼斯贵族与Tiepolo的回应；Vandières（后为Marigny）1754年致罗马法国学院主任的信、派学生临摹Contarini-Pisani别墅壁画的安排及引文所述法国史用途；Cochin对Tiepolo的赞誉；Haskell对bozzetti、全幅装饰、rococo品味与Tiepolo道德担当的评价；最后保留威尼斯肖像庄严、少见法式情色/轻佻绘画及“无Boucher/Fragonard对应者”均为原作者比较判断。保留`probably`、`may have`、`there can be little doubt`及其余作者限定，不作量化推断。

文内与注释实体边界分别记录：Labia宫具体《Banquet》版本与跨页所论的反复出现的Banquet题材先分开；Maria的珠宝作为未识别集合体暂不强定KU类型；Tiepolo在Villa Contarini-Pisani的壁画因具体场景未给出而保留未名作品候选；Vandières姓名中的后续爵号按本页明确括注与既有索引候选记录，其他跨章/同名身份留待S3。正式关系仍不在S2写入；宫殿容纳作品、Maria所有珠宝、书信传递与临摹安排均标为关系候选。

合并脚注L380–386按印本注号登记：注1 Antonio Longo 1820年卷I页81–90；注2 Tassini 1915年页335；注3 De Brosses卷I页149；注4 Renier引文由T. M. Marcellino页18注32转引；注5 Byam Shaw 1960年页530；注6 Villot页169–176；注7 Levey 1959年相关章节。以上均是Haskell原书的定位/转引信息，未独立查阅原书信、回忆录、被引书文或页码；注4转引语不作为Renier原件的独立核验。

页图校读只保存在S2、不改写S0：正文L169 `ahve`→`alive`；脚注L380 `1820,1`→`1820, I`；L384 OCR注号6核为印本注号5，`i960`校为`1960`。L177句末的and与p.258 L180回链；p.257本页注5脚注标记与OCR页底编号差异另记在statement校勘元数据中。

受控脚本`chp9_p257_migration.py`默认dry-run，核验来源资产/段hash、coverage前态、候选ID与自然键、65条提及跨度、29条statement外键和跨页指针；应用前为候选、mentions、statements、coverage四表保存`.bak-s2-chp9-p257-20261001`。应用后全账本814段：370 reviewed/complete、60有理由排除、382 queued、2 reviewed/partial；候选8,424、提及16,364、statement 7,462。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，`tests/test_audit_tables.py`通过。仍有两条既存S5 `enrichment.source_ref`警告、382段queued及2段partial。下一正文段为p.258 `chp-9:09_CHP-9_intro:l179-186`（闭合本页L177），合并注释从L387继续。

## 第九章印刷页258正文与注1–3（2026-10-01）

对照`CHP-9.pdf`物理第20页完成正文段`chp-9:09_CHP-9_intro:l179-186`的L180–186及合并注释段L387–388。p.257 L177末尾的“and”由p.258 L180续接并闭合；p.258 L186以“Angelo”结束，p.259 L188以“Querini”续接，故本页段记`reviewed/partial`。注1–3迁入合并段，其余后置注释续于L389。

新增21个候选（cand-8437–cand-8457）、53条精确提及和23条原书statement。正文保留Haskell关于Pellegrini、Rosalba Carriera与法国绘画比较的`appear to have`限定，对Gian Antonio Guardi在巴黎可能成功的判断仍作为反事实评价；Bathsheba、Susanna、Aurora/Flora及Roman and Greek history按一般绘画题材记录，不识别具体作品。Tiepolo的“纯粹 enchantment”评价引出Villa Valmarana壁画组；其具体委托过程和赞助人被作者明言所知不足，因此不将Valmarana家族成员擅自定为委托人。Leonardo Valmarana 1757年家族首领身份保留`we are told`及`seems`；性格描述归因于葬礼演说，Haskell明确质疑其作为公正传记材料的可靠性，并把其中对谦逊美德的强调作为解释壁画语境的参考。Tiepolo之子未实名，foresteria中的乡村壁画另作未识别作品候选。Marco Foscarini的家世、教育、出使、史官任命、文学史兴趣、Procuratore与Doge职任、政治趋向及反对Angelo Querini均按Haskell叙述分条记录；不添加任职日期或外部人物身份，跨页姓氏仍待p.259闭合。关系性质的表述留在S2 statement候选中，未写入S6正式边。

注1定位Levey在`Journal of Warburg Institute` 1957年卷册的页码298–317。注2登记1765年Parenzo的Valmarana葬礼演说标题及地点/人物。注3将Tommaso Gar、1843年书目定位与Emilio Morpurgo作者名分开记录；因注释未给Morpurgo书名/年份，不另造可唯一识别的作品候选。所有被引文献只按Haskell原书注释定位，本次未独立查阅。页图校读记录于S2：`seventeenthcentury`→`seventeenth-century`、`reHable`→`reliable`、`RepubHc`→`Republic`、`Cartedrale`→`Cattedrale`、`if di`→`il dì`；S0转录未改。

受控脚本`chp9_p258_migration.py`默认dry-run，预检源段/资产SHA-256、coverage前态、候选自然键、53条提及跨度、23条statement锚点与外键，并闭合p.257指针；应用前为候选、mentions、statements和coverage四表保存`.bak-s2-chp9-p258-20261001`。应用后全账本814段：371 reviewed/complete、60有理由排除、381 queued、2 reviewed/partial；候选8,445、提及16,417、statement 7,485。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；两条既存S5 `enrichment.source_ref`警告及未完成覆盖告警仍在。`python -m pytest -q tests/test_audit_tables.py`通过11项，`git diff --check`退出码0。下一正文段为p.259 `chp-9:09_CHP-9_intro:l188-200`（闭合本页L186），合并注释从L389继续。


## 第九章印刷页260正文与注1–9（2026-10-01）

对照`CHP-9.pdf`物理第22页迁入正文段`chp-9:09_CHP-9_intro:l202-210`及合并注释L395–403。p.260 L203闭合p.259 L200“other pictures”；L210“We know too”续至p.261 L212，因此p.260正文保留`reviewed/partial`。印本页码260已纠正S0行首`[Page 200]`，只记S2，不改OCR。

新增31个候选（cand-8491–cand-8521）、74条精确提及和30条原书statement。保留p.259引入的未名画作组cand-8485，并用p.260说明该组表现威尼斯作家、部分作品似在罗马绘制；分别记录Foscarini的书籍/手稿收藏、两城聘用雕刻家、图像散佚、Novelli的嵌套回忆及S. Marco画作/历史画请求、Guarana壁画和Nogari肖像。将当代人对Foscarini房间的修辞性描述与Haskell的评价分层；Pisani私立学院作为机构、Almorò的绘画课作为程序分别记录。Moschini对威尼斯艺术支持的主张与Haskell对赞助范围的限制分别保留为来源判断。脚注5印本编号为5而S0误作6；Novelli所说“Almord”据页图校为“Almorò”；`lais rooms`校为`his rooms`，原始OCR均保留。脚注所引文献只按原书定位，未独立核读。

脚注8在规范OCR L402截于`(G. A.`。据同版扫描转录完整脚注8为新增派生S0/S2段`chp-9:09_CHP-9_intro_notes_p260_visual-transcription:l1-1`；重复部分只提供完整脚注的精确锚点，不重复生成提及或statement。注8中Zenobio/Carlevarijs及Zambelli/Pittoni保留为关系候选，Miani、Baglione和Alessandro Longhi的压缩表述不拆配到个人。原OCR文件保持不变。

受控脚本`chp9_p260_migration.py`默认dry-run，核验OCR及视觉转录哈希、源行跨度、候选ID/自然键、74条提及、statement原文/外键与coverage前态；应用前为候选、mentions、statements、coverage四表保存`.bak-s2-chp9-p260-20261001`。应用后全账本815段：374段reviewed/complete、60段有理由排除、379段queued、2段reviewed/partial；候选8,509、提及16,558、statement 7,543。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；`python -m pytest -q tests/test_audit_tables.py`11项通过，`git diff --check`退出码0（另有环境既存LF/CRLF提示）。仍有两条既存`enrichment.source_ref`警告、379段queued及2段partial。下一正文段为p.261 `chp-9:09_CHP-9_intro:l212-216`（闭合p.260 L210），合并注释从L404继续；全书S2尚未收口。

## 第九章印刷页261正文与注1–6（2026-10-01）

对照`CHP-9.pdf`物理第23页处理正文源段`chp-9:09_CHP-9_intro:l212-216`的L213–216及合并注释L404–409。p.260 L210“We know too”在p.261 L213续为完整句，p.260转`reviewed/complete`；p.261 L216结尾“and to”续到p.262 L218，因此p.261记`reviewed/partial`。注1–6按扫描印本号校读并迁入合并注释段，覆盖由L349–403扩为L349–409。

新增22个候选（cand-8522–cand-8543）、47条精确提及及28条原书statement。记录匿名英国女性旅行者对威尼斯挂画习惯的嵌套描述，并把该书作者保持匿名；分别记录Haskell关于18世纪初旧贵族家庭装饰目标、库存反映当代画委托/购买减少、末代充分进入威尼斯藏画的17世纪末艺术家群，以及Pisani家族在Almorò青年时期对Giuseppe Zais的特别赞助。区分S. Stefano宫殿与Stra乡间宅邸，并为身份未明的后1720年小批画作、Stra当代画作分别保留作品组候选；未把Almorò写成个人委托人。后半页将1745年“贵族不喜欢花钱买画”保留为Gherardi致Muratori信中的单一观察，不当作普遍事实；腐败/颓败、室内装饰、旧画廊、经济衰退及财富集中等说法均按Haskell的论证和限定分别记录。Foscarini为城中最富家族的说法保留`rumoured`，收入续句留待p.262。

脚注登记旅行书`Letters from Italy`及匿名作者描述、Levi收藏和18世纪威尼斯库存、Seminario Patriarcale MSS. 788.13与Pietro Edwards、Muraro/Emporium、Gallo 1945、P. E. Gherardi致L. A. Muratori的1745年信及Biblioteca Estense、Beltrami 1954。脚注引用和馆藏定位按Haskell原书记录，未独立查阅。跨页的patronage、购买和收藏表述保留为S2断言/关系候选，不写入S6正式关系。历史候选与family/branch身份问题留给S3。

页图校读只记S2、不改S0：正文L214 `Almord`→`Almorò`、`closej`→`close,`；L215 `T don’t find’`→`‘I don’t find’`、`welkworn`→`well-worn`；L216 `sine arts`→`fine arts`、`silled`→`filled`；注L404 `ia France`→`in France`、`HI`→`III`，L406 `i960`→`1960`，L408和L409的OCR脚注号8分别核为印本5和6。p.261所有来源引句仍保留原OCR原文，校读信息写入statement限定字段。

受控脚本`chp9_p261_migration.py`默认dry-run，预检p.260–262及注释源段SHA-256、coverage前态、候选ID/自然键、47条提及跨度、28条statement引句与外键及两处跨页指针；应用前为候选、mentions、statements、coverage四表留存`.bak-s2-chp9-p261-20261001`。应用后全账本815段：375 reviewed/complete、60有理由排除、378 queued、2 reviewed/partial；候选8,531、提及16,605、statement 7,571。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；`python -m pytest -q tests/test_audit_tables.py`通过11项，`git diff --check`退出码0（有既存LF/CRLF提示）。两条既存S5 `enrichment.source_ref`警告未涉及本次写入。下一正文段为p.262 `chp-9:09_CHP-9_intro:l218-229`，用于续闭p.261 L216；合并注释下一范围为L410起。全书S2尚未收口。

## 第九章印刷页262正文与注1–6（2026-10-01）

p.262规范段`chp-9:09_CHP-9_intro:l218-229`对照`CHP-9.pdf`物理第24页完成，新增27个候选（cand-8544–cand-8570）、79条精确提及和29条statement。p.261 L216末“and to”由p.262 L219续接并闭合；p.261转complete，p.262正文/页下注OCR范围转complete。合并脚注段扩至L413，仍因后续脚注未处理而partial；本页注1、3、4、5由对应页段/合并段锚定，注2以同版视觉转录补足，注6由p.262页OCR L228–229锚定。

事实范围包括Foscarini年收入转述、最低生计估算、Canaletto与Rosalba Carriera价格、外来竞争对高价的解释、Piazzetta《Angelo Custode》估值、Tiepolo两组作品及相应报酬；另记录新贵族入籍费用与当代画购置、Grassi收藏及可能的古老血统动机、Labia与Giovanelli收藏判断。Biffi 1773年对Palazzo Giovanelli藏画的意大利语引文保留为嵌套档案转引；“Paolo”“Palma”等不充分姓名保持未对齐。将《Angelo Custode》《Martyrdom of St John the Bishop》、Pietà圆顶壁画和Labia库存的`Ritratto con cristallo`、`Una Palla`作为不同作品候选，避免把库存描述当成已确认目录作品。引文所涉库存、档案、书目及Venturi微缩胶片均未独立查阅。

页图校读仅记S2、不改S0：OCR页码`[Page 202]`应为印刷p.262；`domeof`→`dome of`、`GuerCino`→`Guercino`、`art seemed, to stop`→`art seemed to stop`；Cignaroli后OCR注号6核为印本5，Giovanelli句末印本注6在OCR中漏失；MSS. locator标点据页图记录。

受控脚本`chp9_p262_migration.py`默认dry-run，校验p.261–262、合并脚注与视觉转录的段哈希，候选自然键、79条提及精确跨度、29条statement原文/外键及跨页引用。应用前为候选、mentions、statements、coverage四表留存`.bak-s2-chp9-p262-20261001`。应用后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全账本816段中378 complete、60 excluded、377 queued、1 partial。候选8,558、提及16,684、statement 7,600。`python -m pytest -q tests/test_audit_tables.py`退出码0，`git diff --check`退出码0（LF/CRLF为既存提示）。两条既存S5 `enrichment.source_ref`警告未涉及本次写入。下一正文段为p.263 `chp-9:09_CHP-9_intro:l231-238`，合并脚注从L414继续。

## 第九章印刷页263–264正文与注释（2026-10-01）

p.263（PDF物理第25页）源段`chp-9:09_CHP-9_intro:l231-238`、p.264（物理第26页）源段`l240-249`及合并注释L414–427均对照扫描件完成语义处理。新增35个候选（cand-8571–cand-8605）、75条精确提及和31条statement。正文登记Sagredo家族、Niccolò与Zaccaria的家族/政治语境、Zaccaria的Bergamo任职、收藏来源、声誉、家庭安排及遗产；保留作者评价、`seems`限定和引述链。注释登记Barbaro谱系报告、Da Canal/Meschini与Breval评价、Wright轶事定位、Carracci图纸购买、Crespi委托、Piazzetta作品购买、遗嘱与收藏散佚记录。档案、手稿和被引书页均按原书引用层级处理，未声称独立核读。S2仅登记关系候选，不生成S6正式边；人名异写、家族归属和作品身份不提前合并。

p.263 note 6 的遗嘱引文由p.264 OCR L245–248续完并回链。p.264 note 8在合并注释L427截断，断言保留partial并指向p.265 L295–296；L428重复Plate 46题注，作为重复OCR排除迁移，稍后回链至规范图版段。扫描校读只记S2、不改S0；移除了把原样拼写误标为OCR更正的元数据。受控脚本`chp9_p263_p264_migration.py`默认dry-run，预检三源段SHA-256、候选自然键、精确提及字符跨度、statement引句及外键；应用前为候选、mentions、statements、coverage四表留存`.bak-s2-chp9-p263-p264-20261001`。应用后全账本816段：380 complete、60有理由排除、375 queued、1 partial；候选8,593、提及16,759、statement 7,631。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，两条既存S5 `enrichment.source_ref`警告未涉及本次写入；审计测试11项通过；`git diff --check`退出码0（LF/CRLF提示）。下一源段为Plate 45 `chp-9:09_CHP-9_intro:l251-256`，之后继续Plate 46–48及p.265正文/注释。全书S2仍未完成。

## 第九章Plate 45–46图版与视觉转录（2026-10-01）

Plate 45和Plate 46分别对照`CHP-9.pdf`物理第27、28页复核。两段原OCR题注均倒置/破碎，保留`09_CHP-9_intro.md`不变，在已有`09_CHP-9_intro_plates_visual-transcription.md`分别补入L6与L8–9；`build_source_segments.py`预览显示818段、issues=0，写入`segments.jsonl`前分别保存`.bak-s2-chp9-plate45-s0-20261001`和`.bak-s2-chp9-plate46-s0-20261001`。

Plate 45题注确认Batoni《Triumph of Venice》，复用已用于p.259及图版目录的作品候选和Batoni索引候选；新增2条提及、1条`caption_attribution`关系候选。Plate 46图版另有供Plate 46–47共用的编辑性分组题头“Venetian artists in England during the early years of the eighteenth century (see Plates 46 and 47)”，保存在视觉转录和coverage导航说明中，不将该题头虚构为独立实体。作品题注为“Pellegrini: Pierre Motteux and his family”，复用图版目录候选，分别记录作者归属和Pierre Motteux题名主体；其他家庭成员未实名化。新增3条提及、2条statement关系候选。合并注释L428重复分组题头，排除第二次迁移。\n\n第一次Plate 45表审计指出视觉段`source_line_ranges`须为区间格式且原始倒置OCR段须说明`no_semantic_content`；已以`chp9_plate45_coverage_fix.py`修正并留恢复副本。最终coverage为818段：384 complete、60有理由排除、373 queued、1 partial；8,593候选、16,764提及、7,634 statement。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，定向审计测试11项通过；两条既存enrichment `source_ref`警告和单个部分处理注释仍在。下一段为Plate 47 `chp-9:09_CHP-9_intro:l279-285`；p.264 note 8仍待p.265 L295–296闭合。全书S2未完成。\n\n## 第九章印刷页265–267正文、合并注释及第二节开头（2026-10-01）

对照`CHP-9.pdf`物理第29–33页，继续迁移p.265正文及注释、p.266–267正文及注释，并闭合合并脚注段L428–445；p.267第二节标题L1按导航结构排除，L3–4正文和注6完成语义处理。p.264注8由p.265 L295–296续闭；未把重复Plate 46分组题头再迁移。各批次汇总新增66个候选、172条精确提及和89条statement。

p.267注6已在S0第二节文件L4中，扫描页确认印本注号为6，S0字母`a`为OCR误识；`Bozzôla`按扫描校为`Bozzòla`。威尼斯在该处是共和国政治实体，Rome指教廷权威；1657年重新接纳耶稣会、政府要求严格宗教正统及Haskell转述的宗教/政治异议格言分别登记。脚注仅指向Bozzòla对Casanova态度的描述，没有提供描述内容；两个人物候选的身份留待S3。

受控迁移为候选、提及、statement和coverage保留恢复副本。迁移后账本820段：393 reviewed/complete、61有理由排除、366 queued、0 partial；候选8,659、提及16,944、statement 7,728。`build_source_segments.py`预览为820段、issues=0；`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，尚有两条既存`enrichment.source_ref`警告。下一规范段为`chp-9:09_CHP-9_sec_ii:l6-16`（p.268）；全书S2仍未完成。\n

## 第九章印刷页268–269正文与跨页引语（2026-10-01）

p.268（PDF物理第34页）与p.269（物理第35页）按规范段顺序对照扫描件完成：p.268 `chp-9:09_CHP-9_sec_ii:l6-16`新增10个候选、39条精确提及和21条statement；p.269 `l18-25`新增14个候选、40条提及和18条statement。两页合计24个候选、79条提及、39条statement。p.268的1743年观察者引语在p.269 L19闭合，并单独记录Haskell对威尼斯堂区教堂实例的回应；对Scalzi修会、旧堂、新堂与修院作区分，匿名pamphleteer的论证保留为嵌套引文。Cavazza姓氏和St Mark名称在分节OCR中跨行，提及跨度分别按各源行记录。

页图校读只记S2，不改S0：p.268 `of-contemporary`→`of contemporary`；p.269 `S. Toma`据印本读作`S. Tomà`、OCR `A1`核为印本脚注1、`striking'paintings`校为`striking paintings`。p.269关联的脚注1–6在本节注释段处理前仍只作为引用标记，不声称已独立核读被引来源。受控脚本`chp9_p268_migration.py`与`chp9_p269_migration.py`均以SHA、前态、自然键、精确提及跨度、原文引句及外键做预检，应用前保留四表恢复副本。

p.269首次应用后，`audit_tables.py`发现新增statement未实际写入JSONL；覆盖和提及迁移虽已写入，但此状态未作为完成结果接受。保留不完整状态副本，从p.269应用前恢复四张表，修复脚本的JSONL写入列表，重新dry-run并应用。最终审计确认全账本820段：395 reviewed/complete、61有理由排除、364 queued、0 partial；候选8,683、提及17,023、statement 7,767，`s2_missing=[]`、`errors=[]`。`tests/test_audit_tables.py`通过9项。余有两条既存`enrichment.source_ref`警告；脚本/结构审计不替代对S2语义质量的全书交接审查。下一规范段为p.270 `chp-9:09_CHP-9_sec_ii:l27-36`；全书S2仍未完成。


## 第九章印刷页270正文与注7续文待办（2026-10-01）

p.270（PDF物理第36页）正文规范段`chp-9:09_CHP-9_sec_ii:l27-36`已对照扫描处理，新增13个候选、49条精确提及和17条statement。分别记录1742年访客对Gesuati新堂、七座礼拜堂、大理石祭坛与支出的描述及其“全由施舍而来”的报告；匿名访客保持未识别。区分Tiepolo的Carmini壁画与其父/弟作品、Zais肖像及Zattere区域；将“公共施舍”限定为访客所述而不当作外部核实。L27–35正文纳入statement；L36为脚注7意大利文续文，未并入正文。

印本脚注7的标号在Gesuati公共资助句后，但现有注释文本报告Dominicans于1725年开始修建本堂。此处文本内锚点与注释对象错位，保留待复核，不将该注强作Gesuati证据。扫描校读只记S2、不改S0：`Temple ofjerusalem`→`Temple of Jerusalem`、`nobikty`→`nobility`、`Gcsuati`→`Gesuati`、`sine interior`→`fine interior`。迁移后p.270为`reviewed/partial`，访客引语续至p.271，注7续文亦待迁移。

受控迁移脚本`chp9_p270_migration.py`按来源哈希、候选自然键、提及字符跨度、statement锚点和coverage前态预检，应用前为候选、mentions、statements和coverage保存恢复副本`.bak-s2-chp9-p270-20261001`。

## 第九章印刷页271正文（2026-10-01）

p.271（PDF物理第37页）正文规范段`chp-9:09_CHP-9_sec_ii:l38-51`已对照扫描处理，新增13个候选（cand-8709–cand-8721）、50条精确提及和14条statement。p.270开头的1742年访客引语由p.271 L39–40闭合，访客身份仍未具名。另记录Dominican诸圣祭坛、Tiepolo/Piazzetta作品、Ricci祭坛画、Concina对Jesuits的攻击、Oratorians在Fava的委托、Correr任威尼斯宗主教、Capuchin教堂作品，以及Haskell对反宗教改革、耶稣会在威尼斯处境和Manin家族资金的叙述。日期、作者评价、转述与因果限定按原文保留；Piazzetta作品中的“Vincent”与Vincent Ferrer保持区分。

p.271 L51“it was specially mentioned in”尚未完句，statement标为partial并指向p.272 L54；因此p.271 coverage为`reviewed/partial`。印本校读只记S2、不改S0：`It was'not`→`It was not`，`1740.-A few`→`1740. A few`。页下注1–6保留待合并注释源段按源序迁移；本次没有据引文定位声称独立核读被引来源。

受控脚本`chp9_p271_migration.py`默认dry-run，核验源段/资产SHA-256、已有候选与ID、50条提及跨度、14条statement原文和外键、闭合p.270访客引语及续页指针；应用前为四张表保留`.bak-s2-chp9-p271-20261001`。最终审计为820段、395 complete、61 excluded、362 queued、2个未完整迁移的reviewed段；候选8,709、提及17,122、statement 7,798，`s2_missing=[]`、`errors=[]`。`python -m pytest tests/test_audit_tables.py -q`通过11项；`build_source_segments.py`预览820段、issues=0。两条既存S5 `enrichment.source_ref`警告仍在。下一规范段为p.272 `chp-9:09_CHP-9_sec_ii:l53-60`；S2全书交接条件未满足。


## 第九章印刷页272正文（2026-10-01）

p.272（PDF物理第38页）规范段`chp-9:09_CHP-9_sec_ii:l53-60`已对照扫描处理正文L54–58，新增11个候选（cand-8722–cand-8732）、36条精确提及和26条原书statement。L54的敌对小册子引语闭合p.271 L51的未完句；引文称Jesuits从一个家族抽取了教堂巨额开支，但没有在这段引文中点名该家族，故不自动认作前文的Manin家族。保留Haskell对Jesuit教堂彩色大理石、Assumption奉献、建筑/艺术隔离、Fontebasso两项天顶题材与Jesuit/ Carmelite图像关联的判断；Jesuit saints在一两幅祭坛画中缺少显著性，与S. Maria del Rosario的Dominican绘画/圣人三联配置分别记录。新增图像学term，不把建筑空间和祭坛画合并。

后半页记录Pietà旧址十四世纪的弃婴/孤儿收容机构及其受Doge、Senate直接赞助；与Pietà教堂建筑分成不同候选，并将泛称Doge office与后来具名的Doge Grimani分开。记录1745年重建决定及奠基、Gazzetta Veneta对1760年接近完工和建筑之美的引述、Haskell对官方赞助与私人/宗教团体支持的比较、Pietà Governors的筹款困难、Giorgio Massari受保守压力而采用Palladian线条、立面约150年未完工，以及Tiepolo 1754–55年《Triumph of the Faith》。该作品与p.262较宽泛的穹顶壁画候选cand-8550暂不合并，交S3身份裁决。印本校读只记S2、不改S0：L55 `hi Santa Maria Assunta`→`In Santa Maria Assunta`，L58 `Palladian Unes`→`Palladian lines`。

扫描页L59–60的Professor Wilde文字是注3续文，和合并注释来源重复；此处不重复迁移，留待合并注释段。p.272 L58的Tiepolo句续至p.273 L63，coverage保留`reviewed/partial`、源行范围L54–58；p.271段随页尾句闭合转为`reviewed/complete`。p.272脚注1–6待合并注释段按源序处理。

受控脚本`chp9_p272_migration.py`默认dry-run，校验原书资产SHA、p.272段哈希、候选序号、36条精确跨度、statement原文/外键、p.271前态及p.273续接段；写回前为候选、mentions、statements、coverage四表保存`.bak-s2-chp9-p272-20261001`。应用后账本820段：396 reviewed/complete、61有理由排除、361 queued、2 reviewed/partial；候选8,720、提及17,158、statement 7,824。`audit_tables.py`为`s2_missing=[]`、`errors=[]`；两条既存S5 `enrichment.source_ref`警告仍在；`python -m pytest tests/test_audit_tables.py -q`通过11项；`build_source_segments.py`预览820段、issues=0。下一规范段为p.273 `chp-9:09_CHP-9_sec_ii:l62-68`。全书S2交接条件仍未满足。

## 第九章印刷页273正文（2026-10-01）

p.273（PDF物理第39页）正文规范段`chp-9:09_CHP-9_sec_ii:l62-68`新增22个候选（cand-8733–cand-8754）、65条精确提及和21条statement。p.272 Tiepolo句于L63闭合并转complete。记录Tiepolo为Pietà圆顶作品所得500 zecchini、两年后向Pietà Governors出借6,000 ducats及五幅由Piazzetta学派画家创作、私人捐款支付的祭坛画；保留数量、时间和资金关系，不补造具体画名、画家或捐款人。另记录Dominican、Carmelite、Oratorian教堂绘画的侧重点，Tiepolo与Ricci作品中缺失炼狱火焰、Tassis的请求、Piazzetta初稿中的骷髅，以及Scuola del Carmine的委托压力、两套天顶图像方案、第二方案采用并略有修改、后续竞赛和Zompini获采纳的提案。Haskell的解释、推测与引文限定均保留。

扫描校读只记S2、不改S0：L64 `seem to.have`→`seem to have`、`Education os`→`Education of`；L65 `alhthere`→`all there`；L68 `inwhichartists`→`in which artists`。p.273 L68的Zompini句在p.274 L71闭合，故本段最终转complete；页下注1–5仍在合并注释段待处理。受控迁移脚本默认dry-run，核验来源/段哈希、候选顺序、65条提及跨度、statement引句/外键和coverage前态；应用前为四表留恢复副本`.bak-s2-chp9-p273-20261001`。应用后全账本820段：397 complete、61 excluded、360 queued、2 partial；候选8,742、提及17,223、statement 7,845。表审计`errors=[]`、`s2_missing=[]`，定向测试11项通过，源段预览820段且issues=0。下一正文段p.274随后处理；S2仍未交接。

## 第九章印刷页274正文（2026-10-01）

p.274（PDF物理第40页）规范段`chp-9:09_CHP-9_sec_ii:l70-78`新增15个候选（cand-8755–cand-8769）、52条精确提及和25条statement。L71闭合p.273的Zompini提案句；记录Virgin typology、1743年匿名Jesuit sermon与Pietà governors择案，继而记录Flaminio Corner的宗教赞助和生平、Giuseppe Angeli的艺术评价与Corner在S. Canciano、S. Basilio、Pietà的委托；Corner的私用作品分为Four Evangelists绘画、Apostles系列和未名圣徒画。Haskell转述、时间和评价均保留限定。

扫描校读只记录于S2：法文`reputation`据印本补重音为`réputation`；印本L75 `early paintings`后有注6，但S0 OCR遗漏标号。S0不改，`pietestic`在印本页图中亦如此，故不改为推测拼写。Corner的遗物收藏现无合适KU类型，候选留空类型；S. Basilio相对从句的“he”指代不明，不断言Corner或Angeli属于当地贵族团体。p.274页下注1–6仍待合并注释段。

受控脚本`chp9_p274_migration.py`默认dry-run，核验源资产/段SHA-256、候选ID、52条精确跨度、25条statement原句/外键、p.273跨页statement和coverage前态；应用前为候选、mentions、statements、coverage四表保存`.bak-s2-chp9-p274-20261001`。应用后全账本820段：399 complete、61 excluded、359 queued、1 partial；候选8,757、提及17,275、statement 7,870。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，但359段queued及1段partial仍阻止S2收口，另有两条既存`enrichment.source_ref`警告；`python -m pytest tests/test_audit_tables.py -q`通过11项，`git diff --check`退出码0。下一规范段为p.275 `chp-9:09_CHP-9_sec_ii:l80-83`。


## 第九章印刷页275正文（2026-10-02）

p.275（PDF物理第41页）规范段`chp-9:09_CHP-9_sec_ii:l80-83`新增3个候选（cand-8770–cand-8772）、17条精确提及和12条statement。正文记录Flaminio Corner对教堂建筑和装饰的兴趣、S. Rocco与Carità立面的建议（Haskell保留“if not with money”，不推断出资）、Corner对教堂祭坛统一材质/形制/尺度的偏好、S. Canciano作为该风格的现存实例，以及Haskell所述的祭坛构件和对照风格。S. Canciano祭坛与p.274 Giuseppe Angeli祭坛画保持不同候选。L83是注2意大利语引文及Haskell评论的脚注续文，不是正文；作为footnote continuation迁移并交叉链接至合并注释段L127，脚注开头和引文出处仍待注释段核查。

对照`CHP-9.pdf`物理第41页校读并只在S2登记：OCR `Comer`据印本为`Corner`、`Carita`→`Carità`、`os`→`of`、`exfended`→`extended`、`1778/`为注1标记、`eesere`→`essere`；S0未改。Carità具体指称仍未确定；不把脚注尾引的泛称Madonna图像作为可识别艺术作品。

受控脚本`chp9_p275_migration.py`默认dry-run，核验源资产/段SHA-256、候选顺序、17条提及跨度、12条statement引句/外键和coverage前态；应用前为候选、mentions、statements、coverage四表保存`.bak-s2-chp9-p275-20261002`。写回后全账本820段：400 reviewed/complete、61 excluded、358 queued、1 reviewed/partial；候选8,760、提及17,292、statement 7,882。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，保留两条既存enrichment `source_ref`警告；`python -m pytest tests/test_audit_tables.py -q`通过11项，`git diff --check`退出码0。S2未交接；下一段为合并注释`chp-9:09_CHP-9_sec_ii:l85-127`。

## 第九章p.270–271正文脚注标号回链复核（2026-10-02）

在处理合并注释段前，依`CHP-9.pdf`物理第36–37页复核正文断言的脚注指针。`st-chp9-p270-critic-architectural-objection`原错误挂注7；印本注1标记位于同页Tiepolo《Loreto》壁画句后，不支持该建筑批评断言，故从该statement移除`footnote_marker`与`footnote_text_pending`。`st-chp9-p271-tiepolo-st-helen-capuchin-church`原错误挂注4；印本注4位于前一句Fra Francesco Antonio Correr宗主教任职信息后，故从Tiepolo画作断言移除相同两个元数据键。断言、原文引句和其他限定不变；四表无覆盖或计数变化。受控修正脚本先dry-run核对两条statement的唯一性和预期前态，再应用并回读；原断言表恢复副本为`book-statements.jsonl.bak-s2-chp9-footnote-marker-audit-20261002`。这两项只解除错误回链；正确脚注与正文statement的对应仍待本注释段迁移后建立，coverage维持原状态。

## 第十章印刷页276–277正文（2026-10-02）

p.276规范段`chp-10:10_CHP-10_intro:l3-13`的受控迁移脚本`chp10_p276_migration.py`、表行及coverage备注现已对照；其写回在本次接续前已存在，故此处补齐过程摘要。该段新增10个候选（cand-8831–cand-8840）、33条提及和11条原书statement，扫描核读PDF物理第1页；L1标题段排除，正文L3–13完成。脚注保留在规范文件L492–494，待其后源段处理。原脚本以来源和段哈希、覆盖前态及锚点预检，四表恢复副本为`.bak-s2-chp10-p276-20261002`；另有覆盖行格式修复副本`.bak-s2-chp10-p276-range-format-fix-20261002`。本段未据索引和外部知识提前定身份，仍按既有过程记录的限定处理。

p.277规范段`chp-10:10_CHP-10_intro:l15-24`已对照`CHP-10.pdf`物理第2页语义阅读。新增11个候选（cand-8841–cand-8851）、66条精确提及和25条statement。分别记录Maximilian的1704年肖像委托、Christian Louis及仅以头衔出现的Palatine Elector之类似委托与邀请、Frederick IV的1709年访问和十二幅粉彩、Carlevarijs所绘荣誉赛舟图、Saxon Elector/Augustus III的到访及Rosalba作品收藏、Haskell对Venice城市／共和国／居民的不同表述、Crozat与Rosalba的粉彩／交换承诺／1721年巴黎访问，以及外国使节可能委托记录入城景象的关系候选。印本索引将Palatine Elector定位为Johann Wilhelm，但正文只给头衔；跨章身份仍留给S3。城市Venice与政治实体Republic of Venice分列；未具名的收藏因当前taxonomy没有collection类型，保留类型空值待决。

印本确认OCR行首`’`不属于“easily”一词，校读仅写入S2；扫描确实印作`not-an. impoverished`，故保留其异常标点并依句法记录为对“贫困共和国”说的否定，不擅改S0。p.277注1–5合并存于同文件L495–499，暂留待办；L24的“but for other and more important”未完句跨至p.278 L27，故p.277维持`reviewed/partial`，statement带续页锚点，不预断后文的口味分歧。

脚本`chp10_p277_migration.py`默认dry-run，固定来源资产及段SHA-256、候选序号8840、前后段coverage状态，逐条校验提及跨度、statement引句、候选外键和ID唯一性；应用前为候选、mentions、statements、coverage四表留副本`.bak-s2-chp10-p277-20261002`。应用后审计账本820段：403 reviewed/complete、62 excluded、354 queued、1 reviewed/partial；候选8,839、提及17,478、statement 7,985，`s2_missing=[]`、`errors=[]`。定向`test_audit_tables.py`通过；源段生成预览74个规范来源文件、820段、issues=0；`git diff --check`退出码0（仅报告既有LF/CRLF提示）。仍有两条既存enrichment `source_ref`警告，且queued与partial继续阻止S2交接。下一段为p.278 `chp-10:10_CHP-10_intro:l26-41`。

## 第十章印刷页278正文（2026-10-02）

p.278规范段`chp-10:10_CHP-10_intro:l26-41`对照`CHP-10.pdf`物理第3页完成语义处理。新增32个候选（cand-8852–cand-8883）、72条精确提及和32条原书statement。记录德意志诸宫廷继续购买意大利艺术、强势宫廷吸引艺术家及其作品、哈布斯堡召画家与宫廷任职、Bencovich所指“them”未决、Diziani赴Dresden、Amigoni在Munich/Nymphenburg的创作；另记录英国赞助环境、Whig贵族、Manchester 1709年威尼斯使馆叙述、其交游圈、Duchess of Marlborough关于音乐的嵌套引文，以及Manchester安排Pellegrini和Marco Ricci为Scarlatti《Pyrrhus and Demetrius》绘制布景。拆分两位艺术家的委托断言，不推定布景已完成或存世。

本页闭合p.277 L24句，p.277 coverage转complete；p.278 L41“and then to”续至p.279 L44，故p.278暂列partial。p.276“a year later”与p.278所记1709年使馆/返英时间的关系未解决。扫描确认L34 “poets”后印本注号为5、S0 OCR为6；仅在S2记校读，S0不改。p.278注1–6仍待后置合并注释段按源序处理。

`chp10_p278_migration.py`默认dry-run并锁定源资产/源段哈希、候选序号、提及跨度、statement原文/外键及相邻coverage前态。写入前备份四表为`.bak-s2-chp10-p278-20261002`；另留覆盖行格式修复副本`.bak-s2-chp10-p276-range-format-fix-20261002`。p.278写入后审计为404 complete、62 excluded、353 queued、1 partial，候选8,871、提及17,550、statement 8,017；`s2_missing=[]`、`errors=[]`。该快照是本段写回时状态，随后p.279又有更新。

## 第十章印刷页279正文（2026-10-02）

p.279规范段`chp-10:10_CHP-10_intro:l43-49`对照`CHP-10.pdf`物理第4页处理，新增26个候选（cand-8884–cand-8909）、61条精确提及和24条statement。闭合p.278关于Manchester布景后续装饰宅邸的跨页句，并分别记录Pellegrini、Marco Ricci受雇装饰的关系候选；记录Vanbrugh为Lord Carlisle兴建Castle Howard、Carlisle雇用两位威尼斯画家、两人由Castle Howard转至Narford Hall、Narford Hall与Andrew Fountaine的关系及其收藏家/鉴赏家身份。艺术史内容保留为Haskell判断：Pellegrini在英格兰时期的风格描述、Van Dyck肖像的影响、Pierre Motteux素描与conversation-piece比较、Marco Ricci音乐群像可能影响Hogarth、1712年Pellegrini与Marco Ricci争执/离英、Marco携叔父Sebastiano返英，以及Sebastiano的赞助背景和风格对比。Pellegrini—Marco duo与Marco—Sebastiano duo分开建候选，避免将“the two men”误接前组。Lord Portland为Sebastiano早期雇主的句子续至p.280 L52，故p.279保持partial。

页图确认OCR在L48截断“Plate 47”尾部、L49把“work.”与“Sebastiano”之间误插撇号；校读只登记于S2、不改S0。L48的“private”单引号与扫描一致，不作OCR更改。p.279注1–3对应Watson、Vertue及《Mostra di Pellegrini》，只记录引文定位，尚未独立阅读；仍待其合并注释源段处理。p.276–279脚注均按源序留待相应规范注释段。

`chp10_p279_migration.py`默认dry-run，固定源资产/段哈希、候选序号、提及字符跨度、statement引句/外键及前后段coverage状态；应用前为候选、mentions、statements、coverage四表留副本`.bak-s2-chp10-p279-20261002`。应用后账本820段：405 complete、62 excluded、352 queued、1 partial；候选8,897、提及17,611、statement 8,041。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；定向`test_audit_tables.py`退出码0，`git diff --check`退出码0（仅有既存换行符提示）。两条既存S5 `enrichment.source_ref`警告仍在；全书S2仍未完成，下一段为p.280 `chp-10:10_CHP-10_intro:l51-61`。

## 第十章印刷页280正文（2026-10-02）

p.280规范段`chp-10:10_CHP-10_intro:l51-61`对照`CHP-10.pdf`物理第5页处理，新增30个候选（cand-8910–cand-8939）、79条精确提及和25条statement。p.279 L49 Portland句由L52闭合，补录其此前委托Pellegrini绘画；另记Portland与William Bentinck、William III和Orange cause的关系，1709年继承Portland头衔、1716年受封第一代公爵、Rigaud肖像及匿名当代人的引语。分别记录Ricci为Portland的town house及Bulstrode Park chapel创作/受委托的四件作品、Catholic church比较和Vertue评价。

随后记录Sebastiano Ricci在Burlington的赞助下创作、May 1715 Piccadilly mansion改建和大量意大利绘画偏好、Palladianism兴趣尚未形成、John Gay对Burlington House的引语、墙面/天花板绘画及其后迁往Chiswick的来源说法；脚注7将迁移限定为probable，需在注释段完成回链。另录Whig贵族和官员赞助、Chelsea Hospital《The Resurrection》壁画、Bellucci到英后的接待与John Sheffield patronage、Sheffield的政治立场、James II女儿婚姻及Prince Eugene评价的未完引入。对隐含主语和跨页代词逐项回指，不给无名女儿、匿名评论者或未名建筑补造身份。

页图校读仅记S2、不改S0：L53 `William Ill`→`William III`；L55 `Cathode`→`Catholic`；L60 `some'of`→`some of`，且p.280 L60印本注号6被OCR识为8；L61 `biave`→`have`。脚注1–8仍待本章合并注释段依源序迁入；被引Vertue、Turberville、Wittkower、Charlton、Complete Peerage等仅作本书引文定位，未独立阅读。p.280末句“described by Prince Eugene in”续至p.281 L63，故p.280保持partial。

`chp10_p280_migration.py`默认dry-run，锁定来源资产/段SHA-256、候选序号、提及跨度、statement引句和外键以及前后段coverage状态；应用前四表副本为`.bak-s2-chp10-p280-20261002`。p.279转complete、p.280转partial。应用后账本820段：406 complete、62 excluded、351 queued、1 partial；候选8,927、提及17,690、statement 8,066。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，定向`test_audit_tables.py`退出码0，`git diff --check`退出码0（仅既存LF/CRLF提示）。两条既存S5 `enrichment.source_ref`警告仍在；全书S2未完成，下一段为p.281 `chp-10:10_CHP-10_intro:l63-89`。

## 第十章图版49–52与p.280续接校正（2026-10-02）

对照`CHP-10.pdf`物理页6–9，确认p.280之后先出现Plate 49–52图版页，正文到规范源文件L125（印刷p.281）才恢复； Prince Eugene描述接在L126。因此修正statement `st-chp10-p280-sheffield-description-open`的续接锚点为`chp-10:10_CHP-10_intro:l125-139` L126，并同步更正p.280 coverage注记。原`l63-89`是Plate 49，不能作为p.281正文引用。

新增派生来源`10_CHP-10_intro_plates_visual-transcription.md`，保留原OCR/PDF不改写；源段账本由820增为824。OCR段`l63-89`、`l91-112`、`l114-119`及`l121-123`完成核读，四个视觉转录段一并迁入。Plate 49、51、52题注复用已有图版目录候选并新建21条精确mention、16条statement；Plate 50只记录编辑性组题与无独立图注，不从图像推断作品事实。McSwiney/McSwiny拼写差异保留待S3处理；题注的年代、地点、纪念对象、归属均留在原书题注层级。

`chp10_plates49_52_migration.py`默认dry-run，核验四段OCR与四段视觉转录哈希、21条mention跨度、16条statement引句/外键、引用图版目录行及coverage前态；应用前三表恢复副本`.bak-s2-chp10-plates49-52-20261002`。源表审计为824段、414 complete、62 excluded、347 queued、1 partial；候选8,927、提及17,711、statement 8,082；`s2_missing=[]`、`errors=[]`。`build_source_segments.py`预览75个来源文件、824段、issues=0；`tests/test_audit_tables.py`通过，`git diff --check`退出码0（保留既有换行符提示）。下一规范段为p.281正文`chp-10:10_CHP-10_intro:l125-139`；p.276–280脚注仍待按源序处理，全书S2尚未收口。

## 第十章印刷页281正文（2026-10-02）

p.281（PDF物理第10页）规范段`chp-10:10_CHP-10_intro:l125-139`新增11个候选（cand-8940–cand-8950）、78条精确提及和23条statement。闭合p.280 Prince Eugene对Sheffield的评价；记录Sheffield与Queen Anne、Bellucci装饰及Chandos/Canons、其居所和礼拜堂、Handel/Pepusch音乐会、英格兰威尼斯画家赞助语境、Pellegrini/Ricci/Bellucci评价、Damini/Leoni及Johann Wilhelm在Palatinate的统治。保留说话者、转述、作品身份与日期限定；不将艺术家集体或未名作品过早拆为确定实体。p.281 L139关于严重叛乱的句子续到p.282 L142，故该段当时保持partial。

写回经dry-run校验源资产和段哈希、候选序号、提及跨度、statement引句/外键及coverage前态；四表留存恢复副本`.bak-s2-chp10-p281-20261002`。p.280已转complete。印本校读只记S2、不改S0；注1–2对应规范来源L518–519，留待合并注释段处理。

## 第十章印刷页282正文（2026-10-02）

p.282（PDF物理第11页）规范段`chp-10:10_CHP-10_intro:l141-149`新增1个作品候选（cand-8951）、38条精确提及和14条statement。L142闭合p.281 Johann Wilhelm上台及平叛句；分别记录其1708–1714年德国政治影响、Palatinate成为大国的可能性、艺术家对其的赞颂、Rapparini嵌套引语和对Alexander the Great的比较，以及Gabriel Gruppello青铜骑马像。另记Rapparini关于绘画的引文、其对Johann Wilhelm赞助的引导、婚姻背景、收藏意大利作品、四位受雇画家及Balestra/Carriera邀请。保留Haskell的“可能”“无疑”等作者判断和Rapparini引语层次；不把失败邀请写成到访。

对照印本只在S2登记校读：L142 OCR `Giorgio MariaRapparini`→`Giorgio Maria Rapparini`；L143、L148 `Dusseldorf`→`Düsseldorf`；L148 `Rosalba Camera`→`Rosalba Carriera`。p.282脚注1–3对应规范来源L520–522，待注释源段处理。L149是无编号脚注/页脚片段，印本止于“refused regular”；缺失续文和注号均不推断，因此coverage保持`reviewed/partial`。

`chp10_p282_migration.py`默认dry-run，固定来源与源段哈希、前后coverage状态、候选序号、38条提及跨度及14条statement原句/外键；应用前四表恢复副本为`.bak-s2-chp10-p282-20261002`。p.281转complete，p.282为partial。写回后全账本824段：416 reviewed/complete、62 excluded、345 queued、1 reviewed/partial；候选8,939、提及17,827、statement 8,119。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，仍有两条既存enrichment `source_ref`警告；`tests/test_audit_tables.py`通过9项；`build_source_segments.py`预览75个来源文件、824段、issues=0；`git diff --check`通过（保留LF/CRLF提示）。下一段为p.283 `chp-10:10_CHP-10_intro:l151-165`。全书S2未收口，不能交接S3。

## 第十章印刷页283正文及p.282脚注续接（2026-10-02）

p.283规范段`chp-10:10_CHP-10_intro:l151-165`对照`CHP-10.pdf`物理第12页完成本轮语义处理。新增5个候选（cand-8952–cand-8956）、59条精确提及和14条p.283 statement；另新增2条p.282脚注续文statement。候选覆盖Alte Pinakothek、Bensburg城堡、Pellegrini寓意画组、Bellucci作品集合及Lankheit书目引文线索。Lankheit 1956 pp.185–210仅映射至书目定位，不充作独立证据。印本对照校读：L153 `Van det Werff`→`Van der Werff`、L156 `Aencreux`→`généreux`、L157 `Tamour`→`l’amour`、L163 `Eves`→`lives`及`Bibhoteca`→`Biblioteca`；Bensburg按印本原样保留，不推测改字。

p.282 L149无编号页脚在p.283 L163–164脚注区续为“employment under him—see the manuscript lives ... MSS. 1383.”据此分别记录Trevisani与Balestra拒绝Johann Wilhelm麾下常规任职，未猜脚注编号。p.282转complete。p.283 L163 Bellucci句以“but”未完，续至p.284 L167，故coverage保持partial。规范注释源段L523的notes 1–2尚未处理，仍待合并注释段按源序迁移。

受控脚本`chp10_p283_migration.py`默认dry-run，核验来源资产与源段哈希、候选顺序、59条提及跨度、statement原句/外键、跨页脚注语句及coverage前态；写入前四表恢复副本`.bak-s2-chp10-p283-20261002`。应用后全账本824段：417 reviewed/complete、62 excluded、344 queued、1 reviewed/partial；候选8,944、提及17,886、statement 8,135。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，保留两条既存`enrichment.source_ref`警告；`tests/test_audit_tables.py`通过9项；源段预览75个规范来源文件、824段、issues=0；`git diff --check`退出码0。下一段为p.284 `chp-10:10_CHP-10_intro:l167-176`；全书S2仍未收口，不能交接S3。

## 第十章印刷页284正文（2026-10-02）

p.284规范段`chp-10:10_CHP-10_intro:l167-176`对照`CHP-10.pdf`物理第13页完成语义处理。新增10个候选（cand-8957–cand-8966）、48条精确提及和19条原书statement。L168闭合p.283 Bellucci“allegories and group portraits ... but”句：Haskell称这些作品虽较Pellegrini笨拙，却显示Bellucci较早欣赏Veronese。新增/复用对象覆盖Amsterdam City Hall及Pellegrini未具名壁画委托、Low Countries/Antwerp/Amsterdam、Lord Cadogan和未名country house、The Hague、Sebastiano Ricci、Pierre Crozat与Rue Richelieu宅邸、Charles de la Fosse、Antoine Watteau及被Ricci临摹的未名图纸、Carriera、Zanetti、Mississippi Gallery、Banque Royale及John Law的Système。未把Cadogan宅邸放在The Hague，也未把受托装饰写成已完成；Crozat旧宅候选复用p.277条目。

段内记录Pellegrini在Elector去世后赴Low Countries的Haskell推断、Amsterdam市政厅壁画委托及“首位在Holland创作的意大利艺术家”主张；Pellegrini 1719年短期返英为驻海牙大使Cadogan装饰乡间住宅的任务；Ricci 1716年离伦敦赴巴黎；Crozat的藏画/图纸、艺术家交游与接待；La Fosse对Ricci的评价；Ricci临摹Watteau图纸；四年后Pellegrini携Carriera、Zanetti访法；以及Mississippi Gallery委托和皇家颂扬/商业寓意并置的未完句。保留Haskell的历史判断、作品身份限制和委托/完成区别。

页图校读只记于S2，S0不改：L169 `1716?`是注号2而非问号；`rime`→`time`、`who -had`→`who had`；L172 `eopy`→`copy`并删OCR多出的尾随撇号；L174 `This visit, marked`校为`This visit marked`、`the'task`校为`the task`。p.284注1–5位于合并来源L524–527，均留待第十章注释源段按序迁移；脚注引文只作定位，不当作独立核验。

受控脚本`chp10_p284_migration.py`默认dry-run，校验来源与段SHA-256、前后coverage、候选序号、提及精确跨度及statement引句；应用前候选、mentions、statements、coverage四表留存`.bak-s2-chp10-p284-20261002`恢复副本。首次审计发现Pellegrini委托statement的末行范围少记一行，已将`source_line_end`从175修正为176并留`.bak-s2-chp10-p284-quote-fix-20261002`。当前全账本824段：418 complete、62 excluded、343 queued、1 partial；候选8,954、提及17,934、statement 8,154。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，仍有两条既存`enrichment.source_ref`警告；定向测试10项通过；源段预览75个文件、824段、issues=0；`git diff --check`退出码0。p.284末句续至p.285 L178；全书S2仍未收口，不能交接S3。

## 第十章印刷页285正文（2026-10-02）

p.285规范段`chp-10:10_CHP-10_intro:l178-188`对照`CHP-10.pdf`物理第14页完成语义处理，新增16个候选（cand-8967–cand-8982）、47条精确提及和18条原书statement。L179闭合p.284 Mississippi Gallery寓意方案句。记录委托说明中的法文短引、King/Religion/Régent与Commerce/Wealth/Security/Credit及Olympian virtues的图像配置、Seine与Mississippi相拥、Bourse/港口/船只图像；单独记录委托壁画在Système崩溃后不久毁坏、Mariette后来的褒贬以及Haskell对其法国绘画影响的限定判断。图像拟人角色/视觉身份不套用person或work，当前类型不适配的项目保持类型待决；河流、画廊、金融方案分开。

同页记Pellegrini在巴黎的其他作品及至少一幅未名祭坛画；Carriera受Crozat接待和肖像委托、named sitters、Académie入选引语、与Rigaud/Watteau等人的交往，以及离开巴黎的时间和Haskell对其风格影响的评价。Portrait sitter身份和Académie正式全名留待S3；引用信件、Mariette与其他注释出处未独立核读，脚注1–4在合并注释段L528–531待处理。新节行L188的`— ii —`为版面分隔，不迁入正文断言。

页图校读仅写S2、不改S0：L181 `saidThat`→`said that`；L184删去`her`前多出的OCR撇号；L187 `a. number`→`a number`、`intiniate`→`intimate`；L188拆开居中的节号并将`Diisseldorf`校为`Düsseldorf`。受控脚本`chp10_p285_migration.py`默认dry-run，锁定来源和段SHA-256、覆盖前态、候选序号、精确提及跨度及statement引句；写入前四表恢复副本`.bak-s2-chp10-p285-20261002`。审计首次发现Carriera portrait-response statement的引用行尾少一行，已把`source_line_end`由184更正为185，留`.bak-s2-chp10-p285-quote-fix-20261002`。写回后全账本824段：419 complete、62 excluded、342 queued、1 partial；候选8,970、提及17,981、statement 8,172。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，仍有两条既存`enrichment.source_ref`警告；定向测试10项通过，源段预览75个文件、824段、issues=0，`git diff --check`退出码0。p.285 L188新节开篇续至p.286 L190；S2未收口，不能交S3。

## 第十章印刷页286正文（2026-10-02）

p.286规范段`chp-10:10_CHP-10_intro:l190-204`对照`CHP-10.pdf`物理第15页完成逐句语义处理。初迁入22个候选（cand-8983–cand-9004）、50条精确提及和17条原书statement；跨候选审查发现cand-8984“Venetian artists”与既有cand-8104重复，已移除cand-8984并将其提及映射至cand-8104，故本页净增21个候选（cand-8983、cand-8985–cand-9004），全库候选8,991。L191闭合p.285句；p.286末句在L204“gave the job to”处未完，续至p.287 L207，coverage因此为partial。核心内容包括Galilei嵌套引语及Haskell限定、Thornhill取得St Paul's dome和Queen's Bed Chamber绘画、Halifax的Treasury付款警告、Burlington建筑风格和Grand Tour对英格兰品味的作者判断；Amigoni在Tankerville、Powis House和Styles/Moor Park的委托，Powis赞助身份仍不确定，房间/建筑/装饰作品分开建候选，未具名的Prince of Wales、法国大使和法国国王身份不猜定。

扫描校读只记S2、不改S0：L200 `James H`→`James II`，`King-of France`→`King of France`；L201 `house of Lords`→`House of Lords`。p.286注1–3对应Toesca、Vertue、Dictionary of National Biography及Wheatley，已标为待合并注释源段迁移/未独立阅读。初次结构审计发现三条statement的source line span少覆盖跨行引用起始/续行，并有两组提及偏移重叠；已修正主迁移脚本，受控修复脚本`chp10_p286_anchor_repair.py`保留修复证据及恢复副本。候选去重用受控脚本`chp10_p286_candidate_dedupe.py`处理，备份保留。去重后p.286时点全账本824段：420 complete、62 excluded、341 queued、1 partial；候选8,991、提及18,031、statement 8,189。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，两条既存`enrichment.source_ref`警告仍在；定向测试通过，源段预览75个文件、824段、issues=0。p.287继续闭合该页末句；全书S2仍未完成，不交S3。

## 第十章印刷页287正文及p.286跨页闭合（2026-10-02）

p.287规范段`chp-10:10_CHP-10_intro:l206-216`对照`CHP-10.pdf`物理第16页完成语义阅读与迁移。p.286 L204–207闭合Styles委托句：争执后工作交给Amigoni与Francesco Sleter。复用既有Moor Park decoration候选cand-9004，将四幅无独立题名的Jupiter与Io画作为该委托语境的具体内容，不另建重复作品候选；登记7个新候选（cand-9005–cand-9011）、30条精确提及和15条statement。新候选覆盖Fielding《Joseph Andrews》、McSwiny未实现的Van Dyck肖像版画计划、其代Lord March提出的寓意墓葬方案、1688 Glorious Revolution、墓葬计划中的匿名意大利画家群体、Woodward 1957年文章及注2所引但书目身份未明的Haskell 1960文献。McSwiny、Lord March/Duke of Richmond、Fielding、Amigoni、Sleter、Nazari、Van Dyck、Jupiter、Io及Vertue均优先复用现有候选。

逐句保留Haskell对四幅画的审美判断；Amigoni转向肖像、离英时间“约十年”、据称带走£4,000–£5,000及部分收入来自宫廷工作的限定；对英国延聘威尼斯画家及题材类型的概括和“少有例外”；McSwiny爱尔兰身份、舞台职业、失败的版画计划、约1711年因债务前往欧洲大陆、数年后重现及其原创方案。Lord March后来成为Duke of Richmond的同文身份沿用单一候选；墓葬方案明确记作提议，不推断实际完成。Haskell关于军事、政治和知识成就、1688年后进步及“庆祝时机”的解释作为作者判断记录；“wealth at home and peace in Europe...”未完句保留partial并链接p.288 L219。注2在本段包含，印本标号为2、S0 OCR误作`?`；印本金额为£4,000–£5,000，`story'of`校作`story of`，`Verrue`校读为`Vertue`，仅记录在S2、不改S0。注1、3–6仍待合并注释源段处理；注2所引文献未独立阅读，Fielding列出的虚构画家名未建候选。

受控脚本`chp10_p287_migration.py`默认dry-run，锁定来源/段SHA-256、候选序号、30条提及跨度、15条statement引句与外键、相邻coverage前态，并为四表留`.bak-s2-chp10-p287-20261002`。首次审计发现McSwiny职业句引文延伸至L212但行号只标到L211，已由`chp10_p287_quote_repair.py`修正并留恢复副本。审计复核后全账本824段：421 complete、62 excluded、340 queued、1 partial；候选8,998、提及18,061、statement 8,204。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；两条既存enrichment `source_ref`警告和S2未收口警告仍在；`tests/test_audit_tables.py`通过，`build_source_segments.py`预览75个来源文件、824段、issues=0。下一段为p.288 `chp-10:10_CHP-10_intro:l218-227`；全书S2未收口，不交S3。

## 第十章印刷页288–289过程补记（2026-10-02）

此前p.288已在当前结果文件登记，但过程流水线在p.287处中断；为保持过程记录连续，补记p.288迁移。p.288按物理第17页扫描读正文，明确McSwiny纪念方案的意向性、Haskell对成功前景与政治范围的推断、引语层次和图像格式；未把方案描述成全部完成的作品，也未把匿名例外人物强行识别。p.288末尾四位威尼斯画家职业起步句停在“All four Venetian artists were beginning their”，留下跨页待闭合。脚注1–3全篇合并在L540–542，暂留给合并注释源段，避免正文段和注释段重复迁移。控制脚本`chp10_p288_migration.py`固定源资产/段SHA、候选序号和相邻覆盖状态，应用前保存四表备份`.bak-s2-chp10-p288-20261002`；当时结果见`03-processing/.../results/stages.md`对应p.288条目。

p.289按`CHP-10.pdf`物理第18页校读。跨页句在L230闭合：Haskell称四位威尼斯画家处于职业生涯早期、Canaletto尚鲜为人知。Ricci兄弟和Devonshire纪念画分别按人物索引子目登记，并新增未具题名的单幅作品候选；关系候选暂留S2 statement，不写正式关系。Haskell关于高额费用的句子是带“must have”的推断与价值判断；1722年前已启动15幅、后来大部分归Richmond公爵所有，则以Haskell叙述登记，并由注2待读说明归属清单存在混乱。保留“作品虽吸引人但未达保存British Worthies记忆之目的”的作者评价与所引计划宗旨；另将一般capricci绘画类型与已有的特定术语`Capriccio pittoresco`分开。p.289 L232的picturesque/Memento Mori句在p.290 L241闭合，只核对了该续行，不将p.290其余正文提前迁移。页下注1–2在本页OCR L233–238只是重复/截取片段，完整内容统一在合并注释L543–544；本轮不重复创建脚注对象或外部证据。

迁移脚本`chp10_p289_migration.py`默认dry-run，核验资产与段哈希、候选顺序、相邻coverage前态、15条提及跨度、8条statement原文/外键及p.290 L241跨页续文；应用前备份候选、提及、statement和coverage四表为`.bak-s2-chp10-p289-20261002`。审计结果：全账本824段，423 complete、62 excluded、338 queued、1 partial；候选9,004、提及18,118、statement 8,229；`s2_missing=[]`、`errors=[]`；定向测试9项通过。两条既存enrichment `source_ref`警告仍在；一段partial是本次有意保留的p.289脚注摘段待办。下一源段为p.290 `chp-10:10_CHP-10_intro:l240-251`。

## 第十章印刷页290正文及statement写回修复（2026-10-02）

p.290（PDF物理第19页）正文`chp-10:10_CHP-10_intro:l240-251`对照页图处理；新增14个候选（cand-9018–cand-9031）、45条精确提及和24条statement。闭合p.289 L232的picturesque/Memento Mori句，分别登记一般capricci类型和Memento Mori主题；记录1729年客户对两幅变更版本及Lord Bingley持有状态的转述、Goodwood陈列与解释说明、Haskell对1688纪念目的的判断、McSwiny对狭幅叙事和Marlborough纪念像的说明、Richmond与Morice的购藏、Fratta绘图及1730年代订阅计划。Brutus与Roman Admiral保留为未定类型图像角色；收购数量、作品版本、信件来源和题注身份均保留原书归属及注释待处理状态。扫描确认书名为`The Gierusaleme Liberata`。

首次p.290写回后的全表审计发现脚本已写候选和提及，却遗漏将24条新statement追加到`book-statements.jsonl`。当时结果未作为完成状态保留。先把当时四表存为`.bak-s2-p290-p291-before-rebuild-20261002`，再恢复已核验的p.290前四表副本；修正`chp10_p290_migration.py`写入`statements+new_s`，依序重新运行p.290和p.291脚本。重新执行各保留恢复副本`*.bak-s2-chp10-p290-reapply-20261002`、`*.bak-s2-chp10-p291-reapply-20261002`。全表复审确认24条p.290 statement现已写入且无重复。

## 第十章印刷页291正文（2026-10-02）

p.291（PDF物理第20页）正文`chp-10:10_CHP-10_intro:l253-266`新增7个候选（cand-9032–cand-9038）、31条精确提及和12条statement。区分p.290订阅计划中的五十版与1741年出版的`Tombeaux des Princes…`实刊；记录实刊十八版、九座来自Richmond收藏的寓意墓、Lord Dorset与Isaac Newton两份Characters、缺失的三朝纪事、铭牌制作及Haskell审美/历史判断。记录McSwiny与Joseph Smith经手Carriera粉彩和Canaletto风景，以及McSwiny对Canaletto画作的书信评价。Queen Mary、King George、Lord Dorset及“British Nation”保留身份/类型待决；不把实刊信息回填成计划规格。

页图核验书名`siècle`重音、`Rosalba Carriera`拼写（S0 OCR作`Garriera`）；校读只记S2，不改S0。正文称书信写于1727年，但页下注3称致John Conduitt书信日期为1730年9月27日；冲突保留，等待合并注释源段`L551–553`按序迁移。正文末句L266“he commissioned a number of”待p.292 L268闭合，故p.291 coverage为partial；注1–3不在正文段重复迁入。

受控脚本`chp10_p291_migration.py`默认dry-run，锁定来源资产/段哈希、候选序号、页码、提及精确跨度、statement引句及前后coverage状态。当前全账本824段：424 reviewed/complete、62 excluded、336 queued、2 reviewed/partial；候选9,025、提及18,194、statement 8,265。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；两条既存`enrichment.source_ref`警告仍在。下一规范段为p.292 `chp-10:10_CHP-10_intro:l268-277`。

## 第十章印刷页292正文（2026-10-02）

p.292（PDF物理第21页）正文`chp-10:10_CHP-10_intro:l268-277`完成语义阅读并迁移，新增18个候选（cand-9039–cand-9056）、54条精确提及和21条statement。闭合p.291 L266 McSwiny委托Canaletto为英国客户作画的跨页句；区分Grand Tour带回的威尼斯景观画与Canaletto在英绘制的伦敦/乡间住宅系列，保留匿名画家学生、旅行者与委托群体。分别记录Burney和Beckford对Canaletto威尼斯图像的引文层；1740年未名欧洲战争、Amigoni鼓励Canaletto赴英及其衡量英国趣味的经历；Canaletto的英语市场、英国委托与近十年驻英经历、Rowlandson对其人物速写方式的改编；Zuccarelli在英年限、George III客户和Royal Academy创始成员身份；Haskell关于英欧趣味变化的判断；Pellegrini Banque Royale天顶画于1724年被毁、法国收藏者对当代意大利艺术兴趣及意大利艺术对法国艺术家的影响；Count Tessin的瑞典身份、未名建筑师父亲、斯德哥尔摩王宫、出生/旅行年代及初识Watteau。未将1740战争强行识别为具体战争，也未为匿名人物、群体、作品、王宫父亲补姓名或具体身份。

页图核对S0 OCR错误，仅在S2保留校读：`George HI`→`George III`；`bis early travels`→`his early travels`；Zuccarelli carreira后的脚注号OCR作6、印本为5。引文中的`Canaletti`保留原拼写并映射Canaletto候选，不改引文。p.291正文的1727年书信日期与注3所引1730年John Conduitt信仍冲突；p.291注1–3（L551–553）及p.292注1–6（L554–557）现已从第十章合并注释段迁移并链接正文statement。相应引文只记录为原书引证，未独立核验。

`chp10_p292_migration.py`默认dry-run，校验源文件SHA-256、规范段SHA-256、候选序号、相邻coverage状态、索引候选、提及精确跨度和statement原句。首轮全表审计拒绝将跨页完整引句挂在p.291覆盖段外；保留恢复副本后恢复四表，改为在p.292 L269保存段内引句并以cross-reference回链p.291，再受控应用。恢复副本`.bak-s2-chp10-p292-20261002`与`.bak-s2-chp10-p292-reapply-20261002`均保留。当前全账本824段：425 reviewed/complete、62 excluded、335 queued、2 reviewed/partial；候选9,043、提及18,248、statement 8,286。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；仍有两条既存enrichment `source_ref`警告及预期的335 queued/2 partial提示；`tests/test_audit_tables.py`退出码0。p.291转complete，p.292因L277末句续至p.293保持partial；下一规范段为p.293 `chp-10:10_CHP-10_intro:l279-290`。全书S2仍未收口，不能交接S3。

## 第十章印刷页293–294正文（2026-10-02）

p.293正文`chp-10:10_CHP-10_intro:l279-290`新增18个候选（cand-9057–cand-9074）、60条精确提及和21条statement。记录Count Tessin的1728年任职与采购、1739年驻法经历、巴黎收藏和Boucher相关叙述（保留“apparently”限定）、Tiepolo评价信及个人收藏、Gai与法国雕塑家语境、Tessin在威尼斯的交往、柏林意见和德国赞助变化。匿名国王、群体、作品、信件和Taraval身份保留待决；页末“in-1725”待下页闭合。扫描校读仅记S2：`sur turtrès`→`sur un très`、`quelle`→`qu’elle`、`InfortunLtel Ite`→`Unfortunately he`、`seared`→`feared`、`Diisseldorf`→`Düsseldorf`、`Rosalba Camera`→`Rosalba Carriera`；S0未改。受控迁移脚本默认dry-run并锁定源资产/段哈希、相邻coverage、候选序号、提及跨度及statement锚点。p.293处理后全账本为426 complete、62 excluded、334 queued、2 partial；候选9,061、提及18,308、statement 8,307。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，定向测试9项通过；两条既存S5 `enrichment.source_ref`警告和未收口提醒保留。

p.294正文`chp-10:10_CHP-10_intro:l292-302`对照`CHP-10.pdf`物理第23页新增23个候选（cand-9075–cand-9097）、79条精确提及和23条statement，完成Pellegrini 1725年前往Dresden的跨页句；记录Augustus II court/建筑赞助、Gaspare Diziani、Zwinger项目、Pellegrini和Sebastiano Ricci教堂作品、Antonio Zucchi与print cabinet、Pittoni两件作品及Negri/Benefial版本、Migliori/Molinari/Bellucci作品、Augustus III与Count Brühl收藏、Guarienti和Dresden Gallery、Modena藏画、Rossi兄弟代理活动及Marco Ricci景观画。城市/建筑、艺术作品和机构分开；未名教堂、收藏、画柜、Modena公爵和代理人保留未决类型/身份。p.294脚注1–3与合并注释段L491–634回链，尚未独立核查其中引文来源。页末Algarotti句止于“especially to”，待p.295闭合；印本核对未见需补录的S2文字校勘。

脚本`chp10_p294_migration.py`默认dry-run，核验资产和规范段SHA-256、既有索引候选身份、相邻coverage、提及跨度及原书statement引句/外键。写回后全表首次发现Guarienti/Dresden Gallery statement的源行范围漏掉p.294 L298；修正为L298–299并保留恢复副本`book-statements.jsonl.bak-s2-chp10-p294-anchor-fix-20261002`。最终`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全账本824段：427 complete、62 excluded、333 queued、2 partial；候选9,084、提及18,387、statement 8,330。定向测试`tests/test_audit_tables.py` 10项通过，`git diff --check`退出码0（仅有LF/CRLF转换提示）。p.293转complete，p.294保持partial；下一源段为p.295 `chp-10:10_CHP-10_intro:l304-316`。全书S2仍未收口，不能交接S3。

## 第十章印刷页295正文（2026-10-02）

p.295（PDF物理第24页）规范段`chp-10:10_CHP-10_intro:l304-316`完成完整语义阅读与页图对照。迁移新增19个候选（cand-9098–cand-9116）、73条精确提及和32条原书statement。L305闭合p.294 Algarotti于1743年回威尼斯为Augustus III购画的句子；本页记录Algarotti对Tiepolo、Piazzetta、Amigoni、Pittoni及仅以姓氏出现的Zuccarelli所涉委托，并区分Augustus III从私人收藏购入的作品组、Piazzetta《Standard Bearer》、Ricci神话画及Nogari/Nazari肖像和fantasy heads。另记录Carriera的肖像/寓意/宗教题材、早期pastel购藏和超过150件作品的数量下限；Felicita Sartori与未名议员的婚姻及其1741年来到Dresden为Augustus III工作；Bellotto的Dresden court任职、城市景观画、不同尺寸的客户、1765年返Dresden及其Church of the Cross废墟画；Clemens August的头衔、与未名Bavaria Elector的手足关系及访Venice经历。分开登记人物、作品组、教堂建筑、宫廷职位和轰炸事件；没有为匿名议员、Bavaria Elector、Zuccarelli补全身份。相对关系从句“who had employed Amigoni”的先行词保留未决，不转成确定雇佣关系。

页图校读只记S2，不改S0：`Count Briihl`→`Count Brühl`；`ofhis`→`of his`；正文Venice后OCR脚注号6据印本为5。注1–5链接合并注释源段`L491–634`，仍待按源序迁移。L316末“He too was naturally an”续至p.296，故p.295保持partial；p.294因跨页句闭合转complete。

受控脚本`chp10_p295_migration.py`固定来源资产SHA-256 `f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f`、规范段SHA-256 `3ea63b6be08469c90ed3a0f6245fbe4d9f740b11617b55fe56e211cb9f80d064`、候选序号、相邻coverage、提及跨度、statement原句和跨页前态。首次写回后审计发现两个同源索引子目提及与Algarotti/Carriera实体提及重叠；删除这两条误把同一span映射为另一候选的重复mention，并把“他们相遇”mention从Carriera索引子候选cand-0582改映射为主候选cand-0581。索引候选仍保留供S3对齐。修订前现表恢复副本为`mentions.csv.bak-s2-chp10-p295-mention-fix-20261002`，首次应用前的四表恢复副本为各表`.bak-s2-chp10-p295-20261002`。

最终`audit_tables.py --summary`：824段中428 complete、62 excluded、332 queued、2 partial；候选9,103、提及18,460、statement 8,362；`s2_missing=[]`、`errors=[]`。剩余告警为两条既存S5 `enrichment.source_ref`未解析、全书S2尚有queued/partial。`tests/test_audit_tables.py`通过11项，`git diff --check`退出码0（仅LF/CRLF提示）。下一段为p.296 `chp-10:10_CHP-10_intro:l318-330`；S2尚未收口，不能交接S3。

## 第十章印刷页296正文（2026-10-02）

p.296（PDF物理第25页）规范段`chp-10:10_CHP-10_intro:l318-330`对照页图完成阅读与迁移，新增20个候选（cand-9117–cand-9136）、57条精确提及和23条原书statement。闭合p.295 Clemens August为Rosalba Carriera崇拜者并拥有其粉彩的跨页句；记录其1730年后为赞助教堂委托祭坛画、Piazzetta 1735年《Assumption of the Virgin》及Haskell对其风格的评价。之后记录德国/威尼斯艺术赞助在1750年前后的叙述、Würzburg Residenz与独立室内空间Kaisersaal、Schönborn家族/教区继任关系及Karl Philip von Greiffenklau说服Tiepolo赴Würzburg；分开辨认Balthasar Neumann、Kaisersaal装饰、Apollo/Barbarossa/Beatrice天顶场景、婚礼场景和Harold von Hocheim受封场景。沿用Plate 50整幅楼梯壁画候选cand-4180，未重复造《Four Continents》作品；Rezzonico改编只记录为原方案后来修改使用，不与cand-4105强行判为完全同一作品。Haskell关于German princely clergy、absolutism和ancien régime的评价/解释与人物行动分层；Juvarra的Turin任职与Sebastiano Ricci佣金句保留为跨页开放statement。

页图校读只记S2，不改S0：`Schonborn`→`Schönborn`；`Wurzburg`→`Würzburg`。p.295 Venice后OCR脚注6已在本页跨页闭合时按页图确认应为5；p.295现转complete。p.296注1–3回链合并注释段L491–634，仍待按序迁移。L330末句止于“Sebastiano”，续至p.297，故p.296保持partial。

受控脚本`chp10_p296_migration.py`锁定来源资产SHA-256 `f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f`、规范段SHA-256 `9b78eeb58e0f2a805f17499460a4cf76f21530f849917beb42329bbad5b2205c`、候选顺序、相邻coverage、索引候选、提及跨度、statement引句与外键；应用前四表恢复副本为各表`.bak-s2-chp10-p296-20261002`。最终`audit_tables.py --summary`：824段中429 complete、62 excluded、331 queued、2 partial；候选9,123、提及18,517、statement 8,385；`s2_missing=[]`、`errors=[]`。剩余告警为两条既存S5 `enrichment.source_ref`无法解析及预期的queued/partial提示。`tests/test_audit_tables.py`通过11项，`git diff --check`退出码0（仅LF/CRLF提示）。下一段为p.297 `chp-10:10_CHP-10_intro:l332-343`；S2尚未收口，不能交接S3。

## 第十章印刷页293正文（2026-10-02）

p.293（PDF物理第22页）正文`chp-10:10_CHP-10_intro:l279-290`完成语义阅读并迁移，新增18个候选（cand-9057–cand-9074）、60条精确提及和21条statement。闭合p.292 Tessin“in his native country”句；记录其1728年在巴黎为瑞典国王采购、1739年出任驻法大使、巴黎当代艺术收藏及Boucher相关叙述（保留“apparently”限定）、威尼斯画家评价信、对Tiepolo作品和报价的评价与个人收藏；另记录Gai、法国雕塑家、Tessin在威尼斯的交往，以及柏林“hors de Paris point de salut”说法、德意志地区赞助变化、Pellegrini/Ricci/Carriera等画家。匿名国王、法国雕塑家群体、作品、信件和未充分识别的Taraval均保留待对齐；不从群体称谓推断具体成员或身份。页末“in-1725”是未完片段，保持p.293 partial，待p.294续读。

页图校读只记在S2、不改S0：`sur turtrès`→`sur un très`、`quelle`→`qu’elle`、`InfortunLtel Ite`→`Unfortunately he`、`seared`→`feared`、`Diisseldorf`→`Düsseldorf`、`Rosalba Camera`→`Rosalba Carriera`；最终`in-1725`片段保留原样等待续页，不猜补。注1中`Siren, pp. 103 ff.`按原书locator记录为候选，仍待与合并注释和书目核对；本页注释后续仍按源序迁移。

受控脚本`chp10_p293_migration.py`默认dry-run，校验源资产及规范段SHA-256、候选序号、相邻coverage前态、索引候选、60条提及的精确跨度及statement原句/外键；应用前保存四表恢复副本`.bak-s2-chp10-p293-20261002`。dry-run通过后应用；`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，仍有两条既存S5 `enrichment.source_ref`警告及预期的334段queued/2段partial提示。`tests/test_audit_tables.py` 9项通过，`git diff --check`退出码0（仅有LF/CRLF转换提示）。全账本824段：426 complete、62 excluded、334 queued、2 partial；候选9,061、提及18,308、statement 8,307。p.292转complete；p.293保持partial。下一规范段为p.294 `chp-10:10_CHP-10_intro:l292-302`；全书S2仍未收口，不能交接S3。

## 第十章印刷页297正文（2026-10-02）

p.297（PDF物理第26页）规范段`chp-10:10_CHP-10_intro:l332-343`新增18个候选（cand-9137–cand-9154）、52条精确提及和17条原书statement。L333闭合p.296 Juvarra任Turin艺术总监并促成Sebastiano Ricci宫殿/教堂委托的跨页句；本页另记Ricci后期Turin作品及Haskell判断、Juvarra 1735年Madrid宫殿方案和各地画派名额、Amigoni与Tiepolo的Madrid宫廷任务、Tiepolo晚年Aranjuez祭坛画及Mengs替换作品，以及Rotari、Fontebasso和Guarana赴圣彼得堡/莫斯科的经历。区分未名宫殿、作品组、教堂、宫廷机构和艺术家群体，保留Haskell对西班牙反威尼斯态度的可能性限定。

页图校读只记S2、不改S0：`fist`→`list`、`fife`→`life`、`Guaraña`→`Guarana`。L343为注1 OCR摘句，和合并注释段L570重复，故不重复迁移；p.297保持partial，注1–6待合并注释段按源序处理。Juvarra/Ricci跨页句闭合后p.296转complete；下一段为p.298 `chp-10:10_CHP-10_intro:l345-352`。

受控脚本`chp10_p297_migration.py`默认dry-run，固定来源资产/段SHA、候选序号、索引候选、提及跨度、statement引句/外键与前态；写入前为候选、提及、statement、coverage四表保存`.bak-s2-chp10-p297-20261002`。全表审计发现Guarana句跨L341–342而statement范围仅记L342；修正为L341–342后复审。`audit_tables.py --summary`：824段中430 complete、62 excluded、330 queued、2 partial；候选9,141、提及18,569、statement 8,402；`s2_missing=[]`、`errors=[]`。仍有两条既存S5 `enrichment.source_ref`警告及全书S2未收口提示。定向审计测试11项通过；`git diff --check`退出码0（保留既存LF/CRLF提示）。

## 第十章印刷页298–303语义处理（2026-10-02）

p.298（PDF物理第27页）规范段 `chp-10:10_CHP-10_intro:l345-352` 完成并新增11个候选、60条提及和14条statement。记录Catherine II即位及其趣味/政策、Bellotto原拟赴圣彼得堡后转往华沙、Novelli的Creusa画作及其拒绝俄方邀请、Algarotti替Augustus III购得Tiepolo《Banquet of Cleopatra》后转入圣彼得堡的路径；印本核对和细节见coverage及本页迁移脚本。

p.299–301正文段 `chp-10:10_CHP-10_intro:l354-366`、`l368-380`、`l382-389` 合计新增20个候选、87条提及和33条statement。p.299记录Smith的教育、威尼斯商贸/领事身份、Salumieri行会争端、外交会面住宅、Pasquali出版业务及Gori/Guicciardini/Museum Etruscum项目；p.300闭合其领事身份句，处理1762年售藏George III、1767年返任、逝世安葬、收藏与社交网络；p.301开启Smith婚姻和Carriera/Smith关系等叙事。扫描校读只记录于S2，不改S0。三页正文跨页续句已闭合，但页下注1–7仍待合并注释段，三段保留partial。

p.302（PDF物理第31页）新增10个候选、50条提及和16条statement；闭合p.301句首“Lady”为Mary Wortley Montagu，记录Smith婚姻、du Boccage的1757年观察、其收藏和Ricci委托、七幅新约题材画与七件Cignani cartoons、1749年出版及可能关联Turin系列。匿名第二任妻子、作品组和空间分别保留，不合并为确定身份。页图校读脚注号及“fine quality”，脚注摘句继续由合并注释源处理；本页末句续至p.303，故partial。

p.303（PDF物理第32页）新增11个候选（cand-9196–cand-9206）、47条精确提及和16条statement。闭合p.302关于Smith购入Ricci工作室作品的推测，并保留Haskell“强烈暗示/很可能”的证据语气；登记Ricci的13件宗教/古典作品、仿Veronese头像习作和211张杂项素描；记录Marco Ricci与Sebastiano Ricci的侄甥关系、Smith藏有42幅画及近150张素描而委托比例不明、Zanetti 1743年版画书与Algarotti的关系；记录Smith在1721/1723与Carriera的交往、1725/1726/1728付款、代英格兰人安排委托、Winter及两版去向，以及Robert Dingley 1735年索画信。Dingley请求不证明作品完成，Winter两版分别保留。页图确认S0 OCR “Ricci’s Use”应读“Ricci’s life”、“such'' a commission”应读“such a commission”，仅记S2；p.303 L409和脚注1–6继续由合并注释段处理，末句续至p.304，故partial。

本批处理后全书824段为431 reviewed/complete、62 excluded/complete、324 queued/pending、7 reviewed/partial；候选9,193、提及18,813、book statements 8,481。`python scripts/audit_tables.py --summary` 为 `s2_missing=[]`、`errors=[]`；仍有两条既存S5 `enrichment.source_ref` 告警。`tests/test_audit_tables.py`通过9项。7个partial为p.289、p.297、p.299–303；其中p.289注释摘段与第十章p.297及p.299–303脚注需在合并注释源 `L491–634` 收口。下一段按书序为p.304 `chp-10:10_CHP-10_intro:l411-421`；全书S2未收口，不交接S3。

## 第十章印刷页304正文（2026-10-02）

p.304（PDF物理第33页）规范段 `chp-10:10_CHP-10_intro:l411-421` 新增7个候选（cand-9207–cand-9213）、50条精确提及和16条statement。闭合p.303关于Smith居住Palazzo Balbi的跨页句；记录其1731年购入Mogliano乡间宅邸、此前向Gerolamo Canal（时任Procuratore di San Marco）承租四年；分别保留Palazzo Balbi与乡间宅邸两处，并记录Smith在两处陈列Ricci、Cignani、Carriera作品及可能包括Piazzetta作品。保留Haskell关于Smith收藏在威尼斯现代艺术中的地位、趋向风景/城市景观而远离大型历史画的解释，以及“有意与否”的限定和不趋向肖像画的语境。

本页转入Smith与Canaletto：不把1729年前无确证说成未接触，保留“可能早一两年开始为Smith工作”的推断；记录Canaletto作品主要进入英国市场和Smith自藏、作品委托常经Smith之手、Smith自任代理人购画，并保留关系性质未完全确定。记录Smith关于1729年与画家争执的引文、Haskell对双方吝啬性格的评价，以及Count Tessin于1736年所述四年独占聘用（这是Haskell对Tessin说法的解释，不是已核合同）。页末“远多于Royal Collection现存53幅”的比较句续至p.305，不能单页定稿。

页图与S0对照未发现需在S2登记的新OCR词误；印本拼写“submitt”按原样保留。脚注1–7仍待合并注释源逐项处理，包括Mogliano租购档案、Piazzetta委托、关系研究、Conduitt委托信、Smith致Samuel Hill信、Tessin说法来源及Royal Collection销售目录。p.304保留partial状态。 `python scripts/audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全书824段：431 complete、62 excluded、323 queued、8 partial；候选9,200、提及18,863、statement 8,497。`tests/test_audit_tables.py`通过9项。下一段为p.305 `chp-10:10_CHP-10_intro:l423-433`。

## 第十章印刷页305正文（2026-10-02）

p.305（PDF物理第34页）规范段 `chp-10:10_CHP-10_intro:l423-433` 新增9个候选（cand-9214–cand-9222）、45条精确提及和16条statement。L424闭合p.304对Tessin“四年独占”观察的讨论：Haskell只说把Smith替其他客户承接的委托也算入时，该观察大体可信。记录Canaletto为Smith作的六幅S. Marco景观及其早期风格；1730–1735年14幅画组成、其中12幅小型Grand Canal景观与两幅赛船画的区分；把景观序列理解为系统记录、而非突出建筑审美的方式；与以往为赞助人记录当代生活、关联建筑/风景、picturesque街巷或杰出建筑的委托传统作比较。

Haskell把Visentini于1735年出版的版画视为游客认识该系列的渠道，提出该系列可能充当Canaletto能力的视觉目录/广告；这仍是待证假说。记录1736年Tessin报告与Canaletto似乎几乎停止为Smith工作的并置张力，及Smith收藏中两组Canaletto绘画之间约十年的空档、同期Canaletto从英国访客获得重要委托。后列三组独立客户作品：Duke of Bedford 20幅、Sir Robert Hervey 20幅、Earl of Carlisle 17幅；本页以建筑写实度与工作室协助的评价开句，最后一句续p.306。

页图核读确认S0 OCR的“contemporary Use”“slum Use”均为“life”；“impressionistic”后注1可见；“get to know it”后的上标疑似脚注号，须与合并注释段核对后定号。S0未修改。p.304末句已由L424闭合，但p.304脚注1–7仍待合并注释段，故仍partial。p.305注释和跨页尾句未收口，保持partial。处理后824段：431 reviewed/complete、62 excluded、322 queued、9 partial；候选9,209、提及18,908、statement 8,513。`python scripts/audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，两条既存S5来源引用告警仍在。`tests/test_audit_tables.py`通过9项。下一段按书序为p.306 `chp-10:10_CHP-10_intro:l435-443`；全书S2未收口，不交接S3。

## 第十章印刷页306正文（2026-10-02）

p.306（PDF物理第35页）规范段 `chp-10:10_CHP-10_intro:l435-443` 新增8个候选（cand-9223–cand-9230）、30条精确提及和11条statement。L436闭合p.305关于Canaletto晚年风格的句子。记录Smith在此期间的活动无法确知、可能大量购买old masters并扩大素描收藏；Sebastiano Ricci于1734年去世后，Smith可能取得其工作室的大部分内容；Pasquali出版的插图书与Smith保留、主要由Visentini绘制的原始素描。此“工作室大部”是Haskell的推断，与p.302–303关于工作室作品和211张杂项素描的说法保持关联但不假定范围相同。

本页转入Smith的宝石与浮雕宝石收藏和1737–1738年致A. F. Gori的信件；Haskell以此作为Smith艺术趣味的唯一明确线索，记录其本人关于工艺、古代作品与优秀现代作品的引文。另记人们称赞其藏石选择但并非人人认同其慷慨/品味；Girolamo Zanetti称其兄Antonio Maria代Smith描摹宝石却报酬很差，并批评Smith若干“古物”的质量与真实性；Smith仍区分十六世纪名家作品与较晚作品。John Breval参观Smith收藏时见到一件小雕像；p.306引作“似乎是Aesculapius”，p.307续文又称Priapus，身份保持待定。

页图确认S0 OCR的`charactèristic`应读`characteristic`，只登记在S2；p.306 L442–443为页下注摘录，与合并注释源重复，不重复迁移。脚注1–6待合并注释段。`python scripts/audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；`tests/test_audit_tables.py`通过10项。当前824段：431 complete、62 excluded、321 queued、10 partial；候选9,217、提及18,938、statement 8,524。下一段按书序为p.307 `chp-10:10_CHP-10_intro:l445-454`；全书S2仍未收口，不交接S3。

## 第十章印刷页307正文（2026-10-02）

p.307（PDF物理第36页）规范段 chp-10:10_CHP-10_intro:l445-454 已逐句阅读并对照印本。L446闭合p.306 John Breval所见小雕像的引文：p.306称其“seemingly an Aesculapio”，p.307续称Priapus并给出粗鄙比例描述；原书标签不一致，候选cand-9230继续保持未识别，不把两个名称合并为确定身份。补记其他未具名雕塑cand-9241及既有Cignani cartoons候选cand-9191；书籍与古物没有具体题名，不另造对象。

L447称Smith在“forties”初期重新大规模赞助当代艺术家（未给姓名的群体记cand-9242）；1741年Smith向Elector of Saxony售出数量不明、今不可识别的画作（cand-9231），同年或前后从Pellegrini遗孀处买入荷兰及佛兰德绘画收藏（cand-9232）。索引对p.307的Augustus III条目（cand-0148）是“Elector of Saxony”的候选身份，但留待S3核对；Pellegrini按p.307索引候选cand-1862记录，遗孀cand-9233不推定姓名。

L448–449记录Vermeer《Lady at the Virginals》（cand-9234），原文说现藏Buckingham Palace（cand-9240）；Smith从遗孀处取得此画被Haskell称为“almost certainly”，后句又用“if ... really came from Pellegrini’s widow”作条件，故只记强推测，不定为确定来源。书中指出该画当时被归于Frans van Mieris（cand-1663），这是历史归属而非作者认定。原书“the Vermeer greatly influenced Canaletto”被限定为有过此说、理论虽诱人却难证；关系候选保留主张者与Haskell的保留意见。S0 OCR的“theWermeer”经页图核对为“the Vermeer”，只记S2校读，不改S0。

L449–450把1740年奥地利王位继承战争爆发（cand-9235）与英国游客人数下降（未具名群体cand-9236）相连；Canaletto随后重新为Smith工作，精确复工时间未给。L451–452记录Canaletto由小幅威尼斯景观转向宏伟、幻想性和题材扩展的风格描述；其第二次罗马之行只是“quite possibly”，Smith同行则是“perhaps”，并记录此行引出的六幅古罗马纪念物景观（cand-9238）。Haskell称其为Canaletto为Smith画过的最大作品，推测对收藏影响很大；“在威尼斯独特”、古罗马价值将重返意大利艺术中心的信号、外来者眼中的罗马、画面粗硬及回到早期戏剧性视觉，均作为作者评价／解释而不是客观定论保存。Rome使用cand-4490，Venice使用cand-2719；对“neo-classic”影响只保留Haskell的疑问。

L453–454称下一批Canaletto委托画意在呈现Smith偏爱的建筑风格，并开始说1744年的“13 Door Pieces”；候选系列cand-9239暂留这一不完整题名，句子在p.308续接，不提前补全。

页图确认印刷页307页脚注1–4分别涉及Breval 1738（I, p.230）、Blunt与Croft-Murray（p.11）、Pellegrini展览图录及Vivian 1962、以及Brandi的影响说法；这些是原书引证，不作为已独立核读的外部证据，留待合并注释源段L491–634处理。跨页闭合后p.306仍因脚注1–6待处理而为partial；p.307因末句续至p.308且页下注待处理而为partial。

本段新增12个候选（cand-9231–cand-9242）、44条精确提及和18条book statement。p.307迁移脚本chp10_p307_migration.py默认dry-run；本次先dry-run核对来源资产及段哈希、候选ID序列、提及字符跨度、statement候选外键与前态，再应用并为四表生成.bak-s2-chp10-p307-20261002恢复副本。应用后audit_tables.py --summary为s2_missing=[]、errors=[]；总覆盖824段：431 complete、62 excluded、320 queued、11 partial；候选9,229、提及18,982、book statements 8,542。tests/test_audit_tables.py通过（11项）；git diff --check通过，只有既有LF/CRLF转换提示。仍有两条既存S5 enrichment.source_ref告警。下一段按书序为p.308 chp-10:10_CHP-10_intro:l456-466；全书S2未收口，不交接S3。

## 第十章印刷页308正文（2026-10-02）

p.308（PDF物理第37页）规范段 `chp-10:10_CHP-10_intro:l456-466` 已逐句阅读并对照印本。L457闭合p.307关于1744年“13 Door Pieces”的句子，题名补为Canaletto的“principal Buildings of Palladio”；L457–458同时说明Smith目录承认并非系列内所有建筑都是Palladio作品，系列旨在呈现威尼斯最受赞赏的建筑，绝大多数建筑由16世纪Palladian建筑师设计。系列内部不一致性保留为Haskell判断。

L459–461区分按Palladio规划的Rialto景观、Carità庭院实景和想象场景：圣马可马匹脱离教堂、置于广场，以及Scala dei Giganti的幻想性表现。后两者被Haskell称作Canaletto早期caprices；其灵感来源仍有两个并列可能：Algarotti 1743年到达威尼斯及其与Smith往来，或Canaletto一两年前访问罗马时从Pannini处得到构想；不把任一假说登记为确定影响关系。另记录Canaletto约在此时为Smith绘制两幅罗马废墟capricci，原书称其风格“bold frank”。

L462记Canaletto题献Smith的31幅蚀刻作品，保留意大利题名并与为Smith绘制的油画分开；距离、植物覆柱、孤鸟、拱门和山峦等描述及Haskell的审美评价均按作者解释记录。L462–463闭合其赴英句：Canaletto apparently按Smith建议赴英，两人近十年少有往来；“apparently”和时间约数不升级为确定事实。

L464–465记录Smith在Canaletto 1746年离开后委托Visentini、Zuccarelli继续overdoors系列；分别保留Visentini的建筑/书籍插图工作、Zuccarelli的风景画工作，以及其六幅Rebecca、Jacob与Esau题材画作可能早于1746年或由当年委托开启Smith联系的两种可能。Zuccarelli在该项目中的作用被Haskell称为次要、但作品质量更高；其装饰性威尼斯风景加在Visentini建筑景观中。L465所述建筑全为英国乡间宅邸及环境，二人都未亲见，受Lord Burlington及其追随者提升为教条规范的风格影响；句子续至p.309的“taste”，当前statement保留partial。

新增10个候选（cand-9243–cand-9252）、46条精确提及和15条原书statement。系列画、地点和作品均按可支持的具体范围建候选；“Horses of St Mark”幻想画与实体雕塑不合并。页图核对仅记S2：OCR `Carita`校读为印本`Carità`，`Canaletto’s’work`校读为`Canaletto’s work`，未改S0。页下注1–3留在合并注释源段L621–623统一处理；p.308 L466是注1续文，未提前迁移，p.308仍为partial。p.307仍因其自身脚注待办为partial。

受控脚本`chp10_p308_migration.py`默认dry-run，核验来源及段哈希、候选序列、覆盖前态、精确提及跨度、外键和嵌套后应用；四表均生成`.bak-s2-chp10-p308-20261002`恢复副本。应用后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；824段中431 complete、62 excluded、319 queued、12 partial；候选9,239、提及19,028、book statements 8,557。`tests/test_audit_tables.py`通过11项，`git diff --check`通过（只有既有LF/CRLF转换提示）。两条既存S5 `enrichment.source_ref`警告未变。下一段按书序为p.309 `chp-10:10_CHP-10_intro:l468-479`；全书S2未收口，不交接S3。

## 第十章印刷页309正文（2026-10-02）

p.309（PDF物理第38页）规范段 `chp-10:10_CHP-10_intro:l468-479` 已逐句阅读并对照印本。L469闭合p.308末句“a dogmatic canon of taste—the Palladian”；回链更新p.308建筑风格statement，p.308仍因页注待处理而partial。L469–470记录11幅英国建筑画所表现的建筑师作品数量：Inigo Jones五幅、Lord Burlington两幅、Colen Campbell两幅、Roger Morris一幅、Vanbrugh一幅；这是11幅画的分布，不与Canaletto另一个1744年13 Door Pieces系列混同。Vanbrugh所选建筑“most Palladian”作为Haskell评价保存。

L471–472记录这些capricci未采用Canaletto《Horses of St Mark》幻想画的玩味变形、Haskell关于Smith不亲近该类型的判断；建筑图像主要取自Colen Campbell的*Vitruvius Britannicus*版画，建筑细节多数准确。记录Smith委托Nogari绘制Inigo Jones肖像；原书引述“Vandyke”及手持Banquetting House平面图的描述，但不据此另造一幅Van Dyck肖像或确认归属。Smith还出版Jones与Palladio著作的多个版本，具体书名未列出。

L473–476记录Smith于1767年出版其收藏的一份Teofilo Gallacini手稿，题为*Trattato sopra gli errori degli architetti*；印本为`sopra gli`，S0 OCR连写成`sopragli`，只登记S2校读。Visentini很快更新该书并批评Baroque建筑师及后继者直至Piranesi。Haskell称Smith宫殿访客可见大量建筑书籍；Andrea Memmo后来的引文说书籍与Visentini指导使他偏爱“pure and simple”风格，保留为Memmo自述而非对所有威尼斯人的概括。

L477记录Haskell对1746年Smith严格neo-Palladian趣味、英国审美变化及18世纪40年代威尼斯艺术向classicism转向的解释，并保留其关于Smith赞助推动这一倾向的作者判断。L477–478记一件未具名的Tiepolo重要作品委托被Algarotti转往Dresden宫廷、最后未成；不补造委托人、作品名或完成版本。Smith此后倾向于风景和建筑画、远离历史画与幻想题材。约1751年Visentini为“his palace”建造新的古典化大理石立面；该代词指代未定，另存为未知宫殿，不与Smith宫殿合并。Smith同期当代艺术家赞助大幅减少。

L478–479保留Zuccarelli于1752年赴英后Smith“可能”开始雇用Zais的推测，以及Smith未把Zais风景画列入后来售予George III的画作批次的Haskell转述。按“同一年”记录Smith购入Castiglione与Carracci绘画的大批素描，以及从Zaccaria Sagredo继承人处购买的旧大师画作；继承人未具名，具体画作未识别。L479另开启Smith在Canaletto返程时购入更多作品、包括若干英国景观的叙述，末句续p.310，未提前补足返程地点。

新增15个候选（cand-9253–cand-9267）、73条精确提及和27条原书statement。新增对象包含Vitruvius Britannicus、Nogari的Jones肖像、Gallacini著作及Visentini更新、未具名Tiepolo作品、立面和未识别宫殿、1752年绘画/素描组及相应风格术语；不确定对象分别保留身份和版本问题。页图确认S0 OCR `TeoFilo`应读`Teofilo`，`sopragli`应读`sopra gli`；S0未改。p.309脚注1–6留待合并注释源段L491–634处理，因此本段仍partial；p.310为下一段。

受控脚本`chp10_p309_migration.py`默认dry-run，核验来源及段哈希、候选序列、覆盖前态、精确提及跨度、外键和非重叠锚点后应用；四表均生成`.bak-s2-chp10-p309-20261002`恢复副本。应用后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；824段中431 complete、62 excluded、318 queued、13 partial；候选9,254、提及19,101、book statements 8,584。`tests/test_audit_tables.py`通过11项，`git diff --check`通过（只有既有LF/CRLF转换提示）。两条既存S5 `enrichment.source_ref`警告未变。下一段按书序为p.310 `chp-10:10_CHP-10_intro:l481-489`；全书S2未收口，不交接S3。

## 第十章印刷页310正文（2026-10-02）

规范段 `chp-10:10_CHP-10_intro:l481-489` 已逐句对照《CHP-10.pdf》物理第39页阅读。p.309 L479关于Smith从Canaletto购入更多作品、包括若干英国景观的跨页句在p.310 L482闭合：Canaletto于1755年从London返回；未具名景观的数量和各自身份仍不明。同步更新cand-9264及p.309对应statement和coverage说明。

L482–483区分Joseph Smith威尼斯palace与country house两处藏品分布：Canaletto景观、Ricci/Cignani作品和大部分较大型作品挂于palace；Dutch/Flemish画作、若干Zuccarelli作品及许多old masters保存在country house。相关未具名作品分别保留为cand-9268–cand-9273的来源局部组，不与先前提及的购买批次、Ricci/Cignani作品组或Zuccarelli六幅风景画预先合并，留待S3对齐。cand-9171、cand-9207分别作为Smith palace及Mogliano country house候选；p.310本身没有再次写出Mogliano地名。

L484记Smith年近八十、计划处置图书与收藏；他于1755年出版题为Bibliotheca Smithiana的藏书目录。Haskell认为该书“几乎可以肯定”意在作为精心编制的出售目录，此为作者判断，未提升为确定事实。1756年Smith开始与English royal family谈判处置藏品，谈判几乎立即因Seven Years War爆发而中断；不把集体谈判方替换成George III，也不假定谈判持续到1762年。

L486–487记失望、年老和贸易受扰被Haskell用作Smith逐渐退出社交生活的解释；他于1756年放弃S. Giovanni Crisostomo剧院的包厢。四年后他辞去consulship，并在致William Pitt的信中表达希望返回England、先游历自己尚未到过的意大利主要城市（只熟悉Venice）的愿望；引文中的“fine arts”及收藏相关事物属于Smith自述。将该相对年代记为1760，并标明脚注4所指信件日期为1760-10-29；脚注原文和信件证据仍待合并注释段处理。

L487–488记James Adam在此时见到Smith，并在信中称其“devilish poor”，预测若多活几年可能破产、认为他应出售收藏但被虚荣心阻止。保留为James Adam经Haskell转引的同时代财务评价，不作独立财务事实；脚注5所列致Robert与Jenny Adam的信件尚未核读。1762年，Smith经困难谈判把大部分最好的绘画、书籍、素描和宝石卖给George III；“most”与“best”均保留，脚注6指向Appendix 5。售后仍有足够作品覆盖墙面，但具体是哪处住所未明确。其后仍经营、从事picture dealing，1766年短暂恢复Consul职务；晚年似乎过着退隐生活，较少受到当地威尼斯人和游客注意；1770年去世，晚Canaletto两年。末句“will always be associated”记录为Haskell的回顾性评价，不作为独立正式关系。

本页对照扫描记录S2校读而不改S0：L486 `social Use`→`social life`、`sine arts`→`fine arts`、`tilings`→`things`；L488 `retired fife`→`retired life`。脚注1–6均回链合并注释段`chp-10:10_CHP-10_intro:l491-634`，因此p.310正文虽已读，coverage仍为partial；脚注6的Appendix 5还需按全书源序处理。

新增11个候选（cand-9268–cand-9278）、50条精确提及和18条原书statement。受控脚本`chp10_p310_migration.py`默认dry-run，锁定来源资产SHA-256 `f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f`、规范段SHA-256 `1b5b051796bbac3725681b091cb6e82a00f22381d0f651f934a9ccbd590f66b7`、候选序号、coverage前态、提及跨度、statement外键及跨页句前态；应用前为四表保存`.bak-s2-chp10-p310-20261002`恢复副本。应用后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；824段中431 complete、62 excluded、317 queued、14 partial；候选9,265、提及19,151、book statements 8,602。审计测试11项通过；仍有两条既存S5 `enrichment.source_ref`告警。下一规范段为合并注释`chp-10:10_CHP-10_intro:l491-634`；全书S2仍未收口，不能交接S3。


## 第十章印刷页276注1迁移（2026-10-02）

合并注释源段 `chp-10:10_CHP-10_intro:l491-634` 的L492已对照 `CHP-10.pdf` 物理第1页完成语义处理。该注分层保留：Haskell转述“certo signor Colle inglese”是早期传记所称首先建议Rosalba改画粉彩的人；引述Girolamo Zanetti《Elogio》并反驳其1708年日期，称Crespi已于1703年6月26日将其粉彩与Guido Reni比较；随后以推测解释Crespi或想到Reni晚年“chalky”画风。新建cand-9279–cand-9282（匿名作者的《Memorie》1843版、Girolamo Zanetti、《Elogio》、Malamani 1899 p.99引文定位），记录11条精确提及及3条原书statement；将正文st-chp10-p276-cole-carriera-pastel-portraits的注1链接到L492。被引文本未独立核读，不把脚注当作外部验证。

S2页图校读只记录、不改S0：L492 `alia`→`alla`、`net`→`nel`、`P12`→`p.12`、`ason`→`as on`。原书关于Guido画风的评语归于Haskell，不作为Crespi的直接陈述。注2–3（L493–494）以及全书其余合并注释未处理；该源段coverage为reviewed/partial、精确范围L492-492，下一位置为p.276注2 L493。

同页扫描复核另发现规范源文本L13包含一段Cole补充叙述（由现有S2断言记录），但 `CHP-10.pdf` 物理第1页图像未见该段，p.277物理第2页从German princes开始。保留S0与既有S2数据，将其标为待S2交接审计的来源差异；暂不将它改写为印本事实。

受控脚本 `chp10_p276_note1_migration.py` 默认dry-run，锁定来源文件SHA-256 `f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f`、合并注释段SHA-256 `33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76`、L492行哈希、候选序号、coverage前态、提及跨度、statement锚点与外键；写回前为四张规范表保存恢复副本`.bak-s2-chp10-p276-note1-20261002`。初次审计暴露candidate_origin与单行coverage区间格式不符合既有接口，已依审计器契约修正并保存额外恢复副本。最终 `audit_tables.py --summary` 为 `s2_missing=[]`、`errors=[]`；全账本824段中431 complete、62 excluded、316 queued、15 partial；候选9,269、提及19,162、statement 8,605。两条既存S5 `enrichment.source_ref`警告保留。tests/test_audit_tables.py通过11项。


## 第十章印刷页276注2–3迁移（2026-10-02）

合并注释源段 `chp-10:10_CHP-10_intro:l491-634` 的L493–L494已对照 `CHP-10.pdf` 物理第1页完成。注2的“The picture”回指p.276正文中Lord Manchester的入城画；脚注称该画“now”位于Birmingham City Art Gallery，并引用Nisser 1937。该“now”仅按Haskell脚注发表时的语境记录，不宣称为当前馆藏核验。注3只有Mostra di Pellegrini 1959 p.15的引用定位，没有新增可独立断言的事实；将其链接到Manchester携Pellegrini与Marco Ricci离威尼斯的正文statement，不提升为外部验证。

新增cand-9283–cand-9285（Birmingham City Art Gallery、Nisser 1937引文定位、Mostra di Pellegrini 1959 p.15），新增4条精确提及和1条原书statement；更新p.276正文脚注2–3状态为已迁移。扫描确认L493 OCR替换字符`��`应为印本破折号，校读只记S2。L492–L494已覆盖，合并注释段维持reviewed/partial，待处理范围L495–L634；下一步是p.277注1 L495。p.276源文件L13与印本扫描不一致的段落仍保留待S2交接审计。

受控脚本 `chp10_p276_notes2_3_migration.py` 默认dry-run，锁定来源文件与注释段哈希、L493–L494行哈希、候选序号、覆盖前态、mention跨度及statement外键；应用前保存四表恢复副本`.bak-s2-chp10-p276-notes2-3-20261002`。应用后 `audit_tables.py --summary` 为 `s2_missing=[]`、`errors=[]`；全账本824段中431 complete、62 excluded、316 queued、15 partial；候选9,272、提及19,166、statement 8,606。两条既存S5 `enrichment.source_ref`警告仍在；`tests/test_audit_tables.py`通过11项。


## 第十章印刷页277注1–4迁移（2026-10-02）

合并注释源段 chp-10:10_CHP-10_intro:l491-634 的L495–L498已对照 CHP-10.pdf 物理第2页完成。注1（Malamani 1899 pp.39、42）、注3（Malamani 1899 p.49）和注4（Malamani 1899 p.50；Sensier pp.22 ff.）只提供引文定位；未独立查阅引文来源。注2称Frederick IV的Regatta“now”在Fredericksborg, Copenhagen，引用Mauroner 1945 p.51；该地点只按Haskell注释发表时的说法记录，不宣称为当前馆藏。新增cand-9286–cand-9291：Fredericksborg、Copenhagen、Malamani 1899多页引文定位、Mauroner 1945引文定位、Sensier引文定位及仅具姓氏的Sensier候选；新增15条精确提及和1条地点statement，并链接正文注1–4共6条断言。Malamani、Mauroner、Sensier作者与出版物候选仍待全局S3对齐。

页图显示L496 OCR替换字符“��”为印本破折号；该校读只记S2。印本拼写“Fredericksborg”照录，不推断具体馆舍身份。L499的注5仍待处理；合并注释段coverage为reviewed/partial、范围L492-498，下一源行L499。p.276 L13来源文本与扫描不一致的问题继续保留待全书S2交接审计。

受控脚本 chp10_p277_notes1_4_migration.py 默认dry-run，锁定来源与注释段哈希、L495–L498行哈希、候选序号、coverage前态、提及跨度和断言外键；写回前保存四表恢复副本.bak-s2-chp10-p277-notes1-4-20261002。应用后 audit_tables.py --summary 为 s2_missing=[]、errors=[]；全账本824段中431 complete、62 excluded、316 queued、15 partial；候选9,278、提及19,181、statement 8,607。两条既存S5 enrichment.source_ref警告仍在。`tests/test_audit_tables.py`通过11项。


## 第十章印刷页277注5迁移（2026-10-02）

合并注释源段 `chp-10:10_CHP-10_intro:l491-634` 的L499已对照 `CHP-10.pdf` 物理第2页完成。注5回述Manchester入城画及Frederick IV的Regatta，并列出Carlevarijs《Entry of the Count of Colloredo》（1726）、Canaletto《Entry of the Comte de Gergy》（1725）和《Entry of the Count of Bolagno》（1729）。只记录脚注明示的画家、作品、年份、使节身份与书中所报地点；没有把使节写成委托人。Dresden、Hermitage均按Haskell脚注发表时的地点报告记录，不称为当前馆藏核验；Mauroner、Haskell及V. Moschini引文未独立查阅。身份不全的三位伯爵留待S3。

复用索引已有三条作品子目并在S2赋`work`类型；新增cand-9292–cand-9295（三位未具名全名的使节、V. Moschini 1954 p.29引文定位）、20条精确提及和6条原书statement。与正文注5关联的两条statement已链接脚注六条断言并解除pending。源文OCR中的Manchester弯引号与替换字符均保留；扫描校读只记S2、不改S0。合并注释段coverage范围扩至L492–499，仍为partial，L500–L634待处理。

受控脚本 `chp10_p277_note5_migration.py` 默认dry-run，锁定来源/注释段/L499哈希、候选序号、索引子目类型与coverage前态，验证20个mention精确跨度、6条statement锚点及外键；应用前为四表保存恢复副本`.bak-s2-chp10-p277-note5-20261002`。初次dry-run发现Manchester弯引号被脚本误录为乱码，修正脚本后dry-run及apply通过，S0来源未改。应用后 `audit_tables.py --summary` 为 `s2_missing=[]`、`errors=[]`；824段中431 complete、62 excluded、316 queued、15 partial；候选9,282、提及19,201、statement 8,613。两条既存S5 `enrichment.source_ref`警告仍在；`tests/test_audit_tables.py`通过11项，`git diff --check`通过（仅有既存LF/CRLF转换提示）。下一源行为L500。


## 第十章印刷页278注1–6迁移（2026-10-02）

合并注释源段 `chp-10:10_CHP-10_intro:l491-634` 的L500–L505已对照 `CHP-10.pdf` 物理第3页完成。注1–3及5–6是交叉引用或书目定位：Chapter 7/Lavagnino、Pallucchini 1933–4、Donzelli p.82，以及《Duke of Manchester》卷II的泛指和p.140定位；均未独立核读。注4直接称“Nymphenburg的Amigoni作品”始于1716年，另引Lavagnino p.121与Powell pp.68–70、110、147；登记为未具名单件作品的作品群日期陈述，未推断具体作品或将其与建筑亭阁混同。S0中该页脚注5、6编号分别误识为6、8，已依扫描在S2中恢复打印编号并保留OCR原文；Powell页码`Iio`校读为扫描所示`110`，S0未改。

新增cand-9296–cand-9300（Pallucchini、Donzelli、Powell、《Duke of Manchester》卷II引文定位及未具名Amigoni作品群），新增10条精确提及和1条原书statement；复用既有Amigoni与Nymphenburg花园候选。第十章p.278正文marker1–6对应的6条statement均已解除pending，只有注4新增事实statement。coverage范围扩展至L492–505，仍为partial；L506之后待处理。

受控脚本 `chp10_p278_notes1_6_migration.py` 默认dry-run，核对来源/注释段/行哈希、候选序号、coverage前态、六个正文脚注外键及10个mention跨度、statement锚点；应用前保存四表恢复副本`.bak-s2-chp10-p278-notes1-6-20261002`。应用后 `audit_tables.py --summary` 为 `s2_missing=[]`、`errors=[]`；824段中431 complete、62 excluded、316 queued、15 partial；候选9,287、提及19,211、statement 8,614。两条既存S5 `enrichment.source_ref`警告仍在；`tests/test_audit_tables.py`通过11项。


## 第十章印刷页279正文尾片与注1–3迁移（2026-10-02）

物理页279底部的三条脚注见合并注释源段L507–L509：注1引用Watson发表于 `Journal of R.I.B.A.`（1954，pp.171–177），注2引用Vertue《Notebooks》卷III第94页，注3引用《Mostra di Pellegrini》（1959）第56页。它们是来源路径，未独立核读或提升为新事实；将5条正文带注statement分别回链并解除pending。Watson文章题名仍待书目对齐；复用既有George Vertue《Notebooks》候选并补记本页卷页定位；Mostra p.56与既有同名p.15定位分别记录，留S3对齐。

合并注释文件L506单独出现`47).`，对照PDF确认它是p.279正文句“(Plate 47).”被抽离后的尾片，不是脚注。正文段L43–49已有半截图版引用及p.279同一断言，故将L506回链至`st-chp10-p279-marco-musical-groups-hogarth`的`source_fragment_reconciliations`，不重复创建实体、提及或断言。页图同时确认L507 OCR `os`→`of`及L508 `HI`→`III`；校读仅记S2，S0不改。

新增cand-9301–cand-9302（Watson文章定位、Mostra di Pellegrini 1959 p.56定位）和4条精确提及、0条statement。受控脚本`chp10_p279_notes1_3_migration.py`默认dry-run，锁定来源/段/L506–509哈希、候选序号、coverage前态、五条正文脚注外键、Plate 47现有断言及mention跨度；写回前保存四表恢复副本`.bak-s2-chp10-p279-notes1-3-20261002`。应用后 `audit_tables.py --summary` 为 `s2_missing=[]`、`errors=[]`；824段中431 complete、62 excluded、316 queued、15 partial；候选9,289、提及19,215、statement 8,614。两条既存S5 `enrichment.source_ref`警告仍在；`tests/test_audit_tables.py`通过11项。合并注释覆盖至L509，下一位置L510。


## 第十章印刷页280注1–8迁移（2026-10-02）

合并注释源段L510–L516与 `CHP-10.pdf` 物理第5页核对后，注1、2、4、6、8作为来源指引处理：Vertue《Notebooks》卷I p.38与卷IV p.48，Turberville卷II p.14，Wittkower 1948，以及《Complete Peerage》和H. Clifford Smith p.26；引文均未独立核读。注3记录Last Supper草图据称在Washington National Gallery of Art，以及另一幅Baptism草图据称于1960-12-07经Sotheby's售出；两张草图与p.280正文的完成画保持不同对象。注5分别记录Ricci两幅画作1713年日期、Haskell所报Chatsworth地点，以及“Dukes of Devonshire继承Burlington estate”的原书说法；爵位复数主体和estate范围／类型尚未确定，Osti pp.119–123未核。注7记录Chiswick villa于1725年开建，并将作品可能从Piccadilly town house转移到Chiswick保留为Haskell明确标作“probable”的推断，不写成确定流传。

新增cand-9303–cand-9314（Turberville引文定位、两张未具名草图、National Gallery of Art与Sotheby's机构、Chatsworth地点、待定的Dukes/estate对象及五条文献定位），新增26条精确提及和9条原书statement；为已有Ricci索引子目补work类型与本页语境，为Chiswick house子目补place类型。8条带注正文statement全部解除pending。扫描校读只记S2、不改S0：Verme→Vertue、Turberville卷号H→II及注号误识、p.280注6 OCR误作8、1960 OCR误作i960。

受控脚本`chp10_p280_notes1_8_migration.py`默认dry-run，锁定来源及合并段/行哈希、候选序号、coverage前态、八个正文脚注外键、26个mention跨度及9条statement原文锚点；应用前保存四表恢复副本`.bak-s2-chp10-p280-notes1-8-20261002`。应用后 `audit_tables.py --summary` 为 `s2_missing=[]`、`errors=[]`；824段中431 complete、62 excluded、316 queued、15 partial；候选9,301、提及19,241、statement 8,623。两条既存S5 `enrichment.source_ref`警告仍在；`tests/test_audit_tables.py`通过11项。合并注释覆盖至L516，下一位置L517。


## 第十章印刷页281图版导航尾片及注1–2迁移（2026-10-02）

合并注释段L517–519已对照第十章扫描处理。L517是旋转图版分组题头“(see Plates 50 and 51)”的OCR尾片，与既有视觉转录段所记录的导航信息相同，已回链，不重复创建实体或statement。注1为Collins Baker、Muriel I. Baker的引文定位；注2称Canons于1747年拆除后，礼拜堂被移至Lord Foley位于Worcestershire的乡间宅邸，并报告其作为Great Witley parish church保存。具体搬迁日期、移建物理范围及当前保存状况不由该脚注独立确认；Watson引文未核读。

新增cand-9315–cand-9320、9条精确提及和2条原书statement；为既有礼拜堂候选补充语境，并复用Canons索引候选。p.281正文3条带注statement已解除pending。脚注中的“survives intact to this day”作为原书写作时的报告保留，不当作当前实地核验。L517的重复导航尾片与板块视觉转录L6–7对齐；正文段的跨页coverage说明亦同步修正。

受控脚本`chp10_p281_notes1_2_migration.py`默认dry-run，验证来源、段落及行哈希、候选序号、coverage前态、脚注外键、9个mention跨度和statement锚点；应用前保存四表恢复副本`.bak-s2-chp10-p281-notes1-2-20261002`。应用后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；824段中431 complete、62 excluded、316 queued、15 partial；候选9,307、提及19,250、statement 8,625。两条既存S5 `enrichment.source_ref`警告仍在；`tests/test_audit_tables.py`通过11项，`git diff --check`通过（仅有LF/CRLF转换提示）。合并注释段coverage扩至L519，下一位置L520。


## 第十章印刷页282注1–3迁移（2026-10-02）

合并注释段L520–522已对照`CHP-10.pdf`物理第11页处理。注1记Haskell感谢Alessandro Bettagno提示Rapparini manuscripts（1958年在Düsseldorf出版）；沿用索引中的Rapparini标题子目并赋`archive`类型，区分出版材料组与其中被称为1709年eulogy的《Le Portrait du Vrai Mérite…》。Haskell称该文提供Johann Wilhelm patronage的较完整记载，并说明因写于1709年而未提Pellegrini；这些都是书中报告，未独立核读。注2只有“Nicolas de Pigage”，登记人物提及但不推断角色。注3记录Cignani的《St John the Baptist》和《Jupiter giving Suck》、Franceschini的《Venus and The Three Graces》、dal Sole的《St Teresa wounded by Christ》和《Rape of the Sabines》。Cignani两画的1702/1715日期及Augsburg/Munich地点均未逐画配对；“now”保留为Haskell叙述时的来源时间，不代表当前馆藏。Pascoli、Lavagnino、Zanotti所引页面未核读。

新增cand-9321–cand-9329（Bettagno、Pigage、五件具名作品、Augsburg地点及1958 Rapparini manuscript source set），新增21条精确提及和9条原书statement；复用索引Rapparini子目cand-2108及Pascoli、Lavagnino、Zanotti既有文献候选。正文marker1–3均解除pending，marker2仅对应姓名提及。扫描校读记入S2、不改S0：`Dusseldorf`→`Düsseldorf`、`Mérité`→`Mérite`、`hill`→`full`。

受控脚本`chp10_p282_notes1_3_migration.py`默认dry-run，锁定来源/合并段/行哈希、候选序号、coverage前态、三个正文脚注外键及21个mention跨度和statement锚点；应用前保存四表恢复副本`.bak-s2-chp10-p282-notes1-3-20261002`。应用后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；824段中431 complete、62 excluded、316 queued、15 partial；候选9,316、提及19,271、statement 8,634。两条既存S5 `enrichment.source_ref`警告仍在；`tests/test_audit_tables.py`通过11项，`git diff --check`通过（仅有LF/CRLF转换提示）。合并注释coverage扩至L522，下一位置L523。


## 第十章印刷页283注1–2迁移（2026-10-02）

合并注释段L523对照`CHP-10.pdf`物理第12页完成。注1仅为Pöllnitz卷III第274页定位；注2仅为Lavagnino第120页及M. Goering（1937）第233–250页定位。Pöllnitz人物候选与卷III引文定位分别记录；Lavagnino复用已存在文献候选；Goering保留为未与书目条目对齐的引文定位，待书目按来源顺序语义处理。所有引文均未独立核读，没有从被引页码推导新事实。

新增cand-9330–cand-9331及4条精确提及、0条statement；正文两条脚注marker均解除pending。受控脚本`chp10_p283_notes1_2_migration.py`默认dry-run，校验来源/段/行哈希、候选序号、coverage前态、两条正文脚注外键及mention跨度；写入前保存四表恢复副本`.bak-s2-chp10-p283-notes1-2-20261002`。应用后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；824段中431 complete、62 excluded、316 queued、15 partial；候选9,318、提及19,275、statement 8,634。两条既存S5 `enrichment.source_ref`警告仍在；`tests/test_audit_tables.py`通过11项，`git diff --check`通过（仅有LF/CRLF转换提示）。合并注释coverage扩至L523，下一位置L524。

## 第十章印刷页284注1–5迁移与mention重叠修正（2026-10-02）

合并注释源段L524–527已对照`CHP-10.pdf`物理第13页完成。注1记录Haskell所述Domenico Zanetti在Düsseldorf为选侯服务；尾随“—de Pigage”的语法/归属功能不清，保留为独立待对齐候选，并与p.282的Nicolas de Pigage分开，不预判别名或同一身份。注2仅登记Carriera致Mariette信件的Sensier引文路径；注3的Mariette、Adhémar、Stuffman为Crozat相关书目定位；注5为Blunt与Croft-Murray书目定位，均未独立核读。注4保留Levey转引Walpole《Anecdotes》的De La Fosse对Ricci所说之话，以及Haskell明确以“must presumably”标记的时间推断；引文、转引与作者判断分层。

新增9个候选（cand-9332–cand-9340）、26条精确提及和2条原书statement；p.284五个正文脚注marker解除pending，其中注2、3、5仅为来源定位。对注3的“Sensier”曾将完全相同的原文跨度重复登记为人物作者和文献来源，`audit_tables.py`首次报出重叠错误；经核对自然键和跨度后保留文献来源提及、移除冗余人物行。受控修复脚本`chp10_p284_mention_overlap_fix.py`先dry-run确认只影响该重复行，再apply并保存`.bak-s2-chp10-p284-mention-overlap-fix-20261002`。原迁移数据另有四表恢复副本`.bak-s2-chp10-p284-notes1-5-20261002`。

修正后`python scripts/audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；824段中431 complete、62 excluded、316 queued、15 partial；候选9,327、提及19,301、statement 8,636。既存两条S5 `enrichment.source_ref`警告和S2未处理/partial提醒不变；`python -m pytest tests/test_audit_tables.py -q`退出码0，`git diff --check`退出码0（LF/CRLF转换提示）。p.285续页相同编号marker 1 对应另一条脚注，仍链接待处理的L528，不与本次p.284 note 1混并。下一位置L528。

## 第十章印刷页285注1迁移（2026-10-02）

合并注释源段L528与`CHP-10.pdf`物理第14页核对。该注称“See the document published by Sensier, pp.97-102, Garas, 1962”，只有引文路径，没有可从脚注独立抽取的新事实。将Sensier出版的未具名文献、Garas姓氏及Garas 1962引文定位分别登记；未猜文献题名、未断定Garas身份，未核读引文内容。新增3个候选（cand-9341–cand-9343）及4条精确提及、0条statement，解除p.284 Mississippi Gallery跨页statement上续页脚注marker 1的pending状态，并将同一注的引文上下文连到紧随其后的法文方案引句。

受控脚本`chp10_p285_note1_migration.py`默认dry-run，锁定来源资产、合并注释段及L528哈希、候选序号、coverage前态、目标statement脚注状态和提及跨度；应用前四表恢复副本为`.bak-s2-chp10-p285-note1-20261002`。随后核读跨页语义时发现p.285正文分段也把同一个印刷marker 1挂在法文方案引句上；修正脚本`chp10_p285_note1_link_fix.py`验证原印本marker位于跨页句之后，将这一引句作为同一脚注的延续语境一并闭合pending，没有改写claim或计数；JSONL恢复副本为`.bak-s2-chp10-p285-note1-link-fix-20261002`。应用后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；824段中431 complete、62 excluded、316 queued、15 partial；候选9,330、提及19,305、statement 8,636。两条S5 `enrichment.source_ref`警告与S2未处理/partial提醒未变化。下一位置L529；该合并注释段仍为partial，尚不能交接S3。

## 第十章印刷页285注2–4迁移（2026-10-02）

合并注释L529–531已对照`CHP-10.pdf`物理第14页处理。注2称Mariette评价经Sensier从《Abecedario》第102–103页转引；复用已登记的Sensier人物与Orlandi《Abecedario Pittorico》候选，未核读转引或页码。注3指向Couvent des Augustins Déchaussés和Sensier p.107；新增候选cand-9344，暂按具体修院地点归`place`，同时保留建筑空间/宗教机构的对象边界待核；该注未具名具体祭坛画，不据此创建正式委托/创作关系。注4为Sensier pp.199、211的引文定位，与注3短引是否同一著作不作身份合并。新增1个候选和7条精确提及、0条statement；正文marker 2–4均解除pending。

受控脚本`chp10_p285_notes2_4_migration.py`默认dry-run，锁定来源/注释段/L529–531哈希、候选序号、coverage前态、三个正文断言marker及提及跨度；四表恢复副本为`.bak-s2-chp10-p285-notes2-4-20261002`。应用后`python scripts/audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；824段中431 complete、62 excluded、316 queued、15 partial；候选9,331、提及19,312、statement 8,636。既有两条S5来源引用警告及S2排队/partial提醒仍在。`python -m pytest tests/test_audit_tables.py -q`退出码0；`git diff --check`退出码0（LF/CRLF转换提示）。合并注释覆盖至L531，下一位置L532，尚不能交接S3。

## 第十章印刷页286注1–3迁移（2026-10-02）

合并注释L532–534已对照`CHP-10.pdf`物理第15页迁移。注1将Alessandro Galilei引语指向Ilaria Toesca（1952，p.208）；另有章内“I. Toesca”候选，未在S2合并，留S3判定身份。注2以Vertue《Notebooks》卷I p.45及卷III pp.45、49、51、67作为Powis House事件的引文定位；复用Vertue人物和《Notebooks》文献候选。注3将“Dictionary os National Biography”按印本校读为“of”，并记录Wheatley卷III p.18对Lord Powis年龄的书目指引；Wheatley身份和被引内容未核。注3 citation 不升级年龄断言为外部已核事实。新增5个候选（cand-9345–cand-9349）、8条精确提及、0条statement；正文三个脚注marker解除pending。

受控脚本`chp10_p286_notes1_3_migration.py`默认dry-run，锁定来源资产、合并段和L532–534哈希、候选序号、coverage前态、三个正文statement脚注marker及提及跨度；写回前四表恢复副本为`.bak-s2-chp10-p286-notes1-3-20261002`。应用后`python scripts/audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；824段中431 complete、62 excluded、316 queued、15 partial；候选9,336、提及19,320、statement 8,636。两条既存S5来源引用警告和S2未处理/partial提醒未变。`python -m pytest tests/test_audit_tables.py -q`退出码0。合并注释coverage扩展至L534，下一位置L535；S2仍未收口，不能交S3。

## 第十章印刷页287合并注释迁移（2026-10-02）

合并注释L535–539已对照`CHP-10.pdf`物理第16页处理打印注1、3–6。打印注2不在本迁移范围：其正文注释文本已作为statement保存在本章正文段`chp-10:10_CHP-10_intro:l206-216` L215–216，marker2三个相邻statement已链接；避免再次建候选或重复事实。

注1为`English Taste in the Eighteenth Century`（1955–6，p.26）及Hussey（1955，p.43）定位；注3为Watson发表于`Burlington Magazine`（1949，pp.75–79）的定位。注4记录Haskell所称McSwiny在不同生涯阶段以多种拼法署名，但本注没有列出具体拼法；DNB与Whitley只作为传记定位。另一条原书说法称有若干为McSwiny所改编歌剧制作的libretti当时存于British Museum；数量与题名均未给出，“now”按Haskell来源时间处理，不作为现存馆藏核验。分别保存拼写变化与libretto馆藏statement，后者留关系候选。注5对照扫描显示印本注号为5、作者为Vertue，S0 OCR误作6和Vertuc；只在S2记录。注6录Haskell关于McSwiny委托研究的概括和10条引文定位；不从引文题名推导内容。作者全名/同姓人物与已有跨章候选可能匹配者留S3，不自动合并。

新增25个候选（cand-9350–cand-9374）、33条精确提及和3条原书statement。受控脚本`chp10_p287_notes1_3_5_6_migration.py`默认dry-run，验证来源/合并段/L535–539哈希、最大候选序号、coverage前态、所有目标marker与mention跨度；写回前四表备份`.bak-s2-chp10-p287-notes1-3-5-6-20261002`。首次审计发现name-spelling statement引句误将源文逗号录为句号；`chp10_p287_quote_anchor_fix.py`干跑确认只修这一标点，应用后备份为`book-statements.jsonl.bak-s2-chp10-p287-quote-anchor-fix-20261002`。修正后`python scripts/audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；824段中431 complete、62 excluded、316 queued、15 partial；候选9,361、提及19,353、statement 8,639。两条S5未解析来源警告和S2全书未完成提醒保持不变；`python -m pytest tests/test_audit_tables.py -q`退出码0。L535–539已处理，下一位置L540。

## 第十章印刷页288合并注释迁移（2026-10-02）

合并注释段L540–542已对照`CHP-10.pdf`物理第17页处理。注1指向McSwiny《To the Ladies and Gentlemen of Taste》，并称该无日期小册子在Haskell写作时有一册存于British Museum；复用既有小册子与机构候选，不将其写成当前馆藏核验。注2记录Haskell所称Solimena“apparently”曾被考虑用于Isaac Newton之墓，并保留McSwiny致Duke of Richmond、1727年11月28日来函及Mr Francis Watson向Haskell出示该信的证据链；信件未独立查阅，无馆藏号。另记录Francesco Imperiali of Rome绘制King George I纪念物的原书说法，以及Lord Kemsley在来源时点拥有其一个版本的说法；作品形式、版本身份与人物身份保留原文边界。注2所引`English Taste in the Eighteenth Century`（1955–56，p.54）未读。注3的`Zanotti, II, pp.114, 221, 313`按本书唯一的Zanotti书目条目回连，所引页面未读；作者身份判断仍留S3。

新增6个候选（cand-9375–cand-9380）、17条精确提及和6条原书statement；已将正文segment `chp-10:10_CHP-10_intro:l218-227` 的4处脚注引用（marker 1两处、marker 2和3各一处）链接到L540、L541、L542。新建关系均保留为S2候选，未写入正式关系。候选身份、Newton之墓与整体方案的精确关系、Imperiali作品与版本同一性、Duke of Richmond及Watson/Kemsley身份均未裁决。L543–634仍待处理，因此该合并注释段继续为partial。

首次审计指出Newton人名与“Newton’s tomb”作品提及跨度交叉；将作品mention锚点收窄为源句中的“tomb”，保留人名与作品两条不交叠提及。写回前对候选、提及、statement和coverage四表创建恢复副本`.bak-s2-chp10-p288-notes-20261002`；锚点修复另备份`mentions.csv.bak-s2-chp10-p288-mention-anchor-fix-20261002`。最终`python scripts/audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；824段中431 complete、62 excluded、316 queued、15 partial；候选9,367、提及19,370、statement 8,645。`python -m pytest tests/test_audit_tables.py -q`通过11项。两条既存S5 `source_ref`警告和S2全书未完成/partial提醒仍在。下一位置L543。

## 第十章印刷页289注释转录源同步（2026-10-02）

复核p.289注1表格的派生视觉转录后，确认源文件有12个非空行；此前`segments.jsonl`保留了添加印本表题前的11行哈希与行范围，且覆盖表缺少该段。已先备份生成表和覆盖表，运行`build_source_segments.py --apply`重建清单，并将新段登记为`queued/pending`，与合并注释L543同批处理。当前全书源资产76份、规范段825段，覆盖表825行；候选、提及和statement计数未变。`audit_tables.py --summary`结构错误为0，`s2_missing=[]`；仍有317段queued、15段partial及两条既存S5 `source_ref`警告。下一步处理p.289注1表格和合并注释L543–544。

## 第十章印刷页289表格与注1–2迁移（2026-10-02）

对照`CHP-10.pdf`物理第18页，完整处理p.289派生视觉转录L1–12、正文注1散文尾段L234–236及合并注释L543–544。转录保留印本三列关系：artist list、monument subject、parenthetical label；表头/Markdown分隔符不当原文。个别艺术家仅记表格列示，不推断作者或执行角色；问号保留不确定性，地点和馆藏标签保留来源时点，不转成当前馆藏事实。Paltronieri、Blunt及1789年Bernard拍卖Lot 68的“Petoni—A pair of Triumphal Mausoleums”分别留存，不将Petoni与Paltronieri或Pittoni合并。注2登记1741年九项名单、Richmond归属混乱、Vertue在Goodwood之后记录的十项名单，以及Haskell“probably”提出的十四或十五幅解释；两名单共有主题不证明作品/版本同一。

新增39个候选（cand-9381–cand-9419）、82条精确提及及41条原书statement；正文5个脚注目标的marker 1（34条注释断言）及marker 2（7条）均链接至对应注释statement。Valeriani并列姓名、各纪念物版本、标签身份及跨名单对象对齐留待S3；关系均仍为S2候选。迁移脚本`chp10_p289_notes_migration.py`默认dry-run，检查来源/片段哈希、覆盖前态、候选序号、提及跨度、statement引句和外键；修复了无`label_key`行的读取分支、OCR `William HI`与印本`William III`的源跨度，以及Vertue名单跨L237–238的锚点后，dry-run通过再apply。应用前按后缀`.bak-s2-chp10-p289-notes-20261002`保存四表恢复副本。

应用后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；825段中433 complete、62 excluded、316 queued、14 partial；候选9,406、提及19,452、statement 8,686。`python -m pytest tests/test_audit_tables.py -q`通过；`git diff --check`退出码0，只有既有LF/CRLF转换提示。两条S5来源引用警告仍在，S2尚未完成。p.289正文与派生转录已complete，合并注释段覆盖扩至L544但整体仍partial；下一位置为L545。

## 第十章印刷页290注1–6迁移（2026-10-02）

对照`CHP-10.pdf`物理第19页迁移合并注释L545–550，并链接p.290正文16条带注statement。注1记录John Conduitt 1729年6月4日致McSwiny信件、Haskell报告的Conduitt papers/Kings College馆藏位置及其对A. N. L. Munby的致谢；原信未独立查阅。尾注`Haskell, 1967`因书目存在多个同年条目而保留为未定引用，不强行选择题名。注2将Devonshire与Shovel两个版本判断分别记录为Haskell的“must”推断；保留来源时点“now”，不把Barber Institute写作当前馆藏，不合并作品候选。注3 Vertue卷V页149仅作为引文定位；注4登记McSwiny致John Conduitt 1730年9月27日信，并与p.291同日书信引用保持为不同候选，留S3比较；注5登记Joseph Smith致Samuel Hill 1729年11月26日信及其Chaloner出版来源；注6回连Zanotti卷II第313页。

页图校读确认S0 L549脚注号印作5（OCR为6），L550卷号印作II（OCR为U），校正仅存于S2。新增9个候选（cand-9420–cand-9428）、24条精确提及和10条原书statement；marker 1–6均已链接到相应正文断言。迁移脚本`chp10_p290_notes_migration.py`默认dry-run，锁定全文与L545–550哈希、候选最大序号、coverage前态、正文marker状态及mention锚点；通过干跑后应用，四表备份后缀`.bak-s2-chp10-p290-notes-20261002`。应用后审计`s2_missing=[]`、`errors=[]`；全账本825段中433 complete、62 excluded、316 queued、14 partial；候选9,415、提及19,476、statement 8,696。两条既存S5来源引用警告与S2未完成提示仍在。合并注释覆盖扩至L550，仍为partial；下一位置L551。

## 第十章印刷页291注1–3迁移（2026-10-02）

对照`CHP-10.pdf`物理第20页迁移合并注释L551–553。注1记录Newton纪念碑铭牌、Joseph Perrot的设计归属，以及Boucher绘制的Newton medallion与黄道符号、其位于Fontenelle《Eloge》摘文上方的独立页面描述；复用Boucher、Newton、Fontenelle及《Eloge》候选，分别登记纪念碑、铭牌和medallion设计，不与p.288所述未明确完成的Newton tomb合并。注2记录Haskell经Malamani（1899，p.142）转述的1753年致Rosalba Carriera书信及McSwiny似未结清某笔账目的限定说法；发信人和账目性质不明，原信与引文页未独立查阅。注3确认McSwiny致John Conduitt、日期为1730年9月27日，并保留印本指向p.290注1的交叉引用；该目标注释实际描述的是1729年另一封信，不能作为同一性证据。正文将Canaletto书信日期记为1727年；保留正文与注3冲突。p.290注4另有相同寄收双方与日期的候选（cand-9425），与本处Canaletto书信的身份关系留S3比较。

新增7个候选（cand-9429–cand-9435）、17条精确提及和5条原书statement；p.291正文marker 1–3均链接至注释statement。印本校读仅记S2、不改S0：L552 `Garriera`校为`Carriera`；L553 `tom`校为`from`、`Conduits`校为`Conduitt`；正文L264的`Garriera`同样在页图上校读为`Carriera`。迁移脚本`chp10_p291_notes_migration.py`默认dry-run，锁定来源与行哈希、候选序号、coverage前态、marker状态、mention跨度及statement外键；dry-run通过后应用，四表恢复副本后缀`.bak-s2-chp10-p291-notes-20261002`。应用后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全账本825段中433 complete、62 excluded、316 queued、14 partial；候选9,422、提及19,493、statement 8,701。`tests/test_audit_tables.py`通过；两条既存S5 `source_ref`警告与S2未完成/partial提醒仍在。合并注释覆盖至L553，仍为partial；下一位置L554。

## 第十章印刷页292注1–6（2026-10-02）

对照`CHP-10.pdf`物理第21页，迁移合并注释源段L554–557，并将脚注1–6链接到正文7条statement。新增10个候选（cand-9436–cand-9445）、15条精确提及和6条原书statement。注1–5分别为Canaletto市场、Burney、Beckford、Finberg及Zuccarelli履历的书内引证；注6以1935年展览图录和Bjurström 1967支持Tessin生涯/收藏叙述。所引页码/研究未独立查阅，内部书目匹配仍待书目S2核对。印本校读只记S2、不改S0：L556脚注号印作5（OCR为8）；L557年份印作1935（OCR为`193 5`），姓氏印作`Bjurström`（OCR为`Bjurstrôm`）。

受控脚本`chp10_p292_notes_migration.py`默认dry-run，锁定来源与L554–557哈希、候选序号、mention跨度、statement锚点/外键、正文marker状态和coverage前态；应用前为四表留恢复副本`.bak-s2-chp10-p292-notes-20261002`。应用后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全账本825段中433 complete、62 excluded、316 queued、14 partial；候选9,432、提及19,508、statement 8,707。两条既存S5 `source_ref`警告及S2未完成/partial提醒仍在。合并注释覆盖扩至L557，仍为partial；下一位置L558。

## 第十章印刷页295注1–5（2026-10-02）

对照`CHP-10.pdf`物理第24页迁移合并注释L564–566。注1记录Algarotti分别委托Tiepolo、Piazzetta、Amigoni、Pittoni与Zuccarelli绘制历史题材的引述；注2保留Sartori关于Dresden作品的短引；注3–4记录Bellotto抵达Dresden、宫廷服务、1765年离开及Church of the Holy Cross画作的引文路径；注5记录Clemens August访问威尼斯的短引。所有引用均为原书来源指引，没有独立核读被引页面或据此新增事实。

新增6个候选、14条精确提及及6条citation statement；p.295正文注1–5标记均链接到相应注释statement。页图校读确认注5（OCR误作6）、`Kurfürst`和`Köln`，只记S2、不改S0。Rotari“left at this time”的时间含义仍未由本注消歧。合并注释覆盖扩至L566，下一位置为p.296注1（L567）。

## 第十章印刷页296注1–3（2026-10-02）

对照`CHP-10.pdf`物理第25页迁移合并注释L567–569，新增3个候选、8条精确提及和3条citation statement，并将p.296正文的三个脚注标记链接至注释。注1为Von Freeden 1956引文，注2为Levey 1959 p.192，注3为Chapter 7、Claretta 1893及Griseri 1957的引文路径；逐项匹配本地书目。随后核对第21章书目，将Von Freeden 1956匹配到Max H. von Freeden的《Das Meisterwerk des G. B. Tiepolo》（München, 1956）；被引书及相关页均未独立查阅。p.296作者候选与p.293的Von Freeden候选仍分开，交S3作全局身份判断。

候选、提及及statement的总量分别为9,454、19,572和8,725。合并注释段覆盖至L569并保持partial；下一源范围为p.297注1–6（L570–574）。
## 第十章印刷页297注1–6（2026-10-02）

对照`CHP-10.pdf`物理第26页迁移p.297脚注。注1的完整正文不在复合注释L570：其开头“Gabrielli, 1950...”位于L570，后续Juvarra/Ricci及画派分配内容保存在规范OCR正文段L343。页图确认L343与印本注1续文相符；整章平行OCR`10_CHP-10.md`的L601–602也含同文，但未作为第二份语料或新增锚点。故以L343为事实statement锚点，L570只登记Gabrielli引文定位，不重复生成注1事实。

注1分层记录Juvarra于1723年委托Marco Ricci绘画以示Castello di Rivoli方案；另记录Juvarra对Roman painting的偏好及两幅Pannini、两幅Locatelli作品与各一幅Venetian、Turinese画家的数量比较。原文未说明Ricci画是否计入该作品数量，保留未决；具名的画家、两个未具名画家、画作组和地点分开建候选。Gabrielli（1950，pp.204–211）在本地书目未匹配，Viale（1950–51，p.161）匹配到本地条目；被引页面均未查阅。

注2 Battisti（1958，pp.273–297）匹配本地书目条目“Juvarra a Sant’Ildefonso”；注3记录Haskell关于Amigoni出生地、非出国期间的威尼斯工作生活、Giaquinto于1753年随赴Madrid，以及Giaquinto对年轻Goya影响的比较判断。注3的1753年叙述不表述为Amigoni首次或唯一赴Madrid，和正文所述1739年赴Madrid分开保存。注4 Brunetti（1914）匹配本地书目；注5 Donzelli pp.209、90匹配《I pittori Veneti del Settecento》，并将既有p.82 citation candidate `cand-9297`补充为同一书目对象；注6“A. Longhi”依据本地书目匹配Alessandro Longhi 1762年《Compendio》。相关书籍、文章和引文页均未独立查阅。

新增16个候选（cand-9468–cand-9483）、33条精确提及和11条statement；脚注1–6的正文marker均已链接。p.297正文源段覆盖扩至L333–343并转complete；复合注释段覆盖扩至L574、仍为partial，下一源位置为p.298注1（L575）。受控脚本`chp10_p297_notes_migration.py`默认dry-run，核验来源资产与两处段落哈希、最大候选序号、脚注前态、提及跨度、书目匹配和外键；apply前四表恢复副本后缀`.bak-s2-chp10-p297-notes-20261002`。应用后账本为825段：434 complete、62 excluded、316 queued、13 partial；候选9,470、提及19,605、statement 8,736。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；定向测试9项通过。仍有两条既存S5 `source_ref`警告、316段queued和13段partial；S2尚未完成。

## 第十章印刷页298注1–3（2026-10-02）

对照`CHP-10.pdf`物理第27页处理合并注释L575–577。注1复用已有Bellotto 1955展览图录候选`cand-9462`，与本地书目标题、年份相符；图录未独立查阅。注2只写“Novelli.”，复用既有回忆录候选`cand-8363`并连接到本地唯一的Pietro Antonio Novelli《Memorie della vita》（Padova, 1834）条目，作为可能匹配记录；注释未给页码，原书未查。注3是“See later. Chapter 14.”内部交叉引用，登记到第14章规范源段`chp-14:14_CHP-14_intro:l55-61`；该目标仍queued，不能作为正文获取《埃及艳后之宴》或Algarotti委托事实的证据。

新增2条精确提及、3条statement，正文p.298的Bellotto Warsaw views、Novelli拒绝赴俄邀请及Algarotti为Augustus III取得《埃及艳后之宴》三个marker解除pending。没有新增实体候选。合并注释段覆盖扩至L577并保持partial，下一位置为p.299注1（L578）。迁移脚本`chp10_p298_notes_migration.py`默认dry-run，核对来源和脚注哈希、候选序号、候选复用、正文marker、锚点和覆盖前态；apply前为mentions、statements及coverage留恢复副本`.bak-s2-chp10-p298-notes-20261002`。应用后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；825段中434 complete、62 excluded、316 queued、13 partial；候选9,470、提及19,607、statement 8,739。两条既存S5来源引用警告、316段queued和13段partial仍未变化；S2尚未完成。

## 第十章印刷页299正文与注1–4（2026-10-02）

对照`CHP-10.pdf`物理第28页处理p.299正文`chp-10:10_CHP-10_intro:l354-366`及合并注释L578–581。正文原有footnote marker 1–4已逐项链接；L366是注4续文（Smith–Gori通信日期范围及Guicciardini于1738年出版的书内说法），并入同一注释，不另造重复statement。页图确认脚注印本馆藏号为`MSS. B. VIII, 4`（OCR作`MSS. B. Vin, 4`）；OCR将1735、1737拆写的年份仅按印本校读用于S2，未改写S0。L580姓氏按印本记录为`lett me know`，保留扫描校读记录。

注1登记Parker 1948及Smith遗嘱等文献定位；注2登记Lodovico Gabrieli公证档案系列、Avogaria di Comun Civil 263/16争议记录；注3登记Public Record Office State Papers 99/60中1714年5月18日匿名英国Resident来函、Signor Tron及受邀地点“Messrs Williams and Smith”。这组商人身份不与Joseph Smith合并。注4登记Smith致A. F. Gori通信的馆藏与日期范围，并记录Haskell关于Guicciardini《Histories》1738年出版的引证。所有档案、信件和书目仅依本书引证建账，未独立查阅。复用既有Smith–Gori通信候选`cand-9229`；p.306所引1737–38宝石/浮雕部分仍留待后续身份/语境比较，不据此合并相关作者身份。

新增11个候选（cand-9484–cand-9494）、31条精确提及和9条原书statement。修正既有正文中Guicciardini人物与《Histories》作品提及重叠的问题，拆为独立人物和档案作品；Museum Etruscum从索引子目候选拆出为独立档案候选。注释中的Gabrieli、Avogaria机构/档案、State Papers、匿名Resident、Signor Tron、未定Williams and Smith群体、Biblioteca Marucelliana等候选保留各自类型及不确定状态。受控迁移脚本`chp10_p299_notes_migration.py`默认dry-run，校验来源/片段哈希、候选自然键及前态、正文marker、提及跨度、statement锚点与coverage；应用前四表备份后缀`.bak-s2-chp10-p299-notes-20261002`。

应用后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；825段中435 complete、62 excluded、316 queued、12 partial；候选9,481、提及19,637、statement 8,748。`python -m pytest tests/test_audit_tables.py -q`通过9项；`git diff --check`退出码0（只有既有LF/CRLF提示）。两条既存S5来源引用警告和S2全书未完成提醒仍在。正文p.299转complete，合并注释段覆盖至L581、仍为partial；下一位置p.300注1（L582）。

## 第十章印刷页300注1–7（2026-10-02）
处理合并注释L582–588并链接正文脚注marker。注4续文L379、注7馆藏号续文L380并入原注。新增11个候选（cand-9495–cand-9505）、33条精确提及和11条statement；被引材料未独立查阅。
## 第十章印刷页301注1–7（2026-10-02）
处理合并注释L589–594，新增13个候选（cand-9506–cand-9518）、41条提及和10条statement。注4登记Poleni致Smith两信及Smith回信；申请绘图保留为关系候选。页图确认注5印本编号为5、OCR L592误作6，未改S0。Grosley缩写与本地书目、Arrighi-Landini注释年份不一致处保持未决；相关材料未独立查阅。
## 第十章印刷页302正文（2026-10-02）
正文L391–399已有迁移，本次补录其语义处理：新增10个候选（cand-9186–cand-9195）、50条提及和16条statement；p.301遗留的“Lady”按语境识别为Mary Wortley Montagu。正文末句续于p.303，coverage保持partial；L400脚注OCR摘句与合并注释L600去重。
## 第十章印刷页302注1–5迁移（2026-10-02）
处理合并注释L595–599，新增5个候选（cand-9519–cand-9523）、21条提及和7条statement，并链接五个正文脚注marker。注1记录James Adam致Robert Adam、1760-08-20书信；John Fleming另立候选。注2–5的引文和可能书目匹配未独立核读。
页图校读只记S2、不改S0：L595印作“I am”而OCR为“1 am”；L599印本注号为5而OCR为6。L598遗漏的意大利文引文另存为派生转录段。受控迁移脚本经dry-run和前置校验后应用，恢复副本已保留。审计errors为空、s2_missing为空；定向测试9项通过。全账本826段：438 complete、62 excluded、316 queued、10 partial；候选9,510、提及19,732、statement 8,776。下一位置p.303注1（L600）。
## 第十章印刷页303正文补记与注1–6（2026-10-02）

p.303正文L403–409及合并注释L600–604完成语义迁移。正文L409同时包含注5意大利文续引和注6的Malamani定位；页图核对后确认续文已经在规范OCR中，因此没有新增重复转录段。L600印本献辞缩写为“D.D.D.”（OCR `D.DP.`）；L409印本读作“Lunedì desidererei ... a confronto ... all’amico”，OCR分别为`Lunedi`、`desiderei`、`à confronto`、`all’atnico`。校读只记录于S2，S0原文不改。

新增10个候选（cand-9524–cand-9533）、30条提及和8条statement。注1将献辞对象保留为24幅Marco Ricci版画组，与正文提及的1743年书籍是否同一不提前合并，也不依据含混的拉丁印记指定刻印者。注2、4只记录Cust p.153定位；注3按Malamani刊出的Carriera 1726-05-21账目记录《四季》拟寄伦敦给Smith，未记录金额，也不能证明付款或实际寄出。注5记录无日期Smith致Carriera信：Smith希望比较两幅Winter后再决定寄哪一幅给“朋友”；它与Haskell正文“另一幅已寄给朋友（或客户）”存在未解的时间/结果张力，受赠人不明。注6只记录Malamani 1899 p.134定位。上述被引书页、账目刊本和信件均未独立查阅；书目/身份匹配留后续阶段。

正文marker 1–6已解除pending；对付款与委托对象陈述补入相应证据边界。受控脚本`chp10_p303_notes_migration.py`默认dry-run，核验S0全文与L600–604哈希、候选最大ID、coverage前态、marker、锚点、提及重叠和statement外键；apply前四表备份后缀`.bak-s2-chp10-p303-notes-20261002`。审计先发现两条新增候选误将L409指向注释段，按该行实际所属的正文段修正source_ref并另存恢复副本；随后`python scripts/audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`。`python -m pytest tests/test_audit_tables.py -q`退出码0，`git diff --check`无空白错误（仅有Git LF/CRLF提示）。当前全账本826段：438 complete、62 excluded、316 queued、10 partial；候选9,520、提及19,762、statement 8,784。覆盖范围为注释L492–604、p.303正文L403–409，后者因正文末句续至p.304 L412而保持partial。下一位置p.304注1（L605）。
## 第十章印刷页304注1–7（2026-10-02）

对照`CHP-10.pdf`物理第33页处理合并注释L605–610，并链接p.304正文7个marker。注1记录三个威尼斯档案定位，引用范围涉及Smith在Mogliano乡间住宅的租赁/购置；因注释未逐项说明哪条记录支持哪一交易，且档案未查阅，不作一一归属。注2记录Smith于1729年11月将Piazzetta作品寄给Samuel Hill的Haskell转述，所引Chaloner未独立查阅。注3为K. T. Parker p.9起的定位。注4保留John Conduitt在1730年6月要求Smith向Canaletto采购三幅画的引语；其“见p.290注1”目前指向1729年Conduitt致McSwiny信，来源链不一致。注5登记Smith致Samuel Hill的1730-07-17信及Chaloner刊引；注6登记Sirén p.107；注7登记Christie's 1776-05-16 Smith拍卖目录及Haskell称其中另列十四幅画的说法。Appendix 5仍待S2阅读。

新增11个候选（cand-9534–cand-9544）、31条提及和7条statement；没有独立阅读所引档案、文章、信件或拍卖目录。页图校读仅记S2、不改OCR：L605 `£ 84V`为叶码`f.84v`，`13 5V`读作`135v`；L609 `Siren`印作`Sirén`；L610 `foseph`印作`Joseph`。受控脚本`chp10_p304_notes_migration.py`默认dry-run，锁定来源/行段哈希、候选序号、coverage前态、markers、提及跨度及statement外键；apply前四表恢复副本后缀`.bak-s2-chp10-p304-notes-20261002`。应用后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；`tests/test_audit_tables.py`退出码0；`git diff --check`无空白错误（仅Git LF/CRLF提示）。当前账本826段：438 complete、62 excluded、316 queued、10 partial；候选9,531、提及19,793、statement 8,791。合并注释coverage至L610；p.304正文L412–421仍partial，末句续至p.305 L424。下一位置为p.305注1（L611）。

## 第十章印刷页305注1与p.306注1校接（2026-10-02）

对照`CHP-10.pdf`物理第34–35页复核脚注。p.305页底仅见注1 `Constable, 1976.`，标记位于“almost impressionistic”之后；“get to know it”之后没有印刷标记，OCR尾部撇号是正文标点。因此保留`st-chp10-p305-smith-first-six-views`的注1并解除pending，从Visentini出版和Tessin后续报告断言中移除误加的marker 2及其待定注释链接。原文关于独家委托与Canaletto近乎停止为Smith工作之间的张力保持不变。

p.305注1只给姓氏和年份，新增未定题名与页码的archive候选`cand-9545`；“Constable”复用身份未决的`cand-9368`，不与John Constable合并。复读p.306整页后确认注1的印刷marker在L437“Visentini”之后；Blunt与Croft-Murray第67页起的引文被OCR并到L441的Breval雕像文字尾部。此前误连到Breval叙述的anchor已纠正为Smith保留Visentini原稿的断言；Breval段本身没有脚注marker。复用联合书目候选`cand-9340`和作者候选`cand-0379`、`cand-9339`；印本`ff.`与OCR `if` 差异只记在S2。这样L612才是p.306注2。

新增1个候选、5条提及和2条citation statement。受控脚本`chp10_p305_note1_migration.py`默认dry-run，锁定OCR资产及L428/L441/L611行哈希、候选序号、coverage前态和marker；四张表应用前备份为`.bak-s2-chp10-p305-note1-20261002`。初次审计发现正文statement引文超出其OCR源句，遂将引文截回源句子串，并单独记录OCR内嵌的脚注；整页图复核后修正p.306注1的marker锚点。anchor修复曾因coverage文件句柄未关闭而在Windows替换失败；使用恢复副本回滚半完成写入、关闭句柄后dry-run并应用成功。最终`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；`python -m pytest tests/test_audit_tables.py -q`通过11项，`git diff --check`退出码0（仅Git LF/CRLF提示）。当前账本826段：438 complete、62 excluded、316 queued、10 partial；9,532候选、19,798提及、8,793 statements。下一位置p.306注2（L612）。

## 第十章印刷页306注2–6及p.307注1–4（2026-10-02）

对照`CHP-10.pdf`物理第35–36页完成合并注释L612–620，并将p.306注2–6、p.307注1–4的11个正文statement marker链接至相应注释记录。新增候选`cand-9546–cand-9556`共11项，26条提及、10条statement。新对象包括Smith信中所指Hadrian头像、Smith致Gori的两封1737年信、Zanetti 1751年信、Zabeo书目与作者、Vivian 1962年论文与作者、可能对应本地Canaletto书目的Brandi著作及作者，以及Smith medal cabinet。跨章身份不在S2合并；medal cabinet保留未分类，Brandi书目对应保留可能匹配状态。

p.306注2只记录对p.299注4的内部交叉引用；注3保存1737-03-30信件及引文；注4记录Lorenzo Masini对Smith medal cabinet的转述评价，Zabeo p.16未独立查阅；注5的Girolamo Zanetti信日期在L615，B.VIII,13、p.170定位及意大利文引文分布于同段的页级OCR L442–443，并作为同一来源链链接，信件未独立查阅；注6记录Smith致Gori的1737-04-13信和关于古代/近代作品及Hadrian头像的判断。p.307注1页图显示卷号为罗马数字I（OCR为1）；注2引Blunt与Croft-Murray p.11；注3引同书p.14、pp.19–23及Vivian 1962 pp.330–333（OCR为`PP330-3`）；注4的Brandi pp.60 ff.（OCR为`if`）可能对应本地书目所列Cesare Brandi《Canaletto》，书目年份`i960`未核，保留未决。所引档案、文章、书页和信件均未独立查阅。

受控脚本`chp10_p306_p307_notes_migration.py`默认dry-run，核验来源全文SHA、L612–620与L442–443分段SHA、候选序号、coverage前态、正文marker、mentions跨度及statement外键；apply前为四表保存`.bak-s2-chp10-p306-p307-notes-20261002`。应用后`python scripts/audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；仍提示316段queued、10段partial，并保留两条既存enrichment `source_ref`警告。当前账本826段：438 complete、62 excluded、316 queued、10 partial；候选9,543、提及19,824、statement 8,803。合并注释coverage扩至L620；p.306正文L436–443与p.307正文L446–454继续因跨页句保持partial。下一位置p.308注1（L621）。

## 第十章印刷页308–310注释与p.302–306跨页coverage收口（2026-10-02）

对照`CHP-10.pdf`物理第37–39页迁移合并注释L621–634，并补入p.308页级OCR续文L466。p.308注1称overdoors多数作于1744年，Horses of St Mark’s按A.U.C.纪年；印本L466补出A.U.C. 1332 = 1753，并称Blunt将其解释为Canaletto意外多加一个x，所引Exhibition of The King’s Pictures no.440仅作为书内定位。注2引Cust p.153并说虚构场景似受Padua启发。注3所引Blunt 1958 pp.283–284匹配本地书目；Vivian 1963 pp.157–162与本地Italian Studies条目pp.54–66不符，保留为未匹配引用，未推测题名或替换页码。

p.309注1 Cust p.161；注2 [Andrea Memmo] 1786 p.1；注3 Haskell 1958年Burlington Magazine文章pp.212–213及Chapter 14内引；注4 Gradenigo p.5；注5 G. A. Moschini 1924 p.82意大利文引语，拆为Smith分别作为Zais与Zuccarelli“great protector”的两个relation candidate，不升级为正式关系；注6 Blunt和Croft-Murray p.24。页图确认OCR L628/L629标签6/8应为印本5/6。p.310注1以Orlandi pp.79–80、206和Fleming 1959 p.171支持Robert Adam 1757年到Smith Mogliano住宅参观及其对收藏的评价；注2 Parker p.11；注3登记Lodovico Gabrieli公证簿7564、p.12v、1756-03-22的具体定位；注4登记Smith致William Pitt 1760-10-29信，PRO State Papers 99/68 f.96；注5登记James Adam 1760-08-20与08-27信的刊引及Fleming 1962 p.270；注6为Appendix 5内部交叉引用。页图确认L634 OCR标签6/8对应印本5/6。新增候选cand-9557–cand-9567（11项）、45条精确提及、17条statement；p.308–310共15个正文脚注marker解除pending。引文页、书信、公证簿与拍卖目录均未独立查阅；具名作者同一性留待S3。p.310注4只链接旅行计划引语，删除从“Smith辞去领事职务”陈述误挂的marker4。

受控脚本`chp10_p308_p310_notes_migration.py`默认dry-run，固定来源全文、L621–634及L466哈希、候选顺序、覆盖前态、正文marker、mentions锚点和statement外键；apply前四表恢复副本后缀`.bak-s2-chp10-p308-p310-notes-20261002`。另以`chp10_crosspage_coverage_close.py`核对相邻页statement双向交叉引用，收口p.302 L399→p.303 L403、p.303 L408→p.304 L412、p.304 L421→p.305 L424、p.305 L433→p.306 L436、p.306 L441→p.307 L446五个partial段，更新`s2-coverage.csv`并保存`.bak-s2-chp10-crosspage-close-20261002`。最终账本826段：448 reviewed/complete、62 excluded、316 queued、0 partial；9,554候选、19,869提及、8,820 statement。`audit_tables.py --summary`返回`s2_missing=[]`、`errors=[]`；余有两条既存enrichment `source_ref`警告及316段queued提示。`python -m pytest tests/test_audit_tables.py -q`通过；`git diff --check`通过（仅既有LF/CRLF提示）。全书S2未收口；下一源段为`chp-10:10_CHP-10_sec_ii:l1-1`。

## 第十章第二节文件标题及开篇段（2026-10-02）

规范源段`chp-10:10_CHP-10_sec_ii:l1-1`是文件标题`# 10 CHP-10 sec ii`，仅重复章节元数据，无书内陈述，故以理由排除，未造候选或提及。开篇源段L3–5的`MARSHAL SCHULENBURG`副标题与比较性段落对照物理第39页图像迁移：Haskell称Schulenburg在与Joseph Smith大致同时于威尼斯委托和收藏绘画，其背景和活动差异反映在审美品味上；“没有记录二人关系密切”保留为记录限语，“常雇用相同艺术家”因人名未出现，不建人物—艺术家关系端点。新增4条精确提及和4条statement，无新候选；Schulenburg复用`cand-2401`，身份与类型留待S3。受控脚本`chp10_sec_ii_l3_5_migration.py`默认dry-run，核验来源资产和段哈希、既有候选、coverage前态、mention锚点及statement外键；写前为mentions、statements和coverage保存`.bak-s2-chp10-sec-ii-l3-5-20261002`恢复副本。当前账本826段：449 reviewed/complete、63 excluded、314 queued、0 partial；候选9,554、提及19,873、statement 8,824。审计`s2_missing=[]`、`errors=[]`；审计测试通过。下一段`chp-10:10_CHP-10_sec_ii:l7-15`包含p.311正文与首个脚注，需对照下一页图像继续。

## 第十章印刷页311正文（2026-10-02）

对照`CHP-10.pdf`物理第40页处理规范源段`chp-10:10_CHP-10_sec_ii:l7-15`。源OCR页标`[Page 1661]`与扫描印本不符；页眉和页码确认实际为印刷p.311。扫描校正OCR`scries`为`series`、`I747?`为1747（带脚注3）、`claps`为`clapt`，S0来源文本不改。逐行登记Schulenburg出生与军旅、在Corfu抵御土耳其攻击、艺术纪念、Venice授予雕像与终身年金、旅行居住、Hanoverian亲缘、王侯肖像与宫廷往来、Frederick请求及未具名英国贵族的轶闻和1740年遗嘱陈述。新增候选`cand-9568–cand-9584`共17个、61条提及和26条statement；用`cand-8838`指政治实体Republic of Venice、`cand-2719`指城市Venice，`cand-2405`保留索引子目“defence of Corfu”，`cand-9580`单列书内所述1715–1716防守事件，与既有`cand-8119`（1716 siege）留待S3比较。家族、群体与未具名人士保留源文限定，不据此生成KU或正式关系。

句末“determined to maintain”续至同文件L18（印刷p.312）；p.311脚注1–6位于文件后置注释区，尚未迁入或链接。故coverage现为reviewed/partial，正文脚注marker仍pending；note 6所引Rockingham letter尚不能证明未具名贵族身份。受控脚本`chp10_p311_migration.py`默认dry-run，核验来源与段哈希、候选前态、提及跨度和statement外键；apply前为候选、提及、statement、coverage四表保存`.bak-s2-chp10-p311-20261002`。结构审计发现`cand-9584`的来源引用不接受行范围，已按契约修正为起始行L13并另存候选表恢复副本；修正后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，`tests/test_audit_tables.py`通过。

## 第十章印刷页312正文（2026-10-03）

按`CHP-10.pdf`物理第41页处理源段`chp-10:10_CHP-10_sec_ii:l17-32`的正文L18–26。L18补闭p.311遗嘱句，新增延续statement并回链前段statement；p.311 coverage仍为partial，因为其脚注1–6尚未处理。p.312正文记录Schulenburg肖像委托及艺术家群、Simonini战役画和“apparently took him on his campaigns”限定、1726年Canaletto《Corfu》景观（可能据版画）、对艺术家的慷慨、1724年向G. B. Rota购买、Mantua公爵收藏来源、作品归属、Bertos青铜群与骑马肖像、Corradini为Corfu雕像所作modello，以及被称作Giotto作品的未名画。复用索引候选`cand-1918`、`cand-2411`、`cand-0525`、`cand-8632`等；新增`cand-9585–cand-9589`五个作品候选。群体和具体作品分开；modello与p.311所述雕像分开；Mantua藏品流转不与更早的另一组藏品合并；归属、交易路径和未名对象均按原文限定。

该源段L26止于“not so much as an”，续至p.313 L73，故保持partial。段内L27–32是p.312页脚注的局部OCR摘录；与后置规范注释段L273–349的p.312注1–6（L279–283）重复或不完整，本轮不重复迁移。页图确认印本存在OCR遗漏的脚注5、6标号，并将两处OCR `Corfu` 校读为印本`Corfù`；S0保持不变。`chp10_p312_migration.py`默认dry-run，固定全文/段SHA、计数前态、ID、提及精确跨度、statement引句和外键；写前四表备份后缀`.bak-s2-chp10-p312-20261003`。审计发现早期coverage更新覆盖了p.311原有校读记录，已从受控备份恢复并追加后续状态，另存`.bak-s2-chp10-p312-coverage-note-fix-20261003`。

## 第十章图版53题注（2026-10-03）

按`CHP-10.pdf`物理第42页核对`chp-10:10_CHP-10_sec_ii:l34-53`。`[Page 53]`为图版号；竖排图版题头是“German Patrons in Eighteenth-Century Venice”。图版53a题注为“Piazzetta: Marshal Schulenburg”，53b为“Amigoni: Sigismund Streit”。原OCR把竖排英文和题注倒序、交错输出；mentions保留可精确定位的原OCR片段，在note和statement中记录印本读法，不改S0。复用Amigoni的Streit肖像索引候选`cand-0099`，新增`cand-9590`表示图版53a的独立Piazzetta肖像；本段新增6条提及和2条题注statement，并标complete。受控脚本`chp10_plate53_migration.py`默认dry-run，固定源/段SHA、表计数、候选和提及/statement锚点；四表恢复副本后缀为`.bak-s2-chp10-plate53-20261003`。此时全账本826段：450 complete、63 excluded、311 queued、2 partial；候选9,577、提及20,008、statement 8,869。p.311及p.312正文coverage仍partial，分别等待规范注释段与p.313续句。下一游标为`chp-10:10_CHP-10_sec_ii:l55-56`。

## 第十章图版54题注（2026-10-03）

按`CHP-10.pdf`物理第43页核对`chp-10:10_CHP-10_sec_ii:l55-56`。源段`[Page 54] / P : Idyll`中的页标为图版号；印本题注为“PIAZZETTA: Idyll”。复用`cand-1901`（Piazzetta）与`cand-4076`（既有《田园》work候选），新增2条精确提及及1条`relation_candidate=true`的题注statement，不新增候选。仅登记题注所示归属；不从节标题推断赞助、所有权或委托。S0 OCR保持不变。受控脚本`chp10_plate54_migration.py`默认dry-run，固定来源资产/段SHA及表前态，验证候选、span和ID；apply前为mentions、statements、coverage三表保存`.bak-s2-chp10-plate54-20261003`恢复副本。当前全账本826段：451 reviewed/complete、63 excluded、310 queued、2 partial；9,577候选、20,010提及、8,870 statement。`audit_tables.py --summary`返回`s2_missing=[]`、`errors=[]`；`python -m pytest tests/test_audit_tables.py -q`通过（11项）。下一源段为`chp-10:10_CHP-10_sec_ii:l58-60`。


## 第十章图版55题注（2026-10-03）

按`CHP-10.pdf`物理第44页核对规范段`chp-10:10_CHP-10_sec_ii:l58-60`。印本题注为“Canaletto: Dedicatory frontispiece to Etchings”及“Marco Ricci: Village Scene”。复用既有艺术家、作品候选，新增5条提及和2条题注statement，不新增候选；题注不据以推断委托或所有权。受控脚本`chp10_plate55_migration.py`默认dry-run，核验资产/段哈希、前态和锚点；写前备份后缀`.bak-s2-chp10-plate55-20261003`。

## 第十章图版56题注（2026-10-03）

按`CHP-10.pdf`物理第45页旋转校读规范段`chp-10:10_CHP-10_sec_ii:l62-70`。印本题注为“Marieschi: Picture Exhibition at Church of S. Rocco”。OCR将竖排题注倒序并拆分Marieschi首字母；复用既有Marieschi、作品及教堂候选，新增6条提及和1条关系候选statement，不新增候选。受控脚本`chp10_plate56_migration.py`默认dry-run，核验资产/段哈希、前态和锚点；写前备份后缀`.bak-s2-chp10-plate56-20261003`。

## 第十章印刷页313正文（2026-10-03）

对照`CHP-10.pdf`物理第46页迁移规范段`chp-10:10_CHP-10_sec_ii:l72-81`。L73接完p.312关于Guardi角色的跨页句；更新p.312旧statement为薪酬陈述，并与本段的copyist/hack角色对照statement互链，避免把跨页两部分误作重复。正文覆盖Guardi 1737年自作历史画委托、应复制的威尼斯大师作品及同时代艺术家作品、肖像数量/分配、Haskell对存世作品质量的评价、1742–1743年土耳其场景及Van Mour版画、Schulenburg委托和收藏转向Pittoni/Piazzetta、Pittoni历史画与Piazzetta patronage。新增5个候选（`cand-9591`未题名作品组，`cand-9592`未定身份Scipio，`cand-9593`Alexander the Great，`cand-9594` Polyxena，`cand-9595` Iphigenia）、74条提及和19条statement。Polyxena、Iphigenia保留来源候选而不强制归入person；作品数量、身份及原文的推断语气不扩张。

页图确认印本校读：`copyistand`→`copyist and`、`ofhis`→`of his`、`Camera`→`Carriera`、`only.rarely`→`only rarely`、`did notdie`→`did not lie`、`oshistory`→`of history`。p.313脚注1–4可见于页下注，但规范注释段L284–287尚待按来源顺序迁移；正文L81末句续至p.314 L84，因此coverage暂为partial。复核确认原文与印本均作`melodramas`，已撤销迁移时误加的OCR校正说明。修正statement qualifier与coverage note前分别保存`.bak-s2-chp10-p313-print-correction-20261003`；初次迁移四表恢复副本后缀`.bak-s2-chp10-p313-body-20261003`。下一待处理段为`chp-10:10_CHP-10_sec_ii:l83-93`。

## 第十章印刷页314正文（2026-10-03）

对照`CHP-10.pdf`物理第47页处理规范段`chp-10:10_CHP-10_sec_ii:l83-93`。逐行登记Schulenburg以不同画类任用Piazzetta、由其代购通常为佛兰德斯的市场作品、对荷兰与佛兰德斯绘画的偏好、Nazari/Nogari头像组、Piazzetta题材与库存描述、自然主义和genre绘画的评价、Ceruti作品、Canaletto采购限制，以及Marieschi、Carlevarijs、Cimaroli、Joli、Marco Ricci和Zuccarelli作品。新增30个候选（`cand-9596`–`cand-9625`）、79条提及和24条原书statement。保留`some twenty`、`probably`、`perhaps`、`one or two`及作者判断的语气；Cologne/Chicago只登记为城市，不将两件牧歌画逐一分配到城市或与图版54强合并。库存引文、两条田园画描述、作品组和评论解释分开记录。

收藏本身没有现有类型，新增类型待决候选`cand-9622`；“his palace”复用p.311已登记的Palazzo Loredan候选`cand-9571`。第93行“his estates in”是跨页目的地片段，新增庄园place候选`cand-9623`及被装箱作品组`cand-9625`，送画statement标作关系候选并链接下一段p.315。p.314脚注1–4分别对应规范注释L288–291，均留待按源序处理；p.313延续句已与本页L84完成互链，p.313自身仍等L284–287。扫描确认L93印本为“sending crates”；只记录OCR校读，不改S0。

本次表应用前四表恢复副本为`.bak-s2-chp10-p314-body-20261003`。首轮审计发现L88第二个“Venice”误复用第一个词的偏移，已将`m-s2-ch10-p314-0054`从1827更正到2239，恢复副本为`mentions.csv.bak-s2-chp10-p314-offsetfix-20261003`；迁移脚本同步指定第二次出现。修复后`python scripts/audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；`python -m pytest tests/test_audit_tables.py -q`通过9项；`git diff --check`退出码0（保留既有LF/CRLF提示）。当前账本826段：453 reviewed/complete、63 excluded、306 queued、4 reviewed/partial；9,612候选、20,174提及、8,916 statement。p.314 coverage为partial；下一段`chp-10:10_CHP-10_sec_ii:l95-106`。

## 第十章印刷页315正文（2026-10-03）

对照`CHP-10.pdf`物理第48页迁移规范段`chp-10:10_CHP-10_sec_ii:l95-106`。L96的`Germany.`补完p.314送画至庄园的跨页句；statement与前段双向链接，并把目的地限制为德国的未具名庄园。L96–99比较Smith和Schulenburg收藏中的画家构成、收藏偏好及作品数量；“none particularly favoured”保留为偏好限定，“far greater number”无数值，不补造数量。L102–106处理Sigismund Streit的比较位置、商业生涯、居住迁移、收藏、两次遗赠、教育、葬地、对Venice的感情及Canaletto作品与个人生活的联系；“seems”“about”“some”“strikingly high proportion”等语气和集合/子集边界均保留。新增候选`cand-9626–cand-9647`共22项、59条提及、35条statement。Smith与Schulenburg收藏、Streit收藏、Streit四十八幅作品及若干画家作品组分开表示；现有类型无法表达的收藏、未具名机构组和比较群体留待决，不将多个作品组误认成同一批实物。父亲只以铁匠职业识别，未具名演讲作为event候选；本段不处理跨章身份或正式关系。

扫描校读记为S2而不改S0：`cither`→`either`、`-was`前置连字符删去、`represented----`按印本行末破折号解释；L96的`age,-Tiepolo`标点按印本破折号归一。L97脚注1待规范注释L292，L103脚注2待L293；L106句末`about`续至p.316 L109，因此p.315 coverage为partial。p.314的脚注1–4仍待L288–291，虽送运目的地已由本页闭合，其coverage仍为partial。

复核图版53b后修正既有错映射：将原先误映为Amigoni人物的题注全名改映Sigismund Streit (`cand-2519`)，另将`cand-9636`登记为Amigoni肖像作品，Amigoni (`cand-0099`)仅作作者；据印本题注“Amigoni: Sigismund Streit”保留作品—作者—坐像者三者区分。受控脚本`chp10_p315_migration.py`默认dry-run，锁定来源与段哈希、表前态、候选/提及/statement ID、精确提及跨度、statement原文锚点及外键；dry-run通过后应用，四表恢复副本后缀`.bak-s2-chp10-p315-20261003`。应用后审计为`s2_missing=[]`、`errors=[]`；`python -m pytest tests/test_audit_tables.py -q`通过。全账本826段：453 complete、63 excluded、305 queued、5 partial；9,634候选、20,233提及、8,951 statements。当前下一段`chp-10:10_CHP-10_sec_ii:l108-117`。

## 第十章印刷页316正文（2026-10-03）

对照`CHP-10.pdf`物理第49页处理规范段`chp-10:10_CHP-10_sec_ii:l108-117`。先按来源哈希核实所用Markdown与PDF；PDF页图确认OCR的`Queen.of`印本为“Queen of”、`himself-and`为“himself and”，且`Ricci`后的破折号已与印本一致，故后者不再登记为OCR校正。L109闭合p.315“关于其画作”的断句：两幅个人生活相关Canaletto景色分别是从Campo S. Sofia望向Rialto的Grand Canal景色，以及描绘其商业活动所在地Campo di Rialto的另一幅；第一幅前景有Streit立于贡多拉，后景Palazzo Foscari为其住所。两幅作品分别登记，并与p.315所建两幅生活场景组相连。

L111新见两幅节庆夜景及Canaletto追随者绘制的Doge游行图；将Vigilie di S. Pietro、Vigilie di S. Marta作为独立event候选，后一事件的“最受欢迎”判断保留为Haskell陈述。游行画组、未名追随者、未名Doge与未具名官方游行分别记录；脚注2或将补充作品归属，当前不据此推断Doge身份或追随者名单。L112的毁佚寓意画‘Glory of Venice’单列作品。L113记录Streit与Schulenburg共享的王族肖像品味、Antoine Pesne友谊及Pesne受托为Frederick和未具名Prussia王后作肖像；妻后身份不从称号反推。父亲复用`cand-9641`，母亲与姐妹作为未具名人物候选，肖像组与四幅Streit自画像分开；Plate 53b引用未确定四幅中的具体作品。

L114–115记录Haskell对Schulenburg、Smith、Streit的画家收藏比较以及Amigoni为Streit所作肖像和另外十幅画（1739–1746）。四个带题名/主题表达的Amigoni画作候选与其他作者的同题作品分开，保留“似乎”“doubtless”等作者判断，并记录作品被描述为旧约和神话题材、牧歌/轻情色调及与Ricci、Pittoni的风格比较。L116–117复用Zuccarelli、Nogari和Rembrandt，分开登记两幅具体Nogari奇想式半身肖像、‘teste di fantasia’术语、四幅Education寓意画和其他教化题材作品；“最受欢迎”“唯一另有作品被充分代表的艺术家”“progressive circles”等均保留为书内语气。新增37个候选（`cand-9648–cand-9684`）、77条提及和33条statement。相同题名或主题的既有作品不合并；作者身份、Queen/Doge和未名团体保持待后续身份对齐。

脚注1–4分别待规范注释L294–297，故p.316 coverage为partial。受控脚本`chp10_p316_migration.py`默认dry-run，核实Markdown SHA、PDF SHA、段SHA、表计数/ID、覆盖前态、逐条提及跨度、statement源句和外键；应用前四表恢复副本后缀`.bak-s2-chp10-p316-20261003`。应用后`python scripts/audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，`python -m pytest tests/test_audit_tables.py -q`通过，`git diff --check`退出码0（保留既有LF/CRLF提示）。全账本826段：453 complete、63 excluded、304 queued、6 partial；9,671候选、20,310提及、8,984 statements。p.315与p.316跨页句已双向闭合；p.315仍等L292–293，p.316等L294–297。下一源段为`chp-10:10_CHP-10_sec_ii:l119-131`。

## 第十章印刷页317正文（2026-10-03）

按`CHP-10.pdf`物理第50页阅读规范段`chp-10:10_CHP-10_sec_ii:l119-131`。印本将本节标作第十二章“THE ENLIGHTENMENT”，但来源文件仍为第十章第二节，未改S0来源归属。逐句登记威尼斯与欧洲的知识交流、启蒙思想、Arcadia、赞助变化及教皇试图阻止Galileo陵墓等书内说法；保留Haskell的推断语气、事件范围和非具名对象，不在S2裁决人物身份或正式关系。新增20个候选、57条提及和20条statement。印本校读记录装饰首字母V属于“VENICE”、`accepted. Trade`、`taken`、`fifteenth- and`等差异，不改OCR原文。L131的“Although much had been achieved before”续至p.318；脚注1–2待规范注释L298–299，因此coverage为partial。应用后826段：453 complete、63 excluded、303 queued、7 partial；9,691候选、20,367提及、9,004 statements。下一段`chp-10:10_CHP-10_sec_ii:l133-142`。

## 第十章印刷页318正文（2026-10-03）

按`CHP-10.pdf`物理第51页阅读规范段`chp-10:10_CHP-10_sec_ii:l133-142`。L134闭合p.317关于此前成就与1748年《亚琛和约》的句子；Voltaire的1766年评论作为Haskell转述，保留“约二十年”的近似语气。登记Muratori、Galiani、Genovesi、Beccaria及其著作/职位叙述，区分威尼斯共和国与威尼斯城市、Beccaria的未名反对者与具名思想家、Conti与Newton的本地文本指代；不将作者评价当作外部事实或正式关系。新增17个候选、67条提及和21条statement。按印本记录`puhblica`、`felicita`、`de’buoni`和`SirTsaac`的OCR校读，不改S0。

跨页句statement曾把p.317 L131与p.318 L134写成一个超出当前segment的行锚；表审计发现后修正为p.318段内L134引文，并以`continuation_from_segment_id`和`continuation_prefix`保存前页片段。原statement表留有`.bak-s2-chp10-p318-crosspagefix-20261003`恢复副本。p.318末句的Conti–Newton关系已由p.319 L145“of them”闭合；脚注1–4待规范注释L300–303，因此p.318 coverage仍为partial。`chp10_p318_migration.py`经dry-run后应用并保留四表恢复副本。应用后审计`s2_missing=[]`、`errors=[]`；定向测试通过10项。全账本826段：453 complete、63 excluded、302 queued、8 partial；9,708候选、20,434提及、9,025 statements。下一段为`chp-10:10_CHP-10_sec_ii:l144-149`。

## 第十章印刷页319正文（2026-10-03）

对照`CHP-10.pdf`物理第52页处理`chp-10:10_CHP-10_sec_ii:l144-149`。印本确认第319页，OCR页标`[Page 31]`仅作版面标记；L145的`Ke`校为印本`he`并记在S2，不改S0。印本确实作`Sasper`，故保留该拼写并映射到书内Shakespeare候选，不擅自正字。登记Newton提议Conti当选Royal Society、Conti的科学/文学活动、泄露Newton机密笔记后发生的决裂、公开信谴责、Conti对Newton的忠诚、第二次巴黎访问及Caylus友谊、返威尼斯与死年、影响Algarotti的著述、遗失的绘画论著、Newton光学与色彩、Canaletto的camera ottica评价，以及Conti关于绘画幻想的有限推论和引文。新增11个候选、38条提及、21条statement；“建议当选”不写成已当选，未名文献保留未识别，camera ottica不强塞现有类型。

本段首句补完p.318“对双方都满意”的关系句；更新p.318 statement的续接状态，并以当前段引文锚定本段新事实。脚注1–4待规范注释L304–307，L149引文末尾“Moreover,”续至p.320 L151，因此p.319 coverage为partial。受控脚本`chp10_p319_migration.py`锁定来源/PDF/段哈希、表前态、mention跨度、statement原文、前页关系statement及coverage状态；dry-run后应用并保存四表恢复副本`.bak-s2-chp10-p319-20261003`。应用后表审计`s2_missing=[]`、`errors=[]`；全账本826段：453 complete、63 excluded、301 queued、9 partial；9,719候选、20,472提及、9,046 statements。下一段`chp-10:10_CHP-10_sec_ii:l151-163`。

## 第十章印刷页320正文（2026-10-03）

对照`CHP-10.pdf`物理第53页处理规范段`chp-10:10_CHP-10_sec_ii:l151-163`。L152闭合p.319 Conti引文；记录Haskell对Tiepolo或Pittoni某modello的谨慎推断，以及其对Conti美学思想/画家影响的明确限制。随后登记老Zanetti关于彩色木刻工艺的信、Algarotti与Conti的通信和思想继承、Bettinelli著作及Haskell关于艺术家“genius”概念的论述。题名复用索引候选`cand-0370`，genius归项目类型`term`。L157–163记录Lodoli的修会身份、Smith未具名宫殿、教育旅行、学校与教学、Inquisitori di Stato争议、Vico《自传》、审查官职、关联人物群及宫外交往；将学校、作品、地点、人物及群体角色分开。新增10个候选、51条精确提及和32条statement。

页图校读记录OCR`Delientusiasmo`在印本为`Dell'entusiasmo`，并确认规范L310的脚注标签为3而非OCR 8；S0不改。p.320注1–3指向规范注释L308–310，待按源序处理。L163末尾“but”续至`chp-10:10_CHP-10_sec_ii:l165-173`，故p.320保持partial；p.319引文已闭合，但其coverage仍待注释L304–307收口。受控脚本`chp10_p320_migration.py`默认dry-run，核验来源及PDF/段哈希、表前态、提及锚点、statement引句/外键和前页引文续接。首次应用的审计发现候选`cand-9735`误用非注册类型`concept`；从预应用副本恢复四表后改为注册类型`term`，重跑预检并应用，保留`.bak-s2-chp10-p320-typefix-20261003`恢复副本，原预应用副本`.bak-s2-chp10-p320-20261003`亦保留。最终表审计`s2_missing=[]`、`errors=[]`，仅余两条既存enrichment `source_ref`警告、300段queued及10段partial；审计测试通过，`git diff --check`退出码0（仅LF/CRLF提示）。当前826段：453 complete、63 excluded、300 queued、10 partial；9,729候选、20,523提及、9,078 statements。下一段`chp-10:10_CHP-10_sec_ii:l165-173`。

## 第十章印刷页321正文（2026-10-03）

对照`CHP-10.pdf`物理第54页处理规范段`chp-10:10_CHP-10_sec_ii:l165-173`。L166续完并封闭p.320关于Lodoli不被完全当真的句子；记录“许可的小丑”比喻及其有关贵族奢侈和工匠生计的归属引语。L168区分Haskell经同时代人转述的建筑观与Lodoli失传原著，保存功能建筑、理性/舒适准则、他对晚期巴洛克和正在兴起的古典主义的态度，以及对古代建筑、Pantheon与经典艺术权威的不同评议。L169保留影响“微乎其微”的程度和“perhaps”限定、未名作者评论、未名评论群，以及其修会建筑干预。L170分别登记Pietà医院机构、未名总督、Massari模型、提出的教堂空间和模型批评；将“建筑师”的回答按相邻句局部指代到Massari，但标明是假设性自述，不推成实际未获委托。另记录Gozzi对装饰性建筑的批评及Algarotti对Lodoli意见的失真转述。新增16个候选、41条精确提及、27条statement。

页图校读只记入S2、不改S0：`linked.-`在印本为`linked.—`、`Nothing'shocked`为`Nothing shocked`、`outside'S.`为`outside S.`、`tnodello`为`modello`、`logicalgrounds`为`logical grounds`、`five in houses`为`live in houses`。p.320末尾“but”现由本页L166闭合；p.321脚注1–3待规范注释L311–313，L173末句续至下一规范段`chp-10:10_CHP-10_sec_ii:l175-178`（印本p.322 L176），故本段partial。受控脚本`chp10_p321_migration.py`默认dry-run，锁定来源及PDF/段哈希、表前态、候选ID、mention跨度、statement锚点/外键和前页续接。应用前四表恢复副本后缀`.bak-s2-chp10-p321-20261003`。最终`python scripts/audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，仅余两条既存enrichment `source_ref`警告、299段queued及11段partial；`python -m pytest tests/test_audit_tables.py -q`通过，`git diff --check`退出码0（仅LF/CRLF提示）。当前全账本826段：453 complete、63 excluded、299 queued、11 partial；9,745候选、20,564提及、9,105 statements。下一段`chp-10:10_CHP-10_sec_ii:l175-178`。

## 第十至十二章来源范围复核（2026-10-03）

逐页比较23份PDF的页面图像SHA-256，并用印刷页标和章节标题核对边界：`CHP-10.pdf`为跨章节合订扫描，物理页1–27覆盖第10章（印刷页276–298）；物理页28–49覆盖第11章（印刷页299–316）；物理页50–64覆盖第12章（印刷页317–331）。`CHP-11.pdf`物理页1–22与合订PDF物理页28–49逐页完全相同；`CHP-12.pdf`物理页1–15与合订PDF物理页50–64逐页完全相同。故第11、12章正文以`10_CHP-10_sec_ii.md`及`CHP-10.pdf`为主，既有`chp-10`源段ID保留，避免重编号和证据链断裂；独立PDF保留为同版校勘扫描。

99份Markdown资产分为74个规范来源文件、3个章节片段OCR对照文件（`11_CHP-11_intro.md`、`11_CHP-11_sec_ii.md`、`12_CHP-12_intro.md`）及22份整章/书后平行OCR副本。S0原登记的77个文件共826段；3个片段OCR文件合计44段，其中36段与主文本段哈希完全一致，5段去除页码标记后全文已由对应主文本段覆盖，另3段为OCR文件标题而非书本文字。应用前检查确认这44行均为queued，且没有mentions或statements外键。受控脚本`chp10_11_12_scope_exclusion.py`默认dry-run、`--apply`后仅将这44行设为`excluded/complete`并写明对应主段/理由；应用前备份为`04-knowledge/tables/s2-coverage.csv.bak-scope-overlap-20261003`。PDF、Markdown和S0段表均保留未删；S2现有107条排除中，44条为本次重复OCR/标题行，原有63条理由不变。

复核后范围口径为74个规范来源文件对应782个S2源段，加44个有映射的对照段，总计826段；35段派生视觉转录包含在规范来源范围中。覆盖状态为453 reviewed/complete、107 excluded、254 queued、12 reviewed/partial。对照排除未增加或删除实体候选、提及或statement。PDF逐页哈希、印刷页映射及逐段归并明细保留在受控脚本和本记录中。

## 第十章印刷页322正文（2026-10-03）

按`CHP-10.pdf`物理第55页对照规范段`chp-10:10_CHP-10_sec_ii:l175-184`。印本已进入第12章“THE ENLIGHTENMENT”，但S0主文件和段ID仍沿用合订来源的`chp-10`命名空间。L176续完p.321关于Lodoli对Algarotti兴趣的句子；把其仿古服饰批评、书信与十四行诗、作品画廊、Moscheni肖像委托和友谊、肖像题字/古典边饰、耶利米书引文、Lodoli拥护者、反对者及其门徒解释分别记录。保留Haskell的观察、被引文本和`perhaps`等推测，不把同题肖像、版画或群体强行合并为已确认身份/关系。

新增12个候选（`cand-9759`–`cand-9770`）、60条精确提及和39条原书statement。复用现有画家与被描绘者候选；把委托、友谊及其他关系陈述作为S2关系候选保留，正式端点与边留待后续阶段裁决。修正p.321句尾statement的源段指向，使续接锚定完整S0段`l175-184`；不更改此前语义。受控脚本`chp10_p322_migration.py`默认dry-run，核验Markdown、PDF及段哈希、表前态、提及跨度、statement原句/外键和coverage；应用前四表恢复副本后缀`.bak-s2-chp10-p322-20261003`。p.321脚注1–3及p.322脚注1–4分别仍待注释段L311–313、L314–317，故两个正文段保持partial。

本段应用后覆盖账本仍为826段：453 reviewed/complete、107 excluded、254 queued、12 reviewed/partial；候选9,757、提及20,624、原书statement 9,144。`s2-coverage.csv`中下一个queued段为`chp-10:10_CHP-10_sec_ii:l186-192`（印刷页323）。

## 第十章印刷页323正文（2026-10-03）

对照`CHP-10.pdf`物理第56页处理`chp-10:10_CHP-10_sec_ii:l186-192`。记录Goldoni对Pietro Longhi的1750/1757年赞誉、Goldoni的戏剧改革及Haskell关于Longhi可能影响Goldoni的推测；分别保存Longhi在先进圈子与贵族家庭中的接受差异、作品的非直接政治解释、Lodoli观念的间接影响，以及Gian Domenico Tiepolo的Via Crucis组画、Gasparo Gozzi对Longhi的评论和其与Tiepolo的比较。新增6个候选（`cand-9771`–`cand-9776`）、32条精确提及和20条statement；现存索引候选按印刷页范围复用。匿名的早期威尼斯历史学家、未名Goldoni对手、未名贵族家庭保持开放候选；S2仅保留书内断言和关系候选，不裁决正式关系。

页图校读只记入S2、不改S0：L188 OCR `httle`校为`little`；L189 `Venetian Use`校为`Venetian life`；L190 `criticism-because`校为`criticism because`；L191 `Efe he see`校为`life he sees`。这些校读影响引句含义，页图为依据。L188–189的处罚Longhi说法明确由Haskell转述为无支持证据；脚注5尾句位于当前段L192，并与规范注释L322互链，说明被引Paoletti将艺术家误作“Antonio” Longhi且Haskell认为来源不完全可靠。该人仍以未具名候选保存，待注释段完成后再处理姓名对应。页下注1–7对应规范注释段L318–324；其中L322 OCR将印本注5误标为6，扫描确认印本编号为5。整组注释暂未迁移，因此本段coverage标`reviewed/partial`，注释段仍queued。

受控脚本`chp10_p323_migration.py`默认dry-run，锁定Markdown/PDF/段哈希、表前态、提及跨度、statement引句与外键；首次应用将覆盖范围写成`186-192`，表审计据此报出statement和body-mention来源行超出coverage。按审计契约改为`L186-192`，经同一脚本`--repair-coverage-range` dry-run后应用，恢复副本为`s2-coverage.csv.bak-s2-chp10-p323-rangefix-20261003`；四表迁移恢复副本后缀为`.bak-s2-chp10-p323-20261003`。最终`python -X utf8 scripts/audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；`python -m pytest tests/test_audit_tables.py tests/test_build_source_segments.py -q`通过11项。两条既存enrichment `source_ref`警告保留，另有253段queued、13段partial的S2未完成提示。当前账本826段：453 reviewed/complete、107 excluded、253 queued、13 reviewed/partial；候选9,763、提及20,656、statement 9,164。下一段`chp-10:10_CHP-10_sec_ii:l194-201`（印刷页324）。

## 第十章印刷页324正文（2026-10-03）

对照`CHP-10.pdf`物理第57页处理`chp-10:10_CHP-10_sec_ii:l194-201`。新增候选`cand-9777`（类型`term`，Gasparo Gozzi寓言中未具名的劳动阶层）、16条精确提及和15条原书statement。逐句记录Pascoli较早提出的艺术观及其对Bamboccianti的讨论、Haskell关于等级社会中新旧画种比较的解释、Gozzi将Tiepolo与Longhi相较、其经Haskell转述的Longhi写生评论及Haskell由此作出的优劣推断。p.200–201转入Gozzi寓言：把墙上图像、乡村劳作图景、哲人/叙述者及对劳动阶层的礼赞限定在文学叙事中，不推作Gozzi真实住宅、收藏、交易或某位历史画家的事实；劳动阶层按与既有“the poor”候选相同的社会类别表达原则暂归`term`，但不补写群体身份。

页图校读仅记S2、不改S0：L194 OCR页标`[Page 24]`应为印刷页324；L196 `hambocciafiti`校为`Bamboccianti`；L199 `it is”still`校为`it is still`；L200 `foreshortened, figures`移除误逗号；L201 `country Use`校为`country life`。p.323索引交叉核查另确认比较语境中的无名“Tiepolo”应连Giambattista Tiepolo（`cand-2569`），与同页Via Crucis作者Gian Domenico Tiepolo（`cand-2626`）分开；据此修正p.323 L191的两条mention和相关比较statement对象引用，保留Via Crucis候选与断言不变。前态恢复副本为`mentions.csv.bak-s2-chp10-p323-tiepolo-identity-20261003`和`book-statements.jsonl.bak-s2-chp10-p323-tiepolo-identity-20261003`，修正后候选/提及/statement计数未改变，结构审计通过。

p.324独立正文批次最初标`reviewed/partial`：脚注1–4（L325–328）待迁移，末句“appearing through the”待p.325续完。受控脚本`chp10_p324_migration.py`默认dry-run，锁定Markdown/PDF/段SHA、表前态、候选状态、mention精确跨度、statement引句和候选外键；预览后应用，四表副本后缀为`.bak-s2-chp10-p324-20261003`。p.324后续收口见下节。

## 第十章印刷页325正文及p.324–325注释（2026-10-03）

对照`CHP-10.pdf`物理第58页处理`chp-10:10_CHP-10_sec_ii:l203-208`。p.325 L204补完p.324 L201的跨页句：Haskell说寓言中关于夸张透视的讥讽对象显而易见但没有在本段点名，并认为寓言图像似乎预示Millet，而非同时代威尼斯绘画。记录Gian Domenico Tiepolo与Giambattista的父子关系、前者在Villa Valmarana foresteria绘制乡村生活场景、作品被Haskell评价为写实/优美/富有同情却不符合哲人寓言中的劳动者表现方案；另记其社会思想影响、未具名私人别墅壁画与推测仅在朋友间传播的讽刺画稿。Maggiotto的科学兴趣、电气机器发明和《Considerazioni elettriche》著述，及Haskell对其genre painting在Longhi、Zompini、农民题材与Flemish嘲讽传统之间摇摆的评价，均保留说话者和判断性质。L207记录Gozzi 1782年参观Padua Arena chapel、致友人信中要求公共艺术表现贵族德行/爱国服务/文学赞助，并称Memmo同年在Padua实施类似方案；“must have been aware”仍是Haskell推断，Chapter 15回指尚未处理。L208转入Pisani：保留“先进人物”的归属与一两年时限、Barnabotti阶层、改革更利于本人及友人的Haskell评价、回归“古老法律”的方案；与Angelo Querini的比较在“increasingly”处未完，留待p.326续接。新增12个候选（`cand-9778`–`cand-9789`）、53条精确提及和29条statement。

同步迁移合并注释段`chp-10:10_CHP-10_sec_ii:l273-349`的L325–332：p.324注1–4为Pascoli卷I页31、Osservatore Veneto 1761年2月14日、Garganego致Goldoni的1770年题献及Levey 1959年页156、Gozzi《L’abitazione d’un filosofo creduto pazzo》卷IV页5；p.325注1–4为Tessier 1882年Maggiotto论文及《Considerazioni elettriche》手稿定位、Gozzi《Lettere familiari》卷I页239与可能日期1782、Chapter 15回指、Grimaldo关于Pisani的著作。以上均作为书内引证/转述记录，未声称独立读过被引来源。题献将Goldoni与Alessandro Longhi（Pietro之子）相较并提到旧交与互相赞许，另立断言，避免与p.324的Tiepolo/Longhi比较混同。补入p.324各正文statement与脚注statement ID的`footnote_refs`双向链接。

页图校读只记S2、不改S0：p.325 L204 `soresteria`→`foresteria`、`rural Use`→`rural life`；L208 `sacred laws of the pass`→`past`。p.324注3 OCR姓氏`Longbi`按页图校为`Longhi`；p.325注2 OCR `1808,1`据页图校为`1808, I`。受控迁移`chp10_p324_325_migration.py`默认dry-run，核验源文件、PDF和段SHA、前态、外键、引文锚点、提及及coverage；应用前四表恢复副本后缀`.bak-s2-chp10-p324-325-20261003`。首次表审计发现注释mentions的21个`start_char/end_char`相对L325–332局部切片，而契约要求相对完整L273–349段；按6828字符前缀修复并保存`mentions.csv.bak-s2-chp10-p324-325-note-offset-fix-20261003`。修复后全表审计`s2_missing=[]`、`errors=[]`；脚注statement ID回链无悬空引用。

本次处理后p.324转`reviewed/complete`；p.325因L208续到p.326 L211保持`reviewed/partial`。合并注释段已覆盖L325–332并保持partial，L274–324及L333以后仍待处理。全账本826段：454 reviewed/complete、107 excluded、250 queued、15 reviewed/partial；候选9,776、提及20,725、statement 9,208。两条既存enrichment `source_ref`警告保留。下一正文段为p.326 `chp-10:10_CHP-10_sec_ii:l210-222`。

## 第十章印刷页326–327正文及注释（2026-10-03）

对照`CHP-10.pdf`物理第59–60页，处理规范正文段`chp-10:10_CHP-10_sec_ii:l210-222`与`l224-239`，并将合并注释段覆盖扩至L325–337。新增40个候选（`cand-9790`–`cand-9829`）、79条精确提及和36条statement。p.326 L211闭合p.325关于Angelo Querini的比较；记录Pisani反对日益活跃的Inquisitori di Stato、支持政府并为其提供间谍的叙述、1780年竞选/任命、Gozzi的颂词及相关小册子和图像、名片符号与展示特殊绘画的习惯。名片图像不据此推定固定释义。另记Riviera委托Boscarati创作的四幅寓意画、版画及说明册、Pisani政治绘画在游行路线中的位置，并区分作者行为与Haskell对审查官宣传意图的解释。

p.327 L225–226闭合p.326关于新行政大楼外政治绘画的句子；记录Giampiccoli版画及其拉丁题铭后来撤除、宫中庆典、间谍报告所述绘画、法语菜单诗句及流传的意大利语说法；四日后Inquisitors采取行动，Pisani被捕，Boscarati受牵连，而后来的作者称dall’Acqua未被牵连。保留Haskell对这一时期的分期判断及其归属。正文L237位于p.327页脚分隔线上方，续句起始于“Among less offensive poems…”并在p.328 L241续接；分隔线下同一OCR行的注释续文属于p.326脚注3。两者分开锚定，p.327保持`reviewed/partial`。

本批注释包括p.326注1分见规范注释L333与本页页脚L218–222、注2对应L334、注3对应L335并续于p.327分隔线下L237–239；p.327注1–2对应L336–337，已与相应正文statement链接。页图校读仅记S2、不改S0：注1 `peril`校为印本`per il`；注释中的`PisaniIn`依跨页句法分开；注2 OCR `ID`校为`III`；p.327正文L228 `The combination'`校为`The combination of`、`selfadvertisement`校为`self-advertisement`，L233 `1’Ingresso`和`ii Processo`分别校为`l’Ingresso`、`il Processo`。以上所引书籍、手稿与报告仅按Haskell的引述记录，未独立查阅原件。

受控脚本`chp10_p326_327_migration.py`默认dry-run，核验Markdown/PDF及段哈希、注释切片哈希、表前态、mention偏移、statement引句/外键和脚注回链；应用前四表恢复副本后缀`.bak-s2-chp10-p326-327-20261003`。应用后p.325和p.326为`reviewed/complete`，p.327为`reviewed/partial`；合并注释段仍partial，已覆盖L325–337，L274–324及L338以后仍待处理。全账本826段：456 reviewed/complete、107 excluded、248 queued、15 reviewed/partial；候选9,816、提及20,804、statement 9,244。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；两条既存enrichment `source_ref`警告保留。`tests/test_audit_tables.py`与`tests/test_build_source_segments.py`共13项通过。下一正文段为p.328 `chp-10:10_CHP-10_sec_ii:l241-246`。

## 第十章印刷页328正文及注释（2026-10-03）

对照`CHP-10.pdf`物理第61页处理正文段`chp-10:10_CHP-10_sec_ii:l241-246`，并扩展合并注释段至L338–342。PDF印本为328页，S0 OCR页标`[Page 28]`；S0保持不变。p.328首句“election was one called…”接完p.327 L237主文“Among the less offensive poems … Pisani’s”，识别为《Il Filosofo dell'Alpi》，据此关闭`st-chp10-p327-less-offensive-poem-open`，并将候选cand-9829从未名诗作更新为题名对象。其与Pisani 1780年入城庆典的关系留作原书statement，未在S2定为正式图谱关系。

L242记录该颂诗关于阿尔卑斯与自然、Haskell所述Rousseau影响及其对Zuccarelli成功的部分作用判断；另记Zuccarelli获各类赞助人赞誉、A.M. Zanetti在1738年称其“non mai abbastanza lodato”、Consul Smith持续雇用，以及Haskell对英国人偏爱乡间生活/风景画的解释。L243–244记录Baretti的赞誉、他与Samuel Johnson的友谊、Giambattista Biffi与Beccaria/Verri的友谊、Biffi对Zuccarelli的高度评价及其未刊信中引文、Biffi日记对Rousseau之死的反应；也记录Haskell对Arcadia观念及自然主义绘画因果关系的限制，以及其称Zais更真实却被忽视的评价。关系措辞、批评与推论保持原书归属，供S3/S6后续裁决，不转写为无归属事实。

L245–246转向十八世纪中叶“绘画在现代生活中的重要性”问题及Gozzi在1760年称自己因报刊谈论建筑、祭坛和绘画过多而受到批评。L246末“After making the traditional reply that these represent”未完，留至p.329 L249续接；p.328 coverage为`reviewed/partial`。本段新增7个候选（cand-9830–cand-9836：Fossati、Zanetti–Gori书信、Biffi未刊信及日记来源、Arcadia艺术观念、Giacomo Storti、Accademia Francese），41条精确提及和22条statement；引用了既有候选但不做身份对齐。Biffi信件及Zanetti书信作为书内引证记录，未声称已查阅原件。

p.328注释1–7对应合并注释段L338–342并链接到相关statement：注1识别de la Harpe颂诗及Giuseppe Fossati的意大利语改写、威尼斯1780年印记；注2给出A.M. Zanetti致A.F. Gori信、1738-08-23及Biblioteca Marucelliana架号；注3引Baretti卷I页279；注4引Venturi 1957页37–76；注5引Biffi 1773年致Vacchelli未刊信并说明Venturi提供线索；注6引Venturi 1957页45；注7引Gazzetta Veneta 1760-07-26。相关手稿和被引出版物未独立查阅。页图校读只写入S2：正文`country house Use`读作`country house life`；注1的`II`、`del!`及`AccademiaFrancese`按印本读作`Il`、`dell'`和`Accademia Francese`；注2架号`p. 289c`读作`p. 289r`；注5`Govcrnativa`、`fame...preggio`分别读作`Governativa`、`farne...pregio`；注7`Cazzetta Veneta`读作`Gazzetta Veneta`。OCR原文未改。

受控脚本`chp10_p328_migration.py`默认dry-run，核验来源Markdown/PDF哈希、L241–246段哈希、表前态、mention偏移、statement引句/外键、跨页状态与脚注回链；dry-run显示+7候选、+41提及、+22 statement后应用，四表恢复副本后缀`.bak-s2-chp10-p328-20261003`。p.327转complete，p.328 partial，注释段覆盖L325–342并仍partial。全账本826段：457 complete、107 excluded、247 queued、15 partial；候选9,823、提及20,845、statement 9,266。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；原有两条enrichment `source_ref`警告保留；`tests/test_audit_tables.py`和`tests/test_build_source_segments.py`13项通过。下一正文段为p.329 `chp-10:10_CHP-10_sec_ii:l248-256`。

## 第十章印刷页329正文及注释（2026-10-03）

对照`CHP-10.pdf`物理第62页处理规范正文段`chp-10:10_CHP-10_sec_ii:l248-256`，并将合并注释段覆盖扩至L343–345。PDF印本页为329；p.328末句“After making the traditional reply that these represent”在p.329 L249闭合，因此p.328转为`reviewed/complete`。p.329 L256句尾“the position of the artist in society”续至p.330 L258，故p.329保持`reviewed/partial`。

L249记录Gozzi对绘画/艺术社会价值的试探性论述：艺术雇用劳动者、使资金流通并维持家庭生计；Haskell将其解释为对新政治经济学家批评的隐性回应。此后A. M. Zanetti the Younger提出绘画属于实用艺术，仍以神圣和英雄题材的教化作用为旧理论基础，再加入精神休憩功能。L250–252记录Haskell所述`diletto ed utile`旧论与后续功利主义辩护的区别：艺术学校吸引外国人，海外市场和外国君主邀请被用于论证绘画与贸易的联系；Zanetti的结论及Haskell对威尼斯经济效果的否定评价分别保留归属。L252–254记录1772年未具名官方委员会的报告复述自由艺术吸引外来者、提升国家声誉的说法。L255记录威尼斯国家1724年创办绘画与雕塑学院的计划、1756年建院、参议院的商业期待，以及学院以历史画为首、风景/景观画为次的题材等级；Haskell将其评价为回望旧体制而非预示新古典主义。L256仅登记社会地位讨论重新展开的未完引句，留待p.330闭合。

本段新增14个候选（`cand-9837`–`cand-9850`）、42条精确提及和22条statement；包含绘画理论、景观画类型、未具名1772委员会，以及脚注引出的Zanetti、Sagredo、Bassi、Fogolari文献。脚注1–3已链接：注1为`Della Pittura Veneziana`；注2为1772年`Relazione per le riforme`并由Agostino Sagredo转引；注3为Bassi 1941和Fogolari 1913。文献题名依据仓库内书目目录匹配，未独立查阅。地区、参议院、国家和学院均沿用既有候选；不做S3身份合并，也不据此新建正式关系。

页图校读只记于S2，不改S0 OCR：正文`value ofpaintings`读作`value of paintings`、`subjectmatter`读作`subject-matter`；脚注`risorme`读作`riforme`。受控脚本`chp10_p329_migration.py`默认dry-run，锁定Markdown/PDF/段落哈希、表前态、mention跨度、statement引句/外键、脚注回链及续句状态；dry-run后应用，四表恢复副本后缀`.bak-s2-chp10-p329-20261003`。注释覆盖L325–345并仍为partial，L274–324及L346以后仍待处理。当前全账本826段：458 complete、107 excluded、246 queued、15 partial；候选9,837、提及20,887、statement 9,288。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，保留两条既存enrichment `source_ref`警告及246段queued、15段partial提醒；定向测试`tests/test_audit_tables.py`与`tests/test_build_source_segments.py`共13项通过。下一正文段为p.330 `chp-10:10_CHP-10_sec_ii:l258-267`。

## 第十章印刷页330正文及注释（2026-10-03）

对照`CHP-10.pdf`物理第63页处理`chp-10:10_CHP-10_sec_ii:l258-267`，并将合并注释段`chp-10:10_CHP-10_sec_ii:l273-349`的覆盖扩至L346–349。p.330开头续完p.329关于艺术家社会地位的句子；Haskell将Andrea Memmo置于`Inquisitori alle Arti`的行会重组语境，并转述其准备报告时写下的问题。Memmo提出自由艺术从业者免受会费束缚、问及画家C.的税收豁免、参照其他城市和职业、回看Vasari及询问威尼斯学院的名称/标识/守护圣人；这些均保留为草拟问题，不写成已采纳政策。保留Memmo关于绘画想象力和艺术天才不应受束缚的引语，与Haskell称其在行政人员中罕见的评价相区分。Haskell将“C.”几乎肯定指向Canaletto，但同一注指出Canaletto于1768年去世、早于Memmo开始工作的时间；记录该年代张力，不在S2裁决身份。Algarotti的艺术能否自生赞助人论点仍按Haskell归属呈现。

p.330脚注4的S0文本跨两个既有段：总注及(i)位于注释段L349，Martyn的(ii)和`Nuova Gazzetta Veneta`的(iii)位于正文段L265–267。三处均链接到p.330关于威尼斯早期展览场所的statement。Nuova Gazzetta所称“Nassi [sic—Nazari?]”及Marco Foscarini肖像保持未决归属；Martyn、报纸、Nunzio报告和Haskell–Levey文章只按Haskell引证记录，未独立查阅。p.330脚注3记作Vasari《Montorsoli传》，本页印本“Life”校正OCR“Lise”。图版校读只记入S2、不改S0：`Inquisitor! alle Arti`→`Inquisitori alle Arti`、`refers’to`→`refers to`、`Lise`→`Life`、`ku`→`fu`、`piu`→`più`、`Francesco" Algarotti`→`Francesco Algarotti`。

受控脚本`chp10_p330_migration.py`默认dry-run，锁定Markdown/PDF及正文和注释切片哈希、表前态、mention跨度、statement引句/候选外键、脚注回链和续句状态。dry-run后应用，新增17个候选（`cand-9851`–`cand-9867`）、42条提及和15条statement；p.329转complete，p.330因句子续至p.331 L270而为partial。注释段现覆盖L325–349，仍因L274–324未迁移而partial。四表恢复副本后缀`.bak-s2-chp10-p330-20261003`。statement级复核发现L260脚注1正文回链缺项，已补齐；同时将Paris的statement候选映射改为城市候选`cand-4653`，不再误连到索引子条。两次修复各另存`book-statements.jsonl.bak-s2-chp10-p330-footnote1-linkfix-20261003`与`book-statements.jsonl.bak-s2-chp10-p330-candidate-linkfix-20261003`。最终`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；两条既存enrichment `source_ref`警告保留；全账本826段：459 complete、107 excluded、245 queued、15 partial；候选9,854、提及20,929、statement 9,303。`tests/test_audit_tables.py`和`tests/test_build_source_segments.py`通过13项，迁移脚本通过`py_compile`。下一正文段为p.331 `chp-10:10_CHP-10_sec_ii:l269-271`。

## 第十章印刷页331正文（2026-10-03）

对照`CHP-10.pdf`物理第64页处理规范段`chp-10:10_CHP-10_sec_ii:l269-271`。L270补完p.330关于Piazza S. Marco展览地点的句子：Church of S. Geminiano是相邻地标，原文并未说展示发生在教堂内部；画家有时在缺少其他方式时随意向公众展示作品。另登记Scuola di S. Rocco的定期展示及其与每年8月16日Doge和Senate游行的可能起源关系，保留`probably`限定；Algarotti致Mariette的转述及其与Paris Salon的类比；Haskell对组织复杂度、公众注意、存世批评材料和展示的公共讨论功能的评价。L271区分1777年开始的威尼斯学院官方展览安排与圣洛克年度展示，记录Piazzetta临时展台、展览成本、借画补数、投诉及至1787年停办；末句关于State介入艺术的判断保留为Haskell评价。未知参与者和借出作品不补造姓名或作品身份。

新增8个候选（`cand-9868`–`cand-9875`）、24条精确提及和12条statement。将正文Plate 56指针映射至既有作品候选`cand-4056`，并链接对应题注statement。复用已有候选`cand-8587`/`cand-8588`、`cand-8129`、`cand-8728`、`cand-0005`及人物/地点候选；圣洛克年度event与学院展览series分开。页图校读只记S2、不改S0：L270段末OCR多出的撇号不在印本。受控迁移`chp10_p331_migration.py`默认dry-run，校验Markdown/PDF/segment SHA、表前态、候选外键、精确mention跨度、statement引句及p.330续句状态；应用前保存四表恢复副本`.bak-s2-chp10-p331-20261003`。复核后将Church of S. Geminiano限定为相邻地标，并把Academy展览命名改为“1777年开始、至1787年停办”，不推定确切末次展览年份；恢复副本后缀`.bak-s2-chp10-p331-reviewfix-20261003`。p.330与p.331现为complete；合并注释仍因L274–324未迁移而partial，p.311–323的13个正文段也仍partial。应用后账本826段：461 complete、107 excluded、244 queued、14 partial；9,862候选、20,953提及、9,315 statements。结构审计`s2_missing=[]`、`errors=[]`，保留两条既存enrichment `source_ref`警告；全书S2仍未达S3交接条件。下一步先完成合并注释L274–324，再按源序进入第13章。

## 第十章印刷页311–312注释及脚注映射更正（2026-10-03）

对照`CHP-10.pdf`物理第40–41页处理p.311注释L274–278及p.312注释L279–283。另核对p.312印本脚注扩展文本在规范OCR正文L27–32、其简短规范引文在L280的双位置；将L27–32作为脚注2内容迁入并交叉指向L280，不改写S0。

p.311注1–6逐项录入并回链到出生、威尼斯褒奖与养老金、葬礼、普鲁士王储的请求、Schulenburg谈论女性、询问患病贵族六条正文statement。注3保留Haskell列出的威尼斯/维罗纳居留年份，不称作独立核验；注5将De Brosses原话明确标作经Haskell转引；注6登记Rockingham致Essex信及Haskell所给British Museum Add. MSS.定位。印本校读记录Romanin卷号为VIII（OCR作VID）及书名中的德文拼写；未查阅所引书信、手稿和书刊。

p.312印本只有注1–5。注2含Keysler关于Corfu图像及木模型的引文、Schulenburg出版目录中Canaletto画作的转录、其他Corfu模型/图像的说明和Morassi肖像页码；出版目录标题由p.313注3互证，两处暂复用同一候选；所有被引来源均未独立查阅。注4记录1724–1737年Schulenburg收藏手稿目录及Edward Wright引文；注5记录Morassi 1960页码。页图确认注5标记位于Guardi工作至1745年句末；既有S2错误地把注5、6标到前两处陈述，现移除这两个错误标记、恢复Guardi statement的印本注5，并记录OCR的注号8→5、年份i960→1960、馆藏号It. VU→VII校读。正文条目、水肿肖像句和艺术家名单不再带错误脚注。

受控脚本`chp10_p311_312_notes_migration.py`默认dry-run，锁定规范Markdown/PDF哈希、表前态和段状态，校验候选外键、mention精确跨度、statement原句、脚注回链及既有跨页续接；dry-run后应用，四表恢复副本后缀`.bak-s2-chp10-p311-312-notes-20261003`。新增15个候选、25条精确提及和11条statement；p.311、p.312正文段转为complete，合并注释覆盖更新为L274–283及既有L325–349，L284–324仍待处理。修订后全账本826段：463 complete、107 excluded、244 queued、12 partial；9,877候选、20,978提及、9,326 statement。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，仍报告12个partial和244个queued；p.312脚注/回链专项核验的25条新增mentions跨度均精确，14个正文statement链接到相应注释statement。`tests/test_audit_tables.py`与`tests/test_build_source_segments.py`共12项通过。此前记录所称“p.312印本脚注1–6”及“注5/6位于艺术家列表/水肿肖像句”由本条按印本更正。下一段按源序为p.313注释L284–287。

## 第十章印刷页313–314注释、对象重映射与回链（2026-10-03）

对照CHP-10.pdf物理页46–47核对规范注释L284–291。p.313注1记录Haskell经Pignatti引用的一幅Schulenburg肖像及其Guardi归属、Museo Correr位置；注2分别记录作品系列在展览/拍卖中出现的转述，以及Haskell所引Watson将系列归给Gian Antonio而非Francesco Guardi的判断；注3连接Schulenburg出版目录及Morassi 1952页码；注4只保留“See Chapter 10”的印刷交叉引用，未映射到项目文件章节。p.314注1登记Piazzetta、Pittoni、Angelo Trevisani向Schulenburg推荐画作且档案记载于Hanover的陈述；注2记录White与Sewter 1959页码；注3连接出版目录并登记Levey所引的英国后续出售；注4将Marieschi、Carlevarijs、Cimaroli、Joli、Zuccarelli、Marco Ricci的画作数量分为六条statement（10、6、4、2、9、6）。

人物候选只按印本文字及既有候选复用；Angelo Trevisani与已有Angiolo Trevisani不合并，交S3判断。Pignatti、Watson、White、Sewter、Morassi、Levey所引文献及Hanover档案均未独立查阅；来源声称、归属和销售仍标作书内陈述，不作外部验证。校读记录p.313的OCR i960→1960、Feldtnarechal→Feldmarechal；原始S0转录未改。更新既有目录候选cand-9884为印本题名拼写。

复核p.313正文mention后发现存世肖像和“little Turkish scenes”原先误连到重复的Guardi人物候选。新增作品组候选并将三个精确mention及两条statement改连作品组；具体肖像另建work候选，与Plate 53a保持区分。Watson attribution写作关系候选，仍须S3/S6裁决；不把脚注转成正式关系。

受控脚本chp10_p313_314_notes_migration.py默认dry-run，锁定来源/PDF哈希及四表前态；校验提及跨度、statement引句、外键、脚注回链和覆盖行。应用后四表恢复副本后缀.bak-s2-chp10-p313-314-notes-20261003。首次全表审计发现两条六幅画计数statement的claim文字相同；受控修复脚本chp10_p313_314_unique_count_claim_repair.py为六条claim补入对应画家姓名，恢复副本为book-statements.jsonl.bak-s2-chp10-p313-314-unique-count-claims-20261003。最终全表审计为s2_missing=[]、errors=[]；完成段从463增至465，partial由12减至10，244段仍queued。表中共9,891候选、21,011 mentions、9,344 statements；定向pytest 12项通过，两个迁移/修复脚本py_compile通过。下一项为p.315注释L292–293。

## 第十章印刷页315注释（2026-10-03）

对照CHP-10.pdf物理页48核读p.315注释L292–293。注1记载Schulenburg于1743年7月28日致Rosalba Carriera，提请她协助一位名为Angelica Griè的年轻女画家，并给出Biblioteca Laurenziana的MSS. Cod. Ashburn. 1781, Vol. IV, p.266定位；印本人名视觉读作Griè，S0 OCR保留GriS。保留推荐对象身份未定及意大利语di lei amorosa assistenza的原句范围，不推断后续协助结果；以两条关系候选分别登记书信往来和推荐事项。注2分别记Haskell引Rohrlach 1951年页198–200讨论Streit生平、画作及后续归属，以及引Denina页196说明Streit在威尼斯的位置。手稿、所引书刊和档案目录均未独立查阅；Rohrlach、Denina和Angelica的身份留待后续对齐。

受控脚本chp10_p315_notes_migration.py默认dry-run，锁定Markdown/PDF哈希、表前态和覆盖状态，核验提及切片、外键、两处脚注标记及p.315 L106→p.316 L109续句闭合。应用后恢复副本后缀.bak-s2-chp10-p315-notes-20261003。新增6个候选（cand-9905–cand-9910）、11条精确mention和4条statement；p.315正文转complete。合并注释覆盖扩至L274–293及既有L325–349，剩余L294–324；p.316–323的8个正文段仍partial。全账本826段：466 complete、107 excluded、244 queued、9 partial；9,897候选、21,022提及、9,348 statements。全表审计s2_missing=[]、errors=[]；两条既存enrichment source_ref警告、244 queued和9 partial提示保留。定向pytest 12项通过。下一待处理注释为p.316 L294–297。
## 第十章印刷页316注释（2026-10-03）

对照`CHP-10.pdf`物理第49页核读规范合并注释段L294–297。注1记录Haskell称Streit关于Canaletto画作的笔记由Zimmermann刊布，并引W. G. Constable 1956年页81–93讨论这些画作、否定Moretti或其他追随者归属；注2记录Zimmermann页199–203将《Sala del Maggior Consiglio》归给Gianantonio与Francesco Guardi；注3记录Haskell所说Amigoni在1739–1746年间居威尼斯、处于英国之行之后和西班牙之行之前，并称Streit肖像由Zimmermann刊布、于1739年在Streit 52岁时绘成；注4记录Hugh Honour让Haskell查看若干画作照片。

根据印本视觉核读将L295 OCR题名`Sala del Maxtor Consiglio`校读为`Sala del Maggior Consiglio`，不改写S0转录。新增候选`cand-9911`–`cand-9918`，24条精确mention和7条statement。W. G. Constable与索引人物John Constable分开；Zimmermann、Moretti及Hugh Honour均不做外部身份合并。Zimmermann和Constable所引页、肖像及照片均未独立查阅；“these paintings”的指代、特定作品现藏地与各项归属保持未决。四个注释均已回链到对应正文statement。

受控脚本`chp10_p316_notes_migration.py`锁定规范Markdown/PDF哈希、表前态、注释边界、mention跨度、statement外键和四处正文脚注标记；dry-run后写入，并为四张表保存`.bak-s2-chp10-p316-notes-20261003`恢复副本。p.316正文coverage由partial转complete，合并注释coverage扩至L274–297及既有L325–349，L298–324仍待处理。全表审计为`s2_missing=[]`、`errors=[]`；全账本826段：467 complete、107 excluded、244 queued、8 partial；候选9,905、提及21,046、statement 9,355。两条既存enrichment `source_ref`警告保留；`tests/test_audit_tables.py`与`tests/test_build_source_segments.py`共13项通过。下一待处理注释为L298（p.317）；p.317–323正文已有语义登记，仍待各页注释回链后关闭。
## 第十章印刷页317注释（2026-10-03）

对照`CHP-10.pdf`物理第50页核读p.317注释L298–299。注1为“Hazard, 1935”，回链至Haskell关于17世纪末英法知识革命的statement；注2仅为“Maugain”，回链至Galileo《Dialogo》不得早于1744年出版的statement。两处均按印本文字登记为最小书目定位；没有题名、完整作者名或页码，未从外部猜补。新增候选`cand-9919`–`cand-9922`、2条精确mention和2条citation statement。

受控脚本`chp10_p317_notes_migration.py`核验来源/PDF哈希、表前态、两处注释边界、正文脚注标记及外键；dry-run后应用，四表恢复副本后缀`.bak-s2-chp10-p317-notes-20261003`。p.317 coverage转complete，合并注释覆盖扩至L274–299及既有L325–349，L300–324仍待处理。全表审计`s2_missing=[]`、`errors=[]`；全账本826段：468 complete、107 excluded、244 queued、7 partial；候选9,909、提及21,048、statement 9,357。既存两条enrichment `source_ref`警告保留；定向测试13项通过。下一待处理注释为L300（p.318）。
## 第十章印刷页318注释（2026-10-03）

对照`CHP-10.pdf`物理第51页核读p.318注释L300–303。注1把Haskell关于Voltaire在1766年评论意大利知识复兴的正文回指到Natali第5页所引书信；注2分别以Pierantoni定位Giannone在威尼斯的居留/驱逐，以Brol定位Pilati；注3列J. G. Robertson与Moncallero的“I”，保留罗马数字含义未定；注4列Robertson第四章及《Prose e Poesie》第二卷（1756）。正文“his Prose e Poesie”暂按前句Conti作语法先行项，列作待书目核对，不视为已独立确认作者。新增候选`cand-9923`–`cand-9934`、14条mention和6条citation statement。上述被引页/作品未独立查阅，作者身份和出版详情均未外推。

受控脚本`chp10_p318_notes_migration.py`锁定来源/PDF哈希、表前态、四条注释边界、提及跨度、statement外键和正文脚注标记；dry-run后应用，四表恢复副本后缀`.bak-s2-chp10-p318-notes-20261003`。p.318 coverage转complete，合并注释覆盖扩至L274–303及既有L325–349，L304–324仍待处理。全表审计`s2_missing=[]`、`errors=[]`；全账本826段：469 complete、107 excluded、244 queued、6 partial；候选9,921、提及21,062、statement 9,363。既存两条enrichment `source_ref`警告保留；两项定向测试共13项通过。下一待处理注释为L304（p.319）。

## 第十章印刷页319注释（2026-10-03）

对照`CHP-10.pdf`物理页52核读规范注释L304–307。注1仅给Manuel姓氏和页86、94，分别登记作者候选与最小书目定位，不猜全名或著作。注2引用Conti卷II第cxlviii页：记录Leonardo关于绘画色彩和谐的手稿（不与《绘画论》混同）、未具名米兰图书馆、Newtonian色彩理论和机械重心法、未具名德国画家印制图画并在伦敦展示、Antonio Zanetti在威尼斯保存一例、Conti在The Hague见画家、画家自述使用Newton光学原则，以及对人体阴影色彩和谐的条件性推测。各层均标作Conti经Haskell转引；“he assured me”保留为间接报告，“Se ciò è vero”和“forse”保留条件和推测，不作事实核验或身份推断。注3记录Conti卷II第250页对camera ottica构图、Canaletto转移透视点及视觉效果的描述；注4以卷II第278页定位正文绘画幻想引文。

新增`cand-9935`–`cand-9946`共12个候选、26条提及、9条statement；p.319正文四个脚注marker均已连接具体注释statement。印本校读S2记录L305 `bell’ani`→`bell’arti`、`ne , conserva`→`ne conserva`，L306 `tutti fi trasferisca`→`tutti li trasferisca`，没有改写S0。受控脚本`chp10_p319_notes_migration.py`锁定规范来源/PDF哈希、表前态、边界、候选ID、提及锚点和外键，dry-run确认后应用；四表恢复副本后缀`.bak-s2-chp10-p319-notes-20261003`。应用后coverage为470 complete、107 excluded、244 queued、5 partial；9,933候选、21,088提及、9,372 statements。表审计`s2_missing=[]`、`errors=[]`，定向测试13项通过。下一范围为L308–324并收口p.320–323正文partial。

### p.320–323注释迁移前印本预核（2026-10-03）

仅作L308–324下一批迁移的页图定位预核，对照`CHP-10.pdf`物理页53–56，尚未改变coverage。页图确认p.320注释印本编号1–3；规范OCR L310的`8`实际是印本注3。p.321注释1–3与规范L311–313对应；p.322注释1–4与L314–317对应，其中L314是接在p.321正文句尾后的注释。p.323印本注释为1–7：规范L322 OCR标号`6`在印本为注5，L323为注6，L324为注7。初始低分辨率预核只辨到“and Paoletti.”；随后对物理页56脚注区做高分辨率核读，确认同页续句为“who calls the artist ‘Antonio’ Longhi, does not seem wholly reliable.”，对应规范S0 L192。p.323正文/注释marker尚需逐条核定与statement的链接；四个正文段和合并注释段在完成实际迁移前继续保持partial。

## 第十章印刷页320–323注释及尾段收口（2026-10-03）

按源序核读并迁移规范合并注释段L308–324，对照`CHP-10.pdf`物理页53–56。新增`cand-9947`–`cand-9976`共30个候选、57条提及和19条statement。p.320注1为Lorenzetti 1917页49注1，注2以Memmo《Elementi dell’architettura lodoliana》（Rome, 1786）作为Haskell所称Lodoli生平唯一来源，并另引Petrocchi 1947，注3将Vico《Autobiography》出版定位至Calogerà《Raccolta》卷I（1728）并附Fisch/Bergin页183–184。注2补出此前p.309候选`cand-8812`的完整书名，因此更新候选标题和描述，关联依据限于书内作者、主题、年代及页码，没有外部核验。

p.321注1列Ortes致Algarotti 1749年9月26日书信（Algarotti XIV, p.315）及Temanza p.87；注2引G. A. Moschini 1815卷I页48，注3引Gozzi《Dialogo tra un librajo e un Forestiere》卷I页26。p.322注1引Kauffmann 1944/1955，注2给Biblioteca Correr手稿定位Misc. XI/1348 (1140)，注3仅记Previtali，注4称Longhi绘制的Lodoli肖像在Venice的Accademia，并以[Memmo]《Riflessioni》(1788)指向肖像史。注4地点与List of Plates的Plate 48c“Alessandro Longhi: Carlo Lodoli (Museo Correr, Venice)”冲突；S2把两项证据及原有source-specific portrait候选并列保留，未解决机构或对象身份。

p.323注1–2分别定位Goldoni赞美Longhi的两处文字；注3为Dazzi；注4为Giuseppe Gennari致Gaspare Patriarchi的1761年11月5日书信及Melchiori页142；注5为Paoletti 1832页122。印本的注5由L322与同页脚注延续L192组成，记录“无Inquisitors档案证据”及Paoletti把画家称作“Antonio”Longhi、Haskell认为来源不完全可靠。body段原有注尾statement现链接至注段citation statement；未知历史学家没有与Paoletti身份合并。注6复用Pietro Visconti致Gian Pietro Ligari的1749年12月19日书信候选（Arslan 1952, p.63）；注7对应Gazzetta Veneta 1760年8月13日第55期。

印本校读仅记S2，不改S0：L310脚注号OCR 8校为印本3；L312 `G. AMoschini, 1815,1`校读`G. A. Moschini, 1815, I`；L315 shelf locator `Cotter`校为`Correr`；L317 `Tlie`/`Longbi`校为`The`/`Longhi`；L322 OCR注号6校为印本5；L323 `horn`校为`from`；L324 issue `No. 35`校为印本`No. 55`。p.323物理页56的高分辨率裁图确认L192确为注5续文，非缺失内容。脚本`chp10_p320_323_notes_migration.py`锁定规范来源/PDF哈希、候选和表前态、注释边界、提及跨度、外键、已有脚注状态；默认dry-run预览为+30候选、+57提及、+19 statement后应用，四表恢复副本后缀`.bak-s2-chp10-p320-323-notes-20261003`。四个正文partial和合并注释partial均转complete。审计`s2_missing=[]`、`errors=[]`；定向测试13项通过。全账本826段：475 complete、107 excluded、244 queued、0 partial；下一queued源段`chp-13:13_CHP-13_intro:l1-1`。

## 第十三章印刷页332正文（2026-10-03）

按源序处理`chp-13:13_CHP-13_intro:l1-1`与`l3-12`。L1仅为生成的Markdown文件名标题，不是印刷内容，coverage记为`excluded/complete`并写明理由；印刷章名及正文位于下一S0段。L3–12对应CHP-13.pdf物理页1的章名、p.332开篇正文及脚注标记，页图与全文OCR对读后，coverage记为`reviewed/partial`。`[Page 2]`为该节的OCR页标，不当成印刷页号；p.333从同PDF下一页开始。

语义上记录Haskell对威尼斯出版商与欧洲联系、艺术赞助及国际趣味的概述；书籍出版对城市经济的长期作用；共和国末一百年间维持出版优势的努力。该句为被动表达，未指明努力者，statement修订为无实体端点，不把行动归给政府。对审查制度保留“避免批评贵族政体时较宽松”的条件限定；Grosley的法语观察保留为Haskell转引，未独立查阅，不扩写成经核实的法律事实；原书称宽松环境帮助形成威尼斯书籍的国际市场。书店作为文化联系中心是Haskell对未具名旅客记述的概括。

后半记录政府以版权法鼓励面向出口的华丽插图书、法定二十年垄断及原书所述的本地市场质量和出口豪华版本差异。未见法律名称、制定时间或精确范围；为机制登记描述性procedure候选`cand-9978`。旅客难以取得城市原景或聘请临摹者与版画需求的因果关系按Haskell的概述记录，不为匿名旅客或市场关系臆造端点。出版物例证包含Carlevarijs《Le Fabriche e Vedute di Venetia》（1703，候选`cand-0555`）、Lovisa于1720年出版、含建筑绘图和多位画家图片的《Il Gran Teatro delle Pitture e Prospettive di Venezia》（候选`cand-1453`），其中包括“young Tiepolo”。两本图书及Marieschi 1741年未题名views均记录为面向旅客；Marieschi组作来源派生候选`cand-9977`不指认单幅作品，Fragonard的稍后造访没有补造年份。结尾记录Haskell关于插图市场、尺寸和技术改变作品面貌的概括。

印本校读只记S2，不改S0：L6 OCR `HERE was`与L7 `Tcontacts`按跨两行首字母大写T校读为`THERE was` / `contacts`；L11 `Venice,’`校为`Venice;`；L12校正`’forties,are`空格、`Carlevarijs’Le`空格、`II Gran`为印本`Il Gran`，以及`the’limitations`的误撇号。注释标记1–5对应本文件末端合并注释段`chp-13:13_CHP-13_intro:l179-251`，现阶段只登记待链接状态，不能据正文段宣称脚注完整。

受控脚本`chp13_p332_migration.py`默认dry-run，锁定源文件/PDF哈希、覆盖前态、候选编号、提及位置和statement原句；应用后新增2个候选、35条精确提及和20条statement，四表恢复副本后缀`.bak-s2-chp13-p332-20261003`。逐项复核后另修正两个statement：共和国末期出版努力与版画需求都不从上下文臆定行动者/关系端点；修复副本后缀`.bak-s2-chp13-p332-endpoint-review-20261003`。全表审计`errors=[]`、`s2_missing=[]`，保留两条既存enrichment `source_ref`警告及242段queued、1段partial提示。下一源序段为p.333 `chp-13:13_CHP-13_intro:l14-19`。


## 第十三章印刷页333正文（2026-10-03）

按源序核读`chp-13:13_CHP-13_intro:l14-19`，对照`CHP-13.pdf`物理页2。记录Haskell归纳的四类图书图像生产路径：复制既有威尼斯杰作、绘制主要供版画复制的当代绘画、为书籍插图创作图稿、艺术家自行制版。另记录出版商拥有店铺/部分拥有印刷设施、销售版画与插图书、雇用版画工、委托艺术家，以及出版商自身赞助与昂贵项目依赖未具名外部资助的区别；没有将该一般说明变成Tiepolo或Piazzetta在本页的具体委托。此页开始Haskell所分的两类插图书之一：贵族仪式相关的诗歌、颂辞集；记下可有简短装饰题页或较完整插图、由出版商依委托规格制作，以及诗人/艺术家的不同负担与支持作用。

Caterina Barbarigo 1765年的引文记作Haskell转引的印制指示，并保留经代理人传达的层级：纸张与字体、题页样式、局部装饰、家族纹章与Zorzi纹章交织、24页及500册。未把“家族纹章”擅定为Barbarigo家徽，Zorzi只登记家族候选且支系不明；该例不推广为普遍惯例。Haskell正文写作`Gaspara Gozzi`，S1索引候选`cand-1220`另写`Gozzi, Gasparo`且页码也指向333；新建独立候选`cand-9979`，保留拼写/身份冲突待S3判断，不合并。行19以“Bundles of them”开始的另一段引语未署名并续至p.334；不因相邻于Gozzi而归给她，记录为未决说话者及待闭合跨页引文。Barbarigo说明后的脚注标记1待L179–251核对。

本段新增候选`cand-9979`–`cand-9985`（Gaspara Gozzi、Zorzi家族、四种生产路径和仪式诗歌出版类别），23条精确提及、17条statement；一般事实、引用层级及关系候选属性按原书限定。覆盖记为`reviewed/partial`，仅因匿名引文跨至下一S0段且脚注1尚未处理。受控迁移脚本`chp13_p333_migration.py`默认dry-run，核对来源与PDF哈希、表前态、候选编号、提及跨度、statement引句/外键及跨页/脚注状态；dry-run显示+7候选、+23提及、+17 statement后应用，四表恢复副本后缀`.bak-s2-chp13-p333-20261003`。表审计`s2_missing=[]`、`errors=[]`；保留两条既存enrichment `source_ref`警告，以及241段queued、2段partial提示。下一源序段为p.334 `chp-13:13_CHP-13_intro:l21-30`，先闭合引文并处理同页其余正文。


## 第十三章印刷页334正文（2026-10-03）

按源序核读`chp-13:13_CHP-13_intro:l21-30`，对照`CHP-13.pdf`物理页3。p.333行19开始的“Bundles of them”引文在此页L22闭合；本页印本注1为“Bettinelli: Lettere inglesi—lettera seconda”，据此更新前段statement的引文来源和说话者为Saverio Bettinelli，并记下续文、页内注位置及待处理的书末注释链接。不能把Bettinelli的修辞性评价改作出版物的普遍事实。p.333关于两类插图书的statement同步补入第二类：现代、尤其古代作者的精装/精美版本。

p.334继续记录无名贵族自述为一套纪念诗集花费千达克特，以及Bettinelli对印制极奢华的书籍之直接引语。随后记三位在经营与赞助品质方面突出的出版商Giambattista Albrizzi、Giambattista Pasquali、Antonio Zatta；不把Haskell的比较写成穷尽名单。Albrizzi部分记录收藏当代绘画、出版精制书籍、1699年出生并继承父业、游历德国和奥地利及送子赴维也纳、1737年首次刊行《Il Forestiere Illuminato》并献辞萨克森选帝侯、兄弟Almorò组织Accademia Albrizziana、Albrizzi编辑《Novelle della Repubblica delle Lettere》、与神职人员和Pisani等贵族的联系、加入Scuola di S. Rocco并晚年任Guardiano。Haskell明确以广告与献辞推断Albrizzi的天主教身份及社交联系，故保留为作者推断；Pisani家族支系和受教育的儿子不擅自具名，选帝侯不凭头衔识别个人。

另记Albrizzi自1736年起刊印Bossuet作品的完整法文版、各卷献给奥地利王室成员、以原文法语争取国际读者，以及该版首次聘Piazzetta作插图者。新登记描述性文献候选`cand-9987`（具体书名与卷数未给）、期刊候选`cand-9988`、Pisani家族开放候选`cand-9989`和第二类出版物概念`cand-9986`；另新增26条精确提及与18条statement，现成索引候选复用而不在S2合并同名索引行。p.334页脚可见注1–6，分别涉及Bettinelli、Albrizzi父业、维也纳教育、Accademia、期刊创刊时间及Bossuet/异端观点来源；其合并注释段L179–251尚未按源序读完，正文注记均待正式回链。

印本校读仅登记S2，不改S0：L22 `cornplains`→`complains`；L26 `welT`→`well`、`II Forestiere Illuminate`→`Il Forestiere Illuminato`、`Almord`→`Almorò`；L27 `famflies`→`families`。L28 `Scuola di S. Rocco`与印本相符，不作改动。p.334最后关于Albrizzi复兴威尼斯版画声誉的引文在L30中断，续至p.335 S0 L32起；故coverage为`reviewed/partial`。受控脚本`chp13_p334_migration.py`默认dry-run并核验来源/PDF哈希、表前态、行前缀、候选ID、mention跨度、statement锚点/外键及跨页状态；应用后四表恢复副本后缀`.bak-s2-chp13-p334-20261003`。同时更新p.333跨页引文和两类图书statement。全表审计`s2_missing=[]`、`errors=[]`；两条既存enrichment `source_ref`警告保留，另有240段queued和3段partial。定向测试`test_audit_tables.py`与`test_build_source_segments.py`共13项通过。下一源序段为p.335 `chp-13:13_CHP-13_intro:l32-39`，先关闭Albrizzi计划引文。
## 第十三章印刷页335正文与续注处理（2026-10-03）

按源序核读`chp-13:13_CHP-13_intro:l32-39`并对照`CHP-13.pdf`物理页4。p.334 L30的引文在本页L33闭合；印本注1将其来源指向《Novelle》1730年3月19日广告，说明广告拟议刊行圣奥古斯丁作品，不表示该版本后来实际出版。更新p.334 statement的说话者、续文和限定语，标记引文已闭合，但完整书末注释仍待L192。

本页记录Albrizzi与Piazzetta后来形成的友谊及业务伙伴关系；Piazzetta早于两人首次合作十二年，为Recurti出版的无名宗教书绘制扉页，并将其“几乎完整”的插图业务垄断及合作范围限定在书籍插图。随后记录Piazzetta为Albrizzi的Bossuet版绘制幻想性插图、插图母题和其对中欧大主教/富裕修道院读者的作用，以及Haskell对插图风格、Bossuet版影响后续出版物和Albrizzi版物整体美学的评价。Bossuet版的标题与册数未在本页给出，不补造。

继续记录Albrizzi于1745年出版的《Gerusalemme Liberata》插图版、献予Maria Teresa、跨欧洲订户及列名的Schulenburg、Smith、Rosalba Carriera和仅以姓氏出现的Pellegrini；后者仅映射至索引候选，身份留S3。Piazzetta约绘70幅图稿、戏剧性与牧歌式构图的差异和Boucher比较均保留为Haskell评价，不写成影响关系。该书在法国成功、获Abbé Richard赞赏的说法按Haskell转述记录；本页注4注明Richard卷II第492页经Morazzoni第125页转引，未把被引著作标成已独立查阅。L37末尾“and it inspired”对象与结果缺失，保持开放至p.336 L41–50。

新增候选`cand-9990`–`cand-9996`：1745年插图版、约70幅图稿组、Schönbrunn宫、Recurti出版的无名宗教书、Chinoiserie、早期Arcadian Rococo绘画表述，以及Richard/Morazzoni页码定位；新增37条精确提及和21条statement。明显的多重主张拆为独立statement，例如“宗教书的出版者”与“扉页绘制者”、法国市场成功与Richard的赞赏；所有关系仍只是S2候选。未将Albrizzi家族墓穴臆造为地点，未将Schönbrunn装饰范围或绘图来源扩展至脚注之外。

页图校读仅记S2、不改S0：L36 `Schonbrunn`→`Schönbrunn`；L37 `Rosalba Camera`→`Rosalba Carriera`、`drawings?`→`drawings³`、`a" success`→`a success`；L39 `Richard, H`→`Richard, II`。受控脚本`chp13_p335_migration.py`默认dry-run，锁定源文件/PDF哈希、表前态、候选编号、提及跨度、statement引句/外键、p.334开放引文和覆盖状态；初次核查纠正了把L33内容误锚至L34的问题，并按实际换行校正`Central Europe`与订户名单的跨行引句。dry-run通过后应用，四表恢复副本后缀`.bak-s2-chp13-p335-20261003`。当前全账本826段：475 complete、108 excluded、239 queued、4 partial；9,983候选、21,266提及、9,467 statements。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；两条既存enrichment `source_ref`警告未变。`tests/test_audit_tables.py`与`tests/test_build_source_segments.py`共13项通过。p.335保持partial（脚注1–3待L192–194且句子待p.336续完）；下一源序段为`chp-13:13_CHP-13_intro:l41-50`。

## 第十三章印刷页336正文（2026-10-03）

按源序核读`chp-13:13_CHP-13_intro:l41-50`，对照`CHP-13.pdf`物理页5。p.335 L37的“and it inspired”在p.336 L41–42闭合：Francesco Gerbault寄来同样豪华的《Orlando Furioso》订阅邀请，但项目未能实现；引句注1指向Hofer p.37。正文记Piazzetta 1747年为Platnerus外科教材绘制扉页、Haskell所称Guardi兄弟挪用其《Gerusalemme Liberata》图稿及相关画作分藏、Piazzetta 1754年去世和Albrizzi为其撰写生平并以学术素描集保存记忆。记录Albrizzi印书铺、1761年Robert Adam委托出售其《Diocletian宫》书、私人藏画与Piazzetta素描、赞助Zuccarelli/Zais、1770年Scuola di S. Rocco Guardiano任职和展览活动；另记录Pasquali对Lodoli的敬仰、禁书《Dei delitti e delle pene》秘密流通、Smith商号与朋友圈。人物、作品、书信、机构等仅在文字直接支持处建候选；无名Zais画作和身份不明Diocletian宫对象不扩展身份。

页末Gherardi引文尚未结束，续至p.337；印刷注1–8待规范合并注释L195–202按源序处理。p.336称Albrizzi 1777年去世时85岁，与p.334记1699年出生相冲突，保留两条statement并互链`internal_source_conflict`，不自行算改出生年份。页图校读只记S2：L45 `Use`→`life`、L49 `die`→`the`、`povertystricken`→`poverty-stricken`、`successful Use`→`successful life`。本页新增候选`cand-9997`–`cand-10009`（13项）、48条提及和36条statement；p.335续句statement同步从open更新为closed。

受控迁移脚本`chp13_p336_migration.py`默认dry-run，锁定源段、PDF哈希、表前态、候选号、mention跨度、statement引句/外键及前页续句；dry-run显示+13候选/+48提及/+36 statement后应用，表恢复副本后缀`.bak-s2-chp13-p336-20261003`。首次全表审计发现Gherardi书信候选`cand-10008`主锚点落在尚未审阅的合并注释L202，违反coverage；已将主锚点改至正文已审阅L50并保留L202待正式脚注回链，候选表修复恢复副本`.bak-s2-chp13-p336-candidate-ref-fix-20261003`。最终`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，另保留两条既存enrichment `source_ref`警告和238 queued/5 partial提示；`tests/test_audit_tables.py`与`tests/test_build_source_segments.py`共13项通过。p.336为partial；下一源序段`chp-13:13_CHP-13_intro:l52-59`（印刷页337）。

## 第十三章印刷页337正文（2026-10-03）

按源序核读`chp-13:13_CHP-13_intro:l52-59`，对照`CHP-13.pdf`物理页6。p.336开头Gherardi–Muratori引文在p.337 L53首句闭合，补记续文定位和收口状态。正文记Pasquali对Carlo Lodoli的敬仰、其与审查制度冲突以及1764年因秘密散发Beccaria禁书而遭Inquisitori di Stato追究；在压力下透露购书客户名单的细节按Haskell叙述保存，同时保留“No martyr”是作者评价。记Joseph Smith对商号的控制、早期英文文法书、1749年记录Smith收藏的插图书、《Dactylografa Smithiana》所载100幅Brustolon版画及Medusa末版画、Pasquali的Piazzetta宗教书（Caime委托资助）、以及1761年起出版的Goldoni十七卷本与Goldoni的制作意见。对匿名文法书、Medusa末版画及Albrizzi出版的Zanetti宝石图录使用描述性候选，不把近似索引题名先行等同。p.337可见注1–6待合并注释L203–208按源序迁移；正文中Goldoni引文在该页闭合。

页图校读仅记S2、不改S0：L53 `chased`→`chafed`、禁书标题后的误撇号校为分号；L56 `painterly. Baroque`→`painterly Baroque`；L57 `à`→`a`、`pubUcations`→`publications`；L58 `général`→`general`；L59行首OCR连字符删除。受控脚本`chp13_p337_migration.py`默认dry-run，校验源/PDF哈希、表前态、候选编号、44处精确mention跨度、30条statement引句/外键及p.336续句状态；dry-run后应用，四表恢复副本后缀`.bak-s2-chp13-p337-20261003`。应用后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，当前826段为475 complete、108 excluded、237 queued、6 partial；候选9,999、提及21,358、statement 9,533。两条既存enrichment `source_ref`警告仍在；`tests/test_audit_tables.py`与`tests/test_build_source_segments.py`共13项通过。下一源序段为p.338 `chp-13:13_CHP-13_intro:l61-68`。


## 第十三章p.338语义迁移（2026-10-03）

按源序核读`chp-13:13_CHP-13_intro:l61-68`并对照`CHP-13.pdf`物理页7。新增11个候选（cand-10013–cand-10023）、48条提及和23条statement。处理Goldoni关于扉页设计的批评及其以具体生活场景代替陈套图像的建议，结合卷二自传例证与Plate 57b；将Haskell对Novelli插图、专业威尼斯生活、Longhi比较、精致度和“启蒙资产阶级”趣味的论述保留为作者解释。记录Pasquali对Nollet实验科学译著、Lodoli/Vignola版及Visentini反巴洛克论述的支持；将Zatta对耶稣会的支持、与当局冲突、拟议出版攻击耶稣会对手之作分别记述，不扩展为具体出版合同或已实施的出版事实。Plate 57b复用既有候选`cand-4079`。印本校读仅记S2、不改S0：`général`→`general`、`Pasquah’s`→`Pasquali’s`、`pubheations`→`publications`、`suture`→`future`。p.338脚注1–2映射至合并注释L209–210，尚待源序处理；Zatta句续至p.339 L71，coverage保持partial。

受控脚本`chp13_p338_migration.py`默认dry-run，核验来源/PDF哈希、表前态、候选ID、mention跨度、statement锚点/外键和续页状态；dry-run显示+11/+48/+23后应用，四表恢复副本后缀`.bak-s2-chp13-p338-20261003`。应用后结构审计为`s2_missing=[]`、`errors=[]`；826段覆盖状态为475 complete、108 excluded、236 queued、7 partial，候选10,010、提及21,406、statement 9,556。下一源序段为p.339 `chp-13:13_CHP-13_intro:l70-77`。


## 第十三章p.339语义迁移（2026-10-03）

按源序核读`chp-13:13_CHP-13_intro:l70-77`并对照`CHP-13.pdf`物理页8。新增13个候选（cand-10024–cand-10036）、59条提及和23条statement。先闭合p.338段末“the Portuguese”与本页L71“government”组成的短语，更新p.338 statement续句状态为closed；与此相连的印本脚注1映射到L211–212但尚未处理。

Zatta段记录同时代传闻称他是耶稣会第三等级成员、其私人社会活动在Haskell叙述中不显、其序言和目录所见出版角色。对“Accademia dei Cacadubbj”按讽刺性名称记录，不把讽刺话语升为真实机构或说话人身份；喷泉和海豚的寓意按Haskell转述的戏仿保留，不当作Zatta原意。记录目录中的出版规模判断、1756年Petrarch版、1757年Dante插图版以及稍后Ariosto、Tasso、Metastasio作品；Dante版首见于两世纪的说法保留为Haskell历史判断。Fontebasso、Zompini服务Dante插图的叙述及Novelli自1781年开始为Metastasio作品作插图、七年后为Goldoni完整版本另制图稿均分别入statement；依据索引候选将后者关联到Zatta版插图组，但指出正文该句本身未写出出版商。Goldoni插图的社会世界与p.338 Pasquali版相较“更低”保留为作者比较，不推断其具体阶层。

Pinelli在本页被描述为国家出版业务参与者、私人收藏家和赞助人；其私人图书馆及绘画收藏先以type undecided候选保留，因类型表没有个人收藏专类，不冒充机构或文献。来源写“the State”，不据地理语境合并成共和国。页图校读仅记录于S2、不改S0：L72“social Use”读作“social life”；L77“thepublisher”读作“the publisher”，脚注数字“8”读作“6”。p.339印本脚注1–6映射至合并注释L211–216，留待书末注释按源序处理；本段coverage为reviewed/partial。

受控迁移脚本`chp13_p339_migration.py`默认dry-run，核验来源/PDF SHA、各表前态、ID、mention原文跨度、statement引文/外键、前页开放续句、脚注锚点及coverage状态。dry-run通过后应用；候选、提及、statement和coverage四表均保存恢复副本，后缀`.bak-s2-chp13-p339-20261003`。结构审计`s2_missing=[]`、`errors=[]`；写入后状态为826段：475 complete、108 excluded、235 queued、8 partial，候选10,023、提及21,465、statement 9,579。下一源序段为p.340 `chp-13:13_CHP-13_intro:l79-88`。


## 第十三章印刷页340正文（2026-10-03）

按源序核读`chp-13:13_CHP-13_intro:l79-88`，对照`CHP-13.pdf`物理页9。新增候选cand-10037–cand-10058共22项、72条提及和41条statement。复用Maffeo Pinelli、其图书馆和绘画收藏及已登记的艺术家、出版商和版画家候选；对Pinelli的收藏趣味只保留Haskell明确的推断与“似乎”限定。藏品中四幅作品只称“Tiepolo”，另以姓氏候选保留，不与Giambattista或Gian Domenico Tiepolo合并；旧大师作品保留“归于”语气，不登记为已确定作者。Maggiotto为Pinelli制作的总督肖像组、威尼斯教宗/枢机主教肖像、寓意作品与“Good Inclinations”分别按原文指称保留；总督组虽关联Plate 68a，仍与既有三幅肖像候选cand-4190及另一Maggiotto组cand-3352分开待审。

Remondini部分记录Bassano创立地、威尼斯分部、廉价小说与宗教版画的受众、业务扩张后出现的国际客户、较老牌出版机构的竞争和敌意，以及Haskell对低价仿制版画的批评。将“不同公众”与后文“国际客户”作为不同语境处理；未具名竞争机构不映射到宽泛的威尼斯出版商索引项。记录该公司为复制既有绘画/图稿而聘用版画师及其传播Piazzetta、Amigoni、Guarana和Pietro Longhi作品的叙述。Wagner、Viero分别按开店时间和原作委托有限的来源语气记录；Furnaletto在Ponte de’Baretteri经营三十余年，以及1766年委托Canaletto绘制威尼斯公爵仪典图稿、计划由Brustolon制版，保留为委托/预定制作，未声称版画已完成。未命名仪典仅保留事件类描述候选。

印本脚注1–6对应合并注释L217–222，尚待该注释段按源序处理，故本段为`reviewed/partial`。脚注3在S0拆分：L219以“published by A.”结束，L88另载“Rava, 1911.”；两处锚点均保留，待处理注释时判断完整书目，未补造题名或作者全名。页图校读只登记于S2、不改S0：L84行首补记印本连字符；L86删除OCR多出的句点；L87删除OCR多出的撇号。原文限定词、作者判断和作品未决身份均继续保留。

受控脚本`chp13_p340_migration.py`默认dry-run，锁定源文件、PDF及段落哈希，检查表前态、候选ID、提及跨度、statement引句/外键和脚注回链；dry-run通过后应用，并为候选、提及、statement和coverage表保存`.bak-s2-chp13-p340-20261003`恢复副本。首轮应用后发现两处提及锚点重叠，经原文重复短语核对，修正第二处`his collection`至本段第二次出现的位置；修正前另存mentions恢复副本。最终审计`s2_missing=[]`、`errors=[]`；826段中475 complete、108有理由排除、234 queued、9 partial；候选10,045、提及21,537、statement 9,620。下一源序段为p.341 `chp-13:13_CHP-13_intro:l90-96`。


## 第十三章印刷页341正文（2026-10-03）

按源序核读`chp-13:13_CHP-13_intro:l90-96`，对照`CHP-13.pdf`物理页10。复用索引中的Zanetti、Crozat、Sebastiano与Marco Ricci、Carriera、Pellegrini、Mariette、Regent、Arundel、Prince Eugene、Poussin、Castiglione、Crespi、Smith、Schulenburg与Tessin候选，以及对应城市候选；只对缺少的Rotterdam、Plate 58a图像指针、未具名群体和描述性作品组增补18个候选。为“Crespi”“Poussin”“Castiglione”及“the Regent”等来源中的姓氏/称谓保留S1候选但明确延后身份裁决。Plate 58a仅记正文图版指针，图中对象、媒介和作者须待视觉段处理。

记录Zanetti的绘画训练、版画与收藏身份、收藏声誉和威尼斯鉴赏家圈；其与Marco Ricci、Crozat、Carriera、Mariette和Tessin的友情/通信，以及Carriera与Pellegrini姻亲关系分别入statement候选。按原文限定语记录Zanetti于1720年前往巴黎、经Rotterdam、1722年返回威尼斯后“似乎”赴Vienna及1736年确定重返；记Regent托其为画廊购画、送出本人《Daphnis and Chloe》插图，但不推定版书已经出版。Arundel的Parmigianino图稿按购买与影响鉴赏趣味两层记录。1736年从Prince Eugene继承人处购买的Poussin、Castiglione和Crespi作品保留未题名状态，相关评价语气和身份仍待后续脚注与S3核对。Tessin对rococo及优雅轻快题材的法文引文保留原文；p.341句尾“and he made”续至p.342 L99，未推断其后动词宾语。

页图校读只记S2、不改S0：L91 `number.of men`→`number of men`、`ani he soon`→`and he soon`。印刷页脚注1–4映射至合并注释L223–226；该注释段尚未按书序迁移，故本段为`reviewed/partial`。受控脚本`chp13_p341_migration.py`默认dry-run，锁定来源/PDF/段落哈希和写前账本，验证18个候选ID、89条精确提及跨度、26条statement引句/外键、脚注映射及续页指向；应用前输出已逐项检查。应用后四表恢复副本后缀为`.bak-s2-chp13-p341-20261003`。结构审计`s2_missing=[]`、`errors=[]`；826段中475 complete、108有理由排除、233 queued、10 partial；候选10,063、提及21,626、statement 9,646。下一源序段为p.342 `chp-13:13_CHP-13_intro:l98-105`。


## 第十三章印刷页342正文（2026-10-03）

按源序核读`chp-13:13_CHP-13_intro:l98-105`，对照`CHP-13.pdf`物理页11。p.341 L96的“and he made”由本页L99闭合为Tessin借助Zanetti的鉴赏与学识增加自己的收藏；同页开始叙述Tessin送一名未具名门生向Zanetti学习、年轻人很快去世，以及经Zanetti向Tiepolo传递友好消息、瑞典国王拒绝为引诱Tiepolo赴斯德哥尔摩而支付高额款项。消息中的希望不被写成Tiepolo实际情绪反应，君主身份保持未定。

分别记录Tessin从Zanetti处购买Zuccarelli绘画、Nogari绘画及G. M. Crespi版画；Zanetti经办Tessin委托Gai雕塑一事。该塑像只作为“拟塑一位从浴场出来的Venus、以与Tessin所藏Giovanni da Bologna的Bathsheba配对”登记，不称已经完成；将“Giovanni da Bologna”保留为独立名字候选，供S3裁决其与现有索引候选是否同一。Tessin“un demi-Michel Ange”的说法保留为对Gai的引语评价，注4尚待核读。

记录Haskell对Zanetti作为威尼斯与欧洲中介者的概括，以及其收藏较少关注威尼斯以外当代艺术的限定；其藏有Brand和Dietrich作品、没有证据表明曾购入现代法国/英国绘画、素描或版画，不改写成绝对不存在此类购买。法国、英国购入的部分较早作品被称重要并影响其趣味。另记录三幅Sebastiano历史画、Zanetti委托Marco Ricci创作的约六幅风景画、Carriera粉彩与微型画、Canaletto和Zuccarelli早期声誉、从London/Paris/Rotterdam/Vienna带回的奖章与宝石以及大型版画收藏。索引已有medals/gems与print collection候选予以复用；未知作品不补造标题。

处理1752年Zanetti关于版画收藏的第一人称引语，保留其“费尽心力与开销”“超过私人藏家预期”及可提供罕见版画的自述。p.342末尾“except the dish engraved with a Bacchanal by Annibale and the lascivious”在p.343 L108继续，当前只记不完整例外，不推断该器物是否不在收藏、不可出示或另有原因。页注1–7对应合并注释L227–234；这些注释仍待按源序迁移，故p.341、p.342继续保持partial。Plate 58a图像核查也仍待处理。

页图校读只记S2、不改S0：L102 `thereis`→`there is`、`showthat`→`show that`；L104 `Camera`→印本`Carriera`。候选cand-10077–cand-10090新增14项；迁移脚本初次预演生成80条提及，表审计发现“those countries”两条不同候选占据同一跨度。因前文`French`与`English`已各自有锚点，精确修复删除该重复指代跨度，最终本页新增78条提及、26条statement。脚本`chp13_p342_migration.py`默认dry-run，固定源/PDF/段落哈希、前态、候选编号、mention原文跨度、statement引句/外键、脚注映射和p.341续句状态；四表恢复副本后缀`.bak-s2-chp13-p342-20261003`。重叠修复由`chp13_p342_overlap_repair.py`单独预演并应用，mentions恢复副本后缀`.bak-s2-chp13-p342-overlap-fix-20261003`。

最终结构审计`s2_missing=[]`、`errors=[]`；全账本826段：475 reviewed/complete、108有理由排除、232 queued、11 reviewed/partial；候选10,077、提及21,704、statement 9,672。两条既存enrichment `source_ref`警告不变。下一源序段为p.343 `chp-13:13_CHP-13_intro:l107-114`，先闭合本页版画引语，再沿正文源序继续。


## 第十三章印刷页343正文（2026-10-03）

按源序核读`chp-13:13_CHP-13_intro:l107-114`，对照`CHP-13.pdf`物理页12。p.342 L105开放引语续为`prints of Giulio Romano engraved by Marc’Antonio with Aretino’s sonnets`，随后Zanetti说自己从未见过这组版画；这不是对前一项Annibale碟画的描述。两者以及多份版画的购买、保留和交换均在S2分开记录，第一人称内容归于Zanetti的1752年书信语境，footnote6/7暂待L233–234的正式迁移。

Haskell描述Zanetti以完整性为主要目标，同时偏爱靠近rococo的Mannerist与“picturesque”作品：Ugo da Carpi和Parmigianino作品由Faldoni刻制，海外旅行中购入Rembrandt和Callot版画，1759年自刻Castiglione十二幅图稿。年轻A. M. Zanetti在1760年序言中的分类——艺术家与公认鉴赏家偏好速度、活力和宽笔触，普通公众偏好精细完成和强烈明暗对比——保留为引语及Haskell随后对Zanetti归类的层次，不扩展为所有观众的统计判断。

另记录Zanetti认为自己最重要的成就是恢复三、四种颜色的chiaroscuro木刻工艺；他在London期间复兴旧技法，制成约五十张、主要取自或改编自Parmigianino图稿的木刻，随后毁去版片，并向Prince of Liechtenstein献出整套、向英法威尼斯友人分赠单张。Haskell关于版画艺术性与其文人/幻想结合的判断、rococo与neo-classical可以并存的论述，及对Tiepolo蚀刻版画的评价均作为作者/引文层记录。Algarotti与Zanetti对风格综合的差异分别处理。`
Delle Antiche Statue Greche e Romane`始于1725年、约十五年后由Albrizzi出版；p.343 L114“in it Zanetti subordinated”未完，交由p.344闭合。

本页印刷脚注1–4分别映射合并注释L235–238，尚未按原书注释段迁移，故coverage为`reviewed/partial`。S3身份候选包括只以Marc’Antonio和Aretino出现的版画参与者、以及只具头衔的Prince of Liechtenstein；均不从上下文补全姓名。印本校读仅记S2、不改S0：L108 `Aretino’s.sonnets`→`Aretino’s sonnets`并删去引语后的OCR杂符；L111 `Rembrandtand`→`Rembrandt and`、`whomhe`→`whom he`；L112 `He - revived`→`He revived`、删除`his`与`stay`之间的OCR引号；L113 `Zanetti, had`→`Zanetti had`。

受控脚本`chp13_p343_migration.py`默认dry-run，校验来源/PDF/段落SHA、写前状态、候选编号、59条mention跨度、statement引句/外键、脚注位置及p.342开放引语。应用时先扩展p.342 statement的断言和跨段引用；第一次审计发现`original_quote`必须保持在该statement所指的p.342 segment内，不能拼入p.343原文。通过`chp13_p343_quote_repair.py`将引文恢复为p.342精确片段，同时由p.343独立statement记录其续文与“从未见过”的断言，并保留交叉引用；恢复副本后缀`.bak-s2-chp13-p343-quote-repair-20261003`。最终全账本审计`s2_missing=[]`、`errors=[]`；826段：475 complete、108 excluded、231 queued、12 partial；候选10,090、提及21,763、statement 9,695。两条既存enrichment `source_ref`警告不变。下一源序段为p.344 `chp-13:13_CHP-13_intro:l116-122`。


## 第十三章印刷页344正文（2026-10-03）

按源序阅读chp-13:13_CHP-13_intro:l116-122并对照CHP-13.pdf物理页13。闭合p.343末句关于《Delle Antiche Statue Greche e Romane》的内容续文，记录其学术取向和版画在威尼斯新古典趣味兴起中的位置。新增cand-10104作为独立archive文献；修订p.343原publication-history statement，将起始年份1725和十五年后由Albrizzi出版拆成两个事实，更新书名mention外键，不把作品继续挂在Zanetti人物索引候选下。

本页识别p.337候选cand-10012为《Dactyliotheca Ant. M. Zanetti》，记录其1749年出版、宝石与奖章目录、Zanetti提供插图、Albrizzi出版、Francesco Gori撰拉丁评论、为一般读者提供意大利语译本，以及先考虑波兰国王、后选瑞典女王作拟议献辞对象。保留Zanetti关于友人和外国读者的第一人称说法；Haskell关于其自费出版、奢华销售图录目的的解释，以及Abbé Clement的引语分别按陈述者和解释层级登记。姓名仅依当前原文，未替Gori、国王或女王消歧。

继续记录Zanetti的私人绘画、歌剧人物讽刺画像、版画活动和Haskell对其影响Tiepolo《Vari Capricci》的判断；记录其雇用、收留并定期资助Gaetano Zompini，Zompini雕刻Zanetti所有的Castiglione图稿并于1753年为《Le Arti che vanno per via nella Città di Venezia》绘图。两组Castiglione图稿与p.343的Zanetti 1759年十二幅图稿保持分开。个人藏品两项分别记录：cand-10113为Zanetti宝石与奖章收藏，cand-10112为其Felicita Sartori作品收藏；当前taxonomy没有个人收藏类型，二者均留空suggested_type，而目录与具体作品仍按archive/work分别登记。L122是印刷脚注5的续文；L239–246中注1–8仍待按源序迁移并回链。

印本校读只记S2，不改S0：L119的Rosalba Camera按印本读作Carriera；Vari Capriccj读作Vari Capricci；L122的Félicita读作Felicita。1752年Zanetti引文在可用PDF页末止于“two”；后续PDF页为Plate 57，没有提供正文续页，故不推断未见内容。

p.344受控迁移脚本chp13_p344_migration.py默认dry-run，核验来源、PDF、段落SHA和表前态；应用后候选/提及/statement/coverage备份后缀为.bak-s2-chp13-p344-20261003。随后运行chp13_p344_collection_refinement.py，为两组私人收藏补充待决对象并单独保存候选、提及和statement备份，后缀.bak-s2-chp13-p344-collection-refinement-20261003。最终audit_tables.py --summary通过：s2_missing=[]、errors=[]；826段中475 complete、108 excluded、230 queued、13 partial；候选10,100、提及21,796、statement 9,724。保留两条既存enrichment source_ref警告。下一源序段为图版Plate 57的chp-13:13_CHP-13_intro:l124-139。


## 第十三章印刷页346正文（2026-10-03）

对照`CHP-13.pdf`物理第19页处理规范段`chp-13:13_CHP-13_intro:l173-177`。新增候选`cand-10126`（Merceria，place；具体街段/摊位未定）、7条精确提及和6条statement。接续p.345 L171未完句，记录Toni作为代理人及Sagredo、Zanetti、Consul Smith三项书内关系候选；Zanetti仅姓氏、暂映射年长者但身份仍待S3，Consul Smith复用Joseph Smith索引候选且不视为身份核验。Haskell称Venice艺术世界“flourishing and parasitic”的评价单独保留为作者解释；“would go and buy”按习惯/叙事性表达记录Toni从Leonardo Pasquetti购版画，不推定某次具体交易。Merceria只登记为地点候选，不补出具体地址。段末“anonymity and silence”作为修辞过渡，不转为实体断言。

应用后首次结构审计指出跨页statement把p.345起始行锚在p.346 segment内，违反coverage边界，且原引文包含上一段文字。已将statement来源锚限定为本段L174–175、原引文限定为本段实际文字，并在qualification及cross-reference中保留p.345续接关系。复审`python -X utf8 scripts/audit_tables.py --summary`后`errors=[]`、`s2_missing=[]`；全账本830段：484 complete、108 excluded、224 queued、14 partial；候选10,113、提及21,872、statement 9,778。保留两条既存enrichment `source_ref`警告；下一段为合并注释`chp-13:13_CHP-13_intro:l179-251`。


## 第十三章p.332–334注释迁移（2026-10-03）

处理合并注释段`chp-13:13_CHP-13_intro:l179-251`的L180–191，并逐页核对`CHP-13.pdf`物理页1–3的印本文字、注号和正文回链。p.332注1–5记录Horatio Brown、Berengo、Goethe、Morazzoni、Gallo与Marin的引用；将Marin的挑战明确归于书内注释转述，印本为`VIII, p.234`而S0 OCR写作`Vin`。p.333注1记录Roberti 1900页326–35的引注，不扩出题名或作者全名。p.334注1–6记录Bettinelli《Lettere inglesi》第二封信、Morazzoni两处独立页码引注、Bossuet第八卷1755年献辞提示、Battagia引注、`Novelle della Repubblica delle Lettere`“as from 1729”的出版时间限定，以及Hazard 1946卷I页105–7及注。仅重用有依据的候选；短引文候选保持未决，等待书目段落定位。未声称独立查阅任何被引来源。

为可追溯性新增19个候选（6个人名候选及13个书目/引文候选）、28条精确提及、15条note statement；将三段正文（p.332–334）及其脚注回链标为complete。S2只记录印本校读：L183`Vin`→`VIII`，L185`3 26-3 5`→`326-35`，L186`letters seconds`→`lettera seconda`，L190注号`6`→印本`5`；规范OCR未改。复用`cand-9988`并把其publication start说明更新为“as from 1729”，不推定首期确切日期。

首次审计发现`Morazzoni`作者与短引文候选落在完全相同的mention区间；已将短引文锚点扩至含句点的`Morazzoni.`，保留作者mention为其严格内含的子区间。最终`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全账本830段：487 complete、108 excluded、223 queued、12 partial；候选10,132、提及21,900、statement 9,793。两条既存enrichment `source_ref`警告不变。注释段L180–191完成，下一源范围L192–238；L247–248倒序镜像题注仍待账本处置。

## 第十三章p.335注释（2026-10-03）

按印本核对合并注释L192–194及规范OCR L38–39，对应CHP-13.pdf物理页4。注1回链p.334关于恢复威尼斯版画声誉的广告断言，限定为1730年3月19日《Novelle》所载的拟议圣奥古斯丁作品版；注2给出Piazzetta为Recurti出版的宗教书绘制《Religion trampling on Heresy》、由Pitteri刻制及Gallo 1948页176注4的书目线索；L38继续保存Albrizzi与Recurti关系的《Novelle》指引。注3把约70幅《Gerusalemme Liberata》图稿的原属、曾在England及现藏Royal Library, Turin分成三条有时态限定的断言。注4已存在于规范OCR L39而非合并注释段；PDF确认“Richard, II, p.492—quoted by Morazzoni, p.125”，将其识别为页注并回链“该书受Abbé Richard赞赏”的断言。以上引文均未独立查阅。

本批新增7个候选、16条提及和7条statement；复用既有Piazzetta、Pitteri、Recurti、Novelle、Gerusalemme图稿、Richard及Morazzoni候选，并将cand-9993补明为脚注所给书名。S2记录OCR校读“Ges��”→“Gesù”及L39“Richard, H”→“Richard, II”，未改写来源OCR。受控脚本chp13_p335_notes_migration.py先dry-run，再应用；四表备份后缀为.bak-s2-chp13-p335-notes-20261003。覆盖账本现为830段：488 complete、108 excluded、223 queued、11 partial；候选10,139、提及21,916、statement 9,800。audit_tables.py --summary为s2_missing=[]、errors=[]，仍有两条既存enrichment source_ref警告。下一源序为合并注释L195–202（p.336注1–8）。

## 第十三章p.336页注迁移（2026-10-03）

对照CHP-13.pdf物理页5，按源序处理合并注释段chp-13:13_CHP-13_intro:l179-251的L195–202。注1的Hofer页37仅作为原书引用定位，回链Gerbault订阅计划及未实现结果，并清除跨p.335–336续句的待处理标记。注2将Guardi大型画布组分布于Washington、Copenhagen、Hull的博物馆及London私人收藏记录为一条整体位置报告；不补造博物馆名、藏家或现藏核验。注3复用Morazzoni无页码引用候选；注4分别保留Moschini 1809页5与Gradenigo页71；注5记录方括号作者形式的Memorie引注。注6分别记录三条Moschini定位、Brandolese编制而Haskell未能追索的目录，以及Albrizzi版画收藏；该收藏不属于现有work定义，留类型待决，并将cand-10007私人绘画/素描收藏从work修正为类型待决。注7记录Morazzoni页117；注8记录Gherardi致Muratori、1749年7月12日、Biblioteca Estense的书信引注及其意大利语引文。未独立查阅上述书目或档案，均按Haskell原书转引留证。

对照页图校正S2中的OCR记录，不改S0：L196删除“and . private”中的多余句点/分页符；L200将“1815,1”读作“1815, I”、“1806, HI”读作“1806, III”，并校读Albrizzi所有格；L202校读è、dell’Albrizzi与interesse。页图还确认同行注号的实际范围：注1位于Gerbault计划失败句后，不覆盖同一OCR行的Platnerus扉页断言；注6位于Zais高评价句后，不覆盖其后的1770年展览断言。三条误挂已移除；该页其余脚注均与实际断言回链。Gherardi引文续至p.337，引用与正文保持跨段交叉链接。

本批新增11个候选、32条精确提及和10条statement；新增恢复副本后缀.bak-s2-chp13-p336-notes-20261003。cand-10008仍表示Haskell所引而未独立查阅的书信；个人绘画/素描收藏cand-10007与版画收藏cand-10163分立且类型待决。写入后audit_tables.py --summary为s2_missing=[]、errors=[]；全账本830段：489 complete、108 excluded、223 queued、10 partial；候选10,150、提及21,948、statement 9,810。两条既存enrichment source_ref警告不变。合并注释段L180–202已迁移但仍partial；下一源范围为L203–208（p.337注1–6）。

## 第十三章p.337页注迁移（2026-10-03）

对照`CHP-13.pdf`物理页6，按源序处理合并注释段`chp-13:13_CHP-13_intro:l179-251`的L203–208。注1记录Memmo 1786年页45的书内定位、Lodoli作为`Revisore della Stampa`对出版商与书商的影响、Conti致Vico的1728年书信及其由Fisch和Bergin刊布的页184定位，并把“Pasquali paid a good deal of attention”明确记为Haskell的推断。注2记录Pasquali致Prato书商Niccola Mazzoni、日期1785/6年1月7日的书信及意大利语引文；按原书转引Nuti 1941年页199，不推断引语中“qui”的地理所指，保留来源拼写Niccola与索引拼写Nicola的差异。注3登记威尼斯Archivio di Stato的Inquisitori di Stato 537号记录定位，印本页码/叶码读作32v，规范OCR为Z2v；档案未独立查阅。注4登记1736年9月8日《Novelle della Repubblica delle Lettere》期号并回链未具名英文文法书statement；注5只登记Morazzoni页116定位；注6登记Goldoni《Delle Commedie》第一卷（1761）序言`L’Autore a chi legge`第v–vi页。上述被引材料均只记为Haskell所引，未声称独立查阅。

本批新增13个候选、27条页注提及和9条statement，并为正文L53补录Prato提及1条，提及合计28条。印本确认注4只指向英文文法书，移除同一OCR行中误挂到Joseph Smith控制出版商号断言的注4标记。脚本`chp13_p337_notes_migration.py`默认dry-run，校验来源/PDF SHA-256、表前态、候选外键、精确提及跨度及注号回链；应用前四表恢复副本后缀`.bak-s2-chp13-p337-notes-20261003`。写回后p.337正文由partial转complete；合并注释段已迁移到L180–208，L209–246及镜像题注L247–248仍待处理。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全账本830段：490 complete、108 excluded、223 queued、9 partial；候选10,163、提及21,976、statement 9,819。两条既存enrichment `source_ref`警告不变。下一源序为p.338注1–2（L209–210），随后p.339注1–6（L211–216）；S2未收口，不交接S3。

## 第十三章p.338页注迁移（2026-10-03）

对照`CHP-13.pdf`物理页7，按源序处理合并注释段L209–210。注1以页下注书目定位Goldoni《Delle Commedie di Carlo Goldoni avvocato veneto》第二卷（1762）页1，连接他建议以自身生平场景替代程式化扉页的断言；印本卷号为II，规范OCR误作H。注2记录Antonio Zatta致未具名公爵的1761年书信，题名在“Duca di...”处省略；印本载“In Fiorenza [in fact, Venice]”，按Haskell括注保存威尼斯修正，不把Florence记作实际出版地点；另记《Lettera Giustificativa di Antonio Zatta》（Venezia，1761）。该注认为既有争论可由这批出版材料澄清，Zatta坚决支持耶稣会；作为Haskell对所引材料的解释与信心表述保留，未独立查阅或外推为无来源限制的定论。

本批新增3个archive候选、9条精确提及和4条statement。页图确认注1回链Goldoni生平场景扉页提议，注2回链Zatta支持耶稣会statement；移除同行OCR误挂至Vignola版献辞的注1及误挂至拟议出版攻击性著作statement的注2。脚本`chp13_p338_notes_migration.py`默认dry-run，核验来源/PDF SHA-256、表前态、候选外键、statement精确原句、mention跨度及页图确认的标记映射；写入前四表恢复副本后缀`.bak-s2-chp13-p338-notes-20261003`。写回后p.338正文由partial转complete；合并注释段已迁移到L180–210，L211–246及镜像题注L247–248仍待处理。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全账本830段：491 complete、108 excluded、223 queued、8 partial；候选10,166、提及21,985、statement 9,823。两条既存enrichment `source_ref`警告不变。下一源序为p.339注1–6（L211–216）；S2未收口，不交接S3。

## 第十三章p.339页注L211–216（2026-10-03）

按源序对照`CHP-13.pdf`物理页8，迁移合并注释L211–216注1–6。注1拆记Inquisitori di Stato 535页173（1759年6月18日）与536页41v（1760年11月19日），链接回p.338“Portuguese government”跨页statement；两处档案未独立调阅。注2分开保存Cattaneo经Neri 1899页109转引的“terziario, a quel che pare”说法，以及`Nouvelles Ecclésiastiques`经同书页114转引的“Tiers Ordre”描述，保留“as it seems”限定与多层引述。注3把Zatta 1761年信页23回连到p.338注2，作为讽刺段引文的书内出处；p.339载体书候选`cand-10024`与已命名信件候选`cand-10178`显式留给S3做候选对齐。注4登记Zatta 1790年目录；注5保留未给题名的`G. da Venezia, 1934, pp.25–34`短引文；注6登记Pinelli 1785年售画目录及Moschini 1806卷II页64。引文与档案均未独立查阅。

印本校读记录：L211 `Archi vio`→`Archivio`、档案页码`4IV`→`41V`；L212年份`17Ó0`→`1760`；L213意大利语`quel die`→`quel che`；L215目录题名`c italiani`和`efigli`→`e italiani`和`e figli`，短引页码`p.25–34`→`pp.25–34`；L216`Sec also`→`See also`。脚注映射按印本标记而非同行OCR邻近内容确定：注3只挂讽刺性图像解释；注4只挂目录支持的出版量判断，不挂后续经典与Dante断言；注5只挂Metastasio插图句，不挂下一句Goldoni组作。移除“His own prefaces”到单书候选的错误mention，并解除该一般评价statement对候选书的错误对象链接。

受控迁移`chp13_p339_notes_migration.py`默认dry-run；写前核验S0/PDF SHA、合并注释段SHA、表前态、候选外键、每个原文跨度、statement引句及所有body-note目标；四表备份后缀`.bak-s2-chp13-p339-notes-20261003`。本批+8候选、+17页注mention、+7 statements，并删除1误映射mention；p.339正文coverage转complete。迁移后结构审计830段：492 complete、108 excluded、223 queued、7 partial；`s2_missing=[]`、`errors=[]`，两条既存enrichment `source_ref`警告不变。

## 第十三章p.340页注L217–222（2026-10-03）

按源序对照`CHP-13.pdf`物理页9，迁移注1–6。注1 Morelli卷V页348支持对Pinelli图书馆、绘画收藏散佚及同代人反应的书内引用；注2重用Berengo 1957短引文候选，并登记`Mostra dei Remondini`（1958）展览目录。注3连接Longhi致Remondini的七封信（1748–1752）和A. Rava（1911）：S0 L219止于“published by A.”，正文segment L88另载“Rava, 1911.”；分别保留两段原文、mention span及segment ID，用跨段引用关闭，不拼写成跨segment original_quote。注4 Moschini 1924页132只支持Wagner很少委托原作的说法；按印本脚注位置删除其到Wagner国籍、开店年份及店铺重要性断言的误连。注5复用Gallo 1948 pp.153–214来源候选以承接页184，并复用Moschini p.132候选，链接Viero段；注6复用Gallo来源候选的页158、186，链接Furnaletto所委托Canaletto图稿和Brustolon计划刻制的statement。引用源均未独立查阅。

`chp13_p340_notes_migration.py`默认dry-run，核验来源/PDF SHA、写前表状态、候选与mention外键、L219/L88续注、引句、标记目标和精确offset，再保存四表备份`.bak-s2-chp13-p340-notes-20261003`并应用。L218 OCR `Bercngo`校读为印本`Berengo`，行尾多余引号移除记录在S2、不改S0。p.340正文coverage转complete。全账本当前830段：493 complete、108 excluded、223 queued、6 partial；候选10,178、提及22,018、statement 9,836；`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，保留两条既存enrichment `source_ref`警告。下一源序处理p.341 L223–226脚注，并核对Plate 58a图版映射。

## 第十三章p.341页注迁移（2026-10-03）

对照`CHP-13.pdf`物理页10迁移L223–226注1–4。逐条记录注内书目与档案引用的层级，所引Lorenzetti、Borroni、Bottari、Mariette的`Abecedario`、Zanetti遗嘱、Biblioteca Marciana手稿、收据和`Memorie`均未独立查阅。注2的六幅Marco Ricci作品组与p.342另述六幅风景画组分开登记；注4的`lo Spagnolo di Bologna`作为未识别画家绰号，不直接并入Crespi；Anne Marie de Savoye仅记作收据签署人，不推为卖方；15件宝石/浮雕保留集合候选并留类型待决。页图校读把L225 `Ahecedario`校作`Abecedario`、L226 `Pncipe`校作`Principe`，只写S2过程与statement，不改S0转录。

此前已完整审阅视觉段`chp-13:13_CHP-13_intro_plates_visual-transcription:l5-7`及`CHP-13.pdf`物理页15：58a图注指向Zocchi创作、描绘A. M. Zanetti the Elder与Marchese Gerini of Florence的肖像；三个caption statements及图版段均已complete。p.341正文mention `Plate 58a`已映射到既有作品候选`cand-4048`，对应临时候选`cand-10059`标记excluded并说明替代候选；未把印本图注当作外部作者/人物身份核验。

受控脚本`chp13_p341_notes_migration.py`先dry-run再apply，锁定全源及PDF SHA和表前态，核验新增候选ID、44处精确mention跨度、14条statement引句/外键、四个footnote marker的正文目标、Plate 58a映射及coverage状态。四表恢复副本后缀`.bak-s2-chp13-p341-notes-20261003`。写回后p.341正文partial→complete，合并注释coverage范围L180–222→L180–226且继续partial。`audit_tables.py --summary`：830段中494 complete、108有理由排除、223 queued、5 partial；10,191候选、22,062提及、9,850 statements；`s2_missing=[]`、`errors=[]`。仍有两条既存enrichment `source_ref`警告。下一源序处理p.342注1–7（L227–234）。

## 第十三章p.342页注L227–234（2026-10-03）

对照`CHP-13.pdf`物理页11，迁移注1–7并回链p.342正文。注1记录Marciana手稿中Tessin七封信的日期/地点及印本对哥本哈根信日期的`sic—but 1748`修正；将Strahlsund保留为印本拼写，留S3判断地点身份。注2保留“首、三封信”及画家姓名不明；注3保存第三封信关于Tiepolo、价格、食宿与国王津贴的法文引文；注4回链Gai雕像叙述并记录“见第十章”。注5补明Zanetti收藏的《Esther and Ahasuerus》和《The Presentation in the Temple》，以及Pietro Monaco在`Raccolta di Opere scelte`中对应的第41、84号版画；另记录Rosalba Carriera肖像用作1749年`Dactyliotheca`扉页。注6记录A. F. Gori于1752年12月22日来信的Marucelliana架藏定位；注7保留Annibale碟画例外的意大利语引文及Kurz 1955页282–287书目定位。所有手稿、信件、书目、版画和肖像均未独立查阅，不将Haskell转引提升为独立证据。

本批新增9个候选、48条精确提及和11条statement，复用Lorenzetti/Bottari、Sebastiano Ricci作品、Monaco、Gori、Carriera、Dactyliotheca及现有收藏候选。p.342正文的7组页注回链完成，coverage partial→complete；合并注释coverage推进L180–226→L180–234且仍partial。校读只记S2、不改S0：L227破折号、L228空格及`(sic—but 1748)`、L230 `éloigné`→`éloigne`。按源句范围将p.342开放版画引语statement收窄为Annibale碟画；Giulio Romano版画留p.343续文。脚本`chp13_p342_notes_migration.py`默认dry-run并核验来源/PDF SHA、表前态、ID、外键、48个精确跨度、11条原文引句及页注回链；四表备份后缀`.bak-s2-chp13-p342-notes-20261003`。`audit_tables.py --summary`：830段中495 complete、108有理由排除、223 queued、4 partial；候选10,200、提及22,110、statement 9,861；`s2_missing=[]`、`errors=[]`。两条既存enrichment `source_ref`警告不变。下一源序处理p.343注1–4（L235–238）。

## 第十三章p.343页注L235–238（2026-10-03）

对照`CHP-13.pdf`物理页12，迁移注1–4。注1与注4均复用Lorenzetti 1917候选，分别记录页122及页55；注4只回链Tiepolo蚀刻版画的“首次发表”断言，并将1743保留为Haskell转述的可能年代（may well/as early as），移除其对前句广义风格判断的误挂。注2以`Varie Pitture a Fresco de' Principali Maestri Veneziani`（1760）序言为年轻Zanetti版画偏好引文的出处，书未查阅。注3逐名补录九位赠页对象，Richard Mead因此前候选表无对应项而新增候选；“among these”保留为例举，不给每位受赠者分派具体版画。另将p.342注6的Gori来信定位回链到p.343连续引语中的四条断言。印本校读只记S2、不改S0：L236 `de'Principali`→`de’ Principali`。

本批新增1个候选、15条精确提及和4条statement；p.343正文partial→complete，合并注释coverage推进L180–234→L180–238且仍partial。脚本`chp13_p343_notes_migration.py`先dry-run再apply，核验来源/PDF SHA、表前态、ID、外键、提及跨度、statement引句、脚注目标及跨页引语中的p.342注6回链；四表备份后缀`.bak-s2-chp13-p343-notes-20261003`。`audit_tables.py --summary`：830段中496 complete、108有理由排除、223 queued、3 partial；候选10,201、提及22,125、statement 9,865；`s2_missing=[]`、`errors=[]`。仍有两条既存enrichment `source_ref`警告。下一源序处理p.344注1–8（L239–246）。


## 第十三章p.344页注迁移与跨页引语校正（2026-10-03）

对照`CHP-13.pdf`物理页13迁移p.344注1–8（合并注释L239–246），新增4个候选、20条精确提及和10条statement。复用Borroni、Bottari、Blunt/Croft-Murray、Lorenzetti/Vianello、Moschini、Battistella及1843年`Memorie`候选；新增John Northall及其1767年短引来源、P. Clement短引来源和A. M. Zanetti致A. F. Gori的1752年8月26日信件定位。引用页、手稿均未独立查阅。注2拆分Abbé Clement描述与Northall引文，保留`Signor Lanetti’s [sic]`；注5的Rosalba日记编辑者意见与L122续文分别记录，复用p.276已识别的1843年`Memorie`，与Zanetti 1736年`Memorie`候选分开。L240页码`p. 43 8`校作印本`p. 438`，L243 `sec`校作`see`，L122 `Félicita`按印本读作`Felicita`；S0不改。

应用前dry-run通过；四表恢复副本后缀`.bak-s2-chp13-p344-notes-20261003`。首次全表审计发现四个新候选的`candidate_origin`用了未注册值`s2_source`，已按既有来源候选统一改为`body-mention`；随后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`。审阅印本脚注标记确认注1只连Albrizzi出版《Dactyliotheca》的断言；其他被注号误扩散的p.344 statement已解除注1链接。

同次复核发现此前关于续页的判断错误：物理页14是Plate 57，但`CHP-13.pdf`物理页18是印刷页345，L162已记录Zanetti 1752年引语续文并与p.344 statement互链。p.344正文coverage因此由partial改为complete。随后完成L247–248镜像题注核对及p.345注1–3（L249–251）迁移；第13章下一段转入第14章。

## 第十三章p.345正文、页注及镜像题注收口（2026-10-03）

对照`CHP-13.pdf`物理页18完成正文`l161-171`及合并注释尾段L247–251。L247–248为反向/错序OCR题注片段，所载信息与Plate 57/58既有视觉转录段对应；逐项核对OCR残片与题注内容后按重复材料处理，不再新增提及或statement。p.345注1登记Pietro Monaco 112幅版画集短题名并与1763、1779两个现有版本候选保持未决；印本`di`校正OCR `Ji`只记于S2，不改S0。注2保留信件日期`4 February 1763/4`的印本歧义及British Museum架藏号`Add. MSS. 23,729, f. 49`，信件未查阅。注3登记Haskell所引Moschini 1924页167及其称信息源为P. A. Novelli撰写、藏于Seminario Patriarcale的Toni手稿生平；L171所载1790与1762年代均保持为Haskell报告，手稿与引用页未独立查阅。三条印刷脚注均按标记回链至p.345正文；L171的跨页句与p.346段保持连接。

新增3个候选、15条精确提及和3条statement。受控脚本`chp13_p345_notes_migration.py`默认dry-run；核对来源/PDF SHA、表前态、候选外键、精确mention跨度、statement引句、脚注标记目标及镜像题注已有coverage后应用，四表恢复副本后缀`.bak-s2-chp13-p345-notes-20261003`。写回后运行`python scripts/audit_tables.py --summary`：830段中499 complete、108 excluded、223 queued、0 partial；候选10,208、提及22,160、statement 9,878；`s2_missing=[]`、`errors=[]`。两条既存enrichment `source_ref`警告不变；审计另提示223段仍queued，且结构检查不代替语义复核。下一源序转入第14章。


## 第十四章p.347开篇及注1–2（2026-10-03）

按源序处理规范段`chp-14:14_CHP-14_intro:l3-12`及合并页注段`chp-14:14_CHP-14_intro:l168-220`。正文来源为`14_CHP-14_intro.md`，并对照`CHP-14.pdf`物理页1。该扫描是第十四章开篇；物理页2明确印刷页348，结合目录中的起始页347确认物理页1对应印刷页347。整章OCR副本不纳入S0覆盖，不重复计数。

本批新增18个来源候选（`cand-10222`–`cand-10239`）、86条精确提及和12条原书statement。正文记录Haskell对Algarotti在威尼斯赞助史位置的评价，以及个人收藏、Dresden王家画廊委托、Tiepolo/Canaletto联系之间的比较；将“资产阶级而亲近贵族”“启蒙观念与旧秩序”“威尼斯爱国者而少居威尼斯”等作为作者概括，未转写为外部验证事实。保留Algarotti出生/教育、父亲未具名、与Manfredi通信、集体指称“Zanotti brothers”、Bonomo的兄长身份与影响评价。Algarotti个人绘画收藏与其和Bonomo的共同收藏分立为两个类型待决候选；Dresden王家画廊先与既有`cand-9091`分开，交S3裁决身份。

印本校读只记录在S2，S0 OCR不改：物理页1确认L6 `T has`→`It has`、L7 `Ieighteenth`→`eighteenth`、L9 `Plate 486`→`Plate 48d`、L9 `Use`→`life`。L12“80-99. Other references are noticed as they occur.”属于注1末尾，已与合并注释L169双向连接；注1涉及Michelessi、Palese、Farsetti、Treat、Gabrielli与Lepre的文献均仅按Haskell书内引注登记，未独立查阅。注2的Bosdari 1928页157–222也只登记为书内书目定位。正文注1标记后的商人/出生描述与注释书目不构成直接证据关系；注2回链至Bologna及关系叙述。

L11末句停在“it was Bonomo”，由印刷页348及S0段`l14-21`续接，故正文段保持`reviewed/partial`；该段行12是注释续文而非正文。合并页注段仅处理印刷页347注1–2，其余注释从L171起待后续按页处理，故同样保持partial。文件标题段`l1-1`已按生成式文件名排除。受控脚本`chp14_p347_s2_migration.py`默认dry-run，锁定来源/PDF SHA，核验覆盖前态、18个候选ID、精确mention跨度、statement原句与外键；写回前为四表保存`.bak-s2-chp14-p347-20261003`。

写回后`python -X utf8 scripts/audit_tables.py --summary`报告`s2_missing=[]`、`errors=[]`；830段中499 complete、109 excluded、220 queued、2 partial；候选10,226、提及22,246、statement 9,890。两条既存enrichment `source_ref`警告不变；审计另提示220段queued及2个partial段尚未完全迁移。下一源段为第十四章p.348正文`l14-21`。


## 第十四章p.348正文及注1–3（2026-10-03）

对照`CHP-14.pdf`物理页2（印刷页348），处理规范段`chp-14:14_CHP-14_intro:l14-21`及合并注释L171–173。新增14个来源候选、110条初始精确提及和19条statement；结构审计发现4个同一代词被映射到两个Algarotti索引候选后，删除4条重复mention，最终新增106条提及。候选覆盖Cellini《Perseus》、佛罗伦萨洗礼堂门、Raphael两件未定版本绘画、提香画作组及Grand Ducal收藏类型待决对象；Prussia按地域候选记录。新罗马学者群体候选保持无类型，不改写成正式学院。

正文闭合p.347 L11的“it was Bonomo”句，记录Bonomo协助实施Francesco计划并向其通报意大利社交/艺术消息。其余内容包括Algarotti在Veneto的行程与早期艺术趣味、对Palladio的欣赏及扩散、1733年佛罗伦萨观画、1734年罗马行程、古迹与绘画判断、Baroque艺术/文学对照，以及他与Bottari的交往和同期学者关系。Haskell的评价与Algarotti书信转述分层保存。L21末尾“less than”续至p.349 L23，故p.348正文保持partial。

p.348印刷注1–3依标记链接到正文：F. M. Zanotti 1732–1734年书信与`Opere`卷XI/XII；1734-02-22致Bonomo信及`Treviso, Archivio Comunale, MSS.1256`；1734年2–6月致F. M./Eustachio Zanotti、Antonio Conti的罗马书信及`Opere`卷X/XII。引文和手稿均未独立查阅。上述`Opere`短引定位与p.347所述十七卷本候选分立，留S3/书目审查，不提前合并。页图校读仅记S2、不改S0：L15 `helped, to`→`helped to`；L16 `passionate, enthusiasm`→`passionate enthusiasm`；L17 `‘1 go`→`‘I go`、`Up service`→`lip service`、`Prussia.-Towards`→`Prussia. Towards`；L21 `artists.and collectors`→`artists and collectors`。

受控脚本`chp14_p348_s2_migration.py`默认dry-run，核对源文件/PDF哈希、段落前态、候选ID、mention跨度、statement引文/外键与marker回链；四表备份为`.bak-s2-chp14-p348-20261003`。首次写回审计发现同一p.348 L17 Algarotti代词同时映射至`cand-0061`和`cand-0050`；保留与Palladian建筑子目一致的`cand-0050`锚点，移除4条重复跨度，并将修复记录为`chp14_p348_overlap_repair.py`，备份`.bak-s2-chp14-p348-overlap-fix-20261003`。S3仍负责全局候选身份合并。

修复后`python -X utf8 scripts/audit_tables.py --summary`通过：`s2_missing=[]`、`errors=[]`；830段为500 complete、109 excluded、219 queued、2 partial；候选10,240、提及22,352、statement 9,909。两条既存enrichment `source_ref`警告不变；审计仍提示219段queued和两个partial段。p.347正文现complete，注释段覆盖L169–173并保持partial。下一源段为p.349 `chp-14:14_CHP-14_intro:l23-33`。

## 第十四章p.349正文及注1–4（2026-10-03）

对照`CHP-14.pdf`物理页3处理正文`chp-14:14_CHP-14_intro:l23-33`及合并注释段L174–177。印本确认本页接续p.348 L21，闭合“less than a year”；p.349末句在L33逗号处继续至p.350 L35。正文新增10个候选（`cand-10254`–`cand-10263`）、100条提及和27条原书statement。Algarotti在Paris会见Pierre Crozat、Maupertuis与Voltaire，并与Voltaire同住Cirey；其后在Paris/London的社交叙述分别保留Lord Hervey与Lady Mary Wortley Montagu候选。Newtonianismo per le Dame作为文献独立登记，旅行与出版时间、在Frederick the Great宫廷及为Augustus Elector of Saxony工作、威尼斯购画、1753–1756返威尼斯、1760短访与1764年去世等按原书限定记录。“the King”依同段上下文及索引候选指向Augustus III，但仍作为候选关系留待S3/S6，不直接生成正式边。Haskell关于Tiepolo与Canaletto都在三次返威期间工作的概括，与其后书信/理论著作影响评论环境的判断分开记录。

保留脚注/关系候选链：p.349注1为Algarotti致Bonomo的巴黎书信集合及Treviso引文；注2仅为Halsband姓氏，无题名/页码；注3为Albrizzi所引`Novelle della Repubblica delle Lettere` 1758-04-12期及其意大利文警示；注4为G. P. Zanotti 1735-02-12书信及`Opere` XI, p.213。所引书信、期刊、出版物均未独立查阅。注4对应正文“仅间接得知Algarotti与Crozat会面”的证据限定；其日期不是OCR中的1733，而是印本扫描可见的1735。

页图校读只写入S2 qualifiers、不改S0：L24 `lest`→`left`；L28 `alfògether`→`altogether`；L32 `1743-5!`→`1743-5;`；L33 `die ancient monuments`→`the ancient monuments`及`ofhis`→`of his`；L177 `12 February 1733`→印本`12 February 1735`。其余印本用词（包括OCR的`payed`）未见足够差异依据，不擅改。

受控脚本`chp14_p349_s2_migration.py`默认dry-run，核验来源/PDF SHA、表前态、10个候选ID、100条精确mention跨度、statement引句/外键及页注覆盖；应用前四表备份后缀`.bak-s2-chp14-p349-20261003`。首次apply的coverage写回调用遗漏字段参数，前三表虽已临时写入但coverage未写；随即从四表备份恢复一致前态、修正参数并重跑，未保留半批次数据。写回后`python -X utf8 scripts/audit_tables.py --summary`：`s2_missing=[]`、`errors=[]`；830段为501 complete、109 excluded、218 queued、2 partial；候选10,250、提及22,452、statement 9,936。两条既存enrichment `source_ref`警告不变。p.348正文转complete；p.349正文与合并注释段仍partial，注释覆盖推进至L177。下一源段为p.350正文`chp-14:14_CHP-14_intro:l35-44`。

## 第十四章p.350正文及注1–3（2026-10-03）

对照`CHP-14.pdf`物理页4处理正文`chp-14:14_CHP-14_intro:l35-44`及合并注释L178–179。新增7个候选（cand-10264–cand-10270）、68条提及和18条原书statement。闭合p.349末句；记录Algarotti 1741年柏林肖像书信、1737年威尼斯期间“没有证据显示有特别接触在世艺术家”的限定、1742年起在国际艺术界的重要性，以及Dresden王家画廊方案的历史陈列观和委托在世艺术家设想。保留Haskell的历史解释和计划语气，不将“无证据”改写成确定的未接触，不把未具名受委托对象变成已知艺术家或已完成作品。印本注1–3分别回链至Bonomo书信、`Opere`卷VIII页351–388、Lodoli收藏的第12章交叉引用；相关手稿/引文未独立查阅，Lodoli收藏维持无类型候选。校读在qualifiers记录`173 7`→`1737`、`Vin`→`VIII`，不改S0。

脚本`chp14_p350_s2_migration.py`锁定来源/PDF SHA，默认dry-run；应用前为四表保存`.bak-s2-chp14-p350-20261003`。写回后`python -X utf8 scripts/audit_tables.py --summary`报告830段中502 complete、109 excluded、217 queued、2 partial；候选10,257、提及22,520、statement 9,954；`s2_missing=[]`、`errors=[]`。两条既存enrichment `source_ref`警告仍在。p.349正文转complete；p.350正文和合并注释段保持partial，注释覆盖至L179。下一源段为p.351正文`chp-14:14_CHP-14_intro:l46-53`。

## 第十四章p.351正文及注1–2（2026-10-03）

对照`CHP-14.pdf`物理页5处理正文`chp-14:14_CHP-14_intro:l46-53`及合并注释L180–181。新增8个候选（cand-10271–cand-10278）、67条提及和23条原书statement。p.351 L47闭合p.350 L44的“基于何者”未完句，记录Algarotti以风格为题材选择依据；逐项保留Piazzetta、Pittoni、Tiepolo的引述评价、历史画家类别、Zuccarelli题材提议、Pannini题材要求、Canaletto在该名单中的遗漏、Boucher等人与意大利画家的罕见合作，以及不同城市/区域的艺术家名单。Haskell称Algarotti有特殊敏感度，但影响力难以估量；其关于旅居、二手消息和国外收藏的依据仍以推断语气记录。Crespi后获特别赞扬回链注1；五位艺术家的画作据称已完成但全部遗失，回链注2，未臆造单幅题名。`pittore di macchia`与`soggetti graziosi e leggeri`保留为术语候选；题材《The Hunt of Meleager and Atalanta》保持“例如/提议”状态，另将五幅作品组与单一题材分立。页注出处只据Haskell登记，未独立查阅；印本校读记录`Piazzctta`→`Piazzetta`、`2nd`→`and`、`soggetti.`删除句点、`Ercole Lefli`→`Ercole Lelli`、`after.he`→`after he`、`modem`→`modern`、`HI`→`III`、`VW`→`VIII`，不改S0。

受控脚本`chp14_p351_s2_migration.py`默认dry-run，核验来源/PDF SHA、段落前态、8个候选、67条精确提及、23条原句及外键；应用前四表备份后缀`.bak-s2-chp14-p351-20261003`。全表审计报告830段中503 complete、109 excluded、216 queued、2 partial；候选10,265、提及22,587、statement 9,977；`s2_missing=[]`、`errors=[]`。两条既存enrichment `source_ref`警告仍在；p.350正文转complete，p.351正文与合并页注段仍partial。下一源段为p.352正文`chp-14:14_CHP-14_intro:l55-61`。

## 第十四章p.352正文及注1–3（2026-10-03）

按`CHP-14.pdf`物理页6处理正文`chp-14:14_CHP-14_intro:l55-61`及注释L182–184。受控脚本`chp14_p352_s2_migration.py`默认dry-run，按来源/PDF SHA与coverage前态预检，首次写入5个候选、76条提及和21条statement，并为四表保存`.bak-s2-chp14-p352-20261003`。首轮全表审计发现三处Algarotti同字符区间被索引候选重复占用；依据页内语境，将涉及Count Brühl的明确提及留给`cand-0045`，其余映射至相应人物候选，脚本修订后用`chp14_p352_mentions_overlap_repair.py`删除3条重复记录并备份mentions表。另核对到Morassi 1955著作及作者已由`cand-8258`和`cand-8257`登记，故以`chp14_p352_reuse_bibliography_candidate.py`撤销重复候选`cand-10282`并复用既有端点。净增4个候选、73条提及和21条statement。p.351 L53未完句由p.352 L56闭合，p.351正文转complete；p.352 L61比较句续至p.353 L63，故p.352正文保持partial。图版61a（Cognacq-Jay小稿）与61b（Melbourne大幅）按图版清单分别映射；与跨章`cand-9162`的潜在身份问题保留给S3，不合并。注1–3分别记Levey/Haskell关于作品史、Morassi所称既有友谊与Haskell的证据限定、Tiepolo 1743年致Algarotti信的出版定位；未独立查阅被引作品/信件。印本校读只记S2、不改S0：`1757?`→`1737`及注2标记、`Cognacq-‘Jay`→`Cognacq-Jay`、`fight`→`light`、`theatrical;her`→`theatrical; her`。全表审计`s2_missing=[]`、`errors=[]`；830段为504 complete、109 excluded、215 queued、2 partial；候选10,269、提及22,660、statement 9,998。两条既存`source_ref`警告不变；下一源段为p.353正文`chp-14:14_CHP-14_intro:l63-71`。

## 第十四章p.353正文及注1（2026-10-03）

对照`CHP-14.pdf`物理页7处理正文`chp-14:14_CHP-14_intro:l63-71`，并把注释覆盖推进至L185。正文净增15个候选（`cand-10284`–`cand-10298`）、74条提及和24条原书statement；候选包括Mark Antony、Pompeii、Herculaneum、Isis、Serapis、pictorial scholarship、Roman school、Banquet原modello版画、Algarotti致Brühl的未定年书信、Brühl宅园/喷泉图像母题及注释书目定位。L64闭合p.352比较句，L71末尾“As in The”续至p.354 L74，故p.353正文和后续合并页注段仍为partial。

记录完成版Banquet的古典构图、细节改动、Algarotti对建筑真实感/历史准确性/透视/宏伟感及“pictorial scholarship”的评价、Tiepolo与Poussin及Veronese的比较、国王偏好旧大师、委托给Brühl的两项法国描述性题材。保留Haskell对Algarotti动机和创作影响的解释层级；不把未证实的安装状态、正式作品题名或两种装饰母题与两幅作品逐一配对写成事实。p.353注1报告Maecenas画作在Hermitage、Flora画作在De Young Memorial Museum（San Francisco），并引用Levey 1957年Burlington Magazine pp.89–91；“Leonardis版Maecenas版画/Plate 68b”与正文所述Banquet原modello版画分开。引文、信件和Levey论文均未独立查阅。

印本校读只记S2、不改S0：L65删除OCR残片`-..`，L66 `parellel`→`parallel`，L68 `may ell`→`may well`，L69 `whichdie`→`which he`及Brühl姓名校读；注1人名/机构拼写亦按页图记校。首轮表审计发现委托Maecenas statement引文跨L69–70但范围只标L69，已将`source_line_end`修至70。候选表面提示还发现L65 `canvas`与L66 `Europe`两处应连既有类型候选，追加精确提及；本次覆盖范围内无其余未覆盖候选名提示，注释段L192之后的提示属于尚未审阅内容。

迁移脚本`chp14_p353_s2_migration.py`默认dry-run，核验来源/PDF SHA、段落前态、候选ID、精确锚点、引文和外键；初始四表备份后缀`.bak-s2-chp14-p353-20261003`。引文范围与候选表面修复分别由`chp14_p353_quote_span_repair.py`、`chp14_p353_surface_repair.py`在dry-run和备份保护后应用。最终全表审计`s2_missing=[]`、`errors=[]`；830段为505 complete、109 excluded、214 queued、2 partial；候选10,284、提及22,734、statement 10,022。两条既存enrichment `source_ref`警告不变。下一源段为p.354正文`chp-14:14_CHP-14_intro:l73-83`。

## 第十四章p.354正文及注1–5（2026-10-03）

对照`CHP-14.pdf`物理页8处理正文`chp-14:14_CHP-14_intro:l73-83`，并把合并注释覆盖推进至L190。新增8个候选（`cand-10299`–`cand-10306`）、71条提及和27条statement。L74闭合p.353的“As in The Banquet of Cleopatra”；p.354 L83末句继续至p.355，故p.354正文保持partial。p.353正文转complete，页注合并段仍partial。

记录Algarotti对Banquet构图古典性/准确性的强调、为本人委托Tiepolo创作《Bath of Diana》、Boucher风格与巴黎时尚的比较、作品反映的公共/私人趣味、Newton光学观念传播及其对色彩的讨论。Algarotti与Tiepolo相互影响、调亮调色板、早期1740年代古典阶段等均保留Haskell的判断/推测层级。独立登记Algarotti为自娱创作的东方人物素描/蚀刻作品组，不与索引中Tiepolo在p.260注释所涉东方人物素描候选`cand-2586`合并。注1–5分别记录Knox页码、Levey期刊定位、Saggio/1756年致Eustachio Zanotti信/Watson引文、Rava定位及《Saggio sopra l’Accademia di Francia che è in Roma》；均未独立查阅。注3另将Haskell转述信中“白底构想刚刚出现”的内容单列断言，保留“implies”限定。

印本校读只记S2、不改S0：L80 `newscientific`→`new scientific`，L81 `beenagreed`→`been agreed`；注2 `Migazine`→`Magazine`、`i960`→`1960`；注3 `in-21`→`111-21`、`VIH`→`VIII`；注5 `AccaJemia`→`Accademia`、`HI`→`III`。`Saxony`按地理区域记place，和政治实体候选`cand-10256`分开；未确定的作品题名、版本、接收/安置和色彩观念影响范围不外推。

迁移脚本`chp14_p354_s2_migration.py`默认dry-run，校验来源/PDF SHA、coverage前态、候选ID、精确锚点、断言原文、外键及mention不重叠；四表备份为`.bak-s2-chp14-p354-20261003`。后续补充断言使用`chp14_p354_note3_white_ground_repair.py`，另备份statement表。候选表面提示在本次覆盖范围内无剩余未覆盖名称。最终全表审计`s2_missing=[]`、`errors=[]`；830段为506 complete、109 excluded、213 queued、2 partial；候选10,292、提及22,805、statement 10,049。仍有两条既存enrichment `source_ref`警告。下一源段为p.355正文`chp-14:14_CHP-14_intro:l85-95`。


## 第十四章p.355正文及注1–3（2026-10-03）

对照`CHP-14.pdf`物理页9处理正文`chp-14:14_CHP-14_intro:l85-95`及注1–3（L191–193）。新增20个候选（`cand-10307`–`cand-10322`、`cand-10324`–`cand-10327`）、87条提及和27条原书statement。p.355 L86闭合p.354 L83“neo-classical correctness”，p.354正文转complete；p.355 L95末句止于“still intensively”，续至p.356，故p.355正文仍partial。注释总段推进至L193、仍partial。

记录Algarotti的威尼斯文化认同与国际主义处境、其试图调和Tiepolo幻想与新古典规范的矛盾、Piazzetta受Algarotti委托为Augustus绘制《Caesar and the Corsairs of Cilicia》、该画与两幅后续古典题材画的关系、Newtonianismo首版扉页、家族绘画收藏的形成/扩充与规模、寄往Dresden的画作/草图复制品，以及Tiepolo在藏品中的约13幅绘画和116幅素描。单独登记未具名画作组、委托事件、具体作品和收藏对象；p.355失传委托不自动等同p.351五幅作品组，家族收藏不自动等同p.347个人/共同收藏。p.355 note 2列出两处作品地点但未明确分别对应，故不作逐件地点配对；Haskell“没有证据”Algarotti接触Canaletto的判断保留原有限定，不写成未接触的确定事实。

页注1–3均回链：Michelessi/`Opere`定位复用既有候选；Pallucchini 1956页41保留为未核引文；Selva书目保持未识别，Levey 1960论文复用p.354同一候选。页图校读记于S2、不改S0：note 1 `Ixii`→`lxii`，note 3 `i960`→`1960`；被引资料未独立查阅。迁移脚本`chp14_p355_s2_migration.py`默认dry-run并锁定来源/PDF SHA，四表备份后缀`.bak-s2-chp14-p355-20261003`。写回后审计`s2_missing=[]`、`errors=[]`；830段为507 complete、109 excluded、212 queued、2 partial；候选10,312、提及22,892、statement 10,076。两条既存enrichment `source_ref`警告不变。下一源段为p.356正文`chp-14:14_CHP-14_intro:l97-107`。

## 第十四章p.356正文及注1–7（2026-10-03）

对照`CHP-14.pdf`物理页10处理正文段`chp-14:14_CHP-14_intro:l97-105`及合并页注L194–200。新增24个候选（`cand-10328`–`cand-10351`）、72条提及和27条原书statement；并闭合p.355正文L95的跨页句，使p.355正文段转为complete。新迁移包含未具名作品、委托事件、信件及引文定位，不将候选视为身份对齐或事实独立核验。

逐行语义处理：L98闭合“Canaletto … still intensively employed by Consul Smith”，并转述Bonomo早前称Canaletto因委托繁多而数年方能完成绘画。注1给出1740/1年1月28日书信和意大利文，记录价格较高、工期数年；`farli`所指画作不明，未与p.355或p.351任何作品组相连。L99–100记1746年离开意大利、此前在威尼斯约两年半且有短暂离开、1753年才返回；先到Dresden，继而去Berlin，之后七年大部分时间往返/居于Berlin与Potsdam之间，保留原文“most of”的近似限定。L100–101记录其为Frederick the Great及宫廷提供艺术建议，并称他们有把Berlin建成艺术中心的宏图；作为计划表述，不写成已建成机构。L101–102记录其海外推广意大利、尤其威尼斯艺术的多重动机与爱国理由，以及经Algarotti促成Giovanni Marchiori为Berlin一所未具名教堂制作雕像的委托；作品数量、题材、教堂身份和是否完成均未知。对Bonomo的“for the honour of Italy”及“hors de Paris point de salut”引语仍标记为Haskell转引，未假作直接核阅原信。L102记录其鼓励外国艺术家赴意大利、分别为Bouchardon与Rode提供介绍信，并把两封收信人可辨的介绍信分立登记；Rode受Tiepolo影响保留Haskell的将来时预测，不改为已核事实。另记Haskell关于Algarotti凭成功行动提升声望、给有影响者送贵重礼物、财务获利和追踪威尼斯市场的评价。1738年拟为Walpole取得一幅Veronese的计划按未识别作品记录；注4信中条件为价格适中，不能证明购买或交付。1764年遗嘱给William Pitt the Elder两幅未识别画作，与Algarotti早先赠Walpole的设想分开；Diderot评论通过Treat第209页转引，保留二手引文链。注6仅说明1742年12月书信线索。`their collection`指代未裁定，不合并p.347个人/共同收藏与p.355家族收藏；为海外出售挑选的作品也不与p.355寄往Dresden的画布自动等同。L103的混合动机总结保持为Haskell解释。L104–105记Algarotti在England接触neo-Palladianism后，尝试搜集材料说服Frederick；请求Lord Burlington位于Chiswick住宅的plans及Palladio原始图稿，但不推断材料已取得。L105末句“asking them to supply”未闭合，留待p.357，不补猜其索要对象。

页注分别处理：L194 Bonomo信件与Canaletto高价/工期；L195列1749年4封信；L196列1750及1752年2封信；L197列Carcassonne来信及条件性Veronese赠礼；L198记录Treat p.209的Diderot法文引文；L199指向Treviso MSS.1256中的1742年12月信件；L200列致Frederick的1751年两封信及`Opere` XV页153–155。除书内引文和书目定位外，均未独立检查所引原信或著作。

印本对照仅在S2记录、不改写S0：正文L100 `thistime`→`this time`、L101 `commision`→`commission`；注L194 `T1`→`Il`、`pretcnderebbe`→`pretenderebbe`；L197 `fame`→`farne`、`facilitate`→`facilitare`、`1’esecuzione`→`l’esecuzione`；L200 `Opéré`→`Opere`。迁移脚本`chp14_p356_s2_migration.py`默认dry-run，锁定Markdown/PDF SHA并验证coverage前态、唯一ID、提及锚点、重叠、statement原文及脚注回链；四表恢复点后缀为`.bak-s2-chp14-p356-20261003`。写回后全表审计`s2_missing=[]`、`errors=[]`；830段为508 complete、109 excluded、211 queued、2 partial；候选10,336、提及22,964、statement 10,103。保留两条既存enrichment `source_ref`警告及211条queued提示。下一源段为p.357正文`chp-14:14_CHP-14_intro:l107-116`。



## 第十四章p.357正文及注1–8（2026-10-03）

对照`CHP-14.pdf`物理页11处理正文段`chp-14:14_CHP-14_intro:l107-116`和合并页注段L201–207；注4实际位于正文文件L116。新增28个候选（`cand-10352`–`cand-10379`）、75条提及和24条原书statement，并闭合p.356 L105“asking them to supply”跨页句，使p.356正文coverage转为complete。p.357正文L115止于“with their description of”，续至p.358 L120；正文段和合并页注段均保持partial。

逐行处理：L108记录Algarotti继续委托绘画、转向以Rome而非Venice作为Frederick的艺术范本，以及向意大利熟人征求Genoa建筑版画；此处闭合p.356的未完句。L109记录Batoni《Triumph of Venice》曾见于Marco Foscarini的未具名宫邸，并将为King创作、可转为马赛克的Cleopatra保留为提议，不写成已完成作品。L109–110分别记录Algarotti为自己委托Pannini绘制《Interior of the Pantheon》及要求Bonomo暂存；房间归属和是否展出未决。L111–112记录Algarotti在Mead藏品中见过Pannini作品，及对其色彩和室内画能力的评价；脚注标记按印本校为5。L113记录1753年末离开Germany、次年初抵Venice、其官方职位变化、可能持续收藏、首次观看并取得Tiepolo Contarini别墅壁画的modello，以及晚期转向建筑画和Canaletto委托。模型与壁画分立；Canaletto视图与Rialto既有候选`cand-9243`的身份关系保留待S3。L113–115记录拟议视图中的Rialto、Palazzo Chiericati和Vicenza Palazzo della Ragione，Roman architectural capricci，以及Smith早前计划中的Palladio Rialto方案；拟议构图不视作已经完成。L115的理论委托句只记录到当前页原文，不推断p.358续文。

注1–8分别登记Curli书信及Neri出版线索、Scarselli 1748年信、1751年Potsdam信、Bonomo 1750年信、1750年Berlin信与Lazzarini作品/文稿来源链、Tiepolo壁画年代参考、Pesci书信及Parma版本说明、Chapter 11交叉引用。注5中Haskell所引Fantuzzi称两幅作品出自Andrea Lazzarini且原为Frederick制作；后续书信与Algarotti库存目录被转述为支持作品属于Algarotti，而索引将题名列在Gregorio Lazzarini名下。人物与作品归属冲突保持未决，不合并候选。所引书信、库存和论文未独立查阅。

印本校读仅记于S2、不改S0：L108 `him. with`→`him with`并校正Genoa处注号标点；L112注号OCR `6`→印本5；L113 `os France`→`of France`、`his Use`→`his life`，并补录OCR漏掉的注7标记；L205 `i960`→`1960`；L206 `VHI`→`VIII`。脚本`chp14_p357_s2_migration.py`默认dry-run，锁定来源/PDF SHA，核对coverage、唯一ID、精确锚点、非重叠提及、statement原文和脚注链接；修正上下文保护条件、移除与既有Grand Canal/Palladio提及重叠的整句锚点，并将Curli日期锚点移入合并页注段。四表恢复备份后缀为`.bak-s2-chp14-p357-20261003`。应用后审计`s2_missing=[]`、`errors=[]`；830段为509 complete、109 excluded、210 queued、2 partial；候选10,364、提及23,039、book statements 10,127。两条既存enrichment `source_ref`警告仍在。下一源段为p.358正文`chp-14:14_CHP-14_intro:l118-124`；全书S2尚未满足S3交接条件。


## 第十四章p.358正文及注1–6（2026-10-04）

对照`CHP-14.pdf`物理页12处理正文段`chp-14:14_CHP-14_intro:l118-124`及合并页注L208–213。新增17个候选（`cand-10380`–`cand-10396`）、52条提及和36条原书statement；闭合p.357 L115理论方案句，p.357正文coverage转为complete。p.358 L124仍以逗号续至p.359 L127，故p.358正文保持partial；合并页注段已迁移至L213，后续页注仍未处理。

逐行语义处理：L119–120延续p.357 Canaletto视图的说明：书信被刊行后，Algarotti被认为对这一类型绘画负有创始责任；该句只记录“观念逐渐形成”的接受史，不确认为Algarotti发明了体裁。指称的“this type of painting”与前文architectural capricci及特定Canaletto视图的边界留待后续判定。Haskell以Algarotti对Palladian architecture的解释说明其艺术观，并将其称为“frivolous”且不同于Winckelmann所代表的新古典改革激情；再记其认为过度规整不可取、Strada Balbi与Strada Nuova不如罗马Corso或威尼斯Grand Canal“picturesque”。这些比较保留为作者报告的审美判断，不做城市空间的客观评价。L120–121记Algarotti于1741年在Berlin雇用一位久居当地但未具名的Flemish artist；转述其画面执行带意大利式dash/brio、由Algarotti选题，包括古城遗址、渡槽、桥梁和其他建筑，以及罗马装束的人物与士兵。作品组未具题名、数量和现存地点。

L121记Algarotti回到意大利后晚年继续创作建筑幻想画，并关注画中古典建筑结构；1756年移居Bologna后结识Prospero Pesci与Mauro Tesi，并雇用二人为其构想绘画，常令二人依其草图创作。分开保留Pesci、Tesi两条委托及草图关系候选。画面原则为以真实或重建的古典建筑为主体、以幻想背景衬托其精确性；他利用考古书籍指导细节，并反复强调picturesque因素。其私人考古书库没有书名或目录，暂留类型未定，不强归archive或institution。L122保留致Pesci信中的作曲家/Caffariello咏叹调类比，以及对音调流转、变化和艺术魅力的指示；引文层级仍是Haskell转引。L122–123记录建议研究Teniers、Wouwermans、Vernet和Pannini，及把Italian draughtsmanship与Flemish taste/flavour结合的美学目标。L123记Haskell将这种教诲性与picturesque并置比作Algarotti所欣赏的Piranesi创作。L124只记录其意识到Tesi与Pesci这类建筑画家所能提供的picturesque invention有限，后续补偿方式待p.359续文处理。

注1为Blainville卷I页492对该“mixture”的反应；“mixture”具体所指不越出当前上下文，被引页未独立查阅。注2标出1741年9月5日Berlin来信及Treviso MSS.1256，并转录意大利文；手稿和译文未独立核阅，注中未指明保管机构，未在Biblioteca Comunale与Archivio Comunale候选间择一。注3列Opere中多封书信、Bologna Biblioteca Comunale的MSS. Hercolani 207，以及《Raccolta di disegni originali di Mauro Tesi》导言；均为Haskell指引，未独立查看。注4 Opere VIII p.95与注5 p.100回链到p.357 n.7所引Pesci书信候选`cand-10375`；仅据页码范围关系复用，不声称已查原信。注6 Opere VIII pp.104、109、111支持Piranesi比较，出版物及页码未独立核阅。

索引候选`cand-1887`（Pesci, Prospero）适用于本页；p.357迁移另曾新增同名来源候选`cand-10374`。两条先保留，交S3核对候选自然键及身份，不在S2直接合并。印本校读只记于S2、不改S0：L123 `ofltalian`→`of Italian`；L211 `VIH`→`VIII`；L212 `roo`→`100`；L213 `in`→`111`。脚本`chp14_p358_s2_migration.py`默认dry-run，锁定来源/PDF SHA并校验前态、唯一ID、锚点、候选覆盖、断言与脚注回链；p.357既有statement跨页收口，四表备份后缀为`.bak-s2-chp14-p358-20261003`。应用后审计`s2_missing=[]`、`errors=[]`；830段为510 complete、109 excluded、209 queued、2 partial；候选10,381、提及23,091、book statements 10,163。另保留两条既存enrichment `source_ref`警告。下一源段为p.359正文`chp-14:14_CHP-14_intro:l126-137`；全书S2尚未达到S3交接条件。

## 第十四章p.359正文及注1–4（2026-10-04）

对照`CHP-14.pdf`物理页13处理正文段`chp-14:14_CHP-14_intro:l126-137`及合并页注L214–217。新增18个候选（`cand-10397`–`cand-10414`）、49条提及和24条原书statement；p.358 L124的未完句由p.359 L127闭合，p.358正文coverage转为complete。p.359 L137止于“in a”，续至p.360 L140；注1–4已记录至L217。后续对照页图后确认p.359注4的正文标记在L127–137未定位；p.360 L145的注4是独立的Leslie注，不能与Gabbrielli注合并。p.359注4保留为未决孤立注号审计项。

逐行语义处理：L127记录Algarotti请其偏爱的Tiepolo为其他建筑画家的背景加入人物，作为对Tesi/Pesci建筑画效果限制的补充；请求不等同于每项均已完成。L127–128保留Haskell对古典框架限制Tiepolo幻想、同时增加生命与变化的说明。L128记录经Haskell转引的Algarotti书信：Tiepolo为Pesci干涩的建筑背景增加源自Titian的风景，以及“配得上Wouwermans”的船与白马；转引中的艺术家比较不改写为作者归属。L129–131记录Algarotti晚年给Tiepolo的委托主要是建筑画中补人物和仿Veronese的复制画；他已无从前服务于有雄心赞助人时订制大画的条件；Tiepolo因需求过多且被迫前往Spain而无法完成这些要求，Algarotti日益病弱后几乎全靠Mauro Tesi。L132–134记录Algarotti与Tesi及其未具名妻子关系“极亲密”、为其未具名女儿担任教父、携Tesi游历Central Italy复制自己欣赏的作品、雇用Tesi复制Dietrich风景并为筹备中的文集刻制小插图，以及1764年召Tesi为Pisa中他临终所居的房间作装饰。匿名妻女只保留来源内描述；不推断亲密关系的具体性质，也不补身份或作品题名。筹备中文集与已登记的后出十七卷本（`cand-10229`）保持分立，待后续身份/版本核对。

L135–136记录Algarotti晚年理论著作及Haskell的评价：著作对其书信、委托和计划中的非正式观点增益有限，延续其矛盾，却使他成为对艺术家更有同情心且有帮助的批评者；他“稍进一步”趋向neo-classicism，主张素描高于色彩、学习Greek sculpture、理想主义艺术理论和严格价值层级，同时谨慎限定理论命题，指出过多雕塑研究“可能”导致枯燥、过度严峻有害。L137记录Haskell所述每项委托要求调和Roman/Venetian、learned/fantastic、classical/picturesque风格，以及Algarotti持续追求两种新近开始冲突的风格综合；句末续至p.360，暂不把残句独立作完整断言。关系仅登记为书内候选，不创建正式关系边。

注1记Baudi di Vesme 1912年页309–329定位；注2记`Opere` VIII页101；注3、4均指Annamaria Gabbrielli 1938与1939年的一般讨论。重复引文不合并为同一条脚注记录。以上书目、原始书信和被引著作均未独立查阅。页图校读只记录在S2、不修改S0：L128删除误识的句首点并将`Use`校为`life`；L129 `confmed`→`confined`；L131 `himselff`→`himself`；L137 `picturesque.-He`依印本校为`picturesque.—He`；注2 L215 `Opéré`→印本`Opere`。复核页图后未在p.359 L127–137定位注4正文标记；p.360 L145注4对应C. R. Leslie《Memoirs》，与本条Gabbrielli注分立。该孤立标记保留待全书S2交接审计，不删除、不误链。

索引候选`cand-1887`（Pesci, Prospero）用于本页；p.357来源候选`cand-10374`同名问题仍保留到S3核对。Dietrich在正文只出现姓氏，新增来源形式候选`cand-10405`，不在S2与索引候选`cand-0920`合并；新建的Gabbrielli、未具名妻女、作品组及引文候选均保留描述边界。脚本`chp14_p359_s2_migration.py`默认dry-run，锁定来源/PDF SHA，检查coverage前态、ID序列、精确锚点、非重叠提及和新候选覆盖；写回四表的备份后缀为`.bak-s2-chp14-p359-20261004`。写回后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；830段中511 complete、109 excluded、208 queued、2 partial，候选10,399、提及23,140、statement 10,187。两条既存enrichment `source_ref`警告仍在。下一源段为p.360正文`chp-14:14_CHP-14_intro:l139-146`；全书S2尚未达到S3交接条件。

## 第十四章p.360正文及注1–4（2026-10-04）

对照`CHP-14.pdf`物理页14完成正文`chp-14:14_CHP-14_intro:l139-146`，并将合并页注段L218–220补齐。新增8个候选（`cand-10415`–`cand-10422`）、39条精确提及和22条原书statement；闭合p.359 L137跨页句，使p.359与p.360正文complete。L140–141保留Algarotti对较早传统的认同、Tiepolo被视为理想画家、Algarotti转述Tiepolo敬古及其鼓励Tesi绘画性的一组分别断言；L142–145记录Haskell对Algarotti早期新古典代表性、摇摆态度、取悦倾向、性趣味、承诺困难、写作“松软”评价及Constable阅读的转述层级；L143 OCR连字符与L146拉丁文拼写校读记于statement qualifiers，不改S0。注1拆录Zanetti 1743/1885及Patriarchi 1758/Melchiori p.22；注2分别记录Halsband引述线索与Biffi关于Cecilia Emo的引文，并回链p.328注5但不推定同一手稿；注3 Paciaudi信件保留作者未知，OCR注号8校读为印本3；注4 Leslie书目回链Constable断言。L146将Frederick纪念Algarotti与Horace铭文分开记录；Plate 60只回链既有图版目录题注，不把Volpato版画等同实体纪念碑。

页图复核确认p.359注4正文标记在L127–137未定位；p.360 L145的注4是独立Leslie引文。因此p.359 Gabbrielli注4列为孤立注号审计项，不与p.360注4混并。受控脚本`chp14_p360_s2_migration.py`默认dry-run，锁定来源/PDF SHA，检查coverage前态、候选序列、锚点及精确提及；四表备份后缀`.bak-s2-chp14-p360-20261004`。首次审计指出闭合statement超出p.360 coverage起始行；将定位修正为L140并备份statement表`.bak-s2-chp14-p360-lineanchor-20261004`后复审通过：830段中514 complete、109 excluded、207 queued、0 partial；候选10,407、提及23,179、statement 10,209；`s2_missing=[]`、`errors=[]`。两条既存enrichment `source_ref`警告仍在；全书S2仍未达到S3交接条件。下一源段为p.361正文`chp-14:14_CHP-14_intro:l148-149`。

## 第十四章图版61–64及图像题注（2026-10-04）

核对`CHP-14.pdf`物理页15–18。图版61页标题将《安东尼与克娄巴特拉宴会》两图置于Algarotti影响语境；上图标“a. Early version”，下图扫描可见“b. Final version”，OCR只保存前者。沿用图版目录的既有作品候选`cand-4100`/`cand-4101`及题注断言，不合并两版本。图版62画面题注归于Canaletto、称Prà della Valle in Padua；S0 OCR作Prato，印本校读只记S2。图版63扫描保留Domenico Cerato题注残片“Project for the r…”，通过独立图版目录连接其完整题名“Original proposals for reclaiming Prato della Valle”，不把目录题名补写进残片。图版64实物页横向旋转，S0 OCR将题注词序倒置；对照原图校读为“Francesco Guardi: View of John Strange’s villa at Paese near Treviso”，链接既有图版64人物、作品、地点及收藏题注。新增11条提及、4条图像题注statement，未新增候选。受控脚本`chp14_plates61_64_s2_migration.py`锁定来源/PDF SHA并检查S2前态和既有图版statement；四表备份后缀`.bak-s2-chp14-plates61-64-20261004`。覆盖核验通过：全账本830段中517 complete、109 excluded、204 queued、0 partial；候选10,407、提及23,190、statement 10,213；`s2_missing=[]`、`errors=[]`。下一处理位置为第十五章开篇。


## 第十五章 p.361 开篇及注1–2（2026-10-04）

对照`CHP-15.pdf`物理页1处理章题、注释及正文`chp-15:15_CHP-15_sec_i:l3-14`。脚本`chp15_p361_s2_migration.py`锁定两份Markdown与PDF的SHA，默认dry-run，校验覆盖前态、候选连续号、提及锚点、statement原文及脚注回链；四表恢复备份后缀`.bak-s2-chp15-p362-20261004`。新增8个候选（`cand-10423`–`cand-10430`）、53条提及、27条statement。

正文记录1764年威尼斯绘画“great flowering”近尾、Piazzetta/Tiepolo/Pittoni与新一代历史画家的处境、Canaletto与Guardi、Zuccarelli/Zais、Pietro与Alessandro Longhi，以及艺术家、赞助人和藏品逐渐消散的叙述。分列Sagredo藏画分散、Schulenburg收藏1775年解体且此前大部分已送往Germany、Smith最佳绘画1762年归George III及遗孀数年后出售余下画廊、Algarotti私人绘画在Bonomo 1776年去世后开始分散。Smith未具名遗孀和p.361画廊、Zanetti所藏未指明绘画组及两项概念作来源限定候选；不把Smith最佳绘画转移与余下画廊出售合并。沿用Algarotti个人藏画`cand-10223`，与联合藏品`cand-10224`及家族藏品`cand-10312`区分。Zanetti正文只给姓氏，沿用索引候选`cand-2838`但不外推身份；Mariette关于藏画将离开Venice是被Haskell报告的假设，不写成已发生的转移。“these men”完整所指未能确定。关系候选记录Alessandro为Pietro之子、Bonomo为Algarotti之兄弟及藏画交易，尚非S6正式边。

注1记G. A. Moschini 1810引文；注2记Mariette致Temanza的1768年4月15日信及E. Müntz 1890年出版定位。所引作品和信均未独立查阅。S2页图校读、不改S0：`Y 1764…Bnearly`→`By 1764…nearly`、`to.return`→`to return`、`Guaraña`→印本`Guarana`、`out ofVenice`→`out of Venice`、`during'`→`during`及移除行末OCR短横。段尾“though it is”续至p.362 L17，正文coverage保持partial。

首次机械审计发现章题段缺少`no_semantic_content:`理由，补正并保存`s2-coverage.csv.bak-s2-chp15-p362-auditfix-20261004`恢复点；复审`errors=[]`、`s2_missing=[]`。当前830段为519 reviewed/complete、111排除、199 queued、1 partial；候选10,415、提及23,243、statement 10,240。下一段为`chp-15:15_CHP-15_sec_i:l16-25`。

页码复核更正：`CHP-15.pdf`物理第2页页眉标印刷页362，因此本批物理第1页开篇为印刷页361，下一源段从p.362 L17接续。最初写入时将开篇误标为p.362；由`chp15_p361_pagination_repair.py` dry-run/apply更正8个候选题名、53个mention ID、27个statement ID及`printed_page`，并改正内部注释引用和p.361→p.362跨页指针。恢复点为`.bak-s2-chp15-p361-pagination-fix-20261004`；复核后全表`errors=[]`、`s2_missing=[]`。初次写入和章题修复备份仍保留，后缀含p362反映当时误标，不作为当前页码依据。

## 第十五章 p.362 正文及注1–2（2026-10-04）

对照`CHP-15.pdf`物理页2（页眉印刷页362）处理正文段`chp-15:15_CHP-15_sec_i:l16-25`及合并页注段L43–56中的注1–2。受控脚本`chp15_p362_s2_migration.py`默认dry-run，锁定Markdown/PDF SHA并校验coverage前态、候选序列、提及锚点、statement数量和跨页收口。新增19个候选（`cand-10431`–`cand-10449`）、86条提及和42条原书statement；四表恢复副本后缀为`.bak-s2-chp15-p362-apply-20261004`。同日期原后缀恢复副本已存在且内容与本轮前态不同，未覆盖该旧恢复点；本轮另用唯一后缀保存。

正文记录Farsetti出身、Lodoli门生关系、旅行与巴黎经历、成为abate以避开政治责任、投入艺术、威尼斯新古典运动中的地位评价、铸件收藏及Rezzonico的介入、Furlani铸模、Pozzi临摹、四件现代雕塑范例、小型绘画收藏、跨地域趣味，以及Padua别墅计划转往S. Maria di Sala后的住宅设计。作者以“English milord”比拟Farsetti在罗马的行事姿态，独立记录为作者修辞，不推作国籍或头衔。L23的“This”先行词保持未决；p.362 L25的四十二根柱子句以partial statement记录，续文指向p.363 L28。注1的Farsetti家史、Paravia pamphlet和Sforza论文，注2的Memmo引文分别登记为书内引文线索，均未独立查阅。来源Markdown未改写。

对候选跳转再核后修正了索引身份：`cand-2898`“Clement XIII, Pope”是`see under Rezzonico, Carlo`交叉引用，不代表另一人物。p.362的两条姓名提及及一条statement现均只链接既有Carlo Rezzonico候选`cand-2137`。受控修复`chp15_p362_pope_crossref_repair.py`默认dry-run；写回前保存mentions与book-statements恢复副本`.bak-s2-chp15-p362-pope-crossref-20261004`。修复后表审计仍为`s2_missing=[]`、`errors=[]`。

写回后`python -X utf8 scripts/audit_tables.py --summary`通过：`s2_missing=[]`、`errors=[]`；830段中520 reviewed/complete、111有理由排除、197 queued、2 reviewed/partial；候选10,434、提及23,329、原书statement 10,282。两条既存enrichment `source_ref`警告仍在；另有197段queued及2段reviewed/partial的收口提示。下一源段为第十五章p.363正文`chp-15:15_CHP-15_sec_i:l27-36`；全书S2未达到S3交接条件。

## 第十五章 p.363 正文及注1–6（2026-10-04）

对照`CHP-15.pdf`物理页3（印刷页363）处理正文段`chp-15:15_CHP-15_sec_i:l27-36`及合并页注段L43–56中属于本页的注1、3–6；注2在OCR正文段L36抽出。受控脚本`chp15_p363_s2_migration.py`默认dry-run，锁定来源/PDF SHA、coverage前态、候选序列、提及锚点、statement数和p.362跨页收口。新增12个候选（`cand-10450`–`cand-10461`）、86条提及和36条原书statement；四表备份后缀`.bak-s2-chp15-p363-apply-20261004`。p.362柱子结构句闭合，单独记录“由教皇让与Farsetti”的来源陈述并回链；p.362正文coverage转complete。

本页记录别墅平面被批评为过度僵硬、破坏自然节奏，壮盛时期“壮观而非优美”；其后“battered shell”限定为Haskell写作时的描述。百万ducats支出保留“was said”传闻层级，近乎毁掉Farsetti家族和打动同时代人的评价独立记录。匿名同时代人对别墅的长引文保留说话者未名；注2指向Boscovich致Vallisnieri信，但未查原信，不据此确认引文作者。园林、植物珍稀物、Veneto景观、别墅装饰、Farsetti对威尼斯绘画/雕塑的影响、收藏开放给学生临摹、Academy比较、Palazzo Farsetti传播古典范式的作用及其向Algarotti拨款均分别入statement；“拨款特别合宜”作为Haskell评价单列。Antonio Canova的到威尼斯年份、两个篮状作品、在罗马看Farsetti摹本、Raphael’s loggie的威尼斯版本及Farsetti病后失能均保留原有限定。Daniele Farsetti的堂表亲关系、画家身份、Pastels展出和继承/扩充收藏分别登记；“continued the”续至p.364 L39，相关statement仍partial。

本页页图校读只记于S2、不改S0：正文L32 `Use`→`life`；L34 `to' Venice`→`to Venice`；L35 `17251787`→印本`1725–1787`，行末断词`exhibition- / of`规范为空格。注3 L47 `Notarise`→`Notarile`、`ri April`→`11 April`、`788V`→`788v`；注5印本编号5而OCR作6；注6印本编号6而OCR作8。注1、3–6按印本回链，所引De Tipaldo、Mazzotti、Boscovich、档案记录、Malamani、Canova Quaderni及Haskell/Levey均未独立查阅。脚注2在正文段L36的来源定位由一次机械审计发现未纳入覆盖范围；将coverage规范为L27–36，注释说明L36为页下注后复审通过。

写回后表审计`s2_missing=[]`、`errors=[]`；全账本830段中521 reviewed/complete、111有理由排除、196 queued、2 reviewed/partial；候选10,446、提及23,415、原书statement 10,318。两条既存enrichment `source_ref`警告仍在。下一源段为第十五章p.364正文`chp-15:15_CHP-15_sec_i:l38-41`；全书S2未达到S3交接条件。

## 第十五章 p.364 Farsetti段末及注1–2（2026-10-04）

对照`CHP-15.pdf`物理页4（印刷页364）处理`chp-15:15_CHP-15_sec_i:l38-41`，并将合并页注段L51–52（注1–2）接回正文。受控脚本`chp15_p364_farsetti_s2_migration.py`锁定Markdown/PDF SHA，校验coverage前态、候选序列、提及锚点及statement数，默认dry-run；预检发现档案提及锚点与同句机构提及重叠，改用非重叠的`Busta 540`定位，并将statement预期数量校正为实际15条后通过。应用前四表恢复副本后缀`.bak-s2-chp15-p364-farsetti-apply-20261004`。新增6个候选（cand-10462–cand-10467）、38条提及和15条原书statement；更新p.363 Daniele patronage statement并闭合跨页句。

正文记录Tommaso Giuseppe与Daniele的兄弟关系、其更重视书籍和手稿的个人收藏、对Farsetti家史的忠诚及其记述、对Filippo巨额收藏支出的遗憾、其晚年受侄子Anton Francesco挥霍影响及向Inquisitors举报的书内叙述。随后分别记录举报无效、十九世纪初Farsetti财产拆散及收藏出售、学者愤慨；Canova作为十八世纪末从威尼斯出现的唯一重要艺术家的Haskell评价；对Farsetti影响“回顾看来微不足道或有害”的评价；同时代人以其赞助寄望文化复兴、贵族退出传统艺术支持后Farsetti被诗歌和演说树为榜样，以及Haskell对Farsetti“影子人物”的总结。末段将Farsetti置于旧式自足赞助人与Andrea Memmo所代表的公共服务观之间。兄弟关系和举报作为关系候选保留在S2 statement，不生成正式边；Tommaso个人藏书/手稿类型未强定；家史与p.362注1所引作品是否同一、收藏出售对象范围均未外推。文化复兴及公共服务按语境登记为观念候选，不写成制度或实际成效。

注1引用`Inquisitori di Stato`、Busta 540档案记录；注2引用Moschini 1806卷II页114。档案及书目页均未独立查阅，按citation trail记录。相邻`sec_ii`的Andrea Memmo正文尚未处理，因此同页注3–6（合并L53–56）暂留待办，合并页注段coverage扩至L44–52并保持partial。p.363正文段转complete，p.364 Farsetti正文段complete。S2页图校读只记录、不改S0：L39 `fife`→印本`life`、L40 `grëat`→`great`、L39起始跨页OCR `os`→印本`of`；印本保留`rôle`。所引外部来源未独立核验。

写回后`python -X utf8 scripts/audit_tables.py --summary`通过：`s2_missing=[]`、`errors=[]`；830段中523 reviewed/complete、111有理由排除、195 queued、1 reviewed/partial；候选10,452、提及23,453、原书statement 10,333。两条既存enrichment `source_ref`警告仍在。下一源段为`chp-15:15_CHP-15_sec_ii:l3-4`（Andrea Memmo，印刷页364）；全书S2未达到S3交接条件。

## 第十五章 p.364 Andrea Memmo开篇及注3–6（2026-10-04）

对照`CHP-15.pdf`物理页4（印刷页364）迁移正文段`chp-15:15_CHP-15_sec_ii:l3-4`及合并页注L53–56。受控脚本`chp15_p364_memmo_s2_migration.py`默认dry-run，锁定Markdown/PDF SHA并校验coverage前态、候选序号、提及锚点、statement数量及既有脚注链接；四表恢复副本后缀`.bak-s2-chp15-p364-memmo-apply-20261004`。新增10个候选（`cand-10468`–`cand-10477`）、31条提及和19条statement。

正文记录Andrea Memmo的出生、patrician家族背景、与Consul Smith的往来、其后来所述在Smith图书馆初次欣赏“chaste architecture”、Carlo Lodoli对他的影响、政治改革与贵族隔离、法国文化和观念等。将“chaste architecture”、未具名Smith图书馆、未具名家族、威尼斯贵族群体与书目定位分列候选；不与Lodoli的建筑主张或现有图书馆/家族身份自动合并。Casanova、Giustiniana Wynne及Smith求爱关系按作者叙述保留语气，不外推书外事实。段尾“and he”作为partial statement留待p.365闭合。

注3–6逐项迁移：Chapter 12交叉引用；P. Molmenti及Torcellan（1963）书目线索；Chapter 11交叉引用；Tabacco页32及后续页。被引书目未独立查阅。页图确认“chaste architecture”后的印本脚注号为5，而OCR误作6；真正的注6在“intellectual formation”之后并指向Tabacco。校读只记S2、不改S0。全表审计通过；本页结果随后由p.365的跨页句闭合。

## 第十五章 p.365 正文及注1–2（2026-10-04）

对照`CHP-15.pdf`物理页5（印刷页365）处理正文段`chp-15:15_CHP-15_sec_ii:l6-12`及合并页注L91–92。受控脚本`chp15_p365_memmo_s2_migration.py`默认dry-run，核对来源与PDF SHA、覆盖前态、候选ID、精确提及跨度及statement数量；写入前为四表保存`.bak-s2-chp15-p365-memmo-apply-20261004`恢复副本。新增5个候选（`cand-10478`–`cand-10482`）、50条提及、26条statement；并把p.364未完的love-affairs断言改为complete并链接注1。

正文分别记录Memmo拒绝Doge机会、1775年在Padua任Provveditore、赞助成为其主要关切、年度农业集市、Prà della Valle的地理位置、回填/运河/岛屿方案、椭圆规划与Colosseum参照、Abate Cerato实施、募款和雕像计划及其公共德性解释。候选新增为Provveditore术语、集市事件、S. Giustina教堂、Radicchio 1786与Neu-Mayr 1807引文定位；交叉引用既有Prà、作品和人物候选，不合并索引子条目或未经核对的身份。Haskell关于规划价值、启蒙、动机和影响的表述保留评价及概率限定。p.365“Only nobles or men who had brought particular glory to the”续至p.366 L15，故正文coverage为partial。

注1记录Brunelli（1923）定位；注2分列Radicchio 1786（Prà历史）与Neu-Mayr 1807（雕像、铭文）两个引文线索，均未独立查阅。印本注2标记位于集市启用时间之后，但注释所列内容指向Prà历史及雕像/铭文；保留脚注回链，不将其当作精确集市启用年份的独立佐证。OCR将注2拆在脚注L92与正文L12，页图确认原印本完整措辞。印本校读只记S2、不改S0：`Proweditore`→`Provveditore`、`Pra`→`Prà`、`Cerate`→`Cerato`、`Brunel Ji`→`Brunelli`、`Pri`→`Prà`、`thatwas`→`that was`、`themain`→`the main`、`Use`→`life`、`scries`→`series`，并校正fair句后的注号为2。全表审计`s2_missing=[]`、`errors=[]`；830段为525 complete、111有理由排除、192 queued、2 partial；候选10,467、提及23,534、原书statement 10,378。两条既存enrichment `source_ref`警告未变。下一源段为p.366正文`chp-15:15_CHP-15_sec_ii:l14-28`；全书S2未达到S3交接条件。

## 第十五章 p.366 正文及注1（2026-10-04）

对照`CHP-15.pdf`物理页6（印刷页366）处理`chp-15:15_CHP-15_sec_ii:l14-28`。受控脚本`chp15_p366_memmo_s2_migration.py`锁定Markdown与PDF SHA，默认dry-run，校验coverage前态、候选ID、精确提及锚点、statement数量及跨页收口；写入前为候选、提及、statement和coverage表保存`.bak-s2-chp15-p366-memmo-apply-20261004`恢复副本。新增20个候选（`cand-10483`–`cand-10502`）、85条提及、26条statement；另将p.365表示资格句闭合并把p.365正文coverage改为complete。

正文记录雕像提出资格、低成本与统一质量规则；Antenor、Azzo d’Este、布伦瑞克家族及Padua选择的十四世纪podestà；Memmo赴君士坦丁堡任职后在罗马的募像活动、Subleyras图稿、教皇与访客捐助、托斯卡纳大公、波兰/瑞典王室及Piranesi版画，并区分1786年Radicchio记述和“88项中53项已在位”的进度。原书未命名者、作品与机构身份不从索引自动定案；“another six in Rome”的句法关系保持未决。页图校读只记S2、不改S0：OCR `Prato`校为印本`Prà`，`Memiiio’s`校为`Memmo’s`，`dining`校为`during`。段尾“and during”续至p.367，故p.366正文仍partial。

注1保留Haskell对格洛斯特公爵1775/1777年到Padua、Memmo劝其委托雕像的谨慎叙述，以及Egerton MSS. 1969、John Strange致G. M. Sasso和Mingardi绘图的引用链；所引信件未独立查阅。注1链接到公爵雕像statement。合并页注段仍只迁移L91–92，L93–113待正文按源序处理。表审计`s2_missing=[]`、`errors=[]`；830段中526 complete、111有理由排除、191 queued、2 partial；候选10,487、提及23,619、原书statement 10,404。两条既存enrichment `source_ref`警告保留。下一源段为p.367正文`chp-15:15_CHP-15_sec_ii:l30-36`；全书S2未达到S3交接条件。

## 第十五章 p.367 正文及注1–4（2026-10-04）

对照`CHP-15.pdf`物理页7（印刷页367）处理正文`chp-15:15_CHP-15_sec_ii:l30-36`及合并页注L93–96。新增9个候选（`cand-10503`–`cand-10511`）、64条提及和29条原书statement；闭合p.366末句“and during”，但p.367正文L36续至p.368 L39，仍为partial。合并页注段目前迁移到L96，L97–113待后续按源序处理。

正文分别记录Memmo罗马最后一年的《Elementi dell’Architettura lodoliana》出版线索、1787年返威尼斯及Procuratore任职、58则《Apologhi》、向Padua的颂词和其不满；Prà della Valle露天剧场与市政雕像规划；Waldstein、Dux、Skala及Veith相关叙述中的疑问和可能性；Memmo与Canova及Poleni的关系、雕像委托和Haskell对风格变化/中世纪题材的评价。Dux所指地点、Skala候选身份及未完成委托均不补定。注1区分1786年第一卷出版和全书1834年刊行；注2–3记录《Apologhi》及颂词书目；注4保留Molmenti/Torcellan对Memmo书信的二手讨论。被引书信与著作未独立查阅。

页图校读只记录在S2、不修改S0：L31书名末尾`f`为注号；L33 `asked"`为OCR标点噪声；L36印本为“notable variations”。注L93 `HI`校为`III`、`P. Valloni`校为`P. Vallotti`；L94 `Procurala`校为`Procuratia`；L95 `Zana`校为`Zatta`。受控脚本`chp15_p367_memmo_s2_migration.py`默认dry-run，锁定来源与PDF SHA并校验coverage前态、ID、锚点及statement；写表前保存恢复副本。写回后机械审计`s2_missing=[]`、`errors=[]`；830段中527 complete、111有理由排除、190 queued、2 partial；候选10,496、提及23,683、原书statement 10,433。两条既存enrichment `source_ref`警告保留；S2尚未达到S3交接条件。下一正文段为p.368 `chp-15:15_CHP-15_sec_ii:l38-47`，合并页注段L97–113仍待处理。

## 第十五章 p.363 已完成段落的候选提及回查（2026-10-04）

章节级候选表面审查在已complete的p.363 L27–36发现遗漏：句中“himself an amateur painter”的`amateur`未关联既有术语候选`cand-3570`，尽管已有statement `st-chp15-p363-daniele-cousin-amateur-painter`描述该事实。受控脚本`chp15_p363_amateur_surface_repair.py`以来源SHA及原statement为前置条件，dry-run确认精确字符区间后，新增提及`m-chp15-p363-0087`并更新该statement的mentioned候选列表；表恢复副本后缀`.bak-s2-chp15-p363-amateur-repair-20261004`。审计后总提及数为23,684，其他S2段落状态未变化。回查器剩余3个字面命中均在合并页注L97–113的queued范围（Venice、Europe、The Hague），将随源序处理；该启发式扫描不替代召回率或语义验收。

## 第十五章 p.368 正文及注1–7（2026-10-04）

对照`CHP-15.pdf`物理页8（印刷页368）处理正文`chp-15:15_CHP-15_sec_ii:l38-47`和合并页注L97–104。受控脚本`chp15_p368_querini_s2_migration.py`锁定Markdown/PDF SHA、校验前态与精确提及锚点，默认dry-run；写表前保存恢复副本`.bak-s2-chp15-p368-querini-apply-20261004`。新增15个候选（`cand-10512`–`cand-10526`）、49条提及和24条statement；更新p.367气候与Prà della Valle跨页statement为complete。另将sec_ii L1仅含生成式Markdown文件名的标题段按同章标题惯例排除。p.368正文末句“which Querini wished to”续至p.369，故p.368正文仍partial；注1–7已迁移，合并注段覆盖L91–104，L105–113待源序处理。

正文闭合Prà della Valle因风化而呈现的原初“绿洲”印象，并保留Haskell对美与实用结合的评价；记录Memmo与Pietro Zaguri围绕Lodoli的友好争论、政治抱负随威尼斯命运衰退、家族宫殿中的壁画廊、约48幅多为复制品的绘画及其与兄弟向知识界人士开放的聚会。新小节转入Angelo Querini：其公共服务与艺术赞助、进一步的启蒙立场、私人利益指控、scholar-gentleman理想、对Lodoli的敬仰、对Memmo提供早年资料、可能与外国大使的关联、1761年宪政危机及State Inquisition权限争议均按Haskell转述登记。大使和女性匿名，关联保留“possible/perhaps”；p.368关于State Inquisition权限的句子跨页未完，未推断Querini具体希望采取何种行动。另建立未知地点的Memmo家族宫殿、壁画廊、Mengs《圣家》素描、Brenta、未识别引用与档案清单等候选，不借同姓或后页索引先行合并身份。

注1–7分别记Molmenti《Un nobil huomo》页137 ff.、Fontana页142、Sasso与Viero编制并存于威尼斯国家档案馆Petizion 488的1792年财产清单及Levi卷II页254出版线索、Lorenzo da Ponte页52、Brenta防洪争议的Brunelli Bonetti 1951年引文、Memmo 1786年《Elementi》页29注1、Bozzola 1948年页93–116。库存、档案和二手书目均未独立查阅；“These were destroyed”所指对象未强定。页图校读仅记于S2、不改S0：L42 OCR布局符转录为印本分节符“— iii —”；L44 `confmed`→`confined`；L45 `Use`→`life`、`fives`→`lives`；注L98 `i960`→`1960`，L100 `Is published`→`is published`，L102 `BruneUi`→`Brunelli`，L104 `BozzMa`→`Bozzola`。全表审计`s2_missing=[]`、`errors=[]`；830段中528 complete、112有理由排除、188 queued、2 partial；候选10,511、提及23,733、原书statement 10,457。两条既存enrichment `source_ref`警告仍在。下一正文段为p.369 `chp-15:15_CHP-15_sec_ii:l49-59`；全书S2尚未达到S3交接条件。

## 第十五章 p.369 Querini 与 Alticchiero（2026-10-04）

对照 `CHP-15.pdf` 物理页9（印刷页369）处理正文 `chp-15:15_CHP-15_sec_ii:l49-59` 与合并页注 L105–108。受控脚本 `chp15_p369_querini_s2_migration.py` 锁定 Markdown/PDF SHA、coverage 前态、候选编号、提及锚点与跨页statement，默认 dry-run；本批新增18个候选（cand-10527–cand-10544）、50条精确提及和32条原书statement。写回前四表备份后缀 `.bak-s2-chp15-p369-querini-apply-20261004`。表审计发现10个页注来源候选采用了校验器未接受的 `footnote-mention` 值；按仓库枚举修正为 `body-mention`，由 `chp15_p369_candidate_origin_repair.py` 受控修复并备份 `.bak-s2-chp15-p369-origin-repair-20261004`。修正后审计通过。

p.368 State Inquisition 句在本页 `reduce` 闭合，原 statement 转 complete。正文记录Querini对改革“进步性”的限定、改革被Haskell解释为统治阶层内部权力转移、Foscarini胜利后Querini被捕及获释后转向文化活动；1764年被传为Beccaria匿名著作作者严格保留传闻状态。另记录1777年赴瑞士访问Voltaire、赠送特铸奖章及Lucretius铭文、Girolamo Festari同行、Querini营建Alticchiero、其与Giustiniana Wynne的交往和1762年婚姻，以及Wynne-Rosenberg关于别墅的引述、家具、Houdon两尊哲学家胸像、园林影响和安全状况。Haskell的“意大利独一无二”等价值判断保留为作者评价。p.369 L59城市规划句跨至p.370，仍标partial。

页注1把1764年作者传闻回连至Haskell所引匿名《Voyages…》（The Hague, 1777）来源链；注2只记“Festari”字样及页下注位置；注3登记Bernis被引述对Rosenberg与Marquis de Prié的评价；注4记录Wynne-Rosenberg《Alticchiero》(1787)、Bruno Brunelli 1931文章，以及Heraclitus/Democritus胸像当时据称位于Padua Casa Soster。书目、引文及对象位置均未独立查阅。页图见印刷标题 “A NEW DIRECTION”，OCR漏掉；并记录 `accouple`→`a couple`、`dette`→`delle`、`different`→印本旧拼法 `differens`、`2II`→`211`、`Brunelh`→`Brunelli` 等校读，不改S0。

## 第十五章 p.370 Alticchiero 别墅与园林（2026-10-04）

对照 `CHP-15.pdf` 物理页10（印刷页370）处理 `chp-15:15_CHP-15_sec_ii:l61-67` 及合并页注 L109–110。受控迁移脚本 `chp15_p370_alticchiero_s2_migration.py` 默认 dry-run，锁定来源/PDF SHA、coverage前态、候选序号和锚点；新增24个候选（cand-10545–cand-10568）、48条提及、24条原书statement，并更新p.369城市规划partial句。写回前四表备份后缀 `.bak-s2-chp15-p370-alticchiero-apply-20261004`。

正文记录浴室Piranesi版画、Picart东方风俗版画、藏书的分类范围、Bacon胸像以及Querini书斋中《Daphnis and Chloe》版画（依Haskell归于Regent Philippe d'Orléans设计、Audran镌刻）；这些归属只记为书内断言。园林部分记录规则布局与“可悦的混杂”、Young's Wood及Night Thoughts影响、哲学生活寓意、Friendship altar的Epicurus/Phocion胸像、Girolamo Ascanio Giustiniani题铭、其他友谊与理想祭坛、未具名在世雕塑家所作Apollo形象。另记录“cabane de la folie”、Montaigne格言、与威尼斯未具名老妇相似的古代胸像、Wynne-Rosenberg由此联想到东方对疯者的敬重，以及Huber多角度Voltaire头像版画。Haskell的审美/政治解释、未具名对象和不确定关系均保留原有限定，没有生成正式关系边。

注1为Querini Alticchiero财物清单的Levi出版线索（卷II页255），注2为Moschini 1806卷II页116；均未独立查阅。页图校读记录Regent法文名重音、`wildarea`→`wild area`、`who "was`→`who was`、Montaigne撇号、卷号`H`→印本`II`，不改S0。审计发现校读记录最初附在同页所有statement上，已通过 `chp15_p369_p370_ocr_correction_repair.py` 限定到实际受影响的6条statement，并备份 `.bak-s2-chp15-p369-p370-ocr-repair-20261004`。p.369的Beccaria书名校读也移除错误的L50挂接；主体仍挂在L52传闻statement。


## 第十五章 p.371–372 正文与注释（2026-10-04）

对照`CHP-15.pdf`物理页11–12（印刷页371–372）处理p.371正文`chp-15:15_CHP-15_sec_ii:l69-83`、p.372正文`chp-15:15_CHP-15_sec_ii:l85-88`，并收口合并注释L91–113。p.371迁移脚本`chp15_p371_querini_s2_migration.py`新增26个候选、53条提及和28条statement；候选表面回查再发现正文L79的Naples（cand-3534）和L83的Renaissance（cand-3578），由`chp15_p371_candidate_surface_repair.py`补2条提及并更新对应statement引用，恢复副本后缀`.bak-s2-chp15-p371-candidate-surface-repair-20261004`。

p.371正文记录Alticchiero祭坛的Ignorance、Envy与Calumny形象、Querini访客纪念碑、Mme Rosenberg的寓意叙述、雕塑收藏、Winckelmann影响、Algardi与Canova作品，以及Dominique De Non的交往、版画、Voltaire肖像和《Voyage Pittoresque》工作；署名`amico suavissimo`的肖像坐者仍不确定。注1–2记录Isidoro Bianchi、Francesco Milizia、Jacopo Morelli及De Tipaldo、Moschini、Pallucchini等书目线索，未独立查阅。印本校读只进入S2：`above ail`→`above all`、`contacts'was`→`contacts was`、`he.was`→`he was`、`five with`→`live with`。

p.372脚本`chp15_p372_querini_s2_migration.py`新增3个候选（Altar of Furies、Temple of Pallas、Museo Civico at Padua）、17条提及和12条原书statement；闭合p.371关于Renier竞选Doge及Canova胸像的续句。记录Renier于1779年成为Doge及之后的政治妥协、Querini将胸像掷向Altar of Furies、他对古代异教遗址的个人意义、Haskell与Maffei/Winckelmann的比较、Rousseau影响，以及1796年按Querini请求安葬其心脏的叙述。注L113报告一尊被Haskell推定为该胸像的陶制胸像存于Padua的Museo Civico，并转述未具名者关于仆役盥洗处的推测；身份、馆藏与推测均保留为未核来源陈述。

首次结构审计发现p.371原statement的引句越过了所属源段。由`chp15_p372_cross_reference_repair.py`将其恢复为p.371段内引句，续文改以`cross_reference_statement_ids`链接p.372的Doge statement；该修复后复审通过。三段coverage现complete。最终表审计`s2_missing=[]`、`errors=[]`；830段中534 complete、112有理由排除、184 queued、0 partial；候选10,582、提及23,903、原书statement 10,553。候选表面启发式回查扫描17个已审段，仅余p.368 Venice同名重复候选提示（已记cand-2719、未裁决cand-3401），留待S3身份对齐；它不是覆盖或语义验收。两条既存enrichment `source_ref`警告未变。下一源段为第十六章`chp-16:16_CHP-16_intro:l1-1`；全书S2未完成，尚未进入S3。

## 第十六章 p.373 开篇及注1–2（2026-10-04）

对照`CHP-16.pdf`物理页1处理章节开篇正文`chp-16:16_CHP-16_intro:l3-14`及合并注段L70–71；仅文件名构成的L1按惯例排除。受控脚本`chp16_p373_sasso_s2_migration.py`以Markdown/PDF SHA及coverage前态为锁，默认dry-run；新增10个候选、30条提及和16条statement。候选表面回查发现正文L6“art patrons”及注L71 Venice未覆盖，`chp16_p373_candidate_surface_repair.py`补2条提及并把相应候选加入statement提及清单。两次写入前均为被改表保存独立恢复副本。

正文记录Haskell对新式赞助人审美与威尼斯绘画传统的对比、其关于Guardi及低位经销者的判断、商人兼私人收藏者的社会形象，以及Giovan Maria Sasso的交易、收藏、通信、未完成写作计划、出生与早期绘画学习、英国Residency往来和John Strange的商业合作。来源姓名“Giovan Maria”与索引候选“Sasso, Giuseppe Maria”不合并，留待S3；“Republic”按政治实体候选与城市Venice区分。Strange雇Sasso购画的句子在p.373 L14未完，statement保持partial并链接p.374。

注1保留Cicogna 1856版、Lorenzetti 1914及Longhi肖像的书目线索；注2记录Strange至Sasso信件的Epistolario Moschini馆藏、Mauroner转引、Sasso回信大多缺失以及British Museum四封信架藏号。均为Haskell书内引注，未独立查阅。页图校读只记入S2、不改S0：首字母花体W移位、`die/tbe`、姓名周边标点、`termswith`、注释`bis`及`Biblioteca Cotter`分别依印本校正；来源行仍以原S0字面锚定。连续页序显示此PDF物理页1应为印刷页373，但S0 `[Page 2]` 保留并在覆盖说明中记录差异。

表审计`s2_missing=[]`、`errors=[]`；830段中534 complete、113有理由排除、181 queued、2 partial；候选10,592、提及23,935、statement 10,569。剩余14个候选字面提示均在合并注段L72及以后，尚未覆盖；p.373已处理行的两处提示已补记。两条既存enrichment `source_ref`警告未变。下一源序正文为p.374 `chp-16:16_CHP-16_intro:l16-22`；全书S2未完成。

## 第十六章 p.374 正文及注1–4（2026-10-04）

对照`CHP-16.pdf`物理页2（印刷页374）处理正文`chp-16:16_CHP-16_intro:l16-22`及合并注段L72–75。受控脚本`chp16_p374_sasso_s2_migration.py`锁定Markdown/PDF SHA和coverage前态，默认dry-run；新增9个候选、52条提及和19条statement。并闭合p.373 L14的购画列表，将p.373正文coverage转为complete；p.374收藏清单在L22仍续至p.375。

正文记录Sasso为Strange购画名单中的Rosalba、Canaletto及Tiepolo；画作在Strange近Treviso的乡间宅邸或London住所暂存后卖给富裕收藏者的书内叙述；交易中的保密、运输和海关困难；Strange对现代艺术的委托、拟出版Zompini《Le Arti》、雇用Guardi、经Sasso转达的画稿要求、对Guardi与Tiepolo的偏好；Armanni对Mr Poore的嘲讽引语及威尼斯经销者的艺术趣味；Canova索求Tiepolo modello与随后明确撤回的“Sasso买尽”传闻；以及Sasso死后拍卖的个人收藏。Tiepolo姓氏泛指处保留未决，人物、匿名作品、拟议出版和传闻不升级为身份或已完成事实。

注1为Haskell关于Guardi赞助的期刊页码；注2为Strange–Sasso Letter 8（1784-12-22）；注3定位Armanni–Sasso两卷书信、谈及Poore的1789-07-07信件及Edward Poore版画/素描的两场1805拍卖；注4为Haskell在《Journal of Warburg Institute》1960年p.276的引文。上述书信、档案和拍卖目录未独立查阅。页图校读只记S2、不改S0：`citta`→`città`、`hot just clear`→`not just clear`、`with'whom`→`with whom`、`eighteenthcentury`→`eighteenth-century`，以及脚注年份/缩写标点校正。Zompini作品名的正文读法“per le vie”与索引子条目“per via”并列保留待S3。

表审计`s2_missing=[]`、`errors=[]`；830段中535 complete、113有理由排除、180 queued、2 partial；候选10,601、提及23,987、statement 10,588。候选表面回查余下9个字面提示均在合并注段L76以后、尚未处理的脚注范围内；p.374已审行无未覆盖提示。两条既存enrichment `source_ref`警告未变。下一源序为p.375正文`chp-16:16_CHP-16_intro:l24-36`及对应页注L76–81；全书S2未完成。

## 第十六章 p.375 正文及注1–6（2026-10-04）

对照`CHP-16.pdf`物理页3（印刷页375）处理正文段`chp-16:16_CHP-16_intro:l24-36`及合并注段L76–81。迁移脚本`chp16_p375_della_lena_s2_migration.py`默认dry-run，锁定Markdown/PDF SHA并校验覆盖前态、候选ID、锚点、跨页收藏清单和statement数；写回前为四表保存恢复副本。新增12个候选（cand-10618–cand-10629）、62条提及及20条原书statement；表面回查后由`chp16_p375_candidate_surface_repair.py`补记注5中的Venice，合计63条新提及。della Lena复用主索引候选cand-1387，保留Guardi子条目cand-1388，不重复造人物候选；Haskell 1967引用复用cand-9424，期刊cand-6004与未具名篇名的1960页码引文cand-10629分开。

正文闭合p.374的Sasso收藏清单；记录Strange介绍Worsley、Sasso继续为其寻画、Worsley赠Guardi画作给Lady Palmerston，以及Haskell关于Sasso经销可信度/艺术品外流的评价。della Lena被置于经销与学术边缘；记录其与Moschini的友谊、写作威尼斯绘画外流记述、德国经销活动、生于Lucca 1732、长期居Venice、任西班牙副领事并于1807年去世，以及兄弟Innocenzo、Eusebio与西班牙大使和Casanova的关系。另记录32幅Guardi画作、della Lena致Ortes信、信中艺术/科学价值论及Haskell对Guardi风格的解释；未具名历史学家与大使不被擅自命名，概率判断和引语归属保留原层次。页图确认p.375末句完整，下一页正文另起人物。

注1–6逐条接回正文：Sasso拍卖目录与两处副本馆藏；Strange–Sasso Letter 57；Sasso通信对象及档案位置；Haskell 1960期刊页码；della Lena记述的Correr手稿；其致Ortes信的日期/架号。来源均只按Haskell脚注记录，未独立查阅。页图校读仅记S2、不改S0：校正目录题名`Catalogo de' quadri`与`n. 381`、年份`1960`，以及正文行首OCR横线/杂点；保留来源原字面作为锚点。p.374收藏statement现complete；p.375正文complete，合并注段L70–81已迁移、该注段仍partial。

写回及表面修复后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；830段中537 complete、113有理由排除、179 queued、1 partial；候选10,613、提及24,050、原书statement 10,608。其余2个候选表面提示落在尚未处理的注L83–84，随p.376继续。两条既存enrichment `source_ref`警告未变。下一源序为p.376正文`chp-16:16_CHP-16_intro:l38-46`，并处理到达的注L82起；全书S2未完成。

## 第十六章 p.376 正文及注1–3（2026-10-04）

对照`CHP-16.pdf`物理页4（印刷页376）处理正文`chp-16:16_CHP-16_intro:l38-46`及合并注段L82–84。受控脚本`chp16_p376_vianello_toninotto_s2_migration.py`锁定Markdown/PDF SHA和coverage前态，默认dry-run；新增17个开放候选（cand-10630–cand-10646）、55条提及、29条statement，写回前对四表保存恢复副本。页图驱动的候选表面复核发现L44 “old masters”应复用已有术语cand-4288；`chp16_p376_candidate_surface_repair.py`另补1条提及及statement映射并保存两表恢复副本，因此本页最终新增56条提及。S0原始OCR不改写。

逐行语义处理：L39拆分“may well have belonged to the circle of Sasso and della Lena”（Haskell的可能性判断）与“was a canon of Chioggia Cathedral”（书内身份陈述）；后者端点暂留类型空值，因文本未区分教堂建筑与其教士团体。L40–41记录Haskell对Vianello学术姿态的评价、他于1793年刊行Rosalba日记的版本、身份未定的经销者判断、1790年图录对其愿售画作的强烈暗示、200余件藏品及25件della Vecchia画作；未将“strongly suggests”写成已证经销身份。L42登记Rosalba、未能消歧的Ricci、Piazzetta、姓氏待S3确认的Tiepolo及Guardi；保留Guardi作品数量/媒介、其未见于标准工具书、与Canaletto比较、透视批评和Haskell所引审美评价。`Ricci`只给姓，索引同页有Marco与Sebastiano Ricci，故新候选cand-10645明确保持身份未决。L43–45记录Toninotto的道明会身份、相对前述收藏者的比较、在Frari为游客导览与乞讨、State Inquisition责难、1785年del Pian九幅版画组及其Carpaccio题材、收藏中的古代作品归属、两件della Vecchia未题名作品、Zais与Guardi数量和媒介；将版画组出版责任、制作者、题材分作不同关系候选。L46记录Swajer的德国商人身份、常居Venice、1792年死亡、手稿收藏和“secret” manuscripts可能散佚的叙述；原句未完，未补写后续Inquisitors State的反应。注L82将1790图录线索接回正文；L83保留Haskell 1960期刊页码并复用p.374–375文章候选；L84登记Swajer通信在Seminario Patriarcale的馆藏定位，未称已查阅档案。

印本校读只记入S2、不改S0：L39 `ofChioggia`、`GiovanniVianello`补空格；L41 `Pietrp`校读为`Pietro`、`‘alia Giorgionesca’`校读为`‘alla Giorgionesca’`；L44 `tnodelli`校读为`modelli`；注L82 `in.`校读为`in`；L83 `i960`与`Journal os`分别校读为`1960`与`Journal of`。提及锚点仍精确引用S0 OCR字面，校读仅保存在statement限定中。注1连Vianello图录，注2连Toninotto段L43–45；注3连Swajer正文L46。p.376正文L46的末句续在p.377 L49，注3的详细定位续在p.377源段L60–64，两者均以partial和跨段链接保留；合并注段L69–89已处理到L84，其余不是本页注释。

写回后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；830段中537 complete、113有理由排除、178 queued、2 partial；候选10,630、提及24,106、原书statement 10,637。候选表面启发式扫描5个第十六章已审段，未发现未覆盖提示；该检查不代表完整召回或语义验收。两条既存enrichment `source_ref`警告不变。下一源段为p.377正文`chp-16:16_CHP-16_intro:l48-64`，先闭合p.376 L46及注3；全书S2尚未达到S3交接条件。

## 第十六章 p.377 Celotti段、Swajer续文及注释（2026-10-04）

对照`CHP-16.pdf`物理页5（印刷页377），迁移正文段`chp-16:16_CHP-16_intro:l48-64`、p.376注3续文及合并页注段L70–89。受控脚本`chp16_p377_celotti_s2_migration.py`校验来源指纹、覆盖前态、候选ID、提及锚点与statement数量，默认dry-run；应用前四表均保存恢复副本。新增26个候选（cand-10647–cand-10672）、65条提及和34条statement。

正文L49闭合p.376 Swajer手稿句：手稿令国家宗教裁判官不安并被收走；Swajer与Giambattista、Gian Domenico Tiepolo及Canova有往来，后者为其作肖像。L51–58迁移Celotti跨政权经销、伦敦/巴黎/威尼斯活动、报刊售藏启事、梵蒂冈教皇礼拜堂合唱书插画、古代大师与十八世纪威尼斯绘画，以及Canaletto、Tiepolo和Sebastiano Ricci作品描述；保留拍卖宣传引语与Haskell的评价层级，不把被售作品擅自识别为具体作品。L59的复数“these men”保持群体断言，后由p.378继续；不把相似收藏模式分派到每个个体。

正文段同一S0段L60–64还承载p.376注3的续文，已逐项迁移Valerio Vannetti、Durazzo家通信组、两封Tiepolo信及Urbani de Ghelthof文件可靠性疑点；对应p.376正文与注3均由p.377闭合。合并页注L70–89中的Celotti注1–5及先前待接续文本已完成回链；被引手稿、期刊、拍卖目录与信件均未独立查阅。对书内推断及引文保留原有限定。

## 第十六章 p.378 结论段（2026-10-04）

对照`CHP-16.pdf`物理页6（印刷页378），处理`chp-16:16_CHP-16_intro:l66-67`。受控脚本`chp16_p378_conclusion_s2_migration.py`默认dry-run，验证跨段指代、精确提及范围和coverage前态；新增候选cand-10673（Venetian tradition）、6条提及和3条statement，并把p.377的群体综合断言双向连到本段。

本段将p.377“these men”作为群体主体，记录其靠国际古代大师市场维生、收集受十八世纪下半叶欧洲趣味变化影响的画家作品，以及Haskell回顾性地称其为威尼斯传统的守护者。`pandering`与`guardians`保留作者评价/隐喻，不改写成中性事实、正式组织身份或个体层面的关系。结论段coverage complete；第十六章S2至p.378结束。

## 第十七章 p.379 folio i（2026-10-04）

对照`CHP-17.pdf`物理页1（印刷罗马页码i），由`chp17_pi_manfrin_s2_migration.py`迁移标题、Manfrin开篇正文和注1–6。新增15个候选（cand-10674–cand-10688）、52条提及和25条statement；另有两个生成式Markdown文件名标题段按既定规则排除。标题段及注释段完成；正文L3–6保留“Indeed, within five years,”的未完句，因此先标partial，待p.380闭合。

记录Manfrin的商人身份、社会地位、Dalmatia烟草种植垄断、财富及其取得方式的Haskell限定、被报道的终身放逐及撤销、1786携枪许可、1787购入Venier家族房产和收藏家地位。另处理未公开Manfrin材料、Meschini账户、讽刺诗手稿、1797 pamphlet及Inquisitori档案定位；姓名、家族、建筑和档案均保持索引候选或待S3身份审查，不外推为已独立核验事实。页图核定此页为罗马folio i；S0的`[Page 2]`只是OCR页标。页注标记OCR 8/6/8按印本在S2记录为3/5/6，pamphlet题名`impacciale`校读为`imparziale`，档案register读作538；S0不改。

## 第十七章 p.380 正文及注1–6（2026-10-04）

对照`CHP-17.pdf`物理页2（印刷页380），由`chp17_p380_manfrin_s2_migration.py`迁移正文`chp-17:17_CHP-17_sec_i:l8-20`及页注段`l26-35`中L27–31；新增6个候选（cand-10689–cand-10694）、69条提及和26条statement。候选表面启发式回查发现`connoisseurship`漏连既有术语cand-3567，`chp17_p380_candidate_surface_repair.py`补1条提及并更新statement候选清单；另以`chp17_p380_crosspage_statement_link_repair.py`为p.379/p.380跨页句的两条p.380 statement补上反向交叉引用。因此p.380本页净增70条提及、26条statement。

p.380 L9–10闭合p.379句首“Indeed, within five years,”，将Manfrin死亡传闻、Bologna、G. A. Armanni致Sasso的信及信中“几乎唯一在威尼斯为美术花钱的人”的引语分层记录；`Armarmi`依页图校读为Armanni，保留引语的比较语气。随后迁移1785年Tiepolo《Varj Capriccj》献辞、两年后肖像版画卷、Manfrin在威尼斯艺术界的位置、其画廊所呈现的意大利及部分佛兰德绘画史、从Mantegna/Bellini到Guardi/Gian Domenico Tiepolo的作品范围，以及Manfrin致Pietro Edwards书信中的选画权限、品质标准与保密要求。Haskell关于“暴发户势利”的判断、画廊仿佛具有国家机构地位及其对威尼斯绘画的纪念意义均标为作者评价，不写成制度身份。

页注记录Armanni—Sasso 1790年7月20日信件定位、Tiepolo版画册及肖像卷馆藏定位、Meschini引文、Edwards MS.788.13、Manfrin销售/版画目录和Manfrin—Edwards信件的Correr/Appendix 7定位。被引原件、目录和Meschini著作均未独立查阅。印本校读只记S2、不改S0：Armarmi→Armanni；正文L13漏掉的脚注5补入校读记录；`óf`→`of`；`allTlLmo`→`all’Ill.mo`；意大利文`spetti - - pennelli`校为`esperti pennelli`；注6的OCR注号8及`Epistolario Meschini`依页图校为6及`Epistolario Moschini`。

来源边界：分节OCR的p.380注5只保留Edwards手稿记录；印本注5后续销售目录文字与同页正文L16–20重复。该重复已用页图及整章OCR交叉确认，其独立事实由正文statement与候选覆盖，S0文件保持不改。S2覆盖段`l26-35`因此只迁移L27–31并保留partial，因L32–35属于p.381注释，待下一页续办。p.379正文现complete，p.380正文complete。

写回后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全书830段中545 complete、115有理由排除、169 queued、1 partial；候选10,678、提及24,299、原书statement 10,725。两条既存enrichment `source_ref`警告仍在。第十七章候选表面启发式扫描5段后，剩余2个提示均在尚未处理的p.381页注L33与L35；该扫描仅为提示，不代表语义召回或验收。下一源段为p.381正文`chp-17:17_CHP-17_sec_i:l22-24`。

## 第十七章 p.381 Manfrin段、Correr段及注1–5（2026-10-04）

对照`CHP-17.pdf`物理页3处理`chp-17:17_CHP-17_sec_i:l22-24`、合并注段`chp-17:17_CHP-17_sec_i:l26-35`的L32–35，以及`chp-17:17_CHP-17_sec_ii:l3-5`。受控迁移`chp17_p381_s2_migration.py`校验规范分节文件/PDF哈希、覆盖前态、稳定ID、提及精确跨度与statement端点，默认dry-run；应用前为四表留`.bak-s2-chp17-p381-20261004`。随后`chp17_p381_s2_followup_repair.py`按表面提示补2条提及、1条statement并修复竞赛主题映射；mentions与statements另留`.bak-s2-chp17-p381-followup-20261004`。新增12个候选（cand-10695–cand-10706）、47条提及和29条statement。S0及PDF来源资产均未改写。

L23记录Manfrin凭顾问专长和财富形成超过400幅作品的收藏；Batoni《Triumph of Venice》沿用既有作品cand-4085，连接Marco Foscarini（cand-1053）并区分“为其绘制”与已有委托合同；画廊在威尼斯的评价、旅游吸引力，以及Giorgione《Tempesta》（cand-10695）入藏分别成句。L24保留Haskell对Manfrin赞助活动的贬评及“缺少有才华画家”的限定；竞赛组织连接cand-1512与索引主题cand-0817，“erotic themes”映射cand-1313。Joseph与Potiphar之妻、Bathsheba、Lot与女儿、Susanna与长者只作为题材列在原书statement限定中，不指认为竞赛产生的特定存世作品；启发式命中的cand-1445（p.195 Carlo Loth作品）和cand-2177（p.280n Sebastiano Ricci作品）不作错误映射。

sec_ii L3记录Teodoro Correr（索引cand-0857）与Manfrin的对比、1750年出生、画像所显特征、未具名贵族家族、1768年读论文和聚会、政治生涯、Council of Ten、成为abate，以及1787年因缺乏资力不能就任Treviso总督的来信。对“Republic”按威尼斯政治实体与城市区分；未具名Doge只保留为职位，不推测个人身份。画像复用既有Plate 59b作品cand-4007；脚注作者写Bernardo Castelli，而List of Plates写Bernardino Castelli，新增cand-10696保留拼写差异待S3。所引论文候选cand-10697不推断为Correr创作；页末“However, there”续至p.382，故sec_ii段保持partial。

页注1–5均已回链：注1新增Moschini 1806卷II页107及1810引文定位；p.380相同卷页位置写Meschini，本轮保留书内两种姓氏形式，待书目/身份阶段判定。注2记录V. Lazari、G. Mariacher 1957和T. Pignatti 1960的博物馆目录线索；注3说明画像署名和1795年雕版信息；注4将Correr聚会材料定位到Biblioteca Correr、Archivio Correr 1468/10（6a–d）；注5以同档案单元1468/10（5）回链Correr来信。引文、目录和手稿均未独立查阅。

印本校读仅存于S2：L24 `Potiphars Wife`→`Potiphar’s Wife`；sec_ii L3 `his Use`→`his life`、`ofjuno`→`of Juno`、引文尾注号OCR 6→印本5；注L32 `U`→`II`；注L33–34 `i960`→`1960`；注L35 OCR漏掉`1468/10`；sec_ii L4–5的`ibid., (5)`及损坏的`IO`据印本补读为`ibid., 1468/10 (5)`。原OCR字面仍用于提及与引文锚点，校读值写入qualifiers。

候选表面启发式回查覆盖7个已审段，剩4条提示并已人工裁决：L23 Venice命中跨页段索引候选cand-2719（page range 245–383），cand-3401保留为另一来源候选供S3核对；L24 Joseph、Lot and his Daughters、Susanna and the Elders均为竞赛题材，不能复用其他章节同名人物/具体作品候选。该扫描是定位提示，不作召回率结论。`audit_tables.py --summary`通过，`s2_missing=[]`、`errors=[]`；830段为547 complete、116有理由排除、166 queued、1 partial；候选10,690、提及24,346、statement 10,754。两条既存enrichment `source_ref`警告仍在。下一源段为p.382正文`chp-17:17_CHP-17_sec_ii:l7-17`。

## 第十七章 p.382 Correr收藏与Longhi作品群（2026-10-04）

对照`CHP-17.pdf`物理页4处理`chp-17:17_CHP-17_sec_ii:l7-17`，并迁移书末脚注段`l24-33`中的p.382注1–3、5–6（L25–29）；本页注4直接位于正文分节L16–17。受控脚本`chp17_p382_s2_migration.py`先校验分节/PDF哈希、覆盖状态、候选自然键、提及精确跨度和statement端点，dry-run后应用，备份四表。随后`chp17_p382_s2_followup_repair.py`补映射现有Renaissance术语候选、拆分收藏目标与宫殿两项断言、将“他的档案”指回新建的未指明档案材料候选，并用p.382 L8关闭p.381未完句；修复前同样dry-run，应用时备份受影响表。合计新增16个候选（cand-10707–cand-10722）、60条提及和30条净新增statement。来源OCR、PDF均未改写。

L8闭合p.381“However, there”后，记录Correr为威尼斯服务的评价。L9保留“无法确定/可能年轻时开始收藏”的不确定语气，以及将收藏遗赠给威尼斯的书内陈述。L10分别记录委托现世艺术家的不确定判断、Molin/Orsetti/Pellegrini家族作为图片来源、对同时代人财务弱点的利用、参加拍卖、收集有助威尼斯历史和文化研究的文物/书籍/图片，以及Correr宫殿被Haskell回顾性称作博物馆；不把博物馆描述转成当时正式机构。三姓按家族候选保存，Pellegrini不与画家候选合并。L11保留早期与十八世纪作品收藏、Antonello da Messina《Deposition》和Cosimo Tura《Pietà》、藏品质量评价及Haskell关于历史好奇心的“almost certain”判断。L12–14记录Pietro Longhi在十八世纪藏品中的突出位置、约二十幅记录威尼斯生活的画作、Correr拥有一幅Alessandro Longhi肖像，以及向Alessandro取得其父Pietro的素描；不外推单件画作题名或数量。L15“led him”未完，保持partial，待p.383闭合。

p.382注4记Zocchi双人肖像（A. M. Zanetti the Elder与只以“Marchese Gerini”称呼的人）及1803年Sasso拍卖；人物全名和拍卖卖家身份不外推，购买保留“almost certainly”。注1、5均为Dandolo p.97；注2保留“just possible, though unlikely”从Pietro Longhi直接取得画作的例外；注3记录Urbani de Ghelthof出版物及未指明的Correr档案材料；注6分别记录被重新评估为Canaletto工作室作品的威尼斯景观，以及“probably by Francesco Guardi”的受损Castel Cogolo景观。引用材料均未独立查阅。

页图校读仅记在S2：L10 `already-a museum`→`already a museum`、两处`ofhis`→`of his`；L17 `sec Haskell`→`see Haskell`、`i960`→`1960`；页注L27 `Sec the hints`→`See the hints`。p.381 L3–5因L8闭合转complete；p.382正文L7–17仍因L15跨页句为partial；注释聚合段L24–33仅L25–29迁移为partial，p.383脚注L30–33尚待处理。启发式表面扫描中当前p.382已处理范围不再提示未映射实体；现有提示包括已裁决的p.381四项，及命中尚未审读p.383注L31的Biblioteca Correr。扫描不代表召回率或语义验收。

审计：830段中548 complete、116有理由排除、164 queued、2 partial；候选10,706、提及24,406、原书statement 10,784；`s2_missing=[]`、`errors=[]`。仍有两条既存enrichment `source_ref`警告；全书S2未达S3交接条件。下一源段为p.383正文`chp-17:17_CHP-17_sec_ii:l19-22`。

## 第十七章 p.383 Correr藏品与结论前叙事收束（2026-10-04）

对照`CHP-17.pdf`物理页5（印刷页383）完整处理`17_CHP-17_sec_ii.md` L19–22及合并注释段L30–33。受控迁移脚本`chp17_p383_s2_migration.py`校验输入哈希、段状态、候选外键、提及精确跨度、断言端点和既有自然键；先dry-run，再应用并备份四表。新增10个候选（cand-10723–cand-10732）、32条提及和19条原书statement；后续将注1的两件作品归属陈述拆成各自唯一断言，避免同段自然键冲突。

L20–21闭合p.382“led him”跨页句，分别记录Correr购入《Parlatorio》和《Ridotto》两件被Haskell描述为Gian Antonio Guardi、体现Longhi风格的作品；另将Ridotto赌馆作为独立地点。注1所载的Lazari 1859年Longhi归类与Correr时代的Guardi称呼分别挂接两件作品，保留归属史差异，不把引文升级成裁决。L22记录1797革命及随后外国占领导致贵族生活、收藏解体和图像进入市场的Haskell解释；记录Correr在共和国崩溃后购入大量画作、回避新政权承诺、以健康理由请求免除Civic Guard义务及附医生/牙医证明、持续收藏、1830年去世并将半世纪以上收藏留给威尼斯。对“crotchety”等性格描述及历史评价保留为Haskell话语；占领方、医生、具体画作及档案原件均未外推或独立查阅。Byron与Bonington保留原书姓氏候选，身份留待S3，未推断他们与Correr有交往。

印本校读只记于S2，不改S0：正文L22 `Liberia`校为`Libertà`；注L30 `i960`校为`1960`；注L31–32 OCR档号校为`1468/10 (9a)`。注2把该档号定位至Biblioteca Correr / Archivio Correr，原件未查；注3只记录Levi卷I页cxix，题名与身份未定。修正脚本和数据后`audit_tables.py --summary`通过，`s2_missing=[]`、`errors=[]`；全书830段现为551 complete、116有理由排除、163 queued、0 partial。全书语义质量仍待完成剩余段落并核验，不以账本审计代替。

## 第十八章结论 p.384–385（2026-10-04）

范围核对：`18_CHP-18Conclusion.md`对应独立来源`CHP-18Conclusion.pdf`两页；PDF物理页1为印刷页384，物理页2为印刷页385。覆盖段`l1-1`仅为生成的Markdown文件名标题，按理由排除；`l3-17`、`l19-23`为两页正文并已完整处理。两页没有脚注。p.384 L17句子跨页续至p.385 L20，statement已回链前一段。

受控脚本`chp18_conclusion_s2_migration.py`以PDF/Markdown哈希、覆盖状态、候选ID与自然键、提及精确跨度、statement原句及自然键为前置校验，dry-run后应用并备份四张表。新增13个开放候选（cand-10733–cand-10745）、77条提及、20条`origin=book` statement。S2只记录Haskell的叙述、比较、因果解释与评价层级，不把修辞问题改成确定判断，也不把集体陈述改造成具体边。作者未具名的历史人物、群体和制度类别按开放候选保存；Crespi身边的“eccentric Medici prince”没有与后文Grand Prince Ferdinand合并。对Bernini、Pietro da Cortona、Tiepolo、Velasquez、Fetti/Feti、Regent等沿用索引或已有候选；跨章身份和Fetti/Feti拼写差异留待S3。正文所引人物及Haskell判断未作外部来源核验。

逐段语义范围：p.384 L5–9记录Rome/Venice 1623–1797政治衰退、权力展示式艺术赞助、Bernini/Pietro da Cortona/Tiepolo及Haskell对意大利和外国艺术贡献的比较；L10–13记录社会诉求压制原创路径的论点及Bamboccianti、Salvator Rosa、Crespi、Canaletto、Padre Lodoli例证；L14–17记录意大利历史学家对同时代写作从众的反应、比较赞助人教养的修辞问句及跨页未完句。p.385 L20–23闭合“赞助人文化与宽容”的解释，记录继承价值与艺术异议、Fetti例外与城市绘画水平、赞助机会、社会结构崩溃后的适应困难、英法“bourgeois painting”、Parma Academy改革、Church/封建贵族衰退和威尼斯陷落等总结。一般艺术家/权力机构群体关系保留为S2 relation candidates并明确未形成具体正式边。

印本校读只记S2、不改S0：p.384 L5–6的首字母B大写字母在OCR行间错位；L7 `with-what`→`with what`；L11 `Efe`→`life`、`of‘national`→`of ‘national`；L13断行`- - plosive`→`explosive`并去除尾部噪点；L14 `difficult To`→`difficult to`、`Geofirin`→`Geoffrin`。p.385 L20 `above-was`→`above was`。逐条依据为`CHP-18Conclusion.pdf`页图，差异保存在对应statement qualifiers。

迁移后`audit_tables.py --summary`通过，`s2_missing=[]`、`errors=[]`；全书830段中553 complete、117有理由排除、160 queued、0 partial，规范表为10,729候选、24,515提及、10,823条原书statement。第18章候选表面扫描对2个reviewed正文段未报未映射span；工具只提示已入候选表名称的覆盖情况，不证明全章实体召回或语义准确。下一源段为附录标题`chp-19:19_CHP-19Appendix:l1-1`。

## 附录 p.386 来源覆盖补录（2026-10-04）

核对`CHP-19Appendix.pdf`物理页1时发现，规范OCR `19_CHP-19Appendix.md` L3–20到达8 March 1676书信正文，但漏掉页底该信的日期/署名以及随后出现的Brandi收据首段。平行OCR `19_CHP-19Appendix_intro.md`虽保留部分文字，但只是校勘对照，不作为规范锚点。页图显示收据跨至物理页2（印刷页387）续完，并在28 March 1682署期、以Giacinto Brandi署名；因此收据日期不取自上方8 March 1676书信，p.387页首也不是另一张独立收据。

已追加派生资产`19_CHP-19Appendix_p386_receipt_visual-transcription.md`，补录8 March 1676书信遗漏的日期/署名及Brandi收据首段，未改PDF、规范OCR或平行OCR。`build_source_segments.py --apply`结果为79个S0来源文件、832段、0 issues；新段`chp-19:19_CHP-19Appendix_p386_receipt_visual-transcription:l1-2`和`...:l4-4`起初登记为S2 `queued/pending`。随后p.386正文、日期/署名和收据首段均已完成语义迁移；收据与p.387续文联合处理，具体判断见下节。来源OCR与PDF保持原样。

## 附录 p.386–387 Brandi、Maratti收据及附录二开篇（2026-10-04）

核对`CHP-19Appendix.pdf`物理页1–2（印刷页386–387）、规范OCR及p.386派生转录。受控迁移以来源哈希、S0段哈希、覆盖状态、候选自然键、提及精确跨度和statement引文锚点为前置条件，dry-run后写回并备份四表。首次`audit_tables.py --summary`发现覆盖`source_line_ranges`误写为`L4-L20`/`L1-L2`，修正为协议格式`L4-20`/`L1-2`并再次审计通过。随后候选表面扫描在p.387的`modello`命中一个未映射跨度；按句意将其作为“gioia的模型”单独建候选、补确切span，并把“制作宝石”和“模型需装柄”拆为两个statement。该启发式扫描仅用于定位已登记名称，不证明召回率。

p.386 L4–12为Brandi 4 October 1675书信：D. Lerio Licà多次代表S. Andrea Novitiate的rector P. Loro催促一幅画；Brandi原以为须等小堂完备后才需要，收到通知后计划赶工并改动既有草图；信末保留脚伤、致歉和敬语，不外推作品完成。L13–18为25 February 1676书信：Brandi说前一 November已请Mattia di Rossi安排画布与框及预定位置，避免画成后移动；同信稍后写Signor Derossi，作为本信局部指代映射到同一开放候选，是否对应索引的Mattia de' Rossi留待S3。L19–20为8 March 1676信：邀请收信人看“quadro sborzato e tutto il Redentore”，并说其中Madalena不合其意；不把受损措辞升格为确定题名或图像身份。页图校读记为S2限定值、不改OCR：`happella`→`cappella`、`mia`→`mi ha`、`progurarò`→`procurarò`、`anhe`→`anche`。遗漏的8 March日期和Giacinto Brandi署名由同版视觉转录段`...visual-transcription:l1-2`承载，并回链到该信。

视觉转录段L4在p.386打开Brandi收据，规范OCR的p.387 L23–24续完：P. Paolo Ottolini（P.）经C. di G.身份/职衔不展开，按P. Domenico Brunacci之令支付200 scudi；收据称该款是S. Andrea Chapel of the Passion三幅画、`Volta`及retouching的全额，并在p.387签明截至28 March 1682完全结清。`fatti, o fatti fare`保留“亲作或安排他人做”的范围。`Volta`未擅定为穹顶空间或壁画；三幅画和其他项目以收据所给群组记录，不与cand-5344–cand-5346强行合并。此1682收据不并入1675–1676的Novitiate绘画委托。

p.387 L25–29为Maratti独立收据，署22 September 1679：经Casa di Probatione di S. Andrea的procurator P. Severino Vittori收到100 scudi作为B. Stanislao Chapel一画的分期款；承诺一年内完成，并记录未完成时退款以及疾病/意外等明示例外。这是承诺，不证明当时已完成。L30–32为第二张独立收据，署19 September 1687：P. Giuseppe Tonini经手的300 scudi来自一名Tonini认识但未具名的人；连同1679年已收的100 scudi，是Maratti已为同一小堂完成之画作的价款，Maratti声明完全结清。两张文书、付款人和时间限定分别保存；画作候选在本地相连，是否为既有St Stanislaus作品cand-1536/cand-5352留待S3。`Casa di Gesù`不与Brandi收据未展开的`C. di G.`合并。

p.387 L34–36附录二标题把Fondo Orsini、Biblioteca Vallicelliana、Rome与Paolo Giordano Orsini对Bernini/Tacca的委托文书联系起来，并给出171, c. I定位；书内标题是定位/描述，不证明该具体委托履行。L37–41的档案信记录未具名写信人称其从Cavalier Bernino取得Madonna模型并交给Giacomo Ant:o；后者展示四种厚度/高度不同的模型，想用合适混合料制作`gioia`，原文还讨论silver及一件供手持、可固定gioia模型的柄状构件。`Manichette`为OCR读法，页图看似单数`Manichetto`，只在限定中记录。`Il Tedesco`、其未具名妻子及先后两名未具名学徒的死亡/再婚叙述作为信中转述；粉末原料OCR为`dalco`，页图字形未足以排除`talco`，不定校。末句关于四枚蓝宝石在L41截断，跨至p.388，故本段保持partial并以`cross_reference_segments`指向`chp-19:19_CHP-19Appendix:l43-63`；不把V.E.认作Orsini公爵或推定作者。

本批（含表面回查修复）新增35个候选（cand-10746–cand-10780）、64条提及、22条`origin=book` statement；p.386规范正文、日期署名、收据开头及p.387收据/附录段均有覆盖记录，p.387段为partial、等待p.388闭合。候选身份映射保留索引候选和来源候选边界，外部档案/文献未独立查阅。更新后`audit_tables.py --summary`为832段：556 complete、118有理由排除、157 queued、1 partial；10,764候选、24,579提及、10,845 statements，`s2_missing=[]`、`errors=[]`。`audit_s2_candidate_surfaces.py --chapter chp-19`扫描4个已读段，当前0个未映射提示；这不是语义召回或独立接收证明。下一段为p.388 `chp-19:19_CHP-19Appendix:l43-63`，优先闭合四枚蓝宝石的跨页句并继续附录二书信。

## 附录 p.388–389 Fondo Orsini及附录三文书（2026-10-04）

对照`CHP-19Appendix.pdf`物理页3–4（印刷页388–389）处理`chp-19:19_CHP-19Appendix:l43-63`与`l65-84`。p.388闭合p.387蓝宝石句和Fondo Orsini 171, c. I书信；c. I印本签名读作Domenico Fedini，OCR把署名和下一条c.140定位合并并读成Pedini。p.389 c.463信末再次署`Dom.o Fedini`，日期为Rome, 12 July 1626；据此将p.388 c.463请求的发言者更新为同一局部Fedini候选，撤销“未具名写信人”重复候选。两处Fedini读法仍与索引cand-1014分开，等待S3身份对齐。另两封分别署Domenico Pedini的c.140与173, c.2文书保持独立：前者报告向Bastiano Sebastiani提议以不超过25 scudi铸造公爵铜头像及石膏/蜡模型试制，属于计划；后者报告铜铸件已制成、Bernini只准清除浇口并等待公爵命令再移至Bernini家中完成修整，未声称后续转移已经发生。铜头像与cand-5546/5547的关系仍交S3核定。

p.389的172, c.306信署Pietro Tacca，日期为Florence, 30 December 1624。Tacca报告马模型已装箱寄出，要求Federighi按说明谨慎拆箱再包装；若公爵决定铸铜，才会增加模型未表现的配件。没有把条件性方案写成已制作的雕像。该信与第四章脚注所指Tacca致Paolo Giordano II书信候选复用，具体稿本未独立查阅。

附录三标题将两组文书定位为Stefano Conti委托Marcantonio Franceschini与Felice Torelli的相关材料，Biblioteca Governativa, Lucca, MS. 3299，并指回第八章p.227注1–2。2月17日Franceschini信列举若干可选题材，包括Arianna/Bacco、`Tona [sic]`、Eva与Caino/Abele；未把列举方案写成已选或完成作品。印本保留`Tona [sic]`，上下文可能指Latona但不作确定校正。2月24日Giuseppe Torelli信称其兄Felice已为既有画作找到特洛伊题材，叙述Pirro杀Polissena、Calcante、Enea、Antinoro及Achile之墓，并讨论人物身份与画面难度；该信只证实题材选择，不证实画作完成。两信分别复用第八章p.227相应人物/作品候选及文书，不另造重复实体；被引手稿未独立查阅。页图仅记S2：签名OCR`Pedini`校读为印本`Fedini`；标题中的`.Marchesini`多余点在印本不存在；`Febee`校读为`Felice`；`all’in sù`后的框状图形保留为非文字记号，不解释其含义。

受控脚本`chp19_p389_s2_migration.py`核验PDF、Markdown与S0段哈希，dry-run后应用；写前备份候选、提及、statement及coverage四表。首轮表审计发现同一附录标题的两条commission statement使用了相同自然键claim，已由`chp19_p389_claim_repair.py`在dry-run校验后区分为两条对象级claim并备份修正。最终新增6个候选、40条提及、7条statement；p.387、p.388、p.389三段均为reviewed/complete。表面候选扫描6个已审段发现一个`modello`词面提示：其既有cand-3451指油画初稿，本段`modello del Cavallo`指Tacca雕塑马模型cand-5555，属异义，不漏记为同一术语。当前全书832段中559 complete、118有理由排除、155 queued、0 partial；10,781候选、24,662提及、10,861 statement。常规`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；两条既存enrichment来源引用警告仍在。下一源段为p.390 `chp-19:19_CHP-19Appendix:l86-107`。


## 第十九章 p.390：附录四信件与Crespi来信（2026-10-04）

对照`CHP-19Appendix.pdf`物理页5（印刷页390）迁移`chp-19:19_CHP-19Appendix:l86-107`。5月1日Ricci信称送给Ferdinand两箱画：一箱有侄子的两幅风景，另一箱有Canon Marucelli的两幅`sfondi`及一幅小画，并请求将赠物安置于Ferdinand的一处别墅。第八章p.235明确将侄子指为Marco；p.390信本身只写“mio Nipote”。另记小画人物由Ricci绘制、其他人物由`Paesista`绘制，但“其他”的指向范围未定。Canon的名字不在信中，未认作Francesco或Orazio；为其保留局部候选。Ricci希望六月初到场绘制Ferdinand命令的museum room；又称承诺为Canon另画一室。两项都是待履行计划。

5月8日回信确认两箱完好抵达，复述两幅风景、两幅`sfondi`和小画，并称已命人将`sfondi`交给Canon；museum room因Ferdinand疾病与行程尚不能开工，Ricci可暂缓赴约，待可施工时再通知。未把该房间装饰记为完成。候选cand-10798/cand-10799分记背景画组与同箱小画，和1708年Crespi提及的另一幅小画严格区分。

2月26日Crespi信报告返乡并感谢Ferdinand；他称曾在Ferdinand画廊询问一幅小画作者，有人答为Tintoretto，Crespi则自称是自己所作。此为Crespi自述和转述的先前归属，不作独立作者鉴定。同信称看过Sebastiano Ricci的作品并赞其精神与技艺，作为写信人的评价保存。1月31日Vincenzo Ranuzzi信在L105开始，注明Archivio Mediceo, Filza 5897, No.183，正文提到未具名`Spagnuolo Pittore`后跨入p.391；已建局部候选，姓名/身份待闭合。

此页图还校读p.390 L94 `ima Villa`为`una Villa`、L98 `E due Sfondi`为`li due Sfondi`。档案原件未独立查阅。第八章p.235物理页41也印`No. 500`；此前脚注statement依OCR `No. zoo`误登记为200，现保留statement主键但将claim、predicate、候选cand-7976及OCR校正记录改为500；第八章p.235原OCR引句保留，便于追溯。旧迁移脚本记录的是当时误判，当前表与本节为纠正后的权威状态。

受控脚本`chp19_p390_s2_migration.py`核验S0段及来源页哈希，dry-run后应用并备份候选、提及、statement和coverage四表。首轮审计发现coverage行范围多写一个`L`，修成契约格式`L87-107`并另存前态备份；复审后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`。本页新增5个候选、45条提及和10条statement；coverage为reviewed/partial，因为Ranuzzi信待p.391续读。全书832段中559 complete、118有理由排除、154 queued、1 partial；10,786候选、24,707提及、10,871 statements。第十九章候选表面扫描7个已读段仍只有既有`modello`提示（cand-3451油画初稿与cand-5555马雕塑模型异义），p.390未出现新的未覆盖提示。下一段为p.391 `chp-19:19_CHP-19Appendix:l109-124`。

## 第十九章 p.391：Ranuzzi信闭合与附录五开篇（2026-10-04）

对照`CHP-19Appendix.pdf`物理页6（印刷页391）、规范OCR及第八章p.237注2处理`chp-19:19_CHP-19Appendix:l109-124`。p.391页首接续并闭合Ranuzzi信；L110边注`Gius.e Crespi d.o`对应p.390 L107的`lo Spagnuolo Pittore`，第八章p.237注2又将Filza 5897 No.183识别为Crespi的介绍信，因此把原p.390局部候选映射至既有Crespi候选`cand-0873`。保留`d.o`原缩写，不展开；印本文书及档案原件未独立查阅。Ranuzzi称正写信告知Al Caldari其画作发生一件未详事件，以便向Ferdinand报告；Caldari只建姓氏候选，事件、画作内容与后续均不外推。

附录五开篇将Smith收藏史的证据缺口列为问题。Haskell称Smith于1762年向George III出售大量绘画与素描，作品后来构成Royal Collection的重要部分；他去世时（1770）Uccelli记录其宫中仍有数百幅画。清单仅列题材、不列作者，Haskell称其经C. A. Levi从Archivio di Stato-Petizion 467重刊。原清单、档案和Levi刊本未独立查阅。Haskell明确保留两种解释：1762年只售部分、其余留存并可能继续增藏；或全部售出后于1762–1770年重新购入数百幅；现有段落不足以裁决。另记Smith 1761年遗嘱拟由遗孀售出全部或部分藏品，同时希望图书、素描、宝石或绘画等完整类别可继续合并。关于George III购买图书馆的谈判，附录称约1755年已开始，第十章p.310称1756年；两种来源措辞并存，不能强行统一。1761预期身后出售与1762年Smith实际售藏也按原书区分。

受控脚本`chp19_p391_s2_migration.py`核验Markdown/PDF及跨章来源哈希、S0段哈希、既有coverage状态、候选复用与提及精确跨度，dry-run后写回并备份四表。首次表审计发现同页标题/正文重复短语导致两条提及偏移落在较早命中；按上下文将`the Royal`和末句`the King`跨度修正到结尾句，另记录脚本中OCR跨行连字符的真实词面与大写`The list of these`。最终新增5个候选（cand-10803–cand-10807）、40条提及和9条statement；p.390 Ranuzzi statement与相关提及完成闭合，p.391标为reviewed/complete。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全书832段：561 complete、118有理由排除、153 queued、0 partial；候选10,791、提及24,747、原书statement 10,880。候选表面扫描8个已审段仅余既有异义`modello`提示，p.390–391无新增未映射提示。下一段为p.392 `chp-19:19_CHP-19Appendix:l126-138`。


## 第十九章 p.392：Smith售藏证据、后续往来与Gennari来信开篇（2026-10-04）

对照`CHP-19Appendix.pdf`物理页7（印刷页392）处理`chp-19:19_CHP-19Appendix:l126-138`。L127承接p.391的售藏两难：Haskell称目前只有前述内容可确定，其余证据互相冲突。L128记1761年Smith考虑离开Venice、定居England；威尼斯报告称他准备出售宫殿及图书、版画收藏和珍贵物品；Parker页61–62转引Smith希望返英及“this whole Collection, the work of my life”。这些均作为报告、引文和可能计划，不作实际迁居或完整出售事实。James致Robert Adam的20 August 1760信称Smith贫困并可能死于破产，属于第三方判断；Haskell据此讨论全部售藏与后来购买昂贵画作两种可能，并以Smith于1766年重新担任领事补充年龄论证，均保留推论语气。

L129–131据Haskell转述一条1806年III卷p.51的材料，称Smith遗孀把其自留画作带到England；但Haskell指出作者似乎不知道Smith曾售画给King，且所述£20,000仅对应书籍与cameos，因此证据没有解决遗孀带去的是1762自留画还是后来购画。p.392页图读作`(b) Moschini`，OCR为`(¿) Meschini`；L131叙述也印Moschini。书目与此处署名差异及其与其他Meschini/Moschini候选的身份均不在本段裁决；原引文和刊本未独立查阅。

L132 Haskell认为，1762年售予King的画作中最充分代表“两位Riccis”、Rosalba Carriera、Canaletto和Zuccarelli，这些画家都为英国人熟悉，似乎暗示有意选择；“两位Riccis”在本页未展开姓名，有意选择也只是作者推论。同段说1762年后英、威来源极少提Smith，因而大量购画不大可能；这是Haskell对其检索结果的解释，不等于不存在其他档案。其援引Giovanni Volpato 22 April 1766致Remondini信，称有两件`Rametti`受Smith委托、Smith支付70 zecchini，并说还有送往London的事物将持续一年以上；保留意大利语对象名，不推作Smith个人购藏。L134–135另引Smith 9 April 1768致Bologna匿名通信者的信，称其显示Smith仍经手画作但不证明为本人收藏；Haskell感谢Denis Mahon允许发表。手稿及信件收件人均未独立核验/识别。

L136–138打开1768信：Smith收到关于Gennari绘画和素描收藏的清单，表示若所有者愿以适当价格出售，他愿出面收购，并询问全部或分售；这是条件性意向，不是交易完成。collection清单及作品未见原件；不把匿名owner与匿名correspondent合并。原信续到p.393，故p.392保持partial，并由开放statement `st-chp19-p392-smith-conditional-gennari-collection-offer`指向`chp-19:19_CHP-19Appendix:l140-155`。

页图校读仅记S2、不改S0：`rarità'pregevoli`→`rarità pregevoli`，`decided-to`→`decided to`，`buyexpensive`→`buy expensive`，`(¿) Meschini`→`(b) Moschini`，`^20,000`→`£20,000`，`- (d)`→`(d)`，`ih`→`in`，`from-the`→`from the`，`XXX, io`→`XXX, 10`。迁移脚本`chp19_p392_s2_migration.py`校验PDF/Markdown/S0哈希与段状态，dry-run后应用并备份四表，新增8候选（cand-10808–cand-10815）、40条提及、10条statement。候选表面回查另补2条重复England提及及`Biblioteca Comunale, Bologna`机构提及；机构名里的Bologna不另建重叠地点跨度，单独指向通信收件人地点的Bologna提及已登记。回查后p.392不再有未覆盖提示。全书表审计`s2_missing=[]`、`errors=[]`；832段为561 complete、118有理由排除、152 queued、1 partial；候选10,799、提及24,790、原书statement 10,890。下一段p.393 `chp-19:19_CHP-19Appendix:l140-155`。
## 第十九章 p.393：Smith来信闭合与附录五续文（2026-10-04）

对照 CHP-19Appendix.pdf 物理页8（印刷页393）及规范OCR处理 chp-19:19_CHP-19Appendix:l140-155。p.393 L141接续p.392 Smith 1768年4月9日来信：Smith说画作与版画仍不断出售但买家减少，自己购得数件、日后或可给通信者看；不推断这些作品是为个人收藏。L142–144记Smith要求重抄Gennari藏品清单、说明不愿交给他人传看，并以G. Smith署名结束。签名与下段(e)同处OCR L144；提及跨度只取签名，未把Haskell正文并入书信。信件原件和匿名通信者均未独立核验。

附录五后续保留Haskell的分层与限定：L144–146援引Moschini 1806, III, p.78称Zais曾为Smith工作、作品不在售予George III的清单中；“英国不知名/未被王室代理选中”与“1762年后才开始为Smith工作”是未裁决的两种解释。L147–148把Smith关于类似收藏难以再形成的引语与Haskell对£20,000的评论分开；原引语所据材料未在此页说明。L149是Haskell的强烈但非定论判断：1762年只卖出部分、1770年宫中大多数画作长期积累；他承认这可能影响第十一章赞助叙述，同时认为现有证据不足以要求大幅修正。

L150所列Christie's出售日期为1776年4月22日和5月16日；列表质量差、归属不确定。只登记组级描述：14幅Canaletto威尼斯景观、Pietro Longhi的两幅“Mr Murray and family”风俗画、Amigoni的Farinelli及另外两人的肖像条目。原目录未独立查阅，文字没有把各组作品分配到具体日期。第十章p.304注7的16 May目录所称另外14幅作品，未与这里的14幅Canaletto景观合并。L150–151另称若干画“said to have come”自Smith收藏，出现在1789年12月10日匿名拍卖（Haskell括注“in fact, John Strange”）；自画像、风景和其他画家组均按转述归属保存，不作确证。L152–153的1776素描/蚀刻目录更丰富，画家列表包含Marieschi；没有据此推断具体作品、数量或目录归属。Mr Murray不并入索引John Murray，Farinelli不补全名，Fetti与索引Feti, Domenico的关系留待S3。

页图校读只记S2、不改S0：L144 Meschini→Moschini；L147 (/)→(f)、¿20,000→£20,000；L150 fists→lists；L152 OCR Maneschi→印本 Marieschi。L155打开“Smith的书籍史同样难以重建”一句，续至p.394，故本段保持partial。

受控脚本 chp19_p393_s2_migration.py 核验PDF、Markdown及S0段哈希、p.392/393/394覆盖先决状态、候选复用和每条提及跨度；dry-run后应用并备份候选、提及、statement和coverage四表。本段新增14个候选（cand-10816–cand-10829）、54条提及、11条statement；既有p.392开放statement已标记由p.393闭合，p.392转complete，p.393标reviewed/partial。表审计 s2_missing=[]、errors=[]；全书832段为562 complete、118有理由排除、151 queued、1 partial；候选10,813、提及24,844、原书statement 10,901。第十九章候选表面扫描10个已读段仍只有p.389既有异义 modello 提示；p.393没有新增未覆盖提示。下一段p.394 chp-19:19_CHP-19Appendix:l157-183。

## 第十九章 p.394：Smith藏书史闭合与附录六（2026-10-04）

对照`CHP-19Appendix.pdf`物理页9（印刷页394）处理`chp-19:19_CHP-19Appendix:l157-183`。L158续完p.393 L155关于Smith藏书史难以重建的句子；Haskell说1762年出售的是1755年`Bibliotheca Smithiana`编目的图书，1770年Smith去世时宫中仍记录大量书籍，其中一些为新近出版，由此推断Smith持续购书至生命末期。该推断是Haskell根据书籍出版年代作出的解释，不作为直接购书记录。L158–160另记Smith此前向Giacomo Caraboli和Domenico Pompeati售出大量书籍，以及生命最后数月围绕合同发生激烈争议；引文定位为Archivio di Stato, Venice—Atti del Notaio Ludovico Gabrieli, Busta 7570, pp.1215, 1278。原档未独立查阅，售书的确切年份与合同结果不明。既有候选`cand-9857`的详情补入附录六提供的档案位置；新增`cand-10843`专指Inquisitoriato alle Arti档案系列，避免与`Inquisitori alle Arti`机构候选混同。

L160–162记录两种身后书目：1771年`Catalogo di Libri Raccolti...`，称为136页八开本并引Correr I.5911；1773年`Bibliotheca Smithiana, pars altera`广告称余下藏书将于“当日”廉价现金出售。后者保留为广告内容，不推断实际成交。相关档案/目录候选为`cand-10831`–`cand-10833`；相关索引副条目留给后续索引段处理。

附录六标题关联Chapter 12, p.330, note 1。L165–166将Andrea Memmo准备性笔记定位到Archivio di Stato, Venice—Inquisitoriato alle Arti, Busta 15, fascicolo 6；Haskell感谢Gianfranco Torcellan告知此件，称Memmo于1772–1775年担任Inquisitore alle Arti，并推测笔记写于就任前两三年。原件未读，任职期与笔记日期均按Haskell文字记录。p.330相关段落与注1已交叉链接；那里关于“C.”可能为Canaletto的识别只是有时间矛盾的假设，不作为本页身份结论。

L168–183是意大利文准备性问题清单，不是已完成调查结论。内容包括自由职业者免除税费的论述主题、画家“奇异天性”、缩写为“C.”的著名在世威尼斯画家与其免税主张；音乐教师和铜版雕刻师不纳税是笔记中的直接断言，但未独立验证；另有建筑师/画家税制、Naples是否有绘画学院、Parma学院新设、女性画家Rosalba是否纳税、外籍教授与准院士遴选、Terra-ferma公立学院数量/名称/费用、巴黎艺术学院成员特权及教学活动等问题。末句询问“我们的学院”的徽记与名称应确认或改进；结合p.330上下文暂映射到Venetian Academy，但仍待S3确认。`C. Veneziano`保持未扩名，Naples Academy、Paris Academy与Terra-ferma群组均保留原文的疑问或地域限定。

页图校读仅记S2、不改S0：L158 `Sòme`→`Some`、`very7`→`very`、`until-the`→`until the`、`Ebri`→`libri`；L159 `Efe`→`life`；L160 `GabrieE`→`Gabrieli`、`pubEshed`→`published`、`SmitE’s`→`Smith’s`、`Ju`→`fu`、`pulitamenti`→`pulitamente`；L161 `ofJoseph`→`of Joseph`；L168 `EberaE`→`liberali`、`scogliere`→`sciogliere`；L170 `prettenda`→`pretenda`；L171 `IntagEatori`→`Intagliatori`；L175 `NapoE`→`Napoli`；L178 `migEore`→`migliore`、`scegEersi`→`scegliersi`；L180 `PubbEco`→`Pubblico`；L181 `quaE`→`quali`；L182 `deHe`→`delle`；L183 `’1`→`’l`、`migEorare`→`migliorare`。原文中的`tansa/tansati`、`essenzioni`、`instituzione`、`soggezion`和`bizzaro`为印本拼法，保留不现代化。

受控脚本`chp19_p394_s2_migration.py`检查PDF/Markdown资产哈希、S0段哈希、p.393–395状态、候选自然键、每条提及精确跨度及互不交叉跨度；dry-run后写回并备份候选、提及、statement和coverage四表。新增14候选（`cand-10830`–`cand-10843`）、60条提及和12条statement；`st-chp19-p393-smith-books-history-open`由p.394续句闭合，p.393、p.394均转为reviewed/complete。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；832段中564 complete、118有理由排除、150 queued、0 partial；候选10,827、提及24,904、statement 10,913。第十九章11个已审段候选表面扫描仍仅有既存异义`modello`提示，没有p.394新提示。下一段为p.395 `chp-19:19_CHP-19Appendix:l185-208`。

## 第十九章 p.395 与第二版后记标题段（2026-10-04）

对照`CHP-19Appendix.pdf`物理页10（印刷页395）处理`chp-19:19_CHP-19Appendix:l185-208`。L186–195续完Andrea Memmo准备性问题笔记：L186询问缩写`n.A.`所指学院的守护圣人；L187要求查Duke Cosimo给予画家的命令、章程与特权，并标注Vasari已读；L188标注Vasari所载Montorsoli传记已读。L189–191询问巴黎学院秘书与院长、博洛尼亚秘书是否在世，姓名均未给出；L192–193要求查画家、雕塑家、建筑师、铜版雕刻师和青铜铸造者的行会章程，并研究学院年轻人进入学校或团体的特权，均为待查事项。L194把法国国王Carlo VI给予画家的税费、补贴和住房豁免作为笔记中的断言，附`Monier 179`定位；未查阅该引文，不能据此视为已核制度事实。L195为Memmo关于绘画思辨部分应自由、天才不应受实践支配的规范性论点。保留缩写、未具名官员、查询语气及印本拼法，不补定Cosimo身份。

L196–208为Appendix 7及Manfrin致Pietro Edwards的1793年12月3日信。Haskell将信定位于Biblioteca Correr, Venice—Epistolario Moschini，并回指第十七章p.380注6；原件未独立查阅。信中Manfrin请Edwards与Gio. Batta Mingardi按专业判断选择、辨认并排除藏画，表示不以成本为先、只要有“reale merito ed assoluto”的作品，并接受Edwards要求其不公开反对意见。此为委托请求和保密条件，不证明任何具体画作已被选择、购入或入藏；“reale merito ed assoluto”按原文保留，不补出缺失名词。信件statement与p.380既有摘要及出处相互链接，未另造一笔交易。

页图校读只记入对应statement，不改规范OCR：L197 `thè`→`the`、`formatioh`→`formation`、`Vertice`→`Venice`；L199 `bramare_`→`bramare`；L202 `diferenze`→`differenze`。L195印本`denono`、`prattica`等拼法保留。受控脚本`chp19_p395_s2_migration.py`检查PDF/Markdown和S0哈希、覆盖前置状态、候选自然键、提及精确跨度及statement原文锚点；dry-run通过后应用并备份四张表，新增6个候选（`cand-10844`–`cand-10849`）、34条提及和9条statement。

另核对规范OCR附加段`chp-19:19_CHP-19Appendix:l210-211`及`CHP-19Appendix.pdf`物理页1：该`Footnotes`块是p.386版面底部Brandi收据的重复OCR摘录，并非p.395单独印出的脚注。收据此前已从派生视觉转录段`chp-19:19_CHP-19Appendix_p386_receipt_visual-transcription:l4-4`及规范OCR续文`chp-19:19_CHP-19Appendix:l22-41`处理，因此将该段记为`excluded/complete`并写明重复来源，不重复建提及或statement。

检查后记源文件时，另将`chp-20:20_CHP-20Postscript:l1-1`排除为仅含Markdown文件名的生成标题；印本后记题名与正文从L3起。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；832段中565 complete、120有理由排除、147 queued、0 partial；候选10,833、提及24,938、statement 10,922。第十九章候选表面扫描覆盖12个已审段，唯一提示为p.389旧有异义`modello`，p.395无新增未映射提示。按来源行序，下一段为第二版后记开篇`chp-20:20_CHP-20Postscript:l3-12`。

## 第二版后记印刷页396–397（2026-10-04）

p.396（PDF物理页1）逐字对读页图后，新增14个候选、38条提及和9条statement；记录Lavin对圣彼得大教堂交叉空间演变的分析及其对Bernini归属的限定，并区分Hibbard、Lavin和相关研究的版本。p.396末句跨页，先标`partial`。受控迁移脚本经dry-run后写入，四张表留有恢复副本；随后将候选`source_ref`修正为精确单行锚点并重新审计通过。

p.397（PDF物理页2）处理Hibbard对华盖归属的限定、两组Barberini挂毯研究、Harris对Sacchi的再评价、古典／巴洛克论争及Ludovisi和Del Monte相关研究；保留引述层级、推测和未知出版物身份，未将文献转述写成独立核实事实。页图校正`thebaldacchino`、`Don Urbano "Barberini`和`16335`，分别记录为“the baldacchino”、“Don Urbano Barberini”及年份1633加脚注标记7。新增27个候选、48条提及和14条statement；p.396的Lavin引文在此闭合，p.397末尾Agucchi句续至p.398，故p.397保留`partial`。

首次写入后的全表审计发现p.397迁移脚本虽生成48条提及但未将其加入写入列表；候选表面扫描提示5个名称未覆盖。修正脚本并按原规范段哈希、候选外键、精确跨度及不重叠（允许嵌套）条件补写全部48条提及，额外保存`mentions.csv.bak-s2-chp20-p397-mentions-repair-20261004`。复核后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；候选表面扫描覆盖本章2个已审段，未覆盖跨度为0。全账本832段：566 complete、120有理由排除、145 queued、1 partial；候选10,874、提及25,024、statement 10,945。下一源段为印刷页398：`chp-20:20_CHP-20Postscript:l26-36`。


## 第二版后记印刷页398及第3章开篇（2026-10-04）

p.398（PDF物理页3，规范段`chp-20:20_CHP-20Postscript:l26-36`）经页图、Markdown与段哈希核对。处理p.397 Agucchi跨页句闭合；转录Haskell转述d’Onofrio对Agucchi别墅描述的归属、约四十幅Bolognese画作的“委托或购入”假设及其无定论限定；记录Agucchi编目、致友人谈《Erminia and the Shepherds》的信件、Carracci委托及Whitfield对programme的分析。延续记录Marino／Viola、Bentivoglio／Borghese／Baschet与Van Dyck肖像的后记更新。Cardinal Aldobrandini、Cardinal Borghese等身份保留未决，Van Dyck Plate 4a经图版目录确定为Cardinal Guido Bentivoglio肖像。

第3章正文从同段L32开始：记录1969年Fordham关于耶稣会与艺术的研讨会、Wittkower关于耶稣会影响教堂表现内容的判断及Haskell的保留、Haskell自述其对耶稣会与贵族赞助人冲突的论证，以及Ackerman对Gesù建筑中Borgia／Jesuit与Farnese两阵营的转述。Borgia阵营按原文括注理解为Jesuit而非Borgia家族；“Farnese”集体称呼和教堂空间保持语境限定。Ackerman引文在p.398结束，Haskell的“in a persuasive...”评述续至p.399，因此本段为partial；p.397转为complete。

脚注段`l211-280`仍queued；p.398 statement保留marker 1–7与脚注源段回链，不宣称已处理脚注全文。页图校正OCR注释L223“6 Viola”为印本“5 Viola”、L224“Jaffe”为“Jaffé”；校读记录在statement中，不改S0 OCR。迁移脚本dry-run通过后应用，四表恢复副本后缀`.bak-s2-chp20-p398-20261004`。应用后全表审计`s2_missing=[]`、`errors=[]`；832段中567 complete、120有理由排除、144 queued、1 partial；候选10,903、提及25,086、statement 10,959。第20章候选表面扫描覆盖3个已审段，未覆盖跨度0。下一段为p.399 `chp-20:20_CHP-20Postscript:l38-44`。

## 第二版后记印刷页399（2026-10-04）

按`CHP-20Postscript.pdf`物理页4核对规范段`chp-20:20_CHP-20Postscript:l38-44`。闭合p.398末尾Haskell评述：Hibbard认为耶稣会在礼拜堂题献、装饰和图像方案上有比Haskell原先承认的更强控制，同时赞助人仍对委托作品有有限选择。续录Buser对“Jesuit art”研究的挑战、Jerome Nadal默想书版画与Circignani殉道图像在说教意图和形式层面的影响、S. Vitale“牧歌式”酷刑图像的拟古风格解释；后者明确作为Buser的猜测，不写成已证实的创作意图。记录Haskell对Enggass论述的补充、其从沉默推断Enggass看法并承认其判断，以及Lavin支持学者否定Lanckorońska关于Gaulli《基督之血》图稿作为Gesù穹顶备选方案的理论。Haskell明确撤回耶稣会因Quietism拒绝该主题的旧假说。人物、作品、地点、术语和文献候选均保留身份或出版信息未定状态；跨章Lanckorońska及图稿论述回链第3章既有脚注statement，留身份问题给S3。

页图校读不改S0：L43 `osan important`→`of an important`、`Dusseldorf`→`Düsseldorf`、`Sangue dt Cristo`→`Sangue di Cristo`。脚注1–3在规范脚注段L225核为Buser、Enggass 1964、Lavin 1972 pp.169–171；正文statement已连到脚注段`l211-280`，但脚注全文仍queued，未标作已读。

受控迁移脚本`chp20_p399_s2_migration.py`校验来源及段哈希、前置覆盖状态、候选自然键、精确提及跨度、statement原句和跨段引用。预检发现跨页短语`a persuasive paper`不可整段锚定在p.399，改为本页原词`paper`并保留p.398已有提及；另按S0原OCR保留`dt`及破折号后空格，印本校正写入statement。dry-run通过后新增14个候选、49条提及及9条statement，闭合p.398并将p.398、p.399转为complete；恢复副本后缀`.bak-s2-chp20-p399-20261004`。首次全表审计发现三个未单列的`Jesuits`机构提及（其中一处嵌套在文章提及内），随后按段哈希及精确偏移追加3条mention，恢复副本为`mentions.csv.bak-s2-chp20-p399-mention-repair-20261004`。

最终`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全书832段中569 complete、120有理由排除、143 queued、0 partial；候选10,917、提及25,138、statement 10,968。第20章候选表面扫描覆盖4个已审段，未覆盖跨度0（仅为启发式提示，不代表召回率或语义验收）。当前游标按印本顺序移至p.400 `chp-20:20_CHP-20Postscript:l46-57`；后记脚注段`l211-280`、后记余下正文以及书目和索引仍待处理。

## 第二版后记印刷页400（2026-10-04）

按`CHP-20Postscript.pdf`物理页5核对规范段`chp-20:20_CHP-20Postscript:l46-57`。记录Enggass关于Gesù圣依纳爵祭坛的文章及罗马十八世纪雕塑著作、Théodon与Legros雕塑；Casale对Ottonelli—Pietro da Cortona绘画与雕塑论著版本及审查意见的研究；Hess关于Chiesa Nuova早期建筑与礼拜堂赞助人装饰自主性的材料；Cardinal Cesi自我克制、1581年致无名Oratorian的信、Bonadonna Russo对书信和Longhi任命的转述，以及Monsignor Angelo Cesi的另一种赞助风格。后记“Chapter 4”是更新小标题，不改变来源归属。

继续记录Cassiano dal Pozzo家族1689、1695年藏品目录的未出版发现、目录所录法国绘画、Cassiano 1626年西行及两幅不同的失佚肖像。原文未明确将两份目录逐一对应到两位藏家，保持合并描述；Cardinal Barberini身份未定。有关Cassiano日记的末句在“the”处跨到p.401，生成开放statement并将本段标为`partial`。脚注1–8回链到仍queued的注释段`l211-280`；印页p.400脚注9–10在L57转录并连接相应候选。

受控脚本`chp20_p400_s2_migration.py`首次dry-run揭示需修正的来源跨度：重复登记了原文未出现的第二个“Enggass”、OCR字面`kra book`与印本读数`a book`混用、Hess及书信引文锚点偏移、跨行人名和跨行肖像归属。脚本已按S0原文校正提及字面与行锚点；印本校读保留在statement的校勘说明内。dry-run通过后应用，新增23个候选、54条提及、10条statement；恢复副本后缀`.bak-s2-chp20-p400-20261004`。

写入后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；832段中569 complete、120有理由排除、142 queued、1 partial；候选10,940、提及25,192、statement 10,978。第20章候选表面扫描覆盖5段，未覆盖跨度0；该启发式扫描不代表召回率或语义验收。

页序复核发现规范源L59–67是PDF物理页6的Plate 65图版说明，不是印刷页401正文；p.401在PDF物理页10、规范源L81–96，续句以“Escorial has been published in full”起。已用`chp20_p400_continuation_repair.py`经dry-run后改正开放statement的`continues_in_segment`，恢复副本为`book-statements.jsonl.bak-s2-chp20-p400-continuation-repair-20261004`。按源文件顺序，下一段先处理Plate 65说明`chp-20:20_CHP-20Postscript:l59-67`，再处理Plate 66–68说明，之后由p.401 L81–96闭合句子。

## 第二版后记Plate 65图版说明（2026-10-04）

规范段`chp-20:20_CHP-20Postscript:l59-67`对应PDF物理页6。页图和PDF文本层可读出Plate 65a为Mola与Simonelli的双人讽刺像，Plate 65b为Masucci描绘Mola为教宗Alexander VII作肖像。Markdown OCR因竖排文字而逆序、拆分名称；保留S0原文，mentions锚定原始OCR碎片，statement的`ocr_corrections`给出校正后的完整图注。复用Mola `cand-1676`、Simonelli `cand-2434`及Pope Alexander VII `cand-0665`；新增两件未充分识别的作品候选及Agostino Masucci人物候选。没有推断肖像完成/存世、作品日期、媒材或保管地。

受控脚本`chp20_plate65_s2_migration.py`校验PDF与S0哈希、覆盖游标、自然键、精确提及跨度、候选外键及statement引用。dry-run通过后新增4个候选、12条提及、3条statement，恢复副本后缀`.bak-s2-chp20-plate65-20261004`。写后`audit_tables.py --summary`为`errors=[]`、`s2_missing=[]`；832段中570 complete、120 excluded、141 queued、1 partial，候选10,944、提及25,204、statement 10,981。第20章候选表面扫描覆盖6段，未覆盖跨度0（启发式检查，不等同于召回率/语义验收）。下一源段为Plate 66说明`chp-20:20_CHP-20Postscript:l69-70`。

## 第二版后记Plate 66（2026-10-04）

规范段`chp-20:20_CHP-20Postscript:l69-70`对应PDF物理页7。页图确认图注为“Baldassare Franceschini: Fame carrying the name of Louis XIV to the Temple of Immortality”。复用第7章已登记作品`cand-6888`、Baldassare Franceschini主条目`cand-1066`、Louis XIV及书前图版目录中的Fame和寓意场景候选；与第7章委托记述交叉回链，不重复创建作品或候选。

受控脚本`chp20_plate66_s2_migration.py`预检输入哈希、前置段状态、候选外键、精确跨度和跨章statement引用。dry-run通过后新增5条提及、1条statement，恢复副本后缀`.bak-s2-chp20-plate66-20261004`。复核`audit_tables.py --summary`为`errors=[]`、`s2_missing=[]`；832段中571 complete、120 excluded、140 queued、1 partial，候选10,944、提及25,209、statement 10,982。第20章候选表面扫描覆盖7段，未覆盖跨度0。下一源段为Plate 67说明`chp-20:20_CHP-20Postscript:l72-76`。

## 第二版后记Plate 67（2026-10-04）

规范段`chp-20:20_CHP-20Postscript:l72-76`对应PDF物理页8。页图和PDF文本层确认图注为“G. M. Crespi: Jupiter handed over by Cybele to the Corybantes to be fed”。复用第8章已登记的Crespi主候选`cand-0871`、图版索引作品候选`cand-0879`及Jupiter、Cybele、Corybantes候选；回链第8章关于选题、草图和后改题为《The Finding of Moses》的叙述，不把两个来源产生的作品候选预先合并。

受控脚本`chp20_plate67_s2_migration.py`预检来源哈希、覆盖顺序、精确原始OCR片段、候选外键及第8章statement引用。dry-run通过后新增7条提及、1条statement，无新增候选；恢复副本后缀`.bak-s2-chp20-plate67-20261004`。表审计`errors=[]`、`s2_missing=[]`；全书572 complete、120 excluded、139 queued、1 partial，候选10,944、提及25,216、statement 10,983。候选表面扫描覆盖8段，未覆盖跨度0。下一段Plate 68：`chp-20:20_CHP-20Postscript:l78-79`。

## 第二版后记Plate 68（2026-10-04）

规范段`chp-20:20_CHP-20Postscript:l78-79`对应PDF物理页9。图注a为Francesco Maggiotto的三幅总督肖像，复用书前图版目录的Plate68a作品候选`cand-4190`，保持其与另一个168幅肖像组`cand-3352`的关系未定。图注b识别一幅Leonardis据Tiepolo作品制作的版画《Maecenas presenting the Arts to Augustus》；另登记底稿构想与版画两件作品，并把姓氏Tiepolo及Leonardis保持为身份未决。Maecenas、Arts和Augustus沿用前置图版目录候选；图题不作为历史事件证据。

受控脚本`chp20_plate68_s2_migration.py`预检输入哈希、前置状态、候选自然键、精确提及跨度及图版目录引用。dry-run通过后新增4个候选、9条提及、4条statement，恢复副本后缀`.bak-s2-chp20-plate68-20261004`。审计`errors=[]`、`s2_missing=[]`；全书573 complete、120 excluded、138 queued、1 partial，候选10,948、提及25,225、statement 10,987。第20章候选表面扫描覆盖9段，未覆盖跨度0。下一段为印刷页401 `chp-20:20_CHP-20Postscript:l81-96`，将闭合p.400跨页句，并处理Bernini胸像归属等更新。

另核对`02-sources/02-Markdown`中的101个Markdown文件与`segments.jsonl`登记的79个来源文件：17个整章副本未纳入分节规范来源；另有5个旧版后部材料`*_intro.md`未登记。后者不删除，须在S2交接审计前与规范分节文件及页图核对，确认没有独有印本文本后才能结束来源范围核查。

## 第二版后记印刷页401（2026-10-04）

按`CHP-20Postscript.pdf`物理页10核对规范段`chp-20:20_CHP-20Postscript:l81-96`，并以S0登记的页段哈希确认输入未变。该页L82闭合p.400“the”后的Cassiano日记出版范围句，目的地为Escorial；更新原开放statement并将p.400、p.401均转为complete。脚注1–8的具体书目文字分别链接至待处理注释段L231–234，不因页图可见就标作已完成脚注审读。

记录Cassiano对Escorial所藏Titian绘画及墨西哥植物、鸟类图稿的兴趣；报告1664年他曾考虑把Poussin《七圣礼》赠给一位无名友人，但保留Haskell对“可能不喜欢Poussin严峻风格”的推测和“考虑赠送”不等于实际转让。新收集的Paolo Giordano II Orsini胸像依原文区分Humphris持有的版本与Plymouth版本；Wittkower的Bernini归属以“提出”登记，Haskell随后转述其理解的文献反证，未将归属争论裁定为独立事实。Simonelli—Mola双人讽刺像沿用Plate 65a作品候选；本页补足“Mola是Simonelli的朋友”，关系作为书内候选而非正式边。

第6章更新分别记录Haskell对罗马经济史研究不足的判断、Petrocchi参考、Doria-Pamphili档案文件于1972年出版、Alexander VII日记摘录中的简短艺术评论及Bernini常访，以及编者对教宗建筑规划决策权的限定转述；“apparently felt”原样保留。另记录Clement IX赞助Bernini与Ponte S. Angelo装饰研究的关系，脚注8仍待核。页图确认印本为“Garms”“Niccolò”“to be”；S0 OCR原样保留，三处校正写在statement。候选表面扫描发现“Duke of Bracciano”此前未映射，增加对独立索引候选`cand-3479`的精确提及，不与Paolo候选预先合并，留待S3。

受控脚本`chp20_p401_s2_migration.py`按源/PDF哈希、S0段哈希、候选自然键、精确跨度、候选外键和statement原句预检；dry-run后写入并为四张表保存恢复副本`.bak-s2-chp20-p401-20261004`。随后只读表面检查提示标题候选一条漏挂，`chp20_p401_title_mention_repair.py`再次dry-run后追加1条mention并备份mentions与statements。净变更为12候选、35提及、13 statements；未写外部核验结论。

最终`python -X utf8 scripts/audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全书832段中575 complete、120有理由排除、137 queued、0 partial，候选10,960、提及25,260、statement 11,000。第20章表面扫描覆盖10个已审段，未覆盖跨度为0；这是已登记候选名的启发式提示，不代表召回率或语义验收。仍有两条既存enrichment source引用警告和语义质量待审提示。下一源段为印刷页402：`chp-20:20_CHP-20Postscript:l98-108`。

## 第二版后记印刷页402（2026-10-04）

按`CHP-20Postscript.pdf`物理页11核对规范段`chp-20:20_CHP-20Postscript:l98-108`和登记段哈希。记录Queen Christina在罗马的生活与艺术赞助、1966年Council of Europe Stockholm展览及其目录/相关出版物；Bellori新研究、Previtali新版序言，以及Haskell转述Turner关于Bellori评论Lanfranco受Ferrante Carlo影响的发现；第7章意大利化欧洲文化主题的范围说明；Perez Sanchez、Wethey有关西班牙赞助与那不勒斯总督研究的更新；Mazarin在Richelieu时期及其掌权时期引入意大利巴洛克艺术家/作品的政策，以及Haskell对Laurain-Portemer研究的转述；末段关于年轻Louis XIV和Alazard受委托绘画的句子续到p.403。每项学术判断保留为Haskell对文献的报告，不标记为已独立阅读外部著作。

按扫描页保留“a related volume or studies and documents”的现有读法；字形与语义不足以确认应为“of”，不以语法猜测校正。页图校正记录Queen Christinas→Queen Christina's、`Mme .LaurainPortemer`→`Mme Laurain-Portemer`、脚注5 OCR序号6→5；S0原文不改。正文脚注1–7分别回链到queued注释段L235–238，脚注全文未审。最后一句在“a picture commissioned”处开放，跨页续文为p.403 L110–121，因此p.402记`reviewed/partial`。

受控迁移`chp20_p402_s2_migration.py`核对源/PDF/S0哈希、页段前置状态、候选自然键、精确提及跨度、原句、外键及跨页/脚注链接；dry-run后初写17个候选、38条提及和9条statement，备份后缀`.bak-s2-chp20-p402-20261004`。表面定位器发现现有Italian art候选`cand-4131`在L106有一处未登记提及；`chp20_p402_mention_repair.py`经dry-run后追加提及并把候选加入Mazarin statement，备份后缀`.bak-s2-chp20-p402-mention-repair-20261004`。语义复核将`cand-10986`规范为通用term“Italian Baroque artists”，删除不可独立识别的未具名作品群候选`cand-10987`及冗余提及，并将Turner报告的断言端点改为Bellori与Ferrante Carlo；修订经`chp20_p402_semantic_refinement.py` dry-run后写入，备份后缀`.bak-s2-chp20-p402-semantic-refinement-20261004`。p.402最终净增16个候选、38条提及和9条statement。第20章表面扫描覆盖11段，未覆盖跨度0；仅为启发式提示，不证明召回率或语义验收。

最终`python -X utf8 scripts/audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全书832段中575 complete、120有理由排除、136 queued、1 partial，候选10,976、提及25,298、statement 11,009。既存两条enrichment source引用无法解析警告仍在。下一规范段为印刷页403：`chp-20:20_CHP-20Postscript:l110-121`。

## 第二版后记印刷页403（2026-10-04）

按`CHP-20Postscript.pdf`物理页12核对规范段`chp-20:20_CHP-20Postscript:l110-121`及S0哈希。L111–113闭合p.402关于Alazard所述受委托绘画的句子：作品经Colbert与Abate Luigi Strozzi（原文括号中的中介）委托Baldassare Franceschini、il Volterrano创作；印本标题为《Fame Carrying the Name of the King to the Temple of Immortality》，即既有Plate 66作品`cand-6888`。Haskell称作品当时仍在Versailles，并报告Pierre Rosenberg已识别、发表该作。原文没有点名委托者，未把Louis XIV、Colbert或Strozzi写成委托人；“still at Versailles”仅记录第二版后记写作时的说法，不代表当前馆藏核验。

L114保留Haskell对Liechtenstein亲王及Prince Eugene收藏研究的更新；前者未给个人名字，Lankheit仅姓氏，均保留独立候选供S3消歧。L115–116记录Michael Levey对英格兰王室意大利绘画赞助的概述、Croft-Murray对Antonio Verrio职业的研究以及Sir Thomas Isham展览和目录；保留surname-only的Croft-Murray为单独候选，不与p.284候选提前合并。L118–121记录佛罗伦萨十七世纪艺术重估、纽约1969/佛罗伦萨1965与1974/伦敦1979展览、Haskell自述此前低估该艺术质量、Medici赞助研究、1969年`Artisti alla Corte Granducale`展览和Marco Chiarini目录，以及Malcolm Campbell关于Ferdinand II于1637年聘用Pietro da Cortona装饰Palazzo Pitti之决定的研究。展览无正式题名处只用描述性事件候选，不补造标题；Campbell书中涉及Barberini与Sacchetti赞助的范围和学术归属均保留。

L120–121经页图校读记录`alia`→`alla`、`Ferdinand Il`→`Ferdinand II`、`Pietroda`→`Pietro da`及`was-provided b/The exhibition`→`was provided by the exhibition`；L118 `sine`→`since`；L112标题`os`→`of`。校正只进statement，不改S0。L116 `exhibition.of`的点状标记仍有歧义，未擅改为逗号。p.403末句在“an”处未完，继续至p.404；Don Lorenzo与Ferdinand II的叔侄关系、Ferdinand II与Cardinal Leopoldo的兄弟关系，以及“挽救”佛罗伦萨文化的说法均保留为原书关系候选，不写入正式关系表。

正文脚注1–10分别回链注释源段L239–243，仍待该注释段完整审读；关联文献不标为独立查阅。受控脚本`chp20_p403_s2_migration.py`先dry-run核对源/PDF/段哈希、前置覆盖状态、候选自然键、提及精确跨度、statement锚点及p.404续句，再写入四表并留恢复副本`.bak-s2-chp20-p403-20261004`。净增28个候选、63条提及和13条statement，同时删除唯一的p.402临时占位候选`cand-10994`，将其提及与statement改指`cand-6888`；p.402转`reviewed/complete`，p.403转`reviewed/partial`。首次全表审计发现28个新候选来源引用使用了不支持的行范围格式；按审计契约修正为精确`segment#Lline`并留副本`.bak-s2-chp20-p403-source-ref-repair-20261004`。之后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，全书576 complete、120有理由排除、135 queued、1 partial，候选11,003、提及25,361、statement 11,022；两条既存enrichment source引用警告仍在。第20章候选表面扫描覆盖12个已审段，未覆盖跨度为0；此启发式结果不代表召回率、准确率或语义验收。下一段为p.404 `chp-20:20_CHP-20Postscript:l123-135`。

## 第二版后记印刷页404（2026-10-04）

按`CHP-20Postscript.pdf`物理页13核对规范段`chp-20:20_CHP-20Postscript:l123-135`和S0哈希。L123–125从p.403“an”续为“an exhibition”，再列举增加对Cardinal Leopoldo品味认识的展览和Procaccis、Muraro、Meloni、Chiarini de Anna、Bandera文章；Haskell另称Prinz分析了Uffizi自画像画廊的形成。复用p.403的Ferdinand II、Cardinal Leopoldo、Klaus Lankheit和Florence候选；Uffizi自画像画廊保持类型待决，不把馆藏与物理展厅合并。

L126记录Lankheit对Cosimo III角色的重新评价，以及Haskell称1974年在Florence和Detroit连续举办的晚期巴洛克展览使此点明确。Stella Rudolph的解释被单独归属：其文章以`stile Cosimo III`为题之一，讨论佛罗伦萨省域文化复兴、罗马衰落与当地贵族家族的赞助。L127–131记录Chiarini与Strocchi出版的Ferdinand inventories；Haskell称材料证明Grand Prince Ferdinand雇用了Alessandro Magnasco，同时“才能应当与Prince相合”保留为作者推断，并保留Guelfi强调这是一项有限赞助的限定。展览史著作称Prince参与1706展览组织，而1705展览目录使Haskell修正其关于Prince开创此类展览活动的早期看法；两场活动分开记录。Gabbiani在Pitti的多幅作品清理及Chiarini、Ewald相关研究促使Haskell修正对画家及Prince鉴赏力的评价，但不捏造具体作品。

L132–133记录Del Rosso兄弟在更广语境中的研究，Silvia Meloni对Luca Giordano佛罗伦萨活动的讨论，以及她辨认兄弟所藏多件画作；原文不称这些画都出自Giordano。L134–135记录Raimondo Buonaccorsi赞助、`Gallery of the Aeneid`至早期1960年代几乎完整存续、1967年被Comune of Macerata购得，而最好的若干画作此前已散佚。将Comune记作institution、Macerata记作place；画廊/收藏/装饰作品整体的边界以及未具名散佚作品仍待核，不与既有单件作品候选合并。

页图校正只写入statement：L131 OCR `seventeenthand eighteenthcentury`恢复为`seventeenth- and eighteenth-century`；L135 `Macerara`校正为`Macerata`。本页脚注1–19映射至notes源段L244–253，仍queued、未作为已读引文使用。页图可见的注号与S0脚注OCR标签有冲突，待注释段处理时一并核正：p.403正文Croft-Murray标号为5而S0注释L241读作8；p.404正文Meloni为4、Chiarini de Anna为5、Bandera为6，而S0注释L245–246对应标号有OCR误读。未改写S0注释。

受控脚本`chp20_p404_s2_migration.py`核对PDF/源/S0哈希、p.403未闭合statement、候选自然键、提及精确跨度、statement原句、脚注和跨页映射；dry-run后写四表并保留`.bak-s2-chp20-p404-20261004`恢复副本。新增35个候选、62条提及和10条statement；p.403及p.404均转`reviewed/complete`。`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；832段中578 complete、120有理由排除、134 queued、0 partial，候选11,038、提及25,423、statement 11,032。仍有两条既存enrichment来源引用警告。第20章候选表面扫描覆盖13段、未覆盖跨度0；该启发式扫描不是召回率或语义验收。下一段为p.405 `chp-20:20_CHP-20Postscript:l137-148`。

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


## 第二版后记印刷页407（2026-10-04）

按`CHP-20Postscript.pdf`物理页16核读p.407，闭合p.406末尾Jeffrey Daniels的跨页句。记录Daniels反对把Smith的大幅Sebastiano Ricci画作解释为失败委托的派生物；他认为没有理由否认Smith是该组画的原始委托者。此处保留为学术分歧，不与Smith 1770年“second collection”问题混并。另将Smith与Canaletto的财务安排记录为Haskell明确称细节不清。

记录Constable在Links隐含支持下对Smith与Canaletto、或Canaletto单独于1740年代初赴罗马的怀疑，并链接第10章p.307旧说；该旅程不是已确认事件。Levey研究称Canaletto于1751年改动一幅约早16年为Smith所作的威尼斯景观，加入Smith大运河宫邸新立面的描绘；画名、肖像对象及更精确日期均未给出。Smith宅邸的Palladian overdoors及Barcham研究单独登记。

记录Binion对Schulenburg收藏趣味的评估及Haskell以芝加哥、科隆两件Piazzetta牧歌画回应的论证，保留两幅画的群组层级并链接第10章p.314；不把Haskell的评价写成已独立证实的结论。Rossi关于“minor genres”、地方画派及Schulenburg可能具有的收藏使命均作为经Haskell转述的学者解释，而非Schulenburg意图事实。

p.407脚注1–6回链queued注释L264–266。页图校正L165 `The precise, details`为`The precise details`，L172移除OCR误插入的句点；印刷脚注5为Binion、6为Rossi，S0注释L266 OCR把Binion序号读成8，留待注释段复核。启发式候选表面扫描提示本段第四处`Canaletto`（字符732–741）未登记；核对后补入人物候选`cand-0498`，新mention为`m-chp20-p407-046`。扫描器命中的`cand-0504`和`cand-0505`是同名索引下的两件作品，不是此处的人物；这次补录是正文人物提及，不是候选作品匹配。

受控脚本`chp20_p407_s2_migration.py`完成页面迁移，另由`chp20_p407_canaletto_mention_repair.py`在源文件、段哈希、目标跨度和mentions表哈希均匹配后补漏，备份为`.bak-s2-chp20-p407-canaletto-mention-20261004`。p.407新增14个候选、46条提及和8条statement，p.406、p.407均为`reviewed/complete`。审计`errors=[]`、`s2_missing=[]`；全书581 complete、120 excluded、131 queued、0 partial，候选11,087、提及25,582、statement 11,062。第20章候选表面扫描覆盖16段、未覆盖跨度0；这是启发式定位检查，不代表召回率或语义验收。下一段为p.408 `chp-20:20_CHP-20Postscript:l174-185`。


## 第二版后记印刷页408（2026-10-04）

按`CHP-20Postscript.pdf`物理页17核读p.408。记录Haskell对“Venetian Enlightenment”一词使用范围的自我限定、Venturi与Torcellan相关研究，以及自1963年以来对文中若干人物思想/赞助活动的研究更新；原文没有在该句明确指出“two figures”的具体身份，因此不强行指定。Byam Shaw将Antonio Conti感兴趣的德国画家识别为Jakob Christoffel Le Blon；其新彩色印刷方法与Newton理论的关联和在英、意的影响均按Haskell转述保留，未作独立技术验证。

记录McCormick的Vassar College Art Gallery目录收录另一幅Boscarati寓意画、该画与Pisani就任Procuratore di S. Marco的游行路线及政治骚动的联系；未将未具名画强并入已登记的四幅Riviera委托画。Olivato接受Haskell关于这些画早年为他人所作、在游行路线出现更可能出于偶然而非蓄意挑衅的试探性解释；其对Boscarati审判证词的转述及Boscarati在Pisani失势后仍持颠覆性观点，分别作为嵌套来源/观点记录，不等同于已查阅审判记录或文章原文。

第13章补充Anton Maria Zanetti the Elder的350幅讽刺画册被发现并赠予Fondazione Giorgio Cini，以及Bettagno展览目录对Zanetti生平和交游圈的概述。Pinelli所藏Maggiotto总督肖像系列中至少六幅已重新发现；链接既有第13章p.340断言和Plate 68a三幅图像，但不把三幅插图等同于六幅。Parker所说肖像改编自版画、可能来自Piccino在Matina书中的版画保留为暂定，并因句子续至p.409而使本段和该statement保持partial。

页图校读：L177 OCR `oiLodoli`恢复为印刷`of Lodoli`；L178 `begji`恢复为`been`；L179 OCR `Le Bion`按印刷校为`Le Blon`。只在statement qualifiers中记录，不改写S0。脚注1–7回链queued注释L267–270；其出版物尚待注释及书目段处理。

候选复核发现新建的Le Blon行与索引候选`cand-1375`重复，故将2条提及及断言端点重映射至`cand-1375`，删除临时重复候选`cand-11111`。受控修复`chp20_p408_leblon_candidate_repair.py`经dry-run后应用，保留三表备份`.bak-s2-chp20-p408-leblon-reuse-20261004`。最终净增16个候选。受控脚本`chp20_p408_s2_migration.py`默认dry-run，校验来源/PDF/S0段哈希、相邻段状态、候选外键、提及精确跨度/嵌套和原句，再写四表并保留`.bak-s2-chp20-p408-20261004`。本段新增16个候选、43条提及、11条statement，状态`reviewed/partial`。审计`errors=[]`、`s2_missing=[]`；全书581 complete、120 excluded、130 queued、1 partial，候选11,103、提及25,625、statement 11,073。第20章候选表面扫描覆盖17段、未覆盖跨度0；该启发式检查不证明召回率或语义验收。下一段p.409 `chp-20:20_CHP-20Postscript:l187-199`。


## 第二版后记印刷页409（2026-10-04）

按CHP-20Postscript.pdf物理页18核对规范段chp-20:20_CHP-20Postscript:l187-199及S0源段哈希。L188闭合p.408 Parker句：Matina书中的版画实质上是截至1659年威尼斯各任总督的奖章肖像；复用已有Maggiotto总督肖像组及威尼斯候选。L190–193记录Da Pozzo的Algarotti论文校勘本与遗嘱全文出版、Mauro Tesi为Elder Pitt所作两幅画、Tiepolo赠Cosimo Mari的两件作品，以及柏林《赴髑髅地》稿本几乎可以确定是S. Alvise大型祭坛画草图。L194提到巴黎Musée Cognacq-Jay可能藏有《安东尼与克娄巴特拉宴饮》草图，但保留Haskell对身份判断的疑虑。L195–198记录Santifaller关于Algarotti肖像、Schmidt 1752年版画及Salimbeni 1753年蚀刻、Algarotti本人蚀刻与Tiepolo合作，以及Levey指出Tiepolo肖像理论源于误读文献；复用已登记人物/作品，不合并未确认的肖像版本。L199记录比萨Campo Santo的Algarotti墓画、可能取法Volpato版画、John Bryson在Oxford的1963年收藏及后来的Schloss Charlottenburg位置；归属句续至p.410 L201–202。

页图校正仅记入statement qualifiers：L188 OCR多出的点、L191 sarcastic^amusement、L198 a jnisreading分别据印本恢复为正常字词。正文脚注1–9回链queued注释段L271–275，书目核对和注释语义审读尚未完成。受控迁移chp20_p409_s2_migration.py默认dry-run，校验源/PDF/S0哈希、相邻覆盖状态、候选自然键、精确提及跨度、statement原句及外键；dry-run后新增22候选、52提及和12 statements，备份.bak-s2-chp20-p409-20261004。迁移将p.408标complete，p.409标partial。首次全表审计发现跨页statement把p.409行错误并入p.408锚点；受控修复chp20_p409_crosspage_statement_repair.py以dry-run确认后，把原书引文锚定回p.408 L185，并将p.409续页精确锚定为L188，备份.bak-s2-chp20-p409-crosspage-repair-20261004。最终audit_tables.py --summary为s2_missing=[]、errors=[]；全书582 complete、120有理由排除、129 queued、1 partial，候选11,125、提及25,677、statement 11,085。第20章候选表面扫描覆盖18段、未覆盖跨度0；该启发式结果不是召回率或语义验收。下一段为p.410 chp-20:20_CHP-20Postscript:l201-209。


## 第二版后记印刷页410（2026-10-04）

按CHP-20Postscript.pdf物理页19核对规范段chp-20:20_CHP-20Postscript:l201-209及S0段哈希。L202闭合p.409关于Santifaller所论Algarotti墓画的句子：早先作者及Santifaller将画归于Bernhard Rode；Marianne Roland-Michel研究后认为更可能出自某位意大利画家。将其作为相互竞争的学者判断记录，不接受任何一方为定论。L203说明书中所示为该画细部。L204为第16、17章标题，不建候选。L205–207记录Sasso与威尼斯学者/艺术家群体对北意大利早期绘画的重新发现、Christopher Lloyd将未完成的Venezia Pittrice置于复制意大利艺术的展览目录语境、Loredana Olivato关于Sasso的研究及其所引信件、Abate Della Lena的《The Spoliation of Pictures from Venice》及其关于共和国末期作品外流的叙述；复用Sasso、Olivato、Della Lena论著、Guardi、Carpaccio和Bellini等候选，新增缺少的具名对象，未将Abate Della Lena与此前Giacomo della Lena径行合并，Vivarini的个人/家族范围待S3。L208–209将Manfrin收藏的散佚置于19世纪威尼斯史中，称其曾包括Giorgione的Tempesta，指出藏品来源仍不清楚，并转述Vincenzo Fontana关于Manfrin烟草制造财富的研究。未把收藏另造为未经分类的KU，也不把作品在某收藏中等同于已证实的个人购藏关系。

页图校读确认注释L280印本注号为5，S0 OCR误识为6；仅在statement qualifiers中记录。脚注1–5分别回链queued注释L276–280，出版物和脚注正文尚未审读。受控迁移chp20_p410_s2_migration.py默认dry-run，核对源/PDF/S0哈希、p.409 partial与p.410 queued前态、候选自然键、精确提及跨度、statement原句及外键；新增10个候选、26条提及和11条statement，并将p.409、p.410转为complete，备份.bak-s2-chp20-p410-20261004。其后候选表面扫描发现p.410 L209“nineteenth-century Venice”漏挂；受控修复chp20_p410_venice_history_mention_repair.py dry-run后添加m-chp20-p410-027，备份.bak-s2-chp20-p410-venice-history-20261004。最终audit_tables.py --summary为s2_missing=[]、errors=[]；全书584 complete、120有理由排除、128 queued、0 partial，候选11,135、提及25,704、statement 11,096。第20章候选表面扫描覆盖19段，未覆盖跨度0；此启发式检查不证明召回率或语义验收。下一段为第二版后记注释chp-20:20_CHP-20Postscript:l211-280。

## 第二版后记正文—脚注回链审计（2026-10-04）

对照`CHP-20Postscript.pdf`物理页1–2及正文脚注标记，发现p.396–397既有23条statement均缺少到queued注释段的回链。受控修复`chp20_footnote_link_repair.py`逐项为18条带明确印本脚注标记的statement补入footnote refs：p.396注1–6映射L212–214；p.397注1–12映射L215–220。无脚注标记的正文断言未加链接；p.396开启、p.397闭合的Lavin引文只在注号实际出现的p.397闭合statement挂注1。另据p.409印本脚注栏确认注3“Da Pozzo”位于L272，修正3条既有statement的注3定位（原误指L271）。脚本核验规范Markdown与PDF哈希，默认dry-run；应用前备份`book-statements.jsonl.bak-s2-chp20-footnote-link-repair-20261004`。未改写原文引句或断言内容；注释段仍queued，所有正文脚注文本仍待逐条语义审读。应用后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`，覆盖状态及候选、提及、statement计数不变。页图同时确认p.397 OCR将L215的Lavin首字母误读、L223 Viola注号应为5、L237 Perez Sanchez应为5、L241 Croft-Murray应为5、L246 Chiarini de Anna/Bandera应为5/6、L266 Binion应为5、L271 Algarotti应为2、L280 Fontana应为5；校读将在注释段迁移中逐项记录，不改写S0。

## 第二版后记脚注p.396（2026-10-04）

逐条语义处理印刷p.396注1–6（规范源L212–214），并按页图复核注号、作者名和标点。注1–3、5–6分别记录Fagiolo dell’Arca与Carandini、Lavin、d’Onofrio、Longhi、Hibbard的短式引文；注4拆成Bellori 1976 p.224与Mancini I p.227两条书目定位。注释只证明Haskell在该处引用了这些文献，不据此补造题名、版本或引文内容，也不表示已独立查阅文献。复用已有作者/著作候选；只新增Bellori与Mancini两条带原文页码定位的archive候选，新增15条精确跨度mention和7条`footnote_cites_publication` statement（注4对应两条）。六条正文脚注statement现分别连接注释statement，`footnote_text_pending`解除；p.396开启、p.397闭合的Lavin引文仍只由p.397实际注号连接。

受控脚本`chp20_notes_p396_migration.py`核对规范Markdown与PDF SHA-256、迁移前表计数、自然键、精确mention跨度、statement引句、候选外键和既有脚注回链；dry-run通过后应用，四表均保留`.bak-s2-chp20-notes-p396-20261004`恢复副本。注释段`chp-20:20_CHP-20Postscript:l211-280`更新为`reviewed/partial`，覆盖L212–214；L215–280仍未处理。应用后全表审计为`s2_missing=[]`、`errors=[]`，584 complete、120 excluded、127 queued、1 partial；候选11,137、提及25,719、statement 11,103。剩余两条enrichment来源引用警告与本次无关；表覆盖完整性仍不等同于语义质量独立验收。

## 第二版后记脚注p.397（2026-10-04）

逐条处理印刷p.397注1–12（规范源L215–220），并以PDF物理页2核对注号与短式引文。记录Lavin 1968、Hibbard 1973、Dubon、Barberini 1968、Harris、Poirier、Garas 1967、Heikamp、Frommel、Kirwin、Spezzaferro及Posner 1971对应的书目候选；均复用正文处理时已登记的publication与作者候选，不补造短注未提供的题名、版本或页码，也不声称已独立查阅。每条建立`footnote_cites_publication` statement并连接对应正文statement；注释候选对作者身份保留原有状态。citation和author若落在完全相同的短文本跨度，只保留publication mention，并在statement的`mentioned_candidate_ids`中保留作者候选，避免把同一字串记成两条提及。最终新增12条publication mention、6条独立author mention和12条note statement；12条正文脚注的`footnote_text_pending`均解除。

页图校正：L215印本为“Lavin, I., 1968”，规范OCR行读作“Lavin, L, 1968”；校读只记入statement的`ocr_corrections`与限定，不修改S0。首次全表审计发现6组完全相同跨度的重复mention；受控修复`chp20_notes_p397_overlap_repair.py`默认dry-run核验来源/PDF哈希、精确跨度和唯一对应publication mention后，删除重复作者跨度，保留archive引用mention及statement作者映射，备份`mentions.csv.bak-s2-chp20-p397-overlap-repair-20261004`。最终审计`s2_missing=[]`、`errors=[]`，覆盖584 complete、120 excluded、127 queued、1 partial；候选11,137、提及25,737、statement 11,115。注释段覆盖推进至L212–220并仍为partial；下一段p.398注释从L221开始。

## 第二版后记脚注p.398（2026-10-04）

逐条处理印刷p.398注1–7（规范源L221–224），核对PDF物理页3。注1、2分别引用d’Onofrio 1963、1964；注3引用Battisti 1962及其两组页码；注4为Whitfield；注5为Viola；注6为Baschet；注7为Wittkower与Jaffé。除注7的Jaffé作者候选外，出版物和作者候选均复用p.398正文既有候选；短注缺少的题名、版本、日期不补造。新增一条Jaffé姓氏级person候选`cand-11159`，身份及其在文献中的作者/编者角色仍待书目证据，不与先前不同定位的Jaffé archive候选合并。注7引用所指精确文献也待书目处理。新增7条publication mention、5条非重复author mention、7条`footnote_cites_publication` statement；注2连接两条正文statement，注7连接Fordham symposium及Wittkower观点两条statement。

页图校读：S0 L223将注5 Viola误读为注6；印本为5 Viola、6 Baschet。L224印本拼写Jaffé，S0漏重音。两处均保留S0原读法，只在statement的`ocr_corrections`记录。脚注候选身份限定不作跨章裁决。脚本`chp20_notes_p398_migration.py`默认dry-run，核验源/PDF哈希、表前态、候选自然键、提及跨度、原句、外键和正文回链；应用后留四表备份`.bak-s2-chp20-notes-p398-20261004`。审计`s2_missing=[]`、`errors=[]`；全书584 complete、120 excluded、127 queued、1 partial，候选11,138、提及25,749、statement 11,122。注释段覆盖L212–224，保持partial；下一段p.399注释从L225开始。

## 第二版后记脚注p.399（2026-10-04）

逐条处理印刷p.399注1–3（规范源L225），并核对PDF物理页4。注1为Buser，注2为Enggass 1964，注3为Lavin I. 1972 pp.169–71；均复用页面正文已有publication与作者候选，不补造短注未提供的题名或版本。三条note statement按标记连接p.399正文：注1连到Buser对“Jesuit art”质疑及其相关段落的三条statement，注2连到Enggass专著的两条statement，注3连到Lavin对Bernini/Gesu圆顶素描理论的statement。Buser短注的人名与文献跨度完全相同，只保留publication mention，在statement中保留作者候选，避免重复跨度。最终新增3条publication mention、2条独立author mention、3条`footnote_cites_publication` statement；正文回链全部解除pending。

受控脚本`chp20_notes_p399_migration.py`默认dry-run，核对规范Markdown/PDF哈希、迁移前表计数、候选外键、精确跨度、原句及脚注回链；应用后为三表保留`.bak-s2-chp20-notes-p399-20261004`。审计`s2_missing=[]`、`errors=[]`；全书584 complete、120 excluded、127 queued、1 partial，候选11,138、提及25,754、statement 11,125。注释段覆盖推进至L212–225，仍为partial；下一页p.400注释从L226开始。

## 第二版后记脚注p.400（2026-10-04）

对照印刷p.400与PDF物理页5处理规范注释L226–230的脚注1–8。注1、2为Enggass 1974和1976文献，注3为Ottonelli与Berrettini的《Trattato》，注4为Casale关于审查意见的研究，注5为Hess 1963研究，注6为Bonadonna Russo 1968 p.135，注7为其1967与1968年文献，注8为Brejon p.94注21。短注书名与版本信息不足处明确待书目核对；不补造信息，不声称独立查阅。

注8除引用定位外，还说所涉文件于1969年由Marcello del Piazzo发现；单独登记为带出处限定的关系候选，新增Marcello姓氏全名级未决person候选，不把注释报告误写成独立核证。p.400注9（Brejon）与注10（Harris, 1970）已由p.400正文迁移记录在规范源L57，本次不重复转录。页图校正L226 OCR“LnAALSS”→印本“Enggass”，L228“p.13 5”→“p.135”；仅记入`ocr_corrections`，不改S0。短式引文与作者跨度完全相同处只记publication mention，作者候选保留在statement的`mentioned_candidate_ids`；注1 OCR无法读出作者姓名，借助正文语境链接Enggass候选，不伪造note作者mention。

受控脚本`chp20_notes_p400_migration.py`默认dry-run，核对源/PDF哈希、表前态、候选自然键、提及跨度、statement锚点/外键、正文回链及注8双层内容；应用前备份四表`.bak-s2-chp20-notes-p400-20261004`。新增5个候选、17条精确提及、9条statement；注1–8正文链接解除pending，注9–10既有链接保持不变。应用后审计`s2_missing=[]`、`errors=[]`；全书584 complete、120 excluded、127 queued、1 partial；候选11,143、提及25,771、statement 11,134。注释段推进至L212–230并保持partial；下一段p.401注释L231–234。

## 第二版后记脚注p.401（2026-10-04）

对照印刷p.401与PDF物理页10处理注1–8（规范源L231–234），并逐条核对正文脚注锚点。注1为Harris与de Andrés所引Cassiano赴埃斯科里亚尔记录，作者和出版物完整身份待书目核对；注2为Pierre du Colombier短引；注3为Wittkower 1966；注4拆记Radcliffe 1978与Sotheby’s 1979两项不同引文；注5为Petrocchi 1970 p.158；注6为Garms关于Doria-Pamphili文件的出版物；注7复用正文的Alexander VII日记摘录候选，作者/编者记作Krautheimer与Jones；注8复用正文Clement IX研究候选并记录Weil姓氏。短引缺失的题名、版本和人物全名不补造；Harris、de Andrés、Garms、Krautheimer、Jones、Weil等身份问题保留给书目核对及S3。

本页新增14个候选（7项引文对象、7个人物候选）、17条精确提及、9条`footnote_cites_publication` statement；注4分为两条出版物引用statement，注7连接两条正文statement，共解除9个正文脚注的pending。页图确认S0 L231“de Andres”印为“de Andrés”、L233“Garrns”印为“Garms”；原转录不改，校读写入对应注释statement。将先前误附在Doria-Pamphili正文statement上的Garms校读移至注6。首次apply后审计发现新statement未落入JSONL，遂从本轮四表备份恢复原态，修正脚本追加逻辑，再次dry-run及apply；恢复副本保留为`.bak-s2-chp20-notes-p401-20261004`。最终全表审计`s2_missing=[]`、`errors=[]`；候选11,157、提及25,788、statement 11,143，覆盖584 complete、120 excluded、127 queued、1 partial。注释段推进至L212–234并保持partial，下一段为p.402注释L235–238。


## 第二版后记脚注p.402（2026-10-04）

对照印刷p.402与PDF物理页11处理注1–7（规范源L235–238），逐条检查正文引注。注1复用1966年斯德哥尔摩展览目录候选`cand-10979`；注2复用相关出版物候选`cand-10980`并新增姓氏形式Von Platen；注3复用Bellori《Lives》新校勘版候选`cand-10981`，短引为Bellori 1976；注4复用Nicholas Turner及其研究发现候选；注5复用Perez Sanchez目录及作者候选；注6新增Wethey出版物定位候选并复用姓氏级作者；注7复用Laurain-Portemer文章组候选和作者，保留“另附相关论文目录”的注释信息。未给出的题名、年份和作者全名不补造。

新增2个候选、9条提及和7条`footnote_cites_publication` statement；注1、2共用同一正文statement，注7连接两条正文statement，共解除8个正文marker链接的pending。印本注5在S0 L237误读为注6；将校正“6 Perez Sanchez”→“5 Perez Sanchez”从正文断言移到脚注5 statement，保留S0。受控脚本`chp20_notes_p402_migration.py`核对来源/PDF哈希、迁移前计数、候选外键、精确跨度、原句和正文marker回链，dry-run通过后apply，并留四表恢复备份`.bak-s2-chp20-notes-p402-20261004`。最终审计`s2_missing=[]`、`errors=[]`；候选11,159、提及25,797、statement 11,150；全书覆盖584 complete、120 excluded、127 queued、1 partial。注释段覆盖到L238并保持partial，下一页p.403注释L239–243。

## 第二版后记脚注p.403（2026-10-04）

对照印刷p.403与PDF物理页12处理注1–10（规范源L239–243），连接Rosenberg、Lankheit、Eugen/Prinz、Levey、Croft-Murray、Sir Thomas Isham、Chiarini、Campbell 1966/1977及Borea各项引文。复用正文已建的作品、人物和出版物候选；为正文没有精确书目对象的Rosenberg、Lankheit、Eugen/Prinz分别新增引文候选，未补造题名、版本或Eugen/Prinz究竟属于书名还是作者形式。Campbell 1966与1977分开记录；后者的作者身份复用Malcolm Campbell候选。

新增3候选、16条提及、10条`footnote_cites_publication` statement，连接10个正文marker（marker 8、9连接同一正文statement）。PDF页图显示印本注5为Croft-Murray；S0 L241 OCR误作8，校正放在注5 statement且不改S0。受控脚本`chp20_notes_p403_migration.py`默认dry-run，核验来源/PDF哈希、表前态、引文跨度、外键与正文marker；apply后留恢复备份`.bak-s2-chp20-notes-p403-20261004`。审计`s2_missing=[]`、`errors=[]`；候选11,162、提及25,813、statement 11,160；覆盖584 complete、120 excluded、127 queued、1 partial。注释段推进至L239–243，下一段p.404注释L244–253。

## 第二版后记脚注p.404（2026-10-04）

对照印刷p.404与PDF物理页13处理注1–19（规范源L244–253），按注号连接正文关于Cardinal Leopoldo文献、Prinz、Lankheit、Florence/Detroit展览、Rudolph研究、Ferdinand二世及Uffizi、Gabbiani、Del Rosso与Buonaccorsi等statement。复用正文现有的archive/person候选；新增缺失的展览目录、Procacci两位具名作者、Muraro 1965、Meloni Trkulja 1975/1972、Lankheit、Rudolph 1971/1973、Strocchi、Borroni Salvadori作者及《Urbino: Restauri》等引用候选。区分出版物、作者、展览事件和作品对象；Meloni Trkulja可能与正文Silvia Meloni对应但暂不合并。注10同一短注列1971与1973两项，拆成两个出版物candidate和statement并共用marker10；注15与18先复用同一1972引文候选，待书目核实。

新增15候选、32条精确提及、20条`footnote_cites_publication` statement；注1–19连接19个正文marker。页图确认印本注5为Chiarini de Anna、注6为Bandera，S0分别误读为6和8；两项校读放入注释statement，不改S0。脚本`chp20_notes_p404_migration.py`核对来源/PDF哈希、表前计数、每条body marker、候选类型、精确跨度和note quote；dry-run通过后apply，四表保留`.bak-s2-chp20-notes-p404-20261004`。最终审计`s2_missing=[]`、`errors=[]`；候选11,177、提及25,845、statement 11,180；覆盖584 complete、120 excluded、127 queued、1 partial。注释段推进至L244–253，下一段p.405注释L254–258。

## 第二版后记脚注p.405（2026-10-04）

对照`CHP-20Postscript.pdf`物理页14逐项核读印刷p.405脚注1–9（规范S0源L254–258），并检查正文脚注锚点。注1 Merriman、注4 Aikema只有姓氏短引，分别新建出版物候选，题名、年份和作者全名留待书目段核对；不声称已查阅引文原作。注2复用James C. Davis研究；注3复用Pallucchini编著的乡间别墅装饰研究卷；注4关联Zenobio家族赞助研究；注5、6均复用Puppi研究候选，但分别保留pp.211–250与pp.212–216定位；注7复用Croft-Murray《Decorative Painting in England》第二卷；注8复用Daniels关于Sebastiano Ricci的专著；注9复用Shipley讨论Amigoni敌意的文章。姓氏身份和缺失书目字段留待书目审阅/S3处理。

页图印本注号及当前S0转录一致，无需OCR校正。9条注释分别回链到p.405正文的Conti/Crespi、Davis、Pallucchini、Zenobio、两项Puppi、Croft-Murray、Daniels、Shipley statements。受控迁移脚本`chp20_notes_p405_migration.py`默认dry-run，锁定源/PDF哈希、前态计数、注释段状态、候选类型和自然键、精确来源跨度、正文marker/行号及待回链状态；dry-run新增2个引文候选、13条精确mention和9条引文statement。通过后apply，四表恢复副本为`.bak-s2-chp20-notes-p405-20261004`。

写后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全库11,179候选、25,858 mentions、11,189 statements；覆盖584 complete、120 excluded、127 queued、1 partial。注释段迁移覆盖推进至L212–258，p.405九个正文脚注均已链接；下一段为p.406注释L259–263。

## 第二版后记脚注p.409（2026-10-04）

对照`CHP-20Postscript.pdf`物理页18，逐条复核印刷p.409脚注1–9（S0 L271–275）及正文脚注标记。注1据页图读为Matina；S0 OCR写作Matins，新增未具题名的书目候选`cand-11211`，人物/作品身份不据短引补造。印本注2为Algarotti 1963，S0注号误识为3；注3为Da Pozzo。注4拆为Haskell 1958 p.213和Levey 1960 p.250两条出版物引用，S0的`i960`校为1960。注5复用同一Haskell 1958引用；注6–9分别为Santifaller 1976、Santifaller 1977、Levey 1978、Santifaller 1978。短引题名、版本与作者全名均留待书目/S3核对，引用原作未独立查阅。

迁移前确认注释段状态为`reviewed/partial`、覆盖到L270，四表基线为候选11,189、提及25,895、statement 11,213。受控脚本`chp20_notes_p409_migration.py`默认dry-run，核验源Markdown与PDF哈希、候选/正文statement外键、脚注marker定位、精确提及跨度及原句；dry-run新增1候选、16条提及、10条citation statements，14条正文statement完成脚注回链。页图校读三处：Matins→Matina、OCR注号3→印本2、i960→1960；只写入校读记录，不改写S0。apply前保存四表恢复副本`.bak-s2-chp20-notes-p409-20261004`。

写后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全库11,190候选、25,911 mentions、11,223 statements，覆盖584 complete、120有理由排除、127 queued、1 partial。注释段推进至L275；下一页p.410脚注L276–280。

## 第二版后记脚注p.410（2026-10-04）

对照`CHP-20Postscript.pdf`物理页19，逐条核读印刷p.410脚注1–5（S0 L276–280）及正文marker。注1为Previtali 1964 pp.153–158；新增单独的短引档案候选`cand-11212`，与p.301未决短引保持分开，待书目核实是否同一作品。注2复用正文已登记的`Art and its Images`展览目录候选；注3复用Loredana Olivato 1974文章；注4新建Haskell 1967短引候选`cand-11213`，因同年可有多条书目记录，暂不与p.290候选合并；注5复用正文已登记的Vincenzo Fontana文章。五条引文未独立查阅，缺失题名不推断。页图确认注5印本编号为5，S0 OCR误读为6；校读仅记录在注释statement。

受控脚本`chp20_notes_p410_migration.py`默认dry-run，校验源/PDF哈希、前置覆盖状态与表计数、候选类型/外键、每条正文脚注marker、精确跨度、原句及重叠范围。dry-run后新增2个archive候选、8条提及、5条citation statements，并为7条正文statement回链；Previtali/Haskell身份与书目对应关系留待后续对齐。apply前保存四表恢复副本`.bak-s2-chp20-notes-p410-20261004`。

写后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全库1,019 KU、11,192候选、25,919 mentions、11,228 statements；832段中585 complete、120有理由排除、127 queued、0 partial。后记注释段L212–280全部逐条迁移，后续S2游标转到书目33段与索引94段。结构审计通过不代表全书语义召回或准确性已独立验收。

## 全书来源范围核对：旧版书目转录（2026-10-04）

比较`21_CHP-21Bibliography_intro.md`与规范分节来源`21_CHP-21Bibliography.md`：旧版1303行、规范版1306行，除内部文件标题外，正文高度重合，差异主要为OCR标点、断行、两栏顺序与Markdown斜体标记。旧版把一条书目作为独立行列为差异：Noemi Gabrieli, “Aggiunte a Sebastiano Ricci”；规范版将其接在同一行的前一条条目后。对照`CHP-21Bibliography.pdf`物理页13，规范版确实包含该条，旧版未包含；未发现仅存在于旧版、而规范分节文件/印本没有的书目内容。旧文件是替代OCR转录，不另作S0来源，也不删除。其余4个后部`*_intro.md`仍待核对。

## 书目段L3–45：范围说明与手稿保管机构目录（2026-10-04）

核对`CHP-21Bibliography.pdf`物理页1。L5说明该书目有意不求完备，收录正文或注释实际引用的来源，并说明期刊/展览目录的斜体及匿名作者方括号规则；将其作为书目编纂范围statement，不视为学术领域完整综述。L7–45列出34个手稿档案/图书馆保管机构；PDF页图用于恢复两栏下的地点隶属，避免按S0 OCR相邻文字错误配对。逐项复用现有institution候选或新建11项；Florence、Rome、Venice、Verona等同名Archivio di Stato保持地点分支，Biblioteca Nazionale Florence与既有未定分馆候选不提前合并。Perugia的Chiesa del Gesù按实体为教堂建筑记place；Staatsarchiv的机构与其他段中具体Schulenburg手稿候选分开。Biblioteca Vallicelliana括号、Museo di Roma前印刷符号及历史拼写均保留在语境说明；该列表不单独证明某件手稿的具体馆藏位置。

受控脚本`chp21_bibliography_repositories_migration.py`校验来源/PDF/S0段哈希、源段覆盖前态、候选类型/外键、34条精确mention跨度和重叠、原句及生成式标题排除状态。dry-run通过后新增11候选、34提及和2条bibliography statements（选择范围说明、保管机构目录），将L3–45标为reviewed/complete。恢复副本`.bak-s2-chp21-bibliography-repositories-20261004`。同时将纯文件名标题`chp-21:21_CHP-21Bibliography:l1-1`标记为excluded/complete，理由与其他生成式S0标题一致；独立保留表备份`.bak-s2-bibliography-heading-20261004`，来源Markdown不改写。

本次全表审计`s2_missing=[]`、`errors=[]`；候选11,203、mentions 25,953、statements 11,230；832段中586 complete、121 excluded、125 queued、0 partial。书目L3–45之后仍有31个排队书目段和94个索引段；机械完整性不代表实体覆盖或语义质量验收。

## 书目L47–85：已刊资料条目（2026-10-04）

核对`CHP-21Bibliography.pdf`物理页2（印刷p.412）与规范源L47–85：页眉folio 412，分节标题为“Published Materials”；29条出版物记录及一条Gregorio de Andrés作者交叉索引。对每条出版物记录保留原S0引文跨度、书目字段与`archive`候选；21条复用已有候选，新增8条（`cand-11225`–`cand-11232`）。另为交叉索引中的两次Andrés姓名形式及Harris姓名建立3条精确提及，并以statement指向同书目待处理的L578条目。L66为`Andres, Gregorio de`，页图确认印本带重音；与p.401注1的Harris/de Andrés候选建立同书内部书目回链，但候选合并及外部身份核对仍留给S3。

页图校读并仅在statement限定中记下OCR差异，不改写S0：L48装饰性小节标记与标题；L50页码326–336；L56–57的`Mededelingen`断行及`Instituut`；L64年份1960；L67`attività`、`Bellucci`；L75–76作者名Arslan；L78`fasc. 133`；L82`meubles`；L85作者缩写`N.`。Aikema的1979年Zenobio文章与p.405注4短引、D’Arcais的1964年Bellucci文章与p.406注5短引由本书书目补出完整书目信息；没有据此声称查阅文章全文。p.301注6的1757年`Il-Tempio della Filosofia`候选`cand-9514`与本书书目列出的1755年版本分别保留，待后续版本核对。

受控迁移脚本`chp21_bibliography_l47_85_migration.py`校验源文件、PDF与S0段哈希、迁移前表计数、候选类型、精确跨度、重复与外键；dry-run后写回8个候选、32条mention、31条statement及覆盖状态，并保存四表恢复副本`.bak-s2-chp21-bibliography-l47-85-20261004`。首轮审计发现coverage行范围格式不符合验证器要求、29条条目statement的claim自然键重复；未改动来源文本。受控修复脚本`chp21_bibliography_l47_85_audit_repair.py`按契约改为`L47-85`并令每条claim唯一，另保存statement与coverage恢复副本`.bak-s2-chp21-bibliography-l47-85-audit-repair-20261004`。

修复后`python -X utf8 scripts/audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全库候选11,211、mentions 25,985、statements 11,261；832段中587 complete、121有理由排除、124 queued、0 partial。书目下一段L87–127（PDF物理页3）；其余书目30段、索引94段仍待S2处理。结构校验通过不等于语义质量独立验收。

## 书目L87–127：已刊资料条目（2026-10-04）

核对`CHP-21Bibliography.pdf`物理页3（印刷p.413）与规范源L87–127，处理27条出版物记录。18条复用已有archive候选，新增9条（`cand-11233`–`cand-11241`）；写入27条精确mention及27条`bibliography_lists_publication` statement。为Barozzi—Berchet两卷本建立集合级候选，并把既有卷级候选`cand-4365`、`cand-6006`留作S3候选核对；Baldinucci第VI卷条目复用`cand-4846`，另将`cand-8601`记为待S3核对的可能同作候选。没有将作者姓名直接升级为外部身份或正式作者关系。

页图揭示S0 OCR在Barozzi—Berchet条目后漏录整行`2 vols., 1877-8.`；将它作为statement的page-image补记并关联完整两卷本出版信息，未改写S0来源。页图也确认Bartolozzi的1754年份与Bartsch下一条在S0 L111被合并；提及和statement分别截取两条目，避免相互污染。其他校读均保留在statement qualifiers：L99 `Vili`→`VIII`；L103页码格式；L109 `13'0`→`130`；L112 `Negotiation`→`Négotiation`；L113 `Borghése`→`Borghèse`；L117年份1959；L119 `Battegia`→`Battagia`；L120 `Battistélla`→`Battistella`；L122 `Z0-4Z`→`30-43`。源文件不修改。

受控脚本`chp21_bibliography_l87_127_migration.py`检查来源/PDF/段文本哈希、前态计数、候选类型与自然键、精确提及偏移、statement引句及外键；dry-run后写入并保留四表恢复副本`.bak-s2-chp21-bibliography-l87-127-20261004`，另更新10条已有短引候选的书目身份说明。全表审计`s2_missing=[]`、`errors=[]`；候选11,220、mentions 26,012、statements 11,288；832段中588 complete、121有理由排除、123 queued、0 partial。下一书目段L129–163；尚有29个书目段和94个索引段。机械审计不替代语义质量验收。

## 书目L129–163：已刊资料条目（2026-10-04）

核对`CHP-21Bibliography.pdf`物理页4（印刷p.414）与规范源L129–163，迁移27条S0可锚定的出版物记录：20条复用已有archive候选，新增7条（`cand-11242`–`cand-11248`），写入27条精确mention及27条`bibliography_lists_publication` statement。更新15条既有短引候选的书目识别信息；作者姓名不据书目直接建立外部身份或正式作者关系。Bazzoni、Beani、Bernis及Berengo条目可能与旧短引候选相关，均保留给S3身份核对；Bertolotti的1886年期刊文章与`Arte e Storia`卷级候选明确分开。

页图发现Beckford条目在S0 L135后漏录`2 vols., London 1834.`，并将`the author of Vathek`误识为`thè author os Vathek`；两项仅在statement限定中校正。页图还显示一条完整的Bellori《Nota delli Musei…》1664年书目项被S0整体漏录：因原OCR中不存在该条的提及跨度，未伪造mention，而是以独立`bibliography_page_image_addendum` statement记录页图转录，并使用前后相邻OCR行作为明确说明的锚点；复用候选`cand-4805`，S0原文未改。L163的Betcherman页码由`PP-325-33I-`校为`pp. 325–331`。

受控脚本`chp21_bibliography_l129_163_migration.py`锁定来源/PDF/段落哈希、迁移前四表计数、候选类型与自然键、精确提及偏移、statement引句及外键；dry-run通过后apply，四表保留恢复副本`.bak-s2-chp21-bibliography-l129-163-20261004`。全表审计`s2_missing=[]`、`errors=[]`；候选11,227、mentions 26,039、statements 11,316；832段中589 complete、121有理由排除、122 queued、0 partial。下一书目段L165–205；剩余书目28段、索引94段。结构审计不替代语义质量评估。

## 书目L165–205：已刊资料条目（2026-10-04）

核对`CHP-21Bibliography.pdf`物理页5（印刷p.415）与规范源L165–205，处理25条出版物记录：21条复用archive候选，新增4条（`cand-11249`–`cand-11252`），写入25条精确mention和25条`bibliography_lists_publication` statement。对既有候选中先前仅有短引/章节定位的Bettagno、Bevilacqua、Bianchini、Bildt、Binion、Blainville及多项Blunt作品补入本地书目信息；引文原作均未据此声称已独立阅读。书目明确区分Blunt 1945年图书与同年期刊文章、1944/1958期刊文及其容器。

PDF页图确认四项S0校读：L170–171页码`131—136`应为`131–136`；L172年份`i960`应为`1960`；L182 `PP297-303`为`pp. 297–303`；L195 `Poussinin Bulletin`为`Poussin’ in Bulletin`。L185–186 Blainville条目末尾的短横不并入题名；未发现整条书目漏录。来源OCR保持不变。

迁移脚本`chp21_bibliography_l165_205_migration.py`锁定来源/PDF/段落哈希、迁移前表计数、候选类型与自然键、mention偏移及statement引句/外键；dry-run通过后apply，四表恢复副本后缀`.bak-s2-chp21-bibliography-l165-205-20261004`。全表审计`s2_missing=[]`、`errors=[]`；候选11,231、mentions 26,064、statements 11,341；832段中590 complete、121有理由排除、121 queued、0 partial。下一书目段L207–241；剩余书目27段、索引94段。结构审计不替代语义质量评估。

## 书目L207–241：已刊资料条目与交叉索引（2026-10-04）

核对`CHP-21Bibliography.pdf`物理页6（印刷p.416）与规范源L207–241，拆分并处理28条出版物记录：复用17个archive候选，新增11个（`cand-11253`–`cand-11263`）；另处理末尾`Bracciano, Duca di: See Paolo Giordano`目录交叉索引，分别指向既有候选`cand-3479`与`cand-0434`，不合并身份、不生成正式人物关系。共写入30条mention和29条原书statement。书目中已有卷级/单封信短引保持独立，并在set-level publication条目中注明待S3核对。

页图纠正L219 `Vol. 9s`→`Vol. 91`；L224、L225姓氏`Bortoni`→`Borroni`；L236页码`23 3-23 8`→`233–238`。S0 L239将Boyer 1934文章末尾与Bozzòla 1948条目粘连，按页图将两条statement和mention分别锚定到各自精确原文跨度，并记录缺失句点/条目边界。书目与正文OCR保持不改。

迁移脚本`chp21_bibliography_l207_241_migration.py`锁定来源/PDF/段落哈希、迁移前计数、自然键、精确跨度、外键及statement原句；dry-run通过后apply，四表恢复副本后缀`.bak-s2-chp21-bibliography-l207-241-20261004`。全表审计`s2_missing=[]`、`errors=[]`；候选11,242、mentions 26,094、statements 11,370；832段中591 complete、121有理由排除、120 queued、0 partial。下一书目段L243–293；剩余书目26段、索引94段。结构审计不替代语义质量评估。

## 书目L243–293：已刊资料条目（2026-10-04）

核对`CHP-21Bibliography.pdf`物理页7（印刷p.417）与规范源L243–293，处理30项出版物：复用16个archive候选，新增14个（`cand-11264`–`cand-11277`），写入30条精确mention及30条`bibliography_lists_publication` statement。Brugnoli同一书目条目实际列出两篇文章，按两个publication对象分别登记，保留共同刊名、年份和页码；Bricarelli原OCR将刊名挪至作者/题名前，依据页图恢复书目字段次序，但S0不改。集合级Brienne、Burney候选及Brusoni的1662印本文献与卷级引文/索引作品候选分开，供S3对齐。

页图校读：L244、L290 `i960`→1960；L256 `Parafili`→Pamfili；L258 `voi.`→vol.；L260移除OCR多出的`in`；L271去除页码后OCR杂符；L286恢复1620；L293页码`424-43 3`→424–433。另根据页图复原Bricarelli条目及Brugnoli、Brol、Brunelli、Brunetti、Burchard、Burden、Buser等条目的刊名顺序/归属；不把版面校读写回来源转录，也不据书目声称读过被引作品。

受控脚本`chp21_bibliography_l243_293_migration.py`锁定来源/PDF/段落哈希、迁移前计数、候选自然键、mention精确跨度、statement引句和外键；dry-run通过后apply，四表恢复副本后缀`.bak-s2-chp21-bibliography-l243-293-20261004`。`audit_tables.py --summary`结果为`s2_missing=[]`、`errors=[]`；全库候选11,256、mentions 26,124、statements 11,400；832段中592 complete、121有理由排除、119 queued、0 partial。下一书目段L295–334；剩余25个书目段和94个索引段。结构审计不替代语义质量评估。

## 书目L295–334：已刊资料条目与作者交叉索引（2026-10-04）

核对`CHP-21Bibliography.pdf`物理页8（印刷p.418）与规范源L295–334，处理29项出版物并复用23个archive候选、新增6个（`cand-11278`–`cand-11283`）；另将`Carandini, Silvia: See Fagiolo dell’Arca and Carandini`作为作者书目交叉索引，复用既有person/study候选，新增31条mention、30条statement。Canova末尾与Cantalamessa开头在S0 L310粘连，按页图拆分并各自精确定位；Casanova de Seingalt六卷版、Cardella九卷本及Calogerà五十一卷集建立集合级候选，与已有作者/单卷定位候选分开，留S3身份核对。

页图校读并只记在statement限定中：L296 `i960`→1960及多余引号；L298 `Vili`→VIII；L299 `serie`→série；L308 `19ÖO`→1900；L310 Canova/Cantalamessa条目边界；L319 `Scingali`→Seingalt并补édition重音；L320去除多余引号；L329去除尾随下划线。S0保持不改。被引出版物未独立查阅。书目索引将Carandini指向现有Fagiolo/Carandini研究候选，完整书目项位于L458；本段只记录交叉索引，不据此做外部身份认定或正式人物关系。

迁移脚本`chp21_bibliography_l295_334_migration.py`校验来源/PDF/段落哈希、迁移前表计数、候选类型/自然键、精确提及跨度、statement原句与外键；四表恢复副本为`.bak-s2-chp21-bibliography-l295-334-20261004`。首轮审计发现Canova/Cantalamessa及交叉索引提及跨度重叠；从迁移前副本恢复后收窄mention跨度，复用经哈希核验的恢复副本重新写入。最终`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；候选11,262、mentions 26,155、statements 11,430；832段中593 complete、121有理由排除、118 queued、0 partial。下一书目段L336–374；剩余24个书目段和94个索引段。结构审计不替代语义质量评估。

## 书目L336–374：已刊资料条目（2026-10-04）

核对`CHP-21Bibliography.pdf`物理页9（印刷p.419）与规范源L336–374，处理28项出版物：复用15个archive候选，新增13个（`cand-11284`–`cand-11296`），写入28条精确mention和28条`bibliography_lists_publication` statement。两篇Coggiola-Pittoni文章分别建账；Constable两篇文章在S0 L371粘连，依据页图分为p.154期刊文和1956年文集文章，mention跨度分别锚定各自标题。Cicogna、Cochin及Conti集合级候选与已有单卷引文候选分开，留待S3。

页图校读并保留在statement限定中：L337页码`333*343`→333–343；L339清除装饰/下划线残留并校正38–64；L348 `Il`→II；L352去掉条目前杂点；L353补Clément重音；L355补édition重音；L357–358恢复Serenissima跨行；L360去除扫描杂点；L371分开两项Constable书目并校正p.154。S0来源文本不改写，被引内容未独立查阅。

受控脚本`chp21_bibliography_l336_374_migration.py`核验来源/PDF/段落哈希、前态计数、候选类型/自然键、精确提及跨度、statement引句及外键；四表恢复副本为`.bak-s2-chp21-bibliography-l336-374-20261004`。全表审计`errors=[]`、`s2_missing=[]`；候选11,275、mentions 26,183、statements 11,458；832段中594 complete、121有理由排除、117 queued、0 partial。下一书目段L376–418；剩余23个书目段和94个索引段。结构审计不替代语义质量评估。

## 书目L376–418：出版物条目与交叉索引（2026-10-07）

对照`CHP-21Bibliography.pdf`物理页10（印刷p.420）逐行处理规范源L376–418；L376是页码标记，L377–418包含30条出版物记录和1条`See also`书目指针。复用12个archive候选，新增18个（`cand-11297`–`cand-11314`），写入32条精确mention和31条`origin=book` statement。逐项登记作者/题名/出版信息；`Crespi—Mostra celebrativa...`只把Crespi记为书目条目标题，不推定作者。被引作品没有在本次S2中独立查阅。

`Croft-Murray, E.: See also Blunt and Croft-Murray`按书目导航记为`bibliography_cross_reference`，指向本书L210的Blunt—Croft-Murray联合出版物候选`cand-9340`；来源候选沿用`cand-11001`，明确保留跨章身份待S3，不生成作者关系或身份合并。

按页图在statement限定中校正L378 `delle‘chiese`→`delle chiese`、L384与L412位于页边的孤立尾横不纳入书目记录、L404 `191z`→`1913`、L407 `cinquantanni`→`cinquant’anni`、L415 `II Grechetto`→`Il Grechetto`、L416 `l6ème`→`16ème`；S0 OCR文本保持不变，未发现本页整条书目项漏录。受控脚本`chp21_bibliography_l376_418_migration.py`默认dry-run并锁定来源/PDF/段哈希、前态计数、自然键、mention偏移、statement引句与外键；apply前为四表保留`.bak-s2-chp21-bibliography-l376-418-20261007`恢复副本。

写入后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；候选11,293、mentions 26,215、statement 11,489；832段中595 reviewed/complete、121 excluded、116 queued、0 partial。下一段为书目L420–459（PDF物理页11，印刷p.421）；其后还剩21个书目段和94个索引段。机械审计不替代语义范围与质量交接审查。

## 书目L420–459：出版物条目（2026-10-07）

对照`CHP-21Bibliography.pdf`物理页11（印刷p.421）逐行核对规范源L420–459；L420是页码标记，L421–459包含31条出版物记录。复用24个archive候选，新增7个（`cand-11315`–`cand-11321`），写入31条精确mention和31条`bibliography_lists_publication` statement。按书目本身登记作者、题名、出版项，不把引文当成被引作品内容证据。

16个已存在archive候选从仅有引文定位/简称补全为书目可证的题名和出版信息；Ewald的1976引用现对应页421唯一列出的论文题名。`Faldi`的书目年份1954与正文脚注所引1955继续保留差异，不裁决。De Dominici四卷全集`cand-11317`、Evelyn六卷本`cand-11321`分别与具体卷/页引文候选`cand-4835`、`cand-5685`分开，并在statement中标为S3待比对；不提前合并身份。两种来源均未独立查阅。

页图校读只记入statement限定，不改S0：L423移除Ricci与Heidelberg间误入句点；L426移除OCR尾随引号；L432恢复音乐书名中的省略号；L433排除印本以外的尾横扫描痕；L441补回题名闭引号；L455去除行首杂点并校为pp.333–343；L458校正`Effìmero`与`’óoo`；L459将`T busti`校为`‘I busti`。逐项对照页图，未发现整条书目漏录。

受控脚本`chp21_bibliography_l420_459_migration.py`默认dry-run，锁定来源/PDF/段哈希、迁移前表计数、候选类型与自然键、精确mention偏移、statement原句及外键；apply前保存四表恢复副本`.bak-s2-chp21-bibliography-l420-459-20261007`。写入后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；候选11,300、mentions 26,246、statement 11,520；832段中596 reviewed/complete、121 excluded、115 queued、0 partial。下一段书目L461–496（PDF物理页12，印刷p.422）；其后还剩21个书目段和94个索引段。结构审计不替代语义质量与S2交接审查。

## 书目L461–496：出版物与展览条目（2026-10-07）

对照`CHP-21Bibliography.pdf`物理页12（印刷p.422）逐行处理规范源L461–496；L461为页码标记，页内识别29条书目记录。复用20个archive候选，新增9个（`cand-11322`–`cand-11330`），写入29条精确mention和29条`bibliography_lists_publication` statement；另补全13个既有候选的书目题名或出版信息。Ferrari 1882书目项复用此前的短引候选`cand-8777`，避免将同一出版物拆成第二个候选。

Fantuzzi书目记录与`cand-10366`的卷页定位、Félibien六卷本与`cand-7077`的第三卷定位、Fisch—Bergin 1944出版物与Vico通用作品/页码定位候选、Fleming 1958独著文章与Vermeule—Fleming短引候选均保持分立，供S3对齐；`[Fontanella, G. B.]`按印本保留括号归属，不在本阶段认定作者身份。Les Français à Rome 的印刷p.422展览地点和p.202注释中的Archives Nationales描述同时保留，未推断二者是否为不同场地或目录信息。

依据页图在statement限定中校正L466省略号、L473日期前多出的撇号、L476 `if.`→`ff.`、L478行首多出的引号、L480 `Mssrs.`→`Messrs.`、L484与L486–487两处粘连条目的分界、L485 `193 7`→`1937`、L488 `Venezia-—`→`Venezia—`；S0 OCR保持不改。L462–463页图中的行首短横在原始引句及`title_as_printed`中保留。逐项核对未发现整条书目记录遗漏；被引作品未独立查阅。

迁移脚本`chp21_bibliography_l461_496_migration.py`默认dry-run，锁定来源/PDF/段落哈希、迁移前计数、候选类型/名称、自然键、mention偏移、statement引句与外键；dry-run通过后apply，四表恢复副本后缀`.bak-s2-chp21-bibliography-l461-496-20261007`。写入后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；候选11,309、mentions 26,275、statement 11,549；832段中597 reviewed/complete、121 excluded、114 queued、0 partial。下一段书目L498–536；其后还剩20个书目段和94个索引段。结构审计不替代语义质量与S2交接审查。
## 书目 L498–536（PDF物理页13，印刷p.423；2026-10-07）

按规范来源 02-sources/02-Markdown/21_CHP-21Bibliography.md 及 CHP-21Bibliography.pdf 物理页13逐项处理：页图共31条书目记录；S0 L499–536可锚定30条，L498 [Page 423]只是页码标记。另有Gabrieli, Noemi的“Aggiunte a Sebastiano Ricci”在印本上位于Gabrieli, Giuseppe与Galassi Paluzzi两项之间，但OCR被错放到同一来源文件L1304。以页图addendum statement记录完整印本转录，原引句只作相邻L503–504锚点；没有伪造当前段mention。候选cand-11333的候选来源锚定到本已审段L503，detail和statement仍指明精确OCR在L1304；处理l1301-1306时只需将真实mention映射到该候选，不再新增书目statement。

L499为Friedlaender, Caravaggio Studies；L500–501为Frommel论Del Monte与Caravaggio的文章；L502为Gabbrielli论Algarotti的一条同时列有1938年与1939年两组页码的书目项；L503为Giuseppe Gabrieli的Cesi书信集，印本续行“4 vols., Roma 1939–42.”也被OCR错放到L1304，后续须把续行挂到cand-11332；L504–505与L506分别为Galassi Paluzzi的期刊文章与专著；L507为Galilei国家版重印本20卷；L508–509分别为Gallo的1945年专著和1948年文章；L510–511为Galluzzi；L512为Gamba文章；L513–514为Gar文章；L515–517为Garas三篇文章；L518为Garms编辑卷；L519为Ghelli文章；L520–521为带方括号作者归属的Gherardi 1749出版物；L522为Gibbon书信集；L523为Gigli《Diario Romano》；L524–525与L526分别为Giglioli文章和专著；L527–528为Gilmartin文章；L529为Giussani；L530为Giustiniani三卷本；L531为Goering文章；L532为Goethe的Farinelli编本；L533为Goldoni十四卷本；L534–535与L536分别为Golzio文章和专著。各statement只记录Haskell书目所列出版物，不把书目引用当成已读原作的内容证据。

复用18个已存在archive候选并新增13个（cand-11331–cand-11343，含Noemi图像项）；其中14个既有候选（cand-4375、cand-10878、cand-5164、cand-9343、cand-10873、cand-11174、cand-8005、cand-6076、cand-7866、cand-4848、cand-8325、cand-9331、cand-6356、cand-6196）由书目所给信息补齐。cand-11331与Gabbrielli的1938/1939两个定位候选、cand-11332与cand-5642、cand-11334与cand-5835、cand-11335与cand-8515/cand-8537、cand-11336与cand-10138/cand-10150、cand-6076与cand-6269/cand-6360、cand-11341与cand-4389、cand-11342与cand-10135、cand-11343与cand-9496保持为可比对链接，身份不在S2合并，交S3裁决。Gherardi的方括号byline仍保留归属不确定性。

按页图在statement限定中记录L499多余句点、L500断词、L508 Stri→Strà、L509 15 3-214→153-214、L517 28 5-292→285-292、L518 Garrns及(editor) :、L528多余行首引号、L535 PP300-310等OCR校读；S0保持不变。受控迁移脚本默认dry-run并锁定来源/PDF/段哈希、迁移前计数、候选旧名和自然键、mention字符偏移、statement锚点及外键。首次全表审计指出Noemi候选来源不能指向尚未审核的L1304，已将候选来源锚到本已审页图段L503，并在候选detail及statement保留被移位OCR的准确位置；修正后审计errors=[]、s2_missing=[]。四表恢复副本已保存。此段写入30条mention、30条bibliography_lists_publication statement及1条bibliography_page_image_addendum。处理后全表为11,322候选、26,305 mentions、11,580 statements；832段中598 complete、121有理由排除、113 queued、0 partial。下一段书目L538–575；之后还余19个书目段和94个索引段。结构审计不替代S2语义交接复核。

## 书目 L538–575（PDF物理页14，印刷p.424；2026-10-07）

按页图处理28条书目记录，复用17个archive候选，新增11个（`cand-11344`–`cand-11354`），补全10个既有候选；写入28条mentions和28条`bibliography_lists_publication` statements。L553的Griseri两篇文章在S0同一行粘连，按原文连续字符范围拆成两个互不重叠mention。Grosley条目的“3 vols., Londres 1764.”被OCR移至L1305，已在`cand-11347`详情中保留该续行定位；后续处理L1301–1306时为其补精确mention，不重复创建publication statement。Hantsch首半卷与既有卷级定位候选、Gozzi、Gradenigo、Gualandi等书目版候选保持S3比对，不在S2合并。

页图校读记录L544 `Notatoti`→`Notatori`、L553粘连边界和`PP33-39`、L563 `officiai`→`official`、L565年代及标点、L568–575姓名重音/年代/页码等；排除Grassi、Gualdo记录后的脱离短横及扫描边注。S0保持不变，未发现整条书目记录漏录。受控迁移脚本`chp21_bibliography_l538_575_migration.py`默认dry-run，锁定来源/PDF/段哈希、表计数、候选自然键、mention偏移、statement引句及外键；apply前保存四表恢复副本`.bak-s2-chp21-bibliography-l538-575-20261007`。写入后`audit_tables.py --summary`为`s2_missing=[]`、`errors=[]`；全表11,333候选、26,333 mentions、11,608 statements；832段中599 complete、121有理由排除、112 queued、0 partial。下一段书目L577–614；之后还余18个书目段和94个索引段。结构审计不替代S2语义交接复核。

## 书目L577–614：出版物条目（PDF物理页15，印刷p.425；2026-10-07）

对照规范源及`CHP-21Bibliography.pdf`物理页15处理L577–614：页图共26条书目记录，S0 L578–614锚定26条；L577是页码标记。复用25个archive候选，新增`cand-11355`（Haskell, “Art exhibitions in Seventeenth century Rome”, 1960）；写入26条精确mention和26条`bibliography_lists_publication` statement，并补充/校正24个候选的书目信息。L614将Hibbard 1973文章与Hinks的Caravaggio专著拆成两个记录，mention跨度分离；页图确认作者、刊名、重音、页码及条目边界，S0来源不改。

此段复核发现既有候选`cand-4864`把Hibbard 1961年“S. Andrea della Valle”文章与1971年`Carlo Maderno and Roman Architecture 1580-1630`专著误并为一项。已将`cand-4864`修正为1961文章、`cand-5163`修正为1971专著；把第2章L190–245处mention及对应statement从前者重新指向后者，并更新候选来源锚点。S3仍需核对Hibbard 1961书目项与第3章引文的出版物身份；不把书目登记视为独立阅读原作。

受控脚本`chp21_bibliography_l577_614_migration.py`默认dry-run，锁定来源/PDF/段落哈希、迁移前计数、候选类型/自然键、mention跨度、statement引句与外键；dry-run通过后apply，四表恢复副本后缀`.bak-s2-chp21-bibliography-l577-614-20261007`。写入后审计`errors=[]`、`s2_missing=[]`；全表11,334候选、26,359 mentions、11,634 statements；832段中600 reviewed/complete、121 excluded、111 queued、0 partial。下一段书目L616–656；之后还余17个书目段和94个索引段。结构审计不替代S2语义交接复核。

## 书目L616–656：出版物与书目指引（PDF物理页16，印刷p.426；2026-10-07）

对照规范源与`CHP-21Bibliography.pdf`物理页16，处理S0 L617–656。L616的`[Page 426]`只是页码标记；本页有31条出版物／展览记录及2条作者`See`指引，均与页图逐项核对，未发现整条记录漏录。复用19个既有记录候选，更新12个已有书目候选名称/详情，新增12个本页作品候选（`cand-11356`–`cand-11367`）；另为Jaffé作者指引建立目标候选`cand-11368`。写入33条mention和33条statement：31条记录和2条书目指引。

L631的OCR把Incisa della Rocchetta 1925年《Il museo di curiosità del Cardinale Flavio Chigi Seniore》与1959年《Tre quadri Barberini acquistati dal Museo di Roma》粘成一行；按页图拆成两个互不重叠的精确mention和独立statement。校读L619 `195 8`→1958、L620 `i960`→1960、L621 `omirent`→`omtrent`、L623 `193 5`→1935及`ppr`→`pp.`、L631页码`539'544`→539–544并恢复条目边界、L635 `i960`→1960、L638 `.See`→`See`、L653页码`23 3`→233。L653刊名按页图所见保留原拼写，不据外部知识规范化；页边离散墨迹不算正文。S0不改。

L638 `Jaffé, Irma: See Wittkower and Jaffé`指向S0 L1276–1277的合编本`Baroque Art: The Jesuit Contribution`。为保持指引外键完整，先建候选`cand-11368`，其候选来源锚定当前已审指引L638；全书目L1261–1299仍queued，该目标的页图复核、精确mention及书目statement待按书序处理时补入。L641的Jones指引指向本页L653的Krautheimer—Jones论文`cand-11361`。这些指引只记录书目路径，不作为历史关系或外部身份判断。其余短引与完整书目记录以`related_candidate_ids_for_s3`关联，保留独立候选交S3，不在S2合并。King’s Pictures按本页明确的展览记作event候选；出版物与展览项目不混为一类。被引作品均未在此段独立查阅。

受控迁移脚本`chp21_bibliography_l616_656_migration.py`默认dry-run，锁定来源/PDF/段落哈希、迁移前计数、候选类型及自然键、mention偏移、statement引句和外键；dry-run通过后apply，四表恢复副本后缀`.bak-s2-chp21-bibliography-l616-656-20261007`。初次写入后审计发现`cand-11368`候选来源锚指向尚未复核的L1276；已改锚到当前已审L638，L1276的完整书目处理仍queued。最终`audit_tables.py --summary`为`errors=[]`、`s2_missing=[]`；全表11,347候选、26,392 mentions、11,667 statements；832段中601 reviewed/complete、121 excluded、110 queued、0 partial。下一段书目L658–699；之后还余16个书目段和94个索引段。结构通过不等于全书语义交接完成。

## 书目L658–699：出版物与“See also”指引（PDF物理页17，印刷p.427；2026-10-07）

对照规范源与页图处理L658–699。L658的`[Page 427]`只是页码标记；L659–699包含30条出版物记录及L690、L698两条“See also”指引。页图逐项核对，未发现整条漏录或粘连项；L699 Alessandro Longhi书目记录在本段结束，L700为下一印刷页页码标记。写入30条`bibliography_lists_publication`及2条书目指引statement，共32条mention和32条statement。复用并补充24个既有archive候选；新增6个书目archive候选（`cand-11369`–`cand-11374`）及2个书目贡献者候选（`cand-11375`–`cand-11376`）。

按本地作者、年份、题名及页码信息补全24个候选。两项短引保留给S3比对：p.352 n.1的Levey 1955页码为193–203，而书目页图为199–203，因此新建书目候选`cand-11373`并关联原短引`cand-10281`，不合并；Lavagnino的卷III书目记录`cand-11371`与既有`cand-7251`关联，但p.282–283未注明卷号的页码引用不指派到该卷。Lankheit的1956文章与1962专著分别记录；未定题名的Lankheit页码候选链接供S3核对。L690的Levey heading 指向已审L577–614中的Haskell—Levey 1958文章`cand-8638`；L698的Livan heading 指向已审L538–575中的Gradenigo书目记录`cand-11345`，该条注明Lina Livan为编者。指引仅记录书目检索路径，不生成历史关系；跨章作者身份仍交S3。

页图校读记录L661 `II Gesù`→`Il Gesù`、L663 `Miinchner`→`Münchner`、L664页码`16701743`→`1670-1743`、L675 `fase, i`→`fasc. I`、L679 `PP256-261`→`pp. 256-261`、L680 `Valtnarana`→`Valmarana`、L685 `i960`→`1960`、L697 `193 5`→`1935`。页图确认L664印作`Florentinsche`，按印本拼写保留，不作外部规范化。Levey 1955页码差异单独记入statement。S0不改；书目列举不代表独立查阅了这些出版物。

受控迁移脚本`chp21_bibliography_l658_699_migration.py`默认dry-run，锁定来源/PDF/段落哈希、迁移前计数、候选类型及自然键、mention偏移、statement引句、指引目标与外键；dry-run通过后apply，四表恢复副本后缀`.bak-s2-chp21-bibliography-l658-699-20261007`。写入后`audit_tables.py --summary`为`errors=[]`、`s2_missing=[]`；全表11,355候选、26,424 mentions、11,699 statements；832段中602 reviewed/complete、121 excluded、109 queued、0 partial。下一待处理书目段为L701–754；余15个书目段和94个索引段。结构通过不等于全书语义交接完成。

## 书目L701–754：出版物条目（PDF物理页18，印刷p.428；2026-10-07）

对照规范源`21_CHP-21Bibliography.md`的L701–754及`CHP-21Bibliography.pdf`物理页18逐项处理。L701的`[Page 428]`是页码标记，不是书目记录；印本本页有33条书目记录，其中L750一条记录明列两篇不同文章，故登记34个出版物候选与34条书目statement。L702–754无未覆盖来源行，页图逐项核对未发现整条记录遗漏。书目陈列只证明Haskell列出该出版物，不证明本轮阅读了被引作品。

L702–711为四篇R. Longhi期刊文章与L712的Longo四卷本。页图确认L702、L705、L707、L710四个独立`Paragone`行分别属于其后的Longhi文章；保留L703的`Velazquez 1630`印本拼写，新增1950文章`cand-11377`，并复用1954、1956与1963文章候选`cand-7144`、`cand-7604`、`cand-10856`。1963文章标题补为`Il vero “Maffeo Barberini” del Caravaggio`；第2章另一个Longhi 1963简称候选`cand-4350`仍单独保留供S3。L712新增Longo第二版四卷本`cand-11378`；页图确认OCR末尾多出的双引号不在印本，已有卷I页码候选`cand-8426`只作S3比对，不并入出版物身份。

L713–724含Lorenzetti三条、Loret、Lotti及Lumbroso、Luzio、Maclaren、Madrisio。L713的`Fanfulla della Domenica`属于L714–715的Lorenzetti 1914条目，印刷日期首字为数字1；该唯一同作者同年项目补全已有短引候选`cand-10602`。1917的Zanetti专著与1956的`Venezia e il suo estuario`各建新候选`cand-11379`、`cand-11380`，分别链接`cand-9948`/`cand-10192`及`cand-8791`供S3，不提前合并。L719页图读作`Capitolium`而非OCR的`Capitoliam`；L719–720的Loret论文与Lotti家史在OCR中粘接，依印本切成两个不重叠mention和独立statement，分别复用`cand-6583`、`cand-6184`。Lumbroso、Luzio、Maclaren与Madrisio各复用已有archive候选，补齐印本地点、题名或出版项。

L725–737为Mahon七项出版物。页图将L726、L728、L730、L732、L734、L736的期刊/出版者行依次归回下方相邻记录；L731与L733的`i960`按印本校为1960。L727的`Guercino’s paintings of Semiramis`印在`Art Bulletin`，已将`cand-7057`既有误记的`Burlington Magazine`改正；文章与内容未独立查阅。复用1947研究、1949文章、1960两篇文章及1961文章候选（`cand-4371`、`cand-7057`、`cand-5526`、`cand-7070`、`cand-5905`），新增1952年`Addenda to Caravaggio`（`cand-11381`）和1962年`Poussiniana`（`cand-11382`）。`Poussiniana`仍与合并式1960/1962短引`cand-4867`分立，交S3裁决。

L738–754记录Malamani、Male、Malvasia、Manchester、Mancini、Mandosio、Manini、Manuel、Marabottini与Marcellino。页图显示Canova条目末尾印有短横，记录为印本标点而不解释成日期；L739的`Le Gallerie Nazionali Italiane`属于L740 Rosalba Carriera论文。复用`cand-10454`、`cand-9461`，将其余1899年Malamani短引逐个链接供S3。L741 OCR的`XVIlème`按页图校为`XVIIème`；印本作者姓为`Male`，未添加来源未载的重音。L743的Bologna 1841两卷本新建`cand-11384`，与原作年代1678的`cand-6933`区分。Manchester、Mancini和Manuel已有引用候选补全为印本题名；Mandosio复用现有`cand-5600`；Manini新建`cand-11385`并链接既有人物候选。L750在印本是一条含两篇题名和两组页码的书目记录：新建`Novità sul Lucchesino`（pp.116–135，`cand-11386`）及`Il “Trattato di Pittura” e i disegni del Lucchesino`（pp.217–244，`cand-11387`）。S0把标题末尾`Luc- / chesino`与`Commentari`错序；通过两个精确、互不重叠的标题mention还原排版，不改写原来源。L751–752的1963年Paolini研究另建`cand-11388`，不与论Wallenstein的标题未明候选`cand-6191`合并。L753–754的Marcellino Renier专著补全既有`cand-8146`；p.18 note 32的`cand-8431`保持分立供S3。


## 书目L756–806：出版物及展览目录（PDF物理页19，印刷p.429；2026-10-07）

对照规范源`21_CHP-21Bibliography.md`的L756–806与`CHP-21Bibliography.pdf`物理页19逐条审读。L756的`[Page 429]`只是页码标记；页图本页有28条书目记录，包含一条展览目录记录。28条均作为`bibliography_lists_publication`陈述；Mazarin条目复用已有archive候选`cand-7044`，其前文脚注已明确为展览目录，不另建event对象。所有陈述仅记录Haskell列目，不表示本轮独立阅读被引出版物。

L757 Marcheix专著新建`cand-11389`，并与题名未明的`cand-7000`保留S3比对入口。L758–760的Maresca di Serracapriola论文复用并补全`cand-7388`；L758的`Napoli Nobilissima`在OCR中移到作者行上方。L761–763 Mariacher论文新建`cand-11390`，恢复OCR错置的`Ateneo Veneto`；L764同作者1957年Museo Correr图录补全`cand-10704`。L765–766 Mariette六卷本补全`cand-6587`，依页图把OCR的Manette/Àbecedario/pai/18531862校为Mariette/Abecedario/par/1853–1862；卷IV及其他短引仍挂接`cand-1547`、`cand-10196`和`cand-9334`供S3。L767–768新建Marrini两卷本`cand-11391`：印本清楚为Marrini（双r），与OCR Martini及既有、出处未明的`cand-7926`分立交S3。L769新建C. A. Martin八卷本`cand-11392`，校正OCR粘连的1798–1808；L770–773新建W. Martin论文`cand-11393`，恢复被拆开的Burlington Magazine，并校正life/the。

L774复用已完整的Martyn候选`cand-9859`。L775–776新建Marucelli的Indice del Mare Magnum版本`cand-11394`，与未定同一性的`cand-6410`及Biagi前言`cand-6412`留待S3；L777新建Matina著作`cand-11395`并链接索引候选`cand-1578`；L778新建Matteoli论文`cand-11396`并链接身份未明的编者候选`cand-5713`。L779补全Maugain候选`cand-9922`并校读标题首字母É；L780补全Mauroner 1945年专著`cand-9289`；L781–782补全Mauroner 1947年论文`cand-10606`，将OCR前置的Arte Veneta归回该项。L783与L784–785复用Mazarin的1842年书信集`cand-7082`及九卷本`cand-7083`；L786–787的1961年展览目录复用`cand-7044`，不把目录和展览事件混为一项。

L788–790新建Mazza论文`cand-11397`；页图把标题续文、期刊名和期号10重新分开，OCR`io`校为10。L791补全Mazzotti图录`cand-10452`，印本作者确为Mazzotti，OCR作Mazzetti。L792补全Melchiori著作`cand-9972`；L793–796分别补全Meloni Trkulja两篇Paragone论文`cand-11197`与`cand-11189`，恢复错置刊名并校正1975期号和页码。L797复用带方括号作者归属的Memmo 1786年著作`cand-8812`；L798–799新建同一印本归属方式的1788年著作`cand-11398`。L800至L801的Memmoli专著新建`cand-11399`，校正Meliino为Mellino；同一OCR行直接粘入下一条Merriman论文，脚本以L801的`1644`和`Merriman`为边界，建立两段精确引句及互不重叠mention。Merriman论文复用并补全`cand-11199`。L804–806补全Mezzetti论文`cand-4948`，依页图恢复跨行错置的Rivista dell’Istituto Nazionale d’Archeologia e Storia dell’Arte刊名。

受控脚本`chp21_bibliography_l756_806_migration.py`默认dry-run，核对Markdown/PDF/分段指纹、迁移前表规模、候选类型与自然键、statement外键、source line引句和mention字符偏移；dry-run后apply，并在写表前为四张表保存`.bak-s2-chp21-bibliography-l756-806-20261007`恢复副本。本段复用17个archive候选、补全12个，新增11个archive候选，写入28条mention和28条`bibliography_lists_publication` statement。`audit_tables.py --summary`返回`errors=[]`、`s2_missing=[]`；当前11,378候选、26,487 mentions、11,761 statements；832段中604 complete、121 excluded、107 queued、0 partial。下一书目段为L808–844；余13个书目段与94个索引段。机械审计不替代全书S2语义交接审查。

## 书目L808–844：出版物与作者交叉指引（PDF物理页20，印刷p.430；2026-10-07）

对照规范源`21_CHP-21Bibliography.md`的L808–844与PDF物理页20逐条审读。L808的`[Page 430]`只是页码标记；印本本页有26条出版物记录及L820一条作者`See`指引。按材料性质写入26条`bibliography_lists_publication`及1条`bibliography_author_cross_reference` statement；不把书目记录误作正文断言或实体关系。

页图确认L813把两条D. Miller文章分列：Crespi书信论文（1960，pp.530–531）与Macerata Aeneid长廊论文（1963，pp.153–158，并列1964 p.113）。OCR将其粘为一行，迁移时以印本边界拆成两个精确引句；1964定位单独mention并链接既有`cand-7758`，保留与主条目`cand-7757`的S3判断。L818–819确认Mitchell页码为340–343；页图还核对Montaiglon机构名、Morassi两条1955记录与Morelli书名省略号等OCR细节，原OCR文件不改写。

本段复用21个archive候选，其中19个依印本文字补全元数据；另新建5个archive候选`cand-11400`、`cand-11402`–`cand-11405`及1个Molinier作者heading person候选`cand-11401`。L820指向L861的Müntz et Molinier条目；因目标段L846–881仍排队，当前暂链至`cand-4828`并明确标记未复核，不据此裁决身份。Moncallero与旧联合引文`cand-9932`、Monaco版本、Montaiglon分卷定位、Morassi 1952书目页码与正文脚注差异、Morazzoni页码短引均保留S3比较入口。

受控脚本`chp21_bibliography_l808_844_migration.py`默认dry-run，核验Markdown/PDF/段落指纹、迁移前计数、候选类型、statement外键、逐行引句、mention精确偏移与重叠；apply前为四表生成`.bak-s2-chp21-bibliography-l808-844-20261007`恢复副本。写入28条mention及27条statement后，目标段审计确认26条出版物、1条交叉指引，所有外键、引句和偏移有效且mention不重叠；`audit_tables.py --summary`为`errors=[]`、`s2_missing=[]`。当前11,384候选、26,515 mentions、11,788 statements；832段中605 complete、121 excluded、106 queued、0 partial。下一书目段L846–881；余12个书目段及94个索引段。机械检查不等于全书S2语义交接。

## 书目L846–881：出版物及前页作者指引核对（PDF物理页21，印刷p.431；2026-10-07）

对照规范源与PDF页图审读本段。L846的[Page 431]为页码标记，印本本页列有28条出版物；写入28条bibliography_lists_publication statement与28条精确mention。复用24个既有archive候选并补全题名等出版项，新建4个archive候选cand-11406–cand-11409。Northall的cand-10216在主迁移后经单条受控补记补全；上一段创建的Molinier作者候选cand-11401仍保留身份未定状态。

页图确认并记录：Moroni词典条目续文含109卷、威尼斯1840–79年，OCR段漏掉该出版项；L849印本为Moschini而OCR作Meschini，候选与既有相近拼写引用保持分立供S3；L861完整识别Müntz与Molinier合著文章及1885年页码范围，因而将L820作者指引状态改为目标已核对，但不据此确定Molinier个人身份。L876将OCR粘连的Nicodemi与Nisser两条拆成独立引句；另校读期刊卷次、姓名撇号、书名、日期及标点。原始OCR未改写。

受控主迁移脚本默认dry-run，锁定规范Markdown、PDF和段落指纹，核对表前态、候选类型、statement外键、逐行引句与mention字符偏移；应用前为四表保存.bak-s2-chp21-bibliography-l846-881-20261007副本。Northall补记脚本另锁定同一段指纹和现有书目statement，并为候选表保存.bak-s2-chp21-bibliography-l846-881-northall-20261007副本。写入后段级检查确认28条statement、28条mention，引用、外键、字符偏移有效且mention不重叠；全表审计errors=[]、s2_missing=[]。当前11,388候选、26,543 mentions、11,816 statements；832段中606 complete、121 excluded、105 queued、0 partial。下一书目段L883–926；余11个书目段与94个索引段。机械审计不替代全书S2语义交接。

## 书目L883–926：出版物条目（PDF物理页22，印刷p.432；2026-10-07）

对照规范来源及PDF页图处理L884–926；L883的`[Page 432]`仅为页码标记，本页共有31条出版物记录。复用28个archive候选，补全27个（`cand-7137`的Orlandi条目此前已完整），新增3个`cand-11410`–`cand-11412`；写入31条精确mention及31条`bibliography_lists_publication` statement。新候选依次为d’Onofrio 1967、Pallucchini 1952及仅有姓氏的Panciroli 1625。

页图校读：L889标题续行的短横按印本保留在`title_as_printed`；L896页码范围校为158–162；L898、L914的OCR`voi.`校为印本`vol.`；L911将`VÌI`校为`VII`并去除OCR重复句点；L917的行首扫描符号和尾随OCR短横不并入Piazzetta题名；L924–925去除`the`中的OCR重音。L894、L897行末短横按页图记作版面短横，不并入出版项字段。L921未给Panciroli名字或首字母，原样保留姓氏；L926确认方括号作者名`Ermalao Paoletti`，不作规范化。原始OCR不改写。

Nuti条目与Pasquali候选、1652及1973年Ottonelli著作版本、Palomino另一卷页定位保留S3比较入口，不在书目S2中裁决同一性；本段不把书目列表转写为历史关系，也不声称独立阅读被列出版物。受控迁移脚本锁定来源、PDF、段落指纹和表前态；首轮dry-run发现脚本内候选登记块重复，修正后dry-run通过，未发生部分写入。apply前为四表保存`.bak-s2-chp21-bibliography-l883-926-20261007`恢复副本。写入后31条statement、31条mention的外键、逐行引句、字符偏移与不重叠检查通过；`audit_tables.py --summary`为`errors=[]`、`s2_missing=[]`。当前11,391候选、26,574 mentions、11,847 statements；832段中607 complete、121 excluded、104 queued、0 partial。下一书目段L928–983；余10个书目段和94个索引段。机械审计不替代全书S2语义交接。

## 书目L928–983：出版物条目（PDF物理页23，印刷p.433；2026-10-07）

对照规范源L929–983及PDF物理页23逐条处理32条书目记录；L928的`[Page 433]`仅为页码标记。复用23个既有archive候选并补全其书目字段，新建9个`cand-11413`–`cand-11421`；写入32条精确mention和32条`bibliography_lists_publication` statement。候选复用包括Paolo Giordano II的1649年诗集、Paravia、Parker、Passeri、Patrignani、两项Pecchiai、Pellegrini、Perez Sanchez、Pergola、Pesenti、两项Petrocchi、Pieraccini、Pierantoni、Pietro da Cortona展览、Pignatti、两项Pinetti、Pintard、Pittura del Seicento a Venezia及Poirier。新增Pascoli 1933双卷影印本、未标卷次的Pastor 1943意大利文版、Peiresc七卷书信集、Pevsner著作、Pigage著作、Pirri和Pisano论文、von Platen编本、Pollak 1927/1931双卷本。

页图校读：Paolo Giordano II题名为`Rime e Satire`（OCR作Satira）；Parker的`the`无重音；Passeri年代为1641；Perez Sanchez国名为España；Pesenti行首句点、Pignatti的`i960`及Pietro da Cortona展览标题双短横为OCR伪差。Patrignani期刊`Rivista italiana di Numismatica`、两条Pinetti期刊名、Pirri的`Archivum Historicum Societatis Jesu`及Pisano的`Roma`在S0中有片段错排，页图确认其所属条目；保留S0引句行序并在statement记页图解释。Pinetti 1916/1920分开为两篇文章；L958、L962、L967、L971的刊名片段分别回接对应作者行。页图还核对Passeri 1934版、Pascoli I/II卷及1933影印本、Patrignani页码、Pellegrini展览目录、Pignatti与Mariacher不同年代的Museo Correr目录，以及Pollak 1913补编项；被引出版物均未独立查阅。

保留后续S3比较边界：Pascoli合卷影印本与既有分卷候选、Pastor无卷次书目条目与第XII/XIII/XIV卷引文、Peiresc出版书信与手稿候选、Pellegrini目录的p.15/p.56/plate 92定位、Pollak两卷本与既有分卷引文不合并；Parker、Pevsner、Pigage、Poirier及von Platen的作者候选也只作S3身份比较入口。本段不从书目项生成历史关系。

受控迁移脚本默认dry-run，锁定Markdown、PDF、S0分段哈希及表前态；dry-run通过后apply，应用前为四表保存`.bak-s2-chp21-bibliography-l928-983-20261007`恢复副本。迁移后段级验证确认32条statement、32条mention逐一对应L929–983，无源行遗漏或重复；引句、候选外键、字符偏移及mention非重叠检查通过。`audit_tables.py --summary`为`errors=[]`、`s2_missing=[]`；当前11,400候选、26,606 mentions、11,879 statements；832段中608 complete、121 excluded、103 queued、0 partial。下一书目段L985–1020；余9个书目段和94个索引段。机械审计不替代全书S2语义交接。

## 书目L985–1020：出版物条目与跨章引文定位（PDF物理页24，印刷p.434；2026-10-07）

核对规范来源21_CHP-21Bibliography.md的L985–1020及PDF印刷p.434。L985的[Page 434]仅为页码标记；L986–1020有29条出版物记录。原来源哈希为f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3，PDF哈希为1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512，S0段哈希为76480a4c281b0439c39ad8cbf2680ad60a3bb93b46f4b95a4e3a38206a213f70。复用24个archive候选，其中19个补全书目字段；新建5个候选cand-11422–cand-11426。按材料性质写入29条bibliography_lists_publication statement和29条逐行mention；不将出版物内容推作已读事实，不从书目项创建历史关系。

| S0行 | 候选 | 本页书目对象（印本题名／类型） | 处理 |
|---|---|---|---|
| L986 | cand-11422 | Pöllnitz，《Mémoires contenant les observations qu’il a faites dans ses voyages》，三卷本 | 新建；卷II、III引文候选仍分开 |
| L987 | cand-5151 | Ponnelle、Bordet，*St Philip Neri and the Roman society of his times* | 复用并补全 |
| L988 | cand-10513 | Lorenzo da Ponte，*Memorie* | 复用并补全 |
| L989 | cand-4372 | Pope-Hennessy，‘Two portraits of Domenichino’ | 复用并补全 |
| L990–991 | cand-5158 | Pope-Hennessy，*Domenichino drawings in the Royal Library at Windsor Castle* | 复用并补全 |
| L992 | cand-7064 | Pope-Hennessy，‘Some bronze statues by Francesco Fanelli’ | 复用，候选已含题名和页码 |
| L993–994 | cand-8652 | Popham、Wilde，*Italian drawings of the XV and XVI centuries in the Royal Library at Windsor Castle* | 复用并补全 |
| L995 | cand-6352 | Portoghesi，‘I monumenti borrominiani della Basilica Lateranense’ | 复用并补全 |
| L996–997 | cand-4326 | Portoghesi，‘Il palazzo, la villa e la chiesa di S. Vincenzo a Bassano’ | 复用并确认原暂定书目匹配 |
| L998 | cand-10884 | Donald Posner，‘Caravaggio’s homo-erotic early works’ | 复用并补全；作者身份待S3 |
| L999 | cand-4857 | Posse，*Der römische Maler Andrea Sacchi* | 复用并补全 |
| L1000–1001 | cand-9455 | Posse，*Die Staatliche Gemäldegalerie zu Dresden—Erste Abteilung: Die romanischen Länder* | 复用并补全 |
| L1002 | cand-10276 | Posse，Algarotti书信与德累斯顿购画研究（1931增刊） | 复用并补全；与cand-8597信件定位保留S3比对 |
| L1003 | cand-4634 | Poussin，Jouanny编Correspondance | 复用既有版本候选 |
| L1004 | cand-4633 | Poussin，Blunt编展览目录 | 复用既有版本候选 |
| L1005 | cand-9298 | Powell，*From Baroque to Rococo* | 复用并补全 |
| L1006 | cand-11127 | Giovanni da Pozzo，‘Il Testamento dell’Algarotti’ | 复用并补全；与Algarotti 1764年遗嘱原件区分 |
| L1007 | cand-11423 | Mercedes Precerutti Garberi，‘Di alcuni dipinti perduti del Tiepolo’ | 新建 |
| L1008 | cand-4849 | Presenzini，*Vita ed opere del pittore Andrea Camassei* | 复用并补全 |
| L1009 | cand-11424 | Previtali，‘Collezionisti di primitivi nel Settecento’ | 新建；与1964年书及p.301未定短引分开 |
| L1010 | cand-11212 | Previtali，*La Fortuna dei Primitivi dal Vasari ai Neoclassici* | 复用并补全p.410引文 |
| L1011–1012 | cand-11031 | Wolfram Prinz，*Die Sammlung der Selbstbildnisse in den Uffizien*，第I卷 | 复用并补全 |
| L1013 | cand-11185 | Lucia、Ugo Procacci，‘Il carteggio di Marco Boschini con il Cardinale Leopoldo de’ Medici’ | 复用并补全；人名形式留待S3 |
| L1014 | cand-6195 | Prota-Giurleo，*Pittori Napoletani del Seicento* | 复用并补全 |
| L1015 | cand-4861 | Prunières，*L’opéra italien en France avant Lulli* | 复用既有版本候选 |
| L1016 | cand-5598 | Prunières，*La vie et l’œuvre de Claudio Monteverdi* | 复用并校正OCR题名依据 |
| L1017–1018 | cand-7846 | Puliti，Ferdinando dei Medici传记 | 复用既有书目候选 |
| L1019 | cand-11425 | Puppi，‘I Tiepolo a Vicenza e le statue dei “nani” di Villa Valmarana a S. Bastiano’ | 新建；作者按印本记作Lionelli |
| L1020 | cand-11426 | Puppi，‘Carlo Cordellina committente d’artisti’ | 新建；作者按印本记作Lionello |

页图校读并在对应statement保留OCR依据：L986 Memories校为Mémoires；L988与L1004的i960校为1960；L989补回of Domenichino空格；L1006页码i8r-i92校为181–192；L1008将Presenzin!校为Presenzini；L1013将Luda校为Lucia；L1014行首双引号是左边扫描标记，不属于Prota-Giurleo条目；L1015 LuUi校为Lulli，L1016 l’ceuvre校为l’œuvre；L1017 Media, Gran Prindpe校为Medici, Gran Principe；L1019重复逗号),,pp.按页图校为), pp.。印本L1002的Gemäldgalerie及Preuszischen、L1019的Lionelli和L1020的Lionello均照录，不擅自现代化或合并。原S0文件未改写。

这页书目解决了第二版后记p.405两条Puppi引文：note 5的pp.211–250与L1019页码范围相同，故其statement及mention从共享暂定候选cand-11066改接cand-11425；note 6的题名及pp.212–216与L1020相符，改接cand-11426。相应两条正文statement的候选入口同步调整。note 5原引年为1968，书目印作1967–8；保留该差异。两条书目作者形式分别印作Lionelli和Lionello，身份不在S2合并；原共享候选保留为旧分组记录并注释其去向，供S3核对。L1009新建的1959年Previtali论文不拿来裁定p.301“See Previtali”短引；cand-9509仍待S3。Pöllnitz卷次定位、Posse letter no.8、Posner作者身份及其他跨章身份问题均保留对齐入口。上述文献内容未独立阅读。

受控脚本chp21_bibliography_l985_1020_migration.py默认dry-run，锁定Markdown、PDF、S0分段哈希及四表迁移前计数；先dry-run核验后apply，并在写表前为四表保存.bak-s2-chp21-bibliography-l985-1020-20261007恢复副本。目标段核验确认29条mention、29条statement覆盖L986–1020，无漏行、重复或重叠；原文引句、偏移、候选外键和页码映射有效。p.405四条受影响statement与两条mention经前置值、引句、偏移核验后完成重映射。全表audit_tables.py --summary返回errors=[]、s2_missing=[]；当前11,405候选、26,635 mentions、11,908 statements；832段中609 complete、121 excluded、102 queued、0 partial。下一书目段L1022–1057；余8个书目段和94个索引段。机械审计不替代全书S2语义交接。

## 书目L1022–1057：出版物条目与作者交叉指引（PDF物理页25，印刷p.435；2026-10-07）

核对规范来源`21_CHP-21Bibliography.md`的L1022–1057与PDF印刷p.435。L1022为页码标记；L1023–1057逐行覆盖25条出版物和1条作者交叉指引。Markdown哈希为`f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3`，PDF哈希为`1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512`，S0段哈希为`85dd9b22afaa7b6c4bb571221f8a53c1f3a7b79b238790d5df3df1e0225cfcc5`。复用22个archive候选并补全18个，新建3个archive候选`cand-11427`–`cand-11429`；另更新人物候选`cand-5793`与`cand-9930`的来源约束信息。按材料性质记录出版物和交叉指引，不将书目陈述转成历史关系或文献内容断言。

| S0行 | 候选 | 本页条目 | 处理 |
|---|---|---|---|
| L1023–1024 | cand-11427 | Puyvelde，‘Les “Saint Ignace” et “Saint François Xavier” de Rubens’ | 新建；与cand-4976留S3作者对齐 |
| L1025 | cand-11171 | Radcliffe，‘Two Bronzes from the Circle of Bernini’ | 复用并补全；与人物候选cand-10968对齐 |
| L1026 | cand-10478 | Radicchio，*Descrizione della general idea concepita…* | 复用并补全；题名省略号照录，印本作者形式留S3 |
| L1027–1028 | cand-9329 | Rapparini，*Die Rapparini-Handschrift* | 复用并补全；与另一个索引作品候选cand-2108分开 |
| L1029 | cand-10054 | Rava，‘Contributo alla biografia di Pietro Longhi’ | 复用并补全p.340短引 |
| L1030 | cand-10305 | Rava，‘Incisioni su stagno di Francesco Algarotti’ | 复用并补全p.354短引 |
| L1031 | cand-6579 | Rava，‘Il teatro Ottoboni nel Palazzo della Cancelleria’ | 复用既有完整候选 |
| L1032 | cand-4993 | Redig de Campos，‘Intorno a due quadri d’altare di Van Dyck…’ | 复用并补全 |
| L1033 | cand-10189 | Remondini展览目录，G. Barioli编 | 复用并补全；目录未独立阅读 |
| L1034 | cand-8267 | Renaldis，*Memorie storiche dei tre ultimi secoli del patriarcato d’Aquileia* | 复用；关联人物候选cand-8266供S3 |
| L1035–1036 | cand-7069 | *Reni, Guido—catalogo critico della mostra* | 复用；记录编者与导言作者 |
| L1037–1038 | cand-7755 | Amico Ricci，*Memorie storiche delle arti e degli artisti della Marca d’Ancona* | 复用并补全卷数、出版信息 |
| L1039–1040 | cand-7602 | Giuseppe Richa，*Notizie istoriche delle chiese Fiorentine divise ne’ suoi quartieri* | 复用并补全；保留印本`istoriche`拼法，确认10卷 |
| L1041 | cand-4807 | Abbé Richard，*Description historique et critique de l’Italie* | 复用并补全；6卷本信息对应旧卷VI引文 |
| L1042 | cand-5024 | Louis Richeôme，*La peinture spirituelle* | 复用并补全题名 |
| L1043 | cand-4367 | de Rinaldis，‘D’Arpino e Caravaggio’ | 复用并补全题名、卷次及页码 |
| L1044 | cand-4368 | de Rinaldis，‘Le opere d’arte sequestrate al Cavalier d’Arpino’ | 复用并补全题名与页码 |
| L1045 | cand-6605 | de Rinaldis，*Lettere inedite di Salvator Rosa a G. B. Ricciardi* | 复用并补充印本作者形式；旧引文定位保留比较 |
| L1046 | cand-11428 | Rinehart，‘Poussin et la famille dal Pozzo’ | 新建；与cand-5793作者候选留S3 |
| L1047–1048 | cand-5792 | Rinehart，‘Cassiano dal Pozzo (1588–1657), Some unpublished letters’ | 复用并补全；旧引页52落在书目pp.35–59内 |
| L1049 | cand-5793 → cand-5658 | Rinehart “See also Haskell and Rinehart” | 已处理目标L596–597；登记书目交叉指引，不新增正式作者边 |
| L1050–1051 | cand-7352 | Ritschl，*Katalog der Erlaucht Gräflich Harrachschen Gemälde-Galerie in Wien* | 复用并补全 |
| L1052–1053 | cand-9372 | [Rivani]，‘Opere di Donato Creti nella Raccolta della Cassa di Risparmio di Bologna’ | 复用并补全；保留作者方括号及身份不确定 |
| L1054–1055 | cand-10141 | Roberti，‘Lettere inedite di Gasparo Gozzi al tipografo Giambattista Remondini’ | 复用并补全；与cand-10131作者候选留S3 |
| L1056 | cand-11429 | J. G. Robertson，*The genesis of romantic theory* | 新建；与cand-9932、cand-9933两项旧定位分开供S3比较 |
| L1057 | cand-7895 | Robiony，‘La Madonna dal collo lungo di Parmigianino’ | 复用既有完整候选 |

页图核读结果保存在对应statement的校读限定中：L1024的`23ó`校为236，尾随短横不属于条目；L1025的`41842Z`校为418–423；L1026确认`quando fu ...`的印刷省略号，不补写省略内容，并记录`straordinario`后小型上标标记无法判明；L1037核正`2 vols.,`标点；L1039将OCR`¡storiche`读为印本历史拼法`istoriche`，并将`io vols.`读作`10 vols.`；L1043校正1936及577–580；L1044校正断行页码110–118；L1046将`i960,1`读为1960, I；L1055校正326–335；L1056将OCR`}. G.`读为J. G.。原S0文本未改写，作品内容未独立核读。

L1049原文为`Rinehart, S.: See also Haskell and Rinehart.`，目标与已审书目L596–597的`The dal Pozzo collection—some new evidence`相符，映射既有候选cand-5658；目标segment `l577-614`已reviewed/complete。该关系表示书目编排中的交叉指引，不主张独立的作者身份或新增合著事实。p.435另列的Rinehart 1961论文和1960年Poussin论文保持两个独立publication候选；Robertson专著也不据同姓作者与旧短引自动合并。Rivani保留方括号，Radicchio与de Rinaldis既有跨章候选定位及Rinehart作者身份都留S3裁定。

受控脚本`chp21_bibliography_l1022_1057_migration.py`默认dry-run，锁定来源文件、PDF、S0段哈希、前态计数及前序／交叉指引目标状态；dry-run通过后apply，并在写表前为四表保存`.bak-s2-chp21-bibliography-l1022-1057-20261007`恢复副本。迁移后核验26条mention、26条statement、来源行完整覆盖、引句与偏移、候选外键及目标指引；全表计数11,408候选、26,661 mentions、11,934 statements；832段中610 complete、121 excluded、101 queued、0 partial。下一书目段L1059–1100；余7个书目段和94个索引段。机械闭合不替代全书S2语义交接审查。

## 书目L1059–1100（PDF物理页26，印刷p.436；2026-10-07）

对照规范源`21_CHP-21Bibliography.md`的L1059–1100与PDF页图。规范Markdown SHA-256为`f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3`，PDF SHA-256为`1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512`，S0段`chp-21:21_CHP-21Bibliography:l1059-1100` SHA-256为`853a8a80c67691ed8811145b13a8b3d56382dfb8846e3db52fc62392a793eec6`。L1059仅为页码标记；L1060–1100逐行覆盖26条出版物记录，不含作者交叉指引。

| S0行 | 候选 | 条目 | 处理 |
|---|---|---|---|
| L1060–1061 | cand-7579 | van der Rohe，‘The marriage at Cana by Giuseppe Maria Crespi’ | 复用并补全；保持作者原印形式 |
| L1062–1063 | cand-9908 | Rohrlach，‘La collezione di quadri Streit nel Graues Kloster a Berlino’ | 复用并补全；作者身份留S3 |
| L1064–1065 | cand-9877 | Romanin，*Storia documentata di Venezia* | 复用并补全第二版／重印及十卷书目信息；与Romanin人名候选留S3 |
| L1066 | cand-4549 | Romano，*Pasquino e la satira in Roma* | 复用并补全；保留首字母形式 |
| L1067–1068 | cand-11181 | Pierre Rosenberg，‘Un tableau de Volterrano réattribué…’ | 复用并补全；与p.403提及相合，未据此重裁画作归属 |
| L1069–1070 | cand-4384 | Rosi，‘La congiura di Giacomo Centini contro Urbano VIII’ | 复用并补全；作者形式保留为M. Rosi |
| L1071–1072 | cand-11103 | Elisabetta Antoniazzi Rossi，‘Ulteriori considerazioni…’ | 复用并补全；与正文另一拼法的人物候选分开供S3 |
| L1073–1074 | cand-11430 | M. Röthlisberger，‘Les pendants dans l’œuvre de Claude Lorrain’ | 新建archive；与作者候选cand-3502对齐待S3 |
| L1075 | cand-4577 | Röthlisberger，*Claude Lorrain—The Paintings* | 复用；保留既有第I卷引文定位并注明书目列2卷 |
| L1076–1078 | cand-11193 | Stella Rudolph，*Mecenati a Firenze tra Sei e Settecento*两部分 | 复用并补全1971/1972出版信息；与文中合组候选及1973引文分开核对 |
| L1079 | cand-6454 | Ruffo，‘La galleria Ruffo nel secolo XVII in Messina’ | 复用；书目印刷信息已相符 |
| L1080 | cand-9840 | Sagredo，*Sulle consorterie delle Arti edificatorie in Venezia* | 复用；书目印刷信息已相符 |
| L1081 | cand-4324 | Salerno，‘The Picture Gallery of Vincenzo Giustiniani’ | 复用并补全三段页码；不表示已读论文 |
| L1082 | cand-5464 | Salvagnini，*I pittori Borgognone-Cortese* | 复用并补全 |
| L1083 | cand-11431 | Salvino, Salvini，佛罗伦萨教会会吏目录 | 新建archive；连接既有人物候选cand-7506 |
| L1084 | cand-7718 | Santangelo，*Museo di Palazzo Venezia-Catalogo, I—I dipinti* | 复用并校正卷次形式 |
| L1085–1086 | cand-11137 | Santifaller，1976年Schmidt肖像论文 | 复用并补全 |
| L1087–1088 | cand-11139 | Santifaller，1977年Algarotti/Tiepolo论文 | 复用并补全 |
| L1089–1091 | cand-11146 | Santifaller，1978年Rode墓画论文 | 复用并补全；记录广告增刊定位及印本引号位置 |
| L1092 | cand-10618 | Sasso拍卖目录，no.381 | 复用；不推断未印出版年月或地点 |
| L1093 | cand-10601 | Sasso，*Osservazioni sopra i lavori di niello* | 复用并补记Cicogna编者、婚礼出版说明与地点/年份；不裁决作者角色 |
| L1094–1095 | cand-7138 | Saxl，‘The battle scene without a hero…’ | 复用并校正年份及页码范围 |
| L1096 | cand-6440 | Schlosser-Magnino，*La letteratura artistica* | 复用并补全版次、出版地与年份 |
| L1097 | cand-11432 | L. Schudt，*Italienreisen im 17. und 18. Jahrhundert* | 新建archive；保留首字母形式 |
| L1098–1099 | cand-7041 | *Seicento Europeo*展览出版物 | 复用并补记主办方和欧洲委员会支持信息 |
| L1100 | cand-8804 | [Seilern, Count A.]，*Italian paintings and drawings at 56 Princes Gate* | 复用并补全；no.170与本条目是否相同留S3 |

页图校读包括：L1065 `io vols.`→`10 vols.`；L1068 `gioire`→`gloire`并排除条目后的扫描短横；L1069 `Urbano Vili`→`VIII`；L1070 `R-omana`→`Romana`；L1073 `1’œuvre`→`l’œuvre`；L1074 `1958,1`→`1958, I`；L1081 `i960`→`1960`、`13 5-150`→`135–150`；L1084 `VeneZia`→`Venezia`、`1—I`→`I—I`；L1093恢复跨行`Michieli-Segatti`；L1095校正`1939–40`及`70–87`；L1098 `P.L`→`P.I.`。原OCR源文件未改写。保留Salvini书名重音、Sasso目录印本拼写和no.381、Schudt书名、Seilern方括号；Santifaller 1978条目页图的闭引号落在“advertising”之后，作为页图注记，不将增刊说明并入题名。被列出版物均未在本段独立阅读。

本段复用并补全23个既有出版物archive候选；另更新Salvino人物候选cand-7506及Rudolph语境候选cand-11036的来源信息；新建cand-11430–cand-11432三个archive候选。登记26条精确mention及26条`bibliography_lists_publication` statement，`relation_candidate=false`；候选外键、S3对照候选、source quote与行覆盖由受控脚本核验。p.403 Rosenberg短引现可链接到完整书目记录；p.404的Rudolph条目列出1971/1972两个部分，但它与独立的1973引用如何对应仍待S3比较。没有从书目题名推导作品内容或正式关系。

受控脚本`chp21_bibliography_l1059_1100_migration.py`锁定来源、PDF、S0段指纹、迁移前表计数与前序段状态；dry-run通过后apply，并在写入前为四表保存`.bak-s2-chp21-bibliography-l1059-1100-20261007`恢复副本。`python -X utf8 scripts/audit_tables.py --summary`通过：`s2_missing=[]`、`errors=[]`；当前11,411候选、26,687 mentions、11,960 statements；832段中611 complete、121 excluded、100 queued、0 partial。剩余书目段6个，索引段94个；下一段书目L1102–1139。结构审计不替代全书S2语义交接审查。

## 书目L1102–1139（PDF物理页27，印刷p.437；2026-10-07）

对照规范来源21_CHP-21Bibliography.md的L1102–1139与原书PDF物理页27。Markdown SHA-256：f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3；PDF SHA-256：1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512；S0段chp-21:21_CHP-21Bibliography:l1102-1139 SHA-256：f5cc60e16449f246c3cb146f18134a2fabb3bdeaab126afc880e595b26fef707。L1102仅为页码标记；L1103–1139逐行覆盖25条出版物，无作者交叉指引。

| S0行 | 候选 | 条目与处理 |
|---|---|---|
| L1103 | cand-10322 | [Selva, G. A.]目录，Venezia [1776]；补全p.355 note 3候选，精确映射留S3确认 |
| L1104–1105 | cand-11433 | A. Sensier《Le journal de Rosalba Carriera…》，Paris 1865；新建出版物记录，与Sensier及相关信件/文献定位分开比较 |
| L1106–1107 | cand-10447 | G. Sforza《Il testamento d’un bibliofilo…》；补全期刊、系列、卷、年份、页码 |
| L1108–1109 | cand-7847 | Bernardo Sansone Sgrilli《Descrizione della Regia Villa…》；复用既有完整记录 |
| L1110–1111 | cand-11434 | Shaftesbury《Second Characters or The Language of Forms》，Benjamin Rand编，Cambridge 1914；新建edition/archive，区别于work cand-6220 |
| L1112–1113 | cand-11077 | John B. Shipley论Jacopo Amigoni的文章；补全期刊、卷期、年月及页码，与作者候选cand-11076对齐留S3 |
| L1114–1115 | cand-8773 | Étienne de Silhouette《Voyage de France…》，Paris 1770；补全候选，p.268卷I定位仍待精确确认，保留印本异常方括号 |
| L1116–1117 | cand-9066 | O. Sirén《Dessins et tableaux italiens…》，Stockholm 1902；补全候选，p.293/p.304页码匹配供S3核对 |
| L1118 | cand-5502 | Philip Skippon旅行记，收入《A Collection of Voyages and Travels》卷VI，London 1752，pp.359–736；补全p.650定位，p.676与p.679的独立候选保留S3比较 |
| L1119 | cand-7600 | S. Slive《Rembrandt and his critics 1630–1730》；复用既有完整记录 |
| L1120 | cand-9314 | H. Clifford Smith《Buckingham Palace》，London 1930；补全p.280 note 8候选，p.26未独立查阅 |
| L1121 | cand-5592 | A. Solerti《Musica, Ballo e Drammatica alla Corte Medicea…》；复用既有记录 |
| L1122–1123 | cand-5160 | Raffaello Soprani《Vite de’ Pittori…》第二版，Carlo Giuseppe Ratti编注，2卷，Genova 1768；复用既有edition记录 |
| L1124–1125 | cand-11172 | Sotheby’s展览出版物《An Exhibition of Old Master Drawings…》，Plymouth 1979；补全p.401 pp.31–32候选，与Sotheby’s机构cand-9307区别 |
| L1126 | cand-10882 | Luigi Spezzaferro《La cultura del Cardinal Del Monte…》，Storia dell’Arte, 1971, pp.57–92；补全p.397 note 11出版物记录，不据此独立验证Haskell对文章的转述 |
| L1127 | cand-11435 | G. Spini《Ricerca dei libertini》，Roma 1950；新建记录，与人物cand-6375及另一Spini/Limentani出版物cand-6377分开 |
| L1128–1129 | cand-6395 | Jacob Spon与George Wheler《Voyage d’Italie . . .》，2卷，La Haye 1724；补全既有卷I定位，保留书名中的间隔省略号 |
| L1130 | cand-7867 | K. Steinbart《Die Gemalten Schwänke des Pfarrers Arlotto》，Pantheon 1936, pp.233–234；复用既有记录 |
| L1131 | cand-7030 | C. Sterling《Gentileschi in France》，Burlington Magazine 1958, pp.112–120；复用既有记录 |
| L1132 | cand-7048 | L. Stone《The market for Italian art》，Past and Present 1959, pp.92–94；复用既有记录 |
| L1133–1134 | cand-11195 | Maria Letizia Strocchi《Il Gabinetto d’‘opere in piccolo’…》两部分（1975、1976）；补全候选，p.404 note 12对应仍留S3核对 |
| L1135 | cand-5150 | E. Strong《La Chiesa Nuova (S. Maria in Vallicella)》，Roma 1923；补全p.68 note 2已提候选 |
| L1136 | cand-11436 | Stuffmann《Les tableaux de la collection de Pierre Crozat》，Gazette des Beaux-Arts 1968；新建archive，按本书印字保留pp.11–144并记录外部著录差异 |
| L1137–1138 | cand-7268 | J. E. Sweetman《Shaftesbury’s last commission》，Journal of the Warburg and Courtauld Institutes 1956, pp.110–116；复用既有完整记录 |
| L1139 | cand-8330 | G. Tabacco《Andrea Tron e la crisi dell’aristocrazia senatoria a Venezia》，Trieste 1957；补全p.254 note 5 p.38候选，p.123与pp.32 ff.定位仍留S3比较 |

页图校读：L1107将OCR voi. 61校为印本vol. 61；L1111年份后的孤立撇号及L1126页码后的短横不并入书目内容；L1113页码为313–331；L1114印本作者项字面呈S[ilhouette, Étienne de]，保留方括号位置；L1118页码为359–736；L1128书名含间隔省略号，不补写省略内容；L1133印本为Strocchi（非OCR Stracchi），L1134为1976期号311（非OCR zìi）；L1136页码照本书印作11–144；L1138页码校为110–116。原S0 OCR文件未改写。

L1136的页码存在书目记录差异：本书页图读作11–144；National Gallery of Art的藏品书目另列5–142，另一条NGA学术出版注释列1–144，NGA对象PDF中还见11–143；BnF记录的是同题名1968年Gazette单行本、共144页。相关记录分别见[NGA藏品书目](https://www.nga.gov/artworks/provenance/9568-pierre-crozat-younger)、[NGA学术出版注释](https://www.nga.gov/research/publications/french-paintings-fifteenth-through-eighteenth-centuries/french-paintings-fifteenth-through-eighteenth-centuries-ceres-summer-c-17171718)、[NGA对象PDF](https://www.nga.gov/collection/art-object-page.82.pdf)与[BnF目录](https://catalogue.bnf.fr/ark:/12148/cb40341079b)。本次不以外部著录覆盖本书印字，也不声称已核读文章。

本页25条均按bibliography_lists_publication记录，relation_candidate=false，未从书目引用生成历史关系。17个既有候选更新（13个archive、4个人物来源说明），8条复用原已充分的archive候选；另新建4个archive候选cand-11433–cand-11436。保留的跨章比较包括Sensier多个短引、Skippon三个页码定位、Strocchi p.404 note 12、Tabacco三处定位、Silhouette卷次、Sotheby’s机构与展览出版物，以及Shaftesbury work与1914 edition。被列出版物及其引述页均未在本段独立阅读。

受控脚本chp21_bibliography_l1102_1139_migration.py以Markdown/PDF/S0段哈希、迁移前表计数、队列状态及前序段状态为前置条件；dry-run通过后apply，并在写入前为四表保存.bak-s2-chp21-bibliography-l1102-1139-20261007恢复副本。段级检查确认25条mention、25条statement、L1103–1139逐行覆盖、引句唯一、字符偏移有效、候选及S3关联外键有效。写入后全表audit_tables.py --summary为errors=[]、s2_missing=[]；当前11,415候选、26,712 mentions、11,985 statements；832段中612 complete、121 excluded、99 queued、0 partial。下一段书目L1141–1177；余5个书目段和94个索引段。机械闭合不替代全书S2语义交接审查。

## 书目L1141–1177（PDF物理页28，印刷p.438）

核对规范书目源L1142–1177的30条出版物记录；L1141仅为页码行，不计入条目。复用25个既有archive候选，其中20个补全著录；更新Tamizey de Larroque人物候选cand-5833的印本作者形式与来源限定；新建5个archive候选cand-11437–cand-11441。登记30条mention和30条`bibliography_lists_publication` statement，均标记`relation_candidate=false`。被列出版物及所引页均未在本段独立阅读。

| 行 | 候选 | 书目记录与处理 |
|---|---|---|
| L1142–1143 | cand-5467 | P. Tacchi-Venturi，‘Le convenzioni tra Giov. Battista Gaulli e il Generale dei Gesuiti’，Roma 1935，pp.147–156；补全p.80短引，相关页未核读。 |
| L1144 | cand-5492 | Tacchi-Venturi，*La casa di S. Ignazio di Loiola in Roma*，Roma n.d.；保留印本`Loiola`。 |
| L1145 | cand-5834；作者cand-5833 | Tamizey de Larroque，‘Deux testaments inédits’，*Bulletin Critique*，1886-05-15；可能对应p.265的Bouchard遗嘱引文，题名不足以证明，留S3比较。 |
| L1146 | cand-7023 | V. L. Tapié，*La France de Louis XIII et de Richelieu*，Paris 1952；复用已完整候选。 |
| L1147 | cand-6590 | F. M. Tassi，*Vite de’ Pittori, Scultori e Architetti Bergamaschi*，Bergamo 1793；保留卷I与卷II旧定位分别供S3比对。 |
| L1148 | cand-8428 | G. Tassini，*Curiosità Veneziane*，第5版，Venezia 1915；与cand-10687的1887年第4版区分。 |
| L1149–1150 | cand-7089 | F. H. Taylor，*The taste of angels—a history of art collecting from Rameses to Napoleon*，Boston 1948；复用。 |
| L1151 | cand-9957 | T. Temanza，*Vite dei più celebri architetti, e scultori veneziani*，Venezia 1778；补全p.87定位。 |
| L1152 | cand-8799 | D. Cristoforo Tentori，*Saggio sulla storia civile, politica, ecclesiastica e sulla corografia e topografia degli stati della repubblica di Venezia*，12卷，Venezia 1785–90；补全卷X/p.288定位。 |
| L1153–1154 | cand-4569 | Alfred de Terrebasse，*Relation des principaux événements de la vie de Salvaing de Boissieu*，Lyon 1850；补全p.40短引。 |
| L1155 | cand-11437 | G. de Tervarent，*Attributs et symboles dans l’art profane 1450–1600*，Genève 1959；新建，作者名不据首字母扩写。 |
| L1156–1157 | cand-10392 | Mauro Tesi，*Raccolta di disegni originali…*，印本列`Lodovico Inig calcografo`及[Bologna 1787]；保留`Inig`印字，p.358 n.3所引“introduction”的对象边界留S3澄清。 |
| L1158（前段） | cand-9779 | A. Tessier，‘Di Francesco Maggiotto—pittore veneziano’，*Archivio Veneto* 1882，pp.289–315；精确引句截至`289315`。 |
| L1158（后段） | cand-11438 | Girolamo Teti，*Aedes Barberinae ad Quirinalem a comite Hieronymo Tetio Persino descriptae*，Romae MDCXLII；与Tessier共用源行但mention字符范围互不重叠，姓名实体对齐留S3。 |
| L1159 | cand-4837 | J. Thuillier，‘Un peintre passionné’，*L’Œil* no.47，1958年11月，pp.26–33；按页图恢复OCR的`L’CEil`。 |
| L1160 | cand-5805 | J. Thuillier，‘Pour un “Corpus Poussinianum”’，*Actes du Colloque Poussin*，1960，vol.II，pp.49–238；恢复年份`1960`。 |
| L1161 | cand-8792 | *Tiepolo—catalogo della mostra a cura di Giulio Lorenzetti*，Venezia 1951；补全p.270 n.3的展览目录候选，目录及p.8未核读。 |
| L1162–1163 | cand-5493 | H. Tietze，‘Andrea Pozzo und die Fürsten Liechtenstein’，*Jahrbuch für Landeskunde von Niederösterreich*，1914–15，pp.432–446；复用既有记录。 |
| L1164 | cand-7350 | H. Tietze，‘Eugenio di Savoia amico dell’arte’，*Le Vie d’Italia e del Mondo*，1933，pp.891–907；补全书目信息。 |
| L1165–1166 | cand-10451 | Emilio de Tipaldo，*Descrizione della deliziosa villa di Sala di proprietà del signor Demetrio Mircovich*，Venezia 1833；剔除OCR尾随扫描符号。 |
| L1167 | cand-11439 | Emilio de Tipaldo，*Biografia degli Italiani illustri…*，10卷，Venezia 1834–45；新建，与1833年villa出版物分开，按页图恢复`10 vols.`。 |
| L1168 | cand-9346 | L. Toesca，‘Alessandro Galilei in Inghilterra’，*English Miscellany*，Roma 1952，pp.189–220；旧注释作者写Ilaria Toesca，书目写L. Toesca，身份/映射留S3。 |
| L1169 | cand-4333 | L. Toesca，‘Note sulla storia del Palazzo Giustiniani a San Luigi dei Francesi’，*Bollettino d’Arte*，1957，pp.296–308；补全。 |
| L1170 | cand-10476 | Gianfranco Torcellan，*Una figura della Venezia settecentesca: Andrea Memmo*，Venezia–Roma 1963；恢复断行处城市间连接号，补全p.364/p.367定位。 |
| L1171 | cand-11110 | Gianfranco Torcellan，*Settecento veneto e altri scritti storici*，Torino 1969；补全。 |
| L1172 | cand-7002 | E. du Gué Trapier，*Ribera*，New York 1952；复用。 |
| L1173 | cand-5801 | K. Trauman-Steinitz，‘Poussin illustiator of Leonardo da Vinci’，*Art Quarterly*，1953年春，pp.40–55；页图确认为`illustiator`，保留印本疑似拼误。 |
| L1174 | cand-11440 | L. Treat，*Un cosmopolite italien du XVIIIème siècle—Francesco Algarotti*，Trévoux 1913；新建。 |
| L1175 | cand-9303 | A. S. Turberville，*A history of Welbeck Abbey and its owners*，London 1939；补全p.280 n.2卷II/p.14定位，原书及引页未核读。 |
| L1176–1177 | cand-11441 | Nicholas Turner，‘Ferrante Carlo’s Descrittione della Cupola di S. Andrea della Valle depinta dal Cavalier Gio: Lanfranchi; a source for Bellori’s descriptive method’，*Storia dell’Arte*，1971，pp.297–325；新建，保留印本`Descrittione`。 |

页图确认L1158实际是两条相邻书目；OCR把Tessier的`pp. 289315`与Teti作者名粘连，故拆成两个同源行mention，分别使用原行内唯一、互不重叠的字符跨度。其他校读包括：L1159的`L’CEil`→`L’Œil`；L1160的`i960`→`1960`；L1166尾随`■ .`为扫描/OCR杂符；L1167的`io vols.`→`10 vols.`；L1170的`VeneziaRoma`依页图断行恢复为`Venezia–Roma`；L1172尾随撇号为OCR杂符。L1157的`Inig`和L1173的`illustiator`经页图确认后保留，不作猜测性规范化。

跨章候选映射只作为后续比较入口：cand-5834/Tamizey与p.265遗嘱引文、cand-6590的卷I/II定位、cand-10392所指introduction的实体边界、cand-8792的展览目录、cand-9346的Toesca作者形式、cand-9303的Turberville卷页定位均未在S2裁定。没有新增正式关系，relations.csv未改。

受控脚本`chp21_bibliography_l1141_1177_migration.py`锁定来源Markdown、PDF、S0段哈希和迁移前规模，默认dry-run；apply前已备份entity-candidates、mentions、book-statements、s2-coverage四表。dry-run及apply分别写入21项既有候选更新（20个archive及1个人物）、5个新archive、30条mention、30条statement。独立段级核验与全表审计通过：`s2_missing=[]`、`errors=[]`；当前11,420个候选、26,742条mention、12,015条statement；832段中613 complete、121 excluded、98 queued、0 partial。下一段为L1179–1218，尚有4个书目段和94个索引段。机械闭合不代表全书S2语义交接完成。

## 书目L1179–1218（PDF物理页29，印刷p.439）

核对规范书目源L1180–1218的28条出版物；L1179仅为页码行，不计入条目。复用20个既有archive候选并补全其中13个，更新2个人物候选的印本来源信息，新建8个archive候选cand-11442–cand-11449。登记28条mention和28条`bibliography_lists_publication` statement，均标记`relation_candidate=false`。条目与跨章候选映射如下：

| 行 | 候选 | 书目记录与处理 |
|---|---|---|
| L1180 | cand-11192 | *Twilight of the Medici—Late Baroque Art in Florence 1670–1743*，Detroit and Florence 1974；补全p.404 n.9展览出版物候选。 |
| L1181 | cand-11442 | S. Ubaldi，*I Buonaccorsi a Macerata, cenni storici*，Macerata 1950；新建书目候选，与既有Silvio Ubaldi人物/来源候选cand-7734的对应仍待确认。 |
| L1182 | cand-8793 | G. M. Urbani de Ghelthof，*Tiepolo e la sua Famiglia*，Venezia 1879；补全旧引用。 |
| L1183 | cand-11198 | *Urbino—Restauri nelle Marche: testimonianze, acquisti e recuperi*，1973；补全p.404 n.19可能对应的出版物标题；引页未核。 |
| L1184–1185 | cand-4844 | M. Vaes，‘Le séjour de Van Dyck en Italie’，*Bulletin de l’Institut Belge de Rome*，1924，pp.163–234；补全p.211 n.3，并校正期刊名和起页OCR。 |
| L1186–1187 | cand-7584 | M. Vaes，‘Corneille de Wael (1592–1667)’，同刊，1925，pp.137–247；与p.171旧定位cand-6387建立S3比较入口，不提前合并。 |
| L1188–1189 | cand-6997 | M. Vaes，‘Appunti di Carel van Mander su vari pittori italiani suoi contemporanei’，*Roma*，1931，pp.193–208；补全p.202定位。 |
| L1190 | cand-11443 | F. Valcanover，‘Per Luca Carlevaris’，*Arte Veneta*，1952，pp.193–194；新建。 |
| L1191–1192 | cand-7621 | A. C. P. Valery，*Voyages historiques, littéraires et artistiques en Italie*，第2版，3卷，Paris 1838；复用。 |
| L1193 | cand-11444 | J. Valfrey，*Hugues de Lionne—ses ambassades en Italie 1642–1656*，Paris 1877；新建。 |
| L1194 | cand-11445 | G. della Valle，*Lettere Sanesi*，3卷，Roma 1782–86；新建，保留印本作者形式。 |
| L1195–1196 | cand-11116 | *Vassar College Art Gallery—Selections from the Permanent Collection*，Poughkeepsie, N.Y. 1967；补全p.408 n.5目录候选，和机构cand-11115分开；目录及p.24未核。 |
| L1197 | cand-8798 | A. Vecchi，‘La vita spirituale’ in *La Civiltà Veneziana del Settecento*，Venezia 1960；补全p.271 n.3短引，正文代词所指歧义仍保留。 |
| L1198 | cand-11446 | G. da Venezia，‘Il Metastasio di P. A. Novelli’，*Rivista di Venezia*，1934，pp.25–34；新建。 |
| L1199 | cand-11447 | *Venise au dix-huitième siècle*，Paris (Orangerie), 1971；新建展览出版物记录，不扩写为事件。 |
| L1200 | cand-4354 | A. Venturi，*La R. Galleria Estense in Modena*，Modena 1883；复用，作者人物候选cand-7054仍保留印本首字母。 |
| L1201 | cand-11448 | F. Venturi，‘Un amico di Beccaria e di Verri: Profilo di Giambattista Biffi’，*Giornale Storico della Letteratura Italiana*，1957，pp.37–76；新建，与Franco Venturi候选cand-2751留S3核对。 |
| L1202 | cand-11209 | F. Venturi，*Settecento riformatore*，2卷，Torino 1969、1976；补全1969引文候选，1976引文cand-11210保留供S3比对。 |
| L1203 | cand-5690 | C. Vermeule，‘The dal Pozzo-Albani drawings of classical antiquities’，*Art Bulletin*，1956，pp.32–46；补全现代研究引文。 |
| L1204–1205 | cand-7255 | George Vertue，*Notebooks*，Walpole Society 1930–55；保留印本文义“6 vols. and an index”，目录列卷XVIII、XX、XXII、XXIV、XXVI、XXIX及索引XXX，不合并成7卷。 |
| L1206–1207 | cand-9471 | V. Viale，‘Un dipinto del Pannini con la veduta orientale del Castello di Rivoli secondo il progetto originale di Filippo Juvarra’，*Bollettino della Società Piemontese di Archeologia e Belle Arti*，1950–1，pp.161–169；复用并校正尾随扫描标记。 |
| L1208 | cand-11449 | Don Giovanni Vianelli，*Catalogo di quadri esistenti in casa il signor Don Giovanni Dr Vianelli canonico della cattedrale di Chioggia*，Venezia 1790；新建。 |
| L1209–1210 | cand-7588 | Ludovico de la Ville sur-Yllon，‘Il palazzo dei duchi di Maddaloni alla Stella’，*Napoli Nobilissima*，1904，pp.145–147；复用。 |
| L1211 | cand-8435；作者cand-8434 | Frédéric Villot，‘Lettre de Charles-Nicolas Cochin sur les artistes de son temps’，*Archives de l’Art Français*，vol.I，1851–2，pp.169–176；补全标题并按页图补出作者名。 |
| L1212–1213 | cand-10905 | Gianni Eugenio Viola，*Il verso di Narciso—tre tesi sulla poetica di Giovan Battista Marino*，Roma 1978；补全候选，与p.398 n.5的surname-only Viola/cand-10904可能对应，但相关性未证实，留S3。 |
| L1214–1215 | cand-4728 | W. Vitzthum，‘A comment on the iconography of Pietro da Cortona’s Barberini ceiling’，*Burlington Magazine*，1961，pp.427–433；补全p.4与p.96引文。 |
| L1216 | cand-5692 | W. Vitzthum，‘Roman drawings at Windsor Castle’，*Burlington Magazine*，1961，pp.513–518；补全p.4 n.2引文。 |
| L1217–1218 | cand-9552 | Frances Vivian，‘Joseph Smith and Giovanni Antonio Pellegrini’，*Burlington Magazine*，1962，pp.330–333；复用已具题名和页码的候选。 |

页图校读确认L1184期刊名为`l’Institut`，L1185页码为163–234；L1189尾随的短横和撇号为扫描/OCR杂符；L1211行首下划线及行末撇号不属印本；L1207尾随短横、L1216尾随逗号为杂符；L1215 OCR将433拆开，L1218将333后的句点误为短横。原S0 OCR不改写。出版物本身和书目所引页均未在本段独立阅读。没有新建正式关系或改动relations.csv。

受控脚本`chp21_bibliography_l1179_1218_migration.py`锁定Markdown/PDF/S0段哈希、迁移前计数、当前队列状态和前一段完成状态，默认dry-run；apply前为entity-candidates、mentions、book-statements、s2-coverage保存恢复副本。dry-run及apply写入15项候选更新（13个archive、2个人物）、8个新archive、28条mention、28条statement。段级引句、字符偏移、行覆盖和外键检查通过；全表审计`errors=[]`、`s2_missing=[]`。当前11,428候选、26,770 mentions、12,043 statements；832段中614 complete、121 excluded、97 queued、0 partial。下一段书目L1220–1259；剩余3个书目段和94个索引段。机械通过不等于全书S2语义交接完成。

## 书目L1220–1259（PDF物理页30，印刷p.440）

核对规范书目源L1221–1259的28条出版物；L1220仅为页码行。复用并补全21个既有archive候选，更新7个人物候选的书目作者形式，新建4个archive候选cand-11450–cand-11453。登记28条mention与28条`bibliography_lists_publication` statement，均标记`relation_candidate=false`。

| 行 | 候选 | 书目记录与处理 |
|---|---|---|
| L1221–1222 | cand-11450 | Frances Vivian，‘Joseph Smith, Giovanni Poleni and Antonio Visentini’，*Italian Studies*，1963，pp.54–66；新建，与p.308的1963年pp.157–162候选cand-9560因页码不同留S3比较。 |
| L1223 | cand-11092 | Frances Vivian，*Il Console Smith mercante e collezionista*，Vicenza 1971；补全正文已提及的Consul Smith专著候选。 |
| L1224–1225（前段） | cand-9359 | H. Voss，‘Gio Antonio Canal und Owen McSwiny’，*Repertorium für Kunstwissenschaft*，1926，pp.32–37；补全p.287 n.6短引。 |
| L1225（后段） | cand-5875 | H. Voss，‘Die Flucht nach Aegypten’，*Saggi e Memorie di Storia dell’Arte*，Venezia 1957，pp.25–61；补全旧定位。 |
| L1226 | cand-4570 | D. P. Walker，*Spiritual and demonic magic from Ficino to Campanella*，London 1958；补全书名，卷页引用不据此作内容验证。 |
| L1227 | cand-7001 | J. Walker，*Bellini and Titian at Ferrara*，London 1956；补全题名，作者身份仍待对齐。 |
| L1228 | cand-7058 | Horace Walpole，*Anecdotes of Painting in England*，5卷，Strawberry Hill 1726（照印本）；保留与既有1762年卷II/p.51短引的日期/版本差异。 |
| L1229 | cand-8596 | Horace Walpole，*Aedes Walpoliane*，第3版，London 1767；保留印本题名拼法。 |
| L1230–1231 | cand-6580 | E. K. Waterhouse，‘Some Old Masters other than Spanish at the Bowes Museum’，*Burlington Magazine*，1953，pp.120–123；补全p.120定位。 |
| L1232 | cand-7259 | E. K. Waterhouse，‘A note on British collecting of Italian pictures in the later seventeenth century’，*Burlington Magazine*，1960，pp.54–58；补全期刊和页码。 |
| L1233–1234 | cand-11452 | E. K. Waterhouse，‘Painting in Rome in the Eighteenth Century’，*Museum Studies*, Art Institute of Chicago，1971，pp.7–21；新建。 |
| L1235 | cand-11451 | F. J. B. Watson，*Canaletto*，London 1949；新建。 |
| L1236–1237 | cand-9354 | F. J. B. Watson，‘The Nazari—a forgotten family of Venetian portrait painters’，*Burlington Magazine*，1949，pp.75–79；补全p.287 n.3引文。 |
| L1238–1239 | cand-9367 | F. J. B. Watson，‘An allegorical painting by Canaletto, Piazzetta and Cimaroli’，*Burlington Magazine*，1953，pp.362–365；补全p.287 n.6引文。 |
| L1240–1241 | cand-9316 | F. J. B. Watson，‘A Venetian Settecento chapel in the English countryside’，*Arte Veneta*，1954，pp.295–301；补全旧引用。 |
| L1242–1243 | cand-9301 | F. J. B. Watson，‘English villas and Venetian decorators’，*Journal of the Royal Institute of British Architects*，1954；页图所见页码似为pp.11–177，照录并与旧引pp.171–177留待S3比较。 |
| L1244 | cand-10304 | F. J. B. Watson，‘Giovanni Battista Tiepolo: a masterpiece and a book’，*Connoisseur*，1955，vol.136，pp.212–215；补全p.354 n.3的p.214候选。 |
| L1245–1246 | cand-9893 | F. J. B. Watson，‘A series of “Turqueries” by Francesco Guardi’，*Baltimore Museum of Arts Quarterly*，Fall 1960，pp.3–13；补全题名和期刊。 |
| L1247 | cand-11453 | Mark S. Weil，*The History and Decoration of the Ponte S. Angelo*，Pennsylvania 1974；新建，与surname-only作者候选cand-11178关联待对齐。 |
| L1248 | cand-7267 | W. Wells，‘Shaftesbury and Paolo de Matteis’，*Leeds Art Quarterly*，Spring 1950，pp.23–28；复用。 |
| L1249–1250 | cand-11180 | Harold R. Wethey，‘The Spanish Viceroy, Luca Giordano and Andrea Vaccaro’，*Burlington Magazine*，1967，pp.678–686；补全p.402 n.6候选与作者形式。 |
| L1251 | cand-9349 | H. B. Wheatley，*London past and present*，London 1891；补全p.286 n.3卷III/p.18短引。 |
| L1252 | cand-7066 | M. Whinney与O. Millar，*English Art, 1625–1714*，Oxford 1957；复用。 |
| L1253 | cand-9898 | D. Maxwell White与A. C. Sewter，‘Piazzetta’s so-called Group on the Sea shore’，*Connoisseur*，1959，vol.143，pp.96–100；补全p.314 n.2候选。 |
| L1254–1255 | cand-10903 | Clovis Whitfield，‘A Programme for “Erminia and the Shepherds” by G. B. Agucchi’，*Storia dell’Arte*，1973，pp.217–229；补全后记n.4引文。 |
| L1256 | cand-9356 | W. T. Whitley，*Artists and their friends in England 1700–1799*，2卷，London 1928；补全p.287 n.4。 |
| L1257–1258 | cand-6368 | N. Wibiral，‘Contributi alle ricerche sul Cortonismo in Roma—I pittori della Galleria di Alessandro VII nel Palazzo del Quirinale’，*Bollettino d’Arte*，1960，pp.123–165；补全。 |
| L1259 | cand-7185 | F. Wilhelm，‘Neue Quellen zur Geschichte des fürstlich Liechtensteinschen Kunstbesitzes’；本页只见题名，条目续至印刷p.441 L1262–1263，下一段补全期刊与页码。 |

页图确认L1224、L1225两处OCR`EL`实际为`H.`；L1225把Voss 1926与1957两条粘连，已在同源行中拆为两个互不重叠的mention，并补录两条之间的句点。其他OCR校读：L1227将`}`校为J并移除尾随逗号；L1232、L1246、L1258的`i960`校为1960；L1234补回`pp.`标点；L1241补回页码标点；L1242将`fournal`校为`Journal`；L1248将`2328`校为23–28；L1250短横、L1252行首`~"`为扫描/OCR杂符。Walpole日期1726及Watson文章页码11–177照页图保留，不按外部推断改写。原S0 OCR不改写。被列出版物及所引页均未在本段独立阅读；未新增正式关系或改动relations.csv。

受控脚本`chp21_bibliography_l1220_1259_migration.py`锁定来源/PDF/S0段哈希、迁移前计数、当前队列与前段完成状态，默认dry-run；apply前为四表保存恢复副本。dry-run及apply写入28项候选更新（21个archive、7个人物）、4个新archive、28条mention、28条statement。段级引句、字符偏移、L1221–1259覆盖和外键检查通过；全表`errors=[]`、`s2_missing=[]`。当前11,432候选、26,798 mentions、12,071 statements；832段中615 complete、121 excluded、96 queued、0 partial。下一段为L1261–1299；另有L1301–1306书目段和94个索引段。机械通过不等于全书S2语义交接完成。


## 书目L1261–1299（PDF物理页31，印刷p.441）

依规范书目段处理L1262–1299；L1261仅为页码行。L1262–1263续完p.440 L1259的F. Wilhelm条目，不另计出版物；随后逐项记录23条新出版物。核对段哈希及整页扫描，复用19个已有archive候选、更新1个Wilhelm候选，另更新4个人物候选的书目来源形式；新建4个archive候选cand-11454–cand-11457。登记24条mention及24条statement，其中23条bibliography_lists_publication、1条bibliography_continues_publication。

| 行 | 候选 | 书目记录与处理 |
|---|---|---|
| L1262–1263 | cand-7185 | Wilhelm, F., ‘Neue Quellen zur Geschichte des fürstlich Liechtensteinschen Kunstbesitzes’续行；补全Jahrbuch des Kunsthistorischen Institutes der K.K. Zentralkommission, 1911, Beiblatt, pp.87–142。与p.440条目合为一项书目，不重复计数。 |
| L1264–1265 | cand-11454 | E. Wind, ‘Shaftesbury as a patron of art’, Journal of the Warburg and Courtauld Institutes, II, 1938–39, pp.185–188；新建。 |
| L1266–1267 | cand-7230 | E. Wind, ‘Julian the Apostate at Hampton Court’,同刊III卷，1939–40，pp.127–137；页图复核完整书目形式。 |
| L1268–1269 | cand-7111 | R. Wittkower, ‘Domenico Guidi and French classicism’,同刊II卷，1938–39，pp.188–190；复用。 |
| L1270–1271 | cand-9311 | R. Wittkower, The Earl of Burlington and William Kent，York Georgian Society，1948；补全p.280注6短引。 |
| L1272 | cand-4383 | R. Wittkower, The sculptures of Gian Lorenzo Bernini，London 1955；复用。 |
| L1273 | cand-4557 | R. Wittkower, Art and architecture in Italy 1600 to 1750，London 1958；页图确认OCR的“195 8”为1958。 |
| L1274–1275 | cand-11170 | R. Wittkower, Gian Lorenzo Bernini—the Sculptor of the Roman Baroque，第2版，London 1966；补全p.401注3短引。 |
| L1276–1277 | cand-11368 | R. Wittkower与Irma Jaffé编，Baroque Art: The Jesuit Contribution，New York 1972；页图确认OCR的Jaffe应为Jaffé。与p.398注7候选cand-10910的具体篇章对应关系留S3。 |
| L1278–1279 | cand-9010 | J. Woodward, ‘Amigoni as portrait painter in England’, Burlington Magazine, 1957, pp.21–23；补全p.215注2来源。 |
| L1280–1281 | cand-11455 | Edward Wright, Some observations made in travelling through France, Italy &c in the years 1720, 1721 and 1722，2卷，London 1730；新建。与p.261、p.312的两个页码候选cand-8582、cand-9888保持分列，留S3比对。 |
| L1282 | cand-10534 | Giustiniana Wynne-Rosenberg, Alticchiero，页图读作à Padoue 1787；既有候选记作Venezia 1787，保留地点差异供S3/来源核对。 |
| L1283 | cand-9548 | Prosdocimo Zabeo, Memorie intorno l’antiquario Alvise Meneghetti，Venezia 1816；仅登记书目，p.16来源适配性未核实。 |
| L1284 | cand-10117 | A. M. Zanetti, Varie pitture a fresco de’ principali maestri veneziani，Venezia 1760；复用，作者归属留S3。 |
| L1285 | cand-9837 | A. M. Zanetti, Della Pittura Veneziana，Venezia 1771；补全书目作者形式，作者归属留S3。 |
| L1286–1287 | cand-9281 | Girolamo Zanetti, Elogio di Rosalba Carriera letto in una privata sessione dell’Accademia di Belle Lettere ed Arti in Padova il di 6 Dicembre 1781，Venezia 1818；区分题名中的宣读日期与出版年。 |
| L1288–1289 | cand-11456 | [Zanetti, Girolamo], ‘Memorie per servire all’istoria dell’inclita città di Venezia’, Archivio Veneto, 1885, pp.93–148；新建，保留印本方括号作者形式。既有1743年报告及1885年页码定位cand-8781、cand-8816、cand-10415留S3核对。 |
| L1290–1291 | cand-11457 | Diego Zannandreis, Le vite de’ Pittori, Scultori e Architetti Veronesi，注明由Giuseppe Biadego编，Verona 1891；新建，既有p.255与p.327页码候选cand-8360、cand-9819及人物cand-8359留S3比对。 |
| L1292 | cand-7115 | G. P. Zanotti, Storia dell’Accademia Clementina，2卷，Bologna 1739；复用。 |
| L1293–1294 | cand-8794 | Padre Maestro Valerio Antonio Zarzabini, Serie storica de’ Religiosi Carmelitani，Venezia 1779；补全p.270注6的p.19短引。 |
| L1295 | cand-5166 | F. Zeri, La Galleria Spada in Roma，Firenze 1953；补全p.175短引。 |
| L1296 | cand-5135 | Federico Zeri, Pittura e Controriforma，Torino 1957；补全p.146短引。 |
| L1297–1298 | cand-9912 | H. Zimmermann, ‘Über einige Bilder der Sammlung Streit im Grauen Kloster zu Berlin’, Zeitschrift für Kunstwissenschaft, 1954, pp.197–224；L1298行首引号为OCR杂符。人物cand-9911仅补作者形式。 |
| L1299 | cand-9364 | G. Zucchini, ‘Quadri inediti di Donato Creti’, Comune di Bologna, 1933, pp.23–30；补全p.287注6短引；人物cand-9363仅补作者形式。 |

原S0 OCR不改写。页图复核确认L1273的1958、L1276的Jaffé重音符、L1298 journal标题前无引号；未据外部知识更正。Wynne-Rosenberg地点差异与跨章文献/作者对应保留S3。该段未新建正式关系；书目条目及所引出版物内容均未独立阅读。

受控脚本chp21_bibliography_l1261_1299_migration.py锁定来源、PDF、S0段哈希、表前态及前段完成状态，默认dry-run；apply前为四表保存恢复副本。dry-run与apply写入24项候选更新（20个archive、4个人物）、4个新archive、24条mention和24条statement。段级检查确认L1262–1299逐行覆盖，提及字符偏移与statement原句精确、候选外键完整且无重叠。全表audit_tables.py --summary返回errors=[]、s2_missing=[]。当前11,436候选、26,822 mentions、12,095 statements；832段中616 complete、121 excluded、95 queued、0 partial。下一段为L1301–1306，另有94个索引段。机械通过不等于全书S2语义交接完成。

## 书目末尾错位 OCR 块 L1301–1306

规范书目文件将这段扫描/OCR 收在 `**Footnotes:**` 标签下，但它不是新的脚注材料：L1302–1306 分别是前面已处理书目页 p.413、414、423、424、431 的错位续行或完整条目转录。逐页图像及前段 statement 已提供印本依据。本段保留 S0 原文，不改写来源；L1301 是结构标签，不计作内容行；L1302–1306 全部完成逐项定位。

| S0行 | 候选 | 精确处理与既有依据 |
|---|---|---|
| L1302 | cand-11238 | `2 vols., 1877-8.` 链接到 p.413 的 `st-chp21-bib-l87-127-entry-12`；该印本续行补全 Barozzi–Berchet 两卷本，不重复列书目。 |
| L1303 | cand-9439 | `2 vols., London 1834.` 链接到 p.414 的 `st-chp21-bib-l129-163-entry-06`，补 Beckford 条目续行。 |
| L1303 | cand-4805 | 同行 Bellori《Nota delli Musei…》完整转录链接到 p.414 页图增补 `st-chp21-bib-l129-163-page-image-omission-01`；不另造书目断言，版本身份仍待 S3。 |
| L1304 | cand-11332 | `4 vols., Roma 1939-42.` 链接到 p.423 的 `st-chp21-bib-l498-536-entry-04`，补 Giuseppe Gabrieli 条目续行。 |
| L1304 | cand-11333 | Noemi Gabrieli 的 `Aggiunte a Sebastiano Ricci` 转录链接到 p.423 页图增补 `st-chp21-bib-l498-536-page-image-noemi-01`；出版物未独立阅读。 |
| L1305 | cand-11347 | `3 vols., Londres 1764.` 链接到 p.424 的 `st-chp21-bib-l538-575-entry-11`，补 Grosley 条目续行。 |
| L1306 | cand-7696 | `109 vols., Venezia 1840-79.` 链接到 p.431 的 `st-chp21-bib-l846-881-entry-01`，补 Moroni 词典的卷数与刊行年。 |

受控迁移脚本 `chp21_bibliography_l1301_1306_migration.py` 以来源、PDF、分段哈希和四表前态为前置条件，默认 dry-run。新增 7 条精确 mention 和 7 条 `bibliography_displaced_ocr_cross_reference` statement，并在原 statement 上反向登记来源行及交叉引用 ID；更新 7 个候选说明以去除“待本段补链”的过时措辞。未新建候选、出版物列举断言或正式关系。上述出版物内容均未独立查阅。

首轮写入后的机械审计发现 `s2-coverage.csv` 的行范围分隔符与校验契约不符。使用写前恢复副本还原四表（副本与迁移前 Git 版本逐字节一致），将范围格式修为 `L1302-1306` 后重新 dry-run/apply。复核 `python -X utf8 scripts/audit_tables.py --summary`：`errors=[]`、`s2_missing=[]`；全库 11,436 候选、26,829 mentions、12,102 statements；832 段中 617 complete、121 有理由排除、94 queued、0 partial。下一待处理段为 manifest 中首个索引段 `chp-22:22_CHP-22Index:l1-1`；剩余 queued 均为索引段。结构审计不替代全书 S2 语义交接审查。

## 索引首页（PDF物理页1；开篇页码未印，按后页推定p.443）

核对`22_CHP-22Index.md`与`CHP-22Index.pdf`：物理第1页印有INDEX和两栏词头，无可见页码；物理第2页清楚印有444，因此开篇页推定为p.443。S0 L3的`[Page 24]`与PDF不符，是来源中的页标，不是印本页码，coverage现按定位标记排除。开篇页OCR被切成两段：L9–56主要对应左栏，L64–67是Notes说明的OCR残片，L68–109对应右栏；L1为Markdown文件名标题。两栏行次和词头截断均以页图与A.csv对照处理，保留S0原文和PDF。

依全页印本版面与A.csv第0–66行对应：第0–32行为左栏，第33–66行为右栏。65个开放主词头候选的类型已登记（9个institution、55个person、1个event）；候选身份是索引主词头，子项和定位页码仍是导航信息。Alexander VII与Alexander VIII的“see under”别名不另作人物，分别保留到`C.csv#189 / cand-0665`及`O.csv#29 / cand-1794`的目标指向。A.csv#46原始子项`Br¨¹hl`在页图中为`Brühl`，候选已存可见拼法；不改S1原CSV。全页不新增mentions、book statements或正式关系。

首次迁移脚本先登记L1、L3及L9–56，并完成基于全页版面的候选分类；随后发现L64–109仍为独立queued段，故用`chp22_index_p443_l64_109_migration.py`单独审读并关闭该段coverage，不重复更新候选。另将原过程标签p.24更正为“未印页码、推定p.443”。迁移脚本分别锁定来源/PDF/CSV和段哈希；批量写表前留有恢复副本。首次总表审计要求空迁移段显式记录`no_semantic_content`，补齐L9-56及L64-109的协议说明后，最终`errors=[]`、`s2_missing=[]`。全表为11,436候选、26,829 mentions、12,102 statements；832段中619 complete、123有理由排除、90 queued、0 partial。索引尚有2,781个开放且未标类型；下一待处理段按manifest为`chp-22:22_CHP-22Index:l113-168`。结构审计不替代全书S2语义交接审查。

## 索引p.444左栏（S0 L113–168）及页标L111

`CHP-22Index.pdf`物理页2可见印刷页码444。S0 L111的`[Page 444]`单独成段，作为页码导航排除；L113–114为页眉与页码，L115–168转录左栏从“Algarotti, Francesco—continued”到“Arcadia, Society of”。对照页图和S1 A.csv#67–115，为49个仍开放的主词头候选补类型：45个person、2个place、1个term、1个institution。Alticchiero villa与Altieri palace作为建筑地点归place；Arcadia Society归institution；“Anti-papal satire in reign of Alexander VII”是历史语境中的文学政治现象，按概念主题归term，不作为单一event。索引子项（例如书目、作品题名和生平主题）仍从属于主词头，不据此独立造实体、断言或关系。原S0和S1 CSV未改写；本段未新增mentions、book statements或正式关系。

`chp22_index_p444_l113_168_migration.py`默认dry-run，锁定S0/PDF/A.csv与段哈希，并备份候选和coverage表后写入49个类型、关闭L113–168。随后按manifest处理L111页码段，排除为无语义导航。最终总表审计`errors=[]`、`s2_missing=[]`；11,436候选、26,829 mentions、12,102 statements；832段中620 complete、124有理由排除、88 queued、0 partial。索引仍有2,732个开放未分类候选；下一待处理段为`chp-22:22_CHP-22Index:l170-224`。结构审计不替代全书S2语义交接审查。

## 索引p.444右栏（S0 L170–224）

核对`CHP-22Index.pdf`物理页2（印刷p.444）右栏与规范索引段。OCR行170含残缺页眉`S AND PAINTERS`；L176、L178–179、L181–182、L196、L200、L203、L207、L218–221有跨栏串入或识别杂符。按页图校正阅读，不改写S0。右栏从Arconato, Galeazzo延续至Baccinelli/Susanna；`Art dealers` Rome页码在页图为120–125、150，OCR的`IZO`不作为印本文字。L218按页图读作`pictures from collections of Dukes of Modena`，不是`Hom collections`。

对照A.csv#116–154及B.csv#1，共40个开放S1候选依据主词头标注类型：23 person、17 term。人物主词头包括Arconato至Arrighini、Arundel至Azzolini及Baccinelli；`Art dealers`、`Art exhibitions`、`'Artistic temperament'`、`Artist's position in society`和`Artists' status`均是索引的概念主题，归term。`Art exhibitions`的城市、场馆与艺术家子项只提供导航，未指向一个可由本页确定的单一事件；不以定位页码推造事件或关系。Ariosto、Arrighi-Landini和Augustus III项下的作品、文献、场馆及行为子项仍属于S1主词头索引记录，不在索引段另造实体或断言。`Baciccio, see under Gaulli, Giovanni Battista`在S1已有排除别名记录B.csv#0；保留其明确交叉指引，不把它扩为人物端点或正式关系。

受控脚本`chp22_index_p444_rcol_l170_224_migration.py`锁定规范来源、PDF、A/B索引CSV、段哈希及表前态，默认dry-run；逐条预览后应用，仅更新40个候选类型和本段coverage。写前备份候选表与coverage表。迁移未增加mentions、book-statements或relations。脚本回报覆盖621 complete、88 queued、124 excluded；本页迁移后再按manifest单独处理L226–227页标/页眉段。

## 索引p.445页标与页眉（S0 L226–227）

PDF物理页3可见印刷p.445；L226 `[Page 445]`是S0页定位标，L227 `INDEX`是运行页眉，均非索引词头或正文事实。coverage按`excluded/complete`关闭并记录`no_semantic_content`，未改候选或新增提及、statement、关系。受控脚本`chp22_index_p445_marker_l226_227_exclusion.py`锁定来源/PDF/段哈希与表前态，dry-run/apply均核验页标和状态，写前保存coverage恢复副本。下一正文处理段是p.445索引内容`chp-22:22_CHP-22Index:l229-338`。
## 索引p.445两栏（S0 L229–338）

对照`CHP-22Index.pdf`物理页3：印本可见p.445，L229–338覆盖Bacon至Barelli的两栏索引。按页图校读而不改S0。L229的`3 20, 3 70`按印本读作320、370；L249 OCR `Bainboccianti`校为印本`Bamboccianti`；B.csv#18–19把`Niccolò`存成UTF-8字节误读后的`NiccolÃ²`，PDF与S1候选表均为`Niccolò`，原CSV保持不改。OCR中跨栏碎字、页码445及行尾杂符不视为索引内容。

对照B.csv#2–91标注89个开放候选：80 person、6 term、1 family、2 place。B.csv#20–25的Bamboccianti按艺术流派/群体索引主题归term；#45 Barberini family归family；#87–88 Barberini palace（含theatre子项）归place；其余已类型化主词头归person。Cardinal Antonio的brother与nephew分作两个索引主词头保留，不提前身份合并。作品、履历、关系和地点子项均为主词头下的索引导航，不作为本段独立事实或关系。

`cand-0159`（B.csv#6，Baglioni collection，索引定位Venice，214及260n）仍无`suggested_type`：现行taxonomy没有collection类型，本页又不足以证明它是组织、地点或家族；保留类型待决，不冒充institution或place。受控脚本`chp22_index_p445_l229_338_migration.py`锁定来源/PDF/B.csv/段哈希与表前态，默认dry-run并按主词头分组展示差异；写前备份候选表和coverage。未增加mentions、book-statements或relations。页段后覆盖为622 complete、85 queued、125 excluded；2,603个开放索引候选仍无类型，含该待决项。

## 索引p.446页标（S0 L340）

PDF物理页4显示印刷p.446。L340 `[Page 446]`是生成的来源页标，coverage记`excluded/complete`并说明`no_semantic_content`；未改候选或添加事实。受控脚本`chp22_index_p446_marker_l340_exclusion.py`校验页标、PDF与表前态，写前保存coverage恢复副本。当前下一内容段为`chp-22:22_CHP-22Index:l342-396`。

## 索引p.446左栏（S0 L342–396）

核对`CHP-22Index.pdf`物理页4（印刷p.446）左栏与规范索引段，按页图读校，不改写S0。对照B.csv#92–140，为49个开放候选标注类型：47 person、1 term、1 institution。`Barnabotti`按社会阶层词归term；`Benedictines`按宗教修会归institution；其余主词头为person。索引子项和页码是导航，不据此生成正文断言、提及或关系。

受控脚本`chp22_index_p446_l342_396_migration.py`锁定来源、PDF、索引CSV、段哈希及表前态，默认dry-run；先预览后应用，仅更新49个候选类型和本段coverage，写前保存候选表及coverage恢复副本。未新增mentions、book-statements或relations。处理后全表为11,436候选、26,829 mentions、12,102 statements；832段中623 complete、126有理由排除、83 queued、0 partial；开放未分类索引候选2,554。下一段为`chp-22:22_CHP-22Index:l398-452`。结构审计不替代全书S2语义交接审计。


## 索引p.446右栏（S0 L398–452）

核对`CHP-22Index.pdf`物理页4（印刷p.446）右栏与规范索引段。对照页图及B.csv#141–180，40个已有候选均为Bernini人物词头或其子项；39项新增`person`类型，cand-0319此前已有该类型。索引子项仍是导航，未增加mentions、book-statements或relations。

同时发现页图/S0中的主词头`Bentveugels`、`Bergamo`未出现在A.csv或B.csv主词头表，也无对应`index_entry_id`候选。正文中虽有相近对象候选，当前不据此推断同一性或补造索引映射；将该S1种子范围差异保留到全书S2交接审计前解决。受控脚本`chp22_index_p446_rcol_l398_452_migration.py`锁定来源/PDF/B.csv/段哈希及表前态，dry-run后应用，只更新40个候选类型和coverage；写前备份两张受影响表。

随后核对PDF物理页5（印刷p.447）：S0 L454 `[Page 447]`是生成页标，按`excluded/complete`关闭，无候选、mention或statement改动。脚本`chp22_index_p447_marker_l454_exclusion.py`锁定来源、PDF、段哈希和coverage前态，写前备份coverage。当前11,436候选、26,829 mentions、12,102 statements；832段中624 complete、127有理由排除、81 queued、0 partial；开放未分类索引候选2,515。下一段为`chp-22:22_CHP-22Index:l456-510`。

## 索引p.447左栏（S0 L456–510）

对照`CHP-22Index.pdf`物理页5（印刷p.447）及B.csv#181–227处理左栏。47个开放候选均为person；46项新增类型，cand-0379（Blunt）已有该类型。此S0范围包含少量右栏OCR碎片，后续L512–566另按整页右栏独立处理，避免跨栏错配。B.csv#214的`NiccolÃ²`为编码乱码；依页图校正候选使用`Niccolò`，未改写S1来源CSV。索引子项和页码仍是导航，不新增mentions、book-statements或relations。

受控脚本`chp22_index_p447_l456_510_migration.py`锁定来源、PDF、B.csv、段哈希和表前态，dry-run后应用；写前备份候选表与coverage。处理后11,436候选、26,829 mentions、12,102 statements；832段中625 complete、127有理由排除、80 queued、0 partial；开放未分类索引候选2,469。下一段为`chp-22:22_CHP-22Index:l512-566`。结构审计不替代全书S2语义交接审计。

## 索引p.447右栏（S0 L512–566）

对照同一页图及B.csv#228–274处理右栏47个开放候选：42 person、3 place（Bologna两项、Borghese Palace）、1 term（Book illustration）；cand-0387 Bonfiglioli collection因当前taxonomy没有collection类型且索引证据不足，保持type-pending。B.csv#262、#267–270的重音字符在CSV中乱码，按页图和候选名校读而不改写来源。L512的`X 447`是页眉/页码OCR碎片，不作为实体。索引子项及定位不是正文断言或关系；本段不新增mentions、book-statements或relations。

受控脚本`chp22_index_p447_rcol_l512_566_migration.py`锁定来源、PDF、B.csv、段哈希和表前态，dry-run后应用，写前备份受影响表。处理后11,436候选、26,829 mentions、12,102 statements；832段中626 complete、127有理由排除、79 queued、0 partial；开放未分类索引候选2,423。下一段为页标`chp-22:22_CHP-22Index:l568-568`。结构审计不替代全书S2语义交接审计。

## 索引p.448页标（S0 L568）

核对`CHP-22Index.pdf`物理页6，确认印刷p.448；S0 L568 `[Page 448]`为生成页标。按`excluded/complete`关闭并记录`no_semantic_content`，不改候选、mentions或statements。受控脚本`chp22_index_p448_marker_l568_exclusion.py`校验来源、页图与coverage前态，写前备份coverage。当前11,436候选、26,829 mentions、12,102 statements；832段中626 complete、128有理由排除、78 queued、0 partial；开放未分类索引候选2,423。下一段为`chp-22:22_CHP-22Index:l570-624`。机械闭合不代表S2语义交接完成。

## 索引p.448左栏（S0 L570–624）

核对`CHP-22Index.pdf`物理页6（印刷p.448）左栏，对照B.csv#275–323的49条候选行。46个未标类型的候选归person；cand-0434（B.csv#281）原为person，cand-0471（#319，Burlington的Chiswick宅邸）原为place，均保留；cand-2892（#311，Brydges, Grey的see-under交叉指引）维持excluded。页图校读Brienne、Brosses、Brühl及Brunelleschi等OCR疑点；未改S0/S1来源。子项和定位不作为新增断言、提及或关系。

受控脚本`chp22_index_p448_l570_624_migration.py`锁定来源/PDF/B.csv/段哈希和表前态，dry-run后应用并在写前备份候选表与coverage。处理后全表11,436候选、26,829 mentions、12,102 statements；832段中627 complete、128有理由排除、77 queued、0 partial；开放未分类索引候选2,377。下一段为`chp-22:22_CHP-22Index:l626-680`。结构审计不替代全书S2语义交接审计。

## 索引p.448右栏（S0 L626–680）

核对同页右栏及C.csv#0–43，共44条候选行；42个未标类型的主词头/子项对应人物，补标person。cand-0504和cand-0505此前已凭p.277注5证据标为work，本段保留其类型与证据说明。页图复核运行页眉/扫描碎片及Camassei、Canaletto项的OCR页码，来源文本与C.csv均未改写。索引子项和页码不作为新提及、断言或关系。

受控脚本`chp22_index_p448_rcol_l626_680_migration.py`锁定来源/PDF/C.csv/段哈希及表前态，dry-run后应用并为两表留恢复副本。处理后全表11,436候选、26,829 mentions、12,102 statements；832段中628 complete、128有理由排除、76 queued、0 partial；开放未分类索引候选2,335。下一queued段是页标`chp-22:22_CHP-22Index:l682-682`。结构审计不替代全书S2语义交接审计。

## 索引p.449页标（S0 L682）

核对`CHP-22Index.pdf`物理页7，确认印刷p.449；S0 L682 `[Page 449]`为生成页标。按`excluded/complete`关闭并记录`no_semantic_content`，不改候选、mentions或statements。受控脚本`chp22_index_p449_marker_l682_exclusion.py`锁定来源、页图和coverage前态，写前备份coverage。当前11,436候选、26,829 mentions、12,102 statements；832段中628 complete、129有理由排除、75 queued、0 partial；开放未分类索引候选2,335。下一段为`chp-22:22_CHP-22Index:l684-738`。机械闭合不代表S2语义交接完成。

## 索引p.449左栏（S0 L684–738）

核对`CHP-22Index.pdf`物理页7（印刷p.449）左栏，对照C.csv#44–91的48条候选行。为46个未标类型候选补标：44 person、2 institution（Capuchins、Carmelites）；cand-0531（C#55，Canons／Chandos宅邸）保留place，cand-0556（C#80，Entry of the Count of Colloredo）保留既有p.277注5证据支持的work。页图确认L684–738是左栏，OCR混入的右栏片段由L740–794单独处理；来源文本和C.csv均未改写。子项和定位不作为新增断言、提及或关系。

受控脚本`chp22_index_p449_l684_738_migration.py`锁定来源/PDF/C.csv/段哈希及表前态，dry-run后应用，并为候选表与coverage留恢复副本。处理后全表11,436候选、26,829 mentions、12,102 statements；832段中629 complete、129有理由排除、74 queued、0 partial；开放未分类索引候选2,289。下一段为`chp-22:22_CHP-22Index:l740-794`。结构审计不替代全书S2语义交接审计。

## 索引p.449右栏（S0 L740–794）

核对同页右栏及C.csv#92–139，共48条候选行；补标46 person、1 event（Castro战争）和1 institution（Cavalieri di Santo Stefano）。页图校读页眉、栏界与OCR截断；C.csv#117–124的Niccolò存在编码乱码，依印本保留候选中的正确拼写，不改S0或C.csv。主词头之外的索引子项和定位不作为新增断言、提及或关系。

受控脚本`chp22_index_p449_r740_794_migration.py`锁定来源/PDF/C.csv/段哈希及表前态，显式校验Niccolò的S1乱码映射；dry-run后应用并为候选表与coverage留恢复副本。处理后全表11,436候选、26,829 mentions、12,102 statements；832段中630 complete、129有理由排除、73 queued、0 partial；开放未分类索引候选2,241。下一段为p.450页标`chp-22:22_CHP-22Index:l796-796`。结构审计不替代全书S2语义交接审计。

## 索引p.450页标（S0 L796）

核对`CHP-22Index.pdf`物理页8，确认印刷p.450；S0 L796 `[Page 450]`为生成页标。按`excluded/complete`关闭并记录`no_semantic_content`，不改候选、mentions或statements。受控脚本`chp22_index_p450_marker_l796_exclusion.py`锁定来源、页图和coverage前态，写前备份coverage。当前11,436候选、26,829 mentions、12,102 statements；832段中630 complete、130有理由排除、72 queued、0 partial；开放未分类索引候选2,241。下一段为`chp-22:22_CHP-22Index:l798-852`。机械闭合不代表S2语义交接完成。

## 索引p.450左栏（S0 L798–852）

核对`CHP-22Index.pdf`物理页8左栏，对照C.csv#140–190的51条候选行；50个主词头/子项候选归person，cand-0660 `Chi soffre, speri`归work。第2章`02_CHP-2_sec_iv.md` L183–184（印刷p.58）称其为Rospigliosi创作的verse drama，作为类型判断依据。C.csv#172–173的Chantelou、Chardin重音乱码由页图校读，候选沿用印本拼写而不改S0/S1来源。索引子项和定位不作为新增断言、提及或关系。

受控脚本`chp22_index_p450_l798_852_migration.py`锁定来源/PDF/C.csv/段哈希与表前态，并核验两处乱码映射；dry-run后应用，候选表与coverage均留恢复副本。处理后全表11,436候选、26,829 mentions、12,102 statements；832段中631 complete、130有理由排除、71 queued、0 partial；开放未分类索引候选2,190。下一段为`chp-22:22_CHP-22Index:l854-908`。结构审计不替代全书S2语义交接审计。

## 索引p.450右栏（S0 L854–908）

核对同页右栏及C.csv#191–226，共36条候选行：13 person、1 term、22 place。C#204“Churches of religious orders”是教堂集合的主题词；C#205–226的Location与Sub-entry列列明具体教堂或建筑性小空间，依taxonomy归place。页图校读Chigi续项与Churches栏间的OCR碎片；不把索引定位转成正文断言、提及或关系。

受控脚本`chp22_index_p450_r854_908_migration.py`锁定来源/PDF/C.csv/段哈希及表前态，dry-run后应用并为候选表与coverage留恢复副本。处理后全表11,436候选、26,829 mentions、12,102 statements；832段中632 complete、130有理由排除、70 queued、0 partial；开放未分类索引候选2,154。下一段为p.451页标`chp-22:22_CHP-22Index:l910-911`。结构审计不替代全书S2语义交接审计。

## 索引p.451页标与页眉（S0 L910–911）

核对`CHP-22Index.pdf`物理页9，确认印刷p.451；S0 L910 `[Page 451]`为生成页标，L911 `INDEX`为运行页眉。按`excluded/complete`关闭并记`no_semantic_content`，不改候选、mentions或statements。受控脚本`chp22_index_p451_marker_l910_911_exclusion.py`校验来源、页图和coverage前态，写前备份coverage。当前11,436候选、26,829 mentions、12,102 statements；832段中632 complete、131有理由排除、69 queued、0 partial；开放未分类索引候选2,154。下一段为`chp-22:22_CHP-22Index:l913-1022`。机械闭合不代表S2语义交接完成。

## 索引p.451两栏（S0 L913–1022）

核对`CHP-22Index.pdf`物理页9（印刷p.451）及C.csv#227–321，共95条索引行。L913–1022覆盖两栏；对照页图校正页码和栏界，来源Markdown、PDF与C.csv保持不变。六条既有see-under交叉指引C#314–319继续excluded；其余89个开放候选标注25 person、42 place、22 work。教堂/建筑性空间归place，St Peter's内部对象C#238–241保留为work。Cignani的Bacchanal、Forli Cathedral穹顶绘画、Jupiter giving Suck、St John the Baptist以及Cigoli的Deposition按具体作品处理，依据第8章p.220及p.231、第10章导言p.282n和既有作品映射。`Clément, Abbé`按印本重音校正候选拼写；Città di Castello也经页图核对。页码均为索引导航，不据此新增mentions、book statements或relations。

受控脚本`chp22_index_p451_l913_1022_migration.py`锁定来源、PDF、C.csv、段哈希及表前态，dry-run后应用；写前备份候选表和coverage。处理后11,436候选、26,829 mentions、12,102 statements；832段中633 complete、131有理由排除、68 queued、0 partial；开放未分类索引候选2,065。下一段为p.452页标`chp-22:22_CHP-22Index:l1024-1024`。机械审计不替代全书S2语义交接审计。

## 索引p.452页标（S0 L1024）

核对`CHP-22Index.pdf`物理页10，确认印刷p.452；L1024 `[Page 452]`是生成页标。按`excluded/complete`关闭并记录`no_semantic_content`，不改候选、mentions或statements。受控脚本`chp22_index_p452_marker_l1024_exclusion.py`校验来源、PDF、段哈希和coverage前态，写前备份coverage。当前11,436候选、26,829 mentions、12,102 statements；832段中633 complete、132有理由排除、67 queued、0 partial；开放未分类索引候选2,065。下一段为`chp-22:22_CHP-22Index:l1026-1080`。

## 索引p.452左栏（S0 L1026–1080）

核对同一PDF物理页10的左栏；L1026是页眉/页码行，C.csv#322–371共50行对应L1027–1080。为49个开放候选补标32 person、4 place、5 work、6 term、1 family、1 institution；既有cand-0834（C#364，Stefano Conti）保留person。Codazzi四幅有题名绘画及Coli的Lepanto壁画组归work；Contarini family与villa分作family和place；Congregazione dei Virtuosi归institution。`Competitions`和Contracts通用栏目及子项按term处理，未据索引标题臆造具体比赛或存世合同。C#361仍为Antonio Conti人物词头，失传论画文书另由archive候选cand-9728表示；C#364附录文件子项不改变其人物身份。来源Markdown、PDF、C.csv均未改写，索引导航不增加mentions、book statements或relations。

受控脚本`chp22_index_p452_l1026_1080_migration.py`锁定来源/PDF/C.csv/段哈希及表前态，dry-run后应用并写前备份候选表与coverage。处理后11,436候选、26,829 mentions、12,102 statements；832段中634 complete、132有理由排除、66 queued、0 partial；开放未分类索引候选2,016。下一段为右栏`chp-22:22_CHP-22Index:l1082-1136`。本次coverage审计曾发现空reviewed段缺`no_semantic_content`前缀，已补正两段说明；修正后重新审计。

## 索引p.452右栏（S0 L1082–1136）

核对`CHP-22Index.pdf`物理页10（印刷p.452）右栏及C.csv#372–420。L1082是运行页眉，49条索引候选行位于L1083–1136。按页图读取栏界和条目；四个see-under别名C#394、C#397、C#398、C#401维持excluded；既有C#407 cand-0873（Crespi与Grand Prince Ferdinand）保留person；另有43个开放候选补标21 person、19 work、3 family。人物行：C#372–376、379、382、386–387、389、391–392、395–396、399–400、402–406；家族行C#377–378、393；作品行C#380–381、383–385、390、408–420。Corradini的Schulenburg雕像与《Virginity》、Correggio三幅题名绘画，以及Crespi C#408–420的十三条绘画/图像对象归work。C#390“paintings and drawings by P. Longhi”按work处理，因为p.382正文已分别登记约二十幅Longhi绘画组cand-10712和未辨素描组cand-10714。C#388 cand-0858“collections”仍类型待决：p.382及p.383正文已将Correr的异质收藏作为独立对象使用，但现行taxonomy没有collection类型；不把包括书籍、手稿、版画、钱币、青铜器及绘画的整体冒充person、place、institution或term。C#389的“interest in history of Venice”仍随Correr人物词头。页图印作`Créqui, Duc de`，将C#402候选由S1拼写`Crequi, Duc de`校为印本拼写；S0 Markdown、PDF和C.csv均未改。索引子项与页码只是导航，本段不增加mentions、book statements或relations。

受控脚本`chp22_index_p452_rcol_l1082_1136_migration.py`锁定S0段及来源/PDF/C.csv/表前态，dry-run通过后应用，写前备份候选表和coverage。处理后11,436候选、26,829 mentions、12,102 statements；832段中635 complete、132有理由排除、65 queued、0 partial；开放未分类索引候选1,973（含cand-0858类型待决）。下一段为`chp-22:22_CHP-22Index:l1140-1194`。结构审计不替代全书S2语义交接审计。

## 索引p.453页标（S0 L1138）

对照`CHP-22Index.pdf`物理页11，印刷页码为p.453。L1138 `[Page 453]`是生成页标而非索引词条；coverage记为excluded/complete，理由以前缀`no_semantic_content:`记录。不新增候选分类、mentions、book statements或relations。下一段为`chp-22:22_CHP-22Index:l1140-1194`。

受控脚本`chp22_index_p453_marker_l1138_exclusion.py`锁定来源、PDF、段哈希及表前态，dry-run通过后应用并保留恢复副本。全表结构审计为`s2_missing=[]`、`errors=[]`；当前832段中635 complete、133有理由排除、64 queued、0 partial。结构审计不替代全书S2语义交接审计。

## 索引p.453左栏（S0 L1140–1194）

对照`CHP-22Index.pdf`物理页11（印刷p.453）逐项读取左栏，并核对C.csv#421–431、D.csv#0–36，共48个索引候选。S0 L1140–1194的逐行OCR混入右栏截断片段；右栏完整转录单列于L1196–1249，本段不重复分类右栏碎片。候选类型为34 person、7 work、1 term、1 procedure、1 archive、2 place、2 family。C#421“Women washing their Laundry at a Fountain”和C#424“Dance of Nymphs”归work；C#422、C#425的“work for …”是Crespi/Creti人物词头下的描述性子项，不是可独立命名的作品。C#426“Critics, Roman”是通称term；C#431“Customs duty on pictures”是财政机制procedure。D#3《Daphnis and Chloe》按文献/文学文本归archive，与图像作品区分；D#5“Apotheosis of Aeneas”归work。D#9的“introduction of Neapolitan painting into Central Europe”仍属Daun人物子项，未另造事件；D#10维也纳宫殿、D#13 Bergamo的S. Maria Maggiore分别归place；D#32–33 Dolfin family及家族赞助归family。其余人物词头和具名作品依索引页图及类型边界逐项标注。索引页码仅为导航，不新增mentions、book statements或relations。

受控脚本`chp22_index_p453_l1140_1194_migration.py`锁定S0段、来源/PDF、C/D索引表及表前哈希；逐项校验48个候选ID、主词头/子项与开放未分类前态，dry-run通过后应用并为候选表、coverage留恢复副本。迁移后候选11,436、mentions 26,829、statements 12,102；832段中636 complete、133有理由排除、63 queued、0 partial；开放未分类索引候选1,925。下一段为右栏`chp-22:22_CHP-22Index:l1196-1249`。结构审计不替代全书S2语义交接审计。

## 索引p.453右栏（S0 L1196–1249）

对照`CHP-22Index.pdf`物理页11（印刷p.453）读取右栏；L1196为页码行，D.csv#37–66及E.csv#0–15共46个词条从L1197起。上段S0 L1140–1194包含这些词条的OCR残片，本段以页图和右栏完整转录为准，不重复分类。45个开放候选标注24 person、9 work、2 place、1 institution、9 term；D#57 cand-0955既有place分类保留。D#37的Count of Monterey为人物；D#38、D#39和D#42为作品，其中p.76注释具体识别S. Carlo ai Catinari的穹顶 pendentives 上的Cardinal Virtues寓意壁画；D#40“payments”仍为Domenichino人物语境，不另造支付事件；D#41的tribune是S. Andrea della Valle内部建筑空间，归place。D#43是威尼斯的Dominican宗教修会，归institution；D#58“Dutch artists in Rome”作为无独立组织身份的泛称归term。E#4–11的English patronage、游客与启蒙运动索引词头/子项均是一般主题term。页图印作`Düsseldorf`，据此将既有cand-0955由`Dusseldorf`校为`Düsseldorf`；S0、PDF及D.csv未改。其余人物、作品和地点依词头及子项逐项分类。索引页码不形成原书断言，本段不新增mentions、book statements或relations。

受控脚本`chp22_index_p453_rcol_l1196_1249_migration.py`锁定S0段、来源/PDF、D/E索引表及表前哈希；逐项校验46个索引映射，其中45个开放未分类，另保留D#57既有place，dry-run通过后应用并留候选表与coverage恢复副本。迁移后候选11,436、mentions 26,829、statements 12,102；832段中637 complete、133有理由排除、62 queued、0 partial；开放未分类索引候选1,880。下一段为p.454页标`chp-22:22_CHP-22Index:l1251-1251`。结构审计不替代全书S2语义交接审计。

## 索引p.454页标（S0 L1251）

核对`CHP-22Index.pdf`物理页12，印刷页码为p.454。L1251 `[Page 454]`是生成页标而非索引词条；coverage记为excluded/complete并以前缀`no_semantic_content:`说明。不改候选、mentions、book statements或relations。受控脚本`chp22_index_p454_marker_l1251_exclusion.py`锁定来源/PDF/段哈希及coverage前态，dry-run通过后应用并留恢复副本。当前832段中637 complete、134有理由排除、61 queued、0 partial。下一段为左栏`chp-22:22_CHP-22Index:l1253-1307`。

## 索引p.454左栏（S0 L1253–1307）

对照`CHP-22Index.pdf`物理页12（印刷p.454）核读左栏，E.csv#16–20及F.csv#0–44共50行；E#19是see-under别名，保留excluded；F#29 cand-1014既有person分类保留。其余48个开放候选中46个补标31 person、5 work、7 place、1 term、1 family、1 event；Farsetti的cast collection与painting collection（F#20–21）因taxonomy没有collection类型而保留未分类，不强行归入其他类型。

类型判断结合全书正文：F#13所指Gesù是修会教堂建筑，归place；F#27“sale of collections”按第十五章p.364明确叙述的十九世纪初财产拆分与收藏出售归event；Bentivoglio由第二章p.48明确称为家族，归family；Ferrerio的Vigilance雕像及其为Ferrara Archbishop’s Palace楼梯墙设计的灰泥装饰分别归work。其余人物、地点、作品和通称依页图、索引CSV与已有正文语境逐项分类。索引页码只作导航，不新增mentions、book statements或relations。

受控脚本`chp22_index_p454_l1253_1307_migration.py`锁定S0段、来源/PDF、E/F索引表及表前哈希，校验全部50行候选映射与各状态；dry-run通过后应用，为候选表和coverage留恢复副本。处理后11,436候选、26,829 mentions、12,102 statements；832段中638 complete、134有理由排除、60 queued、0 partial；开放未分类索引候选1,834（含本段两项collection类型待决及先前待决项）。下一段为右栏`chp-22:22_CHP-22Index:l1309-1363`。结构审计不替代全书S2语义交接审计。

## 索引p.454右栏（S0 L1309–1363）

对照`CHP-22Index.pdf`物理页12（印刷p.454）核读右栏F.csv#45–92共48行；其中43个开放候选标注29 person、8 work、3 place、1 term、1 archive、1 family，另保留F#68 cand-1053 person、F#72 cand-1057 family、F#74 cand-1059 place、F#85 cand-1070 person。左栏L1253–1307混有F#45–46的OCR残片，本段按右栏完整转录核对，不重复计算。

F#45–46“work for Louis XIV”与“work in S. Maria Maggiore, Bergamo”是Ferri人物词头下的活动/地点语境；书中分别讨论其为法国国王工作及在Bergamo创作多幅绘画，但索引子项未指向单件可辨作品，因此保留person。F#69 Foscarini的私人图书馆确为书籍与手稿收藏，但现行taxonomy缺少collection类型，保留待决；F#55 Flemish artists in Rome是泛称term；F#57仍指Florence这一地点，其艺术中心角色作为子项限定。Fontenelle的《Eloge in Tombeaux des Princes》归archive；页图中可辨认的画作、雕塑/喷泉作品和建筑空间分别归work或place。索引页码不新增mentions、book statements或relations。

受控脚本`chp22_index_p454_rcol_l1309_1363_migration.py`锁定S0段、来源/PDF、F.csv及表前哈希，校验48行候选映射和四个既有类型；dry-run通过后应用，并为候选表及coverage留恢复副本。处理后11,436候选、26,829 mentions、12,102 statements；832段中639 complete、134有理由排除、59 queued、0 partial；开放未分类索引候选1,791（含本段私人图书馆及其他类型待决项）。下一段为p.455页标`chp-22:22_CHP-22Index:l1365-1366`。结构审计不替代全书S2语义交接审计。

## 索引p.455页标（S0 L1365–1366）

核对`CHP-22Index.pdf`物理页13，页图显示印刷p.455与运行页眉`INDEX`。S0 L1365 `[Page 455]`是生成页标，L1366为运行页眉；均不是索引词条，coverage记为excluded/complete并以`no_semantic_content:`说明。不改候选、mentions、book statements或relations。受控脚本`chp22_index_p455_marker_l1365_exclusion.py`锁定来源/PDF/段哈希及coverage前态，dry-run通过后应用并留恢复副本。

## 索引p.455左栏（S0 L1368–1422）

对照印刷p.455页图及F.csv#93–109、G.csv#0–29核读左栏。候选主词头和子项对应45个开放候选，标注30 person、7 work、4 term、3 archive、1 institution；F#94–95的see-under别名保持excluded，既有类型和ID不变。F#108依页图及CSV校读为`Furlani, Ventura`；S0该行末混入的右栏首词碎片不纳入左栏，右栏完整范围由L1424–1477单独处理。Fumiani、Gabbiani和Gaulli下的可辨作品归work；法兰西赞助/艺术倾向归term；Galiani、Galilei、Gallacini下的具名文献归archive。人物子项“and…”, “views on painting”及“payment”保留在索引人物语境，不据此新建关系、主题或事件。索引定位页码仅作导航，本段不新增mentions、book statements或relations。

受控脚本`chp22_index_p455_l1368_1422_migration.py`锁定S0段、来源/PDF、F/G索引表和四表前哈希，逐项校验候选ID、词头、子项及既有排除状态；dry-run通过后应用，为候选表和coverage留恢复副本。处理后候选11,436、mentions 26,829、statements 12,102；832段中640 complete、135有理由排除、57 queued、0 partial；开放未分类索引候选1,746。结构审计通过不等于全书S2语义交接完成。下一段为p.455右栏`chp-22:22_CHP-22Index:l1424-1477`。

## 索引p.455右栏（S0 L1424–1477）

对照`CHP-22Index.pdf`物理页13印刷p.455右栏，逐项核读G.csv#30–79共50个候选。49条新补类型，G#48 cand-1141既有person分类保留；总计34 person、6 work、7 term、1 archive、1 institution、1 place。G#30“work in Gesù”及G#44–45“work for Charles I/Marie de Medici”只说明艺术家工作/委托范围，未识别独立题名，依人物语境保留为person；G#25–28已有Gaulli具名作品词条，不重复造一个Gesù装饰总作品。Orazio的《Public Felicity triumphant over Dangers》已有Plate 25题名与正文说明，归work；Gennari的Danaë及Elizabeth Felton as Cleopatra、Gherardi的Lepanto壁画组、Giambologna的Henri IV骑马像与《Mercury》均为可辨作品，归work。

G#33 `Gazzeta Veneta`是期刊文献，归archive；正文同一刊名在p.323所引期号处写作`Gazzetta Veneta`，候选保留索引拼写，名称规范化留待S3。G#38 Genoa归place；G#39 Genoa aristocracy及德国赞助、德国诸侯艺术趣味/情色关注、Gesuati对Jesuits的敌意等概念性子项归term。G#57 Gesuati指正文中具有组织身份、委托建堂并参与教派论争的修会团体，归institution；p.270新教堂及相邻修院是独立place候选，不与该组织合并，Gesuati与教堂候选的身份对应保留S3裁决。G#62页图可读为Gherardi, Abate Pietro Ercole；G#73页图与G.csv均为Gibbon, Edward，S0的`Gibhon`是OCR误字，未改写S0或候选名。索引页码不新增mentions、book statements或relations。

受控脚本`chp22_index_p455_l1424_1477_migration.py`锁定S0段/来源/PDF、段清单、G.csv及四表前态，核验G.csv#30–79的候选映射与既有类型；dry-run发现并保留cand-1141既有person分类后通过，再应用49条类型更新并为候选表和coverage留恢复副本。处理后候选11,436、mentions 26,829、statements 12,102；832段中641 complete、135有理由排除、56 queued、0 partial；开放未分类索引候选1,697。结构审计通过不等于全书S2语义交接完成。下一queued段为`chp-22:22_CHP-22Index:l1479-1479`（S0页标行）。

## 索引p.456页标（S0 L1479）

核对`CHP-22Index.pdf`物理页14，页图显示印刷p.456。S0 L1479 `[Page 456]`是生成页标，排除并标记complete；L1481运行页眉随下一左栏段处理。不改候选、mentions、book statements或relations。受控脚本`chp22_index_p456_marker_l1479_exclusion.py`锁定来源/PDF/段哈希及coverage前态，dry-run通过后应用并留恢复副本。当前832段中641 complete、136有理由排除、55 queued、0 partial；开放未分类索引候选1,697。下一queued段为p.456左栏`chp-22:22_CHP-22Index:l1481-1535`。

## 索引p.456左栏（S0 L1481–1535）

对照`CHP-22Index.pdf`物理页14印刷p.456左栏、S0分段清单及G.csv#80–126。L1481为运行页眉，左栏完整收至Gozzadini；右栏从L1537开始，避免串栏。47个索引行中46个是开放候选：45个新标23 person、10 work、7 archive、2 family、2 term、1 place；G#99 Giovanelli collection保留类型待决（taxonomy无collection类），G#120 Gonzaga see-under继续排除。Giordano的具体题名/画作组归work，但“work in Spain”“work in S. Maria Maggiore, Bergamo”和payment仍是人物语境；p.219明确的《Crossing of the Red Sea》另作work。G#80“admirers in Venice”是泛称群体term；del Rosso为family。Goldoni的剧作、回忆录与不同版本、Giustiniani雕塑图册出版物及Gori《Museum Etruscum》归archive；“views on art”归term。页图显示G#97为Giori（不改S0 OCR `Gioii`）；G#125页图为Gozadini, Bonifazio，G.csv转录`Bonisezio`，仅把候选名修正为印刷拼写，保留S0和G.csv。索引导航不新增mentions、book statements或relations。

受控脚本`chp22_index_p456_l1481_1535_migration.py`锁定段、来源/PDF、G.csv、manifest及四表前态；dry-run核对47条候选映射、保留G#99待决与G#120排除后通过，应用45条类型并校正cand-1217名称，为候选表和coverage留恢复副本。当前候选11,436、mentions 26,829、statements 12,102；832段中642 complete、136有理由排除、54 queued、0 partial；开放未分类索引候选1,652。下一段为p.456右栏`chp-22:22_CHP-22Index:l1537-1591`。


## 索引p.456右栏（S0 L1537–1591）

对照`CHP-22Index.pdf`物理页14印刷p.456右栏、S0分段及G.csv#127–176；L1537为运行页眉，页面图划清左右栏，S0在L1544–1557和L1569–1574夹入的左栏OCR碎片不在本段重复分类。50条索引行含48个开放候选，47个新增类型为22 person、19 work、2 archive、3 term、1 family；G#135 Grassi collection因taxonomy无collection类保留待决，G#138–139 Gregory see-under继续排除。G#129 Gasparo Gozzi关于Pietro Longhi的文章为archive；绘画社会价值与艺术观点为term，支持Pisani仍为人物语境。G#151和G#159均指向归于两位Guardi的`Sala del Maggior Consiglio`（书p.316），保留独立候选供S3身份对齐；G#152/#160的`Gerusalemme Liberata`场景组据p.336为Guardis画作，G#156 `Parlatorio`及G#158 `Ridotto`据p.383为作品而非地点。G#162的copyist为人物活动语境，G#163–167各为所复制的Tintoretto、Veronese、Bassano绘画；G#171合同归archive，具名Guercino画作归work，付款保留人物语境、收费标准为term。页图将G#141印名读作Griè, Angelica，候选层从`Grill`校正为`Griè`，保留S0与G.csv原转录。索引导航不新增mentions、book statements或relations。

受控脚本`chp22_index_p456_l1537_1591_migration.py`锁定来源段、原书页、G.csv、manifest及四表前态；dry-run核对50条候选映射、47条分类、一个待决集合和两个排除别名后通过，再应用并为候选表、coverage生成恢复副本。当前候选11,436、mentions 26,829、statements 12,102；832段中643 complete、136有理由排除、53 queued、0 partial；开放未分类索引候选1,605。下一段为p.457页标`chp-22:22_CHP-22Index:l1593-1593`。


## 索引p.457页标（S0 L1593）

对照`CHP-22Index.pdf`物理页15，页图显示印刷p.457。S0 L1593 `[Page 457]`为生成页标，排除并标记complete；L1595运行页眉随p.457左栏段处理。不改候选、mentions、book statements或relations。受控脚本`chp22_index_p457_marker_l1593_exclusion.py`锁定页标段、来源/PDF/manifest及表前态；dry-run通过后应用，并为coverage留恢复副本。当前832段中643 reviewed/complete、137有理由排除、52 queued、0 partial；下一queued段为p.457左栏`chp-22:22_CHP-22Index:l1595-1649`。


## 索引p.457左栏（S0 L1595–1649）

对照`CHP-22Index.pdf`物理页15印刷p.457左栏及S0分段；本段含G.csv#177–195、H.csv#0–24和I.csv#0–4共49条，页图划定左栏边界，S0并列的右栏OCR片段留给`l1651-1703`，不重复分类。47个开放候选中46个标注29 person、11 work、2 archive、3 term、1 event；H#4 Hapsburg collections from Prague因taxonomy无collection类型待决，G#195 Guzman与H#6 Harley see-under维持排除。G#177拒绝查理一世邀请为p.178明确叙述的单次行为，标event；G#184为Guercino“work for Don Antonio Ruffo”而无独立作品题名，保留person语境。G#178–183为具名绘画；S0 OCR将Cato题名识为“Lise os”，CSV与页图为“Life of Cato”，只在此记校读，不改来源转录。G#186 `Histories`及I#2 `Imago primi saeculi`为文献（archive）；Guidi的图稿/雕塑组及Houdon胸像、Huber版画为work；H#5 Hapsburg patronage、I#1 Illustrated books类别与I#4 Indecency and the erotic为term。索引导航未新增mentions、book statements或relations。

受控脚本`chp22_index_p457_l1595_1649_migration.py`锁定段、原书、G/H/I.csv、manifest及四表前态，dry-run核对49条候选、46个类型、一个待决收藏和两条排除后通过并应用；随后据p.178原文和taxonomy事件定义，通过`chp22_index_p457_l1595_1649_correct_event_classification.py`将cand-1267从person更正为event，并同步coverage说明。提交前计数一致性复核发现该说明仍将事件计入person，已将分类统计改为29 person、11 work、2 archive、3 term、1 event；候选数据未再变动。两次应用均保留候选/coverage恢复副本。最终候选11,436、mentions 26,829、statements 12,102；832段中644 complete、137有理由排除、51 queued、0 partial；开放未分类索引候选1,559。下一段为p.457右栏`chp-22:22_CHP-22Index:l1651-1703`。


## 索引p.457右栏（S0 L1651–1703）

对照`CHP-22Index.pdf`物理页15印刷p.457右栏、S0分段及I.csv#5–10、J，K.csv#0–26、L.csv#0–8；页面图划清左右栏，避免将左栏混入S0的OCR碎片重复分类。42条索引行中38个开放候选有36个新标23 person、3 institution、7 term、1 work、1 archive、1 family；J，K#15 Van Dyck与Rubens paintings in Johann Wilhelm’s collection及L#5 Labia collection因taxonomy无collection/group类型保留待决，I#6–9 Innocent see-under别名维持排除。Jesuits按语境分别标机构或关于艺术特征/与Gesuati敌意的term，不据索引导航生成关系；Johann Wilhelm条目中的赞助、趣味和未具名单件的收藏内容保留为人物语境/term，不虚构具体作品；Juvarra的马德里宫殿装饰方案为work，La Harpe的`Il Filosofo dell’Alpi`为archive。索引导航不新增mentions、book statements或relations。

受控脚本`chp22_index_p457_l1651_1703_migration.py`锁定段、原书、I/J，K/L.csv、manifest及四表前态；dry-run核对42条候选映射、36条分类、两个待决集合和四条排除别名后通过并应用，为候选表和coverage留恢复副本。当前候选11,436、mentions 26,829、statements 12,102；832段中645 complete、137有理由排除、50 queued、0 partial；开放未分类索引候选1,523。下一段为p.458页标`chp-22:22_CHP-22Index:l1705-1705`。


## 索引p.458页标（S0 L1705）

对照`CHP-22Index.pdf`物理页16，页图显示印刷p.458。S0 L1705 `[Page 458]`为生成页标，排除并标记complete；L1707运行页眉由p.458左栏段覆盖。不改候选、mentions、book statements或relations。受控脚本`chp22_index_p458_marker_l1705_exclusion.py`锁定页标段、来源/PDF/manifest及表前态，dry-run通过后应用并为coverage保留恢复副本。当前832段中645 reviewed/complete、138有理由排除、49 queued、0 partial；下一段为p.458左栏`chp-22:22_CHP-22Index:l1707-1761`。


## 索引p.458左栏（S0 L1707–1761）

对照`CHP-22Index.pdf`物理页16印刷p.458左栏、S0分段及L.csv#9–56，共48条索引候选，均为open；右栏从L.csv#57（Letterini）开始，不重复分类。按原文指称标注31 person、14 work、2 archive、1 term：Van Laer与Legros的具名画作、Lanfranco的S. Andrea della Valle穹顶构件、Lazzarini的具名画作及被原文明确称为其绘制的Triumphal Arch、Leonardo的绘画和Leoni的蚀刻版画归work；L'Hoggidi（第一章p.3注所述1627年出版物）与Leonardo的`Trattato della pittura`（手稿/论著）归archive。`Landscapes, varying reactions to in Rome and Venice`为term。Van Laer的prices、Lanfranco的payments与无具体题名的Monterey委托、Lazzarini为S. Paolo d'Argan所作的未具名作品，以及Giacomo della Lena“on F. Guardi”等均留在人物语境；p.221注只说S. Paolo d'Argan聘用了包括Lazzarini在内的多位画家，不据此造一件作品或关系。

页图逐行核对后，候选定位有四处S1 CSV转录误差：L#13由`311`校为`3n`，L#15末项由`378`校为`328`，L#34 Le Nain由`122`校为`133`，L#41 Lely由`122n`校为`135n`。只订正`entity-candidates.csv`定位字段，S0 OCR与`L.csv`原转录均保留。页图亦确认S0 L1751 Leonardo词头前的杂字符为OCR噪声、L1754印字为`pittura`（S0 OCR作`pistura`）；不改写来源。受控脚本`chp22_index_p458_l1707_1761_migration.py`锁定段、印本页图、L.csv、taxonomy、相关正文证据与四表前态；dry-run核对48条候选及四个定位修订后通过并应用，为候选表与coverage保留恢复副本。索引导航未新增mentions、book statements或relations。最终候选11,436、mentions 26,829、statements 12,102；832段中646 complete、138有理由排除、48 queued、0 partial；开放未分类索引候选1,475。下一段为p.458右栏`chp-22:22_CHP-22Index:l1763-1817`。


## 索引p.458右栏（S0 L1763–1817）

对照`CHP-22Index.pdf`物理页16印刷p.458右栏及S0分段、L.csv#57–105，共49条索引记录：48个开放候选中47个新标29 person、7 work、3 archive、4 term、2 place、1 family、1 institution；cand-1445（L#103 Lot and his Daughters）沿用此前已有的work分类，L#98 Claude Lorrain see-under维持排除。L#59 Flood、L#61合同、L#63 Liechtenstein family、L#64维也纳城堡、L#76学校以及L#70–71两部文献等，按原文所指分别处理；“paintings in collection of Teodoro Correr”不指明单件作品，保留为Pietro Longhi的人物语境。“and”子项及索引所见交往不据此转成正式关系。

正文核对：p.217称The Flood为Liberi送达的画布，并记其S. Maria Maggiore委托合同及后续取消，故具名画作归work、合同文献归archive；“indecency of paintings”归term。p.265直接称Longhi的Fall of the Giants为壁画，归work。p.320说明Lodoli于威尼斯开办、招收学生并持续运营的私立学校，按组织化教学机构归institution；其教育思想和建筑／绘画观点归term。p.322将Nazari与Alessandro Longhi各自绘制的Lodoli肖像列为作品；该复数肖像子项与L#82的Longhi肖像可能重叠，当前只作S2类型判断，留给S3身份对齐处理。p.367确认`Apologhi`及`Elementi dell’architettura lodoliana`为出版文献（archive）。p.393的“两幅谈话场景、Murray先生及其家人”来自1776年拍卖目录，原书明确说目录与归属不足以作定论；保留work候选并保留归属不确定性。

页图逐行核对后，仅修正候选层：L#59子项`Rood, The`校为`Flood, The`；L#62页码`234n`校为`341n`；L#68的`381`校为`384`；L#105的`195`校为`196`。不改S0 OCR或原始L.csv。受控脚本`chp22_index_p458_l1763_1817_migration.py`锁定原书、页图对应PDF、索引CSV、taxonomy、相关正文来源、manifest及表前态；dry-run通过后应用，并为候选表与coverage保留恢复副本。索引导航未新增mentions、book statements或relations。当前候选11,436、mentions 26,829、statements 12,102；832段中647 complete、138有理由排除、47 queued、0 partial；开放未分类索引候选1,428。下一段为p.459页标`chp-22:22_CHP-22Index:l1819-1820`。


## 索引p.459页标（S0 L1819–1820）

对照`CHP-22Index.pdf`物理页17确认印刷p.459。S0 L1819 `[Page 459]`为生成页标，L1820 `INDEX`为运行页眉，均属导航性内容；排除并标记complete，不改候选、mentions、book statements或relations。受控脚本`chp22_index_p459_marker_l1819_1820_exclusion.py`锁定S0、PDF、manifest和表前态，dry-run通过后应用并为coverage留恢复副本。当前832段中647 reviewed/complete、139有理由排除、46 queued、0 partial；开放未分类索引候选1,428。下一段为p.459左栏`chp-22:22_CHP-22Index:l1822-1876`。


## 索引p.459左栏（S0 L1822–1876）

对照`CHP-22Index.pdf`物理页17印刷p.459、S0分段及L.csv#106–120、M.csv#0–32，共48个开放候选，分类为24 person、13 place、6 work、5 archive。类型依据索引所指及正文语境：城市、宫殿、教堂为place；St Peter's façade、Bernini的Louvre方案、Maderno的Barberini palace方案、McSwiny的英国名人纪念画系列、Van Dyck肖像蚀刻提案及Maggiotto的`Good Inclinations leading a Youth to Knowledge`归work；`Il Gran Teatro delle Pitture e Prospettive di Venezia`、Machiavelli的`Prince`、`To the Ladies and Gentlemen of Taste`、`Tombeaux des Princes`及`Considerazioni elettriche`归archive。p.287称McSwiny的Van Dyck蚀刻计划未能实现；仍以可识别的艺术设计提案归work，与正文候选cand-9006一致，但不声称蚀刻或出版已经完成。p.289称纪念画系列到1722年已有15幅开工，p.290–291叙述已完成作品的购藏及1741年画册出版。L#117“patronage of Domenichino”、McSwiny的“and”及“artists employed/Venetian artists”等子项保持相应人物候选语境，不据索引新增关系。S0 L1876残片`X 459`与页图不符，不是索引条目，未建候选。

页图逐项核对后，仅订正候选层L#118（cand-1460）页码`231`为印本`23n`；S0 OCR和原始L.csv均保留。受控脚本`chp22_index_p459_l1822_1876_migration.py`锁定索引段、印本PDF、L/M索引CSV、taxonomy、相关正文来源、manifest与候选/coverage表前态；dry-run通过后应用并保留恢复副本。索引导航未新增mentions、book statements或relations。当前候选11,436、mentions 26,829、statements 12,102；832段中648 complete、139有理由排除、45 queued、0 partial；开放未分类索引候选1,380。下一段为p.459右栏`chp-22:22_CHP-22Index:l1878-1931`。


## 索引p.459右栏（S0 L1878–1931）

对照`CHP-22Index.pdf`物理页17的印刷p.459及S0栏界，核M.csv#33–81共49行：48个candidate仍为open，M#74 `see under Richmond, Duke of`别名维持excluded。47个可分类条目中新增46个类型（26 person、4 place、9 work、4 archive、2 term、1 family、1 procedure），保留既有M#78 person类型。M#50 `collection`指Manfrin超过400幅绘画的收藏；taxonomy尚无collection类型，保持open且类型待决。M#51所指是Manfrin组织的多次画家竞赛机制，归procedure；正文列出的情色主题不据索引另造作品或事件。M#53 `Mannerist painting`和M#75 `Marchands-amateurs`为term。Manin家族归family；Manchester mansions、Manin country house、Manin palace及Altieri palace归place。Maratta项下的雕塑、肖像、画作及St Stanislas Kostka altarpiece归work；Felsina Pittrice、Considerazioni sulla Pittura、Manfrin致Pietro Edwards的信及S. Andrea al Quirinale altarpiece文件归archive。M#70 `payment`在p.17指Maratta肖像的一般收费标准，不是独立付款事件；M#78 `work for Stefano Conti`概括Marchesini的多项代理与建议活动，没有可由该索引子项单独识别的作品，保留既有person类型。`Mantua, Marquis of`作为未具名人物候选登记，身份留待S3。

页图核读确认M#33/cand-1496印本末页为153，候选层从OCR索引CSV的`122`订正为`153`，原始S0和M.csv保留。M#35页图读作116；S0的`11Ó`是OCR误识，但候选页码已是116，不需改动。受控脚本`chp22_index_p459_l1878_1931_migration.py`锁定S0段、印本PDF、M.csv、taxonomy、相关正文来源、manifest及候选/coverage表前态；dry-run与apply均通过，并为两张改写表保留恢复副本。未改mentions、book statements或relations。当前候选11,436、mentions 26,829、statements 12,102；832段中649 complete、139有理由排除、44 queued、0 partial；开放未分类索引候选1,334。下一段为p.459页标`chp-22:22_CHP-22Index:l1933-1933`。

首次`audit_tables.py --summary`指出本段无mention/statement时，coverage.note缺少`no_semantic_content:`理由前缀。受控脚本的`--fix-coverage-rationale`模式经post-apply表哈希锁定、dry-run后只修coverage注释并备份；复跑审计`errors=[]`、`s2_missing=[]`。该修正不改变覆盖计数或事实表。


## 索引p.460页标（S0 L1933）

对照`CHP-22Index.pdf`物理页18确认印刷p.460。S0 L1933 `[Page 460]`是生成页标，不是索引词条或原书断言；单独标excluded/complete并保留`no_semantic_content`理由，不改候选、mentions、book statements或relations。受控脚本`chp22_index_p460_marker_l1933_exclusion.py`锁定S0段、印本PDF、manifest和S2表前态，dry-run与apply通过并为coverage留恢复副本。当前832段中649 reviewed/complete、140有理由排除、43 queued、0 partial；开放未分类索引候选1,334。下一段为p.460左栏`chp-22:22_CHP-22Index:l1935-1989`。


## 索引p.460左栏（S0 L1935–1989）（2026-10-07）

对照`CHP-22Index.pdf`物理页18印刷p.460、S0与M.csv#82–129逐项分类，共48条：M#86 `see under Vandières`是既有排除别名；其余47个open候选中新增43个类型，保留cand-1554/M#93既有person。分类为32个新person、2 place、2 work、3 archive、4 event；计入已有类型则共33 person。M#82–85、#87、#89、#91–93、#96、#99–107、#109、#115–118、#120、#122–129归person；M#97、#119归place；M#111、#121归work；M#88、#90、#95归archive；M#98、#108、#112、#114归event。M#94与#113是Marucelli的私人藏书，M#110是Massimi的古物收藏；三项均保留open/type-pending，因为taxonomy尚无collection类型。

正文语境核对：p.38称Marino写有一系列描写具名艺术家作品的诗；p.115称`Adone`为Marino著名诗作，故M#88、#90归archive文本，M#89“and Poussin”只保留Marino的人物语境。p.158称Marucelli撰写多位画家的生平，M#95归archive，藏书不误作机构或建筑。p.117称Massimi的Nunzio任职、私人藏书与古物收藏；前者留作person角色语境，后两项因收藏类型缺失待决。p.118称Massimi于1670年获任Cardinal及Maestro di Camera，归event；1677年委托Bartoli复制晚期古代Virgil手稿插图，复制品作为视觉作品归work，与原手稿（archive）区分；弟弟继承后迅速处分收藏，归event；Massimi重整Umoristi学院也归event。p.198明确Matteis绘制`Hercules at the Crossroads between Vice and Virtue`，归work；M#122“work for 3rd Earl of Shaftesbury”没有独立单件作品指称，保留人物活动语境。p.181的“neglect of his mature style”是对Mazarin欣赏偏好的描述，不另造事件或术语。索引的“and”子项、赞助/任职语境不自动建立关系；本段为索引导航与分类，不新增mentions或book statements。

页图核对：印本p.460将Marino页码印为122（S0 OCR误作123，候选/M.csv已是122）；M#117印为`Matina, L.`（S0 OCR作`Marina`，候选/M.csv已正确）；cand-1577/M#116 Mastelletta印本页码为393，S0 OCR近似作393′、M.csv与候选误录为395，候选页码由395校为393。只改候选层，不改来源OCR和原始M.csv。受控脚本`chp22_index_p460_l1935_1989_migration.py`锁定S0段、印本PDF、索引CSV、taxonomy、相关正文来源、manifest及候选/coverage前态；dry-run通过后应用，备份两张改写表。未改mentions、book statements或relations。审计`errors=[]`、`s2_missing=[]`；全库11,436候选、26,829 mentions、12,102 statements，832段中650 complete、140有理由排除、42 queued；开放未分类索引候选1,291。下一段为p.460右栏`chp-22:22_CHP-22Index:l1991-2045`。


## 索引p.460右栏（S0 L1991–2045）（2026-10-07）

对照`CHP-22Index.pdf`物理页18印刷p.460、S0与M.csv#130–173逐项分类，共44条；L1991 `AND PAINTERS`为跨栏运行页眉。M#142 `see under Mazarin`是既有排除别名；其余43个open候选中新增40个类型，保留cand-1611/M#151及cand-1617/M#157既有person。类别为30个新person、4 event、2 archive、3 term、1 procedure；计入既有类型则共32 person。M#130–132、#140–141、#143–149、#151–157、#159、#161–164、#166–173归person；M#133、#134、#137、#138归event；M#135、#136归archive；M#139、#158、#165归term；M#150归procedure。M#160 `collection`指Grand Prince Ferdinand的个人艺术收藏，taxonomy尚无collection类型，保持open/type-pending。M#142继续排除。

正文语境核对：p.176–177、p.181记Mazarin引Bernini赴法的具体尝试；p.182–183记其招揽Algardi、Fronde反对及购置Bentivoglio宫的行为，四者按具体历史行动归event。p.184称1653年为Mazarin藏品编成清单，作为archive；p.185–186 Brienne记临终告别藏品的文字为archive。M#139 taste依照对审美判断的索引语义归term。Grand Prince Ferdinand部分：p.230–241记他对艺术家、作家、Venice及藏品的支持、交往和兴趣；M#151/#157的艺术家子项沿用person类型但不据索引添加关系。p.231所述16世纪威尼斯绘画传统及p.232的绘画taste归term；p.240–241将展览作为反复组织的公共展示实践，含1706年特定展览与其后沿袭的展期，M#150据此归procedure。p.239“support in break with conventional history picture”、M#159 Venice和M#161–164的employment/patronage/collaboration/support均保留person语境，不拆成索引未能具体化的作品、关系或事件。M#160私人收藏因类型能力不足而暂缓，不冒充archive、institution或place。

页图核对印刷p.460及本段索引分栏；M.csv#142交叉引用已排除，M#151/#157既有person类型保留。M.csv与候选页码一致，本段无需候选定位修正；S0内的粘连、误识字符和跨栏运行页眉均保留为来源转录，不据OCR噪声改写原件。受控脚本`chp22_index_p460_l1991_2045_migration.py`锁定S0段、印本PDF、索引CSV、taxonomy、相关正文来源、manifest及候选/coverage前态；dry-run通过后应用并备份两张改写表。未改mentions、book statements或relations。审计`errors=[]`、`s2_missing=[]`；全库11,436候选、26,829 mentions、12,102 statements，832段中651 complete、140有理由排除、41 queued；开放未分类索引候选1,251。下一段为p.461页标`chp-22:22_CHP-22Index:l2047-2047`。


## 索引p.461页标（S0 L2047）（2026-10-07）

对照`CHP-22Index.pdf`物理页19确认印刷页码为p.461。S0 L2047 `[Page 461]`是生成页标，不是索引词条或原书断言；页图显示运行页眉`INDEX`在L2049，实体条目自L2050开始。将单行段标记为excluded/complete并写`no_semantic_content`理由，不改候选、mentions、book statements或relations。受控脚本`chp22_index_p461_marker_l2047_exclusion.py`锁定来源段、PDF、manifest及S2表前态；dry-run与apply通过，备份coverage。审计`errors=[]`、`s2_missing=[]`；当前832段中651 complete、141有理由排除、40 queued。下一段为p.461左栏`chp-22:22_CHP-22Index:l2049-2103`。


## 索引p.461左栏（S0 L2049–2103）（2026-10-07）

对照`CHP-22Index.pdf`物理页19的印刷p.461及M.csv#174–223审读左栏50条。L2049为运行页眉`INDEX`，实体条目从L2050起；S0把若干右栏词头碎片粘到左栏行尾，按页图栏界只处理M#174–223，右栏另由下一段处理。48个open候选新增类型：32 person、8 work、3 archive、2 event、1 place、1 family、1 term；保留cand-1682/M#222既有person。cand-1646/M#186 Andrea Memmo的私人绘画收藏类型待决，因为taxonomy没有collection类型；其余候选均保持open而不据索引生成KU。具体分类为：work—M#174/#175（Mei的`Justice and Peace`、`Youth rescued from the Pleasures of Venus`）、#177/#178（Melanconici的试验画`Abraham`及`David with the Head of Goliath`）、#190（Memmo的Prà della Valle城市设计）、#197（Antonello da Messina的`Deposition`）、#201（Michelangelo的`Risen Christ`）、#217（Mola的`Four Elements`）；archive—#187（`Elementi dell'Architettura lodoliana`）、#189（p.330及附录6所载Memmo关于画家地位的档案笔记）、#221（Molinos的`Guida Spirituale`）；event—#184（Memmo获任Procuratore di San Marco）、#191（为庆祝就任而刊行Lodoli的`Apologhi`）；place—#195 Messina；family—#198 Miani family；term—#214 `Modelli`，作为全书反复讨论的预备稿／模型概念归类，不指单件草图。Person类型（含既有M#222）为M#176、#179–183、#185、#188、#192–194、#196、#199–200、#202–213、#215–216、#218–220、#222–223。M#179的教堂作品泛指、#180和#218的付款、#183的“and Carlo Lodoli”、#185任职语境、#188政治改革热忱、#223经销活动均保留人物语境，不独立升为作品、事件或关系；M#222既有person类型不重复迁移。

页图校正两处派生候选：印本M#214 `Modelli`定位为255n，原S0 OCR和M.csv候选读作222n；cand-1674页码从222n校为255n。印本在Mola项下为`payments, 13n`，S0 OCR近似作`payments, izn`，M.csv#218及cand-1678却记录`Five Elements, 12n`；候选子项与定位校为`payments`、`13n`，按p.13一般付款说明留作Mola的人物语境。只改派生候选，不改S0或S1原始M.csv。正文分别支持p.9 Mola创作`Four Elements`，p.154 Mei两件顶棚寓意画，p.220–221 Melanconici作品及教堂委托，p.330和附录6 p.394–395的Memmo手稿笔记，p.364–368的Memmo政治抱负、Prà规划和Lodoli著作，p.382 Correr收藏的Antonello作品，p.81–83 Molinos著作；通用索引导航不产生mentions、book statements或formal relations。

受控脚本`chp22_index_p461_l2049_2103_migration.py`锁定S0段、印本PDF、M.csv、taxonomy、相关正文来源、manifest及候选/coverage/mentions/statements前态；dry-run核对50条映射、48个新分类、1个待决和两项页图校正后通过，再应用并为候选表与coverage保留恢复副本。审计`errors=[]`、`s2_missing=[]`；全库11,436候选、26,829 mentions、12,102 statements，832段中652 complete、141有理由排除、39 queued、0 partial；开放未分类索引候选1,203。下一段为p.461右栏`chp-22:22_CHP-22Index:l2105-2158`。


## 索引p.461右栏（S0 L2105–2158）（2026-10-07）

对照`CHP-22Index.pdf`物理页19确认本段为印刷p.461右栏；L2105 `X 461`是页码OCR噪声，右栏词条从L2106开始，至`Neapolitan painting, diffusion of`。M.csv#224–261共38条，其中#226 `Monsù Desiderio’ see under Nomé, François`沿用既有excluded别名cand-2919；其余37条新增类型：person—#224 Monari、#225 Monconys、#227 Monnot、#228 Jennifer Montagu、#229 Lady Mary Wortley Montagu、#230 Montaigne、#232 Cardinal Francesco del Monte、#233 Federigo da Montefeltre、#234 Count of Monterey、#235 Monterey（“employment of Ribera”是主词条的语境子项）、#237 Montesquieu、#238 Monteverdi、#239 Francesco Monti、#240 Montorsoli、#241 Morandi、#242 Morelli、#243 Morice、#244 Morlaiter、#245 Moroni、#246 Francesco Morosini、#248 Roger Morris、#249 Pietro Moscheni、#250 Abate G. A. Moschini、#252 Pierre Motteux、#253 Jean-Baptiste Van Mour、#254 Pietro Mulier、#257 Francesco de Mura、#258 L. A. Muratori、#260 John Murray、#261 Girolamo Muziano；place—#231 Montanari palace（Vicenza）、#251 Moscow（威尼斯绘画地点语境）、#255 Munich（17世纪赞助语境）、#256 Nymphenburg palace；event—#236 Monterey向Ludovisi家族购买Aldobrandini提香作品；family—#247 Morosini family；archive—#259 Muratori的`Della pubblica felicità, oggetto de' buoni principi`。

对照页图校正派生候选：cand-1693/M#234的页码从M.csv所列126校为印本136（S0与页图均为136）；cand-1717/M#258的274校为271n（S0与页图均为271n）。不改S0和M.csv。M#249印本及M.csv均读作Moscheni，S0 OCR的Moschetti保留为转录差异；正文p.321亦写Moscheni。子项“employment of Ribera”不单独升为人物关系或事件；正文p.172已有statement `st-chp7-p172-cont-i10`记载Monterey雇用Ribera，购买行为由正文`st-chp7-p171-i17`记录；p.193、p.297和p.318对应地点及Muratori著作的正文陈述亦已在既有S2段落登记。索引映射不重复创建mentions、book statements或relations。

受控脚本`chp22_index_p461_l2105_2158_migration.py`锁定S0段、印本PDF、M.csv、taxonomy、相关正文来源、manifest及候选/coverage/mentions/statements前态；dry-run核对38条映射、37个新分类、1个既有排除项和两处页码校正后通过，再应用并保留候选表与coverage恢复副本。审计`errors=[]`、`s2_missing=[]`；全库11,436候选、26,829 mentions、12,102 statements，832段中653 complete、141有理由排除、38 queued、0 partial；开放未分类索引候选1,166。下一段为p.462页标`chp-22:22_CHP-22Index:l2160-2160`。


## 索引p.462页标（S0 L2160）（2026-10-07）

对照`CHP-22Index.pdf`物理页20确认印刷页码p.462；S0 L2160 `[Page 462]`是生成页标，不是索引词条或原书陈述。将单行段标记为excluded/complete，不改候选、mentions、book statements或relations。受控脚本`chp22_index_p462_marker_l2160_exclusion.py`锁定来源行、印本PDF、manifest及S2表前态；dry-run与apply通过，并备份coverage。当前832段中653 reviewed/complete、142有理由排除、37 queued、0 partial。下一段为p.462左栏`chp-22:22_CHP-22Index:l2162-2215`。

## 补核p.461右栏N词条并完成p.462左栏（2026-10-07）

回看印刷p.461整页图发现，S0 L2148–2158在M.csv#224–261之后还含N.csv#0–9；原`chp22_index_p461_l2105_2158_migration.py`只映射M项，coverage虽标complete却漏了9个open N候选。现补录N#0 Nadal、N#1 Naples、N#2 feudal landowners、N#4 Nappi、N#5 Nationalism and art、N#6 Naudé、N#7 Nazari、N#8 Portrait of Carlo Lodoli及N#9 diffusion of Neapolitan painting；类型依次为person、place、term、person、term、person、person、work、term。N#3 Filippo Napoletano的see-under别名既有excluded状态保留。修正后该段覆盖M与N共48条索引记录，46条有类型、2条交叉引用排除。索引导航不新增mentions、book statements或relations。

对照印刷p.462左栏及N.csv#10–45、O.csv#0–11审读48条：34 person、10 work、1 place、2 term、1 archive。Negroni的St Francis Xavier chapel归place；Nepotism in Rome及`teste di fantasia`归term；Nogari、Nomé、Denon和Novelli的具名作品归work；Olina的`Uccelleria`依p.104注作为archive；Oliva的“and”子项只保留人物索引语境，不从索引导航创建关系。页图/正文校正仅作用于派生候选：cand-1734/N#14页码154n改154，cand-1754/N#34姓名Nordiall改Northall，cand-1755/N#35 Octavio改Ottavio，cand-1770/O#4子项Uccelliera改Uccelleria；S0与N/O.csv原件不改。受控脚本`chp22_index_p461_n_p462_l2162_2215_migration.py`锁定来源、页图PDF、索引CSV、taxonomy、正文证据、manifest及候选/coverage/mentions/statements前态；dry-run通过后应用并保留候选表与coverage恢复副本。没有改mentions、book statements或relations。审计`errors=[]`、`s2_missing=[]`；当前832段中654 complete、142有理由排除、36 queued、0 partial，开放未分类索引候选1,109。下一段为p.462右栏`chp-22:22_CHP-22Index:l2217-2270`。


## 索引p.462右栏（S0 L2217–2270）（2026-10-07）

对照`CHP-22Index.pdf`物理页20印刷p.462、S0与O.csv#12–36、P.csv#0–12逐项审读38条；O#23 Paolo Giordano Orsini与P#1 Padovanino为既有see-under排除项，其余36项分类为22 person、6 place、2 institution、4 term、1 work、1 archive。O#16–17 Oratorians是Rome/Venice语境下的宗教机构；O#18 Oratorio、O#34 Ottoboni的Cancelleria theatre以及P#2 Padua、P#3 Prato della Valle、P#5 Palazzo Ducale、P#7 Palazzo Chiericati归place；O#14 Opera in Rome、O#31 patronage effect、O#32 attracting painters failure与P#4 painting social significance是概念或主题归term；O#21 Daphnis and Chloe illustrations归work，O#26 Osservatore Veneto期刊归archive。O#33 patronage of Trevisani保持人物语境，不由索引子项创建关系。印刷p.462右栏还包含P#12 Paltronieri（L2259），已纳入本段；本页右栏止于Pamfili Gianbattista，下一源段为p.463页标。

同页正文候选cand-6545“theatre in the Cancelleria”据p.164–165具体场馆语境补为place；cand-6546舞台布景已为work。此处只补类型，不声称cand-6545与索引cand-1799已身份合并。索引段没有新增mentions、book statements或relations。受控脚本`chp22_index_p462_rcol_l2217_2270_migration.py`锁定S0段、印本PDF、O/P.csv、taxonomy、相关正文证据、manifest及S2表前态；dry-run通过后应用并保留候选表与coverage恢复副本。审计`errors=[]`、`s2_missing=[]`；当前832段中655 complete、142有理由排除、35 queued、0 partial，开放未分类索引候选1,073。下一段为p.463页标`chp-22:22_CHP-22Index:l2272-2272`。


## 索引p.463页标（S0 L2272）（2026-10-07）

对照`CHP-22Index.pdf`物理页21确认印刷页码p.463；S0 L2272 `[Page 463]`仅作生成页标，将单行段标记为excluded/complete，不改候选、mentions、book statements或relations。


## 索引p.463左栏（S0 L2274–2328）（2026-10-07）

对照印本p.463左栏、S0及P.csv#13–66审读54条：51项分类为26 person、5 place、2 institution、5 work、5 archive、6 term、2 event；P#36 `see also under French patronage`标为索引导航排除，P#38与P#60原有排除状态保留。P#19、#21、#31、#32、#50及#59按可讨论主题/条件归term，不把索引短语扩写成独立事件；P#20葬仪争议及P#55 Passarowitz和约归event。P#45–46只是Pasquali的人物语境，不从索引子项建关系；P#47–49、#51–52为出版物/书目文献，归archive。P#27 `Interior of the Pantheon`由p.357正文确认是Pannini画作，归work。P#66按词头所指实体空间归place，与正文已分开的cand-8963/place和cand-8964/work不作身份合并，交S3处理。

印本右栏在本段OCR行中混有碎片，按左栏边界只处理P#13–66；后续右栏从`l2330-2385`另行处理。受控脚本`chp22_index_p463_marker_l2274_2328_migration.py`锁定印本PDF、S0、P.csv、taxonomy、相关正文、manifest及候选/coverage/mentions/statements前态；dry-run和apply通过，并保留候选表与coverage恢复副本。未改mentions、book statements或relations。审计`errors=[]`、`s2_missing=[]`；当前832段中656 complete、143有理由排除、33 queued、0 partial，开放未分类索引候选1,021。

## 索引p.463右栏（S0 L2330–2385）（2026-10-07）

对照`CHP-22Index.pdf`物理页21印刷p.463及S0右栏，处理P.csv#67–114共48条，新增32 person、3 place、13 work类型。P#67–72为Pellegrini履历、地点或工作语境；P#78 S. Andrea della Valle归church/place，不从索引子项推断与Peretti-Montalto的正式关系。P#81 Permoser的`Apotheosis of Prince Eugene`、P#90肖像、P#94 Petrarch像、P#98 Tacca骑马像及P#105–106、#108–114具名或组合作品归work。P#103–104、#107继续作为人物语境；索引不生成关系。P#114 Piazzetta插图与1745年书籍archive候选cand-9990、图稿work候选cand-9991保持区分，不在S2宣称身份合并。

页图核对将cand-1901/P#102的印本页码`313`、`322`校正到候选；原P.csv及S0不改。受控脚本`chp22_index_p463_rcol_l2330_2385_migration.py`锁定S0、印本PDF、P.csv、taxonomy、相关正文、manifest及候选/coverage/mentions/statements前态；dry-run与apply通过，并为候选表和coverage保留恢复副本。未改mentions、book statements或relations。审计`errors=[]`、`s2_missing=[]`；当前832段中657 complete、143有理由排除、32 queued、0 partial，开放未分类索引候选973。下一段为p.464页标`chp-22:22_CHP-22Index:l2387-2387`。

## 索引p.464页标与左栏（S0 L2387–2444）（2026-10-07）

对照`CHP-22Index.pdf`物理页22确认印刷p.464。S0 L2387 `[Page 464]`是生成页标，排除并标记complete。左栏L2389–2444对应P.csv#115–163共49条，分类为23 person、19 work、2 place、3 event、2 archive。Piazzetta作品题名与Pittoni的历史画及McSwiny纪念画组归work；P#155–159的人名是画作/纪念对象子项，未另作人物候选。P#120 `prices`和P#153 `German patrons`留在艺术家person语境，与既有艺术家价格、赞助语境候选的处理一致，不建立未具名群体身份或关系。Pisani的逮捕、选任归event；支持他的诗歌/小册子与Platnerus的`Institutiones Chirurgicae`归archive；Pisani palace及Pitti Palace归place。

按物理页22校正派生候选：cand-1936/P#137子项`Danita`改为印本`Vanità`；cand-1948/P#149页码`222n`改为`335n`；cand-1950/P#151页码`315n`改为`315`。cand-1938/P#139的页码358与印本一致，S0 `z;8`保留为OCR转录。P.csv和S0均未改。受控脚本`chp22_index_p464_marker_l2389_2444_migration.py`锁定来源、PDF、P.csv、taxonomy、相关正文、manifest及候选/coverage/mentions/statements前态；dry-run通过后apply并保留候选表与coverage恢复副本。未新增mentions、book statements或relations。审计`errors=[]`、`s2_missing=[]`；当前832段中658 complete、144有理由排除、30 queued、0 partial，开放未分类索引候选924。下一段为p.464右栏`chp-22:22_CHP-22Index:l2446-2500`。

## 索引p.464右栏（S0 L2446–2500）（2026-10-07）

对照`CHP-22Index.pdf`物理页22确认印刷p.464右栏，处理P.csv#164–212共49条：47个候选分类为23 person、3 place、21 work；P#172 `Pomerancio, see under Roncalli`与P#186 `Poussin, Gaspard, see under Dughet`两个既有交叉引用排除状态保留。P#167 Poggio a Caiano、#173 Pommersfelden、#183 Bulstrode Park归place；P#180 tomb of Paul III及#184 Rigaud portrait归work；P#181–182 Portland及“and Sebastiano Ricci”保留人物语境，不据索引创建正式关系。Poussin主词条、altarpieces及#189–193与其他人物的并列项保留person语境；#194–212视觉题名及Arcadian Shepherds版本、dal Pozzo版Leonardo论著插图归work，不将被插图出版物与其插图合并。

页图核对将cand-1984/P#187页码28、115n、128分别改为38、115、138；cand-1987/P#190页码112改为113；cand-1989/P#192页码112改为115。只改派生候选，P.csv与S0保留原转录。受控脚本`chp22_index_p464_rcol_l2446_2500_migration.py`锁定来源、页图PDF、P.csv、taxonomy、manifest及候选/coverage/mentions/statements前态；dry-run通过后apply并保存候选表与coverage恢复副本。未新增mentions、book statements或relations。审计`errors=[]`、`s2_missing=[]`；当前832段中659 complete、144有理由排除、29 queued、0 partial，开放未分类索引候选877。下一段为p.465页标`chp-22:22_CHP-22Index:l2502-2503`。

## 索引p.465页标（S0 L2502–2503）（2026-10-07）

对照`CHP-22Index.pdf`物理页23确认印刷p.465；S0 L2502 `[Page 465]`与L2503 `INDEX`为生成页标/页眉，将该段标记为excluded/complete，不改候选或原书断言。

## 索引p.465左栏（S0 L2505–2559）（2026-10-07）

对照印本p.465左栏、S0及P.csv#213–263逐项审读51条。页图中左栏从Poussin的`Landscape with Man fleeing from Serpent`至Preti的`Marriage Feast at Cana`；S0同一段夹带右栏OCR词头碎片，物理栏界优先，右栏`Martyrdom of St Bartholomew`留到下一段。49条分类为24 person、24 work、1 archive；P#252 `museum`与P#253 `Museum Chartaceum`对应Cassiano的收藏/纸上博物馆语境，taxonomy没有collection类型，保持待决，且不在S2与正文候选认定身份相同。P#223 `pressure on to return to France`、P#234–246、P#249–251、P#254–259及P#262是人物语境；不从`and [person]`词项或同行出访子项创建关系。P#247 Bernini caricature及P#260–261、P#263是work；P#248 Leonardo `Trattato della pittura`的版本为archive。

页图校正五个派生候选定位：cand-2011/P#214 `48n`→`46n`；cand-2026/P#229 `155`→`15`；cand-2027/P#230 `112, 113, 114`→`113, 114`；cand-2055/P#258 `121n`→`13n`；cand-2056/P#259 `212n`→`213n`。P.csv和S0均保留原转录。受控脚本`chp22_index_p465_marker_left_l2502_2559_migration.py`锁定来源、印本PDF、P.csv、taxonomy、相关正文、manifest及候选/coverage/mentions/statements前态；dry-run通过后apply并保存候选表与coverage恢复副本。未新增mentions、book statements或relations。审计`errors=[]`、`s2_missing=[]`；当前832段中660 complete、145有理由排除、27 queued、0 partial，开放未分类索引候选828。下一段为p.465右栏`chp-22:22_CHP-22Index:l2561-2612`。

## 索引p.465右栏（S0 L2561–2612）（2026-10-07）

对照印本p.465右栏、S0及P.csv#264–275、Q-R.csv#0–33审读46条，从Preti的`Martyrdom of St Bartholomew`到Raphael的`St Michael`。45条新分类，保留Q-R#23 Ranuzzi既有person类型；全段26 person、11 work、5 term、3 place、1 event。P#265 artists' prices、P#268–271职业阶层、行省艺术赞助中心、罗马绘画受忽略及威尼斯出版者作为主题/概念归term。Q-R#6 Querini的逮捕与拘留归event；#7–8 Alticchiero乡间住宅及花园、#15罗马Quirinal归place。具名绘画为work，艺术家及其“and”索引子项保留人物语境，不据索引登记正式关系。

页图校正两个派生候选定位：cand-2062/P#265 `12n`→`13n`；cand-2098/Q-R#25 Raphael主词条`54n`→`54–56`、`362n`→`362–363`。P.csv、Q-R.csv及S0不变。受控脚本`chp22_index_p465_rcol_l2561_2612_migration.py`锁定来源、印本PDF、P/Q-R.csv、taxonomy、manifest及候选/coverage/mentions/statements前态；dry-run通过后apply并保存候选表与coverage恢复副本。未新增mentions、book statements或relations。审计`errors=[]`、`s2_missing=[]`；当前832段中661 complete、145有理由排除、26 queued、0 partial，开放未分类索引候选783。下一段为p.466页标`chp-22:22_CHP-22Index:l2614-2614`。

## 索引p.466页标（S0 L2614）（2026-10-07）

对照`CHP-22Index.pdf`物理页24确认印刷p.466；S0 L2614 `[Page 466]`为生成页标，不是索引对象，标为excluded/complete。

## 索引p.466左栏（S0 L2616–2670）（2026-10-07）

对照印本p.466左栏、S0及Q-R.csv#34–76逐项审读43条，从Rapparini的`Portrait du Vrai Mérite`索引项至Ricci, Marco。41条新增类型：18 person、14 work、5 term、2 institution、1 place、1 event；保留Q-R#35 Rapparini出版物archive及Q-R#76 Ricci Marco person既有类型。Q-R#36《拉施塔特条约》归event；#37 reason and fantasy及#40–43宗教修会赞助主题归term；#49–50 Remondini出版者和其印制作品语境归institution；#72 Riccardi palace归place。作品子项与艺术家分开；Ribera的“altarpieces for Monterey”及Giovanni Ricci的“patronage of Crespi”留作人物语境，不据索引建关系。Reni的“attack on Bamboccianti”也保留人物语境；正文p.141指出Passeri传记作者可能将部分自身情绪归于Reni，索引不足以单独确定言论作者。

物理页图将派生候选cand-2124/Q-R#51 Guido Reni页码321校为324；cand-2137/Q-R#64 Carlo Rezzonico `254, 323`校为`254, 362, 363`。仅改派生候选，Q-R.csv与S0不改。受控脚本`chp22_index_p466_marker_left_l2614_2670_migration.py`锁定S0与印本PDF、Q-R.csv、taxonomy、相关正文、manifest及候选/coverage/mentions/statements前态；dry-run通过后apply并保存候选表与coverage恢复副本。未新增mentions、book statements或relations。审计`errors=[]`、`s2_missing=[]`；当前832段中662 complete、146有理由排除、24 queued、0 partial，开放未分类索引候选742。下一段为p.466右栏`chp-22:22_CHP-22Index:l2672-2726`。

## 索引p.466右栏（S0 L2672–2726）（2026-10-07）

对照印本p.466右栏、S0及Q-R.csv#77–124审读48条，从Ricci, Marco的McSwiny `British Worthies`纪念画系列到Ridolfi, Carlo。新增42个类型：30 work、10 person、1 event、1 term；保留#81 Ricci Sebastiano person及#90、#102、#104、#106、#113五个既有work类型。p.289正文将McSwiny项目说明为一组纪念性绘画，并明确Marco与Sebastiano Ricci合作绘制Devonshire公爵纪念画；索引中的系列和具名纪念画归work，但不据此写入新的艺术家—作品关系。Q-R#80及#106–112“work for/in”项标为work语境候选，不登记正式赞助关系；#83“and Crozat”、#121–122 Richmond公爵与McSwiny系列的语境留作人物候选；#93“fear of style being corrupted by Rome”归term；#117 Richelieu试图将意大利艺术家引入巴黎是一项历史事件/倡议，不据索引建立多条正式关系。

页图校正cand-2154/Q-R#81 Sebastiano Ricci主词条页码311为310；仅改派生候选，Q-R.csv与S0保留原转录。受控脚本`chp22_index_p466_rcol_l2672_2726_migration.py`锁定S0与印本PDF、Q-R.csv、taxonomy、相关正文、manifest及候选/coverage/mentions/statements前态；dry-run通过后apply并保存候选表与coverage恢复副本。未新增mentions、book statements或relations。审计`errors=[]`、`s2_missing=[]`；当前832段中663 complete、146有理由排除、23 queued、0 partial，开放未分类索引候选700。下一段为p.467页标`chp-22:22_CHP-22Index:l2728-2729`。

## 索引p.467页标（S0 L2728–2729）（2026-10-07）

对照`CHP-22Index.pdf`物理页25确认印刷p.467；S0 L2728 `[Page 467]`及L2729 `INDEX`是生成页标与页眉，标为excluded/complete。

## 索引p.467左栏（S0 L2731–2785）（2026-10-07）

对照印本p.467左栏、S0及Q-R.csv#125–173逐项审读49条，从Rigaud, Hyacinthe至Salvator Rosa的`Landscape with Apollo`。S0同段混入右栏OCR碎片，按物理栏界处理；右栏延续的Rosa子项留给下一段。49条分类为24 person、19 work、1 archive、4 event、1 term。Q-R#130 Ripa的《Iconologia》归archive；#136 Romanelli获任Accademia di S. Luca、#156 Roomer在Masaniello起义中的逃离、#166 Rosa对bambocciate的抨击及#170在S. Giovanni Decollato展出均作为事件候选；#160 Roomer收藏体现的南北欧文化关系作为term。具名绘画和艺术家工作语境归work；人物往来、兴趣、收藏主题及地点活动不据索引写成正式关系。

印本校正两个派生候选定位：cand-2206/Q-R#133 Rockingham, Lord `211n`→`311n`；cand-2236/Q-R#163 Salvator Rosa `183`→`169`。仅改派生候选，Q-R.csv与S0不改。受控脚本`chp22_index_p467_marker_left_l2728_2785_migration.py`锁定S0与印本PDF、Q-R.csv、taxonomy、相关正文、manifest及候选/coverage/mentions/statements前态；dry-run通过后apply并保存候选表与coverage恢复副本。未新增mentions、book statements或relations。审计`errors=[]`、`s2_missing=[]`；当前832段中664 complete、147有理由排除、21 queued、0 partial，开放未分类索引候选651。下一段为p.467右栏`chp-22:22_CHP-22Index:l2787-2840`。

## 索引p.467右栏（S0 L2787–2840）（2026-10-07）

对照`CHP-22Index.pdf`物理页25印刷p.467右栏，逐项核Q-R.csv#174–222共49条，从Salvator Rosa的`method of selling pictures`到Rubens的`altarpiece for Chiesa Nuova`。47条新增类型为38 person、6 work、2 archive、1 event；保留Q-R#187 `see under Wynne, Giustiniana`既有交叉引用排除。Q-R#220 `Royal Collection`指向收藏实体，taxonomy未定义collection类型，明确保留open/type-pending，不改投institution、archive或place。

分类依据：Rosa的Prometheus、Regulus、Tityus为绘画作品；`Satire on Painting`对应p.142注引的`Della Pittura`诗文，归archive。`S. Alessio`是p.57–58所述具名歌剧，归work；概括性的operatic librettos是文献，归archive。Maratta portrait与Rubens的Chiesa Nuova祭坛画归work。Rosa拒绝赴巴黎邀请（p.187明确为1665年）是具体事件，归event；Rosa的艺术观、付款、赞助语境、Stoicism语境及一般生涯子项归person，不把`patronage by Carlo de' Rossi`、`and Salvator Rosa`、`and Luca Giordano`或`family links with Naples`写成关系。#202 Rossi并列姓名与#207祖孙说明留作后续身份对齐线索；不从索引单独确认亲缘边。

印本校读显示Q-R#191为Pope Clement IX，S0 OCR作`EX`；Rousseau页码在S0中数字空格错乱，候选已与印本及Q-R.csv一致。无候选页码修正；原始S0与Q-R.csv保留。受控脚本`chp22_index_p467_rcol_l2787_2840_migration.py`锁定该段、印本PDF、Q-R.csv、taxonomy、对应正文、manifest及候选/coverage/mentions/statements前态；dry-run通过后apply并保存候选表与coverage恢复副本。未新增mentions、book statements或relations。审计`errors=[]`、`s2_missing=[]`；当前832段中665 complete、147有理由排除、20 queued、0 partial，开放未分类索引候选604。下一段为p.468页标`chp-22:22_CHP-22Index:l2842-2842`。

## 索引p.468页标与左栏（S0 L2842、L2844–2897）（2026-10-07）

对照`CHP-22Index.pdf`物理页26确认印刷p.468；L2842 `[Page 468]`为生成页标，排除并标complete。物理左栏为L2844–2897，从Rubens续项至Sagrestani；按栏界未把右栏Saint-Non碎片并入。逐项核Q-R.csv#223–239及S.csv#0–28共46条，44条新分类为33 person、6 work、2 place、1 term、1 event、1 archive；Q-R#235 Cardinal Tommaso Ruffo的collection及S#22 Sagredo的prints-and-drawings collection因taxonomy没有collection类型，保留type-pending。

分类依据：Rubens的`Feast of Herod`及`work for Marie de Medici`为work候选，不由“work for”生成关系。Don Antonio Ruffo关于Rembrandt、Guercino、委托市场及收藏规模的子项保留person语境；p.210记其持续尝试为Guercino和Mattia Preti争取Messina公共委托，不作为一次孤立事件或关系。Cardinal Ruffo的Archbishop’s Palace, Ferrara归place；collection待决；`Neapolitan paintings`是其收藏/赞助语境，未指向单件作品。Sacchetti的Castel Fusano country house及Cardinal Ruffo的Ferrara palace归place。Sacchi的`Divine Wisdom`有图版表与p.50–51正文支持，为work；`modelli`为term；`work in Barberini palace`为work语境；对Bamboccianti的敌意、对Raphael的仰慕及Barberini关系语境归person，不建立关系。Sagredo的Carracci/Castiglione drawings归work，收藏分散归event，collection inventories归archive；并列人物、赞助和性情索引子项保留person语境。正文p.263–264说明Sagredo收藏、死后分散及1743/1762库存记录，不把整个收藏冒充archive。

印本确认候选页码已与Q-R.csv、S.csv一致；L2848的160n、L2867的111及L2885的343n/346在S0 OCR中分别呈`i6on`、`III`与粘连形，S1及候选表已规范化，无须修改候选定位。原始S0、Q-R.csv和S.csv不改。受控脚本`chp22_index_p468_marker_left_l2842_2897_migration.py`锁定S0、印本PDF、两份索引CSV、taxonomy、相关正文/图版表、manifest及候选/coverage/mentions/statements前态；dry-run通过后apply并保存候选表与coverage恢复副本。未新增mentions、book statements或relations。审计`errors=[]`、`s2_missing=[]`；当前832段中666 complete、148有理由排除、18 queued、0 partial，开放未分类索引候选560。下一段为p.468右栏`chp-22:22_CHP-22Index:l2899-2952`。

## 索引p.468右栏（S0 L2899–2952）（2026-10-07）

对照`CHP-22Index.pdf`物理页26印刷p.468右栏，逐项核S.csv#29–77共49条，从Saint-Non, Abbé de至Scalzi, Venice。新增分类32 person、8 work、3 institution、2 place、2 archive、1 family、1 event。S#30《Voyage Pittoresque de la Grèce et de la Sicile》与#54《Osservazioni sopra i lavori di niello》是文献，归archive；S#38 frescoes、#43 Bacchus、#50 Madonna delle Arpie、#53 Longhi portrait、#58–59及#61–62具名绘画归work。Salviati family (#36)归family。S#39 Scuola di San Rocco作为组织归institution，p.334记Albrizzi为其成员及Guardiano；#77 Scalzi指在威尼斯活动的赤足加尔默罗会分支，p.269–270所述教会建筑与宗教团体分开，索引主词归institution。Savoy (#67)按p.202明确所称的continental state归institution；St Petersburg (#31)是城市place，Sandi palace (#40)是建筑place。S#55 Sasso为John Strange购画记作交易事件候选，不据此生成正式关系；Prince Eugene的patronage和taste子项仍是person语境。其余人物与人物语境不转写为关系。

印本校读显示S0 OCR将S#59 portrait页码`131n`识为`13m`、S#69 `341n`识为`34m`、S#70 `201n`识为`20m`；印本及S.csv/候选表相符，无候选定位修正。受控脚本`chp22_index_p468_right_l2899_2952_migration.py`锁定印本、S0、S.csv、taxonomy、相关正文/图版表、manifest及候选/coverage/mentions/statements前态；dry-run通过后apply，并保存候选表与coverage恢复副本。S0与S.csv未改，无mentions、book statements或relations变更。审计`errors=[]`、`s2_missing=[]`；当前832段中667 complete、148有理由排除、17 queued、0 partial，开放未分类索引候选511。下一段为p.469页标`chp-22:22_CHP-22Index:l2954-2954`。

## 索引p.469页标与左栏（S0 L2954、L2956–3010）（2026-10-07）

对照`CHP-22Index.pdf`物理页27确认印刷p.469；L2954 `[Page 469]`是生成导航页标，排除并标complete。左栏L2956–3010按物理栏界核S.csv#78–126共49项，从Scaramuccia, Luigi至Skippe, John；L3012右栏从Skippon, Philip起，未混入本段。48项给出类型建议：32 person、6 work、5 event、1 family、1 institution、1 procedure、1 term、1 archive；保留S#124 Sixtus V“see under Peretti, Felice”的既有排除。

类型判断：S#79是Scaramuccia赠予Simonelli的具名版画（p.124，work）。Schulenburg子项中，#93 Corfù防御、#99从G. B. Rota购画雕塑、#101向德国庄园运送图片为事件；#94–95、#97–98所指绘画和#100由Simonini绘制的主要战役图像为work；#96的雕塑兴趣及#102的趣味保留人物语境。#88 Schönborn family归family；#104 Scuola Grande dei Carmini由正文称为协会总部，归institution，与教堂建筑place区分。#111 Servitù particolare指赞助人与艺术家的特殊雇佣机制（第1章pp.6–8），归procedure。Shaftesbury的#116艺术家指示按具体委托行为归event；#117艺术“civilising”社会的作用为term；#118赴那不勒斯退隐为event；#119 Second Characters为书籍/archive。人物“and”子项仅保留候选语境，不凭索引写关系。

印本校读：p.469确认S0中Schönborn, Friedrich Karl页码`29311`应读`293n`、Don Carlo Silva的`2371n`应读`237n`、Schulenburg的`taste sor`应读`taste for`；S.csv与候选页码/子项已对应印本，无locator改动。另S.csv#111将印本`Servitù particolare`误录为`Servizio particolare`；结合页图和第1章pp.6–8，将派生候选cand-2423的canonical name校为`Servitù particolare`，保留S.csv与S0原样。

受控脚本`chp22_index_p469_marker_left_l2954_3010_migration.py`锁定印本、S0、S.csv、taxonomy、所引正文、manifest及候选/coverage/mentions/statements前态；dry-run通过后apply，并为候选与coverage保存`.bak-s2-chp22-index-p469-left-l2954-3010-20261007`恢复副本。S0、S.csv、mentions、book statements、relations未改。`audit_tables.py --summary`：`s2_missing=[]`、`errors=[]`；当前832段中668 complete、149有理由排除、15 queued、0 partial，开放未分类索引候选463。保留两条既存enrichment来源引用警告（`enr-06678`、`enr-06937`）及S2语义质量尚待交接审查的提示。下一段为p.469右栏`chp-22:22_CHP-22Index:l3012-3066`。

## 索引p.469右栏（S0 L3012–3066）（2026-10-07）

对照`CHP-22Index.pdf`物理页27印刷p.469右栏，逐项核S.csv#127–168共42项，从Skippon, Philip至Soldani, Massimiliano。分类41项：19 person、13 event、5 archive、2 place、1 term、1 family；S#151 medal cabinet仍不分类。S#139–141的Bibliotheca Smithiana、pars altera和Catalogo均为书目/售书目录文献，归archive；S#147 Dactylografia Smithiana是记载Smith勋章与宝石、含Brustolon 100幅版画的书，归archive而非作品集。S#146 Mogliano country house与#153 Palazzo Balbi为place；#166艺术家的社会地位为term，#167 Soderini family为family。

Smith人物子项中的往来、趣味、英格兰访客和Schulenburg收藏比较（#130–138、#143–145、#148、#152）保留人物语境；不凭“and”、contacts或比较词生成关系。具体委托、藏书处置、婚姻、出版、购藏、1766复任领事及拍卖记录（#142、#149–150、#154–162、#164）归event；#163 support for Pasquali’s publishing firm仍归Smith人物语境。相应的Smith–Pasquali关系候选已由正文statement `st-chp10-p299-pasquali-firm-launched`、`st-chp10-p301-smith-pasquali-publication-activity`记录，本段不重复写边。婚姻子项对应p.302所述Smith与Katherine Tofts的第一次婚姻及其82岁时与John Murray之妹的第二次婚姻；索引概括不替代已有正文裁决。Will（#165）为archive，不是人物类型。Medal cabinet（#151）仅保留类型待决，既有候选cand-9556说明来源只转述其质量评价，无法确定是柜体、勋章组还是收藏。

印本校读与派生候选订正：主词头Smith, Joseph（#129）印为299–310后接314，去掉S.csv及候选中误加的311；#139 Bibliotheca Smithiana页码应为310、394（S.csv误作212、394）；#141标题印作`Catalogo di Libri Raccolti dal fu Signor Giuseppe Smith`，将候选`Catalogus`校为`Catalogo`；#160印本303后无注号，#161页码为307、310（非307n、317）；#163补入印本遗漏的301。S0中`Dactylograjia`等OCR错读按印本读，不改S0或S.csv。第10章p.300、302、306注、307、309–310及附录p.391–394支持相关目录、婚姻、交易和不确定性；附录作者未能判明1762年是否售尽藏画，故只标交易事件，不把“售尽”写成确定事实。第13章p.337正文作`Dactylografa Smithiana`，索引和P.csv候选作`Dactylografia Smithiana`；cand-2458与cand-1848，以及cand-2450/2451/2452与cand-9274/10833/10832、cand-2476与cand-8651、cand-2462与cand-9556之间的身份对应均留S3判断。

受控脚本`chp22_index_p469_right_l3012_3066_migration.py`锁定印本PDF、S0、S.csv、taxonomy、相关正文、manifest及候选/coverage/mentions/statements前态；dry-run通过后apply，并保存候选表与coverage恢复副本`.bak-s2-chp22-index-p469-right-l3012-3066-20261007`。仅改候选类型、6项派生定位/题名和coverage；未改S0、索引CSV、mentions、book statements或relations。下一段按manifest为p.470页标`chp-22:22_CHP-22Index:l3068-3068`。


## 索引p.470页标与左栏（S0 L3068、L3070–3124）（2026-10-07）

对照`CHP-22Index.pdf`物理页28确认印刷p.470；L3068 @[Page 470]@为生成导航标记，排除并标complete。左栏L3070–3124逐项核S.csv#169–218共50项，从Sole, Giovan Gioseffo dal至Strudel, Peter；全部分类为21 person、19 work、3 event、2 archive、5 term。下一段L3126–3179才开始Strudel的`Tarquin and Lucretia`子项，本次按段界未纳入。

人物主词头及一般生涯、交往与趣味子项保留person语境；#181 `work for Raimondo Buonaccorsi`未指明独立作品或单次委托，仍归Solimena人物语境；#206 `and G. M. Sasso`及#209对Venice的admiration不凭索引措辞建立关系。具名绘画与作品组（#170–180、#185–187、#202、#210、#212–215）归work；《The Levites》由第8章p.216明确为Storer受委托完成的教堂画作，第10章p.316将`Glory of Venice`称作已毁的寓意画。战争、Guardi任职和Streit遗赠（#191、#207、#211）归event；《The Spectator》与《De Bello Belgico》（#192、#204）作为期刊/著作归archive；Spanish patronage及其时段/对象、Status-seeking和Stoicism（#188–190、#196、#199）归term。S#216 Strozzi据附录p.393仅能确认是匿名售画记录中列出的画家姓氏，身份留待S3。

印本校读：S#174在PDF及第8章p.214均作`Deborah and Barach`，S.csv误录`Deborah and Barak`，故仅订正派生候选cand-2485。S#182 Spada, Cardinal Bernardino定位由`75n, 139`校为印本`75, 139`；S#184 Spadaro, Micco定位由`139n, 204n`校为`139, 204n`。S#180印本作`Rebecca and Eliezar`，而S.csv与第8章p.214均作`Rebecca and Eliezer`，候选保留正文与索引CSV支持的Eliezer写法，并记录印本异文。

作品归属待决：S#186将`Revolt of Masaniello`列在Spadaro词头下；但第5章p.139及Plate 22b把同名作品叙述为Cerquozzi所作。可能是索引误归，也可能是不同作品；不将索引子项当作作者断言，不与正文作品候选cand-4060合并。cand-2497的detail记录该冲突供后续身份对齐。第8章p.207注1已有Pool of Bethesda与Woman taken in Adultery的跨收藏陈述；第10章p.315遗赠、p.316家族肖像及第16章p.374 Guardi任职分别已有statement候选`st-chp10-p315-streit-bequests-of-acquired-pictures`、`st-chp10-p316-streit-displayed-family-portraits`和`st-chp16-p374-strange-employs-guardi`。索引不重复新增mentions、book statements或relations。

受控脚本`chp22_index_p470_marker_left_l3068_3124_migration.py`锁定印本PDF、S0、S.csv、taxonomy、相关正文/附录、manifest及候选/coverage/mentions/statements/relations前态；dry-run通过后apply，并保存候选表与coverage恢复副本`.bak-s2-chp22-index-p470-l3068-3124-20261007`。仅更新候选类型、3处派生字段和S2 coverage；未改S0或S.csv。

## 索引p.470右栏（S0 L3126–3179）（2026-10-07）

对照`CHP-22Index.pdf`物理页28审读S.csv#219–225及T.csv#0–37，共45条索引记录，从Strudel的`Tarquin and Lucretia`到Tiepolo未完成的Algarotti肖像。分类33 person、4 work、3 archive、3 institution、1 place、1 term；T.csv#1原已分类为person，因此本段新增44个候选类型。Tacca词头仍是人物；Orsini委托文件由既有archive候选cand-5606及附录p.387 statement单独表示。`Gerusalemme Liberata`作为Tasso的文学文本归archive，与1745年插图本及后文提及的绘画组区分；`Zibaldone`与`Trattato di Pittura`也属archive。Theatines修会及其巴黎、罗马语境归institution，慕尼黑教堂归place；Tarso大主教的个人身份未解决。Tiepolo与Algarotti的`mutual influence`索引语境不构成关系；未完成肖像保留work候选，其身份/归属仍受后记p.409限定。

按印本校正cand-2539拼写`Talbot, Bruno`→`Talbot, Buno`，并校正cand-2569索引定位`383n, 405n`→`384, 405`。候选字段采用印本拼写，T.csv原转录不改。对11条既有正文statement仅补`qualifiers.relation_candidate=true`，供S6复核端点、方向和关系类型；没有新增book statement或正式关系。S0、索引CSV、mentions及relations表均未改。受控迁移脚本`chp22_index_p470_right_l3126_3179_migration.py`先dry-run后apply，锁定来源、索引CSV、相关正文、manifest、taxonomy与表格前态；候选、coverage和statements恢复副本保留在对应表目录。审计`errors=[]`、`s2_missing=[]`；当前832段中671 complete、150有理由排除、11 queued、0 partial，开放未分类索引候选331。下一段按manifest为p.471页标`chp-22:22_CHP-22Index:l3181-3182`。

## 索引p.471页标与两栏（S0 L3181–3292）（2026-10-07）

对照`CHP-22Index.pdf`物理页29确认印刷p.471。L3181–3182的`[Page 471]`与`INDEX`是生成导航标记和页眉，标为excluded/complete。随后L3184–3292为p.471索引两栏，逐项核T.csv#38–127与UVWXYZ.csv#0–3，共94条；分类为35 person、50 work、4 term、3 place、2 event。Tiepolo词头中，具名绘画、壁画、草图、版画及Würzburg四幅具名作品按work处理；仅泛指“为谁工作／在哪里工作”、交往、观点和未识别赞助语境的子项保留person候选，不由索引单独建立关系。`payments to`与赴马德里的具体行程按event处理；威尼斯旧制度信念、价格语境、艺术家授衔及城市艺术赞助语境按term处理；Turin、Udine为place，具名艺术家仍是person。该页的`drawings in Pietro Monaco collection`指Tiepolo作品组，不另造collection对象；T#109“commission from Stefano Conti”沿用Torelli人物候选，附录中的委托档案及既有statement保留原端点语境。

页图校读后订正三个派生候选字段：cand-2595的`Judgment of Solomon`改为印本`Justice of Solomon`；cand-2607的`Saints Agnes, Rose and Catherine`改为印本与第9章p.271正文一致的`Saints Agnes, Rosa and Catherine`；cand-2630 Titian总词头定位将374改为印本376。T.csv、UVWXYZ.csv与S0原文不改；前两项候选detail保留索引CSV原异文。p.253正文statement `st-chp9-p253-udine-fresco-sites-and-works`的限定语已同步：同一性仍交S3与正文候选cand-8283核定。另将已有陈述`st-chp6-p164-v1-22`补标`relation_candidate=true`，因为正文明确记Trevisani为Ottoboni绘制作品；该事实进入S6复核，未新增关系。

识别并保留两处不改写S0的来源异文：L3241 OCR作1136，但p.471印本与第10章p.296均为1156，cand-2622的detail已是1156；印本索引L3247似作`S. Pola`，T.csv与第10章p.323正文均作`S. Polo`，候选保留后者。印本`Varj Capriccj`与CSV规范化拼写`Vari Capricci`也保留为来源字形差异。没有新增mentions或book statements，也没有写入正式relation。受控脚本`chp22_index_p471_left_l3181_3292_migration.py`完成dry-run与apply，锁定相关来源、索引PDF、manifest、taxonomy及候选/coverage/statements前态，并保存三表恢复副本。审计`errors=[]`、`s2_missing=[]`；当前832段672 complete、151有理由排除、9 queued、0 partial，开放未分类索引候选241。下一段按manifest为p.472页标`chp-22:22_CHP-22Index:l3294-3294`。


## 索引p.472页标与两栏（S0 L3294–3405）（2026-10-07）

对照`CHP-22Index.pdf`物理页30确认印刷p.472。L3294 `[Page 472]`为生成页标，coverage记excluded/complete；两栏按索引CSV逐项核对：L3296–3349对应UVWXYZ.csv#4–52，共49行，#4 Urban VIII是既有see-under排除，另48条分类为26 person、15 work、4 event、2 place、1 family；L3351–3405对应#53–99共47条，分类为9 person、7 work、29 term、1 place、1 archive。馆藏/机构成员、委托语境、为谁工作及Venice的主题子项均按对象语境分类，索引导航不独立生成正文事实、mentions或关系。

页图确认四处派生定位校正：cand-2693 Vanetti `37n`→`377n`；cand-2709 Velasquez将OCR误读的122、158、385分别校为印本133、138、384；cand-2718 La Chiesa标题`252n`→`335n`；cand-2755 Veronese将`279n`改为`279`、`355`改为`356`。印本与正文交叉核实Valeriano拼写，不将OCR点号写入作品名。索引候选与正文Scala Regia、La Chiesa档案和Velasquez机构端点保持分立，供S3身份对齐；foreign patrons仍是未具名群体，索引本身不确立赞助关系。未改S0、UVWXYZ.csv、mentions或relations.csv。

关系候选沿用已有正文证据：13条既有book statement补`relation_candidate=true`；将p.126 Velasquez两个成员机构拆为端点明确的独立statement，并将p.196 Verrio服务对象拆为Louis XIV与William III两个端点，新增两条statement。具体关系方向、类型和证据适配留待S6核定；未写入正式关系边。受控脚本`chp22_index_p472_migration.py`锁定来源、页图映射、索引CSV、taxonomy、正文语境和候选/coverage/statements前态，先dry-run后apply；保留三表恢复副本。机械审计发现索引段无mentions/statements时需要明确`no_semantic_content:`理由，已补到两条coverage注释；复审`errors=[]`、`s2_missing=[]`。当前832段674 complete、152有理由排除、6 queued、0 partial；候选11,436、mentions 26,829、statements 12,104，开放未分类索引候选146。下一段为p.473页标`chp-22:22_CHP-22Index:l3407-3408`。

## 索引p.473页标与两栏（S0 L3407–3515）（2026-10-07）

对照`CHP-22Index.pdf`物理页31核实印刷p.473及两栏边界。L3407–3408为`[Page 473]`和`INDEX`页标/页眉，记excluded/complete；左栏L3410–3463对应UVWXYZ.csv#100–146共47行，#124 Vivant-Denon see-under沿用既有排除，余46条开放记录中45条有类型（含既有cand-2798/person），cand-2765/#101“collection”类型待决。右栏L3465–3515对应#147–190共44条，41条有类型，cand-2848–2850/#185–187的medals and gems、paintings and caricatures及print collection因taxonomy没有集合类型而保留待决。全页90条开放候选共86条已有类型、4条类型待决；新增85个类型标注，类型合计57 person、9 archive、7 work、5 place、3 event、2 family、1 institution、1 term、1 procedure。索引页脚L3463不作实体或断言。

语义分类按索引实际指称处理：Aeneid、Autobiography、Anecdotes、The White Devil、Night Thoughts、Wynne对Querini别墅的文字记述及Zanetti两部出版物为archive；Virgil肖像、Visentini版画与Palladian门楣、Vouet肖像、Zanchi作品与Zanetti木刻为work；White Hill战役与Zanchi付款、购买Arundel图稿为event；晚17世纪战争影响艺术赞助为term，木刻技法复原为procedure。#176–181与#184保留Zanetti人物语境，不由索引子目推造关系。按印本将cand-2838主词条定位从341–344扩至341–346；S0和UVWXYZ.csv原文不改。

回查p.218、p.283及p.341–344正文，为12条已有statement补`relation_candidate=true`：Zanchi作品执行/验收、Werff绘画进入Johann Wilhelm画廊、Arundel图稿对Zanetti品味的影响、旅外旧作对品味的影响、Zanetti携回medals/gems、收藏版画、拥有Brand/Dietrich画作、Carriera粉彩/微型画、Sebastiano历史画、复原木刻技法及制作约50张木刻，以及Smith/Schulenburg交往。将Smith与Schulenburg各自拆为端点明确的候选陈述；另新增Zanetti与Sebastiano Ricci交往、与Rosalba Carriera友谊两条端点明确陈述。新statement共3条，关系列仍留S6裁决；未新增mentions或formal relations。

受控脚本`chp22_index_p473_migration.py`锁定来源Markdown、印本PDF、索引CSV、S0段哈希、taxonomy和目标表前态，默认dry-run；预演确认91行、分类计数和目标statement后apply，并保留候选、coverage、statements恢复副本。首次apply因脚本缺少JSONL写入函数中断；从预备副本恢复候选与coverage表、补齐函数并重跑dry-run，再成功apply。最终表审计`errors=[]`、`s2_missing=[]`；全书现有11,436候选、26,829 mentions、12,107 statements；coverage为676 complete、153有理由排除、3 queued、0 partial；开放未分类索引候选61。下一段为p.474页标`chp-22:22_CHP-22Index:l3517-3517`。

## 索引p.474页标与两栏（S0 L3517–3588）（2026-10-07）

对照`CHP-22Index.pdf`物理页32核实印刷p.474与两栏边界。L3517为生成页标，记excluded/complete；左栏L3519–3542对应UVWXYZ.csv#191–210共20条，右栏L3567–3588对应#211–225共15条。35个索引候选均保持open；#197/cand-2860的既有person类型保留，另34条新分类为21 person、4 archive、7 work、1 family、1 place。左栏类型为12 person、4 archive、2 work、1 family、1 place；右栏为10 person、5 work。

按对象语境分类：Della Pittura Veneziana、Ricche Miniere、Elogio di Rosalba Carriera及六位作家的文本版本组归archive；Zanetti家族归family，Zenobio palace归place。Varie Pitture a Fresco是1760年出版的视觉版画册，按taxonomy的艺术图册规则归work；因此同题正文候选cand-10117由archive改为work，仍与索引候选cand-2859分开等待S3身份对齐。Zocchi双人肖像、Zompini版画系列、Le Arti、六幅Rebecca故事风景画、Hunt of Meleager and Atalanta及Palladian overdoors归work；其中Hunt仅是p.351所提拟议题材，不据此认定作品已完成。索引人物子项只作语境入口，不独立证明关系。

印本页图纠正S0的跨栏/OCR读数：Zatta（非`Zana`）、Zompini（非`Zompmi`）、Zucchi前无`der`，`revision of Boschini’s`中有空格；页图将`6 Landscapes...`确认成独立带引号作品子项，去除S0串入的`...sso`残片。S0和UVWXYZ.csv均保持不改。

修正既有正文候选外键：p.308–309中误连到作品候选cand-2883的Zuccarelli提及与statement映射回人物cand-2879，p.309“work in England”语境映射到人物候选cand-2884。p.344将Zompini姓名及代词从作品候选cand-2875/cand-2876改回人物cand-2874；另新增cand-11458表示Zanetti收藏的Castiglione原画，将其与Zompini的输出版画cand-10110分开，所有权statement指向原画，创作statement指向版画成果。cand-2875/cand-10110及cand-2876/cand-10111仍保持各自独立，留待S3对齐。

将p.342 Zanetti早期欣赏Canaletto和Zuccarelli的合并陈述拆为两个端点明确的statement。为p.328 Baretti、Biffi、Smith、Zanetti的四条褒扬/雇佣陈述，p.339 Zatta支持Dante、p.342 Zanetti欣赏艺术家，以及p.345三条出版/编辑/著述记录补`relation_candidate=true`；共补9条既有标记并新增一条端点明确statement。它们仍是S2关系候选；未写入formal relations。

受控脚本`chp22_index_p474_migration.py`锁定来源、taxonomy、目标表前态及三段哈希，默认dry-run；预演核对分类、提及/陈述外键和关系候选后apply，保留candidate、mentions、coverage、statement四份恢复副本。apply后机械审计`errors=[]`、`s2_missing=[]`；当前11,437候选、26,829 mentions、12,108 statements，832段中678 complete、154有理由排除、0 queued、0 partial；开放未分类索引候选27。下一步转入来源范围与S2交接审计，先核明p.446 `Bentveugels`/`Bergamo`索引种子映射，再比较4个旧版后部`*_intro.md`与规范分节来源。

## p.446 索引种子缺项回补（2026-10-07）

对照CHP-22Index.pdf物理页4（印刷p.446）与S0 L399–402，确认B.csv遗漏四条而非此前只标出的两个主词头：Bentveugels、Bergamo主词头，以及Bergamo下Santa Maria Maggiore、S. Paolo d’Argan两个具名地点子项。Bentveugels指向罗马的北方画家团体，taxonomy归institution；Bergamo和两座具名教堂/建筑位置均归place。章1现有Bentveughels与Schildersbent提及分别映射到cand-3152、cand-2989；Bergamo及Santa Maria Maggiore也有多个正文候选，全部保留待S3身份对齐，不复用身份或据索引添加正文关系。

为保留B.csv现有0–323行索引键，将四个转录补项追加为B.csv#324–327，并新增cand-11459–11462。CSV补项字段依据印本页图；S0和PDF不改，已有mentions/statements不重写。受控脚本chp22_index_b446_seed_backfill.py锁定PDF、S0、taxonomy、B.csv和候选表哈希，默认dry-run；核对缺项、追加行号、类型及新增ID后apply，保留B.csv和候选表恢复副本。索引种子计数现与结构化CSV行数增加到2,934；此回补只解决p.446发现的四行，全书纸本索引与CSV逐项对照仍待完成。

## 书后平行OCR与索引转录范围复核（2026-10-07）

逐份对照五个未纳入S0的书后平行OCR文件与规范来源：`18_CHP-18Conclusion_intro.md`、`19_CHP-19Appendix_intro.md`、`20_CHP-20Postscript_intro.md`、`21_CHP-21Bibliography_intro.md`、`22_CHP-22Index_intro.md`。比较以规范OCR、印本PDF和已登记S2锚点为准，不把平行OCR计作新来源段。结论旧稿除文件标题外无实质差异。附录旧稿将173 c. 2书信重复放在Footnotes末尾；规范OCR和印本页序已把该信放回175条目前，并去掉旧稿重复。后记旧稿把9、10号注释文献留在后段，规范OCR将其移入对应页注区；正文词间空格差异不改变语义。书目旧稿将Noemi Gabrieli条目置于p.423的G字头，规范OCR把同一条错位到L1304；已有`cand-11333`及statement `st-chp21-bib-l1301-1306-xref-05`保留错位OCR锚点并回链至规范p.423 L503的书目位置。未发现这些副本含规范S0及现有迁移之外的独有实质文本。

索引旧稿是低质量平行OCR，主要差异为脚注页码后缀`n`漏识、跨栏/OCR粘连及页标；规范索引首页本身没有印刷页码，按物理第1页和次页可见p.444推定为p.443，coverage已排除误读的`[Page 24]`标记并覆盖该首页左右栏。印刷p.444–474连续对应后续31页；当前索引规范源共94段，均已reviewed或有理由排除且migration complete。

对照19组A–Z索引Markdown与CSV：原有Markdown表共2,930行，CSV新增p.446四行后为2,934行；B.md也已追加相同四项，两个索引表均为2,934行。B.csv保留印本页码缩写，B.md按其既有格式展开页码；两边记录逐项对应。除A.csv外的18组既有记录在页码范围与撇号规范化后逐行一致。A.csv为旧Windows-1252编码，不能按UTF-8读取；四处OCR字符损坏为`Almor¨°`、`Br¨¹hl`、`citt¨¤`、`Pr¨¤`，对应印本物理页1–2上的Almorò、Brühl、città、Prà。候选`cand-0024`、`cand-0045`、`cand-0093`、`cand-0104`均按印本及A.md登记了正确字形。未改写原A.csv字节。所有2,934个A–Z行号均有且仅有一个candidate index ID；其余索引页的PDF/CSV对应关系和逐段分类见本过程记录各页条目。

该复核完成书后五个平行OCR副本的范围比对和索引CSV/Markdown行映射；全书17个整章OCR对照副本及语义交接仍须按来源登记继续审计。当前`audit_tables.py --summary`为`segments=832`、`s2_missing=[]`、`errors=[]`、`678 complete/154 excluded/0 queued/0 partial`。两条既存enrichment `source_ref`警告（`enr-06678`、`enr-06937`）与结构审计分开保留；机械闭合不证明召回率或语义质量。

## 第2章整章OCR范围核对（2026-10-07）

将未纳入S0的`02_CHP-2.md`按51个页块与规范分节及派生视觉转录逐页比对。正文页与规范来源高度重合；低重合页为图版页，且图版信息已有明确归位：整章页3的Plate 2组题及两条题注对应`02_CHP-2_sec_i_visual-transcription:L1–4`；页4 Plate 3题注对应`02_CHP-2_sec_i_plate3_visual-transcription:L1–3`；页5 Plate 4组题和题注对应`02_CHP-2_sec_i_visual-transcription:L6–9`；页22 Plate 5组题在`02_CHP-2_sec_ii_plate5_visual-transcription:L1–3`，Bernini题注由规范段`02_CHP-2_sec_ii:L106–107`承载；页25 Plate 8分组题头在`02_CHP-2_sec_ii_visual-transcription:L5–6`，Castelli题注由`02_CHP-2_sec_ii:L115–116`承载；页42 Plate 9、页43 Plate 10及题头、页45 Plate 12分别由`02_CHP-2_sec_iv:L154–155`、`02_CHP-2_sec_iv_plate10_visual-transcription:L1–2`与`02_CHP-2_sec_iv:L157–159`、`02_CHP-2_sec_iv:L165–169`承载。Plate 6、7、11也分别在对应规范段或视觉转录覆盖。对照S2 coverage，章2的75条记录均为`migration_status=complete`，无queued或partial；未发现整章副本独有的实质正文、脚注或图版信息。整章副本是比较副本，不计入规范来源段数。此项是范围与重复审查，不代替全书语义交接验收。

## 第3章整章OCR范围核对（2026-10-07）

将未纳入S0的`03_CHP-3.md`按35个页块与规范分节来源比对。页块筛查只在p.11–14出现图版题注导致的低文本重合：Plate 13的题注由`03_CHP-3_sec_ii:L83–84`覆盖；Plate 14题注由`L86–87`覆盖，印本另有的“JESUIT PATRONAGE OF THE ARTS”组题与图版指针按既有过程记录作版面导航元数据，不另计历史断言；Plate 15由`L89–90`覆盖；竖排Plate 16由`L92–100`覆盖。上述段均已对照`CHP-3.pdf`物理页11–14校读。其余页块与规范分节高度重合。章3共47条coverage记录，42条reviewed/complete、5条有理由排除，0条queued或partial；没有发现整章副本独有的实质正文或脚注。整章OCR不计入规范来源段数；本核对是来源范围与重复审查，不替代全书语义交接验收。

## 第4–5章整章OCR范围核对（2026-10-07）

对照`04_CHP-4.md`的30个页块及`05_CHP-5.md`的30个页块与对应规范分节。第4章低重合页为p.12–14：Plate 17三条肖像题注由`04_CHP-4_sec_ii:L65–67`承载；Plate 18组题由派生视觉转录`04_CHP-4_sec_ii_visual-transcription:L1`承载，题注由`L69–71`承载；Plate 19–20组题与交叉指针由该视觉转录`L3`承载，Plate 19题注由`L73–75`承载。第5章低重合页为p.18和p.20：横排Plate 21a/b题注由`05_CHP-5_sec_iii:L45–57`承载，Plate 23a/b题注由`L63–65`承载；相邻Plate 22题注也由`L59–61`覆盖。各题注均已有对应S2提及、断言或明确的编辑性组题排除理由，并在对应PDF页校读。其余页块与规范分节高度重合。coverage分别为第4章40条（37 reviewed/complete、3 excluded/complete）和第5章41条（35 reviewed/complete、6 excluded/complete），均无queued或partial。未发现整章副本独有的实质正文、脚注或图版信息；两份整章OCR均不计入规范来源段数。本核对不替代全书语义交接验收。

## 第6–7章整章OCR范围核对（2026-10-07）

第6章`06_CHP-6.md`的21个页块与对应规范分节逐页比对，文本五词组筛查最低重合率为0.94，未出现低重合图版例外；coverage 33条，28 reviewed/complete、5 excluded/complete，无queued或partial。第7章`07_CHP-7.md`的43个页块中，低重合页均为图版：p.19 Plate 25由`07_CHP-7_sec_i:L178–179`覆盖；p.20 Plates 26a–b由`L181–182`覆盖；旋转的p.21 Plate 27及页眉由`L184–200`处理；p.22 Plate 28a由`L202–203`覆盖，Plate 28b已在图版目录`00_05_List_of_Plates:L81`覆盖。p.40的Plate 30组题及交叉指针由`07_CHP-7_sec_v_visual-transcription:L1`补录，Plate 30/31题注按既有图版目录去重；p.41 Plate 31题注同样由图版目录覆盖；p.42 Plate 32a由`07_CHP-7_sec_v:L39–40`迁入，OCR遗漏的32b由视觉转录`L3`补录。组题按版面导航处理，不推导研究主题或关系。其余页块与规范分节高度重合。第7章coverage 55条，47 reviewed/complete、8 excluded/complete，无queued或partial。未发现两份整章副本独有的实质正文、脚注或图版信息；本核对不替代全书语义交接验收。

## 第8–10章整章OCR范围核对（2026-10-07）

逐页比较`08_CHP-8.md`（47页块）、`09_CHP-9.md`（40页块）和`10_CHP-10.md`（64页块）。第8章低重合页为p.16–18、p.35–36、p.38：Plate 34、35a、38题名与 venue 对应`08_CHP-8_sec_ii:L41–46,L263–266`及视觉转录`08_CHP-8_sec_ii_plates_visual-transcription:L1`；Plate 35b与Plate 36组题及a/b题注由该视觉转录`L1,L3,L5,L7`覆盖。Plate 37a/b在规范段`L259–261`，c题注被页边裁断，完整题名只由图版目录锚定；Plate 39无独立印刷题注；Plate 40a由`L268–269`覆盖，40b被页边裁断，只保留图版目录的完整目录信息，不冒充本页可读文字。p.35–38页图此前已核对。第8章61条coverage全为complete（56 reviewed、5 excluded）。

第9章低重合页为p.7、p.9–10、p.28、p.30：Plate 41a/b、43、46、47和48分别由`09_CHP-9_intro_plates_visual-transcription:L1–2,L4,L8–11,L13–15`覆盖；Plate 44规范OCR段`09_CHP-9_intro:L74–75`与图版目录相同，按重复题注排除；Plate 48仅转录可辨的a/b题注，c/d不清楚的题注与铭文不从图像推断，目录项保持单独来源。第9章53条coverage全为complete（46 reviewed、7 excluded）。

第10章低重合页为p.6–7、p.9及p.42–45。Plate 49题注在`10_CHP-10_intro_plates_visual-transcription:L1–4`；Plate 50只补录编辑性组题`L6–7`，图像不作为独立题注；Plate 52题头及题注在`L12–15`。p.42–45的Plate 53a/b、54、55a/b、56分别在规范来源`10_CHP-10_sec_ii:L34–53,L55–56,L58–60,L62–70`中处理；图注倒置、混排或反向OCR均据`CHP-10.pdf`校读，并与图版目录候选对应。与第11章全章OCR重复的这些图版页另按重复扫描处理，见后续第11章范围核对。第10章75条coverage全为complete（73 reviewed、2 excluded）。上述三份整章副本均未发现规范来源之外的独有实质正文、脚注或题注；此核对不代替全书语义交接验收。

## 第11–12章整章OCR与重复扫描核对（2026-10-07）

用同一渲染参数逐页比较三份印本PDF：`CHP-11.pdf`物理页1–22与`CHP-10.pdf`物理页28–49逐页像素完全一致；`CHP-12.pdf`物理页1–15与`CHP-10.pdf`物理页50–64逐页像素完全一致。`11_CHP-11.md`的22个OCR页块与`10_CHP-10.md`对应22页在去格式文本上逐块匹配（22/22）。`12_CHP-12.md`页码标识存在OCR误识，但15个页块按顺序与`10_CHP-10_sec_ii.md`规范合并文本对应；词项多重集覆盖率均为100%，五词组覆盖最低0.978、均值0.9983。第12章页末把本章正文和注释并入同一OCR块，故按页面直接比较会产生假性低重合；其文字仍已由规范合并源段承载。第11章Plate 53–56重复页题注已在第10章的规范覆盖中处理。片段OCR覆盖表共44条（第11章27、第12章17），全部为`excluded/complete`；整章副本和重复扫描不重复计入规范段数。

## 第1、13–17章整章OCR范围核对（2026-10-07）

将`01_CHP-1.md`及`13_CHP-13.md`至`17_CHP-17.md`分别与本章规范分节逐页比对。页块筛查的唯一低重合例外为第13章p.59的反向Plate 59题注，已在规范段`13_CHP-13_intro_plates_visual-transcription:L9–11`完整转录；其余页块均与规范文本高度重合。第13章Plate 57–60的扫描页、目录题注与S2覆盖记录逐项对应；第14章Plate 61–64在规范来源段`14_CHP-14_intro:L148–166`中处理，并明确保留被裁断题注的边界，不补写不可见文字。第1、15、16、17章没有发现未映射的低重合页块。coverage记录均无queued或partial：第1章30条（27 reviewed、3 excluded），第13章25条（24、1），第14章19条（18、1），第15章20条（17、3），第16章8条（7、1），第17章13条（10、3）。至此17份整章OCR对照副本均完成范围核对，图版、脚注和重复段落均已映射到规范来源或保留明确排除理由；没有发现需新增S2内容的整章OCR独有实质材料。该范围核对不替代下述全书语义交接审计。

## 全书S2交接审计：第十章p.276脚注1版面与关系端点（2026-10-07）

重新查看`CHP-10.pdf`物理页1和规范OCR `10_CHP-10_intro.md:L3–13`。L3–L5为页码、章名和节标题；正文止于L12。L13的“Cole played a very important part…”实际印在页脚脚注1段内，是脚注1的续文，不是正文补充，也没有缺页。规范OCR将脚注1的前段另置于同一文件L492；两段共同构成印本脚注1。此前coverage及处理记录中将L13称为正文并认为扫描缺文的判断据此更正。将L13的两条statement改列为脚注1续文，链接到合并注释段`chp-10:10_CHP-10_intro:l491-634`的L492，并回链正文脚注标记1对应的`st-chp10-p276-cole-carriera-pastel-portraits`；Osti 1951 p.119保留为Haskell的引文定位，未将其当作独立核验。同步将coverage注释改为当前页图判断，并记录印本`part`及`Niccolò`与OCR字形差异；S0原文不改。

同一页此前未填端点的单一对象关系候选已按原文及提及跨度填写候选外键：Cole→Carriera、Cole→Dartmouth、Cole→Pellegrini、Manchester→Carlevarijs。原文将Manchester带两位画家赴英写在同一句；为保留各自关系端点，将其拆为Manchester→Pellegrini与Manchester→Marco Ricci两条候选陈述，保留共同原文证据和“一年后”的相对时间。脚注3仅为引文定位，没有独立查阅。以上均未写入S6正式关系。

审阅第十四章p.353后，将作品Flora的提及由断开的“l’empire de”与“Flore”合并为覆盖完整跨行法文标题的单一跨度。关于Brühl藏品被纳入画面的陈述补入明确主语Tiepolo；原文单数“the picture”没有指出两件委托作品中的哪一件，故作品宾语仍空，不能将两个图案分别配给作品或宅邸。

截至本次审计，全库有2,259条`relation_candidate=true`的statement：2,126条同时具有主客端点，87条仅有主语、35条仅有宾语、11条两端均空，共133条仍缺至少一个端点。缺项须逐项区分多对象陈述、概括性论断、来源未指名对象和确实漏映射，不能仅按计数补齐。表级严格审计仍为`s2_missing=[]`、`errors=[]`；该检查不替代端点语义审核。
