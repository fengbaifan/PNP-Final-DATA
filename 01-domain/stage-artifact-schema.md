# S0–S7 阶段产出字段规范（草案 v1）

> 状态：**草案，供审**。本文件定义各阶段产物字段、来源与放行约束；阶段实际数量、当前成果及未决项见 [pipeline](../.agents/pipeline.md) 和[第一章结果](../04-knowledge/results/patrons-and-painters-chp-1.md)。数据包机械检查与发布限制见[验证报告](../release/v0.2-draft/validation-report.md)。结构审计通过不证明语义召回率、准确率或独立验收。

## 已决事项（2026-09-25）

1. **关系域值域矩阵现在就建**：见 [relation-domain-range.yml](relation-domain-range.yml)，S6 放行时以 inverse 映射规范化后核对该矩阵。
2. **backlog 阈值 = 20**：同类型候选待办 ≥ 20 时提前批量 drain；关系阶段收口前硬性清空。
3. **关系表迁移目标**：`relations.csv` 是新渲染器的输入，卡片关系表从该表生成。frontmatter.relations 尚保留为迁移对照证据；只有完成单卡预览审阅与获准的批量写回后，才可将其退役。不得删除现存卡片关系数据。

## 0. 跨产物公约

**0.1 稳定 ID**
- `segment_id` = `{chapter}:{section}:l{line_start}-{line_end}`（印刷页另作字段，不塞进 ID）
- `ku_id` = `units/{type}/{slug}`，不带 `.md`。slug 一经发布就不再修改；改名、改类型或合并时，在 `id-redirects.csv` 中登记。
- 所有实体、候选、提及、断言、对齐、补足和关系记录均有稳定唯一 ID。现有格式包含 `cand-{N}`、`m-chp1-secii-{N}`、按对象/来源定位的 `st-{...}`、`aln-{N}`、`enr-{N}`、`rel-{N}`；后续新增 ID 不得与既有记录冲突，不重编号或复用。对同一张表串行写入。
- `index_entry_id` 单独成列，记录原书索引中的定位（`{index_file}#{row}`），只作为来源定位，不作主键，也不拼进 `candidate_id`。

自然键（写入前查重；命中即复用原 ID）：
- `entity-candidates.csv`：`index_entry_id`；非索引来源的候选用「规范名 + 类型」
- `mentions.csv`：`segment_id`、起始位置、结束位置
- `book-statements.jsonl`：`segment_id`、断言规范文本（claim/attribution；缺失时用原文引句）的规范化文本
- `alignment.csv`：`candidate_id`、`external_source`
- `enrichment.jsonl`：`ku_id`、`field`、`value`、`source_id`
- `relations.csv`：主语、谓词、宾语、qualifier（时间、版本）

重定向表 `id-redirects.csv`（在 `04-knowledge/tables/` 内），列为 `old_id,new_id,reason,date`。

**0.2 `origin` 与来源字段（逐事实标注）**

- `origin` ∈ {`book`, `external`, `inferred`}：
  - `book`：原书陈述；
  - `external`：外部来源的事实；
  - `inferred`：Agent 或整理者的解读或推断。
- `align` 不是 `origin` 的取值。身份映射只记录在 `alignment.csv` 的 `decision` 列。
- `source_id` 引用 `sources.csv`。当前表列为 `source_id,kind,label,version,accessed_date,citation,url`；`label` 与 `citation` 必填，无法确认的版本/日期/网址留空，不推断默认值。
- `cited_source`（可为空）：原书转引的档案或文献，用来区分「原书说的」和「原书引用某份档案说的」。
- 不发布标记：`segments.jsonl` 引用原书切片，`release_excluded: true`，S7 导出时排除源文全文。当前受限草案中的 `book-statements.jsonl` 保留 OCR 引文以便审查；公开发布前须按权利审查决定是否删除或取得授权。

**0.3 状态维度（三个维度相互独立，不跨表混用）**
- `evidence_status`：沿用现有 5 值 `unverified` / `source_backed` / `partially_verified` / `externally_verified` / `model_supported`，与 `scripts/_evidence_policy.py` 和 `claim-evidence-governance.md` 保持一致。当前 `enrichment.jsonl` 使用此字段；S2 断言与 S6 关系通过各自的原文/来源定位字段留证。
- `dispute` ∈ {`true`, `false`}：是否存在来源冲突，与证据强度分开记录。
- `decision` ∈ {`same`, `new`, `conflict`, `excluded`, `undecided`}：只用于 `alignment.csv`。
- `relation_status` ∈ {`formal`, `pending`, `rejected`}：只用于 `relations.csv`。
- 不另设 `confirmed`/`contested`/`uncertain` 这类枚举。

**0.4 v0.1 迁移映射（供第 5 步使用）**

| v0.1 现状 | 迁移规则 |
|---|---|
| enrichment.evidence_status = uncertain | 改为 unverified；有具体证据的按实际证据改为 source_backed 或 externally_verified |
| enrichment 中 field/value 为空、只有 QID | 移入 alignment.csv 的 external_id（external_source=Wikidata），从 enrichment 中删除 |
| enrichment 中 source、url、qid 全为空 | 丢弃，只把丢弃条数记入 validation-report.md |
| alignment.decision = paired | 改为 same，必须有 external_id |
| alignment.decision = unpaired | 按原记录区分：「范围不符/候选排除」改 excluded，其余改 undecided |
| alignment.candidate_id 填的是 KU 路径 | 按 entity-candidates.csv 的自然键回填 cand-{N}；匹配不到的，新建候选 |
| entity-candidates 中的 cand-0000 类旧 ID | 按新规则重新发号，并登记到 id-redirects.csv |
| origin = enrich | 改为 external |
| evidence_ref/review 中的 REV-xxx | 移入 process_ref 列，只供内部追溯，S7 导出时排除 |
| ku_id 带或不带 .md 不一致 | 统一为不带 .md |

**0.5 结构化 vs 散文分界（转换安全前提）**
- 目标：结构化事实 → CSV/JSONL 唯一权威，包括名称/别名、类型、日期、外部 ID、对齐决定、补足事实、关系和提及/断言定位。`relations.csv` 和 `enrichment.jsonl` 均驱动只读渲染预览；KU 登记仍与 `accepted.yml`、frontmatter 并行。预览可重建表格行，但批量写回尚未执行，旧卡片仍保留迁移对照证据。
- 散文 → 仍在 `units/*.md` 卡内人工维护：双语描述、「本章相关内容」、「原书转引评论」、原文引用。
- 卡片 = 结构化表由 CSV 渲染 + 散文段落原位；不追求「卡片 100% 由表生成」。

**0.6 关系域值域**：见 [relation-domain-range.yml](relation-domain-range.yml)。

---

## S0 来源规范化

| 文件 | 实际字段 | 必填与约束 |
|---|---|---|
| `sources.csv` | `source_id,kind,label,version,accessed_date,citation,url` | `source_id` 唯一；`kind` 为 `book` 或 `external`；`label`、`citation` 必填；无可靠信息的 version/date/url 留空 |
| `segments.jsonl` | `segment_id,source_id,chapter,section,source_file,line_start,line_end,sha256,asset_sha256,release_excluded` | `segment_id` 唯一；source FK；来源路径、正向物理行区间、两个哈希必填；`release_excluded` 显式标记 |

当前 1,684 个 source、953 个 segment。校验物理行覆盖、不重叠、哈希和来源 FK；source 版本/访问日期不以空值补造。

## S1 全书实体候选（原书索引为种子）

| 文件 | 列 | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `entity-candidates.csv` | `candidate_id` | string | ✅ | 主键 |
| | `index_entry_id` | string\|null | | 索引候选的回溯键 |
| | `canonical_name` | string | ✅ | 候选规范名 |
| | `sub_entry` / `detail` | string | | 保留索引子目及语境 |
| | `candidate_origin` | string | | 空值为索引候选；`accepted-ku` / `body-mention` 为其他来源 |
| | `candidate_source_ref` | string\|null | | 已接收 KU 路径或正文段与原始行定位 |
| | `aliases` | string | | 分号分隔 |
| | `suggested_type` | string\|null | | 已有类型时为九类之一；未判定候选可空 |
| | `index_page_range` | string\|null | | 索引页码；非索引候选为空 |
| | `index_source_file` | string\|null | | `A.csv`…；非索引候选为空 |
| | `status` | string | ✅ | `open`／`excluded` |
| | `exclude_reason` | string\|null | | `excluded` 必填 |

**放行条件**：索引每条 → 候选或 `excluded` 附理由；覆盖 = 100%。
**不重跑**：`03-2-Index-CSV/*.csv` + `List_of_Plates` + `Bibliography`（首次解析，不靠 Agent 从零识别）。

`candidate_id` 标识索引来源候选行，不自动代表唯一现实实体。相同主条目名可能对应多条带不同子目/页码的来源记录；须保留 `index_entry_id`，在 S2 结合原文语境判断提及，不按字符串相同自动合并或选定候选。

## S2 书内语义处理（逐章）

| 文件 | 列 | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| `s2-coverage.csv` | `chapter` | string | ✅ | 本次完整语义处理的章节范围 |
| | `segment_id` | string | ✅ | FK；每章的每个 S0 段恰一行 |
| | `disposition` | string | ✅ | `reviewed` / `excluded` |
| | `migration_status` | string | ✅ | `pending` / `partial` / `complete`；只表示对应提及／断言是否已写入表 |
| | `source_line_ranges` | string | | `reviewed` 段对应的原始 OCR 行范围 |
| | `note` | string | | `excluded` 必填理由；其他限定 |
| `mentions.csv` | `mention_id` | string | ✅ | 主键 |
| | `segment_id` | string | ✅ | FK |
| | `candidate_id` | string | ✅ | 提及→候选；无法定位候选的有名对象先登记 source-derived candidate |
| | `surface_form` | string | ✅ | 文中原形 |
| | `start_char` / `end_char` | integer | ✅ | 相对 S0 段文本的 Unicode 字符偏移，0 起始、左闭右开；原形须与切片完全相等；允许不同对象的严格嵌套提及（如文献名内的地名），拒绝完全重复或交叉重叠 |
| | `note` | string | | 消歧语境 |
| `book-statements.jsonl` | `statement_id` | string | ✅ | 主键 |
| | `segment_id` | string | ✅ | FK |
| | `subject_candidate_id` / `object_candidate_id` | string\|null | | 端点（可待决） |
| | `predicate` | string | ✅ | 关系或断言类型 |
| | `qualifiers` | object | ✅ | 转述/推测/否定/发言者/时间 |
| | `original_quote` | string | ✅ | 原句（仅内部，不发布） |
| | `source_file` | string | ✅ | 原始来源文件，相对项目根路径；引文须能在 `qualifiers.source_line_start/end` 指定行内复现 |
| | `origin` | string | ✅ | 恒 `book` |

**放行条件**：覆盖台账对每章 S0 段恰有一行；排除项有理由；每条提及与断言有锚点。覆盖台账证明段落处置范围，不替代逐段语义质量审查。
**不重跑**：已有章从 `results/stages.md` 抽取；新章直接读分节文件。

## S3 身份对齐（全局、按类型）

`alignment.csv` 实际列：`alignment_id,candidate_id,ku_id,external_source,external_id,decision,accessed_date,process_ref,legacy_ku_id,resolution_note`。

- `alignment_id` 唯一；`candidate_id` 必须指向候选；存在的 `ku_id` 必须在 manifest。
- `same` 必须有 KU、`external_source` 和 `external_id`；`new` 必须有 KU。
- `undecided`、`excluded`、`conflict` 必须有 `process_ref` 或 `resolution_note`。
- 自然键为 `candidate_id + external_source`；每个决定保留稳定对齐 ID。

当前 335 行：185 same、146 undecided、4 excluded，0 条无候选 ID。只有同一对象身份决定有依据时才记 same；数量完整不证明外部身份判断无误。

## S4 KU 登记

`ku-manifest.csv` 实际列：`ku_id,type,canonical_name,name_en,source_task,card_path`。

`ku_id` 唯一且稳定，type 属九类之一，中英文规范名和卡片路径必填；`source_task` 允许空值表示历史登记未留任务 ID。当前 1,019 个 KU。计数只按该表计算；不虚构文件中不存在的 created/updated 字段。

## S5 补足

`enrichment.jsonl` 每行对应一条结构化表格行，并保留可重建卡片的布局和证据单元格。当前使用字段包括：`enrichment_id,ku_id,field,value,origin,source_id,source_ids,source_ref,source_citations,source_urls,evidence,evidence_status,dispute,accessed_date,occurrence_id,table_id,table_section,has_header,table_header,row_index,cells,unit_evidence_status`。

- 自然键：`ku_id + field + value + source_id`；`enrichment_id`、`occurrence_id` 唯一。
- `source_ids`、来源文字/网址、表头和单元格均为数组；`source_backed` 必须有 source FK 与来源定位。`unverified` 明确表示未核验，不能因存在来源字符串自动升级。
- `origin` 可为 `book`、`external`、`inferred`；空值表示混合或尚不能确定来源类别，不猜填。`dispute` 为布尔值或 null。
- `(table_id,row_index)` 稳定且从 1 连续；卡片小节、表头及所有证据单元格均保留。

当前 10,149 行，1,501 行 `unverified`。这表示字段已登记，不表示事实准确率已验收。

## S6 关系

`relations.csv` 实际列：`relation_id,subject_ku_id,object_ku_id,predicate,time,role,scope,origin,status,source_id,source_span,source_file,note`。

- 自然键为主语、谓词、宾语与时间/角色/范围限定；ID 唯一，端点必须在 manifest，谓词按 [relation-domain-range.yml](relation-domain-range.yml) 校验。
- `origin` 实际值为 `book`、`external` 或历史显式值 `explicit`；`status` 为 `formal`、`pending`、`rejected`。
- `formal` 必须有来源定位（`source_file`、`source_span`）；填写的 `source_id` 必须在 sources 表。`pending` 必须保留来源定位及待决理由；无证据时不升级为 formal。

当前 1,227 行（1,225 formal、2 pending）。来源 URL 不能唯一映射到登记项时保留 URL 定位，不猜选 source ID。卡片关系预览按有向边生成正反向投影，派生反边不新增事实。

## S7 发布与验证

`export_dataset.py` 从当前 tables 生成 `release/v0.2-draft/`：实体、候选、对齐、来源、S2 覆盖、segments 元数据、mentions、book-statements、enrichment、relations、metadata、数据字典、README、验证报告和查询示例。源文全文不随包发布；当前包仍含带 OCR 引句的断言，须先完成权利判断。

现有包为内部审阅草案，未确定作者、许可、DOI/正式引用及第三方权利；不能称为公开可复用版本或数据集论文验收完成。机械 FK 和加载示例通过只证明包结构和读取路径可用；语义精度/召回、关系质量、处理速度对照及外部权利审查尚无实测结论。

## 依赖顺序

```
S0(来源) → S1(候选) → S2(提及/断言) → S3(对齐) → S4(KU) → S5(补足) → S6(关系) → S7(发布)
                                              ↑________ backlog drain（阈值 20）________|
```

## 校验与跟踪

- 已对既有 `relation-index.yml` 的 1,227 条边做只读校验：0 弃用类型在途、0 未知谓词、0 非法类型。
- `relation-domain-range.yml` 已修到 v1（domain/range 覆盖当前实际用法）。
- `located_at` 语义过载（person/institution/archive/work → place/institution），标 `needs_split`，拆分去向待定。
- 数据修正 1 条：`gianfranco-torcellan.md` 的 `authored_by` 方向反了，已改回（archive 卡持 `authored_by`→person，person 卡改反向投影）。
- `commissioned_by` 的 `place→person`（建筑/教堂/祭坛被委托人委托建造）为合法用法，矩阵 domain 含 `place`。
- S0–S7 已分步实施，当前仍是部分迁移状态；规则变更按 system-upgrade 维护 pipeline 与对应 Skill，不在本文件外另建副本。已有表的机械可用不代表各阶段语义验收完成。
