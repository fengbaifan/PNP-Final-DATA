# 《赞助人与画家》全书 S2 语义处理与交接结果

更新日期：2026-10-15。任务 ID：`patrons-and-painters-full-book-s2`。

**当前状态：全书 S2 语义处理已完成，产物具备内部交接条件；尚未独立语义验收。本轮全书任务的 S3–S6 尚未启动，下一业务阶段为 S3 身份对齐。** 既有对齐、KU、补足与关系记录继续保留，不能据其存在宣称全书后续阶段已完成。

## 范围与覆盖

S0 登记79个来源文件、832段，涵盖书前材料、第1–17章、结论、附录、第二版后记、书目和索引；其中42段为派生视觉转录。第11、12章复用第10章合订规范来源，44段重复 OCR 已有依据地排除，不重复计算正文阅读。来源资产、规范文本与对照副本的区别见[来源登记](../../02-sources/source-registry.md)。

| S2 coverage 登记 | 段数 |
|---|---:|
| reviewed / complete | 678 |
| 有理由排除 / complete | 154 |
| queued 或迁移未完成 | 0 |
| 合计 | 832 |

正文、脚注、图版题注、跨页续句和书内引用均按既有过程记录处理。书目作为出版记录和引文定位材料，索引作为候选定位材料，不将两者当作正文断言。纸本索引终审覆盖 p.443–474 的32页，2,934个索引行均有对应候选或有理由的排除记录。范围登记和结构检查不能单独证明召回完整或事实准确。

## 当前产物与检查

| 产物 | 当前规模／状态 |
|---|---|
| [KU 登记](../tables/ku-manifest.csv) | 1,019 KU；既有成果，不是本轮全书 S4 已完成 |
| [实体候选](../tables/entity-candidates.csv) | 12,402 candidates |
| [提及账本](../tables/mentions.csv) | 26,616 mentions |
| [原书断言及关系候选](../tables/book-statements.jsonl) | 15,161 statements；relation_candidate true 10,399、false 4,762、unset 0 |
| [覆盖账本](../tables/s2-coverage.csv) | 832段全部完成登记与迁移 |
| [既有对齐](../tables/alignment.csv) | 335条：185 same、146 undecided、4 excluded；本轮全书 S3 尚未执行 |
| [既有字段表](../tables/enrichment.jsonl) | 10,149条，其中1,501条 unverified |
| [既有关系](../tables/relations.csv) | 1,227条：1,225 formal、2 pending；不等于已裁决本轮10,399条关系候选 |
| [候选待办](../tables/candidate-backlog.csv) | 1条 pending：Luigi Pavini，按 S1→S3→S4 处理直接端点 |

331条 S2 关系候选至少缺一个端点，分布于126个来源段：仅缺 object 217条、仅缺 subject 42条、两端均缺72条。331条均保留逐行理由，无缺理由开放端点；它们仍是 S2 候选，不是 S6 正式关系。具体身份、群组边界、版本与指代限定在对应 statement 的 qualifiers 中保留。

严格阶段表审计通过：`errors=[]`、`s2_missing=[]`；关系一致性审计硬错误为0。表格预检与既有批量渲染的完成依据见过程记录；结构一致性不代表独立语义验收，也不产生准确率、召回率或语义处理吞吐指标。

## 未解决项与交接限制

- S3 类型与身份尚待全局裁决。当前664个候选的 suggested_type 为空（621 open、43 excluded）；空类型不是已解决，也不强塞现有类型。身份比较问题按 `qualifiers.candidate_identity_questions` 及相应过程证据接续，不按名称直接合并。
- 331条开放候选继续保留缺证理由；原文未给出的匿名人物、作品组成员、日期、版本和关系目标不补猜。端点可登记、身份可确认及关系可成立分别判断。
- `enr-06678`、`enr-06937` 的 source_ref 无法从对应卡片来源列表解析，属于既有 S5 缺口；1,501条未核验字段不自动升级。身份或书目匹配也不表示读过原件或验证其全部事实。
- 原书异文、OCR 校读和印本标记问题按证据保留，包括 p.247 印号不可见、p.270 注7疑似错位、p.359 注4无标记且重复注3、p.377 正文标号6与页底注5错配。S2 校读没有改写来源本体。
- S2 为内部语义处理与自查，尚未形成独立语义验收或全书 precision/recall 估计；KU 的 confidence/consensus 也没有因机械检查而统一赋值。
- `release/v0.1/` 与 [v0.2-draft](../../release/v0.2-draft/README.md) 是既有快照。后者 metadata 创建日期为2026-09-26，仍含790段、686条提及、192条断言的旧包，不覆盖当前全书 S2，不是本次 S7 交付；作者信息按用户要求留空，公开权利、许可和最终引用尚未完成。

## 完成依据与接续

- [摄入与处理过程](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)：实际阅读、来源核对、判断变化与写回依据。
- [分段处理结果](../../03-processing/patrons-and-painters-full-book-s2/results/stages.md)：按源段保存的处理记录及章节结果入口。
- [历次结果与交接审查记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md#s2-result-history-20261015)：从本文件归位的历史批次、开放端点清单、指代及书目核对。旧计数和游标仅作历史证据，不再定义当前待办。

下一步依 [pipeline](../../.agents/pipeline.md) 执行 S3：以全书候选、提及、断言与既有 KU 为输入，逐对象记录 same/new/conflict/excluded/undecided 及身份依据。S3 的 new 决定可待 S4 登记；已有 KU 的复用和外部标识核对分别说明。S4 登记后再按明确缺口进入 S5，S6 逐候选裁决关系，S7 另行形成版本化数据包。知识发现与页面继续暂停，须用户明确启动。
