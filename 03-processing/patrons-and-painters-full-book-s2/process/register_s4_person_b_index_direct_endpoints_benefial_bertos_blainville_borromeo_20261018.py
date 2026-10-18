from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_s_index_endpoints_schut_segala_serlio_skala_20261018 as registrar  # noqa: E402

registrar.ANCHOR = "s4-benefial-bertos-blainville-borromeo-person-endpoints-20261018"
registrar.PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    "s4-benefial-bertos-blainville-borromeo-person-endpoints-20261018"
)
registrar.BATCH_TITLE = "Benefial、Bertos、Blainville与Borromeo四组人物端点"
registrar.BATCH_PROCESS_NOTE = (
    "四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和8条source_backed姓名字段。"
    "Marco Benefial的索引全名与正文跨行姓名相合；第三幅Agrippina题材画及其转赠均保留为Haskell的叙述和解释，Bottari引文未独立查阅。"
    "Francesco Bertos依据索引全名及Schulenburg收藏中的姓氏称名登记；大型青铜群组含Schulenburg骑马像，但原文未逐件分配购入或委托方式。"
    "Monsieur de Blainville在第9章p.245注1与第14章p.358注1均引Blainville卷I第492页，作为同一书内人物身份的跨章锚点；未见给定名。第21章书目所列Blainville旅行书对应的archive候选cand-10390仍为S3 undecided，不登记、不并入人物KU。"
    "Cardinal Federico Borromeo只按索引及第6章正文称名登记；Haskell对圣彼得宝座的视觉比较不解释为Borromeo直接影响Bernini。"
    "三条明确S2关系候选留待S6；无外部来源、正式关系或backlog写入。"
)
registrar.BATCH_RESULT_NOTE = (
    "；Benefial第三幅Agrippina题材画、Bertos青铜群组及Borromeo影响的比较语境三条S2关系候选留待S6；"
    "Blainville跨章两处引文同指卷I第492页，archive候选cand-10390继续undecided并与人物组分开；不新增正式关系或外部来源。"
)
registrar.TARGETS = [
    {
        "candidate": "cand-0288",
        "group": "new-person:benefial-marco-8c167dc92b",
        "ku": "units/persons/marco-benefial",
        "card": "04-knowledge/units/persons/marco-benefial.md",
        "name_zh": "马尔科·贝内菲亚尔",
        "name_en": "Marco Benefial",
        "index_entry": "B.csv#135",
        "index_name": "Benefial, Marco",
        "index_page": "294",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/10_CHP-10_intro.md",
            "第10章引言，印刷页294，行295–296",
            "lines 295–296; print p. 294",
            "a third, painted by the Roman Marco\nBenefial, arrived in Dresden, his son clearly felt that its possibilities had been exhausted and he gave the picture away.",
            "Haskell称第三幅Agrippina题材画由Roman Marco Benefial绘制并到达Dresden，随后由前文所指Augustus III之子转赠；“clearly felt”为Haskell的解释，注3所引Bottari未独立查阅。",
        ),
        "name_rows": [
            ("索引姓名", "Benefial, Marco", "S1，B.csv#135"),
            ("正文全名", "Marco Benefial", "S2，第10章引言，p.294，L295–296"),
        ],
        "relation_ids": ["st-chp10-p294-benefial-third-version-given-away"],
        "description_zh": (
            "本卡登记书后索引主条“Benefial, Marco”及第10章第294页跨行写出的Marco Benefial；"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Benefial, Marco” and Marco Benefial named across a line break in Chapter 10 on page 294; "
            "the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell称第三幅Agrippina题材画由Marco Benefial绘制并到达Dresden，随后被前文所指Augustus III之子转赠；“clearly felt”是作者解释，Bottari页码未独立查阅。"
        ),
        "context_en": (
            "Haskell says a third Agrippina-subject painting by Marco Benefial arrived in Dresden and was later given away by the son identified in context as Augustus III’s; "
            "“clearly felt” is Haskell’s interpretation, and the cited Bottari pages were not independently consulted."
        ),
    },
    {
        "candidate": "cand-0368",
        "group": "new-person:bertos-francesco-9e9f9df7ff",
        "ku": "units/persons/francesco-bertos",
        "card": "04-knowledge/units/persons/francesco-bertos.md",
        "name_zh": "弗朗切斯科·贝尔托斯",
        "name_en": "Francesco Bertos",
        "index_entry": "B.csv#215",
        "index_name": "Bertos, Francesco",
        "index_page": "312",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
            "第10章第II节，印刷页312，行24",
            "line 24; print p. 312",
            "were a large group of bronzes by Bertos (including an equestrian portrait of himself)",
            "Haskell列出Schulenburg作品中的大型Bertos青铜群组，包括Schulenburg本人的骑马像；该句同时提及购藏与偶有委托，但未逐件指定来源。",
        ),
        "name_rows": [
            ("索引姓名", "Bertos, Francesco", "S1，B.csv#215"),
            ("正文姓氏", "Bertos", "S2，第10章第II节，p.312，L24"),
        ],
        "relation_ids": ["st-chp10-p312-bertos-bronzes-and-equestrian-portrait"],
        "description_zh": (
            "本卡登记书后索引主条“Bertos, Francesco”及第10章第312页正文称名Bertos；"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Bertos, Francesco” and Bertos named in Chapter 10 on page 312; "
            "the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell称Schulenburg作品中有大型Bertos青铜群组，包括Schulenburg本人的骑马像；原文未将购入或委托方式逐件分配给群组成员。"
        ),
        "context_en": (
            "Haskell describes a large group of Bertos bronzes among Schulenburg’s works, including an equestrian portrait of Schulenburg himself; "
            "the passage does not assign purchase or commission status to individual bronzes."
        ),
    },
    {
        "candidate": "cand-0378",
        "group": "new-person:blainville-de-monsieur-d5653ab60b",
        "ku": "units/persons/monsieur-de-blainville",
        "card": "04-knowledge/units/persons/monsieur-de-blainville.md",
        "name_zh": "布兰维尔先生",
        "name_en": "Monsieur de Blainville",
        "index_entry": "B.csv#225",
        "index_name": "Blainville, Monsieur de",
        "index_page": "245n",
        "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/09_CHP-9_intro.md",
                "第9章引言脚注1，印刷页245",
                "line 324; print p. 245, note 1",
                "At the other is that of Blainville who went out of his way to deny reports that the nobles were unapproachable (I, p. 492)",
                "Haskell在第9章脚注转述Blainville否认威尼斯贵族不可接近，并引Blainville卷I第492页。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/14_CHP-14_intro.md",
                "第14章引言脚注1，印刷页358",
                "line 208; print p. 358, note 1",
                "Blainville, I, p. 492, disliked this mixture but admitted that 'some people’ found it attractive.",
                "Haskell在第14章脚注转述Blainville不喜欢该混合风格、但承认有人认为有吸引力；仍引卷I第492页，原卷未独立查阅。",
            ),
        ],
        "name_rows": [
            ("索引姓名与称号", "Blainville, Monsieur de", "S1，B.csv#225"),
            ("脚注称名", "Blainville", "S2，第9章引言，p.245注1，L324；第14章引言，p.358注1，L208"),
        ],
        "relation_ids": [],
        "description_zh": (
            "本卡登记书后索引主条“Blainville, Monsieur de”及第9、14章脚注中的Blainville；"
            "来源未给出其名字，中文显示名是对索引称谓的工作译名。"
        ),
        "description_en": (
            "This card records the index entry “Blainville, Monsieur de” and Blainville named in Chapter 9 and Chapter 14 footnotes; "
            "the source gives no first name, and the Chinese display name is a working translation of the indexed form."
        ),
        "context_zh": (
            "两章脚注均引Blainville卷I第492页，构成同一书内人物锚点；Haskell分别转述其对威尼斯贵族可接近性的评论及对混合风格的看法。"
            "姓名仍限于索引称谓，未补写生平或给定名。"
        ),
        "context_en": (
            "Both chapter footnotes cite volume I, page 492 of Blainville, providing a shared book-level identity anchor; "
            "Haskell reports his comments on access to Venetian nobles and on a stylistic mixture. The name remains at the indexed form, "
            "with no first name or biography added."
        ),
    },
    {
        "candidate": "cand-0403",
        "group": "new-person:borromeo-federico-ad70b15852",
        "ku": "units/persons/federico-borromeo-cardinal",
        "card": "04-knowledge/units/persons/federico-borromeo-cardinal.md",
        "name_zh": "费德里科·博罗梅奥枢机",
        "name_en": "Cardinal Federico Borromeo",
        "index_entry": "B.csv#250",
        "index_name": "Borromeo, Cardinal Federico",
        "index_page": "151",
        "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/06_CHP-6_sec_i.md",
            "第6章第I节，印刷页151，行65",
            "line 65; print p. 151",
            "such nervous religious energy had not been seen in Italian art since the work of those Milanese painters who had been inspired by Cardinal Federico Borromeo in the early years of the century.",
            "Haskell以受Federico Borromeo启发的米兰画家作为Bernini圣彼得宝座视觉能量的比较参照；这是作者的比较，不是对Bernini直接师承或影响的断言。",
        ),
        "name_rows": [
            ("索引姓名与称号", "Borromeo, Cardinal Federico", "S1，B.csv#250"),
            ("正文全名与称号", "Cardinal Federico Borromeo", "S2，第6章第I节，p.151，L65"),
        ],
        "relation_ids": ["st-chp6-p151-chair-doctors-and-milanese-comparison"],
        "description_zh": (
            "本卡登记书后索引主条“Borromeo, Cardinal Federico”及第6章第151页正文称名Cardinal Federico Borromeo；"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Borromeo, Cardinal Federico” and Cardinal Federico Borromeo named in Chapter 6 on page 151; "
            "the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell以受Borromeo启发的米兰画家作为圣彼得宝座宗教能量的比较参照；不据此断言Bernini直接受Borromeo或这些画家影响。"
        ),
        "context_en": (
            "Haskell uses Milanese painters inspired by Borromeo as a comparison for the Chair’s religious energy; "
            "this does not establish direct influence on Bernini by Borromeo or those painters."
        ),
    },
]

if __name__ == "__main__":
    raise SystemExit(registrar.main())
