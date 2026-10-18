from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_s_index_endpoints_schut_segala_serlio_skala_20261018 as registrar  # noqa: E402

registrar.ANCHOR = "s4-tassi-temanza-tessin-thornhill-person-endpoints-20261018"
registrar.PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    "s4-tassi-temanza-tessin-thornhill-person-endpoints-20261018"
)
registrar.BATCH_TITLE = "Tassi、Temanza、Tessin与Thornhill四组人物端点"
registrar.BATCH_PROCESS_NOTE = (
    "四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和12条source_backed姓名字段。"
    "Agostino Tassi依索引第49、56页同组记录，保留第49页装饰语境与第56页全名和受命绘画的语境；"
    "Tommaso Temanza以索引全名连接第6、10、15、21章的书内指称，所引原件和出版物未独立查阅；"
    "Nicodemus Tessin the Younger依索引将第56注与第406页归入同组，同时标明第406页正文只写Tessin，并与Count Carl Gustav Tessin分开；"
    "Sir James Thornhill的St Paul's穹顶、Moor Park与Hampton Court事例仅保留原书所述的受命、建造和改派语气。"
    "本批8条S2关系候选留待S6；无formal relation、外部来源或backlog写入。"
)
registrar.BATCH_RESULT_NOTE = (
    "；8条S2关系候选继续待S6；Tessin第406页身份沿用索引归组并保留正文简称；"
    "本批未新增正式关系或外部来源。"
)
registrar.TARGETS = [
    {
        "candidate": "cand-2542",
        "group": "new-person:agostino-tassi-e888637062",
        "ku": "units/persons/agostino-tassi",
        "card": "04-knowledge/units/persons/agostino-tassi.md",
        "name_zh": "阿戈斯蒂诺·塔西",
        "name_en": "Agostino Tassi",
        "index_entry": "T.csv#5",
        "index_name": "Tassi, Agostino",
        "index_page": "49, 56",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
                "第2章第IV节，印刷页49，行75",
                "line 75; print p. 49",
                "The frescoes by Tassi and Gentileschi were painted in 1611 and 1612",
                "Haskell称Tassi与Gentileschi绘制的壁画完成于1611至1612年。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
                "第2章第IV节，印刷页56，行143",
                "line 143; print p. 56",
                "Don Taddeo was made Prefect of Rome—a scene which Agostino Tassi was required to paint",
                "Haskell称Agostino Tassi受命绘制Don Taddeo出任罗马长官的场景。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Tassi, Agostino", "S1，T.csv#5"),
            ("正文姓名", "Agostino Tassi", "S2，第2章第IV节，p.56，L143"),
            ("正文姓氏", "Tassi", "S2，第2章第IV节，p.49，L75"),
        ],
        "relation_ids": [
            "st-chp2-seciv-l65-77-borghese-palace-decoration-by-tassi",
        ],
        "description_zh": (
            "本卡登记书后索引主条“Tassi, Agostino”及第2章第IV节具名的Agostino Tassi。"
            "索引将其定位于第49、56页；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index main entry “Tassi, Agostino” and Agostino Tassi named in Chapter 2, section IV. "
            "The index locates the entry on pages 49 and 56. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "第49页称Tassi与Gentileschi绘制的壁画完成于1611至1612年；第56页具名Agostino Tassi，并称他受命绘制Don Taddeo出任罗马长官的场景。"
            "本卡依S3索引组对应两页语境，不补充外部生平；S2关系候选留待S6，不登记正式关系。"
        ),
        "context_en": (
            "Page 49 dates frescoes by Tassi and Gentileschi to 1611–1612. Page 56 names Agostino Tassi and says he was required to paint "
            "the scene of Don Taddeo becoming Prefect of Rome. Following the S3 index group, this card records both page contexts without "
            "adding external biography. The S2 relation candidate remains for S6; no formal relation is added."
        ),
    },
    {
        "candidate": "cand-2546",
        "group": "new-person:temanza-tommaso-8171d459b0",
        "ku": "units/persons/tommaso-temanza",
        "card": "04-knowledge/units/persons/tommaso-temanza.md",
        "name_zh": "托马索·特曼扎",
        "name_en": "Tommaso Temanza",
        "index_entry": "T.csv#9",
        "index_name": "Temanza, Tommaso",
        "index_page": "361n",
        "source_file": "02-sources/02-Markdown/15_CHP-15_intro.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/06_CHP-6_sec_v.md",
                "第6章第V节脚注，印刷页165，行68",
                "line 68; print p. 165, note",
                "the unpublished Zibaldone by Tommaso Temanza—MS. 796 in Seminario Patriarcale, Venice.",
                "Haskell将未刊Zibaldone称为Tommaso Temanza所作，并给出手稿号及保管地点；手稿未独立查阅。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "第10章第II节脚注，印刷页321，行311",
                "line 311; print p. 321, note 1",
                "and Temanza, p. 87.",
                "Haskell在脚注中并列引用Temanza第87页，未说明该引文支持正文中的哪一分项。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/15_CHP-15_intro.md",
                "第15章引言脚注，印刷页361，行9",
                "line 9; print p. 361, note 2",
                "Letter from Mariette to Temanza of 15 April 1768 published by E. Müntz, 1890, p. 116.",
                "Haskell记载一封致Temanza的信及其出版信息；信件和出版物未独立查阅。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/21_CHP-21Bibliography.md",
                "第21章书目，印刷页438，行1151",
                "line 1151; print p. 438",
                "Temanza, T.: Vite dei più celebri architetti, e scultori veneziani, Venezia 1778.",
                "Haskell书目列出署名T. Temanza、1778年出版的著作；书籍未独立查阅。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Temanza, Tommaso", "S1，T.csv#9"),
            ("正文全名", "Tommaso Temanza", "S2，第6章第V节，p.165脚注，L68"),
            ("书信收件人", "Temanza", "S2，第15章引言，p.361脚注，L9"),
            ("书目作者写法", "Temanza, T.", "S2，第21章书目，p.438，L1151"),
        ],
        "relation_ids": [
            "st-chp15-p361-note2-mariette-letter-addressed-to-temanza",
        ],
        "description_zh": (
            "本卡登记书后索引主条“Temanza, Tommaso”，并汇集全书第6、10、15、21章对Temanza的指称。"
            "第6章脚注给出全名；其余章节分别引用其著作、提及致其书信及列出T. Temanza书目项。"
            "被引手稿、信件与出版物均未独立查阅。"
        ),
        "description_en": (
            "This card records the index main entry “Temanza, Tommaso” and the book’s references to Temanza in Chapters 6, 10, 15, and 21. "
            "A Chapter 6 note supplies the full name; the other chapters cite a work, mention a letter addressed to him, and list a T. Temanza "
            "bibliographic entry. The cited manuscript, letter, and publication were not independently consulted."
        ),
        "context_zh": (
            "第6章脚注将未刊Zibaldone称为Tommaso Temanza所作；第10章脚注引用Temanza第87页；第15章脚注称Mariette于1768年致信Temanza；"
            "第21章书目列出T. Temanza的1778年著作。上述均为Haskell书内引文信息，不代表本轮查阅了原件。"
            "致信关系候选留待S6；不在本轮登记正式关系。"
        ),
        "context_en": (
            "A Chapter 6 note calls an unpublished Zibaldone a work by Tommaso Temanza; a Chapter 10 note cites page 87 of Temanza; "
            "a Chapter 15 note reports a 1768 letter from Mariette to Temanza; and the Chapter 21 bibliography lists a 1778 work under "
            "T. Temanza. These are Haskell’s in-book references; the cited originals were not consulted in this pass. The letter-recipient "
            "relation candidate remains for S6, and no formal relation is added."
        ),
    },
    {
        "candidate": "cand-2555",
        "group": "new-person:nicodemus-tessin-younger-09dda9ee95",
        "ku": "units/persons/nicodemus-tessin-younger",
        "card": "04-knowledge/units/persons/nicodemus-tessin-younger.md",
        "name_zh": "尼科德穆斯·泰辛",
        "name_en": "Nicodemus Tessin the Younger",
        "index_entry": "T.csv#18",
        "index_name": "Tessin, Nicodemus, the Younger",
        "index_page": "56n, 406",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
                "第2章第IV节脚注，印刷页56，行150–151",
                "lines 150-151; print p. 56, note",
                "and ofthe many travellers’ accounts the fullest is that by Nicodemus Tessin the Younger and must date from 1687-8—Stockholm,\nKungliga Biblioteket, Handskriftsand S.41.",
                "Haskell称Tessin the Younger的游记为所述旅行记中最完整者，并推测其年代为1687至1688年，记录斯德哥尔摩藏本定位。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "第20章后记，印刷页406，行156",
                "line 156; print p. 406",
                "Tessin’s taste in the arts and his standing as a collector of drawings have been discussed by Bjurstrom",
                "Haskell称Bjurström曾讨论Tessin的艺术趣味与绘画收藏者身份；该处正文仅用姓氏。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Tessin, Nicodemus, the Younger", "S1，T.csv#18"),
            ("正文全名", "Nicodemus Tessin the Younger", "S2，第2章第IV节，p.56脚注，L150"),
            ("第406页称名", "Tessin", "S2，第20章后记，p.406，L156；身份归组依索引"),
        ],
        "relation_ids": [
            "st-chp2-seciv-l139-152-tessin-account-locator-and-date",
            "st-chp20-p406-bjurstrom-tessin-drawings",
        ],
        "description_zh": (
            "本卡登记索引主条“Tessin, Nicodemus, the Younger”及第2章脚注中的全名。索引页码为56n和406；"
            "第406页正文只写“Tessin”，本卡按S3索引归组保留该定位，同时与索引另列的Count Carl Gustav Tessin分开。"
        ),
        "description_en": (
            "This card records the index entry “Tessin, Nicodemus, the Younger” and the full name in a Chapter 2 note. The index gives pages "
            "56n and 406; the page 406 passage says only “Tessin.” This card follows the S3 index grouping for that locator and keeps the person "
            "distinct from the separately indexed Count Carl Gustav Tessin."
        ),
        "context_zh": (
            "第56页脚注称其游记为所述旅行记中最完整者，并推测成于1687至1688年，注明斯德哥尔摩藏本位置；第406页称Bjurström讨论Tessin的艺术趣味与绘画收藏。"
            "第406页称名按索引归组，正文简称所指未另行核验。两条S2关系候选留待S6，不登记正式关系。"
        ),
        "context_en": (
            "A Chapter 2 note calls his account the fullest of the travellers’ accounts discussed, says it must date from 1687–1688, and gives a Stockholm shelf locator. "
            "Page 406 says Bjurström discussed Tessin’s taste in art and drawing collection. The page 406 identity follows the index grouping; "
            "the shortened reference was not separately verified. Both S2 relation candidates remain for S6; no formal relation is added."
        ),
    },
    {
        "candidate": "cand-2568",
        "group": "new-person:james-thornhill-65d8cd6a4b",
        "ku": "units/persons/james-thornhill",
        "card": "04-knowledge/units/persons/james-thornhill.md",
        "name_zh": "詹姆斯·索恩希尔爵士",
        "name_en": "Sir James Thornhill",
        "index_entry": "T.csv#31",
        "index_name": "Thornhill, Sir James",
        "index_page": "286",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/10_CHP-10_intro.md",
                "第10章引言，印刷页286，行193–194",
                "lines 193-194; print p. 286",
                "The dome of St Paul’s, which had been a great magnet for the Venetian artists, was given to Thornhill to paint. So too was the ceiling of the Queen’s Bed Chamber at\nHampton Court",
                "Haskell称圣保罗大教堂穹顶和汉普顿宫王后寝宫天顶交由Thornhill绘制。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/10_CHP-10_intro.md",
                "第10章引言，印刷页286，行202",
                "line 202; print p. 286",
                "His country house at Moor Park was built for him in modified Baroque by Sir James\nThornhill and later Giacomo Leoni.",
                "Haskell具名Sir James Thornhill，并称Moor Park乡间住宅由他与Giacomo Leoni先后建造。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/10_CHP-10_intro.md",
                "第10章引言，印刷页287，行204–205",
                "lines 204-205; print p. 287",
                "Amigoni and Francesco Sleter instead.",
                "Haskell称Styles与Thornhill争执后，将Moor Park室内装饰改交Amigoni与Francesco Sleter。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Thornhill, Sir James", "S1，T.csv#31"),
            ("正文全名", "Sir James Thornhill", "S2，第10章引言，p.286，L202"),
        ],
        "relation_ids": [
            "st-chp10-p286-thornhill-st-pauls-dome",
            "st-chp10-p286-moor-park-built",
            "st-chp10-p286-moor-park-decoration-open",
            "st-chp10-p286-queens-bedchamber-commission",
        ],
        "description_zh": (
            "本卡登记索引主条“Thornhill, Sir James”及第10章具名的Sir James Thornhill。"
            "原书在圣保罗大教堂、汉普顿宫与Moor Park语境中称及其工作；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index main entry “Thornhill, Sir James” and Sir James Thornhill named in Chapter 10. "
            "The book discusses his work in connection with St Paul’s, Hampton Court, and Moor Park. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell称圣保罗大教堂穹顶及汉普顿宫王后寝宫天顶交由Thornhill绘制；Moor Park乡间住宅由Sir James Thornhill与Giacomo Leoni先后建造。"
            "Styles原拟委托Thornhill装饰Moor Park，争执后改交Amigoni与Francesco Sleter。四条S2关系候选均留待S6，不新增正式关系。"
        ),
        "context_en": (
            "Haskell says the dome of St Paul’s and the Queen’s Bed Chamber ceiling at Hampton Court were given to Thornhill to paint; "
            "Sir James Thornhill and Giacomo Leoni built Moor Park in succession. Styles had planned to entrust Thornhill with its decoration, "
            "then reassigned the work to Amigoni and Francesco Sleter after a quarrel. All four S2 relation candidates remain for S6; no formal relation is added."
        ),
    },
]


if __name__ == "__main__":
    raise SystemExit(registrar.main())
