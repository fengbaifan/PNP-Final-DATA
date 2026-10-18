from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_s_index_endpoints_schut_segala_serlio_skala_20261018 as registrar  # noqa: E402

registrar.ANCHOR = "s4-wyatt-young-zaguri-zuccalli-person-endpoints-20261018"
registrar.PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    "s4-wyatt-young-zaguri-zuccalli-person-endpoints-20261018"
)
registrar.BATCH_TITLE = "Wyatt、Young、Zaguri与Zuccalli四组人物端点"
registrar.BATCH_PROCESS_NOTE = (
    "四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和7条source_backed姓名字段。"
    "James Wyatt只关联Smith接待英国访客的集体陈述；同段关于Mead、Newton、Walpole的其他关系候选不归给Wyatt。"
    "Edward Young以书后索引主条和第15章p.370的间接称名归组；索引#164不列页码，同主条#165列Night Thoughts子目及p.370。"
    "Night Thoughts索引archive候选cand-2828仍S3 undecided，正文work候选cand-10551保持excluded；作者关系不登记为正式边。"
    "Pietro Zaguri仅按Haskell所述与Memmo围绕Lodoli merits的friendly controversy登记。"
    "Enrico Zuccalli的Schleissheim委建记述保留“a Versailles”原文比喻，不推定委托人为Max Emmanuel或工程已完成。"
    "五条S2关系候选留待S6；无外部来源、正式关系或backlog写入。"
)
registrar.BATCH_RESULT_NOTE = (
    "；5条S2关系候选继续待S6；Wyatt仅属Smith英国访客名单；Young的索引主条及同主条Night Thoughts子目分列，"
    "cand-2828仍S3 undecided、cand-10551仍excluded，未登记作者正式边；Zaguri的争论保留friendly限定；"
    "Zuccalli委建语境不指定委托人或工程完成状态；无外部来源、正式关系或backlog写入。"
)


def index_subentry_source() -> dict:
    return {
        "citation": "Francis Haskell, *Patrons and Painters*, index, UVWXYZ.csv.",
        "location": "书后索引，UVWXYZ.csv#165；同主条“Young, Edward”下的Night Thoughts子目，指向印刷页370。",
        "sentence_summary": "索引在“Young, Edward”主条下列出Night Thoughts子目并指向印刷页370；该行单独保留为archive候选。",
        "original_quotes": [{"source_span": "UVWXYZ.csv#165", "text": "Night Thoughts"}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": "02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv",
            "source_span": "UVWXYZ.csv#165",
        },
    }


registrar.TARGETS = [
    {
        "candidate": "cand-2823",
        "group": "new-person:james-wyatt-d25b8edf77",
        "ku": "units/persons/james-wyatt",
        "card": "04-knowledge/units/persons/james-wyatt.md",
        "name_zh": "詹姆斯·怀亚特",
        "name_en": "James Wyatt",
        "index_entry": "UVWXYZ.csv#160",
        "index_name": "Wyatt, James",
        "index_page": "301",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/10_CHP-10_intro.md",
            "第10章引言，印刷页301，行389",
            "line 389; print p. 301",
            "At one time or another John Breval, Horace Walpole, Richard Wilson, Sir Joshua Reynolds, James Wyatt and Robert Adam were aU welcomed by him.",
            "Haskell将James Wyatt列入曾受Thomas Smith接待的英国鉴赏家与艺术家名单；原文没有给出Wyatt单独到访的日期或细节。",
        ),
        "name_rows": [
            ("索引姓名", "Wyatt, James", "S1，UVWXYZ.csv#160"),
            ("正文全名", "James Wyatt", "S2，第10章引言，p.301，L389"),
        ],
        "relation_ids": ["st-chp10-p301-smith-official-visitors"],
        "description_zh": (
            "本卡登记书后索引主条“Wyatt, James”及第10章第301页具名的James Wyatt。"
            "Haskell将他列在曾受英国领事Thomas Smith接待的英国鉴赏家和艺术家名单中；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records James Wyatt, indexed as “Wyatt, James” and named on page 301 of Chapter 10. "
            "Haskell includes him in a list of English connoisseurs and artists welcomed by the British consul Thomas Smith; "
            "the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "原文称名单中的人“at one time or another”受Smith接待，没有给出Wyatt单独到访的时间或情节。"
            "脚注7所引Levey文章及页码未独立查阅；该集体接待关系候选留待S6。"
        ),
        "context_en": (
            "Haskell says the people in the list were welcomed by Smith “at one time or another”; no individual date or visit details are given for Wyatt. "
            "The Levey article and pages cited in footnote 7 were not independently consulted; the collective hospitality candidate remains for S6."
        ),
    },
    {
        "candidate": "cand-2827",
        "group": "new-person:edward-young-5c6ef7bfa5",
        "ku": "units/persons/edward-young",
        "card": "04-knowledge/units/persons/edward-young.md",
        "name_zh": "爱德华·杨",
        "name_en": "Edward Young",
        "index_entry": "UVWXYZ.csv#164",
        "index_name": "Young, Edward",
        "index_page": "",
        "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
                "第15章第II节，印刷页370，行63",
                "line 63; print p. 370",
                "This was called \u2018Young\u2019s Wood\u2019 in honour of the poet whose Night Thoughts had caught the romantic imagination of Europe.",
                "Haskell称一片林地以“the poet”命名，并提到该诗人的Night Thoughts；书后索引主条将该诗人列为Edward Young。",
            ),
            index_subentry_source(),
        ],
        "name_rows": [
            ("索引姓名", "Young, Edward", "S1，UVWXYZ.csv#164；该行未列页码"),
        ],
        "relation_ids": [
            "st-chp15-p370-youngs-wood-named-in-honour-of-young",
            "st-chp15-p370-night-thoughts-authored-by-edward-young",
        ],
        "description_zh": (
            "本卡登记书后索引主条“Young, Edward”及第15章第370页所述“the poet”。该段未在正文写出诗人全名；"
            "书后索引同主条另列Night Thoughts子目并指向第370页，将此处所指诗人标为Edward Young。"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Young, Edward” and the Chapter 15, page 370 reference to “the poet.” "
            "The passage does not give the poet's full name in its body text; a separate Night Thoughts sub-entry under the same index heading points to page 370 and identifies the poet as Edward Young. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "S3将cand-2827记录为new source-local person identity group；该决定只依据书内索引和正文锚点，不含外部身份核验。"
            "同主条Night Thoughts索引候选cand-2828仍为S3 undecided，正文work候选cand-10551仍excluded；"
            "两条作者／命名关系候选留待S6，不新建或合并Night Thoughts KU，也不登记正式关系。"
        ),
        "context_en": (
            "S3 records cand-2827 as a new source-local person identity group, based only on the book's index and body anchor, with no external identity verification. "
            "The separate Night Thoughts index candidate cand-2828 remains S3 undecided and the body work candidate cand-10551 remains excluded. "
            "Both authorship/naming candidates remain for S6; no Night Thoughts KU is created or merged and no formal relation is registered."
        ),
    },
    {
        "candidate": "cand-2829",
        "group": "new-person:pietro-zaguri-f977d2ea03",
        "ku": "units/persons/pietro-zaguri",
        "card": "04-knowledge/units/persons/pietro-zaguri.md",
        "name_zh": "皮耶特罗·扎古里",
        "name_en": "Pietro Zaguri",
        "index_entry": "UVWXYZ.csv#166",
        "index_name": "Zaguri, Pietro",
        "index_page": "368",
        "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
            "第15章第II节，印刷页368，行41",
            "line 41; print p. 368",
            "During his last years Memmo became involved in friendly controversy with another patrician, Pietro Zaguri, over the merits of Lodoli, to whose memory he remained passionately faithful.",
            "Haskell称Memmo晚年与贵族Pietro Zaguri围绕Lodoli的 merits 进行一场friendly controversy。",
        ),
        "name_rows": [
            ("索引姓名", "Zaguri, Pietro", "S1，UVWXYZ.csv#166"),
            ("正文全名", "Pietro Zaguri", "S2，第15章第II节，p.368，L41"),
        ],
        "relation_ids": ["st-chp15-p368-memmo-zaguri-lodoli-controversy"],
        "description_zh": (
            "本卡登记书后索引主条“Zaguri, Pietro”及第15章第368页具名的Pietro Zaguri。"
            "Haskell将他记为与Andrea Memmo围绕Carlo Lodoli merits发生friendly controversy的贵族；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Pietro Zaguri, indexed as “Zaguri, Pietro” and named on page 368 of Chapter 15. "
            "Haskell describes him as the patrician involved with Andrea Memmo in a friendly controversy over Carlo Lodoli's merits; "
            "the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "原文将争论限定为friendly，且置于Memmo晚年；不补充争论内容或日期。相关关系候选保留原文限定并留待S6。"
        ),
        "context_en": (
            "The passage calls the controversy friendly and places it in Memmo's last years; it gives no further details or date. "
            "The relation candidate retains this wording and remains for S6."
        ),
    },
    {
        "candidate": "cand-2878",
        "group": "new-person:enrico-zuccalli-b2963e912b",
        "ku": "units/persons/enrico-zuccalli",
        "card": "04-knowledge/units/persons/enrico-zuccalli.md",
        "name_zh": "恩里科·祖卡利",
        "name_en": "Enrico Zuccalli",
        "index_entry": "UVWXYZ.csv#215",
        "index_name": "Zuccalli, Enrico",
        "index_page": "193",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
            "第7章第IV节，印刷页193，行17–18",
            "lines 17–18; print p. 193",
            "He was followed by an architect of far greater versatility, Enrico Zuccalli, who, under the new Elector Max Emmanuel, was commissioned in 1712 to build a \u2018Versailles\u2019 at\nSchleissheim.",
            "Haskell称Enrico Zuccalli于Max Emmanuel任新选帝侯期间受命于1712年在Schleissheim建造一个被比作Versailles的项目；原句未明确委托人或完成状态。",
        ),
        "name_rows": [
            ("索引姓名", "Zuccalli, Enrico", "S1，UVWXYZ.csv#215"),
            ("正文全名", "Enrico Zuccalli", "S2，第7章第IV节，p.193，L17"),
        ],
        "relation_ids": ["st-chp7-p193-zuccalli-schleissheim-project"],
        "description_zh": (
            "本卡登记书后索引主条“Zuccalli, Enrico”及第7章第193页具名的Enrico Zuccalli。"
            "Haskell称他在Max Emmanuel为新选帝侯期间受命于Schleissheim建造一个被比作Versailles的项目；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Enrico Zuccalli, indexed as “Zuccalli, Enrico” and named on page 193 of Chapter 7. "
            "Haskell says he was commissioned during Max Emmanuel's tenure as the new Elector to build a project at Schleissheim compared to Versailles; "
            "the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "原文写作“a Versailles”，按比喻保留引号；虽称工程发生于Max Emmanuel任新选帝侯期间，未明确指定委托人，也未证明工程完成。"
            "唯一关系候选留待S6，不据此新增作品KU或正式关系。"
        ),
        "context_en": (
            "The source's phrase “a Versailles” is retained as a comparison. Although the passage places the commission during Max Emmanuel's tenure as new Elector, "
            "it does not explicitly name the commissioning agent or establish completion. The relation candidate remains for S6; no work KU or formal relation is added."
        ),
    },
]

if __name__ == "__main__":
    raise SystemExit(registrar.main())
