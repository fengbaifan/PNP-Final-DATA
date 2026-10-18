from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_s_index_endpoints_schut_segala_serlio_skala_20261018 as registrar  # noqa: E402

registrar.ANCHOR = "s4-teniers-theodon-tofts-torelli-person-endpoints-20261018"
registrar.PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    "s4-teniers-theodon-tofts-torelli-person-endpoints-20261018"
)
registrar.BATCH_TITLE = "Teniers、Théodon、Tofts与Torelli四组人物端点"
registrar.BATCH_PROCESS_NOTE = (
    "四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和10条source_backed姓名字段。"
    "David Teniers依索引全名登记，正文p.358仅称Teniers；Jean Baptiste Théodon以索引第92、400页连接第3章全名与第20章简称，"
    "相关雕塑候选cand-2567、cand-5434、cand-10936继续保留S3 undecided；"
    "Katherine Tofts只按Haskell第302页所述第一段婚姻登记，同段关于Giustiniana Wynne及Smith第二段婚姻的S2关系候选保持区分；"
    "Giacomo Torelli依据索引第182、183页与正文全名归组，保留第183页财务处境归因和脚注书目定位。"
    "本批9条S2关系候选留待S6；无formal relation、外部来源或backlog写入。"
)
registrar.BATCH_RESULT_NOTE = (
    "；9条S2关系候选继续待S6；Teniers正文仅用姓氏；Théodon相关作品候选仍为undecided；"
    "Tofts只对应Smith第一段婚姻，其余同段人物关系分开保留；本批未新增正式关系或外部来源。"
)
registrar.TARGETS = [
    {
        "candidate": "cand-2549",
        "group": "new-person:david-teniers-a9f6e89e4e",
        "ku": "units/persons/david-teniers",
        "card": "04-knowledge/units/persons/david-teniers.md",
        "name_zh": "大卫·泰尼尔斯",
        "name_en": "David Teniers",
        "index_entry": "T.csv#12",
        "index_name": "Teniers, David",
        "index_page": "358",
        "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/14_CHP-14_intro.md",
            "第14章引言，印刷页358，行122",
            "line 122; print p. 358",
            "Flemish painters such as Teniers and\nWouwermans, as well as Vernet and Pannini.",
            "Haskell称Algarotti建议学习Teniers、Wouwermans、Vernet和Pannini等画家。",
        ),
        "name_rows": [
            ("索引姓名", "Teniers, David", "S1，T.csv#12"),
            ("正文称名", "Teniers", "S2，第14章引言，p.358，L122"),
        ],
        "relation_ids": [
            "st-chp14-p358-recommended-study-teniers",
        ],
        "description_zh": (
            "本卡登记书后索引主条“Teniers, David”及第14章第358页所称的Teniers。"
            "正文未给出名字，只记录Algarotti推荐学习的佛兰德画家；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index main entry “Teniers, David” and the Teniers mentioned on page 358 of Chapter 14. "
            "The passage gives only the surname and identifies him as a Flemish painter whom Algarotti recommended studying. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell转述Algarotti建议学习Teniers、Wouwermans、Vernet和Pannini，以兼顾意大利素描的高贵与佛兰德趣味。"
            "第358页正文仅称Teniers；本卡全名依书后索引，不扩展其生平或外部身份。该关系候选留待S6，不登记正式关系。"
        ),
        "context_en": (
            "Haskell reports Algarotti’s recommendation to study Teniers, Wouwermans, Vernet, and Pannini to combine the nobility of Italian "
            "draughtsmanship with Flemish taste. The page 358 passage uses only “Teniers”; the full name follows the book index. "
            "No biography or external identity is added. The relation candidate remains for S6; no formal relation is added."
        ),
    },
    {
        "candidate": "cand-2566",
        "group": "new-person:baptiste-jean-theodon-db4c8b1420",
        "ku": "units/persons/jean-baptiste-theodon",
        "card": "04-knowledge/units/persons/jean-baptiste-theodon.md",
        "name_zh": "让-巴蒂斯特·泰奥东",
        "name_en": "Jean Baptiste Théodon",
        "index_entry": "T.csv#29",
        "index_name": "Théodon, Jean Baptiste",
        "index_page": "92, 400",
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
                "第3章第IV节，印刷页92，行175",
                "line 175; print p. 92",
                "Jean Baptiste Theodon, whose heavily classical lumpiness was a total contrast to Legros’ dramatic, Baroque vigour.",
                "Haskell以Jean Baptiste Theodon之名提及另一侧祭坛雕塑群，并将其风格与Legros比较；该评价不证明作品完成状态。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "第20章后记，印刷页400，行47",
                "line 47; print p. 400",
                "statues by Théodon and Legros in the church—and thus to our knowledge of Jesuit patronage in general.",
                "Haskell称Enggass关于Théodon与Legros在Gesù教堂雕像的研究补充了对耶稣会赞助的认识。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Théodon, Jean Baptiste", "S1，T.csv#29"),
            ("第3章全名", "Jean Baptiste Theodon", "S2，第3章第IV节，p.92，L175"),
            ("第20章简称", "Théodon", "S2，第20章后记，p.400，L47"),
        ],
        "relation_ids": [
            "st-chp20-p400-enggass-rome-sculpture-book",
        ],
        "description_zh": (
            "本卡登记书后索引主条“Théodon, Jean Baptiste”，索引定位于第92、400页。"
            "第3章称Jean Baptiste Theodon，第20章以Théodon简称；姓名重音按书后索引记录。"
        ),
        "description_en": (
            "This card records the index main entry “Théodon, Jean Baptiste,” located on pages 92 and 400. "
            "Chapter 3 names Jean Baptiste Theodon, while Chapter 20 uses “Théodon”; the indexed spelling with the accent is retained."
        ),
        "context_zh": (
            "第3章称另一侧祭坛有一组Faith crushing Idolatry雕塑，归于Jean Baptiste Theodon，并将其风格与Legros比较；"
            "第20章称Enggass的研究讨论了Gesù教堂中Théodon与Legros的雕像。相关作品候选cand-2567、cand-5434、cand-10936仍分别为S3 undecided，"
            "本卡不据此登记作品KU或正式创作关系。唯一S2关系候选留待S6。"
        ),
        "context_en": (
            "Chapter 3 describes a group of Faith crushing Idolatry sculptures on the other side of the altar as the work of Jean Baptiste Theodon "
            "and compares its style with Legros. Chapter 20 says Enggass’s research discusses statues by Théodon and Legros in the Gesù. "
            "The related work candidates cand-2567, cand-5434, and cand-10936 remain separately S3-undecided; this card creates no work KU "
            "or formal creation relation. The sole S2 relation candidate remains for S6."
        ),
    },
    {
        "candidate": "cand-2639",
        "group": "new-person:katherine-tofts-2496dc1f4e",
        "ku": "units/persons/katherine-tofts",
        "card": "04-knowledge/units/persons/katherine-tofts.md",
        "name_zh": "凯瑟琳·托夫茨",
        "name_en": "Katherine Tofts",
        "index_entry": "T.csv#102",
        "index_name": "Tofts, Katherine",
        "index_page": "302",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/10_CHP-10_intro.md",
            "第10章引言，印刷页302，行392–393",
            "lines 392-393; print p. 302",
            "the cynicism of his first marriage to the rich but mad operatic singer\nKatherine Tofts;",
            "Haskell将Katherine Tofts称为歌剧演唱者，并以“rich but mad”描述其本人；此为作者措辞，不作为独立核实的事实。",
        ),
        "name_rows": [
            ("索引姓名", "Tofts, Katherine", "S1，T.csv#102"),
            ("正文姓名", "Katherine Tofts", "S2，第10章引言，p.302，L393"),
        ],
        "relation_ids": [
            "st-chp10-p302-smith-first-marriage",
            "st-chp10-p302-smith-second-marriage",
            "st-chp10-p302-smith-wynne-pursuit",
        ],
        "description_zh": (
            "本卡登记书后索引主条“Tofts, Katherine”及第10章第302页具名的Katherine Tofts。"
            "Haskell在同段称她为歌剧演唱者，并将其列为Joseph Smith的第一任妻子；评价性措辞保留为作者归因。"
        ),
        "description_en": (
            "This card records the index main entry “Tofts, Katherine” and Katherine Tofts named on page 302 of Chapter 10. "
            "In the same passage Haskell identifies her as an operatic singer and Joseph Smith’s first wife; evaluative wording remains attributed to the author."
        ),
        "context_zh": (
            "Haskell称Smith与Katherine Tofts的第一段婚姻，并以“rich but mad”描述她；该措辞是作者评价，未作为独立事实核实。"
            "同段另提Smith追求Giustiniana Wynne及其第二段婚姻，分别保留为不同S2关系候选，不映射为Tofts的关系。"
            "本批三条相关关系候选均待S6，不登记正式关系。"
        ),
        "context_en": (
            "Haskell identifies Katherine Tofts as Smith’s first wife and describes her as “rich but mad”; this is the author’s wording, "
            "not an independently verified fact. The same paragraph separately mentions Smith’s pursuit of Giustiniana Wynne and his second marriage; "
            "those remain distinct S2 relation candidates and are not assigned to Tofts. All three related candidates remain for S6; no formal relation is added."
        ),
    },
    {
        "candidate": "cand-2647",
        "group": "new-person:giacomo-torelli-16d67515c5",
        "ku": "units/persons/giacomo-torelli",
        "card": "04-knowledge/units/persons/giacomo-torelli.md",
        "name_zh": "贾科莫·托雷利",
        "name_en": "Giacomo Torelli",
        "index_entry": "T.csv#110",
        "index_name": "Torelli, Giacomo",
        "index_page": "182, 183",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "第7章第I节，印刷页182，行154",
                "line 154; print p. 182",
                "In 1645 Giacomo Torelli, the most distinguished of all Italian stage designers, was sent there by the Duke of Parma for whom he had been working,",
                "Haskell称Giacomo Torelli于1645年受帕尔马公爵派往巴黎，并说明此前为该公爵工作。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "第7章第I节，印刷页183，行166",
                "line 166; print p. 183",
                "Giacomo Torelli was financially ruined and imprisoned for many months.",
                "Haskell称Fronde期间Torelli财务破产并被监禁数月；保留为书内叙述。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "第7章第I节脚注4，印刷页183，行351",
                "line 351; print p. 183, note 4",
                "Prunières, 1913, p. 149.",
                "Haskell脚注引用Prunières 1913年著作第149页；该研究未独立查阅。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Torelli, Giacomo", "S1，T.csv#110"),
            ("正文全名", "Giacomo Torelli", "S2，第7章第I节，p.182，L154"),
            ("正文姓名", "Giacomo Torelli", "S2，第7章第I节，p.183，L166"),
        ],
        "relation_ids": [
            "st-chp7-p182-i10",
            "st-chp7-p182-i11",
            "st-chp7-p183-i16",
            "st-chp7-p183-n4-cite-prunieres",
        ],
        "description_zh": (
            "本卡登记书后索引主条“Torelli, Giacomo”及第7章第I节第182、183页具名的Giacomo Torelli。"
            "Haskell称他为意大利舞台设计师；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index main entry “Torelli, Giacomo” and Giacomo Torelli named on pages 182 and 183 of Chapter 7, section I. "
            "Haskell identifies him as an Italian stage designer. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell称Torelli于1645年由帕尔马公爵派往巴黎，此前曾为该公爵工作；其布景和新技术比所服务的歌剧吸引更多注意。"
            "第183页称他在Fronde期间财务破产并被监禁数月；此为Haskell书内叙述。"
            "脚注4引用Prunières 1913年著作第149页，未独立查阅。四条S2关系候选留待S6，不登记正式关系。"
        ),
        "context_en": (
            "Haskell says Torelli was sent to Paris by the Duke of Parma in 1645, having worked for him, and that Torelli’s scenery and techniques "
            "attracted more attention than the operas they served. Page 183 says he was financially ruined and imprisoned for months during the Fronde; "
            "this remains Haskell’s account. Note 4 cites Prunières (1913), page 149, which was not independently consulted. "
            "All four S2 relation candidates remain for S6; no formal relation is added."
        ),
    },
]


if __name__ == "__main__":
    raise SystemExit(registrar.main())
