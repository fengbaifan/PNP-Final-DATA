# 第六章全书S2当前结果

任务：patrons-and-painters-full-book-s2。第六章共33个规范段。按当前覆盖账本，28段reviewed、5段excluded，queued/partial均为0；33段的migration_status均为complete。当前计数以`04-knowledge/tables/s2-coverage.csv`为准，全书状态见`04-knowledge/results/patrons-and-painters-full-book-s2.md`，后续逐段记录见同任务`results/stages.md`。

下文逐段处理说明、全书累计数及“下一段”是形成时的历史进度快照；当前覆盖状态以覆盖账本和全书结果文件为准。

## 第六章候选表面提示复核（2026-10-08）

在28个已审段上复核定位器给出的23条提示。8条补录为精确mentions：Rome三处→cand-3126；p.156注2的“collection”→Antonio degli Effetti类型待定收藏cand-6389；Christina的“collection”→既有图片收藏cand-5565；“foreign travellers”→cand-3562；“Renaissance”→cand-3578；p.164注3“theatre”→cand-6545。未新增候选。其余15条按原文语义不写入：普通subject 2、drawings类别、泛指palace、建筑“character”、temperament、financial difficulties、一般churches 2、Rosa比喻中的garden、Gaulli portraits类别、诗歌类别、crop prices及Ottoboni作曲活动。Rome三条均保留原提示“in Rome”，实际mention跨度只取城市名。

受控脚本`chp6_candidate_surface_prompt_reconciliation.py`锁定候选、mentions、statements、segments、coverage、定位器及相关S0分节，默认dry-run，核验23条提示分区、精确原文跨度、候选外键、既有跨度不重叠及statement前态后再apply。写入8条mentions；未增删candidate、statement、coverage或relation行。将p.156注2 statement的`mentioned_candidate_ids`补入cand-6389、p.164注3 citation statement补入cand-6545；修正p.164 Juvarra statement中已失效的“footnote 3 remains pending”限定。plan SHA-256=`db13bb71a4907ad5069cd729caa9c27d6f1069aca61dcb63a3a5475781451513`，script SHA-256=`cfbfbb7b6d4754384d2d3b683c1fa4ccaf26536e6f8f6735b575fe7d327ed5a8`。mentions SHA-256从`c43354eddb206f135ba3b638d4a4949e74dae129c4bbeb30158daf2a219c7541`变为`52a5b14c3ca39e3127ed89a491452f8043cb6a9b9092d19c6898241f80d38b58`；statements从`5999d2851d45c5b0ab2157478d8926d0ca4fc5aa1abcbcae164aab2ebdd9c1a6`变为`c1ba516072b1a54969c1de7a6763afe22ff984bca1469581ee49acdfa007cec3`。恢复副本保存在`%TEMP%\pnp-s2-chp6-surface-prompts-20261008-084741\`。写后定位器剩余15条，与全部no-write签名相同。

`python -X utf8 scripts/audit_tables.py --strict-stage`通过：1,019 KU、11,464 candidates、27,151 mentions、12,255 statements；`s2_missing=[]`、`errors=[]`，覆盖678 complete、154有理由排除、0 queued、0 partial。两条既存enrichment `source_ref`警告不变。第七章现有候选表面扫描为47个已审段、40条提示，均待按书序裁决；定位器提示不代表召回率或语义验收。

第六章旧阅读稿与草稿只作语义核漏背景。当前有效处理逐段对应规范源；脚注、跨页句及扫描校勘按印刷页序登记。第147–156页已处理范围内的跨页句均已闭合；p157 Antonio目录句由L56闭合，p158 Marucelli引介由L13闭合，Bellori《Lives》句由p159 L29闭合。

第160页正文段l40-50已迁移：新增19个候选；正文75条提及、20条原书断言。记录Bellori对竞争艺术趣味的反对及Haskell的限定解释、Maratta与古典理想/高巴洛克比较、Gaulli Gesù壁画的评价和引述层级、外地艺术家在罗马的处境、批评话语、Jacomo di Castro 1670年引文、Bellori任职、Christina经历与收藏及Haskell对其赞助的评价。校记见全书S2过程记录；S0原文未改。p159 L38句由p160 L41闭合；p160 L50末句续至p161 L53。

第160页脚注1–4（复合段l55-72的L66–69）已迁移，新增12条注释提及及4条书目定位记录，并分别回链至Gaulli接收、Jacomo引文、Christina引语和收藏断言。脚注仅作书目定位，未冒充外部核验。

第161页第IV节末段L52–53已迁移，新增1个事件候选、16条正文提及和8条原书断言；闭合p160 L50关于Christina赞赏Mola的未完句。新增Gherardi为Mola学生、其对Venetian colour的偏好，以及Bellori鼓励Christina赞助Canini、Canini分别作为Domenichino学生与Bellori门生等断言；保留Haskell的评价层级，不将赞助扩成委托。第161页脚注1（复合段L70）已与Canini相关断言回链；复核并将先前误挂在p159 ID下的p161注1、3、4提及改回p161。第V节L3–11正文及注2已处理，复合段L71–72的注3–4已回链；L11末句待p162 L15续接。物理第16页校勘：OCR将“of little”连作“oflittle”、在句号后多出逗号，且漏掉protégé重音；原S0不改。额外脚注2转录与第V节L12重复，已在S2有理由排除。

全书账本为247段reviewed/complete、0段reviewed/partial、41段有理由排除、515段queued；候选6,476条、提及9,913条、原书断言4,947条。表审计errors为0；两条既存enrichment source_ref警告及515段queued、语义质量复核提示仍在。

p161第V节迁移新增23个局部候选、53条精确跨度提及和22条正文断言；注2–4以4条引文定位statement处理并链接到正文，注3–4位于复合段L71–72。扫描物理第16页核实Clement IX后有空格、The fresco中间有空格、a Barberini前无多余o；S0原文保持不改。p161 L11末句待p162 L15续为“or a Chigi”，该断言保持pending。

下一段为chp-6:06_CHP-6_sec_v:l14-19（印刷页162）。续接完成后继续全书S2；全书覆盖和语义交接审计完成前不进入S3。

## 第6章脚注引用候选规范化（2026-10-10）

本章2条具有双端候选的`footnote_citation` statement已规范为`cites`候选；缺端引用仍待处理。详见[全书阶段记录](../process/stages.md)。

## 第六章p.158–160脚注书目指引语义复核（2026-10-10）

本章11条双端`footnote_bibliographic_pointer`逐条按印本文字及正文回链复核，规范为12条《赞助人与画家》`cites` archive候选。p.160注3原将Skippon与Misson两种来源合成一条作品间指向，现拆为两条来源引用，并补齐Christina描述statement的脚注回链；p.160注1保留avvisi与Roma出版定位的区别，注2保留书信与刊载文章的区别。被引文本均未独立查阅，关系仍属S2候选。详细依据、写回脚本及恢复副本见[过程记录](../process/stages.md)。

### 第六章 p.148 n.2、p.149 n.6 关系候选分类（2026-10-10）

回核 `06_CHP-6_sec_i.md` L123、L128及段内正文。p.148注2明确将Bernini与《君士坦丁骑马像》置于Innocent X时期委托语境，标记为关系候选；保留“only important”为Haskell的范围判断。p.149注6明确说《Allori d’Eurota》包含对Camillo Pamfili赞助活动的颂扬性记述，按作品主题关系标记为候选，不推断Pamfili为作者。两项均为Haskell脚注报告，作品/诗集未独立查阅，未写入S6正式关系。

p.153注1–5仍是一条复合的二手争议陈述：Samek Ludovici报告比萨条约授予法国国王雇用教皇艺术家的权利，Haskell则称该条款不见于已出版版本。现有subject/object为报告者与条约，无法直接代表被争议关系两端；暂不分类为关系候选，留待拆分主张、反驳和书目引用。此批未增删candidate、mention或statement。
全量同步闭合通过：9/9检查、303 passed与2个subtests；严格表审计errors=[]、s2_missing=[]，结构契约130/130。卡片预检1,019张、2,608张表、10,149行，files_to_write=0；工作树`git diff --check`通过（仅有LF/CRLF转换提示）。全书S2交接仍未完成。
### 第六章 p.153 注1–5 复合脚注拆分（2026-10-10）

将原复合statement拆成三个可追溯记录：Haskell之书对Baldinucci 1948版的引文（印本p.153为pp.111 ff.，并指向该版注107 p.249）；Samek Ludovici经Haskell转述的比萨条约“授予法国国王雇用教皇艺术家之权”主张；Haskell称该条款不见于已出版条约版本的反驳。关系主张端点改为未名法国国王与“Pope’s artists”群组，明确标为二手、受争议的S2关系候选，不声称实际雇用或权利确已生效。反驳保留为来源批评statement，不把缺席判断转换为关系。引用独立连至书目已有的Baldinucci 1948 archive候选；版本和注释未独立查阅。既有mention已覆盖各对象，不新增candidate或mention；statement净增2条。
## 第六章p.154注1所有权与书目引用关系复核（2026-10-10）

复核 `06_CHP-6_sec_i.md` L147。原`st-chp6-notes-l147-p154-n1-citation`明确把《赞助人与画家》`cand-2962`连至Baldinucci卷VI（1728）`cand-4846`，定位pp.558–559；改为`cites`并标记relation candidate。原`st-chp6-notes-l147-p154-n1-location`说`cand-6224`画作为Haskell 1980年文本写作时归`cand-6378` Paul Getty Museum所有，谓词修正为work→institution的`owned_by`，保留来源时间限定，不解释为当前馆藏地点。两端候选类型、source line、印本原文和coverage均通过预检；没有新增或删除candidate、mention、statement，也未写S6关系。

受控脚本 `process/classify_chp6_p154_note1_20261010.py` 以输入SHA、固定statement ID、候选类型、脚注定位、原文锚点和预期端点执行dry-run/apply。恢复副本：`04-knowledge/tables/book-statements.jsonl.bak-s2-chp6-p154-note1-20261010`；写前SHA-256 `862d6afed5b027c3b57238cc99b1b11b8354941a2fb0b9f1d290a10c79dbf09b`，写后SHA-256 `93d20c41325d4918b5fff54f3207a3880a783d5a6dd874277eb15e9db3374fcd`。
写后全量同步闭合通过：9/9检查、303 passed与2个subtests；结构契约130/130；严格表审计`errors=[]`、`s2_missing=[]`；关系一致性机械审计各错误项为0。卡片预检1,019张、2,608张表、10,149行，`files_to_write=0`；`git diff --check`通过。仍有两条既存enrichment `source_ref`警告，S2语义交接仍未完成。
关系候选增至3,780条（3,764条双端、16条开放）；双端未分类降至4,313条；双端脚注引用候选增至128条；`footnote_citation`降至659条，其中645条仍缺至少一个端点。

## 第六章p.154注2–4引文拆分与端点规范化（2026-10-10）

复核 `06_CHP-6_sec_i.md` L148–150及对应页下注。注2 Golzio 1939 p.14映射至既有archive候选`cand-6196`；注3 Pastor XIV p.329映射至既有候选`cand-4836`；注4将Golzio 1939和Incisa della Rocchetta 1925 pp.539–544拆成两条独立引用，分别指向`cand-6196`与书目已识别、内容未独立查阅的`cand-6379`。四条现有/新增statement均为《赞助人与画家》`cand-2962`→archive的`cites`候选；没有新增候选、mention或S6正式关系，statement净增1。

受控脚本 `process/classify_chp6_p154_notes2_4_20261010.py` 以输入SHA、固定statement ID、候选类型、coverage、原文行锚与mention覆盖执行dry-run/apply。恢复副本：`04-knowledge/tables/book-statements.jsonl.bak-s2-chp6-p154-notes2-4-20261010`；写前SHA-256 `93d20c41325d4918b5fff54f3207a3880a783d5a6dd874277eb15e9db3374fcd`，写后SHA-256 `acbd74bfa6cd7a43905209a4bfbc04bd95d20ef33087e31d332d070751b2f471`。全书现12,687条statement、3,784条`relation_candidate=true`（3,768条双端、16条开放），4,313条双端未分类；双端脚注引用候选132条；656条`footnote_citation`中642条仍缺至少一个端点。


本批写后全量同步闭合通过：9/9检查、303 passed与2个subtests；结构契约130/130；严格表审计`errors=[]`、`s2_missing=[]`。卡片预检1,019张、2,608张表、10,149行，`files_to_write=0`；关系一致性机械审计错误项均为0。既存两条enrichment `source_ref`警告和S2语义质量提示仍在。

## 第六章p.155注释1–5引文及范围主张拆分（2026-10-10）

注1、2、3、5及注4续注已规范为7条本书→archive `cites`候选；注3匿名1783年目录与Corti短述分开，注4续注的Pascoli与Bellori引文分开。注4正文概括“十七世纪艺术文献多有Colonna赞助记载”单列为Haskell范围性主张，明确不是关系。正文注4回链与续注L154/L110定位已同步。候选和mention均复用，不新增KU、candidate或mention，不写S6正式关系。受控写回及SHA、备份、端点核验记录见[全书过程记录](../process/stages.md)。写回后全量复核待执行；全书S2交接仍未完成。

## 第六章p.155正文关系候选复核（2026-10-10）

L103–109中12条直接支持的有端点关系现标记为S2候选，覆盖Bernini重建宫殿、Filippo/Girolamo重建装饰Colonna宫殿、Lorenzo–Maria婚姻、Palestrina领地售予Barberini、Lorenzo的家族赞助/收藏增补/艺术家聘用、Grimaldi在宫殿绘制风景、Lorenzo题材偏好与可能的风景装饰影响，以及Resta的艺术批评。保留Haskell引述、作者限定和未名委托者；不合并同名宫殿候选、不建S6正式关系。写回备份、哈希及逐条预检记录见[全书过程记录](../process/stages.md)。全书关系分类与S2语义交接仍未完成。

## 2026-10-15 p.146 开放端点复核

statement st-chp6-p146-taxes-and-patronage 的被动句只说明加税与没收私人银器发生，没有指出行动者。未从前文政治背景推定执行方，保留subject开放并补充open_endpoint_reason；无新增对象或正式关系。严格阶段表审计通过，计数保持12,305 candidates、26,500 mentions、15,118 statements，开放端点481。详情见[全书S2过程记录](../process/stages.md)。

## 2026-10-15 p.158 Marucelli开放对象复核

新增 cand-12328–cand-12330 与三条精确mention，分别登记Marucelli委托的伟人半身像组、其所写生平且与之相友的主要画家子群、以及填充其藏书的伟人作品组。四种媒材按原文保留；个体题名、作者和数量未知。OCR “fdled”未改S0，仅记页图读作“filled”。三项端点均关闭；无新增KU或正式关系。严格阶段表审计通过，当前开放端点478。详见[全书S2过程记录](../process/stages.md)。

## 2026-10-15 p.165 风格关系拆分

将style从master到pupil、court到court的传播与princes/general public对风格的欣赏拆开；把true Baroque、French rococo、later eighteenth-century painting三项评价比较拆为三条statement。新增cand-12331–cand-12334、三条mention和三条statement；将“the true Baroque”既有mention从宽泛Baroque文化候选改接到本段更具体的风格比较候选。保留Haskell的评价归属与S0 OCR校读，不推定具体作品、人物或宫廷。严格阶段表审计通过：12,312 candidates、26,506 mentions、15,121 statements；开放端点476，全段无开放端点。详情见[全书S2过程记录](../process/stages.md)。

## 第六章p.147–148跨页端点与作品对象复核（2026-10-15）

p.147为收入调查受威胁建立事件候选`cand-12396`，把Barberini出逃statement接至该未实际启动、调查主体未明的事件；为Innocent X的建筑意图建立计划建造事件`cand-12398`，保留全部建筑清单未详。军职任命主体仍未具名；cardinalate保留为Camillo的角色描述，不另造办公室实体，二者补充开放理由。

p.148将“a number of other projects”从Camillo人物候选重映射为未定类型的项目群`cand-12397`。金融困难与计划穹顶分别登记为`cand-12399`（类型待定）和`cand-12400`（work）；原先指向整体Lateran改建的穹顶mention改接计划穹顶。Cortona画廊天花板commission的mention从人物候选`cand-0353`改接p.149明确点名的Aeneid壁画组`cand-11957`，首项正式委托statement也接至该作品。p.148“艺术成就”续句改为非关系的评价性概述；“艺术生活复兴”仍记为时间关系候选，具体事件对象开放并说明理由，不推定Camillo造成复兴。

新增5个候选、3条mention；重映射3条既有mention；5条开放关系statement补齐端点，另1条改为非关系分类；3条仍开放的statement补齐理由。严格阶段表审计通过，`errors=[]`、`s2_missing=[]`。无新增KU或正式关系。

## 第六章 p.157–164 开放端点与引文复核（2026-10-15）

p.157 Spon/Wheler脚注、p.161 Pascoli卷I与卷II脚注分别由Haskell原书候选`cand-2962`指向对应archive候选；卷I、卷II不再合并为一个引用statement。p.162 Clement IX的S. Maria Maggiore计划改建与墓地方案连接到新事件候选`cand-12410`（教宗去世），只表达“去世后中止”的时间关系。匿名法语见证引文的文字止于印刷p.162，日期“1685.”在p.163续接；页图校正OCR问号并链接续段。此引文属于来源归属statement，不构成实体关系，原statement改为非关系，Michaud引文仍单独记录。p.164 Ottoboni的1689年枢机任命由新事件候选`cand-12411`表达；原句未指出任命者，不从上下文推定。

本批没有新增KU或正式S6关系。严格阶段审计通过；全库开放端点372，其中51条尚缺行级理由。下一条缺理由记录为第七章p.171 `st-chp7-p171-i09`。

## 第六章 p.151、154、155 书目端点S3–S6（2026-10-26）

`cand-6367` Norbert Wibiral与跨章候选`cand-3498` Giovanni Incisa della Rocchetta由`undecided`改判来源限定`new`人物组；`cand-6368`、`cand-6379`、`cand-6381`沿用各自既有`new`文献组并完成S4映射。五个候选对应五张新KU，新增23条source-backed字段。三条Haskell引文关系formal为`rel-2132`–`rel-2134`；外部书目支持的两条结构性`authored_by`边另列`rel-2135`、`rel-2136`。Colonna目录保留匿名；被引文章、目录和引注页未独立阅读。六张卡写后复预览均无差异；严格表审计`errors=[]`、`s2_missing=[]`，关系一致性阻断为0。全书最新状态及后续队列见[当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)，完整证据见[过程记录](../process/knowledge.md#s3-s4-s5-s6-chp6-bibliographic-endpoints-20261026)。
