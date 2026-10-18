from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_s_index_endpoints_schut_segala_serlio_skala_20261018 as registrar  # noqa: E402

registrar.ANCHOR = "s4-anne-marie-shaftesbury-stanislas-talbot-person-endpoints-20261018"
registrar.PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    "s4-anne-marie-shaftesbury-stanislas-talbot-person-endpoints-20261018"
)
registrar.BATCH_TITLE = "Anne Marie、Shaftesbury、Stanislas与Talbot四组人物端点"
registrar.BATCH_PROCESS_NOTE = (
    "四组均为S3 new单候选人物身份组，登记4张KU卡、4条候选映射和8条source_backed姓名字段。"
    "Anne Marie de Savoye仅登记为收据签署人，不推定为卖方，并与Adelaide Enrichetta身份组保持分立；"
    "Shaftesbury仅以第一伯爵爵位称呼登记，不推补名字；Stanislas Poniatowski的第10章全名与第15章波兰国王称谓按同一索引组登记；"
    "Talbot的T.csv索引转写“Bruno”与正文“S2 Buno”并列保留，候选规范名继续依正文，不改写索引或候选表。"
    "本批6条S2关系候选留待S6；无formal relation或新增外部来源。"
)
registrar.BATCH_RESULT_NOTE = (
    "；六条S2关系候选保持待S6；Anne Marie只作收据署名者，Shaftesbury保留爵位称名，"
    "Talbot索引拼写Bruno与正文Buno并列保存；Stanislas相关未具名Warsaw views候选cand-9156仍待证。"
)
registrar.TARGETS = [
    {
        "candidate": "cand-2381",
        "group": "new-person:anne-marie-of-savoy-f98122919d",
        "ku": "units/persons/anne-marie-of-savoy",
        "card": "04-knowledge/units/persons/anne-marie-of-savoy.md",
        "name_zh": "安娜·玛丽·德·萨伏依",
        "name_en": "Anne Marie of Savoy",
        "index_entry": "S.csv#69",
        "index_name": "Savoy, Anne Marie of",
        "index_page": "341n",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/13_CHP-13_intro.md",
            "第13章引言脚注4，印刷页341，行226",
            "line 226; print p. 341 n. 4",
            "A receipt, dated 10 August 1736 in Vienna, signed Anne Marie de Savoye, refers to ‘un Poussin representant "
            "un Miracle des Apôtres; L’autre de Castiglione Benedetto avec des animaux et figures’ as well as fifteen gems "
            "and cameos as having been sold to Zanetti;",
            "Haskell脚注转述一份署名为Anne Marie de Savoye的收据；署名不证明她是卖方，收据原件未查阅。",
        ),
        "name_rows": [
            ("索引姓名", "Savoy, Anne Marie of", "S1，S.csv#69"),
            ("脚注姓名", "Anne Marie de Savoye", "S2，第13章引言，p.341 n.4，L226"),
        ],
        "relation_ids": ["st-chp13-p341-notes-note4-receipt-date-place-signatory"],
        "description_zh": (
            "本卡登记书后索引主条“Savoy, Anne Marie of”及第13章脚注所称的Anne Marie de Savoye。"
            "Haskell转述一份1736年在维也纳签署的收据；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index main entry “Savoy, Anne Marie of” and the Anne Marie de Savoye named in a Chapter 13 note. "
            "Haskell reports a receipt signed in Vienna in 1736. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "原文仅将Anne Marie de Savoye标为收据签署人；收据所述物品被售予Zanetti，不据此认定她是卖方。"
            "收据未独立查阅，唯一S2关系候选留待S6；本身份组与Adelaide Enrichetta of Savoy保持分立，不新增正式关系。"
        ),
        "context_en": (
            "The passage names Anne Marie de Savoye as the receipt’s signatory; it says the listed objects were sold to Zanetti, "
            "but does not identify her as the seller. The receipt was not independently consulted. The sole S2 relation candidate "
            "remains for S6; this identity group stays distinct from Adelaide Enrichetta of Savoy, and no formal relation is added."
        ),
    },
    {
        "candidate": "cand-2425",
        "group": "new-person:1st-of-shaftesbury-e97b949355",
        "ku": "units/persons/1st-earl-of-shaftesbury",
        "card": "04-knowledge/units/persons/1st-earl-of-shaftesbury.md",
        "name_zh": "沙夫茨伯里第一伯爵",
        "name_en": "1st Earl of Shaftesbury",
        "index_entry": "S.csv#113",
        "index_name": "Shaftesbury, 1st Earl of",
        "index_page": "196",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
            "第7章第IV节，印刷页196，行60",
            "line 60; print p. 196",
            "he had been required to figure the 1st Earl of Shaftesbury in the guise of Faction and then take advice from "
            "the 3rd Earl, his grandson, in depicting the Protestant virtues.",
            "Haskell称Verrio曾奉命把第一代Shaftesbury伯爵描绘为Faction，并向其孙、第三代伯爵征询新项目建议。",
        ),
        "name_rows": [
            ("索引姓名", "Shaftesbury, 1st Earl of", "S1，S.csv#113"),
            ("正文称号", "1st Earl of Shaftesbury", "S2，第7章第IV节，p.196，L60"),
        ],
        "relation_ids": ["st-chp7-p196-verrio_shaftesbury_roles"],
        "description_zh": (
            "本卡登记书后索引主条“Shaftesbury, 1st Earl of”及第7章所称的第一代Shaftesbury伯爵。"
            "原书此处仅用爵位称名；本卡不补推个人名。"
        ),
        "description_en": (
            "This card records the index main entry “Shaftesbury, 1st Earl of” and the first Earl of Shaftesbury named in Chapter 7. "
            "The passage uses the title only; this card does not infer a personal name."
        ),
        "context_zh": (
            "Haskell称Verrio曾将第一代伯爵画作Faction，后来又向第三代伯爵（其孙）征询表现新教美德的意见；"
            "壁画对象及建议所涉作品未具名，唯一S2关系候选留待S6，不新增正式关系。"
        ),
        "context_en": (
            "Haskell says Verrio portrayed the first Earl as Faction and later sought the third Earl’s advice on depicting Protestant virtues. "
            "The paintings and the work receiving that advice are unnamed. The sole S2 relation candidate remains for S6; no formal relation is added."
        ),
    },
    {
        "candidate": "cand-2505",
        "group": "new-person:new-of-poland-poniatowski-stanislas-of-pol-9c93ccb680",
        "ku": "units/persons/stanislas-poniatowski-king-of-poland",
        "card": "04-knowledge/units/persons/stanislas-poniatowski-king-of-poland.md",
        "name_zh": "斯坦尼斯拉斯·波尼亚托夫斯基",
        "name_en": "Stanislas Poniatowski, King of Poland",
        "index_entry": "S.csv#194",
        "index_name": "Stanislas Poniatowski, King of Poland",
        "index_page": "298, 366",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/10_CHP-10_intro.md",
                "第10章引言，印刷页298，行348",
                "line 348; print p. 298",
                "But while already on the journey he was persuaded to stop in Warsaw by the new King of Poland Stanislas Poniatowski",
                "Haskell称Bellotto在途中受新任波兰国王Stanislas Poniatowski劝说而停留Warsaw。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
                "第15章第II节，印刷页366，行21",
                "line 21; print p. 366",
                "the Kings of Poland and Sweden both subscribed",
                "Haskell仅以波兰国王称谓记录其参与Prà计划；依据索引与第10章全名记录为同一S3身份组。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Stanislas Poniatowski, King of Poland", "S1，S.csv#194"),
            ("正文全名", "Stanislas Poniatowski", "S2，第10章引言，p.298，L348"),
        ],
        "relation_ids": [
            "st-chp10-p298-bellotto-persuaded-to-warsaw",
            "st-chp10-p298-bellotto-warsaw-views",
            "st-chp15-p366-poland-sweden-subscriptions",
        ],
        "description_zh": (
            "本卡登记书后索引主条“Stanislas Poniatowski, King of Poland”及第10章具名的Stanislas Poniatowski。"
            "Haskell称他为新任波兰国王；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index main entry “Stanislas Poniatowski, King of Poland” and the Stanislas Poniatowski named in Chapter 10. "
            "Haskell identifies him as the new King of Poland. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "第10章称Bellotto在途中受其劝说而停留Warsaw，并为其绘制大量城市景观；第15章仅写波兰国王参加Prà计划，"
            "按同一索引页码与第10章全名归入本组。未具名Warsaw views候选cand-9156仍为S3 undecided。三个S2关系候选留待S6，"
            "不据此登记正式关系或作品KU。"
        ),
        "context_en": (
            "Chapter 10 says Bellotto was persuaded while travelling to stop in Warsaw and later produced many city views for Poniatowski; "
            "Chapter 15 refers only to the King of Poland subscribing to the Prà scheme, which is grouped with the named index entry. "
            "The unnamed Warsaw-views candidate cand-9156 remains S3 undecided. All three S2 relation candidates remain for S6; no formal "
            "relation or work KU is inferred."
        ),
    },
    {
        "candidate": "cand-2539",
        "candidate_name": "Talbot, Buno",
        "group": "new-person:buno-talbot-5fe8942fd7",
        "ku": "units/persons/buno-talbot",
        "card": "04-knowledge/units/persons/buno-talbot.md",
        "name_zh": "布诺·塔尔博特",
        "name_en": "Buno Talbot",
        "index_entry": "T.csv#2",
        "index_name": "Talbot, Bruno",
        "index_page": "197",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
            "第7章第IV节，印刷页197，行68",
            "line 68; print p. 197",
            "paintings, advised mainly by a dissolute priest called Buno Talbot.",
            "Haskell称Buno Talbot为神父，并称他主要为Isham购画提供建议；“dissolute”为Haskell原文评价。",
        ),
        "name_rows": [
            ("索引姓名", "Talbot, Bruno", "S1，T.csv#2"),
            ("正文姓名", "Buno Talbot", "S2，第7章第IV节，p.197，L68"),
        ],
        "relation_ids": ["st-chp7-p197-isham-acquired-paintings-with-advice"],
        "description_zh": (
            "本卡登记书后T索引的Talbot条目及正文具名的Buno Talbot。Haskell称他为神父，并称他曾为Sir Thomas Isham购画提供建议；"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the Talbot index entry and the Buno Talbot named in Chapter 7. Haskell identifies him as a priest and says he "
            "advised Sir Thomas Isham’s picture acquisitions. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "T.csv索引写作“Bruno”，正文写作“Buno”；沿用S3按正文确定的候选规范名，原样保留索引拼写差异。"
            "“dissolute”仅作为Haskell对神父的描述归因，不升级为独立人物事实。购画建议关系候选留待S6，不新增正式关系。"
        ),
        "context_en": (
            "The T.csv index reads “Bruno,” while the book text reads “Buno.” The card follows the S3 candidate name derived from the text and "
            "preserves the index spelling as a variant. “Dissolute” is retained only as Haskell’s description, not an independently established "
            "person fact. The acquisition-advice relation candidate remains for S6; no formal relation is added."
        ),
    },
]

if __name__ == "__main__":
    raise SystemExit(registrar.main())
