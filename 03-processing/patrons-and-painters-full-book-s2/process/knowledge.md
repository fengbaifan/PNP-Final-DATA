# 全书 S3 身份对齐过程

更新日期：2026-10-18。

## 范围与裁决方式

输入为当前 `entity-candidates.csv`、S2 提及与断言定位、`ku-manifest.csv` 及原有 `alignment.csv`。S3 只裁身份，不补写生平、作品内容、档案事实或正式关系。每个候选均保留 `same`、`new`、`conflict`、`excluded`、`undecided` 之一；决定理由及来源锚点写在 `alignment.csv` 的 `process_ref` / `resolution_note`。`new` 表示已判定应新增一个身份组；S4 已登记者补有对应 KU，未登记者保留待登记状态。

先核对原有 335 条对齐记录。185 条含外部标识的记录原样保留；其余候选级记录复用原 `alignment_id`，把旧决定、KU 指向、日期、过程号和原注释留在新注释末尾作历史。新增的候选级记录取得新 `alignment_id`。`accepted-ku` 候选只在 `candidate_source_ref` 与 manifest 中唯一 `card_path` 完全相同时归为 `same`；1,001 个此类候选均按这条路径匹配。没有对外部目录或网站作新的查询；既有标识不是本轮新验证结果。

分类建议分别覆盖人物、作品、档案文献以及事件、家族、机构、地点、程序、术语和未分类对象，随后统一检查候选覆盖、类型边界、KU 外键、S1 排除状态、跨章组和既有外部记录。名称相似本身不作合并依据；来源未能确定身份、对象层级或类型时保留 `undecided`，相互矛盾的书内归属保留 `conflict`。

`alignment.csv` 没有独立的 group 字段，故在 `resolution_note` 中保存稳定的 `group=` 标识。`same` 组指向 manifest KU；`new` 组内的候选裁为同一新身份；`sg3-review-*` 标记仍待判断的交叉引用或歧义簇。组成员关系本身不替代决定值，也不自动断言同一性。

## 跨章身份分组与边界

- 新身份组：1667 年克勉九世即位（`cand-4813`、`cand-6482`）；贝加莫城市（`cand-11460`、`cand-7743`、`cand-6208`、`cand-8574`）；Farsetti 在 S. Maria di Sala 的乡间宅邸（`cand-1007`、`cand-10432`）；Montecchio 的 Villa Cordellina（`cand-10279`、`cand-8376`）；维琴察 Cordellina 宅邸（`cand-11069`、`cand-8375`）；Dresden Gallery（`cand-10222`、`cand-9091`）。这些组各自没有现成同类 KU，决定为 `new`，不是把不同对象并入既有卡片。
- 分开处理的事件：S. Giovanni Decollato 的持续系列与 1675、1736 两次具体事件分别分组；S. Rocco 的年度系列与 1770 年具体事件分开；贝加莫 1653 年装饰计划与 1695 年完成事件分开。
- 保留待证的交叉引用：John Strange 在 Paese 的别墅与“Treviso 附近乡间宅邸”尚无同一建筑证据；威尼斯与佩鲁贾 Baglioni 家族的谱系关系未明；Rialto 地区与构图中的 Rialto 元素分开。Gonzaga 家族候选与“see under Mantua, Dukes of”索引交叉引用共用 `sg3-review-gonzaga-family-redirect` 仅为检索/复核关系：后者按 S1 已排除，不能被视为另一个 family 身份；House Savoy 的 family 候选与类型不符的索引指引也分别保留。相关候选保留单独的 review 组或候选级决定，不以索引、相邻条目或共现代替证据。
- 档案/文献类型形成 27 个已裁定的跨章多候选身份组；另有 `cand-6207` / `cand-11945` 作为待证重复候选组保留。题名相同但版次、卷册、责任者、日期或档号不一致时不自动合并。
- 历史分组、复用与拆分轨迹见下方各批次记录；截至 2026-10-17 的候选数及逐类型决定数以本节统计表和全书结果文件为准。S4 已登记组按每组一个 KU 处理并映射全部组内候选；未登记组按本节统计保留待办。

## 按类型决定数

数字按每个候选唯一的一条空 `external_source` 决定记录统计，不把保留的外部标识行重复计为另一个候选决定。

| 类型 | 候选 | same | new（组/成员） | conflict | excluded | undecided | S4已登记（组/成员） | S4待登记（组/成员） |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| archive | 2,100 | 90 | 1,203 / 1,249 | 0 | 18 | 743 | 109 / 151 | 1,094 / 1,098 |
| event | 357 | 7 | 231 / 235 | 0 | 0 | 115 | 34 / 38 | 197 / 197 |
| family | 135 | 22 | 88 / 94 | 0 | 1 | 18 | 88 / 94 | 0 / 0 |
| institution | 497 | 180 | 191 / 196 | 0 | 0 | 121 | 24 / 29 | 167 / 167 |
| person | 3,464 | 1,090 | 1,061 / 1,155 | 4 | 7 | 1,208 | 663 / 756 | 398 / 399 |
| place | 1,109 | 226 | 559 / 567 | 0 | 0 | 316 | 40 / 48 | 519 / 519 |
| procedure | 43 | 10 | 29 / 31 | 0 | 0 | 2 | 29 / 31 | 0 / 0 |
| term | 1,640 | 43 | 928 / 940 | 0 | 2 | 655 | 35 / 47 | 893 / 893 |
| work | 2,397 | 237 | 479 / 494 | 5 | 29 | 1,632 | 50 / 56 | 429 / 438 |
| 未分类 | 665 | 0 | 0 / 0 | 0 | 43 | 622 | 0 / 0 | 0 / 0 |
| **合计** | **12,407** | **1,905** | **4,769 / 4,961** | **9** | **100** | **5,432** | **1,072 / 1,250** | **3,697 / 3,711** |

48 项 S1 明确排除均保留为 `excluded`（未分类 43、人物 3、作品 1、术语 1）；另有 52 项按 S3 的对象类型／独立性判断排除（档案文献 18、家族 1、人物 4、术语 1、作品 28）。曾有一条作品占位候选 `cand-10059` 在类型建议中误判为 `same`；合并时按其 S1 排除状态恢复为 `excluded`。其所指的真实作品由候选 `cand-4048` 承接。

人物冲突 4 项、作品冲突 5 项；冲突两侧和来源位置均留在候选行，不强选一方。5,430 项 `undecided` 各自保留对象、版本、身份、类型或来源锚点不足的理由与后续去向；其中 622 项仍为未分类类型，等待类型证据，不强塞入现有类。所有 12,407 个候选各有且仅有一条 `external_source` 为空的当前决定；248 条外部身份记录另行保留。same 的 1,902 条候选指向 1,040 个既有 KU；new 候选组成 4,775 个类型内身份组，共 4,966 条映射。S4 按整组登记，当前没有组内部分登记或类型不符映射；未登记组保留在 S4 待办中。此处收口的是 S3 决定与可追溯去向，冲突和待证身份问题本身未解决。

### 跨章补充裁决：Valmarana 壁画组（2026-10-15）

- 候选 `cand-2594`（work，索引子目为 Homer、Virgil、Tasso、Ariosto 场景壁画）此前被裁为 `undecided`，理由称没有可核的 S2 正文提及。复核当前 `mentions.csv` 与 `book-statements.jsonl` 后发现该理由与现有记录不符：第9章 p.258 的壁画系列提及及 `st-chp9-p258-tiepolo-painted-valmarana-fresco-cycle`，与第20章 p.405 后记的同组壁画提及及 `st-chp20-p405-puppi-corrects-valmarana-fresco-commission` 均指向同一组作品，后记明确回指第9章。
- 该组可按地点、创作者、题材范围及来源交叉指引形成一个可辨认壁画组。对照 S3 时点 manifest 和作品卡，无同类现有 KU；故将 `cand-2594` 的决定由 `undecided` 更正为 `new`，组号 `sg3-work-valmarana-fresco-cycle`，交 S4 登记一个描述性作品 KU。之前决定及更正缘由保存在对齐注释和[复核脚本](reconcile_s3_valmarana_fresco_cycle_20261015.py)中。
- 第9章 p.258 只称 Leonardo Valmarana 似在1757年为家族首领，并明确该人格描述来自不够可靠的葬礼演说；不能把首领身份推为壁画委托人。第20章 p.405 后记转述 Puppi 的更正，称壁画实际由 Conte Giustino Valmarana 委托。此处保存为 Haskell 对该研究的报告，Puppi 文章未独立查阅。家族 KU 与壁画 KU 分开；Leonardo 与 Giustino 人物候选也不混并。

### 跨章补充裁决：Grand Prince Ferdinand de’ Medici 复用既有人物 KU（2026-10-15）

- `cand-1609`（M.csv#149）与 `cand-1611`（M.csv#151）此前按全名/别称证据组成一个 `new` person 组；复核发现相同人物已有 accepted KU `units/persons/ferdinand-grand-prince-tuscany`，且 `cand-1617`、`cand-3761` 已映射该卡。不能仅因索引采用 “Ferdinand de’ Medici” 而将其另建为新人物。
- 第8章 p.229 将 Grand Prince Ferdinand 与 Plate 36a 相连，并称其为推动佛罗伦萨复兴的人物；章前图版目录明确 Plate 36a 为 “Grand Prince Ferdinand of Tuscany”，既有卡还保存第一版序言中的同名用例。第20章 p.403 后记再次以全名 “Grand Prince Ferdinand de’ Medici” 讨论其赞助。全名、称号、图版对象及现有映射共同支持同一人物。索引子目 `and G. M. Crespi` 仅是关联提示，不将 Crespi 并入人物身份。
- 因此将 `cand-1609`、`cand-1611` 从 `new` 更正为 `same`，映射既有 KU，组号统一为 `sg3-ku-units-persons-ferdinand-grand-prince-tuscany`。旧的 `new` 分组及理由完整保存在两条对齐注释末尾；[复核脚本](reconcile_s3_ferdinand_medici_identity_20261015.py)先 dry-run 后 apply。未查询外部来源。该次更正后计数为 same 1,675、new 5,006；当时 new 身份组为4,830，不新增 KU。

### 跨章补充裁决：Bracciano 的 Paolo Giordano II Orsini 独立成组（2026-10-16）

- `cand-0428`（B.csv#275，索引页95–99、401）与 `cand-0434`（B.csv#281，索引页387–389）具有相同全名候选词头。第4章 p.95–99 明称 Paolo Giordano II Orsini, Duke of Bracciano；第19章附录标题为其委托 Bernini 与 Tacca 的文件；第20章 p.401 又以全名识别其青铜胸像。故两条候选归入同一个 `new` person 组 `new-person:bracciano-giordona-ii-of-orsini-paolo-502da19f7d`，供 S4 登记一个 KU。
- `cand-0428` 此前因爵号相同而错误复用 `Duke of Bracciano (Mulier’s patron)`。该卡明确记录 Mulier 的赞助人尚未具名，并保留 Ferdinando/Flavio 两代候选；它不能承载原书明确命名的 Paolo Giordano II。现有 `paolo-giordano-orsini` 卡则指 Paolo Giordano I，罗马数字不同，不与 II 并合。
- 已将 `cand-0428` 从 `same` 更正为 `new`，撤销其 Mulier 卡指向，并与 `cand-0434` 共组。旧决定及注释全文保留在对齐行末尾；[复核脚本](reconcile_s3_bracciano_paolo_giordano_ii_identity_20261016.py)先 dry-run 后 apply。未查询外部来源；本次不新增 KU。该次更正后全表为 same=1,674、new=5,007；当时 new 组数保持4,830，待 S4 映射候选数增加1。

### 跨章补充裁决：Prince Camillo Pamfili 复用既有人物 KU（2026-10-16）

- `cand-1814`（P.csv#13）汇集第1、3、4、5、6章等正文提及。第1章 p.9 将 Prince Pamfili 的 Valmontone 委托与写给 Camillo Pamfili 的信置于同一工程语境；第3章 p.106 明称 Prince Camillo Pamfili 为 Pope Innocent X 之侄，并在脚注指向第6章；第6章 pp.147–150 以“authentic Prince Camillo Pamfili”与 Camillo Astalli 对照，支持该候选不是 Astalli。
- 上述书内锚点与既有人物卡 `units/persons/camillo-pamfili` 的 Camillo Francesco Maria Pamphili 身份、Valmontone 语境，以及已映射至该卡的 `cand-3009` 一致。因此将 `cand-1814` 从 `new` 改为 `same`，指向既有 KU；不新增卡片，也不重复查询外部身份来源。旧 `new` 组与原裁决理由留在对齐行历史注释中；[复核脚本](reconcile_s3_camillo_pamfili_existing_identity_20261016.py)先 dry-run 后 apply。
- `cand-1815` 仍为 `undecided`：它只有索引页码而没有映射的 S2 正文提及。第3章 Gaulli 的未具名 Prince Pamfili（`cand-5228`）和“1667年去世的 Prince Pamfili”（`cand-5327`）也保留各自待证决定，不据姓氏、爵号或相邻语境合并；类型为 place 的 `cand-1816`、`cand-1817` 不纳入人物组。
- 该次更正后决定计数为 same=1,675、new=5,006；当时 new 身份组为4,829，不新增 KU。

### 跨章补充裁决：Gian Pietro Bellori 复用既有人物 KU（2026-10-16）

- `cand-0272`、`cand-0274`、`cand-0277` 的索引词头均为 “Bellori, Gian Pietro”，分别汇集其一般提及、《Descrizione delle Immagini dipinte da Raffaello d’Urbino》及《Le Vite de’ Pittori, Scultori et Architetti Moderni》。第6章 p.159 明称 Gian Pietro Bellori，并将其与1672年出版的《Lives》及前述 Raffaello 著作相连；第4章称其为意大利评论家，另有第7章与第20章后记交叉提及。
- 既有人物卡 `units/persons/giovanni-pietro-bellori` 记载 Giovanni Pietro Bellori，并保留 Giovanni/Giovan Pietro 名称变体；已有 `cand-3056` 映射该卡。名称变体、作品责任者和跨章语境支持三条候选与既有人物为同一身份，因此将三条从 `new` 更正为 `same`，映射该 KU 与既有组 `sg3-ku-units-persons-giovanni-pietro-bellori`。旧 `new` 组与原注释保留在对齐行；[复核脚本](reconcile_s3_bellori_existing_identity_20261016.py)先 dry-run 后 apply。本次不新增卡，也未查询外部来源。
- Bellori 更正后当时人物类型为 `same=944`、`new=1,194`；全表为 `same=1,678`、`new=5,003`，当时 `new` 组4,828个。S4 登记数不变。

### 跨章补充裁决：Giambattista Albrizzi 复用既有人物 KU（2026-10-16）

- `cand-0025`、`cand-0027`、`cand-0029` 均为索引词头 “Albrizzi, Giambattista”，分别定位其出版者及收藏者叙述、与 Piazzetta 的合作和私人收藏。第13章 p.334 明称 Giambattista Albrizzi 为威尼斯重要出版者之一，随后连续叙述其出版、艺术活动及与 Piazzetta 的合作；p.336 又以 Albrizzi 指称其私人收藏。章前图版目录将 Albrizzi 与1745年 Piazzetta 版《耶路撒冷解放》联系起来。
- 既有人物 KU `units/persons/albrizzi` 记录 Giovanni Battista Albrizzi，并把出版署名 “Giambatista Albrizzi” 列为姓名形式；既有 `cand-3711` 已映射该 KU，章前图版目录为其来源证据。第13章的完整姓名、威尼斯出版者身份、Piazzetta 合作及同一1745年出版物语境支持复用该人，而不是另建卡。故将三条候选从 `new` 更正为 `same`，统一映射至 `sg3-ku-units-persons-albrizzi`。旧 `new` 组和理由保留在对齐行；[复核脚本](reconcile_s3_albrizzi_existing_identity_20261016.py)先 dry-run 后 apply，未查询外部来源。
- 第13章称其约生于1699年；既有人物卡外部来源记录精确日期1698-12-29。该差异是来源层级的日期核对项，不足以指向第二个人；本轮不改写旧卡或升级外部事实，留待后续事实核对。索引候选 `cand-0026`、`cand-0028`、`cand-0030` 仍因没有 S2 正文锚点而保持 `undecided`，不因同名主词自动映射。
- Albrizzi 更正后、Marchese del Carpio 复核前，人物类型为 `same=947`、`new=1,191`；全表为 `same=1,681`、`new=5,000`，当时 `new` 组4,827个。S4 已登记数不变。

### 跨章补充裁决：Marchese del Carpio 复用既有人物 KU（2026-10-16）

- `cand-0569`、`cand-0570`、`cand-0571`、`cand-0573` 均为人物索引候选，覆盖 Marchese del Carpio 的跨章一般条目、Bernini 关联、那不勒斯任职及罗马活动。第7章 p.190 明称 “Don Gasparo de Haro y Guzman, known in Italy as the Marchese del Carpio”，pp.191–192 继续叙述同一位大使、总督的赞助和执政活动；其全名及明确爵号指认锁定该组身份。
- 既有人物 KU `units/persons/marchese-del-carpio` 标题为 Gaspar Méndez de Haro, 7th Marquess of Carpio；`cand-3076` 已将该卡纳入同一 S3 `same` 组。故4条具正文锚点的候选从原 `new` 组 `new-person:carpio-del-carpio-del-s-6b4329a11f` 更正为 `same`，映射至该 KU 和既有组 `sg3-ku-units-persons-marchese-del-carpio`。旧组号、分组理由和候选原注完整保存在各对齐行；[复核脚本](reconcile_s3_del_carpio_existing_identity_20261016.py)经 dry-run 后 apply，未查询新外部来源或改动既有卡。
- 索引候选 `cand-0572`（Naples reforms）和 `cand-0574`（罗马从 Massimi 收藏购入物）没有 S2 正文提及映射，仍为 `undecided`；不能仅据索引邻近条目并入。候选组共45条 S2 断言端点不因此另建人物 KU。
- 该次 Carpio 更正后人物类型为 `same=951`、`new=1,187`；全表 `same=1,685`、`new=4,996`；`same` 多候选组271个，`new` 身份组4,826个、其中133组为多候选组。S4 登记的111组、126条候选不变。

### 跨章补充裁决：Sasso 候选复用既有人物 KU（2026-10-16）

- `cand-2364` 的 S2 锚点包含第16章 p.373 的 “Giovan Maria Sasso” 和第17章 p.380 的 “Giuseppe Maria Sasso”；其索引主项 `S.csv#52` 将 p.373–380 等相关页集中为一个人物候选。第16章描述其为在威尼斯经营的艺术商人和收藏者；第17章在 Girolamo Manfrin 的威尼斯艺术赞助语境中，转述1790年 G. A. Armarmi 致 Sasso 的信，并称他是城中少数仍愿为艺术支出的商人之一。
- 既有人物 KU `units/persons/g-m-sasso` 以章前图版的 “G. M. Sasso” 及既有目录/肖像依据登记为 Giovanni Maria Sasso；`cand-3776` 已映射该卡。第16章 “Giovan” 与卡名 “Giovanni” 相符，第17章的 “Giuseppe” 与两章共指、人物职业语境及共用索引主项相连。故将 `cand-2364` 从 `new-person:giuseppe-maria-sasso-53ab44c390` 更正为 `same`，映射至现有 KU 和组 `sg3-ku-units-persons-g-m-sasso`；对齐行保留原 `new` 组和理由，并明确记录 Giovan/Giovanni/Giuseppe 异名，不据此改写旧卡全名或生平。复核脚本 [reconcile_s3_giovanni_maria_sasso_existing_identity_20261016.py](reconcile_s3_giovanni_maria_sasso_existing_identity_20261016.py) 先 dry-run 后 apply，未查询新外部来源。
- 该候选有40条 S2 断言端点，不另建重复人物 KU；其他仅以姓氏或首字母指称的对象不随之自动并入。该次更正后人物类型为 `same=952`、`new=1,186`；全表 `same=1,686`、`new=4,995`；`same` 多候选组272个，`new` 身份组4,825个、其中133组为多候选组。S4 登记的112组、127条候选不变。


### 跨章补充裁决：Guglielmo Borgognone 候选复用既有人物 KU（2026-10-16）

- `cand-0401`、`cand-0402` 原按索引姓名组成 `new-person:borgognone-guglielmo-courtois-guillaume-d85d80e219`。第3章 p.79 先明确 Jacques Courtois／Giacomo Borgognone 与其兄弟 Guglielmo 一同为 Oliva 作画；pp.87–88 又以全名 “Guglielmo Borgognone” 指认受托作品，并称其兄弟 Giacomo 为耶稣会士。
- 既有人物 KU `units/persons/guglielmo-cortese` 已由 `cand-3063` 按卡路径映射，`cand-3480` 也依据第1章全名映射至同一人物组；卡片记录其兄弟为 Jacques Courtois。正文交叉语境和既有映射共同支持复用该人物 KU，而不是再建 Guglielmo 人物卡。故两条从 `new` 更正为 `same`，映射至 `sg3-ku-units-persons-guglielmo-cortese`；旧组号及原始理由留在各自对齐注释历史中。
- `cand-0399` 的 Jacques Courtois／Giacomo Borgognone 仍为独立新人物组，不与其兄 Guglielmo 混并；`cand-0400` 只有索引子目且没有 S2 正文锚点，继续 `undecided`。[复核脚本](reconcile_s3_guglielmo_cortese_existing_identity_20261016.py)先 dry-run 后 apply，未查询外部来源。更正后 S3 为 same 1,688、new 4,993；new 组4,824个，其中132个多候选组。S4 登记数不变。

### 跨章补充裁决：三条人物候选复用既有 KU（2026-10-16）

- `cand-1844` 原为单候选新组 `new-person:giambattista-pasquali-d8a083f523`。索引全名为“Pasquali, Giambattista”；第10章 pp.299–301 以 G. B. Pasquali 指称 Smith 发起其出版事业的年轻出版者，p.301 称其为 Smith 的客户；第13章 pp.334–338 延续同一威尼斯出版者的叙述。既有 `units/persons/pasquali` 卡的规范全名为 Giovanni Battista Pasquali，已记录 Giambattista 异名、印刷者/出版者身份及 Treccani、巴塞罗那大学印刷者规范记录；`cand-3857` 已映射至该卡。故 `cand-1844` 从 `new` 更正为 `same` 并复用既有人物组，不因姓氏相同而合并。该候选有33条 S2 断言端点，其中30条为关系候选。
- `cand-1325` 原为单候选新组 `new-person:elector-johann-palatinate-wilhelm-b5477ca163`。第10章 p.281 明称“the Elector Johann Wilhelm”，p.282 继续以全名叙述其统治。该全名与头衔对应既有 `units/persons/johann-wilhelm-elector-palatine` 卡的 Johann Wilhelm, Elector Palatine；卡内 Deutsche Biographie 的 GND 118712411 记录支持身份。既有候选 `cand-3812` 已映射该 KU，故复用同一人物组。该候选有34条 S2 断言端点，其中29条为关系候选。
- `cand-2426` 原为单候选新组 `new-person:3rd-of-shaftesbury-82bbccfee5`。第7章 p.198 明称“the 3rd Earl of Shaftesbury”，第5、6章亦以 Lord Shaftesbury 指称同一艺术理论与赞助语境中的人物；索引头衔与既有 `units/persons/anthony-ashley-cooper-3rd-earl` 卡的全名 Anthony Ashley-Cooper, 3rd Earl of Shaftesbury 对应，`cand-3378` 已映射该卡。故复用既有 KU。该候选有29条 S2 断言端点，其中27条为关系候选。
- [三项跨章复用脚本](reconcile_s3_cross_chapter_person_reuse_20261016.py)的 dry-run 核对候选原组均为单成员、既有 KU 类型/卡路径/名称、已有 same 映射、相应章页原文及断言端点数后通过；apply 仅将三条 `new` 改为 `same`，把 KU 与既有组写入对齐行，并保留原新组号和理由。未访问新外部来源，未改动其他候选。当前 S3 为 `same=1,691`、`new=4,990`，当前新组4,821个，其中132个多候选组；`same` 仍为1,019组，其中275组含多个候选。S4 已登记的115组、134条候选映射不变。
## 待办端点及交接

关系待办 `bl-0001` 只在书目注释中具名 Luigi Pavini，未见当前同名候选或 KU。本轮按既有 backlog 规则把该直接端点加入 S1 候选表为 `cand-12425`，并以书内“1734 年小册子出版者”这一有限身份决定 `new`，组号 `sg3-person-luigi-pavini`。该裁决不补写其生平或外部身份；backlog 仍为 `pending`，因为 S4 尚未登记 KU，相关 S6 关系也仍保持待证。

## 完成状态与限制

全书候选级 S3 决定闭包已完成：12,404 个候选都有唯一、可追溯的决定；原有 185 条外部标识行保留。S3 的完成表示候选都已进入明确去向，不表示 5,576 个 `undecided` 的身份已查明，也不把 7 个 `conflict` 当作已解决。当前有 5,006 个 `new` 身份候选、4,835 个新身份组；两条 Grand Prince Ferdinand de’ Medici 候选依据第8章全名与图版36a、第20章后记及已登记的 Ferdinand of Tuscany KU，从 `new` 更正为 `same`；`cand-0428` 则因其全名为 Paolo Giordano II Orsini，从未具名的 Mulier 赞助人 KU 拆出，并与 `cand-0434` 共组；`cand-1814` 根据第1、3、6章的具名交叉语境映射至既有人物 KU；`cand-0272`、`cand-0274`、`cand-0277` 根据第4、6、7章和第20章后记的交叉语境映射至既有 Giovanni Pietro Bellori KU；`cand-0025`、`cand-0027`、`cand-0029` 根据第13章出版者叙述和既有姓名署名证据映射至 Giovanni Battista Albrizzi KU；`cand-0569`、`cand-0570`、`cand-0571`、`cand-0573` 根据第7章全名和明确爵号指认映射至既有 Marchese del Carpio KU；`cand-2364` 根据第16、17章威尼斯艺术商人语境和既有人物卡的 G. M. Sasso 证据映射至 Giovanni Maria Sasso KU，并保留书内 Giovan/Giovanni/Giuseppe 姓名差异；cand-0401、cand-0402 复用既有 Guglielmo Cortese KU；cand-1844、cand-1325、cand-2426 分别复用 Pasquali、Johann Wilhelm 与第三代 Shaftesbury 既有人物 KU；cand-1466 复用既有 Owen MacSwinny 人物 KU；cand-0544、cand-0545、cand-0547、cand-0549 复用既有 Caravaggio 人物 KU；cand-0812、cand-0813 从 `undecided` 更正为与 cand-0811 同组的 Lorenzo Onofrio Colonna 新身份；cand-0399 保持 Jacques Courtois 独立 new 组，cand-0400 保持待证。`cand-1815` 及未具名 Prince Pamfili 候选仍待证。Zanetti 工艺、Barberini、Chigi、Del Rosso 及 Valmarana 壁画组分别按证据并组；Borghese、Aldobrandini、Ferdinand de’ Medici、Camillo Pamfili、Bellori、Albrizzi、Marchese del Carpio、Sasso、Owen McSwiny 与 Caravaggio 复用既有 KU；Lorenzo Onofrio Colonna 三条候选已成组，另一个 Naples 语境的 Colonna 候选保留待证。 后续跨章复核又新增 Alessandro Farnese 公爵候选，并将 Dolfin 家族索引主项 `cand-0930` 从 `undecided` 转为与 `cand-0931` 共组的 `new`；Giovanelli family 与 collection、Sagredo family 与个人候选均保留类型和身份边界。其余未决候选应在出现所需书内或适用权威证据前保留现状。后续 S4–S7 仍按阶段推进；知识发现或页面制作未启动。

- 正式决定表：[alignment.csv](../../../04-knowledge/tables/alignment.csv)
- 当前候选表：[entity-candidates.csv](../../../04-knowledge/tables/entity-candidates.csv)
- 交接结果：[全书 S2/S3 当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)

### S3：Cardinal Francesco del Monte 候选复用既有人物 KU（2026-10-16）

- cand-1691（M.csv#232，Cardinal Francesco del Monte）原标为单成员 new-person:del-francesco-monte-7e5c27fe05。对照既有 manifest 与人物卡发现，units/persons/francesco-maria-del-monte 已登记同一位枢机；全书候选 cand-3271 已按 accepted-ku 路径映射该卡。
- 第2章 p.44 明称 Francesco del Monte；同章 p.47–48 将其连续叙述为卡拉瓦乔早期赞助者，并记其晚年继续寻访画家、促成 Andrea Sacchi 的圣彼得大教堂委托。第5章 p.120 与第20章 p.397 后记仍称 Cardinal del Monte。全名片段、枢机称号、赞助对象与跨章连续叙述共同支持复用 Francesco Maria del Monte；未按姓氏单独合并，也未新增外部身份查询。
- 将 cand-1691 从 new 更正为 same，指向既有人物 KU 与 sg3-ku-units-persons-francesco-maria-del-monte。对齐行保留原 new 组及理由全文；复核脚本 reconcile_s3_del_monte_existing_identity_20261016.py 经 dry-run 后 apply。决定计数变为 same=1,697、new=4,988；new 组减为4,819。manifest 和 accepted.yml 不变。

### S3 补充裁决：Giovan Francesco Romanelli 复用既有人物 KU（2026-10-16）

`cand-2208`（Q-R.csv#135，Romanelli, Giovan Francesco）原为 `new-person:francesco-giovan-romanelli-9cc80a7086`。第7章 p.181 以 Giovan Francesco Romanelli 指称 Francesco Barberini 的 favorite painter，随后连续叙述其绘制 Mazarin 画廊上层画廊及《罗慕路斯与雷穆斯》；既有 `units/persons/romanelli` 卡片以 Giovanni Francesco Romanelli 为全名，记录同一画廊和图版26b，且候选 `cand-3878` 已映射到该 KU。据全名异写、人物角色和同一作品/委托语境，将 `cand-2208` 从 `new` 更正为 `same`，并入 `sg3-ku-units-persons-romanelli`。原 `new` 组及理由保存在对齐行历史注释；[复核脚本](reconcile_s3_romanelli_existing_identity_20261016.py) dry-run 核对既有卡、accepted/manifest、精确原文和18条直接断言端点（16条关系候选）后 apply。same=1,698、new=4,988、undecided=5,614；same 组数维持1,019，多候选组增至278；new 组降至4,818。S4 manifest 与已登记147组/187条候选映射不变，未登记余4,671组/4,801条候选。未新增外部来源或正式关系。

### S3 补充裁决：Pierre Crozat 索引子目并入跨章人物组（2026-10-16）

`cand-0895`（C.csv#429，“patronage of Venetian artists”）原为 `undecided`，原因是该索引子目未映射到 S2 正文提及。复核索引父项 C.csv#428、子目页码284–285及第10章 p.284 的 Crozat patronage 断言、p.285 的 Carriera 接待断言后，确认该子目描述同一人物而非第二位赞助者。现将 `cand-0895` 改为 `new`，并与 `cand-0894` 共用 `new-person:crozat-pierre-793a5b5d2e`；原 `undecided` 理由全文保留在对齐行。新身份组数不变；S3 当前为 `new=4,989`、`undecided=5,614`、4,819组。裁决脚本 [reconcile_s3_crozat_index_subentry_20261016.py](reconcile_s3_crozat_index_subentry_20261016.py) dry-run 已核对三条 p.284–285 断言锚点后 apply；未新增 KU 或正式关系。

### 端点校正：Bracciolini 诗作子目与人物分流（2026-10-16）

复核第2章 p.52 后发现，索引 B.csv#288 的人物子目“L’elettione di Urbano VIII”及其正文提及“the poem”被映射到人物候选 `cand-0441`。第2章 p.57 将同名对象明确写作 Francesco Bracciolini 所作的颂诗；同一对象已有 archive 候选 `cand-4796`，其 S3 决定仍为 `undecided`（诗作／版本粒度未裁定）。因此将 `m-chp2-seciv-l96-104-0015`、`m-chp2-seciv-l96-104-0017` 与断言 `st-chp2-seciv-l96-104-poem-publication-and-honours` 的 object 端点改映至 `cand-4796`；`cand-0441` 继续作为索引中的人物子目候选，与 `cand-0440` 共组，不再把诗名当作人物身份锚点。诗作候选保持待证，相关关系留待 S6；人物组直接断言端点仍为16条，其中15条为关系候选；更正仅调整该断言的作品 object candidate。原映射及改因保留在提及、对齐和本记录中。

### S3 纠正：Andrea del Rosso 跨代同名人物拆分（2026-10-16）

`cand-2275`（Q-R.csv#203）与 `cand-2279`（Q-R.csv#207）原按相同姓名锚点共组。第8章 p.211 明确称长兄 Andrea 生于1640年，p.211 注释记其于1715年去世；同页另起句称“their grandfather”在1642年距去世两年，p.212 续以 Andrea 指称建造家族礼拜堂的祖父。两者虽同名，代际和生平不相容，必须分开。保留两条候选级 `new` 决定：`cand-2275` 留在 `new-person:andrea-del-rosso-670cf89453`，`cand-2279` 单独归入 `new-person:andrea-del-rosso-grandfather-2279`。旧组并列理由保留在对齐行历史注释。总组数增1至4,819，多候选组减1至133；候选数、已登记组与映射数不变。尚未新建 KU 或关系。

## S4 KU 登记（2026-10-15）

**状态：处理中。** 本轮按当前 S3 裁决需登记 5,007 条 `new` 候选，按 `resolution_note` 中的 `group=` 汇总为 4,838 个身份组；截至本次复核，已登记196组、247条成员映射，尚待登记4,640组、4,758条。登记约束为每组一个 KU、每条成员候选映射到该 KU；不以关系端点反推新身份。`same` 继续指向原 KU；`conflict`、`undecided`、`excluded` 不进入新卡。新卡的身份与描述限于所引用的书内材料，未把 S4 登记写成外部核验或 S5 补足。

### 登记前的跨章身份核对

候选 `cand-2852` 的索引子目为“rediscovery of process for making colour woodcuts”，p.343 的正文称 A. M. Zanetti the Elder 认为自己重新发现了“三色或四色明暗木刻”工艺；`cand-9734` 的 p.320 正文称同一位年长 Zanetti 曾向 Conti 宣告其重新发现彩色木刻工艺。两处都指向 Zanetti 的同一项工艺发现，p.343 是对工艺的具体化，而非另一个过程。已把两个 `new` 决定归入 `sg3-procedure-zanetti-colour-woodcut`，只登记一张 KU，候选分别映射到该卡。理由和页段同时写入两条对齐注释；候选级决定仍为 `new`，其余 S3 裁决未变。

`cand-0198` 是索引中的 Barberini family 候选，`cand-3464` 是第1章第15页的 Barberini ruling-clan 正文候选，`cand-6473` 则在第6章第161–162页作奢侈规模比较。三者指向同一集体家族，已归入 `sg3-family-barberini`。既有 Barberini household institution 仍单独保留；合组不把家族成员、财产或赞助关系视为已核验。

<a id="s4-luigi-pavini"></a>

### 首批：Luigi Pavini

- 候选：`cand-12425`；S3 组：`sg3-person-luigi-pavini`；类型：`person`。
- 依据：Haskell 第9章印刷页269注5（来源 OCR L95）称 Luigi Pavini 于1734年出版一份32页小册子，并列出题名与 Biblioteca Marciana, Misc. 1135, n. 3；该书目说法转引自 Ferrari 1882。卡片保留原文摘录、逐句摘要、来源文件及行号，不补传记或外部身份。
- 新 KU：`units/persons/luigi-pavini`，卡片为 `04-knowledge/units/persons/luigi-pavini.md`；已加入 `ku-manifest.csv` 和 `accepted.yml`。对应 `aln-12588` 已将 `decision=new` 的 `ku_id` 写为该 KU。
- backlog `bl-0001` 已从等待 S4 更新为 `completed`，填写 KU；这只关闭端点登记待办。关联正式关系仍待 S6 审查，没有新增 `relations.csv` 边。

### procedure 类型批次（2026-10-15）

- 按类型完成全部23个当前 `new` 身份组，登记23张 KU；24条成员候选均已映射。19个身份组出现在 S2 断言端点中，含上述 Zanetti 两候选合并组。
- 每张卡均写入双语标题、语义对应的中英文描述、具体章页来源、句意摘要、原文摘录及文件行定位；书中概括、归属限定和 OCR 异读保留为限定。该批没有外部身份检索，也没有写入 `enrichment.jsonl` 或正式关系；卡片描述仅覆盖登记所需的书内事实。
- 卡片与对齐映射的可复现批次定义见[procedure 批次登记脚本](register_s4_procedure_batch_20261015.py)。`--dry-run` 核对23组、24条候选、S3组号、卡片路径及每条引文可在来源文件中定位后通过；`--apply` 写入23张卡、manifest、accepted.yml 和对应对齐映射。

### family：Barberini（2026-10-15）

- 候选：`cand-0198`（索引家族项）与 `cand-3464`（第1章正文的 ruling-clan 指称）；跨章复核确认两者指向同一集体家族，均保留 `new` 并归入 `sg3-family-barberini`。
- 依据：第1章印刷页15将 Barberini 与 Borghese 并列为大规模赞助能力的 ruling clans 例子。描述仅覆盖书中该集体身份及赞助语境，不推断谱系、支系或成员。既有 Barberini household 为 institution，保持类型边界。
- 新 KU：`units/families/barberini-family`；已加入 `ku-manifest.csv` 与 `accepted.yml`，`aln-0533`、`aln-3649` 均映射至同一 KU。未新增关系或 S5 补足。

### 家族候选跨章复核与登记（2026-10-15）

- `cand-4729` 的第2章 Borghese 集体指称复用 `units/families/borghese-family`；`cand-4742` 的 Aldobrandini 集体指称复用 `units/families/aldobrandini-family`。两条对齐决定由 `new` 更正为 `same`，未新增重复 KU。
- `cand-6329`（第6章对亚历山大七世亲属的叙述）与 `cand-6484`（第162页“or a Chigi”）合并为 `sg3-family-chigi`，登记一张基吉家族 KU。`cand-7489` 与 `cand-8078` 合并为 `sg3-family-del-rosso-florence`：第211页列出 Del Rosso 商人家族及兄弟，第241页再次称佛罗伦萨展览中的 del Rosso brothers；卡片保留集体出借陈述，不指定个人。
- `cand-7368` 的 Naples “Colonnas” 与既有 Colonna family KU 之间缺少支系或同一性依据。该候选由 `new` 更正为 `undecided`，保留 `sg3-review-colonna-family-branch`，待书内或适用权威证据说明家族范围后再决定复用或另立。
- 第8章第203页同段中的 Genoa 11 个、Naples 4 个、Bologna 6 个 family 组共登记21张卡；连同 Chigi、Del Rosso 两组，本批登记23组、映射25条候选。`cand-7361` 保留 OCR `Imperial!` 与印刷扫描读法 `Imperiali` 的区别；`cand-7372` 保留 Tarsia Spinellis 的跨行 OCR 形态。批次不新增 enrichment 或正式关系。
- 上述8项跨章候选调整与23组登记由[family 批次脚本](register_s4_family_batch_20261015.py)执行。`--dry-run` 逐条检查组成员、来源引文、卡路径及登记外键后通过，再以 `--apply` 写入卡片、manifest、accepted.yml 与候选映射。

### family：第2—3章批次（2026-10-15）

- 完成15个独立 `new` 家族组、15条候选映射：第2章8组（Orsini、Este、Ludovisi、Sforza、Della Rovere、Bentivoglio、Lante、Altemps）；第3章7组（Farnese、Caetani、Mellini、Cesi、Mignanelli、Medici、Savelli）。每张卡只保留对应段落支持的家族层级描述，明确与同姓人物、建筑或不确定支系的边界。
- Mellini 卡保留 OCR `Meliini` 与候选记录所载印刷扫描读法 `Mellini`；Medici 候选只记录第3章对该家族赞助身份的集体指称。批次无外部身份检索、无 enrichment 写入、无正式关系新增。
- [第2—3章 family 批次脚本](register_s4_family_ch2_ch3_batch_20261015.py)的 `--dry-run` 核对15条候选组号、卡路径及原文引文后通过，再以 `--apply` 写入15张卡、manifest、accepted.yml 和对齐映射。

### family：第9章及后记批次（2026-10-15）

- 完成8个独立 `new` 家族组、9条候选映射：Corner（2条候选）、Giustiniani、Grassi、Labia、Manin、Soderini、Widmann、Zenobio。9条候选均作为 S2 断言端点出现；每组仅登记一张 family KU。
- 复核了候选表中的同名 family 记录和现有 family manifest，没有发现这8组对应的已登记同名 family KU。`cand-8780` 的 Manini brothers 与 Manin 家族拼写相似，但其候选仍为 `undecided`，不据此并组或映射。
- Zenobio 候选的第9章正文、注释及后记材料均指向书中同一集体家族；Soderini 卡保留索引拼写 `Soderini` 与正文 OCR `Sodcrini` 的差异，不冒称扫描校勘。Labia、Widmann 的第8章视觉转录注释作为跨章依据保留。
- 所有卡片均含双语名称、等义描述、书内章页定位、原文摘录及候选范围限定；本批未新增外部核验、enrichment 或正式关系。
- [第9章 family 批次脚本](register_s4_family_ch9_batch_20261015.py)的 `--dry-run` 核对8个组、9条候选、S2 端点、卡路径和原文引文后通过，再以 `--apply` 写入8张卡、manifest、accepted.yml 与对齐映射。

### family：第7—8章批次（2026-10-15）

- 登记 Liechtenstein、Crescenzi、Gondi、Wittelsbach、Cibo、Bibbiena 六个独立 `new` 家族组，映射6条候选；六条候选均为 S2 断言端点。
- 卡片仅记原书支持的家族身份、赞助或前持有方语境。Gondi 家族与候选 `cand-1212` 所指宫殿分开；Cibo 的宫殿转手不推断具体出售者；Crescenzi 兄长姓名不详，未补写；Wittelsbach 与 Savoy 的婚姻联盟只按原书陈述保留。
- 六张卡均含双语名称、等义描述、章页与行定位、原文摘录及边界说明；没有新增外部核验、enrichment 或正式关系。
- [第7—8章 family 批次脚本](register_s4_family_ch7_ch8_batch_20261015.py)的 `--dry-run` 核对6个组、6条候选、S2 端点、卡路径及原文摘录后通过，再以 `--apply` 写入6张卡、manifest、accepted.yml 与对齐映射。

### family：第5章批次（2026-10-15）

- 登记 Corsini、Salviati、Rospigliosi 三个独立 `new` 家族组，映射3条候选；三条候选均为 S2 断言端点。
- 第5章称 Corsini 与 Salviati 是 Cerquozzi 的热心欣赏者，未称其为委托人。Corsini 礼拜堂另见第8章；书中只是推测 del Rosso 兄弟可能促成 Luca Giordano 的委托，卡片保留该限定。Rospigliosi 候选只记1668年展览组织及其原书语境，不补写四名儿子的姓名或新增正式关系。
- [第5章 family 批次脚本](register_s4_family_ch5_batch_20261015.py)的 `--dry-run` 核对3个组、3条候选、S2 端点、卡路径和原文引文后通过，再以 `--apply` 写入3张卡、manifest、accepted.yml 与对齐映射。

### family：第9、15、17章批次（2026-10-15）

- 登记 Collalto、Farsetti、Molin、Orsetti 四个独立 `new` 家族组，映射4条候选；四条候选均为 S2 断言端点。
- Collalto 卡将第254页“Novelli 记录家族伟大”与第255页的回忆录转述一并引用。Farsetti 卡限于 Filippo 的出生家族及书中财富、贵族身份叙述，并与 Filippo 人物 KU 分开；候选索引页码为 p.362，而对应正文文件页眉标为 p.302，当前卡按可定位的正文来源 p.302 引用，页码差异保留，不改写来源或候选索引。Molin 与 Orsetti 卡保留第17章对 Correr 藏品“来自家族”的宽泛说法，不将其改写成赠与、借展或确认的产权链。
- [第9、15、17章 family 批次脚本](register_s4_family_ch9_ch15_ch17_batch_20261015.py)的 `--dry-run` 核对4个组、4条候选、S2 端点、卡路径及原文摘录后通过，再以 `--apply` 写入4张卡、manifest、accepted.yml 与对齐映射。

### family：第6、7、10章批次（2026-10-15）

- 登记 Schönborn、House of Savoy、Hanoverian dynasty 三个独立 `new` 家族组，映射3条候选；均为 S2 断言端点。
- Schönborn 候选连接第6、7、10章：第10章称“whose vast patronage has already been referred to”，据此保留同一书内家族指称。正文 OCR 形式 `Schônborn`、`Schonborn` 与索引形式 `Schönborn` 并存，卡片逐条保留原文。House of Savoy 与地理候选 Savoy 分开；Hanoverian 亲属关系只记到王朝层级，不补写具体亲属。
- House of Savoy 与 Hanoverian 的候选过程定位页为311，但 OCR 页码标记 L7 读作 `1661`；卡片保留原文定位行、候选页码和标记异读，不将其静默改写为扫描页校勘。
- [第6、7、10章 family 批次脚本](register_s4_family_ch6_ch7_ch10_batch_20261015.py)的 `--dry-run` 核对3个组、3条候选、S2 端点、卡路径及原文摘录后通过，再以 `--apply` 写入3张卡、manifest、accepted.yml 与对齐映射。

### Valmarana 跨章端点簇：逐类型登记（2026-10-15）

- family：登记 Altieri、House of Brunswick、Mantua 语境的 Gonzaga、Valmarana、Zambelli 五组并映射5条候选。Gonzaga 的索引重定向 `cand-2906` 继续保持 S1 `excluded`，不映射到 family KU；Brunswick 的 p.366 与 OCR `[Page 66]` 页标差异保留。Zambelli 卡仅记录 p.260 注8 的集体称谓及 Moschini 引证，不并入 Dottoressa Paola Zambelli 人物。
- work：登记 `cand-2594` 为 Tiepolo 的 Valmarana 别墅壁画组，使用描述性暂题；p.258 与 p.405 的证据指向同一作品组。卡片保存后记对委托人的更正，不拆出单幅壁画，不推定画名、技法或存世状态。
- person：登记 Leonardo Valmarana 与 Conte Giustino Valmarana 两组。前者只保留 p.258“似为家族首领”的限定，后记仅更正其非该壁画委托人；后者按 p.405 对 Puppi 的转述登记为委托人，论文未独立查阅。
- place：登记 Villa Valmarana 与 Vicenza 两组。别墅卡保留书内地点称谓，不推断更精确建筑群；Vicenza 卡以 p.258、p.348、p.405 的跨章用例确认同一城市，未补坐标或现代行政范围。
- [Valmarana 跨章簇登记脚本](register_s4_valmarana_cluster_batch_20261015.py)逐类型运行 `--dry-run` 后再 `--apply`；每类核对 S3 组号、直接 S2 端点/提及、来源摘录、卡路径及全部既有映射组的闭合。四类共新增10张 KU 卡，映射10条候选；manifest 从1,106增至1,116。未新增 enrichment 或 formal relations；相关 S2 断言仍待 S6。

### family：剩余六组有书内段落依据的登记（2026-10-15）

- 登记 Contarini（`cand-0824`，p.255）、Morosini（`cand-1706`，p.250）、Pesaro（`cand-8177`，p.249）、Loredan（`cand-8386`，p.256）、Bonfiglioli（`cand-8589`，p.263 注5）与 Venier（`cand-10674`）六个独立 `new` 家族组，映射6条候选。卡片保留来源引文、书内语境和不扩展支系/成员/产权链的边界；中文名采用音译，不宣称为权威规范名。
- Bonfiglioli 只登记注释所称家族，不独立核验其引述的 Bottari 或将购藏叙述转为正式关系。Venier 段落 OCR L8 页标仅作 `[Page 3]`、L22 为 `[Page 381]`，卡片暂定位 p.380 并明示待页图复核；不将家族并入人物 Leonardo Venier。
- [剩余六组 family 批次脚本](register_s4_family_remaining_clear_batch_20261015.py)的 `--dry-run` 核对组号、候选决定、S2 提及/断言覆盖、卡路径及原文摘录通过后，再以 `--apply` 写入6张卡、manifest、accepted.yml 与候选映射。manifest 从1,116增至1,122；本批未新增外部核验、enrichment 或正式关系。

### person：跨章直接端点优先登记（2026-10-15）

- 登记 Johann Matthias Schulenburg（`cand-2401`，组 `new-person:johann-marshal-matthias-schulenburg-240303b710`）。候选在第9、10、13、20章有同一全名/明确别称锚点，S2 中为高频关系端点；本批只映射该单候选，不把姓氏相似项并入。
- 卡片以第10章正文全名作身份锚，第9章 p.267 的 Castiglione 收藏记述及第20章 p.407 对其收藏研究的回顾作跨章语境。候选索引定位 p.311 与 OCR 页标 `[Page 1661]` 的不一致已在卡内标明待页图复核；不将其军事经历或收藏事实描述为外部已核。
- [Schulenburg person 批次脚本](register_s4_person_schulenburg_batch_20261015.py)的 `--dry-run` 核对 `new` 组、S2 断言端点、卡路径和三处原文摘录后通过，再以 `--apply` 登记1张卡、manifest、accepted.yml 与1条候选映射；manifest 从1,122增至1,123。未新增外部核验、enrichment 或正式关系。

### person：Angelo Querini 跨章直接端点登记（2026-10-16）

- 登记 `cand-2075`，S3 组 `new-person:angelo-querini-angelo-querini-s-2a00c0b28f`。第10章 p.320 将 Querini 列作 Lodoli 的威尼斯交往者；第15章 p.368–369 以其全名为专节，书内身份和跨章端点清楚。
- 卡片以第10章和第15章原文摘录支撑双语身份描述，只保留 Haskell 对其赞助、政治活动与文化生活的书内叙述。没有补外部传记或正式关系；S2 的赞助和交往断言仍待 S6。
- [Angelo Querini person 批次脚本](register_s4_person_angelo_querini_batch_20261016.py)的 `--dry-run` 核对 `new` 组、S2 断言端点、卡路径和三处原文摘录后通过，再以 `--apply` 登记1张卡、manifest、accepted.yml 与1条候选映射；manifest 从1,123增至1,124。未新增外部核验、enrichment 或正式关系。

### person：Tommaso Ruffo 直接端点登记（2026-10-16）

- 登记 `cand-2304`，S3 组 `new-person:ruffo-tommaso-362bd882fa`，映射至 `units/persons/tommaso-ruffo`。该候选在第8章 p.221–223 的 S2 断言中作为直接端点出现59次。
- 第8章 p.221 OCR 正文将 Cardinal Tommaso 的姓多处记作 Russo，但同页接续文字改用 Ruffo；p.224 后注引 Biblioteca Ariostea 手稿题名，明确写作 Cardinal Tommaso Ruffo。卡片按同一连续人物叙述登记，保留正文与注释的拼写差异，并以中文音译作显示名；双语描述只概括书内生平、任职与赞助语境。
- `cand-2305`（and Donato Creti）与 `cand-2308`（Neapolitan paintings）是无 S2 正文提及的索引子目，仍为 `undecided`，未凭子目或页码映射。没有外部核验；S2 作品、委托和任职断言仍待 S6，本卡未新增正式关系。
- [Tommaso Ruffo 人物卡](../../../04-knowledge/units/persons/tommaso-ruffo.md)由[批次脚本](register_s4_person_tommaso_ruffo_batch_20261016.py)的 `--dry-run` 核对组成员、59条直接端点、拼写证据、卡路径和精确原文摘录后，通过 `--apply` 登记入 manifest 与 accepted.yml，并映射1条候选；manifest 从1,124增至1,125。未新增 enrichment 或正式关系。

### person：Paolo Giordano II Orsini 跨章直接端点登记（2026-10-16）

- 将跨第4、19、20章的 `cand-0428` 与 `cand-0434` 共组登记为 `units/persons/paolo-giordano-ii-orsini`，映射2条候选；两者在 S2 断言中共出现73次。
- 第4章 p.95 直接给出 Paolo Giordano II Orsini 全名和布拉恰诺公爵身份；第19章 p.387 附录2标题将 Paolo Giordano Orsini 与 Bernini、Tacca 委托文件相连，并指回第4章；第20章 p.401 再用全名提及青铜半身像。后记同时报告该像归于 Bernini 的理由受到质疑，卡片保留此限定。
- 与既有 Paolo Giordano I 人物卡分开，罗马数字表明代际不同；与仍未具名且保留 Ferdinando/Flavio 两代候选的 Mulier 赞助人卡分开。本批不查询外部来源、不补生平，也不把 S2 委托或作者归属改成正式关系。
- [Paolo Giordano II Orsini 人物卡](../../../04-knowledge/units/persons/paolo-giordano-ii-orsini.md)由[批次脚本](register_s4_person_paolo_giordano_ii_orsini_batch_20261016.py)的 `--dry-run` 核对2条组成员、73条直接端点、代际边界和4处原文摘录后，通过 `--apply` 登记至 manifest 与 accepted.yml，并映射2条候选；manifest 从1,125增至1,126。未新增 enrichment 或正式关系。

### person：Joseph Smith 跨章直接端点登记（2026-10-16）

- 将 `cand-2440`、`cand-2442`、`cand-2443`、`cand-2447`、`cand-2468` 组成的 `new-person:joseph-m-smith-joseph-smith-de20176f48` 登记为 `units/persons/joseph-smith-venice`，映射5条候选；这些候选在 S2 断言中共出现194次。
- 第10章 p.299 以“CONSUL JOSEPH SMITH”为题，称其为英国人和当时重要艺术赞助人，记述其约1675年出生、18世纪初迁居威尼斯从事商贸，并记其于1744年成为英国领事。第9章 p.264 再以全名与领事身份将其置于 Sagredo 继承人售画语境；第19章附录5讨论 Consul Smith 与皇家收藏，p.394 目录又出现 Joseph Smith, Esq. 与威尼斯领事称谓。
- 五条索引候选分别指向其传记、与 McSwiny 及 Rosalba Carriera 的关联、Sagredo 购藏和皇家收藏。现有 manifest 与人物卡中没有同名 Joseph Smith KU；本卡仅登记书内人物身份与来源限定描述，不补外部生平，不将作品购买、委托、收藏及交往写成正式关系，相关 S2 断言待 S6 审查。没有外部查询。
- [Joseph Smith 人物卡](../../../04-knowledge/units/persons/joseph-smith-venice.md)由[批次脚本](register_s4_person_joseph_smith_batch_20261016.py)的 `--dry-run` 核对5条组成员、194条直接端点和5处原文摘录后，通过 `--apply` 登记到 manifest 与 accepted.yml，并映射全部5条候选；manifest 从1,126增至1,127。未新增 enrichment 或正式关系。

### person：Gian Paolo Oliva 跨章直接端点登记（2026-10-16）

- 将 `cand-1771` 与 `cand-1775` 组成的 `new-person:gian-oliva-paolo-b799139c04` 登记为 `units/persons/gian-paolo-oliva`，映射2条候选；组内候选在 S2 断言中共出现56次。
- 第3章 p.64 以全名称 Oliva 为 Jesuit，并称其为 Bernini 的亲密且有影响的朋友；p.88 记 General Oliva 于1680年召 Andrea Pozzo 到罗马，并称 Pozzo 抵达时 Oliva 已去世；p.91 继续叙述 Oliva 任总会长期间推动圣依纳爵纪念工程。第6章 p.153 再以耶稣会总会长身份提到 Oliva。
- 两条索引候选的全名相同，cand-1775 的 “and Gaulli” 子目与第3章同一叙事相接；无同名已登记人物 KU。本卡只登记书内人物身份，不补外部生平，不将友谊、召请或工程意向写为正式关系；相关 S2 关系候选仍待 S6 审查。
- [Gian Paolo Oliva 人物卡](../../../04-knowledge/units/persons/gian-paolo-oliva.md)由[批次脚本](register_s4_person_gian_paolo_oliva_batch_20261016.py)的 `--dry-run` 核对2条组成员、56条直接端点和5处原文摘录后，通过 `--apply` 登记至 manifest 与 accepted.yml，并映射全部2条候选；manifest 从1,127增至1,128。未新增 enrichment 或正式关系。

### person：Rosalba Carriera 跨章直接端点登记（2026-10-16）

- 将 `cand-0581`、`cand-0585`、`cand-0586`、`cand-0588` 组成的 `new-person:carriera-rosalba-f0a77ca508` 登记为 `units/persons/rosalba-carriera`，映射4条候选；这些候选在 S2 断言中共出现49次，涉及第8、9、10、13章。
- 第10章 p.276 以全名介绍其绘鼻烟盒和象牙微型画、转向粉彩肖像的经历；第8章 p.228 记其为 Emmanuela Conti 绘肖像，第9章列其粉彩与微型画价格，第10章 p.303 记 Smith 在20年代委托她作画。书中还有 Camera 拼法；第8章该姓名 OCR 作 Garriera，均保留为来源形式。
- 四条候选分属人物索引主词及肖像、价格、Smith 委托子目；没有同名既有 KU。本卡仅登记身份和来源限定语境，不将客户、委托、作品或交往写成正式关系，不作外部核验。
- [Rosalba Carriera 人物卡](../../../04-knowledge/units/persons/rosalba-carriera.md)由[批次脚本](register_s4_person_rosalba_carriera_batch_20261016.py)的 `--dry-run` 核对4条组成员、49条直接端点和4处原文摘录后，通过 `--apply` 登记至 manifest 与 accepted.yml，并映射全部4条候选；manifest 从1,128增至1,129。未新增 enrichment 或正式关系。

### person：Filippo Farsetti 跨章直接端点登记（2026-10-16）

- 将 `cand-1002` 的 `new-person:farsetti-filippo-farsetti-filippo-h-n-a027772c3f` 组登记为 `units/persons/filippo-farsetti`，映射1条候选。该候选在 S2 断言中出现48次，涉及第10、15章；第16章的索引提及另提供 patronage 语境。
- 第15章正文页标 p.302 以全名介绍其出生、成为 Padre Lodoli 学生、旅行、巴黎居住及转为 abate 后投入艺术；pp.363–364 讨论其收藏、对当代艺术和威尼斯新古典主义的影响，同时称其仍是了解有限的人物。候选索引将首段标为 p.362，沿用既有 Farsetti family 卡的做法，正文卡按可定位页标 p.302 引用并记录差异。第10章候选索引 p.322（正文 OCR 页标 `[Page 22]`）列其为 Lodoli 仰慕者，第16章索引 p.373（正文 OCR 页标 `[Page 2]`）将其与显赫 patronage 比较。
- Filippo 人物 KU 与既有 `units/families/farsetti-family` 集体卡分开；第15章亦将堂亲 Daniele 与 Filippo 区分。书中明确说其收藏时间与个人目标仍不完全清楚，因此卡片不补写收藏编年、未指明作品或家谱。相关师承、赞助、收藏和艺术影响仍待 S6 关系审查；本卡没有正式关系，也未作外部核验。
- [Filippo Farsetti 人物卡](../../../04-knowledge/units/persons/filippo-farsetti.md)由[批次脚本](register_s4_person_filippo_farsetti_batch_20261016.py)的 `--dry-run` 核对1条组成员、48条直接端点、与 family KU 的类型边界和5处原文摘录后，通过 `--apply` 登记至 manifest 与 accepted.yml，并映射该候选；manifest 从1,129增至1,130。未新增 enrichment 或正式关系。

### person：Taddeo Barberini 跨章直接端点登记（2026-10-16）

- 将 `cand-0239` 的 `new-person:barberini-taddeo-2a827b7370` 组登记为 `units/persons/taddeo-barberini`，映射1条候选。该候选在 S2 断言中出现42次，涉及第2、6章。
- 第2章 pp.31–32 称 Taddeo 为 Antonio 的兄弟、教皇乌尔班八世的侄子，并提及其与 Anna Colonna 的婚姻；pp.47–48 记其政治职位、1631年罗马长官职衔及其对艺术的有限兴趣。第6章 p.146 在卡斯特罗战争段落再次称其为总司令，并评价其指挥表现。人物专属检索未发现对应现有 person KU；Barberini family 卡及 Antonio Barberini 卡不替代本人卡。
- 卡片保留书内身份与限定叙述，不从“其父担任 papal armies 最高统帅”推定父亲姓名，也不把婚姻、亲属、任职或军事叙述写成正式关系；这些断言仍待 S6。未作外部核验或 S5 补足。
- [Taddeo Barberini 人物卡](../../../04-knowledge/units/persons/taddeo-barberini.md)由[批次脚本](register_s4_person_taddeo_barberini_batch_20261016.py)的 `--dry-run` 核对1条组成员、42条直接端点、无同名现有人物 KU 及5处原文摘录后，通过 `--apply` 登记至 manifest 与 accepted.yml，并映射该候选；manifest 从1,130增至1,131。未新增 enrichment 或正式关系。


### person：Jacques Courtois／Giacomo Borgognone 登记（2026-10-16）

- `cand-0399` 为独立新人物组 `new-person:borgognone-giacomo-courtois-jacques-e79bfdac5a`；第3章 pp.78–79 明确记录 Jacques Courtois 与意大利名 Giacomo Borgognone 的对应及其加入耶稣会，p.79 说明他与兄弟 Guglielmo 为 Oliva 作画。
- [人物卡](../../../04-knowledge/units/persons/jacques-courtois.md)据此登记双语名称、书内描述、引文和身份边界；与 Guglielmo Cortese KU 分开。`cand-0400` 未因同一索引主项自动映射，仍为 `undecided`。本组有40条 S2 断言端点，其中37条为关系候选，均留待 S6，不在 S4 建正式关系。
- [S4 批次脚本](register_s4_person_jacques_courtois_batch_20261016.py)的 `--dry-run` 核对组成员、40条端点、37条关系候选、原文引句及 KU 外键后通过；`--apply` 登记1张卡、manifest、accepted.yml 和1条候选映射。manifest 从1,131增至1,132；全书已登记113组、128条候选映射。未增加外部核验、enrichment 或正式关系。

### person：Francesco Borromini 跨章登记（2026-10-16）

- `cand-0404`（主索引）、`cand-0406`（and Pope Innocent X）与 `cand-0407`（Scalzi church in Rome）均有指向 Francesco Borromini 的 S2 正文锚点，归入 `new-person:borromini-francesco-685a6ddd7c`，登记为一张 KU。三条候选共有33条断言端点，其中31条是关系候选。
- 原 `04-knowledge/units/persons/francesco-borromini.md` 未列入 accepted.yml 或 manifest，属于未登记旧稿，不能据其存在裁为 `same`。本批核对第2章 p.48、第3章 pp.75–76及第6章 pp.147–149后，在固定路径改写为当前双语人物卡，并加入 manifest/accepted.yml；不另建重复路径。
- [S4 批次脚本](register_s4_person_borromini_batch_20261016.py)的 `--dry-run` 核对三条组成员、33条端点、31条关系候选、旧稿未登记状态、来源引句及 KU 外键后通过；`--apply` 完成一组一卡及三条候选映射。manifest 从1,132增至1,133；全书已登记114组、131条候选映射。未增加外部核验、enrichment 或正式关系。

### person：Count Carl Gustav Tessin 跨章直接端点登记（2026-10-16）

- `cand-2552`（主索引）、`cand-2553`（and Tiepolo）和 `cand-2554`（and A. M. Zanetti the Elder）归入 `new-person:carl-gustav-tessin-aa1ed44d34`，登记为一张人物 KU。第10章 pp.292–293 记其为瑞典人、1695年出生、驻法大使及巴黎收藏；第13章 pp.341–342 将 Swedish Count Tessin 置于 Zanetti 的威尼斯交游与收藏语境。索引全名 Count Carl Gustav Tessin 与两章正文中的 Count Tessin / Swedish Count Tessin 相互对应。
- [Count Carl Gustav Tessin 人物卡](../../../04-knowledge/units/persons/carl-gustav-tessin.md)以索引全名作显示名，同时保留正文简称和不把父亲、Zanetti、Tiepolo 或 protégé 混入身份的边界。三个候选共有34条唯一 S2 断言端点，其中28条为关系候选，均待 S6；未新增正式关系、`enrichment.jsonl` 字段或外部身份核验。
- [Tessin S4 批次脚本](register_s4_person_carl_gustav_tessin_batch_20261016.py)的 dry-run 核对3条组成员、34条端点、28条关系候选、来源引句及 KU 外键后通过；apply 登记一组一卡并映射3条候选。manifest 从1,133增至1,134；登记累计115组、134条候选映射。三条 S3 复用裁决不改变该登记计数。

### person：Girolamo Manfrin 跨章直接端点登记（2026-10-16）

- `cand-1512` 是索引 `M.csv#49` 的单成员新人物组 `new-person:girolamo-manfrin-girolamo-manfrin-s-c3ddada91a`，索引页379、380、381、410。对照当前人物 manifest、accepted 路径及人物名称未发现对应 Manfrin KU；Venier 家族及其宫邸/乡间别墅候选不等于 Manfrin 本人。
- 第17章 pp.379–381 记述其威尼斯赞助与收藏活动：1785年 Tiepolo 版画奉献给他；其画廊有四百余幅画作；他组织画家围绕自拟题材举行竞赛。第20章 p.410 后记称藏品一度包括 Giorgione 的《暴风雨》，并明确说其作品来源仍所知甚少。人物卡只记录上述书内范围，不将评论性人格刻画当作已核验事实，也不把藏品、竞赛题材或单件作品并入人物身份。
- [Girolamo Manfrin 人物卡](../../../04-knowledge/units/persons/girolamo-manfrin.md)采用原书全名作英文规范名，中文名为工作音译。`cand-1512` 有40条唯一 S2 断言端点，其中20条为关系候选；所有关系候选仍待 S6，无正式关系或补足字段在本批新增。
- [Manfrin S4 批次脚本](register_s4_person_girolamo_manfrin_batch_20261016.py)的 dry-run 核对既有人物 KU/固定路径、单成员组、40条端点、20条关系候选、5处原文引句及映射外键后通过；apply 登记一组一卡并映射该候选。manifest 从1,134增至1,135；登记累计116组、135条候选映射。

### person：Ferrante Carlo 跨章直接端点登记（2026-10-16）

- `cand-0560`（索引 `C.csv#84`，Carlo, Ferrante）与 `cand-10983`（第20章后记正文提及 Ferrante Carlo）归入 `new-person:carlo-ferrante-cb229cd01f`，登记为一张人物 KU。第5章 p.123 明称 Ferrante Carlo，记其1578年生于帕尔马、为律师与诗人、先后任两位枢机的秘书，并述其收藏及与画家的往来；第20章 p.402 明称 Bellori 关于 Lanfranco 的一些评论源自 Ferrante Carlo 的写作，并回指作者第5章对该人物的叙述。原文全名、索引倒置名及后记回指支持同一人物，不仅依据姓氏相似。
- [Ferrante Carlo 人物卡](../../../04-knowledge/units/persons/ferrante-carlo.md)保留原文名序、索引名序和工作中文音译；后记对 Nicholas Turner 的转述注明未独立查阅该研究。两条候选共有36条唯一 S2 断言端点，其中24条为关系候选，仍待 S6；本批未新增正式关系。
- [Ferrante Carlo S4 批次脚本](register_s4_person_ferrante_carlo_batch_20261016.py)的 dry-run 核对两条成员候选、单一既有分组、人物卡路径、36条端点、24条关系候选、原文引句及映射外键后通过；apply 登记一组一卡并映射两条候选。manifest 从1,135增至1,136；登记累计117组、137条候选映射。

### person：Antonio Conti 索引交叉子目组登记（2026-10-16）

- `cand-0826`–`cand-0830` 对应索引 `C.csv#356–360`：人物主项及 Francesco Algarotti、Sir Isaac Newton、绘画中的想象力和 Royal Society 交叉子目；五条候选均属于第10章 pp.318–320 连续叙述中的 Antonio Conti，归入 `new-person:antonio-conti-b4d2c59e45`，登记为一张人物 KU。
- 第10章 pp.318–320 记述其贵族出身、赴巴黎与伦敦、结识 Newton、1726年返威尼斯、1749年去世、对 Algarotti 的影响及其绘画观。索引子目“election to Royal Society”不覆盖正文的限定：正文只说 Newton proposed Conti；来源 OCR 在该句后续有 U+FFFD 置换符，卡片仅摘录可清晰定位的前半句，并明确不称 Conti 实际当选。跨行引文按来源原始换行保留。
- [Antonio Conti 人物卡](../../../04-knowledge/units/persons/antonio-conti.md)只记录本书陈述及明确边界，未作外部身份核验；五条候选共有36条唯一 S2 断言端点，其中19条为关系候选，均留待 S6，本批未新增正式关系或补足字段。
- [Antonio Conti S4 批次脚本](register_s4_person_antonio_conti_batch_20261016.py)的 dry-run 核对五条成员候选、索引子目、无既有人物 KU、36条端点、19条关系候选、五处精确引文及映射外键后通过；apply 登记一组一卡并映射五条候选。manifest 从1,136增至1,137；登记累计118组、142条候选映射。

### person：Augustus III of Poland 跨章身份组登记（2026-10-16）

- `cand-0148`（`A.csv#149` 主项）、`cand-0149`（`A.csv#150`，F. Algarotti）、`cand-0151`（`A.csv#152`，Dresden Gallery）与 `cand-0152`（`A.csv#153`，摩德纳公爵收藏作品）有 S2 正文锚点，归入 `new-person:augustus-iii-of-poland-1d39936dba`，登记为一张人物 KU。第10章 p.277 明确将萨克森选帝侯与后来波兰国王 Augustus III 对应；第10章 p.294 记其为 Augustus II 之子、1733年继位者及其购藏；第14章 p.349 记 Algarotti 于1742年为萨克森选帝侯 Augustus 工作、1743年为国王购画，形成跨章语境支持。
- 相邻 `cand-0150`（`A.csv#151`，and Rosalba Carriera）没有 S2 正文提及，S3 保持 `undecided`；本卡不映射该候选，也不由索引子目推定其身份或关系。卡片区分 Augustus III 与其父 Augustus II，未发现既有 Augustus III 人物 KU；未做外部身份核验。
- [Augustus III 人物卡](../../../04-knowledge/units/persons/augustus-iii-of-poland.md)限于书内身份、标题变迁和收藏语境，不扩写外部生平。四条成员候选共有31条唯一 S2 断言端点，其中26条为关系候选，均留待 S6；本批未新增正式关系或补足字段。
- [Augustus III S4 批次脚本](register_s4_person_augustus_iii_batch_20261016.py)的 dry-run 核对四条组成员、相邻待证候选、无既有人物 KU、31条端点、26条关系候选、四处精确引文及映射外键后通过；apply 登记一组一卡并映射四条候选。manifest 从1,137增至1,138；登记累计119组、146条候选映射。

### person：Pietro Longhi 跨章身份组登记（2026-10-16）

- `cand-1429`（`L.csv#86` 主项）、`cand-1430`（`L.csv#87`，Carlo Goldoni and）与 `cand-1433`（`L.csv#90`，Teodoro Correr 收藏）具有跨章 S2 正文/注释锚点，归入 `new-person:longhi-pietro-fbe3e4f111`，登记为一张人物 KU。第10章明确称 Pietro Longhi 为画家，第13章称 Remondini 推广其作品，第17章记其在 Correr 收藏中的位置；第15章与第17章均提到 Alessandro Longhi 是其子，支持两名人物的区分。
- 第10章 p.323 注释续文说 Paoletti 把画家称作“Antonio”Longhi，Haskell 随即评价该来源不完全可靠；既有 S2 迁移已把这条称呼作为来源异文，而非第二人物或可靠别名。卡片保留此限定。第19章后记列出1776年售画目录中的 Longhi 作品，但同段说明目录及归属不可视为定论，本卡不把它提升为确证。
- 相邻 `cand-1431`（Fall of the Giants）、`cand-1432`（Gasparo Gozzi and）和 `cand-1434`（two conversations, Mr Murray and family）继续保留既有 `undecided` 决定，没有映射到本卡。未发现 Pietro Longhi 既有人物 KU；本批未作外部身份核验。
- [Pietro Longhi 人物卡](../../../04-knowledge/units/persons/pietro-longhi.md)记录其书内绘画活动与评价，本批未新增正式关系。三条成员候选共有29条唯一 S2 断言端点，其中20条为关系候选；均留待 S6。批次 dry-run 核对三条成员、三条邻接待证决定、29条端点、20条关系候选、六处精确引文和映射外键后通过；apply 登记一组一卡并映射三条候选。manifest 从1,138增至1,139；登记累计120组、149条候选映射。脚本：[Pietro Longhi S4 批次脚本](register_s4_person_pietro_longhi_batch_20261016.py)。

### S3：Owen McSwiny 复用前置材料既有人物 KU（2026-10-16）

- 全书候选 `cand-1466`（`M.csv#3`）以 Owen McSwiny 为主项，正文 p.287 具名介绍其生平和艺术方案，并在第20章后记 pp.405–406 再次以全名指称同一计划。前置材料已有 accepted/manifest 人物 KU `units/persons/owen-mcswiny`，英文规范名为 Owen MacSwinny；其图版52a肖像卡和既有 S3 候选 `cand-3853` 指向同一人物。
- 同册图版目录写 Owen McSwiny，肖像视觉转录写 Owen McSwiney；既有卡记录 NPG 名称 Owen MacSwinny (or Swinny)。第10章注释又说明 McSwiny 在不同生涯阶段有多种姓名拼写。相同的 Plate 52a 肖像、全书明确姓名和原书拼写说明足以将 `cand-1466` 从 `new` 更正为 `same`，并加入既有组 `sg3-ku-units-persons-owen-mcswiny`。该映射复用既有来源记录；本轮没有新增外部来源，也不重建人物卡。
- `cand-1466` 的28条唯一 S2 断言端点中16条为关系候选，仍待 S6。相邻 `cand-1467`–`cand-1472`、`cand-1474` 保持既有 `undecided`；`cand-1473` 是独立 pamphlet archive `new` 组，不并入人物 KU。
- [S3 复用裁决脚本](reconcile_s3_owen_mcswiny_existing_identity_20261016.py)的 dry-run 核对既有卡/manifest/accepted 路径、`cand-3853` 的既有 `same` 映射、图版和原书拼写证据、28条端点、16条关系候选及邻接候选状态后通过；apply 仅将 `cand-1466` 从 `new` 改为 `same` 并映射至既有 KU。manifest 和 accepted.yml 未变；4,989条 `new` 候选现分为4,820组，S4 已登记的120组、149条成员映射不变，未登记余4,700组、4,840条候选。

### S3：Caravaggio 四条人物索引候选复用既有人物 KU（2026-10-16）

- `cand-0544`（C.csv#68 主项）、`cand-0545`（#69，Vincenzo Giustiniani）、`cand-0547`（#71，《圣母之死》）与 `cand-0549`（#73，《基督下葬》）均以同一主项“Caravaggio, Michelangelo da”编入索引，正文锚点跨第1—5章及后记。第2章 p.25 明称 “Michelangelo da Caravaggio”；第3章 p.70 将《基督下葬》归给 Caravaggio；第5章 p.125 将《圣母之死》归给 Caravaggio。
- manifest/accepted 已有 `units/persons/caravaggio`，卡片题名为“卡拉瓦乔（Caravaggio）”。既有全书候选 `cand-3010` 的全名锚点及 `cand-7513` 的第8章提及均已映射到该卡，属于同一 `sg3-ku-units-persons-caravaggio` 组。因此四条候选从 `new` 更正为 `same`，映射至既有人物 KU；原先新组裁决与其依据留在每条 `resolution_note` 中。没有新增外部来源，也不改写既有卡片、manifest、accepted 或 S2 断言。
- 批次脚本 [Caravaggio S3 复用裁决](reconcile_s3_caravaggio_existing_identity_20261016.py) 的 dry-run 核对 accepted/manifest 卡片、两条已有同组候选、四个索引锚点和相邻 S2 正文；apply 仅改写四条 alignment 决定。当前 same=1,696、new=4,985；new 组从4,820降为4,819，已登记120组/149条候选映射不变，待登记4,699组/4,836条候选映射。

### person：Marie de Medici 跨章单候选组登记（2026-10-16）

- `cand-1631`（`M.csv#171`）是人物主项，索引列出 pp.53、173–175；第2章 p.53 提及 Rubens 为 Marie de Medici 与 Henri IV 所作寓意组画，第7章 pp.173–175 连续讨论她在巴黎的宫廷艺术活动、建筑计划和绘画委托。候选只有一个成员，按既有 S3 身份组 `new-person:de-marie-medici-0edb22161a` 登记为一张人物 KU。manifest 中无同名人物 KU。
- [Marie de Medici 人物卡](../../../04-knowledge/units/persons/marie-de-medici.md)使用书内姓名；中英文描述语义对应，列出五处精确来源引文。保留第7章“唯一明确存世委托”说法的意大利艺术家论述范围，避免抹去 p.174 的 Rubens 长廊记述；未作外部身份核验。
- 该候选有27条 S2 断言端点，其中24条是关系候选，全部留待 S6；本批未新增正式关系。批次脚本 [Marie de Medici S4 登记](register_s4_person_marie_de_medici_batch_20261016.py) 的 dry-run 核对唯一组成员、无既有人物卡、五处原文引文、端点数和外键后通过；apply 登记一组一卡并映射候选。manifest 从1,139增至1,140；累计登记121组、150条成员候选映射，未登记余4,698组、4,835条候选。

### S3：Lorenzo Onofrio Colonna 两条索引子目由待证转入新身份组（2026-10-16）

- `cand-0812`（`C.csv#342`，employment of Claude，p.156）与 `cand-0813`（`C.csv#343`，liking for mythological fables and landscapes，p.155）原先因没有各自单列的 `s2_mentions` 保持 `undecided`。逐条回到正文后，发现第6章 p.155 已明确具名 Lorenzo Onofrio；同一连续叙述在 p.156 明言其“employment of Claude”，在 p.155 明言其对“mythological fables and landscapes”的偏好，两项恰与索引子目对应。对应 S2 statement 已锚定在主项候选 `cand-0811`，并非仅凭索引页码或 Colonna 姓氏合并。
- 因此将两条候选从 `undecided` 更正为 `new`，并入 `cand-0811` 的 `new-person:colonna-lorenzo-onofrio-c75ad3fea2` 组。未具名或其他 Colonna 人物、科隆纳家族及其他类型对象均保持独立；没有访问外部身份源。原先待证理由保存在对齐行的 `prior_resolution_note` 中。
- [Lorenzo Onofrio Colonna 子目复核脚本](reconcile_s3_lorenzo_onofrio_colonna_index_subentries_20261016.py) dry-run 核对两个精确索引子目、同页正文锚点及两条对应 statement 后通过；apply 后 `new=4,987`、`undecided=5,616`，`new` 组数维持4,819，多候选组增至132。S4 尚未登记该组时，待登记为4,698组、4,837条候选。

### person：Lorenzo Onofrio Colonna 三候选组登记（2026-10-16）

- `cand-0811` 主项、`cand-0812` Claude 子目及 `cand-0813` 题材偏好子目登记为一张人物 KU。原有文件 [Lorenzo Onofrio Colonna 人物草稿](../../../04-knowledge/units/persons/lorenzo-onofrio-colonna.md) 当时不在 accepted/manifest 中；本批核对后沿用同一路径，按现行双语正文、来源字段与过程引用格式原位更新，不将草稿状态回溯成先前已登记。
- 新卡区分个人与家族、具体绘画委托与家族宫殿装饰；保留 Haskell 对 Lorenzo 与部分题材构思联系的推测语气。核对六处来源引文与 27 条 S2 断言端点，其中23条为关系候选；均留待 S6，本批未增加正式关系或外部核验。
- 批次脚本 [Lorenzo Onofrio Colonna S4 登记](register_s4_person_lorenzo_onofrio_colonna_batch_20261016.py) dry-run 核对三条候选、未登记草稿状态、无既有人物 KU、引文、端点和外键后通过；apply 更新该草稿、写入 manifest/accepted 并映射三条候选。manifest 从1,140增至1,141；累计登记122组、153条成员候选，待登记4,697组、4,834条。

### person：Giambattista Ricciardi 单候选组登记（2026-10-16）

- `cand-2187`（`Q-R.csv#114`）为人物主项，索引列第5章 p.144–145 与第7章 p.169；第5章 p.142 另有全名锚点。第5章称 Ricciardi 是 Rosa 最亲密且挚爱的朋友、诗人，并记 Rosa 为他绘画和寻求建议；同章说明 Ricciardi 居于另一城，不能提供 Rosa 所求的个人赞助。第7章 p.169 在1669年书信语境中写作 “G. B. Ricciardi”。正文全名、索引全名和书信缩写共同支持此单候选组；没有按姓氏合并其他人物或信件/作品候选。
- 登记为新人物 KU `units/persons/giambattista-ricciardi`。卡片保留 Haskell 对 Ricciardi 的书内评价及“其信未存”的来源限制，区分友情、艺术咨询与个人赞助；中英文描述语义对应，核对六条原文引文记录，覆盖第5章 p.142、144、145 及第7章 p.169。未作外部身份核验。
- `cand-2187` 是23条 S2 断言的端点，23条均为关系候选，全部留待 S6 逐条审查；本批没有新增正式关系。[Ricciardi 人物卡](../../../04-knowledge/units/persons/giambattista-ricciardi.md)与[批次脚本](register_s4_person_giambattista_ricciardi_batch_20261016.py)记录卡片、证据、manifest/accepted 和候选映射。dry-run 核对唯一组成员、无既有人物 KU、六条引用记录、端点及外键后通过；apply 将候选映射至该卡。manifest 从1,141增至1,142；累计登记123组、154条成员候选，待登记4,696组、4,833条。

### person：Count of Monterey 单候选组登记（2026-10-16）

- `cand-1693`（`M.csv#234`）索引列印刷页136、171、172。第5章 p.136 称 Velasquez 于1630年留宿于 “the Ambassador Monterey” 处；第7章 p.171 明称 “the Count of Monterey”，回顾其罗马大使时期后称他于1631年调往 Naples；p.172 继续叙述其作为总督的艺术赞助。索引人物主项、正文称谓与连续时间/职务语境支持一个书内人物组。manifest 无匹配人物 KU。
- 登记为新人物 KU `units/persons/count-of-monterey`。卡片只采用原书和索引提供的称谓，不补写本名或外部身份；区分其与姻亲 Count-Duke Olivarez 及其他总督。核对四处原文引文，未作外部身份核验。
- `cand-1693` 是26条 S2 断言端点，其中24条为关系候选，均留待 S6 逐条审查；本批没有新增正式关系。[Count of Monterey 人物卡](../../../04-knowledge/units/persons/count-of-monterey.md)与[批次脚本](register_s4_person_count_of_monterey_batch_20261016.py)记录卡片、证据、manifest/accepted 和候选映射。dry-run 核对唯一组成员、无既有人物 KU、引文、端点及外键后通过；apply 将候选映射至该卡。manifest 从1,142增至1,143；累计登记124组、155条成员候选，待登记4,695组、4,832条。

### S3：Cardinal / Duke Alessandro Farnese 跨章身份拆分（2026-10-16）

- 索引 `F.csv#10` 将 “Farnese, Cardinal Alessandro” 的 p.137 列在同一主项下；但该页正文说 Famiano Strada《De Bello Belgico》第二卷纪念 Alessandro Farnese 为西班牙一方进行的低地国家战役。此名不能只凭索引归属和重名并到枢机。第3章 p.65–84 及第20章 pp.398–400 的 Gesù 赞助者确为 Cardinal Alessandro Farnese；p.137 的战役人物是另一位 Alessandro Farnese。
- 外部身份核对只用于消歧：Getty ULAN 500121936 标识 Cardinal Alessandro Farnese II 为1520–1589年枢机与艺术赞助人；[Treccani《意大利人传记辞典》](<https://www.treccani.it/enciclopedia/alessandro-farnese-duca-di-parma-piacenza-e-castro_(Dizionario-Biografico)/>)将低地国家战役人物识别为帕尔马、皮亚琴察和卡斯特罗公爵 Alessandro Farnese。Google Books 对 Strada 1647 年第二卷的题名记录写明该卷起于 Alessandro Farnese, Duke of Parma, Piacenza and Castro 的统辖期并覆盖1578–1590年；该书目记录仅作身份比对，不替代对 Haskell 的关系陈述。
- 保留原始索引候选 `cand-0995` 及索引页码，不改写源索引；从其 `s2_mentions` 中移出 p.137 的 `m-chp5-sec-iii-l70-80-007`，新建正文人物候选 `cand-12426`，将该 mention 及 statement `st-chp5-p137-farnese-named-as-campaign-leader` 的人物端点改接公爵候选，并同步 `st-chp5-p137-de-bello-farnese-campaigns` 的 `mentioned_candidate_ids`。`cand-0995` 保持 Cardinal 新身份组 `new-person:alessandro-farnese-b829378191`；`cand-12426` 建立独立组 `new-person:alessandro-farnese-duke-of-parma-cand-12426`。两者的 Getty ULAN/Treccani DBI 身份记录写入 `alignment.csv`，不将外部事实倒填进书内 statement。
- [S3 分拆脚本](reconcile_s3_farnese_cardinal_duke_split_20261016.py) dry-run 核对书内锚点、原索引记录、mention、statement 和两个外部身份记录后通过；apply 新增1条 person 候选及 `new` 决定，并建立 `bl-0002` 待办。之后[双人物 S4 批次脚本](register_s4_person_farnese_cardinal_duke_split_batch_20261016.py)分别登记枢机与公爵两张人物卡；[枢机卡](../../../04-knowledge/units/persons/cardinal-alessandro-farnese.md)与[公爵卡](../../../04-knowledge/units/persons/alessandro-farnese-duke-of-parma.md)保留彼此边界。枢机有23条 S2 断言端点、20条关系候选；公爵有1条端点且为关系候选，均待 S6；没有新增正式关系。`bl-0002` 已映射公爵 KU 并关闭。
- 新增该候选后，全书为12,404个候选决定：`new=4,988`、当前身份组4,820；S4 本批前已有124组/155条成员候选已登记，待4,696组/4,833条。本批登记两组两候选后，manifest 从1,143增至1,145；累计126组/157条映射，待4,694组/4,831条。

### S3：Dolfin 家族主项与子目并组及家族身份边界补裁决（2026-10-16）

- `cand-0930`（`D.csv#32`）是 “Dolfin family” 索引主项，原因缺少正文锚点保留 `undecided`；`cand-0931`（`D.csv#33`）是同一主项下的 “patronage of Tiepolo” 子目，正文第9章 p.252 将 Dolfin 称为家族，并把 Tiepolo 的十幅场景与其赞助相连。逐条核对索引项 `D.csv#32/#33` 的主项与子目层级及正文锚点后，将 `cand-0930` 从 `undecided` 更正为 `new`，与 `cand-0931` 共用 `sg3-family-dolfinfamily`；原待证理由保留在更新后的 `resolution_note`。该组有4条直接 S2 端点陈述，其中3条是关系候选，均留待 S6。
- `cand-7617` 的 p.214 家族所有者群体与 p.262 明确的 Giovanelli 家族叙述支持新 family 身份；不与尚未定型、仍为 `undecided` 的 `cand-1192` “Giovanelli collection” 合并。`cand-8571` 的决定仅确认 pp.263–264 的 Sagredo 家族集体，不补完谱系或成员归属；相关个人候选保持独立。
- [家族身份补裁决脚本](reconcile_s3_pending_family_identity_groups_20261016.py) dry-run 核对了原索引父子行、正文锚点、旧决定和总数后通过；apply 后 `new=4,989`、`undecided=5,615`，身份组数4,820。该更正不改变候选总数或外部标识记录数。

### family：6组、7条候选 S4 登记（2026-10-16）

- 按 S3 新身份组各登记一张 family KU：`sg3-family-dolfinfamily`（`cand-0930`、`cand-0931`）、Foscarini、Giovanelli、Miani of Camerata、Baglione of Polazzo、Sagredo。卡片分别为 [Dolfin](../../../04-knowledge/units/families/dolfin-family-venice.md)、[Foscarini](../../../04-knowledge/units/families/foscarini-family-venice.md)、[Giovanelli](../../../04-knowledge/units/families/giovanelli-family-venice.md)、[Miani](../../../04-knowledge/units/families/miani-family-camerata.md)、[Baglione](../../../04-knowledge/units/families/baglione-family-polazzo.md) 与 [Sagredo](../../../04-knowledge/units/families/sagredo-family-venice.md)。每卡保留中英文等值名称/描述及精确书内证据；不据此补全谱系、成员或外部身份。
- 本批覆盖11条候选直接对应的 S2 断言，其中8条为关系候选：Dolfin 3、Foscarini 3、Giovanelli 1、Miani 1、Baglione 1；Sagredo 家族候选没有直接关系端点。8条关系候选全部留待 S6，Miani/Baglione 注8不把括号中的 Alessandro Longhi 误作已确认的受雇者；没有新增正式关系。
- [family S4 批次脚本](register_s4_pending_family_groups_20261016.py) dry-run 核对6组/7成员、11条断言端点及8条关系候选、六组书内引文、无既有同类 KU 和接受清单路径后通过；apply 后 manifest 从1,145增至1,151，累计登记132组/164条候选映射，未登记余4,688组/4,825条成员候选。family 类型80组、86条候选全部登记。

### person：5th Lord Exeter 单候选组登记（2026-10-16）

- `cand-0984`（`E.csv#20`）索引列 p.197、198、211；第7章 p.197 明称 “The 5th Lord Exeter”，叙述其1680–1685年两次赴意及在所到城市委托绘画；p.198 继续称 “Lord Exeter”。第8章 p.211 注释以相同称谓提到一幅售予 Lord Exeter 的作品。跨章标题与正文称谓相合，支持一条书内人物身份；本书未给出其个人姓名，故卡片只用来源称谓，不外推全名或外部身份。
- 登记为 `units/persons/5th-lord-exeter`。卡片记录收藏、委托及收藏史语境，保留第8章注释作为跨章称谓锚点。`cand-0984` 对应24条 S2 断言端点，其中21条为关系候选；均留待 S6，本批没有新增正式关系。
- [5th Lord Exeter 人物卡](../../../04-knowledge/units/persons/5th-lord-exeter.md)及[批次脚本](register_s4_person_fifth_lord_exeter_batch_20261016.py)保存卡片、双语来源证据、manifest/accepted 登记与候选映射。dry-run 核对唯一组成员、书内称谓、四处原文引文、24条端点及无既有同类 KU 后通过；apply 将候选映射至新 KU，并在 alignment 备注中更正“full personal name”为仅有 title-level referent。manifest 从1,151增至1,152；累计登记133组、165条成员候选，待4,687组、4,824条。

### person：Alessandro Algardi 三候选组登记（2026-10-16）

- `cand-0034`（`A.csv#35`）人物主项、`cand-0035`（`A.csv#36`）与 `cand-0036`（`A.csv#37`）胸像子目均标为 person；第6章 p.148 明称 Alessandro Algardi 制作 Innocent X 与 Donna Olimpia 的胸像，支撑将三条索引候选映射到同一雕塑家身份，不把两件胸像并入人物 KU。跨第2、3、4、6、7、15章的全名、简称及指代均在 S3 组 `new-person:alessandro-algardi-a854efdf4e` 中保留。
- 原有 `alessandro-algardi.md` 是2026-09-09形成但未进入 manifest/accepted 的旧草稿。本批在同一路径更新为现行双语正文和逐处来源记录，保留原卡指出的 Bellori 完整人物传记说法；无新增身份源或外部核验。
- 三条候选对应21条 S2 断言端点，其中19条为关系候选，全部留待 S6；本批没有新增正式关系。[Alessandro Algardi 人物卡](../../../04-knowledge/units/persons/alessandro-algardi.md)与[批次脚本](register_s4_person_alessandro_algardi_batch_20261016.py)记录五处来源、原位更新、manifest/accepted 登记与候选映射。dry-run 后 apply；manifest 从1,152增至1,153，累计登记134组、168条候选映射，待4,686组、4,821条。

### person：Carlo Cignani 跨章双候选组登记（2026-10-16）

- `cand-0748`（`C.csv#272`）为 Carlo Cignani 人物主项；`cand-0749`（`C.csv#273`）以 `and S. Maria Maggiore, Bergamo` 作子目。两条均为 person 候选，S3 已依跨章具名正文归入 `new-person:carlo-cignani-8a5a0153eb`。第8章 pp.219–220 连续记述 Bergamo 中殿委托谈判及1692年再度接洽，明确写出 Carlo Cignani / Cignani，支持子目与主项为同一人；教堂、穹顶与画作不并入人物组。
- 新登记 `units/persons/carlo-cignani`。卡片概述第7章为 Louis XIV 作画及未推进的巴黎邀约、第8章 Bergamo 谈判与 Forlì 穹顶、第10章 Johann Wilhelm 委托及 Joseph Smith 收藏，以及第13章 Pasquali 出版活动。双语描述和六处逐项来源保留原书归属、评价与转述范围；未补入生卒年或外部身份核验。
- 两条候选共有27条唯一 S2 断言端点，其中19条为关系候选，均留待 S6；七幅 cartoons、未具名画作和穹顶保持作品组/作品语境，本批未新增正式关系。
- [Carlo Cignani 人物卡](../../../04-knowledge/units/persons/carlo-cignani.md)与[批次脚本](register_s4_person_carlo_cignani_batch_20261016.py)记录来源、登记和候选映射。dry-run 核对组成员、索引子目、六处原文引文、27条端点、19条关系候选及外键后通过；apply 登记一组一卡并映射两条候选。manifest 从1,153增至1,154；累计登记135组、170条成员候选，待4,685组、4,819条。

### person：Gasparo Gozzi 跨章双候选组登记（2026-10-16）

- `cand-1220`（`G.csv#128`，人物主项）与 `cand-1223`（`G.csv#131`，support for Giorgio Pisani 子目）同属 `new-person:gasparo-gozzi-3503eaac17`。第9章 p.247 称 Gasparo Gozzi 是 Goldoni 的热心崇拜者；第10章 pp.321、323–326 连续论及 Gaspare / Gasparo Gozzi 的建筑评论、期刊编辑、Longhi/Tiepolo 比较、寓言和公共艺术主张，以及为 Pisani 撰写颂词，支持跨页身份组。正文明确说 Carlo 是 Gasparo 的兄弟；人物候选 cand-1219 的 Carlo Gozzi 维持独立组。
- 登记为 `units/persons/gasparo-gozzi`。卡片记录六处双语来源证据，保留 Haskell 对 Lodoli 影响的推断以及对 Gozzi 社会位置的评价，不把作者观点或文学/期刊作品写成正式关系。p.333 的 `cand-9979`（Gaspara Gozzi）与索引 Gasparo p.333 定位仍为 `conflict`，本卡不吸收该候选；文章、观点、未具名颂词仍按 archive / term / undecided 原决定保留。
- 两条成员候选对应27条唯一 S2 断言端点，其中13条为关系候选，全部留待 S6；本批未新增正式关系。[Gasparo Gozzi 人物卡](../../../04-knowledge/units/persons/gasparo-gozzi.md)和[批次脚本](register_s4_person_gasparo_gozzi_batch_20261016.py)记录证据边界及登记。dry-run 核对组成员、相邻候选类型、Carlo Gozzi 独立组、p.333 冲突状态、六处原文引文、27条端点及13条关系候选后通过；apply 将两条候选映射至一张新 KU。manifest 从1,154增至1,155；累计登记136组、172条成员候选，待4,684组、4,817条。

### person：Luigi Celotti 单候选组登记（2026-10-16）

- `cand-0622`（`C.csv#146`，索引 `Celotti, Abate Luigi`）对应第16章 p.377 明确称名 `Abate Luigi Celotti`，已在 S3 归入 `new-person:celotti-luigi-9757752530`。本书同页将他描述为艺术品经销者，记述其在 Venice、Paris、London 反复建立与散出收藏，并列举其经手的彩饰细密画、古代大师、18世纪威尼斯画作及收藏中的 Canaletto、Sebastiano Ricci 与 Tiepolo 作品。
- 新登记 `units/persons/luigi-celotti`。卡片保留 Haskell 对销售才能与独立趣味的推断，不将其据为外部事实；原书注释转引 Levi 对 Celotti 约1846年去世的说法，但该文未独立查阅，故卡片不补入生卒年。作品所有权、具体作品、来源及关系均不由身份登记推定。
- 该候选对应26条唯一 S2 断言端点，其中19条为关系候选，全部留待 S6；本批未新增正式关系。[Luigi Celotti 人物卡](../../../04-knowledge/units/persons/luigi-celotti.md)与[批次脚本](register_s4_person_luigi_celotti_batch_20261016.py)记录来源及映射。dry-run 核对索引项、书内全名、无既有同类 KU、五处原文引文、26条端点及19条关系候选后通过；apply 将单候选映射至一张新 KU。manifest 从1,155增至1,156；累计登记137组、173条成员候选，待4,683组、4,816条。

### person：Antonio Zatta 单候选组登记（2026-10-16）

- `cand-2865`（`UVWXYZ.csv#202`，索引 pp.335、338、339）已在 S3 归入 `new-person:antonio-zatta-d782464a1b`。第13章 p.334 以全名将 Antonio Zatta 列入重要威尼斯出版商；pp.338–339 连续记述其耶稣会争议、出版目录、意大利经典及 Dante 插图版活动，支持人物身份。
- 登记为 `units/persons/antonio-zatta`。卡片保留 Haskell 的转述、评价与目录判断；“同时代人称其为耶稣会平信徒成员”仍明确标注为转述，注释所引资料未独立查阅。第15章 p.367 注释中 `Zana` 的 OCR 据印本校作 `Zatta`，但该处是1787年颂词的出版印记，不是完整人名锚点；S4 登记不依此处确立身份。书目、具体出版物与政治关系未并入人物卡。
- 该候选对应25条唯一 S2 断言端点，其中16条为关系候选，全部留待 S6；本批未新增正式关系。[Antonio Zatta 人物卡](../../../04-knowledge/units/persons/antonio-zatta.md)与[批次脚本](register_s4_person_antonio_zatta_batch_20261016.py)记录来源和映射。dry-run 核对索引项、跨章全名证据、p.367 印记边界、五处原文引文、25条端点及16条关系候选后通过；apply 将单候选映射至一张新 KU。manifest 从1,156增至1,157；累计登记138组、174条成员候选，待4,682组、4,815条。

### person：Don Pietro Antonio Toni 单候选组登记（2026-10-16）

- `cand-2640`（`T.csv#103`，索引 pp.345–346）已在 S3 归入 `new-person:antonio-pietro-priest-toni-antonio-pietro--3f08cc9cc0`。第13章以全名引介其为神父，继而连续叙述其定居 Venice、收藏和经销活动、与 Sebastiano Ricci 的交往，以及对年轻 Pietro Antonio Novelli 的建议与赞助，支持这一书内人物身份。Toni 与 Novelli 保持为两个人物。
- 登记为 `units/persons/pietro-antonio-toni`。卡片仅按原书记录出生于 Modena 附近、定居 Venice 及1748年去世的说法；Haskell 对 Novelli 后来文风的推测保留为可能性，不改写为确定因果。S2 已登记的友谊、照料、馈赠、赞助、代理、收藏和购版画陈述均留待 S6，不在本卡新增正式关系。
- [Don Pietro Antonio Toni 人物卡](../../../04-knowledge/units/persons/pietro-antonio-toni.md)与[批次脚本](register_s4_person_pietro_antonio_toni_batch_20261016.py)记录五处来源及候选映射。dry-run 核对索引项、书内全名、无既有同类 KU、五处原文引文、24条端点及19条关系候选后通过；apply 将单候选映射至一张新 KU。manifest 从1,157增至1,158；累计登记139组、175条成员候选，待4,681组、4,814条。

### person：Gian Antonio Guardi 单候选组登记（2026-10-16）

- `cand-1245`（`G.csv#155`，索引 pp.258、312、315、383）已在 S3 归入 `new-person:antonio-gian-guardi-antonio-gian-guardi-s-daa9764d01`。第9、10章多次以全名指称 Gian Antonio Guardi；第10章记述其为 Schulenburg 工作、主要从事临摹与肖像创作，且1742–1743年土耳其题材临摹显出 Haskell 所称的“Guardi magic”。
- 新登记 `units/persons/gian-antonio-guardi`，与 manifest/accepted 中既有 Francesco Guardi KU 明确区分。第10章注2转述 Watson 将一组作品归于 Gian Antonio 而非 Francesco；该研究未独立查阅。第17章 p.383 主文称其创作带有 Longhi 风格的作品，但同页注1仅写 Correr 当时认为作品为“Guardi”所作，且记载后来目录归于 Longhi；该注未指明 Guardi 的名字，Pignatti 未独立查阅，因此不据此消解归属争议。
- 该候选对应23条唯一 S2 断言端点，其中19条为关系候选，均留待 S6；本批未新增正式关系。[Gian Antonio Guardi 人物卡](../../../04-knowledge/units/persons/gian-antonio-guardi.md)与[批次脚本](register_s4_person_gian_antonio_guardi_batch_20261016.py)记录双语来源、身份边界与候选映射。dry-run 核对索引项、与 Francesco 的区分、五处原文引文、Correr 归属限制、23条端点及19条关系候选后通过；apply 将单候选映射至一张新 KU。manifest 从1,158增至1,159；累计登记140组、176条成员候选，待4,680组、4,813条。

### person：Pierre Crozat 跨章双候选组登记（2026-10-16）

- `cand-0894`（C.csv#428 人物主项）与经 S3 补裁的 `cand-0895`（C.csv#429，“patronage of Venetian artists”子目）同属 `new-person:crozat-pierre-793a5b5d2e`，登记为 `units/persons/pierre-crozat`，两条候选映射到一张人物卡。后者原 S3 `undecided` 的理由仍保存在对齐行历史注释中。
- 卡片依第7章 p.200 注3、第10章 pp.277、284–285、第13章 p.341 和第14章 p.349 的书内证据，记录银行家/收藏者身份、1715年观看 Carriera 粉彩、1716年威尼斯访问与 Zanetti 交往、1721年接待 Carriera 等语境。Loret 与 Zanotti 书信未在本批独立查阅；Crozat 收藏、宅邸、街址及未识别画作继续与人物分开。未补入生卒年、外部身份记录、正式关系或 S5 内容。
- 该组19条直接 S2 断言端点，其中14条标记为关系候选，全部留待 S6 逐项审查。批次脚本 [register_s4_person_pierre_crozat_batch_20261016.py](register_s4_person_pierre_crozat_batch_20261016.py) dry-run 核对 S3 组成员、类型、8处原文锚点、端点/候选数及外键后通过；apply 将两条候选映射至同一卡并登记 manifest/accepted。manifest 从1,161增至1,162；累计登记143组、181条候选映射，余4,676组、4,808条候选。

### person：Alessandro Marchesini 跨章双候选组登记（2026-10-16）

- `cand-1539`（M.csv#77 人物主项）与 `cand-1540`（M.csv#78，“work for Stefano Conti”子目）同属 `new-person:alessandro-marchesini-f0fde7762c`，登记为 `units/persons/alessandro-marchesini`，两条候选映射到一张人物卡。相邻已有程序 KU `units/procedures/marchesini-written-reports-to-conti` 记录的是报告活动，不替代人物卡。
- 第8章 pp.226–228 以全名称其为维罗纳画家，记载其在威尼斯居住、曾在博洛尼亚 Cignani 学习，以及担任 Conti 代理人的具体工作和1725年再次提供建议。第9章注释列出两封1725年致 Conti 的信及 Lucca 馆藏定位；第19章附录列出 Franceschini 于1705年致 Marchesini 的信。书信原件/转引材料未在本批独立查阅，Haskell 对其能力的评价保持为作者判断。
- 该组20条直接 S2 断言端点中16条标记为关系候选，全部留待 S6；本批未新增正式关系、书信 KU、外部身份记录或 S5 补足。批次脚本 [register_s4_person_alessandro_marchesini_batch_20261016.py](register_s4_person_alessandro_marchesini_batch_20261016.py) dry-run 核对 S3 组成员、类型、7处原文锚点、端点/候选数及外键后通过；apply 将两条候选映射至同一卡。manifest 从1,162增至1,163；累计登记144组、183条候选映射，余4,675组、4,806条候选。

### person：Marcantonio Franceschini 跨章双候选组登记（2026-10-16）

- `cand-1069`（F.csv#84 人物主项）与 `cand-1070`（F.csv#85，“letters relating to commission from Stefano Conti”子目）同属 `new-person:franceschini-marcantonio-12371601a9`，登记为 `units/persons/marcantonio-franceschini`，两条候选映射到一张人物卡。卡片与既有 Baldassarre Franceschini 人物 KU 按全名区分。
- 第7章 p.194 记 Liechtenstein 家族向 Franceschini 订购42幅画；第8章 pp.220、223、227 记其为 Cignani 学生、委员会向其询价、Ruffo 委托及其致 Conti 的题材意见；第19章 p.389 附录列出相关 Conti 委托文书及1705年致 Marchesini 的信。原信和馆藏未在本批独立查阅，作者判断仍按原书层级保留。
- 该组18条直接 S2 断言端点中16条标记为关系候选，全部留待 S6。批次脚本 [register_s4_person_marcantonio_franceschini_batch_20261016.py](register_s4_person_marcantonio_franceschini_batch_20261016.py) dry-run 核对组成员、同姓既有 KU 边界、6处原文锚点、端点/候选数及外键后通过；apply 将两条候选映射至同一卡。manifest 从1,163增至1,164；累计登记145组、185条候选映射，余4,674组、4,804条候选。

### person：Giustiniana Wynne-Rosenberg 跨章身份组登记（2026-10-16）

- `cand-2824`（UVWXYZ.csv#161，索引名 Wynne, Giustiniana (Mme Rosenberg)）属于 `new-person:giustiniana-rosenberg-wynne-giustiniana-wy-8bd579547c`，登记为 `units/persons/giustiniana-wynne-rosenberg`。正文中的 Giustiniana Wynne、Mme Rosenberg 与脚注作者名 Giustiniana Wynne-Rosenberg 由第10、15章的跨章回指支持，合为一个人物 KU；Count Rosenberg 和既有 Pierre Rosenberg KU 均保持区分。
- 第10章 pp.300、302 与第15章 pp.369–371 提供身份、婚姻、回指及书目锚点。卡片保留 Haskell 的叙述层级；《Alticchiero》1787年版本未独立查阅。
- 19条直接 S2 断言端点中16条标记为关系候选，全部留待 S6；本批未新增正式关系、外部身份记录或 S5 补足。批次脚本 [register_s4_person_giustiniana_wynne_rosenberg_batch_20261016.py](register_s4_person_giustiniana_wynne_rosenberg_batch_20261016.py) dry-run 核对单候选组、5处精确原文锚点、端点/候选数、既有姓名边界和登记外键后通过，再 apply 完成卡片、manifest、accepted.yml 与候选映射。manifest 从1,164增至1,165；累计登记146组、186条候选映射，余4,673组、4,803条候选。

### person：Giovanni Vianello 直接端点登记（2026-10-16）

- `cand-2764`（UVWXYZ.csv#100，索引名 Vianello, Dr Giovanni）属于 `new-person:giovanni-vianello-01f3203923`，登记为 `units/persons/giovanni-vianello`。第16章 p.376 提供全名、Chioggia Cathedral canon 身份及收藏叙述；OCR 的连写保留在引文中，显示姓名按索引分词。第13章脚注另有姓氏 Vianello 的书内提及，但本卡不据该姓氏单独扩展身份或书目信息。
- 卡片保留 Haskell 对可能圈层成员身份、学术姿态、画商身份和藏品处置的限定；20条直接 S2 断言端点中8条为关系候选，均待 S6。本批未新增正式关系、作品/档案 KU、外部身份记录或 S5 补足。
- [register_s4_person_giovanni_vianello_batch_20261016.py](register_s4_person_giovanni_vianello_batch_20261016.py) dry-run 核对单候选组、5处精确原文锚点、20条端点/8条关系候选、既有人物 KU 边界和登记外键后通过，再 apply 完成卡片、manifest、accepted.yml 与候选映射。manifest 从1,165增至1,166；累计登记147组、187条候选映射，余4,672组、4,802条候选。

### person：Bonomo Algarotti 跨章直接端点登记（2026-10-16）

- `cand-0040`（A.csv#41，索引名 Algarotti, Bonomo）属于 `new-person:algarotti-bonomo-6fee58462e`，登记为 `units/persons/bonomo-algarotti`。第14、15章称 Bonomo 是 Francesco Algarotti 的长兄；第10章脚注记录 Francesco 致兄长 Bonomo 的书信。该组只指兄长，不与既有 Francesco Algarotti KU 合并；本书没有提供 Bonomo 的其他名字。
- 卡片记录第14章对其鉴赏力、影响、共同收藏和协助计划的叙述，并保留 Haskell 对影响难以评估的限定；书中称 Bonomo 于1776年去世。引文所指 Treviso 书信和 1790 年代传记未在本批独立查阅。
- 16条直接 S2 断言端点中15条标记为关系候选，全部留待 S6；本批未新增正式关系、作品/藏品/档案 KU、外部身份记录或 S5 补足。[register_s4_person_bonomo_algarotti_batch_20261016.py](register_s4_person_bonomo_algarotti_batch_20261016.py) dry-run 核对单候选组、6处精确原文锚点、既有 Francesco Algarotti KU 边界、端点数和登记外键后通过，再 apply 完成卡片、manifest、accepted.yml 与候选映射。manifest 从1,166增至1,167；累计登记148组、188条候选映射，余4,670组、4,800条候选。

### person：Donna Olimpia Maidalchini 跨章身份组登记（2026-10-16）

- `cand-1496`（M.csv#33）属于 `new-person:donna-maidalchini-olimpia-d9e87ff16a`，登记为 `units/persons/olimpia-maidalchini`。第3、4、6章的索引与 S2 锚点支持同一位 Donna Olimpia Maidalchini；第6章以全名说明她是 Camillo 的母亲及教皇的弟媳。她与 Camillo 的妻子 Olimpia Aldobrandini 不同；后者继续使用既有 KU `units/persons/olimpia-aldobrandini`。
- 固定路径原有一张第一、六章限定测试草稿，但该卡不在 accepted.yml 或 manifest 中，故 `new` 决定不改为复用。本批在原路径将草稿更新为当前双语 S4 卡，保留其母子／配偶身份边界及来源限定，不复制出第二张卡。
- 17条直接 S2 断言端点中13条为关系候选，全部留待 S6；未新增正式关系、外部身份记录或 S5 补足。批次脚本 [register_s4_person_olimpia_maidalchini_batch_20261016.py](register_s4_person_olimpia_maidalchini_batch_20261016.py) dry-run 核对唯一组成员、6处精确原文锚点、端点及候选数、既有妻子 KU 边界、旧草稿路径和登记外键后通过，再 apply 更新卡片、manifest、accepted.yml 与候选映射。manifest 从1,167增至1,168；累计登记149组、189条候选映射，余4,669组、4,799条候选。

### person：Philip Neri 与 Pietro Liberi 跨章身份组登记（2026-10-16）

- `cand-1898`（P.csv#99）属于 `new-person:neri-philip-42b3421786`，登记为 `units/persons/philip-neri`；`cand-1401`（L.csv#58）属于 `new-person:liberi-pietro-19e17efc6a`，登记为 `units/persons/pietro-liberi`。两组各一名候选，当前 manifest 和 accepted.yml 均无对应 KU；卡片分别保留 St Philip Neri/Philip Neri 与 Pietro Liberi/Liberis 的书内写法。
- Philip Neri 卡据第3章对奥拉托利会创立者、视觉艺术兴趣及 Chiesa Nuova 建设的记述；早期传记故事和 Barocci 画前的宗教体验保留原有转述限定。Pietro Liberi 卡据第7章赴维也纳叙述、第8章贝加莫委托及第19章拍卖清单；作品来源、评价及委托失败原因均按 Haskell 的叙述、推测和不确定归属登记。
- Philip Neri 有17条直接 S2 断言端点（16条关系候选）；Pietro Liberi 有17条端点（11条关系候选），均留待 S6。本批未新增正式关系、work/archive KU、外部身份记录或 S5 补足。批次脚本 [register_s4_person_neri_liberi_batch_20261016.py](register_s4_person_neri_liberi_batch_20261016.py) dry-run 核对两组成员、11处精确引文、端点/关系候选数、既有 KU 和登记外键后通过，再 apply 完成两张卡、manifest、accepted.yml 与候选映射。manifest 从1,168增至1,170；累计登记151组、191条候选映射，余4,667组、4,797条。

### person：Niccolò Cassana 跨索引身份组登记（2026-10-16）

- cand-0593（C.csv#117 主项）与 cand-0594（C.csv#118，“as agent for Grand Prince Ferdinand”子目）属于 `new-person:cassana-niccolo-7c18d86b6b`，共映射至 `units/persons/niccolo-cassana`。同名与第8章对其威尼斯代理角色的直接说明支持并组；manifest 中没有既有人物 KU。
- 第7章称其为热那亚画家，Queen Anne 肖像画家职位及1714年卒年以问号表达；注1转述 Ratti 的1713年说法，并称来英时间和死地不明。第8章说明他自1698年为 Ferdinand 在威尼斯任代理、兼作画家和艺术顾问；第10章估价信息仅保留 Haskell 的转述。不同年份和不确定项并列，不作外部裁决。
- 17条直接 S2 断言端点中16条为关系候选，均留待 S6；本批不新增正式关系、作品/档案 KU、外部身份记录或 S5 补足。[register_s4_person_niccolo_cassana_batch_20261016.py](register_s4_person_niccolo_cassana_batch_20261016.py) dry-run 核对两条组成员、6处精确原文锚点、端点/关系候选数和登记外键后通过，再 apply 登记一张卡并完成 manifest、accepted.yml 和两条候选映射。manifest 从1,170增至1,171；累计登记152组、193条候选映射，余4,666组、4,795条。

### person：Giambattista Marino 跨章身份组登记（2026-10-16）

- `cand-1548`（M.csv#87）属于 `new-person:giambattista-marino-17f964d895`，登记为 `units/persons/giambattista-marino`。索引页码横跨第2、4、10、14、20章；现有 manifest 中无同名人物 KU。
- 第2章记其与 Marcello Sacchetti 的友谊、1623年返意后的行程、绘画兴趣和对 Poussin 的影响；关于教皇赞助未果原因是作者推测。第4章称 Marino 是 Poussin 最早的赞赏者之一，并记 Poussin 图画由其委托、遗赠给身份未明之友人；Cassiano dal Pozzo 只作为可能对象保留。未增写外部生卒年或作品目录。
- 16条直接 S2 断言端点全部为关系候选，留待 S6；本批未新增正式关系、archive/work KU、外部身份记录或 S5 补足。[register_s4_person_giambattista_marino_batch_20261016.py](register_s4_person_giambattista_marino_batch_20261016.py) dry-run 核对候选组、4处精确引文、端点数和登记外键后通过，再 apply 完成卡片、manifest、accepted.yml 与候选映射。manifest 从1,171增至1,172；累计登记153组、194条候选映射，余4,665组、4,794条。

### person：Galileo Galilei 跨章身份组登记（2026-10-16）

- `cand-1105`（G.csv#12）属于 `new-person:galilei-galileo-ff0ea1f6cb`，登记为 `units/persons/galileo-galilei`。索引页码横跨第2、3、4、10、20章；manifest 中无同名人物 KU。
- 卡片据第4章关于 Cassiano dal Pozzo 友好通信与肖像、第4章对 Ludovico Cigoli 的画家身份、第3章对 Orazio Grassi 争议的提及，以及第10章对 Lodoli 阅读偏好的叙述。第4章将科学态度和艺术判断相联系的句子作为 Haskell 的作者解释保留；不扩写外部生平或科学史。
- 16条直接 S2 断言端点中11条为关系候选，全部留待 S6；本批未新增正式关系、作品/archive KU、外部身份记录或 S5 补足。[register_s4_person_galileo_galilei_batch_20261016.py](register_s4_person_galileo_galilei_batch_20261016.py) dry-run 核对唯一组成员、5处精确引文、端点/关系候选数和登记外键后通过，再 apply 完成卡片、manifest、accepted.yml 与候选映射。manifest 从1,172增至1,173；累计登记154组、195条候选映射，余4,664组、4,793条。

### person：萨伏依的欧根亲王跨章身份组登记（2026-10-16）

- S3 组 `new-person:eugene-of-savoy-c81f37e553` 包含 `cand-2384`（S.csv#72，pp.311、341、403）、`cand-2385`（S.csv#73，p.201，patronage of Italian artists）和 `cand-2386`（S.csv#74，p.201，taste），登记为一个人物 KU `units/persons/prince-eugene-of-savoy`。已有 House of Savoy 是 family KU，不与人物合并。
- 书内身份锚点包括第7章 p.201 的 Prince Eugene of Savoy 全名及意大利艺术赞助叙述、第8章 p.228 Crespi 引述中的全名、第10章 p.311 的 Eugene、第13章 p.341 Eugene 的继承人，以及第20章 p.403 对其收藏研究的提及。卡片只保留 Haskell 的来源归属和限定，不扩写外部生平；第20章 OCR 的所有格拼写问题在来源注释中说明。
- 本组16条直接 S2 断言端点中15条为关系候选，全部待 S6；未新增正式关系、外部身份记录或 S5 补足。[register_s4_person_eugene_of_savoy_batch_20261016.py](register_s4_person_eugene_of_savoy_batch_20261016.py) dry-run 核对三条 S3 组成员、6处精确引文、端点/关系候选数和登记外键后通过，再 apply 更新卡片、manifest、accepted.yml 与三条候选映射。manifest 从1,173增至1,174；累计登记155组、198条候选映射，余4,663组、4,790条。

### person：Cardinal Giovan Francesco Negroni 人物组登记（2026-10-16）

- `cand-1732`（N.csv#12，“Negroni, Cardinal Giovan Francesco”，pp.84–85）按一个人物组 `new-person:francesco-giovan-negroni-9728ee603a` 登记为 `units/persons/cardinal-giovan-francesco-negroni`。manifest 中只有 Negroni family 的 family KU；没有同名人物 KU。
- 第3章 p.84 将 Monsignor Negroni 与后来的 Cardinal 连续指称，并记其取得小堂赞助权及委托 Pietro da Cortona；p.85 继续称其为 the Cardinal，记其选用 Gianandrea Carlone 和 Carlo Maratta。卡片姓名采用索引全名；正文只用姓氏/称号，未据同姓推断 family membership。
- 本组17条直接 S2 断言端点中15条为关系候选，均留待 S6；本批不新增正式关系、外部身份记录或 S5 补足。[register_s4_person_giovan_francesco_negroni_batch_20261016.py](register_s4_person_giovan_francesco_negroni_batch_20261016.py) dry-run 核对索引决定、5处精确原文引文、端点/关系候选数及登记外键后通过，再 apply 写入卡片、manifest、accepted.yml 与候选映射。manifest 从1,174增至1,175；累计登记156组、199条候选映射，余4,662组、4,789条。

### person：Francesco Bracciolini 双索引候选组登记（2026-10-16）

- `cand-0440`（B.csv#287，主项）与 `cand-0441`（B.csv#288，`L'elettione di Urbano VIII` 子目）属于同一 S3 人物组 `new-person:bracciolini-francesco-bracciolini-francesc-7cfa25f9e6`，共同登记为 `units/persons/francesco-bracciolini`。
- 子目题名和 p.52 的“the poem”经 S2 端点校正已映射至 archive 候选 `cand-4796`；该候选仍为 S3 `undecided`，不把诗作并入人物 KU。第2章 p.57 明确称该颂诗由 Bracciolini 创作；它是 Rospigliosi 评论的对象，不是 Rospigliosi 评论本身或 Bracciolini 所作的评论。
- 人物组16条直接 S2 断言端点中15条为关系候选，留待 S6；本批不新增正式关系、archive KU、外部身份记录或 S5 补足。[register_s4_person_francesco_bracciolini_batch_20261016.py](register_s4_person_francesco_bracciolini_batch_20261016.py) dry-run 核对两条组成员、4处引文、端点数和候选映射后通过，再 apply 更新卡片、manifest、accepted.yml 与两条人物候选映射。端点改挂未改变关系候选计数。manifest 从1,175增至1,176；累计登记157组、201条候选映射，余4,661组、4,787条。

### person：Carlo de’ Rossi 跨章直接端点组登记（2026-10-16）

- `cand-2269`（Q-R.csv#197，pp.143–144；子目“and Salvator Rosa”）属于 `new-person:carlo-de-rossi-01b009d0b8`，登记为 `units/persons/carlo-de-rossi`。现有 manifest 无同名人物 KU；该索引子目只用于定位，不与 Salvator Rosa 合并。
- 第5章 p.143 提供全名，称其为 Rosa 的银行家、罗马主要赞助人、音乐家及作曲家 Luigi 的兄弟；p.144 记其收藏 Rosa 作品。第6章 p.153 和第7章 p.190 再以 Carlo de’ Rossi／Carlo de Rossi 指其人。
- 16条直接 S2 断言端点中14条为关系候选，均留待 S6；本批不新增正式关系、作品/archive KU、外部身份记录或 S5 补足。[register_s4_person_carlo_de_rossi_batch_20261016.py](register_s4_person_carlo_de_rossi_batch_20261016.py) dry-run 核对组成员、5处原文引文、端点数和登记外键后通过，再 apply 更新卡片、manifest、accepted.yml 与候选映射。manifest 从1,176增至1,177；累计登记158组、202条候选映射，余4,660组、4,786条。

### person：Francesco Marucelli 跨章直接端点组登记（2026-10-16）

- `cand-1554`（M.csv#93，pp.157、158、235）登记为 `units/persons/francesco-marucelli`。第6章 p.157 以全名介绍其赞助人和收藏家身份；第8章 p.235 的 Marucelli 兄弟语境称 Francesco 于1703年在罗马去世，支持其与索引人物同一。
- 第6章 p.158 记其藏书、画家生平写作和向 Baldinucci 提供资料；这些有关人物、收藏、著作和委托的正式端点均留待 S6，卡片不把作者评价转为无条件事实。
- 16条直接 S2 断言端点中11条为关系候选；本批不新增正式关系、archive/work KU、外部身份记录或 S5 补足。[register_s4_person_francesco_marucelli_batch_20261016.py](register_s4_person_francesco_marucelli_batch_20261016.py) dry-run 核对唯一组成员、6处精确引文、端点和外键后通过，再 apply 更新卡片、manifest、accepted.yml 与候选映射。manifest 从1,177增至1,178；累计登记159组、203条候选映射，余4,659组、4,785条。

### person：Andrea del Rosso 长兄身份组登记（2026-10-16）

- `cand-2275`（Q-R.csv#203，pp.210–213、241、403–404）登记为 `units/persons/andrea-del-rosso`。第8章 p.211 明称其为长兄并记生于1640年；同页注释记其1715年去世。与其同名的祖父 `cand-2279` 已经 S3 拆分，归入单独的 `new-person:andrea-del-rosso-grandfather-2279`，本卡不予合并。
- 13条直接 S2 断言端点中9条为关系候选，均留待 S6。批次核对组成员、4处原文锚点、端点、S3 拆分决定及外键后 dry-run 通过；apply 升级人物卡并更新 manifest、accepted.yml、候选映射与结果文件。本批不新增正式关系、外部身份记录或 S5 补足。
- manifest 从1,178增至1,179；累计登记160组、204条候选映射，余4,659组、4,784条。person 类型共1,086组、1,178条候选，当前登记54组、91条映射，余1,032组、1,087条。

### person：Antonio degli Effetti 跨章直接端点组登记（2026-10-16）

- `cand-5974`（第4章 p.116 注释及第6章 pp.156–157）登记为 `units/persons/antonio-degli-effetti`。第4章注释引用其手稿收藏目录，第6章以全名介绍其古物研究者和地方史家身份，并讨论其收藏目录与文学兴趣，支持同一书内人物身份。
- 卡片保留“实际是否拥有目录所列部分画作存疑”和 Pinax 作者归属校正；Haskell 对其趣味和财富主题的解释均注明为作者判断。15条直接 S2 端点中10条为关系候选，均留待 S6；本批不新增作品 KU、正式关系、外部身份记录或 S5 补足。
- 未登记旧稿已按现行双语结构升级，保留来源支持的内容并校正“实际拥有”及 Cebes/Pinax 限定。脚本 dry-run 核对旧稿、7处原文、组成员、端点和外键后通过。manifest 从1,179增至1,180；累计登记161组、205条候选映射，余4,658组、4,783条。person 类型已登记55组、92条候选映射，余1,031组、1,086条。

### person：Simon Vouet 双候选组登记（2026-10-16）

- `cand-2792`（UVWXYZ.csv#129 主项）与 `cand-2793`（#130 “portrait of Isabella, Duchess of Bracciano”子目）共同映射至 `units/persons/simon-vouet`。第4章 p.97 正文明确称 Isabella 已由 Simon Vouet 绘制；子目指画家，不指一位新人物或可识别的肖像作品。
- 第2章 p.46 与第4章 pp.97、102 提供赞助、风格、罗马活动及肖像语境。14条直接 S2 端点全部为关系候选，留待 S6；本批不新增肖像作品 KU、正式关系、外部身份记录或 S5 补足。
- 批次脚本 dry-run 核对两条组成员、5处原文锚点、端点和外键后通过。manifest 从1,180增至1,181；累计登记162组、207条候选映射，余4,657组、4,781条。person 类型已登记56组、94条候选映射，余1,030组、1,084条。

### person：Cardinal Pier Donato Cesi 单候选跨章组登记（2026-10-16）

- `cand-0640`（C.csv#164，索引主项 “Cesi, Cardinal Pier Donato”）对应 S3 组 `new-person:cesi-donato-pier-f179444158`，登记为 `units/persons/cardinal-pier-donato-cesi`。第3章 p.69 给出全名和 Chiesa Nuova 赞助语境；第20章后记 p.400 以 “Cardinal Cesi” 回顾同一人物的自我克制与1581年信件。卡片将该信标为 Haskell 的二手引文，脚注所引原文未在本批核读。
- 11条直接 S2 断言全部带 `relation_candidate`；登记时其中8条对端已映射到 Cardinal Alessandro Farnese 或 Oratorians KU，3条对端为当时尚未登记的 Chiesa Nuova 候选 `cand-0710`。后续 S3 将 `cand-0710` 复用至既有 `units/places/chiesa-nuova`，故 Cesi 的11条关系候选现均有已登记对端；关系本身仍留待 S6 审查。本批不做外部身份核验或 S5 补足。书内将其兄弟 Angelo Cesi 与 Pier Donato 区分，未合并 Cesi 家族卡或 Farnese 枢机卡。
- 批次脚本 dry-run 核对单成员身份组、5处精确引文、11条断言、8个已映射/3个待登记对端及现有外键后通过。manifest 从1,181增至1,182；累计登记163组、208条候选映射，余4,681组、4,808条。person 类型已登记57组、95条候选映射，余1,029组、1,083条。

### term：威尼斯贵族阶层跨章术语组 S4 登记（2026-10-16）

- `cand-8108`（S3 组 `sg3-term-cand-8108`）映射至 `units/terms/venetian-nobility-social-estate`。S2 提及账本在第8、9、10、13、15章均将相关表达指向威尼斯贵族社会阶层；第9章 p.247 的核心段落区分旧贵族家族、较贫的 patrician 家庭和新近获准进入者，并将贵族置于政治行政语境。第9章 p.248 的“aristocracy and the State”表述作为 Haskell 的解释保留，不据此将术语与共和国 institution KU 合并。
- 核对术语目录及 manifest，未发现表达同一社会阶层的既有 term KU。贵族身份准入/购入是程序，不并入本 term；家族和个人为不同粒度对象。`cand-10473` 所指第15章另一个未具名社会群体仍为 `undecided`，对齐注释明确不与 `cand-8108` 合并。本卡只登记本书用法，不作外部术语核验。
- `cand-8108` 连接28条直接 S2 关系候选断言、涉及22个不同对端；登记前11条对端已映射、17条仍待 S3/S4。批次不创建正式关系；后续按 S6 逐项裁决。脚本 dry-run 核对原文引文、身份组唯一成员、类型边界、断言数及关系对端计数后通过。
- 首次表格审计发现卡片手写属性表有5行、但无对应 enrichment 行。S5 尚未启动，故移除属性表、保留带逐项来源的术语范围说明；复审以表格审计 `errors=[]` 为准。
- manifest 从1,182增至1,183；累计登记164组、209条候选映射，余4,672组、4,799条映射。term 类型已登记2组/4条候选，余930组/942条候选。

### term：Bamboccianti 跨章艺术家群体 S4 登记（2026-10-16）

- `cand-0173`（索引主项，B.csv#20）、`cand-0174`（“attacks on”子目，B.csv#21）与 `cand-0177`（“prices for pictures”子目，B.csv#24）同属 S3 组 `sg3-term-bamboccianti`，共同映射到 `units/terms/bamboccianti`。第5章 p.132 说明名称来自 Pieter van Laer 的绰号，并区分指画家群体的 Bamboccianti 与指日常生活题材小画的 bambocciate；第5章 p.141 的攻击/价格子目及第6、8章和结论中的用例都回指同一群体/艺术现象。
- S2 mention notes 区分 artist group、作品类别和风格用法；索引子目不是额外实体。既有人物卡已区分 Pieter van Laer 与 Schildersbent 组织；本卡不把群体名称转为 institution、不创建完整成员表，也不将群体合并为作品类别。第5章 p.141 和第10章 p.324 有 OCR 词形异文；S2 提及账本记录其据页图校读，卡片保留 OCR 原形及该限定。
- 三条组成员对应55条直接 S2 断言，其中26条为关系候选、涉及21个不同对端；14条对端已映射、12条待 S3/S4。未新增正式关系或外部术语核验；候选关系留待 S6。
- 首次表格审计错误及修复过程见前一 term 批次；本卡沿用带出处的叙述式字段，不提前生成 S5 enrichment 属性表。脚本 dry-run 核对三候选组、原文/校读锚点、断言数和对端计数后通过。
- manifest 从1,183增至1,184；累计登记165组、212条候选映射，余4,671组、4,796条映射。term 类型已登记2组/4条候选，余930组/942条候选。

### 登记进度与后续

截至 Bamboccianti 术语组登记后，4,836 个当前 `new` 身份组中完成165组，余4,671组；5,008条成员候选中映射212条，余4,796条。family 已登记80组/86条，另8组/8条待登记；person 类型1,086组、1,178条候选，已登记57组、95条候选，待登记1,029组、1,083条。procedure 已登记23组/24条；term 已登记2组/4条；work、place 各登记1组/1条和2组/2条候选。Borghese、Aldobrandini、Ferdinand de’ Medici、Camillo Pamfili、Bellori、Albrizzi、Marchese del Carpio、Sasso、Caravaggio、Pasquali、Johann Wilhelm 与第三代 Shaftesbury 候选已复用既有 KU；Marie de Medici、Lorenzo Onofrio Colonna、Giambattista Ricciardi、Count of Monterey、Cardinal Alessandro Farnese、Alessandro Farnese 公爵、5th Lord Exeter、Carlo Cignani、Gasparo Gozzi、Luigi Celotti、Antonio Zatta、Don Pietro Antonio Toni、Gian Antonio Guardi、Alessandro Algardi、Giorgio Pisani、Francesco Zuccarelli、Pierre Crozat、Alessandro Marchesini、Marcantonio Franceschini、Giustiniana Wynne-Rosenberg、Giovanni Vianello、Bonomo Algarotti、Donna Olimpia Maidalchini、Philip Neri、Pietro Liberi、Niccolò Cassana、Giambattista Marino、Galileo Galilei、Prince Eugene of Savoy、Cardinal Giovan Francesco Negroni、Francesco Bracciolini、Carlo de' Rossi、Francesco Marucelli、Andrea del Rosso、Antonio degli Effetti、Simon Vouet、Cardinal Pier Donato Cesi 已登记为人物 KU。另一个 Naples 语境的 Colonna 候选仍待证。候选待办共有2条且均已关闭；后续继续逐类型处理未登记 S4 组，并优先覆盖 S2 断言直接端点；Giorgio Pisani 的15条、Francesco Zuccarelli 的17条、Pierre Crozat 的14条、Alessandro Marchesini 的16条、Marcantonio Franceschini 的16条、Giustiniana Wynne-Rosenberg 的16条、Giovanni Vianello 的8条、Bonomo Algarotti 的15条、Donna Olimpia Maidalchini 的17条（其中13条为关系候选）、Philip Neri 的16条关系候选、Pietro Liberi 的11条关系候选与 Niccolò Cassana 的16条、Giambattista Marino 的16条、Galileo Galilei 的11条、Prince Eugene of Savoy 的15条、Cardinal Giovan Francesco Negroni 的15条、Francesco Bracciolini 的15条、Carlo de' Rossi 的14条与 Francesco Marucelli 的11条关系候选及其他已登记对象的 S2 关系候选仍待 S6，正式关系未新增。每批记录组、卡路径、来源依据、manifest/accepted 登记及候选映射数量，不因 `new` 决定或总量统计而推定卡片完成。

### person：Giorgio Pisani 跨章直接端点登记（2026-10-16）

- 将 cand-1942 的 new-person:giorgio-pisani-31dda8db5c 组登记为 units/persons/giorgio-pisani，映射1条候选。该候选对应23条直接 S2 断言端点，其中15条标记为关系候选；其余语境/评价类断言仍以原书限定保存。
- 第10章 pp.325–327 以 Giorgio Pisani 全名介绍其 Barnabotti 身份、改革活动、1780年当选 Procuratore di San Marco、相关图像与版画争议，以及其被捕。第20章 p.408 后记回顾 Boscarati 画作引发的政治风波，并通过 Haskell 转述 Olivato 与 Boscarati 审讯证词；卡片保留该转述和作者对作品意图的修正，不把相关关系候选写为正式关系。
- 对照 manifest 未发现 Giorgio Pisani 同名人物 KU；Pisani 家族集体卡不作为个人卡。双语人物卡只写书内身份与来源限定描述，未作外部核验、S5 补足或正式关系登记。人物卡与 S4 批次脚本的 dry-run 核对组成员、候选类型、23条端点、15条关系候选及4处精确引文后通过；apply 登记一组一卡并完成候选映射。manifest 从1,159增至1,160；累计登记141组、177条候选映射，待4,678组、4,811条候选。

### person：Francesco Zuccarelli 跨章身份组登记（2026-10-16）

- 将 cand-2879（UVWXYZ.csv#216 主项）与 cand-2884（UVWXYZ.csv#221，“work in England”子目）按 S3 组 new-person:francesco-zuccarelli-f14976b723 登记为 units/persons/francesco-zuccarelli，映射2条候选。两条候选共有21条直接 S2 断言端点，其中17条标为关系候选。
- 第10章 p.292 全名识别其为风景画家，并记1752年赴英及长期工作；p.308 记其为 Smith 作画，同时明确二人初次接触时间不明、他在一组建筑画中的分工较小。第13章回述 Zanetti 对其早期职业的赏识及 Albrizzi 对他的赞助；第14章记录 Algarotti 为其提出绘画题材；第19章销售目录列出的作品仅称“据说”来自 Smith 收藏。卡片保留这些归属和时间限定，不据题材建议另造作品，也不把关系候选写成正式关系。
- manifest 中无同名人物 KU；UVWXYZ.csv#221 是同一人物的索引子目，不是另一身份。本卡按原书全名作双语标题，记录 S2 证据、拼写变体及身份边界，不做外部核验、S5 补足或 S6 关系登记。批次脚本 dry-run 核对两条组成员、21条端点、17条关系候选和7处精确引文后通过；apply 登记一组一卡、两条候选映射并加入 accepted.yml。manifest 从1,160增至1,161；累计登记142组、179条候选映射，待4,677组、4,809条。


### S3 家族类型跨章身份复核（2026-10-16）

本轮接续既有 family 分组与 S4 登记，逐项复核 `alignment.csv` 中36条 family `undecided` 候选。判定仅涉及身份、类型和既有 KU 映射；不从家族身份推导成员、婚姻或正式关系。

- **复用既有家族 KU（9）**：`cand-1058` → `units/families/foscarini-family-venice`，索引子项与已登记的 Foscarini 主项一致；`cand-1175` → `units/families/del-rosso-family-florence`，G.csv 的 “and del Rosso family” 指家族子项，不指 Luca Giordano；`cand-1658` → `units/families/miani-family-camerata`，注8明确为 Camerata 的 Miani；`cand-4452` → `units/families/sacchetti-family`，Marcello 与 Giulio 的家族礼拜堂语境指 Sacchetti 家族；`cand-6499` → `units/families/rospigliosi-family`；`cand-7157` → `units/families/house-of-savoy`；`cand-7998` → `units/families/medici-family`；`cand-8500` → `units/families/pisani-di-santo-stefano`，保持支系粒度，不并入更宽泛的 Pisani 家族 KU；`cand-10972` → `units/families/pamphili-family`。Rospigliosi 与 Pamphili 的家族—人物锚点分别由 Treccani 家族条目和教皇人物条目补足，外部行新增为 `aln-12592` 与 `aln-12593`，访问日期 2026-10-16：[Rospigliosi](https://www.treccani.it/enciclopedia/rospigliosi/)；[Innocent X](https://www.treccani.it/enciclopedia/innocenzo-x_%28Enciclopedia-dei-Papi%29/)。Villa Pisani 的 Santo Stefano 支系判断沿用既有家族卡所列的官方 Villa Pisani 沿革来源。以上决定不建立家庭成员关系。
- **新建身份组（8）**：`cand-7729` → `sg3-family-buonaccorsi-family`；`cand-8169` → `sg3-family-barbaro-family`；`cand-8301` → `sg3-family-bon-family-venice`；`cand-8356` → `sg3-family-sandi-family`；`cand-9572` → `sg3-family-bourbon-dynasty`；`cand-9573` → `sg3-family-hapsburg-dynasty`；`cand-9574` → `sg3-family-hohenzollern-dynasty`；`cand-9999` → `sg3-family-guardi-brothers`。名称和原书家族／王朝语境足以建立独立 S3 身份组；无完全匹配的既有 family KU，暂不创建 KU，后续进入 S4。
- **类型排除（1）**：`cand-1019` 的索引父项是 Ferrara，子目 Bentivoglio and。它是地名索引对象，不是 Bentivoglio 家族候选；Ferrara 地点由独立候选 `cand-1017` 表示，故从 family 类型排除，不将此行转作 family `new`。
- **继续待证（18）**：`cand-10472, cand-10709, cand-11856, cand-12038, cand-4279, cand-4360, cand-4361, cand-7170, cand-7368, cand-7519, cand-7575, cand-7694, cand-7959, cand-8780, cand-8868, cand-9980, cand-9989, cand-12255`。逐项所需的来源页、具名家族/支系锚点及不合并边界保留在各自 `resolution_note`；包括未具名家庭、同姓异支、Colonna / Pisani 支系、缩写 Manini 和仅在未刊文书中指称的 Falconieri 受托人。遇到这些缺口时，不因同姓、婚姻网络或相邻条目合并，也不强制新建家族 KU。

复核脚本 `reconcile_s3_family_type_closure_20261016.py` 先以 `--dry-run` 核对36条原待证记录、来源锚点、类型与分组，再以 `--apply` 更新18项决定、18条待证路线和两条外部身份行。应用后全表候选决定为 same=1,707、new=4,996、conflict=7、excluded=98、undecided=5,596；new 为4,827组/4,996条候选，S4 已登记162组/207条映射，尚待4,665组/4,789条映射。family 当前为 same=22、new=94（88组）、excluded=1、undecided=18；其中86条 new 候选/80组已有 KU，8条候选/8组待 S4。表内共12,593行，其中12,404条候选决定和189条外部身份记录。全程未改 manifest、accepted.yml、KU 卡、S5、S6 或页面。

### S3 家族：Baglioni 佩鲁贾与威尼斯出版家族复核（2026-10-18）

复核 `cand-4279`（第2章 p.29，Baglioni family chapel in Perugia）与 `cand-7575`（第8章 p.214，Baglioni publishing family in Venice）。原书分别以礼拜堂语境和收藏／出版家族语境指称两者，没有提供具名成员或谱系连接。外部核对（访问日期均为2026-10-18）：Treccani《Baglióni》称其为佩鲁贾的古老封建家族，统治于1540年结束、主支于17世纪消失（https://www.treccani.it/enciclopedia/baglioni/）；Treccani《Dizionario Biografico degli Italiani》Alfredo Cioni 的“BAGLIONI, Tommaso”记威尼斯印刷出版企业由 Tommaso 创始、家族经营延续至1850年，并记1717年入威尼斯贵族（https://www.treccani.it/enciclopedia/tommaso-baglioni_%28Dizionario-Biografico%29/）；Marco Gozzi《Dizionario degli editori musicali italiani》“Baglioni”条目称 Tommaso 出身贝加莫（https://iris.unitn.it/handle/11572/248214）。

这些记录支持两种不同的历史语境，但没有证明出版家族与佩鲁贾家族之间是同支、异支或无亲缘关系；姓氏相同及地理、行业差异不足以单独解决谱系身份。故 `cand-4279`、`cand-7575` 均维持 `undecided`，沿用各自 review 组，不建 KU、不合并也不确认拆分。解除待证所需材料：可把威尼斯出版家族成员连至佩鲁贾家系的谱牒或档案记录，或足以确认其为独立支系的家族来源。此项复核只处理身份，不建立家族关系。


### S3 procedure 类型跨章复核（2026-10-16）

本轮逐项复核原为 `undecided` 的10条 procedure 候选，按程序对象身份与现有 procedure / term KU 比对；不据候选存在推导关系或执行事实。

- **new：6条候选、5个身份组，待 S4 登记。** `cand-0897` → `sg3-procedure-customs-duty-pictures`：原书索引连接 pp.228、374；第8章称宗教题材画作的关税低于世俗画，第16章称画作跨境运输时海关手续棘手。此组只记录书内所述的画作关税待遇，不推断具体税则、税率或法域。`cand-11471` → `sg3-procedure-pieta-plan-selection`：第9章 p.273 记 Pietà 理事须向最受看重且有合适构想的画家征求方案并择优；这是方案遴选程序，与现有装饰 `modelli` 一般审阅或 commission contracting KU 的身份粒度不同。`cand-1514` → `sg3-procedure-manfrin-painter-competitions`：索引 M.csv#51 子目在 p.381 落到 Manfrin 组织画家为其自拟色情题材竞赛作画；与人物 Manfrin 及既有贵族宴席竞赛程序区分。`cand-7498` 与 `cand-12414` 共组 `sg3-procedure-florentine-flour-revenue-concession-1676`：第8章 p.211 说 Andrea del Rosso 与 Lorenzo 分享始于1676年的九年面粉专营权；同页注2将其称为 Appalto Generale，并说明存有授予法令副本。两候选指同一专营权；archive 候选 `cand-7517` 指法令/档案记录本身，不并入程序 KU。`cand-9982` → `sg3-procedure-paintings-for-engraved-reproduction`：第13章 p.333 明确把当代绘画为雕版复制而作列作第二条生产路径，与同段的既有名作复制、为书籍插图而绘制底稿、艺术家自制版画三条路径分别处理；不映射至相邻三项 procedure KU。
- **same：1条候选。** `cand-2423`（S.csv#111，pp.6–8）原标为 procedure。第1章将 `servitù particolare` 明确作为历史作者使用的 patron-artist employment term，并说明其条件；现有 `units/terms/servitu-particolare` 已表达同一术语身份。故将 `entity-candidates.csv` 的 `suggested_type` 从 `procedure` 更正为 `term`，对齐行映射至该既有 KU。此决定不建立某位画家与某位赞助人的具体服务关系。
- **继续待证：3条候选。** `cand-11988` 保留原文关于 Querini 预测房屋拆除、喷泉增水和熄火会导致疟疾的引述；原句不证明这些措施实际提出或施行，待查原报告与发言语境以判明是程序、政策主张还是被转述的预测。`cand-12252` 是 Brenta 防洪计划，Haskell 的注释未给出具体工程或主管机关，且其引用的 BruneUi Bonetti 1951 pp.185–200 尚未独立查阅；待有可识别工程与足够来源后再定 procedure/event 边界。`cand-1610` 是 A.csv#129 “Grand Prince Ferdinand de’ Medici and art exhibitions” pp.240–241，现无法确认是 Florence 的一次展览事件、组织程序还是一般术语；待逐页核实及与展览 term / event 候选比对，不因共同词语并组。

脚本 `reconcile_s3_procedure_type_review_20261016.py` 的 dry-run 校验原10个 procedure 待证 ID、目标 term KU、组唯一性及全表计数后通过；apply 将6条候选置为 new、1条改类并 same、3条保留待证，旧理由逐行保存在新注释内。应用后全表为 same=1,708、new=5,002（4,832组）、conflict=7、excluded=98、undecided=5,589；procedure 为 same=10、new=30、undecided=3，term 为 same=38、new=946、undecided=657、excluded=1。S4 仍为162组/207条映射，待登记4,670组/4,795条候选映射；本轮未创建 KU、未更动 manifest、accepted.yml、S5、S6 或页面。


### S3 跨章身份复核：Ferdinand 的展览实践与1706年佛罗伦萨展览（2026-10-16）

第8章 pp.240–241 与第20章后记跨章比对，复核 `cand-1610`（M.csv#150，Grand Prince Ferdinand de’ Medici “and art exhibitions”）及 `cand-11046`（正文候选 “Florentine art exhibition organized in 1706”）。书内在第8章先述 Ferdinand 利用展览引导佛罗伦萨绘画：他在 Corpus Domini 游行期间公开展示赞赏艺术家的作品，计划展示 Cassana 的肖像，并于1706年组织更大规模的展览；展览于圣路加日（10月18日）在 Annunziata 修道院回廊中举行，有印刷目录，Ferdinand 本人到场。后记据后续研究确认其参与1706年展览的作用，同时指出新发现的1705年目录修正了 Haskell 关于 Ferdinand 开创该展览做法的原判断。

- `cand-1610` 的索引范围覆盖其展览使用方式与艺术引导，是 `procedure`：新组 `sg3-procedure-ferdinand-art-exhibition-guidance`。它代表在多种场合使用展览引导本地绘画的做法，不与事件或现有艺术家自我宣传程序合并。
- `cand-11046` 是具体的1706年 Florence 展览 `event`：新组 `sg3-event-florentine-art-exhibition-1706`。第8章与后记指向同一场活动；Ferdinand 的确切组织作用沿用后记的修正限定。1705年目录所指活动与1715、1724、1729、1737、1767年展览不并入本组。

两项都由 `undecided` 改为 `new`，分别进入 procedure 与 event 身份组；未因主题相近作跨类型 `same`，也未新增 KU、外部标识或正式关系。脚本 `reconcile_s3_ferdinand_florentine_exhibitions_20261016.py` dry-run 校验两条原决定、候选类型与组号后通过，再 apply 写回；原待证理由保留在 `resolution_note` 历史部分。

应用后全表为 same=1,708、new=5,004（4,834组）、conflict=7、excluded=98、undecided=5,587；procedure 为 same=10、new=31、undecided=2；event 为 same=7、new=218、undecided=132。S4 仍为162组/207条映射，待登记4,672组/4,797条候选映射；本轮未创建 KU、未更动 manifest、accepted.yml、S5、S6 或页面。


### S3 跨章并组：Sasso 遗集1803年拍卖（2026-10-16）

逐条核对第16章与第17章的同事件候选。`cand-11549` 指 Sasso 生前自藏在其去世后于1803年拍卖；`cand-10715` 指 Correr 几乎可以肯定在同一 Sasso 1803年拍卖中购得 Zocchi 的 Zanetti 与 Marchese Gerini 双人肖像。两项具有相同被拍卖藏品、事件名称、年份与上下文，故把 `cand-11549` 从 `undecided` 改为 `new`，加入原有新事件组 `sg3-event-cand-10715`；不是另建一次拍卖事件。Haskell 引用的 Catalog de quadri 目录未在本轮独立查阅，记录仅支持“书内同指一场拍卖”的身份裁决，不作为目录内容核验。

脚本 `reconcile_s3_sasso_1803_sale_cross_chapter_20261016.py` dry-run 核验 `cand-10715` 的已有 new 组、`cand-11549` 的原 undecided 决定和两条 event 类型后通过；apply 保留旧理由并完成并组。当前跨章 event 组有两条候选：`cand-10715`、`cand-11549`。全表现为 same=1,708、new=5,005（4,834组）、conflict=7、excluded=98、undecided=5,586；S4 已登记162组/207条映射，待登记4,672组/4,798条候选映射。本轮无 KU、外部标识、S5、S6 或页面改动。


### S3 事件类型补充裁决：跨章候选与既有事件组（2026-10-16）

复核正文事件候选与相关索引子目后，将10个可由原文识别的独立事件／系列从 `undecided` 裁为 `new`：

| 候选 | S3 身份组 | 决定依据与边界 |
|---|---|---|
| `cand-10532` | `sg3-event-cand-10532` | 第15章 p.369 明确 Querini 于1777年赴瑞士并访问 Voltaire，同行者为 Girolamo Festari；仅确认该次行程，不补写完整路线。 |
| `cand-11601` | `sg3-event-cand-11601` | 第3章 p.79 记 Courtois 于1676年去世及 Gesù 祭坛工程随之停摆；事件与人物、未完成工程分立。 |
| `cand-11625` | `sg3-event-cand-11625` | 第3章 p.91 记 Padre Nickel 提议以秘鲁遗产装饰 Gesù 小堂、此议未获西班牙人欢迎而搁置；不推定资金转移或工程执行。 |
| `cand-11725` | `sg3-event-cand-11725` | 第5章 p.125 可识别为1607年罗马展出《圣母之死》的具体场次；场地和正式活动名称未见于该段，故不补定。 |
| `cand-11728` | `sg3-event-cand-11728` | 第5章 p.125 的罗马 Bergamasque 团体圣巴多罗买节系列，8月24日举办、1650年前已兴盛；起始年份未知。 |
| `cand-11736` | `sg3-event-cand-11736` | 第5章 p.125 另称 S. Bartolomeo all'Isola 举办该圣人命名日展览，地点与组织语境有别，单列系列。 |
| `cand-11879` | `sg3-event-cand-11879` | 第2章 p.33 明确为1593年 Henri IV reconciliation；保留 Haskell 对其作用的叙述，不标作独立核实。 |
| `cand-11932` | `sg3-event-cand-11932` | 第5章 p.138 指 Urban VIII 去世后法国影响结束；第6章 p.146 将其置于1644年3月和平之后。`cand-6260` 是随后召开、身份有别的 conclave。 |
| `cand-11942` | `sg3-event-cand-11942` | 第5章 p.143 注释记1701年 S. Salvatore in Lauro 展览及 Raggi 借展五幅 Cerquozzi 画；与12月常设系列 `cand-6051` 及1675、1697年场次分立，不推定系列归属。 |
| `cand-11955` | `sg3-event-cand-11955` | 第6章 p.146 明确 Giambattista Pamfili 当选 Innocent X；与人物 KU 及 Urban VIII 死后的 conclave (`cand-6260`) 分立。 |

另将索引候选 `cand-1821`（P.csv#20，“dispute over burial of”，p.150）与正文候选 `cand-6297`（Innocent X 葬礼费用争议）并入 `sg3-event-cand-6297`。父级索引标题是人物，但该子目指向事件；没有并入 Innocent X 人物 KU。审查了邻近事件组，包括 S. Salvatore in Lauro 的 recurring series 与已识别的1675、1697年场次、Urban VIII 死亡与其后 conclave、Henri IV reconciliation 与其后刺杀，以及第5章两种不同圣巴多罗买展览系列。

批次脚本 [复核脚本](reconcile_s3_event_cross_chapter_batch_20261016.py) 的 dry-run 核对11条原待证候选、事件类型、索引子目/正文锚点、唯一组与既有 burial-cost 事件组后通过，再 apply。决定后全局 `same=1,708`、`new=5,016`（4,844组）、`undecided=5,575`、`conflict=7`、`excluded=98`；event 为 `same=7`、`new=230`、`undecided=120`。S4 仍待登记4,682组、4,809条候选映射；无新 KU、外部身份记录或正式关系。尚未定位到同一原文场景或无法判明系列/单次场次边界的事件仍留 `undecided`，继续按其对齐行 `source_ref` 回到对应章节复核。

### S3 更正：Chiesa Nuova 索引候选复用既有地点 KU（2026-10-16）

`cand-0710`（C.csv#234，Rome 下 “S. Maria della Vallicella (Chiesa Nuova)” 子目）原裁为 `new`，组 `sg3-place-cand-0710`。复核发现该索引名称与已接受的 `units/places/chiesa-nuova` 完全对应：既有 KU 类型为 place，标题为“罗马新教堂（Chiesa Nuova, Rome）”，其卡片保留 Rome、Santa Maria in Vallicella 与 Chiesa Nuova 的身份依据；全书 S2 也把三者置于同一替换教堂及其建造语境。故将 `cand-0710` 更正为 `same` 并映射至该既有 KU，不另建卡。原 `new` 组号和裁决理由保存在对齐行历史注释中。

该候选是 Pier Donato Cesi 的3条直接关系候选对端。复用后，Cesi 的11条直接关系候选对端全部映射到既有 KU；正式关系仍待 S6，不因端点齐备自动成立。S4 新组总量减少1组、1条候选，已登记数和 manifest 不变：`same=1,709`、`new=5,015`（4,843组）、`undecided=5,575`、`conflict=7`、`excluded=98`；S4 已登记163组/208条，待登记4,680组/4,807条。现有 same KU 去重数仍为1,025。本批未修改 manifest、accepted.yml、既有 Chiesa Nuova 卡或正式关系表。


### S3 跨章复核：威尼斯共和国候选复用与政府机构待证（2026-10-16）

对照既有 `units/institutions/republic-of-venice` 及其 accepted KU，将6条书内候选复用至同一政治实体；`cand-3678` 是既有全书锚点，所有新决定均追加保留原 `new` 组和理由：

| 候选 | 来源锚点 | S3 去向 |
|---|---|---|
| `cand-6255` | 第6章 p.146，Venice 与 France、Tuscany、Modena 联合反对 Barberini 扩张 | `same` → Republic of Venice；“Venice”在此是政治行动者，不是城市。 |
| `cand-8105` | 第9章 p.245，政府推动旅游同时限制外来影响 | `same` → Republic of Venice；Haskell以 government / State 叙述同一主权政治实体及其治理行为，没有另指独立命名的机关。39条直接 S2 关系候选继续保留原词。 |
| `cand-8572` | 第9章 p.263，Sagredo 家族向共和国贡献 Doge Niccolò | `same` → Republic of Venice；正文直接称 Republic。 |
| `cand-8838` | 第10章 p.276，Lord Manchester 与共和国发生争执后离开 | `same` → Republic of Venice；正文直接称 Republic。 |
| `cand-9789` | 第10章 p.325，Barnabotti 与政府、全邦公共利益及改革语境 | `same` → Republic of Venice；这里是威尼斯政治实体的治理语境，未具名另一机关。 |
| `cand-9874` | 第10章 p.331，State interference in the arts | `same` → Republic of Venice；`State`为政治权力指称，没有指名独立部门。 |

`cand-8668`（第9章 p.267）暂改为 `undecided`：Haskell 明说 “Within the State itself ... the government”，区分国家与政府，但未命名该政府机构，也未说明其与 Republic KU 的实体边界。不能把该政府强并为共和国，也不凭一个泛称先创建新机关卡。后续须有来源识别具体机构或足以确定其治理实体边界；在此之前保持待证并阻断相关关系端点。

脚本 dry-run 核对7条原 `new` 决定、各自书内原文、6条 existing-KU 复用映射、1条待证去向及候选组唯一性。应用后候选决定为 `same=1,715`、`new=5,008`、`undecided=5,576`、`conflict=7`、`excluded=98`；same 的唯一既有 KU 仍为1,025。S4 已登记163组/208条映射，待登记4,673组/4,800条；manifest、accepted.yml 与 formal relations 未变。


### S3 补充裁决：Art dealers 候选复用既有画商术语 KU（2026-10-16）

`cand-0125`（A.csv#126；第5章 pp.120–137）与 `cand-0126`（A.csv#127；第16章 pp.377–378）原属 `new` 组 `sg3-term-artdealers`。两者共对应 28 条直接 S2 端点陈述，其中 23 条标为关系候选。第5章将专业画商作为职业／市场角色，讨论其与画家、买家、交易、税务和经营的关系；第16章以 Celotti 为具体人物并以“some of the humbler dealers so far recorded”回指先前同类画商。现有术语 KU `units/terms/art-dealer` 的范围正是买卖或中介艺术品的职业角色，且涵盖本书相应历史语境；候选没有指向独立命名的组织或边界明确的另一个术语。故两条候选由 `new` 改为 `same`，映射至 `units/terms/art-dealer` 及既有同一性组 `sg3-ku-units-terms-art-dealer`。原决定与理由逐字保存在 `alignment.csv` 的 `previous_resolution_note`；原书跨章锚点与语义依据如上。本裁决不新增 KU，不改动来源断言、候选关系或正式关系。

裁决后 S3 为 same=1,717、new=5,006（4,835组）、undecided=5,576、conflict=7、excluded=98；S4已登记165组/212条候选映射，待登记4,670组/4,794条。脚本 `reconcile_s3_art_dealers_existing_term_20261016.py` 以 `--dry-run` 核对后 `--apply` 写回。

### person：Giovanni Battista Agucchi 单候选跨章身份组登记（2026-10-16）

- `cand-0018`（A.csv#17）是单成员 S3 组 `new-person:agucchi-battista-giovanni-9239cc0f09`，登记至 `units/persons/giovanni-battista-agucchi`。索引列 pp.28、159、397–398；第2章称 Monsignor Agucchi，后记以 Giambattista Agucchi 作姓名锚点。卡片采用书内规范全名，保留后记对早年经历的限定；对委托／购买的无确证建议不写成确定事实。
- 13条直接 S2 陈述中11条为关系候选，涉及10个对端候选：Annibale Carracci、Domenichino 两端已映射；6个 term 新身份仍待 S4；2个后记对象候选仍为 `undecided`。所有关系候选继续待 S6；本批不增加正式边，也未作外部身份核验或 S5 补足。
- 批次脚本 dry-run 核对单成员组、5处精确来源引文、13条直接陈述及关系对端去向后通过。manifest 从1,184增至1,185；累计登记166组、213条候选映射，余4669组、4793条。person 类型已登记58组/96条，余1,028组/1,082条。脚本：`register_s4_person_agucchi_batch_20261016.py`。


### S3 类型纠偏：Bernardo Bellotto 的作品索引子目（2026-10-16）

- `cand-0279` 与 `cand-0281` 保留在人物组 `new-person:bellotto-bernardo-3bfd904005`；两条索引主目与第10章 pp.295、298 的 Bernardo Bellotto 指称相互对应。
- `cand-0280` 从 person 改为 work，单独进入 `sg3-work-bellotto-cross-church-ruins`。索引 B.csv#129 的子目是“painting of ruins of Church of the Cross, Dresden”；S2 断言 `st-chp10-p295-cross-church-painting` 另列 Bellotto 为人物端点、该绘画为作品端点。
- 第10章 p.295 仅支持描述性作品名，不提供原题名、媒材、现藏地或作品存续状态。Dresden Church of the Cross 地点候选保持独立；候选 `cand-9110` 所指的多幅城市景观集合仍为 `undecided`，不与此单件作品合并。无现有同一作品 KU，也未作外部身份核验。原 S3 判断保存在三条对齐行的历史说明中。
- 纠偏后全局 S3：same=1,717、new=5,006（4,836 组）、undecided=5,576、conflict=7、excluded=98。person 新组 1,086/1177 候选，其中 S4 已登记 58 组；work 新组 481/494 候选，其中 S4 已登记 1 组。


### person / work：Bernardo Bellotto 与十字教堂废墟绘画 S4 登记（2026-10-16）

- 人物组 `new-person:bellotto-bernardo-3bfd904005` 的 `cand-0279`、`cand-0281` 共映射至 `units/persons/bernardo-bellotto`（04-knowledge/units/persons/bernardo-bellotto.md）；依据第10章 pp.295、298。人物组11条直接 S2 陈述中10条为关系候选，9个不同对端中7个已裁为 new、2个仍 undecided。
- 作品组 `sg3-work-bellotto-cross-church-ruins` 的 `cand-0280` 映射至 `units/works/bellotto-ruins-church-of-the-cross-dresden`（04-knowledge/units/works/bellotto-ruins-church-of-the-cross-dresden.md）；依据索引 B.csv#127 与第10章 p.295 的作品端点陈述。作品名称是描述性标题，不补原题名、媒材、现藏地或存续状态。
- `st-chp10-p295-cross-church-painting` 现在两端均有 KU；正式创作关系仍待 S6。本批未新增关系或外部核验，未执行 S5。
- 批次 dry-run 核对2组、3条候选映射、6处原文引文和现有登记外键；manifest 从1,185增至1,187，S4 累计登记168组/216条成员候选，待登记4,668组/4,790条。

### S3 类型纠偏：Antonio Bellucci 的 Canons 天花作品索引子目（2026-10-16）

- `cand-0282` 保留为人物组 `new-person:antonio-bellucci-f1e7b7cdb6`；`cand-0283`（“Descent from the Cross”）与 `cand-0284`（“Nativity”）根据 B.csv#130–131 和第10章 p.281，从 person 改为 work，并各自进入独立作品组。
- S2 断言 `st-chp10-p281-bellucci-canons-large-canvases` 将三幅大型天花画分别列为 The Nativity、The Descent from the Cross、The Ascension，并将前两项映射至索引子目；故两件作品不并为一件，也不并入 `cand-8945` 所指的三幅画集合。原 S3 分组理由保存在对齐行历史说明中。
- 作品名按索引主题作描述性呈现；本次未补原题名、单件媒材、尺寸或现状。未发现同一 Bellucci/Canons 作品 KU，未作外部核验。
- 纠偏后全局 S3：same=1,717、new=5,006（4,838 组）、undecided=5,576、conflict=7、excluded=98。person 新组 1,086 组/1,175 候选，已登记 59 组/98 候选；work 新组 483 组/496 候选，已登记 2 组/2 候选。


### person / work：Antonio Bellucci 与两件 Canons 作品 S4 登记（2026-10-16）

- `cand-0282` 从 `new-person:antonio-bellucci-f1e7b7cdb6` 登记至 `units/persons/antonio-bellucci`（04-knowledge/units/persons/antonio-bellucci.md）；索引页码包括227、278、280–281、283–284、294及405–406，人物卡引述第10章 p.278、281 与第20章后记 p.406，并保留 Hapsburgs 的边界与 Vienna 年代的可能性限定。直接 S2 陈述 12 条，关系候选 11 条；对端决定 {'undecided': 6, 'new': 5}，均待后续关系阶段。
- `cand-0283` 与 `cand-0284` 分别登记至 `units/works/antonio-bellucci-descent-from-the-cross-canons` 和 `units/works/antonio-bellucci-nativity-canons`；索引 B.csv#130–131 与 p.281 集合描述共同支持两个单件作品。描述性标题不作原题名声明；集合候选 `cand-8945` 保持独立。
- 两作品的创作端点虽由原书在集合画作叙述中共同说明，正式关系仍待 S6 逐端点审核；本批不新建关系，不做外部核验或 S5 补足。
- dry-run 核对3个 S3 成员、3张卡片、5处原文引文及登记外键；manifest 从1,187增至1,190，S4 累计登记171组/219条成员候选，待登记4,667组/4,787条。

### person：Frederick the Great 跨章身份组 S4 登记（2026-10-16）

- `cand-1079` 与 `cand-1080` 共登记至 `units/persons/frederick-the-great`（04-knowledge/units/persons/frederick-the-great.md）；索引 F.csv#96–97，直接证据跨第10章 p.295、311 与第14章 pp.349、356–360。
- 12条直接 S2 陈述中11条为关系候选；10个不同对端决定为 {'same': 5, 'undecided': 1, 'new': 2, 'conflict': 2}。注5转述 Fantuzzi 对两幅画的赞助说法，并同时引用 letters/inventory 支持 Algarotti；本卡不把相反报告强行裁成确定赞助关系。
- 人物卡保留“later the Great”、轰炸归因及柏林艺术中心计划等来源限定；本批不新增正式关系，不作外部身份核验或 S5 补足。
- dry-run 核对唯一2成员组、5处引文、12条直接陈述、11条关系候选及候选映射；manifest 从1,190增至1,191，S4 累计登记172组/221条映射，待登记4,666组/4,785条。

### S3 身份补裁：Pietro Monaco 经纪活动索引子目归组（2026-10-16）

- `cand-1682`（M.csv#222，pp.342n、345）与 `cand-1683`（M.csv#223，“activities as dealer”）均为同一 Pietro Monaco 主目下的人物候选。p.342 注5称其为版画师；p.345 正文称“Monaco himself”，并称其用版画宣传本人经纪活动；同页索引子目对应此活动，支持并入同一人物身份组。
- `cand-1683` 从 `undecided` 裁为 `new`，归入 `new-person:monaco-pietro-2f390e5d35`，与 `cand-1682` 共用一个 S4 KU。保留 Haskell 对宣传意图的“almost certainly”限定；版画、出版物及其他 Monaco 同名候选不据此合并。旧待证理由与新证据去向均保存在对齐行。原注释提及的版画与书目未独立查阅。
- 更新后全局 S3：same=1,717、new=5,007（4,838 组）、undecided=5,575、conflict=7、excluded=98。person 新组 1,086 组/1,176 候选，S4 已登记 61 组/101 条，待登记 1,025 组/1,075 条。


### person：Pietro Monaco 跨章人物身份组 S4 登记（2026-10-16）

- `cand-1682`、`cand-1683` 共登记至 `units/persons/pietro-monaco`（04-knowledge/units/persons/pietro-monaco.md）；覆盖 M.csv#222–223、第8章 p.214 注4及第13章 pp.342n、345。`cand-1683` 在 S3 从 `undecided` 改为与主目同组，S4 映射到同一人物卡。
- 12条直接 S2 陈述中11条为关系候选；10个不同对端的决定为 {'undecided': 6, 'new': 4}。书中版画师、收藏及经纪活动的关系证据继续留待 S6；无正式关系写入。
- 卡片保留 “almost certainly” 对宣传意图的限定、4 February 1763/4 的日期歧义及打印版次映射未决；版画、出版物和信件未独立查阅。
- dry-run 核对唯一2成员组、6处来源引文、12条直接陈述、11条关系候选及登记外键；manifest 从1,191增至1,192，S4 累计登记173组/223条候选映射，待登记4,665组/4,784条。

### S4 archive：Luigi Pavini 直接关系端点小册子登记（2026-10-16）

cand-8789（archive-group-4a4d65fbc201）映射至 [1734年威尼斯赤足加尔默罗会小册子卡](../../../04-knowledge/units/archives/venice-scalzi-pamphlet-1734.md)。第九章 p.269 注5记录原题、32页、M.A.作者形式、Luigi Pavini为出版者、Biblioteca Marciana, Misc. 1135, n. 3 馆藏定位，并注明参见 Ferrari 1882；小册子与 Ferrari 均未独立查阅。出版者候选 cand-12425 已映射至 Luigi Pavini 人物卡，该出版关系仍待 S6 审查；馆藏定位不在本批升级为正式关系。相关短引候选 cand-8777 保持 undecided，未并入本卡。登记前 archive 直接关系对象有一个 new 身份组待映射，本批完成该组；S4 累计登记174组/224条成员候选，待登记4,664组/4,783条。

### S4 institution：Biblioteca Marciana 跨章身份组登记（2026-10-16）

cand-9448（sg3-institution-cand-9448）映射至 [Biblioteca Marciana 机构卡](../../../04-knowledge/units/institutions/biblioteca-marciana.md)。S2 共记录11处跨章提及；第九、十、十三、十七章的引文均将该名称用作馆藏定位。三条直接关系候选为宣传册组、Zanetti 卷册和 Manfrin 小册子定位，仍留待 S6；不推定当前馆藏、不核验外部目录，也未新增正式关系。第十章 p.293 注2 的 OCR 拼作 Bibiioteca，p.301及第十三章 p.341 转录作 Biblioteca；卡片保留该转录差异，不把它另分为身份。S4 累计登记175组/225条成员候选，待登记4,663组/4,782条。

### S4 archive：Biblioteca Marciana 的三个直接文献端点登记（2026-10-16）

分别登记 [cand-12115](../../../04-knowledge/units/archives/pisani-entry-pamphlet-set-1780.md)、[cand-10199](../../../04-knowledge/units/archives/zanetti-marciana-manuscript-volume-cxvi-7356.md)、[cand-10683](../../../04-knowledge/units/archives/manfrin-pamphlet-risposta-1797.md)。cand-12115 是皮萨尼1780年当选后的宣传册集合；cand-10199 是 Zanetti 笔记与书信所在的卷册；cand-10683 是 Haskell p. note 8 所引1797年 Manfrin 相关小册子。三者分别是集合、包含多件材料的卷册、单件出版物，不相互合并。三组共对应8条直接 S2 陈述/关系候选，均留待 S6；本批不新增正式关系或外部目录核验。cand-10205 的七封 Tessin 来信继续作为独立 archive 组，不并入 cand-10199。cand-10683 候选规范名作 imparziale，而 OCR 行 L10 作 impacciale；未校扫描页，保留该拼写待核。S4 累计登记178组/228条成员候选，待登记4,660组/4,779条。

### S4 archive：Lione Pascoli《Vite》第一卷直接引文端点登记（2026-10-16）

cand-4834（archive-group-31f7e821ab60）登记至 [利奥内·帕斯科利《现代画家、雕塑家与建筑师传》第一卷（1730）](../../../04-knowledge/units/archives/lione-pascoli-vite-dei-pittori-vol-i.md)。第21章书目 p.433 将第一卷列为1730年，并记第二卷为1736年及1933年罗马影印版；本卡只登记第一卷。第1章 p.7 注2与第7章 p.187 注4提供跨章引用示例。该候选对应24条直接 S2 陈述，其中22条为关系候选；Haskell所引Pascoli页未独立查阅，卷二 cand-4552 保持独立 new 组。未新增正式关系、外部核验或 S5 补足。S4 当前登记179组/229条成员映射，尚待登记4,659组/4,778条。

### S4 archive：Lione Pascoli《Vite》第二卷直接引文端点登记（2026-10-16）

cand-4552（archive-group-7885c306cd0f）登记至 [利奥内·帕斯科利《现代画家、雕塑家与建筑师传》第二卷（1736）](../../../04-knowledge/units/archives/lione-pascoli-vite-dei-pittori-vol-ii.md)。第21章书目 p.433 将第二卷列为1736年，并记第一卷为1730年及1933年罗马影印版；本卡只登记第二卷。第1章 p.18 注4与第7章 p.187 注4提供跨章引用示例。该候选对应19条直接 S2 陈述，其中16条为关系候选；Haskell所引Pascoli页未独立查阅，卷一 cand-4834 已登记为另一 KU。未新增正式关系、外部核验或 S5 补足。S4 当前登记180组/230条成员映射，尚待登记4,658组/4,777条。

### S4 archive：Zanotti《Storia dell’Accademia Clementina》两卷本登记（2026-10-16）

cand-7115（archive-group-e45ca62cc403）登记至 [G. P. Zanotti《克莱门蒂娜学院史》两卷本（博洛尼亚，1739）](../../../04-knowledge/units/archives/zanotti-storia-accademia-clementina-1739.md)。第21章 p.441 书目列责任者形式 G. P. Zanotti、书名、两卷本及博洛尼亚1739年；不将 initials 扩写为全名。第7章 p.189 注4、注5示例分别引用卷一及卷二。该候选对应27条直接 S2 陈述，其中14条为关系候选；原书和被引页未独立查阅。本批无正式关系、外部核验或 S5 补足。S4 当前登记181组/231条成员映射，尚待登记4,657组/4,776条。

### S4 archive：De Dominici《Vite》第四卷直接关系端点登记（2026-10-16）

cand-4835（archive-group-4fa823613e1b）登记至 [贝尔纳多·德·多米尼奇《那不勒斯画家、雕塑家与建筑师传》第四卷（1843）](../../../04-knowledge/units/archives/de-dominici-vite-napoletane-vol-iv-1843.md)。第21章 p.421 书目列全套四卷本及1843年那不勒斯版；第3章 p.78 注1、第7章 p.189 注6明确引用第四卷。本卡的对象范围限于卷级引文目标，未查阅原书或被引页。全套书目候选 cand-11317 仍为 undecided，未并组、未映射，也未据此建立 part_of 关系。该候选对应24条直接 S2 陈述，其中13条为关系候选；本批无正式关系、外部核验或 S5 补足。S4 当前登记182组/232条成员映射，尚待登记4,656组/4,775条。

### S4 family：余下明确身份组登记（2026-10-16）

- cand-7729 → sg3-family-buonaccorsi-family → units/families/buonaccorsi-family；直接 S2 断言 5 条、其中关系候选 4 条；本批未将其写成正式边。
- cand-8169 → sg3-family-barbaro-family → units/families/barbaro-family；直接 S2 断言 1 条、其中关系候选 1 条；本批未将其写成正式边。
- cand-8301 → sg3-family-bon-family-venice → units/families/bon-family-venice；直接 S2 断言 0 条、其中关系候选 0 条；本批未将其写成正式边。
- cand-8356 → sg3-family-sandi-family → units/families/sandi-family；直接 S2 断言 5 条、其中关系候选 3 条；本批未将其写成正式边。
- cand-9572 → sg3-family-bourbon-dynasty → units/families/bourbon-dynasty；直接 S2 断言 0 条、其中关系候选 0 条；本批未将其写成正式边。
- cand-9573 → sg3-family-hapsburg-dynasty → units/families/hapsburg-dynasty；直接 S2 断言 0 条、其中关系候选 0 条；本批未将其写成正式边。
- cand-9574 → sg3-family-hohenzollern-dynasty → units/families/hohenzollern-dynasty；直接 S2 断言 0 条、其中关系候选 0 条；本批未将其写成正式边。
- cand-9999 → sg3-family-guardi-brothers → units/families/guardi-brothers；直接 S2 断言 1 条、其中关系候选 1 条；本批未将其写成正式边。

逐卡按双语字段和原文引文登记；没有把未列名成员、支系、肖像、税率、程序步骤或作品归属补猜为事实。程序类中，1706年佛罗伦萨展览事件与 Ferdinand 的展览引导做法分组；Florentine 面粉收入专营权与授予法令档案分开；Pietà 方案遴选保留 Haskell 的 seems 限定。全部正式关系继续留待 S6，未开展 S5。

S4 当前已登记190组/240条成员映射，尚待登记4,648组/4,767条。

### S4 procedure：余下明确身份组登记（2026-10-16）

- cand-0897 → sg3-procedure-customs-duty-pictures → units/procedures/customs-duty-on-pictures；直接 S2 断言 0 条、其中关系候选 0 条；本批未将其写成正式边。
- cand-1514 → sg3-procedure-manfrin-painter-competitions → units/procedures/manfrin-painter-competitions；直接 S2 断言 0 条、其中关系候选 0 条；本批未将其写成正式边。
- cand-1610 → sg3-procedure-ferdinand-art-exhibition-guidance → units/procedures/ferdinand-art-exhibition-guidance；直接 S2 断言 0 条、其中关系候选 0 条；本批未将其写成正式边。
- cand-7498, cand-12414 → sg3-procedure-florentine-flour-revenue-concession-1676 → units/procedures/florentine-flour-revenue-concession-1676；直接 S2 断言 2 条、其中关系候选 2 条；本批未将其写成正式边。
- cand-9982 → sg3-procedure-paintings-for-engraved-reproduction → units/procedures/paintings-for-engraved-reproduction；直接 S2 断言 1 条、其中关系候选 0 条；本批未将其写成正式边。
- cand-11471 → sg3-procedure-pieta-plan-selection → units/procedures/pieta-plan-selection；直接 S2 断言 1 条、其中关系候选 1 条；本批未将其写成正式边。

逐卡按双语字段和原文引文登记；没有把未列名成员、支系、肖像、税率、程序步骤或作品归属补猜为事实。程序类中，1706年佛罗伦萨展览事件与 Ferdinand 的展览引导做法分组；Florentine 面粉收入专营权与授予法令档案分开；Pietà 方案遴选保留 Haskell 的 seems 限定。其引文位于 OCR L72，前置页标 L70 为 [Page 274]；本批将旧 S3 过程所记 p.273 更正为印刷页274。全部正式关系继续留待 S6，未开展 S5。

S4 当前已登记196组/247条成员映射，尚待登记4,642组/4,760条。

### S3 跨章复用纠偏：科尔托纳巴贝里尼宫大天花画（2026-10-16）

cand-4687 原裁为新 work 组 workgrp-e046c2fab34446。复核第2章 p.52 L99 的正文明确称 great Barberini ceiling (Plate 13)；章前图版目录 p.xii L59–60 将 Plate 13 标为 Pietro da Cortona: Glorification of the Reign of Urban VIII，并列出 Palazzo Barberini。正文与图版目录的直接交叉指称证明二者是同一作品，故改为 same 并映射至既有 KU units/works/pietro-da-cortona-glorification-of-the-reign-of-urban-viii。cand-4080 已映射至同一 KU；候选因此复用既有作品卡，不新建重复卡。候选 cand-4582 为该天花画中的 Forge of Vulcan 场景，仍保留独立 work 身份组，不在本批合并或创建正式部分关系。该候选的18条关系候选继续留待 S6。S3 决定数现为 same=1,718、new=5,006（4,837组）、conflict=7、excluded=98、undecided=5,575；S4 新组登记数不变。

S4 当前已登记196组/247条成员映射，尚待登记4,641组/4,759条。

### S3 跨章复用纠偏：Albrizzi 1745 年《耶路撒冷解放》插图本（2026-10-16）

cand-9990 原裁为新 archive 组 archive-group-0a3583f7dde3。第13章 p.335 L36 明称 Albrizzi 于1745年推出 Gerusalemme Liberata 并回指 Plate 57a；章前图版目录 p.xv L135 将 Plate 57a 说明为 Piazzetta 为该书绘制的插图末页，并记出版者 Albrizzi 与年份1745。正文与图版目录指向同一版次，故 cand-9990 改为 same，复用既有 archive KU units/archives/gerusalemme-liberata-illustrations-1745；cand-3600 已映射至该 KU。原书并非新增知识元，本批未改卡、manifest 或 accepted。该候选涉及的参与者、赞助、出版和版本关系仍留待 S6 依具体证据审查。

S4 当前已登记196组/247条成员映射，尚待登记4,640组/4,758条。

### S3 跨章身份补裁：Canaletto 人物与 Poussin 作品、Canaletto 入城图（2026-10-16）

本轮复核 person 与 work 未决簇，直接比较书内索引、S2 提及/断言及既有 KU：

- `cand-0498`–`cand-0503` 与 `cand-0506`–`cand-0528` 共29条 person 候选，分别对应 C.csv#22–27、#30–52。索引的主项均为 Canaletto，子目记录其活动和作品关联；既有人物 KU `units/persons/canaletto` 将 Canaletto 作为 Giovanni Antonio Canal 的惯用名。原书相关候选提及跨第8–10、13–20章，共113条，故29条均改为 `same` 并映射至同一既有人物 KU。此为本书语境内的身份复用，不新增外部标识或传记事实。C.csv#28–29 并非人物子目，而是两个独立作品候选，分别单独裁决。
- `cand-0504` 对应 C.csv#28。第10章 p.277 注5 明确记 Canaletto 绘制 Comte de Gergy 入城图，年份1725；`cand-0505` 对应 C.csv#29，同注记 Count of Bolagno 入城图，年份1729。两件作品题名、对象称谓和年份不同，且 manifest 无对应作品 KU，故分别裁为 `new`，组号为 `sg3-work-canaletto-entry-comte-de-gergy-1725` 与 `sg3-work-canaletto-entry-count-bolagno-1729`。不推定两位称谓对应人物的身份；作者、位置等陈述继续留作关系候选，不在 S3 写正式边。
- `cand-2016`（P.csv#219）索引同列页10注与95；第4章 p.95 注1定位尚蒂伊版本，既有 KU `units/works/poussin-massacre-innocents` 对应第1章同一书内索引项，并保留具体版本识别边界，故复用该卡。`cand-2018`（P.csv#221）《Moses trampling on Pharaoh's Crown》与既有图版19a作品卡题名一致；`cand-2019`（P.csv#222）《Plague at Ashdod》与 Poussin 既有作品 KU 同题、同作者。三项均由 `undecided` 改为 `same`，不新增作品卡、不将 Reni 同题作并入，也不据身份映射新增关系。

复核脚本 `reconcile_s3_canaletto_and_poussin_work_identities_20261016.py` 以 `--dry-run` 核对候选类型、索引自然键、原书断言、现有 KU 和新组唯一性后通过，再 `--apply` 写回；每条原待证理由以 `prior_resolution_note` 保留。应用后全局候选决定为 same=1,751（1,025个既有 KU）、new=5,007（4,838组）、conflict=7、excluded=98、undecided=5,541；S4 已登记196组/247条候选映射，待登记4,642组/4,760条。全表12,404个候选均有一条决定、非空裁决说明与过程引用；189条外部标识记录单独计数。分类型现状见[当前结果](../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。本轮未改 KU 卡、manifest、accepted.yml、外部标识、S5 补足或 S6 正式关系。


### S4 institution：Remondini 跨章身份组登记（2026-10-16）

`cand-2122`（Q-R.csv#49，第15章书目出版者指称）与 `cand-2123`（Q-R.csv#50，第13章印刷商行）均映射至[伦多尼印刷商行机构卡](../../../04-knowledge/units/institutions/remondini-firm.md)。第13章称其设于 Bassano、在 Venice 有分支并从事印刷出版；第15章 p.367 注2列有 Bassano [Remondini], 1787。后者按 Haskell 书目指称记录，未独立查阅该版。S2 共有20条直接陈述，其中16条是关系候选，全部留待 S6；不扩展为 Remondini 家族成员身份，不新增正式关系，也未进行外部核验或 S5 补足。S4 累计登记197组/249条成员映射，待登记4,641组/4,758条。

### S4 event：S. Andrea al Quirinale 教堂重建工程登记（2026-10-16）

`cand-5309`（`sg3-event-cand-5309`）登记至[奎里纳尔山圣安德烈初学院教堂重建工程卡](../../../04-knowledge/units/events/s-andrea-al-quirinale-rebuilding-project.md)。S3 类型为 event；既有 S. Andrea al Quirinale KU 是 place，二者保持分开。第3章 pp.85–87 记录项目背景、1649年方案受阻、七年后上诉成功、Bernini 于1658年开建，以及1663年 Pamfili 视察工程；本段未载完工日期。17条直接陈述中的16条关系候选留待 S6，本批未新增正式关系或开展 S5。S4 累计登记198组/250条成员映射，待登记4,640组/4,757条。

### S4 place：Bergamo 跨章城市身份组登记（2026-10-16）

`cand-11460, cand-6208, cand-7743, cand-8574`（`sg3-place-bergamo-city`）统一登记至[贝加莫地点卡](../../../04-knowledge/units/places/bergamo.md)。S3 将索引主项 B.csv#325 与第5章 Codazzi 的 patria、第8章 Santa Maria Maggiore 所在城市和第9章 Sagredo 任职地点归为同一城市。S2 共15条直接陈述，全部是关系候选，仍留待 S6；未把城市与人物、教堂、共和国或任职事件合并，也未新建正式关系。S4 累计登记199组/254条成员映射，待登记4,639组/4,753条。

### S4 institution：Papacy 制度性身份组登记（2026-10-16）

`cand-4223`（`sg3-institution-cand-4223`）登记至[教宗职位制度机构卡](../../../04-knowledge/units/institutions/papacy.md)。按 S3 裁定登记为 institution，指书中作为制度性职位与权力秩序讨论的 papacy；与 Urban VIII 人物及 Roman Court 分开。第2章 p.33 的两处原文分别谈其整体地位所受威胁及社会变化对其影响。17条直接陈述中15条关系候选留待 S6；本批未作外部核验、未将罗马教廷或具体教宗并入，也未开展 S5。S4 累计登记200组/255条成员映射，待登记4,638组/4,752条。

### S3 跨章复用纠偏：Barberini palace 复用既有建筑地点（2026-10-16）

cand-0240（B.csv#87，主项）与 cand-0241（B.csv#88，theatre 子目）原裁为同一新 place 组。第2章 p.57 明称 theatre 是 Barberini palace 的一项特征；独立识别的 theatre 候选 cand-4782 仍是未定身份的内部空间，不并入建筑卡。既有 KU units/places/palazzo-barberini 的类型为 place/building，卡名 Palazzo Barberini；故两项均从 new 更正为 same 并映射至该卡。原决定和组号保留在各 alignment resolution_note。20条直接 S2 陈述中14条为关系候选，仍留待 S6；本批未修改卡片、manifest 或 accepted。S3 现为 same=1,753（1,025个既有 KU）、new=5,005（4,837组）、conflict=7、excluded=98、undecided=5,541。S4 已登记200组/255条映射，待登记4,637组/4,750条。

### S3 跨章身份复用纠偏：Biblioteca Correr 对应既有 Correr Library（2026-10-16）

`cand-8262` 原裁为新 institution 组 `sg3-institution-cand-8262`；现映射至既有[科雷尔图书馆机构卡](../../../04-knowledge/units/institutions/correr-library.md)。第9章关于 Sagredo 资料及 Longhi inventory 的注释、第16章 Cicogna 手稿定位、第17章 Manfrin 目录与书信注释，均以 Biblioteca Correr 指称该图书馆。既有卡片以 Correr Library 为英文名称，来源包括本书第一版序言及馆方 Library 页面。映射不指向父机构 Museo Correr（units/institutions/museo-correr）；各被引手稿、目录和书信仍按 archive 对象分别处理。15条直接 S2 陈述全部为关系候选，留待 S6。S3 现为 same=1,754（1,025个既有 KU）、new=5,004（4,836组）、conflict=7、excluded=98、undecided=5,541；S4 已登记200组/255条映射，待登记4,636组/4,749条。原 new 理由保留于 alignment。

### S3 跨章身份复用纠偏：Churches 索引下的 S. Andrea al Quirinale（2026-10-16）

`cand-0694`（C.csv#218，sub-entry `S. Andrea al Quirinale`）原裁为新 place 组 `sg3-place-cand-0694`；现改为 same 并映射至既有[奎里纳尔圣安德烈堂地点卡](../../../04-knowledge/units/places/s-andrea-al-quirinale.md)。第3章 pp.67–68、85–88 将该名称用于同一教堂；教堂建筑、内部空间 KU `units/places/interior-sant-andrea-quirinale` 和重建工程 event KU `units/events/s-andrea-al-quirinale-rebuilding-project` 各自保持独立。20条直接 S2 陈述中13条为关系候选，仍留待 S6。S3 现为 same=1,755（1,025个既有 KU）、new=5,003（4,835组）、conflict=7、excluded=98、undecided=5,541；S4 已登记200组/255条映射，待登记4,635组/4,748条。原决定和理由保留在 alignment。

### S4 event：万神殿圣约瑟节年度展览身份组登记（2026-10-16）

`cand-6031`（`sg3-event-cand-6031`）映射至[年度展览事件卡](../../../04-knowledge/units/events/annual-st-josephs-day-exhibition-pantheon.md)。身份粒度为每年3月19日的重复展览系列；A.csv#132 的泛称术语候选 `cand-0131` 仍为 `undecided`，只提供索引定位，未并入事件。组织者 `cand-0821` 与地点 `cand-4236` 是各自独立的 S3 new 组，尚待 S4；书中1680年具体场次候选 `cand-6047` 仍待身份裁决。第5章 pp.126–127 记载节日日期、组织者、遴选与陈列、1650年示例和1680年扣押命令；所引段落称系列可能始于17世纪初、1764年前某时结束，扫描印刷页确认 OCR 的“17Ó4”读作1764，首末届精确日期未定。19条直接 S2 陈述中12条关系候选保留至 S6，未登记正式关系或开展 S5。S4 累计登记201组/256条成员映射，待登记4,634组/4,747条。

### S4 work：圣彼得大殿华盖跨章身份组登记（2026-10-16）

`cand-4234`（`workgrp-f64cef5b787fe5`）映射至[圣彼得大殿华盖作品卡](../../../04-knowledge/units/works/baldacchino-st-peters-basilica.md)。同一候选的书内提及横跨第2章、 第4章及第20章后记，S3 判为一个 work 身份组；地点圣彼得大殿、临时前置结构及 Pantheon 地点不并入本作品。第2章 p.34 称 Bernini 于1624年7月开始，九年后完成而未给公历完工年；p.35记方案变更及 Pantheon 青铜移用。已核 p.35 扫描印刷页（CHP-2 PDF物理页16）：费用词读作 scudi；book-statements 的 S2 qualifier 已记录 OCR soldi 与印刷 scudi 的校正，本轮不改 S2 表。第20章后记 p.397 将 Haskell 对 Bernini 及 Barberini patrons 的直接归属表述限定为需要进一步限定；所引研究未独立查阅，卡片保留该状态。15条直接 S2 陈述中的14条关系候选留待 S6；未新增正式关系、外部身份记录或 S5 补足。S4 累计登记202组/257条映射，待登记4,633组/4,746条。

### S2 OCR 校正与 S4 work：Pozzo 圣依纳爵堂拱顶壁画（2026-10-16）

`cand-5074`（`workgrp-1c890e82018f20`）登记至[圣依纳爵堂拱顶壁画作品卡](../../../04-knowledge/units/works/pozzo-fresco-vault-s-ignazio.md)。组内身份为实际拱顶壁画：图版15模型 `cand-4002` 已 same 至既有模型稿卡；较早的 dome painting 候选 `cand-5368` 保持独立 new 组并待 S4；教堂候选 `cand-3967` same 至既有地点卡。第3章 p.90 记录1688年开工、此前考虑放弃、及 Haskell 转引 Pozzo 对图像的解释；未推定完工年。14条直接陈述均为 S2 关系候选，留待 S6。扫描 CHP-3.pdf 物理页32（印刷 p.90）读作 ray of light；源 OCR 误作 ray of fight。为保持原始 OCR 摘录可追溯，两个相关 S2 statement 保留 original_quote 原文并补入 `ocr_corrections` 与 scan qualification；其他 S2 判断不变。本轮未新增正式关系或开展 S5。S4 累计登记203组/258条映射，待登记4,632组/4,745条。

### S4 work：Urban VIII 墓葬纪念碑跨章登记（2026-10-16）

`cand-4512`（`workgrp-aa9759b87aa39d`）映射至[乌尔班八世墓葬纪念碑作品卡](../../../04-knowledge/units/works/tomb-of-urban-viii-st-peters.md)。第2章 p.41 记1627年下令、Bernini受托、原定生前完成及显著安置；p.42记录早期青铜教宗像、停工八年、1639年复工、1644年未能赶上生前完工及 Justice 于1647年完成。p.59 后文称 Bernini 最终完成整座墓葬，但没有具体日期。Justice 的1647年仅为部件完成日期，不推作全墓完工年；原计划亦不写成 Urban 生前已经完成。14条直接 S2 陈述中12条关系候选留待 S6；未新增正式关系或 S5 补足。S4 累计登记204组/259条映射，待登记4,631组/4,744条。

### S4 term：宗教修会的艺术赞助登记（2026-10-16）

`cand-2114` 与 `cand-2115`（`sg3-term-religiousorderspatronageby`）映射至[宗教修会的艺术赞助术语卡](../../../04-knowledge/units/terms/patronage-by-religious-orders.md)。身份依据为第3章印刷页63–65中直接讨论耶稣会及其他宗教修会赞助的三段原文；既有“艺术赞助”卡为一般上位术语，不是同一粒度的对象。索引项 `cand-2113`（Q-R.csv#40）及 `cand-2116`（Q-R.csv#43）仅有索引定位、缺正文身份锚点，继续保留 undecided，不随本次登记映射。13条直接 S2 陈述中12条关系候选仍待 S6；本次未生成正式关系或 S5 补足。S4 累计登记205组/261条映射，待登记4,630组/4,742条。

### S4 event：S. Giovanni Decollato 年度展览系列登记（2026-10-16）

`cand-6039`（`sg3-event-s-giovanni-decollato-series`）映射至[罗马圣若望斩首堂年度展览系列事件卡](../../../04-knowledge/units/events/annual-exhibition-s-giovanni-decollato.md)。第5章 pp.127–128 记载年度展览于8月29日在教堂回廊举行；1620年已有常规活动记录，约1600年前后可见较早迹象，但首届年份不明。卡片保留作者对宗教装饰目的及晚期商业化的判断范围，并区分 Salvator Rosa 的公众展示用途。1662、1668、1675、1736年四个具体场次候选 `cand-11766`–`cand-11769` 各有独立 new 组，尚未登记，不映射为系列本体；同名博洛尼亚善会机构与本罗马展览事件亦分开。12条直接 S2 陈述中8条关系候选仍待 S6；本次未生成正式关系或 S5 补足。S4 累计登记206组/262条映射，待登记4,629组/4,741条。

### S3 institution：Congregazione dei Virtuosi 复用既有万神殿 Virtuosi 学院（2026-10-16）

本条更正取代前述 Pantheon 圣约瑟节展览登记段将 `cand-0821` 记为独立 new/待 S4 的状态；展览地点候选 `cand-4236` 已另行登记为 place。

`cand-0821`（C.csv#351）原裁为 new，`cand-2780`（UVWXYZ.csv#116）原为 undecided；现均映射至既有[万神殿 Virtuosi 学院机构卡](../../../04-knowledge/units/institutions/accademia-dei-virtuosi-al-pantheon.md)，与已 same 的 `cand-3233` 汇合到 `units/institutions/accademia-dei-virtuosi-al-pantheon`。第5章 p.126 将 Congregazione dei Virtuosi 描述为主要由艺术家组成、1543年成立的 confraternity；同页记 Velasquez 为该团体成员。既有机构卡的官方历史页（[机构历史](<https://www.accademiavirtuosi.it/storia>)，2026-10-16访问）说明该 Pantheon 团体1542年创立、原称 Compagnia、1543年开始社会活动，并在后续沿革中称为 Congregazione、最终升格为学院。地点、团体称谓、历史职能及成员证据表明是同一连续机构，不另建新 institution。官方叙述的1542年创立与 Haskell 的1543年成立表述并列保留；官方页面将1543年说明为社会活动开始，日期表述差异属于后续内容核读事项，不拆分身份。`cand-2780` 是同页反序索引项，无独立正文锚点；其名称和页码与正文锚定的 `cand-0821` 完全对应，故复用同一 KU。普通词义的 `cand-5499` 与第3章未具名群体 `cand-11605` 均保持边界，不并入本机构。11条直接 S2 陈述中的7条关系候选仍留待 S6；本次不修改原书陈述、不新增关系或 KU。S3 现为 same=1,757（1,025个既有 KU）、new=5,002（4,834组）、conflict=7、excluded=98、undecided=5,540；S4 已登记206组/262条映射，待登记4,628组/4,740条。原决定及理由保存在 alignment。

### S4 place：罗马 Pantheon 建筑跨章身份组登记（2026-10-16）

`cand-4236`（`sg3-place-cand-4236`）映射至[罗马万神殿地点卡](../../../04-knowledge/units/places/pantheon-rome.md)。同一建筑在第2章 pp.34–35、第5章 p.126、第10章 p.321及第14章 p.348 均有提及；第14章另有一条比较性陈述，仅作提及证据，不改写其评价主体。建筑本体与圣约瑟节年度展览事件、华盖作品及展览门廊陈列空间分开；门廊空间候选 `cand-11743` 仍为 undecided，本次不据其待决状态扩大建筑卡范围。四条直接 S2 端点陈述均为关系候选，保留至 S6；未将材料拆取、场地和评价陈述转成正式边，也未开展 S5。S4 累计登记207组/263条映射，待登记4,627组/4,739条。

### S4 event：S. Giovanni Decollato 年度展览四个具体场次登记（2026-10-16）

将 `cand-11766`（1662）、`cand-11767`（1668）、`cand-11768`（1675圣年）与 `cand-11769`（1736）分别映射至各自事件卡；四者均为已登记年度系列 `cand-6039` 的具体场次，不并入系列本体。1662、1668年份来自原文明确年份及“六年后”的时间顺序；系列日期为每年8月29日，但不为各场次另补精确日。1736年212幅画作与目录为实际记载，教宗出价仅为原文所说的期待。四卡均保留组织、陈列和届次关系为 S2 候选，不写入正式 `relations.csv`；四组共19条直接 S2 陈述，其中17条为关系候选，留待 S6；未开展 S5。S4 累计登记211组/267条映射，待登记4,623组/4,735条。

### S3 跨章人物裁决：Ariosto 与《Orlando Furioso》索引子目（2026-10-16）

`cand-0116`（A.csv#117）在第4章 p.103、第9章 p.258、第13章 p.339、第20章后记 p.405 均指 Ariosto。正文分别将其置于诗人、文学题材来源及经典作品出版语境；Treccani《在线百科》规范项为 Ariosto, Ludovico，明确其为诗人及《Orlando furioso》作者；[Treccani 人物条目](https://www.treccani.it/enciclopedia/ludovico-ariosto/)（2026-10-16访问）。manifest 未有同名 person KU，故归为单一新人物组 `sg3-person-ludovico-ariosto`，待 S4 登记。身份组只合并人物提及，不把所指作品并入人物卡。

`cand-0117`（A.csv#118，sub-entry `Orlando Furioso`，索引页码103、336）原标为 person，现按子目对象更正为 work。p.103 所指文学文本与 `cand-5719` 相同，而该文学文本不属于当前艺术作品 work KU 范围；p.336 指向 Gerbault 发起但未实现的拟议版本，archive 候选 `cand-9997` 已因无实际出版物或存世档案件而排除。该子目不是第二个人，也不与新建的 Ariosto 人物组或未实现出版计划合并，故裁为 excluded。原 undecided 理由保存在 alignment 行的 `prior_resolution_note`。本次未创建 KU、未登记关系或开展 S5。

### S3 跨类型裁决：Lodoli《Apologhi》文本与1787年出版事件（2026-10-16）

`cand-1413`（L.csv#70，archive）与 `cand-1651`（M.csv#191，event）分别改为 new。第15章 p.367 正文称 Andrea Memmo 于1787年回威尼斯就任 Procuratore di San Marco，并为纪念就职出版 Carlo de' Conti Lodoli 的五十八则 `Apologhi`；注2给出原文全题名及 Bassano [Remondini]、1787年出版项。故 archive 候选指这部特定印本，event 候选指出版发生，两者不合并；现有 manifest 无匹配 archive 或 event KU。书本身未独立查阅，当前只裁决书目身份，不作版本全文验证。新组分别为 `sg3-archive-lodoli-apologhi-1787` 与 `sg3-event-publication-lodoli-apologhi-1787`，进入 S4 各登记一 KU。原 undecided 理由保留在对齐行。未登记正式关系或开展 S5。

### S4 person/archive/event：Ariosto 与 Lodoli《Apologhi》出版组登记（2026-10-16）

`cand-0116` 登记至[卢多维科·阿里奥斯托人物卡](../../../04-knowledge/units/persons/ludovico-ariosto.md)，依据第4、9、13、20章的同一人物语境及 Treccani 规范姓名；不把文学作品、版本并入人物。`cand-1413` 登记至[《Apologhi》1787年版档案卡](../../../04-knowledge/units/archives/lodoli-apologhi-1787.md)；身份和印次依据 p.367 注2及正文，所引印本未独立查阅。`cand-1651` 登记至[1787年出版事件卡](../../../04-knowledge/units/events/memmo-apologhi-publication-1787.md)；出版事件与 archive 印本分开，未把出版地 Bassano 当作就职仪式地点。脚注 OCR “Procurala”已依 S2 扫描页校读为印本 “Procuratia”。三组直接 S2 断言端点数分别为 0、5、2；archive 与 event 两组共 7 条关系候选，均留待 S6。未登记正式关系或开展 S5。S4 累计登记214组/270条候选映射，待登记4,623组/4,735条。

### S3 候选决定记录收口核对（2026-10-16）

按候选 ID 核对 `entity-candidates.csv` 与 `alignment.csv`：12,404 个候选各有且仅有一条当前决定行，且均填写 `resolution_note` 与 `process_ref`。`same` 均指向 `ku-manifest.csv` 中既有 KU；`new` 身份组号均可解析，已登记组成员一致映射至同一 KU，未登记组成员整体待登记；7 条 `conflict` 保留双方来源与未决去向；`excluded` 与 `undecided` 均有逐项理由。未发现候选缺行、重复决定、断开的过程引用或组内部分映射。

核对计数：same 1,757（1,025 个既有 KU）；new 5,005（4,837 组）；conflict 7；excluded 99；undecided 5,536。S4 已登记214组、270条候选映射；待登记4,623组、4,735条候选映射。该核对确认的是 S3 决定账本按当前收口标准完整、可追溯，不表示5,536项待证对象已解决，也不替代独立语义验收。

机械检查：`audit_tables.py --summary` 无错误；`build_cards.py --check` 预检通过（1,233张卡、2,626张表、10,220行、2,436条派生关系行，预计影响21张卡），该检查未写卡片文件。仍需处理的事项包括 S4 待登记组、两条历史 enrichment 来源引用待修复，以及全书 S2 独立语义验收。


### S4 person：Pierre II Legros 跨章人物组登记（2026-10-16）

`cand-1379`（L.csv#36）按 `new-person:legros-pierre-304dcc72bb` 登记为一张人物 KU。第3章 p.92 称 Pierre Legros 为法国人，记其赢得圣依纳爵堂祭坛雕像竞赛、法国学院学生身份及法国国王供养人身份；p.93 以 Legros／Pierre Legros 记其在 S. Ignazio 的工作；第20章后记 p.400 再提到该堂的 Legros。Treccani 的 Pierre I 条目区分其子 Pierre II（1666–1719），并记其在罗马为耶稣会工作；与书内语境吻合。该外部来源仅用于父子身份辨析，未据此补入完整生卒履历。新增 alignment 外部身份记录用于 Treccani 匹配；原 S3 `new` 决定及身份组保持不变。11条直接 S2 陈述全部为关系候选，仍留待 S6；本次不登记作品端点、正式关系或 S5 补足。S4 累计登记215组/271条候选映射，待登记4,622组/4,734条。

### S3 补裁：Carlevarijs 三件入城／节庆作品（2026-10-16）

复核 C.csv#80–82 与第10章 p.276 正文、p.277 注5后，明确分开艺术家、人物和三件作品。`cand-0556`（Entry of the Count of Colloredo，1726）、`cand-0557`（Lord Manchester’s Entry into Venice，1707）及 `cand-8845`（Regatta in honour of Frederick IV of Denmark，1709）均由原先待证改裁为独立 new work 组；不与 Carlevarijs 人物 `cand-0554`／`cand-0558` 合并。`cand-0557` 原 suggested_type=person 是索引父项误读，已改为 work；复用既有精确提及 `m-chp10-p277n5-manchester-entry`，并新增 S2 关系候选陈述`st-chp10-notes-p277n5-manchester-entry`；该陈述把 p.277 注5作品名与 p.276 委托正文相连，保留 Lord Manchester 身份待证。Colloredo 的名与委托关系不外推；Fredericksborg 的现今地点不核定。原 alignment 决定及注释在写入前保存在本脚本 dry-run 审查对象及此前 S3 记录；本次逐行改为清晰的当前理由并保留书内来源锚点。本批前 S3 `undecided` 5,536，`new` 5,005；本批后 `undecided` 5,532，`new` 5,009，new 身份组4,840。相关旧注释：- `cand-0556`: prior decision=`undecided`; prior resolution_note=`source_ref=entity-candidates.csv#cand-0556;index_entry=C.csv#80;index_source=C.csv;index_pages=277n;mentions=m-chp10-p277n5-colloredo-entry;segments=chp-10:10_CHP-10_intro:l491-634; 候选来源不是可核的 S2 body-mention，且无现成对齐；保留待证，不凭索引/类型字段推新。` - `cand-0557`: prior decision=`undecided`; prior resolution_note=`source_ref=candidate=cand-0557;index_entry=C.csv#81;index_pages=277n;s2_mentions=none; Undecided: index-seeded candidate has no mapped S2 mention/body source_ref; index locator/page range is only a locator, so original-text identity anchor is missing.` - `cand-8839`: prior decision=`undecided`; prior resolution_note=`source_ref=entity-candidates.csv#cand-8839;candidate_source_ref=chp-10:10_CHP-10_intro:l3-13#L12;mentions=m-chp10-p276-entry_work,m-chp10-p276n23-entry-picture,m-chp10-p277n5-manchester-entry;segments=chp-10:10_CHP-10_intro:l3-13,chp-10:10_CHP-10_intro:l491-634; S2 明示作品题名、物件版本、实体身份或归属对象仍未识别；保留 undecided，避免把描述性提及或某一版本猜成新 KU。` - `cand-8845`: prior decision=`undecided`; prior resolution_note=`source_ref=entity-candidates.csv#cand-8845;candidate_source_ref=chp-10:10_CHP-10_intro:l15-24#L18;mentions=m-chp10-p277-regatta,m-chp10-p277n14-regatta-location-picture,m-chp10-p277n5-frederick-regatta;segments=chp-10:10_CHP-10_intro:l15-24,chp-10:10_CHP-10_intro:l491-634; S2 明示作品题名、物件版本、实体身份或归属对象仍未识别；保留 undecided，避免把描述性提及或某一版本猜成新 KU。`


### S4 person：Carlevarijs 跨章端点批次（2026-10-16）

- `cand-0419` → `new-person:bouchard-jacques-jean-19fda1229d` → `units/persons/jean-jacques-bouchard`; 11 direct S2 statements, 11 relation candidates pending S6.
- `cand-0554,cand-0558` → `new-person:carlevarijs-luca-3987dbd340` → `units/persons/luca-carlevarijs`; 11 direct S2 statements, 11 relation candidates pending S6.
- `cand-0800` → `new-person:baptiste-colbert-jean-ffec9f31bd` → `units/persons/jean-baptiste-colbert`; 10 direct S2 statements, 10 relation candidates pending S6.
- `cand-1078` → `new-person:denmark-frederick-iv-of-65aed0cc97` → `units/persons/frederick-iv-of-denmark`; 2 direct S2 statements, 2 relation candidates pending S6.

本批按类型登记 人物，每个身份组一张 KU，同组候选映射到同一 `ku_id`。卡片按原书书内证据提供双语名称、等值描述和逐条来源引文。本批仅登记对象身份及其来源记载，不把 S2 关系候选写成正式关系；待 S6 按端点、方向、语境和证据逐条审查。未开展 S5 补足或外部事实核验。

S4 当前已登记219组/276条成员映射，尚待登记4,621组/4,733条。


### S4 archive：Carlevarijs 跨章端点批次（2026-10-16）

- `cand-0555` → `archive-group-bf88b7762ce2` → `units/archives/carlevarijs-le-fabriche-1703`; 2 direct S2 statements, 2 relation candidates pending S6.

本批按类型登记 文献，每个身份组一张 KU，同组候选映射到同一 `ku_id`。卡片按原书书内证据提供双语名称、等值描述和逐条来源引文。本批仅登记对象身份及其来源记载，不把 S2 关系候选写成正式关系；待 S6 按端点、方向、语境和证据逐条审查。未开展 S5 补足或外部事实核验。

S4 当前已登记220组/277条成员映射，尚待登记4,620组/4,732条。


### S4 work：Carlevarijs 跨章端点批次（2026-10-16）

- `cand-0556` → `sg3-work-carlevarijs-colloredo-entry-1726` → `units/works/carlevarijs-colloredo-entry-1726`; 2 direct S2 statements, 2 relation candidates pending S6.
- `cand-0557,cand-8839` → `sg3-work-carlevarijs-manchester-entry-1707` → `units/works/carlevarijs-manchester-entry-1707`; 2 direct S2 statements, 2 relation candidates pending S6.
- `cand-8845` → `sg3-work-carlevarijs-regatta-frederick-iv-1709` → `units/works/carlevarijs-regatta-frederick-iv-1709`; 2 direct S2 statements, 2 relation candidates pending S6.

本批按类型登记 作品，每个身份组一张 KU，同组候选映射到同一 `ku_id`。卡片按原书书内证据提供双语名称、等值描述和逐条来源引文。本批仅登记对象身份及其来源记载，不把 S2 关系候选写成正式关系；待 S6 按端点、方向、语境和证据逐条审查。未开展 S5 补足或外部事实核验。

S4 当前已登记223组/281条成员映射，尚待登记4,617组/4,728条。


### S4 place：Carlevarijs 跨章端点批次（2026-10-16）

- `cand-0947` → `sg3-place-cand-0947` → `units/places/dresden`; 7 direct S2 statements, 7 relation candidates pending S6.

本批按类型登记 地点，每个身份组一张 KU，同组候选映射到同一 `ku_id`。卡片按原书书内证据提供双语名称、等值描述和逐条来源引文。本批仅登记对象身份及其来源记载，不把 S2 关系候选写成正式关系；待 S6 按端点、方向、语境和证据逐条审查。未开展 S5 补足或外部事实核验。

S4 当前已登记224组/282条成员映射，尚待登记4,616组/4,727条。


### S4 term：Carlevarijs 跨章端点批次（2026-10-16）

- `cand-6267` → `sg3-term-cand-6267` → `units/terms/decline-of-roman-patronage`; 14 direct S2 statements, 12 relation candidates pending S6.

本批按类型登记 术语，每个身份组一张 KU，同组候选映射到同一 `ku_id`。卡片按原书书内证据提供双语名称、等值描述和逐条来源引文。本批仅登记对象身份及其来源记载，不把 S2 关系候选写成正式关系；待 S6 按端点、方向、语境和证据逐条审查。未开展 S5 补足或外部事实核验。

S4 当前已登记225组/283条成员映射，尚待登记4,615组/4,726条。


### S4 place：Carlevarijs 跨章端点批次（2026-10-16）

- `cand-0086` → `sg3-place-cand-0086` → `units/places/alticchiero-querini-villa-estate`; 21 direct S2 statements, 11 relation candidates pending S6.

本批按类型登记 地点，每个身份组一张 KU，同组候选映射到同一 `ku_id`。卡片按原书书内证据提供双语名称、等值描述和逐条来源引文。本批仅登记对象身份及其来源记载，不把 S2 关系候选写成正式关系；待 S6 按端点、方向、语境和证据逐条审查。未开展 S5 补足或外部事实核验。

S4 当前已登记226组/284条成员映射，尚待登记4,614组/4,725条。


### S4 institution：Carlevarijs 跨章端点批次（2026-10-16）

- `cand-0005` → `sg3-institution-accademiadipitturaescultura` → `units/institutions/academy-of-painting-and-sculpture-venice`; 17 direct S2 statements, 11 relation candidates pending S6.

本批按类型登记 机构，每个身份组一张 KU，同组候选映射到同一 `ku_id`。卡片按原书书内证据提供双语名称、等值描述和逐条来源引文。本批仅登记对象身份及其来源记载，不把 S2 关系候选写成正式关系；待 S6 按端点、方向、语境和证据逐条审查。未开展 S5 补足或外部事实核验。

S4 当前已登记227组/285条成员映射，尚待登记4,613组/4,724条。


### S4 work：跨章直接端点身份组登记（2026-10-16）

- `cand-5789` → `workgrp-99b6f34360e16f` → `units/works/poussin-seven-sacraments-series`；14 条直接 S2 断言，其中 11 条关系候选留待 S6。`cand-5789` 的 group=workgrp-99b6f34360e16f 仅含这一系列候选。第4章 p.106 将其称为 Poussin 为 Cassiano 创作的一组《七件圣事》并称开始绘制于17世纪30年代后半；pp.107、109–110论及系列形式、作者对 Cassiano 委托缘由的解释及 Poussin 对作品的态度；第20章后记 p.401 的1664年报告仅支持“曾考虑赠与”，不证明实际转移。manifest 中无同题 work KU。

本批新增1张作品 KU，每个 S3 new 身份组一张；卡片保存双语描述及精确书内引文。不将关系候选升级为正式关系，也未开展 S5 外部补足。S4 当前已登记228组/286条成员映射，尚待登记4,612组/4,723条。


### S4 event：跨章直接端点身份组登记（2026-10-16）

- `cand-9792` → `sg3-event-cand-9792` → `units/events/giorgio-pisani-1780-election-and-entry`；13 条直接 S2 断言，其中 11 条关系候选留待 S6。`cand-9792` 独立新组。第10章 p.326 记 Pisani 于1780年当选，p.326–327 讨论新任 Procuratore 入城路线与图像，p.327 注3仅以“有充分理由相信”判断图像／版画曾于1780年展出，并指出若干图像早于其当选，不应概括成专为此次入城委托。当选与入城保留原书叙述关联但不声称同日；游行当晚宫邸庆祝会由独立候选 `cand-9812` 表示。
- `cand-9812` → `sg3-event-cand-9812` → `units/events/giorgio-pisani-1780-palace-entry-celebration`；6 条直接 S2 断言，其中 4 条关系候选留待 S6。`cand-9812` 保持为区别于 `cand-9792` 当选／公开入城仪式的独立事件组。第10章 p.327 称大型庆祝会于游行当晚在宫邸举行，记有来宾、侦察者、主接待室画作及菜单诗句；随后记四天后 Inquisitors 行动及 Pisani 被捕。本卡保留来源叙述，不从时间先后推因果。

本批新增2张事件 KU，每个 S3 new 身份组一张；卡片保存双语描述及精确书内引文。不将关系候选升级为正式关系，也未开展 S5 外部补足。S4 当前已登记230组/288条成员映射，尚待登记4,610组/4,721条。


### S4 place：跨章直接端点身份组登记（2026-10-16）

- `cand-5317` → `sg3-place-cand-5317` → `units/places/france`；15 条直接 S2 断言，其中 11 条关系候选留待 S6。cand-5317 为跨章地点候选，包含48条书内提及及15条直接断言端点；其 S3 new 组为 sg3-place-cand-5317。第3章 p.86 明确将 Bernini 访问耶稣会教堂置于 France；第10章 p.284 与第20章后记 p.402 又分别以法国作为艺术传播和政治文化语境。当前 manifest 无代表法国国家地点的 KU；法国圣路易堂是具体建筑，不是同一对象。

本批新增1张事件 KU，每个 S3 new 身份组一张；卡片保存双语描述及精确书内引文。不将关系候选升级为正式关系，也未开展 S5 外部补足。S4 当前已登记231组/289条成员映射，尚待登记4,609组/4,720条。


### S3 地点身份复核：复用 Gesù 与 Barberini Chapel，并合并 Gesù 圣方济各礼拜堂候选（2026-10-16）

`cand-4252` 与既有 `units/places/barberini-chapel-sant-andrea-valle` 指同一谷地圣安德烈堂内部的 Barberini Chapel：第2章记 Maffeo 选择该教堂并为自己建造家族礼拜堂，图版目录以 ‘Barberini Chapel in S. Andrea della Valle, Rome’ 明名。现从 new 改为 same，保留旧组号及理由，不另建地点卡。`cand-5200` 指全书既有 `units/places/gesu-rome` 教堂建筑；第3章 p.82 的建筑外观比较与既有 KU 身份一致，故从 new 改为 same。该决定不把教堂与内部礼拜堂、拱顶绘画或修会合并。两条复用均经现有 manifest、accepted.yml 与卡片核对。

另将 `cand-5237`（Gaulli 合约中的 Chapel of St Francis Xavier）与 `cand-5300`（同教堂右横翼、经历连续更名／改奉的礼拜堂）并入 `sg3-place-cand-5300`。第3章 p.80 列 Gaulli 合约范围中的 St Francis Xavier 礼拜堂；p.84 将右横翼礼拜堂的历次奉献对象及1623年改奉圣方济各·沙勿略记为同一空间。故这两行保持 new、共用一个新组；原独立组号在 `cand-5237` 注释中保留。`cand-5236` 的 St Ignatius 礼拜堂继续独立，且不与圣依纳爵堂 S. Ignazio 或教堂中的祭坛和绘画合并。

更正后 S3：same=1,759、new=5,007（4,837组）、conflict=7、excluded=99、undecided=5,532。S4 已登记231组/289条映射，尚待登记4,606组/4,718条。未改既有 KU、manifest 或正式关系。

### S4 place：跨章直接端点身份组登记（2026-10-16）

- `cand-5236` → `sg3-place-cand-5236` → `units/places/gesu-chapel-st-ignatius`；11 条直接 S2 断言，其中 11 条关系候选留待 S6。cand-5236 保持为耶稣堂内圣依纳爵礼拜堂的独立 place 组。第3章 p.80 将其与圣方济各·沙勿略礼拜堂并列于 Gaulli 横翼拱顶工程范围，p.81 后文提到左横翼圣依纳爵祭坛上方的绘画。它与 Gesù 教堂本体、祭坛及绘画分开，也与 S. Ignazio 教堂中的同名空间分开。

本批新增1张事件 KU，每个 S3 new 身份组一张；卡片保存双语描述及精确书内引文。不将关系候选升级为正式关系，也未开展 S5 外部补足。S4 当前已登记232组/290条成员映射，尚待登记4,605组/4,717条。


### S4 place：跨章直接端点身份组登记（2026-10-16）

- `cand-5237,cand-5300` → `sg3-place-cand-5300` → `units/places/gesu-right-transept-chapel-st-francis-xavier`；12 条直接 S2 断言，其中 12 条关系候选留待 S6。cand-5237 与 cand-5300 现共组 sg3-place-cand-5300。第3章 p.80 的 Gaulli 合约称横翼拱顶位于 St Ignatius 与 St Francis Xavier 礼拜堂之上；p.84 记右横翼礼拜堂从救世主、复活到1623年改奉圣方济各·沙勿略的连续沿革，表明两候选是同一地点在不同段落中的名称锚点。Baglione 祭坛画与 Van Dyck 圣人像保持为作品端点；S. Andrea al Quirinale 的同名礼拜堂不并入。

本批新增1张事件 KU，每个 S3 new 身份组一张；卡片保存双语描述及精确书内引文。不将关系候选升级为正式关系，也未开展 S5 外部补足。S4 当前已登记233组/292条成员映射，尚待登记4,604组/4,715条。


### S4 work：跨章直接端点身份组登记（2026-10-16）

- `cand-6917` → `workgrp-adab2fea7b8577` → `units/works/bernini-equestrian-statue-louis-xiv-marcus-curtius`；11 条直接 S2 断言，其中 11 条关系候选留待 S6。cand-6917 为一个 new work 组，当前无同一骑马像的既有 work KU。现有 units/works/bernini-louis-xiv 是图版27b所记胸像，不与该骑马像合并。第7章 pp.188–189 记录 Louis XIV 委托、相对开工时间、1684年抵达巴黎、凡尔赛安置及 Girardon 改造；p.191 记 Del Carpio 的求购传言及未获接受。作品变化状态严格按 Haskell 叙述，不补外部实物信息。

本批新增1张作品 KU，每个 S3 new 身份组一张；卡片保存双语描述及精确书内引文。不将关系候选升级为正式关系，也未开展 S5 外部补足。S4 当前已登记234组/293条成员映射，尚待登记4,603组/4,714条。


### S4 work：跨章直接端点身份组登记（2026-10-16）

- `cand-9007` → `workgrp-08f1a6d27a1b75` → `units/works/mcswiny-allegorical-tomb-paintings-british-worthies`；29 条直接 S2 断言，其中 10 条关系候选留待 S6。cand-9007 为一个 new work 组，原书第10章 pp.287–291 连续描述 McSwiny 代表 Lord March 提出的寓意墓葬绘画系列、画面规则、1722年前开工情况、作者对项目成效的评价及后续收藏与版画出版。作品对象为绘画系列，不是实际墓葬。Haskell 注2明确说明 Richmond 购藏的具体清单存在混乱，故保留“至少十幅”及收藏不确定性。第20章后记候选 cand-11080 只指“为 Owen McSwiny 绘制的纪念画”及后续目录，尚无明确措辞证明其与本系列同一；cand-11080 仍保持 undecided，不合并到本 work 组。

本批新增1张作品 KU，每个 S3 new 身份组一张；卡片保存双语描述及精确书内引文。不将关系候选升级为正式关系，也未开展 S5 外部补足。S4 当前已登记235组/294条成员映射，尚待登记4,602组/4,713条。


### S4 work：跨章直接端点身份组登记（2026-10-16）

- `cand-5232` → `workgrp-0323f2bb274493` → `units/works/gaulli-gesu-dome-and-vault-decoration-commission`；13 条直接 S2 断言，其中 10 条关系候选留待 S6。cand-5232 为独立 new work 组，表示合同定义的绘饰工程，不是合同文书本身；合同档案 cand-5227 另属 archive，尚待 S4。第3章 p.80 明确将绘饰范围界定为1672年8月合同下的整体工程：穹顶及其灯笼、帆拱，主拱顶及窗龛，横翼拱顶；穹顶工期为两年，其余绘画、镀金与灰泥工程为八年，后殿拱顶排除并留给 Borgognone。既有 `units/works/gaulli-gesu-vaults` 记录第1章所称中殿及横翼拱顶与八年工期；其范围未包含本候选另外列出的穹顶及独立两年期限，因此 S3 保留为大范围装饰工程与范围较窄的拱顶绘画工程两个对象，不并为一张单作卡。`cand-11837` 因缺少 S2 mention-level 锚点仍为 undecided，不并入。当前不新增正式关系，10条关系候选留待 S6核对整体工程与其组成作品的端点关系。

本批新增1张作品 KU，每个 S3 new 身份组一张；卡片保存双语描述及精确书内引文。不将关系候选升级为正式关系，也未开展 S5 外部补足。S4 当前已登记236组/295条成员映射，尚待登记4,601组/4,712条。


### S3 作品复用：Juan de Pareja 肖像跨章组并入既有 KU（2026-10-16）

`cand-2714`（第8章索引中的 Velasquez 肖像）与 `cand-6034`（第5章1650年 Pantheon 展览中的 Pareja 肖像）原共属 `workgrp-63a60a31a83492`，裁为 new。复核第8章 p.222 注4后改为复用既有 `units/works/velasquez-juan-de-pareja`：该注明确指出库存描述中的画作就是现藏 Metropolitan Museum 的作品；第8章正文使用完整画家和人物名，第5章记 Velasquez 在1650年展出的正是其仆人 Pareja 肖像。现有 KU 的图版34目录与 Met 藏品号进一步锁定该作品。两条 alignment 改为 same，`workgrp-63a60a31a83492` 及原裁理由保留在决定注记中；没有新增 KU 或 manifest 行。

S2 中9条关系候选保持待 S6；本次没有改动 `relations.csv` 或已有关系。卡片补入第5章与第8章的书内引文及展览语境，但不新增正式展出／借展边。

更正后 S3：same=1,761、new=5,005（4,836组）、conflict=7、excluded=99、undecided=5,532。S4 已登记236组/295条映射，待登记4,600组/4,710条。

### S4 work：跨章直接端点身份组登记（2026-10-16）

- `cand-5065` → `workgrp-05ac00daf8fe99` → `units/works/lanfranco-dome-fresco-s-andrea-della-valle`；14 条直接 S2 断言，其中 9 条关系候选留待 S6。cand-5065 为一个 new work 组，现有 manifest 无 Lanfranco 在 S. Andrea della Valle 的穹顶壁画 KU。第3章 p.72 称其于1627年完成、描写灯笼中基督为光源及周围图像，并以 probably 将圣安德鲁·阿韦利诺1624年列福与可能开工时间相连；p.78 的“壁画已成经典”是对 Lanfranco 在该堂作品的复数评价，本卡保留范围，不缩写为只评价穹顶。建筑地点、Domenichino 的相邻装饰和绘画中的人物／群体不并入作品身份。索引子项 cand-1360 无 S2 锚点，仍 undecided；cand-12318 的未具名艺术家群体也不并入作品。14条直接 S2 断言中9条关系候选留待 S6，本次不登记正式关系。

本批新增1张作品 KU，每个 S3 new 身份组一张；卡片保存双语描述及精确书内引文。不将关系候选升级为正式关系，也未开展 S5 外部补足。S4 当前已登记237组/296条成员映射，尚待登记4,599组/4,709条。


### S4 work：跨章直接端点身份组登记（2026-10-16）

- `cand-9251` → `workgrp-40fe5d001d7c1f` → `units/works/smith-palladian-overdoor-series`；11 条直接 S2 断言，其中 8 条关系候选留待 S6。cand-9251 是跨第10章 pp.308–309 与第20章后记 p.407 的 new work 组，group=workgrp-40fe5d001d7c1f。第10章先记 Canaletto 于1744年绘制十三幅门上画，后记 Canaletto 离开后由 Visentini 延续同一系列，并由 Zuccarelli 为建筑画增加装饰风景；第10章另列后续十一幅画的建筑师来源。系列 KU 保存总体委托身份与分阶段贡献，但不把十三幅及十一幅并成一个件数或单作。第20章提及的 Barcham 文章没有独立阅读；文献候选 cand-11099 仍属独立 archive 对象，不把引用当作已核研究证据。相邻索引候选 cand-2785、cand-2883 缺少已裁决的独立作品身份，cand-2453 缺少可连接的 S2 委托事件身份，均保留原 undecided 决定和待证去向。11条直接 S2 断言中8条关系候选留待 S6，本次不登记正式关系。

本批新增1张作品 KU，每个 S3 new 身份组一张；卡片保存双语描述及精确书内引文。不将关系候选升级为正式关系，也未开展 S5 外部补足。S4 当前已登记238组/297条成员映射，尚待登记4,598组/4,708条。


### S4 work：跨章直接端点身份组登记（2026-10-16）

- `cand-6307` → `workgrp-e4dc131e4ac24c` → `units/works/bernini-colonnade-st-peters-square`；9 条直接 S2 断言，其中 8 条关系候选留待 S6。cand-6307 为 workgrp-e4dc131e4ac24c 的单候选 new 组，正文锚点跨第6章 pp.151–153。Haskell 明确称 Bernini 在圣彼得大教堂外建造环抱广场的柱廊；第152页转述 Sagredo 于1661年的半途及三年工期估计，并引 Querini 对三百柱、椭圆布局和建筑政策的批评。卡片保留发言者，未把估计变为实际竣工事实，未把 Querini 的预测写成后果。广场 cand-6308、大教堂 cand-5696、Vatican 与 Leonine City 保持地点端点边界。11条候选关联中8条关系候选留待 S6；cand-11982 与 cand-11987 仍为 undecided，不借关系语境强行裁决。

本批新增1张作品 KU，每个 S3 new 身份组一张；卡片保存双语描述及精确书内引文。不将关系候选升级为正式关系，也未开展 S5 外部补足。S4 当前已登记239组/298条成员映射，尚待登记4,597组/4,707条。


### S4 work：跨章直接端点身份组登记（2026-10-16）

- `cand-5022` → `workgrp-d2f152b9c3608e` → `units/works/fiammeri-s-vitale-martyrdom-frescoes`；9 条直接 S2 断言，其中 8 条关系候选留待 S6。cand-5022 是跨第3章 p.67 与第20章后记 p.399 的 new work 组，group=workgrp-d2f152b9c3608e。第3章说明 Fiammeri 统筹、Aquaviva 直接监督并参与、壁画以酷刑为主要题材且唱诗班场景更直接；后记的“牧歌式”场景与风格来源讨论回指同一组 S. Vitale 壁画。卡片不混入 S. Stefano Rotondo 的 Circignani 壁画，不把第19世纪的 Gaspard Poussin 归属误说成作者确认。Buser 的判断仍是 Haskell 对其研究的转述。9条直接 S2 断言中8条关系候选留待 S6；圣维塔莱唱诗班 cand-5023 保持独立 place KU。

本批新增1张作品 KU，每个 S3 new 身份组一张；卡片保存双语描述及精确书内引文。不将关系候选升级为正式关系，也未开展 S5 外部补足。S4 当前已登记240组/299条成员映射，尚待登记4,596组/4,706条。


### S4 work：跨章直接端点身份组登记（2026-10-16）

- `cand-5373` → `workgrp-b9528b8c029410` → `units/works/pozzo-fresco-cycle-tribune-apse-s-ignazio`；9 条直接 S2 断言，其中 8 条关系候选留待 S6。cand-5373 为 workgrp-b9528b8c029410 单候选 new 组。第3章 pp.89–90 将 Pozzo 在 S. Ignazio 的工作分为不同项目：早先拱顶画另有 cand-5074，已登记为 `units/works/pozzo-fresco-vault-s-ignazio`；拱顶画的 modèle cand-4002 亦已有独立 KU。cand-5373 指 p.89 所称1685年后若干年间绘于 tribune 与 apse 的叙事壁画组，题材为耶稣会早期事件并以 La Storta 应许为高潮，因此登记新作品身份，不复用拱顶卡。Haskell 对其与 Gaulli 的比较及“反 Baroque”判断按作者意见记录。9条直接 S2 断言中8条关系候选留待 S6；场所和叙事端点不并入。

本批新增1张作品 KU，每个 S3 new 身份组一张；卡片保存双语描述及精确书内引文。不将关系候选升级为正式关系，也未开展 S5 外部补足。S4 当前已登记241组/300条成员映射，尚待登记4,595组/4,705条。


### S4 work：跨章直接端点身份组登记（2026-10-16）

- `cand-4248` → `workgrp-49e44482856548` → `units/works/titian-worship-of-venus`；9 条直接 S2 断言，其中 8 条关系候选留待 S6。cand-4248 为 workgrp-49e44482856548 单候选 new 组，跨第2章 pp.25、31 与第4章 p.105。第2章记 Aldobrandini 将提香《维纳斯崇拜》与另外两幅作品从费拉拉带至罗马，并讨论其接受；注释对 d’Arpino、Albani、Rubens 的复制关系使用复数范围和 Walker 的限定。第4章确认正确标题拼写，记该画于1637年送往西班牙及版画和 Padovanino 临摹。原作、其他两画、复制品、后出版本和版画均保持边界；不依据注释推导逐件版本谱系。9条直接 S2 断言中8条关系候选留待 S6。

本批新增1张作品 KU，每个 S3 new 身份组一张；卡片保存双语描述及精确书内引文。不将关系候选升级为正式关系，也未开展 S5 外部补足。S4 当前已登记242组/301条成员映射，尚待登记4,594组/4,704条。


### S4 person：跨章人物直接端点身份组登记（2026-10-16）

- `cand-0168,cand-0169` → `new-person:antonio-balestra-208aac65cb` → `units/persons/antonio-balestra`；10条直接 S2 断言，10条关系候选留待 S6。两条索引候选按跨章全名锚点归入同一人物；仅登记书中支持的画家身份与语境。未新增正式关系，未开展 S5 外部补足。

S4 当前已登记243组/303条成员映射，尚待登记4,593组/4,702条。


### S4 archive：1749年《Dactyliotheca Ant. M. Zanetti》登记（2026-10-16）

- `cand-10012,cand-2845` → `archive-group-zanetti-dactyliotheca-1749` → `units/archives/dactyliotheca-ant-m-zanetti-1749`；12条直接 S2 断言，10条关系候选留待 S6。第337页对早期 Albrizzi 宝石出版物的回指与第344页给出的 1749 年题名共同确认同一图录；不与后来的 Pasquali《Dactylografa Smithiana》或被编目的实体收藏合并。未新增正式关系，未开展 S5 外部补足。

S4 当前已登记244组/305条成员映射，尚待登记4,592组/4,700条。


### S4 archive：Memmo《洛多利建筑原理》跨章身份组登记（2026-10-16）

- `cand-1414,cand-1647,cand-8812` → `archive-group-memmo-elementi-lodoliana-1786` → `units/archives/elementi-architettura-lodoliana`；12条直接 S2 断言，7条关系候选留待 S6。第10章 p.320 注2 将题名、Memmo归属及罗马1786年初刊置于同一说明中；第15章 p.367正文与注1区分首卷和完整两卷本；第21章参考书目保留 OCR 异文“Memnio”。卡片只记录 Haskell 对题名、责任者、理论内容及出版沿革的叙述，不声称已独立查阅1786或1834年版本；不与 Memmo 的《Apologhi》或被引学术文献合并。本次不新增正式关系或进行 S5 外部补足。

S4 当前已登记245组/308条成员映射，尚待登记4,591组/4,697条。


### S4 archive：Bellori《未刊传记：圭多·雷尼、安德烈亚·萨基、卡洛·马拉塔》1942年版身份组登记（2026-10-16）

- `cand-4831` → `archive-group-ce7b481807cb` → `units/archives/le-vite-inedite-bellori-piacentini-1942`；14条直接 S2 断言，其中9条引用关系候选留待 S6。第21章参考书目 OCR L138 明列题名、Piacentini 编、Roma 1942；第1、7章注释提供该版在本书中的引用位置。本卡记录 Haskell 所引书目对象，不声称阅读 Bellori 原书；人物 Bellori KU 与该 archive 分开。本次不新增正式关系或进行 S5 外部补足。

S4 当前已登记246组/309条成员映射，尚待登记4,590组/4,696条。


### S4 archive：Lumbroso《卡西亚诺·达尔·波佐生平札记》1874年版身份组登记（2026-10-16）

- `cand-5683` → `archive-group-01f343df099c` → `units/archives/lumbroso-notizie-cassiano-dal-pozzo-1874`；10条直接 S2 断言，其中9条书目引用候选留待 S6。第21章 p.428 参考书目给出题名、G. Lumbroso、Torino 与1874年；第4章 p.101 注1及第7章 p.177 注4显示本书引用该书的不同页码。只登记该明确题名和版本，不表示已读 Lumbroso 原书。`cand-5648`、`cand-5649`、`cand-5643` 与 `cand-5462` 保持各自 undecided，不并入此组。本次不新增正式关系或进行 S5 外部补足。

S4 当前已登记247组/310条成员映射，尚待登记4,589组/4,695条。


### S4 archive：Pollak 1913年艺术家书信补编身份组登记（2026-10-16）

- `cand-4359` → `archive-group-4aa75cf1b8d7` → `units/archives/pollak-italienische-kuenstlerbriefe-1913`；10条直接 S2 断言，其中8条出版物引用候选留待 S6。第21章 p.433 参考书目列出 O. Pollak 的题名、所在年鉴与1913年 Beiheft；第1、2、7章引用同一书目项的不同页码。仅登记补编出版物，不合并其所刊个别信件；cand-4358、cand-4364、cand-4382、cand-4943、cand-7073、cand-3544 保持各自信件对象。与 Pollak 的 *Die Kunsttätigkeit unter Urban VIII*（cand-11421）分开。未查阅补编原件，不新增正式关系或进行 S5 外部补足。

S4 当前已登记248组/311条成员映射，尚待登记4,588组/4,694条。


### S4 archive：Poussin 1911年 Jouanny 编订《书信集》身份组登记（2026-10-16）

- `cand-4634` → `archive-group-449d2522330e` → `units/archives/poussin-correspondance-jouanny-1911`；9条直接 S2 断言，其中8条书目引用候选留待 S6。第21章 p.433 参考书目列题名、Ch. Jouanny、Paris 与1911年；第4、6、7章注释提供不同页码的书内引用位置。个别信件与被引出版物保持对象边界；本次不新增正式关系、外部身份记录或 S5 补足。

S4 当前已登记249组/312条成员映射，尚待登记4,587组/4,693条。


### S4 archive：Soprani/Ratti 1768年第二版跨章身份组登记（2026-10-16）

- `cand-5160` → `archive-group-d2f847262fa3` → `units/archives/soprani-vite-genovesi-ratti-1768`；书目候选仅一项，登记为 archive。第21章 p.437 明列 Raffaello Soprani、题名、Ratti 修订增注、两卷、Genova 1768；第1、3、6、7、8章均有卷页引文。卡片逐条保存本书的对应引文位置，原版及被引页未独立查阅。
- 直接 S2 记录共10条，其中7条为关系候选，留待 S6；第3章 p.74 与第8章 p.234 两条保留为书目／转述记录，不升格为正式关系。第7章 p.197 的 Ratti 1713年说法与正文1714年说法仍为未解决冲突。
- 未将出版物与 Soprani、Ratti 人物或其他版次合并；未新增外部身份、S5字段或正式关系。候选映射至本 KU。

S4 当前已登记250组/313条成员映射，尚待登记4,586组/4,692条。


### S4 archive：de la Harpe《Il Filosofo dell’Alpi》身份组登记（2026-10-16）

- `cand-1345`（索引子条目）与 `cand-9829`（第10章正文）→ `archive-group-la-harpe-filosofo-dell-alpi-1780` → `units/archives/il-filosofo-dell-alpi-ode`；两条 S3 new 候选对应一张 archive KU。索引 p.328 与正文 p.328 的题名互证；注1刊记称其为 de la Harpe 的 ode，由 Giuseppe Fossati 改写成意大利无韵诗，Giacomo Storti 于 Venezia 刊行，MDCCLXXX（1780）。未查阅该刊本。
- 直接 S2 记录8条，其中7条关系候选留待 S6。第10章 p.327 跨页段的 Markdown OCR 有语法损坏，按 p.328 续文和既有 S2 记录保留，不从损坏句段外推。S3 已将诗作与同页另述的宣传册／版画分开；人物与出版者端点亦不并入本 KU。
- 题名转录存在正文 `II` 与索引 `Il`、注释 OCR `del!` 的差异；卡片采用组内规范题名并保留来源摘录，不声称扫描页校勘。未新增正式关系或 S5 外部补足。

S4 当前已登记251组/315条成员映射，尚待登记4,585组/4,690条。


### S4 archive：Friedlaender《Caravaggio Studies》1955年版身份组登记（2026-10-16）

- `cand-4375` → `archive-group-0f865c2062ea` → `units/archives/friedlaender-caravaggio-studies-1955`；第21章 p.423 书目列 Walter Friedlaender、题名、Princeton 与1955年；第1、2、3、5章引用相关页码。卡片登记书目身份与 Haskell 的引文位置，不称查阅原书或核实引文内容。
- 直接 S2 记录8条，其中6条关系候选留待 S6；第3章 p.69–70 的一条注释是纯书目定位，不作关系处理。第3章 p.64 中 Cozzi 对前述观点的反驳保留 Haskell 的限定，本批不裁决学术争论。
- 未并入 Friedlaender 人物或其他出版物；未新增正式关系、外部身份或 S5 补足。

S4 当前已登记252组/316条成员映射，尚待登记4,584组/4,689条。


### S4 archive：G. Briganti《Pietro da Cortona》1962年版身份组登记（2026-10-16）

- cand-4473 → archive-group-68573842c8b3 → units/archives/briganti-pietro-da-cortona-1962；第21章 p.423 书目列 G. Briganti、Pietro da Cortona、Firenze 1962。第1、2、3、6、7章多处引用该书；本次登记书目身份，不表示查阅原书或核验被引页。
- 直接 S2 记录10条，其中6条关系候选留待 S6。Haskell/OCR 中出现 Briganti 与 Brigand 的转录差异；卡片保留书目中的 G. Briganti，不扩写姓名，也不裁决作品归属争论。
- 与 Pietro da Cortona 人物 KU 区分；未新增正式关系、外部身份或 S5 补足。

S4 当前已登记253组/317条成员映射，尚待登记4,583组/4,688条。


### S4 archive：Andrea Memmo Petizion 488 财物清单档案身份组登记（2026-10-16）

- cand-10514 → archive-group-3c5e5c17bee5 → units/archives/andrea-memmo-inventory-petizion-488-1792；Haskell 第15章 p.368 注3将记录定位于 Archivio di Stato, Venice, Petizion 488，列出1792年1月30日及1792/3年2月24日 M.V. 两个日期，并称部分内容刊于 Levi II, p.254。档案原件及刊本未查阅。
- 直接 S2 记录6条，全部为关系候选，留待 S6。清单身份不表示清单内容或 Haskell 的 Mengs 图画、版画转述已独立验证；未将任何端点并入本 KU。
- 未新增正式关系、外部馆藏身份或 S5 补足。

S4 当前已登记254组/318条成员映射，尚待登记4,582组/4,687条。


### S4 archive：Haskell 与 Rinehart 达尔·波佐藏品文章身份组登记（2026-10-16）

- cand-5658 → archive-group-a17b1987a05a → units/archives/haskell-rinehart-dal-pozzo-collection-1960；第21章 p.425 书目列 F. Haskell、S. Rinehart、文章题名、Burlington Magazine、1960年及 pp.318–326；第4章多处引用。文章本身未独立查阅。
- 直接 S2 记录8条，其中6条关系候选留待 S6。书目 OCR 年份写作 i960；S2 候选记录注明扫描页读作1960，卡片保留 OCR 引文并说明该差异。被引库存原件与文章保持分立。
- 未新增正式关系、外部身份或 S5 补足。

S4 当前已登记255组/319条成员映射，尚待登记4,581组/4,686条。


### S4 archive：Albrizzi 1736年起 Bossuet 法文全集身份组登记（2026-10-16）

- cand-9987 → archive-group-f295307228d2 → units/archives/bossuet-french-edition-albrizzi-1736。第13章 pp.334–335 称 Albrizzi 于1736年开始刊行 Bossuet 著作法文全集，每卷有奥地利王室成员献词，Piazzetta 为其绘制插图；注3提及1755年第八卷献词。未查阅该版各卷。
- 直接 S2 记录8条，其中7条关系候选留待 S6。现有书内材料没有确切原题、完整刊记或总卷数；登记只指向该多卷版整体，不推断总卷数，也不单独建卷册卡。
- 未新增正式关系、外部书目身份或 S5 补足。

S4 当前已登记256组/320条成员映射，尚待登记4,580组/4,685条。


### S4 archive：Malvasia《Felsina Pittrice》1678年作品身份组登记（2026-10-16）

- cand-6933 → archive-group-04dd83a032f3 → units/archives/felsina-pittrice-1678-work，按 S3 组登记1678年作品身份。第7章 p.189 称该作题献 Louis XIV；第7、8章另有 Malvasia 卷页引文。第21章书目列两卷本 Bologna 1841 年版，候选 cand-11384 当前为 undecided；本卡不把该 edition 映射到1678年作品。
- 直接 S2 记录6条，全部为关系候选，留待 S6；卷页指向的具体印本未独立确认或查阅。
- 未新增正式关系、外部版本身份或 S5 补足。

S4 当前已登记257组/321条成员映射，尚待登记4,579组/4,684条。


### S4 archive：P. Pecchiai《Il Gesù di Roma》1952年版身份组登记（2026-10-16）

- cand-4996 → archive-group-3fd673cd267d → units/archives/pecchiai-il-gesu-di-roma-1952；第21章 p.433 书目列作者缩写、题名与 Roma 1952。第3章将其指作耶稣堂史的详细研究，并在 pp.79、84、85、91 注释中引用相关页码。原书未查阅。
- 直接 S2 记录7条，其中6条关系候选留待 S6。书目身份指向 Pecchiai 的书，不与耶稣堂建筑、耶稣会机构或画作混同。
- 未新增正式关系、外部身份或 S5 补足。

S4 当前已登记258组/322条成员映射，尚待登记4,578组/4,683条。


### S4 archive：Baldinucci《Vita del Cavaliere Gio. Lorenzo Bernini》1948年版身份组登记（2026-10-16）

- cand-4548 → archive-group-5a4cacb078dc → units/archives/baldinucci-bernini-biography-samek-ludovici-1948；第21章书目列 Filippo Baldinucci、题名、Sergio Samek Ludovici 的研究与注释、Milano 1948；第1、2、3、6、7章多处引用不同页码。原书未查阅。
- 直接 S2 记录8条，其中6条关系候选留待 S6。部分 OCR 形态（BaMinucci、pp. in ff.）及 S2 的校读依据照实保留，不将其写成原书已核读。
- 与作者人物及 Bernini 作品对象区分；未新增正式关系、外部身份或 S5 补足。

S4 当前已登记259组/323条成员映射，尚待登记4,577组/4,682条。


### S4 archive：《Il Gran Teatro delle Pitture e Prospettive di Venezia》1720年出版物身份组登记（2026-10-16）

- `cand-1453` → `archive-group-9db379e0572e` → `units/archives/il-gran-teatro-pitture-prospettive-venezia-1720`；依据第13章 p.332 的题名、1720年出版信息及第333页跨页回指，并以索引 L.csv#111 作为候选锚点。OCR 的 `II` 与 S2 在 CHP-13.pdf 实体页1读取的 `Il` 区别已记录；显示译名为工作译名，不扩展未载的出版信息。
- 直接 S2 记录4条，均为关系候选：出版者 Domenico Lovisa、其资助角色、插图艺术家（含已复用人物 KU Giambattista Tiepolo）及旅行者受众；4条均留待 S6。Lovisa 的人物候选 `cand-1452` 属独立 S3 person 新组，未并入本 archive 组；未新增正式关系或 S5 补足。
- 本卡不合并同段另述的 *Le Fabriche e Vedute di Venetia* 与 Marieschi 1741 年出版物，也不将未逐一辨明的插图拆成 work KU。原出版物未独立查阅。

S4 当前已登记260组/324条成员映射，尚待登记4,576组/4,681条。


### S3/S4 follow-up: Galiani 人物端点与 *Della Moneta* 文本身份（2026-10-16）

- S2 端点回核后，`cand-1102`（person）由原 `undecided` 改为 `new`，组 `sg3-person-cand-1102`。第10章 p.318 L136 明确称 Abate Galiani 的论著 *Della Moneta* 于1750年问世；当前 manifest 无同一人物 KU。裁决只保留原书人名形式，不扩展个人全名、传记或外部身份。
- S3 archive 组将 `cand-1103`（Galiani 索引中的 *della Moneta* 子项）与 `cand-9706`（正文具名论著）合并为 `archive-group-4ef32237dfae`。两者同为 archive、题名对应同一文本且均锚定 p.318；没有证据表明指向不同版次。`cand-9706` 原组标记 `archive-group-d425674fd21e` 保存在其 `resolution_note` 的更正说明中。
- S4：`cand-1102` → `units/persons/abate-galiani`；`cand-1103,cand-9706` → `units/archives/della-moneta-treatise-1750`。分别建立人物与文本卡，双语显示名均保留限定；文献卡不指定版次、出版地或存世副本。
- `st-chp10-p318-galiani-della-moneta-appeared-in-1750` 现以 `cand-1102` 为人物主语、`cand-9706` 为论著宾语；1条直接关系候选保持待 S6 裁决。本次未新增正式关系、外部身份标识或 S5 补足。

S4 当前已登记262组/327条成员映射，尚待登记4,574组/4,679条。


### S4 archive：Muratori《Della pubblica felicità》1749年论著身份组登记（2026-10-16）

- `cand-1718`（索引子项）与 `cand-9705`（正文题名）→ `archive-group-muratori-della-pubblica-felicita-text` → `units/archives/della-pubblica-felicita-1749`；第10章 p.318 记 Muratori 于1749年出版该论著。S2 对照扫描页校读题名为 `Della pubblica felicità, oggetto de’ buoni principi`，原 OCR 形式保留在 sources.original_quotes 与过程记录；具体版次、出版地及存世副本未由本段确定。
- p.318 的人物 mention 与 statement 主语已从 archive 子项候选移至 `cand-1717`。该 person 候选保留 `undecided`（只有缩写形式，尚无全名对齐）；因此作者／出版关系候选继续待证，本批不登记人物 KU、不新增正式关系或 S5 补足。
- S4 当前已登记263组/329条成员映射，尚待登记4,573组/4,677条。


### S4 person：Enzo Bentivoglio 跨章身份组登记（2026-10-16）

- cand-0290 → new-person:bentivoglio-enzo-62e0406c74 → units/persons/enzo-bentivoglio；当前 S3 组仅含此候选。候选索引 B.csv#137 明列 “Bentivoglio, Enzo”，索引页码为48、49、50、55、182；正文第2章 p.48 将 Enzo 列为 Ippolito 的弟弟之一，并称其曾一度担任从 Ferrara 至 Rome 的“ambassador”，作者并称 Enzo 与 Guido 热爱艺术。卡片以索引和正文为依据，不补全个人姓名或传记，不与 Guido 人物或 Bentivoglio 家族合并；未使用外部身份源。
- 涉及 Enzo 的12条 S2 陈述中，11条为关系候选，全部留待 S6；本次不登记正式关系或 S5 补足。
- 修正 st-chp2-seciv-l65-77-enzo-buys-borghese-palace-1619 的原文引句与行范围：原存引句止于买方姓名前，现据 p.49 L67–68 保存“his brother Enzo bought in 1619”，source_line_end 由67改为68。断言、端点、1619日期及脚注 L214 的Bentivoglio 家族表述均未改；主文与脚注的归属表述继续并列，不作静默消解。

S4 当前已登记264组/330条成员映射，尚待登记4,572组/4,676条。


### S4 person：Jan Miel 跨章身份组登记（2026-10-16）

- cand-1662 → new-person:jan-miel-27b41b4426 → units/persons/jan-miel；该 S3 组只含此候选。索引 M.csv#202 列名 Miel, Jan，并指向 p.126、127、137、140、207；第5章 p.126 称其为佛兰德画家并记其遗嘱，扫描页校读记录确认 OCR 的 Jan Miei 应读 Jan Miel。第5章 p.137、140及第8章 p.207 继续以同一姓名讨论插图合作、绘画风格和 Roomer 搜求作品的例子；不据此认定未指名作品或额外传记。
- 直接涉及该人物的13条 S2 陈述均为关系候选，全部留待 S6；本次未登记正式关系、外部身份或 S5 补足。

S4 当前已登记265组/331条成员映射，尚待登记4,571组/4,675条。


### S4 person：Benedetto Gennari 跨章身份组登记（2026-10-16）

- cand-1127 → new-person:benedetto-gennari-2efcec4904 → units/persons/benedetto-gennari；该 S3 组只含此候选。索引 G.csv#34 指向第7章 p.189、196；p.189 将其列为敬慕 Louis XIV 的博洛尼亚画家之一，同时保留 Haskell 对其动机的怀疑；p.196 称其来自 Bologna、为 Guercino 之侄，记其在 England 与 Paris 工作及1688年离开 England 后的去向。本卡保留书内归属，不补入生卒、外部身份或完整传记。
- 涉及该人物的13条 S2 陈述中12条为关系候选，均留待 S6；本次未登记正式关系或 S5 补足。

S4 当前已登记266组/332条成员映射，尚待登记4,570组/4,674条。


### S4 person：Dominique De Non／Dominique Vivant-Denon 跨章身份组登记（2026-10-16）

- cand-1752 → new-person:de-dominique-non-denon-dominique-vivant-d852c29287 → units/persons/dominique-de-non-vivant-denon；索引 N.csv#32 与第15章 p.371 同列 Dominique De Non 和 Dominique Vivant-Denon；正文 L77 明确以 “who later (as Dominique Vivant-Denon)” 说明后者是同一人物的后用名。对应索引交叉引用 cand-2930 保持 excluded，索引中的 Voltaire 肖像版画候选 cand-1753 保持 work，均未并入人物组。
- 涉及该人物的15条 S2 陈述中13条为关系候选，均留待 S6；本次不确定 Napoleon 的具体端点、不登记正式关系或 S5 补足。

S4 当前已登记267组/333条成员映射，尚待登记4,569组/4,673条。


### S3 re-review: Passeri reuse existing person KU（2026-10-16）

- cand-1856 原按新人物组 new-person:giambattista-passeri-110a86b546 待登记。回查发现 manifest 已有 units/persons/giambattista-passeri，其卡片以 Giovanni Battista Passeri 为规范名，并明确将 Giambattista Passeri 列为原书常用名／本章名形；卡片第1章 p.3 L15–18 又引 Haskell 称 art-chronicler Giambattista Passeri。全书索引 P.csv#56 以 Passeri, Giambattista 为主项并指向 p.3，完整书候选在第5章 p.132 L8 再称 critic Giambattista Passeri。名字、来源锚点和人物角色共同支持复用同一人物 KU，无须外部身份裁定。
- 将 cand-1856 的决定由 new 改为 same，映射至 units/persons/giambattista-passeri；原 new 身份组标签保留在 alignment 的 previous_group_label 与本记录中。未创建重复卡片，未改动 S2 陈述或既有 KU 正式关系。

S3 same=1,762 candidates / 1,025 existing KUs; new=5,005 candidates / 4,835 groups. S4 registered=267 groups/333 mappings; pending=4,568 groups/4,672 candidate mappings.


### S4 person：George III 跨章身份组登记（2026-10-16）

- cand-1141 → new-person:england-george-iii-of-0d549c6e37 → units/persons/george-iii；该 S3 组只含此候选。索引 G.csv#48 将人物列为 George III, King of England，指向第10章 pp.292、300、303、309，第15章 p.361，第19章附录5 p.393及第20章后记 p.406。正文 p.300、310及第15章明确写作 King George III / George III；第19章附录讨论 Smith 于1762年售出全部收藏还是部分选择，并明确表示无法得出最终结论。本卡保留该限定，不把交易范围写成已定事实；未使用外部身份源。
- 涉及该人物的41条 S2 陈述中28条为关系候选，均留待 S6；未登记正式关系或开展 S5 补足。

S4 当前已登记268组/334条成员映射，尚待登记4,567组/4,671条。


### S3 re-review: Castiglione index subentries (2026-10-16)

- cand-0602 是人物身份组 new-person:benedetto-castiglione-giovanni-c3cfd274af 的主项候选。复核 C.csv#127、C.csv#128、C.csv#129：三者均与主项同为 Castiglione, Giovanni Benedetto，分别为“drawings in Sagredo collection”“importance of for 18th century”和“print of Diogenes”子项。原始待决理由是没有映射 S2 正文锚点；本次逐页回查解除该缺口。
- 第9章 p.266 L309 明称 “the Genoese artist Giovanni Benedetto Castiglione”，并在同段讲述 Sagredo 的 Castiglione 素描；p.266-267 L309–316 直接对应素描集及其对十八世纪威尼斯趣味的影响，支撑 cand-0603 与 cand-0604 并入主项。第5章 p.124 L38–39 写 Castiglione 的出版者为 Simonelli 献上 Diogenes 版画，脚注 p.124n L47–49 又明确称 “Castiglione's print of Diogenes”，支撑 cand-0605 并入同一画家。cand-0602 已有对应 S2 mention / statement 锚点；这里只把索引子项映射到该同一来源人物，不新造 S2 事实或正式关系。
- 将 cand-0603、cand-0604、cand-0605 从 undecided 改为 new，统一并入 new-person:benedetto-castiglione-giovanni-c3cfd274af；原决定和理由保存在各自 alignment resolution_note 中。S3 new 候选增加3，身份组数不变；undecided 减少3。没有外部身份源、KU 登记或 S6 关系裁决。

S3 same=1,762/1,025; new=5,008/4,835; undecided=5,528. S4 registered=268/334; pending=4,567/4,674.


### S4 person：Giovanni Benedetto Castiglione 跨章身份组登记（2026-10-16）

- cand-0602, cand-0603, cand-0604, cand-0605 → new-person:benedetto-castiglione-giovanni-c3cfd274af → units/persons/giovanni-benedetto-castiglione；该 S3 身份组四条候选共用一张 KU。索引 C.csv#126–129 以 Castiglione, Giovanni Benedetto 列出主项及三个相关子项；原始正文回查已分别锚定 Sagredo 收藏中的素描、其对十八世纪的意义和 Diogenes 版画。第4章 p.114 直接给出热那亚画家全名，并限定无法确认 Cassiano 曾直接关注他；第5章 p.124 正文及注释、第8章 p.207、第9章 pp.266–267 提供相应书内语境。中文标题为项目工作译名；未使用外部身份源，也未把 S2 关系候选转为正式关系。
- 主项 cand-0602 涉及34条 S2 陈述，其中27条为关系候选，均留待 S6 逐条审查；未开展 S5 补足。

S4 当前已登记269组/338条成员映射，尚待登记4,566组/4,670条。


### S4 person：Miguel de Molinos 跨章身份组登记（2026-10-16）

- cand-1680 → new-person:de-miguel-molinos-a5f7ffff73 → units/persons/miguel-de-molinos；该 S3 人物身份组只含一个候选。索引 M.csv#220 与第3章 p.81 的正文全名锚点一致。第3章称其为西班牙司铎，记其1664年抵达罗马并概述其教义及影响；第3章 p.82 明言无法判断另一位艺术家关于基督圣血的观念是否源自 Molinos。卡片保留该不确定性；中文名为项目工作译名，未使用外部身份源。
- 涉及该人物的10条 S2 陈述均为关系候选，留待 S6 逐条审查；没有登记正式关系，也未开展 S5 补足。

S4 当前已登记270组/339条成员映射，尚待登记4,565组/4,669条。


### S4 person：Sir Isaac Newton 跨章身份组登记（2026-10-16）

- cand-1739 → new-person:isaac-newton-800ef74820 → units/persons/isaac-newton；该 S3 人物身份组只含一个候选。索引 N.csv#19 跨章定位第10章 pp.288、301、318–320 及第20章后记 p.408；第10章 p.301 和后记 p.408 明确写出 Sir Isaac Newton，第10章 pp.318–320 继续以 Newton 讨论哲学、光学语境。候选全名与索引、正文锚点一致；未发现既有同身份人物 KU，未使用外部身份源。
- 涉及该人物的31条 S2 陈述中24条为关系候选，留待 S6 逐条审查；没有登记正式关系，也未开展 S5 补足。

S4 当前已登记271组/340条成员映射，尚待登记4,564组/4,668条。


### S3-S4 re-review: Pittoni reuses existing person KU (2026-10-16)

- cand-1950 与 cand-1952 原属 new-person:battista-giovan-pittoni-01fdd70f9d，索引主项和 German patrons 子项均写作 Pittoni, Giovan Battista。既有人物 KU units/persons/pittoni 的双语卡片名为 Giovanni Battista Pittoni，并已用本书图版目录、Zeri 作者字段与Tillotson 纪念画图注建立“图注 Pittoni”身份；全书 cand-3870 亦已判同并映射到该 KU。第10章 p.288 将 Pittoni 列在McSwiny 威尼斯绘画团队中，第10章 p.313 称其为威尼斯历史画家并明确关联 German patrons 子项。全名变体、画家身份和同一图版项目共同支持两候选复用既有身份，不是仅按姓氏合并。
- cand-1950、cand-1952 均由 new 改为 same，映射至 units/persons/pittoni；原 new 组标签及理由分别保留在各自 alignment 行中。未创建重复卡片，未新增正式关系；涉及该人物的20条关系候选仍待 S6。

S3 same=1,764/1,025; new=5,006/4,834; undecided=5,528. S4 registered=271/340; pending=4,563/4,666.


### S4 person：Paolo Veronese 跨章身份组登记（2026-10-16）

- cand-2755 → new-person:paolo-veronese-4afb8ff702 → units/persons/paolo-veronese；该 S3 人物身份组只含一个候选。索引 UVWXYZ.csv#91 与第5章 p.128、第8章 p.216 的正文全名相互印证；第10章 p.284继续以 Veronese 指称同一画家。索引正文存在 pp.279、355/356 的定位差异，候选原记录保留了该差异，本卡引用直接核对过的正文页码，不将索引差异改写为已解决。未发现同身份既有 KU，未使用外部身份源。
- 涉及该人物的26条 S2 陈述中19条为关系候选，留待 S6 逐条审查；未登记正式关系，也未开展 S5 补足。

S4 当前已登记272组/341条成员映射，尚待登记4,562组/4,665条。


### S4 person：Loménie de Brienne 跨章身份组登记（2026-10-16）

- cand-0452 → new-person:brienne-de-lomenie-6472b0f466 → units/persons/lomenie-de-brienne；该 S3 人物身份组只含一个候选。索引 B.csv#299、正文第7章 p.181 的姓名形式 Loménie de Brienne，以及参考书目所列 Louis-Henri de Loménie Comte de Brienne 相互对应。第7章 p.184–186 在同一叙事中继续以 Brienne 称呼，支持将这些姓名形归入同一来源人物。未发现同身份既有 KU；中文名为项目工作译名，未使用外部身份源。
- 涉及该人物的19条 S2 陈述均为关系候选，留待 S6 逐条审查；没有登记正式关系，也未开展 S5 补足。

S4 当前已登记273组/342条成员映射，尚待登记4,561组/4,664条。


### S4 person：Leonardo da Vinci 跨章身份组登记（2026-10-16）

- cand-1390 → new-person:da-leonardo-vinci-092752ba56 → units/persons/leonardo-da-vinci；该 S3 人物身份组只含一个候选。索引 L.csv#47 与第4章 pp.106、113、第10章注释 p.319 均以完整姓名或稳定简称指称 Leonardo da Vinci。manifest 中有 Leonardo Pesaro、Leonardo Valmarana 两名不同人物，均与本候选全名不同，不作为同一性复用目标。未使用外部身份源。
- 涉及该人物的19条 S2 陈述中17条为关系候选，留待 S6 逐条审查；未登记正式关系，也未开展 S5 补足。

S4 当前已登记274组/343条成员映射，尚待登记4,560组/4,663条。


### S4 person：Gaetano Zompini 跨章身份组登记（2026-10-16）

- cand-2874, cand-2877 → new-person:gaetano-zompini-1b920c543e → units/persons/gaetano-zompini；该 S3 身份组两条候选共用一张 KU。索引 UVWXYZ.csv#211、#214 以同一姓名列出人物主项和 Zanetti 相关子项；第9章 pp.273–274 与第13章 pp.340、344 的正文均有相应全名锚点。本卡将索引子项映射到同一人物，不另建人物或作品 KU；中文名为项目工作译名。
- 涉及该人物的14条 S2 陈述中10条为关系候选，均留待 S6 逐条审查；没有登记正式关系，也未开展 S5 补足。

S4 当前已登记275组/345条成员映射，尚待登记4,559组/4,661条。


### S4 person：Giuseppe Zais 跨章身份组登记（2026-10-16）

- cand-2830 → new-person:giuseppe-zais-1e534535f3 → units/persons/giuseppe-zais；该 S3 人物身份组只含一个候选。索引 UVWXYZ.csv#167 与第9章 p.261、第10章 p.328、附录5 p.393 的正文全名相互印证。附录5 对相关绘画活动与1762年交易的时间关系提出问题但未定论，卡片保留此边界；未发现同身份既有 KU，中文名为项目工作译名，未使用外部身份源。
- 涉及该人物的25条 S2 陈述中16条为关系候选，留待 S6 逐条审查；没有登记正式关系，也未开展 S5 补足。

S4 当前已登记276组/346条成员映射，尚待登记4,558组/4,660条。

### S3 冲突复核：Liechtenstein Prince Wenzel 索引组的年代错配（2026-10-16）

- cand-1405 原决定为 `new`，原组标签 `new-person:liechtenstein-of-wenzel-d8f638b83e` 保留。复核发现前次 resolution_note 所称“source anchor gives a full personal name”不实：第7章 p.169 L8 只称 “the Prince of Liechtenstein”；第7章 p.194 L35 及 p.195 L39 也只用头衔，p.195 明确将所引书信定为1691年。原书索引 Markdown 将 Wenzel 关联至 pp.169、194–195、341、345；S1 `L.csv#62` 则将同一条目列为 pp.169、194、195、234n、345，页码范围本身存在不一致。
- 外部身份核对：Liechtenstein Princely Collections 的 Joseph Wenzel I 人物页给出生卒1696–1772，故其不可能是1691年书信作者；官方馆藏记录 FA 67.2 为 Johann Adam Andreas I 于1692-12-06 致 Marcantonio Franceschini 的信；Treccani《意大利人传记辞典》称 Prince Adamo Giovanni 与 Franceschini 的关系始于1691年。合并的姓名变体、年代与书信对象都指向既有 `units/persons/giovanni-adamo-piola`，但索引条目还覆盖较晚页码，故不能把整个 cand-1405 组简单改映为 Johann Adam，也不能按索引直接建立 Wenzel 新卡。
- 将 cand-1405 从 `new` 改为 `conflict`，清楚保留冲突两侧与 S3 后续去向：拆分并复核 p.169、pp.194–195 的正文指代是否可映射到既有 Johann Adam KU；索引所称 Wenzel 的较晚页码须另与源文候选核对。第13章只称 Prince 的木刻赠送 cand-10094 与 Zanetti 往来信件候选 cand-10202 继续各自 `undecided`，不因同一姓氏／头衔合并。16条关联 S2 关系候选仍待身份端点拆分及后续 S6；没有建立新 KU 或正式关系。
- 本次核验来源与访问日期：Liechtenstein Princely Collections，Joseph Wenzel I 人物页，https://www.liechtensteincollections.at/en/princes/prince-joseph-wenzel-i-von-liechtenstein；馆藏信件 FA 67.2，https://www.liechtensteincollections.at/en/collections-online/prince-johann-adam-andreas-i-von-liechtenstein-to-marcantonio-franceschini-he-sends-once-again-the-precise-measurements-for-the-paintings-he-has-o；Treccani，Marcantonio Franceschini，https://www.treccani.it/enciclopedia/marcantonio-franceschini_(Dizionario-Biografico)/；均访问于2026-10-16。

S3 same=1,764/1,025; new=5,005/4,833; conflict=8; undecided=5,528. S4 registered=276/346; pending=4,557/4,659.

### S4 person：Giovan Gioseffo dal Sole 跨章身份组登记（2026-10-16）

- cand-2480 → new-person:dal-gioseffo-giovan-sole-8d002c1de3 → units/persons/giovan-gioseffo-dal-sole；该 S3 人物身份组只含一个候选。索引 S.csv#169 与第7章 p.201、第8章 pp.203、214注、223、225、227、第10章 p.282 的正文共同提供跨章身份锚点。第8章和索引作 Giovan Gioseffo dal Sole，第10章作 Gian Gioseffo dal Sole；Treccani《百科全书》以 Giovan Gioseffo dal Sole 立目并记其为博洛尼亚画家（1654–1719）。ICCD 国家目录记录同一姓名和年代，其具体作品条目标为 attributed，本卡不把这些作品归属升级为已确认。未发现同身份既有 person KU；Gioseffo Guidalotti Franchini 是不同 archive 作者，不合并。中文名为项目工作译名。
- 涉及该人物的17条 S2 陈述中15条为关系候选，均留待 S6 逐条核查；未建立正式关系，未开展 S5 补足。

S4 当前已登记277组/347条成员映射，尚待登记4,556组/4,658条。

### S4 person：Paganino Gaudenzi 身份组登记（2026-10-16）

- cand-1116 → new-person:gaudenzi-paganino-bab47b4e3f → units/persons/paganino-gaudenzi；S3 身份组只有一个候选，对应全书索引 G.csv#23 与第4章 p.109。原书以全名称其为学者，叙述 Cassiano dal Pozzo 于1647年请他寄来肖像；p.117 注2列出1641至1647年二人往来书信。Treccani DBI（Giampiero Brunelli, vol. 52, 1999; https://www.treccani.it/enciclopedia/paganino-gaudenzi_(Dizionario-Biografico)/）与瑞士历史词典（Francesca Negroni; https://hls-dhs-dss.ch/it/articles/015853/2007-09-05/）均以 Paganino Gaudenzi 立目并给出1595–1649年、Poschiavo 出生及 Pisa 去世；Treccani 另记其与 Cassiano dal Pozzo 约1639至1640年有通信。两辞典用于身份比对，不证明哈斯克尔所述具体肖像、通信或关系事实。未在当前 manifest 中发现同身份人物 KU；中文名为项目工作音译。
- 涉及该人物的14条 S2 关系候选留待 S6 逐条审查；没有登记正式关系，也未开展 S5 补足。
- 登记后表审计发现，身份属性与外部链接的 Markdown 表格尚无对应 enrichment 行；已改为带证据的条目列表，不新增 S5 字段或 enrichment。

S4 当前已登记278组/348条成员映射，尚待登记4,555组/4,657条。

### S4 person：François Duquesnoy 跨章身份组登记（2026-10-16）

- cand-0952 → new-person:duquesnoy-francois-3c8db34ada → units/persons/francois-duquesnoy；该 S3 人物组只有一个候选。索引 D.csv#54 列第2章 p.36、第4章 p.104、第7章 pp.176、179；正文分别以全名及姓氏指称雕塑家，连续提及 Bernini Baldacchino、St Andrew、Cassiano 收藏的蜡/陶土模型、St Susanna 及法国招募叙述。Treccani DBI（Gerardo Casale, vol. 42, 1993; https://www.treccani.it/enciclopedia/du-quesnoy-francois-detto-il-fiammingo_(Dizionario-Biografico)/）以 Du Quesnoy, François 立目，记 Brussels 出生及1643年7月19日 Livorno 去世，并讨论 St Susanna、St Andrew 与 Baldacchino。Getty ULAN（500115495）记录 Du Quesnoy, François、François Duquesnoy 与 Francesco Fiammingo 等异形，并列上述作品；其总述生日约1594年，来源项另有1597年。NGA 以 François Duquesnoy 记 Flemish、1597–1643。出生年份异文保留，不据此拆分身份；这些外部记录仅用于身份比对，不证明全部书内关系或作品陈述。未发现同身份既有 person KU；中文名为项目工作音译。
- 涉及该人物的14条 S2 关系候选留待 S6 逐条审查；没有登记正式关系，也未开展 S5 补足。

S4 当前已登记279组/349条成员映射，尚待登记4,554组/4,656条。

### S3-S4 person：Antonio Visentini 跨章身份组裁决与登记（2026-10-16）

- cand-2783 → new-person:antonio-visentini-26bdbd19e8 → units/persons/antonio-visentini；索引 UVWXYZ.csv#119 以 Visentini, Antonio 列出 p.301 注释、第10章 pp.306、309、322 及第13章 p.338。第10章 p.308 正文明确全名 Antonio Visentini，称其长期为 Joseph Smith 担任建筑师与书籍插图者；同章 p.306、p.309及第13章 p.338 的姓氏形式沿用这一语境。Treccani DBI（Elisabetta Molteni, vol. 99, 2020; https://www.treccani.it/enciclopedia/antonio-visentini_(Dizionario-Biografico)/）记其1688年11月21日生于威尼斯、1782年6月26日卒于威尼斯，并列建筑师、画家、雕刻家、图形设计者及建筑/透视论著作者身份，讨论其与 Smith 的工作往来、书籍插图及 Gallacini 论著。意大利文化遗产总目录（ICCD）记录 Visentini Antonio（1688/1782）；威尼斯学院美术馆目录使用 Antonio Maria Visentini，并给出 Venice, 1688–1782。姓名、日期、职业和书内 Smith/Gallacini 语境支持同一身份组。未发现同身份既有 person KU。p.309 的 his palace 所指未裁定；p.322 对 Lodoli 接触关系的说法保留推测性质，不由身份登记转成正式关系。中文名为项目工作音译。
- 涉及该候选的20条 S2 陈述中14条标为关系候选，留待 S6 逐条审查；没有登记正式关系，也未开展 S5 补足。

S4 当前已登记280组/350条成员映射，尚待登记4,553组/4,655条。

### S3-S4 person：Filippo Juvarra 跨章身份组与索引子项裁决（2026-10-16）

- cand-1339 与 cand-1340 → new-person:filippo-juvarra-61d1b03394 → units/persons/filippo-juvarra；主项 J，K.csv#23 列第6章 pp.164–165、第7章 p.202、第10章 pp.296–297；子项 J，K.csv#24 为“as artistic director in Turin”，页码仅296–297。第10章 p.296–297 正文直接称建筑师 Filippo Juvarra 为都灵城市艺术总监，职能与子项完全对应，且该页全名锚点也属于主项的页码范围。据同名、重叠页码和直接正文职能锚点，将 cand-1340 从上一轮的 index-only undecided 改判为与 cand-1339 同属一个 new-person 组；原未决理由保留在对齐记录中，当前理由说明正文锚点如何解除缺口。Treccani DBI（Tommaso Manfredi, vol. 62, 2004; https://www.treccani.it/enciclopedia/filippo-juvarra_(Dizionario-Biografico)/）记 Filippo Juvarra 1678年生于 Messina、1736年1月31日卒于 Madrid，并记录其建筑师生涯。瑞典国家博物馆人物权威记录给出意大利建筑师、Messina / Madrid、1678–1736及 Juvara、Juarra、Ivara 异形；NGA 记 Sicilian、1678–1736，并列 Juvara、Ivara。姓名、日期、建筑师身份和跨章语境支持此单一人物组。未发现同身份既有 person KU；中文名为项目工作音译。
- cand-1339 涉及13条 S2 陈述，其中12条标为关系候选；均留待 S6 逐条审查。cand-1340 原为索引子项，没有独立 S2 statement；没有登记正式关系，也未开展 S5 补足。

S4 当前已登记281组/352条成员映射，尚待登记4,552组/4,654条。

### S3 person：cand-1489 复用弗朗切斯科·费代利人物 KU（2026-10-16）

- 索引候选 cand-1489（M.csv#26，pp.325、340、408、409）原记为 new 组 new-person:francesco-maggiotto-908b8d8efa；现裁决为 same → units/persons/francesco-maggiotto，复用既有人物卡 04-knowledge/units/persons/francesco-maggiotto.md，不新建重复 KU。第10章 p.325 与第13章 p.340 均以全名 Francesco Maggiotto 指称画家；第13章记其与 Maffeo Pinelli 的交往及 Doge 肖像等创作，第20章后记再以全名记至少六幅为 Pinelli 绘制的 Doge 肖像。既有人物卡已由图版68a的 Francesco Maggiotto 全名锚点、Treccani DBI《FEDELI, Francesco, detto il Maggiotto》及 Wikidata Q3080993 支持。Treccani 记其1738年生于威尼斯、1805年9月13日卒于威尼斯，并说明其 Maggiotto 别名来自画家父亲 Domenico。Getty ULAN 500125012 列 Francesco Maggiotto、Fedeli, Francesco、Magiotto/Majotto 等形式，记意大利画家/绘图者、威尼斯活动及父亲 Domenico；其总述日期1750–1805与 Treccani 不同，但所汇 RKD 传记项也有1738–1805。保留日期差异，不据此拆分身份。父亲仍由独立人物 KU units/persons/domenico-fedeli-venice-painter 表示。人物身份复用不合并 Doge 肖像作品候选 cand-10042、cand-3352、cand-4190；这些作品边界仍按各自 S3 待证说明处理。
- 涉及该候选的12条 S2 陈述中10条标为关系候选，留待 S6 逐条审查；没有新增正式关系或 S5 补足。

S4 当前已登记281组/352条成员映射，尚待登记4,551组/4,653条。


### S3 person：cand-2551 跨章复用毛罗·安东尼奥·泰西人物 KU（2026-10-16）

- 索引候选 cand-2551（T.csv#14，pp.358–360、409）原记为 new 组 new-person:mauro-tesi-4af80fb4b8；现裁决为 same，映射至已接收人物 KU units/persons/mauro-antonio-tesi，并并入其跨任务身份组 sg3-ku-units-persons-mauro-antonio-tesi。候选 `cand-3839` 已通过接受卡来源映射到同一 KU。第14章 pp.358–360 在 Algarotti 移居 Bologna、与建筑画家合作、Tesi 及其家人、Pisa 房间等不同语境中反复使用 Mauro Tesi；第20章后记 p.409 亦以全名称其为遗赠给 Elder Pitt 的两幅画的画家。既有人物卡规范名为 Mauro Antonio Tesi，Treccani DBI 的条目标题为“Mauro Antonio, detto Maurino”，记1730年生于 Montalbano、1766年卒于 Bologna，并记述他与 Algarotti 的交往和委托；意大利文化遗产总目录也以“Tesi Mauro (1730/1766)”列出作者规范记录，并关联作品目录。全名、年代、职业和 Algarotti 语境共同支持复用，不是仅凭姓氏或同词命中合并。原 `new` 组标签与“未匹配既有 KU”的初步说明在 alignment 行以 `previous_group_label` 留存；当前 `group` 指向既有 KU 组。本轮只裁决人物身份，不扩大为关系事实确认。
- 涉及该候选的9条直接 S2 陈述中9条标为关系候选，留待 S6；未新增正式关系或 S5 补足。临近对象分别保留去向：`cand-10392` 是独立的1787年书目/画册 archive 新组，待 S4；`cand-10400`、`cand-10401`、`cand-10402`、`cand-11522` 为未识别作品组，继续 undecided；`cand-10405` 仅有 Dietrich 姓氏，身份 undecided；`cand-10406` 未具名妻子、`cand-10407` 未具名女儿均保持 undecided，不推测身份；`cand-10408` 为未识别的比萨房间，继续 undecided。这些对象不因 Tesi 人物身份已对齐而自动并入同一 KU。

S4 当前已登记281组/352条成员映射，尚待登记4,550组/4,652条。


### S3 person：Augustus II of Poland 身份组复核（2026-10-16）

- `cand-0146`（A.csv#147，pp.266、278、294）与 `cand-0147`（A.csv#148，patronage of Venetian artists，p.294）继续组成 `new-person:augustus-ii-of-poland-e7b26d3f40`，决定保持 `new`，暂不写 `ku_id`，待 S4 登记。第10章 p.294 明称 Frederick Augustus I 为萨克森选帝侯、自1697年起为波兰国王 Augustus II ‘the Strong’；p.278 也用 Augustus the Strong 记其宫廷任用 Diziani。Deutsche Biographie 的GND 118505084 以 Friedrich August I 为标题，记1670–1733、萨克森选帝侯与波兰国王 Augustus II 身份，并列 August der Starke 等异名；Sächsische Biografie 亦以 Friedrich August I (August II, der Starke) 记其头衔与生卒年。索引子项 `cand-0147` 与同一索引主项和 p.294 语境对应，因此是同组的索引切分，不另立人物。全书尚无指向该人的同一 person KU。
- 边界核验：既有人物 KU `units/persons/augustus-iii-of-poland` 是 Augustus III / Frederick Augustus II。原书 p.294 明称 Augustus III 为 Augustus II 之子、并记其1733年继位；Deutsche Biographie 另有其子 Friedrich August II 的单独身份记录。父子头衔相邻但身份不同，Augustus II 组不并入 Augustus III 卡。本轮补入两个身份记录（GND 118505084、Sächsische Biografie）；未登记 KU、未新建关系，也未把外部生平事实注入知识卡。

涉及该组的10条直接 S2 陈述中9条为关系候选，均留待 S6；组成员继续待 S4 登记。当前 S4 已登记281组/352条成员映射，尚待登记4,550组/4,652条。


### S3 person：Cardinal Bernardino Spada 跨章身份组复核（2026-10-16）

- 索引候选 `cand-2493`（S.csv#182，pp.75、139）保持 `new-person:bernardino-spada-810d88ac92` 的独立 `new` 决定，KU 尚未登记。第3章 p.75 先以 Virgilio Spada 为主语，接着明确写“his brother Cardinal Bernardino”，并记 Bernardino 从 Mignanelli 手中购得 Farnese 宫附近的宫殿、曾于1627–1631年任博洛尼亚使节；第5章 p.139 再以 Cardinal Bernardino 指称曾任驻巴黎教廷使节、与法国阵营相关的红衣主教。该页关于《Masaniello 起义》的委托语气为“If it was actually painted”，不将可能委托写成确定事实。Treccani DBI（Benedetta Borello，vol.93，2018）以“SPADA, Bernardino”为标题，记其1594年出生、1626年获任枢机、曾任巴黎教廷使节及博洛尼亚使节（至1631年）、1661年去世，并明确记其兄弟 Virgilio。故本书 candidate `cand-2493` 对应 Cardinal Bernardino，与已存在的 `units/persons/virgilio-spada`（Virgilio Spada）是两个人；同姓和兄弟关系不构成合并理由。外部记录只附到 Bernardino 候选，不借用 Virgilio 的身份标识。
- 涉及该候选的11条直接 S2 陈述中9条为关系候选，留待 S6；未新增正式关系或 S5 补足。

S4 当前已登记281组/352条成员映射，尚待登记4,550组/4,652条。

### S3 person：Tommaso Giuseppe Farsetti 跨章身份组复核（2026-10-16）

- 索引候选 cand-1013（F.csv#28，pp.235n、362n、364）保持 new-person:farsetti-giuseppe-tommaso-339a4db213 的独立 new 决定，KU 尚未登记。第8章 p.235n 署名缩写“T. G. Farsetti”，经 Fogolari (1937), p.186 转引一段18世纪末对 Poggio 天花的描述；这是嵌套引文，未经独立核实，不据此确认天花身份、作者原文或引文内容。第14章 p.347n 称“T. G. Farsetti”写过献给 Bonomo 的短篇拉丁文 Algarotti 生平；这是书内归属，本轮不将其扩大为外部核验。第15章 p.362n 引用 Tommaso Giuseppe 1778年刊行的家族史，p.364 明载 Daniele 的兄弟 Tommaso Giuseppe (1720–91)，并提到其关于 Filippo 收藏的叙述。Treccani DBI（Paolo Preto, vol.45, 1995; https://www.treccani.it/enciclopedia/tommaso-giuseppe-farsetti_(Dizionario-Biografico)/）以“FARSETTI, Tommaso Giuseppe”立目，记其1720年4月16日生于威尼斯、1791年10月30日卒于帕多瓦，并列出《Notizie della famiglia Farsetti》(1778)为其著作；同条还称其堂亲 Filippo Vincenzo。全名、初始形式、年代和家族史著作共同支持这些跨章指称属于同一人物组。未发现同身份既有 person KU。既有 units/persons/filippo-farsetti 对应书中另一个Filippo Farsetti（第15章 p.302 记生于1703年；p.363称 Daniele 为 Filippo 的堂亲，p.364 则称 Tommaso 为 Daniele 的兄弟）；units/families/farsetti-family 是不同类型的家族对象。cand-10443 是独立 archive 新组 archive-group-ca70d9ac8f95，指向1778年家族史作品，待 S4；不把作品并入作者人物，也不借身份裁决解决作品内容或其他 claims。
- 该候选的11条直接 S2 陈述中9条为关系候选，留待 S6；未新增正式关系或 S5 补足。涉及亲属、赞助、著述、委托的语句仍按各自 S2 证据和类型保留，不由身份匹配自动升级为正式关系。

S4 当前已登记281组/352条成员映射，尚待登记4,550组/4,652条。

### S3 archive：Röthlisberger《Claude Lorrain—The Paintings》跨章身份组复核（2026-10-16）

- archive 候选 cand-4577 保持 archive-group-4f5f75670a57 的独立 new 决定，KU 待 S4。第2章引文引用1961年 p.153、p.121、p.67、p.127；第4章 p.118 注5引用 pp.428、433；第6章引用 p.374、p.369；第7章引用 vol.I pp.155–160 与 p.274；第21章书目列 Claude Lorrain—The Paintings, 2 vols., Yale and London 1961。候选实体为这部文献的书目/卷册身份，不是 Claude Lorrain 本人或其绘画作品。
- INHA AGORHA（https://agorha.inha.fr/ark:/54721/6ca774b1-afc0-47eb-ac34-561be13db605）以 Marcel Röthlisberger 为作者，列两卷本、New Haven、1961。Folger Shakespeare Library 目录（https://catalog.folger.edu/record/11636）区分 vol.1 “Critical catalogue” 与 vol.2 “Illustrations”，并将 vol.1 书目页标为551–558。书内所引页码均符合 vol.1的分页范围，且 p.274 明标卷I；因此当前候选的“vol. I locator”与同一两卷本出版物身份相容。未发现同类型 archive KU；已存在 units/persons/claude-lorrain 是艺术家人物卡，类型和对象均不同。未将其他 editions 或《Claude Lorrain: The Drawings》(1968) 并入。
- 涉及该候选的10条直接 S2 陈述中4条被标为关系候选，留待 S6；身份裁决不验证各引文页内容或相关作品断言。本轮只新增两条外部书目身份记录，无 KU、卡片、manifest 或正式关系变更。

S4 当前已登记281组/352条成员映射，尚待登记4,550组/4,652条。

### S3 event：S. Salvatore in Lauro 循环展览系列身份复核（2026-10-16）

- event 候选 cand-6051 保持 sg3-event-cand-6051 的独立 new 决定，KU 待 S4。第5章 p.128 以“one more regular art exhibition”引出 S. Salvatore in Lauro，说明 Marchigian 群体在12月10日庆祝 Loreto 圣屋迁来周年时举行画展，并叙述展品留置10–11日、借展安排与年度数量浮动。第8章 p.222 另记一幅 Velázquez 的 Juan de Pareja 肖像于1704年借展至同一地点。候选身份是循环系列，不与任一日期的单次展览同一化。
- 保留既有去向：cand-11770（1675）、cand-11771（1697）为该系列下各自独立的新 event；cand-11942（1701，同一地点）继续是独立 new event，因来源未证明它属于12月周年系列。cand-11783 的1708年“similar situation”未重述地点或系列，保持 undecided。另一系列 cand-6039（S. Giovanni Decollato）及其1675年实例 cand-11768 分别保留；place cand-6053（回廊）身份 undecided；term cand-0134 与 place cand-0720 分别保持各自类型，不并入事件。
- 该候选的12条直接 S2 陈述中5条为关系候选，留待 S6；本轮未新增外部身份行、KU、卡片或正式关系。S2 对1704借展的端点保持原记录，本轮不将其扩展为新的 event 候选。

S4 当前已登记281组/352条成员映射，尚待登记4,550组/4,652条。


### S3 institution：Papal States 跨章身份组裁决（2026-10-16）

- cand-1831（P.csv#30）、cand-1832（P.csv#31，sub-entry `increasing poverty`）、cand-1833（P.csv#32，sub-entry `wealth of in 1623`）统一进入 `sg3-institution-cand-1831`，均为同一项 new institution 候选组，待 S4 登记；没有拆成概念或重复实体 KU。cand-1832、cand-1833 的 `suggested_type` 从 `term` 改为 `institution`，历史类型与原裁决理由保存在相应 alignment 行的 `prior_resolution_note`。
- 跨章身份依据：第2章 pp.31–35 讨论 Papal States 的政治权力与收入；第5章涉及其领土/职务语境；第6章 pp.146、149、162 明确称 papal territory、Papal States、States of the Church；第8章 pp.203、224 再以该政治疆域定位 Bologna、Macerata 与 Raimondo。10条直接 S2 statement 中8条为关系候选，继续留待 S6；身份归组不裁定其内容或正式关系。
- cand-1832 的索引页码 p.149、p.162 与 S2 mentions `m-chp6-p149-045`、`m-chp6-p162-v-008` 指向同一政体；其余 locator 仅作为索引定位，不据此验证全部相关断言。cand-1833 的 mention `m-chp2-seciv-l114-125-0026` 明确将 Papal States 作为政治实体并区别于 Papacy；p.32 的财富/收入叙述也映射到 cand-1831。
- 外部身份核对：Treccani《Pontificio, Stato》，https://www.treccani.it/enciclopedia/stato-pontificio/，访问于2026-10-16；条目称 Stato della Chiesa 由教宗作为世俗主权者统治至1870年。该记录只支持历史政体身份及 institution 类型，不支持本书全部具体断言。manifest 中未发现同类型 Papal States KU。Rome 作为城市与 Holy See 候选 cand-4424 均分开保留；本轮不建立二者关系。
- 本次向 alignment 追加 Treccani 外部身份记录 aln-12617；无 KU/card/manifest/relations 写入。写回后 S3 为 same=1,766、new=5,005/4,830组、conflict=8、excluded=99、undecided=5,526；S4 已登记281组/352条成员映射，待登记4,549组/4,653条。

### S3 institution：威尼斯绘画与雕塑学院及 Remondini 跨章身份复核（2026-10-16）

- cand-0006（A.csv#5，p.331，`art exhibitions`）由 `undecided` 改为 `same`，映射至 `units/institutions/academy-of-painting-and-sculpture-venice`。索引子目挂在 Accademia di Pittura e Scultura 下；第10章 p.329 记该威尼斯学院于1756年成立，第10章 p.331 记其成员按年展示作品、学院借画补足数量，并将该 mention/statement 映射到 cand-0005。子目指学院参与的展览语境，不是另一家学院或独立展览事件。原 undecided 理由留在 alignment 行 `prior_resolution_note`。
- cand-2122（Q-R.csv#49，p.392）与 cand-2123（Q-R.csv#50，p.340）继续同属 `sg3-institution-remondini`，共同映射至 `units/institutions/remondini-firm`。第13章 p.340 将 Remondini 明确称为设于 Bassano、在 Venice 有分支的出版/印刷商行；同章记其出版图书、主要发行单张版画并雇用艺术家制作复制图像。第19章 p.392 记 Giovanni Volpato 1766年4月22日致出版者 Remondini 的信；第15章 p.367 注2另列 `Bassano [Remondini], 1787`。名称、出版职能、地点和时间语境支持同一商行候选。不是 Remondini 家族或未具名成员的身份裁决。原书所述关系和机构活动不由 S3 验证；相关 S2 关系候选仍待 S6。
- 本次不新增外部身份记录、KU、卡片、manifest 或正式关系。写回后 S3 为 same=1,767/1,026个KU、new=5,005/4,830组、conflict=8、excluded=99、undecided=5,525；S4 已登记281组/352条成员映射，待登记4,549组/4,653条。

### S3 archive：Pasquali《Beatae Mariae Virginis Officium》身份裁决（2026-10-16）

- cand-1849（P.csv#49，sub-entry `Beatae Mariae Virginis Officium`，p.337）由 `undecided` 改为 `new`，identity group 为 `archive-group-pasquali-officium-1740`，KU 尚待 S4。第13章 p.337 称 Pasquali 于1740年出版该插图宗教小书，并明确将它与其一般出版物区分；四条直接 S2 statements 记录其插图、出版、委托/资助及作者评价，后续关系判断仍由 S6 分别处理。
- 身份记录：OPAC SBN（Biblioteca Universitaria di Pisa），记录 PUVE008510，https://opac.bibliotecauniversitaria.pi.it/bid/PUVE008510，访问于2026-10-16。目录将题名 `Beatae Mariae Virginis officium` 著录为 printed monograph，出版项 Venetiis : Apud Jo. Baptistam Pasquali, 1740。它与原书索引题名、年份和出版者吻合；仅支持文献身份和版本定位，不证明委托、资助、作品质量或书内关系。
- 边界：与 cand-1848 `Dactylografa Smithiana`（另一出版物）、cand-1851 Goldoni 十七卷版及 cand-12144 未具名的 Pasquali 一般出版物集合分别处理；脚注引文 cand-10175 指向 Morazzoni p.116，并非 Officium 本身。3条关系候选留待 S6。本次只向 alignment 追加外部身份记录，不新建 KU/card/manifest/relations。
- 写回后 S3 为 same=1,767/1,026个KU、new=5,006/4,831组、conflict=8、excluded=99、undecided=5,524；S4 已登记281组/352条成员映射，待登记4,550组/4,654条。

### S3 archive：McSwiny《Tombeaux des Princes》索引候选并组（2026-10-16）

- `cand-1474`（M.csv#11，索引子项 `Tombeaux des Princes`，289n、290、291）从 `undecided` 改为 `new`，加入 `archive-group-25725e686a64`；该组已有正文候选 `cand-9032`，整体待 S4 登记一个 archive KU。索引只提供定位，决定依据是该索引候选的题名及页码与正文候选的同书身份锚点吻合：完整法文题名、1741 年出版信息、具体卷册描述及重叠页码。直接证据为 mentions `m-chp10-p291-published-volume-title`、`m-chp10-p289-note2-tombeaux`，以及 statements `st-chp10-p289-note2-1741-publication`、`st-chp10-p291-volume-publication-and-disappointment`、`st-chp10-p291-volume-plate-and-tomb-count`。
- 边界：`cand-9030` 是已发行、用于征订计划卷的小册子；`cand-9031` 是该小册子所述未实现的50幅铜版出版计划；`cand-9032` 是正文称1741年出版的实际卷册。1741卷与寓意墓葬画系列作品亦分别属于 archive 与 work。新增索引候选与正文候选同组，但仍按规则保留 `new` 决定，等待一个 KU 映射；未新增外部身份记录、KU、卡片或关系。
- 原 `undecided` 理由称缺少该候选自己的正文 mention；本轮利用正文候选及索引重叠页码解除身份定位缺口。仍不把 Haskell 对版数、内容、出版经过或关系的陈述视为独立外部核实。

### S3 archive：Maggiotto《Considerazioni elettriche》身份裁决（2026-10-16）

- `cand-1490`（M.csv#27，索引子项 `Considerazioni elettriche`，p.325n）从 `undecided` 改为 `new`，身份组 `archive-group-maggiotto-considerazioni-elettriche-1781`，待 S4 登记。正文 statement `st-chp10-p325-maggiotto-scientific-invention-and-treatise` 将论著归于 Francesco Maggiotto；脚注 statement `st-chp10-p325-n1-magggiotto-source-citations` 给出书名及 Biblioteca Correr, Venice, `Misc. 105113` 馆藏号。脚注未标年份和出版者，因此补查 Treccani DBI：Ettore Merkel, vol.45 (1995), https://www.treccani.it/enciclopedia/fedeli-francesco-detto-il-maggiotto_(Dizionario-Biografico)/，以 Francesco Fedeli, detto il Maggiotto 立目，并明确列《Considerazioni elettriche》为其1781年在威尼斯出版的小册子。标题、作者与索引/正文语境相合，支持新增一个 archive 身份组。
- 本轮只使用该外部记录确认书目身份和版本锚点，不据此验证电学装置发明叙述、Correr 当前馆藏状态或关系。明确区分脚注同列的 Tessier 1882 论文候选 `cand-9779`，也不把 Treccani 所列另两种1781年电学小册子合并进来。该候选的一条直接 S2 关系候选留待 S6；无 KU、卡片、关系写回。
- 外部身份对齐：Treccani DBI，Ettore Merkel，vol.45 (1995)，访问于2026-10-16；来源标识与身份范围见 `alignment.csv` 新增外部行。

### S3 archive：Malvasia《Felsina Pittrice》索引候选复用（2026-10-16）

- `cand-1502`（M.csv#39，p.189）从 `undecided` 改为 `same` → `units/archives/felsina-pittrice-1678-work`。索引 subentry 与第7章 p.189 同名，正文明确将 *Felsina Pittrice* 记为1678年作品；现有接收卡 `04-knowledge/04-knowledge/units/archives/felsina-pittrice-1678-work.md` 已记录该原文锚点，第7章 Markdown 行252–253。正文候选 `cand-6933` 已映射至同一 KU。由页码、题名、年代与既有卡证据可直接复用，不另建组。
- 版本边界：第21章 p.428 书目候选 `cand-11384` 指向 Bologna 1841 年两卷本，仍 undecided；索引 p.189 指向作品身份，不足以证明具体引用的是1841年印本，因此不把该版本并入本卡。此裁决未添加外部身份记录或新的 KU/card。

### S3 archive：Mancini《Considerazioni sulla Pittura》索引候选并组（2026-10-16）

- `cand-1508`（M.csv#45，pp.124、130）从 `undecided` 改为 `new`，与 `cand-6089` 同属 `archive-group-fb110b11a649`，作为一个待 S4 登记的 archive 身份组。第5章 p.120 注3 statement `st-chp5-p120-note3-mancini-locator` 引用 *Considerazioni sulla Pittura*, vol.I, p.249；同书第21章书目 statement `st-chp21-bib-l701-754-entry-27` 给出题名、Adriana Marucchi 首次刊行、Luigi Salerno 注释、两卷、Roma 1956；第5章 p.123 注4 亦称1956年批判版。版本、题名和卷页相互吻合，足以将索引候选并入正文/书目候选的 pending new 组。
- 第5章 p.124 泛称的“a learned and most valuable artistic Treatise”未具名，不单独建组或仅凭上下文判定它属于哪一具体版次。人物 `Giulio Mancini` 保持既有人物 KU；本轮无外部身份行、KU、卡片或正式关系写入。citation statement 仍留待 S6 审查关系类型与方向。

### S3 archive：Manfrin 致 Edwards 的 1793 年书信索引候选并组（2026-10-16）

- `cand-1515`（M.csv#52，索引子项为致 Pietro Edwards 的 gallery-formation letter，p.395）从 `undecided` 改为 `new`，与 `cand-10849` 同入 `archive-group-4ec5e3284567`，待 S4 登记一个 archive KU。第17章 p.380 注6 statement `st-chp17-p380-note6-edwards-letter-source` 将引文定位至 Biblioteca Correr 的 Epistolario Moschini，并指向本书附录7全文；第19章 p.395 statement `st-chp19-p395-manfrin-edwards-letter-source` 记录完整标题、Girolamo Manfrin 为寄件人、Pietro Edwards 为收件人、1793-12-03 日期和同一手稿系列定位。对具体信件，日期、当事人、议题、内部交叉引用与全篇转录构成充分身份锚点。
- 保持 `cand-10605` 为不同 archive 对象：Epistolario Moschini 手稿系列/档案集合，而非单封信；本轮不把 collection 当作 letter，也不从信件内容扩展关系。身份依据是 Haskell 在 Appendix 7 的全文转录与引用；原件未独立查阅。候选身份组和 S2 关系候选分开处理，未登记 KU、卡片或正式关系。

### S3 archive：Marino《Adone》文学作品身份裁决（2026-10-16）

- `cand-1549`（M.csv#88，p.115）从 `undecided` 改为 `new`，身份组 `archive-group-marino-adone-epic`，待 S4 登记。S2 mentions `m-chp4-sec-ii-p115-0032` 与 statements `st-chp4-sec-ii-p115-drawings-adone`、`st-chp4-sec-ii-p115-adone-created-by-marino` 共同指向 Marino 的具名文学作品《Adone》。未找到既有 archive KU。
- 类型按 literary work 登记为 archive。作品身份与 person `units/persons/giambattista-marino`、由该诗启发的 Poussin drawing candidates 及未具名诗作组 `cand-1551` 分开。原书没有指出本次引用的具体版次或单件；因此只登记作品身份候选，不主张印本、版本或藏本身份。

### S3 archive：Marino 未具名名画题咏诗组索引候选并组（2026-10-16）

- `cand-1551`（M.csv#90，p.38）从 `undecided` 改为 `new`，并入 `cand-4464` 的 `archive-group-c659964650de`。第2章 p.38 S2 mention `m-chp2-secii-l71-78-0065` 与 statement `st-chp2-secii-l71-78-marino-poems-and-pagan-qualities` 记录 Marino 写有“一系列非常流行的、题咏知名艺术家作品的诗”，题材描述、作者和页码均与索引子项一致，属于同一诗作群候选。
- 维持聚合粒度：没有单首诗的名字、出版物或版次，故不再拆分或推定具体作品。与同段另外的单首未具名 song `cand-4463`（献给 Marcello Sacchetti）及《Adone》`cand-1549` 分开。该组仍待 S4，不因作者相同合并其他作品。

### S3 archive：S. Andrea al Quirinale N. 865-13 索引候选并入档案组（2026-10-16）

- `cand-1532`（M.csv#69，pp.386–387）从 `undecided` 改为 `new`，与 `cand-5338` 同属 `archive-group-ff938f5595f2`。附录1 p.386 的 locator statement `st-chp19-p386-appendix-archive-locator` 明载关于 S. Andrea al Quirinale 的 Brandi、Maratta 祭坛画文件，地址为 Jesuit Archives, Fondo di Gesù—N.865-13；第3章 p.88 注2、注3 statements `st-chp3-seciv-notes-l205-243-p88-n2-86513` 与 `...-n3-86513` 复用同一 callmark 并分别指向 Appendix 1 中 Brandi 书信与 Maratta 相关材料。索引子项、档案编号和正文交叉引用共同表明这是一份档案项目/文件组的同一 identity group。
- `cand-11509` 是有关祭坛画的 work 候选，仍保持 undecided；N.865-13 文件组不等同于其中任一绘画，也不证明全部计划作品均已完成。档案原件没有独立查阅；本轮只裁决档案对象身份，不登记 KU、卡片或正式关系。

### S3 archive：Brienne《Mémoires》卷级引用与 Mazarin 两份清单身份裁决（2026-10-16）

- `cand-1596`（M.csv#135，Brienne 告别藏品的叙述，pp.185–186）由 `undecided` 改为 `new`；与卷 I 引用候选 `cand-7071`、卷 III 引用候选 `cand-7100` 统一进入 `archive-group-brienne-memoires-1916-1919`。p.185–186 逐字刊出 Brienne 的第一人称记述，注5定位 `Mémoires`, vol. III, pp.88–90；21章书目确认 Paul Bonnefon 编三卷本、Paris 1916–19。BnF Catalogue général FRBNF34019339（https://catalogue.bnf.fr/ark:/12148/cb340193395）记录同一三卷本、责任者与出版时间，足以确认卷 I 和卷 III 引文属于一个多卷出版物身份。原卷页未独立阅读；裁决不验证引文本身。这里把卷号视为组内 locator，不把不同实体卷册声称为同一物理册。
- `cand-6807`（d’Aumale 书目引文）由 `undecided` 改为 `new`，身份组 `archive-group-daumale-inventaire-1653-1861`；候选名称已规范为 Duc d’Aumale 的 *Inventaire de tous les meubles du Cardinal Mazarin*（London, 1861）。书目完整题名称该清单“dressé en 1653”且据 Condé 档案原件刊行；正文 p.183 注2、p.184 注2分别引该书 p.8 与 pp.293 ff.。BnF Catalogue général FRBNF30039849（https://catalogue.bnf.fr/ark:/12148/cb30039849q）确认作者、题名、Londres: Whittingham et Wilkins、1861，并记录所据 Condé 原件。组内对象是1861年刊本，不是底本清单。
- `cand-6814`（p.184 正文所称1653年编制的藏品清单）由 `undecided` 改为 `new`，与索引候选 `cand-1597`（M.csv#136，p.184 `inventory of collection`）同属 `archive-group-mazarin-inventory-1653`。S2 mention `m-chp7-p184-b-019`、statement `st-chp7-p184-i04` 锚定“An inventory was at once drawn up”；note 2 引 d’Aumale 的1653清单刊本。该身份是 Haskell 所述清单原件的候选身份，历史事实不因目录记录而全量核实。候选表 `cand-6814` 从“date unresolved”更新为1653报告性身份，旧未决说明和索引候选原裁决保留在本记录及 alignment 的 `prior_resolution_note`。
- 与上述1653清单区分：`cand-7091` 是注3所引 de Cosnac item 1240、明载1661年的独立清单，保留 `archive-group-fd76703203a6`。核对复合脚注映射后，注3对应1653至1661年间购藏的叙述；它不是正文“An inventory was at once drawn up”的日期证据。因此解决候选 `cand-6814` 原 alignment note 将注3说成“尚未迁移”导致的日期歧义。
- 本次将 Brienne 与 d’Aumale/清单组映射至 BnF 权威目录，只新增3条 `external_source=BnF Catalogue général` 身份记录；无现有 archive KU 可复用，未创建 KU/card/manifest/relations。Brienne 的引文内容及原始清单未独立查阅；所有相关 S2 关系候选仍由 S6 审查。身份组证据和变化分别回链至 alignment、p.184/185 statements 与本记录。

### S3 archive：d’Aumale 1861年清单刊本跨章候选归组（2026-10-16）

- 复核发现在第21章书目登记中已有 `cand-11231`，与第7章脚注出版物候选 `cand-6807` 都指向同一 d’Aumale 1861 年刊本。两者现同属 `archive-group-daumale-inventaire-1653-1861`，不重复登记第二个 KU；其来源锚点分别保留为第21章书目行和第7章注释定位。BnF FRBNF30039849 同时支持这两个候选的书目身份。
- 为遵守 `entity-candidates.csv` 非索引候选 `canonical_name + suggested_type` 自然键唯一约束，`cand-6807` 恢复原候选名“D'Aumale, cited publication; title and edition unspecified”；完整规范书名、书目字段和映射已写入其 detail 与 alignment 裁决。`cand-11231` 保留完整题名，二者的同一身份组在 alignment 中明确记录。
- 组数复核：三组更动的净效应为 Brienne 卷 I/III 两组并为一组（−1）、1653 清单与索引 locator 新增一组（+1）、d’Aumale 1861 刊本并入既有 cand-11231 组（0），故总 new 身份组由4,833保持4,833；new 候选增加4，S4 待登记映射增加4。

### S3 person：Mazarin 索引主项与子目复用（2026-10-16）

- `cand-1588`（M.csv#127，Mazarin, Cardinal）及 `cand-1589`–`cand-1593`（M.csv#128–132：and Poussin 两条、and Romanelli、and Sacchetti family、association with Barberini and Bentivoglio families）由 `undecided` 改为 `same`，全部映射至 `units/persons/mazarin`，共用 `sg3-ku-units-persons-mazarin`。主索引项与五个关系/主题子目都以 `Mazarin, Cardinal` 为父项，未产生另一个人物身份。
- 复用证据：接受卡 `04-knowledge/units/persons/mazarin.md` 已依图版标题、S2 全名/头衔及生卒等证据记录 Jules Mazarin；第7章 p.180–186 正文及其他索引页范围出现明确 `Cardinal Mazarin` 名称。主项跨多章的索引页码可由候选 `cand-1588` 的 mentions 回链；子项标题与父项共同保存索引定位。
- 原 alignment note 将主候选搁置于单名不足，但现有接收卡与原书全名/头衔锚点已解决实体身份。保留其余关联人物的独立 KU；索引并列只作语境定位，不裁决师承、交往、赞助或其他关系。本批没有新增 KU、卡片、外部记录或正式关系。

### S3 event / term：Mazarin 索引事件分组与“taste”去向（2026-10-16）

- `cand-1594`（M.csv#133，pp.176、177、181）由 `undecided` 改为 `new`，进入 `sg3-event-cand-1594`。S2 明确记载 Mazarin 于1644年初以高额薪俸劝 Bernini 定居法国；后页记录 Urban VIII 的干预，并概括早期招揽失败。该事件与第181页另一项请 Bernini 扩建 Tubeuf 宫殿的计划分开。无既有同一 event KU。
- `cand-1595`（M.csv#134，pp.182–183）由 `undecided` 改为 `new`，进入 `sg3-event-cand-1595`。1648年 Mazarin 亲自致函 Algardi、提出优厚条件以改变其先前拒绝，随后因教宗政策干预而取消法国合同；原文 p.182–183 与 statements `st-chp7-p182-i20/i21/i24` 对应。该事件与1644年 Bernini 招揽行动相隔数年且对象不同，不合并。
- `cand-1598`（M.csv#137，p.183）由 `undecided` 改为 `new`，与正文候选 `cand-6799` 并入 `sg3-event-cand-6799`。`st-chp7-p183-i13` 明记 First Fronde 于1649年猛烈反对 Mazarin，并导致其意大利艺术赞助暂时受挫；保留原书事件框架，不补标准化起止日期。
- `cand-1599`（M.csv#138，p.183）由 `undecided` 改为 `new`，进入 `sg3-event-cand-1599`，作为 Mazarin 购买 Bentivoglio 宫殿的交易。正文称“soon after 1644”，注2称确切日期不定但早于1647；不据注释推定确日。事件与 place 候选 `cand-6796` 分开。
- `cand-1600`（M.csv#139，pp.184–185，subentry `taste`）由 `undecided` 改为 `excluded`。索引词指向 Mazarin 的个人审美偏好及 Haskell 对 La Vrillière 的比较；现有 statements `st-chp7-p184-i07/i10/i11/i16` 以 claims 记录，不界定一个独立、可复用的 term identity。该内容留在 Mazarin 人物与书内断言脉络，不创建泛化的“taste” KU；未来只有出现独立概念界定时才重新立项。
- 决定计数：same=1,774，new=5,021（4,840组），conflict=8，excluded=100，undecided=5,501；S4 待登记4,559组、4,669条候选映射。未新建 KU、卡片或正式关系。


### S4 event/place：Mazarin 招揽、Fronde、购置事件与宫殿地点登记（2026-10-16）

- Event `sg3-event-cand-1594`（`cand-1594`）登记至 `units/events/mazarin-1644-bernini-recruitment-attempt`。第7章 p.176 L89 支持1644年初以金额未载的高额薪俸招揽 Bernini；p.177 L93 是 Haskell 的转述；p.181 L144 对早期招揽作总体回顾，不将总体失败结论强配给该单次行动。
- Event `sg3-event-cand-1595`（`cand-1595`）登记至 `units/events/mazarin-1648-algardi-recruitment-attempt`。p.182 L157–158 与 p.183 L161 记载1648年致函、优厚条件、教廷介入及取消法国合同的转引叙述；早先拒绝只保留“约六年前”，Passeri p.210 未独立查阅。
- Event `sg3-event-cand-6799` 的 `cand-6799` 与索引候选 `cand-1598` 一同映射至 `units/events/first-fronde-mazarin-patronage-setback-1649`。p.183 L165 支持1649年 First Fronde 转向反对 Mazarin 及其对意大利艺术赞助造成暂时挫折；保留 Haskell 的范围和评价，不扩写为完整政治事件史。
- Event `sg3-event-cand-1599`（`cand-1599`）登记至 `units/events/mazarin-bentivoglio-palace-purchase-before-1647`；place `sg3-place-cand-6796`（`cand-6796`）登记至 `units/places/mazarin-bentivoglio-palace-rome`。p.183 L162 与注2转录 L349 支持交易、Lante–Bentivoglio 转手脉络及确切日期不定但早于1647年的限定。购买事件与宫殿地点分开；place 标题注明为描述性工作名，不宣称官方宫名或现代地址。
- 五组登记共写入5张双语卡、`ku-manifest.csv` 5条和 alignment 6条候选映射，并将5条路径加入 `accepted.yml`。place 卡保留原书关于赌场 Aurora 壁画的叙述，但相关 work 候选仍 undecided，不建立对象边；Mazarin—Bernini、Mazarin—Algardi、Fronde—Mazarin、所有权及建筑用途等正式边仍待 S6。未新增 `relations.csv`、S5 字段或外部身份。
- 字段表写入使用 `build_field_facts.py` 的只读预检与 apply；`sources.csv` 同步补登记15条已被既有 KU 引用、此前缺少目录行的来源记录，不包含本批新增外部采集。
- S4 计数：新增登记5组/6条映射；累计286组/358条映射，待登记4,554组/4,663条映射；KU 总数1,305。


### S4 event follow-up：跨章 Sasso 1803 年拍卖组（2026-10-16）

- S3 既有组 `sg3-event-cand-10715` 含 `cand-10715`（ch.17:17_CHP-17_sec_ii:L7–17）与后并入的 `cand-11549`（ch.16:16_CHP-16_intro:L16–22）；两项均为同一场1803年 Sasso 藏品拍卖。按该组登记1张 event KU `units/events/sasso-personal-collection-auction-1803`，两个成员候选均映射至该卡。
- p.374 L22 支持 Sasso 为自己汇集的收藏在其去世后于1803年拍卖及藏品举例；p.382 L16–17 注4称 Correr 几乎可以肯定在该场拍卖购得 Zocchi 的 Zanetti 与 Marchese Gerini 双人肖像。后者精确链接至既有 `units/works/giuseppe-zocchi-a-m-zanetti-the-elder-with-marchese-gerini`，人物入口链接至既有 Sasso、Teodoro Correr KU；未把 S3 尚待身份裁决的 Gerini 人物候选强行合并。
- Haskell 分别引述第16章的藏品叙述与第17章注4的购买判断；注4所引 sale catalogue 与 1960 年 *Bollettino dei Musei Civici Veneziani* 文章未独立查阅。卡片保留“几乎可以肯定”，不宣称已核实交易，不新增 `relations.csv` 正式边；相关购入与参与者边留待 S6。
- 新增1张 event 卡、`ku-manifest.csv` 1条、alignment 2条成员映射及 `accepted.yml` 1条路径；字段行随后通过 `build_field_facts.py` 预检与 apply 登记。S4 累计287组/360条映射，待登记4,553组/4,661条映射；event 为15组已登记、216组/218条成员待登记；KU 总数1,306。


### S4 event follow-up：跨章 Rospigliosi 1667 年即位组（2026-10-16）

- S3 组 `sg3-event-clement-ix-accession-1667` 由 `cand-4813`（ch.2:02_CHP-2_sec_iv:L181–188）与 `cand-6482`（ch.6:06_CHP-6_sec_v:L3–12）组成；同一人物、即位称号及1667年均相符，登记为单一 event KU `units/events/giulio-rospigliosi-accession-clement-ix-1667`。
- 第2章 p.58 L182 称 Rospigliosi 于1667年成为 Pope Clement IX；第6章 p.161 L3 重述1667年即位并称仅在位两年。第6章 OCR 将 `Clement IX` 与后词 `in` 连写为 `Clement IXin`；卡片原始摘录保留原貌，转述不照搬该 OCR 拼接。两段均不支持确定终止日期。
- 复用既有 Giulio Rospigliosi 人物 KU，不新建同名人物。新卡登记两个候选成员，未新增 `relations.csv`；即位者与事件的正式参与边留待 S6。
- 新增1张 event 卡、`ku-manifest.csv` 1条、alignment 2条成员映射及 `accepted.yml` 1条路径；字段行随后通过 `build_field_facts.py` 预检与 apply 登记。S4 累计288组/362条映射，待登记4,552组/4,659条映射；event 为16组已登记、215组/216条成员待登记；KU 总数1,307。


### S4 event follow-up：Innocent X 葬礼费用争议组（2026-10-16）

- S3 将索引候选 `cand-1821`（P.csv#20，父项 Pamfili, Gianbattista / Pope Innocent X；子目 `dispute over burial of`，p.150）与正文候选 `cand-6297`（ch.6:06_CHP-6_sec_i:L48–57）并入 `sg3-event-cand-6297`。子目指向事件而非父项人物；两候选共同登记为 `units/events/innocent-x-burial-expense-dispute-1655`。
- p.150 L56 记 Donna Olimpia 与 Prince Camillo Pamfili 拒付 Innocent X 的棺木费用，并争论安葬费用应由谁承担；原文还以地窖中的遗体作叙述。卡片将此保留为 Haskell 的报告。注5引 Pastor, XIV, p.37，该页未独立查阅；不推断最终付款者或事件解决结果。人物端点复用既有 KU，未新增 `relations.csv`。
- 新增1张 event 卡、`ku-manifest.csv` 1条、alignment 2条成员映射及 `accepted.yml` 1条路径；字段行随后通过 `build_field_facts.py` 预检与 apply 登记。S4 累计289组/364条映射，待登记4,551组/4,657条映射；event 为17组已登记、214组/214条成员待登记；KU 总数1,308。


### S4 archive：Bologna《Francesco Solimena》跨章身份组（2026-10-16）

- S3组 `archive-group-bologna-francesco-solimena-1958` 包含 `cand-7348` 与 `cand-7759`。前者由第7章p.200注4、第8章p.204/p.208/p.212–214引注及第21章p.416书目锚定；后者是第8章p.224的“Bologna (Plate 209)”。p.416书目列Ferdinando Bologna、*Francesco Solimena*、Napoli 1958；Haskell本书的图版目录把Dido图像列为Plate 33a，p.224的209因此指被引书图版号。该身份决定和映射见alignment对应行。
- 两个候选共同登记为 `units/archives/ferdinando-bologna-francesco-solimena-1958`。正文注释所引Bologna pp.191、20均未独立查阅，Bologna原书、其版本/出版者和p.224所述复制品均未外核；书目条未列出版者。`cand-7760`复制品work、`cand-7761` Scholz-Forni collection（类型仍待决）保持独立，不由此新增KU或正式关系。
- 新增1张archive卡、`ku-manifest.csv` 1条、alignment 2条候选映射及`accepted.yml` 1条路径；卡片直接引用本书图版目录（S5）区分Plate 33a与被引书Plate 209。5条字段行经 `build_field_facts.py` 预检与apply登记，图版行的S5证据已补齐。S4累计290组/366条映射，待登记4,550组/4,655条映射；archive为30组已登记、1,191组/1,221条成员待登记；KU总数1,309。


### S4 archive：Morazzoni《Il libro illustrato veneziano del Settecento》跨章身份组（2026-10-16）

- S3组 `archive-group-morazzoni-book-1943` 包含 `cand-10137`、`cand-10140`、`cand-10143`、`cand-10162`、`cand-10175`：`cand-10137` 为第13章无页码引注及第21章书目身份；其余四项分别是第13章p.332注5、p.334注2、p.336注7、p.337注5的pp.70、131、117、116定位。第13章p.336注3另有无标题、无页码的Morazzoni短引，对应同一候选。第21章p.430书目明确列G. Morazzoni, *Il libro illustrato veneziano del Settecento*, Milano 1943。
- 五个候选共同登记为 `units/archives/morazzoni-illustrated-book-venice-1943`。未扩展G.的名字，未补出版者；原书及所引各页均未独立查阅。仍未具书名的其他Morazzoni引文保持独立，不并入本组。未新增 `relations.csv`。
- 新增1张archive卡、`ku-manifest.csv` 1条、alignment 5条候选映射及`accepted.yml` 1条路径；字段行经 `build_field_facts.py` 预检与apply登记。S4累计291组/371条映射，待登记4,549组/4,650条映射；archive为31组已登记、1,190组/1,216条成员待登记；KU总数1,310。


### S4 archive：Zanetti《Della Pittura Veneziana》1771年版身份组（2026-10-16）

- S3组 `archive-group-zanetti-della-pittura-veneziana-1771` 包含索引候选 `cand-2855`（UVWXYZ.csv#192，p.345）与正文／书目候选 `cand-9837`。第10章p.329注1引该书序言p.xiii；第13章p.345称这是A. M. Zanetti the Younger自己的1771年著作；第21章p.441书目列 `Zanetti, AM.: Della Pittura Veneziana, Venezia 1771.`。
- 两候选共同登记为 `units/archives/zanetti-della-pittura-veneziana-1771`。正文语境将该书归于younger Zanetti；既有人物卡 `a-m-zanetti-the-elder` 明确对应长者，不把二人合并。作者全名未展开，出版者未载，序言及原书未独立查阅。
- 新增1张archive卡、`ku-manifest.csv` 1条、alignment 2条候选映射及`accepted.yml` 1条路径；字段行经 `build_field_facts.py` 预检与apply登记。S4累计292组/373条映射，待登记4,548组/4,648条映射；archive为32组已登记、1,189组/1,214条成员待登记；KU总数1,311。


### S4 archive：Bibliotheca Smithiana 1755年藏书目录身份组（2026-10-16）

- S3组 `archive-group-bibliotheca-smithiana-1755` 包含索引子目 `cand-2450`（S.csv#139，pp.310、394）和正文候选 `cand-9274`。第10章p.310称Joseph Smith于1755年出版其藏书目录，题为 *Bibliotheca Smithiana*；Haskell认为它“几乎可以肯定”被设计为精心制作的售书目录，此性质保留为作者推断。第19章附录5 p.394记该目录所列藏书于1762年出售给George III，并称目录由Pasquali于1755年出版。
- 两候选共同登记为 `units/archives/bibliotheca-smithiana-1755`。与1771年 *Catalogo di Libri Raccolti...*（`cand-2452`/`cand-10832`）及1773年 *Bibliotheca Smithiana, pars altera*（`cand-2451`/`cand-10833`）严格区分；它们均保留各自S3组。原目录及其存世本未独立查阅。Joseph Smith与George III之间关于目录所涉藏书的正式关系留待S6，本轮未新增 `relations.csv`。
- 新增1张archive卡、`ku-manifest.csv` 1条、alignment 2条候选映射及`accepted.yml` 1条路径；字段行经 `build_field_facts.py` 预检与apply登记。S4累计293组/375条映射，待登记4,547组/4,646条映射；archive为33组已登记、1,188组/1,212条成员待登记；KU总数1,312。


### S4 archive：Sasso《Osservazioni sopra i lavori di niello》1856年版身份组（2026-10-16）

- S3组 `archive-group-sasso-osservazioni-niello-1856` 包含索引子目 `cand-2366`（S.csv#54，p.373注）和书目/引注候选 `cand-10601`。第16章p.373注1记Cicogna于1856年编订Sasso此书，OCR写作 `A niello`；第21章p.436书目列 `Sasso, G. M.: Osservazioni sopra i lavori di niello`，并列E. Cicogna及Venezia 1856，故本卡按书目题名录入并保留注释OCR原文。两处均未证明原书或被引页已独立查阅。
- 两候选共同登记为 `units/archives/sasso-osservazioni-niello-1856`。虽有既有人物卡G. M. Sasso，本组只解决archive出版物身份，未据相同首字母建立人物 `same` 映射或正式作者边；关系端点如需确认，留待S6核对。原书未独立查阅。
- 新增1张archive卡、`ku-manifest.csv` 1条、alignment 2条候选映射及`accepted.yml` 1条路径；字段行经 `build_field_facts.py` 预检与apply登记。S4累计294组/377条映射，待登记4,546组/4,644条映射；archive为34组已登记、1,187组/1,210条成员待登记；KU总数1,313。


### S4 archive：Shaftesbury《Second Characters》Rand编1914年版身份组（2026-10-16）

- S3组 `archive-group-shaftesbury-second-characters-1914` 包含索引候选 `cand-2431`（S.csv#119，p.142n）和书目候选 `cand-11434`。第5章p.142注6引 *Second Characters*, p.15；第21章p.437书目列 *Second Characters or The Language of Forms*、Shaftesbury第三伯爵、Benjamin Rand编、Cambridge 1914。S2依据图像核对记录OCR末尾多出的撇号并非印刷内容。
- 两个archive候选共同登记为 `units/archives/shaftesbury-second-characters-rand-1914`。正文S2另有work类型候选 `cand-6220`，表示作品身份而非1914年编订出版版；本轮不合并，也不推定该 edition 与 work 的具体版本关系。原著、版本及被引页未独立查阅。
- 新增1张archive卡、`ku-manifest.csv` 1条、alignment 2条候选映射及`accepted.yml` 1条路径；字段行经 `build_field_facts.py` 预检与apply登记。S4累计295组/379条映射，待登记4,545组/4,642条映射；archive为35组已登记、1,186组/1,208条成员待登记；KU总数1,314。


### S4 archive：Vianello 1793年刊行的Carriera日记版本身份组（2026-10-16）

- S3组 `archive-group-vianello-carriera-journal-1793` 包含索引候选 `cand-2766`（UVWXYZ.csv#102，p.376）与正文候选 `cand-10631`。第16章p.376称Vianello于1793年刊行Rosalba的journal。原文限定了年份与刊行行为，但没有题名、出版地、出版者、格式或具体存世版本。
- 两个候选共同登记为 `units/archives/carriera-journal-vianello-1793`，卡片题名为标明缺口的描述性工作名。没有补造原刊题名、手稿身份或edition关系；相关关系留待S6。原刊未独立查阅。
- 新增1张archive卡、`ku-manifest.csv` 1条、alignment 2条候选映射及`accepted.yml` 1条路径；字段行经 `build_field_facts.py` 预检与apply登记。S4累计296组/381条映射，待登记4,544组/4,640条映射；archive为36组已登记、1,185组/1,206条成员待登记；KU总数1,315。


### S3 分组校正与 S4 archive 登记：Gallacini《Trattato》1767年刊本（2026-10-16）

- 对比 `cand-1110`（G.csv#17；索引子目“Trattato sopragli errori degli architetti, 309”）与 `cand-9257`（第10章p.309正文候选）。索引子目指向正文所在页，正文按S2页图读法记载Smith于1767年刊行Gallacini手稿并给出同一题名；这是同一书目身份的索引／正文双锚点。将两行从原组 `archive-group-db9bd962571d`、`archive-group-8924556dfa3f` 统一到 `archive-group-gallacini-trattato-1767`，保留 `decision=new`。原稿作为出版来源，不作为未识别的独立手稿KU。
- `cand-9258` 的Visentini更新版保留 `archive-group-13318baef7cf`，不与1767年刊本合并；来源未给出更新版精确题名、出版项。
- S4新增 `units/archives/trattato-sopra-gli-errori-degli-architetti-1767`，记录原题、书内作者归属及1767刊行叙述，并分别保留正文与索引证据。未独立查阅原刊；不新增正式关系。
- 新增1张archive卡、manifest 1条、alignment 2条KU映射、accepted 1条路径。S3 new身份组净减1，候选决议数不变；S4累计297组/383条映射，待登记4,542组/4,638条映射；archive为37组已登记、1,183组/1,204条成员待登记；KU总数1,316。字段表经 `build_field_facts.py` 预检及apply写回。


### S4 archive：McSwiny《To the Ladies and Gentlemen of Taste》征订小册子（2026-10-16）

- 依现有S3组 `archive-group-mcswiny-ladies-gentlemen-pamphlet` 登记 `cand-1473` 与 `cand-9030`。索引子目指向第288页注1；第10章正文p.290与注1 p.288均识别同一小册子。正文给出“1730年代某时”的约略刊行时间，注释称小册子无日期；一条是刊行时间概述，一条是册上日期说明，不提升为精确年份。
- 新KU `units/archives/mcswiny-ladies-gentlemen-taste-pamphlet` 记录邀请订阅的已发行小册子。Haskell所述计划卷册 `cand-9031` 与1741年实际出版物 `cand-9032` 均不并入；p.291报告实际卷为18幅而征订计划为50幅。British Museum藏本仅保留为Haskell写作时的报告，不视为当前馆藏核验。
- 新增1张archive卡、manifest 1条、alignment 2条候选映射及accepted 1条路径。没有新增正式关系；出版社身份和来源时间馆藏陈述留待S6。字段行经 `build_field_facts.py` 预检与apply登记。S4累计298组/385条映射，待登记4,541组/4,636条映射；archive为38组已登记、1,182组/1,202条成员待登记；KU总数1,317。


### S4 archive：McSwiny《Tombeaux des Princes》1741年出版卷册（2026-10-16）

- 按S3组 `archive-group-25725e686a64` 登记 `cand-1474` 与 `cand-9032`。索引短题名 `Tombeaux des Princes` 指向p.289注、p.290–291；第291页正文给出完整法文题名、1741年刊行说明及卷册版数，足以将索引候选映射到正文同一刊物。S2页图已校读末词为 `siècle`，Markdown OCR不含重音。
- Haskell报告18幅版画、其中9幅寓意墓葬图被刻印；p.289注2称McSwiny刊出了九幅方案图并转述归属Richmond公爵的说法，同时提醒购藏史混乱。未独立查阅原刊或核验归属。征订小册子 `cand-9030`、未实现为50幅出版规格的计划候选 `cand-9031`、墓葬画作系列均保留各自边界。
- 新增 `units/archives/tombeaux-des-princes-mcswiny-1741`、manifest 1条、alignment 2条候选映射和accepted 1条路径；未新增正式关系。S4累计299组/387条映射，待登记4,540组/4,634条映射；archive为39组已登记、1,181组/1,200条成员待登记；KU总数1,318。字段行经 `build_field_facts.py` 预检与apply登记。


### S4 archive：Francesco Maggiotto《Considerazioni elettriche》1781年小册子（2026-10-16）

- S3组 `archive-group-maggiotto-considerazioni-elettriche-1781` 仅含 `cand-1490`（M.csv#27，索引子目 *Considerazioni elettriche*，p.325n）。第10章p.325以Francesco Maggiotto为主语称其写有关于电学机器的论著；注1列同题名及Correr定位“Misc: 105113”，并称Haskell所引本未标日期或出版者；索引子目指向同一脚注。
- S3外部身份行 `aln-12619` 已记 Treccani DBI（Ettore Merkel, vol.45, 1995）；该条目将 *Considerazioni elettriche* 列为Maggiotto名下、威尼斯1781年出版的印刷小册子。它补足题名、作者、出版地与年份的书目身份，不能证明Haskell所引Correr副本的具体版本或当前馆藏，亦不核验其机器发明叙述。未给出版者、版次；中文题名《电学考论》为项目暂译。1882年Tessier文章 `cand-9779` 是独立书目对象；Treccani列出的另外两种1781年小册子不并入本组。
- 新增 `units/archives/considerazioni-elettriche-1781` 卡、manifest 1条、`cand-1490` 映射和accepted路径。既有人物卡与Correr图书馆卡仅作内容入口；本轮不新增正式作者或馆藏关系，均留待S6。字段行经 `build_field_facts.py` 预检与apply登记。S4累计300组/388条映射，待登记4,539组/4,633条映射；archive为40组已登记、1,180组/1,199条成员待登记；KU总数1,319。


### S4 archive：*Beatae Mariae Virginis Officium* 1740年刊本（2026-10-16）

- S3组 archive-group-pasquali-officium-1740 仅有 cand-1849（P.csv#49，索引子目 Beatae Mariae Virginis Officium，p.337）。第13章p.337正文直接给出题名与1740年刊行年份；书末索引在Pasquali名下列出题名和p.337。
- S3外部身份行 aln-12618 记录OPAC SBN（Biblioteca Universitaria di Pisa），record PUVE008510。目录将该题名著录为printed monograph，出版项为Venetiis: Apud Jo. Baptistam Pasquali, 1740。它支持题名、出版地、出版者和年份的书目身份；本轮仅登记edition层级，不把目录的具体馆藏副本、插图者、engraver或印数资料扩展为本KU事实。
- Haskell关于Piazzetta提供插图、商人Caime委托及资助、该书艺术评价等书内叙述仍各待关系/证据阶段核验；本轮未新增正式关系。与 cand-1848 Dactylografa Smithiana、cand-1851 Goldoni edition及 cand-12144 一般出版物集合分开。
- 新增 units/archives/beatae-mariae-virginis-officium-1740 卡、manifest 1条、cand-1849 映射和accepted路径。S4累计301组/389条映射，待登记4,538组/4,632条映射；archive为41组已登记、1,179组/1,198条成员待登记；KU总数1,320。字段行经 build_field_facts.py 预检与apply登记；OPAC来源由字段表生成过程加入sources.csv，未重复其他已登记来源。


### S3 archive：Brienne《Mémoires》书目候选并入三卷本身份组（2026-10-16）

- `cand-11265`（第21章书目候选，`st-chp21-bib-l243-293-entry-07`）原因未决而与卷级候选分开。复核书目原文：`Brienne, Louis-Henri de Loménie Comte de: Mémoires, publiés par Paul Bonnefon, 3 vols., Paris 1916-19.`。该条目给出完整三卷版身份，与`cand-7071`（卷I locator）、`cand-7100`（卷III locator）相合；BnF FRBNF34019339为这组候选提供同一三卷版目录身份依据。
- `cand-11265`现裁为`new`并进入`archive-group-brienne-memoires-1916-1919`，与`cand-1596`、`cand-7071`、`cand-7100`共用一个archive身份组；不是第四种出版物，也不把卷册等同为同一物理对象。旧的‘与卷级候选区分、等待S3’说明保留在alignment的`prior_resolution_note`及本记录；回忆录卷内页未独立查阅。
- 本次改变1条既有候选决定；new候选总数增至5,022，身份组数仍为4,839，undecided降至5,500。S4待登记组仍为4,538，成员候选映射增至4,633；未创建KU、卡片或关系。


### S4 archive：Brienne《Mémoires》1916–1919年三卷本（2026-10-16）

- S3身份组 `archive-group-brienne-memoires-1916-1919` 包含 `cand-11265`（第21章完整书目条目）、`cand-1596`（M.csv#135，索引子目告别藏品，pp.185–186）、`cand-7071`（第7章第181页注2，Brienne, I, p.315）和 `cand-7100`（第7章第185页注5，OCR作Brienne, IH, pp.88–90）。21章书目列Louis-Henri de Loménie Comte de Brienne、Paul Bonnefon编、3 vols.、Paris 1916–19；BnF FRBNF34019339记录同一三卷本。
- 三条候选共同登记至 `units/archives/brienne-memoires-1916-1919`。卷I和卷III是多卷出版物内部的locator，不是同一实体卷册；索引页码是Haskell书内定位。S3以书目及BnF身份将OCR `IH` 解释为III。没有对回忆录原卷的引文页或内容作独立查验，目录记录只支持出版物身份。
- 既有人物卡 `units/persons/lomenie-de-brienne` 仍与文献KU分立；作者与编者仅按书目责任字段列出，正式关系留待S6。没有新增relations.csv边。
- Paul Bonnefon由第21章书目记为编者；backlog bl-0003 后续已按S1→S3→S4处理，候选 cand-12427 映射至 units/persons/paul-bonnefon，端点登记完成。正式编辑关系仍待S6。
- 新增archive卡、manifest 1条、alignment 4条候选映射、accepted路径及1条person端点待办；`build_field_facts.py` dry-run无警告，apply登记8条source-backed字段事实并新增1条BnF来源记录，unverified数不变。S4累计302组/393条映射，待登记4,537组/4,629条映射；archive为42组已登记、1,178组/1,195条成员待登记；KU总数1,321。


### S3 person：d’Aumale, duc 对齐至 Henri d’Orléans（2026-10-16）

- `cand-7090`（第7章注2所引 `d’Aumale, p.8`，候选源行L355）原为undecided，原因是来源只给头衔形式且无S2人物提及。BnF Catalogue général的人物权威记录FRBNF12375307将该作者形式识别为Henri d’Orléans, duc d’Aumale（1822–1897）；第21章书目把同一责任形式用于1861年《Inventaire de tous les meubles du Cardinal Mazarin》。
- 现裁为`new`，身份组`person-group-henri-dorleans-duc-aumale-1822-1897`，待S4登记为独立人物KU；不是既有其他Henri d’Orléans候选或奥尔良家族KU。原undecided理由写入alignment的`prior_resolution_note`。身份记录只支持规范名、头衔和生卒年，不扩写传记；他与1861年刊本的正式作者关系留待S6。
- 新增外部身份行`aln-12623`（BnF FRBNF12375307）。候选决定new增至5,023个、4,840组，undecided降至5,499；S4待登记4,538组、4,630条成员候选；未创建KU或关系。


### S4 person：Henri d’Orléans, duc d’Aumale（1822–1897）（2026-10-16）

- S3组 `person-group-henri-dorleans-duc-aumale-1822-1897` 仅含 `cand-7090`，来源形式为Haskell第7章注释的`d’Aumale`及第21章书目的`d’Aumale, duc`。BnF人物权威记录FRBNF12375307确认其为Henri d’Orléans, duc d’Aumale，1822–1897。
- 新增 `units/persons/henri-dorleans-duc-aumale` 卡和manifest/accepted记录；该人物与1861年马萨林清单刊本的责任关系仍待S6审查，不创建正式边。未添加额外生平信息。
- `build_field_facts.py` dry-run无警告，apply登记4条source-backed字段事实并新增1条BnF人物权威来源记录，unverified数不变；S4累计303组/394条映射，待登记4,537组/4,629条映射；person为89组已登记、995组/1,040条成员待登记；KU总数1,322。


### S4 archive：d’Aumale《Inventaire de tous les meubles du Cardinal Mazarin》1861年刊本（2026-10-16）

- S3组 `archive-group-daumale-inventaire-1653-1861` 包含 `cand-6807`（第7章第183页注2及第184页注2引文候选）和 `cand-11231`（第21章书目候选）。二者指向同一1861年刊本；BnF身份行 `aln-12620` / FRBNF30039849支持规范题名与Londres: Whittingham et Wilkins, 1861。
- 第21章书目OCR题名作 `tneubles`，照录于source quote；卡片按BnF规范题名 *meubles* 登记并保留OCR异文。Haskell还称该刊本为1653年编制、据Condé档案原件刊行；原件未独立查阅，刊本与原件分立。
- `cand-7090` 已在独立person组映射至 `units/persons/henri-dorleans-duc-aumale`；BnF FRBNF12375307将d’Aumale, duc识别为Henri d’Orléans（1822–1897）。作者关系仍待S6，不新增正式边。
- 新增archive卡、manifest 1条、alignment 2条候选映射和accepted路径。`build_field_facts.py` dry-run无警告，apply登记6条source-backed字段事实并新增1条BnF刊本来源记录，unverified数不变。S4累计304组/396条映射，待登记4,536组/4,627条映射；archive为43组已登记、1,177组/1,193条成员待登记；KU总数1,323。


### S4 archive：马萨林1653年清单原件（2026-10-16）

- S3组 `archive-group-mazarin-inventory-1653` 包含正文候选 `cand-6814` 与索引定位候选 `cand-1597`。正文statement `st-chp7-p184-i04` 锚定“An inventory was at once drawn up”；索引子目 `M.csv#136` 的 `inventory of collection` 指向同页。注2与第21章书目指向d’Aumale 1861年刊本，BnF FRBNF30039849说明该刊本据Condé原件刊行；S3外部身份行 `aln-12621` 记录目录身份比较。
- 两候选共同登记为1653年原件KU `units/archives/mazarin-inventory-manuscript-1653`，与1861年印刷刊本 `units/archives/daumale-inventaire-mazarin-1861` 分开。第7章注3另引1661年清单 `cand-7091`，不与本组合并。Haskell所引pp.293 ff.及原件均未独立查阅；“用于估量收藏与赞助”保留为Haskell叙述，不写成独立核实的历史事实。
- 卡片不创建正式作者、所有权或版本关系；原书关系候选继续留在S2断言表，1861年刊本与原件的正式关系留待S6。新增archive卡、manifest 1条、2条候选映射和accepted路径；`build_field_facts.py`预检并登记6条source-backed字段记录，unverified数不变；BnF来源已在sources.csv登记，未重复添加。


### S3 person：Podestà 跨章身份归组（2026-10-16）

- `cand-5558`（第4章p.97正文Andrea Podesta及p.105跨行Andrea / Podesta）与 `cand-1964`（P.csv#165，索引页码97、105、184n）归入同一身份组 `new-person:andrea-podesta-070b483a9a`。第7章p.184注3的 `st-chp7-p184-n3-podesta-inventory` 使用完整形式Giovanni Andrea Podesta，并映射到 `cand-5558` 与1661年清单候选 `cand-7091`。
- Getty ULAN 500021868 的规范名为Podesta, Giovanni Andrea，别名含Podestà, Andrea；卢浮宫艺术家权威记录的规范名为PODESTA Giovanni Andrea，同义名含Podesta Andrea。索引候选原裁决 `undecided` 的理由为缺少映射S2正文提及；本次依据索引页码与第4章显名正文锚点、跨章全名表述和两条机构权威身份记录改为 `new`，指向既有new组。原未决理由保留在alignment `prior_resolution_note`。
- 此身份裁决不验证Haskell关于Podesta参与编制1661年清单的转述；de Cosnac item 1240与底层清单未独立查阅。该人物组尚未登记为KU；其与清单的可能关系留待关系阶段审查，不新增正式边。候选决定new增加1而new组数不变；未决减少1，S4待登记候选映射增加1。

### S4 person：Giovanni Andrea Podesta new-person:andrea-podesta-070b483a9a（2026-10-16）

- `cand-5558`与`cand-1964`共同映射至`units/persons/giovanni-andrea-podesta`，索引及正文候选仍保留各自来源定位。人物卡以第7章p.184注3的全名为规范名，采用第4章p.97和p.105的姓名变体；中文名为工作音译。
- Getty ULAN 500021868及卢浮宫图像艺术部权威记录支持姓名变体与职业识别。二者日期摘要不同，故未录生卒年。Haskell关于1661年清单及Mazarin联系的叙述仅作为有来源归属的书内说法；de Cosnac item 1240、原清单和Blunt文章未独立查阅。
- 卡片保留双语描述、书内来源定位和两条外部身份链接；涉及该人物的5条S2陈述中，4条关系候选仍待S6逐条核查。本轮不新增正式关系边。S4累计306组/400条映射，待登记4,534组/4,624条映射；person为90组已登记、994组/1,039条成员待登记；KU总数1,325。`build_field_facts.py`预检无警告，登记7条source-backed字段事实及2条Getty／卢浮宫来源记录，未核验字段数保持1,578。


### S4 person：Gabriel-Jules de Cosnac new-person:comte-cosnac-de-gabriel-jules-5d54b2a724（2026-10-16）

- `cand-7086`登记至`units/persons/gabriel-jules-de-cosnac`。Haskell书目p.420将Comte Gabriel-Jules de Cosnac列为 *Les richesses du Palais Mazarin*（Paris, 1885）的书内责任者形式；BnF人物权威FRBNF12982918支持其规范名、伯爵/历史学家称谓、生卒年月日及地点，异名含Jules de Cosnac。
- 新增person卡、manifest、候选映射、accepted路径及BnF外部身份行 `aln-12626`。与1885刊本的正式作者关系、其书内引文与1661年清单的关系仍待S6；未将书目归属转成正式边。`build_field_facts.py`预检无警告并apply登记9条source-backed字段事实及1条BnF来源，未核验字段数不变。

### S4 archive：Cosnac《Les richesses du Palais Mazarin》1885年第二版（2026-10-16）

- `cand-7087` → `archive-group-793f3c145dfa` → `units/archives/les-richesses-du-palais-mazarin-1885`。Haskell书目p.420列Comte Gabriel-Jules de Cosnac、Paris 1885；Persée authority 727409给出Renouard 1885第二版，Smithsonian record siris_sil_278901确认书名、责任者、出版年及实体描述。原书和p.144、pp.169 ff.未独立查阅；author关系待S6。新增外部书目身份行 `aln-12627`（Smithsonian）和 `aln-12628`（Persée），字段表apply新增12条source-backed事实。
- 该刊本与单独登记的1661年清单身份、1653年清单原件及d’Aumale 1861印本分开，不把目录副题当作对清单内容的核验。

### S4 archive：1661年马萨林身后清单（de Cosnac item 1240）（2026-10-16）

- `cand-7091` → `archive-group-fd76703203a6` → `units/archives/mazarin-inventory-1661-de-cosnac-item-1240`。Haskell p.184注3指向de Cosnac item 1240；Persée和Smithsonian书目记录显示1885刊本副题包含1661年Mazarin身后清单。清单原件与item 1240均未独立查阅；该KU仅表示来源指向的清单身份，实际载体和刊录关系未定，不标注为原件或手稿。
- Haskell称Giovanni Andrea Podesta为编制者之一，继续作为来源归属明确的S2关系候选；不新增正式编制或刊录边。与1653年清单、1861年印本及1885年书籍保持不同KU。
- 两项登记后S4累计309组/403条映射，待登记4,531组/4,621条映射；archive已登记46组、待登记1,174组/1,189条候选。字段表apply登记12条刊本字段及4条清单字段source-backed记录；同批共新增3条来源（含BnF人物来源），未核验字段数不变。`build_cards.py --check`预检通过（1,329卡、10,373字段行），全库投影包含50个待写文件、其中48卡涉及关系视图；检查只读，未写回卡片。


### S3 person：Paul Bonnefon 直接关系端点身份裁决（2026-10-16）

- backlog bl-0003 定位第21章书目候选 st-chp21-bib-l243-293-entry-07，source_ref chp-21:21_CHP-21Bibliography:l243-293#L254。原文书目列Brienne, Louis-Henri de Loménie Comte de: *Mémoires*, publiés par Paul Bonnefon, 3 vols., Paris 1916–19。既有书籍KU为 units/archives/brienne-memoires-1916-1919；BnF出版物记录FRBNF34019339确认同一版本并列Paul Bonnefon为编辑责任者。
- 新增S1人物候选 cand-12427。BnF人物权威FRBNF12115372（https://catalogue.bnf.fr/ark:/12148/cb12115372q）将规范名列为Bonnefon, Paul（1861–1922），记录作者责任、Arsenal图书馆馆员和法国文学协会秘书长身份；manifest与person卡中未发现同一人。候选裁为 new-person:paul-bonnefon-1861-1922 / new，只解决端点身份，不把书目责任形式自动转为S6正式关系。
- 新增S3候选行 aln-12629 和BnF人物权威行 aln-12630。旧backlog所述“没有匹配person KU或S3候选”作为裁决前状态保留在backlog完成说明中。

### S4 person：Paul Bonnefon 人物组登记（2026-10-16）

- cand-12427 → new-person:paul-bonnefon-1861-1922 → units/persons/paul-bonnefon。新增双语person卡、manifest、accepted路径和候选KU映射；字段表以Haskell书目与BnF人物权威为依据，不扩写超出所录证据的生平。
- backlog bl-0003 现为 completed，表示S1候选、S3身份与S4端点登记完成；与Brienne《Mémoires》的正式编辑关系仍留待S6，未新增relations.csv边。
- S4累计310组/404条映射，待登记4,531组/4,621条；person已登记92组，待登记993组/1,038条成员。build_field_facts.py预检无警告并apply新增7条source-backed字段事实及1条BnF来源，未核验字段数不变。


### S3 person：Cimaroli 跨章候选复用既有人物 KU（2026-10-16）

- 对照候选 cand-0758–cand-0764 与既有人物 KU units/persons/cimaroli。七条候选的索引主项均为 “Cimaroli, Giovan Battista”；cand-0758（C.csv#282）定位 p.266、288、293、314，其中第9章 p.266 OCR 作 Cimatoli，而第10章 p.288、293及既有 p.314／图版锚点均为 Cimaroli。cand-0760–cand-0764（C.csv#284–288）为 McSwiny British Worthies 注释下的具体主题子目；第10章 p.289 注表将 Cimaroli 与 Lord Somers、William III、Tillotson、Dorset 等行并列，与正文称 Canaletto、Cimaroli 参与部分风景绘制及既有人物卡记载的图版52b相合。既有卡已记录 Fondazione Federico Zeri URL69391 的作者身份依据；本轮复用，不新增外部行。cand-0764 的 ‘Cimaroli?’ 与 ‘(possibly) Lord Stanhope’ 只保留其作品归属不确定，不影响该姓名指向既有画家。cand-0759 虽没有映射 S2 提及或页码，但索引全名与同一 McSwiny 子目足以识别人物；不据此新增正文断言或作品关系。
- 七条均裁为 same → units/persons/cimaroli，`sg3-ku-units-persons-cimaroli` 仅作复用映射组。cand-0758、cand-0760–cand-0764 原有的六条 new 建议组及 cand-0759 的 undecided 理由逐行保留于 alignment resolution_note；不新增人物 KU。原书的委托、作品归属及其他关系主张仍待 S6，不写入 relations.csv。
- S3 same 增加7条，new减少6条及1个待登记组，undecided减少1条；当前候选统计由 alignment 重新计算。S4 新组待登记 4,530组/4,615条候选；已登记新组 310组/404条成员映射；manifest 保持1329 KU。


### S4 person：Bernardino Spada 人物组登记（2026-10-16）

- S3身份组 new-person:bernardino-spada-810d88ac92 仅含 cand-2493，现映射至 units/persons/bernardino-spada；既有同姓人物 cand-2494 → units/persons/virgilio-spada 保持独立。Treccani DBI规范条目为“SPADA, Bernardino”，记录1594-04-21至1661-11-10、1623年驻巴黎教廷使节任命、1626-01-19枢机任命，以及1627年获任博洛尼亚使节并任至1631年（条目称其在领红帽前三日获任）。该规范记录此前在S3由 aln-12613 登记，本轮把外部身份行与候选主行共同映射至同一KU。
- 新增person卡、manifest一条、accepted路径及双语描述；字段事实仅登记姓名、书内称名、生卒和可由Treccani直接支持的教廷职务，不把书内关系候选写成正式关系。与Virgilio Spada的兄弟关系、1632年宫殿取得、枢机与Mazarin相关的可能委托等，继续以原statement为证据并留待S6；条件式委托保持未决。
- 9条直接关系候选仍待S6。本次不改变关系表。`build_field_facts.py` dry-run无警告，apply新增8条source-backed字段记录及1条Treccani来源；未核验字段数保持1,578。
- S4累计311组/405条成员映射，待登记4,529组/4,614条；person已登记93组，待登记991组/1,031条；manifest=1330。


### S4 person：Tommaso Giuseppe Farsetti 人物组登记（2026-10-16）

- S3组 new-person:farsetti-giuseppe-tommaso-339a4db213 仅含 cand-1013，现映射至 units/persons/tommaso-giuseppe-farsetti；当前manifest只含另一个人物 Filippo Farsetti 及Farsetti family，均保持分立。Treccani DBI规范条目为“FARSETTI, Tommaso Giuseppe”，记录1720-04-16生于威尼斯、1791-10-30卒于帕多瓦，并称其为文人和藏书家；该记录此前在S3由 aln-12614 登记，本轮把外部身份行和候选主行共同映射到该KU。
- 新增双语person卡、manifest一条及accepted路径。卡片字段限于姓名、书内称名、出生／去世日期与地点及Treccani明示身份；Haskell第14章短篇拉丁文生平署名、第15章家族史叙述继续作为书内来源主张，关系留待S6。第8章转引经Fogolari，未作为独立核实证据；候选 cand-10443 指向的1778年家族史保持独立archive KU边界。
- 9条直接关系候选仍待S6；未写入 `relations.csv`。`build_field_facts.py` dry-run无警告，apply新增8条source-backed字段记录和1条Treccani来源；未核验字段数保持1,578。
- S4累计312组/406条成员映射，待登记4,528组/4,613条；person已登记94组，待登记990组/1,030条；manifest=1331。


### S3 person：Dionisio Dolfin 跨页身份与外部对齐（2026-10-16）

- `cand-0929`（D.csv#31，pp.252–253）为person候选。第9章p.252先以Dionisio称该人物，p.253给出Dionisio Dolfin全名；两处正文锚点与索引页码相互对应。此前decision为new-person:dionisio-dolfin-b1fe9e909e，且无既有人物KU命中；Dolfin family KU不因同姓而合并。
- Cristina Moro, ‘Dolfin Dionisio,’ *Dizionario Biografico dei Friulani Nuovo Liruti*（https://www.dizionariobiograficodeifriulani.it/dolfin-dionisio，访问于2026-10-16）记录1663年生于威尼斯、1734年8月3日卒于San Vito al Tagliamento；1698年获任其叔Giovanni Dolfin的coadjutor，1699年正式接掌阿奎莱亚宗主教职位。乌迪内教区档案馆历史页（https://www.archiviodiocesano.it/storia/）旁证其1699–1734年任期与驻地项目。
- 外部传记与Haskell p.252的1698年表述不构成冲突：前者区分任命和正式接掌。本轮只增强身份与该任职的时间语境，不把Haskell关于Daniele亲属、宫殿修建、召请Tiepolo或具体作品的陈述改写为外部确认事实。新增身份行 `aln-12631`；9条直接关系端点候选保留待S6，另3条仅在限定中提及该人物。

### S4 person：Dionisio Dolfin 人物组登记（2026-10-16）

- `cand-0929` → `new-person:dionisio-dolfin-b1fe9e909e` → `units/persons/dionisio-dolfin`。新增双语人物卡 `[04-knowledge/units/persons/dionisio-dolfin.md](04-knowledge/units/persons/dionisio-dolfin.md)`、manifest一条及accepted路径；候选决定行和外部身份行 `aln-12631` 共同指向该KU。
- 卡片将Haskell与DBF的时间表述并列，记录其姓名、出生/去世信息、coadjutor任命及正式宗主教任期；没有新增relations.csv边。9条以该人物为直接端点的关系候选逐项留待S6，另3条仅为语境提及。
- S4累计313组/407条映射，待登记4,527组/4,612条；person已登记95组，待登记989组/1,029条成员；manifest=1332。`build_field_facts.py` dry-run无警告并apply登记11条source-backed字段记录、新增2条来源；unverified数量保持1,578。


### S4 person：Augustus II of Poland 双候选组登记（2026-10-16）

- `cand-0146`（A.csv#147，pp.266、278、294）与索引子项 `cand-0147`（A.csv#148，p.294）共同映射至 `units/persons/augustus-ii-of-poland`；同一S3组内两条候选分别保留各自来源锚点。GND 118505084（aln-12611）与Sächsische Biografie（aln-12612）此前已在S3确认姓名对应、萨克森选帝侯/波兰国王身份及1670–1733年生卒；本轮将两行与两条候选决定一并映射。
- Haskell第10章p.294将Frederick Augustus I与波兰国王Augustus II ‘the Strong’明确对应；p.278以同一别称称Diziani工作的Dresden宫廷。既有 Augustus III 卡属于其子Friedrich August II，身份保持分立，不把父子或赞助陈述写入relations.csv。
- 新卡记录双语标题、索引/正文名称锚点、外部规范名、生卒及选帝侯/波兰国王身份。10条直接S2端点陈述中9条为关系候选，全部留待S6；本轮没有新增正式关系。
- S4累计314组/409条映射，待登记4,526组/4,610条；person已登记96组，待登记988组/1,027条成员；manifest=1333。`build_field_facts.py` 预检无警告并apply登记11条source-backed字段记录、新增2条来源；unverified数量保持1,578。


### S4 person：Pierre-Jean Mariette 跨章候选登记（2026-10-16）

- `cand-1547`（M.csv#85）保持S3组 `new-person:jean-mariette-pierre-69263c8b1d`，现映射至 `units/persons/pierre-jean-mariette`；没有同名person KU，未把相近姓氏或索引项目并入。新卡只录索引全名、正文称名及Haskell第13章注3所称French connoisseur，不补生卒、籍贯或外部身份。
- 身份与跨章语境依据包括第6章p.165的明示传闻引语、第10章p.285对壁画毁坏的评论、第13章p.341正文及注3、第14章p.351注2和第15章p.361正文／注2。后几处的往来、信件及作品评价仍属原书陈述；不据书目引用声称已读原件。
- 10条直接S2陈述中7条为关系候选，均留待S6；另3条不标为关系候选。本轮没有新增relations.csv边、archive/work KU或外部身份记录。
- `build_field_facts.py` 预检无警告并apply新增4条source-backed字段记录、来源数不变；unverified数量保持1,578。
- S4累计315组/410条映射，待登记4,525组/4,609条；person已登记97组，待登记987组/1,026条成员；manifest=1334。


### S4 person：Pietro Ercole Gherardi 跨章候选登记（2026-10-16）

- `cand-1155`（G.csv#62）保持S3组 `new-person:ercole-gherardi-pietro-8af999ae11`，现映射至 `units/persons/pietro-ercole-gherardi`；第10章p.302注4给出全名，章9和13的P. E. Gherardi缩写与索引页码对应。无既有人物KU命中；新卡不补外部生平字段。
- 书内身份语境包括Haskell称其为Modenese、Muratori的友人及一篇Descrizione作者；相关书信、作品及人物关系不在此转为正式边。第9章多个脚注仅列信件与Biblioteca Estense馆藏信息，原件未查阅。S2候选 `cand-9192` 的出版物题名、版本与对象粒度未定，仍保持undecided；相关archive候选各自保留身份组，不合并为一个文献。
- 10条直接S2陈述中7条为关系候选，均留待S6；另3条为非关系陈述。本轮未新增 `relations.csv` 边、archive/work KU或外部身份记录。
- `build_field_facts.py` 预检无警告并apply新增4条source-backed字段记录、来源数不变；unverified数量保持1,578。
- S4累计316组/411条映射，待登记4,524组/4,608条；person已登记98组，待登记986组/1,025条成员；manifest=1335。


### S4 person：François Boucher 三候选跨章组登记（2026-10-16）

- `cand-0421`（B.csv#268，主项）、`cand-0422`（B.csv#269，and Count Tessin）及`cand-0423`（B.csv#270，designs for Tombeaux des Princes）保持S3组 `new-person:boucher-francois-2b86c8ca6d`，现共同映射至 `units/persons/francois-boucher`。三条索引均为Boucher, François；候选子项分别定位于同一索引主项下，正文跨章以Boucher称画家/设计者。未将索引子目拆成独立person或work KU。
- 既有manifest没有François Boucher人物卡；S3未访问外部身份源。本卡仅录书内全名、三个索引锚点和跨章语境，不补书外生平。p.291设计陈述、Tessin收藏／委托、Algarotti画廊计划、风格比较和相关人物互动仍按原S2 statements保留。
- 三条成员候选对应的7条直接S2陈述均标为关系候选，留待S6逐项审查；未新增 `relations.csv` 边或外部身份行。
- `build_field_facts.py` 预检无警告并apply新增5条source-backed字段记录、来源数不变；unverified数量保持1,578。
- S4累计317组/414条映射，待登记4,523组/4,605条；person已登记99组，待登记985组/1,022条成员；manifest=1336。


### S4 person：Donato Creti 跨章候选登记（2026-10-16）

- `cand-0889`（C.csv#423）保持S3组 `new-person:creti-donato-4d75402fa5`，现映射至 `units/persons/donato-creti`；无既有人物KU命中。索引Creti, Donato及第7、8、14章的全名/指称共同支持书内人物身份；第10章OCR写Donato Cred，`chp10_p288_migration.py`记录已对照纸本校读为Creti，未改写原来源。
- 新卡限于姓名、索引形式及书内画家身份。Haskell对Creti与Crespi的比较、Ruffo的观看／收藏／授予称号叙述、Louis XIV仰慕报告和Algarotti提案均保留原statement及限定，不升级为正式关系；授勋权力和日期不明，相关term候选 `cand-7745` 继续undecided。
- 9条直接S2陈述中7条为关系候选，另2条为非关系陈述；关系候选待S6逐条审查。本轮没有新增 `relations.csv` 边、term KU或外部身份记录。
- S4累计318组/415条映射，待登记4,522组/4,604条；person已登记100组，待登记984组/1,021条成员；manifest=1337。


### S4 person：Pietro Tacca 跨章双候选组登记（2026-10-16）

- `cand-2537`（T.csv#0）与 `cand-2538`（T.csv#1）保持S3组 `new-person:pietro-tacca-374a1e8a84`，共同登记为 `units/persons/pietro-tacca`。索引主项、跨第4、7章的正文全名及第19章附录签名相互支持同一人物身份；现有manifest和person卡均无同名对象。
- 卡片限于索引全名、索引形式和书内雕塑家身份。第4章p.97报告模型发送和附注所述通信；第7章pp.174、178记载纪念碑、雕塑身份及赴英计划被拒；第19章p.389刊出Tacca署名的1624年信件。该信的原档案未独立查阅，方案不视为完成作品。
- 7条直接S2陈述均标为关系候选，全部留待S6逐条审查。本轮不写入 `relations.csv`，不推定未完成雕塑、作品存世或手稿已核。
- `build_field_facts.py` 预检无警告并apply新增3条source-backed字段记录，来源数不变、unverified保持1,578。S4累计319组/417条映射，待登记4,521组/4,602条；person已登记101组，待登记983组/1,019条成员；manifest=1338。


### S4 person：John Breval 跨三章身份组登记（2026-10-16）

- `cand-0451`（B.csv#298）保持S3组 `new-person:breval-john-03249744d6`，映射至 `units/persons/john-breval`。索引列pp.222、266、301、306、307；第8、9、10章均以John Breval全名锚定同一书内人物。无既有人物KU命中，未访问外部身份源。
- 卡片只收录全名、索引形式与第10章明确称作connoisseur的书内身份。第8章Ferrara绘画评论、第9章对Sagredo及其收藏的引语，以及第10章Smith访客记述留作书内语境。Breval 1738年卷I p.230仅见Haskell转引，未独立查阅。
- 9条直接S2 statements中6条为relation_candidate，另3条记录嵌套引文或评价语境，不构成独立正式关系。p.306将小雕像称作‘seemingly an Aesculapio’，p.307续文称‘Priapus’；差异保留，未新建或裁定该对象。6条关系候选留待S6；本轮不修改 `relations.csv`。
- `build_field_facts.py` 预检无警告并apply新增3条source-backed字段记录，来源数不变、unverified保持1,578。S4累计320组/418条映射，待登记4,520组/4,601条；person已登记102组，待登记982组/1,018条成员；manifest=1339。


### S4 person：Francesco Angeloni 跨章人物组登记（2026-10-16）

- `cand-0107`（A.csv#108）保持S3组 `new-person:angeloni-francesco-24d9ba915a`，登记为 `units/persons/francesco-angeloni`。第2章p.53注、第4章p.114和第6章p.158的全名锚点与索引范围相合；无既有人物KU命中，未访问外部身份源。
- 卡片字段限于全名、索引形式及Haskell明确提供的身份称谓：archaeologist、antiquarian、collector、writer。Bellori被称作Angeloni侄子的表述为‘was said to be’，只保留报告性主张；监护关系、朋友关系、勋章收藏、Carracci素描所有权和同时代人提及频率均按原S2 qualifiers 保留，不写入正式关系。
- 9条直接S2 statements中8条为relation_candidate、1条为作者评价。Cassiano、Poussin、其他同时代人的引述及Bellori关系均未据书内书目提升为外部核验。8条关系候选留待S6，本轮不修改 `relations.csv`。
- `build_field_facts.py` 预检无警告并apply新增6条source-backed字段记录，来源数不变、unverified保持1,578。S4累计321组/419条映射，待登记4,519组/4,600条；person已登记103组，待登记981组/1,017条成员；manifest=1340。


### S4 person：Giambattista Biffi 跨章人物组登记（2026-10-16）

- `cand-0373`（B.csv#220）保持S3组 `new-person:biffi-giambattista-0fc083bcf0`，登记为 `units/persons/giambattista-biffi`。索引页码涵盖p.262注、p.328和p.360；第9章简写Gio. Battista Biffi，第10、14章写作Giambattista Biffi。全名与拼写变体属于同一索引人物组；既有manifest无同名person KU，未访问外部身份源。
- 第9章源文本的OCR页标`[Page 202]`已由p.262页图对校；第10章的`[Page 28]`按S2过程记录校为印本p.328。卡片不改写S0来源。
- 卡片仅登记索引/正文名称形式，不扩写书外职业生平。第9章1773年藏画描述、第10章友情陈述、Zuccarelli评价与Rousseau日记引文，以及第14章Biffi对Algarotti与Cecilia Emo的引述，均保留Haskell归属。Haskell引注中的Venturi、Bellori、Lumbroso、Poussin作品、未刊信及日记未独立查阅。
- 9条直接S2 statements中7条为relation_candidate、2条为引文定位或日记事件陈述；7条关系候选留待S6。本轮未修改`relations.csv`，不裁决Palazzo Giovanelli所列作者异名。
- `build_field_facts.py` 预检无警告并apply新增3条source-backed字段记录，来源数不变、unverified保持1,578。S4累计322组/420条映射，待登记4,518组/4,599条；person已登记104组，待登记980组/1,016条成员；manifest=1341。


### S4 person：Carlo Cordellina 跨章人物组登记（2026-10-16）

- `cand-0842`（C.csv#372）保持S3组 `new-person:carlo-cordellina-80fe525d81`，登记为 `units/persons/carlo-cordellina`。索引列p.256和p.405，第9章与第二版后记均以Carlo Cordellina全名锚定；无既有人物KU命中，未访问外部身份源。
- 卡片仅登记姓名、索引形式和第9章明确称为leading advocate的法律身份。第9章两处住所、Tiepolo装饰和作品叙述，以及后记记载的1770年Vicenza宫殿开建和其后去世信息均保留来源归属。Haskell引用的Puppi文章、Tiepolo信件未独立查阅。
- S2为Vicenza房屋及p.405宫殿保留的对象候选`cand-8375`仍未裁定两处是否同一建筑；本轮不合并端点或创建关系。8条直接S2 statements中7条为relation_candidate、1条为非关系生活方式描述；7条关系候选待S6。
- `build_field_facts.py` 预检无警告并apply新增3条source-backed字段记录，来源数不变、unverified保持1,578。S4累计323组/421条映射，待登记4,517组/4,598条；person已登记105组，待登记979组/1,015条成员；manifest=1342。


### S4 person：Cristoforo Roncalli 跨三章身份组登记（2026-10-16）

- `cand-2218`（Q-R.csv#145）保持S3组 `new-person:cristoforo-roncalli-a72597e026`，登记为 `units/persons/cristoforo-roncalli`。索引列第2章p.30、第3章p.69和第4章p.94注；第2章直接给出Painter Cristoforo Roncalli, known as Pomarancio，第3章用Pomerancio，第4章讨论Romanelli/Pomarancio校改及Nicolson提出的抄写可能。现有person KU无同名命中，未访问外部身份源。
- 卡片保留Pomarancio/Pomerancio两种书内拼写，并将校改解释标为Haskell转述；不据该注释独立声称原信确写Roncalli或Pomarancio。
- 8条直接S2 statements均为relation_candidate，涉及出行、绘画/祭坛画、作品购藏、Oratorians、Giustiniani及信件校读，全部留待S6逐条审查。本轮不新增`relations.csv`边，不合并或新建作品KU。
- `build_field_facts.py` 预检无警告并apply新增5条source-backed字段记录，来源数不变、unverified保持1,578。S4累计324组/422条映射，待登记4,516组/4,597条；person已登记106组，待登记978组/1,014条成员；manifest=1343。


### S4 person：Paul Fréart de Chantelou 跨三章身份组登记（2026-10-16）

- `cand-0648`（C.csv#172）保持S3组 `new-person:chantelou-de-freart-paul-258ab261f8`，登记为 `units/persons/paul-freart-de-chantelou`。索引列第4章p.106、第6章p.146和第7章p.176；正文全名/简称跨章相合，S3已按完整姓名锚点分组，现有person KU无同名命中，未访问外部身份源。
- 卡片保留第4章无重音写法`Paul Freart de Chantelou`，记录第6章的巴黎赞助人角色和第7章受未具名Surintendant派遣赴罗马的代理人角色；不补该官员姓名。中文展示名注明为工作音译。
- 7条直接S2 statements均为relation_candidate，涉及友谊、文稿/摹画副本赠与和携带、书信、罗马差遣、招募任务及返程护送，全部留待S6逐条审查。本轮不新增`relations.csv`边，不扩展未具名作品或人员端点。
- `build_field_facts.py` 预检无警告并apply新增5条source-backed字段记录，来源数不变、unverified保持1,578。S4累计325组/423条映射，待登记4,515组/4,596条；person已登记107组，待登记977组/1,013条成员；manifest=1344。


### S4 person：Vittorio Amedeo II, Duke of Savoy 跨两章身份组登记（2026-10-16）

- `cand-2388`（S.csv#76）保持S3组 `new-person:amedeo-ii-of-savoy-vittorio-bf13fb4fc0`，登记为 `units/persons/vittorio-amedeo-ii-duke-of-savoy`。索引同一主项列p.89、200、202；p.89段落接在1680年Oliva召Pozzo赴罗马之后，p.200–202进入西班牙王位继承战争及Turin艺术赞助，年代语境相容。S3按完整姓名/显式异名锚点分组；现有manifest无Vittorio/ Victor Amadeus II人物卡，未访问外部身份源。
- 卡片保留索引形式`Vittorio Amedeo II, Duke of Savoy`和正文拼写`Victor Amadeus of Savoy`，不以标题推演未见于原文的生平信息。
- 10条直接S2 statements中9条为relation_candidate，1条记录公爵的误认并按非关系陈述保留。9条涉及Pozzo任职/召回/许可、对教宗申诉、对耶稣会施压、未具名个人信件、与Juvarra共同改变Turin局面、吸引画家或作品及追随其他赞助人先例；全部留待S6。本轮不写`relations.csv`，不把绘画/作品分支消歧。
- `build_field_facts.py` 预检无警告并apply新增4条source-backed字段记录，来源数不变、unverified保持1,578。S4累计326组/424条映射，待登记4,514组/4,595条；person已登记108组，待登记976组/1,012条成员；manifest=1345。


### S4 person：Felice Boscarati 跨两章身份组登记（2026-10-16）

- `cand-0411`（B.csv#258）保持S3组 `new-person:boscarati-felice-af2f756b3b`，登记为 `units/persons/felice-boscarati`。第10章p.326、327与第20章后记p.408重复给出全名/姓氏锚点，identity group由完整姓名和上下文对应；既有manifest无同名person KU，未访问外部身份源。
- 卡片记录艺术家身份和Boscarati姓氏形式；原文“official painter”不据以推断正式薪职。第20章后记所引证词经过Olivato转述，未独立查阅该文或审讯档案。
- 7条直接S2 statements中6条为relation_candidate，涉及Pisani接纳其为画家、展示图像的候选归因（保留另一种可能）、Pisani与Boscarati的关系、Pisani失势后Boscarati的处境、Boscarati证词及其后续观点；全部留待S6。1条讽刺倾向评价保持非关系候选。本轮不新增`relations.csv`边。
- `build_field_facts.py` 预检无警告并apply新增4条source-backed字段记录，来源数不变、unverified保持1,578。S4累计327组/425条映射，待登记4,513组/4,594条；person已登记109组，待登记975组/1,011条成员；manifest=1346。


### S3 复核：Modena 公爵候选改列待证（2026-10-16）

- 复核 `cand-1675`／`aln-2010`。原决定为`new`，组 `new-person:modena-of-6566b00ada`；现改为`undecided`，撤回该身份组，不登记KU。旧对齐理由原样保留在resolution_note并标注为前次裁决。
- S1索引 M.csv#217 把p.143与p.177注4列在同一标题“Modena, Duke of”下，但索引仅供定位。S2 p.143写Duke of Modena向罗马代理人索求画作，未给请求日期；S2 p.177注4转述Gabriele Balestrieri于1645年写给Duke of Modena的信，原信与Lumbroso/Venturi记录未在本次独立查阅。两处都没有公爵全名。p.143所在论述包含Rosa自1637年至1667年间的多项事件，但此句没有可据以锁定任期的日期。不能仅凭同一标题或索引页码证明是同一公爵；也没有足够证据将此单一索引候选拆成两个已识别人物。
- 原resolution_note的“source anchor gives a full personal name”及“full-name/explicit-alias anchor (modena of)”不受原文支持，现明确视为被撤回的旧理由。依verify规则，头衔不足以合并人物；保持`undecided`，直到有可核的年代/身份记录能够连接或区分两处。
- 候选直接关联10条S2 statement，其中9条relation_candidate、1条评价性非关系陈述；保持原分类。更新后S3为same=1,781、new=5,018/4,839组、conflict=8、excluded=100、undecided=5,498。S4 KU清单和关系表均不因本次修订改变。


### S3复核：Baglione人物子项与《The Resurrection》作品组（2026-10-16）

- cand-0157（B.csv#4，Divine Love，p.127）原为undecided，理由是无S2正文提及。复核索引主项与原文后改为new并并入new-person:baglione-giovanni-f65db6f695：同一主项Baglione, Giovanni在p.127以Divine Love作作品子项；正文同页以[Giovanni Baglione]为全名并明确称其绘制该画。该索引子项不是第二个人，也不作为人物别名。原未决理由保留在alignment resolution_note的prior记录中。
- cand-5013（p.66的The Resurrection画作）和cand-5297（p.84的1602年耶稣堂右横翼礼拜堂祭坛画）从两个new组并为同一new作品组workgrp-3089e5ca7ba112。相同画家、复活题材、耶稣会教堂语境与相容年代支持此判断；p.84未重复题名且p.66未明说地点，因此不推定祭坛画的题名出处、展示状态或投诉年份。两条旧组号与前次理由仍保留在alignment行。
- 其余Cand-0156及Cand-0158保持原new决定；同组三条person候选将在S4映射到一个KU。本次没有新增relations.csv正式关系；p.66、p.84、p.127所涉关系仍待S6审查。

### S4 person：Giovanni Baglione跨章人物组登记（2026-10-16）

- cand-0156、cand-0157、cand-0158同映射至units/persons/giovanni-baglione。三条候选分别来自B.csv#3主项、B.csv#4 Divine Love子项和B.csv#5 Resurrection子项；第3章p.66、第5章p.127的正文全名锚点与共享主项支持同一人物。工作题名子项不作为人物别名；cand-0157从undecided改为new的依据及旧理由保留在S3记录。
- 卡片只收录书内姓名、索引形式和明确画家身份。第3章对1602年祭坛画和The Resurrection报酬争议的两处记录未推定投诉年份、当前陈列或外部身份；第5章证言按Haskell转述保留。6条直接S2关系候选均有已登记KU端点，但全部留待S6逐条裁决，本批未修改relations.csv。
- 本批还将cand-5013与cand-5297映射至同一The Resurrection作品KU，并登记cand-6045的Divine Love及cand-6046的Earthly Love作品KU。各自证据与未采纳的额外推断见卡片、alignment和S3/S4过程段落。三件作品相关关系候选均未升为正式边。
- S4累计331组/432条映射，待登记4,507组/4,587条；person已登记110组，待登记973组/1,008条成员；work已登记23组，待登记462组/474条成员；manifest=1350。build_field_facts.py预检无警告并apply新增13条source-backed字段记录，来源登记未变化，unverified保持1,578；本批不做S5补足或外部采集。

### S4：Pietro Edwards 人物与 MSS. 788.13 档案端点登记（2026-10-16）

人物组 `new-person:edwards-pietro-4c9347ce42`（`cand-0965`）映射至[皮耶特罗·爱德华兹人物卡](../../../04-knowledge/units/persons/pietro-edwards.md)；档案组 `archive-group-e755dc71ceb3`（`cand-8534`）映射至[Edwards 清单档案卡](../../../04-knowledge/units/archives/pietro-edwards-inventories-seminario-patriarcale-ms-788-13.md)。第9章 p.261 与第17章 p.380 均报告 Seminario Patriarcale 的 MSS. 788.13 与 Edwards 清单/曼弗林画廊记录有关；两处报告的时间措辞分别保留为“威尼斯共和国覆亡时”和“18世纪末前”，本轮未把它们换算为精确年份。手稿、目录和原件均未独立查阅，卡名为描述性工作题名。Edwards 的6条直接关系候选及档案端点的2条关系候选全部保留待 S6；Manfrin 人物端点已映射，本轮未修改 `relations.csv`。S4 累计登记333组/434条映射，待登记4,505组/4,585条；KU 总数1,352。

### S4 验证：Edwards 人物与档案端点登记（2026-10-16）

- `build_field_facts.py` 预检：cards=1,352；enrichment rows=10,476；new/changed/removed IDs 均为0；source registry changes=0；warnings=0。无字段表写回。
- `audit_tables.py --strict-stage --summary` 退出码0：KU=1,352；`errors=[]`、`s2_missing=[]`；待登记 new alignment 共4,600条，其中4,585条候选决定映射（4,505组）和15条外部身份记录。既有两条来源引用警告与S2语义审查提示继续按结果文件保留。

### S4：Scipione Maffei 人物与古代雕塑术语端点登记（2026-10-16）

人物组 `new-person:maffei-scipione-5c81fca946`（`cand-1487`）映射至[Scipione Maffei 人物卡](../../../04-knowledge/units/persons/scipione-maffei.md)；术语组 `sg3-term-cand-12249`（`cand-12249`）映射至[古代雕塑术语卡](../../../04-knowledge/units/terms/antique-sculpture-maffei-context.md)。三章全名锚点支持同一人物组；p.230、p.320、p.372 的内容分别保留为 Haskell 对赞助、交往和收藏的书内陈述。Lodoli、Ferdinand de’ Medici 与 Angelo Querini 端点已有 KU；古代雕塑通类本批登记。5条关系候选均留待 S6，其中 `st-chp15-p372-maffei-recorded-evidence-of-the-past` 仍有未具体识别的开放对象端点，不据此新造对象；未修改 `relations.csv`。S4 累计登记335组/436条映射，待登记4,503组/4,583条；KU 总数1,354。

### S4 验证：Maffei 人物与术语登记（2026-10-16）

- `build_field_facts.py` 预检：cards=1,354；enrichment rows=10,476；new/changed/removed IDs 均为0；source registry changes=0；warnings=0。无字段表写回。
- `audit_tables.py --strict-stage --summary` 退出码0：KU=1,354；`errors=[]`、`s2_missing=[]`；待登记 new alignment 共4,598条，其中4,583条候选决定映射（4,503组）和15条外部身份记录。既有两条来源引用警告与S2语义审查提示继续保留。

### S3 复核：Paolo Girolamo Piola 复用既有人物 KU（2026-10-16）

候选 `cand-1935` 原列为 `new-person:girolamo-paolo-piola-b16cf26a54`／`new`。检查发现既有[Paolo Gerolamo Piola 人物卡](../../../04-knowledge/units/persons/paolo-girolamo-piola.md) 已引同一书第1章 p.8 与 p.10 的同名原文，并记录同一索引行 `Piola, Paolo Girolamo, xvii, 8n, 10, 166n, 197`；旧卡明确保存 Gerolamo/Girolamo 名形。因此将 `cand-1935` 从 `new` 改为 `same`，映射至 `units/persons/paolo-girolamo-piola`；原组号、旧理由及撤回原因均保留在 alignment 行。不新增人物卡或 manifest 行，也未改关系；第1、6、7章的关系候选沿用该既有人物端点，开放端点仍待证。更新后 S3 same=1,782（1,027 KU）、new=5,018/4,837组；S4 已登记335组/436条，待登记4,502组/4,582条。

### S3/S4 验证：Piola 身份复用后全书表审计（2026-10-16）

- `audit_tables.py --strict-stage --summary` 退出码0：KU=1,354；`errors=[]`、`s2_missing=[]`；当前待登记 new alignment 共4,597条，其中4,582条候选决定映射（4,502组）和15条外部身份记录。S3 当前 same=1,782/1,027 KU，new=5,018/4,837组，conflict=8，excluded=100，undecided=5,497。S4已登记335组/436条映射，待登记4,502组/4,582条。
- `build_field_facts.py` 预检未产生字段或来源变化，warnings=0；enrichment维持10,476条，其中1,578条unverified。审计保留两条既有字段来源引用警告及S2语义审查提示。

### S4：Jacques Casanova de Seingalt 跨章人物组登记（2026-10-16）

人物组 `new-person:casanova-de-jacques-seingalt-f2334ab49d`（`cand-0591`）映射至[雅克·卡萨诺瓦·德·塞恩加尔特人物卡](../../../04-knowledge/units/persons/jacques-casanova-de-seingalt.md)。本书索引给出全名形式和四个页码；正文跨第9、15、16章以 Casanova 指称。Corner 与 Memmo 端点已映射；Eusebio della Lena 与 Count of Waldstein 各自仍为 S3 new、待 S4。5条关系候选全部留待 S6，未改 `relations.csv`；Count of Waldstein 的书内称谓不扩展为未经证实的名字或生平。S4 累计登记336组/437条映射，待登记4,501组/4,581条；KU 总数1,355。

### S4 验证：Casanova 人物组登记（2026-10-16）

- `build_field_facts.py` 预检：cards=1,355；enrichment rows=10,476；new/changed/removed IDs 均为0；source registry changes=0；warnings=0。无字段表写回。
- `audit_tables.py --strict-stage --summary` 退出码0：KU=1,355；`errors=[]`、`s2_missing=[]`；待登记 new alignment 共4,596条，其中4,581条候选决定映射（4,501组）和15条外部身份记录。Casanova 组5条关系候选保留待S6；Eusebio与Count of Waldstein端点仍待S4。

### S4 验证：Casanova 索引证据修订（2026-10-17）

- 人物卡补入书末索引 p.449 OCR L768 的引文与定位；原 OCR 漏识首字母 C，规范化索引记录 `C.csv#115` 保留全名形式。该证据作为索引定位而非外部身份核验。
- `build_field_facts.py` 预检：cards=1,355、enrichment=10,476；无新增/变更/移除、无来源登记变化、warnings=0。`audit_tables.py --strict-stage --summary` 退出码0：KU=1,355，errors=[]，s2_missing=[]；当前S4待登记4,501组/4,581条候选及15条外部身份记录。

### S4：Eusebio della Lena 人物端点登记（2026-10-17）

人物组 `new-person:della-eusebio-lena-d7eabb742e`（`cand-1386`）映射至[尤西比奥·德拉莱纳人物卡](../../../04-knowledge/units/persons/eusebio-della-lena.md)。第16章正文只称其为 Eusebio，并称其为 Giacomo della Lena 的另一位兄弟；书末索引以 Eusebio della Lena 汇集该页。卡片保留这一书内姓名与亲属语境，不作外部身份扩展。其与 Casanova 的1条关系候选留待 S6；本轮未修改 `relations.csv`。S4 累计登记337组/438条映射，待登记4,500组/4,580条；KU 总数1,356。

### S4 验证：Eusebio della Lena 端点登记（2026-10-17）

- `build_field_facts.py` 预检：cards=1,356；enrichment rows=10,476；new/changed/removed IDs 均为0；source registry changes=0；warnings=0。
- `audit_tables.py --strict-stage --summary` 退出码0：KU=1,356；`errors=[]`、`s2_missing=[]`；当前待登记 new alignment 共4,595条，其中4,580条候选映射（4,500组）和15条外部身份记录。Eusebio–Casanova 关系候选两端现均有KU，仍待S6。

### S3/S4：Waldstein 伯爵称谓的身份限定与端点登记（2026-10-17）

候选 `cand-2797` 保持 `new-person:of-waldstein-9d1421b82c`／`new`，登记至[Waldstein 伯爵人物卡](../../../04-knowledge/units/persons/count-of-waldstein-casanova-dux.md)。复核更正了 S3 旧备注：书中没有给出名字，索引仅列 “Waldstein, Count of”；保留 `new` 的范围是 p.367 语境中 Casanova 在 Dux 的特定保护人这一 source-local person，不宣称外部历史身份已确定。同页另一陈述只询问他是否愿为一座雕像出资，候选 `cand-11561` 仍为 `undecided`；不写成委托或付款。两条关系候选均待 S6，未写入 `relations.csv`。S4 累计登记338组/439条映射，待登记4,499组/4,579条；KU 总数1,357。

### S3 裁决理由补正：Waldstein 身份组依据（2026-10-17）

在 S4 登记后复核 alignment 原备注，发现除“原书提供全名”外，旧备注中的“按 `(of waldstein)` 全名／别名锚点聚组”也不成立。原书和索引都没有给出全名或别名；保留的 `new-person:of-waldstein-9d1421b82c` 仅为稳定追踪键，不构成身份依据。现行 `new` 决定限于 p.367 中作为 Casanova 在 Dux 保护人的单一书内人物，不声称其历史全名或外部身份已确认。该候选组目前只有 `cand-2797`；依据修订已追加到其 alignment 行，旧理由保留为历史记录。

### S4 person：Robert Adam 跨章身份组登记（2026-10-17）

候选 `cand-0012`（A.csv#11）与 `cand-0013`（A.csv#12）保持 S3 人物组 `new-person:adam-robert-145d4691c8`，共同映射至[Robert Adam 人物卡](../../../04-knowledge/units/persons/robert-adam.md)；同组仅登记一个 KU。第10章 p.301、302、310与第19章附录5 p.392多处出现同名；第13章 p.336再次以全名指称该人并记述1761年途经威尼斯时托 Albrizzi 代售其书。章节称谓和日期语境相容，原书关系叙述与被引信件/文献保持各自来源限定；未作外部身份补足。直接相连的3条 S2 relation_candidate 留待 S6：James 致 Robert 的信、Robert 的书对象、以及托 Albrizzi 代售。p.310 注1有关1757年访问与收藏评价的 statement 标为非关系陈述；不新增 `relations.csv` 正式边。S4 累计登记339组/441条候选映射，待登记4,498组/4,577条；KU 总数1,358。

### S4 验证：Robert Adam 跨章组登记（2026-10-17）

- `build_field_facts.py` 预检：cards=1,358；enrichment rows=10,476；new/changed/removed IDs 均为0；source registry changes=0；warnings=0。无字段表写回。
- `audit_tables.py --strict-stage --summary` 退出码0：KU=1,358；`errors=[]`、`s2_missing=[]`；待登记 new alignment 共4,592条，其中4,577条候选映射（4,498组）和15条外部身份记录。两条既有来源引用警告（`enr-06678`、`enr-06937`）与S2语义审查提示继续保留。Robert Adam两条候选均映射至同一卡；3条直接关系候选仍待S6，`relations.csv`未变。


### S3 来源定位补录：Papal States 身份依据（2026-10-17）

`sg3-institution-cand-1831` 的既有 S3 理由提到 Treccani《Pontificio, Stato》，现将其完整记录补入 `sources.csv`：`src-3817a9fe855cd4d5`，访问日期 2026-10-17，URL `https://www.treccani.it/enciclopedia/stato-pontificio/`。复核页面开篇定义确认其将 Stato della Chiesa 说明为教宗行使世俗统治的国家实体，并称治理延续至1870年。该来源只支持 S3 的政治实体身份与 `institution` 类型，不验证 Haskell 的具体收入、边界、主权或艺术史陈述。

### S4 institution：Papal States 跨章身份组登记（2026-10-17）

`cand-1831`（P.csv#30）、`cand-1832`（P.csv#31）与 `cand-1833`（P.csv#32）保持 S3 组 `sg3-institution-cand-1831`，登记为[教皇国机构卡](../../../04-knowledge/units/institutions/papal-states.md)；三条候选映射至一个 KU。第2、6、8章语境与名称锚点支持同一政治地域；Rome 城市及 Holy See 候选 `cand-4424` 保持分开。8条直接关系候选留待 S6；两条关于财富的 statement 是非关系陈述。Treccani 来源仅补足身份/类型追溯，本轮未做 S5、未写正式关系。S4 累计登记340组/444条候选映射，待登记4,497组/4,574条；KU 总数1,359。sources.csv 新增1条外部身份来源（src-3817a9fe855cd4d5）。

### S4 验证：Papal States institution 组登记（2026-10-17）

- `build_field_facts.py` 预检：cards=1,359；enrichment rows=10,476；new/changed/removed IDs 均为0；source registry changes=1（Treccani 条目）；warnings=0。无字段表写回。
- `audit_tables.py --strict-stage --summary` 退出码0：KU=1,359；sources=1,716；`errors=[]`、`s2_missing=[]`；待登记 new alignment 共4,589条，其中4,574条候选映射（4,497组）和15条外部身份记录。既有两条来源引用警告（`enr-06678`、`enr-06937`）与S2语义审查提示继续保留。三个 Papal States 候选映射至同一 KU；8条 S6 关系候选仍未写入 `relations.csv`。


### S3 复核：Colonna palace 与售予 Chigi 的宫殿拆分（2026-10-17）

原共享组 `sg3-place-colonnapalace` 包含 `cand-0815` 与 `cand-0816`；现拆分为两个 `new` place 组：`sg3-place-colonnapalace`（仅 cand-0815）和 `sg3-place-chigi-palace-ss-apostoli`（cand-0816）。第6章 p.154 称 Flavio Chigi 于1662年从 Colonna 家族一支购入 Piazza SS. Apostoli 的宫殿；p.155 随后称 Colonna 家族的另一座宫殿位于“the one sold to the Chigi”附近，并由 Filippo 与 Cardinal Girolamo Colonna 重建和装饰。邻近关系及两个不同所有者/建筑上下文直接排除同一建筑。cand-0816 的旧 S3 组 token 与理由保留在其 alignment 行的 prior 字段；现行分组依据和边界更正追加于两行。两个对象均无同名 place KU，继续作为 source-local new 对象交 S4。修正后 S3 new 仍为5,018条候选、4,838组；S4 待登记4,498组/4,574条映射。

### S4 place：Colonna family palace 与 Flavio Chigi palace 分组登记（2026-10-17）

按已更正的 S3 身份组，`cand-0815` 登记为[罗马科隆纳家族宫殿卡](../../../04-knowledge/units/places/colonna-family-palace-rome.md)，`cand-0816` 登记为[Flavio Chigi 圣使徒广场宫殿卡](../../../04-knowledge/units/places/flavio-chigi-palace-ss-apostoli.md)。两者都是 S3 `new` place，但代表两个相邻建筑，各自一个 KU。前者依据 p.155 的 Colonna 家族宫殿段落；后者依据 p.154 的 Chigi 购买/地点/装饰段落及 p.155 对两座建筑的明确区分。两卡分别保存4条与5条关系候选，均待 S6；Chigi 宫殿另外3条非关系 statement 保持原分类。本轮未写 `relations.csv`。S4 累计登记342组/446条候选映射，待登记4,496组/4,572条；KU 总数1,361。

### S3 来源标识规范化：Treccani 条目（2026-10-17）

`src-6a9a11ba2d327062` 是补录 Treccani 来源时使用的临时标识；字段表构建器按卡片引文生成规范 ID `src-3817a9fe855cd4d5`，原标识会导致预检重复登记。现已将 Papal States 卡、`sources.csv` 与对应 alignment 来源注记统一到规范 ID；该改动仅规范来源标识，不改变来源、S3 身份决定或 S4 KU 映射。


### S4 验证：Colonna 与 Chigi 两座宫殿分组登记（2026-10-17）

- `cand-0815` 当前为 `new` 并映射至 `units/places/colonna-family-palace-rome`；`cand-0816` 当前为独立 `new` 并映射至 `units/places/flavio-chigi-palace-ss-apostoli`。两条 alignment 各对应一个 manifest KU，卡片均在 `accepted.yml` 中。
- 两卡保留9条直接关系候选（Colonna 4、Chigi 5）供 S6 审查；Chigi 宫殿另3条非关系陈述维持原分类。未写入 `relations.csv`。
- `build_field_facts.py` 预检：cards=1,361，rows=10,476，unique_sources=1,716；records_with_source=8,968，unverified=1,578，duplicate_occurrences=0；record_changes/new_ids/removed_ids/source_registry_changes 均为0，warnings=0。仅预检，未写字段表。
- `audit_tables.py --strict-stage --summary` 退出码0：KU=1,361；alignment_new_pending_registration=4,587（候选映射4,572条／4,496组，外部身份记录15条）；`errors=[]`、`s2_missing=[]`；relations=1,227（formal=1,225）；candidate_backlog=3、pending=0。既有 `enr-06678`、`enr-06937` 来源引用警告和 S2 语义质量提示仍在；均非本批新增。


### S4 person：Roomer 商业网络与 Mazarin 对照组的人物端点登记（2026-10-17）

`cand-0914`→[Ferdinand van den Einden 卡](../../../04-knowledge/units/persons/ferdinand-van-den-einden.md)；`cand-0915`→[Jan van den Einden 卡](../../../04-knowledge/units/persons/jan-van-den-einden.md)；`cand-1347`→[Louis Phélipeaux de la Vrillière 卡](../../../04-knowledge/units/persons/louis-phelipeaux-de-la-vrilliere.md)。Ferdinand 与 Jan van den Einden 是两个独立 S3 人物组；正文称 Jan 为 Ferdinand 之父，并分别记述其与 Roomer 的关系。Louis Phélipeaux de la Vrillière 按书内全名登记为独立 source-local person，中文工作音译不作为规范身份依据。Ferdinand 的9条、Jan 的3条、Louis 的9条直接关系候选均留待 S6；Jan 的 Flemish-origin 句为1条非关系陈述。Mazarin 与 Gaspar Roomer 复用现有 KU；女儿群体 cand-11553、Chigi palace endpoint cand-6820 及 La Vrillière 绘画系列 cand-6846 维持 S3 undecided。候选 cand-7462（term）、cand-6826（work）、cand-6828（term）维持 S3 new，仍待 S4；本批未写 relations.csv。S4 累计登记345组/449条候选映射，待登记4,493组/4,569条；KU 总数1,364。

### S4 验证：van den Einden 与 La Vrillière 人物端点登记（2026-10-17）

- `cand-0914`、`cand-0915`、`cand-1347` 均保持各自 S3 `new-person` 组，分别映射到 Ferdinand、Jan 与 Louis Phélipeaux de la Vrillière 三张 person 卡；各卡已列入 `accepted.yml`，同组候选均只有一个 KU。Jan 与 Ferdinand 分别登记，父子关系仍是待 S6 候选。
- 书内直接陈述分区：Ferdinand 9条均为 relation_candidate；Jan 4条中3条为 relation_candidate、1条为非关系陈述；Louis 9条均为 relation_candidate。共21条关系候选留待 S6；未新增正式关系。
- 相关端点去向：Roomer、Mazarin 复用现有 KU；cand-11553（未具名女儿群体）、cand-6820（宫殿）、cand-6846（绘画系列）保留 S3 `undecided`；cand-7462、cand-6826、cand-6828 保持 S3 `new`、待 S4。
- `build_field_facts.py` 预检：cards=1,364，rows=10,476，unique_sources=1,716；records_with_source=8,968，unverified=1,578，duplicate_occurrences=0；record_changes/new_ids/removed_ids/source_registry_changes 均为0，warnings=0。仅预检，未写字段表。
- `audit_tables.py --strict-stage --summary` 退出码0：KU=1,364；alignment_new_pending_registration=4,584（候选映射4,569条／4,493组，外部身份记录15条）；`errors=[]`、`s2_missing=[]`；relations=1,227（formal=1,225）；candidate_backlog=3、pending=0。`enr-06678`、`enr-06937` 来源引用警告和 S2 语义质量提示仍在，均为既有项。


### S4 work/term：La Vrillière 与 van den Einden 的直接端点（2026-10-17）

`cand-6826` 登记为[Guido Reni《The Rape of Helen》作品卡](../../../04-knowledge/units/works/guido-reni-rape-of-helen.md)；它与既有 Pietro da Cortona 同题作品分开。`cand-6828` 登记为[La Vrillière 古代英雄题材术语卡](../../../04-knowledge/units/terms/la-vrilliere-heroic-antique-themes.md)，`cand-7462` 登记为[van den Einden 赞助的受威尼斯影响后辈画家术语卡](../../../04-knowledge/units/terms/later-painters-inspired-by-venetians-patronised-by-van-den-einden.md)。三者均依 S3 new 分组各登记一个 KU；两个 term 只记录 Haskell 的书内描述，不建立涌现层级、普遍类别或完整成员名单。三条直接关系候选留待 S6；La Vrillière palace `cand-6820` 与绘画系列 `cand-6846` 仍为 undecided，本批未写 relations.csv。S4 累计登记348组/452条候选映射，待登记4,490组/4,566条；KU 总数1,367。

### S4 验证：La Vrillière 与 van den Einden 的 work/term 端点登记（2026-10-17）

- `cand-6826`→`units/works/guido-reni-rape-of-helen`；`cand-6828`→`units/terms/la-vrilliere-heroic-antique-themes`；`cand-7462`→`units/terms/later-painters-inspired-by-venetians-patronised-by-van-den-einden`。三个 S3 new 组各有一个对齐候选、一个 manifest KU 和一张 accepted 卡。Guido Reni 作品与既有 Pietro da Cortona 同题作品按作者区分。
- 三条直接 S2 关系候选留待 S6；未新增正式边。`cand-6820` 宫殿与 `cand-6846` 绘画系列仍为 S3 `undecided`，没有因关联端点登记而改变。
- `build_field_facts.py` 预检：cards=1,367，rows=10,476，unique_sources=1,716；records_with_source=8,968，unverified=1,578，duplicate_occurrences=0；record_changes/new_ids/removed_ids/source_registry_changes 均为0，warnings=0。仅预检，未写字段表。
- `audit_tables.py --strict-stage --summary` 退出码0：KU=1,367；alignment_new_pending_registration=4,581（候选映射4,566条／4,490组，外部身份记录15条）；`errors=[]`、`s2_missing=[]`；relations=1,227（formal=1,225）；candidate_backlog=3、pending=0。既有两条 enrichment source_ref 警告及 S2 语义质量提示继续保留，均非本批新增。


### S4 person：Marco Sacconi 跨页人物组登记（2026-10-17）

`cand-2325`（S.csv#13，页码233、240）保持 S3 source-local 人物组 `new-person:marco-sacconi-334444e5e2`，登记为[Marco Sacconi 人物卡](../../../04-knowledge/units/persons/marco-sacconi.md)。正文两页仅以 Sacconi 指称，索引给出 Marco 全名；未用外部身份扩展书内资料。8条直接 relation_candidate 留待 S6，3条颜色、成效和幽默评价保持非关系陈述。Ferdinand de’ Medici、Niccolò Cassana 与 Venice 均复用已有 KU；本轮未写 relations.csv。S4 累计登记349组/453条候选映射，待登记4,489组/4,565条；KU 总数1,368。

### S4 验证：Marco Sacconi 人物组登记（2026-10-17）

- `cand-2325` 保持 `new-person:marco-sacconi-334444e5e2`，映射到 `units/persons/marco-sacconi`；manifest、card、accepted.yml 对齐。正文 pp.233、240 仅用 Sacconi，索引 S.csv#13 提供 Marco 全名及两处定位；本轮未添加外部身份来源。
- 11条直接 S2 陈述分为8条 relation_candidate 和3条评价性非关系陈述；关系候选留待 S6。Grand Prince Ferdinand de’ Medici、Niccolò Cassana 与 Venice 均指向现有 KU；未新增正式关系。
- `build_field_facts.py` 预检：cards=1,368，rows=10,476，unique_sources=1,716；records_with_source=8,968，unverified=1,578，duplicate_occurrences=0；record_changes/new_ids/removed_ids/source_registry_changes 均为0，warnings=0。仅预检，未写字段表。
- `audit_tables.py --strict-stage --summary` 退出码0：KU=1,368；alignment_new_pending_registration=4,580（候选映射4,565条／4,489组，外部身份记录15条）；`errors=[]`、`s2_missing=[]`；relations=1,227（formal=1,225）；candidate_backlog=3、pending=0。两条既有 enrichment source_ref 警告及 S2 语义质量提示继续保留。


### S3–S4：Della Lena 跨章人物组及相关文献端点（2026-10-17）

S3 将 `cand-11152`（后记 p.410 “Abate Della Lena”）并入 `cand-1387` 的 `new-person:della-giacomo-lena-0fb3da9b14`。身份依据是第16章 p.375 的全名、题名与作者关系，以及后记 p.410 对同一题名 treatise 的再次指称；不是姓氏匹配。原组 `new-person:della-lena-718aef6568` 及其原始名称锚点理由保留在 `cand-11152` alignment 历史字段。另核对 Ortes：第10章注释中的 ‘Abate Ortes’ 与第16章 p.375 的 ‘Giuseppe Maria Ortes’ 由书后索引交叉定位；索引Markdown首个定位转录为 ‘32m’，候选记录为 ‘321n’，页码差异保留待核。S3 明确保留：`cand-10623`（32幅 Guardi 绘画集合）、`cand-10627`（未具名西班牙大使）与 `cand-1709`（Moschini 姓名形式不足）为 `undecided`；未知历史学家不另造人物候选。`cand-1454` Lucca、`cand-2719` Venice、`cand-1239` Francesco Guardi 与 `cand-8262` Biblioteca Correr 分别复用已有 KU。新登记5个 KU：人物 Giacomo della Lena（`cand-1387`、`cand-11152` 同组）、Innocenzo della Lena（`cand-1389`）、Giuseppe Maria Ortes（`cand-1789`）；archive 文献文本（`cand-10622`）与 Correr 手稿定位组（`cand-10625`）各自保留独立身份。所有直接关系候选及文献内容断言留待 S6；未改写 `relations.csv`。Giacomo 的两条评价/观点陈述维持非关系分类。S4 累计登记354组/459条候选映射，待登记4,483组/4,559条；KU 总数1,373。

### S3–S4：Grimaldi 跨章人物组与 Mazarin 画廊地点（2026-10-17）

S3 复核 `cand-1232`：索引 G.csv#142 以 Giovanni Francesco Grimaldi 汇集第2章 p.57、第6章 p.155、第7章 pp.182–183、191；正文p.155的 ‘Gianfrancesco’ 由索引同条目和相邻语境支持为同一书内人物。索引转录末尾 ‘lyi’ 保留，正文 p.191 有全名定位。该人物无同类型既有KU，按现行 new 组登记。`cand-1231`（Angelica Griè）仍因索引页212n无正文提及而 undecided，不并入 Grimaldi。`cand-6784` 未列成员的意大利艺术家集合、`cand-6803` 未定位的耶稣会神学院、`cand-6959` 三处未定位画家工作室均保留 undecided。`cand-6781` 为 Mazarin 宫殿上层画廊这一内部 place；图版目录将相关天花板作品定位于 Bibliothèque Nationale（formerly Palais Mazarin），故不与整座 Palais Mazarin（cand-3946）或顶画（cand-4090）合并。人物 `cand-1232` 与画廊 `cand-6781` 分别登记；Romanelli、Rospigliosi、Colonna family palace、Palais Mazarin、顶画复用已有 KU。4条 Grimaldi 和6条画廊直接 relation_candidate 全部留待 S6；一条 landscape artist 属性维持非关系。`relations.csv` 未改。S4 累计登记356组/461条候选映射，待登记4,481组/4,557条；KU 总数1,375。

### S3 跨章身份复核：Sir Anthony Blunt 复用既有人物卡（2026-10-17）

候选 `cand-0379`（B.csv#226，索引形式 ‘Blunt, Sir Anthony’）与 `cand-5902`（正文注释形式 ‘Sir Anthony Blunt’）原作为同一新人物组 `new-person:anthony-blunt-anthony-blunt-opinion-s-c8c64cf49b`。核对发现既有[Anthony Frederick Blunt 人物卡](../../../04-knowledge/units/persons/anthony-blunt.md)已明确记录全名、惯用名 ‘Anthony Blunt’ 与称号 ‘Sir’；候选 `cand-3722` 也已映射到该 KU。两条决定据此从 `new` 更正为 `same`，均映射至 `units/persons/anthony-blunt`；旧组 token 与逐行原理由保留在 `prior_group`/`prior_resolution_note` 字段。一条关于 Blunt 解释 Canaletto 日期的陈述为非关系；p.57 对其 Four Evangelists 系列假说的 statement 保持 relation_candidate，留待 S6。未新建 KU、未改 relations.csv。修正后 S3 same=1,784条、new=5,016条/4,836组；S4 已登记356组/461条映射，待登记4,480组/4,555条；KU 总数1,375。

### S3–S4 类型边界修正：Jacopo Bassano 与 Nativity 作品端点（2026-10-17）

S3 复核人物候选 `cand-0257`（B.csv#104）与 `cand-0258`（B.csv#105）：两条索引行的规范姓名均为 Jacopo Bassano，#105 的 ‘Nativity’ 是作品子项；人物组 `new-person:bassano-jacopo-0104694cf4` 保持不变，登记为一张人物卡。发现 `st-chp10-p313-guardi-copied-bassano-nativity` 原将绘画名称 ‘Bassano’s Nativity’ 的 object 指向人物候选 `cand-0258`。现以新工作候选 `cand-12428` 区分对象，`m-s2-ch10-p313-0019` ‘Bassano’ 保留人物映射，`m-s2-ch10-p313-0020` ‘Nativity’ 改映射至作品；断言 object 与 mentioned_candidate_ids 同步更正。该 work 按 source-local new 身份经 candidate-backlog bl-0004 走 S1→S3→S4，登记为第二张 KU 卡。原文没有 Guardi 临摹件的具体版本/日期，故不另建副本对象。两条直接关系候选（Bassano 的艺术先例；Guardi 受命临摹此作品）留待 S6；本轮未写正式关系。S4 累计登记358组/464条候选映射，待登记4,479组/4,553条；KU 总数1,377。

### S3 跨章身份复核：Pompeo Batoni 复用既有人物 KU（2026-10-17）

`cand-0260`（B.csv#107）、`cand-0261`（B.csv#108，子目 Cleopatra）与 `cand-0262`（B.csv#109，子目 Triumph of Venice）原共属新人物组 `new-person:batoni-pompeo-e737feffb7`。既有[Pompeo Girolamo Batoni 人物卡](../../../04-knowledge/units/persons/pompeo-batoni.md)明确记录全名 Pompeo Girolamo Batoni、惯用名 Pompeo Batoni；全书前置候选 `cand-3871` 已映射至 `units/persons/pompeo-batoni`。索引三条均是同一画家名下的作品定位；规范化索引源记录主项 p.259，Chapter 22 OCR 转录为 p.239 的差异保留待核。第9章 p.259 明称 Pompeo Batoni，第10章 p.298 与第14章 p.357 的 Cleopatra 比较/建议语境及第17章 p.381 对已述《Triumph of Venice》的回指相容。三条决定从 `new` 更正为 `same`，并入既有组 `sg3-ku-units-persons-pompeo-batoni`、映射至 `units/persons/pompeo-batoni`；旧组号及每条原理由保留于 alignment 的 prior_group/prior_resolution_note。本轮不改人物卡、manifest、S2 断言或 relations.csv；作品及提案关系候选仍按原状态留待 S6。修正后 S3 same=1,787条、new=5,014条/4,836组；S4 已登记358组/464条映射，待登记4,478组/4,550条；KU 总数1,377。

### S4 person：Abbate Michele Giustiniani 跨章人物组登记（2026-10-17）

人物组 `new-person:abbate-giustiniani-michele-496853d11b` 包含 `cand-1199`（G.csv#106，索引定位 p.94n）与 `cand-4388`（第2章 p.31 注5正文来源候选），登记为一张[人物卡](../../../04-knowledge/units/persons/abbate-michele-giustiniani.md)。索引形式为 ‘Giustiniani, Abbate Michele’；原书第2章以 ‘Abbatc Michele Giustiniani’（OCR字形）称其为一封信的刊布者，第4章注释称 ‘Abate Michele Giustiniani’ 于1675年首次刊布另一封信，第4、6章注文以 ‘Abbate Michele Giustiniani’ 引用卷册I–III。姓名、头衔词形与跨章引用语境支持同一书内人物；不推定完整生平。仅将人物候选登记至 `units/persons/abbate-michele-giustiniani`。第2、4、6章被引的 volume I/II/III 书目对象不并入人物卡；archive 候选 `cand-4389`、`cand-5963`、`cand-5504` 继续 `undecided`，因为完整题名、版本及卷册间关系尚未确定。相关 S2 statements 均为非关系引用陈述，本轮未新增 `relations.csv` 边，也未添加 backlog 行。候选 `cand-4388` 的旧 detail 将身份和书目缺口混写；现修正为身份已对齐、卷册书目仍待证，旧文字保存在 alignment 历史说明中。S4 累计登记359组/466条候选映射，待登记4,477组/4,548条；KU 总数1,378。

### S3–S4 本轮验证汇总（2026-10-17）

- `audit_tables.py --strict-stage --summary` 退出码0：KU=1,378；candidates=12,406；alignments=12,632、unlinked=0；`s2_missing=[]`、`errors=[]`。当前 S3 same=1,787，new=5,014/4,836组；S4 已登记359组/466条候选映射，待登记4,477组/4,548条；另有15条外部身份记录处于 new alignment 待登记。candidate-backlog=4、pending=0；relations=1,227（formal=1,225），本轮未改 `relations.csv`。
- `build_field_facts.py --apply` 为新人物卡的两条名称字段新增2条 enrichment；随后只读预览 `record_changes=0`、`new_ids=0`、`removed_ids=0`、`source_registry_changes=0`、`warnings=0`。
- 按 S3 收口标准直接对照 `entity-candidates.csv` 与非 external `alignment.csv`：12,406 个候选对应12,406条裁决行；缺裁决、重复裁决、无 `resolution_note`/`process_ref`、非法 `decision` 均为0。分布为 same=1,787、new=5,014、conflict=8、excluded=100、undecided=5,497；undecided 保持显式待证去向，不宣称身份已查明。
- Bassano work candidate `cand-12428` 的 candidate_source_ref、alignment 和 backlog 已统一至 source line 74；`audit_tables.py` 不再报来源定位错误。Batoni 三条索引候选复用既有人物 KU；Giustiniani 两条人物候选登记至同一卡，卷册 archive 候选 `cand-4389`、`cand-5963`、`cand-5504` 仍为 `undecided`。新卡内部来源链接逐项存在。
- `git diff --check` 退出码0；仅见现有 LF/CRLF 转换提示。严格审计仍提示4,563条 new alignment 待 S4、既有 `enr-06678` 与 `enr-06937` 的 `source_ref` 未能从对应卡片来源清单解析，以及 S2 语义审查质量需继续按过程记录核查；这些提示不由本轮新增。


### S4 person：Giuseppe Toninotto 直接关系端点登记（2026-10-17）

候选 `cand-2643`（T.csv#106）保持 S3 人物组 `new-person:giuseppe-toninotto-7d1c034d26`，登记至[朱塞佩·托尼诺托人物卡](../../../04-knowledge/units/persons/padre-giuseppe-toninotto.md)，一组一 KU。第16章 p.376 明称其为 Dominican Padre Giuseppe Toninotto；规范化索引以反序形式列出 Toninotto, Padre Giuseppe。当前 accepted/manifest 中无同类型同一人物卡，本轮只登记书内身份，不补充外部生平或身份标识。该人作为主体的8条 S2 relation_candidate 原样保留：Frari 导览、宗教裁判所处分、1785年版画出版、两件 della Vecchia 作品、Zais 绘画与素描、Guardi 绘画、四件 capricci、四幅威尼斯风景。后四个作品端点 `cand-10637`–`cand-10640` 及 `cand-10646` 当前为 `undecided`；Frari `cand-10642`、State Inquisition `cand-10524` 与 del Pian 版画 `cand-10636` 仍是 S3 `new`、待各自 S4。因对象端点未全部登记或消歧，本轮未写正式关系，未新加 backlog 行。S4 累计登记360组/467条候选映射，待登记4,476组/4,547条；KU 总数1,379。

<a id="s4-antonio-zanchi"></a>

### S4 person/work：Antonio Zanchi 与《Moses striking the Rock》（2026-10-17）

人物候选 `cand-2834` 保持 S3 组 `new-person:antonio-zanchi-df48b8d0ff`，登记至[Antonio Zanchi 人物卡](../../../04-knowledge/units/persons/antonio-zanchi.md)。第8章 p.218 L84 明称 Antonio Zanchi；索引主项 UVWXYZ.csv#171 汇集 p.218、251、294，分别对应第8章委托叙述、第9章画家声望叙述与第10章 Negri 师承句。人物卡只登记书内身份与所载语境，不补充外部生平。

作品候选 `cand-2835`（索引 UVWXYZ.csv#172）与 `cand-7670`（第8章正文）保持同一 S3 组 `workgrp-09d947ea36bdd8`，登记至[作品卡](../../../04-knowledge/units/works/antonio-zanchi-moses-striking-rock-bergamo.md)。索引题名、p.218–219 的 Antonio Zanchi 委托叙事、Bergamo 的 S. Maria Maggiore 页面定位及付款条目相互吻合；原书未说明原定安装的具体墙面或作品后续去向。索引另有归于 Ottavio Vannini 的 p.212 同题画作，未与本对象合并。

人物直接关系候选（8条）：st-chp8-p218-letters-urge-zanchi-to-hurry, st-chp8-p218-zanchi-agrees-to-terms, st-chp8-p218-zanchi-canvas-completed-four-months, st-chp8-p218-zanchi-canvas-sent, st-chp8-p218-zanchi-described-as-venetian, st-chp8-p218-zanchi-no-fee-and-return-terms, st-chp8-p218-zanchi-receives-825-ducats, st-chp8-p218-zanchi-site-visit-and-venice-permission。作品直接关系候选（7条）：st-chp8-p218-committee-accepts-zanchi-canvas, st-chp8-p218-committee-deliberates-on-zanchi-canvas, st-chp8-p218-experts-set-price-if-accepted, st-chp8-p218-zanchi-canvas-completed-four-months, st-chp8-p218-zanchi-canvas-sent, st-chp8-p218-zanchi-receives-825-ducats, st-chp8-p218-zanchi-selected-for-moses-rock。两集合共有画布递送、完成、付款等交叠叙述；全部留待 S6 逐条审查，本轮未写 `relations.csv`，未新增 backlog。S4 累计登记362组/470条候选映射，待登记4,474组/4,544条；KU 总数1,381。

### S3–S4 本批验证汇总（2026-10-17）

- `audit_tables.py --strict-stage --summary` 退出码0：KU=1,381；candidates=12,406；alignments=12,632、unlinked=0；`s2_missing=[]`、`errors=[]`。S4 已登记362组/470条候选映射，待登记4,474组/4,544条；另有15条外部身份记录处于 `decision=new` 待登记。candidate-backlog=4、pending=0；relations=1,227（formal=1,225）。
- S4 映射复核：人物 `cand-2834`→`units/persons/antonio-zanchi`；作品 `cand-2835`、`cand-7670`→`units/works/antonio-zanchi-moses-striking-rock-bergamo`。两张卡 YAML 可解析，双语标题/描述齐全，6条卡片来源记录均指向现存来源文件；过程引用使用稳定锚点 `#s4-antonio-zanchi`。
- `build_field_facts.py --apply` 为两张卡新增4条字段记录；随后预览 `record_changes=0`、`new_ids=0`、`removed_ids=0`、`source_registry_changes=0`、`warnings=0`。字段表为10,485条，其中1,587条 `unverified`。
- 两组分别关联8条人物、7条作品 S2 relation_candidate，交叠后共12条不同 statement；statement 与 `relations.csv` 均未改写，正式关系仍待 S6。`git diff --check` 退出码0；仅见工作区既有 LF/CRLF 转换提示。审计保留两条既有 source_ref 提示及 S2 语义质量提示。


<a id="s4-charles-ii"></a>

### S4 person：Charles II of England 跨章身份组（2026-10-17）

候选 `cand-0656` 保持 S3 组 `new-person:charles-england-ii-of-fba89bfc00`，登记至[查理二世人物卡](../../../04-knowledge/units/persons/charles-ii-of-england.md)。第7章 p.178 L111 称 Charles, Prince of Wales，并以 young Prince 指称；同章 p.195 明称 Charles II 于1660年即位，p.196 再称 King Charles II。书后索引 C.csv#180 汇集 p.195–196。将早年王储称谓与后来的国王视为同一人物，依据是书内称谓与索引定位的延续，不扩展为书外生平或生卒年。

8条直接 S2 relation_candidate 保持原状：st-chp7-p178-i21, st-chp7-p195-arlington-introduced-verrio, st-chp7-p195-charlesii-motive, st-chp7-p195-charlesii-no-contemporary-italian-interest, st-chp7-p195-charlesii-recovers-pictures, st-chp7-p195-verrio-employed-by-charlesii, st-chp7-p196-gennari_salary_and_commissions, st-chp7-p196-sea-triumph-description。本轮未写 `relations.csv`，未新增 backlog。S4 累计登记363组/471条候选映射，待登记4,473组/4,543条；KU 总数1,382。

### S3–S4 本批验证汇总（2026-10-17；Zanchi 与 Charles II）

- `audit_tables.py --strict-stage --summary` 退出码0：KU=1,382；candidates=12,406；alignments=12,632、unlinked=0；`s2_missing=[]`、`errors=[]`。S4 已登记363组/471条候选映射，待登记4,473组/4,543条；另有15条外部身份记录处于 `decision=new` 待登记。candidate-backlog=4、pending=0；relations=1,227（formal=1,225）。
- Charles II 人物卡 YAML、双语描述、4条来源记录、链接和 `#s4-charles-ii` 锚点均核对通过；`cand-0656` 保持 new 并映射至该卡。Zanchi 人物/作品与 Charles II 三张卡的来源文件及卡内链接均可解析，3个身份组共4个候选映射对应3个 KU。
- Charles II 卡经 `build_field_facts.py --apply` 新增4条字段记录；最终预览 `record_changes=0`、`new_ids=0`、`removed_ids=0`、`source_registry_changes=0`、`warnings=0`。字段表10,489条，其中1,591条 `unverified`。
- 8条 Charles II S2 relation_candidate 保持原状；`relations.csv` 未改。`git diff --check` 退出码0；仅有既有 LF/CRLF 转换提示。严格审计保留4,558条 S4 待登记 alignment 警告、两条既有 source_ref 提示和 S2 语义质量提示。


<a id="s3-capuchin-church-rome"></a>

### S3 更正：S. Maria della Concezione 复用既有罗马嘉布遣会教堂 KU（2026-10-17）

复核发现，第2章 p.42 正文候选 `cand-4521` 曾因“暂与既有罗马嘉布遣会教堂区分”的待核说明而登记为 `new`；索引候选 `cand-0708`（C.csv#232，子目 S. Maria della Concezione，pp.42–43）曾因缺少正文对应而列为 `undecided`。当前读取的第2章来源明确称 Urban VIII 与 Antonio Barberini 所涉地点为 S. Maria della Concezione，并称 Antonio 为嘉布遣会建立新教堂及修道院，位于 Pincio；索引页码正对应该段。

已有 `units/places/capuchin-church-rome` 是同类型、已接受地点卡。卡片记录第1章 p.12 的 “Capuchin church in Rome”，并将其身份对应至 Santa Maria della Concezione dei Cappuccini。Treccani《意大利人传记辞典》第89卷 Andrea Sacchi 条列明 Sacchi 为 S. Maria della Concezione 绘制公共祭坛画；[Treccani DBI “SACCHI, Andrea”](https://www.treccani.it/enciclopedia/andrea-sacchi_%28Dizionario-Biografico%29/)（访问于2026-10-17）可复核这一地点名称。结合 Haskell 第1章与第2章的类型、城市和修会语境，p.42 的具名教堂与既有 KU 为同一地点。不是把教堂与修道院合并；`cand-4522` 修道院、index-only 的其他候选继续按各自状态处理。

现将 `cand-4521` 由 `new` 更正为 `same`，将 `cand-0708` 由 `undecided` 更正为 `same`，两者均映射至 `units/places/capuchin-church-rome`；原决定、组号及完整理由保存在 alignment 的 `prior_decision`、`prior_group` 与 `prior_resolution_note` 文本中。该变更不新增 KU、manifest/accepted 条目或关系；10条直接 S2 关系候选保持原状。S3 same=1,789、new=5,013/4,835组、conflict=8、excluded=100、undecided=5,496。S4 已登记363组/471条映射，待登记4,472组/4,542条；KU 总数1,382。

### S3–S4 本批验证汇总（2026-10-17；Capuchin Church 对齐更正）

- `audit_tables.py --strict-stage --summary` 退出码0：KU=1,382；candidates=12,406；alignments=12,632、unlinked=0；`s2_missing=[]`、`errors=[]`。candidate-backlog=4、pending=0；relations=1,227（formal=1,225）。
- 对12,406个候选逐行复核后均有唯一 alignment、合法决定、`resolution_note` 与 `process_ref`；当前 same=1,789/1,027既有KU、new=5,013/4,835组、conflict=8、excluded=100、undecided=5,496。same/new 组与 KU 汇总一致。`cand-0708`、`cand-4521` 的 prior 决定及原理由均保留，复用目标存在于 manifest 与 accepted.yml。
- `build_field_facts.py` 预览无变化：10,489条、1,591条 `unverified`，`record_changes=0`、`new_ids=0`、`removed_ids=0`、`source_registry_changes=0`、`warnings=0`。本轮未修改既有 KU 卡、manifest、accepted.yml、字段表或 `relations.csv`。
- 仍待 S4 登记4,472组/4,542条候选映射，外加15条外部身份 alignment。严格审计保留两条既有 source_ref 提示与 S2 语义质量提示；`git diff --check` 退出码0，仅有 LF/CRLF 转换提示。


<a id="s4-accademia-dei-lincei"></a>

### S4 institution：Accademia dei Lincei（林琴科学院）身份组登记（2026-10-17）

cand-0003（A.csv#2；S3 组 sg3-institution-cand-0003）映射至[机构卡](../../../04-knowledge/units/institutions/accademia-dei-lincei.md)。索引主项同一行定位第2章 p.33 与第4章 p.99；前者将该学院置于罗马科学实验语境，后者脚注99再次使用完整名称并以 the Accademia、the Lincei 指称。没有同类型既有 KU，按 S3 的 new 决定登记一个机构 KU。中文显示名为项目工作译名；书内“欧洲科学社团先驱”保留为 Haskell 的比较性表述，不扩写为已核实的制度传承，也不延伸到后来的同名机构。8条直接 relation_candidate 保持待 S6 审查：st-chp4-sec-ii-l232-308-cassiano-admitted-to-lincei, st-chp4-sec-ii-l232-308-cesi-identified-as-founder, st-chp4-sec-ii-l232-308-clerical-patronage-and-church-conflict, st-chp4-sec-ii-l232-308-heresy-charges-and-attacks-left-lincei-firm, st-chp4-sec-ii-l232-308-lincei-described-as-scientific-ancestor, st-chp4-sec-ii-l232-308-lincei-disintegrated-after-cesi-death, st-chp4-sec-ii-l232-308-lincei-membership-rule, st-chp4-sec-ii-l232-308-lynx-metaphor-and-suppression。本轮未写 relations.csv、未登记正式关系，未改 sources.csv。S4 累计登记364组/472条候选映射；待登记4,471组/4,541条；KU 总数1,383。

### S4 登记后检查：Accademia dei Lincei（2026-10-17）

- audit_tables.py --strict-stage --summary 退出码0：KU=1,383；candidates=12,406；alignments=12,632、unlinked=0；errors=[]；relations=1,227（formal=1,225）。待登记 S4 alignment 共4,556条，包括4,541条候选映射（4,471组）及15条外部身份记录；另有两条既有 source_ref 警告和 S2 语义质量提示。
- build_field_facts.py --apply 登记本卡新增6条字段事实；随后预览无变化：10,495条记录、1,597条 unverified，record_changes=0、new_ids=0、removed_ids=0、source_registry_changes=0、warnings=0。sources.csv 无逻辑变化。
- 本卡 YAML 可解析、来源与本地链接均可解析，候选 cand-0003 只有一条 alignment 并映射至单位卡。8条直接 relation_candidate 均保持原标记；relations.csv 未改。
- git diff --check 退出码0；仅有工作区 LF/CRLF 转换提示。

<a id="s4-manin-palace-venice"></a>

### S4 place：Manin Palace, Venice（马宁宫殿）身份组登记（2026-10-17）

cand-1520（M.csv#57；S3 组 sg3-place-cand-1520）映射至[地点卡](../../../04-knowledge/units/places/manin-palace-venice.md)。索引列名 Manin palace、城市 Venice 与第251页定位；正文称其为 Manin 家族大运河宫殿，注3所引1708年通信题名写 Palazzo di S.E. il Signor Co: Manin in Venezia。书中另有 Passeriano 乡间宅邸，本卡明确与之及 Manin family 区分；不推定现存状态或精确地址。9条直接 relation_candidate 留待 S6：st-chp9-p251-cignani-and-mazza, st-chp9-p251-gallery-andrea-del-sarto-pictures, st-chp9-p251-gallery-giovanni-da-udine-pictures, st-chp9-p251-gallery-sansovino-bronzes, st-chp9-p251-gallery-works, st-chp9-p251-manin-style-at-palace, st-chp9-p251-mazza-marble-venus, st-chp9-p251-palace-hangings-tapestries, st-chp9-p251-palace-mirrors。palace description 与 decoration exceeded expectations 两条 statement 维持非关系分类。本轮未写 relations.csv、未登记正式关系，未新增 sources.csv 记录。S4 累计登记365组/473条候选映射；待登记4,470组/4,540条；KU 总数1,384。

### S4 登记后检查：Manin Palace（2026-10-17）

- audit_tables.py --strict-stage --summary 退出码0：KU=1,384；candidates=12,406；alignments=12,632、unlinked=0；errors=[]；relations=1,227（formal=1,225）。待登记 S4 alignment 为4,555条，含4,540条候选映射（4,470组）及15条外部身份记录；两条既有 source_ref 警告与 S2 语义质量提示继续保留。
- build_field_facts.py --apply 新增本卡9条字段事实；之后预览无变化：10,504条、1,606条 unverified，record_changes=0、new_ids=0、removed_ids=0、source_registry_changes=0、warnings=0。sources.csv 无逻辑变化。
- Manin Palace 卡 YAML、来源及本地链接均通过核对；cand-1520 只有一条 alignment，映射至地点 KU。9条直接 relation_candidate 和2条直接非关系 statement 均保持原状态；relations.csv 未改。
- git diff --check 退出码0；仅见工作区 LF/CRLF 转换提示。

<a id="s3-borghese-palace-identity"></a>

### S3 更正：Borghese Palace 与既有 Bentivoglio/Mazarin 宫殿为同一地点（2026-10-17）

候选 cand-0398（B.csv#245，印刷页49）原判 new，组 sg3-place-cand-0398。复核第2章 p.49：Haskell 将其称为 Quirinal 上的 great Borghese palace，称 Enzo Bentivoglio 于1619年购入；第2章注1记载 Bentivoglio 于1619年从 Altemps 家族购得该宫殿。正文随后明确称 Bentivoglio 将这座宫殿售予 Lante 家族，后由 Cardinal Mazarin 购得。第7章 p.183 注2以相同次序记载 Mazarin 从 Lante 购入、Lante 从 Bentivoglio 取得。既有 units/places/mazarin-bentivoglio-palace-rome 卡已记录 Bentivoglio → Lante → Mazarin 的同一转手链，并将对象类型定为 Rome 的宫殿建筑。两处证据在地点、建筑类型、所有权转移顺序和跨章互引上吻合，故 cand-0398 与已登记 cand-6796 指向同一宫殿；不是另一座 Borghese 建筑。Villa Borghese 仍为不同地点。现将 cand-0398 从 new 更正为 same，映射至 units/places/mazarin-bentivoglio-palace-rome；S3 原决定、原组及原始 resolution_note 完整保存在 alignment 的 prior_decision、prior_group 与 prior_resolution_note 文本中。8条 cand-0398 直接 relation_candidate 保持原端点与分类；relations.csv、KU manifest、accepted.yml 均无需改动。S3 same=1,790（1,028个既有KU）、new=5,012/4,834组、conflict=8、excluded=100、undecided=5,496。S4 已登记365组/473条映射，待登记4,469组/4,539条；KU 总数1,384。

<a id="s4-stoicism"></a>

### S4 term：Stoicism in 17th century 术语组登记（2026-10-17）

cand-2510（S.csv#199；S3 组 sg3-term-cand-2510）映射至[斯多葛主义术语卡](../../../04-knowledge/units/terms/stoicism-seventeenth-century.md)。第5章 pp.143–144 的正文与注释讨论该哲学在 Haskell 所述历史中的传播、伦理／图像影响及 Rosa 的相关实践；索引主项限定页段。卡片保留作者解释与 some daring thinkers 限定，不将局部叙述扩展成全面哲学史；关于 Rosa 1651年自称 Stoic 的内容只按 Haskell 注2转述，不称已独立核读原信。9条直接 relation_candidate 保持待 S6 审查：st-chp5-p143-rosa-quotation-alludes-to-stoicism, st-chp5-p143-rosa-stoic-roast-meat-letter, st-chp5-p143-rosa-studied-stoics-for-art-themes, st-chp5-p143-stoicism-appealed-to-the-disappointed, st-chp5-p143-stoicism-colored-ethics-and-imagery, st-chp5-p143-stoicism-gained-ground-in-europe, st-chp5-p143-stoicism-virtually-replaced-christianity, st-chp5-p144-regulus-raised-small-picture-idiom-to-heroic-tragedy, st-chp5-seciv-note-l41-p143-rosa-described-himself-as-stoic。本轮未写 relations.csv、未登记正式关系，未新增 sources.csv 记录。S4 累计登记366组/474条候选映射；待登记4,468组/4,538条；KU 总数1,385。

<a id="s4-maria-mancini"></a>

### S4 person：Maria Mancini 直接关系端点登记（2026-10-17）

候选 `cand-1509`（M.csv#46）保持 S3 `new` 身份组 `new-person:mancini-maria-652896852a`，映射至[玛丽亚·曼奇尼人物卡](../../../04-knowledge/units/persons/maria-mancini.md)；该组仅含此一条人物候选，同组登记一个 KU。第6章 p.155 L106 明称 Maria Mancini，交代她与 Lorenzo Onofrio 于1661年结婚，并称她是 Cardinal Mazarin 的 niece、Louis XIV 的 first love；p.155 L106–107 描述其抵达罗马后的社会处境。第6章 p.156 L116–117 记 Haskell 所述的 ‘separatione di letto’ 要求及她于1672年离开丈夫；书后索引 M.csv#46 以 Mancini, Maria 定位 p.155。原书称 niece，但未说明亲属支系；本卡不推定该支系，不补出生、死亡或外部生平。Giulio Mancini 等其他同姓人物保持分立。7条直接 relation_candidate 原样保留待 S6：st-chp6-p155-lorenzo-maria-marriage, st-chp6-p155-maria-first-love-of-louis-xiv, st-chp6-p155-maria-impression-of-palace, st-chp6-p155-maria-niece-of-mazarin, st-chp6-p155-maria-social-position, st-chp6-p156-infidelities-lead-to-departure, st-chp6-p156-maria-separation-demand。本轮未写 relations.csv、未新增 enrichment 字段事实或 sources.csv 记录。S4 累计登记367组/475条候选映射；待登记4,467组/4,537条；KU 总数1,386。

### S4 person 批次：直接关系端点（2026-10-17）

#### Giovanni Angelo Canini（乔瓦尼·安杰洛·卡尼尼）

候选 `cand-0530`（C.csv#54；索引定位 154, 161, 187n, 197n）保持 S3 `new` 组 `new-person:angelo-canini-giovanni-adbabef3e8`，单候选映射至[人物卡](../../../04-knowledge/units/persons/giovanni-angelo-canini.md)；同组只登记一个 KU。书内主要证据与身份边界：第6章 p.154 以 Giovanni Angelo Canini 称其随 Cardinal Flavio Chigi 到 Paris 绘写场景；第6章 p.161 使用 Gianangelo Canini，并将其置于 Domenichino 学生、Bellori protégé 的语境。索引 C.csv#54 将其定位至 p.154、161、187n、197n；第7章 p.197 注2把 Thomas Killigrew 肖像归给 Canini 并记为1651年，但所引 Vertue 未独立核读。此卡只登记书内全名及同一索引组中的姓名形式，不把待审关系候选转为正式关系。 5条直接 relation_candidate 原样保留待 S6：st-chp6-p154-canini-and-gaulli-palace-works, st-chp6-p161-canini-faithful-pupil-of-domenichino, st-chp6-p161-canini-protege-of-bellori, st-chp6-p161-christina-patronizes-canini-with-bellori-guidance, st-chp7-p197-n2-killigrew-portrait。不将候选关系写入 relations.csv；未新增 enrichment 字段事实或 sources.csv 登记。

#### John Sheffield（约翰·谢菲尔德）

候选 `cand-0465`（B.csv#313；索引定位 280, 281）保持 S3 `new` 组 `new-person:buckingham-john-of-sheffield-7b3adca9be`，单候选映射至[人物卡](../../../04-knowledge/units/persons/john-sheffield-duke-of-buckingham.md)；同组只登记一个 KU。书内主要证据与身份边界：第10章以 John Sheffield 全名称其为 Buckingham 公爵，并将其任爵起点记为1703年；同段说他是 Bellucci 的早期赞助人之一，且此前已雇用 Sebastiano Ricci。第281页记 Haskell 所述其在女王去世后退出政坛、当时67岁。本卡以书内全名和头衔为身份依据，不将未具名的第三任妻子另行识别，也不把候选关系登记为正式边。 7条直接 relation_candidate 原样保留待 S6：st-chp10-p280-bellucci-patron-sheffield-also-employed-ricci, st-chp10-p280-sheffield-description-open, st-chp10-p280-sheffield-supported-jamesii, st-chp10-p280-sheffield-third-wife-jamesii-daughter, st-chp10-p280-sheffield-title-house-politics, st-chp10-p281-sheffield-ceiling-description, st-chp10-p281-sheffield-favourite-anne。不将候选关系写入 relations.csv；未新增 enrichment 字段事实或 sources.csv 登记。

#### Giacomo Serra（贾科莫·塞拉）

候选 `cand-2420`（S.csv#108；索引定位 70, 71）保持 S3 `new` 组 `new-person:giacomo-mgr-serra-5c15ad9cae`，单候选映射至[人物卡](../../../04-knowledge/units/persons/giacomo-serra.md)；同组只登记一个 KU。书内主要证据与身份边界：第3章 p.70 以 Monsignor Giacomo Serra 全名介绍人物，并称他积极推动年轻画家 Peter Paul Rubens 获得奥拉托利会祭坛画委托，愿意承担300 scudi。第71页记其以撤回资助相劝，神父们随后勉强接受条件。第70页注3另称 Serra 是年轻 Guercino 的赞助人，但 Haskell 引用的 Mahon 尚未独立核读。本卡只据书内姓名与语境登记此人物，不补外部生平。 5条直接 relation_candidate 原样保留待 S6：st-chp3-secii-l144-179-serra-threat-reluctant-agreement, st-chp3-secii-l54-60-conditional-300-scudi-offer, st-chp3-secii-l54-60-serra-anxious-to-promote-rubens, st-chp3-secii-l54-60-serra-approached-oratorians-in-crisis, st-chp3-secii-p70-note3-serra-guercino-patronage。不将候选关系写入 relations.csv；未新增 enrichment 字段事实或 sources.csv 登记。

本批没有外部身份记录；所引 Haskell 脚注中的 Pascoli、Vertue、Mahon 等材料未独立核读。Canini 的 Giovanni Angelo / Gianangelo 拼写按同一索引主项及正文语境登记；未按姓氏合并其他人。Sheffield 的未具名第三任妻子不另造人物；Serra 的 Monsignor 保留为原书称谓，不外推职务或教区。S4 累计登记370组/478条候选映射，待登记4,464组/4,534条；KU 总数1,389。

<a id="s4-rousseau-person"></a>

### S4 person：Jean Jacques Rousseau 跨章直接关系端点登记（2026-10-17）

候选 `cand-2289`（Q-R.csv#217）保持 S3 `new` 组 `new-person:jacques-jean-rousseau-ad86218db7`，单候选映射至[人物卡](../../../04-knowledge/units/persons/jean-jacques-rousseau.md)。索引页码328、369、372跨第10、15章同列；第10章 p.328 以 Rousseau 指向哲学家，并记 Il Filosofo dell’Alpi、Biffi 日记及自然观论述；第15章 p.369 将其与 Alticchiero 的 Houdon 半身像及园林影响并述，p.372 将其与 Querini 的历史观相联。同组按 S3 归并，不与其他 Rousseau 姓名候选臆合；本轮未查阅外部身份记录，也未补生卒年。5条直接 relation_candidate 保持原状待 S6：st-chp10-p328-biffi-diary-on-rousseau, st-chp10-p328-biffi-follower-of-rousseau-inferred, st-chp10-p328-ode-rousseau-influence, st-chp15-p369-rousseau-influence-alticchiero, st-chp15-p372-rousseau-influence-on-querini-view-of-past。`st-chp10-p328-arcadia-not-necessary-cause` 与 `st-chp10-p328-biffi-diary-entry-after-rousseau-death` 均继续保持 `relation_candidate=false`；另两条将 Rousseau 列于 `mentioned_candidate_ids`、但端点为 Alticchiero 与 Houdon 的陈述也不改成 Rousseau 的正式边。本轮未写 relations.csv、未新增 enrichment 字段事实或 sources.csv 记录。S4 累计登记371组/479条候选映射；待登记4,463组/4,533条；KU 总数1,390。

<a id="s4-carlo-barberini-brother-urban-viii"></a>

### S4 person：Carlo Barberini 同组两候选登记（2026-10-17）

`cand-0194`（B.csv#41，pp.26、31）与 `cand-0195`（B.csv#42，monuments to，p.41）保持 S3 组 `new-person:barberini-carlo-2f55dd94e4`，共同映射至[卡洛·巴贝里尼人物卡](../../../04-knowledge/units/persons/carlo-barberini-brother-of-urban-viii.md)，一组登记一个 KU。第2章 p.26 L68 称 Urban 与兄长 Carlo 共同购置宫殿；p.31 L7–8 以 Carlo Barberini 全名指称1624、1625年两次地产交易的同一买方；p.41 L121–123 记 Urban 的兄长 Carlo 于1630年去世，并记 Pope 为其订制纪念牌。主项和 monuments to 子项所列页码由同一原书索引明确连接，支持该候选组为一人。该人不是 Antonio Barberini 卡所记的父亲 Carlo Barberini；后者为 Urban 的父辈，本卡明确分开。6条直接 relation_candidate 原样保留待 S6：st-chp2-sec-ii-l3-8-colonna-sale, st-chp2-sec-ii-l3-8-orsini-sale, st-chp2-secii-l118-125-carlo-caesar-comparison, st-chp2-secii-l118-125-carlo-character-and-honours, st-chp2-secii-l118-125-carlo-command-in-chief, st-chp2-secii-l118-125-urban-sibling-carlo。本轮未新增正式关系、enrichment 字段事实或 sources.csv 记录。S4 累计登记372组/481条候选映射；待登记4,462组/4,531条；KU 总数1,391。
### S3 person 复核：Carlo Barberini 的重复索引子项复用（2026-10-17）

`cand-0196`（B.csv#43，“purchase of Orsini and Colonna estates”，p.31）与 `cand-0197`（B.csv#44，“synopsis of Machiavelli's Prince”，p.41）原因缺少各自的 `mentions.csv` 映射而列 `undecided`。复核发现，前者的索引子项对应第2章 p.31 L7–8，正文明确以全名 Carlo Barberini 指称两笔地产交易的同一买方；该段已由 `cand-0194` 的 S2 提及锚定。后者对应第2章 p.41 L121–124，statement `st-chp2-secii-l118-125-carlo-prince-synopsis` 将 `cand-0197` 作为主体候选，原文说 Carlo 撰写了 Machiavelli《君主论》的拉丁文提要；同段前句已明确所指为 Urban VIII 之兄。两条索引主项均明示相同亲属身份，且子项与正文内容逐一吻合，因此现改为 `same` → `units/persons/carlo-barberini-brother-of-urban-viii`。原暂缓理由保留在 alignment 行中；该人物边界仍与 Urban VIII 的父亲 Carlo Barberini 区分。`cand-0197` 所关联的 S2 关系候选仍待 S6，本轮不创建正式关系或新增内容字段。
### S3 person 跨章复核：Alessandro Algardi 子项复用既有人物 KU（2026-10-17）

`cand-0037`（A.csv#38，Hercules，p.371）、`cand-0038`（A.csv#39，Mazarin invitation to Paris，pp.182–183）与 `cand-0039`（A.csv#40，villa for Prince Camillo Pamfili，p.148）原因缺少各自的 `mentions.csv` 映射而列 `undecided`。逐项对照索引子目与正文：第15章 p.371 L76 明称 Querini 所藏 Hercules by Algardi；第7章 p.182 L157 以 Algardi 指称 Mazarin 于1648年尝试延揽的雕塑家；第6章 p.148 L30–35 先给出全名 Alessandro Algardi，继而称 Camillo Pamfili 的罗马别墅由 Algardi 负责建造。三条索引子目均隶属同一全名主项，正文姓名、类型与语境同既有 [Alessandro Algardi 人物卡](../../../04-knowledge/units/persons/alessandro-algardi.md)一致，且跨第6、7、15章相互吻合。因此三候选改为 `same` → `units/persons/alessandro-algardi`。Hercules 仍为人物所涉作品而非本批新作品身份裁决；Mazarin 邀请保留为尝试，不写成迁居事实。原暂缓理由保留在 alignment 行。本轮不改写 S2 关系候选或 relations.csv。
### S3 person 跨章复核：Guercino 索引主项及子项复用既有人物 KU（2026-10-17）

`cand-1258`（G.csv#168，索引全名形式为 Guercino (Francesco Barbieri)，页码横跨章前至第9章）及其索引子项 `cand-1265`（G.csv#175，payment，p.14）、`cand-1274`（G.csv#184，work for Don Antonio Ruffo，pp.14、209–210）此前均列 `undecided`。正文锚点：第1章 p.14 L76–82 记 Guercino 按画中人物收费；第7章 p.176–178 及第8章 pp.209–210 多处以 Guercino 指称同一画家；子项页码与主项及 S2 提及相符。既有 KU 的英文名为 Giovanni Francesco Barbieri，不能仅凭别名相似自动合并，故本次读取 Treccani《意大利人传记辞典》第6卷（1964）同名条目，标题明确为 “BARBIERI, Giovanni Francesco detto il Guercino”（https://www.treccani.it/enciclopedia/giovanni-francesco-detto-il-guercino-barbieri_(Dizionario-Biografico)/；访问日期2026-10-17）；该身份记录将全名与别名直接相连，支持复用 [Guercino 人物卡](../../../04-knowledge/units/persons/guercino.md)。因此三条候选均改为 `same` → `units/persons/guercino`，原未决理由保留于候选行；alignment 中另加一条 Treccani 外部身份记录，绑定主候选 `cand-1258`。该记录只支持人物身份，不据此新增生平事实；本轮不改写任何 S2 关系候选或 `relations.csv`。
### S3 person 复核：Owen McSwiny 的四条索引子项复用既有人物 KU（2026-10-17）


### S3 person：Caravaggio 五条索引子项补充复用既有人物（2026-10-17）

`cand-0546`（C.csv#70，Conversion of St Paul，p.11）、`cand-0548`（C.csv#72，Earthly Love，p.127）、`cand-0550`（C.csv#74，Martyrdom of St Peter，p.11）、`cand-0551`（C.csv#75，portrait of Maffeo Barberini，p.25）与 `cand-0552`（C.csv#76，Sacrifice of Abraham，p.25）均为人物候选，索引子目隶属主项“Caravaggio, Michelangelo da”，由 `undecided` 改为 `same` → `units/persons/caravaggio`。子目提供作品与主题的检索定位，不构成独立作品候选。第1章 p.11 将《Conversion of St Paul》与《Martyrdom of St Peter》列为 Caravaggio 接受委托的祭坛画；第5章 p.127 明称 “Michelangelo da Caravaggio’s Earthly Love”；第2章 p.25 给出全名，并称他绘制 Maffeo Barberini 肖像、稍后又受托画《The Sacrifice of Abraham》。逐项正文锚点与旧暂缓理由保存在 alignment 行；并入既有 `sg3-ku-units-persons-caravaggio` 组，不新增外部身份记录、KU 或正式关系。现有跨章人物组共11条候选。S3 计数更新为 same=1,807（1,030个 KU）、undecided=5,479；new、S4 数量及 alignment 行数不变。

### S3 汇总与类型决定数更新（2026-10-17）

本节旧版类型分布与候选规模已由当前表重算替换。12,406 条候选决定行均有唯一决定；227 条外部身份记录另计。`same` 指向1,030个既有 KU；`new` 为4,834个身份组，其中372组已由S4登记；待证、冲突与排除分别为5,473、8、100条，去向与理由保留在各 alignment 行。各类型现行数见上方“按类型决定数”表；此汇总仅反映裁决与去向，不表示待证身份已查明或冲突已解决。

### S3 person：A. M. Zanetti the Elder 六条索引子项复用既有人物（2026-10-17）

`cand-2839`（UVWXYZ.csv#176，and Crozat，p.341）、`cand-2840`（#177，and Joseph Smith，p.341）、`cand-2841`（#178，and Marshal Schulenburg，p.341）、`cand-2842`（#179，and Regent de France，p.341）、`cand-2843`（#180，and Sebastiano and Marco Ricci，pp.341–342）与 `cand-2844`（#181，intermediary between Venice and rest of Europe，p.342）均为人物候选，隶属索引主项“Zanetti, A. M., the Elder”，由 `undecided` 改为 `same` → `units/persons/a-m-zanetti-the-elder`。第13章 p.341 L91 明称 Antonio Maria Zanetti the Elder，并在同一段中逐项叙述其与 Sebastiano／Marco Ricci、Crozat、法国 Regent 的往来；L95 同段记其与 Joseph Smith、Schulenburg 的联系。第13章 p.342 L102 称其为连接威尼斯与欧洲其他地区的中间人。正文锚点逐条写入 alignment 行并保留旧暂缓理由；本组与既有 `cand-2838`、`cand-3707` 共8条候选。索引 archive 子项 `cand-2845` 保持独立映射至 archive KU；本轮不新增外部身份记录、KU 或正式关系。



<a id="s4-antonio-barbaro-person"></a>

### S4 person：Antonio Barbaro 两候选同组登记（2026-10-17）

`cand-0184`（B.csv#31，pp.248、249、253）与 `cand-0185`（B.csv#32，and S. Maria del Giglio，pp.248、249）按 S3 身份组 `new-person:antonio-barbaro-antonio-barbaro-conception-e91bacacf4` 共同映射至[Antonio Barbaro 人物卡](../../../04-knowledge/units/persons/antonio-barbaro.md)，一组登记一个 KU。跨页全名、建筑子项与第253页再次出现的姓名支持该书内人物身份；本轮未使用外部身份记录。第248页记 Haskell 对 façade 设计、Candia 战争和 Rome 大使经历的叙述；第249页的战时评价与 Morosini 相关叙述保留作者归属，脚注所引材料未独立核读。第253页将 Tiepolo 的 Roman epics 说成纪念 Antonio Barbaro 与 Daniele Dolfin。7条直接 relation_candidate 原样保留待 S6：st-chp9-p248-antonio-ambassador-in-rome, st-chp9-p248-barbaro-fought-war-of-candia, st-chp9-p248-facade-design-and-building, st-chp9-p249-barbaro-conduct, st-chp9-p249-barbaro-returned-and-opposed-morosini, st-chp9-p249-barbaro-will-location, st-chp9-p253-barbaro-dolfin-roman-epics。未新增正式关系或外部字段事实。S4 累计登记373组/483条候选映射；待登记4,461组/4,529条；KU 总数1,392。

<a id="s4-angelo-giori-person"></a>

### S4 person：Angelo Giori 跨章身份组登记（2026-10-17）

`cand-1190`（G.csv#97，pp.41、59）保持 S3 组 `new-person:angelo-giori-610dcba3b7`，映射至[Angelo Giori 人物卡](../../../04-knowledge/units/persons/angelo-giori.md)。书后索引以同一全名定位两页，正文第41、59页均再次具名；不需要依姓氏或外部相似身份合并。第41页记录 Haskell 对其 Camerino 校长经历、迁往 Rome、监督 Urban VIII 墓工程、Barberini protégé 身份及 Claude 收藏的叙述；“rather mean”保留为作者评价。第59页记其在 Bernini 完成墓葬工程时致信遭流放的枢机；责任范围未明。注5、注6引文未独立核读。7条直接 relation_candidate 原样保留待 S6：st-chp2-secii-l118-125-angelo-giori-admires-sacchi, st-chp2-secii-l118-125-angelo-giori-artistic-interest, st-chp2-secii-l118-125-angelo-giori-background, st-chp2-secii-l118-125-angelo-giori-claude-patron, st-chp2-secii-l118-125-angelo-giori-claude-pictures, st-chp2-secii-l118-125-angelo-giori-supervision, st-chp2-secvii-l5-19-giori-urges-congratulations。本轮未新增正式关系或外部字段事实。S4 累计登记374组/484条候选映射；待登记4,460组/4,528条；KU 总数1,393。

<a id="s4-pellegrino-peri-person"></a>

### S4 person：Pellegrino Peri 索引与正文候选同组登记（2026-10-17）

`cand-1878`（P.csv#79，p.122）与 `cand-6081`（第5章 p.122 注1正文候选）按 S3 组 `new-person:pellegrino-peri-0180e88b93` 共同映射至[Pellegrino Peri 人物卡](../../../04-knowledge/units/persons/pellegrino-peri.md)。索引反序形式、正文全名及同页脚注全名相符；一组只登记一个 KU。Haskell第122页称 Peri 住在 Pasquino 附近并雇用初到 Rome 的 Gaulli；正文另称 Carlone 欠款拒还。注1转述1666年袭击和1681年失窃报告，引述 Pascoli 与 Bertolotti，但被引文献未独立核读。六条直接 relation_candidate 原样保留待 S6：st-chp5-note-p122-n1-carlone-attack, st-chp5-note-p122-n1-carlone-loan, st-chp5-note-p122-n1-peri-theft, st-chp5-p122-carlone-debt, st-chp5-p122-peri-gaulli, st-chp5-p122-peri-residence-near-pasquino。本轮未新增正式关系。S4 累计登记375组/486条候选映射；待登记4,459组/4,526条；KU 总数1,394。

<a id="s4-ferdinando-duke-mantua-person"></a>

### S4 person：Ferdinando, Duke of Mantua 跨章索引身份组登记（2026-10-17）

`cand-1523`（M.csv#60，pp.10、14、175）保持 S3 组 `new-person:ferdinando-mantua-of-ff7aabd931`，映射至[Ferdinando, Duke of Mantua 人物卡](../../../04-knowledge/units/persons/ferdinando-duke-of-mantua.md)。第7章 p.175 明称其为 Marie de Medici 之侄 Ferdinando，并称其于1624年为曼托瓦公爵；第1章 p.14 记1617年一位曼托瓦公爵向 Guido Reni 订画，索引将两页归入同一主项。索引另列的 p.10 当前正文未找到对应公爵提及，保留为未核实定位，不据其扩充身份。父亲 Vincenzo 的统治者身份未解决。7条直接 relation_candidate 原样保留待 S6：st-chp7-p175-i10, st-chp7-p175-i11, st-chp7-p175-i12, st-chp7-p175-i13, st-chp7-p175-i14, st-chp7-p175-i16, st-chp7-p175-i17。未新增正式关系或外部身份记录。S4 累计登记376组/487条候选映射；待登记4,458组/4,525条；KU 总数1,395。

<a id="s4-james-brydges-chandos-person"></a>

### S4 person：James Brydges，第一代 Chandos 公爵身份组登记（2026-10-17）

`cand-0647`（C.csv#171，p.281）保持 S3 组 `new-person:1st-brydges-chandos-james-of-46f0373d10`，映射至[James Brydges 人物卡](../../../04-knowledge/units/persons/james-brydges-first-duke-of-chandos.md)。索引头衔与第10章正文全名、爵位相合。p.281 记其 Paymaster 任职、1713年取得 Canons、1719年成为 Chandos 公爵、赞助 Bellucci 及主持音乐会；财富来源和“最重要英国赞助人”作为 Haskell 的说法保留。六条直接 relation_candidate 原样保留待 S6：st-chp10-p281-bellucci-chandos-chapel-team, st-chp10-p281-brydges-acquired-canons, st-chp10-p281-brydges-bellucci-patron, st-chp10-p281-brydges-canons-concerts, st-chp10-p281-brydges-created-duke, st-chp10-p281-brydges-paymaster-service。本轮未新增正式关系。S4 累计登记377组/488条候选映射；待登记4,457组/4,524条；KU 总数1,396。

<a id="s4-leonora-baroni-person"></a>

### S4 person：Leonora Baroni 跨章同名候选组登记（2026-10-17）

`cand-0249`（B.csv#96，pp.96、180、181）与 `cand-5530`（第4章 p.96 正文候选）按 S3 组 `new-person:baroni-leonora-970b86fc4c` 共同映射至[Leonora Baroni 人物卡](../../../04-knowledge/units/persons/leonora-baroni.md)。索引名与正文全名一致；第4章称她为歌手并提及为其所作的赞颂诗，第7章两页均以同一全名叙述她与 Mazarin 的关系。第4章 OCR 页标作[Page 9]，但索引定位p.96且下页标为p.97；该缺位原样记录。恋爱关系和歌剧明星评价保持 Haskell 归属。五条直接 relation_candidate 原样保留待 S6：st-chp4-sec-i-l20-24-collection-honours-baroni, st-chp4-sec-i-l20-24-milton-captivated-by-baroni, st-chp4-sec-i-l42-67-fn96-baroni-publication, st-chp7-p180-i21, st-chp7-p180-i22。未新增正式关系。S4 累计登记378组/490条候选映射；待登记4,456组/4,522条；KU 总数1,397。

<a id="s4-louis-dorigny-cross-chapter-person"></a>

### S4 person：Louis／Luigi Dorigny 跨章索引组登记（2026-10-17）

`cand-0944`（D.csv#46，pp.201、250、251、268、270）与 `cand-0945`（D.csv#47，work for Manin，p.268）按 S3 组 `new-person:dorigny-louis-fc0f85a71c` 共同映射至[Louis Dorigny 人物卡](../../../04-knowledge/units/persons/louis-dorigny.md)。第7章 p.201 明称 Louis Dorigny；第9章 p.251 以 Luigi Dorigny 指 Manin 家族雇用的画家，p.268 又称 Louis Dorigny，并记其装饰 Manin 的 Passeriano 别墅。同一索引主项和 Manin 子项及共享语境支持该书内姓名变体归并；第270页仅列姓氏，不独立承担身份识别。5条直接 relation_candidate 原样保留待 S6：st-chp9-p250-widmann-country-house-frescoes, st-chp9-p250-zenobio-fresco-cycle, st-chp9-p251-manin-employed-dorigny, st-chp9-p268-dorigny-passeriano-villa, st-chp9-p268-manin-dorigny。本轮未新增正式关系或外部身份记录。S4 累计登记379组/492条候选映射；待登记4,455组/4,520条；KU 总数1,398。

<a id="s4-cornelius-de-wael-person"></a>

### S4 person：Cornelius de Wael 直接关系端点登记（2026-10-17）

`cand-2794`（UVWXYZ.csv#131，p.122）保持 S3 组 `new-person:cornelius-de-wael-34ec2709b7`，映射至[Cornelius de Wael 人物卡](../../../04-knowledge/units/persons/cornelius-de-wael.md)。索引主项和正文全名一致。Haskell记述其于1657年离开 Genoa、经商并持有大量待售画作，与同乡的艺术家和客户往来，且拥有不同类别的小幅画；“must have known”保留为作者推断。6条直接 relation_candidate 原样保留待 S6：st-chp5-p122-wael-clients, st-chp5-p122-wael-gaulli-acquaintance, st-chp5-p122-wael-important-artists, st-chp5-p122-wael-small-pictures, st-chp5-p122-wael-stock, st-chp5-p122-wael-trade。本轮未新增正式关系或外部身份记录。S4 累计登记380组/493条候选映射；待登记4,454组/4,519条；KU 总数1,399。

<a id="s4-leopold-wilhelm-person"></a>

### S4 person：Archduke Leopold Wilhelm 直接关系端点登记（2026-10-17）

`cand-1399`（L.csv#56，p.193）保持 S3 组 `new-person:archduke-leopold-wilhelm-b4ff9984cb`，映射至[Archduke Leopold Wilhelm 人物卡](../../../04-knowledge/units/persons/leopold-wilhelm-archduke.md)。索引头衔和正文全名对应。Haskell称其曾任 Netherlands 总督、带回当地购得的画作、偏爱早期威尼斯画家、赞助 Pietro della Vecchia、邀请 Pietro Liberi 前往 Vienna，并于1662年将财产留给侄子 Emperor Leopold I。6条直接 relation_candidate 原样保留待 S6：st-chp7-p193-leopold-bequest, st-chp7-p193-leopold-patronizes-vecchia, st-chp7-p193-leopold-venetian-painters, st-chp7-p193-liberi-vienna, st-chp7-p193-loot-mitigated, st-chp7-p193-n2-boschini-dedication。本轮未新增正式关系。S4 累计登记381组/494条候选映射；待登记4,453组/4,518条；KU 总数1,400。

<a id="s4-don-gasparo-altieri-person"></a>

### S4 person：Don Gasparo Altieri 身份组登记（2026-10-17）

`cand-0089`（A.csv#90，p.161）保持 S3 组 `new-person:altieri-gasparo-d03e2990cb`，映射至[Don Gasparo Altieri 人物卡](../../../04-knowledge/units/persons/don-gasparo-altieri.md)。书后索引主项及第6章 p.161 正文姓名相合；既有 Altieri family KU 保持独立。Haskell关于其与 Clement X 的关系、Gonfaloniere 职务、宫邸装饰争议和 Claude 作品的叙述仍按原书语境保存。6条直接 relation_candidate 原样保留待 S6：st-chp6-p161-v1-14, st-chp6-p161-v1-15, st-chp6-p161-v1-19, st-chp6-p161-v1-22, st-chp6-p162-v1-01, st-chp6-p162-v1-02。本轮未新增正式关系。S4 累计登记382组/495条候选映射；待登记4,452组/4,517条；KU 总数1,401。

<a id="s4-giovanni-battista-crescenzi-person"></a>

### S4 person：Giovanni Battista Crescenzi 身份组登记（2026-10-17）

`cand-0869`（C.csv#403，p.173）保持 S3 组 `new-person:battista-crescenzi-giovanni-0fabe7dc0e`，映射至[Giovanni Battista Crescenzi 人物卡](../../../04-knowledge/units/persons/giovanni-battista-crescenzi.md)。索引主项及第7章 p.173 正文全名相符；既有 Crescenzi family KU 保持独立。书中未具名的枢机兄弟不另行指认为特定人物。6条直接 relation_candidate 原样保留待 S6：st-chp7-p173-i01, st-chp7-p173-i02, st-chp7-p173-i04, st-chp7-p173-i07, st-chp7-p173-i09, st-chp7-p173-i10。本轮未新增正式关系。S4 累计登记383组/496条候选映射；待登记4,451组/4,516条；KU 总数1,402。

<a id="s4-daniele-dolfin-iii-person"></a>

### S4 person：Daniele Dolfin III 身份组登记（2026-10-17）

`cand-0927`（D.csv#29，pp.252、253）保持 S3 组 `new-person:daniele-dolfin-iii-b39c2311e9`，映射至[Daniele Dolfin III 人物卡](../../../04-knowledge/units/persons/daniele-dolfin-iii.md)。第252页正文称 Daniele III，第253页作 Daniele Dolfin；索引将两页列于同一主项。Daniele IV 和 Daniele Dolfin（Archbishop of Udine）为索引中的分立项，既有 Dionisio Dolfin 及 Dolfin family KU 保持独立。6条直接 relation_candidate 原样保留待 S6：st-chp9-p252-daniele-iii-public-service, st-chp9-p252-daniele-iii-will-programme, st-chp9-p252-daniele-iii-will-shed-blood, st-chp9-p252-daniele-iv-brother-of-iii, st-chp9-p252-dionisio-younger-brother-of-iii, st-chp9-p253-roman-epics-commemorate-daniele-dolfin。本轮未新增正式关系。S4 累计登记384组/497条候选映射；待登记4,450组/4,515条；KU 总数1,403。

<a id="s4-antoine-watteau-person"></a>

### S4 person：Antoine Watteau 跨章身份组登记（2026-10-17）

`cand-2804`（UVWXYZ.csv#141，pp.277、284、285、292、384）保持 S3 组 `new-person:antoine-watteau-92f90f3ca9`，映射至[Antoine Watteau 人物卡](../../../04-knowledge/units/persons/antoine-watteau.md)。第10章 p.284 明示全名，索引将第10章四处及结论 p.384 列于同一人物主项。Crozat 于 p.277 提及的 Watteau 画作保持为独立作品候选。5条直接 relation_candidate 原样保留待 S6：st-chp10-p277-crozat-description-of-watteau, st-chp10-p277-crozat-met-watteau, st-chp10-p284-watteau-at-crozat-house, st-chp10-p285-carriera-met-watteau, st-chp10-p292-tessin-early-travel。本轮未新增正式关系。S4 累计登记385组/498条候选映射；待登记4,449组/4,514条；KU 总数1,404。

<a id="s4-virgin-mary-cross-chapter-person"></a>

### S4 person：Virgin Mary 跨章身份组登记（2026-10-17）

`cand-3427`（body-mention，S2 source anchor `chp-1:01_CHP-1_sec_ii:l28-38#L297`）保持 S3 组 `new-person:mary-virgin-0b7fd09ac8`，映射至[Virgin Mary 人物卡](../../../04-knowledge/units/persons/virgin-mary.md)。30条 S2 提及横跨第1、2、3、4、5、6、8、9、10章；Virgin Mary、the Virgin、Blessed Virgin 与 Madonna 等称谓在相应宗教／图像语境下指向该人物。具体绘画、雕像和作品题名不并入人物卡。7条直接 relation_candidate 原样保留待 S6：st-chp3-secii-l40-52-chapels-marian-mysteries, st-chp3-secii-l74-81-lanfranco-dome-depicts-virgin, st-chp3-seciv-l118-128-madonna-chapel-last-to-be-adorned, st-chp3-seciv-l179-187-unnamed-order-worshipped-virgin, st-chp4-sec-ii-p110-flight-figures-foreground, st-chp9-p255-fatherland-invokes-virgin, st-chp9-p274-zompini-virgin-typology。本轮未新增正式关系。S4 累计登记386组/499条候选映射；待登记4,448组/4,513条；KU 总数1,405。

<a id="s4-giovanni-paolo-pannini-person"></a>

### S4 person：Giovanni Paolo Pannini 身份组登记（2026-10-17）

`cand-1827`（P.csv#26，索引页码297n、307、308、351、357、358、393）沿用 S3 身份组 `new-person:giovanni-pannini-paolo-73bd439aee`，登记为[乔瓦尼·保罗·帕尼尼人物卡](../../../04-knowledge/units/persons/giovanni-paolo-pannini.md)。索引主项和第10、14、19章的姓名提及支持书内身份映射；卡片只保留有书内来源的语境及其原有不确定性，未访问外部身份来源。

索引中的 `cand-1828`（P.csv#27，work：Interior of the Pantheon）与人物分开；其 S3 仍为 undecided，不由同名子项或委托语句推定作品身份。5条直接 relation_candidate 保留待 S6：st-chp10-p308-possible-pannini-source, st-chp14-p351-pannini-subject, st-chp14-p357-pannini-specialized-in-capricci, st-chp14-p357-pantheon-commissioned-painter, st-chp14-p358-recommended-study-pannini。万神殿委托关系的作品端点未决；本轮未新增正式关系。

S4 累计登记387组/500条候选映射；待登记4,447组/4,512条；KU 总数1,406。

<a id="s4-johann-karl-loth-cross-chapter-person"></a>

### S4 person：Johann Karl Loth 跨章身份组登记（2026-10-17）

`cand-1442`（L.csv#100，pp.233、265n）沿用 S3 组 `new-person:johann-karl-loth-77685471f9`，映射至[约翰·卡尔·洛特人物卡](../../../04-knowledge/units/persons/johann-karl-loth.md)。第8章出现 Karl Loth，第9章出现 Johann Karl Loth；全名、索引页码和 S2 提及锚点支持跨章同一人物映射。卡片只记录 Haskell 的书内说法；注5转述 Fogolari 1937，未独立查阅该文献或原信。

索引附项 `cand-1443`（and Grand Prince Ferdinand）与 `cand-1444`（Death of Abel）仍为 S3 undecided；信件 archive `cand-7931` 是另一 new 组、待 S4；自画像 work `cand-7933` 仍待证。6条直接 relation_candidate 保留待 S6：st-chp8-p233-loth-employment, st-chp8-p233-loth-first-visit-contact, st-chp8-p233-note5-death-abel, st-chp8-p233-note5-inventory, st-chp8-p233-note5-loth-letter, st-chp8-p233-note5-self-portrait。未新增正式关系。

S4 累计登记388组/501条候选映射；待登记4,446组/4,511条；KU 总数1,407。

<a id="s4-karl-loth-letter-1691-08-14-archive"></a>

### S4 archive：Karl Loth 致 Grand Prince Ferdinand 的信（1691-08-14）登记（2026-10-17）

`cand-7931`（source anchor: chp-8:08_CHP-8_sec_ii:l372-461#L423）沿用 S3 archive 组 `archive-group-f87eaeb73c93`，映射至[该书信档案卡](../../../04-knowledge/units/archives/karl-loth-letter-to-grand-prince-ferdinand-1691-08-14.md)。Haskell 注5经 Fogolari 1937 转述此信日期、收信人和内容；刊本与原信未独立查阅，卡片使用描述性题名，不声称读取全文。

此候选作为 Loth 人物的直接 archive 端点单独登记；`st-chp8-p233-note5-loth-letter` 保留待 S6，未新增正式关系。

S4 累计登记389组/502条候选映射；待登记4,445组/4,510条；KU 总数1,408。

<a id="s4-bergamasque-st-bartholomew-exhibitions-event"></a>

### S4 event：罗马贝加莫社群圣巴托洛梅奥瞻礼画展系列登记（2026-10-17）

`cand-11728`（第5章 p.125，L56–57）沿用 S3 事件组 `sg3-event-cand-11728`，映射至[事件卡](../../../04-knowledge/units/events/bergamasque-community-st-bartholomew-exhibitions-rome.md)。卡片保留 8月24日、地点、资助者、纪念对象及“起始年份不确定、至迟1650年已兴盛”的原文范围。`cand-11736`（S. Bartolomeo all’Isola 瞻礼展系列）为不同 S3 new 事件组，不合并。

7条直接 relation_candidate 保留待 S6：st-chp5-p125-all-isola-exhibitions-less-important, st-chp5-p125-bergamasque-devotional-purpose, st-chp5-p125-bergamasque-exhibition-celebrated-saint, st-chp5-p125-bergamasque-exhibition-practice, st-chp5-p125-bergamasque-exhibitions-honoured-devotees, st-chp5-p125-bergamasque-venue-funding, st-chp5-p125-guardiano-paid-bergamasque-exhibitions。端点去向：`cand-6027` institution new、`cand-11729` place new、`cand-11736` event new 均待 S4；`cand-6028`、`cand-11730`、`cand-11734` 保持 S3 undecided。本轮未新增正式关系。

S4 累计登记390组/503条候选映射；待登记4,444组/4,509条；KU 总数1,409。

<a id="s4-p125-exhibition-direct-endpoint-drain"></a>

### S4 多类型：第5章 p.125–126 展览关系端点登记（2026-10-17）

在 `cand-11728` 贝加莫社群瞻礼展系列登记后，继续登记其 S2 关系候选直接指向的 S3 new 身份组：`cand-6027` → institution `units/institutions/bergamasque-community-rome`；`cand-11729` → place `units/places/church-s-bartolomeo-bergamasque-exhibition-courtyard`；`cand-11735` → place `units/places/s-bartolomeo-all-isola-exhibition-site`；`cand-11736` → event `units/events/s-bartolomeo-all-isola-name-day-exhibitions`；`cand-11741` → term `units/terms/casual-saints-day-fairs`。每组各登记一个 KU，均以第5章 p.125–126 原文为依据。S3 undecided 端点 `cand-6028`、`cand-11730`、`cand-11734` 与 `cand-11740` 未改决定、未分配 KU；艺术家、挂毯及庭院画作候选 `cand-11731`、`cand-11732` 保持待证。

相关直接 relation_candidate 分别留待 S6 裁决；未新增正式关系。更新贝加莫事件卡的端点入口，链接已登记的社群、地点及独立 S. Bartolomeo all’Isola 系列。

S4 累计登记395组/508条候选映射；待登记4,439组/4,504条；KU 总数1,414。

<a id="s4-cross-chapter-art-exhibitions-and-endpoints"></a>

### S4 跨章术语及直接端点登记：Art exhibitions（2026-10-17）

`cand-0132`（A.csv#133，p.125）、`cand-0134`（A.csv#135，pp.128–129、211）和 `cand-0137` （A.csv#138，p.330）沿用同一 S3 `new` 组 `sg3-term-artexhibitions`，共同映射至 `units/terms/art-exhibitions`。第5章的一般展览论述、第8章 S. Salvatore in Lauro 展览及第10章威尼斯展示语境 支持同一术语概念；具体活动与场地分立。

同批登记两个直接关系端点：`cand-6024`（Corpus Domini，S3 event new）→ `units/events/corpus-domini-feast`；`cand-9856`（Piazza S. Marco，S3 place new）→ `units/places/piazza-s-marco-venice`。前者记录节期／游行语境，不推定特定展览日期；后者按 p.330–331 记录广场地点，不将相邻 S. Geminiano 教堂当作展览室。

术语组7条、Corpus Domini 组3条、Piazza S. Marco 组2条直接 relation_candidate 均留待 S6，未写入正式关系。术语关系中的未决端点 `cand-11715`、`cand-11717`、`cand-11720` 保持 S3 undecided；其余候选及既有对象维持原决定。

S4 累计登记398组/513条候选映射；待登记4,436组/4,499条；KU 总数1,417。

<a id="s4-montalto-1955-archive"></a>

### S4 archive：L. Montalto 1955 年论文书目身份登记（2026-10-17）

`cand-6355` 沿用 S3 `new` 组 `archive-group-f033e02efa56`，映射至 `units/archives/l-montalto-frescoes-palazzo-pamphilj-valmontone-1955`。书后书目给出原题、刊物、年份与页码；第1章与第6章注释多次引用该文。卡片仅确认 Haskell 书内的书目身份及引注路径，论文和所引页码未独立查阅；作者只保留书目中的首字母，不与 `cand-3413` 等人物候选合并。6条 citation relation_candidate 留待 S6，未新增正式关系。

S4 累计登记399组/514条候选映射；待登记4,435组/4,498条；KU 总数1,418。

<a id="s4-albrizzi-and-pasquali-printing-institutions"></a>

### S4 institution：Albrizziana 与 Pasquali 两家印刷机构登记（2026-10-17）

`cand-9799` 沿用 S3 组 `sg3-institution-cand-9799`，依据第10章 p.326 的 “Nella Stamperia Albrizziana” 印刷款识及第13章 p.336 对 Albrizzi firm/shop 的叙述登记；与索引 Accademia Albrizziana 保持区分。`cand-9172` 沿用 S3 组 `sg3-institution-cand-9172`，依据第10章 p.299、p.301 及第13章 p.337 登记为 Pasquali 出版事业；正式商号未见于书内。

修正一处 S2 提及与关系端点错配：`m-s2-ch13-p337-011` 的 “the firm” 依 p.337 段落明确回指 Pasquali，故从 `cand-9799` 改至 `cand-9172`；`st-chp13-p337-smith-controlled-interest-in-pasquali-firm` 的 object_candidate_id 及 mentioned_candidate_ids 同步改至 `cand-9172`。这是局部上下文映射修正，不改变两组 S3 决定。Albrizzi 组4条、Pasquali 组3条直接 relation_candidate 留待 S6，未新增正式关系。

S4 累计登记401组/516条候选映射；待登记4,433组/4,496条；KU 总数1,420。

<a id="s3-history-painting-reuse-and-s4-blood-of-christ-term"></a>

### S3 term 复用修正与 S4 图像主题登记（2026-10-17）

`cand-6179` 原 S3 `new` 组 `sg3-term-cand-6179` 与既有 [历史画术语卡](../../../04-knowledge/units/terms/history-painting.md) 表达同一绘画门类。复核卡片及第5章 p.140、第9章 p.257 的用法后，将该候选改为 `same` → `units/terms/history-painting`；本书语境没有定义独立子类，不重复建卡。

`cand-5254` 保持 S3 `new` 组 `sg3-term-cand-5254`，登记为 `units/terms/blood-of-christ-iconographic-theme`。第3章 p.82 将 Blood of Christ 明称为 devotional theme；Molinos、Bernini、Jesuit dome debate 与 Duplex Intercessio 的区别及不确定性均按原文保留。7条直接 relation_candidate 留待 S6，未新增正式关系。

S4 累计登记402组/517条候选映射；待登记4,431组/4,494条；KU 总数1,421。

<a id="s3-paolo-giordano-plate17c-work-reuse"></a>

### S3 work 复用修正：Ottavio Leoni 图版17c（2026-10-17）

`cand-5545` 原 `new` 组 `workgrp-ce2612f695fe07` 与既有 `units/works/ottavio-leoni-paolo-giordano-orsini-duke-of-bracciano` 为同一作品。第4章 p.20 称 Ottavio Leoni 制作了 Paolo Giordano II 蚀刻肖像并标作图版17c；图版17c目录再次署名 Leoni 并题为 Paolo Giordano Orsini, Duke of Bracciano。故将该候选改为 `same` 并复用既有作品 KU，不新建卡片。对应 S2 关系候选沿用既有作品端点；本次未改正式关系。

S4 登记仍为402组/517条候选映射；待登记4,430组/4,493条；KU 总数1,421。

<a id="s4-molinos-controversy-event"></a>

### S4 event：莫利诺斯争议登记（2026-10-17）

`cand-5253` 沿用 S3 事件组 `sg3-event-cand-5253`，登记为 `units/events/molinos-controversy-jesuits-roman-church`。第3章 p.81–82 将争议放在1670年代，并称事端在 Molinos 1664年抵达后不久开始；段落以耶稣会、Oliva、罗马教会及教义冲突描述事件，不提供精确起讫日期。卡名为描述性工作名，脚注文献未独立核读。7条直接 relation_candidate 留待 S6，未新增正式关系。

S4 累计登记403组/518条候选映射；待登记4,429组/4,492条；KU 总数1,422。

<a id="s3-choice-of-hercules-plate32b-work-reuse"></a>

### S3 work 复用修正：Paolo de Matteis 图版32b（2026-10-17）

`cand-7245` 原 `new` 组 `workgrp-de01ab2bdfc994` 与既有 `units/works/paolo-de-matteis-the-choice-of-hercules` 为同一作品。第7章 p.198 称 Shaftesbury 选择 Paolo de Matteis 创作 “Hercules at the Crossroads between Vice and Virtue”，并交叉引用图版32b；图版目录及现有作品卡均记录 Paolo de Matteis 的《The Choice of Hercules》、Temple Newsam、Leeds。据此将候选改为 `same` 并复用现有 KU，不重复建卡；5条直接 relation_candidate 仍依 S6 处理，本次未改正式关系。

S4 登记仍为403组/518条候选映射；待登记4,428组/4,491条；KU 总数1,422。

### S2/S3 锚点更正：Romanelli 人物与 1638 年任命事件分开（2026-10-17）

复核 `cand-2209`（Q-R.csv#136，`appointment to Accademia di S. Luca`）时发现，原有 S2 段落锚点 `m-chp2-seciv-l106-112-0035` 是人物代词“his leading pupil”，而非事件提及；同段4条人物提及及9条人物断言曾误挂到事件候选。现将这4条提及和9条断言端点改挂到已由 S3 裁决为 `same` 的人物候选 `cand-2208`（`units/persons/romanelli`）。将同段“In 1638 he was made Principe”登记为事件提及 `m-chp2-seciv-l106-112-0051`，并在任命断言的提及候选中保留 `cand-2209`；该候选仍为独立事件组 `sg3-event-cand-2209`，没有并入人物 KU。对齐行的现行 source_ref 改指任命短语，旧锚点作为历史注释保留。原文、职位名和1638年限定未改；本次未新增正式关系。

<a id="s4-romanelli-appointment-event"></a>

### S4 event：Romanelli 1638 年获任 Accademia di S. Luca Principe（2026-10-17）

`cand-2209` 沿用 S3 事件组 `sg3-event-cand-2209`，登记为 `units/events/romanelli-appointment-principe-accademia-di-san-luca-1638`。候选来自索引子目“appointment to Accademia di S. Luca”；第2章 p.53 L112 明载 Romanelli 于1638年奉 Cardinal [Francesco] Barberini 之命获任 Principe。卡片保留原职衔，不补任期、任命地点或正式程序。四条人物提及和九条人物断言已归到同名人物候选 `cand-2208`；事件短语另记为 `cand-2209`。人物—机构关系仍待 S6；没有新增正式关系。

S4 累计登记404组/519条候选映射；待登记4,427组/4,490条；KU 总数1,423。

<a id="s4-aix-la-chapelle-peace-1748"></a>

### S4 event：1748年艾克斯-拉夏贝尔和约（2026-10-17）

`cand-0019` 沿用 S3 事件组 `sg3-event-cand-0019`，登记为 `units/events/peace-of-aix-la-chapelle-1748`。第10章跨 p.317–318 承认此前已有成就，称1748年和约“usually taken”作为意大利出现新精神的起点；卡片将此保留为 Haskell 所述的断代判断，不写成启蒙思想的唯一开端或和约的因果效果。来源未列参与方、条款或签订具体日期，本次未补入。对应 S2 断言不是关系候选，没有新增正式关系。

S4 累计登记405组/520条候选映射；待登记4,426组/4,489条；KU 总数1,424。

<a id="s3-srocco-cross-chapter-s4-registration-20261017"></a>

### S3 机构复用修正与 S4 圣罗科跨章身份组登记（2026-10-17）

复核跨章直接端点时，发现 `cand-7072`（第7章 p.180 注4，“Institute of Arts, Detroit”）与既有 `units/institutions/detroit-institute-of-arts` 重复。第9章 p.265 注2同页明确写出全名 “Detroit Institute of Arts”，与现有机构卡的身份记录吻合；故将其 S3 决定从 `new` 更正为 `same` 并复用既有 KU。第7章两幅 Poussin 画与两处馆藏的逐件配对仍未解决，不因机构同一性而选择任何一条边。

S4 按 S3 当前身份组登记：`cand-8587` 圣罗科年度展览系列，`cand-9871` 总督与元老院8月16日巡行，`cand-10005` 1770年8月16日展览场次，`cand-8569` Piazzetta《守护天使》（Angelo Custode），`cand-8129` 威尼斯元老院，`cand-8728` 威尼斯总督职务，`cand-9866` 圣罗科展览报道中的画家群体，`cand-9870` 巴黎 Salon 比较对象，`cand-9863` 1729年8月20日 Nunzio 报告，`cand-9869` Algarotti 致 Mariette 书信，`cand-8580` Cochin 第三卷引文定位，以及 `cand-0793` Charles-Nicolas Cochin。每组一个 KU；人名、年份、引文、身份层级和原文限定均按来源记录。

保持待证：`cand-8588`（S. Rocco 场所身份边界）、`cand-10006`（两幅 Zais 画未个别识别）、`cand-1904`（“the painter”索引候选缺少可核 S2 body mention）、`cand-8621`（估价记录未识别）、`cand-8586`（d’Argenville 引文身份／粒度未定）。`cand-9863` 报告只报告绘画展示和人群，场地未定，仍不关联圣罗科系列。已映射对象如 `cand-2329`、`cand-1901`、`cand-2569`、`cand-2830`、`cand-4056`、`cand-9874` 沿用原 S3 去向。

本批相关 S2 关系候选仍留待 S6；未写入 `relations.csv`，未把“possibly/probably”改成确定因果，未将年度系列与1770场次合并。

S4 累计登记417组/532条候选映射；待登记4,413组/4,476条；KU 总数1,436。

<a id="s4-s-giovanni-decollato-place-institution"></a>

### S4 place／institution：圣若望斩首堂跨章场所与管理机构登记（2026-10-17）

`cand-6040`（`sg3-place-cand-6040`）登记为[罗马圣若望斩首堂地点](../../../04-knowledge/units/places/s-giovanni-decollato-church-rome.md)；`cand-6041`（`sg3-place-cand-6041`）登记为该堂内部[回廊地点](../../../04-knowledge/units/places/s-giovanni-decollato-cloisters-rome.md)；`cand-6048`（`sg3-institution-cand-6048`）登记为本书语境中的[Compagnia della Misericordia 机构](../../../04-knowledge/units/institutions/compagnia-della-misericordia-s-giovanni-decollato.md)。S3 的三个新组分别保持 place、place、institution 类型；没有与既有年度展览系列及1668、1675场次合并。第5章 p.127–128 记载教堂、回廊和管理机构，第6章 p.154 再次提及 Rosa 在 S. Giovanni Decollato 展画，构成地点的跨章来源锚点。第5章 OCR 的 Decollate 沿用原文转录；S2 既有印刷页核对记录为 Decollato，本次没有改写 S0。教堂、回廊及机构端点对应10条不同的直接 relation_candidate，仍留待 S6；未写入 relations.csv 或新增正式关系。S4 累计登记420组/535条候选映射；待登记4,410组/4,473条；KU 总数1,439。 strict-stage 审计复核通过：`errors=[]`、`s2_missing=[]`；审计的4,488条待登记 new alignment 行包含本表的4,473条候选映射和15条外部身份记录。

<a id="s3-s4-callot-cross-chapter-group"></a>

### S3–S4 person／work：Jacques Callot 跨章人物组与《La Fiera dell'Impruneta》作品边界（2026-10-17）

S3 复核 `cand-0482`（C.csv#6，索引页95、133、343）与 `cand-0483`（C.csv#7，p.213 子项 Fiera dell'Impruneta）：两条人物候选的规范全名均为 Callot, Jacques。第4章 p.95 给出 Jacques Callot 全名；第5章 p.133、第8章 p.213 与第13章 p.343 形成跨章姓氏/归属锚点。故保留 `new-person:callot-jacques-b8b6e13e5f` 为同一人物 new 组，不映射到任何已有 person KU；未访问外部身份源。

检查第8章 p.213 后发现 `m-chp8-p213-040`（Callot’s print）和 `m-chp8-p213-041`（La Fiera dellTmpruneta）被挂在人物候选下。现将两条作品提及改映射至新 work 候选 `cand-12429`，新增 `m-chp8-p213-086` 将其中人名 Callot 单独映射回 `cand-0483`。原断言 `st-chp8-p213-callot-print-and-original-plate` 的 subject/object 保持不变：Del Rosso 兄弟与被称为“apparently the original plate”的 `cand-7570`；只将版画 work 候选补入 mentioned_candidate_ids。

新 work 候选 `cand-12429` 以 `new-work:callot-la-fiera-dell-impruneta-20261017` 裁为 source-local `new`，和 `new-person:callot-jacques-b8b6e13e5f` 的人物组分开，经 backlog `bl-0005` 按 S1→S3→S4 登记为[《La Fiera dell'Impruneta》版画](../../../04-knowledge/units/works/jacques-callot-la-fiera-dell-impruneta-print.md)。印刷页对照读作 La Fiera dell'Impruneta；S0 OCR 保持不变。版画与原版模具分开；cand-7570 的类型继续待证，不新增推定关系。

Callot 相关艺术圈、收藏及版画陈述仍留在 S2；未写 `relations.csv` 或新增正式关系。
S4 累计登记422组/538条候选映射，待登记4,409组/4,471条；KU 总数1,441。


<a id="s3-cross-chapter-group-review-20261017"></a>

### S3 跨章多候选身份组：分类型核对与 Cesi 拆分（2026-10-17）

从现有 alignment 中筛出29个跨章、多候选 `new` 组；组成员和逐候选来源锚点仍以各 alignment 行为准。未重跑或改写其余已有裁决。类型分布如下：

| 类型 | 原多候选跨章组数 | 处置 |
|---|---:|---|
| archive | 3 | 保留现有 new 组 |
| institution | 1 | 保留现有 new 组 |
| person | 16 | 15组保留；1组拆分为两个独立 new person 组 |
| place | 2 | 保留现有 new 组 |
| term | 4 | 保留现有 new 组 |
| work | 3 | 保留现有 new 组 |
| **合计** | **29** | **28组保留；1组拆分** |

拆分依据：第3章 p.69 明称 `Cardinal Angelo Cesi`，说明他在1606年去世；第二版后记 p.400 称 `Monsignor Angelo Cesi` 为 Cardinal Cesi 的兄弟。两处同名并非同一人物。索引候选 `cand-0639` 保留 `new-person:angelo-cesi-d4e25faff9`；`cand-10945` 单独进入 `new-person:angelo-cesi-monsignor-20261017`。原两行按同名归组的理由完整保存在本过程记录及下文；alignment 当前备注改述明确的兄弟关系。两个新组均待 S4，不复用现有同类型人物 KU。

原裁决理由（保留历史）：

- `cand-0639`：source_ref=candidate=cand-0639;index_entry=C.csv#163;index_pages=69, 70, 400;s2_mentions=m-chp3-secii-l40-52-0011@02-sources/02-Markdown/03_CHP-3_sec_ii.md#L40-52[Angelo;chars=779-785],m-chp3-secii-l40-52-0012@02-sources/02-Markdown/03_CHP-3_sec_ii.md#L40-52[Cesi;chars=786-790],m-chp3-secii-l54-60-0026@02-sources/02-Markdown/03_CHP-3_sec_ii.md#L54-60[Cardinal Angelo Cesi;chars=2063-2083],m-chp3-secii-l54-60-0035@02-sources/02-Markdown/03_CHP-3_sec_ii.md#L54-60[Cardinal Cesi;chars=2444-2457]; group=new-person:angelo-cesi-d4e25faff9; New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-0639, cand-10945 by identical normalized full-name/explicit-alias anchor (angelo cesi), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.
- `cand-10945`：source_ref=candidate=cand-10945;candidate_source_ref=chp-20:20_CHP-20Postscript:l46-57#L53;source_file=02-sources/02-Markdown/20_CHP-20Postscript.md#L46-57;s2_mentions=m-chp20-p400-037@02-sources/02-Markdown/20_CHP-20Postscript.md#L46-57[Monsignor Angelo Cesi;chars=1848-1869]; group=new-person:angelo-cesi-d4e25faff9; New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-0639, cand-10945 by identical normalized full-name/explicit-alias anchor (angelo cesi), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.

未更改原文 statement 端点或 `relations.csv`；兄弟关系仍以 S2 来源陈述为据，不在 S3 新增正式关系。其余28个原多候选跨章组沿用各自已有 `resolution_note`、`process_ref` 和 S4 去向。当前 S3 new=5,009个候选／4,832组；S4已登记422组／538条映射，待登记4,410组／4,471条映射；KU总数1,441。

<a id="s3-pamfili-term-subentry-split-20261017"></a>

### S3 term／work／place：跨章候选身份复核与 Pamfili 子项拆分（2026-10-17）

对29个原跨章多候选 new 组按类型核对：archive 3组、institution 1组、person 16组、place 2组、term 4组、work 3组。其余27组保持原 S3 组；本次新增一项 term 拆分，与前一节 Angelo Cesi 拆分合计2组拆分。结果分布见当前 results 与下表。

| 类型 | 原组数 | 保留 | 拆分 | 拆分后涉及的当前组 |
|---|---:|---:|---:|---:|
| archive | 3 | 3 | 0 | 3 |
| institution | 1 | 1 | 0 | 1 |
| person | 16 | 15 | 1 | 17 |
| place | 2 | 2 | 0 | 2 |
| term | 4 | 3 | 1 | 5 |
| work | 3 | 3 | 0 | 3 |
| **合计** | **29** | **27** | **2** | **31** |

P.csv#19 与 #21 的主项都是人物 `Pamfili, Gianbattista (Pope Innocent X)`，但候选类型为 term，子项分别是“conservative nature of patronage”和“effect of economic retrenchment on artists”。父级人物标题只提供索引语境，不证明两个术语是同一概念。故撤回共享组 `sg3-term-pamfiligianbattistapopeinnocentx`，`cand-1820` → `sg3-term-pamfili-conservative-patronage`，`cand-1822` → `sg3-term-pamfili-retrenchment-effects`；两者均为独立 new term，未匹配到同类型既有 KU。既有 `decline-of-roman-patronage` 是范围更广的章级概念，不作 same 映射。

作品边界复核：`cand-0879` 与 `cand-7720` 同属 Crespi 一幅画。第8章 p.228 记录其 Jupiter/Corybantes 名称，p.222 与第二版后记 p.405 说明同一委托后来以 The Finding of Moses 之名送交以降低关税；两种题名保留为同一 work 的题名变化，不拆成两件作品。`cand-2859`／`cand-10117` 是同一 Zanetti 1760 视觉图册；`cand-2876`／`cand-10111` 是同一 Zompini 版画作品，沿用各自行 alignment group。

地点边界复核：`cand-8375` 与 `cand-11069` 同指 Carlo Cordellina 在 Vicenza 的宅邸；p.160 的“两处住宅”定位与 p.143 开始建造的 Vicenza palace 相合。`cand-8376` 与 `cand-10279` 同指 Montecchio 的 Villa Cordellina，p.160 的 Tiepolo 装饰语境与 p.352 的具名地点相合；不补造建筑正式名称。Dresden Gallery 的机构组、其余跨章人物组及三组 archive 保留原 S3 决定和来源锚点。

本次只更新 S3 group、候选 detail 与过程／结果记录；未更改 S2 statement 端点、`relations.csv` 或 S4 卡片。旧 term/work 对齐理由保留如下：

- `cand-1820`：group=sg3-term-pamfiligianbattistapopeinnocentx; source_ref=chp-6:06_CHP-6_sec_i:l26-36#m-chp6-p148-035; S2 source anchor and type-specific description distinguish a source-supported object/concept not represented by an exact same-type KU; eligible for S4 registration after this decision.
- `cand-1822`：group=sg3-term-pamfiligianbattistapopeinnocentx; source_ref=chp-5:05_CHP-5_sec_i:l17-26#m-chp5-p122-0013; S2 source anchor and type-specific description distinguish a source-supported object/concept not represented by an exact same-type KU; eligible for S4 registration after this decision.
- `cand-0879`：source_ref=entity-candidates.csv#cand-0879;index_entry=C.csv#413;index_source=C.csv;index_pages=228;mentions=m-chp8-p228-infant-title-start,m-chp8-p228-infant-title-rest,m-chp8-p228-finding-title,m-chp20-plate67-001,m-chp20-p405-003,m-chp20-p405-004,m-chp20-p405-006;segments=chp-8:08_CHP-8_sec_ii:l206-214,chp-20:20_CHP-20Postscript:l72-76,chp-20:20_CHP-20Postscript:l137-148;cross_candidates=entity-candidates.csv#cand-7720;candidate_source_ref=chp-8:08_CHP-8_sec_ii:l126-138#L135;mentions=m-chp8-p222-finding-moses-work;segments=chp-8:08_CHP-8_sec_ii:l126-138; group=workgrp-beb5c6c0eb0cbc; S2 的跨候选指针/标题/作者/版本语境支持与配对候选属于同一作品身份组（cand-7720,cand-0879）；现有 work manifest 未有可直接对应的既有 KU，建议 new，组 ID 稳定供 S4 合并登记。
- `cand-7720`：source_ref=entity-candidates.csv#cand-7720;candidate_source_ref=chp-8:08_CHP-8_sec_ii:l126-138#L135;mentions=m-chp8-p222-finding-moses-work;segments=chp-8:08_CHP-8_sec_ii:l126-138;cross_candidates=entity-candidates.csv#cand-0879;index_entry=C.csv#413;index_source=C.csv;index_pages=228;mentions=m-chp8-p228-infant-title-start,m-chp8-p228-infant-title-rest,m-chp8-p228-finding-title,m-chp20-plate67-001,m-chp20-p405-003,m-chp20-p405-004,m-chp20-p405-006;segments=chp-8:08_CHP-8_sec_ii:l206-214,chp-20:20_CHP-20Postscript:l72-76,chp-20:20_CHP-20Postscript:l137-148; group=workgrp-beb5c6c0eb0cbc; S2 的跨候选指针/标题/作者/版本语境支持与配对候选属于同一作品身份组（cand-7720,cand-0879）；现有 work manifest 未有可直接对应的既有 KU，建议 new，组 ID 稳定供 S4 合并登记。

当前 S3 new=5,009/4,833；S4已登记422组/538条映射，待登记4,411组/4,471条映射；KU总数1,441。
<a id="s4-person-endpoints-20261017"></a>

### S3 复用修正与 S4 person：四个直接关系端点登记（2026-10-17）

#### S3 same 复用修正

下列20个单成员候选组经同类型既有 KU 及书内对象语境复核，由 `new` 更正为 `same`。原 `group=`、S3 理由及历史状态保留在各 alignment 行；本次写入既有 KU 映射，不重复建卡。

- `cand-0114` → `units/institutions/arcadia`：The index society is the same Arcadia literary academy already represented by this institution KU.
- `cand-6127` → `units/institutions/schildersbent`：The Roman painters' society named Schildersbent is the same organization; the separate Bentvueghels comparison remains separate.
- `cand-9423` → `units/persons/francis-haskell`：The p.290 note names the author Francis Haskell; the title and copyright pages identify that same author as Francis James Herbert Haskell. The cited 1967 work remains unresolved.
- `cand-2822` → `units/places/residenz-wurzburg`：The Würzburg Residenz place candidate denotes the same palace represented by the existing Residenz, Würzburg KU.
- `cand-4623` → `units/places/berlin`：Berlin is the same city already represented by the existing place KU; this does not resolve which of two paintings is paired with it.
- `cand-4957` → `units/places/palazzo-barberini`：Palazzo Barberini is the same named building; this mapping does not expand the source's tapestry-cartoon custody statement.
- `cand-5120` → `units/places/spain`：Spain is the same geographic place; the political entity and geographic place remain distinct by type.
- `cand-5667` → `units/places/spain`：Spain is the same geographic place named in the report; the reported event remains unverified.
- `cand-5696` → `units/places/st-peters-basilica`：St Peter's Basilica is the same named building; the excavation context does not add an institutional identity.
- `cand-6232` → `units/places/tuscany`：Tuscany is the same geographic region named in Rosa's letter.
- `cand-7200` → `units/places/england`：England is the same geographic place named in Haskell's patronage comparison.
- `cand-7287` → `units/places/versailles`：Versailles is the same place already represented by the existing place KU; the official style remains a distinct term.
- `cand-7473` → `units/places/new-york`：New York is the same city named as the reported Metropolitan Museum location.
- `cand-9904` → `units/places/venice`：Venice in the p.313 note is the same city as the existing place KU; the prior S3-deferred wording is superseded.
- `cand-10171` → `units/places/tuscany`：Tuscany in Pasquali's quoted letter is the same region as the existing place KU; the prior S3-deferred wording is superseded.
- `cand-10318` → `units/places/ca-rezzonico`：Cà Rezzonico is the same named place as the existing KU; the source's pairing of two titles with two locations remains unspecified.
- `cand-9114` → `units/terms/bamboccianti`：Bamboccianti is the same art-historical group/style term already represented by the accepted term KU.
- `cand-4477` → `units/works/pietro-da-cortona-rape-of-the-sabines`：The large Sacchetti canvas named by Haskell is the same Pietro da Cortona work as the existing plate-10a work KU; no additional version is implied.
- `cand-5991` → `units/works/claude-view-of-delphi-with-a-procession`：The Claude Lorrain painting named in the source and identified as plate 19b is the same work as the existing KU.
- `cand-6026` → `units/works/caravaggio-death-virgin`：The Caravaggio painting shown in 1607 is the same named work as the existing Death of the Virgin KU; the source-local display claim is not expanded.

`cand-9904` 与 `cand-10171` 的候选 detail 中“S3 deferred”措辞已追加当前复用去向；原说明保留。未改变其余 `conflict`、`undecided` 或 `excluded` 决定。

#### S4 person 新登记

四个 source-local person 组各登记一张 KU。姓名中文形式均为项目工作音译；卡片限于 Haskell 书内原文及索引，不补传记或外部身份事实。每组均有6条直接 S2 关系候选，卡片列明 statement ID；本批没有写入 `relations.csv`，所有关系仍待 S6。

| 候选／身份组 | KU | 书内锚点 | S2 关系候选 |
|---|---|---|---:|
| `cand-2512` / `new-person:cristoforo-storer-61583f1ac4` | `units/persons/cristoforo-storer` | 第8章，印刷页216；OCR L23–25 与索引 S.csv#201 | 6 |
| `cand-0911` / `new-person:david-ludovico-7f9314f137` | `units/persons/ludovico-david` | 第8章，印刷页220；OCR L106 与索引 D.csv#13 | 6 |
| `cand-1365` / `new-person:de-lattre-pierre-22a7f370a1` | `units/persons/pierre-de-lattre` | 第3章，印刷页74；OCR L121–122 与索引 L.csv#22 | 6 |
| `cand-1636` / `new-person:melanconici-niccolo-ef1abca9c3` | `units/persons/niccolo-melanconici` | 第8章，印刷页220–221；OCR L110、113 与索引 M.csv#176 | 6 |

四张卡包含双语规范标题与等义描述、书内来源摘录、精确行和印刷页，以及关系与证据段。Storer 的“Swiss artist”与 David 的“Swiss painter”仅作为 Haskell 原文称谓，不推定出生地或国籍；de Lattre 的 OCR “Coliegio”保留转录状态。

#### Luigi Pavini 端点引用修正

`st-chp9-p269-n05` 的 `subject_candidate_id` 现映射至 `cand-12425`，并将其纳入 `mentioned_candidate_ids`。原书中 Luigi Pavini 为小册子出版者的书目信息不变；旧的“无候选”说明从当前 statement 语义中移除，历史过程仍保留在本文件前文与 backlog 记录。该 statement 仍是 S2 关系候选，正式边待 S6；Luigi 卡片的 `process_ref` 锚点现已在本文件落位，并补上待审关系入口。backlog `bl-0001` 继续保持 completed。


<a id="s3-adami-portrait-collection-type-review-20261017"></a>

### S3 修正：Luigi Adami 人物与肖像收藏索引子目分流（2026-10-17）

`A.csv#13`（`cand-0014`）是 Luigi Adami 人物主项，继续保留 `new-person:adami-luigi-02deb86d77`。`A.csv#14`（`cand-0015`）的子目明确是 “collection of portraits of distinguished men”；第6章 p.158 的两条陈述把该对象作为 Adami 的肖像收藏端点，并另行将 Lord Essex 与 Francesco Drach 的画像列为其中对象。因此 `cand-0015` 不是第二条 Luigi Adami 人物候选，不再与 cand-0014 共用人物组。

项目 taxonomy 的 `work` 表达可辨认艺术作品、构件和设计对象，`archive` 表达文献与档案，`term` 表达概念与术语；当前类型没有忠实表达私人艺术品收藏这一集合对象的类别。故 `cand-0015` 的 suggested_type 清空，S3 决定改为 `undecided`，保留候选、索引子目、S2 端点和原组理由；不将收藏强塞为 person/work/archive/term。两条描述画像所收对象的 statement 资格说明同步为“类型待决”，不新增形式关系。相关关系端点待类型裁决后再进入 S4/S6。

### S4 person：Luigi Adami 人物登记（2026-10-17）

仅登记 `cand-0014`，映射至 `units/persons/luigi-adami`。卡片以第6章 p.158 和索引 A.csv#13 为依据，记录 Haskell 对 Adami 的肖像收藏兴趣及其对1667年书信内容的转述。中文名为项目工作音译。人物的2条直接 S2 关系候选仍待 S6；肖像收藏 `cand-0015` 不进入人物卡映射，也没有写入 `relations.csv`。


<a id="s4-person-endpoints-20261017b"></a>

### S4 person：三个直接关系端点身份组登记（2026-10-17）

三个候选均为独立的单成员 person new 组，现各登记一张 KU。卡片的名称和描述均以索引、正文或注释为据；不补外部传记信息。每组的5条 S2 关系候选保留待 S6，未写入正式关系。

| 候选／身份组 | KU | 书内锚点 | 待审关系候选 |
|---|---|---|---:|
| `cand-0788` / `new-person:august-clemens-cologne-elector-of-a0fd03e59b` | `units/persons/clemens-august-elector-cologne` | 第10章，印刷页295–296；OCR L316、319 与索引 C.csv#312 | 5 |
| `cand-1001` / `new-person:daniele-farsetti-fe28988990` | `units/persons/daniele-farsetti` | 第15章，印刷页363；OCR L35 与索引 F.csv#16 | 5 |
| `cand-2686` / `new-person:giuseppe-valletta-5ab1f14845` | `units/persons/giuseppe-valletta` | 第8章，印刷页204；OCR L17–18、129（注3） 与索引 UVWXYZ.csv#22 | 5 |

Daniele Farsetti 的 p.363 OCR 日期连写及 “exhibitionof” 转录保留在原始摘录中，本卡描述不依赖日期校正。Clemens August 的“younger brother”及 Valletta 的 patronage／friendship 陈述仅保留为 S2 候选；不由卡片登记代替关系审查。


<a id="s4-person-endpoints-20261017c"></a>

### S4 person：三位画家直接关系端点登记（2026-10-17）

三个候选均为单成员 person new 身份组，正文与索引可互相定位，现各登记一张 KU。卡片仅记录来源支持的身份和语境；直接 S2 关系候选保留待 S6，没有新增正式关系。

| 候选／身份组 | KU | 书内锚点 | 待审关系候选 |
|---|---|---|---:|
| `cand-1632` / `new-person:livio-mehus-0c1b46a467` | `units/persons/livio-mehus` | 第8章，印刷页213、240；Markdown L116、351 与索引 M.csv#172 | 3 |
| `cand-1743` / `new-person:giuseppe-nogari-a391e671c6` | `units/persons/giuseppe-nogari` | 第9章印刷页200；第10章印刷页316；Markdown L204–206、116–117 与索引 N.csv#23 | 3 |
| `cand-1047` / `new-person:fontebasso-francesco-76776557de` | `units/persons/francesco-fontebasso` | 第9章印刷页272；第10章印刷页297；第13章印刷页339；Markdown L54–55、340–341、75–76 与索引 F.csv#62 | 4 |

Mehus 关于其去世可能使其未能直接为费迪南多工作的说法保留为 Haskell 的推断；Nogari 与 Foscarini、Schulenburg 的肖像／委托表述，以及 Fontebasso 的作品与工作关系仍按 S2 候选待 S6 审查。中文名均注明为项目工作音译。


<a id="s4-person-endpoints-20261017d"></a>

### S4 person：三组跨章人物端点登记（2026-10-17）

三个候选各自属于单成员 person new 身份组，均有索引主项及正文身份锚点；Henry 与 Ottavio 的姓名按来源可确证范围呈现。各组分别登记一张人物 KU。14 条直接 S2 关系候选保留待 S6，未新增正式关系。

| 候选／身份组 | KU | 书内锚点 | 待审关系候选 |
|---|---|---|---:|
| `cand-2133` / `new-person:paolo-renier-809f039f6e` | `units/persons/paolo-renier` | 第9章印刷页257；第15章印刷页371–372；Markdown L170、83、86–87 与索引 Q-R.csv#60 | 5 |
| `cand-1979` / `new-person:first-henry-of-portland-5343884e1e` | `units/persons/henry-first-duke-portland` | 第10章印刷页279–280；Markdown L49、52–55 与索引 P.csv#181 | 5 |
| `cand-2286` / `new-person:del-ottavio-rosso-c602335dc8` | `units/persons/ottavio-del-rosso` | 第8章印刷页210–211；Markdown L82、85–87、96 与索引 Q-R.csv#214 | 4 |

Ottavio p.211 的 OCR 将 Bishop 识别为“Bjshop”，卡片保留原始转录并在描述中按语境释读，未作外部核验。Henry 以书中给出的 Henry 和 Portland 公爵头衔作双语展示，不补未见于本书的名字。


<a id="s4-person-endpoints-20261017e"></a>

### S4 person：三组跨章人物端点登记（2026-10-17）

三个候选均为单成员 person new 身份组，具索引主项及跨章正文锚点；类型与身份边界按现有 S3 决定登记。各组分别登记一张人物 KU。15 条直接 S2 关系候选保留待 S6，未新增正式关系。

| 候选／身份组 | KU | 书内锚点 | 待审关系候选 |
|---|---|---|---:|
| `cand-1740` / `new-person:goswin-nickel-8976064042` | `units/persons/goswin-nickel` | 第3章印刷页78、91；Markdown L24、160 与索引 N.csv#20 | 5 |
| `cand-1705` / `new-person:francesco-morosini-b34af6f696` | `units/persons/francesco-morosini` | 第9章印刷页246、248–249；Markdown L21–22、41、79–80 与索引 M.csv#246 | 5 |
| `cand-0922` / `new-person:diziani-gaspare-4eb64b5752` | `units/persons/gaspare-diziani` | 第6章印刷页165；第10章印刷页278、294；Markdown L40、30–31、293 与索引 D.csv#24 | 5 |

Nickel 与 Morosini 的卡片保留 Haskell 对人物及事件的来源表述，不扩展为外部履历。Diziani 的舞台布景委托候选跨第6、10章对应其人物端点；正式关系仍待 S6。


<a id="s4-person-endpoints-20261017f"></a>

### S4 person：三组人物直接关系端点登记（2026-10-17）

三个候选均为单成员 person new 身份组，索引主项与正文提供交叉身份锚点，现分别登记一张人物 KU。14 条直接 S2 关系候选保留待 S6；没有新增正式关系。

| 候选／身份组 | KU | 书内锚点 | 待审关系候选 |
|---|---|---|---:|
| `cand-2035` / `new-person:antonio-carlo-dal-pozzo-7658578989` | `units/persons/carlo-antonio-dal-pozzo` | 第4章印刷页100、104、113；后记印刷页400；Markdown L21、63、162；后记L55 与索引 P.csv#238 | 5 |
| `cand-1896` / `new-person:iv-of-philip-spain-12d022dbb2` | `units/persons/philip-iv-spain` | 第4章印刷页116；第7章印刷页172；Markdown L199–200、32–35 与索引 P.csv#97 | 5 |
| `cand-0928` / `new-person:daniele-dolfin-iv-16ea57c49e` | `units/persons/daniele-dolfin-iv` | 第9章印刷页252；Markdown L119–122 与索引 D.csv#30 | 4 |

Carlo Antonio dal Pozzo 与 Cassiano dal Pozzo 是兄弟，分别映射各自人物卡；Philip IV 按跨章索引人物主项登记；Daniele IV Dolfin 与已登记的 Daniele III Dolfin 区分。以上边仍待 S6 审查。


<a id="s4-person-endpoints-20261017g"></a>

### S4 person：Gabriel Naudé、Giorgio Maria Rapparini 与 Ottavio Vannini 登记（2026-10-17）

按 S3 的三个 person new 单人组各登记一个 KU，共保留 12 条已标记的直接关系候选供 S6 审查；本批没有将候选断言写入正式关系。Naudé 的跨章姓名锚点由第2、4、7章及索引互相支持；Rapparini 第282页姓名在 OCR 转录中连写，索引主条目提供分词形式，原引句保留原转录；Vannini 的记录限定于第8章所载家族礼拜堂、作品与作者评价。未引入外部身份或传记资料。

| 候选 / S3 身份组 | KU | 来源与索引锚点 | 直接关系候选 |
|---|---|---|---:|
| cand-1726 / new-person:gabriel-naude-260f2e8c57 | units/persons/gabriel-naude | 第2章，印刷页33，Markdown L27–28；第2章，注3，Markdown L155；第4章，印刷页107，Markdown L106–107；第4章，印刷页108–109，Markdown L117–120；第7章，印刷页177，Markdown L95；索引 N.csv#6 | 4 |
| cand-2107 / new-person:giorgio-maria-rapparini-2fa43bcc34 | units/persons/giorgio-maria-rapparini | 第10章，印刷页282，Markdown L142–143；第10章，注1，Markdown L520；第10章，印刷页283，Markdown L153；索引 Q-R.csv#34 | 4 |
| cand-2694 / new-person:ottavio-vannini-9f4cacf09c | units/persons/ottavio-vannini | 第8章，印刷页212，Markdown L99–101；索引 UVWXYZ.csv#30 | 4 |



<a id="s4-person-endpoints-20261017h"></a>

### S4 person：Giovanni Bottari、Federico Barocci 与 Giulio Romano 登记（2026-10-17）

按 S3 的三个跨章 person new 身份组各登记一个 KU，共保留 9 条直接关系候选供 S6 审查；没有把来源中的请求、群体性作品归属、艺术比较或转引归属提升为正式关系。Bottari 的跨章姓氏命中主要是书目引注，以第14章 p.348 的全名和关系上下文作为卡片依据；Barocci 的英文全名跨行出现，由正文其他页及索引相互支持；Giulio Romano 的法文异名 Jules Romain 按 S3 与索引主条目对齐，Brienne 的作品归属仍为被引来源的说法。未引入外部身份或传记资料。

| 候选 / S3 身份组 | KU | 跨章来源与索引锚点 | 直接关系候选 |
|---|---|---|---:|
| cand-0417 / new-person:bottari-giovanni-634e17e1ce | units/persons/giovanni-bottari | 第14章，印刷页348，Markdown L21；索引 B.csv#264 | 2 |
| cand-0247 / new-person:barocci-federico-c04914b5a3 | units/persons/federico-barocci | 第2章，印刷页26，Markdown L56–58；第3章，印刷页69，Markdown L49；第3章，印刷页76，Markdown L142；索引 B.csv#94 | 4 |
| cand-1194 / new-person:giulio-romano-864f91350e | units/persons/giulio-romano | 第2章，印刷页30，Markdown L113–115；第10章，印刷页312，Markdown L21–23；第7章，印刷页186，Markdown L216；索引 G.csv#101 | 3 |



<a id="s3-person-alias-reuse-20261017"></a>

### S3 person：Ribera 与 Baldassare Franceschini 的既有身份复用（2026-10-17）

复核 S3 的两个 person new 决定时发现已登记人物卡中的姓名变体。两项均改判为 same 并指向原 KU；原 new 决定及组 token 保留在 alignment resolution_note 的 superseded 历史中，当前身份组改并入既有 same 组。此处理只裁决身份，不确认相关关系候选，也不把外部来源内容写入人物卡。

| 候选 | 先前决定 | 当前决定 / KU | 身份比较与依据 |
|---|---|---|---|
| cand-2140 / Q-R.csv#67 | new | same / units/persons/ribera | Haskell第5章 p.120称“the Spaniard Giuseppe Ribera”，并以画家语境叙述；既有KU题名为Jusepe de Ribera，且承接同书图版目录Ribera条目。Saint Louis Art Museum 记录将 Giuseppe de Ribera 列为 Jusepe de Ribera 的异名，身份层面支持复用；其记录亦列 lo Spagnoletto、Spanish (active Italy)、约1590–1652，并链接Getty ULAN与美国国会图书馆规范档。访问日期2026-10-17；记录ID为 https://www.slam.org/collection/constituents/851/。|
| cand-1066 / F.csv#81 | new | same / units/persons/baldassare-franceschini | 本书索引和第20章使用Baldassare Franceschini，并将其与il Volterrano并称；既有KU明确以Baldassarre Franceschini为规范名，同时在名称表记录原书形式Baldassare Franceschini及别名il Volterrano。复用既有KU，不需外部来源。|

主 S3 决策统计：same 1,837→1,839；new groups 4,813→4,811；S4 待登记组 4,365→4,363。Ribera 外部身份链接作为独立 alignment 行保存；不向 sources.csv 或 enrichment.jsonl 复制身份链接。


<a id="s3-index-only-work-crosscandidate-20261017"></a>

### S3 work：索引子目与正文候选跨来源合组（2026-10-17）

两条原为 `undecided` 的索引-only work 候选，现与已有正文锚点的候选合入同一新身份组。裁决依赖精确题名、创作者或索引层级以及原书正文锚点；不重复建组，也不因合组提前登记正式关系。

| 索引候选 | 正文候选／身份组 | S3 去向 | 证据与保留项 |
|---|---|---|---|
| cand-1238 | cand-9154 / `workgrp-d20da8ada884b0` | `new`，同组单一未来 KU | G.csv#148 is an index subentry under Giacomo Guarana and names Sacrifice of Iphigenia on p. 297. The same printed page's S2 statement names that painting, its artist, Moscow destination, and 1762 date. The index-only candidate therefore joins the existing S2 work identity group; it does not create a second work group.；索引和正文均定位 p. 297 |
| cand-1840 | cand-7885 / `workgrp-ec542d23614466` | `new`，同组单一未来 KU | P.csv#40 is an index subentry under Parmigianino, Francesco and names the Madonna del Collo Lungo. S2 independently anchors the same full title, attributed to Parmigianino, in the body candidate cand-7885. The printed index locator is p. 222 while the body anchor is p. 232; the locator discrepancy is retained and not silently corrected. The exact title and creator identify one source-local work, so the index candidate joins the existing work group.；索引页码与正文页码差异保留 |


<a id="s4-person-endpoints-20261017i"></a>

### S4 person：Giacomo Guarana、Domenico Fetti 与 Parmigianino 登记（2026-10-17）

S3 的三个跨章 person `new` 身份组均经同类型既有 KU 与别名检索复核，未发现可复用的现有人物卡；每组各登记一个 KU。Guarana 的索引主项与正文全名相合，第10、15章转录中的 Guaraña 保留为异写；人物候选 `cand-1237` 与作品索引子项 `cand-1238`分属 person/work，后者已在本轮 S3 合入正文作品组。第9章 Markdown 页码层写作200，但PDF物理第22页页图清楚显示印刷页260；人物卡引用页图并保留该转录差异。Fetti 的规范词头沿用印本校勘结果：索引p.454印本为Fetti，CSV与Markdown转录为Feti。Parmigianino 的索引姓名及第2、4、5、8、13章的来源语境支持同一人物候选。未加入外部身份记录或补写来源未载的人物传记；6条S2关系候选均保留待S6，未写入正式边。

| 候选 / S3 身份组 | KU | 跨章来源与索引锚点 | 直接关系候选 |
|---|---|---|---:|
| `cand-1237` / `new-person:giacomo-guarana-04ff210452` | `units/persons/giacomo-guarana` | 第9、10、13、15章；索引 G.csv#147 | 3 |
| `cand-1033` / `new-person:domenico-fetti-d78526d512` | `units/persons/domenico-fetti` | 第7、9、18、19章；索引 F.csv#48 | 2 |
| `cand-1839` / `new-person:francesco-parmigianino-f05afd0c44` | `units/persons/francesco-parmigianino` | 第2、4、5、8、13章；索引 P.csv#39 | 1 |



<a id="s3-person-reuse-and-name-collision-20261017"></a>

### S3 person：既有人物复用与同名爵位分界（2026-10-17）

本批复核3个人物身份组：2组改为复用现有KU，另1组保留new并写明同名爵位下的人物区分。原new决定及理由保存在alignment.csv的resolution_note历史段。

| 候选 | 原S3组 | 当前决定 | 身份去向 |
|---|---|---|---|
| `cand-0092`、`cand-0093` | `new-person:ameyden-dirk-dccff413fe` | `same` | `units/persons/ameyden`；Relatione文献卡保持独立archive类型 |
| `cand-2624` | `new-person:domenico-gian-tiepolo-86ddd4979f` | `same` | `units/persons/giandomenico-tiepolo`；与父亲Giambattista分开 |
| `cand-1524` | `new-person:carlo-ferdinando-mantua-of-66e2b330e3` | `new` | 保持独立；与较早的`units/persons/ferdinando-duke-of-mantua`不是同一人 |

同名爵位比较依据为书内姓名与时间语境：既有KU的Ferdinando是Marie de Medici的侄子、Vincenzo之子，见第7章p.175；cand-1524是Ferdinando Carlo Gonzaga，索引页码p.267、312并对应第9、10章晚期Mantua语境。该组继续待S4登记。


<a id="s4-person-endpoints-20261017j"></a>

### S4 person：Ferdinando Carlo Gonzaga、Emilio Altieri 与 Francis Bacon 登记（2026-10-17）

三个单成员跨章person `new` 组各登记一个KU，补齐双语描述、原书与索引证据、alignment候选映射及可点击的身份入口。Ferdinando Carlo Gonzaga与既有的Ferdinando, Duke of Mantua经姓名、世代及年代语境区分；Emilio Altieri作为人物与Altieri家族对象分开；Francis Bacon的ch.4转引拼写Baccon保留为来源异文。共14条直接S2关系候选继续待S6审查；本批未新增正式关系或外部身份记录。

| 候选 / S3身份组 | KU | 跨章锚点 | 直接关系候选 |
|---|---|---|---:|
| `cand-1524` / `new-person:carlo-ferdinando-mantua-of-66e2b330e3` | `units/persons/ferdinando-carlo-gonzaga` | 第9、10章；索引 M.csv#61 | 5 |
| `cand-0087` / `new-person:altieri-emilio-clement-x-0c9723ef22` | `units/persons/emilio-altieri-pope-clement-x` | 第4、6章；索引 A.csv#88 | 5 |
| `cand-0155` / `new-person:bacon-francis-e77bd98874` | `units/persons/francis-bacon` | 第4、10、15章；索引 B.csv#2 | 4 |



<a id="s4-poleni-crosschapter-person-20261017"></a>

### S3→S4 person：Giovanni Poleni 跨章身份组复核与登记（2026-10-17）

索引候选 `cand-1968`（P.csv#169）与正文候选 `cand-9182` 合并登记为一个人物 KU。第10章 p.301 给出全名 Marchese Giovanni Poleni；同章注4转述1747年致 Smith 的两封信；第15章 p.367 以 Marchese Poleni 指称 Canova 受委制作雕像的对象。正文全名与索引主项的倒置姓名相合，且 p.367 的称号与其吻合，支持跨章同一身份。索引所列 p.201 保留为定位，但当前 S2 提及未映射该页，本裁决不以该页码单独作证。未查阅注4所述原信，也未引入外部身份记录。两条候选共同映射至一个 KU；3 条直接关系候选留待 S6，未登记正式关系。

| 候选 / S3身份组 | KU | 身份证据锚点 | 直接关系候选 |
|---|---|---|---:|
| `cand-1968`、`cand-9182` / `new-person:giovanni-poleni-8cd50ead76` | `units/persons/giovanni-poleni` | 第10章 p.301；第15章 p.367；P.csv#169 | 3 |


<a id="s4-richmond-title-identity-20261017"></a>

### S3→S4 person：里士满公爵身份组复核与登记（2026-10-17）

S3 correction (2026-10-17): the prior note incorrectly called 'Duke of Richmond' a full personal name and described the grouping as a normalized full-name match. The cited passages provide a title only. The group is retained as one source-local person because p.287 names Lord March as becoming Duke in 1723, p.288 cites McSwiny's letter to the Duke in 1727, and pp.289–291 continue with the Duke in the same British Worthies sequence. No full personal name is inferred; it remains unverified. 两条索引候选共同映射至一个标题式人物 KU；完整个人姓名仍待证。6条直接关系候选留待 S6，未登记正式关系。

| 候选 / S3身份组 | KU | 身份证据锚点 | 直接关系候选 |
|---|---|---|---:|
| `cand-2193`、`cand-2194` / `new-person:of-richmond-9053928efd` | `units/persons/duke-of-richmond-mcswiny-british-worthies` | 第10章 p.287–291；Q-R.csv#120–121 | 6 |


<a id="s3-s4-osservatore-veneto-periodical-20261017"></a>

### S3 archive→S4：Osservatore Veneto 期刊题名裁决与登记（2026-10-17）

`cand-1791`（O.csv#26）由 `undecided` 改为 `new`，进入一个题名层级 archive 组。第10章p.323明确称《Osservatore Veneto》为Gasparo Gozzi编辑的期刊；p.324注2给出1761年2月14日期号，作为Gozzi评论Longhi的出处。原待证理由所指的版次/期号缺口不妨碍确定期刊题名本身；卡片不声称已查阅该期，也不另建期号KU。S2直接关系候选 `st-chp10-p323-gozzi-edits-osservatore-along-spectator-lines` 留待S6，未新增正式关系。

[archive卡片](../../../04-knowledge/units/archives/osservatore-veneto-periodical.md)；对齐决定保留在alignment.csv，候选详情记录题名层级与期号边界。


<a id="s4-crosschapter-person-groups-20261017k"></a>

### S4 person：三组跨章人物身份登记（2026-10-17）

复核三组既有person `new` 身份组的索引词头、跨章正文锚点与既有同类型KU；未发现可复用人物卡，分别登记一个KU。只记录原书所支持的姓名、称号及语境，不增补外部传记；书内关系断言继续留待S6逐条审查。

| 候选 / S3身份组 | KU | 跨章锚点 | 直接关系候选 |
|---|---|---|---:|
| `cand-1607` / `new-person:cosimo-de-iii-medici-098cd59653` | `units/persons/cosimo-iii-de-medici` | 第8、20章；索引 M.csv#147 | 4 |
| `cand-2814` / `new-person:england-iii-of-william-d840b96e5c` | `units/persons/william-iii-of-england` | 第7、10章；索引 UVWXYZ.csv#151 | 4 |
| `cand-1295` / `new-person:france-henri-iv-of-95c1a45df8` | `units/persons/henri-iv-of-france` | 第2、7章；索引 H.csv#11 | 4 |



<a id="s3-s4-rezzonico-person-boundary-20261017"></a>

### S3→S4 person：Aurelio 与 Carlo Rezzonico 身份分立复核与登记（2026-10-17）

p.254明确称Carlo是Aurelio的兄弟，且Carlo当选Clement XIII；第15章p.362给出Carlo Rezzonico全名，p.363继续指称该教皇。两人维持独立S3 person new组；Rezzonico family、Ca’ Rezzonico地点及Tiepolo婚姻寓意作品保持不同KU。Clement XIII索引redirect不另立人物，既有Clement XI卡亦非同一人。Q-R.csv#64将页码录为254、323，而原索引转录列为254、362–363；两种读数均保留，candidate index_page_range沿原索引转录。分别登记两张人物卡，8条直接关系候选留待S6。

| 候选 / S3身份组 | KU | 来源锚点 | 直接关系候选 |
|---|---|---|---:|
| `cand-2136` / `new-person:aurelio-rezzonico-02891a7a00` | `units/persons/aurelio-rezzonico` | 第9章；索引 Q-R.csv#63 | 4 |
| `cand-2137` / `new-person:carlo-rezzonico-clement-xiii-5d6bd47b3c` | `units/persons/carlo-rezzonico-pope-clement-xiii` | 第9、15章；索引 Q-R.csv#64 / 原索引转录 | 4 |



<a id="s4-crosschapter-person-endpoints-mead-maderno-zanetti-20261017"></a>

### S3→S4 person：Mead、Maderno 与 Zanetti 跨章身份组登记（2026-10-17）

按候选全名、索引页码及跨章正文/注释锚点复核三个person new组。cand-1477与cand-4873共用Carlo Maderno组；第2章p.27的Maderno仅是中殿方案语境中的具名建筑师，紧接的迁居Spoleto及任主教叙述不归给他。cand-2861与cand-9280共用Girolamo Zanetti组；第10章p.306明确称Anton Maria为Girolamo之兄，故与既有Anton Maria Zanetti the Elder卡区分。Richard Mead由第4章p.118全名、索引和第10、14章的称谓/收藏语境连接。未引入外部身份断言；8条S2直接关系候选继续留待S6。

| 候选 / S3身份组 | KU | 跨章锚点 | 直接关系候选 |
|---|---|---|---:|
| `cand-1604` / `new-person:mead-richard-ffc4adb9cf` | `units/persons/richard-mead` | 第4、10、14章；索引 M.csv#144 | 3 |
| `cand-1477, cand-4873` / `new-person:carlo-maderno-530c4fdfa7` | `units/persons/carlo-maderno` | 第2、3章及 Postscript；索引 M.csv#14 | 3 |
| `cand-2861, cand-9280` / `new-person:girolamo-zanetti-2aceef0ec5` | `units/persons/girolamo-zanetti` | 第9、10、14章；索引 UVWXYZ.csv#198 | 2 |



<a id="s4-crosschapter-person-endpoints-resta-palladio-walpole-20261017"></a>

### S3→S4 person：Sebastiano Resta、Andrea Palladio 与 Horace Walpole 登记（2026-10-17）

按索引主项和多章正文/注释全名、称谓及语境复核三个person new组。Resta的第3章p.77全名、第6章p.155身份描述与第5、8章书信引用相合；Palladio的索引全名与第4、10、14章及Postscript中的建筑师语境相合；Walpole由第9章p.264全名连接至第10、14章的姓氏提及，其中1738年购画仍为计划。三组均无现成同类型人物KU；未引入外部身份断言。6条S2直接关系候选留待S6。

| 候选 / S3身份组 | KU | 跨章锚点 | 直接关系候选 |
|---|---|---|---:|
| `cand-2134` / `new-person:resta-sebastiano-912fe4613b` | `units/persons/sebastiano-resta` | 第3、5、6、8章；索引 Q-R.csv#61 | 2 |
| `cand-1807` / `new-person:andrea-palladio-5e91b207a4` | `units/persons/andrea-palladio` | 第4、10、14章及 Postscript；索引 P.csv#6 | 2 |
| `cand-2798` / `new-person:horace-walpole-71c5b539dc` | `units/persons/horace-walpole` | 第9、10、14章；索引 UVWXYZ.csv#135 | 2 |



<a id="s4-crosschapter-person-endpoints-vecchia-galgario-zeno-20261017"></a>

### S3→S4 person：Pietro della Vecchia、Fra Galgario 与 Apostolo Zeno 登记（2026-10-17）

按索引主项及跨章正文锚点复核三个person new组。Pietro della Vecchia由第7章p.193全名连接至第13章p.340和第16章p.376；后者OCR读作“Pietrp”，保留原样，第7章关于Giorgione伪作的表述仍是Haskell的判断。Fra Galgario与Vittore Ghislandi按G.csv#8的同一索引词头合组；第7章注释另有“Gliislandi”转录异文。Apostolo Zeno由第8章p.230和第10章p.300的同名全称跨章锚定。无外部身份资料写入，6条S2关系候选继续留待S6。

| 候选 / S3身份组 | KU | 跨章锚点 | 直接关系候选 |
|---|---|---|---:|
| `cand-2707` / `new-person:della-pietro-vecchia-bd2908fb58` | `units/persons/pietro-della-vecchia` | 第7、13、16章；索引 UVWXYZ.csv#43 | 3 |
| `cand-1101` / `new-person:fra-galgario-ghislandi-vittore-8b50b26f92` | `units/persons/fra-galgario-vittore-ghislandi` | 第6、7章；索引 G.csv#8 | 2 |
| `cand-2869` / `new-person:apostolo-zeno-9866a1a3e7` | `units/persons/apostolo-zeno` | 第8、10章；索引 UVWXYZ.csv#206 | 2 |



<a id="s4-crosschapter-person-endpoints-mazza-goya-mattielli-20261017"></a>

### S3→S4 person：Giuseppe Mazza、Francisco Goya 与 Lorenzo Mattielli 登记（2026-10-17）

按索引全名及跨章正文提及复核三个person new组。Giuseppe Mazza由第8章p.222、p.227及第9章p.251的全名锚定；Francisco Goya由索引全名连接至第7章p.192和第10章p.297注的“young Goya”语境，原书影响判断不作外部验证；Lorenzo Mattielli由第7章p.201与第14章p.353的雕塑/喷泉语境连接。无外部身份资料写入，6条S2直接关系候选留待S6。

| 候选 / S3身份组 | KU | 跨章锚点 | 直接关系候选 |
|---|---|---|---:|
| `cand-1602` / `new-person:giuseppe-mazza-c434d5ebb3` | `units/persons/giuseppe-mazza` | 第8、9章；索引 M.csv#141 | 2 |
| `cand-1216` / `new-person:francisco-goya-8314253007` | `units/persons/francisco-goya` | 第7、10章；索引 G.csv#124 | 2 |
| `cand-1584` / `new-person:lorenzo-mattielli-e53f3c6116` | `units/persons/lorenzo-mattielli` | 第7、14章；索引 M.csv#123 | 2 |



<a id="s4-crosschapter-person-endpoints-cigoli-ciampelli-anne-20261017"></a>

### S3→S4 person：Cigoli、Ciampelli 与 Anne, Queen of England 登记（2026-10-17）

按索引词头、跨章全名/称名锚点及既有同类型KU复核三组person `new` 身份组；均未发现可复用人物卡，各组各登记一个KU。Cigoli由第2、4章及C.csv#280归组；Ciampelli由第2、3章及C.csv#268归组，并保留第3章OCR异文“Ciampelh”；Anne依据第7章明名、索引A.csv#111与第10章上下文归组，第10章p.281 OCR异文“Queen Arme”保留。未加入外部身份事实。10条S2直接关系候选仍待S6逐条审查，本批未新增正式关系边。

| 候选 / S3身份组 | KU | 跨章锚点 | 直接关系候选 |
|---|---|---|---:|
| `cand-0756` / `new-person:cigoli-ludovico-39b93eea0c` | `units/persons/ludovico-cigoli` | 第2、4章；索引 C.csv#280 | 4 |
| `cand-0744` / `new-person:agostino-ciampelli-64c825d6b8` | `units/persons/agostino-ciampelli` | 第2、3章；索引 C.csv#268 | 3 |
| `cand-0110` / `new-person:anne-england-of-1cb5af41f1` | `units/persons/anne-queen-of-england` | 第7、10章；索引 A.csv#111 | 3 |



<a id="s4-crosschapter-person-endpoints-james-rode-milton-20261017"></a>

### S3→S4 person：James II、Bernhard Rode 与 John Milton 登记（2026-10-17）

按索引词头、跨章称名锚点及既有同类型KU复核三组person `new` 身份组；均未发现可复用人物卡，各组各登记一个KU。James II由J，K.csv#1与第7、10章锚定，OCR“James H”异文保留；Bernhard Rode由第14章姓氏提及、Postscript第20章全名及Q-R.csv#134归组，画作归属争议单独保留；John Milton由第2、4章正文与M.csv#208归组，第10章p.319另有Milton提及但不在索引页码范围内。未加入外部身份事实。8条S2直接关系候选仍待S6逐条审查，本批未新增正式关系边。

| 候选 / S3身份组 | KU | 跨章锚点 | 直接关系候选 |
|---|---|---|---:|
| `cand-1317` / `new-person:england-ii-james-of-95bd33d65c` | `units/persons/james-ii-of-england` | 第7、10章；索引 J，K.csv#1 | 3 |
| `cand-2207` / `new-person:bernhard-rode-f729759924` | `units/persons/bernhard-rode` | 第14、20章；索引 Q-R.csv#134 | 3 |
| `cand-1668` / `new-person:john-milton-f3686fb04d` | `units/persons/john-milton` | 第2、4、10章；索引 M.csv#208 | 2 |



<a id="s4-crosschapter-person-endpoints-dominici-sartori-viero-20261017"></a>

### S3→S4 person：Bernardo de Dominici、Felicita Sartori 与 Teodoro Viero 登记（2026-10-17）

按S3身份组、跨章原书锚点及同类型KU复核三组person `new`；每组登记一个KU。Bernardo de Dominici组含cand-0942与cand-7116：第21章书目L430给出作者全名，第7章p.189注6的De Dominici卷IV短引及第8章p.207–208、p.224注4相连，索引D.csv#44提供同名词头；四卷本全集cand-11317与卷IV引用候选cand-4835仍是独立archive候选。Felicita/Félicita Sartori由第10、13章和S.csv#51归组；Teodoro Viero由第13、15章和UVWXYZ.csv#109归组。未加入外部身份事实。9条S2直接关系候选留待S6逐条审查，本批未新增正式关系边。

| 候选 / S3身份组 | KU | 跨章锚点 | 直接关系候选 |
|---|---|---|---:|
| `cand-0942, cand-7116` / `new-person:bernardo-de-dominici-cbdb693309` | `units/persons/bernardo-de-dominici` | 第6–8章；第21章书目；索引 D.csv#44 | 3 |
| `cand-2363` / `new-person:felicita-sartori-b7a1b9ce62` | `units/persons/felicita-sartori` | 第10、13章；索引 S.csv#51 | 3 |
| `cand-2773` / `new-person:teodoro-viero-15b8599b5c` | `units/persons/teodoro-viero` | 第13、15章；索引 UVWXYZ.csv#109 | 3 |



<a id="s4-archive-crosschapter-letters-20261017"></a>

### S4 archive：跨章书信端点登记（2026-10-17）

- `cand-9831`：S3组`archive-group-af4602857b00`登记为[档案卡](../../../04-knowledge/units/archives/zanetti-letter-to-gori-1738-08-23-marucelliana-b-viii-13.md)。依据限于print p. 328, note 2；印本文字为p. 289r；OCR为p. 289c。此差异只涉及Haskell书内页码转录，不表示已查阅手稿。 未新增正式关系；`st-chp10-p328-n02-letter-authored-by-zanetti`、`st-chp10-p328-n02-letter-addressed-to-gori`、`st-chp10-p328-n02-letter-held-by-marucelliana`保留待S6核对端点与证据。
- `cand-9832`：S3组`archive-group-8cfaf6d6bb80`登记为[档案卡](../../../04-knowledge/units/archives/biffi-letter-to-signor-vacchelli-1773-cremona-aa-i-4.md)。依据限于print p. 328, note 5；Haskell称此信未刊，并说明信息由Franco Venturi提供。OCR馆名Govcrnativa依印本文字校作Governativa；原信和馆藏目录未独立查阅。 未新增正式关系；`st-chp10-p328-n05-letter-authored-by-biffi`、`st-chp10-p328-n05-letter-addressed-to-vacchelli`、`st-chp10-p328-n05-letter-held-by-cremona-library`、`st-chp10-p328-n05-letter-has-subject-zuccarelli`保留待S6核对端点与证据。
- `cand-11571`：S3组`archive-group-dfcf90ed1ec3`登记为[档案卡](../../../04-knowledge/units/archives/rosa-letter-to-ricciardi-1660-04-02.md)。依据限于print p. 142, note 4; PDF physical p. 27；原书仅给出部分难辨的刊者姓氏形式de R...Jdis；引用目标cand-6205保持待决。书信和刊本未独立查阅。 未新增正式关系；`st-chp5-notes-l163-rosa-ricciardi-letter`、`st-chp5-l163-letter-authored-by`、`st-chp5-l163-letter-addressed-to`、`st-chp5-notes-l126-165-l163-letter-published-in-de-rinaldis`保留待S6核对端点与证据。

本批仅登记S3已裁决为`new`的三组档案身份；Haskell书内转引或著录是当前证据范围，没有据此声称查阅原信、馆藏目录或被引刊本。尚未映射的作者、收信人、馆藏机构及刊本端点按卡片中的候选ID保留，所有关系候选仍在`book-statements.jsonl`，本批没有写入`relations.csv`或建立正式关系。

S4累计登记486组/607条候选映射；待登记4,324组/4,379条；KU总数1,505。

<a id="s3-existing-rosa-ruffo-letter-1666-reuse-20261017"></a>

### S3 archive：Salvator Rosa 致 Don Antonio Ruffo 书信复用裁决（2026-10-17）

`cand-3551`（chp-1:01_CHP-1_sec_ii:l155-159#L944）由原先的单候选 `new` 身份组改判 `same`，映射到既有[units/archives/rosa-ruffo-letter-1666](../../../04-knowledge/units/archives/rosa-ruffo-letter-1666.md)。原书第1章 p.22 注1给出通信双方及1666-04-01日期；既有档案卡记录同一书内注释、同一日期、寄件人与收件人。S2句子转录的罗马数字`I`与印本所读阿拉伯数字`1`是转录差异，不构成第二封信。比较仅依据本书及现有卡片；未访问外部来源。

该候选的3条书内关系候选保留原ID，未在本轮重建或增写正式关系。此裁决不改变原刊本归属问题，也不把原信或刊本说成已独立查阅。

当前 S3：same=1,843 候选/1,031 KU；new=4,985 候选/4,809 组；conflict=8；excluded=100；undecided=5,471。S4 已登记486组，尚待登记4,323组/4,378条候选映射。

<a id="s4-cornelius-de-stael-person-20261017"></a>

### S4 person：Cornelius de Stael 跨章同组登记（2026-10-17）

`cand-2504`（S.csv#193；p.122）与`cand-6082`（第5章 p.122 注6）沿用S3组`new-person:cornelius-de-stael-012d225974`，合登记为[units/persons/cornelius-de-stael](../../../04-knowledge/units/persons/cornelius-de-stael.md)。两处均明确给出相同全名；正文称其为dealer，注6引用其1663年6月9日致Don Antonio Ruffo的信。人物卡限定于书内有据身份，不补传记。注6列出的V. Russo仍为候选`cand-11913`，身份待决；原信和被引刊本未独立查阅。3条直接S2关系候选保留待S6，本批未写入正式关系。

S4累计登记487组/609条候选映射；待登记4,322组/4,376条；KU总数1,506。

<a id="s4-de-stael-ruffo-letter-1663-06-09-20261017"></a>

### S4 archive：Cornelius de Stael 致 Don Antonio Ruffo 书信（1663-06-09）登记（2026-10-17）

`cand-6083`沿用S3组`archive-group-cd4ab1cc6b5f`，映射至[书信档案卡](../../../04-knowledge/units/archives/de-stael-letter-to-ruffo-1663-06-09.md)。Haskell第5章 p.122 注6给出书信双方、日期及V. Russo第170页的刊布线索；原信和被引刊本未独立查阅。作者cand-6082与收信人cand-2297已有KU映射；刊者候选cand-11913仍为undecided，且不与cand-3530合并。3条直接S2关系候选保留待S6，本批未新增正式关系。

S4累计登记488组/610条候选映射；待登记4,321组/4,375条；KU总数1,507。

<a id="s3-existing-negri-san-tommaso-letter-1676-reuse-20261017"></a>

### S3 archive：Paolo Negri 致 Marchese di S. Tommaso 书信复用裁决（2026-10-17）

`cand-3553`（chp-1:01_CHP-1_sec_ii:l168-239#L899）由单候选`new`组改判`same`，映射到既有[units/archives/negri-san-tommaso-letter-1676](../../../04-knowledge/units/archives/negri-san-tommaso-letter-1676.md)。原书第1章 p.21 注3明确给出同一寄件人、收件人、1676年12月24日日期及Claretta 1885 p.542刊引信息；既有卡片正以同一注释和同一日期标识该信。内部来源与卡片比对足以确认同一书信；不新增外部身份或原件主张。

3条S2关系候选保留原ID，未新增正式关系。

当前 S3：same=1,844候选/1,031 KU；new=4,984候选/4,808组；conflict=8；excluded=100；undecided=5,471。S4已登记488组，尚待登记4,320组/4,374条候选映射。

### S3 archive：Ruffo 通信组既有书信复用裁决（2026-10-17）

<a id="s3-existing-novetti-ruffo-letter-1670-reuse-20261017"></a>
- `cand-3550`（chp-1:01_CHP-1_sec_ii:l168-239#L753）由`new`改判`same`，映射到既有[units/archives/novetti-ruffo-letter-1670](../../../04-knowledge/units/archives/novetti-ruffo-letter-1670.md)；the same Chapter 1 note identifies the letter from Francesco Novetti to Don Antonio Ruffo dated 22 March 1670 and cites V. Russo, p. 290; the existing archive card records these same correspondents, exact date, and citation。书内书信关系候选原ID保留待S6，未新增正式关系。
<a id="s3-existing-de-rosis-ruffo-letter-1663-09-22-reuse-20261017"></a>
- `cand-3552`（chp-1:01_CHP-1_sec_ii:l168-239#L971）由`new`改判`same`，映射到既有[units/archives/de-rosis-ruffo-letter-1663](../../../04-knowledge/units/archives/de-rosis-ruffo-letter-1663.md)；the same Chapter 1 note identifies the letter from Giuseppe de Rosis to Don Antonio Ruffo dated 22 September 1663 and cites V. Ruffo, p. 172; the existing September archive card records that exact date and citation, while the distinct 2 June 1663 letter remains a separate KU。书内书信关系候选原ID保留待S6，未新增正式关系。

当前 S3：same=1,846候选/1,031 KU；new=4,982候选/4,806组；conflict=8；excluded=100；undecided=5,471。S4已登记488组，尚待登记4,318组/4,372条候选映射。

<a id="s3-existing-bianconi-letter-1762-reuse-20261017"></a>

### S3 archive：G. L. Bianconi 1762年书信复用裁决（2026-10-17）

`cand-3554`（chp-1:01_CHP-1_sec_ii:l168-239#L896）由`new`改判`same`，映射到既有[units/archives/bianconi-letter-1762](../../../04-knowledge/units/archives/bianconi-letter-1762.md)。Haskell第1章 p.21 注2给出Bianconi、1762年11月22日及Bottari卷VII第362页；既有卡记录同一作者、日期和刊本定位。OCR将`of 22`连写为`of22`；日期本身清楚。只确认文献身份，不把Haskell摘引扩成独立内容核验。1条直接书目关系候选保留待S6。

当前 S3：same=1,847候选/1,031 KU；new=4,981候选/4,805组；conflict=8；excluded=100；undecided=5,471。S4已登记488组，尚待登记4,317组/4,371条候选映射。

<a id="s3-existing-coke-arundell-letter-1620-reuse-20261017"></a>

### S3 archive：Mr Coke 1620年书信复用裁决（2026-10-17）

`cand-3421`（chp-1:01_CHP-1_intro:l11-13#L48）由`new`改判`same`，映射到既有[units/archives/coke-arundell-letter-1620](../../../04-knowledge/units/archives/coke-arundell-letter-1620.md)。Haskell第1章注2著录Mr Coke于1620年10月8日致出的书信并引Hervey p.183；相邻正文将通信者置于Lord Arundell语境，既有卡以同一书内脚注、日期和刊引登记同一书信。此为来源内身份比较，不推定第二封信或原始题名。1条书内归属关系候选保留待S6。

当前 S3：same=1,848候选/1,031 KU；new=4,980候选/4,804组；conflict=8；excluded=100；undecided=5,471。S4已登记488组，尚待登记4,316组/4,370条候选映射。

<a id="s4-archive-letter-title-localization-20261017"></a>

### S4 archive：三张书信卡中文描述性题名规范化（2026-10-17）

- 扎内蒂—戈里、比菲—瓦凯利、罗萨—里恰尔迪三张卡的中文展示题名改为中文描述性表达，英文名字段保持原有书内形式。
- 只调整展示题名与`ku-manifest.csv`中的对应`canonical_name`；S3身份组、KU路径、候选映射、证据范围及关系候选均未改变。


<a id="s4-rosa-ricciardi-letters-batch-20261017"></a>

### S4 archive：Rosa–Ricciardi 分日期书信身份登记（2026-10-17）

- `cand-11572`沿用S3组`archive-group-d50591c140c4`，登记为[Letter from Salvator Rosa to G. B. Ricciardi, 9 October 1666](../../../04-knowledge/units/archives/rosa-letter-to-ricciardi-1666-10-09.md)。依据限于print p. 143, note 1；原信及所引刊本未在本批独立查阅。关系候选`st-chp5-seciv-note-l40-p143-marker1`, `st-chp5-l40-letter-authored-by`, `st-chp5-l40-letter-addressed-to`保留待S6。
- `cand-11573`沿用S3组`archive-group-9dfe4a51adaf`，登记为[Letter from Salvator Rosa to G. B. Ricciardi, 24 April 1651](../../../04-knowledge/units/archives/rosa-letter-to-ricciardi-1651-04-24.md)。依据限于print p. 144, note 4；原信及所引刊本未在本批独立查阅。关系候选`st-chp5-seciv-note-l48-p144-marker4`, `st-chp5-l48-letter-authored-by`, `st-chp5-l48-letter-addressed-to`保留待S6。
- `cand-11574`沿用S3组`archive-group-4315528bb872`，登记为[Letter from Salvator Rosa to G. B. Ricciardi, 12 May 1651](../../../04-knowledge/units/archives/rosa-letter-to-ricciardi-1651-05-12.md)。依据限于print p. 144, note 5；原信及所引刊本未在本批独立查阅。关系候选`st-chp5-seciv-note-l49-p144-marker5`, `st-chp5-l49-letter-authored-by`, `st-chp5-l49-letter-addressed-to`保留待S6。
- `cand-11575`沿用S3组`archive-group-45db0f263e84`，登记为[Letter from Salvator Rosa to G. B. Ricciardi, 13 May 1662](../../../04-knowledge/units/archives/rosa-letter-to-ricciardi-1662-05-13.md)。依据限于print p. 144, note 6；原信及所引刊本未在本批独立查阅。关系候选`st-chp5-seciv-note-l50-p144-marker6`, `st-chp5-l50-letter-authored-by`, `st-chp5-l50-letter-addressed-to`保留待S6。
- `cand-11576`沿用S3组`archive-group-08e32659351b`，登记为[Letter from Salvator Rosa to G. B. Ricciardi, 21 May 1664](../../../04-knowledge/units/archives/rosa-letter-to-ricciardi-1664-05-21.md)。依据限于print p. 145, note 1；原信及所引刊本未在本批独立查阅。关系候选`st-chp5-seciv-note-l51-p145-marker1`, `st-chp5-l51-letter-authored-by`, `st-chp5-l51-letter-addressed-to`保留待S6。
- `cand-11954`沿用S3组`archive-group-1ae78d2d6f6e`，登记为[Letter from Salvator Rosa to G. B. Ricciardi, 27 May 1651](../../../04-knowledge/units/archives/rosa-letter-to-ricciardi-1651-05-27.md)。依据限于print p. 143, note 2；原信及所引刊本未在本批独立查阅。关系候选`st-chp5-l41-letter-authored-by`, `st-chp5-l41-letter-addressed-to`保留待S6。

六个日期各作为独立书信身份组登记，没有合并成通信集。通信双方复用已映射人物KU；11572等候选中由正文语境补出的作者／收信人继续按相应S2语境限定。Haskell转引的Limentani、De Rinaldis、Bottari页码未在本批复核；OCR与印本日期差异见各卡。没有写入正式关系。

S4累计登记494组/616条候选映射；待登记4,310组/4,364条；KU总数1,513。

<a id="s4-place-ferrara-20261017"></a>

### S4 place：Ferrara 跨章城市身份组登记（2026-10-17）

`cand-1017`（`sg3-place-ferrara`）登记为[费拉拉地点卡](../../../04-knowledge/units/places/ferrara.md)。S3以第2章及第8章的直接城市指称归为一个地点身份组；本卡仅记录地名和城市地点范围。7条直接关系候选仍待S6逐条裁决，没有写入正式关系。

S4累计登记495组/617条候选映射；待登记4,309组/4,363条；KU总数1,514。

<a id="s4-person-louis-richeome-20261017"></a>

### S4 person：Louis Richeôme 书内人物身份登记（2026-10-17）

`cand-2192`（`new-person:louis-richeome-355a5b7c18`）登记为[Louis Richeôme人物卡](../../../04-knowledge/units/persons/louis-richeome.md)。S3依据第3章全名、French Jesuit身份和跨段复指，将索引Q-R.csv#119与正文候选归为同一书内人物组；中文名标作工作音译。5条直接关系候选仍待S6；未据此补写生平、外部身份或正式关系。

S4累计登记496组/618条候选映射；待登记4,308组/4,362条；KU总数1,515。

<a id="s4-work-visitation-chapel-altarpiece-20261017"></a>

### S4 work：Chapel of the Visitation 祭坛画身份组登记（2026-10-17）

`cand-5039`（`workgrp-8e3da8b6b4eae3`）登记为[未具名访亲小堂祭坛画作品卡](../../../04-knowledge/units/works/visitation-chapel-altar-painting.md)。原书明确委托、预定小堂、转向 Barocci 及相对时间，但未给作品原题或题材；卡片据此采用描述性工作题名，不把小堂名称当作画作题材。7条直接关系候选均留待S6，没有写入正式关系。

S4累计登记497组/619条候选映射；待登记4,307组/4,361条；KU总数1,516。

<a id="s4-visitation-direct-place-term-endpoints-20261017"></a>

### S4 place/term：Chiesa Nuova 委托祭坛画的直接端点（2026-10-17）

- `cand-5038`（`sg3-place-cand-5038`）登记为[Chapel of the Visitation at Chiesa Nuova](../../../04-knowledge/units/places/chiesa-nuova-chapel-of-the-visitation.md)。依据限于第3章 L49; print p. 69；2条相应关系候选仍留待S6。
- `cand-12314`（`sg3-term-cand-12314`）登记为[Devotional Function of Fresco Subject Matter in Richeôme’s Account](../../../04-knowledge/units/terms/richeome-fresco-subject-devotional-function.md)。依据限于第3章 L35; print p. 68；1条相应关系候选仍留待S6。
- `cand-12316`（`sg3-term-cand-12316`）登记为[Ornamental Forms Described by Richeôme as Not Touching Devotion](../../../04-knowledge/units/terms/richeome-ornamental-forms-and-devotion.md)。依据限于第3章 L34-L35; print p. 68；1条相应关系候选仍留待S6。

`cand-5038`在两条关系候选的限定中作为预定安置小堂保留；`cand-12314`与`cand-12316`是Richeôme论述中的source-local term。三组分别映射，不合并地点、作品和术语；所有相关关系候选仍待S6，没有写入正式关系。

S4累计登记500组/622条候选映射；待登记4,304组/4,358条；KU总数1,519。

<a id="s4-person-prospero-pesci-20261017"></a>

### S4 person：Prospero Pesci 跨候选人物组登记（2026-10-17）

`cand-1887, cand-10374`（`new-person:pesci-prospero-a4b78e3c88`）共同登记为[Prospero Pesci人物卡](../../../04-knowledge/units/persons/prospero-pesci.md)。索引主项与第14章正文、脚注的全名相合；两条候选映射至同一人物KU。卡片只保留Haskell所述艺术家与Algarotti草图语境，中文名为工作音译。4条直接关系候选仍待S6，未新增正式关系或外部身份记录。

S4累计登记501组/624条候选映射；待登记4,303组/4,356条；KU总数1,520。

<a id="s4-person-maria-labia-20261017"></a>

### S4 person：Maria Labia 人物身份登记（2026-10-17）

`cand-1350`（`new-person:labia-maria-60556f1ddc`）登记为[Maria Labia人物卡](../../../04-knowledge/units/persons/maria-labia.md)。S3依据索引L.csv#7及第9章第257页正文全名，将其与Labia家族卡区分为个人人物KU；书内称谓和作者对Cleopatra对应及Tiepolo创作意图的推断均保留来源限定。4条直接关系候选仍待S6；珠宝集合端点尚未完成类型裁决，未新增正式关系或外部身份记录。

S4累计登记502组/625条候选映射；待登记4,302组/4,355条；KU总数1,521。

<a id="s3-person-girolamo-rainaldi-treccani-20261017"></a>

### S3/S4 person：Girolamo Rainaldi 身份核对与登记（2026-10-17）

`cand-2093`（`new-person:girolamo-rainaldi-cfd3000d9f`；索引Q-R.csv#20）登记为[Girolamo Rainaldi人物卡](../../../04-knowledge/units/persons/girolamo-rainaldi.md)。原书第6章第147页将Girolamo Rainaldi列为Innocent X时期接替Bernini的建筑师之一，并把Piazza Navona上的家族大宅规划归于他；第148页的年龄与能力评价仍属Haskell判断。外部身份对照：Cristiano Marchegiani, ‘Rainaldi, Girolamo (Geronimo),’ Treccani, *Dizionario Biografico degli Italiani*, vol. 86 (2016), https://www.treccani.it/enciclopedia/girolamo-rainaldi_%28Dizionario-Biografico%29/（访问日期2026-10-17）。该条确认为建筑师，并将Piazza Navona的Palazzo Pamphilj归于Girolamo，名称、职业和具体建筑与书内锚点相合；条目还记Carlo Rainaldi为Girolamo之子。因此第7章候选`cand-2092`（Carlo）保留独立`new-person:carlo-rainaldi-7ecc91cf92`身份组，不并入本组；该外部来源未验证Carlo候选所涉Louvre设计。Treccani身份记录已写入`alignment.csv`；4条直接书内关系候选仍待S6，不新增正式关系。

S4累计登记503组/626条候选映射；待登记4,301组/4,354条；KU总数1,522。

<a id="s4-archive-tiepolo-algarotti-letter-1743-10-26"></a>

### S4 archive：Tiepolo–Algarotti 1743年10月26日书信跨章身份组登记（2026-10-17）

`cand-8379, cand-10280`（`archive-group-tiepolo-algarotti-letter-1743-10-26`）共同登记为[该书信档案卡](../../../04-knowledge/units/archives/tiepolo-letter-to-algarotti-1743-10-26.md)。第9章第256页注5与第14章第352页正文、注3均指向Giambattista Tiepolo致Francesco Algarotti、1743年10月26日、Fogolari 1942年刊本第34页；发送人、收信人、日期及刊引一致，两个章节候选归入同一个archive KU。沿用S2对第9章扫描页18的校勘：OCR注号8、年份1.942分别校正为印刷注5、1942；原信和Fogolari刊本未在本批独立查阅。3条直接S2关系候选继续待S6，未新增正式关系。

S4累计登记504组/628条候选映射；待登记4,300组/4,352条；KU总数1,523。

<a id="s4-work-gesu-st-ignatius-great-altar-20261017"></a>

### S4 work：Gesù圣依纳爵小堂大祭坛方案登记（2026-10-17）

`cand-5420`（`workgrp-6e3beccdc5b5e1`）登记为[大祭坛方案知识卡](../../../04-knowledge/units/works/gesu-st-ignatius-great-altar-project.md)。S3按Haskell第3章第92–93页确定其为Gesù圣依纳爵小堂的特定祭坛项目，与Pietro da Cortona的较早祭坛方案及S. Ignazio教堂内另一祭坛保持边界。正文记录资金与赞助权、竞赛、1695年决定及Pozzo负责等书内说法；卡片不补出完工日期、现存状态或馆藏定位。7条直接S2关系候选仍待S6，未新增正式关系。

S4累计登记505组/629条候选映射；待登记4,299组/4,351条；KU总数1,524。

<a id="s4-work-gaulli-gesu-apse-adoration-of-the-lamb-20261017"></a>

### S4 work：Gaulli的Gesù后殿《羔羊崇拜》壁画登记（2026-10-17）

`cand-5287`（`workgrp-02e05bf99bb333`）登记为[后殿壁画知识卡](../../../04-knowledge/units/works/gaulli-gesu-apse-adoration-of-the-lamb-fresco.md)。Haskell第3章第84页描述Gesù后殿中Gaulli与《羔羊崇拜》题材的联系，并明确以数百年前S. Prassede和S. Maria Maggiore的马赛克作为旧有题材对照。此作品与manifest中Gaulli的Gesù穹顶／拱顶项目及《耶稣圣名的胜利》分别登记；候选题名为描述性暂题。7条直接S2关系候选仍待S6，包括作者联系、题材关系、作者推断与评价；未新增正式关系。

S4累计登记506组/630条候选映射；待登记4,298组/4,350条；KU总数1,525。

<a id="s3-s4-person-cesare-beccaria-treccani-20261017"></a>

### S3/S4 person：Cesare Beccaria 跨章身份核对与登记（2026-10-17）

`cand-0265, cand-0266`（`new-person:beccaria-cesare-904a6681ff`）共同登记为[Cesare Beccaria人物卡](../../../04-knowledge/units/persons/cesare-beccaria.md)。S1索引B.csv#112、B.csv#113均为全名`Beccaria, Cesare`，后者附《Dei delitti e delle pene》子目；S2分别锚定第10章第318、328页、第13章第337页和第15章第369页。第13章与第15章的表述涉及该作品，不将Pasquali或另一段落中的代词行动归给Beccaria。外部对照：Franco Venturi, ‘BECCARIA, Cesare,’ Treccani, *Dizionario Biografico degli Italiani*, vol. 7 (1970), https://www.treccani.it/enciclopedia/cesare-beccaria_%28Dizionario-Biografico%29/（访问日期2026-10-17）。该条讨论同一人物及其《Dei delitti e delle pene》，与全名和第10章1764年作品锚点相合；只确认身份，不验证Haskell的‘epoch-making’、巴黎欢迎、Biffi友谊或未具名威尼斯反对者等陈述。书本身候选`cand-9707`（archive组`archive-group-47e19ac2f4b5`）保持独立，未并入人物卡；未具名对手`cand-9711`保持undecided。3条直接关系候选仍待S6；Treccani身份记录分别附于两个候选映射，未新增正式关系。

S4累计登记507组/632条候选映射；待登记4,297组/4,348条；KU总数1,526。

### S4 archive：Beccaria《Dei delitti e delle pene》文本身份登记（2026-10-17）

- `cand-9707`（archive-group-47e19ac2f4b5）登记为[《论犯罪与刑罚》](../../../04-knowledge/units/archives/dei-delitti-e-delle-pene-treatise.md)；文献身份为文本层级论著，不指定版本或实物副本。依据第10章p.318的书名与出版陈述、第13章p.337关于Pasquali散发副本的叙述，以及第15章p.369明确标作传闻的Querini作者说。p.369 OCR `dette` 按既有S2对印刷页校为 `delle`。
- Beccaria、Pasquali与Querini相关的3条直接关系候选留待S6；未将出版叙述、散发事件或作者传闻转成正式边。书名候选与Beccaria人物候选分别落在archive和person KU。未新增外部版次或馆藏断言。

S4当前已登记508组/633条候选映射，尚待登记4,296组/4,347条。


<a id="s3-s4-person-christian-cole-20261017"></a>

### S4 person：Christian Cole关系端点登记（2026-10-17）

- `cand-0801`（`new-person:christian-cole-b8a8cee01c`）映射到[Christian Cole人物卡](../../../04-knowledge/units/persons/christian-cole.md)。全书索引C.csv#331列`Cole, Christian`；第10章p.276正文给出全名`Christian Cole`，注1中的`certo signor Colle inglese`只作为Haskell转述的早期传记归属，不视为独立核验。
- 直接S2关系候选4条，分别涉及Carriera、Lord Dartmouth及Pellegrini；Dartmouth端点`cand-0904`仍为S3 undecided。引述的早期传记未独立查阅，Manchester/Pellegrini关系保留原文“almost certainly”。本次只登记人物身份，不新增正式关系。

S4累计登记509组/634条候选映射；待登记4,295组/4,346条。

<a id="s3-s4-place-villa-cordellina-montecchio-20261017"></a>

### S3 evidence locator correction / S4 place：Villa Cordellina at Montecchio（2026-10-17）

S3原过程段落及候选说明中的“p.160”误把来源Markdown行号L160写作印刷页。现据`st-chp9-p256-cordellina-built-montecchio-house`、第9章页标与PDF物理页记录更正为印刷p.256（PDF物理页18）；候选detail及两条alignment rationale已原位更正，S3身份决定仍为同一跨章new组，不改变候选去向。
- `cand-8376`（第9章p.256，源行L160）与`cand-10279`（第14章p.352）统一登记至[Villa Cordellina at Montecchio地点卡](../../../04-knowledge/units/places/villa-cordellina-montecchio.md)。Haskell分别称Montecchio乡间住宅和Villa Cordellina；第9章另述的Vicenza住宅仍由独立候选组保留。
- 2条直接关系候选（Cordellina建宅、Tiepolo装饰）留待S6；未新增正式关系、现代地理断言或独立建筑作品对象。

S4累计登记510组/636条候选映射；待登记4,294组/4,344条。

<a id="s3-s4-person-domenico-passignani-20261017"></a>

### S4 person：Domenico Passignani直接关系端点登记（2026-10-17）

- `cand-1857`（`new-person:domenico-passignani-0029da3d84`）登记至[Domenico Passignani人物卡](../../../04-knowledge/units/persons/domenico-passignani.md)。索引P.csv#57列全名和pp.26、30、94；第2章p.26正文明确写作`Domenico Passignani`，支持该书内人物身份。未补外部生平。
- 4条直接S2关系候选待S6：Maffeo转而选用Passignani、穹顶装饰方案、被动句中的壁画委托、lunette场景绘制。提案不等于执行；Haskell的“most fashionable”“masterpieces”不升级为核实事实。cupola地点`cand-4258`待S4，cupola fresco和lunette work候选`cand-4259`、`cand-4260`仍S3 undecided；未指名委托方保持未决。

S4累计登记511组/637条候选映射；待登记4,293组/4,343条。

<a id="s3-s4-place-barberini-chapel-cupola-20261017"></a>

### S4 place：Barberini Chapel穹顶直接关系端点登记（2026-10-17）

- `cand-4258`（`sg3-place-cand-4258`）登记为[Cupola of the Barberini Chapel at S. Andrea della Valle地点卡](../../../04-knowledge/units/places/barberini-chapel-cupola-s-andrea-della-valle.md)。第2章p.25将Maffeo自用礼拜堂置于S. Andrea della Valle，p.26记录Passignani提出穹顶方案；第3章p.77将该穹顶作为Pietro da Cortona在Chiesa Nuova穹顶装饰的比较对象，不把两处合并。该KU只表示礼拜堂内部建筑空间。
- `st-chp2-seci-l55-69-cupola-proposal`与`st-chp3-seciv-l8-14-cupola-style-comparison`两条关系候选留待S6；穹顶壁画`cand-4259`与lunette作品`cand-4260`仍为S3 undecided。未推断方案实施情况、未登记正式关系。

S4累计登记512组/638条候选映射；待登记4,292组/4,342条。

<a id="s3-s4-person-giambettino-cignaroli-20261017"></a>

### S4 person：Giambettino Cignaroli跨索引身份组登记（2026-10-17）

- `cand-0754`（C.csv#278，索引页262、268、271）与`cand-0755`（C.csv#279，子目`work for Labia`，p.262n）同列全名`Cignaroli, Giambettino`，按S3组`new-person:cignaroli-giambettino-1b6e1c2f7d`登记至[Giambettino Cignaroli人物卡](../../../04-knowledge/units/persons/giambettino-cignaroli.md)。子目保留人物语境，不新建作品对象。
- 3条以该人物候选为端点的直接S2关系候选留待S6；p.262注5与p.268的限定及未核验状态保留。p.271还提及Cignaroli属于Oratorian所雇艺术家名单，但现有statement `st-chp9-p271-oratorian-fava-commissions`将关系端点记作机构与altarpiece作品候选`cand-8711`；本次不把该集合式陈述拆成个人关系。

S4累计登记513组/640条候选映射；待登记4,291组/4,340条。

<a id="s3-work-devonshire-monument-adjudication-20261017"></a>

### S3 work：McSwiny 德文郡公爵纪念画与改绘版本区分（2026-10-17）

`cand-9016` 的正文锚点为第10章 p.289 L230，注1表的同项行位于转录文件 L6；两处相合，将其裁决为 McSwiny 方案中的一幅单件、无正式题名作品，归入唯一新组 `workgrp-812459889b2b31`。现有 manifest 无对应 work KU，因此决定为 `new`。第10章 p.290 注2将 Bingley 改绘的 Devonshire 画推断为另一版本；其具体对象与版本身份未被识别，`cand-9020` 保持 `undecided`，不并入本组。未作外部身份核验；原书对 Ricci 参与的陈述仍按 S2 关系候选留待 S6。

<a id="s4-work-devonshire-monument-registration-20261017"></a>

### S4 work：McSwiny 德文郡公爵纪念画登记（2026-10-17）

`cand-9016`（`workgrp-812459889b2b31`）登记为单个 work KU：[作品卡](../../../04-knowledge/units/works/mcswiny-duke-of-devonshire-monument.md)。卡片保存第10章 p.289 正文、注1表及 p.290 注2的来源范围，标明无正式题名、描述性工作题名和版本边界。7条直接S2关系候选仍待S6：`st-chp10-p289-devonshire-monument-subject`, `st-chp10-p289-marco-ricci-collaborated`, `st-chp10-p289-note1-row02-artist1`, `st-chp10-p289-note1-row02-artist2`, `st-chp10-p289-note1-row02-subject`, `st-chp10-p289-sebastiano-ricci-collaborated`, `st-chp10-p290-note2-devonshire-alternate-version`。没有新增正式关系或外部身份断言。

S4累计登记514组/641条候选映射；待登记4,290组/4,339条；KU总数1,533。

<a id="s3-s4-brugnoli-albani-domenichino-article-20261017"></a>

### S3/S4 archive：Brugnoli 第二篇论文跨章身份组登记（2026-10-17）

`cand-4329`（第2章 p.29 注5）与`cand-11270`（第21章 p.417 书目）构成同一 archive 身份组 `archive-group-brugnoli-albani-domenichino-bassano-1957`。第2章注释提及 Brugnoli 等人的1957年论文；第21章书目提供第二篇文章的完整题名，S2 页图布局记录将 *Bollettino d’Arte*、1957年及 pp.255–277 归为同一条目中两篇文章的共同刊载信息。卡片只登记书目身份，不表示原文或文章内容已经查阅。

该书目项还列有题名不同的 Brugnoli 论文 *Il soggiorno a Roma di Bernardo Castello e le sue pitture nel Palazzo di Bassano di Sutri*，其候选 `cand-4328` 保持另一 S3 身份组。作者人物候选 `cand-4327` 因仅有缩写仍为 `undecided`。

S4将两条组成员映射至[Brugnoli论文卡](../../../04-knowledge/units/archives/brugnoli-albani-domenichino-frescoes-bassano-sutri-1957.md)。`st-chp2-seci-l95-106-citation-brugnoli-frescoes` 仍待S6；没有新增正式关系或外部事实断言。

S4累计登记515组/643条候选映射；待登记4,289组/4,337条；KU总数1,534。

<a id="s3-dresden-gallery-scope-adjudication-20261017"></a>

### S3 institution：Dresden Gallery 与 royal collection 候选范围拆分（2026-10-17）

复核既有跨章组后，`cand-9091` 保持 `new` 组 `sg3-institution-dresden-gallery`：第10章印刷页294（Markdown L298–299）明确称 Guarienti 领导下的 Dresden Gallery；第14章印刷页350（L39）称 Algarotti 为 Augustus of Saxony 正在形成的画廊制定扩充与完成计划，两个锚点指向同一绘画馆机构。此组不等同于 Augustus III 的个人绘画收藏或某座实体建筑。

`cand-10222` 从原 `sg3-institution-dresden-gallery` 组改列 `undecided`。其第14章候选除 p.347 L7 的 “royal gallery at Dresden” 外，还把 p.355 “royal collection” 词组和另一处 “gallery” 一并映射为同一候选。S3 按候选粒度对齐，现不能只将画廊提及映射至机构KU；暂不合并、不新建收藏KU，待 mention/candidate scope 分离后再裁决。对齐行保留原分组及变更理由。

<a id="s4-dresden-gallery-registration-20261017"></a>

### S4 institution：Dresden Gallery 登记（2026-10-17）

`cand-9091` 登记为一个 institution KU：[Dresden Gallery](../../../04-knowledge/units/institutions/dresden-gallery.md)。卡片只采用第10章 p.294 和第14章 p.350 的机构锚点，保留 Guarienti 与 Algarotti 的关系候选及方案未必实施的限定。`cand-10222` 不映射该卡。3条直接S2关系候选留待S6：`st-chp10-p294-guarienti-dresden-gallery`, `st-chp14-p350-dresden-gallery-plan`, `st-chp14-p350-gallery-represent-history-and-schools`。没有新增正式关系或外部身份断言。

S4累计登记516组/644条候选映射；待登记4,288组/4,335条；KU总数1,535。

<a id="s3-crespi-finding-moses-same-title-split-20261017"></a>

### S3 work：Crespi 两件同名《The Finding of Moses》作品分组更正（2026-10-17）

本节更正此前把 cand-0879 与 cand-7720 合并为同一幅 Crespi 画的决定。原组仅据同名题名及跨段指针判断身份，忽略了原书明确区分的委托与题材；旧判断与完整语境不符，保留在下方历史记录，不再作为当前裁决。

- cand-0879：改为 same，映射至既有 units/works/g-m-crespi-jupiter-handed-over-by-cybele-to-the-corybantes-to-be-fed。第8章 p.228 与第20章后记 p.405 均把 Conti 的委托识别为 Jupiter/Cybele 题材；Haskell明确说明《The Finding of Moses》是为降低关税而使用的发货题名。图版67的题名及既有 KU 的题材、Stuttgart inv.3294 与 Conti 委托信息相合。
- cand-7720：保持 new，单独归入 workgrp-ruffo-crespi-finding-of-moses-p222，待 S4 登记。第8章 p.222 将《The Finding of Moses》列为 Crespi 在 Ruffo 任使期间受委托的宗教题材作品之一；该画与 p.228 的 Conti Jupiter/Cybele 画是不同作品。p.222 OCR作 Russo’s，S2页图核对已校正为 Ruffo’s。未推断该画的具体年份、媒材或现藏地。

两件作品共享同一英文题名，但 p.222 的委托语境与 p.228/p.405 的 Jupiter/Cybele 题材及避税改题记录形成明确区分；本次不是 unresolved conflict。cand-7720 的一条书内委托关系候选仍待 S6；本次不新增正式关系。

#### 更正前 alignment 与候选说明（保留历史）

- cand-0879 原 alignment：source_ref=chp-8:08_CHP-8_sec_ii:l206-214#L210; p.228 title and ch.20 p.405 postscript; group=workgrp-beb5c6c0eb0cbc; S3 cross-chapter review 2026-10-17: same painting as cand-7720. Haskell first records the Jupiter/Corybantes title and later explains that the same commission was sent as The Finding of Moses to reduce customs duty. Preserve both titles and the source's qualification; do not create two work identities. Prior rationale retained in process record.
- cand-7720 原 alignment：source_ref=chp-8:08_CHP-8_sec_ii:l126-138#L135; p.222 title; group=workgrp-beb5c6c0eb0cbc; S3 cross-chapter review 2026-10-17: same painting as cand-0879. Haskell's p.405 postscript says the Jupiter/Corybantes commission was sent under the title The Finding of Moses to reduce customs duty. Preserve both titles and the source's qualification; do not create two work identities. Prior rationale retained in process record.
- cand-0879 原 candidate detail：S3 cross-chapter review 2026-10-17: same Crespi painting as candidate cand-7720. Haskell says the picture was first described as Jupiter among the Corybantes and was sent under the title The Finding of Moses to reduce customs duty; the two titles are not separate works.
- cand-7720 原 candidate detail：S3 cross-chapter review 2026-10-17: same Crespi painting as index candidate cand-0879. Haskell's p.405 postscript explains that the Jupiter/Corybantes commission was sent under the title The Finding of Moses; both names refer to one object.

<a id="s4-ruffo-crespi-finding-of-moses-registration-20261017"></a>

### S4 work：Ruffo 任使期间受委托的 Crespi《The Finding of Moses》登记（2026-10-17）

`cand-7720` 在 S3 更正后作为独立新作品组 `workgrp-ruffo-crespi-finding-of-moses-p222`，登记为 [作品卡](../../../04-knowledge/units/works/giuseppe-maria-crespi-finding-of-moses-ruffo-commission.md)。第8章 p.222 将其列为 Crespi 的作品之一及 Ruffo 任使期间委托的宗教题材画；OCR 的 Russo 依 S2 页图核对校正为 Ruffo。第8章 p.228 与第20章 p.405 所述 Conti Jupiter/Cybele 画虽然用了同一《The Finding of Moses》发货题名，但身份不同，映射至既有工作 KU 的候选 `cand-0879` 已改为 `same`。

卡片不补写 `cand-7720` 的具体创作年份、媒材、现藏地或外部身份。`st-chp8-p222-ruffo-commissioned-finding-of-moses` 仍为 S2 关系候选，待 S6；本批未写入正式关系。

S4累计登记517组/645条候选映射；待登记4,287组/4,333条；KU总数1,536。

<a id="s3-s4-german-patronage-of-italian-art-20261017"></a>

### S3→S4 term：German patronage 跨章身份组裁决与登记（2026-10-17）

`cand-1145`（G.csv#52，子目“in 17th century”）与`cand-1146`（G.csv#53，子目“of Venetian artists in 18th century”）保留为同一 `new` term 组 `sg3-term-germanpatronage`。第7章 pp.194–195 将17世纪后期的德国诸侯赞助与意大利多个绘画中心、受雇画家和北运作品相连；第10章 p.278 描述德国宫廷从意大利购画及延请画家，pp.294–296 则聚焦 Augustus III、其他德国君主及教会诸侯赞助威尼斯艺术。两项索引指向同一宽泛书内主题，但各自的时代与地域重心分开记录，不推断连续统一的制度或网络。现有一般术语 Art patronage 与罗马赞助主题的 term KU 范围不同，均不复用；未发现与本组同粒度的既有 KU。

S4将两条候选共同映射至[德国对意大利艺术的赞助术语卡](../../../04-knowledge/units/terms/german-patronage-of-italian-art.md)。卡片逐项限定第7章和第10章的历史语境、索引用法及作者的时期判断，没有外部术语核验。`cand-1145` 的4条直接 S2 关系候选仍待 S6：`st-chp7-p194-bologna-affected-by-patronage`、`st-chp7-p194-rome-affected-by-patronage`、`st-chp7-p194-venice-affected-by-patronage`、`st-chp7-p195-price-of-german-orders`；本次没有新增正式关系。

S4累计登记518组/647条候选映射；待登记4,286组/4,331条；KU总数1,537。

<a id="s3-s4-place-farsetti-country-house-s-maria-di-sala-20261017"></a>

### S3→S4 place：Farsetti 在 S. Maria di Sala 的乡间别墅身份组裁决与登记（2026-10-17）

`cand-1007`（F.csv#22，索引子目“country house at S. Maria di Sala”）与`cand-10432`（第15章 p.362 正文）维持同一 `new` 身份组 `sg3-place-farsetti-country-house-s-maria-di-sala`。正文将其称为 country house/villa，定位于法尔塞蒂家族在 S. Maria di Sala 的庄园；索引子目与正文对象的地点、所有者语境及建筑称谓相合。第362页另述法尔塞蒂在 Rialto 附近的家族宫邸，以及因争议未建成的帕多瓦罗马式别墅计划；两者不并入本组。登记名称为描述性工作题名，原书未给该建筑正式专名。

S4将两条候选映射至[法尔塞蒂 S. Maria di Sala 乡间别墅地点卡](../../../04-knowledge/units/places/filippo-farsetti-country-house-s-maria-di-sala.md)。卡片将第363页“battered shell”严格限定为哈斯克尔写作时的记述；未据此推定目前建筑状态，也未补外部地理或建筑身份。9条直接 S2 关系候选继续待 S6，其中收藏端点`cand-1005`、`cand-1006`仍为 untyped/undecided；本批没有新增正式关系。

S4累计登记519组/649条候选映射；待登记4,285组/4,329条；KU总数1,538。

<a id="s3-s4-term-bambocciate-small-pictures-20261017"></a>

### S3→S4 term：bambocciate 小幅日常生活画作身份裁决与登记（2026-10-17）

`cand-6099`保持 `new`，作为独立术语组 `sg3-term-cand-6099` 登记。第5章 p.132 直接将 bambocciate 释作描绘日常生活场景的小幅画作；第5章 pp.134、141、143 及第6章 p.158 将其用于画面表现、评价、收藏和 Helmbrecker 作品。既有 `units/terms/bamboccianti` 记录画家群体／艺术现象，其卡片明确把 bambocciate 保留为不同的画作类别；相关词形不构成同一性。未发现相同范围的既有 term KU。

S4登记为[日常生活题材小幅画作术语卡](../../../04-knowledge/units/terms/bambocciate-small-pictures-everyday-life.md)。卡片记录 Haskell 的描述及不同章节用法，不将其推广为涵盖所有日常生活题材的固定流派。8条直接 S2 关系候选继续待 S6；没有外部术语核验或新增正式关系。

S4累计登记520组/650条候选映射；待登记4,284组/4,328条；KU总数1,539。

<a id="s3-s4-term-cerquozzi-patrons-spanish-sphere-20261017"></a>

### S3→S4 term：塞尔奎齐赞助人的西班牙势力圈语境裁决与登记（2026-10-17）

`cand-6148` 保持 `new` 并登记为 `sg3-term-cand-6148`。第5章 p.137 称塞尔奎齐几乎所有较重要赞助人位于西班牙势力范围，随后以 Rapaccioli、Raggi、Carandini 等为例，并称“多数”相关家庭与 Barberini 圈在品味上有显著差异。此候选是作者段落中的概念性集体类别，不是 institution、单一家族或完整人物清单；原文没有组织身份，也未列出穷尽成员。S3 保留 `nearly all`、`most` 限定，不推断西班牙政治控制、统一网络或固定成员。个体 person 和具体 family KU 为不同对象粒度；未发现同范围既有 term KU。

S4登记至[术语卡](../../../04-knowledge/units/terms/cerquozzi-patrons-spanish-sphere-context.md)。卡片记述作者的审美比较及其对“直接赞助压力”因果解释的保留；11条直接 S2 关系候选继续待 S6，不新增正式关系或外部政治身份断言。

S4累计登记521组/651条候选映射；待登记4,283组/4,327条；KU总数1,540。

<a id="s3-s4-person-giuliano-finelli-20261017"></a>

### S3→S4 person：Giuliano Finelli 跨章身份组裁决与登记（2026-10-17）

`cand-1038`（F.csv#53，索引页171、172、190）维持 `new` 人物组 `new-person:finelli-giuliano-bbae0005b0`。第7章 p.171 给出全名 Giuliano Finelli 与 sculptor 身份；同一段跨至 p.172，代词和后续 Finelli 全名均处于副王在大教堂雇用雕塑家的叙述；第7章 p.190 再次列出 Giuliano Finelli，并称其参与为王室收藏制作摹本及原创作品。索引全名、正文姓名与跨页指代相合，person manifest 未发现同名既有 KU。OCR 的“Neapohtan”依 S2 页图校读为“Neapolitan”；这里只记家世用语，不推断出生地。未使用外部身份来源。

S4登记至[Giuliano Finelli 人物卡](../../../04-knowledge/units/persons/giuliano-finelli.md)，卡片仅记录书内职业、赞助语境及王室收藏工作。4条直接 S2 关系候选仍待 S6；没有新增正式关系或外部生平断言。

S4累计登记522组/652条候选映射；待登记4,282组/4,326条；KU总数1,541。

<a id="s3-s4-person-francesco-cozza-20261017"></a>

### S3→S4 person：Francesco Cozza 单人身份组核对与登记（2026-10-17）

`cand-0867`（C.csv#400，索引页131）保留 `new`，登记为 `new-person:cozza-francesco-f2b1f96cec`／`units/persons/francesco-cozza`。索引全名“Cozza, Francesco”与第5章 p.131 正文全名“Francesco Cozza”相合；人物 manifest 中没有同名 KU。外部身份比对使用 Ludovica Trezzani，*Dizionario Biografico degli Italiani*，vol. 30（1984），Treccani 条目[“COZZA, Francesco”](https://www.treccani.it/enciclopedia/francesco-cozza_(Dizionario-Biografico)/)（访问：2026-10-17）：条目以全名收录一位卡拉布里亚画家，并记其师从 Domenichino，与 Haskell p.131 的姓名、同乡和师承语境相合。此来源仅作身份佐证，不将生平或作品事实导入卡片；不裁决原文的推荐、师承或交往关系。

S4 新建[Francesco Cozza 人物卡](../../../04-knowledge/units/persons/francesco-cozza.md)，并把候选 `aln-1202` 映射到 `units/persons/francesco-cozza`；外部身份比对作为独立 alignment 行保存。4条直接 S2 关系候选 `st-chp5-p131-cozza-altarpiece`、`st-chp5-p131-cozza-probably-recommended`、`st-chp5-p131-shared-pupilage`、`st-chp5-p131-almost-certain-association` 均未正式化，待 S6。相关端点状态分别为：未具名祭司群体 `cand-6068` 仍 `undecided`／未分类；祭坛画 `cand-6069` 仍 `undecided`／作品身份未识别；Sassoferrato `cand-2369` 仍 `undecided`；Domenichino `cand-0932` 已复用既有 KU。不得将 Treccani 身份佐证作为上述关系成立的证据。

S4 当前登记 523 组／653 条候选映射；待登记 4281 组／4325 条映射；KU 总数 1542。

<a id="s3-sassoferrato-person-crosschapter-20261017"></a>

### S3 person：Sassoferrato 索引主项与 style 子项复用既有人物（2026-10-17）

`cand-2369`（S.csv#57，主项“ Sassoferrato (Giovan Battista Salvi) ”，pp.130–131）由 undecided 改为 same → units/persons/sassoferrato。S2 正文 p.130–131 有12条映射到该候选的人名、画家称谓与指代；本次仅决定人物身份，不据此接受全部传记或关系陈述。

`cand-2372`（S.csv#60，子项 style，p.131）也由 undecided 改为 same → units/persons/sassoferrato。子项重复同一完整人物主项，只定位其风格讨论；它不是另一人物，也不在没有独立概念锚点时新建风格术语 KU。原 alignment 理由认为缺少全名，现补入索引主项全名及既有别名证据，旧理由作为 prior_resolution_note 保留。

权威身份比对：Treccani DBI，Silvia Blasio，vol. 90（2017），条目标题“ SALVI, Giovanni Battista, detto il Sassoferrato ”（[条目链接](https://www.treccani.it/enciclopedia/salvi-giovanni-battista-detto-il-sassoferrato_(Dizionario-Biografico)/)，访问：2026-10-17）。标题将 Giovanni Battista Salvi 与 Sassoferrato 直接并列，匹配本书索引的 “Giovan Battista Salvi” 及既有人物卡的全名／惯用名。这里只记录身份比对，不导入生平或作品字段；原书人物关系命题仍须按 S6 逐条审查。

两候选并入既有 `sg3-ku-units-persons-sassoferrato` 身份组，与已登记的图版候选 cand-3880 共用同一 KU。cand-2373、cand-2374 是作品候选，未随人物身份合并；Cozza 组中的4条 S2 关系候选仍待 S6，本次未新增正式关系。

S3 现行决定计数：same=1,851（1,031个既有KU）；undecided=5,470。S4 登记数不变。

<a id="s3-s4-person-mario-chigi-20261017"></a>

### S3→S4 person：Don Mario Chigi 直接关系端点身份组登记（2026-10-17）

cand-0674（C.csv#198，p.154）保留 new 并登记为 new-person:chigi-mario-1e3f6f6032／units/persons/mario-chigi。索引全名及括注将 Don Mario Chigi 标为 Pope Alexander VII 之弟；正文 p.154 有 Don Mario Chigi 全名及其后回指。人物 manifest 未见同名 KU。

外部身份比对使用 Treccani DBI 第88卷 Salvator Rosa 条目（[PDF](https://static.treccani.it/export/sites/default/catalogo/catalogo_prodotti/grandi_opere/biografia_nazionale/pdf/DBI88_Rosa_Salvatore.pdf)，访问：2026-10-17）。该条目记载 Rosa 1659 年展出的《Fortune》被读作对 Chigi 教廷裙带关系的讽刺，并称 Mario Chigi（教皇之弟）为画家辩护、使其免受指控。姓名、教皇亲缘和同一画作争议与 Haskell p.154 的 Don Mario 对应。此来源只支持人物身份，不替代 S6 关系裁决，也不把 Rosa 是否实际面临监禁或法律指控写成事实。

S4 新建[马里奥·基吉人物卡](../../../04-knowledge/units/persons/mario-chigi.md)，候选 cand-0674 映射至 units/persons/mario-chigi；外部身份比对作为单独 alignment 行。4条直接 S2 关系候选（介入、兄弟、影射、父子）仍待 S6；作者的 double irony 解释保留为非关系陈述，未新增正式边。

S4 当前登记 524 组／654 条候选映射；待登记 4280 组／4324 条映射；KU 总数 1543。

<a id="s3-s4-person-felice-torelli-20261017"></a>

### S3→S4 person：Felice Torelli 跨章身份组登记（2026-10-17）

`cand-2645`（T.csv#108，pp.203、227、348）与 `cand-2646`（T.csv#109，p.389 子目）按相同全名及书内全名锚点保留在 `new-person:felice-torelli-f294b4c634`，映射至 `units/persons/felice-torelli`。第8章 p.203、p.227 和第19章附录 p.389 均直接写出 Felice Torelli；第14章 p.348 正文仅写姓氏，但该页列在同一索引主项下。人物清单中没有同名 KU；Giuseppe、Giacomo Torelli 另有独立索引项，未与本组合并。

卡片覆盖 Belloni 的未具名画作群、Torelli 提出的特洛伊历史画方案、Algarotti 评价语境及 Conti 委托文书标题。作品组 `cand-12006` 与提案作品 `cand-7798` 均保持 `undecided`；提案、接受“此类”画作和后来送达的画没有被合并为一件已确认作品。附录所称文书未独立查阅。4条直接 S2 关系候选仍待 S6；没有外部身份字段或正式关系边。

S4 当前登记 525 组／656 条候选映射；待登记 4279 组／4322 条映射；KU 总数 1544。

<a id="s4-felice-torelli-card-fields-repair-20261017"></a>

### S4 卡片结构化字段登记校正：Felice Torelli（2026-10-17）

首次严格审计发现人物卡的两张 Markdown 表有7条内容行，但 `enrichment.jsonl` 尚无对应行；`build_cards.py --check` 因渲染器无法从字段表重建这些卡内表而拒绝预检。现将姓名表与本章内容表按卡片来源序号 S1–S6 补入 `enrichment.jsonl`；中文显示名工作音译移出表格，不伪造来源支持。`build_field_facts.py` 预览：cards=1,544、rows=10,516、records_with_source=8,975、unverified=1,611、record_changes=0、new_ids=7、removed_ids=0、source_registry_changes=0、warnings=0；随后 apply 写回7行。复核后严格阶段审计 `errors=[]`、`s2_missing=[]`；`build_cards.py --check` 通过（1,544 cards、2,706 tables、10,516 rows），未写出渲染文件。审计保留原有两条 enrichment source_ref 警告和 S2 语义质量提示；本校正未改 relations.csv 或任何 S6 状态。

<a id="s3-s4-person-alexander-the-great-20261017"></a>

### S3→S4 person：Alexander the Great 跨章身份组登记（2026-10-17）

cand-3442（第1章 p.10、第8章 p.228、第10章 p.282）与 cand-9593（第10章 p.313）按相同完整人名保留在 new-person:alexander-great-68fcc5120d，共映射至[亚历山大大帝人物卡](../../../04-knowledge/units/persons/alexander-the-great.md)。两项均为人物候选；人物清单未见该全名或同义拼写对应的既有 KU。卡片仅登记书内具名身份，未补写外部生平。

来源摘录与句意分别记在卡片的四条 Haskell 来源项：第1章 p.10 为一般性王室委托例子；第8章 p.228 所述 Ricci 提案因报价过高而未实施；第10章 p.282 是 Haskell 对 Rapparini 比较 Johann Wilhelm 与 Alexander 的转述；第10章 p.313 列出 Pittoni 为 Schulenburg 创作的系列题材，未给单件作品题名。

三条直接 S2 关系候选 `st-chp10-p282-rapparini-alexander-comparison`、`st-chp10-p313-pittoni-history-series-for-schulenburg`、`st-chp8-p228-sebastiano-proposal-failed` 留待 S6；第1章概括性例子不转为人物关系。本次未新增正式关系。

S4 当前登记 526 组／658 条候选映射；待登记 4,278 组／4,320 条映射；KU 总数 1,545。

<a id="s3-s4-person-enriqueta-harris-20261017"></a>

### S3→S4 person：Enriqueta Harris 跨章身份组登记（2026-10-17）

cand-1292（H.csv#8，第7章 p.190 n.）与 cand-11166（第20章 p.401 n.1）按相同全名／书目交叉线索保留在 new-person:enriqueta-harris-df8f6c82dc，共映射至[恩里克塔·哈里斯人物卡](../../../04-knowledge/units/persons/enriqueta-harris.md)。第4章 p.116 注释与第7章 p.190 n.5 给出全名；第20章短引的 Harris 经第21章 p.412 的书目交叉指引及 p.425 联合署名与 Harris, Enriqueta 相合。人物清单未见同名 KU。归组只解决书内身份，不证明所引文章或致谢信息。

卡片记录索引 H.csv#8、第4章 p.116、第7章 p.190、第20章 p.401 及第21章 pp.412、425 的可定位依据。OCR 中 de Andres 的重音校正沿用 S2 页图记录；没有新增外部身份来源。

四条 S2 关系候选 `st-chp7-p190-n1-cite-harris-1960`、`st-chp7-p190-n1-cite-harris-1961`、`st-chp7-p190-n5-cite-harris-1957`、`st-chp7-p190-n5-haskell-acknowledges-harris` 留待 S6；第4章 p.116 的两个期刊定位和第20章 p.401 的短引仍按 citation-only 语境处理。本次未新增正式关系。

S4 当前登记 527 组／660 条候选映射；待登记 4,277 组／4,318 条映射；KU 总数 1,546。

<a id="s3-s4-archive-harris-citation-endpoints-20261017"></a>

### S3→S4 archive：Harris 引文与合著书目身份组登记（2026-10-17）

本次登记四个互不合并的 archive 身份组：

- cand-7118（archive-group-ead5029fb147）→ units/archives/harris-velazquez-mission-italy-1960：委拉斯开兹的意大利之行（Velazquez’s Mission in Italy）
- cand-7119（archive-group-bb76a9f7bb76）→ units/archives/harris-colonna-decoration-san-antonio-portugueses：安杰洛·米凯莱·科隆纳与葡萄牙人圣安东尼堂装饰（Angelo Michele Colonna and the Decoration of San Antonio of the Portuguese）
- cand-7127（archive-group-63afaa8ea5cf）→ units/archives/harris-marques-del-carpio-velazquez-1957：卡皮奥侯爵与委拉斯开兹绘画（The Marquis of Carpio and His Paintings by Velázquez）
- cand-11165（archive-group-7d2e75a7375b）→ units/archives/harris-andres-descripcion-escorial-1972：卡西亚诺·达尔·波佐的埃斯科里亚尔记述（1626）（Description of El Escorial by Cassiano dal Pozzo (1626)）

四项均依据哈斯克尔注释或书目中的可定位题名、责任者和出版信息登记；没有独立查阅文章，也没有导入文章内容。1961 年只由第7章 p.190 注1给出，书目 p.424 未列年份；1972 年书目的 de Andrés 署名按行内原样保存，人物候选 cand-11167 仍 undecided。三条 S2 书目引用关系候选留待 S6；1972 年 p.401 短引及 p.425 书目项不是 relation_candidate。本次未新增正式关系或外部身份记录。

四张卡的书目字段表已列出原题、责任者署名及来源限定；20条表格事实已通过 build_field_facts 登记，见下方字段登记记录。

S4 当前登记 531 组／664 条候选映射；待登记 4,273 组／4,314 条映射；KU 总数 1,550。

<a id="s4-harris-archive-card-fields-20261017"></a>

### S4 archive 卡片结构化字段登记：Harris 书目端点（2026-10-17）

四张新增 archive 卡各含5条有来源的书目字段行，按 `build_field_facts.py` 的默认预览核对后以 `--apply` 登记：cards=1,550、cards_with_tables=1,088、rows=10,536、unique_sources=1,716、records_with_source=8,995、unverified=1,611、duplicate_occurrences=0、record_changes=0、new_ids=20、removed_ids=0、source_registry_changes=0、warnings=0。书目关系候选状态未改变；`cand-11167` 仍 undecided。卡片字段与来源表同步，未生成渲染输出。

<a id="s3-s4-person-giovanni-ricci-20261017"></a>

### S3→S4 person：Giovanni Ricci 索引主项、子目与跨页正文并组登记（2026-10-17）

S3 复核将 `cand-2147`（Q-R.csv#74，索引定位 pp.204、238）由 `undecided` 改为 `new`，与 `cand-2148`（Q-R.csv#75，“patronage of Crespi”，p.204）共同保留在 `new-person:giovanni-ricci-3e157bdeda`。此前 `cand-2147` 的未决理由称其无正文提及；复核发现第8章 p.238 L327–336 已以全名 Giovanni Ricci 记述其为 Crespi 的 Bologna 赞助人，且 S2 的 `st-chp8-p238-note2-ricci-pepoli-correspondence`、`st-chp8-p238-ricci-acquired-work`、`st-chp8-p238-ricci-financed-travels` 已将其作为直接端点。现向 mentions.csv 补入 `m-chp8-p238-giovanni-ricci`（L329，segment chars 754–768），不改写这三条既有 statement 的命题。p.204 与 p.238 两处全名、对 Crespi 的重叠赞助语境，以及同一索引主项/子目结构支持两候选同一身份；旧 undecided 理由保留于候选对齐行及本过程记录。

该组登记为[乔瓦尼·里奇人物卡](../../../04-knowledge/units/persons/giovanni-ricci.md)。卡片限于哈斯克尔书内身份和角色，不补外部生平。7条直接 S2 关系候选留待 S6，评价性 `st-chp8-p204-ricci-leading-patron` 继续保持非关系陈述；本次未修改 `relations.csv`。

S4 当前登记532组/666条候选映射；待登记4,272组/4,313条；KU 总数1,551。

<a id="s3-s4-person-pietro-francavilla-20261017"></a>

### S3→S4 person：Pietro Francavilla 跨页人物组登记（2026-10-17）

`cand-1064`（F.csv#79，索引 pp.174、178）保留 S3 source-local 人物组 `new-person:francavilla-pietro-c1cca1c0e8`，登记为[彼得罗·弗朗卡维拉人物卡](../../../04-knowledge/units/persons/pietro-francavilla.md)。第7章 p.174 给出 Pietro Francavilla 全名、Flemish-Florentine sculptor 称谓及召赴巴黎语境；同页称其与 Francesco Bordoni 同行，并由 Pietro Tacca 与 Francavilla 完成 Giambologna 创作的亨利四世骑马像。p.178 将 Francavilla 与 Giambologna、Pietro Tacca 并列于雕塑传统叙述。索引页码与正文语境支持跨页同一人物；未用外部来源补充身份或生平。

4条直接 S2 关系候选 `st-chp7-p174-i08`、`st-chp7-p174-i09`、`st-chp7-p174-i10`、`st-chp7-p174-i17` 留待 S6；本次没有新增正式关系，未写入 `relations.csv`。

S4 当前登记533组/667条候选映射；待登记4,271组/4,312条；KU 总数1,552。

<a id="s3-s4-followup-verification-20261017"></a>

### S3→S4 后续批次核验（2026-10-17）

Ricci 与 Francavilla 登记后运行 `audit_tables.py --strict-stage --summary`：KU=1,552、候选决定=12,407、alignment=12,642、待登记 `decision=new` 行=4,327、mentions=26,619、`s2_missing=[]`、`errors=[]`。本轮 Ricci 新增提及的第一次审计发现偏移使用了段内行偏移；现已按完整 segment `chp-8:08_CHP-8_sec_ii:l327-336` 的 Unicode 字符偏移修正为754–768，复核通过。审计仍报告4,327条待登记 `decision=new` 行、两条既有 enrichment source_ref 警告（`enr-06678`、`enr-06937`）及 S2 语义质量提示。

`build_cards.py --check` 全库预检通过：1,552 cards、2,710 tables、10,536 rows、预计148个渲染文件；只预检，未渲染写入。Ricci、Francavilla 单卡 preview 均未发现需写回差异。`build_field_facts.py` 默认预览：cards=1,552、cards_with_tables=1,088、rows=10,536、unique_sources=1,716、records_with_source=8,995、unverified=1,611、duplicate_occurrences=0、record_changes=0、new_ids=0、removed_ids=0、source_registry_changes=0、warnings=0。针对本轮文件的 `git diff --check` 退出码为0；Git 提示部分 UTF-8 文档下次写入时 LF 将转为 CRLF，无空白错误。

<a id="s4-pietro-foscarini-verification-20261017"></a>

### S4 补充人物组登记后核验：Pietro Foscarini（2026-10-17）

Foscarini 登记后再次运行严格阶段审计：KU=1,553、候选决定=12,407、alignment=12,642、待登记 `decision=new` 行=4,326、mentions=26,619、`s2_missing=[]`、`errors=[]`。当前 S4 已登记534组／668条候选映射，待登记4,270组／4,311条。既有两条 enrichment source_ref 警告及 S2 语义质量提示未变化。

`build_cards.py --check` 通过（1,553 cards、2,710 tables、10,536 rows、预计148个文件；没有写卡）；Pietro Foscarini 单卡 preview 无待写回差异。`build_field_facts.py` 默认预览为0项新增或删除、0 warnings；`git diff --check` 退出码0，只有 LF→CRLF 提示。

<a id="s4-nicola-del-rosso-verification-20261017"></a>

### S4 补充两候选人物组登记后核验：Nicola del Rosso（2026-10-17）

Nicola del Rosso 登记后，严格阶段审计为 KU=1,554、候选决定=12,407、alignment=12,642、待登记 `decision=new` 行=4,324、mentions=26,619、`s2_missing=[]`、`errors=[]`。S4 已登记535组／670条候选映射，待登记4,269组／4,309条；两条既有 enrichment source_ref 警告及 S2 语义质量提示保持不变。

`build_cards.py --check` 通过（1,554 cards、2,710 tables、10,536 rows、预计148个文件；未渲染）；Nicola del Rosso 单卡 preview 无待写回差异。`build_field_facts.py` 默认预览显示0新增／删除／来源变更、0 warnings；针对本批文件的 `git diff --check` 退出码0，仅有 LF→CRLF 提示。

<a id="s4-nicolas-fouquet-verification-20261017"></a>

### S4 补充人物组登记后核验：Nicolas Fouquet（2026-10-17）

Fouquet 登记后严格阶段审计为 KU=1,555、候选决定=12,407、alignment=12,642、待登记 `decision=new` 行=4,323、mentions=26,619、`s2_missing=[]`、`errors=[]`。S4 已登记536组／671条候选映射，待登记4,268组／4,308条；原有两条字段来源引用警告和 S2 语义质量提示仍在。

`build_cards.py --check` 通过（1,555 cards、2,710 tables、10,536 rows、预计148个文件；未渲染）；Nicolas Fouquet 单卡 preview 无待写回差异。`build_field_facts.py` 默认预览为0新增／删除、0 warnings；本批 `git diff --check` 退出码0，仅有 LF→CRLF 提示。

<a id="s3-s4-person-pietro-foscarini-20261017"></a>

### S3→S4 person：Pietro Foscarini 跨页人物组登记（2026-10-17）

`cand-1056`（F.csv#71，索引 p.259 与 p.273 n.2）保留 S3 source-local 人物组 `new-person:foscarini-pietro-0946cf5155`，登记为[皮埃特罗·福斯卡里尼人物卡](../../../04-knowledge/units/persons/pietro-foscarini.md)。第9章 p.259 全名指向其作为 Procuratore di San Marco 及一组留在宅邸画作的前任所有者，Haskell 对1745年去世的记述带问号；p.259 注4与 p.273 注2将遗嘱定位到同一 Biblioteca Correr 手稿，p.273 注2再次全名并记载1745年祭坛留款。索引定位、全名与遗嘱语境支持同一书内人物。原始遗嘱和清单未独立查阅；本卡不把1745年遗嘱日期写成确切死亡日期，也不与既有 Marco Foscarini 合并。

4条直接 S2 关系候选 `st-chp9-p259-pietro-foscarini-procuratore`、`st-chp9-p259-pietro-left-picture-group-with-palace`、`st-chp9-p259-pietro-left-other-venetian-classics`、`st-chp9-p273-n02-foscarini-will-marble-altar-bequest` 留待 S6；本次未新增正式关系或写入 `relations.csv`。

S4 当前登记534组/668条候选映射；待登记4,270组/4,311条；KU 总数1,553。

<a id="s3-s4-person-nicola-del-rosso-20261017"></a>

### S3→S4 person：Nicola del Rosso 两候选跨页并组登记（2026-10-17）

`cand-2285`（Q-R.csv#213，主项定位 p.211、p.212 n.5）与 `cand-7611`（p.212 n.5 全名正文候选）共同保留在 `new-person:del-nicola-rosso-e3ae15d1b4`，登记为[Nicola del Rosso 人物卡](../../../04-knowledge/units/persons/nicola-del-rosso.md)。p.211 称第四个兄弟 Nicola 的两名儿子 Antonio 与 Giovanni Battista 为继承人，并称 Nicola 于1710年去世；p.212 n.5 再以全名指认“第四个兄弟”，并称其岳父为 Francesco Panciatichi。索引主项、全名和亲属限定支持同一人物。去世年份是非关系陈述；未补外部生平。

3条直接 S2 关系候选 `st-chp8-p211-nicola-father-of-antonio`、`st-chp8-p211-nicola-father-of-giovanni-battista`、`st-chp8-p212-n5-panciatichi-nicola-kinship` 留待 S6；本次未新增正式关系或写入 `relations.csv`。

S4 当前登记535组/670条候选映射；待登记4,269组/4,309条；KU 总数1,554。

<a id="s3-s4-person-nicolas-fouquet-20261017"></a>

### S3→S4 person：Nicolas Fouquet 人物组登记（2026-10-17）

`cand-1062`（F.csv#77，索引定位 p.186）保留 S3 source-local 人物组 `new-person:fouquet-nicolas-426b26efec`，登记为[尼古拉·富凯人物卡](../../../04-knowledge/units/persons/nicolas-fouquet.md)。第7章 p.186–187 连续段落以 Fouquet 姓氏描述财政大臣、被捕、由 Colbert 接替、曾受雇于 Mazarin 及与 Colbert 同为意大利艺术收藏者；全名由索引对应。卡片限于哈斯克尔书内叙述，未使用外部身份来源或补充收藏事实。

4条直接 S2 关系候选 `st-chp7-p186-i17`、`st-chp7-p186-i18`、`st-chp7-p186-i19`、`st-chp7-p187-i01` 留待 S6；本次未新增正式关系或写入 `relations.csv`。

S4 当前登记536组/671条候选映射；待登记4,268组/4,308条；KU 总数1,555。

<a id="s3-s4-person-camillo-astalli-20261017"></a>

### S3→S4 person：Camillo Astalli 人物组登记（2026-10-17）

`cand-0144`（A.csv#145，索引定位 p.148）按 S3 组 `new-person:astalli-camillo-acfa71028e` 登记为[卡米洛·阿斯塔利人物卡](../../../04-knowledge/units/persons/camillo-astalli.md)。第6章 p.148 明确具名 Camillo Astalli，称纳沃纳广场教皇宫曾分配给他，称他为 Donna Olimpia 的一位亲属但未说明具体亲缘，并记述他称自己 Pamfili。依照 S3，Astalli 不与真正的 Prince Camillo Pamfili 合并；不补外部生平，也不据书中关系陈述预先建立正式边。仓库原有同路径草稿未列入 accepted.yml 或 ku-manifest.csv，本次原位升级并登记，不创建重复卡。

3条直接 S2 关系候选 `st-chp6-p148-astalli-assigned-papal-palace`、`st-chp6-p148-astalli-relation-to-olimpia`、`st-chp6-p148-astalli-substitute-nephew` 留待 S6；“自称 Pamfili” statement 为非关系陈述。本次未写入 `relations.csv`。

S4 当前登记537组/672条候选映射；待登记4,267组/4,307条；KU 总数1,556。

#### 本组登记后核验

`audit_tables.py --strict-stage --summary`：KU=1,556、候选决定=12,407、alignment=12,642、待登记 `decision=new` 行=4,322（含4,307条候选映射及15条外部身份记录）、mentions=26,619、`s2_missing=[]`、`errors=[]`。审计继续提示两条既有 enrichment source_ref 引用未能从对应卡片 source 列表解析（`enr-06678`、`enr-06937`），并保留 S2 语义质量提示；这些警告未由本次 S4 登记解决。卡片字段表写回两条姓名事实后，`build_field_facts.py` 预览为0条新增／删除、0 warnings；`build_cards.py --check` 通过（1,556 cards、2,711 tables、10,538 rows、2,436 projected relation rows、146 cards with relation changes、148 files in render scope），Camillo 单卡 preview 无差异，未渲染写卡。`git diff --check` 退出码0，仅有 LF→CRLF 提示；本组未修改 `relations.csv`（1,225 formal、2 pending）。

<a id="s3-s4-person-grey-brydges-fifth-lord-chandos-20261017"></a>

### S3→S4 person：Grey Brydges, 5th Lord Chandos 两候选并组登记（2026-10-17）

`cand-0644`（C.csv#168，Chandos 主项）与 `cand-0645`（C.csv#169，Discourse of Rome 子项）按 S3 组 `new-person:5th-brydges-chandos-grey-b35ab5db22` 共用[格雷·布里奇斯人物卡](../../../04-knowledge/units/persons/grey-brydges-fifth-lord-chandos.md)。书后索引两条均定位 p.63；第3章第一节以完整姓名引出 *Discourse of Rome* 中的旅人引文，第3章注2又将同一全名置于 *Horae Subsecivae* 前。两候选是同一人物的索引主项及子项，不是两个人物。正文和脚注的书目题名关系仍待证，方括号归属未独立核实；S4 不据此建立文献或作者正式关系。

直接 S2 关系候选 `st-chp3-seci-l3-14-charge-attributed-to-grey`、`st-chp3-seci-l3-14-grey-quoted-jesuit-description`、`st-chp3-intro-l7-9-horae-authored-by-chandos` 留待 S6；哈斯克尔对 Grey 的评价 statement 保持非关系分类。引文中的耶稣会教堂不在本卡身份裁决中消歧。本次未写入 `relations.csv`。

S4 当前登记538组/674条候选映射；待登记4,266组/4,305条；KU 总数1,557。

#### 本组登记后核验

`audit_tables.py --strict-stage --summary`：KU=1,557、候选决定=12,407、alignment=12,642、待登记 `decision=new` 行=4,320（含4,305条候选映射及15条外部身份记录）、mentions=26,619、`s2_missing=[]`、`errors=[]`。审计继续提示既有 `enr-06678`、`enr-06937` 两条 enrichment source_ref 不能从对应卡片 sources 解析，并保留 S2 语义质量提示；本批未修改相关字段。卡片姓名表写回两条字段事实后，`build_field_facts.py` 预览为0条新增／删除、0 warnings；`build_cards.py --check` 通过（1,557 cards、2,712 tables、10,540 rows、2,436 projected relation rows、146 cards with relation changes、148 files in render scope），Grey Brydges 单卡 preview 无差异，未写渲染卡片。三条直接关系候选及标题差异仍待证，`relations.csv` 未新增关系。

### S3 person：Emilio Altieri 索引子项复用既有人物（2026-10-17）

`cand-0088`（A.csv#89，子目 “financial difficulties”，定位 p.162）原因未映射 S2 正文提及而列为 `undecided`。复核第6章 p.162 原文开头明确写 “Clement X had good reason to try to economise”；同页提及 `m-chp6-p162-v-007`（“Clement X”，字符224–233）此前已随主项 `cand-0087` 登记。主项索引 A.csv#88 与子项 A.csv#89 具有同一全名 “Altieri, Emilio (Pope Clement X)”，而 p.162 子项内容与正文锚点一致，支持同一人物。

现将 `cand-0088` 改为 `same` → `units/persons/emilio-altieri-pope-clement-x`，与已登记人物 KU 对齐；保留旧待证理由及其解决依据。未改写 S2 mentions，不新增外部身份断言或关系。

### S3 person：Grey Brydges 人物索引子项映射至既有人物（2026-10-17）

`cand-0646`（C.csv#170，索引子目 *Horae Subsecivae*，p.63）原因缺少映射到该候选的正文提及而列为 `undecided`。第3章 p.63 原文以全名 “Grey Brydges, 5th Lord Chandos” 引出 *Discourse of Rome*；同页既有提及 `m-chp3-seci-l3-14-0011` 已映射至 `cand-0644`，其人物组已登记为 `units/persons/grey-brydges-fifth-lord-chandos`。C.csv#170 的子目仍在同一全名人物标题下，故裁决的是索引所指人物身份。

现将 `cand-0646` 改为 `same` → `units/persons/grey-brydges-fifth-lord-chandos`。原待证理由保留于对齐行和本记录。此项不证明 Grey 对 *Horae Subsecivae* 的作者身份，也不解决其脚注归属或题名关联；没有新增关系。

### S3 person：Augustus III 的 Rosalba 子项复用人物 KU（2026-10-17）

`cand-0150`（A.csv#151，子目 “and Rosalba Carriera”，p.295）因没有直接映射的 S2 提及而列为 `undecided`。第10章 p.294 明确说 Augustus the Strong 之子 “Augustus III”；其后 p.295 连续叙述该 Augustus 与 Rosalba Carriera 相识、并持续收购其粉彩作品。候选 `cand-0148` 已将 p.294 “his son” 的 S2 提及映射到同一全名人物组，并已登记为 `units/persons/augustus-iii-of-poland`。索引全名、相邻正文指代链与 p.295 子目共同支持复用该人物。

现将 `cand-0150` 改为 `same` → `units/persons/augustus-iii-of-poland`。旧待证理由保留；未新增 S2 提及，也未把该子目转为 Rosalba 的人物关系或作品事实。

### S3 person：Paolo Giordano II Orsini 十条索引子项复用既有人物（2026-10-17）

复核 `cand-0429`（p.97 “and Claude”）、`cand-0430`（p.97 “and van den Hecke”）、`cand-0431`（p.97 “and Pietro Tacca”）、`cand-0432`（p.97 “and Podestà”）、`cand-0433`（pp.96–97 “Bernini head, medal, and bust”）、`cand-0435`（pp.97–98 “correspondence with Queen Christina of Sweden”）、`cand-0436`（p.96 “Leoni etching”）、`cand-0437`（pp.95–97 “love of music and spectacle”）、`cand-0438`（p.97 “medal collecting”）和 `cand-0439`（p.96 “poetry”）。这些均为人物类型候选，索引使用完全相同的全名标题 `Bracciano, Paolo Giordona II Orsini, Duke of`；各页范围与第4章已具名人物正文重叠。`cand-0428` 的正文提及 `m-chp4-sec-i-0171` 将 Paolo Giordano II Orsini 锚定于该段，`m-chp4-sec-i-0181` 在同一上下文给出 Duke of Bracciano；`cand-0428` 与附录候选 `cand-0434` 已共同登记到 `units/persons/paolo-giordano-ii-orsini`。 索引 B.csv#277–288 将名字写作 “Giordona”；书内正文和附录作 “Giordano”。此处记录为索引拼写异文，结合全名、爵号、代际和对应页锚点后用于身份映射，不把它扩展成第二个人物。

十条候选现均由 `undecided` 改为 `same`，指向该既有人物 KU。各条旧待证理由保存在对齐行中，并记录本次解决依据。索引子目仅参与人物身份归属，不据此补写与 Claude、van den Hecke、Tacca、Podestà、Bernini、Queen Christina 或 Leoni 的关系，也不把 Etching、胸像、奖章或诗歌作为新作品事实；没有新增关系或 S2 提及。

### S3 person：Francesco Borromini 三条人物索引子项复用（2026-10-17）

`cand-0405`（pp.75–76 “and Oratorians”）、`cand-0408`（p.75 “work on the Oratorio”）和 `cand-0409`（p.75 “work on Spada palace”）均为 person 类型，候选全名与主项 Francesco Borromini 相同。第3章 p.75 正文写明 Oratorians 委托 Borromini 建造 Chiesa Nuova 旁的 Oratorio，并在同页继续以 Borromini 记述 Oratorio 与 Spada 宫的工作；对应提及 `m-chp3-secii-l125-135-0027` 已归入 `cand-0404`，该组已登记为 `units/persons/francesco-borromini`。

三条候选从 `undecided` 改为 `same` 并复用该 KU，原待证理由及本次证据保留。此身份映射不把索引子目升级为正式关系；本次未新增关系或作品 KU。

### S3 person：Filippo Farsetti 四条索引子项复用（2026-10-17）

`cand-1003`（p.363 “and Canova”）、`cand-1004`（p.362 “and Carlo Lodoli”）、`cand-1009`（p.363 “interest in contemporary arts”）和 `cand-1011`（p.363 “promotion of Venetian neo-classicism”）均为 person 类型、全名与 Farsetti 主项 `cand-1002` 一致。第15章 p.362 明确以 “Filippo Farsetti” 开篇介绍该人物；p.363 延续同一叙述并继续具名 “Farsetti”。相应正文提及 `m-chp15-p362-0001`、`m-chp15-p363-0033` 已归入主项候选；该人物组已登记为 `units/persons/filippo-farsetti`。

四条索引子项现由 `undecided` 改为 `same`，复用既有人物 KU。旧待证理由及解决依据逐行保留。索引子目中的 Canova、Lodoli 及艺术活动措辞只作身份定位，本次不建立人物关系或新增作品事实。

### S3 person：Niccolò Cassana 六条作品子目复用人物（2026-10-17）

`cand-0595`（p.234 *Bacchanal*）、`cand-0596`（p.234 *Conspiracy of Catiline*）、`cand-0597`（p.234 “paintings for Grand Prince Ferdinand”）、`cand-0598`（pp.234、240 *Portrait of a Cook*）、`cand-0599`（p.241 *Portrait of a Hunter*）和 `cand-0600`（p.234 *Venus playing with Cupid*）均为 person 类型、同属 Cassana 全名词头。第8章 p.234 的 `m-chp8-p234-cassana-name` 明确记录 Niccolo Cassana，随即叙述其为 Grand Prince Ferdinand 创作的历史画与肖像，并列举上述题材；p.241 又称 “his Cassana Portrait of a Hunter”。同名人物组 `cand-0593`、`cand-0594` 已登记为 `units/persons/niccolo-cassana`。

六条候选由 `undecided` 改为 `same`，复用该人物 KU。旧待证理由保留于对齐行。子目只定位到人物名下的作品／创作语境，不在 S3 确认单件作品身份、具体归属或人物关系；本次不新增作品卡、关系或 S2 提及。

### S3 person：Federico Barocci 的《Presentation》索引子项复用（2026-10-17）

`cand-0248`（B.csv#95，p.69，子目 *Presentation of Jesus in the Temple*）为 person 类型、正文提及未直接映射到该索引子项而列为 `undecided`。第3章 p.69 正文先以全名 “Federico Barocci” 引出委托，再以 “the same artist” 指回 Barocci 并叙述《Presentation of Jesus in the Temple》的委托；提及 `m-chp3-secii-l40-52-0032` 与 `m-chp3-secii-l40-52-0040` 已归入主项 `cand-0247`，其人物组已登记为 `units/persons/federico-barocci`。

现将 `cand-0248` 改为 `same` 并复用该人物 KU。原待证理由保留。此项不新建作品 KU，也不将索引子目直接升级为正式关系。

<a id="s3-s4-person-ottaviano-prati-20261017"></a>

### S3→S4 person：Ottaviano Prati 书内人物身份组登记（2026-10-17）

`cand-6090` 是单成员 S3 组 `new-person:ottaviano-prati-f3bfa7e4a0`。第5章 p.131 注3以 “Monsignor Ottaviano Prati” 具名；脚注转述一幅 Prati 的签名肖像，并称他曾在不同时期任 Benevento、Viterbo 总督，但未给任职年代或肖像作者。该书内锚点足以登记来源内人物身份，不提供外部生平或完整身份链。

现登记为[奥塔维亚诺·普拉蒂人物卡](../../../04-knowledge/units/persons/ottaviano-prati.md)，仅映射 `cand-6090` 一个候选。项目已有的 `Ottaviano Ottoviani` 是另一个全名与独立来源的对象；本组不因共享名字 Ottaviano 而合并。另一个候选 `cand-6091` 是签名肖像的独立 work 组，未在本次 S4 登记。

`st-chp5-note-p131-n3-prati-portrait`、`st-chp5-note-p131-n3-prati-governor-benevento` 与 `st-chp5-note-p131-n3-prati-governor-viterbo` 保持 S2 关系候选，留待 S6；不修改 `relations.csv`。本次没有新增外部身份记录或 S5 字段核验。

S4 当前登记539组/675条候选映射；待登记4,265组/4,304条；KU 总数1,558。

<a id="s3-person-prati-index-cross-reference-20261017"></a>

### S3 person：全书索引 Prati 主项与第5章脚注同一性裁决（2026-10-17）

`cand-2055` 原因是索引候选无 mapped S2 mention 而保持 undecided。复核原书索引转录 L2552 后，该行以倒置全名写作 “Prati, Monsignor Ottaviano”；第5章 p.131 注3以 “Monsignor Ottaviano Prati” 具名。全名与称谓逐项对应，且当前人物 KU 中无其他 Prati 对象，故将索引候选裁为与 `cand-6090` 同一人物，映射至 [奥塔维亚诺·普拉蒂人物卡](../../../04-knowledge/units/persons/ottaviano-prati.md)。本判断只处理身份，不扩写该人物履历或正式关系。

索引定位留有转录异文：`entity-candidates.csv` 记 `13n`，结构化 `P.csv#258` 记 `121n`，原索引 OCR 行尾为 `13 m G`。不据此推定印本页码；索引姓名本身与正文全名支持身份映射。该索引来源已作为 S2 加入人物卡。

更新后 S3：same=1,879，new=4,979（4,804组），conflict=8，excluded=100，undecided=5,441；S4 登记状态不变。

<a id="s4-prati-portrait-and-governorship-places-20261017"></a>

### S4 work/place：Prati 签名肖像及两处总督任职地点直接端点登记（2026-10-17）

按三组现有 S3 `new` 决定登记：`cand-6091`（`workgrp-18912bb6d0e607`）→ [奥塔维亚诺·普拉蒂肖像](../../../04-knowledge/units/works/portrait-monsignor-ottaviano-prati.md)；`cand-6093`（`sg3-place-cand-6093`）→ [贝内文托](../../../04-knowledge/units/places/benevento.md)；`cand-6094`（`sg3-place-cand-6094`）→ [维泰博](../../../04-knowledge/units/places/viterbo.md)。

第5章 p.131 注3提供签名肖像及两个任职地点的书内锚点。肖像卡采用项目描述性暂题，不推定作者、原题或年代；地点卡只保留书内地名及任职语境，不补任期或辖区。中文地名是项目工作音译。所有卡均有双语描述及原文来源定位。

`st-chp5-note-p131-n3-prati-portrait`、`st-chp5-note-p131-n3-portrait-located-galleria`、`st-chp5-note-p131-n3-prati-governor-benevento` 与 `st-chp5-note-p131-n3-prati-governor-viterbo` 仍是 S2 关系候选，留待 S6；本次不写入 `relations.csv`。未做外部身份核验或 S5 字段补足。

S4 当前登记542组/678条候选映射；待登记4,262组/4,301条；KU 总数1,561。

<a id="s4-saverio-bettinelli-cross-chapter-20261017"></a>

### S4 person：Saverio Bettinelli 跨章身份组登记（2026-10-17）

跨章身份组 `new-person:bettinelli-saverio-9ac59400eb` 含两条 S3 `new` 候选：`cand-0369` 是索引主项 `B.csv#216`（索引列 p.320、334），`cand-0370` 是同名主项下的子目 `B.csv#217`（`Dell'entusiasmo per le Belle Arti`，p.320）。第13章 p.334 正文以完整姓名 “Saverio Bettinelli” 点名发言者；书后索引以倒置姓名列主项。两候选据此登记到同一张[萨韦里奥·贝蒂内利人物卡](../../../04-knowledge/units/persons/saverio-bettinelli.md)。这只裁决人物身份，不将索引子目题名登记为作品，也未作外部身份核验。

`st-chp13-p333-anonymous-quotation-on-poem-collections` 与 `st-chp13-p334-bettinelli-criticized-opulent-poem-collection` 是人物对仪式纪念诗集的书内评论／评价关系候选，均留待 S6；未修改 `relations.csv`。卡片记录第13章 p.334 正文及全书索引的姓名证据，不扩写人物生平。未进行 S5 外部字段核验。

S4 当前登记543组/680条候选映射；待登记4,261组/4,299条；KU 总数1,562。

<a id="s4-giovanni-adamo-20261017"></a>

### S4 person：Giovanni Adamo 直接关系端点登记（2026-10-17）

`cand-0016` 是单成员 S3 人物组 `new-person:adamo-giovanni-15d8ae3b24`。第1章 p.10 正文以 “Giovanni Adamo” 具名，书后 A 项索引以倒置形式列名，均指向同一书内人物身份；现登记为[乔瓦尼·阿达莫人物卡](../../../04-knowledge/units/persons/giovanni-adamo.md)。未作外部身份核验。

`st-chp1-secii-l40-46-09` 记录 Adamo 委托 Paolo Girolamo Piola 创作一件未具名作品并将题材选择留给画家的书内断言，仍留待 S6；不写入 `relations.csv`，不为未具名作品另建 KU。没有据此扩展人物生平或作品清单。

S4 当前登记544组/681条候选映射；待登记4,260组/4,298条；KU 总数1,563。

<a id="s4-james-adam-source-local-group-20261017"></a>

### S4 person：James Adam 跨章书内人物组登记（2026-10-17）

`cand-0011` 是单成员 S3 人物组 `new-person:adam-james-24bd4e0e2f`，索引主项 `A.csv#10` 合并页302、310、392。p.302 与 p.310 均以全名 James Adam 指认讨论 Joseph Smith 的说话者；p.302 注1与 p.310 注5涉及 1760 年 8 月20日的同一封 James 致 Robert Adam 信件，附录5 p.392 再引该信。现以本书内姓名、索引和相同书信锚点登记为[詹姆斯·亚当人物卡](../../../04-knowledge/units/persons/james-adam-venice.md)。信件原件和 Fleming 刊本均未独立查读；本次不据此确认外部身份或亲属关系。

`st-chp10-p302-james-adam-criticism` 保留为 James Adam 对 Joseph Smith 的书内评价候选，待 S6 裁决；不修改 `relations.csv`。p.310 的财务评价仍明确归于哈斯克尔转引，不登记为已核实事实。

S4 当前登记545组/682条候选映射；待登记4,259组/4,297条；KU 总数1,564。

<a id="s4-john-vanbrugh-person-20261017"></a>

### S4 person：Sir John Vanbrugh 书内人物组登记（2026-10-17）

`cand-2690` 是单成员 S3 人物组 `new-person:john-vanbrugh-c177249729`，对应书后索引主项 `UVWXYZ.csv#26`（pp.278–279、309）。正文 p.278 将 Vanbrugh 称为 gentleman-architect；p.279 以 “The same architect” 延续指称；书后索引以倒置全名 “Vanbrugh, Sir John” 列项。无同名既有人物 KU，故将该书内身份登记为[约翰·范布勒爵士人物卡](../../../04-knowledge/units/persons/sir-john-vanbrugh.md)。本次不引入外部生平或身份来源。

`st-chp10-p278-vanbrugh-built-friends-country-houses`、`st-chp10-p279-vanbrugh-carlisle-castle-howard` 与 `st-chp10-p309-one-picture-after-vanbrugh` 保留为 S2 关系候选，留待 S6；未修改 `relations.csv`。p.279 后文出现的 Castle Howard 不用于本次解决尚待核的住宅／地点候选映射。

S4 当前登记546组/683条候选映射；待登记4,258组/4,296条；KU 总数1,565。

<a id="s4-archive-lavagnino-artisti-italiani-germania-iii-20261017"></a>

### S4 archive：E. Lavagnino《Gli artisti italiani in Germania》第III卷跨章组登记（2026-10-17）

`cand-7251`（第7章 p.193 n.3、p.194 n.1 引文候选）与 `cand-11371`（第21章 p.427 书目候选）属于既有 S3 跨章组 `archive-group-lavagnino-artists-germany-vol3-1943`，据书目中的作者、卷次、副题、出版地和年份对应为同一册。现以一张[《在德国的意大利艺术家》第三卷：画家与版画家](../../../04-knowledge/units/archives/lavagnino-artisti-italiani-germania-iii-1943.md) archive KU 接收两条候选映射。中文、英文题名均为项目工作译题；书目只署名 `E. Lavagnino`，未补作者全名或出版者。

`st-chp7-p193-n3-cite-lavagnino` 与 `st-chp7-p194-n1-lavagnino` 保留为 S2 书内引用关系候选，留待 S6；被引原书及 p.69、p.66 均未独立查读。p.282 n.3 的 p.85 与 p.283 n.2 的 p.120 未标卷次，按 S3 决定不归入本卷；p.294 n.2 的 p.115 也未核准其卷次归属。书目陈述 `st-chp21-bib-l658-699-entry-06` 仅支持出版记录，不登记为正式关系。本次未修改 `relations.csv`。

S4 当前登记547组/685条候选映射；待登记4,257组/4,294条；KU 总数1,566。

<a id="s4-place-cordellina-vicenza-house-20261017"></a>

### S4 place：Carlo Cordellina 的维琴察住宅跨章组登记（2026-10-17）

`cand-8375`（第9章 p.256，“one in his native Vicenza”）与 `cand-11069`（后记 p.405，1770年开始营建的 Vicenza palace）是既有 S3 组 `sg3-place-cordellina-vicenza-house` 的两条候选。S3 依据跨章地点和人物锚点裁为同一地点，并明确原书没有正式建筑题名。现以描述性暂题登记为[卡洛·科尔代利纳在维琴察的住宅](../../../04-knowledge/units/places/carlo-cordellina-vicenza-house.md)。Montecchio 的 Villa Cordellina 保持为另一地点 KU；本卡不扩写地址、现存状态或外部建筑身份。

`st-chp9-p256-cordellina-built-vicenza-house` 与 `st-chp20-p405-cordellina-vicenza-palace` 仍是书内关系候选，留待 S6。p.405 的生平信息为哈斯克尔转述 Puppi，Puppi 文献未独立查读；本次不修改 `relations.csv`。

S4 当前登记548组/687条候选映射；待登记4,256组/4,292条；KU 总数1,567。

<a id="s4-term-contracts-artistic-commissions-20261017"></a>

### S4 term：艺术委托合同跨章概念组登记（2026-10-17）

按既有 S3 组 sg3-term-contracts 登记四条 `new` 候选：`cand-0837`（C.csv#367，索引主项）、`cand-0839`（C.csv#369，price）、`cand-0840`（C.csv#370，subject）和 `cand-0841`（C.csv#371，time limit），统一映射至[艺术委托合同术语卡](../../../04-knowledge/units/terms/artistic-commission-contracts.md)。第1章 pp.8–9 说明实际合同是否订立取决于委托范围，题材条款可保留画家发挥空间；p.12 讨论工期；p.13 讨论价款及不同付款安排。描述保留个案差异，不将概述表述为统一规则。

同一索引文本组中的 `cand-0838`（C.csv#368，measurements of works，p.8）在 S3 为 `undecided`：现有记录只有索引定位，未有足以确定指涉的关联 S2 提及，因此继续不映射，不并入本卡。现有 procedure KU [委托合同订立惯例](../../../04-knowledge/units/procedures/commission-contracting.md)描述订约实践，类型和职责不同；本次没有将其改写或复制。

`st-chp1-secii-l73-77-01` 保留为一般性价款陈述，虽带 relation-candidate 标记但没有第二端点，不据此生成正式关系；`st-chp9-p255-contracts-and-consultation-limits` 是哈斯克尔的方法性说明，不登记为关系。其他候选关系仍按既有 S6 流程处理；本次未修改 `relations.csv`，未新增 S5 enrichment。

S4 当前登记549组/691条候选映射；待登记4,255组/4,288条；KU 总数1,568。

<a id="s4-work-zompini-le-arti-20261017"></a>

### S4 work：Zompini《Le Arti》跨章作品组登记（2026-10-17）

既有 S3 组 workgrp-4dad04ca7f0e40 包含索引候选 `cand-2876`（UVWXYZ.csv#213；页344、374）与第13章正文候选 `cand-10111`，两者均为 `new`，统一映射至[《威尼斯街头的各行各业》作品卡](../../../04-knowledge/units/works/le-arti-che-vanno-per-via-nella-citta-di-venezia.md)。第13章 p.344 称 Gaetano Zompini 于1753年为该作品作图稿，并对题材和内容作评价；第16章 p.374 记 John Strange 曾计划推出一个版本，但不证明出版计划落实。姓名端点已有去向：Zompini 为 `same/new` 决定所指向的 `units/persons/gaetano-zompini`，Strange 指向 `units/persons/john-strange`。

作品卡保留索引题名与第16章题名变体，中文及英文仅作描述性工作译名；没有推定媒介、版次、印数、收藏或存世情况。`st-chp13-p344-zompini-drew_for_le_arti_1753` 和 `st-chp16-p374-strange-zompini-publication-plan` 作为 S2 关系候选留待 S6；`st-chp13-p344-haskell-le_arti_assessment` 保留为 Haskell 的评价性陈述，不登记为关系。本次未修改 `relations.csv`，未新增 S5 enrichment。

S4 当前登记550组/693条候选映射；待登记4,254组/4,286条；KU 总数1,569。

<a id="s4-work-zanetti-varie-pitture-20261017"></a>

### S4 work：Zanetti《Varie Pitture a Fresco》跨章作品组登记（2026-10-17）

既有 S3 组 workgrp-25c14f82a2c959 的 `cand-2859`（UVWXYZ.csv#196，Zanetti 主项下的 Varie Pitture a Fresco 子目）与 `cand-10117`（第13章正文及第21章书目链接）均为 `new`，统一映射至[《威尼斯主要名家的各式壁画》作品卡](../../../04-knowledge/units/works/varie-pitture-a-fresco-principal-venetian-masters.md)。第13章 p.345 说“较年轻的 Zanetti”制作古典名家作品的摹本，并于1760年以 Varie Pitture a Fresco 之名出版；第21章书目列完整题名、A. M. Zanetti、Venezia 和1760年。被引出版物未独立查阅，卡片不补图像目录、媒介、技法、数量或具体版本内容。

作品类型依据图像摹本／视觉图册语境；仅因被书目列载，不另复制成 archive KU。相关文本出版物候选 `cand-2855` 与 `cand-2858` 类型不同，继续各按其自身 S3 决定处理。作者候选 `cand-2854` 仍为 `undecided`，不映射人物 KU；因此 `st-chp13-p345-varie-pitture-1760` 的创作者／出版者关系保持待 S3 身份解决后再交 S6。`st-chp13-p343-notes-note2-varie-pitture-preface-source` 是引用定位，`st-chp21-bib-l1261-1299-entry-14` 是书目记录，均不升级为关系。本次未修改 `relations.csv`，未新增 S5 enrichment。

S4 当前登记551组/695条候选映射；待登记4,253组/4,284条；KU 总数1,570。

<a id="s4-archive-luzio-gonzaga-gallery-1913-20261017"></a>

### S4 archive：Alessandro Luzio《La galleria dei Gonzaga》书目组登记（2026-10-17）

单成员 S3 组 archive-group-32cf29336a05（`cand-7052`）依据第21章书目、多个脚注引用和第7章 p.177 n.3 的卷册标题定位，登记为[贡扎加画廊书目卡](../../../04-knowledge/units/archives/luzio-gonzaga-gallery-1913.md)。哈斯克尔书目列 Alessandro Luzio、题名 La galleria dei Gonzaga venduta all’Inghilterra nel 1627-38、Milano、1913；第1章脚注引用 Luzio pp.48、292、295，第7章脚注引用 pp.63–167。被引原书及页面未独立查读，卡片只登记书目身份与哈斯克尔提供的引文定位。

五条 S2 引用候选 st-chp1-secii-p13-n3-cites-luzio-p48-gozadini, st-chp1-secii-p10-n4-cites-luzio-p292, st-chp1-secii-p14-n2-cites-luzio-p48-reni, st-chp1-secii-p14-n5-cites-luzio-p295-arragona-letter, st-chp7-p177-n3-cite-luzio 继续留待 S6 逐条审查；书目陈述 st-chp21-bib-l701-754-entry-12 仅支持出版记录。端点哈斯克尔对应既有 archive KU `units/archives/patrons-and-painters`。本次未把脚注内容升级为 Luzio 原书的事实，未修改 `relations.csv`，未新增 S5 enrichment。

S4 当前登记552组/696条候选映射；待登记4,252组/4,283条；KU 总数1,571。

<a id="s4-person-longhi-maccarani-facade-endpoints-20261017"></a>

### S4 person：特雷维广场立面作品的两个书内人物端点（2026-10-17）

按既有 S3 身份组分别登记：`cand-1428`（new-person:longhi-martino-younger-48ba69e866；索引 L.csv#85）映射至[马蒂诺·隆吉（小）人物卡](../../../04-knowledge/units/persons/martino-longhi-younger.md)；`cand-1463`（new-person:maccarani-paolo-bda33fc651；索引 M.csv#0）映射至[保罗·马卡拉尼人物卡](../../../04-knowledge/units/persons/paolo-maccarani.md)。第7章 p.183 分别称 Longhi the Younger 为建筑师，称 Maccarani 为罗马代理人。两卡仅记录来源内具名身份与角色，不补写外部生平。

两人物出现在 st-chp7-p183-i08 的书内叙述中；该关系候选仍按 S6 核对 Mazarin、人物角色、作品及地点端点。作品 cand-6797 与地点 cand-6806 仍各按其 S3 新组等待 S4，不在本次写入正式关系；`relations.csv` 与 enrichment 未变更。

S4 当前登记554组/698条候选映射；待登记4,250组/4,281条；KU 总数1,573。

<a id="s4-place-piazza-di-trevi-20261017"></a>

### S4 place：Piazza di Trevi 书内地点端点登记（2026-10-17）

单成员 S3 地点组 sg3-place-cand-6806（`cand-6806`）依据第7章 p.183 的明确地点指称登记为[特雷维广场地点卡](../../../04-knowledge/units/places/piazza-di-trevi.md)。卡片只保留书内可确认的广场名称及其在教堂立面叙述中的位置语境；未补坐标、边界、现址或外部对应。其与立面 work 候选 `cand-6797` 的空间关系留待 S6，不在 S4 建边。

S4 当前登记555组/699条候选映射；待登记4,249组/4,280条；KU 总数1,574。

<a id="s4-place-ss-vincenzo-ed-anastasio-20261017"></a>

### S4 place：SS. Vincenzo ed Anastasio 教堂建筑地点登记（2026-10-17）

索引候选 `cand-0723` 属 S3 单成员组 sg3-place-cand-0723，类型为 place，索引主项 Churches 下的子目为 SS. Vincenzo ed Anastasio。现登记为[圣文森佐与圣阿纳斯塔西奥教堂地点卡](../../../04-knowledge/units/places/church-ss-vincenzo-ed-anastasio.md)。第7章 p.183 的立面记述将其指作建筑地点，并说明位置语境为已登记的 Piazza di Trevi。教堂建筑、广场及立面 work 候选 `cand-6797` 各保留为不同对象；本次只登记教堂 place。

`st-chp7-p183-i08` 中建筑与立面、广场的关系仍留待 S6 审查，不写入 `relations.csv`。本卡不补外部建筑名、坐标、建造历史或现存状态，也未新增 S5 enrichment。

S4 当前登记556组/700条候选映射；待登记4,248组/4,279条；KU 总数1,575。

<a id="s4-work-mazarin-facade-ss-vincenzo-20261017"></a>

### S4 work：Mazarin 委托的 SS. Vincenzo ed Anastasio 教堂立面（2026-10-17）

单成员 S3 作品组 `workgrp-568625e1ef6077`（`cand-6797`）映射至[特雷维广场圣文森佐与圣阿纳斯塔西奥教堂立面作品卡](../../../04-knowledge/units/works/facade-ss-vincenzo-ed-anastasio-piazza-di-trevi.md)。第7章 p.183 称 Mazarin 经 Paolo Maccarani 委托建筑师 Martino Longhi the Younger 增建立面；哈斯克尔另述工程延宕及经济困难，并将立面解释为彰显枢机权威。后者保留为作者解释。卡片将立面 work 与教堂建筑及 Piazza di Trevi place 分开；跨章端点在本次登记前均已有 KU 去向。

本段关联的 5 条 S2 关系候选 `st-chp7-p183-i08, st-chp7-p183-i09, st-chp7-p183-i10, st-chp7-p183-i12, st-chp7-p183-n3-facade-inscription` 留待 S6 逐条核验。脚注所引档案与铭文未在本轮独立核阅，不据此新增证据或关系；`relations.csv` 与 `enrichment.jsonl` 未变更。

S4 当前登记557组/701条候选映射；待登记4,247组/4,278条；KU 总数1,576。

<a id="s4-work-sant-andrea-tribune-dome-decoration-20261017"></a>

### S4 work：谷地圣安德烈堂祭坛席与穹顶装饰项目（2026-10-17）

单成员 S3 作品组 `workgrp-2c7580b60f39a4`（`cand-5064`）映射至[圣安德烈堂祭坛席与穹顶装饰项目作品卡](../../../04-knowledge/units/works/s-andrea-della-valle-tribune-dome-decoration.md)。第3章 p.72 记录 Montalto 的初始承诺及后来委托分配变化：Domenichino 获得装饰工作，Lanfranco 获得穹顶部分，两位画家分担委托；哈斯克尔称两人至1628年完成各自任务。初始承诺不等于最终分配。本卡记录整体项目，与已登记的 Lanfranco 穹顶壁画作品分别处理；正式作品组成及人物、地点、术语关系留待 S6。

关联的 7 条关系候选留待 S6；两条聚合陈述未标为 relation candidate，仍作为 S2 断言保留。`cand-4500` 巴洛克术语候选尚待 S4；未新增正式关系或 S5 enrichment，`relations.csv` 与 `enrichment.jsonl` 未变更。

S4 当前登记558组/702条候选映射；待登记4,246组/4,277条；KU 总数1,577。

<a id="s4-place-gesu-tribune-20261017"></a>

### S4 place：耶稣堂祭坛席内部空间（2026-10-17）

单成员 S3 地点组 `sg3-place-cand-5000`（`cand-5000`）映射至[耶稣堂祭坛席空间地点卡](../../../04-knowledge/units/places/tribune-of-gesu.md)。第3章 p.66 明确称 Cardinal Alessandro Farnese 将祭坛席装饰专留给家族，并称其死后装饰工程须获继承人许可。该对象是耶稣堂内部建筑空间，区别于教堂建筑、High Altar 与装饰作品。

7条关联关系候选留待 S6；`cand-5007` 继承人和 `cand-5427` 决策参与者群体仍为 S3 undecided。未新增正式关系或 S5 enrichment，`relations.csv` 与 `enrichment.jsonl` 未变更。

S4 当前登记559组/703条候选映射；待登记4,245组/4,276条；KU 总数1,578。

<a id="s4-circignani-stefano-crosschapter-20261017"></a>

### S4 跨章：Circignani 与 S. Stefano Rotondo 殉道壁画组身份登记（2026-10-17）

本次按各自 S3 身份组登记四个对象：`cand-1970`（new-person:circignani-dalle-niccolo-pomarance-f260aa2103）→ [尼科洛·奇尔奇尼亚尼](../../../04-knowledge/units/persons/niccolo-circignani-dalle-pomarance.md)；`cand-10924`（sg3-place-cand-10924）→ [罗马圣斯特凡诺圆形堂](../../../04-knowledge/units/places/s-stefano-rotondo-rome.md)；`cand-5020`（sg3-institution-cand-5020）→ [晚期罗马帝国](../../../04-knowledge/units/institutions/late-roman-empire.md)；`cand-5019`（workgrp-859c21d6ba4ca9）→ [圣斯特凡诺圆形堂殉道题材壁画组](../../../04-knowledge/units/works/circignani-martyrdom-fresco-cycle-s-stefano-rotondo.md)。第3章 p.67 将一组早期基督教殉道壁画归于 Niccolò Circignani dalle Pomarance，并称一位未具名校长委托其创作；后记 p.399 再以 Circignani 指称 S. Stefano Rotondo 的同组殉道场景。索引 P.csv#171 将人物条目连至 p.67 与 p.399，支持人名和跨章身份对应。作品、画家、教堂地点和 Late Roman Empire 政治实体分别登记，不合并为同一 KU。

第20章通过哈斯克尔转述 Thomas Buser 对教诲意图和形式的比较，不把它写成图像构图的直接来源；未独立查阅 Buser 原文。六条 S2 关系候选 `st-chp3-secii-l19-31-jesuits-pride-in-innovation, st-chp3-secii-l19-31-rector-commissioned-stefano-cycle, st-chp3-secii-l19-31-stefano-cycle-martyrdoms-setting, st-chp3-secii-l19-31-stefano-torture-explanations-attached, st-chp3-secii-l19-31-venetian-tradition-in-subjects, st-chp3-secii-p67-note2-necrology-claim` 留待 S6。其余未决对象保留原 S3 去向：cand-5017 German College、cand-5018 未具名校长、cand-4319 Venetian High Renaissance tradition、cand-5147 Lauretano、cand-12311 未分类的说明文字组；不因四项登记而提升为已知端点。未新增正式关系或 S5 enrichment，`relations.csv` 与 `enrichment.jsonl` 未变更。

S4 当前登记563组/707条候选映射；待登记4,241组/4,272条；KU 总数1,582。

<a id="s4-gesu-high-altar-muziano-works-20261017"></a>

### S4：耶稣堂主祭坛、Muziano 與《The Circumcision》登记（2026-10-17）

按三个独立 S3 身份组登记：`cand-1720`（new-person:girolamo-muziano-85c13d2489）→ [吉罗拉莫·穆齐亚诺](../../../04-knowledge/units/persons/girolamo-muziano.md)；`cand-4999`（workgrp-75fd35c26a4b62）→ [耶稣堂主祭坛](../../../04-knowledge/units/works/gesu-high-altar.md)；`cand-5003`（workgrp-c358a8984d4dc4）→ [耶稣堂主祭坛《割礼》祭坛画](../../../04-knowledge/units/works/muziano-circumcision-gesu-high-altar.md)。第3章 p.66 称 Cardinal Alessandro Farnese 委托 Girolamo Muziano 为 High Altar 绘制《The Circumcision》，并称 Farnese 将主祭坛装饰保留给自己及家族。人物、祭坛结构和绘画分别建卡；S3 已将 High Altar 定为 work，故不与耶稣堂 place 或祭坛画合并。原书未说明该画是否完成、材质或现存地点，本轮不补写。

四条相关 S2 关系候选 `st-chp3-secii-l6-17-muziano-circumcision-commission, st-chp3-seciv-l16-24-cardinal-high-altar-decoration, st-chp3-seciv-l16-24-farnese-heirs-high-altar-decoration, st-chp3-seciv-l26-33-ignatius-remains-proposed-relocation` 留待 S6；继承人候选 `cand-5007` 仍为 undecided。未新增正式关系或 S5 enrichment，`relations.csv` 与 `enrichment.jsonl` 未变更。

S4 当前登记566组/710条候选映射；待登记4,238组/4,269条；KU 总数1,585。

<a id="s4-place-gesu-apse-20261017"></a>
<a id="s4-place-gesu-side-chapels-20261017"></a>

### S4 place：耶稣堂后殿与侧礼拜堂群（2026-10-17）

按 S3 的两个单成员地点组分别登记：`cand-5001`（`sg3-place-cand-5001`）→ [耶稣堂后殿地点卡](../../../04-knowledge/units/places/apse-of-gesu.md)；`cand-5002`（`sg3-place-cand-5002`）→ [耶稣堂侧礼拜堂群地点卡](../../../04-knowledge/units/places/side-chapels-of-gesu.md)。第3章 p.66 分别以 apse、tribune 和 side-chapels 指称后殿、祭坛席及侧礼拜堂群；本批保持这些名称对应的身份边界，不将后殿与祭坛席断言为边界互不重叠的空间，也不将复数侧礼拜堂群拆成未被逐一识别的成员。

后殿与祭坛席的术语区分另经外部资料交叉核对：《耶稣堂》官方介绍分别称述 catino dell'abside 与 tribuna 的装饰；Nayyar 的同行评审研究亦分别讨论 apse vault 与 tribune patronage rights。此核对只支持保留原书分别命名的参照，不补写精确建筑边界或现状：[官方教堂介绍](https://www.chiesadelgesu.org/documenti/presentazione_chiesa_del_gesu_roma.pdf)；[Nayyar, “Joshua and the Jesuits: The Battle for the Apse of the Gesù”](https://brill.com/view/journals/jjs/3/2/article-p211_3.pdf)。

后殿关系候选 `st-chp3-seciv-l75-81-apse-after-oliva` 与侧礼拜堂群的 6 条候选关系留待 S6；未具名继承人 `cand-5007`、决策参与者群体 `cand-5427` 和 pious ladies 术语候选 `cand-5008` 维持原 S3 待决状态。已有单体礼拜堂 KU 与侧礼拜堂群分开保留，本批不推定具体成员或建立包含边。未新增正式关系或 S5 enrichment，`relations.csv` 与 `enrichment.jsonl` 未变更。

S4 当前登记568组/712条候选映射；待登记4,236组/4,267条；KU 总数1,587。

<a id="s4-archive-ignatius-xavier-canonization-centenary-20261017"></a>
<a id="s4-archive-redig-de-campos-van-dyck-gesu-1936-20261017"></a>

### S4 archive：第3章封圣纪念出版物与 Redig de Campos 论文（2026-10-17）

按两个独立 S3 archive 组分别登记：cand-4992（archive-group-ecd7f6180feb）映射至[封圣三百周年纪念集 archive 卡](../../../04-knowledge/units/archives/ignatius-xavier-canonization-centenary-1923.md)。第3章 p.64 注3列原题、Roma、1923；题名逐字保留 Haskell 印刷文本中的拼写。原卷与独立目录记录未查阅，故不补出版者、编者、馆藏或完整版本信息。该脚注关系候选留待 S6。 cand-4993（archive-group-220a5b4072d7）映射至[Redig de Campos 论文 archive 卡](../../../04-knowledge/units/archives/redig-de-campos-van-dyck-gesu-article-1936.md)。第3章 p.64 注3给出作者姓氏与年份，第21章 p.435 书目条目提供题名、期刊、卷、年份与页码；论文原文未独立查阅。注释引用关系候选留待 S6，书目条目只作为本卡身份依据。

两项引用关系候选 st-chp3-seci-l35-43-canonization-volume-citation、st-chp3-seci-l35-43-redig-de-campos-citation 留待 S6；对应事件组 cand-4980 尚未登记，本批不预建关系。relations.csv 与 enrichment.jsonl 未变更，也未新增正式关系或 S5 enrichment。

S4 当前登记570组/714条候选映射；待登记4,234组/4,265条；KU 总数1,589。

<a id="s4-event-gregory-xv-canonisation-20261017"></a>

### S4 event：格列高利十五世时期的册封事件（2026-10-17）

单成员 S3 事件组 sg3-event-cand-4980（cand-4980）登记至[册封事件卡](../../../04-knowledge/units/events/gregory-xv-canonisation-ignatius-francis-xavier-philip-neri.md)。第3章 p.64 称 Gregory XV 颁令册封 Ignatius、Francis Xavier 与 Philip Neri，并称其后举行庆典；原段未给出精确日期或庆典地点，本卡不补写。

该事件与同段随后提到的 1639–1640 年耶稣会会规获批百周年庆典候选 cand-4981 分开；Van Dyck 绘画候选 cand-4977 仍为 undecided。三条关联 S2 关系候选 st-chp3-seci-l16-24-canonisation-occasion-paintings, st-chp3-seci-l35-43-canonization-volume-citation, st-chp3-seci-l35-43-redig-de-campos-citation 留待 S6。cand-1309 的 Ignatius 人物身份保持 undecided；本次不为未决人物或画作建立关系或合并身份。

S4 当前登记571组/715条候选映射；待登记4,233组/4,264条；KU 总数1,590。

<a id="s4-event-jesuit-statutes-centenary-1639-1640-20261017"></a>

### S4 event：耶稣会会规获批百周年庆祝语境（2026-10-17）

单成员 S3 事件组 sg3-event-cand-4981（cand-4981）登记至[百周年庆祝事件卡](../../../04-knowledge/units/events/jesuit-statutes-centenary-celebrations-1639-1640.md)。第3章 p.64 称 Urban VIII 于1639和1640年两次到访耶稣堂，当时正在庆祝耶稣会会规获批百周年。本卡将这两次到访保留为共同庆祝语境，不拆成两项，也不推算会规批准日。

该对象与第2章 1639 年接待候选 cand-4761 保持分立：两者处于同一百周年纪念语境，但当前 S3 决定分别对应两次到访的集体语境与单次接待。来源行未为 cand-4981 生成 book-statements 关系候选；本次只登记事件身份，不新增正式关系，不能据此宣称其关系审查已完成。

S4 当前登记572组/716条候选映射；待登记4,232组/4,263条；KU 总数1,591。

<a id="s4-place-antwerp-cross-chapter-roomer-20261017"></a>

### S4 place：安特卫普跨章地点端点（2026-10-17）

单成员 S3 地点组 sg3-place-cand-4983（cand-4983）映射至[安特卫普地点卡](../../../04-knowledge/units/places/antwerp.md)。第3章 p.64 将 Antwerp 作为耶稣会士出版 Imago primi saeculi 的城市，第8章 p.205 又明确记载 Gaspar Roomer 出生于 Antwerp，支持两个章节指向同一城市地点。现有 Roomer 人物端点 cand-2223 已复用至 units/persons/gaspar-roomer。

关系候选 st-chp8-p205-roomer-origin-residence-gallery 保留待 S6 审查；本次只登记城市身份，不写入出生地正式边，不新增 S5 enrichment。

S4 当前登记573组/717条候选映射；待登记4,231组/4,262条；KU 总数1,592。

<a id="s4-archive-galassi-ottonelli-casale-20261017"></a>

### S4 archive 与直接人物端点：Galassi Paluzzi、Ottonelli–Pietro da Cortona、Vittorio Casale（2026-10-17）

- `cand-4974`（`archive-group-0126bbcbcfbc`）登记至[《耶稣会风格秘史》](../../../04-knowledge/units/archives/storia-segreta-stile-gesuiti-1951.md)。第3章开篇注1引用Galassi Paluzzi, 1951，并报告其书目覆盖范围；第21章p.423列完整原题、作者缩写和Roma 1951书目项。书籍及评价未独立查阅或核验，未扩展作者姓名、出版者或著作内容。
- `cand-4979`（`archive-group-e399514e8ce5`）登记至[《绘画与雕塑论：其用途与滥用》](../../../04-knowledge/units/archives/ottonelli-cortona-treatise-1652.md)，对象粒度限定为第21章p.432所列Firenze 1652版本。第3章p.64正文和注5记录合作论著及括号署名；原书目假名、方括号责任者和完整题名照录。第20章p.400的后出版本叙述保留为书内语境，不当作本项目读过1652年版或审查意见的证据。
- `cand-10937`（`new-person:casale-vittorio-9476a988c6`）登记至[维托里奥·卡萨莱人物卡](../../../04-knowledge/units/persons/vittorio-casale.md)。第20章p.400及第21章p.432明确以Vittorio Casale全名提及其与后出版本／审查意见的关联；仅登记书内可识别人物身份，不扩展传记。
- 1652年版本与第21章另列的Treviso 1973年版分开处理。`cand-11160` 的S3状态为 `undecided`，本次未写入KU或关系。Ottonelli人物候选 `cand-1800` 因姓名形式不足仍为 `undecided`；Pietro da Cortona复用既有`units/persons/pietro-da-cortona`。候选`cand-10938`所指未具名审查意见文献仍未决，不与书本身合并。
- Galassi组2条、Ottonelli论著组4条、Casale人物组1条直接S2关系候选均留待S6；本次没有新增正式关系或S5补足。登记依据只限Haskell书内段落、脚注和书目。

S4 当前登记576组/720条候选映射；待登记4,228组/4,259条；KU 总数1,595。

<a id="s4-archive-rapparini-de-bello-20261017"></a>

### S4 archive 与直接人物端点：Rapparini颂词、De Bello Belgico、Famiano Strada（2026-10-17）

- `cand-2108`（`archive-group-91edf12eec0e`）登记至[《普法尔茨选侯殿下所体现的真德》](../../../04-knowledge/units/archives/le-portrait-du-vrai-merite-rapparini-1709.md)。第10章p.282注1给出题名，并称该颂词写于1709年、Rapparini文稿于Dusseldorf 1958年出版。既有S2记录已将扫描读作`Mérité`校为`Mérite`、将`hill`校为`full`；本次沿用该S2校勘，不声称重读文献或扫描。Rapparini人物端点已复用units/persons/giorgio-maria-rapparini。
- `cand-2515`（`archive-group-80d625037359`）登记至[《比利时战争》](../../../04-knowledge/units/archives/de-bello-belgico.md)，仅到书名层级。第5章p.137称第二卷，并叙述1647年Cerquozzi与Jan Miel、Giacomo Borgognone等人为该卷作插图；1647不作出版年。Haskell明确称书为Famiano Strada之作，因此其S3新人物端点`cand-2514`同步登记至[法比亚诺·斯特拉达](../../../04-knowledge/units/persons/famiano-strada.md)。Miel、Borgognone和Cerquozzi端点已分别映射既有卡。
- De Bello组的6条S2关系候选均留待S6；campaign事件端点`cand-11927`和未具名艺术家组`cand-11930`在S3为`undecided`，本次未推定或创建KU。Rapparini颂词的1条关系候选及Strada著作归属候选也留待S6；没有新增正式边或S5补足。

S4 当前登记579组/723条候选映射；待登记4,225组/4,256条；KU 总数1,598。

<a id="s3-correction-existing-archive-duplicates-20261017"></a>

### S3 更正：四项书内文书已对应既有archive KU（2026-10-17）

S4重复对象预检发现下列全书S3新组与既有章前/单章KU指向同一件文献。保留原S3 `new` 文字作为历史，在当前决定列改为`same`并直接映射到唯一既有KU，不新建重复卡：

| 候选 | 当前决定 | 既有KU | 对齐依据 |
|---|---|---|---|
| `cand-3541`（原组 `archive-group-ad7b3715e8f9`） | `same` | `units/archives/camassei-sebastian-receipt` | Haskell第1章p.10注1 L372以相同的Bertolotti Artisti bolognesi pp.161–162收据识别Andrea Camassei；既有卡已逐项读取该同一引文及付款文书，来源与对象定位完全重合。 |
| `cand-3543`（原组 `archive-group-957100686406`） | `same` | `units/archives/gini-cortona-letter-1666` | Haskell第1章p.11注1 L415–418记Onorato Gini 1666年书信并称由Claretta 1885 p.516概述；既有卡记录相同发信人、年份、转引和内容语境，收信人及原件号同样未明。 |
| `cand-3549`（原组 `archive-group-c9cd423af65c`） | `same` | `units/archives/testi-fontana-bernini-letter` | Haskell第1章p.17 L699–703所引Fulvio Testi致Conte Francesco Fontana信，与既有卡相同；既有卡已用Fraschetti p.108刊引补出1633-01-29日期，候选1633年描述对应这一书信。 |
| `cand-3558`（原组 `archive-group-74048430b6b1`） | `same` | `units/archives/arragona-mantua-letter-1621` | Haskell第1章p.14 L542–547、567–568记Mantua驻罗马代理Fabrizio Arragona于1621-10-09致一名未具名公国大臣，刊于Luzio p.295；既有卡定位到同一日期、发信人、收信角色与刊布链。 |

本次只修正身份去向，不改写来源、既有卡内容或S6关系；后续S4计数按修正后的S3决定重算。当前S4新组已登记579组/723条候选映射，待登记4,221组/4,252条；KU总数1,598。

<a id="s4-crosschapter-pecchiai-i-barberini-1959-20261017"></a>

### S3跨章合组与S4登记：Pecchiai《I Barberini》（2026-10-17）

`cand-4239`与`cand-4575`此前分别处于`archive-group-504003309f78`和`archive-group-78dbb797828e`两个单成员archive新组。逐条核对后合并为`archive-group-pecchiai-i-barberini-1959`：第2章开篇注1以`Pecchiai, 1959`作总体书目指引；第2章p.41注3引第130页及后续页；第2章p.47注2引第161页及后续页并报告Pecchiai所刊文件与Pastor说法的冲突；第2章p.54注1再次引用该书；第21章p.433完整列出`Pecchiai, P.: I Barberini, Roma 1959`。题名、责任者缩写、出版地与年份一致，支持两候选属于同一书目身份。

两候选映射至唯一[《巴贝里尼家族》archive KU](../../../04-knowledge/units/archives/pecchiai-i-barberini-1959.md)。`cand-4238`所指作者人物仅有姓氏和首字母，S3仍为`undecided`；卡内保留书目署名，不扩展姓名或创建作者正式关系。Pecchiai所刊文件与Pastor关于Taddeo道德操守的冲突仅按Haskell原话保留，书和所引页未独立查阅；2条关系候选留待S6。没有新增S5补足。

S4 当前登记580组/725条候选映射；待登记4,219组/4,250条；KU总数1,599。

<a id="s4-archive-fraschetti-and-avviso-20261017"></a>

### S4 archive：Fraschetti《Il Bernini》及1633年Avviso（2026-10-17）

- `cand-4553`（`archive-group-3091943966c4`）登记至[Fraschetti《Il Bernini》书目卡](../../../04-knowledge/units/archives/fraschetti-il-bernini-1900.md)。第21章p.422将其列为`Fraschetti, S.: Il Bernini, Milano 1900`；第1章p.17、第2章p.37与p.58、第5章p.123等多处引文共同支持它们指向同一出版物。作者候选`cand-3519`只有首字母，S3仍未决；本卡不扩展其身份。
- `cand-4554`（`archive-group-fad1206fd041`）登记至[1633年1月8日Avviso文书卡](../../../04-knowledge/units/archives/este-resident-avviso-1633-01-08-bernini.md)。唯一直接证据为第2章p.37注1：Haskell称其来自罗马埃斯特使节，记载日期，并引述意大利语文字；Cardinal Borghese仅保留姓氏，原报告、Fraschetti p.107及档案定位未独立查阅。
- `cand-4554`有S2提及`m-chp2-secii-l147-193-0040`及候选来源锚点，但`book-statements.jsonl`当前没有以该文书为主语或宾语的S2关系行。故虽已登记其身份，本次不新建Avviso→Fraschetti正式边；过程明确保留这一来源映射缺口供S6回到p.37原文处理。Haskell关于书籍引文的3条S2关系候选照常留待S6。

S4 当前登记582组/727条候选映射；待登记4,217组/4,248条；KU总数1,601。

<a id="s4-archive-rothlisberger-claude-lorrain-paintings-1961-20261017"></a>

### S4 archive：Röthlisberger《Claude Lorrain—The Paintings》（2026-10-17）

- `cand-4577`（`archive-group-4f5f75670a57`）登记至[Claude Lorrain绘画集 archive KU](../../../04-knowledge/units/archives/claude-lorrain-paintings-1961.md)。第21章p.436书目列出两卷本 *Claude Lorrain—The Paintings*，Yale and London 1961；第2、4、6、7章的页码引文指向同一书目身份。INHA AGORHA完整著录作者 Marcel Röthlisberger、两卷本与New Haven 1961（https://agorha.inha.fr/ark:/54721/6ca774b1-afc0-47eb-ac34-561be13db605）。
- 本卡覆盖该两卷本书目身份；第7章两注明确标卷I，其余未标卷的定位不强行分配到具体卷册。已存在的 Claude Lorrain 人物卡不与本书合并；书目身份不验证书中引文内容或具体绘画归属。
- 10条直接S2陈述中4条为关系候选，保留待S6；本次只登记KU，不新增正式关系或S5补足。

This one-member S3 archive group is registered as the bibliographic identity of the 1961 two-volume publication. Haskell’s chapters 2, 4, 6, and 7 cite the same title-year record, and chapter 21 supplies the bibliography entry. INHA AGORHA records Marcel Röthlisberger as author and gives the two-volume New Haven 1961 publication. Volume I is retained only for citations explicitly marked as such in chapter 7. The book remains distinct from the Claude Lorrain person KU. Four direct S2 relation candidates remain pending S6; no formal relation or S5 enrichment was added.

S4 当前登记583组/728条候选映射；待登记4,216组/4,247条；KU总数1,602。

<a id="s4-archive-mancini-considerazioni-sulla-pittura-1956-20261017"></a>

### S4 archive：Mancini《Considerazioni sulla Pittura》1956年版（2026-10-17）

- `cand-1508`（M.csv#45，pp.124、130）与`cand-6089`（第5章正文／第21章书目）保留同一S3身份组`archive-group-fb110b11a649`，共同映射到[1956年版archive KU](../../../04-knowledge/units/archives/mancini-considerazioni-sulla-pittura-1956.md)。书目p.428给出完整题名、Adriana Marucchi编、Luigi Salerno注释、Roma 1956、2 vols；第1章注1和第5章注3的卷I页码定位及第5章注4的1956年校勘版说明相互支持。文献未独立查阅。
- 两名候选写入同一KU；不把第5章p.124的泛称`Treatise`另建对象，也不与Giulio Mancini人物KU合并。4条直接S2陈述中3条关系候选留待S6；本次不添加正式边或S5补足。

The index candidate and the body/bibliography candidate remain one S3 archive group and map to a single KU. Haskell's bibliography records the full title, Marucchi as editor, Salerno's commentary, Rome 1956, and two volumes; chapter 1 and chapter 5 cite volume I, and chapter 5 also points to the 1956 critical edition. The edition was not independently consulted. Three of the four direct S2 statements remain relation candidates for S6; no formal relation or S5 enrichment was added.

S4 当前登记584组/730条候选映射；待登记4,211组/4,245条；KU总数1,603。

<a id="s3-mancini-group-token-normalization-20261017"></a>

### S3组号分隔符核正：Mancini 1956年版（2026-10-17）

`cand-1508`与`cand-6089`此前已判为同一身份组并映射到同一 KU；`cand-1508` 的组号后误用句点，使分组统计把后续说明文字并入组号，导致登记组数多计1。现将组号后的标点改为分号，候选决定、组号主体、KU映射和原理由均保留。重算后S4为584组/730条候选映射已登记，待登记4,214组/4,245条；KU总数仍为1,603。这是计数与机器解析边界更正，不是新的身份裁决。

`cand-1508` and `cand-6089` were already assigned to the same identity group and KU. A period after the group token on `cand-1508` caused the grouping parser to absorb following prose and count a second group. The separator is now a semicolon; the decision, identity, KU mapping, and prior rationale remain unchanged. Counts were recalculated; this corrects parsing and reporting only.

<a id="s3-remaining-group-token-delimiter-normalization-20261017"></a>

### S3组号分隔符核正：Manfrin、耶稣档案与Marino组（2026-10-17）

全表复核发现5条`new`候选的`group=`字段在身份组号后直接接入解释文字：`cand-1515`、`cand-1532`、`cand-1549`、`cand-1551`、`cand-1791`。将句点或逗号改为分号，使解析器只读取原组号；这5条候选的S3决定、KU映射和理由内容均未改变。`cand-1515`与`cand-10849`、`cand-1532`与`cand-5338`、`cand-1551`与`cand-4464`各自解析为同一双候选组，修正后待登记组数减少3；`cand-1549`和`cand-1791`为单成员组，修正不改变登记组数。

重算后当前S3为new=4,975个候选／4,795个身份组；S4已登记584组／730条映射，待登记4,211组／4,245条；KU总数1,603。该修正只校正组号解析和统计，不增加或撤销身份决定。

Five `new` alignment notes had punctuation immediately after an identity-group token, causing the parser to absorb following prose. Delimiters were normalized for `cand-1515`, `cand-1532`, `cand-1549`, `cand-1551`, and `cand-1791`; decisions, mappings, and rationale text were retained. Three two-candidate groups now parse as one group each, reducing pending S4 groups by three. The two single-member group fixes do not change group counts.

<a id="s4-archive-manfrin-edwards-letter-1793-12-03-20261017"></a>

### S4 archive：Manfrin致Edwards书信（1793-12-03；2026-10-17）

- `cand-1515`（M.csv#52，p.395）与`cand-10849`（第19章附录7）同属`archive-group-4ec5e3284567`，共同映射至[1793年书信archive KU](../../../04-knowledge/units/archives/manfrin-edwards-letter-1793-12-03.md)。附录标题明确Girolamo Manfrin致Pietro Edwards、日期1793-12-03及画廊形成主题；第17章p.380注6称书信藏于Biblioteca Correr的Epistolario Meschini并在附录7全文刊出。附录标题写作Epistolario Moschini；两处拼写均保留。手稿未独立查阅。
- 该KU仅指单封书信，与`cand-10605`所指档案系列Epistolario Moschini分开。2条直接S2关系候选留待S6；本次只登记身份，不新增正式边或S5补足。

The index entry and the Appendix 7 letter candidate map to one KU. The appendix heading identifies Manfrin as sender, Edwards as recipient, gives the date 3 December 1793, and describes the letter's subject as the formation of Manfrin's gallery. Chapter 17, page 380, note 6 points to the same letter and spells the collection Meschini; Appendix 7 spells it Moschini. Both forms are retained. The manuscript was not independently consulted. The letter remains distinct from the archival series candidate; both direct S2 relation candidates remain pending S6.

S4 当前登记585组/732条候选映射；待登记4,210组/4,243条；KU总数1,604。

<a id="s4-institution-biblioteca-direct-endpoints-20261017"></a>

### S4 institution：两项书内具名图书馆端点（2026-10-17）

- `cand-8556`（`sg3-institution-cand-8556`）登记至[克雷莫纳 Biblioteca Governativa](../../../04-knowledge/units/institutions/biblioteca-governativa-cremona.md)。第9章p.262注6给出MSS. aa.I.4.1，第10章p.328注5定位Biffi致Signor Vacchelli的1773年未刊信；第10章书页读作Governativa，OCR作Govcrnativa。该卡只记录Haskell书内名称和地点。
- `cand-9493`（`sg3-institution-cand-9493`）登记至[佛罗伦萨 Biblioteca Marucelliana](../../../04-knowledge/units/institutions/biblioteca-marucelliana.md)。第10章p.299及pp.306–307、p.328多条信件注释和第13章p.342注6均以该馆为保存处；原件与馆藏目录未独立查阅。
- 两组各登记一张institution KU。直接S2关系候选分别为2条和5条，合计7条，全部留待S6；本次不新增正式关系或S5补足。

`cand-8556` and `cand-9493` are registered as separate institution KUs based on Haskell's named repository references. The book supplies localities and manuscript locators; no manuscripts or repository catalogues were independently consulted. All seven direct S2 relation candidates remain pending S6, and no formal relation or S5 enrichment was added.

S4 当前登记587组/734条候选映射；待登记4,208组/4,241条；KU总数1,606。

<a id="s4-person-varotari-longhi-20261017"></a>

### S4 person：两组跨章人物关系端点（2026-10-17）

- `cand-2701`（`new-person:alessandro-varotari-il-padovanino-8619a21d71`）登记至[Alessandro Varotari](../../../04-knowledge/units/persons/alessandro-varotari-il-padovanino.md)。第4章p.105明确写出全名与别称“il Padovanino”，并记述其赴罗马临摹Titian的《维纳斯的崇拜》；第13章p.340另以Padovanino列名。S3已依据同一全名／明确别称锚点完成组内对齐，未调用外部身份来源。
- `cand-5505`（`new-person:longhi-roberto-5fac70ede1`）登记至[Roberto Longhi](../../../04-knowledge/units/persons/roberto-longhi.md)。S2跨第4、5、7、20章记录同一全名及姓氏指代；本卡以第5章p.136注3和第20章p.396作为书内事实依据，保留哈斯克尔对Velasquez归属的限定。
- 两组均为S3 `new`，各登记一个KU；直接S2关系候选共5条，均留待S6：`st-chp4-sec-ii-l80-89-cassiano-acquired-varotari-pictures`, `st-chp4-sec-ii-l80-89-varotari-travelled-to-copy-worship`, `st-chp4-sec-ii-p100-varotari-assumption`, `st-chp5-notes-l140-velasquez-attribution`, `st-chp20-p396-longhi-alternative-portrait`。本次未登记外部核验状态、作品归属事实或正式关系。

`cand-2701` and `cand-5505` are registered as separate person KUs from cross-chapter book evidence. The book supports the names, alias, and cited contexts; no external identity records were consulted. All five direct S2 relation candidates remain pending S6, and no formal relations were added.

S4 当前登记589组/736条候选映射；待登记4,206组/4,239条；KU总数1,608。

<a id="s4-person-peter-vignola-20261017"></a>

### S4 person：两组跨章人物关系端点（2026-10-17）

- `cand-4231`（`new-person:apostle-peter-94e2c375ba`）登记至[使徒圣彼得](../../../04-knowledge/units/persons/saint-peter-the-apostle.md)。S2在第2、3、6、8、9章累计记录16处提及，明确区分使徒本人、同名教堂地点及作品题名；本卡以第2章p.35和第3章p.72的具名语句作为证据。两条直接关系候选为华盖中的圣彼得象征及Lanfranco穹顶人物描绘，均待S6。
- `cand-2775`（`new-person:barozzi-da-giacomo-vignola-072c61027f`）登记至[Giacomo Barozzi da Vignola](../../../04-knowledge/units/persons/giacomo-barozzi-da-vignola.md)。原书索引规范全名并列出跨章页码65、103、338、398；第3章p.65称其为Alessandro Farnese的建筑师，第4章和第20章继续出现其名。S3已按索引全名及跨章指称完成身份组，不调用外部身份记录。
- 两组新增2个person KU、2条候选映射；1条雇用建筑师关系候选与2条涉及圣彼得的关系候选共3条，全部保留待S6。未新增正式关系或S5事实。

`cand-4231` and `cand-2775` are registered as separate person KUs from cross-chapter book evidence. S2 distinguishes the apostle Peter from the basilica and similarly named work; the Vignola group follows the book index's full name and chapter references. All three direct relation candidates remain pending S6; no external identity records or formal relations were added.

S4 当前登记591组/738条候选映射；待登记4,204组/4,237条；KU总数1,610。

<a id="s4-person-montagu-diderot-20261017"></a>

### S4 person：两组跨章人物关系端点（2026-10-17）

- `cand-1688`（`new-person:lady-mary-montagu-wortley-e31f25b442`）登记至[Lady Mary Wortley Montagu](../../../04-knowledge/units/persons/lady-mary-wortley-montagu.md)。第10章p.302与第14章p.349分别给出Mary Wortley Montagu和Lady Mary Wortley Montagu，并记录不同语境；两项姓名与书内指代支持同一人物身份。两个直接关系候选均保留待S6。
- `cand-0919`（`new-person:denis-diderot-940e9e0035`）登记至[Denis Diderot](../../../04-knowledge/units/persons/denis-diderot.md)。第14章p.356正文及注5、第二版后记p.409再次提及其对Algarotti遗赠行为的讽刺反应；法文原话在书中注明经Treat转引，本次未独立核对Treat原书。两条直接关系候选均保留待S6。
- 两组新增2个person KU和2条候选映射；4条直接S2关系候选保持待S6，不登记正式关系、不添加外部身份核验状态。

`cand-1688` and `cand-0919` are registered as separate person KUs based on cross-chapter names and references. Haskell's Diderot quotation is explicitly mediated through Treat and was not independently checked. All four direct relation candidates remain pending S6; no formal relations or external identity status were added.

S4 当前登记593组/740条候选映射；待登记4,202组/4,235条；KU总数1,612。

<a id="s4-person-lemaire-gai-20261017"></a>

### S4 person：两组跨章人物关系端点（2026-10-17）

- `cand-1385`（`new-person:jean-lemaire-e5876e626a`）登记至[Jean Lemaire](../../../04-knowledge/units/persons/jean-lemaire.md)。第4章p.105明示其为Poussin之友并称其制作capricci；第7章p.176再次以全名将其作为Poussin的朋友提及。两个直接关系候选留待S6。
- `cand-1099`（`new-person:antonio-gai-479e2478a1`）登记至[Antonio Gai](../../../04-knowledge/units/persons/antonio-gai.md)。第10章p.293称其为雕塑家并记Tessin特别欣赏他；第13章正文转录在页标342称其制作一件人物雕像，Tessin称其为“un demi-Michel Ange”。书内索引G.csv L8给出全名Antonio Gai，但页码列为293、341；第13章源码页标为342，故同时保留，不改写为同页。相关雕像无正式题名或完成状态依据。
- 两组新增2个person KU、2条候选映射；直接S2关系候选共4条，全部留待S6；本次未新增正式关系或外部身份核验状态。

`cand-1385` and `cand-1099` are registered as separate person KUs from cross-chapter book references. The Gai identity follows the book index's full name; its index page 341 and the chapter transcription's page marker 342 are both retained. All four direct relation candidates remain pending S6.

S4 当前登记595组/742条候选映射；待登记4,200组/4,233条；KU总数1,614。

<a id="s4-person-peiresc-sandrart-20261017"></a>

### S4 person：两组跨章人物关系端点（2026-10-17）

- `cand-1861`（`new-person:claude-de-fabri-nicolas-peiresc-cf0115e95f`）登记至[Nicolas-Claude-Fabri de Peiresc](../../../04-knowledge/units/persons/nicolas-claude-fabri-de-peiresc.md)。第2章p.30称其为普罗旺斯古物学者，第4章p.100引用其对Cassiano的称誉；P.csv L64给出索引全名并列页30、100、107注。两条直接关系候选均待S6。
- `cand-2353`（`new-person:german-joachim-sandrart-von-joachim-sandra-2467fbbb7e`）登记至[Joachim von Sandrart](../../../04-knowledge/units/persons/joachim-von-sandrart.md)。第2章p.29以全名称其为德国人，第8章p.205再次以Sandrart姓氏转述其所见Cato绘画；S.csv L43确认书内索引姓名。两条直接关系候选均待S6。
- 两组新增2个person KU和2条候选映射；4条直接S2关系候选保留待S6，不新增正式关系或外部身份核验状态。

`cand-1861` and `cand-2353` are registered as separate person KUs from cross-chapter references and book-index names. All four direct relation candidates remain pending S6; no external identity records or formal relations were added.

S4 当前登记597组/744条候选映射；待登记4,198组/4,231条；KU总数1,616。

<a id="s4-person-petty-pitt-paul-iii-20261017"></a>

### S4 person：三组跨章人物关系端点（2026-10-17）

- `cand-1894`（`new-person:petty-william-e0750fd206`）登记至[William Petty](../../../04-knowledge/units/persons/william-petty-arundel-agent.md)。第4章p.97称Lord Arundel给代理人写信，注5（p.98）指明寄往William Petty；第7章p.179再次称Arundel写给罗马的William Petty。相关两条直接关系候选留待S6。
- `cand-1947`（`new-person:elder-pitt-william-a3834b7e2c`）登记至[William Pitt, the Elder](../../../04-knowledge/units/persons/william-pitt-the-elder.md)。第14章p.356记载Algarotti遗嘱将两幅画留给elder Pitt，第20章后记p.409再次提及该遗赠；P.csv L150给出索引全名。直接遗赠候选留待S6。
- `cand-4515`（`new-person:iii-paul-d17277c320`）登记至[Pope Paul III](../../../04-knowledge/units/persons/pope-paul-iii.md)。第2章p.41–42明确写Paul III召集特伦托会议，并续述其陵墓移位；第4章p.104的OCR将Paul III转录为“Paul Ill”，该异文已保留。两条直接关系候选留待S6。
- 三组新增3个person KU和3条候选映射；直接S2关系候选共5条，均不在本次升级为正式关系。

`cand-1894`, `cand-1947`, and `cand-4515` are registered as separate person KUs from cross-chapter book evidence. The Paul III reference in chapter 4 preserves the OCR form “Paul Ill.” All five direct relation candidates remain pending S6; no external identity records or formal relations were added.

S4 当前登记600组/747条候选映射；待登记4,195组/4,228条；KU总数1,619。

<a id="s4-person-catherine-molinari-20261017"></a>

### S4 person：跨章人物关系端点（2026-10-17）

- `cand-0609`（`new-person:catherine-great-of-russia-85ee1f0320`）按S3跨章身份组登记为[叶卡捷琳娜二世](../../../04-knowledge/units/persons/catherine-the-great-russia.md)。第10章p.298称其购买《埃及艳后宴会》；第20章p.406后记明确将作者此前关于她本人购买该画的假定改为“now seems to me over-confident”。这是作者对先前判断把握程度的回撤，并非否认购买。`st-chp10-p298-catherine-tiepolo-purchase`与`st-chp20-p406-catherine-tiepolo-purchase-reassessment`均留待S6，卡片未写成确定的购买关系。
- `cand-1679`（`new-person:antonio-molinari-5e2b48c6a7`）依据第5章p.129“Antonio Molinari”全名及第10章p.294“Molinari”姓氏提及登记为[Antonio Molinari](../../../04-knowledge/units/persons/antonio-molinari.md)。第5章原OCR行读作“sit of patriotic enthusiasm”，印本校读为“fit”；卡片与来源摘要保留此读法差异。来源仅称他在1707年叙述时“had died 25 years earlier”，未据此算出具体去世年份。`st-chp5-p129-molinari-authorship`与`st-chp5-p129-molinari-reception`仍为S2关系候选，待S6逐条裁决。
- 两组各新增一个person KU与一条候选映射；4条直接S2关系候选继续待S6。本次仅做S4登记，不增加外部身份核验或正式关系。

The Catherine group is registered with both the chapter 10 purchase statement and the chapter 20 retrospective qualification visible; the latter limits the author's confidence and does not negate the earlier statement. The Molinari group follows the full name in chapter 5 and surname reference in chapter 10. The OCR/print correction “sit”/“fit” and the source-relative death interval are preserved. All four direct relation candidates remain pending S6; no external identity verification or formal relation was added.

S4 当前登记602组/749条候选映射；待登记4,193组/4,226条；KU总数1,621。

<a id="s3-federigo-zuccari-reuse-20261017"></a>

### S3/S4复核：Federigo Zuccari 同一人物复用（2026-10-17）

- 全书候选`cand-2885`原分入`new-person:federigo-zuccari-2774f913d3`。S4写入预检命中既有`units/persons/federigo-zuccari`卡，停止新建并回查身份依据。
- 既有卡的第一章来源L681–683明确出现“Federigo Zuccari”，该人物已由`cand-3030`经`aln-3307`映射至现有KU。当前S3候选`cand-2885`在第2章p.30及第3章p.66使用同一全名；既有卡将来源形式Federigo对应规范名Federico Zuccari，并保留既有外部身份核对。姓名形式及对象语境一致，判为同一人物。
- 将`cand-2885`当前决定改为`same` → `units/persons/federigo-zuccari`，在`alignment.csv`保留原alignment ID和原新组作为历史说明，并记录本次查重更正。无新增KU、卡片或accepted.yml项；直接关系候选`st-chp3-secii-l6-17-pious-ladies-introduced-zuccari`仍待S6。

The full-book candidate was initially assigned a new group. S4's duplicate check found an accepted Federico Zuccari person KU whose chapter 1 source gives the exact form “Federigo Zuccari,” already aligned through cand-3030. The full name recurs in chapters 2 and 3, so cand-2885 now reuses that KU. The original new grouping is retained in the alignment rationale; no duplicate card was created. The direct relation candidate remains pending S6.

<a id="s4-person-clear-crosschapter-endpoints-20261017"></a>

### S4 person：四组跨章人物关系端点（2026-10-17）

- `cand-2361`（`new-person:andrea-del-sarto-914ca633fc`）依据第2章p.30和第9章p.251的同一全名提及登记为[Andrea del Sarto](../../../04-knowledge/units/persons/andrea-del-sarto.md)。第2章只把他列在Cardinal Barberini宫中旧大师绘画群组的举例中；关系候选`st-chp2-seci-l108-119-palace-paintings-by-andrea-del-sarto`限定为群组层级，不能解释为该组每幅画皆由他创作。
- `cand-4876`（`new-person:da-giovanni-giovanni-san-a3958ee8ea`）依据第2章注释中的全名及第4章重复全名登记为[Giovanni da San Giovanni](../../../04-knowledge/units/persons/giovanni-da-san-giovanni.md)。第2章相关叙述经Haskell转述Baldinucci；直接候选`st-chp2-seciv-l190-245-baldinucci-anecdote`不表示原始轶事已独立核实。
- `cand-1446`（`new-person:louis-xiii-56b02fc735`）依据第2、7章重复全名登记为[Louis XIII](../../../04-knowledge/units/persons/louis-xiii.md)。第2章把礼物与房间中已有的挂毯相邻叙述，原文未在同一分句明确等同；关系候选`st-chp2-seciv-l6-17-louis-xiii-tapestry-gift`保留此来源限定。
- 三组各新增一个person KU与一条候选映射；3条关系候选仍待S6。本次不新增正式关系或外部身份核验状态。

The three groups follow repeated full names across chapters. The Barberini palace attribution remains aggregate, the Giovanni anecdote remains mediated through Baldinucci, and the identification of Louis XIII's gift with the adjacent tapestries remains unresolved. All three relation candidates remain pending S6; no formal relations or external verification statuses were added.

S4 当前登记605组/752条候选映射；待登记4,189组/4,222条；KU总数1,624。

<a id="s4-person-lavin-gregory-xiii-20261017"></a>

### S4 person：两组跨章人物关系端点（2026-10-17）

- `cand-4787`（`new-person:aronberg-lavin-marilyn-88b8833863`）依据第2章p.56注释的全名及第20章p.396后记“Marilyn Lavin”登记为[Marilyn Aronberg Lavin](../../../04-knowledge/units/persons/marilyn-aronberg-lavin.md)。S2候选记录注明印本姓氏为Lavin、OCR误作Lavili；卡片保留原OCR引句并记校读。出版物及清单未独立查阅，关系候选`st-chp2-seciv-l139-152-lavin-publishes-barberini-inventories`留待S6。
- `cand-0386`（`new-person:boncampagni-ugo-gregory-xiii-064b1bab8e`）依据第2、3章反复出现的Pope Gregory XIII／Gregory XIII指称登记为[Pope Gregory XIII](../../../04-knowledge/units/persons/pope-gregory-xiii.md)。第2章p.32注5将公共慈善引文归于该教宗，但转引链为Baglione、Orbaan，未独立核查；第3章p.67–68记述其与两项教会划拨相关的书内语境。关系候选`st-chp2-secii-l147-193-gregory-quotation-chain`保持为来源报告链，不升为经独立核实的事实。
- 两组各新增一个person KU与一条候选映射；两条直接S2关系候选继续待S6，不新增正式关系或外部身份核验状态。

The Lavin group follows the corrected print reading in the chapter 2 footnote and the chapter 20 postscript; the inventories were not independently consulted. Gregory XIII is named across chapters 2 and 3; the chapter 2 quotation remains a mediated Baglione/Orbaan source chain. Both direct relation candidates remain pending S6, with no formal relation or external verification status added.

S4 当前登记607组/754条候选映射；待登记4,187组/4,220条；KU总数1,626。

<a id="s4-person-julian-wals-gigli-20261017"></a>

### S4 person：三组跨章人物关系端点（2026-10-17）

- `cand-1336`（`new-person:apostate-julian-faf208b96a`）依据第4章p.109全名及第7章p.196对Verrio题材的再次提及登记为[Julian the Apostate](../../../04-knowledge/units/persons/julian-the-apostate.md)。关系候选`st-chp4-sec-ii-p109-petau-preface-argument`是Haskell对Petau序言的摘要，不视作已独立核对Petau原文。
- `cand-2800`（`new-person:goffredo-wals-e36dbf4df9`）依据第5章p.125全名及第8章p.206收藏名单异写登记为[Goffredo Wals](../../../04-knowledge/units/persons/goffredo-wals.md)。`Goffredo`与`Gioffredo`两种原书OCR形式均保留；`st-chp5-p125-claude-studied-under-wals`中的`is supposed to have`限定不转写为确定师承。
- `cand-1168`（`new-person:giacinto-gigli-cef75d311f`）依据第5章p.131叙述和书内索引G.csv L77登记为[Giacinto Gigli](../../../04-knowledge/units/persons/giacinto-gigli.md)。正文OCR作“Giacinto GigE”，书内索引列作“Gigli, Giacinto”；第6章注4再次引用Gigli。正文所述日记版本未独立查阅，OCR中“diEgently”与印本“diligently”的校读保留在证据摘要中。
- 三组各新增一个person KU与一条候选映射；3条直接S2关系候选仍待S6，本次不新增正式关系或外部身份核验状态。

The three groups follow the cross-chapter names and spellings recorded in the book. The Petau passage remains a mediated summary, the Wals apprenticeship remains qualified as reported, and the Gigli OCR form is compared with the book index. All three relation candidates remain pending S6; no formal relation or external identity verification was added.

S4 当前登记610组/757条候选映射；待登记4,184组/4,217条；KU总数1,629。

<a id="s4-person-spadaro-gustavus-berrettoni-20261017"></a>

### S4 person：三组跨章人物关系端点（2026-10-17）

- `cand-2495`（`new-person:micco-spadaro-2b56032967`）依据第5章p.139全名及第8章收藏注释中的重复全名登记为[Micco Spadaro](../../../04-knowledge/units/persons/micco-spadaro.md)。`st-chp5-notes-l126-165-l152-spadaro-workgroup-authorship`所指博物馆绘画群，与第5章正文的Cerquozzi《Masaniello起义》双场景画分立；第8章Codazzi作品中的人物提及另作语境记录。
- `cand-1284`（`new-person:adolphus-gustavus-of-sweden-e13b1682aa`）依据第6章p.160及第7章p.193关于Christina之父的跨章指称登记为[Gustavus Adolphus of Sweden](../../../04-knowledge/units/persons/gustavus-adolphus-sweden.md)。第6章OCR读作Adolfus，候选记录注明印本为Adolphus；第7章直接使用Adolphus。两章对布拉格藏品被劫事件的责任者表述均保留，关系候选`st-chp6-p160-gustavus-looted-collection-from-prague`不作独立历史验证。
- `cand-0367`（`new-person:berrettoni-niccolo-e92fe6e410`）依据第6章p.161注4姓氏及第7章p.191–192全名登记为[Niccolò Berrettoni](../../../04-knowledge/units/persons/niccolo-berrettoni.md)。第7章将其称为Maratta的学生；印本重音由S2页图记录，OCR不含重音。候选`st-chp7-p191-i13`仍待S6，不在卡片中登记正式师承边。
- 三组各新增一个person KU与一条候选映射；3条直接S2关系候选仍待S6，不新增正式关系或外部身份核验状态。

The Spadaro museum group remains distinct from the Masaniello double-scene picture. Gustavus Adolphus retains both source spellings and chapter attributions concerning the Prague collections. Berrettoni's pupil statement remains a relation candidate. All three candidates remain pending S6, with no formal relation or external identity verification added.

S4 当前登记613组/760条候选映射；待登记4,181组/4,214条；KU总数1,632。

<a id="s3-ferdinando-ii-reuse-20261017"></a>

### S3/S4复核：Ferdinando II de’ Medici 复用既有人物 KU（2026-10-17）

- `cand-1608`原判为`new-person:de-ferdinando-ii-medici-of-tuscany-86d09e74dc`。S4重复对象预检命中`units/persons/ferdinando-ii-de-medici`。M.csv#148索引完整写作“Medici, Ferdinando II de’, Grand Duke of Tuscany”；第7章p.178以Grand Duke of Tuscany出现，第20章p.403写Grand Duke Ferdinand II，现有人物卡正是Ferdinando II de’ Medici。索引姓名、头衔和跨章语境足以支持同一人物。
- 将`cand-1608`当前决定改为`same`并映射到既有KU；原new组留在`alignment.csv`理由中，不新建卡。`st-chp20-p403-campbell-ferdinand-ii-palazzo-pitti`记录的学术转述仍待S6逐条裁决。

<a id="s3-marco-pitteri-reuse-locator-review-20261017"></a>

### S3/S4复核：Marco Pitteri 复用既有人物 KU，页码定位待核（2026-10-17）

- `cand-1948`原判为`new-person:marco-pitteri-1a39ee76ea`。S4重复对象预检命中既有`units/persons/marco-pitteri`，其规范名为Marco Alvise Pitteri；该卡引用同一书的图版目录“Marco Pitteri”并已有Treccani身份记录。第9章p.200正文明确称engraver Marco Pitteri，第10章p.312与第13章p.335注2均在雕版语境称Pitteri，足以支持身份复用。
- 页码分歧单独保留：`entity-candidates.csv`所存索引范围为260、312、335n，S1原始P.csv#149记录260、312、222n，而第9章Markdown页标为200。未把p.200改写为p.260，也未改动原始索引或来源资产；该问题是定位待核，不据此新建第二个Pitteri。
- 将`cand-1948`当前决定改为`same` → `units/persons/marco-pitteri`，原new组与定位差异均留痕。直接关系候选`st-chp10-p312-pitteri-engraved-portraits-of`及`st-chp13-p335-note2-pitteri-engraved-design`待S6；不新建KU或正式关系。

Both groups were initially marked new. Accepted person cards and source names identify Ferdinando II de’ Medici and Marco Alvise Pitteri as the existing targets, so their current alignment rows now use `same`. For Pitteri, the S1 index range, raw index row, and chapter 9 page marker remain discrepant; the locator issue is retained without changing source records or creating a duplicate person. All three direct relation candidates remain pending S6.

<a id="s4-five-direct-endpoint-terms-20261017"></a>

### S4 term：五组直接关系端点登记（2026-10-17）

本批按待登记直接关系端点优先级登记五个已有 S3 `new` 单成员身份组。逐组裁决、来源引文、边界和逐条关系候选见对应知识卡。

- `cand-4131`（`sg3-term-cand-4131`）保持 S3 `new` 决定，映射至[意大利艺术术语卡](../../../04-knowledge/units/terms/italian-art.md)（`units/terms/italian-art`）。**对象边界：** 本卡是书内主题术语，不是地域实体、艺术家群体或艺术制度；它不等同于“意大利巴洛克”“意大利艺术赞助”或某一国别风格，也不把正文中所有意大利艺术家、作品及收藏活动自动视为同一关系。书前的“Art, Italian”仅作为原编目词形保留。 直接关系候选 11 条，全部留待 S6。
- `cand-8134`（`sg3-term-cand-8134`）保持 S3 `new` 决定，映射至[新近获准进入威尼斯贵族阶层的家族术语卡](../../../04-knowledge/units/terms/new-families-admitted-venetian-nobility.md)（`units/terms/new-families-admitted-venetian-nobility`）。**对象边界：** 此术语不指某个具名家族，也不把所有较晚进入贵族阶层的家庭合并成一个组织。它与原有的 Venetian nobility social estate 术语卡范围不同；不能据此推定每个新贵族家族的财富、政治行为、收藏实践或统一身份。第9章的社会评价和因果解释均保留为哈斯克尔的论述。 直接关系候选 8 条，全部留待 S6。
- `cand-3396`（`sg3-term-cand-3396`）保持 S3 `new` 决定，映射至[反宗教改革术语卡](../../../04-knowledge/units/terms/counter-reformation.md)（`units/terms/counter-reformation`）。**对象边界：** 本卡保存哈斯克尔的用词及其叙述，不是天主教会机构卡，不等同于耶稣会或其他修会，也不提供该术语在学界的穷尽定义或统一分期。p.271 关于“延续至18世纪”的判断明确作为作者表述保留。 直接关系候选 8 条，全部留待 S6。
- `cand-2068`（`sg3-term-cand-2068`）保持 S3 `new` 决定，映射至[威尼斯出版商群体术语卡](../../../04-knowledge/units/terms/publishers-in-venice.md)（`units/terms/publishers-in-venice`）。**对象边界：** 本卡不是威尼斯正式出版行会或机构，也不是所有书商、印刷工和版画家的合并名单。出版商可兼任书商、收藏者或赞助人，但这些角色须按具体人物和原书证据分别记录；本卡不把群体层面的概述推及每一位出版者。 直接关系候选 8 条，全部留待 S6。
- `cand-11543`（`sg3-term-cand-11543`）保持 S3 `new` 决定，映射至[哈斯克尔所述的威尼斯艺术传统术语卡](../../../04-knowledge/units/terms/venetian-art-tradition-haskell-account.md)（`units/terms/venetian-art-tradition-haskell-account`）。**对象边界：** 本卡不把“威尼斯艺术传统”设为正式学科分类、机构、家族或一组成员固定的画家组织，也不据“最后一位伟大大师”等评价推导客观终结年代或连续谱系。它与 Venice 地点卡及具体的威尼斯艺术家、作品和收藏活动分开；后续关系仍须逐条依据对应证据裁决。 直接关系候选 8 条，全部留待 S6。

五组各登记一个 term KU，并将唯一成员候选映射至该卡；候选决定保持 `new`，未改动 S3 分组或身份判断。五组共 43 条直接 S2 关系候选仍待 S6；没有新增正式关系、外部术语验证或 S5 enrichment。

S4累计登记618组/765条候选映射；待登记4,174组/4,207条；KU总数1,637。

<a id="s4-two-direct-endpoint-terms-20261017"></a>

### S4 term：两组直接关系端点登记（2026-10-17）

两组均为单成员 S3 `new` 术语组，来源引文与候选映射记录在卡片和 `alignment.csv` 中：

- `cand-9985`（`sg3-term-cand-9985`）保持 S3 `new`，登记为[纪念贵族典礼的诗歌与颂诗集术语卡](../../../04-knowledge/units/terms/poem-eulogy-collections-noble-ceremonies.md)（`units/terms/poem-eulogy-collections-noble-ceremonies`）。**对象边界：** 本卡只登记类别本身，不代表每一部纪念集都有插图、相同格式或相同受众。p.334 所述花费一千杜卡特的匿名贵族个案，不因此成为本卡所指的单一对象；未具名的具体纪念集候选 `cand-12135` 保持独立 archive 身份决定，不与此 term 合并。 7 条直接关系候选留待 S6。
- `cand-6554`（`sg3-term-cand-6554`）保持 S3 `new`，登记为[哈斯克尔所述奥托博尼影响下的艺术风格术语卡](../../../04-knowledge/units/terms/ottoboni-influence-style-haskell-account.md)（`units/terms/ottoboni-influence-style-haskell-account`）。**对象边界：** 这不是 Ottoboni 赞助的全部艺术风格，也不是具有已知成员名册的画派。哈斯克尔的比较语句不等于每位受其赞助的画家都呈现相同风格；“true Baroque”、法国洛可可和后期18世纪绘画是原文中的对照项，保持各自候选及关系裁决，不并入本卡。 7 条直接关系候选留待 S6。

合计登记2个 term KU 与2条候选映射。两组共14条直接 S2 关系候选仍待 S6；本次未新增正式关系、外部术语验证或 S5 enrichment。

S4累计登记620组/767条候选映射；待登记4,172组/4,205条；KU总数1,639。

<a id="s4-five-direct-endpoint-works-20261017"></a>

### S4 work：五组直接关系端点登记（2026-10-17）

本批登记五个已有 S3 `new` work 身份组；每组一个 KU，所有直接关系候选保持待 S6：

- `cand-6676`（`workgrp-b1a186cf103e3c`）保持 S3 `new`，登记为[马里·德·美第奇推动委托的亨利四世骑马像作品卡](../../../04-knowledge/units/works/henri-iv-equestrian-statue-marie-de-medici-commission.md)（`units/works/henri-iv-equestrian-statue-marie-de-medici-commission`）。**身份边界：** 本卡对应为 Henri IV 制作的纪念像。叙述同时提到 Marie 曾请求斐迪南将为自己制作的骑马像转交给她，该请求未获准；该自用骑马像与本卡对象分别处理。Pont Neuf 是原文所述的计划安置地，不据此补写安装史或后续流传。 6 条直接关系候选留待 S6。
- `cand-10554`（`workgrp-a758d643d80f43`）保持 S3 `new`，登记为[阿尔蒂奇耶罗园林的神龛与雕塑配置作品卡](../../../04-knowledge/units/works/alticchiero-garden-shrines-sculpture-programme.md)（`units/works/alticchiero-garden-shrines-sculpture-programme`）。**对象边界：** 本卡记录园林中的群组性装饰配置，不是阿尔蒂奇耶罗庄园本身，也不是一件单独雕塑或完整馆藏清单。原文分别具名的祭坛、雕塑和纪念像仍可由各自候选承接；群组与园林地点、单件作品之间的正式关系留待 S6。 6 条直接关系候选留待 S6。
- `cand-5272`（`workgrp-5ea1e2fb75fd5a`）保持 S3 `new`，登记为[盖乌利耶稣堂中殿壁画作品卡](../../../04-knowledge/units/works/gaulli-gesu-nave-fresco.md)（`units/works/gaulli-gesu-nave-fresco`）。**与既有项目卡的关系：** 既有[Gaulli 耶稣堂拱顶壁画工程卡](gaulli-gesu-vaults.md)记录中殿及横翼拱顶工程整体；本卡限定为第3章 p.83 所指的中殿单幅壁画。它与该较广工程、穹顶及祭坛区方案的组成关系留待 S6 逐条裁决，本次不建立正式 `part_of` 边。 6 条直接关系候选留待 S6。
- `cand-10013`（`workgrp-48c8f5fcc77fe0`）保持 S3 `new`，登记为[诺韦利为帕斯夸利版戈尔多尼作品所作插图系列作品卡](../../../04-knowledge/units/works/novelli-goldoni-pasquali-illustration-programme.md)（`units/works/novelli-goldoni-pasquali-illustration-programme`）。**与单件作品的区别：** 已有[第二卷卷首图卡](pietro-antonio-novelli-frontispiece-to-vol-2-of-goldoni-opere.md)对应图版57b这一件具体图像；本卡对应逾百幅图稿及其系列方案，二者保持不同对象粒度。未逐一确认的卷首图、版画家和作品成员不补入名单；系列与第二卷单幅图之间的正式组成关系留待 S6。 6 条直接关系候选留待 S6。
- `cand-10586`（`workgrp-32819d9dcd5818`）保持 S3 `new`，登记为[奎里尼委托卡诺瓦制作的保罗·雷尼耶胸像作品卡](../../../04-knowledge/units/works/canova-bust-paolo-renier-querini-commission.md)（`units/works/canova-bust-paolo-renier-querini-commission`）。**待证内容：** p.372 注1以“what must be the bust”表述对帕多瓦陶土胸像的推定，并说曾有人提出它被置于仆役盥洗处。此处只作为 Haskell 转述的注释及未证身份线索保留，不把馆藏归属、作品保存状态或传闻当作已核事实；本次不建立作品现存地关系。 6 条直接关系候选留待 S6。

五组新增5个 work KU 与5条候选映射，合计30条直接 S2 关系候选仍待 S6；未新增正式关系、外部作品身份核验或 S5 enrichment。

S4累计登记625组/772条候选映射；待登记4,167组/4,200条；KU总数1,644。

<a id="s4-three-direct-endpoint-terms-20261017"></a>

### S4 term：三组直接关系端点登记（2026-10-17）

本批登记三个已有 S3 `new` 术语组，其中 English patronage 组含两条同组候选；同组候选共同映射至一个 KU。来源范围、类型边界和待证关系见对应卡片：

- `cand-0969`、`cand-0970`（`sg3-term-englishpatronage`）保持同一 S3 `new` term 组，映射至[英国对意大利艺术的赞助术语卡](../../../04-knowledge/units/terms/english-patronage-of-italian-art.md)（`units/terms/english-patronage-of-italian-art`）。**对象边界：** 本卡是哈斯克尔第7章所述的国别性赞助主题，不是机构、赞助人名单或所有英国人在意大利的活动汇总。它比既有一般术语 `Art patronage` 范围具体；“English tourists in Italy”候选 `cand-0973` 独立记录旅行者群体，不并入本卡。哈斯克尔关于王室赞助与游客影响的比较保留为作者判断。 6 条直接关系候选留待 S6。
- `cand-4672`（`sg3-term-cand-4672`）保持同一 S3 `new` term 组，映射至[萨基《神圣智慧》中的智慧人格化概念术语卡](../../../04-knowledge/units/terms/wisdom-personified-sacchi-divine-wisdom.md)（`units/terms/wisdom-personified-sacchi-divine-wisdom`）。**对象边界：** 本卡与候选“Divine Wisdom”所指的壁画作品分开，也与《所罗门智训》这部文本分开。它不把基督教神学中的一切智慧概念合并到此条书内解释，也不独立裁决该图像解释的神学效力；相关作品、文本及人物关系仍按各自候选待 S6。 6 条直接关系候选留待 S6。
- `cand-4686`（`sg3-term-cand-4686`）保持同一 S3 `new` term 组，映射至[布拉奇奥利尼为巴贝里尼大礼堂设计的图像纲领术语卡](../../../04-knowledge/units/terms/bracciolini-barberini-ceiling-iconographic-programme.md)（`units/terms/bracciolini-barberini-ceiling-iconographic-programme`）。**对象边界：** 本卡的 `term` 类型表示一项可识别的图像纲领概念，而非独立档案文献或单件作品。巴贝里尼大礼堂穹顶壁画本体仍按 work 候选处理；二者的正式 `depicts`、`realized_as` 或组成关系留待 S6，不在本次登记中建立。 6 条直接关系候选留待 S6。

三组登记3个 term KU 与4条候选映射。共18条直接 S2 关系候选继续待 S6；本次未新增正式关系、外部术语验证或 S5 enrichment。

S4累计登记628组/776条候选映射；待登记4,164组/4,196条；KU总数1,647。

<a id="s4-english-tourists-italy-term-20261017"></a>

### S4 term：英国游客身份组登记（2026-10-17）

`cand-0973`（`sg3-term-cand-0973`）保持单一 S3 `new` term 组，映射至[17世纪后半赴意大利的英国旅行者术语卡](../../../04-knowledge/units/terms/english-tourists-italy-late-seventeenth-century.md)（`units/terms/english-tourists-italy-late-seventeenth-century`）。该组与英国对意大利艺术赞助术语分开；游客多数、因公务留意大利者和后文的重要收藏者按原书语境区分。6条直接 S2 关系候选留待 S6；本次未新增正式关系、外部身份验证或 S5 enrichment。

S4累计登记629组/777条候选映射；待登记4,163组/4,195条；KU总数1,648。

<a id="s4-two-direct-endpoint-terms-20261017-batch2"></a>

### S4 term：两组直接关系端点登记（2026-10-17）

本批登记两个已有 S3 `new` term 组。候选成员各自映射一个 KU；来源定位、语境和边界见对应卡片：

- `cand-0680`（`sg3-term-cand-0680`）保持 S3 `new` term 组，映射至[哈斯克尔所述罗马宗教修会的教堂术语卡](../../../04-knowledge/units/terms/churches-of-religious-orders-in-rome-haskell-account.md)（`units/terms/churches-of-religious-orders-in-rome-haskell-account`）。**对象边界：** 本卡是书内的类别性术语，不是修会、单一教堂或统一工程。Gesù、S. Ignazio、S. Andrea della Valle、Chiesa Nuova 等可辨认建筑仍各属 place 身份；本卡不替代这些对象，也不据类别表述新建教堂之间的正式关系。它与既有术语“宗教修会的艺术赞助”（`units/terms/patronage-by-religious-orders`）相关但不相同：本卡关注教堂类别及其营建、装饰语境。 6 条直接关系候选留待 S6。
- `cand-11845`（`sg3-term-cand-11845`）保持 S3 `new` term 组，映射至[因赞助与发展机会聚集罗马的画家群体术语卡](../../../04-knowledge/units/terms/artists-drawn-to-rome-by-patronage-and-prospects.md)（`units/terms/artists-drawn-to-rome-by-patronage-and-prospects`）。**对象边界：** 本卡记录哈斯克尔在特定历史论述中划定的群体，不是正式团体、单一迁徙事件或罗马城市本身。未具名的群体判断不自动识别各成员；可识别画家仍按 person 身份分别登记。它与罗马 place 身份及一般的艺术赞助术语相区分，不把“发展机会”扩展为所有艺术家的共同动机。 6 条直接关系候选留待 S6。

两组登记2个 term KU 与2条候选映射。共12条直接 S2 关系候选继续待 S6；本次未新增正式关系、外部身份验证或 S5 enrichment。

S4累计登记631组/779条候选映射；待登记4,161组/4,193条；KU总数1,650。

<a id="s4-indecency-erotic-term-20261017"></a>

### S4 term：跨章索引主题登记（2026-10-17）

`cand-1313`（`sg3-term-cand-1313`）保持 S3 `new` term 组，映射至[哈斯克尔索引中的不雅与艳情主题术语卡](../../../04-knowledge/units/terms/indecency-and-erotic-in-haskell-index.md)（`units/terms/indecency-and-erotic-in-haskell-index`）。该身份按索引的主题性汇集登记；第7章的裸体画讨论与第17章的 Manfrin 竞赛保留各自语境，不据此构造统一流派或历史态度。

6条直接 S2 关系候选（`st-chp7-p194-german-princely-taste-variation`、`st-chp7-p194-nudes-expected`、`st-chp7-p195-cignani-testimony`、`st-chp7-p195-female-nude-historical-role`、`st-chp7-p195-german-patron-generalization`、`st-chp7-p195-lazzarini-testimony`）继续待 S6。本次未新增正式关系、外部身份验证或 S5 enrichment。

S4累计登记632组/780条候选映射；待登记4,160组/4,192条；KU总数1,651。

<a id="s4-two-direct-endpoint-events-20261017"></a>

### S4 event：两组直接关系端点登记（2026-10-17）

本批登记两个已有 S3 `new` event 组；日期、来源归属与对象边界见对应卡片：

- `cand-4780`（`sg3-event-cand-4780`）保持 S3 `new` event 组，映射至[巴贝里尼宫最初的歌剧演出（哈斯克尔纪为1632年2月）事件卡](../../../04-knowledge/units/events/first-operatic-performances-barberini-palace-1632.md)（`units/events/first-operatic-performances-barberini-palace-1632`）。**身份边界：** 本卡是宫内演出事件组，不是剧场建筑或某一部歌剧作品；演出参与者、剧目与相关人员仍按各自候选处理。正文称“最初”演出，范围限于巴贝里尼宫的叙述语境。日期采用哈斯克尔在注3中的裁决，同时保留其列出的史料分歧，不扩展为独立验证结论。 6条直接关系候选留待 S6。
- `cand-4767`（`sg3-event-cand-4767`）保持 S3 `new` event 组，映射至[卡迪纳尔安东尼奥在纳沃纳广场组织的中世纪式骑士比武（1634）事件卡](../../../04-knowledge/units/events/cardinal-antonio-medieval-joust-piazza-navona-1634.md)（`units/events/cardinal-antonio-medieval-joust-piazza-navona-1634`）。**身份边界：** 本卡记录一次比武事件，不是 Sacchi 的绘画作品、Bentivoglio 的书或巴贝里尼家族整体复兴骑士传统的抽象概念。相关人物、作品、家族与地点仍各按其候选身份审查；本次不因同一叙述建立正式关系。 6条直接关系候选留待 S6。

两组登记2个 event KU 与2条候选映射。共12条直接 S2 关系候选继续待 S6；本次未新增正式关系、外部事件验证或 S5 enrichment。

S4累计登记634组/782条候选映射；待登记4,158组/4,190条；KU总数1,653。

<a id="s4-bergamo-santa-maria-maggiore-place-20261017"></a>

### S4 place：贝加莫圣母玛利亚教堂登记（2026-10-17）

`cand-7627`（`sg3-place-cand-7627`）保持 S3 `new` place 组，映射至[贝加莫的圣母玛利亚教堂地点卡](../../../04-knowledge/units/places/santa-maria-maggiore-bergamo.md)（`units/places/santa-maria-maggiore-bergamo`）。来源将该教堂与贝加莫城市及内部空间、建筑构件、祭坛画区分；6条直接 S2 关系候选继续待 S6，本次不建立正式边或 S5 enrichment。

S4累计登记635组/783条候选映射；待登记4,157组/4,189条；KU总数1,654。

<a id="s4-pieta-venice-place-20261017"></a>

### S4 place：威尼斯 Pietà 教堂登记（2026-10-17）

`cand-8551`（`sg3-place-cand-8551`）保持 S3 `new` place 组，映射至[哈斯克尔所称威尼斯“Pietà”教堂地点卡](../../../04-knowledge/units/places/church-of-the-pieta-venice-haskell-account.md)（`units/places/church-of-the-pieta-venice-haskell-account`）。卡片保留哈斯克尔来源命名，与同址早期收容所、穹顶及壁画作品分开；6条直接 S2 关系候选继续待 S6，本次不建立正式边或 S5 enrichment。

S4累计登记636组/784条候选映射；待登记4,156组/4,188条；KU总数1,655。

<a id="s4-memmo-query-sheet-20261017"></a>

### S4 archive：Andrea Memmo《画家地位札记》文献身份组登记（2026-10-17）

- cand-9857 保持 S3 new 组 archive-group-c9f891c0a384，登记为[安德烈亚·梅莫《画家地位札记》](../../../04-knowledge/units/archives/andrea-memmo-notes-status-painters.md)（units/archives/andrea-memmo-notes-status-painters）。本卡只记录附录6所题的单张便笺；该标题不被当作原件题名。它与 Memmo 人物、《Elementi dell’architettura lodoliana》及 Petizion 488 财物清单分别处理。
- Haskell 第10章 p.330称该便笺记有准备行会重组报告时提出的问题，注1称全文刊于附录6；附录 p.394给出威尼斯国家档案馆的定位，并将成文时间列为就任前约两至三年，保留为作者估计。原件、馆藏目录及所述日期未独立核验。
- 直接 S2 关系候选共4条（st-chp10-p330-n01-memmo-sheet-appendix, st-chp19-p394-memmo-sheet-source-and-date, st-chp19-p395-memmo-note-marks-life-of-montorsoli-read, st-chp10-p330-memmo-preparatory-sheet），全部留待 S6；本批未新增正式关系、外部身份验证或 S5 enrichment。

S4 当前已登记637组/785条成员映射，尚待登记4,155组/4,187条。

<a id="s4-dactylografa-smithiana-20261017"></a>

### S4 archive：Dactylografa Smithiana 插图书登记（2026-10-17）

- cand-1848 与 cand-2458 保持同一 S3 new 身份组 archive-group-dactylografia-smithiana，共同映射至[约瑟夫·史密斯奖章与宝石图册](../../../04-knowledge/units/archives/dactylografa-smithiana.md)（units/archives/dactylografa-smithiana）。正文题名为 Dactylografa Smithiana，两条索引子目写作 Dactylografia Smithiana；异文并存，不据此拆分对象。
- Haskell 称此书在1749年相关插图书之后十八年出版，含 Brustolon 刻制的100幅版画，表现 Joseph Smith 的奖章与宝石；仅用拉丁语，面向较学术的读者。版年不从相对时间换算，本书及题名页未查阅。与既有1749年 Zanetti 图录分开。
- 共7条直接 S2 陈述，其中6条关系候选（st-chp13-p337-dactylografa-contained-100-brustolon-plates, st-chp13-p337-dactylografa-illustrated-smith-medals-gems, st-chp13-p337-dactylografa-influenced-by-albrizzi-zanetti-publication, st-chp13-p337-dactylografa-latin-only-scholarly-audience, st-chp13-p337-dactylografa-simpler-presentation-than-albrizzi-book, st-chp13-p337-pasquali-published-dactylografa-smithiana）全部留待 S6；本批未新增正式关系、外部身份验证或 S5 enrichment。

S4 当前已登记638组/787条成员映射，尚待登记4,154组/4,185条。

<a id="s3-levi-inventory-publication-merge-20261017"></a>

### S3 archive：C. A. Levi 1900 年出版物跨章并组（2026-10-17）

- cand-8533 原列为 archive-group-b3cea361eaf4，cand-11374 列为 archive-group-5b4568c2a1c8。复核后保留两者的 new 决定，统一进入 archive-group-5b4568c2a1c8；该组含这两条候选。
- 身份依据：第9章 p.261 注2称18世纪威尼斯库存清单收录于 C. A. Levi 的1900年汇编；第15章 p.368 注3及 p.370 注1分别引 Levi 第二卷 p.254、p.255；第19章 p.391称 Petizion 467 档案所载清单由 Levi 第二卷 pp.236–248 重刊；第21章 p.427书目给出 *Le Collezioni Veneziane d’arte e d’antichità dal secolo XIV ai nostri giorni*，Venezia 1900。题名、出版地、年份和卷次相合，支持这是同一多卷本出版物，不是各项清单或底层档案本身。
- 原分组 archive-group-b3cea361eaf4 与原 new 理由保留在 cand-8533 的 alignment 注释中；仅修正身份组，不改候选数或决定类型。Levi 卷I短引 cand-10659、cand-10732 仍为 undecided；未具名清单群 cand-8531、作者 initials 人物 cand-8532、Petizion 467 清单 cand-10806 及 Querini 清单 cand-10567 保持各自身份与状态。
- 5 条直接关系候选仍待 S6；未新增外部身份记录、KU 或正式关系。

当前 S3 为 new=4,972（4,791组）；S4 已登记638组/787条映射，待登记4,153组/4,185条。

<a id="s4-levi-1900-publication-20261017"></a>

### S4 archive：Levi 1900 年《威尼斯艺术与古物收藏》登记（2026-10-17）

- cand-8533 与 cand-11374 保持同一 S3 new 组 archive-group-5b4568c2a1c8，共同映射至[《从十四世纪至今的威尼斯艺术与古物收藏》](../../../04-knowledge/units/archives/le-collezioni-veneziane-1900.md)（units/archives/le-collezioni-veneziane-1900）。书目原题为 Le Collezioni Veneziane d’arte e d’antichità dal secolo XIV ai nostri giorni，第21章列 Venezia 1900；中文与英文展示题名均为描述性工作译名。
- 第9章称该1900年出版物收入若干18世纪威尼斯库存清单；第15章引其第二卷 p.254、p.255，第19章引第二卷 pp.236–248。正文卷页定位与书目题名、年份支持跨章身份并组；出版物及被引页未独立查阅。
- 共6条直接 S2 陈述，其中5条关系候选（st-chp9-p261-note2-levi-inventory-collection, st-chp15-p368-note3-cites-levi-volume-ii-p254, st-chp15-p368-note3-inventory-partly-published-in-levi, st-chp15-p370-note1-cites-levi-volume-ii-p255, st-chp15-p370-note1-inventory-published-in-levi）全部留待 S6。原档案清单、未具名库存清单群、C. A. Levi 人物与卷I短引保持独立；本批未新增正式关系、外部身份验证或 S5 enrichment。

S4 当前已登记639组/789条成员映射，尚待登记4,152组/4,183条。

<a id="s4-person-guarino-guarini-20261017"></a>

### S4 person：Guarino Guarini 跨章身份组登记（2026-10-17）

- cand-6876 保持 S3 new 组 new-person:guarini-guarino-bdced3f938，映射至[瓜里诺·瓜里尼（Guarino Guarini）人物卡](../../../04-knowledge/units/persons/guarino-guarini.md)（units/persons/guarino-guarini）。第7章 p.186 与 p.193 均明载同一全名，候选分组保留单一人物；本次仅据书内全名登记，不作外部身份或生平核验。
- p.186 称 Theatines 召来本会成员 Guarini，记其1662年抵达、开始圣安娜—皇家教堂工程，工程1669年中断并约五十年后完成；p.193 称 Adelaide Enrichetta 未能吸引 Guarini，未详邀请条件或时间。工程完成时间保持约数。
- 3 条直接关系候选（{', '.join(RELATION_IDS)}）全部留待 S6。cand-2564 Theatines 已映射 units/institutions/theatines；cand-6875 圣安娜—皇家教堂与 cand-2380 Adelaide Enrichetta 各自保持 S3 new、待 S4；本次不建立正式关系。

S4 当前已登记640组/790条成员映射，尚待登记4,151组/4,182条。

<a id="s4-person-giuseppe-valeriani-crosschapter-20261017"></a>

### S4 person：Giuseppe Valeriani 跨章身份组登记（2026-10-17）

- cand-9382 保持 S3 new 组 new-person:giuseppe-valeriani-196d624a19，映射至[朱塞佩·瓦莱里亚尼（Giuseppe Valeriani）人物卡](../../../04-knowledge/units/persons/giuseppe-valeriani.md)（units/persons/giuseppe-valeriani）。第10章 p.289 注1表和第20章 p.406 后记均以同一全名指名；候选组按现有 S3 身份决定登记，不作外部人物核验。
- 第10章表格把他列为参与相关纪念碑项目的威尼斯艺术家，在 William III、Isaac Newton 两行出现；没有说明其个人创作、执行或委托角色。第20章称1948年有一部关于 Giuseppe Valeriani 的资料详尽著作研究俄国宫廷对威尼斯艺术家的兴趣；该书未独立查阅。
- 3 条直接关系候选（{', '.join(RELATION_IDS)}）全部留待 S6。索引合并候选 cand-2679 维持 excluded；Domenico Valeriani cand-9381 为独立 new 人物组；William III、Isaac Newton 纪念碑候选 cand-9387、cand-9375 维持 undecided；相关1948年著作 cand-11088 为独立 archive new 组，待 S4。

S4 当前已登记641组/791条成员映射，尚待登记4,150组/4,181条。

<a id="s4-person-girolamo-colonna-crosschapter-20261017"></a>

### S4 person：Girolamo Colonna 跨章身份组登记（2026-10-17）

- cand-0809 保持 S3 new 组 new-person:colonna-girolamo-4252615c6d，映射至[吉罗拉莫·科隆纳（Girolamo Colonna）人物卡](../../../04-knowledge/units/persons/girolamo-colonna.md)（units/persons/girolamo-colonna）。第6章 p.155 称 Cardinal Girolamo，第7章 p.180 写出全名 Girolamo Colonna；两处共同支持同一书内人物组，未作外部核验。
- 第6章称 Filippo 与其子 Cardinal Girolamo 参与 Colonna 家族宫殿重建、装饰，但没有区分个人贡献；此处父子措辞尚无单独 S2 statement ID，保留为 S6 回读核查项。cand-0806 Filippo Colonna 独立保持 S3 new、待 S4。
- 两条直接关系候选（st-chp6-p155-colonna-palace-decorated-by-girolamo, st-chp7-p180-i07）留待 S6。宫殿 cand-0815 已登记；Mazarin cand-1588 与 Spain cand-5120 已指向既有 KU；本批没有登记正式关系。

S4 当前已登记642组/792条成员映射，尚待登记4,149组/4,180条。

<a id="s4-person-philip-skippon-crosschapter-20261017"></a>

### S4 person：Philip Skippon 跨章身份组登记（2026-10-17）

- cand-2438 保持 S3 new 组 new-person:philip-skippon-3ee8383fd8，映射至[菲利普·斯基彭（Philip Skippon）人物卡](../../../04-knowledge/units/persons/philip-skippon.md)（units/persons/philip-skippon）。索引 S.csv#127 给出倒置全名与 p.104 注定位；第4章 p.104、第6章 p.160及第4章导言的提及均保留原书语境，未作外部人物核验。
- 第4章 p.104 注3称 Skippon 于1663年由 Cassiano 未具名的侄子带看藏品，记有许多鸟类绘画；Haskell明确说他未记录这些画是否为 Poussin，且未指认单件作品。导言注1的 him 指 Ghibbesio，不构成 Skippon 的历史关系。
- 两条直接关系候选（st-chp4-sec-ii-p104-footnote3-skippon-noted-bird-paintings, st-chp4-sec-ii-p104-footnote3-skippon-shown-collection）留待 S6；未具名侄子、单件绘画身份及 Poussin 归属均保持未决。本批未登记正式关系或外部身份核验。

S4 当前已登记643组/793条成员映射，尚待登记4,148组/4,179条。

<a id="s3-s4-valeriani-1948-publication-reconciliation-20261017"></a>

### S3 archive：1948 年 Giuseppe Valeriani 著作跨章并组与脚注校正（2026-10-17）

- cand-11088 原属 archive-group-8a548cd83811，cand-11204 原属 archive-group-09a3b2fdbd56；两者均保持 S3 new，现统一进入 archive-group-09a3b2fdbd56，作为一个待 S4 登记的 archive 身份组。旧组号、原裁决理由及本次合组依据均保留在 alignment 注释。
- 第20章 p.406 正文称一部1948年、资料详尽的 Giuseppe Valeriani 著作；紧随该句的注号7指向同页注释“Konopleva”。第21章 p.426 书目列 M. S. Konopleva、Teatralni Zhivopicets Giuseppe Valeriani、Leningrad 1948。注号与完整书目题名、年份及被研究人物相互吻合，支持正文候选与书目候选是同一出版物；未独立查阅该书。
- 顺带更正 st-chp20-p406-n07-citation 的 S2 claim：原称注7引用“后续论文”，但正文明确将注号7附于1948年著作，后续两篇论文标注注号8，注释列为“Ernst; Fomiciova”。现记录注7对应正文所述书籍；关系候选状态仍为 false，仅作为书目引用事实。作者全名未得，人物候选 cand-11203 保持 undecided；两篇后续论文候选 cand-11089 也保持 undecided。
- 相关实体边界：人物 cand-9382 已映射 units/persons/giuseppe-valeriani；18世纪俄罗斯宫廷 cand-11087 与出版地 Leningrad cand-5796 保持各自 S3 new、待 S4，不并入文献卡；合并索引标题 cand-2679 仍 excluded。

S3 new 候选4,972，身份组4,790；S4 当前登记643组/793条映射，待登记4,147组/4,179条。

<a id="s4-valeriani-1948-book-20261017"></a>

### S4 archive：1948 年 Giuseppe Valeriani 著作登记（2026-10-17）

- 同一 S3 new 身份组 archive-group-09a3b2fdbd56 的 cand-11088（第20章 p.406 正文）和 cand-11204（注7及第21章 p.426 书目）共同映射至 [舞台画家朱塞佩·瓦莱里亚尼](../../../04-knowledge/units/archives/teatralni-zhivopicets-giuseppe-valeriani-1948.md)（units/archives/teatralni-zhivopicets-giuseppe-valeriani-1948）；2条候选映射对应1个 archive KU。原题、作者著录、出版地与年份均按 Haskell 书内书目记录，书未独立查阅。
- 中文与英文名称为描述性工作译名。作者保留为书目所载 M. S. Konopleva，不扩写身份。正文关于此书研究俄国宫廷吸引威尼斯艺术家的兴趣，是直接关系候选，留待 S6；注7和书目条目只作身份依据，不另建关系。
- 作者候选 cand-11203 与注8两篇文章 cand-11089 仍 undecided；俄罗斯宫廷 cand-11087 与出版地 cand-5796 保持各自 S3 new、待 S4；Valeriani 人物 cand-9382 已有 KU；索引标题 cand-2679 仍 excluded。以上均未并入本书卡。

S4 累计登记644组/795条候选映射；待登记4,146组/4,177条；KU 总数1,663。


<a id="s4-andrea-brustolon-person-20261017"></a>

### S4 person：Andrea Brustolon 登记（2026-10-17）

- cand-0463 保持 S3 new 组 new-person:andrea-brustolon-fc71fb65c2，映射至 [安德烈亚·布鲁斯托隆](../../../04-knowledge/units/persons/andrea-brustolon.md)（units/persons/andrea-brustolon）。Haskell 索引以 Brustolon, Andrea 为主项并指向 p.337、p.340；两页正文均以 Brustolon 指称雕刻者。身份限于书内索引与正文锚点，不添加外部生平或标识。
- 第13章称《Dactylografa Smithiana》有100幅由 Brustolon 雕刻的图版，并称特定 Perseus 与 Medusa 尾页图由他依据 Pietro Antonio Novelli 图稿雕刻；对 Canaletto 仪式图稿的雕刻仅记为计划。3条直接关系候选留待 S6，未添加正式关系。

S4 累计登记645组/796条候选映射；待登记4,145组/4,176条；KU 总数1,664。

<a id="s4-peterborough-3rd-earl-20261017"></a>

### S4 person：Peterborough 第三代伯爵登记（2026-10-17）

- cand-1891 保持 S3 new 组 new-person:3rd-of-peterborough-37b576d7e2，映射至 [彼得伯勒第三代伯爵](../../../04-knowledge/units/persons/3rd-earl-of-peterborough.md)（units/persons/3rd-earl-of-peterborough）。P.csv#92 列“Peterborough, 3rd Earl of”，第7章 p.200 注1也称第三代伯爵，故按书内标题登记人物；来源没有个人姓名，S3 旧说明中的“full personal name”措辞已在 alignment 附注中校正。
- 注1试探地提出正文 Admiral “Pekemburgh” cand-7285 可能是该伯爵；cand-7285 仍为 S3 undecided，不与本卡合并。OCR 的 tbe/ofPeterborough 校正依据记录在 S2（PDF物理页38），不影响身份裁决。4条直接关系候选留待 S6；原引述中的行程和委托均保留在可能识别语境中。

S4 累计登记646组/797条候选映射；待登记4,144组/4,175条；KU 总数1,665。

<a id="s4-pietro-rotari-person-20261017"></a>

### S4 person：Pietro Rotari 登记（2026-10-17）

- cand-2288 保持 S3 new 组 new-person:pietro-rotari-9ec7a16898，映射至 [彼得罗·罗塔里](../../../04-knowledge/units/persons/pietro-rotari.md)（units/persons/pietro-rotari）。Q-R.csv#216 将 “Rotari, Pietro” 指向第295页注3及第297页正文；两处全名和索引页码相互吻合。
- 第295页“left at this time”不折算为年份，也不与第297页1756年赴 St Petersburg 的叙述调和；注3所引 Bellotto 图录未独立查阅。未识别的数百幅画作 cand-9152 保持 undecided，St Petersburg cand-2343 保持 S3 new、待 S4。3条直接关系候选留待 S6。

S4 累计登记647组/798条候选映射；待登记4,143组/4,174条；KU 总数1,666。

<a id="s4-place-st-petersburg-20261017"></a>

### S4 place：St Petersburg 城市地点登记（2026-10-17）

- cand-2343 保持 S3 new 组 sg3-place-cand-2343，映射至 [圣彼得堡](../../../04-knowledge/units/places/st-petersburg.md)（units/places/st-petersburg）。索引 S.csv#31 将“St Petersburg, Venetian artists in”指向第297–298页，正文提供 Rotari、Bellotto 计划及《克娄巴特拉宴会》转移的来源锚点。按城市地点登记，不与俄罗斯政治实体或机构合并。
- Bellotto 前往该地仅为计划；Haskell 关于画作转移与欧洲力量变化的解释保持为作者解释。3条直接关系候选留待 S6，未添加正式关系。Rotari 人物 cand-2288 已登记；未识别绘画 cand-9152 仍 undecided。

S4 累计登记648组/799条候选映射；待登记4,142组/4,173条；KU 总数1,667。

<a id="s3-verona-cross-chapter-place-merge-20261017"></a>

### S3 place：Verona 跨章身份组并合（2026-10-17）

- cand-7661 原属 sg3-place-cand-7661，cand-8681 原属 sg3-place-cand-8681；两者保持 S3 new，现归入 sg3-place-cand-8681 一个 place 身份组，两个候选在 S4 共用一个 KU。旧组号和裁决理由保留在 alignment 注释。
- 语义依据：第8章 p.216 将 Brusasorci 称为 “Veronese”，对应 statement 的限定明确将地域形容词连到 Verona；第9章 p.268 明称 “Cignaroli in Verona”。此外，S2 已用 cand-8681 记录 p.297 Rotari 的 native Verona、p.311 Schulenburg 在 Verona 的叙述及 p.327 书籍在 Verona 出版；第14章 p.348 也将 Verona 列入行程。以上是同一城市的地名/地域来源用法，不表示所有人物曾居住于此。
- 未把 Verona 与政治实体或机构合并；cand-8681 的相关作品与人物关系仍按各自 S2 资格状态处理。本次不增加或删除候选、提及、statement。

S3 new 候选4,972，身份组4,789；S4 当前登记648组/799条映射，待登记4,141组/4,173条。

<a id="s4-place-verona-cross-chapter-20261017"></a>

### S4 place：Verona 跨章地点登记（2026-10-17）

- cand-7661 与 cand-8681 属于同一 S3 new 身份组 sg3-place-cand-8681，共同映射至 [维罗纳](../../../04-knowledge/units/places/verona.md)（units/places/verona）；两条候选映射只对应一张 place KU。
- 依据覆盖第8章 p.216 的 regional adjective、第9章 p.268 的明确地点名、第10章 pp.297、311、327 与第14章 p.348 的城市用法。第216页不据 regional adjective 推断出生/居住；其余仍为 Haskell 书内叙述。
- 3条直接关系候选留待 S6；本卡没有新增正式关系或扩展到政治实体、机构及未识别作品。

S4 累计登记649组/801条候选映射；待登记4,140组/4,171条；KU 总数1,668。

<a id="s3-s4-camillo-pamfili-place-endpoints-20261017"></a>

### S3/S4 place：Camillo Pamfili 的 palace 与 Algardi villa 分组纠偏（2026-10-17）

原组 sg3-place-pamfiliprincecamillonephewtopopeinnocentx 将 P.csv#15 的 palace（cand-1816）与 P.csv#16 的 villa built by Algardi（cand-1817）合为一个 place 身份，索引的共同父项 Camillo Pamfili 不能证明两座建筑为同一地点。第6章 p.148 先称流放期间Camillo 负责由 Algardi 建造一座罗马别墅，随后另称返罗马后为自己建造一座位于 Collegio Romano 对面的宫殿，明确区分 villa 与另建 palace。

cand-1816 改为 same → units/places/palazzo-doria-pamfili，复用既有 Palazzo Doria-Pamfili 地点卡。Roma Capitale 的 Turismo Roma 记录将该罗马宫殿定位于 Via del Corso，并记载其1647年归 Camillo Pamphilj，及其委托 Antonio Del Grande 的沿革（https://www.turismoroma.it/en/node/1422；访问于 2026-10-17）；结合既有卡所载第1章宫殿身份与第6章位置描述，支持复用。旧 new 组及理由保存在 alignment 历史字段。

cand-1817 保持 new，但从共享旧组拆出到 sg3-place-villa-doria-pamphilj，并登记至 units/places/villa-doria-pamphilj。罗马首都督察局将 Villa Doria Pamphilj 记为 Pamphilj 家族乡间庄园，记录 Camillo 的营建活动，并称 Algardi 等艺术家参与园区建设（https://sovraintendenzaroma.it/node/2148；访问于 2026-10-17）。该比对支持别墅身份，不把 Algardi 写成整个庄园的唯一设计者。外部身份记录分别附于两条 alignment 行；共组旧 token 和原理由均保留。

更新 book-statements.jsonl 中五条 villa 端点的 S3 映射限定，保留原书陈述和候选谓词。五条 villa 关系候选及一条 palace 关系候选共六条均仍待 S6；relations.csv 未改写。

S4 新增一张地点卡 04-knowledge/units/places/villa-doria-pamphilj.md，cand-1817 映射该 KU；cand-1816 映射既有宫殿 KU。本次不添加正式关系，也未填入未经单条核验的 enrichment 字段。

更新后 same=1,887（1,040个既有 KU），new=4,971（4,789组），conflict=8，excluded=100，undecided=5,441；S4 已登记650组/802条映射，待登记4,139组/4,169条映射；KU=1669。

<a id="s4-jesuit-fondo-di-gesu-86513-20261017"></a>

### S4 archive：Jesuit Archives N. 865-13 跨章身份组登记（2026-10-17）

- `archive-group-ff938f5595f2` 含 `cand-1532`（M.csv#69，pp.386–387）与 `cand-5338`；登记为[S. Andrea al Quirinale 祭坛画文书（耶稣会档案馆 Fondo di Gesù N. 865-13）](../../../04-knowledge/units/archives/jesuit-fondo-di-gesu-865-13-s-andrea-altarpiece-documents.md)（`units/archives/jesuit-fondo-di-gesu-865-13-s-andrea-altarpiece-documents`）。依据为第3章 p.88 注1–3与第19章附录1 p.386：三条脚注引用同一编号，注2、注3与附录题注交叉对应。
- 本卡只把对象范围界定为哈斯克尔所载的档案引用定位号及其描述；不将其表述成已核实的实体卷宗、档案层级或已逐件查阅的原件。候选 `cand-11509` 是祭坛画作品类型，仍保持独立 S3 待决。
- 三条直接关系候选（st-chp3-seciv-notes-l205-243-p88-n1-86513, st-chp3-seciv-notes-l205-243-p88-n2-86513, st-chp3-seciv-notes-l205-243-p88-n3-86513）继续留待 S6；本批未登记正式关系或 S5 enrichment。

S4 当前已登记651组/804条成员映射，尚待登记4,138组/4,167条。

<a id="s4-term-enlightenment-in-italy-20261017"></a>

### S3/S4 term：Enlightenment in Italy 跨章身份组登记（2026-10-17）

- `sg3-term-enlightenmentinitaly` 包含 `cand-0974`（E.csv#9）、`cand-0975`（#10 contacts of Italian intellectuals with England and France）、`cand-0976`（#11 opposition in Venice）；三个候选共享索引主项，两个子项是同一术语下的主题入口，不是另两个术语。本组登记为[意大利启蒙运动（Enlightenment in Italy）](../../../04-knowledge/units/terms/enlightenment-in-italy.md)（`units/terms/enlightenment-in-italy`）。
- 跨章对照覆盖第8章 p.225、第10章引言 p.288、第10章 pp.317–318和第15章 p.361。第8章“dawning Age”表述是对 Raimondo 的试探归类；第10章将启蒙思想在意大利的扩散说为初期缓慢，并称1748年通常被视为意大利“新精神”的起点，同时指出威尼斯直接参与有限；第15章又明确描述启蒙思想如何进入威尼斯。合并保留同一书内概念及其地域语境，不外推统一分期。
- 5 条直接 S2 statements 均非正式关系候选；本批未写入 `relations.csv`，也未使用外部术语库。S4 当前已登记652组/807条成员映射，尚待登记4,137组/4,164条。

<a id="s4-person-vittore-carpaccio-20261017"></a>

### S3/S4 person：Vittore Carpaccio 跨章身份组登记（2026-10-17）

- `new-person:carpaccio-vittore-89b0809b12` 含 `cand-0565`（C.csv#89，p.410 主项）与 `cand-0566`（C.csv#90，p.376《Scenes from Life of St Ursula》子目）。同一规范人名及两章书内上下文支持一位 source-local person，登记为[维托雷·卡帕乔（Vittore Carpaccio）](../../../04-knowledge/units/persons/vittore-carpaccio.md)（`units/persons/vittore-carpaccio`）。
- 第16章 p.376 将 Giovanni del Pian 的1785年版画与 Carpaccio 的圣乌尔苏拉场景相连；第20章后记 p.410 将 Carpaccio 列入 Della Lena 欣赏的画家。仅记录这两处书内提及，不补生卒年或外部生平；原作循环与版画组保持分开。
- 关系候选 `st-chp16-p376-toninotto-del-pian-prints-after-carpaccio`、`st-chp20-p410-della-lena-painter-appreciations` 留待 S6；本批未创建正式关系。
S4 当前已登记653组/809条成员映射，尚待登记4,136组/4,162条。

### S3 候选决定覆盖收口核对（2026-10-17）

- 对 `entity-candidates.csv` 与主候选 alignment 做全量机械覆盖核对：12,407 个候选均有且仅有一条决定记录和非空理由；same 行有 KU 目标，new 行有身份组，冲突与待决行保留来源定位及处理说明。跨类型统计见结果文件 S3 表。
- 当前分类为 same=1,887（指向1,040个既有 KU）、new=4,971（4,789组）、conflict=8、excluded=100、undecided=5,441。冲突和待证项仍处于各自明确状态；这次核对未把它们强制转成 same/new，也不表示其证据缺口已经解决。
- 该收口核对证明候选决定覆盖、去向字段和可追溯理由完整，不等同于全表身份判断的独立语义接收。S4 仍有4,136组/4,162条候选映射待登记；严格阶段审计 `errors=[]`、`s2_missing=[]`。

<a id="s3-s4-baroque-term-identity-20261017"></a>

### S3/S4 term：Baroque 跨章身份复核与文化范畴登记（2026-10-17）

- S3 将 cand-3569 从原 new 组改为 same → units/terms/baroque。其“Baroque period”候选及第1、2、6、7、8、18章的相关提及，与既有卡所引哈斯克尔第一版序言的操作性分期相同；原组号与旧决定保留在对齐行中，但不再计入 S4 新组。
- cand-4500 维持 new，单成员组 sg3-term-cand-4500，登记为[哈斯克尔论述中的巴洛克艺术文化范畴（The Baroque as an artistic-cultural category in Haskell's account）](../../../04-knowledge/units/terms/baroque-cultural-category-haskell.md)（units/terms/baroque-cultural-category-haskell）。跨第2、3、4、6、10、14章的提及共同指向书内较广的艺术文化范畴，与巴洛克时期卡及 Baroque painting 媒介类别分开；本区分不外推为一般艺术史范畴互斥。卡片引第2章 p.40 L99 与第10章 p.317 L123–124，未作外部术语核验。
- 直接关联的七条 S2 关系候选为st-chp2-secii-l91-104-baroque-flattery-interpretation, st-chp2-seciv-l31-43-patronage-encouraged-barque-style, st-chp3-seci-l3-14-mother-churches-baroque-inference, st-chp3-secii-l74-81-decoration-major-baroque-achievement, st-chp3-seciv-l141-150-cycle-reaction-against-baroque, st-chp4-sec-ii-p112-attack-on-baroque, st-chp6-p151-baroque-flowering-obscures-economic-crisis，均留待 S6；本次未写入 relations.csv 或 enrichment.jsonl。
- S4 当前已登记654组/810条成员映射，尚待登记4,134组/4,160条。

<a id="s3-s4-spanish-cause-in-rome-20261017"></a>

### S3/S4 place、term：Rome 端点复用与 Spanish cause 跨章登记（2026-10-17）

- S3 将 cand-6474 从原 new 组改为 same → units/places/rome。该候选的来源锚点以第6章 p.161 的叙述语境命名，同组核心指称均为 Rome 城市；唯一“countryside around Rome”提及保留为城外农业语境，不并入城市范围或另造无专名端点。七条直接关系候选中的 Rome 均指城市或前往该城。现有 Rome place KU 可复用，候选旧组号与旧判断保留在对齐行中。
- cand-4404 保持 new，单成员 term 组 sg3-term-cand-4404，登记为[哈斯克尔所述罗马的亲西班牙政治倾向（The Spanish cause in Rome in Haskell's account）](../../../04-knowledge/units/terms/spanish-cause-in-rome-haskell-account.md)（units/terms/spanish-cause-in-rome-haskell-account）。第2章 p.35、第5章 p.137、第7章 p.173 对 Ginnasi、Raggi、Carandini 与 Crescenzi 兄弟的表述支持同一书内政治倾向概念。它与既有 Cerquozzi patrons/Spanish sphere term 有交集但不等同；本组记录跨章的 cause/alignment 称谓，不把它当作正式组织。
- 六条直接 S2 关系候选为st-chp2-secii-l42-50-ginnasi_profile_partisan, st-chp5-notes-l142-rapaccioli-report, st-chp5-p137-carandini-spanish-alignment, st-chp5-p137-raggi-devoted-to-spanish-cause, st-chp7-p173-i07, st-chp7-p173-i08，留待 S6；Rome 候选关联的七条 S2 关系端点也可映射至现有 Rome KU，但本次均未写入 relations.csv。未新增 enrichment.jsonl 事实。
- S4 当前已登记655组/811条成员映射，尚待登记4,132组/4,158条。

<a id="s3-s4-first-war-of-castro-20261017"></a>

### S3/S4 event：第一次卡斯特罗战争跨章身份登记（2026-10-17）

- cand-4904 保持 new，单成员组 sg3-event-cand-4904，登记为[第一次卡斯特罗战争（First War of Castro）](../../../04-knowledge/units/events/first-war-of-castro.md)（units/events/first-war-of-castro）。第2章 p.58 明言1641年战争爆发；第6章 p.146 补述对帕尔马公爵的财政争端、军事进程及1644年3月和约。卡片路径此前存在一张未登记的历史草稿，但 manifest 和 accepted.yml 均无该对象；本次沿用固定路径，将其改写为当前有效的双语来源卡，不把孤立文件当作既有 KU。
- 身份边界保持明确：cand-0607 是合并索引入口且仍 undecided；cand-6289 是后续第二次战争；cand-6259 的未命名和约仍 undecided，不因记录战争结果而提升。五条直接 S2 关系候选（st-chp2-secvii-l3-3-parma-consequences-fragment, st-chp2-secvii-l5-19-barberini-effects-continuation, st-chp2-secvii-l5-19-financial-inquiry-threat, st-chp6-p146-1644-peace, st-chp6-p146-decline-war-onset）留待 S6；未写入 relations.csv 或 enrichment.jsonl。
- S4 当前已登记656组/812条成员映射，尚待登记4,131组/4,157条。

<a id="s3-s4-scalzi-in-venice-20261017"></a>

### S3/S4 institution：Scalzi 威尼斯分支登记（2026-10-17）

- cand-2389 保持 new，单成员身份组 sg3-institution-cand-2389，登记为[威尼斯赤足加尔默罗会（Scalzi in Venice）](../../../04-knowledge/units/institutions/scalzi-in-venice.md)（units/institutions/scalzi-in-venice）。第9章 p.269 将 Scalzi 说成加尔默罗会的严格分支，并称其1633年到达威尼斯；p.270 明确将 Carmelites 称为其母会。因此 cand-0563 母会候选保持独立；cand-5119 Discalced Trinitarians 亦为不同修会，不因共享“赤足”描述合并。
- 六条直接 S2 关系候选为st-chp9-p269-benefactions-and-public-alms, st-chp9-p269-scalzi-arrival-1633, st-chp9-p269-scalzi-luxury-pamphlet, st-chp9-p269-scalzi-noble-links-missions, st-chp9-p269-scalzi-original-church-too-small, st-chp9-p270-carmelite-patronage-comparison，留待 S6；修会、母会、教堂、赞助人和建筑师之间本次未登记 formal relations 或 enrichment。
- S4 当前已登记657组/813条成员映射，尚待登记4,130组/4,156条。

<a id="s4-person-endpoints-dati-animuccia-simonini-20261017"></a>

### S4 person：三个直接关系端点身份组登记（2026-10-17）

本批按 person 类型登记三个单成员 S3 new 身份组，每组对应一个双语 KU。仅依据 Haskell 正文、注释与索引记录书内身份；未添加外部生平、身份标识或正式关系。

- cand-0905（new-person:carlo-dati-621c03d9fe）→ [卡洛·达蒂（Carlo Dati）](../../../04-knowledge/units/persons/carlo-dati.md)（units/persons/carlo-dati）。书内锚点：第4章，印刷页108及注释；索引 D.csv#7；3 条直接 S2 关系候选留待 S6：st-chp4-sec-ii-l109-119-dati-disciple-friend, st-chp4-sec-ii-l109-119-dati-friend-cassiano, st-chp4-sec-ii-l109-119-dati-pages-about-cassiano-orthodoxy-alchemy。
- cand-0108（new-person:animuccia-giovanni-221f8cfa79）→ [乔万尼·阿尼穆恰（Giovanni Animuccia）](../../../04-knowledge/units/persons/giovanni-animuccia.md)（units/persons/giovanni-animuccia）。书内锚点：第3章，印刷页70；索引 A.csv#109；3 条直接 S2 关系候选留待 S6：st-chp3-secii-l54-60-animuccia-first-book-intent, st-chp3-secii-l54-60-animuccia-oratory-growth-and-second-book, st-chp3-secii-l54-60-haskell-musical-shift。
- cand-2435（new-person:francesco-simonini-44f28a129e）→ [弗朗切斯科·西蒙尼尼（Francesco Simonini）](../../../04-knowledge/units/persons/francesco-simonini.md)（units/persons/francesco-simonini）。书内锚点：第10章，印刷页312；索引 S.csv#123；3 条直接 S2 关系候选留待 S6：st-chp10-p312-simonini-battles-and-campaigns, st-chp10-p312-simonini-painted-portraits-of, st-chp10-p312-schulenburg-battle-paintings-created-by-simonini。

S4 当前已登记660组/816条成员映射，尚待登记4,127组/4,153条。

<a id="s3-bambini-existing-ku-20261017"></a>

### S3 person：Niccolò Bambini 既有身份复核（2026-10-17）

- cand-0171 原先列为 new 组 new-person:bambini-niccolo-d2c7887763；复核后改为 same → [units/persons/niccolo-bambini](../../../04-knowledge/units/persons/niccolo-bambini.md)。已有 Bambini 人物卡在 accepted.yml 与 ku-manifest.csv 中均为有效 person KU；第9章正文 p.249、p.252 的Niccolo Bambini 提及、索引 B.csv#18 的五组页码、图版42b来源及既有 cand-3846 same 决定共同指向同一人物。现行卡采用 Nicolò Bambini，书内索引作 Niccolò、正文多作 Niccolo；这些拼写差异保留，不生成重复卡。
- 三条直接 S2 关系候选（st-chp9-p247-bambini-frescoes, st-chp9-p252-bambini-painted-library-frescoes, st-chp9-p252-vendramin-cycle-attributed-to-bambini）仍待 S6；本次不改变关系表、卡片或补足字段。
- S3 same=1,890（1,040个 KU），new=4,968/4,786组；S4 已登记660组/816条，待登记4,126组/4,152条。

<a id="s4-person-endpoints-belloni-clostermann-20261017"></a>

### S4 person：Belloni 与 Clostermann 直接关系端点登记（2026-10-17）

本批登记两个单成员 person new 身份组，每组对应一个双语 KU；仅记录书内人物身份与语境，不新增外部生平或正式关系。
- cand-0271（new-person:antonio-belloni-giovanni-da1194d2db）→ [乔万尼·安东尼奥·贝洛尼（Giovanni Antonio Belloni）](../../../04-knowledge/units/persons/giovanni-antonio-belloni.md)（units/persons/giovanni-antonio-belloni）；书内锚点：第8章，印刷页203，索引 B.csv#118；3 条直接 S2 关系候选留待 S6：st-chp8-p203-belloni-collection, st-chp8-p203-belloni-hospitality-james-iii, st-chp8-p203-belloni-sent-gambarini-to-rome。
- cand-0791（new-person:clostermann-john-ba5d3dbe8f）→ [约翰·克洛斯特曼（John Clostermann）](../../../04-knowledge/units/persons/john-clostermann.md)（units/persons/john-clostermann）；书内锚点：第7章，印刷页198，索引 C.csv#321；3 条直接 S2 关系候选留待 S6：st-chp7-p198-closterman-instructions-advice, st-chp7-p198-closterman-shaftesbury-portrait, st-chp7-p198-guidi-drawings-project-failed。
- Belloni 所在段落另列 Giovanni Battista Bellucci；cand-0285 保持独立 new 组，不并入 Belloni。Closterman／Clostermann 的正文与索引拼写差异在卡片中并列保留。

S4 当前已登记662组/818条成员映射，尚待登记4,124组/4,150条。

<a id="s4-person-bellucci-direct-endpoint-20261017"></a>

### S4 person：Giovanni Battista Bellucci 直接端点登记（2026-10-17）

cand-0285 保持单成员 new 组 new-person:battista-bellucci-giovanni-dbf80f5eed，登记为 [乔万尼·巴蒂斯塔·贝卢奇（Giovanni Battista Bellucci）](../../../04-knowledge/units/persons/giovanni-battista-bellucci.md)（units/persons/giovanni-battista-bellucci）。第8章 p.203 与索引 B.csv#132 同指该人；同段将 Bellucci 明确称作另一位商人，与 Belloni 分开，故保留 cand-0285 与 cand-0271 两个独立人物组。
- 两条直接关系候选（st-chp8-p203-bellucci-crespi-pictures, st-chp8-p203-bellucci-dal-sole-pictures）留待 S6；未写入 formal relations 或 enrichment。
- S4 当前已登记663组/819条成员映射，尚待登记4,123组/4,149条。

<a id="s4-person-endpoints-bentinck-dupuy-20261017"></a>

### S4 person：Bentinck 与 Dupuy 直接关系端点登记（2026-10-17）

本批按 person 类型登记两个单成员 S3 new 组，各对应一个双语 KU。证据限于 Haskell 正文与书后索引；未添加外部传记或身份标识。
- cand-0289（new-person:bentinck-william-f9cae452d7）→ [威廉·本廷克（William Bentinck）](../../../04-knowledge/units/persons/william-bentinck.md)（units/persons/william-bentinck）；书内锚点：第10章，印刷页280；索引 B.csv#136；3 条直接 S2 关系候选留待 S6：st-chp10-p280-bentinck-orange-loyalty-reward, st-chp10-p280-portland-son-of-bentinck, st-chp10-p280-williamiii-favourite-bentinck。
- cand-0951（new-person:christophe-dupuy-384608af60）→ [克里斯托夫·迪皮（Christophe Dupuy）](../../../04-knowledge/units/persons/christophe-dupuy.md)（units/persons/christophe-dupuy）；书内锚点：第4章，印刷页108；索引 D.csv#53；3 条直接 S2 关系候选留待 S6：st-chp4-sec-ii-l109-119-cassiano-shows-papers-to-dupuy, st-chp4-sec-ii-l109-119-dupuy-knew-official-bouchard, st-chp4-sec-ii-l109-119-dupuy-prior-in-rome。

S4 当前已登记665组/821条成员映射，尚待登记4,121组/4,147条。

<a id="s4-person-domenico-bernini-20261017"></a>

### S4 person：Domenico Bernini 直接关系端点登记（2026-10-17）

cand-0294 保持单成员 new 组 new-person:bernini-domenico-e245cae3bd，登记为 [多梅尼科·贝尔尼尼（Domenico Bernini）](../../../04-knowledge/units/persons/domenico-bernini.md)（units/persons/domenico-bernini）。第2章 p.58 注8称艺术家的儿子 Domenico 多年后写下另一种叙述；第7章 p.191正文明确将 Domenico 称为 Bernini 之子，注3列出 Domenico Bernino；书后索引 B.csv#141 将 p.58 注、p.85 与p.191 汇于同一人物主项。该组身份仅限书内证据。
- 三条直接关系候选（st-chp2-seciv-l190-245-later-bernini-account, st-chp7-p191-i07, st-chp7-p191-i08）留待 S6；未新增 formal relations。
- S4 当前已登记666组/822条成员映射，尚待登记4,120组/4,146条。

<a id="s3-giovanni-bonati-existing-identity-20261017"></a>

### S3 person：Giovanni Bonati／Bonatti 既有身份复核（2026-10-17）

- cand-0385（B.csv#232，Bonati, Giovanni）原属 new-person:bonati-giovanni-d0cc94b9b1；复核后改为 same → [units/persons/giovanni-bonati](../../../04-knowledge/units/persons/giovanni-bonati.md)。第1章 p.6 注记的对象正是该人物：Haskell/OCR 作 Bonari，印刷页目视校读为 Bonati；既有 Bonatti 卡已收录同一页及拼写校正。Treccani DBI 词条明列“BONATTI (Bonati), Giovanni”，并记录 Cardinal Carlo Pio junior 的保护及 Florence、Bologna、Modena、Parma、Milan、Venice 的旅行（[词条](https://www.treccani.it/enciclopedia/bonatti-giovanni-detto-giovannino-del-pio-o-il-ferraresino_(Dizionario-Biografico)/)）。这一独立书目身份依据与本书同页人名、保护人及旅行内容吻合，支持复用现有人物 KU，不按一字拼写差异新建。
- 直接 S2 关系候选（st-chp1-l186-187-pio-travel）留待 S6；本次未改写关系表或既有卡。
- S3 same=1,891（1,040个 KU），new=4,967/4,785组；S4 已登记666组/822条，待登记4,119组/4,145条。

<a id="s3-bombelli-index-subentry-20261017"></a>

### S3 person：Sebastiano Bombelli 索引子目并入跨章人物组（2026-10-17）

- cand-0384（B.csv#231）原为 undecided：索引候选无独立 S2 mention，故旧理由要求补正文锚点。第8章 p.227 正文明确说 Stefano Conti 的妻子、儿子和本人肖像由 Sebastiano Bombelli 绘制；索引子目“portraits of Stefano Conti and his family”即定位该处，不是另一个人物或作品实体。现改为 new，并入候选主项 cand-0383 的 {GROUP}。
- 主项 cand-0383 的索引 B.csv#230 覆盖 p.227、278；第8章与第10章正文均以 Sebastiano Bombelli 指同一人物。本组可登记为一个 person KU；第10章召往 Vienna 的关系候选仍待 S6。
- S3 same=1,891（1,040个 KU），new=4,968/4,785组，undecided=5,440；S4 已登记666组/822条，待登记4,119组/4,146条。

<a id="s4-person-bombelli-crosschapter-20261017"></a>

### S4 person：Sebastiano Bombelli 跨章身份组登记（2026-10-17）

S3 身份组 new-person:bombelli-sebastiano-c6f300a2fb 含 cand-0383（B.csv#230 主项，pp.227、278）与 cand-0384（B.csv#231 肖像子项，p.227），共同映射至 [塞巴斯蒂亚诺·邦贝利（Sebastiano Bombelli）](../../../04-knowledge/units/persons/sebastiano-bombelli.md)（units/persons/sebastiano-bombelli）。第8章 p.227 与第10章 p.278 均用同一全名；卡片只记录书内两个锚点，不补外部传记或职位。
- 直接关系候选（st-chp10-p278-hapsburgs-summon-bombelli）留待 S6；未新增 formal relations。
- S4 当前已登记667组/824条成员映射，尚待登记4,118组/4,144条。

<a id="s4-person-boni-crosschapter-20261017"></a>

### S3/S4 person：Giacomo Antonio Boni 跨章身份复核与登记（2026-10-17）

- 候选 cand-0388、cand-0389 维持同一 S3 new 组 new-person:antonio-boni-giacomo-1f5e983239；B.csv#235 主项列 p.201 与 p.214 注；B.csv#236 子项“Virgil 'portrait' for Prince Eugene of Savoy”列 p.201。第7章 p.201 以全名称在 Bologna 为 Prince Eugene 绘制 Virgil 'portrait' 的 Boni；第8章 p.214 注以同一全名称受召为宫殿房间绘制神话壁画。跨章全名、职业语境及索引子项互相吻合，未发现同名冲突或既有 person KU。
- 该组登记为 [贾科莫·安东尼奥·博尼（Giacomo Antonio Boni）](../../../04-knowledge/units/persons/giacomo-antonio-boni.md)（units/persons/giacomo-antonio-boni）。卡片限于本书中的姓名、语境与具体书目／作品提及；未补外部传记，未写入正式关系。

<a id="s4-person-fra-bartolommeo-crosschapter-20261017"></a>

### S3/S4 person：Fra Bartolommeo 跨章身份复核与登记（2026-10-17）

- 候选 cand-0252、cand-0253 维持同一 S3 new 组 new-person:bartolommeo-fra-e49e28ddb8；B.csv#99 主项列 p.348；B.csv#100 的 S. Marco 子项列 p.231。第8章 p.231 明确将 S. Marco 画作归于 Fra Bartolommeo；第14章 p.348 记载 Algarotti 对 Fra Bartolommeo 的艺术成就印象深刻。两处均指画家，不将作品 S. Marco 并入人物卡。
- 该组登记为 [弗拉·巴托洛梅奥（Fra Bartolommeo）](../../../04-knowledge/units/persons/fra-bartolommeo.md)（units/persons/fra-bartolommeo）。卡片限于本书中的姓名、语境与具体书目／作品提及；未补外部传记，未写入正式关系。

<a id="s4-person-boschini-crosschapter-20261017"></a>

### S3/S4 person：Marco Boschini 跨章身份复核与登记（2026-10-17）

- 候选 cand-0412、cand-0413 维持同一 S3 new 组 new-person:boschini-marco-6cf51f8040；第7章 p.193 注2的 Boschini p.44 引文由第21章书目识别为 Marco Boschini《La carta del navegar pittoresco》（Venice, 1660）；第13章 p.345 明称 Marco Boschini 的《Ricche Miniere》于1733年由较年轻的 Zanetti 修订。B.csv#259–260 主项及作品子项对应两章。两部出版物仍各自作为 archive 对象处理；作者身份合并为一个人物 KU。
- 该组登记为 [马尔科·博斯基尼（Marco Boschini）](../../../04-knowledge/units/persons/marco-boschini.md)（units/persons/marco-boschini）。卡片限于本书中的姓名、语境与具体书目／作品提及；未补外部传记，未写入正式关系。

S4 当前已登记670组/830条候选映射，尚待登记4,115组/4,138条。

<a id="s4-archive-temanza-zibaldone-ms796-20261017"></a>

### S3/S4 archive：Temanza 未刊 Zibaldone MS 796 登记（2026-10-17）

S3 new 组 archive-group-temanza-zibaldone-ms796 含 cand-2547（T.csv#10 的 Zibaldone 索引子项）与 cand-6588（第6章 p.165 注5 的未刊手稿引用），合并登记为 [ 托马索·滕曼扎未刊《Zibaldone》手稿（MS 796）（Tommaso Temanza, unpublished Zibaldone MS 796）](../../../04-knowledge/units/archives/temanza-zibaldone-ms-796.md)（units/archives/temanza-zibaldone-ms-796）。索引页码、题名、责任者和 MS 796 定位相合；该卡仅记录 Haskell 的引文定位，手稿未独立查阅。
- 直接 S2 引用候选 st-chp6-p165-n5-cite 留待 S6；本次未新增 formal relations。
- S4 当前已登记671组/832条成员映射，尚待登记4,114组/4,136条。

<a id="s4-person-isidoro-bianchi-endpoint-20261017"></a>

### S3/S4 person：Isidoro Bianchi 直接关系端点登记（2026-10-17）

cand-0372 保持单成员 new 组 new-person:bianchi-isidoro-fb1a5df6ac，登记为 [伊西多罗·比安基（Isidoro Bianchi）](../../../04-knowledge/units/persons/isidoro-bianchi.md)（units/persons/isidoro-bianchi）。第15章 p.371 注1与索引 B.csv#219 均给出同一全名和定位；卡片不补外部生平或未具名题献书目。
- 两条直接关系候选（st-chp15-p371-note1-antiquarians-dedicated-books-to-querini, st-chp15-p371-note1-bianchi-dedication）留待 S6；未新增 formal relations。
- S4 当前已登记672组/833条成员映射，尚待登记4,113组/4,135条。

<a id="s4-person-vittorio-bigari-endpoint-20261017"></a>

### S3/S4 person：Vittorio Bigari 直接关系端点登记（2026-10-17）

cand-0374 保持单成员 new 组 new-person:bigari-vittorio-2e86eea2d2，登记为 [维托里奥·比加里（Vittorio Bigari）](../../../04-knowledge/units/persons/vittorio-bigari.md)（units/persons/vittorio-bigari）。第8章 p.222 正文与索引 B.csv#221 均给出 Vittorio Bigari 全名；正文称其为 Bolognese artist 并记载天花壁画。人物身份清楚，作品归属关系仍按 S2 候选待审。
- 直接关系候选（st-chp8-p222-bigari-paints-catholic-religion-fresco）留待 S6；未写入 formal relations。

<a id="s4-person-bernardo-bizoni-endpoint-20261017"></a>

### S3/S4 person：Bernardo Bizoni 直接关系端点登记（2026-10-17）

cand-0377 保持单成员 new 组 new-person:bernardo-bizoni-e54061a723，登记为 [贝尔纳多·比佐尼（Bernardo Bizoni）](../../../04-knowledge/units/persons/bernardo-bizoni.md)（units/persons/bernardo-bizoni）。第2章 p.30 注1与索引 B.csv#224 均以全名指向 Bernardo Bizoni；注释称其为 Giustiniani 的朋友和 journal keeper，但未给出出版物题名。人物身份可登记，友谊及 journal 相关候选关系留待 S6。
- 直接关系候选（st-chp2-seci-l124-157-bizoni-kept-journal, st-chp2-seci-l124-157-giustiniani-friend-bizoni）留待 S6；未写入 formal relations。

S4 当前已登记674组/835条成员映射，尚待登记4,111组/4,133条。

<a id="s4-person-mme-de-boccage-endpoint-20261017"></a>

### S3/S4 person：Mme de Boccage 直接关系端点登记（2026-10-17）

cand-0380 保持单成员 new 组 new-person:boccage-de-mme-d3ea92b77b，登记为 [博卡热夫人（Mme de Boccage）](../../../04-knowledge/units/persons/mme-de-boccage.md)（units/persons/mme-de-boccage）。索引 de 形式与正文 du 形式指向 p.302 同一旅行观察段；注2所引版本未独立查阅。
- 直接 S2 候选 st-chp10-p302-boccage-palace-english-taste 留待 S6；未新增 formal relations。
- S4 当前已登记675组/836条成员映射，尚待登记4,110组/4,132条。

<a id="s4-person-francesco-bordoni-endpoint-20261017"></a>

### S3/S4 person：Francesco Bordoni 直接关系端点登记（2026-10-17）

cand-0392 保持单成员 new 组 new-person:bordoni-francesco-67f728663d，登记为 [弗朗切斯科·博尔多尼（Francesco Bordoni）](../../../04-knowledge/units/persons/francesco-bordoni.md)（units/persons/francesco-bordoni）。第7章 p.174 以全名记载其随 Pietro Francavilla 到达巴黎，并称其为助手和未来女婿；索引 B.csv#239 定位至同页。
- 直接 S2 关系候选 st-chp7-p174-i10 留待 S6；未新增 formal relations。
- S4 当前已登记676组/837条成员映射，尚待登记4,109组/4,131条。

<a id="s4-person-francesco-albergati-capacelli-endpoint-20261017"></a>

### S3/S4 person：Francesco Albergati-Capacelli 直接关系端点登记（2026-10-17）

cand-0023 保持单成员 new 组 new-person:albergati-capacelli-francesco-361200a267，登记为 [弗朗切斯科·阿尔贝加蒂-卡佩切利（Francesco Albergati-Capacelli）](../../../04-knowledge/units/persons/francesco-albergati-capacelli.md)（units/persons/francesco-albergati-capacelli）。第13章 p.336 将其列为 Pasquali 的 non-conforming spirits 朋友之一；索引 A.csv#22 定位至同页。
- 直接 S2 关系候选 st-chp13-p336-pasquali-friend-of-albergati-capacelli 留待 S6；未新增 formal relations。
- S4 当前已登记677组/838条成员映射，尚待登记4,108组/4,130条。

<a id="s4-person-claudio-aquaviva-endpoint-20261017"></a>

### S3/S4 person：Claudio Aquaviva 直接关系端点登记（2026-10-17）

cand-0113 保持单成员 new 组 new-person:aquaviva-claudio-aquaviva-claudio-general-fbc1409a12，登记为 [克劳迪奥·阿夸维瓦（Claudio Aquaviva）](../../../04-knowledge/units/persons/claudio-aquaviva.md)（units/persons/claudio-aquaviva）。第3章 p.67 以全名称其为 General，并记其对 S. Vitale 装饰方案的个人关注和建议；同段另述其筹资通信及 Richeôme 的献书。
- 直接 S2 关系候选 st-chp3-secii-l19-31-aquaviva-controlled-and-shaped-scheme, st-chp3-secii-l19-31-aquaviva-correspondence-raising-funds, st-chp3-secii-l19-31-richeome-dedicated-book-to-aquaviva 留待 S6；未新增 formal relations。
- S4 当前已登记678组/839条成员映射，尚待登记4,107组/4,129条。

<a id="s4-archive-the-table-pinax-dialogue-20261017"></a>

### S3/S4 archive：The Table / Pinax 对话登记（2026-10-17）

cand-6390 保持单成员 new 组 archive-group-7156a2e4e186，登记为[《寓意人生图的对话》（The Table (Pinax dialogue)）](../../../04-knowledge/units/archives/the-table-pinax-dialogue.md)（units/archives/the-table-pinax-dialogue）。第6章 p.157 正文称 The Table，注2称 Pinax 并校正 Cebes 归属；同注仅称作者另有其人、可能作于公元一世纪。作品内部的寓意图不另立 work。Haskell 所用 Seebohm 英译本 cand-6407 仍为 undecided；不与古代对话合并。
- 五条直接 S2 候选 st-chp6-p157-effetti-literary-interest, st-chp6-p157-renaissance-ekphrasis, st-chp6-p157-table-attribution-correction, st-chp6-p157-table-content, st-chp6-p157-table-vogue-mascardi 留待 S6；未新增 formal relations。
- S4 当前已登记679组/840条成员映射，尚待登记4,106组/4,128条。

<a id="s4-archive-monaco-raccolta-112-1763-20261017"></a>

### S3/S4 archive：Pietro Monaco 1763 年版画集登记（2026-10-17）

cand-7618 保持单成员 new 组 archive-group-c1033ea3e250，登记为[《圣史绘画112幅版画集（1763年版）》（Collection of 112 Prints of Sacred-History Paintings (1763 edition)）](../../../04-knowledge/units/archives/monaco-raccolta-112-stampe-1763.md)（units/archives/monaco-raccolta-112-stampe-1763）。本卡指第21章书目明确列出的完整 Venice 1763 版次；版画作为出版物内容，逐件作品另有 work 身份。第13章注1无年份，不将其短题名强配到1763或其他版次。
类型与版次核对参照 Treccani《意大利人传记辞典》Pietro Monaco 条目（2011，edition-history paragraphs，访问2026-10-17；https://www.treccani.it/enciclopedia/pietro-monaco_(Dizionario-Biografico)/）：该文称1763年为定本，后续版次为1772、1789。Haskell p.345 将 Viero 后出版记为1779；年代差异保留待证。Lombardia Beni Culturali 相关页面记录的是该系列中的具体版画，不作为整版的同粒度外部身份标识。（https://www.lombardiabeniculturali.it/stampe/schede/H0540-05143/）
- 五条直接 S2 候选 st-chp13-p345-monaco-1763-later-edition, st-chp13-p345-monaco-collection-advertised-dealer, st-chp13-p345-monaco-pittoni-works-reproduced, st-chp13-p345-monaco-three-works-reproduced, st-chp13-p345-monaco-tiepolo-works-reproduced 留待 S6；未新增 formal relations。
- S4 当前已登记680组/841条成员映射，尚待登记4,105组/4,127条。

<a id="s4-archive-applausi-poetici-baroni-1639-20261017"></a>

### S3/S4 archive：Applausi poetici 1639 年版登记（2026-10-17）

cand-5531 保持单成员 new 组 archive-group-6e104b1ffa20，登记为[《莱奥诺拉·巴罗尼颂诗集（1639年）》（Poetic Tributes to Leonora Baroni (1639 edition)）](../../../04-knowledge/units/archives/applausi-poetici-leonora-baroni-1639.md)（units/archives/applausi-poetici-leonora-baroni-1639）。正文称 Paolo Giordano II 负责出版赞颂 Leonora Baroni 的诗，注3给出题名、Bracciano 与1639年。S0 OCR `plorie` 与扫描印本 `glorie` 的校正依既有 stages.md 记录；S0 不改写。
- 四条直接 S2 候选 st-chp4-sec-i-l20-24-baroni-poems, st-chp4-sec-i-l20-24-collection-honours-baroni, st-chp4-sec-i-l20-24-poems-by-admirers, st-chp4-sec-i-l42-67-fn96-baroni-publication 留待 S6；未新增 formal relations。
- S4 当前已登记681组/842条成员映射，尚待登记4,104组/4,126条。

<a id="s4-person-jane-costello-20261017"></a>

### S3/S4 person：Jane Costello 身份组登记（2026-10-17）

cand-7016 保持单成员 new 组 new-person:costello-jane-costello-jane-miss-c6062f1806，登记为[简·科斯特洛（Jane Costello）](../../../04-knowledge/units/persons/jane-costello.md)（units/persons/jane-costello）。书内以 Miss Jane Costello 指称作者；University of Chicago Press 的1950年卷期目录将 Jane Costello 列为该篇论文作者。候选 cand-3509 的单姓 Costello 仍 undecided，不合并；本卡不补入传记事实。
- 未新增 formal relations。
- S4 登记后：682组/843条成员映射已登记，4,103组/4,125条待登记。

<a id="s4-archive-journal-warburg-courtauld-institutes-20261017"></a>

### S3/S4 archive：Warburg 期刊跨题名登记（2026-10-17）

cand-6004 保持单成员 new 组 archive-group-288e9f99e396，登记为[《瓦尔堡与考陶尔德学院学报》（Journal of the Warburg and Courtauld Institutes）](../../../04-knowledge/units/archives/journal-warburg-courtauld-institutes.md)（units/archives/journal-warburg-courtauld-institutes）。候选来源的旧题名 Journal of the Warburg Institute 与后续题名依出版社期刊史归于同一连续期刊：Courtauld 关联正式体现在1940年卷III刊名中。Haskell 第4章1944年引文使用旧题名短式；候选 cand-6005 的 Blunt 文章对象仍 undecided，不在此处改判。
- 未新增 formal relations。
- S4 登记后：683组/844条成员映射已登记，4,102组/4,124条待登记。

<a id="s4-archive-costello-twelve-pictures-1950-20261017"></a>

### S3/S4 archive：Jane Costello 1950 年论文登记（2026-10-17）

cand-7017 保持单成员 new 组 archive-group-4ecb8673d506，登记为[《委拉斯开兹“订购”的十二幅画与瓦尔古阿内拉审判（1950年）》（The Twelve Pictures "Ordered by Velasquez" and the Trial of Valguarnera (1950)）](../../../04-knowledge/units/archives/costello-twelve-pictures-ordered-velasquez-1950.md)（units/archives/costello-twelve-pictures-ordered-velasquez-1950）。Haskell 第21章书目 p.420 与 University of Chicago Press 1950年第13卷第3–4期目录核对题名、作者、页码237–284；JSTOR 记录 DOI 10.2307/750214。论文正文及 Haskell 所引页未独立查阅。作者候选 cand-7016 与期刊候选 cand-6004 已分别登记为人物和期刊 KU。
- 四条直接 S2 引文候选 st-chp1-secii-l613-n1-cites-costello-p274-275, st-chp1-secii-p11-n3-cites-costello-p278, st-chp1-secii-p11-n6-cites-costello-p274, st-chp7-p172-n3-cite-costello 留待 S6；未新增 formal relations。
- S4 当前已登记684组/845条成员映射，尚待登记4,101组/4,123条。

<a id="s4-costello-card-table-provenance-20261017"></a>

### S4 结构化字段与来源登记（2026-10-17）

Costello 三张 S4 卡的字段表已映射为 enrichment.jsonl 行，按卡片来源序号关联 Haskell、University of Chicago Press 与 JSTOR 记录；三条外部来源登记至 sources.csv。此修复只补齐既有卡片结构化字段及来源映射，不改变身份组、KU 数量或关系决定。

<a id="s4-institution-austrian-government-20261017"></a>

### S3/S4 institution：Austrian government 端点登记（2026-10-17）

cand-8471 保持单成员 new 组 sg3-institution-cand-8471，登记为[奥地利政府（Austrian government）](../../../04-knowledge/units/institutions/austrian-government.md)（units/institutions/austrian-government）。Haskell 第9章 p.259 注5将 Austrian government 作为 Marco Foscarini 图书收藏1800年出售记述中的受让方。名称按原书保留，不指定更细的政府机关。
- 直接 S2 候选 st-chp9-p259-note5-foscarini-library-transfer 留待 S6；未新增 formal relations。
- S4 登记后：685组/846条已登记，4,100组/4,122条待登记。

<a id="s4-institution-hofbibliothek-vienna-20261017"></a>

### S3/S4 institution：Hofbibliothek, Vienna 端点登记（2026-10-17）

cand-8472 保持单成员 new 组 sg3-institution-cand-8472，登记为[维也纳宫廷图书馆（Hofbibliothek, Vienna）](../../../04-knowledge/units/institutions/hofbibliothek-vienna.md)（units/institutions/hofbibliothek-vienna）。Haskell 第9章 p.259 注5称 Foscarini 图书收藏后来位于 Hofbibliothek, Vienna。此机构与 Vienna place、藏书 collection 分开；未确认现代继承馆名。
- 直接 S2 候选 st-chp9-p259-note5-library-current-location 留待 S6；未新增 formal relations。
- S4 登记后：686组/847条已登记，4,099组/4,121条待登记。

<a id="s4-archive-marco-foscarini-library-20261017"></a>

### S3/S4 archive：Marco Foscarini 书籍与手稿收藏登记（2026-10-17）

cand-8462 保持单成员 new 组 archive-group-915e97393793，登记为[马尔科·福斯卡里尼的书籍与手稿收藏（Marco Foscarini's library of manuscripts and history books）](../../../04-knowledge/units/archives/marco-foscarini-library.md)（units/archives/marco-foscarini-library）。Haskell 第9章 pp.259–260 描述该收藏的内容和 Foscarini 的收藏活动；注5报告1800年出售及后来的存放地点。人物端点复用 Marco Foscarini KU；家族与 Vienna place 端点沿用既有映射；两个机构端点分别登记。候选 cand-1059 的 Foscarini palace 仍 undecided，不强行并入建筑或空间 KU。
- 四条直接 S2 候选 st-chp9-p259-marco-library-versus-pictures, st-chp9-p259-note5-foscarini-library-transfer, st-chp9-p259-note5-library-current-location, st-chp9-p260-books-and-manuscripts-returned 留待 S6；未新增 formal relations。
- S4 登记后：687组/848条已登记，4,098组/4,120条待登记。

<a id="s4-foscarini-card-table-fields-20261017"></a>

### S4 结构化字段登记（2026-10-17）

Foscarini 书籍与手稿收藏、Austrian government 和 Hofbibliothek 三张卡的表格字段已映射为10条 enrichment.jsonl 记录，统一关联本书来源 haskell-1980-rev-ed；本批无外部来源登记。此修复只补齐字段级来源结构，不改变 S3 身份裁决、KU 映射或 S6 关系状态。

<a id="s4-person-tirso-gonzalez-20261017"></a>

### S3/S4 person：Tirso Gonzalez 身份组登记（2026-10-17）

cand-1213（G.csv#121；索引列 pp.91–92）保持单成员 new 组 new-person:gonzalez-tirso-dbb6b94ada，登记为[蒂尔索·冈萨雷斯（Tirso Gonzalez）](../../../04-knowledge/units/persons/tirso-gonzalez.md)（units/persons/tirso-gonzalez）。第3章 p.91 与 p.92 的全名和总会长语境相合；仅按 Haskell 的称谓记录，未补外部身份或生平。
- 三条直接 S2 关系候选 st-chp3-seciv-l152-163-gonzalez-resumed-undertaking, st-chp3-seciv-l165-177-tirso-final-decision-may-1695, st-chp3-seciv-l165-177-tirso-forbade-further-criticism 留待 S6；未新增 formal relations。
- S4 登记后：688组/849条已登记，4,097组/4,119条待登记。

<a id="s4-tirso-card-table-fields-20261017"></a>

### S4 结构化字段登记（2026-10-17）

Tirso Gonzalez 人物卡的原文姓名与本书称谓两行已映射为 enrichment.jsonl，均关联 Haskell 来源 haskell-1980-rev-ed。本记录只补齐字段级来源结构，不改变 S3 身份决定、KU 映射或三条 S6 待审关系候选。

<a id="s4-person-martino-longhi-elder-20261017"></a>

### S3/S4 person：Martino Longhi the Elder 跨章身份组登记（2026-10-17）

cand-1427（L.csv#84，索引列 pp.69、400）保持单成员 new 组 new-person:elder-longhi-martino-e7aa738609，登记为[马蒂诺·隆吉（长者）（Martino Longhi the Elder）](../../../04-knowledge/units/persons/martino-longhi-elder.md)（units/persons/martino-longhi-elder）。第3章 p.69 与第20章 p.400 在不同章节重复全名并均置于 Chiesa Nuova 建筑师语境；与 Martino Longhi the Younger KU 分开，不推断亲缘，也未访问外部身份来源。
- 两条直接 S2 关系候选 st-chp20-p400-bonadonna-russo-longhi-and-angelo-cesi, st-chp3-secii-l40-52-longhi-replaces-matteo 留待 S6；第20章的任命解释保留 probably 限定。
- S4 登记后：689组/850条已登记，4,096组/4,118条待登记。

<a id="s4-martino-longhi-elder-card-fields-20261017"></a>

### S4 结构化字段登记（2026-10-17）

Martino Longhi the Elder 人物卡的原文姓名和职业身份两行已映射为 enrichment.jsonl，分别保留第3章 p.69 与第20章 p.400 的 Haskell 来源。此记录不改变身份边界、KU 映射或两条 S6 待审关系候选。

<a id="s4-person-giovanni-battista-piranesi-20261017"></a>

### S3/S4 person：Giovanni Battista Piranesi 跨章身份组登记（2026-10-17）

cand-1938（P.csv#139，索引页码309、358、370）保持单成员 new 组 new-person:battista-giovanni-piranesi-8cb8ba565d，登记为[乔瓦尼·巴蒂斯塔·皮拉内西（Giovanni Battista Piranesi）](../../../04-knowledge/units/persons/giovanni-battista-piranesi.md)（units/persons/giovanni-battista-piranesi）。第10章 p.309、第14章 p.358 与第15章 p.370 的姓氏提及由书内索引归入同一全名主项。
- 区分：cand-1937 Francesco Piranesi（P.csv#138，p.366）保持独立人物组；cand-10495 是其1786年版画作品组；cand-10545 浴室版画集合仍 undecided，不拆成单件。
- 直接 S2 候选 st-chp15-p370-piranesi-prints-created-by-piranesi 留待 S6；未新增 formal relations。
- S4 登记后：690组/851条已登记，4,095组/4,117条待登记。

<a id="s4-piranesi-card-fields-20261017"></a>

### S4 结构化姓名字段登记（2026-10-17）

Giovanni Battista Piranesi 人物卡的原文全名已映射为一条 enrichment.jsonl 记录，来源为 Haskell 书内索引 P.csv#139。该结构化登记不改变跨章身份组、Francesco Piranesi 的分组，也不改变浴室版画候选的 undecided 状态或 S6 关系待审状态。

<a id="s4-person-andrea-mantegna-20261017"></a>

### S3/S4 person：Andrea Mantegna 跨章身份组登记（2026-10-17）

cand-1522（M.csv#59，索引页码175、380）保持单成员 new 组 new-person:andrea-mantegna-b0a921de46，登记为[安德烈亚·曼特尼亚（Andrea Mantegna）](../../../04-knowledge/units/persons/andrea-mantegna.md)（units/persons/andrea-mantegna）。第7章 p.175 与第17章 p.380 的姓氏提及由索引对应同一全名主项；未添加外部身份或作品清单。
- Manfrin collection 候选 cand-1513 仍 undecided/untyped；不建立作品或收藏 KU。
- 直接 S2 关系候选 st-chp17-p380-manfrin-collection-represented-mantegna 留待 S6；未新增 formal relations。
- S4 登记后：691组/852条已登记，4,094组/4,116条待登记。

<a id="s4-mantegna-card-fields-20261017"></a>

### S4 结构化姓名字段登记（2026-10-17）

Andrea Mantegna 人物卡原文全名已映射为一条 enrichment.jsonl 记录，来源为 Haskell 书内索引 M.csv#59。该记录不改变 Manfrin collection 候选 cand-1513 的 undecided/untyped 状态，也不提前裁决 S6 关系。

<a id="s4-person-alessandro-scarlatti-20261017"></a>

### S3/S4 person：Alessandro Scarlatti 跨章身份组登记（2026-10-17）

cand-2393（S.csv#81，索引页码230、278）保持单成员 new 组 new-person:alessandro-scarlatti-e86fc84234，登记为[亚历山德罗·斯卡拉蒂（Alessandro Scarlatti）](../../../04-knowledge/units/persons/alessandro-scarlatti.md)（units/persons/alessandro-scarlatti）。第8章 p.230 提供全名，第10章 p.278 的姓氏与歌剧语境由索引归入同一人物主项；本卡不创建具体歌剧对象。
- 直接 S2 关系候选 st-chp8-p230-scarlatti-music 留待 S6；未新增 formal relations。
- S4 登记后：692组/853条已登记，4,093组/4,115条待登记。

<a id="s4-scarlatti-card-fields-20261017"></a>

### S4 结构化姓名字段登记（2026-10-17）

Alessandro Scarlatti 人物卡原文全名已映射为一条 enrichment.jsonl 记录，来源为 Haskell 书内索引 S.csv#81。该记录不改变第8、10章身份组或 S6 待审关系状态。

<a id="s4-person-stefano-della-bella-20261018"></a>

### S3/S4 person：Stefano della Bella 身份组登记（2026-10-18）

cand-0268（B.csv#115，索引页码176、183）保持单成员 new 组 new-person:bella-della-stefano-4ee4ce0873，登记为[斯特凡诺·德拉·贝拉（Stefano della Bella）](../../../04-knowledge/units/persons/stefano-della-bella.md)（units/persons/stefano-della-bella）。第7章两页以同一全名和艺术家身份相互支持。
- 保留既有 S0 OCR 对照：p.176 扫描读作 della Bella，OCR 转录差异不写回来源文件。
- 三条直接 S2 关系候选 st-chp7-p176-i21, st-chp7-p176-i22, st-chp7-p183-i17 留待 S6；未新增 formal relations。
- S4 登记后：693组/854条已登记，4,092组/4,114条待登记。

<a id="s4-stefano-della-bella-card-fields-20261018"></a>

### S4 结构化字段登记（2026-10-18）

Stefano della Bella 人物卡的原文全名与职业身份已映射为两条 enrichment.jsonl 记录，均链接到 Haskell 书内第7章来源；现有 OCR/扫描对照与三条 S6 待审关系保持原样。

<a id="s4-person-francesco-gabburri-20261018"></a>

### S3/S4 person：Francesco Gabburri 跨章身份组登记（2026-10-18）

cand-1097（G.csv#4，索引页码211n、241n、266n）保持单成员 new 组 new-person:francesco-gabburri-21c9271841，登记为[弗朗切斯科·加布里乌里（Francesco Gabburri）](../../../04-knowledge/units/persons/francesco-gabburri.md)（units/persons/francesco-gabburri）。第8章 p.211、p.241 注5与第9章 p.266 注6给出全名及书信语境，索引对应同一人物主项。
- 直接 S2 关系候选 st-chp8-p241-note5-gabburri-correspondence 留待 S6；未新增 formal relations。
- S4 登记后：694组/855条已登记，4,091组/4,113条待登记。

<a id="s4-francesco-gabburri-card-fields-20261018"></a>

### S4 结构化字段登记（2026-10-18）

Francesco Gabburri 人物卡中的原文全名与本书称谓已按 `build_field_facts.extract_records` 登记为两条 enrichment.jsonl 记录，均由 Haskell 书内来源 `haskell-1980-rev-ed` 支持；未添加外部身份事实，直接关系候选仍待 S6。

<a id="s4-person-giorgio-massari-20261018"></a>

### S3/S4 person：Giorgio Massari 跨章身份组登记（2026-10-18）

cand-1562（M.csv#103，索引页码270、272、321）保持单成员 new 组 new-person:giorgio-massari-068f7c6d56，登记为[乔尔乔·马萨里（Giorgio Massari）](../../../04-knowledge/units/persons/giorgio-massari.md)（units/persons/giorgio-massari）。第9章 p.270以全名记述 Gesuati 聘请其建造新教堂，p.272称其为 Pietà 教堂建筑师；第10章 p.321续见 Massari 模型及建筑师的回应。索引将这些页码列于同一人物条目。
- 直接关系候选 st-chp9-p272-massari-architect, st-chp9-p272-massari-palladian-lines 留待 S6；相关陈述 st-chp10-p321-pieta-governor-invited-lodoli-to-view-massari-model, st-chp9-p270-gesuati-new-church-public-funding 保留供 S6 核对，未新增 formal relations。
- S4 登记后：695组/856条已登记，4,090组/4,112条待登记。

<a id="s4-giorgio-massari-card-fields-20261018"></a>

### S4 结构化字段登记（2026-10-18）

Giorgio Massari 人物卡中的原文全名、建筑师称谓及 Gesuati 新教堂项目已按 `build_field_facts.extract_records` 登记为三条 enrichment.jsonl 记录，均由 Haskell 书内来源 `haskell-1980-rev-ed` 支持；未添加外部身份事实，关系候选仍待 S6。

<a id="s3-reuse-bartolommeo-nazari-existing-ku-20261017"></a>

### S3/S4 person：Bartolommeo Nazari 对齐至既有 KU（2026-10-17）

cand-1727 的 S3 决定由 new 改为 same，复用[巴托洛梅奥·纳扎里（Bartolomeo Nazari）](../../../04-knowledge/units/persons/b-nazari.md)（units/persons/b-nazari）。S1 索引 N.csv#7 将第10章 p.287、293、295、312、314、322及第13章 p.345列为同一人物条目；S2 第10章 p.312 全名为 Bartolommeo Nazari，并明确称其为 Schulenburg 画像者；p.322又以完整姓名记载其绘制 Lodoli 肖像。既有 KU 的 Treccani DBI 来源记名 Bartolomeo Nazari，并记1733年 Schulenburg 委托骑马肖像；本次实际阅读该 DBI 条目（https://www.treccani.it/enciclopedia/bartolomeo-nazari_res-1dbdf466-03ed-11e7-b5f4-00271042e8d9_(Dizionario-Biografico)/，访问日期 2026-10-17）用于核对姓名拼写及同一 Schulenburg 委托。判断为单写/双写 m 的拼写差异，不把 DBI 的生平或作品事实扩写进书内断言，也不新建重复 KU。外部身份记录另列于 alignment.csv。

<a id="s4-person-andrew-fountaine-20261017"></a>

### S3/S4 person：Sir Andrew Fountaine 跨章身份组登记（2026-10-17）

cand-1060（F.csv#75，索引页码279、343n）保持单成员 new 组 new-person:andrew-fountaine-7d5ace0041，登记为[安德鲁·方丹爵士（Sir Andrew Fountaine）](../../../04-knowledge/units/persons/andrew-fountaine.md)（units/persons/andrew-fountaine）。第10章 p.279给出全名、收藏家／鉴赏家称谓并称 Narford Hall 为其乡间居所；第13章 p.343 注3列其为 Zanetti 木刻图版集的受赠者之一，但未将其对应到某件图版。
- 直接关系候选 st-chp10-p279-narford-seat-fountaine 留待 S6；受赠者集合陈述 st-chp13-p343-notes-note3-named-dedicatees 不作逐件配对，未新增 formal relations。
- S4 登记后：696组/857条已登记，4,088组/4,110条待登记。

<a id="s4-andrew-fountaine-card-fields-20261017"></a>

### S4 结构化字段登记（2026-10-17）

Sir Andrew Fountaine 人物卡的原文全名、Haskell称谓与 Narford Hall 乡间居所已登记为三条 enrichment.jsonl 记录，均由 Haskell 书内来源 haskell-1980-rev-ed 支持；第13章受赠者名单没有被拆成逐件关系。

<a id="s4-archive-delogu-grechetto-1928-20261017"></a>

### S3/S4 archive：Delogu《G. B. Castiglione detto Il Grechetto》登记（2026-10-17）

cand-11312（body-mention，source anchor 指向第21章书目 line 415）保持单成员 new 组 archive-group-2bb2d5388a18，登记为[G. B. 卡斯蒂廖内（称作“格雷切托”）](../../../04-knowledge/units/archives/giuseppe-delogu-g-b-castiglione-il-grechetto-1928.md)（units/archives/giuseppe-delogu-g-b-castiglione-il-grechetto-1928）。Haskell书目印刷页420提供作者、原题名、Bologna和1928；S2据扫描页将 OCR 的 II 校为印刷题名 Il。第1章 p.21 n.1 引用该书 p.40 n.9，但 Delogu 专著及被引内容均未独立查阅。
- 直接关系候选 st-chp1-secii-p21-n1-cites-delogu-1928-p40n9 留待 S6；本卡不新增 formal relations。

<a id="s4-archive-delogu-grechetto-fields-20261017"></a>

### S4 archive 结构化字段登记（2026-10-17）

Delogu 1928 书目卡的中文工作题名、原题名、文献类型、作者、出版地及出版年已登记为六条 enrichment.jsonl 记录，均由 Haskell 全书书目或第1章引文支持。原题名按 S2 页图校正，Delogu 专著和其第40页注9未独立查阅。

<a id="s4-archive-chiesa-gesu-cristo-vendicata-cluster-20261017"></a>

### S3/S4 archive/person/work：第13章 p.335 书籍与卷首图像身份簇登记（2026-10-17）

- archive 组 `archive-group-chiesa-gesu-cristo-vendicata-text`：cand-2718（UVWXYZ.csv#54，p.335n）与 cand-9993（第13章 p.335 注2完整题名）映射至[《耶稣基督教会在其标志与教义上的辩护》](../../../04-knowledge/units/archives/la-chiesa-di-gesu-cristo-vendicata.md)。索引主项／子目与注2题名相合；只确认书籍文本层级，未确认具体版次、出版地或出版年。索引原错误页码和 OCR `3^5n` 的校正保留在候选与原始索引，不改写来源。
- person 组 `new-person:antonio-da-venezia-1f888bfe23`（cand-10148）登记为[Antonio da Venezia](../../../04-knowledge/units/persons/antonio-da-venezia.md)，仅表示 Haskell 题名前置署名形式；未补传记、教职或外部身份，也不建立正式著作权边。person 组 `new-person:battista-giovanni-recurti-abdf8eeb09`（cand-2111）登记为[Giovanni Battista Recurti](../../../04-knowledge/units/persons/giovanni-battista-recurti.md)，以索引全名及本章 Recurti 称名相互定位；出版者与 Albrizzi 关系仍是 Haskell 的书内陈述。
- work 组 `workgrp-eecaa82c32cc90`（cand-10149）登记为[《宗教践踏异端》](../../../04-knowledge/units/works/religion-trampling-on-heresy-book-frontispiece.md)，粒度为注释所称图像／设计，不指明具体版次印张或存世原稿。Piazzetta 绘制、Pitteri 刻版按 Haskell 注释保留。
- 六条直接 S2 关系候选（st-chp13-p335-albrizzi-close-relations-with-recurti, st-chp13-p335-note2-book-frontispiece, st-chp13-p335-note2-piazzetta-drew-design, st-chp13-p335-note2-pitteri-engraved-design, st-chp13-p335-piazzetta-frontispiece-before-albrizzi-enterprise, st-chp13-p335-recurti-published-devotional-book）全部留待 S6；端点已映射至新 KU 或既有 KU，但没有新增正式关系。`st-chp13-p335-note2-recurti-citation` 的 `relation_candidate=false` 状态不变。Gallo 1948 p.176 n.4 与被引书籍均未独立查阅。
- 本簇四个 S3 新身份组登记为四个不同 KU，五条候选映射；S4 累计登记701组/863条映射，待登记4,083组/4,104条，KU 总数1,720，结构化字段10,642条。


<a id="s4-event-salvatore-exhibition-series-20261017"></a>

### S4 event：S. Salvatore in Lauro 常规画展系列登记（2026-10-17）

cand-6051 保持 S3 独立 new 组 `sg3-event-cand-6051`，登记为[圣萨尔瓦托雷因劳罗教堂常规画展](../../../04-knowledge/units/events/s-salvatore-in-lauro-picture-exhibition-series.md)（units/events/s-salvatore-in-lauro-picture-exhibition-series）。第5章 p.128 支持常规系列、12月10日庆典与画展、10–11日展出及1682年起 Ghezzi 负责安排；未推算系列首年。第8章 p.222 注4仅作为跨章线索，1704届是否属于该系列不作关系裁决。
- 保持边界：cand-11770（1675）与 cand-11771（1697）为独立届次 event 组；cand-11942（1701）不并入系列；cand-11783（1708）仍 undecided；place cand-6053（回廊）仍 undecided。另一个 S. Giovanni Decollato 系列及其1675年届次保持分立。
- 12条直接 S2 陈述中5条 relation_candidate（st-chp5-p128-ghezzi-appointment, st-chp5-p128-salvatore-1675-instance-of-series, st-chp5-p128-salvatore-1697-instance-of-series, st-chp5-p128-salvatore-series-venue, st-chp8-p222-n4-portrait-lent-to-salvatore-exhibition）均留待 S6；7条其余陈述维持各自属性/限定状态。本轮没有新增 formal relation 或外部身份行。
- S4 累计登记702组/864条映射，待登记4,082组/4,103条，KU 总数1,721，结构化字段10,648条。

<a id="s4-work-titian-andrians-and-person-john-walker-20261017"></a>

### S4 work/person：The Andrians 与 John Walker 直接端点登记（2026-10-17）

- work 组 `workgrp-49973a4844cb3f`（cand-4249，两处提及：第2章 p.25与p.129注4）登记为[提香《安德罗斯人》](../../../04-knowledge/units/works/titian-andrians.md)。只按Haskell归作Titian绘画；Ferrara至Rome的转移说法归于Haskell。Rubens版本保持与原作区分；相邻 OCR 题名 `Worship os Venus` 原样注明，未作本轮OCR校正。
- person 组 `new-person:john-walker-e3f95ea0f9`（cand-4356）登记为[John Walker](../../../04-knowledge/units/persons/john-walker.md)，只记录Haskell的姓名形式及其对《维纳斯的崇拜》和《安德罗斯人》的限定性转述观点；无外部身份核对或传记补写。
- The Andrians 的五条直接 S2 关系候选（st-chp2-seci-l124-157-albani-study-andrians, st-chp2-seci-l124-157-darpino-copy-andrians, st-chp2-seci-l124-157-rubens-version-andrians, st-chp2-seci-l124-157-walker-view-andrians, st-chp2-seci-l44-53-andrians-transfer）及 Walker—The Worship of Venus 的观点候选 `st-chp2-seci-l124-157-walker-view-worship` 均留待 S6。cand-0121（Cavaliere d’Arpino）仍 undecided；本次不由其复制关系推断姓名或身份。没有新增正式关系或外部身份记录。
- S4 累计登记704组/866条映射，待登记4,080组/4,101条，KU 总数1,723，结构化字段10,658条。

<a id="s4-place-germany-crosschapter-20261017"></a>

### S4 place：Germany 跨章地点组登记（2026-10-17）

- `cand-5529`（`sg3-place-cand-5529`）登记至[德国地点卡](../../../04-knowledge/units/places/germany.md)，仅作为 Haskell 多章中的地理地点名；未补定现代边界、历史主权、具体路线或未记载地点。
- 对照第4章 p.96、 第7章 pp.194–195、第10章 pp.293、295、第13章 p.334及第15章 p.361的书内语境，保留人物服役、迁移、作品流向、赞助、旅行、君主比较与收藏转运的原文范围。p.295 的比较句不是关系候选。
- 六条直接 S2 关系候选（st-chp10-p293-venetian-patronage-germany, st-chp13-p334-albrizzi-travel-and-vienna-education, st-chp15-p361-most-schulenburg-collection-sent-to-germany, st-chp4-sec-i-l20-24-soldiered-in-germany, st-chp7-p194-carlone-court-migration, st-chp7-p195-lazzarini-output-germany）留待 S6。cand-8832 与 cand-8861 的 Southern Germany 地点组不并入本组；无外部身份来源或正式关系新增。
- S4 累计登记705组/867条映射，待登记4,079组/4,100条；KU=1,724，字段=10,665。

<a id="s4-institution-dominicans-crosschapter-20261017"></a>

### S4 institution：Dominicans 跨章修会身份组登记（2026-10-17）

- `cand-0941`（`sg3-institution-cand-0941`）登记至[多明我会机构卡](../../../04-knowledge/units/institutions/dominicans.md)；S3 以 D.csv#43 及第5章 Santa Sabina、第9章威尼斯修会语境、第13章 local-Dominicans 判断为修会层级 institution。alignment 已补充跨章范围理由：地方团体、教堂与个别行动不等同于全体修会。
- 8处来源引文覆盖组织称谓及地方语境；六条直接 S2 关系候选（st-chp5-p131-1636-transfer-to-barberini, st-chp5-p131-dominicans-decided-to-sell-raphael-holy-family, st-chp5-p131-dominicans-held-raphael-holy-family, st-chp9-p270-dominican-commission, st-chp9-p270-n07-benigna-dominican-church-model, st-chp9-p270-n07-zanetti-dominican-alms）留待 S6。第9章 p.271 的 `st-chp9-p271-dominican-church-exaltation` 不是 relation candidate，不转为正式边。未使用外部身份来源。
- S4 累计登记706组/868条映射，待登记4,078组/4,099条；KU=1,725，字段=10,673。

<a id="s4-event-memmo-family-palace-open-house-20261017"></a>

### S4 event：Memmo 家族宫邸开放聚会组登记（2026-10-17）

- `cand-11534`（`sg3-event-cand-11534`）登记为[Memmo 宫邸开放聚会事件卡](../../../04-knowledge/units/events/memmo-family-palace-open-house.md)。按第15章 p.368，识别为反复活动而非单次事件；原文未识别具体宫邸、兄弟姓名、来客名单或具体场次。
- Andrea Memmo 复用 `units/persons/andrea-memmo`；宫邸 `cand-10517` 与两类未具名参与者 `cand-11532`、`cand-11533` 均仍 undecided。五条直接 S2 关系候选（st-chp15-p368-memmo-open-house-at-family-palace, st-chp15-p368-memmo-open-house-for-advanced-spirits, st-chp15-p368-memmo-open-house-hosted-by, st-chp15-p368-memmo-open-house-until-death, st-chp15-p368-memmo-open-house-with-brothers）留待 S6；未新增正式关系或外部身份来源。
- S4 累计登记707组/869条映射，待登记4,077组/4,098条；KU=1,726，字段=10,674。

<a id="s3-spain-polity-crosschapter-20261017"></a>

### S3 institution/place：Spain 跨章政治实体与地理地点裁决（2026-10-17）

- cand-4591（第2章 p.28）、cand-8123（第9章 p.246）、cand-8833（第10章 p.276）由三个单候选 new 组并为一个机构身份组 sg3-institution-spain-polity。第2、3、5、7、8、9、10章反复以 Spain / Spanish rule 指同一国家政治实体；战争威胁、Ludovisi为其利益行事、Spain及其在Rome的支持者、对意大利画家的兴趣、Naples的Spanish rule、对Spain的绥靖及相似政体语境分别保留为原书表述，不推导政体沿革、精确边界或未记载外交事实。原单候选组名与裁决说明逐条留在alignment历史注释中。
- 地理组复核：cand-10409（第14章 p.359，并见第15章 p.361）从 new 改为 same → units/places/spain；其含义是 Tiepolo 前往／身处 Spain 这一地理地点，与 cand-5120 及已复用同一 place KU 的 cand-5667 相同。旧单候选组与原决定理由留在alignment历史注释中。
- 修正两条提及映射：m-chp2-seciv-l31-43-0046 的 Spain 是 Francesco 离开的目的地，改映射 cand-5120；m-chp5-sec-iii-l36-43-039 的 Spain 与其在 Rome 的支持者相连，是政治实体语境，改映射 cand-4591。未改变相应书内断言或候选关系。
- 边界：cand-5511 Spanish Crown、cand-7478 Spanish Empire、cand-9147 Spanish monarchy 与 cand-4592 threatened-war event 仍是各自不同的 new 组；cand-6622 “Spanish political power in Italy”继续 undecided，因“the Spaniards / Spanish cause”不足以单独判定为国家、军政群体或具体机构。未具名 Spanish collective、Spanish Embassy 与有关人物／事件候选仍保持各自现行决定；未把这些对象并入本卡。

<a id="s4-spain-polity-registration-20261017"></a>

### S4 institution：Spain 政治实体身份组登记（2026-10-17）

cand-4591、cand-8123、cand-8833 均映射至[西班牙政治实体（Spain as a polity）](../../../04-knowledge/units/institutions/spain-polity.md)（units/institutions/spain-polity）。卡片只记录 Haskell 的跨章政治实体指称；地理地点 Spain 仍指向既有 units/places/spain，未使用外部身份标识或声称外部验证。

直接关系端点候选 st-chp4-sec-ii-p117-spanish-french-quarrels、st-chp4-sec-ii-p117-spanish-backing、st-chp6-p156-lorenzo-connections-with-spain-grow-closer、st-chp7-p189-i28、st-chp8-p203-naples-families-and-school 留待 S6；本轮没有新增 relations.csv 正式边。其余含 Spain 语境的 statement 仍按各自已有端点、语气与候选关系状态处理，不因本次身份登记自动升级。

- 当前S3统计：same=1,893，new=4,966／4,781组，conflict=8，excluded=100，undecided=5,440。
- S4 累计：已登记708组／872条成员映射；待登记4,073组／4,094条映射；KU=1,727。机构类型为 21/26 已登记、170/170 待登记；地点类型为 40/48 已登记、519/519 待登记。


### S4 结构化字段：Spain 政治实体（2026-10-17）

西班牙政治实体卡的“书内指称与范围”表已按 build_field_facts.extract_records 为单卡提取并登记三行：enr-14425、enr-14426、enr-14427。三行均 source_backed，映射至既有 Haskell 来源 haskell-1980-rev-ed；表中 S1–S9 仍指向各自章节、页码和行号。全库 build_field_facts.py 预览显示另有三条外部来源登记缺项，分别来自其他既有卡片（src-24fd4d5c5e90ace5、src-a9f1d182264561ef、src-f3e3a57be7801fc4）；它们不是本卡所需来源。本卡目标预览无警告，故仅写入本卡三行 enrichment，sources.csv 未改动。

<a id="s4-person-direct-relation-endpoints-20261017"></a>

### S4 person：三组直接关系端点身份组登记（2026-10-17）

- 按 S3 已裁为 new 的身份组登记，每组一个 person KU；中文标题为编辑性音译，英文规范名保留候选与书内索引／正文形式。本批未查询外部身份来源。
- new-person:benjamin-styles-96734d9ba8（cand-2531）登记至[Benjamin Styles 人物卡](../../../04-knowledge/units/persons/benjamin-styles.md)。Haskell 正文称 Mr Styles，索引列 Styles, Benjamin；卡片保留此差别，不补写外部身份。Moor Park 建造阶段未分定。
- new-person:lazzaro-riviera-b4050e50ae（cand-2204）登记至[Lazzaro Riviera 人物卡](../../../04-knowledge/units/persons/lazzaro-riviera.md)。仅记录 Haskell 关于 Boscarati 四幅寓意画及 La Educazione Virile 小册子的委托／出版归属；小册子未独立查阅。
- new-person:anna-colonna-22071d55fd（cand-0805）登记至[Anna Colonna 人物卡](../../../04-knowledge/units/persons/anna-colonna.md)。原书称她被选作 Don Taddeo 的新娘，不据此断言婚礼完成；Contestabile 仅为原文称谓，未识别其个人身份。
- 三组各有3条直接 S2 关系候选作为端点，共9条；人物端点现已映射，但关系仍留待 S6。本批未增加 relations.csv 正式边。
- 三张卡的九条姓名、身份、委托、出版、婚姻选择及亲缘字段由 build_field_facts.extract_records 逐卡提取并写入既有 Haskell 来源字段；enrichment IDs：enr-14428, enr-14429, enr-14430, enr-14431, enr-14432, enr-14433, enr-14434, enr-14435, enr-14436。来源登记表未改动。
- 登记后 person 类型：316组／402条候选映射已登记，753组／754条映射待登记；全书 S4 累计711组／875条候选映射已登记，4,070组／4,091条映射待登记；KU=1,730。

<a id="s4-person-direct-relation-endpoints-batch2-20261017"></a>

### S4 person：Francesco Maria della Rovere、Jennifer Montagu、Ippolito Bentivoglio、Francis Xavier 四组登记（2026-10-17）

本批按当前 S3 `new` 决定逐组登记，每个单成员组登记一个 person KU；身份判断依据限于书内姓名、索引定位与正文锚点，不作无证据的跨人合并。
- cand-2671（new-person:della-francesco-maria-of-rovere-urbino-a2e180b241）登记至[Francesco Maria della Rovere 人物卡](../../../04-knowledge/units/persons/francesco-maria-della-rovere-urbino.md)。书末索引给出姓名与 Duke of Urbino 头衔，第2章 p.54 正文同名；未将未具名的占有行动者或全部公爵收藏继承写成已识别事实。
- cand-1687（new-person:jennifer-montagu-52540a5df8）登记至[Jennifer Montagu 人物卡](../../../04-knowledge/units/persons/jennifer-montagu.md)。索引列 p.52、56 注；正文分别提到其 Barberini 天顶画文章及其向作者提供 Tessin 记载的线索。本轮未独立查阅该文章。
- cand-0293（new-person:bentivoglio-ippotilo-0720feb34a）登记至[Ippolito Bentivoglio 人物卡](../../../04-knowledge/units/persons/ippolito-bentivoglio.md)。正文拼写 Ippolito，索引拼作 Ippotilo；以正文拼写作标题并保留索引异写，书内政治行动及 Guido、Enzo 亲缘字段各按原书表述。
- cand-2826（new-person:francis-xavier-914536af47）登记至[Francis Xavier 人物卡](../../../04-knowledge/units/persons/francis-xavier.md)。第3章 p.64、84、85 注4 的 Francis/St Francis Xavier 指向同一具名圣人；圣髑内容仅记录 Haskell 注释，未作独立核验。
- 四张卡共提取18条双语卡片结构字段，均 source_backed 并复用既有 `haskell-1980-rev-ed` 来源；enrichment IDs：enr-14437–enr-14454。sources.csv 未改动。
- 四组各含3条直接 S2 关系候选，共12条；本次只完成端点身份映射，相关关系留待 S6，relations.csv 未新增正式边。
- 登记后 person 类型为320组／406条候选映射已登记、749组／750条待登记；全书累计715组／879条已登记、4,066组／4,087条待登记；KU=1,734，enrichment=10,704。

<a id="s4-person-direct-relation-endpoints-batch3-20261017"></a>

### S4 person：Count Camillo Carandini、Marchese Girolamo Durazzo、André Félibien、Andrea Ferrerio 四组登记（2026-10-17）

本批按当前 S3 `new` 决定登记四个单成员 person 身份组；只据原书索引和正文记录姓名、角色与书内事实，不作外部身份补证。
- cand-0542（new-person:camillo-carandini-camillo-carandini-conte-5372eb31de）登记至[Count Camillo Carandini 人物卡](../../../04-knowledge/units/persons/camillo-carandini.md)。索引列 Count Camillo Carandini；第5章 p.137 称其倾向西班牙一方且收藏 Cerquozzi 此类绘画，注2随名列出1619–1663。
- cand-0953（new-person:durazzo-girolamo-f6ce69a495）登记至[Marchese Girolamo Durazzo 人物卡](../../../04-knowledge/units/persons/girolamo-durazzo.md)。第8章 p.213–214 将其置于热那亚显贵家族与跨城绘画收藏语境；Giordano、Solimena 的作品按家族归属记录。
- cand-1015（new-person:andre-felibien-3106675281）登记至[André Félibien 人物卡](../../../04-knowledge/units/persons/andre-felibien.md)。索引作 Félibien, André，正文作 Felibien；保留拼写差别。Haskell 称其为法国史家／作者，p.115 关于素描的所有权仍归 Massimi。
- cand-1024（new-person:andrea-ferrerio-b07af1830b）登记至[Andrea Ferrerio 人物卡](../../../04-knowledge/units/persons/andrea-ferrerio.md)。索引含 Vigilance 与 Ferrara 总主教宫子目；第8章 p.221–222 称其为雕塑家及 Giuseppe Mazza 的学生，并记述雕像与楼梯灰泥装饰。
- 四张卡共提取18条结构字段（enr-14455–enr-14472），均 source_backed 并复用既有 `haskell-1980-rev-ed` 来源；sources.csv 未改动。
- 四组各有3条直接 S2 关系候选，共12条；人物端点已映射，相关关系留待 S6；relations.csv 未新增正式边。
- 登记后 person 类型为324组／410条候选映射已登记、745组／746条待登记；全书累计719组／883条已登记、4,062组／4,083条待登记；KU=1,738，enrichment=10,722。

<a id="s4-archive-boschini-ricche-miniere-1733-20261017"></a>

### S4 archive：Boschini《Ricche Miniere》1733年修订本双候选组登记（2026-10-17）

- S3 身份组 archive-group-boschinis-ricche-miniere-zanetti-1733 含索引候选 cand-2858（UVWXYZ.csv#195，p.345）与正文候选 cand-10118（第13章 p.345、OCR L164）。两行均为 new 且同组，现共同映射至 [Boschini《Ricche Miniere》1733年修订本卡](../../../04-knowledge/units/archives/boschini-ricche-miniere-revision-1733.md)；一组登记一个 archive KU。
- 正文称 Antonio Maria the Younger 修订 Boschini《Ricche Miniere》，并将修订与1733年及致其年长堂兄的友好献辞相联系；书末索引以 Zanetti, A. M., the Younger 条目列出同一修订项。显示题名为描述性工作题名，不补出版者、出版地或未读版本的书目细节。
- 七条字段记录（enr-14473–enr-14479）均 source_backed，复用既有 haskell-1980-rev-ed 来源；sources.csv 未改动。
- 直接 S2 候选 st-chp13-p345-ricche-miniere-edited-1733 与 st-chp13-p345-ricche-miniere-dedication 保持待 S6。修订者候选 cand-2854 当前为 S3 undecided，未映射人物 KU；献辞对象 cand-2838 已 same 至 a-m-zanetti-the-elder，但未因此提前写正式边。relations.csv 未改动。
- 登记后 archive 类型为101组／138条候选映射已登记、1,103组／1,112条待登记；全书累计720组／885条已登记、4,061组／4,081条待登记；KU=1,739，enrichment=10,729。

<a id="s4-archive-zatta-letter-1761-20261017"></a>

### S4 archive：Zatta 致未具名公爵书信（1761）双候选组登记（2026-10-17）

- S3 身份组 `archive-group-zatta-letter-1761` 含正文候选 `cand-10024` 与书信题名候选 `cand-10178`。p.339 注3明示该段所说的小图像见 Zatta 1761 年书信第23页，并交叉引用第338页注2；两候选由此对齐到同一被引书信，共映射至一个 archive KU。
- 卡片保留 Haskell 所引不完整题名、1761 年、未具名公爵，以及原注 Fiorenza 后附的 Venice 更正；原信、完整题名和刊地未独立核实。第338页注2另列的 `Lettera Giustificativa di Antonio Zatta` 是另一书目对象，未并入本组。
- 八条字段记录（enr-14480–enr-14487）均为 source_backed，复用既有 `haskell-1980-rev-ed`；未改 `sources.csv`。
- `st-chp13-p338-note2-zatta-authored-letter` 与 `st-chp13-p338-note2-zatta-letter-to-unnamed-duke` 两条直接 S2 关系候选保留待 S6；收信人没有具名端点。`relations.csv` 未改动。
- 登记后 archive 类型为102组／140条候选映射已登记、1,102组／1,110条待登记；全书累计721组／887条已登记、4,060组／4,079条待登记；KU=1,740，enrichment=10,737。

<a id="s4-archive-zanetti-delle-antiche-statue-20261017"></a>

### S4 archive：Zanetti《Delle Antiche Statue Greche e Romane》身份组登记（2026-10-17）

- S3 身份组 `archive-group-zanetti-delle-antiche-statue-1740` 含正文候选 `cand-10104` 与索引候选 `cand-2846`（UVWXYZ.csv#183，子目 Delle Antiche Statue Greche e Romane）。正文题名与索引子目完全对应，两候选共同映射至一个 archive KU。
- Haskell 称该作1725年开始、十五年后由 Albrizzi 出版；原文未直接给出出版年，本卡不将时间间隔换算成1740年。第344页书内评价也按 Haskell 的表述记录。原书和具体版本未独立查阅。
- 六条字段记录（enr-14488–enr-14493）均为 source_backed，复用既有 `haskell-1980-rev-ed`；未改 `sources.csv`。
- 出版者候选陈述 `st-chp13-p343-delle_antiche_statue-published_by_albrizzi` 保留待 S6；`relations.csv` 未改动。
- 登记后 archive 类型为103组／142条候选映射已登记、1,101组／1,108条待登记；全书累计722组／889条已登记、4,059组／4,077条待登记；KU=1,741，enrichment=10,743。

<a id="s4-archive-guida-spirituale-molinos-20261017"></a>

### S4 archive：Molinos《Guida Spirituale》文本身份组登记（2026-10-17）

- S3 身份组 `archive-group-molinos-guida-spirituale-text` 含索引子目候选 `cand-1681`（M.csv#221，页82）与正文候选 `cand-5255`（第3章 p.82，L61）。索引题名与正文引文出处一致，两候选共同映射至一个 archive KU。
- S3 仅确认文本层级；未识别具体刊本、版次、原件或出版信息。脚注1（L202）只写 `Book I, chapter 16, verse 117`，未具名书名，保留待证。
- 六条字段记录（enr-14494–enr-14499）均为 source_backed，复用既有 `haskell-1980-rev-ed`；未改 `sources.csv`。
- `st-chp3-seciv-l58-67-molinos-guida-quote` 保留待 S6 裁决；未新增人物—文献正式关系，`relations.csv` 未改动。
- 登记后 archive 类型为104组／144条候选映射已登记、1,100组／1,106条待登记；全书累计723组／891条已登记、4,058组／4,075条待登记；KU=1,742，enrichment=10,749。

<a id="s4-archive-marino-poems-by-leading-artists-20261017"></a>

### S4 archive：Marino 描写画家作品的诗组身份组登记（2026-10-17）

- S3 身份组 `archive-group-c659964650de` 含正文候选 `cand-4464`（第2章 p.38 L77）与索引子目候选 `cand-1551`（M.csv#90，页38）。两处均指向 Marino 描写主要艺术家作品的同一组诗作，共映射至一个 archive KU。
- Haskell 称诗作流行并赞赏其中所写作品的异教性质；单篇题名、具体对象、版本和存本均未给出。该诗组与 *Adone* 及致 Marcello Sacchetti 的未具名歌曲分开。
- 四条字段记录（enr-14500–enr-14503）均为 source_backed，复用既有 `haskell-1980-rev-ed`；未改 `sources.csv`。
- `st-chp2-secii-l71-78-marino-poems-and-pagan-qualities` 保留待 S6；未新增人物—文献正式关系，`relations.csv` 未改动。
- 登记后 archive 类型为105组／146条候选映射已登记、1,099组／1,104条待登记；全书累计724组／893条已登记、4,057组／4,073条待登记；KU=1,743，enrichment=10,753。

<a id="s4-archive-marino-adone-20261017"></a>

### S4 archive：Marino《Adone》单篇文本登记（2026-10-17）

- S3 组 `archive-group-marino-adone-epic` 以索引候选 `cand-1549`（M.csv#88，子目 Adone，页115）代表正文第4章 p.115 所名的同一诗作，登记为一个 archive KU。
- Haskell 称其为 Marino 最著名的诗；另称 Poussin 相关图像题材主要为神话场景且松散地受该诗启发。该组与 Marino 人物、Poussin 图像组及描写画家作品的诗组分别保留；无版本或存本断言。
- 五条字段记录（enr-14504–enr-14508）均为 source_backed，复用既有 `haskell-1980-rev-ed`；未改 `sources.csv`。
- 直接关系候选 `st-chp4-sec-ii-p115-adone-created-by-marino` 与 `st-chp4-sec-ii-p115-drawings-adone` 保留待 S6；`relations.csv` 未改动。
- 登记后 archive 类型为106组／147条候选映射已登记、1,098组／1,103条待登记；全书累计725组／894条已登记、4,056组／4,072条待登记；KU=1,744，enrichment=10,758。

<a id="s4-archive-saint-non-voyage-pittoresque-20261017"></a>

### S4 archive：Saint-Non《Voyage Pittoresque》身份组登记（2026-10-17）

- S3 身份组 `archive-group-saint-non-voyage-pittoresque-text` 含正文候选 `cand-10583`（第15章 p.371 L80）与索引子目候选 `cand-2342`（S.csv#30，页371）。题名完全对应，两候选映射至一个 archive KU。
- Haskell 说 Dominique De Non 曾在那不勒斯为 Abbé de Saint-Non 的出版物工作，但没有说明具体贡献。二者保持为不同人物角色；本卡不推定作者、编者或版本信息。
- 五条字段记录（enr-14509–enr-14513）均为 source_backed，复用既有 `haskell-1980-rev-ed`；未改 `sources.csv`。
- 直接关系候选 `st-chp15-p371-de-non-saint-non-travel-book-work` 保留待 S6；`relations.csv` 未改动。
- 登记后 archive 类型为107组／149条候选映射已登记、1,097组／1,101条待登记；全书累计726组／896条已登记、4,055组／4,070条待登记；KU=1,745，enrichment=10,763。

<a id="s4-archive-salerno-giustiniani-gallery-1960-20261017"></a>

### S4 archive：Salerno《The Picture Gallery of Vincenzo Giustiniani》跨章引文身份组登记（2026-10-17）

- S3 身份组 `archive-group-bd46446e4adc` 的单一正文候选 `cand-4324` 连接第2章注5、第4章注2与第21章书目条目：两章均引用 Salerno 1960 年的 Giustiniani 绘画收藏 inventory，书目确认题名为 *The Picture Gallery of Vincenzo Giustiniani*。登记为一个 archive KU。
- 书目页影确认期刊 Burlington Magazine、1960 年及页码21–27、93–104、135–150；文章和所引页面未独立查阅。作者仅记为 `Salerno, L.`；人物候选 `cand-4323` 仍为 S3 undecided，不扩名，也不与附近的 Dr. Salerno 合并。
- 六条字段记录（enr-14514–enr-14519）均为 source_backed，复用既有 `haskell-1980-rev-ed`；未改 `sources.csv`。
- `st-chp2-seci-l95-106-citation-salerno` 与 `st-chp4-intro-notes-02-salerno-citation` 两条 `cites` 候选保留待 S6；书目条目本身不验证文章内容。`relations.csv` 未改动。
- 登记后 archive 类型为108组／150条候选映射已登记、1,096组／1,100条待登记；全书累计727组／897条已登记、4,054组／4,069条待登记；KU=1,746，enrichment=10,769。

<a id="s4-work-verrio-sea-triumph-20261017"></a>

### S4 work：Verrio《A Sea triumph》描述性身份组登记（2026-10-17）

- S3 身份组 `workgrp-b43402f3260265` 将索引简称候选 `cand-2762` 与正文候选 `cand-7206` 合并为一个 work KU。索引子目指向 pp.195–196 的 Verrio 王室绘画；正文称其为最早的王室绘画、“A Sea triumph”。此名称作为描述性工作题名，原文没有确认正式题名或具体作品身份。
- 第195页句子在第196页续完；Haskell 称画中有 Charles II，并评价该画奉承国王但与其统治实际关联有限。该评价保留为 Haskell 的判断；媒介、尺寸、地点、委托与存世情况未由此处确定。Antonio Verrio 与 Charles II 已各有对应人物 KU。
- 六条字段记录（enr-14520–enr-14525）均为 source_backed，复用既有 `haskell-1980-rev-ed`；未改 `sources.csv`。
- `st-chp7-p195-sea-triumph-open` 与 `st-chp7-p196-sea-triumph-description` 两条关系候选保留待 S6；不在本轮登记正式创作者或描绘对象关系。`relations.csv` 未改动。
- 登记后 work 类型为49组／55条候选映射已登记、433组／442条待登记；全书累计728组／899条已登记、4,053组／4,067条待登记；KU=1,747，enrichment=10,775。

<a id="s4-work-capture-jerusalem-titus-20261017"></a>

### S4 work：Francesco Barberini 所购《The Capture of Jerusalem by the Emperor Titus》（2026-10-17）

- S3 单成员 new 组 `workgrp-ee0cd4da4ed810`（`cand-4601`）登记为一张 work KU。Haskell 第2章 p.44 称 Francesco Barberini 从 Nicolas Poussin 处买得此画；原文只确认卖方，不据此认定 Poussin 为创作者。
- 题名按 Haskell 原文记录，中文为工作译名；题名不用于验证历史事件或画面内容。注4称一位 Barberini 红衣主教后来将画赠出（收受者“也许是 Richelieu”），并报告当时已散佚。第45页另提约十二年后的第二版本；索引候选 `cand-2001` 仍为 S3 undecided，不登记KU、不合并。
- 七条字段记录（enr-14526–enr-14532）均为 source_backed，复用既有 `haskell-1980-rev-ed`；未改 `sources.csv`。
- 五条直接 S2 关系候选（st-chp2-seciv-l6-17-purchased-capture-from-poussin, st-chp2-seciv-l6-17-capture-title-names-place-and-titus, st-chp2-seciv-l6-17-capture-title-names-titus, st-chp2-seciv-l19-29-second-capture-relative-interval, st-chp2-seciv-l190-245-lost-capture）保留待 S6；不新增正式作者、购藏、赠予、描绘或版本关系。`relations.csv` 未改动。
- 登记后 work 类型为50组／56条候选映射已登记、432组／441条待登记；全书累计729组／900条已登记、4,052组／4,066条待登记；KU=1,748，enrichment=10,782。

<a id="s3-reuse-bernini-thomas-baker-bust-20261017"></a>

### S3 复核：Thomas Baker 胸像跨章复用既有 KU（2026-10-17）

- `cand-4436` 原裁为单成员 `new` 组 `workgrp-5b3c6d0ce899cf`，现经跨章比对改为 `same`，映射至既有[贝尔尼尼的托马斯·贝克肖像胸像](../../../04-knowledge/units/works/bernini-thomas-baker-bust.md)。既有 same 候选 `cand-3182` 已指向该 KU。原 `new` 决定及组号留在 alignment 注释中作历史，不再作为待登记组。
- 第1章 p.17 将一件 6,000 scudi 的肖像胸像与 Thomas Baker 联系，并记 Haskell 当时所称 V&A 收藏（S2：`st-chp1-secii-l106-116-01b`、`st-chp1-secii-notes-bernini-prices`、`st-chp1-secii-notes-bernini-bust-vna`）。第2章 p.37 据 Nicholas Stone 的记述称 Bernini 正在雕刻 Baker 胸像，同时说明 Baker 受托把 Van Dyck 的 Charles I 三人肖像带给 Bernini（`st-chp2-secii-l62-69-nicholas-stone-baker-bust-account`）。第7章 p.179 又述 Baker 让 Bernini记录自己的面貌（`st-chp7-p179-i09`）。合并指向同一胸像；Charles I 肖像保持为另一件作品。
- 该身份判断不消除 Baker 在第1章压缩脚注中的角色歧义，也不新增或改写正式关系。现有 `rel-0452`–`rel-0454` 与其他 S2 候选交 S6 对照；本次未改 `relations.csv`、KU 卡片或 enrichment。
- 更新后 S3：same=1,894（指向1,040个既有KU）；new=4,965（4,780组）。work 类型 same=235、new=496/481组；S4 新组待登记4,051组／4,065条映射。KU=1,748，enrichment=10,782。

<a id="s3-reuse-fame-and-streit-works-20261017"></a>

### S3 work：弗兰切斯基尼《Fame》与 Amigoni 施特赖特肖像复用既有 KU（2026-10-17）

- `cand-6888` 原裁为单成员 `new` 组 `workgrp-0c379bfa64b197`，本次依据跨章／图版／对象记录改为 `same`，指向既有 [units/works/baldassare-franceschini-fame-carrying-the-name-of-louis-xiv-to-the-temple-of-immortality KU](../../../04-knowledge/units/works/baldassare-franceschini-fame-carrying-the-name-of-louis-xiv-to-the-temple-of-immortality.md). 第7章 p.187 的委托记述、第20章 Plate 66 图注及 p.402–403 跨页回指均落在同一件弗兰切斯基尼作品；Plate 66 已由既有 KU 收录。图注以 Louis XIV 具体化正文的 ‘the King’，是同一作品的题名信息，不据此拆成第二件作品。委托者仍未具名；本次不新增作者、委托或现藏关系。 旧组与理由保留在 alignment `resolution_note` 中，不再进入 S4。
- `cand-9636` 原裁为单成员 `new` 组 `workgrp-f2a47c2cb10ac4`，本次依据跨章／图版／对象记录改为 `same`，指向既有 [units/works/amigoni-sigismund-streit KU](../../../04-knowledge/units/works/amigoni-sigismund-streit.md). 第10章 p.315 正文与 Plate 53b 图注共同识别 Amigoni 所绘 Streit 肖像；p.316 正文及注3将 Amigoni 为 Streit 所绘肖像与1739年、坐像者52岁相连。既有 KU 的题注和柏林馆藏对象 obj:863940（Streit.1）对应这一单件肖像。p.316 关于四幅 Streit 肖像的句子没有逐幅指认，本裁决不把四幅作品并为一件，也不推断其余三幅身份。 旧组与理由保留在 alignment `resolution_note` 中，不再进入 S4。
- 两项均未新建 KU，也未改写卡片、enrichment 或 `relations.csv`；相应 S2 关系候选仍按既有状态交 S6。
- 更新后 S3：same=1,896（指向1,040个既有KU）；new=4,963（4,778组）。work 类型 same=237、new=494/479组；S4 新组待登记4,049组／4,063条映射。KU=1,748，enrichment=10,782。
- 复核后重跑 `python scripts/audit_tables.py --strict-stage --summary` 通过：`alignments=12,645`、`unlinked=0`、`alignment_new_pending_registration=4,063`、`errors=[]`、`s2_missing=[]`；其余 warning 为待登记 S4、既有两条 source_ref 引用及 S2 语义质量提示。
- S3 去向核对（记录完整性）：12,407 个候选各有且仅有一条决定，且都有 `process_ref` 与 `resolution_note`；same 的既有KU类型匹配，new 的4,778组无拆组或类型错配；8 conflict、5,440 undecided、100 excluded 均未误填 KU 去向，逐类型重算与本表一致。未解决的 conflict／undecided 仍按待证处理；本核对不等同独立语义验收。

<a id="s4-archive-rava-longhi-1911-20261017"></a>

### S4 archive：Rava《Contributo alla biografia di Pietro Longhi》（1911）登记（2026-10-17）

- 单成员 S3 组 `archive-group-84f06577c903`（`cand-10054`）由第13章 p.340 注3的分段引用（L219、L88）与第21章书目 p.435 L1029 对应至同一篇期刊文章；登记一个 archive KU。书目给出的刊名、卷、年份和页码均按原记载分字段录入。
- 作者仅保存书目署名 `Rava, A.`，不扩写全名，也不凭相同署名合并人物。七封 Longhi 致 Remondini 信件 `cand-10190` 是独立 archive 候选；另两篇 Rava 书目文章 `cand-10305`、`cand-6579` 保持各自 S3 身份组。文章和信件未独立查阅。
- 七条字段记录（enr-14533–enr-14539）均为 source_backed，复用既有 `haskell-1980-rev-ed`；未改 `sources.csv`。
- S2 候选 `st-chp13-p340-note3-longhi-letters-rava-publication` 保留待 S6；书目记录本身不是关系断言。`relations.csv` 未改动。
- 登记后 archive 类型为109组／151条候选映射已登记、1,095组／1,099条待登记；全书累计730组／901条已登记、4,048组／4,062条待登记；KU=1,749，enrichment=10,789。
- 登记后 `python scripts/audit_tables.py --strict-stage --summary` 通过：KU=1,749，alignment=12,645、未链接=0、待登记映射=4,062、enrichment=10,789、`errors=[]`、`s2_missing=[]`；`build_cards.py --preview --ku units/archives/rava-contributo-alla-biografia-di-pietro-longhi-1911` 无差异。


<a id="s4-person-relation-endpoints-andreosi-audran-barbarigo-20261017"></a>

### S4 person relation endpoints：Andreosi、Audran、Barbarigo（2026-10-17）

`cand-0104`、`cand-0145`、`cand-0182` 分属三个单候选 S3 身份组，分别登记为 [Francesco Andreosi](../../../04-knowledge/units/persons/francesco-andreosi.md)、[Benoit Audran](../../../04-knowledge/units/persons/benoit-audran.md)、[Caterina Barbarigo](../../../04-knowledge/units/persons/caterina-barbarigo.md)。Andreosi 只按Haskell所述预定制作角色记录，雕像候选 `cand-10484` 仍为 undecided；Audran 按第15章姓氏与同页索引全名对齐，插图组候选 `cand-10549` 仍为 undecided；Barbarigo 的1765年小册子要求为Haskell转引，代理人候选 `cand-9979` 与索引候选 `cand-1220` 仍有姓名/身份冲突。三个S2关系候选均保留待S6审查，未写入正式关系；Barbarigo引文及Gozzi身份未作外部核验。

本批登记3组/3条候选映射；累计S4已登记733组/904条，待登记4,045组/4,059条，KU=1,752。


<a id="s4-person-relation-endpoints-carrara-damini-20261017"></a>

### S4 person relation endpoints：Carrara、Damini（2026-10-17）

`cand-3497` 登记为[Conte Ventura Carrara](../../../04-knowledge/units/persons/conte-ventura-carrara.md)。Haskell第1章注2称其为一封1696年7月11日书信的收信人；S2记录OCR姓名 Quarisinini 的印刷本校正为 Quarismini，原信及Bottari刊本未独立查阅。对应archive端点复用已有KU，但正式收信关系留待S6。

`cand-0898` 登记为[Vincenzo Damini](../../../04-knowledge/units/persons/vincenzo-damini.md)。第10章称Damini为次要画家，并称其与Giacomo Leoni从Düsseldorf抵达英格兰；Leoni候选 `cand-1394` 与England候选 `cand-4439` 仍待S4，该statement不转为正式关系。

本批登记2组/2条候选映射；累计S4已登记735组/906条，待登记4,043组/4,057条，KU=1,754。


<a id="s3-reassessment-saverio-savini-gubbio-terms-20261017"></a>

### S3复核：Saverio／Salvio Savini 与Gubbio条款archive（2026-10-17）

复核`cand-2377`（Saverio Savini）与既有`units/persons/saverio-savini`、`cand-12277`（Gualandi刊布的Savini 1608 Gubbio条款）与既有`units/archives/savini-gubbio-terms-1608`。两项候选都指向第1章印刷页9注1同一来源锚点：Gubbio、1608、Saverio Savini、Gualandi卷IV第60页；既有人物卡保留书内Saverio拼写，并记录与外部来源所用Salvio Savini姓名的对齐；既有archive卡记录同一被引条款及其限制。因此前者从`new`改为`same`→既有人物KU，后者从`new`改为`same`→既有archive KU；两个旧new组号保留在alignment历史备注中，不创建重复KU。被引Gualandi刊本和原始合同本任务未另行查阅；本次只复用已有卡片中留存的身份/来源证据。S2 statement保留待S6复核，未改relations.csv。

改判后S3：same=1,898候选→1,040个既有KU；new=4,961候选/4,776组。S4累计已登记735组/906条映射，待登记4,041组/4,055条；KU=1,754。


<a id="s4-person-relation-endpoint-jan-weenix-20261017"></a>

### S4 person relation endpoint：Jan Weenix（2026-10-17）

`cand-2807` 登记为[Jan Weenix](../../../04-knowledge/units/persons/jan-weenix.md)。第10章称他与Adrian van der Werff受Johann Wilhelm邀请前往Düsseldorf；邀请不证明Weenix接受。索引全名、p.283正文锚点与S3单候选组一致；关联S2候选留待S6。Van der Werff候选 `cand-2808` 仍待S4。

本批登记1组/1条映射；累计S4已登记736组/907条，待登记4,040组/4,054条，KU=1,755。


<a id="s4-person-relation-endpoint-adrian-van-der-werff-20261017"></a>

### S4 person relation endpoint：Adrian van der Werff（2026-10-17）

`cand-2808` 登记为[Adrian van der Werff](../../../04-knowledge/units/persons/adrian-van-der-werff.md)。第10章p.283称其与Jan Weenix受Johann Wilhelm邀请，并记其拒绝正式宫廷画家职位、同意每年六个月专为选侯工作，且大量画作进入画廊。S2限定未证明Weenix接受邀请或该安排每年均履行；同段审美引文的发言者未识别。三条S2关系候选保留待S6，未新增正式边。

本批登记1组/1条映射；累计S4已登记737组/908条，待登记4,039组/4,053条，KU=1,756。


<a id="s4-person-relation-endpoint-gabriel-gruppello-20261017"></a>

### S4 person relation endpoint：Gabriel Gruppello（2026-10-17）

`cand-1236` 登记为[Gabriel Gruppello](../../../04-knowledge/units/persons/gabriel-gruppello.md)。第10章称其为Flemish雕塑家，并以其一尊青铜骑马雕像说明Düsseldorf时期艺术与Johann Wilhelm自我展示之间的联系；原文没有给出雕像日期或现存地点。对应作品候选 `cand-8951` 仍待S4；S2关系候选留待S6，未新增正式边。

本批登记1组/1条映射；累计S4已登记738组/909条，待登记4,038组/4,052条，KU=1,757。


<a id="s4-person-relation-endpoint-domenico-zanetti-20261017"></a>

### S4 person relation endpoint：Domenico Zanetti（2026-10-17）

`cand-2860` 登记为[Domenico Zanetti](../../../04-knowledge/units/persons/domenico-zanetti.md)。第10章注1称其为在Düsseldorf为选侯工作的威尼斯画家；索引提供人物全名与页码，原文后缀“de Pigage”保留未决，不并入姓名。S2列`cand-9332`为undecided，可能关联`cand-9322`，未作身份或关系判断；Haskell陈述未独立核验。S2关系候选留待S6。

本批登记1组/1条映射；累计S4已登记739组/910条，待登记4,037组/4,051条，KU=1,758。

<a id="s4-person-relation-endpoints-allegrini-antonazzi-arconato-arrighi-maffeo-bouchardon-20261018"></a>

### S4 person：六组直接关系端点身份组登记（2026-10-18）

- `cand-0084`（`new-person:allegrini-francesco-59c88290a5`）→ [弗朗切斯科·阿莱格里尼（Francesco Allegrini）](../../../04-knowledge/units/persons/francesco-allegrini.md)；S2直接关系候选 `st-chp6-p157-collection-includes-work-by-allegrini` 留待S6；该S2候选只称收藏中有Allegrini的作品，不指认单件作品或完整作品目录；关系留待S6。
- `cand-0112`（`new-person:antonazzi-antonio-maria-603399deaf`）→ [安东尼奥·玛丽亚·安东纳齐（Antonio Maria Antonazzi）](../../../04-knowledge/units/persons/antonio-maria-antonazzi.md)；S2直接关系候选 `st-chp4-sec-ii-p116note-fn3-antonazzi` 留待S6；S2记录Haskell注3所述Massimi与Antonazzi同行；目的地、日期及正式关系尚未另行确认，留待S6。
- `cand-0115`（`new-person:arconato-galeazzo-8143cc061e`）→ [加莱亚佐·阿尔科纳托（Galeazzo Arconato）](../../../04-knowledge/units/persons/galeazzo-arconato.md)；S2直接关系候选 `st-chp4-sec-ii-l91-99-arconato-reconstructed-mazenta-collection`, `st-chp4-sec-ii-l91-99-cassiano-acquaintance-of-arconato` 留待S6；收藏重建与Cassiano熟人两条S2陈述保持原文限定，均留待S6逐条裁决。
- `cand-0122`（`new-person:arrighi-landini-orazio-e060d35cff`）→ [奥拉齐奥·阿里吉-兰迪尼（Orazio Arrighi-Landini）](../../../04-knowledge/units/persons/orazio-arrighi-landini.md)；S2直接关系候选 `st-chp10-p301-note6-arrighi_pope_epitaph_report` 留待S6；所引《Tempio della Filosofia》页未查，1757/1755版次对应未决；该S2陈述留待S6，且不把墓志铭连到Newton。
- `cand-0238`（`new-person:barberini-maffeo-1c4c752e81`）→ [马费奥·巴贝里尼亲王（塔代奥之子）（Prince Maffeo Barberini (son of Taddeo Barberini)）](../../../04-knowledge/units/persons/maffeo-barberini-son-of-taddeo.md)；S2直接关系候选 `st-chp2-secvii-l32-36-maffeo-son-of-taddeo` 留待S6；Haskell直接称Maffeo为Taddeo之子；亲子关系只保留为S2候选，正式关系留待S6。
- `cand-0420`（`new-person:bouchardon-edme-6f9687ca41`）→ [埃德梅·布沙东（Edmé Bouchardon）](../../../04-knowledge/units/persons/edme-bouchardon.md)；S2直接关系候选 `st-chp14-p356-algarotti-provided-introduction-for-bouchardon` 留待S6；S2陈述未把注3的两封信与Bouchardon逐一对应；正式关系留待S6。

本批登记6个单候选S3 new人物组，每组映射至一张KU；姓名表所列名称均有索引或正文来源。Arrighi-Landini索引条目页码栏为空，登记保留这一限制；其书目版次对应仍未解决。未添加外部身份事实或formal relations；卡片中的姓名行将按来源登记为结构化字段。其余未决对象不受本批影响。

登记后人物类型S4为339组/425条已登记、729组/730条待登记；全书为745组/916条已登记、4,031组/4,045条待登记，KU=1764。

<a id="s4-person-endpoint-name-fields-20261018"></a>

### S4 结构化字段：人物端点姓名（2026-10-18）

Allegrini、Antonazzi、Arconato、Arrighi-Landini、Maffeo Barberini与Bouchardon六张人物卡的姓名表行，已按 `build_field_facts.extract_records` 解析为六条 `enrichment.jsonl` 记录；每条均保留对应索引来源引用，source_id 为既有 `haskell-1980-rev-ed`，状态为 `source_backed`。未登记生平或关系字段；关系候选仍待S6。

<a id="s4-person-relation-endpoints-bracci-burnacini-simone-bussi-cadani-calandrucci-20261018"></a>

### S3/S4 person：六组直接关系端点身份组登记（2026-10-18）

- `cand-0425`（`new-person:bracci-pietro-f76036a853`）→ [皮埃特罗·布拉奇（Pietro Bracci）](../../../04-knowledge/units/persons/pietro-bracci.md)；直接S2关系候选 `st-chp3-seciv-l179-187-bracci-made-annunciation-relief` 留待S6；作品候选cand-5455仍须按S3/S4状态处理；制作关系候选留待S6，未据此建立作品KU或正式边。
- `cand-0472`（`new-person:burnacini-lodovico-ottavio-ef7e064231`）→ [洛多维科·奥塔维奥·布尔纳奇尼（Lodovico Ottavio Burnacini）](../../../04-knowledge/units/persons/lodovico-ottavio-burnacini.md)；直接S2关系候选 `st-chp7-p193-leopold-father-summoned-burnacini` 留待S6；被指称的召请者在该段未具名；召请关系仍为S2候选，留待S6核对端点与原文范围。
- `cand-0469`（`new-person:buonaccorsi-simone-0295b5645e`）→ [西蒙·布奥纳科尔西枢机（Cardinal Simone Buonaccorsi）](../../../04-knowledge/units/persons/simone-buonaccorsi.md)；直接S2关系候选 `st-chp8-p223-francesca-mother-of-simone` 留待S6；同页索引支持将子女名单中的Simone映射到Cardinal Simone Buonaccorsi；母子谓词仍是S2候选，留待S6。
- `cand-0474`（`new-person:bussi-francesca-bfc6aa40fd`）→ [弗朗切斯卡·布西（Francesca Bussi）](../../../04-knowledge/units/persons/francesca-bussi.md)；直接S2关系候选 `st-chp8-p223-raimondo-married-francesca`、`st-chp8-p223-francesca-mother-of-simone` 留待S6；婚姻对象在对应S2候选中为cand-0467；Simone现按同页索引对齐至cand-0469。两项关系均留待S6，不添加其他家族分支主张。
- `cand-0476`（`new-person:cadani-stefano-ec786fc4ba`）→ [斯特法诺·卡达尼（Stefano Cadani）](../../../04-knowledge/units/persons/stefano-cadani.md)；直接S2关系候选 `st-chp7-p194-cadani-employed-dresden` 留待S6；雇用陈述留待S6；该句后注1未查，未据此增加雇用起始日或其他任职信息。
- `cand-0481`（`new-person:calandrucci-giacinto-de37a3f605`）→ [贾钦托·卡兰德鲁奇（Giacinto Calandrucci）](../../../04-knowledge/units/persons/giacinto-calandrucci.md)；直接S2关系候选 `st-chp7-p197-exeter-collected-calandrucci-rome` 留待S6；p.197清单为概括性城市—画家列举，没有指认单件作品或具体交易；关联候选留待S6。

#### S3补充复核：Cardinal Simone Buonaccorsi同页身份映射

第8章p.223称Francesca Bussi的十八名子女之一Simone将成为枢机；索引B.csv#317同页列出“Buonaccorsi, Cardinal Simone”。cand-0469既有new组保持不变；本次补记该书内mention-to-index身份对应，S2的母子关系候选仍待S6。未访问外部身份记录。

六个S3单候选new人物组各登记为一张KU；六条原文全名/索引名字段均从卡片表提取并另行登记。未新增formal relations；其他冲突、未决和待登记组保持原状态。

登记后人物类型S4为345组/431条已登记、723组/724条待登记；全书为751组/922条已登记、4,025组/4,039条待登记，KU=1770。

<a id="s4-person-endpoint-name-fields-bracci-burnacini-simone-bussi-cadani-calandrucci-20261018"></a>

### S4 结构化字段：第二批人物端点姓名（2026-10-18）

Pietro Bracci、Lodovico Ottavio Burnacini、Cardinal Simone Buonaccorsi、Francesca Bussi、Stefano Cadani与Giacinto Calandrucci六张人物卡的姓名表行，按 `build_field_facts.extract_records` 登记为六条 `enrichment.jsonl` 记录，均引用既有索引来源 `haskell-1980-rev-ed` 且标记 `source_backed`。本批不登记生平或正式关系字段。

<a id="s3-simone-buonaccorsi-same-page-identity-20261018"></a>

### S3补充：Simone Buonaccorsi同页身份映射落入陈述限定（2026-10-18）

对 `st-chp8-p223-francesca-eighteen-children`、`st-chp8-p223-francesca-mother-of-simone` 与 `st-chp8-p223-simone-cardinal` 的 `qualification` 更新，保留正文只写Simone、人数及将成为枢机的时态，并记录S3依据同一印刷页上的索引B.csv#317映射至cand-0469。mother_of仍为S2候选，留待S6；该对齐仅属书内证据，不表示外部身份核验或正式关系成立。

<a id="s4-person-direct-endpoints-cambiaso-campanella-campbell-campione-cappello-polidoro-20261017"></a>

### S4人物：六组直接关系端点身份组登记（2026-10-17）

- `cand-0488`（`new-person:cambiaso-luca-7e46c6cf0e`）→ [卢卡·坎比亚索（Luca Cambiaso）](../../../04-knowledge/units/persons/luca-cambiaso.md)；S2直接关系候选 `st-chp2-seci-l95-106-cambiaso-collection`, `st-chp2-seci-l95-106-lighting-comparison` 留待S6；作品归属候选指向原文所述的一组未逐件识别的收藏画作；照明比较保留“可能”限定。两项均留待S6，不创建正式关系。
- `cand-0491`（`new-person:campanella-tommaso-08b48e27fb`）→ [托马索·坎帕内拉（Tommaso Campanella）](../../../04-knowledge/units/persons/tommaso-campanella.md)；S2直接关系候选 `st-chp2-secii-l147-193-campanella-urban-research`, `st-chp2-secii-l147-193-campanella-surveillance` 留待S6；帮助Urban VIII研究与Barberini下令监视Campanella均为注释转述；引文来源未独立查阅，保持S2限定并留待S6。
- `cand-0493`（`new-person:campbell-colen-dc5c057058`）→ [科伦·坎贝尔（Colen Campbell）](../../../04-knowledge/units/persons/colen-campbell.md)；S2直接关系候选 `st-chp10-p309-two-pictures-after-campbell` 留待S6；该候选指两幅画描绘Campbell的作品，不表示Campbell本人绘制这两幅画；正式关系留待S6。
- `cand-0494`（`new-person:campione-da-giovanni-587cbff61c`）→ [乔瓦尼·达·坎皮奥内（Giovanni da Campione）](../../../04-knowledge/units/persons/giovanni-da-campione.md)；S2直接关系候选 `st-chp8-p215-campione-erected-gothic-portico-1355`, `st-chp8-p215-campione-built-south-entrance` 留待S6；门廊与南入口是两项不同建造陈述；后一项只给出“数年后”，不补出确切年份。两项关系均留待S6。
- `cand-0537`（`new-person:antonio-cappello-17b238059e`）→ [安东尼奥·卡佩洛（Antonio Cappello）](../../../04-knowledge/units/persons/antonio-cappello.md)；S2直接关系候选 `st-chp15-p367-canova-statue-commissioned-by-cappello-from-ferrari` 留待S6；S2陈述是Cappello委托Ferrari制作Canova雕像，不是Cappello直接委托Canova创作；正式关系留待S6。
- `cand-0553`（`new-person:caravaggio-da-polidoro-2585cffaf3`）→ [波利多罗·达·卡拉瓦乔（Polidoro da Caravaggio）](../../../04-knowledge/units/persons/polidoro-da-caravaggio.md)；S2直接关系候选 `st-chp8-p210-ruffo-interest-in-polidoro-da-caravaggio` 留待S6；第8章S2候选为Ruffo对Polidoro的兴趣，保留纸本校正及原文范围；第5章仅用作跨章身份锚点。本批不创建正式关系，候选留待S6。

本批登记6个单候选S3 new人物组，每组映射至一张KU；姓名字段均由书内索引或正文支持。Polidoro da Caravaggio的cand-0553由第5章与第8章的全名提及组成跨章身份锚点。本批没有加入外部身份事实或formal relations；其余未决与冲突对象保持原有去向。

登记后人物类型S4为351组/437条已登记、717组/718条待登记；全书为757组/928条已登记、4,019组/4,033条待登记，KU=1776。

<a id="s4-person-endpoint-name-fields-cambiaso-campanella-campbell-campione-cappello-polidoro-20261017"></a>

### S4结构化字段：六个人物端点姓名（2026-10-17）

Luca Cambiaso、Tommaso Campanella、Colen Campbell、Giovanni da Campione、Antonio Cappello与Polidoro da Caravaggio六张人物卡的姓名表行，按 build_field_facts.extract_records 登记为六条enrichment.jsonl记录，均引用既有索引来源 haskell-1980-rev-ed 并标记 source_backed。本批不登记生平或正式关系字段。

<a id="s4-person-direct-endpoints-canal-carpioni-carracci-catalano-cavagna-cavallino-20261017"></a>

### S4人物：六组直接关系端点身份组登记（2026-10-17）

- `cand-0495`（`new-person:canal-fabio-1d5b97c563`）→ [法比奥·卡纳尔（Fabio Canal）](../../../04-knowledge/units/persons/fabio-canal.md)；S2直接关系候选 `st-chp9-p254-note2-molmenti-fabio-canal-attribution` 留待S6；本项是Haskell注释对Molmenti归属说的转述，非本项目独立确认的作者归属；S2校正OCR“Mohnenti”为Molmenti。保留为S2候选，留待S6。
- `cand-0575`（`new-person:carpioni-giulio-9a3210b9f2`）→ [朱利奥·卡尔皮奥尼（Giulio Carpioni）](../../../04-knowledge/units/persons/giulio-carpioni.md)；S2直接关系候选 `st-chp19-p393-1789-carpioni-pictures-attribution` 留待S6；拍卖记录及作品归属是Haskell转述的未核目录信息；不据此新增正式创作关系，S2候选留待S6。
- `cand-0580`（`new-person:carracci-ludovico-13430870c0`）→ [卢多维科·卡拉奇（Ludovico Carracci）](../../../04-knowledge/units/persons/ludovico-carracci.md)；S2直接关系候选 `st-chp5-note-p123-n2-ludovico-letters` 留待S6；S2候选描述Nicodemi发表书信的书目记录，出版物未独立查阅；后记异拼只作为跨章身份锚点。本批不创建正式关系，候选留待S6。
- `cand-0608`（`new-person:catalano-francesco-89bacc7e59`）→ [弗朗切斯科·卡塔拉诺（Francesco Catalano）](../../../04-knowledge/units/persons/francesco-catalano.md)；S2直接关系候选 `st-chp5-notes-l136-swanevelt-catalano-case` 留待S6；该S2候选保留Haskell对Bertolotti的转述和“被指控”状态；不把指控写成既定事实，正式关系留待S6。
- `cand-0611`（`new-person:cavagna-giampaolo-81fd593733`）→ [吉安保罗·卡瓦尼亚（Giampaolo Cavagna）](../../../04-knowledge/units/persons/giampaolo-cavagna.md)；S2直接关系候选 `st-chp8-p215-cavagna-dome-frescoes-1614` 留待S6；该候选指Cavagna与两位未具名协作者共同完成的一组穹顶壁画，不推定协作者身份；候选留待S6。
- `cand-0613`（`new-person:bernardo-cavallino-27645d6985`）→ [贝尔纳多·卡瓦利诺（Bernardo Cavallino）](../../../04-knowledge/units/persons/bernardo-cavallino.md)；S2直接关系候选 `st-chp8-p208-de-dominici-cavallino-affect` 留待S6；影响关系来自Haskell对de Dominici的转述，原始文本未查；保留转述与纸本校正限定，正式关系留待S6。

本批登记6个单候选S3 new人物组，每组映射至一张KU；姓名、来源锚点与候选关系均逐项对应。Fabio Canal与Canaletto因完整姓名不同而分卡，不据共有姓氏合并；Carracci的Ludovico/Lodovico异拼按S3全名组保留；Carpioni拍卖归属、Catalano盗窃指控、Cavagna未具名协作者及Cavallino转引来源的限定均保留。本批没有添加外部身份事实或formal relations。

登记后人物类型S4为357组/443条已登记、711组/712条待登记；全书为763组/934条已登记、4,013组/4,027条待登记，KU=1782。

<a id="s4-person-endpoint-name-fields-canal-carpioni-carracci-catalano-cavagna-cavallino-20261017"></a>

### S4结构化字段：六个人物端点姓名（2026-10-17）

Fabio Canal、Giulio Carpioni、Ludovico Carracci、Francesco Catalano、Giampaolo Cavagna与Bernardo Cavallino六张人物卡的姓名表行，按 build_field_facts.extract_records 登记为六条enrichment.jsonl记录，均引用既有索引来源 haskell-1980-rev-ed 并标记 source_backed。本批不登记生平或正式关系字段。

<a id="s4-person-direct-endpoints-ceruti-cesi-champaigne-charles-chiarini-chigi-20261017"></a>

### S4人物：六组直接关系端点身份组登记（2026-10-17）

- `cand-0637`（`new-person:ceruti-giacomo-435ed1cd37`）→ [贾科莫·切鲁蒂（Giacomo Ceruti）](../../../04-knowledge/units/persons/giacomo-ceruti.md)；S2直接关系候选 `st-chp10-p312-ceruti-painted-portraits-of` 留待S6；Haskell只列出肖像画家，没有给出具体作品题名；该S2候选留待S6。
- `cand-0641`（`new-person:cesi-federico-5a8ec02660`）→ [费德里科·切西亲王（Prince Federico Cesi）](../../../04-knowledge/units/persons/prince-federico-cesi.md)；S2直接关系候选 `st-chp4-sec-ii-l232-308-cesi-died-1630`, `st-chp4-sec-ii-l232-308-cesi-identified-as-founder` 留待S6；创办者身份与1630年卒年均按Haskell书内陈述记录，未作外部传记核验；两项S2候选留待S6。
- `cand-0643`（`new-person:champaigne-de-philippe-bec5499e28`）→ [菲利普·德·尚佩涅（Philippe de Champaigne）](../../../04-knowledge/units/persons/philippe-de-champaigne.md)；S2直接关系候选 `st-chp7-p175-i04` 留待S6；影响说是对研究者判断的转述，不等同师承或单件作品影响；保留S2限定，候选留待S6。
- `cand-0659`（`new-person:charles-of-sweden-xii-22ffb5a1d4`）→ [瑞典国王卡尔十二世（Charles XII of Sweden）](../../../04-knowledge/units/persons/charles-xii-of-sweden.md)；S2直接关系候选 `st-chp10-p311-schulenburg-fought-for-saxons-against-charles-xii` 留待S6；S2记录Schulenburg为萨克森一方与Charles XII交战的书内叙述；“晚年谈起”亦保留为Haskell转述，候选留待S6。
- `cand-0662`（`new-person:chiarini-marcantonio-92d65d97a6`）→ [马尔坎托尼奥·基亚里尼（Marc’antonio Chiarini）](../../../04-knowledge/units/persons/marcantonio-chiarini.md)；S2直接关系候选 `st-chp7-p200-v-chiarini-frescoes-daun-palace` 留待S6；宫殿壁画归属保留Haskell原文范围，不补入年代、房间或题材；正式关系留待S6。
- `cand-0663`（`new-person:agostino-chigi-il-magnifico-8646b69f00`）→ [阿戈斯蒂诺·基吉（il Magnifico）（Agostino Chigi ‘il Magnifico’）](../../../04-knowledge/units/persons/agostino-chigi-il-magnifico.md)；S2直接关系候选 `st-chp6-p150-agostino-raphael-friendship`, `st-chp6-p150-fabio-descended-from-agostino` 留待S6；Raphael友谊的“传奇”表述和Fabio Chigi直系后裔关系均为Haskell书内叙述，未外部核验；两项S2候选留待S6。

本批登记6个单候选S3 new人物组；身份依据限于书内姓名、索引定位及相应来源段。Champaigne的OCR异拼、Cesi的书内生卒/创办者陈述、Chigi的谱系与评价以及其余端点的限定均保留；本批没有添加外部身份事实或formal relations。

登记后人物类型S4为363组/449条已登记、705组/706条待登记；全书为769组/940条已登记、4,007组/4,021条待登记，KU=1788。

<a id="s4-person-endpoint-name-fields-ceruti-cesi-champaigne-charles-chiarini-chigi-20261017"></a>

### S4结构化字段：六个人物端点姓名（2026-10-17）

Giacomo Ceruti、Prince Federico Cesi、Philippe de Champaigne、Charles XII of Sweden、Marc’antonio Chiarini与Agostino Chigi ‘il Magnifico’六张人物卡的姓名表行，按build_field_facts.extract_records登记为六条enrichment.jsonl记录，均引用既有索引来源haskell-1980-rev-ed并标记source_backed。本批不登记生平或正式关系字段。

<a id="s4-person-direct-endpoints-ciarpi-castello-conduitt-corelli-corradini-coypel-20261017"></a>

### S4人物：六组直接关系端点身份组登记（2026-10-17）

- `cand-0745`（`new-person:baccio-ciarpi-ed3407fcf7`）→ [巴乔·恰尔皮（Baccio Ciarpi）](../../../04-knowledge/units/persons/baccio-ciarpi.md)；S2直接关系候选 `st-chp2-secii-l141-145-ciarpi-master-of-pietro`, `st-chp2-secii-l141-145-baccio-ciarpi-paintings-contributed` 留待S6；师承说按Haskell书内叙述保留；祭坛画只指一组未逐件识别的作品，不推定具体画作。两项候选留待S6。
- `cand-0766`（`new-person:castello-citta-da-di-matteo-8b25099440`）→ [马泰奥·达·卡斯泰洛（Matteo da Castello）](../../../04-knowledge/units/persons/matteo-da-castello.md)；S2直接关系候选 `st-chp3-secii-l33-38-philip-worked-with-oratorian-chosen-matteo`, `st-chp3-secii-l40-52-longhi-replaces-matteo` 留待S6；建筑师由Oratorians选定、与Philip Neri合作，并由Longhi接任；均保留来源角色限定，候选留待S6。
- `cand-0820`（`new-person:conduitt-john-1595bc5af5`）→ [约翰·康杜伊特（John Conduitt）](../../../04-knowledge/units/persons/john-conduitt.md)；S2直接关系候选 `st-chp10-p290-note1-letter-direction`, `st-chp10-p304-note4-conduitt-procurement-request` 留待S6；1729年致McSwiny信与1730年代购引文之间的内部引用不吻合；信件身份和出处未决，两项S2候选均留待S6。
- `cand-0843`（`new-person:arcangelo-corelli-ed47e21c49`）→ [阿尔坎杰洛·科雷利（Arcangelo Corelli）](../../../04-knowledge/units/persons/arcangelo-corelli.md)；S2直接关系候选 `st-chp6-p165-n3-europa`, `st-chp6-p165-n3-friend` 留待S6；友谊为Haskell注释所述；Ricci作品仅称Europa且库存目录未查，作品身份未决。两项候选留待S6。
- `cand-0849`（`new-person:antonio-corradini-f5fd2d8463`）→ [安东尼奥·科拉迪尼（Antonio Corradini）](../../../04-knowledge/units/persons/antonio-corradini.md)；S2直接关系候选 `st-chp10-p312-corradini-sculpted-portraits-of` 留待S6；Haskell只列出肖像雕塑家，没有给出具体作品题名；该S2候选留待S6。
- `cand-0866`（`new-person:antoine-coypel-d0089dab93`）→ [安托万·柯佩尔（Antoine Coypel）](../../../04-knowledge/units/persons/antoine-coypel.md)；S2直接关系候选 `st-chp10-p285-carriera-met-coypel` 留待S6；S2只将Coypel列入集体名单，没有提供单独会面的细节；候选留待S6。

本批登记6个单候选S3 new人物组，每组映射至一张KU。Conduitt的1729/1730内部引用差异、Corelli作品题名与OCR异拼、其余对象的来源范围均保留；本批没有添加外部身份事实或formal relations。

登记后人物类型S4为369组/455条已登记、699组/700条待登记；全书为775组/946条已登记、4,001组/4,015条待登记，KU=1794。

<a id="s4-person-endpoint-name-fields-ciarpi-castello-conduitt-corelli-corradini-coypel-20261017"></a>

### S4结构化字段：六个人物端点姓名（2026-10-17）

Baccio Ciarpi、Matteo da Castello、John Conduitt、Arcangelo Corelli、Antonio Corradini与Antoine Coypel六张人物卡的姓名表行，按build_field_facts.extract_records登记为六条enrichment.jsonl记录，均引用既有索引来源haskell-1980-rev-ed并标记source_backed。本批不登记生平或正式关系字段。

<a id="s4-person-endpoints-crescenzi-curli-dingley-errard-falcone-fanzago-20261017"></a>

### S4人物：六组身份组登记（2026-10-17）

- `cand-0870`（`new-person:crescenzi-paolo-pietro-b4e83b9a13`）→ [彼得罗·保罗·克雷申齐（Pietro Paolo Crescenzi）](../../../04-knowledge/units/persons/pietro-paolo-crescenzi.md)；S2直接关系候选 `st-chp7-p173-i05`, `st-chp7-p173-i08` 留待S6；Haskell以“both”概括两兄弟早期雇用Claude及支持西班牙事业；S2将相关陈述映射到本候选，但正文未明写Pietro Paolo。索引身份与该指代不作等同断言，两项候选留待S6。
- `cand-0896`（`new-person:curli-girolamo-e60c7adef7`）→ [吉罗拉莫·库尔利（Girolamo Curli）](../../../04-knowledge/units/persons/girolamo-curli.md)；S2直接关系候选 `st-chp14-p357-note1-letter-addressed-to-curli` 留待S6；日期、收信人及刊布信息来自Haskell的书目注释；信件与Neri刊本未独立查阅，S2候选留待S6。
- `cand-0921`（`new-person:dingley-robert-65504f2aee`）→ [罗伯特·丁格利（Robert Dingley）](../../../04-knowledge/units/persons/robert-dingley.md)；S2直接关系候选 `st-chp10-p303-dingley-requested-similar-picture` 留待S6；该请求经Haskell转述自书信；没有依据称Carriera完成了所请求的画作，S2候选留待S6。
- `cand-0979`（`new-person:charles-errard-5bced1ab85`）→ [夏尔·埃拉尔（Charles Errard）](../../../04-knowledge/units/persons/charles-errard.md)；S2直接关系候选 `st-chp4-sec-ii-l91-99-errard-embellished-drawings-and-poussin-objected` 留待S6；背景装饰与Poussin的批评均为Haskell转述；“gauches”是被转述的评价，不作客观判断，S2候选留待S6。
- `cand-0987`（`new-person:aniello-falcone-05afc5f58e`）→ [阿涅洛·法尔科内（Aniello Falcone）](../../../04-knowledge/units/persons/aniello-falcone.md)；S2直接关系候选 `st-chp8-p206-falcone-painted-battle-scenes-for-roomer` 留待S6；Haskell称Falcone为Roomer绘制若干战斗场景；短语并非正式题名，数量不明，S2候选留待S6。
- `cand-0994`（`new-person:cosimo-fanzago-0ba0e98418`）→ [科西莫·范扎戈（Cosimo Fanzago）](../../../04-knowledge/units/persons/cosimo-fanzago.md)；S2直接关系候选 `st-chp7-p172-cont-i08` 留待S6；“this”指Finelli获得更大装饰份额的安排；书中没有交代正式争端或结局，S2候选留待S6。

本批登记6个单候选S3 new人物组，每组映射一张KU。姓名结构化字段仅登记索引主项；没有新增外部身份事实或formal relations。Pietro Paolo Crescenzi的正文身份指代与索引条目的对应仍未确认，故卡片仅登记索引人物并保留S2候选；Curli的书信刊本未独立查阅；Dingley请求的画作未证明完成；Errard引文保留OCR与扫描校读差异；Falcone场景短语不是已证实题名；Fanzago段落不证明正式争端或结果。

登记后人物类型S4为375组/461条已登记、693组/694条待登记；全书为781组/952条已登记、3,995组/4,009条待登记，KU=1800。

<a id="s4-person-endpoint-name-fields-crescenzi-curli-dingley-errard-falcone-fanzago-20261017"></a>

### S4结构化字段：六个人物索引名（2026-10-17）

Pietro Paolo Crescenzi、Girolamo Curli、Robert Dingley、Charles Errard、Aniello Falcone与Cosimo Fanzago六张人物卡各登记一条索引名enrichment记录，均引用既有索引来源haskell-1980-rev-ed并标记source_backed。该字段记录索引主项，不把索引位置扩展为未经核实的书内指代或关系事实。

<a id="s3-reassessment-barelli-index-subentries-20261017"></a>

### S3复核：Agostino Barelli 的两个索引子项并入同一人物组（2026-10-17）

`cand-0244`（B.csv#91，Theatine church in Munich）原为undecided；现与`cand-0243`（B.csv#90，palace at Nymphenburg）归入同一new组`new-person:agostino-barelli-5bf161332b`。依据是两行索引的规范主项均为“Barelli, Agostino”，页码均为193，且第7章p.193同一句明确点名Agostino Barelli，并分别叙述Theatines教堂与Nymphenburg宫中央建筑。两个子项是同一人物的索引定位，不是两个新人物；旧undecided状态及理由保留在alignment行并由本裁决覆盖。待登记组数不变，待登记候选映射增加1条。

<a id="s4-person-endpoints-assereto-barelli-baretti-bartoli-basadonna-bassi-20261017"></a>

### S4人物：六组直接关系端点登记（2026-10-17）

- `cand-0143`（`new-person:assereto-gioacchino-c4b08a3476`）→ [焦阿基诺·阿塞雷托（Gioacchino Assereto）](../../../04-knowledge/units/persons/gioacchino-assereto.md)；S2直接关系候选 `st-chp7-p197-exeter-collected-assereto-genoa` 留待S6；Haskell的列表将Assereto與Exeter在Genoa的收藏相连，但没有指出具体作品或交易性质；S2候选留待S6。
- `cand-0243`、`cand-0244`（`new-person:agostino-barelli-5bf161332b`）→ [阿戈斯蒂诺·巴雷利（Agostino Barelli）](../../../04-knowledge/units/persons/agostino-barelli.md)；S2直接关系候选 `st-chp7-p193-barelli-nymphenburg`, `st-chp7-p193-barelli-theatine-church` 留待S6；同一句分别指认Theatines教堂与Nymphenburg宫中央部分；不扩展为建造整座宫殿，两个S2候选留待S6。
- `cand-0245`（`new-person:baretti-giuseppe-aa0168e566`）→ [朱塞佩·巴雷蒂（Giuseppe Baretti）](../../../04-knowledge/units/persons/giuseppe-baretti.md)；S2直接关系候选 `st-chp10-p318-baretti-expelled-from-venetian-territory`, `st-chp10-p328-baretti-wrote-enthusiastically-of-zuccarelli` 留待S6；逐出威尼斯领土为Haskell的概括；关于Zuccarelli的赞语由Haskell转引Baretti，所引原信未查。两项S2候选留待S6。
- `cand-0251`（`new-person:bartoli-pietro-santo-29a748b5ca`）→ [彼得罗·桑托·巴托利（Pietro Santo Bartoli）](../../../04-knowledge/units/persons/pietro-santo-bartoli.md)；S2直接关系候选 `st-chp4-sec-ii-p118-bartoli-copied-illustrations`, `st-chp4-sec-ii-p117note-fn2-bartoli-authorship` 留待S6；手稿未逐件识别；注2所列160幅图样及作者归属保留为Haskell的书目陈述，不扩展作品清单。两项S2候选留待S6。
- `cand-0254`（`new-person:basadonna-pietro-a1f78c71c6`）→ [枢机彼得罗·巴萨多纳（Cardinal Pietro Basadonna）](../../../04-knowledge/units/persons/pietro-basadonna.md)；S2直接关系候选 `st-chp6-p162-v1-24`, `st-chp6-p162-n7-tomb` 留待S6；卧室内容为Haskell转述的法国使节说法，保留作者限定；墓与半身像的雕塑者未具名。两项S2候选留待S6。
- `cand-0259`（`new-person:bassi-francesco-cremonese-il-6c7c921364`）→ [弗朗切斯科·巴西（il Cremonese）（Francesco Bassi (il Cremonese)）](../../../04-knowledge/units/persons/francesco-bassi-il-cremonese.md)；S2直接关系候选 `st-chp8-p228-bassi-blindness`, `st-chp8-p233-bassi-loyalty` 留待S6；失明说为Haskell转述Marchesini；忠诚动机明确为Haskell推测，作品价值疑虑也保留为来源判断。两项S2候选留待S6。

本批登记6个S3 new人物身份组、7条候选映射；Barelli两条同名索引子项按S3裁决共用一张KU。姓名结构化字段仅登记索引主项；本批不添加外部身份事实或formal relations。Assereto全名来自同页索引；Barelli建筑范围、Baretti转引、Bartoli的OCR校正与作品范围、Basadonna的使节转述限定及Bassi的转述/推测语气均按来源保留。

登记后人物类型S4为381组/468条已登记、687组/688条待登记；全书为787组/959条已登记、3,989组/4,003条待登记，KU=1806。

<a id="s4-person-endpoint-name-fields-assereto-barelli-baretti-bartoli-basadonna-bassi-20261017"></a>

### S4结构化字段：六个人物索引名（2026-10-17）

Gioacchino Assereto、Agostino Barelli、Giuseppe Baretti、Pietro Santo Bartoli、Cardinal Pietro Basadonna与Francesco Bassi (il Cremonese)六张人物卡各登记一条索引名enrichment记录，均引用既有索引来源haskell-1980-rev-ed并标记source_backed。Barelli姓名行同时引用两个索引子项；本批不写入生平或formal relations字段。

<a id="s4-person-endpoints-bencovich-borzone-bossuet-breughel-brusasorci-buckingham-20261017"></a>

### S4人物：六组直接关系端点登记（2026-10-17）

- `cand-0286`（`new-person:bencovich-federico-1928910f49`）→ [费德里科·本科维奇（Federico Bencovich）](../../../04-knowledge/units/persons/federico-bencovich.md)；S2直接关系候选 `st-chp10-p278-bencovich-followed-to-vienna` 留待S6；“there”指Vienna；“them”的复数先行词未确定，不推断雇用关系或群体归属，S2候选留待S6。
- `cand-0410`（`new-person:borzone-francesco-26c9abc1e6`）→ [弗朗切斯科·博尔佐内（Francesco Borzone）](../../../04-knowledge/units/persons/francesco-borzone.md)；S2直接关系候选 `st-chp7-p189-i05` 留待S6；“新王朝初年”保留原文宽泛时间范围；受雇记录为Haskell转述并引Soprani，候选留待S6。
- `cand-0415`（`new-person:benigne-bossuet-jacques-a6e63d1549`）→ [雅克-贝尼涅·博须埃（Jacques-Bénigne Bossuet）](../../../04-knowledge/units/persons/jacques-benigne-bossuet.md)；S2直接关系候选 `st-chp13-p334-bossuet-interest-and-heresy-context` 留待S6；该关联为Haskell对书籍出版背景的历史解释，不作独立事实核验，S2候选留待S6。
- `cand-0448`（`new-person:abram-breughel-becae77cfc`）→ [阿布拉姆·勃鲁盖尔（Abram Breughel）](../../../04-knowledge/units/persons/abram-breughel.md)；S2直接关系候选 `st-chp8-p210-breughel-reported-rembrandt-reception-1665` 留待S6；对Rembrandt绘画评价为Haskell转述Breughel的书信；“here”范围未定，Haskell关于其并非虚伪亦是作者判断，S2候选留待S6。
- `cand-0460`（`new-person:brusasorci-felice-7846e65690`）→ [费利切·布鲁萨索尔奇（Felice Brusasorci）](../../../04-knowledge/units/persons/felice-brusasorci.md)；S2直接关系候选 `st-chp8-p216-massimo-pupil-of-brusasorci`, `st-chp8-p216-brusasorci-described-as-veronese` 留待S6；师生说按Haskell书内叙述保留，不补入训练地点或日期；Veronese不转换为出生地/居住地事实。两项S2候选留待S6。
- `cand-0464`（`new-person:buckingham-charles-of-villiers-25a2484d8a`）→ [查尔斯·维利尔斯（白金汉公爵）（Charles Villiers, Duke of Buckingham）](../../../04-knowledge/units/persons/charles-villiers-duke-of-buckingham.md)；S2直接关系候选 `st-chp7-p178-i10` 留待S6；Haskell将Charles与白金汉公爵并列为欢迎者，但不指定具体发起者；完整姓名由同页索引提供，S2候选留待S6。

本批登记6个单候选S3 new人物组，每组映射一张KU。人物全名以正文或同页索引为锚；Bencovich指代、Borzone年代、Bossuet历史解释、Breughel引文范围、Brusasorci地域修饰与Buckingham公爵姓名来源均保留限定。本批不添加外部身份事实或formal relations。

登记后人物类型S4为387组/474条已登记、681组/682条待登记；全书为793组/965条已登记、3,983组/3,997条待登记，KU=1812。

<a id="s4-person-endpoint-name-fields-bencovich-borzone-bossuet-breughel-brusasorci-buckingham-20261017"></a>

### S4结构化字段：六个人物索引名（2026-10-17）

Federico Bencovich、Francesco Borzone、Jacques-Bénigne Bossuet、Abram Breughel、Felice Brusasorci与Charles Villiers, Duke of Buckingham六张人物卡各登记一条索引名enrichment记录，均引用既有索引来源haskell-1980-rev-ed并标记source_backed。本批不写入生平或formal relations字段。

<a id="s3-person-admiral-binchs-byng-identity-20261017"></a>

### S3人物身份组复核：‘Binchs’与Admiral Byng（2026-10-17）

`cand-0475`（B.csv#323，索引‘Byng, Admiral’，p.200n）与`cand-7301`（正文来源拼写‘English Admiral ‘Binchs’’）均保留`new`，现归入同一身份组`new-person:admiral-byng-817cd89b59`。第7章p.200正文称Paolo de Matteis在那不勒斯被攻占后为English Admiral ‘Binchs’工作；该句注号5。已渲染的CHP-7.pdf物理第38页扫描确认注5明言‘Binchs’ must be Admiral Byng，并称其自1718年起为地中海英国舰队司令；同注报告‘Binchs’于1719年已回那不勒斯。直接原文依据是Haskell的书内识别，足以把这两个书内名称候选归为一个source-local人物组；它不是外部身份核验，也不补出索引未提供的名字。原来因脚注尚未迁入而将cand-7301单列的理由已被注5的现行证据取代；旧组号保留为`prior_group_id=new-person:admiral-binchs-admiral-binchs-english-a1fee8a9dc`。

`st-chp7-p200-n5-binchs-identified-byng`仅作为S3身份依据，不作为实质关系边，已从S6关系候选中明确关闭；‘1719年回那不勒斯’、自1718年任舰队司令及de Matteis为其工作三项原书陈述仍保留为关系/履历候选，留待S6逐条审查。本次没有外部来源核验、没有新增formal relation。S3 new候选数不变，身份组减少1；待登记组减少1，待登记成员候选数不变。

<a id="s4-person-admiral-byng-identity-group-20261017"></a>

### S4人物：Admiral Byng身份组登记（2026-10-17）

`cand-0475`与`cand-7301`共用S3身份组`new-person:admiral-byng-817cd89b59`，登记为一个人物KU：[拜恩海军上将（Admiral Byng）](../../../04-knowledge/units/persons/admiral-byng.md)。卡片分别记录索引名‘Byng, Admiral’与正文来源拼写‘Admiral ‘Binchs’’；注5对两者的识别作为Haskell的推断保留，未写作外部核验结论。两条名称字段各有对应索引或正文证据。S2关系/履历候选`st-chp7-p200-n5-binchs-return-naples`, `st-chp7-p200-n5-byng-fleet-command`, `st-chp7-p200-v-paolo-works-for-binchs-and-daun`留待S6；`st-chp7-p200-n5-binchs-identified-byng`已在S3作为身份证据关闭，不进入formal relations。

本批登记1个S3 new人物组、2条候选映射；不添加外部身份事实或formal relations。登记后人物类型S4为388组/476条已登记、679组/680条待登记；全书为794组/967条已登记、3,981组/3,995条待登记，KU=1813。

<a id="s3-reconcile-cesi-sibling-identity-and-title-only-rationales-20261017"></a>

### S3跨章身份组复核：Angelo Cesi 与头衔型人物理由更正（2026-10-17）

#### Cesi身份组

将`cand-0639`（C.csv#163；索引页69、70、400）与`cand-10945`（后记p.400来源候选）重新归为同一组`new-person:angelo-cesi-d4e25faff9`。第3章p.69称Angelo Cesi为Cardinal Pier Donato的兄弟及托迪主教；后记p.400称Monsignor Angelo Cesi为Cardinal Cesi的兄弟。两处都指向同一兄弟身份。Treccani DBI条目“CESI, Angelo”将其识别为托迪主教；条目称1586年枢机任命推荐未成功，并记其1606年去世；该文还称他与兄弟Pier Donato共同资助Vallicella教堂。来源：[Luigi Cajani, ‘CESI, Angelo’, Dizionario Biografico degli Italiani, vol. 24 (1980)](https://www.treccani.it/enciclopedia/angelo-cesi_res-9e027433-87ea-11dc-8e9d-0016357eee51_(Dizionario-Biografico)/)，访问于2026-10-17。由此，第3章p.70的‘Cardinal Angelo’及‘1606年Cardinal Cesi去世’可映射到同一Angelo Cesi，但书内枢机头衔与DBI不符；此头衔冲突保留为来源问题，不据以拆出第三个人，也不把书内身份判断当作外部事实。旧拆分组号`new-person:angelo-cesi-monsignor-20261017`保留在cand-10945的alignment历史字段；被纠正的旧裁决记录如下：

- `cand-0639`旧注：source_ref=candidate=cand-0639;index_entry=C.csv#163;index_pages=69,70,400; group=new-person:angelo-cesi-d4e25faff9; S3 cross-chapter review 2026-10-17: retain as a source-local person group for Cardinal Angelo Cesi, named in chapter 3, pp.69–70. The postscript, p.400, separately names Monsignor Angelo Cesi as the Cardinal's brother; the brother is cand-10945 and is no longer grouped here. The index page locator is not identity evidence for merging the two brothers. Previous same-name grouping rationale superseded; see S3-cross-chapter-groups-2026-10-17. No existing same-type person KU matched; S4 registration pending.
- `cand-10945`旧注：source_ref=candidate=cand-10945;candidate_source_ref=chp-20:20_CHP-20Postscript:l46-57#L53; source_file=02-sources/02-Markdown/20_CHP-20Postscript.md#L46-57; s2_mentions=m-chp20-p400-037@02-sources/02-Markdown/20_CHP-20Postscript.md#L46-57[Monsignor Angelo Cesi]; group=new-person:angelo-cesi-monsignor-20261017; S3 cross-chapter review 2026-10-17: the p.400 passage explicitly identifies Monsignor Angelo Cesi as the brother of Cardinal Angelo Cesi (cand-0639). They share a name but are distinct people. Retain as a source-local new person group; no existing same-type person KU matched; S4 registration pending. Previous same-name grouping rationale superseded; see S3-cross-chapter-groups-2026-10-17.

`st-chp3-secii-l54-60-cesi-promised-high-altar-decoration`的端点身份已在S3定为cand-0639；其装饰承诺仍留待S6逐条审查。`st-chp3-secii-l54-60-angelo-cesi-died-1606`仅是履历断言，已从关系候选中关闭；死年获DBI支持，Cardinal称谓仍与DBI冲突。

#### 头衔型人物组理由更正

`cand-0538`（Marshal Caprara）、`cand-0559`（Earl of Carlisle）、`cand-0614`（Conte Cavazza）和`cand-0615`（Comte de Caylus）均保留原new组，但alignment旧理由误称它们有‘full personal name’。现更正为书内/索引仅给头衔与姓氏，未提供given name；不补造全名。Caylus的p.319全称与p.360跨行拆开的同一称谓构成书内跨章锚点；Carlisle的索引页279、305及正文p.278–279明确承接‘Lord Carlisle’与代词‘He’。

被更正的四条旧alignment理由保留如下：

- `cand-0538`：source_ref=candidate=cand-0538;index_entry=C.csv#62;index_pages=201;s2_mentions=m-chp7-p201-p202-003@02-sources/02-Markdown/07_CHP-7_sec_v.md#L42-55[Marshal Caprara;chars=77-92]; group=new-person:caprara-marshal-bff39a6eb9; New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-0538 by identical normalized full-name/explicit-alias anchor (caprara marshal), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.
- `cand-0559`：source_ref=candidate=cand-0559;index_entry=C.csv#83;index_pages=279, 305;s2_mentions=m-chp10-p278-carlisle_name@02-sources/02-Markdown/10_CHP-10_intro.md#L26-41[Carlisle;chars=1546-1554],m-chp10-p305-earl-carlisle@02-sources/02-Markdown/10_CHP-10_intro.md#L423-433[Earl of Carlisle;chars=3109-3125],m-chp10-p279-carlisle@02-sources/02-Markdown/10_CHP-10_intro.md#L43-49[Lord Carlisle;chars=255-268],m-chp10-p279-he_carlisle@02-sources/02-Markdown/10_CHP-10_intro.md#L43-49[He;chars=410-412]; group=new-person:carlisle-of-b2c281b2ce; New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-0559 by identical normalized full-name/explicit-alias anchor (carlisle of), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.
- `cand-0614`：source_ref=candidate=cand-0614;index_entry=C.csv#138;index_pages=269;s2_mentions=m-chp9-p269-cavazza-title@02-sources/02-Markdown/09_CHP-9_sec_ii.md#L18-25[Conte;chars=1397-1402],m-chp9-p269-cavazza-surname@02-sources/02-Markdown/09_CHP-9_sec_ii.md#L18-25[Cavazza;chars=1403-1410]; group=new-person:cavazza-conte-ebbfa1d543; New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-0614 by identical normalized full-name/explicit-alias anchor (cavazza conte), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.
- `cand-0615`：source_ref=candidate=cand-0615;index_entry=C.csv#139;index_pages=319, 360;s2_mentions=m-s2-ch10-p319-0025@02-sources/02-Markdown/10_CHP-10_sec_ii.md#L144-149[Comte de Caylus;chars=820-835],m-chp14-p360-0015@02-sources/02-Markdown/14_CHP-14_intro.md#L139-146[Caylus;chars=1231-1237]; group=new-person:caylus-comte-de-0164c373cd; New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name. Grouped with cand-0615 by identical normalized full-name/explicit-alias anchor (caylus comte de), not surname-only similarity. No external identity source was accessed; KU assignment remains for S4.

本次S3组成员增加cand-10945并并入既有组，候选数不变、new身份组数减少1；S4待登记组减少1，待登记成员数不变。S3 new=4,962候选/4,774组；S4已登记794组/967条映射，待登记3,980组/3,995条映射；KU=1813。

<a id="s3-correct-cesi-candidate-detail-20261017"></a>

### S3候选元数据纠正：cand-10945（2026-10-17）

核对entity-candidates.csv时发现cand-10945的detail仍保留旧的“不同人物”说明，与alignment.csv中已执行的cand-0639/cand-10945同组决定冲突。S3裁决、组号及候选映射本身正确；前次更正脚本把detail写到了候选字典外层，本次将说明修正到cand-10945行。现明确两者同为Cardinal Pier Donato Cesi的兄弟Angelo Cesi；Treccani支持托迪主教身份，第3章p.70的枢机头衔仍保留为来源冲突。组成员和S3决定计数不变。

<a id="s4-person-direct-endpoints-caprara-carlisle-cavazza-caylus-cesi-20261017"></a>

### S4人物身份组登记：Caprara、Carlisle、Cavazza、Caylus、Angelo Cesi（2026-10-17）

- `cand-0538`（`new-person:caprara-marshal-bff39a6eb9`）→ [卡普拉拉元帅（Marshal Caprara）](../../../04-knowledge/units/persons/marshal-caprara.md)；S2直接关系候选 `st-chp7-p201-v-caprara-commissions-bologna-paintings` 留待S6。Haskell报告Caprara在博洛尼亚的多项绘画委托，但没有给出作品清单或具体对象；该S2候选留待S6。
- `cand-0559`（`new-person:carlisle-of-b2c281b2ce`）→ [卡莱尔伯爵（Earl of Carlisle）](../../../04-knowledge/units/persons/earl-of-carlisle.md)；S2直接关系候选 `st-chp10-p279-carlisle-employs-marco-ricci`, `st-chp10-p279-carlisle-employs-pellegrini` 留待S6。两条S2候选共享“two Venetian artists”这一集体表述；端点分别映射至Marco Ricci与Pellegrini，但不据此拆定个人合同或工作范围，均留待S6。
- `cand-0614`（`new-person:cavazza-conte-ebbfa1d543`）→ [卡瓦扎伯爵（Count Cavazza）](../../../04-knowledge/units/persons/conte-cavazza.md)；S2直接关系候选 `st-chp9-p269-cavazza-admission-patriciate`, `st-chp9-p269-cavazza-paid-facade` 留待S6。1653年入贵族阶层及支付立面费用均按Haskell原书陈述保存；注释所引记录未核，两个S2候选留待S6。
- `cand-0615`（`new-person:caylus-comte-de-0164c373cd`）→ [卡亚吕伯爵（Comte de Caylus）](../../../04-knowledge/units/persons/comte-de-caylus.md)；S2直接关系候选 `st-chp10-p319-conti-friendship-with-caylus` 留待S6。交友情形来自Haskell对Conti第二次巴黎停留的叙述；未补入额外交往细节，该S2候选留待S6。
- `cand-0639`、`cand-10945`（`new-person:angelo-cesi-d4e25faff9`）→ [安杰洛·切西（托迪主教）（Angelo Cesi, Bishop of Todi）](../../../04-knowledge/units/persons/angelo-cesi-bishop-of-todi.md)；S2直接关系候选 `st-chp3-secii-l40-52-angelo-continues-family-patronage`, `st-chp3-secii-l54-60-cesi-promised-high-altar-decoration` 留待S6。第3章分别记录Angelo Cesi延续家族对Chiesa Nuova的赞助，以及高坛装饰曾由“Cardinal Angelo Cesi”承诺；后者的头衔冲突保留，两个S2候选留待S6。后记p.400的兄弟身份仅用作S3身份锚点，不在本批建立正式边。

本批登记5个S3 new人物身份组、6条候选映射；每组只登记书内支持的名称。Cesi外部身份比较另记Treccani DBI为aln外部记录，仅支持身份及头衔冲突辨析。新增6条source_backed姓名字段；不新增formal relations。

登记后person类型S4为393组/482条已登记、673组/674条待登记；全书为799组/973条已登记、3,975组/3,989条待登记，KU=1818。

<a id="s3-almoro-academy-crosschapter-boundaries-20261017"></a>

### S3跨章复核：Almorò身份与三所学院区分（2026-10-17）

- cand-0024为Almorò Albrizzi：索引A.csv#23及第13章p.334的Almorò与[Treccani DBI人物条目](https://www.treccani.it/enciclopedia/almoro-albrizzi_%28Dizionario-Biografico%29/)相合（访问日期：2026-10-17）；不与cand-1941混同。
- cand-1941为Pisani家族之子Almorò：第9章p.255、260–261的家族语境与[Treccani DBI的Longhi条目](https://www.treccani.it/enciclopedia/pietro-longhi_%28Dizionario-Biografico%29/)相合（访问日期：2026-10-17）。该Longhi条目明确称Almorò Pisani，但不是其本人规范记录，故不借用其URL作为人物外部标识。p.261的1740–66不作生卒年。
- cand-0001 Accademia Albrizziana与既有Albrizziana印刷所分开；其为文学与科学学会。cand-8496是为Pisani之子提供绘画课、由Longhi主持的私人学院；cand-0004由第8章展览语境及第10章p.330注3定位为佛罗伦萨Accademia del Disegno。三所机构的名称、组织者／受教者、用途或地点不同，不合并。cand-8500已same至Pisani di Santo Stefano家族卡，cand-1429已映射Pietro Longhi。
- cand-7977仍为S3 undecided；Vasari文献cand-9864仍待S4。相关关系继续待S6。


<a id="s4-almoro-academy-crosschapter-endpoints-20261017"></a>

### S4跨章学院与直接端点身份组登记（2026-10-17）

- cand-0024（new-person:albrizzi-almoro-ac00ba2f26）→ [阿尔莫罗·阿尔布里齐（Almorò Albrizzi）](../../../04-knowledge/units/persons/almoro-albrizzi.md)。Treccani DBI外部身份行仅支持该人物身份；组织学院的S2候选留待S6。
- cand-1941（new-person:almoro-pisani-44c6067e62）→ [阿尔莫罗·皮萨尼（Almorò Pisani）](../../../04-knowledge/units/persons/almoro-pisani.md)。以来源支持的姓氏、家族角色和Treccani Longhi条目分开Albrizzi同名人物；学院授课候选留待S6。
- cand-0001（sg3-institution-cand-0001）→ [阿尔布里齐学会（Accademia Albrizziana）](../../../04-knowledge/units/institutions/accademia-albrizziana.md)。不并入印刷所KU。
- cand-8496（sg3-institution-cand-8496）→ [皮萨尼家族私人学院（Pisani family private academy under Pietro Longhi）](../../../04-knowledge/units/institutions/pisani-private-academy.md)。标题为描述性暂名，不冒充原书专名。
- cand-0004（sg3-institution-cand-0004）→ [佛罗伦萨设计学院（Accademia del Disegno in Florence）](../../../04-knowledge/units/institutions/accademia-del-disegno-florence.md)。展览端点cand-7977待决，Vasari文献cand-9864待S4。

本批登记5个S3 new身份组、5条候选映射和1条Albrizzi外部身份行；抽取8条source_backed名称字段，不改sources.csv、candidate-backlog.csv或relations.csv，不新增正式关系。

登记后person类型S4为395组/484条已登记、671组/672条待登记；institution类型为24组/29条已登记、167组/167条待登记；全书为804组/978条已登记、3,970组/3,984条待登记，KU=1823。


<a id="s4-person-direct-endpoints-gloucester-farsetti-monconys-mei-newcastle-20261017"></a>

### S4人物直接关系端点登记：Gloucester、Farsetti、Monconys、Mei、Newcastle（2026-10-17）

- cand-1204（new-person:1st-gloucester-henry-of-william-f80c2b53e6）→ [威廉·亨利（第一代格洛斯特公爵）（William Henry, 1st Duke of Gloucester）](../../../04-knowledge/units/persons/william-henry-duke-of-gloucester.md)。以索引G.csv#111与第15章；印刷页366及注1的称谓建立书内身份锚点；S2直接关系候选st-chp15-p366-duke-gloucester-azzo-statue、st-chp15-p366-note1-duke-visits、st-chp15-p366-note1-memmo-contact-and-order-date留待S6逐条裁决。本批未查验外部身份记录，不新增正式关系。
- cand-1000（new-person:anton-farsetti-francesco-89c16bbb22）→ [安东·弗朗切斯科·法尔塞蒂（Anton Francesco Farsetti）](../../../04-knowledge/units/persons/anton-francesco-farsetti.md)。以索引F.csv#15与第15章；印刷页364的称谓建立书内身份锚点；S2直接关系候选st-chp15-p364-tommaso-embittered-by-nephew、st-chp15-p364-tommaso-denounced-anton-francesco、st-chp15-p364-anton-nephew-of-tommaso留待S6逐条裁决。本批未查验外部身份记录，不新增正式关系。
- cand-1685（new-person:balthasar-de-monconys-0b85e40d5c）→ [巴尔塔萨·德·蒙科尼（Balthasar de Monconys）](../../../04-knowledge/units/persons/balthasar-de-monconys.md)。以索引M.csv#225与第5章；印刷页124的称谓建立书内身份锚点；S2直接关系候选st-chp5-p124-monconys-rome-visit、st-chp5-p124-monconys-visited-rome、st-chp5-p124-monconys-picture-sale留待S6逐条裁决。另在st-chp5-p124-monconys-introduced-poussin、st-chp5-p124-monconys-introduced-claude中仅列为提及对象，不是结构化主客体端点，故不作直接端点映射。本批未查验外部身份记录，不新增正式关系。
- cand-1633（new-person:bernardino-mei-15dd160f7a）→ [贝尔纳迪诺·梅伊（Bernardino Mei）](../../../04-knowledge/units/persons/bernardino-mei.md)。以索引M.csv#173与第6章；印刷页154的称谓建立书内身份锚点；S2直接关系候选st-chp6-p154-mei-allegories、st-chp6-p154-mei-paints-fortune-fresco、st-chp6-p154-mei-youth-rescued-allegory留待S6逐条裁决。本批未查验外部身份记录，不新增正式关系。
- cand-1737（new-person:cavendish-newcastle-of-william-adc14e205b）→ [威廉·卡文迪什（纽卡斯尔公爵）（William Cavendish, Duke of Newcastle）](../../../04-knowledge/units/persons/william-cavendish-duke-of-newcastle.md)。以索引N.csv#17与第7章；印刷页178的称谓建立书内身份锚点；S2直接关系候选st-chp7-p178-i20、st-chp7-p178-i21、st-chp7-p178-i22留待S6逐条裁决。本批未查验外部身份记录，不新增正式关系。

本批登记5个既有S3 new单成员人物组及5条候选映射，新增10条source_backed名称字段；不改写S3分组，不添加外部身份标识、候选、来源或正式关系。

登记后person类型S4为400组/489条已登记、666组/667条待登记；全书为809组/983条已登记、3,965组/3,979条待登记，KU=1828。


<a id="s3-reuse-fumiani-existing-identity-20261017"></a>

### S3跨章复核：Fumiani候选复用既有人物KU（2026-10-17）

- cand-1087（原S3 new组 new-person:fumiani-giannantonio-09eeb0cf67）改判same至units/persons/giannantonio-fumiani。索引F.csv#104列Giannantonio Fumiani及pp.227、232；第8章p.234的姓名和Grand Prince Ferdinand语境与既有卡图版40b的GiannAntonio Fumiani相连。Treccani DBI《意大利人传记辞典》第50卷（1998）条目以Giovanni Antonio Fumiani为题，并记其受Ferdinando委托创作《撒迦利亚被石击》。姓名变体与画家—赞助人语境支持复用同一人物KU；旧new判断已由本条更正，不另建重复人物卡。
- cand-1088（索引F.csv#105，子项and Grand Prince Ferdinand，p.234）改判same至同一KU。该索引子项定位到已映射在cand-1087下的p.234人物提及，不作为第二个人物；OCR形式Giannaritonio保留，不据此静默校正。
- 外部身份比较行登记Treccani DBI URL及访问日期2026-10-17，只支持人物身份。p.234具体作品识别仍保留原有不确定性；cand-1090及cand-7939的作品身份裁决不在本次变更内。直接关系候选st-chp8-p232-fumiani-david-instruction、st-chp8-p233-loth-and-responsive-artist、st-chp8-p234-fumiani-option-to-paint-david继续待S6。



<a id="s4-person-direct-endpoints-guidiccioni-malpighi-gambarini-pourbus-sacchetti-20261017"></a>

### S4人物直接关系端点登记：Guidiccioni、Malpighi、Gambarini、Pourbus、Sacchetti（2026-10-17）

- cand-1281（new-person:guidiccioni-lelio-3a426183a6）→ [莱利奥·圭迪乔尼（Lelio Guidiccioni）](../../../04-knowledge/units/persons/lelio-guidiccioni.md)。以索引G.csv#191和所列正文姓名／语境建立书内身份锚点；直接S2关系候选st-chp5-note-p121-n2-mercati-print、st-chp5-p121-guidiccioni-attributions、st-chp5-note-p121-n2-print-inscription-interest留待S6逐条裁决。本批不查验外部身份记录，不新增正式关系。
- cand-1500（new-person:malpighi-marcello-dfbdbe5c0e）→ [马尔切洛·马尔皮基（Marcello Malpighi）](../../../04-knowledge/units/persons/marcello-malpighi.md)。以索引M.csv#37和所列正文姓名／语境建立书内身份锚点；直接S2关系候选st-chp8-p203-malpighi-friend-guercino、st-chp8-p203-malpighi-reni-painting-and-taste、st-chp8-p203-malpighi-friend-cignani留待S6逐条裁决。本批不查验外部身份记录，不新增正式关系。
- cand-1113（new-person:gambarini-giuseppe-41d66b2cf1）→ [朱塞佩·甘巴里尼（Giuseppe Gambarini）](../../../04-knowledge/units/persons/giuseppe-gambarini.md)。以索引G.csv#20和所列正文姓名／语境建立书内身份锚点；直接S2关系候选st-chp8-p203-belloni-sent-gambarini-to-rome、st-chp8-p225-gambarini-pagan-scenes、st-chp8-p225-artist-produces-aeneid-scenes-gambarini留待S6逐条裁决。本批不查验外部身份记录，不新增正式关系。
- cand-1983（new-person:franz-pourbus-younger-cd004e16c5）→ [弗朗茨·普尔布斯（小）（Franz Pourbus the Younger）](../../../04-knowledge/units/persons/franz-pourbus-the-younger.md)。以索引P.csv#185和所列正文姓名／语境建立书内身份锚点；直接S2关系候选st-chp7-p174-i19、st-chp7-p174-i20、st-chp7-p174-i21留待S6逐条裁决。本批不查验外部身份记录，不新增正式关系。
- cand-2312（new-person:francesco-giovanni-sacchetti-e5e90628e9）→ [乔瓦尼·弗朗切斯科·萨凯蒂（Giovanni Francesco Sacchetti）](../../../04-knowledge/units/persons/giovanni-francesco-sacchetti.md)。以索引S.csv#0和所列正文姓名／语境建立书内身份锚点；直接S2关系候选st-chp7-p180-i09、st-chp7-p180-i10、st-chp7-p180-i11留待S6逐条裁决。本批不查验外部身份记录，不新增正式关系。

本批登记5个既有S3 new单成员人物组及5条候选映射，新增10条source_backed名称字段；不改写S3分组，不添加外部身份标识、候选、来源或正式关系。

登记后person类型S4为405组/494条已登记、660组/661条待登记；全书为814组/988条已登记、3,959组/3,973条待登记，KU=1833。


<a id="s3-del-rosso-index-subentries-crosschapter-20261018"></a>

### S3索引子项复核：Lorenzo del Rosso组（2026-10-18）

cand-2283（Q-R.csv#211，and Luca Giordano，pp.212-213）与cand-2284（Q-R.csv#212，taste，p.213）从undecided改为new，并并入cand-2282的new-person:del-lorenzo-rosso-0ec611aff2组。两项是同一索引主条目下对Lorenzo del Rosso的主题／交叉定位，不是新人物。第8章p.212的S2提及m-chp8-p212-055已将Lorenzo置于同一连续段落；p.212-213延续叙述该兄弟家户与Luca Giordano的往来。该组仍与Andrea、Ottavio及其他del Rosso家族成员分开；外部身份未查验，S4将为三条候选映射同一KU。



<a id="s4-person-direct-endpoints-rospigliosi-rossi-del-rosso-savelli-roccatagliata-20261018"></a>

### S4人物直接端点登记：Rospigliosi、Rossi、Del Rosso、Savelli、Roccatagliata（2026-10-18）

- 候选cand-2262（new-person:camillo-rospigliosi-fb5ca73bce）→ [卡米洛·罗什皮廖西（Camillo Rospigliosi）](../../../04-knowledge/units/persons/camillo-rospigliosi.md)。索引主项Q-R.csv#190与所列正文建立书内身份锚点；直接S2关系候选st-chp5-p127-camillo-brother-of-pope、st-chp5-p127-rospigliosi-sons-novices、st-chp5-p127-four-sons-of-camillo留待S6逐条裁决。本批未查验外部身份记录，不新增正式关系。
- 候选cand-2272（new-person:de-mattia-rossi-f41c4c976a）→ [马蒂亚·德·罗西（Mattia de’ Rossi）](../../../04-knowledge/units/persons/mattia-de-rossi.md)。索引主项Q-R.csv#200与所列正文建立书内身份锚点；直接S2关系候选st-chp3-seciv-l106-116-mattia-assistant-to-berni、st-chp3-seciv-l106-116-mattia-paid-in-kind、st-chp3-seciv-l130-139-mattia-advice-plan-accepted留待S6逐条裁决。本批未查验外部身份记录，不新增正式关系。
- 候选cand-2282、cand-2283、cand-2284（new-person:del-lorenzo-rosso-0ec611aff2）→ [洛伦佐·德尔·罗索（Lorenzo del Rosso）](../../../04-knowledge/units/persons/lorenzo-del-rosso.md)。索引主项Q-R.csv#210与所列正文建立书内身份锚点；直接S2关系候选st-chp8-p210-house-inhabited-by-lorenzo-del-rosso、st-chp8-p211-wills-and-caravaggio-bequest、st-chp8-p212-lorenzo-may-have-started-career-naples留待S6逐条裁决。本批未查验外部身份记录，不新增正式关系。
- 候选cand-2376（new-person:giulio-savelli-0722b9a04e）→ [朱利奥·萨韦利（Prince Giulio Savelli）](../../../04-knowledge/units/persons/giulio-savelli.md)。索引主项S.csv#64与所列正文建立书内身份锚点；直接S2关系候选st-chp3-seciv-l165-177-emperor-mediated-patronage-transfer、st-chp3-seciv-l165-177-savelli-family-head-of-giulio、st-chp3-seciv-l165-177-cardinal-savelli-ancestor-of-giulio留待S6逐条裁决。本批未查验外部身份记录，不新增正式关系。
- 候选cand-2205（new-person:giovanni-roccatagliata-stefano-9f5bb05e0c）→ [乔瓦尼·斯特法诺·罗卡塔利亚塔（Giovanni Stefano Roccatagliata）](../../../04-knowledge/units/persons/giovanni-stefano-roccatagliata.md)。索引主项Q-R.csv#132与所列正文建立书内身份锚点；直接S2关系候选st-chp5-note-p121-n7-roccatagliata-contact、st-chp5-note-p121-n7-roccatagliata-sales留待S6逐条裁决。本批未查验外部身份记录，不新增正式关系。

本批登记5个既有S3 new身份组、7条候选映射，新增10条source_backed名称字段；不添加外部身份标识、候选、来源或正式关系。

登记后person类型S4为410组/501条已登记、655组/656条待登记；全书为819组/995条已登记、3,954组/3,968条待登记，KU=1838。

<a id="s3-reuse-baldoini-existing-person-ku-20261018"></a>

### S3人物复核：Baldoini候选复用既有人物KU（2026-10-18）

cand-0167（B.csv#14，Gio. Gasparo Baldoini）由new改为same，复用[乔瓦尼·加斯帕雷·巴尔多伊诺（Giovanni Gaspare Baldoino）](../../../04-knowledge/units/persons/gio-gasparo-baldoini.md)（units/persons/gio-gasparo-baldoini）。第1章注释记其由Maurizio di Savoia任命为“per nostro pittore”；既有卡已保存这条原文，并以独立记录核对Gio. Gasparo Baldoini与Giovanni Gaspare Baldoino/Baudoin的名字变体及赞助语境。故索引形式Baldoini归入同一人物；不新建重复KU，不新增外部身份行或正式关系。

<a id="s3-giovanni-bellini-index-and-cross-chapter-identity-20261018"></a>

### S3跨章身份裁决：Giovanni Bellini（2026-10-18）

cand-0270保持new，身份组为new-person:bellini-giovanni-b88f43a625。索引B.csv#117将pp.380、410两处Bellini统一列为Giovanni Bellini；同一索引的B.csv#118将Gentile Bellini另列于p.198。第17章p.380记Manfrin收藏中的Bellini，第20章后记p.410记Della Lena对Vivarini、Carpaccio与Bellini的赞赏。既有Gentile Bellini卡称Giovanni为其弟，进一步说明二者是不同人物。当前无Giovanni Bellini卡，因此该组应新建；不主张外部身份核验。


<a id="s4-person-direct-endpoints-bagnara-barbarigo-bellini-clement-20261018"></a>

### S4人物直接关系端点登记：Bagnara、Barbarigo、Bellini、Clément（2026-10-18）

- cand-0160（new-person:bagnara-duchess-of-4e303ad55f）→ [巴尼亚拉公爵夫人（Duchess of Bagnara）](../../../04-knowledge/units/persons/duchess-of-bagnara.md)。索引B.csv#7与指定正文页段构成书内身份依据；S2直接关系候选st-chp8-p209-ruffo-mother-built-palace留待S6。个人姓名未由原书提供的对象保留原称谓；本批未查验外部身份记录，不新增正式关系。
- cand-0183（new-person:affiliations-barbarigo-pietro-political-s--c55fc905b5）→ [皮耶特罗·巴尔巴里戈（Pietro Barbarigo）](../../../04-knowledge/units/persons/pietro-barbarigo.md)。索引B.csv#30与指定正文页段构成书内身份依据；S2直接关系候选st-chp9-p254-barbarigo-nephews-in-strength-fresco留待S6。个人姓名未由原书提供的对象保留原称谓；本批未查验外部身份记录，不新增正式关系。
- cand-0270（new-person:bellini-giovanni-b88f43a625）→ [乔瓦尼·贝利尼（Giovanni Bellini）](../../../04-knowledge/units/persons/giovanni-bellini.md)。索引B.csv#117与指定正文页段构成书内身份依据；S2直接关系候选st-chp17-p380-manfrin-collection-represented-bellini留待S6。个人姓名未由原书提供的对象保留原称谓；本批未查验外部身份记录，不新增正式关系。
- cand-0789（new-person:abbe-clement-abbe-clement-s-d72d932bb3）→ [克莱芒（Abbé Clement）（Abbé Clement）](../../../04-knowledge/units/persons/abbe-clement-zanetti-description.md)。索引C.csv#313与指定正文页段构成书内身份依据；S2直接关系候选st-chp13-p344-clement-description_of_zanetti留待S6。个人姓名未由原书提供的对象保留原称谓；本批未查验外部身份记录，不新增正式关系。

本批登记4个S3 new人物组和4条候选映射，新增8条source_backed名称字段；不添加外部身份标识、候选、来源或正式关系。4条直接S2关系候选留待S6。

登记后person类型S4为414组/505条已登记、650组/651条待登记；全书为823组/999条已登记、3,949组/3,963条待登记，KU=1842。


<a id="s4-person-direct-endpoints-colonna-concina-20261018"></a>

### S4人物直接关系端点登记：Colonna与Concina（2026-10-18）

- cand-0806（new-person:colonna-filippo-75b1b9b619）→ [菲利波·科隆纳（Filippo Colonna）](../../../04-knowledge/units/persons/filippo-colonna.md)。索引C.csv#336与所列章节页段构成书内身份依据；直接S2关系候选st-chp6-p155-colonna-palace-rebuilt留待S6。本批不扩写来源未载的姓名或世系，不查验外部身份记录，也不新增正式关系。
- cand-0808（new-person:colonna-francesco-51fabc2402）→ [弗朗切斯科·科隆纳亲王（Prince Francesco Colonna）](../../../04-knowledge/units/persons/prince-francesco-colonna.md)。索引C.csv#338与所列章节页段构成书内身份依据；直接S2关系候选st-chp2-seci-l124-157-colonna-sale-letter留待S6。本批不扩写来源未载的姓名或世系，不查验外部身份记录，也不新增正式关系。
- cand-0810（new-person:colonna-giuliano-09b7a0c524）→ [唐·朱利亚诺·科隆纳（Don Giuliano Colonna）](../../../04-knowledge/units/persons/don-giuliano-colonna.md)。索引C.csv#340与所列章节页段构成书内身份依据；直接S2关系候选st-chp8-p207-n1-daughter-married-giuliano-colonna留待S6。本批不扩写来源未载的姓名或世系，不查验外部身份记录，也不新增正式关系。
- cand-0814（new-person:antonio-colonna-marc-512265ff8f）→ [马尔坎托尼奥·科隆纳（Marc’Antonio Colonna）](../../../04-knowledge/units/persons/marc-antonio-colonna.md)。索引C.csv#344与所列章节页段构成书内身份依据；直接S2关系候选st-chp6-p156-fresco-cycle-depicts-marcantonio-at-lepanto留待S6。本批不扩写来源未载的姓名或世系，不查验外部身份记录，也不新增正式关系。
- cand-0819（new-person:concina-daniele-66b178ccc2）→ [达尼埃莱·孔奇纳神父（Padre Daniele Concina）](../../../04-knowledge/units/persons/padre-daniele-concina.md)。索引C.csv#349与所列章节页段构成书内身份依据；直接S2关系候选st-chp9-p271-concina-anti-jesuit-invective留待S6。本批不扩写来源未载的姓名或世系，不查验外部身份记录，也不新增正式关系。

本批登记5个S3 new人物组、5条候选映射和10条source_backed名称字段；5条直接S2关系候选留待S6。未添加外部身份标识、来源、候选或正式关系。

登记后person类型S4为419组/510条已登记、645组/646条待登记；全书为828组/1,004条已登记、3,944组/3,958条待登记，KU=1847。


<a id="s4-person-direct-endpoints-constable-contarini-correr-corsini-20261018"></a>

### S4人物直接关系端点登记：Constable、Contarini、Correr、Corsini（2026-10-18）

- cand-0822（new-person:constable-john-425769ec08）→ [约翰·康斯特勃尔（John Constable）](../../../04-knowledge/units/persons/john-constable.md)。索引C.csv#352与正文页段构成书内身份依据；直接S2关系候选st-chp14-p360-constable-studied-works留待S6。本批不查验外部身份记录，不新增正式关系；Haskell转引的Baldinucci来源未独立查阅。
- cand-0823（new-person:contarini-pietro-8efdf34875）→ [彼得罗·孔塔里尼（Pietro Contarini）](../../../04-knowledge/units/persons/pietro-contarini.md)。索引C.csv#353与正文页段构成书内身份依据；直接S2关系候选st-chp2-sec-ii-l10-18-contarini-state-and-rome-description留待S6。本批不查验外部身份记录，不新增正式关系；Haskell转引的Baldinucci来源未独立查阅。
- cand-0856（new-person:antonio-correr-fra-francesco-bae96cd018）→ [弗朗切斯科·安东尼奥·科雷尔修士（Fra Francesco Antonio Correr）](../../../04-knowledge/units/persons/fra-francesco-antonio-correr.md)。索引C.csv#386与正文页段构成书内身份依据；直接S2关系候选st-chp9-p271-correr-patriarch-1734留待S6。本批不查验外部身份记录，不新增正式关系；Haskell转引的Baldinucci来源未独立查阅。
- cand-0861（new-person:corsini-filippo-097b8200c1）→ [菲利波·科西尼侯爵（Marchese Filippo Corsini）](../../../04-knowledge/units/persons/marchese-filippo-corsini.md)。索引C.csv#391与正文页段构成书内身份依据；直接S2关系候选st-chp5-notes-l144-corsini-miel留待S6。本批不查验外部身份记录，不新增正式关系；Haskell转引的Baldinucci来源未独立查阅。
- cand-0862（new-person:clement-xii-corsini-lorenzo-b071aa0e12）→ [洛伦佐·科西尼（教宗克勉十二世）（Lorenzo Corsini (Pope Clement XII)）](../../../04-knowledge/units/persons/lorenzo-corsini-pope-clement-xii.md)。索引C.csv#392与正文页段构成书内身份依据；直接S2关系候选st-chp10-p317-pope-attempted-to-prevent-galileo-mausoleum留待S6。本批不查验外部身份记录，不新增正式关系；Haskell转引的Baldinucci来源未独立查阅。

本批登记5个S3 new人物组、5条候选映射及10条source_backed名称字段；5条直接S2关系候选留待S6。未添加外部身份标识、候选、来源或正式关系。

登记后person类型S4为424组/515条已登记、640组/641条待登记；全书为833组/1,009条已登记、3,939组/3,953条待登记，KU=1852。

<a id="s3-dolfin-and-devonshire-identity-boundaries-20261018"></a>

### S3身份边界：Daniele Dolfin与Devonshire公爵头衔（2026-10-18）

- cand-0926保留new组new-person:a-daniele-dolfin-new-patriarch-daniele-dol-463e05f412：索引D.csv#28的Daniele Dolfin（Archbishop of Udine）对应第9章p.253注1所述1759年新任宗主教；既有D.csv#29、#30的Daniele III、Daniele IV均据第9章p.252于1729年去世，不能复用其KU。该新组可进入S4，身份限于书内。
- cand-0918由new改为conflict，组person-conflict-devonshire-titleholders-20261018。第10章pp.289-290的Duke of Devonshire与第13章p.343注3、1760年序言语境中的同头衔，未证明是同一世代。无KU；p.289-290的三条直接关系端点保留待证。下一步先以权威或原始记录识别p.343注的公爵；确认不同后再经backlog新增候选并回到S2重映射。未使用外部身份源。



<a id="s4-person-direct-endpoints-dolfin-douglas-erlach-ferdinand-ferrari-20261018"></a>

### S4人物直接关系端点登记：Dolfin、Douglas、Erlach、Ferdinand Maria、Ferrari（2026-10-18）

- cand-0926（new-person:a-daniele-dolfin-new-patriarch-daniele-dol-463e05f412）→ [丹尼埃莱·多尔芬（乌迪内总主教）（Daniele Dolfin (Archbishop of Udine)）](../../../04-knowledge/units/persons/daniele-dolfin-archbishop-of-udine.md)。索引D.csv#28与所列章节页段构成书内身份依据；直接S2关系候选st-chp9-p253-note1-later-recall-and-chapel留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-0946（new-person:douglas-hamilton-of-7bc05a28df）→ [汉密尔顿（道格拉斯侯爵）（Hamilton, Marquis of Douglas）](../../../04-knowledge/units/persons/hamilton-marquis-of-douglas.md)。索引D.csv#48与所列章节页段构成书内身份依据；直接S2关系候选st-chp16-p375-douglas-in-touch-with-sasso留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-0978（new-person:erlach-fischer-von-a7b320e21b）→ [费舍尔·冯·埃尔拉赫（Fischer von Erlach）](../../../04-knowledge/units/persons/fischer-von-erlach.md)。索引E.csv#13与所列章节页段构成书内身份依据；直接S2关系候选st-chp7-p201-v-winter-palace-begun-by-fischer留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1016（new-person:bavaria-elector-ferdinand-maria-of-70b67fff1d）→ [费迪南德·玛丽亚（巴伐利亚选帝侯）（Ferdinand Maria, Elector of Bavaria）](../../../04-knowledge/units/persons/ferdinand-maria-elector-of-bavaria.md)。索引F.csv#31与所列章节页段构成书内身份依据；直接S2关系候选st-chp7-p193-ferdinand-maria-marriage留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1020（new-person:ferrari-giovanni-b75250fc2c）→ [乔瓦尼·费拉里（Giovanni Ferrari）](../../../04-knowledge/units/persons/giovanni-ferrari.md)。索引F.csv#35与所列章节页段构成书内身份依据；直接S2关系候选st-chp15-p367-canova-statue-made-by-ferrari留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。

本批登记5个S3 new人物组、5条候选映射和10条source_backed名称字段；5条直接S2关系候选留待S6。未添加外部身份标识、来源、候选或正式关系。

登记后person类型S4为429组/520条已登记、634组/635条待登记；全书为838组/1,014条已登记、3,933组/3,947条待登记，KU=1857。

<a id="s3-reuse-conte-francesco-fontana-20261018"></a>

### S3人物复核：Conte Francesco Fontana复用既有人物KU（2026-10-18）

cand-1046（F.csv#61，Conte Francesco Fontana）由new改为same，复用[弗朗切斯科·丰塔纳人物卡](../../../04-knowledge/units/persons/francesco-fontana.md)（units/persons/francesco-fontana）。既有卡已保存第1章p.17同一段落，明确其为Fulvio Testi书信所致的Fontana伯爵；其1633年书信候选cand-3549亦已映射至既有书信卡，书信收信人端点指向此人物。既有卡同时记录家族研究对身份的独立支持。原new组号及理由作为历史保留；不重复建卡，不新增外部身份行或正式关系。该候选的直接关系仍交S6核对既有边及候选对应。


<a id="s4-person-direct-endpoints-ferretti-festari-fiammeri-fontana-20261018"></a>

### S4人物直接关系端点登记：Ferretti、Festari、Fiammeri与Carlo Fontana（2026-10-18）

- cand-1026（new-person:domenico-ferretti-gian-23c449bb47）→ [吉安·多梅尼科·费雷蒂（Gian Domenico Ferretti）](../../../04-knowledge/units/persons/gian-domenico-ferretti.md)。索引F.csv#41与所列章节页段构成书内身份依据；直接S2关系候选st-chp10-p299-publication-obstacles留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1032（new-person:festari-girolamo-bb06b8d193）→ [吉罗拉莫·费斯塔里（Girolamo Festari）](../../../04-knowledge/units/persons/girolamo-festari.md)。索引F.csv#47与所列章节页段构成书内身份依据；直接S2关系候选st-chp15-p369-querini-festari-companion-trip,st-chp15-p369-querini-festari-trip-observations留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1034（new-person:battista-fiammeri-giovanni-1df26fcd92）→ [乔瓦尼·巴蒂斯塔·菲亚梅里（Giovanni Battista Fiammeri）](../../../04-knowledge/units/persons/giovanni-battista-fiammeri.md)。索引F.csv#49与所列章节页段构成书内身份依据；直接S2关系候选st-chp3-secii-l19-31-fiammeri-directed-vitale-decoration留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1044（new-person:carlo-fontana-ca9cdad95d）→ [卡洛·丰塔纳（Carlo Fontana）](../../../04-knowledge/units/persons/carlo-fontana.md)。索引F.csv#59与所列章节页段构成书内身份依据；直接S2关系候选st-chp6-p165-v1-07留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。

本批登记4个S3 new人物组、4条候选映射和9条source_backed名称字段；5条直接S2关系候选留待S6。未添加外部身份标识、来源、候选或正式关系。

登记后person类型S4为433组/524条已登记、629组/630条待登记；全书为842组/1,018条已登记、3,928组/3,942条待登记，KU=1861。


<a id="s4-person-direct-endpoints-forabosco-fragonard-furlani-furnaletto-gagliardi-20261018"></a>

### S4人物直接关系端点登记：Forabosco、Fragonard、Furlani、Furnaletto与Gagliardi（2026-10-18）

- cand-1052（new-person:forabosco-girolamo-forabosco-girolamo-vene-196ebc5df6）→ [吉罗拉莫·福拉博斯科（Girolamo Forabosco）](../../../04-knowledge/units/persons/girolamo-forabosco.md)。索引F.csv#67与所列章节页段构成书内身份依据；直接S2关系候选st-chp7-p169-i08,st-chp7-p169-i10留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1063（new-person:fragonard-honore-jean-f88a2369f3）→ [让-奥诺雷·弗拉戈纳尔（Jean Honoré Fragonard）](../../../04-knowledge/units/persons/jean-honore-fragonard.md)。索引F.csv#78与所列章节页段构成书内身份依据；直接S2关系候选st-chp13-p332-marieschi-views-appealed-to-fragonard,st-chp9-p257-fragonard-connoisseurs-may-share-distinction留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1091（new-person:furlani-ventura-5493c4c482）→ [文图拉·富尔拉尼（Ventura Furlani）](../../../04-knowledge/units/persons/ventura-furlani.md)。索引F.csv#108与所列章节页段构成书内身份依据；直接S2关系候选st-chp15-p362-furlani-employed-to-make-casts留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1092（new-person:furnaletto-lodovico-fb8983e6c5）→ [洛多维科·富尔纳莱托（Lodovico Furnaletto）](../../../04-knowledge/units/persons/lodovico-furnaletto.md)。索引F.csv#109与所列章节页段构成书内身份依据；直接S2关系候选st-chp13-p340-furnaletto-commissioned-twelve-canaletto-drawings-in-1766,st-chp13-p340-furnaletto-established-over-thirty-years-at-ponte-de-baretteri留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1098（new-person:bernardino-gagliardi-bdbef465f5）→ [贝尔纳迪诺·加利亚尔迪（Bernardino Gagliardi）](../../../04-knowledge/units/persons/bernardino-gagliardi.md)。索引G.csv#5与所列章节页段构成书内身份依据；直接S2关系候选st-chp6-p157-collection-includes-work-by-gagliardi留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。

本批登记5个S3 new人物组、5条候选映射和10条source_backed名称字段；8条直接S2关系候选留待S6。未添加外部身份标识、来源、候选或正式关系。

登记后person类型S4为438组/529条已登记、624组/625条待登记；全书为847组/1,023条已登记、3,923组/3,937条待登记，KU=1866。


<a id="s4-person-direct-endpoints-galli-garganego-genovesi-gerbault-20261018"></a>

### S4人物直接关系端点登记：Galli、Galli-Bibiena、Garganego、Genovesi与Gerbault（2026-10-18）

- cand-1111（new-person:agnolo-galli-924c863641）→ [阿尼奥洛·加利（Agnolo Galli）](../../../04-knowledge/units/persons/agnolo-galli.md)。索引G.csv#18与所列章节页段构成书内身份依据；直接S2关系候选st-chp4-sec-ii-notes-l255-259-fn255-galli-letter留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1112（new-person:bibiena-ferdinando-galli-dc0b5ad40e）→ [费迪南多·加利-比比耶纳（Ferdinando Galli-Bibiena）](../../../04-knowledge/units/persons/ferdinando-galli-bibiena.md)。索引G.csv#19与所列章节页段构成书内身份依据；直接S2关系候选st-chp7-p201-v-galli-bibiena-theatrical-spectacles留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1114（new-person:garganego-girolamo-1498d7ac22）→ [吉罗拉莫·加尔加内戈（Girolamo Garganego）](../../../04-knowledge/units/persons/girolamo-garganego.md)。索引G.csv#21与所列章节页段构成书内身份依据；直接S2关系候选st-chp10-p324-n3-dedication-compares-goldoni-and-longhi留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1133（new-person:antonio-genovesi-3d7e20d618）→ [安东尼奥·杰诺维西（Antonio Genovesi）](../../../04-knowledge/units/persons/antonio-genovesi.md)。索引G.csv#40与所列章节页段构成书内身份依据；直接S2关系候选st-chp10-p318-genovesi-first-professor-of-political-economy留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1142（new-person:francesco-gerbault-8e64d75c81）→ [弗朗切斯科·热尔博（Francesco Gerbault）](../../../04-knowledge/units/persons/francesco-gerbault.md)。索引G.csv#49与所列章节页段构成书内身份依据；直接S2关系候选st-chp13-p336-gerbault-invited-orlando-subscriptions留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。

本批登记5个S3 new人物组、5条候选映射和10条source_backed名称字段；5条直接S2关系候选留待S6。未添加外部身份标识、来源、候选或正式关系。

登记后person类型S4为443组/534条已登记、619组/620条待登记；全书为852组/1,028条已登记、3,918组/3,932条待登记，KU=1871。


<a id="s4-person-direct-endpoints-gherardi-ghibbesio-giannone-girardon-giustiniani-20261018"></a>

### S4人物直接关系端点登记：Gherardi、Ghibbesio、Giannone、Girardon与Giustiniani（2026-10-18）

- cand-1152（new-person:antonio-gherardi-131ec7865c）→ [安东尼奥·盖拉尔迪（Antonio Gherardi）](../../../04-knowledge/units/persons/antonio-gherardi.md)。索引G.csv#59与所列章节页段构成书内身份依据；直接S2关系候选st-chp6-p161-gherardi-devotee-of-venetian-colour,st-chp6-p161-gherardi-pupil-of-mola留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1158（new-person:ghibbesio-jacopo-d39f4a5655）→ [雅各布·吉贝西奥（Jacopo Ghibbesio）](../../../04-knowledge/units/persons/jacopo-ghibbesio.md)。索引G.csv#65与所列章节页段构成书内身份依据；直接S2关系候选st-chp4-intro-l3-8-ghibbesio-collection-contents留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1164（new-person:giannone-pietro-68879d63dd）→ [彼得罗·贾诺内（Pietro Giannone）](../../../04-knowledge/units/persons/pietro-giannone.md)。索引G.csv#71与所列章节页段构成书内身份依据；直接S2关系候选st-chp10-p318-giannone-pilati-baretti-and-other-thinkers-expelled留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1193（new-person:francois-girardon-3ccbbdffed）→ [弗朗索瓦·吉拉尔东（François Girardon）](../../../04-knowledge/units/persons/francois-girardon.md)。索引G.csv#100与所列章节页段构成书内身份依据；直接S2关系候选st-chp7-p188-i31留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1195（new-person:andrea-giustiniani-2bbf388a1b）→ [安德烈亚·朱斯蒂尼亚尼（Andrea Giustiniani）](../../../04-knowledge/units/persons/andrea-giustiniani.md)。索引G.csv#102与所列章节页段构成书内身份依据；直接S2关系候选st-chp4-sec-i-l6-18-heir-marriage留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。

本批登记5个S3 new人物组、5条候选映射和10条source_backed名称字段；6条直接S2关系候选留待S6。未添加外部身份标识、来源、候选或正式关系。

登记后person类型S4为448组/539条已登记、614组/615条待登记；全书为857组/1,033条已登记、3,913组/3,927条待登记，KU=1876。


<a id="s4-person-direct-endpoints-giustiniani-gozzi-grassi-greiffenklau-20261018"></a>

### S4人物直接关系端点登记：Giustiniani、Gozzi、Grassi与Greiffenklau（2026-10-18）

- cand-1196（new-person:benedetto-giustiniani-461ae63141）→ [贝内代托·朱斯蒂尼亚尼（Benedetto Giustiniani）](../../../04-knowledge/units/persons/benedetto-giustiniani.md)。索引G.csv#103与所列章节页段构成书内身份依据；直接S2关系候选st-chp2-seci-l95-106-benedetto-caravaggio-support留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1198（new-person:ascanio-girolamo-giustiniani-d1dc8c0909）→ [吉罗拉莫·阿斯卡尼奥·朱斯蒂尼亚尼（Girolamo Ascanio Giustiniani）](../../../04-knowledge/units/persons/girolamo-ascanio-giustiniani.md)。索引G.csv#105与所列章节页段构成书内身份依据；直接S2关系候选st-chp15-p370-altar-inscription-dedicated-to-giustiniani,st-chp15-p370-giustiniani-querinis-closest-friend留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1219（new-person:carlo-gozzi-b0baf536c1）→ [卡洛·戈齐（Carlo Gozzi）](../../../04-knowledge/units/persons/carlo-gozzi.md)。索引G.csv#127与所列章节页段构成书内身份依据；直接S2关系候选st-chp9-p256-gozzi-literary-equivalent留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1226（new-person:grassi-orazio-488025973f）→ [奥拉齐奥·格拉西（Orazio Grassi）](../../../04-knowledge/units/persons/orazio-grassi.md)。索引G.csv#134与所列章节页段构成书内身份依据；直接S2关系候选st-chp3-secii-l115-123-grassi-appointment,st-chp3-secii-l115-123-grassi-galileo留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。
- cand-1230（new-person:greiffenklau-karl-philip-von-775d76e75d）→ [卡尔·菲利普·冯·格赖芬克劳（Karl Philip von Greiffenklau）](../../../04-knowledge/units/persons/karl-philip-von-greiffenklau.md)。索引G.csv#140与所列章节页段构成书内身份依据；直接S2关系候选st-chp10-p296-bishopric-transfer,st-chp10-p296-karl-philip-persuades-tiepolo留待S6。来源未给出的姓名或世系不作扩写；本批未查验外部身份记录，不新增正式关系。

本批登记5个S3 new人物组、5条候选映射和10条source_backed名称字段；8条直接S2关系候选留待S6。未添加外部身份标识、来源、候选或正式关系。

登记后person类型S4为453组/544条已登记、609组/610条待登记；全书为862组/1,038条已登记、3,908组/3,922条待登记，KU=1881。

<a id="s3-grimani-halifax-title-only-persons-20261018"></a>

### S3人物复核：Doge Grimani与Earl of Halifax保留职衔型书内身份（2026-10-18）

- cand-1234（G.csv#144，Doge Grimani）保留原new组，但撤回“完整个人姓名”的判断。第9章p.272将其置于1745年决定重建Pietà教堂的具体情境；卡片只登记书内称谓，不推定其名字。它与通称职务机构cand-8728及较早的Cardinal Grimani候选cand-1233分开；cand-1233仍为undecided。
- cand-1286（H.csv#1，Earl of Halifax）保留原new组，但撤回“完整个人姓名”的判断。第10章p.286明确其在Queen’s Bed Chamber委托叙述中的行动角色，未给出名字；不映射至任何外部命名的伯爵。威胁拒付按Haskell报告保留，不写成实际拒付。
- 两组均为来源限定的person/titleholder记录，不添加外部身份行或正式关系；各自直接S2关系候选仍待S6。

<a id="s3-h-person-crosschapter-identity-groups-20261018"></a>

### S3人物：H段跨章身份组复核（2026-10-18）

- cand-1287（H.csv#2；Hamen, Juan van der）：原new组复核，group=`new-person:der-hamen-juan-van-98401ebaa1`。第20章后记p.400正文写Juan van der Hamen，索引H.csv#2给出同一全名；这是人物cand-1287的书内身份组。它只作为已佚Cardinal Barberini肖像的画家提及，不与作品候选cand-10952合并；无相同类型既有KU。
- cand-1288（H.csv#3；Handel, George Frederick）：原new组复核，group=`new-person:frederick-george-handel-b7a9ead66a`。第10章p.281正文只用姓氏Handel；索引H.csv#3展开为George Frederick Handel。保留索引给出的书内身份形式，未据名字补写生平或外部标识；无相同类型既有KU。
- cand-1291（H.csv#7；Harrach, Count）：undecided改为new，group=`new-person:aloys-thomas-raimund-harrach-20261018`。第7章p.200的Count Harrach与Aloys Thomas Raimund Harrach相符：正文和注7均置于奥地利驻那不勒斯总督及那不勒斯艺术赞助语境。Deutsche Biographie《Aloys Graf von Harrach》列名变体Aloys Thomas Raimund Graf von Harrach及GND 132626748；Treccani《Harrach》条目记其为那不勒斯总督（1728–1733）。两处身份锚点吻合。现有KU中无该人物；改为独立new人物组，不与Harrach家族、收藏或作品对象合并。
- cand-1293（H.csv#9；Helmbrecker, Theodor）：原new组复核，group=`new-person:helmbrecker-theodor-5737710433`。第6章p.158的正文全名为Theodor Helmbrecker，索引H.csv#9同列此名。Uffizi Galleries的《Rustic scene》记录用Theodor Helmbreker（少一个c），并称Monsù Teodoro；该记录还把作品的捐赠者记为Francesco Marucelli，与Haskell同页的人物语境吻合。保留Haskell拼写作书内锚点，在卡片中并列权威形式；无相同类型既有KU，且不与work候选cand-6414混合。外部记录只用于身份，不验证Haskell所述十六幅画及赞助关系。
- cand-1294（H.csv#10；Henri III of France）：原new组复核，group=`new-person:france-henri-iii-of-6f746d232e`。第9章p.255正文及索引H.csv#10均称Henri III of France；语境明确为1574年到访Mira的法国国王。它与Henri IV候选cand-1295为不同君主；同段作品、事件和地点候选保持各自类型，不并入人物组。无同类型既有KU。
- cand-1296（H.csv#12；Henrietta Maria, Queen of England）：原new组复核，group=`new-person:england-henrietta-maria-of-b9baa37f48`。第7章p.179正文在Charles之后以‘the Queen’指称人物；索引H.csv#12标为Henrietta Maria, Queen of England，S2提及也已将这些指代连到同一候选。保留索引名并以Charles的王后语境支持身份；不与未具名Cardinal Barberini候选cand-6757或Queen’s Chapel地点cand-6759合并。无同类型既有KU。
- cand-1297（H.csv#13；Hervey, Sir Robert）：原new组复核，group=`new-person:hervey-robert-b62bf2d0f9`。第10章p.305正文称Sir Robert Hervey；索引H.csv#13将此人物定位于同页。Haskell同时提及Canaletto为他绘制的二十幅景观，但相应cand-9220是work类型且身份仍待证；人物和作品候选分开。与cand-1298的Lord Hervey不因同姓合并：本候选有不同给名与称谓，目前没有同一身份证据。无相同类型既有KU。
- cand-1298（H.csv#14；Hervey, Lord）：undecided改为new，group=`new-person:john-hervey-2nd-baron-hervey-20261018`。第14章p.349的Lord Hervey处于Algarotti 1736年赴伦敦后与其交往的语境。Westminster School Archive & Collections规范记录将John Hervey（1696–1743）列为该时期的Lord Hervey，记录其1723年起以Lord Hervey称呼，权威记录号GB-2014-WSA-00767；该年代与书内语境相合。现有KU中无该人物，改为new身份组，并与Sir Robert Hervey候选cand-1297分开，不将Haskell对交往的叙述当作外部证实。
- cand-1299（H.csv#15；Hildebrandt, Lucas von）：原new组复核，group=`new-person:hildebrandt-lucas-von-425ee5c0e1`。第7章p.201正文和索引H.csv#15称Lucas von Hildebrandt。MAK Collection Online人物记录规范名为Johann Lucas von Hildebrandt，姓名与时代相符；Haskell在此只把两座Belvederes归于Lucas von Hildebrandt。无相同类型既有KU；卡片保存书内称名及外部规范全名，不将外部生平资料扩展为本书断言。
- cand-1300（H.csv#16；Hill, Samuel）：原new组复核，group=`new-person:hill-samuel-3c347d356a`。第10章pp.290n、304n共三处提及Samuel Hill，mention账本都映射至cand-1300；第10章p.304注2的S2候选记Smith向Samuel Hill发送Piazzetta作品。全名在原文注释中出现，索引H.csv#16汇总两页定位。无相同类型既有KU；所引Chaloner材料仍未独立查阅。
- cand-1301（H.csv#17；Hogarth, William）：原new组复核，group=`new-person:hogarth-william-51254bc070`。第10章p.279正文以Hogarth姓氏提及画家；索引H.csv#17给出William Hogarth。保留索引身份形式，不从该短提及扩写事实；无相同类型既有KU。
- cand-1302（H.csv#18；Honthorst, Gerrit van）：原new组复核，group=`new-person:gerrit-honthorst-van-1acc9537ec`。第4章p.95正文以Honthorst姓氏列入Giustiniani对直接使用模特画家的比较；索引H.csv#18展开为Gerrit van Honthorst。正文和索引共同支持书内身份组；无相同类型既有KU。
- cand-1303（H.csv#19；Horace）：undecided改为new，group=`new-person:horace-roman-poet-20261018`。第13章p.333以Horace的诗篇为古代作品范例，第14章p.360明确提及Horace的Non omnis moriar；两处跨章语境指向罗马诗人，而非既有Horace Walpole人物KU（units/persons/horace-walpole，cand-2798）。本候选没有相同类型既有KU，改为独立的Horace罗马诗人new组；不把诗句引述扩展为对纪念铭文的外部核实。

外部身份比较仅用于消歧，未据此核实S2断言或建立正式关系：[Deutsche Biographie / GND Harrach](https://www.deutsche-biographie.de/sfz26099.html)，[Treccani Harrach](https://www.treccani.it/enciclopedia/harrach/)，[Uffizi Theodor Helmbreker](https://www.uffizi.it/en/artworks/rustic-scene)，[Westminster School Archive John Hervey](https://collections.westminster.org.uk/index.php/hervey-john-hervey-baron-1696-1743)，[MAK Johann Lucas von Hildebrandt](https://sammlung.mak.at/en/artist/hildebrandt-johann-lucas-von_30775)。

本组13个候选均为new人物组；其中9条直接S2关系候选仍待S6，cand-1297对应的work候选cand-9220仍为独立待证对象。新增4条外部身份记录，待S4与各自人物KU映射；本批无正式关系。


<a id="s3-ignatius-leopold-crosschapter-groups-20261018"></a>

### S3人物跨章身份组：St Ignatius与两位Leopold（2026-10-18）

- cand-1309（I.csv#0，Ignatius, St）由undecided改为new，group=`new-person:st-ignatius-jesuit-founder-20261018`。第3章p.64、p.89–91将Ignatius置于耶稣会与其创立者语境，第20章后记p.399再次称St Ignatius；Vatican身份记录支持其为St Ignatius of Loyola。未发现同类型既有人物KU。
- cand-1397（L.csv#54，Leopold I, Grand Duke of Tuscany）与cand-8097（第8章注3所引1767年展览题名中的Pietro Leopoldo）归为一个new人物组`new-person:pietro-leopoldo-grand-duke-of-tuscany-20261018`。第15章p.366的1777年后语境称Grand Duke of Tuscany；Treccani DBI记录Pietro Leopoldo自1765年任托斯卡纳大公、后来为皇帝Leopold II。该组与HRE Leopold I分开。
- cand-1398（L.csv#55，Leopold I, Holy Roman Emperor）由undecided改为new，group=`new-person:leopold-i-holy-roman-emperor-20261018`。第7章p.193明确其1658–1705年统治期；Deutsche Biographie / GND 118571869身份吻合，现无同类型KU。

外部身份来源：[Vatican St Ignatius](https://www.vatican.va/roman_curia/congregations/ccatheduc/documents/rc_con_ccatheduc_doc_20021119_press-release_en.html)、[Treccani DBI Pietro Leopoldo](https://www.treccani.it/enciclopedia/pietro-leopoldo-d-asburgo-lorena-granduca-di-toscana-poi-imperatore-del-sacro-romano-impero-come-leopoldo-ii_%28Dizionario-Biografico%29/)、[Deutsche Biographie Leopold I](https://www.deutsche-biographie.de/gnd118571869.html?language=en)。外证仅用于身份消歧；14条直接S2关系候选留待S6；本批不新增KU或正式关系。


<a id="s4-person-direct-endpoints-h-section-20261018"></a>

### S4人物登记：H段跨章身份组（2026-10-18）

- cand-1287（new-person:der-hamen-juan-van-98401ebaa1）→ [胡安·范德尔·哈门（Juan van der Hamen）](../../../04-knowledge/units/persons/juan-van-der-hamen.md)。索引H.csv#2与所列章节页段构成书内身份依据；直接S2关系候选：无直接S2关系候选；关系均留待S6。无正式关系写入。
- cand-1288（new-person:frederick-george-handel-b7a9ead66a）→ [乔治·弗雷德里克·亨德尔（George Frederick Handel）](../../../04-knowledge/units/persons/george-frederick-handel.md)。索引H.csv#3与所列章节页段构成书内身份依据；直接S2关系候选：无直接S2关系候选；关系均留待S6。无正式关系写入。
- cand-1291（new-person:aloys-thomas-raimund-harrach-20261018）→ [阿洛伊斯·托马斯·赖蒙德·哈拉赫（Aloys Thomas Raimund Harrach）](../../../04-knowledge/units/persons/aloys-thomas-raimund-harrach.md)。索引H.csv#7与所列章节页段构成书内身份依据；外部身份入口：Deutsche Biographie / GND（132626748）；直接S2关系候选：st-chp7-p200-v-harrach-continues-process-after-1728,st-chp7-p200-n7-harrach-patronage；关系均留待S6。无正式关系写入。
- cand-1293（new-person:helmbrecker-theodor-5737710433）→ [特奥多尔·赫尔姆布雷克（Theodor Helmbreker）](../../../04-knowledge/units/persons/theodor-helmbreker.md)。索引H.csv#9与所列章节页段构成书内身份依据；外部身份入口：Uffizi Galleries（https://www.uffizi.it/en/artworks/rustic-scene）；直接S2关系候选：st-chp6-p158-helmbrecker-admired,st-chp6-p158-helmbrecker-pictures-for-marucelli；关系均留待S6。无正式关系写入。
- cand-1294（new-person:france-henri-iii-of-6f746d232e）→ [法国国王亨利三世（Henri III of France）](../../../04-knowledge/units/persons/henri-iii-of-france.md)。索引H.csv#10与所列章节页段构成书内身份依据；直接S2关系候选：无直接S2关系候选；关系均留待S6。无正式关系写入。
- cand-1296（new-person:england-henrietta-maria-of-b9baa37f48）→ [亨利埃塔·玛丽亚（Henrietta Maria）](../../../04-knowledge/units/persons/henrietta-maria.md)。索引H.csv#12与所列章节页段构成书内身份依据；直接S2关系候选：st-chp7-p179-i17；关系均留待S6。无正式关系写入。
- cand-1297（new-person:hervey-robert-b62bf2d0f9）→ [罗伯特·赫维爵士（Sir Robert Hervey）](../../../04-knowledge/units/persons/robert-hervey.md)。索引H.csv#13与所列章节页段构成书内身份依据；直接S2关系候选：无直接S2关系候选；关系均留待S6。无正式关系写入。
- cand-1298（new-person:john-hervey-2nd-baron-hervey-20261018）→ [约翰·赫维（第二代赫维男爵）（John Hervey, 2nd Baron Hervey of Ickworth）](../../../04-knowledge/units/persons/john-hervey-2nd-baron-hervey.md)。索引H.csv#14与所列章节页段构成书内身份依据；外部身份入口：Westminster School Archive & Collections（GB-2014-WSA-00767）；直接S2关系候选：st-chp14-p349-social-advances-hervey；关系均留待S6。无正式关系写入。
- cand-1299（new-person:hildebrandt-lucas-von-425ee5c0e1）→ [约翰·卢卡斯·冯·希尔德布兰特（Johann Lucas von Hildebrandt）](../../../04-knowledge/units/persons/lucas-von-hildebrandt.md)。索引H.csv#15与所列章节页段构成书内身份依据；外部身份入口：MAK Collection Online（https://sammlung.mak.at/en/artist/hildebrandt-johann-lucas-von_30775）；直接S2关系候选：st-chp7-p201-v-belvederes-by-hildebrandt；关系均留待S6。无正式关系写入。
- cand-1300（new-person:hill-samuel-3c347d356a）→ [塞缪尔·希尔（Samuel Hill）](../../../04-knowledge/units/persons/samuel-hill.md)。索引H.csv#16与所列章节页段构成书内身份依据；直接S2关系候选：st-chp10-p304-note2-piazzetta-works-to-hill；关系均留待S6。无正式关系写入。
- cand-1301（new-person:hogarth-william-51254bc070）→ [威廉·霍加斯（William Hogarth）](../../../04-knowledge/units/persons/william-hogarth.md)。索引H.csv#17与所列章节页段构成书内身份依据；直接S2关系候选：无直接S2关系候选；关系均留待S6。无正式关系写入。
- cand-1302（new-person:gerrit-honthorst-van-1acc9537ec）→ [赫里特·范·洪特霍斯特（Gerrit van Honthorst）](../../../04-knowledge/units/persons/gerrit-van-honthorst.md)。索引H.csv#18与所列章节页段构成书内身份依据；直接S2关系候选：无直接S2关系候选；关系均留待S6。无正式关系写入。
- cand-1303（new-person:horace-roman-poet-20261018）→ [贺拉斯（Horace）](../../../04-knowledge/units/persons/horace.md)。索引H.csv#19与所列章节页段构成书内身份依据；直接S2关系候选：st-chp14-p360-inscription-adapts-horace；关系均留待S6。无正式关系写入。

本批登记13个S3 new人物组、13条候选映射和26条source_backed名称字段；另保留4条外部身份导航行；对应稳定标识仅在alignment.csv，未写入enrichment.jsonl；9条直接S2关系候选留待S6，4条外部身份记录映射至相应KU。cand-9220作品候选继续独立待证；本批未新增正式关系或扩大S2断言。

登记后person类型S4为466组/557条已登记、601组/603条待登记；全书为875组/1,051条已登记、3,900组/3,915条待登记，KU=1894。


<a id="s4-person-direct-endpoints-ignatius-leopold-groups-20261018"></a>

### S4人物直接关系端点登记：Ignatius与两位Leopold（2026-10-18）

- `cand-1309`（`new-person:st-ignatius-jesuit-founder-20261018`）→ [圣依纳爵·罗耀拉（Ignatius of Loyola）](../../../04-knowledge/units/persons/ignatius-of-loyola.md)。索引I.csv#0及所列书内页段构成来源身份依据；外部身份入口仅作消歧（Vatican, Congregation for Catholic Education）；直接S2关系候选：st-chp3-seci-l16-24-gregory-canonisation-ignatius, st-chp3-seciv-l130-139-scenes-depict-ignatius, st-chp3-seciv-l141-150-pozzo-adapted-reference-to-ignatius, st-chp3-seciv-l141-150-pozzo-explained-honour-to-ignatius, st-chp3-seciv-l152-163-chapel-conceived-for-founder, st-chp20-p399-nadal-engravings-commission-and-influence, st-chp3-seciv-l141-150-ignatius-encouraged-disciples-rhetorical-question, st-chp3-seciv-l141-150-fresco-depicts-ignatius-transmitting-ray，留待S6逐条裁决。无正式关系写入。
- `cand-1397`、`cand-8097`（`new-person:pietro-leopoldo-grand-duke-of-tuscany-20261018`）→ [彼得罗·莱奥波尔多（Pietro Leopoldo）](../../../04-knowledge/units/persons/pietro-leopoldo-grand-duke-of-tuscany.md)。索引L.csv#54及所列书内页段构成来源身份依据；外部身份入口仅作消歧（Treccani, Dizionario Biografico degli Italiani）；直接S2关系候选：st-chp15-p366-grandduke-funds-petrarch-galileo-statues, st-chp15-p366-grandduke-pays-for-galileo-statue，留待S6逐条裁决。无正式关系写入。
- `cand-1398`（`new-person:leopold-i-holy-roman-emperor-20261018`）→ [利奥波德一世（Leopold I, Holy Roman Emperor）](../../../04-knowledge/units/persons/leopold-i-holy-roman-emperor.md)。索引L.csv#55及所列书内页段构成来源身份依据；外部身份入口仅作消歧（Deutsche Biographie / GND）；直接S2关系候选：st-chp7-p193-leopold-bequest, st-chp7-p193-leopold-commissions-stage-sets, st-chp7-p193-leopold-commissions-wing, st-chp7-p193-leopold-i-patronage，留待S6逐条裁决。无正式关系写入。

本批登记3个S3 new人物组、4条候选映射、7条source_backed名称字段和3条unverified外部身份导航字段；外部标识只留在alignment.csv。14条直接S2关系候选继续待S6；Pietro Leopoldo（cand-1397、cand-8097）合为一组，与Holy Roman Emperor Leopold I（cand-1398）分开。本批未新增正式关系或扩写原书事实。

登记后person类型S4为469组/561条已登记、598组/599条待登记；全书为878组/1,055条已登记、3,897组/3,911条待登记，KU=1897。


<a id="s4-person-direct-endpoints-huber-imperiali-jabach-james-johann-20261018"></a>

### S4人物直接关系端点登记：Huber、Imperiali、Jabach、James III与Johann Georg III（2026-10-18）

- `cand-1306`（`new-person:huber-jean-79331e446d`）→ [让·于贝尔（Jean Huber）](../../../04-knowledge/units/persons/jean-huber.md)。索引H.csv#22与所列书内页段构成身份及来源锚点；直接S2关系候选st-chp15-p370-huber-engraving-created-by-huber留待S6逐条裁决，不登记正式关系。
- `cand-1312`（`new-person:francesco-imperiali-98d434bd1c`）→ [弗朗切斯科·因佩里亚利（Francesco Imperiali）](../../../04-knowledge/units/persons/francesco-imperiali.md)。索引I.csv#3与所列书内页段构成身份及来源锚点；直接S2关系候选st-chp10-p288-n02-imperiali-monument留待S6逐条裁决，不登记正式关系。
- `cand-1316`（`new-person:everard-jabach-3e5e428848`）→ [埃弗哈德·雅巴赫（Everard Jabach）](../../../04-knowledge/units/persons/everard-jabach.md)。索引J，K.csv#0与所列书内页段构成身份及来源锚点；直接S2关系候选st-chp7-p184-i02留待S6逐条裁决，不登记正式关系。
- `cand-1318`（`new-person:england-iii-james-of-d1d84625ab`）→ [英格兰的詹姆斯三世（James III of England）](../../../04-knowledge/units/persons/james-iii-of-england.md)。索引J，K.csv#2与所列书内页段构成身份及来源锚点；直接S2关系候选st-chp8-p203-belloni-hospitality-james-iii留待S6逐条裁决，不登记正式关系。
- `cand-1324`（`new-person:georg-iii-johann-of-saxony-d06916a347`）→ [萨克森的约翰·格奥尔格三世（Johann Georg III of Saxony）](../../../04-knowledge/units/persons/johann-georg-iii-of-saxony.md)。索引J，K.csv#8与所列书内页段构成身份及来源锚点；直接S2关系候选st-chp7-p194-cadani-employed-dresden留待S6逐条裁决，不登记正式关系。

本批登记5个S3 new人物组、5条候选映射和10条source_backed名称字段；5条直接S2关系候选留待S6。本批无外部身份行、无正式关系、无来源登记变更。

登记后person类型S4为474组/566条已登记、593组/594条待登记；全书为883组/1,060条已登记、3,892组/3,906条待登记，KU=1902。


<a id="s4-person-direct-endpoints-john-sobieski-leblon-batch-20261018"></a>

### S4人物直接关系端点登记：John Sobieski、Inigo Jones、La Fosse、Langetti与Le Blon（2026-10-18）

- `cand-1332`（`new-person:john-of-poland-sobieski-831a5af6fd`）→ [波兰国王扬·索别斯基（John Sobieski, King of Poland）](../../../04-knowledge/units/persons/john-sobieski-king-of-poland.md)。索引J，K.csv#16与所列书内页段构成身份和来源锚点；直接S2关系候选st-chp5-p129-king-john-victory-group, st-chp5-p129-john-sobieski-widow留待S6逐条裁决，不登记正式关系。
- `cand-1335`（`new-person:inigo-jones-a18fbfb698`）→ [伊尼戈·琼斯（Inigo Jones）](../../../04-knowledge/units/persons/inigo-jones.md)。索引J，K.csv#19与所列书内页段构成身份和来源锚点；直接S2关系候选st-chp10-p309-five-pictures-after-jones留待S6逐条裁决，不登记正式关系。
- `cand-1343`（`new-person:charles-de-fosse-la-0e31b8e216`）→ [夏尔·德·拉福斯（Charles de la Fosse）](../../../04-knowledge/units/persons/charles-de-la-fosse.md)。索引L.csv#0与所列书内页段构成身份和来源锚点；直接S2关系候选st-chp10-p284-la-fosse-lodged-and-aged, st-chp10-notes-p284n4-la-fosse-remark-to-ricci留待S6逐条裁决，不登记正式关系。
- `cand-1363`（`new-person:battista-giovanni-langetti-0431e4284a`）→ [乔瓦尼·巴蒂斯塔·兰盖蒂（Giovanni Battista Langetti）](../../../04-knowledge/units/persons/giovanni-battista-langetti.md)。索引L.csv#20与所列书内页段构成身份和来源锚点；直接S2关系候选st-chp8-p234-langetti-report留待S6逐条裁决，不登记正式关系。
- `cand-1375`（`new-person:christoffel-jakob-leblon-559fe2b5aa`）→ [雅各布·克里斯托费尔·勒布隆（Jakob Christoffel Le Blon）](../../../04-knowledge/units/persons/jakob-christoffel-le-blon.md)。索引L.csv#32与所列书内页段构成身份和来源锚点；直接S2关系候选st-chp20-p408-byam-shaw-identifies-le-blon留待S6逐条裁决，不登记正式关系。

本批登记5个S3 new人物组、5条候选映射和10条source_backed名称字段；7条直接S2关系候选留待S6。Langetti条目同时保留Haskell转述Ratti及同注提出的年代矛盾；La Fosse评语保留Levey/Walpole转引和Haskell推测；Le Blon保留后记拼写变体及Byam Shaw归属。本批无外部身份行、无正式关系、无来源登记变更。

登记后person类型S4为479组/571条已登记、588组/589条待登记；全书为888组/1,065条已登记、3,887组/3,901条待登记，KU=1907。


<a id="s4-person-direct-endpoints-le-nain-lorca-batch-20261018"></a>

### S4人物直接关系端点登记：Le Nain、Le Vau、Lelli、Lely与Lorca（2026-10-18）

- `cand-1377`（`new-person:le-louis-nain-147a6ee7a9`）→ [路易·勒南（Louis Le Nain）](../../../04-knowledge/units/persons/louis-le-nain.md)。索引L.csv#34（页码122, 184）与书内页段构成身份锚点；直接S2关系候选st-chp7-p175-i02留待S6裁决，不登记正式关系。
- `cand-1378`（`new-person:le-louis-vau-324972e817`）→ [路易·勒沃（Louis Le Vau）](../../../04-knowledge/units/persons/louis-le-vau.md)。索引L.csv#35（页码187）与书内页段构成身份锚点；直接S2关系候选st-chp7-p187-i11, st-chp7-p187-i12留待S6裁决，不登记正式关系。
- `cand-1383`（`new-person:ercole-lelli-49868de830`）→ [埃尔科莱·莱利（Ercole Lelli）](../../../04-knowledge/units/persons/ercole-lelli.md)。索引L.csv#40（页码351）与书内页段构成身份锚点；直接S2关系候选st-chp14-p351-bologna-subjects留待S6裁决，不登记正式关系。
- `cand-1384`（`new-person:lely-peter-2424b887f2`）→ [彼得·莱利爵士（Sir Peter Lely）](../../../04-knowledge/units/persons/sir-peter-lely.md)。索引L.csv#41（页码122n）与书内页段构成身份锚点；直接S2关系候选st-chp5-notes-l135-lely-admiration留待S6裁决，不登记正式关系。
- `cand-1436`（`new-person:bernardino-lorca-c2952a5e49`）→ [贝尔纳迪诺·洛尔卡（Bernardino Lorca）](../../../04-knowledge/units/persons/bernardino-lorca.md)。索引L.csv#93（页码135n）与书内页段构成身份锚点；直接S2关系候选st-chp5-notes-l138-lorca-friend留待S6裁决，不登记正式关系。
- 定位值差异处理：`cand-1377`原候选快照为`133, 184`，当前`L.csv#34`原行为`122, 184`；`cand-1384`原候选快照为`135n`，当前`L.csv#41`原行为`122n`。按`build_entity_candidates.py`的字段生成规则，仅将`entity-candidates.csv`中的派生`index_page_range`同步到当前索引原行；原索引文件未改，旧值与更正理由保留在本记录及对应alignment resolution_note中，S3身份分组不变。

本批登记5个S3 new人物组、5条候选映射和10条source_backed名称字段；6条直接S2关系候选留待S6。保留Le Nain影响表述的未指明来源、Lelli正文异拼、Lely的推测及目录归属限定、Lorca书信转引状态。本批无外部身份行、无正式关系、无来源登记变更。

登记后person类型S4为484组/576条已登记、583组/584条待登记；全书为893组/1,070条已登记、3,882组/3,896条待登记，KU=1912。


<a id="s4-person-direct-endpoints-loredan-lovisa-batch-20261018"></a>

### S4人物直接关系端点登记：Loredan、Lorenzi与Lovisa（2026-10-18）

- `cand-1437`（`new-person:antonio-loredan-d07ef14ba2`）→ [安东尼奥·洛雷丹（Antonio Loredan）](../../../04-knowledge/units/persons/antonio-loredan.md)。索引L.csv#94（页码256）与书内页段支持source-local人物登记；直接S2关系候选st-chp9-p256-antonio-loredan-pompey-comparison留待S6裁决，不登记正式关系。
- `cand-1438`（`new-person:loredan-pietro-d8a0532873`）→ [皮耶特罗·洛雷丹（Pietro Loredan）](../../../04-knowledge/units/persons/pietro-loredan.md)。索引L.csv#95（页码256）与书内页段支持source-local人物登记；直接S2关系候选st-chp9-p256-pietro-loredan-1724-mucius-comparison留待S6裁决，不登记正式关系。
- `cand-1439`（`new-person:francesco-lorenzi-3ec9131e80`）→ [弗朗切斯科·洛伦齐（Francesco Lorenzi）](../../../04-knowledge/units/persons/francesco-lorenzi.md)。索引L.csv#96（页码255n）与书内页段支持source-local人物登记；直接S2关系候选st-chp9-p255-lorenzi-scheme-report留待S6裁决，不登记正式关系。
- `cand-1452`（`new-person:domenico-lovisa-46b41e2e35`）→ [多梅尼科·洛维萨（Domenico Lovisa）](../../../04-knowledge/units/persons/domenico-lovisa.md)。索引L.csv#110（页码332, 333）与书内页段支持source-local人物登记；直接S2关系候选st-chp13-p332-lovisa-gran-teatro-publication-and-illustrations, st-chp13-p333-lovisa-book-sponsored-example留待S6裁决，不登记正式关系。
- `cand-1441`（`new-person:lorraine-of-dc18d315ff`）保留S4待证：索引L.csv#99与第9章p.267只给出“Duke of Lorraine”爵号，未给个人姓名；alignment resolution_note记录不建KU及其待补身份依据。

本批登记4个S3 new人物组、4条候选映射和8条source_backed名称字段；5条直接S2关系候选留待S6，另1组因身份锚点仅为未具名爵号而保持待证。保留Antonio的日期限定、Pietro演说引文未独立查阅状态、Lorenzi的嵌套转述和可能伪托、Lovisa出版与赞助两种角色及标题OCR更正。本批无外部身份行、无正式关系、无来源登记变更。

登记后person类型S4为488组/580条已登记、579组/580条待登记；全书为897组/1,074条已登记、3,878组/3,892条待登记，KU=1916。


<a id="s4-person-direct-endpoints-maffei-m-20261018"></a>

### S4人物直接关系端点登记：Maffei、Magalotti、Magnasco、Magni与Maidalchini（2026-10-18）

- `cand-1486`（`new-person:francesco-maffei-fbe66c73c0`）→ [弗朗切斯科·马费伊（Francesco Maffei）](../../../04-knowledge/units/persons/francesco-maffei.md)。索引M.csv#23（页码232, 248）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp9-p248-maffei-governor-canvases留待S6逐条裁决，不登记正式关系。
- `cand-1488`（`new-person:lorenzo-magalotti-fa04976cc4`）→ [洛伦佐·马加洛蒂（Lorenzo Magalotti）](../../../04-knowledge/units/persons/lorenzo-magalotti.md)。索引M.csv#25（页码31, 42）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp2-sec-ii-l3-8-magalotti-cardinal, st-chp2-secii-l127-139-magalotti-chapel-materials留待S6逐条裁决，不登记正式关系。
- `cand-1492`（`new-person:alessandro-magnasco-ba9ee3bdc8`）→ [亚历山德罗·马格纳斯科（Alessandro Magnasco）](../../../04-knowledge/units/persons/alessandro-magnasco.md)。索引M.csv#29（页码404）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp20-p404-inventories-magnasco-limited-patronage留待S6逐条裁决，不登记正式关系。
- `cand-1493`（`new-person:magni-pietro-d0f4dde5f1`）→ [彼得罗·马尼（Pietro Magni）](../../../04-knowledge/units/persons/pietro-magni.md)。索引M.csv#30（页码216）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp8-p216-magni-working-for-marquis-mantua留待S6逐条裁决，不登记正式关系。
- `cand-1495`（`new-person:francesco-maidalchini-e5968ef278`）→ [弗朗切斯科·马伊达尔基尼（Francesco Maidalchini）](../../../04-knowledge/units/persons/francesco-maidalchini.md)。索引M.csv#32（页码147）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp6-p147-francesco-maidalchini-selected留待S6逐条裁决，不登记正式关系。

本批登记5个S3 new人物组、5条候选映射和10条source_backed名称字段；6条直接S2关系候选留待S6。Maffei两章指称、Magalotti两处正文形式均按各自既有身份组处理；Magalotti与Maidalchini的相关已登记人物入口只作导航。本批未新增外部身份行、正式关系、来源登记或S2断言。

登记后person类型S4为493组/585条已登记、574组/575条待登记；全书为902组/1,079条已登记、3,873组/3,887条待登记，KU=1921。


<a id="s4-person-direct-endpoints-n-section-20261018"></a>

### S3复核与S4人物直接端点登记：N索引组（2026-10-18）

- S3更正：`cand-1741`（索引N.csv#21，Benedict Nicolson）由new改为same → [Lionel Benedict Nicolson](../../../04-knowledge/units/persons/benedict-nicolson.md)。现有same候选`cand-3732`已映射到该KU；第4章注3的姓名和语境与章前相同。原new判断及理由留在alignment行历史；直接候选`st-chp4-intro-notes-03-nicolson-hypothesis`仍待S6，因书信端点`cand-5507`未决。
- `cand-1736`（`new-person:balthasar-neumann-de17cb965f`）→ [巴尔塔萨·诺伊曼（Balthasar Neumann）](../../../04-knowledge/units/persons/balthasar-neumann.md)。索引N.csv#16（页码296）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp10-p296-neumann-builds-residenz留待S6逐条裁决，不登记正式关系。
- `cand-1764`（`new-person:de-francois-noyers-sublet-c3e504e823`）→ [弗朗索瓦·苏布莱·德·努瓦耶（François Sublet de Noyers）](../../../04-knowledge/units/persons/francois-sublet-de-noyers.md)。索引N.csv#44（页码112）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp4-sec-ii-p112-denoyers-assessment-of-cassiano留待S6逐条裁决，不登记正式关系。
- `cand-1742`（`new-person:de-marechal-noailles-5dbb196acf`）→ [诺阿耶元帅（Maréchal de Noailles）](../../../04-knowledge/units/persons/marechal-de-noailles.md)。索引N.csv#22（页码200）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp7-p200-v-noailles-secures-de-ferrari-at-marseilles留待S6逐条裁决，不登记正式关系。
- `cand-1749`（`new-person:desiderio-monsu-francois-frenchman-nome-fr-31a920c8cc`）→ [弗朗索瓦·诺梅（François Nomé (Monsù Desiderio)）](../../../04-knowledge/units/persons/francois-nome-monsu-desiderio.md)。索引N.csv#29（页码213）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp8-p213-nome-inventory-described-as-lorenese留待S6逐条裁决，不登记正式关系。
- `cand-1731`（`new-person:negri-pietro-d97f9be175`）→ [彼得罗·内格里（Pietro Negri）](../../../04-knowledge/units/persons/pietro-negri.md)。索引N.csv#11（页码219, 294）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp8-p219-negri-san-rocco-picture, st-chp8-p219-negri-enters-noah-competition留待S6逐条裁决，不登记正式关系。
- `cand-1735`（`new-person:neri-vincenzo-94f1ade31a`）→ [温琴佐·内里（Vincenzo Neri）](../../../04-knowledge/units/persons/vincenzo-neri.md)。索引N.csv#15（页码136）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp5-p136-neri-and-friends-immortalised-in-plate-22a留待S6逐条裁决，不登记正式关系。
- `cand-1756`（`new-person:francesco-novelli-ae0651e151`）→ [弗朗切斯科·诺韦利（Francesco Novelli）](../../../04-knowledge/units/persons/francesco-novelli.md)。索引N.csv#36（页码371）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp15-p371-rembrandt-prints-influenced-novelli留待S6逐条裁决，不登记正式关系。
本批S4登记7个S3 new人物组、7条候选映射和14条source_backed名称字段；9条直接S2关系候选留待S6。Noailles按书内称谓保留为source-local身份，未补给名或外部人物匹配；Nomé称号和Negri跨章姓名按原书语境记录。本批未新增外部身份行、正式关系、来源登记或S2断言。

登记后person类型S4为500组/592条已登记、566组/567条待登记；全书为909组/1,086条已登记、3,865组/3,879条待登记，KU=1928。


<a id="s4-person-direct-endpoints-o-section-20261018"></a>

### S3复核与S4人物直接端点登记：O索引组（2026-10-18）

- cand-1767（new-person:oderisi-roberto-9cef78b777）→ [罗伯托·奥德里西（Roberto Oderisi）](../../../04-knowledge/units/persons/roberto-oderisi.md)。索引O.csv#1（页码107）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp4-sec-ii-l101-107-oderisi-frescoes-ascribed留待S6逐条裁决，不登记正式关系。
- cand-1769（new-person:livio-odescalchi-2f323704d5）→ [利维奥·奥德斯卡尔基（Livio Odescalchi）](../../../04-knowledge/units/persons/livio-odescalchi.md)。索引O.csv#3（页码98）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp4-sec-i-l35-40-sale-to-livio留待S6逐条裁决，不登记正式关系。
- cand-1779（new-person:olivieri-paolo-pietro-b164336a9d）→ [彼得罗·保罗·奥利维耶里（Pietro Paolo Olivieri）](../../../04-knowledge/units/persons/pietro-paolo-olivieri.md)。索引O.csv#13（页码71）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp3-secii-l62-72-olivieri-authority-over-proposed-person留待S6逐条裁决，不登记正式关系。
- cand-1781（new-person:gilles-marie-oppenord-5d38abd47a）→ [吉尔-马里·奥本诺尔（Gilles-Marie Oppenord）](../../../04-knowledge/units/persons/gilles-marie-oppenord.md)。索引O.csv#15（页码285）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp10-p285-carriera-met-oppenord留待S6逐条裁决，不登记正式关系。
- cand-1788（new-person:alessandro-orsini-908fd3aa90）→ [亚历山德罗·奥尔西尼（Alessandro Orsini）](../../../04-knowledge/units/persons/alessandro-orsini.md)。索引O.csv#22（页码99）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp4-sec-ii-l10-13-alessandro-brother-of-paolo, st-chp4-sec-ii-l10-13-cassiano-close-friend-alessandro留待S6逐条裁决，不登记正式关系。
- cand-1793（new-person:ottley-william-young-211293a343）→ [威廉·扬·奥特利（William Young Ottley）](../../../04-knowledge/units/persons/william-young-ottley.md)。索引O.csv#28（页码377n）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp16-p377-note3-miniatures-described-by-ottley留待S6逐条裁决，不登记正式关系。
本批S4登记6个S3 new人物组、6条候选映射和12条source_backed名称字段；7条直接S2关系候选留待S6。人物身份按索引及本书正文建立，不据姓氏相似补并外部人物；未决的匿名人物、拟议建筑师及作品端点保持原状态。本批未新增外部身份行、正式关系、来源登记或S2断言。

登记后person类型S4为506组/598条已登记、560组/561条待登记；全书为915组/1,092条已登记、3,859组/3,873条待登记，KU=1934。


<a id="s4-person-direct-endpoints-p-early-section-20261018"></a>

### S3复核与S4人物直接端点登记：P索引前段组（2026-10-18）

- cand-1813（new-person:il-mirandolese-paltronieri-pietro-0e77ff1415）→ [彼得罗·帕尔特罗涅里（Pietro Paltronieri (il Mirandolese)）](../../../04-knowledge/units/persons/pietro-paltronieri.md)。索引P.csv#12（页码289n）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp10-p289-note1-paltronieri-bolognese, st-chp10-p289-note1-row06-artist1留待S6逐条裁决，不登记正式关系。
- cand-1825（new-person:francesco-panciatichi-senator-bf360bf677）→ [弗朗切斯科·潘恰蒂基（Senator Francesco Panciatichi）](../../../04-knowledge/units/persons/francesco-panciatichi.md)。索引P.csv#24（页码212n）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp8-p212-n5-panciatichi-nicola-kinship, st-chp8-p212-n5-panciatichi-office留待S6逐条裁决，不登记正式关系。
- cand-1841（new-person:antonio-domenico-parodi-domenico-parodi-741540edee）→ [多梅尼科·安东尼奥·帕罗迪（Domenico Antonio Parodi）](../../../04-knowledge/units/persons/domenico-antonio-parodi.md)。索引P.csv#41（页码200, 201）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp7-p200-v-parodi-trip-to-england-failed, st-chp7-p201-v-parodi-made-statues-for-hall-and-gardens留待S6逐条裁决，不登记正式关系。
- cand-1843（new-person:lorenzo-pasinelli-901ba3712c）→ [洛伦佐·帕西内利（Lorenzo Pasinelli）](../../../04-knowledge/units/persons/lorenzo-pasinelli.md)。索引P.csv#43（页码197）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp7-p197-exeter-collected-pasinelli-bologna留待S6逐条裁决，不登记正式关系。
- cand-1853（new-person:hunchback-leonardo-pasquetti-leonardo-pasq-52e202de52）→ [莱奥纳多·帕斯奎蒂（Leonardo Pasquetti）](../../../04-knowledge/units/persons/leonardo-pasquetti.md)。索引P.csv#53（页码346）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp13-p346-toni-would-buy-prints-from-pasquetti留待S6逐条裁决，不登记正式关系。
- cand-1860（new-person:jacopo-pedozzi-ba3154b82f）→ [雅各布·佩多齐（Padre Jacopo Pedozzi）](../../../04-knowledge/units/persons/jacopo-pedozzi.md)。索引P.csv#61（页码270）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp9-p270-pedozzi-reputation-and-canaletto-patron留待S6逐条裁决，不登记正式关系。
- cand-1899（new-person:del-giovanni-pian-f2cac6631e）→ [乔瓦尼·德尔·皮安（Giovanni del Pian）](../../../04-knowledge/units/persons/giovanni-del-pian.md)。索引P.csv#100（页码376）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp16-p376-del-pian-maker-of-print-series留待S6逐条裁决，不登记正式关系。
本批S4登记7个S3 new人物组、7条候选映射和15条source_backed名称字段；10条直接S2关系候选留待S6。跨页姓名形式按本书索引及对应正文定位归组；Paltronieri的Petoni为Haskell转述的拍卖目录异写，未当作独立核验。未决的海军将领、纪念碑项目、职务或版画组端点保持原状态；本批未新增外部身份行、正式关系、来源登记或S2断言。

登记后person类型S4为513组/605条已登记、553组/554条待登记；全书为922组/1,099条已登记、3,852组/3,866条待登记，KU=1941。


<a id="s4-person-direct-endpoints-p-middle-section-20261018"></a>

### S3复核与S4人物直接端点登记：P索引中段组（2026-10-18）

- S3依据修正：cand-1969原对齐说明称来源提供full personal name，现撤回。索引与正文仅称Baron de Pöllnitz，保留为source-local人物组，不补给名或外部匹配；原错误措辞保留于Git历史。
- cand-1925（new-person:bernard-picart-ecea5d104f）→ [贝尔纳·皮卡尔（Bernard Picart）](../../../04-knowledge/units/persons/bernard-picart.md)。索引P.csv#126（页码370）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp15-p370-picart-engravings-created-by-picart留待S6逐条裁决，不登记正式关系。
- cand-1929（new-person:antonio-pignatelli-innocent-xii-96ebb8305a）→ [安东尼奥·皮尼亚泰利（教宗英诺森十二世）（Antonio Pignatelli (Pope Innocent XII)）](../../../04-knowledge/units/persons/antonio-pignatelli-innocent-xii.md)。索引P.csv#130（页码221, 222）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp8-p221-innocent-xii-appoints-vice-legate, st-chp8-p222-innocent-xii-patron-of-ruffo留待S6逐条裁决，不登记正式关系。
- cand-1930（new-person:antonio-carlo-pilati-e89a18d7a3）→ [卡洛·安东尼奥·皮拉蒂（Carlo Antonio Pilati）](../../../04-knowledge/units/persons/carlo-antonio-pilati.md)。索引P.csv#131（页码318, 336）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp10-p318-pilati-expelled-from-venetian-territory, st-chp13-p336-pasquali-friend-of-pilati留待S6逐条裁决，不登记正式关系。
- cand-1931（new-person:giuseppe-pinacci-5cb62bbf30）→ [朱塞佩·皮纳奇（Giuseppe Pinacci）](../../../04-knowledge/units/persons/giuseppe-pinacci.md)。索引P.csv#132（页码191, 233n）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp7-p191-i22留待S6逐条裁决，不登记正式关系。
- cand-1937（new-person:francesco-piranesi-42d51ce564）→ [弗朗切斯科·皮拉内西（Francesco Piranesi）](../../../04-knowledge/units/persons/francesco-piranesi.md)。索引P.csv#138（页码366）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp15-p366-piranesi-engraves-subleyras-drawing留待S6逐条裁决，不登记正式关系。
- cand-1969（new-person:baron-de-pollnitz-745cce1347）→ [波尔尼茨男爵（Baron de Pöllnitz）](../../../04-knowledge/units/persons/baron-de-pollnitz.md)。索引P.csv#170（页码283）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp10-p283-pollnitz-praise留待S6逐条裁决，不登记正式关系。
- cand-1973（new-person:edward-poore-f2d0623bd5）→ [爱德华·普尔（Edward Poore）](../../../04-knowledge/units/persons/edward-poore.md)。索引P.csv#175（页码374）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp16-p374-armanni-introduces-poore, st-chp16-p374-note3-poore-letter-locator, st-chp16-p374-note3-poore-auction-sales留待S6逐条裁决，不登记正式关系。
- cand-1976（new-person:della-giacomo-porta-b53d418aa4）→ [贾科莫·德拉·波尔塔（Giacomo della Porta）](../../../04-knowledge/units/persons/giacomo-della-porta.md)。索引P.csv#178（页码71, 91）与对应书内页段支持source-local人物登记；直接S2关系候选st-chp3-secii-l62-72-gesualdo-appointed-own-architects, st-chp3-seciv-l152-163-della-porta-designed-uncompleted-altar留待S6逐条裁决，不登记正式关系。
本批S4登记8个S3 new人物组、8条候选映射和22条source_backed名称字段；13条直接S2关系候选留待S6。Antonio Pignatelli与Innocent XII按同一索引及第8章正文形式分组，与Innocent XIII分立；Pilati按第10、13章相同全名归组，其两处姓名字段按章页标记以保留各自证据定位并满足 enrichment 自然键；Pinacci的p.233注仅记录姓名与书目指引，不新增关系；Francesco Piranesi与Giovanni Battista Piranesi保持分立。Poore组保留Haskell索引和脚注的书内关联，不据未核的拍卖目录断言访客与拍卖藏家为同一外部个人。未决的画作组、藏画集合、书信、拍卖事件、提议建筑师及未完成祭坛对象均保持原状态。本批未新增外部身份行、正式关系、来源登记或S2断言。

登记后person类型S4为521组/613条已登记、545组/546条待登记；全书为930组/1,107条已登记、3,844组/3,858条待登记，KU=1949。


<a id="s4-person-direct-endpoints-p-late-section-20261018"></a>

### S3理由校正与S4人物直接端点登记：P索引末段（2026-10-18）

- S3理由校正：cand-2064正文拼作Ercole Proccaccini，索引为Procaccini, Ercole；以页段和索引对应支持source-local new组，保留拼写差异，并与已有Andrea Procaccini人物KU区分。cand-2069索引给出Samuel，p.320正文只写Puffendorf；此前声称正文提供完整姓名的理由撤回，具体著作仍未指明。cand-2072的Scipione与Pulzone来自同页相邻mention，合读为正文全名。三项决定均保持new，不据此新增外部身份匹配。
- cand-2064（new-person:ercole-procaccini-395244d722）→ [埃尔科莱·普罗卡奇尼（Ercole Procaccini）](../../../04-knowledge/units/persons/ercole-procaccini.md)。索引P.csv#267与列明的正文页段支持source-local人物登记；直接S2关系候选st-chp8-p216-storer-pupil-proccaccini留待S6逐条裁决，不登记正式关系。
- cand-2069（new-person:pufendorf-samuel-2430e8c679）→ [塞缪尔·冯·普芬多夫（Samuel Pufendorf）](../../../04-knowledge/units/persons/samuel-pufendorf.md)。索引P.csv#272与列明的正文页段支持source-local人物登记；直接S2关系候选st-chp10-p320-lodoli-taught-puffendorf-on-duties留待S6逐条裁决，不登记正式关系。
- cand-2072（new-person:pulzone-scipione-a1ff2a9238）→ [西皮奥内·普尔佐内（Scipione Pulzone）](../../../04-knowledge/units/persons/scipione-pulzone.md)。索引P.csv#275与列明的正文页段支持source-local人物登记；直接S2关系候选st-chp3-secii-l6-17-pious-ladies-introduced-pulzone留待S6逐条裁决，不登记正式关系。

本批登记3个S3 new人物组、3条候选映射和6条source_backed名称字段；3条直接S2关系候选留待S6，未新增正式关系、S2断言或来源。登记后person类型S4为524组/616条已登记、542组/543条待登记；全书为933组/1,110条已登记、3,841组/3,855条待登记，KU=1952。


<a id="s4-person-direct-endpoints-qr-early-20261018"></a>

### S3理由校正与S4人物直接端点登记：Q-R索引前段（2026-10-18）

- S3理由校正：cand-2073的正文全名和索引页码支持Quaini书内组，但原文将敬慕Louis XIV的说法明确作为转述，保留归因。cand-2089以p.366全名和p.365同章姓氏对齐Radicchio。cand-2090按Q-R.csv#17索引链接p.140注的Marchese Raggi，并与p.155注的Ferdinando Raggi书内形式相互参照；不与Q-R.csv#18的Monsignor Raggi合并，也不作外部身份匹配。cand-2096以同一封1708年1月31日书信的题头Vincenzo与续页署名Vincenzio归组，手稿未独立查阅。cand-2112以p.229姓氏Redi和p.230全名Francesco Redi，结合索引页段归组。五项S3决定均保持new，旧的自我匹配式说明已撤回并由上述证据依据替换。
- cand-2073（new-person:luigi-quaini-cdd63f39d2）→ [路易吉·奎尼（Luigi Quaini）](../../../04-knowledge/units/persons/luigi-quaini.md)。索引Q-R.csv#0与相应正文页段支持source-local人物登记；直接S2关系候选st-chp7-p189-i23-quaini留待S6逐条裁决，不登记正式关系。
- cand-2089（new-person:radicchio-vincenzo-36639ad243）→ [唐·文琴佐·拉迪基奥（Don Vincenzo Radicchio）](../../../04-knowledge/units/persons/don-vincenzo-radicchio.md)。索引Q-R.csv#16与相应正文页段支持source-local人物登记；直接S2关系候选st-chp15-p366-radicchio-account-authored-by, st-chp15-p366-radicchio-secretary-to-memmo留待S6逐条裁决，不登记正式关系。
- cand-2090（new-person:ferdinando-raggi-07e6d94c1b）→ [费迪南多·拉吉（Ferdinando Raggi）](../../../04-knowledge/units/persons/ferdinando-raggi.md)。索引Q-R.csv#17与相应正文页段支持source-local人物登记；直接S2关系候选st-chp5-notes-l143-raggi-patronage-loan, st-chp5-notes-l126-165-l143-raggi-loaned-five-pictures留待S6逐条裁决，不登记正式关系。
- cand-2096（new-person:ranuzzi-vincenzo-c540db0da6）→ [温琴佐·拉努齐（Vincenzo Ranuzzi）](../../../04-knowledge/units/persons/vincenzo-ranuzzi.md)。索引Q-R.csv#23与相应正文页段支持source-local人物登记；直接S2关系候选st-chp19-p391-ranuzzi-margin-crespi, st-chp19-p391-ranuzzi-caldari-picture-incident留待S6逐条裁决，不登记正式关系。
- cand-2112（new-person:francesco-redi-01250bf868）→ [弗朗切斯科·雷迪（Francesco Redi）](../../../04-knowledge/units/persons/francesco-redi.md)。索引Q-R.csv#39与相应正文页段支持source-local人物登记；直接S2关系候选st-chp8-p229-ferdinand-educated-by-redi留待S6逐条裁决，不登记正式关系。

本批登记5个S3 new人物组、5条候选映射和14条source_backed名称字段；8条直接S2关系候选留待S6，未新增正式关系、S2断言或来源。登记后person类型S4为529组/621条已登记、537组/538条待登记；全书为938组/1,115条已登记、3,836组/3,850条待登记，KU=1957。


<a id="s4-person-direct-endpoints-qr-middle-20261018"></a>

### S3理由校正与S4人物直接端点登记：Q-R索引中段（2026-10-18）

- S3理由校正：cand-2138由索引和p.254正文全名支持，并按正文亲属措辞与Aurelio、Carlo既有KU区分。cand-2139由p.135的Don Ferdinando及p.136续文Afan de Ribera明确识别；对应source identity statement的S3待办文字已更新，未增加关系边。cand-2146索引和正文均给出Francesco Maria Ricchini。cand-2188正文只称Abbé Richard，名字未提供；引文经Morazzoni转引，原刊未核，并与Richard Mead分开。cand-2198名字Hyacinthe来自索引，正文p.285仅称Rigaud。五项S3决定均保持new，原自我匹配式说明已撤回并以可追溯的页段证据替换。
- cand-2138（new-person:lodovico-rezzonico-dd8b30f008）→ [洛多维科·雷佐尼科（Lodovico Rezzonico）](../../../04-knowledge/units/persons/lodovico-rezzonico.md)。索引Q-R.csv#65与相应正文页段支持source-local人物登记；直接S2关系候选st-chp9-p254-aurelio-father-of-lodovico, st-chp9-p254-faustina-lodovico-marriage留待S6逐条裁决，不登记正式关系。
- cand-2139（new-person:afan-de-ferdinando-ribera-369de73a8f）→ [唐·费迪南多·阿凡·德·里贝拉（Don Ferdinando Afan de Ribera）](../../../04-knowledge/units/persons/don-ferdinando-afan-de-ribera.md)。索引Q-R.csv#66与相应正文页段支持source-local人物登记；直接S2关系候选st-chp5-p135-van-laer-dedicated-eight-animal-engravings留待S6逐条裁决，不登记正式关系。
- cand-2146（new-person:francesco-maria-ricchini-03415a916c）→ [弗朗切斯科·马里亚·里基尼（Francesco Maria Ricchini）](../../../04-knowledge/units/persons/francesco-maria-ricchini.md)。索引Q-R.csv#73与相应正文页段支持source-local人物登记；直接S2关系候选st-chp8-p215-ricchini-planned-dome-1612留待S6逐条裁决，不登记正式关系。
- cand-2188（new-person:abbe-richard-b9f32ee805）→ [阿贝·理查德（Abbé Richard）](../../../04-knowledge/units/persons/abbe-richard.md)。索引Q-R.csv#115与相应正文页段支持source-local人物登记；直接S2关系候选st-chp13-p335-gerusalemme-admired-by-richard留待S6逐条裁决，不登记正式关系。
- cand-2198（new-person:hyacinthe-rigaud-27fb3b4435）→ [雅辛特·里戈（Hyacinthe Rigaud）](../../../04-knowledge/units/persons/hyacinthe-rigaud.md)。索引Q-R.csv#125与相应正文页段支持source-local人物登记；直接S2关系候选st-chp10-p285-carriera-met-artists留待S6逐条裁决，不登记正式关系。

本批登记5个S3 new人物组、5条候选映射和12条source_backed名称字段；6条直接S2关系候选留待S6，未新增正式关系或来源。登记后person类型S4为534组/626条已登记、532组/533条待登记；全书为943组/1,120条已登记、3,831组/3,845条待登记，KU=1962。


<a id="s4-person-direct-endpoints-del-rosso-family-20261018"></a>

### S3家族身份组校正与S4登记：del Rosso三代人物（2026-10-18）

- S3身份边界承接2026-10-16已记录的修正：cand-2279是兄弟三人的祖父，与既有cand-2275（生于1640年的Andrea del Rosso）分代；p.211的祖父称谓和p.212的Andrea续文支撑该组。cand-2280和cand-2281的索引分别给出Antonio del Rosso与Giovanni Battista del Rosso，正文p.211只给名字并说明二人是Nicola之子；原‘正文全名’理由撤回，姓氏按索引与家族上下文定位。三项均各自保留new组，不互相合并，不作外部匹配。
- cand-2279（new-person:andrea-del-rosso-grandfather-2279）→ [安德烈亚·德尔·罗索（安德烈亚、洛伦佐与奥塔维奥三兄弟之祖父）（Andrea del Rosso (grandfather of Andrea, Lorenzo, and Ottavio del Rosso)）](../../../04-knowledge/units/persons/andrea-del-rosso-grandfather.md)。索引Q-R.csv#207与相应正文页段支持source-local人物登记；直接S2关系候选st-chp8-p211-forebears-grandfather-open, st-chp8-p212-grandfather-andrea-built-chapel留待S6逐条裁决，不登记正式关系。
- cand-2280（new-person:antonio-del-rosso-7dc9d7753f）→ [安东尼奥·德尔·罗索（Antonio del Rosso）](../../../04-knowledge/units/persons/antonio-del-rosso.md)。索引Q-R.csv#208与相应正文页段支持source-local人物登记；直接S2关系候选st-chp8-p211-nicola-father-of-antonio留待S6逐条裁决，不登记正式关系。
- cand-2281（new-person:battista-del-giovanni-rosso-6a1d2554fa）→ [乔瓦尼·巴蒂斯塔·德尔·罗索（Giovanni Battista del Rosso）](../../../04-knowledge/units/persons/giovanni-battista-del-rosso.md)。索引Q-R.csv#209与相应正文页段支持source-local人物登记；直接S2关系候选st-chp8-p211-nicola-father-of-giovanni-battista留待S6逐条裁决，不登记正式关系。

本批登记3个S3 new人物组、3条候选映射和7条source_backed名称字段；4条直接S2关系候选留待S6，未新增正式关系、S2断言或来源。登记后person类型S4为537组/629条已登记、529组/530条待登记；全书为946组/1,123条已登记、3,828组/3,842条待登记，KU=1965。


<a id="s4-person-direct-endpoints-princess-rossi-20261018"></a>

### S3身份复用与S4人物端点登记：Rossano公主及Rossi（2026-10-18）

- S3复用：cand-2267原登记为标题身份new组。第5章p.131仅称Princess of Rossano，并称其为Camillo Pamfili之妻；现有Olimpia Aldobrandini KU已有与Camillo的配偶身份记录，且引用Treccani《意大利传记辞典》对Olimpia Pamphili（principessa di Rossano）的识别，故改判same并映射至该KU。Haskell叙述的1643年委托早于该KU所载1647年婚期，保留为待核时间差异；不以本次身份复用裁定时间主张或正式关系。三条直接S2关系候选留待S6。
- S3新组：cand-2270正文与索引均给出建筑师Domenico Rossi；cand-2271索引补足姓氏，正文仅称Luigi，并明确其为Carlo de' Rossi之兄弟，故与Carlo分别登记；cand-2273正文给出Pellegrino de Rossi全名。三人只按各自书内证据登记source-local人物，不按Rossi姓氏相互合并或引入外部身份。
- cand-2270（new-person:domenico-rossi-6b2f907fa1）→ [多梅尼科·罗西（Domenico Rossi）](../../../04-knowledge/units/persons/domenico-rossi.md)。索引Q-R.csv#198与正文页段支持书内人物登记；直接S2关系候选st-chp9-p251-manin-employed-rossi留待S6逐条裁决，不登记正式关系。
- cand-2271（new-person:de-luigi-rossi-565b338a56）→ [路易吉·德·罗西（Luigi de' Rossi）](../../../04-knowledge/units/persons/luigi-de-rossi.md)。索引Q-R.csv#199与正文页段支持书内人物登记；直接S2关系候选st-chp5-p143-carlo-de-rossi-brother-of-luigi留待S6逐条裁决，不登记正式关系。
- cand-2273（new-person:de-pellegrino-rossi-d7ade35e0b）→ [佩莱格里诺·德·罗西（Pellegrino de' Rossi）](../../../04-knowledge/units/persons/pellegrino-de-rossi.md)。索引Q-R.csv#201与正文页段支持书内人物登记；直接S2关系候选st-chp5-p122-rossi-preti留待S6逐条裁决，不登记正式关系。
- cand-2267（标题候选）→ 既有[units/persons/olimpia-aldobrandini](../../../04-knowledge/units/persons/olimpia-aldobrandini.md)；保留日期冲突待核，三条关系候选不在S4写入正式关系。

本批将1条S3决定由new改为same，登记3个new人物组及6条source_backed名称字段；6条直接S2关系候选留待S6，未新增正式关系、S2断言或来源。登记后person类型S4为540组/632条已登记、525组/526条待登记；全书为949组/1,126条已登记、3,824组/3,838条待登记，KU=1968。


<a id="s4-person-direct-endpoints-rota-rovere-rowlandson-20261018"></a>

### S3人物身份组理由校正与S4登记：Rota、Rovere、Rowlandson（2026-10-18）

- cand-2287：索引与第10章p.312正文均给出Giovanni Battista Rota全名；正文称律师及艺术品交易者。未找到精确同名既有KU，登记独立source-local人物组；注4所指档案与Edward Wright页码未独立查阅。
- cand-2290：索引Q-R.csv#218与第2章p.54正文支持Vittoria della Rovere全名；现有Francesco Maria della Rovere KU只提供“女儿”语境，没有Vittoria人物KU，故新增source-local组。私人物品继承限于原文表述。
- cand-2291：索引与第10章p.292正文均给出Thomas Rowlandson全名；正文称其讽刺画家并记其转用Canaletto人物简笔。未找到精确同名既有KU，登记独立source-local人物组。三组不依姓氏相似性合并，不作外部身份声明。
- cand-2287（new-person:battista-giovanni-rota-738eac852a）→ [乔瓦尼·巴蒂斯塔·罗塔（Giovanni Battista Rota）](../../../04-knowledge/units/persons/giovanni-battista-rota.md)。索引Q-R.csv#215与正文页段支持书内人物登记；直接S2关系候选st-chp10-p312-1724-purchase-from-rota留待S6逐条裁决，不登记正式关系。
- cand-2290（new-person:della-rovere-vittoria-128b06ba87）→ [维托里娅·德拉·罗韦雷（Vittoria della Rovere）](../../../04-knowledge/units/persons/vittoria-della-rovere.md)。索引Q-R.csv#218与正文页段支持书内人物登记；直接S2关系候选st-chp2-seciv-l114-125-private-possession-inheritance留待S6逐条裁决，不登记正式关系。
- cand-2291（new-person:rowlandson-thomas-587b2a4589）→ [托马斯·罗兰森（Thomas Rowlandson）](../../../04-knowledge/units/persons/thomas-rowlandson.md)。索引Q-R.csv#219与正文页段支持书内人物登记；直接S2关系候选st-chp10-p292-rowlandson-adaptation留待S6逐条裁决，不登记正式关系。

本批登记3个S3 new人物组、3条候选映射和6条source_backed名称字段；3条直接S2关系候选留待S6，未新增正式关系或来源。登记后person类型S4为543组/635条已登记、522组/523条待登记；全书为952组/1,129条已登记、3,821组/3,835条待登记，KU=1971。


<a id="s4-person-direct-endpoints-grimani-grosley-guidi-20261018"></a>

### S3身份组交接与S4登记：Grimani、Grosley、Guidi（2026-10-18）

- cand-1234：沿用本日既有S3标题身份审查，登记为Doge Grimani书内人物KU，不补姓名；1745年奠基语境将其与一般性的威尼斯总督机构候选分开，Cardinal Grimani仍按现有S3记录保持未决。
- cand-1235：修正旧的自我匹配式new理由。索引G.csv#145定位p.301n与p.332；前者转引1758年在威尼斯的Grosley，后者称旅人Grosley并引其出版许可观察，支持同一书内人物组。引文U p.99与书目条目的对应仍未证实。
- cand-1277：修正旧的自我匹配式new理由。索引G.csv#187将p.189与p.198并列；两处正文均称Domenico Guidi，分别置于凡尔赛雕塑遴选及Closterman寄送其素描的语境。p.198关系候选仍映射Closterman与素描对象，本批不把Guidi增作该statement的端点。
- cand-1234（new-person:doge-grimani-ee5c26c638）→ [格里马尼总督（Doge Grimani）](../../../04-knowledge/units/persons/doge-grimani.md)。索引G.csv#144与正文页段支持书内人物登记；直接S2关系候选st-chp9-p272-doge-grimani-rebuild留待S6逐条裁决，不登记正式关系。
- cand-1235（new-person:grosley-jean-pierre-ebde05d809）→ [皮埃尔·让·格罗斯莱（Pierre Jean Grosley）](../../../04-knowledge/units/persons/pierre-jean-grosley.md)。索引G.csv#145与正文页段支持书内人物登记；直接S2关系候选st-chp10-p301-note1-grosley-quote留待S6逐条裁决，不登记正式关系。
- cand-1277（new-person:domenico-guidi-8bb3bdb48b）→ [多梅尼科·圭迪（Domenico Guidi）](../../../04-knowledge/units/persons/domenico-guidi.md)。索引G.csv#187与正文页段支持书内人物登记；直接S2关系候选st-chp7-p189-i06留待S6逐条裁决，不登记正式关系。

本批保留1个标题身份S3决定并校正2条new身份理由，登记3个new人物组、3条候选映射和6条source_backed名称字段；3条直接S2关系候选留待S6，未新增正式关系或来源。登记后person类型S4为546组/638条已登记、519组/520条待登记；全书为955组/1,132条已登记、3,818组/3,832条待登记，KU=1974。


<a id="s4-person-direct-endpoints-gustavus-halifax-lorraine-20261018"></a>

### S3身份复核与S4人物登记：Gustav III、Halifax与Leopold of Lorraine（2026-10-18）

- cand-1283（G.csv#193）：第15章p.366正文只称King of Sweden，索引列Gustavus III of Sweden。瑞典国家档案馆《瑞典传记辞典》记录13317列Gustav III为瑞典国王（1746–1792，在位1771–1792），与1777年语境相符。该身份与cand-1284 Gustavus Adolphus（Gustav II Adolf，1611–1632）分开；未匹配现有KU，判new并登记为Gustav III of Sweden。外证不验证认捐陈述。
- cand-1286（H.csv#1）：重申new人物身份组，但名称严格保留为未具名Earl of Halifax。第10章p.286确认其在Queen’s Bed Chamber委托叙述中的发言角色；未查得足以识别个人的跨章/外部锚点，也不映射至具名继承人。
- cand-1441（L.csv#99）：修正本日早先‘仅有爵号、待身份锚点’的S4说明。第9章p.267及索引只给出Duke of Lorraine；Griffin, ‘Duke Leopold of Lorraine,’ The Historical Journal 65, no. 5 (2022), pp.1244–1261, DOI 10.1017/S0018246X2100090X, §I and n.26将Leopold (1679–1729)与Ferdinando-Carlo Gonzaga继承及1708年事件相连，足以识别本候选。与cand-1398（Holy Roman Emperor Leopold I）、cand-1397/cand-8097（Pietro Leopoldo of Tuscany）及cand-1399（Leopold Wilhelm）分开。身份由pending改为new；无现有精确KU，登记为Leopold, Duke of Lorraine。
- cand-1441的身份匹配不裁决Haskell‘successfully established his claim’与Griffin所述未取得Mantua、Monferrato之间的表述差异；该关系候选仍待S6解释。cand-11467 ‘Gonzaga effects’仍无支持类型，保持undecided，不建KU。
- cand-1283（new-person:gustavus-iii-of-sweden-5f6ef99faa）→ [古斯塔夫三世（瑞典国王）（Gustav III of Sweden）](../../../04-knowledge/units/persons/gustav-iii-of-sweden.md)；外部身份记录：Svenskt Biografiskt Lexikon (Riksarkivet)（13317）；直接S2关系候选st-chp15-p366-king-of-sweden-subscribed留待S6逐条裁决，不登记正式关系。
- cand-1286（new-person:halifax-of-d914fc61b9）→ [哈利法克斯伯爵（原书未具名）（Earl of Halifax (unnamed in the source)）](../../../04-knowledge/units/persons/earl-of-halifax-source-local.md)；不作外部身份映射；直接S2关系候选st-chp10-p286-queens-bedchamber-commission留待S6逐条裁决，不登记正式关系。
- cand-1441（new-person:leopold-duke-of-lorraine-20261018）→ [洛林公爵利奥波德（Leopold, Duke of Lorraine）](../../../04-knowledge/units/persons/leopold-duke-of-lorraine.md)；外部身份记录：The Historical Journal / Cambridge Core（10.1017/S0018246X2100090X）；直接S2关系候选st-chp9-p267-lorraine-claim留待S6逐条裁决，不登记正式关系。

本批确认/更正3项S3身份组并登记3个new person KU、3条候选映射、6条source_backed名称字段及2条外部身份记录；3条直接S2关系候选留待S6。未新增正式关系、来源登记或candidate-backlog项。登记后person类型S4为549组/641条已登记、516组/517条待登记；全书为958组/1,135条已登记、3,815组/3,829条待登记，KU=1977。

<a id="s4-person-relation-endpoints-scaramuccia-gonzaga-crespi-spezzaferro-20261018"></a>

### S4 person：Scaramuccia、Gonzaga、Crespi、Spezzaferro四组人物身份登记（2026-10-18）

- `cand-2390`（`new-person:luigi-scaramuccia-aa9d76a4e9`）→ [路易吉·斯卡拉穆恰（Luigi Scaramuccia）](../../../04-knowledge/units/persons/luigi-scaramuccia.md)；S2候选`st-chp5-note-p124-n1-scaramuccia-dedicated-by`留待S6；哈斯克尔把Scaramuccia记为版画题献者；该书内陈述对应的S2关系候选保留待S6审查。索引作品候选cand-2391与人物cand-2390类型不同，仍各自保持其S3去向。
- `cand-5453`（`new-person:blessed-gonzaga-luigi-302904be8f`）→ [阿洛伊修斯·贡扎加（Aloysius Gonzaga）](../../../04-knowledge/units/persons/aloysius-gonzaga.md)；S2候选`st-chp3-seciv-l179-187-assumption-relief-represents-luigi-gonzaga`留待S6；本书称该人物为S. Ignazio左横堂一件浮雕所表现的主题，并以the Assumption of the Blessed Luigi Gonzaga称述；这里依原句表述为Luigi Gonzaga升天主题，不据此另造作品题名。第8章及第9章另以S. Luigi Gonzaga指称绘画与modello主题。相应S2关系候选留待S6，不在S4建立作品关系。
- `cand-7716`（`new-person:crespi-luigi-bd0f28eb72`）→ [路易吉·克雷斯皮（Luigi Crespi）](../../../04-knowledge/units/persons/luigi-crespi-author.md)；S2候选`st-chp8-p239-note1-luigi-crespi-stay`留待S6；原书的L. Crespi两年说与哈斯克尔所述八个月上限并列，Zanotti的多次到访暗示也未消解差异；关系候选保留来源归因并待S6，不作实体层面的事实裁决。
- `cand-10881`（`new-person:luigi-spezzaferro-cd9c5c8655`）→ [路易吉·斯佩察费罗（Luigi Spezzaferro）](../../../04-knowledge/units/persons/luigi-spezzaferro.md)；S2候选`st-chp20-p397-spezzaferro-del-monte-caravaggio`留待S6；第20章的S2关系候选记载哈斯克尔对Spezzaferro研究的转述；原书所引文章另有archive候选cand-10882，二者保持人物与文献类型区别，关系留待S6。

四组均按各自S3 new身份组登记为一个人物KU，未按名字相近合并。Scaramuccia人物候选cand-2390与版画作品候选cand-2391保持类型区分；Luigi Crespi与画家Giuseppe Maria Crespi保持人物区分；Spezzaferro及其文章候选cand-10882保持人物/文献区分。Luigi Gonzaga与Aloysius Gonzaga的别名同一性据梵蒂冈2025年英意礼仪对照行确认，未将外部资料用于扩写书内事实。四条S2关系候选均留待S6；未新增正式关系或enrichment字段。

登记后人物类型S4为553组/645条已登记、512组/513条待登记；全书KU=1981。

<a id="s4-person-name-fields-luigi-scaramuccia-gonzaga-crespi-spezzaferro-20261018"></a>

### S4结构化字段与来源登记：四张人物卡姓名（2026-10-18）

四张新人物卡的姓名表行登记为6条enrichment.jsonl记录（`enr-14943`, `enr-14944`, `enr-14945`, `enr-14946`, `enr-14947`, `enr-14948`），来源序号与卡片sources对应。Luigi/Aloysius Gonzaga的英文惯用名字段引用Holy See礼仪文本来源`src-6828ef56b8f5c57f`；该外部来源已列入sources.csv，URL与PDF页码定位见人物卡。其余姓名字段引用Haskell书内页段或索引。本批只登记名称字段，不新增生平事实、formal relation或S6裁决。

<a id="s4-person-relation-endpoints-mancini-manfredi-marchesi-marchiori-20261018"></a>

### S4 person：Mancini、Manfredi、Marchesi、Marchiori四组直接端点登记（2026-10-18）

- `cand-1506`（`new-person:francesco-mancini-f439d8fb6a`）→ [弗朗切斯科·曼奇尼（Francesco Mancini）](../../../04-knowledge/units/persons/francesco-mancini.md)；S2关系候选`st-chp14-p351-rome-artists`留待S6。第14章将Mancini列入Algarotti的罗马画家建议名单；对应statement仍是S2关系候选，留待S6裁决。该人物与现有Giulio Mancini、Maria Mancini为不同身份。
- `cand-1511`（`new-person:eustachio-manfredi-e87f85ad8e`）→ [尤斯塔基奥·曼弗雷迪（Eustachio Manfredi）](../../../04-knowledge/units/persons/eustachio-manfredi.md)；S2关系候选`st-chp14-p347-algarotti-corresponded-with-manfredi`留待S6。Haskell称Algarotti与Manfredi在学生时代相识后持续通信；该陈述仍为来源归因的关系候选，不在S4转为正式关系。
- `cand-1538`（`new-person:marchesi-raffaelo-548b679336`）→ [拉斐洛·马尔凯西（Raffaelo Marchesi）](../../../04-knowledge/units/persons/raffaelo-marchesi.md)；S2关系候选`st-chp5-p136-marchesi-lawyer-and-beneficiary-of-cerquozzi-bequest`留待S6。第5章称律师Raffaele Marchesi为Cerquozzi部分作品遗赠对象。索引拼写Raffaelo与正文Raffaele的差异记作来源异形，未借此判断人物为两人；关系候选仍待S6。
- `cand-1541`（`new-person:giovanni-marchiori-065f269ab2`）→ [乔瓦尼·马尔基奥里（Giovanni Marchiori）](../../../04-knowledge/units/persons/giovanni-marchiori.md)；S2关系候选`st-chp14-p356-marchiori-berlin-church-commission`留待S6。原书称Algarotti取得该委托并提及其致Bonomo信中“for the honour of Italy”的劝促；人物与教堂雕塑委托关系候选留待S6。

四组均为单候选S3 new身份组，各登记一个人物KU。cand-1538的书后索引写Raffaelo Marchesi，而正文同页写Raffaele Marchesi；相同索引页码、姓名和律师/遗赠语境支持归为同一书内人物，卡片保留拼写异形，不认定哪一形式为规范名。所有书内陈述仍为S2关系候选；未新增正式关系、外部事实、来源登记或backlog项目。

登记后人物类型S4为557组/649条已登记、508组/509条待登记；全书KU=1985。

<a id="s4-person-name-fields-mancini-manfredi-marchesi-marchiori-20261018"></a>

### S4结构化姓名字段登记：四张人物卡（2026-10-18）

四张卡姓名表共登记5条source_backed enrichment行（`enr-14949`、`enr-14950`、`enr-14951`、`enr-14952`、`enr-14953`），全部引用既有Haskell书目来源ID；Raffaelo Marchesi（索引）与Raffaele Marchesi（正文）分列为来源拼写异形，未设定标准形式。本批未新增sources.csv记录、生平字段或formal relation。

<a id="s4-person-relation-endpoints-mari-maria-teresa-martinelli-mascardi-20261018"></a>

### S4 person：Cosimo Mari、Maria Teresa、Domenico Martinelli与Agostino Mascardi四组直接端点登记（2026-10-18）

- `cand-1543`（`new-person:cosimo-mari-23dde1b6dd`）→ [科西莫·马里（Cosimo Mari）](../../../04-knowledge/units/persons/cosimo-mari.md)；S2关系候选`st-chp20-p409-tiepolo-pictures-bequeathed-to-cosimo-mari`留待S6。Haskell将该遗赠说法归于Da Pozzo公布的遗嘱；相关候选关系留待S6，脚注3所涉遗嘱依据仍按S2记录保留待核。
- `cand-1545`（`new-person:holy-maria-roman-teresa-b39636bd88`）→ [玛丽亚·特蕾莎（Empress Maria Teresa）](../../../04-knowledge/units/persons/maria-teresa-holy-roman-empress.md)；S2关系候选`st-chp13-p335-gerusalemme-dedicated-to-maria-teresa`留待S6。正文称名“Empress Maria Teresa”与索引称名“Maria Teresa, Holy Roman Empress”并列保存；题献关系候选留待S6。关于Schönbrunn的表述作为Haskell的作者叙述保留，不登记为第二条正式关系。
- `cand-1553`（`new-person:domenico-martinelli-8fc1406b14`）→ [多梅尼科·马蒂内利（Domenico Martinelli）](../../../04-knowledge/units/persons/domenico-martinelli.md)；S2关系候选`st-chp7-p201-v-martinelli-town-palace-1691`留待S6。本条只登记人物身份及Haskell的书内叙述；城市宅邸仍是独立地点候选，相关关系候选留待S6。
- `cand-1560`（`new-person:agostino-mascardi-04145514b9`）→ [阿戈斯蒂诺·马斯卡尔迪（Agostino Mascardi）](../../../04-knowledge/units/persons/agostino-mascardi.md)；S2关系候选`st-chp6-p157-mascardi-professorship`、`st-chp6-p157-table-vogue-mascardi`留待S6。两条关于任教与翻译/声望的S2关系候选均留待S6；Rome University与cand-5169（Sapienza）的身份对应仍待S3处理，不在本次扩写或定边。

四组均为单候选S3 new身份组，逐组登记一个人物KU。Maria Teresa正文称名与索引称号并列保留；Cosimo Mari遗嘱叙述、Martinelli的“came to build”限定、Mascardi关于任教及《The Table》的来源归因均按原书语气保留。关系候选留待S6；Rome University与cand-5169（Sapienza）的身份对应仍待S3。未新增正式关系、外部来源或backlog项目。

登记后人物类型S4为561组/653条已登记、504组/505条待登记；全书KU=1989。

<a id="s4-person-name-fields-mari-maria-teresa-martinelli-mascardi-20261018"></a>

### S4结构化姓名字段登记：四张人物卡（2026-10-18）

四张卡姓名表共登记5条source_backed enrichment行（`enr-14954`、`enr-14955`、`enr-14956`、`enr-14957`、`enr-14958`），全部引用既有Haskell书目来源ID；Maria Teresa的正文称名与索引称号分别保留为两行。本批未新增sources.csv记录、生平字段或formal relation。

<a id="s4-person-relation-endpoints-mattei-mazenta-mazzoni-menzini-20261018"></a>

### S4 person：Mattei、Mazenta、Mazzoni与Menzini四组直接端点登记（2026-10-18）

- `cand-1580`（`new-person:mattei-tommaso-037aacedcb`）→ [托马索·马泰（Tommaso Mattei）](../../../04-knowledge/units/persons/tommaso-mattei.md)；S2关系候选`st-chp8-p221-palace-built-by-mattei`留待S6。第8章下一页还以“his architect”指称Mattei；相关关系候选只按S2原记录留待S6，不在本次登记中新增关系边。
- `cand-1601`（`new-person:ambrogio-mazenta-f50481318d`）→ [安布罗焦·马曾塔（Ambrogio Mazenta）](../../../04-knowledge/units/persons/ambrogio-mazenta.md)；S2关系候选`st-chp4-sec-ii-l91-99-cassiano-corresponded-with-leonardo-manuscript-owners`、`st-chp4-sec-ii-l91-99-mazenta-collection-reconstructed`留待S6。通信与收藏散佚／重建两条候选均留待S6；本卡不将Haskell的叙述转为正式关系。
- `cand-1603`（`new-person:mazzoni-nicola-3547657524`）→ [尼科拉·马佐尼（Nicola Mazzoni）](../../../04-knowledge/units/persons/nicola-mazzoni.md)；S2关系候选`st-chp13-p337-note2-pasquali-letter-to-mazzoni`留待S6。该脚注报告Pasquali写给Mazzoni的信，并经Nuti（1941）转引；书信内容及其中“qui”所指保持S2限定，关系候选留待S6。
- `cand-1653`（`new-person:benedetto-menzini-b45fd70cd1`）→ [贝内代托·门齐尼（Benedetto Menzini）](../../../04-knowledge/units/persons/benedetto-menzini.md)；S2关系候选`st-chp8-p230-ferdinand-supported-benedetto-menzini`留待S6。来源所述支持关系候选留待S6；不将其扩写为具体资助或委托。

四组均为单候选S3 new身份组，各登记一个人物KU。Mattei与Mazenta的登记保留原书建筑及通信／收藏表述的来源限定；Nicola Mazzoni的索引拼写与脚注“Niccola”异形并列保存，书信依据仍为Haskell经Nuti的转引；Menzini的支持表述不扩写为具体资助或委托。关系候选均待S6；未新增正式关系、外部来源或backlog项目。

登记后人物类型S4为565组/657条已登记、500组/501条待登记；全书KU=1993。

<a id="s4-person-name-fields-mattei-mazenta-mazzoni-menzini-20261018"></a>

### S4结构化姓名字段登记：四张人物卡（2026-10-18）

四张卡姓名表共登记5条source_backed enrichment行（`enr-14959`、`enr-14960`、`enr-14961`、`enr-14962`、`enr-14963`），全部引用既有Haskell书目来源ID；Nicola Mazzoni的索引拼写与脚注“Niccola”异形分列。本批未新增sources.csv记录、生平字段或formal relation。

<a id="s3-person-mario-minnitti-reuse-20261018"></a>

### S3人物身份复核：复用Mario Minniti既有KU（2026-10-18）

cand-1671的书后索引M.csv#211写作“Minitti, Mario”，指向第1章脚注页9n；同一脚注正文写“Mario Minnitti in Augusta (Sicily) in 1617”。已采纳的[mario-minnitti.md](../../../04-knowledge/units/persons/mario-minnitti.md)保存了完全相同的Haskell段落和来源引用，并明确将“Mario Minnitti”列为该人物的来源拼写异形。因此撤回cand-1671的S3 new判断，改为same → units/persons/mario-minnitti；旧决定理由（未匹配既有KU）不再成立，索引多一个t的拼写不是另一人物。新映射加入既有身份组，未新增KU或外部来源。脚注引述的Agnello出版材料及原始合同仍未独立核读；关系候选st-chp1-secii-notes-local-commissions-minnitti-1617仍待S6。

复核后人物S3为same 398个KU/1,090条，new 1,064组/1,157条；S4新组待登记499组/500条，全书KU=1993。

<a id="s4-person-relation-endpoints-mercati-mieris-morice-20261018"></a>

### S4 person：Mercati、van Mieris与Morice三组直接端点登记（2026-10-18）

- `cand-1654`（`new-person:battista-giovanni-mercati-5106be2253`）→ [乔瓦尼·巴蒂斯塔·梅尔卡蒂（Giovanni Battista Mercati）](../../../04-knowledge/units/persons/giovanni-battista-mercati.md)；S2关系候选`st-chp5-note-p121-n2-print-created-by`留待S6。版画制作关系候选留待S6；本卡只登记脚注和索引所支持的人物身份。
- `cand-1663`（`new-person:frans-mieris-van-7bf8b1dd69`）→ [弗兰斯·范·米里斯（Frans van Mieris）](../../../04-knowledge/units/persons/frans-van-mieris.md)；S2关系候选`st-chp10-p307-vermeer-attribution-to-mieris`留待S6。该画的历史归属候选留待S6；本次登记不将其表述为作品现行作者。
- `cand-1702`（`new-person:morice-william-007a902cb7`）→ [威廉·莫里斯爵士（Sir William Morice）](../../../04-knowledge/units/persons/sir-william-morice.md)；S2关系候选`st-chp10-p290-morice-purchase`留待S6。S2关系候选只指Haskell所述已完成画作的购买；相关脚注记载的信件由Chaloner刊布而未独立查阅，候选留待S6。

三组均为单候选S3 new身份组，各登记一个KU。Mercati的脚注身份保留转引范围；van Mieris仅记录《Lady at the Virginals》的历史归属；Morice的购买范围限定为已完成画作，脚注所引信件未独立查阅。关系候选留待S6，未新增外部来源、正式关系或backlog项目。

登记后人物类型S4为568组/660条已登记、496组/497条待登记；全书KU=1996。

<a id="s4-person-name-fields-mercati-mieris-morice-20261018"></a>

### S4结构化姓名字段登记：三张人物卡（2026-10-18）

三张卡姓名表登记3条source_backed enrichment行（`enr-14964`、`enr-14965`、`enr-14966`），全部引用既有Haskell书目来源ID。本批未新增sources.csv记录、生平字段或formal relation。

<a id="s4-person-relation-endpoints-morlaiter-morris-moscheni-mura-20261018"></a>

### S4 person：Morlaiter、Morris、Moscheni与de Mura四组直接端点登记（2026-10-18）

- `cand-1703`（`new-person:michelangelo-morlaiter-17d79e97ce`）→ [米开朗基罗·莫莱特（Michelangelo Morlaiter）](../../../04-knowledge/units/persons/michelangelo-morlaiter.md)；S2关系候选`st-chp10-p312-morlaiter-sculpted-portraits-of`留待S6。Haskell列举了不止一位为Schulenburg制作肖像的艺术家，且未给出具体肖像题名；相关关系候选留待S6。
- `cand-1707`（`new-person:morris-roger-69ba5e4869`）→ [罗杰·莫里斯（Roger Morris）](../../../04-knowledge/units/persons/roger-morris.md)；S2关系候选`st-chp10-p309-one-picture-after-morris`留待S6。S2候选指十一幅图中有一幅呈现Roger Morris的一件作品；不将其改写成Morris绘制该图。关系候选留待S6。
- `cand-1708`（`new-person:moscheni-pietro-41b3d0bea5`）→ [皮耶特罗·莫斯凯尼（Pietro Moscheni）](../../../04-knowledge/units/persons/pietro-moscheni.md)；S2关系候选`st-chp10-p322-moscheni-commissioned-longhi-portrait`、`st-chp10-p322-moscheni-friend-of-lodoli`留待S6。委托与Lodoli友谊两条S2关系候选均留待S6；未把来源叙述转换为正式关系。
- `cand-1716`（`new-person:de-francesco-mura-a4cbc8f2bb`）→ [弗朗切斯科·德·穆拉（Francesco de Mura）](../../../04-knowledge/units/persons/francesco-de-mura.md)；S2关系候选`st-chp14-p351-neapolitan-subjects`留待S6。S2候选记录Haskell对Algarotti提案的报告；地区语境保留为“那不勒斯画家中”，不据此构造机构关系。

四组均为单候选S3 new身份组，各登记一个KU。Morlaiter正文只作姓氏称呼，索引提供Michelangelo全名；Morris不被写成所绘图片的作者；Moscheni两条候选分别记录委托和友谊；de Mura的地区措辞保留为‘那不勒斯画家中’。关系候选留待S6，未新增外部来源、正式关系或backlog项目。

登记后人物类型S4为572组/664条已登记、492组/493条待登记；全书KU=2000。

<a id="s4-person-name-fields-morlaiter-morris-moscheni-mura-20261018"></a>

### S4结构化姓名字段登记：四张人物卡（2026-10-18）

四张卡姓名表共登记5条source_backed enrichment行（`enr-14967`、`enr-14968`、`enr-14969`、`enr-14970`、`enr-14971`），全部引用既有Haskell书目来源ID；Morlaiter 的索引全名与正文姓氏分列记录。本批未新增sources.csv记录、生平字段或formal relation。

<a id="s4-person-murray-nadal-novelli-noyelle-20261018"></a>

### S4 person：Murray、Nadal、Novelli与Noyelle四组索引人物登记（2026-10-18）

- `cand-1719`（`new-person:john-murray-587d09c515`）→ [约翰·默里（John Murray）](../../../04-knowledge/units/persons/john-murray-resident.md)；依据索引M.csv#260与正文第10章，印刷页302；OCR L391–393登记。
- `cand-1721`（`new-person:jerome-nadal-c9c2d78438`）→ [杰罗姆·纳达尔（Jerome Nadal）](../../../04-knowledge/units/persons/jerome-nadal.md)；依据索引N.csv#0与正文Postscript，印刷页399；OCR L40–41登记。
- `cand-1757`（`new-person:il-monrealese-novelli-pietro-c49178815b`）→ [彼得罗·诺韦利（il Monrealese）（Pietro Novelli (il Monrealese)）](../../../04-knowledge/units/persons/pietro-novelli-il-monrealese.md)；依据索引N.csv#37与正文第8章第I节，印刷页210；OCR L75登记。
- `cand-1763`（`new-person:charles-de-noyelle-54b3847378`）→ [夏尔·德·努瓦耶尔（Charles de Noyelle）](../../../04-knowledge/units/persons/charles-de-noyelle.md)；依据索引N.csv#43与正文第3章第IV节，印刷页91；OCR L162–163登记。

四组均为单候选S3 new身份组；均依据书后索引与正文姓名登记，不新增外部来源或正式关系。Pietro Novelli的索引别称保留，并未仅凭姓氏并入既有Pietro Antonio Novelli卡；两组的历史身份关系未由本批外部核验。 `cand-1748`（Abbé Nollet）本批暂缓S4登记：索引与正文仅给出尊称加姓氏，没有足以唯一登记的完整姓名依据；S3决定保留，待获得进一步身份依据后再回到S4。

登记后人物类型S4为576组/668条已登记、488组/489条待登记；全书KU=2004。

<a id="s4-person-name-fields-murray-nadal-novelli-noyelle-20261018"></a>

### S4结构化姓名字段登记：四张人物卡（2026-10-18）

四张卡姓名表共登记8条source_backed enrichment行（`enr-14972`、`enr-14973`、`enr-14974`、`enr-14975`、`enr-14976`、`enr-14977`、`enr-14978`、`enr-14979`），全部引用既有Haskell书目来源ID；Novelli索引别称、Noyelle的OCR断行校正及Murray、Nadal的索引／正文称名均按来源分列。本批未新增sources.csv记录、生平字段或formal relation。

<a id="s4-person-harley-paciaudi-paolini-parigi-20261018"></a>

### S4 person：Harley、Paciaudi、Paolini与Parigi四组索引／正文人物登记（2026-10-18）

- `cand-1801`（`new-person:harley-of-oxford-robert-a663f62cf8`）→ [罗伯特·哈利（牛津伯爵）（Robert Harley, Earl of Oxford）](../../../04-knowledge/units/persons/robert-harley-earl-of-oxford.md)；依据索引O.csv#36与正文第10章，印刷页288；OCR L220–221登记。
- `cand-1802`（`new-person:maria-paciaudi-paolo-c642933872`）→ [保罗·玛丽亚·帕西奥迪（Paolo Maria Paciaudi）](../../../04-knowledge/units/persons/paolo-maria-paciaudi.md)；依据索引P.csv#0与正文第14章，印刷页360注2；OCR L219登记。
- `cand-1829`（`new-person:paolini-pietro-aa29b3e319`）→ [皮耶特罗·保利尼（Pietro Paolini）](../../../04-knowledge/units/persons/pietro-paolini.md)；依据索引P.csv#28与正文第5章第III节注150，印刷页150注1；OCR L150登记。
- `cand-1835`（`new-person:giulio-parigi-905380a51e`）→ [朱利奥·帕里吉（Giulio Parigi）](../../../04-knowledge/units/persons/giulio-parigi.md)；依据索引P.csv#34与正文第4章第I节，印刷页95；OCR L14登记。

四组均为单候选S3 new身份组，各登记一个KU。Paolini归属断言`st-chp5-notes-l126-165-l150-wallenstein-authorship`保留待S6核对作品端点；Harley纪念碑语境、Paciaudi书目信息及Parigi群体语境不转换为formal relation。未新增外部来源或relation row。

登记后人物类型S4为580组/672条已登记、484组/485条待登记；全书KU=2008。

<a id="s4-person-name-fields-harley-paciaudi-paolini-parigi-20261018"></a>

### S4结构化姓名字段登记：四张人物卡（2026-10-18）

四张卡姓名表共登记8条source_backed enrichment行（`enr-14980`、`enr-14981`、`enr-14982`、`enr-14983`、`enr-14984`、`enr-14985`、`enr-14986`、`enr-14987`），全部引用既有Haskell书目来源ID；Paciaudi索引完整姓名与正文姓氏分列，Paolini作品归属仍待S6核对。本批未新增sources.csv记录、生平字段或formal relation。

<a id="s4-person-passante-perugino-perusini-pesne-20261018"></a>

### S4 person：Passante、Perugino、Perusini与Pesne四组索引／正文登记（2026-10-18）

- `cand-1854`（`new-person:bartolommeo-passante-776a9fc247`）→ [巴托洛梅奥·帕桑特（Bartolommeo Passante）](../../../04-knowledge/units/persons/bartolommeo-passante.md)；依据索引P.csv#54与正文第8章第I节，印刷页206；OCR L38登记。
- `cand-1883`（`new-person:perugino-pietro-628c4b189f`）→ [彼得罗·佩鲁吉诺（Pietro Perugino）](../../../04-knowledge/units/persons/pietro-perugino.md)；依据索引P.csv#84与正文第2章第IV节，印刷页56；OCR L145登记。
- `cand-1884`（`new-person:giovanni-perusini-bcbd5a7b57`）→ [乔瓦尼·佩鲁西尼（Giovanni Perusini）](../../../04-knowledge/units/persons/giovanni-perusini.md)；依据索引P.csv#85与正文第5章第I节注，印刷页122注1；OCR L132登记。
- `cand-1888`（`new-person:antoine-pesne-22a62961be`）→ [安托万·佩斯内（Antoine Pesne）](../../../04-knowledge/units/persons/antoine-pesne.md)；依据索引P.csv#89与正文第10章第II节，印刷页316；OCR L113登记。

四组均为单候选S3 new身份组。Perugino的第56、175页姓氏称名由同一索引条目连接；Pesne的朋友关系候选`st-chp10-p316-streit-regarded-pesne-as-friend`保留待S6。Passante绘画、Perusini失窃画作归属均按Haskell来源语境记录，未新增formal relation或外部来源。

登记后人物类型S4为584组/676条已登记、480组/481条待登记；全书KU=2012。

<a id="s4-person-name-fields-passante-perugino-perusini-pesne-20261018"></a>

### S4结构化姓名字段登记：四张人物卡（2026-10-18）

四张卡姓名表共登记8条source_backed enrichment行（`enr-14988`、`enr-14989`、`enr-14990`、`enr-14991`、`enr-14992`、`enr-14993`、`enr-14994`、`enr-14995`），全部引用既有Haskell书目来源ID；Perugino的两章称名共享同一索引条目。本批未新增sources.csv记录、生平字段或formal relation。

<a id="s4-person-philip-piccino-pompeati-porta-20261018"></a>

### S4 person：Philip II、Piccino、Pompeati与della Porta四组索引／正文登记（2026-10-18）

- `cand-1895`（`new-person:ii-of-philip-spain-d29092bda5`）→ [西班牙的菲利普二世（Philip II of Spain）](../../../04-knowledge/units/persons/philip-ii-of-spain.md)；依据索引P.csv#96与正文第7章第I节，印刷页170；OCR L15–16登记。
- `cand-1926`（`new-person:jacopo-piccino-7b6fbf5d82`）→ [雅各布·皮奇诺（Jacopo Piccino）](../../../04-knowledge/units/persons/jacopo-piccino.md)；依据索引P.csv#127与正文Postscript，印刷页408；OCR L185–188登记。
- `cand-1972`（`new-person:domenico-pompeati-dddf91ab34`）→ [多梅尼科·庞佩亚蒂（Domenico Pompeati）](../../../04-knowledge/units/persons/domenico-pompeati.md)；依据索引P.csv#174与正文第19章Appendix，印刷页394；OCR L159–160登记。
- `cand-1977`（`new-person:della-guglielmo-porta-e07ba351f0`）→ [古列尔莫·德拉·波尔塔（Guglielmo della Porta）](../../../04-knowledge/units/persons/guglielmo-della-porta.md)；依据索引P.csv#179与正文第4章第II节，印刷页104；OCR L54–56登记。

四组均为单候选S3 new身份组。Piccino版画来源保留Parker的可能性措辞；della Porta的Paul III墓创作候选`st-chp4-sec-ii-l53-63-guglielmo-created-paul-tomb`留待S6核对。Philip II的概括性收藏史语境和Pompeati售书记录不转换为formal relation；未新增外部来源或relation row。

登记后人物类型S4为588组/680条已登记、476组/477条待登记；全书KU=2016。

<a id="s4-person-name-fields-philip-piccino-pompeati-porta-20261018"></a>

### S4结构化姓名字段登记：四张人物卡（2026-10-18）

四张卡姓名表共登记8条source_backed enrichment行（`enr-14996`、`enr-14997`、`enr-14998`、`enr-14999`、`enr-15000`、`enr-15001`、`enr-15002`、`enr-15003`），全部引用既有Haskell书目来源ID；Piccino的索引全名与正文姓氏分列，della Porta的创作候选仍待S6。本批未新增sources.csv记录、生平字段或formal relation。

<a id="s4-person-pozzi-puget-querini-rainaldi-20261018"></a>

### S4 person：Pozzi、Puget、Querini与Rainaldi四组索引／正文登记（2026-10-18）

- `cand-2032`（`new-person:luigi-pozzi-99e955d500`）→ [路易吉·波齐（Luigi Pozzi）](../../../04-knowledge/units/persons/luigi-pozzi.md)；依据索引P.csv#235与正文第15章第I节，印刷页362；OCR L19登记。
- `cand-2070`（`new-person:pierre-puget-c313de05b2`）→ [皮埃尔·皮热（Pierre Puget）](../../../04-knowledge/units/persons/pierre-puget.md)；依据索引P.csv#273与正文第10章第II节，印刷页312；OCR L22登记。
- `cand-2087`（`new-person:giacomo-querini-7687c88ca3`）→ [贾科莫·奎里尼（Giacomo Querini）](../../../04-knowledge/units/persons/giacomo-querini.md)；依据索引Q-R.csv#14与正文第6章第I节，印刷页152；OCR L72–74登记。
- `cand-2092`（`new-person:carlo-rainaldi-7ecc91cf92`）→ [卡洛·拉伊纳尔迪（Carlo Rainaldi）](../../../04-knowledge/units/persons/carlo-rainaldi.md)；依据索引Q-R.csv#19与正文第7章第I节，印刷页187；OCR L230登记。

四组均为单候选S3 new身份组。Pozzi临摹工作、Puget浮雕归属、Querini的Sagredo继承人称谓及Rainaldi方案语境均按来源原有范围记录；未新增外部来源或formal relation。

登记后人物类型S4为592组/684条已登记、472组/473条待登记；全书KU=2020。

<a id="s4-person-name-fields-pozzi-puget-querini-rainaldi-20261018"></a>

### S4结构化姓名字段登记：四张人物卡（2026-10-18）

四张卡姓名表共登记8条source_backed enrichment行（`enr-15004`、`enr-15005`、`enr-15006`、`enr-15007`、`enr-15008`、`enr-15009`、`enr-15010`、`enr-15011`），全部引用既有Haskell书目来源ID；Querini正文重复称名并保留索引正名。本批未新增sources.csv记录、生平字段或formal relation。

<a id="s4-person-sagredo-family-endpoints-20261018"></a>

### S3身份复核与S4人物直接端点登记：Sagredo三位人物（2026-10-18）

- `cand-2326`（`new-person:gherardo-sagredo-6252819bc6`）→ [杰拉尔多·萨格雷多（Gherardo Sagredo）](../../../04-knowledge/units/persons/gherardo-sagredo.md)；索引S.csv#14、第9章，印刷页263–264；OCR L236、241、246；S3续核（2026-10-18）：DIA馆藏号38.56的沿革记录将Gherardo Sagredo列在Zaccaria之后，姓名及卒年与第9章对应；该作品沿革只支持身份比对，不把收藏转移叙述转成新关系事实。另查Princeton object x1948-601列Gherardo生卒年1691–1738，而Haskell p.264称其1738年去世时49岁；年龄差异留待后续事实核验，不改变本次身份分组。
- `cand-2327`（`new-person:niccolo-sagredo-52f2c679cd`）→ [尼科洛·萨格雷多（Niccolò Sagredo）](../../../04-knowledge/units/persons/niccolo-sagredo.md)；索引S.csv#15、第9章，印刷页263–264；OCR L234、243；另见第6章第I节，印刷页152、OCR L70；S3续核（2026-10-18）：Treccani《Enciclopedia Italiana》Mario Brunetti撰“SAGREDO, Niccolò”记其为威尼斯总督并于1675年当选；书中第6章p.152的全名和第9章p.263的总督称谓、当选年份与之相合。cand-2327与既有Zaccaria Sagredo及其父Stefano保持分立。
- `cand-2328`（`new-person:sagredo-stefano-fce8efdd59`）→ [斯特法诺·萨格雷多（Stefano Sagredo）](../../../04-knowledge/units/persons/stefano-sagredo.md)；索引S.csv#16、第9章，印刷页263注1；OCR L414；S3续核（2026-10-18）：索引S.csv#16给出“Sagredo, Stefano”；第9章p.263注1转述Barbaro称Zaccaria为Stessano Sagredo之子，既有S2页图校读记该姓名为“Steffano”。三种拼写按索引名、OCR与页图读法保留，指向同一书内父辈人物。对照Princeton University Art Museum object x1948-601时，其来源链虽列Niccolò之弟Stefano及Zaccaria之父，但以“possibly”限定沿承，且将Zaccaria生年列为1633，与书中转引的1653不合；该外部对应记为undecided，不据此改动书内身份或生年。

外部记录结论：cand-2326 → same（Detroit Institute of Arts collection record）；cand-2327 → same（Treccani, Enciclopedia Italiana）；cand-2328 → undecided（Princeton University Art Museum）。Niccolò、Stefano、Gherardo分别对应不同身份组；Stefano的Princeton馆藏沿革仅作未决比对，保留其对Zaccaria生年的冲突，不改写书内原名和日期。五条直接S2关系候选留待S6审查，未新增formal relation。

登记脚本 `register_s4_person_sagredo_family_endpoints_20261018.py` 与姓名字段脚本 `register_s4_person_name_fields_sagredo_family_20261018.py` 均先dry-run后apply。

登记后人物类型S4为595组/687条已登记、469组/470条待登记；全书KU=2023。

<a id="s4-person-name-fields-sagredo-family-20261018"></a>

### S4结构化姓名字段登记：Sagredo三张人物卡（2026-10-18）

三张人物卡登记7条source_backed姓名enrichment行（`enr-15012`、`enr-15013`、`enr-15014`、`enr-15015`、`enr-15016`、`enr-15017`、`enr-15018`），均引用既有Haskell书目来源ID。Gherardo卡保留遗嘱拼写“Girardo P.O Sagredio”；Niccolò卡保留索引名与第6章正文全名；Stefano卡分列索引“Stefano”、脚注OCR“Stessano”及页图校读“Steffano”。Princeton馆藏沿革的外部身份比对仍为undecided，未写成姓名事实。本批未新增sources.csv记录、生平字段或formal relation。


<a id="s3-s4-person-m-index-endpoints-20261018"></a>

### S3身份复核与S4人物端点登记：M索引组（2026-10-18）

- `cand-1552`（原组`new-person:duchess-marlborough-of-a578c57838`）→ `new-person:sarah-churchill-duchess-of-marlborough` → [萨拉·丘吉尔（Sarah Churchill）](../../../04-knowledge/units/persons/sarah-churchill.md)；NPG person record mp02960 identifies Sarah Churchill (née Jenyns/Jennings), 1660–1744, as Duchess of Marlborough and wife of John Churchill, 1st Duke; Haskell p.278 places the title in the context of Lord Manchester's 1709 Venice embassy. No matching person KU exists. New identity group; the undated letter's attribution is not independently verified and its relation_candidate remains for S6.
- `cand-1585`（原组`new-person:louis-maupertuis-pierre-bddd1f3354`）→ `new-person:pierre-louis-moreau-de-maupertuis` → [皮埃尔-路易·莫罗·德·莫佩尔蒂（Pierre-Louis Moreau de Maupertuis）](../../../04-knowledge/units/persons/pierre-louis-moreau-de-maupertuis.md)；Deutsche Biographie GND 118731998 lists “Maupertuis, Pierre-Louis” and “Maupertuis” as names for Pierre-Louis Moreau de Maupertuis, matching the index and p.349 body mention. No matching person KU exists. New identity group; external identity evidence does not validate the meeting claim in the relation_candidate.
- `cand-1586` 与 `cand-1587` 合并为 `new-person:maximilian-ii-emanuel-of-bavaria-074eaa9da4`，共同映射至一张Maximilian II Emanuel人物卡；Deutsche Biographie GND 11857941X列明Max Emanuel与Maximilian II. Emanuel为同一选帝侯记录。
- `cand-1586`（原组`new-person:bavaria-elector-emmanuel-max-of-185c8d9fb9`）→ `new-person:maximilian-ii-emanuel-of-bavaria-074eaa9da4` → [马克西米连二世·埃曼努埃尔（Maximilian II Emanuel of Bavaria）](../../../04-knowledge/units/persons/maximilian-ii-emanuel-of-bavaria.md)；Deutsche Biographie GND 11857941X lists Max Emanuel and Maximilian II. Emanuel under one identity and records him as Elector of Bavaria from 1679. This matches cand-1586 (pp.193, 278) and cand-1587 (p.277, commission in 1704). The prior separate groups are superseded and merged as one new identity group; no matching person KU exists.
- `cand-1605`（原组`new-person:christian-louis-mecklenburg-of-6ce0779819`）→ `new-person:christian-ludwig-ii-mecklenburg-schwerin` → [克里斯蒂安·路德维希二世（Christian Ludwig II of Mecklenburg-Schwerin）](../../../04-knowledge/units/persons/christian-ludwig-ii-of-mecklenburg-schwerin.md)；Deutsche Biographie GND 102111847 lists “Christian Ludwig, Mecklenburg, Herzog” as an alternate name for Christian Ludwig II of Mecklenburg-Schwerin (1683–1756), matching Haskell's index form and body title. The commission date is unstated, so only the identity/name correspondence is used. No matching person KU exists.
- `cand-1587`（原组`new-person:bavaria-elector-maximilian-of-7d0b923214`）→ `new-person:maximilian-ii-emanuel-of-bavaria-074eaa9da4` → [马克西米连二世·埃曼努埃尔（Maximilian II Emanuel of Bavaria）](../../../04-knowledge/units/persons/maximilian-ii-emanuel-of-bavaria.md)；cand-1587在第10章p.277称Maximilian of Bavaria；Deutsche Biographie GND 11857941X将Maximilian II. Emanuel与Max Emanuel列为同一巴伐利亚选帝侯记录。与cand-1586并入同一new身份组，没有匹配既有person KU。
- `cand-1525`（原组`new-person:mantua-of-73894be007`）由`new`改为`undecided`：书后索引M.csv#62及第8章p.216只称‘Marquis of Mantua’，未给个人姓名；旧S3理由误称其为full personal name，现撤回。尚无本批外部记录或书内跨章锚点能把这一头衔唯一对应到具体人物，故由new改为undecided，不登记KU。后续需有据的1656年曼图亚头衔持有人或原始委托记录才能消歧；关系候选st-chp8-p216-magni-working-for-marquis-mantua仍待S6。

本批登记4个S3人物组、5条候选映射、4张KU卡及14条source_backed姓名字段；新增5条外部身份对齐行（4个外部记录），并登记4个外部来源ID。6条直接S2 relation_candidate（含待证的cand-1525）全部留待S6，未新增formal relation。

登记后人物类型S4为599组/692条已登记、463组/464条待登记；全书KU=2027。


<a id="s3-s4-person-medici-endpoints-20261018"></a>

### S3身份组登记与S4人物端点：Medici索引候选（2026-10-18）

- cand-1606（原组new-person:anna-de-ludovica-maria-medici-4e4e0c1fff）→ new-person:anna-de-ludovica-maria-medici-4e4e0c1fff → [安娜·玛丽亚·卢多维卡·德·美第奇（Anna Maria Ludovica de' Medici）](../../../04-knowledge/units/persons/anna-maria-ludovica-de-medici.md)；索引与第10章p.282均使用Anna Maria Ludovica形式；无匹配的既有person KU。保留现有new身份组，不将未见于本书的姓名异体补入。
- cand-1626（原组new-person:de-francesco-maria-medici-d2f7719ab0）→ new-person:de-francesco-maria-medici-d2f7719ab0 → [弗朗切斯科·玛丽亚·德·美第奇（Francesco Maria de' Medici）](../../../04-knowledge/units/persons/francesco-maria-de-medici.md)；索引提供Medici姓氏，第8章p.229提供正文称名及叔侄语境；无匹配的既有person KU。该关系候选不在S4写为正式边。
- cand-1627（原组new-person:de-gastone-gian-medici-6164ea1b9e）→ new-person:de-gastone-gian-medici-6164ea1b9e → [吉安·加斯托内·德·美第奇（Gian Gastone de' Medici）](../../../04-knowledge/units/persons/gian-gastone-de-medici.md)；索引列Grand Duke Gian Gastone de'，第8章p.229有两处正文提及。保留与Ferdinand相区分的候选映射；不把相邻句中关于Ferdinand的1663年出生日期转移给Gian Gastone。
- cand-1628（原组new-person:de-isabella-medici-6acace310c）→ new-person:de-isabella-medici-6acace310c → [伊莎贝拉·德·美第奇（Isabella de' Medici）](../../../04-knowledge/units/persons/isabella-de-medici.md)；索引姓名及Bracciano头衔与第4章p.98注3的Isabella de' Medici相合。保持与cand-5550（Paolo Giordano II之身份未明妻子）分开；不以同名推定同一人物。

本批沿用4个既有S3 new人物组，登记4张KU卡、4条候选映射和14条source_backed名称／头衔字段；身份依据为既有书内索引与正文来源，未新增外部身份对齐行或sources.csv记录。8条直接S2 statement中5条relation_candidate继续待S6，3条非关系叙述不转为关系；未新增formal relation。cand-1628与仍为undecided的cand-5550保持区分。

登记后person类型S4为603组/696条已登记、459组/460条待登记；全书KU=2031。


<a id="s3-s4-person-montage-endpoints-20261018"></a>

### S3身份组登记与S4人物端点：M索引候选（2026-10-18）

- cand-1673（原组new-person:alvise-doge-mocenigo-112023801c）→ new-person:alvise-doge-mocenigo-112023801c → [阿尔维塞·莫切尼戈（Alvise Mocenigo）](../../../04-knowledge/units/persons/alvise-mocenigo.md)；索引与第9章p.269注1均使用Doge Alvise Mocenigo；书内未给出在任序号。本卡保留源内指称，不作外部人物消歧。
- cand-1689（原组new-person:de-michel-montaigne-49e9b48a8a）→ new-person:de-michel-montaigne-49e9b48a8a → [米歇尔·德·蒙田（Michel de Montaigne）](../../../04-knowledge/units/persons/michel-de-montaigne.md)；索引列出Michel de Montaigne，第15章p.370以Montaigne称呼门上格言的作者；本卡保留书内归属，不声称独立核验。
- cand-1692（原组new-person:da-federigo-montefeltre-7c480bf440）→ new-person:da-federigo-montefeltre-7c480bf440 → [费代里戈·达·蒙特费尔特罗（Federigo da Montefeltre）](../../../04-knowledge/units/persons/federigo-da-montefeltre.md)；索引与第2章p.54均给出Federigo da Montefeltre全名；与未命名宫殿候选cand-4746分开，关系留待S6。
- cand-1697（原组new-person:claudio-monteverdi-306c7d79d5）→ new-person:claudio-monteverdi-306c7d79d5 → [克劳迪奥·蒙特威尔第（Claudio Monteverdi）](../../../04-knowledge/units/persons/claudio-monteverdi.md)；索引列出Claudio Monteverdi，第4章p.96称Monteverdi；脚注2仅指向Prunières (1926)，作为书目定位而非关系或独立查证。

本批沿用4个既有S3 new人物组，登记4张KU卡、4条候选映射和12条source_backed名称字段；身份依据为书内索引与正文，未新增外部身份对齐行或sources.csv记录。5条直接S2 statement中4条relation_candidate继续待S6，Monteverdi的Prunières (1926)脚注仅为书目定位；未新增formal relation。

登记后person类型S4为607组/700条已登记、455组/456条待登记；全书KU=2035。


<a id="s3-s4-person-s-index-endpoints-20261018"></a>

### S3身份组登记与S4人物端点：S索引候选（2026-10-18）

- cand-2347（原组new-person:nicola-salvi-4ff08e1bab）→ new-person:nicola-salvi-4ff08e1bab → [尼古拉·萨尔维（Nicola Salvi）](../../../04-knowledge/units/persons/nicola-salvi.md)；S.csv#35与第8章p.223均给出Nicola Salvi全名；礼拜堂作为教堂内部空间保持独立，建造关系待S6。
- cand-2357（原组new-person:de-santi-tommaso-ed5fd73fba）→ new-person:de-santi-tommaso-ed5fd73fba → [托马索·德·桑蒂（Tommaso de Santi）](../../../04-knowledge/units/persons/tommaso-de-santi.md)；索引与正文称名为Tommaso de’ Santi，遗嘱引文拼作Tomaso；原始遗嘱未独立查阅。Gherardo／Girardo身份对应仍待S3，不通过登记Tommaso KU替代该裁决。
- cand-2358（原组new-person:carlo-saraceni-d6fa6d7fe0）→ new-person:carlo-saraceni-d6fa6d7fe0 → [卡洛·萨拉切尼（Carlo Saraceni）](../../../04-knowledge/units/persons/carlo-saraceni.md)；索引S.csv#46确认完整姓名；p.205句末与p.206续行构成同一条Roomer藏画陈述，保留两条S2记录但不当作两项作品事实。
- cand-2360（原组new-person:giuseppe-sardi-d9fb8f5ac8）→ new-person:giuseppe-sardi-d9fb8f5ac8 → [朱塞佩·萨尔迪（Giuseppe Sardi）](../../../04-knowledge/units/persons/giuseppe-sardi.md)；索引列p.248、269；p.248明确区分Antonio Barbaro为设计者、Sardi为建造者，p.269只称Longhena与Sardi受聘建造新教堂，不推定具体分工。

本批沿用4个既有S3 new人物组，登记4张KU卡、4条候选映射和14条source_backed名称字段；身份依据为书内索引与正文，未新增外部身份对齐行或sources.csv记录。7条relation_candidate记录继续待S6，其中Saraceni跨页续句、Tommaso遗嘱摘要与引文保留来源层差异；Gherardo／Girardo身份对应仍待S3，不合并。未新增formal relation。

登记后person类型S4为611组/704条已登记、451组/452条待登记；全书KU=2039。


<a id="s3-identity-review-duchess-of-savoy-20261018"></a>

### S3人物身份复核：Duchess of Savoy（2026-10-18）

- cand-2383由new改为undecided，原组new-person:duchess-of-savoy-5fdc78ee0e撤回，不登记KU。S.csv#71及第3章p.65只有“Duchess of Savoy”称号，虽有17世纪末和Turin语境，未给个人姓名，也没有书内跨章锚点能对应cand-2380或cand-2381。不因同属Savoy或头衔相近而合并；关系候选st-chp3-seci-l26-33-duchess-wanted-ciro-ferri、st-chp3-seci-l26-33-duchess-turin-not-prevented继续待S6。

复核后person类型S4为611组/704条已登记、450组/451条待登记；全书KU=2039。

<a id="s4-schmidt-schonborn-person-endpoints-20261018"></a>

### S4 person：Schmidt与Schönborn四个身份组登记（2026-10-18）

- cand-2396（new-person:friedrich-georg-schmidt-91439cc794）→ [格奥尔格·弗里德里希·施密特（Georg Friedrich Schmidt）](../../../04-knowledge/units/persons/georg-friedrich-schmidt.md)；S2关系候选st-chp20-p409-santifaller-algarotti-portraits-schmidt-print、st-chp20-p409-schmidt-salimbeni-etching留待S6。两条涉及Schmidt的S2关系候选分别涉及Algarotti肖像与1752年版画、以及为Felice Salimbeni制作的蚀刻像；保留原书归因并待S6逐条裁决。
- cand-2397（new-person:friedrich-karl-schonborn-ec83d66570）→ [弗里德里希·卡尔·申伯恩（Friedrich Karl Schönborn）](../../../04-knowledge/units/persons/friedrich-karl-schonborn.md)；S2关系候选st-chp10-p293-note4-franz-schoenborn-letter、st-chp10-p293-note4-franz-letter-addressed-to、st-chp10-p296-bishopric-transfer留待S6。涉及本人的三条S2候选涵盖脚注所述信件及其收件人、以及1746年去世后Würzburg主教职位的转移；原信未读，三条均保留来源限定并待S6裁决。
- cand-2398（new-person:franz-johann-philip-schonborn-934e428cde）→ [约翰·菲利普·弗朗茨·申伯恩（Johann Philip Franz Schönborn）](../../../04-knowledge/units/persons/johann-philip-franz-schonborn.md)；S2关系候选st-chp10-p293-note4-franz-schoenborn-letter、st-chp10-p293-note4-franz-letter-authored-by留待S6。同一脚注的综合陈述和作者指认均为S2关系候选；书信原件未读，关系与信件细节待S6依据现有证据裁决。
- cand-2399（new-person:franz-lothar-schonborn-von-9635ffd088）→ [洛塔尔·弗朗茨·冯·申伯恩（Lothar Franz von Schönborn）](../../../04-knowledge/units/persons/lothar-franz-von-schonborn.md)；S2关系候选st-chp7-p195-german-patron-generalization、st-chp7-p195-lothar-schonborn-letter、st-chp7-p195-n2-schoenborn-letter留待S6。相关三条S2候选分别涉及信中陈述、Haskell关于其他德国赞助人的概括，以及脚注书目指引；后两者不作为独立人物关系或已核实原件处理，均留待S6。

四条S3 new决定分别对应四个单候选身份组，各登记一张人物KU。Friedrich Karl与Johann Philip Franz Schönborn按不同全名和独立身份组分别登记。书信及引文均保留Haskell的转述范围；Johann Philip Franz与Friedrich Karl相关信件原件、Lothar Franz所引信件及书目均未在本轮独立查阅。本批不新增外部来源、正式关系或backlog项目。

登记后人物类型S4为615组/708条已登记、446组/447条待登记；全书KU=2043。

<a id="s4-person-name-fields-schmidt-schonborn-20261018"></a>

### S4结构化姓名字段登记：四张人物卡（2026-10-18）

四张卡姓名表共登记9条source_backed enrichment行（enr-15073、enr-15074、enr-15075、enr-15076、enr-15077、enr-15078、enr-15079、enr-15080、enr-15081），全部关联既有Haskell书目来源ID；未新增sources.csv记录、S5生平字段或formal relation。

<a id="s4-schut-segala-serlio-skala-person-endpoints-20261018"></a>

### S4 person：Schut、Segala、Serlio、Skala四组直接端点登记（2026-10-18）

- cand-2415（new-person:corneille-schut-c477be65d5）→ [科内利斯·舒特（Corneille Schut）](../../../04-knowledge/units/persons/corneille-schut.md)；S2关系候选st-chp8-p206-roomer-owned-hundreds-by-flemish-artists留待S6。关系候选将Schut列入Roomer所藏画作的多人作者名单；作品数量和归属范围保持原书的集合表述，候选留待S6。
- cand-2417（new-person:giovanni-segala-c9998cedb7）→ [乔瓦尼·塞加拉（Giovanni Segala）](../../../04-knowledge/units/persons/giovanni-segala.md)；S2关系候选st-chp8-p227-gallery-academic-style留待S6。关系候选将Segala列入Conti为画廊挑选的画家名单；关于同代与风格的评价仍按原文集体限定，候选待S6。
- cand-2419（new-person:sebastiano-serlio-9c5888fd05）→ [塞巴斯蒂亚诺·塞尔里奥（Sebastiano Serlio）](../../../04-knowledge/units/persons/sebastiano-serlio.md)；S2关系候选st-chp4-sec-ii-l46-51-restorers-took-proportions-from-roman-buildings留待S6。Cassiano引文中的集合关系候选把Serlio列在建筑艺术复兴者名单中；不补造其个人作品或具体建筑对应，候选待S6。
- cand-2436（new-person:dubravio-giovanni-skala-b564631145）→ [乔瓦尼·杜布拉维奥·斯卡拉（Giovanni Dubravio Skala）](../../../04-knowledge/units/persons/giovanni-dubravio-skala.md)；S2关系候选st-chp15-p367-skala-possible-statue-subject、st-chp15-p367-skala-student-description留待S6。两条候选分别涉及可能的雕像对象和带问号的Padua学生描述；均不改写为确定身份或经历，留待S6裁决。

四组均为S3 new单候选身份组，登记4张KU卡、4条候选映射和8条source_backed姓名字段。Skala的雕像对象建议与Padua学生描述保留perhaps和问句限定；Schut的数百件作品数量保留为多人集合总量。本批不新增外部来源、正式关系或backlog项目。

登记后人物类型S4为619组/712条已登记、442组/443条待登记；全书KU=2047。

<a id="s4-skippe-sleter-stazio-stone-person-endpoints-20261018"></a>

### S4 person：Skippe、Sleter、Stazio、Stone四组直接端点登记（2026-10-18）

- cand-2437（new-person:john-skippe-c41d071db2）→ [约翰·斯基普（John Skippe）](../../../04-knowledge/units/persons/john-skippe.md)；S2关系候选st-chp16-p375-skippe-in-touch-with-sasso留待S6。唯一关系候选是Haskell脚注所述Skippe与Sasso的联系及其书信目录指引；原信未读，候选待S6。
- cand-2439（new-person:francesco-sleter-5d38f9ab80）→ [弗朗切斯科·斯莱特（Francesco Sleter）](../../../04-knowledge/units/persons/francesco-sleter.md)；S2关系候选st-chp10-p281-bellucci-chandos-chapel-team、st-chp10-p286-moor-park-decoration-open留待S6。两条候选分别涉及礼拜堂装饰雇用和Moor Park工作改派；后一陈述跨页，按原文续句保留，不将其拆成不同身份。
- cand-2508（new-person:andrea-stazio-a3e55b8f8f）→ [安德烈亚·斯塔齐奥（Andrea Stazio）](../../../04-knowledge/units/persons/andrea-stazio.md)；S2关系候选st-chp9-p269-n01-stae-choir-pictures、st-chp9-p269-n01-stazio-bequest留待S6。两条候选区分Stazio遗赠款项与合唱席画作支出；委托者未明，关系候选保留此缺口并待S6。
- cand-2511（new-person:nicholas-stone-02907ebe1f）→ [尼古拉斯·斯通（Nicholas Stone）](../../../04-knowledge/units/persons/nicholas-stone.md)；S2关系候选st-chp2-secii-l62-69-nicholas-stone-baker-bust-account留待S6。关系候选是Haskell转引Stone关于Bernini为Thomas Baker制作胸像及教皇派人阻止的记述；不将引文直接当作已核读原件。

四组均为S3 new单候选身份组，登记4张KU卡、4条候选映射和9条source_backed姓名字段。Sleter在p.286–287的句子跨页续接；Stazio遗嘱明确未说明合唱席画作的委托者；Nicholas Stone的陈述是Haskell转引的嵌套引文。本批不新增外部来源、正式关系或backlog项目。

登记后人物类型S4为623组/716条已登记、438组/439条待登记；全书KU=2051。

<a id="s4-adelaide-worsley-vittrice-visconti-person-endpoints-20261018"></a>

### S4 person：Adelaide Enrichetta、Worsley、Vittrice、Visconti四个直接关系人物组（2026-10-18）

- cand-2380（new-person:adelaide-enrichetta-of-savoy-0950f861b1）→ [阿德莱德·恩里凯塔·德·萨伏依（Adelaide Enrichetta of Savoy）](../../../04-knowledge/units/persons/adelaide-enrichetta-of-savoy.md)；S2关系候选st-chp7-p193-wittelsbach-alliance、st-chp7-p193-adelaide-fails-to-attract-guarini、st-chp7-p193-adelaide-surrounds-artists、st-chp7-p193-ferdinand-maria-marriage留待S6。第7章还称Wittelsbach家族因婚姻与一支“most astute ruling family”结盟；该家族端点按现有S3决定映射至House of Savoy。此项及婚姻、艺术活动语境、未能吸引Guarini等S2关系候选均保留Haskell归因，待S6逐条裁决。
- cand-2819（new-person:richard-worsley-15b37d86ea）→ [理查德·沃斯利（Sir Richard Worsley）](../../../04-knowledge/units/persons/sir-richard-worsley.md)；S2关系候选st-chp16-p375-strange-introduces-worsley-to-sasso、st-chp16-p375-sasso-finds-works-for-worsley留待S6。介绍信及其后Sasso寻购、Worsley赠画的内容均为Haskell书内叙述；S2关系候选继续待S6，不将未具题名的Guardi作品另行消歧。
- cand-2787（new-person:alessandro-vittrice-25d1b90bf9）→ [亚历山德罗·维特里切（Alessandro Vittrice）](../../../04-knowledge/units/persons/alessandro-vittrice.md)；S2关系候选st-chp3-secii-l54-60-vittrice-commissioned-entombment、st-chp3-secii-l54-60-vittrice-nephew-of-philip-friend留待S6。本书将委托时间写作约1601年，并指出委托情况尚未澄清；家庭礼拜堂及与圣菲利普·内里相关的亲属均未具名，两条S2关系候选留待S6，不新增正式关系。
- cand-2781（new-person:antonio-maria-visconti-0f913a4080）→ [安东尼奥·马里亚·维斯孔蒂（Antonio Maria Visconti）](../../../04-knowledge/units/persons/antonio-maria-visconti.md)；S2关系候选st-chp5-note-p121-n7-visconti-shop、st-chp5-note-p121-n7-visconti-theft留待S6。两项内容均来自Haskell转引Bertolotti的脚注；原书未给出十一幅画的题名、所有人或失窃地点。作品端点cand-11910仍为S3 undecided，候选关系待S6，不据此新建作品KU。

四组均为S3 new单候选人物身份组，登记4张KU卡、4条候选映射、9条source_backed姓名字段和1条source_backed作品字段。Adelaide Enrichetta与仅有公爵称号的cand-2383及Anne Marie de Savoye候选cand-2381保持分立；Wittelsbach联盟陈述的家族端点cand-7157已由既有S3决定映射至House of Savoy，关系仍待S6；Worsley索引与正文称名按同一书内身份记录。Vittrice所涉《基督下葬》复用既有work KU，未具名家庭礼拜堂不新建KU，委托语境保留原文未澄清限定。Visconti脚注所引Bertolotti未独立查阅，被盗的十一幅画无题名；cand-11910仍按S3 undecided保留。本批不新增外部来源、正式关系或backlog项目。

登记后人物类型S4为627组/720条已登记、434组/435条待登记；全书KU=2055。

<a id="s4-savorgnan-strudel-subleyras-swanevelt-person-endpoints-20261018"></a>

### S4 person：Savorgnan、Strudel、Subleyras与Swanevelt四组直接人物端点（2026-10-18）

- cand-2378（new-person:faustina-savorgnan-27789ccf3b）→ [福斯蒂娜·萨沃尔尼昂（Faustina Savorgnan）](../../../04-knowledge/units/persons/faustina-savorgnan.md)；S2关系候选st-chp9-p254-faustina-lodovico-marriage、st-chp9-p254-tiepolo-rezzonico-marriage-fresco、st-chp9-p254-solar-chariot-scene留待S6。原文脚注1引Livan和Giussani，本卡只记录Haskell正文叙述。紧接的Rezzonico婚姻壁画及双人乘日车场景按页内语境保留，不视为独立肖像归属；三个S2关系候选留待S6，不新增正式关系。
- cand-2529（new-person:peter-strudel-a6aaeee55b）→ [彼得·施特鲁德尔（Peter Strudel）](../../../04-knowledge/units/persons/peter-strudel.md)；S2关系候选st-chp7-p195-strudel-tarquin、st-chp7-p195-strudel-joseph、st-chp7-p195-lothar-schonborn-letter留待S6。Liechtenstein亲王1691年书信所列Tarquin and Lucretia及Joseph画作均未能落实到具体作品；Joseph身份也未指明。后续Schönborn引文对Strudel裸像绘画的评价仍为Haskell转述，日期尚待核。三条S2关系候选留待S6，不新增作品KU或正式关系。
- cand-2532（new-person:giuseppe-subleyras-1180e5b00c）→ [朱塞佩·苏布莱拉斯（Giuseppe Subleyras）](../../../04-knowledge/units/persons/giuseppe-subleyras.md)；S2关系候选st-chp15-p366-subleyras-drew-pra-plans留待S6。原文只称其为“一位法国画家的儿子”，本卡不推定父亲身份或与其他Subleyras候选合并。计划图未具题名、数量；作品候选cand-10494仍为S3 undecided，该关系候选留待S6，不新建作品KU或正式关系。
- cand-2535（new-person:hermann-swanevelt-610e66be4a）→ [赫尔曼·斯瓦内费尔特（Hermann Swanevelt）](../../../04-knowledge/units/persons/hermann-swanevelt.md)；S2关系候选st-chp5-p135-swanevelt-owned-two-van-laer-pictures、st-chp5-p135-swanevelt-pictures-by-van-laer、st-chp5-notes-l136-swanevelt-catalano-case留待S6。Haskell在Van Laer作品段落中称Swanevelt拥有两幅画，作品作者归属依段落语境而定，画作未具名。脚注转引Bertolotti，称Swanevelt曾指控Francesco Catalano偷窃两幅Van Laer画作；这只是转引的指控，不是裁判结论。三条S2关系候选留待S6，候选画作cand-11915仍为S3 undecided，不新增作品KU或正式关系。

四组均为S3 new单候选人物身份组，登记4张KU卡、4条候选映射和8条source_backed姓名字段。Faustina Savorgnan的婚姻叙述及后续Rezzonico婚姻壁画语境保持原书限定；Strudel的两幅作品候选未辨明，Schönborn引文保留为Haskell转述；Giuseppe Subleyras与未具名的法国画家保持区分，其计划图作品候选仍待证；Swanevelt两幅Van Laer作品未具名，Catalano偷窃说法只记录为Haskell转引的指控。本批10条S2关系候选留待S6，不新增作品KU、正式关系或外部来源。

登记后人物类型S4为631组/724条已登记、430组/431条待登记；全书KU=2059。

<a id="s4-anne-marie-shaftesbury-stanislas-talbot-person-endpoints-20261018"></a>

### S4 person：Anne Marie、Shaftesbury、Stanislas与Talbot四组人物端点（2026-10-18）

- cand-2381（new-person:anne-marie-of-savoy-f98122919d）→ [安娜·玛丽·德·萨伏依（Anne Marie of Savoy）](../../../04-knowledge/units/persons/anne-marie-of-savoy.md)；S2关系候选st-chp13-p341-notes-note4-receipt-date-place-signatory留待S6。原文仅将Anne Marie de Savoye标为收据签署人；收据所述物品被售予Zanetti，不据此认定她是卖方。收据未独立查阅，唯一S2关系候选留待S6；本身份组与Adelaide Enrichetta of Savoy保持分立，不新增正式关系。
- cand-2425（new-person:1st-of-shaftesbury-e97b949355）→ [沙夫茨伯里第一伯爵（1st Earl of Shaftesbury）](../../../04-knowledge/units/persons/1st-earl-of-shaftesbury.md)；S2关系候选st-chp7-p196-verrio_shaftesbury_roles留待S6。Haskell称Verrio曾将第一代伯爵画作Faction，后来又向第三代伯爵（其孙）征询表现新教美德的意见；壁画对象及建议所涉作品未具名，唯一S2关系候选留待S6，不新增正式关系。
- cand-2505（new-person:new-of-poland-poniatowski-stanislas-of-pol-9c93ccb680）→ [斯坦尼斯拉斯·波尼亚托夫斯基（Stanislas Poniatowski, King of Poland）](../../../04-knowledge/units/persons/stanislas-poniatowski-king-of-poland.md)；S2关系候选st-chp10-p298-bellotto-persuaded-to-warsaw、st-chp10-p298-bellotto-warsaw-views、st-chp15-p366-poland-sweden-subscriptions留待S6。第10章称Bellotto在途中受其劝说而停留Warsaw，并为其绘制大量城市景观；第15章仅写波兰国王参加Prà计划，按同一索引页码与第10章全名归入本组。未具名Warsaw views候选cand-9156仍为S3 undecided。三个S2关系候选留待S6，不据此登记正式关系或作品KU。
- cand-2539（new-person:buno-talbot-5fe8942fd7）→ [布诺·塔尔博特（Buno Talbot）](../../../04-knowledge/units/persons/buno-talbot.md)；S2关系候选st-chp7-p197-isham-acquired-paintings-with-advice留待S6。T.csv索引写作“Bruno”，正文写作“Buno”；沿用S3按正文确定的候选规范名，原样保留索引拼写差异。“dissolute”仅作为Haskell对神父的描述归因，不升级为独立人物事实。购画建议关系候选留待S6，不新增正式关系。

四组均为S3 new单候选人物身份组，登记4张KU卡、4条候选映射和8条source_backed姓名字段。Anne Marie de Savoye仅登记为收据签署人，不推定为卖方，并与Adelaide Enrichetta身份组保持分立；Shaftesbury仅以第一伯爵爵位称呼登记，不推补名字；Stanislas Poniatowski的第10章全名与第15章波兰国王称谓按同一索引组登记；Talbot的T.csv索引转写“Bruno”与正文“S2 Buno”并列保留，候选规范名继续依正文，不改写索引或候选表。本批6条S2关系候选留待S6；无formal relation或新增外部来源。

登记后人物类型S4为635组/728条已登记、426组/427条待登记；全书KU=2063。

<a id="s4-tassi-temanza-tessin-thornhill-person-endpoints-20261018"></a>

### S4 person：Tassi、Temanza、Tessin与Thornhill四组人物端点（2026-10-18）

- cand-2542（new-person:agostino-tassi-e888637062）→ [阿戈斯蒂诺·塔西（Agostino Tassi）](../../../04-knowledge/units/persons/agostino-tassi.md)；S2关系候选st-chp2-seciv-l65-77-borghese-palace-decoration-by-tassi留待S6。第49页称Tassi与Gentileschi绘制的壁画完成于1611至1612年；第56页具名Agostino Tassi，并称他受命绘制Don Taddeo出任罗马长官的场景。本卡依S3索引组对应两页语境，不补充外部生平；S2关系候选留待S6，不登记正式关系。
- cand-2546（new-person:temanza-tommaso-8171d459b0）→ [托马索·特曼扎（Tommaso Temanza）](../../../04-knowledge/units/persons/tommaso-temanza.md)；S2关系候选st-chp15-p361-note2-mariette-letter-addressed-to-temanza留待S6。第6章脚注将未刊Zibaldone称为Tommaso Temanza所作；第10章脚注引用Temanza第87页；第15章脚注称Mariette于1768年致信Temanza；第21章书目列出T. Temanza的1778年著作。上述均为Haskell书内引文信息，不代表本轮查阅了原件。致信关系候选留待S6；不在本轮登记正式关系。
- cand-2555（new-person:nicodemus-tessin-younger-09dda9ee95）→ [尼科德穆斯·泰辛（Nicodemus Tessin the Younger）](../../../04-knowledge/units/persons/nicodemus-tessin-younger.md)；S2关系候选st-chp2-seciv-l139-152-tessin-account-locator-and-date、st-chp20-p406-bjurstrom-tessin-drawings留待S6。第56页脚注称其游记为所述旅行记中最完整者，并推测成于1687至1688年，注明斯德哥尔摩藏本位置；第406页称Bjurström讨论Tessin的艺术趣味与绘画收藏。第406页称名按索引归组，正文简称所指未另行核验。两条S2关系候选留待S6，不登记正式关系。
- cand-2568（new-person:james-thornhill-65d8cd6a4b）→ [詹姆斯·索恩希尔爵士（Sir James Thornhill）](../../../04-knowledge/units/persons/james-thornhill.md)；S2关系候选st-chp10-p286-thornhill-st-pauls-dome、st-chp10-p286-moor-park-built、st-chp10-p286-moor-park-decoration-open、st-chp10-p286-queens-bedchamber-commission留待S6。Haskell称圣保罗大教堂穹顶及汉普顿宫王后寝宫天顶交由Thornhill绘制；Moor Park乡间住宅由Sir James Thornhill与Giacomo Leoni先后建造。Styles原拟委托Thornhill装饰Moor Park，争执后改交Amigoni与Francesco Sleter。四条S2关系候选均留待S6，不新增正式关系。

四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和12条source_backed姓名字段。Agostino Tassi依索引第49、56页同组记录，保留第49页装饰语境与第56页全名和受命绘画的语境；Tommaso Temanza以索引全名连接第6、10、15、21章的书内指称，所引原件和出版物未独立查阅；Nicodemus Tessin the Younger依索引将第56注与第406页归入同组，同时标明第406页正文只写Tessin，并与Count Carl Gustav Tessin分开；Sir James Thornhill的St Paul's穹顶、Moor Park与Hampton Court事例仅保留原书所述的受命、建造和改派语气。本批8条S2关系候选留待S6；无formal relation、外部来源或backlog写入。

登记后人物类型S4为639组/732条已登记、422组/423条待登记；全书KU=2067。

<a id="s4-teniers-theodon-tofts-torelli-person-endpoints-20261018"></a>

### S4 person：Teniers、Théodon、Tofts与Torelli四组人物端点（2026-10-18）

- cand-2549（new-person:david-teniers-a9f6e89e4e）→ [大卫·泰尼尔斯（David Teniers）](../../../04-knowledge/units/persons/david-teniers.md)；S2关系候选st-chp14-p358-recommended-study-teniers留待S6。Haskell转述Algarotti建议学习Teniers、Wouwermans、Vernet和Pannini，以兼顾意大利素描的高贵与佛兰德趣味。第358页正文仅称Teniers；本卡全名依书后索引，不扩展其生平或外部身份。该关系候选留待S6，不登记正式关系。
- cand-2566（new-person:baptiste-jean-theodon-db4c8b1420）→ [让-巴蒂斯特·泰奥东（Jean Baptiste Théodon）](../../../04-knowledge/units/persons/jean-baptiste-theodon.md)；S2关系候选st-chp20-p400-enggass-rome-sculpture-book留待S6。第3章称另一侧祭坛有一组Faith crushing Idolatry雕塑，归于Jean Baptiste Theodon，并将其风格与Legros比较；第20章称Enggass的研究讨论了Gesù教堂中Théodon与Legros的雕像。相关作品候选cand-2567、cand-5434、cand-10936仍分别为S3 undecided，本卡不据此登记作品KU或正式创作关系。唯一S2关系候选留待S6。
- cand-2639（new-person:katherine-tofts-2496dc1f4e）→ [凯瑟琳·托夫茨（Katherine Tofts）](../../../04-knowledge/units/persons/katherine-tofts.md)；S2关系候选st-chp10-p302-smith-first-marriage、st-chp10-p302-smith-second-marriage、st-chp10-p302-smith-wynne-pursuit留待S6。Haskell称Smith与Katherine Tofts的第一段婚姻，并以“rich but mad”描述她；该措辞是作者评价，未作为独立事实核实。同段另提Smith追求Giustiniana Wynne及其第二段婚姻，分别保留为不同S2关系候选，不映射为Tofts的关系。本批三条相关关系候选均待S6，不登记正式关系。
- cand-2647（new-person:giacomo-torelli-16d67515c5）→ [贾科莫·托雷利（Giacomo Torelli）](../../../04-knowledge/units/persons/giacomo-torelli.md)；S2关系候选st-chp7-p182-i10、st-chp7-p182-i11、st-chp7-p183-i16、st-chp7-p183-n4-cite-prunieres留待S6。Haskell称Torelli于1645年由帕尔马公爵派往巴黎，此前曾为该公爵工作；其布景和新技术比所服务的歌剧吸引更多注意。第183页称他在Fronde期间财务破产并被监禁数月；此为Haskell书内叙述。脚注4引用Prunières 1913年著作第149页，未独立查阅。四条S2关系候选留待S6，不登记正式关系。

四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和10条source_backed姓名字段。David Teniers依索引全名登记，正文p.358仅称Teniers；Jean Baptiste Théodon以索引第92、400页连接第3章全名与第20章简称，相关雕塑候选cand-2567、cand-5434、cand-10936继续保留S3 undecided；Katherine Tofts只按Haskell第302页所述第一段婚姻登记，同段关于Giustiniana Wynne及Smith第二段婚姻的S2关系候选保持区分；Giacomo Torelli依据索引第182、183页与正文全名归组，保留第183页财务处境归因和脚注书目定位。本批9条S2关系候选留待S6；无formal relation、外部来源或backlog写入。

登记后人物类型S4为643组/736条已登记、418组/419条待登记；全书KU=2071。

<a id="s4-torelli-torresani-triva-tron-person-endpoints-20261018"></a>

### S4 person：Torelli、Torresani、Triva与Tron四组人物端点（2026-10-18）

- cand-2648（new-person:giuseppe-torelli-a6692bccd5）→ [朱塞佩·托雷利（Giuseppe Torelli）](../../../04-knowledge/units/persons/giuseppe-torelli.md)；S2关系候选st-chp19-p389-giuseppe-reports-felice-trojan-subject留待S6。信中称Torelli的兄弟Felice已为一幅已知绘画找到特洛伊题材，并提及Pyrrhus杀害Polyxena及其他构图人物；信件报告题材选择和预期绘制难点，不证明绘画已经完成。原书OCR将Felice转录为“Febee”，S2据页图校读为Felice。该信的原始档案材料未独立查阅；关系候选留待S6。
- cand-2649（new-person:andrea-torresani-a049f34c67）→ [安德烈亚·托雷萨尼（Andrea Torresani）](../../../04-knowledge/units/persons/andrea-torresani.md)；S2关系候选st-chp9-p266-torresani-views留待S6。该句经Haskell转引Moschini，称Sagredo委托Torresani以笔墨绘制100幅views；印刷页图读数为“100”，书本文本OCR为“too”。Moschini原文与单幅作品未独立查阅，数量及委托关系候选留待S6裁决。
- cand-2654（new-person:antonio-triva-0ffbc63d0f）→ [安东尼奥·特里瓦（Antonio Triva）](../../../04-knowledge/units/persons/antonio-triva.md)；S2关系候选st-chp7-p193-munich-italian-painters留待S6。Haskell说一组意大利画家在三十年战争结束后的三十年间受聘于慕尼黑，并列出Pietro Liberi、Antonio Triva、Pietro Bellotti为其中最知名者；该名单不表示穷尽，原文相对年代不转写成精确任职日期。关系候选留待S6。
- cand-2655（new-person:caterina-dolfin-tron-dd7c35da12）→ [卡泰丽娜·多尔芬·特龙（Caterina Dolfin Tron）](../../../04-knowledge/units/persons/caterina-dolfin-tron.md)；S2关系候选st-chp10-p318-venetian-status-quo-limited-doctrine-origin留待S6。Haskell称启蒙思想可能较容易通过审查，并可能在Consul Smith的图书馆或Caterina Dolfin Tron及其知识界朋友中讨论；作者随后把威尼斯维护现状的利益视为共和国未成为启蒙学说发源地的原因。might／perhaps限定均保留；不据此断言Tron实际参加讨论，威尼斯政治文化判断仍归于Haskell。关系候选留待S6。

四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和8条source_backed姓名字段。Giuseppe Torelli依据附录书信题头和索引登记；书信内容报告其兄弟Felice选定画题及预期绘制难点，不证明作品完成，OCR的Febee按S2页图校读记录为Felice。Andrea Torresani依据第9章及索引登记；Haskell转引Moschini的句子中，印刷页图读作100 views，OCR转录为too views，Moschini原文及单幅作品未独立查阅。Antonio Triva仅按Haskell列举为慕尼黑受聘意大利画家之一登记，保留“best known”非穷尽和相对年代限定。Caterina Dolfin Tron保留Haskell的might/perhaps语气；可能讨论不记作已发生事件，威尼斯状态 quo 的判断仍归于作者。四条S2关系候选留待S6；不新增外部来源、正式关系或backlog项目。

登记后人物类型S4为647组/740条已登记、414组/415条待登记；全书KU=2075。

<a id="s4-troy-tubeuf-turchi-uccelli-person-endpoints-20261018"></a>

### S4 person：de Troy、Tubeuf、Turchi与Uccelli四组人物端点（2026-10-18）

- cand-2656（new-person:de-francois-troy-41388b5a89）→ [弗朗索瓦·德·特鲁瓦（François de Troy）](../../../04-knowledge/units/persons/francois-de-troy.md)；S2关系候选st-chp10-p285-carriera-met-de-troy留待S6。Haskell称Carriera见过Rigaud、Watteau及其他艺人与鉴赏家，并在集体名单中列出de Troy。该处没有提供其单独会面细节；相关关系候选留待S6。
- cand-2657（new-person:jacques-tubeuf-da9776ab01）→ [雅克·蒂伯夫（Jacques Tubeuf）](../../../04-knowledge/units/persons/jacques-tubeuf.md)；S2关系候选st-chp7-p181-i19留待S6。Haskell称Mazarin未能说服Bernini扩建一座其从Tubeuf处强行取得的宫殿。原文没有提供取得日期、法律机制或宫殿确切名称；以上均保留为书内叙述，关系候选留待S6。
- cand-2660（new-person:alessandro-turchi-62c226570b）→ [亚历山德罗·图尔基（Alessandro Turchi）](../../../04-knowledge/units/persons/alessandro-turchi.md)；S2关系候选st-chp7-p185-i05、st-chp7-p185-i11留待S6。Haskell称La Vrillière在1640年代增加一组绘画，并列出Alessandro Turchi名下的《The Death of Cleopatra》。该归属仍是书内陈述，相关系列和作品关系候选分别留待S6；S2记录页图将OCR在题名后的尾随撇号校为转录误差。
- cand-2665（new-person:ferdinando-uccelli-49b207abe4）→ [费迪南多·乌切利（Ferdinando Uccelli）](../../../04-knowledge/units/persons/ferdinando-uccelli.md)；S2关系候选st-chp19-p391-smith-1770-picture-list留待S6。Haskell称Smith于1770年去世时，公证人Uccelli记录其宫殿内有数百幅画；清单仅列主题而不列作者。该段未命名宫殿，Archivio di Stato记录及C. A. Levi的再版未独立查阅；关系候选留待S6。

四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和8条source_backed姓名字段。François de Troy依据索引全名和第10章集体名单中的de Troy登记；不补写个人会面细节。Jacques Tubeuf依据索引及第7章被称作金融家之正文记录；强行取得宫殿的具体法律机制、日期与宫殿名称未见于该处。Alessandro Turchi的T.csv索引行未列页码，正文p.185提供全名及作品归属语境；保留Haskell归属、系列边界和OCR尾随撇号校读。Ferdinando Uccelli依据索引与附录p.391登记为Haskell所称公证人；Smith宫殿未在该段具名，档案清单与Levi出版物未独立查阅。五条S2关系候选继续留待S6；无外部来源、formal relation或backlog写入。

登记后人物类型S4为651组/744条已登记、410组/411条待登记；全书KU=2079。

<a id="s4-vico-vigarani-viola-viviani-person-endpoints-20261018"></a>

### S4 person：Vico、Vigarani、Viola与Viviani四组人物端点（2026-10-18）

- cand-2770（new-person:giambattista-vico-fecfefaafe）→ [詹巴蒂斯塔·维柯（Giambattista Vico）](../../../04-knowledge/units/persons/giambattista-vico.md)；S2关系候选st-chp13-p337-note1-conti-letter-to-vico-1728留待S6。Haskell脚注称Conti致Vico的1728年信由Fisch与Bergin刊于第184页；脚注中的Conti仅有姓氏，身份仍有歧义，书信及所引出版页未独立查阅。正文转录在1728年后有句点，S2据页图校读为无句点；该关系候选留待S6。
- cand-2774（new-person:gaspare-vigarani-7728563f06）→ [加斯帕雷·维加拉尼（Gaspare Vigarani）](../../../04-knowledge/units/persons/gaspare-vigarani.md)；S2关系候选st-chp7-p185-i26留待S6。Haskell称Vigarani受召从Mantua到Mazarin宫殿建剧场，发现空间不足后“移至Tuileries”。原句对移动主体表达压缩，不据此断言剧场在Tuileries建成；脚注引文页码未独立查阅，关系候选留待S6。
- cand-2776（new-person:domenico-viola-9c07bd68a7）→ [多梅尼科·维奥拉（Domenico Viola）](../../../04-knowledge/units/persons/domenico-viola.md)；S2关系候选st-chp5-p136-cerquozzi-close-friend-domenico-viola留待S6。Haskell称Cerquozzi最亲密的两位朋友是画家Domenico Viola与Giacinto Brandi；原文未给出日期或进一步语境。该朋友关系候选留待S6裁决。
- cand-2788（new-person:vincenzo-viviani-fd372f4147）→ [温琴佐·维维亚尼（Vincenzo Viviani）](../../../04-knowledge/units/persons/vincenzo-viviani.md)；S2关系候选st-chp8-p229-ferdinand-education留待S6。Haskell称Ferdinand由Viviani、Lorenzini、Redi等人教育；本段只写Viviani姓氏，不以该段扩写姓名或经历。教育关系候选留待S6。

四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和8条source_backed姓名字段。Giambattista Vico依据UVWXYZ.csv全名及第13章脚注中的姓氏登记；脚注引用的1728年书信及Fisch与Bergin第184页未独立查阅，Conti姓氏端点仍有歧义，页图对1728年后标点的校读按S2保留。Gaspare Vigarani依据索引与p.185正文登记；原句对移往Tuileries的主体表达压缩，不据此断言剧场建成，脚注Hautecœur页码未独立查阅。Domenico Viola依据索引和p.136正文登记为Haskell所称Cerquozzi两位密友之一，不补入原文未给的日期或语境。Vincenzo Viviani依据索引全名与p.229正文姓氏登记；正文仅称Viviani，不扩展其名字或经历。四条S2关系候选留待S6；无外部身份来源、formal relation或backlog写入。

登记后人物类型S4为655组/748条已登记、406组/407条待登记；全书KU=2083。

<a id="s4-vleughels-wael-wagner-webster-person-endpoints-20261018"></a>

### S4 person：Vleughels、de Wael、Wagner与Webster四组人物端点（2026-10-18）

- cand-2789（new-person:nicolas-vleughels-f1b8031c61）→ [尼古拉·弗勒赫尔（Nicolas Vleughels）](../../../04-knowledge/units/persons/nicolas-vleughels.md)；S2关系候选st-chp10-p285-carriera-met-vleughels、st-chp13-p343-notes-note3-named-dedicatees留待S6。Haskell将Vleughels列入Carriera所遇艺人与鉴赏家的集体名单；另一脚注将他列入Zanetti画页受赠者名单，但不对应具体纸张。两处均不提供个别会面或逐件赠送细节；两条关系候选留待S6。
- cand-2795（new-person:baptiste-de-jean-wael-5ccecc0733）→ [让-巴蒂斯特·德·瓦尔（Jean-Baptiste de Wael）](../../../04-knowledge/units/persons/jean-baptiste-de-wael.md)；S2关系候选st-chp8-p208-de-wael-dedicated-print-series留待S6。原书文本OCR作“peasant Use”，S2据页图校读为“peasant life”。版画没有逐件题名或日期，相关脚注3仍待查；委托／赠献关系候选留待S6。
- cand-2796（new-person:german-joseph-wagner-joseph-wagner-029a33bcd8）→ [约瑟夫·瓦格纳（Joseph Wagner）](../../../04-knowledge/units/persons/joseph-wagner-printseller.md)；S2关系候选st-chp13-p340-wagner-german-and-opened-shop-1742、st-chp13-p340-wagner-shop-significant-to-printers留待S6。Haskell称Wagner于1742年开店，并称该店对印刷业者极其重要；S2据页图校正“significance.to printers”中的OCR多余句点。该店的名称、地址和精确类型未确定；脚注4不回指国籍或开店日期，两条关系候选留待S6。
- cand-2805（new-person:john-webster-6bdfe375fe）→ [约翰·韦伯斯特（John Webster）](../../../04-knowledge/units/persons/john-webster-playwright.md)；S2关系候选st-chp4-sec-i-l42-67-fn98-white-devil-inspiration留待S6。Haskell脚注称Isabella de’ Medici被勒死的事件启发了Webster的《The White Devil》；这是作者的文学影响判断，未独立评价。该关系候选留待S6。

四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和9条source_backed姓名字段。Nicolas Vleughels的全名取自索引，正文p.285与p.343脚注均只写Vleughels；Carriera会面名单不含个别细节，Zanetti受赠者名单也不对应具体纸张。Jean-Baptiste de Wael的p.208引文OCR作peasant Use，S2按页图校读为life；版画未逐件题名或定年，脚注3仍待查。Joseph Wagner的p.340两条陈述分别记录1742年开店及店铺对印刷业者的重要性；S2页图校正.to中的OCR多余句点，并确认脚注4不回指国籍或开店年份；店铺名称、地址和精确类型仍未确定。John Webster依据索引及p.98脚注登记；《The White Devil》的影响说法归于Haskell，未作独立评价。六条S2关系候选继续留待S6；无外部来源、formal relation或backlog写入。

登记后人物类型S4为659组/752条已登记、402组/403条待登记；全书KU=2087。

<a id="s4-wilson-de-witte-wouwermans-wren-person-endpoints-20261018"></a>

### S4 person：Wilson、de Witte、Wouwermans与Wren四组人物端点（2026-10-18）

- cand-2815（new-person:richard-wilson-6ea937c8d1）→ [理查德·威尔逊（Richard Wilson）](../../../04-knowledge/units/persons/richard-wilson.md)；S2关系候选st-chp10-p301-smith-official-visitors留待S6。Haskell写道Wilson等人“at one time or another”受Smith接待；名单没有给出Wilson单独到访的时间或情节。脚注7所引Levey文章及页码未独立查阅；该集体接待关系候选留待S6。
- cand-2817（new-person:de-peter-witte-d00315b83f）→ [彼得·德·维特（Peter de Witte）](../../../04-knowledge/units/persons/peter-de-witte.md)；S2关系候选st-chp8-p206-roomer-owned-hundreds-by-flemish-artists留待S6。原文称Roomer拥有数百件由该段多位画家创作的作品，并以“many others”继续开放名单；数量不是de Witte个人作品数，也未识别其单件作品。该集体藏品关系候选留待S6。
- cand-2820（new-person:philips-wouwermans-44cfb8cece）→ [菲利普斯·沃维尔曼斯（Philips Wouwermans）](../../../04-knowledge/units/persons/philips-wouwermans.md)；S2关系候选st-chp14-p358-recommended-study-wouwermans、st-chp14-p359-tiepolo-additions-to-pesci-setting留待S6。第358页的学习建议不证明师承；第359页的“worthy of Wouwermans”是风格比较，不把该船、白马或架构画归于Wouwermans。第二处引文经Haskell转述，所引书信未独立查阅；两条关系候选留待S6。
- cand-2821（new-person:christopher-wren-512fe90374）→ [克里斯托弗·雷恩（Christopher Wren）](../../../04-knowledge/units/persons/christopher-wren.md)；S2关系候选st-chp7-p196-whitehall_programme留待S6。原文将Wren与三人并列，称其共同促成Whitehall一处未具名英国教堂的巴洛克装饰；教堂和具体装饰作品均未识别，“most full-blooded”为Haskell评价。该集体关系候选留待S6。

四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和8条source_backed姓名字段。Wilson只关联Smith接待英国访客的集体陈述；同一段中Mead、Newton与Walpole的其他关系陈述不归给Wilson。de Witte仅列入Roomer所藏数百件作品的多人作者名单，未具名单件作品或个人数量。Wouwermans在p.358是Algarotti建议学习的画家之一，p.359仅作作品风格比较；两者均不表示师承或作品归属。Wren与Gennari、Verrio、Gibbons共同出现在Whitehall一处未具名教堂的装饰陈述中。五条相关S2关系候选留待S6；无外部来源、正式关系或backlog写入。

登记后人物类型S4为663组/756条已登记、398组/399条待登记；全书KU=2091。