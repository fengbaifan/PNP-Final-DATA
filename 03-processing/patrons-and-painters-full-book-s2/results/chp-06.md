# 第六章全书S2当前结果

任务：patrons-and-painters-full-book-s2。第六章共33个规范段。按当前覆盖账本，28段reviewed、5段excluded，queued/partial均为0；33段的migration_status均为complete。当前计数以`04-knowledge/tables/s2-coverage.csv`为准，全书状态见`04-knowledge/results/patrons-and-painters-full-book-s2.md`，后续逐段记录见同任务`results/stages.md`。

下文逐段处理说明、全书累计数及“下一段”是形成时的历史进度快照；当前覆盖状态以覆盖账本和全书结果文件为准。

## 第六章候选表面提示复核（2026-10-08）

在28个已审段上复核定位器给出的23条提示。8条补录为精确mentions：Rome三处→cand-3126；p.156注2的“collection”→Antonio degli Effetti类型待定收藏cand-6389；Christina的“collection”→既有图片收藏cand-5565；“foreign travellers”→cand-3562；“Renaissance”→cand-3578；p.164注3“theatre”→cand-6545。未新增候选。其余15条按原文语义不写入：普通subject 2、drawings类别、泛指palace、建筑“character”、temperament、financial difficulties、一般churches 2、Rosa比喻中的garden、Gaulli portraits类别、诗歌类别、crop prices及Ottoboni作曲活动。Rome三条均保留原提示“in Rome”，实际mention跨度只取城市名。

受控脚本`chp6_candidate_surface_prompt_reconciliation.py`锁定候选、mentions、statements、segments、coverage、定位器及相关S0分节，默认dry-run，核验23条提示分区、精确原文跨度、候选外键、既有跨度不重叠及statement前态后再apply。写入8条mentions；未增删candidate、statement、coverage或relation行。将p.156注2 statement的`mentioned_candidate_ids`补入cand-6389、p.164注3 citation statement补入cand-6545；修正p.164 Juvarra statement中已失效的“footnote 3 remains pending”限定。plan SHA-256=`db13bb71a4907ad5069cd729caa9c27d6f1069aca61dcb63a3a5475781451513`，script SHA-256=`cfbfbb7b6d4754384d2d3b683c1fa4ccaf26536e6f8f6735b575fe7d327ed5a8`。mentions SHA-256从`c43354eddb206f135ba3b638d4a4949e74dae129c4bbeb30158daf2a219c7541`变为`52a5b14c3ca39e3127ed89a491452f8043cb6a9b9092d19c6898241f80d38b58`；statements从`5999d2851d45c5b0ab2157478d8926d0ca4fc5aa1abcbcae164aab2ebdd9c1a6`变为`c1ba516072b1a54969c1de7a6763afe22ff984bca1469581ee49acdfa007cec3`。恢复副本保存在`%TEMP%\pnp-s2-chp6-surface-prompts-20261008-084741\`。写后定位器剩余15条，与全部no-write签名相同。

`python -X utf8 scripts/audit_tables.py --strict-stage`通过：1,019 KU、11,464 candidates、27,151 mentions、12,255 statements；`s2_missing=[]`、`errors=[]`，覆盖678 complete、154有理由排除、0 queued、0 partial。两条既存enrichment `source_ref`警告不变。第七章现有候选表面扫描为47个已审段、40条提示，均待按书序裁决；定位器提示不代表召回率或语义验收。

第六章旧阅读稿与草稿只作语义核漏背景。当前有效处理逐段对应规范源；脚注、跨页句及扫描校勘按印刷页序登记。第147–156页已处理范围内的跨页句均已闭合；p157 Antonio目录句由L56闭合，p158 Marucelli引介由L13闭合，Bellori《Lives》句由p159 L29闭合。

第160页正文段l40-50已迁移：新增19个候选；正文75条提及、20条原书断言。记录Bellori对竞争艺术趣味的反对及Haskell的限定解释、Maratta与古典理想/高巴洛克比较、Gaulli Gesù壁画的评价和引述层级、外地艺术家在罗马的处境、批评话语、Jacomo di Castro 1670年引文、Bellori任职、Christina经历与收藏及Haskell对其赞助的评价。校记见全书S2过程记录；S0原文未改。p159 L38句由p160 L41闭合；p160 L50末句续至p161 L53。

第160页脚注1–4（复合段l55-72的L66–69）已迁移，新增12条注释提及及4条书目定位记录，并分别回链至Gaulli接收、Jacomo引文、Christina引语和收藏断言。脚注仅作书目定位，未冒充外部核验。

第161页第IV节末段L52–53已迁移，新增1个事件候选、16条正文提及和8条原书断言；闭合p160 L50关于Christina赞赏Mola的未完句。新增Gherardi为Mola学生、其对Venetian colour的偏好，以及Bellori鼓励Christina赞助Canini、Canini分别作为Domenichino学生与Bellori门生等断言；保留Haskell的评价层级，不将赞助扩成委托。第161页脚注1（复合段L70）已与Canini相关断言回链；复核并将先前误挂在p159 ID下的p161注1、3、4提及改回p161。第V节L3–11正文及注2已处理，复合段L71–72的注3–4已回链；L11末句待p162 L15续接。物理第16页校勘：OCR将“of little”连作“oflittle”、在句号后多出逗号，且漏掉protégé重音；原S0不改。额外脚注2转录与第V节L12重复，已在S2有理由排除。

全书账本为247段reviewed/complete、0段reviewed/partial、41段有理由排除、515段queued；候选6,476条、提及9,913条、原书断言4,947条。表审计errors为0；两条既存enrichment source_ref警告及515段queued、语义质量复核提示仍在。

p161第V节迁移新增23个局部候选、53条精确跨度提及和22条正文断言；注2–4以4条引文定位statement处理并链接到正文，注3–4位于复合段L71–72。扫描物理第16页核实Clement IX后有空格、The fresco中间有空格、a Barberini前无多余o；S0原文保持不改。p161 L11末句待p162 L15续为“or a Chigi”，该断言保持pending。

下一段为chp-6:06_CHP-6_sec_v:l14-19（印刷页162）。续接完成后继续全书S2；全书覆盖和语义交接审计完成前不进入S3。
