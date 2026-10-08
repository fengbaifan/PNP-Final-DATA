# 《赞助人与画家》全书语义处理（S2）当前结果

更新日期：2026-10-08。任务ID：`patrons-and-painters-full-book-s2`。**状态：S2交接审计进行中，尚未进入S3。**本页只记录当前范围、数据、未决项和下一步；历史逐项裁决见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)、[阶段结果索引](../../03-processing/patrons-and-painters-full-book-s2/results/stages.md)及各章结果。

## 范围与覆盖

S0登记79个规范来源文件、832段，涵盖书前材料、第1–17章、结论、附录、第二版后记、书目和索引；42段为派生视觉转录。第十一、十二章与第十章同版扫描产生的44段重复OCR已排除。书目按出版记录和引文定位处理，索引按候选定位材料处理，不作为正文断言。

| 当前S2覆盖状态 | 段数 |
|---|---:|
| reviewed / complete | 678 |
| 有理由排除 / complete | 154 |
| queued / partial | 0 |
| 合计 | 832 |

所有纳入处理的正文、注释、图版说明及书前/书后材料均已有S2处理记录。书目段已处理至L3–1306。纸本索引范围终审已完成：`CHP-22Index.pdf`共32页（p.443–474），规范索引94段均有coverage且迁移完成；19份Markdown与CSV的2,934行集合一致，2,934个CSV行号均有唯一候选索引ID并纳入逐页/栏映射。此前p.446发现并回补的四条为本次确认的纸本漏录；未发现其他未登记纸本词条。另将p.454印本“Fetti, Domenico”与F.csv#48的“Feti, Domenico”差异核清，cand-1033显示名已按印本校正，源文件未改写。p.460和p.462页码在页图中存在，PDF文本层漏识。全库脚注续页、正文回链和statement引用已专项检查：第七章p.186注1、第十三章p.333–334注1及第九章p.264–265注8的正文范围、目标注文页和正反链接已核正；嵌套脚注/续注pending键及打印页错配均为0。p.247印号不可见、p.270注7疑似错位、p.359注4无标记且重复注3等印本异常按证据保留，不强行回链。

## 当前数据与机械检查

当前表包含1,019个KU、11,497个候选、27,395条mentions及12,263条statement；索引候选2,934行。`python -X utf8 scripts/audit_tables.py --strict-stage`通过，`s2_missing=[]`、`errors=[]`；两条既存第1章statement缺少的claim已补齐。关系候选2,331条，2,325条端点齐全，6条仍开放且保留待证。全库`footnote_pending`、`footnote_text_pending`及statement失效引用均为0。同步闭合检查已通过：301 passed、2 subtests passed。

仍有两条既存enrichment `source_ref`警告：`enr-06678`、`enr-06937`无法从对应卡片source清单解析。机械检查不等于语义准确或实体召回完整；目前没有独立外部语义验收。

## 候选表面复核与当前游标

书前材料及第1–10章、第13–18章的候选表面提示已逐项裁决；第十一、十二章与第十章共用规范来源。第十六章7个reviewed段的11条提示中6条映射、5条不写；新增cand-11500至cand-11502、6条mentions和1条statement，另修订既有statement的候选关联与subject、更新cand-10598 detail。写后定位器剩余5条，与已裁决的不写项一致。逐项记录见[第十六章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-16.md)。

第十七章10个reviewed段的8条提示已逐项裁决；新增cand-11503至cand-11508、9条mentions，修正Joseph mention的候选映射，并更新竞赛题材statement。定位器剩余3条均为已裁决的不写项。第十八章2个reviewed段的2条提示也已核实为普通词义/候选错配，无表修改。第十九章12个reviewed段的17条提示已完成语义裁决：新增cand-11509至cand-11516及20条mentions，修正或扩展7条既有mention、核正statement候选关联；唯一残余提示`subject`为一般词义，明确不映射。第二版后记20个reviewed段的24条提示也已完成；新增2个候选和4条mentions，修订4条statements，写后剩余20条均与有依据的no-write裁决一致。详见[第十七章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-17.md)、[第十八章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-18.md)、[第十九章结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-19.md)及[第二版后记结果](../../03-processing/patrons-and-painters-full-book-s2/results/chp-20.md)。

全书候选表面提示复核已推进至第二版后记并完成；定位器剩余的20条均为已逐项裁决的不写项。定位器只匹配已有候选词形，不证明实体召回完整，也不替代全书S2交接审计。

## 全书S2交接审计与下一步

交接前还需按证据边界完成最后汇总：来源范围与排除项依据、候选外键和覆盖的机械核对已通过；脚注印号、续页、正文回链及statement引用专项复核已完成，递归pending扫描为0。剩余工作是全书语义指代与statement限定语的最后审视、六条端点未齐关系候选的逐项交接说明，以及汇总全部S2遗留风险并形成S3输入。六条关系候选继续开放，不转为无证正式关系；目前尚不进入S3。

S2交接前不推进S3–S6、知识发现或页面工作。
