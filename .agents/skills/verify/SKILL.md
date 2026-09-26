---
name: verify
kind: leaf
phase: current
triggers:
  - verify
  - 知识元对齐
  - 验证知识元
  - 冲突裁决
description: 负责 S3 身份对齐；产物 `alignment.csv`。**只做身份，不注入内容事实**；决定只有 same/new/conflict/excluded/undecided 五档，各带证据。
---

# verify

负责 S3 身份对齐；产物 `alignment.csv`。**只做身份，不注入内容事实**；决定只有 same/new/conflict/excluded/undecided 五档，各带证据。

## 输入与工作

读 S1 `entity-candidates.csv`、S2 `mentions.csv`/`book-statements.jsonl`，以及 `ku-manifest.csv` 中已有的 KU（用于跨任务、跨章判定 same）。S3 是身份对齐：比较名称、别名、身份、年代和作品/文献版本，识别明显重复与冲突；同名不等于同一对象。不以生平、作品清单等详细信息齐全作为进入补足的前提，详细内容由 S5 按证据完善（REV-026）。章内对齐可以依据原文完成，但不能代替外部身份验证。
存在原文关系候选时，核对原文提及到KU的端点映射并保留原词、歧义和候选锚点。外部记录可支持消歧和身份确认，但身份依据不自动支持候选谓词，也不能把外部名称或确定性倒填为原书表达。
按 REV-056，对齐使用与实体类型相符的身份链：比较原文锚点与专业数据库、国家或机构规范记录、馆藏／档案／书目记录中的名称、类型、年代、地点、责任者、版本和稳定标识。QID、Wikipedia页面、VIAF、ULAN、SBN标识、馆藏号、档号、DOI或数字化项目标识都只在该对象实际适用时采用；没有某一种全局标识不构成失败，也不为填标识借用相关对象的记录。

人物、家族和机构优先核对国家人物辞典、档案生产者记录、专业规范库及所属机构资料；意大利对象按需使用Treccani《意大利人传记辞典》、SIUSA、OPAC SBN／ICCU等。文献与档案优先核对保管机构目录、档案检索工具、OPAC SBN、EDIT16、Manus Online、VIAF及可核版本的数字化全文；Internet Archive等聚合数字库须先核版本、责任者、出版项或馆藏来源。其他类型的适用来源见按类型参考，不固定网站数量或顺序。

当对象存在准确的Wikipedia与Wikidata记录时，沿用以下核对：

1. 阅读实际Wikipedia条目和Wikidata实体内容，将身份特征与来源对象逐项比较，不能只看标题或搜索分数。
2. 核对候选QID的Wikipedia sitelink及页面的Wikidata item链接（或pageprops.wikibase_item）是否双向指向同一对象。英文页面优先；无准确英文条目时按原语与历史背景回退意大利语、德语等实际页面，不机械遍历语言。
3. 只有消歧义页、粒度不一致或身份冲突时，不确认该QID；这只表示该Wiki身份链不成立，不自动否定其他权威记录已经支持的实体身份。

在过程文件记录实际采用数据库、URL或记录标识、访问日期、对象比较、版本与结论；卡内展示可用的身份／书目／馆藏入口及当前状态。结果分开说明章内对齐、外部身份核对、书目或馆藏核对、全文阅读与具体事实验证。已有证据可复用，不要求每轮重复搜索。

外部事实补证须读能支持该问题的实际内容，记录来源独立性及支持范围。相互聚合、链接或转录的数据库不因域名不同就计为独立事实证据；身份通过不等于整篇KU已验证。书目记录只支持书目身份，数字化扫描只有在版本核对并实际阅读相应页后才支持正文事实。
仅遇真实冲突时比较两侧来源和语境，得出已解决、并列解释、暂缓或否决；身份无法确认时不合并。

## 产出与交接

03-processing/<task-id>/process/knowledge.md 记录比较和理由，04-knowledge/results/<task-id>.md 记录已对齐、待消歧、争议和实际修改。验证日期只记录真正发生的验证，对齐不等于发现层级归属。
可用对象及内容缺口交 enrich；关键身份不明的对象阻断相关关系/合并。无须补足对象记录理由后进入关系阶段，不额外走一次全面核验。

## 工具边界

常规语义判断在授权范围内完成并记录实际证据。现有 `verify_apply_evidence.py --dry-run` 仍可检查旧格式证据包；`--apply/--resume` 与 `evidence_batch_runner.py --apply-low-risk` 已暂停，因为旧接口写卡片 frontmatter，而字段证据已迁入 `enrichment.jsonl`。恢复批量写回前须实现以表为目标、保持来源和证据限定的写入器；不得将卡片旧状态与表状态分叉。此时填写 `source_independence_group`，防止转引被计为独立来源。
L1–L7 仅是该接口兼容代码，不是业务阶段或事实可信度的自动排名。数量、脚本分数不自动提高 confidence/consensus；失败和 no_delta 如实记录。
现有各类collector只收集候选，不能替代Agent对对象、版本和粒度的实际阅读与判断。Wikipedia/Wikidata collector也未自动完成双向QID核对；成功输出不能称为身份确认。

## 按需直接参考

- `.agents/skills/ingest/references/body-template.md`：身份链接、关系导航与阅读范围的卡内展示。
- `references/type-verification.md`：按对象类型选择身份特征与补证来源。
- `references/cascade.md`：来源选择与渠道代码含义。
- `references/no-data-and-browser-research.md`：失败、未命中或开放网页查证。
- `references/api-verification.md`：实际调用 API collector 时的证据格式。
- `references/result-handling.md`：需要改变验证状态或使用机器写回时。
- `.agents/skills/system-upgrade/references/work-package-contract.md`：仅批量机器写回或旧接口续接。

外部标识（QID、ULAN、VIAF、SBN、馆藏号等）只写入 `alignment.csv` 的 `external_source`/`external_id`，不写入 `enrichment.jsonl`。
