# 按类型选择核对内容与补足来源

本参考从属于verify/SKILL.md。对齐按实体类型选择能识别同一对象、版本或记录粒度的来源，不另设固定搜索级数或审批。标识符只在适用时采用；同名、数据库聚合或相互链接仍须符合来源语境。Wikipedia与Wikidata有准确同粒度对象时核对双向链接，没有QID不构成实体缺陷。

| 类型 | 关键身份边界与核对内容 | 按缺口选用的补足来源 |
|---|---|---|
| person | 原名／别名、生卒年代、职业、活动地点、交往对象；同姓和头衔不足以合并 | 国家人物辞典与传记工具，如Treccani《意大利人传记辞典》；SIUSA人物档案生产者记录；Getty ULAN、VIAF／ISNI、SBN及国家图书馆规范记录、博物馆与所属机构记录 |
| family | 家族与支系、原语名称、地域和时代、可核成员；排除姓氏页、个人、家户及同名不同族 | SIUSA及档案馆家族／档案生产者记录、图书馆家族规范记录、博物馆收藏沿革及有出处的谱系研究；成员和联姻逐项核对 |
| institution | 机构或政治实体名称、存续年代、职能及继承变化；共和国与同名城市分开 | 机构官网、法规或官方沿革、SIUSA机构档案生产者记录、档案馆与图书馆规范记录；适用时用ULAN团体记录 |
| place | 地理位置、历史名称、建筑身份与年代；城市／建筑不等于政府或管理机构 | Getty TGN、ICCD文化遗产总目录、国家／地方地名资料、建筑和管理机构记录 |
| work | 作者／归属、题材、年代、媒介、版本、收藏位置及馆藏号；原作、复制品、草稿与系列分开 | 博物馆馆藏、ICCD及其他文化遗产目录、专业作品总目、适用的Getty CONA；馆藏号或国家目录号优先于百科题名 |
| archive | 题名、作者／发收者、日期、文献性质、卷册／版本、保管机构和索书号；单封信、信集与刊录论文分开 | 保管机构目录和finding aid、OPAC SBN／EDIT16／Manus Online、国家与大学图书馆目录、VIAF责任者入口、出版社／期刊与Crossref等书目记录；Internet Archive、HathiTrust、Google Books、Gallica等只在核定版本与实际页后支持正文 |
| term | 语义定义、语种、历史语境与适用范围；同词跨学科或历史义不同不能直接等同 | Getty AAT、历史／专业词典、规范词表及实际定义该术语的原始文献和研究文献 |
| procedure | 实际操作、步骤、条件、参与者和适用范围；广义方法页不等于本书中的特定做法 | 合同、章程、工场或机构操作记录、专业技术史资料及适用的Getty AAT |
| event | 时间、地点、参与者、事件范围；一项委托、具体执行与泛称历史时期分开 | 原始档案、当时报刊／书信、官方历史记录及实质讨论该事件的研究文献；参与者页面不能代替事件证据 |

所有文献归archive，包含未出版档案及学术文献；艺术原作图册与文献性图录按taxonomy-registry.md判断。具体书信、合同或作品通常没有独立QID或Wikipedia页，可用档号、索书号、SBN／EDIT16／Manus Online标识、DOI、ISBN、OCLC号、数字化项目标识或馆藏号表达其身份；没有适用标识时保留来源中的题名、责任者、日期和位置组合，不借用信集、作者或保管机构的标识。

数据库命中的能力必须分开：人物辞典正文可支持其明确叙述；规范库主要支持名称同一与责任者身份；联合目录支持版本和馆藏线索；finding aid支持档案层级和保管信息；Internet Archive等数字库的item页面支持版本与文件入口，只有核对扫描版本并实际阅读相应页面后才支持正文事实。聚合站从其他机构转入的记录保留原始提供者与同源关系。

采用外部内容须阅读正文或完整记录，并将事实绑定准确来源和实际访问日期。书目命中只支持相应书目事实，不能声称读过原件。网页/摘要仅提及目标名称不支持其定义、技术史地位或与本书对象的具体关系。模型内部知识可帮助提出检索线索，不能作为已查阅的外证，也不能凭空标为 source_backed。

使用机器验证状态接口时遵循collect → evidence JSONL → 语义判断 → dry-run → apply；格式与状态上限以result-handling.md为准。任何两个互相链接或共享上游记录的数据库都不自动构成两份独立事实证据，也不自动完成整篇知识元验证。

claim 不是 KU：分别核对事实、解释、归纳和评价，保留作者及证据责任，以 quality/claim-registry.yml 绑定证据；KU 的存在不证明相关断言。domain/dimension/theme/topic 的形成与审查归已启动的 synthesize；当前不开展，不把后续层级审查加入第一部分。

来源能力参考：[Treccani人物辞典](https://www.treccani.it/biografico/)、[SIUSA](https://siusa-archivi.cultura.gov.it/)、[OPAC SBN](https://opac.sbn.it/it-IT/opac-del-sevizio-bibliotecario-nazionale)、[Manus Online](https://manus.iccu.sbn.it/)、[ICCD文化遗产总目录](https://catalogo.beniculturali.it/)、[Internet Archive文本库](https://archive.org/details/texts)、[VIAF](https://www.viaf.org/)、[Getty Vocabularies](https://www.getty.edu/research/tools/vocabularies/)、[Wikidata Sitelinks](https://www.wikidata.org/wiki/Help:Sitelinks)、[MediaWiki Pageprops](https://www.mediawiki.org/wiki/API:Pageprops)（2026-09-11核对适用范围）。
