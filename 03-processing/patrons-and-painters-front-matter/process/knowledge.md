# 章前材料：知识元登记与对齐过程

task-id：`patrons-and-painters-front-matter`；REV-085–086。前置输入为[摄入与处理定稿](../results/stages.md)及[实体候选](../results/entity-candidates.md)。前半部分保留REV-085登记判断与写回历史；候选映射维护当前去向。REV-086的外部核对、改变判断的依据及剩余问题见[初步对齐](#初步对齐rev-086)。

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
| FM-E055 | 暂缓 | 索引Gregorio Lazzarini条未列xvii；仅姓氏不足以完成该段同一性判断。 |
| FM-E056 | 新建 | [塞巴斯蒂亚诺·孔卡（Sebastiano Conca）](../../../04-knowledge/units/persons/sebastiano-conca.md) |
| FM-E057 | 原位整理后接收 | [朱塞佩·马里亚·克雷斯皮（Giuseppe Maria Crespi）](../../../04-knowledge/units/persons/giuseppe-maria-crespi.md) |
| FM-E058 | 新建 | [索利梅纳（Solimena）](../../../04-knowledge/units/persons/solimena.md) |
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
| FM-H01 | 暂缓 | 署名的个人／商号／复合代理或机构具体身份未定，保留原供片编号，不据摄影署名猜法人或合并现有机构。 |
| FM-H02 | 暂缓 | 署名的个人／商号／复合代理或机构具体身份未定，保留原供片编号，不据摄影署名猜法人或合并现有机构。 |
| FM-H03 | 暂缓 | 署名的个人／商号／复合代理或机构具体身份未定，保留原供片编号，不据摄影署名猜法人或合并现有机构。 |
| FM-H04 | 暂缓 | 署名的个人／商号／复合代理或机构具体身份未定，保留原供片编号，不据摄影署名猜法人或合并现有机构。 |
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
| FM-H24 | 暂缓 | 署名的个人／商号／复合代理或机构具体身份未定，保留原供片编号，不据摄影署名猜法人或合并现有机构。 |
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
| FM-P20.creator1 | 新建 | [委拉斯开兹（Velasquez）](../../../04-knowledge/units/persons/velasquez.md) |
| FM-P20.holder1 | 新建 | [拉尔夫·班克斯（Ralph Bankes）](../../../04-knowledge/units/persons/ralph-bankes.md) |
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
| FM-P30a.holder1 | 新建 | [拉尔夫·班克斯（Ralph Bankes）](../../../04-knowledge/units/persons/ralph-bankes.md) |
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
| FM-P31b.holder1 | 新建 | [盖尔斯·伊舍姆（Gyles Isham）](../../../04-knowledge/units/persons/gyles-isham.md) |
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
| FM-P33a.creator1 | 新建 | [索利梅纳（Solimena）](../../../04-knowledge/units/persons/solimena.md) |
| FM-P33a.former_site1 | 新建 | [布奥纳科尔西宫（Palazzo Buonaccorsi）](../../../04-knowledge/units/places/palazzo-buonaccorsi.md) |
| FM-P33a.former_site2 | 新建 | [马切拉塔（Macerata）](../../../04-knowledge/units/places/macerata.md) |
| FM-P33a.object | 新建 | [狄多与埃涅阿斯（Dido and Aeneas）](../../../04-knowledge/units/works/solimena-dido-and-aeneas.md) |
| FM-P33b.object | 新建 | [布奥纳科尔西宫画廊（Gallery of Palazzo Buonaccorsi）](../../../04-knowledge/units/places/gallery-palazzo-buonaccorsi.md) |
| FM-P33b.part1 | 新建 | [布奥纳科尔西宫（Palazzo Buonaccorsi）](../../../04-knowledge/units/places/palazzo-buonaccorsi.md) |
| FM-P33b.site1 | 新建 | [马切拉塔（Macerata）](../../../04-knowledge/units/places/macerata.md) |
| FM-P34.creator1 | 新建 | [委拉斯开兹（Velasquez）](../../../04-knowledge/units/persons/velasquez.md) |
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
| FM-P42a.creator1 | 暂缓 | 仅Tiepolo姓氏；按本件作品核对父子及归属后再映射。 |
| FM-P42a.object | 新建 | [海神向威尼斯致敬（Neptune paying homage to Venice）](../../../04-knowledge/units/works/tiepolo-neptune-paying-homage-to-venice.md) |
| FM-P42a.site1 | 新建 | [总督宫（威尼斯）（Palazzo Ducale）](../../../04-knowledge/units/places/palazzo-ducale.md) |
| FM-P42a.site2 | 复用并更新 | [威尼斯（Venice）](../../../04-knowledge/units/places/venice.md) |
| FM-P42b.creator1 | 新建 | [尼科洛·班比尼（Niccolo Bambini）](../../../04-knowledge/units/persons/niccolo-bambini.md) |
| FM-P42b.object | 新建 | [威尼斯寓意（Allegory of Venice）](../../../04-knowledge/units/works/niccolo-bambini-allegory-of-venice.md) |
| FM-P42b.site1 | 新建 | [佩萨罗宫（Ca' Pesaro）](../../../04-knowledge/units/places/ca-pesaro.md) |
| FM-P42b.site2 | 复用并更新 | [威尼斯（Venice）](../../../04-knowledge/units/places/venice.md) |
| FM-P43.creator1 | 暂缓 | 仅Tiepolo姓氏；按本件作品核对父子及归属后再映射。 |
| FM-P43.family1 | 新建 | [雷佐尼科家族（Rezzonico family）](../../../04-knowledge/units/families/rezzonico-family.md) |
| FM-P43.object | 新建 | [雷佐尼科家族婚姻寓意（Marriage Allegory of the Rezzonico family）](../../../04-knowledge/units/works/tiepolo-marriage-allegory-of-the-rezzonico-family.md) |
| FM-P43.site1 | 新建 | [雷佐尼科宫（Ca' Rezzonico）](../../../04-knowledge/units/places/ca-rezzonico.md) |
| FM-P43.site2 | 复用并更新 | [威尼斯（Venice）](../../../04-knowledge/units/places/venice.md) |
| FM-P44.creator1 | 暂缓 | 仅Tiepolo姓氏；按本件作品核对父子及归属后再映射。 |
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
| FM-P50.creator1 | 暂缓 | 仅Tiepolo姓氏；按本件作品核对父子及归属后再映射。 |
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
| FM-P57a.self1 | 新建 | [皮亚泽塔（Piazzetta）](../../../04-knowledge/units/persons/piazzetta.md) |
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
| FM-P58a.subject1 | 新建 | [老A. M. 扎内蒂（A. M. Zanetti the Elder）](../../../04-knowledge/units/persons/a-m-zanetti-the-elder.md) |
| FM-P58a.subject2 | 新建 | [杰里尼侯爵（Marchese Gerini）](../../../04-knowledge/units/persons/marchese-gerini.md) |
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
| FM-P68b.creator1 | 暂缓 | 仅Tiepolo姓氏；按本件作品核对父子及归属后再映射。 |
| FM-P68b.creator2 | 新建 | [莱奥纳迪斯（Leonardis）](../../../04-knowledge/units/persons/leonardis.md) |
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

### 仍暂缓的14条主候选

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
