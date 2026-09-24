# 第一章样例：第一部分当前结果

**当前进度（2026-09-25）：第一章样例的知识元补足与关系审查继续进行，尚未整体定稿。** 摄入与处理沿用既有定稿；当前全库1,001个有效KU、1,191条关系索引（1,190条显式、1条规则派生）。最近一次全量闭包16步及274项测试通过，结构健康度130/130；关系机械检查的断端点、非法关系类型、缺反向映射和弱证据均为0。内容检查仍有1项既存档案标题格式提示；全库有203个单一来源KU。近期补入Ludovisi亲缘链中缺失的Orazio、Niccolò、Lavinia三个端点，完成其中两人的Wikipedia—Wikidata双向身份核对，并登记9条有据关系；Orazio卒年异文保留，Lavinia无可确认的个人Wiki身份。最新一批补入Maggiotto肖像组、Maffeo Pinelli及Pisani di Santo Stefano支系三个KU和三条有据关系。以上机械检查不替代语义定稿。

- 对Maggiotto与Maffeo Pinelli完成Wikipedia—Wikidata双向身份核对：前者核对英文、意大利文页面均回链Q3080993；后者查无适用的英语和意大利语页面，以法语页面双向匹配Q56006855。新增1778年168幅油画铜板肖像组、Maffeo Pinelli与Pisani di Santo Stefano家族支系三个KU，登记创作、委托和1787年购藏三条显式关系。图版68a的三幅肖像不与该系列合并；1791年加入的Manin夫妇肖像作者与实物身份仍待证。关系只在作品卡保存一次，关联人物／家族卡提供反向展示。详情见[Maggiotto肖像组与Maffeo Pinelli身份关系闭合](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md#maggiotto肖像组与maffeo-pinelli身份关系闭合2026-09-25)。本轮全量闭包16步、274项测试通过；单一既存档案标题格式提示未受本批影响。

- 从巴尔多伊诺作品年表登记1661年《圣埃洛伊与圣若翰洗者、圣安德烈》，采用Thevenon研究和法国文化部Palissy PM06000568的同题名、签名、尺寸与地点信息。后续发现意大利语主教座堂条目把1646年“Bernardino Baldoïno”说法引至同一Palissy对象号，故当前按一个目录对象处理；1661／1646年代及父亲／儿子归属异文仍未裁定，不另建第二件或给Bernardin增加正式创作边。主教座堂的法语Wikipedia—Wikidata Q1084011双向身份核对已记录。
- 据Thevenon补登记[贝尔纳丁·巴尔多伊诺（Bernardin Baldoino）](../units/persons/bernardin-baldoino.md)，并建立与父亲的`parent_of`／`child_of`互指；另登记一件1670年《施洗者圣若翰斩首》和两件成对的1680年圣罗撒画作，以及尼斯黑衣忏悔者团体端点。该批新增5个KU和8条显式关系，包括三件作品的创作者、1670年服务对象及两件1680年作品的研究所载地点；未将服务用途写成合同委托，也未补造媒材、尺寸或在馆时间。详情见[Bernardin身份、作品及亲缘关系补足](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md#bernardin-baldoino身份作品及亲缘关系补足2026-09-25)。

- 补充Ottavio Leoni、Pietro Testa、Paolo de Matteis三张既有人物卡的英文Wikipedia与Wikidata双向身份入口，三组姓名、职业、年代等特征相符；并据已读来源补充称谓／别名字段。Pietro的1611／1612和Paolo的1727／1728差异保留为来源异文，不以对齐覆盖原有证据判断。Q51562312访问时重定向到Paolo de Matteis的Q1851224，不另作人物身份。三组双向比对现已补入`alignment-evidence.jsonl`；本批复核已有关系未见需修订处，未新增知识元或关系。详细比对见[三位画家身份核对](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md#三位画家wikipediawikidata身份双向核对2026-09-25)。
- 追核央行艺术收藏对Paolo de Matteis与Francesco di Maria的概括性师承说法，并与两篇Treccani人物传记对读。由于馆方语句未明确限定教师对象，Paolo的DBI仅明确其师从Luca Giordano，Francesco di Maria的DBI未述此关系，故保留为待证线索，不新增正式师承／影响关系或端点；详见[关系线索复核](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md#paolo-de-matteis与francesco-di-maria关系线索复核2026-09-25)。
- 为已登记的比安科尼1762年信件补入收件人人物端点，将“Marchese Filippo Hercolani”对齐至1736–1810年的菲利波·埃尔科拉尼；Wikipedia的`pageprops`与Wikidata Q47468606的`itwiki`站点链接双向一致。补入其父亲Marcantonio Hercolani（1709–1772）端点及有据`child_of`／`parent_of`关系。信件→收件人`addressed_to`和比安科尼→埃尔科拉尼`corresponded_with`保留，后者限于1762-11-22这一封信。详见[收件人身份与关系补足及身份纠正](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md#filippo-hercolani身份纠正及父子关系闭合2026-09-25)。

- 为格列高利十五世亲缘链中已采用但未建档的Orazio、Niccolò与Lavinia Albergati补建3个KU；Orazio、Niccolò分别完成Wikipedia—Wikidata双向对齐，Lavinia未找到可匹配的独立条目，以Treccani多篇传记支持其身份。新增9条显式关系，覆盖教皇—弟弟／侄子、夫妻、父母子女及兄弟；Orazio卒年来源冲突（DBI／Wikipedia：1624；Wikidata：1640）保留。详见[Ludovisi亲缘端点对齐与关系闭合](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md#rev-122-ludovisi亲缘端点的对齐补足与关系闭合2026-09-25)。

- 随后为Ferri的Sant’Agnese穹顶关系链新增Pamphili家族和合同对象Giovanni Battista Pamphilj Aldobrandini（1648–1709）两个KU，并写入4条有据关系。纠正原卡将“G. B. Pamphili”含混指向已故教皇的风险；区分家族委托责任、个人合同及合同彩稿。家族完整谱系、合同原件、彩稿实物身份仍未确认。
- 本批为Guercino祭坛画新增Messina城市和San Gregorio教堂两个place KU，并把教堂登记为Zeri所载末知地点；另以官方市级来源把教堂定位至Messina。全库现为967个有效KU、1128条关系索引。1665年委托修院法人及其与San Gregorio附属修院的关系仍未确认，故不建立委托边。
- 本轮依据RISD馆藏号52.195补登记Ottavio Leoni 1617年《烛光下的马达莱娜·泰利肖像》，并连接肖像人物和保管机构；2006年目录旧题名以同一馆藏号确认为同件作品。补建RISD Museum及Providence端点，为机构完成Wikipedia—Wikidata双向身份对齐；修正Maddalena、Eufrasia误写为儿子的双语描述，并为Maddalena补婚姻、嫁资和丧偶记录。该后续更新后全库为971个KU、1135条关系索引。
- 章前图版64对应人物John Strange完成Wikipedia—Wikidata双向身份核对；Villa Loredan已作为独立地点登记，并补齐历史所有权、所在地和图版描绘关系。没有把具体Met或National Gallery馆藏画作误配成本书图版；现全库971个KU、1135条关系索引。
- 四位画家的身份与外部专业来源相连；Vincenzo I Gonzaga与Giovanni Angelo d’Altemps均完成适用的Wikipedia—Wikidata双向核对。Francesco与Domenico Fedeli关联同一学院端点；Paolo de Matteis加入画家会众的端点使用DBI描述性称谓，未伪称正式机构专名。
- 《赫拉克勒斯的选择》区分阿什莫林委托原作、利兹较小亲笔版本及DBI所列原作地点；不将原作地点写成委托地点。Testa受洗日期不作出生日期；Leoni对Caravaggio仅面熟，不建立朋友关系。
- Francesco Fontana依据家族研究和1633、1634两封有日期的Testi书信完成章内人物的初步对齐；新建1634年信件KU并补入Testi—Fontana通信边。不匹配的同名Wiki页不代填QID；其生卒和完整生平仍待证。
- 为圭尔奇诺西西里祭坛画新增“圣额我略堂加尔默罗圣母小堂”place端点及画作`installed_at`关系；小堂→教堂`located_at`。原有Zeri“末知地点”关系保留，安装日期不推定；Maria Teresa Ruffo的1688年资助记载未延伸为关系边。
- 对Maria Teresa Ruffo进一步消歧时，发现Ruffo谱系页列有两条分别在San Gregorio修院的同名人物记录；Wikipedia／Wikidata精确查询未找到可用的唯一人物入口。小堂资助者身份因此仍待证，不合并候选、不建立赞助边；详见[消歧续核](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md#maria-teresa-ruffo资助者消歧续核2026-09-25)。
- 本轮全量闭包16步、274项测试通过；有效KU 986、关系索引1165（显式1164、规则派生1），结构健康度130/130；关系完整性机械审计的断端点、非法类型、缺反向映射和弱证据均为0。仍有1项既存档案标题格式提示及197项单一来源研究债务。
- 本轮涉及的端点、时间／版本、关系方向与对应来源见[画家关系接续](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md#第一章人物身份和作品关系接续2026-09-25)、[Guercino祭坛画末知地点核对](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md#圣额我略堂末知地点与城市端点2026-09-25)、[Guercino祭坛画安置空间补足](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md#圭尔奇诺祭坛画历史安置空间与关系闭合2026-09-25)、[马达莱娜·泰利作品与身份关系补足](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md#马达莱娜泰利作品与身份关系补足2026-09-25)及[Francesco Fontana身份对齐与1634年通信补足](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md#francesco-fontana身份对齐与1634年通信补足2026-09-25)。其余对象对齐、作品和关系缺口仍待继续；证据不足的对象保留待证。知识发现、页面和人工校验仍暂停。

以下REV-067–068及更早段落保留历史状态；既往“定稿”不表示已完成独立全面语义验收。



## REV-067–068作品闭合与全类型补足结果

| 项目 | 当前结果 |
|---|---|
| 作品对象辨析 | 卡拉瓦乔人物页57项具名记录按版本、实物、复制品、失佚和归属争议拆为61个作品对象：新建60个，复用既有《圣马太与天使》第一版1个；原有两张1600年合同委托对象卡继续与实物分开 |
| 必要关系端点 | 新增57个非作品端点：人物15、机构28、地点12、家族2；仁慈山会机构与其教堂建筑分开，城市、政治实体、建筑、机构和内部作品不混类 |
| 初步对齐 | 新增117卡中103个具有同粒度Wikipedia与Wikidata双入口；3个只有同粒度Wikipedia、5个只有Wikidata、6个两者均无。后14个依据馆方、教堂、作品来源或其他适用记录保留，缺QID不判失败 |
| 内容补足 | 作品按题名、版本、年代、媒材、尺寸／状态、创作者归属、委托、原定／历史安置、现藏和证据组织；新增人物补姓名／别名／头衔、基本信息、身份标签、履历、当前作品链及亲缘证据边界；机构、地点、家族分别补性质、所在地／空间信息、职能或谱系范围 |
| 关系闭合 | 当前406条显式关系分别记录端点、方向、实际角色、时间／版本范围与证据；创作、委托、赞助、所有权、保管、安置、预定地点、师承、合作、朋友、成员、书信收件和程序实例等不再压成宽泛关联 |
| 全类型反查 | 文献补收件关系，事件与程序建立实例入口，人物补有据师承／合作／成员关系；家族、机构、地点接收作品或人物发出边的反向入口。术语和无可证关系对象不为降低孤点数强行连边 |
| 验收边界 | 本次完成的是第一章当前来源和已采纳事实的第一部分样例，不是卡拉瓦乔全集目录、所有外部人物的作品全集或家族全谱。争议归属不写确定创作边；不具名“St. Rosario”等无法独立识别对象继续暂缓 |

[REV-067–068过程](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md#rev-067068具名作品闭合与全类型内容关系复核2026-09-13)记录逐阶段范围、判断与未决；外部读取、身份核对及采用事实保存于[补足证据](../../03-processing/patrons-and-painters-chp-1/process/enrichment-evidence.jsonl)。以下REV-065及更早段落作为历史状态保留，旧数字和“部分完成”措辞不代表当前结论。

**本地验证：** 完整仓库闭包16步通过，274项测试通过；418张有效卡内容机械缺陷0，关系断端点、非法类型、缺反向映射和弱证据均为0，规则漂移0，系统结构契约130/130。72个无正式关系的知识元主要是术语、背景地点或当前无可靠关系对象，不自动构成缺陷。页面保持暂停前快照。

## REV-065审核问题修复结果

| 修复项 | 当前结果 |
|---|---|
| 宽泛关系 | 原81条`associated_*`逐条语义裁决为83条具体关系；2项因同时包含师承和合作而拆分。accepted卡片中宽泛关系为0 |
| 关系限定与展示 | frontmatter、卡内原向／反向关系表和关系索引均保留`time`、`role`、`scope`；反向入口指明原断言卡与原证据 |
| 卡拉瓦乔作品清单 | 补回1601年《圣彼得受难》，当前为57项页面具名对象；明确作品全集、页面清单、委托对象和具体实物四种口径 |
| 家族与婚姻端点 | 新建克勉八世、奥林皮娅·阿尔多布兰迪尼、保罗·博尔盖塞3个双语人物KU，并完成双站身份核对、字段补足及家族／配偶关系 |
| 初步对齐 | Wikipedia—Wikidata身份配对由172增至176；原126个无同粒度配对对象保持原处置，不以缺QID判定失败 |
| 有效范围与审计 | accepted从298增至301；正式有向边从219经细分和新增端点关系增至226；内容与关系审计不再混入19个遗留卡、旧正文模板、暂停阶段或旧字段协议；301卡来源均可追溯，437条显式来源定位错误数为0 |
| 暂停范围 | 知识发现、Topic—Theme—Dimension—Domain、页面数据和第六章均未启动或刷新 |

本轮解决了REV-064列出的工具契约、状态标题、证据回链、宽泛关系和已明确家族端点问题。关系阶段仍需继续处理已采纳人物清单中的具体作品：卡拉瓦乔57项中多数没有独立work端点，作品—创作者—委托／赞助—安置／保管链尚未形成完整图谱。这个缺口需要按知识元→对齐→补足→关系逐项闭合，不用孤点数量或页面阅读声明代替语义完成。

[关系决策计划](../../03-processing/patrons-and-painters-chp-1/process/relation-review-rev065.jsonl)保存81项逐条判断；[REV-065过程](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md#rev-065审核问题修复与关系阶段再收口)记录范围与结果。以下REV-064及更早段落作为历史状态保留，旧数字和待修项不代表当前结论。

**本地验证：** 完整仓库闭包通过；内容机械缺陷0；226条正式关系的断端点、非法类型、缺反向映射、弱证据均为0；来源错误引用0；当前系统缺陷P0／P1／P2均为0；规则漂移0；8个Skill入口有效；274项测试通过。76个孤立KU仅表示当前无正式关系，不自动构成应补关系。页面数据保持暂停前快照，未因本轮门禁刷新。

## REV-064全面进度审核：当前结论

| 阶段 | 核实结果 | 当前判断 |
|---|---|---|
| 摄入、处理 | 原章OCR／PDF指纹与定稿一致；80个语义跨度覆盖L1–980，无缺行或越界，含页码、摘要及跨页处置 | 已有可复用的阶段定稿；本轮确认记录完整，不以行覆盖证明实体穷尽 |
| 知识元 | accepted登记298个KU、12条断言；九类最小元数据及1594条来源的citation/location/sentence_summary均存在 | 现有登记完成；补足发现的必要具名端点尚未完整登记 |
| 对齐 | 当前记录172项WP—WD身份配对、126项未确认；发现结果表两行落后于卡片及证据，已校正 | 现有298项已有处置；本轮未重新逐个外网核验，无QID不自动构成缺陷 |
| 补足 | 有来源捕获、阅读／采用记录和分字段成果；既有记录声明193个WP对象／候选页全文阅读 | 部分完成；阅读声明、已有内容和完整实体转化是不同结果，不能记为298卡全面补足完成 |
| 关系 | 219条正式有向边、13种已用类型；端点均在accepted内，索引与边集合一致；221个KU连接、77个孤立 | 部分完成；65条associated_person及其他宽泛边待细分，正文中的缺端点／缺边事实待回查 |
| 发现、呈现、第六章 | accepted结构节点为0；页面保留298节点／173边旧快照；第六章保留暂停前材料和草稿 | 暂不开展／暂停；不计入第一章完成，也不为填空层级补做 |

**本次定位的优先问题：**

1. **作品与关系完整性尚未达标。** 卡拉瓦乔56条清单仍漏掉所存S5页面图注中的《圣彼得受难》（Crucifixion of Saint Peter）；两张圣保罗／圣彼得卡仍是委托对象，不能直接代替现存作品版本。56只是当前清单行数，不是页面完整提取数。阿尔多布兰迪尼家族卡已有具名成员和联姻内容，却无正式成员／婚姻关系；相关端点须核定后登记。
2. **卡内证据与状态展示有残留错误。** 卡拉瓦乔的反向创作关系把作品卡的“本卡S6”原样显示在人物卡，人物卡S6实际是Wikidata人物记录；应明确来源属于哪张卡并链接原始证据。297张卡仍有“REV-060 定稿”标题，按主要人物数量计价卡既有入边表又写“暂无正式关系”，不能据局部标题判断当前完成状态。
3. **新关系规则尚未落实到工具与数据。** 词表已有99种类型，但现有219条边均未使用time/role/scope；索引生成器也未保留这三个字段。不是所有边都必须填满限定，但需要限定的安置、所有权、任职等事实必须可保留，详见系统审查。
4. **审计口径及派生工件需要后续校正。** 有效KU为298，磁盘KU为317，另19个遗留对象不计成果；部分工具仍扫描全盘并要求旧模板，产生误导性缺项。关系索引219边是当前的，生成清单的关系索引输出哈希已过时；页面173边是暂停前快照。本轮未刷新这些工件。

**已做的报告纠正：** 朱利奥·罗斯皮廖西更新为配对通过Q155961，瓦尔蒙托内多利亚·潘菲利宫更新为配对通过Q16586138；依据既有卡片和REV-052对齐记录，不算本轮新增配对。此前结果表只有170个带QID的通过项，与顶部172项不一致，现已对齐。

**验证与同步：** 现行8个Skill入口／直接引用检查及规则漂移检查通过；关系机械检查未报断端点、非法类型或弱证据；258项pytest测试通过。这些检查不证明关系完整或事实均正确。核查时本地HEAD与远端main均为`63ecaa465188972766ded24e21643b2625638e19`，对应[Quality gate已成功](https://github.com/fengbaifan/PNP-Final-DATA/actions/runs/34621228757)。另有313个已跟踪文件的本地修改；本轮审查记录也留在工作树，未提交推送。

**后续顺序：** 先修正关系限定／证据回链的最小工具缺口及旧状态口径；再以已采纳事实盘点必要端点，逐项按知识元→对齐→补足→关系完成受影响路径；最后从正文与正式边双向核对并重新定稿。缺证事实明确暂缓，不无限扩张人物全集、网页外链或为孤点硬补关系。业务核查依据在[REV-064过程](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md#rev-064全面进度审核)，工具问题在[系统审查记录](../../06-runtime/governance/system-upgrade-log.md#rev-064进度审核中的系统一致性检查2026-09-12)。

以下按REV编号保留阶段沿革；旧轮次的数字与“定稿”措辞不代表当前状态，接续以本节为准。

当前有**172项Wikipedia—Wikidata身份配对通过，126项未确认配对**。本轮新增确认Giovanni Ludovico Bianconi、Johann Adam Andreas I、Gaspar Méndez de Haro和Niccolò Maria Pallavicini四人；Berlingero Gessi、Jacopo Salviati等年代冲突候选已明确排除。单封书信、具体事件、章内术语、未定名作品或争议稿组没有同粒度独立条目时，保留无配对状态，不借相关对象QID。

全章来源定位现为**1594条**。累计完整阅读**193个Wikipedia对象／候选页（178英文、14意大利文、1德文）**；配对通过后提取适用Wikidata字段，并保留rank、限定信息和有无引用状态。另采用王室收藏、国家博物馆、文化遗产目录、Treccani、Fondazione Zeri、官方期刊与开放学术文献补证。页面或字段未提供的信息保持未知，不由模板推断。

当前有**12条复杂断言、219条正式有向关系**。这些关系本身都有端点与证据，但不构成关系全集：正文中尚有具名对象未建KU，师承、合作、朋友、赞助、亲缘、任职、作品创作及安置／存放等事实也未全部转为具体关系。知识发现、知识涌现、页面与第六章均未开展。

**同步状态：** REV-055及此前成果已经同步；REV-060–063的关系审查、状态纠正和规则调整当前保存在本地工作树，本次任务未包含提交与推送。

## REV-062–063内容—实体—关系完整性复核

卡拉瓦乔卡的Wikipedia英文页revision 1372526492确有全文阅读记录，保存范围为正文、信息框、图注及注释／书目，共83995字符；未阅读所有外链作品页。问题发生在阅读后的转化：本轮把保存页面中的具名作品、版本或归属争议对象整理为56条，人物卡此前只保留5个代表性作品／工程组。页面自己也说明其作品总数存在40至80件等意见，所以56条只代表该页面的具名对象，不是卡拉瓦乔全集。

现有三张卡拉瓦乔相关work卡中，[《圣马太与天使》第一版](../units/works/caravaggio-giustiniani-rejected-altarpiece.md)是具体作品实体并已有`created_by`；[《圣保罗归化》](../units/works/caravaggio-conversion-saint-paul.md)和[《圣彼得殉难》](../units/works/caravaggio-martyrdom-saint-peter.md)两卡记录1600年委托对象，尚未拆成原约、早期版本与现存版本的独立作品实体。其余页面具名作品没有进入当前accepted集合，也没有相应创作、委托、安置、保管或所有权边。因此“Wikipedia全文已读”不能再被表述为“作品清单与关系已完成”。

同一页面中有据的Simone Peterzano师承、Giuseppe Cesari工作室雇用、Prospero Orsi／Onorio Longhi／Mario Minniti朋友关系、del Monte／Wignacourt／Colonna／Borghese保护与赞助、马耳他骑士团成员，以及各作品的教堂安置与馆藏变化，也需按端点和时间重建。当前流程已调整为从已采纳内容反查下列关系层：

| 关系层 | 需要分别表达 |
|---|---|
| 人物与作品 | 创作者、共同创作、委托、赞助、模特；委托对象、方案、版本和存世实物分开 |
| 作品与地点／机构 | 创作地、原定安置、历史安置、当前物理地点、保管机构、所有者及各自时间 |
| 人物专业关系 | 师承、合作、朋友、保护／赞助、雇用、任命、机构或家户隶属 |
| 亲缘与群体 | 父母子女、配偶、手足、其他有据亲属、家族成员；血缘、婚姻、家族和家户服务分开 |
| 文献与事件 | 作者、收件人、被论及对象、事件参与者及具体角色，避免都落入`associated_person` |

现有219条关系继续保留为有据关系；新增或替换必须回读来源。缺少端点的事实先回知识元阶段，再只重走受影响对象的对齐、补足和关系，不递归接收网页所有背景链接。详细证据与56条口径见[REV-062–063过程](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md#rev-062063从内容反查实体与关系完整性)。

## REV-061现有知识元与关系的语义分析（已被REV-063修正完成状态）

现有219条正式关系全部是带证据的显式记录，使用13种关系类型。其语义重心可以分为文献责任与内容、作品生产与委托、人物专业交往、机构／家族成员、空间与保存位置、事件参与以及程序实例七层。这是对第一章事实表达方式的分析，不是Topic、Theme、Dimension或Domain的知识发现。

| 分析维度 | 结果与解释 |
|---|---|
| 证据基础 | 172条（78.5%）直接以第一章为关系依据，47条（21.5%）来自已读外部页面或刊本。当前图谱首先表达第一章的叙事与证据网络，并非人物和艺术史关系全集 |
| 关系精度 | `member_of` 30、`authored_by` 22、`created_by` 22、`has_subject` 22、`located_at` 21等138条已有相对明确角色；三个 `associated_*` 类型共81条，需要依赖note解释具体语义 |
| 最大语义风险 | `associated_person` 65条，占全部关系29.7%；其中人物→人物29条、文献→人物22条、事件→人物8条、作品→人物6条，实际混合收信人、师承、赞助、任命、购买／收藏和事件参与等不同角色 |
| 对象覆盖 | archive 38/39、event 6/6、work 30/31、person 105/124已进入关系；term仅4/30、place 19/38、procedure 5/10。抽象术语与背景地点的低连接来自证据边界，不应为提高覆盖率强行成边 |
| 网络结构 | 共有107个弱连通分量；最大分量133个知识元，另有77个孤立知识元。圣路加学院25度、Antonio Ruffo与Mola各7度，是当前主要连接点；度数反映材料与补足密度，不能直接解释为历史重要性或未来主题 |

关系表达目前有三个需要在未来发现前控制的结构性问题。第一，宽泛关系依靠自然语言说明才能区分角色，直接按 `associated_person` 查询会把师承、赞助、收信和购藏混在一起。第二，同一历史行动有时同时表达为事件节点、文献节点和人物直连，例如提香授衔、萨基家户晋级、兰弗兰科申请；这些是不同观察层，不应当作三个独立历史事件累计。第三，`located_at` 同时承担原定场所、书中写作时馆藏和今日馆藏三种时间语境；当前note已作限制，但关系本身没有结构化时间限定。

本轮发现并修正六处具体的关系—证据表达问题：Thomas Baker胸像的委托与V&A馆藏两条关系不再声称未取得的V&A单件对象页支持，分别限定为第一章所记付款角色和书中时点馆藏；《圣马太与天使》第一版的作者与Giustiniani购藏关系改由柏林绘画馆对象记录直接支持；《当今》的作者关系和画家帮的罗马地点关系把版本／年代异文移回各卡争议字段，不再让关系note承担超出对应证据的事实。关系总数仍为219条。

当前关系图可以作为第一章第一部分的可追溯事实子图使用，但不能称为关系完整的定稿。应对正文缺端点事实和65条 `associated_person` 做语义回查，细分反复出现的角色，并为事件重叠和地点时间增加必要限定；这些属于第一部分的补做工作，不能根据节点度数自动生成主题，也不要求给没有事实依据的孤立对象补边。

## REV-060关系阶段集中审查（完成状态已由REV-063撤回）

| 审查项 | 定稿结果 |
|---|---|
| 原有正式关系 | 173条全部复核；保留165条，替换8条，另修订8条关系说明 |
| 新接收关系 | 54条：文献／事件13条、家族成员4条、机构成员21条、师承／赞助网络8条、方向或类型替换8条 |
| 当前正式关系 | 219条；全部具备明确端点、类型、方向、语境和对应证据 |
| 卡片呈现 | 298/298张有效卡均有“关系记录（REV-060定稿）”；221张可由正式关系连通，77张明确记录当前未接收正式关系 |
| 反向入口 | 从正式有向关系派生为可点击导航，不复制为第二条事实，不增加关系总数 |

本轮将七条笼统的“艺术家指向作品”关系改为“作品 `created_by` 创作者”，并将卡马塞伊付款令与贝尔托洛蒂研究的 `part_of` 改为有版本边界的 `derived_from`。新关系主要来自已经完整阅读的本章、Wikipedia对象页、Treccani／DBI、机构史、馆藏记录及书信刊本；具体采用依据见[关系审查过程](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md#rev-060关系阶段集中审查与定稿)。

未接收的候选包括：只在同页共现或正文互链的对象、仅共享地点或风格的对象、没有具名端点的关系、来源未实际读到的师承、只有工作室存画或购藏磋商却被扩大为委托的关系，以及为消除孤点而设的连接。人物活动地点与出生地没有压缩成无日期的 `located_at`；家户成员也不自动等同亲属。现有关系词表能够表达本轮有据事实，较具体的亲缘、赞助或收发角色暂由说明限定，没有为本轮数量扩充关系词表。

## REV-055剩余129卡的最终结果

| 类型 | 数量 | 本轮结果 |
|---|---:|---|
| archive | 23 | 书信、合同、自传、图录与论文补入发受者、日期、载体、刊布链、内容和支持范围；原件未得处逐项保留 |
| event | 3 | 图像询问、委托申请与家户晋级分别补入参与者、时间、结果和证据边界 |
| institution | 6 | 机构身份、沿革与官方来源完成；博洛尼亚善会与其会址建筑保持分离 |
| person | 54 | 37卡完成双站全文和结构字段，17卡完成消歧与检索后未决处置；人物允许多身份标签 |
| place | 20 | 全部完成双站身份核对，补入位置、历史名称、行政／政治归属和建筑沿革的适用字段 |
| term | 6 | 三项有相符概念页，三项按章内历史语义定义；均记录原语、证据角色和排除边界 |
| work | 17 | 三项完成双站对象核对，十四项由馆藏、目录、论文或明确未知状态完成题名、作者、年代、位置与版本边界 |
| **合计** | **129** | **129/129均已写入固定知识元路径，并有语义应用证据记录** |

129卡中69卡在本轮完成Wikipedia全文与Wikidata完整实体的双向核对；本轮共新读70个Wikipedia页（62英文、7意大利文、1德文）。其余对象的“未配对”是逐项检索和粒度判断后的结果，不是漏做。逐项采纳、暂缓、页面版本与写入前后SHA256见[过程记录](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md#rev-055剩余129卡对齐与补足收口)及[补足证据](../../03-processing/patrons-and-painters-chp-1/process/enrichment-evidence.jsonl)。

关键识别成果包括：

- Piola书信中的Giovanni Adamo确认为列支敦士登亲王Johann Adam Andreas I；官方王室资料用于裁决Wikidata内并列生卒日。
- 驻罗马的Marchese del Carpio确认为Gaspar Méndez de Haro；Piola的Marchese Pallavicini确认为Niccolò Maria Pallavicini。
- Valentin的风俗画定位为《有算命人的音乐聚会》；Rubens 1606年Chiesa Nuova委托定位为格勒诺布尔现藏第一版祭坛画。
- Albani、Ferri、Gavasetti、Guercino、Ricci对象补入规范题名、时间、位置或失佚状态；Guercino图像角色异文及Cortona稿组归属仍保持争议层级。
- artistic independence、artistic temperament和inspiration只作为第一章中的分析性知识元补定义，不预置为未来Topic、Theme、Dimension或Domain。

## 连续补足的已保存结果（REV-052）

本轮已原位更新 157 张详细卡：人物 64 卡（帕塞里、兰切洛蒂、蒙塔尔托、乌尔班八世、保禄五世、西斯笃五世、波佐、希皮奥内·博尔盖塞、卢多维科·卢多维西、安尼巴莱·卡拉奇、阿梅登、科雷乔、帕斯科利、卡米洛·潘菲利、莫拉、卡洛·皮奥、乔瓦尼·博纳蒂、吉米尼亚尼、托马斯·科克、阿伦德尔伯爵、巴尔多伊诺、毛里齐奥、朱利奥·罗斯皮廖西、安德烈亚·萨基、小安东尼奥·巴贝里尼、马尔切洛·萨凯蒂、皮耶特罗·达·科尔托纳、彼得罗·奥托博尼、弗朗切斯科·特雷维萨尼、穆利耶尔、布拉恰诺公爵、科尔泰塞、卡马塞伊、阿尔曼尼、卡拉瓦乔、文琴佐·朱斯蒂尼亚尼、雷尼、费迪南多·贡扎加、朱塞佩·盖齐、真蒂莱·贝利尼、提香、祖卡里、普罗卡奇尼、卢蒂、劳里、布兰迪、莫兰迪、奥达齐、努齐、切尔阔齐、范拉尔、瓦朗坦、乔万尼·安德烈亚·卡尔洛内、保罗·杰罗拉莫·皮奥拉、奇罗·费里、卡米洛·加瓦塞蒂、马里奥·明尼蒂、萨尔维奥·萨维尼、马蒂亚·普雷蒂、保罗·圭多蒂、塞巴斯蒂亚诺·里奇、安东尼奥·鲁福、卡洛·马拉塔、阿尔泰米西娅·真蒂莱斯基）；地点 17 卡（罗马、圣彼得大殿、威尼斯、佛罗伦萨、博洛尼亚、圣母大殿、米涅瓦圣母堂、谷地圣安德烈堂、帕尔马、意大利地域、米兰、摩德纳、瓦尔蒙托内、科尔托纳、佩鲁贾、帕拉蒂尼圣塞巴斯蒂安堂、瓦尔蒙托内潘菲利宫）；机构 11 卡（阿尔卡迪亚学会、卡萨纳滕塞图书馆、巴尔纳伯会、戴蒂尼会、嘉布遣会、奥拉托利会、耶稣会、巴贝里尼家族／家户混合记录、奥古斯塔图书馆、画家帮、圣路加学院）；术语 24 卡（教皇亲族任用、祭坛画、领衔教堂、画商、鉴赏爱好者、特定保护人服务、家户、本府画家、湿壁画技法、可移动画廊画、成对绘画、bozzetto、modello、祈祷图像、历史画、自画像、群青、新闻纸、caparra、基督骑士荣衔、行宫伯爵、荣誉侍从、圣年、同巢之鸟）；程序10卡（赞助人资助学习旅行、保护与职业引介、展览售画与自我宣传、委托合同订立、题材与图像志协商、预备稿提交、按主要人物计价、付款与结算、工作室存画交易、艺术家荣衔与职位授予）；文献 15 卡（《当今》《赞助人与画家》、阿梅登1642年手稿、科克1620年10月8日信、巴尔多伊诺任命文字、瓦萨利证词刊引、Pascoli《特雷维萨尼传》手稿、阿尔曼尼《书信集》、阿尔曼尼致潘菲利信、贝尔托洛蒂艺术家研究、卡马塞伊付款令、1633材料约定、莫拉1657工程条款、卡拉瓦乔1600合同、1621学院章程）；作品 13 卡（博尔盖塞肖像头部、萨基《圣安东尼复活死者》小幅版本、卡马塞伊圣塞巴斯蒂安祭坛画及施洗稿、莫拉四元素与空气方案、卡拉瓦乔圣保罗／圣彼得委托及圣马太退画、雷尼《正义拥抱和平》与《屠杀婴孩》、普桑《屠杀婴孩》与《春》）；事件3卡（提香1533授衔、画家帮成立、1633学院措施）。补入字段与来源，保留日期、版本和归属异文。全章来源定位记录现为 1389 条，不等于独立来源数。

博尔盖塞肖像的被表现者已有对应依据；两件实物的馆号、尺寸、材质和款项分开，仍不确定本章所指版本，不强填 QID。Ludovisi 的 Montecitorio 误归及 nepotism 的错误 Wikidata 词源项未采用；其他关键裁决见各卡。

MS.5001 的官方修复项目记录已支持同馆号、题名、17世纪和纸本载体；手稿正文未读，仍无确认Wiki配对。卡拉奇兄长／堂兄身份、博洛尼亚古代纪年及大学约定创始年已分别处理；祭坛画的媒材范围与领衔教堂的制度／赞助边界已补入。

已取得其余页面继续按完整阅读要求处理；批量采集中出现的 HTTP 429 仅是访问失败，不证明无条目或处理完成。本段记录的是REV-052当时的补足状态；补足后的全章关系已由REV-060收口。逐项成果在固定 KU 路径，过程与写入指纹见 [REV-052 过程](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md#rev-052连续补足与关系推进)及同包 enrichment-evidence.jsonl。

## 前轮字段化与补足结果（REV-045）

| 步骤 | 已保存结果 | 边界 |
|---|---|---|
| 1．人物样例 | [圭尔奇诺](../units/persons/guercino.md)：姓名、基本信息、身份、亲缘、逐项履历、作品及研究文献分开 | 复用既有事实与证据，不计新增补足 |
| 2．关系表达 | 检查类型、方向、端点及证据；正式关系仍在元数据，正文链接只作导航 | 本段为REV-045样例；全章正式关系后来由REV-060定稿 |
| 3．其他类型样例 | [作品](../units/works/plague-at-ashdod-1631.md)、[书信](../units/archives/testi-fontana-bernini-letter.md)、[家族](../units/families/aldobrandini-family.md)各一张原位整理 | 购藏／展出、发收／刊引、成员／联姻分别表达；既有争议保留 |
| 4．继续补足 | [那不勒斯](../units/places/naples.md)：WD 属性、遗产面积范围和书目责任；[格列高利十五世](../units/persons/gregory-xv.md)：原名、亲缘、教育、任职与来源异文 | 那不勒斯 Getty 原站未核、Brill 仅索引可读；教皇任命和典礼日期等继续待证 |

六张卡均沿固定路径更新，未新建知识元、关系或发现内容。四张纯格式样例元数据及来源完整保留；两张补足卡仅追加有阅读范围的来源记录。必要检查确认有效对象与正式关系数不变、六卡链接有效、原章 Markdown／PDF 哈希不变；不把这些检查当作全章语义验收。过程与采集／采用记录见 [knowledge.md](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md#rev-045字段化样例关系表达与后续补足) 及其 [enrichment-evidence.jsonl](../../03-processing/patrons-and-painters-chp-1/process/enrichment-evidence.jsonl)。

## 三位画家补足结果（REV-038）

| 对象 | 本组已保存 | 尚存限制 |
|---|---|---|
| [圭尔奇诺](../units/persons/guercino.md) | WD 适用字段、亲缘／师承、账簿分工；区分迁居与购屋，采用有据工作年表 | 迁居日、账簿分工、具体委托实物及荣衔仍待原档 |
| [多梅尼基诺](../units/persons/domenichino.md) | 亲缘、婚姻、任命、训练及壁画时间；死亡日异文逐项记录 | 6／15／16 日异文未消除，学院入会年原页及其他字段继续待证 |
| [兰弗兰科](../units/persons/giovanni-lanfranco.md) | 亲缘、学院职务、年精度履历、多角色与 NGA 作品对象资料 | 卒日及具体出生地点保留异文；原清册、论文和本章稿本尚未核定 |

三卡已保存本组内容和证据，未标为全面补足完成。过程与采用／暂缓依据见 [knowledge.md](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md) REV-038 及同目录 [enrichment-evidence.jsonl](../../03-processing/patrons-and-painters-chp-1/process/enrichment-evidence.jsonl)。

## 本轮家族补足结果（REV-037）

| 对象 | 已保存内容 | 保留缺口 |
|---|---|---|
| [阿尔多布兰迪尼](../units/families/aldobrandini-family.md) | 双语描述、名称／成员线索、联姻和收藏转移、WD 字段、档案与研究入口；1646／1647 婚期异文作有据裁决 | 早期与后期支系、完整继承链、具体作品和宅邸权属、规范库原站 |
| [博尔盖塞](../units/families/borghese-family.md) | 双语描述、家族与具体赞助人区分、分期营建及收藏迁出／购藏、WD 字段及清册入口；校正一条原文句意摘要 | 创始人和成立年、威尼斯身份范围、成员日期冲突、逐件藏品权属 |
| [佩雷蒂](../units/families/peretti-family.md) | 双语描述、母系传名及部分亲缘、家户服务边界、分期财产与收藏流散、WD 字段及文献线索 | 谱系内部矛盾、收养与爵位继承文书、作品逐项流传、规范库原站 |

本组 3/3 已完成实际页面阅读与内容稿保存，**不表示 3/3 的全部历史事实与适用字段已验证**。未增加家族成员 KU、作品 KU 或正式关系。过程见 [knowledge.md](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md) REV-037；采集版本、字段和采用／暂缓依据见 [补足证据](../../03-processing/patrons-and-painters-chp-1/process/enrichment-evidence.jsonl)。

## 初步对齐结果（REV-034）

| 结论 | 数量 | 交接 |
|---|---:|---|
| 身份配对通过 | 160 | 人物 91、家族 3、机构 15、地点 34、术语 13、作品 3、文献 1；比较身份语义且核对同语种 WP↔WD。事实属性和具体关系仍须分别有证据 |
| 尚无配对 | 108 | 保留原文对象；检索多仍限登记名及同名 sitelink，继续原语题名、责任者、版本、馆藏或权威标识检索，不称没有条目 |
| 范围待对齐 | 13 | 家族与家户、建筑与馆藏、历史地理与现代政体、原词与现代概念的范围不能直接替代 |
| 候选待证 | 8 | 有候选对象或内部线索，但独特身份／版本锚点不足 |
| 已排除误配 | 5 | Gessi、Fontana、Perugini、Salviati、Negri 的命中项不是本章人物；正确对象仍待配对 |
| 版本待证 | 4 | 《L’Hoggidi》、Borghese 肖像头部及 Caravaggio 两项合同／作品的版本关系待核 |
| **合计** | **298** | **160 通过＋138 未确认；未决不删除、不填造 QID** |

160 项包含既有《阿什杜德的瘟疫》和泰斯蒂两项；本轮新增确认 158 项，补齐圭尔奇诺、多梅尼基诺、兰弗兰科及那不勒斯此前欠缺的反向核对。154 项采用英文页，6 项回退意大利语页；具体语言和版本以证据记录为准。18 张人物卡原位规范显示名，并保留原名作为检索异名。没有把 QID 配对、API 返回成功或字段数量当成整卡验证完成。

查询范围：298 项均尝试英文登记名；未命中或存在歧义者补查适用别名及部分意大利语页面。187 项至少读到一个带 QID 的候选对象页及该 WD 实体（其中有明确误配），余下 111 项另作 WD 同标题 enwiki sitelink 查询，均未命中；另有 10 项 WD 名称搜索未命中、1 项受限，以及 Armanni 名称搜索取得 1 个尚未确认的候选。**同标题查询不等于完整名称／ISBN／馆藏检索**；剩余原语、版本和对象级检索逐项交补足。短时 HTTP 429 后停止对应请求，改为间隔查询；失败记录不当无条目证据。

必要过程及复杂裁决见 [knowledge.md](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md) 的 REV-034；逐项查询、页面版本、两侧链接、身份判断和未决项保存在 [alignment-evidence.jsonl](../../03-processing/patrons-and-painters-chp-1/process/alignment-evidence.jsonl)。160 项通过只读了身份需要的导言及指定消歧段，**不宣称新读完 160 个 Wikipedia 全文**。定稿沿本文件和既有 KU 路径更新，证据留在 03，不另建重复最终版。

## 提取与分类修订基线（REV-016）

此前 270 个有效 KU 的统计属首次提取。复查补入 26 个对象：21 项文献与档案、3 处建筑、2 项作品；另外用同书索引明确 1 个既有暂缓人物，纳入有效集合，故为 270＋26＋1＝297。新增 36 条来源支持关系；上一轮 137 条中的 Francesco Barberini 保护人关系纠正了精确行号。

原 publication 类型改为 **archive（文献与档案）**，目录由 units/publications 迁为 units/archives，原有文献不复制新副本。有效 archive 为原 18 项加新增 21 项，共 39 项。39 项中包含来源书目、被引书信、手稿/条款/收据及学术文献，不等于本次读过 39 份原件。

## 分类边界与实例

| 原文指称的对象 | 类型 | 本章处置 |
|---|---|---|
| 城市、行程、出版地点“威尼斯” | place | 保留 Venice 地点卡 |
| 共和国、政府等政治行动主体 | institution | 规则明确；不从本章城市名无证生成“威尼斯共和国” |
| 宫殿、教堂等建筑与空间 | place | 新增 Valmontone 乡间宅邸及两处宫殿，区别于城市/家族/内部作品 |
| 独立建筑构件、雕塑、绘画、稿本、艺术图册原作 | work | Thomas Baker 胸像明确为 sculpture；作品位置不改变作品类型 |
| 管理图书馆或收藏的机构 | institution | 馆藏语境中的图书馆仍为机构，建筑空间另作判断 |
| 书信、手稿、合同、收据、章程、图录、学术著作/论文 | archive | 包含所有文献，不以出版、ISBN 或年代作门槛 |
| 同一艺术图册的文献用途，或学术图册 | 按对象身份判断 | 视觉原作归 work，记录/研究性质的文本归 archive；不同用途不自动复制同一对象 |

类型契约见 [taxonomy-registry.md](../../01-domain/taxonomy-registry.md)。材料名/颜色概念可为 term；具体颜料批次或施工设备实物、神话图像角色等存在当前类型不能直接充分表达的边界，已在过程记录单列，未强塞为作品或现实人物，也未为凑类型新增类别。

## 阶段状态

| 阶段 | 当前成果 | 尚存边界 |
|---|---|---|
| 摄入 | 第一章完整 OCR 与 PDF、书名版权页已定位 | 为本章消歧另定向读取同书书目及索引，未展开其他章节 |
| 处理 | OCR L1–980 已逐行语义阅读，正文/脚注/跨页有处置 | 行号覆盖不是对象提取完整性的证明；REV-016 已回查具体遗漏 |
| 知识元 | 现有298个登记对象均有当前成果 | REV-063发现补足内容中的具名关系端点尚未全部建KU，受影响范围重新处理中 |
| 对齐 | 298项均有结论；当前172项身份配对通过 | 126项未确认均有检索后结论；不强制分配QID |
| 补足 | 现有298卡均有处置；193个WP对象／候选页全文已读；来源定位1594条 | 新识别端点须逐项补足；全文已读不等于内容已经完整转成实体 |
| 关系 | 219条已有正式有向关系可追溯；298张现有卡均有可读关系区 | 部分完成；须反查正文中的作品、师承、合作、朋友、赞助、亲缘、隶属及安置／存放事实 |
| 发现与页面 | 暂不开展 | 没有新增涌现结构或刷新页面 |

[摄入处理定稿及完整逐行分析](../../03-processing/patrons-and-painters-chp-1/results/stages.md) · [必要处理记录](../../03-processing/patrons-and-painters-chp-1/process/stages.md) · [知识判断与边界修订过程](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md)

## 当前成果统计

当前正文仍以本章证据为主，外部身份与事实支持分开记录。当前172项身份配对通过；其中《瘟疫》Q3900760 与泰斯蒂 Q594614 沿用既有适用 WD 属性，其余配对对象按类型接收本轮可用字段。身份配对不等于整卡事实全部验证。各卡保留 source_backed 总体状态，正文区分具体外部支持、初步对应、来源差异及未验证内容。

| 类型 | 数量 |
|---|---:|
| archive | 39 |
| event | 6 |
| family | 3 |
| institution | 17 |
| person | 124 |
| place | 38 |
| procedure | 10 |
| term | 30 |
| work | 31 |
| **合计** | **298** |

有效对象的唯一登记见 [accepted.yml](../accepted.yml)，断言见 [claim-registry.yml](../quality/claim-registry.yml)，关系原记录在 KU 的 relations，派生索引见 [relation-index.yml](../quality/relation-index.yml)。第六章专属 19 个草稿仍未接收；其中两张文献草稿只机械迁移类型/路径，未进行第六章语义处理。

## 可解决与仍未解决的问题

- **已解决**：同书索引 Domenichino 子条明确第 4 页所述枢机为 Scipione Borghese。原候选卡沿用路径并限定该处身份，不再把整个人物都笼统暂缓。
- **已补足**：Armanni 信集题名/卷数/年份、Bertolotti 缩题、Grassi 1957 论文的刊名及页码，均可由同书书目定向核对。
- **新增补证**：泰斯蒂致丰塔纳的信已据 Fraschetti 第十二章第 108 页注 1 刊引及扫描图补入罗马、1633 年 1 月 29 日；泰斯蒂的 1593 年 8 月 23 日按 Treccani 区分为受洗日，不照搬 WD 为确定生日。刊引不等于手稿原件。
- **尚未解决**：第 17 页头部肖像端点与具体版本、无题名借阅书的版本、若干缩引文献、部分原件文本与当今馆藏；Alessandro Vasalli、Berlingero Gessi、Jacopo Salviati、授 Giuseppe Ghezzi 荣衔的帕尔马公爵等身份仍受证据限制。Giovanni Adamo 已在 REV-055 确认为 Johann Adam Andreas I。
- **类型待决**：具体材料/设备实物与图像角色不能不加说明地套入当前类型；当前相关文字与图像题材已保留，后续依据实际对象决定是否扩展。
- **沿用的重要纠正**：费率为 Domenichino 130、Lanfranco 100、Guercino 报 125 ducats；萨基家户属于 Antonio 而非 Francesco；《瘟疫》已有稿后商议完成，《春》为另行新委托；稿本争议、逸事与“首次引入”推测不转确定事实。

source_backed 保留来源支持基线；REV-026–030 已为八卡新增有范围限定的外部来源，不能把全库内容概括为仅来自本书。同书书目和索引仍非独立外部来源；Wiki 两站也不当作两份独立事实证据。主 Agent 直接分析及自查，不称独立验收。

## 登记收口的结果与暂缓项（REV-033）

| 本轮处置 | 当前结果 |
|---|---|
| 289 张早期短稿 | 原路径更新双语名称与描述、统一来源子字段、按类型的已有信息及具体缺口；不是从模型记忆填写人物全集或作品现状 |
| 8 张已补足卡 | 保留原有外部内容、版本、证据与验证状态；本轮不重复外采或提升状态 |
| 新增 1 个 term | [新闻纸](../units/terms/news-sheets.md)：第一章第 19 页 L778–783 的 Lauri 阅读与社交语境；类别不冒充某份具体报纸 |
| 来源定位 | 补原先仅有页码的精确行段，跨页及不同事实分列来源；书目页 412／414／424 与索引页 453 经对应 PDF 文本页号核对 |
| 名称与事实纠正 | Gessi 书信中文与人物统一；无题名通信采用已知姓名的双语描述；《L’Hoggidi》保留本章的 1627 首刊说及后来重印说；REV-034 新发现 Treccani 的 1623 首刊／1627 重印差异，见当前对齐裁决；Colnaghi 图录不独立证明已经成交 |
| 去重及对象边界 | 不改稳定路径，不因城市／家族／宫殿／内部作品同名而合并；章程与机构、草稿与作品、现画完成与新订作品分开。未新增虚构关系 |

下列是本阶段对处理定稿中余下线索的具体处置，**暂缓不等于排除**。表内已登记对象的属性缺口直接交对齐／补足；需要新增对象而身份不足的线索保留原行段，取得依据后回写同一登记结果。

| 来源线索与章页／行号 | 登记处置及理由 | 后续责任 |
|---|---|---|
| Counter Reformation；第 3 页 L15–25 | 保留历史运动指称；本段只是赞助与控制的背景，没有界定运动对象、时段和组织，不强塞为机构或预设研究主题 | 对齐时判断作为历史事件／概念的对象边界；当前类型与独立成稿暂缓 |
| 神话、圣经及画题人物；第 9 页 L295–319，第 10 页 L357–371，第 11 页 L407–412 | Juno、Chloris、Zephyr、Ganymede、Iris、Turnus、圣者、Alexander、Samson、Pope Leo、Attila 等留在图像／题材语境，不能据被描绘关系填写现实生平或事件 | 角色建模与具体作品版本核对后决定是否独立成稿；不自动新增 person |
| 四季、四元素、绘画寓意与系列委托；第 9–10 页 L308–319、357–371 | 具体四元素与空气方案已有 work；泛举题材、系列安排先作为作品或委托属性，不按同一称谓重复造概念卡 | 实际需要独立定义且有充分材料时再判断 term／procedure |
| 行会、镀金工、家族传艺及艺术家社会地位；第 17–18 页 L678–736，第 21 页 L862–893 | 未具名行会不成为虚构机构；镀金工保留职业与会员条件，传艺保留人物／家族语境，社会地位解释保留断言责任 | 核具体组织、角色或过程，不从一个概括自动拆多个 KU |
| 颜料、绷框、底料、脚手架；第 13 页 L486–523 | 群青已有 term，费用条款已有 archive／procedure；Mola 合同卡保留原 OCR 材料词形，未核古色名不强译现代标准色。未识别具体批次或器物 | 概念与实物分开；实物的类型能力待实际对象出现后决定 |
| Osimo；第 13 页 L509–510 | 当前在 Cesare Leopardi d’Osimo 名称内，不能仅从姓名附属语确认为发信、出生或居住地点 | 人物及信件对齐后判断地点关系 |
| Bernini 父亲／兄弟、Mario 的两子、Costaguti 总管及其妹妹；第 20–21 页 L845–846、858–874 | 关系角色有记录但未具名；总管的妹妹不能误写为侯爵的妹妹 | 逐个核身份后判断新增人物，当前保留匿名角色 |
| Compagnia della Morte；第 22 页 L905–926 | 原文已修正的 Rosa 传说，不能作为真实组织成员或已发生事件写回 | 仅保留传说及否决理由，除非出现新证据 |
| Hervey；第 3 页 L48；Felici；第 4 页 L89–95 | 缩引分别保留在 Coke 信、Ameyden／更替论述的引用链；缺确切书名／版本，未以同姓猜配 | 定向书目对齐后决定 archive 或责任者卡 |
| Panciroli、Ortolani；第 5 页 L142 | 转引链两层，不能当作直接读原著；本处不足以唯一登记两部文献 | 核原题、版次及转引责任 |
| Montalto、Baudi di Vesme；第 6–7 页 L178–189、229–237 | 服务、旅行与工程引文的短引；区别 Montalto 书目姓氏与 Peretti-Montalto 人物 | 逐条书目核定，不按同名合并 |
| Incisa della Rocchetta、Battisti；第 7 页 L229–237 | 对应 Sacchi 等记载的缩引，未读全著 | 核作者与版本，再登记文献 |
| Soprani、Golzio、Rothlisberger；第 8 页 L278–283 | Piola、津贴及 Claude 研究的引用线索；具体对象属性已有卡，不伪造缩引题名 | 书目对齐；Golzio 在第 12 页的其他引文分开判断 |
| Gualandi、Giuseppe Agnello、von Derschau、Ruffo；第 9 页 L321–330；Bertolotti、Friedlaender、Bottari、Luzio、Bellori；第 10 页 L372–377 | 具体条款、信件、收据与作品已登记；Bertolotti 缩题已据同书核定；其余短引的书名／版本及责任者仍须分别确认，Bellori 人物已有卡 | 复用已登记对象，只为实际不同文献新增 archive |
| Claretta、Pollak、Costello、Friedlaender；第 11 页 L415–425 | Gini 与 Lanfranco 具体信件已登记；短引载体未全部展开 | 不把所引信件、刊印载体及未读交叉章节混成同一来源 |
| Grassi、Briganti、Waterhouse、Wittkower、Golzio、Tacchi-Venturi；第 12 页 L461–472 | Grassi 论文已定名；Waterhouse 的个人提供信息不冒充论文；其他缩引保留。Sacchi／Camassei 反例及争议稿本均已有对象 | 区分个人告知、书目引用与归属主张 |
| Ferdinand Boyer、Faldi、Luzio、Mancini、V. Ruffo；第 14 页 L562–570 | 保留市场／价格材料的引用链；Mancini 人物、各具体信件已有卡，V. Ruffo 不能合并 Antonio Ruffo | 责任者与文献版本对齐 |
| Costello、Baldinucci、Malvasia、Fraschetti、Passeri、Pascoli、Wittkower；第 15–17 页 L614–615、628–677、699–710 | 已登记人物及八卡实际外读资料复用；没有把一条简称扩展为整套著作已读 | 将具体引用与外部已读范围逐项对应，不重复造书 |
| Pevsner、Mahon、Missirini、Hoogewerff；第 17 页 L711–712；Narducci、Hoogewerff、Pascoli；第 20 页 L847–853 | 学院史及家庭态度引用仍有未展开版次；年份是书目年，不是人物生卒 | 定向核版本与页码；脚注反例保留 |
| G. Delogu、Bottari、Claretta；第 21 页 L894–900 | 1635 喜剧未寻得，Bianconi／Negri 两信已登记；引用载体另待辨 | 不伪造剧本题名或刊印载体身份 |
| 第 17 页 Borghese 肖像版本；第 10、15 页未具名退画、存画；第 9 页借阅书；各语境公爵／枢机全名 | 已可按局部指称登记的对象继续有效；例如第 4 页 Scipione 身份已成立，不能据此自动合并第 17 页肖像 | 初步对齐解决具体身份与版本，尚无配对者保留待证 |

短引可用 archive 类型，暂缓原因是对象／版本不足，绝非因为“只是脚注”。登记阶段 REV-033 未新建来源本体或改变当时八类表；候选处置保留在本结果，后续不另建同用途总账。

## 知识元目录

下表是唯一正文入口与首项来源定位；跨页、多来源及句子摘要在各卡 sources 分条列明。全文已用三部分组织，未知字段仍如实标待补。后续沿这些固定路径更新。

| 类型 | 知识元 | 首项来源定位 | 初步对齐 |
|---|---|---|---|
| archive | [圣路加学院章程（1621 年确认）（Statutes of the Accademia di S. Luca (confirmed in 1621)）](../units/archives/accademia-statutes-confirmed-1621.md) | 第一章；印刷页 17；OCR L690–691 | 尚无配对 |
| archive | [《罗马城记述》（1642）（Account of the City of Rome (1642)）](../units/archives/ameyden-relazione-1642.md) | 第一章；印刷页 4；OCR L89–92 | 尚无配对 |
| archive | [阿尔曼尼《书信集》（Armanni's Collected Letters）](../units/archives/armanni-delle-lettere.md) | 第一章；印刷页 9；OCR L329–330 | 尚无配对 |
| archive | [温琴佐·阿尔曼尼致卡米洛·潘菲利的装饰建议信（日期未明）（Letter from Vincenzo Armanni to Camillo Pamfili on Decoration (undated)）](../units/archives/armanni-pamfili-letter-undated.md) | 第一章；印刷页 9；OCR L329–330 | 尚无配对 |
| archive | [法布里齐奥·阿拉戈纳致曼图亚公国大臣的信（1621-10-09）（Letter from Fabrizio Arragona to a Mantuan Ducal Minister (1621-10-09)）](../units/archives/arragona-mantua-letter-1621.md) | 第一章；印刷页 14；OCR L542–547, 567–568 | 尚无配对 |
| archive | [毛里齐奥任命巴尔多伊诺为本府画家的文字（Maurice of Savoy’s appointment of Baldoino as his painter）](../units/archives/baldoini-painter-appointment.md) | 第一章；印刷页 6；OCR L173–175,188–189 | 尚无配对 |
| archive | [贝尔托洛蒂《罗马的博洛尼亚、费拉拉及原教皇国其他艺术家》（Bertolotti's Bolognese, Ferrarese and Other Artists of the Former Papal States in Rome）](../units/archives/bertolotti-artisti-bolognesi.md) | 第一章；印刷页 10；OCR L372–374 | 尚无配对 |
| archive | [乔万尼·洛多维科·比安科尼致菲利波·埃尔科拉尼侯爵的信（1762-11-22）（Letter from Giovanni Ludovico Bianconi to Marchese Filippo Hercolani (1762-11-22)）](../units/archives/bianconi-letter-1762.md) | 第一章；印刷页 21；OCR L896–898 | 文献身份已由刊本定位 |
| archive | [卡马塞伊圣塞巴斯蒂安祭坛画付款令刊录（Published Payment Order for Camassei’s Saint Sebastian Altarpiece）](../units/archives/camassei-sebastian-receipt.md) | 第一章；印刷页 10；OCR L335–338,372–374 | 尚无配对 |
| archive | [卡马塞伊与乌尔班八世的合同（1633）（Contract between Camassei and Urban VIII (1633)）](../units/archives/camassei-urban-contract-1633.md) | 第一章；印刷页 13；OCR L514–516 | 尚无配对 |
| archive | [卡拉瓦乔两幅祭坛画的合同（1600）（Contract for Caravaggio's Two Altarpieces (1600)）](../units/archives/caravaggio-altarpieces-contract-1600.md) | 第一章；印刷页 11；OCR L397–401,421 | 尚无配对 |
| archive | [本韦努托·切利尼自传《生平》（The Life of Benvenuto Cellini）](../units/archives/cellini-autobiography.md) | 第一章；印刷页 16；OCR L634–635 | 身份配对通过 Q4014886 |
| archive | [托马斯·科克致托马斯·霍华德，阿伦德尔伯爵信（1620年10月8日）（Letter from Thomas Coke to Thomas Howard, Earl of Arundel, 8 October 1620）](../units/archives/coke-arundell-letter-1620.md) | 第一章；印刷页 3, 4；OCR L40–44,48,53–55 | 尚无配对 |
| archive | [科尔纳吉图录（1961 年 5–6 月，第 2 号）（Colnaghi Catalogue (May–June 1961, no. 2)）](../units/archives/colnaghi-catalogue-1961.md) | 第一章；印刷页 12；OCR L467–468 | 尚无配对 |
| archive | [朱塞佩·德·罗西斯致安东尼奥·鲁福的信（1663-09-22）（Letter from Giuseppe de Rosis to Antonio Ruffo (1663-09-22)）](../units/archives/de-rosis-ruffo-letter-1663.md) | 第一章；印刷页 23；OCR L957–958, 971–972 | 尚无配对 |
| archive | [奇罗·费里致安东尼奥·鲁福的信（1672-09-19）（Letter from Ciro Ferri to Antonio Ruffo (1672-09-19)）](../units/archives/ferri-ruffo-letter-1672.md) | 第一章；印刷页 23；OCR L974–978 | 尚无配对 |
| archive | [加瓦塞蒂皮亚琴察壁画委托条款（1624）（Terms for Gavasetti's Piacenza Frescoes (1624)）](../units/archives/gavasetti-piacenza-contract-1624.md) | 第一章；印刷页 9；OCR L323–326 | 文献身份通过来源链定位 |
| archive | [贝尔林杰罗·杰西致切萨雷·莱奥帕尔迪·多西莫的信（1647-07-10）（Letter from Berlingero Gessi to Don Cesare Leopardi d’Osimo (1647-07-10)）](../units/archives/gessi-leopardi-letter-1647.md) | 第一章；印刷页 13；OCR L486–489, 509–510 | 尚无配对 |
| archive | [奥诺拉托·吉尼关于科尔托纳选题的信（1666）（Onorato Gini’s Letter on Cortona’s Choice of Subjects (1666)）](../units/archives/gini-cortona-letter-1666.md) | 第一章；印刷页 11；OCR L383–385,415–418 | 尚无配对 |
| archive | [列支敦士登亲王约翰·亚当·安德烈亚斯致保罗·吉罗拉莫·皮奥拉的委托信（1690-02-03）（Commission Letter from Johann Adam Andreas of Liechtenstein to Paolo Girolamo Piola (1690-02-03)）](../units/archives/giovanni-adamo-piola-letter-1690.md) | 第一章；印刷页 10；OCR L354–356,376 | 文献身份已由刊本定位 |
| archive | [格拉西关于科尔托纳与多利亚潘菲利宫画廊草稿的论文（1957）（Grassi's Article on Cortona and the Bozzetti for the Doria Pamphili Gallery (1957)）](../units/archives/grassi-cortona-bozzetti-1957.md) | 第一章；印刷页 12；OCR L461–463 | 文献身份已由期刊原文定位 |
| archive | [圭尔奇诺致安东尼奥·鲁福的信（1649-09-25）（Letter from Guercino to Antonio Ruffo (1649-09-25)）](../units/archives/guercino-ruffo-letter-1649.md) | 第一章；印刷页 14；OCR L548–552, 569–570 | 尚无配对 |
| archive | [乔万尼·兰弗兰科致巴贝里尼枢机的信（1640-07-14）（Letter from Giovanni Lanfranco to Cardinal Barberini (1640-07-14)）](../units/archives/lanfranco-barberini-letter-1640.md) | 第一章；印刷页 11；OCR L408–425 | 文献身份通过来源链定位 |
| archive | [《当今》（1627）（L'Hoggidi (1627)）](../units/archives/lhoggidi-1627.md) | 第一章；印刷页 3；OCR L45–47 | 版本待证 |
| archive | [明尼蒂在奥古斯塔的委托条款刊录（1617）（Published Terms for Minnitti's Augusta Commission (1617)）](../units/archives/minnitti-augusta-terms-1617.md) | 第一章；印刷页 9；OCR L321–322 | 尚无配对 |
| archive | [莫拉借阅的神谱书（题名未明）（Genealogy of the Gods Borrowed by Mola (title unidentified)）](../units/archives/mola-borrowed-genealogy-gods.md) | 第一章；印刷页 9；OCR L312–316 | 尚无配对 |
| archive | [莫拉借阅的维吉尔注释本（版本未明）（Annotated Virgil Borrowed by Mola (edition unidentified)）](../units/archives/mola-borrowed-virgil-commentary.md) | 第一章；印刷页 9；OCR L312–316 | 尚无配对 |
| archive | [莫拉与潘菲利瓦尔蒙托内工程的合同条款（1657）（Contract Terms for Mola and Pamfili's Valmontone Project (1657)）](../units/archives/mola-pamfili-contract-1657.md) | 第一章；印刷页 13；OCR L505–506,514–519 | 尚无配对 |
| archive | [保罗·内格里致圣托马索侯爵的信（1676-12-24）（Letter from Paolo Negri to the Marquis of S. Tommaso (1676-12-24)）](../units/archives/negri-san-tommaso-letter-1676.md) | 第一章；印刷页 21；OCR L889–900 | 尚无配对 |
| archive | [弗朗切斯科·诺韦蒂致安东尼奥·鲁福的信（1670-03-22）（Letter from Francesco Novetti to Antonio Ruffo (1670-03-22)）](../units/archives/novetti-ruffo-letter-1670.md) | 第一章；印刷页 18；OCR L750–758 | 尚无配对 |
| archive | [帕斯科利《特雷维萨尼传》手稿（MS.1383）（Pascoli’s Manuscript Life of Francesco Trevisani (MS.1383)）](../units/archives/pascoli-trevisani-life-ms1383.md) | 第一章；印刷页 7；OCR L236–237 | 尚无配对 |
| archive | [《赞助人与画家》（Patrons and Painters）](../units/archives/patrons-and-painters.md) | 书名页及版权页；无章节、未编号；OCR L3–17 | 尚无配对 |
| archive | [卡洛·夸里斯米尼致文图拉·卡拉拉伯爵的信（1696-07-11）（Letter from Carlo Quarismini to Count Ventura Carrara (1696-07-11)）](../units/archives/quarisimini-carrara-letter-1696.md) | 第一章；印刷页 13；OCR L511–513 | 文献身份已由刊本定位 |
| archive | [里奇《施洗者约翰斩首》的委托条款（1682）（Terms for Ricci's Beheading of Saint John the Baptist (1682)）](../units/archives/ricci-bologna-terms-1682.md) | 第一章；印刷页 9；OCR L326–328 | 文献身份通过研究文献定位 |
| archive | [萨尔瓦多·罗萨致安东尼奥·鲁福的信（1666-04-01）（Letter from Salvator Rosa to Antonio Ruffo (1666-04-01)）](../units/archives/rosa-ruffo-letter-1666.md) | 第一章；印刷页 22；OCR L937–947 | 尚无配对 |
| archive | [雅各布·萨尔维亚蒂致莱奥波尔多·德·美第奇的信（1662-07-22）（Letter from Jacopo Salviati to Leopoldo de’ Medici (1662-07-22)）](../units/archives/salviati-medici-letter-1662.md) | 第一章；印刷页 14；OCR L537–540, 565–566 | 尚无配对 |
| archive | [萨维尼在古比奥的委托条款刊录（1608）（Published Terms for Savini's Gubbio Commission (1608)）](../units/archives/savini-gubbio-terms-1608.md) | 第一章；印刷页 9；OCR L321–322 | 尚无配对 |
| archive | [富尔维奥·泰斯蒂致弗朗切斯科·丰塔纳的信（Letter from Fulvio Testi to Francesco Fontana）](../units/archives/testi-fontana-bernini-letter.md) | 第一章印刷页 17；原 OCR 行 699–703 | 尚无配对 |
| archive | [瓦萨利关于莫拉与潘菲利服务争议的证词记录（Vasalli's Testimony on the Mola–Pamfili Service Dispute）](../units/archives/vasalli-testimony-mola-pamfili.md) | 第一章；印刷页 6；OCR L179–185 | 尚无配对 |
| event | [圣路加学院征税及公共委托措施（1633）（Taxation and Public-Commission Measures of the Accademia di S. Luca (1633)）](../units/events/accademia-tax-privilege-1633.md) | 第一章；印刷页 17, 18；OCR L696–698,717–722 | 尚无配对 |
| event | [圭尔奇诺西西里祭坛画图像询问（1665）（Guercino's Questions about a Sicilian Altarpiece (1665)）](../units/events/guercino-iconography-query-1665.md) | 第一章；印刷页 9；OCR L295–307 | 尚无配对 |
| event | [兰弗兰科申请《教皇利奥与阿提拉》委托（1640）（Lanfranco's Request for the Pope Leo and Attila Commission (1640)）](../units/events/lanfranco-leo-attila-request-1640.md) | 第一章；印刷页 11；OCR L408–425 | 尚无配对 |
| event | [萨基在巴贝里尼家户内晋级（1640）（Sacchi's Promotion in the Barberini Household (1640)）](../units/events/sacchi-household-promotion-1640.md) | 第一章；印刷页 7；OCR L195–198 | 尚无配对 |
| event | [画家帮成立（1623）（Formation of the Schildersbent (1623)）](../units/events/schildersbent-formation-1623.md) | 第一章；印刷页 20；OCR L819–833 | 尚无配对 |
| event | [查理五世授提香荣衔（1533）（Charles V's Grant of Honours to Titian (1533)）](../units/events/titian-honours-1533.md) | 第一章；印刷页 19；OCR L799–804 | 尚无配对 |
| institution | [圣路加学院（Accademia di S. Luca）](../units/institutions/accademia-di-san-luca.md) | 第一章；印刷页 17, 18；OCR L678–698,717–722 | 身份配对通过 Q338523 |
| family | [阿尔多布兰迪尼家族（Aldobrandini Family）](../units/families/aldobrandini-family.md) | 第一章；印刷页 5；OCR L111–116 | 身份配对通过 Q961820 |
| institution | [宗座财务院（Apostolic Chamber）](../units/institutions/apostolic-chamber.md) | 第一章；印刷页 17；OCR L685–689 | 身份配对通过 Q620030 |
| institution | [阿尔卡迪亚学会（Society of Arcadia）](../units/institutions/arcadia.md) | 第一章；印刷页 19；OCR L770–773 | 身份配对通过 Q338478 |
| institution | [巴贝里尼家族及家户（Barberini Family and Households）](../units/institutions/barberini-household.md) | 第一章；印刷页 3；OCR L15–47 | 范围待对齐 |
| institution | [巴尔纳伯会（Barnabites）](../units/institutions/barnabites.md) | 第一章；印刷页 5；OCR L125–130 | 身份配对通过 Q620456 |
| institution | [奥古斯塔图书馆（Biblioteca Augusta）](../units/institutions/biblioteca-augusta.md) | 第一章；印刷页 7；OCR L236–237 | 身份配对通过 Q3639560 |
| institution | [卡萨纳滕塞图书馆（Biblioteca Casanatense）](../units/institutions/biblioteca-casanatense.md) | 第一章；印刷页 4；OCR L89–92 | 身份配对通过 Q2901274 |
| family | [博尔盖塞家族（Borghese Family）](../units/families/borghese-family.md) | 第一章；印刷页 5；OCR L111–116 | 身份配对通过 Q241133 |
| institution | [嘉布遣会（Capuchins）](../units/institutions/capuchins.md) | 第一章；印刷页 5；OCR L125–130 | 身份配对通过 Q124862 |
| institution | [科尔纳吉画廊（Colnaghi's）](../units/institutions/colnaghi.md) | 第一章；印刷页 12；OCR L467–468 | 身份配对通过 Q5147759 |
| institution | [博洛尼亚佛罗伦萨人圣若翰善会（Confraternity of Saint John of the Florentines, Bologna）](../units/institutions/confraternita-san-giovanni-battista-decollato-bologna.md) | 第一章；印刷页 9；OCR L326–328 | 尚无机构配对 |
| institution | [圣彼得营造管理机构（Fabbrica di S. Pietro）](../units/institutions/fabbrica-di-san-pietro.md) | 第一章；印刷页 17；OCR L700–703 | 身份配对通过 Q2381511 |
| institution | [耶稣会（Jesuits）](../units/institutions/jesuits.md) | 第一章；印刷页 5；OCR L125–130 | 身份配对通过 Q36380 |
| institution | [奥拉托利会（Oratorians）](../units/institutions/oratorians.md) | 第一章；印刷页 5；OCR L125–130 | 身份配对通过 Q247132 |
| family | [佩雷蒂家族（Peretti Family）](../units/families/peretti-family.md) | 第一章；印刷页 5；OCR L111–116 | 身份配对通过 Q63522275 |
| institution | [梵蒂冈绘画馆（Pinacoteca Vaticana）](../units/institutions/pinacoteca-vaticana.md) | 第一章；印刷页 12；OCR L465–466 | 身份配对通过 Q774940 |
| institution | [画家帮（Schildersbent）](../units/institutions/schildersbent.md) | 第一章；印刷页 20；OCR L819–833 | 身份配对通过 Q514377 |
| institution | [戴蒂尼会（Theatines）](../units/institutions/theatines.md) | 第一章；印刷页 5；OCR L125–130 | 身份配对通过 Q1414924 |
| institution | [维多利亚与阿尔伯特博物馆（Victoria and Albert Museum）](../units/institutions/victoria-and-albert-museum.md) | 第一章；印刷页 17；OCR L699–700 | 身份配对通过 Q213322 |
| person | [塞孔多·兰切洛蒂（Secondo Lancellotti）](../units/persons/abate-lancellotti.md) | 第一章；印刷页 3；OCR L45–47 | 身份配对通过 Q15733678 |
| person | [亚历山德罗·佩雷蒂—蒙塔尔托（Alessandro Peretti-Montalto）](../units/persons/alessandro-peretti-montalto.md) | 第一章；印刷页 4；OCR L68–70 | 身份配对通过 Q82659 |
| person | [亚历山德罗·瓦萨利（Alessandro Vasalli）](../units/persons/alessandro-vasalli.md) | 第一章；印刷页 6；OCR L179–185 | 尚无配对 |
| person | [迪尔克·范·阿梅登（Dirk van Ameyden）](../units/persons/ameyden.md) | 第一章；印刷页 4；OCR L89–92 | 身份配对通过 Q3983865 |
| person | [安德烈亚·卡马塞伊（Andrea Camassei）](../units/persons/andrea-camassei.md) | 第一章；印刷页 10；OCR L336–338,372–374 | 身份配对通过 Q3615565 |
| person | [安德烈亚·波佐（Andrea Pozzo）](../units/persons/andrea-pozzo.md) | 第一章；印刷页 20；OCR L840–843 | 身份配对通过 Q380103 |
| person | [安德烈亚·普罗卡奇尼（Andrea Procaccini）](../units/persons/andrea-procaccini.md) | 第一章；印刷页 18；OCR L745–747 | 身份配对通过 Q2846401 |
| person | [安德烈亚·萨基（Andrea Sacchi）](../units/persons/andrea-sacchi.md) | 第一章；印刷页 7；OCR L195–198 | 身份配对通过 Q495008 |
| person | [安尼巴莱·卡拉奇（Annibale Carracci）](../units/persons/annibale-carracci.md) | 第一章；印刷页 4, 5；OCR L84–88,101–110 | 身份配对通过 Q7824 |
| person | [安尼巴莱·拉帕雷利（Annibale Laparelli）](../units/persons/annibale-laparelli.md) | 第一章；印刷页 13；OCR L507–508 | 尚无配对 |
| person | [安东尼奥·巴贝里尼（Antonio Barberini）](../units/persons/antonio-barberini.md) | 第一章；印刷页 7；OCR L195–198 | 身份配对通过 Q599744 |
| person | [安东尼奥·鲁福（Don Antonio Ruffo）](../units/persons/antonio-ruffo.md) | 第一章；印刷页 14；OCR L569–570 | 身份配对通过 Q88949215 |
| person | [阿尔泰米西娅·真蒂莱斯基（Artemisia Gentileschi）](../units/persons/artemisia-gentileschi.md) | 第一章；印刷页 13；OCR L523 | 身份配对通过 Q212657 |
| person | [贝内代托·卢蒂（Benedetto Luti）](../units/persons/benedetto-luti.md) | 第一章；印刷页 8；OCR L278 | 身份配对通过 Q816847 |
| person | [本韦努托·切利尼（Benvenuto Cellini）](../units/persons/benvenuto-cellini.md) | 第一章；印刷页 16；OCR L634–635 | 身份配对通过 Q190116 |
| person | [贝尔林杰罗·杰西（Berlingero Gessi）](../units/persons/berlingete-gessi.md) | 第一章；印刷页 13；OCR L509–510 | 已排除误配 |
| person | [博尼法齐奥·戈扎迪尼（Bonifazio Gozadini）](../units/persons/bonifazio-gozadini.md) | 第一章；印刷页 13；OCR L515–516 | 尚无配对 |
| person | [卡米洛·加瓦塞蒂（Camillo Gavasetti）](../units/persons/camillo-gavasetti.md) | 第一章；印刷页 9；OCR L323–326 | 身份配对通过 Q16853519 |
| person | [卡米洛·弗朗切斯科·玛丽亚·潘菲利（Camillo Francesco Maria Pamphili）](../units/persons/camillo-pamfili.md) | 第一章；印刷页 6；OCR L179–185 | 身份配对通过 Q2935138 |
| person | [卡拉瓦乔（Caravaggio）](../units/persons/caravaggio.md) | 第一章；印刷页 10；OCR L349–353 | 身份配对通过 Q42207 |
| person | [希皮奥内·博尔盖塞枢机（Cardinal Scipione Borghese）](../units/persons/cardinal-borghese-ch1.md) | 第一章；印刷页 4；OCR L79–83 | 身份配对通过 Q452570 |
| person | [卡洛·皮奥·迪·萨伏依（Carlo Pio di Savoia）](../units/persons/cardinal-pio-bonati.md) | 第一章；印刷页 6；OCR L186–187 | 身份配对通过 Q2939240 |
| person | [朱利奥·罗斯皮廖西（Giulio Rospigliosi）](../units/persons/cardinal-rospigliosi-gimignani.md) | 第一章；印刷页 6；OCR L186–187 | 身份配对通过 Q155961 |
| person | [卡洛·切萨雷·马尔瓦西亚（Carlo Cesare Malvasia）](../units/persons/carlo-cesare-malvasia.md) | 第一章；印刷页 16；OCR L630–638,657–658 | 身份配对通过 Q1160847 |
| person | [卡洛·马拉塔（Carlo Maratta）](../units/persons/carlo-maratta.md) | 第一章；印刷页 17；OCR L670–677,704–710 | 身份配对通过 Q538998 |
| person | [卡洛·夸里斯米尼（1696年通信者）（Carlo Quarismini, correspondent in 1696）](../units/persons/carlo-quarisimini-ch1.md) | 第一章；印刷页 13；OCR L511–513 | 尚无配对 |
| person | [卡洛·里多尔菲（Carlo Ridolfi）](../units/persons/carlo-ridolfi.md) | 第一章；印刷页 19；OCR L763–767 | 身份配对通过 Q776990 |
| person | [切萨雷·莱奥帕尔迪·多西莫（Don Cesare Leopardi d’Osimo）](../units/persons/cesare-leopardi-dosimo.md) | 第一章；印刷页 13；OCR L509–510 | 尚无配对 |
| person | [查理五世（Charles V）](../units/persons/charles-v.md) | 第一章；印刷页 19；OCR L764–767, 799–804 | 身份配对通过 Q32500 |
| person | [瑞典女王克里斯蒂娜（Christina of Sweden）](../units/persons/christina-of-sweden.md) | 第一章；印刷页 19；OCR L767–770 | 身份配对通过 Q52937 |
| person | [奇罗·费里（Ciro Ferri）](../units/persons/ciro-ferri.md) | 第一章；印刷页 12；OCR L437–453 | 身份配对通过 Q975452 |
| person | [克劳德·洛兰（Claude Lorrain）](../units/persons/claude-lorrain.md) | 第一章；印刷页 8；OCR L265–273,283 | 身份配对通过 Q214074 |
| person | [克雷芒十一世（Clement XI）](../units/persons/clement-xi.md) | 第一章；印刷页 19；OCR L771–773 | 身份配对通过 Q129967 |
| person | [科雷乔（Correggio）](../units/persons/correggio.md) | 第一章；印刷页 6；OCR L169–171 | 身份配对通过 Q8457 |
| person | [丹尼斯·马洪（Denis Mahon）](../units/persons/denis-mahon.md) | 第一章；印刷页 12；OCR L467–468 | 身份配对通过 Q3705445 |
| person | [多梅尼科·赞皮耶里（Domenico Zampieri）](../units/persons/domenichino.md) | 第一章印刷页 4, 13；OCR 行 79–83, 498–502 | 身份配对通过 Q320118 |
| person | [布拉恰诺公爵（穆利耶尔的雇主）（Duke of Bracciano (Mulier’s patron)）](../units/persons/duke-bracciano-mulier.md) | 第一章；印刷页 7；OCR L231–233 | 尚无配对 |
| person | [费迪南多·贡扎加（Ferdinando Gonzaga）](../units/persons/duke-mantua-reni-1617.md) | 第一章；印刷页 14；OCR L531–534 | 身份配对通过 Q969739 |
| person | [帕尔马公爵（盖齐授衔语境）（Duke of Parma (Ghezzi’s honorary appointment)）](../units/persons/duke-parma-ghezzi.md) | 第一章；印刷页 19；OCR L770–773 | 尚无配对 |
| person | [法布里齐奥·阿拉戈纳（Fabrizio Arragona）](../units/persons/fabrizio-arragona.md) | 第一章；印刷页 14；OCR L567–568 | 尚无配对 |
| person | [法布里齐奥·瓦尔瓜尔内拉（Fabrizio Valguarnera）](../units/persons/fabrizio-valguarnera.md) | 第一章；印刷页 15；OCR L591–603 | 尚无配对 |
| person | [费德里科·祖卡里（Federico Zuccari）](../units/persons/federigo-zuccari.md) | 第一章；印刷页 17；OCR L681–683 | 身份配对通过 Q345605 |
| person | [菲利波·巴尔迪努奇（Filippo Baldinucci）](../units/persons/filippo-baldinucci.md) | 第一章；印刷页 15；OCR L614 | 身份配对通过 Q979574 |
| person | [菲利波·劳里（Filippo Lauri）](../units/persons/filippo-lauri.md) | 第一章；印刷页 19；OCR L778–781 | 身份配对通过 Q3071902 |
| person | [弗拉维奥·基吉（Flavio Chigi）](../units/persons/flavio-chigi.md) | 第一章；印刷页 8；OCR L282 | 身份配对通过 Q1397340 |
| person | [弗朗切斯科·阿尔巴尼（Francesco Albani）](../units/persons/francesco-albani.md) | 第一章；印刷页 13；OCR L503–505, 515–516 | 身份配对通过 Q358147 |
| person | [弗朗切斯科·巴贝里尼（Francesco Barberini）](../units/persons/francesco-barberini.md) | 第一章；印刷页 17；OCR L691–696 | 身份配对通过 Q534683 |
| person | [弗朗切斯科·丰塔纳（Francesco Fontana）](../units/persons/francesco-fontana.md) | 第一章印刷页 17；OCR 行 700–703 | 已排除误配 |
| person | [弗朗切斯科·诺韦蒂（Francesco Novetti）](../units/persons/francesco-novetti.md) | 第一章；印刷页 18；OCR L757–758 | 尚无配对 |
| person | [弗朗切斯科·特雷维萨尼（Francesco Trevisani）](../units/persons/francesco-trevisani.md) | 第一章；印刷页 7；OCR L220–221,235–237 | 身份配对通过 Q963875 |
| person | [皇帝腓特烈三世（Frederick III）](../units/persons/frederick-iii.md) | 第一章；印刷页 19；OCR L799–800 | 身份配对通过 Q150966 |
| person | [富尔维奥·泰斯蒂（Fulvio Testi）](../units/persons/fulvio-testi.md) | 第一章印刷页 17；OCR 行 700–703 | 身份配对通过 Q594614 |
| person | [加斯帕尔·迪盖（Gaspard Dughet）](../units/persons/gaspard-dughet.md) | 第一章；印刷页 12；OCR L457–459 | 身份配对通过 Q741375 |
| person | [真蒂莱·贝利尼（Gentile Bellini）](../units/persons/gentile-bellini.md) | 第一章；印刷页 19；OCR L799–800 | 身份配对通过 Q290407 |
| person | [贾钦托·布兰迪（Giacinto Brandi）](../units/persons/giacinto-brandi.md) | 第一章；印刷页 12；OCR L456–457 | 身份配对通过 Q1748199 |
| person | [乔万尼·巴蒂斯塔·帕塞里（Giovanni Battista Passeri）](../units/persons/giambattista-passeri.md) | 第一章；印刷页 3；OCR L15–18 | 身份配对通过 Q962495 |
| person | [乔万尼·玛丽亚·莫兰迪（Giovanni Maria Morandi）](../units/persons/giammaria-morandi.md) | 第一章；印刷页 18；OCR L744–745 | 身份配对通过 Q1773095 |
| person | [吉安·洛伦佐·贝尔尼尼（Gian Lorenzo Bernini）](../units/persons/gian-lorenzo-bernini.md) | 第一章；印刷页 16, 17；OCR L641–646,656,668–672 | 身份配对通过 Q160538 |
| person | [乔万尼·安德烈亚·卡尔洛内（Giovanni Andrea Carlone）](../units/persons/gianandrea-carlone.md) | 第一章；印刷页 21；OCR L858–861 | 身份配对通过 Q3106993 |
| person | [乔瓦尼·加斯帕雷·巴尔多伊诺（Giovanni Gaspare Baldoino）](../units/persons/gio-gasparo-baldoini.md) | 第一章；印刷页 6；OCR L188–189 | 尚无配对 |
| person | [瓦萨里（Vasari）](../units/persons/giorgio-vasari.md) | 第一章；印刷页 21；OCR L882–884 | 身份配对通过 Q128027 |
| person | [乔万尼·巴蒂斯塔·盖乌利（Giovanni Battista Gaulli）](../units/persons/giovan-battista-gaulli.md) | 第一章；印刷页 12；OCR L430–460 | 身份配对通过 Q520573 |
| person | [列支敦士登亲王约翰·亚当·安德烈亚斯一世（Johann Adam Andreas I, Prince of Liechtenstein）](../units/persons/giovanni-adamo-piola.md) | 第一章；印刷页 10；OCR L354–356, 376 | 身份配对通过 Q581481 |
| person | [乔瓦尼·博纳蒂（Giovanni Bonatti）](../units/persons/giovanni-bonati.md) | 第一章；印刷页 6；OCR L186–187 | 身份配对通过 Q5565359 |
| person | [乔万尼·兰弗兰科（Giovanni Lanfranco）](../units/persons/giovanni-lanfranco.md) | 第一章印刷页 7, 11, 13, 15；OCR 行 210–213, 408–425, 500–502, 596–601 | 身份配对通过 Q447730 |
| person | [乔万尼·奥达齐（Giovanni Odazzi）](../units/persons/giovanni-odazzi.md) | 第一章；印刷页 12；OCR L455–457 | 身份配对通过 Q464446 |
| person | [乔万尼·佩鲁吉尼（Giovanni Perugini）](../units/persons/giovanni-perugini.md) | 第一章；印刷页 21；OCR L889–893 | 已排除误配 |
| person | [乔万尼·彼得罗·贝洛里（Giovanni Pietro Bellori）](../units/persons/giovanni-pietro-bellori.md) | 第一章；印刷页 10；OCR L369–371 | 身份配对通过 Q714400 |
| person | [朱利奥·曼奇尼（Giulio Mancini）](../units/persons/giulio-mancini.md) | 第一章；印刷页 14；OCR L529–531 | 身份配对通过 Q3769699 |
| person | [朱塞佩·德·罗西斯（Giuseppe de Rosis）](../units/persons/giuseppe-de-rosis.md) | 第一章；印刷页 23；OCR L971–972 | 尚无配对 |
| person | [朱塞佩·盖齐（Giuseppe Ghezzi）](../units/persons/giuseppe-ghezzi.md) | 第一章；印刷页 19；OCR L770–773 | 身份配对通过 Q1749764 |
| person | [乔万尼·卢多维科·比安科尼（Giovanni Ludovico Bianconi）](../units/persons/gl-bianconi.md) | 第一章；印刷页 21；OCR L896–898 | 身份配对通过 Q5563896 |
| person | [格列高利十五世（Gregory XV）](../units/persons/gregory-xv.md) | 第一章；印刷页 3；OCR L26–27 | 身份配对通过 Q132692 |
| person | [乔万尼·弗朗切斯科·巴尔比耶里（Giovanni Francesco Barbieri）](../units/persons/guercino.md) | 第1章，印刷页 9, 14；OCR 行 295–307, 548–552, 569–570 | 身份配对通过 Q334262 |
| person | [古列尔莫·科尔泰塞（Guglielmo Cortese）](../units/persons/guglielmo-cortese.md) | 第一章；印刷页 7；OCR L231–233 | 身份配对通过 Q1749032 |
| person | [圭多·雷尼（Guido Reni）](../units/persons/guido-reni.md) | 第一章；印刷页 10；OCR L373–374 | 身份配对通过 Q109061 |
| person | [英诺森十世（Innocent X）](../units/persons/innocent-x.md) | 第一章；印刷页 19；OCR L764–767 | 身份配对通过 Q101266 |
| person | [英诺森十三世（Innocent XIII）](../units/persons/innocent-xiii.md) | 第一章；印刷页 19；OCR L771–773 | 身份配对通过 Q133100 |
| person | [雅各布·萨尔维亚蒂（Jacopo Salviati）](../units/persons/jacopo-salviati.md) | 第一章；印刷页 14；OCR L565–566 | 已排除误配 |
| person | [利奥十世（Leo X）](../units/persons/leo-x.md) | 第一章；印刷页 16；OCR L650–654 | 身份配对通过 Q49237 |
| person | [莱奥波尔多·德·美第奇（Leopoldo de’ Medici）](../units/persons/leopoldo-de-medici.md) | 第一章；印刷页 14；OCR L538–540, 565–566 | 身份配对通过 Q968920 |
| person | [洛多维科·吉米尼亚尼（Lodovico Gimignani）](../units/persons/lodovico-gimignani.md) | 第一章；印刷页 6；OCR L186–187 | 身份配对通过 Q3839112 |
| person | [托马斯·霍华德，阿伦德尔伯爵（Thomas Howard, Earl of Arundel）](../units/persons/lord-arundell-coke-correspondent.md) | 第一章；印刷页 3, 4；OCR L40–44,48,53–55 | 配对通过：Q166517（REV-052） |
| person | [卢卡·焦尔达诺（Luca Giordano）](../units/persons/luca-giordano.md) | 第一章；印刷页 12；OCR L455–457 | 身份配对通过 Q332494 |
| person | [卢多维科·卢多维西（Ludovico Ludovisi）](../units/persons/ludovico-ludovisi.md) | 第一章；印刷页 4；OCR L79–83 | 身份配对通过 Q707750 |
| person | [马尔切洛·萨凯蒂（Marcello Sacchetti）](../units/persons/marcello-sacchetti.md) | 第一章；印刷页 7；OCR L217–220 | 身份配对通过 Q6087600 |
| person | [科斯塔古蒂侯爵（卡尔洛内婚姻事例语境）（Marchese Costaguti (Carlone marriage context)）](../units/persons/marchese-costaguti-household.md) | 第一章；印刷页 21；OCR L858–861 | 尚无配对 |
| person | [加斯帕尔·门德斯·德阿罗，第七代卡尔皮奥侯爵（Gaspar Méndez de Haro, 7th Marquess of Carpio）](../units/persons/marchese-del-carpio.md) | 第一章；印刷页 10；OCR L369–371 | 身份配对通过 Q380763 |
| person | [文琴佐·朱斯蒂尼亚尼（Vincenzo Giustiniani）](../units/persons/marchese-giustiniani-ch1.md) | 第一章；印刷页 10；OCR L349–353 | 身份配对通过 Q1396468 |
| person | [尼科洛·马里亚·帕拉维奇尼侯爵（Niccolò Maria Pallavicini）](../units/persons/marchese-pallavicini-piola.md) | 第一章；印刷页 8；OCR L278–281 | 身份配对通过 Q105105120 |
| person | [圣托马索侯爵（内格里的收信人）（Marchese di S. Tommaso (Negri’s correspondent)）](../units/persons/marchese-san-tommaso-negri.md) | 第一章；印刷页 21；OCR L899–900 | 尚无配对 |
| person | [马里奥·努齐（Mario Nuzzi）](../units/persons/mario-de-fiori.md) | 第一章；印刷页 8；OCR L282 | 身份配对通过 Q1227379 |
| person | [马里奥·明尼蒂（Mario Minniti）](../units/persons/mario-minnitti.md) | 第一章；印刷页 9；OCR L322 | 身份配对通过 Q153619 |
| person | [马蒂亚·普雷蒂（Mattia Preti）](../units/persons/mattia-preti.md) | 第一章；印刷页 13；OCR L523 | 身份配对通过 Q468632 |
| person | [毛里齐奥·迪·萨伏依（Maurizio di Savoia）](../units/persons/maurizio-di-savoia.md) | 第一章；印刷页 6；OCR L188–189 | 身份配对通过 Q610738 |
| person | [米开朗基罗·切尔阔齐（Michelangelo Cerquozzi）](../units/persons/michelangelo-cerquozzi.md) | 第一章；印刷页 18；OCR L753–754 | 身份配对通过 Q979862 |
| person | [米开朗基罗（Michelangelo）](../units/persons/michelangelo.md) | 第一章；印刷页 16；OCR L623, 641–646 | 身份配对通过 Q5592 |
| person | [托马斯·科克（Thomas Coke，阿伦德尔家户通信者）](../units/persons/mr-coke-rome-correspondent.md) | 第一章；印刷页 3, 4；OCR L40–44,48,53–55 | 尚无配对 |
| person | [尼古拉·普桑（Nicolas Poussin）](../units/persons/nicolas-poussin.md) | 第一章；印刷页 10；OCR L373–374 | 身份配对通过 Q41554 |
| person | [奥诺拉托·吉尼（Onorato Gini）](../units/persons/onorato-gini.md) | 第一章；印刷页 11；OCR L415–418 | 尚无配对 |
| person | [保罗·杰罗拉莫·皮奥拉（Paolo Gerolamo Piola）](../units/persons/paolo-girolamo-piola.md) | 第一章；印刷页 8；OCR L278–281 | 身份配对通过 Q3894101 |
| person | [保罗·圭多蒂（Paolo Guidotti）](../units/persons/paolo-guidotti.md) | 第一章；印刷页 14；OCR L535–537 | 身份配对通过 Q3894144 |
| person | [保罗·内格里（Paolo Negri）](../units/persons/paolo-negri.md) | 第一章；印刷页 21；OCR L899–900 | 已排除误配 |
| person | [利奥内·帕斯科利（Lione Pascoli）](../units/persons/pascoli.md) | 第一章；印刷页 6；OCR L178–187 | 身份配对通过 Q1101774 |
| person | [保禄五世（Paul V）](../units/persons/paul-v.md) | 第一章；印刷页 3；OCR L26–27 | 身份配对通过 Q132711 |
| person | [鲁本斯（Rubens）](../units/persons/peter-paul-rubens.md) | 第一章；印刷页 11；OCR L402–404 | 身份配对通过 Q5599 |
| person | [皮耶尔·弗朗切斯科·莫拉（Pier Francesco Mola）](../units/persons/pier-francesco-mola.md) | 第一章；印刷页 6；OCR L179–185 | 身份配对通过 Q1192715 |
| person | [彼得·范拉尔（Pieter van Laer）](../units/persons/pieter-van-laer.md) | 第一章；印刷页 18；OCR L753–754 | 身份配对通过 Q576907 |
| person | [皮耶特罗·达·科尔托纳（Pietro da Cortona）](../units/persons/pietro-da-cortona.md) | 第一章；印刷页 7；OCR L217–220 | 身份配对通过 Q333323 |
| person | [皮耶特罗·穆利耶尔（Pietro Mulier）](../units/persons/pietro-mulier.md) | 第一章；印刷页 7；OCR L231–233 | 身份配对通过 Q666337 |
| person | [彼得罗·奥托博尼（Pietro Ottoboni）](../units/persons/pietro-ottoboni.md) | 第一章；印刷页 7；OCR L220–221,235–237 | 身份配对通过 Q725737 |
| person | [拉斐尔（Raphael）](../units/persons/raphael.md) | 第一章；印刷页 16；OCR L623 | 身份配对通过 Q5597 |
| person | [伦勃朗（Rembrandt）](../units/persons/rembrandt.md) | 第一章；印刷页 17；OCR L674–677 | 身份配对通过 Q5598 |
| person | [萨尔瓦多·罗萨（Salvator Rosa）](../units/persons/salvator-rosa.md) | 第一章；印刷页 11；OCR L382–389 | 身份配对通过 Q359421 |
| person | [萨尔维奥·萨维尼（Salvio Savini）](../units/persons/saverio-savini.md) | 第一章；印刷页 9；OCR L321–322 | 尚无配对 |
| person | [塞巴斯蒂亚诺·里奇（Sebastiano Ricci）](../units/persons/sebastiano-ricci.md) | 第一章；印刷页 9；OCR L326–328 | 身份配对通过 Q506483 |
| person | [西斯笃五世（Sixtus V）](../units/persons/sixtus-v.md) | 第一章；印刷页 4；OCR L68–69 | 身份配对通过 Q133350 |
| person | [托马斯·贝克（Thomas Baker）](../units/persons/thomas-baker.md) | 第一章；印刷页 17；OCR L699–700 | 候选待证 |
| person | [提香（Titian）](../units/persons/titian.md) | 第一章；印刷页 19；OCR L764–767, 800–804 | 身份配对通过 Q47551 |
| person | [乌尔班八世（Urban VIII）](../units/persons/urbano-viii.md) | 第一章；印刷页 3；OCR L15–34 | 身份配对通过 Q131579 |
| person | [瓦朗坦·德·布洛涅（Valentin de Boulogne）](../units/persons/valentin.md) | 第一章；印刷页 11；OCR L389–392 | 身份配对通过 Q1337275 |
| person | [文图拉·卡拉拉伯爵（Count Ventura Carrara）](../units/persons/ventura-carrara.md) | 第一章；印刷页 13；OCR L511–513 | 尚无配对 |
| person | [温琴佐·阿尔曼尼（Vincenzo Armanni）](../units/persons/vincenzo-armanni-ch1.md) | 第一章；印刷页 9；OCR L329–330 | 候选待证 |
| person | [维吉尔（Virgil）](../units/persons/virgil.md) | 第一章；印刷页 9；OCR L314–319 | 身份配对通过 Q1398 |
| place | [奥古斯塔（西西里）（Augusta, Sicily）](../units/places/augusta-sicily.md) | 第一章；印刷页 9；OCR L322 | 身份配对通过 Q194005 |
| place | [博洛尼亚（Bologna）](../units/places/bologna.md) | 第一章；印刷页 4, 5；OCR L79–88,101–110 | 身份配对通过 Q1891 |
| place | [罗马嘉布遣会教堂（Capuchin Church in Rome）](../units/places/capuchin-church-rome.md) | 第一章；印刷页 12；OCR L467–468 | 身份配对通过 Q546141 |
| place | [博洛尼亚塞尔维教堂（Chiesa de' Servi, Bologna）](../units/places/chiesa-de-servi-bologna.md) | 第一章；印刷页 13；OCR L515–516 | 身份配对通过 Q1021897 |
| place | [罗马新教堂（Chiesa Nuova, Rome）](../units/places/chiesa-nuova.md) | 第一章；印刷页 11；OCR L402–404 | 身份配对通过 Q2031901 |
| place | [科尔托纳（Cortona）](../units/places/cortona.md) | 第一章；印刷页 7；OCR L217–220 | 身份配对通过 Q52080 |
| place | [佛罗伦萨（Florence）](../units/places/florence.md) | 第一章；印刷页 4；OCR L71–83 | 身份配对通过 Q2044 |
| place | [热那亚（Genoa）](../units/places/genoa.md) | 第一章；印刷页 8；OCR L278–281 | 身份配对通过 Q1449 |
| place | [罗马耶稣堂（Gesù, Rome）](../units/places/gesu-rome.md) | 第一章；印刷页 12；OCR L452–454 | 身份配对通过 Q719794 |
| place | [古比奥（Gubbio）](../units/places/gubbio.md) | 第一章；印刷页 9；OCR L321–322 | 身份配对通过 Q20458 |
| place | [意大利（Italy）](../units/places/italy.md) | 第一章；印刷页 4；OCR L58–59,71–83 | 范围待对齐 |
| place | [伦敦（London）](../units/places/london.md) | 第一章；印刷页 12；OCR L467–468 | 身份配对通过 Q84 |
| place | [米兰（Milan）](../units/places/milan.md) | 第一章；印刷页 6；OCR L186–187 | 身份配对通过 Q490 |
| place | [摩德纳（Modena）](../units/places/modena.md) | 第一章；印刷页 6；OCR L186–187 | 身份配对通过 Q279 |
| place | [那不勒斯主教座堂（Naples Cathedral）](../units/places/naples-cathedral.md) | 第一章；印刷页 13；OCR L500–502 | 身份配对通过 Q256486 |
| place | [那不勒斯（Naples）](../units/places/naples.md) | 第一章印刷页 11, 13；OCR 行 423–425, 500–502 | 身份配对通过 Q2634 |
| place | [巴贝里尼宫（Palazzo Barberini）](../units/places/palazzo-barberini.md) | 第一章；印刷页 12；OCR L461–468 | 身份配对通过 Q1136614 |
| place | [多利亚潘菲利宫（Palazzo Doria-Pamfili）](../units/places/palazzo-doria-pamfili.md) | 第一章；印刷页 12；OCR L461–463 | 身份配对通过 Q385387 |
| place | [瓦尔蒙托内多利亚·潘菲利宫（Palazzo Doria-Pamphilj, Valmontone）](../units/places/pamfili-country-house-valmontone.md) | 第一章；印刷页 9；OCR L312–319 | 身份配对通过 Q16586138 |
| place | [帕尔马（Parma）](../units/places/parma.md) | 第一章；印刷页 6；OCR L169–171, 186–187 | 身份配对通过 Q2683 |
| place | [佩鲁贾（Perugia）](../units/places/perugia.md) | 第一章；印刷页 7；OCR L236–237 | 身份配对通过 Q3437 |
| place | [皮亚琴察（Piacenza）](../units/places/piacenza.md) | 第一章；印刷页 9；OCR L323–326 | 身份配对通过 Q13329 |
| place | [西班牙广场（Piazza di Spagna）](../units/places/piazza-di-spagna.md) | 第一章；印刷页 20；OCR L827–829 | 身份配对通过 Q15124814 |
| place | [纳沃纳广场（Piazza Navona）](../units/places/piazza-navona.md) | 第一章；印刷页 12；OCR L438–453 | 身份配对通过 Q463400 |
| place | [罗马（Rome）](../units/places/rome.md) | 第一章；印刷页 3, 4；OCR L15–34,56–83 | 身份配对通过 Q220 |
| place | [帕拉蒂尼山圣塞巴斯蒂安堂（S. Sebastiano on the Palatine）](../units/places/san-sebastiano-palatine.md) | 第一章；印刷页 10；OCR L336–338 | 身份配对通过 Q787605 |
| place | [纳沃纳广场圣阿涅塞堂（S. Agnese in Piazza Navona）](../units/places/sant-agnese-piazza-navona.md) | 第一章；印刷页 12；OCR L438–453 | 身份配对通过 Q1192577 |
| place | [谷地圣安德烈堂（S. Andrea della Valle）](../units/places/sant-andrea-della-valle.md) | 第一章；印刷页 5, 6；OCR L139–141,147–152 | 身份配对通过 Q1631593 |
| place | [皮亚琴察圣安托尼诺堂（S. Antonino, Piacenza）](../units/places/sant-antonino-piacenza.md) | 第一章；印刷页 9；OCR L323–326 | 身份配对通过 Q1670729 |
| place | [圣母大殿（Santa Maria Maggiore）](../units/places/santa-maria-maggiore.md) | 第一章；印刷页 5；OCR L120–124 | 身份配对通过 Q186282 |
| place | [米涅瓦圣母堂（Santa Maria sopra Minerva）](../units/places/santa-maria-sopra-minerva.md) | 第一章；印刷页 5；OCR L120–124 | 身份配对通过 Q823685 |
| place | [西西里（Sicily）](../units/places/sicily.md) | 第一章；印刷页 9；OCR L295–307,322 | 范围待对齐 |
| place | [西班牙（Spain）](../units/places/spain.md) | 第一章；印刷页 18；OCR L745–747 | 范围待对齐 |
| place | [圣彼得大殿（St Peter's Basilica）](../units/places/st-peters-basilica.md) | 第一章；印刷页 3, 5；OCR L28,115–116 | 身份配对通过 Q12512 |
| place | [都灵（Turin）](../units/places/turin.md) | 第一章；印刷页 21；OCR L890–893 | 身份配对通过 Q495 |
| place | [瓦尔蒙托内（Valmontone）](../units/places/valmontone.md) | 第一章；印刷页 7；OCR L231–233 | 身份配对通过 Q243514 |
| place | [威尼斯（Venice）](../units/places/venice.md) | 第一章；印刷页 3；OCR L46–47 | 身份配对通过 Q641 |
| place | [玛古塔街（Via Margutta）](../units/places/via-margutta.md) | 第一章；印刷页 20；OCR L827–829 | 身份配对通过 Q1060690 |
| procedure | [艺术家荣衔与职位授予（Conferral of titles and offices on artists）](../units/procedures/artist-title-conferral.md) | 第一章；印刷页 19；OCR L770–777, 799–804 | 尚无配对 |
| procedure | [委托合同订立惯例（Commission contracting）](../units/procedures/commission-contracting.md) | 第一章；印刷页 8, 9；OCR L252–277,288–307 | 尚无配对 |
| procedure | [定金、进度款与结算（Advances, instalments and final payment）](../units/procedures/commission-payment.md) | 第一章；印刷页 13；OCR L478–523 | 尚无配对 |
| procedure | [展览售画与自我宣传（Exhibiting paintings and self-promotion）](../units/procedures/exhibition-self-promotion.md) | 第一章；印刷页 6；OCR L154–164 | 尚无配对 |
| procedure | [题材与图像志协商（Consultation over subjects and iconography）](../units/procedures/iconographic-consultation.md) | 第一章；印刷页 8, 9；OCR L274–277,288–330 | 尚无配对 |
| procedure | [预备稿提交与批准（Submission and approval of preliminary designs）](../units/procedures/modello-approval.md) | 第一章；印刷页 11, 12；OCR L393–414,430–446 | 尚无配对 |
| procedure | [赞助人资助学习旅行（Patron-funded study travel）](../units/procedures/patron-funded-study-travel.md) | 第一章；印刷页 6；OCR L165–189 | 尚无配对 |
| procedure | [保护与职业引介程序（Patronage and professional introduction）](../units/procedures/patronage-introduction.md) | 第一章；印刷页 4, 5；OCR L84–88,101–110 | 尚无配对 |
| procedure | [按主要人物数量计价（Pricing by principal figures）](../units/procedures/per-figure-pricing.md) | 第一章；印刷页 9, 10；OCR L320–321,335–338 | 尚无配对 |
| procedure | [工作室存画议价与完成（Negotiating and completing studio stock）](../units/procedures/studio-stock-sale.md) | 第一章；印刷页 15；OCR L591–606 | 尚无配对 |
| term | [祭坛画（Altarpiece）](../units/terms/altarpiece.md) | 第一章；印刷页 5；OCR L101–110 | 身份配对通过 Q15711026 |
| term | [画商（Art dealer）](../units/terms/art-dealer.md) | 第一章；印刷页 6；OCR L160–164 | 身份配对通过 Q173950 |
| term | [创作独立（Artistic independence）](../units/terms/artistic-independence.md) | 第一章；印刷页 22, 23；OCR L927–943,952–970 | 尚无配对 |
| term | [艺术家气质（Artistic temperament）](../units/terms/artistic-temperament.md) | 第一章；印刷页 21, 22；OCR L882–893,905–926 | 尚无配对 |
| term | [同巢之鸟（Bentveughels）](../units/terms/bentveughels.md) | 第一章；印刷页 20；OCR L819–833 | 范围待对齐 |
| term | [艺术家“波希米亚”群体（Bohemian artists）](../units/terms/bohemian-artists.md) | 第一章；印刷页 16；OCR L624–627 | 范围待对齐 |
| term | [构思草稿（Bozzetto）](../units/terms/bozzetto.md) | 第一章；印刷页 12；OCR L461–468 | 身份配对通过（REV-052，Q5416402） |
| term | [定金（Caparra）](../units/terms/caparra.md) | 第一章；印刷页 13；OCR L478–485,503–508 | 范围待对齐 |
| term | [基督骑士荣衔（Cavaliere dell’abito di Cristo）](../units/terms/cavaliere-abito-cristo.md) | 第一章；印刷页 19；OCR L774–777 | 尚无配对 |
| term | [行宫伯爵（Count Palatine）](../units/terms/count-palatine.md) | 第一章；印刷页 19；OCR L799–804 | 身份配对通过 Q22932 |
| term | [祈祷用图像（Devotional picture）](../units/terms/devotional-picture.md) | 第一章；印刷页 20；OCR L811–818 | 尚无配对 |
| term | [鉴赏爱好者（Dilettante）](../units/terms/dilettante.md) | 第一章；印刷页 6；OCR L160–164 | 候选待证 |
| term | [家户（Famiglia）](../units/terms/famiglia.md) | 第一章；印刷页 6, 7；OCR L171–177,195–198 | 范围待对齐 |
| term | [湿壁画技法（Fresco）](../units/terms/fresco.md) | 第一章；印刷页 8；OCR L258–264 | 身份配对通过 Q134194 |
| term | [可移动画廊画（Gallery picture）](../units/terms/gallery-picture.md) | 第一章；印刷页 8；OCR L265–273 | 尚无配对 |
| term | [天才观（Genius）](../units/terms/genius.md) | 第一章；印刷页 16；OCR L650–654 | 范围待对齐 |
| term | [荣誉侍从（Gentiluomo d’onore）](../units/terms/gentiluomo-onore.md) | 第一章；印刷页 19；OCR L770–773 | 范围待对齐 |
| term | [历史画（History painting）](../units/terms/history-painting.md) | 第一章；印刷页 15；OCR L603–606 | 身份配对通过 Q742333 |
| term | [圣年（Holy Year）](../units/terms/holy-year.md) | 第一章；印刷页 12；OCR L453–455 | 身份配对通过 Q838794 |
| term | [灵感与热情（Inspiration / entusiasmo）](../units/terms/inspiration.md) | 第一章；印刷页 22；OCR L937–947 | 尚无配对 |
| term | [预备稿／模型（Modello）](../units/terms/modello.md) | 第一章；印刷页 11, 12；OCR L393–414,430–446 | 身份配对通过 Q3859830 |
| term | [教皇亲族任用（Nepotism）](../units/terms/nepotism.md) | 第一章；印刷页 4；OCR L56–70 | 身份配对通过 Q161165 |
| term | [新闻纸（News sheets）](../units/terms/news-sheets.md) | 第一章；印刷页 19；OCR L778–783 | 尚无配对 |
| term | [本府画家（Nostro pittore）](../units/terms/nostro-pittore.md) | 第一章；印刷页 6；OCR L173–189 | 范围待对齐 |
| term | [成对绘画（Pendant pictures）](../units/terms/pendant-pictures.md) | 第一章；印刷页 8；OCR L265–273 | 身份配对通过 Q591644 |
| term | [柏拉图主义（Platonism）](../units/terms/platonism.md) | 第一章；印刷页 16；OCR L650–654 | 身份配对通过 Q193589 |
| term | [自画像（Self-portrait）](../units/terms/self-portrait.md) | 第一章；印刷页 19；OCR L791–795 | 身份配对通过 Q192110 |
| term | [特定保护人服务（Servitù particolare）](../units/terms/servitu-particolare.md) | 第一章；印刷页 6, 7；OCR L165–177,195–198 | 尚无配对 |
| term | [领衔教堂（Titular church）](../units/terms/titular-church.md) | 第一章；印刷页 5；OCR L117–124 | 身份配对通过 Q1092939 |
| term | [群青（Ultramarine / oltremare）](../units/terms/ultramarine.md) | 第一章；印刷页 13；OCR L486–519 | 身份配对通过 Q219660 |
| work | [阿尔巴尼《圣安德烈朝拜殉道十字架》（Saint Andrew Adoring the Cross of Martyrdom）](../units/works/albani-servi-altarpiece-1639.md) | 第一章；印刷页 13；OCR L515–516 | 尚无配对 |
| work | [巴贝里尼大厅所谓草稿（归属有争议）（Supposed bozzetto for the Barberini Salone (disputed attribution)）](../units/works/barberini-salone-bozzetto-disputed.md) | 第一章；印刷页 12；OCR L463–464 | 尚无配对 |
| work | [贝尔尼尼的博尔盖塞枢机肖像头部（Bernini’s portrait head of Cardinal Borghese）](../units/works/bernini-cardinal-borghese-head.md) | 第一章；印刷页 17；OCR L700–703 | 版本待证 |
| work | [贝尔尼尼《大卫》（Bernini’s David）](../units/works/bernini-david.md) | 第一章；印刷页 19；OCR L763–767 | 身份配对通过 Q766487 |
| work | [贝尔尼尼的托马斯·贝克肖像胸像（Bernini’s bust of Thomas Baker）](../units/works/bernini-thomas-baker-bust.md) | 第一章；印刷页 17；OCR L668–670, 699–700 | 身份配对通过 Q5002075 |
| work | [卡马塞伊《圣塞巴斯蒂安殉难》祭坛画（Camassei’s Martyrdom of Saint Sebastian altarpiece）](../units/works/camassei-martyrdom-saint-sebastian.md) | 第一章；印刷页 10；OCR L336–338,372–374 | 尚无配对 |
| work | [卡马塞伊《圣彼得与圣保罗在马默蒂诺监狱施洗》稿（Camassei’s modello of Saints Peter and Paul baptizing in the Mamertine Prison）](../units/works/camassei-peter-paul-mamertine-modello.md) | 第一章；印刷页 12；OCR L464–466 | 尚无配对 |
| work | [卡拉瓦乔《圣保罗归化》委托（Caravaggio’s Conversion of Saint Paul commission）](../units/works/caravaggio-conversion-saint-paul.md) | 第一章；印刷页 11；OCR L397–401 | 版本待证 |
| work | [《圣马太与天使》（第一版）（Saint Matthew and the Angel (first version)）](../units/works/caravaggio-giustiniani-rejected-altarpiece.md) | 第一章；印刷页 10；OCR L349–353 | 身份配对通过 Q577248 |
| work | [卡拉瓦乔《圣彼得殉难》委托（Caravaggio’s Martyrdom of Saint Peter commission）](../units/works/caravaggio-martyrdom-saint-peter.md) | 第一章；印刷页 11；OCR L397–401 | 版本待证 |
| work | [1635 年演出的喜剧（题名未明）（Unidentified comedy performed in 1635）](../units/works/comedy-performed-1635.md) | 第一章；印刷页 21；OCR L858–863,894–895 | 尚无配对 |
| work | [归于科尔托纳的多里亚—潘菲利画廊稿组（有争议）（Doria-Pamfili modelli attributed to Cortona (disputed)）](../units/works/cortona-doria-pamfili-modelli-disputed.md) | 第一章；印刷页 12；OCR L461–463 | 尚无配对 |
| work | [费里《荣耀中的圣母与诸圣》（拉帕雷利祭坛）（Ciro Ferri’s Virgin in Glory with Saints for the Laparelli altar）](../units/works/ferri-laparelli-altarpiece.md) | 第一章；印刷页 13；OCR L507–508 | 尚无配对 |
| work | [费里《圣阿涅塞被引入天堂荣耀》穹顶壁画（Ferri’s Saint Agnes Introduced to the Glory of Paradise）](../units/works/ferri-sant-agnese-cupola.md) | 第一章；印刷页 12；OCR L437–453 | 尚无配对 |
| work | [费里圣阿涅塞穹顶彩色稿（Ferri’s coloured modello for the S. Agnese cupola）](../units/works/ferri-sant-agnese-modello.md) | 第一章；印刷页 12；OCR L437–441 | 尚无配对 |
| work | [盖乌利耶稣堂拱顶壁画工程（Gaulli’s vault fresco project at the Gesù）](../units/works/gaulli-gesu-vaults.md) | 第一章；印刷页 12；OCR L452–454 | 范围待对齐 |
| work | [加瓦塞蒂皮亚琴察圣安东尼诺司祭席装饰（Gavasetti’s decoration of the presbytery at Sant’Antonino, Piacenza）](../units/works/gavasetti-sant-antonino-frescoes.md) | 第一章；印刷页 9；OCR L323–326 | 尚无配对 |
| work | [圭尔奇诺《圣德肋撒从加尔默罗圣母领受会衣》（Guercino’s Saint Teresa Receiving the Habit from Our Lady of Mount Carmel）](../units/works/guercino-sicilian-altarpiece-1665.md) | 第一章；印刷页 9；OCR L295–307 | 尚无配对 |
| work | [兰弗兰科《受难》工作室画稿（Lanfranco’s unfinished Crucifixion in his studio）](../units/works/lanfranco-crucifixion-stock.md) | 第一章；印刷页 15；OCR L596–601 | 尚无配对 |
| work | [兰弗兰科《抹大拉》工作室画稿（Lanfranco’s unfinished Magdalene in his studio）](../units/works/lanfranco-magdalene-stock.md) | 第一章；印刷页 15；OCR L596–601 | 尚无配对 |
| work | [莫拉瓦尔蒙托内《空气》构图方案（Mola’s design for Air at Valmontone）](../units/works/mola-air-valmontone.md) | 第一章；印刷页 9；OCR L316–319 | 尚无配对 |
| work | [莫拉的瓦尔蒙托内《四元素》壁画方案（Mola’s Four Elements fresco programme at Valmontone）](../units/works/mola-four-elements-valmontone.md) | 第一章；印刷页 9；OCR L312–319 | 尚无配对 |
| work | [《阿什杜德的瘟疫》（The Plague at Ashdod）](../units/works/plague-at-ashdod-1631.md) | 第一章，印刷页 15；OCR 行 599–601 | 身份配对通过 Q3900760 |
| work | [普桑《屠杀婴孩》（本章提及）（Poussin’s Massacre of the Innocents (chapter 1 reference)）](../units/works/poussin-massacre-innocents.md) | 第一章；印刷页 10；OCR L372–374 | 候选待证 |
| work | [普桑为瓦尔瓜尔内拉新订的《春》（Poussin’s Spring commissioned by Valguarnera）](../units/works/poussin-spring-valguarnera.md) | 第一章；印刷页 15；OCR L599–601 | 尚无配对 |
| work | [雷尼《正义拥抱和平》委托（1617）（Reni’s Justice embracing Peace commission (1617)）](../units/works/reni-justice-embracing-peace.md) | 第一章；印刷页 14；OCR L531–534 | 尚无配对 |
| work | [雷尼《屠杀婴孩》（Reni’s Massacre of the Innocents）](../units/works/reni-massacre-innocents.md) | 第一章；印刷页 10；OCR L372–374 | 身份配对通过 Q2448678 |
| work | [里奇 1682 年《施洗者约翰斩首》委托（Ricci’s Beheading of Saint John the Baptist commission (1682)）](../units/works/ricci-beheading-john-baptist-1682.md) | 第一章；印刷页 9；OCR L326–328 | 尚无配对 |
| work | [鲁本斯《教皇圣格里高利与诸圣朝拜瓦利切拉圣母像》（Rubens’s Saint Gregory with Saints Venerating the Madonna della Vallicella）](../units/works/rubens-chiesa-nuova-altarpiece-1606.md) | 第一章；印刷页 11；OCR L402–404 | 尚无配对 |
| work | [萨基罗马嘉布遣会教堂祭坛稿（Sacchi’s modello for a Roman Capuchin church altarpiece）](../units/works/sacchi-capuchin-altarpiece-modello.md) | 第一章；印刷页 12；OCR L466–468 | 尚无配对 |
| work | [瓦朗坦《有算命人的音乐聚会》（A Musical Company with a Fortune-Teller）](../units/works/valentin-genre-commission.md) | 第一章；印刷页 11；OCR L389–392 | 尚无配对 |

298 卡已具双语关键内容、三部分结构、来源定位及句意摘要。这里记录来源范围内的成稿状态；未把形式齐备当作独立语义验收，未把补足阶段需要的字段提前编满。

## 既有八卡的当前补足交接（REV-045 更新）

| 对象 | 当前补充 | 下一步与限制 |
|---|---|---|
| [圭尔奇诺](../units/persons/guercino.md) | 适用 WD 字段、署名传记支持的生卒／亲缘／师承与迁居年表，账簿分工及书目；复用 WP 全文 | 配对已完成；迁居精确日、账簿顺序、荣衔及具体西西里作品仍待核 |
| [多梅尼基诺](../units/persons/domenichino.md) | WD 日期异文、亲缘／婚姻／任命、训练顺序与壁画签约／完成年表 | 配对已完成；死亡日和原因、兄弟姓名异文、入会年原页及职责继续待证 |
| [兰弗兰科](../units/persons/giovanni-lanfranco.md) | WD 多标签与年度履历、署名亲缘／任职、NGA 作品尺寸媒介与清册转录 | 配对已完成；卒日、具体出生地、扩展全名、荣衔及本章稿本待核 |
| [那不勒斯](../units/places/naples.md) | WP 全文复用；Q2634 适用属性、遗产区／缓冲区面积、书目编者与版本已分别记录 | 历史政权日期、Getty 原站及完整地图未核；Brill 书目仅索引可读 |
| [《阿什杜德的瘟疫》](../units/works/plague-at-ashdod-1631.md) | Q3900760 双向配对通过；WD 适用字段，WP 全文语义提取，Louvre 对象/年代/材料/流传补证 | 配对通过不等于事实无冲突；原庭审、原画目视、版画年代和完整书目仍待核 |
| [富尔维奥·泰斯蒂](../units/persons/fulvio-testi.md) | Q594614 双向配对，WP 和 Treccani 传记全文已读；补多角色、亲缘、教育、任职及著述 | 受洗日与生日区分；赦免年份、扩展全名、爵位原授予及作品归属待核 |
| [弗朗切斯科·丰塔纳](../units/persons/francesco-fontana.md) | 以家族研究第 2.3 节第 66–67 页及刊引信初步对应收信人，补多角色、亲缘及部分履历 | 尚未找到匹配 Wiki 对象配对；不能使用同名天文学家身份；生卒、教育及完整履历待补 |
| [泰斯蒂致丰塔纳的信](../units/archives/testi-fontana-bernini-letter.md) | 双语标题；Fraschetti 刊引支持 1633-01-29 罗马发信及艺术交往内容，章页和句子摘要齐备 | 所读为刊引，手稿、今日保管地、索书号和 Campori 初刊未核；无该封信的 Wiki 配对 |

八卡的早期过程、实际访问及阅读范围见 [knowledge.md](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md) REV-026–030。补足覆盖以本文件顶部当前数为准；所有既有对象均有当前处置。已完成的阅读与有效身份判断复用，访问失败项和未决项保留，避免无新条件反复请求。REV-063已发现补足内容中的具名关系端点尚未全部形成KU，故既有对象补足完成不再等同整个关系范围闭合。

## 第一部分状态与后续边界（REV-063）

| 顺序 | 已保存结果 | 下一步／边界 |
|---|---|---|
| 摄入与处理 | 唯一阶段定稿及逐行语义分析已保存 | 仅在发现来源缺页或错页时回退 |
| 知识元登记 | 现有298个有效对象均有当前成果 | 回补已采纳内容中缺失的具名关系端点；同一对象不建副本 |
| 对齐 | 298项均有结论；172项身份配对通过 | 126项未确认均有消歧或检索后边界 |
| 补足 | 现有298卡均有处置；193个WP对象／候选页全文已读；来源定位1594条 | 对回补的新端点逐项对齐与补足；不把全文已读等同实体已转化 |
| 关系 | 219条已有关系可追溯；298张现有卡均有关系展示 | 部分完成；从人物作品清单、履历及外部补足反查缺端点和缺边事实 |

第一章第一部分当前为部分完成。缺失端点与关系须按知识元→对齐→补足→关系重走受影响路径，完成后才能重新定稿。第六章、知识发现／涌现及页面仍后置；只有用户明确启动第二部分后，才基于已闭合范围的知识元和关系逐级开展 Topic → Theme → Dimension → Domain 的涌现分析。

2026-09-15章前收藏链复用了[卡尔皮奥侯爵](../units/persons/marchese-del-carpio.md)既有KU。依据实际读取的CEEH出版介绍，将旧出生地“那不勒斯”更正为“马德里”，保留旧来源并补出生地关系；[依据和未核范围](../../03-processing/patrons-and-painters-front-matter/process/knowledge.md#卡尔皮奥侯爵出生地更正)见章前过程。本次为共享实体单点更正，不表示第一章新增整体语义验收。
