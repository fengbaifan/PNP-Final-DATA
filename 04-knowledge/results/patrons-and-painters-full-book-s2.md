# 《赞助人与画家》全书语义处理（S2）当前结果

更新日期：2026-10-11。任务ID：`patrons-and-painters-full-book-s2`。**状态：S2交接审计进行中，尚未进入S3。**本页只记录当前范围、数据、未决项和下一步；历史逐项裁决见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)、[阶段结果索引](../../03-processing/patrons-and-painters-full-book-s2/results/stages.md)及各章结果。

## 范围与覆盖

S0登记79个规范来源文件、832段，涵盖书前材料、第1–17章、结论、附录、第二版后记、书目和索引；42段为派生视觉转录。第十一、十二章与第十章同版扫描产生的44段重复OCR已排除。书目按出版记录和引文定位处理，索引按候选定位材料处理，不作为正文断言。

| 当前S2覆盖状态 | 段数 |
|---|---:|
| reviewed / complete | 678 |
| 有理由排除 / complete | 154 |
| queued / partial | 0 |
| 合计 | 832 |

所有纳入处理的正文、注释、图版说明及书前/书后材料均已有S2处理记录。书目段已处理至L3–1306。纸本索引范围终审已完成：`CHP-22Index.pdf`共32页（p.443–474），规范索引94段均有coverage且迁移完成；19份Markdown与CSV的2,934行集合一致，2,934个CSV行号均有唯一候选索引ID并纳入逐页/栏映射。此前p.446发现并回补的四条为本次确认的纸本漏录；未发现其他未登记纸本词条。另将p.454印本“Fetti, Domenico”与F.csv#48的“Feti, Domenico”差异核清，cand-1033显示名已按印本校正，源文件未改写。p.460和p.462页码在页图中存在，PDF文本层漏识。全库脚注续页、正文回链和statement引用已专项检查：第七章p.186注1、第十三章p.333–334注1及第九章p.264–265注8的正文范围、目标注文页和正反链接已核正；嵌套脚注/续注pending项在已审范围内闭合；印本异常按证据保留，包括p.247印号不可见、p.270注7疑似错位、p.359注4无标记且重复注3，以及本次确认的p.377正文标号6与页底注5错配（已标记mismatched，不强行回链）。p.247印号不可见、p.270注7疑似错位、p.359注4无标记且重复注3等印本异常按证据保留，不强行回链。

## 当前数据与机械检查

当前库表规模：1,019 KU、11,745 candidates、27,697 mentions、13,348 statements；另有1,227条relation记录（1,225 formal、2 pending）、335条alignment及10,149条enrichment（1,501未验证）。S2覆盖登记832/832：678 reviewed/complete、154 excluded/complete、0 queued/partial；该登记不等于语义交接完成。statement分类为relation_candidate true 6,344、false 2,336、unset 4,668；9,107条双端statement中6,268 true、536 false、2,303 unset；76条true候选仍缺至少一端。

本轮按书序补记并推进第5章p.120–127。p.120–123复核原断言、细分主张并记录跨页和脚注；p.124复核21条旧statement并新增29条原子断言，另将注1的Monconys与Bellori两项引证规范为独立cites候选；p.125复核19条旧statement、新增23条原子断言、25个开放候选和27条精确mention；p.126复核20条旧statement并新增38条断言、14个候选和14条mention；p.127复核31条旧statement并新增15条断言、14个候选和11条mention，46条statement全部分类为40条关系候选与6条非关系陈述。更正1680年Pantheon警务命令与实际扣押的区分、1662/1668展览实例、匿名群体端点、Baglione—Orazio竞争及作品地点；p.128续引和Haskell评价已接回。保留来源归属、不确定性和OCR差异，不写入S6正式关系。

最新检查：p.127写回后audit_tables.py --strict-stage --summary为errors=[]、s2_missing=[]；仅保留两条既存enrichment来源引用警告（enr-06678、enr-06937）及语义质量提示。关系一致性五类硬错误均为0，另有135个零关系KU及1个超连接诊断；全卡预检1,019张、2,608张表、10,149行，files_to_write=0。本次未重跑全量闭合；最近一次p.126后9/9通过（303 tests、2 subtests；结构契约130/130、系统升级链4/4、项目规则契约4/4）。第5章候选表面定位器此前提示43处，p.125正文与注释段没有未覆盖提示；该工具只查已有候选词面，不证明实体召回完整。成熟度仍未评分：1,019个KU均缺confidence/consensus，证据状态为6 externally verified、2 partially verified、1,011 source-backed；没有独立外部语义验收。结构通过不证明事实准确或实体召回完整。

## 保留的历史进度摘录

以下摘录保留先前进度说明，可能包含旧计数和旧游标，不表示当前状态；当前范围、计数和游标以上文为准。逐项过程依据见对应过程记录。

本轮按书序复核第一版序言L10–17的5条双端statement：4条标为非关系陈述，1条标为S2关系候选并将协助者Enzo Crea校正为主体、Haskell校正为受助端。复合的那不勒斯绘画—威尼斯解释保留作者归属，因当前端点不能表达原文完整因果链而不升级为关系，后续交接审计仍需判断是否拆分。无candidate、mention或statement增删。 写后严格表审计`errors=[]`、`s2_missing=[]`；全量同步闭合9/9通过（303 passed、2 subtests），结构契约130/130；卡片预检`files_to_write=0`。

本轮继续处理第一版序言L19–29：14条双端致谢/署名陈述均标为S2关系候选，逐项保留帮助者、受助者、作品、机构和语境角色。页图（CHP-0Cover.pdf物理第7页／印刷页ix）确认“Elizabeth Orna”，S0的“Oma”转录未改写；无candidate、mention或statement增删。 写后严格表审计`errors=[]`、`s2_missing=[]`；全量闭合9/9通过（303 passed、2 subtests），结构契约130/130；卡片预检`files_to_write=0`。
第二章p.61注1、3、4已分别转为Vatican手稿引用与馆藏、全书范围说明及Baglione/Pastor引文、Francesco参与San Carlo建造的未定角色陈述及Pollak引文；未具名的其他馆藏不扩展成候选，Pastor卷XIII的1943年份仍不作版本断定。第六章p.153注1–5的争议已保留在来源限定的关系主张与作者反驳中，未把主张写成已证实事实。

仍有两条既存enrichment source_ref警告（enr-06678、enr-06937），语义成熟度未评分且尚无独立外部语义验收。第十六章p.377正文及p.376注3续文、页下注1–5已完成语义复审：由首轮34条细化为49条statement，本次新增15条statement、3个候选和3条mention；p.378结论拆为4条组级statement，校正Sasso回指到人物候选cand-2364。全书交接审计另将p.362“all three patrons”按第十五章三位赞助人小节标题解析为Farsetti、Memmo、Querini，新增三条标量S2关系候选；并为p.207明确限定的“三名女儿”补建无类型群组候选`cand-11553`、原文mention及标量关系端点，未分配具体份额或个体身份；p.43联合委托的“altar pictures”现以作品群组候选`cand-11554`承接，并修正“Guido Reni”映射至人物候选`cand-2124`，保留索引作品子项`cand-2126`与具名画作候选`cand-4544`分立。p.377正文印本标号6与页底注5仍为已记录错配。第2章p.38回查新增匿名学者群体候选cand-11557并补精确mention；Haskell随后的Pietro叙述将Galatea复制品画家在本书叙事中指向cand-0342，注4仍保留不同版本限定；通称“new talent”仍无有界对象、保持开放。第二章p.42将“great figures from all over Europe”及获准后被撤回权限的“foreign princes”分别登记为来源界定、无类型且status=open的群组候选`cand-11555`、`cand-11556`；成员与数量未知，不把相邻人物例子当作完整名册。Peretti“similar plans”保持开放，限定为未指明具体计划或献堂对象。p.39“one chronicler”现按直接相连的注3来源归到已有Soprani候选`cand-3500`，仅为引用层面归属；被引页未独立查阅，S3身份仍待核。p.367单数“one”登记为开放作品候选`cand-11561`，Waldstein资助疑问及Skala/Veith备选题材连接至该候选；复数“further statues”现以作品群组候选`cand-11562`承接，并新增精确mention，未枚举的成员和数量仍未知，且不推断单数雕像属于该组。p.363“Venetian painting and sculpture”现按来源限定的艺术实践term候选`cand-11563`接入开放statement端点，并保留同词段内`Venetian`到Venice地点候选`cand-3401`的嵌套修饰语映射；“one of them”现登记为未名同时代人候选`cand-11564`并连接赞语statement，身份仍待核，未据注2认作Boscovich。p.364“一大批诗歌和演说”现登记为来源限定、类型待定的开放文本群候选`cand-11565`，不推断个别作品、作者、日期或数量。第七章p.180注4复裁将原合并的2×2关系候选拆为两个标量S2候选：cand-6773→cand-3254（Inspiration du Poète—Louvre）及cand-6774→cand-7072（Diana and Endymion—Detroit）；配对依据作品、馆藏和目录页码的并列顺序，原注未使用“respectively”，所引目录pp.46/65未独立查阅。原聚合statement保留作上下文，不生成S6正式边。全书S2语义交接尚未完成；此前记录的第3章游标已过时，当前游标见下方“全书S2交接审计与下一步”；coverage完成不等于语义接收。

仍有两条既存enrichment `source_ref`警告：`enr-06678`、`enr-06937`无法从对应卡片source清单解析。机械检查不等于语义准确或实体召回完整；目前没有独立外部语义验收。

## 候选表面复核与当前游标

书前材料及第1–10章、第13–18章的候选表面提示已逐项裁决；第十一、十二章与第十章共用规范来源。第十六章7个reviewed段的11条提示中6条映射、5条不写；新增cand-11500至cand-11502、6条mentions和1条statement，另修订既有statement的候选关联与subject、更新cand-10598 detail。写后定位器剩余5条，与已裁决的不写项一致。逐项记录见[第十六章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-16.md)。

第十七章10个reviewed段的8条提示已逐项裁决；新增cand-11503至cand-11508、9条mentions，修正Joseph mention的候选映射，并更新竞赛题材statement。定位器剩余3条均为已裁决的不写项。第十八章2个reviewed段的2条提示也已核实为普通词义/候选错配，无表修改。第十九章12个reviewed段的17条提示已完成语义裁决：新增cand-11509至cand-11516及20条mentions，修正或扩展7条既有mention、核正statement候选关联；唯一残余提示`subject`为一般词义，明确不映射。第二版后记20个reviewed段的24条提示也已完成；新增2个候选和4条mentions，修订4条statements，写后剩余20条均与有依据的no-write裁决一致。详见[第十七章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-17.md)、[第十八章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-18.md)、[第十九章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-19.md)及[第二版后记结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-20.md)。

全书候选表面提示复核已推进至第二版后记并完成；定位器剩余的20条均为已逐项裁决的不写项。定位器只匹配已有候选词形，不证明实体召回完整，也不替代全书S2交接审计。

## 全书S2交接审计与下一步

按书序核对，当前游标为第5章印刷p.128 L88：st-chp5-p128-medici-1675-exhibition，属于段chp-5:05_CHP-5_sec_i:l85-97。全库双端statement共9,107条：6,268条标记关系候选、536条标记非关系、2,303条尚未分类；另有76条true关系候选缺少至少一端。p.120–127裁决记录已补齐；S2全书交接仍未完成。

全书候选表面提示复核、段覆盖登记、statement语义裁决及跨阶段登记属于不同工作状态。不能从832段迁移完成、候选提示已处理、现有KU/关系/enrichment表，推断全书实体召回、事实准确或S3–S6交接已验收。

下游快照状态：仓库中的`release/v0.1`与`release/v0.2-draft`是既有快照，不代表当前S7交付。`v0.2-draft/metadata.json`及`validation-report.md`仍记790个规范段、29段迁移，当前表为832段、678段reviewed/complete；该包的README标注不得公开分发，权利审查和引文元数据未完成。待全书S2交接后再按当前表重建与验证发布包。

全书S2交接审计仍在进行。已复核两条原标为`referent_status=unresolved`的statement：第十章p.316注4的“These paintings”回指本段cand-9678所代表的Nogari作品组；单幅照片与作品之间的对应仍未知。第十五章p.362的“This”回指前句的country-house architecture，后文将该住宅定位为S. Maria di Sala别墅；正文候选cand-10432与索引种子cand-1007留给S3做身份对齐。两条显式未决指代状态现均已改为有范围的上下文解析，但全书其余指代和限定语仍需终审。第二章后置注释L147–193本轮完成语义复核：已修复113条正文—注释反链，拆分1633年avviso的制作、委托和报酬主张，厘清p.33与p.60挂毯候选之间的交叉引用但不合并身份；p.40脚注、第1章脚注及L193通往`sec_iv:l3-4`的引用均已对齐。该段现有85条statement、93条mention及16条关系候选；所有关系仍处S2候选状态。

第二章p.39页图复核后，四条关系候选继续开放：Giulio升任枢机的授予者未明；Marcello的教皇财务长职务无任期和任命者；Pietro习惯性向“his patrons”索题材但未给出具体对象群；Sacchetti家族的品味影响未限定具体目标。没有从教皇身份、相邻引文或例子补猜端点。p.40的“his friends”现登记为无类型、status=open的匿名群体候选cand-11558，精确mention为m-chp2-secii-l91-104-0066（[547,558)）；对应关系候选已连接该群体。成员、人数未知，不把前句提到的诗人直接并入。
第八章p.211关系端点复核：原文“a series of ingenious marriage alliances with the best families”明确提及参与该系列联姻的未名家族群，现登记无类型、status=open候选`cand-11559`及精确mention `m-chp8-p211-080`（[453,470)），statement `st-chp8-p211-del-rosso-marriage-alliances`对象端点指向该群组。具体家族、人数、婚配配对与日期均未载；不推断成员或个体婚姻。
第十五章p.370重新复核“those formed in Switzerland”：该短语指园林中另一组由祭坛纪念的瑞士友谊，新增无类型、status=open群组候选`cand-11560`及mention `m-chp15-p370-alticchiero-0049`（[2218,2245)），连接关系候选对象端点。成员、人数及名册未知；不将Voltaire、Festari、Girolamo Giustiniani或Mme Rosenberg并入。

第十五章p.367端点复裁：单数“one”登记为开放作品候选`cand-11561`，mention `m-chp15-p367-memmo-0066`跨度`[1175,1178)`；Waldstein的资助疑问及Skala/Veith两个备选题材均连接至该候选。复数“further statues”另登记为开放作品群组候选`cand-11562`，mention `m-chp15-p367-memmo-0067`跨度`[1001,1016)`，对象端点接入该群组；原文未枚举成员或数量，也未说明单数雕像是否属于该组。写后全库11,543 candidates、27,476 mentions、12,644 statements；2,808条S2关系候选中2,793条端点齐备、15条开放。


脚注候选交接审计已覆盖第二章p.59注1–5、p.60注1、注2（Bellori与Mezzetti拆分）、注6、p.61注2；本轮复合注2形成两条独立cites候选，Mezzetti端点cand-4948保持open。此前第二章复核批次规范化115条；全书已规范化的双端脚注引用候选按既有记录为132条。p.60注3已拆为位置报告、肖像群与Nanteuil两幅归属候选、Lombardo引用四条记录；“the portrait”mention已改指cand-4922。未分类footnote-claim当前为0；第六章p.153注1–5已拆分为来源引用、关系主张与反驳。当前表另有599条`footnote_citation` statement：仅有subject 6条、仅有object 528条、两端皆缺50条、两端齐全15条；至少一端缺候选的共584条，仍须逐条结合来源语境处理。

### 指代记录

- `st-chp10-p316-n04-honour-showed-haskell-painting-photographs`：目标cand-9678；注释说明组级先行词已确定，未把照片逐张映射到作品。正文statement的旧“注4待规范链接”限定已清理，`cand-9918` detail同步修正。
- `st-chp15-p362-this-surpassed-venetian-collections-referent-unresolved`：主语锚定`cand-10432`，predicate现表述country-house architecture与威尼斯收藏的比较；新增mention `m-chp15-p362-0087`，来源段字符范围`2426:2430`。`candidate_identity_questions`记录cand-1007与cand-10432的S3比较，S2不合并。

第十四章p.351已完成一次语义复审：23条首轮statement扩至45条、67条mentions扩至74条。两条原误指Pittoni的`his`改指Algarotti，补入7条明确的人称指代；另拆清三位历史画家的类别、拟分配题材、区域艺术家名单、Augustus对古代大师的偏好、五幅作品组的选择/绘制/遗失，以及注2书信的作者和收信人。该页28条关系候选均有标量端点，仍处S2候选层；没有新建候选或正式关系。`the four Venetians`的指代集合保留未决，因为同段明确说Canaletto被忽略，未用Zuccarelli替换或猜定名单。p.351末句与p.352互链；p.352说明其Tiepolo画作不属于五幅失传作品组。

p.352首轮21条statement和73条mentions经复审后调整为31条statement、76条mentions。改正Tiepolo人物与作品候选混淆、Algarotti跨页指代及本页人称映射；补全画作作者、组别、原定受赠者、信件端点、Smith权利放弃、两版本位置等断言，拆开注2中Morassi的归属说法、Haskell的可能性与证据限制。18条关系候选端点齐全；没有新增KU、候选或正式关系。Brühl只作为计划拟送对象，未断言已寄出；身份及引注差异留待S3。

p.353首轮24条statement和74条mentions经复审后调整为35条statement、75条mention。修正Tiepolo人物与《Cleopatra宴会》作品候选混淆，处理错指画作的“this”、Algarotti代词及Brühl专题索引子目映射；分拆两幅Brühl作品的作者、送达和注释所载位置关系，并记录未定年信件的作者/收件人/携带版画计划。两幅画的具体Brühl装饰母题仍未配对；一条开放端点关系保留待证。p.353现20条关系候选，19条端点齐全；无新增候选、KU或正式关系。内部书目与注释、版图题注及相邻页statement均已互链。详见[第十四章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-14.md)。

p.354首轮27条statement和71条mentions经复审，纠正注5 OCR页码`296`为印本`206`，并补齐注2–4与第21章对应书目statement的双向链接。p.354/p.355跨页句的断言范围和互链同步校正；没有新增知识元、候选、statement、mention或关系。详见[第十四章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-14.md)。

p.355首轮27条statement和87条mentions经复审，14条关系候选端点全齐。注2 Pallucchini 1956定位与Piazzetta书目条目双向链接；注3 Levey 1960及Selva可能对应的目录条目建立双向链接，Selva匹配留待S3确认；并连通与p.354同一Levey引注。正文至p.356的跨页句和注释链接保持有效；未新增或删除实体、statement、mention或关系。详见[第十四章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-14.md)。

p.356现有30条statement（正文23条、注释7条）和72条mentions。将“Venice”mention从Algarotti索引候选改映射至地点候选，新增其持续关注意大利艺术事务的独立断言，并明确推广意大利／威尼斯艺术的动因包含爱国情感。印本校读更正记在S2，未改S0；p.356至p.357续句和脚注链接有效。13条关系候选维持S2状态，不新增候选或正式关系。详见[第十四章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-14.md)。本页复审后按书序转入p.357；全书S2交接仍未完成。

p.357复审共58条statement、79条mention和36条关系候选（36/36端点齐全）。新增2个候选、4条mention、34条statement，修订18条本页statement及1条p.358跨页statement；校正印本脚注标记与数处OCR读法，修正作品/人物/地点映射，并拆分Batoni、Pannini、Tiepolo、Canaletto及脚注书信相关断言。拟议作品、请求、归属冲突和Rialto视图身份均保留原文限定；未新增KU或正式关系。详见[第十四章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-14.md)。本页复审后按书序转入p.359；全书S2交接仍未完成。

p.358复审36条statement、52条mention及17个既有候选，无数据行增删；仅为4条statement加入5项印本校读。注5 OCR标号误作6已按页图改记；注2中的印本方括号保留。正文对绘画类型责任的表述仍限定为书信刊行后逐渐形成的观念，p.357/p.359续句及注释链接有效。全库总数不变，严格表审计`errors=[]`、`s2_missing=[]`。详见[第十四章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-14.md)。下一项按书序复核p.359 `chp-14:14_CHP-14_intro:l126-137`；全书S2交接仍未完成。

p.359复审24条statement、49条mention，无增删；新增未具名原作候选`cand-11522`并与Tesi复制品`cand-10400`分开，修正两条mention映射和理论作品评价的主语。对照印本为五条statement记录六项OCR校读，未改S0或原始引文。注4仍是无正文标记、与注3重复的孤立注释；12条本页关系候选端点齐全。严格审计`errors=[]`、`s2_missing=[]`；全量同步闭合通过（303 passed、2 subtests passed）。详见[第十四章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-14.md)。下一项按书序复核p.360 `chp-14:14_CHP-14_intro:l139-146`；全书S2交接仍未完成。

p.360复审后为23条statement、43条mention和7条本页关系候选（7/7端点齐全）。新增碑铭候选`cand-11523`，补入碑铭、纪念碑及注2中Algarotti两处mention；拆分碑铭改编Horace诗句与置于纪念碑的断言，并将Biffi引语限定为Algarotti—Cecilia Emo关系候选。三项OCR校读只记在S2；版画、纪念碑与碑铭分开，p.359注4与本页注4分开。严格审计`errors=[]`、`s2_missing=[]`；全量同步闭合通过（303 passed、2 subtests passed）。详见[第十四章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-14.md)。下一项按书序复核p.361 `chp-14:14_CHP-14_intro:l148-149`；全书S2交接仍未完成。

p.361版图说明复审后为2条statement、2条本段关系候选；另将书前Plate 61a/61b的两条作品—作者caption归类为关系候选。将早期版与最终版的作品关系和页题归属于Algarotti的影响表述拆开；后者保留为印本页题的主张，不当作独立核实的历史事实。S0只含“a. Early version”；“b. Final version”及主页题按扫描图读取，无伪造mention或改写OCR。印本页题拼作“Antony”，书前图版目录拼作“Anthony”，两种文本层保持原样。严格审计`errors=[]`、`s2_missing=[]`；全书关系候选2,616条、2,595条端点齐全、21条开放。

p.362–363图版题注复核后新增2条嵌套地点mention和2条statement，Plate 62的作者、描绘地点、地点在Padua分项记录为关系候选；书前同名索引seed留S3对齐。Plate 63 OCR/扫描题注为截断片段，完整题名只由单独的书前图版目录支持，S0不补写。对应已有的p.62与p.63书前作者/地点statement也标为关系候选。阶段审计后全库关系候选2,625条、2,604条端点齐全、21条开放。

p.364旋转题注复核新增地点候选`cand-11524`和1条精确mention；把作品作者与画作描绘的John Strange别墅分开，并将别墅位于Paese、Paese近Treviso及题名与Strange的关联分别记录。匿名London private collection保留开放端点，不推断所有人。S0逐词倒序文本保留；印本视觉读数作为独立证据。严格审计`errors=[]`、`s2_missing=[]`；全书关系候选2,632条、2,610条端点齐全、22条开放。详见[第十四章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-14.md)。该批次后转入第十五章p.361；此页现已完成本轮交接复审，最新游标见下文。

第十五章p.361正文及脚注交接复审（2026-10-09）：对照CHP-15.pdf物理页1复核正文及intro文件中的本页注1–2。补入此前遗漏的标题mention FILIPPO FARSETTI（m-chp15-p361-0054，cand-1002，跨度0:16）；更正两条脚注断言中的印刷页号p.362为p.361；从注2所引信件新增Mariette authored_by及Temanza addressed_to两条来源关系候选。新增1条mention、2条statement，不增候选、KU或正式关系；信件及刊本未独立查阅。详细裁决见第十五章结果。下一项按书序为p.362正文 chp-15:15_CHP-15_sec_i:l16-25。

第十五章p.362正文复审（2026-10-09）：对照`CHP-15.pdf`物理页2重核`chp-15:15_CHP-15_sec_i:l16-25`。73条mention跨度均准确，44条statement引文在S0内均精确；印本`milord, employing`与OCR连写`milord,employing`的差异记入S2校读，不改S0。补入6条断言，将别墅位置、拟容纳的两类收藏、柱群与Dea Concordia神庙来源及神庙所在Rome分开建模；为Farsetti居住Paris、其在威尼斯新古典运动中的角色、别墅和柱群关系补齐S2关系候选。`Lodoli`是“三位赞助人”的直接启发者现列为开放关系候选，目标名单不猜定。修正候选`cand-10430`的跨页说明和`cand-9206`的使用范围；无新增候选、KU、mention或正式关系。第十五章结果与过程记录见[此处](../../03-processing/patrons-and-painters-full-book-s2/results/chp-15.md)。p.362后的下一项为第十五章p.363正文`chp-15:15_CHP-15_sec_i:l27-36`。

第十五章p.363正文与注释语义复审（2026-10-09）：对照`CHP-15.pdf`物理页3复核正文及L43–56注释。纠正million-ducats断言误连注1；将整段赞誉（包括Farsetti在Paris受敬重）归于匿名当代引文，不据注2将说话者认作Boscovich。将Canova“最著名的学生”关系改为Canova→Palazzo Farsetti，将花园/住宅比较关系改为花园→住宅；“Venetian painting and sculpture”不再误连Venice地点。拆分Canova创作首批两只花篮与花篮被放置在宫邸楼梯的断言；新增Algarotti古典范式理论归属及注2书信的作者、收信人statement，均保留来源限定。对正文与注释记录9项印本校读，不改S0或原始引文。正文段现35条statement、69条mention、23条关系候选（3条保持开放）；新增4条statement，无新增候选、KU、mention或正式关系。全库现12,409条statement、2,659条S2关系候选（2,633条端点齐全、26条开放）；所有12,409条引文均可在来源行段复现。详细裁决见[第十五章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-15.md)。下一处为p.364续接段`chp-15:15_CHP-15_sec_i:l38-41`。

### S2 关系候选开放端点（清单59/71；S2交接审计中）

当前全库有5,907条S2关系候选，其中5,836条双端齐备、71条至少一端未定。下表目前列出59条逐条说明；另有12条尚未进入该说明表，须在S2交接前逐条核对。relation_candidate_note与open_endpoint_reason字段统计另见上方快照，两个字段计数有重叠。

| Statement | 来源锚点 | 未决端点与处理边界 |
|---|---|---|
| `st-fm-2ed-l174-185-10-group-migration` | 第二版导言L180 | 主体是未具名画家群体；Rome `cand-3126`为目的地。Conca、Giaquinto、Batoni为例示，不把Naples/Tuscany分别配给画家。 |
| `st-fm-2ed-l174-185-11-refusal-explanation` | 第二版导言L182 | 拒绝定居Rome者是来源限定的未建模群体；Waterhouse提出竞争恐惧这一解释，保留其不确定性，不视为画家本人证词。 |
| `st-fm-2ed-l174-185-12-guido-guercino-comparison` | 第二版导言L183 | Guido与Guercino拒留Rome的历史比较保留来源归属；Guido身份和具体事件未定，不补具体场合。 |
| `st-fm-2ed-l174-185-14-disjunctive-painter-claim` | 第二版导言L184 | Haskell所说的意大利画家群体未具名；Crespi与Solimena是例子，不能把二选一的群体断言分配给个体。 |
| `st-fm-2ed-l174-185-17-later-generation` | 第二版导言L184 | Giaquinto与Batoni较晚一代来到Rome；保留群体主语开放及相对年代，不换算为具体年份。 |
| `st-fm-2ed-l174-185-19-innocent-xi-quotation` | 第二版导言L185 | Innocent XI `cand-3808`已识别；引文所指“艺术资金”政策范围未映射为有界对象，且主张来自未名引述者。 |
| `st-fm-2ed-l174-185-22-employment-implication` | 第二版导言L185 | Clement XI `cand-3022`为推论主体；寻求就业的画家群体未具名，不推为具体委托或雇佣关系。 |
| `st-fm-2ed-l190-196-04-poerson-war-claim` | 第二版导言L192 | Poerson书信称战争阻止外国人前往Rome `cand-3126`；战争主体保持开放，Europe不是目的地。 |
| `st-fm-2ed-l190-196-05-poerson-patronage-groups` | 第二版导言L192 | 外国赞助者与意大利男性均为宽泛群体端点；保留Poerson的修辞性对照，不扩为个体交易或已证行为。 |
| `st-fm-2ed-l190-196-08-assumed-employment` | 第二版导言L193 | Clement XI `cand-3022`为Haskell推论中的行动者；“最好的艺术家”群体未具名，不能当作已记录合同。 |
| `st-fm-2ed-l190-196-09-selected-artists` | 第二版导言L193 | S. Clemente重新装饰事件`cand-3613`已识别；七名被选艺术家保留在参与者列表，群组端点未建模，不拆成七份委托。 |
| `st-chp2-secii-l118-125-paul-v-lifetime-monument` | 第2章p.41，L125 | Paul V `cand-0393`已识别；原文称其在世时有宏大纪念物，但未给作品名或有界作品组。后文Urban VIII陵墓只是比较语境，不作为Paul V作品端点。 |
| `st-chp2-secii-l118-125-sixtus-v-lifetime-monument` | 第2章p.41，L125 | Sixtus V `cand-1874`已识别；原文称其在世时有宏大纪念物，但未给作品名或有界作品组。后文Urban VIII陵墓只是比较语境，不作为Sixtus V作品端点。 |
| `st-chp2-secii-l118-125-urban-public-monuments` | 第2章p.41，L120 | Urban VIII `cand-0220`已识别；此句是对公众纪念物的一般性、带保留评价。同段另述Velletri铜像与元老院委托的大理石像，但未说二者穷尽该类别或将评价对应到其中任一件；对象端点保持开放，不推断Urban VIII委托了元老院雕像。 |
| `st-chp2-secii-l127-139-peretti-similar-plans` | 第2章p.42，L136 | Peretti `cand-1875`仍有身份问题；“similar plans”接续皇帝要求建Felice小堂和Magalotti为St Lawrence小堂积集石材，但未指明Peretti具体计划、作品或献堂对象；不把前两项移接。 |
| `st-chp2-secii-l71-78-marcello-searches-for-new-talent` | 第2章p.38，L77 | “new talent”是未界定对象的一般性搜寻目标；紧接的Galatea复制品个案在Haskell叙事中指向Pietro cand-0342，但不能将其并入这项一般习惯。 |
| `st-chp2-secii-l80-89-giulio-made-cardinal` | 第2章p.39，L86 | Giulio Sacchetti `cand-2313`已识别；任命主体及任命机关未说明，不推断为Urban VIII。 |
| `st-chp2-secii-l80-89-marcello-papal-treasurer` | 第2章p.39，L86 | Marcello `cand-2314`已识别；“papal treasurer”保留为职务表述，任职时间及任命主体未说明，不另造办公室实体。 |
| `st-chp2-secii-l80-89-pietro-requested-subjects` | 第2章p.39，L81 | Pietro `cand-0356`已识别；习惯性请求所涉及的具体赞助人和题材未具名。 |
| `st-chp2-secii-l80-89-sacchetti-influence-on-taste` | 第2章p.39，L87 | Sacchetti家族`cand-4452`已识别；“品味影响”的具体对象和范围未指明。 |
| `st-chp8-p238-note4-pictures-at-pisa-cabinet` | 第8章p.238注4，L446 | Pisa机构`cand-8048`所指图片可能为`cand-0874/0887`，也可能包括`cand-0885`；时间限定保留，Casini pp.42–50未独立查阅。 |
| `st-chp14-p353-bruhl-possessions-in-the-pictures` | 第14章p.353，L70–71 | 母题`cand-10293/10294`未逐一指配给`Maecenas` `cand-2597`或`Flora` `cand-2590`，亦未指配到具体住宅。 |
| `st-chp20-p403-alazard-commissioned-franceschini-picture` | 第二版后记p.403，L111–113 | 作品`cand-6888`及画家`cand-1066`已识别；实际委托人未具名，Colbert `cand-0800`及Strozzi `cand-2528`只记为经手人。 |
| `st-fm-pl-p64-private-collection` | 第14章p.364图版目录 | “Private Collection, London”未具名，保留开放端点；不创建虚构收藏实体。 |
| `st-chp15-p363-daniele-continued-patronage-partial` | 第15章p.363–364，L35及L39 | Daniele继续赞助当代艺术家，但未列受助者或具体委托；不造未具名艺术家实体。 |
| `st-chp2-sec-viii-l3-7-no-new-squares-recall-urban` | 第2章p.61，L3 | Urban VIII 的公共纪念/城市空间比较未具名具体广场；保留负面纪念断言，不把它解释成未建广场，也不补造对象端点。 |
| `st-chp2-secvii-l38-54-fn-p60-7b-ferri-attribution-suggested` | 第2章p.60注7，L50 | 经Haskell转述的Ferri归属仅为建议；注释未明确指挂毯组还是cartoons/designs，保留作品主语开放，不确认为作者关系。 |
| `st-chp2-seciv-l139-152-barberini-wealth-and-revival-interpretation` | 第2章p.56，L143 | Haskell将Barberini财富消费与对未具名“oldest families”的损害相连；未界定家族群组或具体机制，端点保持开放。 |
| `st-chp2-seciv-l139-152-joust-pastiche-receives-delighted-approval` | 第2章p.56，L140 | 原文报告对比武活动中封建风格仿古的赞赏，但未指明赞赏者，保持对象端点开放。 |
| `st-chp2-seciv-l139-152-palace-filled-with-art-and-treasures` | 第2章p.56，L144 | 原文称宫殿充满艺术品与珍宝，但未界定作品集合或具体对象，不推定完整收藏范围。 |
| `st-chp3-seci-l16-24-orders-social-integration` | 第3章p.64，L20 | 原文将耶稣会与其他宗教会集体描述为嵌入社会结构；保留条件语气，当前无有界社会对象候选。 |
| `st-chp3-seci-l26-33-church-decoration-synthesis` | 第3章p.65，L32–33 | 装饰依赖彼此冲突的力量之综合，但未指明单一有界对象；不从前后文选择赞助人或教堂。 |
| `st-chp3-seci-l26-33-families-superiority-legal-financial` | 第3章p.65，L27 | 家族优势由未具体化的法律和财务力量保障；不将对象缩减为单一征收权。 |
| `st-chp3-seci-l26-33-secular-princes-claims-first` | 第3章p.65，L30 | 世俗诸侯的主张优先，但未指明与之竞争的主张或艺术家；公爵夫人随后举例不能视为穷尽对象。 |
| `st-chp3-secii-l6-17-apse-mosaic-plan` | 第3章p.66，L8 | 覆盖Gesu后殿的马赛克规划者未具名；不据后文Jesuit施工叙述推定规划主体或委托关系。|
| `st-chp3-secii-l6-17-external-painter-exposed-jesuit-financial-weakness` | 第3章p.66，L11 | 文中称Jesuit另聘既有名望画家暴露财力不足，但画家未具名；不补造个体或具体委托对象。|
| `st-chp3-secii-l6-17-schemes-grandiose-while-alive` | 第3章p.66，L7 | Haskell称Farnese生前计划宏大，但未列具体计划对象；不将后文装饰项目全部并入。|
| `st-chp3-secii-l19-31-aquaviva-correspondence-raising-funds` | 第3章p.67，L29–30 | Haskell称Aquaviva书信经常涉及筹款；未指明具体信件或筹款事项，保留对象开放。|
| `st-chp3-secii-l19-31-shortage-funds-explains-limited-patronage` | 第3章p.67，L28 | Haskell以资金短缺解释Jesuit赞助有限；保留其因果解释，未把结果建模为有界对象。|
| `st-chp3-secii-l19-31-stefano-cycle-detail-and-explanations` | 第3章p.67，L22 | 每幅壁画附有刑罚说明；说明文本未具名或作为独立对象登记，保留开放端点。|
| `st-chp3-secii-l19-31-vitale-images-martyr-and-soldier` | 第3章p.67，L27 | S. Vitale壁画描绘未具名殉难者和受刑士兵；不补造人物身份或群组成员。|
| `st-chp3-secii-l19-31-vitale-subjects-mostly-torture` | 第3章p.67，L26 | Haskell称壁画主题几乎全与刑罚有关；保留主题端点未建模及范围限定。|
| `st-chp3-secii-l33-38-philip-attracted-cultivated-people-and-decorated-church` | 第3章p.68，L37 | Neri吸引“最有教养的人士”群体，成员未具名；不据相邻Roman捐助者或赞助群体补定成员。|
| `st-chp3-secii-l33-38-new-church-not-dependent-on-one-patron` | 第3章p.68，L38 | Chiesa Nuova建造与装饰“不完全”依赖单一全能赞助人，但未指明此赞助人；保留否定范围和开放对象。|
| `st-chp3-secii-l33-38-richeome-book-topic-paintings` | 第3章p.68，L34 | Richeome 1611年著作谈及S. Andrea与S. Vitale绘画，但绘画对象群未作为有界实体建模。|
| `st-chp3-secii-l33-38-richeome-focused-devotion-on-fresco-subject` | 第3章p.68，L35 | Richeome主张专注壁画题材并如布道般阅读；具体题材群端点保持开放。|
| `st-chp3-secii-l33-38-richeome-rejected-extravagant-ornament` | 第3章p.68，L34–35 | Richeome否定奢华装饰对虔敬的作用；装饰对象组不具名、不补造实体。|
| `st-chp3-secii-l74-81-florentine-families-competed-over-chapels` | 第3章p.72，L75 | 多个佛罗伦萨家族竞相装饰礼拜堂，但家族、礼拜堂身份与数量均未列明；对象端点保持开放。|
| `st-chp3-secii-l74-81-lanfranco-dome-model-for-later-artists` | 第3章p.72，L79 | Lanfranco穹顶壁画被称为后世艺术家的范本，但“艺术家”没有有界成员名单，不逐个补实体。|
| `st-chp3-seciv-l16-24-courtois-good-faith-test` | 第3章p.78，L22 | Courtois被要求证明诚意，但要求者未具名；不据相邻叙述推定为Goswin Nickel。|
| `st-chp3-seciv-l16-24-oliva-took-advantage-of-new-situation` | 第3章p.78，L24 | 保留Haskell关于Oliva利用“新局面”的推断；原文未把新局面界定为独立对象。|
| `st-chp3-seciv-l26-33-private-patron-painting` | 第3章p.79，L27 | Courtois受鼓励继续为私人赞助者作画，但鼓励者和赞助者均未具名；不补具体委托。|

第二章p.42的两条对象端点现指向来源界定、但成员与类型仍待定的群组候选`cand-11555`和`cand-11556`，因此不列入本表。相邻皇帝、Magalotti及Peretti的statement只作语境参照，不据此列成穷尽成员名册或逐人分配群组成员。

| st-chp4-sec-ii-p112-innocent-hostility | 第4章p.112 L158 | Barberini关联者未具名；cand-0198只代表Barberini家族，不能代替其关联者群体，保留开放。 |
| st-chp4-sec-ii-p112-innocent-hostile-to-cassiano-pursuits | 第4章p.112 L158 | Cassiano所欣赏的“pursuits”未指明为有界对象，保留开放，不将敌意改写为Innocent X对Cassiano本人的敌意。 |
| `st-chp4-sec-ii-p113-first-private-patron-influence` | 第4章p.113 L170 | “arts of his day”是宽泛影响对象，段内没有有界实体承接；保留Haskell的“probably”限定，不补造艺术群组。 |
| `st-chp4-sec-ii-p113-portrait-result-uncertain` | 第4章p.113 L169 | “the two men”所指及未完成肖像的作者、对象均未明确；不猜作Cassiano或Velasquez。 |
| `st-chp4-sec-ii-p113-poussin-french-clients` | 第4章p.113 L163 | Poussin为之工作的法国友人和客户未具名，不据此建立虚构群组。 |
| `st-chp4-sec-ii-p113-scholar-encouragement` | 第4章p.113 L169 | Cassiano鼓励的学者未列名或限定范围；保留关系候选，目标开放。 |
| `st-chp4-sec-ii-p113-taste-currents-fragment` | 第4章p.113 L170，续p.114 L173 | “currents of taste”未成为有界对象；跨页续文已链接，读完p.114后再判断是否能解析。 |
未发现应据原文新增而遗漏的具名、可独立识别端点；`candidate-backlog.csv`不存在。开放端点不补猜测，不写入`relations.csv`；身份问题交S3比对，关系成立与边类型交S6裁决。

### 递归引用完整性（最近专项快照）

最近一次递归引用专项复核覆盖12,704条statement及27,504条mention；当时12,704个statement_id均唯一，嵌套statement-ID引用6,297处、缺失目标0。后续S2写入已增加statement，当前表为13,032条statement、27,565条mention；上述专项计数不覆盖其后328条statement和61条mention。该次复核中`referent_status=unresolved`为0，`cross_reference_text_pending`与`footnote_text_pending`待决标记均为0；p.373 Sasso私人收藏statement及p.367雕像/资助statement互链已核正。保留10条有页图依据的mismatched状态（p.270、p.377）及第十四章p.359注4的1条orphan_unresolved，不强行回链。另有1个collection_type_pending=true（第八章p.224）及1条跨页清单predicate_status=partial，后者已链接至p.375续表。当前70条开放关系候选中59条已收入上表；另11条尚待逐项说明，须在S2交接前补齐。全书其他断言限定语与语义风险仍待终审。

### 引用锚点、书目匹配与候选类型待决

前次引文锚点全量复核覆盖12,690条statement：12,644条逐字匹配、46条统一空白后匹配、未匹配0。Hervey p.183 `cites` statement亦已通过批次检查。该专项全量锚点统计对应12,691条statement；当前表为12,997条，新增的306条尚未纳入同一全量锚点复核。175条第一章statement沿用01_CHP-1.md整章来源路径而segment_id指向规范分节来源；其引文和行号均能复现，整章副本不另计S0来源或覆盖。

第3章p.81注释`st-chp3-seciv-l48-56-enggass-citation`现在链接至本书书目`st-chp21-bib-l420-459-entry-17`，两者均指现有候选`cand-5243`。内部书目身份已确定，`bibliographic_identity_pending=false`；论文未独立查阅，不能据此声称已核验论文内容。

第8章p.224注释中的“Bologna (Plate 209)”已通过本书内部材料识别为Ferdinando Bologna的《Francesco Solimena》（Napoli, 1958）：书目p.416 entry 7与作者、题名、年份一致；本书自身图版目录将该画列为Plate 33a，因此209是被引书的图版号。正文候选`cand-7759`与书目候选`cand-7348`已互链，但保留为两个S2候选并新增S3身份对齐问题；被引书未独立查阅，replica的具体实物身份仍未核验。

第8章p.224注释仍有`collection_type_pending=true`：`cand-7761`为Scholz-Forni art collection，现行taxonomy没有collection类型，按规则保留空类型，不改成institution、archive或work。

全候选表有472行`suggested_type`为空（429条open、43条excluded）。该集合属于S3类型/身份判定输入；严格结构审计不证明空类型均已语义解决。需在S3按证据给出same/new/conflict/excluded/undecided决定；S2不提前登记KU。

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

## 第十四章p.349另一次拜访Voltaire的关系候选（2026-10-08）

原`st-chp14-p349-return-publish-newtonianismo`同时包含1736年底返意并在威尼斯、米兰之间停留约一年，以及“另一次短暂拜访Voltaire”和出版《Newtonianismo per le Dame》。现将行程收窄为返意与停留；出版断言沿用既有`st-chp14-p349-authored-newtonianismo`单独记录。新增`st-chp14-p349-another-short-visit-to-voltaire`，主语Algarotti（cand-0080）、宾语Voltaire（cand-2791），谓词`visited`，标为S2关系候选。它与同页先前在巴黎结识Voltaire并留居Cirey的statement分开；后一次拜访没有确切日期或地点，出版地点也不由“where”推定为米兰或威尼斯。

第349段的第二处Voltaire mention已存在（`m-chp14-p349-0007`，字符479:487），故未新增mention或候选。新增1条statement；p.349关系候选14条、14条端点齐全；全书关系候选2,531条、2,510条端点齐全、21条开放。严格阶段审计：1,019 KU、11,498 candidates、27,401 mentions、12,311 statements、832 segments；`s2_missing=[]`、`errors=[]`。原文行号与引文逐字核对通过；正式`relations.csv`未改。全书S2交接继续。

## 第十四章p.350正文及注1关系语义复核（2026-10-08）

将原`st-chp14-p350-youth-status-and-associations`拆为年龄/著作出版状态、Voltaire友谊与伦敦/巴黎社会成功、在威尼斯的财富/声望/关系网状态三项。Voltaire友谊依据“had already made friends with Voltaire”单列为关系候选；不与p.349记录的再次短访或Cirey留居混为一事。补录mention `m-chp14-p350-0069`，字符2509:2521，指向“royal master”所指的Augustus候选cand-0151；与p.349 cand-0148留给S3对齐。

对`st-chp14-p350-proposed-living-artist-commissions`补回Haskell所说的“这并非皇家主人所见”的视角限定，并明确其偏好内容未载；“皇家主人”指向前句Augustus of Saxony。将`st-chp14-p350-followed-historians`标为Algarotti—Muratori的方法承袭关系候选；将`st-chp14-p350-gallery-represent-history-and-schools`标为画廊内容方案关系候选。`st-chp14-p350-rediscovery-of-primitives`改为无人物主语的历史判断，并保留“虽非在Algarotti本人身上发生”的排除限定，不把该现象归因于他个人。

注1定位到档案候选`cand-10265`（1741-09-05致Bonomo的信，Treviso MSS. 1256）。将注1statement改为letter→Bonomo的`addressed_to`关系候选；新增正文statement记录该信由Algarotti执笔，并通过既有footnote ID连到注1。原件及馆藏目录未独立查阅。另在gallery-plan statement上登记3组S3身份问题：`cand-0056/0071/0072/0075`的Algarotti候选、`cand-0148/0151`的Augustus候选，以及`cand-9091/10222`的Dresden gallery候选；S2保持分立。

新增3条statement及1条mention，不新增候选。p.350共有9条关系候选，端点9/9齐全；全书关系候选2,536条、端点齐全2,515条、21条开放。严格阶段审计：1,019 KU、11,498 candidates、27,402 mentions、12,314 statements、832 segments；`s2_missing=[]`、`errors=[]`。全书S2交接仍在进行。


## 第十五章 p.364 Farsetti 段语义复审（2026-10-09）

本轮完成 p.364 L39–41 及 p.363→364 跨页句复审。正文21条 statement、30条 mention；拆分并新增8条 statement，新增事件候选 cand-11525。举报档案仅按 Haskell 注释登记，未独立查阅。将“This”解析为举报事件；撤销将“the collections”同时绑定铸像与绘画两项候选的重复映射，所售藏品仍不具名；“the property”范围未定。Tommaso 家族记述与候选 cand-10443 的身份待 S3，书籍／手稿收藏 cand-10465 类型未定；侄舅关系和其他有据关系保留为 S2 候选。

8条 p.364 关系候选中7条端点齐备、1条因诗歌／演说未指名而开放；Canova 的 Venice 表述不推断出生或居住，同代人的文化复兴愿望不表述为实现结果，新式公共服务模式不专属归给 Memmo。印刷校正只记于 S2，未改 S0。严格表审计 errors=[]、s2_missing=[]；全库12,417个 original_quote 锚点中12,371项精确、46项经空白归一化匹配、0项未匹配。

当前全库：1,019 KU；11,510 candidates；27,432 mentions；12,478 statements；2,711条 S2 关系候选（2,680条两端齐备、31条开放）。覆盖表832段中678段 reviewed/complete、154段 excluded/complete、0段 queued/partial；覆盖与迁移状态不代表全书语义复审完成。p.367复审后下一步按书序为p.368：`chp-15:15_CHP-15_sec_ii:l38-47`。

## 第十五章 p.364 Andrea Memmo 段语义复审（2026-10-09）

对照 `CHP-15.pdf` 物理页4复核第十五章 p.364 L3–4及合并注释L43–56中注3–6。新增标题mention `m-chp15-p364-memmo-title-0001`（ANDREA MEMMO，cand-1642，0:12）；将1729年出生与未具名家族出身拆开，将Lodoli的主要影响、Memmo传播其思想、宣称受其影响拆为三条，将政治改革热情与打破同辈贵族隔绝拆开。既有statement ID保留；新增4条statement；本段现18条statement、25条mention。8条关系候选端点齐备；S2关系候选总数增加2条，没有新增候选、KU或正式关系。

印本页图确认建筑句脚注标号为5（S0 OCR作6），并确认`thé`应为`the`；校读写入S2，不改S0。注3、5分别指向第12、11章，注4引Molmenti/Torcellan，注6为Tabacco pp.32 ff.；仅保留引用路径，未声称独立查阅。p.364末句已由p.365 L7闭合；续句statement现描述Memmo继续热衷并书写一系列恋情，保留与p.365注1的链接，移除误列入正文的Brunelli作者/作品候选。

全库现12,421条statement、27,425条mention、2,667条S2关系候选（2,640条端点齐备、27条开放）；引文锚点12,375条精确、46条空白归一、0条未匹配。严格阶段审计通过。下一段为p.365 `chp-15:15_CHP-15_sec_ii:l6-12`；全书S2交接仍未完成。

## 第十五章 p.372 语义复审（2026-10-09）

p.372对照物理页12复核正文与注1：正文13条statement、注释3条、17条mention、6条关系候选（6/6端点齐备）。从首轮数据净增4条statement，拆分Querini对异教遗址的个人意义与同时代学者对比、Maffei收藏与记录、Querini政治退隐与重返理想过去，并单列Winckelmann比较及“洞见较少”的Haskell限定。Renier竞选续句、政治妥协、胸像掷向Altar of Furies、Rousseau影响、1796年心脏安葬和注释中的馆藏推定/匿名传闻均保留来源归属；没有新增候选、mention、KU或S6关系。

严格审计`errors=[]`、`s2_missing=[]`；12,566条引文锚点中12,520条精确、46条空白归一、0条未匹配。全书S2尚未交接。下一处按书序重新复核第十六章p.373 `chp-16:16_CHP-16_intro:l3-14`及注释L69–71。详见[第十五章过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)与[章节结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-15.md)。

## 关系候选语义复核游标（2026-10-10）

十二批专项复核累计为775条statement补入relation_candidate=true；当前3,584条显式候选中3,570条statement具有两个端点ID、14条仍缺端点；另有4,471条双端statement仍未分类。最近两批将收藏／宫殿断言按原文可界定的对象组拆分：Ghibbesio的画作和素描登记为作品组cand-11566；Maffeo宫殿旧大师画作登记为cand-11567；Giustiniani室内其他画作登记为cand-11568，并将威尼斯高文艺复兴大师登记为类型未定的创作者集体cand-11569。所有作品标题、数量及完整成员仍未知。Carracci集体cand-4318、威尼斯大师集体cand-11569及绘画收藏cand-4313的类型仍未定；相关记录仅为S2候选，不生成S6正式边。此前22条关系候选覆盖绘制、题献、委托范围、友谊、引荐、赞助及作者关系；10条谓词已统一方向或表达（painted→creator_of、patronage_relationship_reported→patronized、authored_by_reported→authored_by）。

11条收藏／宫殿原始断言现均完成对象粒度复核：先前2条直接指向既有雕塑群组`cand-4314`与绘画收藏`cand-4313`；Ghibbesio对应作品组`cand-11566`；Maffeo宫殿的五位旧大师对应作品组`cand-11567`，各自保留creator_of候选并以location_of连接宫殿；Giustiniani室内的Carracci、威尼斯大师与Cambiaso画作对应作品组`cand-11568`，新增room location与collection part_of候选。威尼斯大师群体`cand-11569`与Carracci集体`cand-4318`仍无可用类型；集合对象`cand-4313`也未定类型。关系候选的端点ID齐备不代表类型已通过S6。原文未给出的作品标题、数量、成员和所有权均未补造。下一步继续分类其余4,463条双端statement；另有612条footnote_citation statement缺少完整双端候选（subject-only 59、object-only 495、两端皆无58），需回到原文补判。不得据已处理的92条宣称全书脚注引用已完成。

## 第5章 Rosa 书信脚注关系规范化（2026-10-10）

本轮复核8条p.142–145脚注引用：6条改指向有日期的archive书信候选，另2条继续指向刊本，不强连至某封信。新增6个候选、6条精确mentions和12条作者／收信人S2关系候选；所有引用关系均以《赞助人与画家》为主语。书信收信人、日期、刊本页码及OCR/印本差异均保留证据边界，原信和引文版本未独立查阅。

写后全库11,554 candidates、27,486 mentions、12,663 statements；3,604条relation_candidate=true（3,590条双端齐备、14条开放），4,463条双端statement仍待分类。缺少完整双端候选的脚注引用仍为612条。严格表审计errors=[]、s2_missing=[]；全量同步闭合通过（5/5检查，结构契约130/130）。语义交接未完成，下一步继续全书S2交接审计。

## 第七章p.197 Exeter收藏艺术家关联候选分类（2026-10-10）

9条`collector_artist_association_in_city`均标为来源限定的S2关系候选。Liberi条目明确说Exeter在威尼斯购买其作品；其余8名艺术家位于按城市组织的省略式列举中，只保留收藏叙述中的关联，不推断具体购买、作品或交易对象。未新增候选、mention、statement或S6正式关系。

写后全库11,554 candidates、27,486 mentions、12,663 statements；3,613条relation_candidate=true（3,599条双端齐备、14条开放），4,454条双端statement仍待分类。严格表审计`errors=[]`、`s2_missing=[]`；全量同步闭合5/5通过、结构契约130/130。全书S2交接未完成。

## 第六章p.155注释1–5及全书当前校验（2026-10-10）

p.155注1、2、3、5及注4续注已逐条规范为7条《赞助人与画家》指向具体archive候选的`cites`记录；注3拆分匿名1783年目录与Corti短述，注4续注拆分Pascoli与Bellori两项引文。另将注4“十七世纪艺术文献多有Colonna赞助记载”单列为Haskell的范围性`footnote_claim`，标记非关系；正文注4回链及续注L154/L110定位同步更新。复用既有候选与mentions，无新增candidate/mention，不写S6正式关系。写前statement SHA-256 `acbd74bfa6cd7a43905209a4bfbc04bd95d20ef33087e31d332d070751b2f471`；恢复副本为`04-knowledge/tables/book-statements.jsonl.bak-s2-chp6-p155-footnotes-20261010`；写后SHA-256 `cdb1614f56310ef6f222e6524b0922aa2c77c1573d7eea5d5ebeb1265feb2edb`。当前statement总数12,690；显式关系候选3,791（3,775条双端、16条开放）；双端未分类4,312条；`footnote_citation` 652条、其中638条缺少至少一端。

本轮全量闭合在本次写回前通过：9/9检查、303 tests与2 subtests通过；写回后的定向及全量复核见过程记录。严格表审计写前为`errors=[]`、`s2_missing=[]`。覆盖表仍为832段全部complete（678 reviewed、154 excluded）；这不代表全书语义交接完成。

## 第六章p.155正文关系候选复核（2026-10-10）

对照L103–109，将12条端点清楚、原文直接支持的关系断言标为S2 relation candidates：Bernini重建宫殿；Colonna宫殿由Filippo与Girolamo重建/装饰；Lorenzo与Maria的婚姻；Palestrina领地售予Barberini家族；Lorenzo作为Colonna家族赞助人、增添家族绘画收藏、聘用罗马艺术家；Grimaldi在其宫殿绘制风景；Lorenzo对题材的限定偏好及其对风景装饰风尚可能产生的影响；Resta对风景画家与bamboccianti的批评。所有断言保持Haskell/Resta来源归属、时间/语气限定和原候选端点；未解决的同名宫殿候选不合并，未从被动语态补出委托人。无candidate/mention新增，无S6正式关系。

写前SHA-256 `cdb1614f56310ef6f222e6524b0922aa2c77c1573d7eea5d5ebeb1265feb2edb`；恢复副本`04-knowledge/tables/book-statements.jsonl.bak-s2-chp6-p155-body-relations-20261010`；写后SHA-256 `c4b77ef59f53b5c729614d99192805731678fa294ef79ece043d74c180d337e7`。当前12,690条statement；relation candidates 3,803条（3,787条双端、16条开放）；双端未分类降至4,300条。

## 书前版权页与CIP关系候选复核（2026-10-10）

按`segments.jsonl`书序，对版权页/CIP中的12条最早未分类双端statement完成语义裁决并标为S2关系候选：出版者、两个出版地、版权方、版权法条款引文、印制地、Library of Congress CIP来源、作者目录项及4条目录主题项。严格保留题名页、版权通知和CIP各自的陈述范围；主题项只记为目录元数据，不扩展为对全书内容的穷尽判断；Yale University（版权方）与Yale University Press（出版者）保持区别。无候选、mention或statement新增，无正式S6边。写前SHA-256 `c4b77ef59f53b5c729614d99192805731678fa294ef79ece043d74c180d337e7`；恢复副本`04-knowledge/tables/book-statements.jsonl.bak-s2-front-matter-title-page-relations-20261010`；写后SHA-256 `7ce9a416dbdfb05bd7d8a338296dc4df6a7930882ab6bc0751315ddf9933ca4e`。当前关系候选3,815条（3,799条双端、16条开放），双端未分类4,288条。


## 第二版序言关系候选复核（2026-10-10）

按来源L5–17裁决9条双端statement：7条关系候选涵盖作者对传记参考书的推荐、Chatto/Windus及Norah Smallwood的支持、John Nicoll对新版本的建议与协助、Haskell与Tim Munby/Ben Nicolson的友谊和咨询，以及Oxford/November 1979题记；另将两条“报告某人去世”记录标为非关系，因为当前端点是报告者和被报道者，而非死亡事件本身。作者自称“I”的主语依据statement现有`speaker=Haskell`，不伪造原文mention。无候选、mention或statement新增。写前SHA-256 `7ce9a416dbdfb05bd7d8a338296dc4df6a7930882ab6bc0751315ddf9933ca4e`；恢复副本`04-knowledge/tables/book-statements.jsonl.bak-s2-front-matter-second-ed-preface-relations-20261010`；写后SHA-256 `9289f6713a93a062c41e900c7804c41a759f80ee277ad27315abd042d417f623`。

## 第一版序言术语与章节范围statement裁决（2026-10-10）

按L4–8裁决11条双端statement：4条作为S2候选保留Baroque阶段在Urban VIII时期的高峰、其延续至威尼斯共和国终结，以及书前两节关于罗马的范围关系；其余7条为作者的术语定义、标题评价、方法论、材料选择、叙述取舍或历史解释，不作为端点之间的关系。均保留Haskell归属与章节/概念语境。无新增candidate、mention或statement。写前SHA-256 `9289f6713a93a062c41e900c7804c41a759f80ee277ad27315abd042d417f623`；恢复副本`04-knowledge/tables/book-statements.jsonl.bak-s2-front-matter-first-ed-preface-scope-20261010`；写后SHA-256 `d6a03e97f88f43139db93d9064bd8c8dcab4cf1c124f8219abab71b6f2ec19d9`。当前全库12,690条statement，3,826条relation_candidate=true（3,810条双端、16条开放），双端未分类4,268条。
