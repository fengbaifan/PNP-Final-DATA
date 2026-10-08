# 第八章全书 S2 当前结果

任务：`patrons-and-painters-full-book-s2`。状态：本章当前候选表面提示已逐条裁决；这不等于全书召回验收或S3交接完成。全书状态见[当前结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)，完整裁决与证据见[过程记录](../process/stages.md)。

## 当前处理

- 覆盖账本：56段`reviewed/complete`、5段`excluded/complete`，无queued或partial。
- 候选表面提示：写前111条中47条映射、64条不写；写后剩余59条与已裁决no-write残余一致。定位器只提示已登记词形，不证明未登记实体是否齐全。
- 本轮新增4个来源局部候选、47条mentions，为20条既有statement补齐候选提及链接；未新增statement、未改关系表或正式关系。
- 严格阶段审计：1,019 KU、11,471 candidates、27,215 mentions、12,255 statements；`s2_missing=[]`、`errors=[]`。两条既存enrichment source_ref警告仍在，见全书结果。

下一书序为第九章；当前定位器在46个reviewed段上提示91条，须逐项回到来源裁决。全书S2交接审计仍待完成。
