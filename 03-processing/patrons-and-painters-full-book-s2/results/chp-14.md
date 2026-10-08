# 第十四章候选表面提示裁决（2026-10-08）

定位器在18个reviewed/complete段中给出24条提示。逐项核对规范来源、上下文断言和候选边界后，10条映射、14条不写；定位器只覆盖现有候选词形，不代表实体召回率或语义验收。

新增3个来源候选：Mead在伦敦的绘画收藏（类型未定）、Treviso保存的Algarotti—Bonomo书信群（archive）及Augustus III扩充的古代大师收藏（类型未定）。前两组的具体边界分别缺少藏品清单和档案fonds信息；第三组与Dresden royal gallery的关系未定。未新增KU、statement或S6正式关系。

字符跨度为拼接段文本的零起点、右开区间；行号回到规范来源。索引误撞、泛称、未界定媒介组及身份未决的代词不强行写入。

| 序号 | 来源定位 | 字符跨度 | 提示原文 | 裁决/候选 | 判断依据 |
|---:|---|---:|---|---|---|
| 1 | 14_CHP-14_intro.md#L111 | 762:772 | collection | 映射 cand-11496 (Dr Richard Mead's collection of paintings seen by Algarotti in London (p.357)) | The phrase refers to Dr Richard Mead's identifiable London art collection; preserve its unspecified holdings and keep its type unresolved. |
| 2 | 14_CHP-14_intro.md#L123 | 2742:2749 | in Rome | 映射 cand-4490 (Rome) | Rome is the geographic location of Piranesi's parallel creations; use the existing Rome place candidate, not the unrelated index phrases 'in Rome'. |
| 3 | 14_CHP-14_intro.md#L140 | 11:17 | battle | 不写入 | 'Battle' is a metaphor for conflict between styles, not Salvator Rosa or a titled work. |
| 4 | 14_CHP-14_intro.md#L145 | 1526:1532 | winter | 不写入 | 'Winter' describes the season of Constable's evenings and does not identify Rosalba Carriera. |
| 5 | 14_CHP-14_intro.md#L174 | 1072:1082 | collection | 映射 cand-11497 (Large Treviso collection of letters from Francesco Algarotti to Bonomo (p.349 n.1)) | The note identifies a larger Treviso-held correspondence group, within which the separately recorded Paris letters are a subset; keep fonds and boundary unresolved. |
| 6 | 14_CHP-14_intro.md#L188 | 2860:2867 | subject | 不写入 | 'The subject' means the topic of Algarotti's ideas, not the Contracts index concept. |
| 7 | 14_CHP-14_intro.md#L192 | 3541:3547 | Venice | 映射 cand-2719 (Venice) | Venice is the city containing the two named picture locations; use the place candidate, not the topical Venice index entries. |
| 8 | 14_CHP-14_intro.md#L206 | 5966:5975 | Canaletto | 映射 cand-0499 (Canaletto) | Canaletto is named as the painter in the possessive phrase; the referenced view is separately identified in the main-text statement. |
| 9 | 14_CHP-14_intro.md#L219 | 7508:7514 | Venice | 映射 cand-2719 (Venice) | Venice is where Biffi arrived in 1773; use the geographic city candidate. |
| 10 | 14_CHP-14_intro.md#L33 | 2957:2968 | temperament | 不写入 | 'Temperament' is a general personal quality in Haskell's interpretation, not a separately identified person or work. |
| 11 | 14_CHP-14_intro.md#L6 | 95:106 | art patrons | 映射 cand-4129 (Art patrons) | 'Art patrons' is the social category in Haskell's description of Algarotti; the existing term candidate has the same category meaning. |
| 12 | 14_CHP-14_intro.md#L7 | 451:466 | artistic tastes | 不写入 | 'Artistic tastes' describes Algarotti's critical quality; it is not Joseph Smith or an independently bounded entity. |
| 13 | 14_CHP-14_intro.md#L8 | 1044:1055 | temperament | 不写入 | 'Temperament' is a general quality attributed to Algarotti, not either person candidate returned by the index matcher. |
| 14 | 14_CHP-14_intro.md#L8 | 1184:1193 | character | 不写入 | 'Receptive character' is a description of Algarotti, not Maffeo Barberini. |
| 15 | 14_CHP-14_intro.md#L39 | 1259:1284 | scholarly approach to art | 不写入 | The scholarly approach is an attributed interpretive quality, not the person candidate's index subentry or a separate work. |
| 16 | 14_CHP-14_intro.md#L50 | 1297:1304 | subject | 不写入 | 'Subject' means the generic topic assigned to a history painting, not the Contracts term. |
| 17 | 14_CHP-14_intro.md#L52 | 2979:2990 | old masters | 映射 cand-4288 (Old masters) | 'Old masters' names the broad art-historical category in the contrast with Algarotti's promotion of modern artists. |
| 18 | 14_CHP-14_intro.md#L60 | 2405:2411 | garden | 不写入 | The Italian garden is a generic pictorial setting in the sketch, not an independently identified place. |
| 19 | 14_CHP-14_intro.md#L61 | 2833:2839 | garden | 不写入 | This is the same generic garden setting described as absent from the large version; no bounded garden is identified. |
| 20 | 14_CHP-14_intro.md#L68 | 2374:2384 | collection | 映射 cand-11498 (Augustus III's collection of old masters (p.353)) | The source identifies Augustus III's collection of old masters as an object he sought to enlarge; its identity in relation to the Dresden royal gallery remains unresolved. |
| 21 | 14_CHP-14_intro.md#L68 | 2602:2618 | Italian painting | 不写入 | The 'tradition of Italian painting' is a broad historical characterization; cand-11017 refers to Italian painting as the subject of a specific catalogue, not this tradition. |
| 22 | 14_CHP-14_intro.md#L93 | 2513:2521 | drawings | 不写入 | The large number of drawings is an unbounded medium group within the collection; no separate drawing set or individual sheets are identified here. |
| 23 | 14_CHP-14_intro.md#L95 | 2885:2891 | Venice | 映射 cand-2719 (Venice) | Venice is the city of the visit discussed in this statement; use the place candidate. |
| 24 | 14_CHP-14_intro.md#L102 | 1828:1838 | collection | 不写入 | The pronoun 'their' is explicitly unresolved among the p.347 personal/joint collections, the p.355 family collection, or another group; preserve the existing identity question without forcing a mapping. |

## 写回与核验

- 表格新增：3个候选、10条mentions；未新增statement，补齐10条既有statement的候选引用。
- 写后定位器剩余14条，与14条no-write裁决逐跨度一致。定位器不证明召回完整。
- 严格S2审计：errors=[]; s2_missing=[]; candidates=11477; mentions=27347; statements=12262。
- 关系候选：2331条；本批没有写入S6正式关系。
- 决策计划SHA-256：2d584101fb48fc104d39982ecd9a83705105fd9cdd45142817946a534815d461；脚本SHA-256：69ef779da463b937d8196d49329303f843e1133b402b491b4284b31cc27a8ce6。
- 写前表SHA-256：candidates 14d110c7438e00699a4e9dbeb31c4987ab3475ed8cf756022cb9348bf70af134；mentions c75f88628b6450bcbc54566eb8a21c578fd65e7af2e7fd2e310c0038d55a78ae；statements 435bc84c80d9f49335084155e4231d36e8de62a769e6404d06a94edc951c32ef。
- 写后表SHA-256：candidates 08661d2bd55ac80f82a314a013334e0203cc51d3ab6beda7a4d6a57ba7f73eab；mentions 459ecd81f77e97bef006dca8003aba7c3731f66e4fd30a30d93c420c33a10e14；statements 37ec0304b794b839157bfd00996330612a202ff84c96283c53dbb26921205949。
- 恢复副本：C:\Users\001\AppData\Local\Temp\pnp-s2-chp14-surface-prompts-20261008-121411。

候选提示裁决不取代全书S2交接审计中的未登记实体、重复副本、跨页注释、指代、限定语、候选外键与全部关系候选复核。

## 第十四章p.348通信关系候选与提及补录（2026-10-08）

将原st-chp14-p348-move-to-rome中混合的行程与通信断言分开：保留1734年2月续行至罗马的行程statement；新增Algarotti—Bonomo与Algarotti—Francesco Zanotti两条corresponded_with候选，分别链接p.348注2（L172）和注3（L173）。注2只著录一封致Bonomo的信，不能代替完整往来；所引书信、版本及档案均未独立查阅。

补录跨行mention m-chp14-p348-0111（Francesco Zanotti，1561:1578），映射既有候选cand-2864（索引形为F. M. Zanotti），身份比对留S3。两条Algarotti候选与Zanotti兄弟群体候选保持分立。新增2条statement和1条mention，不新增候选或正式关系。写后全书S2关系候选2,529条、端点齐全2,508条、开放21条；严格审计errors=[]、s2_missing=[]。其余第14章及全书S2关系/限定语仍在审查。

## 第十四章p.349宫廷关系与授衔断言拆分（2026-10-08）

原st-chp14-p349-travel-and-frederick-court把Algarotti的旅行、在Frederick the Great宫廷安置及1740年12月授爵合在一条。现拆为行程statement、settled_at_court_of关系候选，以及受控方向honoured_by的授衔候选；后者主语为Algarotti、宾语为Frederick，日期仅属于授衔。原文未给出进入宫廷的确切日期或授衔文书，不作延伸推断。

p.349现有13条关系候选，端点全齐；该段旅行目的地仍作为有来源的行程事实记录，不推断每处的居住/任职。全书关系候选2,530条、完整端点2,509条、开放21条。新增2条statement、无新增mention/candidate或正式关系。严格阶段审计errors=[]、s2_missing=[]。其余第14章及全书S2语义审计继续。

## 第十四章p.349另一次拜访Voltaire（2026-10-08）

原复合statement `st-chp14-p349-return-publish-newtonianismo`现只记录Algarotti于1736年底返意、其后约一年在威尼斯与米兰之间停留；Newtonianismo per le Dame的出版仍由既有statement单独记录。新增`st-chp14-p349-another-short-visit-to-voltaire`，记录其在返意前又短暂拜访Voltaire。它与先前的相识及Cirey留居分开，后一次拜访的日期和地点未给出。现有mention `m-chp14-p349-0007`覆盖第二处Voltaire姓名，无需新增mention；不将出版地点指定为米兰或威尼斯。

p.349现有14条S2关系候选，端点14/14齐全；全书关系候选2,531条、端点齐全2,510条、开放21条。statement总数12,311；严格审计`errors=[]`、`s2_missing=[]`；未新增候选、mention或正式关系。第14章和全书S2语义审查继续。

## 第十四章p.350正文与注1关系复核（2026-10-08）

将原复合状态statement拆为年龄/著作出版状态、与Voltaire已成朋友及在伦敦/巴黎的社会成功、在威尼斯的财富/声望/关系网状态。后者均归于Haskell对1737年威尼斯期间的描述；Voltaire友谊另列关系候选，不等同于p.349再次短访或Cirey留居。补录`royal master` mention `m-chp14-p350-0069`（2509:2521）指向前文点明的Augustus cand-0151，并保留与p.349 cand-0148的S3身份问题。

补回Haskell认为皇家主人对画廊委托方案另有看法的限定；其具体偏好未说明。将Algarotti对Muratori等史家方法的承袭、画廊应代表绘画史与各画派的方案分别列为关系候选。修订“first rediscovery of the primitives” claim，明确原文排除Algarotti本人，不把后续原始主义收藏运动归因于他个人。

p.350注1识别出`cand-10265`档案对象：致Bonomo、1741-09-05、Treviso MSS. 1256。注1关系记录为信件`addressed_to` Bonomo；另以正文主体`he`和脚注连接记录Algarotti的`authored_by`关系。原件/目录未查。新增3条statement、1条mention、0个candidate；新登记3组同名/同机构身份问题供S3对齐。p.350关系候选9条、端点全齐；全书2,536条、2,515条端点齐全、21条开放。严格审计`errors=[]`、`s2_missing=[]`；全书语义复核继续。


## 第十四章p.351语义复审补正（2026-10-08）

p.351首轮23条statement、67条mentions经过复审后，现为45条statement、74条mentions。更正两条`his`误指：`m-chp14-p351-0062/0063`均改指Algarotti；新增7条单数人称指代mention。题材分配、五幅画组、区域名单、Augustus偏好与现代艺术计划分别拆清；未确定“the four Venetians”的实际名单，因为Canaletto在同段被明确说成忽略。

本页28条关系候选均有标量端点，仍处S2候选层；未新增实体候选或S6正式关系。注2把13 February 1751信件与Algarotti、Mariette建立`authored_by`和`addressed_to`候选边，并链接至书目；与第十章S. Rocco信件的身份保留给S3比较。p.351 L53和p.352 Tiepolo画作双向链接，明确该画不属于五幅失传作品组。

对照印本后撤销旧过程记录中的`after.he` OCR纠正：句点见于印本，S0原文保持不变。严格表审计`errors=[]`、`s2_missing=[]`；全书当前12,336条statement、27,409条mentions、2,562条关系候选（2,541条端点齐全，21条开放）。下一处按书序复核p.352；全书S2交接仍未完成。

## 第十四章p.352语义复审补正（2026-10-09）

重读正文`l55-61`与注释`l168-220`并核对印刷p.352。将Tiepolo人物mention及相关statement端点改指人物候选`cand-2572`，保留作品题名候选`cand-2577`；修正跨p.351的Algarotti先行词与本段人称指代。新增10条statement，拆分画作作者/组别/预定对象、Villa Cordellina装饰、1743年信件端点、Smith放弃权利、作品版本位置和注释中的不同说话者/证据限定。mention净增3条；现有76条。将书内引注页码差异、相似书信身份及多个作品候选关系列为S3比较问题，不作合并。

本页18条关系候选全部有标量端点；未新增KU、候选或正式关系。没有把提及Brühl误写成发信/转移已经完成，也没有把“1743年前无实际证据”写成未发生接触。表审计：`s2_missing=[]`、`errors=[]`；两条既存enrichment来源警告及通用语义审查提示保留。下一源段按书序为p.353 `chp-14:14_CHP-14_intro:l63-71`，全书S2未完成。

## 第十四章p.353语义复审补正（2026-10-09）

复审正文、注1以及p.352/p.354跨页续接。修正Tiepolo人称映射至页码相符的人物候选`cand-2572`，修正“this”所指为Melbourne完成版`cand-4101`；Brühl专题中的Algarotti改用索引子目`cand-0045`，身份比较留S3。补录“the author”mention，区分比较性评价与画作古典性断言，并将Brühl两件作品的作者、送达对象、注释所载位置拆成逐件关系候选。信件拆记作者、收件人和携带版画的意图；Brühl拥有的两种装饰母题不逐件指配Maecenas/Flora，仍保留一条开放关系。

p.353现35条statement、75条mention和20条关系候选（19条端点齐全、1条原文端点未定）。note 1与第21章Levey书目条目、Plate 68b题注建立回链；p.352/p.353及p.353/p.354续句互链。没有新增KU、候选或正式关系；图书/期刊和未定年信件未称已独立查阅。严格表审计`errors=[]`、`s2_missing=[]`。

## 第十四章p.354语义复审补正（2026-10-09）

复审已有首轮记录的正文`chp-14:14_CHP-14_intro:l73-83`和注1–5（L186–190），并对照印本物理页8与p.353/p.355续句。Markdown和`CHP-14.pdf`哈希未变，未改S0。p.354首轮27条statement、71条mention经复审；本次没有增删statement、mention、候选、KU或正式关系。11条关系候选端点全部齐全。

关键更正为注5页码：OCR原文保留`p.296`，印本实为`Opere, III, p.206`，据此更正statement和`cand-10306`标签，并在S2登记OCR校读。跨页句的p.354 statement仅陈述本页部分；两位作者未及争论进入关键阶段的内容归p.355，且两页statement双向链接。p.354注2、3、4分别与第21章Levey 1960（书目statement 21）、Watson 1955（statement 17）、Rava 1913（statement 06）条目双向链接；这只确认本书内部引注与书目对应，不表示独立读过被引论文。其他原文限定、注释定位及正文脚注回链经检查未见新增问题。全书严格表审计`errors=[]`、`s2_missing=[]`；本次编辑后全量同步闭合通过：303 passed、2 subtests passed。

## 第十四章p.355语义复审补正（2026-10-09）

复审正文`chp-14:14_CHP-14_intro:l85-95`与注1–3（L191–193），对照印本物理页9，并核对p.354/p.356续接。p.355首轮27条statement、87条mention经复审；14条关系候选端点全部齐全。本次只补书目及statement交叉链接，没有增删知识数据行。

注2中两幅画与两处地点不作一一配对；Pallucchini 1956页41定位与第21章Piazzetta 1956条目双向链接。注3的Levey 1960短引与第21章完整条目及p.354注2互链；G. A. Selva短引与第21章目录条目建立可能匹配链接，仍留待S3确认。两种书内对应均不代表独立查阅被引材料。p.355末句和p.356的续文及Bonomo注1已有跨页链接；Michelessi注1与Bonomo注1按各自页码区分。相关引文限定、跨页指代和关系候选复核后未发现需要新建候选或关系的情况。全量同步闭合通过（303 passed、2 subtests passed）；下一项按书序复核p.356 `chp-14:14_CHP-14_intro:l97-105`，全书S2未交接。

## 第十四章p.356语义复审补正（2026-10-09）

复审正文`chp-14:14_CHP-14_intro:l97-105`与注1–7（L194–200），对照`CHP-14.pdf`物理页10，并核对p.355/p.357续接。源Markdown和PDF哈希未变，未改S0。共30条statement、72条mention；将正文“Venice”mention从Algarotti索引项改映射至威尼斯地点候选，新增一条断言记录其离开意大利后仍关注当地艺术事务，并在艺术推广断言中保留爱国动因。其余语义限定包括Berlin/Potsdam居留范围、Marchiori委托未具名教堂且未确认完成、Rode影响Tiepolo属预测、Walpole赠画及Palladio图稿仍属条件／计划，以及`their collection`指代未定；未扩写未具名对象或将提案写成已完成事实。

印本校读只记S2、不改S0：L101 `commision`→`commission`；注1 `T1`→`Il`、`pretcnderebbe`→`pretenderebbe`；注4 `fame un regalo`→`farne un regalo`、`facilitate`→`facilitare`、`1'esecuzione`→`l'esecuzione`；注7 `Opéré`→`Opere`。既有`thistime`→`this time`记录经页图复核。p.356末句与p.357续句、Bonomo注1及相应脚注链接有效。13条关系候选保持S2，不新增candidate或正式关系；statement净增1条，提及数量、候选数量与coverage不变。严格表审计`errors=[]`、`s2_missing=[]`；p.356之后按书序复核p.357 `chp-14:14_CHP-14_intro:l107-116`，全书S2未交接。


## 第十四章p.357语义复审补正（2026-10-09）

复审正文`chp-14:14_CHP-14_intro:l107-116`及本页脚注，对照印本物理页11并核对p.356/p.358续接。共58条statement、79条mention、36条关系候选，端点36/36齐全。新增2个候选（拟议的Canaletto Grand Canal视图及构图中的Rialto要素）、4条mention和34条statement，修订18条本页statement及1条p.358跨页statement；更正4条旧mention候选映射。

印本校读仅进入S2：`him. with`→`him with`、`ten yeTs`→`ten years`、`os France`→`of France`、`his Use`→`his life`、`Mar-chigian`→`Marchigian`、注6两处`i960`→`1960`、`VHI`→`VIII`，并校正正文 superscript 5及柏林来信前的注5标记。未更改来源文件。

语义上分开Triumph of Venice作品与Batoni作者、Algarotti观看作品的宫殿语境和时间；区分Cleopatra事件与拟议作品；把Pantheon委托、拟由Pannini作画及Bonomo保管请求分别记录，不把请求写成已完成。Tiepolo壁画与modello、Algarotti对Pannini的评价、Pannini/Canaletto对建筑capricci的熟悉程度及Canaletto拟议构图分别拆分。本页注释中的书信作者/收件人/内容及两件Lazzarini作品的互相冲突归属保持各自范围；`his rooms`、作品身份及p.315 Rialto视图与本页视图是否同一均未猜定。没有新建KU或正式关系。

全库严格表审计`errors=[]`、`s2_missing=[]`；全量同步闭合通过（303 passed、2 subtests passed）。当前S2关系候选2,609条，2,588条端点齐全、21条开放。下一项按书序复核p.358 `chp-14:14_CHP-14_intro:l118-124`，全书S2未交接。


## 第十四章p.358语义复审（2026-10-09）

对照印本物理页12复核正文`l118-124`和注1–6（L208–213），核对p.357/p.359续接。36条statement、52条mention及17个候选均已复核；没有新增/删除数据行。校读只记S2，未改来源与原始引文：L123 `ofltalian`→`of Italian`；注4 L211 `VIH`→`VIII`；注5 L212 OCR编号`6`→印本5、`roo`→`100`；注6 L213 `in`→`111`。页图确认注2 `[I pens]ieri`及`[ac]quedotti`中的方括号为印本内容，原样保留。

语义复核维持“负责这种绘画类型”的说法是书信出版后逐渐形成的看法，不写成Algarotti发明画种；审美评价、1741年未具名佛兰德画家与其选题、建筑幻想和古典建筑结构、Pesci/Tesi合作与草图指导、致Pesci书信比喻及艺术家参考分别记录。注2手稿、注3列举的书信/手稿/画册及各处被引页码均未独立查阅。p.357 Canaletto方案的描述与p.359 L127对建筑画家、Tiepolo补画人物的续文保持跨页链接。全库严格表审计`errors=[]`、`s2_missing=[]`；p.358复审后的全量同步闭合通过（303 passed、2 subtests passed）。下一项按书序复核p.359 `chp-14:14_CHP-14_intro:l126-137`，全书S2未交接。

## 第十四章p.359语义复审补正（2026-10-09）

对照印本物理页13复核正文L127–137及注1–4（L214–217），并核对p.358/p.360跨页续接。24条statement、49条mention均保持原数；新建`cand-11522`记录Algarotti欣赏并由Tesi复制的未具名原作组，与复制品候选`cand-10400`分开。将`m-chp14-p359-0025`映射至原作组，将`m-chp14-p359-0040`“the picturesque”改映射至既有概念`cand-10384`。把理论作品评价statement的主语从Algarotti修正为作品候选`cand-10404`，并在旅行断言中明确原作和复制品均未识别、行程无日期。

印本校读写入五条statement的S2 `ocr_corrections`，共六项：L128 `. add`→`add`、`Use`→`life`；L129 `confmed`→`confined`；L131 `himselff`→`himself`；L137 `picturesque.-He`→`picturesque.—He`；注2 L215 `Opéré`→`Opere`。不改源Markdown、S0或`original_quote`。p.359注3、注4所引Gabbrielli相同，但注4未见正文标记，仍为`orphan_unresolved`；不与p.360注4 Leslie互链。12条本页关系候选端点齐全；没有新增KU、statement、mention或正式关系。全库严格表审计`errors=[]`、`s2_missing=[]`，全量同步闭合通过（303 passed、2 subtests passed）；全书S2交接未完成。下一页按书序为p.360。

## 第十四章p.360语义复审补正（2026-10-09）

对照印本物理页14复核正文L140–146和注1–4（L218–220），并核对p.359续句与Plate 60题注。原22条statement经复审为23条，原39条mention补至43条；新增碑铭候选`cand-11523`和4条mention。改正风格冲突statement的主体：冲突本身没有人物候选，不把人物Algarotti误作“待解决之战”的主体。将“Algarottus non omnis”登记为纪念碑碑铭并映射至碑铭候选；把其改编Horace诗句与安置于Algarotti纪念碑分列为两条S2关系候选。纪念碑`cand-4107`与Plate 60版画`cand-4042`保持不同对象；题注只证明版画表现墓前悼念者，不声称图中展示碑铭。

为注2 L219的两处Algarotti补入独立mention。将Biffi引语拆清为Algarotti—Cecilia Emo的有据关系候选，speaker仍为Biffi（由Haskell转引），并保留原信未查、p.328 note 5身份不确定的限定；不新增正式关系。注4 C. R. Leslie的Memoirs引文（印本Memoirs）独立保留，与p.359 note 4无标记的Gabbrielli重复引注不混淆。印本校读：L143 `-psychological`→`psychological`，L146 `Non omnis mortar`→`Non omnis moriar`，注3 L219编号`8`→`3`。修订仅在S2，原始引文和S0未改。

p.360现7条关系候选，7/7端点齐全。全库严格表审计`errors=[]`、`s2_missing=[]`，全量同步闭合通过（303 passed、2 subtests passed）；全书S2未交接。下一项按书序为p.361版图说明。

## 第十四章p.361图版说明语义复审（2026-10-09）

对照`CHP-14.pdf`物理页15，核对Plate 61主页题与上下两图副题，并与书前图版目录现有caption statement交叉定位。S0段`chp-14:14_CHP-14_intro:l148-149`仅保留“a. Early version”；现有mention `m-chp14-plates61-64-0001`的字符范围11:27准确对应原文。扫描页另见“b. Final version”及“TIEPOLO’S CHANGES TO THE BANQUET OF ANTONY AND CLEOPATRA UNDER THE IMPACT OF ALGAROTTI”；这些视觉读数注明PDF物理页15和来源文件，不写回S0，也不造出不存在于S0的mention。页题“Antony”和书前目录“Anthony”的拼法差异保留。

将原合并statement拆清：`st-chp14-p361-plate61-version-sequence`记录`cand-4100`（Cognacq-Jay／早期版）与`cand-4101`（Victoria／最终版）的作品关系；新增`st-chp14-p361-heading-algarotti-impact`记录印本页题把Tiepolo（`cand-3781`）对该题材的改动归于Algarotti（`cand-0050`）影响。第二项以`influenced_by`记录为来源归属候选，不声称独立证实该历史影响。两项均为S2关系候选；没有新建KU、候选、mention或正式关系。

p.361本段现2条statement、2条关系候选，端点2/2齐全；书前Plate 61a/61b的两条既有作品—作者caption也标为关系候选。全库1,019 KU、11,502 candidates、27,421 mentions、12,394 statements；关系候选2,616条，2,595条端点齐全、21条开放。严格阶段审计`errors=[]`、`s2_missing=[]`。下一项为Plate 62–63题注段`chp-14:14_CHP-14_intro:l151-153`；全书S2交接未完成。

## 第十四章Plate 62–63题注语义复审（2026-10-09）

对照`CHP-14.pdf`物理页16–17复核共享段`chp-14:14_CHP-14_intro:l151-153`。p.362印本题注读作“Canaletto: The Prà della Valle in Padua”；S0 OCR“Prato”保留，并记录印本校读。将作者归属、作品描绘的Prà della Valle（`cand-3960`）及该地点在Padua（`cand-3944`）拆为三条关系候选；新增mention `m-chp14-plates61-64-0012`（`Prato della Valle`，25:42）和`m-chp14-plates61-64-0013`（`Padua`，46:51）。将书前p.62地点statement改为`cand-3960`→`cand-3944`；同名索引种子`cand-1804`仍留S3对齐，不合并。

p.363物理页16–17图像的Cerato题注只有“Domenico Cerato: Project for the r”截断片段。完整标题仅从独立书前Plate 63 caption获得，不回填S0；作者和提案地点只通过可追踪的原statement及书前statement表达。p.362图像statement及书前Plate 62 creator/site/location三项、p.363图像作者归属及书前Plate 63 creator/site两项均列S2关系候选。无新增candidate、S6正式关系或全文补写。

本批后全库1,019 KU、11,502 candidates、27,423 mentions、12,396 statements；关系候选2,625条，2,604条端点齐全、21条开放。严格阶段审计`errors=[]`、`s2_missing=[]`。下一项复核Plate 64 `chp-14:14_CHP-14_intro:l155-166`。

## 第十四章Plate 64题注语义复审（2026-10-09）

对照`CHP-14.pdf`物理页18复核旋转图版题注。印本可读为“Francesco Guardi: View of John Strange’s villa at Paese near Treviso”；S0倒序OCR保持不变。新增地点候选`cand-11524`（John Strange在Paese的别墅，type=`place`，状态open），并新增mention `m-chp14-plates61-64-0014`，严格覆盖反转token `alliv`（32:37）。别墅地点与画作`cand-4036`及Paese/Treviso分立。

将图像页现有statement拆分为Guardi归属和作品描绘该别墅两项关系候选。书前caption中的别墅→Paese、Paese→Treviso、别墅与John Strange的题名关联分别改正端点并标为关系候选；“Private Collection, London”因收藏者未指明保持空宾端点和pending，未建泛化机构实体。S0不改，也不将题名的所有格升级为法律所有权。

本页新增1个candidate、1条mention、1条statement；新增/重标7条关系候选，6条端点完整，匿名collection一条保持开放。全库1,019 KU、11,503 candidates、27,424 mentions、12,397 statements；关系候选2,632条，2,610条端点齐全、22条开放。严格阶段审计`errors=[]`、`s2_missing=[]`；全量同步闭合通过（303 passed、2 subtests passed）。下一项按书序转入第十五章p.361 `chp-15:15_CHP-15_sec_i:l3-14`；全书S2交接未完成。
