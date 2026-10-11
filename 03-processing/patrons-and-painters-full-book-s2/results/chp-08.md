# 第八章全书 S2 当前结果

任务：`patrons-and-painters-full-book-s2`。状态：本章当前候选表面提示已逐条裁决；这不等于全书召回验收或S3交接完成。全书状态见[当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)，完整裁决与证据见[过程记录](../process/stages.md)。

## 当前处理

- 覆盖账本：56段`reviewed/complete`、5段`excluded/complete`，无queued或partial。
- 候选表面提示：写前111条中47条映射、64条不写；写后剩余59条与已裁决no-write残余一致。定位器只提示已登记词形，不证明未登记实体是否齐全。
- 本轮新增4个来源局部候选、47条mentions，为20条既有statement补齐候选提及链接；未新增statement、未改关系表或正式关系。
- 严格阶段审计：1,019 KU、11,471 candidates、27,215 mentions、12,255 statements；`s2_missing=[]`、`errors=[]`。两条既存enrichment source_ref警告仍在，见全书结果。

下一书序为第九章；当前定位器在46个reviewed段上提示91条，须逐项回到来源裁决。全书S2交接审计仍待完成。

## 第八章 p.211 联姻对象群组关系端点复核（2026-10-09）

对照印刷p.211页图及规范段`chp-8:08_CHP-8_sec_i:l84-96`，将原句“a series of ingenious marriage alliances with the best families”解释为具体联姻中的来源界定匿名家族群。新增无类型、status=open候选`cand-11559`和mention `m-chp8-p211-080`，字符跨度`[453,470)`；将statement `st-chp8-p211-del-rosso-marriage-alliances`的object连接到群组。未推断成员、数量、婚配对或日期；不新增KU或正式S6关系。写后全书11,537 candidates、27,470 mentions、12,644 statements；S2关系候选2,808条，2,785端点齐备、23条开放。严格阶段审计通过（`errors=[]`、`s2_missing=[]`）；全量同步闭合303 passed、2 subtests passed，9/9检查及结构契约130/130通过。全书S2交接仍在进行。详见[过程记录](../process/stages.md)及[全书当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。
