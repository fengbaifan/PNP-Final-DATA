# 第一章以前材料：摄入与语义处理结果

任务：`patrons-and-painters-front-matter`；依据REV-083、084。范围为书名版权、两版序言、目录、图版清单、图片来源和第二版导言。**摄入与处理已完成；知识元登记已接续，见[知识阶段当前结果](../../../04-knowledge/results/patrons-and-painters-front-matter.md)。** 本文件保留本阶段的原始候选和分析；登记后的实体映射与待决去向由知识阶段结果维护，关系候选尚未转为正式边。

## 1. 摄入定稿

书籍：Francis Haskell, *Patrons and Painters: A Study in the Relations Between Italian Art and Society in the Age of the Baroque*，Yale University Press，1980修订扩充版，本件印刷2006。doc-id：`patrons-and-painters`；本任务版本键：`patrons-and-painters-1980-print2006-front-matter`，以如下哈希确定实际载体。

| 简称 | 来源资产 | 行数／页数 | SHA-256 |
|---|---|---:|---|
| PDF | [CHP-0Cover.pdf](../../../02-sources/01-book/CHP-0Cover.pdf) | 15页 | 502a6dcf66b5c01b09209ad92abbf6b1a172488de1058750ca9db9b906b2d266 |
| A | [00_01_Title_Copyright.md](../../../02-sources/02-Markdown/00_01_Title_Copyright.md) | 31行 | 75dfb1077cb870473ecb3a5576fe6b5ef5b2d244bfe43dc55d884d66ebfe1c32 |
| B | [00_02_Preface_2nd_Ed.md](../../../02-sources/02-Markdown/00_02_Preface_2nd_Ed.md) | 19行 | 8de19ec8cbf405958ad3c47f1cf4023a18a4fce8323e3e34b93ad36dfed3d7d0 |
| C | [00_03_Preface_1st_Ed.md](../../../02-sources/02-Markdown/00_03_Preface_1st_Ed.md) | 31行 | e793793f71fc5e9b9ba97a1c12fa50d497ec4de89f3c19f247c4a93228618c4a |
| D | [00_04_Contents.md](../../../02-sources/02-Markdown/00_04_Contents.md) | 3行 | c808682cc2d3d10e01ff871d3f575a9c295779b997ea68009f94915bf463cadb |
| E | [00_05_List_of_Plates.md](../../../02-sources/02-Markdown/00_05_List_of_Plates.md) | 198行 | 96aa11521c311c17676147c3ec99fb47d7cf9042a13bc58768c3742553ac5f83 |

以上A–E均按原文件一基物理行号引用，共282行。长行包含多句时逐句分析，不能因一行很长略过后半。A–E的Page标记并非统一印刷页序。PDF与Markdown来自同一载体，不算独立证实。图版目录已读不等于68组图版原图均已观看。

| 材料 | PDF页 | 印刷页／版面 | Markdown定位 |
|---|---:|---|---|
| 书名、版权及献辞 | 1–2 | 未印页号 | A:L1–31 |
| 第二版序言 | 3–4 | 首叶无可见页号，续页vi；首叶按续页推为v | B:L1–19 |
| 第一版序言 | 5–7 | 首叶无可见页号，续页viii、ix；首叶按续页推为vii | C:L1–31 |
| 目录 | 8 | 无可见印刷页号 | D:L1–3、E:L1–32 |
| 图版清单 | 9–13 | xii–xvi；xii据目录与续页推定 | E:L33–160 |
| 图片来源 | 13下半页 | xvi | E:L161–172 |
| 第二版导言 | 14–15 | xvii–xviii；xvii据目录与续页推定 | E:L175–198 |

摄入判断：本地15页均可读取，材料有连续的内容结尾；实际缺陷是OCR错词、斜体漏词和文件分割错置，并非发现缺失的正文页。Part I / Rome扉页另在CHP-1.pdf第1页，已由[第一章定稿](../../patrons-and-painters-chp-1/results/stages.md)覆盖。书中所列其他章节、图版原图及引用文献全文不纳入本轮已读声明。

## 2. 完整语义处理与行覆盖

摘要是模型转述。全部“作者认为／批评者认为”保留说话者，不把历史作者主张直接当本项目判断。原句引用统一回上表A–E及指定行段，扫描改读证据见[过程记录](../process/stages.md)。实体候选详见[实体候选表](entity-candidates.md)，其中FM-E为正文提及，FM-P为图版子项，FM-H为供片者。

| 跨度 | 原文位置 | 句意摘要与处理 | 候选／交接 |
|---|---|---|---|
| FM-S01 | A:L1–14 | 题名、副题、作者、修订扩充版、出版社、两出版地与1980；装饰线误识排除 | FM-E001、002、004、地名组；版本字段 |
| FM-S02 | A:L15–17 | 献给Larissa及意大利朋友；版权属Yale University；本次印刷2006 | FM-E003、005；献辞不等于配偶关系 |
| FM-S03 | A:L18–31 | 使用声明、印刷地、中国、国会图书馆编目、作者生卒、分类号、两个ISBN与索引标志；Bibliography:p.为空 | FM-E006、088及书目属性；版权条款作为本印本文本记录 |
| FM-S04 | B:L1–4 | 1963以后艺术研究增加；作者承认未跟进全部研究、若重写会改变重点；“只有一项重大批评”是其判断 | FM-E001；不能当文献检索完整率 |
| FM-S05 | B:L5–7 | 三路修订：正文订误、导言回应批评、后记按章评议新文献；1966意译版已开始订正；未列DBI不等于否认价值；书目与索引重编 | FM-E007及文献版本属性；my／I指Haskell |
| FM-S06 | B:L8–10 | 1963时仅见文献的若干画作后来被发现，新增复制图；不列具体对象 | 保留未具名作品群，不能分配到任一图版 |
| FM-S07 | B:L11–13 | 初版出版支持、Nicoll提议新版、Enggass／Hibbard／Blunt纠错、其他人协助书目图版；跨行Marco Chiarini、Ann Sutherland Harris | FM-E008–018；各角色分开 |
| FM-S08 | B:L14–19 | Tim Munby、Ben Nicolson是亲近朋友及咨询者，写序时已逝；Oxford、1979年11月为署地时间 | FM-E019、020与地点；不推定精确卒日或逝世事件日期 |
| FM-S09 | C:L1–4 | 书名不足以概括方法，序言承担释义 | 文献结构，不新造“题名不足”实体 |
| FM-S10 | C:L5–6 | Baroque为作者方便使用的时空范围；赞助人自身兴趣与所委托艺术质量不总一致；篇幅不是艺术价值排序 | FM-E021、022、023；共和国为政体，不与Venice城市合并 |
| FM-S11 | C:L7 | 第一部分着重Urban VIII时期Rome；放弃十八世纪Rome是作者取舍及论证，随后导言回应争议 | 原书研究范围，不作未来Domain |
| FM-S12 | C:L8–12 | 国际赞助和外省个人延续罗马经验；“These men／they”指两类赞助者，Ferdinand是品味评价的例外；跨页接“不受教条约束” | FM-E024、025；群体论述不逐人套用 |
| FM-S13 | C:L13 | 后部转向叙事，涉及建筑、雕塑、园林；经济和思想变化是作者解释；篇章变短被解释为绘画衰落表现 | 方法／评价断言，非普遍因果边 |
| FM-S14 | C:L14–16 | 明确避免以赞助“解释”艺术、拒绝普遍规律，保留内部发展、个人偶然性；希望别人综合；不追踪每件作品 | term／方法候选；不能误译为否认一切艺术社会联系 |
| FM-S15 | C:L17–19 | 图版用于帮助理解论证，选择不等于质量榜；Enzo Crea协助组织图像 | FM-E026；friends指作者称谓，不强推所有致谢者皆朋友 |
| FM-S16 | C:L20 | 研究处于历史与艺术史之间，承认跨领域跟踪难度与朋友帮助 | 方法语境、未具名群体保留，不建匿名人物KU |
| FM-S17 | C:L21–22 | Warburg图书馆、所在学院支持；Munby解决问题、Rylands读稿校样、Orna编索引、Constable印刷 | FM-E027–032、094；my own College结合签名定位 |
| FM-S18 | C:L23–25 | Pignatti提供Correr研究便利；意英学者协助；Waterhouse、Mahon、Calvocoressi读稿；Pevsner启发议题；Blunt、Levey讨论；Nicolson持续审稿 | FM-E033–046；读稿支持不等于同意全书论证 |
| FM-S19 | C:L26–31 | Haskell署名，King's College／Cambridge，1962年7月；序言时间不是出版时间 | FM-E001、028及日期属性 |
| FM-S20 | D:L1–3 | 只有目录标题，正文续入E | 无正文缺失判断，跨文件接读 |
| FM-S21 | E:L1–5 | 文件名误导；实际是目录的图版、图片来源与导言入口 | 作为本书章节／页码属性 |
| FM-S22 | E:L6–15 | 原书Part I Rome、Part II Dispersal及1–8章题与起页 | 文献内部组织；不执行第六章，不预建Theme |
| FM-S23 | E:L16–32 | Part III Venice、9–17章和结论／附录／后记／书目／索引页号 | Algarotti提及进入FM-E047；章题非实体全集 |
| FM-S24 | E:L33–65 | 图版1–16逐子项列作者、作品、肖像对象和书中收藏／位置；2a归属不确定，8／16建筑空间不同于绘画 | FM-P01–P16各行，按角色登记候选 |
| FM-S25 | E:L66–81 | 图版17–28；换页及多子项挤在一行；17a机构名中的104为装订页号；21组扫描136 | FM-P17a–P28b，收藏者不等于赞助人 |
| FM-S26 | E:L82–111 | 图版29–40；29复制许可、35a基金购买、33a旧位置；作品局部不自动另造独立原作 | FM-P29–P40b；所有权／许可／捐赠分开 |
| FM-S27 | E:L112–119 | 图版41–44；建筑立面、纪念物、城市拟人、家族寓意分别表达 | FM-P41a–P44；Venice寓意不能自动当共和国行为 |
| FM-S28 | E:L120–139 | 图版45–60；原作与刻印者、肖像对象、出版社及承载书分开；52b多人共同创作 | FM-P45–P60；合作候选不能扩成私人友谊 |
| FM-S29 | E:L140–160 | 图版61–68；同题两实物、地景／规划方案、旧藏、联合漫画、三幅未具名肖像及刻版者 | FM-P61a–P68b；68a保持三件作品群待拆 |
| FM-S30 | E:L161–172 | 供片名单逐项与图版号对应，机构／摄影者／商号需判类；供片不等于创作或拥有原作 | FM-H01–H26与对应图版；不把所有博物馆逐一套默认规则 |
| FM-S31 | E:L173–177 | 导言开始；Honour评论“厌恶新古典主义”，Haskell承认态度变化但另问史观是否失真 | FM-E048；同一批评不是Haskell自述原话 |
| FM-S32 | E:L178–183 | Waterhouse先反驳Wittkower的威尼斯中心判断，再批评Haskell；画家迁居／拒居是所引例据，竞争动机是解释 | FM-E039、049–052及画家组；保留三层发言 |
| FM-S33 | E:L184 | Haskell回应：无重要委托或仅旅游是两个备选范围，不可任选套到Crespi／Solimena；Conca1707及7年后首项公共委托；Tiepolo威尼托活动 | FM-E050–058；优劣判断不是客观质量指标 |
| FM-S34 | E:L185–188 | 引Conforti评Innocent XI削减艺术支出、Pastor评Clement XI不任人唯亲；作者从此论赞助衰落；脚注各归引用句 | FM-E059–063、089–090、093及书评083；“无nepotism→无委托”不是已证关系 |
| FM-S35 | E:L189–192 | xviii页眉误识；接“centre of art patronage”；Poerson1708来信将战争、外国人减少与报酬相连，Mgr收信人未明 | FM-E064–067；法国学院在Rome，译文不添收信人 |
| FM-S36 | E:L193–195 | Clement XI让S. Clemente重新装饰，列七位艺术家；“we can assume”是Haskell推定聘到最好者，不是合同证明 | FM-E060、068–074；项目候选可存，不能凭名单给每人分配具体画作 |
| FM-S37 | E:L196–198 | Waterhouse和已故Clark显示Rome有优秀画家；Haskell仍坚持绘画相对地位下降并限定不适于建筑雕塑；脚注Montaiglon／Gilmartin | FM-E039、067、075、076、091–092；本项目不裁决双方史学优劣 |

## 3. 实体候选结果

见[实体候选表](entity-candidates.md)：正文提及、图版子项及供片者分字段保存。候选编号是本任务内原文提及锚点，不是已分配的正式KU ID；原文同名提及可复用一条候选或保留待合并，最终唯一实体数量待下一阶段语义查重。页行位置与本文件映射共同构成原句引用，不用译名代替原名。

| 候选记录范围 | 当前条目 | 数量含义 |
|---|---:|---|
| 正文提及 FM-E | 94 | 包含别名复现、属性和匿名群体待决，不是94个已确认实体 |
| 地理提及 FM-L | 13 | 图版中的其他地名另随FM-P逐项保留 |
| 图版子项 FM-P | 108 | 覆盖1–68全部编号及a／b／c／d；每项保留多个角色候选，68a仍是三幅未具名作品群 |
| 图片来源 FM-H | 26 | 25个具名提供者提及及1条匿名默认规则，不是26个确定机构 |

这些不同粒度的记录不相加报告为唯一实体总数。每项均保存来源定位、类型／角色与后续处置。

## 4. 关系候选、指代与证据

以下均为待关系阶段裁决的候选，不使用正式边的completed／confirmed状态。原句短引便于识别，支持范围为完整指定行段。每个候选携带证据页码，引用上表载体指纹；引述者与历史行动者分开。

| 锚点 | 端点提及与候选关系 | 原句／来源定位 | 限定与交接 |
|---|---|---|---|
| FM-R01 | FM-E001撰写FM-E002；E004出版、E005版权 | “FRANCIS HASKELL”；“Copyright © 1980 by Yale University.” A:L3–17，PDF1–2 | Press与University不是同一角色；1980版与2006印次分开 |
| FM-R02 | FM-E002献给FM-E003 Larissa | “For Larissa and my friends in Italy” A:L15，PDF2 | 献辞不证明配偶；朋友群匿名 |
| FM-R03 | FM-E001修订本书、提及FM-E007 DBI | “three separate ways”；“Nor have I made references” B:L5–7，PDF3 | DBI被推荐使用，但不是正式书目已经引用；不能生成正文引用肯定边 |
| FM-R04 | E008／009支持初版，E010提出新版 | “worked together on the first handsome edition”；“proposing a new edition” B:L11–12，vi | 项目协助关系，不全当学术共同作者 |
| FM-R05 | E011–013指出E001错误；E014–018协助 | “pointed out to me”；“suggestions in the preparation” B:L12–13，vi | `me`是Haskell；书目／图像／其他帮助的集合不逐人分配具体一项 |
| FM-R06 | E001与E019、E020友谊和咨询 | “two very close friends to whom I turned so often for advice” B:L14–15，vi | 两个别名与首版全称待身份核对；只证写序时已故 |
| FM-R07 | E026协助E001安排图版 | “my friend Dr Enzo Crea ... organise this side of the book” C:L17，viii | friend有明确称谓；本书图像组织，不是作品共同创作 |
| FM-R08 | E027、028支持E001研究 | “library of the Warburg Institute”；“my own College” C:L21–22、27–28，ix | my own College由签名章内映射King's；不推出具体雇佣任职 |
| FM-R09 | E030解决问题；E031读稿；E032编索引；E029印刷 | “the librarian”；“whole book in proof”；“compiling ... Index”；“printers” C:L22，ix | librarian修饰Munby；工作对象是本书 |
| FM-R10 | E033帮助E001使用E034 Correr Library | “facilities for working in the Correr Library” C:L23，ix | 不推Pignatti任图书馆馆长 |
| FM-R11 | E035–038、040协助；E039、041、042读稿；E043启发；E013、044讨论；E045审稿 | “read the typescript”；“first interested me”；“at every stage” C:L23–25，ix | 角色按句法分配；读稿不等于赞同全书观点 |
| FM-R12 | E039评论E002并反驳E049观点 | “refute Rudolf Wittkower's claim”；“Waterhouse commented” E:L178–183＋187，xvii | Haskell转引Waterhouse；批评的两个对象不得合并 |
| FM-R13 | E048评论E002，E001承认旧偏好 | “distaste for Neo-classicism”；“Since then I have overcome” E:L176–177＋187，xvii | 1963评论，时间变化保留 |
| FM-R14 | E050、051、052迁Rome；Piola／Viani／Lazzarini拒居 | “moved to Rome from Naples or Tuscany”；“more likely ... feared competition” E:L181–183，xvii | 源地是并列集合，不能逐人分配；动机为Waterhouse假说 |
| FM-R15 | E056 Conca到Rome并获首项公共委托 | “arrived in 1707 ... seven years” E:L184，xvii | 到达和委托不同事件；作品／委托人未名，1714仅据7年后推算 |
| FM-R16 | Crespi／Solimena与Rome的活动边界；Tiepolo在Veneto创作 | “either failed ... or ... tourists”；“works in the Veneto” E:L184，xvii | 不把前半析取句转成二人都未访Rome |
| FM-R17 | E059 Innocent XI抑制艺术支出 | “keep money from the arts” E:L185＋188，xvii | 引Conforti；本项目未读原文，不推全期无资助 |
| FM-R18 | E060 Clement XI与nepotism | “kept himself free from all nepotism” E:L185＋188，xvii | 引Pastor；否定命题不能生成肯定亲族任用边 |
| FM-R19 | E064 Poerson任E065法国学院主管并撰E066来信 | “director of the French Academy”；“in 1708 ... wrote” E:L191–192＋198，xviii | Mgr未具名；不填写收信人；证据为Montaiglon转引 |
| FM-R20 | E066表述战争—访客—报酬机制 | “empêchent les Etrangers de venir icy” E:L192，xviii | `icy／ce païs-cy`在语境指Rome／当地；观点归信作者，不作为普遍经济规律 |
| FM-R21 | E060委托E069教堂装饰项目于E068；E050、070–074、E080参与 | “had the church ... freshly decorated”；“list of those chosen” E:L193–195＋198，xviii | 原文“十八世纪第二个十年”；七位艺术家分别列候选，不分配具体壁画；“best artists”是作者推测 |
| FM-R22 | E001评价Rome／Venice绘画，E039与E075提供研究 | “Waterhouse himself and the late Anthony Clark”；“quite justified ... painting” E:L196，xviii | 可记论争／引用候选，不生成人物敌对关系 |
| FM-R23 | 两版序言陈述E001选材方法 | “Any attempt to ‘explain’ art in terms of patronage has been deliberately avoided.” C:L14–16，viii | 方法断言；不等同发现层Theme，不否认所有社会联系 |
| FM-R24 | E048评论E002的E083刊于E093；E039与E063、E089与E061、E090与E062、E091与E067、E092与E076的文献责任候选 | “Hugh Honour ... review”；“In an article”；“Apollo, December 1963”；“Conforti”；“Pastor”；“Montaiglon”；“Gilmartin” E:L176、178、187–188、198，xvii–xviii | 单篇书评与期刊分开；缩引仅给责任者线索，须查书目才确定全名、正式题名及作者／编者角色 |
| FM-R25 | E027图书馆属于E094研究院 | “the library of the Warburg Institute” C:L21–22，ix | 跨行修饰，组织与其下属图书馆分开；不推出建筑所有权 |

图版关系逐项附在实体表每个FM-P行，继承**该行独有**页行证据，候选锚点为`FM-R-P<图版子号>-<角色>`：`creator`（表列创作／设计／刻印者）、`subject`（描绘／纪念）、`holder`（书中收藏）、`site`（空间）、`derived`（刻本与原设计／载体文献）。一个单元格多端点按原列顺序加1、2，尚未具名端点保留疑问，不制造KU。

- 2a只记录attributed_to候选，不能用确定created_by。
- 8、16是建筑／内部空间，其设计者关系不能照搬绘画作品created_by；41a为立面构件，41b为纪念物，分别判断。
- 9、28b、55a／b、57a／b、68b分开图像、承载文献／演出和设计／刻印角色；“from”不自动等于二人合作或相识。
- 26b的formerly修饰建筑旧名；33a的formerly是历史位置；65a的formerly是旧藏。61a／61b为同题不同对象，不能合并。
- 29的reproduced by permission只证复制许可；35a的1961与基金购买有关，不是作品年；基金不能当创作者或当然赞助人。
- 52b三名具名共同创作者与65a联合漫画有共同作品证据，可记共同创作候选；不能推出长期合作／友谊。
- 所有馆藏／位置是本印本沿用的记载，未证明2026现藏。图片来源FM-H的关系锚点为`FM-R-H<编号>-<图版子号>`，只记录提供该复制图像；没有给摄影对象独立编号时以本书plate／panel为证据载体，不等同拥有艺术原作。

## 5. 当前结果与下一阶段

摄入与处理阶段已完成本地章前材料的语义解析，实体候选、关系候选及必要校正均已保存。该阶段本身不新增KU、正式边或外部配对。REV-085已接续知识元登记、REV-086已接续初步对齐；实际成稿、复用和待决见[登记映射](../process/knowledge.md#候选登记映射)，不在本文件复制知识阶段统计。

待决集中在：Larissa及匿名对象、Munby／Nicolson别名、Ghezzi／Chiari及缩引身份、来源机构与建筑粒度、图版旧藏与具体版本、68a三件作品拆分、神话角色是否需独立表达。未读引用原件和图版图像按后续事实需要定向补足；本轮不借Wikipedia／Wikidata补造书中提及。
