# 《赞助人与画家》全书语义处理（S2）当前结果

更新日期：2026-10-08。任务ID：`patrons-and-painters-full-book-s2`。**状态：S2交接审计进行中，尚未进入S3。**本页只记录当前范围、数据、未决项和下一步；历史逐项裁决见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)、[阶段结果索引](../../03-processing/patrons-and-painters-full-book-s2/results/stages.md)及各章结果。

## 范围与覆盖

S0登记79个规范来源文件、832段，涵盖书前材料、第1–17章、结论、附录、第二版后记、书目和索引；42段为派生视觉转录。第十一、十二章与第十章同版扫描产生的44段重复OCR已排除。书目按出版记录和引文定位处理，索引按候选定位材料处理，不作为正文断言。

| 当前S2覆盖状态 | 段数 |
|---|---:|
| reviewed / complete | 678 |
| 有理由排除 / complete | 154 |
| queued / partial | 0 |
| 合计 | 832 |

所有纳入处理的正文、注释、图版说明及书前/书后材料均已有S2处理记录。书目段已处理至L3–1306。纸本索引范围终审已完成：`CHP-22Index.pdf`共32页（p.443–474），规范索引94段均有coverage且迁移完成；19份Markdown与CSV的2,934行集合一致，2,934个CSV行号均有唯一候选索引ID并纳入逐页/栏映射。此前p.446发现并回补的四条为本次确认的纸本漏录；未发现其他未登记纸本词条。另将p.454印本“Fetti, Domenico”与F.csv#48的“Feti, Domenico”差异核清，cand-1033显示名已按印本校正，源文件未改写。p.460和p.462页码在页图中存在，PDF文本层漏识。全库脚注续页、正文回链和statement引用已专项检查：第七章p.186注1、第十三章p.333–334注1及第九章p.264–265注8的正文范围、目标注文页和正反链接已核正；嵌套脚注/续注pending键及打印页错配均为0。p.247印号不可见、p.270注7疑似错位、p.359注4无标记且重复注3等印本异常按证据保留，不强行回链。

## 当前数据与机械检查

当前表包含1,019个KU、11,497个候选、27,397条mentions及12,282条statement；索引候选2,934行。`python -X utf8 scripts/audit_tables.py --strict-stage --summary`通过，`s2_missing=[]`、`errors=[]`；两条既存第1章statement缺少的claim已补齐。关系候选2,433条，2,419条端点齐全，14条仍开放且保留待证。全库`footnote_pending`、`footnote_text_pending`、`cross_reference_text_pending`及statement失效引用均为0。同步闭合检查已通过：303 passed、2 subtests passed。

仍有两条既存enrichment `source_ref`警告：`enr-06678`、`enr-06937`无法从对应卡片source清单解析。机械检查不等于语义准确或实体召回完整；目前没有独立外部语义验收。

## 候选表面复核与当前游标

书前材料及第1–10章、第13–18章的候选表面提示已逐项裁决；第十一、十二章与第十章共用规范来源。第十六章7个reviewed段的11条提示中6条映射、5条不写；新增cand-11500至cand-11502、6条mentions和1条statement，另修订既有statement的候选关联与subject、更新cand-10598 detail。写后定位器剩余5条，与已裁决的不写项一致。逐项记录见[第十六章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-16.md)。

第十七章10个reviewed段的8条提示已逐项裁决；新增cand-11503至cand-11508、9条mentions，修正Joseph mention的候选映射，并更新竞赛题材statement。定位器剩余3条均为已裁决的不写项。第十八章2个reviewed段的2条提示也已核实为普通词义/候选错配，无表修改。第十九章12个reviewed段的17条提示已完成语义裁决：新增cand-11509至cand-11516及20条mentions，修正或扩展7条既有mention、核正statement候选关联；唯一残余提示`subject`为一般词义，明确不映射。第二版后记20个reviewed段的24条提示也已完成；新增2个候选和4条mentions，修订4条statements，写后剩余20条均与有依据的no-write裁决一致。详见[第十七章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-17.md)、[第十八章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-18.md)、[第十九章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-19.md)及[第二版后记结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-20.md)。

全书候选表面提示复核已推进至第二版后记并完成；定位器剩余的20条均为已逐项裁决的不写项。定位器只匹配已有候选词形，不证明实体召回完整，也不替代全书S2交接审计。

## 全书S2交接审计与下一步

全书S2交接审计仍在进行。已复核两条原标为`referent_status=unresolved`的statement：第十章p.316注4的“These paintings”回指本段cand-9678所代表的Nogari作品组；单幅照片与作品之间的对应仍未知。第十五章p.362的“This”回指前句的country-house architecture，后文将该住宅定位为S. Maria di Sala别墅；正文候选cand-10432与索引种子cand-1007留给S3做身份对齐。两条显式未决指代状态现均已改为有范围的上下文解析，但全书其余指代和限定语仍需终审。

### 指代记录

- `st-chp10-p316-n04-honour-showed-haskell-painting-photographs`：目标cand-9678；注释说明组级先行词已确定，未把照片逐张映射到作品。正文statement的旧“注4待规范链接”限定已清理，`cand-9918` detail同步修正。
- `st-chp15-p362-this-surpassed-venetian-collections-referent-unresolved`：主语锚定`cand-10432`，predicate现表述country-house architecture与威尼斯收藏的比较；新增mention `m-chp15-p362-0087`，来源段字符范围`2426:2430`。`candidate_identity_questions`记录cand-1007与cand-10432的S3比较，S2不合并。

### 六条端点未齐关系候选（交S3/S6）

| Statement | 来源锚点 | 未决内容 | 下游处理 |
|---|---|---|---|
| `st-chp7-p180-n4-pair-location` | 第7章p.180注4，L338 | 两幅画`cand-6773/6774`与Louvre、Detroit Institute of Arts `cand-4589/7072`是成对提及；注释引Nicolas Poussin pp.46、65，但没有逐幅指配。 | S3对齐已有端点；S6在来源可逐幅指配前不生成单幅地点边。 |
| `st-chp8-p207-n1-ferdinand-left-thirds-to-daughters` | 第8章p.207注1，L136 | `cand-0914`把画作的三份之一分别留给三名未具名女儿；未说明嫁给Giuliano Colonna `cand-7598`的是哪一女儿。 | 保留群体层断言；不为女儿造端点或分配份额。 |
| `st-chp8-p211-del-rosso-marriage-alliances` | 第8章p.211，L85 | del Rosso家族`cand-7489`与“best families”的婚姻联盟未列出对方家族或具体婚姻。 | 不补造对方；S6不生成具体婚姻边。 |
| `st-chp8-p238-note4-pictures-at-pisa-cabinet` | 第8章p.238注4，L446 | Pisa机构`cand-8048`所指图片可能是两幅风俗画`cand-0874/0887`，也可能包括前述讽刺画`cand-0885`；“are—or were in 1941”保留时间不确定，Casini pp.42–50未独立查阅。 | 保留注释statement及范围歧义；不作单幅地点边。 |
| `st-chp14-p353-bruhl-possessions-in-the-pictures` | 第14章p.353，L70–71 | 两个图像母题`cand-10293/10294`未指配给Brühl委托的`Maecenas` `cand-2597`或`Flora` `cand-2590`，也未指配到具体住宅。 | S3对齐现有候选；S6等待作品与母题的逐项证据。 |
| `st-chp20-p403-alazard-commissioned-franceschini-picture` | 第二版后记p.403，L111–113 | 作品`cand-6888`与画家`cand-1066`已识别；Colbert `cand-0800`、Abate Luigi Strozzi `cand-2528`是经手人，实际委托人未具名。 | 不把经手人提升为委托人；保留端点未决。 |

以上开放候选均无新近具名、可独立识别而缺候选的端点，故未创建`candidate-backlog.csv`；未新增S6正式关系。六条statement及候选映射构成当前关系问题的交接清单，不表示关系阶段已完成。

### 递归引用完整性

对全部statement嵌套字段和mentions的候选ID进行递归核对：78,288个候选ID引用、10,114个不同候选均可解析；17,895个类型化statement引用全部存在；17,872个段落引用涉及591个不同segment，均可解析，`#L`锚点越界为0。新增的S3身份问题当前共16条statement、25个问题、20个不同候选ID，引用均存在。`candidate-backlog.csv`当前不存在；无新具名且可独立识别的缺失端点。其余全书断言限定语与语义风险仍待终审，S2尚未交接。

### 引用锚点、书目匹配与候选类型待决

对12,263条statement按其自身`source_file`及`source_line_start/end`复核：源文件缺失、行范围越界、引文不在指定范围内均为0。7,246条引文与行段完全相同，5,013条引文位于所指行段内，4条需忽略换行空白后匹配。另有175条第一章statement沿用`01_CHP-1.md`整章来源路径，而`segment_id`指向规范分节来源；这175条引文和行号均可在各自`source_file`中复现，保留为旧S2定位，不另计来源段或覆盖。

第3章p.81注释`st-chp3-seciv-l48-56-enggass-citation`现在链接至本书书目`st-chp21-bib-l420-459-entry-17`，两者均指现有候选`cand-5243`。内部书目身份已确定，`bibliographic_identity_pending=false`；论文未独立查阅，不能据此声称已核验论文内容。

第8章p.224注释中的“Bologna (Plate 209)”已通过本书内部材料识别为Ferdinando Bologna的《Francesco Solimena》（Napoli, 1958）：书目p.416 entry 7与作者、题名、年份一致；本书自身图版目录将该画列为Plate 33a，因此209是被引书的图版号。正文候选`cand-7759`与书目候选`cand-7348`已互链，但保留为两个S2候选并新增S3身份对齐问题；被引书未独立查阅，replica的具体实物身份仍未核验。

第8章p.224注释仍有`collection_type_pending=true`：`cand-7761`为Scholz-Forni art collection，现行taxonomy没有collection类型，按规则保留空类型，不改成institution、archive或work。

全候选表有450行`suggested_type`为空（407条open、43条excluded；来源中378条为body-mention、72条为index seed）。该集合属于S3类型/身份判定输入；严格结构审计不证明空类型均已语义解决。需在S3按证据给出same/new/conflict/excluded/undecided决定；S2不提前登记KU。

S2交接前不推进S3–S6、知识发现或页面工作。

## 书内引用与跨页续接残余收口（2026-10-08）

p.251注1“See p.268, note 5”已链接到`st-chp9-p268-n05`及其来源段L89；书目L66的Andrés指引链接到L578条目statement，L638的Jaffé指引链接到L1276–1277条目statement。三者只闭合书内引用路径；候选身份仍交S3，引用出版物未声称独立查阅。第3章p.74–75跨页句现以statement ID互链，去除与complete coverage不一致的旧partial迁移状态，并澄清“another full generation”的修饰范围。

按当前coverage坐标重新核对7,562条正文候选来源引用，全部落在reviewed行段，无悬空或越界。上述结构修改后严格阶段审计仍为`s2_missing=[]`、`errors=[]`。

## 第十章p.314–324脚注状态措辞复核（2026-10-08）

在完整的注释coverage L274–349中，p.314–324有26条正文限定语仍显示脚注待迁移/待链接；现已按实际注文L288–326及其statement外键修正。25条沿用正文已有`footnote_statement_ids`，另1条使用嵌套`citation_statement_ids`，共41个目标ID全部存在。只校正状态表述；引文未被视为独立查阅，断言、候选、mentions、statement数量与关系判断未变。全书S2交接审计仍继续。

## 第十章p.281–297脚注状态限定语复核（2026-10-08）

p.281–297的42条正文限定语已按原书注文与当前coverage修正。33条已有注文statement ID，共79个且均解析；另外9条对应纯书目/页码定位注，不含独立注文断言。注释coverage `chp-10:10_CHP-10_intro:l491-634` 为reviewed/complete，42条正文的`footnote_text_pending`均为false。只更新限定语中的过时迁移状态，未改事实、候选、mentions、statement ID、链接字段或正式关系；原引文未独立查阅、未决身份和作品范围仍明确保留。

严格阶段审计通过（1,019 KU、11,497 candidates、27,396 mentions、12,263 statements、832 segments，`s2_missing=[]`、`errors=[]`）；结构闭合健康130/130。审计器仍报告既有`enr-06678`、`enr-06937`两条enrichment `source_ref`告警及语义审查提示。全书S2交接仍未完成；下一步核对第十章p.298–313及余下注文状态限定，再继续全书指代、证据限定和关系候选终审。


## 第十章p.302–325状态与链接复核（2026-10-08）

修正32条与已完成注文/书目/书内指引不一致的限定语；补齐p.303、p.315、p.321正文与注文statement双向链接，并将p.318注4归到印本实际标记的Conti陈述。书内书目确认Antonio Conti《Prose e poesie》卷二（1756），候选仍保持分立交S3；p.325第15章指引只作为书内引用。保留p.299身份语境未决、p.310–311候选待S3、p.304注5年份差异、原引材料未独立查阅等限制。

严格阶段审计通过：1,019 KU、11,497 candidates、27,396 mentions、12,263 statements、832 segments，`s2_missing=[]`、`errors=[]`；既有两条enrichment `source_ref`告警和语义审查提示未解决。结构闭合130/130。此批仅核验结构与已定位的局部语义问题，不构成全书S2交接；后续继续第十章p.326以后及全书剩余指代、证据限定和关系候选终审。

## 第十章p.326–331交接复核（2026-10-08）

p.326注1的首种小册子题名补入mention；第二、第三种题名跨度扩至全名，原文OCR／换行保留。p.330注1现链接至已处理的附录六p.394–395及14条相关statement，并回链正文；附录文本为书内转引，档案原件仍未独立查阅。另将10条明确关系statement纳入关系候选：官方画家、当选职务、两项委托、两项友谊、Memmo任职、名片创作、版画题铭赞誉及诗作影响；没有创建S6正式关系。

本次严格阶段审计通过：1,019 KU、11,497 candidates、27,397 mentions、12,263 statements、832 segments；`s2_missing=[]`、`errors=[]`。关系候选2,341条，2,335条两端齐全，6条待证；既有两条enrichment `source_ref`告警和语义审查提示仍在。覆盖状态不等于语义交接完成。下一步继续对其余全书来源段执行断言限定、指代、书内引用和关系候选的语义终审，并专门核对本章其余脚注／图版与尾注残余；S2交接前不进入S3–S6。


## 第二章亲属、友谊与家族关系候选补录（2026-10-08）

补齐7条明确亲属/友谊statement的关系候选标记；将p.38 Sacchetti兄弟与父亲信息拆成兄弟关系和两条逐人父子映射，并将两兄弟与Maffeo的友谊分别按候选端点记录。另补标p.38父亲迁居/社群领导、宅邸与礼拜堂、别墅与画廊三条关系候选。共新增15条关系候选输入；不新增正式关系。cand-0209与cand-0213同名身份问题记录交S3。严格审计通过：12,266 statements、2,356条关系候选、2,350条标量端点齐全、6条待证；`s2_missing=[]`、`errors=[]`。同段p.38的委托、引介、创作及交往陈述仍待逐项审查，全书S2交接未完成。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)。

## 第二章p.38委托、创作与交往关系补录（2026-10-08）

为p.38壁画委托/分配、艺术家引介与赞助圈、Pietro摹制委托、Marino影响Poussin、诗作与评价、Marcello—Marino友谊、赠歌题献及原文限定性推断补上关系候选标记。把赠歌与共同兴趣拆为两项statement，新增题献关系映射及Marcello—Marino友谊映射；没有新增S6正式关系。严格审计通过：12,268 statements、2,368条关系候选、2,362条端点齐全、6条待证；`s2_missing=[]`、`errors=[]`。p.38剩余活动/端点边界和全书S2交接仍待复核。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)。

## 第二章p.38遗漏关系端点与复合陈述拆分（2026-10-08）

p.38明确的付款、壁画委托/分配、艺术家引介/赞助圈、摹本与未具名摹手、风景创作/新人搜寻、旅行/学者交往、赠歌/共同兴趣、诗作与评价、Poussin赴意影响、兄弟家族关系、群体接纳和Urban VIII语境现已按statement端点整理。Bernini付款与Ciampelli委托的同日并列保留为时间陈述；不把它提升为正式关系。未具名目标保持开放，摹手是否为Pietro留待S3。严格审计通过：12,274 statements、2,377条关系候选、2,369条标量端点齐全、8条开放；`s2_missing=[]`、`errors=[]`。以上是局部回补，全书S2关系与语义交接仍未完成。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)。

第二章另补标4条枢机任命、3条家族资产/领地转让、1条纪念碑提案和1条婚配选择候选关系；保留提议未执行、选作新娘不等于已婚、集体买方/卖方未具体化等限定。当前严格审计为12,274 statements、2,386条关系候选、2,378条两端齐全、8条开放；`s2_missing=[]`、`errors=[]`。全书S2语义交接仍未完成。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)。

## 第二章p.39关系候选、脚注回链与提及修订（2026-10-08）

复核p.39（`02_CHP-2_sec_ii:l80-89`）后补标并拆分关系断言：本段现有27条关系候选，其中5条因目标、职务或群体端点未明确而保持开放。补录风格比较短语的精确mention，修正一条泛指所有艺术家的断言误连Pietro候选，并将p.39脚注1–4与L176–179注释statement双向链接；p.38同号脚注仍指向L172–175。保留跨段购藏句，不生成正式关系边。严格阶段审计：12,275 statements、27,398 mentions、2,413条关系候选、2,400条端点齐全、13条开放；`s2_missing=[]`、`errors=[]`。全书S2语义交接仍未完成。详见[章节结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-02.md)及[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)。

## 第二章p.40断言拆分与关系候选复核（2026-10-08）

对`l91-104`正文及脚注L180–184复核后，将23条首轮statement拆整为30条；删除1条把“his friends”错映射到诗歌候选的mention，当前64条mention。补标12条正文关系候选，其中未具名朋友对象保持开放；脚注L183中Urban VIII对Galileo的未详处置另列候选。脚注1–5与正文双向链接，注1回链3条断言。L104肖像句与L119续句保持互链。严格审计：12,282 statements、27,397 mentions、2,426条关系候选、2,412条端点齐全、14条开放；`s2_missing=[]`、`errors=[]`。本段未新增KU或正式关系边。其后的Plate 5题注现已另行复核并加入2条S2关系候选；当前下一段为Plate 8题注`chp-2:02_CHP-2_sec_ii:l115-116`，全书S2交接继续。详见[章节结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-02.md)及[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)。

## 第二章Plate 5题注（2026-10-08）

题注归属与描绘两条statement现列为S2关系候选；“Bernini; Cardinal Borghese”与同页页题合读，将人物指向已接收的Cardinal Scipione Borghese候选，但作品版本仍未定。候选作品不并入正文胸像组，不据题注断言外部鉴定。严格审计无错误；全书关系候选2,428条、2,414条端点齐全、14条开放。详见[章节结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-02.md)及[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)。

## 第二章Plate 7题注（2026-10-08）

将题注“Domenichino: Hunt of Diana”记录为作品—作者的S2关系候选；沿用候选及两条精确mentions，保留题注归属不等于独立鉴定的限定。严格表审计无错误；全书关系候选2,429条、2,415条端点齐全、14条开放。当前下一段为Plate 8题注`chp-2:02_CHP-2_sec_ii:l115-116`。详见[章节结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-02.md)及[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)。

## 第二章Plate 8题注及书前目录（2026-10-08）

正文题注与书前目录各有两条caption关系statement，分别记录礼拜堂位置及Castelli设计署名；复用Barberini Chapel、S. Andrea della Valle、Castelli候选，四条均列为关系候选，保留caption attribution边界，不写正式边。严格表审计无错误；全书关系候选2,433条、2,419条端点齐全、14条开放。下一段为`chp-2:02_CHP-2_sec_ii:l118-125`。详见[章节结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-02.md)及[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)。


## 第二章p.41断言拆分、关系候选与脚注链接（2026-10-08）

完成第二章正文 l118-125（印刷p.41／PDF物理第26页）的语义复核，并回核其注释L185–190。正文由29条statement细化为35条，新增6条断言、1个“papal land and sea forces”机构候选和1条精确mention；补标28条关系候选，其中3条因比较性或一般性纪念物没有具体作品端点而开放。脚注1–6逐项与正文双向连接，注6涉及的两幅Claude Seaports保持机构对应未定。S2表中不写正式关系。

写后严格审计：1,019 KU、11,498 candidates、27,398 mentions、12,288 statements、832 segments；关系候选2,462条、端点齐全2,445条、开放17条；s2_missing=[]、errors=[]。两条既存enrichment来源定位警告和语义审查提示仍未解决。下一源段 chp-2:02_CHP-2_sec_ii:l127-139 已有早期迁移稿，现继续审查其语义和关系候选，不重复计数或另建来源。
