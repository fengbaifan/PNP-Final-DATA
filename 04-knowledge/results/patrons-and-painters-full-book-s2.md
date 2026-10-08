# 《赞助人与画家》全书语义处理（S2）当前结果

更新日期：2026-10-08。任务ID：`patrons-and-painters-full-book-s2`。**状态：处理中，尚未达到S3交接条件。**本文件只保留当前状态与后续顺序；逐页判断和迁移依据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)与[逐段结果](../../03-processing/patrons-and-painters-full-book-s2/results/stages.md)。

## 范围与覆盖

S0纳入79个规范来源文件、832段，其中42段为派生视觉转录；另将CHP-11/12与CHP-10同版扫描对应的44段重复OCR标为excluded，不重复处理。规范来源文本覆盖书前材料、第1–17章正文/脚注/图版、第18章结论、附录、第二版后记、书目与索引。

p.446索引种子漏项已核实并回补：印本有Bentveugels、Bergamo主词头，以及Santa Maria Maggiore、S. Paolo d’Argan两个Bergamo地点子项，原B.csv和B.md均缺。四行已追加为B.csv#324–327、登记为cand-11459–11462，并在B.md末尾新增独立补录表；既有正文候选与提及保持独立，身份留待S3。已对照19组A–Z索引Markdown与CSV，现均为2,934行并逐项对应；A.csv保留旧Windows-1252编码及四处OCR重音字形损坏，印本、A.md及对应候选（cand-0024、0045、0093、0104）已核正。索引PDF页、段与候选的逐页处理记录见过程文件；书后五个平行OCR副本也已比对。17个整章OCR校勘副本的范围核对均已完成，重复扫描和独有图版内容均已映射到规范来源或排除理由；全书语义交接审计仍未完成。

| S2状态 | 段数 |
|---|---:|
| reviewed / complete | 678 |
| 有理由排除 | 154 |
| queued | 0 |
| reviewed / partial | 0 |
| 合计 | 832 |

索引p.474页标与两栏已处理，当前无queued段；书目段已全部处理，L1301结构性“Footnotes”标签不作为条目内容。已按书序审读和登记书目前置选择说明L3–45及条目段L47–85、L87–127、L129–163、L165–205、L207–241、L243–293、L295–334、L336–374、L376–418、L420–459、L461–496、L498–536、L538–575、L577–614、L616–656、L658–699、L701–754、L756–806、L808–844、L846–881、L883–926、L928–983、L985–1020和L1022–1057、L1059–1100、L1102–1139、L1141–1177、L1179–1218、L1220–1259、L1261–1299。书目末尾七处错位OCR已链接到既有书目statement，不重复登记出版物；当前待补链接包括L616–656指向L1276的Jaffé目标页图复核；L658–699的Levey 1955页码差异与Lavagnino未标卷次页码、L701–754与L756–806的短引/版本身份问题及L846–881的Moschini/Meschini旧引文匹配均留待S3。L820作者指引的L861目标已核实，Molinier身份仍未确定。L883–926的Nuti/Pasquali、Ottonelli两版及Palomino定位保留S3比较入口；L928–983的Pascoli、Pastor、Peiresc、Pellegrini和Pollak卷次／版本定位仍待S3比较；L985–1020登记29条出版物记录，复用24个archive候选并补全其中19个，新建5个；p.405两条Puppi引文按页码范围映射到不同书目条目。L1022–1057登记25条出版物并复用22个archive候选，新建3个；L1049的Rinehart “See also”指向已处理的L596–597 Haskell/Rinehart条目；L1059–1100登记26条出版物，复用23个既有出版物archive候选并新增3个；p.403的Rosenberg引文补全至相符书目项，p.404 Rudolph两部分与独立1973年引文关系仍待S3。L1102–1139登记25条出版物，21条复用已有archive候选、4条新建；L1141–1177登记30条书目记录，复用25个archive候选、新增5个；L1179–1218登记28条书目记录，复用20个archive候选并新增8个；L1220–1259登记28条书目记录，补全21个archive候选、新增4个；L1261–1299登记23条书目记录，补完跨页Wilhelm条目并新增4个archive候选。完成页图校读和OCR订正，跨章短引、作者映射及Wynne-Rosenberg地点差异保留S3比较。Stuffmann页码差异已记过程，保留本书印字。页图校读及OCR补项依据见逐段过程记录；书目和索引按材料性质处理，不当作正文断言。

当前S2表有11,467个候选、27,168条提及和12,255条statement。第十四章p.353将Flora标题两个断开的提及合并为一条完整跨度（净减1条mention）；第十章p.276、十五章及第八至十九章交接审计按原文端点拆分复合statement。


## 当前游标

第二版后记正文p.396–410、Plate 65–68及脚注已完成；书目段L3–1306已全部处理。p.402–403跨页句和委托人空缺已复核，第二十章63条过时的脚注排队/待审限定语已按注释覆盖与回链状态更正；未独立查阅的引文及未决书目身份仍保留原限定。Levey、Lavagnino、短引与版本身份等书目比较问题保留给S3，具体清单见“范围与覆盖”。

索引已按书序处理至p.474，94段均完成覆盖判断；p.446纸本索引漏录的4行已补入，35个开放候选中34个完成分类，cand-2860沿用既有person类型。17份整章OCR副本均完成范围核对，未发现规范来源之外的实质材料。书目与索引的逐项S2处理和未决比较项见“范围与覆盖”及过程记录。

全书S2关系候选端点交接审计仍在进行。已完成第7–10章及第13–20章相关开放项的逐项处理；具体段、证据与遗留理由见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)。第二十章Alazard/Franceschini作品记录已核对p.402–403页图、p.403脚注1、Plate 66图注及第七章p.187同一作品的委托记述；原文仍未明确委托者，主语保持空值。第七章p.180注4未说明两件Poussin作品与Louvre、Detroit两馆的逐件配对，仍保留开放项；其3条正文脚注限定语已改为与已完成注释状态一致。第八章p.238注4现已回链到标记所在句的两条正文statement，但“这些图画”的逐件指代仍不确定；第八章3条开放关系候选经原文复核后继续按证据理由保留。第十章p.279–280以及p.300–311已依据完整注释段修正脚注待处理措辞，保留引文和档案未独立查阅的限定；p.300注2另回链到p.301 Goldoni题献续句。全库2,327条关系候选中2,321条端点齐全、6条仍开放；未闭合项按章为第7章1、第8章3、第14章1、第20章1。第十四章p.353唯一开放端点已对照页图及注1复核；原文未将Brühl两处母题与Maecenas/Flora逐项对应，故继续保留空object端点，不作为遗漏。S2尚未达到S3交接条件。

第七章已审47段上的40条候选表面提示完成逐项裁决：17条补为精确mentions，23条因泛称、语法义或索引错配不写入；新增cand-11486类型待定收藏、cand-11487 Le Brun设计图稿组及cand-11488 Chigi 1664年访巴黎事件。11条statement补入候选提及链接；另将Shaftesbury“English patronage”statement对象由England地理候选改为English patronage术语。p.180注4的两画与两馆配对仍开放。写后定位器剩23条且与no-write集合完全一致。严格阶段审计确认当前11,467 candidates、27,168 mentions、12,255 statements，`s2_missing=[]`、`errors=[]`。下一章第八章有56个reviewed段、112条提示，仍待逐条语义裁决。

第十章p.278注1–6已完成源迁移，本次清除6条正文限定语和覆盖备注中残留的待处理措辞。注1–3、5–6保留为引用定位，注4保留未具名单件Amigoni作品群的1716年日期陈述；被引页未独立查阅，Manchester作者身份留待S3。全书S2脚注状态与回链核对及交接审计仍在进行。

第一章印刷p.19（CHP-1.pdf物理页18）脚注1–6已复核并回链：注1–3对应轶事/Ghezzi陈述，注4对应荣衔概述，注5–6对应Lauri/Passeri段；注4新增Frederick III→Gentile Bellini、Charles V→Titian两条带限定的S2关系候选，注6只保留Haskell对Cerquozzi/Passeri p.285的归属。六处引文定位现映射至archive候选，被引页未独立查阅。正文OCR尾部误带的注1、2全文已从body statement移除，正文L763–795与注释L796–806不再重叠；注2印本罗马数字I与OCR小写l差异仅记于S2，S0不改。以本轮前备份逐项核验，候选外键与回链有效；全库当前27,011条提及、12,254条statement，2,327条关系候选中2,321条端点完整、6条仍开放。

第二章印刷p.40（CHP-2.pdf物理页21）注1–5已连接到现有注释statement，六条正文陈述的待处理状态已清除。注3两项有明确端点的关系列为S2候选，未写入正式关系；Haskell将巴黎监视与占星联系起来的判断仍单独保留为作者推论。补入D. P. Walker人物提及，原出版物citation mention保留；被引作品和页码未独立查阅。受控迁移及表级核验见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)。

第七章印刷p.188–193的脚注旧状态已复核：p.188注1–2、p.189注1–6、p.193注1与注3完成正文回链；12条旧`footnote_pending`标记清除，p.189 Maratta整句后半statement及p.193 Vecchia复合句两条statement均纳入正确链接。p.270注7也已复查：印本锚点与Dominican注文内容错位属原书页内状态，维持5条`mismatched`记录且不改数据（no_delta）。被引材料未独立阅读。第十三章p.332–338及第十六章p.376脚注状态已复核。下一步转为全书S2交接总审计。

第十章p.306注1的页内锚点已纠正：印本标号跟在Visentini绘稿句后，结构化回链落到该句；前面三条购藏／收藏判断不再继承整段引句上的注号或旧待处理状态。Blunt与Croft-Murray所引页未独立查阅；严格阶段审计通过。下一待核旧脚注状态为第十三章p.332–338，随后处理第十六章p.376，再作全书状态扫描和S2总交接审计。

第十三章p.332–338的12条有效脚注现已链接到既有note statements；p.332版权效果句、p.337 Caime句、p.338 Goldoni插图举例句的3个继承标号已按印本位置清除。p.334印本注5与OCR注6的差异保留为既有校正。严格阶段审计通过；第十六章p.376注3跨页续文已闭合；全库pending标记与失效statement引用均为0。第九章p.270注7错位和第十四章p.359无正文标号的重复注4保留为已核实例外。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)。

## 第十六章p.376注3跨页续文与全库脚注回链扫描（2026-10-08）

印刷p.376注3从L84开始，续文位于p.377 L60–64；正文L46的脚注回链现已闭合，续文仍由8条既有statement承载。全库扫描确认`footnote_pending`、`footnote_text_pending`待处理标记为0，指向不存在statement的注释/正文回链为0；递归扫描statement表中的嵌套statement ID也无悬空目标。另修复第四章p.94注2的旧`citation_body_statement_id`，现指向Giustiniani收藏statement；并修正第八章p.239注1的3条旧目标ID，现均指向第八章p.238 L333–334关于Crespi佛罗伦萨停留的现有statement。严格阶段审计通过，统计行数未改变。

第九章p.270注7的5条错位状态继续保留：印本标号在Gesuati筹资句后，注文讨论Dominicans。第十四章p.359注4在正文L127–137找不到标号，且纸本注4与注3重复，保留`orphan_unresolved`及既有异常说明；p.360注4则单独对应Leslie引文。上述异常均不作为强制回链项。脚注状态收口不代表全书S2语义交接审计完成。

## 当前验证

`python -X utf8 scripts/audit_tables.py --strict-stage`：`s2_missing=[]`、`errors=[]`；全库1,019个KU、11,467个候选、2,934个索引候选行、832段、27,168条提及和12,255条statement。当前覆盖为678 complete、154有理由排除、0 queued、0 partial。2,328条关系候选中2,322条端点齐全、6条仍开放（第7章1、第8章3、第14章1、第20章1）；全库脚注statement引用专项检查未发现失效引用。审计仍提示两条既存enrichment来源引用无法从卡片source清单解析（`enr-06678`、`enr-06937`）；结构闭合不代表实体召回率、准确率或语义质量已独立验收。

第十九章候选表面扫描覆盖12个已审段，仍只提示一处`modello`词面；该词位于p.389且已判为异义。第20章候选表面扫描覆盖19个已审段，未覆盖跨度为0；此类启发式扫描只提示已登记名称，不能证明召回率或语义准确性。

第一轮全书候选表面扫描覆盖678个已审段，产生4,316个启发式提示；其中193条经筛选人工裁决，147条按原跨度映射，9条错配提示改用准确跨度生成12条mentions，37条不写入；另核实子跨度并共新增159条mentions。该轮其余提示没有系统审阅；扫描数不构成召回率验收。过程与受控脚本见[记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)。

随后在前批写入后重跑定位器：678个已审段产生4,156处提示。按来源计，书前16；第1–10章64、75、40、54、69、23、40、112、99、117；第13–17章33、24、16、11、8；结论2、附录17、第二版后记24、书目7、索引3,305。第11、12章与第10章共用合订来源，提示归在chp-10。该数包含重复出现的已裁决通用词提示，也会随新增mention与嵌套跨度遮盖而变化，不能视作剩余遗漏数。

本轮逐项核对书前16条，新增2条mentions（`VENICE`目录地点标题、第二版导言引文中的`renaissance`术语），14条泛词或错配索引提示不写入；写后定向复扫书前提示为14条，均已裁决。随后完成第一章64处候选表面提示逐项裁决，新增27条mentions、37条拒绝映射；写后第一章定向扫描剩余37条，均与拒绝映射项一致。全库严格阶段审计为1,019 KU、27,040 mentions、12,254 statements，`s2_missing=[]`、`errors=[]`。详细跨度、理由、来源定位和恢复记录见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)。其他章节、书目和索引提示仍待系统处理，全书S2尚未交接。

第二章当前已审64段上的75条候选表面提示完成逐项裁决：40条有据映射、35条不映射；新增40条mentions，另补5个类型待定的来源集合候选，修正2条Scipione集合提及及相关statement对象，并把Casino Rospigliosi脚注的所有权判断单独登记为1条S2关系候选。写后定位器的34条提示均与裁决中的泛词/修饰语/错配项一致；35条拒绝项中，“Italian art”因与采纳的“art patrons”跨度重叠而被扫描器遮盖。严格阶段审计与同步闭合通过，完整裁决及恢复信息见过程记录。提示数不是遗漏数或语义验收。

第三章已审42段上的40条候选表面提示完成逐项裁决：14条准确映射并新增14条mentions，26条按泛称或普通用法不写入；写后定位器剩余26条，与拒绝映射集合完全一致。未新增候选或statement。严格阶段审计通过，全库27,094条mentions；下一章第四章当前提示54条，分布于37个已审段。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)。提示数不代表遗漏数或语义验收。

第四章已审37段上的54条候选表面提示完成逐项裁决：23条准确映射并新增23条mentions，31条按泛称或普通话题不写入；写后定位器剩余31条，与no-write集合完全一致。复用Fondo Orsini、Cassiano收藏、Roman antiquities图稿组、St Romualdo、Altieri palace等已有候选，未新增候选或statement；三项collection候选保持类型待定。严格阶段审计通过，当前全库27,117条mentions。第五章提示复核结果见下文。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)。提示数不代表遗漏数或语义验收。

第五章已审35段上的69条提示完成逐项裁决：25条有据映射、44条按泛称/普通用法/索引错配不写入；新增7个候选、26条mentions，并为10条既有statement补充候选链接。写后定位器剩余44条，逐项吻合no-write裁决。完成时全库1,019 KU、11,464 candidates、27,143 mentions、12,255 statements；严格阶段审计`s2_missing=[]`、`errors=[]`，同步闭合结构健康130/130。两条既存enrichment source_ref警告不变。详细依据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)；提示数不是遗漏数或语义验收。

第六章28个已审段上的23条提示完成逐项裁决：8条映射到已有Rome、Antonio degli Effetti collection、Queen Christina picture gallery、Foreign travellers、Renaissance及Ottoboni theatre候选，新增8条mentions；15条按普通类别、比喻或索引错配不写入，未新增候选。写后定位器剩余15条，与计划中的no-write跨度完全一致。修正p.164注3关联statement中已过时的`footnote pending`限定，并补齐p.156注2收藏候选与p.164注3 theatre候选的statement提及链接。严格阶段审计确认`s2_missing=[]`、`errors=[]`，当时全库1,019 KU、11,464 candidates、27,151 mentions、12,255 statements；两条既存enrichment来源引用警告仍在。过程、逐段裁决及恢复副本见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)。

第七章47个已审段上的40条提示完成逐项裁决：17条映射并新增17条mentions，23条按具体词义或索引候选错配不写入；新增3个候选，其中Cardinal Aldobrandini收藏保留类型待定，Le Brun为Guidi Versailles雕塑组提供的图稿组归work，Cardinal Chigi 1664年访巴黎归event且参与者身份未定。Rome/意大利艺术、Louvre、Mazarin palace、Rosa的Battle、Del Carpio收藏、Guidi Prudence/Justice图稿和Liechtenstein Prince均复用当前候选。将“English patronage”statement的object由England place修正为cand-0969 term；其他11条statement只补充相关candidate提及，不更改relation表或未决端点。写后定位器剩余23条，与no-write跨度完全一致。严格阶段审计通过；当前全库1,019 KU、11,467 candidates、27,168 mentions、12,255 statements，`s2_missing=[]`、`errors=[]`。下一步按书序核对第八章：56个reviewed段上112条提示。详细裁决及恢复信息见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)与[第七章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-07.md)。

## 后续工作顺序

1. **继续全书S2候选召回审查。** 书前16处及第一至七章64、75、40、54、69、23、40处提示均已逐项裁决；对应写后提示保留14、37、34、26、31、44、15、23处已裁定的未映射项。下一步按书序处理第八章当前112处提示，再继续其余章节、结论、附录、后记、书目和索引；提示数不是遗漏数，不按字符串批量写入。
2. **完成全书S2总交接审计。** 逐项核对规范来源与排除副本、正文/脚注/图版覆盖及续注回链、具名对象和候选外键、statement锚点、限定语和关系端点；复核六条有理由保留的开放关系端点，并作有范围说明的语义抽样。机械覆盖通过不替代语义验收。S2有充分交接依据后再启动S3；此前不推进S3–S6、知识发现或页面工作。
3. **S3身份对齐。** 当前alignment有335条：185 same、146 undecided、4 excluded；待S2交接后再对届时全部候选裁决same/new/conflict/excluded/undecided，只处理身份并记录证据。
4. **S4 KU登记。** 当前manifest有1,019个KU。按S3结果创建或复用KU，以`ku-manifest.csv`作为唯一计数入口，并核对遗留`accepted.yml`与卡片元数据的对应关系。
5. **S5定向补足。** 当前`enrichment.jsonl`有10,149行，其中1,501行标为unverified；先逐项确认实际缺口与来源链，再按实体类型补明确必需字段。不要把unverified数量直接当作错误数。
6. **S6关系收口。** 当前`relations.csv`有1,227条（1,225 formal、2 pending），尚不能代表全书关系完整。结合S2 statements及人物作品、履历和关系说明逐项核证端点、方向、语境、时间/版本和证据。S5/S6新增端点按pipeline进入backlog；目前`candidate-backlog.csv`尚不存在，进入该阶段前需建立并按规则维护。
7. **S7重建并验证数据集。** 现有`release/v0.2-draft/`验证报告仍是旧快照，与当前表规模不一致；S0–S6稳定后应从规范表重新导出。发布前处理引文/源文片段权利、第三方复用条款、代码授权、稳定标识及最终引用；作者字段按用户决定暂留空值。
8. **再做系统收尾。** 核对第一章、章前结果文件中的当前汇总数字与规范表一致；逐项检查脚本、备份和临时图像的调用/恢复价值，再处理确认已过时的材料，保留恢复证据。

第二部分Topic→Theme→Dimension→Domain知识发现与页面呈现须用户明确启动。论文工作不属于本路线图范围。
