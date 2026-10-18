from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_s_index_endpoints_schut_segala_serlio_skala_20261018 as registrar  # noqa: E402

registrar.ANCHOR = "s4-bagutti-balbi-baldi-bandinelli-person-endpoints-20261018"
registrar.PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    "s4-bagutti-balbi-baldi-bandinelli-person-endpoints-20261018"
)
registrar.BATCH_TITLE = "Bagutti、Balbi、Baldi与Bandinelli四组人物端点"
registrar.BATCH_PROCESS_NOTE = (
    "四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和8条source_backed姓名字段。"
    "Pietro Martire Bagutti仅在正文以Bagutti出现；Haskell称Brydges雇用他与Bellucci、Sleter装饰Canons礼拜堂，但未分配个人分工。"
    "Paolo Battista Balbi与Beccari、Marcello Malpighi被列为拥有画作的博洛尼亚医生；不将具体画作分配给Balbi，也不与Genoese Balbi家族合并。"
    "Lazzaro Baldi依据索引及正文姓名登记；p.60的委托事实明确保留在卡片语境供S6反向关系审查，但当前S2没有关联到该身份组的relation_candidate，不在本批造边。"
    "Baccio Bandinelli只出现在Galileo对Orlando Furioso的嵌套引文及假设性草图中，不登记为现存作品的作者或归属。"
    "三条已登记的S2关系候选留待S6；无外部来源、正式关系或backlog写入。"
)
registrar.BATCH_RESULT_NOTE = (
    "；Bagutti教堂装饰团队、Balbi多人藏画陈述及Bandinelli／Parmigianino假设草图语境的三条S2关系候选留待S6；"
    "Baldi的p.60委托句保留供S6反向关系审查，当前无对应S2 relation_candidate；不新增正式关系、外部来源或backlog项目。"
)
registrar.TARGETS = [
    {
        "candidate": "cand-0161",
        "group": "new-person:bagutti-martire-pietro-ef19d5eb62",
        "ku": "units/persons/pietro-martire-bagutti",
        "card": "04-knowledge/units/persons/pietro-martire-bagutti.md",
        "name_zh": "皮耶特罗·马尔蒂雷·巴古蒂",
        "name_en": "Pietro Martire Bagutti",
        "index_entry": "B.csv#8",
        "index_name": "Bagutti, Pietro Martire",
        "index_page": "281",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/10_CHP-10_intro.md",
            "第10章引言，印刷页281，行131",
            "line 131; print p. 281",
            "the Bolognese stuccatore Bagutti",
            "Haskell称Bagutti为博洛尼亚stuccatore，并将其列入Brydges雇用的Canons礼拜堂装饰团队。",
        ),
        "name_rows": [
            ("索引姓名", "Bagutti, Pietro Martire", "S1，B.csv#8"),
            ("正文姓氏", "Bagutti", "S2，第10章引言，p.281，L131"),
        ],
        "relation_ids": ["st-chp10-p281-bellucci-chandos-chapel-team"],
        "description_zh": (
            "本卡登记书后索引主条“Bagutti, Pietro Martire”及第10章第281页正文称名Bagutti；"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Bagutti, Pietro Martire” and Bagutti named in Chapter 10 on page 281; "
            "the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell称Bagutti为博洛尼亚stuccatore，并与Bellucci、Francesco Sleter并列为Brydges雇用的Canons礼拜堂装饰人员；原文未说明个人分工。"
        ),
        "context_en": (
            "Haskell calls Bagutti a Bolognese stuccatore and lists him with Bellucci and Francesco Sleter among those employed by Brydges to decorate the Canons chapel; "
            "the passage does not specify individual tasks."
        ),
    },
    {
        "candidate": "cand-0164",
        "group": "new-person:balbi-battista-paolo-63acb22825",
        "ku": "units/persons/paolo-battista-balbi",
        "card": "04-knowledge/units/persons/paolo-battista-balbi.md",
        "name_zh": "保罗·巴蒂斯塔·巴尔比",
        "name_en": "Paolo Battista Balbi",
        "index_entry": "B.csv#11",
        "index_name": "Balbi, Paolo Battista",
        "index_page": "203",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/08_CHP-8_sec_i.md",
            "第8章第I节，印刷页203，行8",
            "line 8; print p. 203",
            "Paolo Battista Balbi, Beccari and the great - Marcello Malpighi all owned pictures.",
            "Haskell将Paolo Battista Balbi、Beccari与Marcello Malpighi列为拥有画作的博洛尼亚医生；OCR中的great后多余连字符已由S2记录校正。",
        ),
        "name_rows": [
            ("索引姓名", "Balbi, Paolo Battista", "S1，B.csv#11"),
            ("正文全名", "Paolo Battista Balbi", "S2，第8章第I节，p.203，L8"),
        ],
        "relation_ids": ["st-chp8-p203-bolognese-doctors-picture-owners"],
        "description_zh": (
            "本卡登记书后索引主条“Balbi, Paolo Battista”及第8章第203页正文具名的Paolo Battista Balbi；"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Balbi, Paolo Battista” and Paolo Battista Balbi named in Chapter 8 on page 203; "
            "the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell把Balbi与Beccari、Marcello Malpighi列作拥有画作的博洛尼亚医生；未识别或逐人分配具体画作，不与Genoese Balbi家族混并。"
        ),
        "context_en": (
            "Haskell lists Balbi with Beccari and Marcello Malpighi as Bolognese doctors who owned pictures; no particular picture is identified or assigned to one of them, "
            "and this person is kept distinct from the Genoese Balbi family."
        ),
    },
    {
        "candidate": "cand-0165",
        "group": "new-person:baldi-lazzaro-f2aa552fa8",
        "ku": "units/persons/lazzaro-baldi",
        "card": "04-knowledge/units/persons/lazzaro-baldi.md",
        "name_zh": "拉扎罗·巴尔迪",
        "name_en": "Lazzaro Baldi",
        "index_entry": "B.csv#12",
        "index_name": "Baldi, Lazzaro",
        "index_page": "60",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_vii.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/02_CHP-2_sec_vii.md",
            "第2章第VII节，印刷页60，行28–29",
            "lines 28–29; print p. 60",
            "He commissioned from Lazzaro Baldi and Ciro",
            "Haskell称Francesco于下一年委托Lazzaro Baldi与Ciro Ferri为Urban VIII生平十二幅挂毯创作图稿和纸本草图；未关联到本身份组的S2关系候选。",
        ),
        "name_rows": [
            ("索引姓名", "Baldi, Lazzaro", "S1，B.csv#12"),
            ("正文全名", "Lazzaro Baldi", "S2，第2章第VII节，p.60，L28"),
        ],
        "relation_ids": [],
        "description_zh": (
            "本卡登记书后索引主条“Baldi, Lazzaro”及第2章第60页正文具名的Lazzaro Baldi；"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Baldi, Lazzaro” and Lazzaro Baldi named in Chapter 2 on page 60; "
            "the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell称Francesco委托Baldi与Ciro Ferri为Urban VIII生平的十二幅挂毯创作图稿和纸本草图；此委托事实留供S6反向关系审查，本卡不新增正式关系。"
        ),
        "context_en": (
            "Haskell says Francesco commissioned drawings and cartoons from Baldi and Ciro Ferri for a twelve-tapestry series on the life of Urban VIII; "
            "this commission statement remains for the S6 reverse relation review, and no formal relation is added here."
        ),
    },
    {
        "candidate": "cand-0179",
        "group": "new-person:baccio-bandinelli-7015a2f061",
        "ku": "units/persons/baccio-bandinelli",
        "card": "04-knowledge/units/persons/baccio-bandinelli.md",
        "name_zh": "巴乔·班迪内利",
        "name_en": "Baccio Bandinelli",
        "index_entry": "B.csv#26",
        "index_name": "Bandinelli, Baccio",
        "index_page": "103",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
            "第4章第II节，印刷页103，行47",
            "line 47; print p. 103",
            "some little sketches by Baccio Bandinelli or Parmigianino.",
            "Haskell转引Galileo关于Tasso与Ariosto的嵌套引文，其中以Bandinelli或Parmigianino举作假设性草图作者；引文不是具体作品清单。",
        ),
        "name_rows": [
            ("索引姓名", "Bandinelli, Baccio", "S1，B.csv#26"),
            ("嵌套引文中的姓名", "Baccio Bandinelli", "S2，第4章第II节，p.103，L47"),
        ],
        "relation_ids": ["st-chp4-sec-ii-l46-51-galileo-orlando-furioso-imagery"],
        "description_zh": (
            "本卡登记书后索引主条“Bandinelli, Baccio”及第4章第103页Galileo嵌套引文中的Baccio Bandinelli；"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Bandinelli, Baccio” and Baccio Bandinelli named in Galileo’s nested quotation in Chapter 4 on page 103; "
            "the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Galileo的引文把《Orlando Furioso》想象为珍宝室和画廊，并将Bandinelli或Parmigianino的草图作为假设性对照；不把草图认作现存作品或确定归属。"
        ),
        "context_en": (
            "Galileo’s quotation imagines Orlando Furioso as a treasure room and gallery and uses sketches by Bandinelli or Parmigianino as a hypothetical contrast; "
            "no extant work or definite attribution is inferred."
        ),
    },
]

if __name__ == "__main__":
    raise SystemExit(registrar.main())
