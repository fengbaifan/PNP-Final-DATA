# 第七章脚注段 S2 独立语义复核

更新：2026-10-21。状态：本段已独立复核并接收（31条statement、56条mention）；第七章整体仍未接收。

## 范围与方法

独立复核登记段 `chp-7:07_CHP-7_sec_iv:l97-119`，逐条核对当前 `book-statements.jsonl` 的31条 statement（印刷页193–199，PDF物理页31–37），并核对56条 mention span 与 S0 文本。其中30条 `relation_candidate=true`、1条 `false`、0条未分类。校读依据为对应 PDF 印本页。脚注所引作品、手稿及馆藏目录未因此视为独立查阅。

## 发现、修订与裁决去向

| Statement | 发现与当前去向 |
|---|---|
| `st-chp7-p195-n1-prince-taste-comment` | 当前记录已是 Haskell 的 `authorial_interpretation`，对象端点为空且 `relation_candidate=false`；保留“even in sacred pictures”限定，不连到 Wilhelm 或未识别作品。本次无改动。 |
| `st-chp7-p195-n1-wilhelm-citation` | 注1的 “ibid., pp. 89 and 92” 回指注4中的 Wilhelm 引文；当前书→文献引用、定位和同篇文章候选相符。此条在前次30条清单中漏列，现计入31条总数。 |
| `st-chp7-p194-n3-cite-von-freeden` | 原始 OCR 引文保留；已补印本校读 `8 Hantsch und Schers`→`3 Hantsch und Scherf`，并与同注的 Hantsch–Scherf 记录使用相同校读依据（PDF物理页32）。独立复核指出 claim 重复了完整书名；已精简为一次书名，并保留其与 Hantsch–Scherf 同注并列的语境。 |
| `st-chp7-p195-n3-da-canal` | 印本注3为 “especially pp. 71–3”；claim 已改为 pp.71–73。候选 `cand-6593` 在其他章节出现 p.69 的定位仍独立保留，不把其页码带入本注。 |
| `st-chp7-p196-n1-gennari-evidence` | 在保留手稿 `cand-7262` 为被引档案端点的同时，为 Whinney and Millar `cand-7066` p.182 与 Zanotti `cand-7115` vol.I pp.170–171 保留两条书目 `citations`；手稿定位 `MS B.344` 移至独立的顶层 `shelfmark`，馆藏机构 `cand-7263` 保留在顶层 `repository_candidate_id`。引文数组不再混入档案定位；独立审阅者已复核通过，所引材料仍未独立查阅。 |
| `st-chp7-p197-n4-isham-pictures-lamport`、`st-chp7-p197-n5-exeter-pictures-burghley` | S2 保留画作组位置陈述；S6 均裁为 `rejected`（仅否决图谱边）。当前人物→地点端点无法表达未识别的画作组，且不等于人物居住、拥有或当前馆藏。逐项理由见[关系裁决记录](knowledge.md#s6-chp7-collective-picture-location-notes-20261021)。 |

其余条目未发现需要改变事实方向、书目对象或来源限定的实质问题；56条 mention span 均与本登记段 S0 文本对应。原始 OCR 保留，必要读法以 `ocr_corrections` 记录。

## 接收与覆盖统计

改动项已由独立审阅者复核，Gennari 的两条书目 citation 与顶层 shelfmark／repository 分离清楚；S6 两条裁决和端点边界均通过。本段接收仅限 `chp-7:07_CHP-7_sec_iv:l97-119`，章节其他范围尚未完成，故第七章仍不接收。当前结果快照记录第七章1,009/1,239条；本记录先不增加汇总分子，待按 statement ID 去重后再归并至全书9,400/15,167统计。

该批之后的下一游标为 `chp-7:07_CHP-7_sec_v:l3-7`；页码标记段 `l1-1` 无 statement。后续接续记录见下节。

## 第七章 p.199 第V节当前ID独立语义复核

逐条核读登记段 `chp-7:07_CHP-7_sec_v:l3-7` 的14条 statement（印刷p.199、PDF物理页37），并对照S0及46条 mention span。12条 `relation_candidate=true`、2条 `false`、0条未分类；46条span均精确对应登记源段。p.199的“Roman art”原被误映到Rome地点候选 `cand-4490`；按同一“Roman art”艺术生产领域的跨章语义，改映到既有term候选 `cand-4631`（其来源已含第2章和第7章p.173），并把相应 statement 主语同步改为该term。两个明确的城市提及仍映到 `cand-4490`；Maratta、Trevisani两条mention中的旧待S3备注同步为当前 `same` 决定。S3既有 `new` 身份组决定不变，不新增候选或身份组。

本段14条按 statement ID 去重后计入全书独立复核：第七章1,023/1,239，全书9,414/15,167（62.1%）。接收范围仅限本登记段，第七章及全书仍未接收。下一游标为p.200 `chp-7:07_CHP-7_sec_v:l9-18`。
