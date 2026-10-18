from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_s_index_endpoints_schut_segala_serlio_skala_20261018 as registrar  # noqa: E402

registrar.ANCHOR = "s4-both-bramante-bramer-brand-person-endpoints-20261018"
registrar.PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    "s4-both-bramante-bramer-brand-person-endpoints-20261018"
)
registrar.BATCH_TITLE = "Both、Bramante、Bramer与Brand四组人物端点"
registrar.BATCH_PROCESS_NOTE = (
    "四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和8条source_backed姓名字段。"
    "Jan Both的姓名跨行，所处句保留Haskell的probably限定；Donato Bramante仅列于Cassiano引述的建筑复兴者集合中，"
    "不将集合表述拆作个人事实。Leonard Bramer列于Roomer藏画的开放多人名单，数百件不归到个人名下。"
    "Johannes Christian Brand依据索引全名与正文姓氏对齐；相关藏画未具名或计数。五条S2关系候选留待S6；"
    "无外部身份来源、正式关系或backlog写入。"
)
registrar.BATCH_RESULT_NOTE = (
    "；Both的群体陈述保留probably，Bramante仅在建筑复兴者集合引文中出现，"
    "Bramer与Brand分别留在Roomer藏画及Zanetti藏画的多人表述范围内；五条S2关系候选留待S6，不新增正式关系。"
)

book_source = registrar.book_source
registrar.TARGETS = [
    {
        "candidate": "cand-0416",
        "group": "new-person:both-jan-e494918365",
        "ku": "units/persons/jan-both",
        "card": "04-knowledge/units/persons/jan-both.md",
        "name_zh": "扬·博特",
        "name_en": "Jan Both",
        "index_entry": "B.csv#263",
        "index_name": "Both, Jan",
        "index_page": "172",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
        "book_source": book_source(
            "02-sources/02-Markdown/07_CHP-7_sec_i.md",
            "第7章第I节，印刷页172，行34–35",
            "lines 34–35; print p. 172",
            "It was practised mainly by the young Claude, by a number of Flemish painters, "
            "of whom the most-distinguished was probably Jan\nBoth, and, to a lesser extent, by Nicolas Poussin.",
            "Haskell称这种平衡风景画类型主要由年轻的Claude及若干佛兰德画家实践，其中Jan Both可能最突出，Poussin作用较小；保留probably等限定。",
        ),
        "name_rows": [
            ("索引姓名", "Both, Jan", "S1，B.csv#263"),
            ("正文跨行全名", "Jan Both", "S2，第7章第I节，p.172，L34–35"),
        ],
        "relation_ids": ["st-chp7-p172-i11", "st-chp7-p172-i12"],
        "description_zh": (
            "本卡登记书后索引作“Both, Jan”及第7章第172页跨行写出的Jan Both。"
            "Haskell将他列入实践平衡风景画的佛兰德画家，并称其可能最为突出；“probably”限定仍保留。中文名为项目工作音译。"
        ),
        "description_en": (
            "This card records Jan Both, indexed as “Both, Jan” and named across a line break in Chapter 7, page 172. "
            "Haskell includes him among Flemish painters who practised balanced landscape painting and says he was probably the most distinguished; "
            "the qualification “probably” is retained. The Chinese name is a project working transliteration."
        ),
        "context_zh": (
            "相关S2候选描述的是多人及未具名佛兰德画家群体；不把“probably”改写为确定排序，也不将群体活动扩写为单人经历。"
        ),
        "context_en": (
            "The S2 candidates describe several named artists and an unnamed group of Flemish painters; “probably” is not converted into a definite ranking, "
            "and the group statement is not expanded into an individual biography."
        ),
    },
    {
        "candidate": "cand-0443",
        "group": "new-person:bramante-donato-11c48b73a0",
        "ku": "units/persons/donato-bramante",
        "card": "04-knowledge/units/persons/donato-bramante.md",
        "name_zh": "多纳托·布拉曼特",
        "name_en": "Donato Bramante",
        "index_entry": "B.csv#290",
        "index_name": "Bramante, Donato",
        "index_page": "103",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
        "book_source": book_source(
            "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
            "第4章第II节，印刷页103，行50–51",
            "lines 50–51; print p. 103",
            "This was not the way of Brunelleschi, Buonarotti,\nBramante, Serlio, Palladio, Vignola and the other restorers of this great art, "
            "who took the true proportions of those perfectly regular orders from Roman buildings.",
            "Haskell引述Cassiano，将Bramante列在复兴古典建筑的一组人物之中；取法罗马建筑比例的说法保持为对该群体的引述。",
        ),
        "name_rows": [
            ("索引姓名", "Bramante, Donato", "S1，B.csv#290"),
            ("正文称名", "Bramante", "S2，第4章第II节，p.103，L50–51"),
        ],
        "relation_ids": ["st-chp4-sec-ii-l46-51-restorers-took-proportions-from-roman-buildings"],
        "description_zh": (
            "本卡登记书后索引主条“Bramante, Donato”及第4章第103页Cassiano引文中的Bramante。"
            "引文将他列入一组建筑复兴者；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Donato Bramante, indexed as “Bramante, Donato” and named in the Chapter 4 quotation on page 103. "
            "The quotation lists him among a group of architectural restorers. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "建筑复兴者及其取法罗马建筑比例的陈述来自Haskell转引Cassiano；不将集合谓词拆作已独立核实的Bramante个人事实。"
        ),
        "context_en": (
            "The statement about architectural restorers taking proportions from Roman buildings is Haskell's report of Cassiano; "
            "the collective predicate is not separated into an independently verified fact about Bramante."
        ),
    },
    {
        "candidate": "cand-0444",
        "group": "new-person:bramer-leonard-86eba64601",
        "ku": "units/persons/leonard-bramer",
        "card": "04-knowledge/units/persons/leonard-bramer.md",
        "name_zh": "莱昂纳德·布拉默",
        "name_en": "Leonard Bramer",
        "index_entry": "B.csv#291",
        "index_name": "Bramer, Leonard",
        "index_page": "206",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "book_source": book_source(
            "02-sources/02-Markdown/08_CHP-8_sec_i.md",
            "第8章第I节，印刷页206，行34–36",
            "lines 34–36; print p. 206",
            "Peter de Witte, Velvet Breughel, Leonard Bramer, Jacques Duyvelant",
            "Haskell列举Roomer所藏作品的作者，其中包括Leonard Bramer；“数百件”修饰开放的多人作品集合。",
        ),
        "name_rows": [
            ("索引姓名", "Bramer, Leonard", "S1，B.csv#291"),
            ("正文全名", "Leonard Bramer", "S2，第8章第I节，p.206，L34–36"),
        ],
        "relation_ids": ["st-chp8-p206-roomer-owned-hundreds-by-flemish-artists"],
        "description_zh": (
            "本卡登记书后索引主条“Bramer, Leonard”及第8章第206页Roomer藏画作者名单中的Leonard Bramer。"
            "原书称作品为数百件并以“many others”开放名单；数量不归到单一作者名下。中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Leonard Bramer, indexed as “Bramer, Leonard” and named in Chapter 8's list of makers of works in Roomer's collection, page 206. "
            "The book describes several hundred works and leaves the list open with “many others”; the number is not assigned to an individual maker. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "关系候选是Roomer藏有多人作品的开放名单；不推定Bramer个人作品数量、单件题名或委托方式。"
        ),
        "context_en": (
            "The relation candidate is an open list of makers whose works Roomer owned; no individual work count, title, or commission is inferred for Bramer."
        ),
    },
    {
        "candidate": "cand-0445",
        "group": "new-person:brand-christian-johannes-4b11408288",
        "ku": "units/persons/johannes-christian-brand",
        "card": "04-knowledge/units/persons/johannes-christian-brand.md",
        "name_zh": "约翰内斯·克里斯蒂安·布兰德",
        "name_en": "Johannes Christian Brand",
        "index_entry": "B.csv#292",
        "index_name": "Brand, Johannes Christian",
        "index_page": "342",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
        "book_source": book_source(
            "02-sources/02-Markdown/13_CHP-13_intro.md",
            "第13章引言，印刷页342，行102",
            "line 102; print p. 342",
            "He owned pictures by the German artists Brand and Dietrich,",
            "Haskell称Zanetti收藏有德国画家Brand与Dietrich的作品；正文仅作姓氏称名，索引列出Johannes Christian Brand。",
        ),
        "name_rows": [
            ("索引姓名", "Brand, Johannes Christian", "S1，B.csv#292"),
            ("正文姓氏", "Brand", "S2，第13章引言，p.342，L102"),
        ],
        "relation_ids": ["st-chp13-p342-zanetti_owned_brand_and_dietrich_pictures"],
        "description_zh": (
            "本卡登记书后索引主条“Brand, Johannes Christian”及第13章第342页正文的Brand。"
            "Haskell称Zanetti收藏有Brand与Dietrich的作品，但未具名单件作品或数量。中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Johannes Christian Brand, indexed as “Brand, Johannes Christian” and named as Brand in Chapter 13, page 342. "
            "Haskell says Zanetti owned works by Brand and Dietrich but identifies no individual works or quantity. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "索引全名与正文姓氏按书内索引锚点对齐；藏画陈述仍限于Haskell的多人表述，不据此新增作品或收藏的具体事实。"
        ),
        "context_en": (
            "The indexed full name is aligned with the surname in the text through the book's index anchor; "
            "the collection statement remains Haskell's group-level account, with no specific work or collection detail added."
        ),
    },
]

if __name__ == "__main__":
    raise SystemExit(registrar.main())
