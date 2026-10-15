# 第八章全书 S2 当前结果

任务：`patrons-and-painters-full-book-s2`。状态：此前statement分类已处理至p.236；本轮开放端点按书序复核至p.225，下一待复核项为`st-chp8-p238-note4-pictures-at-pisa-cabinet`（p.238注4，1条开放statement）。此前statement分类的下一未分类项仍在p.237 `chp-8:08_CHP-8_sec_ii:l311-325`，11条statement中3条未分类。以上均不等于全书召回验收或S3交接完成。全书状态见[当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)，裁决证据见[过程记录](../process/stages.md)。

## 当前处理

- 覆盖账本：56段`reviewed/complete`、5段`excluded/complete`，无queued或partial；这是覆盖登记，不替代statement语义裁决。
- 本轮按源序复核p.233–236共44条既有statement，新增63条statement。四段合计107条，77条`relation_candidate=true`、30条false；p.234新增2个候选和1条mention，无新增KU或S6正式关系。
- p.233（L271–279）：27条（18 true、9 false）；保留Haskell推测和被动施事的不确定性，拆开赞助、雇佣、委托、展览、评价及modello续句。
- p.234（L281–289）：34条（25 true、9 false）；拆开Fumiani方案和审稿、Cassana履历与作品、Cook肖像评价及Ratti/Langetti报告；两处引句修复恢复S0原文契约。
- p.235（L291–301）：25条（20 true、5 false）；拆开Giordano绘画/到访/服务、两位未名画家、Ricci委托/购藏/运输/延期及装饰和毁损；脚注1–6按印本回链。
- p.236（L303–309）：21条（14 true、7 false）；拆开Haskell推论与Gherardi报告、风格判断与Ferdinand反应、Ricci画组/合作者/引语；校正引句行锚。
- 严格表审计：1,019 KU、12,076 candidates、28,120 mentions、14,630 statements；`s2_missing=[]`、`errors=[]`。关系一致性硬错误均为0；两条既存enrichment source_ref警告及通用语义复核提示仍在。

下一statement分类段为第八章p.237 `chp-8:08_CHP-8_sec_ii:l311-325`：11条statement中3条未分类。全库剩余1,519条未分类statement；全书S2交接审计仍在进行。

## 2026-10-15：p.203–204 开放端点语义复核

p.203物理页1复核`st-chp8-p203-bolognese-doctors-picture-owners`后保持object开放。来源只说Balbi、Beccari和Malpighi各自拥有画作，没有指定作品，也没有说明三人共用同一收藏；不将分散所有权压成一个共有作品组。既存印本校读将OCR的“great - Marcello”确认为“great Marcello”，没有进一步表格改动。

p.204物理页2中，“the arts”是“Naples lawyers”支持行为的明确概念宾语。新增term候选`cand-12348`及mention `m-chp8-p204-lawyers-support-arts`，连接`st-chp8-p204-naples-lawyers-supported-arts`。此概念端点不代表具体作品、机构或项目。本段关系候选端点齐备；无新增KU或正式S6关系。

当前全库12,326 candidates、26,521 mentions、15,128 statements；关系候选true/false/unset为10,389/4,739/0，开放端点459条，分布于163段。严格阶段表审计`errors=[]`、`s2_missing=[]`，关系一致性硬错误为0。下一待复核段为p.211 `chp-8:08_CHP-8_sec_i:l84-96`。全书S2交接仍未完成。详见[全书过程记录](../process/stages.md)。

## 2026-10-15：p.211 脚注作者端点复核

对照物理页9，将脚注中Manini与Salvini对del Rosso兄弟简要履历的来源归属拆成两条原子statement，分别连接`cand-7505`与`cand-7506`并互链。没有声称两人合著某一已识别文献，也没有将某份账户映射到特定兄弟；题名、日期和版本仍未知。本段开放端点关闭，无新增候选、mention、KU或正式关系。

当前全库12,326 candidates、26,521 mentions、15,129 statements；开放端点458条，分布于162段。严格阶段表审计`errors=[]`、`s2_missing=[]`，关系一致性硬错误为0。下一待复核段为p.213 `chp-8:08_CHP-8_sec_i:l108-118`。全书S2交接仍未完成。详见[全书过程记录](../process/stages.md)。

## 第八章 p.211 联姻对象群组关系端点复核（2026-10-09）

对照印刷p.211页图及规范段`chp-8:08_CHP-8_sec_i:l84-96`，将原句“a series of ingenious marriage alliances with the best families”解释为具体联姻中的来源界定匿名家族群。新增无类型、status=open候选`cand-11559`和mention `m-chp8-p211-080`，字符跨度`[453,470)`；将statement `st-chp8-p211-del-rosso-marriage-alliances`的object连接到群组。未推断成员、数量、婚配对或日期；不新增KU或正式S6关系。写后全书11,537 candidates、27,470 mentions、12,644 statements；S2关系候选2,808条，2,785端点齐备、23条开放。严格阶段审计通过（`errors=[]`、`s2_missing=[]`）；全量同步闭合303 passed、2 subtests passed，9/9检查及结构契约130/130通过。全书S2交接仍在进行。详见[过程记录](../process/stages.md)及[全书当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。

## 2026-10-15：p.213 Nomé别名断言分类修正

核对物理页11后，将`st-chp8-p213-nome-alias-and-inventory-description`从关系候选改为非关系身份断言。`Monsù Desiderio`已映射到Nomé的同一人物候选；库存中的“Lorenese”另由`st-chp8-p213-nome-inventory-described-as-lorenese`记录，两项判断已互链。清除本statement重复存储在qualifiers之外的顶层claim字段，保留原文及OCR拼写校读。本段开放端点归零；无新增候选、mention、statement或KU。

当前全库12,326 candidates、26,521 mentions、15,129 statements；关系候选true/false/unset为10,389/4,740/0，开放端点457条，分布于161段。严格阶段表审计`errors=[]`、`s2_missing=[]`；关系一致性硬错误为0。下一待复核段为p.214 `chp-8:08_CHP-8_sec_i:l120-124`。全书S2交接仍未完成。详见[全书过程记录](../process/stages.md)。

## 2026-10-15：p.214 Baglioni家族端点复核

将家族进入贵族身份的宾语连接到已有term候选`cand-8108`（Venetian nobility as a social estate），并新增mention `m-chp8-p214-040`“the nobility”。“bought their way”保留为Haskell措辞，不推断具体交易、个人成员或准确授予日期；Venice Baglioni家族与Perugia候选`cand-4279`保持身份待对齐。本段开放端点关闭；无新增候选、statement、KU或正式关系。

当前全库12,326 candidates、26,522 mentions、15,129 statements；关系候选true/false/unset为10,389/4,740/0，开放端点456条，分布于160段。严格阶段表审计`errors=[]`、`s2_missing=[]`；关系一致性硬错误为0。下一待复核段为 `chp-8:08_CHP-8_sec_i:l126-157`（3条开放statement）。全书S2交接仍未完成。详见[全书过程记录](../process/stages.md)。


## 2026-10-15：p.215 开放端点语义复核

对照物理页13及p.216续页，新增7个来源限定候选、13条mention。关闭施工起始、古典主义制度与偏远城市、相对失败与谈判、收藏发展与特殊赞助机制、收藏群与罗马绘画、Haskell致谢Dora Coggiola共6条statement端点。p.216“these”回指谈判系列；续页评价不改判为关系。委员会是否实际委托外来画家仍是假设性表述，具体有影响力的收藏也未指明，故两条关系继续开放。无新增KU或正式关系。

当前全库12,343 candidates、26,546 mentions、15,129 statements；开放端点443条（仅缺object 277、仅缺subject 62、两端皆缺104），分布于160段。严格阶段审计`errors=[]`、`s2_missing=[]`；关系一致性硬错误为0。下一待复核段为`chp-8:08_CHP-8_sec_ii:l21-35`（7条开放statement）。全书S2交接仍未完成。详见[全书过程记录](../process/stages.md)。


## 2026-10-15：p.216 开放端点语义复核

对照物理页14，新增两个未定类型的来源群组候选：Storer在Bergamo有密切联系的主要家族，以及受托绘制四幅作品的米兰地区艺术家群；再为“第一阶段装饰于1659年前完成”新增event候选。关闭Storer—家族群、四幅作品—艺术家群及装饰计划—完成事件共6条端点映射；不将集体来源断言拆成未证实的个人画家—单幅作品配对。治理者与全城是否均为“they”的主体仍不清，故保留一条statement开放。

当前全库12,346 candidates、26,549 mentions、15,129 statements；开放端点437条（仅缺object 275、仅缺subject 58、两端皆缺104），分布于160段。严格阶段审计`errors=[]`、`s2_missing=[]`；关系一致性硬错误为0。下一待复核段为`chp-8:08_CHP-8_sec_ii:l69-76`（1条开放statement）。全书S2交接仍未完成。详见[全书过程记录](../process/stages.md)。


## 2026-10-15：p.217 开放端点语义复核

对照物理页19，在Haskell明确标为“most probable”的解释中，将“Bergamasque susceptibilities”作为term候选`cand-12369`，精确mention跨度为`[2462,2490)`，连接Liberi裸像与地方文化敏感性的解释性关系。保留作者归因和不确定性，不称作已证实的社会事实。本段开放端点归零，无新增KU或正式关系。

当前全库12,347 candidates、26,550 mentions、15,129 statements；开放端点436条（仅缺object 274、仅缺subject 58、两端皆缺104），分布于160段。严格阶段审计`errors=[]`、`s2_missing=[]`；关系一致性硬错误为0。下一待复核段为`chp-8:08_CHP-8_sec_ii:l78-84`（2条开放statement）。全书S2交接仍未完成。详见[全书过程记录](../process/stages.md)。


## 2026-10-15：p.218 开放端点语义复核

对照物理页20，将句中未具名“patrons”与“Various artists”分别建为来源限定、未定类型群组候选`cand-12370`、`cand-12371`。前者用于记录Ferri与赞助群体关系降温，不等同于指定委员会；后者记录自荐画家群，不拆成个人候选。两条关系端点均已闭合，延误原因与成员身份仍未知，无新增KU或正式关系。

当前全库12,349 candidates、26,552 mentions、15,129 statements；开放端点434条（仅缺object 273、仅缺subject 57、两端皆缺104），分布于158段。严格阶段审计`errors=[]`、`s2_missing=[]`；关系一致性硬错误为0。下一待复核段为`chp-8:08_CHP-8_sec_ii:l112-124`（1条开放statement）。全书S2交接仍未完成。详见[全书过程记录](../process/stages.md)。


## 2026-10-15：p.221 开放端点语义复核

对照物理页23，`st-chp8-p221-abraham-picture-approved`继续保留approver开放。句子使用被动表达“met with approval”，后续整体委托虽指向Melanconici，但没有足够依据确定此处的批准者具体是committee还是教堂治理者。记`no_delta`，不补写行动者或新增对象；数据表未变。

当前库表仍为12,349 candidates、26,552 mentions、15,129 statements；开放端点434条（仅缺object 273、仅缺subject 57、两端皆缺104），分布于158段。全库最近一次严格阶段审计`errors=[]`、`s2_missing=[]`，关系一致性硬错误为0。下一待复核段为`chp-8:08_CHP-8_sec_ii:l372-461`（p.223注释中的1条开放statement）。全书S2交接仍未完成。详见[全书过程记录](../process/stages.md)。


## 2026-10-15：p.223 注4 开放端点语义复核

对照物理页25，为Count Orlando提供的Raimondo相关存世材料建立未定类型候选`cand-12372`，并连接到Haskell的致谢statement。原文未指明材料内容、媒介或数量；不推断它就是本注稍后提及的妻子1726年手稿。本段开放端点关闭，无新增KU或正式关系。

当前全库12,350 candidates、26,553 mentions、15,129 statements；开放端点433条（仅缺object 272、仅缺subject 57、两端皆缺104），分布于158段。严格阶段审计`errors=[]`、`s2_missing=[]`；关系一致性硬错误为0。下一待复核项为`st-chp8-p225-n9-haskell-collection-visit`（p.225注9）。全书S2交接仍未完成。详见[全书过程记录](../process/stages.md)。


## 2026-10-15：p.225 注9 作者访问记录

对照物理页27，为Haskell访问Buonaccorsi收藏的第一人称报告补入主体`cand-9423`，并添加“I”的精确mention `m-chp8-p225-n9-haskell-visit-author`（跨度`[3560,3561)`）。收藏对象`cand-7765`不变；该记录属于作者自述，不是独立复查。本段端点关闭，无新增candidate、KU或正式关系。

当前全库12,350 candidates、26,554 mentions、15,129 statements；开放端点432条（仅缺object 272、仅缺subject 56、两端皆缺104），分布于158段。严格阶段审计`errors=[]`、`s2_missing=[]`；关系一致性硬错误为0。下一待复核项为`st-chp8-p238-note4-pictures-at-pisa-cabinet`（p.238注4）。全书S2交接仍未完成。详见[全书过程记录](../process/stages.md)。
