from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_s_index_endpoints_schut_segala_serlio_skala_20261018 as registrar  # noqa: E402

registrar.ANCHOR = "s4-wilson-de-witte-wouwermans-wren-person-endpoints-20261018"
registrar.PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    "s4-wilson-de-witte-wouwermans-wren-person-endpoints-20261018"
)
registrar.BATCH_TITLE = "Wilson、de Witte、Wouwermans与Wren四组人物端点"
registrar.BATCH_PROCESS_NOTE = (
    "四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和8条source_backed姓名字段。"
    "Wilson只关联Smith接待英国访客的集体陈述；同一段中Mead、Newton与Walpole的其他关系陈述不归给Wilson。"
    "de Witte仅列入Roomer所藏数百件作品的多人作者名单，未具名单件作品或个人数量。"
    "Wouwermans在p.358是Algarotti建议学习的画家之一，p.359仅作作品风格比较；两者均不表示师承或作品归属。"
    "Wren与Gennari、Verrio、Gibbons共同出现在Whitehall一处未具名教堂的装饰陈述中。"
    "五条相关S2关系候选留待S6；无外部来源、正式关系或backlog写入。"
)
registrar.BATCH_RESULT_NOTE = (
    "；5条S2关系候选继续待S6；Wilson的接待名单、de Witte的多人藏品作者名单、Wouwermans的学习建议与风格比较、"
    "以及Wren参与的未具名教堂装饰均保留原书语境和限制；无外部来源、正式关系或backlog写入。"
)
registrar.TARGETS = [
    {
        "candidate": "cand-2815",
        "group": "new-person:richard-wilson-6ea937c8d1",
        "ku": "units/persons/richard-wilson",
        "card": "04-knowledge/units/persons/richard-wilson.md",
        "name_zh": "理查德·威尔逊",
        "name_en": "Richard Wilson",
        "index_entry": "UVWXYZ.csv#152",
        "index_name": "Wilson, Richard",
        "index_page": "301",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/10_CHP-10_intro.md",
            "第10章引言，印刷页301，行389",
            "line 389; print p. 301",
            "At one time or another John Breval, Horace Walpole, Richard Wilson, Sir Joshua Reynolds, James Wyatt and Robert Adam were aU welcomed by him.",
            "Haskell称Richard Wilson与其他英国鉴赏家或艺术家曾受Thomas Smith接待；原文没有给出Wilson单独到访的日期或细节。",
        ),
        "name_rows": [
            ("索引姓名", "Wilson, Richard", "S1，UVWXYZ.csv#152"),
            ("正文全名", "Richard Wilson", "S2，第10章引言，p.301，L389"),
        ],
        "relation_ids": ["st-chp10-p301-smith-official-visitors"],
        "description_zh": (
            "本卡登记书后索引主条“Wilson, Richard”及第10章第301页具名的Richard Wilson。"
            "Haskell将他列在曾受英国领事Thomas Smith接待的英国鉴赏家与艺术家名单中；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Richard Wilson, indexed as “Wilson, Richard” and named on page 301 of Chapter 10. "
            "Haskell includes him in a list of English connoisseurs and artists welcomed by the British consul Thomas Smith; "
            "the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell写道Wilson等人“at one time or another”受Smith接待；名单没有给出Wilson单独到访的时间或情节。"
            "脚注7所引Levey文章及页码未独立查阅；该集体接待关系候选留待S6。"
        ),
        "context_en": (
            "Haskell says Wilson and others were welcomed by Smith “at one time or another”; the list gives no individual date or visit details for Wilson. "
            "The Levey article and pages cited in footnote 7 were not independently consulted; the collective hospitality candidate remains for S6."
        ),
    },
    {
        "candidate": "cand-2817",
        "group": "new-person:de-peter-witte-d00315b83f",
        "ku": "units/persons/peter-de-witte",
        "card": "04-knowledge/units/persons/peter-de-witte.md",
        "name_zh": "彼得·德·维特",
        "name_en": "Peter de Witte",
        "index_entry": "UVWXYZ.csv#154",
        "index_name": "Witte, Peter de",
        "index_page": "206",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/08_CHP-8_sec_i.md",
            "第8章第I节，印刷页206，行34–36",
            "lines 34–36; print p. 206",
            "and he owned several hundreds by Paul Brill,\nPeter de Witte, Velvet Breughel, Leonard Bramer, Jacques Duyvelant, Cornelius\nPoelenburgh, Corneille Schut, Gioffredo Wals, Gerard van dor Bos and many others.",
            "Haskell称Roomer拥有数百件由包括Peter de Witte在内的多位佛兰德画家创作的作品。",
        ),
        "name_rows": [
            ("索引姓名", "Witte, Peter de", "S1，UVWXYZ.csv#154"),
            ("正文全名", "Peter de Witte", "S2，第8章第I节，p.206，L35"),
        ],
        "relation_ids": ["st-chp8-p206-roomer-owned-hundreds-by-flemish-artists"],
        "description_zh": (
            "本卡登记书后索引主条“Witte, Peter de”及第8章第206页具名的Peter de Witte。"
            "Haskell在Roomer藏品叙述中将他列入作品作者名单；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Peter de Witte, indexed as “Witte, Peter de” and named on page 206 of Chapter 8. "
            "Haskell lists him among the makers in an account of Roomer's collection; the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "原文称Roomer拥有数百件由该段多位画家创作的作品，并以“many others”继续开放名单；数量不是de Witte个人作品数，"
            "也未识别其单件作品。该集体藏品关系候选留待S6。"
        ),
        "context_en": (
            "The passage attributes several hundreds of works collectively to the listed painters and leaves the list open with “many others.” "
            "This is not a count of de Witte's individual works, and it identifies no individual work by him; the collective ownership candidate remains for S6."
        ),
    },
    {
        "candidate": "cand-2820",
        "group": "new-person:philips-wouwermans-44cfb8cece",
        "ku": "units/persons/philips-wouwermans",
        "card": "04-knowledge/units/persons/philips-wouwermans.md",
        "name_zh": "菲利普斯·沃维尔曼斯",
        "name_en": "Philips Wouwermans",
        "index_entry": "UVWXYZ.csv#157",
        "index_name": "Wouwermans, Philips",
        "index_page": "358, 359",
        "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/14_CHP-14_intro.md",
                "第14章引言，印刷页358，行122–123",
                "lines 122–123; print p. 358",
                "For these reasons he recommends studying Flemish painters such as Teniers and\nWouwermans, as well as Vernet and Pannini.",
                "Haskell称Algarotti建议学习包括Wouwermans在内的佛兰德画家，作为其所求风格组合的参考。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/14_CHP-14_intro.md",
                "第14章引言，印刷页359，行128",
                "line 128; print p. 359",
                "worthy of Wouwermans",
                "Haskell转述Algarotti将Tiepolo添加的船与白马称为“worthy of Wouwermans”；这是风格比较，不是作品归属。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Wouwermans, Philips", "S1，UVWXYZ.csv#157"),
            ("正文姓名形式", "Wouwermans", "S2，第14章引言，pp.358–359，L123、L128"),
        ],
        "relation_ids": [
            "st-chp14-p358-recommended-study-wouwermans",
            "st-chp14-p359-tiepolo-additions-to-pesci-setting",
        ],
        "description_zh": (
            "本卡登记书后索引主条“Wouwermans, Philips”及第14章第358–359页提及的Wouwermans。"
            "Haskell分别记述Algarotti建议学习他，以及将Tiepolo所加船与白马比作“worthy of Wouwermans”；"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Philips Wouwermans, indexed as “Wouwermans, Philips” and referred to on pages 358–359 of Chapter 14. "
            "Haskell reports Algarotti's recommendation to study him and compares Tiepolo's added boat and white horse as “worthy of Wouwermans”; "
            "the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "第358页的学习建议不证明师承；第359页的“worthy of Wouwermans”是风格比较，不把该船、白马或架构画归于Wouwermans。"
            "第二处引文经Haskell转述，所引书信未独立查阅；两条关系候选留待S6。"
        ),
        "context_en": (
            "The page 358 recommendation does not establish a teacher–pupil relationship. On page 359, “worthy of Wouwermans” is a stylistic comparison "
            "and does not attribute the boat, horse, or architectural setting to him. The second statement is quoted through Haskell; the cited letter was not independently consulted. "
            "Both relation candidates remain for S6."
        ),
    },
    {
        "candidate": "cand-2821",
        "group": "new-person:christopher-wren-512fe90374",
        "ku": "units/persons/christopher-wren",
        "card": "04-knowledge/units/persons/christopher-wren.md",
        "name_zh": "克里斯托弗·雷恩",
        "name_en": "Christopher Wren",
        "index_entry": "UVWXYZ.csv#158",
        "index_name": "Wren, Sir Christopher",
        "index_page": "196",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
            "第7章第IV节，印刷页196，行56–57",
            "lines 56–57; print p. 196",
            "Gennari turned from Danae or Elizabeth Felton as Cleopatra to altar paintings, and in combination with\n"
            "Verrio, Christopher Wren and Grinling Gibbons he helped to put into effect in\n"
            "Whitehall the most full-blooded Baroque decoration ever seen in an English church.",
            "Haskell称Gennari与Verrio、Christopher Wren、Grinling Gibbons共同促成Whitehall一处英国教堂的巴洛克装饰。",
        ),
        "name_rows": [
            ("索引姓名", "Wren, Sir Christopher", "S1，UVWXYZ.csv#158"),
            ("正文全名", "Christopher Wren", "S2，第7章第IV节，p.196，L56"),
        ],
        "relation_ids": ["st-chp7-p196-whitehall_programme"],
        "description_zh": (
            "本卡登记书后索引主条“Wren, Sir Christopher”及第7章第196页具名的Christopher Wren。"
            "Haskell将他列入与Gennari、Verrio、Gibbons共同促成Whitehall教堂装饰的名单；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Christopher Wren, indexed as “Wren, Sir Christopher” and named on page 196 of Chapter 7. "
            "Haskell lists him with Gennari, Verrio, and Gibbons in an account of a Whitehall church decoration programme; "
            "the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "原文将Wren与三人并列，称其共同促成Whitehall一处未具名英国教堂的巴洛克装饰；教堂和具体装饰作品均未识别，"
            "“most full-blooded”为Haskell评价。该集体关系候选留待S6。"
        ),
        "context_en": (
            "The passage groups Wren with three others in realizing Baroque decoration for an unnamed English church at Whitehall. "
            "Neither the church nor individual decorative works are identified, and “most full-blooded” is Haskell's evaluation. "
            "The collective relation candidate remains for S6."
        ),
    },
]

if __name__ == "__main__":
    raise SystemExit(registrar.main())
