# 第一章样例：当前知识元与关系结果

更新依据：REV-017（2026-09-09，补足要求及状态澄清；数量沿用 REV-016）。当前登记 **297 个知识元、12 条复杂断言、173 条有出处的有向关系**。这是一份经过类型边界修订及补漏的当前清单，**不是已证明穷尽的全章清单**。第六章、知识涌现和网页继续暂停。

## 本次变化

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

类型契约见 [taxonomy-registry.md](../../01-domain/taxonomy-registry.md)。材料名/颜色概念可为 term；具体颜料批次或施工设备实物、神话图像角色等存在八类不能直接充分表达的边界，已在过程记录单列，未强塞为作品或现实人物，也未为凑类型新增类别。

## 阶段状态

| 阶段 | 当前成果 | 尚存边界 |
|---|---|---|
| 摄入 | 第一章完整 OCR 与 PDF、书名版权页已定位 | 为本章消歧另定向读取同书书目及索引，未展开其他章节 |
| 处理 | OCR L1–980 已逐行语义阅读，正文/脚注/跨页有处置 | 行号覆盖不是对象提取完整性的证明；REV-016 已回查具体遗漏 |
| 知识元 | 297 个可用对象，类型及粒度修订、26 个漏项补入 | 其他短引书目与类型待决对象仍须逐项判断，不能宣称全量穷尽 |
| 对齐 | 第 4 页 Borghese → Scipione；3 组书目补全；地名/政治实体等边界明确 | 第 17 页肖像同一性、其他未明全名和版本不自动解决 |
| 补足 | 已做来源内补漏：同书书目、索引及对象边界纠正；外部补足未开始 | REV-017 要求的逐实体 Wikipedia—Wikidata 双重身份核对及 Getty/适用官方来源补足尚未执行，不记补足阶段完成 |
| 关系 | 173 条逐条附 note、来源文件、行号及印刷页 | 不以同页共现造边，不以消除孤点证明完备 |
| 发现与页面 | 暂不开展 | 没有新增涌现结构、刷新页面或提交推送 |

[摄入处理结果](../../03-processing/patrons-and-painters-chp-1/results/stages.md) · [逐行阅读过程](../../03-processing/patrons-and-painters-chp-1/process/stages.md) · [知识判断与边界修订过程](../../03-processing/patrons-and-painters-chp-1/process/knowledge.md)

## 当前成果统计

当前正文以本章证据为主，记录对象、具体事例、限定条件与来源定位；部分身份定义和历史语境仍较简略。以 Guercino 为例，目前写入 1665 年祭坛画图像与照明问题、1649 年每位主要人物 125 杜卡特的报价及限制，尚未加入经双重核对的外部身份资料。此次只修订规则并澄清状态，未对 297 个对象作外部核验、添加 QID 或提升验证状态。

| 类型 | 数量 |
|---|---:|
| archive | 39 |
| event | 6 |
| institution | 20 |
| person | 124 |
| place | 38 |
| procedure | 10 |
| term | 29 |
| work | 31 |
| **合计** | **297** |

有效对象的唯一登记见 [accepted.yml](../accepted.yml)，断言见 [claim-registry.yml](../quality/claim-registry.yml)，关系原记录在 KU 的 relations，派生索引见 [relation-index.yml](../quality/relation-index.yml)。第六章专属 19 个草稿仍未接收；其中两张文献草稿只机械迁移类型/路径，未进行第六章语义处理。

## 可解决与仍未解决的问题

- **已解决**：同书索引 Domenichino 子条明确第 4 页所述枢机为 Scipione Borghese。原候选卡沿用路径并限定该处身份，不再把整个人物都笼统暂缓。
- **已补足**：Armanni 信集题名/卷数/年份、Bertolotti 缩题、Grassi 1957 论文的刊名及页码，均可由同书书目定向核对。
- **尚未解决**：第 17 页头部肖像端点与具体版本，Giovanni Adamo 等其他身份全名、无题名借阅书的版本、若干缩引文献、原件文本及当今馆藏。
- **类型待决**：具体材料/设备实物与图像角色不能不加说明地套入八类；当前相关文字与图像题材已保留，后续依据实际对象决定是否扩展。
- **沿用的重要纠正**：费率为 Domenichino 130、Lanfranco 100、Guercino 报 125 ducats；萨基家户属于 Antonio 而非 Francesco；《瘟疫》已有稿后商议完成，《春》为另行新委托；稿本争议、逸事与“首次引入”推测不转确定事实。

本次全部 source_backed 仍指 Haskell 本书及定向辅助页的支持；同书书目和索引不是独立外部来源。主 Agent 直接分析及自查，不称独立验收。必要机械检查、迁移映射和类型工具验证见 [系统修订日志](../../06-runtime/governance/system-upgrade-log.md) 的 REV-016。

## 知识元目录

以下只链接唯一当前正文，不复制内容；每张卡保留来源定位及对象边界。

| 类型 | 知识元 |
|---|---|
| archive | [圣路加学院章程（1621 年确认语境）](../units/archives/accademia-statutes-confirmed-1621.md) |
| archive | [《Relatione della città di Roma》（1642）](../units/archives/ameyden-relazione-1642.md) |
| archive | [Armanni《Delle lettere…》信集](../units/archives/armanni-delle-lettere.md) |
| archive | [阿尔曼尼致潘菲利装饰建议信（未注明日期）](../units/archives/armanni-pamfili-letter-undated.md) |
| archive | [Arragona 曼图亚通信（1621-10-09）](../units/archives/arragona-mantua-letter-1621.md) |
| archive | [Baldoini 本府画家任命文字](../units/archives/baldoini-painter-appointment.md) |
| archive | [Bertolotti《Artisti bolognesi…》](../units/archives/bertolotti-artisti-bolognesi.md) |
| archive | [G. L. Bianconi 信（1762-11-22）](../units/archives/bianconi-letter-1762.md) |
| archive | [卡马塞伊《圣塞巴斯蒂安殉难》收据刊录](../units/archives/camassei-sebastian-receipt.md) |
| archive | [卡马塞伊与乌尔班八世合同（1633）](../units/archives/camassei-urban-contract-1633.md) |
| archive | [卡拉瓦乔两幅祭坛画合同（1600）](../units/archives/caravaggio-altarpieces-contract-1600.md) |
| archive | [切利尼自传（本章引用）](../units/archives/cellini-autobiography.md) |
| archive | [Coke 致 Arundell 信（1620-10-08）](../units/archives/coke-arundell-letter-1620.md) |
| archive | [Colnaghi 图录（1961 年 5–6 月，第 2 号作品）](../units/archives/colnaghi-catalogue-1961.md) |
| archive | [de Rosis 致 Ruffo 信（1663-09-22）](../units/archives/de-rosis-ruffo-letter-1663.md) |
| archive | [费里致鲁福信（1672-09-19）](../units/archives/ferri-ruffo-letter-1672.md) |
| archive | [加瓦塞蒂皮亚琴察壁画委托条款（1624）](../units/archives/gavasetti-piacenza-contract-1624.md) |
| archive | [Gessi 致 Leopardi 信（1647-07-10）](../units/archives/gessi-leopardi-letter-1647.md) |
| archive | [Onorato Gini 关于科尔托纳选题的信（1666）](../units/archives/gini-cortona-letter-1666.md) |
| archive | [Giovanni Adamo 致 Piola 委托信（1690-02-03）](../units/archives/giovanni-adamo-piola-letter-1690.md) |
| archive | [Grassi 关于多利亚潘菲利画廊草稿的论文（1957）](../units/archives/grassi-cortona-bozzetti-1957.md) |
| archive | [圭尔奇诺致鲁福信（1649-09-25）](../units/archives/guercino-ruffo-letter-1649.md) |
| archive | [兰弗兰科致巴贝里尼信（1640-07-14）](../units/archives/lanfranco-barberini-letter-1640.md) |
| archive | [《L’Hoggidi》（1627）](../units/archives/lhoggidi-1627.md) |
| archive | [明尼蒂在奥古斯塔的委托条款刊录（1617）](../units/archives/minnitti-augusta-terms-1617.md) |
| archive | [莫拉为四元素装饰借阅的神谱书（题名未明）](../units/archives/mola-borrowed-genealogy-gods.md) |
| archive | [莫拉借阅的带注释 Virgil 文本（版本未明）](../units/archives/mola-borrowed-virgil-commentary.md) |
| archive | [莫拉与潘菲利 Valmontone 工程合同条款（1657）](../units/archives/mola-pamfili-contract-1657.md) |
| archive | [Negri 致 S. Tommaso 信（1676-12-24）](../units/archives/negri-san-tommaso-letter-1676.md) |
| archive | [Novetti 致 Ruffo 信（1670-03-22）](../units/archives/novetti-ruffo-letter-1670.md) |
| archive | [帕斯科利未刊《特雷维萨尼传》（MS.1383）](../units/archives/pascoli-trevisani-life-ms1383.md) |
| archive | [《赞助人与画家》（Patrons and Painters）](../units/archives/patrons-and-painters.md) |
| archive | [Quarismini 致 Carrara 信（1696-07-11）](../units/archives/quarisimini-carrara-letter-1696.md) |
| archive | [里奇《施洗者约翰斩首》委托条款（1682）](../units/archives/ricci-bologna-terms-1682.md) |
| archive | [罗萨致鲁福信（1666-04-01）](../units/archives/rosa-ruffo-letter-1666.md) |
| archive | [萨尔维亚蒂致美第奇信（1662-07-22）](../units/archives/salviati-medici-letter-1662.md) |
| archive | [萨维尼在古比奥的委托条款刊录（1608）](../units/archives/savini-gubbio-terms-1608.md) |
| archive | [Fulvio Testi 致 Francesco Fontana 信（贝尔尼尼报酬记载）](../units/archives/testi-fontana-bernini-letter.md) |
| archive | [瓦萨利关于莫拉与潘菲利服务争议的证词记录](../units/archives/vasalli-testimony-mola-pamfili.md) |
| event | [圣路加学院 1633 年征税及公共委托措施](../units/events/accademia-tax-privilege-1633.md) |
| event | [圭尔奇诺西西里祭坛画图像询问（1665）](../units/events/guercino-iconography-query-1665.md) |
| event | [兰弗兰科申请《教皇利奥与阿提拉》委托（1640）](../units/events/lanfranco-leo-attila-request-1640.md) |
| event | [萨基在巴贝里尼家户内晋级（1640）](../units/events/sacchi-household-promotion-1640.md) |
| event | [画家帮成立（Schildersbent, 1623）](../units/events/schildersbent-formation-1623.md) |
| event | [查理五世授提香荣衔（1533）](../units/events/titian-honours-1533.md) |
| institution | [圣路加学院（Accademia di S. Luca）](../units/institutions/accademia-di-san-luca.md) |
| institution | [阿尔多布兰迪尼家族（Aldobrandini）](../units/institutions/aldobrandini-family.md) |
| institution | [宗座财务院（Apostolic Chamber）](../units/institutions/apostolic-chamber.md) |
| institution | [阿尔卡迪亚学会（Society of Arcadia）](../units/institutions/arcadia.md) |
| institution | [巴贝里尼家族及家户（Barberini）](../units/institutions/barberini-household.md) |
| institution | [巴尔纳伯会（Barnabites）](../units/institutions/barnabites.md) |
| institution | [奥古斯塔图书馆（Biblioteca Augusta）](../units/institutions/biblioteca-augusta.md) |
| institution | [卡萨纳滕塞图书馆（Biblioteca Casanatense）](../units/institutions/biblioteca-casanatense.md) |
| institution | [博尔盖塞家族（Borghese）](../units/institutions/borghese-family.md) |
| institution | [嘉布遣会（Capuchins）](../units/institutions/capuchins.md) |
| institution | [Colnaghi’s 画廊](../units/institutions/colnaghi.md) |
| institution | [Bologna 圣若翰斩首善会](../units/institutions/confraternita-san-giovanni-battista-decollato-bologna.md) |
| institution | [圣彼得营造管理机构（Fabbrica di S. Pietro）](../units/institutions/fabbrica-di-san-pietro.md) |
| institution | [耶稣会（Jesuits）](../units/institutions/jesuits.md) |
| institution | [奥拉托利会（Oratorians）](../units/institutions/oratorians.md) |
| institution | [佩雷蒂家族（Peretti）](../units/institutions/peretti-family.md) |
| institution | [梵蒂冈绘画馆（Pinacoteca Vaticana）](../units/institutions/pinacoteca-vaticana.md) |
| institution | [画家帮（Schildersbent）](../units/institutions/schildersbent.md) |
| institution | [戴蒂尼会（Theatines）](../units/institutions/theatines.md) |
| institution | [维多利亚与阿尔伯特博物馆（Victoria and Albert Museum）](../units/institutions/victoria-and-albert-museum.md) |
| person | [兰切洛蒂神父（Abate Lancellotti）](../units/persons/abate-lancellotti.md) |
| person | [亚历山德罗·佩雷蒂—蒙塔尔托（Alessandro Peretti-Montalto）](../units/persons/alessandro-peretti-montalto.md) |
| person | [亚历山德罗·瓦萨利（Alessandro Vasalli）](../units/persons/alessandro-vasalli.md) |
| person | [Ameyden（1642 年罗马手稿作者）](../units/persons/ameyden.md) |
| person | [安德烈亚·卡马塞伊（Andrea Camassei）](../units/persons/andrea-camassei.md) |
| person | [安德烈亚·波佐（Andrea Pozzo）](../units/persons/andrea-pozzo.md) |
| person | [安德烈亚·普罗卡奇尼（Andrea Procaccini）](../units/persons/andrea-procaccini.md) |
| person | [安德烈亚·萨基（Andrea Sacchi）](../units/persons/andrea-sacchi.md) |
| person | [安尼巴莱·卡拉奇（Annibale Carracci）](../units/persons/annibale-carracci.md) |
| person | [安尼巴莱·拉帕雷利（Annibale Laparelli）](../units/persons/annibale-laparelli.md) |
| person | [安东尼奥·巴贝里尼（Antonio Barberini）](../units/persons/antonio-barberini.md) |
| person | [安东尼奥·鲁福（Don Antonio Ruffo）](../units/persons/antonio-ruffo.md) |
| person | [阿尔泰米西娅·真蒂莱斯基（Artemisia Gentileschi）](../units/persons/artemisia-gentileschi.md) |
| person | [贝内代托·卢蒂（Benedetto Luti）](../units/persons/benedetto-luti.md) |
| person | [本韦努托·切利尼（Benvenuto Cellini）](../units/persons/benvenuto-cellini.md) |
| person | [Berlingero Gessi](../units/persons/berlingete-gessi.md) |
| person | [Bonifazio Gozadini](../units/persons/bonifazio-gozadini.md) |
| person | [卡米洛·加瓦塞蒂（Camillo Gavasetti）](../units/persons/camillo-gavasetti.md) |
| person | [卡米洛·潘菲利（Camillo Pamfili）](../units/persons/camillo-pamfili.md) |
| person | [卡拉瓦乔（Caravaggio）](../units/persons/caravaggio.md) |
| person | [希皮奥内·博尔盖塞枢机（Cardinal Scipione Borghese）](../units/persons/cardinal-borghese-ch1.md) |
| person | [Pio 枢机（博纳蒂的保护人）](../units/persons/cardinal-pio-bonati.md) |
| person | [Rospigliosi 枢机（吉米尼亚尼的保护人）](../units/persons/cardinal-rospigliosi-gimignani.md) |
| person | [马尔瓦西亚（Malvasia）](../units/persons/carlo-cesare-malvasia.md) |
| person | [卡洛·马拉塔（Carlo Maratta）](../units/persons/carlo-maratta.md) |
| person | [Carlo Quarismini（1696 年通信者）](../units/persons/carlo-quarisimini-ch1.md) |
| person | [里多尔菲（Ridolfi）](../units/persons/carlo-ridolfi.md) |
| person | [Don Cesare Leopardi d’Osimo](../units/persons/cesare-leopardi-dosimo.md) |
| person | [查理五世（Charles V）](../units/persons/charles-v.md) |
| person | [瑞典女王克里斯蒂娜（Christina of Sweden）](../units/persons/christina-of-sweden.md) |
| person | [奇罗·费里（Ciro Ferri）](../units/persons/ciro-ferri.md) |
| person | [克劳德·洛兰（Claude Lorrain）](../units/persons/claude-lorrain.md) |
| person | [克雷芒十一世（Clement XI）](../units/persons/clement-xi.md) |
| person | [科雷乔（Correggio）](../units/persons/correggio.md) |
| person | [丹尼斯·马洪（Denis Mahon）](../units/persons/denis-mahon.md) |
| person | [多梅尼基诺（Domenichino）](../units/persons/domenichino.md) |
| person | [布拉恰诺公爵（穆利耶尔的雇主）](../units/persons/duke-bracciano-mulier.md) |
| person | [曼图亚公爵（雷尼 1617 年委托语境）](../units/persons/duke-mantua-reni-1617.md) |
| person | [帕尔马公爵（盖齐授衔语境）](../units/persons/duke-parma-ghezzi.md) |
| person | [Fabrizio Arragona](../units/persons/fabrizio-arragona.md) |
| person | [法布里齐奥·瓦尔瓜尔内拉（Fabrizio Valguarnera）](../units/persons/fabrizio-valguarnera.md) |
| person | [费德里戈·祖卡里（Federigo Zuccari）](../units/persons/federigo-zuccari.md) |
| person | [巴尔迪努奇（Baldinucci）](../units/persons/filippo-baldinucci.md) |
| person | [菲利波·劳里（Filippo Lauri）](../units/persons/filippo-lauri.md) |
| person | [弗拉维奥·基吉（Flavio Chigi）](../units/persons/flavio-chigi.md) |
| person | [弗朗切斯科·阿尔巴尼（Francesco Albani）](../units/persons/francesco-albani.md) |
| person | [弗朗切斯科·巴贝里尼（Francesco Barberini）](../units/persons/francesco-barberini.md) |
| person | [Francesco Fontana 伯爵](../units/persons/francesco-fontana.md) |
| person | [Francesco Novetti](../units/persons/francesco-novetti.md) |
| person | [弗朗切斯科·特雷维萨尼（Francesco Trevisani）](../units/persons/francesco-trevisani.md) |
| person | [皇帝腓特烈三世（Frederick III）](../units/persons/frederick-iii.md) |
| person | [富尔维奥·泰斯蒂（Fulvio Testi）](../units/persons/fulvio-testi.md) |
| person | [加斯帕尔·迪盖（Gaspard Dughet）](../units/persons/gaspard-dughet.md) |
| person | [真蒂莱·贝利尼（Gentile Bellini）](../units/persons/gentile-bellini.md) |
| person | [贾钦托·布兰迪（Giacinto Brandi）](../units/persons/giacinto-brandi.md) |
| person | [乔万巴蒂斯塔·帕塞里（Giambattista Passeri）](../units/persons/giambattista-passeri.md) |
| person | [Giammaria Morandi](../units/persons/giammaria-morandi.md) |
| person | [吉安·洛伦佐·贝尔尼尼（Gian Lorenzo Bernini）](../units/persons/gian-lorenzo-bernini.md) |
| person | [Gianandrea Carlone](../units/persons/gianandrea-carlone.md) |
| person | [Gio. Gasparo Baldoini](../units/persons/gio-gasparo-baldoini.md) |
| person | [瓦萨里（Vasari）](../units/persons/giorgio-vasari.md) |
| person | [乔万·巴蒂斯塔·盖乌利（Giovan Battista Gaulli）](../units/persons/giovan-battista-gaulli.md) |
| person | [Giovanni Adamo（皮奥拉的委托人）](../units/persons/giovanni-adamo-piola.md) |
| person | [乔万尼·博纳蒂（Giovanni Bonati）](../units/persons/giovanni-bonati.md) |
| person | [乔万尼·兰弗兰科（Giovanni Lanfranco）](../units/persons/giovanni-lanfranco.md) |
| person | [乔万尼·奥达齐（Giovanni Odazzi）](../units/persons/giovanni-odazzi.md) |
| person | [Giovanni Perugini](../units/persons/giovanni-perugini.md) |
| person | [乔万尼·彼得罗·贝洛里（Giovanni Pietro Bellori）](../units/persons/giovanni-pietro-bellori.md) |
| person | [朱利奥·曼奇尼（Giulio Mancini）](../units/persons/giulio-mancini.md) |
| person | [Giuseppe de Rosis](../units/persons/giuseppe-de-rosis.md) |
| person | [朱塞佩·盖齐（Giuseppe Ghezzi）](../units/persons/giuseppe-ghezzi.md) |
| person | [G. L. Bianconi](../units/persons/gl-bianconi.md) |
| person | [格列高利十五世（Gregory XV）](../units/persons/gregory-xv.md) |
| person | [圭尔奇诺（Guercino）](../units/persons/guercino.md) |
| person | [古列尔莫·科尔泰塞（Guglielmo Cortese）](../units/persons/guglielmo-cortese.md) |
| person | [圭多·雷尼（Guido Reni）](../units/persons/guido-reni.md) |
| person | [英诺森十世（Innocent X）](../units/persons/innocent-x.md) |
| person | [英诺森十三世（Innocent XIII）](../units/persons/innocent-xiii.md) |
| person | [雅各布·萨尔维亚蒂（Jacopo Salviati）](../units/persons/jacopo-salviati.md) |
| person | [利奥十世（Leo X）](../units/persons/leo-x.md) |
| person | [莱奥波尔多·德·美第奇（Leopoldo de’ Medici）](../units/persons/leopoldo-de-medici.md) |
| person | [洛多维科·吉米尼亚尼（Lodovico Gimignani）](../units/persons/lodovico-gimignani.md) |
| person | [阿伦德尔勋爵（Lord Arundell，本章收信人）](../units/persons/lord-arundell-coke-correspondent.md) |
| person | [卢卡·焦尔达诺（Luca Giordano）](../units/persons/luca-giordano.md) |
| person | [卢多维科·卢多维西（Ludovico Ludovisi）](../units/persons/ludovico-ludovisi.md) |
| person | [马尔切洛·萨凯蒂（Marcello Sacchetti）](../units/persons/marcello-sacchetti.md) |
| person | [Costaguti 侯爵（卡尔洛内婚姻事例语境）](../units/persons/marchese-costaguti-household.md) |
| person | [Del Carpio 侯爵（西班牙驻罗马大使）](../units/persons/marchese-del-carpio.md) |
| person | [Giustiniani 侯爵（卡拉瓦乔收藏者）](../units/persons/marchese-giustiniani-ch1.md) |
| person | [Pallavicini 侯爵（皮奥拉的罗马保护人）](../units/persons/marchese-pallavicini-piola.md) |
| person | [S. Tommaso 侯爵（内格里的收信人）](../units/persons/marchese-san-tommaso-negri.md) |
| person | [马里奥·德·菲奥里（Mario de’ Fiori）](../units/persons/mario-de-fiori.md) |
| person | [马里奥·明尼蒂（Mario Minnitti）](../units/persons/mario-minnitti.md) |
| person | [马蒂亚·普雷蒂（Mattia Preti）](../units/persons/mattia-preti.md) |
| person | [毛里齐奥·迪·萨伏依（Maurizio di Savoia）](../units/persons/maurizio-di-savoia.md) |
| person | [米开朗基罗·切尔阔齐（Michelangelo Cerquozzi）](../units/persons/michelangelo-cerquozzi.md) |
| person | [米开朗基罗（Michelangelo）](../units/persons/michelangelo.md) |
| person | [Mr Coke（1620 年罗马通信者）](../units/persons/mr-coke-rome-correspondent.md) |
| person | [尼古拉·普桑（Nicolas Poussin）](../units/persons/nicolas-poussin.md) |
| person | [奥诺拉托·吉尼（Onorato Gini）](../units/persons/onorato-gini.md) |
| person | [保罗·吉罗拉莫·皮奥拉（Paolo Girolamo Piola）](../units/persons/paolo-girolamo-piola.md) |
| person | [保罗·圭多蒂（Paolo Guidotti）](../units/persons/paolo-guidotti.md) |
| person | [保罗·内格里（Paolo Negri）](../units/persons/paolo-negri.md) |
| person | [帕斯科利（Pascoli）](../units/persons/pascoli.md) |
| person | [保禄五世（Paul V）](../units/persons/paul-v.md) |
| person | [鲁本斯（Rubens）](../units/persons/peter-paul-rubens.md) |
| person | [皮耶尔·弗朗切斯科·莫拉（Pier Francesco Mola）](../units/persons/pier-francesco-mola.md) |
| person | [彼得·范拉尔（Pieter van Laer）](../units/persons/pieter-van-laer.md) |
| person | [皮耶特罗·达·科尔托纳（Pietro da Cortona）](../units/persons/pietro-da-cortona.md) |
| person | [皮耶特罗·穆利耶尔（Pietro Mulier）](../units/persons/pietro-mulier.md) |
| person | [Ottoboni 枢机（特雷维萨尼的保护人）](../units/persons/pietro-ottoboni.md) |
| person | [拉斐尔（Raphael）](../units/persons/raphael.md) |
| person | [伦勃朗（Rembrandt）](../units/persons/rembrandt.md) |
| person | [萨尔瓦多·罗萨（Salvator Rosa）](../units/persons/salvator-rosa.md) |
| person | [萨韦里奥·萨维尼（Saverio Savini）](../units/persons/saverio-savini.md) |
| person | [塞巴斯蒂亚诺·里奇（Sebastiano Ricci）](../units/persons/sebastiano-ricci.md) |
| person | [西斯笃五世（Sixtus V）](../units/persons/sixtus-v.md) |
| person | [托马斯·贝克（Thomas Baker）](../units/persons/thomas-baker.md) |
| person | [提香（Titian）](../units/persons/titian.md) |
| person | [乌尔班八世（Urban VIII）](../units/persons/urbano-viii.md) |
| person | [瓦朗坦（Valentin）](../units/persons/valentin.md) |
| person | [Ventura Carrara 伯爵](../units/persons/ventura-carrara.md) |
| person | [Vincenzo Armanni（致卡米洛信的作者）](../units/persons/vincenzo-armanni-ch1.md) |
| person | [维吉尔（Virgil）](../units/persons/virgil.md) |
| place | [奥古斯塔（Augusta，Sicily）](../units/places/augusta-sicily.md) |
| place | [博洛尼亚（Bologna）](../units/places/bologna.md) |
| place | [罗马嘉布遣会教堂（Capuchin church）](../units/places/capuchin-church-rome.md) |
| place | [Chiesa de’ Servi（Bologna）](../units/places/chiesa-de-servi-bologna.md) |
| place | [新教堂（Chiesa Nuova，Rome）](../units/places/chiesa-nuova.md) |
| place | [科尔托纳（Cortona）](../units/places/cortona.md) |
| place | [佛罗伦萨（Florence）](../units/places/florence.md) |
| place | [热那亚（Genoa）](../units/places/genoa.md) |
| place | [耶稣堂（Gesù，Rome）](../units/places/gesu-rome.md) |
| place | [古比奥（Gubbio）](../units/places/gubbio.md) |
| place | [意大利（Italy）](../units/places/italy.md) |
| place | [伦敦（London）](../units/places/london.md) |
| place | [米兰（Milan）](../units/places/milan.md) |
| place | [摩德纳（Modena）](../units/places/modena.md) |
| place | [那不勒斯主教座堂（Naples Cathedral）](../units/places/naples-cathedral.md) |
| place | [那不勒斯（Naples）](../units/places/naples.md) |
| place | [巴贝里尼宫（Barberini 宫殿语境）](../units/places/palazzo-barberini.md) |
| place | [多利亚潘菲利宫（Palazzo Doria-Pamfili）](../units/places/palazzo-doria-pamfili.md) |
| place | [潘菲利在 Valmontone 的乡间宅邸](../units/places/pamfili-country-house-valmontone.md) |
| place | [帕尔马（Parma）](../units/places/parma.md) |
| place | [佩鲁贾（Perugia）](../units/places/perugia.md) |
| place | [皮亚琴察（Piacenza）](../units/places/piacenza.md) |
| place | [西班牙广场（Piazza di Spagna）](../units/places/piazza-di-spagna.md) |
| place | [纳沃纳广场（Piazza Navona）](../units/places/piazza-navona.md) |
| place | [罗马（Rome）](../units/places/rome.md) |
| place | [S. Sebastiano（Palatine）](../units/places/san-sebastiano-palatine.md) |
| place | [S. Agnese（Piazza Navona）](../units/places/sant-agnese-piazza-navona.md) |
| place | [谷地圣安德烈堂（S. Andrea della Valle）](../units/places/sant-andrea-della-valle.md) |
| place | [S. Antonino（Piacenza）](../units/places/sant-antonino-piacenza.md) |
| place | [圣母大殿（S. Maria Maggiore）](../units/places/santa-maria-maggiore.md) |
| place | [米涅瓦圣母堂（S. Maria sopra Minerva）](../units/places/santa-maria-sopra-minerva.md) |
| place | [西西里（Sicily）](../units/places/sicily.md) |
| place | [西班牙（Spain）](../units/places/spain.md) |
| place | [圣彼得大殿（St Peter’s）](../units/places/st-peters-basilica.md) |
| place | [都灵（Turin）](../units/places/turin.md) |
| place | [瓦尔蒙托内（Valmontone）](../units/places/valmontone.md) |
| place | [威尼斯（Venice）](../units/places/venice.md) |
| place | [玛古塔街（Via Margutta）](../units/places/via-margutta.md) |
| procedure | [艺术家荣衔与职位授予](../units/procedures/artist-title-conferral.md) |
| procedure | [委托合同订立惯例（commission contracting）](../units/procedures/commission-contracting.md) |
| procedure | [定金、进度款与结算](../units/procedures/commission-payment.md) |
| procedure | [展览售画与自我宣传](../units/procedures/exhibition-self-promotion.md) |
| procedure | [题材与图像志协商](../units/procedures/iconographic-consultation.md) |
| procedure | [预备稿提交与批准](../units/procedures/modello-approval.md) |
| procedure | [赞助人资助学习旅行](../units/procedures/patron-funded-study-travel.md) |
| procedure | [保护与职业引介程序](../units/procedures/patronage-introduction.md) |
| procedure | [按主要人物数量计价](../units/procedures/per-figure-pricing.md) |
| procedure | [工作室存画议价与完成](../units/procedures/studio-stock-sale.md) |
| term | [祭坛画（altarpiece）](../units/terms/altarpiece.md) |
| term | [画商（art dealer）](../units/terms/art-dealer.md) |
| term | [创作独立（artistic independence）](../units/terms/artistic-independence.md) |
| term | [艺术家气质（artistic temperament）](../units/terms/artistic-temperament.md) |
| term | [同巢之鸟（bentveughels）](../units/terms/bentveughels.md) |
| term | [艺术家“波希米亚”群体](../units/terms/bohemian-artists.md) |
| term | [草稿（bozzetto）](../units/terms/bozzetto.md) |
| term | [定金（caparra）](../units/terms/caparra.md) |
| term | [基督骑士荣衔（Cavaliere dell’abito di Cristo）](../units/terms/cavaliere-abito-cristo.md) |
| term | [行宫伯爵（Count Palatine）](../units/terms/count-palatine.md) |
| term | [祈祷用图像（devotional picture）](../units/terms/devotional-picture.md) |
| term | [鉴赏爱好者（dilettante）](../units/terms/dilettante.md) |
| term | [家户（famiglia）](../units/terms/famiglia.md) |
| term | [壁画（fresco）](../units/terms/fresco.md) |
| term | [可移动画廊画（gallery picture）](../units/terms/gallery-picture.md) |
| term | [天才观（genius）](../units/terms/genius.md) |
| term | [荣誉侍从（gentiluomo d’onore）](../units/terms/gentiluomo-onore.md) |
| term | [历史画（history painting）](../units/terms/history-painting.md) |
| term | [圣年（Holy Year）](../units/terms/holy-year.md) |
| term | [灵感与热情（inspiration / entusiasmo）](../units/terms/inspiration.md) |
| term | [预备油画稿（modello）](../units/terms/modello.md) |
| term | [教皇亲族任用（nepotism）](../units/terms/nepotism.md) |
| term | [本府画家（nostro pittore）](../units/terms/nostro-pittore.md) |
| term | [成对绘画（pictures in pairs）](../units/terms/pendant-pictures.md) |
| term | [柏拉图主义（Platonism）](../units/terms/platonism.md) |
| term | [自画像（self-portrait）](../units/terms/self-portrait.md) |
| term | [专属服务（servitù particolare）](../units/terms/servitu-particolare.md) |
| term | [领衔教堂（titular church）](../units/terms/titular-church.md) |
| term | [群青（ultramarine / oltremare）](../units/terms/ultramarine.md) |
| work | [阿尔巴尼博洛尼亚塞尔维教堂祭坛画（1639）](../units/works/albani-servi-altarpiece-1639.md) |
| work | [巴贝里尼大厅所谓 bozzetto（归属有争议）](../units/works/barberini-salone-bozzetto-disputed.md) |
| work | [贝尔尼尼的博尔盖塞枢机肖像头部](../units/works/bernini-cardinal-borghese-head.md) |
| work | [贝尔尼尼《大卫》中的自我形象](../units/works/bernini-david.md) |
| work | [贝尔尼尼的托马斯·贝克肖像胸像](../units/works/bernini-thomas-baker-bust.md) |
| work | [卡马塞伊《圣塞巴斯蒂安殉难》祭坛画](../units/works/camassei-martyrdom-saint-sebastian.md) |
| work | [卡马塞伊《圣彼得与圣保罗在马默蒂诺监狱施洗》稿](../units/works/camassei-peter-paul-mamertine-modello.md) |
| work | [卡拉瓦乔《圣保罗归化》委托](../units/works/caravaggio-conversion-saint-paul.md) |
| work | [朱斯蒂尼亚尼购藏的卡拉瓦乔退画](../units/works/caravaggio-giustiniani-rejected-altarpiece.md) |
| work | [卡拉瓦乔《圣彼得殉难》委托](../units/works/caravaggio-martyrdom-saint-peter.md) |
| work | [1635 年演出的喜剧（题名未明）](../units/works/comedy-performed-1635.md) |
| work | [归于科尔托纳的多里亚—潘菲利画廊稿组（有争议）](../units/works/cortona-doria-pamfili-modelli-disputed.md) |
| work | [费里为拉帕雷利所作科尔托纳祭坛画](../units/works/ferri-laparelli-altarpiece.md) |
| work | [费里圣阿涅塞穹顶壁画工程](../units/works/ferri-sant-agnese-cupola.md) |
| work | [费里圣阿涅塞穹顶彩色稿](../units/works/ferri-sant-agnese-modello.md) |
| work | [盖乌利耶稣堂拱顶壁画工程](../units/works/gaulli-gesu-vaults.md) |
| work | [加瓦塞蒂圣安东尼诺堂壁画](../units/works/gavasetti-sant-antonino-frescoes.md) |
| work | [圭尔奇诺 1665 年西西里祭坛画委托对象](../units/works/guercino-sicilian-altarpiece-1665.md) |
| work | [兰弗兰科《受难》工作室画稿](../units/works/lanfranco-crucifixion-stock.md) |
| work | [兰弗兰科《抹大拉》工作室画稿](../units/works/lanfranco-magdalene-stock.md) |
| work | [莫拉瓦尔蒙托内《空气》构图方案](../units/works/mola-air-valmontone.md) |
| work | [莫拉的瓦尔蒙托内《四元素》壁画方案](../units/works/mola-four-elements-valmontone.md) |
| work | [《阿什杜德的瘟疫》（The Plague at Ashdod）](../units/works/plague-at-ashdod-1631.md) |
| work | [普桑《屠杀婴孩》（本章提及）](../units/works/poussin-massacre-innocents.md) |
| work | [普桑为瓦尔瓜尔内拉新订的《春》](../units/works/poussin-spring-valguarnera.md) |
| work | [雷尼《正义拥抱和平》委托（1617）](../units/works/reni-justice-embracing-peace.md) |
| work | [雷尼《屠杀婴孩》（本章提及）](../units/works/reni-massacre-innocents.md) |
| work | [里奇 1682 年《施洗者约翰斩首》委托](../units/works/ricci-beheading-john-baptist-1682.md) |
| work | [鲁本斯新教堂祭坛画委托（1606）](../units/works/rubens-chiesa-nuova-altarpiece-1606.md) |
| work | [萨基罗马嘉布遣会教堂祭坛稿](../units/works/sacchi-capuchin-altarpiece-modello.md) |
| work | [Valentin 风俗画委托（题名未明）](../units/works/valentin-genre-commission.md) |

## 关键内容双语状态（REV-018）

标题与描述中英文对照规则已生效；[那不勒斯](../units/places/naples.md)已保留双语 title、补入 name_en，并完成中文/英文描述对应。其他条目尚未全量改写，不能据此声明 297 个 KU 已双语完成。原有计数、关系及来源支持状态不变，外部补足仍未开始。

## 三部分结构状态（REV-019、020）

现行知识元结构为统一元数据、按类型的内容、关系与证据。[圭尔奇诺](../units/persons/guercino.md)已完成本章证据范围内的结构样例，双语描述配合属性/活动/作品/评价/研究文献记录，缺证项目明示待补。全名与生平仍未外部核验。其余 KU 未全量调整；当前 297 KU、12 条断言和 173 条关系计数不变。
