# 第九章全书 S2 当前结果

更新日期：2026-10-14。任务：`patrons-and-painters-full-book-s2`。本章语义处理继续中，尚未交接S3；全书状态见[当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)，逐项来源判断见[过程记录](../process/stages.md)。

## 当前语义进度

- 本章coverage共53段：46段reviewed/complete、7段excluded/complete。此为机械登记，不代表statement语义全部完成。
- 本章目前886条statement：461条`relation_candidate=true`、87条false、338条unset。按S0源序，首个未分类段为p.254 `chp-9:09_CHP-9_intro:l134-146`，25条中7条待裁决。
- p.247–251五段已复核74条既有statement并新增49条；各段最终为30、16、15、28、34条，均无unset。恢复并核对280条页内mention，另补8条脚注mention。
- p.252正文复核20条既有statement并新增15条，写后35条（28 true、7 false）；恢复61条正文mention及45条p.252脚注mention。p.253正文复核14条既有statement并新增13条，写后27条（14 true、13 false）；恢复46条正文mention及22条本页脚注mention。
- p.252修正Tiepolo风格/战争语境与作者历史判断的端点和断言边界、Daniele III遗嘱主语、Dionisio任职/迁居/居住/建馆、Bambini壁画作者与地点等；不明房间不再映射为Udine图书馆。p.253拆开三组宫殿作品及其空间位置，保留匿名Resident引文、未具名委员会人和“a Daniele Dolfin”的身份不确定性。`cand-8275`名称收窄为未识别天顶壁画中的题材群。

全库严格阶段审计`errors=[]`、`s2_missing=[]`，关系一致性硬错误为0；`tests/test_audit_tables.py`十二项通过。既存两条enrichment `source_ref`警告及语义复核提示见全书结果；机械检查不构成S2整体验收。

## 候选表面提示复核记录

此前对候选表面提示写前91条：44条映射、47条不写；写后剩余45条与已裁决不写集合扣除两个嵌套提示后的残余一致。该定位器只匹配已有候选标签，不证明未登记实体是否齐全，仍须逐段核对原文。
