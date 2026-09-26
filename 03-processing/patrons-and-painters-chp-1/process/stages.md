# 第一章摄入与处理：必要过程记录

当前唯一成果：[摄入与处理定稿](../results/stages.md)。本文件只保留改变处理判断的过程，不复制逐行分析和当前统计。

## 关键裁决沿革

| 依据 | 实际工作与决定 |
|---|---|
| REV-013 | 确认 1980 修订版／2006 印刷，读取第一章 OCR 和随页脚注；完整章与分节副本不算独立来源。最初代表性成稿不足以证明完整提取。 |
| REV-014、015 | 按原始 L1–980 逐行复读，处理跨页、断行及正文—脚注；保留 80 个跨度的语义依据。范围限定第一章，第六章暂停。 |
| REV-015、016 | 目视 PDF 印刷页 6、9、13、18、20、22，校正姓名、脚注及费率。Domenichino／Lanfranco 合写 130 被纠正为 130／100；旧知识元数量不能证明完整。回查脚注独立文献、建筑和作品，并定向查同书书目／索引。 |
| REV-032 | 来源 SHA-256 与原阅读版本一致；核对页界、行段和关键句后，将完整逐行分析与章页、摘要、校正及未决项归入 results/stages.md。修正 L382 的新段边界，已核 OCR 名形归入定稿，不再与旧“待核”并存。 |

## S2 表迁移（2026-09-26）

### 后续语义核对与修订

`sec_ii:l118-127` 的原文段实际覆盖 OCR L717–752，旧覆盖行漏列 L717–722，导致两条有证据的断言未进入 `book-statements.jsonl`。现修正范围并补记 L717–719 的措施撤回、L720–722 的短期财务收益及学院成员社会地位关切；补录 Urban VIII brief、France、gilders、critics 等适当提及和4个开放候选。随后核对 `sec_ii:l148-153`、`l155-159`，补入 social climbing、artist as exceptional being、King of Savoy（身份未定）、self-advertisement、self-portraiture、claque、artistic independence 等提及；重复概念映射到已有艺术展览与艺术家气质候选。两段合计新增10条提及、8个开放候选，不新增原书断言。当前 S2 为 643 条提及、172 条断言；严格表审计通过。该复核仍是定向抽查，不构成全章语义准确率或召回率估计。

继续检查 `sec_ii:l161-166` 后，再增补6条提及、2个开放术语候选，记录艺术的优越地位与十九世纪浪漫主义对艺术家形象的接受，并将 publicity、independence、inspiration、eccentricity 映射到前段已建立的概念。当前为649条提及、172条断言；严格表审计通过。跨段的 OCR 行重叠已逐项检查，现见于续句与脚注上下文回指，不代表额外源段或完整性计数。

继续复核实体密集段 `sec_ii:l28-38` 时，对照30条提及与5条正文断言及1条脚注断言。将 `St John the Baptist` 的提及跨度由末词扩为含原换行的全名；统一 OCR 与分节转录的 `Iris` / `his` 差异经 PDF 文本核对后保留原分节字符串及候选说明。其余明确人名、地点、作品/题材和史料作者均已有映射；未具名律师、诗人及不确定的修院会规书名继续留在断言语境，不推定身份。严格表审计通过；这是同代理逐项复核，不作独立语义接收。

### 独立语义复核抽样与结果（2026-09-26）
为取得独立语义证据，按既定分层样本复核：总体为27个已迁移正文段、649条提及、172条断言；低（≤10提及，N=6）抽2，中（11–30，N=19）抽5，高（>30，N=2）全取；随机种子20260926，无放回。样本9段：chp-1:01_CHP-1_intro:l3-5、chp-1:01_CHP-1_sec_i:l3-13、chp-1:01_CHP-1_sec_i:l15-24、chp-1:01_CHP-1_sec_ii:l28-38、chp-1:01_CHP-1_sec_ii:l48-60、chp-1:01_CHP-1_sec_ii:l79-84、chp-1:01_CHP-1_sec_ii:l137-146、chp-1:01_CHP-1_sec_ii:l161-166、chp-1:01_CHP-1_sec_ii:l168-239；当前账本共363条提及、69条断言。

审阅由独立隔离上下文的 Codex 代理完成：首轮仅读抽样原文、taxonomy 和字段契约，未读当前提及/断言表及处理记录；先列原文实体与作者断言，再逐段交叉核对现表。代理不修改文件，主代理核验证据后应用以下四项高置信修正：

- m-chp1-secii-0056 原跨度误指 l28-38 的 “this” 中子串 his，却映射到 Iris；现将跨度移至同段实际误录为 “his” 的 apparition of his to Turnus，并说明分节文本异文、全章 OCR 与 PDF 所见 Iris。表面形式保留所用分节来源的原字样，避免声称该分节源已写出 Iris。
- m-chp1-secii-0223 将 Pieter Van 扩为跨行的完整跨度 Pieter Van + 换行 + Laer，覆盖同一段中的完整姓名。
- st-chp1-secii-l952-958-04 删除原文未提出的“按成品质量定价”解释，保留作者关于能力能否预先评估、Rosa坚持交出最佳作品及匿名代理人所述声誉的限定。
- st-chp1-secii-notes-comedy-and-letters 删除脚注没有提供的喜剧年份 1635。

代理另将 Four Elements、两幅 Caravaggio 作品、Chiesa Nuova、St Peter’s 标为疑似映射过泛。按数据字典合读索引候选 canonical_name 与 sub_entry 后撤销这些疑点：子项分别保留具体作品或地点，对应关系正确，未改动。Mr Coke 的身份由抽样之外的脚注第45–48行提供；该归属另有项目内核查记录，但不能仅凭本次正文样本复核，故作为范围限制保留。其余抽样范围未发现可明确裁定的高置信差异。

这是有价值的缺陷发现与修正，不是整章精确率/召回率估计或正式人工验收；未形成可逐条量化的独立黄金标注集，不能用样本通过/错误数外推全章质量。修正后严格表审计已针对提及跨度复核。

覆盖台账 `04-knowledge/tables/s2-coverage.csv` 对第一章 30 个 S0 段逐一记录处理范围；3 个生成的分节文件标题按格式元数据排除。前述各段的迁移及逐行核对细节仍有效。后续复核将脚注中 OCR L321–322 的 Savini、Minnitti 归回实际承载正文的 `l28-38`，L323–330 的其余来函记录归 `l168-239`，避免把跨段脚注整体错误挂在一个 S0 段下。在 `sec_ii:l3-8` 抽查中，市场中介断言列举 middlemen、foreign travellers 与其 agents；账本原先只记录 dealers 和 dilettantes，现补三条未具名 `term` 候选及精确跨度，保持 open。在人物与机构较密集的 `sec_ii:l106-116` 抽查中，又补 `picture dealers` 到既有 art-dealer 候选，并将 feast of St Luke 中的 St Luke 记作开放人物候选；不预先解决其身份。在 `sec_ii:l129-135` 又发现已成稿的 `gentiluomo d’onore` 荣衔术语未登记为提及，现连接至既有候选 `cand-3164`，不新建 KU。在 `sec_ii:l137-146` 抽查时，发现关于贫困画家的同一段原书断言还提及 dealers 和 devotional pictures；现分别连到既有 art-dealer 与 devotional-picture 候选，不扩充类型清单。在 `sec_ii:l19-26` 又补入此前仅在断言层表示的补助换取赞助人优先权机制，新增开放术语候选 `cand-3565`，由 `subsidy` 与 `priority over all other customers` 两个原文跨度支撑，不创建具体人物或知识元。在 `sec_ii:l40-46` 又将教堂名提及跨度扩展为 `Sebastiano on the Palatine`，并为 movable gallery picture、connoisseurship 登记两个 open term 候选，保留 OCR 软连字符行折的说明。在 `sec_ii:l48-60` 为 Valentin 专长的 Caravaggesque genre scenes 补登记开放术语候选。在 `sec_ii:l62-71` 补记既有 Holy Year 候选的 Holy Years 提及，并为 Baroque period 与 amateur 建立开放术语候选；amateur 暂不并入 dilettante。在 `sec_ii:l73-77` 将 deposit 提及映射到既有 caparra 候选，并为画布 canvas 新增开放材料术语候选。当前 27 个已审阅段全部完成、0 段部分、0 段待迁移，另 3 个格式标题排除；总账本 608 条实体提及、170 条原书断言。逐段迁移状态是结构闭合指标，不等于实体召回率、准确率或独立语义验收。所有断言均携带原始 OCR 文件及行号；校验器检查引文能在所引行复现、行范围属于覆盖记录。跨页句、未具名 Lanfranco 草图、Barberini 家族与家户差异、Malvasia 归语限定及未决身份均保留；正文候选不自动提升为 KU。严格阶段审计现无结构或迁移错误，但语义质量仍需独立评估。

### 语义抽查更正（2026-09-26）

对 `sec_ii:l168-239` 逐行核对时发现 `V. Ruffo` 曾错误映射到 Giuseppe de Rosis 的书信 KU；现为编辑者建立独立、身份未定候选 `cand-3474`，OCR 变体及仅存首字母的刊印署名均保留在该候选下，且不与收信人 Antonio Ruffo 合并。又按 L562–570 补录 Jacopo Salviati、Cardinal Leopoldo de’ Medici、Fabrizio Arragona、Guercino 与 Don Antonio Ruffo 等来函端点，并新增开放候选。复核同时补入其他具名人物、地点、机构、作品及信件／收据／契约等 archive 对象；完整性检查将只含 `ibid.`、章节或页码互引的行作为无独立实体跨度处理。脚注跨段归属修正后，该段及全章 S2 账本为 590 条提及、170 条断言；后续四个正文段抽查再补8条提及和1个人物候选。随后在 `sec_ii:l10-17` 对照原始段、现有12条实体提及和13条原书断言：具名人物、地点、引语归属及跨段续句均有处理；匿名家内职位和文人类别保留在断言中，未据泛称建立具体对象或额外术语 KU。该样本没有发现明确漏项或错误映射。在 `sec_ii:l19-26` 再核对8条原有提及和11条断言时，发现补助换优先权是独立于家内供职的 patronage mechanism；现增开放术语候选并以两处原句定位。在 `sec_ii:l40-46` 核查15条原有提及和6条断言时，扩展了 San Sebastiano 教堂名的精确跨度，并补记 movable gallery picture 与 connoisseurship 两个重要术语；未将普通买卖活动或泛指赞助人擅自拆成实体关系。在 `sec_ii:l48-60` 核查20条原有提及和7条断言时，发现 Valentin 的 Caravaggesque genre scenes 专长应作为可复用术语保留，现增开放候选。在 `sec_ii:l62-71` 核查19条原有提及和7条断言时，补齐了既有 Holy Year 候选的原文提及，并新增 Baroque period、amateur 两个开放候选；未将 amateur 直接等同于 dilettante。在 `sec_ii:l73-77` 核查10条原有提及和4条断言时，补记与现存 caparra 知识元相连的 deposit 提及，并新增 canvas 开放材料候选；概括性支付比例和例外仍留在断言中。在 `sec_ii:l79-84` 又补录一处 `deposit` 提及并映射到 `caparra` 候选；同段“Duke of Mantua”因仅有头衔不足以证明与前文同名候选为同一人物，现拆为独立、身份未定候选 `cand-3572`，不合并。在 `sec_ii:l86-94` 对照15条既有提及、7条断言及原文后，补录 dilettantes 并映射既有术语，Venetian、Bolognese、Neapolitan 映射到既有 Venice、Bologna、Naples 地点候选；另为 art dealing、art exhibitions、landscapes、large historical scenes 建立4个开放术语候选，精确锚定原始 OCR L604、L606、L608。新增提及共8条，没有新增断言或接收KU。在 `sec_ii:l96-104` 对照20条既有提及和5条断言，补录 artist’s status、Renaissance、Baroque、Bolognese、status of the artist 与 High Renaissance 六条提及；Bolognese 映射 Bologna，Baroque 映射既有时期候选，另建 artist’s social status、Renaissance、High Renaissance 三个开放 term 候选，并区分广义 Renaissance 与 High Renaissance。当前623条提及的严格阶段审计通过；全量同步闭环需在本次数据更新后重跑。以上仍是有限抽查，不是全章独立召回率、准确率或语义验收。

跨节 no-delta 抽查覆盖 `sec_i:l15-24` 的正文和对应断言：32 条现有提及、14 条原书断言与来源段逐项对照。具名人物、地名、机构、作品／图像和术语均有映射；“relatives, friends and clients”等泛指群体保留在原书断言语境，不凭复数泛称建立具体对象。该样本未发现需再改表的明确漏项或错误映射；样本量不足以推断全章精确率或召回率。

脚注密集段 `sec_i:l38-47` 交叉抽查：对照 29 条提及、7 条断言及原始脚注范围；Ameyden 手稿与保管机构、转引链、未决 Montalto / Cardinal Pio 身份、Bonari OCR 异文及旅行目的地均保留各自证据边界。未发现可明确补录的独立对象或错误映射，本段 no-delta；该判断不替代独立验收。

## 本阶段清理

逐行分析已作为阶段成果原位迁至 results/stages.md，过程不再按轮次重复抄录总数、旧计划及结果。前后重复叙述移除，改变结论的理由保留如上。知识元及其后续阶段的 process/knowledge.md 暂保留，到知识元登记等相应步骤再整理。

旧 compact-v4 包的 manifest.json、source-map.jsonl、semantic-units.jsonl、candidate-ledger.jsonl、summary.md 已被当前语义结果取代，退出本任务的在用文件。其 15 候选／10 KU／5 claim、预设维度、旧客户端 accepted 声明不再作为当前入口或待执行队列。旧 source-map 还含重叠页段，不能用来替代当前实际 Page 标记定位。源 PDF、OCR 与分节副本均保留。

清理前确认上述五文件已经 Git 跟踪，且工作树内容与提交 `f84e3d7cb679194ca7400876ca798ca724d9af3d` 一致；历史内容可按该提交及原路径恢复，不另建归档副本。同步清除派生候选索引中的旧待执行项，仅刷新相应机器记录，不开展知识发现。

## 核对与交接

本轮核对实际 OCR 为 980 行、PDF 为 22 页，来源指纹一致；语义跨度包含章内正文、注释和排除项。物理行覆盖只作定位检查，语义工作依据前轮完整阅读和本轮定向复核，不称独立正式验收。

收口检查：80 个语义跨度覆盖 L1–980，无越界或缺行，均有印刷页和摘要／排除说明；相关文档 341 个本地链接有效。与本轮开始时的 516 个文件指纹比较，只有来源登记 source-registry.md 按授权更新，其余 515 个来源、知识元和页面文件均未改变。规则漂移为 0，git diff --check 通过。候选索引为 0 条、无生成问题；健康快照同步移除已退役包的旧 accepted 声明。健康／治理快照的其他模板或内容提示不是本阶段语义完成的自动门禁，本轮未据此修改知识元或页面。

下一阶段为知识元登记，既有下游成果保留；未经其阶段复查，不把它们标为本轮定稿。用户原话留在治理记录，本文件不复制原话。本轮未提交或推送。


在 `sec_ii:l40-46` 的定向语义抽查中，发现原文 “during the Renaissance” 尚无对应提及；按源段拼接文本的 2313–2324 字符跨度，新增 `m-chp1-secii-0651` 并复用既有开放术语候选 `cand-3578`（Renaissance）。未新建候选或 KU。此为同一执行者的针对性漏项修正，不构成独立验收或全章准确率估计。


在 `sec_i:l26-33` 定向对照24条提及、8条原书断言、分节文本及印刷页5。已具名家族、地点、宗教团体、教堂与候选端点均有相应提及；匿名的主教、教皇、贵族／枢机群体及建筑类别保留在原书断言，不据泛称造候选，本段无明确需补录对象或错误映射。印刷页核见分节 OCR 的 “his family palace” 为正确读法；整章 OCR 同一处误作 “Iris family palace”。同页另有 “essential” / `essentia]`、Aldobrandini / `Aldôbrandini` 转录差异。现有断言引文按其 `source_file` 所指整章 OCR 原样保存，来源差异仅记为读取限制；未改写来源资产或让引文跨文件失去定位。本次是同一执行者的定向抽查，不构成独立验收。


在 `sec_i:l35-36` 对照分节文本、1条提及和3条原书断言：Peretti-Montalto 引文续句通过 `continuation_of` 接回前段；本段唯一具名地点 Rome 已登记。新教堂赞助人、政治地位、艺术接触及古老教堂中的现代绘画作为带限定的作者概括保留在断言，不拆成无名实体。本段 no-delta；仅为同一执行者的抽查。


`intro:l11-13` 脚注抽查对照8条提及、4条断言、分节文本与 PDF 扫描：具名作者、文献、刊行地、Coke 书信及 Hervey 引证均有记录；未新增候选。PDF 扫描与分节文本均读作 “Passeri, p. 293”，整章 OCR 则误作 “Passed”。为遵守断言 locator 指向整章 OCR 的行范围契约，保留两条 OCR 引文和原行号，在断言限定中记录异文；提及仍按分节来源登记的 Passeri 形式保留。其余两条断言边界及匿名文献身份保持原裁决。


对 `intro:l7-9` 做 no-delta 核验：仅含页码标记、章节序号与章名；coverage 中 `no_semantic_content` 判断正确，不增实体提及或原书断言。


对27个已完成 S2 段执行只读候选表面筛查：以有类型候选的规范名／子项匹配原文，过滤短单词并合并同一跨度，得到13处未与现有提及重叠的提示。逐处对照原文和候选后，补入13条提及，分别为 `Madonna del Carmine`、`Northern Europe`、第二处 `Piazza Navona`、两处 `ultramarine`、`Mancini`、`Claude`、三处 `canvas`、两处 `modello` 及 `In tela il disegno`；全部复用既有候选，保留 `Mancini`、`Claude` 与 Madonna 对象的身份／类型待决状态。此扫描只能提示候选清单中可匹配的未覆盖表面形式；不发现未列入候选的实体、不裁决身份，也不作为召回率或语义验收。S2 现为663条提及、172条断言。


S2 后续定向语义抽查（2026-09-26）：对照 `sec_ii:l3-8`、`l62-71`、`l106-116`、`l148-153` 的原文、75条提及和23条断言；前述分层盲审未抽到这四段。发现 `m-chp1-secii-0653` 将原文 “Northern Europe”（源文物理行436）挂到更宽泛的 `cand-3462`（Europe，源自 `l79-84`）上。现新增开放地域候选 `cand-3594`（Northern Europe，`place`），将该提及改映射至此候选；原文跨度不变，未据此建立KU或宣称身份配对。其他三段此次未发现可裁定的映射或断言问题。此为同一上下文的定向语义检查，不是盲审、独立验收或全章精确率／召回率估计。

### 短词候选覆盖复查（2026-09-26）

在默认 6 字符门槛外，将候选表面扫描下调至 3 字符，检查 27 个已迁移段的 652 个类型化候选标签；首轮出现 9 个无提及跨度覆盖的候选词命中。逐处核对原文、候选来源及现有跨度后，7 处 `Pope` 是匿名职衔、通称或已由相邻具名提及表达的标题成分，不能因同词命中映射至来源为 `L657` 的身份未定候选 `cand-3518`；2 处 `Italy`（`sec_ii:l48-60` 字符 259–264；`sec_ii:l106-116` 字符 818–823）确为国家实体提及，现均复用 `cand-3461` 补入 mentions。为减少将仅以职衔记录的未决人物候选跨段误配，扫描器现对“identified only by office”的 body-mention 候选限制在其来源段，并以回归测试覆盖。当前总账本为 665 条提及、172 条断言；再次低阈值扫描无未覆盖候选词命中。此工具只能提示既有候选标签的字面未覆盖位置，不能发现未列候选的实体，也不构成召回率或语义验收。
