# 第七章全书 S2 当前结果

任务：`patrons-and-painters-full-book-s2`。第七章共55个规范段；当前覆盖账本显示47段reviewed/complete、8段excluded/complete，queued与partial均为0。当前覆盖状态以`04-knowledge/tables/s2-coverage.csv`为准，全书状态见`04-knowledge/results/patrons-and-painters-full-book-s2.md`，逐项判断及执行记录见同任务`process/stages.md`。

## 候选表面提示裁决（2026-10-08）

在47个已审段上复扫候选表面定位器，10,489个既有类型词形形成40条启发式提示。逐项核对S0原文、候选、mentions及statement后，17条映射为精确mention，23条因泛称、普通语义或索引候选错配不写入。新增候选3个：cand-11486为Cardinal Aldobrandini所藏两件Titian作品相关收藏（类型待定）；cand-11487为Charles Le Brun提供给Domenico Guidi凡尔赛雕塑组的设计图稿（work）；cand-11488为Cardinal Chigi 1664年访巴黎事件（event）。三者的身份或具体范围按原文证据保留未决。

更新11条statement的`mentioned_candidate_ids`；另将Shaftesbury“English patronage”statement对象从England地理候选修正为cand-0969术语候选。未改关系表或未决关系端点。第七章p.180注4没有给出两件Poussin作品与Louvre、Detroit两馆的逐件配对，继续保留开放判断。

受控脚本`process/chp7_candidate_surface_prompt_reconciliation.py`默认dry-run，按输入哈希、提示分区、原文跨度、候选外键、mention重叠与statement前态校验后再写入；写后重扫的23条提示与no-write清单完全一致。恢复副本位于`%TEMP%\pnp-s2-chp7-surface-prompts-20261008-090555\`。完整跨度、逐条no-write理由、plan/script哈希和表哈希见`process/stages.md`。

`python -X utf8 scripts/audit_tables.py --strict-stage`通过：全库1,019 KU、11,467 candidates、27,168 mentions、12,255 statements；`s2_missing=[]`、`errors=[]`，覆盖678 reviewed/complete、154有理由排除、0 queued、0 partial。两条既存enrichment `source_ref`警告未变。候选表面提示只用于定位审查，不证明召回率或语义质量。下一步按书序处理第八章：56个reviewed段上当前有112条提示。
