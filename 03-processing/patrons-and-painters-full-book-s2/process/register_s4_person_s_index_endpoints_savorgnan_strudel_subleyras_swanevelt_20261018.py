from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_s_index_endpoints_schut_segala_serlio_skala_20261018 as registrar  # noqa: E402

registrar.ANCHOR = "s4-savorgnan-strudel-subleyras-swanevelt-person-endpoints-20261018"
registrar.PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    "s4-savorgnan-strudel-subleyras-swanevelt-person-endpoints-20261018"
)
registrar.BATCH_TITLE = "Savorgnan、Strudel、Subleyras与Swanevelt四组直接人物端点"
registrar.BATCH_PROCESS_NOTE = (
    "四组均为S3 new单候选人物身份组，登记4张KU卡、4条候选映射和8条source_backed姓名字段。"
    "Faustina Savorgnan的婚姻叙述及后续Rezzonico婚姻壁画语境保持原书限定；"
    "Strudel的两幅作品候选未辨明，Schönborn引文保留为Haskell转述；"
    "Giuseppe Subleyras与未具名的法国画家保持区分，其计划图作品候选仍待证；"
    "Swanevelt两幅Van Laer作品未具名，Catalano偷窃说法只记录为Haskell转引的指控。"
    "本批10条S2关系候选留待S6，不新增作品KU、正式关系或外部来源。"
)
registrar.BATCH_RESULT_NOTE = (
    "；四组共10条S2关系候选保持待S6及原书限定；候选作品cand-7195、cand-7196、"
    "cand-10494、cand-11915继续待证，不新增作品KU或formal relation。"
)
registrar.TARGETS = [
    {
        "candidate": "cand-2378",
        "group": "new-person:faustina-savorgnan-27789ccf3b",
        "ku": "units/persons/faustina-savorgnan",
        "card": "04-knowledge/units/persons/faustina-savorgnan.md",
        "name_zh": "福斯蒂娜·萨沃尔尼昂",
        "name_en": "Faustina Savorgnan",
        "index_entry": "S.csv#66",
        "index_name": "Savorgnan, Faustina",
        "index_page": "254",
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/09_CHP-9_intro.md",
                "第9章引言，印刷页254，行137",
                "line 137; print p. 254",
                "In 1758, for instance, Faustina Savorgnan, a young girl of the most select nobility, "
                "married Lodovico Rezzonico, second son of a family whose rise had been as spectacular as it was recent.",
                "Haskell称Faustina Savorgnan于1758年与Lodovico Rezzonico成婚；本卡仅记录该书内叙述。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/09_CHP-9_intro.md",
                "第9章引言，印刷页254，行140–141",
                "lines 140–141; print p. 254",
                "In his marriage fresco for the Pope’s nephew Tiepolo envisages a scene which puts even these successes "
                "in the shade (Plate 43). The bridal pair are being carried on the chariot of the sun drawn by four "
                "hurtling white horses and accompanied by\nApollo himself, while Fame sounds the event to the world.",
                "紧接的段落描述教皇侄子的婚姻壁画及双人场景；其与Faustina的关联仅按页内语境保留，不升级为独立归属判断。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Savorgnan, Faustina", "S1，S.csv#66"),
            ("正文姓名", "Faustina Savorgnan", "S2，第9章引言，p.254，L137"),
        ],
        "relation_ids": [
            "st-chp9-p254-faustina-lodovico-marriage",
            "st-chp9-p254-tiepolo-rezzonico-marriage-fresco",
            "st-chp9-p254-solar-chariot-scene",
        ],
        "description_zh": (
            "本卡登记书后索引主条“Savorgnan, Faustina”及第9章具名的Faustina Savorgnan。"
            "Haskell称她于1758年与Lodovico Rezzonico成婚；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index main entry “Savorgnan, Faustina” and the Faustina Savorgnan named in Chapter 9. "
            "Haskell says she married Lodovico Rezzonico in 1758. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "原文脚注1引Livan和Giussani，本卡只记录Haskell正文叙述。紧接的Rezzonico婚姻壁画及双人乘日车场景按页内语境保留，"
            "不视为独立肖像归属；三个S2关系候选留待S6，不新增正式关系。"
        ),
        "context_en": (
            "Footnote 1 cites Livan and Giussani, neither independently consulted here; this card records Haskell’s narrative. "
            "The following Rezzonico marriage fresco and solar-chariot scene remain contextual to the page and are not treated as "
            "independent portrait identifications. All three S2 relation candidates remain for S6; no formal relation is added."
        ),
    },
    {
        "candidate": "cand-2529",
        "group": "new-person:peter-strudel-a6aaeee55b",
        "ku": "units/persons/peter-strudel",
        "card": "04-knowledge/units/persons/peter-strudel.md",
        "name_zh": "彼得·施特鲁德尔",
        "name_en": "Peter Strudel",
        "index_entry": "S.csv#218",
        "index_name": "Strudel, Peter",
        "index_page": "195",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
                "第7章第IV节，印刷页195，行40",
                "line 40; print p. 195",
                "Peter Strudel a Tarquin and Lucretia and a Joseph.",
                "Haskell转引Liechtenstein亲王1691年书信，列出归于Peter Strudel的Tarquin and Lucretia及一幅Joseph画作。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
                "第7章第IV节，印刷页195，行40–41",
                "lines 40–41; print p. 195",
                "comme j’ay observé que le plus fort de\nStrudel consiste in dem nakenden",
                "Haskell转引Lothar Franz von Schönborn的多语引文，称Strudel的强项在裸像；引文日期尚未由该段确定。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Strudel, Peter", "S1，S.csv#218"),
            ("正文姓名", "Peter Strudel", "S2，第7章第IV节，p.195，L40"),
        ],
        "relation_ids": [
            "st-chp7-p195-strudel-tarquin",
            "st-chp7-p195-strudel-joseph",
            "st-chp7-p195-lothar-schonborn-letter",
        ],
        "description_zh": (
            "本卡登记书后索引主条“Strudel, Peter”及第7章具名的Peter Strudel。"
            "Haskell在转引的书信中将两幅画作归于他；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index main entry “Strudel, Peter” and the Peter Strudel named in Chapter 7. "
            "In quoted letters, Haskell reports attributions of pictures to him. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Liechtenstein亲王1691年书信所列Tarquin and Lucretia及Joseph画作均未能落实到具体作品；Joseph身份也未指明。"
            "后续Schönborn引文对Strudel裸像绘画的评价仍为Haskell转述，日期尚待核。三条S2关系候选留待S6，不新增作品KU或正式关系。"
        ),
        "context_en": (
            "The Tarquin and Lucretia and Joseph pictures in the quoted 1691 Liechtenstein letter are not identified as physical works; "
            "the Joseph is unspecified. Schönborn’s later comment on Strudel’s nude figures remains Haskell’s report, and its date is not "
            "established in this passage. All three S2 relation candidates remain for S6; no work KU or formal relation is added."
        ),
    },
    {
        "candidate": "cand-2532",
        "group": "new-person:giuseppe-subleyras-1180e5b00c",
        "ku": "units/persons/giuseppe-subleyras",
        "card": "04-knowledge/units/persons/giuseppe-subleyras.md",
        "name_zh": "朱塞佩·苏布莱拉斯",
        "name_en": "Giuseppe Subleyras",
        "index_entry": "S.csv#221",
        "index_name": "Subleyras, Giuseppe",
        "index_page": "366",
        "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
            "第15章第II节，印刷页366，行20–21",
            "lines 20–21; print p. 366",
            "He had his plans drawn by\nGiuseppe Subleyras, son of the French painter,",
            "Haskell称Memmo请Giuseppe Subleyras绘制计划图，并称他是法国画家的儿子；该句未给出图稿标题或数量。",
        ),
        "name_rows": [
            ("索引姓名", "Subleyras, Giuseppe", "S1，S.csv#221"),
            ("正文姓名", "Giuseppe Subleyras", "S2，第15章第II节，p.366，L20–21"),
        ],
        "relation_ids": ["st-chp15-p366-subleyras-drew-pra-plans"],
        "description_zh": (
            "本卡登记书后索引主条“Subleyras, Giuseppe”及第15章具名的Giuseppe Subleyras。"
            "Haskell称他为Memmo的Prà计划绘制图稿；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index main entry “Subleyras, Giuseppe” and the Giuseppe Subleyras named in Chapter 15. "
            "Haskell says he drew plans for Memmo’s Prà scheme. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "原文只称其为“一位法国画家的儿子”，本卡不推定父亲身份或与其他Subleyras候选合并。计划图未具题名、数量；"
            "作品候选cand-10494仍为S3 undecided，该关系候选留待S6，不新建作品KU或正式关系。"
        ),
        "context_en": (
            "The passage calls him “the son of the French painter” but does not name the father; this card does not infer the father’s identity "
            "or merge him with another Subleyras candidate. The plans have no supplied title or count; work candidate cand-10494 remains S3 undecided, "
            "and the relation candidate remains for S6. No work KU or formal relation is added."
        ),
    },
    {
        "candidate": "cand-2535",
        "group": "new-person:hermann-swanevelt-610e66be4a",
        "ku": "units/persons/hermann-swanevelt",
        "card": "04-knowledge/units/persons/hermann-swanevelt.md",
        "name_zh": "赫尔曼·斯瓦内费尔特",
        "name_en": "Hermann Swanevelt",
        "index_entry": "S.csv#224",
        "index_name": "Swanevelt, Hermann",
        "index_page": "135",
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_iii.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/05_CHP-5_sec_iii.md",
                "第5章第III节，印刷页135，行32",
                "line 32; print p. 135",
                "Hermann Swanevelt, the Dutch landscape painter, owned two",
                "Haskell称荷兰风景画家Hermann Swanevelt拥有两幅画；该句位于Van Laer作品的段落中，作品具体身份未给出。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/05_CHP-5_sec_iii.md",
                "第5章第III节脚注3，印刷页136，行136",
                "line 136; print p. 136 n. 3",
                "3 Bertolotti: Artisti belgi c olandesi, pp. 127 If., reports the case brought by Swanevelt against Francesco Catalano "
                "of Benevento whom he accused of stealing two pictures by Van Laer. The testimony provides much useful information about "
                "the artist’s circumstances.",
                "Haskell脚注转引Bertolotti所述诉讼及Swanevelt对Catalano的指控；本项目未独立查阅该证词，指控不视为裁决结果。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Swanevelt, Hermann", "S1，S.csv#224"),
            ("正文姓名", "Hermann Swanevelt", "S2，第5章第III节，p.135，L32"),
        ],
        "relation_ids": [
            "st-chp5-p135-swanevelt-owned-two-van-laer-pictures",
            "st-chp5-p135-swanevelt-pictures-by-van-laer",
            "st-chp5-notes-l136-swanevelt-catalano-case",
        ],
        "description_zh": (
            "本卡登记书后索引主条“Swanevelt, Hermann”及第5章具名的Hermann Swanevelt。"
            "Haskell称他为荷兰风景画家；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index main entry “Swanevelt, Hermann” and the Hermann Swanevelt named in Chapter 5. "
            "Haskell identifies him as a Dutch landscape painter. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell在Van Laer作品段落中称Swanevelt拥有两幅画，作品作者归属依段落语境而定，画作未具名。脚注转引Bertolotti，"
            "称Swanevelt曾指控Francesco Catalano偷窃两幅Van Laer画作；这只是转引的指控，不是裁判结论。三条S2关系候选留待S6，"
            "候选画作cand-11915仍为S3 undecided，不新增作品KU或正式关系。"
        ),
        "context_en": (
            "In a passage about Van Laer’s works, Haskell says Swanevelt owned two pictures; their attribution to Van Laer depends on that "
            "paragraph context, and the pictures are unnamed. A footnote citing Bertolotti says Swanevelt accused Francesco Catalano of stealing "
            "two Van Laer pictures; this is a reported accusation, not a judicial finding. All three S2 relation candidates remain for S6; work "
            "candidate cand-11915 remains S3 undecided, and no work KU or formal relation is added."
        ),
    },
]

if __name__ == "__main__":
    raise SystemExit(registrar.main())
