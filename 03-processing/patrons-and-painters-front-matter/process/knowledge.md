# 章前材料：知识元登记与对齐过程

task-id：`patrons-and-painters-front-matter`；REV-085–087。前置输入为[摄入与处理定稿](../results/stages.md)及[实体候选](../results/entity-candidates.md)。前半部分保留REV-085登记判断与写回历史；候选映射维护当前去向。外部核对和改变判断的依据见[REV-086](#初步对齐rev-086)及[REV-087](#图版作者与版本对齐rev-087)，当前状态见04任务结果。

## 判断与范围

- 对照有效登记的418个KU及未接收旧卡，逐项判断人物、作品、机构及空间。相同作者和上下文可支持复用；同题、同姓、爵号或同一建筑中的作品不能单独证明同一性。
- 书目仅定向读取`21_CHP-21Bibliography.md` L368–369、527–528、834–835、934–935、1233–1234，分别辨认Conforti、Gilmartin、Montaiglon、Pastor及Waterhouse缩引。索引仅读取相关查重条目；实际纳入初稿的是`22_CHP-22Index.md` L2415、3414。它们是同书内部身份／书目线索，不是独立外部核验，更不是全文已读。
- Conforti与Gilmartin的原题和刊期可以据书目保存；Pastor书目列意大利译本，导言却引英文版，不能把意译版出版信息写入英文版第三十三卷。Montaiglon保留书目责任者，不据排列直接指定编者或来信作者。
- 图版作品、画中人物、创作者、收藏者、保管机构、实际位置及描绘地点按角色分开；物理位置、收藏与复制图提供者不混同。供片者在摄影来源段和图版目录出现相同名称及同一图号时可作书内复用，未具定位的National Gallery仍待核。
- 图版14《耶稣圣名的胜利》按单幅作品登记，区别于已接收的耶稣堂整体拱顶工程。图版05未指明博尔盖塞枢机双胸像中的具体版本，暂不合并既有版本未定卡。图版68a的三幅未具名总督肖像保留群项，不造三份虚构题名。
- 英诺森十一世、G. M. Crespi、罗萨《命运》及图中Alexander VII涉及未接收的第六章旧卡。本轮保存确切候选路径及章前依据，不把旧卡的第六章内容自动纳入有效成果；其范围迁移需明确保留旧证据后处理。其余无关旧卡不动。
- Tim／Ben别名、复合印名Marabottini Marabotti、Ghezzi／Chiari印名、Guido及Tiepolo简称、爵号收藏者和部分摄影商号继续待决；姓名未展开不等于不存在。有上下文可以唯一锚定的其他对象以已知名初稿，不编造全名、生卒、QID或对齐状态。
- 泰斯塔和卡拉瓦乔的《逃往埃及途中的休息》题名相近，但目录作者不同，分开登记。未确认的同题版次仍保留具体出处，不用通用题名跨来源合并。

## 精确写回与预检

模型逐项编写类型、名称、字段、映射与边界；辅助程序只据这些明确裁决复制指定原文、排版和生成精确变更集，不以字符串相似度自动合并。写回前已生成完整差异预览并检查所有目标，修正了旧卡sources缩进差异及供片事实的来源编号。

预检覆盖：候选均有去向，拟建文件无未接收旧卡路径冲突；新增原书摘录逐条与实际行号文本一致；知识元链接与来源序号可解析；已有sources前缀与正式relations保持原值；新卡仅使用source_backed，不加入外部标识或验证日期。名称同一性及类型由本轮语义自查决定，不称独立验收。

写回采用全目标旧内容指纹核对后串行执行；更改前的已跟踪KU与accepted必须等于输入Git基线，新增路径必须不存在。事务在临时目录保留完整before／after及差异，失败可按实际写入列表恢复；仓库内只保存必要的写回路径与前后指纹，不重复存储全部正文。


## 写回结果与修正

已应用373个新路径、43个已接收KU的章前增量，以及4个未接收旧卡的范围整理；有效登记由418变为795。四张旧卡原位保留已知对象身份，仅采用本轮章前／索引证据成稿，原第六章草稿可从输入Git提交恢复；因此此前因旧卡范围暂缓的Crespi、Innocent XI、Fortune及画中Alexander VII现已交接。没有接受其旧有第六章事实。

逐卡检查发现20个人物与肖像标题相同，已在肖像标题中明确对象性质。图版61a／61b曾在排版变更集中共用了题名路径，已按两家不同馆藏拆为独立路径，并纠正全部受影响链接。链接标签替换曾越过三卡OCR摘录中的未闭合方括号；已从审查过的原始差异恢复，限定只改正文单行链接，并重新核对YAML和全部新增原句。

最终核对547条新增／重新登记的原书摘录及精确行号，已有43张有效卡的原sources和正式relations保持不变；4张旧卡的范围迁移另列在[写回指纹记录](registration-writeback.json)。已建立知识元链接，不新增正式边、外部验证日期或QID。源PDF和原始Markdown不变。

## 候选登记映射

以下只维护锚点到KU或处置的映射，不复制原句。原文、页行及语义边界仍见实体候选表和摄入处理结果。图版角色子锚点按该角色在本图版出现次序编号；`creator`、`subject`、`holder`、`site`、`carrier`、`depicted`等不是新增正式关系类型。相关表中链接属于来源内容导航，不是已验证的图谱边。

### 主候选

| 原文锚点 | 当前去向 | 知识元／说明 |
|---|---|---|
| FM-E001 | 新建 | [弗朗西斯·哈斯克尔（Francis Haskell）](../../../04-knowledge/units/persons/francis-haskell.md) |
| FM-E002 | 复用并更新 | [《赞助人与画家》（Patrons and Painters）](../../../04-knowledge/units/archives/patrons-and-painters.md) |
| FM-E003 | 新建 | [拉里萨（Larissa）](../../../04-knowledge/units/persons/larissa-dedicatee.md) |
| FM-E004 | 新建 | [耶鲁大学出版社（Yale University Press）](../../../04-knowledge/units/institutions/yale-university-press.md) |
| FM-E005 | 新建 | [耶鲁大学（Yale University）](../../../04-knowledge/units/institutions/yale-university.md) |
| FM-E006 | 新建 | [美国国会图书馆（Library of Congress）](../../../04-knowledge/units/institutions/library-of-congress.md) |
| FM-E007 | 新建 | [意大利人传记辞典（Dizionario biografico degli Italiani）](../../../04-knowledge/units/archives/dizionario-biografico-degli-italiani.md) |
| FM-E008 | 新建 | [查托与温达斯出版社（Chatto and Windus）](../../../04-knowledge/units/institutions/chatto-and-windus.md) |
| FM-E009 | 新建 | [诺拉·斯莫尔伍德（Norah Smallwood）](../../../04-knowledge/units/persons/norah-smallwood.md) |
| FM-E010 | 新建 | [约翰·尼科尔（John Nicoll）](../../../04-knowledge/units/persons/john-nicoll.md) |
| FM-E011 | 新建 | [罗伯特·恩加斯（Robert Enggass）](../../../04-knowledge/units/persons/robert-enggass.md) |
| FM-E012 | 新建 | [霍华德·希巴德（Howard Hibbard）](../../../04-knowledge/units/persons/howard-hibbard.md) |
| FM-E013 | 新建 | [安东尼·布伦特（Anthony Blunt）](../../../04-knowledge/units/persons/anthony-blunt.md) |
| FM-E014 | 新建 | [布鲁斯·鲍彻（Bruce Boucher）](../../../04-knowledge/units/persons/bruce-boucher.md) |
| FM-E015 | 新建 | [马尔科·基亚里尼（Marco Chiarini）](../../../04-knowledge/units/persons/marco-chiarini.md) |
| FM-E016 | 新建 | [安·萨瑟兰·哈里斯（Ann Sutherland Harris）](../../../04-knowledge/units/persons/ann-sutherland-harris.md) |
| FM-E017 | 新建 | [皮埃尔·罗森贝格（Pierre Rosenberg）](../../../04-knowledge/units/persons/pierre-rosenberg.md) |
| FM-E018 | 新建 | [玛丽安娜·罗兰-米歇尔（Marianne Roland-Michel）](../../../04-knowledge/units/persons/marianne-roland-michel.md) |
| FM-E019 | 对齐后复用 | [艾伦·诺埃尔·拉蒂默·芒比（Alan Noel Latimer Munby）](../../../04-knowledge/units/persons/a-n-l-munby.md)；Tim与A. N. L.为同人，见REV-086。 |
| FM-E020 | 对齐后复用 | [莱昂内尔·本尼迪克特·尼科尔森（Lionel Benedict Nicolson）](../../../04-knowledge/units/persons/benedict-nicolson.md)；Ben与Benedict为同人，见REV-086。 |
| FM-E021 | 新建 | [巴洛克（Baroque）](../../../04-knowledge/units/terms/baroque.md) |
| FM-E022 | 复用并更新 | [乌尔班八世（Urban VIII）](../../../04-knowledge/units/persons/urbano-viii.md) |
| FM-E023 | 新建 | [威尼斯共和国（Republic of Venice）](../../../04-knowledge/units/institutions/republic-of-venice.md) |
| FM-E024 | 新建 | [托斯卡纳大公子费迪南多（Grand Prince Ferdinand of Tuscany）](../../../04-knowledge/units/persons/ferdinand-grand-prince-tuscany.md) |
| FM-E025 | 新建 | [那不勒斯反古典绘画（Neapolitan anti-classical painting）](../../../04-knowledge/units/terms/neapolitan-anti-classical-painting.md) |
| FM-E026 | 新建 | [恩佐·克雷亚（Enzo Crea）](../../../04-knowledge/units/persons/enzo-crea.md) |
| FM-E027 | 新建 | [瓦尔堡研究院图书馆（Library of the Warburg Institute）](../../../04-knowledge/units/institutions/warburg-institute-library.md) |
| FM-E028 | 新建 | [剑桥国王学院（King's College, Cambridge）](../../../04-knowledge/units/institutions/kings-college-cambridge.md) |
| FM-E029 | 新建 | [T.与A.康斯特布尔印刷公司（T. and A. Constable Ltd.）](../../../04-knowledge/units/institutions/t-and-a-constable.md) |
| FM-E030 | 新建 | [A. N. L. 芒比（A. N. L. Munby）](../../../04-knowledge/units/persons/a-n-l-munby.md) |
| FM-E031 | 新建 | [G. H. W. 赖兰兹（G. H. W. Rylands）](../../../04-knowledge/units/persons/g-h-w-rylands.md) |
| FM-E032 | 新建 | [伊丽莎白·奥纳（Elizabeth Orna）](../../../04-knowledge/units/persons/elizabeth-orna.md) |
| FM-E033 | 新建 | [泰里西奥·皮尼亚蒂（Terisio Pignatti）](../../../04-knowledge/units/persons/terisio-pignatti.md) |
| FM-E034 | 新建 | [科雷尔图书馆（Correr Library）](../../../04-knowledge/units/institutions/correr-library.md) |
| FM-E035 | 新建 | [亚历山德罗·贝塔尼奥（Alessandro Bettagno）](../../../04-knowledge/units/persons/alessandro-bettagno.md) |
| FM-E036 | 新建 | [詹弗兰科·托尔切兰（Gianfranco Torcellan）](../../../04-knowledge/units/persons/gianfranco-torcellan.md) |
| FM-E037 | 新建 | [弗兰科·文图里（Franco Venturi）](../../../04-knowledge/units/persons/franco-venturi.md) |
| FM-E038 | 新建 | [加埃塔诺·科齐（Gaetano Cozzi）](../../../04-knowledge/units/persons/gaetano-cozzi.md) |
| FM-E039 | 新建 | [埃利斯·沃特豪斯（Ellis Waterhouse）](../../../04-knowledge/units/persons/ellis-waterhouse.md) |
| FM-E040 | 对齐后新建 | [亚历山德罗·马拉博蒂尼·马拉博蒂（Alessandro Marabottini Marabotti）](../../../04-knowledge/units/persons/alessandro-marabottini-marabotti.md)；大学目录另有复姓倒序写法，原印名保留。 |
| FM-E041 | 复用并更新 | [丹尼斯·马洪（Denis Mahon）](../../../04-knowledge/units/persons/denis-mahon.md) |
| FM-E042 | 新建 | [彼得·卡尔沃科雷西（Peter Calvocoressi）](../../../04-knowledge/units/persons/peter-calvocoressi.md) |
| FM-E043 | 新建 | [尼古拉斯·佩夫斯纳（Nikolaus Pevsner）](../../../04-knowledge/units/persons/nikolaus-pevsner.md) |
| FM-E044 | 新建 | [迈克尔·利维（Michael Levey）](../../../04-knowledge/units/persons/michael-levey.md) |
| FM-E045 | 新建 | [本尼迪克特·尼科尔森（Benedict Nicolson）](../../../04-knowledge/units/persons/benedict-nicolson.md) |
| FM-E046 | 新建 | [新古典主义（Neo-classicism）](../../../04-knowledge/units/terms/neo-classicism.md) |
| FM-E047 | 新建 | [弗朗切斯科·阿尔加罗蒂（Francesco Algarotti）](../../../04-knowledge/units/persons/francesco-algarotti.md) |
| FM-E048 | 新建 | [休·昂纳（Hugh Honour）](../../../04-knowledge/units/persons/hugh-honour.md) |
| FM-E049 | 新建 | [鲁道夫·维特科尔（Rudolf Wittkower）](../../../04-knowledge/units/persons/rudolf-wittkower.md) |
| FM-E050 | 新建 | [塞巴斯蒂亚诺·孔卡（Sebastiano Conca）](../../../04-knowledge/units/persons/sebastiano-conca.md) |
| FM-E051 | 新建 | [贾昆托（Giaquinto）](../../../04-knowledge/units/persons/giaquinto-front-matter.md) |
| FM-E052 | 新建 | [蓬佩奥·巴托尼（Pompeo Batoni）](../../../04-knowledge/units/persons/pompeo-batoni.md) |
| FM-E053 | 复用并更新 | [保罗·杰罗拉莫·皮奥拉（Paolo Gerolamo Piola）](../../../04-knowledge/units/persons/paolo-girolamo-piola.md) |
| FM-E054 | 新建 | [多梅尼科·马里亚·维亚尼（Domenico Maria Viani）](../../../04-knowledge/units/persons/domenico-maria-viani.md) |
| FM-E055 | 新建后对齐 | [格雷戈里奥·拉扎里尼（Gregorio Lazzarini）](../../../04-knowledge/units/persons/gregorio-lazzarini.md)；DBI明确记其拒绝迁居罗马，补足语境身份链，见REV-090。 |
| FM-E056 | 新建 | [塞巴斯蒂亚诺·孔卡（Sebastiano Conca）](../../../04-knowledge/units/persons/sebastiano-conca.md) |
| FM-E057 | 原位整理后接收 | [朱塞佩·马里亚·克雷斯皮（Giuseppe Maria Crespi）](../../../04-knowledge/units/persons/giuseppe-maria-crespi.md) |
| FM-E058 | 新建 | [弗朗切斯科·索利梅纳（Francesco Solimena）](../../../04-knowledge/units/persons/solimena.md) |
| FM-E059 | 原位整理后接收 | [英诺森十一世（Innocent XI）](../../../04-knowledge/units/persons/innocent-xi.md) |
| FM-E060 | 复用并更新 | [克雷芒十一世（Clement XI）](../../../04-knowledge/units/persons/clement-xi.md) |
| FM-E061 | 新建 | [皮埃尔·勒格罗与晚期巴洛克罗马雕塑家的设计师角色（Pierre Legros and the role of Sculptors as Designers in late Baroque Rome）](../../../04-knowledge/units/archives/conforti-legros-designers-1977.md) |
| FM-E062 | 新建 | [帕斯托教皇史英文版第三十三卷（Pastor's history of the popes, English edition, volume XXXIII）](../../../04-knowledge/units/archives/pastor-popes-english-vol33.md) |
| FM-E063 | 新建 | [十八世纪罗马绘画（Painting in Rome in the Eighteenth Century）](../../../04-knowledge/units/archives/waterhouse-rome-painting-1971.md) |
| FM-E064 | 新建 | [夏尔-弗朗索瓦·普瓦松（Charles-François Poerson）](../../../04-knowledge/units/persons/charles-francois-poerson.md) |
| FM-E065 | 新建 | [罗马法国学院（French Academy in Rome）](../../../04-knowledge/units/institutions/french-academy-in-rome.md) |
| FM-E066 | 新建 | [普瓦松1708年论罗马绘画报酬的信（Poerson's 1708 letter on rewards for painting in Rome）](../../../04-knowledge/units/archives/poerson-letter-1708.md) |
| FM-E067 | 新建 | [罗马法国学院主管与王室建筑总监通信集（Correspondence of the Directors of the French Academy in Rome with the Superintendents of Buildings）](../../../04-knowledge/units/archives/montaiglon-academy-correspondence.md) |
| FM-E068 | 新建 | [罗马圣克莱孟堂（S. Clemente, Rome）](../../../04-knowledge/units/places/san-clemente-rome.md) |
| FM-E069 | 新建 | [圣克莱孟堂重新装饰（Redecoration of S. Clemente）](../../../04-knowledge/units/events/san-clemente-redecoration.md) |
| FM-E070 | 新建 | [皮埃特罗·迪·皮耶特里（Pietro di Pietri）](../../../04-knowledge/units/persons/pietro-di-pietri.md) |
| FM-E071 | 对齐后新建 | [皮耶尔·莱奥内·盖齐（Pier Leone Ghezzi）](../../../04-knowledge/units/persons/pier-leone-ghezzi.md)；以圣克莱孟堂项目定位，保留Pier Leoni原书写法。 |
| FM-E072 | 对齐后新建 | [托马索·基亚里（Tommaso Chiari）](../../../04-knowledge/units/persons/tommaso-chiari.md)；官方目录与Giuseppe Bartolomeo Chiari分列，不改名合并。 |
| FM-E073 | 新建 | [乔万尼·多梅尼科·皮亚斯特里尼（Giovanni Domenico Piastrini）](../../../04-knowledge/units/persons/giovanni-domenico-piastrini.md) |
| FM-E074 | 新建 | [贾科莫·特里加（Giacomo Triga）](../../../04-knowledge/units/persons/giacomo-triga.md) |
| FM-E075 | 新建 | [安东尼·克拉克（Anthony Clark）](../../../04-knowledge/units/persons/anthony-clark.md) |
| FM-E076 | 新建 | [克勉十一世为罗马圣克莱孟圣殿委托的绘画（The Paintings commissioned by Pope Clement XI for the Basilica of S. Clemente in Rome）](../../../04-knowledge/units/archives/gilmartin-san-clemente-1974.md) |
| FM-E077 | 对齐后复用 | [圭多·雷尼（Guido Reni）](../../../04-knowledge/units/persons/guido-reni.md)；据十七世纪、与Guercino并举及罗马活动语境作语义配对，非索引直接指页证明。 |
| FM-E078 | 复用并更新 | [乔万尼·弗朗切斯科·巴尔比耶里（Giovanni Francesco Barbieri）](../../../04-knowledge/units/persons/guercino.md) |
| FM-E079 | 对齐后新建 | [乔万巴蒂斯塔·提埃坡罗（Giambattista Tiepolo）](../../../04-knowledge/units/persons/giambattista-tiepolo.md)；此行只确认导言xvii提及；图版作者逐件判断。 |
| FM-E080 | 复用并更新 | [乔万尼·奥达齐（Giovanni Odazzi）](../../../04-knowledge/units/persons/giovanni-odazzi.md) |
| FM-E081 | 复用并更新 | [皮耶特罗·达·科尔托纳（Pietro da Cortona）](../../../04-knowledge/units/persons/pietro-da-cortona.md) |
| FM-E082 | 对齐后新建 | [圣克莱孟一世（Clement I）](../../../04-knowledge/units/persons/clement-i.md)；教堂命名人物，区别于装饰委托人Clement XI。 |
| FM-E083 | 新建 | [休·昂纳1963年评论赞助人与画家的书评（Hugh Honour's 1963 review of Patrons and Painters）](../../../04-knowledge/units/archives/honour-patrons-painters-review-1963.md) |
| FM-E084 | 新建 | [艺术赞助（Art patronage）](../../../04-knowledge/units/terms/art-patronage.md) |
| FM-E085 | 属性／语境保留 | [本书](../../../04-knowledge/units/archives/patrons-and-painters.md)及处理结果，不新增KU |
| FM-E086 | 属性／语境保留 | [本书](../../../04-knowledge/units/archives/patrons-and-painters.md)及处理结果，不新增KU |
| FM-E087 | 属性／语境保留 | [本书](../../../04-knowledge/units/archives/patrons-and-painters.md)及处理结果，不新增KU |
| FM-E088 | 新建 | [美国版权法（U.S. Copyright Law）](../../../04-knowledge/units/archives/us-copyright-law.md) |
| FM-E089 | 新建 | [迈克尔·康福尔蒂（Michael Conforti）](../../../04-knowledge/units/persons/michael-conforti.md) |
| FM-E090 | 新建 | [路德维科·冯·帕斯托（Ludovico von Pastor）](../../../04-knowledge/units/persons/pastor-historian.md) |
| FM-E091 | 新建 | [A. 德·蒙泰格隆（A. de Montaiglon）](../../../04-knowledge/units/persons/a-de-montaiglon.md) |
| FM-E092 | 新建 | [约翰·吉尔马丁（John Gilmartin）](../../../04-knowledge/units/persons/john-gilmartin.md) |
| FM-E093 | 新建 | [阿波罗期刊（Apollo）](../../../04-knowledge/units/archives/apollo-periodical.md) |
| FM-E094 | 新建 | [瓦尔堡研究院（Warburg Institute）](../../../04-knowledge/units/institutions/warburg-institute.md) |
| FM-L01 | 新建 | [纽黑文（New Haven）](../../../04-knowledge/units/places/new-haven.md) |
| FM-L02 | 复用并更新 | [伦敦（London）](../../../04-knowledge/units/places/london.md) |
| FM-L03 | 新建 | [中国（China）](../../../04-knowledge/units/places/china.md) |
| FM-L04 | 复用并更新 | [意大利（Italy）](../../../04-knowledge/units/places/italy.md) |
| FM-L05 | 新建 | [牛津（Oxford）](../../../04-knowledge/units/places/oxford.md) |
| FM-L06 | 新建 | [剑桥（Cambridge）](../../../04-knowledge/units/places/cambridge.md) |
| FM-L07 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-L08 | 复用并更新 | [威尼斯（Venice）](../../../04-knowledge/units/places/venice.md) |
| FM-L09 | 新建 | [托斯卡纳（Tuscany）](../../../04-knowledge/units/places/tuscany.md) |
| FM-L10 | 复用并更新 | [那不勒斯（Naples）](../../../04-knowledge/units/places/naples.md) |
| FM-L11 | 新建 | [欧洲（Europe）](../../../04-knowledge/units/places/europe.md) |
| FM-L12 | 新建 | [英格兰（England）](../../../04-knowledge/units/places/england.md) |
| FM-L13 | 新建 | [威尼托（Veneto）](../../../04-knowledge/units/places/veneto.md) |
| FM-P01 | 新建 | [罗马寓意（Allegory of Rome）](../../../04-knowledge/units/works/valentin-allegory-of-rome.md) |
| FM-P02a | 新建 | [马费奥·巴贝里尼肖像（Maffeo Barberini）](../../../04-knowledge/units/works/caravaggio-maffeo-barberini.md) |
| FM-P02b | 新建 | [乌尔班八世肖像（Maffeo Barberini as Pope Urban VIII）](../../../04-knowledge/units/works/bernini-maffeo-barberini-as-pope-urban-viii.md) |
| FM-P03a | 新建 | [弗朗切斯科·巴贝里尼枢机（Cardinal Francesco Barberini）](../../../04-knowledge/units/works/ottavio-leoni-cardinal-francesco-barberini.md) |
| FM-P03b | 新建 | [安东尼奥·巴贝里尼枢机（Cardinal Antonio Barberini）](../../../04-knowledge/units/works/carlo-maratta-cardinal-antonio-barberini.md) |
| FM-P04a | 新建 | [本蒂沃利奥枢机肖像（Portrait of Cardinal Bentivoglio）](../../../04-knowledge/units/works/van-dyck-cardinal-bentivoglio.md) |
| FM-P04b | 新建 | [马尔切洛·萨凯蒂肖像（Portrait of Marcello Sacchetti）](../../../04-knowledge/units/works/pietro-da-cortona-marcello-sacchetti.md) |
| FM-P05 | 暂缓 | 图版未说明两件Scipione胸像中的哪一件；既有卡也未裁定版本，保留候选而不合并或造重复卡。 候选：[贝尔尼尼的博尔盖塞枢机肖像头部（Bernini’s portrait head of Cardinal Borghese）](../../../04-knowledge/units/works/bernini-cardinal-borghese-head.md) |
| FM-P06 | 新建 | [1630年博尔盖塞别墅景观（View of Villa Borghese in 1630）](../../../04-knowledge/units/works/guglielmo-baur-view-of-villa-borghese-in-1630.md) |
| FM-P07 | 新建 | [狄安娜狩猎（Hunt of Diana）](../../../04-knowledge/units/works/domenichino-hunt-of-diana.md) |
| FM-P08 | 新建 | [谷地圣安德烈堂巴贝里尼礼拜堂（Barberini Chapel）](../../../04-knowledge/units/places/barberini-chapel-sant-andrea-valle.md) |
| FM-P09 | 新建 | [《巴贝里尼宫》卷首图（Frontispiece of Aedes Barberinae ad Quirinalem）](../../../04-knowledge/units/works/guido-abbatini-frontispiece-of-aedes-barberinae-ad-quirinalem.md) |
| FM-P10a | 新建 | [劫夺萨宾妇女（Rape of the Sabines）](../../../04-knowledge/units/works/pietro-da-cortona-rape-of-the-sabines.md) |
| FM-P10b | 新建 | [劫夺海伦（Rape of Helen）](../../../04-knowledge/units/works/pietro-da-cortona-rape-of-helen.md) |
| FM-P11a | 新建 | [以扫与雅各相会（Meeting of Esau and Jacob）](../../../04-knowledge/units/works/gio-maria-bottalla-meeting-of-esau-and-jacob.md) |
| FM-P11b | 新建 | [约瑟被兄弟出卖（Joseph Sold by his Brothers）](../../../04-knowledge/units/works/pietro-testa-joseph-sold-by-his-brothers.md) |
| FM-P12 | 新建 | [神圣智慧寓意（Allegory of Divine Wisdom）](../../../04-knowledge/units/works/andrea-sacchi-allegory-of-divine-wisdom.md) |
| FM-P13 | 新建 | [乌尔班八世统治的荣耀（Glorification of the Reign of Urban VIII）](../../../04-knowledge/units/works/pietro-da-cortona-glorification-of-the-reign-of-urban-viii.md) |
| FM-P14 | 新建 | [耶稣圣名的胜利（Triumph of The Name of Jesus）](../../../04-knowledge/units/works/gaulli-triumph-name-jesus.md) |
| FM-P15 | 新建 | [圣依纳爵堂拱顶壁画模型（Modello for fresco on vault of S. Ignazio）](../../../04-knowledge/units/works/andrea-pozzo-modello-for-fresco-on-vault-of-s-ignazio.md) |
| FM-P16 | 新建 | [奎里纳尔圣安德烈堂内部（Interior of S. Andrea al Quirinale）](../../../04-knowledge/units/places/interior-sant-andrea-quirinale.md) |
| FM-P17a | 新建 | [卡西亚诺·达尔·波佐漫画（Caricature of Cassiano dal Pozzo）](../../../04-knowledge/units/works/bernini-caricature-of-cassiano-dal-pozzo.md) |
| FM-P17b | 新建 | [文琴佐·朱斯蒂尼亚尼肖像（Portrait of Vincenzo Giustiniani）](../../../04-knowledge/units/works/claude-mellan-vincenzo-giustiniani.md) |
| FM-P17c | 新建 | [布拉恰诺公爵（Paolo Giordano Orsini, Duke of Bracciano）](../../../04-knowledge/units/works/ottavio-leoni-paolo-giordano-orsini-duke-of-bracciano.md) |
| FM-P18a | 新建 | [逃往埃及途中的休息（Rest on the Flight into Egypt）](../../../04-knowledge/units/works/pietro-testa-rest-on-the-flight-into-egypt.md) |
| FM-P18b | 新建 | [婚姻（Marriage）](../../../04-knowledge/units/works/poussin-marriage.md) |
| FM-P19a | 新建 | [摩西践踏法老王冠（Moses trampling on Pharaoh's crown）](../../../04-knowledge/units/works/poussin-moses-trampling-on-pharaoh-s-crown.md) |
| FM-P19b | 新建 | [有队列的德尔斐景观（View of Delphi with a Procession）](../../../04-knowledge/units/works/claude-view-of-delphi-with-a-procession.md) |
| FM-P20 | 新建 | [卡米洛·马西米肖像（Portrait of Camillo Massimi）](../../../04-knowledge/units/works/velasquez-camillo-massimi.md) |
| FM-P21a | 新建 | [玫瑰圣母与道明、加大利纳（Madonna of the Rosary with Saints Dominic and Catherine）](../../../04-knowledge/units/works/sassoferrato-madonna-of-the-rosary-with-saints-dominic-and-catherine.md) |
| FM-P21b | 新建 | [圣母子（Madonna and Child）](../../../04-knowledge/units/works/sassoferrato-madonna-and-child.md) |
| FM-P22a | 新建 | [画家及友人群像（The artist with a group of friends）](../../../04-knowledge/units/works/michelangelo-cerquozzi-the-artist-with-a-group-of-friends.md) |
| FM-P22b | 新建 | [马萨涅洛起义（The Revolt of Masaniello）](../../../04-knowledge/units/works/michelangelo-cerquozzi-the-revolt-of-masaniello.md) |
| FM-P23a | 新建 | [女浴（Women's Bath）](../../../04-knowledge/units/works/michelangelo-cerquozzi-women-s-bath.md) |
| FM-P23b | 新建 | [雷古鲁斯之死（The Death of Regulus）](../../../04-knowledge/units/works/salvator-rosa-the-death-of-regulus.md) |
| FM-P24 | 原位整理后接收 | [罗萨命运（Fortune by Salvator Rosa）](../../../04-knowledge/units/works/fortune-salvator-rosa.md) |
| FM-P25 | 新建 | [公共幸福战胜危难（Public Felicity triumphant over Dangers）](../../../04-knowledge/units/works/orazio-gentileschi-public-felicity-triumphant-over-dangers.md) |
| FM-P26a | 新建 | [画廊中的马扎然（Cardinal Mazarin in his Gallery）](../../../04-knowledge/units/works/nanteuil-cardinal-mazarin-in-his-gallery.md) |
| FM-P26b | 新建 | [罗慕路斯与雷穆斯顶画局部（Romulus and Remus）](../../../04-knowledge/units/works/romanelli-romulus-and-remus.md) |
| FM-P27a | 新建 | [查理一世肖像（Portrait of Charles I）](../../../04-knowledge/units/works/francesco-fanelli-charles-i.md) |
| FM-P27b | 新建 | [路易十四肖像（Portrait of Louis XIV）](../../../04-knowledge/units/works/bernini-louis-xiv.md) |
| FM-P28a | 新建 | [克娄巴特拉之死（Death of Cleopatra）](../../../04-knowledge/units/works/guido-cagnacci-death-of-cleopatra.md) |
| FM-P28b | 新建 | [歌剧《拉丁君权凯旋》的极乐世界（The Elysian Fields）](../../../04-knowledge/units/works/burnacini-the-elysian-fields.md) |
| FM-P29 | 新建 | [汉普顿宫楼梯壁画（Fresco on staircase of Hampton Court Palace）](../../../04-knowledge/units/works/antonio-verrio-fresco-on-staircase-of-hampton-court-palace.md) |
| FM-P30a | 新建 | [杰罗姆·班克斯肖像（Portrait of Jerome Bankes）](../../../04-knowledge/units/works/massimo-stanzione-jerome-bankes.md) |
| FM-P30b | 新建 | [托马斯·贝恩斯（Sir Thomas Baines）](../../../04-knowledge/units/works/carlo-dolci-sir-thomas-baines.md) |
| FM-P31a | 新建 | [查尔斯·福克斯肖像（Portrait of Charles Fox）](../../../04-knowledge/units/works/carlo-maratta-charles-fox.md) |
| FM-P31b | 新建 | [托马斯·伊舍姆（Sir Thomas Isham）](../../../04-knowledge/units/works/carlo-maratta-sir-thomas-isham.md) |
| FM-P32a | 新建 | [醉西勒诺斯（The drunken Silenus）](../../../04-knowledge/units/works/ribera-the-drunken-silenus.md) |
| FM-P32b | 新建 | [赫拉克勒斯的选择（The choice of Hercules）](../../../04-knowledge/units/works/paolo-de-matteis-the-choice-of-hercules.md) |
| FM-P33a | 新建 | [狄多与埃涅阿斯（Dido and Aeneas）](../../../04-knowledge/units/works/solimena-dido-and-aeneas.md) |
| FM-P33b | 新建 | [布奥纳科尔西宫画廊（Gallery of Palazzo Buonaccorsi）](../../../04-knowledge/units/places/gallery-palazzo-buonaccorsi.md) |
| FM-P34 | 新建 | [胡安·德·帕雷哈肖像（Portrait of Juan de Pareja）](../../../04-knowledge/units/works/velasquez-juan-de-pareja.md) |
| FM-P35a | 新建 | [凝视荷马像的亚里士多德（Aristotle contemplating the bust of Homer）](../../../04-knowledge/units/works/rembrandt-aristotle-contemplating-the-bust-of-homer.md) |
| FM-P35b | 新建 | [希律王宴会（The Feast of Herod）](../../../04-knowledge/units/works/rubens-the-feast-of-herod.md) |
| FM-P36a | 新建 | [托斯卡纳大公子费迪南多肖像（Portrait of Grand Prince Ferdinand of Tuscany）](../../../04-knowledge/units/works/francesco-petrucci-grand-prince-ferdinand-of-tuscany.md) |
| FM-P36b | 新建 | [梳妆少女（Girl at her toilet）](../../../04-knowledge/units/works/g-m-crespi-girl-at-her-toilet.md) |
| FM-P37a | 新建 | [画家一家（The Painter's Family）](../../../04-knowledge/units/works/g-m-crespi-the-painter-s-family.md) |
| FM-P37b | 新建 | [波焦阿卡亚诺集市局部（Detail from Fair at Poggio a Caiano）](../../../04-knowledge/units/works/g-m-crespi-detail-from-fair-at-poggio-a-caiano.md) |
| FM-P37c | 新建 | [阿尔洛托教区神父的玩笑（La Burla del Piovano Arlotto）](../../../04-knowledge/units/works/baldassare-franceschini-la-burla-del-piovano-arlotto.md) |
| FM-P38a | 新建 | [劫夺欧罗巴（Rape of Europa）](../../../04-knowledge/units/works/sebastiano-ricci-rape-of-europa.md) |
| FM-P38b | 新建 | [潘与绪任克斯（Pan and Syrinx）](../../../04-knowledge/units/works/sebastiano-ricci-pan-and-syrinx.md) |
| FM-P39 | 新建 | [维纳斯与阿多尼斯（Venus and Adonis）](../../../04-knowledge/units/works/sebastiano-ricci-venus-and-adonis.md) |
| FM-P40a | 新建 | [乐师群像（A Group of Musicians）](../../../04-knowledge/units/works/a-d-gabbiani-a-group-of-musicians.md) |
| FM-P40b | 新建 | [撒迦利亚被石击（The stoning of Zechariah）](../../../04-knowledge/units/works/giannantonio-fumiani-the-stoning-of-zechariah.md) |
| FM-P41a | 新建 | [百合圣母堂立面（Facade of S. Maria del Giglio）](../../../04-knowledge/units/works/facade-of-s-maria-del-giglio.md) |
| FM-P41b | 新建 | [乔瓦尼·佩萨罗总督纪念碑（Monument to Doge Giovanni Pesaro）](../../../04-knowledge/units/works/monument-to-doge-giovanni-pesaro.md) |
| FM-P42a | 新建 | [海神向威尼斯致敬（Neptune paying homage to Venice）](../../../04-knowledge/units/works/tiepolo-neptune-paying-homage-to-venice.md) |
| FM-P42b | 新建 | [威尼斯寓意（Allegory of Venice）](../../../04-knowledge/units/works/niccolo-bambini-allegory-of-venice.md) |
| FM-P43 | 新建 | [雷佐尼科家族婚姻寓意（Marriage Allegory of the Rezzonico family）](../../../04-knowledge/units/works/tiepolo-marriage-allegory-of-the-rezzonico-family.md) |
| FM-P44 | 新建 | [皮萨尼家族的荣耀（Glorification of the Pisani family）](../../../04-knowledge/units/works/tiepolo-glorification-of-the-pisani-family.md) |
| FM-P45 | 新建 | [威尼斯的胜利（The Triumph of Venice）](../../../04-knowledge/units/works/pompeo-batoni-the-triumph-of-venice.md) |
| FM-P46 | 新建 | [皮埃尔·莫特及家人（Pierre Motteux and his family）](../../../04-knowledge/units/works/pellegrini-pierre-motteux-and-his-family.md) |
| FM-P47 | 新建 | [歌剧排练（An Operatic Rehearsal）](../../../04-knowledge/units/works/marco-ricci-an-operatic-rehearsal.md) |
| FM-P48a | 新建 | [弗拉米尼奥·科尔内尔肖像（Portrait of Flaminio Corner）](../../../04-knowledge/units/works/marco-pitteri-flaminio-corner.md) |
| FM-P48b | 新建 | [扎卡里亚·萨格雷多肖像（Portrait of Zaccaria Sagredo）](../../../04-knowledge/units/works/gian-antonio-faldoni-zaccaria-sagredo.md) |
| FM-P48c | 新建 | [卡洛·洛多利肖像（Portrait of Carlo Lodoli）](../../../04-knowledge/units/works/alessandro-longhi-carlo-lodoli.md) |
| FM-P48d | 新建 | [弗朗切斯科·阿尔加罗蒂肖像（Portrait of Francesco Algarotti）](../../../04-knowledge/units/works/francesco-algarotti.md) |
| FM-P49a | 新建 | [普法尔茨王储教育寓意（Allegory of the Education of the Crown Prince of the Palatinate）](../../../04-knowledge/units/works/pellegrini-allegory-of-the-education-of-the-crown-prince-of-the-palatinate.md) |
| FM-P49b | 新建 | [朱庇特与伊娥（Jupiter and Io）](../../../04-knowledge/units/works/amigoni-jupiter-and-io.md) |
| FM-P50 | 新建 | [维尔茨堡宫楼梯顶画局部（Detail from fresco on ceiling of staircase in Residenz）](../../../04-knowledge/units/works/tiepolo-detail-from-fresco-on-ceiling-of-staircase-in-residenz.md) |
| FM-P51 | 新建 | [巴德明顿景观（View from Badminton, 1748）](../../../04-knowledge/units/works/canaletto-view-from-badminton-1748.md) |
| FM-P52a | 新建 | [欧文·麦克斯温尼肖像（Portrait of Owen McSwiny）](../../../04-knowledge/units/works/p-van-bleek-owen-mcswiny.md) |
| FM-P52b | 新建 | [蒂洛特森大主教寓意纪念墓（Allegorical Tomb to the memory of Archbishop Tillotson）](../../../04-knowledge/units/works/canaletto-allegorical-tomb-to-the-memory-of-archbishop-tillotson.md) |
| FM-P53a | 新建 | [舒伦堡元帅肖像（Portrait of Marshal Schulenburg）](../../../04-knowledge/units/works/piazzetta-marshal-schulenburg.md) |
| FM-P53b | 新建 | [西吉斯蒙德·施特赖特肖像（Portrait of Sigismund Streit）](../../../04-knowledge/units/works/amigoni-sigismund-streit.md) |
| FM-P54 | 新建 | [田园（Idyll）](../../../04-knowledge/units/works/piazzetta-idyll.md) |
| FM-P55a | 新建 | [蚀刻集献辞卷首图（Dedicatory frontispiece to Etchings）](../../../04-knowledge/units/works/canaletto-dedicatory-frontispiece-to-etchings.md) |
| FM-P55b | 新建 | [村景（Village Scene）](../../../04-knowledge/units/works/marco-ricci-village-scene.md) |
| FM-P56 | 新建 | [圣洛克堂画展（Picture Exhibition at Church of S. Rocco）](../../../04-knowledge/units/works/marieschi-picture-exhibition-at-church-of-s-rocco.md) |
| FM-P57a | 新建 | [《耶路撒冷解放》插图末页（Final plate of Illustrations to Gerusalemme Liberata）](../../../04-knowledge/units/works/piazzetta-final-plate-of-illustrations-to-gerusalemme-liberata.md) |
| FM-P57b | 新建 | [戈尔多尼《作品集》第二卷卷首图（Frontispiece to Vol. 2 of Goldoni: Opere）](../../../04-knowledge/units/works/pietro-antonio-novelli-frontispiece-to-vol-2-of-goldoni-opere.md) |
| FM-P58a | 新建 | [老扎内蒂与杰里尼侯爵（A. M. Zanetti the Elder with Marchese Gerini）](../../../04-knowledge/units/works/giuseppe-zocchi-a-m-zanetti-the-elder-with-marchese-gerini.md) |
| FM-P58b | 新建 | [G. M. 萨索肖像（Portrait of G. M. Sasso）](../../../04-knowledge/units/works/alessandro-longhi-g-m-sasso.md) |
| FM-P59a | 新建 | [阿马德奥·斯瓦耶尔肖像（Portrait of Amadeo Swajer）](../../../04-knowledge/units/works/canova-amadeo-swajer.md) |
| FM-P59b | 新建 | [泰奥多罗·科雷尔肖像（Portrait of Teodoro Correr）](../../../04-knowledge/units/works/bernardino-castelli-teodoro-correr.md) |
| FM-P60 | 新建 | [阿尔加罗蒂墓前悼念者（Mourners at Tomb of Francesco Algarotti in Pisa）](../../../04-knowledge/units/works/g-volpato-mourners-at-tomb-of-francesco-algarotti-in-pisa.md) |
| FM-P61a | 新建 | [安东尼与克娄巴特拉宴会：科涅克—杰藏本（Banquet of Anthony and Cleopatra, Cognacq-Jay version）](../../../04-knowledge/units/works/tiepolo-banquet-cognacq-jay.md) |
| FM-P61b | 新建 | [安东尼与克娄巴特拉宴会：维多利亚国家美术馆藏本（Banquet of Anthony and Cleopatra, National Gallery of Victoria version）](../../../04-knowledge/units/works/tiepolo-banquet-victoria.md) |
| FM-P62 | 新建 | [帕多瓦Prà广场（Prà della Valle, Padua）](../../../04-knowledge/units/works/canaletto-pra-della-valle-padua.md) |
| FM-P63 | 新建 | [Prà广场整治原始方案（Original proposals for reclaiming Prà della Valle）](../../../04-knowledge/units/works/domenico-cerato-original-proposals-for-reclaiming-pra-della-valle.md) |
| FM-P64 | 新建 | [约翰·斯特兰奇别墅景观（View of John Strange's villa at Paese near Treviso）](../../../04-knowledge/units/works/francesco-guardi-view-of-john-strange-s-villa-at-paese-near-treviso.md) |
| FM-P65a | 新建 | [西莫内利与莫拉联合漫画（Joint caricature of Simonelli and Mola）](../../../04-knowledge/units/works/mola-joint-caricature-of-simonelli-and-mola.md) |
| FM-P65b | 新建 | [莫拉为亚历山大七世作像（Mola painting the portrait of Pope Alexander VII）](../../../04-knowledge/units/works/agostino-masucci-mola-painting-the-portrait-of-pope-alexander-vii.md) |
| FM-P66 | 新建 | [声名携路易十四之名入不朽殿堂（Fame carrying the name of Louis XIV to the Temple of Immortality）](../../../04-knowledge/units/works/baldassare-franceschini-fame-carrying-the-name-of-louis-xiv-to-the-temple-of-immortality.md) |
| FM-P67 | 新建 | [库柏勒将朱庇特交给科律班忒斯哺育（Jupiter handed over by Cybele to the Corybantes to be fed）](../../../04-knowledge/units/works/g-m-crespi-jupiter-handed-over-by-cybele-to-the-corybantes-to-be-fed.md) |
| FM-P68a | 暂缓 | 目录合列三幅未具名总督肖像；未定位三件实物前不把群项伪装成一个或三个确定作品。 |
| FM-P68b | 新建 | [梅塞纳斯向奥古斯都呈献艺术（Maecenas presenting the Arts to Augustus）](../../../04-knowledge/units/works/tiepolo-maecenas-presenting-the-arts-to-augustus.md) |
| FM-H01 | 新建后对齐 | [Agraci — Arts Graphiques de la Cité](../../../04-knowledge/units/institutions/agraci.md)；按摄影商号登记，19a、25供片；见REV-090。 |
| FM-H02 | 暂缓 | 署名的个人／商号／复合代理或机构具体身份未定，保留原供片编号，不据摄影署名猜法人或合并现有机构。 |
| FM-H03 | 新建后对齐 | [巴莱利摄影工作室（Studio fotografico Balelli）](../../../04-knowledge/units/institutions/studio-fotografico-balelli.md)；馆方明确工作室与画廊照片题材，33b供片；见REV-091。 |
| FM-H04 | 新建后对齐 | [Ditta Osvaldo Böhm](../../../04-knowledge/units/institutions/osvaldo-bohm-photographic-publisher.md)；摄影出版商号，41b、44供片；见REV-090。 |
| FM-H05 | 暂缓 | 署名的个人／商号／复合代理或机构具体身份未定，保留原供片编号，不据摄影署名猜法人或合并现有机构。 |
| FM-H06 | 新建 | [R. B. 弗莱明（R. B. Fleming）](../../../04-knowledge/units/persons/r-b-fleming.md) |
| FM-H07 | 新建 | [约翰·R. 弗里曼（John R. Freeman）](../../../04-knowledge/units/persons/john-r-freeman.md) |
| FM-H08 | 新建 | [国家摄影室（Gabinetto Fotografico Nazionale）](../../../04-knowledge/units/institutions/gabinetto-fotografico-nazionale.md) |
| FM-H09 | 暂缓 | 署名的个人／商号／复合代理或机构具体身份未定，保留原供片编号，不据摄影署名猜法人或合并现有机构。 |
| FM-H10 | 新建 | [马尔伯勒美术公司（Marlborough Fine Art Ltd）](../../../04-knowledge/units/institutions/marlborough-fine-art-ltd.md) |
| FM-H11 | 新建 | [工程部（Ministry of Works）](../../../04-knowledge/units/institutions/ministry-of-works.md) |
| FM-H12 | 暂缓 | 署名的个人／商号／复合代理或机构具体身份未定，保留原供片编号，不据摄影署名猜法人或合并现有机构。 |
| FM-H13 | 暂缓 | 署名的个人／商号／复合代理或机构具体身份未定，保留原供片编号，不据摄影署名猜法人或合并现有机构。 |
| FM-H14 | 暂缓 | 署名的个人／商号／复合代理或机构具体身份未定，保留原供片编号，不据摄影署名猜法人或合并现有机构。 |
| FM-H15 | 新建 | [国家肖像馆（National Portrait Gallery）](../../../04-knowledge/units/institutions/national-portrait-gallery.md) |
| FM-H16 | 暂缓 | 署名的个人／商号／复合代理或机构具体身份未定，保留原供片编号，不据摄影署名猜法人或合并现有机构。 |
| FM-H17 | 新建 | [皇家艺术学院（Royal Academy）](../../../04-knowledge/units/institutions/royal-academy.md) |
| FM-H18 | 新建 | [奥斯卡·萨维奥（Oscar Savio）](../../../04-knowledge/units/persons/oscar-savio.md) |
| FM-H19 | 新建 | [法国国家博物馆摄影文献服务处（Service de Documentation Photographique des Musées Nationaux）](../../../04-knowledge/units/institutions/service-de-documentation-photographique-des-musees-nationaux.md) |
| FM-H20 | 新建 | [佛罗伦萨美术馆监管机构（Soprintendenza alle Gallerie, Florence）](../../../04-knowledge/units/institutions/soprintendenza-alle-gallerie-florence.md) |
| FM-H21 | 新建 | [斯特恩父子公司（Stearn and Son）](../../../04-knowledge/units/institutions/stearn-and-son.md) |
| FM-H22 | 新建 | [剑桥特纳摄影商号（Turners of Cambridge）](../../../04-knowledge/units/institutions/turners-of-cambridge.md) |
| FM-H23 | 新建 | [剑桥大学图书馆（University Library, Cambridge）](../../../04-knowledge/units/institutions/university-library-cambridge.md) |
| FM-H24 | 新建后对齐 | [A. Villani e Figli](../../../04-knowledge/units/institutions/a-villani-e-figli.md)；摄影公司，28a供片；见REV-090。 |
| FM-H25 | 新建 | [埃伯哈德·茨维克（Eberhard Zwicker）](../../../04-knowledge/units/persons/eberhard-zwicker.md) |
| FM-H26 | 属性／语境保留 | [本书](../../../04-knowledge/units/archives/patrons-and-painters.md)及处理结果，不新增KU |

### 图版角色与登记时补出的引用端点

| 提及锚点 | 当前去向 | 知识元／说明 |
|---|---|---|
| FM-P01.creator1 | 复用并更新 | [瓦朗坦·德·布洛涅（Valentin de Boulogne）](../../../04-knowledge/units/persons/valentin.md) |
| FM-P01.holder1 | 新建 | [芬兰研究院（罗马）（Finnish Institute）](../../../04-knowledge/units/institutions/finnish-institute.md) |
| FM-P01.object | 新建 | [罗马寓意（Allegory of Rome）](../../../04-knowledge/units/works/valentin-allegory-of-rome.md) |
| FM-P01.site1 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P02a.creator1 | 复用并更新 | [卡拉瓦乔（Caravaggio）](../../../04-knowledge/units/persons/caravaggio.md) |
| FM-P02a.object | 新建 | [马费奥·巴贝里尼肖像（Maffeo Barberini）](../../../04-knowledge/units/works/caravaggio-maffeo-barberini.md) |
| FM-P02a.site1 | 复用并更新 | [佛罗伦萨（Florence）](../../../04-knowledge/units/places/florence.md) |
| FM-P02a.subject1 | 复用并更新 | [乌尔班八世（Urban VIII）](../../../04-knowledge/units/persons/urbano-viii.md) |
| FM-P02b.creator1 | 复用并更新 | [吉安·洛伦佐·贝尔尼尼（Gian Lorenzo Bernini）](../../../04-knowledge/units/persons/gian-lorenzo-bernini.md) |
| FM-P02b.object | 新建 | [乌尔班八世肖像（Maffeo Barberini as Pope Urban VIII）](../../../04-knowledge/units/works/bernini-maffeo-barberini-as-pope-urban-viii.md) |
| FM-P02b.site1 | 新建 | [保守宫（Palazzo dei Conservatori）](../../../04-knowledge/units/places/palazzo-dei-conservatori.md) |
| FM-P02b.site2 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P02b.subject1 | 复用并更新 | [乌尔班八世（Urban VIII）](../../../04-knowledge/units/persons/urbano-viii.md) |
| FM-P03a.creator1 | 新建 | [奥塔维奥·莱奥尼（Ottavio Leoni）](../../../04-knowledge/units/persons/ottavio-leoni.md) |
| FM-P03a.object | 新建 | [弗朗切斯科·巴贝里尼枢机（Cardinal Francesco Barberini）](../../../04-knowledge/units/works/ottavio-leoni-cardinal-francesco-barberini.md) |
| FM-P03a.subject1 | 复用并更新 | [弗朗切斯科·巴贝里尼（Francesco Barberini）](../../../04-knowledge/units/persons/francesco-barberini.md) |
| FM-P03b.creator1 | 复用并更新 | [卡洛·马拉塔（Carlo Maratta）](../../../04-knowledge/units/persons/carlo-maratta.md) |
| FM-P03b.object | 新建 | [安东尼奥·巴贝里尼枢机（Cardinal Antonio Barberini）](../../../04-knowledge/units/works/carlo-maratta-cardinal-antonio-barberini.md) |
| FM-P03b.site1 | 新建 | [阿尼克城堡（Alnwick Castle）](../../../04-knowledge/units/places/alnwick-castle.md) |
| FM-P03b.subject1 | 复用并更新 | [安东尼奥·巴贝里尼（Antonio Barberini）](../../../04-knowledge/units/persons/antonio-barberini.md) |
| FM-P04a.creator1 | 新建 | [范·戴克（Van Dyck）](../../../04-knowledge/units/persons/van-dyck.md) |
| FM-P04a.object | 新建 | [本蒂沃利奥枢机肖像（Portrait of Cardinal Bentivoglio）](../../../04-knowledge/units/works/van-dyck-cardinal-bentivoglio.md) |
| FM-P04a.site1 | 新建 | [皮蒂宫（Palazzo Pitti）](../../../04-knowledge/units/places/palazzo-pitti.md) |
| FM-P04a.site2 | 复用并更新 | [佛罗伦萨（Florence）](../../../04-knowledge/units/places/florence.md) |
| FM-P04a.subject1 | 新建 | [本蒂沃利奥枢机（Cardinal Bentivoglio）](../../../04-knowledge/units/persons/cardinal-bentivoglio.md) |
| FM-P04b.creator1 | 复用并更新 | [皮耶特罗·达·科尔托纳（Pietro da Cortona）](../../../04-knowledge/units/persons/pietro-da-cortona.md) |
| FM-P04b.object | 新建 | [马尔切洛·萨凯蒂肖像（Portrait of Marcello Sacchetti）](../../../04-knowledge/units/works/pietro-da-cortona-marcello-sacchetti.md) |
| FM-P04b.site1 | 新建 | [博尔盖塞别墅（Villa Borghese）](../../../04-knowledge/units/places/villa-borghese.md) |
| FM-P04b.site2 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P04b.subject1 | 复用并更新 | [马尔切洛·萨凯蒂（Marcello Sacchetti）](../../../04-knowledge/units/persons/marcello-sacchetti.md) |
| FM-P05.creator1 | 复用并更新 | [吉安·洛伦佐·贝尔尼尼（Gian Lorenzo Bernini）](../../../04-knowledge/units/persons/gian-lorenzo-bernini.md) |
| FM-P05.object | 暂缓 | 图版未说明两件Scipione胸像中的哪一件；既有卡也未裁定版本，保留候选而不合并或造重复卡。 候选：[贝尔尼尼的博尔盖塞枢机肖像头部（Bernini’s portrait head of Cardinal Borghese）](../../../04-knowledge/units/works/bernini-cardinal-borghese-head.md) |
| FM-P05.site1 | 新建 | [博尔盖塞别墅（Villa Borghese）](../../../04-knowledge/units/places/villa-borghese.md) |
| FM-P05.site2 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P05.subject1 | 复用并更新 | [希皮奥内·博尔盖塞枢机（Cardinal Scipione Borghese）](../../../04-knowledge/units/persons/cardinal-borghese-ch1.md) |
| FM-P06.creator1 | 新建 | [古列尔莫·鲍尔（Guglielmo Baur）](../../../04-knowledge/units/persons/guglielmo-baur.md) |
| FM-P06.depicted1 | 新建 | [博尔盖塞别墅（Villa Borghese）](../../../04-knowledge/units/places/villa-borghese.md) |
| FM-P06.object | 新建 | [1630年博尔盖塞别墅景观（View of Villa Borghese in 1630）](../../../04-knowledge/units/works/guglielmo-baur-view-of-villa-borghese-in-1630.md) |
| FM-P06.site1 | 新建 | [博尔盖塞别墅（Villa Borghese）](../../../04-knowledge/units/places/villa-borghese.md) |
| FM-P06.site2 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P07.creator1 | 复用并更新 | [多梅尼科·赞皮耶里（Domenico Zampieri）](../../../04-knowledge/units/persons/domenichino.md) |
| FM-P07.object | 新建 | [狄安娜狩猎（Hunt of Diana）](../../../04-knowledge/units/works/domenichino-hunt-of-diana.md) |
| FM-P07.site1 | 新建 | [博尔盖塞别墅（Villa Borghese）](../../../04-knowledge/units/places/villa-borghese.md) |
| FM-P07.site2 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P08.creator1 | 新建 | [马泰奥·卡斯泰利（Matteo Castelli）](../../../04-knowledge/units/persons/matteo-castelli.md) |
| FM-P08.object | 新建 | [谷地圣安德烈堂巴贝里尼礼拜堂（Barberini Chapel）](../../../04-knowledge/units/places/barberini-chapel-sant-andrea-valle.md) |
| FM-P08.part1 | 复用并更新 | [谷地圣安德烈堂（S. Andrea della Valle）](../../../04-knowledge/units/places/sant-andrea-della-valle.md) |
| FM-P08.site1 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P09.author1 | 新建 | [吉罗拉莫·泰蒂（Girolamo Teti）](../../../04-knowledge/units/persons/girolamo-teti.md) |
| FM-P09.carrier1 | 新建 | [奎里纳尔山的巴贝里尼宫（Aedes Barberinae ad Quirinalem）](../../../04-knowledge/units/archives/aedes-barberinae-ad-quirinalem.md) |
| FM-P09.creator1 | 新建 | [圭多·阿巴蒂尼（Guido Abbatini）](../../../04-knowledge/units/persons/guido-abbatini.md) |
| FM-P09.depicted1 | 复用并更新 | [巴贝里尼宫（Palazzo Barberini）](../../../04-knowledge/units/places/palazzo-barberini.md) |
| FM-P09.object | 新建 | [《巴贝里尼宫》卷首图（Frontispiece of Aedes Barberinae ad Quirinalem）](../../../04-knowledge/units/works/guido-abbatini-frontispiece-of-aedes-barberinae-ad-quirinalem.md) |
| FM-P09.publication_place1 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P10a.creator1 | 复用并更新 | [皮耶特罗·达·科尔托纳（Pietro da Cortona）](../../../04-knowledge/units/persons/pietro-da-cortona.md) |
| FM-P10a.holder1 | 新建 | [卡比托利欧绘画馆（Pinacoteca Capitolina）](../../../04-knowledge/units/institutions/pinacoteca-capitolina.md) |
| FM-P10a.object | 新建 | [劫夺萨宾妇女（Rape of the Sabines）](../../../04-knowledge/units/works/pietro-da-cortona-rape-of-the-sabines.md) |
| FM-P10a.site1 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P10b.creator1 | 复用并更新 | [皮耶特罗·达·科尔托纳（Pietro da Cortona）](../../../04-knowledge/units/persons/pietro-da-cortona.md) |
| FM-P10b.holder1 | 新建 | [罗马市美术委员办公室（Ufficio dell'Assessore Comunale alle Belle Arti）](../../../04-knowledge/units/institutions/ufficio-dell-assessore-comunale-alle-belle-arti.md) |
| FM-P10b.object | 新建 | [劫夺海伦（Rape of Helen）](../../../04-knowledge/units/works/pietro-da-cortona-rape-of-helen.md) |
| FM-P10b.site1 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P11a.creator1 | 新建 | [乔·马里亚·博塔拉（Gio. Maria Bottalla）](../../../04-knowledge/units/persons/gio-maria-bottalla.md) |
| FM-P11a.holder1 | 新建 | [卡比托利欧绘画馆（Pinacoteca Capitolina）](../../../04-knowledge/units/institutions/pinacoteca-capitolina.md) |
| FM-P11a.object | 新建 | [以扫与雅各相会（Meeting of Esau and Jacob）](../../../04-knowledge/units/works/gio-maria-bottalla-meeting-of-esau-and-jacob.md) |
| FM-P11a.site1 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P11b.creator1 | 新建 | [皮埃特罗·泰斯塔（Pietro Testa）](../../../04-knowledge/units/persons/pietro-testa.md) |
| FM-P11b.holder1 | 新建 | [卡比托利欧绘画馆（Pinacoteca Capitolina）](../../../04-knowledge/units/institutions/pinacoteca-capitolina.md) |
| FM-P11b.object | 新建 | [约瑟被兄弟出卖（Joseph Sold by his Brothers）](../../../04-knowledge/units/works/pietro-testa-joseph-sold-by-his-brothers.md) |
| FM-P11b.site1 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P12.creator1 | 复用并更新 | [安德烈亚·萨基（Andrea Sacchi）](../../../04-knowledge/units/persons/andrea-sacchi.md) |
| FM-P12.object | 新建 | [神圣智慧寓意（Allegory of Divine Wisdom）](../../../04-knowledge/units/works/andrea-sacchi-allegory-of-divine-wisdom.md) |
| FM-P12.site1 | 复用并更新 | [巴贝里尼宫（Palazzo Barberini）](../../../04-knowledge/units/places/palazzo-barberini.md) |
| FM-P12.site2 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P13.creator1 | 复用并更新 | [皮耶特罗·达·科尔托纳（Pietro da Cortona）](../../../04-knowledge/units/persons/pietro-da-cortona.md) |
| FM-P13.object | 新建 | [乌尔班八世统治的荣耀（Glorification of the Reign of Urban VIII）](../../../04-knowledge/units/works/pietro-da-cortona-glorification-of-the-reign-of-urban-viii.md) |
| FM-P13.site1 | 复用并更新 | [巴贝里尼宫（Palazzo Barberini）](../../../04-knowledge/units/places/palazzo-barberini.md) |
| FM-P13.site2 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P13.subject1 | 复用并更新 | [乌尔班八世（Urban VIII）](../../../04-knowledge/units/persons/urbano-viii.md) |
| FM-P14.creator1 | 复用并更新 | [乔万尼·巴蒂斯塔·盖乌利（Giovanni Battista Gaulli）](../../../04-knowledge/units/persons/giovan-battista-gaulli.md) |
| FM-P14.object | 新建 | [耶稣圣名的胜利（Triumph of The Name of Jesus）](../../../04-knowledge/units/works/gaulli-triumph-name-jesus.md) |
| FM-P14.site1 | 复用并更新 | [罗马耶稣堂（Gesù, Rome）](../../../04-knowledge/units/places/gesu-rome.md) |
| FM-P14.site2 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P15.creator1 | 复用并更新 | [安德烈亚·波佐（Andrea Pozzo）](../../../04-knowledge/units/persons/andrea-pozzo.md) |
| FM-P15.design_site1 | 新建 | [圣依纳爵堂（罗马）（S. Ignazio）](../../../04-knowledge/units/places/s-ignazio.md) |
| FM-P15.object | 新建 | [圣依纳爵堂拱顶壁画模型（Modello for fresco on vault of S. Ignazio）](../../../04-knowledge/units/works/andrea-pozzo-modello-for-fresco-on-vault-of-s-ignazio.md) |
| FM-P15.site1 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P16.creator1 | 复用并更新 | [吉安·洛伦佐·贝尔尼尼（Gian Lorenzo Bernini）](../../../04-knowledge/units/persons/gian-lorenzo-bernini.md) |
| FM-P16.object | 新建 | [奎里纳尔圣安德烈堂内部（Interior of S. Andrea al Quirinale）](../../../04-knowledge/units/places/interior-sant-andrea-quirinale.md) |
| FM-P16.part1 | 新建 | [奎里纳尔圣安德烈堂（S. Andrea al Quirinale）](../../../04-knowledge/units/places/s-andrea-al-quirinale.md) |
| FM-P16.site1 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P17a.creator1 | 复用并更新 | [吉安·洛伦佐·贝尔尼尼（Gian Lorenzo Bernini）](../../../04-knowledge/units/persons/gian-lorenzo-bernini.md) |
| FM-P17a.holder1 | 新建 | [博伊曼斯—范伯宁恩博物馆（Museum Boymans–van Beuningen）](../../../04-knowledge/units/institutions/museum-boymansvan-beuningen.md) |
| FM-P17a.object | 新建 | [卡西亚诺·达尔·波佐漫画（Caricature of Cassiano dal Pozzo）](../../../04-knowledge/units/works/bernini-caricature-of-cassiano-dal-pozzo.md) |
| FM-P17a.site1 | 新建 | [鹿特丹（Rotterdam）](../../../04-knowledge/units/places/rotterdam.md) |
| FM-P17a.subject1 | 新建 | [卡西亚诺·达尔·波佐（Cassiano dal Pozzo）](../../../04-knowledge/units/persons/cassiano-dal-pozzo.md) |
| FM-P17b.creator1 | 新建 | [克洛德·梅朗（Claude Mellan）](../../../04-knowledge/units/persons/claude-mellan.md) |
| FM-P17b.object | 新建 | [文琴佐·朱斯蒂尼亚尼肖像（Portrait of Vincenzo Giustiniani）](../../../04-knowledge/units/works/claude-mellan-vincenzo-giustiniani.md) |
| FM-P17b.subject1 | 复用并更新 | [文琴佐·朱斯蒂尼亚尼（Vincenzo Giustiniani）](../../../04-knowledge/units/persons/marchese-giustiniani-ch1.md) |
| FM-P17c.creator1 | 新建 | [奥塔维奥·莱奥尼（Ottavio Leoni）](../../../04-knowledge/units/persons/ottavio-leoni.md) |
| FM-P17c.object | 新建 | [布拉恰诺公爵（Paolo Giordano Orsini, Duke of Bracciano）](../../../04-knowledge/units/works/ottavio-leoni-paolo-giordano-orsini-duke-of-bracciano.md) |
| FM-P17c.subject1 | 新建 | [保罗·乔尔达诺·奥尔西尼（Paolo Giordano Orsini）](../../../04-knowledge/units/persons/paolo-giordano-orsini.md) |
| FM-P18a.creator1 | 新建 | [皮埃特罗·泰斯塔（Pietro Testa）](../../../04-knowledge/units/persons/pietro-testa.md) |
| FM-P18a.depicted1 | 新建 | [埃及（Egypt）](../../../04-knowledge/units/places/egypt.md) |
| FM-P18a.object | 新建 | [逃往埃及途中的休息（Rest on the Flight into Egypt）](../../../04-knowledge/units/works/pietro-testa-rest-on-the-flight-into-egypt.md) |
| FM-P18b.creator1 | 复用并更新 | [尼古拉·普桑（Nicolas Poussin）](../../../04-knowledge/units/persons/nicolas-poussin.md) |
| FM-P18b.object | 新建 | [婚姻（Marriage）](../../../04-knowledge/units/works/poussin-marriage.md) |
| FM-P18b.site1 | 新建 | [贝尔沃城堡（Belvoir Castle）](../../../04-knowledge/units/places/belvoir-castle.md) |
| FM-P19a.creator1 | 复用并更新 | [尼古拉·普桑（Nicolas Poussin）](../../../04-knowledge/units/persons/nicolas-poussin.md) |
| FM-P19a.holder1 | 复用并更新 | [卢浮宫博物馆（Louvre Museum）](../../../04-knowledge/units/institutions/louvre-museum.md) |
| FM-P19a.object | 新建 | [摩西践踏法老王冠（Moses trampling on Pharaoh's crown）](../../../04-knowledge/units/works/poussin-moses-trampling-on-pharaoh-s-crown.md) |
| FM-P19b.creator1 | 复用并更新 | [克劳德·洛兰（Claude Lorrain）](../../../04-knowledge/units/persons/claude-lorrain.md) |
| FM-P19b.depicted1 | 新建 | [德尔斐（Delphi）](../../../04-knowledge/units/places/delphi.md) |
| FM-P19b.holder1 | 新建 | [芝加哥艺术博物馆（Art Institute of Chicago）](../../../04-knowledge/units/institutions/art-institute-of-chicago.md) |
| FM-P19b.object | 新建 | [有队列的德尔斐景观（View of Delphi with a Procession）](../../../04-knowledge/units/works/claude-view-of-delphi-with-a-procession.md) |
| FM-P20.creator1 | 新建 | [迭戈·委拉斯开兹（Diego Velázquez）](../../../04-knowledge/units/persons/velasquez.md) |
| FM-P20.holder1 | 新建 | [亨利·约翰·拉尔夫·班克斯（Henry John Ralph Bankes）](../../../04-knowledge/units/persons/ralph-bankes.md) |
| FM-P20.object | 新建 | [卡米洛·马西米肖像（Portrait of Camillo Massimi）](../../../04-knowledge/units/works/velasquez-camillo-massimi.md) |
| FM-P20.site1 | 新建 | [金斯顿莱西庄园（Kingston Lacy）](../../../04-knowledge/units/places/kingston-lacy.md) |
| FM-P20.subject1 | 新建 | [卡米洛·马西米（Camillo Massimi）](../../../04-knowledge/units/persons/camillo-massimi.md) |
| FM-P21a.creator1 | 新建 | [萨索费拉托（Sassoferrato）](../../../04-knowledge/units/persons/sassoferrato.md) |
| FM-P21a.object | 新建 | [玫瑰圣母与道明、加大利纳（Madonna of the Rosary with Saints Dominic and Catherine）](../../../04-knowledge/units/works/sassoferrato-madonna-of-the-rosary-with-saints-dominic-and-catherine.md) |
| FM-P21a.site1 | 新建 | [圣撒比纳堂（罗马）（S. Sabina）](../../../04-knowledge/units/places/s-sabina.md) |
| FM-P21a.site2 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P21b.creator1 | 新建 | [萨索费拉托（Sassoferrato）](../../../04-knowledge/units/persons/sassoferrato.md) |
| FM-P21b.object | 新建 | [圣母子（Madonna and Child）](../../../04-knowledge/units/works/sassoferrato-madonna-and-child.md) |
| FM-P21b.site1 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P22a.creator1 | 复用并更新 | [米开朗基罗·切尔阔齐（Michelangelo Cerquozzi）](../../../04-knowledge/units/persons/michelangelo-cerquozzi.md) |
| FM-P22a.holder1 | 新建 | [卡塞尔艺术收藏机构（Kunstsammlungen, Kassel）](../../../04-knowledge/units/institutions/kunstsammlungen-kassel.md) |
| FM-P22a.object | 新建 | [画家及友人群像（The artist with a group of friends）](../../../04-knowledge/units/works/michelangelo-cerquozzi-the-artist-with-a-group-of-friends.md) |
| FM-P22a.self1 | 复用并更新 | [米开朗基罗·切尔阔齐（Michelangelo Cerquozzi）](../../../04-knowledge/units/persons/michelangelo-cerquozzi.md) |
| FM-P22a.site1 | 新建 | [卡塞尔（Kassel）](../../../04-knowledge/units/places/kassel.md) |
| FM-P22b.creator1 | 复用并更新 | [米开朗基罗·切尔阔齐（Michelangelo Cerquozzi）](../../../04-knowledge/units/persons/michelangelo-cerquozzi.md) |
| FM-P22b.holder1 | 新建 | [斯帕达美术馆（Galleria Spada）](../../../04-knowledge/units/institutions/galleria-spada.md) |
| FM-P22b.object | 新建 | [马萨涅洛起义（The Revolt of Masaniello）](../../../04-knowledge/units/works/michelangelo-cerquozzi-the-revolt-of-masaniello.md) |
| FM-P22b.site1 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P23a.creator1 | 复用并更新 | [米开朗基罗·切尔阔齐（Michelangelo Cerquozzi）](../../../04-knowledge/units/persons/michelangelo-cerquozzi.md) |
| FM-P23a.object | 新建 | [女浴（Women's Bath）](../../../04-knowledge/units/works/michelangelo-cerquozzi-women-s-bath.md) |
| FM-P23a.site1 | 复用并更新 | [罗马（Rome）](../../../04-knowledge/units/places/rome.md) |
| FM-P23b.creator1 | 复用并更新 | [萨尔瓦多·罗萨（Salvator Rosa）](../../../04-knowledge/units/persons/salvator-rosa.md) |
| FM-P23b.holder1 | 新建 | [弗吉尼亚美术馆（Virginia Museum of Fine Arts）](../../../04-knowledge/units/institutions/virginia-museum-of-fine-arts.md) |
| FM-P23b.object | 新建 | [雷古鲁斯之死（The Death of Regulus）](../../../04-knowledge/units/works/salvator-rosa-the-death-of-regulus.md) |
| FM-P24.creator1 | 复用并更新 | [萨尔瓦多·罗萨（Salvator Rosa）](../../../04-knowledge/units/persons/salvator-rosa.md) |
| FM-P24.object | 原位整理后接收 | [罗萨命运（Fortune by Salvator Rosa）](../../../04-knowledge/units/works/fortune-salvator-rosa.md) |
| FM-P25.creator1 | 新建 | [奥拉齐奥·真蒂莱斯基（Orazio Gentileschi）](../../../04-knowledge/units/persons/orazio-gentileschi.md) |
| FM-P25.holder1 | 复用并更新 | [卢浮宫博物馆（Louvre Museum）](../../../04-knowledge/units/institutions/louvre-museum.md) |
| FM-P25.object | 新建 | [公共幸福战胜危难（Public Felicity triumphant over Dangers）](../../../04-knowledge/units/works/orazio-gentileschi-public-felicity-triumphant-over-dangers.md) |
| FM-P26a.creator1 | 新建 | [南特伊（Nanteuil）](../../../04-knowledge/units/persons/nanteuil.md) |
| FM-P26a.object | 新建 | [画廊中的马扎然（Cardinal Mazarin in his Gallery）](../../../04-knowledge/units/works/nanteuil-cardinal-mazarin-in-his-gallery.md) |
| FM-P26a.subject1 | 新建 | [马扎然（Mazarin）](../../../04-knowledge/units/persons/mazarin.md) |
| FM-P26b.creator1 | 新建 | [罗马内利（Romanelli）](../../../04-knowledge/units/persons/romanelli.md) |
| FM-P26b.former_name1 | 新建 | [马扎然宫（Palais Mazarin）](../../../04-knowledge/units/places/palais-mazarin.md) |
| FM-P26b.holder1 | 新建 | [法国国家图书馆（Bibliothèque Nationale）](../../../04-knowledge/units/institutions/bibliotheque-nationale.md) |
| FM-P26b.object | 新建 | [罗慕路斯与雷穆斯顶画局部（Romulus and Remus）](../../../04-knowledge/units/works/romanelli-romulus-and-remus.md) |
| FM-P27a.creator1 | 新建 | [弗朗切斯科·法内利（Francesco Fanelli）](../../../04-knowledge/units/persons/francesco-fanelli.md) |
| FM-P27a.holder1 | 新建 | [达芙妮·伊奥尼德斯（Daphne Ionides）](../../../04-knowledge/units/persons/daphne-ionides.md) |
| FM-P27a.object | 新建 | [查理一世肖像（Portrait of Charles I）](../../../04-knowledge/units/works/francesco-fanelli-charles-i.md) |
| FM-P27a.site1 | 复用并更新 | [伦敦（London）](../../../04-knowledge/units/places/london.md) |
| FM-P27a.subject1 | 新建 | [查理一世（Charles I）](../../../04-knowledge/units/persons/charles-i.md) |
| FM-P27b.creator1 | 复用并更新 | [吉安·洛伦佐·贝尔尼尼（Gian Lorenzo Bernini）](../../../04-knowledge/units/persons/gian-lorenzo-bernini.md) |
| FM-P27b.object | 新建 | [路易十四肖像（Portrait of Louis XIV）](../../../04-knowledge/units/works/bernini-louis-xiv.md) |
| FM-P27b.site1 | 新建 | [凡尔赛（Versailles）](../../../04-knowledge/units/places/versailles.md) |
| FM-P27b.subject1 | 新建 | [路易十四（Louis XIV）](../../../04-knowledge/units/persons/louis-xiv.md) |
| FM-P28a.creator1 | 新建 | [圭多·卡尼亚奇（Guido Cagnacci）](../../../04-knowledge/units/persons/guido-cagnacci.md) |
| FM-P28a.holder1 | 复用并更新 | [维也纳艺术史博物馆（Kunsthistorisches Museum）](../../../04-knowledge/units/institutions/kunsthistorisches-museum.md) |
| FM-P28a.object | 新建 | [克娄巴特拉之死（Death of Cleopatra）](../../../04-knowledge/units/works/guido-cagnacci-death-of-cleopatra.md) |
| FM-P28a.site1 | 新建 | [维也纳（Vienna）](../../../04-knowledge/units/places/vienna.md) |
| FM-P28b.creator1 | 新建 | [布尔纳奇尼（Burnacini）](../../../04-knowledge/units/persons/burnacini.md) |
| FM-P28b.derived1 | 新建 | [拉丁君权凯旋（La Monarchia Latina Trionfante）](../../../04-knowledge/units/works/la-monarchia-latina-trionfante.md) |
| FM-P28b.object | 新建 | [歌剧《拉丁君权凯旋》的极乐世界（The Elysian Fields）](../../../04-knowledge/units/works/burnacini-the-elysian-fields.md) |
| FM-P28b.performance_place1 | 新建 | [维也纳（Vienna）](../../../04-knowledge/units/places/vienna.md) |
| FM-P29.creator1 | 新建 | [安东尼奥·韦里奥（Antonio Verrio）](../../../04-knowledge/units/persons/antonio-verrio.md) |
| FM-P29.object | 新建 | [汉普顿宫楼梯壁画（Fresco on staircase of Hampton Court Palace）](../../../04-knowledge/units/works/antonio-verrio-fresco-on-staircase-of-hampton-court-palace.md) |
| FM-P29.site1 | 新建 | [汉普顿宫（Hampton Court Palace）](../../../04-knowledge/units/places/hampton-court-palace.md) |
| FM-P30a.creator1 | 新建 | [马西莫·斯坦齐奥内（Massimo Stanzione）](../../../04-knowledge/units/persons/massimo-stanzione.md) |
| FM-P30a.holder1 | 新建 | [亨利·约翰·拉尔夫·班克斯（Henry John Ralph Bankes）](../../../04-knowledge/units/persons/ralph-bankes.md) |
| FM-P30a.object | 新建 | [杰罗姆·班克斯肖像（Portrait of Jerome Bankes）](../../../04-knowledge/units/works/massimo-stanzione-jerome-bankes.md) |
| FM-P30a.site1 | 新建 | [金斯顿莱西庄园（Kingston Lacy）](../../../04-knowledge/units/places/kingston-lacy.md) |
| FM-P30a.subject1 | 新建 | [杰罗姆·班克斯（Jerome Bankes）](../../../04-knowledge/units/persons/jerome-bankes.md) |
| FM-P30b.creator1 | 新建 | [卡洛·多尔奇（Carlo Dolci）](../../../04-knowledge/units/persons/carlo-dolci.md) |
| FM-P30b.holder1 | 新建 | [菲茨威廉博物馆（Fitzwilliam Museum）](../../../04-knowledge/units/institutions/fitzwilliam-museum.md) |
| FM-P30b.object | 新建 | [托马斯·贝恩斯（Sir Thomas Baines）](../../../04-knowledge/units/works/carlo-dolci-sir-thomas-baines.md) |
| FM-P30b.site1 | 新建 | [剑桥（Cambridge）](../../../04-knowledge/units/places/cambridge.md) |
| FM-P30b.subject1 | 新建 | [托马斯·贝恩斯（Thomas Baines）](../../../04-knowledge/units/persons/thomas-baines.md) |
| FM-P31a.creator1 | 复用并更新 | [卡洛·马拉塔（Carlo Maratta）](../../../04-knowledge/units/persons/carlo-maratta.md) |
| FM-P31a.object | 新建 | [查尔斯·福克斯肖像（Portrait of Charles Fox）](../../../04-knowledge/units/works/carlo-maratta-charles-fox.md) |
| FM-P31a.subject1 | 新建 | [查尔斯·福克斯（Charles Fox）](../../../04-knowledge/units/persons/charles-fox.md) |
| FM-P31b.creator1 | 复用并更新 | [卡洛·马拉塔（Carlo Maratta）](../../../04-knowledge/units/persons/carlo-maratta.md) |
| FM-P31b.holder1 | 已登记后对齐 | [盖尔斯·伊舍姆（Gyles Isham）](../../../04-knowledge/units/persons/gyles-isham.md)；第十二代从男爵，历史收藏者；见REV-089。 |
| FM-P31b.object | 新建 | [托马斯·伊舍姆（Sir Thomas Isham）](../../../04-knowledge/units/works/carlo-maratta-sir-thomas-isham.md) |
| FM-P31b.site1 | 新建 | [兰波特庄园（Lamport Hall）](../../../04-knowledge/units/places/lamport-hall.md) |
| FM-P31b.subject1 | 新建 | [托马斯·伊舍姆（Thomas Isham）](../../../04-knowledge/units/persons/thomas-isham.md) |
| FM-P32a.creator1 | 新建 | [里贝拉（Ribera）](../../../04-knowledge/units/persons/ribera.md) |
| FM-P32a.holder1 | 新建 | [卡波迪蒙特博物馆（Museo di Capodimonte）](../../../04-knowledge/units/institutions/museo-di-capodimonte.md) |
| FM-P32a.object | 新建 | [醉西勒诺斯（The drunken Silenus）](../../../04-knowledge/units/works/ribera-the-drunken-silenus.md) |
| FM-P32a.site1 | 复用并更新 | [那不勒斯（Naples）](../../../04-knowledge/units/places/naples.md) |
| FM-P32b.creator1 | 新建 | [保罗·德·马泰伊斯（Paolo de Matteis）](../../../04-knowledge/units/persons/paolo-de-matteis.md) |
| FM-P32b.object | 新建 | [赫拉克勒斯的选择（The choice of Hercules）](../../../04-knowledge/units/works/paolo-de-matteis-the-choice-of-hercules.md) |
| FM-P32b.site1 | 新建 | [坦普尔纽萨姆庄园（Temple Newsam）](../../../04-knowledge/units/places/temple-newsam.md) |
| FM-P32b.site2 | 新建 | [利兹（Leeds）](../../../04-knowledge/units/places/leeds.md) |
| FM-P33a.creator1 | 新建 | [弗朗切斯科·索利梅纳（Francesco Solimena）](../../../04-knowledge/units/persons/solimena.md) |
| FM-P33a.former_site1 | 新建 | [布奥纳科尔西宫（Palazzo Buonaccorsi）](../../../04-knowledge/units/places/palazzo-buonaccorsi.md) |
| FM-P33a.former_site2 | 新建 | [马切拉塔（Macerata）](../../../04-knowledge/units/places/macerata.md) |
| FM-P33a.object | 新建 | [狄多与埃涅阿斯（Dido and Aeneas）](../../../04-knowledge/units/works/solimena-dido-and-aeneas.md) |
| FM-P33b.object | 新建 | [布奥纳科尔西宫画廊（Gallery of Palazzo Buonaccorsi）](../../../04-knowledge/units/places/gallery-palazzo-buonaccorsi.md) |
| FM-P33b.part1 | 新建 | [布奥纳科尔西宫（Palazzo Buonaccorsi）](../../../04-knowledge/units/places/palazzo-buonaccorsi.md) |
| FM-P33b.site1 | 新建 | [马切拉塔（Macerata）](../../../04-knowledge/units/places/macerata.md) |
| FM-P34.creator1 | 新建 | [迭戈·委拉斯开兹（Diego Velázquez）](../../../04-knowledge/units/persons/velasquez.md) |
| FM-P34.holder1 | 复用并更新 | [大都会艺术博物馆（Metropolitan Museum of Art）](../../../04-knowledge/units/institutions/metropolitan-museum-of-art.md) |
| FM-P34.object | 新建 | [胡安·德·帕雷哈肖像（Portrait of Juan de Pareja）](../../../04-knowledge/units/works/velasquez-juan-de-pareja.md) |
| FM-P34.site1 | 新建 | [纽约（New York）](../../../04-knowledge/units/places/new-york.md) |
| FM-P34.subject1 | 新建 | [胡安·德·帕雷哈（Juan de Pareja）](../../../04-knowledge/units/persons/juan-de-pareja.md) |
| FM-P35a.creator1 | 复用并更新 | [伦勃朗（Rembrandt）](../../../04-knowledge/units/persons/rembrandt.md) |
| FM-P35a.holder1 | 复用并更新 | [大都会艺术博物馆（Metropolitan Museum of Art）](../../../04-knowledge/units/institutions/metropolitan-museum-of-art.md) |
| FM-P35a.object | 新建 | [凝视荷马像的亚里士多德（Aristotle contemplating the bust of Homer）](../../../04-knowledge/units/works/rembrandt-aristotle-contemplating-the-bust-of-homer.md) |
| FM-P35a.site1 | 新建 | [纽约（New York）](../../../04-knowledge/units/places/new-york.md) |
| FM-P35a.subject1 | 新建 | [亚里士多德（Aristotle）](../../../04-knowledge/units/persons/aristotle.md) |
| FM-P35a.subject2 | 新建 | [荷马（Homer）](../../../04-knowledge/units/persons/homer.md) |
| FM-P35b.creator1 | 复用并更新 | [鲁本斯（Rubens）](../../../04-knowledge/units/persons/peter-paul-rubens.md) |
| FM-P35b.holder1 | 新建 | [苏格兰国家美术馆（National Gallery of Scotland）](../../../04-knowledge/units/institutions/national-gallery-of-scotland.md) |
| FM-P35b.object | 新建 | [希律王宴会（The Feast of Herod）](../../../04-knowledge/units/works/rubens-the-feast-of-herod.md) |
| FM-P36a.creator1 | 新建 | [弗朗切斯科·彼得鲁奇（Francesco Petrucci）](../../../04-knowledge/units/persons/francesco-petrucci.md) |
| FM-P36a.object | 新建 | [托斯卡纳大公子费迪南多肖像（Portrait of Grand Prince Ferdinand of Tuscany）](../../../04-knowledge/units/works/francesco-petrucci-grand-prince-ferdinand-of-tuscany.md) |
| FM-P36a.subject1 | 新建 | [托斯卡纳大公子费迪南多（Grand Prince Ferdinand of Tuscany）](../../../04-knowledge/units/persons/ferdinand-grand-prince-tuscany.md) |
| FM-P36b.creator1 | 原位整理后接收 | [朱塞佩·马里亚·克雷斯皮（Giuseppe Maria Crespi）](../../../04-knowledge/units/persons/giuseppe-maria-crespi.md) |
| FM-P36b.holder1 | 复用并更新 | [乌菲齐美术馆（Uffizi Gallery）](../../../04-knowledge/units/institutions/uffizi-gallery.md) |
| FM-P36b.object | 新建 | [梳妆少女（Girl at her toilet）](../../../04-knowledge/units/works/g-m-crespi-girl-at-her-toilet.md) |
| FM-P36b.site1 | 复用并更新 | [佛罗伦萨（Florence）](../../../04-knowledge/units/places/florence.md) |
| FM-P37a.creator1 | 原位整理后接收 | [朱塞佩·马里亚·克雷斯皮（Giuseppe Maria Crespi）](../../../04-knowledge/units/persons/giuseppe-maria-crespi.md) |
| FM-P37a.holder1 | 复用并更新 | [乌菲齐美术馆（Uffizi Gallery）](../../../04-knowledge/units/institutions/uffizi-gallery.md) |
| FM-P37a.object | 新建 | [画家一家（The Painter's Family）](../../../04-knowledge/units/works/g-m-crespi-the-painter-s-family.md) |
| FM-P37a.site1 | 复用并更新 | [佛罗伦萨（Florence）](../../../04-knowledge/units/places/florence.md) |
| FM-P37b.creator1 | 原位整理后接收 | [朱塞佩·马里亚·克雷斯皮（Giuseppe Maria Crespi）](../../../04-knowledge/units/persons/giuseppe-maria-crespi.md) |
| FM-P37b.depicted1 | 新建 | [波焦阿卡亚诺（Poggio a Caiano）](../../../04-knowledge/units/places/poggio-a-caiano.md) |
| FM-P37b.holder1 | 复用并更新 | [乌菲齐美术馆（Uffizi Gallery）](../../../04-knowledge/units/institutions/uffizi-gallery.md) |
| FM-P37b.object | 新建 | [波焦阿卡亚诺集市局部（Detail from Fair at Poggio a Caiano）](../../../04-knowledge/units/works/g-m-crespi-detail-from-fair-at-poggio-a-caiano.md) |
| FM-P37b.site1 | 复用并更新 | [佛罗伦萨（Florence）](../../../04-knowledge/units/places/florence.md) |
| FM-P37c.creator1 | 新建 | [巴尔达萨雷·弗兰切斯基尼（Baldassare Franceschini）](../../../04-knowledge/units/persons/baldassare-franceschini.md) |
| FM-P37c.holder1 | 复用并更新 | [乌菲齐美术馆（Uffizi Gallery）](../../../04-knowledge/units/institutions/uffizi-gallery.md) |
| FM-P37c.object | 新建 | [阿尔洛托教区神父的玩笑（La Burla del Piovano Arlotto）](../../../04-knowledge/units/works/baldassare-franceschini-la-burla-del-piovano-arlotto.md) |
| FM-P37c.site1 | 复用并更新 | [佛罗伦萨（Florence）](../../../04-knowledge/units/places/florence.md) |
| FM-P38a.creator1 | 复用并更新 | [塞巴斯蒂亚诺·里奇（Sebastiano Ricci）](../../../04-knowledge/units/persons/sebastiano-ricci.md) |
| FM-P38a.object | 新建 | [劫夺欧罗巴（Rape of Europa）](../../../04-knowledge/units/works/sebastiano-ricci-rape-of-europa.md) |
| FM-P38a.site1 | 新建 | [皮蒂宫（Palazzo Pitti）](../../../04-knowledge/units/places/palazzo-pitti.md) |
| FM-P38a.site2 | 复用并更新 | [佛罗伦萨（Florence）](../../../04-knowledge/units/places/florence.md) |
| FM-P38b.creator1 | 复用并更新 | [塞巴斯蒂亚诺·里奇（Sebastiano Ricci）](../../../04-knowledge/units/persons/sebastiano-ricci.md) |
| FM-P38b.object | 新建 | [潘与绪任克斯（Pan and Syrinx）](../../../04-knowledge/units/works/sebastiano-ricci-pan-and-syrinx.md) |
| FM-P38b.site1 | 新建 | [皮蒂宫（Palazzo Pitti）](../../../04-knowledge/units/places/palazzo-pitti.md) |
| FM-P38b.site2 | 复用并更新 | [佛罗伦萨（Florence）](../../../04-knowledge/units/places/florence.md) |
| FM-P39.creator1 | 复用并更新 | [塞巴斯蒂亚诺·里奇（Sebastiano Ricci）](../../../04-knowledge/units/persons/sebastiano-ricci.md) |
| FM-P39.object | 新建 | [维纳斯与阿多尼斯（Venus and Adonis）](../../../04-knowledge/units/works/sebastiano-ricci-venus-and-adonis.md) |
| FM-P39.site1 | 新建 | [皮蒂宫（Palazzo Pitti）](../../../04-knowledge/units/places/palazzo-pitti.md) |
| FM-P39.site2 | 复用并更新 | [佛罗伦萨（Florence）](../../../04-knowledge/units/places/florence.md) |
| FM-P40a.creator1 | 新建 | [A. D. 加比亚尼（A. D. Gabbiani）](../../../04-knowledge/units/persons/a-d-gabbiani.md) |
| FM-P40a.object | 新建 | [乐师群像（A Group of Musicians）](../../../04-knowledge/units/works/a-d-gabbiani-a-group-of-musicians.md) |
| FM-P40a.site1 | 新建 | [皮蒂宫（Palazzo Pitti）](../../../04-knowledge/units/places/palazzo-pitti.md) |
| FM-P40a.site2 | 复用并更新 | [佛罗伦萨（Florence）](../../../04-knowledge/units/places/florence.md) |
| FM-P40b.creator1 | 新建 | [詹安东尼奥·富米亚尼（GiannAntonio Fumiani）](../../../04-knowledge/units/persons/giannantonio-fumiani.md) |
| FM-P40b.holder1 | 复用并更新 | [乌菲齐美术馆（Uffizi Gallery）](../../../04-knowledge/units/institutions/uffizi-gallery.md) |
| FM-P40b.object | 新建 | [撒迦利亚被石击（The stoning of Zechariah）](../../../04-knowledge/units/works/giannantonio-fumiani-the-stoning-of-zechariah.md) |
| FM-P40b.site1 | 复用并更新 | [佛罗伦萨（Florence）](../../../04-knowledge/units/places/florence.md) |
| FM-P41a.object | 新建 | [百合圣母堂立面（Facade of S. Maria del Giglio）](../../../04-knowledge/units/works/facade-of-s-maria-del-giglio.md) |
| FM-P41a.part1 | 新建 | [百合圣母堂（S. Maria del Giglio）](../../../04-knowledge/units/places/s-maria-del-giglio.md) |
| FM-P41a.site1 | 复用并更新 | [威尼斯（Venice）](../../../04-knowledge/units/places/venice.md) |
| FM-P41b.object | 新建 | [乔瓦尼·佩萨罗总督纪念碑（Monument to Doge Giovanni Pesaro）](../../../04-knowledge/units/works/monument-to-doge-giovanni-pesaro.md) |
| FM-P41b.site1 | 新建 | [弗拉里教堂（Church of the Frari）](../../../04-knowledge/units/places/church-of-the-frari.md) |
| FM-P41b.site2 | 复用并更新 | [威尼斯（Venice）](../../../04-knowledge/units/places/venice.md) |
| FM-P41b.subject1 | 新建 | [乔瓦尼·佩萨罗（Giovanni Pesaro）](../../../04-knowledge/units/persons/giovanni-pesaro.md) |
| FM-P42a.creator1 | 对齐后复用 | [乔万巴蒂斯塔·提埃坡罗（Giambattista Tiepolo）](../../../04-knowledge/units/persons/giambattista-tiepolo.md)；具体角色及依据见REV-087。 |
| FM-P42a.object | 新建 | [海神向威尼斯致敬（Neptune paying homage to Venice）](../../../04-knowledge/units/works/tiepolo-neptune-paying-homage-to-venice.md) |
| FM-P42a.site1 | 新建 | [总督宫（威尼斯）（Palazzo Ducale）](../../../04-knowledge/units/places/palazzo-ducale.md) |
| FM-P42a.site2 | 复用并更新 | [威尼斯（Venice）](../../../04-knowledge/units/places/venice.md) |
| FM-P42b.creator1 | 新建 | [尼科洛·班比尼（Niccolo Bambini）](../../../04-knowledge/units/persons/niccolo-bambini.md) |
| FM-P42b.object | 新建 | [威尼斯寓意（Allegory of Venice）](../../../04-knowledge/units/works/niccolo-bambini-allegory-of-venice.md) |
| FM-P42b.site1 | 新建 | [佩萨罗宫（Ca' Pesaro）](../../../04-knowledge/units/places/ca-pesaro.md) |
| FM-P42b.site2 | 复用并更新 | [威尼斯（Venice）](../../../04-knowledge/units/places/venice.md) |
| FM-P43.creator1 | 对齐后复用 | [乔万巴蒂斯塔·提埃坡罗（Giambattista Tiepolo）](../../../04-knowledge/units/persons/giambattista-tiepolo.md)；具体角色及依据见REV-087。 |
| FM-P43.family1 | 新建 | [雷佐尼科家族（Rezzonico family）](../../../04-knowledge/units/families/rezzonico-family.md) |
| FM-P43.object | 新建 | [雷佐尼科家族婚姻寓意（Marriage Allegory of the Rezzonico family）](../../../04-knowledge/units/works/tiepolo-marriage-allegory-of-the-rezzonico-family.md) |
| FM-P43.site1 | 新建 | [雷佐尼科宫（Ca' Rezzonico）](../../../04-knowledge/units/places/ca-rezzonico.md) |
| FM-P43.site2 | 复用并更新 | [威尼斯（Venice）](../../../04-knowledge/units/places/venice.md) |
| FM-P44.creator1 | 对齐后复用 | [乔万巴蒂斯塔·提埃坡罗（Giambattista Tiepolo）](../../../04-knowledge/units/persons/giambattista-tiepolo.md)；具体角色及依据见REV-087。 |
| FM-P44.family1 | 新建 | [皮萨尼家族（Pisani family）](../../../04-knowledge/units/families/pisani-family.md) |
| FM-P44.object | 新建 | [皮萨尼家族的荣耀（Glorification of the Pisani family）](../../../04-knowledge/units/works/tiepolo-glorification-of-the-pisani-family.md) |
| FM-P44.site1 | 新建 | [皮萨尼别墅（斯特拉）（Villa Pisani）](../../../04-knowledge/units/places/villa-pisani.md) |
| FM-P44.site2 | 新建 | [斯特拉（Stra）](../../../04-knowledge/units/places/stra.md) |
| FM-P45.creator1 | 新建 | [蓬佩奥·巴托尼（Pompeo Batoni）](../../../04-knowledge/units/persons/pompeo-batoni.md) |
| FM-P45.holder1 | 新建 | [北卡罗来纳艺术博物馆（North Carolina Museum of Art）](../../../04-knowledge/units/institutions/north-carolina-museum-of-art.md) |
| FM-P45.object | 新建 | [威尼斯的胜利（The Triumph of Venice）](../../../04-knowledge/units/works/pompeo-batoni-the-triumph-of-venice.md) |
| FM-P45.site1 | 新建 | [罗利（Raleigh）](../../../04-knowledge/units/places/raleigh.md) |
| FM-P46.creator1 | 新建 | [佩莱格里尼（Pellegrini）](../../../04-knowledge/units/persons/pellegrini.md) |
| FM-P46.holder1 | 新建 | [大英博物馆（British Museum）](../../../04-knowledge/units/institutions/british-museum.md) |
| FM-P46.object | 新建 | [皮埃尔·莫特及家人（Pierre Motteux and his family）](../../../04-knowledge/units/works/pellegrini-pierre-motteux-and-his-family.md) |
| FM-P46.subject1 | 新建 | [皮埃尔·莫特（Pierre Motteux）](../../../04-knowledge/units/persons/pierre-motteux.md) |
| FM-P47.creator1 | 新建 | [马尔科·里奇（Marco Ricci）](../../../04-knowledge/units/persons/marco-ricci.md) |
| FM-P47.holder1 | 新建 | [沃特金·威廉斯-温（Watkin Williams-Wynn）](../../../04-knowledge/units/persons/watkin-williams-wynn.md) |
| FM-P47.object | 新建 | [歌剧排练（An Operatic Rehearsal）](../../../04-knowledge/units/works/marco-ricci-an-operatic-rehearsal.md) |
| FM-P47.site1 | 新建 | [圣阿萨夫（St Asaph）](../../../04-knowledge/units/places/st-asaph.md) |
| FM-P48a.creator1 | 新建 | [马尔科·皮泰里（Marco Pitteri）](../../../04-knowledge/units/persons/marco-pitteri.md) |
| FM-P48a.creator2 | 新建 | [朱塞佩·安杰利（Giuseppe Angeli）](../../../04-knowledge/units/persons/giuseppe-angeli.md) |
| FM-P48a.object | 新建 | [弗拉米尼奥·科尔内尔肖像（Portrait of Flaminio Corner）](../../../04-knowledge/units/works/marco-pitteri-flaminio-corner.md) |
| FM-P48a.subject1 | 新建 | [弗拉米尼奥·科尔内尔（Flaminio Corner）](../../../04-knowledge/units/persons/flaminio-corner.md) |
| FM-P48b.creator1 | 新建 | [詹安东尼奥·法尔多尼（Gian Antonio Faldoni）](../../../04-knowledge/units/persons/gian-antonio-faldoni.md) |
| FM-P48b.creator2 | 新建 | [B. 纳扎里（B. Nazari）](../../../04-knowledge/units/persons/b-nazari.md) |
| FM-P48b.holder1 | 新建 | [科雷尔博物馆（Museo Correr）](../../../04-knowledge/units/institutions/museo-correr.md) |
| FM-P48b.object | 新建 | [扎卡里亚·萨格雷多肖像（Portrait of Zaccaria Sagredo）](../../../04-knowledge/units/works/gian-antonio-faldoni-zaccaria-sagredo.md) |
| FM-P48b.site1 | 复用并更新 | [威尼斯（Venice）](../../../04-knowledge/units/places/venice.md) |
| FM-P48b.subject1 | 新建 | [扎卡里亚·萨格雷多（Zaccaria Sagredo）](../../../04-knowledge/units/persons/zaccaria-sagredo.md) |
| FM-P48c.creator1 | 新建 | [亚历山德罗·隆吉（Alessandro Longhi）](../../../04-knowledge/units/persons/alessandro-longhi.md) |
| FM-P48c.holder1 | 新建 | [科雷尔博物馆（Museo Correr）](../../../04-knowledge/units/institutions/museo-correr.md) |
| FM-P48c.object | 新建 | [卡洛·洛多利肖像（Portrait of Carlo Lodoli）](../../../04-knowledge/units/works/alessandro-longhi-carlo-lodoli.md) |
| FM-P48c.site1 | 复用并更新 | [威尼斯（Venice）](../../../04-knowledge/units/places/venice.md) |
| FM-P48c.subject1 | 新建 | [卡洛·洛多利（Carlo Lodoli）](../../../04-knowledge/units/persons/carlo-lodoli.md) |
| FM-P48d.holder1 | 新建 | [科雷尔博物馆（Museo Correr）](../../../04-knowledge/units/institutions/museo-correr.md) |
| FM-P48d.object | 新建 | [弗朗切斯科·阿尔加罗蒂肖像（Portrait of Francesco Algarotti）](../../../04-knowledge/units/works/francesco-algarotti.md) |
| FM-P48d.site1 | 复用并更新 | [威尼斯（Venice）](../../../04-knowledge/units/places/venice.md) |
| FM-P48d.subject1 | 新建 | [弗朗切斯科·阿尔加罗蒂（Francesco Algarotti）](../../../04-knowledge/units/persons/francesco-algarotti.md) |
| FM-P49a.creator1 | 新建 | [佩莱格里尼（Pellegrini）](../../../04-knowledge/units/persons/pellegrini.md) |
| FM-P49a.depicted1 | 新建 | [普法尔茨（Palatinate）](../../../04-knowledge/units/places/palatinate.md) |
| FM-P49a.holder1 | 新建 | [巴伐利亚国家绘画收藏机构（Bayerischen Staatsgemäldesammlungen）](../../../04-knowledge/units/institutions/bayerischen-staatsgemaldesammlungen.md) |
| FM-P49a.object | 新建 | [普法尔茨王储教育寓意（Allegory of the Education of the Crown Prince of the Palatinate）](../../../04-knowledge/units/works/pellegrini-allegory-of-the-education-of-the-crown-prince-of-the-palatinate.md) |
| FM-P49a.site1 | 新建 | [慕尼黑（Munich）](../../../04-knowledge/units/places/munich.md) |
| FM-P49b.creator1 | 新建 | [阿米戈尼（Amigoni）](../../../04-knowledge/units/persons/amigoni.md) |
| FM-P49b.object | 新建 | [朱庇特与伊娥（Jupiter and Io）](../../../04-knowledge/units/works/amigoni-jupiter-and-io.md) |
| FM-P49b.site1 | 新建 | [穆尔公园庄园（Moor Park）](../../../04-knowledge/units/places/moor-park.md) |
| FM-P50.creator1 | 对齐后复用 | [乔万巴蒂斯塔·提埃坡罗（Giambattista Tiepolo）](../../../04-knowledge/units/persons/giambattista-tiepolo.md)；具体角色及依据见REV-087。 |
| FM-P50.object | 新建 | [维尔茨堡宫楼梯顶画局部（Detail from fresco on ceiling of staircase in Residenz）](../../../04-knowledge/units/works/tiepolo-detail-from-fresco-on-ceiling-of-staircase-in-residenz.md) |
| FM-P50.site1 | 新建 | [维尔茨堡宫（Residenz, Würzburg）](../../../04-knowledge/units/places/residenz-wurzburg.md) |
| FM-P50.site2 | 新建 | [维尔茨堡（Würzburg）](../../../04-knowledge/units/places/wurzburg.md) |
| FM-P51.creator1 | 新建 | [卡纳莱托（Canaletto）](../../../04-knowledge/units/persons/canaletto.md) |
| FM-P51.depicted1 | 新建 | [巴德明顿（Badminton）](../../../04-knowledge/units/places/badminton.md) |
| FM-P51.object | 新建 | [巴德明顿景观（View from Badminton, 1748）](../../../04-knowledge/units/works/canaletto-view-from-badminton-1748.md) |
| FM-P52a.creator1 | 新建 | [P. 范·布莱克（P. Van Bleek）](../../../04-knowledge/units/persons/p-van-bleek.md) |
| FM-P52a.holder1 | 新建 | [国家肖像馆（National Portrait Gallery）](../../../04-knowledge/units/institutions/national-portrait-gallery.md) |
| FM-P52a.object | 新建 | [欧文·麦克斯温尼肖像（Portrait of Owen McSwiny）](../../../04-knowledge/units/works/p-van-bleek-owen-mcswiny.md) |
| FM-P52a.subject1 | 新建 | [欧文·麦克斯温尼（Owen McSwiny）](../../../04-knowledge/units/persons/owen-mcswiny.md) |
| FM-P52b.creator1 | 新建 | [卡纳莱托（Canaletto）](../../../04-knowledge/units/persons/canaletto.md) |
| FM-P52b.creator2 | 新建 | [奇马罗利（Cimaroli）](../../../04-knowledge/units/persons/cimaroli.md) |
| FM-P52b.creator3 | 新建 | [皮托尼（Pittoni）](../../../04-knowledge/units/persons/pittoni.md) |
| FM-P52b.holder1 | 新建 | [彼得·穆尔斯（Peter Moores）](../../../04-knowledge/units/persons/peter-moores.md) |
| FM-P52b.object | 新建 | [蒂洛特森大主教寓意纪念墓（Allegorical Tomb to the memory of Archbishop Tillotson）](../../../04-knowledge/units/works/canaletto-allegorical-tomb-to-the-memory-of-archbishop-tillotson.md) |
| FM-P52b.site1 | 新建 | [利物浦（Liverpool）](../../../04-knowledge/units/places/liverpool.md) |
| FM-P52b.subject1 | 新建 | [蒂洛特森大主教（Archbishop Tillotson）](../../../04-knowledge/units/persons/archbishop-tillotson.md) |
| FM-P53a.creator1 | 新建 | [皮亚泽塔（Piazzetta）](../../../04-knowledge/units/persons/piazzetta.md) |
| FM-P53a.object | 新建 | [舒伦堡元帅肖像（Portrait of Marshal Schulenburg）](../../../04-knowledge/units/works/piazzetta-marshal-schulenburg.md) |
| FM-P53a.site1 | 新建 | [斯福尔扎城堡（Castello Sforzesco）](../../../04-knowledge/units/places/castello-sforzesco.md) |
| FM-P53a.site2 | 复用并更新 | [米兰（Milan）](../../../04-knowledge/units/places/milan.md) |
| FM-P53a.subject1 | 新建 | [舒伦堡元帅（Marshal Schulenburg）](../../../04-knowledge/units/persons/marshal-schulenburg.md) |
| FM-P53b.creator1 | 新建 | [阿米戈尼（Amigoni）](../../../04-knowledge/units/persons/amigoni.md) |
| FM-P53b.holder1 | 新建 | [灰修道院中学（Gymnasium zu Grauen Kloster）](../../../04-knowledge/units/institutions/gymnasium-zu-grauen-kloster.md) |
| FM-P53b.object | 新建 | [西吉斯蒙德·施特赖特肖像（Portrait of Sigismund Streit）](../../../04-knowledge/units/works/amigoni-sigismund-streit.md) |
| FM-P53b.site1 | 新建 | [柏林（Berlin）](../../../04-knowledge/units/places/berlin.md) |
| FM-P53b.subject1 | 新建 | [西吉斯蒙德·施特赖特（Sigismund Streit）](../../../04-knowledge/units/persons/sigismund-streit.md) |
| FM-P54.creator1 | 新建 | [皮亚泽塔（Piazzetta）](../../../04-knowledge/units/persons/piazzetta.md) |
| FM-P54.holder1 | 新建 | [瓦尔拉夫—里夏茨博物馆（Wallraf-Richartz Museum）](../../../04-knowledge/units/institutions/wallraf-richartz-museum.md) |
| FM-P54.object | 新建 | [田园（Idyll）](../../../04-knowledge/units/works/piazzetta-idyll.md) |
| FM-P54.site1 | 新建 | [科隆（Cologne）](../../../04-knowledge/units/places/cologne.md) |
| FM-P55a.creator1 | 新建 | [卡纳莱托（Canaletto）](../../../04-knowledge/units/persons/canaletto.md) |
| FM-P55a.object | 新建 | [蚀刻集献辞卷首图（Dedicatory frontispiece to Etchings）](../../../04-knowledge/units/works/canaletto-dedicatory-frontispiece-to-etchings.md) |
| FM-P55b.creator1 | 新建 | [马尔科·里奇（Marco Ricci）](../../../04-knowledge/units/persons/marco-ricci.md) |
| FM-P55b.creator2 | 新建 | [巴尔托洛齐（Bartolozzi）](../../../04-knowledge/units/persons/bartolozzi.md) |
| FM-P55b.object | 新建 | [村景（Village Scene）](../../../04-knowledge/units/works/marco-ricci-village-scene.md) |
| FM-P56.creator1 | 新建 | [马里耶斯基（Marieschi）](../../../04-knowledge/units/persons/marieschi.md) |
| FM-P56.depicted1 | 新建 | [圣洛克堂（威尼斯）（Church of S. Rocco）](../../../04-knowledge/units/places/church-of-s-rocco.md) |
| FM-P56.depicted2 | 复用并更新 | [威尼斯（Venice）](../../../04-knowledge/units/places/venice.md) |
| FM-P56.object | 新建 | [圣洛克堂画展（Picture Exhibition at Church of S. Rocco）](../../../04-knowledge/units/works/marieschi-picture-exhibition-at-church-of-s-rocco.md) |
| FM-P57a.carrier1 | 新建 | [耶路撒冷解放插图本（1745）（Gerusalemme Liberata, illustrations, 1745）](../../../04-knowledge/units/archives/gerusalemme-liberata-illustrations-1745.md) |
| FM-P57a.creator1 | 新建 | [皮亚泽塔（Piazzetta）](../../../04-knowledge/units/persons/piazzetta.md) |
| FM-P57a.object | 新建 | [《耶路撒冷解放》插图末页（Final plate of Illustrations to Gerusalemme Liberata）](../../../04-knowledge/units/works/piazzetta-final-plate-of-illustrations-to-gerusalemme-liberata.md) |
| FM-P57a.publisher1 | 新建 | [阿尔布里齐（Albrizzi）](../../../04-knowledge/units/persons/albrizzi.md) |
| FM-P57a.self1 | 新建；REV-088将角色限定为肖像对象，保留旧锚点 | [乔万尼·巴蒂斯塔·皮亚泽塔（Giovanni Battista Piazzetta）](../../../04-knowledge/units/persons/piazzetta.md) |
| FM-P57a.subject1 | 新建 | [阿尔布里齐（Albrizzi）](../../../04-knowledge/units/persons/albrizzi.md) |
| FM-P57b.author1 | 新建 | [戈尔多尼（Goldoni）](../../../04-knowledge/units/persons/goldoni.md) |
| FM-P57b.carrier1 | 新建 | [戈尔多尼作品集第二卷（1761）（Goldoni, Opere, vol. 2, 1761）](../../../04-knowledge/units/archives/goldoni-opere-vol-2-1761.md) |
| FM-P57b.creator1 | 新建 | [皮埃特罗·安东尼奥·诺韦利（Pietro Antonio Novelli）](../../../04-knowledge/units/persons/pietro-antonio-novelli.md) |
| FM-P57b.object | 新建 | [戈尔多尼《作品集》第二卷卷首图（Frontispiece to Vol. 2 of Goldoni: Opere）](../../../04-knowledge/units/works/pietro-antonio-novelli-frontispiece-to-vol-2-of-goldoni-opere.md) |
| FM-P57b.publisher1 | 新建 | [帕斯夸利（Pasquali）](../../../04-knowledge/units/persons/pasquali.md) |
| FM-P58a.creator1 | 新建 | [朱塞佩·佐基（Giuseppe Zocchi）](../../../04-knowledge/units/persons/giuseppe-zocchi.md) |
| FM-P58a.holder1 | 新建 | [科雷尔博物馆（Museo Correr）](../../../04-knowledge/units/institutions/museo-correr.md) |
| FM-P58a.object | 新建 | [老扎内蒂与杰里尼侯爵（A. M. Zanetti the Elder with Marchese Gerini）](../../../04-knowledge/units/works/giuseppe-zocchi-a-m-zanetti-the-elder-with-marchese-gerini.md) |
| FM-P58a.site1 | 复用并更新 | [威尼斯（Venice）](../../../04-knowledge/units/places/venice.md) |
| FM-P58a.subject1 | 已登记后对齐 | [老安东·玛丽亚·扎内蒂（Anton Maria Zanetti the Elder）](../../../04-knowledge/units/persons/a-m-zanetti-the-elder.md)；原书简称保留，见REV-089。 |
| FM-P58a.subject2 | 已登记后对齐 | [安德烈亚·杰里尼（Andrea Gerini）](../../../04-knowledge/units/persons/marchese-gerini.md)；原书Marchese Gerini，见REV-089。 |
| FM-P58b.creator1 | 新建 | [亚历山德罗·隆吉（Alessandro Longhi）](../../../04-knowledge/units/persons/alessandro-longhi.md) |
| FM-P58b.holder1 | 新建 | [科雷尔博物馆（Museo Correr）](../../../04-knowledge/units/institutions/museo-correr.md) |
| FM-P58b.object | 新建 | [G. M. 萨索肖像（Portrait of G. M. Sasso）](../../../04-knowledge/units/works/alessandro-longhi-g-m-sasso.md) |
| FM-P58b.site1 | 复用并更新 | [威尼斯（Venice）](../../../04-knowledge/units/places/venice.md) |
| FM-P58b.subject1 | 新建 | [G. M. 萨索（G. M. Sasso）](../../../04-knowledge/units/persons/g-m-sasso.md) |
| FM-P59a.creator1 | 新建 | [卡诺瓦（Canova）](../../../04-knowledge/units/persons/canova.md) |
| FM-P59a.holder1 | 新建 | [科雷尔博物馆（Museo Correr）](../../../04-knowledge/units/institutions/museo-correr.md) |
| FM-P59a.object | 新建 | [阿马德奥·斯瓦耶尔肖像（Portrait of Amadeo Swajer）](../../../04-knowledge/units/works/canova-amadeo-swajer.md) |
| FM-P59a.site1 | 复用并更新 | [威尼斯（Venice）](../../../04-knowledge/units/places/venice.md) |
| FM-P59a.subject1 | 新建 | [阿马德奥·斯瓦耶尔（Amadeo Swajer）](../../../04-knowledge/units/persons/amadeo-swajer.md) |
| FM-P59b.creator1 | 新建 | [贝尔纳迪诺·卡斯泰利（Bernardino Castelli）](../../../04-knowledge/units/persons/bernardino-castelli.md) |
| FM-P59b.holder1 | 新建 | [科雷尔博物馆（Museo Correr）](../../../04-knowledge/units/institutions/museo-correr.md) |
| FM-P59b.object | 新建 | [泰奥多罗·科雷尔肖像（Portrait of Teodoro Correr）](../../../04-knowledge/units/works/bernardino-castelli-teodoro-correr.md) |
| FM-P59b.site1 | 复用并更新 | [威尼斯（Venice）](../../../04-knowledge/units/places/venice.md) |
| FM-P59b.subject1 | 新建 | [泰奥多罗·科雷尔（Teodoro Correr）](../../../04-knowledge/units/persons/teodoro-correr.md) |
| FM-P60.creator1 | 新建 | [G. 沃尔帕托（G. Volpato）](../../../04-knowledge/units/persons/g-volpato.md) |
| FM-P60.depicted1 | 新建 | [弗朗切斯科·阿尔加罗蒂墓（Tomb of Francesco Algarotti）](../../../04-knowledge/units/works/tomb-of-francesco-algarotti.md) |
| FM-P60.depicted2 | 新建 | [比萨（Pisa）](../../../04-knowledge/units/places/pisa.md) |
| FM-P60.object | 新建 | [阿尔加罗蒂墓前悼念者（Mourners at Tomb of Francesco Algarotti in Pisa）](../../../04-knowledge/units/works/g-volpato-mourners-at-tomb-of-francesco-algarotti-in-pisa.md) |
| FM-P60.subject1 | 新建 | [弗朗切斯科·阿尔加罗蒂（Francesco Algarotti）](../../../04-knowledge/units/persons/francesco-algarotti.md) |
| FM-P61a.creator1 | 对齐后复用 | [乔万巴蒂斯塔·提埃坡罗（Giambattista Tiepolo）](../../../04-knowledge/units/persons/giambattista-tiepolo.md)；Paris Musées J 104。 |
| FM-P61a.holder1 | 新建 | [科涅克—杰博物馆（Musée Cognacq-Jay）](../../../04-knowledge/units/institutions/musee-cognacq-jay.md) |
| FM-P61a.object | 新建 | [安东尼与克娄巴特拉宴会：科涅克—杰藏本（Banquet of Anthony and Cleopatra, Cognacq-Jay version）](../../../04-knowledge/units/works/tiepolo-banquet-cognacq-jay.md) |
| FM-P61a.site1 | 新建 | [巴黎（Paris）](../../../04-knowledge/units/places/paris.md) |
| FM-P61b.creator1 | 对齐后复用 | [乔万巴蒂斯塔·提埃坡罗（Giambattista Tiepolo）](../../../04-knowledge/units/persons/giambattista-tiepolo.md)；NGV 103-4。 |
| FM-P61b.holder1 | 新建 | [维多利亚国家美术馆（National Gallery of Victoria）](../../../04-knowledge/units/institutions/national-gallery-of-victoria.md) |
| FM-P61b.object | 新建 | [安东尼与克娄巴特拉宴会：维多利亚国家美术馆藏本（Banquet of Anthony and Cleopatra, National Gallery of Victoria version）](../../../04-knowledge/units/works/tiepolo-banquet-victoria.md) |
| FM-P61b.site1 | 新建 | [墨尔本（Melbourne）](../../../04-knowledge/units/places/melbourne.md) |
| FM-P62.creator1 | 新建 | [卡纳莱托（Canaletto）](../../../04-knowledge/units/persons/canaletto.md) |
| FM-P62.depicted1 | 新建 | [Prà广场（Prà della Valle）](../../../04-knowledge/units/places/pra-della-valle.md) |
| FM-P62.depicted2 | 新建 | [帕多瓦（Padua）](../../../04-knowledge/units/places/padua.md) |
| FM-P62.object | 新建 | [帕多瓦Prà广场（Prà della Valle, Padua）](../../../04-knowledge/units/works/canaletto-pra-della-valle-padua.md) |
| FM-P63.creator1 | 新建 | [多梅尼科·切拉托（Domenico Cerato）](../../../04-knowledge/units/persons/domenico-cerato.md) |
| FM-P63.design_site1 | 新建 | [Prà广场（Prà della Valle）](../../../04-knowledge/units/places/pra-della-valle.md) |
| FM-P63.object | 新建 | [Prà广场整治原始方案（Original proposals for reclaiming Prà della Valle）](../../../04-knowledge/units/works/domenico-cerato-original-proposals-for-reclaiming-pra-della-valle.md) |
| FM-P64.creator1 | 新建 | [弗朗切斯科·瓜尔迪（Francesco Guardi）](../../../04-knowledge/units/persons/francesco-guardi.md) |
| FM-P64.depicted1 | 新建 | [帕埃塞（Paese）](../../../04-knowledge/units/places/paese.md) |
| FM-P64.depicted2 | 新建 | [特雷维索（Treviso）](../../../04-knowledge/units/places/treviso.md) |
| FM-P64.object | 新建 | [约翰·斯特兰奇别墅景观（View of John Strange's villa at Paese near Treviso）](../../../04-knowledge/units/works/francesco-guardi-view-of-john-strange-s-villa-at-paese-near-treviso.md) |
| FM-P64.property_owner1 | 新建 | [约翰·斯特兰奇（John Strange）](../../../04-knowledge/units/persons/john-strange.md) |
| FM-P64.site1 | 复用并更新 | [伦敦（London）](../../../04-knowledge/units/places/london.md) |
| FM-P65a.creator1 | 复用并更新 | [皮耶尔·弗朗切斯科·莫拉（Pier Francesco Mola）](../../../04-knowledge/units/persons/pier-francesco-mola.md) |
| FM-P65a.creator2 | 新建 | [西莫内利（Simonelli）](../../../04-knowledge/units/persons/simonelli.md) |
| FM-P65a.former_holder1 | 新建 | [维塔莱·布洛赫（Vitale Bloch）](../../../04-knowledge/units/persons/vitale-bloch.md) |
| FM-P65a.object | 新建 | [西莫内利与莫拉联合漫画（Joint caricature of Simonelli and Mola）](../../../04-knowledge/units/works/mola-joint-caricature-of-simonelli-and-mola.md) |
| FM-P65a.self1 | 复用并更新 | [皮耶尔·弗朗切斯科·莫拉（Pier Francesco Mola）](../../../04-knowledge/units/persons/pier-francesco-mola.md) |
| FM-P65a.self2 | 新建 | [西莫内利（Simonelli）](../../../04-knowledge/units/persons/simonelli.md) |
| FM-P65b.creator1 | 新建 | [阿戈斯蒂诺·马苏奇（Agostino Masucci）](../../../04-knowledge/units/persons/agostino-masucci.md) |
| FM-P65b.holder1 | 新建 | [斯德哥尔摩国家博物馆（National Museum, Stockholm）](../../../04-knowledge/units/institutions/national-museum-stockholm.md) |
| FM-P65b.object | 新建 | [莫拉为亚历山大七世作像（Mola painting the portrait of Pope Alexander VII）](../../../04-knowledge/units/works/agostino-masucci-mola-painting-the-portrait-of-pope-alexander-vii.md) |
| FM-P65b.site1 | 新建 | [斯德哥尔摩（Stockholm）](../../../04-knowledge/units/places/stockholm.md) |
| FM-P65b.subject1 | 复用并更新 | [皮耶尔·弗朗切斯科·莫拉（Pier Francesco Mola）](../../../04-knowledge/units/persons/pier-francesco-mola.md) |
| FM-P65b.subject2 | 原位整理后接收 | [亚历山大七世（Alexander VII）](../../../04-knowledge/units/persons/alexander-vii.md) |
| FM-P66.creator1 | 新建 | [巴尔达萨雷·弗兰切斯基尼（Baldassare Franceschini）](../../../04-knowledge/units/persons/baldassare-franceschini.md) |
| FM-P66.object | 新建 | [声名携路易十四之名入不朽殿堂（Fame carrying the name of Louis XIV to the Temple of Immortality）](../../../04-knowledge/units/works/baldassare-franceschini-fame-carrying-the-name-of-louis-xiv-to-the-temple-of-immortality.md) |
| FM-P66.site1 | 新建 | [凡尔赛（Versailles）](../../../04-knowledge/units/places/versailles.md) |
| FM-P66.subject1 | 新建 | [路易十四（Louis XIV）](../../../04-knowledge/units/persons/louis-xiv.md) |
| FM-P67.creator1 | 原位整理后接收 | [朱塞佩·马里亚·克雷斯皮（Giuseppe Maria Crespi）](../../../04-knowledge/units/persons/giuseppe-maria-crespi.md) |
| FM-P67.holder1 | 新建 | [斯图加特州立美术馆（Staatsgalerie, Stuttgart）](../../../04-knowledge/units/institutions/staatsgalerie-stuttgart.md) |
| FM-P67.object | 新建 | [库柏勒将朱庇特交给科律班忒斯哺育（Jupiter handed over by Cybele to the Corybantes to be fed）](../../../04-knowledge/units/works/g-m-crespi-jupiter-handed-over-by-cybele-to-the-corybantes-to-be-fed.md) |
| FM-P67.site1 | 新建 | [斯图加特（Stuttgart）](../../../04-knowledge/units/places/stuttgart.md) |
| FM-P68a.creator1 | 新建 | [弗朗切斯科·马焦托（Francesco Maggiotto）](../../../04-knowledge/units/persons/francesco-maggiotto.md) |
| FM-P68a.object | 暂缓 | 目录合列三幅未具名总督肖像；未定位三件实物前不把群项伪装成一个或三个确定作品。 |
| FM-P68b.creator1 | 对齐后复用 | [乔万巴蒂斯塔·提埃坡罗（Giambattista Tiepolo）](../../../04-knowledge/units/persons/giambattista-tiepolo.md)；具体角色及依据见REV-087。 |
| FM-P68b.creator2 | 对齐后复用 | [雅科波·莱奥纳迪斯（Jacopo Leonardis）](../../../04-knowledge/units/persons/leonardis.md)；版画刻印者，保留原路径。 |
| FM-P68b.object | 新建 | [梅塞纳斯向奥古斯都呈献艺术（Maecenas presenting the Arts to Augustus）](../../../04-knowledge/units/works/tiepolo-maecenas-presenting-the-arts-to-augustus.md) |
| FM-X01 | 新建 | [伯灵顿杂志（Burlington Magazine）](../../../04-knowledge/units/archives/burlington-magazine.md) |
| FM-X02 | 新建 | [博物馆研究期刊（Museum Studies）](../../../04-knowledge/units/archives/museum-studies-art-institute-chicago.md) |


## 关系阶段交接

原文关系候选FM-R01–25继续保存在[处理结果第四节](../results/stages.md#4-关系候选指代与证据)。本轮将其端点按上表落实；原句、发言者、否定／推测及版本限定不因登记而改变。图版角色和供片联系依同一图版锚点反查上表及卡内对应字段。两家馆藏的《宴会》分别对应FM-P61a和FM-P61b，不共享作品端点。

REV-085登记交接时有22条主候选尚无KU映射；此外，卡内仍有未定的图像角色、爵位持有人、匿名收藏／群体和待补字段。此数仅为当时主候选暂缓量，当前变化见下方REV-086。所有新卡均未完成全面补足或正式关系裁决。

## 最终核对

写回后逐一核对420个受影响KU及accepted的内容指纹；795条有效路径全部存在，主候选无遗漏去向。547条新增／重新登记摘录与原文件行段一致；当前任务文档及KU新增链接、来源编号、YAML结构、双语标题／描述检查通过。已有内容质量检查在本轮420个对象范围内未报确定性缺陷；两位作者的同题《逃往埃及途中的休息》已作语义区分。`git diff --check`通过，原书PDF／Markdown和页面无改动。上述机械检查与本轮语义自查分别报告，不称独立验收；未提交、推送。

## 初步对齐：REV-086

### 范围与结论

2026-09-14接续用户“继续”。本轮实际审查22条主候选暂缓项的身份问题，并重点落实两组别名、复合人名、圣克莱孟堂参与者及图版61的两个版本。使用verify；对身份解除暂缓后需成稿的5个对象，按ingest既有字段契约回填原文来源。没有对420张初稿逐一完成外部身份验证，也没有完成整页百科补足。

8条主候选解除暂缓：FM-E019、020、040、071、072、077、079、082；其中3条复用已有对象，5条新建。另确认FM-P61a.creator1和61b.creator1，更新圣克莱孟堂事件的两个人物端点。主候选现为223条映射KU、4条属性／语境、14条暂缓；任务涉及425个KU，全库有效登记800个。原文候选谓词、作者评价、否定和推测均保留；未新增正式relations。

### 实际来源与身份比较

下表所列采用记录均于2026-09-14实际打开阅读对应条目或段落。来源条目、原书原句及逐字段证据保存在各卡sources；这里仅记录判断变化。官网目录和同一官网的展册属于同一来源组，不计作两份独立证明；意大利目录引用Gilmartin研究，与原书注释存在来源关联，也不包装成完全独立的事实验证。

| 对象／锚点 | 实际核对与采用范围 | 裁决与限制 |
|---|---|---|
| Tim／A. N. L. Munby | [国王学院现代档案指南](https://www.kings.cam.ac.uk/guide-modern-archives)，Munby Papers／ANLM：Alan Noel Latimer ('Tim') Munby，1913–1974；对照B:L14–15、C:L22 | 昵称、缩写及序言写于1979年的已故语境一致，复用同卡；咨询与朋友事实仍由原书支持。Cambridge Library legacy页403，不算已读证据。 |
| Ben／Benedict Nicolson | [Paul Mellon Centre档案介绍](https://www.paul-mellon-centre.ac.uk/about/news/benedict-nicolson-archive-now-fully-catalogued/news-category/archives-library-collections/page/2)列Lionel Benedict，1914–1978；[档案展册](https://www.paul-mellon-centre.ac.uk/media/_file/collections/booklet-art-life-love.pdf)印刷35／PDF38的Further Reading同时使用Ben与Benedict | 结合两版序言同一写作协助语境配对；不与John Nicoll混同。仅采用档案介绍与书目页，不称40页展册或相关传记全文已读。 |
| Alessandro Marabottini Marabotti | [佩鲁贾大学特藏名录](https://csb.unipg.it/organizzazione/fondi-storici/censimento-fondi-e-collezioni-speciali)M项列Alessandro Marabotti Marabottini；C:L24原印复姓与教授语境 | 复姓名字组相同，大学书库目录提供倒序异文；以原书全称成稿，不删复姓，不宣称已核法定姓名顺序。其他网页搜索所得生平未采入。 |
| Pier Leoni Ghezzi | [项目目录1200757776A-0](https://catalogo.beniculturali.it/detail/HistoricOrArtisticProperty/1200757776A-0)及[组成作品1200757776A-4](https://catalogo.beniculturali.it/detail/HistoricOrArtisticProperty/1200757776A-4)列Pier Leone，1674–1755 | 同一教堂、同一装饰语境与姓名对应；保留Leoni为原书写法，规范展示Leone，不合并Giuseppe Ghezzi。作品记录号不可作为人物规范ID。 |
| Tommaso Chiari | 同项目[1200757776A-0](https://catalogo.beniculturali.it/detail/HistoricOrArtisticProperty/1200757776A-0)同时列Tommaso及Giuseppe Bartolomeo；[1200757776A-1](https://catalogo.beniculturali.it/detail/HistoricOrArtisticProperty/1200757776A-1)明确Tommaso，1665–1733 | 不是凭知名度可纠正的误名；单独登记Tommaso。组成作品只用作此次身份链，未在人物正文扩写其作品清单。 |
| Pietro di Pietri、Piastrini、Odazzi、Triga、Conca | [同项目目录](https://catalogo.beniculturali.it/detail/HistoricOrArtisticProperty/1200757776A-0)逐名比较，共5个已有KU | Pietro规范展示为目录所用Pietro Antonio De Petri，保留Pietro di Pietri及固定路径；其余4位增加身份入口。仅确认这个项目名单中的人物，不把目录所有附属作品扩入人物生平。 |
| Guido | E:L183–184十七世纪、与Guercino并举、不留Rome；[英国国家美术馆人物条目](https://www.nationalgallery.org.uk/artists/guido-reni)的Reni年代及罗马—博洛尼亚活动，与已有KU身份依据相合 | 语义配对为Guido Reni。索引Reni条L2640–2641没有xvii，不能声称索引直接解出了这一页简称。馆方生平只辅助身份，不证明“拒留”的心理或动机。 |
| 导言Tiepolo | E:L184／xvii；索引L3170–3174明确Tiepolo, Giambattista含xvii；[Paris Musées](https://www.parismuseescollections.paris.fr/fr/musee-cognacq-jay/oeuvres/le-banquet-de-cleopatre)及[NGV](https://www.ngv.vic.gov.au/explore/collection/work/4409/)列同名画家 | 导言映射Giambattista；不能顺带决定其他图版仅写Tiepolo的作者。只新增已实际核出的61a、61b作品清单入口。 |
| 图版61a／61b | Paris Musées J 104，1742–1743，50.5×69cm；NGV 103-4，1743–1744，250.3×357.0cm，Felton Bequest 1933；题材、作者、馆藏与原目录匹配 | 两件作品分别保留原路径、原题及馆藏规范题。巴黎馆方将J 104界定为墨尔本作品预备版本；此为外部版本事实，不倒写成原书所述。此轮读馆藏记录，未进行两张图像的视觉比对。 |
| S. Clemente主保圣人 | [教堂官网History](https://www.basilicasanclemente.com/eng/history/)明确纪念彼得第三位继任者；[梵蒂冈Clement名录](https://www.vatican.va/content/vatican/en/holy-father/clemente.html)为第四任教宗 | 映射早期教宗Clement I，区别教堂地点、Clement XI和十八世纪装饰事件；“Clement XI的主保圣人”仍取自原书句子。 |

上述采用链是机构档案、馆藏与教堂记录。本轮没有新增或确认任何QID，也没有完成新的Wikipedia↔Wikidata双向核对；原有Wiki验证记录保留，不因此提高整卡状态。

### REV-086时暂缓的14条主候选

以下保留当时的证据状态；其中4条在REV-090取得新证据后解除暂缓，当前去向见本文件候选登记映射及REV-090段落。

| 锚点 | 当前依据、问题与下一步 |
|---|---|
| FM-E055 Lazzarini | 原文仅姓氏；本书索引Gregorio Lazzarini条不列xvii，本轮检索没有补上“拒绝移居罗马”特定语境的直接身份链，继续暂缓。 |
| FM-P05 博尔盖塞胸像 | 原书仅列人物、Bernini及Villa Borghese，未区分两个胸像版本；本轮未新完成图像比对，不借既有不分版本卡强行合并。 |
| FM-P68a 三幅总督肖像 | 原文是三件群项，人物和实物仍未逐件定位；不新造三张具体作品卡。 |
| FM-H01 Agraci | 已读[INHA AGORHA](https://agorha.inha.fr/ark:/54721/4bce2cf5-9986-48c2-9cff-c6dd1728b597)，称巴黎艺术翻拍摄影师、活动1960–1980；Zeri搜索候选却显示“Agraci. Arts Graphiques de la Cité”。后者记录未成功打开，个人／商号粒度仍未解决；不取前者单库类型直接登记人物。 |
| FM-H02 Annan | 已读[格拉斯哥大学T. & R. Annan & Sons条目](https://www.mackintosh-architecture.gla.ac.uk/catalogue/name/?nid=AnnSon&xml=des)，明确是家族摄影企业，并区分创办人及后人；尚未以图版35b底片或原始署名确定原书Annan所指业务主体，保留企业候选。 |
| FM-H03 Balelli | 国家图书馆Balelli档案为搜索线索，实际页未成功打开；有家族多代摄影师／工作室粒度问题。需定位图版33b供片或底片记录。 |
| FM-H04 Böhm | 检索得到Osvaldo Böhm摄影师、工作室及摄影出版者不同角色；尚未逐条读取可对应41b／44的照片记录，不指定具体个人。 |
| FM-H05 Cacco | ICCD摄影师索引同时见Cacco和Cacco, Giorgio，仅名字不够；需图版48b／48d／55b／60／62对应记录。 |
| FM-H09 Gilchrist | Leeds检索出现Sarah Gilchrist画廊档案，但既无该供片者姓名展开，也无图版32b联系；不把同城同姓画廊经营者代入。 |
| FM-H12 Mansell-Alinari | 复合署名的摄影／代理分工仍缺直接记录；检索到其他书相同署名不证明单一机构，不建“Mansell-Alinari”法人。 |
| FM-H13 Mansell-Anderson | 同上，保持两个署名成分及原图版范围，等待摄影目录／代理记录；不将Anderson个人、工作室与Mansell混成实体。 |
| FM-H14 National Gallery | 图版34与52b供片，原文无城市；不能以作品所在馆反推供片馆，也不能把Met改作供片者；本轮无新增可确定地域的直接证据。 |
| FM-H16 Rossi | 常见姓氏加Venice不能辨别摄影师或商号；本轮检索未获得与58a相合的可靠记录，继续待核。 |
| FM-H24 Villani | 已读[Alinari的Fondo Villani介绍](https://www.alinari.it/cms/it/news/fondo-villani-trasferimento-bologna)，区分Achille／Vittorio和1914–1980的Bologna工作室；尚缺图版28a署名对应，保留工作室候选，不写成某位摄影师的个人供片。 |

14是主候选暂缓数，不是全部事实缺口。其余420张登记卡还未逐一完成外部对齐；尤其5件其他Tiepolo图版创作者、爵号持有人、部分仅姓氏的创作者／出版者、书目版本及图像角色仍须按映射和正文检查。没有用未命中搜索证明实体不存在。

### 对关系阶段的影响

FM-R06相关朋友／咨询端点现可复用两位人物，FM-R09的Munby图书馆工作与前者是同人不同事实；FM-R11的Marabottini观看／接待端点有卡可用。FM-R16的导言Tiepolo可定位，FM-R21的七位参与者已全部有明确人物KU，并可反查同一原句。上述锚点编号以处理定稿为准；对齐只更新端点，关系候选不自动升为正式边。图版61的作者、作品、收藏机构端点具备，但具体版本关系来自外部馆方记录，应与原书图版关系分开。

### 写回与检查

本轮5个新KU、12个已有KU更新及accepted，共18个写回目标。预览后核对全部目标旧内容，再串行写回；25条受影响卡内原书摘录与实际行段一致，已有sources前缀及正式relations保持原值，accepted的claims和structure保持原值。见[本轮写回指纹](alignment-writeback.json)；REV-085的registration-writeback保留当时结果，不覆盖为本轮快照。原书PDF／Markdown、第一章任务结果和页面未变。最终检查结果见当前04结果；未提交或推送。

## 图版作者与版本对齐：REV-087

### 提交同步与接续范围

先将REV-083–086的章前成果及生成索引提交为`7a046470ca7f286cf7636dafa83b900d85dd2858`，推送origin/main。2026-09-14核对本地HEAD与`git ls-remote origin refs/heads/main`相同，同步时工作树干净。完整测试通过；GitHub [Quality gate运行34813317233](https://github.com/fengbaifan/PNP-Final-DATA/actions/runs/34813317233)的Python 3.10和3.12两项均成功。首次提交前检查的generated snapshots步骤因新生成文件尚未提交而报告差异；已将这些变化纳入该提交，远端检查通过。网页数据未刷新。

随后接续初步对齐，集中处理剩余5件Tiepolo图版与Leonardis姓名，不以姓氏批量指定父子。外部资料只用于本件作品的身份和必要角色；引入的明确协作者回ingest建卡，不扩张馆方页面上所有作品和人物。实际采用网页均于2026-09-14打开相应段落；PDF仅阅读所列条目，未声称180页全文阅读或扫描图像比对。

| 原文锚点 | 来源与比较 | 当前裁决 |
|---|---|---|
| FM-P42a.creator1／object | [MUVE作品条目](https://www.visitmuve.it/en/masterpiece/giambattista-tiepolo-neptune-offering-gifts-to-venice/)的作者、题材与总督宫位置吻合，馆藏号TS 2° p. n. 6 n. 328 | 创作者为Giambattista Tiepolo。采用馆方1757–1758断代，明确字段名为“馆方创作年代”；没有将搜索所得其他断代混入本条。书中Neptune paying homage与馆方Neptune Offering Gifts分别留存。 |
| FM-P43.creator1／object | [Ca’ Rezzonico官网First floor](https://carezzonico.visitmuve.it/en/layout-and-collections/first-floor/)的Nuptial Allegory Room段 | 主画家Giambattista Tiepolo；Girolamo Mengozzi Colonna负责建筑幻景，儿子Giandomenico负责萨堤尔。两位协作者分别建立KU及明确角色；这些协作／亲缘事实来自外部馆方，不伪装成原图版目录所述。 |
| FM-P44.creator1／object | [威尼托国家博物馆管理机构2025-04-25活动说明](https://museiveneto.cultura.gov.it/eventi-e-mostre/museo-di-villa-pisani-25-aprile-ore-11-dialoghi-dellesedra-da-tiepolo-paschetto)的舞厅顶画段 | 作者Giambattista Tiepolo、舞厅天顶与1761–1762年对应。Villa Pisani旧站请求多次超时，未把只见搜索摘要的旧站当作本轮完整阅读证据；改用已读主管机构正文。部分人物寓意有争议，不按常见解说强定人物身份。 |
| FM-P50.creator1／object | [巴伐利亚宫殿管理局Staircase正文](https://www.residenz-wuerzburg.de/englisch/residenz/treppe.htm)明确Giovanni Battista Tiepolo、1752/53与楼梯厅顶画 | 身份配对至既有Giambattista卡。知识元是整幅固定位置顶画，原书仅复制局部；标题与描述区分作品和图版裁切范围，保留稳定路径。网页图像标题提及其他姓名，不能据此推断所有人为共同作者；本轮没有为该壁画新增Giandomenico创作事实。 |
| FM-P68b.creator1／creator2／object | [慕尼黑国家版画收藏馆2022数字馆藏目录](https://www.sgsm.eu/fileadmin/Dokumente/Venedig_SGSM_Bestandskatalog_220119.pdf)，印刷78／PDF78的Leonardis, Jacopo条下HISTORIE段 | Jacopo Leonardis于1766年依据G. B. Tiepolo设计制作该蚀刻版画；原设计与刻印角色分开。11348 D是目录中的慕尼黑印本，不能直接填为本书图版所用实物的馆藏号。保持作品级匹配，具体印本／版次仍未核同。Leonardis原卡增加规范名，未新造第二人。 |

### 外部补入端点与关系候选

| 新锚点 | 对象及来源 | 必要事实与交接 |
|---|---|---|
| FM-EX01 | [Girolamo Mengozzi Colonna](../../../04-knowledge/units/persons/girolamo-mengozzi-colonna.md)，MUVE的Nuptial Allegory Room段 | 该作品建筑幻景的绘制者；候选方向人物→FM-P43作品，角色限建筑幻景。 |
| FM-EX02 | [Giandomenico Tiepolo](../../../04-knowledge/units/persons/giandomenico-tiepolo.md)，同段 | 该作品萨堤尔的绘制者；候选方向人物→FM-P43作品。亲缘为Giandomenico→Giambattista（父亲）；父子两卡提供互链，仍未写正式边。 |

这两个对象没有本轮已读原书中的直接具名出处，sources只登记实际外部段落，不复制其父亲的原书原句充作自身出处。二者不进入原始241条主候选计数。作品卡保存分工及链接，人物卡保存对应作品；Giambattista卡补入5件作品／原设计入口，现覆盖本任务7件Tiepolo署名图版，不是其完整作品全集。图版68b的“原设计”不表示他亲自刻印这件版画；原设计所据画作的具体版本须补足时继续辨认，不能把它与版画合成同一实物。

### 当前结果与剩余问题

5条Tiepolo作者子锚点已落实，Leonardis已展开姓名；主候选仍为223条映射、4条属性／语境、14条暂缓。新增2个人物KU，更新7个已有KU，全库有效登记802个；本任务涉及427个对象。14条主候选的暂缓理由延续REV-086，其他爵号、供片机构、书目版本及印本核同仍未完成，整体初步对齐继续进行。作者身份可用不等于外部补足完整，更不等于所有创作／安置／委托等关系已定稿。

本轮为模型逐项判断后机械排版，精确before/after保存在本机临时目录`C:/Users/001/AppData/Local/Temp/pnp-rev087-alignment/plan.json`；写回前核对10个目标原内容，旧sources和正式relations保持原值。正式可恢复基线为已推送提交7a04647；本段接续成果尚未再次提交或推送。阶段结果原位更新04，未修改源书、第一章任务结果、规则／技能或页面。

接续写回后检查9张受影响KU的内容格式无确定性发现，8条原书摘录与实际行段一致；802条有效路径、正文相对链接和来源序号有效，既有sources前缀与正式relations不变，`git diff --check`通过。这是本轮语义自查与机械检查，不是独立验收。

## 出版者与书目对齐：REV-088

2026-09-14接续初步对齐，集中处理图版57a／57b的两部载体文献、作者与出版者，以及导言所引Gilmartin论文。采用verify；发现文字作者端点缺失后，按ingest契约建立Torquato Tasso。模型逐项比较原文与外部记录，脚本只负责已决定内容的排版、差异预览和写回。未启动全面补足或关系定稿。

### 来源、阅读范围与裁决

| 对象／锚点 | 实际阅读与比较 | 本轮结果与范围 |
|---|---|---|
| FM-P57a.publisher1／subject1：Albrizzi | [Treccani人物条目](https://www.treccani.it/enciclopedia/giovanni-battista-albrizzi_(Dizionario-Biografico)/)正文，及[普林斯顿图书馆Z-GA-EGA-131](https://static-prod.lib.princeton.edu/scsites/portfolio/ega/r00000032.htm)目录说明；与原书E:L135的1745年版本及Piazzetta配对 | 展开为Giovanni Battista Albrizzi，1698–1777；原位保留Albrizzi及出版署名Giambatista。DBI明确区分同名孙辈，本次采用十八世纪中叶的出版者；没有把其他Albrizzi人物或家族合入。 |
| FM-P57b.publisher1：Pasquali | [巴塞罗那大学印刷者规范记录](https://marques.crai.ub.edu/en/printer/pasquali-giovanni-battista)姓名、异名与活动项；[WorldCat 14629858](https://search.worldcat.org/title/Delle-commedie-di-Carlo-Goldoni-../oclc/14629858)责任者及出版项；[Treccani人物条目](https://www.treccani.it/enciclopedia/giambattista-pasquali_(Dizionario-Biografico)/)生平及Goldoni出版段 | 展开为Giovanni Battista Pasquali，另列Giambattista／Giambatista及Jo. Baptista；与1761年威尼斯版本的印刷／出版角色吻合。姓氏保留为原书形式，人物不改成机构。 |
| FM-P57a.creator1／self1：Piazzetta | [Treccani人物条目](https://www.treccani.it/enciclopedia/giovanni-battista-piazzetta_(Dizionario-Biografico)/)姓名、生年及1745年插图设计段；对照E:L135的“with portraits of Piazzetta and Albrizzi” | 展开Giovanni Battista，别名Giambattista。书目与传记支持插图设计，不能据此认定该末页由他亲自刻版。原初稿“自我描绘者”过强，收窄为“描绘对象”；旧self1锚点保留，并在候选表／两张KU中一致更正。 |
| FM-P57b.author1／creator1 | WorldCat上述记录的Carlo Goldoni、Pietro Antonio Novelli及[Novelli人物条目](https://www.treccani.it/enciclopedia/pietro-antonio-novelli_(Dizionario-Biografico)/)姓名、生年、Pasquali与Zatta两版比较段 | Goldoni展开Carlo Goldoni，Novelli核为1729年生者，保留Pier Antonio异名；设计角色落到现有KU。两人都提供文献／插图入口。原书第二卷不与其他版次、第一卷肖像或第一章Novetti合并。 |
| FM-P57a.carrier1 | 普林斯顿图书馆目录完整书目说明，结合Piazzetta条目与原书1745年载体 | 规范为1745年Albrizzi插图本，补文字作者Tasso、出版地及各责任者。普林斯顿Z-GA-EGA-131是图像目录编号，不能当作本书图版所用印本的馆藏号；没有查看该版本全部扫描或进行末页图像比对。 |
| FM-P57b.carrier1 | WorldCat整套记录与[Casa di Carlo Goldoni馆藏版本说明](https://carlogoldoni.visitmuve.it/it/il-museo/servizi-agli-studiosi/biblioteca/servizi-scientifici-3-2/edizioni-goldoniane/)的Pasquali项 | 对齐为Delle commedie di Carlo Goldoni之Pasquali版第二卷，保留原书简题Opere。馆方整套时段1761–1778?与目录1761属不同粒度；卡内分字段保存“原书所标年份”“整套书目所标年份”“馆方所记整套出版时段”。第二卷实际出书年尚无单册原件证明，不把整个时段套入第二卷，也不宣称1761已经证伪。 |
| FM-E092及gilmartin-san-clemente-1974 | [出版社1974年6月目录](https://www.burlington.org.uk/archive/back-issues/197406)的刊期及该文条目；[JSTOR同期期目](https://www.jstor.org/stable/i236686)可定位至stable/877695 | 明确John Gilmartin、正式题名、116卷855期、1974年6月；作者与论文互链。出版社目录未提供页码，JSTOR文章页未取得可读正文；保留原书305–310为“原书书目所载页码”，不当作已校定全文页段。 |

以上均于2026-09-14读取所述页面或段落。Treccani条目互相关联，WorldCat和大学规范记录也可能复用规范数据，不以站点数量计算独立证据。这里只采纳本轮身份、版本及必要角色；传记中其余家庭、作品、生平与评价仍交补足阶段逐项处理，未将页面所有名称递归建卡。本轮未新增QID或Wikipedia↔Wikidata双向核对。

### 外部作者端点与关系交接

| 稳定锚点 | 当前对象 | 来源与候选范围 |
|---|---|---|
| FM-EX03 | [托尔夸托·塔索（Torquato Tasso）](../../../04-knowledge/units/persons/torquato-tasso.md) | 普林斯顿上述书目说明明确文字作者；Tasso→1745年《耶路撒冷解放》插图本的文字责任来自外部目录，原书E:L135未具名。卡内不伪造该行作为Tasso原书出处。 |

57a的设计者／肖像对象、文字作者、出版者、载体与版内作品分别保留；57b的文字作者、设计者、出版者与第二卷分别保留。Treccani Pasquali条目还提到整套插图的刻版者Antonio Baratti，但本轮未核第二卷卷首图的具体署名，暂列刻版者候选，不直接写为该图的已采纳刻印者，不将整套责任机械分配给每一图。两张作品的具体印本和雕版署名仍待核。

### 未决与未成功读取

- Gilmartin论文页码：检索出现意大利文物目录所引305–313，与原书305–310不同；本轮打开的[1200757785-0页面](https://catalogo.beniculturali.it/detail/HistoricOrArtisticProperty/1200757785-0)未显示检索摘要中的完整历史说明，故305–313仅保留为补查线索，未采入KU。JSTOR正文不可读，Crossref对10.2307/877695返回未找到，不据此填DOI。另检出1970年硕士论文，是不同文献，未把其年代、页数混入1974年论文。
- LOC数字化记录和Heidelberg扫描入口未取得可用页面；改用实际读到的普林斯顿目录做1745年书目核对，不称原件扫描已读。
- Waterhouse论文的芝加哥艺术博物馆PDF请求返回403；Conforti论文仅取得检索线索，二者未在本轮写回，也未计入本轮已对齐对象。
- 原先14条主候选的暂缓理由继续有效；本轮解决的是已有KU的署名和版本粒度，不减少这14项。书目身份可用不等于全文已读；人物基本信息增加不等于履历、作品与家庭关系已补足。

### 写回

11张已有KU原位更新，新建1张Tasso卡并登记accepted；共13个数据目标。差异预览和写前内容核对后串行写回，精确before／after存于本机临时目录`C:/Users/001/AppData/Local/Temp/pnp-rev088-alignment/plan.json`。保留已有原书引文及定位、正式relations和accepted的claims／structure；仅更正4条来源句意摘要中的角色表述或重叠书名号。来源本体未改，未提升全卡验证状态。

当前全库803个有效KU，本任务涉及428个：累计381个新建、43个已有有效KU更新、4个旧卡整理后接收；主候选223条映射、4条属性／语境、14条暂缓。REV-087的本地成果保留，当前没有再次提交或推送。

写回后核对12张KU：14条原书摘录与实际文件行段完全对应，48条本地内容／过程链接有效，来源编号不越界，803个有效登记路径存在且不重复。既有内容检查最初提示Gilmartin长标题的YAML折行问题，改为单行保存后12卡检查无确定性发现；字段语义与预览一致，原书原句及定位不变。正式relations、accepted的claims／structure保持；`git diff --check`通过。上述为本轮语义自查与机械核对，不称独立验收。

## 收藏者与肖像身份对齐：REV-089

2026-09-14继续初步对齐，按verify比较图版30b、31a、31b、58a中的人物、爵号、作品和历史收藏。采用实际读到的博物馆说明与作品研究；新出现的必要委托人按ingest建立KU。更新12张已有卡，新增1张人物卡；原书原句、行页和正式relations保持，未将原文与外部关系混合。

### 实际来源与身份裁决

| 对象／原文锚点 | 已读来源与范围 | 本轮裁决 |
|---|---|---|
| FM-P58a.subject1、subject2、creator1、object | [Fabio Sottili，Giuseppe Zocchi e le sue Vedute di Firenze，Uffizi Imagines 13（2025）](https://www.datocms-assets.com/103094/1767175021-imagines-n-13-ottobre-2025_sottili.pdf)，印刷95、99–100、139注21，PDF2、6–7、46；另查看印刷99的图3及图注图像 | Marchese Gerini落实为Andrea Gerini；A. M. Zanetti展开Anton Maria Zanetti，保留原书the Elder。作者、双人组合、Museo Correr及画面形制吻合。作品属性采用约1750、铜板油画及37.5×29 cm；Ca’ Rezzonico只记为2025年研究所载地点，不虚构从Museo Correr转移的时间或所有权。编号按文献印字C1. I. 144保存，非本轮馆藏数据库直接核验。 |
| FM-P30b.subject1、creator1、object | [Cambridge Museums：Finch and Baines](https://www.museums.cam.ac.uk/magic/finch-and-baines)，读两幅作品标签及相邻人物说明；[Fitzwilliam展览标签](https://fitz-cms-images.s3.eu-west-2.amazonaws.com/hockney-large-labels-final2.pdf)，PDF10–11 | Thomas Baines为医生，与Dolci肖像PD.13-1972相配。作者、人物、收藏机构三项吻合；作品约1665–1670年、佛罗伦萨、布面油画，委托人John Finch。Finch本人肖像是另一件PD.12-1972，不与图版30b合并；本轮未采为独立作品成果。 |
| FM-P31b.holder1 | [Lamport Hall：The Hall](https://www.lamporthall.co.uk/see-and-do/the-hall/)，庄园历史正文及末两段；Mezzetti下述第83项 | Gyles Isham确为第十二代从男爵，卒于1976；与17世纪的肖像人物Thomas Isham分开。原书与旧目录所记收藏是历史记录，不把已故收藏者写为当前所有人。 |
| FM-P31b.subject1、object | [Amalia Mezzetti，Contributi a Carlo Maratti，INASA数字化论文](https://www.inasaroma.org/patrimonio/wp-content/uploads/2021/04/07-A.-MEZZETTI-Contributi-a-Carlo-Maratti-02.pdf)，印刷331第83项／PDF79；[Stella Rudolph的2017年展览论文](https://www.nicholashall.art/exhibition/paintings-by-carlo-maratti/)，Apotheosis of Baroque painting及图18 | 作者、Sir Thomas Isham、Lamport及Gyles收藏相配；两篇研究均记1677，Mezzetti记罗马作。目录另提及的复制品不并入本件。人物的具体从男爵代次和生年本轮不作最终裁定。 |
| FM-P31a.subject1、object | Mezzetti同文印刷329第71项／PDF77，阅读条目及查看整页扫描；PDF2页眉核出作者名Amalia Mezzetti | Carlo／Charles Fox肖像约1680年，布面油画；目录的1659–1713及后加题铭支持本人物配对。保留原书Charles Fox和旧目录意大利语形式，不据简称匹配到其他时代同名者。Earl of Ilchester的具体持衔人仍未定，不能用今天持衔人代填。 |

访问日期均为2026-09-14。Mezzetti PDF的印刷315工作年表也作定位阅读；首次页和页眉用于题名及作者核对，未读完整102页论文。Sottili仅阅读所述页段及定位上下文，未读完54页；Fitzwilliam仅阅读本对象相关两页，未读134页标签全集。PDF下载与临时页图保存在本机`C:/Users/001/AppData/Local/Temp/pnp-rev089-sources/`；权威URL及页段保存在各卡sources和本表。没有新增QID或Wikipedia↔Wikidata双向核对。

### 外部端点、关系候选与字段异文

- **FM-EX04**：[约翰·芬奇（John Finch）](../../../04-knowledge/units/persons/john-finch.md)。原书已读范围未直接具名，仅据Cambridge Museums标签登记外部出处。候选为Finch→[贝恩斯肖像](../../../04-knowledge/units/works/carlo-dolci-sir-thomas-baines.md)的委托、Finch↔[Baines](../../../04-knowledge/units/persons/thomas-baines.md)的终身伴侣、Finch↔[Dolci](../../../04-knowledge/units/persons/carlo-dolci.md)的朋友；各端点已链接。不能把馆方“marriage of souls”的修辞转成法律配偶关系。
- 外部赞助候选：[Andrea Gerini](../../../04-knowledge/units/persons/marchese-gerini.md)→[Giuseppe Zocchi](../../../04-knowledge/units/persons/giuseppe-zocchi.md)，据Sottili印刷95的画家受支持记载，两卡互链；时间未细定，不据此认定Gerini委托了双人肖像。Sottili印刷99将双人图像解释为Gerini与Zanetti友谊的表现，此为外部研究者的解释，暂不转成已确认朋友边。
- 图版30b、31a、31b、58a的原书创作、描绘与收藏候选保留原锚点、原词和页行；本轮身份与版本判断只更新端点映射。外部的委托、伴侣、赞助和2025年地点另列，正式关系仍未写入。
- **Baines卒年异文**：Cambridge Museums网页标签为1680，Fitzwilliam同一PD.13-1972号作品的展览标签为1681；卡内分两行标明来源，未取多数裁决。两个入口均属同一馆藏解释链，不计为两个独立历史证据；后续须核生平或一手记录。
- **Isham尺寸异文**：Mezzetti第83项147×121 cm，2017年Rudolph图18为148×121 cm，两值各列出处；未猜测画心／含框差异。Mezzetti给人物生年1657，但检索线索存在其他年份，人物卡暂不采单一生年；Art UK对象页未成功读取，未采其馆藏号或断代为已核事实。
- Mezzetti第71项的Fox题铭涉及父亲Stephen Fox，第83项另述复制品；Lamport官网涉及保护信托及遗赠。上述超出本轮已采字段的亲缘、复制品与产权端点交补足阶段核建；不能把它们当作已经完成的关系。

### 剩余问题与写回

Annan等供片署名检索未获得能将具体照片与法律主体对应的依据，保持no_delta；原先11项供片署名继续暂缓。Ricci《歌剧排练》有多个版本和不同收藏史；本轮未取得足以对应原书Watkin Williams-Wynn爵号、St Asaph语境的记录，不将拍卖页面的别本信息写回。其余书目未取得新证据，延续REV-088缺口。

本轮解决的是已有KU的身份、角色与作品配对；原始241条主候选仍为223条映射、4条属性／语境、14条暂缓。全库有效登记804个，本任务涉及429个：累计382个新建、43个既有有效KU更新、4个旧卡整理接收。初步对齐仍进行中，未启动全面补足、正式关系、知识发现或页面。

模型完成上述判断后，以临时脚本排版并预览差异；14个数据目标（13张KU及accepted）的精确before／after保存在`C:/Users/001/AppData/Local/Temp/pnp-rev089-alignment/plan.json`，写前逐项核对原内容，串行写回。13卡既有内容检查无确定性发现，12条原书摘录与实际行段逐字对应、49条本地链接有效，804个有效路径存在且不重复；旧sources前缀、正式relations及accepted的claims／structure保持。这是语义自查和机械核对，未进行人工或独立验收。成果本地保存，尚未再次提交或推送。

## 供片商号与Lazzarini身份对齐：REV-090

2026-09-14接续初步对齐，使用verify比较原书简称、城市、图版对象与外部实际记录；身份成立后按ingest登记1个人物和3个摄影商号，更新5件作品的供片字段及Tiepolo学习经历。用户原话见REV-090。没有把供片者写成艺术作品创作者，也没有把摄影商号等同于某位实际拍摄者。

### 身份依据与实际阅读范围

| 原文锚点 | 实际采用来源与阅读范围 | 判断及变化 |
|---|---|---|
| FM-E055；E:L180–183，xvii | [Francesco Sorce，Gregorio Lazzarini，DBI 64（2005）](https://www.treccani.it/enciclopedia/gregorio-lazzarini_(Dizionario-Biografico)/)：完整生平与参考文献，重点为拒绝迁居罗马、Tiepolo学习及生卒段；[英文Wikipedia](https://en.wikipedia.org/w/index.php?title=Gregorio_Lazzarini&oldid=1365386914)：Life、注释与文献；[Wikidata Q1384461](https://www.wikidata.org/wiki/Q1384461)：身份、生卒与英文站点链接 | DBI明确记至少两次拒绝迁居罗马，补上REV-086缺少的特定行为线索；结合时代、地域和画家身份，落实为Gregorio Lazzarini。Wikipedia的Edit links实际进入Q1384461，Wikidata英文站点链接返回同页，双向身份成立。DBI生年1655与英文Wikipedia／Wikidata的1657并列，不选一侧掩盖异文。 |
| FM-H04；E:L164，xvi；图版41b、44 | [Ditta Osvaldo Böhm，1983年摄影目录](https://wwwuser.gwdg.de/~fotokat/Fotokataloge/Naya_Boehm_1983_1_l.pdf)：PDF3标题、PDF4／印刷V导言、PDF5／印刷VII说明、PDF87／印刷161 Frari条；印刷161另查看页图 | 公司自称Ditta Osvaldo Böhm、O. Böhm Fotografo-Editore，并要求Foto Böhm署名；地域与艺术翻拍业务吻合。Frari的Pesaro纪念碑有对应照片条目。原书Böhm按摄影出版商号登记institution；约1910年活动起点依据商号自身目录。 |
| FM-H24；E:L172，xvi；图版28a | Zeri实际照片记录[212704／照片档案号522770](https://catalogo.fondazionezeri.unibo.it/scheda/fotografia/212704/)及[212702／522768](https://catalogo.fondazionezeri.unibo.it/scheda/fotografia/212702/)：题材、作者、摄影者、地址、背章和年代字段 | Cagnacci、维也纳艺术史博物馆、《克娄巴特拉之死》与原书图版28a相合；署名Foto A. Villani - Bologna及A. Villani e Figli，另一张背章展开公司名称。登记摄影公司，未指定Achille或Vittorio个人。 |
| FM-H01；E:L164，xvi；图版19a、25 | Zeri[204958／照片档案号500600](https://catalogo.fondazionezeri.unibo.it/entry/photo/204958/)实际摄影者、背章、地址与题材字段；[Paris Musées档案PPEX1967(1)-PH](https://www.parismuseescollections.paris.fr/fr/petit-palais/archives/photographies-de-l-exposition-toutankhamon-et-son-temps-au-petit-palais-en)作者及内容介绍 | Zeri照片题材为Orazio Gentileschi《公共幸福寓意》，与图版25的作者、题材相合；背章使用Agraci. Arts Graphiques de la Cité和巴黎地址，Paris Musées采用相同展开名。登记摄影商号，不推定具体经营者或法人形式；此前INHA的photographe角色称谓不足以单独证明是自然人。19a供片仍直接据原书编号，未据25的照片记录核同19a底片。 |

来源访问日均为2026-09-14。Böhm目录共125页，只读上述页段及检索定位，不称全文阅读；Villani和Agraci采用实际照片元数据，未作本书图版与原底片视觉核同。Zeri网页工具超时、直接请求证书校验失败后，通过仅针对这些公开页面的请求取得实际HTML；未修改系统证书或持久网络设置。临时PDF、页图及部分HTML在`C:/Users/001/AppData/Local/Temp/pnp-rev090/`，权威链接、记录号和阅读范围保存在本段及各卡sources。

Wikipedia／Wikidata互相链接及复用信息，不计两份独立的生卒事实证据；两条Zeri照片也不因有两个记录号就自动成为两组独立证明。DBI说明其拒居罗马的记载出自Da Canal；本轮未读该早期传记原件。

### 内容、关系与版本边界

- FM-R14中的Lazzarini端点现映射到新卡，原文谓词、否定和评论者归属保持。Waterhouse将“畏惧竞争”作为解释的推测，不能转成确定动机，也不能把拒居罗马变成在罗马任职。
- Lazzarini→Tiepolo的教学事实来自外部传记，已在两卡分字段互链；这是外部关系候选，与FM-R14原书评论分开。全文实际阅读后仅采纳本次身份和必要师承，不把页面全部人物及作品递归登记；详细家庭、履历、作品清单仍交补足。
- Böhm的3519和180 NV是同一纪念碑的不同照片记录，后者属于Naya旧档案；不能任选其一当作41b所用底片。图版44供片依据原书同一商号署名，未在这部教堂目录中核定其底片。
- Villani的522770、522768及Agraci的500600是照片档案号，不是绘画藏品号；Villani另一照片的底片24509及其1967–1980年断代不倒填到本书。供片署名、照片作者和底片权利各按自身证据范围处理。
- 新机构卡补入原书图版目录与图片来源两组原句，使作品题名、编号和供片署名能回查；作品卡原有创作者、收藏者及其他sources保留。尚无正式relations新增。

### 当前暂缓项与交接

4条主候选解除暂缓：FM-E055、FM-H01、FM-H04、FM-H24。初始241条现为227条映射KU、4条属性／语境、10条暂缓。本轮新增4张KU、更新6张已有KU；全库808个有效KU，本任务433个（累计386个新建、43个既有有效KU更新、4个旧卡整理接收）。

剩余10条为FM-P05博尔盖塞双胸像的具体版本、FM-P68a三幅未具名总督肖像，以及FM-H02 Annan、H03 Balelli、H05 Cacco、H09 Gilchrist、H12 Mansell-Alinari、H13 Mansell-Anderson、H14未指城市的National Gallery、H16 Rossi。10仅指初始主候选暂缓，其他卡内爵号持有人、版本和角色仍待初步对齐。

本轮另读[威尼斯国家档案馆Palazzo Besarel展览记录](https://mostre.archiviodistatovenezia.it/mostre-documentarie/la-stagione-della-liberazione/mostra-la-stagione-della-liberazione/il-ritorno-alla-normalita-dopo-la-liberazione/dimore-e-palazzi-dopo-la-liberazione-dissequestri-risarcimenti-e-problemi-abitativi/6-3-la-liberazione-di-palazzo-besarel/)，记Giorgio Cacco（1907–1977）、1946–1947年开设工作室及1948年照片背章Foto Cacco Giorgio，但所拍对象不是本书列出的图版；保留候选，不据此指定本书供片者。其他未决项未取得足以改判的新证据，不把搜索未命中当作不存在。

10张卡及accepted的写前／写后内容保存于临时`plan.json`，先预览差异并核对写前内容，再串行写回。REV-087–089的既有本地工作保持；本轮未提交、推送或启动全面补足、正式关系、发现及页面。

写回检查：10张受影响KU的21条原书摘录与实际行段逐字一致，51条本地链接有效，来源编号未越界；808个有效登记路径存在且无重复，原sources前缀、正式relations及accepted其他内容保持。既有内容检查未报确定性缺陷，`git diff --check`通过。模型对本轮采纳内容作语义自查；这不是独立验收或人工校验。

## 关联对象集中对齐：REV-091

2026-09-14按用户提高效率的要求，将有共同来源的作品、人物、供片商号及收藏空间合并处理；模型比较实际记录，辅助脚本只排版、保存写前差异和检查。不再反复搜索没有新线索的同一暂缓项。新增6个必要端点、更新14个已有KU，一次写回20张卡；仍属初步对齐及必要事实补证。

| 对象组 | 实际阅读来源及结论 |
|---|---|
| FM-H03、FM-P33b | [Macerata Musei，Galleria dell’Eneide](https://musei.macerata.it/opera/galleria-delleneide/)完整对象说明、作者与技术字段明确Studio fotografico Balelli、Macerata、1851–1972及该宫画廊照片；与原书图版33b、L95和供片L164匹配。供片者按工作室登记，解除主候选暂缓；未指定Carlo／Alfonso个人或具体底片。画廊空间仍是place，照片题材不把它变成摄影作品。 |
| FM-P33a及Solimena | [MFAH作品2000.92](https://emuseum.mfah.org/objects/48122/visit)完整作品字段、Description、Provenance与展览条目，加上上述原址馆方去向说明：原书笼统Dido and Aeneas对应The Royal Hunt of Dido and Aeneas。作者规范为Francesco Solimena，约1712–1714、303×321 cm，原为Raimondo Buonaccorsi伯爵的宫内埃涅阿斯画廊所作。建立委托人和休斯敦美术馆端点，作品／原址／委托人互链；原始路径和题名保留，馆方展开题名单列。伦敦NG6397是另一件迎接埃涅阿斯与丘比特的作品，不合并。 |
| FM-P30a、Ralph及Jerome Bankes | [NT 1257045](https://www.nationaltrustcollections.org.uk/object/1257045)作品字段、Summary、Provenance、题铭与作者：[NT 1251462](https://www.nationaltrustcollections.org.uk/object/1251462)的题名／Summary展开20世纪收藏者为Henry John Ralph Bankes（1902–1981）；[NT 1257049](https://www.nationaltrustcollections.org.uk/object/1257049)人物说明和题名确认17世纪Sir Ralph（约1631–1677）。原书20、30a所记收藏者保留原路径并展开全名；另建17世纪兄长端点，避免将其可能委托弟弟肖像的行为归给20世纪收藏者。作品作者Stanzione、约1655、那不勒斯、尺寸及NT号分别保存。 |
| FM-P20、Massimi、Velasquez及Kingston Lacy | [NT 1257142](https://www.nationaltrustcollections.org.uk/object/1257142)作品、Caption、Summary、Provenance及文献列表；[庄园历史](https://www.nationaltrust.org.uk/visit/dorset/kingston-lacy/the-history-of-kingston-lacy)相关收藏者、20世纪及National Trust ownership段。作者、对象、Kingston Lacy和原书收藏者吻合，落实1649–1650、759×610 mm及NT号；补入1819/20年购入者William John Bankes及1981年接收机构National Trust的端点。题铭、委托语境和历代收藏分开；馆藏页引用Haskell，不能当作与本书完全独立的整条传承证明。 |
| FM-P34、Juan de Pareja及Velasquez | [Met 1971.86](https://www.metmuseum.org/art/collection/search/437869)页面导言、Artwork Details和已显示音频文字稿：作者全名Diego Rodríguez de Silva y Velázquez；1650、布面油画81.3×69.9 cm、1971购入，描绘对象约1608–1670。Pareja为画家，绘像时被作者奴役；解放文件与至1654年的生效安排分字段互链。没有用普通合作／师承关系替代这种人身关系。页中未实际展开的Catalogue Entry、详细Provenance和References不称已读。 |

以上均于2026-09-14访问。NT绘画总览另遇WAF，转用已成功读取的具体馆藏记录；未采用失败页面作正文依据。MFAH与Macerata说明可互证作品身份和去向，但离藏时间不同：MFAH记1960–1962间散出，Macerata把陈设散出关联到1967年整体销售；未确证是否分批处置，不把两者拼成一条确定时间线。当前卡内未写单一离藏年份。

新增端点：[Balelli工作室](../../../04-knowledge/units/institutions/studio-fotografico-balelli.md)、[Raimondo Buonaccorsi](../../../04-knowledge/units/persons/raimondo-buonaccorsi.md)、[休斯敦美术馆](../../../04-knowledge/units/institutions/museum-of-fine-arts-houston.md)、[17世纪Sir Ralph Bankes](../../../04-knowledge/units/persons/ralph-bankes-1631-1677.md)、[William John Bankes](../../../04-knowledge/units/persons/william-john-bankes.md)、[National Trust](../../../04-knowledge/units/institutions/national-trust.md)。除Balelli外，五个对象来自外部补证，未伪造章页或原书引文。只采纳本组身份及直接必要关系；完整家谱、其他收藏者链、所有作品与参考文献原文仍交补足，不递归扩张网页人名。

### 保留的判断边界

- Jerome的兄长身份有据，肖像委托为馆方“Probably”推定；两种确定性分别记录，不生成确定委托边。其生年1635／1636及Sir Ralph约1631保留限定。
- Massimi绘像时的教廷侍从身份与后来枢机头衔分开；未倒填为1649–1650年已任枢机。William John取得年份采用Provenance的1819/20，不将Caption的1820当成另一笔购买。
- 本书National Gallery的供片身份仍未定；Met确认画作身份和现收藏，不能因此把Met填成原书供片者。Annan家族公司记录、Mansell代理线索虽有检索结果，仍未落实本书复合署名的具体分工；Gilchrist、Beaufort检索无可据新结论，不改判。
- 当前主候选为228条映射、4条属性／语境、9条暂缓。9项：FM-P05、P68a、H02、H05、H09、H12、H13、H14、H16；其他卡内版本、简称和具体角色的缺口仍在，9不是全库缺口总数。没有新增QID、Wiki双向核对或正式relations。

写回前后的21个数据目标（20卡及accepted）保存于本机临时`C:/Users/001/AppData/Local/Temp/pnp-rev091/plan.json`，预览后逐项核对写前内容并串行写回。20卡的23条原书摘录与行段逐字一致、88条本地链接有效、来源编号未越界；814个有效路径存在且不重复，原sources前缀、正式relations及accepted非units内容保持，既有内容检查无确定性发现。过程是模型语义自查及机械核对，不称人工或独立验收。

全库814个有效KU，本任务439个：累计392个新建、43个既有有效KU更新、4个旧卡整理接收。既有本地成果保留，未提交或推送；下一步集中核对其余已登记对象的身份／版本，难解主候选按新线索处理，不让单项长期卡住全部对象。

## 作品与收藏链集中对齐：REV-093

2026-09-14，在REV-094同步后的`649c1a5`基线接续REV-093目标。集中处理27张KU：更新21张，新增6个必要端点。verify完成身份比较；同时取得的有据内容按enrich分字段保存，不表示整体对齐或全面补足结束。原书sources与逐字摘录保持，来源资产未改写。

### 身份、来源与实际阅读范围

| 原文锚点 | 实际来源与范围 | 判断及处理 |
|---|---|---|
| FM-P46，E:L124，xv | [BM 1874,0808.43](https://www.britishmuseum.org/collection/object/P_1874-0808-43)，搜索工具返回完整索引记录，包括技术字段、Curator’s comments、书目与入藏字段；直接页面和HTTP均403 | 作者、被描绘者、家庭群像与保管机构共同对应。Pellegrini展开为Giovanni Antonio Pellegrini；Pierre Motteux对应馆方Peter Anthony Motteux。作品为纸本素描，261×352 mm，1874入藏。评论1708–13与数据库1690–1741并列；不称已知油画。使用馆方索引内容，不称实时页面完整打开。 |
| FM-P49a，E:L127，xv | [艺术家M0xy0EO4pl](https://www.sammlung.pinakothek.de/de/artist/M0xy0EO4pl)完整人物索引、[馆藏4666](https://www.sammlung.pinakothek.de/de/artwork/Y0GRkdB4RX)完整对象字段；[GND118712411](https://www.deutsche-biographie.de/gnd118712411.html?language=en)身份摘要和异名区 | 画布、347×311 cm、1806年来源及馆藏分部按记录保存。馆方题名将原书王储落实为Johann Wilhelm，画中角色为选侯继承人；不由教育寓意图推定现实师承。GND用于身份，不称完整NDB／ADB传记已读；画作年代未给，不反推。 |
| FM-P45，E:L123，xv | [Kress K2149](https://www.kressfoundation.org/kress-collection/artwork/84f51f076ea69e90ef971adebc587d9802d0a5f3d6888bb5d9f5554435356c3f)实际HTTP全文字段及流传；[NCMA说明](https://ncartmuseum.org/wp-content/uploads/2021/06/Curator_Intro_Batoni_Triumph_of_Venice.pdf)实际两页PDF全文；[Treccani Foscarini简传](https://www.treccani.it/enciclopedia/marco-foscarini/)与[Kress历史](https://www.kressfoundation.org/Kress-Collection/History)全文 | 题名、Batoni、Kress收藏与NCMA共同配对为K2149／GL.60.17.60。规范作者全名；分开1737年完成、Foscarini委托、罗马委托地点、威尼斯宫安置、1956-11-30基金会购入与1961年捐赠。基金会不是原始赞助人；委托地点不自动等于有证制作地点。 |
| FM-P52a，E:L130，xv；供片E:L168，xvi | [NPG mp02907](https://www.npg.org.uk/collections/search/person/mp02907/owen-macswinny-or-swinny)简介与8件肖像索引；[mp07669](https://www.npg.org.uk/collections/search/person/mp07669/peter-van-bleeck?role=art)题头与首页20项；[D5204](https://www.npg.org.uk/collections/search/portrait/mw39557/Owen-MacSwinny-or-Swinny)对象字段 | P. Van Bleek对应Peter van Bleeck，Owen McSwiny对应Owen MacSwinny；机构确定为伦敦国家肖像馆。索引中NPG1417是after Peter van Bleeck的油画，D5204是本人制作的美柔汀；不能凭同名和馆名选一个号。仅落实人物和机构，作品版本继续待核。 |
| FM-P40a，E:L110，xiv | [Uffizi On Being Present](https://www.uffizi.it/en/online-exhibitions/on-being-present)，直接读取第15项全文及第16项中三名乐师比较段 | A. D. Gabbiani对应Anton Domenico Gabbiani。皮蒂宫《四名宫廷侍从》3827和学院美术馆《三名宫廷乐师》2802均不能直接等同本书《乐师群像》；不采两作尺寸、年代或人物名单。学院美术馆导览PDF未成功读取，不列为采用来源。 |
| 图版49a收藏链外部端点 | [Pinakothek馆方历史，2026-04-07](https://www.pinakothek.de/de/alles-gute-zum-geburtstag-alte-pinakothek)，收藏汇集、1836年开放与管理机构段；并用馆藏4666 | 历史杜塞尔多夫选侯画廊与今日老绘画陈列馆分别登记institution；前者按历史收藏机构而非某座建筑建模。1806是转入慕尼黑收藏的日期，不写成1836才开放的博物馆已于1806接收。 |
| FM-P52b，E:L130，xv | [Zeri作品URL69391／条目67084](https://catalogo.fondazionezeri.unibo.it/entry/work/69391/)完整实际目录；[NPG Tillotson图像目录](https://www.npg.org.uk/collections/search/personExtended/mp04507/john-tillotson?tab=iconography)题头与末段；[Landmark Trust Fox Hall History Album](https://www.landmarktrust.org.uk/globalassets/3.-images-and-documents-to-keep/history-albums/fox-hall-history-album.pdf)PDF90及重复的118全文与图注；[Compton Verney](https://www.comptonverney.org.uk/our-story/history-of-compton-verney/)Sir Peter Moores完整纪念简介 | 三位作者展开为Giovanni Antonio Canal、Giovanni Battista Cimaroli、Giovanni Battista Pittoni；Tillotson为John，1630–1694。NPG依据1970年目录分出Moores原画和其他版本；Landmark图注明确三人分别画建筑、风景、人物。MacSwinny的系列委托约1725–29年，与当代收藏者Moores分开；Moores的2003骑士称号不倒填为本书出版时称号。 |

实际访问日均为2026-09-14。BM索引不是独立于馆方记录的新研究；Kress与NCMA共用同一收藏解释链，不能仅按域名数当作独立事实证据。未新增QID或Wikipedia全文阅读／双向核对声明。

Zeri直接请求出现本机证书链错误后，仅为读取此公开目录采用一次不校验证书的请求，未更改持久网络设置。Landmark PDF90和118内容重复，只算一处证据；未称整部图册全文已读。NPG的1970版本判断为2009目录转述，本轮未读取Croft-Murray原书。Zeri该条记录列218×138.5 cm及1993年Newhouse Galleries，与Moores原画尚未核同，因此仅用其作者身份字段，不把尺寸、年代、Newhouse位置写入本书作品。

### 新端点与关系交接

| 稳定锚点 | 新知识元 | 必需角色 |
|---|---|---|
| FM-P45.ext.commissioner | [Marco Foscarini](../../../04-knowledge/units/persons/marco-foscarini.md) | 委托人；驻罗马1736–40、总督1762–63分列。 |
| FM-P45.ext.original-site | [Palazzo Venezia](../../../04-knowledge/units/places/palazzo-venezia.md) | 1737年完成后的安置建筑，与威尼斯共和国政治实体分开。 |
| FM-P45.ext.donor | [Samuel H. Kress Foundation](../../../04-knowledge/units/institutions/samuel-h-kress-foundation.md) | 1956购入、1961捐赠；不等同原书集合性Kress Collection。 |
| FM-P49a.ext.subject | [Johann Wilhelm](../../../04-knowledge/units/persons/johann-wilhelm-elector-palatine.md) | 教育寓意图的描绘人物；头衔不是现实授课关系。 |
| FM-P49a.ext.repository | [Alte Pinakothek](../../../04-knowledge/units/institutions/alte-pinakothek.md) | 馆藏4666所属博物馆，机构与建筑分开。 |
| FM-P49a.ext.former-collection | [Düsseldorf Electoral Picture Gallery](../../../04-knowledge/units/institutions/dusseldorf-electoral-picture-gallery.md) | 1806年的来源收藏，不与今日Kunstpalast无据合并。 |

6个对象均以实际外部来源登记，不伪造原书引文；相关作品与机构字段已链接，正式relations尚未写入。原书图版45的创作、收藏和位置候选保持；外部委托、安置、购入、捐赠另以以上锚点及卡内来源交接。原书46的创作、描绘、保管由BM该素描记录补证；馆方对Motteux与画家相识途径的两种猜测不转为朋友或委托事实。1712年重返商业保留“似已”的限定。

FM-P52b的三名共同作者原书已有，外部补入分工：Canaletto→建筑、Cimaroli→风景、Pittoni→人物。各人物卡与作品卡同步分字段；这是该画具体合作，不能泛化为终生合作。FM-P52b.ext.commission记录MacSwinny组织委托，端点复用此前已对齐的[Owen MacSwinny](../../../04-knowledge/units/persons/owen-mcswiny.md)；范围为约1725–29年的纪念画系列，不作为单画的精确完工年。Tillotson为已故纪念对象，作品是绘画，不能建立Tillotson本人委托、实际墓建筑或安葬关系。NPG所记Moores原画属历史收藏证据，不证明今天仍在Moores私人收藏中。

图版49a的Palatinate是人物称谓中的地理限定；已将原卡“描绘地点／对象”改为“原书人物称谓中的地区”，不转成描绘景观的正式关系。图版40a和52a的版本待核，不能对未确定实物的年代、材质、摹制关系定稿。9项原始主候选仍为FM-P05、P68a、H02、H05、H09、H12、H13、H14、H16；9不是全部版本或内容缺口数。

NCMA两页说明中的Leonardo Loredan生卒／任期1436–1531／1501–1531存在疑点，未采该日期或扩写整幅寓意人物系统。Kress与NCMA索引对1916拍卖项、Butterfield生年有异文，尚未采入字段；后续如补全流传史应核实相应记录并建端点。BM早期收藏者同样留待作品流传补足。并未完成全部图版的视觉核同，馆藏身份比较不称图像验证。

### 写回与状态

逐项语义判断后，阅读拟写回正文并预检临时`C:/Users/001/AppData/Local/Temp/pnp-rev093/plan.json`与差异，同一文件串行写回；图版52b接续计划另保留`tomb-plan.json`的中间before／after。累计27卡、27条原书摘录、119条本地链接及来源编号检查通过；820个有效路径无重复／缺失，原sources前缀、已有正式relations及accepted非units内容保持，既有内容检查无确定性发现。这是模型语义自查与机械核对，不称人工或独立验收。

当前全库820个有效KU，章前任务445个：累计398个新建、43个既有有效KU更新、4个旧卡整理接收。初始241条仍为228条映射、4条属性／语境、9条暂缓。图版45、46、49a的可用身份带具体缺口交后续补足；其余对象继续集中对齐。整体初步对齐、全面补足及关系定稿仍未完成，本轮业务成果未提交或推送。


## 章前对齐接续：肖像与收藏机构

2026-09-14，REV-095提交`1f6a67c`后继续REV-093目标。上一轮完成提交及远端一致性实测，属于有效进展；本轮继续语义工作，不重复提交。共处理15张卡：12张已有卡与3个新增必要端点。柏林绘画馆复用既有`institutions/gemaeldegalerie-berlin.md`，保留其第一章关系与来源；当前process_ref指向本段，第一章处理入口仍在卡内。

### 对象判断与实际来源

| 原文锚点 | 实际阅读 | 结论与边界 |
|---|---|---|
| FM-P53b，E:L131，xv | [SMB Streit.1／obj:863940](https://search.smb.museum/en/object/obj-863940?objectType=Gem%C3%A4lde&sammlungen=Gem%C3%A4ldegalerie)实际HTTP200：完整对象字段、说明及书目；[NPG Amigoni mp06613](https://www.npg.org.uk/collections/search/person/mp06613/jacopo-amigoni)题头与14项肖像索引 | Amigoni展开为Jacopo Amigoni。Streit是1687–1775年的商人、收藏家，1697–1701就读灰修道院中学、1709迁威尼斯。1739年自画像委托应准确表述为“委托画家为自己画像”，不写成Streit自行创作。作品为97.9×78.6 cm布面油画；1758赠校与1964起基金会出借分列。 |
| FM-P53a，E:L131，xv | [Lombardia 4y010-09081](https://www.lombardiabeniculturali.it/opere-arte/schede/4y010-09081/)完整网页；[15页SIRBeC PDF](https://www.lombardiabeniculturali.it/opere-arte/schede-complete/4y010-09081/)定向读取PDF2–5的对象、收藏、年代、技术与评论；[ICCD聚合记录](https://catalogo.beniculturali.it/detail/Lombardia/HistoricOrArtisticProperty/4y010-09081_R03)全文 | 舒伦堡肖像是素描；387×303 mm为高×宽，网页未标方向的303×387不倒读。库存号4884/5 E 82/5与目录号4y010-09081分开。年代字段约1730–1735、评论1738并列。Piazzetta卡原先“两幅绘画”及此肖像“绘画作品”改正，既有作品清单保留。 |
| FM-P48b原设计者B. Nazari，E:L126，xv | [Fiorenzo Fisogni的Nazari人物辞典](https://www.treccani.it/enciclopedia/bartolomeo-nazari_res-1dbdf466-03ed-11e7-b5f4-00271042e8d9_(Dizionario-Biografico)/)正文及书目全部读取 | 原设计者初步对应Bartolomeo Nazari，年代、威尼斯肖像及版画设计身份吻合；另有明确Schulenburg委托。生卒采用辞典1693-05-31／1758-08-24。尚未找到48b确切印本记录，辞典身份不等于该件刻印细节已核。 |
| FM-P56，E:L134，xv | [Met 69.551(17)](https://www.metmuseum.org/art/collection/search/676336)完整对象字段；[CMA 1978.136.17](https://www.clevelandart.org/art/1978.136.17)完整目录字段 | Marieschi对应Michele Marieschi（1710–1743），1741年Campo San Rocco蚀刻。两馆是不同印本，只采作品层面的作者、技法和年代，不把它们的尺寸、入藏、现藏或库存号写成本书印本。Met题名将教堂立面记为画家设想，不转成实景建造事实。 |

原书图版53另实际查看`02-sources/01-book/CHP-11.pdf`第15页（同页亦见CHP-10.pdf第42页）：53b为白色假发、坐姿、宽袖肖像，与SMB所述52岁Streit坐姿图像特征相符；53a为舒伦堡半身素描。此为指定图版的查看，不表示已执行第十／十一章或完成整书图像审核；未声称已视觉比对全部外部原图。图版标签将作者拼作Amiconi，原书目录Amigoni仍保留。检索时定向看到CHP-11.pdf第20页的Bartolommeo Nazari与Schulenburg上下文，只作同书人物参照，未作为章前原句倒填或宣称该章已处理。

实际访问均为2026-09-14。SMB目录明确有多个年龄的Streit肖像，本轮通过作品说明和原书坐姿特征核对1739年的52岁版本，不采1717年30岁版本字段。NPG与SMB支持约1682生年；检索另见NGA的1675标年，未读其完整研究依据，留作Amigoni生年异文后续核实，不把所采约年宣称为已解决争议。

Lombardia与ICCD为同一地区目录的原始发布和聚合，只有一组事实证据；正文的1738与字段1730–1735是来源内部异文。评论将画像写为“autoritratti”但上下文明确是艺术家为Schulenburg绘像，不误写成Piazzetta自画像。评论对早期Belgioioso收藏为“可能”，未升级为无条件所有权。PDF5的1943年赠送、捐赠人和市有产权尚未整条采纳，后续流传补足须建立相应端点。

Prado直接请求403，不能称整篇人物传记已读；Art UK的Moor Park对象403，未采二手转录的PCF1、尺寸或日期。Met直接请求429，采用web工具实际返回的完整对象字段，未作可得原图声明。Lombardia本机证书链失败后只在一次公开PDF请求中停用证书核验，未改持久设置。Wikipedia、Wikidata搜索命中没有成为本轮身份验证，未新增QID或双向核对状态。

### 关系证据与新增端点

- FM-P53b.ext.commission：Streit→Amigoni→Streit.1，1739年；同一人分别为委托人和描绘对象。
- FM-P53b.ext.gift：Streit→灰修道院中学，1758年赠画；FM-P53b.ext.loan：Streitsche Stiftung→Gemäldegalerie，1964年起借展。借展与赠予是不同权利行为，基金会与学校、博物馆不合并。
- FM-P53a.ext.adviser：Piazzetta→Schulenburg，为其评估购藏、估价；肖像创作关系与顾问关系分开。服务威尼斯共和国属于Schulenburg军职，不代表出生地或现代国籍。
- FM-P48b.ext.commission：1733年Schulenburg委托Nazari绘骑马肖像；新建[失传骑马肖像](../../../04-knowledge/units/works/nazari-equestrian-portrait-of-schulenburg.md)，不同于Piazzetta的53a素描。1744年随行邀请另作履历记录，不从同行自动推导朋友或师承。
- 新增[施特赖特基金会](../../../04-knowledge/units/institutions/streitsche-stiftung.md)、[斯福尔扎城堡素描室](../../../04-knowledge/units/institutions/gabinetto-dei-disegni-castello-sforzesco.md)两个机构端点；[柏林绘画馆](../../../04-knowledge/units/institutions/gemaeldegalerie-berlin.md)复用既有卡。素描室是机构，城堡是建筑空间。

Nazari辞典明确区分1717年与Angelo Trevisani合作和传统所谓师承，并倾向排除Fra Galgario正式师承；未将风格相似、造访画室、受影响转成老师关系。亲属、其他失传作品、收藏者和同僚虽有记载，本轮仅采服务于上述已登记作品／人物链的事实；没有展开全篇百科外链。进一步补足时仍需审视与本书对象有关的关系，不以本轮字段已有链接宣称关系齐全。

### 写回与交接

模型逐项形成拟写回正文后，临时`C:/Users/001/AppData/Local/Temp/pnp-rev093-next/plan.json`保留16个目标的before／after及差异。预检发现柏林绘画馆已有不同转写路径，已在写回前取消重复新建、改为复用；全部输入指纹一致后串行写回。15卡的14条原书摘录逐字一致、81条本地链接有效、来源序号无越界，原sources及正式relations保留，823条有效登记存在且无重复；既有内容检查无确定性发现。属于语义自查及机械检查，不称人工或独立验收。

当前章前任务实际涉及449个KU：401个新建、44个既有有效KU更新、4个旧卡整理接收；全库823个有效KU。初始241条仍为228映射、4属性／语境、9暂缓。以上有据内容与关系证据已保存，整体对齐、全面补足与正式关系阶段仍未完成；本轮未提交推送。


## 版画作者与萨索身份

2026-09-14，继续REV-093目标；同步基线为9310fb7。初步对齐和明确缺口补足合并检索、分别解释，不提前宣称正式关系完成。

### 来源与实际阅读

- Met对象335623：实际阅读作品说明、完整Artwork Details及可得字段；[51.501.2843](https://www.metmuseum.org/art/collection/search/335623)是Met印本，非书中图版已知印本。馆方记1769年、蚀刻与雕版；Volpato刻制、Bianconi提供绘图并负责墓建造、Tesi设计墓。
- Rijksmuseum [200471954／RP-P-2004-543](https://id.rijksmuseum.nl/200471954)：读取linked-art的责任者、名称、描述、年代和尺寸字段。馆方2015-08-27说明明确Algarotti委托朋友Tesi设计墓、Bianconi执行、墓在Pisa Camposanto。该记录是另一印本，其637×457 mm字段为plaatrand（版面／版边），不是Met的裁切纸张62.5×43.4 cm；两组尺寸均不写成本书图版的物理尺寸。两个馆藏分别管理印本，但不能据两域名断言其历史解释相互独立。
- [Giorgio Marini撰Volpato传记](https://www.treccani.it/enciclopedia/giovanni-volpato_(Dizionario-Biografico)/)：阅读完整正文和Fonti e Bibl.。原姓Trevisan、采用外祖母姓Volpato、别署Jean Renard。辞典依据洗礼登记记1735-05-20出生，Met目录记1732，分别保留。1762年受Bartolozzi劝说迁Venice、在其工作室工作；不将“在工作室工作”改写为师徒。文中Bartolozzi迁伦敦年份写1754，与段落次序不合，本轮不采纳该年。读到的其他家属、作品、瓷器厂沿革和教宗墓委托细节尚未纳入本轮内容，不以整篇可读推定全部补足；Volpato对Canova的支持先作有据一般关联，不能替代具体委托边。
- [Correr Canova手册](https://correr.visitmuve.it/wp-content/uploads/sites/3/2026/01/DOWNLOADS-Collezione-Canoviana-del-Museo-Correr-ITA-2020.pdf)：8页文字完整阅读，含图注与末页信息。采用姓名、生年、卒日、去世城市、雕塑与绘画活动；未列Swajer肖像单件目录，所以不能凭此确定该肖像材质、尺寸、年代或库存号。商业复制品网页出现该像，但未采用为馆藏核验。不同作品的大量例举不自动扩大本次端点。
- National Gallery [NGA8](https://www.nationalgallery.org.uk/research/research-centre/archive/record/NGA8)及[NGA8/1](https://www.nationalgallery.org.uk/research/research-centre/archive/record/NGA8/1)：阅读完整收藏级、系列级目录的身份史、内容、保管史及相关材料；不是原信全文。两页属同源档案说明。Sasso为Venice艺术商人，Hume为1749–1838年的收藏家、政治人物及准男爵。1787–1805是包含多位通信者的系列范围，不据此延伸为Sasso个人通信起止。目录明确区分拟售、购入、运输；未读具体信件时不产生具体作品购藏边。
- [Laura Popoviciu博士论文（2014）仓储6353](https://sas-space.sas.ac.uk/6353/)：核书目；第二卷实际读取印刷p.280图35目录及p.311图35题注（PDF58、89），确认Alessandro Longhi—Giovanni Maria Sasso—Museo Correr—I.760。检索还返回附录题名和其他图注，仅作定位，不表示整篇论文或信件全文已读。本轮没有查看外部原图，不称完成视觉比对。

### 身份与端点裁决

FM-P60.creator1的G. Volpato落实为Giovanni Volpato；题材、责任者、Pisa地点和1769版画相符，具体印本待证。新建Carlo Bianconi，不能复用第一章Giovanni Ludovico Bianconi；新建Mauro Antonio Tesi，依据两馆同一墓的设计角色与姓名变体配对。墓本身沿用work，Camposanto是安置它的建筑空间，单独登记place，不生成同名管理机构。

FM-P58b.subject1落实为Giovanni Maria Sasso，既有肖像路径保留，标题和人物链接更新；新增Abraham Hume满足已采纳通信、购藏服务事实的端点。FM-P59a.creator1的Canova规范为Antonio Canova；仅完成人物初步身份，不替代该件肖像核验。FM-P55b.creator2规范Francesco Bartolozzi，版画《村景》的具体版本及原设计—刻制链仍须另核。

### 关系候选交接

| 锚点／来源范围 | 起点 → 角色 → 终点 | 限定与下一步 |
|---|---|---|
| FM-P60；Met | Volpato → 刻制 → 阿尔加罗蒂墓版画 | 1769；原书署名与外部刻制角色并列，具体印本未定 |
| Met、Rijks外部记录 | Carlo Bianconi → 提供绘图 → 阿尔加罗蒂墓版画 | 不混作刻版者；具体绘图实物版本未确定，不新建假定存世草图 |
| Met、Rijks外部记录 | Mauro Antonio Tesi → 设计 → 阿尔加罗蒂墓 | 不从Rijks“after sculpture by”直接推定亲自雕凿 |
| Met、Rijks外部记录 | Carlo Bianconi → 负责建造 → 阿尔加罗蒂墓 | 具体雕塑执行者与建造年代待进一步来源；不由印本1769倒填墓年代 |
| Rijks外部说明 | Algarotti → 委托设计 → Tesi；Algarotti ↔ 朋友 ↔ Tesi | 有直接文字；不延伸为全部工程出资 |
| Met、Rijks外部说明 | 阿尔加罗蒂墓 → 安置于 → Camposanto | Camposanto属于Pisa；不是馆藏机构 |
| Volpato辞典 | Volpato → 工作于 → Bartolozzi工作室；Volpato → 支持 → Canova | 1762迁Venice；工作室活动与师承分开，支持关系具体类型后续按证据细化 |
| FM-P58b与论文图35 | Alessandro Longhi → 创作 → 萨索肖像 → 描绘 → Sasso | I.760为论文所列馆藏号；原书及外部题注分别保留 |
| NGA8、NGA8/1外部目录 | Sasso ↔ 通信 ↔ Hume；Sasso → 购藏服务 → Hume | 未把系列所有作品或所有日期套到个人；具体信、交易另核 |

上述候选与有据内容已回写卡片；原文候选含义和九项暂缓不变。本轮不产生正式relations，不把一般支持、工作室活动或目录提及升级为具体师承、出资或所有权事实。

### 写回检查与当前状态

语义决定形成临时pnp-rev093-authors/plan.json的16个before／after及preview.diff；审看差异，预检输入一致、原sources与正式relations不变后串行写回。15张卡（11更新、4新建）、16条原书摘录逐字核对、80条本地链接及来源序号有效；827个有效登记路径存在且无重复，accepted其他内容保留，既有内容检查无确定性发现。此为语义自查及机械检查，不是人工或独立验收。

任务现涉及453个KU，累计405新建、44已有有效KU更新、4旧卡整理接收；类型较前轮增加3个人物、1个地点。仍需完成其他身份及版本对齐、逐类补足、正式关系定稿。当前业务改动未提交推送；生成索引保持9310fb7基线，待同步时统一刷新。


## 舞台图与歌剧责任者

同日继续上述接续工作，原文锚点FM-P28b（图版目录印刷xiii，L81）。[Met 53.600.3581](https://www.metmuseum.org/art/collection/search/700810)的完整作品说明、作者、年代、技法、尺寸及分类已读，直接对应The Elysian Fields、Burnacini、1678和歌剧题名；新增刻制者Matthäus Küsel，与舞台设计者分开。29.7×42.1 cm是Met裁切纸张尺寸，本书具体印本未确定，不写为本书所用印本尺寸。后续必须注意场景设计、版画表达和具体印本的粒度，不能把舞台当作版画原件。

[Theatermuseum GS_GSU6464](https://collection.theatermuseum.at/en/objects/alternativtitel-die-sig-prangende-roemische-monarchey-983861)的可得网页缓存含完整对象介绍、作者／刻制者、日期、场所、材料及尺寸；直接重开后返回403，未假称观看原图或获得完整额外附件。它是同剧的Piazza Reale场景，不是《极乐世界》。仅采用其明确的1678-10-10演出、Theater auf der Cortina地点和设计／刻制责任；不把该对象GS_GSU6464、29.2×42 cm或铜版字段套到《极乐世界》。两个馆藏分别记录不同场景，不按域名数量证明历史信息独立。

[Christie’s sale2178 lot518](https://www.christies.com/en/lot/lot-5214348)的完整拍品书目与说明已读，属于1678年印本目录，不是原剧本全文。与Met的责任者相容：Nicolò Minato脚本、Antonio Draghi音乐、Johann Heinrich Schmelzer芭蕾部分。Met拼作Schmeizer，本轮以拍品的Schmelzer规范名登记，前者只记为来源异文，不扩为真实别名。AGORHA检索命中Schmelzer及该剧，实际打开超时，未把搜索片段当已读条目或采用其中生卒。芭蕾部分的作曲、编舞等更细责任仍须核，不笼统写成编舞家。拍品说明另称可能1667首演，暂不采用；本书及演出目录明确的1678场次不等于证明首演年。

Küsel在Met记1621–1682，Theatermuseum记1629–1681（拍品同后者），并列按来源保留，不以来源数投票裁决。Burnacini采用Ludovico Ottavio全名，Lodovico异体另列。其生地及其他生平未作本轮补足，不从常识补字段。

### 候选与端点

- Burnacini → 舞台设计 →《拉丁君权凯旋》及《极乐世界》；Küsel → 刻制 →《极乐世界》：Met明确，1678，原书简称与外部角色分别保留。
- Minato → 脚本；Draghi → 音乐；Schmelzer → 芭蕾部分 →《拉丁君权凯旋》：新增三个责任者端点，只承接该剧的有据职责，详细生平未完成。
- 《拉丁君权凯旋》→ 演出于 → Theater auf der Cortina → 位于 → Vienna：1678-10-10来自同剧场景目录；新建剧院place，不创造剧团或管理机构。
- 歌剧本体沿用既有work；1678年出版物仅作为本轮所读目录的对象，不把剧本印本和歌剧本体视为同一载体。具体剧本版本原件、庆典与皇室成员线索留待后续补足，没有将拍品所有背景名字递归新增。

本段8卡更新3、新增5，连同上一段共23卡更新14、新增9（7人物、2地点）。临时差异在pnp-rev093-stage/preview.diff中预检输入一致、来源保留后串行写回；合并检查覆盖23卡、19条原书原句、110条本地链接和832个有效登记。原sources、正式relations及accepted非units部分保留；正文机械检查无确定性发现。本轮仍为语义自查，不称独立或人工验收。

章前任务累计410新建、44已有有效KU更新、4旧卡整理接收，共458个KU。九项主候选暂缓及其他印本、作品版本缺口未变；整体对齐、逐类补足、正式关系审查仍未完成。当前23卡及相关记录未提交推送，生成索引保持9310fb7基线。

## 马扎然画廊与版画责任

REV-093接续，2026-09-14；REV-097已实测同步至c2164c6，本段为同步后业务更新。范围为FM-P26a／26b及其已采纳创作、委托与安置事实，不把同题版画的其他印本直接认作本书图版印本。

### 来源与实际阅读

- [Met 349118／2000.416.90](https://www.metmuseum.org/art/collection/search/349118)：完整可见对象记录及Artwork Details。1659年雕刻版画，列Nanteuil、Chauveau、van Schuppen、After Mignard四项责任；作者生卒及文化归属用于初步身份展开。47.5×67.1 cm是Met印本纸张尺寸，不作为书中印本字段。
- [Columbia 2017展览展签C00.0802.132](https://projects.mcah.columbia.edu/ma/label?field_record_id_value=2017_exhibition_C00.0802.132&height=500&iframe=true&width=500)：完整展签。Nanteuil借Mignard肖像处理面貌，Chauveau负责构图，van Schuppen刻制其中一部分，未明确具体部位。44.3×57 cm是该印本画面尺寸；第二版状态带问号，未转为确定事实。展签为学术展览研究，不把Met作者列表当作独立复证全部分工。
- [BnF La galerie Mazarine](https://www.bnf.fr/en/mazarin-gallery)：实际内容为法文，完整正文、历史沿革与图注已读。1644年Mansart受托扩建两层画廊；1646–1647年Romanelli及作坊绘上层穹顶，列Paolo Gismondi；镀金灰泥责任者按原文记Ottaviano Ottoviani。网页含2019／2021未来计划，不作为当前开放或修复状态。
- [BnF Histoire d’une renaissance](https://www.bnf.fr/fr/histoire-dune-renaissance)：读取宫殿、两层画廊、皇家图书馆1721年迁入及后段机构沿革；本轮采用全名Giovanni Francesco Romanelli、巴黎馆址和上层穹顶年代等。同一BnF的两页是同机构资料，不据来源条数提升可信度。旧页Fransceco为姓名排字差异，不增作人物别名；1994年机构改组的详细端点不在本轮展开。

### 对齐、补足及候选去向

1. 规范[Nanteuil](../../../04-knowledge/units/persons/nanteuil.md)、[Mazarin](../../../04-knowledge/units/persons/mazarin.md)、[Romanelli](../../../04-knowledge/units/persons/romanelli.md)姓名及有据身份，保留原书简称、原句和L79锚点。新增[Chauveau](../../../04-knowledge/units/persons/francois-chauveau.md)、[van Schuppen](../../../04-knowledge/units/persons/pierre-van-schuppen.md)、[Mignard](../../../04-knowledge/units/persons/pierre-mignard.md)为制作责任端点。van Schuppen生年Met1627／Columbia1629按来源并列，尚未裁定。
2. FM-P26a保留原书Nanteuil创作及Mazarin描绘对象；外部候选`FM-P26a-EXT-composition`为Chauveau→[版画](../../../04-knowledge/units/works/nanteuil-cardinal-mazarin-in-his-gallery.md)构图，`FM-P26a-EXT-engraving`为van Schuppen→版画部分刻制，`FM-P26a-EXT-model`为Mignard→版画人物肖像原型。原型肖像具体版本未定，不虚构油画KU，也不把After翻成刻版合作。Columbia关于Mazarin可能引介Nanteuil入宫的判断暂不采为正式事实。
3. [马扎然宫](../../../04-knowledge/units/places/palais-mazarin.md)和[BnF机构](../../../04-knowledge/units/institutions/bibliotheque-nationale.md)原位补入历史使用。新增[画廊空间](../../../04-knowledge/units/places/galerie-mazarin.md)与[穹顶装饰整体](../../../04-knowledge/units/works/mazarin-gallery-vault-decoration.md)，并新增[Mansart](../../../04-knowledge/units/persons/francois-mansart.md)、[Gismondi](../../../04-knowledge/units/persons/paolo-gismondi.md)、[Ottoviani](../../../04-knowledge/units/persons/ottaviano-ottoviani.md)。空间归place，壁画及灰泥装饰整体归work；宫殿、画廊和装饰分别登记。
4. 外部候选`FM-P26b-EXT-gallery`涵盖Mazarin→Mansart的1644年建筑委托、Mazarin→Romanelli的顶画委托、Romanelli／Gismondi→穹顶绘画、Ottoviani→镀金灰泥、装饰→画廊安置。各人物只获得实际所载责任；不从作坊参与推定师承，不把整个穹顶作坊分工套到每个局部。
5. [Romulus and Remus局部](../../../04-knowledge/units/works/romanelli-romulus-and-remus.md)保留原书对象和路径，仅增相关馆方入口。BnF两页没有明确列出这一场景，本轮未完成图版视觉比对；局部→装饰整体的part_of关系暂缓，不把地点和作者相同当作局部场景识别的充分依据。窗口壁画Grimaldi与穹顶有不同部位，尚未采入本轮穹顶责任表；后期修复及继承链不在本轮展开。

本组处理15卡（更新7、新增8），未新增QID或Wikipedia双向确认，未新增正式边。上述外部身份和事实补足交后续关系审查，不表示所有人物传记、原型和具体印本已全面补足。

## 本蒂沃利奥肖像与流传

REV-093接续，2026-09-14；范围为FM-P04a，按本书Van Dyck／Cardinal Bentivoglio／Pitti／Florence四个锚点核对同一馆藏肖像。

### 来源与实际阅读

- [OPD修复记录](https://opificiodellepietredure.cultura.gov.it/attivita/antoon-van-dyck-il-ritratto-del-cardinale-bentivoglio-1623-galleria-palatina-le-gallerie-degli-uffizi-firenze/)：完整作品字段、历史说明、技术、保存状态、修复处理、书目及图注已读。网页工具本轮超时后直接HTTP成功取得正文。1623年Guido委托；1653年佛罗伦萨教廷使节Annibale Bentivoglio赠Granduca Ferdinando II，先安置Uffizi Tribuna；1799年自Pitti送巴黎，1815年返回。GR13382（ex7505）为OPD档案标识，不是画作馆藏号。
- [ICCD 0900129521](https://catalogo.beniculturali.it/detail/HistoricOrArtisticProperty/0900129521)：完整公开网页目录已读，不称下载完整PDF或阅读被引档案原件。馆藏号Palatina82，编目1979、更新2006；1622–1623年，195×147 cm，布面油画。引用库存中的1652采用佛罗伦萨报喜节历，目录叙事明确作1653，不制造历法冲突。返还日期1814与OPD1815确有异文，保留两值。
- [Frick展览记录](https://www.frick.org/exhibitions/van_dyck/15)：完整作品展签及技术字段已读。作者Anthony van Dyck，1599–1641，1623年罗马肖像；Guido为外交官、赞助人和历史学家。画家寄居说为likely，未作确定居住边。Frick是借展作品记录，不是作品当前收藏者；各机构可能采用共同作品研究，不据三域名断言三条独立历史证据。

### 采纳、异文与端点

1. [Van Dyck](../../../04-knowledge/units/persons/van-dyck.md)原位展开Anthony／Antoon／Antonie用名；[Guido Bentivoglio](../../../04-knowledge/units/persons/cardinal-bentivoglio.md)原位展开全名、生卒、头衔及多重身份。[肖像](../../../04-knowledge/units/works/van-dyck-cardinal-bentivoglio.md)补充创作、委托、材料、库存号、流传及原画布已不存的事实；原书四个端点保持。
2. OPD现测195.8×146.6 cm与ICCD／Frick195×147 cm分别列明。OPD材料总字段记tempera、olio，但技术与修复正文说明后期修补含蛋彩及油性材料，因此不把原作直接改称蛋彩画。颜料层转移确定发生；具体年代、城市和修复者在OPD历史归因与后文讨论中并非完全一致，本轮不赋确定日期或责任人。
3. 新增[Annibale Bentivoglio](../../../04-knowledge/units/persons/annibale-bentivoglio.md)、[Ferdinando II de’ Medici](../../../04-knowledge/units/persons/ferdinando-ii-de-medici.md)、[Galleria Palatina](../../../04-knowledge/units/institutions/galleria-palatina.md)、[Tribuna degli Uffizi](../../../04-knowledge/units/places/tribuna-uffizi.md)，补齐赠送、受赠、保管及历史陈列场所。[Pitti](../../../04-knowledge/units/places/palazzo-pitti.md)保留建筑身份；画廊为机构，Tribuna为内部空间。Ferdinando II不与已登记Grand Prince Ferdinand合并；Annibale与Guido不因同姓推定亲缘。
4. 外部候选`FM-P04a-EXT-commission`为Guido→肖像委托及Van Dyck→肖像创作（罗马，OPD1623，ICCD1622–1623）；`FM-P04a-EXT-gift`为Annibale赠画、Ferdinando II受赠（1653）；`FM-P04a-EXT-location`分别为肖像→Tribuna（1653）、Pitti（1799年征收前）、Paris（1799年转运）及Galleria Palatina现保管。返还边带1814／1815来源异文，不无条件归并时间。
5. ICCD人物段将Guido写作Clemente VII的cameriere segreto，年代明显不相容，不采纳也不凭记忆替换为另一教宗；所引Bellori、库存档案、研究论文仍是转述与书目线索。画中信件不能据图像自动建立现存档案实体。完整人物辞典、生平亲缘、著述及其他作品版本仍待相应来源，未声称全面补足。

本组处理8卡（更新4、新增4）。与马扎然组共23卡（更新11、新增12）；原有正式关系保持，外部候选已带具体来源交接。9条主候选暂缓不变；版本、日期和场景缺口另列，不以“9条暂缓”代替全部未完成项。

## 作者与序言学者身份

REV-093同轮接续，2026-09-14。对本书作者、献辞及序言帮助者进行初步身份展开，复用已有KU，未新增对象。

- [Charles Hope, Francis James Herbert Haskell, 1928–2000, PBA 115 (2002), pp.227–242](https://www.thebritishacademy.ac.uk/documents/366/115p227.pdf)：实际读取PDF2–3、7–8、10、15–17，采用印刷pp.227–228、232–233、242的全名、出生／死亡日期、1948年入学、Pevsner指导、Bettagno介绍及1965年婚姻。未称整篇全文阅读；其他书目、父母、任职机构及晚年活动没有在本轮递归新增。传记p.232明确Larissa Salmina为Hermitage威尼斯素描策展人及Haskell配偶，结合本书作者和献辞语境，与[Larissa原卡](../../../04-knowledge/units/persons/larissa-dedicatee.md)配对；这不是将原书献辞本身解释为婚姻证据。
- [National Gallery NGA16](https://www.nationalgallery.org.uk/research/research-centre/archive/record/NGA16)：完整集合目录和Administrative history已读，确认[Ellis Kirkham Waterhouse](../../../04-knowledge/units/persons/ellis-waterhouse.md)全名、1905–1985及1929–1933任馆助理。25封信的目录不等于读过信件正文；不把档案中的每名通信者自动加入本任务。
- [National Gallery Sir Michael Levey](https://www.nationalgallery.org.uk/about-us/history/directors/sir-michael-levey)：完整人物传记段已读，采用生卒、1951年入馆至1973–1986任馆长的分条履历。下方Selected acquisitions为任期相关馆藏索引，未把馆藏收购等同个人所有或个人委托；也未全面阅读各藏品独立页面。
- [American Academy of Arts and Sciences: Howard Hibbard](https://www.amacad.org/person/howard-hibbard)：网页工具取得完整人物字段，确认1928–1984、艺术史学家及教育者；直接HTTP受403限制不影响已读页面字段。其机构与当选年本轮未展开新端点。另找到Columbia 1986系刊，但未完整阅读Hibbard纪念文，未采为已核事实或全名补足。
- [Getty ULAN 500121330: Enggass, Robert](https://www.getty.edu/vow/ULANFullDisplay?find=laurens&role=&nation=&subjectid=500121330)：完整规范记录已读，人物类型、Robert Enggass、1921–2003、美国、艺术史／教授／作者及巴洛克研究一致。搜索所得层级页的500299802经打开实为Non-Artists分类节点，排除；从层级页人物链接得到500121330后才写入。ULAN转引CAA News和LOC资料，未称已独立阅读这两份原件；不将ULAN标识当成QID。

保留本书原句、页行与帮助者角色，新增外部候选分别归源：`FM-DEDICATION-EXT-spouse`连接[Haskell](../../../04-knowledge/units/persons/francis-haskell.md)与[Salmina](../../../04-knowledge/units/persons/larissa-dedicatee.md)，1965年结婚；`FM-PREFACE-EXT-supervision`为[Pevsner](../../../04-knowledge/units/persons/nikolaus-pevsner.md)→Haskell，1951年同意指导，不追认为博士学位指导；`FM-PREFACE-EXT-introduction`保留[Bettagno](../../../04-knowledge/units/persons/alessandro-bettagno.md)1962年在威尼斯介绍两人相识；`FM-PREFACE-EXT-employment`分别为Levey／Waterhouse→伦敦National Gallery的分期职务和Salmina→Hermitage的1962年策展身份。伦敦馆已有确定KU，但不能由这些学者任职反推原书FM-H14未指明的National Gallery就是伦敦馆，H14继续暂缓。

本段9张既有卡（8人物、1学院）原位更新，连同前两组共32卡（更新20、新增12）。章前仍470个KU、全库844个；外部初步身份展开不表示这些学者的完整学术履历、著作及亲缘已全部补足，未写正式边，整体目标继续执行。

### 本轮保存与检查

32卡经可审阅差异及输入一致性预检后串行写回，核对25条原书原句、143条本地链接、全部新增来源编号及过程锚点；844个有效路径和470个任务KU计数一致。原sources前缀、正式relations及accepted非units字段保留，受影响卡内容机械检查无确定性发现，过程／结果文件链接与`git diff --check`通过。临时检查脚本首次对全库旧卡假定都有sources导致KeyError，已限定计数读取兼容缺省；32张本轮卡的来源仍逐项必检，重跑通过。本轮为直接语义工作与自查，不是独立或人工验收。

成果未再次提交推送；生成索引仍为c2164c6同步基线，下一次授权同步时刷新。继续处理其余人物、机构、文献和作品的初步身份与版本缺口，再按现有外部和原文候选进入全面补足及正式关系审查；不启动知识发现或页面。
