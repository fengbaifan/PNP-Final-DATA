---
name: verify
kind: leaf
phase: current
triggers:
  - verify
  - 知识元对齐
  - 验证知识元
  - 冲突裁决
description: 负责阶段 4 的身份与表述对齐，以及各阶段围绕明确问题的事实核验。
---

# verify

负责阶段 4 的身份与表述对齐，以及各阶段围绕明确问题的事实核验。

## 输入与工作

读 KU 成稿结果、相关来源与待核问题。阶段 4 是初步对齐：比较名称、别名、身份、年代和作品/文献版本，识别明显重复与冲突；同名不等于同一对象。不以生平、作品清单等详细信息齐全作为进入补足的前提，详细内容由阶段 5 按证据完善（REV-026）。章内对齐可以依据原文完成，但不能代替外部身份验证。
按 REV-017，每个实体均须尝试 Wikipedia 与 Wikidata 双重身份核对；对齐时完成，未完成项明确交补足，不重复已经有效的判断。

Wikipedia 查询先查英文对象页；未找到对应英文条目时，根据实体来源国家、原语及历史活动背景查询相关语言版本，如意大利语或德语（REV-028），不将现代国籍作为唯一判断，也不逐实体机械遍历所有语言。记录英文查询结果、回退理由与实际采用语言；英文页访问失败不等于不存在。回退页仍须与同一候选 QID 双向核对；补足读取该语言的实际全文，不用英文搜索摘要替代。

通过条件如下：

1. 阅读 Wikipedia 实际条目和 Wikidata 实体内容，将名称/别名、对象类型、年代、地点、作者或版本等身份特征与来源中的对象逐项比较，不能只看标题或搜索分数。
2. 核对候选 QID 的 Wikipedia sitelink，以及该 Wikipedia 页的 Wikidata item 链接（或 pageprops.wikibase_item），确认双向指向同一个 QID。记录实际语言版本、规范页面与重定向；若重定向扩大到人物、系列或其他上位对象，不能当作具体作品/文献的匹配。
3. 缺少一侧、只有消歧义页、粒度不一致或身份冲突时，记录“未找到／双重验证未完成／冲突待解”及理由。候选 QID 不写成已确认标识；保留有原文依据的 KU，不借用作者、保管机构或相关对象的 QID。
4. 在现有过程文件记录两侧 URL、QID、实际访问日期、身份比较和双向核对结论；结果区分章内对齐、双重身份验证与具体事实验证。已有证据可复用，不要求每轮重复搜索。

外部事实补证须读能支持该问题的实际内容，记录来源独立性及支持范围。Wikipedia 与 Wikidata 相互关联，不因来自两个站点就计为两份独立事实证据；身份通过不等于整篇 KU 已验证。Getty 及其他官方来源按对象和缺口选择，见 enrich 与按类型参考。
仅遇真实冲突时比较两侧来源和语境，得出已解决、并列解释、暂缓或否决；身份无法确认时不合并。

## 产出与交接

03-processing/<task-id>/process/knowledge.md 记录比较和理由，04-knowledge/results/<task-id>.md 记录已对齐、待消歧、争议和实际修改。验证日期只记录真正发生的验证，对齐不等于发现层级归属。
可用对象及内容缺口交 enrich；关键身份不明的对象阻断相关关系/合并。无须补足对象记录理由后进入关系阶段，不额外走一次全面核验。

## 工具边界

常规语义编辑在授权范围内原位更新并核对。使用现有验证状态批量接口时遵守 collect → evidence JSONL → Agent 判断 → verify_apply_evidence.py --dry-run → --apply；整批预检、原子写回，恢复核对输入指纹。此时填写 source_independence_group，防止转引被计为独立来源。
L1–L7 仅是该接口兼容代码，不是业务阶段或事实可信度的自动排名。数量、脚本分数不自动提高 confidence/consensus；失败和 no_delta 如实记录。
现有 Wikipedia/Wikidata collector 分别收集候选，尚未实现上述双向 QID 核对；其成功输出不能代替 Agent 的实际阅读与配对判断，也不能称为自动双重验证通过。

## 按需直接参考

- `references/type-verification.md`：按对象类型选择身份特征与补证来源。
- `references/cascade.md`：来源选择与渠道代码含义。
- `references/no-data-and-browser-research.md`：失败、未命中或开放网页查证。
- `references/api-verification.md`：实际调用 API collector 时的证据格式。
- `references/result-handling.md`：需要改变验证状态或使用机器写回时。
- `.agents/skills/system-upgrade/references/work-package-contract.md`：仅批量机器写回或旧接口续接。
