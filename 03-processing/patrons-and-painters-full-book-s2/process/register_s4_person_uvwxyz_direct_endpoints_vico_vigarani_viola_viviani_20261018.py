from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_s_index_endpoints_schut_segala_serlio_skala_20261018 as registrar  # noqa: E402

registrar.ANCHOR = "s4-vico-vigarani-viola-viviani-person-endpoints-20261018"
registrar.PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    "s4-vico-vigarani-viola-viviani-person-endpoints-20261018"
)
registrar.BATCH_TITLE = "Vico、Vigarani、Viola与Viviani四组人物端点"
registrar.BATCH_PROCESS_NOTE = (
    "四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和8条source_backed姓名字段。"
    "Giambattista Vico依据UVWXYZ.csv全名及第13章脚注中的姓氏登记；脚注引用的1728年书信及Fisch与Bergin第184页未独立查阅，"
    "Conti姓氏端点仍有歧义，页图对1728年后标点的校读按S2保留。Gaspare Vigarani依据索引与p.185正文登记；"
    "原句对移往Tuileries的主体表达压缩，不据此断言剧场建成，脚注Hautecœur页码未独立查阅。"
    "Domenico Viola依据索引和p.136正文登记为Haskell所称Cerquozzi两位密友之一，不补入原文未给的日期或语境。"
    "Vincenzo Viviani依据索引全名与p.229正文姓氏登记；正文仅称Viviani，不扩展其名字或经历。"
    "四条S2关系候选留待S6；无外部身份来源、formal relation或backlog写入。"
)
registrar.BATCH_RESULT_NOTE = (
    "；4条S2关系候选继续待S6；Vico脚注所引材料未独立核读且Conti身份仍待决，"
    "Vigarani条目不推定剧场建成，Viviani正文保留姓氏层级；未新增正式关系或外部来源。"
)
registrar.TARGETS = [
    {
        "candidate": "cand-2770",
        "group": "new-person:giambattista-vico-fecfefaafe",
        "ku": "units/persons/giambattista-vico",
        "card": "04-knowledge/units/persons/giambattista-vico.md",
        "name_zh": "詹巴蒂斯塔·维柯",
        "name_en": "Giambattista Vico",
        "index_entry": "UVWXYZ.csv#106",
        "index_name": "Vico, Giambattista",
        "index_page": "",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/13_CHP-13_intro.md",
            "第13章引言脚注1，印刷页337，行203",
            "line 203; print p. 337, note 1",
            "Conti’s letter to Vico of 1728. published by Fisch and Bergin, p. 184",
            "Haskell脚注提及Conti致Vico的1728年信，并称其由Fisch与Bergin刊于第184页；脚注原文在1728年后出现句点，S2据页图记录为OCR转录误差，信件和引用页未独立查阅。",
        ),
        "name_rows": [
            ("索引姓名", "Vico, Giambattista", "S1，UVWXYZ.csv#106；索引页码栏为空"),
            ("脚注姓名", "Vico", "S2，第13章引言脚注1，p.337，L203"),
        ],
        "relation_ids": ["st-chp13-p337-note1-conti-letter-to-vico-1728"],
        "description_zh": (
            "本卡登记书后索引主条“Vico, Giambattista”；该索引行未列页码。第13章引言脚注提到一封1728年写给Vico的信。"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Vico, Giambattista,” whose page field is blank. A footnote in the Chapter 13 introduction "
            "mentions a letter to Vico dated 1728. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell脚注称Conti致Vico的1728年信由Fisch与Bergin刊于第184页；脚注中的Conti仅有姓氏，身份仍有歧义，"
            "书信及所引出版页未独立查阅。正文转录在1728年后有句点，S2据页图校读为无句点；该关系候选留待S6。"
        ),
        "context_en": (
            "Haskell’s footnote says a 1728 letter from Conti to Vico was published by Fisch and Bergin on page 184. Conti is given by surname only "
            "and remains ambiguous; neither the letter nor the cited publication page was independently consulted. The transcription has a full stop "
            "after 1728, which S2 records as absent from the page image. The relation candidate remains for S6."
        ),
    },
    {
        "candidate": "cand-2774",
        "group": "new-person:gaspare-vigarani-7728563f06",
        "ku": "units/persons/gaspare-vigarani",
        "card": "04-knowledge/units/persons/gaspare-vigarani.md",
        "name_zh": "加斯帕雷·维加拉尼",
        "name_en": "Gaspare Vigarani",
        "index_entry": "UVWXYZ.csv#110",
        "index_name": "Vigarani, Gaspare",
        "index_page": "185",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/07_CHP-7_sec_i.md",
            "第7章第I节，印刷页185，行211",
            "line 211; print p. 185",
            "Gaspare Vigarani was summoned from Mantua in 1659 to build a theatre in Mazarin’s palace, but found that there was not enough space and moved to the Tuileries instead.3",
            "Haskell称Vigarani于1659年从Mantua被召至Mazarin宫殿建剧场，空间不足后移至Tuileries；原文未确认剧场建成，脚注所引Hautecœur页码未独立查阅。",
        ),
        "name_rows": [
            ("索引姓名", "Vigarani, Gaspare", "S1，UVWXYZ.csv#110"),
            ("正文全名", "Gaspare Vigarani", "S2，第7章第I节，p.185，L211"),
        ],
        "relation_ids": ["st-chp7-p185-i26"],
        "description_zh": (
            "本卡登记书后索引主条“Vigarani, Gaspare”及第7章第I节第185页具名的Gaspare Vigarani。"
            "Haskell记述他于1659年受召为Mazarin宫殿的剧场项目工作；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Vigarani, Gaspare” and Gaspare Vigarani named on page 185 of Chapter 7, section I. "
            "Haskell reports that he was summoned in 1659 for a theatre project at Mazarin’s palace; the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell称Vigarani受召从Mantua到Mazarin宫殿建剧场，发现空间不足后“移至Tuileries”。原句对移动主体表达压缩，"
            "不据此断言剧场在Tuileries建成；脚注引文页码未独立查阅，关系候选留待S6。"
        ),
        "context_en": (
            "Haskell says Vigarani was summoned from Mantua to build a theatre at Mazarin’s palace and, after finding insufficient space, “moved to the Tuileries.” "
            "The sentence compresses what moved and does not establish that a theatre was completed there. The cited footnote pages were not independently consulted; "
            "the relation candidate remains for S6."
        ),
    },
    {
        "candidate": "cand-2776",
        "group": "new-person:domenico-viola-9c07bd68a7",
        "ku": "units/persons/domenico-viola",
        "card": "04-knowledge/units/persons/domenico-viola.md",
        "name_zh": "多梅尼科·维奥拉",
        "name_en": "Domenico Viola",
        "index_entry": "UVWXYZ.csv#112",
        "index_name": "Viola, Domenico",
        "index_page": "136",
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_iii.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/05_CHP-5_sec_iii.md",
            "第5章第III节，印刷页136，行40",
            "line 40; print p. 136",
            "His two closest friends were painters—Domenico Viola and Giacinto Brandi",
            "Haskell称Cerquozzi最亲密的两位朋友是画家Domenico Viola与Giacinto Brandi；来源未提供日期或更多关系语境。",
        ),
        "name_rows": [
            ("索引姓名", "Viola, Domenico", "S1，UVWXYZ.csv#112"),
            ("正文全名", "Domenico Viola", "S2，第5章第III节，p.136，L40"),
        ],
        "relation_ids": ["st-chp5-p136-cerquozzi-close-friend-domenico-viola"],
        "description_zh": (
            "本卡登记书后索引主条“Viola, Domenico”及第5章第III节第136页具名的Domenico Viola。"
            "Haskell称他为Cerquozzi两位最亲密朋友之一，并列为画家；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Viola, Domenico” and Domenico Viola named on page 136 of Chapter 5, section III. "
            "Haskell identifies him as a painter and one of Cerquozzi’s two closest friends; the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell称Cerquozzi最亲密的两位朋友是画家Domenico Viola与Giacinto Brandi；原文未给出日期或进一步语境。"
            "该朋友关系候选留待S6裁决。"
        ),
        "context_en": (
            "Haskell says Cerquozzi’s two closest friends were the painters Domenico Viola and Giacinto Brandi; the passage gives no dates or further context. "
            "The friendship candidate remains for S6."
        ),
    },
    {
        "candidate": "cand-2788",
        "group": "new-person:vincenzo-viviani-fd372f4147",
        "ku": "units/persons/vincenzo-viviani",
        "card": "04-knowledge/units/persons/vincenzo-viviani.md",
        "name_zh": "温琴佐·维维亚尼",
        "name_en": "Vincenzo Viviani",
        "index_entry": "UVWXYZ.csv#125",
        "index_name": "Viviani, Vincenzo",
        "index_page": "229",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
            "第8章第II节，印刷页229，行218",
            "line 218; print p. 229",
            "Ferdinand was educated by all the most remarkable personalities in a city that was still notable in the intellectual Europe of the day—Viviani, Lorenzini, Redi.",
            "Haskell称Ferdinand曾由Viviani、Lorenzini、Redi等人教育；正文仅给Viviani姓氏，完整名依据索引。",
        ),
        "name_rows": [
            ("索引姓名", "Viviani, Vincenzo", "S1，UVWXYZ.csv#125"),
            ("正文姓氏", "Viviani", "S2，第8章第II节，p.229，L218"),
        ],
        "relation_ids": ["st-chp8-p229-ferdinand-education"],
        "description_zh": (
            "本卡登记书后索引主条“Viviani, Vincenzo”及第8章第II节第229页的“Viviani”。"
            "正文只写姓氏，完整名依索引记录；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Viviani, Vincenzo” and “Viviani” on page 229 of Chapter 8, section II. "
            "The text gives only the surname; the full name is recorded from the index. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell称Ferdinand由Viviani、Lorenzini、Redi等人教育；本段只写Viviani姓氏，不以该段扩写姓名或经历。"
            "教育关系候选留待S6。"
        ),
        "context_en": (
            "Haskell says Ferdinand was educated by Viviani, Lorenzini, Redi, and others. This passage gives only Viviani’s surname and does not support "
            "additional personal details. The education candidate remains for S6."
        ),
    },
]

if __name__ == "__main__":
    raise SystemExit(registrar.main())
