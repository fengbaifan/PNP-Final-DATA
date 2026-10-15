# 第二版后记当前结果

更新日期：2026-10-15。第二版后记正文与注释已完成S2语义处理；20个reviewed/complete段的候选表面提示复核也已完成。当前统计与全书交接状态见[全书S2结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)，来源阅读与页图校读见[阶段结果索引](stages.md)，逐项候选裁决见[过程记录](../process/stages.md)。

## 候选表面提示复核

定位器给出24条提示。逐项回看原文、语境、候选子项及既有记录后，4条写入、20条不写。新增cand-11517（未量化的Francesco Algarotti肖像组，Haskell转述Santifaller的判断）及cand-11518（类型未定的Girolamo Manfrin分散艺术收藏）；另复用cand-9622（Schulenburg图片收藏）。新增4条mentions，并修订4条既有statement的候选关系。Manfrin收藏中曾有Giorgione的Tempesta，但收藏与人物、单件作品保持区分；来源未给出完整清单、边界或取得年代，不据此补造成员或所有权转移。

20条不写提示均有上下文理由：普通词义和无界类别不建候选；索引子项与当前词义不匹配时不建立mention；已有的Bernini赞助关系不重复登记。写后扫描剩余的20条提示与no-write裁决逐项一致。候选提示是复核线索，不证明实体召回完整。

当前严格阶段审计通过：1,019 KU、12,239 candidates、25,964 mentions、15,109 statements；全库relation_candidate=true 10,373、false 4,736、unset 0。当前15,109条statement间引用8,439条、缺失目标0；原书引文锚点15,040条逐字匹配、69条空白归一化匹配、缺失0。S2全书交接仍待开放端点与未决指代的语义复核。errors=[]、s2_missing=[]；enr-06678、enr-06937两条既存source_ref警告未变。尚未进入S3。
## 后记p.408–410关系候选裁决（2026-10-15）

p.408–410最后13条statement的`relation_candidate`状态已补齐：10条关系候选、3条非关系陈述。p.409修正“the same artist”提及指向Schmidt，并增加对其Salimbeni蚀刻作品的精确mention；`st-chp20-p409-schmidt-salimbeni-etching`现以作品为主语、创作者为对象。开放群体、封套对象、Vivarini身份及未独立查阅的学术论著继续保留来源限定，未写入S6正式关系。全库统计与剩余交接核查见[全书S2结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。

## p.403与p.408开放关系端点复核（2026-10-15）

p.403的Franceschini画作委托statement继续开放：Haskell写明Colbert与Abate Luigi Strozzi为经手人，但未指名委托者；不以邻近的Louis XIV叙述补端点。p.408原复合statement拆为Venturi与Torcellan分别受到威尼斯启蒙研究关注、Venturi关注Lodoli意义三条关系候选；Torcellan二十八岁去世后“本书会更完善”另存为反事实非关系陈述。论文引用仍标为未独立查阅，未新建正式关系。
