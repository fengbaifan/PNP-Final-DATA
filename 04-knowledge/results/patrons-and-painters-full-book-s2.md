# 《赞助人与画家》全书 S2 语义处理、S3 身份对齐与交接结果

### 本轮进度与后续工作（2026-10-25）

**当前快照（2026-10-25，第8章 p.216 Padre Massimo端点批次后）：** S0已处置832段（678 complete、154 excluded）。S2为15,362 statements／26,840 mentions；统一独立复核9,617（62.60%，未接收）；p.190的43条页内复核仍待按当前statement ID与来源版本核平，p.189五条、p.191三条及p.216本批修改/新增三条当前statement版本待独立复核，均未计入分子。按candidate_id首条alignment的主决定计，S3为12,426项：same=2,062、new=5,094、conflict=9、excluded=104、undecided=5,157；另有26项跨来源decision差异待按来源与身份语义核对。S4已映射2,152/5,094条new，待登记2,942条；未登记new候选组中1,230组触及当前关系端点（对应1,235条组成员映射；按端点组类型计：term 457、archive 265、work 195、place 165、event 82、institution 65、person 1）；KU共2,935。S5字段13,471条（1,634 unverified）。S6累计裁决1,409项（803 formal、490 pending、116 rejected）；当前relation_candidate=true为10,577，历史裁决台账与当前statement版本分母仍差1，不据此报告完成率或余数。relations.csv为2,068条（2,035 formal、33 pending；含结构性边）。另有337条关系statement至少缺一个S2端点候选ID（subject-only 45、object-only 220、both 72）。candidate-backlog.csv有44条记录（12 completed、32 undecided，严格审计pending=0）。严格表审计errors=[]、s2_missing=[]；关系审计的broken target、invalid relation_type、missing inverse、weak evidence及unbaselined generic evidence-backed均为0。S2尚未接收，S3–S6未全书收口；S7、知识发现与页面均未启动。
**本批完成：第8章 p.216 Padre Massimo作品端点与逐项S6裁决。** `cand-1576`由S3 `undecided`定点改为来源局部`new`，只登记索引名/正文称谓，不补全历史全名；沿用`cand-7653`作品组及`cand-7643`南耳堂地点组，三者登记为3个KU并新增6条来源字段。将委托句原statement改为人物—作品`creator_of`，另拆出委员会`commissioned_by`及南耳堂`intended_for`两条statement。9条关系候选逐条裁决为6 formal（`rel-2063`–`rel-2068`）和3 process-only pending；后两项“they”施事继续开放，先前altar pictures不造未命名作品端点。7张受影响卡定向渲染并复预览无差异；严格表审计`errors=[]`、`s2_missing=[]`，关系端点/类型/证据阻断均为0。修改的原statement及新增两条statement待独立S2复核，不增加全书复核分子。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp8-p216-massacre-20261025)。
**本批完成：第7章 p.191 Bernini自画像素描端点登记。** `cand-6958`／`aln-7134` 由 `undecided` 定点裁为来源局部 `new`，登记一张作品KU；Del Carpio、Bernini、Domenico复用既有人物KU。修正原取得关系方向，正式裁为1条 `acquired_by`、1条 `created_by`、1条 `has_subject`（`rel-2060`–`rel-2062`）；Domenico仅保留为原文所称转移来源，不推断出售或此前所有权，也不认定任何存世版本。新增3条Haskell来源字段。三张受影响卡定向渲染并写后复预览无差异；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断均为0。修订的原statement及两条拆分statement待独立复审，不计入全书S2复核分子。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-ch7-p191-bernini-self-portrait-20261025)。
**本批完成：第7章 p.189 Preti 拟赠 Louis XIV 的寓意肖像S3沿用及S4/S5/S6登记。** 沿用 `cand-6937`／`aln-7113` 的来源局部 `new` 组，新增1个作品KU及1条Haskell来源字段；S2将作者、肖像对象、拟赠意图拆分，并把法西敌对行动改为叙述背景，不建event→work边。4项关系候选逐条formal为 `rel-2056 created_by`、`rel-2057 has_subject`、`rel-2058 intended_gift_to`、`rel-2059 sold_by`；不表示赠礼已交付，也不推断买家或出售去向。五条当前S2 statement因版本更新待重新独立复核，不计入统一复核分子。三张卡定向渲染并复预览无差异；严格表审计、关系一致性、规则漂移检查通过。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp7-p189-preti-louis-xiv-portrait-20261025)。

**本批完成：第16章 p.373 注1 Longhi—Sasso肖像关系端点复用。** S4登记触发S3定点复核：`cand-10599`、索引候选`cand-1426`与章前候选`cand-3999`指向同一既有作品卡`units/works/alessandro-longhi-g-m-sasso`，前两项由`new`改为`same`并完成2条既有KU映射。S5 no_delta；两条S6 statement分别formal复用`rel-0397 created_by`与`rel-0398 has_subject`，在原边补入精确p.373注1 statement来源，不新增重复关系行。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s6-chp16-p373-longhi-sasso-portrait-20261025)。

**S2分章审读：** 第七章p.190的43条statement已逐条对照印本扫描复核，未发现需改写项；该页局部复核仍待按当前statement ID与来源版本核平后并入统一台账。p.189五条当前statement因内容或关系候选状态更新、p.191三条statement因纠正与拆分、p.216本批一条修订及两条新增statement，均须重新独立逐条复核，尚未计入全书分子。下一项沿书序处理p.192，并在推进中回收这些待复审项。见[p.190逐条记录](../../03-processing/patrons-and-painters-full-book-s2/process/s2-independent-review-chp7-p190-20261025.md)及[p.191本批记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-ch7-p191-bernini-self-portrait-20261025)及[p.216关系端点批次](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp8-p216-massacre-20261025)。

**下一步规划：** 继续按书序从p.192推进S2逐条独立审读，同时按当前statement ID与来源版本回收p.189、p.191、p.216等待复核版本；从1,230个未登记关系端点组中优先选可解除正式关系阻断的对象，完成每批S4登记后立即逐条做S6裁决；对337条缺端点关系按证据定向补齐或保留pending，并优先核实影响正式关系的S5关键字段（当前unverified 1,634条）；S4/S5/S6达到全书收口条件后再准备S7，知识发现与页面仍待用户明确启动。

**本批完成：第1章 p.12 Ferri Sant’Agnese 彩色稿候选复用及关系裁决。** `cand-11835` 从 S3 `new` 改为 `same`，复用 `cand-3192`／`units/works/ferri-sant-agnese-modello`；彩色稿与穹顶壁画 `cand-3191` 保持分立。关联 statement `st-chp1-secii-l62-71-03` formal复用既有 `rel-0684 created_by`，关系证据入口补入statement ID；不新建KU、字段或重复关系边。两张受影响卡定向渲染并复预览无差异；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断均为0。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s6-chp1-ferri-sant-agnese-modello-reuse-20261025)。

**本批完成：第13章 p.336 Piazzetta 为 Platnerus《Institutiones Chirurgicae》设计的卷首图。** 沿用 `cand-10004` 的 S3 `new` 组登记作品KU；创作者候选 `cand-1907` 复用既有 `units/persons/piazzetta`。新增5条Haskell p.336来源支持字段；S6候选 `st-chp13-p336-piazzetta-designed-platnerus-frontispiece` formal裁为 `rel-2055 designed_by`。未把Haskell对书的评价当作作品属性，也未推断完整版次、出版信息或存世印张。两张卡写后复预览2/2无差异；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断均为0。S2 statement／mention及统一复核台账未改。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp13-p336-piazzetta-frontispiece-20261025)。

**本批完成：第10、13章《苏珊娜与长老》《圣殿献礼》及Chatsworth跨章身份与关系端点。** `cand-2177` 裁为来源局部 `new` 组并映射作品KU；`cand-9308` 沿用既有 `new` 组映射地点KU。`cand-2175` 同时连接第10章p.280与第13章p.342注5，外部目录提示存在多个版本，但当前证据不足以确认两处同名画是否同一对象，故保留 `undecided`，不把其映射到Chatsworth画作。新增6条有据S5字段（4条作品、2条地点）。4条关联S6候选最初裁为1 formal（`rel-2053 located_at`）及3条process-only pending；随后完成版画端点 `cand-10208` 的S4登记、新增5条Haskell来源字段，并将相应S6 statement改为formal（`rel-2054 created_by`）。目前另2项关于 `cand-2175` 的关系仍pending；另一条此前pending候选的去向详见跟进裁决。三张相关卡定向渲染并写后复预览无差异；严格表审计和关系一致性阻断检查通过。详见[主批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp10-chatsworth-susanna-20261025)及[版画端点跟进](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp13-p342-monaco-engraving-no84-20261025)。


**本批完成：第9、10章都灵宫廷与 Sebastiano Ricci 跨章端点。** 将索引候选 `cand-2184` 的类型由work纠正为person，S3判为same并复用Ricci人物KU；沿用 `cand-8273` 的institution new组，登记都灵宫廷来源局部KU，不与城市Turin或House of Savoy合并。新增3条Haskell `source_backed` 字段；两条跨章雇佣statement均formal并共用 `rel-2052 employed_by`，不推定职位、聘期或委托数量。两张卡定向渲染并复预览无差异；严格表审计与关系一致性五类阻断检查通过。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp9-chp10-turin-court-ricci-20261025)。

**本批完成：第16、17章 G. A. Armanni人物组、Armanni–Sasso通信与1789年书信端点。** `cand-0119` 从 `undecided` 裁为来源局部 `new` 人物组，保留首字母，不与Vincenzo Armanni合并；`cand-10615` 沿用既有 `new` 档案组并映射到单封信KU。复用Sasso、Poore、两卷通信及Seminario Patriarcale既有KU。新增9条S5来源字段；4条本批关系候选裁为3 formal、1 rejected，另有两条已有档案定位关系继续pending。新增7条关系表记录，其中3条对应本批formal S6决定、4条为书信集与单封信的结构性边。五张受影响卡定向渲染后复预览无差异；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断为0，规则漂移检查为0。未查阅档案原件或外部人物规范记录。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp16-chp17-ga-armanni-20261025)。

**本批完成：第9、14章 Tiepolo《亨利三世受迎》壁画跨章身份组、modello与雅克马尔-安德烈机构。** 将 `cand-8367` 与 `cand-2604` 从 `undecided` 裁为同一 `new` 身份组；modello `cand-10356` 保持独立作品，机构 `cand-8358` 映射至机构KU，共4个候选映射到3个KU。补1条第9章p.255壁画mention，S5新增8条来源字段。5条关系候选逐项决定为4 formal、1 pending；两条创作者断言共用 `rel-2041`，另加`rel-2042`、`rel-2043`；脚注地点候选记为`rel-2044` pending，建筑地点列入`bl-0044`待S1/S3/S4。3张新卡定向预览及渲染通过；严格表审计与关系一致性阻断检查通过。S2统一复核分子不变。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp9-chp14-contarini-henri-iii-fresco-20261025)。

**本批完成：第8章 Ricci 皮蒂宫小室壁画组、毁坏的《艺术寓意》与图版39草图。** 为 p.235–236 和注2补40个来源锚定mention及1条尚未独立复核的草图—壁画S2关系statement。S3将8项判为来源局部 `new` 并完成S4，3项判为 `same` 并复用现有作品KU；`cand-7966`、`cand-7959`、`cand-8010` 保持 `undecided`，分别进入 `bl-0041`–`bl-0043`。S5新增25条书内 `source_backed` 字段。20项S6决定为13 formal、6 pending、1 rejected；正式关系表新增14条边（`rel-2027`–`rel-2040`）。14张相关卡预览后定向渲染，写后字节核验通过；表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断均为0。S2复核分子仍为9,617。本批过程记录同时揭示S6累计分母与当前 `relation_candidate` 标记有6项差异，须先核平再报告剩余量。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-ch8-ricci-pitti-room-20261025)。

**本批完成：第8章《Madonna delle Arpie》与 Ricci《Crucifixion》跨章端点。** 索引候选 `cand-2362` 判为既有画作 `same`，正文人物mention改挂至 `cand-2361`；沿用 `cand-7862` 的作品 `new` 组登记《Madonna delle Arpie》，并将 `cand-7957` 判为来源限定的 Ricci 委托作品 `new` 组，新增2个KU。两个卖方／画廊对象继续 `undecided`，分别保留在 `bl-0039`、`bl-0040`。新增8条书内 `source_backed` 字段；7项S6候选裁为4 formal、3 pending，购藏双重叙述合并为一条边。六张受影响卡定向渲染并复预览无差异；严格表审计与关系一致性检查通过。逐项依据见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-ch8-madonna-delle-arpie-ricci-20261025)。

**本批完成：第5、8章马萨涅洛起义事件端点。** 延用 `cand-1559`／`aln-1894` 的 S3 `new` 身份组登记 event KU `units/events/revolt-of-masaniello-1647`，与同名 Cerquozzi 作品分开。新增3条 Haskell `source_backed` 字段；两条跨章关系候选分别裁为1 formal（`rel-2020 visualizes`）和1 process-only pending（不把 Roomer 遇险误记为参与起义）。事件与作品卡定向渲染并写后复预览2/2无差异；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断均为0。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp5-chp8-masaniello-revolt-1647-20261025)。

**本批完成：第9、16、21章两封 Swajer 往返信及 Urbani de Ghelthof 1879 年出版物。** 沿用三个互相独立的 S3 `new` archive 身份组登记3个 KU；两封信分别连接既有人物KU，并各以 `part_of` 关系正式记录其书内刊载位置（第19、32页）。新增20条 Haskell 来源 `source_backed` 字段；四条 S2 关系候选逐项裁为2 formal、2 pending，其中绘画端点仍未识别、收藏权属主张保留待证。关系表新增8行（5条结构边、2条S6正式边、1条S6待证边）；7张受影响卡片渲染并写后复预览无差异。严格表审计及关系一致性检查通过。未查原信、刊本或被引页。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp9-chp16-chp21-swajer-urbani-1879-20261025)。

**本批完成：第4章 Paolo Giordano II《Rime, e Satire》档案端点。** 延用 `cand-5533`／`aln-5714` 的 S3 `new` 身份组登记一个 archive KU；第4章 p.96 注5与第21章 p.433 题名形式不同，保留 “Rime, e Satire”／“Rime e Satira”，不声称已查原刊本。新增8条书内 `source_backed` 字段；3条 S6 候选逐项裁决为1 formal（`rel-2011`，`authored_by`）和2 pending（风格谓词未受控；文学史家未具名且端点未定）。新档案卡及人物卡定向渲染、写后核验通过。严格表审计 `errors=[]`、`s2_missing=[]`；关系一致性五类阻断均为0。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-paolo-giordano-ii-rime-e-satire-archive-20261025)。

**本批完成：第5章Azzolini、S. Salvatore in Lauro与1701展览。** S3将Cardinal Azzolini对应到Decio Azzolino Junior；`cand-6052`教堂和`cand-11942`展览各自登记，合计新增3个KU和10条`source_backed`字段。`cand-11941`五幅匿名画组因不等同于单件作品或已知艺术组合，继续`undecided`并进入`bl-0038`。6条关联S6均有明确去向（6 pending；其中地点候选记为`rel-2010`）。另补2条mention锚点、校正4条脚注印刷页字段。三张卡均定向预览；仅1701展览卡写入1条待证关系展示，写后字节核验通过。严格表审计`errors=[]`、`s2_missing=[]`；关系一致性五类阻断均为0。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp5-salvatore-azzolini-1701-20261025)。

**本批完成：第3章 Richeôme《La peinture spirituelle》档案端点组。** 沿用 `cand-5024` 既有 S3 `new` 组，登记为 archive KU `units/archives/la-peinture-spirituelle-1611`；第3章叙述与第21章书目支持作者、题名、Lyon和1611年。新增5条书内 `source_backed` 字段；3条相关S6候选分别为1 formal（`rel-2009`，`authored_by`）和2 pending（题献关系超出现行 archive 域值域；绘画组候选 `cand-12315` 边界未定）。定向渲染新 archive 与 Louis Richeôme 人物卡，写后复预览无差异；严格表审计与关系一致性检查通过，导出测试4项通过。未查原书、被引页或外部目录。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-ch3-richeome-la-peinture-spirituelle-20261025)。

**本批完成：第8、9、21章 Vincenzo da Canal 人物端点组。** 沿用 `cand-7781` 的既有 S3 `new` 决定并登记为一个 source-local person KU；第8、9章引注与第21章完整书目责任形式支持跨章身份映射。新增1条书内 `source_backed` 姓名字段，并根据书目行新增结构性 formal `authored_by` `rel-2008`（archive → person），不并入S2关系候选决定分母。人物与 Da Canal 文献 KU 分开；不外推生平，不主张外部身份核验或被引页已读。人物卡与既有书目卡定向渲染及写后复预览2/2无差异。严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断均为0，导出测试4项通过。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-ch8-ch9-ch21-vincenzo-da-canal-20261025)。

**本批完成：第17章印刷页381、383 科雷尔档案端点组。** 沿用4个既有S3 new档案组，为paper、1787年致总督信、1468/10书内档案定位组、免除市民卫队通信完成4项S4映射和4张双语卡，新增12条书内source_backed字段。6条S6候选均有去向：4 formal（rel-2003至rel-2006）、2 pending（其中read_paper_in_1768因无准确受控谓词不写关系边；paper与1468/10的part_of保留rel-2007待证）。四张卡定向渲染并写后复预览无差异；另校正622条跨行mention的CRLF/LF表示与end_char（保留start_char、S0原文及26,789条总数），不计入S2统一独立复核。严格表审计errors=[]、s2_missing=[]，关系一致性五类阻断均为0。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp17-correr-archival-endpoints-20261025)。


**本批完成：第2章印刷页37 圣比比亚娜端点组。** 沿用 `cand-4441` place 与 `cand-4442` work 的既有S3 `new`身份组，完成2项S4映射、2张新卡和5条书内 `source_backed` S5字段；将雕像创作与教堂预定安置拆为独立S2关系statement，并为重建工程补一条地点statement。10项相关S6均有去向：6 formal（`rel-1997`–`rel-2002`）、3 pending、1 rejected。五张受影响卡定向渲染并写后复预览无差异；严格表审计`errors=[]`、`s2_missing=[]`，关系一致性五类阻断均为0。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp2-p37-s-bibiana-endpoints-20261025)。

**前批完成（Giustiniani跨章术语）：** 沿用 `cand-4337` 的既有 S3 `new` 身份组，登记一个来源局部术语 KU 并新增6条书内 `source_backed` 字段；四条直接关系候选均 pending，理由分别为两条文献端点身份未定、两条 person→term 观点缺少准确受控谓词。详见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp2-chp4-giustiniani-eclecticism-20261025)。

**后续工作规划（按当前任务优先级）：**

1. **先推进1,232个关系直接端点的S4登记。** 当前按类型为term 457、archive 265、work 197、place 165、event 82、institution 65、person 1；共1,232组／1,237条组成员映射。按类型与相邻章节分组，优先解除正式关系端点缺口；每批同步核对S3身份组、S5关键字段和S6候选。只因登记或新证据需要时重开S3，不对5,159个未决项全量强判。
2. **同批闭合端点关联的S5与S6。** 对每批新登记端点补足会影响身份、类型、关系方向或证据范围的关键字段，并将关联关系候选逐条裁为formal、pending或rejected。地点/保管、原件未读、端点未识别或谓词不受控时保留具体pending条件，不用临时弱边填数。
3. **按端点缺失类型处理337条关系候选。** 分为仅缺subject 45、仅缺object 220、两端均缺72；来源足以识别对象时，补S2候选与mention后走S3→S4并回到S6。缺证时保留待证去向，不把关系叙述文本本身当端点。
4. **以关系价值定向补1,634条未验证S5字段。** 先看会改变端点身份、类型、正式关系或证据边界的字段；有来源依据再转为 `source_backed`，否则保留 `unverified` 与具体缺口。按受影响卡定向预览、渲染及复核。
5. **核平S6台账的6项差异。** 历史分母10,578与当前`relation_candidate=true`的10,572项相差6项；按statement ID对照关系候选标记、状态变更和历史裁决，核平后再计算余数，继续逐条完成全书S6。当前累计1,393项（790 formal、487 pending、116 rejected），仍不能据分母差直接推算余数。
6. **继续分章推进S2独立语义复核。** 统一台账原快照为9,617/15,356；本轮第七章p.190另审43条，尚待按当前statement ID和来源版本核平后汇总，暂不重算全书剩余数。逐条审语义并记录修订、重复、失效或新增；章节局部复核与机械校验不冒充全书独立接收。下一项沿书序处理p.191续页。
7. **达到阶段门槛后再准备S7。** S2台账核平并完成独立语义接收；S3所有候选有可追溯决定或具条件的待证去向；可登记的new完成S4；关键S5字段已证实或明确缺口；S6逐条闭合且剩余pending均有具体解除条件。知识发现和页面仍待用户明确启动。

**提速方式：** 以共同来源页、身份组和关系端点价值编批；只预览、渲染本批受影响卡片，并运行必要表审计。CI矩阵的执行时长与语义审读是不同成本，不通过删减Python版本门禁制造项目进度。

**当前快照与第2章 p.58 Bernini临时剧场及《L’Inondazione del Tevere》批次（2026-10-25）：** `cand-4819` 由 `undecided` 改判 `new` 并登记来源限定的临时剧场地点；`cand-4821` 保留 `new`，将实体类型与身份组由 archive 更正为 work。未界定的剧目组 `cand-4820` 与未识别的匿名见证档案 `cand-4824` 保持 `undecided`，分别记入 `bl-0035`、`bl-0036`。新增2个KU、2条S4映射、5条source-backed字段；S2新增5条statement。11项S6候选逐条有去向：6 formal（`rel-1967`–`rel-1972`）、5 pending。5张受影响卡定向渲染并写后复预览无差异。严格表审计 `errors=[]`、`s2_missing=[]`；关系一致性五类阻断均为0。批后S2为15,348 statements／26,787 mentions，统一独立复核9,617/15,348（62.66%，未接收）；S3 same=2,054、new=5,076、conflict=9、excluded=103、undecided=5,184；S4已映射2,090/5,076条new、待登记2,986条，其中1,268条触及直接关系端点；KU共2,875。S5字段13,257（1,634 unverified）；S6已裁决1,285/10,564（726 formal、449 pending、110 rejected），余9,279；`relations.csv`共1,972条（1,948 formal、24 pending）；`candidate-backlog.csv`共36条（12 completed、24 undecided，严格审计pending=0）。本段原有20条statement中17条未变，3条修订及5条新增共8条仍待独立语义复核，不计入统一复核分子。详见[本批身份与逐项裁决](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp2-p58-inondazione-20261025)。

**当前快照与第2章 p.59 两封书信及 Lumbroso 书目端点批次（2026-10-25）：** `cand-4943`、`cand-4944` 沿用各自既有 S3 `new` archive 组并登记为两张书信 KU；`cand-4946` 定点由 `undecided` 改判 `same`，映射至第21章唯一对应的 Lumbroso 1874 书目项及既有 KU。新增9条 `source_backed` 字段；第2章 p.59 n.2/n.3 两条 `cites` 候选 formal 裁决为 `rel-1965`、`rel-1966`。3张受影响卡定向渲染后复预览无差异；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断均为0。批后 S2 为15,343 statements／26,787 mentions，统一独立复核9,617/15,343（62.68%，未接收）；S3主决定12,426（same 2,054、new 5,075、conflict 9、excluded 103、undecided 5,185；另有26个跨来源decision不一致候选）；S4已映射2,088/5,075条 `new`、待登记2,987条，其中1,270条仍触及直接关系端点；KU共2,873。S5字段13,252条（1,634 `unverified`）；S6已裁决1,274/10,559（720 formal、444 pending、110 rejected），余9,285；`relations.csv`共1,966条（1,942 formal、24 pending）；`candidate-backlog.csv`共34条（12 completed、22 undecided，严格审计 pending=0）。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp2-p59-letters-20261025)。

**当前快照与第3章／第21章 Baumgarten 跨章端点批次（2026-10-25）：** 沿用 `cand-5494` 的既有 S3 `new` 组 `archive-group-e5c8b64933ba`，登记1个 archive KU；根据第21章书目新增4条 source_backed 字段，第3章脚注 `cites` 候选 formal 裁决为 `rel-1962`。Haskell 来源卡与新卡定向渲染，复预览2/2无差异；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断均为0。批后 S2 为15,343 statements／26,787 mentions，统一独立复核9,617/15,343（62.68%，未接收）；S3 主决定12,426（same 2,053、new 5,075、conflict 9、excluded 103、undecided 5,186）；S4 已映射2,084/5,075条 `new`，待登记2,991条，其中1,274个未映射候选触及直接关系端点；KU共2,869。S5字段13,235（1,634 `unverified`）；S6已裁决1,270/10,559（716 formal、444 pending、110 rejected），余9,289；`relations.csv`共1,962条（1,938 formal、24 pending）；`candidate-backlog.csv`共34条（12 completed、22 undecided，严格审计 pending=0）。第2章 sec. iv 的多作品地点复合 statement 及第一／第二幅《耶路撒冷陷落》的指代仍待定点修订，本批未据此新增关系。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp3-baumgarten-20261025)。

**第2章引注与第21章书目跨章身份、S4/S5/S6批次（2026-10-25）：** 保留4个既有文献 `new` 组，新增 Roger Hinks 来源限定人物组并复用 Aldo De Rinaldis 既有 KU；“M. Rosi”作者身份仍待证，记入 `bl-0034`。新增5个 KU、35条有来源字段、4条 formal `cites` 与3条目录支持的结构性 `authored_by`；后者不计入 S6 的 S2 候选分母。严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断为0，7张目标卡写后复预览无差异。当前 S2 为15,343 statements／26,787 mentions，统一独立复核9,617/15,343（62.68%，未接收）；S3 主决定12,426个候选：same=2,053、new=5,075、conflict=9、excluded=103、undecided=5,186；S4 已映射2,083/5,075条 `new`，待登记2,992条，其中1,275条触及直接关系端点；KU共2,868。S5字段13,231（1,634 `unverified`）；S6已裁决1,269/10,559（715 formal、444 pending、110 rejected），尚余9,290；`relations.csv`共1,961条（1,937 formal、24 pending）；`candidate-backlog.csv`共34条（12 completed、22 undecided，严格审计 pending=0）。详见[本批逐项过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp2-citations-20261025)。

**第20章 pp.396–397 圣彼得大殿交叉部端点收束（2026-10-25）：** 将前批暂缓的 `cand-10861` 从 `undecided` 定点裁为来源限定 `new`，登记1个 place KU；p.396 对 crossing 的明指及 p.397 引文闭合支持其为建筑内部空间，精确边界仍未确定。相关 S6 `st-chp20-p396-lavin-bernini-crossing-open` 从 pending 改裁 formal，新增 `rel-1954 has_subject`。新卡与 Lavin 档案卡定向渲染、写后核验，复预览2/2无差异。严格表审计 `errors=[]`、`s2_missing=[]`；关系一致性五类阻断均为0。批后 S2 未变（15,343 statements／26,781 mentions；统一独立复核9,617/15,343，62.68%，未接收）；S3 same=2,053、new=5,074、conflict=9、excluded=103、undecided=5,185；S4 已映射2,078/5,074条 `new` 候选，待登记2,996条，其中1,279条仍触及直接关系端点；KU共2,863。S5字段13,196（1,634 `unverified`）；S6已裁决1,265/10,559（711 formal、444 pending、110 rejected），未裁决9,294；`relations.csv`共1,954条（1,930 formal、24 pending）。当前全库卡片预检 `files_to_write=564`；本批只处理直接受影响卡片。详见[本批逐项过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp20-p396-crossing-space-resolution-20261025)。

**第20章 p.396 后记／第21章书目跨章端点批次（2026-10-25）：** 沿用5个既有 S3 `new` 档案组登记5张 archive 卡，并将书目责任者 Silvia Carandini 定点裁为来源限定 `new`、Maurizio Fagiolo 的全名补入既有身份组；跨章 Hibbard 候选裁为 `same → units/persons/howard-hibbard`。共新增7个 KU、7条 `new` 映射、18条 source_backed 字段；另新增1条 same 映射。5条 S2 关系候选逐条有去向：3 formal（rel-1951–rel-1953）、2 pending；另按书目责任字段新增6条 formal `authored_by`（rel-1945–rel-1950），这些结构性记录不属于 S2 关系候选分母。14张受影响卡定向预览、渲染并写后核验。严格表审计 `errors=[]`、`s2_missing=[]`；关系一致性 `broken target=0`、`invalid relation_type=0`、`missing inverse=0`、`weak evidence=0`、`unbaselined generic=0`。当时全库卡片预检计划写回578个文件（含本批14张）；本批只渲染受影响的14张。批后 S2 为15,343 statements／26,781 mentions，统一独立复核9,617/15,343（62.68%，未接收）；S3 same=2,053、new=5,073、conflict=9、excluded=103、undecided=5,186；S4 已映射2,077/5,073条 `new` 候选，待登记2,996条，其中1,279条仍触及直接关系端点；KU共2,862。S5字段13,195（1,634 `unverified`）；S6已裁决1,265/10,559（710 formal、445 pending、110 rejected），未裁决9,294；`relations.csv`共1,953条（1,929 formal、24 pending）；`candidate-backlog.csv`为33条（12 completed、21 undecided，严格审计 pending=0）。详见[本批逐项过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp20-p396-archives-cross-chapter-20261025)。

**第15章 p.371 Querini 直接关系端点批次（2026-10-25）：** 沿用7个既有 S3 new 身份组，登记3个术语、4个作品；4条端点明确的关系裁为 formal（rel-1941–rel-1944），5条因缺精确谓词或对象身份待定而留在过程级 pending。坐者、未具名大公及归因性审美观点均保留原有不确定性。10张相关卡完成预览、定向渲染和写后复预览。严格表审计 errors=[]、s2_missing=[]；关系一致性五类阻断均为0。批后 S2 为15,343 statements／26,781 mentions，统一独立复核9,617/15,343（62.68%，未接收）；S3 same=2,052、new=5,072、conflict=9、excluded=103、undecided=5,188；S4 已映射2,070/5,072条 new 候选，待映射3,002条，其中1,284条仍触及直接关系端点；KU共2,855。S5字段13,177（1,634 unverified）；S6已裁决1,260/10,559（707 formal、443 pending、110 rejected），未裁决9,299；relations.csv共1,944条（1,920 formal、24 pending）。candidate-backlog.csv仍为33条（12 completed、21 undecided，严格审计 pending=0）。详见[本批逐项过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s6-chp15-p371-querini-endpoints-20261025)。

**第9章 pp.270–273 威尼斯教会端点跨章登记与裁决（2026-10-25）：** 沿用7个既有 S3 `new` 身份组并完成7条 S4 映射；定点复核 Tiepolo 穹顶壁画组 `cand-8550` 与《信仰的胜利》`cand-8732` 后维持二者 `undecided`（no_delta），不把单件与复数壁画范围强行合并或拆为两个 new。17条 S6 候选均有去向：3 formal（`rel-1938`–`rel-1940`）、12 pending、2 rejected；仅正式边进入 `relations.csv`。9张受影响卡逐卡预览后定向渲染，5个文件写后字节核验通过。严格表审计 `errors=[]`、`s2_missing=[]`；关系一致性五项阻断均为0。当前 S2 为15,343 statements／26,781 mentions，统一独立复核9,617/15,343（62.68%，仍未接收）；S3 same=2,052、new=5,072、conflict=9、excluded=103、undecided=5,188；S4 已映射2,059/5,072条 new 候选，待映射3,013条；KU共2,844。S5字段13,177（1,634 `unverified`）；S6累计1,244/10,559（703 formal、431 pending、110 rejected），余9,315；`relations.csv`共1,940条（1,916 formal、24 pending）；`candidate-backlog.csv`仍为33条（12 completed、21 undecided，严格审计 pending=0）。详见[本批逐项过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s6-ch9-p270-p273-venetian-church-endpoints-20261025)。

**第9章 p.273 两套卡尔米内学院方案与主题端点批次（2026-10-25）：** 沿用5个既有 S3 `new` 组，登记第一套方案及4个主题 KU；与 p.255 的三项人物化图像区分，不把集合型“神学美德”卡一对一复用为单项端点。11条 S6 候选全部有去向：6 formal（`rel-1932`–`rel-1937`）和5 pending，后者因 S3 端点未决或无精确受控谓词留在过程记录，不写缺端点关系占位行。定向渲染7张卡，写后核验通过，7/7 复预览无差异。严格表审计 `errors=[]`、`s2_missing=[]`；关系一致性五类阻断均为0。批后 S4 为2,052/5,072条 `new` 已映射，待登记3,020条；其中1,308条未映射 `new` 候选仍触及直接关系。S2为15,343 statements／26,781 mentions；统一独立复核9,617/15,343（62.68%，仍未接收）；S3 same=2,052、new=5,072、conflict=9、excluded=103、undecided=5,188；S5字段13,177（1,634 `unverified`）；S6累计1,227/10,559（700 formal、419 pending、108 rejected），余9,332；`relations.csv`为1,937条（1,913 formal、24 pending）。详情见[本批逐项过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s6-ch9-p273-two-schemes-20261025)。

**第9章 p.252 Tiepolo–Dolfin 十幅罗马史组画跨章分组与关系裁决（2026-10-24）：** `cand-8241` 从 `undecided` 改判为来源限定的十幅作品组并登记 KU；`cand-5796` 与 `cand-8263` 分别按跨章城市指称、相同手稿题名与架号完成映射。6项 S6 均有去向：3 formal（`rel-1926`–`rel-1928`，创作者、人物层级赞助、作品组受画方）及3 pending（`rel-1929`–`rel-1931`，组画分藏地点与手稿保管定位）。p.253 两条“纪念”候选仍 pending，理由改为缺精确谓词及 Daniele 个体身份待证。5张受影响卡定向渲染并复预览无差异；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五项阻断均为0。S2/S5未变。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s6-tiepolo-dolfin-cycle-ch9-p252-20261024)。

**第9章 p.252 Vendramin-Calergi 组画关系端点批次（2026-10-24）：** 将 `cand-8253` 登记为 place KU；S3定点复核 `cand-8254`，由 `undecided` 改为来源限定的 `new` 组画身份并登记 work KU。两项S4映射完成；地点关系新增 formal `rel-1925 located_at`，Bambini“被归于”表述因无精确受控谓词保留为过程级pending，不误写 `created_by`。两张卡定向渲染并写后核验；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性阻断为0。S2 statement／mention及独立复核分子未变。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s6-ch9-p252-vendramin-cycle-20261024)。

**第8、9、19章 Lucca MS(S). 3299 书信跨章组及 S6 裁决（2026-10-24）：** 将 `cand-7801`、`cand-7802`、`cand-10797`、`cand-7803`、`cand-8620` 归入4个跨章身份组，登记3封档案信与Lucca机构4张KU卡、5条候选映射；第8章注2与附录3的Torelli条目确认是同封信。新增6条S2作者/收件人statement、23条Haskell来源S5字段，不增加mention或独立复核分子。14项S6均有去向（7 formal、6 pending、1 rejected），其中4项非表级裁决保存在知识过程记录；relations.csv新增10行。10张受影响卡定向渲染并通过写后核验。批次记录见[逐项过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-lucca-ms3299-letters-20261024)。

**第7章 p.191 注5、注9迁入与裁决（2026-10-24）：** 补入 Pascoli 卷I、卷II及 Pacichelli 三条引证 statement、两条卷级 mention，并修正本段的脚注指向、转述语气和12条引文的编辑性后缀。S3将 cand-6972 的“卷I+卷II”合并身份排除；两卷和 Pacichelli 均复用既有 archive KU。三条 S6 引证去向明确：复用 rel-1862、新增 rel-1914、复用 rel-1738。S5 no_delta，统一独立复核分子不变。严格表审计及关系一致性审计在偏移修正后通过；残余 st-chp7-p191-i07 端点判断、cand-6955 类型仍待处理，本页未接收。当前 S2 15,337 statements、26,781 mentions，独立复核9,617/15,337（62.70%，未接收，台账仍待核平）；S3 same=2,052、new=5,069、conflict=9、excluded=103、undecided=5,191；S4映射2,037/5,069、待映射3,032（其中1,313条触及直接关系端点）；S5字段13,154（1,634 unverified）；S6已裁决1,194/10,551（683 formal、404 pending、107 rejected），余9,357；relations.csv 1,914条（1,896 formal、18 pending）。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s2-s3-s4-s6-ch7-p191-notes5-9-migration-20261024）。

**第8章 p.234 撒迦利亚被石击关系端点批次（2026-10-24）：** S4 端点核对触发 S3 定点复核：作品 `cand-7939`、Ferdinand 的 1716 inventory `cand-7936`、Uffizi `cand-7945` 均复用既有 work/archive/institution KU；未新建对象。三个直接 S6 候选均有去向：委托关系 formal `rel-1912 commissioned_by`（保留 Haskell 对遗失指示的推断）、清单记录 formal `rel-1913 has_subject`、Uffizi 保管关系 formal 复用 `rel-0737 held_by`，未造重复边。S5 `no_delta`；S2 statement／mention与独立复核分子不变。严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断为0。批后 S3 same=2,052、new=5,069、conflict=9、excluded=102、undecided=5,192；S4映射2,037/5,069、待映射3,032（直接关系端点1,313）；S5 13,154字段（1,634 `unverified`）；S6裁决1,191/10,548（680 formal、404 pending、107 rejected），余9,357；`relations.csv` 1,913条（1,895 formal、18 pending）。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-ch8-p234-zechariah-endpoints-20261024)。

**第17章 p.381／第20章 p.410 Tempesta 跨章作品端点（2026-10-24）：** 沿用 S3 作品组 `workgrp-ab3548af485776`，将正文候选 `cand-10695` 与索引候选 `cand-1189` 映射至1个新 work KU；修正两条误映射到作品的 Giorgione 人物提及，并新增1条书内 `created_by` S2 statement（不增加 mention，不计入独立复核）。S5 新增2条来源支持字段。3项直接 S6 候选均有去向：Haskell 所述创作者归属 formal `rel-1911`；Manfrin 画廊与收藏端点因类型／范围未决分别 pending，理由留在过程记录而未写成无效端点关系。严格表审计 `errors=[]`、`s2_missing=[]`；关系一致性阻断为0。批后 S2 为15,334 statements／26,779 mentions；S4 映射2,037/5,071条 `new` 候选，待映射3,034条；S5为13,154条（1,634条 `unverified`）；S6已裁决1,188/10,548（677 formal、404 pending、107 rejected），余9,360；`relations.csv`为1,911条（1,893 formal、18 pending）。本次归属仅限 Haskell 的书内表述，未作外部作品身份核验。详见[本批 S2–S6 过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-tempesta-crosschapter-20261024)。

**第9、16、17章 Seminario Patriarcale 与 Armanni–Sasso 档案端点批次（2026-10-24）：** 沿用3个既有 S3 `new` 组，登记1个institution与2个archive KU并映射3条候选；新增9条 Haskell `source_backed` S5字段。3条直接 S6 候选均 pending：受控 `located_at` 仍为 `needs_split`，`held_by` 不允许 archive→institution；没有新增 formal 边。MSS.565–566两卷材料与1790年单封信保持不同粒度；与既有Vincenzo Armanni刊本分开。S2记录和独立复核分子不变。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-seminario-patriarcale-ch9-ch16-ch17-20261024)。

**第7、8、14章 Zanotti 人物端点批次（2026-10-24）：** 沿用既有 S3 跨章 new 组 `cand-7114`，登记1个 person KU 并映射1条候选；新增2条 Haskell `source_backed` S5 字段。两条直接 S6 候选均 pending：一条是 Haskell 对未读 Zanotti 页的归因性解释，另一条受制于未决信件端点；未新增 formal 边。S2 statement、mention和独立复核分子不变。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-zanotti-ch7-ch8-ch14-person-endpoint-20261024)。

**第9章 p.253 Tiepolo 端点批次（2026-10-24）：** 沿用9个既有 S3 new 身份组，登记9个 KU、10条 S4 映射；cand-8283 与索引 cand-2595 共用一张 work 卡。第9章注1一条复合 S2 statement 原子化后净增3条，不增 mention，不计入独立复核分子。新增11条 Haskell 来源 S5 字段。p.252–253 同一连续语境内20条 S6 候选逐项裁决为2 formal、18 pending，新增 formal `rel-1909–rel-1910`；未把未具名楼梯壁画、Abraham 场景组、first-masterpieces 组或未给目的地的召回推成确定对象。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp9-p253-tiepolo-endpoints-20261024)。

**第6章 p.153／第7章 p.193 威斯特伐利亚和约跨章身份与关系闭环（2026-10-24）：** 将 `cand-6322` 与 `cand-7156` 保留各自 `new` 主决定并归入同一 S3 事件组；登记1个事件 KU、2条 S4 映射和5条 Haskell 来源支持字段。依既有 p.193 复核意见拆分一条复合 S2 断言，并把 p.153“和约结束三十年战争”拆为独立 statement；净增2条 statement、不增 mention，均未计入 S2 独立复核分子。四项直接 S6 关系均 pending，因受控词表没有精确谓词，未写入 `relations.csv`。卡片定向复预览无差异；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性阻断为0。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-peace-of-westphalia-crosschapter-20261024)。

**第7章 p.201 建筑端点批次（2026-10-24）：** 将三个既有S3 `new`地点组 `cand-7306`、`cand-7307`、`cand-7317` 登记为3个KU并完成S4映射；新增6条Haskell来源S5字段，均为`source_backed`。冬宫“begun by”、两座Belvederes“by”、town palace“came to build”三项关系均按明确语义边界记为pending（`rel-1906`–`rel-1908`），不推断完工、设计职责或正式委托。三张新卡定向渲染，复预览无差异；严格表审计`errors=[]`，关系一致性阻断为0。S2 statement／mention及独立复核分子不变。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-ch7-p201-building-endpoints-20261024)。


**第7章 pp.193–198直接端点批次（2026-10-24）：** 沿用10个既有S3 `new`组，登记8个archive、2个work；另登记既有 `cand-1342` Thomas Killigrew来源局部person组，共11条S4映射。新增57条Haskell来源S5字段；根据p.197正文与注2补2条 `has_subject` S2 statement。12项直接S6候选均formal，新增 `rel-1894`–`rel-1905`（8 cites、2条保留来源归属的 created_by、2条 has_subject）。Bankes Collection候选 `cand-7271` 仍类型／身份未决，记入 `bl-0033`。11张新卡及4张受影响卡定向渲染，复预览 `files_to_write=0`；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性阻断为0。全库预检虽提示575张卡待渲染，本批只写回15张。新增2条S2 statement未计入独立复核分子。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp7-p193-198-direct-endpoints-20261024)。

**S3人物跨章归组（2026-10-24）：** `cand-7114`（Zanotti, G. P.）的书内引注跨第7、8、14章；Treccani《意大利人传记辞典》将 Giampietro Zanotti Cavazzoni 与1739年《Storia dell’Accademia Clementina》相连，并区分其子 Eustachio，故该候选改判 `new`，不并入既有 Eustachio KU。此为 S3 身份裁决，S4 尚未登记；所引内容未独立阅读。详见[跨章人物身份记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-giampietro-zanotti-ch7-ch8-ch14-20261024)。

**第4章 pp.106、113 跨章身份组与关系闭环（2026-10-24）：** 以第21章书目复核 `cand-5797`、`cand-5798`、`cand-5803` 的文献身份，并将 `cand-5806` 改为复用既有 Lumbroso KU；新增 `cand-12441`–`cand-12446` 六个边界明确或待界定的来源候选。登记13个 KU、15条 S4 映射和36条 Haskell 来源 S5 字段。60项 S6 候选均有去向（19 formal、39 pending、2 rejected），正式边为 `rel-1875`–`rel-1893`；两条 Fontainebleau 位置因地点候选未决保持 pending。22张受影响卡定向渲染并复预览无差异；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断为0。S2独立复核分子不变，未接收。详见[跨章身份分组与逐项裁决](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp4-p106-p113-endpoints-20261024)。

**第6章 p.161 Altieri 宫殿跨章端点批次（2026-10-24）：** 沿用10个既有 S3 `new` 身份组，登记10个KU及10条S4映射；新增26条 Haskell 原书 S5 字段。S2 关系断言拆分后新增5条statement（4条关系候选、1条职衔属性），不增加mention或独立复核分子。25项S6逐项裁决为10 formal、12 pending、3 rejected，新增rel-1861–rel-1870。未识别肖像、Cortona作品、Bellori/Clark书目与不明施工活动保留待证；OCR校读只记入 qualifiers，不改S0转录。详见[跨章身份与逐项裁决](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp6-p161-altieri-endpoints-20261024)。

**第6章 p.146 教宗当选与解释因素跨章端点批次（2026-10-24）：** 复核并沿用6项S3 `new` 身份组；`cand-6245` 的第6、7章提及作为同一欧洲势力均衡术语组呈现。登记6个KU及6条映射，新增6条Haskell来源S5字段。5条直接S6关系候选逐项保留 `pending`：当前受控谓词不能准确表达“艺术整体受事件影响”或“概念因素→概念变化框架”，未伪造正式边或关系谓词。7张目标卡预检/复预览无差异；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断为0。S2 statement／mention与独立复核分子不变。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp6-p146-election-factors-20261024)。
**第6章注2／第7章 pp.187–188 跨章 identity 与 S6 端点批次（2026-10-24）：** 将 cand-6353 的两章提及归入同一君士坦丁骑马像 work 组；登记12个 S4 KU、12条新映射并收窄2个未能定义的概念候选为 undecided。补入14条 Haskell 来源支持字段；32项S6候选逐项有去向（9 formal、20 pending、3 rejected），新增 `rel-1851`–`rel-1860`（其中1条 pending）。修正第6章注2引文锚点与第7章 p.188 安置关系端点；9张关系投影卡定向渲染并复预览无差异。严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断为0。S2独立复核分子不变，未接收。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp7-p188-endpoints-20261024)。

**第15章 p.371 De Non 伏尔泰肖像／Ferney与第15–16章国家宗教裁判所跨章端点批次（2026-10-24）：** 重新裁决 `cand-10524` 为 same 并复用 Inquisitori di Stato；将 `cand-10581` 的源文本地点 Ferney 从 undecided 收束为 new place；沿用 `cand-10582` 的 new 作品组。新增2个KU、7条Haskell来源S5字段。6项S6候选有去向（4 formal、2 pending、0 rejected），新增 `rel-1846`–`rel-1850`；Swajer手稿获取因目标 `cand-10643` 未决，仅记过程级pending。7张相关卡定向渲染、字节核验并复预览无差异；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断均为0。详见[身份与逐项裁决记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp15-p371-de-non-voltaire-ferney-20261024)及[裁判所身份复用记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s6-inquisitori-state-inquisition-20261024)。

**第7章 p.201 注2 跨章 archive 端点批次（2026-10-24）：** 沿用 cand-7349、cand-7350、cand-7351 三个 S3 `new` 身份组，登记3个 archive KU并补3条S4映射；Ilg 书名复数／单数差异由 Haskell 第21章书目与 TU Wien 记录对照，保留 OCR “Ug” 异文，不声称查阅被引文献。S5新增23条 source-backed 字段；三项直接S6 `cites` 均 formal（rel-1843–rel-1845）。四张受影响卡定向渲染、写后核验并复预览无差异；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断为0。未增改S2 statement／mention，独立复核分子不变。详见[过程裁决](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-ch7-p201-citations-20261024)。


**第10章 p.310／附录5 p.391 1762年售藏跨章端点批次（2026-10-24）：** 将 `cand-2471`、`cand-9278` 保留各自 `new` 决定并归入同一事件身份组，登记1个 event KU及2条S4映射；S2原子化后 statement 净增3条、mention净增1条，不计入独立复核分子。事件卡定向补足6条书内字段；6项直接S6候选均有去向（2 formal、2 pending、2 rejected），新增 `rel-1841`、`rel-1842`。三张受影响卡渲染后复预览无差异；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断均为0。仍未接收S2语义复核，未收口全书S4–S6。详见[跨章身份组与逐项裁决](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-ch10-p310-smith-sale-20261024)。

**第5、7、8章德尔罗索跨章关系端点批次（2026-10-24）：** 将第5章Ghezzi papers与第8章Ghezzi notes依明确回引归入同一档案来源组（候选各保留new决定），新增15个KU、16条S4映射及23条Haskell来源字段；25项S6候选均有去向（9 formal、15 pending、1 rejected），新增rel-1832–rel-1840。修正1条S2关系候选的原子性，新增1条遗嘱关系statement，不增加独立复核分子。19张目标卡预检，14张定向渲染并写后核验；复预览files_to_write=0。严格表审计errors=[]、s2_missing=[]，关系一致性五项阻断均为0。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-ch8-p211-del-rosso-cross-chapter-20261024)。

**第8章 p.215 祭衣间与1653年装饰计划端点批次（2026-10-24）：** 沿用 `cand-7633`、`cand-7639` 两个既有S3 `new` 身份组，登记1个 place KU、1个 event KU及2条S4映射；新增8条Haskell来源字段。两项直接S6候选分别裁为 `rel-1830 part_of`（祭衣间→教堂）和 `rel-1831 has_participant`（装饰计划→Consiglio del Consorzio）。六条教堂直接候选当前为2 formal、1条既有rejected、3 pending。四张受影响卡定向渲染并复预览无差异；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五项结构阻断均为0。未改S2 statement／mention、S3主决定或独立复核分子。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-ch8-p215-sacristy-decoration-programme-20261024)。

**第8章 p.215 钟楼、穹顶与灰泥装饰端点批次（2026-10-24）：** 沿用 `cand-7632`、`cand-7636`、`cand-7637` 的既有 S3 `new` 组，登记3个 work KU 和3条 S4 映射；新增8条 Haskell 来源字段，3条直接 S6 候选分别裁为 formal `part_of`（钟楼→教堂）、`designer_of`（Ricchini→穹顶，仅指1612年规划）、`part_of`（灰泥装饰→穹顶内饰）。五张受影响卡定向渲染并复预览无差异；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断项均为0。未重开 S3，也未新增 S2 statement／mention，独立复核分子不变。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-ch8-p215-architectural-work-endpoints-20261024)。

**第6章 p.166 Crespi 余下六件圣事端点批次（2026-10-24）：** 沿用 `cand-6563` 的既有 S3 `new` 组并登记作品组KU；新增2条书内S5字段，裁决2条直接S6候选为 formal（`rel-1824 commissioned_by`、`rel-1825 located_at`），另按馆方完整系列级证据新增外部 formal `rel-1826 creator_of`。四张受影响卡定向渲染并复预览无差异；表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断为0。未新增S2 statement／mention，独立复核分子不变；系列级1712年信息未用于单幅作品定年。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp6-p166-crespi-six-sacraments-20261024)。

**第5–7章 De Rinaldis 1939 跨章身份与 S4/S6 批次（2026-10-24）：** 沿用已复核的跨章 S3 身份组，完成8条 S4 映射并新增6个 KU；第5–7章与第21章的引注和书信关系逐项裁决为25条 formal 新边、复用既有 `rel-1239` 一条。新增两条第七章书信关系候选及一条mention，不计入独立 S2 复核分子。S5本批未写入，因全局预览包含范围外变更及既有来源支持字段降级；16张受影响卡预览、14张定向渲染。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s6-de-rinaldis-1939-rosa-ricciardi-citations-20261024)。

**第5章 p.136 Cerquozzi Plate 22a 跨章身份与关系端点批次（2026-10-24）：** 将 `cand-6137`／`aln-6318` 从原 `new` 修正为 `same → units/works/michelangelo-cerquozzi-the-artist-with-a-group-of-friends`，前置图版目录 FM-P22a 的作品题名、作者与图版号均与正文p.136直接相合；复用已有 `rel-0793 created_by`，不重复建KU或作者边。新增 `rel-1794 has_subject` 连接Vincenzo Neri；未具名朋友 `cand-6138` 保留S3 undecided、S6 pending，并列入 `bl-0031`，不为缺失端点伪造关系行。未新增S2 statement／mention或重复S5字段；两张受影响卡已定向更新。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s6-chp5-p136-cerquozzi-plate22a-20261024)。

**第8章 p.215 哥特式门廊端点批次（2026-10-24）：** 沿用 `cand-7629` 的 S3 `new` 身份组，登记门廊 work KU；与教堂整体、成对石狮及数年后建成的南入口分开。新增3条仅由 Haskell 书内来源支持的 S5 字段；将“Giovanni da Campione 于1355年建造门廊”裁为 formal `erected_by`（`rel-1793`），不外推设计、委托或南入口日期。S2 statement、S3决定及独立复核分子不变。批后计数与验证见下方快照和[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp8-p215-gothic-portico-20261024)。
**第7章 p.192 注2书目端点批次（2026-10-24）：** 沿用 cand-7143 与 cand-7144 的既有 S3 new 身份组，登记 Griseri 1956 与 Longhi 1954 两篇期刊论文 archive KU；新增16条 Haskell 来源 S5 字段。两条 cites 候选均 formal 裁决（rel-1791、rel-1792），只记录 Haskell 的引注和页码，不表示论文或所引页已查阅。未新增或重开 S3 决定、S2 statement 或独立复核分子。两张新卡与 Haskell 书目总卡定向渲染后复预览；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp7-p192-griseri-longhi-citations-20261024)。

**第7章 p.183 注3与第21章书目跨章端点批次（2026-10-24）：** 沿用5个已判 `new` 的候选组并复用1个既有书信候选组，新增 Carlo Morbio、M. A. Chéruel 两个来源限定人物身份组；完成8个S4映射及27条S5字段，新增12条mention和10条有锚点的关系候选statement。18项新S6裁决为14 formal、2 pending、2 rejected，另复用既有 `rel-1297`；待证 avviso 与 Maccarani gallery 各保留明确去向。8张新卡与马扎林、马卡拉尼、Haskell书目总卡3张既有端点卡均定向渲染，复预览无差异；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断为0。新statement未计入S2独立复核分子，所引原书和页码未独立查阅。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp7-p183-note3-endpoints-20261024)。

**第4章 pp.117–118《阿波罗与达芙妮》跨章身份与端点批次（2026-10-24）：** 将索引候选 `cand-1992` 与正文候选 `cand-5988` 归入同一 Poussin 未完成画作组；为 `cand-11669` 补齐精确 mention 锚点后改判 `new` 并登记主题词 KU。同题 Bernini 雕塑与 Maratta 绘画维持独立身份。修订3条既有 S2 statement，未增加 statement；补1条 mention。S5新增2条 Haskell 来源字段；4项 S6 候选均有去向（3 formal：`rel-1774`–`rel-1776`，1 rejected）。四张受影响卡完成定向渲染与复预览；严格审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断为0。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp4-p118-apollo-daphne-20261024)。

**第4章 p.118 Claude 海岸画与 Origin of Coral 端点批次（2026-10-24）：** 沿用 `cand-5992` 与 `cand-11673` 的既有 S3 `new` 身份组，登记1件作品与1个主题词 KU，新增2条 Haskell 来源 S5 字段；10条关联 S6 候选逐项裁为2 formal（`rel-1772 created_by`、`rel-1773 has_subject`）和8 pending。未把两幅画的集合描述强拆为单件身份，脚注所列两个地点未逐画配对，Poussin 与 Cortona 对象保持待证。三张相关卡片完成定向渲染和复预览；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断均为0；S2分子及S3主决定不变。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp4-p118-coral-endpoints-20261024)。

**第4章 p.100 图版17a 卡西亚诺讽刺像端点批次（2026-10-24）：** 沿用 `cand-5655` 的S3 `new` 身份组，登记1个作品KU并补1条书内来源作品类型字段；两条图版题注关系 formal（`rel-1770 created_by`、`rel-1771 has_subject`），正文对“唯一已知肖像”的视觉评述保留为S2断言并拒绝作为正式图边。新卡定向渲染和复预览无差异；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断均为0。S2复核分子与S3决定不变。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp4-p100-plate17a-cassiano-caricature-20261024)。

**第7章 p.201《神化》作品与 Permoser 跨章身份组（2026-10-24）：** 将 P.csv#80（cand-1879）与 P.csv#81（cand-1880）归并为同一人物身份组，S3 均判 `new` 并映射到巴尔塔萨·佩尔莫泽 KU；把 P#81 的作品子目与人物主条目区分。cand-7308 沿用既有作品组，经 Belvedere object 3013 对照后登记为独立 work KU。S5新增10条字段；三条 Haskell 关系候选裁为2 formal（rel-1767、rel-1768）和1 rejected，另新增1条外部 `has_subject` formal（rel-1769）。Lower Belvedere 单体端点尚无 KU，记入 bl-0026，未建立 located_at 边。三张卡完成定向渲染及复预览；严格表审计 errors=[]、s2_missing=[]，关系一致性五类阻断均为0；S2独立复核分子不变。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp7-p201-apotheosis-endpoints-20261024)。

**第5章 p.135 Bertolotti 引注档案端点批次（2026-10-24）：** 沿用 `cand-6182` 的既有 S3 `new` 组，登记档案 KU 并补4条 Haskell 书目字段；从页图确认注3短题和 pp. 127 ff.，新增一条 S2 `cites` statement，将注3、注4和注5拆为三个有独立范围的 formal S6 引注边。S0 原转录保留，OCR 校读只记入 S2 qualifiers；新 statement 未计入独立复核分子。新卡和 Haskell 来源卡定向渲染并复预览无差异，严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五类阻断均为0。被引书及所引页未独立查阅。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp5-p135-bertolotti-citations-20261024)。

**第15章 p.369《Voyages》档案与作者身份批次（2026-10-24）：** 登记 cand-10528 为1777年海牙第一卷archive KU，新增4条S5字段和2条书目来源记录；cand-10527 作者候选经CiNii与相关1778年e-rara版本对照后仍为 undecided，不并入Carlo Antonio Pilati。3条关联S6候选分别裁为1 formal cites、1 pending authorship、1 rejected为独立图谱边。新卡定向渲染和复预览无差异；S2复核分子不变。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-ch15-p369-voyages-archive-20261024)。

**第14章 p.355 Algarotti 委托与三幅作品端点批次（2026-10-24）：** 登记4个既有 S3 new 身份组（1个 event、3个 work）；在三件单幅作品均已分开登记后，将集合候选 cand-12201 从 undecided 改为 excluded，完整集合断言仍留在 S2。补入3条尚未独立复核的作者归属 statement（不计入统一复核分子）、18条 Haskell 来源字段；8条 S6 候选均有去向：7 formal（rel-1756–rel-1762）、1 rejected。委托者、委托画、三件作品的书内作者归属与两幅后续画的相对先后分别成边；注2的并列地点未分配到单件画，也未补具体日期。六张受影响卡定向渲染并复预览无差异；严格表审计 errors=[]、s2_missing=[]，关系一致性五项阻断均为0。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp14-p355-algarotti-commission-20261024)。

**第3章两座耶稣会教堂端点批次（2026-10-24）：** `cand-0703` 从 `new` 局部改判 `same` 并复用 S. Ignazio 地点 KU；`cand-0724` 保留 `new` 组并登记 S. Vitale 地点 KU。新增1条S5地点性质字段与3条尚未独立复核的S2 statement；11条关联S6逐项裁为4 formal（`rel-1751`–`rel-1754`）、5 pending、2 rejected。六张受影响卡定向渲染并复预览无差异；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五项阻断均为0。详见[批次过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp3-jesuit-church-endpoints-20261024)。

**第6章 p.146 卡斯特罗镇端点批次（2026-10-24）：** 沿用 `cand-6257` 的 S3 `new` 组，新增1条S4映射，并记录1条来源支持的S5地点性质字段。3项关联S6逐条裁为1 formal（`rel-1750 located_at`）、1 pending（“belonging to Duke”含义未定）、1 rejected（复合叙述不足以建立具体关系边）。卡斯特罗镇与 Papal States 两张受影响卡片完成预览、定向渲染和复预览；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五项阻断均为0。S2分母与S3决定不变。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-ch6-p146-castro-town-20261024)。

**第七章 p.189 档案端点与引注批次（2026-10-24）：** `cand-7113` 由 `new` 局部改判 `same`，复用已登记的 Montaiglon 18卷系列，不新建重复KU；在同批完成两条引注关系 formal 裁决（`rel-1748`、`rel-1749`），卷I页104与190分别保留在关系语境中。页图核实正文大小写和脚注编号两处OCR订正并写入statement字段；同页44条statement逐条复核，统一复核更新至9,617/15,283（62.9%），尚未接收。两张受影响卡片完成预览、定向渲染与复预览；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五项阻断均为0。详见[端点与关系过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s6-chp7-p189-montaiglon-citations-20261024)和[S2复核记录](../../03-processing/patrons-and-painters-full-book-s2/process/s2-independent-review-chp7-p189-20261024.md)。

**第七章 pp.190–191 与第21章书目跨章端点批次（2026-10-24）：** 将 `cand-7125` 从 `new` 改判 `same` 并复用 Roma XIX（1941）卷；将 `cand-6974` 从 `undecided` 改判 `new`，按原书书目形式登记 Gio: Battista Pacichelli 人物 KU。登记13个 S4 映射（10个 archive、3个人物），新增66条 Haskell 来源 S5 字段；新添7条关系 statement 和5条 mention，不计入 S2 独立复核分子。20条相关 S6 候选逐项有去向：16 formal（`rel-1732`–`rel-1747`）、4 pending；未决的 Ghelli、Maclaren、Duc d’Estrées 与 Society 分支分别保留在 `bl-0022`–`bl-0025`。不从 Berwick 公开接纳演说的引注推断演说以 Duke 为主题。17张卡定向渲染；严格表审计 `errors=[]`、`s2_missing=[]`，关系一致性五项阻断检查均为0。详见[跨章端点批次过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp7-p190-p191-archive-endpoints-20261024)。

**Farsetti 别墅建筑端点批次：** 第15章印刷页362–363新增11个 S4 KU 映射；cand-12219从类型未决改判为work，其余10项沿用原 S3 new 组。新增3条建筑构件 S2 原子 statement、25条 Haskell 来源 S5 字段。20条 S6 候选逐项有去向：9 formal（新增 rel-1713–rel-1722 共10条边，移交断言分别表达接收与移交者）、9 pending、2 rejected。bl-0016–bl-0018分别保留两个类型边界未决收藏端点和匿名赞誉者。过程见[Farsetti 别墅建筑批次](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-ch15-p362-farsetti-villa-architecture-20261023)。本批3条 S2 新 statement 未计入独立复核分子。

**第3章 p.91 祭坛与遗骨瓮批次（2026-10-24）：** 沿用既有 S3 组，登记3条新候选至作品 KU，补入8条有来源支持的 S5 字段；7项直接关系候选均有去向：4 formal、3 pending。遗骨类型仍待分类的 cand-5220 记入 bl-0019；不把来源的推测性付款、未说明提供者的赠予或未登记遗骨端点写成正式关系。过程见[祭坛与遗骨瓮批次](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp3-p91-jesuit-altar-and-urn-20261024)。

**第3章 pp.73–76 作品与赌场端点批次（2026-10-24）：** 沿用6个直接关系端点候选的既有 S3 new 身份组，并将同段主题词 cand-5174 登记为 term；共新增7个 S4 映射、26条 Haskell 来源 S5 字段。9条关联 S6 候选逐项有去向：5 formal（rel-1727–rel-1731）、4 pending；未把未来计划、无精确受控谓词或不确定的委托解释写成正式边。未具名宫殿 cand-5112 与身份不明的 Cardinal Borghese cand-5178 分别进入 bl-0020、bl-0021。修正一项 S2 嵌套限定字段名，不增 statement 数量或独立复核分子。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp3-p73-76-aurora-colonnade-allegories-20261024)。

**第9章 p.251跨章身份与端点批次（2026-10-24）：** cand-6960 与 cand-8218 经跨章核对分别复用圣彼得大殿及 Bernini 柱廊 KU；cand-1518、cand-8229、cand-8231 登记为 Manin Passeriano country house、Le Grazie（Florio）与 La Galleria di Minerva 第六卷。cand-8230 因可能与同卷第83页的 cand-9523 指向同一匿名信件，保留 S3 undecided。新增3条 mention 锚点、1条 authored_by S2 statement（不计独立复核分子），新增13条 S5 字段并更正 Daniele Florio 卡的印刷题名；5条相关 S6 候选逐条裁为1 formal、3 pending、1 rejected。六张受影响卡定向渲染并复预览无差异；严格表审计 errors=[]、s2_missing=[]，关系一致性五类阻断均为0。详见[本批过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp9-p251-endpoints-20261024)。

**全书当前快照以本节顶部为准。** 现有 S3 undecided 类型分布如下；“关系端点”列仅计这些undecided候选中出现在当前 `relation_candidate=true` statement的唯一候选ID。

**S3 收口判据：** 按类型与相邻来源页分批；先汇总跨章同一身份组及各自来源锚点，再逐候选记录决定和去向。`same`须指向复用KU，`new`须归入唯一身份组并完成S4，`conflict`须保留双方及证据，`excluded`须说明排除依据；`undecided`须列明缺证、解除条件和待证位置。证据不足时不强行归并或新建对象。

1. **按类型逐组处理S3未决并优先解锁直接关系端点。** 当前1,231个未映射 `new` 候选组触及直接关系端点（1,231组／1,240条组成员映射），类型为term 457、archive 265、work 196、place 165、event 82、institution 65、person 1；按类型与相邻来源页编批，先审证据和跨章身份，再确定same、new、conflict、excluded或带解除条件的undecided。另有26项跨来源decision差异，逐项回到来源与身份语义核对，不自动视为冲突。其余5,158个undecided候选按下表类型队列推进。
2. **端点确定后同批完成S4、关键S5和关联S6。** 当前S4已映射2,149/5,093个 `new` 候选，待登记2,944个。每批新对象登记后补有来源支持的关键字段，并将关联S6候选逐条裁为formal、pending或rejected；身份、证据或受控谓词不足时记录明确条件，不强建关系。
3. **定点处理缺候选端点的关系statement，并核平S6台账。** 当前10,575条 `relation_candidate=true` statement中，有337条至少缺一个S2端点候选ID（仅缺subject 45、仅缺object 220、两端均缺72）。回源补mention与候选后再走S3/S4并返回S6。累计S6裁决1,400项（797 formal、487 pending、116 rejected）；历史分母10,578与当前10,575相差3，按statement ID核平后再报告剩余量和完成率。
4. **按关系价值核查S5。** 对1,634条 `unverified` 字段先判断是否影响身份、端点、类型或正式关系；只有证据充分时才更新状态，其余保留未验证及具体缺口。
5. **分章完成S2独立语义复核并对齐台账。** 统一复核为9,617/15,360（62.61%，未接收），另有5,743条未进入统一复核；按当前statement ID和来源版本标记有效、重复、已改写、失效或新增。p.190的43条页内复核待与全书台账核平，p.189五条和p.191三条当前statement版本待独立复审；随后沿书序处理p.192。章节局部审读、机械审计和本批自查不并入统一接收口径。
6. **满足门槛后再准备S7。** S3候选都有可追溯决定或有条件待证去向；可登记的 `new` 均完成S4；关键S5字段有证或有明确缺口；S6候选逐项有决定且累计台账核平；backlog 44项（12 completed、32 undecided，严格审计pending=0）有清楚去向。S2台账核平并完成独立语义接收后，才进入发布验证；知识发现和页面仍需用户明确启动。

**当前未决身份按类型分布：** 按每个candidate_id的首条alignment主决定计数；关系端点列只计仍为undecided且作为当前relation_candidate=true statement的subject或object的唯一候选。

| S3 undecided类型 | 候选总数 | 其中关系端点候选 |
|---|---:|---:|
| 类型未定 | 626 | 471 |
| work | 1,578 | 1,088 |
| term | 658 | 444 |
| person | 1,062 | 430 |
| archive | 678 | 296 |
| place | 305 | 130 |
| institution | 118 | 82 |
| event | 113 | 67 |
| family | 18 | 13 |
| procedure | 2 | 2 |
| **合计** | **5,158** | **3,023** |

**本批验证与提速方式：** 第4章 pp.106、113 本批13个S4 KU、36条S5来源字段、60项S6逐条决定；19条formal边涉及22张卡，定向渲染后22/22复预览无差异。严格表审计`s2_missing=[]`、`errors=[]`，关系一致性五类阻断为0；S2独立复核分子仍为9,617。本项目继续以同一来源页闭环方式推进，脚本只负责定位、结构核查和已审定内容的写回，不代替身份与关系判断。

前述第七章黎塞留批次的事件身份仅限 Haskell 书内所指事件；1642为书内所报年份，不声称外部核验。招揽政策与马萨林 1644 年贝尔尼尼行动、1648 年阿尔加迪行动分开。未将 `minister_to`、招募目标、负向“未中断”或作者因果解释强套进不精确的正式谓词。



### S2定向修订／S3／S4／S5／S6：第七章黎塞留招揽政策与死亡事件（2026-10-23）

沿用与本批相同的身份、端点和 S6 去向，详见[过程裁决](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-ch7-richelieu-policy-death-20261023)。两项 S4 新登记分别为 `units/events/richelieu-attempt-to-recruit-italian-artists-paris`、`units/events/death-of-cardinal-richelieu-haskell-1642`；死亡事件仅标注 Haskell 所报 1642 年。定向检查结果保存在同一过程记录。

### S3身份分组／S4登记／S5来源字段／S6裁决：第七章 p.175 阿波罗与缪斯十幅画（2026-10-23）

`cand-6693`（`aln-6870`）由undecided裁为new，建立来源限定作品群并登记KU `units/works/ten-pictures-apollo-muses-baglione-rome`。身份范围仅为Haskell所称十幅以阿波罗与缪斯为题、由Giovanni Baglione从罗马带来的作品群；不识别单幅作品、作者或版本，也不与《公共幸福战胜危险》合并。费迪南多提议将画作送作礼物，但送达、接收者与接受状态未确认。

S4新增一条候选映射；S5新增6条source_backed字段，均指向Haskell第7章印刷页175 L64–65（PDF物理页9）。未查证单幅作品的外部身份。

S6逐项裁决三条直接候选：`st-chp7-p175-i17` pending（礼物提议未说明接收者且不证明送达）；`st-chp7-p175-i18` pending（玛丽提出描绘要求，但原文未说明是否实施，当前关系词表不能精确表达该请求）；`st-chp7-p175-i19` formal，新增 `rel-1602 influenced`（作品群→黎塞留），只记录Haskell所述的间接注意力影响，不推断购入。未改动S2 statements或mentions，未增加独立S2复核计数。
### S4/S5/S6 archive：第10章 p.302 与第19章 p.392 James Adam 书信端点（2026-10-23）

沿用既有跨章S3 `new`组，登记1个archive KU，新增5条Haskell来源支持字段；三条直接S6关系均裁为formal：`authored_by` James Adam、`addressed_to` Robert Adam、`has_subject` Joseph Smith。最后一条只表明信件讨论Smith的财务状况，不证明实际或后来破产。原信、副本与Fleming刊本均未查阅。详见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp10-p302-p392-adam-letter-20261023)。

### S4/S5/S6 archive：第3章 p.85 Negroni 致 Oliva 书信端点（2026-10-23）

沿用既有S3 `new`组，登记1个archive KU，新增4条Haskell原书支持字段；两条直接S6候选均裁为formal（书信 `authored_by` Negroni、`addressed_to` Oliva）。原信、日期及保管信息未提供；不把Haskell关于祭坛徽章的叙述与引文中的信件内容混同。详见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp3-p85-negroni-letter-oliva-20261023)。

### S3沿用／S4/S5/S6：第9章 p.275 注2 Gherardi 致 Muratori 书信（2026-10-22）

沿用既有书信与机构S3 `new`组，登记1746年2月20日档案卡及Biblioteca Estense机构卡；新增4条Haskell原书支持字段。三条直接S6候选逐项裁为formal：书信 `authored_by` Gherardi、`addressed_to` Muratori、`located_at` Biblioteca Estense。仅记录Haskell书内通信与馆藏定位，不表示原信或馆藏目录已查阅，也不将其与其他年份的Gherardi–Muratori信件或未定复数通信合并。详情见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp9-p275-gherardi-muratori-20261022)。

批后：S0为832个源段（678 complete、154 excluded）；S2为9,573/15,208，独立复核分子不变、尚未接收；S3对齐表12,716行覆盖12,408个候选，289个候选有多来源记录、22个候选跨来源decision不一致，按触发条件定点核查；S4登记1,477/4,791组、1,691/5,020条映射，待登记3,314组/3,329条映射；S5字段12,240条（1,634条 `unverified`）；S6裁决437/10,436（264 formal、122 pending、51 rejected），余9,999条；`relations.csv`共1,481条（1,477 formal、4 pending）；candidate-backlog pending=0。`audit_tables.py --strict-stage --summary`：`errors=[]`、`s2_missing=[]`；关系一致性检查的broken target、invalid relation_type、missing inverse、weak evidence、unbaselined generic均为0。机械检查不代表S2语义接收或S4–S6全书收口。

### S3沿用／S4／S5／S6：第10章 p.329 注2–3 与第21章书目跨章端点（2026-10-22）

沿用七个已有S3 `new`身份组，登记四条archive与三位作者person KU；S2定向补入Haskell对Sagredo 1857出版物的引注及三条书目作者候选，并修正两条Academy语境脚注的引注主体。扫描确认注2原题为 *Relazione per le riforme*。七条相关S6候选逐条裁为formal（`rel-1472`–`rel-1478`）：三条Haskell书内 `cites`、一条Sagredo出版物→报告的 `cites`、三条archive→person `authored_by`。被引材料与原件均未独立查阅；未重开S3。25条字段预览均有对应来源，未增加 `unverified`。详情见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-ch10-p329-sagredo-bassi-fogolari-citations-20261022)。

批后（结构化表和本批记录）：S0 832个源段均有complete/excluded处置；S2为9,573/15,208，独立复核分子未增加、未接收；S3对齐表12,716行覆盖12,408个唯一候选；289个候选有多来源记录，其中22个跨来源decision不一致，列为相关端点或新证据触发时的定点复核对象；本批七个对象沿用既有new决定；S4已登记1,475/4,791组、1,689/5,020条映射，待登记3,316组/3,331条映射；S5字段12,236条（1,634条 `unverified`）；S6裁决434/10,436（261 formal、122 pending、51 rejected），余10,002条；`relations.csv`共1,478条（1,474 formal、4 pending）；candidate-backlog 5条历史记录、pending=0。`audit_tables.py --strict-stage --summary`：`errors=[]`、`s2_missing=[]`；关系一致性检查未发现broken target、invalid relation type、missing inverse、weak evidence或unbaselined generic。仍有3,331条new映射待S4，且全书S2语义审读未完成；机械检查不等于阶段收口。

### S3沿用／S4/S5/S6 archive：Faldi 1957 跨章引注（2026-10-22）

沿用 `archive-group-47abbb90563f` 登记 `cand-4331`，新增一张archive KU及5条书目支持字段。第21章扫描书目确认题名、责任者形式、期刊、年份与页码；扫描行末的 `di - Sutri` 按候选身份中的连续地名形式写作 `di Sutri`，不表示已查阅文章正文。第1章p.14注3与第2章p.29注5两条明确引注分别裁为formal `cites`（`rel-1470`、`rel-1471`），只记录Haskell书内引注。详见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-archive-faldi-guidotti-1957-cross-chapter-citations-20261022)。

本批后（由当前结构化表重算）：S2为9,573/15,204，未接收；S3主决定12,388/12,408，另有20个候选尚无主决定（16 person、2 institution、2 archive）；已有主决定中same 2,026、new 5,020、conflict 9、excluded 100、undecided 5,233，其中622项类型未决。S4已登记1,468/4,791组、1,682/5,020条映射；待登记3,323组／3,338条映射，其中直接关系端点1,587组／1,596条组成员映射；S5字段12,211条（1,634条 `unverified`）；S6裁决427/10,432（254 formal、122 pending、51 rejected），余10,005条；`relations.csv`共1,471条（1,467 formal、4 pending）。本次表格审计 `errors=[]`、`s2_missing=[]`；关系结构审计未发现 broken target、invalid type、missing inverse、weak evidence 或 unbaselined generic。机械检查不代表全书S2语义接收或S3–S6收口。
更新日期：2026-10-22。

### S3沿用／S4/S5/S6：Hoogewerff 1913 跨章引注（2026-10-22）

沿用 `archive-group-b1605ff43569` 登记 `cand-6199`，新增一张archive KU及4条书目支持字段。扫描页确认第21章p.426原题拼写 `omtrent`，Markdown OCR作 `omirent`；登记仅限书目所列出版物，不解决Hoogewerff人物身份。第1章p.18注1与第5章p.141注1两条明确引注均逐项裁为formal `cites`（`rel-1468`、`rel-1469`），只记录Haskell书内引注，不表示被引出版物或其第49–50页已独立查阅。详细证据见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-archive-hoogewerff-1913-cross-chapter-citations-20261022)。

批后：S2为9,573/15,204，独立复核分子未增加；S3仍为12,388/12,408；S4已登记1,466/4,791组、1,681/5,020条映射；待登记3,325组／3,339条，其中直接关系端点1,588组／1,597条映射；S5为12,206条字段（1,634条 `unverified`）；S6裁决425/10,432（252 formal、122 pending、51 rejected），余10,007条；关系表1,469条（1,465 formal、4 pending）。


### S2定向补足／S3沿用／S4/S5/S6：第七章 p.201 Pozzo 天顶画（2026-10-22）

沿用三个既有 S3 `new` 组，登记 Liechtenstein 家族花园宫殿、其内部大厅及 Pozzo 于1704年开始绘制的大厅天顶画；同批新增两条原子空间候选。五条 S5 字段均由 Haskell 原书支持。三条 S6 候选均裁为 formal：Pozzo→天顶画 `creator_of`、天顶画→大厅 `located_at`、大厅→花园宫殿 `part_of`；另一个“召见皇帝”候选仍 pending。完成状态、现今位置与产权均未推断。详见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp7-p201-pozzo-ceiling-20261022)。

批后：S2为9,573/15,204，独立复核分子未增加；S3仍为12,388/12,408；S4已登记1,465/4,791组、1,680/5,020映射；S5为12,202条（1,634条 `unverified`）；S6裁决423/10,432（250 formal、122 pending、51 rejected），余10,009条；关系表1,467条（1,463 formal、4 pending）。

### S3沿用／S4/S5/S6：第4章 p.104 St Susanna 与 S. Maria di Loreto（2026-10-22）

沿用两组既有 S3 `new` 身份组，登记一件作品与一座教堂；补入3条 Haskell 原书支持字段。三条相关 S6 候选逐条裁决：2条 formal（`rel-1463 creator_of`、`rel-1464 located_at`），1条 pending（比较对象仍为未定集合性 term，且受控谓词不能表达 work→term）。详情见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp4-p104-st-susanna-20261022)。

批后：S2为9,573/15,202，尚未接收；S3主决定仍为12,388/12,408，缺20；S4已登记1,462/4,791组、1,677/5,020映射，待登记3,329组／3,343映射（直接端点1,590组／1,599映射）；S5为12,197条（1,634条 `unverified`）；S6裁决420/10,430（247 formal、122 pending、51 rejected），余10,010条；关系表1,464条（1,460 formal、4 pending）。

### S3身份沿用／S4／S5／S6：第15章 p.371 注2的 Moschini 与 Pallucchini 引注（2026-10-22）

沿用两组跨章 `new` 身份组，将六条 Moschini 候选与一条 Pallucchini 候选登记为两张 archive KU；新增十条原书支持字段。第15章注2的两条 `cites` 候选均裁为 formal（`rel-1461`、`rel-1462`），仅记录 Haskell 的引注，不声称已查阅被引原书或页码。详见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp15-de-non-citations-moschini-pallucchini-20261022)。

批后：S2为9,573/15,202，尚未接收；S3主决定仍为12,388/12,408，缺20；S4已登记1,460/4,791组、1,675/5,020映射，待登记3,331组／3,345映射（直接端点1,592组／1,601映射）；S5为12,194条（1,634条 `unverified`）；S6裁决417/10,430（245 formal、121 pending、51 rejected），余10,013条；关系表1,462条（1,458 formal、4 pending）。审计无结构错误，但不代表全书阶段收口。

### S4/S5/S6：第15章 p.370 阿尔蒂基耶罗图书室、藏书与培根胸像（2026-10-22）

沿用3个既有S3 `new`组，登记藏书集合、胸像及图书室三个KU，新增4条原书支持字段。三条S2关系候选均裁为formal：藏书集合和胸像分别 `located_at` 图书室；胸像→Francis Bacon以受控 `has_subject` 表达，不推断创作者或现今地点。`idol of the temple`保留为Haskell修辞，不作作品题名。详见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp15-p370-alticchiero-library-bacon-20261022)。

批后：S2为9,573/15,202，尚未接收；S3主决定仍为12,388/12,408，本批未重开身份决定；S4已登记1,458/4,791组、1,668/5,020映射，待登记3,333组／3,352映射（直接端点1,594组／1,608映射）；S5为12,184条（1,634条unverified）；S6裁决415/10,430（243 formal、121 pending、51 rejected），余10,015条；关系表1,460条（1,456 formal、4 pending）。结构审计与关系一致性检查通过，不代表全书阶段接收。

### S3定点复核与 S2/S4/S5/S6：第9章 p.254–255 皮萨尼寓意壁画（图版44）

S3将作品候选复用到既有Plate 44作品KU；另将不适配现有类型的在世家族成员集合保留为undecided。对p.255关系候选作S2原子化修订，分别记录theological virtues与Wisdom；登记两个term端点，补入11条来源支持字段。5条S6候选均裁决：4 formal（含复用rel-1004）及1 pending；新增rel-1455–rel-1457。详见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp9-pisani-plate44-20261022)。

批后：S2为9,573/15,202，关系候选10,430条、335条缺至少一个S2端点候选ID；S3主决定覆盖12,388/12,408；S4已登记1,455/4,791组、1,665/5,020映射，待登记3,336组／3,355映射（直接端点1,597组／1,611映射）；S5为12,180条（1,634条unverified）；S6裁决412/10,430（240 formal、121 pending、51 rejected），余10,018条；关系表1,457条（1,453 formal、4 pending）。结构审计通过不代表全书阶段接收。


### S4/S5/S6：第4章 p.118 Accademia degli Umoristi 机构端点（2026-10-22）

沿用 `cand-0002` 的S3 `new`身份组，登记乌莫里斯蒂学院为来源限定的机构KU，新增1条S5字段 `enr-15938`。Massimi重组学院的S2关系候选保持pending：受控关系词表没有精确表达“重组机构”的谓词，不以成员、管理或赞助关系替代；无新增formal关系。批后S4为1,453/4,792组、1,663/5,022映射；S5为12,169条（1,634条 `unverified`）；S6累计407/10,429（236 formal、120 pending、51 rejected），余10,022条；关系表1,454条（1,450 formal、4 pending）。S2独立复核分子、S3决定均未改变。详见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp4-p118-umoristi-20261022)。

### S3沿用／S4／S5／S6：第八章 p.223 鲁福礼拜堂与所在教堂（2026-10-22）

沿用两个既有 S3 `new` 地点组，登记教堂与其内部的鲁福礼拜堂为不同 KU。将原有建造陈述与地点关系拆分，礼拜堂→教堂的 `part_of` 裁为 formal（`rel-1454`）；建造者及两位装饰者候选因缺少精确受控谓词均记 pending，不强套创作、委托或建造谓词。新增5条 Haskell 原书支持字段，Conca 拼写按扫描页校读；未添加外部身份核验。详情见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp8-p223-ruffo-chapel-20261022)。

批后状态：S2为9,573/15,201，关系候选10,429条，335条缺至少一个S2候选端点ID；第八章当前统一复核覆盖487/1,464，独立复核分子未因本批定向修订增加。S3主决定行12,388/12,408，类别未变、缺行20。S4已登记1,452/4,792组、1,662/5,022条映射；待登记3,340组／3,360条，其中直接端点1,601组／1,615条。S5字段表12,168条（1,634条 `unverified`），本批新增 `enr-15933`–`enr-15937`；预览与应用均无警告。S6累计裁决406/10,429条（236 formal、119 pending、51 rejected），余10,023条；关系表1,454条（1,450 formal、4 pending）。表格审计 `errors=[]`、`s2_missing=[]`；关系一致性检查无 broken target、invalid type、missing inverse 或 weak evidence。上述机械检查不构成S2语义接收或全书阶段收口。


### S4/S5/S6：第20章 p.401 两个胸像版本及馆藏端点（2026-10-22）

沿用既有S3 `new`组登记Humphris版本、普利茅斯另一版本及City Museum and Art Gallery, Plymouth，共3组／3条映射；两件作品分开建卡。新增10条原书支持字段。S2原子性修订拆分“另一版本”与馆藏位置、Radcliffe研究转述；新增版本关系裁为formal（`rel-1453 variant_of`）。Humphris持有叙述及馆藏位置分别为`rel-1451`、`rel-1452 held_by`；Wittkower提出的Bernini归属及Haskell转述的反对理由均拒绝作为当前图谱边，原书陈述仍保留。Radcliffe讨论保留为S2来源报告，不建图谱边；S3身份决定未重开。详见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp20-p401-bust-versions-20261022)。

批后：S2为9,573/15,200（63.0%，未接收）；S3主决定行12,388/12,408，缺20；S4已登记1,450/4,792组、1,660/5,022映射，待登记3,342组／3,362映射（直接端点1,600组／1,614映射）；S5为12,163条字段（1,634条 `unverified`）；S6裁决402/10,428（235 formal、116 pending、51 rejected），余10,026；`relations.csv`共1,453条（1,449 formal、4 pending）。candidate-backlog为5条历史记录、pending=0。全表审计`s2_missing=[]`、`errors=[]`；关系一致性检查的broken target、invalid type、missing inverse、weak evidence及unbaselined generic均为0。机械检查通过不等于S2语义接收或全书收口。

### S4/S5/S6：I Bamboccianti 展览图录与引言关系端点（2026-10-22）

沿用 `cand-6181` 的既有 S3 `new` 身份组完成图录登记，修复候选说明中的乱码而不改决定或组号，新增5条书目字段；将脚注引文与引言作者两条S6候选分别裁为 `cites`、`contributed_by`（`rel-1449`、`rel-1450`）。引言作者责任仅限于图录引言；原 OCR “Brigand” 保留，印本校读及 S3 人物端点路径见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-bamboccianti-catalogue-20261022)。批后：S4为1,447/4,792组、1,657/5,022映射；S5为12,153条（1,634条 `unverified`）；S6为397/10,427条（232 formal、116 pending、49 rejected），关系表1,450条（1,446 formal、4 pending）。

### S3/S4/S5/S6：第八章 p.237 Silva 与 Crespi作品端点（2026-10-22）

修复 `cand-2433` 与 `cand-0882` 的四条精确正文／注2 mention，将缺锚点的两条S3 `undecided`改为来源限定`new`，分列person与work身份组，不合并Poussin、Reni同题材作品。两组各完成S4登记并增加2条S5来源字段。相关S6候选均有去向：Silva委托画作裁为formal（`rel-1448 commissioned_by`）；违约并撤回赠画意图只拒绝当前关系边，保留S2原断言。详见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp8-p237-silva-massacre-20261022)。

批后：S2为9,573/15,198（63.0%，未接收）；S3决定分类same=2,025（1,089个既有KU）、new=5,022（4,792组）、conflict=9、excluded=100、undecided=5,232（含622项类型未决），主决定行覆盖12,388/12,408、缺行20；S4已登记1,446/4,792组、1,656/5,022条映射，待登记3,346组／3,366条（直接端点1,604组／1,618条、非直接1,742组／1,748条）；S5为12,148条字段（1,634条`unverified`）；S6累计395/10,427（230 formal、116 pending、49 rejected），余10,032条；`relations.csv`为1,448条（1,444 formal、4 pending）。

### S4/S6：第八章 Pratolino 地点端点与直接关系（2026-10-22）

沿用既有S3 `new` 组 `sg3-place-cand-7838`，完成 `cand-7838` 的Pratolino地点KU登记。三条直接候选全部有去向：两条formal（`rel-1446`、`rel-1447`），一条rejected为当前person→place候选边错置；原书关于收藏地点的statement保留。新增地点卡与一条S4映射，无S5字段新增。逐项理由见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s6-pratolino-direct-endpoint-20261022)。

### S2：第八章 p.237 当前 statement ID 独立语义复核（2026-10-22）

对照物理页43逐条复核39条当前 `st-chp8-p237-*` statement；发现Silva委托《无辜者屠杀》与其后违约、撤回赠画意图被合并，现拆为两项原子statement。新增1条statement及1条S6候选，并补齐4条精确mention；统一S2复核分子不变，待全书按当前statement ID核平第八章487/1,463与既有1,462/1,462直接核读记录后再更新。详见[S2复核记录](../../03-processing/patrons-and-painters-full-book-s2/process/s2-independent-review-chp8-p237-20261022.md)。

### S3/S4/S6：第八章 p.215–221 装饰委员会与直接关系端点（2026-10-22）

本批将5项有精确正文锚点的未决对象裁为来源限定 `new`，登记九条S4映射，并补入六条精确mention。40条直接以委员会为关系端点的S6候选全部有去向：12 formal、5 pending、23 rejected；另登记竞赛获胜画作的formal委托边，将Melanconici委托方身份保留为pending。关系表增至1,445条（1,441 formal、4 pending）；S2 statement及S5字段数不变。逐项决定及证据见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s6-chp8-p215-221-decoration-committee-20261022)。

批后：S2为9,573/15,197（63.0%，未接收）；S3主决定行12,388/12,408：same=2,025（1,089个既有KU）、new=5,020（4,790组）、conflict=9、excluded=100、undecided=5,234（含622项类型未决），缺主决定行20；S4已登记1,443/4,790组、1,653/5,020条映射，待登记3,347组／3,367条，其中直接端点1,605组／1,619条、非直接1,742组／1,748条；S5为12,146条字段（1,634条`unverified`）；S6累计390/10,426条（227 formal、116 pending、47 rejected），余10,036条；`relations.csv`为1,445条（1,441 formal、4 pending）。

### S3跨章身份复用与 S4/S5/S6：教会机构及关系端点（2026-10-22）

`cand-3400` 经跨章来源复核从 `new` 改为 `same`，复用第9章p.268 `cand-8672` 已建立的教会机构KU；该决定仅统一Haskell书内的机构指称，不作外部身份或连续性断言。既有卡片扩展至第1–4、8–10章语境，新增1条有原书依据的S5字段。8条直接S6候选逐项裁决：3条formal（`rel-1435`–`rel-1437`），3条pending，2条因端点错置rejected。详情见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-church-institution-cross-chapter-20261022)。

批后：S2为9,573/15,197，未接收；S3决定行12,388/12,408，same=2,025（1,089个既有KU）、new=5,015（4,785组）、undecided=5,239，缺行20；S4已登记1,434/4,785组、1,644/5,015条映射，待登记3,351组／3,371条（直接端点1,609组／1,623条）；S5字段12,146条（1,634条`unverified`）；S6累计裁决350/10,426（215 formal、111 pending、24 rejected），余10,076条；`relations.csv`为1,437条（1,434 formal、3 pending）。

### S3定点复核与 S4/S5/S6：第七章 p.175 三幅 Bacchanals 端点批次（2026-10-22）

`cand-1998`在S4直接端点登记触发下，依据印刷页175 L69及现有S2正文mention从`undecided`定点修订为来源限定的三幅作品群`new`；不识别单件作品或完成状态。登记三组：作品群、黎塞留城堡及Richelieu地点；黎塞留人物复用既有卡。修正作品群委托端点，新增预定地点与城堡所在地两条原子statement。新增11条`source_backed`的S5字段。三条相关S6候选全部裁为formal（`rel-1432`–`rel-1434`），关系表增至1,434条（1,431 formal、3 pending）。独立S2复核分子不变。逐项依据见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp7-p175-bacchanals-20261022)。

批后：S2为9,573/15,197，未接收；S3有决定行12,388/12,408，new=5,016（4,786组），undecided=5,239，缺行20；S4已登记1,434/4,786组、1,644/5,016条映射，直接端点待登记1,610组／1,624条映射；S5字段12,145条（1,634条`unverified`）；S6已裁决342/10,426条（212 formal、108 pending、22 rejected），余10,084条；`relations.csv`为1,434条（1,431 formal、3 pending）。


### S3复用/S4/S5/S6：第3章 p.93 右耳堂、报喜浮雕与 Fabrini 引文端点批次（2026-10-22）

沿用三个既有 `new` 身份组，登记礼拜堂、浮雕和 Fabrini 1952 年书目项；按第21章 p.421 书目修正第3章 “see Fabrini” 的引用主体与对象，S3身份组不变。新增18条书内来源字段，并补入一条右耳堂礼拜堂→S. Ignazio的S2位置候选。五条直接S6候选逐项有去向：四条formal（`rel-1428`–`rel-1431`），一条因未证实浮雕物理安置而pending。逐项证据及裁决见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp3-p93-annunciation-endpoints-20261022)。

批后：S2 9,573/15,195，未接收；S3有决定行12,388/12,408；S4已登记1,431/4,785组、1,641/5,015条映射，待登记3,354组／3,374条（直接端点1,612组／1,626条）；S5字段12,134条（1,634条`unverified`）；S6累计裁决339/10,424条（209 formal、108 pending、22 rejected），余10,085条；`relations.csv`为1,431条（1,428 formal、3 pending）。

### S3/S4/S5/S6：第九章 p.248–249 圣玛利亚·德尔·吉廖立面端点批次（2026-10-22）

`cand-8153`从S3 `new`按第七章版图与第九章文字的同一对象证据改为`same`，复用立面KU；Tempio Malatestiano与Rimini两个既有`new`决定完成S4登记。S2将设计、颂扬、比较与地点拆为原子断言，并新增3条statement；独立复核分子不变。补入6条来源字段。7条S6候选全部有去向：5 formal、2 pending；后两项分别因四兄弟集体身份和六处地点计划的对象边界未决而保留。逐项依据见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp9-p248-facade-endpoints-20261022)。

批后：S2为9,573/15,194，未接收；S3决定行12,388/12,408；S4已登记1,428/4,785组、1,638/5,015条映射；S5字段12,116条（1,634条`unverified`）；S6已裁决334/10,423条（205 formal、107 pending、22 rejected），余10,089条；`relations.csv`为1,427条（1,424 formal、3 pending）。

### S2定向修复与S3复用下的S4/S5/S6：第七章 p.186 画廊、教堂工程与脚注端点（2026-10-22）

依据印刷页186（PDF物理页24）修订14条旧statement、拆出8条原子statement，并为注1补入Wittkower作者和 `1958, p. 269` 两条精确mention。S3决定不变，沿用10个既有 `new` 身份组登记KU；新增23条有原书依据的S5字段。本段及脚注23条S6关系候选全部有去向：5 formal、15 pending、3 rejected；未以域值域缺项制造formal边，也未将整个Theatine修会代表未具名分支。新拆statement不计入独立S2复核分子。逐项理由见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)。

批后：S2 9,573/15,191，未接收；S3 12,388/12,408项有决定行；S4已登记1,427/4,788组、1,636/5,016条映射；S5 12,110条字段（1,634条 `unverified`）；S6累计327/10,420条（200 formal、105 pending、22 rejected），余10,093条；relations.csv 1,422条（1,419 formal、3 pending）。


### S2/S3/S4/S5/S6：第5章 p.138 战事绘画跨章端点批次（2026-10-22）

第5章 p.138 逐条复核36条statement并补入4条精确mention；第6章 p.146再补1条Urban VIII之死的跨章mention。保留cand-11931（未具名社交群体）与cand-11933（泛指复数战争集合）为有理由的S3 `undecided`；登记4个S3 `new`组、4个S4映射，并新增5条来源支持S5字段。与新增端点直接关联的7条S6候选均裁决：5 pending、2 rejected，无新增formal边；同段其余13条关系候选仍在全书S6队列。逐项记录见[S2复核](../../03-processing/patrons-and-painters-full-book-s2/process/s2-independent-review-chp5-20261022.md#s2-review-chp5-p138-battle-discussion-20261022)与[跨阶段过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp5-p138-cerquozzi-battle-discussion-20261022)。

本批后：S2 9,573/15,183（63.1%，未接收）；S3有决定行12,388/12,408；S4已登记1,417/4,788组、1,626/5,016条映射，待登记3,371组／3,390条（直接端点1,626组／1,639条）；S5字段12,087（1,634 unverified）；S6已裁决304/10,418条（195 formal、90 pending、19 rejected），剩余10,114条；relations.csv 1,417条（1,414 formal、3 pending）。

### S2定向修复与 S4/S5/S6：第15章 p.370 小屋铭文、Huber 版画及 Daphnis print series（2026-10-22）

拆分书房版画组statement的位置与设计目的；后者只记Haskell所述意图，不写成已证实效果。三个S3 `new`直接端点登记为地点、档案和作品KU，新增11条来源支持字段；本批10条 p.370 关系候选均有去向：5 formal、5 pending，版画组 `cand-10549` 继续 undecided。

批后：S2 9,537/15,183（62.8%），未接收；S3决定记录12,388/12,408，类别未变；S4已登记1,412/4,786组、1,622/5,016映射，待登记3,374组／3,394条（直接端点1,630组／1,643条）；S5字段12,082（1,634 unverified）；S6已裁决297/10,418条（195 formal、85 pending、17 rejected），剩余10,121条；relations.csv 1,417条（1,414 formal、3 pending）。逐项端点、证据和待决理由见[知识过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp15-cabane-inscription-huber-20261022)。

### S4/S5/S6 person：第七章 p.200 de Ferrari 与 del Po 直接端点（2026-10-22）

登记两个既有 S3 `new` 人物组、三条候选映射，并为两卡新增4条书内来源支持字段。Noailles—de Ferrari 候选依 p.200 对军事指挥官委托当地艺术家的语境及具体说服作画记载，裁为 `patron_of` formal（`rel-1412`）；关系限于人物赞助，不推定未识别画作。del Po—画布组候选复核后仍为 pending，因为 `cand-7300` 未完成身份对齐且无单件作品分配。本批未重开 S3、未访问外部身份源。逐项依据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-person-direct-endpoints-chp7-p200-20261022)。

批后：S4已登记1,409/4,786组、1,619/5,016条映射；待登记3,377组／3,397条（直接端点1,633组／1,646条，非直接1,744组／1,751条）。S5字段12,071条（1,634条 `unverified`）。S6已裁决287/10,417条（190 formal、80 pending、17 rejected），剩余10,130条；关系表1,412条（1,409 formal、3 pending）。S2为9,537/15,182；S3决定记录仍为12,388/12,408。

### S3/S4/S5/S6 archive：Roma XVIII（1940）与 1672 年 Avviso 跨章批次（2026-10-22）

将 cand-5242、cand-6477、cand-6570 对齐为同一 Roma XVIII（1940）档案/期刊卷，并将 cand-6476 登记为独立的 1672 年 Avviso；本批 S2 定点修复了脚注引注主体，S2独立复核计数不变。新增11条来源支持字段；五条关系候选全部有去向：4 formal cites、1 pending。逐项依据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-ch3-ch6-roma-xviii-1940-cross-chapter-20261022)。

批后：S4已登记1,407/4,786组、1,616/5,016条映射；待登记3,379组／3,400条映射（直接端点1,635组／1,649条，非直接1,744组／1,751条）。S5字段12,067条（1,634条`unverified`）。S6已逐项裁决286/10,417条（189 formal、80 pending、17 rejected），剩余10,131条；关系表1,411条（1,408 formal、3 pending）。S2仍为9,537/15,182；S3决定类别覆盖仍为12,388/12,408。

### S3定点复核与S4/S5/S6：第10章 p.329 有用艺术论证（2026-10-22）

`cand-9846` 保持S3 `new`，并与第10章同页提及的Gozzi较早社会价值论述、旧有 *diletto ed utile* 理论分开。登记为来源限定术语KU，新增3条Haskell书内来源支持字段（`enr-15823`–`enr-15825`）。3条直接关系候选均逐项裁为pending：当前受控谓词及域值域不能表达“人物提出论证”或“论证所称经济作用”，不写入formal边。S2独立复核计数不变。逐项依据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp10-p329-useful-arts-argument-20261022)。

批后：S4已登记1,405/4,788组、1,612/5,016条映射；待登记3,383组／3,404条映射（直接端点1,638组／1,653条、非直接1,745组／1,751条）。S5字段12,056条（1,634条`unverified`）。S6已裁决281/10,417条（185 formal、79 pending、17 rejected），剩余10,136条；关系表1,407条（1,404 formal、3 pending）。S2仍为9,537/15,182；S3决定类别不变。

### S3/S4/S5/S6：第七章 p.188 路易十四胸像与跨章术语（2026-10-22）

cand-6915依据第7章 p.188 L237 对 Plate 27b 的直接回指，从S3 new定点修订为same，复用既有Bernini路易十四胸像卡；保留原决定和组号作为历史。骑马像 cand-6917 仍为独立作品。cand-6916 与 cand-6923 保持new并登记为两项术语；cand-6923 同时承接第10章 p.296 的跨章语境，与“ancien régime”区分。胸像新增3条、术语新增3条S5来源支持字段（enr-15817–enr-15822）。四条S6候选逐项裁决为3 formal（rel-1404–rel-1407）和1 pending：委托者未在被动句中具名，不能据被描绘者推定。S2独立复核计数不变。逐项依据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp7-p188-louis-xiv-bust-20261022)。批后S3为same 2,023（1,089个既有KU）、new 5,016（4,788组）、conflict 9、excluded 100、undecided 5,240；S4已登记1,404/4,788组、1,611/5,016条映射；S5为12,053条字段（1,634条unverified）；S6为278/10,417条候选已裁决（185 formal、76 pending、17 rejected），关系表1,407条（1,404 formal、3 pending）。

### S4/S5/S6：第15章祭坛、浮雕与拟人化恶德（2026-10-22）

保留 cand-10569、cand-10570、cand-10592–cand-10594 五个S3 new组，分别登记两件作品和三个概念KU；cand-12246仍因作品身份未定而undecided。新增5条S5来源字段。对p.371的9条关系候选逐项裁决为6 formal（rel-1398–rel-1403）、2 pending、1 rejected；使用受控has_subject映射作品与概念主题。S2独立复核计数不变。逐项依据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp15-alticchiero-vices-20261022)。


### S3/S4/S5/S6：第15章 Alticchiero 花园端点批次（2026-10-22）

cand-2081保持S3 new，身份组从共享的 Querini 花园/住宅组拆出；花园、住宅和人物分别处理。S4新增7个 source-local KU 映射，S5新增12条来源字段并校正4条既有字段的来源引用。S6裁决12条候选：6 formal（rel-1392–rel-1397）、4 pending、2 rejected；Apollo原书引文补全但S2独立复核计数不变。全书当前S4为1,397/4,789组、1,604/5,017条映射；S5为12,042条字段（1,634条unverified）；S6为265/10,417条候选已裁决（176 formal、73 pending、16 rejected），关系表1,397条（1,394 formal、3 pending）。逐项证据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp15-alticchiero-garden-endpoints-20261022)。


### S2语义复核：第七章 p.200–202 复合脚注（2026-10-22）

复核34条statement、44条mention，全部mention跨度精确；校读p.200注4 OCR并补齐p.201注3正文回链。p.200注6此前已在正文段复核，p.200 Plate 30倒置图注已由图版清单覆盖，均未重复计数。批后统一S2复核为9,537/15,182（62.8%），第七章1,146/1,252；章节与全书仍未接收。逐条记录见[复核过程](../../03-processing/patrons-and-painters-full-book-s2/process/s2-independent-review-chp7-notes-20261021.md#s2-review-chp7-p200-p202-composite-notes-20261022)。

### S3/S4/S5/S6 archive：Diario Romano 跨章引注端点（2026-10-22）

第21章印刷页423书目将Diario Romano列在Gigli, Giacinto名下，注明Giuseppe Ricciotti编、Roma、1958。据此把cand-6269（第6章p.146注4的pp.203–240）与cand-6360（第6章p.150注2的p.233）由undecided改为同一现有new身份组 archive-group-1bfc6126228c，并与cand-6076合并；p.233位于pp.203–240范围内。只确定被引出版物身份，不表示已查阅该版本或页面。本批重算全书统计时只计非external_source主裁决行；20项只有外部对齐记录的候选仍不计作S3决定。按现有group标记重算，new组为4,789，修正此前当前快照多计1组；本次未更改其他S3候选。

S4将该archive组登记为 units/archives/gigli-diario-romano-ricciotti-1958，映射三条候选；S5新增10条书目与引注支持字段。S6对四条明确引注逐条裁为formal cites（rel-1386–rel-1389）；对Gigli“kept a detailed diary”候选裁为pending：原文支持保留行为，但当前受控关系类型没有准确的keeper谓词，不能改写为authored_by。

批后S3裁决行仍为12,388/12,408；new 5,017项／4,789组，undecided 5,240项。S4已登记1,388/4,789组、1,595/5,017条映射；S5字段12,024条；S6逐项裁决248/10,417条，关系表1,389条。逐项依据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-diario-romano-cross-chapter-citations-20261022)。


### S3/S4/S5/S6：第4章 p.116 与第7章 p.190 的 Donna Olimpia 肖像（2026-10-21）

将 cand-1498、cand-2713 与 cand-5970 归入同一新作品组；cand-2712 复用既有 Camillo Massimi 肖像KU。登记一张作品卡并新增四条书内字段。修订两条第7章肖像取得statement，另拆出两条Velasquez创作者statement；八个关系候选均裁决为7 formal（含1条复用）和1 rejected。逐项证据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-ch4-p116-ch7-p190-donna-olimpia-portrait-20261021)。

### S4/S5/S6：第七章 p.177–179 胸像、肖像与人物地点批次（2026-10-21）

登记 Bernini 查理一世胸像与 Van Dyck 查理一世三面肖像两组 S3 `new` 身份；`cand-0964` 与 `cand-4437` 映射到同一肖像卡。两卡新增4条 Haskell 书内来源支持字段；S6对16个关系候选逐条给出10 formal、4 pending、2 rejected 去向，新增9条正式边并复用既有 `rel-0452`。p.179 新增6条原子 statement 并修订3条既有 statement；这些定点修订未计入 S2 独立复核分子。逐项依据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp7-p177-179-bernini-and-vandyck-works-20261021)。

### S3：第七章 p.179 胸像、肖像与 England 的跨章身份复核（2026-10-21）

修订 `cand-0304` 为 Bernini 的胸像作品新组；将索引候选 `cand-0964` 与第2章正文候选 `cand-4437` 合并到同一 Van Dyck 肖像身份组；`cand-6290` 复用既有 England place KU。胸像和肖像保持为两件作品。当前 S3：same 2,026、new 5,028（4,802组）、undecided 5,245；S4待登记映射增至3,428。关系裁决与两件作品登记留在后续批次。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s6-chp7-p179-cross-chapter-identity-20261021)。

### S3/S4/S5/S6 work + term：第10章 p.296 楼梯厅顶画端点（2026-10-21）

图版身份复核将 cand-4180 从 new 改为 same，复用完整楼梯厅壁画 KU；Plate 50 仍只视为局部。cand-9136 登记为来源限定 term KU，新增1条 source_backed 字段。六条关系候选逐项裁为2条新 formal（rel-1369–rel-1370）、2条复用已有正式边（rel-1001、rel-1002）、2条否决图谱边且保留原书陈述。两条新增 statement 完成定点复核，但未并入统一 S2 复核分子。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp10-p296-staircase-fresco-20261021)。

### S4/S5/S6 work：Claude《A Storm at Sea》直接端点（2026-10-21）

登记既有 S3 新组 `workgrp-8b74eec6fd2029` 的作品候选 `cand-5556`，新增4条 Haskell 书内 `source_backed` 字段。四条直接关系候选逐条裁决为2 formal、2 pending：正式边为作品 `commissioned_by` Paolo Giordano II 与 `created_by` Claude；格言关系因原文仅为“perhaps”且 term 端点未登记而待证；*Liber Veritatis* 第33号记录关系因端点未登记且图册未核而待证。第4章注7 `recorded_in` statement 的页锚、父statement链接及 Röthlisberger OCR校读一并修复；不增加S2覆盖计数，不表示第4章接收。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-storm-at-sea-20261021)。批后 S4 1,395/4,803组、1,599/5,028条映射；S5 12,005条（1,634条 `unverified`）；S6 207/10,402条（143 formal、55 pending、9 rejected），关系表 1,368条（1,365 formal、3 pending）。

### S4/S5/S6 archive：Mazarin 1961展览图录及两处书内引注（2026-10-21）

沿用 S3 `new` 组 `archive-group-1e3bcedc560c`，将 `cand-7044` 登记为单成员 archive KU `units/archives/mazarin-homme-detat-collectionneur-1961`。身份依据 Haskell 第21章书目（印刷页429）列出的法文题名、纪念展说明、Bibliothèque Nationale、Paris 和1961年；不推定个人作者或出版者身份，图录未独立查阅。S5 提取6条书内 `source_backed` 字段（`enr-15765`–`enr-15770`），来源登记无变化。

S6 对第7章 p.176 注1与 p.181 注3的两条候选分别裁为 formal `cites`，共用一条关系 `rel-1366`，分别保留 L314 / p.176 n.1 与 L341 / p.181 n.3 两个证据跨度。裁决只确认 Haskell 的书内引注；图录及其 p. xxxiii 均未独立查阅。批后 S4 已登记1,394/4,803组、1,598/5,028条候选映射；待登记3,409组／3,430条映射，其中直接端点1,662组／1,662个候选／1,676条组成员映射、非直接1,747组／1,754条映射。S5字段12,001条（1,634条 `unverified`）；S6累计逐条裁决203/10,402条（141 formal、53 pending、9 rejected），关系表1,366条（1,363 formal、3 pending）。S2复核计数不变。逐项证据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-mazarin-exhibition-catalogue-citations-20261021)。

### S3/S4/S5/S6 archive：Loret、Wind 与 Torcellan 跨章引注（2026-10-21）

两篇新 archive 沿用既有 S3 `new` 组：`cand-6583` Loret（1934）和 `cand-7230` Wind（1939–40）；新增11条Haskell书目支持的 `source_backed` 字段。端点查重触发S3局部复核：`cand-10476` Torcellan 1963与既有 `units/archives/torcellan-andrea-memmo-1963` 为同一出版物，决定由 `new` 改为 `same`，不重复建卡。S6对六条明确书内引注逐条裁为 formal `cites`（`rel-1360`–`rel-1365`）；第8章 p.214 对 Loret 的阅读指引保持非关系。被引文献和页面未独立查阅。逐项证据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-archive-loret-wind-and-torcellan-citations-20261021)。

### S4/S5/S6 archive：第6章 Michaud 与 Roma 引注端点（2026-10-21）

沿用既有 S3 `new` 单成员组登记两项 archive：`cand-6571`（`archive-group-06ab78ee5350`）对应 Michaud 四卷本 *Louis XIV et Innocent XI*；`cand-6575`（`archive-group-e4f0548d6dd1`）对应 *Roma* XIX (1941)。两组身份沿用第21章书目与第6章脚注定位，不增加外部身份断言。按 Haskell 原书支持新增13条 `source_backed` 字段。

S6 对四条脚注候选逐条裁为 formal `cites`，登记 `rel-1356`–`rel-1359`。关系仅记录 Haskell 的书内引注；Michaud 各卷、Roma 卷册、报告、avvisi 及被引内容均未独立查阅。批后 S4 1,391/4,804组、1,595/5,029条映射；S5字段11,984条（1,634条 `unverified`）；S6累计195/10,402项裁决；关系表1,359条。逐项依据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-ch6-michaud-roma-citations-20261021)。


### S4/S5/S6 archive：Da Canal《Vita di Gregorio Lazzarini》跨章引注（2026-10-21）

沿用既有 S3 `new` 组 `archive-group-aa69e7e50bc3`，将 `cand-6593` 登记为 archive KU；第21章书目 L307 记作 *Vita di Gregorio Lazzarini (1732)*、Venezia 1809。括注原样保留，不赋予其未证实含义；作者人物候选 `cand-7781` 不与文献合并。按原书支持新增6条 `source_backed` 字段。

S6 对第6章 p.166 注2和第7章 p.195 注3两条关系候选逐条裁为 formal `cites`，分别登记 `rel-1354`、`rel-1355`。关系只表达 Haskell 的书内引注；出版物及被引页均未独立查阅。批后 S4 1,389/4,804组、1,593/5,029条映射；S5字段11,971条（1,634条 `unverified`）；S6累计191/10,402项裁决；关系表1,355条。逐条依据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-da-canal-cross-chapter-citations-20261021)。


### S2语义复核：第七章 p.200 Plate 32a–32b 图版簇（2026-10-21）

对照CHP-7.pdf物理页42复核常规OCR段 `chp-7:07_CHP-7_sec_v:l39-40` 与视觉转录段 `chp-7:07_CHP-7_sec_v_visual-transcription:l3-3`。共6条statement、8条mention，跨度全数精确；32b qualifier与Roomer／Shaftesbury mention中的旧S3状态已按当前same映射更新。两条creator候选已有对应formal边，不重复登记；“painted for”与神话人物subject候选留待S6按受控谓词和端点逐项裁决。S2本批复核增加6条至9,452/15,171（62.3%），第七章1,061/1,243；无statement、mention、S3、S4或关系表行数变化。逐项依据见[S2复核记录](../../03-processing/patrons-and-painters-full-book-s2/process/s2-independent-review-chp7-notes-20261021.md#第七章-p200-plate-32a32b-图版簇-s2-语义复核)。

### S2 语义复核：第七章 p.201 正文（2026-10-21）

对照 CHP-7.pdf 物理页43复核 `chp-7:07_CHP-7_sec_v:l42-55`：38条statement（原37条，拆分后增加1条）、97条mention；36条关系候选、2条非关系判断。修正 commander 跨页指代、Eugene 对 Venetian style 的分句、Pozzo 的 ceiling work 与受召事实；新增两条精确代词mention。原书 OCR 保留，必要读法维持在statement的校读元数据。天顶画候选与未具名 Emperor 的关系分别记为S6 pending；无formal边。S2计数增加38条至9,490/15,172（62.5%），第七章1,099/1,244。逐项理由见[S2复核记录](../../03-processing/patrons-and-painters-full-book-s2/process/s2-independent-review-chp7-notes-20261021.md#第七章-p201-正文-s2-独立语义复核)和[S6裁决](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s6-chp7-p201-pozzo-ceiling-and-summons-20261021)。下一段为 p.202 `chp-7:07_CHP-7_sec_v:l57-60`，随后核对 p.200 脚注 `l62-76`。

### S2语义复核与S3类型更正：第七章 p.202（2026-10-22）

对照 CHP-7.pdf 印刷页202、物理页44，逐条复核13条statement与15条mention；跨度和页图一致，未改S2行。确认 `cand-2663` 指向Turin城市而非抽象term，将其从S3 `new` 身份组修订为 `same` → `units/places/turin`，类型更正为 `place`；没有新增S6关系。该13条计入统一逐条复核后，全书为9,503/15,182（62.6%），第七章1,112/1,252；两者均未接收。下一游标是第七章复合脚注 `chp-7:07_CHP-7_sec_v:l62-76`。详细证据及逐条理由见[复核记录](../../03-processing/patrons-and-painters-full-book-s2/process/s2-independent-review-chp7-notes-20261021.md#第七章-p202-正文-s2-逐条语义复核)与[身份裁决记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-chp7-p202-turin-type-correction-20261022)。

### S2/S4/S5/S6：第2章木制烛台与十字架直接端点（2026-10-22）

第2章印刷页43、PDF物理页28的独立复核指出，两条Cardinal S. Onofrio订置陈设的statement引文截断于“sent them to”。已修正两条 `original_quote`，纳入来源L143中的“the church”；不增删statement，不改变S2统一复核计数。保留现有S3新组，分别登记十二支木制烛台和两件木制十字架，未重开S3。两张卡各新增三条直接有据的S5字段（类型、数量、材质）。

S6逐项裁决五条候选：两条订置并送达候选以作品→提供者 `supplied_by` 裁为formal（rel-1390、rel-1391）；Capuchin修士退回两组物件的两条候选，以及Urban VIII坚持接收烛台的一条候选均裁为pending。来源虽然支持退还／接收事件，但当前受控谓词不能准确表达这些事实；不以`held_by`或`owned_by`替代。逐条理由见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp2-wooden-candlesticks-crucifixes-20261022)。

### 进度记录导航

当前统计、未决队列及后续工作规划统一见本文件顶部；以下为按批次保留的历史记录，历史段落中的累计计数不替代当前快照。

### S2语义复核与S6待证裁决：第七章 p.200 正文（2026-10-21）

对照 p.200 页图复核原有28条statement及70条mention，拆分和校正关系端点后该段共32条statement、71条mention；将政治变化、重要场合、介绍行为及共同作品制作中的开放角色保留在正确位置。新增四条原子关系候选均逐项裁为S6 `pending`，不生成formal边；`cand-7296` 因成为直接关系端点进入S4待登记队列。详见[S2复核记录](../../03-processing/patrons-and-painters-full-book-s2/process/s2-independent-review-chp7-notes-20261021.md#第七章-p200-正文-s2-独立语义复核)与[S6裁决](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s6-chp7-p200-atomic-relations-20261021)。本批后 S2 为9,446/15,171（62.3%），S6为211/10,406（143 formal、59 pending、9 rejected）；第七章仍未接收。下一游标为 p.200 `chp-7:07_CHP-7_sec_v:l39-40`，继而 p.201 `l42-55`。

### S2独立复核与S6裁决：第七章脚注段（2026-10-21）

独立核读并接收31条 statement（30条 relation candidate、1条非关系解释）和56条 mention span；修正Da Canal注页、Gennari注引文结构，并补齐von Freeden书名及同注印本校读记录。两条画作组地点陈述在S2保留、S6仅否决人物→地点图谱边，未新增关系表记录。逐条发现与接收依据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/s2-independent-review-chp7-notes-20261021.md)及[S6裁决](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s6-chp7-collective-picture-location-notes-20261021)。该批当时未单独增加汇总分子；随后p.199第V节14条已按statement ID去重归并，当前第七章1,023/1,239、全书9,414/15,167；第七章整体仍未接收。


### S2独立复核：第七章 p.199 第V节（2026-10-21）

逐条核读当前14条statement和46条mention span（印刷p.199、PDF物理页37）；12条为关系候选、2条为非关系陈述，46条span均精确对应登记源段。修正“Roman art”从Rome地点 `cand-4490` 到既有艺术生产领域term `cand-4631` 的错误映射，按来源语义保留其与城市Rome的区别；同步清理Maratta、Trevisani的过时待S3 mention备注。`cand-4631`既有S3 `new` 身份组决定不变。statement和候选总数不变；本段按statement ID去重后将独立复核更新为第七章1,023/1,239、全书9,414/15,167（62.1%）。该段接收不代表第七章整体接收；下一游标p.200 `chp-7:07_CHP-7_sec_v:l9-18`。逐条依据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/s2-independent-review-chp7-notes-20261021.md)。

### S3 archive：Da Canal《Vita di Gregorio Lazzarini》跨章身份（2026-10-21）

`cand-6593` 保留为单成员 `new` archive 组 `archive-group-aa69e7e50bc3`。第21章书目确认作品全名及 Venezia 1809 版；第6、7、9章中的 p.69、pp.71–73、pp.32–33、57、36 是同一作品的引注定位。已从候选规范名移除 locator，并与作者人物候选分开；未核读被引页或外部目录，S4登记及相应S6引注裁决仍待后续批次。决定数量不变。详见[裁决记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-da-canal-bibliographic-identity-locator-separation-20261021)。

### S4/S5/S6 archive：第3章 Jesuit Archives 引注簇（2026-10-21）

沿用八个既有 S3 new 档案组，补齐8张卡、8条映射及32条原书支持字段，并逐条裁决9条档案引注为 formal cites。Fondo di Gesù, N. 865-18 在两处脚注出现，身份组复用、两条引注分别记录；档案原件与馆藏均未独立核查。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp3-jesuit-archive-citations-20261021)。批后 S4 为1,388/4,804组、1,592/5,029条映射；S5为11,965条字段（1,634条 unverified）；S6累计裁决187/10,402条（127 formal、53 pending、7 rejected），关系表1,353条（1,350 formal、3 pending）。

### S4/S5/S6 archive：第7章书目引注端点（2026-10-21）

沿用11个既有 S3 `new` 跨章身份组登记为 archive，新增44条由第21章书目支持的字段，并将14条第7章书内引注逐条裁为 formal `cites`。卡片、manifest、accepted units、alignment 与正式关系表均已对应；书目与引文仅作为 Haskell 记录，不代表被引作品或页码已独立核验。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp7-bibliography-endpoints-20261021)。批后 S4 为1,380/4,804组、1,584/5,029条映射；S5为11,933条字段（1,634条 `unverified`）；S6累计裁决178/10,402条（118 formal、53 pending、7 rejected），关系表1,344条（1,341 formal、3 pending）。

### S4/S5/S6 archive：Monaco—Strange书信与Algarotti书目端点（2026-10-20）

沿用既有S3 `new`组登记3个archive端点，新增9条来源支持字段，并对7条S2关系候选裁为4 formal、3 pending。正式边为`rel-1319`–`rel-1322`；未解决项保留清单端点与谓词缺口、相对年代无法用现有谓词表达、出版地缺少受控谓词。书信日期保留“4 February 1763/4”的原排法；书目版次和手稿均未独立核查。逐条决定、依据与边界见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-monaco-and-algarotti-bibliographic-endpoints-20261020)。

### S4/S5/S6 archive 与 institution：Algarotti—Bonomo 特雷维索书信簇（2026-10-20）

登记4个既有 `new` 身份组：大型特雷维索书信汇集、其中来自巴黎的1734–1736年书信子集、1741年9月5日致Bonomo的书信，以及原书称作Archivio Comunale in Treviso的机构。新增10条由Haskell第14章支持的字段；7条直接关系候选逐条裁为6 formal（`rel-1313`–`rel-1318`）和1 pending。巴黎地点候选因 `originated_from` 无受控映射而保留pending；书内“from Paris”未被改写为保管地点。手稿、档案系列和当前馆藏均未独立核查。批后S4登记1,362/4,804组、1,566/5,029条映射；S5为11,859条字段（1,634条 `unverified`）；S6关系表1,318条（1,315 formal、3 pending），逐条裁决累计149/10,402（92 formal、50 pending、7 rejected）。逐项理由见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-treviso-algarotti-correspondence-20261020)。

### S3/S4/S6：六个直接机构／职位端点及逐候选裁决（2026-10-20）

登记五个既有 S3 `new` 机构组和一个按原文“given the post”校正为 term 的职位组，共新增6张 KU 卡及6条候选映射。16条直接关系候选逐项有去向：5条 formal 合并为 `rel-1310`–`rel-1312` 三条边，11条 pending；没有为邻接、未具名作品、职位归属或市政请求强制套用其他谓词。修正三条 S2 qualifiers，statement 总数15,167、独立复核9,400/15,167不变。每条证据与理由见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s6-direct-institution-batch-20261020)。

### S4/S5/S6 archive：三组跨章文献端点与六条引注（2026-10-20）

登记 Claretta（1893）、Tassi《Vite》卷 II（1793）及 Whinney–Millar（1957）三个既有 S3 身份组；新增17条书内来源字段，并修正 Wilhelm、Sweetman 卡片11条字段的来源标记，S5 `unverified` 仍为1,634。六条跨章明确引文裁为 formal `cites`（`rel-1304`–`rel-1309`），仅表示 Haskell 书内引注，不表示已查阅被引页面。`cand-6076` 日记／版本身份仍待证；第10章 Claretta 语句未进入本批关系裁决。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-archive-cross-chapter-citations-20261020)。

### S4/S5/S6 archive：Sweetman《Shaftesbury’s last commission》及第7章引文（2026-10-20）

沿用 `cand-7268` 的 S3 `new` 身份组登记为 archive KU；第21章书目支持题名、书目署名、期刊、年份与页码。第7章 p.199 n.1 明确引用 pp. 110–116，故对应 S6 `cites` 候选裁为 formal，新增 `rel-1303`。作者全名和被引文章内容未独立核验，不建作者人物或 `authored_by` 边。新增7条书内 `source_backed` 字段；OCR原文与页图校读分开保留。过程记录：[Sweetman archive 与引文裁决](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-sweetman-last-commission-20261020)。

### S4/S6 archive：Pintard《Le libertinage érudit》及第4章跨章引文（2026-10-20）

登记既有 S3 `new` 组 `cand-4547` 为一张 archive 卡；书目责任者仍按“Pintard, R.”保留，作者人物身份待证。第4章两条明确的 S2 `cites` 候选逐条裁为 formal，分别记录 p.107 n.2 的第2章指引和 p.108 n.2 的 p.238 引用。原书与被引内容均未独立查阅。过程记录：[Pintard 文献与跨章引文批次](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s6-pintard-book-cross-chapter-citations-20261020)。

### S4/S5/S6 archive：跨章引文端点与三组文献登记（2026-10-20）

`cand-5718`、`cand-10475`、`cand-10535`登记为三张archive卡；`cand-11271`与`cand-10535`依第15章p.369 n.4及第21章书目p.417所载作者、年份和页码合并到同一Brunelli文章组，登记四条候选映射。新增20条由Haskell书内引文支持的字段；Molmenti p.368 n.1保留OCR原引句并另记印刷页“ff.”校读。9条两端齐备的S2关系候选逐条裁为formal，登记`rel-1284`–`rel-1292`；被引文章、信件和版本均未声称独立查阅。字段同步、卡片关系渲染、关系一致性及严格结构审计结果见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-archive-citation-endpoints-batch-20261020)。



### S4/S5/S6 archive：Johann Philip Franz Schönborn 致 Friedrich Karl Schönborn 的书信（2026-10-20）

沿用既有 S3 `new` 组 `cand-9451`，登记一张 archive KU；Haskell 第10章 p.293 注4支持书内记载的发信人、收信人、日期与介绍 Pellegrini 的内容，不代表原信或 Von Freeden（1955）p.848 已独立查阅。新增六条 `source_backed` 字段，三条直接关系候选逐条裁为 formal：`rel-1281`、`rel-1282`、`rel-1283`。同时修正阿尔蒂耶里宫《仁慈》壁画卡六条字段的来源序号／原始表格快照；来源ID仍为 `haskell-1980-rev-ed`，没有全局重建其他字段。逐项依据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-direct-archive-letter-franz-schonborn-1723-20261020)。

### S4/S5/S6 place：Palais du Luxembourg 直接端点登记（2026-10-20）

沿用 S3 `new` 组 `cand-1461` 登记为[卢森堡宫地点卡](../units/places/palais-du-luxembourg.md)，新增4条由第7章 p.174 支持的结构化字段。四条直接 S2 候选逐条裁决为1 formal、3 pending；formal 边 `rel-1280 commissioned_by` 仅记录1611年建造委托，不声称工程完成。场址上较早的宫殿 `cand-6683` 继续待证；未作外部建筑身份或现状核验。逐项理由见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s6-place-palais-luxembourg-20261020)。

### S4/S5/S6 term：巴洛克天花板装饰与英国对意大利艺术影响（2026-10-20）

登记既有 S3 `new` 的两个术语组：巴洛克天花板装饰类型、英国对意大利艺术影响主题。两卡新增10条 `source_backed` 字段，依 Haskell 第2章 p.101、第7章 p.195–196 保留其艺术史评价与时期限定。8条直接关系候选逐条裁为6 pending、2 rejected、0 formal；术语端点组合不符合当前域值域矩阵，且两条被否决候选分别是无第二端点的单端描述、明确归因于德国赞助者的叙述。`relations.csv` 未增加边。逐项依据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s6-term-barq-ceiling-and-english-impact-20261020)。


### S4/S5/S6 archive：第15章 Memmo—Strange 与 Strange—Sasso 两封书信（2026-10-20）

两个既有 S3 `new` archive 组分别登记为 Memmo 致 John Strange 的 Egerton MSS. 1969, no. 80 书信，以及 John Strange 于1777年10月8日致 G. M. Sasso 的书信。后者依第16章 p.373 注2只记录 Haskell 报告的 Epistolario Moschini／Biblioteca Correr 集合级定位，不补单件索书号；前者保留 `18 October [1775]` 的方括号。两卡共新增10条 `source_backed` 字段。六条直接关系候选逐条裁决为5条 formal、1条 pending；formal边为 `rel-1275`–`rel-1279`。绘图请求未证明图样完成且无准确受控谓词，继续待决。原件和馆藏记录均未独立查阅。依据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s6-chp15-strange-memmo-letters-20261020)。


### S3/S4/S5/S6：Saint-Saulveur 书信与直接人物端点（2026-10-20）

登记既有 S3 `new` archive 组 `cand-5813` 与 source-local person 组 `cand-5815`，新增两张 KU 卡、4条 source_backed 字段及 `rel-1274 addressed_to` 正式边。`cand-4159`（“Her Majesty the Queen”）保留为 source-local 称谓候选，未登记人物KU；相应的复制许可候选明确判为 pending，因为来源未指出具体君主，且当前谓词表没有对应的复制许可关系类型。原信及 Peiresc 卷III第252页均未独立查阅。批次后 S4 已登记1,332/4,805组、1,535/5,029条映射；S6关系表1,274条（1,271 formal、3 pending）。逐条依据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s6-direct-endpoints-saint-saulveur-20261020)。

### S4/S5/S6 archive：La Educazione Virile 两种语言版本（2026-10-20）

登记既有 S3 `new` 组 `cand-9806` 为1张 archive KU，并补入7条由 Haskell 第10章 p.326–327支持的 `source_backed` 字段。四条直接关系候选逐条裁决：3条 formal（发行、出版地、书内报告的 Correr 馆藏位置），1条 pending（“Riviera’s own”不足以区分作者责任与发行责任）；原件、目录及当前馆藏未独立查阅。本批后 S4 已登记1,330/4,805组、1,533/5,029条映射；S6关系表1,273条（1,270 formal、3 pending）。逐项证据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-archive-la-educazione-virile-20261020)。


### S4/S5/S6 archive：第3章与第7章书目引注端点批次（2026-10-20）

登记三个直接 archive 组及其 S3 既有决定；另登记 Bonnaffé 书目责任者已有的 S3 新人物组，作为该 archive 必需责任者字段的依赖。S5 从 Haskell 原书为三张 archive 卡新增19条 source_backed 字段；不新增外部核验。九条直接 `cites` 候选逐条判为 formal，映射到三条关系记录；被引文献及页码均未独立查阅。Lanckoronska 与 Baldinucci 责任者形式保留其身份未决边界；不新增作者关系。批次后 S4 为1,329/4,805组、1,532/5,029条映射；S6关系表共1,269条。逐条证据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-archive-ch3-ch7-bibliographic-citations-20261020)。


**全书当前阶段状态、统一计数及未决范围见上方“当前全书阶段总览”。**

### S4/S6 archive：Missirini（1823）跨章引注（2026-10-20）

登记既有 S3 `new` 组 `cand-6361`，新增1张 archive 卡；第1、6章三条 S2 引注候选逐条裁决为 formal，映射至 `rel-1265`、`rel-1266` 两条 `cites` 边。只记录 Haskell 书目与脚注中的出版物指向，不声称查阅原书或被引页；新增7条由 Haskell 书目与脚注锚点支持的结构字段。人物候选 `cand-3538` 仍保持原 S3 待决状态。逐条证据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s6-cross-chapter-archive-missirini-1823-20261020)。

### S4/S6：第六章拉特朗改建与宗徒之椅（2026-10-20）

登记三张直接关系端点 KU 卡；对11条 S2 关系候选逐项裁决，5条 statement 映射到3条 formal 关系（`rel-1254`–`rel-1256`），另有3条 pending、3条 rejected。完整端点、证据与理由见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s6-ch6-lateran-apostles-chair-20261020)。

### S4/S6 archive：Röthlisberger 与 Mahon 的跨章引注（2026-10-20）

登记 `cand-4371` 的新 archive 组；`cand-4577` 已复用既有两卷本 archive 卡，不另建卷I卡。七条 S2 引注候选均裁决为 formal，映射到六条 `cites` 记录 `rel-1257`–`rel-1262`；仅记录书目引用，不验证被引页内容。完整证据、范围和理由见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s6-cross-chapter-archive-citations-20261020)。

### S4/S6 archive：Ruffo 与 Prunières 两篇跨章引注（2026-10-20）

登记 `cand-6454` 的1916年期刊文章与 `cand-4861` 的1913年出版物，共新增2张 archive 卡；六条 S2 引注候选逐条裁决为 formal，分别映射至 `rel-1263`、`rel-1264` 两条 `cites` 边。只记录Haskell书目引注，不声称核实被引文献内容。逐条证据和范围见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s6-archive-publication-citations-20261020-ruffo-prunieres)。

### S6：关系表45条来源ID回补（2026-10-20）

原有45条关系记录（44 formal、1 pending）均已绑定有效 `source_id`，32条复用来源表既有记录，12条关联至6条新增来源记录，另1条切换到已登记的同版 Warburg PDF。3条旧定位更新为可确认的当前地址；rel-1226 仍为 pending。来源登记总数现为1,758，关系状态与候选端点未变。完整来源映射与依据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s6-relation-source-id-reconciliation-20261020)。

### S2／S4／S6：圣依纳爵教堂走廊与拱顶端点簇（2026-10-20）

第3章 p.89–90 的两条说话者误归 statement 已改为 Haskell 作者叙述；新增 Pozzo 分场与描绘的关系候选，原文引句已与来源行核对。S4 登记 cand-5365、cand-5366、cand-5368、cand-5389、cand-5390 五个既有 S3 new 组，共新增5张KU卡及5条候选映射。S6 对本簇19条候选逐项裁决：9条 formal、9条 pending、1条 rejected；formal 边为 rel-1243–rel-1251。详细证据、端点与理由见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s6-s-ignazio-endpoint-cluster-20261020)。新增S2 statement尚未纳入独立复核；第3章当前1,173/1,174条已复核，仍不接收。


### S4 archive：六组直接文献端点登记（2026-10-20）

沿用既有 S3 `new` 组，为 `cand-4830`、`cand-5461`、`cand-5745`、`cand-6239`、`cand-6576`、`cand-5467` 新增六张 archive 卡：Bottari/Ticozzi《Raccolta》卷 I、III，P. Olina 的 *Uccelleria*，Limentani 论 Salvator Rosa 的诗歌与书信，Hantsch–Scherf 的 Schönborn 研究资料卷，以及 Tacchi-Venturi 论 Gaulli 与耶稣会总会长的出版物。身份依第21章书目和原书卷次／题录引用记录；不宣称查阅具体印本或被引页。本批未新增外部身份或 S5 字段。

二十条直接 S2 关系候选仍待 S6：十九条的另一端已有 KU，Resta 致 Ghezzi 信的一条另一端仍缺 KU。端点可解析不代表关系获准。第8章三个卷 III statement 的 ID 标为 p.217、p.218、p.220，但当前 source anchors 指向 OCR L375、L376、L379（来源页标记241）；卷 I 第4章 S2 页码标签与当前来源页标记也有待核对。Limentani 书目年份 OCR 为“!95O”，Hantsch 作者拼写在脚注 OCR 中有异文；这些转录问题与关系裁决分开保留，均不在本批改写 S2 statement。

调整后 S4 已登记1,309/4,805组、1,511/5,028条映射，待登记3,496组／3,517条；直接关系端点待登记1,744组／1,744个候选／1,758条成员映射，其中 archive 为471组／476成员；非直接队列为1,752组／1,759条映射。KU=2,328。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-archive-bottari-ticozzi-volumes-i-iii-20261020)。


### S4 term：两个直接关系端点登记（2026-10-20）

沿用 S3 的两个 `new` 组，登记 cand-6065（中等与较低社会地位人群）及 cand-4294（教宗政府国务秘书职位）。第5章 pp.130、132、136 直接支持前者的意大利语类别及其来源限定；第2章 p.28 与第6章 p.147 支持后者的职位用法。卡片将社会类别与固定成员名单分开，将职位与任职人物、政府机构分开，均未补写外部事实。两组关联的7条直接 S2 关系候选，其另一端均已有 KU；全部仍留待 S6 逐条裁决，本批未改写 S2 statement、mentions、enrichment 或 relations.csv。

S4 更新为已登记1,311/4,805组、1,513/5,028条候选映射；待登记3,494组／3,515条。直接端点待登记1,742组／1,742个候选／1,756条组成员映射（其中术语526组／526成员）；非直接队列1,752组／1,759条映射；KU=2,330。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-term-endpoints-20261020)。

### S6：两个术语端点关联的七条候选裁决（2026-10-20）

本批对第2、5、6章7条两端 KU 已登记的 S2 关系候选逐条裁决，7条均为 pending：候选有直接来源锚点，但当前受控关系类型和值域不能表达 person/term 或 term/term 组合，且其中起源、客群判断带 Haskell 的推断限定。无 formal 边或新增关系类型；`relations.csv` 未改动。逐条去向与理由见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s6-seven-term-endpoint-candidates-20261020)。

### S4 work：密西西比画廊壁画装饰方案（2026-10-20）

沿用既有 S3 `new` 组 `workgrp-ac7a28ee4bbeb5`，登记 cand-8964 为[佩莱格里尼为密西西比画廊创作的壁画装饰方案](../units/works/pellegrini-mississippi-gallery-fresco-programme.md)。第10章 pp.284–285 将对象描述为为 Banque Royale 内 Mississippi Gallery 制作的装饰方案／壁画组；本书未给作品原题，名称保持描述性，Royal glorification、商业寓意及 Système 崩溃后的毁损均按 Haskell 原文限定。本批登记一张 work KU 和一条候选映射；不新增外部身份或 S5 字段。

对该对象关联的4条 S2 关系候选逐条记录 S6 pending：一条是任务委派而非受控的创作者／委托边；两条记载方案内容与指示，但当前无对应端点组合和受控类型；一条把壁画毁损与金融方案崩溃相连，当前无受控时间限定毁损关系，且 cand-8966 指向金融方案 term、不是“崩溃”事件。本批未新增 formal 边或类型，`relations.csv` 未改动。S4 已登记1,312/4,805组、1,514/5,028条映射，待登记3,493组／3,514条；直接关系端点待登记1,741组／1,741个候选／1,755条成员映射，其中 work 为326组／335成员；非直接队列1,752组／1,759条映射；KU=2,331。S6 已在过程记录中逐条裁决11条 S2 候选，11条均为 pending。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-work-mississippi-gallery-programme-20261020)及[四条裁决](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s6-four-mississippi-gallery-candidates-20261020)。

### S3 same／S4 place：Palazzo Pitti 复用与圣母小堂登记（2026-10-20）

`cand-1949` 原列为单成员 `new` 组，但其来源名称 “Palazzo Pitti” 与既有同类型地点 KU `units/places/palazzo-pitti` 相同；核对既有卡片、索引候选及第2、7、8章相关原文后，改为 `same` 并复用该 KU。其4条直接 S2 关系候选现在可映射至现有地点端点；不新建重复卡。

`cand-5348` 沿用既有 S3 `new` 组 `sg3-place-cand-5348`，登记为描述性地点卡[奎里纳尔圣安德烈堂圣母小堂](../units/places/chapel-of-the-madonna-s-andrea-al-quirinale.md)。第3章印刷页88称该小堂最后装饰、转述1691年耶稣会文书评价，并记载 Ottoboni 接手及 Pamfili 继承人的装饰权；名称保持描述性，与教堂本体、主礼拜堂及圣方济各·沙勿略小堂分立。4条直接 S2 关系候选仍待 S6 逐条裁决；其中两条另一端仍缺 KU。本批不新增外部身份、S5字段或正式关系。

调整后 S3 为 same=2,024、new=5,028/4,805组；S4 已登记1,303/4,805组、1,505/5,028条映射，待登记3,502组／3,523条映射。直接关系端点待登记队列为1,750组／1,750个候选／1,764条成员映射；非直接队列为1,752组／1,759条映射。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-place-pitti-madonna-chapel-20261020)。

### S4 term：三个跨章术语直接端点登记（2026-10-20）

沿用既有 S3 new 决定，将 cand-4397、cand-11643、cand-1729 分别登记为[贝尼尼华盖图像方案术语](../units/terms/bernini-baldacchino-iconographic-scheme.md)、[真实古典绘画路径术语](../units/terms/true-classical-painting-path.md)及[那不勒斯绘画传播术语](../units/terms/diffusion-of-neapolitan-painting.md)。三组均有书内来源锚点；未新增候选裁决、外部身份、S5字段或formal关系。14条直接 S2 关系候选中，按当前对齐映射有8条两端均能解析至 KU；这只表示端点映射可用，不代表 S2 语义接收或 S6 成边。独立审读指出 cand-1729 对应的第8章 p.210 委托断言把传播术语当成委托对象，且 cand-7485 人群候选类型也有误，需先修 S2；第2章 p.35 另有 cand-4397 的 statement/mention 映射差异。登记后 S4 为1,295/4,806组、1,497/5,029条映射，待登记3,511组／3,532条；直接端点待登记1,759组／1,759个候选／1,773条成员映射。全过程见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-term-direct-endpoints-crosschapter-20261020)。


### S4 event：第5、10章展览直接端点登记（2026-10-20）

`cand-11770`与`cand-11771`分别登记为1675、1697年 S. Salvatore in Lauro 的具体展览场次，保持与既有常规系列卡分立；`cand-9872`登记为1777年开始、至1787年时已停办的威尼斯学院皮亚泽塔年度展览系列，不补推末届年份。共新增3张双语事件卡和3条候选映射。11条直接 S2 关系候选仍留待 S6；没有新增正式关系、S5字段或外部身份行。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-event-direct-endpoints-exhibitions-ch5-ch10-20261020)。


### S4 work：四个直接关系端点登记（2026-10-20）

沿用既有 S3 new 身份组，新增[圣比比亚娜像](../units/works/bernini-saint-bibiana-statue.md)、[保罗·焦尔达诺二世蜡制头像模型](../units/works/bernini-wax-head-model-paolo-giordano-ii.md)、[保罗·焦尔达诺二世骑马像模型](../units/works/tacca-modello-equestrian-statue-paolo-giordano-ii.md)及[为莱昂纳多·维涅尔制作的波莱尼侯爵像](../units/works/canova-poleni-statue-for-leonardo-venier.md)四个 work KU，各对应一条既有候选映射。S4 当前为1,302/4,806组、1,504/5,029条候选映射；待登记3,504组／3,525条映射。12条关联 S2 关系候选仍待 S6 按原文逐条裁决；本批未新增正式关系、S5字段或外部身份。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-direct-work-endpoints-four-20261020)。

### S2 定点修订：第8章 p.216 提及与来源限定（2026-10-20）

依据独立语义复核，对 st-chp8-p216-massimo-response-and-no-further-work 将“the governors were pleased”改为不识别指代对象的“the unnamed actors referred to as ‘they’ were pleased”，并删除与印本不符的 promise-of OCR correction。补入6条精确 mention span，并将 cand-7640、cand-12367 补入各自 statement 的 mention 映射。S3 身份决定、候选类型、关系裁决和 statement 总数未变；第7章 p.197 与第8章 p.215–216 其他复核发现仍待修订。证据与逐项范围见[阶段记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md#2026-10-20-s2-review-followup)及[知识处理记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s2-targeted-repair-ch8-p216-mentions-20261020)。

## 范围与覆盖

S0 登记79个来源文件、832段，涵盖书前材料、第1–17章、结论、附录、第二版后记、书目和索引；其中42段为派生视觉转录。第11、12章复用第10章合订规范来源，44段重复 OCR 已有依据地排除，不重复计算正文阅读。来源资产、规范文本与对照副本的区别见[来源登记](../../02-sources/source-registry.md)。

| S2 coverage 登记 | 段数 |
|---|---:|
| reviewed / complete | 678 |
| 有理由排除 / complete | 154 |
| queued 或迁移未完成 | 0 |
| 合计 | 832 |

正文、脚注、图版题注、跨页续句和书内引用均按既有过程记录处理。书目作为出版记录和引文定位材料，索引作为候选定位材料，不将两者当作正文断言。纸本索引终审覆盖 p.443–474 的32页，2,934个索引行均有对应候选或有理由的排除记录。范围登记和结构检查不能单独证明召回完整或事实准确。

## 当前产物与检查

| 产物 | 当前规模／状态 |
|---|---|
| [KU 登记](../tables/ku-manifest.csv) | 2,773 KU；新组登记与待登记分类型统计见下表 |
| [实体候选](../tables/entity-candidates.csv) | 12,408 candidates（新增 Callot《La Fiera dell'Impruneta》版画 work 候选；含直接关系端点候选 Luigi Pavini、Alessandro Farnese 公爵与 Paul Bonnefon） |
| [提及账本](../tables/mentions.csv) | 26,644 mentions |
| [原书断言及关系候选](../tables/book-statements.jsonl) | 15,171 statements；relation_candidate true 10,406、false 4,765、unset 0 |
| [覆盖账本](../tables/s2-coverage.csv) | 832段全部完成登记与迁移 |
| [全书对齐](../tables/alignment.csv) | 12,716 条：12,408 条候选决定记录及 308 条独立外部身份记录；候选决定数见下表 |
| [字段表](../tables/enrichment.jsonl) | 12,024条，其中1,634条 unverified |
| [来源登记](../tables/sources.csv) | 1,763 条来源记录 |
| [关系表](../tables/relations.csv) | 1,389条：1,386 formal、3 pending；0条缺结构化 source_id；S2另有10,417条relation_candidate=true的statement，二者不是同一计数口径 |
| [候选待办](../tables/candidate-backlog.csv) | 5条记录：5条 completed、0条 pending；既有对象与待决关系端点分别处理 |

当前statement表中335条 S2 关系候选至少一端尚无候选ID，分布于128个来源段：仅缺 object 218条、仅缺 subject 45条、两端均缺72条。其中327条以 relation_candidate_note、8条以 open_endpoint_reason 说明端点缺口；这些仍是 S2 候选，不是 S6 正式关系。具体身份、群组边界、版本与指代限定在对应 statement 的 qualifiers 中保留。HEAD基线为333条（仅缺subject 43、仅缺object 218、两端均缺72）；本次p.200语义修订将两个未具名主语保留为空，因此当前增加2条。

### S4 place：Chiesa Nuova旁的Oratorio建筑直接关系端点登记（2026-10-20）

cand-1784 沿用既有 S3 new 身份组，登记为描述性来源局部 place KU。哈斯克尔称该建筑毗邻 Chiesa Nuova、供图书馆及宗教音乐会使用，并记载 Virgilio Spada 选择 Borromini、其于1637年受请设计并开始工作。五条相关 S2 关系候选保留待 S6 逐条裁决；无外部身份核验、S5补足或正式关系写入。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-place-oratorio-direct-endpoint-chp3-20261020)与[知识卡](../units/places/oratorio-adjoining-chiesa-nuova.md)。

### S4 place：Ruffo在费拉拉使用的总主教宫登记（2026-10-20）

`cand-2306`（Q-R.csv#234）沿用既有 S3 `new` 组，登记至[费拉拉总主教宫卡](../units/places/palazzo-vescovale-di-ferrara.md)。Haskell称 Ruffo 的画廊收藏存放在该宫，称其1710年由 Tommaso Mattei 为 Ruffo 建造、毗邻未具名座堂；脚注所引手稿未直接查阅。五条相关 S2 关系候选留待 S6，新增5条仅由哈斯克尔原书支持的结构化字段；未新增外部身份或外部补足、正式关系。登记后 S4 已登记1,275／4,807组、1,476条映射，待登记3,532组／3,552条；直接端点队列为1,779组／1,779个候选／1,792条成员映射，其中 place 230组／230成员。KU=2,294。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-place-palazzo-vescovale-ferrara-direct-endpoint-ch8-20261020)。

### S4 place：帕姆菲利家族／教宗宫殿（Piazza Navona）登记（2026-10-20）

`cand-1824` 沿用既有 S3 `new` 身份组，登记为[纳沃纳广场宫殿卡](../units/places/palace-on-piazza-navona.md)。第3章 p.77 与第6章 pp.147–149 共同支持其为同一处纳沃纳广场宫殿；卡片使用描述性名称，不宣称正式建筑名、现代建筑身份或现状。四条直接以该地点为端点的关系候选及四条仅将其作为地点语境的候选均留待 S6；未新增formal边、S5补足字段或外部身份链接。登记后 S4 已登记1,276／4,807组、1,477条映射，待登记3,531组／3,551条；直接端点队列为1,778组／1,778个候选／1,791条成员映射，其中 place 229组／229成员。KU=2,295。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-place-palace-piazza-navona-20261020)。

### S4 work：阿尔蒂耶里宫《仁慈》寓意天顶壁画（2026-10-20）

`cand-5990`、`cand-6466` 与索引候选 `cand-1528` 按既有 S3 `new` 组登记到 `units/works/altieri-clemency-fresco`，新增6条来源支持的结构化字段；未做外部身份／归属核验，未新增正式关系。触及的10条 S2 关系候选中，3条当前两端已映射到 KU，登记仅解除 S6 端点缺口，其余7条仍待补端点或保留开放对象。S4 当前为1,272／4,812组、1,468条已登记映射；待登记3,540组／3,560条映射，直接端点队列1,785组／1,785个端点候选／1,798条成员映射。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-work-altieri-clemency-fresco-20261020)。

2026-10-19 本批工作登记前 strict-stage 表审计通过：KU=2,218；candidates=12,407；alignments=12,715（12,407条候选决定、308条外部身份记录）、unlinked=0；enrichment=11,702（1,627条unverified）；sources=1,752；S4待登记new候选映射3,634条；errors=[]、s2_missing=[]。该较早批次历史快照记录为same=1,982（1,056个KU）、new=5,027（4,812个类型内身份组）、conflict=9、excluded=100、undecided=5,289（含622项未分类）；S4已登记1,201组／1,395条候选映射，待登记3,611组／3,632条，其中直接关系端点队列1,857组／1,857条。S2有10,399条relation_candidate=true statement；当前有330条空候选端点记录（仅缺object 217、仅缺subject 41、两端均缺72，125段）；S6关系表有1,237条formal和2条pending，行数不表示这些S2候选已逐条裁决。S6关系表45条缺结构化source_id（44条formal、1条pending）。new组无部分登记，same均指向有效且类型相符的KU，各候选决定均有理由记录。逐类型裁决及组信息见[过程记录的S3统计表](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#按类型决定数)。保留的warning包括S4待登记new候选映射3,632条、既有enrichment来源定位问题（enr-06678、enr-06937）及S2语义质量提示；结构检查不替代独立语义验收。308条额外外部身份记录单独保存；18条现行候选决定行本身同时包含外部来源信息。

### S4 person：第8章四个直接关系端点登记（2026-10-19）

`cand-7505` Giuseppe Manini、`cand-7658` Dora Coggiola、`cand-7734` Silvio Ubaldi 与 `cand-7736` Tiberio Cenci 按各自既有 S3 `new` 组完成 S4 人物登记。卡片仅收录原书姓名及对应语境，保留记述来源、致谢、未具名出版物和未查阅书信等限制；4条 S2 关系候选仍待 S6，不新增正式关系或外部身份事实。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-chp8-20261019)。

### S3–S4 work直接关系端点组：Pomerancio祭坛画与Legros临终像（2026-10-19）

`cand-5046`、`cand-5440` 沿用既有 `new` 决定，分别登记为单成员work组并各新增一张卡及一条映射。前者将原书无正式题名的 Pomerancio 祭坛画登记为描述性题名；Cardinal Baronio 同名领衔教堂端点仍未决。后者登记 Legros 的圣斯坦尼斯劳斯·科斯特卡临终多彩人物像，与同章 Maratta 在 S. Andrea 的祭坛画区分；注1所述迁移提议不代表实际搬迁。两组共计10条S2关系候选仍待S6逐条裁决；未新增S5外部补足或formal关系，新增12条源文本支持的卡内结构化属性。S4当前待登记直接关系端点队列由1,859组减至1,857组，work由340减至338；详见[工作端点S4过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-work-direct-endpoints-20261019)。

### S3–S4 跨类型身份批次：人物姓名链及两组档案端点（2026-10-19）

`cand-0105` 已按人物新组 `new-person:filippo-dangeli-napoletano-715dfcf2d8` 登记，四条候选身份提及映射至同一人物卡；S3 使用的 d’Angeli／Napoletano 姓名链依据原书跨章锚点、Treccani DBI 与 ICCD 记录。两条关系候选仍待S6，其中一条另有未具名侯爵端点。档案组 `cand-10534`、`cand-10567` 各新增一张卡及一条候选映射；前者保留书内 `Venezia 1787` 与书目 `à Padoue 1787` 的出版地差异，后者使用描述性暂题并注明原件和Levi卷册未独立查阅。三组均未新增正式关系或S5外部补足；10条相关关系候选仍按statement逐条待裁决。详见[跨类型S4过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-filippo-dangeli-and-archive-endpoints-20261019)。

### S3–S4 person：Cesare Baronio 跨章身份组登记（2026-10-19）

`cand-0250` 由待证改判为新人物组 `new-person:cesare-baronio-20261019`，已登记至[Cesare Baronio人物卡](../units/persons/cesare-baronio.md)。Treccani DBI“BARONIO, Cesare”确认其规范姓名与奥拉托里会／枢机身份；第3章 p.69、p.71及第4章 p.109的称名与之相合。该判断只解决人物身份，不确认教堂端点或关系谓词。Rubens指示与Gaudenzi引语两条关系候选现有完整人物端点，仍待S6；titular church候选因 `cand-5050` 尚待身份裁决。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-person-baronio-cross-chapter-20261019)。

### S6：三位一体会建筑关系批次（2026-10-19）

第3章 p.75–76 的11条关系候选现分为5条 formal（`rel-1228`–`rel-1232`）、1条因匿名原驻地端点未决而 pending、5条评价或转述候选不建图谱边。新增受控关系 `entrusted_to_build` 记录教堂、修道院于1634年被委托给 Borromini 建造；它不表示工程已经开工或完工。待证端点 `cand-5121` 保持 S3 undecided，没有用 Spain 地理实体替代未具名原驻地。判断依据与逐条去向见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s6-trinitarian-commission-site-migration-20261019)。

2026-10-19 定点校正第七章 p.185 注2–4的引用定位：脚注原文仅列作者与页码，链接出版物由唯一对应书目项映射；此前误写入的两个不符书名已移除。S3身份端点、全书统计及关系状态未变，所引页面仍未独立阅读；细节见[阶段过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)及修订脚本。
历史过程快照（2026-10-19，后续 S4 登记前）：待登记直接关系端点队列按类型（组／全部候选成员；括号为直接端点候选数）为：person 30／30（30）、institution 96／96（96）、event 144／144（144）、place 232／232（232）、work 337／348（338）、archive 478／482（478）、term 539／539（539）；合计1,856组、1,857个直接端点候选、1,871条组成员映射；不含已复用、已登记或没有直接承担关系候选端点的new组。历史全库预检（2026-10-19、本批前）通过且未写卡片。本批 `build_cards.py --check` 只读预检显示2,213张卡、3,238张表、11,702行、预计关系派生2,454行、475张卡／487个文件有派生差异，未写卡片。当前只对本批两个关系端点卡片进行定点预览与渲染，全库派生视图仍有历史差异待处理。
2026-10-19 Bellori 1976跨章版次组：cand-4377、cand-11157、cand-10981合并至同一archive KU并完成S4；Braidense OPAC RAV0025303与第21章唯一书目项支持身份。两条直接关系候选端点现齐备、仍待S6；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-archive-bellori-1976-cross-chapter-group-20261019)。
2026-10-19 最新人物端点批次复核20个单候选组：4组改为 `same` 并复用既有人物 KU，16组保持 `new` 且完成 S4 登记。身份判断、边界和外部身份依据见[批次过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-person-endpoints-20261019)；关系候选仍待 S6，本批未新增正式关系。
2026-10-19 四组人物端点登记（批次快照）：cand-2685、cand-2700、cand-7353、cand-5833各保留既有S3 new身份组并新增一个person KU；cand-7353另有Treccani DBI身份入口。该批后S4登记至1,181组／1,369条候选映射，待登记为3,630组／3,651条；直接端点队列为1,875组／1,875条（person 31组／31条）。四条S2关系候选留待S6；无formal relation或enrichment新增。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-person-endpoints-varda-della-valle-carlo-emanuele-tamizey-20261019)。
历史快照：1,902组是2026-10-19二十组人物批次完成前的数值；1,882组／1,883条是该批完成后的中间数值；1,880组／1,881条为其后四组人物登记后的中间数值，Bottari档案登记再将直接端点队列降至1,879组／1,879条；随后四组人物端点批次后的历史数值为1,875组／1,875条。Alazard／Strozzi批次前为1,864组／1,864条；该批后为1,863组／1,863条；Hautecœur档案登记后曾为1,862组／1,862条。
2026-10-19 回填73条具唯一来源证据的关系 `source_id`；剩余45条（44 formal、1 pending）仍待消歧或补来源依据。关系状态与证据范围未改；详见[S6来源ID修复记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s6-source-id-exact-url-repair-20261019)。

2026-10-19 后续四组人物批次：cand-7034、cand-7036、cand-0657、cand-1448 均裁决为 `new` 并完成 S4，KU 总数增至2,195；其中 Catherine de’ Medici 与 Philip III of Spain 直接承担 S2 关系候选端点，直接端点待登队列由1,882组／1,883条减至1,880组／1,881条。查理二世与路易十五在本批仅作身份登记，不据此新增正式关系。详见[四组人物裁决记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-person-batch-four-20261019)。

2026-10-19 人物复用复核：`cand-1252`、`cand-1701`、`cand-4147` 从 `undecided` 改为 `same`，分别复用 Gian Antonio Guardi、Jacopo Morelli 与 Henry John Ralph Bankes 人物 KU；Bankes 与 17 世纪 Sir Ralph Bankes 分开。same 现为1,973条／1,052个目标KU，undecided为5,305条；不新增KU，相关关系仍须S6裁决。两条 statement 的 candidate endpoint 指派疑点已标注，不能据本次身份复用直接建边。详见[人物复用裁决记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-existing-ku-reuse-20261019)。
## S3 身份决定与交接

### S3–S4 person：Anton Francesco Gori 跨章身份组登记（2026-10-19）

`cand-1214`（G.csv#122，“Gori, A. F.”）与 `cand-10105`（第13章 p.344 的“Francesco Gori”）由 `undecided` 改为 `new`，组成 `new-person:anton-francesco-gori-20261019` 并登记为一个 person KU。第10章 p.299、p.328注2及第13章 p.342注6保留 A. F. Gori 的索引与书信语境；第13章 p.344称 Francesco Gori 为 *Dactyliotheca* 撰写拉丁文 commentary。Treccani DBI 对 Anton Francesco Gori 的身份条目及 Zanetti 条目提供外部身份对照。1749/1750年版年差异仍待证。4条 S2 关系候选没有转成正式关系；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-person-gori-cross-chapter-20261019)。本批新增1个 KU、2条候选映射及2条外部身份记录。

### S3 person：R. Longhi（Roberto Longhi）1956年文章署名复用（2026-10-19）

`cand-7603`（第8章 pp.212–213 注释中的“R. Longhi”）由 `undecided` 改为 `same`，映射到既有人物 KU `units/persons/roberto-longhi`（其新身份组由 `cand-5505` 建立并已登记）。第21章 p.428 书目将同篇文章列作 “Longhi, R.”，并提供题名、期号、年份和页码；Fondazione Roberto Longhi 的档案目录在 Roberto Longhi 的文献记录中列出同一题名的全写形式及 Paragone 75（1956）、pp.61–64，支持首字母作者形式与全名对应。文章未独立阅读。本次只处理人物身份；两条第8章 S2 关系候选仍留待 S6，不验证文章内容、作品归属或正式关系。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-longhi-1956-article-reuse-20261019)与[人物卡](../units/persons/roberto-longhi.md)。

### S3–S4跨章人物与直接关系作品／档案批次（2026-10-19）

人物 `cand-1106`、`cand-1108`、`cand-2349` 复用既有人物 KU；作品 `cand-5945` 与地点 `cand-5439` 由待新增组改为复用既有 KU；作品 `cand-5457` 与档案定位 `cand-5458` 两个新组已登记，见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-person-work-archive-endpoints-20261019)。新增2个KU；10条直接关系候选中8条已有两端KU映射并可交S6，另2条仍待 Josephus 身份与《圣经》档案端点补齐。本批未新增正式关系或S5外部补足；两张新卡新增9条书内结构字段。

### S3 person：Filippo d’Angeli（Napoletano）跨章身份裁决（2026-10-19）

`cand-0105`（A.csv#106）由 `undecided` 改为 `new`，分入 `new-person:filippo-dangeli-napoletano-715dfcf2d8`。第2章 p.29 的 Filippo d’Angeli（Napoletano）、第2章 p.50 的 Filippo Napoletano 和第4章 p.95 的同名风景画家语境相互衔接；Treccani DBI 与 ICCD 目录支持这组称名对应同一人物。索引 `cand-2920` 是 see-under，继续排除。旧决定理由保留在 alignment 行中；本次只完成身份裁决，不创建 KU 或正式关系。两条直接 S2 关系候选留待 S6。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-filippo-dangeli-napoletano-cross-chapter-identity-20261019)。

### S3 person：Antonio degli Effetti 索引主项与子项复用既有人物 KU（2026-10-19）

`cand-0966`（E.csv#1，pp.156、157）与 `cand-0967`（E.csv#2，p.157，“delight in idea of wealth”）由 `undecided` 改为 `same`，均指向既有人物 KU `units/persons/antonio-degli-effetti`。索引两行给出同一全名，页码与已登记候选 `cand-5974` 的来源范围重合；第6章 p.156 以全名介绍该人物，第6章 p.157 继续叙述其收藏和文学兴趣。第二条是同一人物的主题性索引子项，不是第二个人物。旧 undecided 理由留在各自 alignment 行历史注释中；无新增 KU、外部身份记录、enrichment 或关系。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-effetti-existing-ku-reuse-20261019)。

### S3–S4 跨章人物与档案登记：Jean Alazard／《L’Abbé Luigi Strozzi》（2026-10-19）

`cand-7098`（Jean Alazard）和 `cand-7099`（1924年《L’Abbé Luigi Strozzi correspondant artistique de Mazarin, de Colbert, de Louvois et de La Teulière》）沿用已作出的 `new` 决定，分别登记为 source-local person KU 与单成员 archive KU；本批不更改S3决定，也不增加外部生平事实。第7章注释与第21章书目把人物姓名和出版物连接起来；书目作者字段只作书内书目责任信息，没有增设 `authored_by` 关系候选。第7章 p.185、p.187、p.189四条注释引用登记为 `rel-1233`–`rel-1236` formal `cites`，所引页面未独立阅读。新增2个KU、2条候选映射及4条正式关系，直接关系端点待登记队列减少1组／1个候选。两张关联卡已定点同步，详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-alazard-strozzi-cross-type-batch-20261019)。

### S3–S4 archive：Hautecœur《L’Histoire des Châteaux du Louvre et des Tuileries》登记（2026-10-19）

`cand-7097` 沿用既有 `new` 决定，登记为单成员档案组并完成 S4；第21章书目记录责任者形式 `Hautecœur, L.`、原题及 Paris 1927。第7章 p.185 注2、注3及 p.187 注6 的三条 `cites` 候选登记为 `rel-1237`–`rel-1239` formal，定位依赖书目唯一项及注3的 ibid. 回指；被引页未独立阅读。责任者候选 `cand-7096` 仍为 S3 `undecided`（来源只有首字母），不扩写全名、不建立 `authored_by` 边。新增1个 KU、1条映射和3条正式关系，直接端点队列减少1组。[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-hautecoeur-1927-archive-registration-20261019)。

### S4 person：第20章后记六个直接关系端点登记（2026-10-19）

`cand-10865`、`cand-10877`、`cand-10902`、`cand-10967`、`cand-11125`、`cand-11148` 各保留原 S3 `new` 决定，登记为六张 source-local 人物卡；其中 Whitfield 的正文姓氏由第21章书目全名补足。卡片只记录原书对研究、出版、持有和未完成项目的报告，不补外部生平或确认正式关系；六条S2关系候选仍待S6。本批新增6个KU／6条映射，person待登记队列减少6组；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-postscript-20261019)。

### S4 person：四个正文篇章直接关系端点登记（2026-10-19）

`cand-2536`、`cand-2750`、`cand-2754`、`cand-2758` 沿用原 S3 `new` 分组，登记为四张 source-local 人物卡。Michael Sweerts 与 Leonardo Venier 由正文全名定位；Joseph Vernet 与 Pietro Verri 的正文姓氏分别由书后索引全名对齐。四张卡只保存书内语境及证据范围，不补外部生平或身份标识；四条关系候选仍待 S6。本批新增4个 KU／4条映射，person待登记减少4组；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-core-chapters-20261019)。

### S4 person：四个直接关系端点人物登记（2026-10-19）

`cand-4334`、`cand-5548`、`cand-5561`、`cand-6613` 沿用 S3 `new` 分组，登记为四张 source-local 人物卡。Hopf 的出版、della Greca 的可能奖章归属、van den Hecke 的 patronage 表述及 van Mander 的引文归属均按原书限定记录；四条关系候选仍待 S6。本批新增4个 KU／4条映射，person待登记减少4组；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-followup-20261019)。

### S4 person：第10章四个直接关系端点登记（2026-10-19）

`cand-9092` Pietro Guarienti、`cand-9429` Joseph Perrot、`cand-9830` Giuseppe Fossati 与 `cand-9835` Giacomo Storti 按既有 S3 `new` 单成员组完成登记，分别映射至四张人物卡。卡片只记录 Haskell 在第10章正文／脚注中的姓名及书内说法，并保留评价、归属和未独立查阅的限制；四条 S2 关系候选仍待 S6，本批未新增外部身份事实、补足字段或正式关系。直接人物端点待登记数降至8组。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-ch10-20261019)。

### S4 person：六组直接关系端点登记（2026-10-19）

本批沿用 S3 既有 `new` 身份组，将 Laurent de la Hyre、Valerio Castelli、Luca Ombrosi、Mucius Scaevola、Sebastiano Molino 与 Carlo VI, King of France 分别登记为人物 KU，并补齐六条候选映射。卡片仅保留书内姓名及语境：Ombrosi 的作者归属仍为“可能”；Scaevola 仅记为原书援引的罗马英雄人物；Molino 注释只作为文献定位，不据此确认相邻匿名赞语的作者；Carlo VI 所获豁免仍是未经独立核验的书内陈述。中文名均为项目工作译名／音译。六条相关 S2 关系候选仍待 S6，未新增外部身份事实、补足字段或正式关系。Her Majesty the Queen 与 Monsieur de Saint-Saulveur 因身份锚点不足仍保留待证。当前 S4 累计登记1,229组／1,423条映射，待登记3,583组／3,605条；直接关系端点待登记降至1,828组／1,829个候选／1,843条成员映射，其中人物剩2组。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-six-20261019)。

### S4 event：第3章六个直接关系端点组登记（2026-10-19）

本批按既有 S3 `new` 组登记圣母诞生、圣母奉献、圣母加冕、Chiesa Nuova 建造期间的圣母奇迹、Miguel de Molinos 于1664年的抵达，以及耶稣会在奎里纳尔山圣安德烈堂的祭坛画集体安排，共6组／6条映射。卡片保留来源限定：三项圣母奥迹不与同题祭坛画混并；奇迹仍是 Haskell 报告、未经独立核实，1664年只对应壁画委托；Molinos 抵达目的地未注明；祭坛画安排与教堂重建工程分开。九条相关 S2 关系候选仍待 S6，没有新增 S5 字段或正式关系。S4累计登记1,235组／1,429条映射，待登记3,577组／3,599条；直接关系端点队列为1,822组／1,823个候选／1,837条成员映射，其中事件端点余138组。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-event-direct-endpoints-chp3-20261019)。
### S4 event：第4章13个直接关系端点组登记（2026-10-19）

本批沿用既有 S3 new 组，完成 cand-5573、cand-5576、cand-5625、cand-5641、cand-5668、cand-5669、cand-5680、cand-5876、cand-5895、cand-5914、cand-5919、cand-5927 与 cand-5977 的事件 KU 登记。跨章皈依、脚注死亡年份、来信奇闻、版画题材与和约叙述均保留来源限定；19条相关 S2 关系候选仍待 S6。事件组累计登记59组／63条映射，待登记172组／172条。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-event-direct-endpoints-chp4-20261019)。

### S3–S4 institution：France 跨章身份组及直接端点登记（2026-10-20）

`cand-4221`、`cand-6253`、`cand-6704`、`cand-6764`、`cand-7223`、`cand-8308`六条既有 `new` 决定归并为`sg3-institution-france-polity`，登记到[法国政治实体卡](../units/institutions/france-polity.md)。地理法国、法国宫廷、法国君主制分别保留；France作为目的地的`cand-4632`待单独核对类型与指称范围，未并入。此组涉及11条S2关系候选，全部仍待S6逐项裁决；未新增formal关系或外部身份事实。S3 new候选数不变、身份组由4,812减至4,807；S4已登记1,273组／1,474条映射，待登记3,534组／3,554条。直接端点队列为1,781组／1,781个候选／1,794条成员映射；非直接队列为1,753组／1,760条映射。过程与验证见[记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-france-polity-crosschapter-20261020)。

### S4/S5/S6 archive：第14章四封书信身份组与关系裁决（2026-10-20）

沿用四个既有S3 new身份组，登记4张archive卡并新增21条由Haskell原书支持的字段。Mariette信的作者与收信人由p.351注2明示；Curli、Bonomo、Pesci三封信的作者归属取自正文与脚注的对应语境，四封信的收信人均有对应注释。八条S2关系候选逐项裁为formal并登记为rel-1323至rel-1330。OCR刊本卷次VW、VHI原样保留；信件原件、刊本与被引文献均未独立查阅。详见[逐条过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp14-algarotti-correspondence-20261020)。

### S3 复核：Modena 公爵候选改列待证（2026-10-16）

- `cand-1675`（M.csv#217）原列为 `new-person:modena-of-6566b00ada`／`new`，现改为 `undecided`，不登记KU；原组号与理由保留在alignment行中并标明已撤回。
- 索引将 p.143 与 p.177 注4列在同一“Duke of Modena”条目下，但这只是定位。p.143正文只称公爵，未给出所述画作请求的日期；p.177注4转述一封1645年书信，也只称公爵。没有全名锚点或已读的原始书信证明两处是同一人。原S3备注声称存在full personal-name anchor，与源文不符，现已更正。
- 保留9条关系候选及1条评价性非关系陈述；未将可能的不同公爵合并，也不拆分成缺少姓名依据的新候选。待核查能为p.143请求定年的原始记录或其他直接身份依据后再决定复用、新建或拆分。

### S3复核：Baglione人物子项与《The Resurrection》作品组（2026-10-16）

cand-0157（B.csv#4，Divine Love）由undecided改为new并入Giovanni Baglione人物组：同页正文全名及作品子项语境提供直接身份锚点。cand-5013（p.66 The Resurrection）与cand-5297（p.84 1602年耶稣堂祭坛画）归为一个new作品组，依据为同一画家、复活题材、耶稣会教堂语境及相容年代；题名和具体陈列状态不作超出原文的推断。两项工作组判断及旧理由均保留于对齐表和过程记录。

候选决定按每个 `candidate_id` 的现行决定统计，每个候选只计一次；308条额外外部身份记录不另算候选决定。当前18条候选决定行本身也带外部来源字段，仍分别按候选ID计数。

| S3 决定 | 候选数 | 去向 |
|---|---:|---|
| same | 2,048 | 指向 1,101 个既有 KU |
| new | 5,068 | 按 4,826 个当前身份组进入 S4；每组登记一个 KU |
| conflict | 9 | 冲突两侧与来源依据保留在对齐行，等待解决证据 |
| excluded | 102 | 含 48 项 S1 排除及其余 S3 类型/对象边界排除 |
| undecided | 5,191 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |
| **合计** | **12,418** | 每个候选一条当前决定记录 |

**S3 决定去向核对：** 每条候选均有 `resolution_note` 与 `process_ref`；same 指向既有 manifest KU；new 组成员全部待登记或一致映射至同一 KU；conflict、undecided 和 excluded 均保留各自理由。此处表示当前决定与去向可追溯，不表示所有冲突或待证身份已解决。逐项裁决及判断变化见[全书 S3/S4 过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)与[对齐表](../tables/alignment.csv)。

2026-10-19 补录人物身份复用：`cand-1308`（p.375n “A. Hume”）改列 `same` 并映射至 `units/persons/abraham-hume`。National Gallery Archive NGA8/1 支持 Hume 与 Sasso 的通信语境；具体被引信件未核，关系候选仍待 S6。本次只改变 S3 去向，不新增 KU 或正式关系。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-abraham-hume-sasso-crossref-20261019)。

### S3 person：Domenico Fedini 索引与页图签名归并（2026-10-18）

`cand-1014`（F.csv#29，pp.388–389）由 `undecided` 改为 `new`，与 `cand-10766`、`cand-10781` 共用一个 source-local 身份组。附录页图签名读作“Domenico Fedini”及“Dom.o Fedini”，与索引姓名相合；OCR “Pedini”保留为转录异文，不另立人物。原有 `cand-10781` 独立组撤回，旧理由与变更依据均保存在对齐记录。未新增外部身份或生平事实；`cand-10791`仍为排除。

### S4 person：Domenico Fedini 登记

三个候选现映射至[多梅尼科·费迪尼人物卡](../units/persons/domenico-fedini.md)。卡片记录索引、两页图签名及OCR转录差异；6条直接S2关系候选留待S6，未登记正式关系。strict-stage表审计 `errors=[]`、`s2_missing=[]`，现有两条字段来源引用警告与S2语义审查提示未变。

### S3 family：Baglioni 跨章候选保持待证（2026-10-18）

复核 `cand-4279`（佩鲁贾礼拜堂所指家族）与 `cand-7575`（威尼斯出版家族）。Treccani 与 Marco Gozzi 的记录分别支持佩鲁贾封建家族和 Tommaso Baglioni 创立、源自贝加莫的威尼斯印刷出版家族，但未证明两者的谱系关系；两候选继续保持独立 review 组、`undecided`、不登记 KU。仅在取得能说明同支、异支或无谱系联系的家族材料后再裁决。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)。

Cimaroli 索引候选 cand-0758–cand-0764 现统一 same → [Giovanni Battista Cimaroli 人物卡](../units/persons/cimaroli.md)。索引全名、第9章 OCR 异写、第10章多项正文／注表锚点与既有图版及 Zeri 身份依据支持同一画家；cand-0764 的 Stanhope 作品归属问号继续保留，cand-0759 只解决人物身份而无新增正文断言。此前的 6 条 new 建议组与 1 条 undecided 理由保存在对齐行中；S4 无需重复登记该人物。

本轮新增一项身份冲突：`cand-1405` 的 Wenzel 索引标签与第七章 1691 年书信年代不相容；该信的 Prince 较可能是既有人物 Johann Adam Andreas I，但索引跨页组尚待拆分核实。该候选由 `new` 改为 `conflict`，不生成 Wenzel KU；另两条只具头衔的第十三章候选继续独立待证。16条相关关系候选不进入正式关系。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)。

本轮复核 `cand-0146`（Augustus II of Poland / Frederick Augustus I of Saxony）与其索引子项 `cand-0147`：二者保持 new-person:augustus-ii-of-poland-e7b26d3f40 的独立 new 身份组，外部身份由 GND 118505084 与 Sächsische Biografie 支持；已有 Augustus III 人物卡对应其子，原书与权威记录均明确父子及继位边界，故不映射到该卡。现已登记为[Augustus II人物卡](../units/persons/augustus-ii-of-poland.md)；10条直接 S2 陈述中的9条关系候选仍留待 S6。

人物候选 `cand-2493`（Cardinal Bernardino Spada）的跨第3、5章锚点与 Treccani DBI 身份记录相符，保持独立 new 组 `new-person:bernardino-spada-810d88ac92`，现已登记为[贝尔纳迪诺·斯帕达人物卡](../units/persons/bernardino-spada.md)。既有 `units/persons/virgilio-spada` 对应 Virgilio Spada；第3章明说二人为兄弟，但人物 KU 保持分立，关系候选留待 S6。9条关系候选尚未建立正式边。

复核人物候选 cand-1013（Farsetti, Tommaso Giuseppe）：第8章 p.235n 的 T. G. Farsetti、第14章 p.347n 的 T. G. Farsetti 与第15章 pp.362n、364 的全名及1720–91相互对应；Treccani DBI 支持该身份，并列出其1778年家族史。该候选保留 new-person:farsetti-giuseppe-tommaso-339a4db213 的独立 new 决定，现登记为[托马索·朱塞佩·法尔塞蒂人物卡](../units/persons/tommaso-giuseppe-farsetti.md)。现有 Filippo Farsetti 人物 KU 与 Farsetti family KU 分别是不同人物和集体对象；cand-10443 是独立 archive 新组 archive-group-ca70d9ac8f95，不与作者人物合并。9条关系候选仍待 S6；第8章转引不作为独立核验的天花描述。

复核 archive 候选 cand-4577（Claude Lorrain—The Paintings，1961）：第2、4、6、7章引文及第21章书目指向同一两卷本；INHA 与 Folger 目录记录作者 Marcel Röthlisberger，并区分卷I目录与卷II图版。archive-group-4f5f75670a57 已登记到[既有两卷本archive KU](../units/archives/claude-lorrain-paintings-1961.md)；候选中的vol. I作为页码定位保留，不另建卷I卡，也不与 Claude Lorrain 人物或其1968年绘画作品集混合。四条引注候选现已formal，详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s6-cross-chapter-archive-citations-20261020)；书目身份不验证具体引文内容。

复核 event 候选 cand-6051：第5章将 S. Salvatore in Lauro 描述为十二月循环展览，第8章记录同一地点的1704年展览。保留 sg3-event-cand-6051 为“系列”身份；1675、1697 和 1701 年展览候选分别保持独立新事件，其中 cand-11942 未证明属于十二月系列；1708 年相似展览 cand-11783 仍待证。S. Giovanni Decollato 系列和其1675年展览不合并；修道院回廊位置 cand-6053 保持 undecided。5条关系候选仍待 S6。

### S3 person：Dionisio Dolfin 跨页身份与外部对齐（2026-10-16）

- cand-0929（D.csv#31，pp.252–253）由索引主项、p.252人物名和p.253正文全名锚定同一人物。Dizionario Biografico dei Friulani Nuovo Liruti（Cristina Moro，https://www.dizionariobiograficodeifriulani.it/dolfin-dionisio）确认Dionisio Dolfin为1663–1734年的阿奎莱亚宗主教，并区分1698年coadjutor任命与1699年正式接掌；因此与Haskell的1698年说法不冲突。新增外部身份行 aln-12631，不把外证扩展为亲属或艺术关系判断。
- 保留 `new-person:dionisio-dolfin-b1fe9e909e`；现有Dolfin family KU为family类型，不与人物合并。9条以Dionisio为主／客体端点的S2关系候选仍待S6；另3条只在statement限定中提及他，不计作直接关系端点。

### S3 institution：Papal States 跨章身份组裁决（2026-10-16）

- cand-1831、cand-1832、cand-1833 → `sg3-institution-cand-1831`，合为一个 new institution 身份组，待 S4 登记。cand-1832、cand-1833 原标 term，按索引子目和对应 S2 提及改正为 institution；两者是 Papal States 政体的索引定位，不另建概念 KU。
- Treccani《Pontificio, Stato》确认 Stato della Chiesa 是教宗作为世俗主权者统治的政治实体（至1870年）；本条只支持对象身份与类型。Rome 城市和 Holy See 候选 cand-4424 保持分立。没有同类型既有 institution KU。10条直接 S2 陈述中8条关系候选留待 S6；未创建 KU、卡片或正式关系。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)。

### S3 institution：威尼斯绘画与雕塑学院及 Remondini 跨章复核（2026-10-16）

- cand-0006（A.csv#5，p.331，sub-entry `art exhibitions`）判为 same → [威尼斯绘画与雕塑学院](../units/institutions/academy-of-painting-and-sculpture-venice.md)。p.331 的 S2 叙述将学院成员与年度展览、借画补足展品数量相连，并已映射至 cand-0005；它是既有学院索引子目，不是第二所学院或展览事件。
- cand-2122（Q-R.csv#49，p.392）与 cand-2123（Q-R.csv#50，p.340）保留 `sg3-institution-remondini` 同一 new institution 组，已共同映射至[Remondini 印刷商行](../units/institutions/remondini-firm.md)。第13章称其为 Bassano 商行、在 Venice 有分支并从事出版/印刷；第19章称 1766 年 Volpato 致出版者 Remondini 的信。此组表示商行，不推及家族或具名成员。没有新增外部身份行、KU 或正式关系。

### S3 archive：Pasquali《Beatae Mariae Virginis Officium》身份裁决（2026-10-16）

- cand-1849（P.csv#49，p.337）从 `undecided` 改为 new，进入 `archive-group-pasquali-officium-1740`，待 S4 登记。Haskell 直接给出题名与1740年出版信息；OPAC SBN PUVE008510 将同题名著录为单行本，出版地 Venetiis、出版者 Jo. Baptistam Pasquali、年份1740。
- 本组仅表示该书的书目身份。与 cand-1848《Dactylografa Smithiana》、cand-1851 Goldoni 十七卷版、cand-12144 未具名的 Pasquali 一般出版物群区分；未将 Morazzoni 注释引用当成该书本身。3条直接关系候选留待 S6；本轮不验证委托、资助或艺术评价，不创建 KU、卡片或正式关系。

### S3 archive：McSwiny《Tombeaux des Princes》索引候选并组（2026-10-16）

- `cand-1474`（M.csv#11，289n、290、291）由 `undecided` 改为 `new`，与正文候选 `cand-9032` 同属 `archive-group-25725e686a64`，待 S4 映射为一个 KU。索引短题名与正文中完整法文题名、1741 年出版信息及重叠页码相合；正文 mentions 与 statements 提供可回溯锚点。因该组已有 `new` 决定，本索引候选继续标 `new`，不另建第二个出版物组。
- 边界：与已发行征订小册子 `cand-9030`、未实现的五十幅铜版计划卷 `cand-9031`、以及寓意墓葬画系列作品分开。Haskell 报告 1741 年卷有18幅、其中9幅为寓意墓葬；本轮只裁决文献身份，不独立核实全部内容或书内 claims。未添加外部身份行、KU、卡片或关系。

### S3 archive：Maggiotto《Considerazioni elettriche》身份裁决（2026-10-16）

- `cand-1490`（M.csv#27，p.325n）由 `undecided` 改为 `new`，进入 `archive-group-maggiotto-considerazioni-elettriche-1781`，待 S4 登记。Haskell 正文称 Francesco Maggiotto 撰写电学论著；脚注给出题名、威尼斯 Biblioteca Correr 的 `Misc. 105113` 馆藏号，但未标年份或出版者。Treccani DBI（Ettore Merkel，vol.45，1995）将 Francesco Fedeli, detto il Maggiotto 的《Considerazioni elettriche》列为威尼斯1781年出版的小册子，足以支持题名、作者和版本身份。
- 本组仅表示该书的书目身份。与1882年 Tessier 论文 `cand-9779` 分开；Treccani 同时列出的另外两种1781年电学小册子亦为不同题名，不合并。外部记录不证明发明叙述、Correr 当前馆藏或关系；一条直接关系候选留待 S6，不创建 KU、卡片或正式关系。

### S3 archive：Malvasia《Felsina Pittrice》索引候选复用（2026-10-16）

- `cand-1502`（M.csv#39，p.189）由 `undecided` 改为 `same` → `units/archives/felsina-pittrice-1678-work`。索引子项与第7章 p.189 正文同名，正文明确将作品年代记为1678；既有卡已收录同一页的书名与年份证据，并在 `accepted.yml` 接收，故复用现有身份。
- 边界：第21章书目所列两卷本 Bologna 1841 年版是另一版本候选 `cand-11384`，仍 undecided；本次不将其并入 1678 年作品，也不新增 archive 组或外部身份记录。

### S3 archive：Mancini《Considerazioni sulla Pittura》索引候选并组（2026-10-16）

- `cand-1508`（M.csv#45，pp.124、130）由 `undecided` 改为 `new`，与正文/书目候选 `cand-6089` 同入 `archive-group-fb110b11a649`，待 S4 登记一个 archive KU。第5章 p.120 注3引用 Mancini 卷I、p.249；第21章书目将该书具体著录为 Adriana Marucchi 编、Luigi Salerno 注释、罗马1956年两卷本。标题与卷页引文对应，版次缺口解除。
- 边界：p.124 正文中的泛称“Treatise”不是另一个具名文献；本轮不把 Mancini 人物、原作抽象身份或笼统著述清单并入版次身份，也未登记 KU 或关系。

### S3 archive：Manfrin 致 Edwards 的 1793 年书信索引候选并组（2026-10-16）

- `cand-1515`（M.csv#52，p.395）由 `undecided` 改为 `new`，与正文候选 `cand-10849` 同入 `archive-group-4ec5e3284567`，待 S4 登记一个 archive KU。附录7完整刊出 Girolamo Manfrin 致 Pietro Edwards、1793年12月3日书信，说明其关于组建 Manfrin 画廊的主题并定位至 Biblioteca Correr 的 Epistolario Moschini；第17章 p.380 注6交叉指向同一信件。
- 文献边界：单封书信与其所在的 `Epistolario Moschini` 手稿系列候选 `cand-10605` 分开；索引候选、正文候选归同一 letter 组。当前依据为 Haskell 的完整刊布文本和档案定位，未独立查阅原件；本轮不登记 KU 或正式关系。

### S3 archive：Marino《Adone》文学作品身份裁决（2026-10-16）

- `cand-1549`（M.csv#88，p.115）由 `undecided` 改为 `new`，进入 `archive-group-marino-adone-epic`，待 S4 登记。第4章 p.115 直接称 Marino 委托 Poussin 绘制受《Adone》启发的题材，并将《Adone》归于 Marino；索引子项定位至同页。现有 archive KU 中无同名对象。
- 边界：该组表示文学作品本身，不含 Giambattista Marino 人物 KU，也不含据诗篇主题绘制的 Poussin 图画候选；Marino 的未具名诗作群候选 `cand-1551` 保持独立未决。原书未给出本次所引具体版次或馆藏本，本轮不据此声称某一印本。

### S3 archive：Marino 未具名名画题咏诗组索引候选并组（2026-10-16）

- `cand-1551`（M.csv#90，p.38）由 `undecided` 改为 `new`，与正文候选 `cand-4464` 同入 `archive-group-c659964650de`，待 S4 登记一个 archive KU。索引子项与第2章 p.38 对 Marino 所作“一系列描写名家作品的流行诗”的正文措辞对应，指向同一未具名诗作群。
- 本组表示多个未具名文学作品的聚合身份；不拆造诗名或版次。与献给 Marcello Sacchetti 的单首未具名歌诗 `cand-4463`、以及单独具名的《Adone》`cand-1549` 区分。

### S3 archive：S. Andrea al Quirinale N. 865-13 索引候选并入档案组（2026-10-16）

- `cand-1532`（M.csv#69，pp.386–387）与 `cand-5338` 同入 `archive-group-ff938f5595f2`，现均映射至[Jesuit Archives N. 865-13 档案定位卡](../units/archives/jesuit-fondo-di-gesu-865-13-s-andrea-altarpiece-documents.md)。第3章 p.88 注1–3与第19章附录1 p.386共同支持同一书内引用定位号；档案实体层级与单件边界尚未独立核实。
- 该档案身份组与作品候选分开；`cand-11509`仍为待裁决 work 候选。三条直接 S2 关系候选留待 S6；原件未独立查阅，本次未登记正式关系。

### S3 archive：Brienne《Mémoires》卷级引用与 Mazarin 两份清单身份裁决（2026-10-16）

- `cand-1596`（M.csv#135，pp.185–186）由 `undecided` 改为 `new`，与 `cand-7071`（卷 I 引文）及 `cand-7100`（卷 III 引文）同入 `archive-group-brienne-memoires-1916-1919`。第7章 p.185–186 刊出 Brienne 的告别叙述，注5定位卷 III、pp.88–90；第21章书目列 Bonnefon 编三卷本、Paris 1916–19。BnF 记录 FRBNF34019339 确认同一三卷版，因此卷 I、卷 III 是同一出版物的不同引用定位，索引所指段落并非独立出版物。人物候选 `cand-0452` 与此档案身份分开。
- `cand-6807`（第7章两条注释引用）由 `undecided` 改为 `new`，与第21章书目候选 `cand-11231`（原属独立 new 组）合入 `archive-group-daumale-inventaire-1653-1861`，表示 Duc d’Aumale 于1861年刊行的 *Inventaire de tous les meubles du Cardinal Mazarin*；`cand-6814` 与索引候选 `cand-1597` 同组 `archive-group-mazarin-inventory-1653`，表示正文所称1653年清单原件。第7章 p.184 正文将编制时间置于 Mazarin 1653 年复权后，注2定位 d’Aumale 出版物；书目全题为“dressé en 1653 … conservé dans les archives de Condé”。第21章书目候选 `cand-11231` 与第7章注释候选指向相同刊本，并据此合组；BnF FRBNF30039849 确认1861年版及其所据 Condé 原件。
- 区分 p.184 注3另引 de Cosnac item 1240 的1661年清单（`cand-7091`，保留独立身份组 `archive-group-fd76703203a6`）；注3对应后文1653–1661年购入作品的叙述，不将1661误当作正文“An inventory”日期。原清单和 Brienne 引用页均未独立查阅；BnF 对齐只支持书目/文献身份，不验证 Haskell 的全部历史陈述。3条 BnF 外部身份记录见 `alignment.csv`；本轮不创建 KU、卡片或正式关系。

### S3 person：Mazarin 索引主项与子目复用（2026-10-16）

- `cand-1588`（M.csv#127）及索引子目 `cand-1589`–`cand-1593`（M.csv#128–132）均由 `undecided` 改为 `same` → [Jules Mazarin 人物卡](../units/persons/mazarin.md)。主项及其页码 locator 中的“and Poussin”“and Romanelli”“and Sacchetti family”“association with Barberini and Bentivoglio families”仍指向同一索引父项人物；既有卡以图版标题、全名、生卒与头衔识别该人，正文反复使用 Cardinal Mazarin 明称。
- 子目仅保留为主题/页码定位，不由此新增 Poussin、Romanelli、Sacchetti、Barberini 或 Bentivoglio 关系边。六条候选共享 `sg3-ku-units-persons-mazarin` 复用组；不新增外部身份行、KU、卡片或关系。

### S3 event / term：Mazarin 索引事件分组与“taste”去向（2026-10-16）

- `cand-1594`（M.csv#133）判为 `new`，进入 `sg3-event-cand-1594`：Mazarin 1644年招揽 Bernini 定居法国的尝试，S2 statements `st-chp7-p176-i32`、`st-chp7-p177-i01` 与 `st-chp7-p181-i18` 对应索引页码。它不是 p.181 另一项请 Bernini 扩建 Tubeuf 宫殿的计划。
- `cand-1595`（M.csv#134）判为 `new`，进入 `sg3-event-cand-1595`：1648年向 Algardi 提出优厚条件、劝其赴法的单独事件，S2 statements `st-chp7-p182-i20`、`st-chp7-p182-i21`、`st-chp7-p182-i24` 支持。因对象、年代和行动均不同，与 Bernini 事件分组。
- `cand-1598`（M.csv#137）判为 `new`，与正文候选 `cand-6799` 共用 `sg3-event-cand-6799`。`st-chp7-p183-i13` 明确对应1649年 First Fronde 反对 Mazarin、使其艺术赞助暂时受挫的同一事件。
- `cand-1599`（M.csv#138）判为 `new`，进入 `sg3-event-cand-1599`，表示购入 Bentivoglio 宫殿的交易；`st-chp7-p183-i02` 与 `st-chp7-p183-i20` 记载“1644年后不久”及“确切日期不定、早于1647年”。事件与宫殿 place 候选 `cand-6796` 分开，日期不擅自精确化。
- `cand-1600`（M.csv#139）由 `undecided` 改为 `excluded`：`taste` 在该索引语境中是 Mazarin 个人审美偏好的主题定位，不是材料中独立界定的术语实体。相关断言保留在 S2 statements，并关联既有人物候选 `cand-1588`；不建立泛化术语 KU。
- 对齐表与 KU 映射交叉核算发现旧摘要少计4个 archive 身份组：按29个已登记 KU 目标和1,192个待登记 group token 计为1,221组；全部类型合计原为4,837组、待登记4,556组。这是计数更正，不是新增语义裁决。本批将4条 event 候选转为 `new`，新增3个身份组；1条 term 候选排除。未登记 KU、卡片或关系；S4 待登记现为4,559组、4,669条成员映射。逐条 `resolution_note` 保存此前未决理由和当前证据。

### S3 person：Carlo Barberini 重复索引子项复用已登记人物（2026-10-17）

- `cand-0196`（B.csv#43，地产购买，p.31）由 `undecided` 改为 `same` → [Urban VIII 之兄 Carlo Barberini 人物卡](../units/persons/carlo-barberini-brother-of-urban-viii.md)：索引子项对应正文 L7–8；正文以全名将两笔地产交易归于同一买方，并已由 `cand-0194` 的 S2 提及锚定。
- `cand-0197`（B.csv#44，马基雅维利《君主论》提要，p.41）由 `undecided` 改为 `same` → 同一人物卡：索引子项与 S2 statement `st-chp2-secii-l118-125-carlo-prince-synopsis` 相符，该 statement 明确以 `cand-0197` 为主体候选；同段将 Carlo 指明为 Urban VIII 之兄。
- 两条 alignment 均保留原暂缓理由并追加正文／索引核对依据；不将 S2 关系候选转为正式关系。S3 计数更新为 same=1,792（1,029个 KU）、undecided=5,494；new 及 S4 数量不变。

### S3 person：Alessandro Algardi 三个跨章索引子项复用既有人物（2026-10-17）

- `cand-0037`（A.csv#38，Hercules，p.371）、`cand-0038`（A.csv#39，Mazarin invitation to Paris，pp.182–183）与 `cand-0039`（A.csv#40，villa for Prince Camillo Pamfili，p.148）由 `undecided` 改为 `same` → [Alessandro Algardi 人物卡](../units/persons/alessandro-algardi.md)。第15章 p.371 L76 将 Hercules 归于 Algardi；第7章 p.182 L157 以 Algardi 指称被 Mazarin 延揽的雕塑家；第6章 p.148 L30–35 给出其全名并称 Camillo Pamfili 的罗马别墅由他建造。索引子项均位于同一人物全名下，跨章身份锚点与既有 KU 相符。
- 三条 alignment 保留原暂缓理由并追加各自正文与索引证据；不把 Hercules 合并为人物、不将邀请写成迁居，也不改写正式关系。
- S3 计数更新为 same=1,795（1,030个 KU）、undecided=5,491；new 及 S4 数量不变。

### S3 person：Guercino 跨章身份组复用既有人物（2026-10-17）

- `cand-1258`（G.csv#168，Guercino (Francesco Barbieri)）及子项 `cand-1265`（payment，p.14）、`cand-1274`（work for Don Antonio Ruffo，pp.14、209–210）由 `undecided` 改为 `same` → [乔万尼·弗朗切斯科·巴尔比耶里人物卡](../units/persons/guercino.md)。第1章 p.14、第7章及第8章 pp.209–210 的正文／S2 提及与索引主项、子项定位相符。
- 身份名称差异由 Treccani《意大利人传记辞典》第6卷（1964）条目标题 “BARBIERI, Giovanni Francesco detto il Guercino” 核对，支持索引别名与既有 KU 的同一性；该条目只作为身份依据，不导入生平事实。另存一条 Treccani 外部 identity alignment，绑定主候选 `cand-1258`，访问日期 2026-10-17。
- 三条候选的旧暂缓理由均保留并追加本次依据；不将作品、委托或收费叙述转为正式关系。S3 计数更新为 same=1,798（1,030个 KU）、undecided=5,488；alignment 总行数增至 12,633（其中外部身份记录 227 条）。

### S3 person：Owen McSwiny 四条索引子项复用既有人物（2026-10-17）

- `cand-1467`（M.csv#4，and Canaletto，pp.291–292）、`cand-1468`（M.csv#5，and Joseph Smith，p.291）、`cand-1471`（M.csv#8，British worthies series／artists employed，pp.288–291）及 `cand-1472`（M.csv#9，同系列／Venetian artists，p.289n）由 `undecided` 改为 `same` → [Owen McSwiny 人物卡](../units/persons/owen-mcswiny.md)。四条均在同一人物全名主项下；第10章相应页段的正文内容与既有主项 `cand-1466` 的 S2 提及锚点一致。
- 原暂缓理由留存于 alignment 行；本次只复用人物 KU，不将纪念画系列、Canaletto 作品或 Smith 合作关系写成正式关系。`cand-1469`、`cand-1470` 等作品候选保持原决定。
- S3 计数更新为 same=1,802（1,030个 KU）、undecided=5,484；new、S4 与 alignment 行数不变。

### S3 person：Caravaggio 五条索引子项补充复用既有人物（2026-10-17）

- `cand-0546`（C.csv#70，Conversion of St Paul，p.11）、`cand-0548`（C.csv#72，Earthly Love，p.127）、`cand-0550`（C.csv#74，Martyrdom of St Peter，p.11）、`cand-0551`（C.csv#75，portrait of Maffeo Barberini，p.25）与 `cand-0552`（C.csv#76，Sacrifice of Abraham，p.25）均为人物候选，索引子目隶属主项“Caravaggio, Michelangelo da”，由 `undecided` 改为 `same` → [卡拉瓦乔人物卡](../units/persons/caravaggio.md)。子目提供作品与主题的检索定位，不构成独立作品候选。
- 第1章 p.11 将《Conversion of St Paul》与《Martyrdom of St Peter》列为 Caravaggio 接受委托的祭坛画；第5章 p.127 明称 “Michelangelo da Caravaggio’s Earthly Love”；第2章 p.25 给出全名，并称他绘制 Maffeo Barberini 肖像、稍后又受托画《The Sacrifice of Abraham》。逐项正文锚点与旧暂缓理由保存在 alignment 行；本次并入既有 `sg3-ku-units-persons-caravaggio` 组，不新增外部身份记录、KU 或正式关系。
- Caravaggio 现有跨章人物组共11条候选。S3 计数更新为 same=1,807（1,030个 KU）、undecided=5,479；new、S4 数量及 alignment 行数不变。

### S3 person：A. M. Zanetti the Elder 六条索引子项复用既有人物（2026-10-17）

- `cand-2839`（UVWXYZ.csv#176，and Crozat，p.341）、`cand-2840`（#177，and Joseph Smith，p.341）、`cand-2841`（#178，and Marshal Schulenburg，p.341）、`cand-2842`（#179，and Regent de France，p.341）、`cand-2843`（#180，and Sebastiano and Marco Ricci，pp.341–342）与 `cand-2844`（#181，intermediary between Venice and rest of Europe，p.342）均为人物候选，隶属索引主项“Zanetti, A. M., the Elder”，由 `undecided` 改为 `same` → [老安东·玛丽亚·扎内蒂人物卡](../units/persons/a-m-zanetti-the-elder.md)。
- 第13章 p.341 L91 明称 Antonio Maria Zanetti the Elder，并在同一段中逐项叙述其与 Sebastiano／Marco Ricci、Crozat、法国 Regent 的往来；L95 同段记其与 Joseph Smith、Schulenburg 的联系。第13章 p.342 L102 称其为连接威尼斯与欧洲其他地区的中间人。正文锚点逐条写入 alignment 行并保留旧暂缓理由；本组与既有 `cand-2838`、`cand-3707` 共8条候选，索引档案子项 `cand-2845` 不随人物合并，仍映射至其 archive KU。本轮不新增外部身份记录、KU 或正式关系。
- S3 计数更新为 same=1,813（1,030个 KU）、undecided=5,473；new、S4 数量及 alignment 行数不变。

### S4 按类型登记进度

下表只统计 `decision=new` 的身份组与成员映射。一个组只登记一个 KU；未登记组继续待办。

| 类型 | same（候选→KU） | new（候选／组） | S4 新组（已登记／待登记；待登候选） | conflict | excluded | undecided |
|---|---:|---:|---:|---:|---:|---:|
| archive | 94→64 | 1,306／1,238 | 288／950；954 | 0 | 18 | 684 |
| event | 8→8 | 237／232 | 92／140；140 | 0 | 0 | 113 |
| family | 22→16 | 94／88 | 88／0；0 | 0 | 1 | 18 |
| institution | 183→143 | 195／184 | 45／139；139 | 0 | 0 | 119 |
| person | 1,204→451 | 1,185／1,082 | 826／256；257 | 4 | 7 | 1,068 |
| place | 234→153 | 569／558 | 109／449；449 | 0 | 0 | 307 |
| procedure | 10→10 | 32／30 | 30／0；0 | 0 | 0 | 2 |
| term | 43→35 | 937／925 | 98／827；827 | 0 | 2 | 658 |
| work | 250→221 | 513／489 | 178／311；320 | 5 | 31 | 1,599 |
| 未分类 | 0→0 | 0／0 | 0／0；0 | 0 | 43 | 623 |
| **合计** | **2,048→1,101** | **5,068／4,826** | **1,754／3,072；3,086** | **9** | **102** | **5,191** |

2026-10-17 十批 S4 登记见[term批次一](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-terms-20261017)、[term批次二](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017)、[term批次三](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-three-direct-endpoint-terms-20261017)、[work批次](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-works-20261017)、[英国游客身份组](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-english-tourists-italy-term-20261017)、[修会教堂与罗马画家群体](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017-batch2)、[不雅与艳情索引主题](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-indecency-erotic-term-20261017)、[两组事件](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-events-20261017)、[贝加莫圣母玛利亚教堂](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-bergamo-santa-maria-maggiore-place)及[威尼斯 Pietà 教堂](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-pieta-venice-place-20261017)；共新增23个KU与24条候选映射，153条直接关系候选继续待S6。

本轮新增的 archive 身份组包括：`archive-group-9db379e0572e`（`cand-1453`）映射至[《威尼斯绘画与透视大剧场》](../units/archives/il-gran-teatro-pitture-prospettive-venezia-1720.md)，4条关系候选待 S6；`archive-group-4ef32237dfae`（`cand-1103`、`cand-9706`）映射至[*Della Moneta*](../units/archives/della-moneta-treatise-1750.md)，其人物端点已登记为[Abate Galiani](../units/persons/abate-galiani.md)，1条关系候选待 S6；`archive-group-muratori-della-pubblica-felicita-text`（`cand-1718`、`cand-9705`）映射至[*Della pubblica felicità*](../units/archives/della-pubblica-felicita-1749.md)，1条关系候选待 S6，其人物候选 `cand-1717` 仍为 S3 `undecided`；person 身份组 new-person:bentivoglio-enzo-62e0406c74（cand-0290）映射至[恩佐·本蒂沃利奥人物卡](../units/persons/enzo-bentivoglio.md)，11条关系候选留待 S6；person 身份组 new-person:jan-miel-27b41b4426（cand-1662）映射至[扬·米尔人物卡](../units/persons/jan-miel.md)，13条关系候选留待 S6；person 身份组 new-person:benedetto-gennari-2efcec4904（cand-1127）映射至[贝内代托·詹纳里人物卡](../units/persons/benedetto-gennari.md)，12条关系候选留待 S6；person 身份组 new-person:de-dominique-non-denon-dominique-vivant-d852c29287（cand-1752）映射至[多米尼克·德农人物卡](../units/persons/dominique-de-non-vivant-denon.md)，13条关系候选留待 S6；person 身份组 new-person:england-george-iii-of-0d549c6e37（cand-1141）映射至[乔治三世人物卡](../units/persons/george-iii.md)，28条关系候选留待 S6；person 身份组 new-person:benedetto-castiglione-giovanni-c3cfd274af（cand-0602、cand-0603、cand-0604、cand-0605）映射至[乔瓦尼·贝内代托·卡斯蒂廖内人物卡](../units/persons/giovanni-benedetto-castiglione.md)，27条关系候选留待 S6；person 身份组 new-person:de-miguel-molinos-a5f7ffff73（cand-1680）映射至[米格尔·德·莫利诺斯人物卡](../units/persons/miguel-de-molinos.md)，10条关系候选留待 S6；person 身份组 new-person:isaac-newton-800ef74820（cand-1739）映射至[艾萨克·牛顿人物卡](../units/persons/isaac-newton.md)，24条关系候选留待 S6；person 身份组 new-person:paolo-veronese-4afb8ff702（cand-2755）映射至[保罗·委罗内塞人物卡](../units/persons/paolo-veronese.md)，19条关系候选留待 S6；person 身份组 new-person:brienne-de-lomenie-6472b0f466（cand-0452）映射至[洛梅尼·德·布里埃讷人物卡](../units/persons/lomenie-de-brienne.md)，19条关系候选留待 S6；person 身份组 new-person:da-leonardo-vinci-092752ba56（cand-1390）映射至[莱昂纳多·达·芬奇人物卡](../units/persons/leonardo-da-vinci.md)，17条关系候选留待 S6；person 身份组 new-person:gaetano-zompini-1b920c543e（cand-2874、cand-2877）映射至[加埃塔诺·宗皮尼人物卡](../units/persons/gaetano-zompini.md)，10条关系候选留待 S6；person 身份组 new-person:giuseppe-zais-1e534535f3（cand-2830）映射至[朱塞佩·扎伊斯人物卡](../units/persons/giuseppe-zais.md)，16条关系候选留待 S6；person 身份组 new-person:dal-gioseffo-giovan-sole-8d002c1de3（cand-2480）映射至[乔万·乔塞福·达·索莱人物卡](../units/persons/giovan-gioseffo-dal-sole.md)，15条关系候选留待 S6；person 身份组 new-person:gaudenzi-paganino-bab47b4e3f（cand-1116）映射至[帕加尼诺·高登齐人物卡](../units/persons/paganino-gaudenzi.md)，14条关系候选留待 S6；person 身份组 new-person:duquesnoy-francois-3c8db34ada（cand-0952）映射至[弗朗索瓦·迪凯努瓦人物卡](../units/persons/francois-duquesnoy.md)，14条关系候选留待 S6；person 身份组 new-person:antonio-visentini-26bdbd19e8（cand-2783）映射至[安东尼奥·维森蒂尼人物卡](../units/persons/antonio-visentini.md)，14条关系候选留待 S6；person 身份组 new-person:filippo-juvarra-61d1b03394（cand-1339、cand-1340）映射至[菲利波·尤瓦拉人物卡](../units/persons/filippo-juvarra.md)，12条关系候选留待 S6；person 候选 cand-1489（Maggiotto, Francesco）复用[弗朗切斯科·费代利（又称马焦托）人物卡](../units/persons/francesco-maggiotto.md)，10条关系候选留待 S6；person 候选 cand-2551（Tesi, Mauro）复用[毛罗·安东尼奥·泰西人物卡](../units/persons/mauro-antonio-tesi.md)，9条关系候选留待 S6。各组来源、身份边界和映射更正见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)。

### S4 event/place：Mazarin 招揽、Fronde、购置事件与宫殿地点登记（2026-10-16）

- 新增4张 event 卡及1张 place 卡，登记5个 S3 new 身份组：Mazarin 1644年招揽 Bernini、1648年招揽 Algardi、1649年 First Fronde 赞助受挫、购买 Bentivoglio 宫殿，以及该宫殿地点。候选 `cand-1598` 与 `cand-6799` 共映射至 First Fronde 事件卡；其余候选各映射至对应组卡。
- 卡片保存双语名称、语义对应描述、具体章页原文摘录及证据范围；5张卡的结构化字段另登记26条与表格逐行对应的来源支持行。宫殿地点采用描述性工作名；购买事件与建筑 place 分开。未新增外部身份、外部事实补足或正式关系；直接关系候选留待 S6。
- S4 当前累计登记286组、358条候选映射；待登记4,554组、4,663条映射。event 类型为14组已登记、217组/220条成员待登记；place 类型为10组已登记、566组/571条成员待登记。

### S4 event follow-up：跨章 Sasso 1803 年拍卖组（2026-10-16）

- `cand-10715`（第17章 p.382 注4）与 `cand-11549`（第16章 p.374）映射到同一事件组 `sg3-event-cand-10715`，登记为 `units/events/sasso-personal-collection-auction-1803`；候选和组内两个 source_ref 均保留在 alignment。
- 第16章称 Sasso 为自己汇集的收藏在其去世后于1803年拍卖；第17章注4称 Correr 几乎可以肯定在该场拍卖购得 Zocchi 的 Zanetti—Gerini 双人肖像。卡片链接既有 Sasso、Teodoro Correr 与 work KU，不新增正式关系。原书引用的拍卖目录及1960年期刊文章未独立查阅，买入判断继续标为 Haskell 的“几乎可以肯定”。
- 新增1张 event 卡、1条 manifest 映射、2条候选映射；累计S4登记287组/360条映射，待登记4,553组/4,661条映射；event 为15组已登记、216组/218条成员待登记。

### S4 event follow-up：跨章 Rospigliosi 1667 年即位组（2026-10-16）

- `cand-4813`（第2章 p.58）与 `cand-6482`（第6章 p.161）属于同一组 `sg3-event-clement-ix-accession-1667`，登记为 `units/events/giulio-rospigliosi-accession-clement-ix-1667`；两个来源锚点映射到同一事件 KU。
- 两章均将即位年份记为1667，并称在位仅两年；不据此补定终止日期。第6章原OCR将 `Clement IX` 与 `in` 连写为 `Clement IXin`，原始摘录保留该转录，摘要按语义表达。人物入口复用既有 Giulio Rospigliosi KU；与人物的正式参与关系仍待 S6。
- 新增1张 event 卡、1条 manifest 映射、2条候选映射；累计S4登记288组/362条映射，待登记4,552组/4,659条映射；event 为16组已登记、215组/216条成员待登记。

### S4 event follow-up：Innocent X 葬礼费用争议组（2026-10-16）

- `cand-1821` 是 `P.csv#20`（Pamfili, Gianbattista / Innocent X）之“dispute over burial of”子目；该父级索引名虽指人物，子目实际指事件。它与第6章正文候选 `cand-6297` 同属 `sg3-event-cand-6297`，现映射至 `units/events/innocent-x-burial-expense-dispute-1655`。未把索引子目并入 Innocent X 人物 KU。
- p.150 L56 称 Donna Olimpia 与 Prince Camillo Pamfili 在 Innocent X 于1655年1月去世时拒绝支付棺木费用，并争议安葬费用承担者。注5引 Pastor, XIV, p.37，本轮未独立查阅；原文没有交代最终付款者或解决方式。三个人物端点复用既有 KU；正式事件关系仍待 S6。
- 新增1张 event 卡、1条 manifest 映射、2条候选映射；累计S4登记289组/364条映射，待登记4,551组/4,657条映射；event 为17组已登记、214组/214条成员待登记。

### S4 archive follow-up：Bologna《Francesco Solimena》（2026-10-16）

- `cand-7348`（第7、8章注释及第21章书目）与 `cand-7759`（第8章 p.224“Bologna (Plate 209)”）同属 `archive-group-bologna-francesco-solimena-1958`，映射至 `units/archives/ferdinando-bologna-francesco-solimena-1958`。书目p.416列Ferdinando Bologna、题名 *Francesco Solimena*、Napoli 1958；没有出版者信息。
- 第7章p.200注4引该书p.191，第8章p.208注4引p.20；被引页未独立查阅。第8章p.224称该书图版209刊载一件在汉堡Scholz-Forni collection的复制品；此处只保存Haskell的转述，不据此识别复制品、确认原书内容或建立关系。未新增 `relations.csv` 正式边。
- 新增1张 archive 卡、1条 manifest 映射及2条候选映射；累计S4登记290组/366条映射，待登记4,550组/4,655条映射；archive 为30组已登记、1,191组/1,221条成员待登记。

### S4 archive follow-up：Morazzoni《Il libro illustrato veneziano del Settecento》（2026-10-16）

- `cand-10137`、`cand-10140`、`cand-10143`、`cand-10162`、`cand-10175` 同属 `archive-group-morazzoni-book-1943`，映射至 `units/archives/morazzoni-illustrated-book-venice-1943`。第21章p.430书目给出G. Morazzoni、题名、Milano与1943年；第13章相关短引分别提供四个页码定位及两处无页码指引。
- 原书和被引页未独立查阅；出版者未载，作者首字母未扩展。其他未具书名的Morazzoni引注不并入本组。本轮只登记书目身份，不新增 `relations.csv` 正式边。
- 新增1张archive卡、1条manifest映射、5条候选映射；累计S4登记291组/371条映射，待登记4,549组/4,650条映射；archive为31组已登记、1,190组/1,216条成员待登记；KU总数1,310。

### S4 archive follow-up：Zanetti《Della Pittura Veneziana》（1771）（2026-10-16）

- `cand-2855`（UVWXYZ.csv#192，p.345）与 `cand-9837`（第10章注1、第13章正文及第21章书目）同属 `archive-group-zanetti-della-pittura-veneziana-1771`，映射至 `units/archives/zanetti-della-pittura-veneziana-1771`。书目列Della Pittura Veneziana、Venezia 1771；第13章称其为A. M. Zanetti the Younger自己的著作。
- 第10章注1引该书序言p.xiii，未独立查阅。作者首字母不扩展；与既有人物卡A. M. Zanetti the Elder分开。出版者未载，未新增 `relations.csv` 正式边。
- 新增1张archive卡、1条manifest映射、2条候选映射；累计S4登记292组/373条映射，待登记4,548组/4,648条映射；archive为32组已登记、1,189组/1,214条成员待登记；KU总数1,311。

### S4 archive follow-up：Bibliotheca Smithiana（1755）（2026-10-16）

- `cand-2450`（S.csv#139，pp.310、394）与 `cand-9274`（第10章p.310正文及第19章附录5 p.394）同属 `archive-group-bibliotheca-smithiana-1755`，映射至 `units/archives/bibliotheca-smithiana-1755`。Haskell称该目录1755年出版；第19章记由Pasquali出版。
- 第10章称它“几乎可以肯定”是精心设计的售书目录，这是Haskell推断；第19章称目录所列藏书于1762年售给George III。1771年 *Catalogo di Libri Raccolti...* 与1773年 *Bibliotheca Smithiana, pars altera* 保持独立。未独立查阅目录原件或版本，未新增 `relations.csv` 正式边。
- 新增1张archive卡、1条manifest映射、2条候选映射；累计S4登记293组/375条映射，待登记4,547组/4,646条映射；archive为33组已登记、1,188组/1,212条成员待登记；KU总数1,312。

### S4 archive follow-up：Sasso《Osservazioni sopra i lavori di niello》（1856）（2026-10-16）

- `cand-2366`（S.csv#54，p.373n）与 `cand-10601`（第16章p.373注1及第21章书目）同属 `archive-group-sasso-osservazioni-niello-1856`，映射至 `units/archives/sasso-osservazioni-niello-1856`。书目列G. M. Sasso、E. Cicogna、Venezia 1856；第16章OCR将标题读为“A niello”，第21章书目作“di niello”，卡片保留差异并按书目题名登记。
- 未将作者缩写映射至既有人物卡，也未独立查阅原书。正式作者—作品关系留待S6；本轮未新增 `relations.csv`。
- 新增1张archive卡、1条manifest映射、2条候选映射；累计S4登记294组/377条映射，待登记4,546组/4,644条映射；archive为34组已登记、1,187组/1,210条成员待登记；KU总数1,313。

### S4 archive follow-up：Shaftesbury《Second Characters》1914年编订版（2026-10-16）

- `cand-2431`（S.csv#119，p.142n）与 `cand-11434`（第21章p.437书目）同属 `archive-group-shaftesbury-second-characters-1914`，映射至 `units/archives/shaftesbury-second-characters-rand-1914`。第5章注6引该书p.15；书目给出完整副题、Benjamin Rand编、Cambridge 1914。
- 本卡表示1914年编订版，与work候选 `cand-6220` 保持类型及粒度区分；未独立查阅版本或被引页。S2据页图排除了OCR末尾多出的撇号，未新增 `relations.csv` 正式边。
- 新增1张archive卡、1条manifest映射、2条候选映射；累计S4登记295组/379条映射，待登记4,545组/4,642条映射；archive为35组已登记、1,186组/1,208条成员待登记；KU总数1,314。

### S4 archive follow-up：Vianello 1793年刊行的Carriera日记版本（题名未载）（2026-10-16）

- `cand-2766`（UVWXYZ.csv#102，p.376）与正文候选 `cand-10631`（第16章p.376）同属 `archive-group-vianello-carriera-journal-1793`，映射至 `units/archives/carriera-journal-vianello-1793`。Haskell称Dr Giovanni Vianello于1793年刊行Rosalba的journal，但未给出版物题名、出版地、载体或版本信息。
- 卡片使用明确标注“题名未载”的工作名，不把它升级为原作题名，也不新建或合并手稿对象；未独立查阅原刊。本轮未新增 `relations.csv` 正式边。
- 新增1张archive卡、1条manifest映射、2条候选映射；累计S4登记296组/381条映射，待登记4,544组/4,640条映射；archive为36组已登记、1,185组/1,206条成员待登记；KU总数1,315。

### S3 分组校正与 S4 archive 登记：Gallacini《Trattato》1767年刊本（2026-10-16）

- `cand-1110` 的索引子目（G.csv#17，索引转录L1407–1408）完整列出 *Trattato sopragli errori degli architetti* 并指向p.309；`cand-9257` 的第10章正文候选记录同页所述1767年刊本。原先两个 `new` 组据同题名和同页指向合并为 `archive-group-gallacini-trattato-1767`，二者映射到 `units/archives/trattato-sopra-gli-errori-degli-architetti-1767`。S2依据页图把正文标题读作“sopra gli”；索引OCR连写保留为来源差异。
- 对象范围限于1767年刊本；书内所称手稿只作为刊本来源，不另建未获馆藏号或存世定位的手稿对象。`cand-9258` 所述Visentini更新版保持独立组，精确版本信息仍未载。原刊未独立查阅；作者、刊行与更新关系留待S6，本次未新增正式关系。
- 新增1张archive卡、1条manifest映射、2条候选KU映射和1条accepted路径。S3 new候选数不变，身份组由4,840减至4,839；S4累计登记297组/383条映射，待登记4,542组/4,638条映射；archive为37组已登记、1,183组/1,204条成员待登记；KU总数1,316。

### S4 archive：McSwiny《To the Ladies and Gentlemen of Taste》征订小册子（2026-10-16）

- `cand-1473`（M.csv#10，索引指向p.288n）与 `cand-9030`（第10章p.290正文、p.288注1）同属 `archive-group-mcswiny-ladies-gentlemen-pamphlet`，映射至 `units/archives/mcswiny-ladies-gentlemen-taste-pamphlet`。正文称McSwiny在1730年代某时发行小册子并征订计划卷册；注1称小册子无日期，并报告Haskell写作时大英博物馆藏本。当前馆藏未核验。
- 计划中的50幅版画卷册（`cand-9031`）与1741年实际出版的 *Tombeaux des Princes*（`cand-9032`）均与小册子分开；Haskell记1741年卷有18幅版画。本卡不把征订计划规格当作已发行实体。相关出版者与馆藏正式关系留待S6。
- 新增1张archive卡、1条manifest映射、2条候选映射和1条accepted路径。S4累计登记298组/385条映射，待登记4,541组/4,636条映射；archive为38组已登记、1,182组/1,202条成员待登记；KU总数1,317。

### S4 archive：McSwiny《Tombeaux des Princes》1741年出版卷册（2026-10-16）

- `cand-1474`（M.csv#11，索引短题名及289n、290–291页码）与正文候选 `cand-9032` 同属 `archive-group-25725e686a64`，映射至 `units/archives/tombeaux-des-princes-mcswiny-1741`。第10章p.291提供完整法文题名及1741年出版信息；S2按页图确认末词“siècle”，索引和正文OCR的题名形式及页码互相对应。
- Haskell报告卷册有18幅版画，其中9幅寓意墓葬图被刻印；p.289注2同时报告九幅作品的归属主张，并提醒相关购藏经过混乱。以上均保留为书内报告，原刊及归属未独立核验。小册子 `cand-9030` 和未完成50幅规格的计划 `cand-9031` 保持分开；本卡不升级为画作制作或所有权正式边。
- 新增1张archive卡、1条manifest映射、2条候选映射和1条accepted路径。S4累计登记299组/387条映射，待登记4,540组/4,634条映射；archive为39组已登记、1,181组/1,200条成员待登记；KU总数1,318。

### S4 archive：Francesco Maggiotto《Considerazioni elettriche》1781年小册子（2026-10-16）

- S3组 `archive-group-maggiotto-considerazioni-elettriche-1781` 仅含索引候选 `cand-1490`（M.csv#27，325n）。第10章p.325称Francesco Maggiotto写有关于电学机器的论著，注1列出同题名、Correr定位Misc. 105113，并称所引本没有日期或出版者信息；书末索引在Maggiotto名下列同题名及325n。
- Treccani DBI（Ettore Merkel, vol.45, 1995）将 *Considerazioni elettriche* 列为Maggiotto名下、威尼斯1781年刊行的印刷小册子。该记录用于书目身份、作者、出版地和年份；不据此确认Haskell所引具体副本或当前馆藏，也不核实机器陈述。中文题名《电学考论》为项目暂译；出版者和版次未载。1882年Tessier文章 `cand-9779` 与本书分开，其他1781年电学小册子亦保持独立。
- 新增 `units/archives/considerazioni-elettriche-1781`、1条manifest映射、1条候选映射和1条accepted路径；作者入口链接到既有人物卡，不登记正式著作关系，关系留待S6。字段行经 `build_field_facts.py` 预检与apply登记。S4累计300组/388条映射，待登记4,539组/4,633条映射；archive为40组已登记、1,180组/1,199条成员待登记；KU总数1,319。

### S4 archive：*Beatae Mariae Virginis Officium* 1740年刊本（2026-10-16）

- S3组 archive-group-pasquali-officium-1740 仅含索引候选 cand-1849（P.csv#49，p.337）。Haskell第13章p.337以 Beatae Mariae Virginis Officium 指称一部1740年出版的宗教插图书；索引子目同题名并列p.337。
- OPAC SBN记录PUVE008510将同题名著录为印刷单行本，出版项为Venetiis: Apud Jo. Baptistam Pasquali, 1740；据此登记1740年刊本，中文题名《圣母玛利亚日课》为描述性暂译。SBN身份信息不核验Haskell关于插图、Caime资助、委托或艺术评价的叙述。出版者Giambattista Pasquali复用既有人物卡入口，但本轮不新增正式关系。
- cand-1848 Dactylografa Smithiana、cand-1851 Goldoni edition及cand-12144所指Pasquali一般出版物集合均保持独立。新增1张archive卡、manifest 1条、候选映射1条及accepted路径；S4累计301组/389条映射，待登记4,538组/4,632条映射；archive为41组已登记、1,179组/1,198条成员待登记；KU总数1,320。字段行经 build_field_facts.py 预检与apply登记。

### S3 archive：Brienne《Mémoires》书目候选并入三卷本身份组（2026-10-16）

- `cand-11265`的第21章书目条目明确列Brienne《Mémoires》Paul Bonnefon编、3 vols.、Paris 1916-19；现并入已由BnF FRBNF34019339支持的卷I／卷III引文身份组。
- new=5,022（4,839个身份组），undecided=5,500；S4待登记4,538组、4,633条成员候选。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)。

### S4 archive：Brienne《Mémoires》1916–1919年三卷本（2026-10-16）

- S3组 `archive-group-brienne-memoires-1916-1919` 包含 `cand-11265`（第21章完整书目条目）、`cand-1596`（M.csv#135，索引告别藏品条目，pp.185–186）、`cand-7071`（第7章卷I引注定位）及 `cand-7100`（第7章卷III引注定位），统一映射至 `units/archives/brienne-memoires-1916-1919`。
- 第21章书目列Louis-Henri de Loménie Comte de Brienne、Paul Bonnefon编、3卷、Paris 1916–19；BnF FRBNF34019339支持同一三卷本身份。Haskell脚注列卷I p.315及卷III pp.88–90，后者OCR作“IH”，按S3身份裁决解释为III；回忆录原卷页未独立查阅。已有Brienne人物KU作为独立身份入口保留，不创建作者或编者正式关系；相关关系留待S6。
- 书目编者Paul Bonnefon已通过 bl-0003 完成S1候选、S3身份裁决及S4 KU登记；人物身份由BnF规范记录支持，正式编辑关系仍留待S6。
- 新增1张archive卡、manifest 1条、4条候选映射、accepted路径和1条person端点待办；S4累计302组/393条映射，待登记4,537组/4,629条映射；archive为42组已登记、1,178组/1,195条成员待登记；KU总数1,321。字段行经 `build_field_facts.py` 预检与apply登记。

### S3 person：d’Aumale, duc 对齐至 Henri d’Orléans（2026-10-16）

- `cand-7090`由BnF人物权威记录FRBNF12375307识别为Henri d’Orléans, duc d’Aumale（1822–1897），现裁为单独new-person组。
- new=5,023（4,840组），undecided=5,499；S4待登记4,538组、4,630条成员候选。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)。

### S4 person：Henri d’Orléans, duc d’Aumale（1822–1897）（2026-10-16）

- `cand-7090`按BnF人物权威记录FRBNF12375307登记至 `units/persons/henri-dorleans-duc-aumale`。该权威记录将书目形式 `d’Aumale, duc` 识别为Henri d’Orléans, duc d’Aumale，并给出1822–1897；未扩写其他传记事实。
- 本次新增1张person卡、manifest 1条、候选映射1条及accepted路径。其与1861年马萨林清单刊本的正式责任关系留待S6，不新增relations.csv边。S4累计303组/394条映射，待登记4,537组/4,629条映射；person为89组已登记、995组/1,040条成员待登记；KU总数1,322。字段行经 `build_field_facts.py` 预检与apply登记。

### S4 archive：d’Aumale《Inventaire de tous les meubles du Cardinal Mazarin》1861年刊本（2026-10-16）

- S3组 `archive-group-daumale-inventaire-1653-1861` 的 `cand-6807`（第7章注释出版物候选）与 `cand-11231`（第21章完整书目候选）共同映射至 `units/archives/daumale-inventaire-mazarin-1861`。Haskell书目OCR将 *meubles* 转录为 *tneubles*；BnF FRBNF30039849确认规范题名及Londres: Whittingham et Wilkins, 1861。
- 本KU是1861年刊本，不与其据称依据的1653年清单原件（独立S3组 `archive-group-mazarin-inventory-1653`）合并。作者形式d’Aumale, duc已映射至独立Henri d’Orléans人物KU；正式作者关系留待S6。
- 新增1张archive卡、manifest 1条、2条候选映射及accepted路径；S4累计304组/396条映射，待登记4,536组/4,627条映射；archive为43组已登记、1,177组/1,193条成员待登记；KU总数1,323。字段行经 `build_field_facts.py` 预检与apply登记。

### S4 archive：马萨林1653年清单原件（2026-10-16）

- S3组 `archive-group-mazarin-inventory-1653` 的 `cand-6814`（第7章p.184正文候选）与 `cand-1597`（M.csv#136，p.184索引子目）共同映射至 `units/archives/mazarin-inventory-manuscript-1653`。第21章书目和BnF FRBNF30039849将其与据Condé原件刊行的1861年印本联系起来；原件未直接查阅。
- 1861年刊本保持独立KU `units/archives/daumale-inventaire-mazarin-1861`；第7章注3所引1661年清单候选 `cand-7091` 仍为另一对象。注2所引刊本pp.293 ff.未独立核读，正式版本关系留待S6。
- 新增1张archive卡、manifest 1条、2条候选映射及accepted路径；字段表登记6条source-backed记录，unverified数不变。S4累计305组/398条映射，待登记4,535组/4,625条映射；archive为44组已登记、1,176组/1,191条成员待登记；KU总数1,324。

### S3 person：Podestà 跨章身份归组（2026-10-16）

- `cand-5558`（第4章p.97、p.105正文人物锚点）与 `cand-1964`（P.csv#165，索引页码97、105、184n）同属 `new-person:andrea-podesta-070b483a9a`。第7章p.184注3给出全名 Giovanni Andrea Podesta；Getty ULAN 500021868 将 `Podestà, Andrea` 列为别名，卢浮宫艺术家权威记录列出 `Podesta Andrea` 同义名。`cand-1964` 原 `undecided` 的缺少正文身份锚点问题据此解决，候选保留自身索引定位并加入现有new组。
- 本裁决只确认人物身份，不确认Haskell转述的1661年清单编制者身份；de Cosnac item 1240未独立查阅。S3新增1条new候选、未增加new身份组、undecided减少1；S4现将两条候选共同映射至一个KU。相关关系不在本轮写入 `relations.csv`。

### S4 person：Giovanni Andrea Podesta 跨章身份组登记（2026-10-16）

- `cand-5558`（第4章正文人物候选）与 `cand-1964`（P.csv#165，页码97、105、184n）共用S3身份组 `new-person:andrea-podesta-070b483a9a`，现共同映射至 `units/persons/giovanni-andrea-podesta`。卡片以第7章全名为规范名；Getty ULAN与卢浮宫权威记录支持书内别名。两条权威记录的日期范围不一致，故本卡不录生卒年。
- 第4章关于交往与版画题献、第7章关于1661年清单编制者及Mazarin联系的关系候选继续待S6；清单与Blunt文章未独立查阅。本次不写入正式关系，也不将版画题献解释为版画创作。涉及候选的S2陈述共5条，其中4条为关系候选，仍由原statement记录承载。
- 新增1张person卡、1条manifest、2条候选KU映射及accepted路径；S4累计306组/400条成员映射，待登记4,534组/4,624条；person为90组已登记、994组/1,039条成员待登记；KU总数1,325。`build_field_facts.py`预检无警告，登记7条source-backed字段事实及2条Getty／卢浮宫来源记录，未核验字段数保持1,578。

### S4 person：Gabriel-Jules de Cosnac 人物组登记（2026-10-16）

- `cand-7086`映射至 `units/persons/gabriel-jules-de-cosnac`。Haskell第21章书目列其为 *Les richesses du Palais Mazarin*（Paris, 1885）的责任者；BnF人物权威记录FRBNF12982918确认Gabriel-Jules de Cosnac（1819–1893）、伯爵、历史学家，并提供生卒年月日及地点。与该出版物的正式作者边留待S6。
- 新增1张person卡、1条manifest、1条候选KU映射、BnF身份行 `aln-12626` 和accepted路径；S4累计307组/401条成员映射，待登记4,533组/4,623条；person为91组已登记、993组/1,038条成员待登记；KU总数1,326。`build_field_facts.py`预检无警告并apply登记9条source-backed字段事实及1条BnF来源，未核验字段数保持1,578。

### S4 archive：Cosnac《Les richesses du Palais Mazarin》1885年第二版（2026-10-16）

- `cand-7087`登记至 `units/archives/les-richesses-du-palais-mazarin-1885`。Haskell书目列Paris 1885；Persée确认第二版、Renouard及Paris，Smithsonian确认书籍记录、责任者和1885年。两个外部记录支持刊本书目身份；原书及Haskell所引页未独立查阅，正式作者边留待S6。
- 新增archive卡、manifest、1条候选映射及2条外部书目身份行 `aln-12627`（Smithsonian）和 `aln-12628`（Persée）；与1885刊本中所称的1661年清单分别登记。字段表新增12条source-backed事实。

### S4 archive：1661年马萨林身后清单（de Cosnac item 1240）（2026-10-16）

- `cand-7091`登记至 `units/archives/mazarin-inventory-1661-de-cosnac-item-1240`，表示Haskell注3指向的1661年清单身份。Persée与Smithsonian记录说明1885年刊本副题含1661年Mazarin身后清单；它们识别的是刊本，不是独立item 1240。原件、de Cosnac条目以及item的文本形态均未核实，故不称手稿或抄本。
- 新增archive卡、manifest及1条候选KU映射；与1653年清单、1861年刊本和1885年书籍保持分立。Podesta编制者身份及清单—刊本关系均留待S6，不新增正式关系。
- S4累计309组/403条成员映射，待登记4,531组/4,621条；archive为46组已登记、1,174组/1,189条成员待登记；KU总数1,328。两个新archive卡共新增16条source-backed字段事实及2条目录来源；本批字段事实apply无警告，未核验字段数保持1,578。

### S3 person：Paul Bonnefon 直接关系端点身份裁决（2026-10-16）

- backlog bl-0003 源于第21章书目候选 st-chp21-bib-l243-293-entry-07，source_ref为 chp-21:21_CHP-21Bibliography:l243-293#L254。书目原文将 Paul Bonnefon 列入 Brienne《Mémoires》三卷本的 publiés par 责任表述；既有 archive KU 与BnF书目记录FRBNF34019339对应同一出版物。
- 新增S1人物候选 cand-12427。BnF人物权威 FRBNF12115372（https://catalogue.bnf.fr/ark:/12148/cb12115372q）识别为Bonnefon, Paul（1861–1922），并记录其作者身份和Arsenal图书馆、法国文学协会职务；当前manifest无同一人物KU，故裁为 new-person:paul-bonnefon-1861-1922 / new。该裁决只确认人物端点，不将编辑责任自动写成S6正式边。
- 增加候选决定行 aln-12629 与BnF人物身份行 aln-12630；原backlog理由保留在完成说明中。

### S4 person：Paul Bonnefon 人物组登记（2026-10-16）

- cand-12427 映射至 units/persons/paul-bonnefon；新增person卡、manifest、accepted路径及候选KU映射。卡片记录双语名称与描述、BnF规范姓名、生卒年月日、作者身份及有据职务；中文名为项目工作音译。
- backlog bl-0003 更新为 completed，只表示身份端点已登记。与Brienne《Mémoires》的正式编辑关系仍待S6逐条审查；未新增relations.csv边。
- S4累计310组/404条成员映射，待登记4,531组/4,621条；person为92组已登记、993组/1,038条成员待登记；KU总数1,329。字段事实经 build_field_facts.py 预检无警告并apply，新增7条source-backed字段事实及1条BnF来源，未核验字段数保持1,578。

### S4 person：Bernardino Spada 人物组登记（2026-10-16）

- cand-2493 → new-person:bernardino-spada-810d88ac92 → units/persons/bernardino-spada。新增双语人物卡、manifest及accepted路径；Treccani DBI（Benedetta Borello，vol. 93，2018）支持规范名、生卒、枢机任命、驻巴黎教廷使节及博洛尼亚使节任期。Haskell第3、5章提供书内称名和跨章锚点。
- 9条 S2 关系候选继续待S6；Haskell关于兄弟、宫殿取得、职务与条件性委托的断言保留原限定，本次不写入 `relations.csv`，不将“如果作品确曾绘制”改成确定委托。
- S4累计311组/405条映射，待登记4,529组/4,614条；person已登记93组，待登记991组/1,031条成员；KU总数1330。字段事实由 `build_field_facts.py` 预检并登记。

### S4 person：Tommaso Giuseppe Farsetti 人物组登记（2026-10-16）

- cand-1013 → new-person:farsetti-giuseppe-tommaso-339a4db213 → units/persons/tommaso-giuseppe-farsetti。新增双语人物卡、manifest及accepted路径；Treccani DBI（Paolo Preto，vol. 45，1995）支持规范名、出生／去世日期与地点，以及文人、藏书家身份。Haskell索引及第8、14、15章提供跨章名称锚点；第8章的Fogolari嵌套转引没有作为独立验证事实。
- 9条 S2 关系候选继续待S6；亲属、作品、著述、委托及收藏主张不在本次写入正式关系表。1778年家族史保持独立archive候选 cand-10443，不合并进人物KU。
- S4累计312组/406条映射，待登记4,528组/4,613条；person已登记94组，待登记990组/1,030条成员；KU总数1331。字段事实由 `build_field_facts.py` 预检并登记。

### S4 person：Dionisio Dolfin 人物组登记（2026-10-16）

- cand-0929 → new-person:dionisio-dolfin-b1fe9e909e → units/persons/dionisio-dolfin。新增双语person卡、manifest、accepted路径及候选／外部身份映射；卡片只录姓名、书内锚点、DBF支持的生卒和任职信息。
- 9条以Dionisio为主／客体端点的S2关系候选继续待S6，未写入 `relations.csv`；另3条statement只在语境限定中提及他。书内关于Daniele亲属、宫殿/作品、Tiepolo委托的说法保留原statement及限定；不因端点登记认定为正式关系。
- S4累计313组/407条映射，待登记4,527组/4,612条；person已登记95组，待登记989组/1,029条成员；KU总数1332。`build_field_facts.py` dry-run无警告并apply登记11条source-backed字段记录、新增2条来源；unverified数量保持1,578。

### S4 person：Augustus II of Poland 双候选组登记（2026-10-16）

- `cand-0146` 与 `cand-0147` → `new-person:augustus-ii-of-poland-e7b26d3f40` → `units/persons/augustus-ii-of-poland`。新增双语人物卡、manifest、accepted路径；两条候选决定行及 GND/Sächsische Biografie 外部身份行共同映射到该KU。
- Deutsche Biographie GND 118505084与Winfried Müller的Sächsische Biografie条目支持Friedrich August I = Augustus II、选帝侯/波兰国王身份及1670–1733年生卒。Haskell第10章p.294明示同一对应，p.278的“Augustus the Strong”是相同别称。既有 Augustus III 卡保持独立。
- 10条直接S2陈述中9条为关系候选，仍待S6逐项审查；无正式关系写入。S4累计314组/409条映射，待登记4,526组/4,610条；person已登记96组、待登记988组/1,027条成员；KU总数1333。`build_field_facts.py` 预检无警告并apply登记11条source-backed字段记录、新增2条来源；unverified数量保持1,578。

### S4 person：Pierre-Jean Mariette 跨章候选登记（2026-10-16）

- `cand-1547`（M.csv#85）→ `new-person:jean-mariette-pierre-69263c8b1d` → `units/persons/pierre-jean-mariette`。新增双语人物卡、manifest、accepted路径；候选决定行映射至该KU。书内索引全名和第13章‘French connoisseur’称谓支持有限身份字段；未增加外部生平或身份标识。
- 该候选在第6、10、13–15章有直接 S2 端点；10条直接陈述中7条为关系候选，均留待S6，另3条为非关系陈述。Haskell所引传闻、信件书目及关系语句按原限定保留；未读原始引文，也未写入正式关系。S4累计315组/410条映射，待登记4,525组/4,609条；person已登记97组、待登记987组/1,026条成员；KU总数1334。`build_field_facts.py` 预检无警告并apply新增4条source-backed字段记录、来源数不变；unverified数量保持1,578。

### S4 person：Pietro Ercole Gherardi 跨章候选登记（2026-10-16）

- `cand-1155`（G.csv#62）→ `new-person:ercole-gherardi-pietro-8af999ae11` → `units/persons/pietro-ercole-gherardi`。新增双语人物卡、manifest、accepted路径；候选决定行映射至该KU。第10章p.302注4给出全名，索引与第9、13章缩写称名相互对应；未增加外部身份或生平事实。
- 该候选跨第9、10、13章有10条直接S2陈述，其中7条为关系候选，均留待S6；另3条为非关系陈述。Haskell所引书信未作为已读原件；`cand-9192` 描述的文献对象仍待裁决，本轮未登记archive/work KU或正式关系。S4累计316组/411条映射，待登记4,524组/4,608条；person已登记98组、待登记986组/1,025条成员；KU总数1335。`build_field_facts.py` 预检无警告并apply新增4条source-backed字段记录、来源数不变；unverified数量保持1,578。

### S4 person：François Boucher 三候选跨章组登记（2026-10-16）

- `cand-0421`、`cand-0422`、`cand-0423`（B.csv#268–270）→ `new-person:boucher-francois-2b86c8ca6d` → `units/persons/francois-boucher`。三条索引同名主项／子项候选共同映射到一张双语人物卡，新增manifest与accepted路径；未发现同名person KU。
- 书内索引全名及第9、10、13、14章上下文支持跨章身份组。7条直接S2陈述均为关系候选，全部留待S6；本轮没有新增正式关系或外部身份记录。S4累计317组/414条映射，待登记4,523组/4,605条；person已登记99组、待登记985组/1,022条成员；KU总数1336。`build_field_facts.py` 预检无警告并apply新增5条source-backed字段记录、来源数不变；unverified数量保持1,578。

### S4 person：Donato Creti 跨章候选登记（2026-10-16）

- `cand-0889`（C.csv#423）→ `new-person:creti-donato-4d75402fa5` → `units/persons/donato-creti`。新增双语人物卡、manifest、accepted路径；索引全名及第7、8、14章正文称名支持独立人物KU。第10章p.288 OCR作Cred，按S2对照纸本校读为Creti，来源原文未改。
- 9条直接S2陈述中7条为关系候选，均留待S6；另2条为非关系陈述。称号对象 `cand-7745` 仍为undecided，未作人物属性或新增term KU。S4累计318组/415条映射，待登记4,522组/4,604条；person已登记100组、待登记984组/1,021条成员；KU总数1337。

### S4 person：Pietro Tacca 跨章双候选组登记（2026-10-16）

- `cand-2537`（T.csv#0，pp.97、174、178）与 `cand-2538`（T.csv#1，pp.387、389）保持S3组 `new-person:pietro-tacca-374a1e8a84`，共同映射至 `units/persons/pietro-tacca`。既有manifest无同名person；两候选全名、章节正文称名及附录署名相合。新卡不补外部身份或书外生平。
- 第4、7、19章的模型、纪念碑、雕塑活动和书信内容保留原S2 statements；附录信仅按Haskell刊本记录，档案原件未独立查阅。7条直接关系候选均留待S6，本轮未新增正式关系。
- `build_field_facts.py` 预检无警告并apply新增3条source-backed字段记录、来源数不变；unverified数量保持1,578。S4累计319组/417条映射，待登记4,521组/4,602条；person已登记101组，待登记983组/1,019条成员；KU总数1338。

### S4 person：John Breval 跨三章身份组登记（2026-10-16）

- `cand-0451`（B.csv#298，pp.222、266、301、306、307）保持S3组 `new-person:breval-john-03249744d6`，现映射至 `units/persons/john-breval`。既有manifest无同名人物KU；索引全名及第8、9、10章同名锚点相合。新卡仅记录姓名和书内鉴赏家身份，不补外部生平。
- 9条直接S2陈述中6条为关系候选、3条为非关系陈述；6条留待S6逐项审查。第9章引述的Breval 1738年版未独立查阅；第10章小雕像在p.306与p.307的称谓差异保留，未裁定对象身份。
- `build_field_facts.py` 预检无警告并apply新增3条source-backed字段记录、来源数不变；unverified数量保持1,578。S4累计320组/418条映射，待登记4,520组/4,601条；person已登记102组，待登记982组/1,018条成员；KU总数1339。

### S4 person：Francesco Angeloni 跨章人物组登记（2026-10-16）

- `cand-0107`（A.csv#108，pp.53n、114、158）保持S3组 `new-person:angeloni-francesco-24d9ba915a`，现映射至 `units/persons/francesco-angeloni`；既有manifest无同名人物KU。卡片登记姓名及书内明确称为考古学者、古物学者、收藏家和作家的身份，不补外部生平。
- 9条直接S2陈述中8条为关系候选、1条为非关系评价；8条关系候选留待S6。Bellori为其侄子的表述保留‘was said to be’限定，Cassiano、Poussin、Carracci图像相关主张仍以Haskell文本为依据；所引文献未独立查阅。
- `build_field_facts.py` 预检无警告并apply新增6条source-backed字段记录、来源数不变；unverified数量保持1,578。S4累计321组/419条映射，待登记4,519组/4,600条；person已登记103组，待登记981组/1,017条成员；KU总数1340。

### S4 person：Giambattista Biffi 跨章人物组登记（2026-10-16）

- `cand-0373`（B.csv#220，pp.262n、328、360）保持S3组 `new-person:biffi-giambattista-0fc083bcf0`，现映射至 `units/persons/giambattista-biffi`。第9章Gio. Battista与第10、14章Giambattista拼写共同支持索引全名；无同名既有person KU，不补外部生平。
- 第9章OCR页标202已由S2对照页图校为p.262，第10章OCR页标28据S2记录校为p.328。9条直接S2陈述中7条为关系候选、2条为非关系记录；7条均留待S6。书信、日记和Venturi转引未独立查阅。
- `build_field_facts.py` 预检无警告并apply新增3条source-backed字段记录、来源数不变；unverified数量保持1,578。S4累计322组/420条映射，待登记4,518组/4,599条；person已登记104组，待登记980组/1,016条成员；KU总数1341。

### S4 person：Carlo Cordellina 跨章人物组登记（2026-10-16）

- `cand-0842`（C.csv#372，pp.256、405）保持S3组 `new-person:carlo-cordellina-80fe525d81`，现映射至 `units/persons/carlo-cordellina`。索引全名与第9章、第20章后记同名锚点对应；既有manifest无同名人物KU。新卡只登记书内法律倡辩者身份，不补外部生平。
- 8条直接S2陈述中7条为关系候选，1条为非关系性格描述。Vicenza住宅与后记所称宫殿的同一性候选`cand-8375`保持未决；Tiepolo委托、作品及其他端点关系留待S6。本轮不修改`relations.csv`。
- `build_field_facts.py` 预检无警告并apply新增3条source-backed字段记录、来源数不变；unverified数量保持1,578。S4累计323组/421条映射，待登记4,517组/4,598条；person已登记105组，待登记979组/1,015条成员；KU总数1342。

### S4 person：Cristoforo Roncalli 跨三章身份组登记（2026-10-16）

- `cand-2218`（Q-R.csv#145，pp.30、69、94n）保持S3组 `new-person:cristoforo-roncalli-a72597e026`，现映射至 `units/persons/cristoforo-roncalli`。第2章全名与Pomarancio别名、第3章Pomerancio异拼和第4章注3的Roncalli校改讨论相合；既有manifest无同名person KU。
- 第4章关于Romanelli/Pomarancio抄写问题的说明保留Haskell转述与Nicolson可能性限定。8条直接S2陈述均为关系候选，全部留待S6；本轮未新增正式关系。
- `build_field_facts.py` 预检无警告并apply新增5条source-backed字段记录、来源数不变；unverified数量保持1,578。S4累计324组/422条映射，待登记4,516组/4,597条；person已登记106组，待登记978组/1,014条成员；KU总数1343。

### S4 person：Paul Fréart de Chantelou 跨三章身份组登记（2026-10-16）

- `cand-0648`（C.csv#172，pp.106、146、176）保持S3组 `new-person:chantelou-de-freart-paul-258ab261f8`，现映射至 `units/persons/paul-freart-de-chantelou`。索引全名与第4章无重音写法、第6章简称及第7章全名相合；既有manifest无同名person KU。
- 卡片仅记录书内姓名、拼写变体、Poussin的巴黎赞助人及受未具名Surintendant派遣的代理人角色；中文展示名标为项目工作音译。7条直接S2陈述均为关系候选，全部留待S6；本轮未新增正式关系。
- `build_field_facts.py` 预检无警告并apply新增5条source-backed字段记录、来源数不变；unverified数量保持1,578。S4累计325组/423条映射，待登记4,515组/4,596条；person已登记107组，待登记977组/1,013条成员；KU总数1344。

### S4 person：Vittorio Amedeo II, Duke of Savoy 跨两章身份组登记（2026-10-16）

- `cand-2388`（S.csv#76，pp.89、200、202）保持S3组 `new-person:amedeo-ii-of-savoy-vittorio-bf13fb4fc0`，现映射至 `units/persons/vittorio-amedeo-ii-duke-of-savoy`。p.89叙述置于1680年Oliva召Pozzo赴罗马之后；p.200–202转入西班牙王位继承战争，索引将三页列在同一姓名项下，年代语境相容。
- 卡片保留索引姓名`Vittorio Amedeo II`与正文形式`Victor Amadeus of Savoy`，只记录萨伏依公爵身份和书内语境；9条直接S2陈述为关系候选，另1条信念陈述为非关系候选。本轮不新增正式边。
- `build_field_facts.py` 预检无警告并apply新增4条source-backed字段记录、来源数不变；unverified数量保持1,578。S4累计326组/424条映射，待登记4,514组/4,595条；person已登记108组，待登记976组/1,012条成员；KU总数1345。

### S4 person：Felice Boscarati 跨两章身份组登记（2026-10-16）

- `cand-0411`（B.csv#258，pp.326–327、408）保持S3组 `new-person:boscarati-felice-af2f756b3b`，现映射至 `units/persons/felice-boscarati`。第10章p.326–327与第20章后记p.408均给出全名/姓氏锚点，既有manifest无同名person KU。
- 卡片只登记书内姓名、艺术家身份及来源限定；“official painter”不扩展为正式薪职，后记的审讯证词保留为Haskell经Olivato转述，原论文和案卷未独立查阅。6条直接关系候选留待S6，1条讽刺倾向评价保持非关系候选。
- `build_field_facts.py` 预检无警告并apply新增4条source-backed字段记录、来源数不变；unverified数量保持1,578。S4累计327组/425条映射，待登记4,513组/4,594条；person已登记109组，待登记975组/1,011条成员；KU总数1346。

### S4 person/work：Baglione人物与直接作品端点登记（2026-10-16）

- Giovanni Baglione人物组 cand-0156/0157/0158 映射至一个person KU；The Resurrection工作组 cand-5013/5297 映射至一个work KU，Divine Love cand-6045与Earthly Love cand-6046各登记为独立work KU。三组人物/作品身份判断均附有书内证据和候选映射。
- 六条直接人物关系候选的端点现均有KU；Divine Love与Earthly Love的2条直接关系候选也有对应作品端点。所有关系保持待S6审查，本批没有新增正式关系或外部身份核验。
- 当前S4为331组/432条候选映射已登记，待登记4,507组/4,587条；KU总数1350。字段表经build_field_facts.py预检无警告并apply新增13条source-backed记录，来源登记未变化、unverified保持1,578。

### S3复核与S4人物端点：M索引候选组（2026-10-18）

`cand-1552` → `../units/persons/sarah-churchill.md`（`new-person:sarah-churchill-duchess-of-marlborough`）；
`cand-1585` → `../units/persons/pierre-louis-moreau-de-maupertuis.md`（`new-person:pierre-louis-moreau-de-maupertuis`）；
`cand-1586` → `../units/persons/maximilian-ii-emanuel-of-bavaria.md`（`new-person:maximilian-ii-emanuel-of-bavaria-074eaa9da4`）；
`cand-1605` → `../units/persons/christian-ludwig-ii-of-mecklenburg-schwerin.md`（`new-person:christian-ludwig-ii-mecklenburg-schwerin`）；
`cand-1587` → `../units/persons/maximilian-ii-emanuel-of-bavaria.md`（`new-person:maximilian-ii-emanuel-of-bavaria-074eaa9da4`）。cand-1586、cand-1587经Deutsche Biographie GND 11857941X合并为一个人物组及一张KU卡。cand-1525由new改为undecided：p.216只有‘Marquis of Mantua’头衔，没有可唯一确认的个人姓名，旧S3 full-name理由撤回。本批6条直接S2 relation_candidate继续待S6；未新增正式关系。S4累计1,008组/1,186条候选映射已登记，3,762组/3,776条待登记；KU=2027。

### S4人物端点：Medici索引候选组（2026-10-18）

cand-1606 → ../units/persons/anna-maria-ludovica-de-medici.md（new-person:anna-de-ludovica-maria-medici-4e4e0c1fff）；
cand-1626 → ../units/persons/francesco-maria-de-medici.md（new-person:de-francesco-maria-medici-d2f7719ab0）；
cand-1627 → ../units/persons/gian-gastone-de-medici.md（new-person:de-gastone-gian-medici-6164ea1b9e）；
cand-1628 → ../units/persons/isabella-de-medici.md（new-person:de-isabella-medici-6acace310c）。本批5条直接关系候选继续待S6；cand-1628与未决的cand-5550未合并。S4累计1,012组/1,190条候选映射已登记，3,758组/3,772条待登记；KU=2031。

### S4人物端点：M索引候选组（2026-10-18）

cand-1673 → ../units/persons/alvise-mocenigo.md（new-person:alvise-doge-mocenigo-112023801c）；cand-1689 → ../units/persons/michel-de-montaigne.md（new-person:de-michel-montaigne-49e9b48a8a）；cand-1692 → ../units/persons/federigo-da-montefeltre.md（new-person:da-federigo-montefeltre-7c480bf440）；cand-1697 → ../units/persons/claudio-monteverdi.md（new-person:claudio-monteverdi-306c7d79d5）。4条直接关系候选继续待S6；Monteverdi脚注仅保留书目定位。S4累计1,016组/1,194条候选映射已登记，3,754组/3,768条待登记；KU=2035。

### S4人物端点：S索引候选组（2026-10-18）

cand-2347 → ../units/persons/nicola-salvi.md（new-person:nicola-salvi-4ff08e1bab）；cand-2357 → ../units/persons/tommaso-de-santi.md（new-person:de-santi-tommaso-ed5fd73fba）；cand-2358 → ../units/persons/carlo-saraceni.md（new-person:carlo-saraceni-d6fa6d7fe0）；cand-2360 → ../units/persons/giuseppe-sardi.md（new-person:giuseppe-sardi-d9fb8f5ac8）。7条relation_candidate记录继续待S6；Gherardo／Girardo身份对应未并入Tommaso裁决。S4累计1,020组/1,198条候选映射已登记，3,750组/3,764条待登记；KU=2039。

### S3人物身份复核：Duchess of Savoy（2026-10-18）

cand-2383由new改为undecided，撤回原身份组并暂不登记KU：原书只给出头衔、世纪末语境与Turin关联，没有具名或跨章身份锚点可将其对应到cand-2380或cand-2381。两条直接关系候选继续待S6。

### S4 人物身份组登记：S索引四个直接端点（2026-10-18）

cand-2415 → ../units/persons/corneille-schut.md；cand-2417 → ../units/persons/giovanni-segala.md；cand-2419 → ../units/persons/sebastiano-serlio.md；cand-2436 → ../units/persons/giovanni-dubravio-skala.md。五条S2关系候选继续待S6；Skala相关两条保留原文的试探语气。S4累计1,028组/1,206条候选映射已登记，3,741组/3,755条待登记；KU=2047。

### S4 人物身份组登记：S索引四个直接端点（2026-10-18）

cand-2437 → ../units/persons/john-skippe.md；cand-2439 → ../units/persons/francesco-sleter.md；cand-2508 → ../units/persons/andrea-stazio.md；cand-2511 → ../units/persons/nicholas-stone.md。六条S2关系候选继续待S6；Sleter跨p.286–287续接、Stazio遗嘱未具名画作委托者、Stone陈述的转引层级均保留。S4累计1,032组/1,210条候选映射已登记，3,737组/3,751条待登记；KU=2051。

### S4 人物身份组登记：Adelaide Enrichetta、Worsley、Vittrice、Visconti四个直接关系人物组（2026-10-18）

cand-2380 → ../units/persons/adelaide-enrichetta-of-savoy.md；cand-2819 → ../units/persons/sir-richard-worsley.md；cand-2787 → ../units/persons/alessandro-vittrice.md；cand-2781 → ../units/persons/antonio-maria-visconti.md。十条S2关系候选继续待S6；Adelaide与其他Savoy称谓候选不合并，Vittrice的《基督下葬》链接既有work KU且保留未具名礼拜堂与委托未明限定，Visconti被盗画作对象cand-11910继续待证。S4累计1,036组/1,214条候选映射已登记，3,733组/3,747条待登记；KU=2055。

### S4 人物身份组登记：Savorgnan、Strudel、Subleyras与Swanevelt四组直接人物端点（2026-10-18）

cand-2378 → ../units/persons/faustina-savorgnan.md；cand-2529 → ../units/persons/peter-strudel.md；cand-2532 → ../units/persons/giuseppe-subleyras.md；cand-2535 → ../units/persons/hermann-swanevelt.md；四组共10条S2关系候选保持待S6及原书限定；候选作品cand-7195、cand-7196、cand-10494、cand-11915继续待证，不新增作品KU或formal relation。S4累计1,040组/1,218条候选映射已登记，3,729组/3,743条待登记；KU=2059。

### S4 人物身份组登记：Anne Marie、Shaftesbury、Stanislas与Talbot四组人物端点（2026-10-18）

cand-2381 → ../units/persons/anne-marie-of-savoy.md；cand-2425 → ../units/persons/1st-earl-of-shaftesbury.md；cand-2505 → ../units/persons/stanislas-poniatowski-king-of-poland.md；cand-2539 → ../units/persons/buno-talbot.md；六条S2关系候选保持待S6；Anne Marie只作收据署名者，Shaftesbury保留爵位称名，Talbot索引拼写Bruno与正文Buno并列保存；Stanislas相关未具名Warsaw views候选cand-9156仍待证。S4累计1,044组/1,222条候选映射已登记，3,725组/3,739条待登记；KU=2063。

### S4 人物身份组登记：Tassi、Temanza、Tessin与Thornhill四组人物端点（2026-10-18）

cand-2542 → ../units/persons/agostino-tassi.md；cand-2546 → ../units/persons/tommaso-temanza.md；cand-2555 → ../units/persons/nicodemus-tessin-younger.md；cand-2568 → ../units/persons/james-thornhill.md；8条S2关系候选继续待S6；Tessin第406页身份沿用索引归组并保留正文简称；本批未新增正式关系或外部来源。S4累计1,048组/1,226条候选映射已登记，3,721组/3,735条待登记；KU=2067。

### S4 人物身份组登记：Teniers、Théodon、Tofts与Torelli四组人物端点（2026-10-18）

cand-2549 → ../units/persons/david-teniers.md；cand-2566 → ../units/persons/jean-baptiste-theodon.md；cand-2639 → ../units/persons/katherine-tofts.md；cand-2647 → ../units/persons/giacomo-torelli.md；9条S2关系候选继续待S6；Teniers正文仅用姓氏；Théodon相关作品候选仍为undecided；Tofts只对应Smith第一段婚姻，其余同段人物关系分开保留；本批未新增正式关系或外部来源。S4累计1,052组/1,230条候选映射已登记，3,717组/3,731条待登记；KU=2071。

### S4 人物身份组登记：Torelli、Torresani、Triva与Tron四组人物端点（2026-10-18）

cand-2648 → ../units/persons/giuseppe-torelli.md；cand-2649 → ../units/persons/andrea-torresani.md；cand-2654 → ../units/persons/antonio-triva.md；cand-2655 → ../units/persons/caterina-dolfin-tron.md；4条S2关系候选继续待S6；Torelli书信未证明作品完成，Torresani数量保留OCR与页图读数差异，Tron相关讨论保留可能语气；未新增正式关系或外部来源。S4累计1,056组/1,234条候选映射已登记，3,713组/3,727条待登记；KU=2075。

### S4 人物身份组登记：de Troy、Tubeuf、Turchi与Uccelli四组人物端点（2026-10-18）

cand-2656 → ../units/persons/francois-de-troy.md；cand-2657 → ../units/persons/jacques-tubeuf.md；cand-2660 → ../units/persons/alessandro-turchi.md；cand-2665 → ../units/persons/ferdinando-uccelli.md；5条S2关系候选继续待S6；Turchi索引页码栏为空，按正文锚点保留身份依据；Uccelli所涉档案清单未独立查阅；未新增正式关系或外部来源。S4累计1,060组/1,238条候选映射已登记，3,709组/3,723条待登记；KU=2079。

### S4 人物身份组登记：Vico、Vigarani、Viola与Viviani四组人物端点（2026-10-18）

cand-2770 → ../units/persons/giambattista-vico.md；cand-2774 → ../units/persons/gaspare-vigarani.md；cand-2776 → ../units/persons/domenico-viola.md；cand-2788 → ../units/persons/vincenzo-viviani.md；4条S2关系候选继续待S6；Vico脚注所引材料未独立核读且Conti身份仍待决，Vigarani条目不推定剧场建成，Viviani正文保留姓氏层级；未新增正式关系或外部来源。S4累计1,064组/1,242条候选映射已登记，3,705组/3,719条待登记；KU=2083。

### S4 人物身份组登记：Vleughels、de Wael、Wagner与Webster四组人物端点（2026-10-18）

cand-2789 → ../units/persons/nicolas-vleughels.md；cand-2795 → ../units/persons/jean-baptiste-de-wael.md；cand-2796 → ../units/persons/joseph-wagner-printseller.md；cand-2805 → ../units/persons/john-webster-playwright.md；6条S2关系候选继续待S6；Vleughels两份集体名单均不分配到单件或个别会面，de Wael的life为页图校读，Wagner店铺身份与Webster影响说均保留来源限定；未新增正式关系或外部来源。S4累计1,068组/1,246条候选映射已登记，3,701组/3,715条待登记；KU=2087。

### S4 人物身份组登记：Wilson、de Witte、Wouwermans与Wren四组人物端点（2026-10-18）

cand-2815 → ../units/persons/richard-wilson.md；cand-2817 → ../units/persons/peter-de-witte.md；cand-2820 → ../units/persons/philips-wouwermans.md；cand-2821 → ../units/persons/christopher-wren.md；5条S2关系候选继续待S6；Wilson的接待名单、de Witte的多人藏品作者名单、Wouwermans的学习建议与风格比较、以及Wren参与的未具名教堂装饰均保留原书语境和限制；无外部来源、正式关系或backlog写入。S4累计1,072组/1,250条候选映射已登记，3,697组/3,711条待登记；KU=2091。

### S4 人物身份组登记：Wyatt、Young、Zaguri与Zuccalli四组人物端点（2026-10-18）

cand-2823 → ../units/persons/james-wyatt.md；cand-2827 → ../units/persons/edward-young.md；cand-2829 → ../units/persons/pietro-zaguri.md；cand-2878 → ../units/persons/enrico-zuccalli.md；5条S2关系候选继续待S6；Wyatt仅属Smith英国访客名单；Young的索引主条及同主条Night Thoughts子目分列，cand-2828仍S3 undecided、cand-10551仍excluded，未登记作者正式边；Zaguri的争论保留friendly限定；Zuccalli委建语境不指定委托人或工程完成状态；无外部来源、正式关系或backlog写入。S4累计1,076组/1,254条候选映射已登记，3,693组/3,707条待登记；KU=2095。

### S4 人物身份组登记：Zambelli、Zanotti、Zen与Zucchi四组人物端点（2026-10-18）

cand-2833 → ../units/persons/paola-zambelli.md；cand-2863 → ../units/persons/eustachio-zanotti.md；cand-2868 → ../units/persons/alessandro-zen.md；cand-2886 → ../units/persons/andrea-zucchi.md；仅Andrea Zucchi关联1条直接S2关系候选并留待S6；Paola Zambelli致谢、Eustachio Zanotti书信定位、Alessandro Zen死亡报告均不扩写成正式关系；同段题献给Zaccaria Sagredo的版画不归给Andrea Zucchi。无外部来源、正式关系或backlog写入。S4累计1,080组/1,258条候选映射已登记，3,689组/3,703条待登记；KU=2099。

### S4 人物身份组登记：Acqua、Albani、Altham与Anne of Austria四组人物端点（2026-10-18）

cand-0010 → ../units/persons/cristoforo-dall-acqua.md；cand-0020 → ../units/persons/annibale-albani.md；cand-0085 → ../units/persons/james-altham.md；cand-0109 → ../units/persons/anne-of-austria-regent-france.md；dall’Acqua的两条版画陈述、Albani参与支持d’Adda邀Viani、Altham肖像／游客陈述及Anne of Austria语境关系均留待S6；不新增外部来源或正式关系。S4累计1,084组/1,262条候选映射已登记，3,685组/3,699条待登记；KU=2103。

### S4 人物身份组登记：Bagutti、Balbi、Baldi与Bandinelli四组人物端点（2026-10-18）

cand-0161 → ../units/persons/pietro-martire-bagutti.md；cand-0164 → ../units/persons/paolo-battista-balbi.md；cand-0165 → ../units/persons/lazzaro-baldi.md；cand-0179 → ../units/persons/baccio-bandinelli.md；Bagutti教堂装饰团队、Balbi多人藏画陈述及Bandinelli／Parmigianino假设草图语境的三条S2关系候选留待S6；Baldi的p.60委托句保留供S6反向关系审查，当前无对应S2 relation_candidate；不新增正式关系、外部来源或backlog项目。S4累计1,088组/1,266条候选映射已登记，3,681组/3,695条待登记；KU=2107。

### S4 人物身份组登记：Baratta、Bassanino、Bedford与Bellotti四组人物端点（2026-10-18）

cand-0181 → ../units/persons/francesco-baratta.md；cand-0255 → ../units/persons/virgilio-bassanino.md；cand-0267 → ../units/persons/john-4th-duke-of-bedford.md；cand-0278 → ../units/persons/pietro-bellotti.md；Baratta财务纠纷、Bassanino绘画及Livorno语境、Bedford景观委托和Bellotti慕尼黑受雇四条S2关系候选留待S6；不新增外部来源、正式关系或backlog项目。S4累计1,092组/1,270条候选映射已登记，3,677组/3,691条待登记；KU=2111。

### S4 人物身份组登记：Benefial、Bertos、Blainville与Borromeo四组人物端点（2026-10-18）

cand-0288 → ../units/persons/marco-benefial.md；cand-0368 → ../units/persons/francesco-bertos.md；cand-0378 → ../units/persons/monsieur-de-blainville.md；cand-0403 → ../units/persons/federico-borromeo-cardinal.md；Benefial第三幅Agrippina题材画、Bertos青铜群组及Borromeo影响的比较语境三条S2关系候选留待S6；Blainville跨章两处引文同指卷I第492页，archive候选cand-10390继续undecided并与人物组分开；不新增正式关系或外部来源。S4累计1,096组/1,274条候选映射已登记，3,673组/3,687条待登记；KU=2115。

### S4 人物身份组登记：Both、Bramante、Bramer与Brand四组人物端点（2026-10-18）

cand-0416 → ../units/persons/jan-both.md；cand-0443 → ../units/persons/donato-bramante.md；cand-0444 → ../units/persons/leonard-bramer.md；cand-0445 → ../units/persons/johannes-christian-brand.md；Both的群体陈述保留probably，Bramante仅在建筑复兴者集合引文中出现，Bramer与Brand分别留在Roomer藏画及Zanetti藏画的多人表述范围内；五条S2关系候选留待S6，不新增正式关系。S4累计1,100组/1,278条候选映射已登记，3,669组/3,683条待登记；KU=2119。

### S4 人物身份组登记：Velvet Breughel、du Breuil、Paul Brill与Charles de Brosses四组人物端点（2026-10-18）

cand-0449 → ../units/persons/jan-brueghel-the-elder.md；cand-0450 → ../units/persons/toussaint-du-breuil.md；cand-0453 → ../units/persons/paul-bril.md；cand-0455 → ../units/persons/charles-de-brosses.md；Velvet Breughel和Paul Brill的Getty ULAN身份记录分别列于alignment.csv，规范显示名采用Jan Brueghel the Elder与Paul Bril；de Brosses的章10人物候选cand-9436随后复核为本KU的same，章10引文定位及第21章书目对象保持archive类型。四条直接关系候选继续留待S6，不新增正式关系。S4累计1,104组/1,282条候选映射已登记，3,665组/3,679条待登记；KU=2123。

### S3 person：de Brosses跨章人物身份复用（2026-10-18）

cand-9436由new改为same，映射至[Charles de Brosses KU](../units/persons/charles-de-brosses.md)。第10章p.311注5与S1索引B.csv#302的311n定位相合，第21章书目提供Charles de Brosses全名；人物same裁决与书目／引文archive候选分开。

### S4 人物身份组登记：Brugiori、Brunelleschi、Brusoni与Burrini四组人物（2026-10-18）

cand-0456 → ../units/persons/domenico-brugiori.md；cand-0459 → ../units/persons/filippo-brunelleschi.md；cand-0461 → ../units/persons/girolamo-brusoni.md；cand-0473 → ../units/persons/giovanni-antonio-burrini.md；Brunelleschi、Brusoni、Burrini的Treccani DBI身份记录列于alignment.csv；Brugiori仅据书内全名登记，作品cand-0457保持独立work候选。相关S2关系候选仍留待S6，不新增正式关系。S4累计1,108组/1,286条候选映射已登记，3,660组/3,674条待登记；KU=2127。

## 未解决项与交接限制

- 664 个候选的 `suggested_type` 仍为空（621 个保持 `undecided`、43 个按 S1 理由排除）；未分类不是已解决，也未强塞现有类型。其余 `undecided` 与 `conflict` 对象均已进入 S3 对齐表，保留身份问题及后续去向；不按名称直接合并。
- 331条开放候选继续保留缺证理由；原文未给出的匿名人物、作品组成员、日期、版本和关系目标不补猜。端点可登记、身份可确认及关系可成立分别判断。
- `enr-06678`、`enr-06937` 的 source_ref 无法从对应卡片来源列表解析，属于既有 S5 缺口；1,578条未核验字段不自动升级。身份或书目匹配也不表示读过原件或验证其全部事实。
- 原书异文、OCR 校读和印本标记问题按证据保留，包括 p.247 印号不可见、p.270 注7疑似错位、p.359 注4无标记且重复注3、p.377 正文标号6与页底注5错配。S2 校读没有改写来源本体。
- S2 为内部语义处理与自查，尚未形成独立语义验收或全书 precision/recall 估计；S3 完成的是逐候选决定闭包，不等于所有未决身份已查明。KU 的 confidence/consensus 也没有因机械检查而统一赋值。
- `release/v0.1/` 与 [v0.2-draft](../../release/v0.2-draft/README.md) 是既有快照。后者 metadata 创建日期为2026-09-26，仍含790段、686条提及、192条断言的旧包，不覆盖当前全书 S2，不是本次 S7 交付；作者信息按用户要求留空，公开权利、许可和最终引用尚未完成。

## 完成依据与接续

- S0–S2 逐章阅读、来源核对与处理状态见[分段处理记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)及[阶段结果](../../03-processing/patrons-and-painters-full-book-s2/results/stages.md)。
- S3 身份决定、跨章分组、候选变化及证据去向见[知识处理记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)；当前逐候选决定见[alignment.csv](../tables/alignment.csv)。
- S4 KU 清单为[ku-manifest.csv](../tables/ku-manifest.csv)，有效卡片入口见[accepted.yml](../accepted.yml)。Luigi Pavini 与 Alessandro Farnese 公爵两个 backlog 端点已登记，backlog 均为 `completed`；相应正式关系仍待 S6。

接续工作按类型推进剩余 S4 `new` 组，优先处理直接关系端点；已有 same 复用目标不重复建卡，同组候选映射到同一 KU，conflict 与 undecided 对象继续保留待证。S4 收口后再按实际缺口进入 S5；本轮全书 S5–S7 尚未完成。


### S4：Pietro Edwards 跨章人物与档案端点登记（2026-10-16）

人物候选 `cand-0965` 登记为[皮耶特罗·爱德华兹人物卡](../units/persons/pietro-edwards.md)；档案候选 `cand-8534` 登记为[MSS. 788.13 清单档案卡](../units/archives/pietro-edwards-inventories-seminario-patriarcale-ms-788-13.md)。p.261 与 p.380 共享手稿号，但原件和目录未查阅；档案描述不等同于原题或完整目录著录，时间保持书内模糊表述。6条人物关系候选和2条档案关系候选待 S6，未写入正式边；Girolamo Manfrin 人物端点已登记。S4 当前登记333组/434条映射，待登记4,505组/4,585条；KU 总数1,352。

### S4：Scipione Maffei 人物与古代雕塑术语登记（2026-10-16）

人物候选 `cand-1487` 登记为[Scipione Maffei 人物卡](../units/persons/scipione-maffei.md)；`cand-12249` 登记为[古代雕塑术语卡](../units/terms/antique-sculpture-maffei-context.md)。卡片保留书内三章人物锚点和术语通类边界。5条关系候选留待 S6；Lodoli、Ferdinand de’ Medici 与 Angelo Querini 已有 KU，古代雕塑端点已登记；“记录过去遗存”的对象仍未具体识别，保持开放，不新增正式关系。S4 当前登记335组/436条映射，待登记4,503组/4,583条；KU 总数1,354。

### S3 复核：Piola 候选复用既有人物卡（2026-10-16）

`cand-1935` 原 S3 `new` 组经原书同章交叉核对后改为 `same`，复用[Paolo Gerolamo Piola 人物卡](../units/persons/paolo-girolamo-piola.md)。旧卡已引第1章 p.8、p.10 中本候选的全名原文，并记录相同索引行及 Gerolamo/Girolamo 名形；因此不另建人物 KU。旧组和旧理由留在 alignment 行作为历史。关系候选仍待 S6，原件或开放对象缺口未因此解除。更新后 S3 same=1,782/1,027 KU，new=5,018/4,837组；S4 待登记4,502组/4,582条。

### S4：Casanova de Seingalt 跨章人物组登记（2026-10-16）

候选 `cand-0591` 登记为[Jacques Casanova de Seingalt 人物卡](../units/persons/jacques-casanova-de-seingalt.md)。索引全名对应 p.274、364、367、375；正文使用 Casanova。五条关系候选留待 S6；Corner 与 Memmo 已有 KU，Eusebio 与 Count of Waldstein 仍待 S4。本轮不新增正式边或扩写 Count of Waldstein 的身份。S4 当前登记336组/437条映射，待登记4,501组/4,581条；KU 总数1,355。

### S4 记录修订：Casanova 索引 OCR 限定补录（2026-10-17）

Casanova 人物卡补入书末索引 p.449 OCR L768 的来源定位；OCR 行漏识首字母 C，故卡片并列保留原始OCR串和规范化候选索引行 `C.csv#115`，并明确索引仅作定位。人物卡 `updated` 改为2026-10-17。此修订不改alignment、KU manifest或正式关系。

### S4：Eusebio della Lena 人物端点登记（2026-10-17）

`cand-1386` 登记为[Eusebio della Lena 人物卡](../units/persons/eusebio-della-lena.md)。姓名形式依据书末索引，正文仅称 Eusebio，并以兄弟关系提供语境。其与 Casanova 的关系候选待 S6；未新增正式关系。S4 当前登记337组/438条映射，待登记4,500组/4,580条；KU 总数1,356。

### S3/S4：Waldstein 伯爵称谓限定（2026-10-17）

`cand-2797` 保持 source-local `new`，登记为[Count of Waldstein 人物卡](../units/persons/count-of-waldstein-casanova-dux.md)。旧 S3 备注误称原书提供全名，现已在 alignment 行追加更正：原书只给爵称及“Casanova 在 Dux 的保护人”语境；旧备注中按 `(of waldstein)` 全名／别名锚点聚组的说法也已撤回，组 token 仅作追踪标识。卡片未推定名字或外部身份。是否为 Prà della Valle 一座雕像出资只是 Memmo 的询问，未证明承诺；雕像候选 `cand-11561` 保持 `undecided`，两条关系候选待 S6。S4 当前登记338组/439条映射，待登记4,499组/4,579条；KU 总数1,357。

### S4 验证：Waldstein source-local person 登记（2026-10-17）

- `build_field_facts.py` 预检：cards=1,357；enrichment rows=10,476；new/changed/removed IDs 均为0；source registry changes=0；warnings=0。无字段表写回。
- `audit_tables.py --strict-stage --summary` 退出码0：KU=1,357；`errors=[]`、`s2_missing=[]`；待登记 new alignment 共4,594条，其中4,579条候选映射（4,499组）和15条外部身份记录。既有两条来源引用警告（`enr-06678`、`enr-06937`）与S2语义审查提示继续保留。卡片/清单/映射对齐；Casanova 关系候选端点现有 KU，但两条关系候选仍待 S6，未改 `relations.csv`。


### S4 person：Robert Adam 跨章身份组（2026-10-17）

`cand-0012`、`cand-0013` 共映射至[Robert Adam 人物卡](../units/persons/robert-adam.md)，依据第10、13章及附录中的跨章全名锚点。3条直接关系候选留待 S6；p.310 访问叙述保留为非关系陈述。S4 当前登记339组/441条映射，待登记4,498组/4,577条；KU 总数1,358。


### S4 institution：Papal States 跨章身份组（2026-10-17）

`cand-1831`、`cand-1832`、`cand-1833` 共映射至[教皇国卡](../units/institutions/papal-states.md)。书内名称及第2、6、8章地域语境支持同一政治实体；Treccani 仅支持身份/类型，不扩展书中具体史实。8条关系候选留待 S6，两个非关系陈述仍按原分类保留。S4 当前登记340组/444条映射，待登记4,497组/4,574条；KU 总数1,359。

### S3 复核：Colonna palace 与售予 Chigi 的宫殿（2026-10-17）

旧组 `sg3-place-colonnapalace` 拆分为两个 place 身份组：`cand-0815` 保留 Colonna family palace；`cand-0816` 改入 `sg3-place-chigi-palace-ss-apostoli`，指向1662年由 Colonna 家族一支售给 Cardinal Flavio Chigi、位于 Piazza SS. Apostoli 的另一座宫殿。第6章 p.155 明确称两座宫殿相邻而非同一座；原理由保留在 alignment 历史字段。S3 new 共5,018条候选/4,838组；S4 待登记4,498组/4,574条映射。

### S4 place：Colonna / Chigi 两座宫殿分别登记（2026-10-17）

`cand-0815` 与 `cand-0816` 分别映射到[Colonna 家族宫殿卡](../units/places/colonna-family-palace-rome.md)和[Flavio Chigi 宫殿卡](../units/places/flavio-chigi-palace-ss-apostoli.md)。S3 已根据 p.154–155 拆为两个相邻建筑组。分别有4条和5条关系候选待 S6；未新增正式关系。S4 当前登记342组/446条映射，待登记4,496组/4,572条；KU 总数1,361。

### S4 person：van den Einden 与 Louis Phélipeaux de la Vrillière（2026-10-17）

`cand-0914`→[Ferdinand van den Einden 卡](../units/persons/ferdinand-van-den-einden.md)；`cand-0915`→[Jan van den Einden 卡](../units/persons/jan-van-den-einden.md)；`cand-1347`→[Louis Phélipeaux de la Vrillière 卡](../units/persons/louis-phelipeaux-de-la-vrilliere.md)。Ferdinand、其父 Jan 及 Louis 各按独立 S3 new 组登记；21条直接关系候选留待 S6，Jan 另有1条非关系陈述。未决的具名边界、群体成员与绘画系列保持 undecided；cand-6826、cand-6828、cand-7462 三个直接 work/term 端点现已登记；本批未新增正式关系。S4 当前登记345组/449条映射，待登记4,493组/4,569条；KU 总数1,364。

### S4 work/term：La Vrillière 与 van den Einden 的直接端点（2026-10-17）

`cand-6826`→[Guido Reni《The Rape of Helen》作品卡](../units/works/guido-reni-rape-of-helen.md)；`cand-6828`→[古代英雄题材术语卡](../units/terms/la-vrilliere-heroic-antique-themes.md)；`cand-7462`→[受威尼斯影响的后辈画家术语卡](../units/terms/later-painters-inspired-by-venetians-patronised-by-van-den-einden.md)。三条直接关系候选留待 S6，未新增正式关系；相似题名的 Pietro da Cortona《Rape of Helen》保持独立。S4 当前登记348组/452条映射，待登记4,490组/4,566条；KU 总数1,367。

### S4 person：Marco Sacconi（2026-10-17）

`cand-2325`→[Marco Sacconi 人物卡](../units/persons/marco-sacconi.md)。页233、240的姓氏提及由书后索引全名定位；8条直接关系候选留待 S6，3条评价性陈述保持非关系。未新增正式关系。S4 当前登记349组/453条映射，待登记4,489组/4,565条；KU 总数1,368。

### S3–S4 复核：Della Lena 与关联人物/文献端点（2026-10-17）

`cand-11152` 已并入 `cand-1387` 的 Giacomo della Lena 人物组：第16章 p.375 与后记 p.410 对同一题名及作者的明确对应，排除了只凭姓氏合并。Ortes 由第10章注释称谓与第16章全名、索引交叉归为同一书内人物；原索引首个页码转录差异记入卡片和 alignment。Giacomo、Innocenzo、Ortes、同题 treatise 文本、Correr 手稿定位组均已映射到各自 KU；旧组和新身份判断均保留于 alignment。32幅 Guardi 作品集合、未具名西班牙大使和 Moschini 的身份候选继续为 `undecided`；Lucca、Venice、Francesco Guardi、Biblioteca Correr 复用既有 KU。本批关系候选仍待 S6，未新增正式关系。S3 new 共5,018条候选/4,837组；S4 已登记354组/459条映射，待登记4,483组/4,559条；KU 总数1,373。

### S3–S4 复核：Grimaldi 与 Mazarin 画廊（2026-10-17）

Grimaldi 全名及第6章变体按同一索引条目与跨章页码归组；`cand-1232` 已登记一张 source-local person 卡。Mazarin 宫殿上层画廊按独立 place 身份登记，与 Palais Mazarin 和《Romulus and Remus》顶画分开。索引未支持的 Angelica Griè、成员不明艺术家集合、未定位神学院与工作室仍为 undecided；现有关系端点复用决定保持原样。本批关系候选留待 S6，未新增正式关系。S3 new 共5,018条候选/4,837组；S4 已登记356组/461条映射，待登记4,481组/4,557条；KU 总数1,375。

### S3 复核：Anthony Blunt 身份复用（2026-10-17）

`cand-0379` 与 `cand-5902` 从 `new-person:anthony-blunt-anthony-blunt-opinion-s-c8c64cf49b` 更正为 same，复用 `units/persons/anthony-blunt`；既有卡明确包含全名、惯用名与称号，候选 `cand-3722` 亦已指向该卡。旧决定和理由均留存于 alignment 历史字段。本轮没有新增 KU 或正式关系。S3 same=1,784；new=5,016/4,836；S4 待登记4,480组/4,555条候选映射。

### S3–S4 复核：Bassano 人物与 Nativity 作品分型（2026-10-17）

索引 B.csv#104、#105 同指 Jacopo Bassano；人物两条候选共用一张 KU。p.313 的 “Bassano’s Nativity” 则为作品而非人物：新增 source-local work 候选并已登记，修正 S2 对象端点及提及映射。两张卡均保留临摹关系候选供 S6 审查；没有生成 Guardi 临摹件或正式关系。S3 new=5,017/4,837；S4 已登记358组/464条映射，待登记4,479组/4,553条；KU 总数1,377。

### S3 复核：Pompeo Batoni 跨章候选复用（2026-10-17）

`cand-0260`、`cand-0261`、`cand-0262` 从 `new-person:batoni-pompeo-e737feffb7` 更正为 same，复用 `units/persons/pompeo-batoni`；既有卡明确记录全名与惯用名，`cand-3871` 已属同一 KU。旧决定和理由保存在 alignment 历史字段；未新增 KU 或正式关系。S3 same=1,787；new=5,014/4,836；S4 待登记4,478组/4,550条候选映射。

### S4 person：Abbate Michele Giustiniani 跨章人物组（2026-10-17）

`cand-1199` 与 `cand-4388` 共同映射至 `units/persons/abbate-michele-giustiniani`。第2章将其列为来信刊布者，第4、6章以 Abate/Abbate Michele Giustiniani 引用相关卷册；书目卷册身份继续待证，不与人物或彼此合并。S4 已登记359组/466条候选映射；待登记4,477组/4,548条；KU 总数1,378。


### S4 person：Giuseppe Toninotto 直接端点（2026-10-17）

`cand-2643` 映射至 `units/persons/padre-giuseppe-toninotto`。其8条直接 S2 关系候选保留待 S6；Frari、State Inquisition 与 Del Pian 版画候选待 S4，其余相关作品候选仍待身份消歧。未登记正式关系。S4 已登记360组/467条候选映射；待登记4,476组/4,547条；KU 总数1,379。

### S4 person/work：Antonio Zanchi 与《Moses striking the Rock》（2026-10-17）

`cand-2834`（UVWXYZ.csv#171）登记至[Antonio Zanchi 人物卡](../units/persons/antonio-zanchi.md)：第8章 p.218 全名、索引同一主项的 p.251 和 p.294 定位支持跨章人物归并。`cand-2835`（UVWXYZ.csv#172）与 `cand-7670` 按既有 S3 作品组 `workgrp-09d947ea36bdd8` 共映射至[《Moses striking the Rock》作品卡](../units/works/antonio-zanchi-moses-striking-rock-bergamo.md)；索引题名、正文画家及 Bergamo 委托语境相符。人物8条、作品7条直接关系候选继续待 S6；未写正式关系，未改 relations.csv。作品与索引中 Vannini 的同题子目保持区分。S4 累计登记362组/470条候选映射，待登记4,474组/4,544条；KU 总数1,381。


### S4 person：Charles II of England 跨章身份组（2026-10-17）

候选 `cand-0656`（C.csv#180）登记至[查理二世人物卡](../units/persons/charles-ii-of-england.md)。第7章 p.178 的 Prince of Wales 称谓与 pp.195–196 的 Charles II 王号及索引主项相接；8条直接关系候选留待 S6，本轮未登记正式关系。S4 已登记363组/471条候选映射；待登记4,473组/4,543条；KU 总数1,382。


### S3 place：S. Maria della Concezione 复用既有罗马嘉布遣会教堂 KU（2026-10-17）

候选 `cand-4521`（第2章 p.42 正文）和索引子目 `cand-0708`（C.csv#232，pp.42–43）现均由原 `new`／`undecided` 改为 `same`，映射至既有[罗马嘉布遣会教堂卡](../units/places/capuchin-church-rome.md)。索引页码对应的正文明确称 S. Maria della Concezione 是为嘉布遣会建立的教堂；该名称与既有卡已记录的 Santa Maria della Concezione dei Cappuccini 身份一致。相邻修道院候选 `cand-4522` 保持独立。10条直接关系候选不变，未创建新 KU 或正式关系。S3 same=1,789、new=5,013/4,835组、undecided=5,496；S4 已登记363组/471条映射，待登记4,472组/4,542条；KU 总数1,382。

### S4 institution：Accademia dei Lincei 跨章身份组（2026-10-17）

cand-0003（A.csv#2）由第2章 p.33 与第4章 p.99 的索引定位合并至[林琴科学院卡](../units/institutions/accademia-dei-lincei.md)。本卡保留意大利语名称，将中文名标为项目工作译名；Haskell 的“先驱”比较不作为已核实的正式沿革。8条直接关系候选待 S6，未新增正式关系。S4 当前登记364组/472条映射，待登记4,471组/4,541条；KU 总数1,383。

### S4 批次验证：Accademia dei Lincei（2026-10-17）

严格阶段审计通过：KU=1,383；candidates=12,406；alignments=12,632、unlinked=0；errors=[]；relations=1,227（formal=1,225）。字段事实现为10,495条，其中1,597条 unverified。8条 Lincei 关系候选继续待 S6；本批未登记正式关系。当前另有4,471组/4,541条候选映射待登记，及15条外部身份 alignment。两条既有 source_ref 警告与 S2 语义质量提示仍在。

### S4 place：Manin Palace, Venice 跨章/索引身份组（2026-10-17）

cand-1520（M.csv#57）登记至[马宁宫殿地点卡](../units/places/manin-palace-venice.md)。第9章 p.251 正文、注3与索引主项相互定位；与 Manin family 和 Passeriano country house 分开。9条关系候选留待 S6，2条非关系陈述保持原分类。S4 当前登记365组/473条映射，待登记4,470组/4,540条；KU 总数1,384。

### S4 批次验证：Manin Palace（2026-10-17）

严格阶段审计通过：KU=1,384；candidates=12,406；alignments=12,632、unlinked=0；errors=[]；relations=1,227（formal=1,225）。字段事实10,504条，其中1,606条 unverified；字段预览无变化，warnings=0。S4 已登记365组/473条候选映射；待登记4,470组/4,540条候选映射，另有15条外部身份 alignment。Manin Palace 的9条关系候选及2条非关系陈述保持原分类。

### S3 更正：Borghese Palace 复用既有 Bentivoglio/Mazarin 宫殿 KU（2026-10-17）

cand-0398（B.csv#245）由 new 更正为 same，映射至既有[马萨林购得的罗马本蒂沃利奥宫殿卡](../units/places/mazarin-bentivoglio-palace-rome.md)。第2章 p.49 将 Borghese 宫殿的1619年购置与后续 Bentivoglio—Lante—Mazarin 转手相连；第7章 p.183 注2给出相同转手链。保留原 new 决定与理由；8条关系候选未改。S3 same=1,790、new=5,012/4,834组；S4 待登记4,469组/4,539条；KU 总数1,384。

### S4 term：Stoicism in 17th century 术语身份组（2026-10-17）

cand-2510（S.csv#199）登记至[斯多葛主义术语卡](../units/terms/stoicism-seventeenth-century.md)。卡片按 pp.143–144 的作者叙述限定对象范围，保留 “some daring thinkers” 限定及 Rosa 1651年信件为 Haskell 注释转述的证据状态。9条直接关系候选留待 S6，未新增正式关系。S4 当前登记366组/474条映射，待登记4,468组/4,538条；KU 总数1,385。

### S4 person：Maria Mancini 直接关系端点身份组（2026-10-17）

`cand-1509`（M.csv#46）按 S3 身份组 `new-person:mancini-maria-652896852a` 登记至[玛丽亚·曼奇尼人物卡](../units/persons/maria-mancini.md)。索引反序全名对应第6章 p.155 的 Maria Mancini，p.156 的 wife/her 指代由同一段婚姻语境承接；本卡不与 Giulio Mancini 等同姓人物合并。仅记录 Haskell 对人物身份、婚姻和后续叙述的原书表述，不补具体亲属支系或外部生平。7条直接 S2 关系候选保持待 S6，未新增正式关系或字段事实。S4 累计登记367组/475条候选映射；待登记4,467组/4,537条；KU 总数1,386。

### S4 person：Giovanni Angelo Canini 直接关系端点身份组（2026-10-17）

`cand-0530`（C.csv#54）按 S3 组 `new-person:angelo-canini-giovanni-adbabef3e8` 登记至[乔瓦尼·安杰洛·卡尼尼人物卡](../units/persons/giovanni-angelo-canini.md)。索引页码 154, 161, 187n, 197n 与书内全名／变体相互定位；本卡仅记录 Haskell 可支持的身份与叙述，脚注所引研究未独立核读，身份不扩展至未具名对象或外部传记。5条直接关系候选保留待 S6，不新增正式关系。S4 累计登记370组/478条候选映射；待登记4,464组/4,534条；KU 总数1,389。

### S4 person：John Sheffield 直接关系端点身份组（2026-10-17）

`cand-0465`（B.csv#313）按 S3 组 `new-person:buckingham-john-of-sheffield-7b3adca9be` 登记至[约翰·谢菲尔德人物卡](../units/persons/john-sheffield-duke-of-buckingham.md)。索引页码 280, 281 与书内全名／变体相互定位；本卡仅记录 Haskell 可支持的身份与叙述，脚注所引研究未独立核读，身份不扩展至未具名对象或外部传记。7条直接关系候选保留待 S6，不新增正式关系。S4 累计登记370组/478条候选映射；待登记4,464组/4,534条；KU 总数1,389。

### S4 person：Giacomo Serra 直接关系端点身份组（2026-10-17）

`cand-2420`（S.csv#108）按 S3 组 `new-person:giacomo-mgr-serra-5c15ad9cae` 登记至[贾科莫·塞拉人物卡](../units/persons/giacomo-serra.md)。索引页码 70, 71 与书内全名／变体相互定位；本卡仅记录 Haskell 可支持的身份与叙述，脚注所引研究未独立核读，身份不扩展至未具名对象或外部传记。5条直接关系候选保留待 S6，不新增正式关系。S4 累计登记370组/478条候选映射；待登记4,464组/4,534条；KU 总数1,389。

### S4 person：Jean Jacques Rousseau 跨章人物组（2026-10-17）

`cand-2289`（Q-R.csv#217）按 S3 组 `new-person:jacques-jean-rousseau-ad86218db7` 登记至[让-雅克·卢梭人物卡](../units/persons/jean-jacques-rousseau.md)。索引将第10章 p.328 与第15章 pp.369、372 归入同一人物条目；本卡保留 Haskell 对 Rousseau 影响的书内叙述，不补外部身份或生卒信息。5条直接关系候选留待 S6；两条 `relation_candidate=false` 陈述保持原分类，未新增正式关系。S4 累计登记371组/479条候选映射；待登记4,463组/4,533条；KU 总数1,390。

### S4 person：Carlo Barberini 两候选同组登记（2026-10-17）

`cand-0194`（B.csv#41）与 `cand-0195`（B.csv#42 子项 monuments to）按同一 S3 组 `new-person:barberini-carlo-2f55dd94e4` 共映射至[卡洛·巴贝里尼人物卡](../units/persons/carlo-barberini-brother-of-urban-viii.md)。索引明示其为 Urban VIII 之兄；第2章 pp.26、31、41 的亲属称谓、全名和纪念叙述相互吻合。与 Antonio Barberini 卡中另一代父亲 Carlo Barberini 区分。6条直接关系候选待 S6，未新增正式关系。S4 累计登记372组/481条候选映射；待登记4,462组/4,531条；KU 总数1,391。


### S4 person：Antonio Barbaro 同组两候选登记（2026-10-17）

`cand-0184` 与 `cand-0185` 按 S3 组 `new-person:antonio-barbaro-antonio-barbaro-conception-e91bacacf4` 共同映射至[Antonio Barbaro 人物卡](../units/persons/antonio-barbaro.md)。书后索引主项定位第248、249、253页，S. Maria del Giglio 子项定位第248、249页；第248页同一段给出 Antonio Barbaro 全名与建筑语境，第253页再次以全名提及此人。卡片只记录 Haskell 书内说法，第249页脚注所引来源未独立核读。7条直接关系候选仍待 S6，未新增正式关系。S4 累计登记373组/483条候选映射；待登记4,461组/4,529条；KU 总数1,392。

### S4 person：Angelo Giori 跨章身份组登记（2026-10-17）

`cand-1190`（G.csv#97，pp.41、59）映射至[Angelo Giori 人物卡](../units/persons/angelo-giori.md)。索引同名主项、跨章页码和正文重复全名支持同一人物组；第41页关于其生平、监督 Urban VIII 墓工程及 Claude 收藏的内容，以及第59页的致信叙述，均保留为 Haskell 书内说法。脚注来源未独立核读，“rather mean”和“who was in charge”的范围分别保持作者评价及未定状态。7条直接关系候选仍待 S6，未新增正式关系。S4 累计登记374组/484条候选映射；待登记4,460组/4,528条；KU 总数1,393。

### S4 person：Pellegrino Peri 同组登记（2026-10-17）

`cand-1878` 与 `cand-6081` 按 S3 组 `new-person:pellegrino-peri-0180e88b93` 共同映射至[Pellegrino Peri 人物卡](../units/persons/pellegrino-peri.md)。索引主项与第5章 p.122 的全名及脚注同名锚点吻合。有关居所、Gaulli 雇用及 Carlone 债务为 Haskell 正文说法；注1中的1666年袭击与1681年失窃报告转引 Pascoli、Bertolotti，未独立核读。6条直接关系候选仍待 S6，未新增正式关系。S4 累计登记375组/486条候选映射；待登记4,459组/4,526条；KU 总数1,394。

### S4 person：Ferdinando, Duke of Mantua 跨章身份组登记（2026-10-17）

`cand-1523`（M.csv#60）映射至[Ferdinando, Duke of Mantua 人物卡](../units/persons/ferdinando-duke-of-mantua.md)。第7章 p.175 的全名、亲属语境和1624年爵位与书后索引主项相合；第1章 p.14 的曼托瓦公爵订画记录依索引归入同一条目。p.10 索引定位未在现有正文转录中找到明确对应，不作身份依据。父亲 Vincenzo 的确切身份及7条关系候选留待后续阶段，未新增正式关系。S4 累计登记376组/487条候选映射；待登记4,458组/4,525条；KU 总数1,395。

### S4 person：James Brydges，第一代 Chandos 公爵身份组登记（2026-10-17）

`cand-0647`（C.csv#171）映射至[James Brydges 人物卡](../units/persons/james-brydges-first-duke-of-chandos.md)。第10章 p.281 的全名、爵位与索引主项对应；卡片将第一代 Chandos 公爵作为人物头衔而非另一个实体。六条直接关系候选仍待 S6，未新增正式关系。S4 累计登记377组/488条候选映射；待登记4,457组/4,524条；KU 总数1,396。

### S4 person：Leonora Baroni 跨章身份组登记（2026-10-17）

`cand-0249` 与 `cand-5530` 按 S3 组 `new-person:baroni-leonora-970b86fc4c` 共同映射至[Leonora Baroni 人物卡](../units/persons/leonora-baroni.md)。第4章歌手及赞颂诗叙述、第7章 p.180–181 重复全名和索引页码96、180、181相合。第4章 OCR 页标缺一位，暂按索引定位记录为p.96；婚恋与成功评价仍属 Haskell 的书内说法。五条直接关系候选仍待 S6，未新增正式关系。S4 累计登记378组/490条候选映射；待登记4,456组/4,522条；KU 总数1,397。

### S4 person：Louis／Luigi Dorigny 跨章身份组登记（2026-10-17）

`cand-0944` 与 `cand-0945` 按 S3 组 `new-person:dorigny-louis-fc0f85a71c` 共同映射至[Louis Dorigny 人物卡](../units/persons/louis-dorigny.md)。第7章 p.201 全名、Manin 子项、p.251 的 Luigi 与 p.268 的 Louis 写法及赞助语境相合。第270页只见姓氏，按索引保留定位，不单独作身份锚点。5条直接关系候选仍待 S6，未新增正式关系。S4 累计登记379组/492条候选映射；待登记4,455组/4,520条；KU 总数1,398。

### S4 person：Cornelius de Wael 身份组登记（2026-10-17）

`cand-2794`（UVWXYZ.csv#131）映射至[Cornelius de Wael 人物卡](../units/persons/cornelius-de-wael.md)。索引及第5章 p.122 正文给出相同全名；人物描述保留 Haskell 对其商业活动、收藏及其与 Gaulli 相识的推断。6条直接关系候选仍待 S6，未新增正式关系。S4 累计登记380组/493条候选映射；待登记4,454组/4,519条；KU 总数1,399。

### S4 person：Archduke Leopold Wilhelm 身份组登记（2026-10-17）

`cand-1399`（L.csv#56）映射至[Archduke Leopold Wilhelm 人物卡](../units/persons/leopold-wilhelm-archduke.md)。第7章 p.193 全名与书后索引相合；侄子 Emperor Leopold I 保持独立。6条直接关系候选仍待 S6，未新增正式关系。S4 累计登记381组/494条候选映射；待登记4,453组/4,518条；KU 总数1,400。

### S4 person：Don Gasparo Altieri 身份组登记（2026-10-17）

`cand-0089`（A.csv#90）映射至[Don Gasparo Altieri 人物卡](../units/persons/don-gasparo-altieri.md)。书后索引姓名与第6章 p.161 正文相合；阿尔蒂耶里家族保持独立。6条直接关系候选仍待 S6，未新增正式关系。S4 累计登记382组/495条候选映射；待登记4,452组/4,517条；KU 总数1,401。

### S4 person：Giovanni Battista Crescenzi 身份组登记（2026-10-17）

`cand-0869`（C.csv#403）映射至[Giovanni Battista Crescenzi 人物卡](../units/persons/giovanni-battista-crescenzi.md)。索引姓名与第7章 p.173 正文全名相合；既有 Crescenzi family KU 保持独立，未具名的兄弟不作身份指认。6条直接关系候选仍待 S6，未新增正式关系。S4 累计登记383组/496条候选映射；待登记4,451组/4,516条；KU 总数1,402。

### S4 person：Daniele Dolfin III 身份组登记（2026-10-17）

`cand-0927`（D.csv#29）映射至[Daniele Dolfin III 人物卡](../units/persons/daniele-dolfin-iii.md)。索引将 pp.252、253 列于同一人物主项；Daniele IV 与 Daniele Dolfin（Udine 大主教）保持区分，6条直接关系候选仍待 S6。未新增正式关系。S4 累计登记384组/497条候选映射；待登记4,450组/4,515条；KU 总数1,403。

### S4 person：Antoine Watteau 跨章身份组登记（2026-10-17）

`cand-2804`（UVWXYZ.csv#141）映射至[Antoine Watteau 人物卡](../units/persons/antoine-watteau.md)。第10章 p.284 正文全名及索引跨页定位支持同一人物身份；p.277 提及的画作单独保留。5条直接关系候选仍待 S6，未新增正式关系。S4 累计登记385组/498条候选映射；待登记4,449组/4,514条；KU 总数1,404。

### S4 person：Virgin Mary 跨章身份组登记（2026-10-17）

`cand-3427` 映射至[Virgin Mary 人物卡](../units/persons/virgin-mary.md)。30条 S2 提及跨9个章节，第6章 p.162 与第10章 p.295 明示全名；人物与特定圣母像、作品保持区分。7条直接关系候选仍待 S6，未新增正式关系。S4 累计登记386组/499条候选映射；待登记4,448组/4,513条；KU 总数1,405。

### S4 person：Giovanni Paolo Pannini 身份组登记（2026-10-17）

`cand-1827`（P.csv#26）映射至[Giovanni Paolo Pannini 人物卡](../units/persons/giovanni-paolo-pannini.md)。索引的 P.csv#27 “Interior of the Pantheon”是分立 work 候选 `cand-1828`，S3 仍为 undecided；不据此或委托陈述将人物与作品合并。5条直接关系候选仍待 S6，且未登记正式关系。S4 累计登记387组/500条候选映射；待登记4,447组/4,512条；KU 总数1,406。

### S4 person：Johann Karl Loth 跨章身份组登记（2026-10-17）

`cand-1442`（L.csv#100）映射至[Johann Karl Loth 人物卡](../units/persons/johann-karl-loth.md)。第8章的 Karl Loth 与第9章的 Johann Karl Loth 对应索引同一人物主项。L.csv#101“and Grand Prince Ferdinand”与L.csv#102“Death of Abel”所对应候选仍待证；注5信件为分立 archive 候选，待 S4；自画像 work 候选仍待证。6条直接关系候选留待 S6，未登记正式关系。S4 累计登记388组/501条候选映射；待登记4,446组/4,511条；KU 总数1,407。

### S4 archive：Karl Loth 致 Grand Prince Ferdinand 的信（1691-08-14）登记（2026-10-17）

`cand-7931` 映射至[书信档案卡](../units/archives/karl-loth-letter-to-grand-prince-ferdinand-1691-08-14.md)。身份依据限于 Haskell 对 Fogolari 1937 的转述；刊本与原信未独立查阅。与 Loth 的 1 条直接关系候选仍待 S6，未登记正式关系。S4 累计登记389组/502条候选映射；待登记4,445组/4,510条；KU 总数1,408。

### S4 event：罗马贝加莫社群圣巴托洛梅奥瞻礼画展系列登记（2026-10-17）

`cand-11728` 映射至[事件卡](../units/events/bergamasque-community-st-bartholomew-exhibitions-rome.md)。登记的是周期性系列，起始年份未知、至迟1650年已兴盛；S. Bartolomeo all’Isola 瞻礼展系列保持独立。7条关系候选留待 S6，未登记正式关系。S4 累计登记390组/503条候选映射；待登记4,444组/4,509条；KU 总数1,409。

### S4 多类型：第5章展览关系端点登记（2026-10-17）

直接关系端点按 S3 原决定分别登记：`cand-6027` → [罗马贝加莫社群](../units/institutions/bergamasque-community-rome.md)；`cand-11729` → [S. Bartolomeo 教堂庭院](../units/places/church-s-bartolomeo-bergamasque-exhibition-courtyard.md)；`cand-11735` → [S. Bartolomeo all’Isola 地点](../units/places/s-bartolomeo-all-isola-exhibition-site.md)；`cand-11736` → [S. Bartolomeo all’Isola 瞻礼展系列](../units/events/s-bartolomeo-all-isola-name-day-exhibitions.md)；`cand-11741` → [圣人瞻礼日集市术语](../units/terms/casual-saints-day-fairs.md)。S3 undecided 的圣人、Guardiano、信众与未名艺术家群体仍待证；所有相关关系候选留待 S6。S4 累计登记395组/508条候选映射；待登记4,439组/4,504条；KU 总数1,414。

### S4 跨章术语及直接端点登记（2026-10-17）

`cand-0132`、`cand-0134`、`cand-0137` 作为同一跨章 S3 术语组登记为 [艺术展览](../units/terms/art-exhibitions.md)；`cand-6024` 登记为 [Corpus Domini 节期](../units/events/corpus-domini-feast.md)；`cand-9856` 登记为 [威尼斯圣马可广场](../units/places/piazza-s-marco-venice.md)。7、3、2条直接关系候选分别保留待 S6；未决艺术家群体、观众群体及圣人瞻礼日／游行类别不改裁决。S4 累计登记398组/513条候选映射；待登记4,436组/4,499条；KU 总数1,417。

### S4 archive：L. Montalto 1955 年论文登记（2026-10-17）

`cand-6355` 映射至 [《瓦尔蒙托内潘菲利宫壁画》](../units/archives/l-montalto-frescoes-palazzo-pamphilj-valmontone-1955.md)。书内书目身份及跨章注释引注可追溯；原文与引注页未独立查阅，作者身份不扩展为具名人物。6条直接 citation relation_candidate 留待 S6。S4 累计登记399组/514条候选映射；待登记4,435组/4,498条；KU 总数1,418。

### S4 institution：Albrizziana 与 Pasquali 印刷机构登记（2026-10-17）

`cand-9799` 登记为 [威尼斯阿尔布里齐印刷所](../units/institutions/albrizziana-printing-house-venice.md)；`cand-9172` 登记为 [吉安巴蒂斯塔·帕斯夸利的威尼斯印刷所](../units/institutions/pasquali-venetian-publishing-firm.md)。p.337 的 “the firm” 提及和 relation-candidate 端点已从 Albrizzi 候选更正至 Pasquali 机构候选。两组共7条关系候选留待 S6，未新增正式关系。S4 累计登记401组/516条候选映射；待登记4,433组/4,496条；KU 总数1,420。

### S3/S4 term：history painting 复用与 Blood of Christ 主题登记（2026-10-17）

`cand-6179` 从原 `new` 身份组修正为 `same`，复用[历史画（History painting）](../units/terms/history-painting.md)；历史画作为画种的书内用法没有形成独立窄义实体。`cand-5254` 映射至[基督之血图像主题](../units/terms/blood-of-christ-iconographic-theme.md)，7条直接关系候选留待 S6。历史画未新建 KU，主题卡未新增正式关系。S4 累计登记402组/517条候选映射；待登记4,431组/4,494条；KU 总数1,421。

### S3 work：Paolo Giordano II 图版17c复用（2026-10-17）

`cand-5545` 从原 `new` 身份组修正为 `same`，映射至[Paolo Giordano II 图版17c作品卡](../units/works/ottavio-leoni-paolo-giordano-orsini-duke-of-bracciano.md)。正文描述、图版目录署名及图版号支持同一作品判断；未重复建卡。S4 登记402组/517条候选映射；待登记4,430组/4,493条；KU 总数1,421。

### S4 event：莫利诺斯争议登记（2026-10-17）

`cand-5253` 映射至[莫利诺斯与罗马教会、耶稣会的争议](../units/events/molinos-controversy-jesuits-roman-church.md)。时间范围按 Haskell 的“1664年抵达后不久”及“1670年代”表述保留，未补确切起讫日期。7条直接关系候选留待 S6，未新增正式关系。S4 累计登记403组/518条候选映射；待登记4,429组/4,492条；KU 总数1,422。

### S3 work：Choice of Hercules 图版32b复用（2026-10-17）

`cand-7245` 从原 `new` 身份组修正为 `same`，映射至[Paolo de Matteis《The Choice of Hercules》图版32b作品卡](../units/works/paolo-de-matteis-the-choice-of-hercules.md)。第7章正文与图版目录的题名及图版号对应；不重复建卡。5条候选关系留待 S6。S4 登记403组/518条候选映射；待登记4,428组/4,491条；KU 总数1,422。

### S4 event：Romanelli 1638 年获任圣路加学院 Principe

`cand-2209` 映射至[乔万尼·弗朗切斯科·罗马内利获任圣路加学院 Principe（1638）](../units/events/romanelli-appointment-principe-accademia-di-san-luca-1638.md)。第2章 p.53 直接记载1638年任命及 Cardinal [Francesco] Barberini 的下令；原文未给任期或地点。相关人物—机构关系仍待 S6。S4 累计登记404组/519条候选映射；待登记4,427组/4,490条；KU 总数1,423。

### S4 event：1748年艾克斯-拉夏贝尔和约

`cand-0019` 映射至[艾克斯-拉夏贝尔和约（1748）](../units/events/peace-of-aix-la-chapelle-1748.md)。卡片保留 Haskell 对其作为意大利“新精神”断代起点的限定表述；不推导启蒙思想的首次出现或因果关系。S4 累计登记405组/520条候选映射；待登记4,426组/4,489条；KU 总数1,424。

### S3 机构复用修正与 S4 圣罗科跨章身份组登记（2026-10-17）

`cand-7072`（Institute of Arts, Detroit）改为 `same`，复用既有[底特律艺术学院](../units/institutions/detroit-institute-of-arts.md)。第9章注2给出同一机构的完整名称；第7章两幅 Poussin 画与两处馆藏的逐件配对仍待证。

新增登记：`cand-8587` → [圣罗科年度展览系列](../units/events/s-rocco-annual-exhibition.md)；`cand-9871` → [威尼斯总督与元老院赴圣罗科堂巡行（8月16日）](../units/events/doge-senate-procession-to-s-rocco-august-16.md)；`cand-10005` → [1770年8月16日展览（Albrizzi 记述）](../units/events/exhibition-of-16-august-1770-albrizzi-account.md)；`cand-8569` → [《守护天使》](../units/works/piazzetta-angelo-custode-altarpiece.md)；`cand-8129` → [威尼斯元老院](../units/institutions/senate-of-venice.md)；`cand-8728` → [威尼斯总督职务](../units/institutions/doge-of-venice-office.md)；`cand-9866` → [圣罗科展览报道中的画家群体](../units/terms/painters-in-s-rocco-exhibition-reports.md)；`cand-9870` → [巴黎沙龙展览（Haskell 所引比较对象）](../units/events/salon-in-paris-exhibition-series.md)；`cand-9863` → [1729年8月20日教廷使节报告（Haskell 引用）](../units/archives/papal-nuncio-report-1729-08-20.md)；`cand-9869` → [Algarotti 致 Mariette 谈圣罗科展览的书信（至迟1751年）](../units/archives/algarotti-letter-to-mariette-s-rocco-by-1751.md)；`cand-8580` → [Cochin 第三卷所记 Sagredo 宫绘画（1758）](../units/archives/cochin-volume-iii-sagredo-pictures-1758.md)；`cand-0793` → [夏尔-尼古拉·科尚](../units/persons/charles-nicolas-cochin.md)。年度展览系列、巡行和1770年场次保持分立；Nunzio 报告没有可据以关联圣罗科的场地信息。`cand-8588`、`cand-10006`、`cand-1904`、`cand-8621`、`cand-8586` 继续保留各自 S3 待证理由。相关 S2 关系候选留待 S6，本批未新增正式关系。

S4 累计登记417组/532条候选映射；待登记4,413组/4,476条；KU 总数1,436。

### S4 place／institution：圣若望斩首堂与回廊跨章端点登记（2026-10-17）

`cand-6040`、`cand-6041`、`cand-6048` 分别登记为[教堂地点](../units/places/s-giovanni-decollato-church-rome.md)、[内部回廊地点](../units/places/s-giovanni-decollato-cloisters-rome.md)和[Compagnia della Misericordia 机构](../units/institutions/compagnia-della-misericordia-s-giovanni-decollato.md)。第5章展览及空间叙述与第6章 Rosa 的场地提及支持地点跨章归组；OCR 与印刷页拼写差异保留可追溯说明。10条不同的直接关系候选待 S6；未新增正式关系。S4 登记420组/535条映射，待登记4,410组/4,473条；KU 总数1,439。

### S3–S4 跨章复核：Jacques Callot 人物组与《La Fiera dell'Impruneta》版画分型（2026-10-17）

`cand-0482`、`cand-0483` 按 C.csv#6/#7 与第4、5、8、13章的人名锚点归为同一人物组，登记为[Jacques Callot 人物卡](../units/persons/jacques-callot.md)。C.csv#7 的 Fiera 子项另指向作品；第8章 p.213 的版画名称提及现拆映至新 work 候选 `cand-12429`，与原版模具候选 `cand-7570` 分开。版画候选经 backlog `bl-0005` 完成 S1→S3→S4，登记为[《La Fiera dell'Impruneta》版画](../units/works/jacques-callot-la-fiera-dell-impruneta-print.md)。
`cand-7570` 类型仍待证；相关关系继续留待 S6。未新增正式关系或外部身份断言。
S3 new=5,009/4,831；S4 已登记422组/538条映射，待登记4,409组/4,471条；KU 总数1,441。


### S3 跨章多候选身份组：分类型核对（2026-10-17）

接续现有 alignment 记录，完成29个原跨章、多候选 `decision=new` 组的类型与身份边界核对。27组维持原组，2组拆分为四个独立身份组：Cardinal Angelo Cesi 与其兄弟 Monsignor Angelo Cesi；以及 Innocent X 索引下两个彼此不同的 term 子项。各候选的来源锚点、当前组号和变化理由见[对齐表](../tables/alignment.csv)及[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)。

| 类型 | 原跨章多候选组数 | 当前处置 |
|---|---:|---|
| archive | 3 | 3组保留 |
| institution | 1 | 1组保留 |
| person | 16 | 15组保留；1组拆分 |
| place | 307 | 132 |
| term | 4 | 3组保留；1组拆分 |
| work | 1,599 | 1,107 |
| **合计** | **29** | **27组保留；2组拆分；形成31个new组** |

术语拆分仅改 S3 identity grouping：`cand-1820` 与 `cand-1822` 共用的是人物索引主项，子项分别指向赞助保守性和经济紧缩影响，语义对象不同；两者各保留一个 new term 组。S4 已登记422组／538条映射，待登记4,411组／4,471条映射；S3 new=5,009个候选／4,833组；KU总数1,441。


### S3 复用修正与 S4 person：四个直接关系端点登记（2026-10-17）

20个单成员 `new` 候选组经同类型既有 KU 复核后改为 `same`；保留其 S3 历史理由并指向既有记录。复用分布：institution 2、person 1、place 13、term 1、work 3。四个单成员 person `new` 组另各登记一张 KU：

- `cand-2512` → [克里斯托福罗·斯托雷尔（Cristoforo Storer）](../units/persons/cristoforo-storer.md)：第8章，印刷页216；OCR L23–25；6条直接关系候选待 S6。
- `cand-0911` → [卢多维科·达维德（Ludovico David）](../units/persons/ludovico-david.md)：第8章，印刷页220；OCR L106；6条直接关系候选待 S6。
- `cand-1365` → [皮埃尔·德·拉特尔（Pierre de Lattre）](../units/persons/pierre-de-lattre.md)：第3章，印刷页74；OCR L121–122；6条直接关系候选待 S6。
- `cand-1636` → [尼科洛·梅兰科尼奇（Niccolò Melanconici）](../units/persons/niccolo-melanconici.md)：第8章，印刷页220–221；OCR L110、113；6条直接关系候选待 S6。

Luigi Pavini 已登记人物端点与 `st-chp9-p269-n05` 当前 statement 的映射已接通；该关系未提前转为正式边。以上批次不改变其他 conflict／undecided 对象。


### S3 修正与 S4 person：Luigi Adami 与肖像收藏对象分流（2026-10-17）

`cand-0014` 保留为 Luigi Adami 人物并登记为 [Luigi Adami 人物卡](../units/persons/luigi-adami.md)。索引子目 `cand-0015` 指向其肖像收藏，不是第二个人物；现列为 S3 `undecided` 类型待证项，保留为 S2 对象端点，待现有类型能否表达该集合对象获得裁决。人物的2条直接关系候选待 S6；本批未新增正式关系。


### S4 person：Clemens August、Daniele Farsetti 与 Giuseppe Valletta 登记（2026-10-17）

- `cand-0788` → [克莱门斯·奥古斯特（Clemens August, Archbishop-Elector of Cologne）](../units/persons/clemens-august-elector-cologne.md)：第10章，印刷页295–296；OCR L316、319；5条直接关系候选待 S6。
- `cand-1001` → [达尼埃莱·法尔塞蒂（Daniele Farsetti）](../units/persons/daniele-farsetti.md)：第15章，印刷页363；OCR L35；5条直接关系候选待 S6。
- `cand-2686` → [朱塞佩·瓦莱塔（Giuseppe Valletta）](../units/persons/giuseppe-valletta.md)：第8章，印刷页204；OCR L17–18、129（注3）；5条直接关系候选待 S6。

未新增正式关系或外部身份核验。


### S4 person：Livio Mehus、Giuseppe Nogari 与 Francesco Fontebasso 登记（2026-10-17）

- `cand-1632` → [利维奥·梅胡斯（Livio Mehus）](../units/persons/livio-mehus.md)：第8章，印刷页213、240；Markdown L116、351；3条直接关系候选待 S6。
- `cand-1743` → [朱塞佩·诺加里（Giuseppe Nogari）](../units/persons/giuseppe-nogari.md)：第9章印刷页200；第10章印刷页316；Markdown L204–206、116–117；3条直接关系候选待 S6。
- `cand-1047` → [弗朗切斯科·丰特巴索（Francesco Fontebasso）](../units/persons/francesco-fontebasso.md)：第9章印刷页272；第10章印刷页297；第13章印刷页339；Markdown L54–55、340–341、75–76；4条直接关系候选待 S6。

未新增正式关系或外部身份核验。


### S4 person：Paolo Renier、Henry（波特兰第一代公爵）与 Ottavio del Rosso 登记（2026-10-17）

- `cand-2133` → [保罗·雷尼耶（Paolo Renier）](../units/persons/paolo-renier.md)：第9章印刷页257；第15章印刷页371–372；Markdown L170、83、86–87；5条直接关系候选待 S6。
- `cand-1979` → [亨利，波特兰第一代公爵（Henry, first Duke of Portland）](../units/persons/henry-first-duke-portland.md)：第10章印刷页279–280；Markdown L49、52–55；5条直接关系候选待 S6。
- `cand-2286` → [奥塔维奥·德尔·罗索（Ottavio del Rosso）](../units/persons/ottavio-del-rosso.md)：第8章印刷页210–211；Markdown L82、85–87、96；4条直接关系候选待 S6。

未新增正式关系或外部身份核验。


### S4 person：Goswin Nickel、Francesco Morosini 与 Gaspare Diziani 登记（2026-10-17）

- `cand-1740` → [戈斯温·尼克尔（Goswin Nickel）](../units/persons/goswin-nickel.md)：第3章印刷页78、91；Markdown L24、160；5条直接关系候选待 S6。
- `cand-1705` → [弗朗切斯科·莫罗西尼（Francesco Morosini）](../units/persons/francesco-morosini.md)：第9章印刷页246、248–249；Markdown L21–22、41、79–80；5条直接关系候选待 S6。
- `cand-0922` → [加斯帕雷·迪齐亚尼（Gaspare Diziani）](../units/persons/gaspare-diziani.md)：第6章印刷页165；第10章印刷页278、294；Markdown L40、30–31、293；5条直接关系候选待 S6。

未新增正式关系或外部身份核验。


### S4 person：Carlo Antonio dal Pozzo、Philip IV 与 Daniele IV Dolfin 登记（2026-10-17）

- `cand-2035` → [卡洛·安东尼奥·达尔·波佐（Carlo Antonio dal Pozzo）](../units/persons/carlo-antonio-dal-pozzo.md)：第4章印刷页100、104、113；后记印刷页400；Markdown L21、63、162；后记L55；5条直接关系候选待 S6。
- `cand-1896` → [西班牙国王腓力四世（Philip IV of Spain）](../units/persons/philip-iv-spain.md)：第4章印刷页116；第7章印刷页172；Markdown L199–200、32–35；5条直接关系候选待 S6。
- `cand-0928` → [丹尼埃莱·多尔芬四世（Daniele IV Dolfin）](../units/persons/daniele-dolfin-iv.md)：第9章印刷页252；Markdown L119–122；4条直接关系候选待 S6。

未新增正式关系或外部身份核验。


### S4 person：Gabriel Naudé、Giorgio Maria Rapparini 与 Ottavio Vannini 登记（2026-10-17）

- cand-1726：[加布里埃尔·诺代（Gabriel Naudé）](../units/persons/gabriel-naude.md)；N.csv#6；4 条直接关系候选留待 S6。
- cand-2107：[乔治奥·玛丽亚·拉帕里尼（Giorgio Maria Rapparini）](../units/persons/giorgio-maria-rapparini.md)；Q-R.csv#34；4 条直接关系候选留待 S6。
- cand-2694：[奥塔维奥·万尼尼（Ottavio Vannini）](../units/persons/ottavio-vannini.md)；UVWXYZ.csv#30；4 条直接关系候选留待 S6。

Rapparini 姓名的 OCR 连写已在卡片中保留并注明索引分词依据；本批未登记正式关系或外部身份标识。


### S4 person：Giovanni Bottari、Federico Barocci 与 Giulio Romano 登记（2026-10-17）

- cand-0417：[乔瓦尼·博塔里（Giovanni Bottari）](../units/persons/giovanni-bottari.md)；B.csv#264；2 条直接关系候选留待 S6。
- cand-0247：[费德里科·巴罗奇（Federico Barocci）](../units/persons/federico-barocci.md)；B.csv#94；4 条直接关系候选留待 S6。
- cand-1194：[朱利奥·罗马诺（Giulio Romano）](../units/persons/giulio-romano.md)；G.csv#101；3 条直接关系候选留待 S6。

本批保留各来源的范围与归属限定，未登记正式关系或外部身份标识。


### S3 person：Ribera 与 Baldassare Franceschini 复用既有 KU（2026-10-17）

- cand-2140：new 改为 same，映射至 [Jusepe de Ribera](../units/persons/ribera.md)。 Saint Louis Art Museum 将 Giuseppe de Ribera 列为其异名；只用于身份比较，未补入外部传记事实。
- cand-1066：new 改为 same，映射至 [Baldassarre Franceschini](../units/persons/baldassare-franceschini.md)。 既有卡已记录本书原拼 Baldassare Franceschini 及别名 il Volterrano。
- 两项均不新增 KU；原 S3 决定与组 token 保留为可追溯历史。Ribera 外部身份记录见 alignment.csv 和过程记录。


### S3 work：索引子目与正文候选跨来源合组（2026-10-17）

- `cand-1238` 与正文候选 `cand-9154` 合入 `workgrp-d20da8ada884b0`；G.csv#148 与第10章 p.297 的作品题名和定位一致。
- `cand-1840` 与正文候选 `cand-7885` 合入 `workgrp-ec542d23614466`；题名和创作者一致，索引 p.222 与正文 p.232 的页码差异继续保留待核。
- 两组均仍待 S4 登记；合组只确定来源内作品身份，不确认作者归属之外的事实或关系。


### S4 person：三组跨章人物身份登记（2026-10-17）

- `cand-1237` / `new-person:giacomo-guarana-04ff210452` → [贾科莫·瓜拉纳（Giacomo Guarana）](../units/persons/giacomo-guarana.md)；第9、10、13、15章；索引 G.csv#147；3条直接关系候选留待S6。
- `cand-1033` / `new-person:domenico-fetti-d78526d512` → [多梅尼科·费蒂（Domenico Fetti）](../units/persons/domenico-fetti.md)；第7、9、18、19章；索引 F.csv#48；2条直接关系候选留待S6。
- `cand-1839` / `new-person:francesco-parmigianino-f05afd0c44` → [弗朗切斯科·帕尔米贾尼诺（Francesco Parmigianino）](../units/persons/francesco-parmigianino.md)；第2、4、5、8、13章；索引 P.csv#39；1条直接关系候选留待S6。

本批未登记正式关系或外部身份标识；候选卡提供指向 alignment.csv 与过程记录的内部身份入口。


### S3 person：既有人物复用与同名爵位分界（2026-10-17）

- `cand-0092`、`cand-0093` → `same`，复用 [Dirk van Ameyden](../units/persons/ameyden.md)；人物候选与《Relatione della città di Roma 1642》archive对象分开。
- `cand-2624` → `same`，复用 [Giandomenico Tiepolo](../units/persons/giandomenico-tiepolo.md)。
- `cand-1524` 维持 `new` 身份组；与已有的Ferdinando duke KU经时代和全名复核后保持分开，待S4。


### S4 person：三组跨章人物身份登记（2026-10-17）

- `cand-1524` / `new-person:carlo-ferdinando-mantua-of-66e2b330e3` → [费迪南多·卡洛·贡扎加（Ferdinando Carlo Gonzaga）](../units/persons/ferdinando-carlo-gonzaga.md)；第9、10章；索引 M.csv#61；5条直接关系候选留待S6。
- `cand-0087` / `new-person:altieri-emilio-clement-x-0c9723ef22` → [埃米利奥·阿尔蒂耶里（Emilio Altieri (Pope Clement X)）](../units/persons/emilio-altieri-pope-clement-x.md)；第4、6章；索引 A.csv#88；5条直接关系候选留待S6。
- `cand-0155` / `new-person:bacon-francis-e77bd98874` → [弗朗西斯·培根（Francis Bacon）](../units/persons/francis-bacon.md)；第4、10、15章；索引 B.csv#2；4条直接关系候选留待S6。

本批未登记正式关系或外部身份标识；候选卡提供指向 alignment.csv 与过程记录的内部身份入口。


### S3→S4 person：Giovanni Poleni 跨章身份组复核与登记（2026-10-17）

`cand-1968`（P.csv#169）与 `cand-9182`（第10章 p.301）维持同一 `new-person:giovanni-poleni-8cd50ead76`，映射至[Giovanni Poleni 人物卡](../units/persons/giovanni-poleni.md)。第15章 p.367 的 Marchese Poleni 语境与 p.301 的全名相合；索引 p.201 定位保留，但不单独作为本次身份依据。3 条直接关系候选留待 S6。


### S3→S4 person：里士满公爵身份组复核与登记（2026-10-17）

`cand-2193`、`cand-2194` 维持同一 `new-person:of-richmond-9053928efd`，映射至[里士满公爵人物卡](../units/persons/duke-of-richmond-mcswiny-british-worthies.md)。原文仅提供头衔，完整个人姓名留待核实；6条直接关系候选留待 S6。


### S3 archive→S4：Osservatore Veneto 期刊题名裁决与登记（2026-10-17）

`cand-1791`（O.csv#26）由待证改为题名层级 archive 新组，登记为[《Osservatore Veneto》期刊卡](../units/archives/osservatore-veneto-periodical.md)。正文和注释支持期刊题名及1761年2月14日的引文定位；该期未独立查阅，不另建期号对象。1条直接关系候选留待S6。


### S4 person：三组跨章人物身份登记（2026-10-17）

- `cand-1607` / `new-person:cosimo-de-iii-medici-098cd59653` → [科西莫三世·德·美第奇（Cosimo III de' Medici）](../units/persons/cosimo-iii-de-medici.md)；第8、20章；索引 M.csv#147；4条直接关系候选留待S6。
- `cand-2814` / `new-person:england-iii-of-william-d840b96e5c` → [英格兰的威廉三世（William III of England）](../units/persons/william-iii-of-england.md)；第7、10章；索引 UVWXYZ.csv#151；4条直接关系候选留待S6。
- `cand-1295` / `new-person:france-henri-iv-of-95c1a45df8` → [法兰西的亨利四世（Henri IV of France）](../units/persons/henri-iv-of-france.md)；第2、7章；索引 H.csv#11；4条直接关系候选留待S6。

本批未登记正式关系或外部身份标识；各卡提供候选、对齐行与过程记录入口。


### S3→S4 person：Aurelio 与 Carlo Rezzonico 身份分立复核与登记（2026-10-17）

- `cand-2136` / `new-person:aurelio-rezzonico-02891a7a00` → [奥雷利奥·雷佐尼科（Aurelio Rezzonico）](../units/persons/aurelio-rezzonico.md)；第9章；索引 Q-R.csv#63；4条直接关系候选留待S6。
- `cand-2137` / `new-person:carlo-rezzonico-clement-xiii-5d6bd47b3c` → [卡洛·雷佐尼科（Carlo Rezzonico (Pope Clement XIII)）](../units/persons/carlo-rezzonico-pope-clement-xiii.md)；第9、15章；索引 Q-R.csv#64 / 原索引转录；4条直接关系候选留待S6。

两人分立；本批未新增正式关系或外部身份断言。


### S3→S4 person：Mead、Maderno 与 Zanetti 跨章身份组登记（2026-10-17）

- `cand-1604` / `new-person:mead-richard-ffc4adb9cf` → [理查德·米德（Richard Mead）](../units/persons/richard-mead.md)；第4、10、14章；索引 M.csv#144；3条直接关系候选留待S6。
- `cand-1477, cand-4873` / `new-person:carlo-maderno-530c4fdfa7` → [卡洛·马代尔诺（Carlo Maderno）](../units/persons/carlo-maderno.md)；第2、3章及 Postscript；索引 M.csv#14；3条直接关系候选留待S6。
- `cand-2861, cand-9280` / `new-person:girolamo-zanetti-2aceef0ec5` → [吉罗拉莫·扎内蒂（Girolamo Zanetti）](../units/persons/girolamo-zanetti.md)；第9、10、14章；索引 UVWXYZ.csv#198；2条直接关系候选留待S6。

本批未新增正式关系或外部身份断言。


### S3→S4 person：Sebastiano Resta、Andrea Palladio 与 Horace Walpole 登记（2026-10-17）

- `cand-2134` / `new-person:resta-sebastiano-912fe4613b` → [塞巴斯蒂亚诺·雷斯塔（Sebastiano Resta）](../units/persons/sebastiano-resta.md)；第3、5、6、8章；索引 Q-R.csv#61；2条直接关系候选留待S6。
- `cand-1807` / `new-person:andrea-palladio-5e91b207a4` → [安德烈亚·帕拉迪奥（Andrea Palladio）](../units/persons/andrea-palladio.md)；第4、10、14章及 Postscript；索引 P.csv#6；2条直接关系候选留待S6。
- `cand-2798` / `new-person:horace-walpole-71c5b539dc` → [霍勒斯·沃波尔（Horace Walpole）](../units/persons/horace-walpole.md)；第9、10、14章；索引 UVWXYZ.csv#135；2条直接关系候选留待S6。

本批未新增正式关系或外部身份断言。


### S3→S4 person：Pietro della Vecchia、Fra Galgario 与 Apostolo Zeno 登记（2026-10-17）

- `cand-2707` / `new-person:della-pietro-vecchia-bd2908fb58` → [皮耶特罗·德拉·韦基亚（Pietro della Vecchia）](../units/persons/pietro-della-vecchia.md)；第7、13、16章；索引 UVWXYZ.csv#43；3条直接关系候选留待S6。
- `cand-1101` / `new-person:fra-galgario-ghislandi-vittore-8b50b26f92` → [维托雷·吉斯兰迪（Fra Galgario）（Fra Galgario (Vittore Ghislandi)）](../units/persons/fra-galgario-vittore-ghislandi.md)；第6、7章；索引 G.csv#8；2条直接关系候选留待S6。
- `cand-2869` / `new-person:apostolo-zeno-9866a1a3e7` → [阿波斯托洛·泽诺（Apostolo Zeno）](../units/persons/apostolo-zeno.md)；第8、10章；索引 UVWXYZ.csv#206；2条直接关系候选留待S6。

本批未新增正式关系或外部身份断言。


### S3→S4 person：Giuseppe Mazza、Francisco Goya 与 Lorenzo Mattielli 登记（2026-10-17）

- `cand-1602` / `new-person:giuseppe-mazza-c434d5ebb3` → [朱塞佩·马扎（Giuseppe Mazza）](../units/persons/giuseppe-mazza.md)；第8、9章；索引 M.csv#141；2条直接关系候选留待S6。
- `cand-1216` / `new-person:francisco-goya-8314253007` → [弗朗西斯科·戈雅（Francisco Goya）](../units/persons/francisco-goya.md)；第7、10章；索引 G.csv#124；2条直接关系候选留待S6。
- `cand-1584` / `new-person:lorenzo-mattielli-e53f3c6116` → [洛伦佐·马泰利（Lorenzo Mattielli）](../units/persons/lorenzo-mattielli.md)；第7、14章；索引 M.csv#123；2条直接关系候选留待S6。

本批未新增正式关系或外部身份断言。


### S3→S4 person：Cigoli、Ciampelli 与 Anne, Queen of England 登记（2026-10-17）

- `cand-0756` / `new-person:cigoli-ludovico-39b93eea0c` → [卢多维科·奇戈利（Ludovico Cigoli）](../units/persons/ludovico-cigoli.md)；第2、4章；索引 C.csv#280；4条直接关系候选留待S6。
- `cand-0744` / `new-person:agostino-ciampelli-64c825d6b8` → [阿戈斯蒂诺·钱佩利（Agostino Ciampelli）](../units/persons/agostino-ciampelli.md)；第2、3章；索引 C.csv#268；3条直接关系候选留待S6。
- `cand-0110` / `new-person:anne-england-of-1cb5af41f1` → [英国女王安妮（Anne, Queen of England）](../units/persons/anne-queen-of-england.md)；第7、10章；索引 A.csv#111；3条直接关系候选留待S6。

本批未新增正式关系或外部身份断言；OCR异文依来源保留。


### S3→S4 person：James II、Bernhard Rode 与 John Milton 登记（2026-10-17）

- `cand-1317` / `new-person:england-ii-james-of-95bd33d65c` → [英格兰国王詹姆斯二世（James II of England）](../units/persons/james-ii-of-england.md)；第7、10章；索引 J，K.csv#1；3条直接关系候选留待S6。
- `cand-2207` / `new-person:bernhard-rode-f729759924` → [贝恩哈德·罗德（Bernhard Rode）](../units/persons/bernhard-rode.md)；第14、20章；索引 Q-R.csv#134；3条直接关系候选留待S6。
- `cand-1668` / `new-person:john-milton-f3686fb04d` → [约翰·弥尔顿（John Milton）](../units/persons/john-milton.md)；第2、4、10章；索引 M.csv#208；2条直接关系候选留待S6。

本批未新增正式关系或外部身份断言；OCR异文和来源归属争议均予保留。


### S3→S4 person：Bernardo de Dominici、Felicita Sartori 与 Teodoro Viero 登记（2026-10-17）

- `cand-0942, cand-7116` / `new-person:bernardo-de-dominici-cbdb693309` → [贝尔纳多·德·多米尼奇（Bernardo de Dominici）](../units/persons/bernardo-de-dominici.md)；第6–8章；第21章书目；索引 D.csv#44；3条直接关系候选留待S6。
- `cand-2363` / `new-person:felicita-sartori-b7a1b9ce62` → [费利奇塔·萨托里（Felicita Sartori）](../units/persons/felicita-sartori.md)；第10、13章；索引 S.csv#51；3条直接关系候选留待S6。
- `cand-2773` / `new-person:teodoro-viero-15b8599b5c` → [特奥多罗·维耶罗（Teodoro Viero）](../units/persons/teodoro-viero.md)；第13、15章；索引 UVWXYZ.csv#109；3条直接关系候选留待S6。

本批未新增正式关系或外部身份断言；书内作者归属和引文页阅读状态按来源边界保留。


### S4 archive：跨章书信身份登记（2026-10-17）

- `cand-9831` → [档案卡](../units/archives/zanetti-letter-to-gori-1738-08-23-marucelliana-b-viii-13.md)；身份范围及未独立查阅项见卡片。关系候选待S6。
- `cand-9832` → [档案卡](../units/archives/biffi-letter-to-signor-vacchelli-1773-cremona-aa-i-4.md)；身份范围及未独立查阅项见卡片。关系候选待S6。
- `cand-11571` → [档案卡](../units/archives/rosa-letter-to-ricciardi-1660-04-02.md)；身份范围及未独立查阅项见卡片。关系候选待S6。

3个S3 `new` 档案组各登记为1个KU；来源仅为Haskell书内著录/转引，原信、馆藏目录或被引刊本未在本批独立查阅。11条已有关系候选未转为正式关系；未映射端点仍待相应S3/S4处理后再进入S6。

S4累计登记486组/607条候选映射；待登记4,324组/4,379条；KU总数1,505。

### S3 archive：Rosa–Ruffo 1666年书信复用（2026-10-17）

`cand-3551` 已从 `new` 改判 `same`，映射至既有[书信卡](../units/archives/rosa-ruffo-letter-1666.md)。第1章 p.22 注1所载寄件人、收件人和1666年4月1日日期与卡片相合；OCR `I April` 与印本 `1 April` 为转录差异。原书3条关系候选仍保留，未新增正式关系或KU。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-existing-rosa-ruffo-letter-1666-reuse-20261017)。

### S4 person：Cornelius de Stael 身份组登记（2026-10-17）

`cand-2504`与`cand-6082`作为一个S3人物身份组映射至[人物卡](../units/persons/cornelius-de-stael.md)。人物卡仅记录Haskell对其dealer身份及1663年书信的书内描述；V. Russo身份、原信和刊本未核。3条直接关系候选仍待S6。

S4累计登记487组/609条候选映射；待登记4,322组/4,376条；KU总数1,506。

### S4 archive：de Stael–Ruffo 书信身份登记（2026-10-17）

`cand-6083`映射至[书信档案卡](../units/archives/de-stael-letter-to-ruffo-1663-06-09.md)。身份依据限于Haskell第5章 p.122 注6；原信与刊本未独立查阅。刊者`V. Russo`身份仍待决，3条关系候选留待S6。

S4累计登记488组/610条候选映射；待登记4,321组/4,375条；KU总数1,507。

### S3 archive：Negri–Marchese di S. Tommaso 1676年书信复用（2026-10-17）

`cand-3553`已从`new`改判`same`，映射至既有[书信卡](../units/archives/negri-san-tommaso-letter-1676.md)。原书注3与卡片在寄件人、收件人、1676年12月24日及Claretta刊引上相合；未新增KU或关系。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-existing-negri-san-tommaso-letter-1676-reuse-20261017)。

### S3 archive：Ruffo 通信既有身份复用（2026-10-17）

- `cand-3550` → [既有书信卡](../units/archives/novetti-ruffo-letter-1670.md)；Novetti–Ruffo 1670年书信的寄件人、收件人、精确日期与书内刊引相合。
- `cand-3552` → [既有书信卡](../units/archives/de-rosis-ruffo-letter-1663.md)；de Rosis–Ruffo 1663年9月22日书信的寄件人、收件人、精确日期与书内刊引相合。
原书4条关系候选保持待S6，未新增KU或正式关系。

### S3 archive：Bianconi 1762年书信复用（2026-10-17）

`cand-3554`已从`new`改判`same`，映射至既有[书信卡](../units/archives/bianconi-letter-1762.md)。Haskell注2与卡片在作者、1762年11月22日和Bottari卷VII第362页上相合；未新增KU。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-existing-bianconi-letter-1762-reuse-20261017)。

### S3 archive：Coke 1620年书信复用（2026-10-17）

`cand-3421`已从`new`改判`same`，映射至既有[书信卡](../units/archives/coke-arundell-letter-1620.md)。Haskell注2和相邻正文与卡片在日期、通信语境及Hervey刊引上相合；未新增KU或正式关系。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-existing-coke-arundell-letter-1620-reuse-20261017)。

### S4 archive：Rosa–Ricciardi 六封分日期书信登记（2026-10-17）

- `cand-11572` → [书信卡](../units/archives/rosa-letter-to-ricciardi-1666-10-09.md)；原题未给，工作题名为描述性暂题，原信及刊本未独立查阅。
- `cand-11573` → [书信卡](../units/archives/rosa-letter-to-ricciardi-1651-04-24.md)；原题未给，工作题名为描述性暂题，原信及刊本未独立查阅。
- `cand-11574` → [书信卡](../units/archives/rosa-letter-to-ricciardi-1651-05-12.md)；原题未给，工作题名为描述性暂题，原信及刊本未独立查阅。
- `cand-11575` → [书信卡](../units/archives/rosa-letter-to-ricciardi-1662-05-13.md)；原题未给，工作题名为描述性暂题，原信及刊本未独立查阅。
- `cand-11576` → [书信卡](../units/archives/rosa-letter-to-ricciardi-1664-05-21.md)；原题未给，工作题名为描述性暂题，原信及刊本未独立查阅。
- `cand-11954` → [书信卡](../units/archives/rosa-letter-to-ricciardi-1651-05-27.md)；原题未给，工作题名为描述性暂题，原信及刊本未独立查阅。
六个S3 `new` 组各登记为一个archive KU；日期不同，未合并为通信集。17条书内关系候选均未转为正式关系；作者、收信人和被引刊物的证据范围见卡片与`book-statements.jsonl`。

S4累计登记494组/616条候选映射；待登记4,310组/4,364条；KU总数1,513。

### place：Ferrara 跨章身份组 S4 登记（2026-10-17）

`cand-1017` → [费拉拉地点卡](../units/places/ferrara.md)。第2章与第8章均以 Ferrara 指称城市地点；7条直接S2关系候选未转为正式关系。

全书S4当前登记495组/617条映射，待登记4,309组/4,363条；KU总数1,514。

### person：Louis Richeôme 书内身份组 S4 登记（2026-10-17）

`cand-2192` → [人物卡](../units/persons/louis-richeome.md)。卡片只登记Haskell明确给出的姓名、French Jesuit身份及1611年写书这一语境，中文名注明工作音译；5条直接S2关系候选仍待S6。

全书S4当前登记496组/618条映射，待登记4,308组/4,362条；KU总数1,515。

### work：Chapel of the Visitation 祭坛画身份组 S4 登记（2026-10-17）

`cand-5039` → [作品卡](../units/works/visitation-chapel-altar-painting.md)。题名为描述性工作题名；原书未说明原题或画作题材。7条直接S2关系候选仍待S6裁决，未新增正式关系。

全书S4当前登记497组/619条映射，待登记4,307组/4,361条；KU总数1,516。

### place/term：委托祭坛画及Richeôme论述端点 S4 登记（2026-10-17）

- `cand-5038` → [知识卡](../places/chiesa-nuova-chapel-of-the-visitation.md)；身份范围、描述性译名及来源限定见卡片。
- `cand-12314` → [知识卡](../terms/richeome-fresco-subject-devotional-function.md)；身份范围、描述性译名及来源限定见卡片。
- `cand-12316` → [知识卡](../terms/richeome-ornamental-forms-and-devotion.md)；身份范围、描述性译名及来源限定见卡片。
其中1个place组和2个term组分别登记；4条直接或地点限定关系候选继续待S6，未新增正式关系。

全书S4当前登记500组/622条映射，待登记4,304组/4,358条；KU总数1,519。

### person：Prospero Pesci 跨候选身份组 S4 登记（2026-10-17）

`cand-1887`、`cand-10374`共同映射至[Prospero Pesci人物卡](../units/persons/prospero-pesci.md)。索引主项、正文全名与1759年书信收信人全名互相对应；4条直接S2关系候选仍待S6，未新增正式关系。

全书S4当前登记501组/624条映射，待登记4,303组/4,356条；KU总数1,520。


### person：Maria Labia 书内身份组 S4 登记（2026-10-17）

`cand-1350` → [人物卡](../units/persons/maria-labia.md)。卡片仅保留第9章第257页的人物名称与书内语境，将家族整体与个人区分；珠宝收藏及作者解释按来源边界陈述。4条直接S2关系候选仍待S6，未新增正式关系或外部身份断言。

全书S4当前登记502组/625条映射，待登记4,302组/4,355条；KU总数1,521。

### person：Girolamo Rainaldi 跨候选身份组 S4 登记（2026-10-17）

`cand-2093` → [人物卡](../units/persons/girolamo-rainaldi.md)。Treccani DBI的Girolamo条目与原书的Piazza Navona宫殿规划锚点相合；Carlo Rainaldi为其子，仍保留为另一个S3人物组。4条直接S2关系候选待S6，未新增正式关系。

全书S4当前登记503组/626条映射，待登记4,301组/4,354条；KU总数1,522。

### archive：Tiepolo–Algarotti书信跨章身份组 S4 登记（2026-10-17）

`cand-8379`（第9章）与`cand-10280`（第14章）共同映射至[同一书信档案卡](../units/archives/tiepolo-letter-to-algarotti-1743-10-26.md)。两处对通信双方、日期及Fogolari 1942年刊本第34页的著录相同；原信和刊本未独立查阅。3条直接关系候选继续待S6，未新增正式关系。

全书S4当前登记504组/628条映射，待登记4,300组/4,352条；KU总数1,523。

### work：Gesù圣依纳爵小堂大祭坛方案 S4 登记（2026-10-17）

`cand-5420` → [作品卡](../units/works/gesu-st-ignatius-great-altar-project.md)。采用描述性暂题；本章记录方案、竞赛和祭坛内部细节，未据此补写完工或存世状态。7条直接关系候选继续待S6，未新增正式关系。

全书S4当前登记505组/629条映射，待登记4,299组/4,351条；KU总数1,524。

### work：Gesù后殿《羔羊崇拜》壁画 S4 登记（2026-10-17）

`cand-5287` → [作品卡](../units/works/gaulli-gesu-apse-adoration-of-the-lamb-fresco.md)。题名为描述性暂题；后殿壁画、旧马赛克和图像题材分别保留。7条直接关系候选仍待S6，未新增正式关系。

全书S4当前登记506组/630条映射，待登记4,298组/4,350条；KU总数1,525。

### person：Cesare Beccaria 跨章身份组 S4 登记（2026-10-17）

`cand-0265`、`cand-0266`共同映射至[人物卡](../units/persons/cesare-beccaria.md)。第10、13、15章的书内提及与索引全名相合；Treccani DBI记录核对已写入alignment。Treatise `Dei delitti e delle pene`保持独立archive候选；3条直接关系候选待S6。

全书S4当前登记507组/632条映射，待登记4,297组/4,348条；KU总数1,526。

### archive：Beccaria 论著文本身份组登记（2026-10-17）

`cand-9707`登记至[文献卡](../units/archives/dei-delitti-e-delle-pene-treatise.md)。第10、13、15章的题名提及合为一个文本层级archive KU；第15章Querini作者说保留为明确传闻。3条直接关系候选待S6。

S4当前登记508组/633条映射，待登记4,296组/4,347条。


### person：Christian Cole关系端点 S4 登记（2026-10-17）

`cand-0801`登记至[人物卡](../units/persons/christian-cole.md)；全名由第10章正文与索引相合。4条关系候选待S6；Lord Dartmouth端点`cand-0904`仍为S3 undecided。

S4当前登记509组/634条映射，待登记4,295组/4,346条。


### place：Villa Cordellina at Montecchio 跨章身份组 S4 登记（2026-10-17）

`cand-8376`（第9章p.256，源行L160）与`cand-10279`（第14章p.352）映射至[地点卡](../units/places/villa-cordellina-montecchio.md)。修正此前把L160误写成印刷页p.160的定位；Vicenza住宅保持独立。2条关系候选待S6。

S4当前登记510组/636条映射，待登记4,294组/4,344条。


### person：Domenico Passignani直接关系端点 S4 登记（2026-10-17）

`cand-1857`登记至[人物卡](../units/persons/domenico-passignani.md)。索引全名与第2章p.26正文锚点相合；4条关系候选留待S6。杯形穹顶地点候选待S4，壁画作品端点仍S3 undecided。

S4当前登记511组/637条映射，待登记4,293组/4,343条。


### place：Barberini Chapel cupola直接端点 S4 登记（2026-10-17）

`cand-4258`登记至[地点卡](../units/places/barberini-chapel-cupola-s-andrea-della-valle.md)，与完整礼拜堂及作品分开。第3章p.77比较支持同一地点指称，但比较对象保持独立；2条关系候选待S6。

S4当前登记512组/638条映射，待登记4,292组/4,342条。


### person：Giambettino Cignaroli跨索引组 S4 登记（2026-10-17）

`cand-0754`与`cand-0755`共同映射至[人物卡](../units/persons/giambettino-cignaroli.md)。同全名索引主项与`work for Labia`子项对应一个人；3条人物关系候选待S6，p.271集合式Oratorian陈述未拆为个人边。

S4当前登记513组/640条映射，待登记4,291组/4,340条。

### work：McSwiny 德文郡公爵纪念画 S3/S4 裁决与登记（2026-10-17）

`cand-9016` 判为 `workgrp-812459889b2b31` 的单件新作品组并登记至[作品卡](../units/works/mcswiny-duke-of-devonshire-monument.md)。p.289正文和注1表为身份依据；描述性题名、作品版本及原书表格的 Barber Institute 标记均按来源范围限定。`cand-9020` 的Bingley改绘版本仍为 `undecided`，未合并；7条直接S2关系候选留待S6，未新增正式关系。没有进行外部身份或现藏核验。

全书S4当前登记514组/641条映射，待登记4,290组/4,339条；KU总数1,533。

### archive：Brugnoli 第二篇论文跨章身份组 S3/S4 登记（2026-10-17）

`cand-4329`（第2章注5）与`cand-11270`（第21章书目）作为同一篇 Brugnoli 论文跨章映射至[文献卡](../units/archives/brugnoli-albani-domenichino-frescoes-bassano-sutri-1957.md)。书目中的另一篇 Brugnoli 论文题名不同，仍为独立对象；两篇文章未被独立查阅。`cand-4327`作者人物身份保留 `undecided`；1条书内引文关系候选留待S6，没有新增正式关系。

全书S4当前登记515组/643条映射，待登记4,289组/4,337条；KU总数1,534。

### institution：Dresden Gallery 跨章裁决与S4登记（2026-10-17）

`cand-9091` 依据第10章 p.294 与第14章 p.350 映射至[德累斯顿绘画馆卡](../units/institutions/dresden-gallery.md)；3条直接关系候选留待S6。`cand-10222` 改列 `undecided`：同一候选还映射到第14章 p.355 的“royal collection”，当前粒度不能安全地只对齐画廊机构；未分配KU，待拆清提及范围。不把个人收藏、具体画作或实体建筑并入绘画馆。

全书S4当前登记516组/644条映射，待登记4,288组/4,335条；KU总数1,535。

### S3 work：Crespi 两件同名《The Finding of Moses》作品分组更正（2026-10-17）

cand-0879 改为 same，映射至既有 Jupiter/Cybele 作品卡；cand-7720 保持 new，另成组 workgrp-ruffo-crespi-finding-of-moses-p222。原并组只凭同名题名，忽略了 p.222 Ruffo 委托与 p.228/p.405 Conti Jupiter/Cybele 委托及避税改题的差别；现依据完整书内语境拆分。S3 当前候选去向均有决定记录；本次新增候选仍待 S4 登记。S6关系候选不在本次转正。

当前 same=1,849，new=4,978（4,804组），conflict=8，undecided=5,472；S4已登记516组/644条，待登记4,288组/4,334条；KU总数1,535。

### S4 work：Crespi《The Finding of Moses》（Ruffo 委托语境）登记（2026-10-17）

`cand-7720`（`workgrp-ruffo-crespi-finding-of-moses-p222`）登记为[作品卡](../units/works/giuseppe-maria-crespi-finding-of-moses-ruffo-commission.md)。它与已复用至既有 Conti Jupiter/Cybele 作品卡的 `cand-0879` 分属两件作品，仅共用《The Finding of Moses》题名。卡片保存 p.222 委托语境及 p.228/p.405 的身份区分；一条直接 S2 关系候选仍待 S6，未新增正式关系。

S4当前登记517组/645条候选映射；待登记4,287组/4,333条；KU总数1,536。

### S3→S4 term：German patronage 跨章身份组裁决与登记（2026-10-17）

`cand-1145` 与 `cand-1146` 保留为同一 `new` 术语组并映射至[术语卡](../units/terms/german-patronage-of-italian-art.md)。第7章的17世纪后期意大利多地语境与第10章的18世纪德国宫廷、威尼斯艺术语境分别记录，不推断连续统一制度。四条直接关系候选留待S6；未新增正式关系。

S4当前登记518组/647条候选映射；待登记4,286组/4,331条；KU总数1,537。

### S3→S4 place：Farsetti 在 S. Maria di Sala 的乡间别墅身份组裁决与登记（2026-10-17）

`cand-1007`（索引子目）与`cand-10432`（正文候选）依据第15章 p.362 对同一 S. Maria di Sala 乡间别墅的明确对应，共同映射至[地点卡](../units/places/filippo-farsetti-country-house-s-maria-di-sala.md)。Rialto 家族宫邸与未实现的帕多瓦计划保持区分；9条直接关系候选留待S6。

S4当前登记519组/649条候选映射；待登记4,285组/4,329条；KU总数1,538。

### S3→S4 term：bambocciate 小幅日常生活画作身份裁决与登记（2026-10-17）

`cand-6099`与`Bamboccianti`画家群体保持对象区分，登记至[术语卡](../units/terms/bambocciate-small-pictures-everyday-life.md)。第5章释义及第5、6章用例支持其作为小幅日常生活画作类别的书内用法；8条直接关系候选待S6。

S4当前登记520组/650条候选映射；待登记4,284组/4,328条；KU总数1,539。

### S3→S4 term：塞尔奎齐赞助人的西班牙势力圈语境裁决与登记（2026-10-17）

`cand-6148`以作者定义的概念类别保留为 `new` 并登记至[术语卡](../units/terms/cerquozzi-patrons-spanish-sphere-context.md)。保留“几乎所有”和“多数”的范围限定；不把相关家庭写成正式组织或穷尽成员清单。11条直接关系候选待S6。

S4当前登记521组/651条候选映射；待登记4,283组/4,327条；KU总数1,540。

### S3→S4 person：Giuliano Finelli 跨章身份组裁决与登记（2026-10-17）

`cand-1038`依据索引全名、p.171正文及p.172跨页续句、第190页正文中的全名与相合语境，登记为[人物卡](../units/persons/giuliano-finelli.md)。4条直接关系候选待S6；不补充外部生平或出生地。

S4当前登记525组/656条候选映射；待登记4,279组/4,322条；KU总数1,544。

### S3→S4 person：Francesco Cozza 人物身份组登记（2026-10-17）

`cand-0867` C.csv#400 的全名索引项与第5章 p.131 正文全名指向同一人物；Treccani DBI（Ludovica Trezzani，vol. 30，1984）以同名收录卡拉布里亚画家 Francesco Cozza，并记其师从 Domenichino。身份比对与本书的人名、同乡和师承语境相合；外部记录仅作身份佐证，未把生平事实导入[人物卡](../units/persons/francesco-cozza.md)。候选保留 `new` 并映射至该卡。

4条直接 S2 关系候选仍待 S6；祭司群体 `cand-6068` 未分类、祭坛画 `cand-6069` 未消歧、Sassoferrato `cand-2369` 现复用既有人物 KU，Domenichino `cand-0932` 已复用既有 KU。没有新增正式关系。

S4 当前登记 523 组／653 条候选映射；待登记 4,281 组／4,325 条映射；KU 总数 1,542。

### S3 person：Sassoferrato 主项与 style 子项复用既有人物（2026-10-17）

`cand-2369`（S.csv#57，pp.130–131）与 `cand-2372`（S.csv#60，style 子项）均在同一人物主项“Giovan Battista Salvi／Sassoferrato”下，现改为 same → [Sassoferrato 人物卡](../units/persons/sassoferrato.md)，并并入 `sg3-ku-units-persons-sassoferrato`。Treccani DBI（Silvia Blasio，vol. 90，2017）条目标题直接列为“Salvi, Giovanni Battista, detto il Sassoferrato”，与索引及既有人物卡的全名、惯用名相合。cand-2372 的 style 是人物主项的主题定位，不另建人物或术语 KU；其无 S2 独立提及的限制保留，未据此抽取风格事实。原 undecided 理由保存在 alignment 行的 prior_resolution_note 中。

本次只解决人物身份；相关 S2 关系候选仍待 S6。作品候选 cand-2373、cand-2374 未并入人物 KU，也未在本次重判。

S3 现行决定计数更新为 same=1,851（指向1,031个既有 KU）、undecided=5,470；S4 登记进度不变。

### S3→S4 person：Don Mario Chigi 直接关系端点身份组登记（2026-10-17）

cand-0674（C.csv#198，p.154）登记为[马里奥·基吉人物卡](../units/persons/mario-chigi.md)。Treccani DBI 第88卷 Rosa 传记记述同一《Fortune》画作争议、Mario Chigi 的教皇亲属身份及其为 Rosa 辩护，支持与本书 p.154 的人物相同；外部来源只作身份比对。

4条直接 S2 关系候选留待 S6；作者关于 double irony 的修辞解释不转为关系。本卡未新增正式边。

S4 当前登记 524 组／654 条候选映射；待登记 4,280 组／4,324 条映射；KU 总数 1,543。

### S3→S4 person：Felice Torelli 跨章身份组登记（2026-10-17）

`cand-2645`、`cand-2646` 共映射至[Felice Torelli 人物卡](../units/persons/felice-torelli.md)。第8章 pp.203、227 与第19章附录 p.389 给出全名；第14章 p.348 的姓氏提及列于同一索引主项下。未与 Giuseppe 或 Giacomo Torelli 合并。

4条直接关系候选留待 S6。未具名 Belloni 藏画组与 Torelli 提案作品仍 `undecided`；不把 Conti 接受此类方案或后来送达的画解释为同一件作品。本卡没有新增正式关系或外部身份记录。

S4 当前登记 525 组／656 条候选映射；待登记 4,279 组／4,322 条映射；KU 总数 1,544。

### S4 字段表写回：Felice Torelli 人物卡（2026-10-17）

姓名表与本章内容表共7行已登记至 [既有字段表](../tables/enrichment.jsonl)，卡片结构与可重建字段行一致。严格阶段审计通过（`errors=[]`、`s2_missing=[]`），卡片预检通过（1,544 cards、2,706 tables、10,516 rows）；未写入渲染卡片文件。关系候选仍待 S6，正式关系数未变。

### S3→S4 person：Alexander the Great 跨章身份组登记（2026-10-17）

cand-3442 与 cand-9593 同属一个跨章人物身份组，已映射至[亚历山大大帝人物卡](../units/persons/alexander-the-great.md)。身份依据为第1章 p.10、第8章 p.228、第10章 pp.282、313 的书内全名；没有新增外部生平或身份标识。

Ricci 未实施的方案、Pittoni 系列题材及 Rapparini 的比较叙述所涉三条直接 S2 关系候选留待 S6；第1章的一般性例子不建边。本次未新增正式关系。

S4 当前登记 526 组／658 条候选映射；待登记 4,278 组／4,320 条映射；KU 总数 1,545。

### S3→S4 person：Enriqueta Harris 跨章身份组登记（2026-10-17）

cand-1292 与 cand-11166 共映射至[恩里克塔·哈里斯人物卡](../units/persons/enriqueta-harris.md)。索引主项及第4、7、20、21章的全名／短引／书目线索支持这一书内身份组；不补写外部生平或把引文关系提前正式化。

四条引用与致谢关系候选留待 S6；本次未新增正式关系。被引文章和致谢所涉信息未独立核验。

S4 当前登记 527 组／660 条候选映射；待登记 4,277 组／4,318 条映射；KU 总数 1,546。

### S3→S4 archive：Harris 引文与合著书目身份组登记（2026-10-17）

四个互不合并的 archive 组已分别登记：cand-7118 → [委拉斯开兹的意大利之行（Velazquez’s Mission in Italy）](../units/archives/harris-velazquez-mission-italy-1960.md)；cand-7119 → [安杰洛·米凯莱·科隆纳与葡萄牙人圣安东尼堂装饰（Angelo Michele Colonna and the Decoration of San Antonio of the Portuguese）](../units/archives/harris-colonna-decoration-san-antonio-portugueses.md)；cand-7127 → [卡皮奥侯爵与委拉斯开兹绘画（The Marquis of Carpio and His Paintings by Velázquez）](../units/archives/harris-marques-del-carpio-velazquez-1957.md)；cand-11165 → [卡西亚诺·达尔·波佐的埃斯科里亚尔记述（1626）（Description of El Escorial by Cassiano dal Pozzo (1626)）](../units/archives/harris-andres-descripcion-escorial-1972.md)。依据限于第7章 p.190 注释、第20章 p.401 短引及第21章 pp.424–425 书目；文章均未独立查阅。1961 年只由第7章注1给出；1972 年责任者署名按书目记录，de Andrés 人物候选 cand-11167 仍 undecided。

三条直接 S2 书目引用候选留待 S6；1972 年短引及书目记录不标为 relation_candidate。本次未新增正式关系。

S4 当前登记 531 组／664 条候选映射；待登记 4,273 组／4,314 条映射；KU 总数 1,550。

### S3→S4 person：Giovanni Ricci（2026-10-17）

`cand-2147`、`cand-2148` → [乔瓦尼·里奇（Giovanni Ricci）](../units/persons/giovanni-ricci.md)。父级索引定位项与“patronage of Crespi”子目由第8章 pp.204、238 的同名正文归为一组；索引候选 cand-2147 的旧未决理由已在过程记录中说明并保留。7条关系候选留待 S6；评价性陈述不转成关系，本次未新增正式边。S4 当前登记532组/666条候选映射，待登记4,272组/4,313条；KU 总数1,551。

### S3→S4 person：Pietro Francavilla（2026-10-17）

`cand-1064`→[彼得罗·弗朗卡维拉人物卡](../units/persons/pietro-francavilla.md)。索引 pp.174、178 与正文 p.174 全名、p.178 雕塑语境支持同一书内人物。4条直接关系候选留待 S6；本次未新增正式关系。S4 当前登记533组/667条映射，待登记4,271组/4,312条；KU 总数1,552。

### S3→S4 person：Pietro Foscarini（2026-10-17）

`cand-1056`→[皮埃特罗·福斯卡里尼人物卡](../units/persons/pietro-foscarini.md)。索引 p.259、p.273 n.2 与两页重复全名及同一遗嘱手稿定位相合；1745年死亡仍带原书问号。4条直接关系候选留待 S6；本次未新增正式关系。S4 当前登记534组/668条映射，待登记4,270组/4,311条；KU 总数1,553。

### S3→S4 person：Nicola del Rosso（2026-10-17）

`cand-2285`、`cand-7611`→[Nicola del Rosso 人物卡](../units/persons/nicola-del-rosso.md)。p.211 的第四兄弟与 p.212 n.5 的全名、亲属限定相合。3条直接关系候选留待 S6；去世年份陈述不作为关系。S4 当前登记535组/670条映射，待登记4,269组/4,309条；KU 总数1,554。

### S3→S4 person：Nicolas Fouquet（2026-10-17）

`cand-1062`→[尼古拉·富凯人物卡](../units/persons/nicolas-fouquet.md)。全名由索引 p.186 对应正文连续段落中的姓氏 Fouquet。4条直接关系候选留待 S6；本次未新增正式关系。S4 当前登记536组/671条映射，待登记4,268组/4,308条；KU 总数1,555。

### S3→S4 person：Camillo Astalli（2026-10-17）

`cand-0144`→[卡米洛·阿斯塔利人物卡](../units/persons/camillo-astalli.md)。以第6章 p.148 原文和索引定位登记 source-local 身份；3条直接关系候选留待 S6，未新增正式关系。S4 当前登记537组/672条映射，待登记4,267组/4,307条；KU 总数1,556。

#### 本组登记后核验

严格阶段审计：KU=1,556、alignment=12,642、待登记 `decision=new` 行=4,322（4,307条候选映射、4,267组及15条外部身份记录）、enrichment=10,538、`s2_missing=[]`、`errors=[]`。保留两条既有 enrichment source_ref 警告及 S2 语义质量提示。新增两条名称字段记录后，`build_field_facts.py` 预览为 `new_ids=0`、`warnings=0`；卡片全库预检通过（1,556 cards、2,711 tables、10,538 rows），Camillo 单卡 preview 无差异，`git diff --check` 退出码0（仅有 LF→CRLF 提示）。本组未修改 `relations.csv`；正式关系仍为1,225条，另有2条既有 pending。

### S3→S4 person：Grey Brydges, 5th Lord Chandos（2026-10-17）

`cand-0644`（Chandos 主项）与 `cand-0645`（*Discourse of Rome* 子项）共用一张人物 KU。p.63 正文全名和同页索引定位支持书内身份；正文与注2分别列 *Discourse of Rome* 与 *Horae Subsecivae*，两题名关系及脚注归属继续待证。3条直接关系候选留待 S6，未新增正式关系。S4 当前登记538组/674条映射，待登记4,266组/4,305条；KU 总数1,557。

#### 本组登记后核验

严格阶段审计：KU=1,557、alignment=12,642、待登记 `decision=new` 行=4,320（4,305条候选映射、4,266组及15条外部身份记录）、enrichment=10,540、`s2_missing=[]`、`errors=[]`。保留两条既有 enrichment source_ref 警告及 S2 语义质量提示。两条姓名字段写回后，`build_field_facts.py` 预览为 `new_ids=0`、`warnings=0`；卡片全库预检通过（1,557 cards、2,712 tables、10,540 rows），Grey Brydges 单卡 preview 无差异，未渲染写卡。`relations.csv` 未因本组登记增加关系；原有关系计数不变。

### S3 person：Emilio Altieri 索引子项复用既有人物（2026-10-17）

`cand-0088`（A.csv#89，子目 “financial difficulties”，定位 p.162）原因未映射 S2 正文提及而列为 `undecided`。复核第6章 p.162 原文开头明确写 “Clement X had good reason to try to economise”；同页提及 `m-chp6-p162-v-007`（“Clement X”，字符224–233）此前已随主项 `cand-0087` 登记。主项索引 A.csv#88 与子项 A.csv#89 具有同一全名 “Altieri, Emilio (Pope Clement X)”，而 p.162 子项内容与正文锚点一致，支持同一人物。

现将 `cand-0088` 改为 `same` → `units/persons/emilio-altieri-pope-clement-x`，与已登记人物 KU 对齐；保留旧待证理由及其解决依据。未改写 S2 mentions，不新增外部身份断言或关系。

### S3 person：Grey Brydges 人物索引子项映射至既有人物（2026-10-17）

`cand-0646`（C.csv#170，索引子目 *Horae Subsecivae*，p.63）原因缺少映射到该候选的正文提及而列为 `undecided`。第3章 p.63 原文以全名 “Grey Brydges, 5th Lord Chandos” 引出 *Discourse of Rome*；同页既有提及 `m-chp3-seci-l3-14-0011` 已映射至 `cand-0644`，其人物组已登记为 `units/persons/grey-brydges-fifth-lord-chandos`。C.csv#170 的子目仍在同一全名人物标题下，故裁决的是索引所指人物身份。

现将 `cand-0646` 改为 `same` → `units/persons/grey-brydges-fifth-lord-chandos`。原待证理由保留于对齐行和本记录。此项不证明 Grey 对 *Horae Subsecivae* 的作者身份，也不解决其脚注归属或题名关联；没有新增关系。

### S3 person：Augustus III 的 Rosalba 子项复用人物 KU（2026-10-17）

`cand-0150`（A.csv#151，子目 “and Rosalba Carriera”，p.295）因没有直接映射的 S2 提及而列为 `undecided`。第10章 p.294 明确说 Augustus the Strong 之子 “Augustus III”；其后 p.295 连续叙述该 Augustus 与 Rosalba Carriera 相识、并持续收购其粉彩作品。候选 `cand-0148` 已将 p.294 “his son” 的 S2 提及映射到同一全名人物组，并已登记为 `units/persons/augustus-iii-of-poland`。索引全名、相邻正文指代链与 p.295 子目共同支持复用该人物。

现将 `cand-0150` 改为 `same` → `units/persons/augustus-iii-of-poland`。旧待证理由保留；未新增 S2 提及，也未把该子目转为 Rosalba 的人物关系或作品事实。

### S3 person：Paolo Giordano II Orsini 十条索引子项复用既有人物（2026-10-17）

复核 `cand-0429`（p.97 “and Claude”）、`cand-0430`（p.97 “and van den Hecke”）、`cand-0431`（p.97 “and Pietro Tacca”）、`cand-0432`（p.97 “and Podestà”）、`cand-0433`（pp.96–97 “Bernini head, medal, and bust”）、`cand-0435`（pp.97–98 “correspondence with Queen Christina of Sweden”）、`cand-0436`（p.96 “Leoni etching”）、`cand-0437`（pp.95–97 “love of music and spectacle”）、`cand-0438`（p.97 “medal collecting”）和 `cand-0439`（p.96 “poetry”）。这些均为人物类型候选，索引使用完全相同的全名标题 `Bracciano, Paolo Giordona II Orsini, Duke of`；各页范围与第4章已具名人物正文重叠。`cand-0428` 的正文提及 `m-chp4-sec-i-0171` 将 Paolo Giordano II Orsini 锚定于该段，`m-chp4-sec-i-0181` 在同一上下文给出 Duke of Bracciano；`cand-0428` 与附录候选 `cand-0434` 已共同登记到 `units/persons/paolo-giordano-ii-orsini`。 索引 B.csv#277–288 将名字写作 “Giordona”；书内正文和附录作 “Giordano”。此处记录为索引拼写异文，结合全名、爵号、代际和对应页锚点后用于身份映射，不把它扩展成第二个人物。

十条候选现均由 `undecided` 改为 `same`，指向该既有人物 KU。各条旧待证理由保存在对齐行中，并记录本次解决依据。索引子目仅参与人物身份归属，不据此补写与 Claude、van den Hecke、Tacca、Podestà、Bernini、Queen Christina 或 Leoni 的关系，也不把 Etching、胸像、奖章或诗歌作为新作品事实；没有新增关系或 S2 提及。

### S3 person：Francesco Borromini 三条人物索引子项复用（2026-10-17）

`cand-0405`（pp.75–76 “and Oratorians”）、`cand-0408`（p.75 “work on the Oratorio”）和 `cand-0409`（p.75 “work on Spada palace”）均为 person 类型，候选全名与主项 Francesco Borromini 相同。第3章 p.75 正文写明 Oratorians 委托 Borromini 建造 Chiesa Nuova 旁的 Oratorio，并在同页继续以 Borromini 记述 Oratorio 与 Spada 宫的工作；对应提及 `m-chp3-secii-l125-135-0027` 已归入 `cand-0404`，该组已登记为 `units/persons/francesco-borromini`。

三条候选从 `undecided` 改为 `same` 并复用该 KU，原待证理由及本次证据保留。此身份映射不把索引子目升级为正式关系；本次未新增关系或作品 KU。

### S3 person：Filippo Farsetti 四条索引子项复用（2026-10-17）

`cand-1003`（p.363 “and Canova”）、`cand-1004`（p.362 “and Carlo Lodoli”）、`cand-1009`（p.363 “interest in contemporary arts”）和 `cand-1011`（p.363 “promotion of Venetian neo-classicism”）均为 person 类型、全名与 Farsetti 主项 `cand-1002` 一致。第15章 p.362 明确以 “Filippo Farsetti” 开篇介绍该人物；p.363 延续同一叙述并继续具名 “Farsetti”。相应正文提及 `m-chp15-p362-0001`、`m-chp15-p363-0033` 已归入主项候选；该人物组已登记为 `units/persons/filippo-farsetti`。

四条索引子项现由 `undecided` 改为 `same`，复用既有人物 KU。旧待证理由及解决依据逐行保留。索引子目中的 Canova、Lodoli 及艺术活动措辞只作身份定位，本次不建立人物关系或新增作品事实。

### S3 person：Niccolò Cassana 六条作品子目复用人物（2026-10-17）

`cand-0595`（p.234 *Bacchanal*）、`cand-0596`（p.234 *Conspiracy of Catiline*）、`cand-0597`（p.234 “paintings for Grand Prince Ferdinand”）、`cand-0598`（pp.234、240 *Portrait of a Cook*）、`cand-0599`（p.241 *Portrait of a Hunter*）和 `cand-0600`（p.234 *Venus playing with Cupid*）均为 person 类型、同属 Cassana 全名词头。第8章 p.234 的 `m-chp8-p234-cassana-name` 明确记录 Niccolo Cassana，随即叙述其为 Grand Prince Ferdinand 创作的历史画与肖像，并列举上述题材；p.241 又称 “his Cassana Portrait of a Hunter”。同名人物组 `cand-0593`、`cand-0594` 已登记为 `units/persons/niccolo-cassana`。

六条候选由 `undecided` 改为 `same`，复用该人物 KU。旧待证理由保留于对齐行。子目只定位到人物名下的作品／创作语境，不在 S3 确认单件作品身份、具体归属或人物关系；本次不新增作品卡、关系或 S2 提及。

### S3 person：Federico Barocci 的《Presentation》索引子项复用（2026-10-17）

`cand-0248`（B.csv#95，p.69，子目 *Presentation of Jesus in the Temple*）为 person 类型、正文提及未直接映射到该索引子项而列为 `undecided`。第3章 p.69 正文先以全名 “Federico Barocci” 引出委托，再以 “the same artist” 指回 Barocci 并叙述《Presentation of Jesus in the Temple》的委托；提及 `m-chp3-secii-l40-52-0032` 与 `m-chp3-secii-l40-52-0040` 已归入主项 `cand-0247`，其人物组已登记为 `units/persons/federico-barocci`。

现将 `cand-0248` 改为 `same` 并复用该人物 KU。原待证理由保留。此项不新建作品 KU，也不将索引子目直接升级为正式关系。

### S3→S4 person：Ottaviano Prati（2026-10-17）

`cand-6090` 由单成员 new-person 组登记为一张人物卡，依据为第5章 p.131 注3的全名锚点。签名肖像及两处总督任职仍各自保留为 S2 关系候选，未新增正式关系；Ottaviano Ottoviani 保持分立。S4 当前登记539组/675条映射，待登记4,265组/4,304条；KU 总数1,558。

### S4 work/place：Prati 肖像与任职地点（2026-10-17）

三个直接关系端点组已登记为一张作品卡与两张地点卡；S2 关系候选仍待 S6，`relations.csv` 未修改。S4 当前登记542组/678条映射，待登记4,262组/4,301条；KU 总数1,561。

### S4 person：Saverio Bettinelli 跨章身份组（2026-10-17）

两个索引候选合并映射到一张人物卡；两条第13章书内关系候选仍待 S6。S4 当前登记543组/680条映射，待登记4,261组/4,299条；KU 总数1,562。

### S4 person：Giovanni Adamo（2026-10-17）

单成员人物组已登记；未具名作品及委托关系保持待 S6 裁决。S4 当前登记544组/681条映射，待登记4,260组/4,298条；KU 总数1,563。

### S4 person：James Adam（2026-10-17）

索引 p.302、310、392 的单人组已登记；评论关系候选仍待 S6。S4 当前登记545组/682条映射，待登记4,259组/4,297条；KU 总数1,564。

### S4 person：Sir John Vanbrugh（2026-10-17）

单成员索引人物组登记为来源内人物 KU；3条关系候选及相邻住宅／地点映射仍待后续裁决。S4 当前登记546组/683条映射，待登记4,258组/4,296条；KU 总数1,565。

### S4 archive：E. Lavagnino 第III卷（2026-10-17）

第7章脚注与第21章书目候选按同一跨章 S3 组映射至一张 archive KU；被引原书未读，其他未标卷次引注继续待核。S4 当前登记547组/685条映射，待登记4,257组/4,294条；KU 总数1,566。

### S4 place：Cordellina 维琴察住宅（2026-10-17）

第9章住宅候选与后记宫殿候选按既有跨章 S3 组映射到一张地点 KU；正式题名、地址和现存状态未由原书提供。S4 当前登记548组/687条映射，待登记4,256组/4,292条；KU 总数1,567。

### S4 term：艺术委托合同（2026-10-17）

将 S3 组中四条 new 候选映射至一张 term KU；同组索引子目 cand-0838 因缺少关联 S2 指涉仍为 undecided，未映射。S4 当前登记549组/691条映射，待登记4,255组/4,288条；KU 总数1,568。

### S4 work：Zompini《Le Arti》作品组（2026-10-17）

跨章索引与正文候选映射至一张 work KU；1753年作图稿和后来计划推出版本分别按原文限定记录，关系候选留待 S6。S4 当前登记550组/693条映射，待登记4,254组/4,286条；KU 总数1,569。

### S4 work：Zanetti《Varie Pitture a Fresco》（2026-10-17）

跨章索引与正文候选映射至一张 work KU；出版物未独立查读，作者人物候选 cand-2854 仍未决，关系保持待证。S4 当前登记551组/695条映射，待登记4,253组/4,284条；KU 总数1,570。

### S4 archive：Luzio 贡扎加画廊书目组（2026-10-17）

单成员 S3 文献候选登记为 archive KU；仅保存 Haskell 书目记录及引用页码，原书内容未独立查读，五条引用关系留待 S6。S4 当前登记552组/696条映射，待登记4,252组/4,283条；KU 总数1,571。

### S4 person：Longhi the Younger 与 Paolo Maccarani（2026-10-17）

两个独立 S3 人物组按索引及第7章 p.183 登记为 source-backed 人物 KU；身份仅限书内，不新增正式关系。S4 当前登记554组/698条映射，待登记4,250组/4,281条；KU 总数1,573。

### S4 place：Piazza di Trevi（2026-10-17）

单成员书内地点候选登记为 place KU；与教堂立面 work 的空间关系保持待 S6。S4 当前登记555组/699条映射，待登记4,249组/4,280条；KU 总数1,574。

### S4 place：SS. Vincenzo ed Anastasio 教堂（2026-10-17）

索引子目及第7章叙述支持一张建筑 place KU；教堂、广场与立面仍分属不同候选对象，正式关系待 S6。S4 当前登记556组/700条映射，待登记4,248组/4,279条；KU 总数1,575。

### S4 work：Mazarin 委托的教堂立面（2026-10-17）

`cand-6797` 映射至[立面作品卡](../units/works/facade-ss-vincenzo-ed-anastasio-piazza-di-trevi.md)。卡片按书内叙述记录委托、建筑师角色、工程延宕与作者对立面权威表达的解释；与教堂和广场地点分开。5 条关联 S2 关系候选留待 S6，脚注所引档案与铭文未独立核阅；本轮未新增正式关系或 S5 补足。S4 当前登记557组/701条映射，待登记4,247组/4,278条；KU 总数1,576。

### S4 work：谷地圣安德烈堂祭坛席与穹顶装饰项目（2026-10-17）

`cand-5064` 映射至[项目作品卡](../units/works/s-andrea-della-valle-tribune-dome-decoration.md)。卡片区分 Montalto 的初始承诺、Domenichino 与 Lanfranco 后来的分工，以及已单独登记的 Lanfranco 穹顶壁画；7 条关系候选留待 S6，`cand-4500` 术语端点仍待 S4。未新增正式关系或 S5 补足。S4 当前登记558组/702条映射，待登记4,246组/4,277条；KU 总数1,577。

### S4 place：耶稣堂祭坛席内部空间（2026-10-17）

`cand-5000` 映射至[祭坛席地点卡](../units/places/tribune-of-gesu.md)。地点依据第3章 p.66 的家族专属装饰和继承人许可叙述登记；继承人及决策群体仍待证，7条关系候选留待 S6。未新增正式关系或 S5 补足。S4 当前登记559组/703条映射，待登记4,245组/4,276条；KU 总数1,578。

### S4 跨章：Circignani 与 S. Stefano Rotondo 殉道壁画组（2026-10-17）

按四个独立 S3 身份组登记画家、教堂地点、晚期罗马帝国政治实体与殉道壁画 work。第3章 p.67 与后记 p.399 的人名、作品称谓及索引 P.csv#171 支持跨章对应；Haskell 对 Buser 的转述与其限定保留为转述。未具名校长、German College、Lauretano、Venetian High Renaissance tradition 与未分类说明文字仍按原状态待证；六条关系候选留待 S6。S4 当前登记563组/707条映射，待登记4,241组/4,272条；KU 总数1,582。

### S4：耶稣堂主祭坛、Muziano 与《The Circumcision》（2026-10-17）

按三个独立 S3 身份组登记画家、主祭坛结构和祭坛画；祭坛结构与画作保持不同 work 身份。委托、家族保留装饰及继承人相关陈述留待 S6；未补写作品完成状态、材质或现存地点。S4 当前登记566组/710条映射，待登记4,238组/4,269条；KU 总数1,585。

### S4 place：耶稣堂后殿与侧礼拜堂群（2026-10-17）

两个独立 S3 地点组分别登记为耶稣堂后殿和侧礼拜堂群 KU；原书对 apse、tribune 与 side-chapels 的分别命名得到保留，不据此断言后殿与祭坛席的精确边界，也不拆分未具名的群体成员。后殿 1 条、侧礼拜堂群 6 条关系候选留待 S6；cand-5007、cand-5427 与 cand-5008 保持待决。未新增关系或 S5 补足。S4 当前登记568组/712条映射，待登记4,236组/4,267条；KU 总数1,587。

### S4 archive：两条耶稣堂封圣史文献引用（2026-10-17）

两个单成员 archive 组分别登记为1923年封圣三百周年纪念集与 Redig de Campos 1936年论文；前者仅按第3章脚注书目线索登记，后者按脚注与第21章书目交叉定位。两项所引文献均未独立查阅，引用关系留待 S6；未新增正式关系或 S5 补足。S4 当前登记570组/714条映射，待登记4,234组/4,265条；KU 总数1,589。

### S4 event：格列高利十五世册封事件（2026-10-17）

单成员事件组 cand-4980 登记为 source-backed KU；日期与地点按原书未说明处理，不与 1639–1640 年耶稣会会规获批百周年庆典合并。3条关系候选留待 S6，cand-4977 作品身份与 cand-1309 人物身份继续待证。未新增正式关系或 S5 补足。S4 当前登记571组/715条映射，待登记4,233组/4,264条；KU 总数1,590。

### S4 event：耶稣会会规获批百周年庆祝语境（2026-10-17）

单成员事件组 cand-4981 登记为 source-backed KU，记录 Urban VIII 于1639、1640年两次到访耶稣堂的共同庆祝语境；与第2章 cand-4761 的1639年接待保持分立。S2 未绑定该候选的关系记录，本次不新增正式关系或 S5 补足。S4 当前登记572组/716条映射，待登记4,232组/4,263条；KU 总数1,591。

### S4 place：安特卫普跨章地点端点（2026-10-17）

单成员地点组 cand-4983 登记为安特卫普城市 KU；第3章的出版地点与第8章 Gaspar Roomer 出生地点共同支持跨章对应。Roomer 已有人物 KU；出生地关系候选留待 S6，未新增正式关系或 S5 补足。S4 当前登记573组/717条映射，待登记4,231组/4,262条；KU 总数1,592。

### S4 archive / person：Galassi、Ottonelli–Pietro da Cortona 与 Casale（2026-10-17）

`cand-4974`映射至Galassi Paluzzi书目项，`cand-4979`映射至Haskell所列1652年论著版本；`cand-10937`映射至书内明确全名人物Vittorio Casale。1652与1973年书目版本保持分立，`cand-11160`继续待决；Ottonelli人物`cand-1800`及未具名审查意见文献`cand-10938`也未借本次登记消解。对应书内关系候选均留待S6，未新增S5事实。

S4 当前登记576组/720条映射，待登记4,228组/4,259条；KU 总数1,595。

### S4 archive / person：Rapparini颂词与De Bello Belgico（2026-10-17）

`cand-2108`登记为Rapparini颂词的书内文献身份；`cand-2515`登记为书名 *De Bello Belgico*，`cand-2514`登记Famiano Strada人物端点。两组文献未外查或独立阅读。De Bello的6条关系候选及Rapparini、Strada关联候选留待S6；`cand-11927`、`cand-11930`继续保留S3未决。

S4 当前登记579组/723条映射，待登记4,225组/4,256条；KU 总数1,598。

### S3/S4 archive：Pecchiai《I Barberini》跨章同一身份组（2026-10-17）

`cand-4239`与`cand-4575`依据第2章多处书内引用及第21章书目统一为一个新archive组并登记一张卡；作者人物`cand-4238`仍因缩写不足待证。Haskell转述的文献冲突不作独立裁决，关系候选留待S6。

S4 当前登记580组/725条映射，待登记4,219组/4,250条；KU总数1,599。

### S4 archive：Fraschetti《Il Bernini》与1633年Avviso（2026-10-17）

`cand-4553`登记为Fraschetti 1900年 *Il Bernini*，对应第1、2、5章及书目中的同一书目身份；`cand-4554`登记为Haskell第2章引述的1633年1月8日Avviso。原件与刊本未独立查阅，未推定Cardinal Borghese的名字。发现cand-4554已有mentions锚点但无S2主客体关系行；本次在过程记录保留该缺口，未新增正式边。

S4 当前登记582组/727条映射，待登记4,217组/4,248条；KU总数1,601。

### S4 archive：Mancini《Considerazioni sulla Pittura》1956年版（2026-10-17）

`cand-1508`（索引子项）与`cand-6089`（正文／书目候选）同属`archive-group-fb110b11a649`，共同登记为[1956年校勘版archive KU](../units/archives/mancini-considerazioni-sulla-pittura-1956.md)。第21章p.428书目明确给出Marucchi编、Salerno注释、罗马1956年两卷本；第1、5章的卷I页码定位与该书目对应。4条直接S2陈述中3条关系候选仍待S6，原书未独立查阅。

S4 当前登记584组/730条映射，待登记4,211组/4,245条；KU总数1,603。

### S4 archive：Manfrin致Edwards书信（1793-12-03；2026-10-17）

`cand-1515`（索引子项）与`cand-10849`（附录7书信候选）同属`archive-group-4ec5e3284567`，共同登记为[1793年书信archive KU](../units/archives/manfrin-edwards-letter-1793-12-03.md)。附录标题给出发信人、收信人、日期及画廊语境，并回指第17章p.380注6；注6称该信藏于Epistolario Meschini并在附录7全文刊出，附录标题拼作Epistolario Moschini。原件未独立查阅，两条直接S2关系候选待S6。

S4 当前登记585组/732条映射，待登记4,210组/4,243条；KU总数1,604。

### S4 institution：Biblioteca Governativa, Cremona 与 Biblioteca Marucelliana（2026-10-17）

直接S2关系端点`cand-8556`和`cand-9493`分别登记为[克雷莫纳 Biblioteca Governativa](../units/institutions/biblioteca-governativa-cremona.md)与[佛罗伦萨 Biblioteca Marucelliana](../units/institutions/biblioteca-marucelliana.md)。第9、10章书内书信注释提供馆名与所在地，Marucelliana另见第13章引文定位。两张卡只记录书内具名机构身份；7条相关S2关系候选仍待S6，未新增正式边。

S4 当前登记587组/734条映射，待登记4,208组/4,241条；KU总数1,606。

### S4 person：跨章人物关系端点——Alessandro Varotari 与 Roberto Longhi（2026-10-17）

`cand-2701`（new-person:alessandro-varotari-il-padovanino-8619a21d71）按第4章全名与别称“il Padovanino”及第13章索引条目中的Padovanino用例登记为[Alessandro Varotari](../units/persons/alessandro-varotari-il-padovanino.md)。`cand-5505`（new-person:longhi-roberto-5fac70ede1）依据第4、5、7、20章的全名及姓氏指代登记为[Roberto Longhi](../units/persons/roberto-longhi.md)。两组各新增一个person KU；3条与Varotari相关、2条与Longhi相关的直接S2关系候选均待S6，本次不新增正式边。未访问外部身份规范记录。

S4 当前登记589组/736条候选映射，待登记4,206组/4,239条；KU总数1,608。

### S4 person：跨章人物关系端点——Saint Peter 与 Giacomo Barozzi da Vignola（2026-10-17）

`cand-4231`（new-person:apostle-peter-94e2c375ba）登记为[使徒圣彼得](../units/persons/saint-peter-the-apostle.md)；S2已将其与圣彼得大教堂地点及同名作品区分。`cand-2775`（new-person:barozzi-da-giacomo-vignola-072c61027f）依据原书索引全名与第3、4、10、20章的指称登记为[Giacomo Barozzi da Vignola](../units/persons/giacomo-barozzi-da-vignola.md)。两组各新增一个person KU；与两人相关的3条直接S2关系候选均待S6，本次不新增正式边，未访问外部身份来源。

S4 当前登记591组/738条候选映射，待登记4,204组/4,237条；KU总数1,610。

### S4 person：跨章人物关系端点——Lady Mary Wortley Montagu 与 Denis Diderot（2026-10-17）

`cand-1688`（new-person:lady-mary-montagu-wortley-e31f25b442）依据第10章与第14章的全名、头衔及语境登记为[Lady Mary Wortley Montagu](../units/persons/lady-mary-wortley-montagu.md)。`cand-0919`（new-person:denis-diderot-940e9e0035）依据第14章与第20章后记的姓名和回指登记为[Denis Diderot](../units/persons/denis-diderot.md)；第14章注释明确将法文引语经Treat转引。两组各新增一个person KU；4条直接S2关系候选均待S6，未新增正式边或外部核验状态。

S4 当前登记593组/740条候选映射，待登记4,202组/4,235条；KU总数1,612。

### S4 person：跨章人物关系端点——Jean Lemaire 与 Antonio Gai（2026-10-17）

`cand-1385`（new-person:jean-lemaire-e5876e626a）依据第4、7章反复出现的全名登记为[Jean Lemaire](../units/persons/jean-lemaire.md)。`cand-1099`（new-person:antonio-gai-479e2478a1）依据第10、13章“雕塑家Gai”的指称及书内索引全名登记为[Antonio Gai](../units/persons/antonio-gai.md)。Gai索引列示第341页，而第13章正文转录页标为342，过程记录保留两种定位。两组各新增一个person KU；4条直接关系候选待S6，不新增正式边或外部身份核验状态。

S4 当前登记595组/742条候选映射，待登记4,200组/4,233条；KU总数1,614。

### S4 person：跨章人物关系端点——Nicolas-Claude-Fabri de Peiresc 与 Joachim von Sandrart（2026-10-17）

`cand-1861`（new-person:claude-de-fabri-nicolas-peiresc-cf0115e95f）依据第2、4章姓名及书内索引全名登记为[Nicolas-Claude-Fabri de Peiresc](../units/persons/nicolas-claude-fabri-de-peiresc.md)。`cand-2353`（new-person:german-joachim-sandrart-von-joachim-sandra-2467fbbb7e）依据第2章全名及第8章姓氏指代登记为[Joachim von Sandrart](../units/persons/joachim-von-sandrart.md)。两组各新增一个person KU；4条直接S2关系候选留待S6，不新增正式边或外部身份核验状态。

S4 当前登记597组/744条候选映射，待登记4,198组/4,231条；KU总数1,616。

### S4 person：跨章人物关系端点——William Petty、William Pitt the Elder 与 Pope Paul III（2026-10-17）

`cand-1894`（new-person:petty-william-e0750fd206）依据第4、7章及索引条目登记为[William Petty](../units/persons/william-petty-arundel-agent.md)。`cand-1947`（new-person:elder-pitt-william-a3834b7e2c）依据第14、20章及索引条目登记为[William Pitt, the Elder](../units/persons/william-pitt-the-elder.md)。`cand-4515`（new-person:iii-paul-d17277c320）依据第2、4章关于Paul III陵墓的指称登记为[Pope Paul III](../units/persons/pope-paul-iii.md)；第4章OCR作“Paul Ill”，已保留。三组各新增一个person KU；5条直接S2关系候选留待S6，不新增正式边或外部身份核验状态。

S4 当前登记600组/747条候选映射，待登记4,195组/4,228条；KU总数1,619。

### S4 person：跨章人物关系端点——Catherine the Great 与 Antonio Molinari（2026-10-17）

`cand-0609`（`new-person:catherine-great-of-russia-85ee1f0320`）登记为[叶卡捷琳娜二世](../units/persons/catherine-the-great-russia.md)。第10章p.298将购买《埃及艳后宴会》作为其欣赏威尼斯艺术的证据；第20章p.406后记称作者此前关于她本人购买该画的假定过于自信。卡片保留这一跨章判断变化，不将购买行为写作已确认事实。`cand-1679`（`new-person:antonio-molinari-5e2b48c6a7`）登记为[Antonio Molinari](../units/persons/antonio-molinari.md)，依据第5章p.129全名及第10章p.294姓氏提及。p.129 OCR读作“sit”，印本校读为“fit”；保留该校正，且不把“25 years earlier”换算为具体年份。

两组各新增一个person KU和一条候选映射；Catherine的2条、Molinari的2条直接S2关系候选均待S6。本次不新增正式关系或外部身份核验状态。

S4 当前登记602组/749条候选映射；待登记4,193组/4,226条；KU总数1,621。

### S3/S4 复核：Federigo Zuccari 复用既有人物 KU（2026-10-17）

`cand-2885`原列为`new-person:federigo-zuccari-2774f913d3`，在S4查重时发现应复用[Federico Zuccari人物卡](../units/persons/federigo-zuccari.md)。该卡已有`cand-3030`通过`aln-3307`映射至同一KU，且第一章来源原句已明确写出“Federigo Zuccari”；第2、3章重复该精确姓名。故将`cand-2885`改为`same`并映射至既有KU，不新建卡；原`new`决定及漏检更正理由保留于过程记录与对齐行。第3章未具名贵妇引入画家的关系候选仍待S6。

当前对齐决定为same 1,884条、new 4,974条（4,794组）；S4新组已登记602组，待登记4,192组/4,225条映射；KU总数1,621。

### S4 person：跨章关系端点——Andrea del Sarto、Giovanni da San Giovanni 与 Louis XIII（2026-10-17）

`cand-2361`登记为[Andrea del Sarto](../units/persons/andrea-del-sarto.md)，依据第2章p.30与第9章p.251的跨章具名提及；第2章只将其列入宫殿绘画群组的举例，具体作品未定。`cand-4876`登记为[Giovanni da San Giovanni](../units/persons/giovanni-da-san-giovanni.md)，第2章注释转述Baldinucci轶事，第4章将其列入Orsini周围的艺术家圈。`cand-1446`登记为[Louis XIII](../units/persons/louis-xiii.md)；第2章将赠礼与已悬挂的七幅挂毯连续叙述，但未明言二者相同，第7章记其于1643年年中已去世。

三组各新增一个person KU和一条候选映射；3条直接S2关系候选全部保留待S6。本次不将原书集合性、转述性或相邻句推断升级为正式边。

S4 当前登记605组/752条候选映射；待登记4,189组/4,222条；KU总数1,624。

### S4 person：跨章关系端点——Marilyn Aronberg Lavin 与 Pope Gregory XIII（2026-10-17）

`cand-4787`（`new-person:aronberg-lavin-marilyn-88b8833863`）登记为[Marilyn Aronberg Lavin](../units/persons/marilyn-aronberg-lavin.md)。第2章注释的OCR作“Lavili”，现有S2候选记录注明印本为“Lavin”；第20章后记再次以Marilyn Lavin称呼该出版者。两处书内姓名及语境支持本组映射，未独立查阅清单出版物。`cand-0386`（`new-person:boncampagni-ugo-gregory-xiii-064b1bab8e`）登记为[Pope Gregory XIII](../units/persons/pope-gregory-xiii.md)。第2章脚注保存经Baglione与Orbaan传递的引文归属，第3章另以全名记述两项教会划拨语境；没有独立核查前者的转引来源。

两组各新增一个person KU和一条候选映射；两条直接S2关系候选均待S6。本次不新增正式关系或外部身份核验状态。

S4 当前登记607组/754条候选映射；待登记4,187组/4,220条；KU总数1,626。

### S4 person：跨章关系端点——Julian the Apostate、Goffredo Wals 与 Giacinto Gigli（2026-10-17）

`cand-1336`（`new-person:apostate-julian-faf208b96a`）登记为[Julian the Apostate](../units/persons/julian-the-apostate.md)，依据第4章1630年版本语境及第7章作品题材提及；第4章对Petau序言的说明仍是Haskell转述。`cand-2800`（`new-person:goffredo-wals-e36dbf4df9`）登记为[Goffredo Wals](../units/persons/goffredo-wals.md)，第5章原文的“is supposed to have”限定保留，第8章异写“Gioffredo”并存。`cand-1168`（`new-person:giacinto-gigli-cef75d311f`）登记为[Giacinto Gigli](../units/persons/giacinto-gigli.md)，第5章OCR“Giacinto GigE”与书内索引全名相对照，第6章注释再次出现Gigli；OCR读法及日记未独立查阅的状态均保留。

三组各新增一个person KU和一条候选映射；3条直接S2关系候选均待S6。本次不新增正式关系或外部身份核验状态。

S4 当前登记610组/757条候选映射；待登记4,184组/4,217条；KU总数1,629。

### S4 person：跨章关系端点——Micco Spadaro、Gustavus Adolphus 与 Niccolò Berrettoni（2026-10-17）

`cand-2495`（`new-person:micco-spadaro-2b56032967`）登记为[Micco Spadaro](../units/persons/micco-spadaro.md)。第5章注释定位其绘画于圣马蒂诺博物馆，第8章注释另述其为Codazzi作品绘制人物；相关作品语境与《Masaniello起义》双场景画保持分离。`cand-1284`（`new-person:adolphus-gustavus-of-sweden-e13b1682aa`）登记为[Gustavus Adolphus of Sweden](../units/persons/gustavus-adolphus-sweden.md)，保留第6章OCR“Adolfus”与第7章“Adolphus”形式及两章各自的布拉格藏品叙述；不独立裁决劫掠责任。`cand-0367`（`new-person:berrettoni-niccolo-e92fe6e410`）登记为[Niccolò Berrettoni](../units/persons/niccolo-berrettoni.md)，第6章以姓氏提及其宫殿作品，第7章两次给出全名且页图有重音符号。

三组各新增一个person KU和一条候选映射；3条直接S2关系候选均待S6。本次不新增正式关系或外部身份核验状态。

S4 当前登记613组/760条候选映射；待登记4,181组/4,214条；KU总数1,632。

### S3/S4 复核：Ferdinando II de’ Medici 与 Marco Alvise Pitteri 复用既有 KU（2026-10-17）

`cand-1608`由`new-person:de-ferdinando-ii-medici-of-tuscany-86d09e74dc`改为`same` → [Ferdinando II de’ Medici人物卡](../units/persons/ferdinando-ii-de-medici.md)。M.csv索引全名与头衔、章7大公指称及章20“Grand Duke Ferdinand II”同现身份，既有卡已登记该人物；本次复用，不重复建卡。

`cand-1948`由`new-person:marco-pitteri-1a39ee76ea`改为`same` → [Marco Alvise Pitteri人物卡](../units/persons/marco-pitteri.md)。第9章p.200明确称“Marco Pitteri”，第10、13章继续以雕版家语境称Pitteri；既有卡已用图版目录中的“Marco Pitteri”及外部身份记录标识该人物。页码定位问题仍保留：候选记录写索引页260、312、335n；当前P.csv#149写260、312、222n；第9章来源页标为p.200。此差异不改变人物复用判断，不据此补造或替换章节定位。

两条候选均映射既有KU，不增加manifest或新卡。Ferdinando II的1条、Pitteri的2条直接S2关系候选仍待S6。

当前same 1,886条，new 4,972条（4,792组）；S4新组已登记613组，待登记4,179组/4,212条映射；KU总数1,632。

### S3 archive：C. A. Levi 1900 年出版物跨章并组（2026-10-17）

cand-8533（第9、15、19章引文）与 cand-11374（第21章书目）现同属 archive-group-5b4568c2a1c8：书目所列 *Le Collezioni Veneziane d’arte e d’antichità dal secolo XIV ai nostri giorni* （Venezia 1900）与三章中“Levi 1900年汇编”及卷II页码引文相合。两候选均保持 S3 new，合并为一个待 S4 登记的 archive KU；未独立查阅出版物。卷I短引、未具名库存群、C. A. Levi 人物身份及具体库存清单继续保持各自的 undecided/new 状态，未并入该出版物。详见[S3裁决过程](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-levi-inventory-publication-merge-20261017)与[对齐表](../tables/alignment.csv)。


### person：Guarino Guarini 跨章身份组 S4 登记（2026-10-17）

cand-6876 登记至[人物卡](../units/persons/guarino-guarini.md)。第7章 p.186、p.193 的全名一致；本卡只记录 Haskell 的书内叙述。3 条直接关系候选待 S6；Theatines 已映射既有机构 KU，教堂地点与 Adelaide Enrichetta 人物各自待 S4。

S4 当前登记640组/790条映射，待登记4,151组/4,182条。


### person：Giuseppe Valeriani 跨章身份组 S4 登记（2026-10-17）

cand-9382 登记至[人物卡](../units/persons/giuseppe-valeriani.md)。第10章 p.289 与第20章 p.406 均以全名指名；不推断其在两件纪念碑中的个人角色，1948年著作未独立查阅。3条直接关系候选待 S6。Domenico Valeriani 保持独立；合并索引标题维持 excluded，两个纪念碑端点及1948年著作各保留原 S3 决定。

S4 当前登记641组/791条映射，待登记4,150组/4,181条。


### person：Girolamo Colonna 跨章身份组 S4 登记（2026-10-17）

cand-0809 登记至[人物卡](../units/persons/girolamo-colonna.md)。第6章与第7章的全名、称谓相合；两条关系候选待 S6。Mazarin 与 Spain 复用既有 KU，家族宫殿候选已独立登记；Filippo Colonna 另组待 S4，原文父子措辞尚无独立 statement ID，留待 S6 回读核查。

S4 当前登记642组/792条映射，待登记4,149组/4,180条。


### person：Philip Skippon 跨章身份组 S4 登记（2026-10-17）

cand-2438 登记至[人物卡](../units/persons/philip-skippon.md)。索引全名、1663年藏品记录与第4章及第6章的引用作为同一书内人物组；两条直接关系候选待 S6。鸟类绘画未逐件识别，Poussin 归属不确定，Cassiano 的侄子未具名。

S4 当前登记643组/793条映射，待登记4,148组/4,179条。

### S3 archive：1948 年 Giuseppe Valeriani 著作跨章并组（2026-10-17）

cand-11088（第20章 p.406 正文描述）与 cand-11204（第20章注7及第21章 p.426 书目）现同属 archive-group-09a3b2fdbd56：1948年出版年、Giuseppe Valeriani 主题与注号7所指的 M. S. Konopleva 书目记录相合。两候选均保持 S3 new，合并为一个待 S4 登记的 archive KU；书籍未独立查阅。已更正注7 statement 对应书目的 claim；作者个人身份与注号8的两篇后续论文仍待证。


### S4 archive：1948 年 Giuseppe Valeriani 著作登记（2026-10-17）

cand-11088 与 cand-11204 按 S3 同组裁决共同映射至 [舞台画家朱塞佩·瓦莱里亚尼](../units/archives/teatralni-zhivopicets-giuseppe-valeriani-1948.md)。正文、注7与书目页形成可追溯身份链；作者身份和被引书原文未扩展，正文关系候选仍待 S6。S4 累计登记644组/795条候选映射；待登记4,146组/4,177条；KU 总数1,663。

### S4 person：Andrea Brustolon 登记（2026-10-17）

cand-0463 映射至 [安德烈亚·布鲁斯托隆](../units/persons/andrea-brustolon.md)。索引与第13章 p.337、p.340 提供姓名及书内身份锚点；3条版画和雕刻计划关系候选仍待 S6，未登记为正式关系。S4 累计登记645组/796条候选映射；待登记4,145组/4,176条；KU 总数1,664。

### S4 person：Peterborough 第三代伯爵登记（2026-10-17）

cand-1891 映射至 [彼得伯勒第三代伯爵](../units/persons/3rd-earl-of-peterborough.md)。书内仅给爵位，不补个人姓名；Admiral “Pekemburgh” cand-7285 仍 undecided，未合并。4条直接关系候选保持待 S6。S4 累计登记646组/797条候选映射；待登记4,144组/4,175条；KU 总数1,665。

### S4 person：Pietro Rotari 登记（2026-10-17）

cand-2288 映射至 [彼得罗·罗塔里](../units/persons/pietro-rotari.md)。索引和第10章 pp.295、297提供同一书内身份锚点；时间表述保留原样，3条关系候选待 S6，未识别作品组不登记为 KU。S4 累计登记647组/798条候选映射；待登记4,143组/4,174条；KU 总数1,666。

### S4 place：St Petersburg 城市地点登记（2026-10-17）

cand-2343 映射至 [圣彼得堡](../units/places/st-petersburg.md)。索引和第10章 pp.297–298提供多处书内锚点；Bellotto 的前往计划及 Haskell 对画作转移的解释均按来源限定保留，3条关系候选待 S6。S4 累计登记648组/799条候选映射；待登记4,142组/4,173条；KU 总数1,667。

### S3 place：Verona 跨章身份组合（2026-10-17）

cand-7661（p.216 regional adjective）与 cand-8681（p.268 explicit Verona）现同属 sg3-place-cand-8681，并由 p.297、311、327、348 的同一城市用法补强跨章映射。两候选仍保持 new；S4 应登记一个 Verona place KU。

### S4 place：Verona 跨章地点登记（2026-10-17）

cand-7661 与 cand-8681 共同映射至 [维罗纳](../units/places/verona.md)。跨第8、9、10、14章的地名及地域用语支撑同一城市地点；3条直接关系候选留待 S6。S4 累计登记649组/801条候选映射；待登记4,140组/4,171条；KU 总数1,668。

### S3/S4 place：Camillo Pamfili palace 与 Villa Doria Pamphilj 分组纠偏（2026-10-17）

cand-1816（P.csv#15, palace）复用既有 Palazzo Doria-Pamfili KU；cand-1817（P.csv#16, villa built by Algardi）拆出为独立 new place 组 sg3-place-villa-doria-pamphilj，映射至 [Villa Doria Pamphilj](../units/places/villa-doria-pamphilj.md)。第6章 p.148 明确叙述先有 Algardi 建造的别墅、后另建 Collegio Romano 对面的宫殿；官方记录中的 Camillo、Algardi 与罗马乡间庄园语境支持身份区分。六条直接关系候选继续待 S6，无正式边新增。当前 S3 same=1,887（1,040个既有 KU）、new=4,971（4,789组）；S4 已登记650组/802条映射，待登记4,139组/4,169条；KU=1669。

### S3/S4 term：Baroque 跨章身份复核与文化范畴登记（2026-10-17）

cand-3569 改判 same → units/terms/baroque；原 new 组撤回。cand-4500 保持 new，登记至[哈斯克尔论述中的巴洛克艺术文化范畴（The Baroque as an artistic-cultural category in Haskell's account）](../units/terms/baroque-cultural-category-haskell.md)。两项分别落实哈斯克尔的操作性历史分期与跨章艺术文化范畴用法。七条直接 S2 关系候选仍待 S6；本次未新增正式关系或 S5 补足。当前 S3 same=1,888、new=4,970（4,788组）；S4 已登记654组/810条候选映射，待登记4,134组/4,160条映射；KU总数1673。

### S3/S4 place、term：Rome 端点复用与 Spanish cause 跨章登记（2026-10-17）

cand-6474 改判 same → units/places/rome，原 new 组撤回；cand-4404 维持 new 并登记至[哈斯克尔所述罗马的亲西班牙政治倾向（The Spanish cause in Rome in Haskell's account）](../units/terms/spanish-cause-in-rome-haskell-account.md)。六条直接关系候选仍待 S6；另有七条 Rome 端点映射至既有城市 KU，本次没有新增正式关系或补足事实。当前 S3 same=1,889、new=4,969（4,787组）；S4 已登记655组/811条候选映射，待登记4,132组/4,158条映射；KU总数1674。

### S3/S4 event：第一次卡斯特罗战争跨章身份登记（2026-10-17）

cand-4904 保持 new 并登记为[第一次卡斯特罗战争（First War of Castro）](../units/events/first-war-of-castro.md)。历史草稿不在当前 manifest/accepted 中；本次沿用对象路径并更新为双语来源卡。索引总入口、第二次战争和未命名和约分别保留原待决／独立去向。五条直接关系候选仍待 S6，本次未新增正式关系或补足事实。当前 S3 same=1,889、new=4,969（4,787组）；S4 已登记656组/812条候选映射，待登记4,131组/4,157条映射；KU总数1675。

### S3/S4 institution：Scalzi 威尼斯分支登记（2026-10-17）

cand-2389 保持 new 并登记至[威尼斯赤足加尔默罗会（Scalzi in Venice）](../units/institutions/scalzi-in-venice.md)。卡片将其与母会 Carmelites 及另一修会 Discalced Trinitarians 分开。六条直接关系候选仍待 S6；本次未新增正式关系或 S5 补足。当前 S3 same=1,889、new=4,969（4,787组）；S4 已登记657组/813条候选映射，待登记4,130组/4,156条映射；KU总数1676。


### S4 person：三个直接关系端点身份组登记（2026-10-17）

- cand-0905 → [卡洛·达蒂（Carlo Dati）](../units/units/persons/carlo-dati.md)；3 条直接关系候选留待 S6。
- cand-0108 → [乔万尼·阿尼穆恰（Giovanni Animuccia）](../units/units/persons/giovanni-animuccia.md)；3 条直接关系候选留待 S6。
- cand-2435 → [弗朗切斯科·西蒙尼尼（Francesco Simonini）](../units/units/persons/francesco-simonini.md)；3 条直接关系候选留待 S6。

本批未新增正式关系或外部身份核验。

### S3 person：Niccolò Bambini 既有身份复核（2026-10-17）

cand-0171 原 new 组改为 same → [units/persons/niccolo-bambini](../units/persons/niccolo-bambini.md)。正文、索引、图版42b及既有同人候选互相印证；原 new 组及旧理由保留在 alignment 中，未重复登记 KU。三条直接关系候选留待 S6。


### S4 person：Belloni 与 Clostermann 直接关系端点登记（2026-10-17）

- cand-0271 → [乔万尼·安东尼奥·贝洛尼（Giovanni Antonio Belloni）](../units/units/persons/giovanni-antonio-belloni.md)；3 条直接关系候选留待 S6。
- cand-0791 → [约翰·克洛斯特曼（John Clostermann）](../units/units/persons/john-clostermann.md)；3 条直接关系候选留待 S6。

Belloni 与 Giovanni Battista Bellucci 分立；Closterman／Clostermann 拼写差异保留。未新增正式关系或外部身份核验。

### S4 person：Giovanni Battista Bellucci 直接端点登记（2026-10-17）

cand-0285 → [乔万尼·巴蒂斯塔·贝卢奇（Giovanni Battista Bellucci）](../units/persons/giovanni-battista-bellucci.md)；与 Belloni 分属不同人物组，两条收藏关系候选留待 S6。

### S4 person：Bentinck 与 Dupuy 直接关系端点登记（2026-10-17）

- cand-0289 → [威廉·本廷克（William Bentinck）](../units/units/persons/william-bentinck.md)；3 条直接关系候选留待 S6。
- cand-0951 → [克里斯托夫·迪皮（Christophe Dupuy）](../units/units/persons/christophe-dupuy.md)；3 条直接关系候选留待 S6。

本批未新增正式关系或外部身份核验。

### S4 person：Domenico Bernini 直接关系端点登记（2026-10-17）

cand-0294 → [多梅尼科·贝尔尼尼（Domenico Bernini）](../units/persons/domenico-bernini.md)；书内姓名与索引跨页定位相符，三条直接关系候选留待 S6。

### S3 person：Giovanni Bonati／Bonatti 既有身份复核（2026-10-17）

cand-0385 原 new 组改为 same → [units/persons/giovanni-bonati](../units/persons/giovanni-bonati.md)。印刷页姓名校读、既有卡同页记录、保护人与旅行语境及 Treccani DBI 的“BONATTI (Bonati), Giovanni”相互印证；未重复登记 KU。关系候选留待 S6。


### S3 person：Sebastiano Bombelli 索引子目并组复核（2026-10-17）

cand-0384 从 undecided 改为 new，并入 new-person:bombelli-sebastiano-c6f300a2fb；p.227 的索引肖像子目由同页正文锚定，与 p.278 主项共同指向同一人物组。S4 登记时两条候选映射共用一个 KU。


### S4 person：Sebastiano Bombelli 跨章身份组登记（2026-10-17）

cand-0383、cand-0384 → [塞巴斯蒂亚诺·邦贝利（Sebastiano Bombelli）](../units/persons/sebastiano-bombelli.md)；第8章 p.227 正文对应索引肖像子目，第10章 p.278 主项提供跨章同名锚点。直接关系候选留待 S6。

### S3/S4 person：三组跨章人物身份复核与登记（2026-10-17）

cand-0388、cand-0389 → [贾科莫·安东尼奥·博尼（Giacomo Antonio Boni）](../units/persons/giacomo-antonio-boni.md)；cand-0252、cand-0253 → [弗拉·巴托洛梅奥（Fra Bartolommeo）](../units/persons/fra-bartolommeo.md)；cand-0412、cand-0413 → [马尔科·博斯基尼（Marco Boschini）](../units/persons/marco-boschini.md)。逐组裁决、来源边界与组成员见过程记录。


### S3/S4 archive：Temanza 未刊 Zibaldone MS 796（2026-10-17）

cand-2547、cand-6588 → [托马索·滕曼扎未刊《Zibaldone》手稿（MS 796）（Tommaso Temanza, unpublished Zibaldone MS 796）](../units/archives/temanza-zibaldone-ms-796.md)。手稿身份限于原书脚注和索引定位；馆藏与手稿内容未独立核验。引用候选留待 S6。

### S3/S4 person：Isidoro Bianchi 直接关系端点登记（2026-10-17）

cand-0372 → [伊西多罗·比安基（Isidoro Bianchi）](../units/persons/isidoro-bianchi.md)；两条直接关系候选仍待 S6。

### S3/S4 person：Bigari 与 Bizoni 直接关系端点登记（2026-10-17）

cand-0374 → [维托里奥·比加里（Vittorio Bigari）](../units/persons/vittorio-bigari.md)；cand-0377 → [贝尔纳多·比佐尼（Bernardo Bizoni）](../units/persons/bernardo-bizoni.md)。双语卡只记录书内姓名和语境；各自的直接关系候选留待 S6。

### S3/S4 person：Mme de Boccage 直接关系端点登记（2026-10-17）

cand-0380 → [博卡热夫人（Mme de Boccage）](../units/persons/mme-de-boccage.md)；正文与索引拼写差异按同页语境保留。

### S3/S4 person：Francesco Bordoni 直接关系端点登记（2026-10-17）

cand-0392 → [弗朗切斯科·博尔多尼（Francesco Bordoni）](../units/persons/francesco-bordoni.md)；中文名为工作音译，关系陈述仍待 S6。

### S3/S4 person：Francesco Albergati-Capacelli 直接关系端点登记（2026-10-17）

cand-0023 → [弗朗切斯科·阿尔贝加蒂-卡佩切利（Francesco Albergati-Capacelli）](../units/persons/francesco-albergati-capacelli.md)；中文名为工作音译，关系陈述仍待 S6。

### S3/S4 person：Claudio Aquaviva 直接关系端点登记（2026-10-17）

cand-0113 → [克劳迪奥·阿夸维瓦（Claudio Aquaviva）](../units/persons/claudio-aquaviva.md)；称谓与关系范围按原文保留，三项关系候选仍待 S6。

### S3/S4 archive：The Table / Pinax 对话登记（2026-10-17）

cand-6390 → [《寓意人生图的对话》（The Table (Pinax dialogue)）](../units/archives/the-table-pinax-dialogue.md)；作者未具名、年代保留 probably 限定，Seebohm 英译本保持独立待决。

### S3/S4 archive：Pietro Monaco 1763 年版画集登记（2026-10-17）

cand-7618 → [《圣史绘画112幅版画集（1763年版）》（Collection of 112 Prints of Sacred-History Paintings (1763 edition)）](../units/archives/monaco-raccolta-112-stampe-1763.md)；Haskell 与 Treccani 对后出 Viero 版的年份不同，保留待证。

### S3/S4 archive：Applausi poetici 1639 年版登记（2026-10-17）

cand-5531 → [《莱奥诺拉·巴罗尼颂诗集（1639年）》（Poetic Tributes to Leonora Baroni (1639 edition)）](../units/archives/applausi-poetici-leonora-baroni-1639.md)；题名 scan correction 依现有 S0 记录，四条关系候选仍待 S6。

### S3/S4 person：Jane Costello 身份组登记（2026-10-17）

cand-7016 → [简·科斯特洛（Jane Costello）](../units/persons/jane-costello.md)；范围限于该书所引1950年论文的作者身份，cand-3509 保留待证。

### S3/S4 archive：Warburg 期刊跨题名登记（2026-10-17）

cand-6004 → [《瓦尔堡与考陶尔德学院学报》（Journal of the Warburg and Courtauld Institutes）](../units/archives/journal-warburg-courtauld-institutes.md)；出版社期刊史支持1937–1939年旧题名及1940年改题沿革。

### S3/S4 archive：Jane Costello 1950 年论文登记（2026-10-17）

cand-7017 → [《委拉斯开兹“订购”的十二幅画与瓦尔古阿内拉审判（1950年）》（The Twelve Pictures "Ordered by Velasquez" and the Trial of Valguarnera (1950)）](../units/archives/costello-twelve-pictures-ordered-velasquez-1950.md)；四项直接引文关系候选留待 S6；论文全文未独立查阅。

### S3/S4 institution：Austrian government 端点登记（2026-10-17）

cand-8471 → [奥地利政府（Austrian government）](../units/institutions/austrian-government.md)；仅保留原书所用的受让方称谓。

### S3/S4 institution：Hofbibliothek, Vienna 端点登记（2026-10-17）

cand-8472 → [维也纳宫廷图书馆（Hofbibliothek, Vienna）](../units/institutions/hofbibliothek-vienna.md)；按原书所述存放机构登记，不等同于 Vienna 城市。

### S3/S4 archive：Marco Foscarini 书籍与手稿收藏登记（2026-10-17）

cand-8462 → [马尔科·福斯卡里尼的书籍与手稿收藏（Marco Foscarini's library of manuscripts and history books）](../units/archives/marco-foscarini-library.md)；四项关系候选留待 S6；Foscarini palace 继续 undecided。

### S3/S4 person：Tirso Gonzalez 身份组登记（2026-10-17）

cand-1213 → [蒂尔索·冈萨雷斯（Tirso Gonzalez）](../units/persons/tirso-gonzalez.md)；保留原书人名与总会长语境，三条关系候选留待 S6。

### S3/S4 person：Martino Longhi the Elder 跨章身份组登记（2026-10-17）

cand-1427 → [马蒂诺·隆吉（长者）（Martino Longhi the Elder）](../units/persons/martino-longhi-elder.md)；第3章与第20章同名身份组登记，与 Martino Longhi the Younger 分立；两条关系候选留待 S6。

### S3/S4 person：Giovanni Battista Piranesi 跨章身份组登记（2026-10-17）

cand-1938 → [乔瓦尼·巴蒂斯塔·皮拉内西（Giovanni Battista Piranesi）](../units/persons/giovanni-battista-piranesi.md)；与 Francesco Piranesi 分组；浴室版画候选仍 undecided，关系候选留待 S6。

### S3/S4 person：Andrea Mantegna 跨章身份组登记（2026-10-17）

cand-1522 → [安德烈亚·曼特尼亚（Andrea Mantegna）](../units/persons/andrea-mantegna.md)；第7章与第17章提及归于书内索引的同一主项；Manfrin collection 候选保持 undecided/untyped，关系候选留待 S6。

### S3/S4 person：Alessandro Scarlatti 跨章身份组登记（2026-10-17）

cand-2393 → [亚历山德罗·斯卡拉蒂（Alessandro Scarlatti）](../units/persons/alessandro-scarlatti.md)；第8章全名与第10章索引对应的姓氏提及归于同组；关系候选留待 S6。

### S3/S4 person：Stefano della Bella 身份组登记（2026-10-18）

cand-0268 → [斯特凡诺·德拉·贝拉（Stefano della Bella）](../units/persons/stefano-della-bella.md)；第7章两处身份锚点对应索引同一主项；关系候选留待 S6。

### S3/S4 person：Francesco Gabburri 跨章身份组登记（2026-10-18）

cand-1097 → [弗朗切斯科·加布里乌里（Francesco Gabburri）](../units/persons/francesco-gabburri.md)；第8、9章书信注释与索引全名对应同一人物组；关系候选留待 S6。

### S3/S4 person：Giorgio Massari 跨章身份组登记（2026-10-18）

cand-1562 → [乔尔乔·马萨里（Giorgio Massari）](../units/persons/giorgio-massari.md)；M.csv#103将第9章 p.270、p.272与第10章 p.321列为同一人物主项；关系候选留待 S6。

### S3/S4 person：Bartolommeo Nazari 复用既有 KU（2026-10-17）

cand-1727 的新建决定经身份复核改为 same，映射到[既有 Bartolomeo Nazari KU](../units/persons/b-nazari.md)；S2 全名与 Treccani DBI 所记 Schulenburg 肖像委托相互吻合，没有新增卡片。

### S3/S4 person：Sir Andrew Fountaine 跨章身份组登记（2026-10-17）

cand-1060 → [安德鲁·方丹爵士（Sir Andrew Fountaine）](../units/persons/andrew-fountaine.md)；F.csv#75将第10章 p.279与第13章 p.343 注3列为同一人物主项；关系候选留待 S6。


### S3/S4 institution/place：Spain 跨章政治实体与地点身份裁决（2026-10-17）

- cand-4591、cand-8123、cand-8833 合并为一个新的 Spain 政治实体身份组并登记至[西班牙政治实体 KU](../units/institutions/spain-polity.md)；cand-10409 改为 same，复用既有 units/places/spain。
- 两条提及映射已校正：第2章 p.46 的目的地映射到地理 Spain；第5章 p.136 的 Spain 及其在 Rome 的支持者语境映射到政治实体。
- Spanish Crown、Spanish Empire、Spanish monarchy、未具名 Spaniards／Spanish political power 及 threatened-war event 保持各自新建或待证去向，不与本卡混同。直接 S2 关系候选仍待 S6，无新增正式关系或外部身份记录。
- 更新后 S3：same=1,893；new=4,966/4,781组；conflict=8；excluded=100；undecided=5,440。S4 已登记 708组/872条映射，待登记 4,073组/4,094条映射；KU=1,727。


### S4 结构化字段登记：Spain 政治实体（2026-10-17）

新机构卡的跨章指称、政体范围与身份边界已登记为三条双语 enrichment 字段（enr-14425–enr-14427），均由 Haskell 书内来源支持；S4 总字段记录数为10,677。未新增外部身份事实或正式关系。


### S4 person：三组直接关系端点身份组登记（2026-10-17）

S3 已裁为 new 的人物组 new-person:benjamin-styles-96734d9ba8（cand-2531）、new-person:lazzaro-riviera-b4050e50ae（cand-2204）和 new-person:anna-colonna-22071d55fd（cand-0805）各登记为一张 KU；对齐表已逐一写入 KU 映射，三张卡均含双语名称与等值描述、书内原文来源及姓名／类型字段。九条字段记录为enr-14428, enr-14429, enr-14430, enr-14431, enr-14432, enr-14433, enr-14434, enr-14435, enr-14436，均 source_backed、复用既有 Haskell 来源。三人各自的3条直接 S2 关系候选仍待 S6，本批没有新增正式关系；sources.csv 未改动。本批后 S4 已登记711组／875条候选映射，待登记4,070组／4,091条映射；KU=1,730，字段=10,686。

### S4 person：Francesco Maria della Rovere、Jennifer Montagu、Ippolito Bentivoglio、Francis Xavier 四组登记（2026-10-17）

cand-2671、cand-1687、cand-0293、cand-2826 分别按其 singleton S3 new 组登记至四张人物 KU；卡片保留原书姓名／索引拼写差异、来源页码和语境限定。18条字段记录（enr-14437–enr-14454）均有既有 Haskell 来源。12条直接 S2 关系候选的人物端点现已映射，正式关系仍待 S6；sources.csv 与 relations.csv 未改动。本批后 KU=1,734、enrichment=10,704；S4 已登记715组／879条成员映射，待登记4,066组／4,087条。

### S4 person：Count Camillo Carandini、Marchese Girolamo Durazzo、André Félibien、Andrea Ferrerio 四组登记（2026-10-17）

cand-0542、cand-0953、cand-1015、cand-1024 分别按其 singleton S3 new 组登记为人物 KU，姓名、索引／正文差异及书内身份锚点已写入四张卡。18条字段记录（enr-14455–enr-14472）均复用既有 Haskell 来源。12条直接 S2 关系候选端点已映射，正式边仍待 S6；sources.csv 与 relations.csv 未改动。本批后 KU=1,738、enrichment=10,722；S4 已登记719组／883条成员映射，待登记4,062组／4,083条。


### S4 archive：Boschini《Ricche Miniere》1733年修订本双候选组登记（2026-10-17）

S3 组 archive-group-boschinis-ricche-miniere-zanetti-1733 的索引候选 cand-2858 与正文候选 cand-10118 已共同映射至一个 archive KU；七条字段记录（enr-14473–enr-14479）复用 Haskell 来源。修订者 cand-2854 仍为 S3 undecided；两条直接关系候选继续待 S6，未新增正式关系。本批后 KU=1,739、enrichment=10,729；S4 已登记720组／885条成员映射，待登记4,061组／4,081条。

### S4 archive：Zatta 致未具名公爵书信（1761）（2026-10-17）

S3 组 `archive-group-zatta-letter-1761` 的 `cand-10024` 与 `cand-10178` 已共同映射至一个 archive KU。第339页注3通过第23页与第338页注2的交叉引用识别同一书信；八条 source_backed 字段复用 Haskell 来源。原信与刊地未独立核实；两条直接关系候选留待 S6，未新增正式关系。本批后 KU=1,740、enrichment=10,737；S4 已登记721组／887条成员映射，待登记4,060组／4,079条。


### S4 archive：Zanetti《Delle Antiche Statue Greche e Romane》（2026-10-17）

S3 组 `archive-group-zanetti-delle-antiche-statue-1740` 的正文题名候选 `cand-10104` 与索引子目候选 `cand-2846` 已映射至一个 archive KU。六条 source_backed 字段复用 Haskell 来源；开始时间1725、出版间隔十五年及出版者 Albrizzi 按原文记录，不换算确切出版年。出版者关系候选留待 S6，未新增正式关系。本批后 KU=1,741、enrichment=10,743；S4 已登记722组／889条，待登记4,059组／4,077条。


### S4 archive：Molinos《Guida Spirituale》文本身份组（2026-10-17）

S3 组 `archive-group-molinos-guida-spirituale-text` 的索引子目候选 `cand-1681` 与正文候选 `cand-5255` 已映射至一个 archive KU。六条 source_backed 字段复用 Haskell 来源；仅确认文本身份，未确认具体刊本。脚注1书名缺失，关系候选留待 S6。本批后 KU=1,742、enrichment=10,749；S4 已登记723组／891条，待登记4,058组／4,075条。

### S4 archive：Marino 描写画家作品的诗组身份组（2026-10-17）

S3 组 `archive-group-c659964650de` 的正文候选 `cand-4464` 与索引子目候选 `cand-1551` 已映射至一个 archive KU。四条 source_backed 字段复用 Haskell 来源；未提供单篇题名、对象或版本，与 *Adone* 及未具名歌曲保持区分。关系候选留待 S6。本批后 KU=1,743、enrichment=10,753；S4 已登记724组／893条，待登记4,057组／4,073条。

### S4 archive：Marino《Adone》单篇文本（2026-10-17）

S3 索引候选 `cand-1549` 已映射至一张 *Adone* archive KU，与 Marino 人物、Poussin 图像组及诗作组分开。五条 source_backed 字段复用 Haskell 来源；两个直接关系候选留待 S6。本批后 KU=1,744、enrichment=10,758；S4 已登记725组／894条，待登记4,056组／4,072条。


### S4 archive：Saint-Non《Voyage Pittoresque》文本身份组（2026-10-17）

S3 组 `archive-group-saint-non-voyage-pittoresque-text` 的正文候选 `cand-10583` 与索引子目候选 `cand-2342` 已映射至一个 archive KU。五条 source_backed 字段复用 Haskell 来源；Dominique De Non 的参与范围及出版版本未确定，直接关系候选留待 S6。本批后 KU=1,745、enrichment=10,763；S4 已登记726组／896条，待登记4,055组／4,070条。

### S4 archive：Salerno《The Picture Gallery of Vincenzo Giustiniani》（2026-10-17）

第2章、第4章引用与第21章书目条目对应至同一 archive KU；六条 source_backed 字段记录 Haskell 所给文章题名、刊物、年份与页码。文章未独立查阅，作者人物候选 `cand-4323` 继续 undecided，两条 `cites` 关系候选留待 S6。本批后 KU=1,746、enrichment=10,769；S4 已登记727组／897条，待登记4,054组／4,069条。


### S4 work：Verrio《A Sea triumph》描述性身份组（2026-10-17）

索引候选 `cand-2762` 与正文候选 `cand-7206` 已映射至一个 work KU；“A Sea triumph”仅作为描述性工作题名，具体作品身份及正式题名未确认。六条 source_backed 字段记录 Haskell 第7章 pp.195–196 的称谓与画面描述。两条直接关系候选留待 S6，未新增正式关系。本批后 KU=1,747、enrichment=10,775；S4 已登记728组／899条，待登记4,053组／4,067条。


### S4 work：Barberini 所购《The Capture of Jerusalem by the Emperor Titus》（2026-10-17）

`cand-4601` 已登记为一张 work KU。Haskell 确认 Francesco Barberini 从 Nicolas Poussin 处购得此画，但未称 Poussin 为创作者；题名为工作译名。注4保留“也许赠予 Richelieu”及散佚报告；第二版本索引候选 `cand-2001` 保持 undecided，不合并。五条直接关系候选待 S6。本批后 KU=1,748、enrichment=10,782；S4 已登记729组／900条，待登记4,052组／4,066条。


### S3 复核：Thomas Baker 胸像跨章复用既有 KU（2026-10-17）

`cand-4436` 从 pending `new` 组改为 `same`，映射至既有[Bernini 的 Thomas Baker 胸像 KU](../units/works/bernini-thomas-baker-bust.md)。第1章价格与注释、第2章 Nicholas Stone 记述和第7章 Baker 本人像描述共同支持同一胸像；Van Dyck 的 Charles I 三人肖像保持区分。Baker 的精确交易角色仍按原文保留待证；既有正式边与新 S2 关系候选不在本次改动。S3 当前 same=1,894（1,040个既有 KU），new=4,965（4,780组）；待登记 S4 为4,051组／4,065条映射。KU=1,748，enrichment=10,782。

### S3 跨章复核：两项作品复用既有 KU（2026-10-17）

`cand-6888` 由 `new` 改为 `same` → [弗兰切斯基尼《Fame》作品 KU](../units/works/baldassare-franceschini-fame-carrying-the-name-of-louis-xiv-to-the-temple-of-immortality.md)：第7章委托记述与第20章 Plate 66、p.402–403 回指同一件作品。`cand-9636` 由 `new` 改为 `same` → [Amigoni《施特赖特肖像》KU](../units/works/amigoni-sigismund-streit.md)：第10章 p.315 图文、Plate 53b 与 p.316 注3的1739年肖像信息对应现有单件作品；四幅肖像的具体指代仍未确定。两条旧 new 组号和理由保留在 alignment 中；未新建 KU、字段或正式关系。

更新后 S3 same=1,896（1,040个既有 KU），new=4,963（4,778组）；待登记 S4 为4,049组／4,063条映射。work 类型 same=237、new=494（479组）；KU=1,748，enrichment=10,782。

复核后重跑 strict-stage 表审计通过：KU=1,748；候选=12,407；alignment=12,645、未链接=0；待登记映射=4,063；`errors=[]`、`s2_missing=[]`。保留待登记 S4、两条既有 source_ref 引用及 S2 语义质量提示。

S3 去向核对确认 12,407 个候选各有一条决定与过程理由；same 指向同类型既有 KU，new 身份组一致且无拆组；conflict、undecided 与 excluded 均未误登记 KU。按类型重算与过程表一致。此为记录去向完整性核对，不构成独立语义验收；8 项冲突与5,440项待证对象仍保留待解决状态。


### S4 archive：Rava《Contributo alla biografia di Pietro Longhi》（1911）（2026-10-17）

`cand-10054` 已登记为 archive KU，七条 source_backed 字段记录书目题名、署名、期刊、卷、年份与页码。作者只按书目署名 `Rava, A.` 记录；七封 Longhi 致 Remondini 信件是独立 archive 候选，另外两篇 Rava 文章也保持各自身份组。本文与信件未独立查阅；S2 引用关系候选留待 S6。本批后 KU=1,749、enrichment=10,789；S4 已登记730组／901条，待登记4,048组／4,062条。

登记后 strict-stage 表审计通过：alignment=12,645、未链接=0、待登记映射=4,062、`errors=[]`、`s2_missing=[]`；该卡 `build_cards.py --preview` 无差异。


### S4 人物身份组登记：Andreosi、Audran、Barbarigo（2026-10-17）

`cand-0104` → `units/persons/francesco-andreosi`；只记录Haskell称为Antenor雕像预定制作者，作品候选仍待决。`cand-0145` → `units/persons/benoit-audran`；同页索引展开Audran为Benoit Audran，插图组候选仍待决。`cand-0182` → `units/persons/caterina-barbarigo`；其1765年要求为Haskell转引，Gaspara Gozzi 与索引 Gozzi, Gasparo 的身份冲突保留。三个S2关系候选未转为正式关系。

本批3组/3条映射；累计已登记733组/904条，待登记4,045组/4,059条；KU=1,752。

### S4 人物身份组登记：Carrara、Damini（2026-10-17）

`cand-3497` → `units/persons/conte-ventura-carrara`，Haskell注2所列1696年书信收信人；原信与Bottari刊本未独立查阅，正式关系待S6。`cand-0898` → `units/persons/vincenzo-damini`，Haskell称其为次要画家，并记其与Giacomo Leoni从Düsseldorf抵达英格兰；相关候选端点仍待登记，未建立正式关系。

本批2组/2条映射；累计已登记735组/906条，待登记4,043组/4,057条；KU=1,754。

### S3复核：Savini跨章重复候选映射既有KU（2026-10-17）

`cand-2377` 由 `new` 改为 `same` → `units/persons/saverio-savini`；`cand-12277` 由 `new` 改为 `same` → `units/archives/savini-gubbio-terms-1608`。二者与既有卡都对应第1章p.9注1同一段Gubbio 1608年、Saverio Savini、Gualandi IV p.60书目锚点；既有人物卡已记录Saverio/SALVIO姓名差异及支持依据，故不另建KU。原new组号和变更理由保存在alignment行；没有新增正式关系。

改判后 same=1,898→1,040个既有KU；new=4,961/4,776组；S4已登记735组/906条，待登记4,041组/4,055条。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-reassessment-saverio-savini-gubbio-terms-20261017)。

### S4 人物身份组登记：Jan Weenix（2026-10-17）

`cand-2807` → `units/persons/jan-weenix`。Haskell第10章称Jan Weenix与Adrian van der Werff受Johann Wilhelm邀请前往Düsseldorf；邀请不证明Weenix接受，S2关系候选留待S6，未新增正式关系。Van der Werff候选 `cand-2808` 仍待S4。

本批1组/1条映射；累计已登记736组/907条，待登记4,040组/4,054条；KU=1,755。

### S4 人物身份组登记：Adrian van der Werff（2026-10-17）

`cand-2808` → `units/persons/adrian-van-der-werff`。卡片依据第10章p.283及索引记录其邀约、拒绝正式宫廷职位、季节性专属工作和画作入藏陈述，保留未接受邀约、未证明每年履行及引文发言者未识别等限定。三条S2关系候选留待S6，未新增正式关系。

本批1组/1条映射；累计已登记737组/908条，待登记4,039组/4,053条；KU=1,756。

### S4 人物身份组登记：Gabriel Gruppello（2026-10-17）

`cand-1236` → `units/persons/gabriel-gruppello`。卡片记录Haskell第10章的雕塑家称谓与青铜骑马雕像例证；雕像候选仍待S4，日期与现存地点未知，S2关系候选留待S6且未新增正式关系。

本批1组/1条映射；累计已登记738组/909条，待登记4,038组/4,052条；KU=1,757。

### S4 人物身份组登记：Domenico Zanetti（2026-10-17）

`cand-2860` → `units/persons/domenico-zanetti`。记录Haskell第10章注1的画家身份与为选侯工作的陈述；“de Pigage”后缀及其与Nicolas de Pigage候选的可能关系仍待证，不作姓名合并。关系留待S6，未新增正式关系。

本批1组/1条映射；累计已登记739组/910条，待登记4,037组/4,051条；KU=1,758。

### S4 人物身份组登记：六个直接关系端点（2026-10-18）

`cand-0084` → `../units/persons/francesco-allegrini.md`；`cand-0112` → `../units/persons/antonio-maria-antonazzi.md`；`cand-0115` → `../units/persons/galeazzo-arconato.md`；`cand-0122` → `../units/persons/orazio-arrighi-landini.md`；`cand-0238` → `../units/persons/maffeo-barberini-son-of-taddeo.md`；`cand-0420` → `../units/persons/edme-bouchardon.md`。六组均为S3单候选new组；相关S2关系候选留待S6。Arrighi-Landini索引页码栏为空，且1757/1755年版次对应未解决；本批仅登记书内点名的人物，不将书目信息升级为外部验证。

### S3/S4 人物身份组登记：六个直接关系端点（2026-10-18）

`cand-0425` → `../units/persons/pietro-bracci.md`；`cand-0472` → `../units/persons/lodovico-ottavio-burnacini.md`；`cand-0469` → `../units/persons/simone-buonaccorsi.md`；`cand-0474` → `../units/persons/francesca-bussi.md`；`cand-0476` → `../units/persons/stefano-cadani.md`；`cand-0481` → `../units/persons/giacinto-calandrucci.md`。六组均为单候选new组。cand-0469的p.223提及与索引B.csv#317同页，S3据此将Simone映射到Cardinal Simone Buonaccorsi；母子关系仍待S6。其余关系候选留待S6；未新增正式边。

### S4 人物身份组登记：六个直接关系端点（2026-10-17）

`cand-0488` → `../units/persons/luca-cambiaso.md`；`cand-0491` → `../units/persons/tommaso-campanella.md`；`cand-0493` → `../units/persons/colen-campbell.md`；`cand-0494` → `../units/persons/giovanni-da-campione.md`；`cand-0537` → `../units/persons/antonio-cappello.md`；`cand-0553` → `../units/persons/polidoro-da-caravaggio.md`。六组均为S3单候选new组；Polidoro da Caravaggio以第5、8章全名锚点合并登记。对应S2关系候选留待S6；本批不创建formal relations，也不添加外部身份事实。

### S4 人物身份组登记：六个直接关系端点（2026-10-17）

`cand-0495` → `../units/persons/fabio-canal.md`；`cand-0575` → `../units/persons/giulio-carpioni.md`；`cand-0580` → `../units/persons/ludovico-carracci.md`；`cand-0608` → `../units/persons/francesco-catalano.md`；`cand-0611` → `../units/persons/giampaolo-cavagna.md`；`cand-0613` → `../units/persons/bernardo-cavallino.md`。六组均为S3单候选new组；姓名字段和书内依据可追溯。有关归属、指控、日期、拼写及引文限制见对应卡片。S2关系候选留待S6，本批不创建formal relations。

### S4 人物身份组登记：六个直接关系端点（2026-10-17）

`cand-0637` → `../units/persons/giacomo-ceruti.md`；`cand-0641` → `../units/persons/prince-federico-cesi.md`；`cand-0643` → `../units/persons/philippe-de-champaigne.md`；`cand-0659` → `../units/persons/charles-xii-of-sweden.md`；`cand-0662` → `../units/persons/marcantonio-chiarini.md`；`cand-0663` → `../units/persons/agostino-chigi-il-magnifico.md`。六组均为S3单候选new组；各卡保留对应来源限定。S2关系候选留待S6，本批不创建formal relations。

### S4 人物身份组登记：六个直接关系端点（2026-10-17）

`cand-0745` → `../units/persons/baccio-ciarpi.md`；`cand-0766` → `../units/persons/matteo-da-castello.md`；`cand-0820` → `../units/persons/john-conduitt.md`；`cand-0843` → `../units/persons/arcangelo-corelli.md`；`cand-0849` → `../units/persons/antonio-corradini.md`；`cand-0866` → `../units/persons/antoine-coypel.md`。六组均为S3单候选new组；姓名字段与书内依据可追溯。S2关系候选留待S6，本批不创建formal relations。

### S4人物身份组登记：六个端点（2026-10-17）

`cand-0870` → `../units/persons/pietro-paolo-crescenzi.md`；`cand-0896` → `../units/persons/girolamo-curli.md`；`cand-0921` → `../units/persons/robert-dingley.md`；`cand-0979` → `../units/persons/charles-errard.md`；`cand-0987` → `../units/persons/aniello-falcone.md`；`cand-0994` → `../units/persons/cosimo-fanzago.md`。六组均为单候选S3 new组；索引姓名与书内证据可追溯，身份限定见过程记录。直接关系候选留待S6，本批不创建formal relations。

### S4人物身份组登记：六个直接关系端点（2026-10-17）

`cand-0143` → `../units/persons/gioacchino-assereto.md`；`cand-0243 / cand-0244` → `../units/persons/agostino-barelli.md`；`cand-0245` → `../units/persons/giuseppe-baretti.md`；`cand-0251` → `../units/persons/pietro-santo-bartoli.md`；`cand-0254` → `../units/persons/pietro-basadonna.md`；`cand-0259` → `../units/persons/francesco-bassi-il-cremonese.md`。六组对应七条候选映射，均为new身份组；S2关系候选留待S6，本批不创建formal relations。

### S4人物身份组登记：六个直接关系端点（2026-10-17）

`cand-0286` → `../units/persons/federico-bencovich.md`；`cand-0410` → `../units/persons/francesco-borzone.md`；`cand-0415` → `../units/persons/jacques-benigne-bossuet.md`；`cand-0448` → `../units/persons/abram-breughel.md`；`cand-0460` → `../units/persons/felice-brusasorci.md`；`cand-0464` → `../units/persons/charles-villiers-duke-of-buckingham.md`。六组均为单候选S3 new组；直接关系候选留待S6，本批不创建formal relations。

### S3人物身份组裁决：‘Binchs’与Admiral Byng（2026-10-17）

`cand-0475`（B.csv#323）与`cand-7301`（正文来源拼写）均维持`new`，归入`new-person:admiral-byng-817cd89b59`。第7章p.200注5明言‘Binchs’ must be Admiral Byng；扫描页物理第38页核对了该注与正文注号。本决定仅采用Haskell的书内身份推断，未作外部身份核验；索引未给出名字。身份断言已标为S3证据而非S6实质关系；1719年回那不勒斯、1718年舰队司令身份及de Matteis为其工作仍待S6审查。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-admiral-binchs-byng-identity-20261017)。

### S4人物身份组登记：Admiral Byng（2026-10-17）

`cand-0475`、`cand-7301` → [`units/persons/admiral-byng`](../units/persons/admiral-byng.md)。一张卡、两条S3成员映射；登记索引名与书内来源别名各一条enrichment。书内身份推断未转写为外部身份验证，三项实质候选留待S6，身份断言已作为S3证据关闭。

### S3跨章身份组更正：Angelo Cesi兄弟身份（2026-10-17）

`cand-0639`（托迪主教Angelo Cesi）与`cand-10945`（后记p.400的Monsignor Angelo Cesi）合入`new-person:angelo-cesi-d4e25faff9`。第3章p.69与后记p.400均称其为Cardinal Pier Donato Cesi的兄弟。Treccani DBI证实Angelo为托迪主教、1606年去世，且1586年枢机推荐未成功；书中p.70称‘Cardinal Angelo’的头衔冲突保留为来源问题。当前新组数减少1，S4待登记组减少1、成员映射不变。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-reconcile-cesi-sibling-identity-and-title-only-rationales-20261017)。

### S4人物身份组登记：五个直接关系端点组（2026-10-17）

`cand-0538` → `../units/persons/marshal-caprara.md`；`cand-0559` → `../units/persons/earl-of-carlisle.md`；`cand-0614` → `../units/persons/conte-cavazza.md`；`cand-0615` → `../units/persons/comte-de-caylus.md`；`cand-0639 / cand-10945` → `../units/persons/angelo-cesi-bishop-of-todi.md`。共5组/6条映射；Cesi的p.70头衔冲突保留，Treccani外部记录仅作身份比较。8条直接S2关系候选留待S6，本批无新增formal relations。

### S3/S4跨章身份组登记：Almorò与三所学院（2026-10-17）

已区分Almorò Albrizzi与Almorò Pisani，并将Accademia Albrizziana、Pisani家族私人学院、佛罗伦萨Accademia del Disegno分别登记。cand-8500复用Pisani di Santo Stefano家族KU；cand-1429复用Pietro Longhi KU。cand-0024新增Treccani DBI外部身份行；Longhi条目用于cand-1941与Pisani学院的交叉比对，不借作实体标识。

Albrizzi组织学会、Pisani学院与Almorò的授课／终止、佛罗伦萨学院与展览及Vasari文献等S2候选均留待S6；cand-7977仍S3 undecided，cand-9864仍待S4。未新增正式关系。本批5组/5条候选映射；KU=1823，名称字段=10859。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-almoro-academy-crosschapter-endpoints-20261017)。


### S4人物直接端点登记：Gloucester、Farsetti、Monconys、Mei、Newcastle（2026-10-17）

登记5个已有S3 new单成员人物组，各组对应一个KU；候选映射保留原S3分组号。名称字段仅依据全书索引及对应正文形式，本批未查验外部人物规范记录，也未新增关系。15条直接S2关系候选保留待S6逐条裁决。KU=1828，名称字段总数=10869。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-gloucester-farsetti-monconys-mei-newcastle-20261017)。


### S3跨章复核：Fumiani候选复用既有人物KU（2026-10-17）

cand-1087与索引子项候选cand-1088均映射至既有人物KU units/persons/giannantonio-fumiani；Treccani DBI身份对照和Haskell索引、p.234语境支持同一人物。cand-1087旧S3 new组判断已更正，未新增KU。Giannaritonio OCR形式保留；p.234作品识别仍待证，3条直接关系候选待S6。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-reuse-fumiani-existing-identity-20261017)。


### S4人物直接端点登记：Guidiccioni、Malpighi、Gambarini、Pourbus、Sacchetti（2026-10-17）

登记5个已有S3 new单成员人物组，各组对应一个KU；候选映射保留原S3分组号。名称及描述依据全书索引和对应正文。本批未查验外部人物规范记录，未新增关系；15条直接S2关系候选保留待S6逐条裁决。KU=1833，名称字段总数=10879。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-guidiccioni-malpighi-gambarini-pourbus-sacchetti-20261017)。


### S3索引子项复核：Lorenzo del Rosso组（2026-10-18）

cand-2283、cand-2284已并入cand-2282的new身份组new-person:del-lorenzo-rosso-0ec611aff2；三条候选将在S4映射至同一人物KU。详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。


### S4人物直接端点登记：Rospigliosi、Rossi、Del Rosso、Savelli、Roccatagliata（2026-10-18）

登记5个已有S3 new身份组，其中Lorenzo del Rosso组包含cand-2282、cand-2283、cand-2284三条候选映射。各组只建立一个KU；本批未查验外部人物规范记录，未新增关系；14条直接S2关系候选保留待S6逐条裁决。KU=1838，名称字段总数=10889。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-rospigliosi-rossi-del-rosso-savelli-roccatagliata-20261018)。

### S3人物复核：Baldoini候选复用既有KU（2026-10-18）

cand-0167改判same并映射至既有[Giovanni Gaspare Baldoino KU](../units/persons/gio-gasparo-baldoini.md)；第1章任命注释与该卡已保存的同段来源及姓名变体核对相符，没有新增卡片。

### S3跨章身份裁决：Giovanni Bellini（2026-10-18）

cand-0270的pp.380、410索引映射共同指向Giovanni Bellini，并与另列p.198的Gentile Bellini区分；保留为独立new人物组，待S4登记。


### S4人物直接关系端点登记：Bagnara、Barbarigo、Bellini、Clément（2026-10-18）

登记4个已有S3 new人物组，各组各映射一个候选到一个KU。巴尼亚拉公爵夫人与Abbé Clement保留原书称谓，不补造个人全名；Giovanni Bellini与Gentile Bellini分开。4条直接S2关系候选仍待S6逐条裁决；本批未查验外部身份记录或新增正式关系。KU=1842，新增名称字段=8。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-bagnara-barbarigo-bellini-clement-20261018)。


### S4人物直接关系端点登记：Colonna与Concina（2026-10-18）

登记Filippo Colonna、Prince Francesco Colonna、Don Giuliano Colonna、Marc’Antonio Colonna与Padre Daniele Concina五个S3 new组；候选姓名和头衔按索引及章节原文保留，未据同姓合并或推定额外世系。五条直接S2关系候选仍待S6逐条裁决。未查验外部身份记录、未新增正式关系；KU=1847，名称字段=10。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-colonna-concina-20261018)。


### S4人物直接关系端点登记：Constable、Contarini、Correr、Corsini（2026-10-18）

登记John Constable、Pietro Contarini、Fra Francesco Antonio Correr、Marchese Filippo Corsini与Lorenzo Corsini（Pope Clement XII）五个S3 new身份组。名称、称号和书内语境以索引及正文为准；不扩写外部生平。五条直接S2关系候选继续待S6逐条裁决；Haskell转引的Baldinucci来源未在本批独立查阅。未新增外部身份记录或正式关系；KU=1852，名称字段=10。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-constable-contarini-correr-corsini-20261018)。

### S3身份边界：Daniele Dolfin与Devonshire公爵头衔（2026-10-18）

cand-0926确认为新身份组，与1729年去世的Daniele III、IV分开；cand-0918改列conflict，保留为未拆分头衔候选，暂不登记KU。


### S4人物直接关系端点登记：Dolfin、Douglas、Erlach、Ferdinand Maria、Ferrari（2026-10-18）

登记Daniele Dolfin（Archbishop of Udine）、Hamilton, Marquis of Douglas、Fischer von Erlach、Ferdinand Maria（Elector of Bavaria）与Giovanni Ferrari五个S3 new身份组。对未载全名的对象保留来源称谓；cand-0926与1729年去世的Daniele III、IV区分。五条直接S2关系候选仍待S6逐条裁决。本批无外部身份记录或正式关系；KU=1857，名称字段=10。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-dolfin-douglas-erlach-ferdinand-ferrari-20261018)。

### S3人物复核：Conte Francesco Fontana复用既有KU（2026-10-18）

cand-1046由new改判same，复用[Francesco Fontana人物卡](../units/persons/francesco-fontana.md)。索引名称、Haskell第1章p.17同一书信段落及既有卡记录的书信收信人身份一致；相关1633年书信已映射至该人物端点。不新建重复KU，关系仍按S6核对。


### S4人物直接关系端点登记：Ferretti、Festari、Fiammeri与Carlo Fontana（2026-10-18）

登记Gian Domenico Ferretti、Girolamo Festari、Giovanni Battista Fiammeri与Carlo Fontana四个S3 new人物组。名称、描述和语境均限于索引及所引章节；五条直接S2关系候选仍待S6逐条裁决。本批无外部身份记录或正式关系；KU=1861，名称字段=9。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-ferretti-festari-fiammeri-fontana-20261018)。


### S4人物直接关系端点登记：Forabosco、Fragonard、Furlani、Furnaletto与Gagliardi（2026-10-18）

登记Girolamo Forabosco、Jean Honoré Fragonard、Ventura Furlani、Lodovico Furnaletto与Bernardino Gagliardi五个S3 new人物组。Fragonard第9章p.257的推测语气及Furnaletto经营年限约数按来源保留；八条直接S2关系候选仍待S6逐条裁决。本批无外部身份记录或正式关系；KU=1866，名称字段=10。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-forabosco-fragonard-furlani-furnaletto-gagliardi-20261018)。


### S4人物直接关系端点登记：Galli、Galli-Bibiena、Garganego、Genovesi与Gerbault（2026-10-18）

登记Agnolo Galli、Ferdinando Galli-Bibiena、Girolamo Garganego、Antonio Genovesi与Francesco Gerbault五个S3 new人物组。购画及书信信息保留转引状态，Garganego的嵌套题献和Genovesi优先权说法均按来源归属表述；五条直接S2关系候选仍待S6逐条裁决。本批无外部身份记录或正式关系；KU=1871，名称字段=10。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-galli-garganego-genovesi-gerbault-20261018)。


### S4人物直接关系端点登记：Gherardi、Ghibbesio、Giannone、Girardon与Giustiniani（2026-10-18）

登记Antonio Gherardi、Jacopo Ghibbesio、Pietro Giannone、François Girardon与Andrea Giustiniani五个S3 new人物组。Gherardi与既有Pietro Ercole Gherardi不作姓氏推断合并；Giustiniani婚姻保留为来源中的预期安排。六条直接S2关系候选仍待S6逐条裁决。本批无外部身份记录或正式关系；KU=1876，名称字段=10。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-gherardi-ghibbesio-giannone-girardon-giustiniani-20261018)。


### S4人物直接关系端点登记：Giustiniani、Gozzi、Grassi与Greiffenklau（2026-10-18）

登记Benedetto Giustiniani、Girolamo Ascanio Giustiniani、Carlo Gozzi、Orazio Grassi与Karl Philip von Greiffenklau五个S3 new人物组。Giustiniani家族候选保持为不同人物；Gozzi作品未具名，Grassi任命者与Greiffenklau短期前任仍未识别。八条直接S2关系候选仍待S6逐条裁决。本批无外部身份记录或正式关系；KU=1881，名称字段=10。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-giustiniani-gozzi-grassi-greiffenklau-20261018)。

### S3人物复核：Doge Grimani与Earl of Halifax保留职衔型书内身份（2026-10-18）

cand-1234与cand-1286仍为source-local new组，但裁决理由更正为来源只提供职衔／称谓，不提供完整个人姓名。Doge Grimani只按1745年重建语境登记，且与通称Doge职务候选及Cardinal Grimani候选分开；Earl of Halifax不映射至外部命名的继承人。两项无新KU、外部身份行或正式关系；cand-1233仍待S3。

### S3人物：H段跨章身份组复核（2026-10-18）

复核cand-1287、1288、1291、1293、1294、1296–1303共13个人物候选，均有可追溯的new身份组；其中Count Harrach、Lord Hervey和Horace由undecided改为new。Count Harrach映射至Aloys Thomas Raimund Harrach，Lord Hervey映射至John Hervey, 2nd Baron Hervey；Horace指罗马诗人，与Horace Walpole分开。新增4条外部身份记录，来源只用于身份消歧。13个new组待S4登记；9条直接S2关系候选仍待S6，cand-9220作品组继续单独待证。


### S3人物跨章身份组：St Ignatius与两位Leopold（2026-10-18）

cand-1309改为St Ignatius（耶稣会创立者）的new人物组；cand-1397与cand-8097合为Pietro Leopoldo（托斯卡纳大公）一个new组；cand-1398确定为另一位、1658–1705年在位的HRE Leopold I并建独立new组。新增3条外部身份记录；共14条直接S2关系候选仍待S6。身份来源和边界见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-ignatius-leopold-crosschapter-groups-20261018)。未创建KU或正式关系。


### S4人物登记：H段跨章身份组（2026-10-18）

登记Juan van der Hamen、George Frederick Handel、Aloys Thomas Raimund Harrach、Theodor Helmbreker、Henri III、Henrietta Maria、Sir Robert Hervey、John Hervey, 2nd Baron Hervey、Johann Lucas von Hildebrandt、Samuel Hill、William Hogarth、Gerrit van Honthorst与Horace共13个人物组。九条直接S2关系候选仍待S6；四条外部身份行映射到相应KU。Canaletto为Sir Robert Hervey绘制的二十幅景观候选cand-9220保持独立待证；本批未新增正式关系。KU=1894，名称字段=26，外部身份导航行=4。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-h-section-20261018)。


### S4人物直接端点登记：Ignatius与两位Leopold（2026-10-18）

登记Ignatius of Loyola、Pietro Leopoldo（cand-1397与cand-8097共用一KU）及Holy Roman Emperor Leopold I三组人物身份。本批4条候选映射、3条外部身份行和14条直接S2关系候选；身份外证仅用于消歧，关系仍待S6，未新增正式边。当前KU=1897；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-ignatius-leopold-groups-20261018)。


### S4人物直接端点登记：Huber、Imperiali、Jabach、James III与Johann Georg III（2026-10-18）

登记Jean Huber、Francesco Imperiali、Everard Jabach、James III of England与Johann Georg III of Saxony五个人物组。本批5条候选映射、10条source_backed名称字段和5条直接S2关系候选；均保留原书来源限定，关系待S6，未新增正式边。KU=1902；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-huber-imperiali-jabach-james-johann-20261018)。


### S4人物直接端点登记：John Sobieski、Inigo Jones、La Fosse、Langetti与Le Blon（2026-10-18）

登记John Sobieski、Inigo Jones、Charles de la Fosse、Giovanni Battista Langetti与Jakob Christoffel LeBlon五个人物组。本批5条候选映射、10条source_backed名称字段和7条直接S2关系候选；保留Langetti的书内年代矛盾、La Fosse的转引及推测语气、Le Blon的拼写与归属限定。关系待S6，未新增正式边。KU=1907；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-john-sobieski-leblon-batch-20261018)。


### S4人物直接端点登记：Le Nain、Le Vau、Lelli、Lely与Lorca（2026-10-18）

登记Louis Le Nain、Louis Le Vau、Ercole Lelli、Sir Peter Lely与Bernardino Lorca五个人物组。本批5条候选映射、10条source_backed名称字段和6条直接S2关系候选；来源限定与不确定性均保留，关系待S6，未新增正式边。并将cand-1377、cand-1384的派生索引页码从旧快照同步至当前L.csv原行，保留前后值及S3分组不变的依据。KU=1912；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-le-nain-lorca-batch-20261018)。


### S4人物直接端点登记：Loredan、Lorenzi与Lovisa（2026-10-18）

登记Antonio Loredan、Pietro Loredan、Francesco Lorenzi与Domenico Lovisa四个人物组。本批4条候选映射、8条source_backed名称字段及5条直接S2关系候选；关系待S6，未新增正式边。Duke of Lorraine仅有爵号，身份锚点不足，记为S4待证且不创建KU。KU=1916；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-loredan-lovisa-batch-20261018)。


### S4人物直接端点登记：Maffei、Magalotti、Magnasco、Magni与Maidalchini（2026-10-18）

登记Francesco Maffei、Lorenzo Magalotti、Alessandro Magnasco、Pietro Magni与Francesco Maidalchini五个人物组；本批5条候选映射、10条source_backed名称字段及6条直接S2关系候选。关系均留待S6，未新增正式边；中文显示名均为工作音译。KU=1921；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-maffei-m-20261018)。


### S3复核与S4人物直接端点登记：N索引组（2026-10-18）

Benedict Nicolson候选cand-1741由new更正为same，复用既有Lionel Benedict Nicolson KU。另登记Balthasar Neumann、François Sublet de Noyers、Maréchal de Noailles、François Nomé、Pietro Negri、Vincenzo Neri与Francesco Novelli七个人物组；本批7条new候选映射、14条source_backed名称字段及9条直接S2关系候选。关系均留待S6，未新增正式边；中文显示名均为工作音译。KU=1928；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-n-section-20261018)。


### S3复核与S4人物直接端点登记：O索引组（2026-10-18）

登记Roberto Oderisi、Livio Odescalchi、Pietro Paolo Olivieri、Gilles-Marie Oppenord、Alessandro Orsini与William Young Ottley六个人物组；本批6条new候选映射、12条source_backed名称字段及7条直接S2关系候选。关系均留待S6，未新增正式边；中文显示名均为工作音译。KU=1934；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-o-section-20261018)。


### S3复核与S4人物直接端点登记：P索引前段组（2026-10-18）

登记Pietro Paltronieri、Senator Francesco Panciatichi、Domenico Antonio Parodi、Lorenzo Pasinelli、Leonardo Pasquetti、Padre Jacopo Pedozzi与Giovanni del Pian七个人物组；本批7条new候选映射、15条source_backed名称字段及10条直接S2关系候选。关系均留待S6，未新增正式边；中文显示名均为工作音译。KU=1941；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-p-early-section-20261018)。


### S3复核与S4人物直接端点登记：P索引中段组（2026-10-18）

登记Bernard Picart、Antonio Pignatelli（Pope Innocent XII）、Carlo Antonio Pilati、Giuseppe Pinacci、Francesco Piranesi、Baron de Pöllnitz、Edward Poore与Giacomo della Porta八个人物组；本批8条new候选映射、22条source_backed名称字段及13条直接S2关系候选。关系均留待S6，未新增正式边；Pöllnitz只保留书内头衔与姓氏，Poore外部身份与拍卖归属未核。KU=1949；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-p-middle-section-20261018)。


### S3理由校正与S4人物直接端点登记：P索引末段（2026-10-18）

登记Ercole Procaccini、Samuel Pufendorf与Scipione Pulzone三个source-local人物组。修正cand-2064、cand-2069、cand-2072的S3证据表述，保留new决定；三条直接S2关系候选留待S6，未新增正式关系。KU=1952；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-p-late-section-20261018)。


### S3理由校正与S4人物直接端点登记：Q-R索引前段（2026-10-18）

登记Luigi Quaini、Don Vincenzo Radicchio、Ferdinando Raggi、Vincenzo Ranuzzi与Francesco Redi五个source-local人物组；修正五条S3证据表述并保留new决定。8条直接S2关系候选留待S6，未新增正式关系。KU=1957；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-qr-early-20261018)。


### S3理由校正与S4人物直接端点登记：Q-R索引中段（2026-10-18）

登记Lodovico Rezzonico、Don Ferdinando Afan de Ribera、Francesco Maria Ricchini、Abbé Richard与Hyacinthe Rigaud五个source-local人物组；校正五条S3证据说明，保留new决定。6条直接S2关系候选留待S6，未新增正式关系。KU=1962；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-qr-middle-20261018)。


### S3家族身份组校正与S4登记：del Rosso三代人物（2026-10-18）

登记Andrea del Rosso（兄弟三人之祖父）、Antonio del Rosso与Giovanni Battista del Rosso三个source-local人物组；保留祖父与孙辈同名者的分代裁决，并修正两条正文姓名证据说明。4条直接S2关系候选留待S6，未新增正式关系。KU=1965；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-del-rosso-family-20261018)。


### S3身份复用与S4人物端点登记：Rossano公主及Rossi（2026-10-18）

cand-2267由标题身份new改为复用Olimpia Aldobrandini既有KU，并将1643委托叙述与该KU记载的1647婚期保留为待核时间差异；Domenico Rossi、Luigi de' Rossi、Pellegrino de' Rossi分别登记为三个source-local人物组。六条直接S2关系候选均留待S6；未新增正式关系。KU=1968；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-princess-rossi-20261018)。


### S3人物身份组理由校正与S4登记：Rota、Rovere、Rowlandson（2026-10-18）

登记Giovanni Battista Rota、Vittoria della Rovere、Thomas Rowlandson三个source-local人物组，分别保留采购、私人物品继承、画法转用三条S2关系候选待S6。KU=1971；未新增正式关系；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-rota-rovere-rowlandson-20261018)。


### S3身份组交接与S4登记：Grimani、Grosley、Guidi（2026-10-18）

登记Doge Grimani（保留标题形式）、Pierre Jean Grosley（合并索引所指p.301n与p.332书内出现）、Domenico Guidi（合并p.189与p.198书内出现）三个source-local人物组。三条直接S2关系候选留待S6；未新增正式关系。KU=1974；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-grimani-grosley-guidi-20261018)。


### S3身份复核与S4人物登记：Gustav III、Halifax与Leopold of Lorraine（2026-10-18）

登记Gustav III of Sweden（与Gustavus Adolphus分开）、未具名Earl of Halifax及Leopold, Duke of Lorraine三个new人物组。Lorraine候选由待证改为以Cambridge学术文章支持的身份匹配；Haskell继承请求的表述差异仍留S6，cand-11467仍未分类。三条直接S2关系候选待S6；本批未新增正式关系。名称字段=6，外部身份行=2，KU=1977。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-gustavus-halifax-lorraine-20261018)。


### S4 人物身份组登记：四个直接关系端点（2026-10-18）

`cand-2390` → `../units/persons/luigi-scaramuccia.md`；`cand-5453` → `../units/persons/aloysius-gonzaga.md`；`cand-7716` → `../units/persons/luigi-crespi-author.md`；`cand-10881` → `../units/persons/luigi-spezzaferro.md`。四组均为S3 new，逐组登记一张KU；Luigi Gonzaga/Aloysius Gonzaga别名同一性据梵蒂冈礼仪文本核对。Scaramuccia相关作品cand-2391、Spezzaferro文章cand-10882和各关系候选维持独立S3/S6去向；Luigi Crespi关于佛罗伦萨停留的书内说法仍有冲突且未独立核读。

### S4 人物身份组登记：四个直接关系端点（2026-10-18）

`cand-1506` → `../units/persons/francesco-mancini.md`；`cand-1511` → `../units/persons/eustachio-manfredi.md`；`cand-1538` → `../units/persons/raffaelo-marchesi.md`；`cand-1541` → `../units/persons/giovanni-marchiori.md`。四组均为S3 new，逐组登记一张KU，相关关系候选待S6。Marchesi书后索引的Raffaelo与正文的Raffaele拼写差异已保留；此批不认定规范拼法，不新增外部来源或正式关系。

### S4人物身份组登记：Mari、Maria Teresa、Martinelli与Mascardi（2026-10-18）

`cand-1543` → `../units/persons/cosimo-mari.md`；`cand-1545` → `../units/persons/maria-teresa-holy-roman-empress.md`；`cand-1553` → `../units/persons/domenico-martinelli.md`；`cand-1560` → `../units/persons/agostino-mascardi.md`。四组均为S3 new，各登记一张KU；关系候选留待S6。Maria Teresa正文称名与索引称号并列保留；Cosimo Mari的遗嘱依据仍按S2待核记录处理，Martinelli的原文不延伸为工程完成或合同事实，Mascardi的因果性与任职内容保留为Haskell报告而未独立核实。未新增外部来源或正式关系。

### S4人物身份组登记：Mattei、Mazenta、Mazzoni与Menzini（2026-10-18）

`cand-1580` → `../units/persons/tommaso-mattei.md`；`cand-1601` → `../units/persons/ambrogio-mazenta.md`；`cand-1603` → `../units/persons/nicola-mazzoni.md`；`cand-1653` → `../units/persons/benedetto-menzini.md`。四组均为S3 new，各登记一张KU；关系候选留待S6。Nicola Mazzoni索引主条与脚注的Niccola拼写均保留，脚注所涉信件仍按Haskell转引Nuti（1941）的范围记录；未新增外部来源或正式关系。

### S3人物身份复核：Mario Minniti姓名异形复用（2026-10-18）

cand-1671由new改判same，映射至既有Mario Minniti KU。M.csv的“Minitti, Mario”与第1章脚注的“Mario Minnitti”指向同一页9n材料；既有卡已保存该精确Haskell引文并将Minnitti记录为来源拼写异形。未新增KU或外部来源；Agnello转引材料/原始合同仍未独立核读，关系候选留待S6。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-mario-minnitti-reuse-20261018)。

### S4人物身份组登记：Mercati、van Mieris与Morice（2026-10-18）

`cand-1654` → `../units/persons/giovanni-battista-mercati.md`；`cand-1663` → `../units/persons/frans-van-mieris.md`；`cand-1702` → `../units/persons/sir-william-morice.md`。三组均为S3 new，各登记一张KU；关系候选留待S6。van Mieris仅记载为书中所述历史归属对象；Morice的购买对象限于已完成作品；Mercati身份来自Haskell脚注，所引材料未独立核查。未新增外部来源或正式关系。

### S4人物身份组登记：Morlaiter、Morris、Moscheni与de Mura（2026-10-18）

`cand-1703` → `../units/persons/michelangelo-morlaiter.md`；`cand-1707` → `../units/persons/roger-morris.md`；`cand-1708` → `../units/persons/pietro-moscheni.md`；`cand-1716` → `../units/persons/francesco-de-mura.md`。四组均为S3 new，各登记一张KU；Morlaiter正文姓氏与索引全名并列记录，Morris未被写作图片作者，Moscheni关系候选分开保留，de Mura地域描述不扩展为机构归属。候选关系留待S6，未新增外部来源或正式关系。

### S4人物身份组登记：Murray、Nadal、Novelli与Noyelle（2026-10-18）

`cand-1719` → `../units/persons/john-murray-resident.md`；`cand-1721` → `../units/persons/jerome-nadal.md`；`cand-1757` → `../units/persons/pietro-novelli-il-monrealese.md`；`cand-1763` → `../units/persons/charles-de-noyelle.md`。四组均为S3 new，各登记一张KU；Pietro Novelli索引别称照录，未凭姓氏与既有Pietro Antonio Novelli合并，历史身份关系待核。`cand-1748` Abbé Nollet因称名不足暂缓S4，不改动其S3决定。

### S4人物身份组登记：Harley、Paciaudi、Paolini与Parigi（2026-10-18）

`cand-1801` → `../units/persons/robert-harley-earl-of-oxford.md`；`cand-1802` → `../units/persons/paolo-maria-paciaudi.md`；`cand-1829` → `../units/persons/pietro-paolini.md`；`cand-1835` → `../units/persons/giulio-parigi.md`。四组均为S3 new，各登记一张KU；Paolini的作品归属候选保留待S6核对，未新增正式关系。

### S4人物身份组登记：Passante、Perugino、Perusini与Pesne（2026-10-18）

`cand-1854` → `../units/persons/bartolommeo-passante.md`；`cand-1883` → `../units/persons/pietro-perugino.md`；`cand-1884` → `../units/persons/giovanni-perusini.md`；`cand-1888` → `../units/persons/antoine-pesne.md`。四组均为S3 new，各登记一张KU；Perugino跨章称名由同一索引条目连接，Pesne的朋友关系候选保留待S6。

### S4人物身份组登记：Philip II、Piccino、Pompeati与della Porta（2026-10-18）

`cand-1895` → `../units/persons/philip-ii-of-spain.md`；`cand-1926` → `../units/persons/jacopo-piccino.md`；`cand-1972` → `../units/persons/domenico-pompeati.md`；`cand-1977` → `../units/persons/guglielmo-della-porta.md`。四组均为S3 new，各登记一张KU；Piccino来源归属保留推测语气，della Porta创作关系候选留待S6。

### S4人物身份组登记：Pozzi、Puget、Querini与Rainaldi（2026-10-18）

`cand-2032` → `../units/persons/luigi-pozzi.md`；`cand-2070` → `../units/persons/pierre-puget.md`；`cand-2087` → `../units/persons/giacomo-querini.md`；`cand-2092` → `../units/persons/carlo-rainaldi.md`。四组均为S3 new，各登记一张KU；来源原有语境均予保留，未创建正式关系。

### S3复核与S4人物登记：Sagredo三位人物（2026-10-18）

`cand-2326` → `../units/persons/gherardo-sagredo.md`；`cand-2327` → `../units/persons/niccolo-sagredo.md`；`cand-2328` → `../units/persons/stefano-sagredo.md`。三位均为各自独立的S3 new身份组，各登记一张KU；Niccolò与Gherardo的外部身份对应已记录，Stefano的Princeton馆藏沿革映射仍为undecided，书内索引、注释及页图拼写差异保留。Princeton记录与Haskell对Zaccaria生年（1633／1653）的记载不一，且Princeton对Gherardo列1691–1738，Haskell称其1738年去世时49岁；日期与年龄差异留待S5事实核验，不作为身份冲突裁决。五条关系候选留待S6，不新增正式关系。


### S4 人物身份组登记：S索引四个直接端点（2026-10-18）

cand-2396 → ../units/persons/georg-friedrich-schmidt.md；cand-2397 → ../units/persons/friedrich-karl-schonborn.md；cand-2398 → ../units/persons/johann-philip-franz-schonborn.md；cand-2399 → ../units/persons/lothar-franz-von-schonborn.md。四个S3 new单候选身份组各登记一个KU；Schönborn三人按各自全名分别保留。本批涉及的S2关系候选继续待S6；书信原件与引文依据保留各自核读限制。未新增外部来源或正式关系。


### S3跨章人物身份归并：Brusoni与Canal/Canale（2026-10-18）

cand-0462复用既有Girolamo Brusoni KU；cand-0496与cand-0497合并为待S4登记的new组new-person:canal-gerolamo-1e30c99339。判断依据、撤回组号、Canal/Canale拼写及与Canaletto、Fabio Canal的边界见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-brusoni-canal-cross-chapter-20261018)与alignment.csv。相关S2关系候选留待S6，未新增正式关系。


### S3 person：Rosalba Carriera索引子项复用（2026-10-18）

五个只含同一人物主项及其子目的索引候选改为same并指向既有Rosalba Carriera人物KU；1793年日记刊本与Winter作品候选保持独立。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-rosalba-carriera-index-subentries-20261018)及alignment.csv。


### S3 person：Angelo Querini索引子项复用（2026-10-18）

八个同一人物主项下的索引候选改为same并指向既有Angelo Querini人物KU；相邻人物、事件、地点及子目关系范围保持分开。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-angelo-querini-index-subentries-20261018)及alignment.csv。


### S3 person：Joseph Smith跨章索引身份组复用（2026-10-18）

12条同一人物主项下的索引子目现映射至既有Joseph Smith人物KU；索引中涉及的档案、作品、事件、地点、主题与其他人物均保留各自候选及当前决定。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-joseph-smith-index-subentries-20261018)及alignment.csv。


### S3 person：Grand Prince Ferdinand跨章索引身份组复用（2026-10-18）

10条人物主项下的索引子目现映射至既有Grand Prince Ferdinand人物KU；画家、地点、术语、展览程序及收藏候选保留各自类型和决定。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-ferdinand-tuscany-index-subentries-20261018)及alignment.csv。


### S3 person：Schulenburg跨章同一性与重复KU合并（2026-10-18）

cand-2401及五条人物索引子目均映射至既有人物KU；其重复S4卡已合并来源后撤下，原正式关系端点保持不变。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-schulenburg-duplicate-ku-reconciliation-20261018)及alignment.csv。


### S3 person：Oliva人物索引子目身份归组（2026-10-18）

四条人物型交叉索引子目现映射至既有Gian Paolo Oliva人物KU；索引中涉及的其他人物与书内往来继续保留各自身份及证据状态。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-oliva-index-subentries-20261018)及alignment.csv。


### S3 person：Albrizzi人物索引子目身份归组（2026-10-18）

三个描述Bossuet版、威尼斯指南及Zanetti宝石目录的person型索引子目现映射至既有Giovanni Battista Albrizzi人物KU；出版物对象、身份外的事实与正式关系仍各守其证据状态。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-albrizzi-index-subentries-20261018)及alignment.csv。


### S3 person：Bellori人物索引子目身份归组（2026-10-18）

三个有关其任职、Raphael及艺术观点的person型索引子目现映射至既有Bellori人物KU；卡片事实范围、其他人物身份及正式关系均不由索引交叉项扩写。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-bellori-remaining-index-subentries-20261018)及alignment.csv。


### S3 person：A. M. Zanetti the Younger 跨章身份组（2026-10-18）

`cand-2854`（UVWXYZ.csv#191）、`cand-2856`（#193，p.343）及 `cand-2857`（#194，p.329）现为同一待登记 new-person 组 `new-person:anton-maria-zanetti-younger-1706-1778`。第13章 p.345 明称 Antonio Maria the Younger 为年长同名堂兄的年轻表亲；p.343 和第10章 p.329 分别以 “the younger A. M. Zanetti” 与 “A. M. Zanetti the Younger”指称此人。Treccani DBI 的身份对照记录及访问日期见 alignment.csv。既有 Zanetti the Elder KU 保持独立。`cand-2855`、`cand-2858` 是不同 archive 对象，`cand-2859` 是 work 对象，不并入人物组；相应书内关系候选仍待 S6。此前的待证理由保留于alignment历史注释，不新增KU或正式关系。

### S3 person/archive：Moschini跨章人物与1924年文献归组（2026-10-18）

- `cand-1709`与`cand-9820`裁为 `new`，归入 `new-person:giannantonio-moschini-1773-1840`；外部身份依据记录在 `aln-12675`。Treccani DBI给出Giannantonio Moschini全名、司铎身份及其1924年《Dell’incisione in Venezia》线索，书内索引与第16章p.375的“Abate G. A. Moschini”、第10章p.327的1924年姓氏引文相合；[Treccani DBI条目](https://www.treccani.it/enciclopedia/giannantonio-moschini_%28Dizionario-Biografico%29/)。
- `cand-9561`、`cand-9821`、`cand-9886`、`cand-10191`、`cand-10220`、`cand-10587`裁为同一1924年出版物身份组 `archive-group-ec73462cbd49`；引用页未独立查阅，KU待S4登记。
- `cand-8658`（V. Moschini）继续待证；`cand-10605`（Epistolario Moschini）保持独立档案对象。书内关系候选未改写，仍待S6。
- 详情、原S2未决理由及历史组号见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-giannantonio-moschini-person-and-1924-publication-20261018)。当前总计：new=4,968/4,767组，undecided=5,372；S4待登记3,660组/3,683条候选映射。

### S3 person：V. Moschini 跨章新身份组（2026-10-18）

`cand-8658`（第9章 p.265 注5、第10章 p.277 注5中的“V. Moschini”）由 `undecided` 改为待登记的 `new-person:vittorio-moschini-1896-1976`。两处分别引用 1956 年 *Pietro Longhi* 与 1954 年 *Canaletto*；第21章书目列出这两部出版物。美国国家美术馆的馆藏书目分别把对应作者写为 Vittorio Moschini（[《The Faint》书目](https://www.nga.gov/artworks/204-faint)、[《Entrance to the Grand Canal from the Molo, Venice》书目](https://www.nga.gov/artworks/32589-entrance-grand-canal-molo-venice)）；BiblioToscana记录其全名与1896–1976年生卒（[《La pittura italiana del Settecento》目录记录](https://biblio.toscana.it/catalogo/record/a_pittura_italiana_del_settecento_moschini_vittorio_1896_1976_1931_nemi_novissima_enciclopedia_monografica_illustrata-prato_XABPO0017420)）。外部依据及访问日期见 `alignment.csv` 的 `aln-12676`–`aln-12677`。

此人物与 Giannantonio Moschini（1773–1840）分开；`cand-8643` 和 `cand-9295` 仍各自标识 *Pietro Longhi* 与 *Canaletto* 两部文献，`cand-10605` 仍是独立 *Epistolario Moschini* 档案对象。引用内容、作品位置与论证未据此核实，书内关系候选未改写；本组待 S4 登记。当前对齐为12,674行，其中12,407条候选决定与267条外部身份记录；全书 `new=4,969`/4,768组、`undecided=5,369`，S4待登记3,661组/3,684条映射。

### S3 place：John Strange 在 Paese 的别墅跨章复用（2026-10-18）

`cand-11524`（图版64说明中的Paese别墅）与 `cand-11546`（第16章 p.374 所称Treviso附近乡间住宅）均 `same` → 既有[洛雷丹别墅（Villa Loredan, Paese）](../units/places/villa-loredan-paese.md)。National Gallery称Villa Loredan为Strange在Paese的乡间住宅；Met所录题记把Villa Loredan近Treviso与Paese及John Strange联系起来（[National Gallery记录](https://www.nationalgallery.org.uk/paintings/francesco-guardi-villa-del-timpano-arcuato-at-paese)、[Met馆藏记录](https://www.metmuseum.org/art/collection/search/338929)）。`cand-11524`还与已接受的图版64作品候选共用来源，既有作品到Villa Loredan的 `has_subject` 端点见 `rel-0698`。来源与访问日期见 `alignment.csv` 的 `aln-12678`–`aln-12680`。

本决定复用同一物理地点，不把图版64与某件具体馆藏画作配对；第16章所述画作临时存放在该处也未由外部记录验证。当前全书same=1,960（指向1,046个KU），new=4,969/4,768组，conflict=9，excluded=100，undecided=5,369；S4待登记3,661组/3,684条候选映射。alignment为12,677行，其中12,407条候选决定、270条外部身份记录。

### S3 archive：Baldinucci《Notizie》卷 VI（1728）跨章新身份组（2026-10-18）

`cand-4846`（第1、2、4、5、6、7、8章的卷VI引文）与 `cand-8601`（第9章 p.263–264 注7，卷VI p.421）现归为新 archive 组 `archive-group-baldinucci-notizie-vol-vi-1728`。第21章 p.413 书目将该卷列为 Filippo Baldinucci, *Notizie de’ Professori del disegno da Cimabue in qua, Secolo V dal 1610 al 1670*, vol. VI, Firenze 1728；两候选的卷次与年份匹配该条。详见[对齐行](../tables/alignment.csv)及[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-baldinucci-notizie-vol-vi-1728-cross-chapter-20261018)。

此裁决只确认引文指向同一书目卷册；页码内容和相关历史主张未独立核验，KU待S4登记。卷IV/1688、卷V/1702、未指明卷册的艺术史称谓，以及1948年《Bernini》传记均保持分立或待证。当前全书same=1,960（1,046个既有KU）、new=4,971/4,769组、conflict=9、excluded=100、undecided=5,367；S4待登记3,662组/3,686条候选映射。

### S3 archive：Passeri《Vite》Jacob Hess 1934版跨章新身份组（2026-10-18）

`cand-4376`、`cand-5749`、`cand-6241` 现归为新 archive 组 `archive-group-passeri-vite-hess-1934`。第21章 p.433 书目完整列出 G. B. Passeri《Vite de’ Pittori Scultori et Architetti dall’anno 1641 sino all’anno 1673》，Jacob Hess 编，Leipzig und Wien 1934。第6章 p.146 注2 的 p.301 与 `cand-4376` 的第2章 p.301 引文相同；第4章 `cand-5749` 的 p.107、p.187及 ibid. p.186 引文与同一书目项相符。跨章 mention、statement 和原决定均留在[对齐表](../tables/alignment.csv)，裁决比较与边界见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-passeri-vite-hess-1934-cross-chapter-20261018)。

本决定只确认所引出版物身份；引文页未阅读，正文主张未据此验证；KU待S4登记。作者人物KU不充作文献卡；题名、责任者不同的 `cand-7502` 保持独立。全书当前 `same=1,960`（1,046个既有KU）、`new=4,974`／4,770组、`conflict=9`、`excluded=100`、`undecided=5,364`；S4待登记3,663组／3,689条候选映射。


### S3 archive：Orbaan《Documenti sul Barocco in Roma》（1920）跨章新身份组（2026-10-18）

`cand-4373` 现归入新 archive 组 `archive-group-orbaan-documenti-barocco-1920`。第21章书目完整列出 J. A. F. Orbaan, *Documenti sul Barocco in Roma*, Roma 1920；第2–4章引文的作者、年份与书目相符，来源锚点见[对齐行](../tables/alignment.csv)与[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-orbaan-documenti-barocco-1920-cross-chapter-20261018)。

1631年 Barberini 清单、1608年 Avviso 与 Orbaan 1914–15 年论文保持独立；本裁决只确认1920年书目身份，所引页码未读、KU待S4登记。当前全书 `new=4,975`／4,771组、`undecided=5,363`，S4待登记3,664组／3,690条候选映射。


### S3 archive：Wittkower与Ruffo三项跨章书目身份（2026-10-18）

- `cand-4383` → 新组 `archive-group-wittkower-sculptures-bernini-1955`：第21章书目列明 *The sculptures of Gian Lorenzo Bernini*（London, 1955），第2、7章引文与书目相符。
- `cand-4557` → 新组 `archive-group-wittkower-art-architecture-1958`：书目列明 *Art and architecture in Italy 1600 to 1750*（London, 1958），第1–7章引用与年份及同书 ibid. 定位相符；与Wittkower 1955年专著分开。
- `cand-6454` → 新组 `archive-group-ruffo-galleria-1916`：书目列明 V. Ruffo 文章《La galleria Ruffo nel secolo XVII in Messina》，*Bollettino d’Arte* X（1916）；第1、6、8章短引与之相合。引用该文的独立书信KU不并入文章组。

对齐行保留书目statement、所有候选提及与原未决理由；具体比较见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)。三项只确认书目身份，未读引文页，均待S4登记。当前全书 `new=4,978`／4,774组、`undecided=5,360`；S4待登记3,667组／3,693条候选映射。

### S3 archive：四项跨章书目身份（2026-10-18）

- `cand-4633` → `archive-group-poussin-blunt-exhibition-1960`：Poussin 1960年展览目录，第2、4章引文与第21章书目相符。
- `cand-9456` → `archive-group-garas-pellegrini-deutschland-1971`：Garas关于Pellegrini在德国的1971年论文，第10、20章引文与书目相符。
- `cand-8815` → `archive-group-battistella-gaetano-zompini-1930`：Battistella《Gaetano Zompini》（1930），第9、13章页码短引与书目相符。
- `cand-9501` → `archive-group-brunelli-amica-casanova-1923`：Brunelli《Un’amica del Casanova》（1923），第10、15章与书目相符。

四组均为新 archive 身份、待S4登记；各候选引用页未读。完整证据见[对齐表](../tables/alignment.csv)及[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-four-cross-chapter-publication-identities-20261018)。当前 `new=4,982`／4,778组、`undecided=5,356`；S4待登记3,671组／3,697条候选映射。

### S3 archive：Bellori与Claretta两项跨章书目身份（2026-10-18）

- `cand-4805` → `archive-group-bellori-nota-musei-1664`：第21章书目影像记录《Nota delli Musei…》为Lunadoro《Relatione della corte di Roma》的1664年附录，第2、5、6章均以“Nota dei Musei”指引该项。
- `cand-4995` → `archive-group-claretta-reali-savoia-1893`：Claretta关于萨伏依王室赞助艺术的1893年论文，第3、7、10章引用与书目题名及出版项相符。该论文与既有书信所引的Claretta 1885年论文不同。

两项仅确认书目身份，原书及引文页未读，KU待S4登记。当前 `new=4,984`／4,780组、`undecided=5,354`；S4待登记3,673组／3,699条候选映射。

### S3 archive：Pastor 意大利文版卷 XIII 与卷 XIV 跨章身份（2026-10-18）

- `cand-4237` → `archive-group-pastor-storia-dei-papi-vol-xiii`：第2、3、6章一致引用卷 XIII；外部书目支持卷题及其 Gregorio XV／Urbano VIII 时期范围。所用具体印次仍未确定，不将第21章泛称系列条目的 1943 年套用于此卷。
- `cand-4836` → `archive-group-pastor-storia-dei-papi-vol-xiv-parts-i-ii`：第2、3、6章引用卷 XIV；跨章证据涉及 I、II 两部分，按两部分卷 XIV 的书目单元建组，不归入 II 部单册。
- `cand-11414` 继续 `undecided`：第21章 p.433 的系列条目缺卷号，保留为系列／版本级待证对象；不与具体卷册合并。完整 mention、statement 和比较理由见[对齐表](../tables/alignment.csv)与[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-pastor-volumes-xiii-xiv-20261018)。

两项新组只确认书目身份；引文页未独立查阅，KU待S4登记。当前全书 `same=1,960`（1,046个既有KU）、`new=4,986`／4,782组、`conflict=9`、`excluded=100`、`undecided=5,352`；S4已登记1,107组／1,285条候选映射，待登记3,675组／3,701条候选映射。archive 类型当前 `new=1,270`／1,216组、`undecided=722`；S4已登记109组／151条候选映射，待登记1,107组／1,119条候选映射。

### S3 archive：Bottari 卷 I/II、Parker 1948与Smith 1761遗嘱（2026-10-18）

`cand-4830`归入 Bottari/Ticozzi Milano 1822 卷 I；`cand-6200`、`cand-7516`、`cand-8584`统一归入 Bottari/Ticozzi 卷 II；`cand-9484`归入 Parker 1948 年 Windsor Canaletto 图录；`cand-8651`归入独立的 Smith 1761 遗嘱文献件。第19章 Parker pp.61–62 mention 已从遗嘱候选校正到 Parker 书目候选。Blunt 1957 p.12 n.6 与 Pastor 泛称继续待证。书目身份有据；引文页及遗嘱原件未独立查阅，均待S4登记。过程比较、外部书目和原决定见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-bottari-parker-smith-will-20261018)及[对齐表](../tables/alignment.csv)。

当前 S3 `new=4,990`／4,785组、`same=1,960`（1,046个既有KU）、`conflict=9`、`excluded=100`、`undecided=5,348`；S4已登记1,107组／1,285条映射，待登记3,678组／3,705条映射。archive 类型 `new=1,274`／1,219组、`undecided=718`；S4已登记109组／151条映射，待登记1,110组／1,123条映射。计数按候选决策行统计，排除270条外部身份来源记录。

### S3 archive：Bottari 卷 III、V、VI、VII跨章卷册身份（2026-10-18）

`cand-5461`、`cand-9458`、`cand-5503`、`cand-11868`分别归入 Ticozzi《Raccolta》卷 III、V、VI、VII 新组；跨章引文和系列书目相符。卷 V、VI、VII 的 Internet Archive 卷册标识复用既有相应信件卡片记载，信件与出版物分开。各页未独立查阅。全书当前 S3 `new=4,994`／4,789组、`same=1,960`、`conflict=9`、`excluded=100`、`undecided=5,344`；S4已登记1,107组／1,285条映射，待登记3,682组／3,709条映射。archive 类型 `new=1,278`／1,223组、`undecided=714`；待登记1,114组／1,127条映射。详细卷册边界与证据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-bottari-volumes-iii-v-vii-20261018)和[对齐表](../tables/alignment.csv)。

### S3 archive：四项跨章出版物归组与一项版本待证（2026-10-18）

`cand-4635`（Blunt 1945 Windsor 法国素描目录）、`cand-4843`（Bentivoglio《Memorie》第五卷，1807）、`cand-4845`（Callari《I Palazzi di Roma》第三版，1944）及 `cand-4847`（Campori《Lettere artistiche inedite》，1866）均由 `undecided` 改为 `new`，分属四个 archive 身份组并待S4登记；外部馆藏目录记录已绑定各自的来源行。`cand-4354`（Venturi《La R. Galleria Estense in Modena》）仍待证：Haskell书目记1883，已识别数字化本记1882，版本日期未解决。引文页与出版物正文未核验；不新增 KU、关系或补足事实。过程依据及逐项来源见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-blunt-bentivoglio-callari-campori-20261018)，决定见[对齐表](../tables/alignment.csv)。

当前全书 S3 `new=4,998`／4,793组、`same=1,960`（1,046个既有KU）、`conflict=9`、`excluded=100`、`undecided=5,340`；S4已登记1,107组／1,285条候选映射，待登记3,686组／3,713条候选映射。archive 类型 `new=1,282`／1,227组、`undecided=710`；S4已登记109组／151条映射，待登记1,118组／1,131条候选映射。计数按无外部身份副记录的候选决定行统计；严格表审计通过。

### S3 archive：四项跨章书目身份（2026-10-18）

`cand-7066`（Whinney–Millar, *English Art*）、`cand-10878`（Frommel 的 *Storia dell’arte* 论文）、`cand-7584`（Vaes 关于 Corneille de Wael 的期刊论文）及 `cand-9350`（Royal Academy 的 *English Taste* 展览目录）均由 `undecided` 改为 `new`，分别归入四个 archive 身份组并待S4登记；Vaes 的期刊论文和另有分页的抽印本分开。决定证据、外部目录记录及未核验范围见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-whinney-frommel-vaes-english-taste-20261018)及[对齐表](../tables/alignment.csv)。

当前全书 S3 `new=5,002`／4,797组、`same=1,960`（1,046个既有KU）、`conflict=9`、`excluded=100`、`undecided=5,336`；S4已登记1,107组／1,285条候选映射，待登记3,690组／3,717条候选映射。archive 类型 `new=1,286`／1,231组、`undecided=706`；S4已登记109组／151条映射，待登记1,122组／1,135条映射。严格表审计通过；其余 candidate 的身份、复用、冲突和待证去向尚在逐类型处理中。
### S3 archive：Tassi、Petrocchi 与 Constable 三项跨章出版物身份（2026-10-18）

`cand-6590`（Tassi《Vite》第二卷，1793）、`cand-9950`（Massimo Petrocchi，1947）及 `cand-9914`（W. G. Constable，1956论文）均由 `undecided` 改判 `new`，各归入独立 archive 身份组并待 S4 登记。Tassi 卷一候选 `cand-7690` 保持分组边界；三项只裁决书目身份，不核验所引内容。证据与候选映射见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-tassi-petrocchi-constable-archive-identities-20261018)及[对齐表](../tables/alignment.csv)。

当前全书 S3 `new=5,005`／4,800组、`same=1,960`（1,046个既有KU）、`conflict=9`、`excluded=100`、`undecided=5,333`；S4已登记1,107组／1,285条候选映射，待登记3,693组／3,720条候选映射。archive 类型 `new=1,289`／1,234组、`undecided=703`；S4已登记109组／151条候选映射，待登记1,125组／1,138条候选映射。统计排除分立外部身份来源行；严格表审计复核后更新最终计数。

### S3 archive：Tassi 第一卷与 Bjurström 论文两项身份裁决（2026-10-18）

`cand-7690`（Tassi《Vite》第一卷，1793）及 `cand-9445`（Per Bjurström 1967 年论文）由 `undecided` 改判 `new`，各归入独立 archive 身份组并待 S4 登记。Tassi 第一卷与已裁决的第二卷保持卷级边界；两项只确认书目身份，原文和所引内容未核读。裁决依据和映射见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-tassi-vol-i-bjurstrom-archive-20261018)及[对齐表](../tables/alignment.csv)。

当前全书 S3 `new=5,007`／4,802组、`same=1,960`（1,046个既有KU）、`conflict=9`、`excluded=100`、`undecided=5,331`；S4已登记1,107组／1,285条候选映射，待登记3,695组／3,722条候选映射。archive 类型 `new=1,291`／1,236组、`undecided=701`；S4已登记109组／151条候选映射，待登记1,127组／1,140条候选映射。严格表审计复核后更新最终计数。

### S3 archive：Ferrari 1900 年 Algarotti 研究论文身份（2026-10-18）

`cand-9460`（Luigi Ferrari, “Gli acquisti dell’Algarotti pel Regio Museo di Dresda”）由 `undecided` 改判 `new`，归入独立 archive 论文身份组并待 S4 登记；记录指向 *L’Arte* 期刊论文，不推定或登记单行本。书目身份的跨章依据及外部来源见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-ferrari-algarotti-article-1900-20261018)及[对齐表](../tables/alignment.csv)。

当前全书 S3 `new=5,008`／4,803组、`same=1,960`（1,046个既有KU）、`conflict=9`、`excluded=100`、`undecided=5,330`；S4已登记1,107组／1,285条候选映射，待登记3,696组／3,723条候选映射。archive 类型 `new=1,292`／1,237组、`undecided=700`；S4已登记109组／151条候选映射，待登记1,128组／1,141条候选映射。严格表审计复核后更新最终计数。

### S3 archive：Bellotto 展览目录与 Battisti 论文两项身份裁决（2026-10-18）

`cand-9462`（Bellotto/Gierymski 1955 年展览目录）和 `cand-9479`（E. Battisti 1958 年论文）均由 `undecided` 改判 `new`，各归入独立 archive 身份组并待 S4 登记。前者裁定为展览目录，后者裁定为期刊论文；均仅核书目身份，不核验内容主张。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-bellotto-battisti-archive-identities-20261018)及[对齐表](../tables/alignment.csv)。

当前全书 S3 `new=5,010`／4,805组、`same=1,960`（1,046个既有KU）、`conflict=9`、`excluded=100`、`undecided=5,328`；S4已登记1,107组／1,285条候选映射，待登记3,698组／3,725条候选映射。archive 类型 `new=1,294`／1,239组、`undecided=698`；S4已登记109组／151条候选映射，待登记1,130组／1,143条候选映射。严格表审计复核后更新最终计数。

### S3 archive：Viale 论文与 Clemens August 展览目录两项身份裁决（2026-10-18）

`cand-9471`（Viale 关于 Rivoli 的论文）和 `cand-9464`（Brühl 1961 年 Clemens August 展览目录）均由 `undecided` 改判 `new`，各归入独立 archive 身份组并待 S4 登记。Viale 外部书目拼法与本地目录存在一字母差异且略去副标题，过程记录保留此差异；Clemens August 记录指向展览目录，不与同年评论文章混并。两项只裁决书目身份。依据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-viale-clemens-august-archive-20261018)及[对齐表](../tables/alignment.csv)。

当前全书 S3 `new=5,012`／4,807组、`same=1,960`（1,046个既有KU）、`conflict=9`、`excluded=100`、`undecided=5,326`；S4已登记1,107组／1,285条候选映射，待登记3,700组／3,727条候选映射。archive 类型 `new=1,296`／1,241组、`undecided=696`；S4已登记109组／151条候选映射，待登记1,132组／1,145条候选映射。严格表审计复核后更新最终计数。


### S3 person/work：Giorgione 与《Tempesta》跨章分组（2026-10-18）

- `cand-1188` 由 `undecided` 改为独立 new-person 组 `new-person:giorgione-giorgio-da-castelfranco-20261018`；Treccani 支持 Giorgione / Giorgio da Castelfranco 的人物身份，并警示 Barbarelli 姓氏有误。
- `cand-1189` 由 `undecided` 改为 `new`，与 `cand-10695` 共用既有作品组 `workgrp-ab3548af485776`；索引子目和第17、20章同一 Manfrin 收藏的《Tempesta》陈述支持作品身份。人物与作品分开，作者归属仍是原书表述。

严格表审计通过：全书 `new=5,014`／4,808组、`same=1,960`（1,046个既有KU）、`conflict=9`、`excluded=100`、`undecided=5,324`；S4已登记1,107组／1,285条映射，待登记3,701组／3,729条映射。人物类型当前 `new=1,160`、`undecided=1,150`；作品类型 `new=495`、`undecided=1,631`。本批没有登记KU、补足字段或正式关系。证据及旧待决理由见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-giorgione-person-and-tempesta-work-20261018)和[对齐表](../tables/alignment.csv)。


### S3 person：Velasquez 跨章身份复用（2026-10-18）

`cand-2709` 由 `undecided` 改为 `same`，映射到既有人物 KU `units/persons/velasquez`。索引主项跨章出现，第8章注4直接写出 “Diego Velasquez”，与卡片规范名 Diego Velázquez、别名 Velasquez 及已映射候选 `cand-3894` 相合。仅复用人物身份，作品及其归属保留 S2 限定；不新增 KU 或关系。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-velasquez-cross-chapter-person-reuse-20261018)及[对齐表](../tables/alignment.csv)。

当前 S3 `same=1,961`（1,046个既有KU）、`new=5,014`／4,808组、`conflict=9`、`excluded=100`、`undecided=5,323`；S4待登记映射仍为3,729条。严格表审计复核后确认。


### S3 person：Bottari 与 Bellori 人物候选复用（2026-10-18）

`cand-3507` 映射到 Giovanni Bottari 人物 KU：第14章全名、B.csv#264 及已登记索引候选 `cand-0417` 相合。`cand-3535` 映射到 Giovanni Pietro Bellori 人物 KU：B.csv#119 全名主项、跨章引文语境及已映射候选组支持复用。引文所指书信、刊本及人物著作维持 archive 与 person 粒度边界，相关编者关系仍留待 S6。

当前 S3 `same=1,963`（1,046个既有KU）、`new=5,014`／4,808组、`conflict=9`、`excluded=100`、`undecided=5,321`；S4待登记映射仍为3,729条。人物类型 `same=1,146`、`new=1,160`、`undecided=1,147`。严格表审计复核后确认。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-bottari-bellori-cross-chapter-person-reuse-20261018)与[对齐表](../tables/alignment.csv)。


### S3 person：Soprani 跨章作者身份新组（2026-10-18）

`cand-3500` 由 `undecided` 改为新人物组 `new-person:raffaele-soprani-20261018`，并与出版物候选 `cand-5160` 保持人物／archive 类型区分。多章卷册引文与第21章 Raffaello Soprani 书目署名相合；Treccani DBI 记载 Raffaele Soprani 的《Le Vite》作者身份与 Ratti 的1768年重印，Braidense 记录明确将 Raffaello 列为 Raffaele 的变体名。只确认人物及责任者身份，原书和被引页未独立阅读，KU待 S4。

当前全书 S3 `same=1,963`（1,046个既有KU）、`new=5,015`／4,809组、`conflict=9`、`excluded=100`、`undecided=5,320`；S4已登记1,107组／1,285条映射，待登记3,702组／3,730条映射。人物类型 `new=1,161`／1,063组、`undecided=1,146`。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-soprani-cross-chapter-person-identity-20261018)和[对齐表](../tables/alignment.csv)。


### S3 person：Cardinal Richelieu 跨章身份新组（2026-10-18）

`cand-2189` 由 `undecided` 改为 `new-person:armand-jean-du-plessis-de-richelieu-20261018`。第2章的法国枢机称谓与第7、18、20章的跨章记述及 Q-R.csv#116 页码项相合；Treccani 支持其规范名 Armand-Jean Du Plessis de Richelieu、枢机身份和1585–1642生卒。尚无同类型人物 KU；人物新组待 S4。身份裁决不验证 Haskell 关于艺术政策与委托的具体陈述。

当前 S3 `same=1,963`（1,047个既有KU）、`new=5,016`／4,810组、`conflict=9`、`excluded=100`、`undecided=5,319`；S4已登记1,107组／1,285条映射，待登记3,703组／3,731条映射。人物类型 `new=1,162`／1,064组、`undecided=1,145`。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-richelieu-cross-chapter-person-identity-20261018)与[对齐表](../tables/alignment.csv)。


<a id="s3-person-arundel-cross-chapter-reuse-20261018"></a>

### S3 person：Lord Arundel 跨章身份复用（2026-10-18）

`cand-0142` 由 `undecided` 改为 `same`，复用人物 KU `units/persons/lord-arundell-coke-correspondent`。第4章 S2 注释给出 Thomas Howard 全名锚点；第7、13章称名与同一收藏家语境相合，且既有人物卡和已映射的 `cand-3071` 提供交叉对应。旧待决理由保留于 alignment 行；索引页码不单独作证。本次沿用卡内已有身份证据，不新增外部来源、知识元或正式关系。

当前全书 S3 `same=1,964`（1,047个既有KU）、`new=5,016`／4,810组、`conflict=9`、`excluded=100`、`undecided=5,318`；S4已登记1,107组／1,285条映射，待登记3,703组／3,731条映射。人物类型 `same=1,147`、`new=1,162`／1,064组、`undecided=1,144`。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-arundel-cross-chapter-reuse-20261018)和[对齐表](../tables/alignment.csv)。


<a id="s3-person-orleans-regent-cross-chapter-new-20261018"></a>

### S3 person：Philippe d’Orléans 跨章摄政者新组（2026-10-18）

`cand-1786` 由 `undecided` 改为新人物组 `new-person:philippe-dorleans-regent-1674-1723-20261018`，待 S4 登记。第7章注释称奥尔良公爵后来成为摄政且于1715年邀请 Solimena；第10、13章是1720年巴黎活动中的摄政者；第15章 p.370 明称 “Régent Philippe d’Orléans”。BnF 人物规范记录 FRBNF11918201 确认其姓名、生卒1674–1723及法国摄政（1715–1723）。仅确认人物身份，画像、绘制、委托等书中陈述不因此获外部验证；与 Anne of Austria 等其他摄政者分立。

当前全书 S3 `same=1,964`（1,047个既有KU）、`new=5,017`／4,811组、`conflict=9`、`excluded=100`、`undecided=5,317`；S4已登记1,107组／1,285条映射，待登记3,704组／3,732条映射。人物类型 `same=1,147`、`new=1,163`／1,065组、`undecided=1,143`。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-orleans-regent-cross-chapter-new-20261018)和[对齐表](../tables/alignment.csv)。


### S3 person：L. A. Muratori 跨章身份新组（2026-10-18）

cand-1717 由 undecided 改为 new-person:ludovico-antonio-muratori-20261018，待 S4 登记。第9、10、13、14章的提及与 Treccani《意大利人传记辞典》身份词条吻合。与 Della pubblica felicità 的 archive 候选分开；不据此验证书信或艺术关系。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-muratori-cross-chapter-new-20261018)与[对齐表](../tables/alignment.csv)。

### S3 person：Lord Burlington 跨章身份新组（2026-10-18）

cand-0470 由 undecided 改为 new-person:richard-boyle-earl-burlington-20261018，待 S4 登记。第10、14章称名与 National Portrait Gallery 的 Richard Boyle, 3rd Earl of Burlington 身份记录相符。只解决人物身份，不验证具体赞助或建筑主张。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-burlington-cross-chapter-new-20261018)与[对齐表](../tables/alignment.csv)。

### S3 person：Voltaire 跨章身份新组（2026-10-18）

cand-2791 由 undecided 改为 new-person:voltaire-francois-marie-arouet-20261018，待 S4 登记；第10、14、15章八处提及对应 BnF 人物规范记录 FRBNF11928669。只确认人物身份，不验证旅行、访问、肖像及思想影响叙述。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-voltaire-cross-chapter-new-20261018)与[对齐表](../tables/alignment.csv)。

### S3 person：Tintoretto 跨章身份新组（2026-10-18）

cand-2627 由 undecided 改为 new-person:jacopo-robusti-tintoretto-20261018，待 S4 登记；第9、10、19章称名与 Treccani 的 Iacopo Robusti detto il Tintoretto 词条相符。只确认人物身份，不验证相关作品归属。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-tintoretto-cross-chapter-new-20261018)与[对齐表](../tables/alignment.csv)。

### S3 person：Marcel Roethlisberger 跨章作者身份新组（2026-10-18）

cand-3502 由 undecided 改为 new-person:marcel-roethlisberger-20261018，待 S4 登记；第1、4、6、7章的书目提及与 BnF 人物规范记录 FRBNF12399359 相合。只确认被引作者身份，不表示已阅读其引文或核验其研究结论。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-roethlisberger-cross-chapter-new-20261018)与[对齐表](../tables/alignment.csv)。


### S3 person：Claude 跨章复用既有人物 KU（2026-10-18）

cand-3481 由 undecided 改为 same，映射至 Claude Lorrain 人物卡。第1、4、6、7章同一风景画家语境与既有卡内第1章原书用例、身份记录相合；沿用现有 KU，不新建人物或关系。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-claude-cross-chapter-reuse-20261018)和[对齐表](../tables/alignment.csv)。


### S3 person：A. Morassi 跨章作者身份新组（2026-10-18）

cand-8257 由 undecided 改为 new-person:antonio-morassi-20261018，待 S4 登记。第9、10、14章引文与第21章书目列出的 A. Morassi 作品及 Getty ULAN 人物记录相符。只裁作者身份，不验证被引研究结论。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-morassi-cross-chapter-new-20261018)与[对齐表](../tables/alignment.csv)。


<a id="s3-person-bertolotti-cross-chapter-new-20261018"></a>

### S3 person：Bertolotti 跨章作者身份新组（2026-10-18）

`cand-3504` 由 undecided 改为 new，归入 `new-person:antonino-bertolotti-20261018`，待 S4 登记。第1、4、5章的引文将 Bertolotti 作为作者；Braidense 目录记录将书目中的 A. Bertolotti 对应为 Antonino Bertolotti，并列 Antonio 为异名；Treccani 传记记录提供同一身份依据。未发现同类型人物 KU。此决定只消歧作者身份，不验证被引作品或 Haskell 的具体陈述；见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-bertolotti-cross-chapter-new-20261018)及[对齐表](../tables/alignment.csv)。


<a id="s4-person-direct-endpoint-batch-20261018"></a>

### S4 person：五组高优先级直接关系端点登记（2026-10-18）

完成Richelieu、年轻的Anton Maria Zanetti、Voltaire、Philippe d’Orléans与Ludovico Antonio Muratori五个S3身份组的S4登记，7条候选映射各指向组内唯一人物KU。五组均为书内关系断言的直接端点，合计49条关系候选保留待S6审查；本批未新增正式关系。卡片保留双语名称、等义描述、章页证据与S3已记录的身份入口。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoint-batch-20261018)、[KU清单](../tables/ku-manifest.csv)及[对齐表](../tables/alignment.csv)。

### S4 person：三组直接关系端点（2026-10-18）

`cand-8465`（Pietro Visconti）、`cand-2668`（John Udney）和`cand-10590`（Jacopo Morelli）各自按既有S3 `new`组登记为一个人物 KU。卡片保留双语名称、书内角色和精确来源定位；John的“Zuane Udni”作为来源转录形式保留。共6条S2关系候选留待S6，没有新增正式关系。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-visconti-udney-morelli-20261018)、[KU清单](../tables/ku-manifest.csv)及[对齐表](../tables/alignment.csv)。

### S4 archive：Passeri《Vite》Jacob Hess 1934版（2026-10-18）

`cand-4376`、`cand-5749`、`cand-6241` 三项候选依既有S3身份组共同映射至一张 archive KU。第21章书目与页图校读支持原题、Jacob Hess编者、Leipzig und Wien及1934年；题名译文明确为工作译名。28条关系候选留待S6；未新增正式关系或外部来源。此前S4已登记1,122组／1,305条映射，待登记3,696组／3,719条；KU=2,141，字段=11,560。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-archive-passeri-vite-hess-1934-20261018)、[KU清单](../tables/ku-manifest.csv)及[对齐表](../tables/alignment.csv)。

### S4 person：George Vertue、Francesco Milizia 与 Barbara Mazza（2026-10-18）

`cand-8933`、`cand-10589`、`cand-11078` 分别按既有S3人物组映射至一张人物KU。George Vertue的五处姓名提及归组；Haskell引述的Vertue两卷均未独立查阅。Milizia按第15章p.371注1登记，不补写未具名著作。Mazza按后记pp.405–406跨页提及归组；其目录的完整书目尚未识别或查阅。6条S2关系候选继续留待S6，本批未新增正式关系或外部来源。截至该批，S4已登记1,125组／1,308条映射，待登记3,693组／3,716条；KU=2,144，字段=11,569。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-vertue-milizia-mazza-20261018)、[KU清单](../tables/ku-manifest.csv)及[对齐表](../tables/alignment.csv)。

### S4 person：Giovanni de’ Vecchi、Alessandro Borgia 与 Urbani de Ghelthof（2026-10-18）

`cand-2706`、`cand-7737`、`cand-12253` 分别按既有S3身份组登记为一张人物KU。Vecchi卡依据第3章索引页码66、80及两处正文记载壁画语境；Borgia卡保留第8章p.223注5所列称谓、两封信日期及“未独立查阅”边界；Urbani de Ghelthof卡保留Haskell的出版者归属陈述与文献使用警示，不另作可靠性裁决。6条S2关系候选继续待S6；本批未新增正式关系或外部来源。截至该批，S4已登记1,128组／1,311条映射，待登记3,690组／3,713条；KU=2,147，字段=11,579。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-vecchi-borgia-ghelthof-20261018)、[KU清单](../tables/ku-manifest.csv)及[对齐表](../tables/alignment.csv)。

### S4 archive：Baldinucci《Notizie》卷 VI（1728）跨章直接关系端点组登记（2026-10-18）

`cand-4846`、`cand-8601` 按既有 S3 组 `archive-group-baldinucci-notizie-vol-vi-1728` 共同映射至一个 archive KU。第21章 p.413 书目记录支持原题、Filippo Baldinucci 书目署名、Secolo V 时间范围、卷VI、Firenze与1728年；第1、2、4、5、6、7、8、9章的卷VI引文支持跨章身份归组，所有被引原页未独立查阅。新增8条 source-backed 字段记录并复用既有Haskell来源；作者人物卡已链接，本批未登记正式作者关系。该卷作为15条S2关系候选的端点，15条全部留待S6逐项审查，本批不将引文转为正式关系。该批后S4已登记1,129组／1,313条映射，待登记3,689组／3,711条；KU=2,148，字段=11,587。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-archive-baldinucci-notizie-volume-vi-1728-20261018)、[KU清单](../tables/ku-manifest.csv)、[对齐表](../tables/alignment.csv)及[知识卡](../units/archives/baldinucci-notizie-volume-vi-1728.md)。

### S4 archive：Pastor《教皇史》卷 XIV 两部分跨章身份组登记（2026-10-18）

`cand-4836` 按既有 S3 组 `archive-group-pastor-storia-dei-papi-vol-xiv-parts-i-ii` 映射至[Pastor《教皇史》卷 XIV 两部分档案卡](../units/archives/pastor-storia-dei-papi-vol-xiv-parts-i-ii.md)。第2、3、6章均有卷XIV引文，第3章明指 `parte II`；书目身份组覆盖两部分，具体印次未定。第21章泛称Roma 1943书目没有卷号，不据以确定本卷出版年、地点或版本。新增8条 source-backed 字段记录，未新增来源登记或正式关系；15条关系候选留待S6。本批后S4已登记1,130组/1,314条映射，待登记3,688组/3,710条；archive类型登记112组/157条，待登记1,119组/1,139条；KU=2,149，字段=11,595。严格阶段审计通过，既有来源引用警告和S2语义审查提示仍保留。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-archive-pastor-storia-dei-papi-vol-xiv-20261018)、[KU清单](../tables/ku-manifest.csv)及[对齐表](../tables/alignment.csv)。

### S4 archive：Pastor《教皇史》卷 XIII 跨章身份组登记（2026-10-18）

`cand-4237` 按既有 S3 组 `archive-group-pastor-storia-dei-papi-vol-xiii` 映射至[Pastor《教皇史》卷 XIII 档案卡](../units/archives/pastor-storia-dei-papi-vol-xiii.md)。第2、3、6章的卷XIII引文一致归入该卷级书目组。外部书目支持卷号、系列题名与历史范围，但不确定Haskell所引具体印次；第21章Roma 1943泛称条目无卷号，`cand-11414` 仍待证且不并入。本卡新增8条source-backed字段记录；5条关系候选留待S6，无正式关系或S5补足。本批后S4已登记1,131组/1,315条映射，待登记3,687组/3,709条；archive类型登记113组/158条，待登记1,118组/1,138条；KU=2,150，字段=11,603。严格阶段审计通过，既有警告仍保留。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-archive-pastor-storia-dei-papi-vol-xiii-20261018)、[KU清单](../tables/ku-manifest.csv)及[对齐表](../tables/alignment.csv)。


### S4 archive：Orbaan《Documenti sul Barocco in Roma》（1920）跨章引文身份组登记（2026-10-18）

`cand-4373` 按 S3 组 `archive-group-orbaan-documenti-barocco-1920` 映射至[《罗马巴洛克文献》档案卡](../units/archives/documenti-sul-barocco-in-roma-1920.md)。第21章 p.432 书目给出 J. A. F. Orbaan、原题、Roma 与1920年；第2至4章的引文与该身份相合。登记范围限于书目身份，未独立查阅原书、所引页或转引材料；不推断出版社、版本或作者规范身份。1631年清单、1608年Avviso及Orbaan 1914–1915年论文保持分立；人物候选 `cand-6384` 仍待证。6条S2关系候选留待S6，未新增正式关系或外部来源。本批新增8条source-backed字段事实。此后S4已登记1,132组／1,316条映射，待登记3,686组／3,708条；archive类型登记114组／159条，待登记1,127组／1,137条；KU=2,151，enrichment=11,611。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-archive-orbaan-documenti-barocco-1920-20261018)、[KU清单](../tables/ku-manifest.csv)、[对齐表](../tables/alignment.csv)与知识卡。


### S4 archive：Wittkower 两种著作跨章身份组登记（2026-10-18）

`cand-4383` 按 `archive-group-wittkower-sculptures-bernini-1955` 登记至[1955年Bernini雕塑专著卡](../units/archives/wittkower-sculptures-bernini-1955.md)；`cand-4557` 按 `archive-group-wittkower-art-architecture-1958` 登记至[1958年意大利艺术与建筑著作卡](../units/archives/wittkower-art-architecture-italy-1600-1750-1958.md)。第21章 p.441书目和跨章引文支持两项不同出版物身份；1958年年份校读及第7章p.187注6 OCR纠正保存在对应S2 statement qualifiers中：`st-chp21-bib-l1261-1299-entry-07`、`st-chp7-p187-n6-cite-wittkower`，见[原书断言记录](../tables/book-statements.jsonl)。被引页及原书未独立查阅；R. Wittkower链接至既有人物KU，但未新增正式作者关系。每组6条S2关系候选共12条均留待S6。本批新增2张archive卡、2条manifest、2条候选映射、accepted路径及16条source-backed字段事实，不新增来源或正式关系。此后S4已登记1,134组／1,318条映射，待登记3,684组／3,706条；archive类型登记116组／161条，待登记1,125组／1,135条；KU=2,153，enrichment=11,627。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-archive-wittkower-sculptures-bernini-1955-20261018)、[KU清单](../tables/ku-manifest.csv)及[对齐表](../tables/alignment.csv)。

2026-10-19 卡诺瓦雕像 work 组 `cand-11531` 保留S3 `new` 并完成S4登记。四条直接关系候选现有完整KU端点，仍待S6语义裁决；“唯一受尊崇的当代人”候选仍因未分类对象 `cand-12236` 缺端点。KU=2,204，S4已登记1,185组／1,376条映射，待登记3,626组／3,647条；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-work-canova-statue-prato-della-valle-20261019)与[知识卡](../units/works/canova-statue-prato-della-valle.md)。

2026-10-19 罗马语境中的 Discalced Trinitarians（cand-5119）保留既有 S3 `new` 身份组并完成 S4 institution 登记；与威尼斯赤足加尔默罗会分立。五条 S2 关系候选中三条现有完整 KU 端点但仍待 S6，另两条仍因西班牙原驻地 cand-5121 未分类、教堂 place 候选 cand-5123 未登记而缺端点；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-institution-discalced-trinitarians-rome-20261019)及[知识卡](../units/institutions/discalced-trinitarians-rome.md)。

2026-10-19 三项地点端点登记并完成 San Carlo alle Quattro Fontane 跨章分组：cand-0701 与 cand-4963 从 undecided 改列 new，与 cand-5123 共同映射至一张 place KU；cand-5122 修道院、cand-5125 施工地点另立对象。cand-5121 原驻地、cand-5124 具体地标仍待证。七条相关 S2 关系候选现有 KU 端点但仍待 S6。当前 S3/S4 累计与过程见[地点身份组记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-place-san-carlo-alle-quattro-fontane-20261019)。

### S3 person：索引姓名候选复用与 Tommaso Ruffo 页图核对（2026-10-19）

本批完成11项 person same 裁决，映射至6张既有人物卡：Orazio Arrighi-Landini（cand-0123）、Jacques Courtois／Giacomo Borgognone（cand-0400）、Niccolò Melanconici（cand-1639、cand-1640）、Andrea del Rosso（cand-2276–2278）、Tommaso Ruffo（cand-2305、cand-2308）及 Don Pietro Antonio Toni（cand-2641、cand-2642）。决定依据各自索引主项／子项与原书对应页的身份锚点，不新增知识元或关系。尤其 p.221 页图直接印作 Tommaso Ruffo，确认 OCR L115 的 Russo 是该处识读错误；两条 Ruffo 子项现 same 映射至既有人物卡，并保留 S2 正文其他拼写及关系陈述的原有边界。

S3 当前为 same=1,993、new=5,027／4,812组、conflict=9、excluded=100、undecided=5,278；person same=1,174、undecided=1,108。KU仍为2,220；S4待登记3,611组／3,632条成员映射，其中直接关系端点队列为1,857组／1,857个端点候选、共1,871个组成员映射。本批11个候选均非 S2 关系直接端点，S4、S5、S6数据未变。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-index-reuse-russo-ruffo-20261019)、[人物卡](../units/persons/tommaso-ruffo.md)及[对齐表](../tables/alignment.csv)。

### S3 person：完成40项既有人物 KU 复用候选审查（2026-10-19）

本批新增29项 same 裁决；连同上一批11项，预备的40项人物索引姓名／异名复用候选现均有明确去向，全部映射到6项 Ruffo／Longhi／Loth／Courtois 等已复用对象及其他同类型既有 KU。候选历史理由仍保留。p.221 页图核对解决了 Tommaso Ruffo 首见名称的 OCR 误读；另对 Camerino p.55n 和 Colonna p.21n 保留索引定位与现有正文锚点之间的差异，不以其定位补写新事实。索引子项提到的作品、并列或关系仍须独立审查。

当前 S3 为 same=2,022（1,092个目标 KU）、new=5,027／4,812组、conflict=9、excluded=100、undecided=5,249；person same=1,203、undecided=1,079。KU仍为2,220，S4待登记3,611组／3,632条映射；S5字段11,714条（1,627条unverified）；S6关系表1,239条（1,237 formal、2 pending），这些阶段总量均未因本批改变。40项候选均非 S2 关系直接端点。逐项证据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-person-index-reuse-remaining-20261019)和[对齐表](../tables/alignment.csv)；Ruffo卡同步记录扫描页与 OCR 差异。


### S4 event：第3章六个直接关系端点组登记（后续批次，2026-10-19）

`cand-5375`、`cand-5398`、`cand-5403`、`cand-5421`、`cand-11601`、`cand-11625` 沿用各自既有 S3 `new` 身份组并完成 S4 登记，新增6张双语事件卡及6条候选映射。十条相关 S2 关系候选仍待 S6；本批未新增外部补足或正式关系。事件边界、原文定位与各项限制见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-event-direct-endpoints-chp3-additional-20261019)。本批后已登记1,241组／1,435条映射，待登记3,571组／3,593条；直接关系端点队列1,816组／1,817个候选／1,831条成员映射，其中事件132组；KU=2,260。

### S5：两项作品馆藏标识来源定位（2026-10-19）

`enr-06678`、`enr-06937` 的 `source_ref` 与依据已改为对应卡片中的 S2 来源，并将字段范围限定为所引页面未列出可识别的单件馆藏号。字段表与卡片已同步；全书字段表仍为11,714条，`unverified` 当前为1,625条。该修订不表示全局馆藏号不存在。过程记录见[来源定位记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s5-work-identifiers-source-resolution-20261019)。


### S4 work：Liberi《洪水》画布（2026-10-20）

cand-7664 映射至[《洪水》画布知识卡](../units/works/the-flood-canvas-liberi-bergamo.md)。作品边界限于 Haskell 所称 Liberi 为贝加莫 Santa Maria Maggiore 委托绘制的首幅画布；原题及当代实物身份未核实，成书时“仍在南门上方”的报告不表示当前状态。7条直接 S2 statement 中5条关系候选仍待 S6；无 formal 关系及外部补足。当前 S4 为1,277组/1,478条已登记映射，3,529组/3,550条映射待登记。


### S4 work：Scuola del Carmine 第二套天顶装饰方案（2026-10-20）

`cand-8742` 沿用既有 S3 `new` 组 `workgrp-30ad0d8bb1910a`，登记至[第二套天顶装饰方案卡](../units/works/scuola-del-carmine-second-ceiling-scheme.md)。第9章 p.273 称 Tiepolo 提出两种主厅装饰方案；第二方案以启迪兄弟会的德性为周围画布主题，并与第一方案区分。Haskell 称第二方案经少量修改后被选择并实施；本卡不推定具体修改、存世画作身份或最终配置。6条直接 S2 statement 中5条关系候选（st-chp9-p273-second-scheme-chosen-and-executed, st-chp9-p273-second-scheme-depicts-charity, st-chp9-p273-second-scheme-depicts-faith, st-chp9-p273-second-scheme-depicts-hope, st-chp9-p273-tiepolo-proposed-second-scuola-scheme）留待 S6；本批未改动 S2 statements/mentions，未新增 formal 关系、外部身份核验或 S5 补足。S4 当前登记 1,278/4,806 组、1,479/5,028 条映射；待登记 3,528 组／3,549 条映射。


### S4 work：Scuola del Carmine 第二方案结构化字段（2026-10-20）

卡片中的1条名称字段与5条基本信息字段已登记至 `enrichment.jsonl`，均由第9章 p.273 原书支持并保留表格单元格和来源定位；未作外部身份核验或外部补足。


### S4 work：Chiesa Nuova 主祭坛（2026-10-20）

`cand-5033` 沿用 S3 `new` 组 `workgrp-d80b6b26bc76a0`，登记至[Chiesa Nuova 主祭坛卡](../units/works/high-altar-chiesa-nuova.md)。第3章 pp.69–70 记载主祭坛与圣母诞生的奉献关系、Cardinal Angelo Cesi 的装饰承诺及约1605年预留款被意外立面费用吸收的报告。卡片按原书来源保留头衔冲突和‘its’暂定先行词，区分主祭坛与后文祭坛画。4条直接关系候选留待 S6；圣母诞生及 Angelo Cesi 已有 KU，立面 `cand-5032` 待登记。未新增正式关系、外部身份或 S5 字段。S4 登记 1,279/4,806 组、1,480/5,028 条映射；待登记 3,527 组／3,548 条映射。


### S4：Chiesa Nuova 立面与 Fausto Rughesi（2026-10-20）

`cand-5032` 与 `cand-2309` 分别沿用既有 S3 `new` 组，登记 Chiesa Nuova 立面 work 与来源点名的 Fausto Rughesi 人物卡。Haskell称主结构到1590年已完成，而立面又过十六年才建成；保留相对时间，不换算绝对年份。相关 S2 关系候选两端现均已有 KU，关系裁决留待 S6。不新增 S2 断言、正式关系、外部身份核验或 S5 字段。当前 S4 登记 1,281/4,806 组、1,482/5,028 条映射；待登记 3,525 组／3,546 条映射。

### S4 term：外国旅行者跨章术语组（2026-10-20）

`cand-3562` 沿用既有 S3 `new` 组 `sg3-term-cand-3562`，登记至[外国旅行者术语卡](../units/terms/foreign-travellers.md)。第1、4、5、9章提供不同语境的来源锚点；旅行者、游客、外国人、使节与普通来访者不视为同一批人。第7章限定为17世纪后半赴意大利英国游客的术语卡保持独立。5条直接 S2 关系候选留待 S6；本次未新增正式关系、S5字段或外部身份核验。登记后 S4 已登记1,282/4,806组、1,483/5,028条映射；待登记3,524组／3,545条映射。

### S4 term：羔羊崇拜图像主题（2026-10-20）

`cand-5291` 沿用既有S3 `new`组 `sg3-term-cand-5291`，登记至[羔羊崇拜图像主题卡](../units/terms/adoration-of-the-lamb-iconographic-subject.md)。第3章 p.84 将其作为 Gaulli 后殿壁画所表现的主题，并分别提及较早的 S. Prassede、S. Maria Maggiore 马赛克；主题、壁画和马赛克保持分立。5条直接 S2 关系候选留待 S6，本批未新增正式关系、外部身份或 S5 字段。登记后 S4 已登记1,283/4,806组、1,484/5,028条映射；待登记3,523组／3,544条映射。

### S2定点修复：羔羊崇拜主题端点（2026-10-20）

st-chp3-seciv-l75-81-revived-lamb-subject 的对象端点已由壁画作品候选 cand-5287 校正为图像主题候选 cand-5291，依据为第3章 L76 原文及同段提及映射；该术语 KU 当前对应的6条直接 S2 关系候选均待 S6 逐条裁决，不表示正式关系或独立语义验收。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s2-targeted-repair-revived-lamb-subject-endpoint-20261020)。

### S4 term：博洛尼亚画家集体称谓（2026-10-20）

cand-4229 按既有 S3 new 组 sg3-term-cand-4229 登记至[术语卡](../units/terms/bolognese-artists-collective-category.md)。第2章 p.28、p.34、p.45 与第5章 p.123 的多处书内用例支持将其登记为地域性画家集体称谓；不设固定名录或正式组织身份。4条直接 S2 关系候选已有逐条 S6 去向：Passeri 的回顾评价否决为图谱边；Carlo 偏爱、交游、委托三项因群体成员/具体对象未定且没有 person → term 受控关系而待证；本批不新增 formal 关系。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s6-bolognese-collective-candidates-20261020)。登记后 S4 已登记1,284/4,806组、1,485/5,028条映射；待登记3,522组／3,543条映射。

### S4 place：波焦阿卡亚诺费迪南德画廊中的博物馆房间（2026-10-20）

cand-7963 沿用既有 S3 new 组 sg3-place-cand-7963 登记为[地点卡](../units/places/poggio-a-caiano-museum-room.md)。第8章 p.235 与附录 p.390 所录 1706年书信支持其为 Ferdinand 在 Poggio a Caiano 的威尼斯画作画廊中的博物馆房间，且 Ricci 的绘制计划当时被推迟；原始档案信件未直接查阅。本卡不声称房间最终完成或与后来的房间、天顶装饰为同一对象。4条直接 S2 关系候选（st-chp19-p390-ferdinand-defers-room, st-chp19-p390-ricci-museum-room-plan, st-chp8-p235-ferdinand-postpones-poggio-scheme, st-chp8-p235-poggio-visit-postponed）均有类型匹配的另一端 KU，仍待 S6 逐条裁决；登记后 S4 已登记1,285/4,806组、1,486/5,028条映射，待登记3,521组／3,542条映射。

### S4 term：圣马可 Procuratore 职位（2026-10-20）

`cand-8449`沿用既有S3 `new`组 `sg3-term-cand-8449`，登记至[圣马可 Procuratore 职位卡](../units/terms/procuratore-di-san-marco-office.md)。第9、10、15章分别称 Marco Foscarini、Pietro Foscarini、Pisani 与 Memmo 曾担任、当选或就任该职位；第10章 p.327 的政治图像只称一位未具名 Procurator，未据此识别其身份。五条直接 S2 关系候选留待 S6；未新增正式关系、外部身份或 S5 字段。登记后 S4 已登记1,286/4,806组、1,487/5,028条映射；待登记3,520组／3,541条映射。

### S4 term：威尼斯艺术家集合称谓（2026-10-20）

`cand-8104`沿用S3 `new`组 `sg3-term-cand-8104`，登记至[威尼斯艺术家集合称谓卡](../units/terms/venetian-artists-collective-category.md)。该卡记录哈斯克尔在第8、10章中用于展览、书信、英国赞助与海外流动叙述的集合性称谓；不设固定成员名单，亦不把不同语境推为同一群体。5条直接 S2 关系候选留待 S6；未新增正式关系、外部身份或 S5 字段。登记后 S4 已登记1,287/4,806组、1,488/5,028条映射；待登记3,519组／3,540条映射。

### S4 institution：哈斯克尔威尼斯叙述中的教会机构（2026-10-20）

`cand-8672`沿用S3 `new`组 `sg3-institution-cand-8672`，登记至[教会机构卡](../units/institutions/church-as-patron-in-venice-haskell-account.md)。第9章 p.268 将“the Church”作为威尼斯当代艺术的集体性赞助主体；本卡不与威尼斯共和国、教宗职位、教廷国家或单座教堂合并，不据此推定法律组织边界。5条直接 S2 关系候选留待 S6；未新增正式关系、外部身份或 S5 字段。登记后 S4 已登记1,288/4,806组、1,489/5,028条映射；待登记3,518组／3,539条映射。

### S4 term：第13章威尼斯出版商的两个来源类别端点（2026-10-20）

`cand-12120`与`cand-12121`沿用各自既有S3 `new`术语组，分别登记为出版商雇用的雕版工、以及出版商选用于图画委托的艺术家类别。两组共享第13章 p.333 的出版活动语境，来源不提供个人名单；不推定两类人员互斥或完全相同。4条直接S2关系候选留待S6逐条裁决；本批不新增正式关系、外部身份或S5字段。登记后S4已登记1,290/4,806组、1,491/5,028条映射；待登记3,516组／3,537条映射。

### S4 term：洛多利论述中的新兴古典主义端点（2026-10-20）

`cand-9748`（`sg3-term-cand-9748`）沿用既有 S3 `new` 决定，登记为来源局部术语“洛多利论述中取代晚期巴洛克的古典主义”。第10章 p.321 称该古典主义正在取代晚期巴洛克、并处于洛多利反对的样式之列；p.322 的 “that very classicism” 明确回指前者，称 Memmo、Querini、Farsetti 后来支持它。按来源回指将两处映射到同一 S3 组；不自动并入既有 Neo-classicism KU。四条直接 S2 关系候选的另一端均已有 KU，本批补齐该端点映射；关系仍待 S6 逐条裁决，不写 formal 边、外部身份或 S5 字段。登记后 S4 为 1,291/4,806 组、1,492/5,028 条映射；待登记 3,515 组／3,536 条映射。


### S4 institution：Inquisitori di Stato 跨章身份组（2026-10-20）

`cand-9739` 与 `cand-10464` 已按第10章 p.320 及第15章 p.364 注1的同名机构锚点合并登记至[知识卡](../units/institutions/inquisitori-di-stato-venice.md)。后者从 S3 `undecided` 改列 `new`；官方威尼斯国家档案指南用于核对同名机构及档案层级，机构、保管机构和档案记录仍分开。相关四条 S2 关系候选中三条的 KU 端点已齐但均待 S6，另有一条因 `cand-9807` 未决而阻断；本批未新增正式关系或 S5 字段。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-institution-inquisitori-di-stato-20261020)。当前 S4 已登记1,292/4,806组、1,494/5,029条映射；待登记3,514组/3,535条映射。
