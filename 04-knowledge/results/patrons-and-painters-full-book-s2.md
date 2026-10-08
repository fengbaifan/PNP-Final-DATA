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

当前表包含1,019个KU、11,498个候选、27,401条mentions及12,310条statement；索引候选2,934行。严格阶段审计通过，s2_missing=[]、errors=[]；两条既存第1章statement缺少的claim已补齐。S2关系候选statement 2,530条，2,509条端点齐全，21条仍开放且保留待证。全库footnote_pending、footnote_text_pending、cross_reference_text_pending及statement失效引用均为0。同步闭合检查已通过：303 passed、2 subtests passed。

仍有两条既存enrichment `source_ref`警告：`enr-06678`、`enr-06937`无法从对应卡片source清单解析。机械检查不等于语义准确或实体召回完整；目前没有独立外部语义验收。

## 候选表面复核与当前游标

书前材料及第1–10章、第13–18章的候选表面提示已逐项裁决；第十一、十二章与第十章共用规范来源。第十六章7个reviewed段的11条提示中6条映射、5条不写；新增cand-11500至cand-11502、6条mentions和1条statement，另修订既有statement的候选关联与subject、更新cand-10598 detail。写后定位器剩余5条，与已裁决的不写项一致。逐项记录见[第十六章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-16.md)。

第十七章10个reviewed段的8条提示已逐项裁决；新增cand-11503至cand-11508、9条mentions，修正Joseph mention的候选映射，并更新竞赛题材statement。定位器剩余3条均为已裁决的不写项。第十八章2个reviewed段的2条提示也已核实为普通词义/候选错配，无表修改。第十九章12个reviewed段的17条提示已完成语义裁决：新增cand-11509至cand-11516及20条mentions，修正或扩展7条既有mention、核正statement候选关联；唯一残余提示`subject`为一般词义，明确不映射。第二版后记20个reviewed段的24条提示也已完成；新增2个候选和4条mentions，修订4条statements，写后剩余20条均与有依据的no-write裁决一致。详见[第十七章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-17.md)、[第十八章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-18.md)、[第十九章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-19.md)及[第二版后记结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-20.md)。

全书候选表面提示复核已推进至第二版后记并完成；定位器剩余的20条均为已逐项裁决的不写项。定位器只匹配已有候选词形，不证明实体召回完整，也不替代全书S2交接审计。

## 全书S2交接审计与下一步

全书S2交接审计仍在进行。已复核两条原标为`referent_status=unresolved`的statement：第十章p.316注4的“These paintings”回指本段cand-9678所代表的Nogari作品组；单幅照片与作品之间的对应仍未知。第十五章p.362的“This”回指前句的country-house architecture，后文将该住宅定位为S. Maria di Sala别墅；正文候选cand-10432与索引种子cand-1007留给S3做身份对齐。两条显式未决指代状态现均已改为有范围的上下文解析，但全书其余指代和限定语仍需终审。第二章后置注释L147–193本轮完成语义复核：已修复113条正文—注释反链，拆分1633年avviso的制作、委托和报酬主张，厘清p.33与p.60挂毯候选之间的交叉引用但不合并身份；p.40脚注、第1章脚注及L193通往`sec_iv:l3-4`的引用均已对齐。该段现有85条statement、93条mention及16条关系候选；所有关系仍处S2候选状态。

### 指代记录

- `st-chp10-p316-n04-honour-showed-haskell-painting-photographs`：目标cand-9678；注释说明组级先行词已确定，未把照片逐张映射到作品。正文statement的旧“注4待规范链接”限定已清理，`cand-9918` detail同步修正。
- `st-chp15-p362-this-surpassed-venetian-collections-referent-unresolved`：主语锚定`cand-10432`，predicate现表述country-house architecture与威尼斯收藏的比较；新增mention `m-chp15-p362-0087`，来源段字符范围`2426:2430`。`candidate_identity_questions`记录cand-1007与cand-10432的S3比较，S2不合并。

### 21条标量端点未齐的关系候选（交S3/S6）

当前2,530条S2关系候选中，2,509条有标量主、宾端点，21条至少一端保持开放。开放是原文语义范围或对象尚未细化，不等于候选外键悬空；目前21条涉及的候选引用均可解析。

| Statement | 来源锚点 | 未决端点与处理边界 |
|---|---|---|
| `st-chp2-secii-l118-125-paul-v-lifetime-monument` | 第2章p.41，L125 | Paul V `cand-0393`已识别，具体纪念物未指明；不创建单件作品。 |
| `st-chp2-secii-l118-125-sixtus-v-lifetime-monument` | 第2章p.41，L125 | Sixtus V `cand-1874`已识别，具体纪念物未指明；不创建单件作品。 |
| `st-chp2-secii-l118-125-urban-public-monuments` | 第2章p.41，L120 | Urban VIII `cand-0220`已识别；原文在“允许”与“鼓励”之间保留不确定，未指明纪念物或直接委托。 |
| `st-chp2-secii-l127-139-church-fashionable-patronage` | 第2章p.42，L134 | 教堂`cand-4521`已识别；竞争关联的欧洲显要人物未具名，不生成个人或群体实体。 |
| `st-chp2-secii-l127-139-peretti-similar-plans` | 第2章p.42，L136 | Peretti `cand-1875`仍有身份问题；“类似计划”的具体内容未说明，身份比较交S3，计划对象不猜定。 |
| `st-chp2-secii-l127-139-urban-withdraws-princes-permissions` | 第2章p.42，L137 | Urban VIII `cand-0213`已识别；获撤许可的外国王子未具名，不作个人端点。 |
| `st-chp2-secii-l141-145-barberini-altar-pictures-commission` | 第2章p.43，L144 | Urban VIII及共同委托人Antonio Barberini `cand-0186`已识别；委托对象是未逐件列举的祭坛画集合，没有单一作品端点。 |
| `st-chp2-secii-l71-78-marcello-searches-for-new-talent` | 第2章p.38，L77 | Marcello `cand-2314`已识别；所寻觅的艺术家未具名。 |
| `st-chp2-secii-l71-78-marcello-scholar-contacts` | 第2章p.38，L76 | Marcello `cand-2314`已识别；学者仅称为跨国群体，未列个人。 |
| `st-chp2-secii-l80-89-chronicler-quote-on-sacchetti-protection` | 第2章p.39，L87及注3 L178 | Sacchetti相关statement已记录；被转引的编年史作者未识别，所引原文未独立查阅。 |
| `st-chp2-secii-l80-89-giulio-made-cardinal` | 第2章p.39，L86 | Giulio Sacchetti `cand-2313`已识别；任命主体及任命机关未说明，不推断为Urban VIII。 |
| `st-chp2-secii-l80-89-marcello-papal-treasurer` | 第2章p.39，L86 | Marcello `cand-2314`已识别；“papal treasurer”保留为职务表述，任职时间及任命主体未说明，不另造办公室实体。 |
| `st-chp2-secii-l80-89-pietro-requested-subjects` | 第2章p.39，L81 | Pietro `cand-0356`已识别；习惯性请求所涉及的具体赞助人和题材未具名。 |
| `st-chp2-secii-l80-89-sacchetti-influence-on-taste` | 第2章p.39，L87 | Sacchetti家族`cand-4452`已识别；“品味影响”的具体对象和范围未指明。 |
| `st-chp2-secii-l91-104-urban-encouraged-friends-to-abandon-pagan-themes` | 第2章p.40，L97 | Urban VIII `cand-0230`已识别；朋友仅以泛称出现，主题候选`cand-4495`不是关系另一端。 |
| `st-chp7-p180-n4-pair-location` | 第7章p.180注4，L338 | 两幅画`cand-6773/6774`与Louvre、Detroit Institute of Arts `cand-4589/7072`成对提及；未逐幅指配。 |
| `st-chp8-p207-n1-ferdinand-left-thirds-to-daughters` | 第8章p.207注1，L136 | `cand-0914`将画作三分之一分别留给三名未具名女儿；未说明嫁给Giuliano Colonna `cand-7598`的是哪一位。 |
| `st-chp8-p211-del-rosso-marriage-alliances` | 第8章p.211，L85 | del Rosso家族`cand-7489`与“best families”联姻；对方家族和具体婚姻均未具名。 |
| `st-chp8-p238-note4-pictures-at-pisa-cabinet` | 第8章p.238注4，L446 | Pisa机构`cand-8048`所指图片可能为`cand-0874/0887`，也可能包括`cand-0885`；时间限定保留，Casini pp.42–50未独立查阅。 |
| `st-chp14-p353-bruhl-possessions-in-the-pictures` | 第14章p.353，L70–71 | 母题`cand-10293/10294`未逐一指配给`Maecenas` `cand-2597`或`Flora` `cand-2590`，亦未指配到具体住宅。 |
| `st-chp20-p403-alazard-commissioned-franceschini-picture` | 第二版后记p.403，L111–113 | 作品`cand-6888`及画家`cand-1066`已识别；实际委托人未具名，Colbert `cand-0800`及Strozzi `cand-2528`只记为经手人。 |

未发现应据原文新增而遗漏的具名、可独立识别端点；`candidate-backlog.csv`不存在。开放端点不补猜测，不写入`relations.csv`；身份问题交S3比对，关系成立与边类型交S6裁决。

### 递归引用完整性

递归引用检查覆盖12,310条statement及27,401条mention：78,487个候选ID字段引用涉及10,111个候选，悬空0；5,848个嵌套statement引用均解析。statement与mentions共45,311个segment引用、覆盖596个规范segment，悬空0；唯一带#L的行锚仍在段内。S3身份问题为22条statement、31个问题、22个候选ID，引用均存在；未决指代状态为0，脚注与交叉引用pending状态为0。另有1个collection_type_pending=true，对应第8章集合类型暂缺，不属于外键或脚注错误。严格阶段审计errors=[]、s2_missing=[]。关系候选的21条开放标量端点已逐条列于上表。全书其余断言限定语与语义风险仍待终审，S2尚未交接。

### 引用锚点、书目匹配与候选类型待决

对当前12,310条statement的顶层original_quote按各自source_file及source_line_start/end检查：12,264条在所指行段逐字匹配，46条在统一空白后匹配，未匹配0。175条第一章statement沿用01_CHP-1.md整章来源路径而segment_id指向规范分节来源；其引文和行号均能复现，整章副本不另计S0来源或覆盖。

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


## 第二章p.41–43正文与关系候选复核（2026-10-08）

完成第二章正文 l118-125（印刷p.41／PDF物理第26页）的语义复核，并回核其注释L185–190。正文由29条statement细化为35条，新增6条断言、1个“papal land and sea forces”机构候选和1条精确mention；补标28条关系候选，其中3条因比较性或一般性纪念物没有具体作品端点而开放。脚注1–6逐项与正文双向连接，注6涉及的两幅Claude Seaports保持机构对应未定。S2表中不写正式关系。

截至p.43复核，写后严格审计为1,019 KU、11,498 candidates、27,398 mentions、12,300 statements、832 segments；全书S2关系候选2,512条，其中2,491条具两端点、21条开放；`s2_missing=[]`、`errors=[]`。两条既存enrichment来源定位警告及语义复核提示仍在。p.42为34条statement、62条mention、26条关系候选（3条开放）；p.43为29条statement、38条mention、25条关系候选（1条开放）。未生成正式S6边。下一步复核已迁移的`chp-2:02_CHP-2_sec_ii:l147-193`注释段。

## 第十三章p.332–345脚注限定语与书目指引复核（2026-10-08）

第十三章合并注释段`chp-13:13_CHP-13_intro:l179-251`为reviewed/complete。对65条statement的过时注释状态、无对应脚注标记的限定语及图版年份冲突作定点修订；不改statement、mention、candidate或coverage数量。原引的期刊、书籍、信件、档案与手稿仍标为未独立查阅。澄清p.336 note 6不支持Zais送展断言、p.337 note 5不支持Caime句、p.338 note 1只链接Goldoni的扉页方案；p.342 note 5的标号落在收藏句末，不据此补出奖章或宝石的来源细节。Plate 57b题注的1761与p.338 note 1所引volume II (1762)作为未决年份差异保留。

p.332 note 4的“Berengo, 1957”已链接到书内唯一相符条目`st-chp21-bib-l129-163-entry-17`；note候选`cand-10136`与书目候选`cand-10134`仍分立，身份比较交S3。S3身份问题更新为22条statement、31个问题、22个候选ID。严格阶段审计仍为`errors=[]`、`s2_missing=[]`；全书语义限定和关系候选终审继续，未进入S3。

## 第十四章p.348通信关系候选与提及补录（2026-10-08）

复核14_CHP-14_intro.md L19–20，将原合并statement拆为“1734年2月续行至罗马”及两条通信关系候选：Algarotti—Bonomo、Algarotti—Francesco Zanotti。前者链接注2（L172，所引为一封1734年2月22日致Bonomo的信）；后者链接注3（L173，所引为1734年2–6月致F. M.及Eustachio Zanotti、Antonio Conti的信件）。原信与所引版本均未独立查阅，不将单封注释引文扩写为完整往来证据。

补录mention m-chp14-p348-0111，精确覆盖跨行姓名“Francesco Zanotti”，映射至现有p.348索引候选cand-2864（F. M. Zanotti）。cand-0043/cand-0068的Algarotti候选及cand-10226（Zanotti兄弟群体）不合并；身份对齐留S3。共增加2条statement、1条mention；候选表、coverage及正式relations.csv未变。当前S2关系候选2,529条，其中2,508条端点齐全、21条仍开放。

写前SHA-256：book-statements.jsonl=27cef89e4340b50912d859ff505ec05b88056e83e4c5aab37bebb81c5ebefb2c，mentions.csv=83cbe74b42385c62a552e90b1bdd1ffa45881ae9f28db524387cd3dc1e2664de；写后SHA-256：book-statements.jsonl=64a9c6b4e848d3d7cb883858bf577a56519f08e1fce3677e49ade040e14f902f，mentions.csv=6300b7dc5d4d5284d6ddab06c8ea3a80bb425790c8c5b2e1b9a4d74fd97bf9c9。恢复副本：%TEMP%/pnp-chp14-p348-correspondence-nizrx2c_。

严格阶段审计通过：1,019 KU、11,498 candidates、27,401 mentions、12,308 statements、832 segments；s2_missing=[]、errors=[]。未解决的source_ref警告仍为enr-06678和enr-06937。本项仅补录p.348关系候选与mention，不代表第14章关系审计或全书S2交接完成；继续审查p.349起的全书关系候选与限定语。

## 第十四章p.349关系候选拆分（2026-10-08）

复核14_CHP-14_intro.md L30，将原复合statement拆为三项：Algarotti在法国、英格兰、俄罗斯的行程；在Frederick the Great宫廷的安置/服务关系；Frederick于1740年12月授予其伯爵头衔。后两项各自保留为关系候选，其中授衔使用受控语义方向honoured_by（受荣者Algarotti → 授予者Frederick）。“December 1740”仅限定授衔，不外推为进入宫廷的日期；原书未提供授衔文书，仍按Haskell叙述记录。旅行列表保留为有据statement，不把它误写成对三国的居住或任职关系。

新增2条statement，无新增mention/candidate；p.349当前有13条关系候选，端点全部齐全。全书S2关系候选现为2,530条，2,509条端点齐全、21条仍开放；正式relations.csv未改。写前book-statements.jsonl SHA-256=64a9c6b4e848d3d7cb883858bf577a56519f08e1fce3677e49ade040e14f902f；写后=5f22734e1c6e52917eb4047958e103470ba5411ba6471dda16e4be14126d66ae。恢复副本：%TEMP%/pnp-chp14-p349-frederick-85_zgpem。

严格阶段审计通过：1,019 KU、11,498 candidates、27,401 mentions、12,310 statements、832 segments；s2_missing=[]、errors=[]。本批只完成p.349行程与授衔的语义拆分；第14章其余段和全书限定语、关系候选仍需审查，S2尚未交接。
