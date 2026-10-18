from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_s_index_endpoints_schut_segala_serlio_skala_20261018 as registrar  # noqa: E402

registrar.ANCHOR = "s4-vleughels-wael-wagner-webster-person-endpoints-20261018"
registrar.PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    "s4-vleughels-wael-wagner-webster-person-endpoints-20261018"
)
registrar.BATCH_TITLE = "Vleughels、de Wael、Wagner与Webster四组人物端点"
registrar.BATCH_PROCESS_NOTE = (
    "四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和9条source_backed姓名字段。"
    "Nicolas Vleughels的全名取自索引，正文p.285与p.343脚注均只写Vleughels；Carriera会面名单不含个别细节，"
    "Zanetti受赠者名单也不对应具体纸张。Jean-Baptiste de Wael的p.208引文OCR作peasant Use，S2按页图校读为life；"
    "版画未逐件题名或定年，脚注3仍待查。Joseph Wagner的p.340两条陈述分别记录1742年开店及店铺对印刷业者的重要性；"
    "S2页图校正.to中的OCR多余句点，并确认脚注4不回指国籍或开店年份；店铺名称、地址和精确类型仍未确定。"
    "John Webster依据索引及p.98脚注登记；《The White Devil》的影响说法归于Haskell，未作独立评价。"
    "六条S2关系候选继续留待S6；无外部来源、formal relation或backlog写入。"
)
registrar.BATCH_RESULT_NOTE = (
    "；6条S2关系候选继续待S6；Vleughels两份集体名单均不分配到单件或个别会面，"
    "de Wael的life为页图校读，Wagner店铺身份与Webster影响说均保留来源限定；未新增正式关系或外部来源。"
)
registrar.TARGETS = [
    {
        "candidate": "cand-2789",
        "group": "new-person:nicolas-vleughels-f1b8031c61",
        "ku": "units/persons/nicolas-vleughels",
        "card": "04-knowledge/units/persons/nicolas-vleughels.md",
        "name_zh": "尼古拉·弗勒赫尔",
        "name_en": "Nicolas Vleughels",
        "index_entry": "UVWXYZ.csv#126",
        "index_name": "Vleughels, Nicolas",
        "index_page": "285, 343n",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/10_CHP-10_intro.md",
                "第10章引言，印刷页285，行186",
                "line 186; print p. 285",
                "She met Rigaud and Watteau, both of whom expressed their deep admiration, and all the other artists and connoisseurs—Coypel, Vleughels, Oppenord, de Troy, Mariette.",
                "Haskell将Vleughels列入Rosalba Carriera所遇艺人与鉴赏家的集体名单；没有提供单独会面细节。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/13_CHP-13_intro.md",
                "第13章引言脚注3，印刷页343，行237",
                "line 237; print p. 343, note 3",
                "3 Among these were Mariette, Crozat, Vleughels, the Duke of Devonshire, Sir Andrew Fountaine, Dr Richard Mead, Joseph Smith, Rosalba Carriera and Zaccaria Sagredo.",
                "Haskell在Zanetti赠送画页的受赠者名单中列出Vleughels；“among these”不说明哪一张画页赠予哪一人。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Vleughels, Nicolas", "S1，UVWXYZ.csv#126"),
            ("正文姓氏", "Vleughels", "S2，第10章引言，p.285，L186"),
            ("脚注姓氏", "Vleughels", "S2，第13章引言脚注3，p.343，L237"),
        ],
        "relation_ids": [
            "st-chp10-p285-carriera-met-vleughels",
            "st-chp13-p343-notes-note3-named-dedicatees",
        ],
        "description_zh": (
            "本卡登记书后索引主条“Vleughels, Nicolas”及第10章第285页、第13章第343页脚注中的“Vleughels”。"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Vleughels, Nicolas” and “Vleughels” in Chapter 10, page 285, and a Chapter 13 footnote on page 343. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell将Vleughels列入Carriera所遇艺人与鉴赏家的集体名单；另一脚注将他列入Zanetti画页受赠者名单，"
            "但不对应具体纸张。两处均不提供个别会面或逐件赠送细节；两条关系候选留待S6。"
        ),
        "context_en": (
            "Haskell lists Vleughels in a collective list of artists and connoisseurs Carriera met, and in a footnote list of recipients of Zanetti’s sheets. "
            "The latter does not map particular sheets to individuals, and neither passage gives individual encounter or gift details. "
            "Both relation candidates remain for S6."
        ),
    },
    {
        "candidate": "cand-2795",
        "group": "new-person:baptiste-de-jean-wael-5ccecc0733",
        "ku": "units/persons/jean-baptiste-de-wael",
        "card": "04-knowledge/units/persons/jean-baptiste-de-wael.md",
        "name_zh": "让-巴蒂斯特·德·瓦尔",
        "name_en": "Jean-Baptiste de Wael",
        "index_entry": "UVWXYZ.csv#132",
        "index_name": "Wael, Jean-Baptiste de",
        "index_page": "208",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/08_CHP-8_sec_i.md",
            "第8章第I节，印刷页208，行55",
            "line 55; print p. 208",
            "when Jean-Baptiste de Wael dedicated to him a set of prints showing scenes from peasant Use",
            "Haskell称Jean-Baptiste de Wael赠给Roomer一组描绘农民生活的版画；OCR转录为Use，S2记录页图校读为life。版画未逐件题名或定年，脚注3仍待查。",
        ),
        "name_rows": [
            ("索引姓名", "Wael, Jean-Baptiste de", "S1，UVWXYZ.csv#132"),
            ("正文全名", "Jean-Baptiste de Wael", "S2，第8章第I节，p.208，L55"),
        ],
        "relation_ids": ["st-chp8-p208-de-wael-dedicated-print-series"],
        "description_zh": (
            "本卡登记书后索引主条“Wael, Jean-Baptiste de”及第8章第I节第208页具名的Jean-Baptiste de Wael。"
            "Haskell称他赠给Roomer一组描绘农民生活的版画；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Wael, Jean-Baptiste de” and Jean-Baptiste de Wael named on page 208 of Chapter 8, section I. "
            "Haskell says he dedicated a set of prints showing peasant life to Roomer; the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "原书文本OCR作“peasant Use”，S2据页图校读为“peasant life”。版画没有逐件题名或日期，相关脚注3仍待查；"
            "委托／赠献关系候选留待S6。"
        ),
        "context_en": (
            "The book text OCR reads “peasant Use”; S2 records “peasant life” from the page image. The prints are not individually titled or dated, "
            "and footnote 3 remains pending. The dedication candidate remains for S6."
        ),
    },
    {
        "candidate": "cand-2796",
        "group": "new-person:german-joseph-wagner-joseph-wagner-029a33bcd8",
        "ku": "units/persons/joseph-wagner-printseller",
        "card": "04-knowledge/units/persons/joseph-wagner-printseller.md",
        "name_zh": "约瑟夫·瓦格纳",
        "name_en": "Joseph Wagner",
        "index_entry": "UVWXYZ.csv#133",
        "index_name": "Wagner, Joseph",
        "index_page": "340",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/13_CHP-13_intro.md",
                "第13章引言，印刷页340，行86",
                "line 86; print p. 340",
                "the German Joseph Wagner, who opened a shop in 1742",
                "Haskell将Joseph Wagner称为德国人，并称其于1742年开店；均为书内叙述。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/13_CHP-13_intro.md",
                "第13章引言，印刷页340，行86",
                "line 86; print p. 340",
                "which was of the utmost significance.to printers",
                "Haskell称该店对印刷业者极其重要；OCR在to之前多出句点，S2据页图校正。店铺名称、地址和精确类型未给出。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Wagner, Joseph", "S1，UVWXYZ.csv#133"),
            ("正文全名与描述", "German Joseph Wagner", "S2，第13章引言，p.340，L86"),
        ],
        "relation_ids": [
            "st-chp13-p340-wagner-german-and-opened-shop-1742",
            "st-chp13-p340-wagner-shop-significant-to-printers",
        ],
        "description_zh": (
            "本卡登记书后索引主条“Wagner, Joseph”及第13章第340页具名的German Joseph Wagner。"
            "Haskell称他于1742年开设一间印刷品商店；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Wagner, Joseph” and Joseph Wagner named on page 340 of Chapter 13. "
            "Haskell describes him as German and says he opened a printseller’s shop in 1742; the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell称Wagner于1742年开店，并称该店对印刷业者极其重要；S2据页图校正“significance.to printers”中的OCR多余句点。"
            "该店的名称、地址和精确类型未确定；脚注4不回指国籍或开店日期，两条关系候选留待S6。"
        ),
        "context_en": (
            "Haskell says Wagner opened a shop in 1742 and that it was highly significant to printers; S2 records the extra OCR full stop "
            "in “significance.to printers” as corrected against the page image. The shop’s name, address, and exact type are not established. "
            "Footnote 4 does not refer back to the nationality or opening date; both relation candidates remain for S6."
        ),
    },
    {
        "candidate": "cand-2805",
        "group": "new-person:john-webster-6bdfe375fe",
        "ku": "units/persons/john-webster-playwright",
        "card": "04-knowledge/units/persons/john-webster-playwright.md",
        "name_zh": "约翰·韦伯斯特",
        "name_en": "John Webster",
        "index_entry": "UVWXYZ.csv#142",
        "index_name": "Webster, John",
        "index_page": "",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_i.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/04_CHP-4_sec_i.md",
            "第4章第I节脚注3，印刷页98，行66",
            "line 66; print p. 98, note 3",
            "3 His grandfather Paolo Giordano I had had his wife Isabella de’ Medici strangled—an episode which inspired Webster’s White Devil.",
            "Haskell脚注称Paolo Giordano I之妻Isabella de’ Medici被勒死的事件启发了Webster的《The White Devil》；影响说法未独立评价。",
        ),
        "name_rows": [
            ("索引姓名", "Webster, John", "S1，UVWXYZ.csv#142；索引页码栏为空"),
            ("脚注姓名", "Webster", "S2，第4章第I节脚注3，p.98，L66"),
        ],
        "relation_ids": ["st-chp4-sec-i-l42-67-fn98-white-devil-inspiration"],
        "description_zh": (
            "本卡登记书后索引主条“Webster, John”；该索引行未列页码。第4章第I节脚注称John Webster的《The White Devil》。"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Webster, John,” whose page field is blank. A footnote in Chapter 4, section I, "
            "refers to John Webster’s The White Devil. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell脚注称Isabella de’ Medici被勒死的事件启发了Webster的《The White Devil》；这是作者的文学影响判断，未独立评价。"
            "该关系候选留待S6。"
        ),
        "context_en": (
            "Haskell’s footnote says Isabella de’ Medici’s strangling inspired Webster’s The White Devil. This is the author’s literary-influence claim, "
            "not independently assessed; the relation candidate remains for S6."
        ),
    },
]

if __name__ == "__main__":
    raise SystemExit(registrar.main())
