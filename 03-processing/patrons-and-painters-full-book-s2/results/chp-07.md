# 第七章全书 S2 当前结果

## 2026-10-25：p.190 独立语义复核

对照印刷页190及跨页续句所在p.191扫描图，逐条复核p.190对应的43条当前statement。当前OCR订正和p.190→p.191续句链接均准确；没有需改写的claim、候选端点或statement结构，本次未写回S2表。逐条结果见[独立复核记录](../process/s2-independent-review-chp7-p190-20261025.md)。此页的43条局部审读暂不并入全书汇总分子，待全书statement ID与来源版本台账核平后再汇总。

任务：`patrons-and-painters-full-book-s2`。第七章共55个规范段；当前覆盖账本显示47段reviewed/complete、8段excluded/complete，queued与partial均为0。当前覆盖状态以`04-knowledge/tables/s2-coverage.csv`为准，全书状态见`04-knowledge/results/patrons-and-painters-full-book-s2.md`，逐项判断及执行记录见同任务`process/stages.md`。

截至2026-10-21，当前ID独立逐条语义复核为1,099/1,244；这不同于上述段级coverage状态，也不表示第七章已接收。已按顺序完成p.200正文、Plate 32a–32b图版簇及p.201正文；下一游标为p.202 `chp-7:07_CHP-7_sec_v:l57-60`，随后核对p.200脚注 `l62-76`。

## 候选表面提示裁决（2026-10-08）

在47个已审段上复扫候选表面定位器，10,489个既有类型词形形成40条启发式提示。逐项核对S0原文、候选、mentions及statement后，17条映射为精确mention，23条因泛称、普通语义或索引候选错配不写入。新增候选3个：cand-11486为Cardinal Aldobrandini所藏两件Titian作品相关收藏（类型待定）；cand-11487为Charles Le Brun提供给Domenico Guidi凡尔赛雕塑组的设计图稿（work）；cand-11488为Cardinal Chigi 1664年访巴黎事件（event）。三者的身份或具体范围按原文证据保留未决。

更新11条statement的`mentioned_candidate_ids`；另将Shaftesbury“English patronage”statement对象从England地理候选修正为cand-0969术语候选。未改关系表或未决关系端点。第七章p.180注4经复裁后按顺序拆为两条来源归属的地点关系候选：cand-6773 Inspiration du Poète→Louvre cand-3254，以及 cand-6774 Diana and Endymion→Institute of Arts, Detroit cand-7072。依据是正文作品名、注4馆藏名和目录页码pp.46/65的对应次序；原注未使用“respectively”，所引目录页未独立查阅。S2保留Haskell归属，尚未写入正式关系表。

受控脚本`process/chp7_candidate_surface_prompt_reconciliation.py`默认dry-run，按输入哈希、提示分区、原文跨度、候选外键、mention重叠与statement前态校验后再写入；写后重扫的23条提示与no-write清单完全一致。恢复副本位于`%TEMP%\pnp-s2-chp7-surface-prompts-20261008-090555\`。完整跨度、逐条no-write理由、plan/script哈希和表哈希见`process/stages.md`。

`python -X utf8 scripts/audit_tables.py --strict-stage`通过：全库1,019 KU、11,467 candidates、27,168 mentions、12,255 statements；`s2_missing=[]`、`errors=[]`，覆盖678 reviewed/complete、154有理由排除、0 queued、0 partial。两条既存enrichment `source_ref`警告未变。候选表面提示只用于定位审查，不证明召回率或语义质量。下一步按书序处理第八章：56个reviewed段上当前有112条提示。

## 第7章脚注引用候选规范化（2026-10-10）

本章20条具有双端候选的`footnote_citation` statement已规范为`cites`候选；缺端引用仍待处理。详见[全书阶段记录](../process/stages.md)。

## p.197 Exeter收藏艺术家关联候选分类（2026-10-10）

全段9条按城市列举的`collector_artist_association_in_city`均标为S2关系候选。Liberi一项明说购买；Pasinelli、Piola、Assereto、Castelli、Maratta、Brandi、Gaulli及Calandrucci为省略式列举。候选只记录Haskell在Exeter收藏叙述中的来源限定关联，不把后8项扩写为具体购买或作品，不生成S6正式边。全库关系候选3,613条（3,599端点齐备、14开放），双端未分类statement 4,454条；严格审计`errors=[]`、`s2_missing=[]`，同步闭合5/5、结构契约130/130。全书S2仍未交接。

## 2026-10-13：p.169–179关系候选语义分类

按源序完成12个正文/注释段的283条statement分类，其中256条为关系候选、27条为非关系。修正p.169–179中人物、作品、地点、匿名群组等关系端点；p.175、p.176同步校正作品mention候选映射。p.179的端点修正以p.180续文和本页明确语境为依据；未把未实现的雕塑计划写成已完成，也未把匿名投诉补成具名主体。没有新增KU或S6正式关系。第七章覆盖账本仍为47段reviewed/complete、8段有理由排除；当前关系分类游标已到p.180正文L129–138。逐段决定与全库审计见[全书过程记录](../process/stages.md)及[当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。

## 2026-10-13：p.182–188关系候选分类

按书序完成七段共176条新分类（168条关系候选、8条非关系）；p.186另保留并说明3条此前已有的true判定。逐页true/false总量为p.182 23/1、p.183 21/2、p.184 18/0、p.185 29/1、p.186 20/1、p.187 29/0、p.188 31/3。修正Borghese casino、Aurora fresco、匿名群体、Mazarin、Charles I picture collection及Bernini后续方案等端点；p.182至p.189间的引文和跨页statement续接已互链。p.188印本以CHP-7.pdf物理页26复核。未新增KU或S6正式关系。写后全库relation_candidate true/false/unset为8,284/3,391/2,496；严格表审计errors=[]、s2_missing=[]，关系一致性硬错误为0。下一段为p.189 L243–257，有28条statement待分类；全书S2交接尚未完成。详细裁决见[过程记录](../process/stages.md)。

## 2026-10-15：p.198开放端点复核

印本CHP-7.pdf物理页36确认S0转录内容。7条开放关系候选拆为12条原子关系候选；新增`cand-12335`–`cand-12340`、6条精确mention和5条statement。分开记录English milordi访画室、付高价及邀请艺术家赴英；Shaftesbury理论、Exeter收藏史角色、Haskell对Choice of Hercules的判断、那不勒斯知识圈、为英国友人购画、Closterman劝阻信推论，以及对Holland与France的政治态度。复用既有精确England mention `cand-8983`。有据端点关闭6项；高价陈述因原文没有具体交易或对象继续开放。注2和Haskell归属限定随拆分保留；无新增KU或S6正式边。

当前全库为12,318 candidates、26,512 mentions、15,126 statements；relation_candidate true/false/unset为10,387/4,739/0。开放端点470（仅缺object 293、仅缺subject 64、两端皆缺113），本段仅剩高价陈述开放。严格阶段表审计`errors=[]`、`s2_missing=[]`；关系一致性硬错误为0。下一待复核段为p.199 `chp-7:07_CHP-7_sec_iv:l89-95`，3条开放statement。全书S2交接仍未完成。

## 2026-10-15：p.199第IV节开放端点复核

物理页37核对后，将画作无法表达的复杂构思连接到前页已明确的“Vice and Virtue”主题候选`cand-7249`，并链接p.198相关statement。将Shaftesbury强调的艺术教化作用与他所延伸出的“良善社会必然产生良好艺术”命题拆为两条来源限定statement；后一命题保留Haskell“较不可取”的评价。新增`cand-12341`–`cand-12343`三个term候选、3条精确mention和1条statement；分别表达艺术的教化作用、社会与良好艺术的因果命题及绘画的情感感染力。Haskell对Shaftesbury非正式写作的判断仍有归属限定，不补造具体文献或画作。本段3条原开放statement对象均已有依据，关闭后本段无开放端点；无新增KU或S6正式关系。

写后全库为12,321 candidates、26,515 mentions、15,127 statements；relation_candidate true/false/unset为10,388/4,739/0。开放端点467（仅缺object 290、仅缺subject 64、两端皆缺113），分布于165段。严格阶段表审计`errors=[]`、`s2_missing=[]`；关系一致性硬错误为0。下一段为p.199第V节 `chp-7:07_CHP-7_sec_v:l3-7`，2条开放statement；全书S2交接仍未完成。

## 2026-10-15：p.199第V节开放端点复核

将收藏者可转向的Bologna、Venice、Naples连接到本段前文所述“provincial centres”候选`cand-2066`；不将英德收藏者个体分配到具体城市。六位画家与Maratta、Trevisani的比较性“European favourites”判断仍开放：没有可复用的特定艺术家群实体或明确受众，逐人拆边会改变原文的集体比较范围，故保留原理由并记`no_delta`。本段无新增候选、mention或statement。

当前全库12,321 candidates、26,515 mentions、15,127 statements；relation_candidate true/false/unset为10,388/4,739/0。开放端点466（仅缺object 289、仅缺subject 64、两端皆缺113），分布于165段。本段剩余1条开放关系候选。严格阶段表审计`errors=[]`、`s2_missing=[]`；关系一致性硬错误为0。下一段为p.201 `chp-7:07_CHP-7_sec_v:l42-55`，6条开放statement。全书S2交接仍未完成。

## 2026-10-15：p.201 开放端点复核

以印本物理页43核对p.201。新增`cand-12344`–`cand-12347`四个来源限定候选，分别表示Venetian绘画风格、Galli-Bibiena未具体指名的戏剧演出、Vienna兴起所涉军事结果及Eugene绘画收藏散佚；补4条精确mention。将Eugene的私人赞助人评价连接到Europe范围；Mattielli与Parodi分别接到同一雕塑群的制作statement；散佚事件与注2“Carlo Emanuele III购得大量藏画”互链，同时保留购藏范围不完整的限制。原6个开放端点全部关闭；无新增KU或S6正式关系。

写后全库12,325 candidates、26,519 mentions、15,128 statements；关系候选true/false/unset为10,389/4,739/0。开放端点460条，分布于164段；本段无开放端点。严格阶段表审计通过，关系一致性硬错误为0。全书S2交接未完成。详细记录见[全书过程记录](../process/stages.md)。

## 2026-10-15：p.202 开放端点复核与漏提及修正

以印本物理页44核对p.202。原句明确表达“画家，或至少他们的画作”的替代关系，故保留标量object端点开放及候选`cand-7344`、`cand-7345`，不把二选一写成两条并行事实。补入遗漏的来源城市群提及`m-chp7-p202-v-origin-cities`（候选`cand-12005`，跨度`[1067,1093)`），使该候选与“more richly endowed cities”原文跨度对应。无新增候选、statement、KU或正式关系。

全库12,325 candidates、26,520 mentions、15,128 statements；开放端点460条，分布于164段。严格阶段表审计`errors=[]`、`s2_missing=[]`；关系一致性审计硬错误为0。下一待复核段按书序为第8章p.203 `chp-8:08_CHP-8_sec_i:l3-12`，有1条开放statement。全书S2交接仍未完成。详细判断见[全书过程记录](../process/stages.md)。
## 2026-10-20：p.199 定向语义修正

复核已覆盖的p.199正文与注释，纠正一项将Shaftesbury去世时间误设为人物—作品关系的statement（改为单主语、非关系断言），并清理Sweetman脚注claim中的内部背景摘要。页图校读仍与原OCR分开保存；该修复不增加S2独立复核覆盖，也未生成S6正式边。详见全书过程记录 `stages.md`。
