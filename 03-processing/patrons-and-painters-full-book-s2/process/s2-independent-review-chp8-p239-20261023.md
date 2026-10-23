# 第八章 p.239 S2 语义复核与端点处理

更新：2026-10-23。范围：第8章印刷页239（PDF物理页45）、正文 `chp-8:08_CHP-8_sec_ii:l338-348` 与注释段中本页注1、3、5（`chp-8:08_CHP-8_sec_ii:l372-461`）。逐条核读本页40条现有 statement，并对照 S0 转录及扫描页；p.238注1仅用于核对 p.239 注3 的 No.357 回指，不将 p.238其他内容并入本批。

## 逐页核读与修订

40条现有 statement 均按印刷页图和 S0 检查了 claim、引文跨度、主体／客体、语气、时间、限定及 relation-candidate 状态。原有状态为 `relation_candidate=true` 17条、`false` 23条、未分类0条。本批将 p.239注3 的 Zanotti 书目引注补定为书内 `cites` 候选，现为 `true` 18条、`false` 22条、未分类0条。该新增候选只记录 Haskell 的引书行为，不声称读过所引页。

保留 S0 和原始 quote，不用扫描校读覆盖来源转录。分别补记扫描校读：p.239 L341 `Crcspi’s humour` → `Crespi’s humour`；L341 `die support` → `the support`（既有校勘）；L342 `side ef his temperament` → `side of his temperament`（既有校勘）；注1 L449 `p. $4` → `p. 54`；注3 L450 `Archivio Medicco` → `Archivio Mediceo`、`No. 3 57` → `No. 357`；注5标题前扫描脚注号为5，S0转录为6（既有校勘）。日期范围“1716–1723”及“1716 Inventory”便利称呼继续由独立 statement 表达；将 `st-chp8-p239-note5-inventory-description` 的 claim 收窄为保管地点，修复其把保管、日期和便利标签混成一个 claim 的原子性问题。

在正文段补录 Crespi、Ferdinand 两个页内人物锚点；在注3补录 Ferdinand、No.357信件、档案定位、Zanotti作者和书目对象的精确跨度；在注5补录库存题名、所称保管机构及 S.P.F. 标记。其余候选—来源段差异不按 ID 自动扩增 mention；p.238复核记录中的候选—段落差异仍须逐项语义判断。

本页 S2 statement 总数未增，独立复核统一分子仍为9,573/15,254；本次语义核读及修订不计作全书接收，也不改变章节台账数字，待统一复核台账按当前 statement ID 与来源版本核平后再调整。

## S3、S4 与 S5

沿用 `cand-8032` 的既有 S3 `new` 身份组 `archive-group-86920fdc70d6`，将 `aln-8207` 登记为 `units/archives/ferdinand-letter-28-apr-1708-no-357`。身份限定为 Haskell 所指 No.357信件，不推断收信人、原件题名或现存保管地点；未重开 S3。

新卡按描述性题名登记3条 `source_backed` 字段（`enr-16362`–`enr-16364`）：来源所报日期、发信人及档案定位。`cand-1609` 的人物映射沿用既有 S3 `same` 决定。注5库存对象 `cand-8054` 与保管机构 `cand-8053` 未在本批登记；后者名称与已登记的 Soprintendenza 机构卡相近，需先核对跨章身份后再写回 S4。

## S6 逐候选裁决

两条候选均有清晰书内证据和已登记端点，且通过关系类型与域值域检查，裁为 formal：

| statement_id | 决定 | 关系与边界 |
|---|---|---|
| `st-chp8-p239-note3-zanotti-and-letter-357` | formal | `rel-1616 authored_by`：No.357信件 → Ferdinand；Haskell明确称为 Ferdinand 于1708-04-28所发的信。原件未查，未补收信人或内容。 |
| `st-chp8-p239-note3-zanotti-citation` | formal | `rel-1617 cites`：《赞助人与画家》→ Zanotti《Storia dell’Accademia Clementina》卷II，第52、54页；只记录书内引注，所引页未读。 |

注5库存—保管机构候选未裁决：机构身份仍需与现有 KU 比较，库存 `cand-8054` 的 S4 登记及相关 S6 `held_at` 关系后续处理；S.P.F. 标记候选仍保留现有未决身份，不据缩写造正式关系。
