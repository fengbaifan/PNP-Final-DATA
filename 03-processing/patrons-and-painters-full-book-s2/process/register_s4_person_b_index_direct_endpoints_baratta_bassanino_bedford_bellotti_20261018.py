from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_s_index_endpoints_schut_segala_serlio_skala_20261018 as registrar  # noqa: E402

registrar.ANCHOR = "s4-baratta-bassanino-bedford-bellotti-person-endpoints-20261018"
registrar.PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    "s4-baratta-bassanino-bedford-bellotti-person-endpoints-20261018"
)
registrar.BATCH_TITLE = "Baratta、Bassanino、Bedford与Bellotti四组人物端点"
registrar.BATCH_PROCESS_NOTE = (
    "四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和8条source_backed姓名字段。"
    "Francesco Baratta与Ercole Ferrata均被Haskell写作与Camillo Pamfili及其未具名继承人发生长期财务纠纷的雕刻家；继承人身份及关系边界不外推。"
    "Virgilio Bassanino只据Haskell转述的Livorno《Sabines之劫》绘画记述登记；未补画作观察日期或现藏地。"
    "John, 4th Duke of Bedford依据索引全称及第10章p.305的Duke of Bedford称名归组；只将Canaletto二十幅景观的委托归于该身份，不给单件作品补题名或日期。"
    "Pietro Bellotti被列为三十年战争结束后约三十年间在慕尼黑受雇的意大利画家之一；不推导精确任期或具体委托。"
    "四条相关S2关系候选留待S6；无外部来源、正式关系或backlog写入。"
)
registrar.BATCH_RESULT_NOTE = (
    "；Baratta财务纠纷、Bassanino绘画及Livorno语境、Bedford景观委托和Bellotti慕尼黑受雇四条S2关系候选留待S6；"
    "不新增外部来源、正式关系或backlog项目。"
)
registrar.TARGETS = [
    {
        "candidate": "cand-0181",
        "group": "new-person:baratta-francesco-8d4e7a7bfb",
        "ku": "units/persons/francesco-baratta",
        "card": "04-knowledge/units/persons/francesco-baratta.md",
        "name_zh": "弗朗切斯科·巴拉塔",
        "name_en": "Francesco Baratta",
        "index_entry": "B.csv#28",
        "index_name": "Baratta, Francesco",
        "index_page": "149",
        "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/06_CHP-6_sec_i.md",
            "第6章第I节，印刷页149，行40",
            "line 40; print p. 149",
            "Both the sculptors Francesco Baratta and Ercole Ferrata were involved in prolonged financial difficulties with Pamfili and his heirs",
            "Haskell称雕刻家Francesco Baratta与Ercole Ferrata均与Pamfili及其继承人发生长期财务纠纷；继承人未具名。",
        ),
        "name_rows": [
            ("索引姓名", "Baratta, Francesco", "S1，B.csv#28"),
            ("正文全名", "Francesco Baratta", "S2，第6章第I节，p.149，L40"),
        ],
        "relation_ids": ["st-chp6-p149-baratta-ferrata-financial-difficulties"],
        "description_zh": (
            "本卡登记书后索引主条“Baratta, Francesco”及第6章第149页正文具名的Francesco Baratta；"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Baratta, Francesco” and Francesco Baratta named in Chapter 6 on page 149; "
            "the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell将Baratta与Ercole Ferrata并列为与Pamfili及其继承人发生长期财务纠纷的雕刻家；继承人未具名，也不与其他段落的继承人候选合并。"
        ),
        "context_en": (
            "Haskell names Baratta with Ercole Ferrata as sculptors involved in prolonged financial difficulties with Pamfili and his heirs; "
            "the heirs are unnamed and are not merged with heirs mentioned elsewhere."
        ),
    },
    {
        "candidate": "cand-0255",
        "group": "new-person:bassanino-virgilio-5074fb2e86",
        "ku": "units/persons/virgilio-bassanino",
        "card": "04-knowledge/units/persons/virgilio-bassanino.md",
        "name_zh": "维吉利奥·巴萨尼诺",
        "name_en": "Virgilio Bassanino",
        "index_entry": "B.csv#102",
        "index_name": "Bassanino, Virgilio",
        "index_page": "",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
            "第8章第II节，印刷页232，行254",
            "line 254; print p. 232",
            "in Livorno there is a Rape of the Sabines by Virgilio Bassanino",
            "Haskell转述Ferdinand书信语境中一幅位于Livorno、表现Sabines之劫题材的Virgilio Bassanino绘画；该段未给出观察日期或现藏地。",
        ),
        "name_rows": [
            ("索引姓名", "Bassanino, Virgilio", "S1，B.csv#102（该索引行未列页码）"),
            ("正文全名", "Virgilio Bassanino", "S2，第8章第II节，p.232，L254"),
        ],
        "relation_ids": ["st-chp8-p232-bassanino-rape-sabines"],
        "description_zh": (
            "本卡登记书后索引主条“Bassanino, Virgilio”（索引行未列页码）及第8章第232页正文具名的Virgilio Bassanino；"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Bassanino, Virgilio” (the index row gives no page) and Virgilio Bassanino named in Chapter 8 on page 232; "
            "the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell转述Ferdinand书信语境中一幅位于Livorno、表现Sabines之劫题材的绘画；不据此推定确切观察日期或现藏地。"
        ),
        "context_en": (
            "Haskell reports a Rape of the Sabines by Bassanino at Livorno in the context of Ferdinand’s letters; "
            "no exact observation date or present location is inferred."
        ),
    },
    {
        "candidate": "cand-0267",
        "group": "new-person:4th-bedford-john-of-0badc6a345",
        "ku": "units/persons/john-4th-duke-of-bedford",
        "card": "04-knowledge/units/persons/john-4th-duke-of-bedford.md",
        "name_zh": "约翰，第四代贝德福德公爵",
        "name_en": "John, 4th Duke of Bedford",
        "index_entry": "B.csv#114",
        "index_name": "Bedford, John, 4th Duke of",
        "index_page": "305",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/10_CHP-10_intro.md",
            "第10章引言，印刷页305，行431–432",
            "lines 431–432; print p. 305",
            "Canaletto painted twenty views for the\nDuke of Bedford",
            "Haskell称Canaletto在1730年代后半为Duke of Bedford绘制二十幅景观；未给出各幅题名或单件委托日期。",
        ),
        "name_rows": [
            ("索引姓名与爵号", "Bedford, John, 4th Duke of", "S1，B.csv#114"),
            ("正文称号", "Duke of Bedford", "S2，第10章引言，p.305，L431–432"),
        ],
        "relation_ids": ["st-chp10-p305-bedford-views"],
        "description_zh": (
            "本卡登记书后索引主条“Bedford, John, 4th Duke of”及第10章第305页正文中的Duke of Bedford；"
            "不将来源未给出的姓氏扩入规范名。"
        ),
        "description_en": (
            "This card records the index entry “Bedford, John, 4th Duke of” and the Duke of Bedford named in Chapter 10 on page 305; "
            "no surname absent from the source is added to the preferred name."
        ),
        "context_zh": (
            "Haskell称Canaletto在1730年代后半为该公爵绘制二十幅景观；不为各幅补题名或日期，也不把同段给Hervey、Carlisle的画作归给贝德福德。"
        ),
        "context_en": (
            "Haskell says Canaletto painted twenty views for the duke during the latter half of the 1730s; no individual titles or dates are supplied, "
            "and the views for Hervey and Carlisle in the same passage are not assigned to Bedford."
        ),
    },
    {
        "candidate": "cand-0278",
        "group": "new-person:bellotti-pietro-89aea065b8",
        "ku": "units/persons/pietro-bellotti",
        "card": "04-knowledge/units/persons/pietro-bellotti.md",
        "name_zh": "皮耶特罗·贝洛蒂",
        "name_en": "Pietro Bellotti",
        "index_entry": "B.csv#125",
        "index_name": "Bellotti, Pietro",
        "index_page": "193",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
            "第7章第IV节，印刷页193，行18–19",
            "lines 18–19; print p. 193",
            "Antonio Triva and Pietro Bellotti, were also employed at Munich during the three decades that followed the end of the Thirty Years War.",
            "Haskell将Pietro Bellotti列为三十年战争结束后三十年间在慕尼黑受雇的数位意大利画家之一；“a number”并非穷尽名单。",
        ),
        "name_rows": [
            ("索引姓名", "Bellotti, Pietro", "S1，B.csv#125"),
            ("正文全名", "Pietro Bellotti", "S2，第7章第IV节，p.193，L18–19"),
        ],
        "relation_ids": ["st-chp7-p193-munich-italian-painters"],
        "description_zh": (
            "本卡登记书后索引主条“Bellotti, Pietro”及第7章第193页正文具名的Pietro Bellotti；"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Bellotti, Pietro” and Pietro Bellotti named in Chapter 7 on page 193; "
            "the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell将Bellotti列为三十年战争结束后三十年间在慕尼黑受雇的数位意大利画家之一；不推导精确任期或具体委托。"
        ),
        "context_en": (
            "Haskell includes Bellotti among a number of Italian painters employed at Munich during the three decades after the Thirty Years War; "
            "no exact tenure or individual commission is inferred."
        ),
    },
]

if __name__ == "__main__":
    raise SystemExit(registrar.main())
