# 第二版后记当前结果

更新日期：2026-10-08。第二版后记正文与注释已完成S2语义处理；20个reviewed/complete段的候选表面提示复核也已完成。全书当前状态见[全书S2结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)，来源阅读与页图校读见[阶段结果索引](stages.md)，逐项候选裁决见[过程记录](../process/stages.md)。

## 候选表面提示复核

定位器给出24条提示。逐项回看原文、语境、候选子项及既有记录后，4条写入、20条不写。新增cand-11517（未量化的Francesco Algarotti肖像组，Haskell转述Santifaller的判断）及cand-11518（类型未定的Girolamo Manfrin分散艺术收藏）；另复用cand-9622（Schulenburg图片收藏）。新增4条mentions，并修订4条既有statement的候选关系。Manfrin收藏中曾有Giorgione的Tempesta，但收藏与人物、单件作品保持区分；来源未给出完整清单、边界或取得年代，不据此补造成员或所有权转移。

20条不写提示均有上下文理由：普通词义和无界类别不建候选；索引子项与当前词义不匹配时不建立mention；已有的Bernini赞助关系不重复登记。写后扫描剩余的20条提示与no-write裁决逐项一致。候选提示是复核线索，不证明实体召回完整。

严格阶段审计通过：1,019 KU、11,497 candidates、27,395 mentions、12,263 statements；832段中678 complete、154有理由排除、0 queued/partial，`s2_missing=[]`、`errors=[]`。全书交接审计仍进行中；6条端点未齐关系候选保留待证，两个既存enrichment `source_ref`警告未变，尚未进入S3。
