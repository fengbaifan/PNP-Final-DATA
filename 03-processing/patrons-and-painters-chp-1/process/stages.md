# 第一章处理过程

## v6.0.0 接续记录（2026-09-09）

本轮只整理旧工件到新阶段入口，未重新阅读原典，不新增语义验收。原分析依据保留在 [source-map](../source-map.jsonl)、[semantic-units](../semantic-units.jsonl)、[candidate-ledger](../candidate-ledger.jsonl) 和 [manifest](../manifest.json)。

原 manifest 声明 completed 及 Agent 复读接受；该声明属于历史执行者，不能视为本轮独立复核。新的分析、修订理由和范围变化继续追加到本文件，不覆盖历史工件。

当前交接见 [阶段结果](../results/stages.md)。

## REV-013 第一部分测试：摄入

日期：2026-09-09。主 Agent 直接阅读；不调用知识发现或页面生成。

输入为完整章 OCR `02-sources/02-Markdown/01_CHP-1.md` 与同章 PDF；分节 OCR 为定位副本，不另算来源。书籍为 1980 年修订扩充版，版权页记录本次印刷 2006。印刷页 3–23；PDF 页码与印刷页码分别记录。

OCR SHA-256：`2c99c1b372f756b1482d746f5714fe930b538118792b52a3de0834f585d4f3fb`。
PDF SHA-256：`0b9a3ca88e6f09209bd20185948e18a68f527d0628e893940a7e3f07f6d22c86`。

来源可读，含脚注；跨章/图版引用只记录本章能支持的内容，不称已阅读所引原著。测试覆盖全章语义阅读；成稿选择可辨认且能承载本章具体事实、程序及跨章关系的对象，旁及例子和未能消歧的名称留在线索中，不宣称穷尽人名索引。

## REV-013 处理：全章阅读与覆盖

已顺序阅读完整 OCR 1–980 行及随页脚注，复读受工具输出截断影响的段落。PDF 共 22 页：第 1 页为 Part I/Rome 扉页；第 2–22 页对应印刷页 3–23。以下页码均指印刷页。已查看 PDF 印刷页 9，确认圭尔奇诺的图像志询问；旧条目将 PDF 页序 8 写成了书页 8。所有本章引用改按实际印刷页定位，原 OCR 不改。

| 阅读范围 | 语义判断与候选去向 |
|---|---|
| pp. 3–5 | 乌尔班八世的赞助是既有发展高潮而非突然开端；更替的教皇家族与同乡网络组织机会。古老领衔堂/家族墓所与新教堂的出资者不同，不能据建筑新旧推断艺术新旧。保留乌尔班、罗马、巴贝里尼对象，整体判断进入作者断言。 |
| pp. 6–7 | servitù particolare 包括优先服务、住所/月俸及作品另付报酬，不等于艺术家所有作品无偿归赞助人。萨基在 Antonio 而非 Francesco Barberini 的家中；1637–1640 年地位变动说明家庭服务有内部等级。科尔托纳、特雷维萨尼是同乡保护例子。 |
| pp. 8–10 | 独立工作室仍受委托尺寸、地点、光线和题材约定约束；画家也会主动要求图像志细节。圭尔奇诺 1665 年来函在 p. 9；莫拉通过书籍和交谈选择四元素中的神话。不可将作者所说的较大自由改写为完全不受控制。 |
| pp. 11–12 | modello 是有条件使用的预备油画/设计；上半世纪不能说普遍强制。盖乌利的作用是作者提出的可能性，不升为“发明了 modello”的关系。工期与大型壁画规模、圣年等相关，速度也会招致批评。 |
| pp. 13–14 | 定金、进度款、材料费、月付与按主要人物计价并存，且有例外。caparra 属支付安排；125 杜卡特是圭尔奇诺的报价，不是全行业固定价格。保留程序、术语和具体事例，金额不用作一般规律。 |
| p. 15 | 瓦尔瓜尔内拉看到普桑未完成的《阿什杜德的瘟疫》，商议完成，并另订《春》。前者不是从无到有定制，不能把观看/购买自动标为作品最初委托。罗萨准备现画售卖，偏好的历史画与顾客偏好的小风景画不同。 |
| pp. 16–19 | 高收入、学院、礼仪、教育、荣誉共同参与身份建构；这些是作者的历史解释。学院 1633 年征税与公共委托排他措施未充分执行并被撤回，不是稳固长期垄断；Francesco Barberini 为保护人。逸事的象征价值不等于事件可靠发生。 |
| pp. 20–21 | Schildersbent 是组织，1623 年成立是事件，需拆开；范拉尔同时属于学院，不能把两群体处理为互斥。职业上升、贫困与“艺术家异常性”并存；马尔瓦西亚转述的教皇言论有传闻性质，不记作可靠逐字发言。 |
| pp. 22–23 | 罗萨拒收定金、主张完工定价、使用展览与宣传；其独立策略不等于客观脱离市场。本章说他无真正追随者，脚注又举费里、卢蒂局部相似行为，须保留这一限定。 |

成稿取舍：保留上述制度、程序、事件和可辨认关键人物/作品；盖乌利、费里、兰弗兰科、克劳德等旁及事例在需要跨章使用时再成稿。多名脚注作者、受托画家及孤立轶事不在本次逐名建卡，来源位置仍由本表覆盖。章节解释保存为来源断言，不生成 Topic、Theme 或更高结构。

## REV-013 处理结果交接

全章阅读完成，可辨认候选交知识元阶段。需在对齐阶段处理：Antonio/Francesco Barberini；事件与机构混淆；PDF 页序与书页差一；Camillo Pamfili 与第六章 Camillo Astalli 的同名风险；《瘟疫》的购买与原始委托边界。旧 15 候选及 compact-v4 的 completed 仅保留历史，不沿用为本次执行证据。

## REV-014 覆盖标准修订

此前全章通读和代表性成稿不足以证明完整提取。本阶段重新打开，按原始行号、跨页和脚注衔接逐段核对，所有可辨认知识对象均进入提取或带明确原因的待消歧清单。49 个草稿未纳入 accepted.yml，后续原位修订，不新建副本。

## REV-014 逐行语义记录：第一章

记录原则：原始行号以完整章 OCR 为准；每行均归入下列语义跨度。相邻物理行合并为完整句，行末连字符、页眉和脚注不混入正文。空行及页眉只登记位置，不制造知识对象。对象、作者断言、被引证言和纯书目指向分别记录；能独立辨认的对象不得因次要而漏掉，未充分辨认者列出具体待解决事项。

### L1–190：章首至印刷页 6

| 原始行 | 复原与语义分析 | 知识对象、断言及处置 |
|---|---|---|
| 1–14 | 章名和第一部分扉页，不是正文或发现节点；PDF 1 无书页号，PDF 2 起为书页 3。 | 《赞助人与画家》第一章作为来源章节定位；Rome 复用地点。 |
| 15–25 | after-/noon 合回 afternoon。Passeri 的黄金时代回忆与 Haskell 的“高潮而非开端”是两层发言；宽松艺术实验不等于允许思想异端。 | Urban VIII、Giambattista Passeri；Counter Reformation 为历史运动候选；“赞助增长同时收紧控制”为 Haskell 断言。 |
| 26–34 | 前任教皇建立先例，精神/世俗统治者与家长身份产生张力；画廊、礼拜堂类型不等同某一实物。 | Paul V（1605–1621）、Gregory XV（1621–1623）；St Peter’s 作为具名建筑；教皇家族赞助程序。 |
| 35–44 ＋ 53–55 | 引文跨 PDF 2→3；L45–48 是页下注，L50–52 是页界/页眉，应先接完 Coke 引文再解释。'speedy revolutions' 指教皇更替和家族兴替，不是现代社会革命。 | Lord Arundell、Mr Coke；1620-10-08 信作为出版/手稿文献候选，身份缺全名需补足；“频繁更替带来机会”是证言，不普遍因果。 |
| 45–48 | Passed 与上文 Passeri 对应，为 OCR 变体；L’Hoggidi、1627 Venice 是书目事实，不表示本次读过该书。 | Abate Lancellotti、L’Hoggidi（1627）、Venice；Hervey 仅缩引姓氏，待书目定位，不编全名。 |
| 56–70 | govern-/ment 合回；新教皇亲友客户夺取职位、兴建宅邸，教皇死后失去收入。Peretti-Montalto 是明确例外。 | nepotism（教皇亲族任用）；Alessandro Peretti-Montalto、Sixtus V；现有 Gregory XV 复用。不可把所有后继任命写成例外全无。 |
| 71–83 | Maffeo Barberini 即后来 Urban VIII；Cardinal Ludovisi 即该段的 Gregory XV，Ludovico 为侄辈，不是同一人。Domenichino 因同乡教皇回到 Rome，获 Vatican architect 职位。 | Florence、Bologna、Venice、Italy；Domenichino、Cardinal Borghese（缺名字待核）、Ludovico Ludovisi；“Vatican architect”职业角色记录在人物，不另造人物。 |
| 84–88 ＋ 101–110 | 主句跨 PDF 3→4，L89–95 脚注不能作为修饰 'influential' 的内容；altar-/pieces 合回。寄宿→圈内宫殿及祭坛委托→声名扩大→独立接单是作者概括的职业路径。 | Annibale Carracci；艺术家职业引介程序；titular church（领衔教堂）、altarpiece（祭坛画）为语境明确术语。匿名年轻画家是概括模型，不造个人卡。 |
| 89–95 | Ameyden 1642 手稿发言被 Haskell 用来说明更替预期；引文非 Haskell 直接信念。ibid. 续接 Passeri，不能建立作者名 ibid。 | Ameyden、Relatione della città di Roma（1642）、Biblioteca Casanatense、MS.5001；Felici 缩引待核。Passeri 复用，原著未直接读。 |
| 111–124 | 旧教堂/家族旧墓所承载新画，与建筑年代简单对应艺术保守相反。'perhaps' 表示解释性推测。 | Aldobrandini、Peretti、Borghese 家族（作为赞助组织/家户待精确定名）；S. Maria Maggiore、S. Maria sopra Minerva、St Peter’s；nouveaux-riches 保留作者修辞，不强造术语。 |
| 125–141 ＋ 147–152 | Peretti-Montalto 引文跨 PDF 4→5，先排除 L142 脚注与页眉。建造耗时、预算超支、继承人兴趣改变，使装饰资金主体变化。 | Oratorians、Jesuits、Theatines、Barnabites、Capuchins；Rome 的佛罗伦萨/伦巴第侨民群体，身份是群体而非具名修会；S. Andrea della Valle；教堂建设与礼拜堂装饰接续程序。 |
| 142 | 引文由 Panciroli 经 Ortolani 转引，有中介责任。 | Panciroli、Ortolani 均为缩引，书目待补，不假称原话直接核验。 |
| 153–164 | 第二节，从宫内优先服务到无特定买家作画之间存在中介形态。作者说展览“通常”被视为失业者最后手段，已保留例外。 | art dealer（画商）、dilettante（鉴赏爱好者）、exhibition sale（展览售画程序）、servitù particolare；外国旅行者/代理为角色，没有具名对象不造卡。 |
| 165–177 ＋ 195–199 | pro-/duced 合回；句子延至下页萨基晋级，不能在此收束等级论述。famiglia 包括侍从与官员；nostro pittore 为授职措辞。 | servitù particolare、famiglia、nostro pittore；Parma、Venice、Correggio；学习资助程序；避免将一家人解释为血缘。 |
| 178–185 | 第二个脚注被 OCR 标为 3，内容为 Alessandro Vasalli 在 Mola/Pamfili 纠纷中的证词：优先服务仍须支付作品酬劳。 | Pascoli 为传记引用；Alessandro Vasalli、Pier Francesco Mola、Prince Pamfili；证词作为证据/断言，不当作所有时期通用法律。Montalto 缩引待书目定位。 |
| 186–189 | 两条旅行资助事例和一项授职均为脚注中的独立事实，必须保留。人名 OCR 不先自动“修正”。 | Cardinal Pio→Giovanni Bonari，Florence/Bologna/Modena/Parma/Milan/Venice；Cardinal Rospigliosi→Lodovico Gimignani→Venice；Maurizio di Savoia→Gio. Gasparo Baldoini。Bonari、Baldoini 拼写与枢机全名待 PDF/书目核对；Baudi di Vesme 为缩引。 |
| 49–52、96–100、143–146、190 | 空行、页界及运行页眉，已识别并从句子复原中排除。 | 无新增知识对象；保留原始定位。 |

### L191–385：印刷页 7–11 开头

| 原始行 | 复原与语义分析 | 知识对象、断言及处置 |
|---|---|---|
| 191–198 | 接 L177 的晋级句，pen-/sioners 合回。1637–1640 是低阶位置区间，1640 是进入高阶的年份。 | Andrea Sacchi、Antonio Barberini；家庭等级升迁事件与来源事实，不误写为连续四年均属最高阶。 |
| 199–213 | 服务带来不自由，也使艺术家进入能争取重要教堂委托的网络；“所有作者一致”仍为 Haskell 概括。 | Giovanni Lanfranco、Passeri；保护/职业引介程序。 |
| 214–223 | servi tit 为 servitù 的 OCR 变体。同乡与礼仪都影响住处/保护获得。 | Marcello Sacchetti、Pietro da Cortona、Cortona、Francesco Trevisani、Cardinal Ottoboni（第六章可具名）；出生地、赞助、同乡判断各自记依据。 |
| 224–228 ＋ 242–251 | 句子跨 PDF 6→7，不能读成“尽管有脚注所以自由”；制度优势受政治更替和职业阶段影响，独立住处与优先服务可兼容。 | servitù particolare 的变体与退出条件；不另造匿名艺术家。 |
| 229–237 | Incisa della Rocchetta 的年份为书目；具体离境限制来自 Pascoli/Montalto 转述；Trevisani 传未刊。 | Duke of Bracciano（待全名）、Pietro Mulier、Guglielmo Cortese、Valmontone、Prince Pamfili；Biblioteca Augusta、Perugia、Pascoli 未刊 Trevisani 传（MS.1383）；Battisti 缩引待核。 |
| 252–264 | 合同是否书面订立取决于规模；场所照明为远程委托的具体信息缺口。 | 委托合同订立、现场/照明沟通程序；fresco（壁画）、altarpiece 术语。 |
| 265–273 | 成对布置、嵌墙装饰影响尺寸和构图，是装饰语境而非所有画的形式规律。 | pendant paintings（成对绘画）、gallery picture（画廊画）；成对尺寸协商程序，匿名个案不另造作品。 |
| 274–277 ＋ 288–294 | 'but the contracts' 跨 PDF 7→8，中间是脚注；强控制的可能与合同文本少细节并存。 | 图像志协商程序；宗教题材不自动等于无创作自由。 |
| 278–283 | Rosa/Luti 是后文交叉定位；Piola 的居住个案、Chigi 津贴为独立脚注事实。 | Benedetto Luti、Paolo Girolamo Piola、Marchese Pallavicini（待具名）、Genoa、1690 年来罗马居住协商；Flavio Chigi、Mario de’ Fiori、每月 30 scudi；Soprani/Golzio/Rothlisberger 缩引待核；Claude 复用。 |
| 295–307 | monas-/tery 合回；1665 年是来函委托语境，不自动证明作品完成年。艺术家问色彩、会规载体、圣者位置、悬挂与光线。 | Guercino；西西里祭坛画委托（事件/拟制作品待区分）；Sicily；Madonna del Carmine、Christ Child、St Teresa、St Joseph、St John the Baptist 作为图像人物/题材对象，不补其生平。会规未具书名，保留指代。 |
| 308–319 | 四季是泛举题材；四元素是莫拉在 Valmontone 的具体工程。Virgil 及注释本未具书名，不能自动指定为某版本《埃涅阿斯纪》。 | 四季/四元素（题材术语）；Valmontone 四元素壁画及“空气”方案；Mola、Pamfili、Virgil；Juno、Chloris、Zephyr、Ganymede、Iris、Turnus 为神话人物，Milky Way 为图像母题；匿名律师不造名字，书籍待精确识别。 |
| 320–321 ＋ 335–338 | L321 把正文 full- 与脚注 1 粘接，应接下页 length，复原 full-length figures 后再读脚注。 | 按主要全身人物计价程序；Urban VIII 委托 S. Sebastiano on the Palatine 八人《圣塞巴斯蒂安殉难》；Andrea Camassei 由 L372 脚注明确，不把雕刻家同名错配。 |
| 321–330（脚注） | 四个地方委托/建议例子都提取，不因位于脚注忽略。SS. i Deputati 是执行委员称谓，不是作品标题。 | Saverio Savini/Gubbio/1608；Mario Minnitti/Augusta(Sicily)/1617；Camillo Gavasetti/S. Antonino/Piacenza/1624 壁画；Sebastiano Ricci/Confraternità di S. Giovanni Battista Decollato/Bologna/1682《施洗者约翰斩首》；Vincenzo Armanni（OCR Armarmi）、致 Camillo 信；Gualandi、Giuseppe Agnello、von Derschau、Ruffo 为引用。 |
| 339–356 | 可移动画的市场流通改变题材/尺寸重要性；Giustiniani 买退画与 Piola 获题材自由是不同个案。 | 可移动画廊画、收藏鉴赏术语；Marchese Giustiniani（待全名）、Caravaggio、被拒祭坛画（未命名，待消歧）；Giovanni Adamo（待姓氏）、Piola、1690-02-03 信。 |
| 357–371 | 统一题材与多画家并用是折中；'evidently' 标明对曼图亚方案的推断，不去掉语气。 | Alexander the Great、Samson 作为题材人物；Duke of Mantua（待按时段消歧）；Marchese del Carpio（西班牙驻罗马大使，待全名）；绘画寓意征集、系列委托程序。 |
| 372–377 | Camassei 信息来自收据；Guido/Poussin 的《屠杀婴孩》合同只是作者希望找到，并未实际引用合同。 | Andrea Camassei、A. Bertolotti、Artisti bolognesi（缩题待核）；Guido Reni 与 Poussin 的两项《屠杀婴孩》作品候选；Friedlaender/Bottari/Luzio/Bellori 书目引用。 |
| 378–385 | 页界后新论点尚未完句，须继续下一段，不把科尔托纳的拒选题裁成拒绝绘画。 | 该语义跨度延续 L386–393。 |
| 238–241、284–287、331–334 | 空白、页码/页眉已排除；印刷页 11 在 OCR 写作 ii。 | 定位信息，不是章节二。 |

### L382–590：印刷页 11–15 的合同、草图与市场

| 原始行 | 复原与语义分析 | 知识对象、断言及处置 |
|---|---|---|
| 382–392 | 接上段未完句。科尔托纳拒选题而罗萨反对按要求作画，但后者仍向朋友求建议，不能二分为完全服从/完全自主。 | Valentin（按本段法国风俗画家身份待全名）、其吉卜赛人/士兵/奏乐女性委托（未具标题，保留事件）；Pietro/Rosa 复用。 |
| 393–412 | 油画稿或素描可用于监督，但上半世纪并非普遍强制。鲁本斯初到罗马的条件不同于卡拉瓦乔的难合作声誉。 | Caravaggio 1600《圣保罗归化》《圣彼得殉难》委托；Rubens 1606 Chiesa Nuova 祭坛画；Lanfranco 1640《教皇利奥与阿提拉》申请，Pope Leo、Attila 为画题人物；'in tela il disegno' 原画布构图草绘，暂不等同独立 modello。 |
| 413–414 ＋ 430–446 | Cortona 跨 PDF 10→11 被脚注截开。正文关于博洛尼亚画家的绝对说法须与同页脚注中萨基、卡马塞伊 modelli 并读；Gaulli 引入说、草图欣赏兴起皆带可能语气。 | Giovan Battista Gaulli、Genoa、Wittkower；Ciro Ferri 1670 S. Agnese/Piazza Navona 穹顶彩稿及不得擅改条件；Pamfili 家族；modello、bozzetto、草图收藏（术语/实践），不建 Gaulli “发明”边。 |
| 415–425 | Onorato Gini 1666 信为转引；1640-07-14 Lanfranco 信从 Naples 发出。脚注 6 被误读为 8。 | Onorato Gini、Claretta；Pollak、Costello、Friedlaender 缩引；Naples；第三章 p.70 是未读交叉引文，仅作定位，不谎称已读。 |
| 447–460 | 工期条款与实际完成速度分开；Holy Years 为可能催工场景，速度高可获奖也可受贬。 | Ferri 穹顶四年、Gaulli Gesù 拱顶/横翼八年；Giovanni Odazzi、Luca Giordano、Giacinto Brandi、Gaspard Dughet；Gesù 教堂、Holy Year（圣年）术语；工期/奖励程序。 |
| 461–468 | 正文“没有确定例子”被脚注限定；Grassi 的归属未经普遍接受，Waterhouse 提供具体反例。 | L. Grassi（1957）、Briganti（OCR Brigand）、Waterhouse；Palazzo Doria-Pamfili galleria 的争议稿、Barberini Salone 的争议 bozzetto；Camassei《圣彼得与圣保罗在马默蒂诺监狱施洗》稿、Pinacoteca Vaticana、Mamertine prison；Andrea Sacchi（OCR Sacelli）、Rome Capuchin church 祭坛稿、Colnaghi’s、London、Denis Mahon。旧目录号与“现藏”仅限 Haskell 写作时点。 |
| 469–472 | 具体书目指向，不另制造人物行为。 | Wittkower、Golzio、Tacchi-Venturi、Pascoli 缩引保留待书目核对。 |
| 478–485 | arrange-/ments 复原。款项含定金、半成时付款、结余和奖金，壁画可能月付；“通常”与例外共存。 | caparra、分期付款、壁画月付程序；七分之一至近一半是作者材料范围，不是法律统一比例。 |
| 486–497 | stretcher、priming、ultramarine 的负担可分配；脚手架与离家施工食宿另计。 | 画框/底料/群青（材料术语）、材料费分担与食宿供给程序；Mola、Valmontone、Pamfili 实例。不得由菜肴描述推出合作没有争议。 |
| 498–502 ＋ 528–552 | 论定价跨 PDF 12→13；主画人物与背景人物不同，客户地位也影响金额。“慷慨赠礼”与市场化同时存在。 | Domenichino 130、Lanfranco 100 ducats／主要人物，Naples Cathedral（依 PDF 印刷页 13 纠正此前合写 130 的错误）；Giulio Mancini；Guido Reni 1617《正义拥抱和平》委托、Duke of Mantua 待当时身份；Paolo Guidotti；Claude、Leopoldo de’ Medici；Guercino 125/80 ducats 拒价。不能混币种或把每人价推广到所有画家。 |
| 503–508 | 三项定金实例：Albani 450/1000 lire、Mola 300＋1000 scudi、Ferri 50＋180 scudi。 | Francesco Albani、1639 委托（题材未明）；Ferri 在 Cortona 为 Annibale Laparelli（OCR Laparclli）作祭坛画；与 Mola 工程复用，不从不同付款数字另造同一对象副本。 |
| 509–513 | 两封信支持预付/材料惯例，但收发双方与日期不可漏。 | Berlingete Gessi→Don Cesare Leopardi d’Osimo（1647-07-10），Carlo Quarisimini（OCR Quarisinini，待核）→Conte Ventura Carrara（1696-07-11）；Osimo 仅人名附属地，待确认是否确指来源地点。 |
| 514–523 | 多项材料承担例外；'sor' 为 for。不同颜色名是列举材料，不能将未核对古色名硬译为现代标准颜料。 | Camassei/Urban VIII 1633；Bonifazio Gozadini/Albani/Chiesa de’ Servi(Bologna)/1639；Pamfili/Mola/1657；Gavasetti/Piacenza/1624；Mattia Preti、Artemisia Gentileschi 的计价信件。古材料名保留在材料术语依据中。 |
| 553–561 ＋ 575–590 | 'as we have seen' 跨 PDF 13→14。Rome 为 richest city in Italy，不是 Europe。供需吸引及财政突变风险是作者的机制解释。 | Rome、Borghese/Barberini 家族；国际艺术市场、工作室现画售卖程序的背景；一般因果转为 Haskell 断言，不标为独立统计事实。 |
| 562–570 | 第二组具体来函与短引文献，Ruffe/Rufifo 与 Ruffo 的 OCR 变体不可另建重复人名。 | Jacopo Salviati→Leopoldo de’ Medici（1662-07-22）；Fabrizio Arragona→曼图亚公国大臣（1621-10-09）；Guercino→Don Antonio Ruffo（1649-09-25）；Ferdinand Boyer、Faldi、Luzio、Mancini、V. Ruffo 书目指向，Antonio 与编辑 V. Ruffo 不能混同。 |
| 426–429、473–477、524–527、571–574 | 页界、页眉、空行已排除，保留纸页到 PDF 页序的映射。 | 无知识元；跨页句已在上列复原。 |

### L591–790：印刷页 15–19 的交易、学院与身份

| 原始行 | 复原与语义分析 | 知识对象、断言及处置 |
|---|---|---|
| 591–606 | 买方看见初稿后议价完成，与事前指定新画区分；Rosa 顾客买小画但他重视大历史画。 | 工作室存货画交易程序；Valguarnera、Lanfranco《抹大拉》《受难》未完稿；Poussin《阿什杜德的瘟疫》与另订《春》；Rosa 不具名画仅记录销售事实。 |
| 607–615 ＋ 620–627 | society 跨 PDF 14→15 接 L612；第五章引用不是本轮已读依据。'bohemian' 是当时社会位置的作者表述。 | art dealing、art exhibition 复用；Michelangelo、Raphael；bohemian（艺术家波希米亚群体）术语；Costello、Baldinucci（OCR Balditiucci）缩引。 |
| 628–655 | Malvasia 让 Paul V 说的话有 'corre voce' 传闻标记；艺术家实用地位上升与神秘光环下降的区分不可丢。 | Malvasia、Benvenuto Cellini、自传文献；Bernini、Sixtus V、Leo X；Platonism、genius（天才观）、artistic status（艺术家社会地位）术语；整体变化是作者史学断言。 |
| 657–662 | 引文可信度须沿脚注限定，Passeri/Pascoli 对 Bernini 有偏见，Wittkower 判断也非本次统计。 | Malvasia/Fraschetti/Passeri/Pascoli/Wittkower 引用链；否决把传闻教皇原话当作直接核实引文。 |
| 656 ＋ 668–677 | 'in themselves responsible' 跨 PDF 15→16，中间为页下注。Bernini 6000 scudi 明确异常，不代表常规胸像价；Maratta/Gaulli 肖像金额可比较但不推导收入总额。 | Bernini 肖像胸像、Maratta 全身肖像 150、Gaulli 100；Rembrandt、Baldinucci、竞价提升职业声望的转述。 |
| 678–698 ＋ 717–722 | 学院公共委托排他权在跨页后的正文被限定为未完全施行、后撤回，不可截断为垄断已经实现。 | Accademia di S. Luca、Federigo Zuccari、Apostolic Chamber、Paul V 1605 每年圣路加节赦一死刑犯、Gregory XV 1621 章程、Francesco Barberini 保护人、Urban VIII 1633 征税措施；gild（行会）及艺术/机械技艺区分。 |
| 699–703 | 脚注指明胸像客户及文献，金额不同对象不可合并。 | Thomas Baker、其 Bernini 胸像、Victoria and Albert Museum；Fulvio Testi→Conte Francesco Fontana 的信；Cardinal Borghese 肖像头部；Fabbrica di S. Pietro 每月薪俸。当前馆藏只记书中时点。 |
| 704–712 | Bellori 对 Maratta 提高报酬的肯定是批评话语；不能将“画家应感激”当作实际集体声明。 | Bellori、Pevsner、Mahon、Missirini、Hoogewerff 缩引；既有 Pascoli、Baldinucci 复用。 |
| 723–736 | history pain-/ters、respect-/ability 复原。早期可收风俗画家/镀金工；1645 后镀金工次等资格；法国影响后的教条化为作者后续时期判断。 | history painting（历史画）、gilder（镀金工艺身份）、学院会员制度变化；不能给早期学院强加晚期规则。 |
| 737–752 ＋ 763 | 'seems to have been prepared' 跨 PDF 17→18；上层礼仪的模仿与作者对传记叙述的依赖明确。 | Giacinto Brandi、Ciro Ferri、Lodovico Gimignani、Giammaria Morandi、Andrea Procaccini、Spain；他们的生活方式分别是传记所述，不作为其他艺术家的事实。Maratta 委托抱怨有具体来函。 |
| 753–758 | 两位学院会员及一封付款抱怨信，不能跳过。 | Pieter van Laer、Michelangelo Cerquozzi；Francesco Novetti→Don Antonio Ruffo（1670-03-22）；V. Russo 为 V. Ruffo 疑似 OCR，待核。 |
| 763–777 | Charles V 捡画笔→Barberini 举镜/教皇递画布是逸事母题类比。Mola 乘车与 Ghezzi 的职位描述需分开，'same artist' 指 Mola 不是 Bernini。 | Ridolfi、Charles V、Titian；Bernini《大卫》中的自我形象（作者解释）；Innocent X、Queen Christina、Mola；Giuseppe Ghezzi、Society of Arcadia、Clement XI、Innocent XIII、Duke of Parma（待时段）；Cavaliere dell’abito di Cristo、gentiluomo d’onore 荣衔术语。 |
| 778–790 ＋ 后续 791–797 | 新闻阅读和谈吐被作为教育/尊严条件；Passeri 贬评是职业礼仪话语，不转为人物客观人格标签。 | Filippo Lauri、news-sheets（新闻纸）术语；Passeri 关于 Cerquozzi 的文字由脚注归属，必须在下一页脚注复核。 |
| 616–619、663–667、713–716、759–762 | 页码 17 被识别为 U，18 为 i8；排除这些字形后才能定位制度史。 | 无研究对象；保留疑点供 PDF 核对。 |

### L791–980：印刷页 19–23 的荣誉、画家帮与罗萨

| 原始行 | 复原与语义分析 | 知识对象、断言及处置 |
|---|---|---|
| 791–795 | 承接谈吐的作用，艺术家自画像的共同面貌是 Haskell 视觉概括，不是本次已逐幅看图。 | self-portrait（自画像）术语；未具名作品不强制虚构标题。 |
| 796–806 | 古例说明荣衔授予早于十七世纪，后期常规化不能抹去例外。 | Emperor Frederick III、Gentile Bellini、Count Palatine；Charles V→Titian（1533）所授 Lateran Palace/Court/Imperial Consistory 爵号；Michelangelo Cerquozzi 为 Passeri 引文对象。 |
| 811–818 | 被承认艺术家与贫困画家并存；'easy enough to imagine' 明确是作者想象性重构。 | 批量 devotional pictures（祈祷图像）制作、经销及节日展卖；贫困状态不是具名个人的既成事实。 |
| 819–833 | Schildersbent 是互助组织，bentveughels 指成员群；1623 后字符需看 PDF。抗税不排除 Van Laer 同时学院会员。 | Schildersbent、成立事件、bentveughels；Via Margutta、Piazza di Spagna；组织宴饮/入会仪式。'to this day' 限 Haskell 写作时点，不更新为今天。 |
| 834–846 ＋ 858–861 | And Gianandrea Carlone 跨 PDF 19→20，L847–853 为脚注。传记选择偏见已明示，不据无反对记载推导全体家庭支持。 | Andrea Pozzo、Mario de’ Fiori（两个未命名儿子记角色不编名）、Gianandrea Carlone、Marchese Costaguti 家庭总管及其妹妹（未具名）；1635 喜剧（标题不可得，文献候选待考）。 |
| 847–853 | Procaccini 父母并不认同绘画但未阻止，正好限定正文的“缺乏反对”。 | Andrea Procaccini、Narducci（1870）、Hoogewerff（1952）、Pascoli 书目指向；不漏脚注反例。 |
| 862–874 | 接受艺术家特殊性与职业尊严并行；Bernini 父亲/兄弟为传承例外但未具名，不由记忆补写。 | 家族作坊/技艺传承程序；Bernini 家属待消歧；Rome/Venice 社会地位比较为 Haskell 断言。 |
| 875–881 | 事前约定价和按人物计价显示艺术仍被类比为较高工艺；不是判断画家没有创造力。 | 委托/按人物计价复用；艺术与机械技艺区分的作者断言。 |
| 882–893 ＋ 905–926 | 'against this background ... we must consider' 跨 PDF 20→21，先排除脚注和页眉。Vasari、Malvasia、1676 来信处于不同时代，不能合并成同时代证言。 | Vasari、artistic temperament（艺术家气质）、Giovanni Perugini、Turin、Savoy 宫廷（具体君主待时段核对）；Salvator Rosa；Compagnia della Morte 是被史料修正的传说，不建真实成员关系；展览宣传和 claque（喝彩者）组织程序。 |
| 894–900 | Haskell 不能找到喜剧本体，不能假称已识别书名；两封信可作为文献候选。 | G. Delogu（1928）、G. L. Bianconi 1762-11-22 信（收信人未给）；Paolo Negri→Marchese di S. Tommaso（1676-12-24）；Bottari/Claretta 为转引。 |
| 927–943 ＋ 952–958 | 'roots of the generally held conception' 跨 PDF 21→22，脚注 L944–947 不属于该句。拒定金为保留改画别题自由；按质量定价否定可事前完全评估。 | Rosa 致 Antonio Ruffo 1666-04-01 信；artistic independence（创作独立）、inspiration（灵感）术语；拒收定金与完工定价程序。自述与 Haskell 的独立性解释分层。 |
| 944–947 | 书信原文为 Haskell 转引，不表示本次看到原手稿；V. Russo/OCR 需核对编辑署名。 | 前列 1666 信复用，不再造第二文献。 |
| 959–970 | 宣传、完整性、独立和气质合为作者解读；“没有真正追随者”不等于没有任何局部相似做法。 | Baldinucci 对 Rosa 的评价；十九世纪浪漫接受为历史论述，不能在当前启动涌现。 |
| 971–980 | 最后脚注是全章关键限定：de Rosis 对质量的评价，Ferri 的拒预付与忙碌，Luti 的低依附姿态。 | Giuseppe de Rosis→Antonio Ruffo（1663-09-22）；Ciro Ferri→Antonio Ruffo（1672-09-19）；Benedetto Luti；Pascoli/Baldinucci/Ruffo 引用链。 |
| 807–810、854–857、901–904、948–951 | 余下空行、页眉及页界均已排除。 | 无研究对象。 |

### 第一章本次处理进度

已完成原始 L1–980 的逐行复读和语义跨度登记，包括脚注和全部页界。该覆盖不等于知识元已经完整成稿：名称/作品/书目信息的消歧、逐对象去重和映射尚待完成。原来的代表性清单已被本节更广的对象/断言清单取代，不据 49 个草稿数量声称全章提取完成。

### PDF 疑难文字核对（第一章）

直接查看印刷页 6、9、20 的 PDF 页面：L186 的 Giovanni Bonari 实为 **Giovanni Bonati**；L179 第二个脚注编号为 **2**，不是 3；L821 的 `1623?` 实为 **1623. 加上标脚注 2**，不是作者对年份提出问号。Gio. Gasparo Baldoini 拼写在该页可见，先依原页保留，不再猜改。L295–307 的圭尔奇诺来函位于印刷页 9。所有纠正记录在处理层和对象来源中，原 OCR 不覆盖。

### 当前样例边界（REV-015）

仅第一章继续向下交接，第六章暂停。第一章全行语义记录与对象登记是后续成稿依据；不以先前跨章草稿的数量作为本章完成标准。可辨认的人物、地点、机构、作品、文本、术语、程序和事件均须有处置；仅为短书目引用而尚无可辨认身份/题名的项目保留书目待证，不虚构正文内容。

## REV-015 当前交接结果

全行复读后的对象成稿、对齐与章内补足已写回：271 张相关卡中 270 张登记可用，Borghese 跨段合并身份候选 1 张暂缓。复杂断言 12 条，正式有向关系 137 条；去向与逐对象目录见 04 的当前结果，原先 49 张代表性草稿口径不再作全章完成依据。

追加原页核对：印刷页 9 为 Vincenzo Armanni；印刷页 13 为 Berlingero Gessi、Carlo Quarismini、Annibale Laparelli、Bonifazio Gozadini。第 18、22 页脚注署 V. Ruffo，不是另一个 V. Russo。费率前者 Domenichino 130、后者 Lanfranco 100，纠正处理表及知识卡前稿错误。原始 OCR 与 PDF 全部保持原样，修订缘由在 04 过程中同时保留。

## REV-016 提取边界复审

980 行的阅读覆盖保留；上一轮代表对象数量不能证明全量提取。回读 L179–189、321–330、354–425、461–468、503–523、690–703、858–863、894–900，按文献/建筑/作品独立对象补漏。具体处置与 26 个新增对象见 04 的过程和结果。

为解决本章身份和引文，定向读取同书书目 L69–70、161、546–547，及索引 L34、527–533、1190–1194；索引明确第 4 页 Scipione Borghese，未据此合并第 17 页肖像。以上为已有书内辅助页，不是扩展章节测试，不新增/改写来源。未解决的短引书目、材料/设备实物与图像角色类型边界均已明确记录，不再把它们笼统视为“无知识元”。
