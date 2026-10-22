# 第八章 p.237 S2 独立语义复核

更新：2026-10-22。状态：进行中。本记录仅覆盖第八章 p.237 的当前 statement ID，不接收全章，也不据此上调尚未核平的全书统一复核分子。

## 范围与方法

对照 `CHP-8.pdf` 物理页43页图、S0源文件 `08_CHP-8_sec_ii.md` 的 `chp-8:08_CHP-8_sec_ii:l311-325`（正文及页下注释）和 `l372-461`（注2–4连续文本，L439–442），逐条检查当前全部39条 `st-chp8-p237-*` statement 的 claim、原子性、端点、谓词、说话层、限定和页间/脚注回链，并核对相应mention与来源跨度。页图、迁移状态及既有 `reviewed/complete` 标记均不替代本次语义判断。页面末句“but he”续至 p.238 L328；本次不补写续句。

本次原38条中 `relation_candidate=true` 32条、`false` 6条、未分类0条。第八章结果文件旧游标“11条中3条未分类”与当前表不符，系历史快照；该数字不作为当前待办或复核计数。`s2-coverage.csv` 保持原迁移状态。

## 发现与修订

`st-chp8-p237-note2-massacre-commission-and-default` 将两个先后发生的事实合并：Don Carlo Silva 委托《无辜者屠杀》作为呈给 Ferdinand 的作品；画作完成后，Silva 违约并声明不再赠予。现保留原 ID 表达委托及预定呈递对象，新增 `st-chp8-p237-note2-silva-defaulted-on-massacre-gift` 单独表达其违约和撤回赠画意图。两条均将叙述归于 Haskell；引述的 Zanotti 与1948年展览目录没有独立核读。记录不声称赠画完成、所有权转移或实际交付。

其他37条原有 statement 的断言本身经逐项核读，未发现需修改的语义问题；其来源锚点、指代、Haskell评价与推测限定、档案书目定位和端点判断仍与页图及S0相符。另发现S2 mentions.csv漏记本页正文和注2中的人物与作品提及，已按精确字符跨度补入4条记录，未改变statement断言。Crespi和Ricci错过会面、作品风格比较、Ferdinand对Crespi作品的反应、两幅静物委托与Crespi职业变化保持为不同断言；1708年书信内容仍按Haskell转述处理。注2中的原委托、违约、赴Livorno及Ferdinand介入纠纷分开；注3对早年受雇可能性、《圣玛格丽特的狂喜》与Lanfranco画作关系保留原书限定。图版校读继续保留在S2 qualifiers，未改S0。

修订后 p.237 共有39条 statement：`relation_candidate=true` 33条、`false` 6条、未分类0条。新增一条关系候选使全书 statement 总数和 S6 候选分母各增加1；补入四条精确 mention：`m-chp8-p237-massacre-title-body`、`m-chp8-p237-silva-citation-n2`、`m-chp8-p237-massacre-title-note2`、`m-chp8-p237-don-carlo-silva-n2`，分别锚定印刷页237 L319、L322和注2 L440。全书S2统一复核仍按当前结果表记为9,573/15,198，未接收；第八章暂记487/1,463。由于第八章487/1,462统一口径与 `process/stages.md` 的1,462/1,462直接核读记录仍未按当前statement ID核平，本批不调整统一复核分子，也不将迁移覆盖等同于复核。

人物、作品身份组、S4登记及两条相关S6候选的决定见[跨阶段过程记录](knowledge.md#s3-s4-s5-s6-chp8-p237-silva-massacre-20261022)；本S2复核记录不替代全章接收。下一项关系端点复核沿既定游标为 `st-chp8-p238-note4-pictures-at-pisa-cabinet`。本记录不代表第八章或全书S2接收。
