from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_s_index_endpoints_schut_segala_serlio_skala_20261018 as registrar  # noqa: E402

registrar.ANCHOR = "s4-adelaide-worsley-vittrice-visconti-person-endpoints-20261018"
registrar.PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    "s4-adelaide-worsley-vittrice-visconti-person-endpoints-20261018"
)
registrar.BATCH_TITLE = "Adelaide Enrichetta、Worsley、Vittrice、Visconti四个直接关系人物组"
registrar.BATCH_PROCESS_NOTE = (
    "四组均为S3 new单候选人物身份组，登记4张KU卡、4条候选映射、9条source_backed姓名字段和1条source_backed作品字段。"
    "Adelaide Enrichetta与仅有公爵称号的cand-2383及Anne Marie de Savoye候选cand-2381保持分立；"
    "Wittelsbach联盟陈述的家族端点cand-7157已由既有S3决定映射至House of Savoy，关系仍待S6；"
    "Worsley索引与正文称名按同一书内身份记录。Vittrice所涉《基督下葬》复用既有work KU，"
    "未具名家庭礼拜堂不新建KU，委托语境保留原文未澄清限定。Visconti脚注所引Bertolotti未独立查阅，"
    "被盗的十一幅画无题名；cand-11910仍按S3 undecided保留。本批不新增外部来源、正式关系或backlog项目。"
)
registrar.BATCH_RESULT_NOTE = (
    "。十条S2关系候选继续待S6；Adelaide与其他Savoy称谓候选不合并，"
    "Vittrice的《基督下葬》链接既有work KU且保留未具名礼拜堂与委托未明限定，"
    "Visconti被盗画作对象cand-11910继续待证。"
)
registrar.TARGETS = [
    {
        "candidate": "cand-2380",
        "group": "new-person:adelaide-enrichetta-of-savoy-0950f861b1",
        "ku": "units/persons/adelaide-enrichetta-of-savoy",
        "card": "04-knowledge/units/persons/adelaide-enrichetta-of-savoy.md",
        "name_zh": "阿德莱德·恩里凯塔·德·萨伏依",
        "name_en": "Adelaide Enrichetta of Savoy",
        "index_entry": "S.csv#68",
        "index_name": "Savoy, Adelaide Enrichetta of",
        "index_page": "193n",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
                "第7章，印刷页193，行14–15",
                "lines 14–15; print p. 193",
                "and when, in 1652, the Elector Ferdinand Maria married\n"
                "Adelaide Enrichetta of Savoy they found themselves allied to the most astute ruling family in Europe.",
                "Haskell称Elector Ferdinand Maria于1652年与Adelaide Enrichetta of Savoy成婚；此处仅登记书内具名身份和婚姻叙述。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
                "第7章，印刷页193，行15",
                "line 15; print p. 193",
                "But Adelaide Enrichetta was also a keen lover of art and surrounded herself with a number of painters and architects from Italy. "
                "She failed in her attempt to attract Guarino Guarini,",
                "Haskell称Adelaide Enrichetta热爱艺术、周围有来自意大利的画家和建筑师，并称她未能吸引Guarino Guarini。",
            ),
        ],
        "name_rows": [
            ("索引主条姓名", "Savoy, Adelaide Enrichetta of", "S1，S.csv#68"),
            ("正文全名", "Adelaide Enrichetta of Savoy", "S2，第7章，p.193，L14–15"),
            ("正文简称", "Adelaide Enrichetta", "S2，第7章，p.193，L15"),
        ],
        "relation_ids": [
            "st-chp7-p193-wittelsbach-alliance",
            "st-chp7-p193-adelaide-fails-to-attract-guarini",
            "st-chp7-p193-adelaide-surrounds-artists",
            "st-chp7-p193-ferdinand-maria-marriage",
        ],
        "description_zh": (
            "本卡登记书后索引作“Savoy, Adelaide Enrichetta of”、第7章具名的Adelaide Enrichetta of Savoy。"
            "Haskell称她1652年与选侯Ferdinand Maria成婚，并写她热爱艺术、身边聚集来自意大利的画家和建筑师，"
            "也未能吸引Guarino Guarini。中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Adelaide Enrichetta of Savoy, indexed as “Savoy, Adelaide Enrichetta of” and named in Chapter 7. "
            "Haskell says she married Elector Ferdinand Maria in 1652 and describes her as a keen lover of art, surrounded by "
            "painters and architects from Italy; he also says she failed to attract Guarino Guarini. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "第7章还称Wittelsbach家族因婚姻与一支“most astute ruling family”结盟；该家族端点按现有S3决定映射至House of Savoy。"
            "此项及婚姻、艺术活动语境、未能吸引Guarini等S2关系候选均保留Haskell归因，待S6逐条裁决。"
        ),
        "context_en": (
            "Chapter 7 also says the Wittelsbachs became allied through the marriage to a “most astute ruling family”; "
            "the family endpoint is mapped to the House of Savoy under the existing S3 decision. "
            "This and the marriage, artistic context, and Guarini candidates retain Haskell's attribution and remain for S6 review."
        ),
    },
    {
        "candidate": "cand-2819",
        "group": "new-person:richard-worsley-15b37d86ea",
        "ku": "units/persons/sir-richard-worsley",
        "card": "04-knowledge/units/persons/sir-richard-worsley.md",
        "name_zh": "理查德·沃斯利",
        "name_en": "Sir Richard Worsley",
        "index_entry": "UVWXYZ.csv#156",
        "index_name": "Worsley, Sir Richard",
        "index_page": "375",
        "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/16_CHP-16_intro.md",
                "第16章，印刷页375，行26–27",
                "lines 26–27; print p. 375",
                "Strange left, but he provided a letter of introduction to Sasso for his successor, Sir\n"
                "Richard Worsley: ‘He is a great lover and a great connoisseur of all beautiful things. "
                "He already has fine treasures and I know that you will be able to find more for him.’2",
                "Haskell称Strange离开时给Sasso一封介绍其继任者Sir Richard Worsley的信，并转引信中对Sasso的评价。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/16_CHP-16_intro.md",
                "第16章，印刷页375，行27–28",
                "lines 27–28; print p. 375",
                "Sasso did; and quite soon Sir Richard Worsley was himself presenting a Guardi to Lady\nPalmerston.",
                "Haskell称Sasso为Worsley找到更多作品，随后Worsley向Lady Palmerston赠送一件Guardi作品；书中未给出作品题名。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Worsley, Sir Richard", "S1，UVWXYZ.csv#156"),
            ("正文姓名", "Sir Richard Worsley", "S2，第16章，p.375，L26–28"),
        ],
        "relation_ids": [
            "st-chp16-p375-strange-introduces-worsley-to-sasso",
            "st-chp16-p375-sasso-finds-works-for-worsley",
        ],
        "description_zh": (
            "本卡登记书后索引作“Worsley, Sir Richard”、第16章称为Sir Richard Worsley的人物。"
            "Haskell称Strange将其继任者身份介绍给Sasso；随后Sasso为其寻得作品，Worsley不久向Lady Palmerston赠送一件Guardi作品。"
            "本卡仅记录第16章叙述；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Sir Richard Worsley, indexed as “Worsley, Sir Richard” and named in Chapter 16. "
            "Haskell says Strange introduced his successor to Sasso; Sasso later found works for Worsley, who soon presented a Guardi "
            "to Lady Palmerston. This card is limited to the Chapter 16 account. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "介绍信及其后Sasso寻购、Worsley赠画的内容均为Haskell书内叙述；S2关系候选继续待S6，不将未具题名的Guardi作品另行消歧。"
        ),
        "context_en": (
            "The introduction and the later purchase and gift account are Haskell's reports. The S2 relation candidates remain for S6; "
            "the untitled Guardi work is not separately identified here."
        ),
    },
    {
        "candidate": "cand-2787",
        "group": "new-person:alessandro-vittrice-25d1b90bf9",
        "ku": "units/persons/alessandro-vittrice",
        "card": "04-knowledge/units/persons/alessandro-vittrice.md",
        "name_zh": "亚历山德罗·维特里切",
        "name_en": "Alessandro Vittrice",
        "index_entry": "UVWXYZ.csv#123",
        "index_name": "Vittrice, Alessandro",
        "index_page": "70",
        "source_file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "第3章第II节，印刷页70，行56–57",
                "lines 56–57; print p. 70",
                "Alessandro Vittrice, who in about 1601 commissioned a picture from Caravaggio of The Entombment os\n"
                "Christ for his family chapel, was the nephew of one of St Philip’s closest friends, and it is therefore possible that the Oratorians welcomed the picture.",
                "Haskell称Vittrice约1601年委托Caravaggio为其家庭礼拜堂作画，并称他是圣菲利普·内里一位密友的侄子；正文OCR的作品题名拼写保留原样。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "第3章第II节，印刷页70，行57",
                "line 57; print p. 70",
                "the circumstances of the commission have not yet been clarified.",
                "Haskell明确保留委托情况未澄清的限定。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Vittrice, Alessandro", "S1，UVWXYZ.csv#123"),
            ("正文姓名", "Alessandro Vittrice", "S2，第3章第II节，p.70，L56–57"),
        ],
        "relation_ids": [
            "st-chp3-secii-l54-60-vittrice-commissioned-entombment",
            "st-chp3-secii-l54-60-vittrice-nephew-of-philip-friend",
        ],
        "additional_field_rows": 1,
        "description_zh": (
            "本卡登记书后索引作“Vittrice, Alessandro”、第3章具名的Alessandro Vittrice。"
            "Haskell在论述耶稣会教堂装饰时提及他，并称他是圣菲利普·内里一位密友的侄子；该亲属未具名。"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Alessandro Vittrice, indexed as “Vittrice, Alessandro” and named in Chapter 3. "
            "Haskell mentions him in discussing the decoration of a Jesuit church and says he was the nephew of one of St Philip Neri's "
            "close friends; that relative is unnamed. The Chinese display name is a project working transliteration."
        ),
        "type_sections": (
            "### 作品\n\n"
            "| 字段 | 值 | 证据 |\n"
            "|---|---|---|\n"
            "| [《基督下葬》（The Entombment of Christ）](../works/caravaggio-entombment-christ.md) | "
            "Haskell称Vittrice约1601年委托Caravaggio作画，并说明委托情况尚未澄清。 | "
            "S2，第3章第II节，p.70，L56–57 |"
        ),
        "context_zh": (
            "本书将委托时间写作约1601年，并指出委托情况尚未澄清；家庭礼拜堂及与圣菲利普·内里相关的亲属均未具名，"
            "两条S2关系候选留待S6，不新增正式关系。"
        ),
        "context_en": (
            "The book dates the commission to about 1601 and says its circumstances remain unclear. "
            "Neither the family chapel nor the relative connected to St Philip Neri is named. Both S2 relation candidates remain for S6, "
            "and no formal relation is added."
        ),
    },
    {
        "candidate": "cand-2781",
        "group": "new-person:antonio-maria-visconti-0f913a4080",
        "ku": "units/persons/antonio-maria-visconti",
        "card": "04-knowledge/units/persons/antonio-maria-visconti.md",
        "name_zh": "安东尼奥·马里亚·维斯孔蒂",
        "name_en": "Antonio Maria Visconti",
        "index_entry": "UVWXYZ.csv#117",
        "index_name": "Visconti, Antonio Maria",
        "index_page": "121n",
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/05_CHP-5_sec_i.md",
            "第5章第I节脚注7，印刷页121",
            "line 131; print p. 121 n. 7",
            "So too was Antonio Maria Visconti, whose shop was near the Albergo del Moretto and who in 1699 denounced the theft of eleven pictures— ibid., p. 199.",
            "Haskell脚注称Visconti的店铺邻近Albergo del Moretto，并称他于1699年报告十一幅画失窃；该注引用Bertolotti。",
        ),
        "name_rows": [
            ("索引姓名", "Visconti, Antonio Maria", "S1，UVWXYZ.csv#117"),
            ("注释姓名", "Antonio Maria Visconti", "S2，第5章第I节，p.121 n.7，L131"),
        ],
        "relation_ids": [
            "st-chp5-note-p121-n7-visconti-shop",
            "st-chp5-note-p121-n7-visconti-theft",
        ],
        "description_zh": (
            "本卡登记书后索引作“Visconti, Antonio Maria”、第5章脚注具名的Antonio Maria Visconti。"
            "Haskell称其店铺邻近Albergo del Moretto，并称他1699年报告十一幅画失窃；该脚注转引Bertolotti。"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Antonio Maria Visconti, indexed as “Visconti, Antonio Maria” and named in a Chapter 5 footnote. "
            "Haskell says his shop was near the Albergo del Moretto and that he reported the theft of eleven pictures in 1699; "
            "the footnote cites Bertolotti. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "两项内容均来自Haskell转引Bertolotti的脚注；原书未给出十一幅画的题名、所有人或失窃地点。"
            "作品端点cand-11910仍为S3 undecided，候选关系待S6，不据此新建作品KU。"
        ),
        "context_en": (
            "Both claims come from Haskell's footnote citing Bertolotti. The note gives no titles, owners, or theft location for the eleven pictures. "
            "The work endpoint cand-11910 remains S3 undecided; its relation candidate stays for S6, and no work KU is inferred."
        ),
    },
]

if __name__ == "__main__":
    raise SystemExit(registrar.main())
