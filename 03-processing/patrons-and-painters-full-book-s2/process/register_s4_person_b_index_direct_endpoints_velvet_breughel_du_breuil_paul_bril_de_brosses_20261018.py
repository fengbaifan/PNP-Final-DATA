from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_s_index_endpoints_schut_segala_serlio_skala_20261018 as registrar  # noqa: E402

registrar.ANCHOR = "s4-b-index-velvet-breughel-du-breuil-paul-bril-de-brosses-20261018"
registrar.PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    "s4-b-index-velvet-breughel-du-breuil-paul-bril-de-brosses-20261018"
)
registrar.BATCH_TITLE = "Velvet Breughel、du Breuil、Paul Brill与Charles de Brosses四组人物端点"
registrar.BATCH_PROCESS_NOTE = (
    "四组S3 new身份组登记为4张KU卡、4条候选映射和8条source_backed姓名字段。"
    "Velvet Breughel按Getty ULAN 500007095的名称变体映射到Jan Brueghel the Elder；Paul Brill按Getty ULAN 500005652的名称变体映射到Paul Bril；"
    "两条外部身份记录仅支持名称与人物身份，不验证Roomer藏画归属。Toussaint du Breuil保留Haskell对法国绘画政策结果的评价限定。"
    "Charles de Brosses以索引主项及书目全名登记；第10章p.292与p.311的S2人物候选cand-9436在下一条S3复核中并入本KU，"
    "而archive候选cand-9437、cand-9879、cand-11268继续各自保留其书目／引文定位粒度。"
    "四条直接S2关系候选留待S6；本批不登记正式关系或backlog。"
)
registrar.BATCH_RESULT_NOTE = (
    "；Velvet Breughel和Paul Brill的Getty ULAN身份记录分别列于alignment.csv，规范显示名采用Jan Brueghel the Elder与Paul Bril；"
    "de Brosses的章10人物候选cand-9436随后复核为本KU的same，章10引文定位及第21章书目对象保持archive类型。"
    "四条直接关系候选继续留待S6，不新增正式关系。"
)
book_source = registrar.book_source

registrar.TARGETS = [
    {
        "candidate": "cand-0449",
        "group": "new-person:breughel-velvet-e4c1642729",
        "ku": "units/persons/jan-brueghel-the-elder",
        "card": "04-knowledge/units/persons/jan-brueghel-the-elder.md",
        "name_zh": "扬·布鲁盖尔（老）",
        "name_en": "Jan Brueghel the Elder",
        "index_entry": "B.csv#296",
        "index_name": "Breughel, Velvet",
        "index_page": "206",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "book_source": book_source(
            "02-sources/02-Markdown/08_CHP-8_sec_i.md",
            "第8章第I节，印刷页206，行34–35",
            "line 35; print p. 206",
            "Velvet Breughel,",
            "Haskell在Roomer藏画作者的开放名单中列出Velvet Breughel；“数百件”指多人作品集合。",
        ),
        "name_rows": [
            ("索引原名", "Breughel, Velvet", "S1，B.csv#296"),
            ("正文别称", "Velvet Breughel", "S2，第8章第I节，p.206，L35"),
        ],
        "relation_ids": ["st-chp8-p206-roomer-owned-hundreds-by-flemish-artists"],
        "external_identities": [
            {
                "source": "Getty ULAN",
                "id": "500007095",
                "resolution_note": (
                    "Getty Research ULAN 500007095; https://www.getty.edu/vow/ULANFullDisplay?find=500032603&nation=&page=1&role=&subjectid=500007095. "
                    "The preferred person record is Brueghel, Jan, the elder; its variant names include the exact form Velvet Breughel. "
                    "Used to resolve the book's nickname to Jan Brueghel the Elder only."
                ),
            }
        ],
        "s3_identity_note": (
            "Getty Research ULAN 500007095（https://www.getty.edu/vow/ULANFullDisplay?find=500032603&nation=&page=1&role=&subjectid=500007095，访问日期2026-10-18）"
            "的preferred记录为Brueghel, Jan, the elder，variant names明确列有Velvet Breughel；与索引B.csv#296及正文p.206称名相合。"
            "本库没有该规范身份的既有person KU，故候选仍为new，S4以Jan Brueghel the Elder登记；不与既有Abram Breughel人物卡合并。"
        ),
        "identity_section": (
            "### 身份与外部链接\n\n"
            "- Getty Research Institute，Union List of Artist Names："
            "[Jan Brueghel the Elder（ULAN 500007095）](https://vocab.getty.edu/page/ulan/500007095)。"
            "记录列有“Velvet Breughel”名称变体；支持别称与人物身份对齐，Roomer藏画范围仍据Haskell原文。"
        ),
        "description_zh": (
            "本卡将书后索引主项“Breughel, Velvet”及第8章第206页正文别称“Velvet Breughel”"
            "按Getty ULAN名称变体对齐到Jan Brueghel the Elder。书中原有称名保留为姓名证据；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card aligns the index entry “Breughel, Velvet” and the Chapter 8, page 206 form “Velvet Breughel” "
            "with Jan Brueghel the Elder through a Getty ULAN name variant. The book's forms remain as name evidence. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell将其列入Roomer藏画的开放作者名单；数百件是多人作品总量，不归给该人物个人。"
            "同一名单另有Abram Breughel相关记录，但本候选的别称由ULAN对应Jan Brueghel the Elder；没有依据把两张人物卡合并。"
        ),
        "context_en": (
            "Haskell includes him in an open list of makers represented in Roomer's collection; several hundred is the collective total, not an individual count. "
            "Abram Breughel is represented elsewhere in the book, but ULAN resolves this candidate's nickname to Jan Brueghel the Elder; "
            "there is no basis for merging the two person records."
        ),
    },
    {
        "candidate": "cand-0450",
        "group": "new-person:breuil-du-toussaint-49211ac1bb",
        "ku": "units/persons/toussaint-du-breuil",
        "card": "04-knowledge/units/persons/toussaint-du-breuil.md",
        "name_zh": "图桑·迪布勒伊",
        "name_en": "Toussaint du Breuil",
        "index_entry": "B.csv#297",
        "index_name": "Breuil, Toussaint du",
        "index_page": "173",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
        "book_source": book_source(
            "02-sources/02-Markdown/07_CHP-7_sec_i.md",
            "第7章第I节，印刷页173，行42",
            "line 42; print p. 173",
            "such as Toussaint du Breuil and Ambroise Dubois.",
            "Haskell将Toussaint du Breuil与Ambroise Dubois列作后期风格主义画家，并以provincial decoration评价其绘画政策结果。",
        ),
        "name_rows": [
            ("索引姓名", "Breuil, Toussaint du", "S1，B.csv#297"),
            ("正文全名", "Toussaint du Breuil", "S2，第7章第I节，p.173，L42"),
        ],
        "relation_ids": ["st-chp7-p173-i23"],
        "description_zh": (
            "本卡登记书后索引主条“Breuil, Toussaint du”及第7章第173页正文全名Toussaint du Breuil；"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Toussaint du Breuil, indexed as “Breuil, Toussaint du” and named in full in Chapter 7, page 173. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell把他与Ambroise Dubois并列为后期风格主义画家，并评价相关绘画结果为provincial decoration；"
            "该判断保留为作者评价，不扩写成中性事实或个人生平。"
        ),
        "context_en": (
            "Haskell groups him with Ambroise Dubois as a latter-day Mannerist painter and characterizes the painting outcome as provincial decoration; "
            "this remains the author's evaluation and is not expanded into neutral fact or biography."
        ),
    },
    {
        "candidate": "cand-0453",
        "group": "new-person:brill-paul-0242398f04",
        "ku": "units/persons/paul-bril",
        "card": "04-knowledge/units/persons/paul-bril.md",
        "name_zh": "保罗·布里尔",
        "name_en": "Paul Bril",
        "index_entry": "B.csv#300",
        "index_name": "Brill, Paul",
        "index_page": "206",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "book_source": book_source(
            "02-sources/02-Markdown/08_CHP-8_sec_i.md",
            "第8章第I节，印刷页206，行34",
            "line 34; print p. 206",
            "and he owned several hundreds by Paul Brill,",
            "Haskell在Roomer藏画作者开放名单中写作Paul Brill；数百件指多人作品集合。",
        ),
        "name_rows": [
            ("索引姓名", "Brill, Paul", "S1，B.csv#300"),
            ("正文姓名形式", "Paul Brill", "S2，第8章第I节，p.206，L34"),
        ],
        "relation_ids": ["st-chp8-p206-roomer-owned-hundreds-by-flemish-artists"],
        "external_identities": [
            {
                "source": "Getty ULAN",
                "id": "500005652",
                "resolution_note": (
                    "Getty Research ULAN 500005652; https://www.getty.edu/vow/ULANFullDisplay?find=500027565&nation=&page=1&role=&subjectid=500005652. "
                    "The preferred form is Bril, Paul; variant names include Paul Brill and Brill, Paul, matching the book's index and text forms. "
                    "Used for identity and name normalization only."
                ),
            }
        ],
        "s3_identity_note": (
            "Getty Research ULAN 500005652（https://www.getty.edu/vow/ULANFullDisplay?find=500027565&nation=&page=1&role=&subjectid=500005652，访问日期2026-10-18）"
            "preferred为Bril, Paul，variant names含Paul Brill与Brill, Paul；与索引和正文异体拼写相合。"
            "本库没有Paul Bril既有person KU，候选仍为new并以规范英文名登记；该身份核对不验证藏画归属。"
        ),
        "identity_section": (
            "### 身份与外部链接\n\n"
            "- Getty Research Institute，Union List of Artist Names："
            "[Paul Bril（ULAN 500005652）](https://vocab.getty.edu/page/ulan/500005652)。"
            "记录列有Paul Brill名称变体；支持姓名与人物身份对齐，Roomer藏画范围仍据Haskell原文。"
        ),
        "description_zh": (
            "本卡登记书后索引“Brill, Paul”及正文“Paul Brill”，并按Getty ULAN所列名称变体规范为Paul Bril。"
            "书中拼写保留为姓名证据；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index form “Brill, Paul” and the text form “Paul Brill,” normalized to Paul Bril using a Getty ULAN name variant. "
            "The book's spellings remain as name evidence. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell把Paul Brill列入Roomer藏画的开放作者名单；数百件是多人作品总量，不归给单一画家，也不由身份记录验证。"
        ),
        "context_en": (
            "Haskell includes Paul Bril in an open list of makers represented in Roomer's collection; several hundred is the collective total, "
            "not an individual painter's count, and the identity record does not verify the collection claim."
        ),
    },
    {
        "candidate": "cand-0455",
        "group": "new-person:brosses-charles-de-president-73d472266d",
        "ku": "units/persons/charles-de-brosses",
        "card": "04-knowledge/units/persons/charles-de-brosses.md",
        "name_zh": "夏尔·德·布罗斯",
        "name_en": "Charles de Brosses",
        "index_entry": "B.csv#302",
        "index_name": "Brosses, Président Charles De",
        "index_page": "245, 260, 311n",
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
        "book_sources": [
            book_source(
                "02-sources/02-Markdown/09_CHP-9_intro.md",
                "第9章引言，印刷页245，注1正文",
                "line 15; print p. 245, note 1 body",
                "de Brosses sounds plausible when he says (I, p. 129) that in general nobles very rarely received foreigners.",
                "Haskell认为de Brosses关于贵族很少接待外国人的报告听来可信；原引文未独立查阅。",
            ),
            book_source(
                "02-sources/02-Markdown/09_CHP-9_intro.md",
                "第9章引言，印刷页260，行205",
                "line 205; print p. 260",
                "President de Brosses found to be a man ‘d’un esprit et d’un feu surprenants’",
                "Haskell转述President de Brosses对Marco Foscarini的评价；保留引语及转述层级。",
            ),
            book_source(
                "02-sources/02-Markdown/09_CHP-9_intro.md",
                "第9章引言脚注3，印刷页257",
                "line 382; print p. 257, note 3",
                "De Brosses, I, p. 149.",
                "Haskell脚注列出De Brosses卷I第149页；这是书目定位，不表示已读原文。",
            ),
            book_source(
                "02-sources/02-Markdown/09_CHP-9_intro.md",
                "第9章引言脚注1，印刷页260",
                "line 395; print p. 260, note 1",
                "De Brosses, II, p. 39.",
                "Haskell脚注列出De Brosses卷II第39页；这是书目定位，不表示已读原文。",
            ),
            book_source(
                "02-sources/02-Markdown/10_CHP-10_intro.md",
                "第10章引言脚注1，印刷页292",
                "line 554; print p. 292, note 1",
                "1 De Brosses, I, p. 282.",
                "Haskell脚注以De Brosses卷I第282页为Canaletto市场叙述的引文定位；原页未独立查阅。",
            ),
            book_source(
                "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "第10章第II节脚注5，印刷页311",
                "line 278; print p. 311, note 5",
                "5 De Brosses, I, p. 142:",
                "Haskell以De Brosses卷I第142页引文描述Schulenburg；这是经Haskell转引，原卷未独立查阅。",
            ),
            book_source(
                "02-sources/02-Markdown/21_CHP-21Bibliography.md",
                "第21章书目，Brosses条目",
                "line 264; bibliography entry",
                "Brosses, Charles de: Lettres d’Italie",
                "书目将Lettres d’Italie列在Charles de Brosses名下；这是文献作者署名，书本身作为archive对象另行登记。",
            ),
        ],
        "name_rows": [
            ("索引姓名与称号", "Brosses, Président Charles De", "S1，B.csv#302"),
            ("书目署名", "Brosses, Charles de", "S2，第21章书目，L264"),
        ],
        "relation_ids": ["st-chp9-p245-footnote1-measures-and-brosses"],
        "description_zh": (
            "本卡登记索引主项“Brosses, Président Charles De”及第21章书目署名“Brosses, Charles de”，规范显示名为Charles de Brosses。"
            "第9章索引定位包括第245、260页及第10章第311页脚注；中文名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Brosses, Président Charles De” and the Chapter 21 bibliography form “Brosses, Charles de,” "
            "using Charles de Brosses as the display name. The index locators include pages 245 and 260 and a Chapter 10 note on page 311. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "第9章p.245与p.260及第10章p.292、p.311均以De Brosses姓名或引文定位出现；p.311注5与索引311n相合。"
            "第10章人物候选cand-9436将在S3复核中映射到本KU；archive候选cand-9437、cand-9879及书目作品cand-11268保持分开。"
            "引文均经Haskell转引，De Brosses原书页未独立查阅。"
        ),
        "context_en": (
            "De Brosses appears by name or citation in Chapter 9, pages 245 and 260, and Chapter 10, pages 292 and 311; the page 311 note matches index locator 311n. "
            "The Chapter 10 person candidate cand-9436 will be aligned to this KU in an S3 review; archive candidates cand-9437 and cand-9879 and the bibliographic work cand-11268 remain separate. "
            "The cited passages are mediated by Haskell, and the original De Brosses pages were not independently consulted."
        ),
    },
]

if __name__ == "__main__":
    raise SystemExit(registrar.main())
