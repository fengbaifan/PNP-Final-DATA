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
| FM-P65a.self1 | 复用并更新；当前角色为描绘对象 | [皮耶尔·弗朗切斯科·莫拉（Pier Francesco Mola）](../../../04-knowledge/units/persons/pier-francesco-mola.md) |
| FM-P65a.self2 | 新建；当前角色为描绘对象 | [西莫内利（Simonelli）](../../../04-knowledge/units/persons/simonelli.md) |
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
## 图版画家与作品版本集中核对

REV-093接续，2026-09-14，REV-098同步后。本组更新13张、新增11张，围绕图版11a、21a、28a、32a及导言Giaquinto展开；不新增正式关系，9项主候选暂缓不变。新端点只承接本次已经采用的具体事实，不递归收集传记所有作品和亲属。

| 原文对象与问题 | 实际读取的来源 | 采用、排除与关系交接 |
|---|---|---|
| FM-P32a，L92，xiv；Ribera及《醉西勒诺斯》 | [ICCD 1500626054／Q298](https://catalogo.beniculturali.it/detail/HistoricOrArtisticProperty/1500626054)完整对象记录；[2024借展清单](https://capodimonte.cultura.gov.it/mdc/uploads/2024/10/24.10.2024_opere-in-prestito_Capodimonte_elenco-completo-1.pdf)PDF16整页及页脚；[2018 Carta Bianca](https://capodimonte.cultura.gov.it/mdc/uploads/2018/03/Cartella-stampa_Carta-Bianca.pdf)PDF19作品清单 | Ribera展开Jusepe de Ribera；作者、同题、1626、Capodimonte及Q298对应。采用油画媒介、库存号，185×229与179×228 cm并列，不猜测画框或裁切原因。作者→作品→保管机构各有现成端点；Q298不是外部QID。 |
| FM-P21a／21b，L74，xiii；Sassoferrato及玫瑰圣母委托 | [Blasio，DBI 90，2017](https://www.treccani.it/enciclopedia/salvi-giovanni-battista-detto-il-sassoferrato_(Dizionario-Biografico)/)传记和书目完整阅读；[National Gallery](https://www.nationalgallery.org.uk/artists/sassoferrato)完整人物短文及作品索引摘要；[Italia.it Santa Sabina](https://www.italia.it/it/lazio/roma/s-sabina-all-aventino)完整地点说明与地址 | 展开Giovanni Battista Salvi，保留别称；新增父Tarquinio、母Vittoria、妻Angela和出生城镇。父亲首位教师保留“可能”；1629在Domenichino家居住不直接提升为已证师生。21a采用1643年40 scudi付款及教堂／小堂空间端点。21b同题版本仍未配定，未套入Corsini其他对象的尺寸或库存。 |
| 21a委托者及空间粒度 | 同一DBI称Olimpia Pamphili principessa di Rossano，并明确Camillo Pamphili为其丈夫；对照[既有Olimpia Aldobrandini卡](../../../04-knowledge/units/persons/olimpia-aldobrandini.md)中婚后名、配偶和生卒依据 | 复用Olimpia Aldobrandini，不误配Olimpia Maidalchini，不因1643年付款倒推1643年已经与Camillo结婚。金额来自DBI转引Archivio Doria Pamphilj 86/54 f.26r，未查原件；该DBI书目包含Haskell，不能以不同域名视为完全独立于本书。Italia.it将画定位d’Elci小堂，故新增place；[Roma旅游的博物馆介绍](https://www.turismoroma.it/it/node/216)亦提同题作品，本轮未据此判定原画已经迁入博物馆。空间记录不声明2026年现场在位。 |
| FM-P11a，L54–55，xii；Bottalla、师承与委托 | [Sborgi，DBI 13，1971](https://www.treccani.it/enciclopedia/bottalla-giovanni-maria-detto-il-raffaellino-raffaellino-da-savona_(Dizionario-Biografico)/)全文和书目；[Musei Capitolini供稿的Google Arts & Culture记录](https://artsandculture.google.com/asset/meeting-between-esau-and-jacob/PgEnU9pjokCdww?hl=it)完整详情 | 全名Giovanni Maria Bottalla，1613年2月生、1644年卒；保护者Giulio Sacchetti安排Cortona指导。新建Giulio、Sacchetti家族、Savona，复用Cortona。作品采用1636–1641、油画与家族委托，集体委托不改为Giulio个人付款。聚合页w3340×h2380 cm明显异常，排除尺寸而不自行除以10；DBI与该馆记录均记Milan，未误改为Genoa。 |
| FM-P28a，L81，xiii；Cagnacci与同题版本 | [KHM GG260](https://www.khm.at/en/artworks/cleopatra-s-suicide-383)完整对象及说明，通过HTTP正文实际读取；[KHM GG6508](https://www.khm.at/en/artworks/selbstmord-der-kleopatra-384-1)检索返回完整对象字段，直开未成功 | 画家补1601–1663及晚年维也纳宫廷身份。GG260为153×169 cm群像，GG6508为124×93.5×2 cm，均记1659年后；本书题名、作者和持藏馆不足以选择其一。两个入口仅列为版本候选，未把GG260的尺寸、Leopold Wilhelm收藏或人物标识灌入28a。此前Zeri 212704仍只支持Villani摄影商号，照片档案号不能充当绘画库存。 |
| FM-E051，导言L181–184，xvii；Giaquinto抵罗马及活动年代 | [Meyer，DBI 54，2000](https://www.treccani.it/enciclopedia/corrado-giaquinto_(Dizionario-Biografico)/)实际选读出生至1743年罗马工程连续段及死亡段，未读完整后期生涯／书目 | 展开Corrado Giaquinto；1721年3月赴Naples，1723–1724返乡，1727年3月赴Rome；采用1731装饰合同、1740-01-03入圣路加学院。新增Molfetta、S. Nicola dei Lorenesi建筑及装饰工程，分别记录作者、合同年、安置地。正文保留Haskell的代际评论，不以外部年份证明其价值判断。DBI质疑正式Conca学生说，未新增师生边。 |

补证边界：National Gallery对Salvi卒地Florence只作推测，DBI给出Rome及1685-08-01；本轮采用后者，异文理由留本过程。Salvi其余子女、作品和研究文献尚未系统补足，三名具名家属的建立不表示家族完整。Bottalla在Barberini宫试图接管天顶的故事被DBI标为传闻，未写为合作／接管事实；DBI另记Barberini继承人藏《以扫与雅各》版本，未与Capitoline本合并。[ICCD 1201008737](https://catalogo.beniculturali.it/detail/HistoricOrArtisticProperty/1201008737)检索显示Via della Lungara，故不借其资料补卡皮托利欧对象。

《醉西勒诺斯》2024出借清单的展期终点为2025-03-09，而[Petit Palais展览页面](https://www.petitpalais.paris.fr/decouvrir-la-programmation/expositions/ribera)检索返回2025-02-23；两者都不是实际运输／返还记录。本轮只用该清单的Q298和尺寸，不采为已执行的借展历史。搜索另命中1628年同题版画，未混入1626油画。《圣母子》21b搜索命中[ICCD 1201007462](https://catalogo.beniculturali.it/detail/HistoricOrArtisticProperty/1201007462)的1550–1599断代，与归属作者年代矛盾，及Zeri跟随者版本；仅作待查线索，不当作确证。本组未新增QID或声称Wiki双向验证。

交接：可继续上述5名画家及有据作品的明确缺口补足；保留21b、28a版本阻断，其他创作、委托、亲缘、师承、安置与馆藏事实作为带来源候选交正式关系阶段。当前对齐、全面补足及关系定稿均未全部完成。

本组写回前核对输入未变化、原sources前缀及既有relations保留；写回后复核24卡、22条原书摘录、119条本地链接、来源编号及过程锚点。855个有效登记与482个章前KU及类型分布一致，受影响内容机械检查未报缺陷，git diff --check通过。这是语义自查与机械核对，不是全面补足、正式关系定稿或人工验收；生成索引未刷新，本轮未提交推送。


## 序言学者与图版角色集中对齐

REV-099同步至`59bc2c6`后继续REV-093目标。按既有卡、原书证据及专业来源集中处理32张KU（更新20、新增12），不把初步身份核对与全文补足混为一体。采用verify、enrich及必要的ingest端点回送；未启动知识发现或网页。

### 来源、阅读范围与身份判断

| 对象组 | 实际来源与阅读范围 | 判断及限度 |
|---|---|---|
| Montaiglon、通信集、Guiffrey | [INHA Agorha](https://agorha.inha.fr/ark:/54721/b7e772e8-be9a-4fb1-a0ba-a21b2283912a)，完整人物、传记说明及书目 | 原书简称对应Anatole Courde de Montaiglon；同一18卷、1887–1912年通信集并列Montaiglon与Jules Guiffrey。Guiffrey以共同编者为本轮身份范围，未展开其全部生平。BnF外链未另核；未读通信原件，不把编者当全部来信作者。 |
| Rylands | [King’s现代档案指南](https://www.kings.cam.ac.uk/guide-modern-archives)，指南说明与GHWR完整条 | G. H. W.＝George Humphrey Wolferstan，昵称Dadie，1902–1999。KC1921按该页定义为admission，不称1921年成为Fellow。原书校阅工作只由序言证明。 |
| Harris | [匹兹堡大学教师页面](https://www.haa.pitt.edu/people/ann-sutherland-harris)，完整研究、教育与出版清单；未下载CV | 安·萨瑟兰·哈里斯的专业身份、Courtauld教育与1977年萨基专著可用。原书OCR的Aim不另造人物；教材初版同页2004／2005有分歧，本轮不写该出版项。未把页面Current Projects称为2026仍在执行，未读专著全文。 |
| Boucher | [UVA任命新闻](https://www.newswise.com/articles/architectural-historian-and-museum-curator-bruce-ambler-boucher-appointed-director-of-the-university-of-virginia-art-museum)，完整正文；[Soane 2016–2017年报](https://www.soane.org/sites/default/files/2023-06/soane-museum-annual-report-accounts-2017.pdf)，PDF第6、8、11、43页（印刷4、6、9、41） | 全名Bruce Ambler Boucher，2002起任芝加哥欧洲雕塑策展人，2016-05-16就任Soane馆长。Newswise正文无明确发布日期，将于3月1日赴Virginia的预告未当已发生的具体日期；年报2017-03-31不是离任日期。 |
| Chiarini | [Padovani与Chappell纪念文章](https://www.burlington.org.uk/archive/obituary/marco-chiarini-19332015)，完整正文 | Marco Chiarini，1933-09-01至2015-11-06；1964迁佛罗伦萨，1969–2000任Galleria Palatina馆长。只采与身份及任职链有关内容，作品、展览与家族清单并未全面补足。 |
| Conforti及1977年论文 | [Burlington 1977年8月目录](https://www.burlington.org.uk/archive/back-issues/197708)，原刊目录；[Clark个人档案](https://archives.clarkart.edu/repositories/2/resources/159)，完整Biographical / Historical段及馆藏摘要；[2016年报](https://www.clarkart.edu/getmedia/8419623c-ddf2-4876-8815-2b45d376ca90/2016.pdf)，PDF第3页馆长前言 | 原书论文与期刊同题、同作者，卷119期893。结合馆方晚期巴洛克意大利雕塑研究履历识别人物。档案页1952出生与1968毕业可疑，任命1994与任期1995起亦不一致，均未写成确定值；退休2015-08-31依年报。论文页557–560仍依原书，未读付费正文或个人档案原件。 |
| Pignatti | [Istituto Veneto会员页](https://www.istitutoveneto.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/1353)，检索返回完整短传和日期；直开403 | Terisio Pignatti，1920-09-19至2004-12-31；1945入Musei civici veneziani，1974离职时为馆长，不能称29年均任馆长。历史市立博物馆系统与单一Museo Correr／图书馆及2008年成立的MUVE基金会不直接等同。本轮未核后者身份，也未读纪念文章全文。 |
| Cozzi | [Ca’ Foscari档案指南](https://edizionicafoscari.unive.it/media/pdf/books/978-88-6969-706-7/978-88-6969-706-7-ch-04.pdf)，PDF第54页、印刷382页完整Fondo Gaetano Cozzi条 | Gaetano Cozzi，1922-09-15至2001-03-15；Ca’ Foscari任教1960–1965、1970–1998，Padua任教1966–1969。采用校方明确分期，不沿旧FBSR英文页面搜索片段重建履历；指南所述藏书不等于原件已读。 |
| Venturi | [Viarengo专题传记](https://www.treccani.it/enciclopedia/franco-venturi_(altro)/)，导言与完整La vita段 | Franco Venturi，1914-05-16至1994-12-14，启蒙和俄国研究；1955–1958年Genova之后转Torino，教席至1984。来源是2013年专题文集，不能标DBI；后续专题段与全部著作未完成本轮阅读。 |
| Torcellan、Memmo及研究书 | [Oechslin书目011679565](https://www.bibliothek-oechslin.ch/einfachesuche.php?Oui=Oui&Showtime=011679565)，完整书目、规范、物理馆藏字段 | Torcellan（1938–1966）与Andrea Memmo（1729–1793）按作者／主题规范区分。1963年书与馆藏散页复印件分开，未读书正文；GND仅该机构规范引用，不称另行GND回查。Unito学生清单直开未成功，未将搜索片段出生日期加入卡。 |
| Baur与图版06 | [Galleria Borghese库存519](https://www.collezionegalleriaborghese.it/opere/prospetto-di-villa-borghese)，完整技术字段和正文；[ICCD 1201008256](https://catalogo.beniculturali.it/detail/HistoricOrArtisticProperty/1201008256)，完整记录 | Guglielmo Baur＝Johann Wilhelm Baur。按作者、地点题材、同馆保管及签名配对519，1636、羊皮纸蛋彩30×45 cm；这是馆藏记录对齐，非图版图像独立比对。原书题名1630原样保留且不继续断言真实描绘年份；1641另一构图／别藏本不混入。委托者属推测、无日期巴黎借展状态均未采纳；两目录不计两项独立原始证明。 |
| Simonelli、Mola与65a | [原书补记](../../../02-sources/02-Markdown/20_CHP-20Postscript.md)，p.401 L90–91，定向完整两行及相邻小节边界；[BM1857,0613.365](https://www.britishmuseum.org/collection/object/P_1857-0613-365)，检索返回完整对象与策展注释，直开403 | 原书明确Niccolo Simonelli与朋友Pierfrancesco Mola共同创作65a；图版目录只明确两人被描绘，不证明各自画自己。BM只用于人物身份、职业标签及活动期，不把另一幅画的库存、尺寸、材质、收藏史写入65a；fl.1636–1671不是生卒年。补记关于第五章的小节仅为本图版消歧，不是开展第五／六章。 |

### 语义修正与关系交接

- 图版65a在最初实体候选中已正确记为“共同作者也为描绘对象”，登记写回却变成“自我描绘者”。本轮在Simonelli、Mola和作品卡中改为“描绘对象”，两人物sources的错误句意摘要同步修正；原书原句、行号、章节与来源顺序保留。稳定候选ID `FM-P65a.self1/self2`保留以便追溯，映射行明确当前角色，不将旧ID字面当判定依据。
- 朋友关系依据新增的原书补记L90–91，不能回填为早先图版目录本身明说的事实。合作仅限该双人漫画；各自绘制范围仍未定。BM提供外部赞助人身份标签，不据此虚构具体付款或委托交易。
- 编纂、研究对象、博士教育、馆长／策展人任职、校阅、研究便利及馆藏关系均有字段与端点链接。原书的致谢／校阅候选仍用原书证据；后来的大学与博物馆履历只支持各自任职事实，不证明所有人在序言写作时已担任这些职务。
- 更新20卡并新增12卡：共同编者Guiffrey、研究对象Memmo；Harris萨基专著、Torcellan梅莫研究；Pittsburgh、Courtauld、Soane、Clark、历史威尼斯市立博物馆系统、Ca’ Foscari、Padua、Turin八个机构。博尔盖塞美术馆复用原有有效卡，新增章前库存519关联，不重复建馆。
- 来源元数据记录实际阅读范围，书目不作全文证明。人物亲缘、全部作品／著述、其他任职与细节继续按明确缺口补足；不因这一轮有全名与外部入口就宣布整卡完成。

### 本轮结果

本轮32卡更新20、新建12；全库867个有效KU，章前495个（累计445个新建、46个既有有效KU更新、4个旧卡整理后接收）。9项原始主候选继续暂缓，其他具体版本缺口仍按前段保留。正式关系未新增，相关有据候选交后续关系审查；未再次提交推送。

本轮32张卡的31条原书摘录、141条本地链接、来源编号及过程锚点核对通过；867条有效登记与495个章前KU计数一致。除两条明确纠正的65a句意摘要外，原sources前缀保持；原有正式relations保持。受影响内容机械检查无确定性发现，文档差异检查通过；这是语义自查与机械核对，不代表全面补足或正式关系定稿。

## 馆藏机构与图版版本集中核对

REV-100已实测同步至`485fca9`。本段继续REV-093目标，集中处理馆藏记录及其必需端点；阶段仍为初步对齐，已得到的内容字段同时补入。未重启知识发现、网页或人工校验。

### 实际阅读与来源范围

- Nationalmuseum对象[82794／NMH 554/1863](https://collection.nationalmuseum.se/en/collection/item/82794/)：完整对象字段、Description、题铭及图像版权文字；未做原图视觉比对。馆方[About Nationalmuseum](https://www.nationalmuseum.se/en/about-nationalmuseum)完整简介正文通过公开HTTP读取。仅据该页记录1792年成立、艺术与设计博物馆及政府机构身份，不将创立年当作现馆址落成年。
- NGS[NG 2193](https://www.nationalgalleries.org/art-and-artists/5382)：完整对象字段、About及More about正文；后者原刊2015年馆藏选集。另读[National单馆入口](https://www.nationalgalleries.org/visit/scottish-national-gallery)馆名、简介和Getting here地址段。单馆与National Galleries of Scotland总机构不同；本次保留原书单馆端点，不另将总机构合并为同一KU，不把In Storage字段推广为持续至今的陈列状态。
- ICCD[1200962613](https://catalogo.beniculturali.it/detail/HistoricOrArtisticProperty/1200962613)：完整对象页面及同源[ICCD4644610 PDF](https://sigecweb.beniculturali.it/sigec/item/print/ICCD4644610)全部3页。PDF1为库存号、罗马馆址及第四室；PDF2为年代、技术、数值、委托和推测合作；PDF3为照片、参考书目及2005编目／2006更新。未阅读所引Cannatà、Vicini原著，不把目录书目命中当作全文阅读。
- [Galleria Spada作品说明](https://galleriaspada.cultura.gov.it/capolavori/esplora-le-sale/sala-iv/cerquozzi-la-rivolta-di-masaniello/)：网页工具超时后公开HTTP读取题头及完整两段作品说明。ICCD及馆方是同一馆藏的不同描述，不能以域名不同自动计为独立事实证据。
- [Boijmans I 135 (PK)／对象58489](https://www.boijmans.nl/en/collection/artworks/58489/caricature-portarit-of-cassiano-dal-pozzo)：公开HTTP读取题头、全部Specifications、collector及作者字段。Fondazione1563的[2024年Cassiano文章](https://programmabarocco.fondazione1563.it/cassianodalpozzo/)中图注及末节提供馆藏链接线索；没有把该文所有知识、Museo cartaceo出版计划或引用人物扩张成已采纳内容。此次采用的技术、藏品号及借展链均直接来自馆藏页。
- 复用此前已读Cambridge Museums、Paris Musées J 104、NGV 103-4来源，补到3个保管机构卡。Cambridge本轮另定向读两幅肖像当前标签；Paris本轮核对馆名、作者、年代及编号字段；NGV使用此前已读对象字段，不新增“本轮全文阅读”声明。复用来源不计新独立证据，不把两幅提埃坡罗宴会合并。卡内原有来源与对应作品卡一致。
- 卡塞尔32136公开记录HTTP超时，当前未得到可用正文，未采纳搜索所见QID、库存或作品日期；不据此阻断其他馆藏对象。

### 身份、版本及字段裁决

1. 图版65b为马苏奇纸本黑粉笔素描，42.2×32.9厘米，NMH 554/1863；马苏奇1691–1758，题材是莫拉给教宗作像，不是马苏奇本人受教宗委托画肖像。馆方题铭记莫拉1609／1665，与既有生平1612／1666不同；本轮不以画上铭文改写人物出生死亡日期。汉堡FP566仅为目录比较线索，未读该对象记录，不并入本图版。
2. 图版35b对应鲁本斯NG 2193，约1635–1638，1958年购入。馆方“probably commissioned”原样保留为可能委托，Gaspar Roomer新卡只承接有据商人／收藏家身份及该限定，不制造已确证交易。至1640年已到那不勒斯不等于1640年绘制。作品三维与带框三维分别保存，不猜第三项的测量定义。宗教叙事情节没有自动转成历史人物亲缘事实；原有Herod题材仍需单独身份与描绘关系处理。
3. 图版22b对应馆藏81，国家目录1200962613。ICCD记1648，馆方详述1647年底至1648年初，分别记录不判作不同作品。ICCD PDF2记高96.8、宽134但未显式显示单位，馆方网页却记184×186 cm；本轮未填尺寸值，保留该字段待证，不凭常识选择或转换。ICCD对Codazzi建筑分工使用推测语气，馆方采用肯定表述；卡内并列限定，后续不能写成无条件共同创作边。宫殿为地点、馆为机构，Virgilio为委托人与历史收藏者。馆方所述与Bernardino的兄弟关系及Masaniello身份尚未展开端点，列后续待核，不宣称人物亲缘与描绘对象已补足。
4. 图版17a对应I 135 (PK)，纸本笔绘棕墨，104×117 mm。馆方年代字段约1680单列；这不是作于模特生前的证明，不能由题材推导现场作画。保留Bernini的既有全名，馆方作者异体Giovanni Lorenzo不建立第二个人物。1940是借入记录；Franz Koenigs为旧藏者、Stichting Museum Boijmans Van Beuningen为出借方、Museum Boijmans Van Beuningen为保管方，三者不合并，也不把该年写成作品制作年或捐赠年。
5. 鲁本斯显示名展开为Peter Paul Rubens，双语描述去掉旧的“完整姓名未验证”陈述，保留第一章新教堂及modello语境。其原卡教育、亲缘、代表作等旧表仍有未参考或未链接内容，需要后续针对来源清理；本轮不以改名和一件作品资料宣称其整卡补足完成。Codazzi已有合作反向展示错误把发出端S7写成“本卡S7”，此次只改成“发出端第7条来源”，不更改该正式关系断言。

### 关系候选交接

以下为外部证据支持的内容关联，原书候选仍保留原证据跨度，未新增正式边；同行角色各自沿对应作品卡sources核对。

| 候选锚点 | 起点 → 终点 | 类型／限定 | 证据及待核 |
|---|---|---|---|
| MUS-01 | Masucci → 莫拉为教宗作像素描 | 创作 | NMH 554/1863；无精确制作年 |
| MUS-02 | 莫拉作像素描 → Mola／Alexander VII | 描绘，分别确认两端 | NMH 554/1863；不推导委托 |
| MUS-03 | Nationalmuseum → 莫拉作像素描 | 保管 | NMH 554/1863；非成立年起藏 |
| MUS-04 | Rubens → 希律王宴会 | 创作，约1635–1638 | NG 2193 |
| MUS-05 | Gaspar Roomer → 希律王宴会 | 可能委托 | NG 2193；不可升为确定边 |
| MUS-06 | 苏格兰国家美术馆 → 希律王宴会 | 1958购入／收藏 | NG 2193；单馆与总机构粒度保留 |
| MUS-07 | Virgilio Spada → 马萨涅洛起义 | 委托、历史收藏，分别记录 | ICCD与馆方；年粒度分别保存 |
| MUS-08 | Codazzi → 马萨涅洛起义 | 建筑背景绘制，归属表述不同 | 不以一般合作关系证明本件分工确定 |
| MUS-09 | 马萨涅洛起义 → Palazzo Spada／Galleria Spada | 安置建筑／保管机构，分别记录 | ICCD；第四室为2006年目录记录 |
| MUS-10 | Bernini → Cassiano漫画 | 创作 | I 135 (PK)；馆方约1680待更精细比较 |
| MUS-11 | Franz Koenigs → Cassiano漫画 | 旧藏 | I 135 (PK)；入藏退出具体年未载 |
| MUS-12 | Stichting → 博伊曼斯博物馆／Cassiano漫画 | 1940借出／借入，需保留作品范围 | I 135 (PK)，不是捐赠或机构同一关系 |
| MUS-13 | Fitzwilliam／Cognacq-Jay／NGV → 各自图版作品 | 保管，各对象独立 | PD.13-1972／J 104／103-4；复用已核来源 |

### 本轮结果

更新14卡、新建6卡，共20卡。新建3个人物（Roomer、Virgilio Spada、Franz Koenigs）、2个地点（Edinburgh、Palazzo Spada）、1个出借基金会。Codazzi为已有第一章有效人物，首次加入章前任务范围。全库873个有效KU，章前502个（累计451个新建、47个既有有效KU更新、4个旧卡整理后接收）。9项主候选仍暂缓；其他版本、日期、尺寸和端点缺口继续保留。当前未新增正式关系，未再次提交推送，生成索引保持`485fca9`同步基线。

本轮20张卡的15条原书摘录、86条本地链接、来源编号及过程锚点核对通过；873条有效登记与502个章前KU计数一致，原sources前缀和正式relations保持。受影响内容机械检查无确定性发现；文档差异检查通过。这是语义自查与机械核对，不表示全面补足或正式关系定稿完成。

## 雷古鲁斯油画与准备稿版本

同轮继续处理6卡：VMFA油画、馆、Rosa；新增普林斯顿准备稿、保管馆及Dan Fellows Platt三个必要端点。与上一段合计26卡，章前505个，全库876个有效KU。

### 阅读、裁决及交接

- 完整阅读[Princeton x1948-610](https://artmuseum.princeton.edu/art/collections/objects/8060)对象说明、Information、Provenance、书目条目、展览记录及Citation。明确本件是VMFA《雷古鲁斯之死》油画的准备稿，约1652年；纸张、技法及20.3×25.7厘米仅属于准备稿。所引1965学位论文、1666书信、展览文献未读原文，不把目录引述当作阅读全文。
- VMFA旧PDF路径在网页工具一度返回可检索PDF，但后续打开重定向失效；公开HTTP的about路径返回空体，不能据此宣称已读文件。采用的2009会议记录仅限搜索索引实际返回的“Additional Information on Previously Approved Loans”第1项，明确作者、题名、1650–1652、oil on canvas及59.15；批准和出借建议均不作为实际出借证明，故未建立2010巡展事件或正式外借关系。
- 另实际读[Commons转存文件](https://commons.wikimedia.org/w/index.php?title=File:Rosa_-_The_Death_of_Regulus,_ca._1650-1652.jpg&oldid=1018278172)的来源与完整Metadata字段。其Author为Virginia Museum of Fine Arts，Image title记59.15、约1650–1652、布面油画及无框／带框尺寸，生成和修改日期为2008年；与馆方2009索引片段的对象信息相符。尺寸据此注明为馆方图像元数据转存，不称当前馆藏页直接核验。只读取文字元数据，未下载或重分发图片，也未做原图视觉比对；旧piction源链接未独立读取。该转存与VMFA会议记录同属馆方来源，不算两个独立权威体系。
- 另有VMFA 2014.273蚀刻及Met 80.3.341“after Rosa”素描线索，均不是59.15油画，未导入其尺寸、年代或作者归属，也未声称这些对象的完整目录已读。Princeton对Regulus受刑的故事为图像主题说明；同名历史人物具体身份仍需单独核，不直接转为确证历史死亡事实。Williams Fund原署名仍保留，尚未完成其基金身份对齐。
- 新候选：Rosa→准备稿（创作）；准备稿→VMFA油画（准备关系）；Platt→准备稿／Princeton（遗赠）；各馆→其对应版本（保管）。遗赠日期未明，不从x1948-610号码推断；Class of 1895未转成未经另核的学历事实。上述候选与油画原书图版23b关系分开，未新增正式边。Rosa既有第一章source、正式relation及叙述保留。

### 当前结果

此段6卡更新3、新建3；本轮合计26卡更新17、新建9。章前505个KU（累计454新建、47既有有效KU更新、4旧卡整理后接收），全库876个。9项主候选以及其他版本／内容缺口仍待证；未再次提交推送，全面补足与正式关系定稿尚未完成。

本段6卡的10条原书摘录、29条本地链接、来源编号及过程锚点复核通过；876条有效登记、505个章前KU及类型计数一致，原sources与正式relations保持。两段合计26卡、25条原书摘录、115条本地链接完成受影响范围检查，未报确定性内容缺陷，文档差异检查通过；不表示全面补足或正式关系定稿。

## 出版研究机构与图书馆角色

REV-101已实测同步至`2d7db45`。继续REV-093目标，集中处理22卡（19既有、3新增），以既有原书角色为起点，核对机构层级、书目身份和明确内容缺口。新端点为伦敦大学、意大利百科全书研究院和罗马兰特别墅；未开始知识发现、页面或人工校验，未新增正式关系。

### 阅读与对象裁决

| 对象／来源 | 实际读取与采纳 | 边界、剩余缺口 |
|---|---|---|
| [Warburg官方历史](https://warburg.sas.ac.uk/about-us/history-warburg-institute) | 完整历史正文，包括图书馆发展、迁伦敦、归入大学与馆舍；采用1921、1933、1944、1958事件 | 研究所、图书馆、伦敦大学分开。1926馆舍开放不作为1921研究所建立年；未读契约原件。Aby Warburg、Saxl等人物仅为本次背景阅读，尚未补入创办／任职字段，若继续展开该字段须先落实人物端点 |
| [Yale历史](https://www.yale.edu/about-yale/traditions-history)及[出版社历史](https://yalebooks.yale.edu/a-brief-history-of-yale-university-press/) | 大学导言、1701条；出版社首段及1961段。大学1701年特许、1718旧名，出版社1908创立、1910迁纽黑文、1961所属与伦敦分支 | 不按时间线抽取后的顺序给无年份段补日期。出版社历史改编自Basbanes著作，不另计独立来源；未读整部书。版权人与出版者区分，财务／运营自主不抹掉所属关系；未把出版社同名创立视为1908即已属大学 |
| [Library of Congress官方介绍](https://www.loc.gov/about/general-information) | 完整General Information及Collections、年度统计段；只采1800起源与藏品类型。原书版权页提供CIP角色与80-5213 | 不采用2023规模为2026现况。CIP署名不证明某个具体印本现藏该馆，也不证明版权归该馆 |
| [Museo Correr图书馆介绍](https://correr.visitmuve.it/en/library/) | The Library和Services正文；采用1830遗赠创立、图书馆归属和研究服务 | 博物馆与图书馆各有KU，不把同一创立渊源写成相同实体。Teodoro Correr新增遗赠者与威尼斯贵族身份；图版59b肖像具体尺寸、版本仍需后续核对。藏书目录、画像原件未读；不把1830直接当个人卒日或每件藏品取得年 |
| [Poerson学院传记](https://villamedici.it/directeur/charles-francois-poerson/)及[RCT 421279](https://www.rct.uk/collection/421279/charles-francois-poerson-1653-1725-0) | 学院完整短传和1704–1725题头，RCT仅返回题名；任命1704与原书1708在任可配对 | 学院首句卒日1725-09-02、任职段却写1724，分字段保留；RCT题名支持1725年，不能单独证实9月2日。暂不写确定任职终日，也不把现代Villa Medici站名当1708院址。传记父亲Charles Poerson、教师Noël Coypel及墓作者Pierre de L’Estache为后续人物／师承／作品端点缺口，不据姓名猜建；墓作品亦待单独识别 |
| [Roma Capitale：芬兰研究所](https://www.turismoroma.it/it/luoghi/istituto-finlandese-di-roma) | 完整介绍、地址；采用1954活动、研究培训／驻留及Villa Lante地点 | 区分研究机构与罗马Gianicolo建筑，排除Bagnaia同名别墅。建筑当前使用事实不证明图版01作品的现藏、产权或原始安置；作品保管仍引原书。芬兰国家所有建筑的背景记载尚未展开产权端点 |
| [Reading：Chatto档案CW](https://www.reading.ac.uk/adlib/Details/archiveSpecial/110292665) | 前次接续已读完整目录Title、Creator History、Scope，后续重访超时／500；采用出版企业身份及1873商号名 | Creator History参考出版集团历史，不算另一个独立历史来源。档案覆盖1860s–1990s不是企业成立／结束。未读信件、合同或公司档案原件；本书初版支持来自原书，未将John Nicoll自动写为该公司职员 |
| [NLS：T and A Constable信簿MS.23268](https://manuscripts.nls.uk/repositories/2/archival_objects/56601) | 检索索引返回完整目录字段及Cite Item，直接访问403；据上级全宗名核对爱丁堡印刷企业 | 只核企业与地点；未读1898信簿原件，档号及1898年不是本书印刷信息。原书第一版序言中的印刷角色不迁移到本件2006年中国印刷记录 |
| [Apollo介绍](https://apollo-magazine.com/apollo/)与[Burlington历史](https://www.burlington.org.uk/about-us/about-the-magazine-150004/history) | 两页介绍正文完整读；分别采用1925、1903创刊及月刊身份，链接本书所引文章 | 期刊、网站、刊期和文章不合并。既有书评／论文具体内容仍限已读范围，不因期刊身份核对即标全文已读 |
| [Treccani第100卷说明](https://www.treccani.it/enciclopedia/i-cento-volumi-del-dizionario-biografico_%28Dizionario-Biografico%29/)与[机构历史](https://www.treccani.it/istituto/la-nostra-storia.html) | 第100卷出版说明及历史／编排讨论，机构开篇1925年成立与出版计划段；采用1960首卷、2020第100卷完成预定序列、机构身份 | 1925编纂计划、1960开始出版、2020字母序列完成分开；不声称网络更新停止，不称100卷全部阅读。同机构两页不计两个独立来源。新增机构端点不递归导入创办者及整部百科 |
| [ISSN 0069-3235](https://portal.issn.org/resource/ISSN/0069-3235)及[JSTOR期刊记录](https://www.jstor.org/journal/artinstchicmuses) | ISSN全部公开标识／名称／媒介字段、JSTOR完整可见介绍和出版者／收录字段 | Museum Studies明确为芝加哥艺术博物馆期刊，排除同名其他刊物；ISSN属印刷版。1966–2011是JSTOR收录范围，未仅凭该范围写停刊裁决。馆方第1卷PDF网页与HTTP均未成功读取，未采其正文，Waterhouse论文仍待全文补足 |

所有本次来源访问／复用日期为2026-09-14，来源的URL、实际范围及句意摘要在各卡sources保存。原有sources与正式relations保持；本次未采用QID，不填Wiki双向验证状态。上述研究针对身份和具体缺口，不代表全库或整卡全面补足。

### 内容与关系交接

原书候选继续在既有处理结果维护；下表只记本次端点映射、外部候选及需要确认的角色，未改写原书证据。

| 锚点 | 起点 → 终点 | 角色、时间、证据范围 | 交接 |
|---|---|---|---|
| INST-01 | Warburg Institute → University of London | 1944起所属；官方历史 | 新增大学端点，候选可进入正式关系核对 |
| INST-02 | Warburg Library → Warburg Institute | 所属图书馆；原书与官方机构历史 | 保留两层对象，不设same-as |
| INST-03 | Warburg Library → Haskell／本书 | 研究支持；第一版序言p.ix L21–22 | 支持者为图书馆／机构人员集体，不能虚构具体顾问姓名 |
| INST-04 | Yale University Press → Yale University | 1961起所属；出版社历史 | 财务运营自主限定保留 |
| INST-05 | Yale University Press／Yale University／Library of Congress → 本书 | 1980版出版／1980版权标注／CIP提供者 | 三种角色分别引用版权页原句，不合并成笼统参与 |
| INST-06 | T and A Constable → 本书初版 | 印刷、排版及核对；第一版序言p.ix L22 | 不能套到2006年印刷地点 |
| INST-07 | Chatto负责人／Norah Smallwood → Haskell／本书初版 | 初版制作支持；第二版序言p.vi L11–12 | 公司、负责人、被特别致谢者保留粒度；不推定具体合同角色 |
| INST-08 | John Nicoll → 本书新版本 | 提议新版并协助；同前序言 | 不由相邻句认定其雇主为Chatto |
| INST-09 | Teodoro Correr → Museo Correr／Correr Library | 遗赠促成1830机构创立；官方历史 | 两个受益机构端点，未定遗赠法律生效日 |
| INST-10 | Correr Library → Museo Correr | 所属；官方介绍 | 与博物馆所藏各作品的保管边分开 |
| INST-11 | Pignatti → Haskell；研究场所Correr Library | 提供研究便利；第一版序言p.ix L23 | 不是图书馆收藏物所有者关系 |
| INST-12 | Poerson → French Academy in Rome | 1704获任、1708在任；学院传记＋原书 | 任职终期随卒年冲突待证，不将头衔视作姓名的一部分 |
| INST-13 | Finnish Institute → Villa Lante, Rome | 机构使用建筑；罗马市介绍 | 与原书图版01艺术作品保管边分开；使用起年不直接套1954活动年 |
| INST-14 | Honour书评 → Apollo；Conforti论文 → Burlington | 文章刊载；既有原书及已核书目 | 期刊身份已补，全文阅读不因此升级 |
| INST-15 | Dizionario biografico → Istituto della Enciclopedia Italiana | 出版机构；机构和第100卷说明 | 辞典、机构及词条各自不同粒度 |
| INST-16 | Haskell → Dizionario biografico | 推荐使用、未逐条列引；第二版序言p.v L5–6 | 保留否定限定，不建立笼统逐条引用关系 |
| INST-17 | Museum Studies → Art Institute of Chicago | 出版机构；JSTOR期刊记录 | 已补期刊与机构互链，非全部文章逐篇验证 |

### 暂缓与当前结果

本轮纳入22张卡，其中更新19、新建2个机构及1个建筑地点。章前508个KU（累计457新建、47既有有效KU更新、4旧卡整理后接收），全库879个。9项主候选保持待证；本轮另遇Cambridge Library官网历史页连续不可读、Ministry of Works档案页验证墙、Royal Academy仅有展览目录线索，未以访问失败或身份相关性宣称这些对象完成；保留后续适用目录查证路径，不无依据重复抓取。

下一步优先完成其余图书馆、供片机构及书目版本身份，再围绕已登记作品／正文事实集中补足。上述17组候选交关系阶段逐项确认，完整性还受其他未完成对象及端点影响。本轮未提交推送，生成索引保留`2d7db45`同步基线。

本轮22卡的28条原书摘录、99条本地链接、来源编号及过程锚点复核通过；879条有效登记与508个章前KU类型计数一致，原sources前缀和正式relations保持。受影响内容机械检查无确定性发现；此为语义自查及机械核对，不表示全面补足或正式关系定稿。

## 供片机构与复制图像角色

REV-102已实测同步至`664bb5d`。接续REV-093目标，上一轮产生了22卡实质更新并已同步；本轮集中对齐5个机构，补入13件作品的供片字段，新增必要的ICCD端点，共19卡。继续使用原书来源与外部记录分列的方式，未新增正式关系。

### 阅读、配对与采用范围

| 来源／对象 | 实际阅读与采用 | 身份及证据边界 |
|---|---|---|
| [ICCD：国家摄影室](https://iccd.beniculturali.it/it/fotografia/gabinettofotograficonazionale) | 完整正文及档案构成段。采用1895设立、文化遗产摄影职责、1975并入ICCD，建立ICCD端点并互链 | 1975是并入年，不是摄影室停办年，也未据此写ICCD创立日期。未把1893前身实验室直接当同一机构成立；集合规模及其他摄影师、藏家仅作背景，不逐名扩张 |
| [Uffizi：1966年洪水摄影档案](https://www.uffizi.it/opere/fondo-fotografico-alluvione-a-firenze) | Chiara Ulivi完整介绍、图片题注及书目；采用Soprintendenza alle Gallerie历史机构名、部属监管职责、佛罗伦萨及1966年抢救活动 | 监管机构、摄影部门、当前美术馆不同粒度，不作same-as合并。Procacci、Baldini的个人任职和洪水档案单件尚未展开；本文参考书未读。不以照片保管证明绘画产权 |
| [BnF FRBNF45029807](https://catalogue.bnf.fr/ark:/12148/cb45029807c) | 完整可见目录及保管项；照片署Service de documentation photographique des Musées Nationaux，支持该摄影服务名称与业务 | 照片组另外两张署Giraudon，不合并机构；1950–1969属照片集合日期。BnF记录的是Pompadour题材，不能代替本书Bernini图版27b的供片证据；该边仍来自原书。现行RMN体系归属未核，不强设法人连续性 |
| [Jesus College：Stearn规范记录](https://collegecollections.jesus.cam.ac.uk/index.php/stearn-sons-photographers-bridge-street-cambridge) | 完整机构规范记录、沿革与Sources。采用摄影商号、约1866业务创办、剑桥72 Bridge Street；保留原书Stearn and Son与档案Stearn & Sons不同写法 | Sources转引Magdalene，不能当两项独立历史来源。1943年另设有限责任公司，不能把1866直接作为其法人注册年。邻接浏览记录的标识不复制到本条；没有把家庭每位成员建为本书具体摄影师 |
| [RCT：Royal Academy成立史](https://www.rct.uk/collection/stories/george-iii-joseph-farington-and-the-royal-academy)及[NT 3119476](https://www.nationaltrustcollections.org.uk/object/3119476) | RCT完整主文；NT完整可见书目对象字段。采用Royal Academy of Arts、伦敦及1768-12-10成立文件签署日期，与原书简名及时代语境初步配对 | NT仅是1960年展览目录书目，不表示已读目录全文，也不证明本书供片出自该展览。王室收藏、Royal Academy及其任何展览不是同一对象；未采用未展开的创办者、成员及馆址端点 |

### 原书扫描与断行裁决

实际查看`02-sources/01-book/CHP-0Cover.pdf`的PDF第13页／印刷xvi（Photographic Sources），与`02-sources/02-Markdown/00_05_List_of_Plates.md` L165–172对读。扫描为Gabinetto Fotografico **Nazionale**及图版**10b**，OCR作Naziotiale、rob；扫描为**Stearn**，OCR作Steam。保留来源本体及原有OCR摘录，不在sources中伪造已经校正的OCR原句。当前规范名称、图版对应据扫描和外部机构记录判断。

Royal与Academy跨L168–169，原有S1只引L169不完整，本轮追加完整跨行摘录并将名称引用改指新来源。Stearn的图版55未分a／b，且Cacco另外明确署55b；仍保留55，不将其擅配55a、55b或两者。Marlborough扫描拼写也已确认，但商号外部身份与供片版本尚待核，本轮不改该卡。

### 关系候选交接

以下续接原始候选登记映射，具体艺术对象端点以本轮卡内供片表及作品卡为准。尚待关系阶段审查，不从正文链接自动转正。

| 锚点 | 端点与候选事实 | 对应证据与限定 | 当前去向 |
|---|---|---|---|
| PHOTO-01 | 国家摄影室 → 图版10b、12、15所示的三件作品：提供本书复制照片 | 原书p.xvi L165–166及扫描；不是创作、收藏或作品归属 | 已补双侧内容字段，交关系审查 |
| PHOTO-02 | 法国国家博物馆摄影文献服务机构 → 图版27b《路易十四》：供片 | 原书p.xvi L169–170；BnF只核机构署名 | 已补双侧内容字段，交关系审查 |
| PHOTO-03 | 佛罗伦萨Soprintendenza → 图版38a、38b、39、40a作品：供片 | 原书p.xvi L170–171；不因此解决40a具体版本 | 已补双侧内容字段，交关系审查 |
| PHOTO-04 | Stearn → 图版17b、26a、28b、56、63作品：供片 | 原书p.xvi L171及扫描；未指定底片号或拍摄时间 | 已补双侧内容字段，交关系审查 |
| PHOTO-05 | Stearn → 图版55的复制图像 | 原书未分55a／55b，Cacco另署55b；不可由另一署名反推排他归属 | 暂缓细分端点，不创建确定边 |
| PHOTO-06 | Royal Academy → 图版3b、30a、30b、31a、31b、47、49b、51、54、61b所示作品：供片 | 原书p.xvi L168–169；机构卡保存十个作品端点；不当成馆藏清单或1960展览名单 | 补全机构身份及证据跨度，交关系审查；未重复扩写十张作品卡 |
| PHOTO-07 | 国家摄影室 → ICCD：1975年并入 | ICCD官方历史，属外部新增候选；不倒填成原书事实 | 双侧端点已建，交关系审查 |
| PHOTO-08 | Soprintendenza → 佛罗伦萨；法国服务机构 → 巴黎；Stearn → 剑桥；Royal Academy → 伦敦：所在地 | 各机构卡的原书／外部事实级来源；历史供片角色不自动证明现址 | 地点端点已存在，交关系审查 |

### 结果与剩余工作

本轮5个既有机构完成名称、性质和历史语境的初步核对；13件作品只新增本书复制图像的供片证据，不把这一更新称为13件作品完成外部版本对齐或全面补足。新增ICCD一张，章前509个KU（458新建、47既有有效KU更新、4旧卡整理接收），全库880个。9项主候选保持待证；图版55细分、40a及其他具体印本／保管端点仍有缺口。

后续优先处理尚未对齐的机构、书目与作品版本；已获得稳定身份的对象按明确缺口补足，再集中审查全部候选与正文中的有据关系。不得把供片当创作、所有权或保管。未新增正式边，未再次提交推送，生成索引保持`664bb5d`同步基线。

上述19卡已写回：32条原书摘录、121条本地链接、来源编号及过程锚点检查通过，880条有效登记和509个章前KU计数一致，原sources前缀和正式relations保留；受影响内容机械检查无确定性发现，`git diff --check`通过。这不表示全面补足或关系定稿。

## 英国供片机构与大学图书馆

同轮继续处理12卡：Ministry of Works、Marlborough、Turners、Cambridge University Library四个供片机构及七件对应作品，新增剑桥大学作为图书馆所属端点。与前段合计31张不同卡，来源本体未改；未新增正式边。

### 实际来源与身份裁决

| 来源 | 实际读取与采纳 | 限制及未采纳内容 |
|---|---|---|
| [Historic England PSA01/04](https://historicengland.org.uk/images-books/photos/series/PSA01/04) | 完整可见系列目录，采用英国政府部门身份、Ministry of Works名称时期1943–1962和历史建筑／公共工程／政府地产职责，支持摄影业务 | 不把1943写成所有前身行政机构起源。系列由多个先后部门形成，不将全部底片归此部；未读底片原件，也未匹配本书图版29底片。旧议会档案链接转为档案首页，不充当原目录已读；前次国家档案馆验证墙已改用此适用机构目录补证 |
| [Marlborough档案历史](https://marlborougharchive.com/history-marlborough-gallery) | 1946两段及1947–1949题注；采用伦敦、1946创办、17–18 Old Bond Street初址和画廊／交易业务。原书图版目录L77与供片表L166合读，补《命运》供片互链 | 只读早期部分，未声称完整时间线已读。页面1948加入的David Somerset及后来公爵称号不自动解决原书《命运》的Duke of Beaufort具体持衔人。未采用Getty 500434822的Person分类和异常fl. -1946作分类／年代依据 |
| [Fading Images工作室记录研究](https://www.fadingimages.uk/RMCompleteV2.pdf) | HTTP取得134页PDF，读PDF1的材料说明、PDF3完整业务分析及PDF15日记转录／注16；Turners、Turner and Sons、剑桥、经销／冲印业务共同支持商号初步配对，分条录入研究转引的1933年地址 | 不是134页全文已读，未读1933目录原件及日记手稿。1932日记中Turner经研究者注释识别，保留二次识别层级；不将摄影师个人、法人注册名与商号强等同。Newcastle同名商号、Clare目录中“The Turners”题名不采用；本书三张照片的具体冲印时间／底片仍不明 |
| [剑桥馆方出版物：A Journey Around the World Mind](https://api.repository.cam.ac.uk/server/api/core/bitstreams/678848c7-a7b2-4a76-a937-ea1bbd5ba59c/content) | 大学资料库38页PDF；读题名页PDF2、馆长导言PDF3／印刷1、年表与出版项PDF38／印刷36；末页图像已查看。出版年2005、ISBN 0-902205-60-9；采用图书馆全名、研究服务、大学关联、1416最早明确记录、1424首目录、1934迁馆、2005出版地址 | 不是整册38页完整阅读。1416不强写精确创立日，1934不作大学或机构成立年；不为馆舍、设计师、每个捐赠者自动建立端点。官网About和展览History页直接访问失败，检索摘要仅定位，卡内采用实际读到的资料库PDF |

### 关系候选交接

| 锚点 | 端点／候选事实 | 实际证据与限定 | 去向 |
|---|---|---|---|
| PHOTO-09 | Ministry of Works → 图版29汉普顿宫楼梯壁画：为本书供片 | p.xvi L166；图版目录p.xiv L85–86另记女王复制许可；供片与许可分开，不推定绘画所有权 | 双侧内容已补，交关系审查 |
| PHOTO-10 | Marlborough → 图版24罗萨《命运》：为本书供片 | 供片p.xvi L166、作品p.xiii L77及原书扫描；未将画廊与博福特公爵收藏身份合并 | 双侧内容已补，交关系审查 |
| PHOTO-11 | Turners → 图版3a、17c、18a：为本书供片 | p.xvi L171–172，三件作品各有原图版目录摘录；原书供片事实成立，外部商号法律同一性未确认 | 内容关系保留，正式关系仅能采用原书署名粒度 |
| PHOTO-12 | Cambridge University Library → 图版9和57a：为本书供片 | p.xvi L172；图书馆名称已核，但本书所据两件印本的索书号未明 | 双侧内容已补，交关系审查；不直接写印本保管边 |
| PHOTO-13 | Cambridge University Library → University of Cambridge：大学所属研究图书馆 | 2005馆方导言与年表／出版项；外部候选 | 新建大学端点并互链，交关系审查 |
| PHOTO-14 | Marlborough → London；Turners及Cambridge University Library → Cambridge：地点关联 | 各自历史来源、原书署名；地址与时期保留 | 地点端点已存在，交关系审查 |

### 当前结果

章前510个KU（累计459新建、47既有有效KU更新、4旧卡整理接收），全库881个；本轮合计31卡（29更新、2新增）。四个英国机构的初步核对和图像角色进一步完善；Turners法律身份仍有粒度限制。9项主候选和其他作品／印本版本疑点保持待证，全文补足、正式关系定稿尚未完成。

后续先解决尚未初步对齐的机构与作品版本，重点包括Kassel藏品机构粒度、Stuttgart的Crespi作品版本、Wallraf的Piazzetta作品对应等。Wallraf旧baroque/gallery-9链接重定向到中世纪展厅，旧索引仍显示Piazzetta条目，不能用重定向正文证明该作品；本轮不采用这条冲突页面。已稳定对象按明确缺口继续补足，全部候选与正文事实交关系阶段审查。未再次提交推送，生成索引保持`664bb5d`基线。

本段12卡的19条原书摘录、63条本地链接、来源编号及过程锚点复核通过，881条有效登记和510个章前KU类型计数一致，原sources前缀与正式relations保留；受影响内容机械检查无确定性发现。本轮两段合计31卡、51条原书摘录、184条本地链接完成受影响范围核对，文档差异检查通过。这是语义自查与机械核对，不表示全面补足、正式关系定稿或人工验收。


## 德国馆藏版本与创作委托关系

REV-093接续；2026-09-15。上一轮31卡已于REV-103同步至03f41e5，本轮继续原目标。采用原书提及定位对象，以外部馆藏目录、专业研究与艺术家辞典核对版本及具体关系；不把外部补足当作原书陈述。先完成所涉身份与内容的语义判断，再将下列19条有据关系正式写入；其他对象的对齐、补足和关系阶段仍未全部完成。

### 实际阅读与版本裁决

1. **卡塞尔图版22a／GK 554**：阅读RKD Gerson Digital §2.4的Cerquozzi正文、图21、注38–40；图21将作品定名为Garden party of artists in Rome，1640年代初，Museum Schloss Wilhelmshöhe，GK 554。没有通读该长章。另通过RKD数字化合订卷阅读Andrea Bayer〈A Note on Ribera’s Drawing of Niccolo Simonelli〉全文、图注及注释（Metropolitan Museum Journal 30，1995，印刷73–80页；104页合订PDF的72–79页），并查看PDF74／印刷75页图4图像。图4记约1650、布面油画97.5×132.5厘米，两个断代并列。馆藏专站超时；Met提供的下载返回一页空白PDF，已渲染确认，未把HTTP200算作原文。实际依据为RKD复制的期刊原页与RKD研究正文。
2. **卡塞尔人物与机构边界**：Bayer将左侧黑衣人辨认为Simonelli，注6追溯Briganti、Spezzaferro及Laureati；保留研究性辨认，不写确定的has_subject，更不从同图推出每个人的friend_of。其他可能人物以及“医生Vincenzo Neri”没有在本轮采纳为确定端点。RKD注39所说旧藏Paets／Wittert、下落不明的Bent群像不是GK 554，不混入其收藏史，也不据此认定画家加入Bent。书中Kunstsammlungen的机构粒度与RKD的Museum Schloss Wilhelmshöhe分别保留；新建后者，不把两名称默认为同一法人、先后转让或建筑本体。
3. **斯图加特图版67／3294**：Zeri对象记录已完整阅读（网页URL work/121785；正文Entry number 119514，二者分开）；年代1728–1729、画布、186×215厘米。Treccani DBI的Crespi专段记为卢卡商人Stefano Conti所作，与Zeri的Conti收藏（1729起）相合，新建Conti及卢卡。DBI该段引用Haskell 1966与Merriman 1976，所以不能作为完全独立于本书的再验证。仅采纳本件相关内容，没有将所读传记所有生平及作品一并摄入；DBI的1746卒年与其他记录1747冲突未用于本轮人物生卒字段。
4. **斯图加特流传与同题版本**：Zeri列Conti（Lucca，1729起）、Albert（Wiesbaden及London，无日期）、Sotheby's London（1974-12-11，lot23）、Colnaghi London（1976–1977）、Staatsgalerie Stuttgart。此次正式写Colnaghi经手及馆藏保管；Albert个人身份及其两地迁移时点未定，Sotheby拍卖对应原目录未读，保留此处作为后续流传链待补，不凭目录位置自动推定所有权。Christie's lot6486418的页面正文另记109.5×94厘米的拍卖品，并列Kimbell AP1984.17与Stuttgart3294两个其他版本；该拍品尺寸、1968／1995拍卖记录及其特定构图解释均未移植到3294。
5. **科隆图版54／2806及米兰素描**：SIRBeC 4y010-09084完整10页PDF已读；主对象是米兰Testa femminile di profilo（4884/8 C 526/1），不是科隆画作。PDF4对应作品字段给Idillio、1745、Cologne、2806；PDF5评论给不晚于1745、Schulenburg及芝加哥配对画作。米兰素描241×186毫米，纸色在材料字段记蓝色、描述记灰色，均保留。Pallucchini将其视为Cleveland《Il fiorellin d’amore》（38.387）的准备稿，Leslie Jones联系科隆画作；Barbara身份只是拟议辨认。因此不写素描至油画的确定创作依存边，不新建未核的Barbara人物；替代解释和Cleveland端点仍待证。本轮采用创作者、材质尺寸、库存和保管信息；Trivulzio／Belgioioso旧藏、1943捐赠及市政府所有权尚未补齐端点，未把这张新卡称为全面补足完成。
6. **芝加哥配对画／1937.68**：馆方网页403后，公开API artwork23333成功读取。已读作品字段、description全文、provenance_text全文及publication_history／exhibition_history全部返回字段。馆号1937.68、1740年、布面油画191.8×143厘米；Schulenburg委托、1743年清单已载，1937年本馆购入。与SIRBeC所述Chicago Scena pastorale配合，落实配对对象。含葡萄的男童被释为Bacchus只是解释，未写确定has_subject。API同时列Greenwood及后继经手人等完整流传链，此次仅采入委托、1743清单、1937购入和保管；中间流传的端点及其馆方“不足证”限定后续处理，未认定全链已完成。科隆旧gallery-9链接现指向中世纪页面，Kulturelles-Erbe为校验挑战，均未记为实际读取到2806内容；未采用搜索缓存中的尺寸或取得年。

### 正式关系裁决

以下为模型依据具体来源逐项作出的语义决定，既有正文链接不自动转为关系。每条在来源KU的relations保存一次，阅读表提供出入方向及原关系证据入口；反向视图不新增事实。Museum Schloss Wilhelmshöhe与Kunstsammlungen两条保管边的来源范围不同，不表达转让。

| 来源KU | 正式关系 | 端点 | 时间／范围 | 证据 |
|---|---|---|---|---|
| [works/michelangelo-cerquozzi-the-artist-with-a-group-of-friends.md](../../../04-knowledge/units/works/michelangelo-cerquozzi-the-artist-with-a-group-of-friends.md) | created_by | [persons/michelangelo-cerquozzi.md](../../../04-knowledge/units/persons/michelangelo-cerquozzi.md) | ；图版22a | [patrons-and-painters](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；lines 75–75; print p. xiii |
| [works/michelangelo-cerquozzi-the-artist-with-a-group-of-friends.md](../../../04-knowledge/units/works/michelangelo-cerquozzi-the-artist-with-a-group-of-friends.md) | has_subject | [persons/michelangelo-cerquozzi.md](../../../04-knowledge/units/persons/michelangelo-cerquozzi.md) | ；图版22a题名所指画家自我描绘 | [patrons-and-painters](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；lines 75–75; print p. xiii |
| [works/michelangelo-cerquozzi-the-artist-with-a-group-of-friends.md](../../../04-knowledge/units/works/michelangelo-cerquozzi-the-artist-with-a-group-of-friends.md) | held_by | [institutions/kunstsammlungen-kassel.md](../../../04-knowledge/units/institutions/kunstsammlungen-kassel.md) | ；本书图版22a所记保管机构；不推定取得时间 | [patrons-and-painters](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；lines 75–75; print p. xiii |
| [works/michelangelo-cerquozzi-the-artist-with-a-group-of-friends.md](../../../04-knowledge/units/works/michelangelo-cerquozzi-the-artist-with-a-group-of-friends.md) | held_by | [institutions/museum-schloss-wilhelmshoehe.md](../../../04-knowledge/units/institutions/museum-schloss-wilhelmshoehe.md) | ；RKD图21所记保管机构；不视为与书中机构之间的转让 | [rkd-gerson-italy](https://gersonitaly.rkdstudies.nl/2-rome/24-bambocciate-rome-and-beyond/)；图21；GK 554 |
| [institutions/museum-schloss-wilhelmshoehe.md](../../../04-knowledge/units/institutions/museum-schloss-wilhelmshoehe.md) | located_at | [places/kassel.md](../../../04-knowledge/units/places/kassel.md) | ；馆藏说明中的博物馆所在地 | [rkd-gerson-italy](https://gersonitaly.rkdstudies.nl/2-rome/24-bambocciate-rome-and-beyond/)；图21；GK 554 |
| [works/g-m-crespi-jupiter-handed-over-by-cybele-to-the-corybantes-to-be-fed.md](../../../04-knowledge/units/works/g-m-crespi-jupiter-handed-over-by-cybele-to-the-corybantes-to-be-fed.md) | created_by | [persons/giuseppe-maria-crespi.md](../../../04-knowledge/units/persons/giuseppe-maria-crespi.md) | 1728–1729；Stuttgart inv.3294 | [zeri-119514](https://catalogo.fondazionezeri.unibo.it/entry/work/121785/Crespi%20Giuseppe%20Maria%20%28Spagnoletto%29%2C%20Educazione%20di%20Giove)；AUTHOR、Dating；Stuttgart inv.3294 |
| [works/g-m-crespi-jupiter-handed-over-by-cybele-to-the-corybantes-to-be-fed.md](../../../04-knowledge/units/works/g-m-crespi-jupiter-handed-over-by-cybele-to-the-corybantes-to-be-fed.md) | commissioned_by | [persons/stefano-conti.md](../../../04-knowledge/units/persons/stefano-conti.md) | 1728–1729；Stuttgart的Giove tra i coribanti | [dbi-crespi](https://www.treccani.it/enciclopedia/crespi-giuseppe-maria-detto-lo-spagnolo_(Dizionario-Biografico)/)；Giove tra i coribanti专段 |
| [works/g-m-crespi-jupiter-handed-over-by-cybele-to-the-corybantes-to-be-fed.md](../../../04-knowledge/units/works/g-m-crespi-jupiter-handed-over-by-cybele-to-the-corybantes-to-be-fed.md) | held_by | [institutions/staatsgalerie-stuttgart.md](../../../04-knowledge/units/institutions/staatsgalerie-stuttgart.md) | ；目录最后已知保管机构；不推定取得年 | [zeri-119514](https://catalogo.fondazionezeri.unibo.it/entry/work/121785/Crespi%20Giuseppe%20Maria%20%28Spagnoletto%29%2C%20Educazione%20di%20Giove)；LOCATIONS：Last known、inv.3294 |
| [works/g-m-crespi-jupiter-handed-over-by-cybele-to-the-corybantes-to-be-fed.md](../../../04-knowledge/units/works/g-m-crespi-jupiter-handed-over-by-cybele-to-the-corybantes-to-be-fed.md) | handled_by | [institutions/colnaghi.md](../../../04-knowledge/units/institutions/colnaghi.md) | 1976–1977；Stuttgart inv.3294的市场经手记录 | [zeri-119514](https://catalogo.fondazionezeri.unibo.it/entry/work/121785/Crespi%20Giuseppe%20Maria%20%28Spagnoletto%29%2C%20Educazione%20di%20Giove)；Previous location：Colnaghi, Londra, 1976–1977 |
| [works/piazzetta-idyll.md](../../../04-knowledge/units/works/piazzetta-idyll.md) | created_by | [persons/piazzetta.md](../../../04-knowledge/units/persons/piazzetta.md) | ；图版54，科隆2806 | [patrons-and-painters](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；lines 132–132; print p. xv |
| [works/piazzetta-idyll.md](../../../04-knowledge/units/works/piazzetta-idyll.md) | held_by | [institutions/wallraf-richartz-museum.md](../../../04-knowledge/units/institutions/wallraf-richartz-museum.md) | ；目录对应作品2806的保管机构 | [sirbec-4y010-09084](https://www.lombardiabeniculturali.it/opere-arte/schede-complete/4y010-09084/)；PDF4：Idillio、inv.2806 |
| [works/piazzetta-idyll.md](../../../04-knowledge/units/works/piazzetta-idyll.md) | commissioned_by | [persons/marshal-schulenburg.md](../../../04-knowledge/units/persons/marshal-schulenburg.md) | 不晚于1745；科隆Idillio，为Schulenburg所作 | [sirbec-4y010-09084](https://www.lombardiabeniculturali.it/opere-arte/schede-complete/4y010-09084/)；PDF5：Notizie storico-critiche |
| [works/piazzetta-idyll.md](../../../04-knowledge/units/works/piazzetta-idyll.md) | pendant_of | [works/piazzetta-pastoral-scene-chicago.md](../../../04-knowledge/units/works/piazzetta-pastoral-scene-chicago.md) | ；科隆2806与芝加哥1937.68；后者身份由馆方23333记录核对 | [sirbec-4y010-09084](https://www.lombardiabeniculturali.it/opere-arte/schede-complete/4y010-09084/)；PDF5：Idillio与Scena pastorale配对说明 |
| [works/piazzetta-female-head-in-profile-milan.md](../../../04-knowledge/units/works/piazzetta-female-head-in-profile-milan.md) | created_by | [persons/piazzetta.md](../../../04-knowledge/units/persons/piazzetta.md) | ；米兰4884/8 C 526/1 | [sirbec-4y010-09084](https://www.lombardiabeniculturali.it/opere-arte/schede-complete/4y010-09084/)；PDF4：AUTORE |
| [works/piazzetta-female-head-in-profile-milan.md](../../../04-knowledge/units/works/piazzetta-female-head-in-profile-milan.md) | held_by | [institutions/gabinetto-dei-disegni-castello-sforzesco.md](../../../04-knowledge/units/institutions/gabinetto-dei-disegni-castello-sforzesco.md) | ；米兰4884/8 C 526/1 | [sirbec-4y010-09084](https://www.lombardiabeniculturali.it/opere-arte/schede-complete/4y010-09084/)；PDF3：COLLOCAZIONE SPECIFICA、INVENTARIO |
| [works/piazzetta-pastoral-scene-chicago.md](../../../04-knowledge/units/works/piazzetta-pastoral-scene-chicago.md) | created_by | [persons/piazzetta.md](../../../04-knowledge/units/persons/piazzetta.md) | 1740；1937.68 | [aic-23333](https://api.artic.edu/api/v1/artworks/23333)；artist_display、date_display |
| [works/piazzetta-pastoral-scene-chicago.md](../../../04-knowledge/units/works/piazzetta-pastoral-scene-chicago.md) | commissioned_by | [persons/marshal-schulenburg.md](../../../04-knowledge/units/persons/marshal-schulenburg.md) | 不晚于1743；1937.68；1743年清单已有记录 | [aic-23333](https://api.artic.edu/api/v1/artworks/23333)；description、provenance_text首句 |
| [works/piazzetta-pastoral-scene-chicago.md](../../../04-knowledge/units/works/piazzetta-pastoral-scene-chicago.md) | acquired_by | [institutions/art-institute-of-chicago.md](../../../04-knowledge/units/institutions/art-institute-of-chicago.md) | 1937；1937.68 | [aic-23333](https://api.artic.edu/api/v1/artworks/23333)；provenance_text末句：purchased by Art Institute, 1937 |
| [works/piazzetta-pastoral-scene-chicago.md](../../../04-knowledge/units/works/piazzetta-pastoral-scene-chicago.md) | held_by | [institutions/art-institute-of-chicago.md](../../../04-knowledge/units/institutions/art-institute-of-chicago.md) | ；馆藏1937.68 | [aic-23333](https://api.artic.edu/api/v1/artworks/23333)；馆方对象记录、main_reference_number |

### 待证与否决去向

- 保留待证：Kassel年代异文、Simonelli及其他人物辨认；米兰素描对应两件作品的不同研究判断；科隆少女是否Barbara；Crespi的Albert收藏身份和完整交易链；芝加哥及米兰作品的中间收藏端点。9条主候选仍不改变。
- 否决套用：失踪Bent群像的流传和团体身份、Christie's其他朱庇特版本的尺寸及拍卖史、科隆旧页面重定向内容、HTTP200空白PDF、以配对或同图推论朋友／家族关系。
- 本轮内容写回保留原sources顺序、原书引句及既有正式关系；新增外部实体不附造原书引文。可成立的19条关系进入正式记录，不因相关对象另有缺口而搁置；上述不确定关系不转正。仍须继续完成全任务的其他对齐、补足与关系裁决。


## 供片关系集中定稿

REV-093接续；2026-09-15。集中复核既有PHOTO-01–04、06、09–12的30件图版与9个供片机构，不重新采集已读资料。逐项对照机构卡、作品卡和图片来源的原句／页行，采用上一轮已经完成的p.xvi扫描核字，确认Stearn、Nazionale、10b及Marlborough；Royal Academy取L168–169完整跨行署名。以下关系单侧保存在作品卡，机构卡显示反向导航；全部限定于本书复制图像的供应，不表达作品创作、所有权、原定安置、实际拍摄者或拍摄时间。

| 原候选 | 图版 | 作品端点 | 供片机构 | 裁决与来源范围 |
|---|---|---|---|---|
| PHOTO-01 | 10b | [pietro-da-cortona-rape-of-helen](../../../04-knowledge/units/works/pietro-da-cortona-rape-of-helen.md) | [gabinetto-fotografico-nazionale](../../../04-knowledge/units/institutions/gabinetto-fotografico-nazionale.md) | 正式supplied_by；PDF13；印刷xvi；图片来源；lines 165–166 |
| PHOTO-01 | 12 | [andrea-sacchi-allegory-of-divine-wisdom](../../../04-knowledge/units/works/andrea-sacchi-allegory-of-divine-wisdom.md) | [gabinetto-fotografico-nazionale](../../../04-knowledge/units/institutions/gabinetto-fotografico-nazionale.md) | 正式supplied_by；PDF13；印刷xvi；图片来源；lines 165–166 |
| PHOTO-01 | 15 | [andrea-pozzo-modello-for-fresco-on-vault-of-s-ignazio](../../../04-knowledge/units/works/andrea-pozzo-modello-for-fresco-on-vault-of-s-ignazio.md) | [gabinetto-fotografico-nazionale](../../../04-knowledge/units/institutions/gabinetto-fotografico-nazionale.md) | 正式supplied_by；PDF13；印刷xvi；图片来源；lines 165–166 |
| PHOTO-02 | 27b | [bernini-louis-xiv](../../../04-knowledge/units/works/bernini-louis-xiv.md) | [service-de-documentation-photographique-des-musees-nationaux](../../../04-knowledge/units/institutions/service-de-documentation-photographique-des-musees-nationaux.md) | 正式supplied_by；lines 169–170; 章前：图片来源；印刷页xvi |
| PHOTO-03 | 38a | [sebastiano-ricci-rape-of-europa](../../../04-knowledge/units/works/sebastiano-ricci-rape-of-europa.md) | [soprintendenza-alle-gallerie-florence](../../../04-knowledge/units/institutions/soprintendenza-alle-gallerie-florence.md) | 正式supplied_by；lines 170–171; 章前：图片来源；印刷页xvi |
| PHOTO-03 | 38b | [sebastiano-ricci-pan-and-syrinx](../../../04-knowledge/units/works/sebastiano-ricci-pan-and-syrinx.md) | [soprintendenza-alle-gallerie-florence](../../../04-knowledge/units/institutions/soprintendenza-alle-gallerie-florence.md) | 正式supplied_by；lines 170–171; 章前：图片来源；印刷页xvi |
| PHOTO-03 | 39 | [sebastiano-ricci-venus-and-adonis](../../../04-knowledge/units/works/sebastiano-ricci-venus-and-adonis.md) | [soprintendenza-alle-gallerie-florence](../../../04-knowledge/units/institutions/soprintendenza-alle-gallerie-florence.md) | 正式supplied_by；lines 170–171; 章前：图片来源；印刷页xvi |
| PHOTO-03 | 40a | [a-d-gabbiani-a-group-of-musicians](../../../04-knowledge/units/works/a-d-gabbiani-a-group-of-musicians.md) | [soprintendenza-alle-gallerie-florence](../../../04-knowledge/units/institutions/soprintendenza-alle-gallerie-florence.md) | 正式supplied_by；lines 170–171; 章前：图片来源；印刷页xvi |
| PHOTO-04 | 17b | [claude-mellan-vincenzo-giustiniani](../../../04-knowledge/units/works/claude-mellan-vincenzo-giustiniani.md) | [stearn-and-son](../../../04-knowledge/units/institutions/stearn-and-son.md) | 正式supplied_by；PDF13；印刷xvi；图片来源；lines 171–171 |
| PHOTO-04 | 26a | [nanteuil-cardinal-mazarin-in-his-gallery](../../../04-knowledge/units/works/nanteuil-cardinal-mazarin-in-his-gallery.md) | [stearn-and-son](../../../04-knowledge/units/institutions/stearn-and-son.md) | 正式supplied_by；PDF13；印刷xvi；图片来源；lines 171–171 |
| PHOTO-04 | 28b | [burnacini-the-elysian-fields](../../../04-knowledge/units/works/burnacini-the-elysian-fields.md) | [stearn-and-son](../../../04-knowledge/units/institutions/stearn-and-son.md) | 正式supplied_by；PDF13；印刷xvi；图片来源；lines 171–171 |
| PHOTO-04 | 56 | [marieschi-picture-exhibition-at-church-of-s-rocco](../../../04-knowledge/units/works/marieschi-picture-exhibition-at-church-of-s-rocco.md) | [stearn-and-son](../../../04-knowledge/units/institutions/stearn-and-son.md) | 正式supplied_by；PDF13；印刷xvi；图片来源；lines 171–171 |
| PHOTO-04 | 63 | [domenico-cerato-original-proposals-for-reclaiming-pra-della-valle](../../../04-knowledge/units/works/domenico-cerato-original-proposals-for-reclaiming-pra-della-valle.md) | [stearn-and-son](../../../04-knowledge/units/institutions/stearn-and-son.md) | 正式supplied_by；PDF13；印刷xvi；图片来源；lines 171–171 |
| PHOTO-06 | 3b | [carlo-maratta-cardinal-antonio-barberini](../../../04-knowledge/units/works/carlo-maratta-cardinal-antonio-barberini.md) | [royal-academy](../../../04-knowledge/units/institutions/royal-academy.md) | 正式supplied_by；lines 168–169; 章前：图片来源；印刷页xvi |
| PHOTO-06 | 30a | [massimo-stanzione-jerome-bankes](../../../04-knowledge/units/works/massimo-stanzione-jerome-bankes.md) | [royal-academy](../../../04-knowledge/units/institutions/royal-academy.md) | 正式supplied_by；lines 168–169; 章前：图片来源；印刷页xvi |
| PHOTO-06 | 30b | [carlo-dolci-sir-thomas-baines](../../../04-knowledge/units/works/carlo-dolci-sir-thomas-baines.md) | [royal-academy](../../../04-knowledge/units/institutions/royal-academy.md) | 正式supplied_by；lines 168–169; 章前：图片来源；印刷页xvi |
| PHOTO-06 | 31a | [carlo-maratta-charles-fox](../../../04-knowledge/units/works/carlo-maratta-charles-fox.md) | [royal-academy](../../../04-knowledge/units/institutions/royal-academy.md) | 正式supplied_by；lines 168–169; 章前：图片来源；印刷页xvi |
| PHOTO-06 | 31b | [carlo-maratta-sir-thomas-isham](../../../04-knowledge/units/works/carlo-maratta-sir-thomas-isham.md) | [royal-academy](../../../04-knowledge/units/institutions/royal-academy.md) | 正式supplied_by；lines 168–169; 章前：图片来源；印刷页xvi |
| PHOTO-06 | 47 | [marco-ricci-an-operatic-rehearsal](../../../04-knowledge/units/works/marco-ricci-an-operatic-rehearsal.md) | [royal-academy](../../../04-knowledge/units/institutions/royal-academy.md) | 正式supplied_by；lines 168–169; 章前：图片来源；印刷页xvi |
| PHOTO-06 | 49b | [amigoni-jupiter-and-io](../../../04-knowledge/units/works/amigoni-jupiter-and-io.md) | [royal-academy](../../../04-knowledge/units/institutions/royal-academy.md) | 正式supplied_by；lines 168–169; 章前：图片来源；印刷页xvi |
| PHOTO-06 | 51 | [canaletto-view-from-badminton-1748](../../../04-knowledge/units/works/canaletto-view-from-badminton-1748.md) | [royal-academy](../../../04-knowledge/units/institutions/royal-academy.md) | 正式supplied_by；lines 168–169; 章前：图片来源；印刷页xvi |
| PHOTO-06 | 54 | [piazzetta-idyll](../../../04-knowledge/units/works/piazzetta-idyll.md) | [royal-academy](../../../04-knowledge/units/institutions/royal-academy.md) | 正式supplied_by；lines 168–169; 章前：图片来源；印刷页xvi |
| PHOTO-06 | 61b | [tiepolo-banquet-victoria](../../../04-knowledge/units/works/tiepolo-banquet-victoria.md) | [royal-academy](../../../04-knowledge/units/institutions/royal-academy.md) | 正式supplied_by；lines 168–169; 章前：图片来源；印刷页xvi |
| PHOTO-09 | 29 | [antonio-verrio-fresco-on-staircase-of-hampton-court-palace](../../../04-knowledge/units/works/antonio-verrio-fresco-on-staircase-of-hampton-court-palace.md) | [ministry-of-works](../../../04-knowledge/units/institutions/ministry-of-works.md) | 正式supplied_by；lines 166–166; 章前：图片来源；印刷页xvi |
| PHOTO-10 | 24 | [fortune-salvator-rosa](../../../04-knowledge/units/works/fortune-salvator-rosa.md) | [marlborough-fine-art-ltd](../../../04-knowledge/units/institutions/marlborough-fine-art-ltd.md) | 正式supplied_by；PDF13；印刷xvi；图片来源；lines 166–166 |
| PHOTO-11 | 3a | [ottavio-leoni-cardinal-francesco-barberini](../../../04-knowledge/units/works/ottavio-leoni-cardinal-francesco-barberini.md) | [turners-of-cambridge](../../../04-knowledge/units/institutions/turners-of-cambridge.md) | 正式supplied_by；lines 171–172; 章前：图片来源；印刷页xvi |
| PHOTO-11 | 17c | [ottavio-leoni-paolo-giordano-orsini-duke-of-bracciano](../../../04-knowledge/units/works/ottavio-leoni-paolo-giordano-orsini-duke-of-bracciano.md) | [turners-of-cambridge](../../../04-knowledge/units/institutions/turners-of-cambridge.md) | 正式supplied_by；lines 171–172; 章前：图片来源；印刷页xvi |
| PHOTO-11 | 18a | [pietro-testa-rest-on-the-flight-into-egypt](../../../04-knowledge/units/works/pietro-testa-rest-on-the-flight-into-egypt.md) | [turners-of-cambridge](../../../04-knowledge/units/institutions/turners-of-cambridge.md) | 正式supplied_by；lines 171–172; 章前：图片来源；印刷页xvi |
| PHOTO-12 | 9 | [guido-abbatini-frontispiece-of-aedes-barberinae-ad-quirinalem](../../../04-knowledge/units/works/guido-abbatini-frontispiece-of-aedes-barberinae-ad-quirinalem.md) | [university-library-cambridge](../../../04-knowledge/units/institutions/university-library-cambridge.md) | 正式supplied_by；lines 172–172; 章前：图片来源；印刷页xvi |
| PHOTO-12 | 57a | [piazzetta-final-plate-of-illustrations-to-gerusalemme-liberata](../../../04-knowledge/units/works/piazzetta-final-plate-of-illustrations-to-gerusalemme-liberata.md) | [university-library-cambridge](../../../04-knowledge/units/institutions/university-library-cambridge.md) | 正式supplied_by；lines 172–172; 章前：图片来源；印刷页xvi |


PHOTO-05（Stearn署55）仍暂缓细分；Cacco署55b不能反推出Stearn只供55a。PHOTO-03中的40a虽未完成外部版本确认，书中图版与供片机构的关系已明确，scope只指书中该图版。PHOTO-11采用原书Turners署名粒度，不提升为法律实体已核。PHOTO-12只记录复制图像供片，不从University Library之名推出本书两件印本的保管或索书号。PHOTO-06不视为1960年展览目录，也不将供片名单改成Royal Academy作品收藏。

PHOTO-07、08、13、14中的机构沿革、大学归属和所在地尚未在此批转正，继续沿各自外部证据审查。此轮使已确定的供片候选实际进入正式关系，不以机构内容已补代替关系阶段处理。9项主候选仍保留待证，所有对象的全面补足与关系定稿仍未完成。

### 应用与验证结果

两段均先形成明确语义决定、完整前后文本及dry-run差异，逐文件前置校验后通过稳定文件编辑接口应用。德国馆藏段23个文件与计划逐字一致，供片段42个文件与计划逐字一致；两段共有57张不同知识元卡（其中5张新建），其余为过程、结果及用户要求的处理记录。关系阅读表由既有投影函数只更新直接受影响卡，不从链接自动选择关系。

最终复核57卡的94条原书摘录、491条本地链接，既有sources前缀和原正式关系均保留。49条新增关系逐条在派生索引找到唯一对应，其端点、类型、time／role／scope及evidence_ref与权威记录一致；索引共459条，其中458条explicit、1条既有规则反向边。新配对关系另一侧可由卡内反向导航找回，未反写第二条事实。有效登记886个，章前516个KU（人物213、机构77、文献18、地点89、术语4、作品111、家族3、事件1），与结果表一致。

德国馆藏与词表变更后的完整同步检查通过，274项测试通过；追加30条供片后再次完成受影响内容检查和14步同步检查，断端点、非法关系类型、缺失反向映射及弱证据检查均通过。此为语义自查及机械验证，不是人工校验或全任务语义验收。页面数据未刷新，本轮未提交推送。


## 机构沿革出版责任与研究支持定稿

REV-093接续；2026-09-15。上一轮已形成49条正式关系，本轮继续逐项裁决PHOTO-07、08、13、14及INST候选，并反查本书、书评和论文中的明确责任字段。正式边来自下列人工语义决定，不由正文链接或共同出现自动生成。

### 依据与边界

- 再读ICCD机构史正文、Warburg历史的首段／迁伦敦段、Yale出版社1961–1984年伦敦分部段及Correr Library介绍；沿用已读的剑桥馆方2005年PDF题名、馆长导言和年表／出版项，以及其他机构卡明确引用的目录记录。GFN1975年并入后继续活动，用part_of表达组成，不以merged_into暗示业务终止。Warburg及Yale的起年分别为1944、1961，后者财务和运营自主保留。大学、研究所与图书馆仍是不同端点。
- 书中城市署名只支持对应历史机构的城市；Royal Academy伦敦依据1960目录，Marlborough依据1946创办历史，Cambridge Library的West Road限定2005出版项。不把这些时点外推为所有年代的地址。Turners仍采用原书商号粒度，Stearn图版55细分继续待证。
- 本轮重读第一版序言L21–23、第二版序言L11–12、书名版权页、第二版导言L176–198及Conforti／Waterhouse书目定位。图书馆的研究支持与人员帮助分别保留，不由致谢推断雇佣。书目责任与论文原件阅读分开。Honour书评的具体正式题名和页码没有据此补造。
- 机构沿革、图书馆归属、出版／版权、CIP与印制采用各自角色；版权owned_by严格限于1980版权页标注的著作权，不表达印刷载体所有权。Constable的印制工作只限初版。Chatto是初版合作支持，Nicoll的新版本建议不由相邻句推成Chatto雇佣。Poerson1704院长任职与1708在任有据，1724／1725任职终期仍不确定。
- 本轮新补足Nicoll：Yale官方历史明确其1973年受聘管理伦敦办事处并持续约30年，解决原来未定的任职机构。按当年出版社及伦敦部门粒度记录，不新建法人身份未单独核定的分部，不将约30年计算成精确离职日。
- Finnish Institute使用罗马Villa Lante的建筑事实沿用已读罗马市介绍；不因此形成建筑所有权或《罗马寓意》的原定安置关系。Correr的遗赠支持与馆藏作品的所有／保管边分开，不补造具体遗赠法律生效日。

### 正式关系

| 来源KU | 关系 | 端点 | 时间／角色／范围 | 证据 |
|---|---|---|---|---|
| [institutions/gabinetto-fotografico-nazionale.md](../../../04-knowledge/units/institutions/gabinetto-fotografico-nazionale.md) | part_of | [institutions/istituto-centrale-per-il-catalogo-e-la-documentazione.md](../../../04-knowledge/units/institutions/istituto-centrale-per-il-catalogo-e-la-documentazione.md) | 1975起；组成机构；1975年并入后作为ICCD组成部分继续运作；不记录为停止摄影活动 | [来源](https://iccd.beniculturali.it/it/fotografia/gabinettofotograficonazionale)；机构史1895设立与1975并入段 |
| [institutions/soprintendenza-alle-gallerie-florence.md](../../../04-knowledge/units/institutions/soprintendenza-alle-gallerie-florence.md) | located_at | [places/florence.md](../../../04-knowledge/units/places/florence.md) | ；；本书图片来源所列历史监管机构所在地 | [来源](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；lines 170–171; 章前：图片来源；印刷页xvi |
| [institutions/service-de-documentation-photographique-des-musees-nationaux.md](../../../04-knowledge/units/institutions/service-de-documentation-photographique-des-musees-nationaux.md) | located_at | [places/paris.md](../../../04-knowledge/units/places/paris.md) | ；；本书供片署名所列巴黎；不推定今日地址 | [来源](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；lines 169–170; 章前：图片来源；印刷页xvi |
| [institutions/stearn-and-son.md](../../../04-knowledge/units/institutions/stearn-and-son.md) | located_at | [places/cambridge.md](../../../04-knowledge/units/places/cambridge.md) | ；营业城市；档案规范记录中的摄影商号历史所在地；72 Bridge Street | [来源](https://collegecollections.jesus.cam.ac.uk/index.php/stearn-sons-photographers-bridge-street-cambridge)；Identity题名与History中的Bridge Street地址 |
| [institutions/royal-academy.md](../../../04-knowledge/units/institutions/royal-academy.md) | located_at | [places/london.md](../../../04-knowledge/units/places/london.md) | 1960年目录记录；；1960展览目录责任机构所列城市；不表示本书供片来自该展览 | [来源](https://www.nationaltrustcollections.org.uk/object/3119476)；Makers and roles：Royal Academy of Arts, London |
| [institutions/marlborough-fine-art-ltd.md](../../../04-knowledge/units/institutions/marlborough-fine-art-ltd.md) | located_at | [places/london.md](../../../04-knowledge/units/places/london.md) | 1946；初始营业城市；画廊初创时期所在城市，17–18 Old Bond Street | [来源](https://marlborougharchive.com/history-marlborough-gallery)；1946年创办两段 |
| [institutions/turners-of-cambridge.md](../../../04-knowledge/units/institutions/turners-of-cambridge.md) | located_at | [places/cambridge.md](../../../04-knowledge/units/places/cambridge.md) | ；；原书Turners of Cambridge署名粒度；不据此确认法律实体 | [来源](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；lines 171–172; 章前：图片来源；印刷页xvi |
| [institutions/university-library-cambridge.md](../../../04-knowledge/units/institutions/university-library-cambridge.md) | part_of | [institutions/university-of-cambridge.md](../../../04-knowledge/units/institutions/university-of-cambridge.md) | ；所属图书馆；大学所属研究图书馆，不与大学合并为同一KU | [来源](https://api.repository.cam.ac.uk/server/api/core/bitstreams/678848c7-a7b2-4a76-a937-ea1bbd5ba59c/content)；2005馆长导言PDF3／印刷1及PDF38／印刷36年表 |
| [institutions/university-library-cambridge.md](../../../04-knowledge/units/institutions/university-library-cambridge.md) | located_at | [places/cambridge.md](../../../04-knowledge/units/places/cambridge.md) | 2005年记录；出版项所列馆址；2005年出版项所列West Road城市；不倒填1416年的精确地址 | [来源](https://api.repository.cam.ac.uk/server/api/core/bitstreams/678848c7-a7b2-4a76-a937-ea1bbd5ba59c/content)；PDF38／印刷36出版项 |
| [institutions/warburg-institute.md](../../../04-knowledge/units/institutions/warburg-institute.md) | part_of | [institutions/university-of-london.md](../../../04-knowledge/units/institutions/university-of-london.md) | 1944起；大学所属研究所；1944年起成为伦敦大学组成机构；图书馆另设KU | [来源](https://warburg.sas.ac.uk/about-us/history-warburg-institute)；首段及The Move to London的1944段 |
| [institutions/warburg-institute-library.md](../../../04-knowledge/units/institutions/warburg-institute-library.md) | part_of | [institutions/warburg-institute.md](../../../04-knowledge/units/institutions/warburg-institute.md) | ；所属图书馆；第一版序言Library of the Warburg Institute；机构图书馆的归属 | [来源](../../../02-sources/02-Markdown/00_03_Preface_1st_Ed.md)；lines 21–22; 章前：第一版序言；印刷页ix；PDF 7 |
| [institutions/warburg-institute.md](../../../04-knowledge/units/institutions/warburg-institute.md) | located_at | [places/london.md](../../../04-knowledge/units/places/london.md) | 1933起；迁入城市；1933年迁入伦敦；不由此确定各阶段街道地址 | [来源](https://warburg.sas.ac.uk/about-us/history-warburg-institute)；首段及The Move to London |
| [institutions/warburg-institute-library.md](../../../04-knowledge/units/institutions/warburg-institute-library.md) | located_at | [places/london.md](../../../04-knowledge/units/places/london.md) | ；；第一版序言所述图书馆所在地 | [来源](../../../02-sources/02-Markdown/00_03_Preface_1st_Ed.md)；lines 21–22; 章前：第一版序言；印刷页ix；PDF 7 |
| [institutions/yale-university-press.md](../../../04-knowledge/units/institutions/yale-university-press.md) | part_of | [institutions/yale-university.md](../../../04-knowledge/units/institutions/yale-university.md) | 1961起；所属出版部门；出版社为大学所属部门，同时保持财务和运营自主 | [来源](https://yalebooks.yale.edu/a-brief-history-of-yale-university-press/)；II. Growth and Diversification，1961段 |
| [institutions/yale-university-press.md](../../../04-knowledge/units/institutions/yale-university-press.md) | located_at | [places/new-haven.md](../../../04-knowledge/units/places/new-haven.md) | 1910起；迁入城市；1910年迁往纽黑文；不外推当时的具体街址 | [来源](https://yalebooks.yale.edu/a-brief-history-of-yale-university-press/)；The First Half-Century的1910迁址段 |
| [institutions/yale-university-press.md](../../../04-knowledge/units/institutions/yale-university-press.md) | located_at | [places/london.md](../../../04-knowledge/units/places/london.md) | 1961起；伦敦分部；1961年设伦敦分部；不是纽黑文总部搬迁至伦敦 | [来源](https://yalebooks.yale.edu/a-brief-history-of-yale-university-press/)；II. Growth and Diversification，1961段 |
| [institutions/correr-library.md](../../../04-knowledge/units/institutions/correr-library.md) | part_of | [institutions/museo-correr.md](../../../04-knowledge/units/institutions/museo-correr.md) | ；所属图书馆；博物馆包含其威尼斯艺术与历史图书馆 | [来源](https://correr.visitmuve.it/en/library/)；The Library：The Correr Museum incorporates the Library |
| [institutions/correr-library.md](../../../04-knowledge/units/institutions/correr-library.md) | located_at | [places/venice.md](../../../04-knowledge/units/places/venice.md) | ；；第一版序言所述研究场所所在地 | [来源](../../../02-sources/02-Markdown/00_03_Preface_1st_Ed.md)；lines 23–23; 章前：第一版序言；印刷页ix；PDF 7 |
| [institutions/museo-correr.md](../../../04-knowledge/units/institutions/museo-correr.md) | located_at | [places/venice.md](../../../04-knowledge/units/places/venice.md) | ；；图版48b–48d所列科雷尔博物馆城市 | [来源](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；lines 126–126; 章前：图版目录；印刷页xv |
| [institutions/museo-correr.md](../../../04-knowledge/units/institutions/museo-correr.md) | supported_by | [persons/teodoro-correr.md](../../../04-knowledge/units/persons/teodoro-correr.md) | 1830；创立遗赠者；遗赠促成博物馆1830年创立；不补造遗赠法律生效日期 | [来源](https://correr.visitmuve.it/en/library/)；The Library首句：museum and library founded through bequest |
| [institutions/correr-library.md](../../../04-knowledge/units/institutions/correr-library.md) | supported_by | [persons/teodoro-correr.md](../../../04-knowledge/units/persons/teodoro-correr.md) | 1830；创立遗赠者；遗赠促成图书馆1830年创立；与博物馆端点分别记录 | [来源](https://correr.visitmuve.it/en/library/)；The Library首句：museum and library founded through bequest |
| [institutions/finnish-institute.md](../../../04-knowledge/units/institutions/finnish-institute.md) | located_at | [places/villa-lante-rome.md](../../../04-knowledge/units/places/villa-lante-rome.md) | ；机构使用建筑；机构使用的罗马Villa Lante建筑；不等于建筑所有权，也不确定作品原定安置 | [来源](https://www.turismoroma.it/it/luoghi/istituto-finlandese-di-roma)；机构介绍与地址：Villa Lante，Gianicolo |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | authored_by | [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | ；作者；本书作者；修订扩充版书名页 | [来源](../../../02-sources/02-Markdown/00_01_Title_Copyright.md)；lines 3–17; unnumbered title and copyright pages |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | published_by | [institutions/yale-university-press.md](../../../04-knowledge/units/institutions/yale-university-press.md) | 1980版；出版者；1980年修订扩充版；本件印刷年2006另记 | [来源](../../../02-sources/02-Markdown/00_01_Title_Copyright.md)；lines 3–17; unnumbered title and copyright pages |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | owned_by | [institutions/yale-university.md](../../../04-knowledge/units/institutions/yale-university.md) | 1980版权标注；1980年版权标注权利人；仅指版权页Copyright © 1980 by Yale University标注的著作版权；不指本件印刷载体或任意版本的所有权 | [来源](../../../02-sources/02-Markdown/00_01_Title_Copyright.md)；lines 16–16; 未编号版权页；PDF2 |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | contributed_by | [institutions/library-of-congress.md](../../../04-knowledge/units/institutions/library-of-congress.md) | ；出版编目提供者；版权页Library of Congress Cataloging in Publication Data；仅CIP书目编制，不表示保管本件 | [来源](../../../02-sources/02-Markdown/00_01_Title_Copyright.md)；lines 20–29; 未编号版权页；PDF2 |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | contributed_by | [institutions/t-and-a-constable.md](../../../04-knowledge/units/institutions/t-and-a-constable.md) | ；初版印刷、排版与文字核对；第一版序言致谢的初版印制工作；不套到2006年印刷 | [来源](../../../02-sources/02-Markdown/00_03_Preface_1st_Ed.md)；lines 22–22; 章前：第一版序言；印刷页ix；PDF 7 |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | supported_by | [institutions/chatto-and-windus.md](../../../04-knowledge/units/institutions/chatto-and-windus.md) | ；初版制作支持；第二版序言回顾公司负责人员给予初版制作的支持；未拆分具体负责人 | [来源](../../../02-sources/02-Markdown/00_02_Preface_2nd_Ed.md)；lines 11–12; 章前：第二版序言；印刷页vi；PDF 4 |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | supported_by | [persons/norah-smallwood.md](../../../04-knowledge/units/persons/norah-smallwood.md) | ；初版制作支持；第二版序言特别致谢的初版合作支持；不补造合同角色 | [来源](../../../02-sources/02-Markdown/00_02_Preface_2nd_Ed.md)；lines 11–12; 章前：第二版序言；印刷页vi；PDF 4 |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | supported_by | [persons/john-nicoll.md](../../../04-knowledge/units/persons/john-nicoll.md) | ；新版提议与制作帮助；第二版序言明确提议新版并协助；不将相邻Chatto署名当其雇主 | [来源](../../../02-sources/02-Markdown/00_02_Preface_2nd_Ed.md)；lines 11–12; 章前：第二版序言；印刷页vi；PDF 4 |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | supported_by | [institutions/warburg-institute-library.md](../../../04-knowledge/units/institutions/warburg-institute-library.md) | ；研究使用、鼓励与建议；第一版序言对图书馆及机构相关人员的集体致谢；不虚构具体顾问 | [来源](../../../02-sources/02-Markdown/00_03_Preface_1st_Ed.md)；lines 21–22; 章前：第一版序言；印刷页ix；PDF 7 |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | supported_by | [persons/terisio-pignatti.md](../../../04-knowledge/units/persons/terisio-pignatti.md) | ；提供研究便利；在威尼斯科雷尔图书馆研究时获得的便利；不据此推定Pignatti当时任职 | [来源](../../../02-sources/02-Markdown/00_03_Preface_1st_Ed.md)；lines 23–23; 章前：第一版序言；印刷页ix；PDF 7 |
| [persons/charles-francois-poerson.md](../../../04-knowledge/units/persons/charles-francois-poerson.md) | member_of | [institutions/french-academy-in-rome.md](../../../04-knowledge/units/institutions/french-academy-in-rome.md) | 1704起；1708在任；院长；1704获任院长，1708原书来信佐证仍在任；不确定1724／1725终期 | [来源](https://villamedici.it/directeur/charles-francois-poerson/)；Biographie任职段：1704年获任院长 |
| [archives/poerson-letter-1708.md](../../../04-knowledge/units/archives/poerson-letter-1708.md) | authored_by | [persons/charles-francois-poerson.md](../../../04-knowledge/units/persons/charles-francois-poerson.md) | 1708；写信人；本书所引1708年法语来信；收信人仅Mgr，不补造身份 | [来源](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；lines 191–192; 章前：第二版导言；印刷页xviii |
| [archives/honour-patrons-painters-review-1963.md](../../../04-knowledge/units/archives/honour-patrons-painters-review-1963.md) | authored_by | [persons/hugh-honour.md](../../../04-knowledge/units/persons/hugh-honour.md) | ；书评作者；本书导言所称Hugh Honour书评；非已读书评原件 | [来源](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；lines 176–177; 章前：第二版导言；印刷页xvii |
| [archives/honour-patrons-painters-review-1963.md](../../../04-knowledge/units/archives/honour-patrons-painters-review-1963.md) | has_subject | [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | ；所评著作；书评所评著作；评价经Haskell转述 | [来源](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；lines 176–177; 章前：第二版导言；印刷页xvii |
| [archives/honour-patrons-painters-review-1963.md](../../../04-knowledge/units/archives/honour-patrons-painters-review-1963.md) | part_of | [archives/apollo-periodical.md](../../../04-knowledge/units/archives/apollo-periodical.md) | 1963-12；刊载期刊；本书脚注定位Apollo 1963年12月，页码未补造 | [来源](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；lines 187–187; 章前：第二版导言；印刷页xvii |
| [archives/conforti-legros-designers-1977.md](../../../04-knowledge/units/archives/conforti-legros-designers-1977.md) | authored_by | [persons/michael-conforti.md](../../../04-knowledge/units/persons/michael-conforti.md) | 1977-08；论文作者；期刊官方目录的文章署名；不是已读论文全文 | [来源](https://www.burlington.org.uk/archive/back-issues/197708)；本期目录及Conforti论文条；未读付费论文正文 |
| [archives/conforti-legros-designers-1977.md](../../../04-knowledge/units/archives/conforti-legros-designers-1977.md) | part_of | [archives/burlington-magazine.md](../../../04-knowledge/units/archives/burlington-magazine.md) | 1977-08；刊载期刊；1977年8月，119卷893期；正文页码另见本书书目 | [来源](https://www.burlington.org.uk/archive/back-issues/197708)；本期目录及Conforti论文条；未读付费论文正文 |
| [archives/waterhouse-rome-painting-1971.md](../../../04-knowledge/units/archives/waterhouse-rome-painting-1971.md) | authored_by | [persons/ellis-waterhouse.md](../../../04-knowledge/units/persons/ellis-waterhouse.md) | 1971；论文作者；本书书目所列E. K. Waterhouse；书目事实不代替全文阅读 | [来源](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)；lines 1233–1234; 书后：书目；仅定向读取所引条目，印刷页未核 |
| [archives/waterhouse-rome-painting-1971.md](../../../04-knowledge/units/archives/waterhouse-rome-painting-1971.md) | part_of | [archives/museum-studies-art-institute-chicago.md](../../../04-knowledge/units/archives/museum-studies-art-institute-chicago.md) | 1971；刊载期刊；本书书目所列1971年Museum Studies论文pp.7–21 | [来源](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)；lines 1233–1234; 书后：书目；仅定向读取所引条目，印刷页未核 |
| [archives/museum-studies-art-institute-chicago.md](../../../04-knowledge/units/archives/museum-studies-art-institute-chicago.md) | published_by | [institutions/art-institute-of-chicago.md](../../../04-knowledge/units/institutions/art-institute-of-chicago.md) | ；期刊出版者；期刊出版机构；不因此逐篇验证其全部文章 | [来源](https://www.jstor.org/journal/artinstchicmuses)；JSTOR期刊页Published by |
| [archives/dizionario-biografico-degli-italiani.md](../../../04-knowledge/units/archives/dizionario-biografico-degli-italiani.md) | published_by | [institutions/istituto-della-enciclopedia-italiana.md](../../../04-knowledge/units/institutions/istituto-della-enciclopedia-italiana.md) | ；辞典出版机构；人物辞典出版项目的责任机构；辞典与机构分开 | [来源](https://www.treccani.it/istituto/la-nostra-storia.html)；机构成立时的出版项目及原名 |
| [persons/john-nicoll.md](../../../04-knowledge/units/persons/john-nicoll.md) | employed_by | [institutions/yale-university-press.md](../../../04-knowledge/units/institutions/yale-university-press.md) | 1973起；官方历史记此后约30年；伦敦办事处负责人；受聘负责出版社伦敦办事处；未补造精确离职日期 | [来源](https://yalebooks.yale.edu/a-brief-history-of-yale-university-press/)；II. Growth and Diversification：In 1973, John Nicoll was hired to oversee the Press’s London office |


### 候选去向

PHOTO-07、08、13、14已按上述对象范围转正。INST-01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、17的明确归属／职责进入正式记录；其中版权限定著作权、机构支持限定原文集体署名、Poerson终期继续待证。INST-16保留为推荐读者使用且未逐条引用的内容事实，不生成逐条cites边，也不从词典主题反推作者的学术归属。未处理作品的保管链、版本及不确定身份仍按原待证记录接续；本次定稿不表示全任务已完成。


## 馆藏作品创作收藏与借存关系定稿

REV-093接续；2026-09-15。REV-104已提交并实测同步至d53ffb5。本轮集中处理MUS-01–13及对应作品正文中已经采纳的角色；正式边逐条由语义判断形成，不由正文链接自动推断。

### 来源复核与新补足

- Nationalmuseum NMH 554/1863完整对象字段及Description、苏格兰NG 2193完整About／More about／对象字段、斯帕达馆方全文和ICCD1200962613网页均重读。ICCD同源PDF第1页第四室定位沿用上一轮已读全3页的证据。马苏奇画中莫拉及教宗分别建立描绘边；不因此给莫拉或教宗新增本素描创作／委托。
- 博伊曼斯网页经浏览工具失败后改公开HTTP读取，状态200；题名、作者及全部Specifications已读。1940借存的基金会与博物馆分别建立出借／借入边，Franz Koenigs为历史收藏者，保管不等于所有权。馆方约1680制作年代仍待比较，不当作波佐坐像日期。
- Cambridge Museums网页正文、两件肖像标签及SENSUAL VIRTUAL段已读，未声称观看嵌入视频。PD.13-1972的创作、委托、描绘和保管落实；补1972赠入。Finch与Dolci的朋友关系有独立明确词句。Finch与Baines的终身伴侣事实保留，不能将marriage of souls直接转换为法律配偶。
- Paris Musées浏览工具超时后公开HTTP200读取全部对象字段、图像学与历史说明、取得信息。J 104明确为墨尔本藏本的预备版本，采用model_for；补1928遗赠接收。NGV103-4对象、About、Frame及Frame Details本轮均读，补1933取得；两卡双语描述改为具体版本内容。新读的主题人物、画框参与人、遗赠人和流传细节仅作为具体待核线索列在下文，未据网页外链自动建KU。

### 正式关系

| 来源KU | 关系 | 端点 | 时间／角色／范围 | 证据 |
|---|---|---|---|---|
| [works/agostino-masucci-mola-painting-the-portrait-of-pope-alexander-vii.md](../../../04-knowledge/units/works/agostino-masucci-mola-painting-the-portrait-of-pope-alexander-vii.md) | created_by | [persons/agostino-masucci.md](../../../04-knowledge/units/persons/agostino-masucci.md) | ；绘图者；NMH 554/1863纸本黑粉笔素描 | [来源](https://collection.nationalmuseum.se/en/collection/item/82794/)；Artist/Maker、Inventory number |
| [works/agostino-masucci-mola-painting-the-portrait-of-pope-alexander-vii.md](../../../04-knowledge/units/works/agostino-masucci-mola-painting-the-portrait-of-pope-alexander-vii.md) | has_subject | [persons/pier-francesco-mola.md](../../../04-knowledge/units/persons/pier-francesco-mola.md) | ；描绘人物；画中正在绘制教宗肖像的莫拉；不代表此素描由莫拉创作 | [来源](https://collection.nationalmuseum.se/en/collection/item/82794/)；Description |
| [works/agostino-masucci-mola-painting-the-portrait-of-pope-alexander-vii.md](../../../04-knowledge/units/works/agostino-masucci-mola-painting-the-portrait-of-pope-alexander-vii.md) | has_subject | [persons/alexander-vii.md](../../../04-knowledge/units/persons/alexander-vii.md) | ；画中肖像的对象；莫拉所绘教宗肖像中的人物；不据此认定教宗委托马苏奇 | [来源](https://collection.nationalmuseum.se/en/collection/item/82794/)；Description |
| [works/agostino-masucci-mola-painting-the-portrait-of-pope-alexander-vii.md](../../../04-knowledge/units/works/agostino-masucci-mola-painting-the-portrait-of-pope-alexander-vii.md) | held_by | [institutions/national-museum-stockholm.md](../../../04-knowledge/units/institutions/national-museum-stockholm.md) | ；保管机构；NMH 554/1863馆藏记录；不据馆藏号后缀推定取得日期 | [来源](https://collection.nationalmuseum.se/en/collection/item/82794/)；对象题头、Inventory number、Collection |
| [works/rubens-the-feast-of-herod.md](../../../04-knowledge/units/works/rubens-the-feast-of-herod.md) | created_by | [persons/peter-paul-rubens.md](../../../04-knowledge/units/persons/peter-paul-rubens.md) | 约1635–1638；画家；NG 2193布面油画 | [来源](https://www.nationalgalleries.org/art-and-artists/5382)；Artist、Date、Accession number |
| [works/rubens-the-feast-of-herod.md](../../../04-knowledge/units/works/rubens-the-feast-of-herod.md) | held_by | [institutions/national-gallery-of-scotland.md](../../../04-knowledge/units/institutions/national-gallery-of-scotland.md) | ；原书保管机构；原书图版35b所列保管单馆；不把当前总机构或库房粒度并入此端点 | [来源](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；lines 100–100; 章前：图版目录；印刷页xiv |
| [works/rubens-the-feast-of-herod.md](../../../04-knowledge/units/works/rubens-the-feast-of-herod.md) | located_at | [places/naples.md](../../../04-knowledge/units/places/naples.md) | 至1640年；历史到达城市；至1640年已运抵该城；未确定建筑或此后迁出时间 | [来源](https://www.nationalgalleries.org/art-and-artists/5382)；More about this artwork：2015年说明的运抵那不勒斯段 |
| [works/michelangelo-cerquozzi-the-revolt-of-masaniello.md](../../../04-knowledge/units/works/michelangelo-cerquozzi-the-revolt-of-masaniello.md) | created_by | [persons/michelangelo-cerquozzi.md](../../../04-knowledge/units/persons/michelangelo-cerquozzi.md) | 1647年底至1648年初；画家；馆藏81；创作时段采用馆方说明，目录另记1648 | [来源](https://galleriaspada.cultura.gov.it/capolavori/esplora-le-sale/sala-iv/cerquozzi-la-rivolta-di-masaniello/)；作品说明：commissionata、eseguì段 |
| [works/michelangelo-cerquozzi-the-revolt-of-masaniello.md](../../../04-knowledge/units/works/michelangelo-cerquozzi-the-revolt-of-masaniello.md) | commissioned_by | [persons/virgilio-spada.md](../../../04-knowledge/units/persons/virgilio-spada.md) | 1648；委托人；馆藏81的具体委托；年粒度依国家目录 | [来源](https://catalogo.beniculturali.it/detail/HistoricOrArtisticProperty/1200962613)；Notizie storico critiche |
| [works/michelangelo-cerquozzi-the-revolt-of-masaniello.md](../../../04-knowledge/units/works/michelangelo-cerquozzi-the-revolt-of-masaniello.md) | owned_by | [persons/virgilio-spada.md](../../../04-knowledge/units/persons/virgilio-spada.md) | ；历史收藏者；馆方明确曾属其绘画收藏，未记具体取得和转出日期 | [来源](https://galleriaspada.cultura.gov.it/capolavori/esplora-le-sale/sala-iv/cerquozzi-la-rivolta-di-masaniello/)；作品说明：collezione di pittura段 |
| [works/michelangelo-cerquozzi-the-revolt-of-masaniello.md](../../../04-knowledge/units/works/michelangelo-cerquozzi-the-revolt-of-masaniello.md) | held_by | [institutions/galleria-spada.md](../../../04-knowledge/units/institutions/galleria-spada.md) | ；保管机构；原书图版22b保管机构，区别斯帕达宫建筑 | [来源](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；lines 75–75; 章前：图版目录；印刷页xiii |
| [works/michelangelo-cerquozzi-the-revolt-of-masaniello.md](../../../04-knowledge/units/works/michelangelo-cerquozzi-the-revolt-of-masaniello.md) | installed_at | [places/palazzo-spada.md](../../../04-knowledge/units/places/palazzo-spada.md) | 2006年目录记录；目录所载展陈建筑；馆藏81在宫内第四室；仅采用2006年目录定位，不表示原定安置 | [来源](https://catalogo.beniculturali.it/detail/HistoricOrArtisticProperty/1200962613)；同源PDF第1页：LDC与LDCS Sala 4；2006更新 |
| [works/michelangelo-cerquozzi-the-revolt-of-masaniello.md](../../../04-knowledge/units/works/michelangelo-cerquozzi-the-revolt-of-masaniello.md) | located_at | [places/rome.md](../../../04-knowledge/units/places/rome.md) | 1647年底至1648年初；创作城市；馆方称画家未离开罗马完成本件；创作地点而非起义发生地 | [来源](https://galleriaspada.cultura.gov.it/capolavori/esplora-le-sale/sala-iv/cerquozzi-la-rivolta-di-masaniello/)；作品说明：senza mai allontanarsi da Roma |
| [works/bernini-caricature-of-cassiano-dal-pozzo.md](../../../04-knowledge/units/works/bernini-caricature-of-cassiano-dal-pozzo.md) | created_by | [persons/gian-lorenzo-bernini.md](../../../04-knowledge/units/persons/gian-lorenzo-bernini.md) | ；绘图者；I 135 (PK)作者归属；馆方约1680年代仍待细化，不将其作为双方会面日期 | [来源](https://www.boijmans.nl/en/collection/artworks/58489/caricature-portarit-of-cassiano-dal-pozzo)；Specifications：Artists、Accession number |
| [works/bernini-caricature-of-cassiano-dal-pozzo.md](../../../04-knowledge/units/works/bernini-caricature-of-cassiano-dal-pozzo.md) | has_subject | [persons/cassiano-dal-pozzo.md](../../../04-knowledge/units/persons/cassiano-dal-pozzo.md) | ；描绘对象；馆藏题名明确的漫画肖像人物 | [来源](https://www.boijmans.nl/en/collection/artworks/58489/caricature-portarit-of-cassiano-dal-pozzo)；Title |
| [works/bernini-caricature-of-cassiano-dal-pozzo.md](../../../04-knowledge/units/works/bernini-caricature-of-cassiano-dal-pozzo.md) | owned_by | [persons/franz-koenigs.md](../../../04-knowledge/units/persons/franz-koenigs.md) | ；历史收藏者；旧藏者身份，未载取得和转出年；不推定1940年直接赠予博物馆 | [来源](https://www.boijmans.nl/en/collection/artworks/58489/caricature-portarit-of-cassiano-dal-pozzo)；Specifications：Collector及Credits former Koenigs collection |
| [works/bernini-caricature-of-cassiano-dal-pozzo.md](../../../04-knowledge/units/works/bernini-caricature-of-cassiano-dal-pozzo.md) | held_by | [institutions/museum-boymansvan-beuningen.md](../../../04-knowledge/units/institutions/museum-boymansvan-beuningen.md) | ；保管机构；I 135 (PK)馆藏与素描版画部门记录；现列库存，非当前展陈 | [来源](https://www.boijmans.nl/en/collection/artworks/58489/caricature-portarit-of-cassiano-dal-pozzo)；Specifications：Location、Department、Accession number |
| [works/bernini-caricature-of-cassiano-dal-pozzo.md](../../../04-knowledge/units/works/bernini-caricature-of-cassiano-dal-pozzo.md) | borrowed_by | [institutions/museum-boymansvan-beuningen.md](../../../04-knowledge/units/institutions/museum-boymansvan-beuningen.md) | 1940；借入机构；本件由Stichting出借进入博物馆；非捐赠或购入 | [来源](https://www.boijmans.nl/en/collection/artworks/58489/caricature-portarit-of-cassiano-dal-pozzo)；Specifications：Credits、Acquisition date |
| [works/bernini-caricature-of-cassiano-dal-pozzo.md](../../../04-knowledge/units/works/bernini-caricature-of-cassiano-dal-pozzo.md) | lent_by | [institutions/stichting-museum-boijmans-van-beuningen.md](../../../04-knowledge/units/institutions/stichting-museum-boijmans-van-beuningen.md) | 1940；出借机构；本件1940借存的出借方；记录不单独证明基金会所有权 | [来源](https://www.boijmans.nl/en/collection/artworks/58489/caricature-portarit-of-cassiano-dal-pozzo)；Specifications：Credits Loan Stichting Museum Boijmans Van Beuningen |
| [works/carlo-dolci-sir-thomas-baines.md](../../../04-knowledge/units/works/carlo-dolci-sir-thomas-baines.md) | created_by | [persons/carlo-dolci.md](../../../04-knowledge/units/persons/carlo-dolci.md) | 约1665–1670；画家；PD.13-1972贝恩斯肖像 | [来源](https://www.museums.cam.ac.uk/magic/finch-and-baines)；The paintings’ current labels：Baines |
| [works/carlo-dolci-sir-thomas-baines.md](../../../04-knowledge/units/works/carlo-dolci-sir-thomas-baines.md) | has_subject | [persons/thomas-baines.md](../../../04-knowledge/units/persons/thomas-baines.md) | ；描绘对象；PD.13-1972题名所指人物，区别芬奇肖像PD.12-1972 | [来源](https://www.museums.cam.ac.uk/magic/finch-and-baines)；The paintings’ current labels：Sir Thomas Baines |
| [works/carlo-dolci-sir-thomas-baines.md](../../../04-knowledge/units/works/carlo-dolci-sir-thomas-baines.md) | commissioned_by | [persons/john-finch.md](../../../04-knowledge/units/persons/john-finch.md) | 驻佛罗伦萨期间；作品约1665–1670；委托人；Finch标签明确同时委托其本人及Baines肖像；本边只指PD.13-1972 | [来源](https://www.museums.cam.ac.uk/magic/finch-and-baines)；The paintings’ current labels：Finch的commissioned段 |
| [works/carlo-dolci-sir-thomas-baines.md](../../../04-knowledge/units/works/carlo-dolci-sir-thomas-baines.md) | held_by | [institutions/fitzwilliam-museum.md](../../../04-knowledge/units/institutions/fitzwilliam-museum.md) | ；保管机构；PD.13-1972，网页介绍其在馆内Gallery 3；与供片机构Royal Academy不同 | [来源](https://www.museums.cam.ac.uk/magic/finch-and-baines)；首段及Baines标签PD.13-1972 |
| [works/carlo-dolci-sir-thomas-baines.md](../../../04-knowledge/units/works/carlo-dolci-sir-thomas-baines.md) | located_at | [places/florence.md](../../../04-knowledge/units/places/florence.md) | 1665–1670；创作城市；贝恩斯肖像创作城市；不表示现藏地点 | [来源](https://www.museums.cam.ac.uk/magic/finch-and-baines)；Baines标签：This portrait was painted in Florence |
| [works/carlo-dolci-sir-thomas-baines.md](../../../04-knowledge/units/works/carlo-dolci-sir-thomas-baines.md) | acquired_by | [institutions/fitzwilliam-museum.md](../../../04-knowledge/units/institutions/fitzwilliam-museum.md) | 1972；受赠接收馆；PD.13-1972，馆方标签记1972年由National Art-Collections Fund赠入；本边仅表达接收机构 | [来源](https://www.museums.cam.ac.uk/magic/finch-and-baines)；Baines标签：Given by the National Art-Collections Fund, 1972 |
| [works/tiepolo-banquet-cognacq-jay.md](../../../04-knowledge/units/works/tiepolo-banquet-cognacq-jay.md) | created_by | [persons/giambattista-tiepolo.md](../../../04-knowledge/units/persons/giambattista-tiepolo.md) | 1742–1743；画家；J 104巴黎预备版本，区别墨尔本藏本 | [来源](https://www.parismuseescollections.paris.fr/fr/musee-cognacq-jay/oeuvres/le-banquet-de-cleopatre)；Auteur(s)、Date de production、Numéro d’inventaire |
| [works/tiepolo-banquet-cognacq-jay.md](../../../04-knowledge/units/works/tiepolo-banquet-cognacq-jay.md) | held_by | [institutions/musee-cognacq-jay.md](../../../04-knowledge/units/institutions/musee-cognacq-jay.md) | ；保管机构；J 104保管机构 | [来源](https://www.parismuseescollections.paris.fr/fr/musee-cognacq-jay/oeuvres/le-banquet-de-cleopatre)；Institution、Numéro d’inventaire |
| [works/tiepolo-banquet-cognacq-jay.md](../../../04-knowledge/units/works/tiepolo-banquet-cognacq-jay.md) | model_for | [works/tiepolo-banquet-victoria.md](../../../04-knowledge/units/works/tiepolo-banquet-victoria.md) | 1742–1743；预备版本；馆方明确称巴黎J 104为墨尔本1743–1744作品的modello及version préparatoire；非泛指全部同题作品 | [来源](https://www.parismuseescollections.paris.fr/fr/musee-cognacq-jay/oeuvres/le-banquet-de-cleopatre)；Commentaire historique |
| [works/tiepolo-banquet-cognacq-jay.md](../../../04-knowledge/units/works/tiepolo-banquet-cognacq-jay.md) | acquired_by | [institutions/musee-cognacq-jay.md](../../../04-knowledge/units/institutions/musee-cognacq-jay.md) | 1928；遗赠接收馆；J 104馆藏取得，目录记遗赠，1928；遗赠者另待必要端点核定 | [来源](https://www.parismuseescollections.paris.fr/fr/musee-cognacq-jay/oeuvres/le-banquet-de-cleopatre)；Mode d’acquisition、Date d’acquisition、Institution |
| [works/tiepolo-banquet-victoria.md](../../../04-knowledge/units/works/tiepolo-banquet-victoria.md) | created_by | [persons/giambattista-tiepolo.md](../../../04-knowledge/units/persons/giambattista-tiepolo.md) | 1743–1744；画家；103-4墨尔本藏本，区别巴黎J 104 | [来源](https://www.ngv.vic.gov.au/explore/collection/work/4409/)；题头及Accession Number |
| [works/tiepolo-banquet-victoria.md](../../../04-knowledge/units/works/tiepolo-banquet-victoria.md) | held_by | [institutions/national-gallery-of-victoria.md](../../../04-knowledge/units/institutions/national-gallery-of-victoria.md) | ；保管机构；103-4馆藏；具体馆内展室随目录时点，不作所有年代定位 | [来源](https://www.ngv.vic.gov.au/explore/collection/work/4409/)；Credit Line、Gallery location、Accession Number |
| [works/tiepolo-banquet-victoria.md](../../../04-knowledge/units/works/tiepolo-banquet-victoria.md) | acquired_by | [institutions/national-gallery-of-victoria.md](../../../04-knowledge/units/institutions/national-gallery-of-victoria.md) | 1933；取得机构；103-4于1933取得；Felton Bequest为资金／收藏来源署名，不推定Felton本人当年直接赠画 | [来源](https://www.ngv.vic.gov.au/explore/collection/work/4409/)；Credit Line及Frame：acquired by the National Gallery of Victoria in 1933 |
| [persons/viviano-codazzi.md](../../../04-knowledge/units/persons/viviano-codazzi.md) | friend_of | [persons/michelangelo-cerquozzi.md](../../../04-knowledge/units/persons/michelangelo-cerquozzi.md) | ；朋友；馆方叙述中明确amico pittore，并称其提供起义见闻；不由此认定本件具体绘制分工已无争议 | [来源](https://galleriaspada.cultura.gov.it/capolavori/esplora-le-sale/sala-iv/cerquozzi-la-rivolta-di-masaniello/)；作品说明：amico pittore Viviano Codazzi |
| [persons/john-finch.md](../../../04-knowledge/units/persons/john-finch.md) | friend_of | [persons/carlo-dolci.md](../../../04-knowledge/units/persons/carlo-dolci.md) | ；朋友；Finch馆藏标签明确befriended及到访画室；不把委托本身当友情依据 | [来源](https://www.museums.cam.ac.uk/magic/finch-and-baines)；The paintings’ current labels：Finch的befriended段 |


### 候选去向与后续依赖

- MUS-01–04、07、09–13的上述有据角色已转正；MUS-06原书单馆保管转正，1958购买主体的总机构／单馆粒度仍待单独核定，中文描述同步为购入国家收藏。MUS-05的Roomer可能委托保留待证，MUS-08的Codazzi本件绘制分工确定性冲突保留，朋友关系不消除该冲突。MUS-10的作者边不证明约1680制作年代已获解决。
- 22b图像所涉Masaniello、两件宴会的Cleopatra／Mark Antony等端点仍需具体身份核对。Paris说明另具名Lucius Plancus，主题及文本来源须独立判断；不从描绘场景推断真实亲缘、会面或恋爱事件。
- PD.12-1972芬奇肖像及其与PD.13-1972的配对有明确页面依据，需回知识元阶段成稿；National Art-Collections Fund作为1972赠入者待建或复用规范端点。J 104的Ernest Cognacq遗赠者端点亦需补齐，1928接收边不代替赠出边。以上为已发现的具体缺口，不能因本轮已有边均通过就宣称关系完整。
- NGV画框说明涉及1744支付、德累斯顿运送、约1800–1933俄罗斯收藏及1954–1955伦敦展览／修复／换框，具体支付者、作品与画框边界及流传端点另行核对。未把画框作者写成油画作者，未把本书供片关系当1954展览证据；Felton Bequest署名不等于Felton本人1933直接赠画。
- 原9项主候选继续待证，其他对齐和内容缺口继续推进；本轮未开展知识发现、页面或人工校验，未再次提交推送。

### 应用与检查

34条逐项关系裁决经exact plan预检和差异审阅后写入，连同反向入口与取得／借入标签修正共涉及39张卡。106条原书摘录、323条本地链接、来源编号及端点有效性通过，原sources前缀及旧正式关系保持；42个计划文件的应用结果与预检版本一致。首次局部检查调用传入相对路径导致工具报错，改为检查器要求的绝对路径后通过，未更改判断标准。受影响卡内容检查无确定性发现，34条新增边的方向、证据、时间、角色及范围与索引逐项一致。

索引刷新为537条（536条explicit、1条既有派生边）；886个有效KU保持。16步同步检查及274项测试通过。规则检查和系统升级链通过；网页数据未刷新。以上为语义自查与机械验证，不是独立或人工验收，也不证明全任务补足和关系阶段已完成。


## 肖像配对与遗赠主体补齐

REV-093接续；2026-09-15。本轮回送上一轮已确认的必需端点，并纠正J 104的取得主体粒度。先读来源和完成提及比较，再成稿，最后裁决关系；没有批量扩张网页外链。

### 摄入处理与身份比较

- 已读Fitzwilliam object922完整作品记录，包括Titles、作者、历史、赠入、制作、材料、书目及展览字段；image media-218826仅作为同一PD.12-1972的图像元数据交叉核对，未代替作品记录。Cambridge Museums的两作品标签和配对首段与之对应，Finch并非Baines，也不是两件共用一个实体。馆藏对象号922、PD.12-1972、尺寸及1665–1670制作年落入新作品卡。
- Art Fund官方Our purpose全文和页脚已读；其运营名与National Art Collections Fund直接对应，注册号209174／SC038331照录，未将运营名称误解为另建法人。National Gallery机构词条全文交叉核对1903成立与用途。两肖像的1972赠出责任来自Fitzwilliam及Cambridge具体记录，不由基金的一般资助使命推定。
- BnF FRBNF16168805全规范记录与Cognacq-Jay夫妻传记全文、博物馆历史全文、Paris Musées馆藏概述全文及J 104对象取得字段逐项比较。Théodore-Ernest Cognacq对应具体遗赠者Cognacq, Ernest；生卒及全名异体有规范依据。Marie-Louise Jaÿ／Jay是其妻及共同收藏者，另建人物，不把夫妻合成单一捐赠者。出生地Saint-Martin-de-Ré在BnF明确，为该采纳字段建place端点。人物父母的姓名、其他亲缘及完整生平仍未全面补足。
- Ville de Paris／City of Paris作为遗赠受益主体归institution，区别已有place巴黎。博物馆历史明确1928年Cognacq去世后市政主体继续推进项目，1929-06-04开馆。没有把现今巴黎市政法律形式或现任官员倒填到1928年。

### 新增知识元与内容

| 对象 | 类型 | 采纳内容与依据 |
|---|---|---|
| [芬奇肖像](../../../04-knowledge/units/works/carlo-dolci-sir-john-finch.md) | work | PD.12-1972；作者、描绘、委托、尺寸、制作、配对及1972赠入 |
| [国家艺术收藏基金](../../../04-knowledge/units/institutions/national-art-collections-fund.md) | institution | Art Fund运营名、1903成立、慈善注册号与两件具体赠出作品 |
| [科涅克](../../../04-knowledge/units/persons/ernest-cognacq.md) | person | 全名、惯用名、昵称、性别、生卒、出生／去世地、职业标签、配偶及具体遗赠 |
| [玛丽—路易丝·杰](../../../04-knowledge/units/persons/marie-louise-jay.md) | person | 姓名异体、生卒年、配偶、共同收藏及商业／慈善角色；不使用配偶的BnF号冒充其本人 |
| [巴黎市政当局](../../../04-knowledge/units/institutions/city-of-paris.md) | institution | 1928遗赠接收主体，区别地理城市及保管馆 |
| [圣马丹德雷](../../../04-knowledge/units/places/saint-martin-de-re.md) | place | 原语地名、地区及Cognacq出生事实；人物规范号不冒充地点规范号 |

旧卡按实际采纳补入配对、赠出方、遗赠双方及开馆日期，保留原有原书摘录与来源。六个新对象为外部补足端点，不伪造原书原句；无新增QID或Wiki验证声明，身份依据来自馆藏及规范记录。

### 正式关系与修订

| 来源KU | 关系 | 端点 | 时间／角色／范围 | 证据 |
|---|---|---|---|---|
| [works/carlo-dolci-sir-john-finch.md](../../../04-knowledge/units/works/carlo-dolci-sir-john-finch.md) | created_by | [persons/carlo-dolci.md](../../../04-knowledge/units/persons/carlo-dolci.md) | 1665–1670；画家；PD.12-1972 | [来源](https://data.fitzmuseum.cam.ac.uk/id/object/922)；Maker(s)、Dating |
| [works/carlo-dolci-sir-john-finch.md](../../../04-knowledge/units/works/carlo-dolci-sir-john-finch.md) | has_subject | [persons/john-finch.md](../../../04-knowledge/units/persons/john-finch.md) | ；描绘人物；PD.12-1972，不与贝恩斯肖像混合 | [来源](https://data.fitzmuseum.cam.ac.uk/id/object/922)；Titles、People depicted |
| [works/carlo-dolci-sir-john-finch.md](../../../04-knowledge/units/works/carlo-dolci-sir-john-finch.md) | commissioned_by | [persons/john-finch.md](../../../04-knowledge/units/persons/john-finch.md) | 驻佛罗伦萨期间；委托人；Finch委托本人和Baines肖像；本边只指本人肖像 | [来源](https://www.museums.cam.ac.uk/magic/finch-and-baines)；Finch标签：commissioned not only this portrait and that of Baines |
| [works/carlo-dolci-sir-john-finch.md](../../../04-knowledge/units/works/carlo-dolci-sir-john-finch.md) | held_by | [institutions/fitzwilliam-museum.md](../../../04-knowledge/units/institutions/fitzwilliam-museum.md) | ；保管机构；PD.12-1972保管馆 | [来源](https://data.fitzmuseum.cam.ac.uk/id/object/922)；Associated departments & institutions、Identification numbers |
| [works/carlo-dolci-sir-john-finch.md](../../../04-knowledge/units/works/carlo-dolci-sir-john-finch.md) | acquired_by | [institutions/fitzwilliam-museum.md](../../../04-knowledge/units/institutions/fitzwilliam-museum.md) | 1972；受赠接收馆；1972年赠入，区别旧藏流传及1947拍卖 | [来源](https://data.fitzmuseum.cam.ac.uk/id/object/922)；Legal notes、Acquisition and important dates |
| [works/carlo-dolci-sir-john-finch.md](../../../04-knowledge/units/works/carlo-dolci-sir-john-finch.md) | contributed_by | [institutions/national-art-collections-fund.md](../../../04-knowledge/units/institutions/national-art-collections-fund.md) | 1972；赠出机构；将PD.12-1972赠入菲茨威廉博物馆 | [来源](https://data.fitzmuseum.cam.ac.uk/id/object/922)；Legal notes、Acquisition and important dates |
| [works/carlo-dolci-sir-john-finch.md](../../../04-knowledge/units/works/carlo-dolci-sir-john-finch.md) | pendant_of | [works/carlo-dolci-sir-thomas-baines.md](../../../04-knowledge/units/works/carlo-dolci-sir-thomas-baines.md) | ；配对肖像；馆方明确两肖像成对；单侧记录，反向导航 | [来源](https://www.museums.cam.ac.uk/magic/finch-and-baines)；首段及两件作品标签 |
| [works/carlo-dolci-sir-john-finch.md](../../../04-knowledge/units/works/carlo-dolci-sir-john-finch.md) | located_at | [places/florence.md](../../../04-knowledge/units/places/florence.md) | 1665–1670；创作城市；作画城市，不表示现藏所在地 | [来源](https://data.fitzmuseum.cam.ac.uk/id/object/922)；Dating及Note：Painted in Florence |
| [works/carlo-dolci-sir-thomas-baines.md](../../../04-knowledge/units/works/carlo-dolci-sir-thomas-baines.md) | contributed_by | [institutions/national-art-collections-fund.md](../../../04-knowledge/units/institutions/national-art-collections-fund.md) | 1972；赠出机构；将PD.13-1972赠入菲茨威廉博物馆 | [来源](https://www.museums.cam.ac.uk/magic/finch-and-baines)；Baines标签：Given by the National Art-Collections Fund, 1972 |
| [works/tiepolo-banquet-cognacq-jay.md](../../../04-knowledge/units/works/tiepolo-banquet-cognacq-jay.md) | contributed_by | [persons/ernest-cognacq.md](../../../04-knowledge/units/persons/ernest-cognacq.md) | 1928；遗赠者；J 104具体遗赠者，区别夫妻共同形成收藏的总体表述 | [来源](https://www.parismuseescollections.paris.fr/fr/musee-cognacq-jay/oeuvres/le-banquet-de-cleopatre)；Nom du donateur, testateur, vendeur、Date d’acquisition |
| [persons/ernest-cognacq.md](../../../04-knowledge/units/persons/ernest-cognacq.md) | spouse_of | [persons/marie-louise-jay.md](../../../04-knowledge/units/persons/marie-louise-jay.md) | 1872结婚；配偶；馆方传记明确结婚；不据艺术收藏关系反推婚姻 | [来源](https://www.museecognacqjay.paris.fr/en/museum/cognacq-jay-spouses)；A remarkable example of commercial success：1871租约后的次年结婚 |
| [persons/ernest-cognacq.md](../../../04-knowledge/units/persons/ernest-cognacq.md) | located_at | [places/saint-martin-de-re.md](../../../04-knowledge/units/places/saint-martin-de-re.md) | 1839-10-02；出生地；人物出生地点，未写成长期活动地 | [来源](https://catalogue.bnf.fr/ark:/12148/cb161688058)；Naissance |
| [persons/ernest-cognacq.md](../../../04-knowledge/units/persons/ernest-cognacq.md) | located_at | [places/paris.md](../../../04-knowledge/units/places/paris.md) | 1928-02-21；去世地；巴黎第16区，死亡地点而非所有人生阶段居住地 | [来源](https://catalogue.bnf.fr/ark:/12148/cb161688058)；Mort |
| [institutions/city-of-paris.md](../../../04-knowledge/units/institutions/city-of-paris.md) | located_at | [places/paris.md](../../../04-knowledge/units/places/paris.md) | ；对应市政城市；遗赠行政主体对应巴黎城市；不是两个同类地理实体 | [来源](https://parismuseescollections.paris.fr/en/the-musee-cognacq-jay)；馆藏概述：City of Paris |
| [institutions/musee-cognacq-jay.md](../../../04-knowledge/units/institutions/musee-cognacq-jay.md) | supported_by | [persons/ernest-cognacq.md](../../../04-knowledge/units/persons/ernest-cognacq.md) | 1928遗赠；1929开馆；创馆收藏遗赠者；遗赠收藏成为博物馆基础，博物馆1929开馆；不记本人1929在世任职 | [来源](https://www.museecognacqjay.paris.fr/en/museum/history-museum)；The museum located Boulevard des Capucines |


J 104上一轮acquired_by→Musée Cognacq-Jay、time=1928、role=遗赠接收馆，依据当代目录的Institution和取得字段，将保管馆误作当年遗赠主体。本轮撤换这一条，改为acquired_by→City of Paris、time=1928、role=遗赠受益主体；held_by→Musée Cognacq-Jay保留。判断依据是具体J 104的Ernest Cognacq／Legs／1928取得记录，与馆史明确的遗赠受益主体共同支持。原边及前一判断保留在前节和Git差异；不将修正称为新增一条事实，也不重写原书图版所列保管馆。

### 未采纳或待补范围

Fitzwilliam所列Finch家族至1947、Hanbury拍卖、Barlow及Christie-Miller旧藏链已经读到，具体同名人物、家族及流转时间尚待核，未把这些名称自动转正。书目题名与页码仅代表馆方列书目，未读原书，不能据此建评价或独立验证。Cognacq夫妻的商业、建筑及慈善机构外链不递归接收；当前采纳的出生地、配偶及J 104遗赠端点均已建或复用，其他活动待实际问题驱动。共同形成收藏不能推出妻子也是J 104在1928年的具体遗赠者，她于1925年去世；该作品的testateur字段只署Ernest。

9项主候选及Roomer可能委托、Codazzi分工等既有待证状态保持；全任务的初步对齐、全面补足及关系定稿仍未完成。页面、知识发现、人工校验继续暂停，本轮未提交推送。

### 应用与检查

21个计划文件应用结果与预检版本一致，涉及17张知识元卡（新建6张、更新11张）；24条原书摘录、160条本地链接及来源编号核对通过。已有来源前缀保留；既有正式关系仅按上述明确纠正案替换J 104的acquired_by，其余保持。15条新增关系和1条修正关系的端点、方向、时间、角色、范围及证据与索引逐项核对，旧的博物馆取得边及反向入口均已移除，保管边仍在。

全库892条有效登记与章前522个KU计数一致，章前类型为人物215、机构79、文献18、地点90、术语4、作品112、家族3、事件1。关系索引552条（551条explicit、1条既有派生边），受影响内容检查无确定性发现，14步同步检查通过。此轮仅内容及登记变化，没有重复上一轮已经通过的274项全套代码测试；网页数据未刷新。这些检查不等于全部内容补足或全任务关系定稿。


## 研究者身份任职与序言关系集中补齐

2026-09-15继续REV-093。7名已有对象补入外部身份字段，Orna采用已校读原书的索引角色；5个必要端点回送知识元登记。固定路径和原sources保留，未新增QID或声称Wiki双向验证。

### 来源、范围与身份判断

- `persons/hugh-honour.md`：British Academy, Mr Hugh Honour FBA. https://www.thebritishacademy.ac.uk/fellows/profiles/hugh-honour-FBA/. Accessed 2026-09-15. 个人记录全部字段及机构页脚。Hugh Honour，1927–2016，艺术史家，1986年当选International Fellow。
- `persons/anthony-blunt.md`：National Portrait Gallery, Anthony Frederick Blunt, mp12247. https://www.npg.org.uk/collections/search/person/mp12247/anthony-frederick-blunt. Accessed 2026-09-15. 姓名、两段人物传记、相关人物与肖像列表；未逐件读肖像记录。全名Anthony Frederick Blunt，1907–1983，艺术史家，1947年任考陶尔德学院院长，1979年爵士荣誉被撤销。
- `persons/anthony-clark.md`：Getty Research Institute, Anthony M. Clark papers, 2023.M.59. https://www.getty.edu/research/collections/static/pdf/2023.M.59.pdf. Accessed 2026-09-15. PDF pp.3–6：传记、档案概述及接收信息；非档案原件全文。Anthony Morris Clark，1923-10-12至1976-11-22，艺术史家、画家、收藏者及博物馆工作者，研究十八世纪罗马；1973–1975年任大都会欧洲绘画策展人。
- `persons/rudolf-wittkower.md`：Columbia University Libraries, Rudolf Wittkower papers, NYCR89-A956. https://www.columbia.edu/cu/libraries/inside/projects/findingaids/scans/pdfs/48_WIEN-WIT_21.pdf. Accessed 2026-09-15. 扫描PDF第1页完整档案概述及Biography；后12页未逐项研究，原档案未读。Rudolf Wittkower，1901–1971，1956–1969年哥伦比亚大学艺术史教授；研究文艺复兴及巴洛克绘画、雕塑与建筑。
- `persons/pierre-rosenberg.md`：Académie française, Pierre Rosenberg, no.688. https://www.academie-francaise.fr/les-immortels/pierre-rosenberg. Accessed 2026-09-15. 个人荣誉字段、Biographie全文及Œuvres清单；演说与著作正文未读。Pierre Rosenberg，1936-04-13生于巴黎；1962进入卢浮宫绘画部，1994-10至2001-04-13任院长；1995-12-07当选法兰西学院第23席，1996-11-14接纳。
- `persons/marianne-roland-michel.md`：Paris Musées, Chardin / Marianne Roland Michel, record 660244. https://parismuseescollections.paris.fr/en/node/660244. Accessed 2026-09-15. 完整书目字段、责任者、版本、载体、ISBN及索书号；图书正文未读。Marianne Roland Michel，1936-02-22至2004-11-18；Chardin，Hazan，巴黎，1994，法文，292页，ISBN 2-85025-370-7。
- `persons/vitale-bloch.md`：National Gallery of Art, Dr. Vitale Bloch, provenance 22490. https://www.nga.gov/artworks/provenance/22490-dr-vitale-bloch. Accessed 2026-09-15. Provenance人物记录、所选作品与Bibliography；未逐件核作品流传。Vitale Bloch，称谓Dr.，国别标签Russian，1900–1975；记录为人物收藏流传身份入口。
- `institutions/columbia-university.md`：Columbia University, About Columbia University. https://www.columbia.edu/content/about-columbia-university. Accessed 2026-09-15. University Mission Statement两段及页面栏目；视频未观看。哥伦比亚大学是在纽约从事本科、研究生教育及科研的大学。
- `institutions/hazan.md`：Éditions Hazan, Qui sommes-nous ?. https://www.editions-hazan.fr/qui-sommes-nous/. Accessed 2026-09-15. 机构正文全部四段及页脚；未逐项读目录书籍。Hazan于1946年成立，出版艺术专著、艺术史论著及展览图录。


Clark的Anthony M.与Anthony Morris由同一Getty档案传记及接收字段衔接，并以十八世纪罗马研究与1976卒年匹配导言；1929–1976是档案日期，不作生卒。Blunt原书Sir保留历史语境，1979撤衔不改写原句。Wittkower仅采用Columbia首页身份与任职，不将档案书稿名单当已读著作。Honour书评责任复用原书脚注及既有书评卡，不重复反向事实。Rosenberg院长时期与1962入馆分开；Académie française不合并到Institut de France或美术学院。Marianne以姓名、生卒与艺术书目身份配对；Hachette作者页重定向、DDB失败不作已读来源；未将书目国别France当作者国籍。Vitale以馆方收藏流传身份配对原书旧藏者，Russian保存为馆方标签。Orna沿用PDF7的Oma校正，不凭同名信息管理文献填生平。

### 正式关系裁决

| 发出对象 | 关系 | 端点 | 范围与证据 |
|---|---|---|---|
| [persons/hugh-honour.md](../../../04-knowledge/units/persons/hugh-honour.md) | member_of | [institutions/british-academy.md](../../../04-knowledge/units/institutions/british-academy.md) | 国际院士身份；1986年当选；个人记录全部字段及机构页脚 |
| [persons/anthony-blunt.md](../../../04-knowledge/units/persons/anthony-blunt.md) | employed_by | [institutions/courtauld-institute-of-art.md](../../../04-knowledge/units/institutions/courtauld-institute-of-art.md) | 院长任命；本来源未采用离任年；1947年就任；姓名、两段人物传记、相关人物与肖像列表；未逐件读肖像记录 |
| [persons/anthony-clark.md](../../../04-knowledge/units/persons/anthony-clark.md) | employed_by | [institutions/metropolitan-museum-of-art.md](../../../04-knowledge/units/institutions/metropolitan-museum-of-art.md) | 欧洲绘画部门任职；1973–1975；PDF p.4 Biographical Note |
| [persons/rudolf-wittkower.md](../../../04-knowledge/units/persons/rudolf-wittkower.md) | employed_by | [institutions/columbia-university.md](../../../04-knowledge/units/institutions/columbia-university.md) | 艺术史教学任职；1956–1969；PDF第1页 Biography |
| [persons/pierre-rosenberg.md](../../../04-knowledge/units/persons/pierre-rosenberg.md) | employed_by | [institutions/louvre-museum.md](../../../04-knowledge/units/institutions/louvre-museum.md) | 1962进入绘画部；1994-10至2001-04-13任院长，不将院长头衔倒推至1962；1962–2001-04-13；Biographie前两段 |
| [persons/pierre-rosenberg.md](../../../04-knowledge/units/persons/pierre-rosenberg.md) | member_of | [institutions/academie-francaise.md](../../../04-knowledge/units/institutions/academie-francaise.md) | 第23席；1996-11-14接纳；1995-12-07当选；Biographie末段 |
| [persons/pierre-rosenberg.md](../../../04-knowledge/units/persons/pierre-rosenberg.md) | located_at | [places/paris.md](../../../04-knowledge/units/places/paris.md) | 出生地；1936-04-13；Biographie首句 |
| [institutions/british-academy.md](../../../04-knowledge/units/institutions/british-academy.md) | located_at | [places/london.md](../../../04-knowledge/units/places/london.md) | 机构所在地；；个人记录全部字段及机构页脚 |
| [institutions/columbia-university.md](../../../04-knowledge/units/institutions/columbia-university.md) | located_at | [places/new-york.md](../../../04-knowledge/units/places/new-york.md) | 机构所在地；；University Mission Statement两段及页面栏目；视频未观看 |
| [archives/roland-michel-chardin-1994.md](../../../04-knowledge/units/archives/roland-michel-chardin-1994.md) | authored_by | [persons/marianne-roland-michel.md](../../../04-knowledge/units/persons/marianne-roland-michel.md) | 1994年Chardin；目录责任者；1994；完整书目字段、责任者、版本、载体、ISBN及索书号；图书正文未读 |
| [archives/roland-michel-chardin-1994.md](../../../04-knowledge/units/archives/roland-michel-chardin-1994.md) | published_by | [institutions/hazan.md](../../../04-knowledge/units/institutions/hazan.md) | 1994年法文版；1994；完整书目字段、责任者、版本、载体、ISBN及索书号；图书正文未读 |
| [archives/roland-michel-chardin-1994.md](../../../04-knowledge/units/archives/roland-michel-chardin-1994.md) | located_at | [places/paris.md](../../../04-knowledge/units/places/paris.md) | 出版项Paris；不表示实体册现藏地；1994；完整书目字段、责任者、版本、载体、ISBN及索书号；图书正文未读 |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | contributed_by | [persons/anthony-blunt.md](../../../04-knowledge/units/persons/anthony-blunt.md) | 第二版序言感谢其指出书中错误；；lines 12–12; 章前：第二版序言；印刷页vi；PDF 4 |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | contributed_by | [persons/robert-enggass.md](../../../04-knowledge/units/persons/robert-enggass.md) | 第二版序言感谢其指出书中错误；；lines 12–12; 章前：第二版序言；印刷页vi；PDF 4 |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | contributed_by | [persons/howard-hibbard.md](../../../04-knowledge/units/persons/howard-hibbard.md) | 第二版序言感谢其指出书中错误；；lines 12–12; 章前：第二版序言；印刷页vi；PDF 4 |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | contributed_by | [persons/bruce-boucher.md](../../../04-knowledge/units/persons/bruce-boucher.md) | 第二版序言集体致谢书目、图版建议及其他帮助；未逐人指定具体分工；；lines 12–13; 章前：第二版序言；印刷页vi；PDF 4 |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | contributed_by | [persons/marco-chiarini.md](../../../04-knowledge/units/persons/marco-chiarini.md) | 第二版序言集体致谢书目、图版建议及其他帮助；未逐人指定具体分工；；lines 12–13; 章前：第二版序言；印刷页vi；PDF 4 |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | contributed_by | [persons/ann-sutherland-harris.md](../../../04-knowledge/units/persons/ann-sutherland-harris.md) | 第二版序言集体致谢书目、图版建议及其他帮助；未逐人指定具体分工；；lines 12–13; 章前：第二版序言；印刷页vi；PDF 4 |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | contributed_by | [persons/pierre-rosenberg.md](../../../04-knowledge/units/persons/pierre-rosenberg.md) | 第二版序言集体致谢书目、图版建议及其他帮助；未逐人指定具体分工；；lines 12–13; 章前：第二版序言；印刷页vi；PDF 4 |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | contributed_by | [persons/marianne-roland-michel.md](../../../04-knowledge/units/persons/marianne-roland-michel.md) | 第二版序言集体致谢书目、图版建议及其他帮助；未逐人指定具体分工；；lines 12–13; 章前：第二版序言；印刷页vi；PDF 4 |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | contributed_by | [persons/elizabeth-orna.md](../../../04-knowledge/units/persons/elizabeth-orna.md) | 第一版序言所述索引编制；OCR Oma按已完成PDF7校读对应Orna；；lines 22–22; 章前：第一版序言；印刷页ix；PDF 7 |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | supported_by | [persons/anthony-blunt.md](../../../04-knowledge/units/persons/anthony-blunt.md) | 第一版序言明确的研究讨论；不推定师承或共同著作；；lines 24–24; 章前：第一版序言；印刷页ix；PDF 7 |
| [works/mola-joint-caricature-of-simonelli-and-mola.md](../../../04-knowledge/units/works/mola-joint-caricature-of-simonelli-and-mola.md) | created_by | [persons/pier-francesco-mola.md](../../../04-knowledge/units/persons/pier-francesco-mola.md) | 双人漫画共同创作；未指派两人各自绘制哪一人；；lines 90–91; print p.401 |
| [works/mola-joint-caricature-of-simonelli-and-mola.md](../../../04-knowledge/units/works/mola-joint-caricature-of-simonelli-and-mola.md) | has_subject | [persons/pier-francesco-mola.md](../../../04-knowledge/units/persons/pier-francesco-mola.md) | 图版65a题名中的描绘对象；；lines 150–151; 章前：图版目录；印刷页xvi |
| [works/mola-joint-caricature-of-simonelli-and-mola.md](../../../04-knowledge/units/works/mola-joint-caricature-of-simonelli-and-mola.md) | created_by | [persons/simonelli.md](../../../04-knowledge/units/persons/simonelli.md) | 双人漫画共同创作；未指派两人各自绘制哪一人；；lines 90–91; print p.401 |
| [works/mola-joint-caricature-of-simonelli-and-mola.md](../../../04-knowledge/units/works/mola-joint-caricature-of-simonelli-and-mola.md) | has_subject | [persons/simonelli.md](../../../04-knowledge/units/persons/simonelli.md) | 图版65a题名中的描绘对象；；lines 150–151; 章前：图版目录；印刷页xvi |
| [works/mola-joint-caricature-of-simonelli-and-mola.md](../../../04-knowledge/units/works/mola-joint-caricature-of-simonelli-and-mola.md) | owned_by | [persons/vitale-bloch.md](../../../04-knowledge/units/persons/vitale-bloch.md) | 原书formerly Vitale Bloch collection；不是当前所有权；原书所记旧藏时期，具体起止未载；lines 150–151; 章前：图版目录；印刷页xvi |
| [persons/simonelli.md](../../../04-knowledge/units/persons/simonelli.md) | friend_of | [persons/pier-francesco-mola.md](../../../04-knowledge/units/persons/pier-francesco-mola.md) | 本书补记p.401称Mola为Simonelli的friend；；lines 90–91; print p.401 |


致谢按原句区分：Enggass、Hibbard、Blunt指出错误；其余五人的书目／图版／其他帮助为集体致谢，不猜个人分工。Orna初版索引不扩为所有再版索引。图版65a创作由p.401补记支持，题名支持描绘对象，旧藏由目录支持；不指定谁画谁。朋友关系取自friend明文，不由共同创作推导。

### 剩余工作

7名人物完成本轮初步外部身份核对与所列字段补足，不等于生平和作品全集完成。Clark其他任职、著述与收藏，Rosenberg书目及荣誉成员名单，Wittkower著作及教学履历仍须按本书研究需要核具体对象；未采纳背景外链不自动扩张。Orna外部身份仍待证。Chardin仅核书目；馆藏副本的保管关系与所研究的Chardin人物端点待核。9项主候选及其他版本疑点保持，章前全任务未完成；知识发现、网页和人工校验暂停，本轮未提交推送。
### 本轮写回与检查

模型逐条拟定33文件exact plan，预检旧sources与关系保留、原书引文、来源编号、本地链接及词表，生成差异后经稳定apply_patch写回。预检将误写的located_in纠正为现有词表located_at，未新增关系类型。33文件与计划一致；29张受影响卡含5张新卡，53条原书摘录、242条本地链接核对通过。受影响内容检查未报确定性缺陷；28条新增关系逐项核对端点、类型、方向、证据、角色、时间及范围，索引580条（579条explicit，1条既有派生边）。897个有效登记及527个章前KU计数通过；计数查询兼容不含sources的旧卡，不改变旧卡事实或接收状态。14步同步检查通过，未改代码或规则，不重复已通过的274项测试。业务目标仍进行中，本轮未提交推送。


## 序言协助亲缘师承与学术履历关系定稿

2026-09-15继续REV-093，集中反查正文已经采纳但尚缺正式边的事实。完整重读初、二版序言致谢段，复用卡内实际读取记录；外部复查Haskell传记pp.227–228、232、Pitt教师页全文、Hibbard成员记录、Levey传记、Waterhouse档案行政史。Cozzi、Venturi、Boucher及Torcellan沿用既有准确记录的时段和角色，不重复声称新增身份核验。

### 本轮补证与内容

- The de Laszlo Archive Trust, catalogue 2671, Peter John Ambrose Calvocoressi, KF 2016. https://docs.google.com/document/d/1XD-r_i6baE533sA46h4Q4w6vhpGSCMgX0-E6-iL_-Do/pub?embedded=true. Accessed 2026-09-15. 由作品2671实际嵌入的目录全文：生平、流传、展览、文献及注释；未读所引自传。Peter John Ambrose Calvocoressi，1912年生，2010-02-05卒；律师、国际事务研究者、出版人；1955年加入Chatto & Windus，先为合伙人后为董事。
- John Q. Barrett, Peter Calvocoressi (1912–2010), Nuremberg Prosecutor, 2010. https://thejacksonlist.com/wp-content/uploads/2014/02/20100208-Jackson-List-Calvocoressi.pdf. Accessed 2026-09-15. 两页正文及脚注全文；所引法庭记录未读。Peter John Ambrose Calvocoressi于2010-02-05去世，曾为律师，战后从事历史写作和出版。
- Phaidon, Our Company. https://www.phaidon.com/en-int/pages/our-company. Accessed 2026-09-15. 完整About Phaidon段及相关品牌概述；无下载全目录。Phaidon为创意艺术图书出版者，创办于维也纳；页面未给明确成立年份，不由one hundred years ago倒算。


Calvocoressi以档案信托作品页2671内嵌传记衔接全名、1912生年、2010卒日、律师和出版人身份；1955加入Chatto & Windus与本书出版圈相符。Barrett两页人物文支持全名、卒日及战后历史写作与出版身份。信托页面与内嵌正文不是两个独立来源；原头像作品1917及尺寸未采用，不把原页面与内嵌正文不同尺寸混合。IWM访问失败不记已读；搜索返回两个不同Wikidata候选，均未核实或写入。本轮没有Wiki双向核验。个人其他家庭、军务和出版履历尚未全面补足，不递归接收所有外链。

Phaidon由现行官网品牌性质和1977年作者书目衔接；官网相对时间不倒算成立年。文化合作研究所仅按1963年书目历史出版项登记，未合并任何同名现代机构。美国艺术与科学院采用Hibbard所属学科、1969当选及学院署名，区别此前英国国家学术院。三个端点均先登记再供本轮正式关系使用。Hibbard新内容只增加有据成员字段，不把单位名Columbia University当作特定教授任期。

### 正式关系与原文语境

| 发出对象 | 关系 | 端点 | 限定与证据 |
|---|---|---|---|
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | supported_by | [institutions/kings-college-cambridge.md](../../../04-knowledge/units/institutions/kings-college-cambridge.md) | 第一版序言my own College由同序King’s College署名落实；院长与院士未逐人具名；研究持续开展支持；；lines 22–29; 章前：第一版序言；印刷页ix；PDF 7 |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | contributed_by | [persons/g-h-w-rylands.md](../../../04-knowledge/units/persons/g-h-w-rylands.md) | 第一版序言对具体文字工作的致谢；不指后续所有版本；阅读大量打字稿、全书校样及提出订正；；lines 22–22; 章前：第一版序言；印刷页ix；PDF 7 |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | contributed_by | [persons/ellis-waterhouse.md](../../../04-knowledge/units/persons/ellis-waterhouse.md) | 第一版序言对具体文字工作的致谢；不指后续所有版本；阅读并改进打字稿；；lines 24–24; 章前：第一版序言；印刷页ix；PDF 7 |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | contributed_by | [persons/denis-mahon.md](../../../04-knowledge/units/persons/denis-mahon.md) | 第一版序言对具体文字工作的致谢；不指后续所有版本；阅读并改进打字稿；；lines 24–24; 章前：第一版序言；印刷页ix；PDF 7 |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | contributed_by | [persons/peter-calvocoressi.md](../../../04-knowledge/units/persons/peter-calvocoressi.md) | 第一版序言对具体文字工作的致谢；不指后续所有版本；阅读并改进打字稿；；lines 24–24; 章前：第一版序言；印刷页ix；PDF 7 |
| [archives/patrons-and-painters.md](../../../04-knowledge/units/archives/patrons-and-painters.md) | contributed_by | [persons/benedict-nicolson.md](../../../04-knowledge/units/persons/benedict-nicolson.md) | 第一版序言对具体文字工作的致谢；不指后续所有版本；各写作阶段文字帮助及严格意见；；lines 25–25; 章前：第一版序言；印刷页ix；PDF 7 |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | supported_by | [persons/a-n-l-munby.md](../../../04-knowledge/units/persons/a-n-l-munby.md) | 第一版序言点名致谢；不外推共同著作、任职或资助合同；解决研究问题；；lines 22–22; 章前：第一版序言；印刷页ix；PDF 7 |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | supported_by | [persons/alessandro-bettagno.md](../../../04-knowledge/units/persons/alessandro-bettagno.md) | 第一版序言点名致谢；不外推共同著作、任职或资助合同；研究讨论与帮助；；lines 23–24; 章前：第一版序言；印刷页ix；PDF 7 |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | supported_by | [persons/gianfranco-torcellan.md](../../../04-knowledge/units/persons/gianfranco-torcellan.md) | 第一版序言点名致谢；不外推共同著作、任职或资助合同；研究讨论与帮助；；lines 23–24; 章前：第一版序言；印刷页ix；PDF 7 |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | supported_by | [persons/franco-venturi.md](../../../04-knowledge/units/persons/franco-venturi.md) | 第一版序言点名致谢；不外推共同著作、任职或资助合同；研究讨论与帮助；；lines 23–24; 章前：第一版序言；印刷页ix；PDF 7 |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | supported_by | [persons/gaetano-cozzi.md](../../../04-knowledge/units/persons/gaetano-cozzi.md) | 第一版序言点名致谢；不外推共同著作、任职或资助合同；研究讨论与帮助；；lines 23–24; 章前：第一版序言；印刷页ix；PDF 7 |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | supported_by | [persons/alessandro-marabottini-marabotti.md](../../../04-knowledge/units/persons/alessandro-marabottini-marabotti.md) | 第一版序言点名致谢；不外推共同著作、任职或资助合同；陪同观看作品与多次款待；；lines 24–24; 章前：第一版序言；印刷页ix；PDF 7 |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | supported_by | [persons/michael-levey.md](../../../04-knowledge/units/persons/michael-levey.md) | 第一版序言点名致谢；不外推共同著作、任职或资助合同；启发性的研究讨论；；lines 24–24; 章前：第一版序言；印刷页ix；PDF 7 |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | influenced_by | [persons/nikolaus-pevsner.md](../../../04-knowledge/units/persons/nikolaus-pevsner.md) | 只指最初引发对艺术赞助研究的兴趣，不代替具体师承；研究兴趣启发；；lines 24–24; 章前：第一版序言；印刷页ix；PDF 7 |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | friend_of | [persons/a-n-l-munby.md](../../../04-knowledge/units/persons/a-n-l-munby.md) | 第二版序言明确very close friends，写序时两人已故；亲近朋友；1979年序言回顾；lines 14–15; 章前：第二版序言；印刷页vi；PDF 4 |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | advised_by | [persons/a-n-l-munby.md](../../../04-knowledge/units/persons/a-n-l-munby.md) | 第二版序言称写作时经常求教，不指定未载的具体建议；写作咨询；写作期间；lines 14–15; 章前：第二版序言；印刷页vi；PDF 4 |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | friend_of | [persons/benedict-nicolson.md](../../../04-knowledge/units/persons/benedict-nicolson.md) | 第二版序言明确very close friends，写序时两人已故；亲近朋友；1979年序言回顾；lines 14–15; 章前：第二版序言；印刷页vi；PDF 4 |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | advised_by | [persons/benedict-nicolson.md](../../../04-knowledge/units/persons/benedict-nicolson.md) | 第二版序言称写作时经常求教，不指定未载的具体建议；写作咨询；写作期间；lines 14–15; 章前：第二版序言；印刷页vi；PDF 4 |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | trained_by | [persons/nikolaus-pevsner.md](../../../04-knowledge/units/persons/nikolaus-pevsner.md) | 1951年为学院Fellowship论文寻求研究指导；不称为博士导师；研究指导；1951年同意指导；印刷p.228，Pevsner agreed to act as supervisor |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | spouse_of | [persons/larissa-dedicatee.md](../../../04-knowledge/units/persons/larissa-dedicatee.md) | 1965年获准结婚；不由1962相识倒推婚姻；配偶；1965年结婚；印刷p.232 |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | introduced_by | [persons/alessandro-bettagno.md](../../../04-knowledge/units/persons/alessandro-bettagno.md) | 1962年在威尼斯介绍认识Larissa Salmina；非引介进入职务；相识介绍人；1962；印刷p.232 |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | friend_of | [persons/alessandro-bettagno.md](../../../04-knowledge/units/persons/alessandro-bettagno.md) | 传记明称Francis’s friend Alessandro Bettagno；朋友；1962年相识段；印刷p.232 |
| [persons/larissa-dedicatee.md](../../../04-knowledge/units/persons/larissa-dedicatee.md) | employed_by | [institutions/hermitage-museum.md](../../../04-knowledge/units/institutions/hermitage-museum.md) | 1962年相识时职务；不推定完整任期；威尼斯素描策展人；1962年时点；印刷p.232 |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | located_at | [places/london.md](../../../04-knowledge/units/places/london.md) | 出生地；出生；1928-04-07；印刷p.227 |
| [persons/francis-haskell.md](../../../04-knowledge/units/persons/francis-haskell.md) | educated_at | [institutions/kings-college-cambridge.md](../../../04-knowledge/units/institutions/kings-college-cambridge.md) | 就读机构；不混为受雇、组织院士或个人师承；本科：前两年历史，末年英语；1948年入学；实际读取PDF2–3、7–8、10、15–17；本轮采用印刷pp.227–228、232–233、242 |
| [persons/g-h-w-rylands.md](../../../04-knowledge/units/persons/g-h-w-rylands.md) | educated_at | [institutions/kings-college-cambridge.md](../../../04-knowledge/units/institutions/kings-college-cambridge.md) | 就读机构；不混为受雇、组织院士或个人师承；入学；不表示Fellow任命；1921年入学；档案指南说明及GHWR完整条目 |
| [persons/bruce-boucher.md](../../../04-knowledge/units/persons/bruce-boucher.md) | educated_at | [institutions/courtauld-institute-of-art.md](../../../04-knowledge/units/institutions/courtauld-institute-of-art.md) | 就读机构；不混为受雇、组织院士或个人师承；硕士与博士学位教育；；完整大学任命新闻正文；可见页未显示明确发布日期 |
| [persons/ann-sutherland-harris.md](../../../04-knowledge/units/persons/ann-sutherland-harris.md) | educated_at | [institutions/courtauld-institute-of-art.md](../../../04-knowledge/units/institutions/courtauld-institute-of-art.md) | 就读机构；不混为受雇、组织院士或个人师承；博士学位教育；；完整教师页面：研究、教育、项目与出版清单；未下载CV |
| [persons/bruce-boucher.md](../../../04-knowledge/units/persons/bruce-boucher.md) | employed_by | [institutions/art-institute-of-chicago.md](../../../04-knowledge/units/institutions/art-institute-of-chicago.md) | 大学任命新闻回顾既有职务，不推定离任年；欧洲雕塑策展人；2002年起；完整大学任命新闻正文；可见页未显示明确发布日期 |
| [persons/bruce-boucher.md](../../../04-knowledge/units/persons/bruce-boucher.md) | employed_by | [institutions/sir-john-soanes-museum.md](../../../04-knowledge/units/institutions/sir-john-soanes-museum.md) | 年度报告时点，不将期末当离任；馆长；2016-05-16就任；2017-03-31仍在任；PDF第6、8、11、43页；印刷页4、6、9、41；人员、地址、机构历史与任命段 |
| [persons/ann-sutherland-harris.md](../../../04-knowledge/units/persons/ann-sutherland-harris.md) | employed_by | [institutions/university-of-pittsburgh.md](../../../04-knowledge/units/institutions/university-of-pittsburgh.md) | 校方教师页面任职身份；未补造任期；艺术史教授；；完整教师页面：研究、教育、项目与出版清单；未下载CV |
| [persons/marco-chiarini.md](../../../04-knowledge/units/persons/marco-chiarini.md) | employed_by | [institutions/galleria-palatina.md](../../../04-knowledge/units/institutions/galleria-palatina.md) | 帕拉蒂纳馆务任期；馆长；1969–2000；完整纪念文章；采用首段生卒、迁居及馆务任期 |
| [persons/michael-levey.md](../../../04-knowledge/units/persons/michael-levey.md) | employed_by | [institutions/national-gallery-london.md](../../../04-knowledge/units/institutions/national-gallery-london.md) | 1951 Assistant Keeper；1966 Deputy Keeper；1968 Keeper；1973-10至1986年底Director；助理保管员→副保管员→保管员→馆长；1951–1986年底；完整人物传记段；下方Selected acquisitions仅浏览本页索引 |
| [persons/ellis-waterhouse.md](../../../04-knowledge/units/persons/ellis-waterhouse.md) | employed_by | [institutions/national-gallery-london.md](../../../04-knowledge/units/institutions/national-gallery-london.md) | 早期馆务任职，1933离任；助理／Assistant；1929–1933；完整档案集合目录、Administrative history、Related material |
| [persons/franco-venturi.md](../../../04-knowledge/units/persons/franco-venturi.md) | employed_by | [institutions/university-of-turin.md](../../../04-knowledge/units/institutions/university-of-turin.md) | Genova1955–1958任教后转任Torino；后来荣休不扩大教席任期；近代史教席；1958年后至1984；导言与完整La vita段；后续专题段本轮未全读 |
| [persons/gaetano-cozzi.md](../../../04-knowledge/units/persons/gaetano-cozzi.md) | employed_by | [institutions/ca-foscari-university-venice.md](../../../04-knowledge/units/institutions/ca-foscari-university-venice.md) | 两个不连续任教时段；不覆盖1966–1969帕多瓦阶段；教师；1960–1965；1970–1998；PDF第54页，印刷页382，完整Fondo Gaetano Cozzi条 |
| [persons/gaetano-cozzi.md](../../../04-knowledge/units/persons/gaetano-cozzi.md) | employed_by | [institutions/university-of-padua.md](../../../04-knowledge/units/institutions/university-of-padua.md) | 仅帕多瓦任教阶段；政治科学系教师；1966–1969；PDF第54页，印刷页382，完整Fondo Gaetano Cozzi条 |
| [persons/peter-calvocoressi.md](../../../04-knowledge/units/persons/peter-calvocoressi.md) | employed_by | [institutions/chatto-and-windus.md](../../../04-knowledge/units/institutions/chatto-and-windus.md) | 出版履历；不倒推为本书文字协助的合同角色；合伙人，后任董事；1955年加入；由作品2671实际嵌入的目录全文：生平、流传、展览、文献及注释；未读所引自传 |
| [persons/howard-hibbard.md](../../../04-knowledge/units/persons/howard-hibbard.md) | member_of | [institutions/american-academy-of-arts-and-sciences.md](../../../04-knowledge/units/institutions/american-academy-of-arts-and-sciences.md) | 成员目录Elected1969；不据此指定Columbia任期；当选成员；1969；完整人物字段：姓名、生卒、机构、学科、当选年；页面更新2025-04 |
| [persons/marco-chiarini.md](../../../04-knowledge/units/persons/marco-chiarini.md) | located_at | [places/rome.md](../../../04-knowledge/units/places/rome.md) | 出生地；出生；1933-09-01；完整纪念文章；采用首段生卒、迁居及馆务任期 |
| [persons/marco-chiarini.md](../../../04-knowledge/units/persons/marco-chiarini.md) | located_at | [places/florence.md](../../../04-knowledge/units/places/florence.md) | 两个具体人生事件，不指在整个区间连续居住；迁居；去世；1964迁居；2015-11-06去世；完整纪念文章；采用首段生卒、迁居及馆务任期 |
| [persons/franco-venturi.md](../../../04-knowledge/units/persons/franco-venturi.md) | located_at | [places/rome.md](../../../04-knowledge/units/places/rome.md) | 出生地；出生；1914-05-16；导言与完整La vita段；后续专题段本轮未全读 |
| [persons/franco-venturi.md](../../../04-knowledge/units/persons/franco-venturi.md) | located_at | [places/turin.md](../../../04-knowledge/units/places/turin.md) | 去世地；去世；1994-12-14；导言与完整La vita段；后续专题段本轮未全读 |
| [persons/gaetano-cozzi.md](../../../04-knowledge/units/persons/gaetano-cozzi.md) | located_at | [places/venice.md](../../../04-knowledge/units/places/venice.md) | 去世地；去世；2001-03-15；PDF第54页，印刷页382，完整Fondo Gaetano Cozzi条 |
| [archives/harris-andrea-sacchi-1977.md](../../../04-knowledge/units/archives/harris-andrea-sacchi-1977.md) | authored_by | [persons/ann-sutherland-harris.md](../../../04-knowledge/units/persons/ann-sutherland-harris.md) | 所列版本书目责任，不声称读过全文；作者；1977；完整教师页面：研究、教育、项目与出版清单；未下载CV |
| [archives/harris-andrea-sacchi-1977.md](../../../04-knowledge/units/archives/harris-andrea-sacchi-1977.md) | has_subject | [persons/andrea-sacchi.md](../../../04-knowledge/units/persons/andrea-sacchi.md) | 书目题名及内容说明中的研究人物；研究对象；1977；完整教师页面：研究、教育、项目与出版清单；未下载CV |
| [archives/harris-andrea-sacchi-1977.md](../../../04-knowledge/units/archives/harris-andrea-sacchi-1977.md) | published_by | [institutions/phaidon.md](../../../04-knowledge/units/institutions/phaidon.md) | 所列版本出版项；出版者；1977；完整教师页面：研究、教育、项目与出版清单；未下载CV |
| [archives/harris-andrea-sacchi-1977.md](../../../04-knowledge/units/archives/harris-andrea-sacchi-1977.md) | located_at | [places/london.md](../../../04-knowledge/units/places/london.md) | 出版地点，不表示现藏实体册位置；出版地；1977；完整教师页面：研究、教育、项目与出版清单；未下载CV |
| [archives/torcellan-andrea-memmo-1963.md](../../../04-knowledge/units/archives/torcellan-andrea-memmo-1963.md) | authored_by | [persons/gianfranco-torcellan.md](../../../04-knowledge/units/persons/gianfranco-torcellan.md) | 所列版本书目责任，不声称读过全文；作者；1963；完整书目、作者规范与馆藏字段；未读书正文 |
| [archives/torcellan-andrea-memmo-1963.md](../../../04-knowledge/units/archives/torcellan-andrea-memmo-1963.md) | has_subject | [persons/andrea-memmo.md](../../../04-knowledge/units/persons/andrea-memmo.md) | 书目题名及内容说明中的研究人物；研究对象；1963；完整书目、作者规范与馆藏字段；未读书正文 |
| [archives/torcellan-andrea-memmo-1963.md](../../../04-knowledge/units/archives/torcellan-andrea-memmo-1963.md) | published_by | [institutions/istituto-per-la-collaborazione-culturale.md](../../../04-knowledge/units/institutions/istituto-per-la-collaborazione-culturale.md) | 所列版本出版项；出版者；1963；完整书目、作者规范与馆藏字段；未读书正文 |
| [archives/torcellan-andrea-memmo-1963.md](../../../04-knowledge/units/archives/torcellan-andrea-memmo-1963.md) | located_at | [places/venice.md](../../../04-knowledge/units/places/venice.md) | 出版地点，不表示现藏实体册位置；出版地；1963；完整书目、作者规范与馆藏字段；未读书正文 |
| [institutions/phaidon.md](../../../04-knowledge/units/institutions/phaidon.md) | located_at | [places/vienna.md](../../../04-knowledge/units/places/vienna.md) | 官网称在维也纳创办，未用相对时间倒算成立年；创办地；；完整About Phaidon段及相关品牌概述；无下载全目录 |


初版署名支持my own College的端点指代；不虚构院长或院士个人名单。原文讨论、文字工作、朋友和咨询分别表达：前三名审稿人与Rylands、Nicolson各保留职责，友谊由very close friends明文支持，不由致谢或共处推导。Pevsner的兴趣启发与1951年Fellowship论文指导来自不同证据，不能称博士导师。Bettagno引介限定到1962年认识Larissa，非任职引介。婚姻按1965年，反向投影不新增亲属事实。Cozzi分段任教、Levey升职与年度报告时点完整保留，均不推定连续任期。就读机构与师承、受雇分开，教育类型调整的唯一记录在06系统日志。

### 待补及范围

本轮只定稿逐条所列关系，不宣称所有序言学者内容完整。Haskell献辞、其他著作和新读到的传记旁支尚需相应证据与对象；Calvocoressi已完成本轮初步外部身份配对，其他履历及作品待有据补足。Torcellan书的复印本馆藏不能推为出版原件保管；所列书目不等于已读原件。9项主候选、Orna外部身份以及作品版本和收藏链等原待证状态保持。全任务仍进行中，未启动知识发现、网页或人工校验，未再次提交推送。
### 本轮写回与检查

53条关系由模型按上述语境逐项拟定，生成49文件exact plan及差异，经预检后稳定apply_patch写回；最终内容与计划一致。45张受影响卡含3张新卡，115条原书摘录、414条本地链接、来源序号、旧sources及旧正式关系保留检查通过；受影响内容检查无确定性发现。53条新增关系逐项核对端点、类型、方向、角色、时间、范围及证据，633条关系索引一致（632条explicit、1条既有派生边）。4条就读关系的人物发出端与机构反向展示均复核。全库900个有效登记、章前530个KU；类型为人物215、机构86、文献19、地点90、作品112、术语4、家族3、事件1。16步同步检查及274项测试通过。下一步回到尚缺外部身份依据的对象及作品版本缺口，来源URL有无仅作检索路由，不据此判定身份成败。全任务未完成，本轮未提交推送。


## 图版画家与版画家身份角色补足

2026-09-15继续REV-093。集中核对7名图版画家／版画家，逐项保留书中姓名形式、原句与页行，追加实际读取的外部身份依据。原书作品记录已逐张重读，关系并非由正文链接自动生成。

### 阅读与初步对齐

- [Camillo Semenzato, ANGELI, Giuseppe, DBI 3 (1961)](https://www.treccani.it/enciclopedia/giuseppe-angeli_(Dizionario-Biografico)/)：传记正文及书目全文；原引文献未读。威尼斯画家，可能1709年生，1798年卒据Moschini；1745年画背自称Piazzetta作坊负责人。
- [Laura Mocci, FUMIANI, Giovanni Antonio, DBI 50 (1998)](https://www.treccani.it/enciclopedia/giovanni-antonio-fumiani_(Dizionario-Biografico)/)：传记正文、注释及书目全文；原引档案未读。规范姓名Giovanni Antonio Fumiani；生年有1643、1645与1650-12-04诸说，1710年卒于威尼斯；17世纪末为费迪南多绘制《撒迦利亚被石击》。
- [National Gallery, Francesco Guardi (1712–1793)](https://www.nationalgallery.org.uk/artists/francesco-guardi)：艺术家传记全文及页面作品摘要；未逐件打开23件作品记录。Francesco Guardi，1712–1793，生于威尼斯，约1760年转向城市景观绘画。
- [Antonella Sacconi, FALDONI (Faldon), Giovanni Antonio, DBI 44 (1994)](https://www.treccani.it/enciclopedia/giovanni-antonio-faldoni_(Dizionario-Biografico)/)：传记正文及书目全文；原引档案未读。Giovanni Antonio Faldoni，1689-04-24生于Asolo，约1770年卒，卒地罗马或威尼斯；研习Mellan版画技术，Pitteri为其学生。
- [Giulio Lorenzetti, PITTERI, Marco Alvise, Enciclopedia Italiana (1935)](https://www.treccani.it/enciclopedia/marco-alvise-pitteri_(Enciclopedia-Italiana)/)：词条正文与书目全文；未读所引专著。Marco Alvise Pitteri，1702-05-24至1786-08-04，生卒均在威尼斯；刻版家，与Piazzetta合作自1740年开始。
- [Annalisa Scarpa, RICCI, Marco, DBI 87 (2016)](https://www.treccani.it/enciclopedia/marco-ricci_(Dizionario-Biografico)/)：传记正文、引文及书目全文；原引档案未读。Marco Ricci，1676-06-05生，1730-01-21卒（威尼斯历1729）；画家、舞台布景设计者、版画家和素描家，与叔父Sebastiano及Pellegrini合作。
- [Marco Gallo, FRANCESCHINI, Baldassarre detto il Volterrano, DBI 49 (1997)](https://www.treccani.it/enciclopedia/baldassarre-detto-il-volterrano-franceschini_(Dizionario-Biografico)/)：传记正文及书目全文；原引研究未读。Baldassarre Franceschini，别称il Volterrano，1611年生于Volterra；DBI记1690-01-07卒于佛罗伦萨，与在线百科1689有异。


另读Treccani的Volterrano在线百科与NGA艺术家2707页。弗兰切斯基尼的1689／1690-01-07并列，不擅自归为历法差异；Marco Ricci则有DBI明确的1730-01-21／1729 more Veneto说明，不能套用到其他人。Marco条目中的1796返威尼斯及卒年段“56岁”与所列生卒不相容，未采纳这两个值。Fumiani生年保留三种说法；Angeli生年保留probabilmente、卒年保留Moschini归属。Pitteri采用此次实际读取的Marco Alvise规范形式，保留原书Marco，不由搜索所得Giovanni Marco形式改写为已核别名。Faldoni不因学习Mellan版画而记为Mellan亲授学生。上述7人的章内身份与外部条目在姓氏、角色、地域、时代上相合；均未新增QID或宣称Wiki双向核验。

Guardi的馆方完整人物传记已读，页面23件作品仅有摘要，不称逐件馆藏记录全读。各人物辞典正文及附录书目已读，所引档案／原件未读。BM Faldoni页没有返回可识别的人物记录，故不作为证据。对其他作品的批评、争议及亲属线索只定位为后续缺口，不把人物辞典全部外链递归接收。

### 正式关系裁决

| 起点 | 类型 | 端点 | 角色、时间与证据范围 |
|---|---|---|---|
| works/giannantonio-fumiani-the-stoning-of-zechariah.md | created_by | persons/giannantonio-fumiani.md | 画家；；原书对应图版所列制作责任；原设计与刻版分别保留角色；lines 111–111; 章前：图版目录；印刷页xiv |
| works/marco-pitteri-flaminio-corner.md | created_by | persons/marco-pitteri.md | 刻版者；；原书对应图版所列制作责任；原设计与刻版分别保留角色；lines 126–126; 章前：图版目录；印刷页xv |
| works/marco-pitteri-flaminio-corner.md | created_by | persons/giuseppe-angeli.md | 原设计者；from Giuseppe Angeli；；原书对应图版所列制作责任；原设计与刻版分别保留角色；lines 126–126; 章前：图版目录；印刷页xv |
| works/gian-antonio-faldoni-zaccaria-sagredo.md | created_by | persons/gian-antonio-faldoni.md | 刻版者；；原书对应图版所列制作责任；原设计与刻版分别保留角色；lines 126–126; 章前：图版目录；印刷页xv |
| works/gian-antonio-faldoni-zaccaria-sagredo.md | created_by | persons/b-nazari.md | 原设计者；from B. Nazari；；原书对应图版所列制作责任；原设计与刻版分别保留角色；lines 126–126; 章前：图版目录；印刷页xv |
| works/marco-ricci-an-operatic-rehearsal.md | created_by | persons/marco-ricci.md | 画家；；原书对应图版所列制作责任；原设计与刻版分别保留角色；lines 125–125; 章前：图版目录；印刷页xv |
| works/marco-ricci-village-scene.md | created_by | persons/marco-ricci.md | 原设计者；；原书对应图版所列制作责任；原设计与刻版分别保留角色；lines 133–133; 章前：图版目录；印刷页xv |
| works/marco-ricci-village-scene.md | created_by | persons/bartolozzi.md | 刻印者；；原书对应图版所列制作责任；原设计与刻版分别保留角色；lines 133–133; 章前：图版目录；印刷页xv |
| works/francesco-guardi-view-of-john-strange-s-villa-at-paese-near-treviso.md | created_by | persons/francesco-guardi.md | 画家；；原书对应图版所列制作责任；原设计与刻版分别保留角色；lines 148–149; 章前：图版目录；印刷页xvi |
| works/baldassare-franceschini-la-burla-del-piovano-arlotto.md | created_by | persons/baldassare-franceschini.md | 画家；；原书对应图版所列制作责任；原设计与刻版分别保留角色；lines 105–106; 章前：图版目录；印刷页xiv |
| works/baldassare-franceschini-fame-carrying-the-name-of-louis-xiv-to-the-temple-of-immortality.md | created_by | persons/baldassare-franceschini.md | 画家；；原书对应图版所列制作责任；原设计与刻版分别保留角色；lines 154–155; 章前：图版目录；印刷页xvi |
| works/marco-pitteri-flaminio-corner.md | has_subject | persons/flaminio-corner.md | 肖像／纪念对象；；图版题名中的肖像或寓意纪念对象；不是出资或所有权证明；lines 126–126; 章前：图版目录；印刷页xv |
| works/gian-antonio-faldoni-zaccaria-sagredo.md | has_subject | persons/zaccaria-sagredo.md | 肖像／纪念对象；；图版题名中的肖像或寓意纪念对象；不是出资或所有权证明；lines 126–126; 章前：图版目录；印刷页xv |
| works/baldassare-franceschini-fame-carrying-the-name-of-louis-xiv-to-the-temple-of-immortality.md | has_subject | persons/louis-xiv.md | 肖像／纪念对象；；图版题名中的肖像或寓意纪念对象；不是出资或所有权证明；lines 154–155; 章前：图版目录；印刷页xvi |
| works/giannantonio-fumiani-the-stoning-of-zechariah.md | held_by | institutions/uffizi-gallery.md | 书中保管者；本书所述时点；原书图版目录所记收藏／保管，不宣称2026年现藏状态；lines 111–111; 章前：图版目录；印刷页xiv |
| works/gian-antonio-faldoni-zaccaria-sagredo.md | held_by | institutions/museo-correr.md | 书中保管者；本书所述时点；原书图版目录所记收藏／保管，不宣称2026年现藏状态；lines 126–126; 章前：图版目录；印刷页xv |
| works/baldassare-franceschini-la-burla-del-piovano-arlotto.md | held_by | institutions/uffizi-gallery.md | 书中保管者；本书所述时点；原书图版目录所记收藏／保管，不宣称2026年现藏状态；lines 105–106; 章前：图版目录；印刷页xiv |
| works/giannantonio-fumiani-the-stoning-of-zechariah.md | located_at | places/florence.md | 书中保管地点；本书所述时点；原书目录位置；不外推现藏或画中地点；lines 111–111; 章前：图版目录；印刷页xiv |
| works/gian-antonio-faldoni-zaccaria-sagredo.md | located_at | places/venice.md | 书中保管地点；本书所述时点；原书目录位置；不外推现藏或画中地点；lines 126–126; 章前：图版目录；印刷页xv |
| works/marco-ricci-an-operatic-rehearsal.md | located_at | places/st-asaph.md | 书中收藏地点；本书所述时点；原书目录位置；不外推现藏或画中地点；lines 125–125; 章前：图版目录；印刷页xv |
| works/francesco-guardi-view-of-john-strange-s-villa-at-paese-near-treviso.md | located_at | places/london.md | 书中私人收藏地点；本书所述时点；原书目录位置；不外推现藏或画中地点；lines 148–149; 章前：图版目录；印刷页xvi |
| works/baldassare-franceschini-la-burla-del-piovano-arlotto.md | located_at | places/florence.md | 书中保管地点；本书所述时点；原书目录位置；不外推现藏或画中地点；lines 105–106; 章前：图版目录；印刷页xiv |
| works/baldassare-franceschini-fame-carrying-the-name-of-louis-xiv-to-the-temple-of-immortality.md | located_at | places/versailles.md | 书中收藏地点；本书所述时点；原书目录位置；不外推现藏或画中地点；lines 154–155; 章前：图版目录；印刷页xvi |
| works/francesco-guardi-view-of-john-strange-s-villa-at-paese-near-treviso.md | has_subject | places/paese.md | 画中地点；；画中别墅位于Paese近Treviso；不将近邻城市写成别墅地址；lines 148–149; 章前：图版目录；印刷页xvi |
| persons/marco-pitteri.md | trained_by | persons/gian-antonio-faldoni.md | 刻版学习；；DBI明称suo allievo Marco Pitteri；不以技术相似代替师承；传记师生纠纷段：suo allievo Marco Pitteri |
| persons/gian-antonio-faldoni.md | influenced_by | persons/claude-mellan.md | 版画技术研习；；在巴黎学习Mellan的版画；Mellan早于Faldoni出生去世，不成立亲授师承；早年学习段：在巴黎研究Claude Mellan版画 |
| persons/giuseppe-angeli.md | collaborated_with | persons/piazzetta.md | 作坊负责人；1745年时点；1745年画背自述负责Piazzetta作坊，限定作坊工作；生平首段：1745年画背direttore della bottega del Piazzetta |
| persons/marco-pitteri.md | collaborated_with | persons/piazzetta.md | 设计与刻版合作；1740年起，生前合作；自1740开始的图像设计与刻版合作；Piazzetta1754去世后的复制不算在世合作；合作段：iniziatasi nel 1740及Piazzetta卒年1754 |
| persons/marco-ricci.md | kin_of | persons/sebastiano-ricci.md | 侄子→叔父；；父亲的兄弟为Sebastiano，明确叔侄而非兄弟；传记第2段：Fratello di suo padre era Sebastiano |
| persons/marco-ricci.md | collaborated_with | persons/sebastiano-ricci.md | 风景与建筑背景；18世纪初起；Marco承担风景或建筑背景；不推及叔父每一件作品；合作段：Fin dagli albori del Settecento至fondali scenografici |
| persons/marco-ricci.md | collaborated_with | persons/pellegrini.md | 绘画装饰；1709–1710；共同装饰Castle Howard，非仅同时在英国；英国行程段：A Castle Howard, tra il 1709 e il 1710 |
| persons/marco-ricci.md | located_at | places/venice.md | 返回；1715；结束英国行程后的返抵事件；非全生涯连续住址；归国段：Nel 1715 i due Ricci fecero ritorno a Venezia |
| persons/giuseppe-angeli.md | located_at | places/venice.md | 出生／去世；生年可能1709；1798卒；出生与去世均为威尼斯，生年保留可能与卒年来源归属；首段Nacque a Venezia及Morì a Venezia, secondo il Moschini, nel 1798 |
| persons/giannantonio-fumiani.md | located_at | places/venice.md | 出生／去世；生年未定；1710卒；出生和去世均为威尼斯；起首出生考证段；末段Il F. morì a Venezia nel 1710 |
| persons/francesco-guardi.md | located_at | places/venice.md | 出生；1712；出生地；人物年代与传记第2段Francesco Guardi was born in Venice |
| persons/marco-pitteri.md | located_at | places/venice.md | 出生／去世；1702-05-24出生；1786-08-04去世；生卒均在威尼斯；传记首句：nato a Venezia il 24 maggio 1702, ivi morto il 4 agosto 1786 |
| persons/marco-ricci.md | located_at | places/castle-howard.md | 装饰工作地点；1709–1710；共同绘制宅邸装饰画；不推定产权或建筑设计；英国行程段：A Castle Howard, tra il 1709 e il 1710 |
| persons/pellegrini.md | located_at | places/castle-howard.md | 装饰工作地点；1709–1710；共同绘制宅邸装饰画；不推定产权或建筑设计；英国行程段：A Castle Howard, tra il 1709 e il 1710 |


### 待证端点与版本

- Fumiani：父母Biagio／Lucrezia、妻子Caterina Bazan／Barzan及子女、教师Domenico degli Ambrogi、Scuola di S. Rocco与Cassana中介均已见辞典，但尚须建立／核对相应端点；相关事实暂未扩入正式人物字段和边。Ferdinando对《撒迦利亚被石击》的委托是有据外部候选；图版40b成稿与草稿尚需核对后再把具体委托和尺寸写入作品。检索到Zeri作品60836（目录号58108）含bozzetto及Petraia156，未据此将其尺寸、馆藏号并入本书作品，也未称已核定同一版本。原文作者、书中保管者与地点可先定稿。
- Angeli：1756学院裸体教学与1772院长、Piazzetta的作品续绘、其他具名作品须核对应机构和作品端点；作坊负责人已与Piazzetta建立有角色限定的合作，不将二者自动记为师生。
- Guardi：父Domenico与兄Gian Antonio、姐妹与Tiepolo亲缘线索需核对应人物；John Strange别墅尚未独立识别，不由画中房产推出画作委托或画作所有权。Treviso为近邻方位，未建立其为别墅地址的边。
- Faldoni：父母、Antonio Luciani师承、Asolo出生地和具体书籍版次需建／复用端点；去世地争议保留，不建确定卒地边。Pitteri的Faldoni师承可用现有端点落实，Piazzetta可能师承不提升为正式边。
- Marco Ricci：Belluno出生地、父母、其他具名作品及收藏版本仍需逐项接续；《歌剧排练》存在不同版本，不能用Yale或其他同题作品替代本书Williams-Wynn版本。书中所有者同名具体爵位仍待核，暂只定稿画家、图中明确刻印者与书中位置。
- Franceschini：Volterra出生地、Daddi／Rosselli师承、Mannozzi合作及具名赞助人需相应端点核对。图版37c的Uffizi书中记载与外部Galleria Palatina定位分开，尚不改写现藏。图版66与DBI的1664年路易十四寓意画同一性须结合馆藏号／图像确认，Strozzi委托与Colbert中介暂不写到此版本。

已采纳的Castle Howard装饰活动需要建筑端点，因此建立霍华德城堡并落实两名画家的工作地点关系；仅依据实际传记，不补造现任产权、参观信息或建筑设计者卡。

本轮保留原9项主候选与其他未决项；新增正式边不表示7人全部生平、作品或关系已补足完成。已处理记录原位更迭，过程留03，当前结果留04；知识发现、网页、人工校验和再次提交推送未执行。

### 写入与验证

38条关系、33张受影响卡（含1张新建建筑卡）已实际写入。预检核对80条原书摘录与320条本地链接，原sources前缀、既有正式关系及有效登记中的其他字段保持。exact plan核对时唯一格式差异为治理文件末尾补齐换行，实体与研究记录均与计划一致；未用该格式差异放宽内容比对。新增38条关系的端点、类型、方向、证据、角色、时间和范围与671条关系索引逐项一致。受影响卡内容机械检查未发现确定性缺陷，14步同步检查通过；本轮未改代码，不重复上一轮已通过的274项测试。全库901个有效KU，章前531个；机械通过不代表全面语义验收或全任务完成。

## 画家与收藏家姓名师承及肖像关系

2026-09-15继续REV-093原目标。5个既有主要人物逐一对齐，追加结构化内容和身份入口；6个必要关系端点新增，原路径与原书sources保留。

### 阅读、映射与裁决

- [viani](https://www.treccani.it/enciclopedia/viani/)：完整短条目，父子两代人物段。Giovanni Maria与Domenico Maria为父子兼师生；分别生于1636和1668年，卒于1700和1711年。
- [lodoli](https://www.treccani.it/enciclopedia/carlo-lodoli_(Dizionario-Biografico)/)：完整传记正文及附录书目；出生及取修会名段、教学段、末段。本名Cristoforo Ignazio Antonio，1707年取名Carlo；Algarotti和Memmo为其学生，1761年卒于帕多瓦。
- [castelli](https://www.treccani.it/enciclopedia/bernardino-castelli_(Dizionario-Biografico)/)：完整传记正文及附录书目；起首、迁居段、卒年段、Correr藏品段。1750年出生，1810年卒于威尼斯；1775年迁帕多瓦，Correr肖像与1795年复制版画分别记载。
- [verrio](https://www.hrp.org.uk/hampton-court-palace/whats-on/william-iiis-apartments/)：实际阅读正文The Grand Staircase至William III’s Private Apartments，包括图注；人物年代见The Grand Staircase。Antonio Verrio为意大利艺术家，约1636–1707；馆方记其绘制汉普顿宫国王楼梯墙画。
- [svajer](https://media.agiati.org/page/attachments/memorie-mem-06-i-buoni-ingegni-della-patria-art02-ferrari.pdf)：直接阅读PDF扫描图第1–8页＝印刷pp.51–58；完整第1节及第2节开头，含页内注释。p.51出生及德语姓名；p.52教师；p.57婚姻、职务及死亡；p.58学会会员及学名Marsio。


Viani的索引将xvii提及映射到Domenico Maria，本轮将第二版导言L179–183的原文一并登记；Waterhouse的否定迁居记载及其“畏惧竞争”解释与Haskell转述语境分开。未建立Viani位于罗马的边。Treccani父子条目可确认父亲及师承，未将父子的生卒混合。Prado完整人物摘要在搜索返回中可读，但直接条目403，本轮不计为已打开全文来源；其学院、作品与行旅线索留待后续实际页核对。

Lodoli的规范展示采用修会通用名Carlo，本名与1707取名分列；Algarotti和Memmo均有“allievi”直接根据，可建立受教关系。1720年拟设的航海教席未落实，未写任职或大学隶属；其1700年代早期罗马／Forlì时段与1715年Verona衔接不够清楚，未机械补齐时间线。

Castelli的1750–1810生卒与Correr肖像对应书中姓名和角色；1795系复制版画年份，不能填成原画年份。网页“782”“792”有截位疑点，未擅改为确定入会年份。Giustiniani赞助人不与第一章同姓侯爵合并；Conca是其教师的教师，不越级建立亲授关系。

Svajer研究PDF文本层失码，改为直接阅读扫描图pp.51–58，跨页教师死亡句、婚姻及死亡日期均按页核对。意大利姓名Svaier与德语Amadeus／Gottlieb Schweyer在p.51并列；原书Swajer保留为显示和检索入口。以罕见姓名、德裔威尼斯收藏者身份与时代做初步对应，肖像的具体馆藏号和制作年代尚未核。威尼托目录候选44731所见1724–1792标年与研究不同，但实际页面超时／服务不可用，未作为已核外部来源写入卡；研究日期暂按具体页支持，候选标年的差异保留待复查。论文第2节从p.58开始，后续p.59–85未读，不称整篇论文或所引档案全文已读。

Verrio按HRP实际页面中的姓名、年代及汉普顿宫楼梯绘画确认身份，原书作者与建筑位置可正式记录。官网楼梯《亚历山大胜过凯撒诸帝》与图版29的具体截取范围尚须图像配对，未擅改原书作品标题，未将大小寝室顶画合并为此件，也未由建筑整体委托推出本件壁画的赞助边。未新增QID，不宣称Wiki双向身份核验。

### 正式关系裁决

| 起点 | 类型 | 端点 | 角色、时间和依据 |
|---|---|---|---|
| institutions/accademia-degli-agiati.md | located_at | places/rovereto.md | 机构所在城市；18世纪语境；印刷p.58第2节；PDF第8页；研究中的学会所在城市；不推定具体建筑地址 |
| works/alessandro-longhi-carlo-lodoli.md | created_by | persons/alessandro-longhi.md | 肖像作者；；lines 126–126; 章前：图版目录；印刷页xv；原书该图版明确列出的作者 |
| works/alessandro-longhi-carlo-lodoli.md | has_subject | persons/carlo-lodoli.md | 肖像对象；；lines 126–126; 章前：图版目录；印刷页xv；原书该图版明确列出的肖像对象 |
| works/alessandro-longhi-carlo-lodoli.md | held_by | institutions/museo-correr.md | 书中保管者；本书所述时点；lines 126–126; 章前：图版目录；印刷页xv；书中图版目录记载，不以此声称已核2026年现藏 |
| works/alessandro-longhi-carlo-lodoli.md | located_at | places/venice.md | 书中保管地点；本书所述时点；lines 126–126; 章前：图版目录；印刷页xv；书中馆藏地点，不表示作品创作地点 |
| works/canova-amadeo-swajer.md | created_by | persons/canova.md | 肖像作者；；lines 137–137; 章前：图版目录；印刷页xv；原书该图版明确列出的作者 |
| works/canova-amadeo-swajer.md | has_subject | persons/amadeo-swajer.md | 肖像对象；；lines 137–137; 章前：图版目录；印刷页xv；原书该图版明确列出的肖像对象 |
| works/canova-amadeo-swajer.md | held_by | institutions/museo-correr.md | 书中保管者；本书所述时点；lines 137–137; 章前：图版目录；印刷页xv；书中图版目录记载，不以此声称已核2026年现藏 |
| works/canova-amadeo-swajer.md | located_at | places/venice.md | 书中保管地点；本书所述时点；lines 137–137; 章前：图版目录；印刷页xv；书中馆藏地点，不表示作品创作地点 |
| works/bernardino-castelli-teodoro-correr.md | created_by | persons/bernardino-castelli.md | 肖像作者；；lines 137–137; 章前：图版目录；印刷页xv；原书该图版明确列出的作者 |
| works/bernardino-castelli-teodoro-correr.md | has_subject | persons/teodoro-correr.md | 肖像对象；；lines 137–137; 章前：图版目录；印刷页xv；原书该图版明确列出的肖像对象 |
| works/bernardino-castelli-teodoro-correr.md | held_by | institutions/museo-correr.md | 书中保管者；本书所述时点；lines 137–137; 章前：图版目录；印刷页xv；书中图版目录记载，不以此声称已核2026年现藏 |
| works/bernardino-castelli-teodoro-correr.md | located_at | places/venice.md | 书中保管地点；本书所述时点；lines 137–137; 章前：图版目录；印刷页xv；书中馆藏地点，不表示作品创作地点 |
| works/antonio-verrio-fresco-on-staircase-of-hampton-court-palace.md | created_by | persons/antonio-verrio.md | 壁画作者；；lines 85–86; 章前：图版目录；印刷页xiv；图版29明确作者 |
| works/antonio-verrio-fresco-on-staircase-of-hampton-court-palace.md | located_at | places/hampton-court-palace.md | 楼梯壁画所在建筑；本书所述时点；lines 85–86; 章前：图版目录；印刷页xiv；原书题名明确建筑位置；不推定作品产权 |
| persons/domenico-maria-viani.md | kin_of | persons/giovanni-maria-viani.md | 儿子→父亲；；Domenico Maria人物段：Il figlio；父子关系，非同名合并 |
| persons/domenico-maria-viani.md | trained_by | persons/giovanni-maria-viani.md | 绘画师承；；Domenico Maria人物段：allievo del padre；传记明确随父学习，亲缘另列 |
| persons/domenico-maria-viani.md | located_at | places/bologna.md | 出生；1668；Domenico Maria生卒括注；条目明确生卒地点 |
| persons/domenico-maria-viani.md | located_at | places/pistoia.md | 去世；1711；Domenico Maria生卒括注；条目明确生卒地点 |
| persons/giovanni-maria-viani.md | located_at | places/bologna.md | 出生／去世；1636出生；1700去世；Giovanni Maria生卒括注；条目明确生卒地点 |
| persons/francesco-algarotti.md | trained_by | persons/carlo-lodoli.md | 受教者→教师；1725；教学段：nel 1725, F. Algarotti；DBI明确记为学生；不等同大学学位 |
| persons/andrea-memmo.md | trained_by | persons/carlo-lodoli.md | 受教者→教师；；著述段：due allievi，Algarotti与A. Memmo；DBI明确记为学生；不等同大学学位 |
| persons/carlo-lodoli.md | located_at | places/venice.md | 出生／返回；1690出生；1720返回；起首出生段及1720返威尼斯段；明确生平地点事件，非全生涯连续住址 |
| persons/carlo-lodoli.md | located_at | places/padua.md | 去世；1761-10-27；末段Morì a Padova；明确生平地点事件，非全生涯连续住址 |
| persons/bernardino-castelli.md | located_at | places/padua.md | 迁居；1775；1775年转往Padova段；传记明确地点事件 |
| persons/bernardino-castelli.md | located_at | places/venice.md | 去世；1810-02-24；Morì a Venezia段；传记明确地点事件 |
| persons/amadeo-swajer.md | trained_by | persons/johann-conrad-hofmann.md | 家庭教育；；印刷p.52教师段；PDF第2页；家庭教师身份明确，不外推大学学历 |
| persons/amadeo-swajer.md | kin_of | persons/katharina-heinzelmann.md | 丈夫→妻子；1760年4月底结婚；印刷p.57首段；PDF第7页；婚姻开始日期明确，未推定配偶生卒或婚姻结束日期 |
| persons/amadeo-swajer.md | member_of | institutions/accademia-degli-agiati.md | 学会会员；1752年加入；印刷p.58第2节首段；PDF第8页；学会吸收为会员，学名Marsio；不推定终止年份 |
| persons/amadeo-swajer.md | located_at | places/venice.md | 出生／去世；1727-12-12出生；1791-12-28去世；印刷p.51末段及p.57首段；PDF第1、7页；出生与去世地点均为威尼斯 |
| persons/johann-conrad-hofmann.md | located_at | places/padua.md | 去世；1756-03-15；印刷pp.52–53跨页句；PDF第2–3页；跨页句明确在帕多瓦去世 |


### 剩余具体缺口

- Viani：Cignani教师的全名端点、父亲的其他师承、具体作品及所在教堂／馆藏待核，不以一个传记链接代替作品版本审查。
- Lodoli：父Bernardo、母Anna Maria Alberghetti、Muazzo教师、修会与出版监管机构、具名著作及其后世出版版本仍须相应端点；不得把他生前未刊的建筑论著与Algarotti／Memmo的著作混记为本人出版物。
- Castelli：Arsié出生地、父母Francesco／Maria Elisabetta Forcellini、Giovanni d’Antonio师承、Giustiniani赞助，以及其他肖像作品须各自核端点和版本；这些线索未当成已正式采纳的关系。
- Svajer：父母与兄弟、商业企业／领事主体、藏书流转和本人著述版本待接续；此次只补入直接需要的教师、配偶及学会。没有从同一收藏者推出所有著作的所有权；目录购买与捐赠性质需实际保管机构记录核对。
- Verrio：出生地、早年教师与其他宫殿项目尚未全面补足；图版29与官网具体题名及图像范围的对应、实际委托人与时间仍待核。

本轮保留原9项主候选及其他具体未决项；既有成果原位更迭，过程留03，当前结果留04。知识发现、页面与人工校验暂停；本轮不提交或推送。

### 写入与验证

31条关系及25张受影响知识元卡（含6张新卡）已写入。预检核对44条原书摘录、224条本地链接，既有来源与正式关系保持；29个计划文件的内容核对完成，唯一格式差异为apply_patch去掉03过程文档末尾的一个空行，实体内容完全一致。全库907个有效KU，章前537个；31条新增关系的端点、类型、证据、角色、时间与范围逐项匹配702条关系索引。14步同步检查通过，未改代码，不重复全套测试；未刷新页面。以上为本批直接语义核对与机械检查，不表示独立验收或章前任务整体完成。

## 机构身份与书目版本责任集中补足

2026-09-15继续REV-093原目标；本轮发生在REV-108已同步提交b9d2f45之后。本轮内部接续不新增用户原话。

### 实际阅读与身份映射

- [cap](https://www.museicapitolini.org/it/percorsi/pinacoteca-capitolina)：完整馆藏部门介绍正文及所在楼层说明；不含链接的各展室详情。绘画馆于1748–1750年形成，绘画藏品陈列于Palazzo dei Conservatori二楼。
- [stuttgart](https://www.stuttgart.de/tourismus/sehenswuerdigkeiten/staatsgalerie)：德语页面正文、图注与地址字段；页面标注2021-02-18。美术馆1843年开放，位于斯图加特，收藏范围由14世纪延续至今。
- [wallraf](https://www.wallraf.museum/en/the-museum/history/)：完整沿革正文各小节；采用1861开放及2001更名节点。1861年7月1日开放；2001年采用Wallraf-Richartz-Museum & Fondation Corboud名称。
- [wallraf-contact](https://www.wallraf.museum/en/the-museum/contact/contact/)：完整联系页机构名称与地址字段。博物馆位于科隆Obenmarspforten，邻近市政厅。
- [pastor](https://archive.org/download/historyofpopesfr33past/historyofpopesfr33past.pdf)：直接查看题名页扫描（PDF第7页）和印刷pp.13–14（PDF第53–54页）；只读所引页及邻页，未读全卷。题名页确认原作者、译者、卷次、出版地及1941年；p.13起首为本书转引克勉十一世不徇私亲的评价。
- [montaiglon](https://archive.org/download/correspondancede03acad/correspondancede03acad_bw.pdf)：直接查看题名页（PDF第9页）、第1317号信完整扫描印刷pp.239–241（PDF第249–251页）；不将相邻第1318、1319号信纳入本信。第三卷覆盖1699–1711，出版于1889年12月；第1317号Poerson致M. d’Antin信日期为1708年10月20日，引文在p.240，p.241署Poerson并列Archives nationales, O¹ 1953。
- [antin](https://www.chateauversailles-recherche.fr/corpus/article533.html)：完整目录引介、作者名、图注、版本说明及目录；未读取所链回忆录原文。作者完整姓名Louis-Antoine de Pardaillan de Gondrin de Montespan，1665–1736；目录列1708年获得建筑总监部门领导职务、1711年获得公爵爵位。
- [met](https://www.metmuseum.org/art/collection/search/344493)：完整Artwork Details：责任者、出版地、年份、媒介与具体印本字段；未读全书。Girolamo Teti著，Mascardi于罗马出版，1642；48.106.2及尺寸属于大都会所藏印本。
- [lmu](https://epub.ub.uni-muenchen.de/12211/)：完整目录记录、题名、出版项、语言、索书号、URN及印本流传说明；未读400MB全文。作者拉丁名Hieronymus Tetius，罗马Mascardus出版，1642，拉丁语；Cim.36 (=2 Art.277)为该馆印本索书号。


### 判断变化与版本边界

三家美术馆的名称、地址及沿革取得机构自身或市政府根据。卡比托利欧绘画馆属于Musei Capitolini，陈列于保守宫二楼；不把部门、总馆和建筑合并。斯图加特和科隆的作品卡已有外部保管边，本轮保持；补足机构身份不重新认领作品“现藏”验证。科隆官网旧展室链接跳转到中世纪展厅，不能据搜索摘要判断Piazzetta作品身份。三件卡比托利欧图版新增书内创作、历史保管与罗马位置边；Bottalla已采纳的Sacchetti家族委托按既有传记证据补边，不外推另一版本。

帕斯托第三十三卷题名页为1941年，而IA聚合目录日期1891为系列层面的元数据，未用于单卷。题名页的Ludwig, Freiherr von Pastor与书后意大利形式Ludovico Barone von Pastor按相同著作系列、作者姓氏和贵族称号对应；姓名形式分列，不把译者Graf与意译者Cenci合并。扫描p.13起首与哈斯克尔所引评价一致；这是作者的教皇史论断，不据此替克勉十一世添加“绝无裙带任用”的无条件属性。题名页与所引邻页可核，不声称全卷阅读。译者以contributed_by加role=译者表达，不混成原作者。

《通信集》第三卷题名页为1889年12月，覆盖1699–1711；此前系列1887–1912保持。实际阅读第1317号信从p.239题头到p.241署名，写信日期1708-10-20；邻接第1318号信所说9月28日是另一封信，不误套到本信。收信人M. d’Antin据题头、1708年职务背景和凡尔赛研究中心全名记录对应Louis-Antoine；1711才获公爵爵位，因此信件标题不冠以1708年尚未取得的公爵称号。旧authored_by边保留原书来源及1708时间，只替换过时的“收信人未明”scope，前后值保存在corrections计划及本段。新增收信人、通信及编刊收录边；书信收录关系不冒充手稿保管关系。p.241的Archives nationales, O¹ 1953为刊本所报档号，未访问手稿原件。Guiffrey只按INHA的系列编者记录建边，不说第三卷题名页署其名。

《巴贝里尼宫》1642罗马版同时得到Met与LMU具体印本目录支持，Girolamo Teti与Hieronymus Tetius按同题同年书目责任对齐。48.106.2与Cim.36是不同馆藏印本的标识，分别标注；未把两馆的尺寸、装帧、来源或收藏地写成本书图版9所用印本事实。原书剑桥大学图书馆供片边保留；供片不自动证明保管。Mascardi/Mascardus作为该版所列出版机构建必要端点，未未经证明指认为Vitale个人。另见Soane目录1647年版线索，不覆盖1642卡；其他刻版者仅在目录中笼统署若干图版，不能推定卷首图刻制者。全书未读，不声称各图版职责已补齐。

### 正式关系裁决

| 起点 | 类型 | 端点 | 角色、时间和证据范围 |
|---|---|---|---|
| institutions/pinacoteca-capitolina.md | part_of | institutions/capitoline-museums.md | 绘画收藏部门；；完整馆藏部门介绍正文及所在楼层说明；不含链接的各展室详情；馆方现行收藏部门；不同于建筑空间 |
| institutions/pinacoteca-capitolina.md | located_at | places/palazzo-dei-conservatori.md | 陈列场所：二楼；页面访问2026-09-15；完整馆藏部门介绍正文及所在楼层说明；不含链接的各展室详情；馆方页面所述绘画收藏陈列位置 |
| institutions/staatsgalerie-stuttgart.md | located_at | places/stuttgart.md | 机构所在城市；页面访问2026-09-15；德语页面正文、图注与地址字段；页面标注2021-02-18；市政府机构地址；不等于作品创作地点 |
| institutions/wallraf-richartz-museum.md | located_at | places/cologne.md | 机构所在城市；页面访问2026-09-15；完整联系页机构名称与地址字段；馆方联系地址；不以此说明作品产权 |
| works/pietro-da-cortona-rape-of-the-sabines.md | created_by | persons/pietro-da-cortona.md | 图版作品作者；；lines 51–51; 章前：图版目录；印刷页xii；图版目录明确署名；不推断另版本 |
| works/pietro-da-cortona-rape-of-the-sabines.md | held_by | institutions/pinacoteca-capitolina.md | 书中保管者；本书所述时点；lines 51–51; 章前：图版目录；印刷页xii；原书图版目录记载的保管机构；不等于核实当前产权 |
| works/pietro-da-cortona-rape-of-the-sabines.md | located_at | places/rome.md | 书中位置；本书所述时点；lines 51–51; 章前：图版目录；印刷页xii；书中明确的保管城市，不是作品创作地 |
| works/gio-maria-bottalla-meeting-of-esau-and-jacob.md | created_by | persons/gio-maria-bottalla.md | 图版作品作者；；lines 54–55; 章前：图版目录；印刷页xii；图版目录明确署名；不推断另版本 |
| works/gio-maria-bottalla-meeting-of-esau-and-jacob.md | held_by | institutions/pinacoteca-capitolina.md | 书中保管者；本书所述时点；lines 54–55; 章前：图版目录；印刷页xii；原书图版目录记载的保管机构；不等于核实当前产权 |
| works/gio-maria-bottalla-meeting-of-esau-and-jacob.md | located_at | places/rome.md | 书中位置；本书所述时点；lines 54–55; 章前：图版目录；印刷页xii；书中明确的保管城市，不是作品创作地 |
| works/pietro-testa-joseph-sold-by-his-brothers.md | created_by | persons/pietro-testa.md | 图版作品作者；；lines 56–56; 章前：图版目录；印刷页xii；图版目录明确署名；不推断另版本 |
| works/pietro-testa-joseph-sold-by-his-brothers.md | held_by | institutions/pinacoteca-capitolina.md | 书中保管者；本书所述时点；lines 56–56; 章前：图版目录；印刷页xii；原书图版目录记载的保管机构；不等于核实当前产权 |
| works/pietro-testa-joseph-sold-by-his-brothers.md | located_at | places/rome.md | 书中位置；本书所述时点；lines 56–56; 章前：图版目录；印刷页xii；书中明确的保管城市，不是作品创作地 |
| works/gio-maria-bottalla-meeting-of-esau-and-jacob.md | commissioned_by | families/sacchetti-family.md | 家族集体委托；；Bottalla传记：Incontro di Esaù con Giacobbe、galleria Sacchetti段；人物辞典明确为Sacchetti家族画廊制作；与Barberini继承人版本区分 |
| archives/pastor-popes-english-vol33.md | authored_by | persons/pastor-historian.md | 原作者；；题名页；PDF第7页；题名页原作者；英文译者另列 |
| archives/pastor-popes-english-vol33.md | contributed_by | persons/ernest-graf.md | 译者；1941出版；题名页TRANSLATED BY；PDF第7页；英文第三十三卷题名页明确的翻译责任 |
| archives/pastor-popes-english-vol33.md | published_by | institutions/kegan-paul-trench-trubner.md | 出版商；1941；题名页出版项；PDF第7页；本次核对的英文第三十三卷版本 |
| archives/pastor-popes-english-vol33.md | located_at | places/london.md | 出版地；1941；题名页出版项；PDF第7页；版本出版地点，不是现存印本保管地 |
| archives/pastor-popes-english-vol33.md | has_subject | persons/clement-xi.md | 传记对象；论述1700–1721；题名页CLEMENT XI；印刷p.13；卷题明确的教皇；书中评价不转写为现代研究定论 |
| archives/poerson-letter-1708.md | addressed_to | persons/louis-antoine-de-pardaillan-de-gondrin.md | 收信人；1708-10-20；印刷p.239第1317号信题头；PDF第249页；刊本第1317号信题头M. d’Antin；身份依收信人人物卡来源 |
| archives/poerson-letter-1708.md | part_of | archives/montaiglon-academy-correspondence.md | 刊载于第三卷pp.239–241；1889年12月刊行；题名页和印刷pp.239–241；第1317号；信件的编刊收录位置，非手稿物理归属 |
| persons/charles-francois-poerson.md | corresponded_with | persons/louis-antoine-de-pardaillan-de-gondrin.md | 写信人→收信人；1708-10-20；第1317号信题头、日期及署名；印刷pp.239、241；此信支持一次通信，不自动证明朋友或赞助关系 |
| archives/montaiglon-academy-correspondence.md | compiled_by | persons/a-de-montaiglon.md | 第三卷编者；1889年12月；第三卷题名页；PDF第9页；第三卷题名页署名；不将本卷署名扩大为各卷唯一责任 |
| archives/montaiglon-academy-correspondence.md | compiled_by | persons/jules-guiffrey.md | 系列共同编者；系列1887–1912；INHA人物记录书目：Correspondance des directeurs，Montaiglon et Guiffrey；INHA所列18卷系列的共同编者，不声称第三卷题名页列其名 |
| archives/montaiglon-academy-correspondence.md | published_by | institutions/charavay-freres.md | 第三卷出版商；1889年12月；第三卷题名页；PDF第9页；仅核第三卷题名页所列出版商，不覆盖全部18卷 |
| archives/montaiglon-academy-correspondence.md | located_at | places/paris.md | 第三卷出版地；1889年12月；第三卷题名页；PDF第9页；第三卷版本的出版地，不是手稿所在地 |
| archives/aedes-barberinae-ad-quirinalem.md | authored_by | persons/girolamo-teti.md | 文字作者；1642出版；Artwork Details：Author、Date；馆方明确的文字作者，不是全书插图刻版者 |
| archives/aedes-barberinae-ad-quirinalem.md | published_by | institutions/mascardi-rome.md | 出版机构；1642；Artwork Details：Publisher、Published in、Date；1642年罗马版出版项；不把机构名称扩写成特定自然人 |
| archives/aedes-barberinae-ad-quirinalem.md | located_at | places/rome.md | 出版地点；1642；Artwork Details：Published in、Date；出版地，非印本保管地 |
| works/guido-abbatini-frontispiece-of-aedes-barberinae-ad-quirinalem.md | part_of | archives/aedes-barberinae-ad-quirinalem.md | 卷首图；1642；lines 49–50; 章前：图版目录；印刷页xii；原书图版明确的卷首图与1642载体；未核剑桥具体印本号 |
| works/guido-abbatini-frontispiece-of-aedes-barberinae-ad-quirinalem.md | created_by | persons/guido-abbatini.md | 图版署名作者；；lines 49–50; 章前：图版目录；印刷页xii；原书图版作者署名；不细分未核的设计与刻制职责 |
| works/guido-abbatini-frontispiece-of-aedes-barberinae-ad-quirinalem.md | has_subject | places/palazzo-barberini.md | 描绘建筑；；lines 49–50; 章前：图版目录；印刷页xii；题名明确with view of Palazzo Barberini |
| institutions/kegan-paul-trench-trubner.md | located_at | places/london.md | 出版活动地；1941；题名页出版项；PDF第7页；题名页所示该出版商的出版活动地点 |
| institutions/charavay-freres.md | located_at | places/paris.md | 书商地址所在城市；1889年12月；第三卷题名页；PDF第9页；题名页出版商地址4, rue de Furstenberg |
| institutions/mascardi-rome.md | located_at | places/rome.md | 出版活动地；1642；Artwork Details：Publisher、Published in、Date；1642版出版项所载出版活动地点，不推定全时段地址 |


### 剩余工作与交接

9项主候选继续待证。Kunstsammlungen Kassel的历史机构边界、罗马市政美术办公室的具体建制仍需核；威尼斯共和国已有文化部沿革线索，本轮未写入。Honour评论的精确题名与页码、Waterhouse文章页码异文及可读全文、图版9剑桥具体印本与卷首图刻制职责仍待证。帕斯托其他译本和Graf个人生平未全面补足，不把题名页核验扩大为人物全传。D’Antin回忆录目录仅用于所需身份，不自动摄入其中的各个人名和作品。新建5个直接责任端点，无新增文献卡；现有文献原路径更迭。整体对齐、全面内容补足和关系定稿尚未完成；不启动发现、页面或人工校验，本轮不自动提交推送。

### 写入与验证

39个计划文件已按差异写入，其中35张受影响知识元卡、5张新卡；预检核对78条原书摘录、281条本地链接及来源保留。35条新增关系的端点、类型、证据、时间、角色与范围逐项匹配737条关系索引；旧信件作者边只更新已记录的scope。全库912个有效KU、章前542个，类型为人物220、机构90、文献19、地点93、作品112、术语4、家族3、事件1。14步同步检查通过；没有代码改动，不重复全套测试。末次语义复核将收信人卡中的“接收”改为“信的署期”，避免将写信日期误说为实际收信日期；该句不改变正式边。未刷新页面，未提交推送。上述为本批语义自查与机械核对，不是独立验收或整体完成。

扫描证据指纹（下载文件的SHA-256，页码对应见上述来源阅读范围）：Pastor PDF为`3439aace1ab7be1a2d93cc66ac992749fea5e52be983f404266c6cc9c3679cbd`；Montaiglon灰度PDF为`89cf4fe2e42e8c1e8f72caa2765676e59c69a1fd9006539798106632e0e0fd3c`。引用使用已记录的稳定下载地址，临时阅读缓存不是新增来源版本。
