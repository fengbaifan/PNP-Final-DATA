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
