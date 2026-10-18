from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_s_index_endpoints_schut_segala_serlio_skala_20261018 as registrar  # noqa: E402

registrar.ANCHOR = "s4-troy-tubeuf-turchi-uccelli-person-endpoints-20261018"
registrar.PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    "s4-troy-tubeuf-turchi-uccelli-person-endpoints-20261018"
)
registrar.BATCH_TITLE = "de Troy、Tubeuf、Turchi与Uccelli四组人物端点"
registrar.BATCH_PROCESS_NOTE = (
    "四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和8条source_backed姓名字段。"
    "François de Troy依据索引全名和第10章集体名单中的de Troy登记；不补写个人会面细节。"
    "Jacques Tubeuf依据索引及第7章被称作金融家之正文记录；强行取得宫殿的具体法律机制、日期与宫殿名称未见于该处。"
    "Alessandro Turchi的T.csv索引行未列页码，正文p.185提供全名及作品归属语境；保留Haskell归属、系列边界和OCR尾随撇号校读。"
    "Ferdinando Uccelli依据索引与附录p.391登记为Haskell所称公证人；Smith宫殿未在该段具名，档案清单与Levi出版物未独立查阅。"
    "五条S2关系候选继续留待S6；无外部来源、formal relation或backlog写入。"
)
registrar.BATCH_RESULT_NOTE = (
    "；5条S2关系候选继续待S6；Turchi索引页码栏为空，按正文锚点保留身份依据；"
    "Uccelli所涉档案清单未独立查阅；未新增正式关系或外部来源。"
)
registrar.TARGETS = [
    {
        "candidate": "cand-2656",
        "group": "new-person:de-francois-troy-41388b5a89",
        "ku": "units/persons/francois-de-troy",
        "card": "04-knowledge/units/persons/francois-de-troy.md",
        "name_zh": "弗朗索瓦·德·特鲁瓦",
        "name_en": "François de Troy",
        "index_entry": "T.csv#119",
        "index_name": "Troy, François de",
        "index_page": "285",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/10_CHP-10_intro.md",
            "第10章引言，印刷页285，行186",
            "line 186; print p. 285",
            "She met Rigaud and Watteau, both of whom expressed their deep admiration, and all the other artists and connoisseurs—Coypel, Vleughels, Oppenord, de Troy, Mariette.",
            "Haskell将de Troy列入Rosalba Carriera所遇艺人与鉴赏家的集体名单；该句未提供单独会面细节。",
        ),
        "name_rows": [
            ("索引姓名", "Troy, François de", "S1，T.csv#119"),
            ("正文简称", "de Troy", "S2，第10章引言，p.285，L186"),
        ],
        "relation_ids": ["st-chp10-p285-carriera-met-de-troy"],
        "description_zh": (
            "本卡登记书后索引主条“Troy, François de”及第10章第285页名单中的“de Troy”。"
            "Haskell将其列入Rosalba Carriera所遇艺人与鉴赏家的集体名单；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Troy, François de” and “de Troy” in a list on page 285 of Chapter 10. "
            "Haskell includes him in a collective list of artists and connoisseurs Carriera met; the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell称Carriera见过Rigaud、Watteau及其他艺人与鉴赏家，并在集体名单中列出de Troy。"
            "该处没有提供其单独会面细节；相关关系候选留待S6。"
        ),
        "context_en": (
            "Haskell says Carriera met Rigaud, Watteau, and other artists and connoisseurs, listing de Troy among them. "
            "The passage gives no individual encounter details; the relation candidate remains for S6."
        ),
    },
    {
        "candidate": "cand-2657",
        "group": "new-person:jacques-tubeuf-da9776ab01",
        "ku": "units/persons/jacques-tubeuf",
        "card": "04-knowledge/units/persons/jacques-tubeuf.md",
        "name_zh": "雅克·蒂伯夫",
        "name_en": "Jacques Tubeuf",
        "index_entry": "T.csv#120",
        "index_name": "Tubeuf, Jacques",
        "index_page": "181",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/07_CHP-7_sec_i.md",
            "第7章第I节，印刷页181，行144",
            "line 144; print p. 181",
            "He not only failed to get Bernini to enlarge the palace that he had forcibly acquired from the financier Jacques Tubeuf;",
            "Haskell称Mazarin未能说服Bernini扩建其从金融家Jacques Tubeuf处强行取得的宫殿；原文未给出日期、法律机制或宫殿确切名称。",
        ),
        "name_rows": [
            ("索引姓名", "Tubeuf, Jacques", "S1，T.csv#120"),
            ("正文全名", "Jacques Tubeuf", "S2，第7章第I节，p.181，L144"),
        ],
        "relation_ids": ["st-chp7-p181-i19"],
        "description_zh": (
            "本卡登记书后索引主条“Tubeuf, Jacques”及第7章第I节第181页所称的金融家Jacques Tubeuf。"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Tubeuf, Jacques” and the financier Jacques Tubeuf named on page 181 of Chapter 7, section I. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell称Mazarin未能说服Bernini扩建一座其从Tubeuf处强行取得的宫殿。原文没有提供取得日期、法律机制或宫殿确切名称；"
            "以上均保留为书内叙述，关系候选留待S6。"
        ),
        "context_en": (
            "Haskell says Mazarin failed to get Bernini to enlarge a palace he had forcibly acquired from Tubeuf. "
            "The passage supplies no acquisition date, legal mechanism, or exact palace name; the account remains attributed to the book, "
            "and the relation candidate remains for S6."
        ),
    },
    {
        "candidate": "cand-2660",
        "group": "new-person:alessandro-turchi-62c226570b",
        "ku": "units/persons/alessandro-turchi",
        "card": "04-knowledge/units/persons/alessandro-turchi.md",
        "name_zh": "亚历山德罗·图尔基",
        "name_en": "Alessandro Turchi",
        "index_entry": "T.csv#123",
        "index_name": "Turchi, Alessandro",
        "index_page": "",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/07_CHP-7_sec_i.md",
            "第7章第I节，印刷页185，行207–209",
            "lines 207-209; print p. 185",
            "In the 1640s La Vrilliere added to these a series of paintings by Guercino [The War between the Romans and the Sabines and\nCoriolanus and his Mother), Pietro da Cortona (Caesar restoring Cleopatra to her usurped\nThrone, The Sibyl announcing the Birth of Christ to Augustus and the Finding of Romulus and Remus) and Alessandro Turchi (The Death of Cleopatra').",
            "Haskell称La Vrillière在1640年代增加一组作品，并将其中《The Death of Cleopatra》列在Alessandro Turchi名下；索引行未列页码，正文定位为p.185。",
        ),
        "name_rows": [
            ("索引姓名", "Turchi, Alessandro", "S1，T.csv#123；索引页码栏为空"),
            ("正文全名", "Alessandro Turchi", "S2，第7章第I节，p.185，L209"),
        ],
        "relation_ids": [
            "st-chp7-p185-i05",
            "st-chp7-p185-i11",
        ],
        "description_zh": (
            "本卡登记书后索引主条“Turchi, Alessandro”；该索引行未列页码。第7章第I节第185页具名Alessandro Turchi，"
            "并在La Vrillière藏画叙述中将《The Death of Cleopatra》列于其名下。中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Turchi, Alessandro,” whose page field is blank. Alessandro Turchi is named on page 185 of Chapter 7, section I, "
            "where Haskell lists The Death of Cleopatra under his name in an account of La Vrillière’s paintings. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell称La Vrillière在1640年代增加一组绘画，并列出Alessandro Turchi名下的《The Death of Cleopatra》。"
            "该归属仍是书内陈述，相关系列和作品关系候选分别留待S6；S2记录页图将OCR在题名后的尾随撇号校为转录误差。"
        ),
        "context_en": (
            "Haskell says La Vrillière added a group of paintings in the 1640s and lists The Death of Cleopatra under Alessandro Turchi. "
            "The attribution remains the book’s account, and the series and work relation candidates remain for S6. S2 records the trailing apostrophe "
            "after the title in OCR as a transcription error corrected against the page image."
        ),
    },
    {
        "candidate": "cand-2665",
        "group": "new-person:ferdinando-uccelli-49b207abe4",
        "ku": "units/persons/ferdinando-uccelli",
        "card": "04-knowledge/units/persons/ferdinando-uccelli.md",
        "name_zh": "费迪南多·乌切利",
        "name_en": "Ferdinando Uccelli",
        "index_entry": "UVWXYZ.csv#0",
        "index_name": "Uccelli, Ferdinando",
        "index_page": "391",
        "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/19_CHP-19Appendix.md",
            "附录3，印刷页391，行118–119",
            "lines 118-119; print p. 391",
            "when he died in 1770, only eight years later, several hundred pictures were recorded by the notaio Ferdinando Uccelli as being in his palace. The list of these, which gives the subject only and not the artist, is reprinted from the\nArchivio di Stato-Petizion 467 by C. A. Levi, II, pp. 236-48.",
            "Haskell报告Smith于1770年去世时，公证人Ferdinando Uccelli记录其宫殿内有数百幅画；所列清单仅给主题、不列作者，档案原件与Levi出版物未独立查阅。",
        ),
        "name_rows": [
            ("索引姓名", "Uccelli, Ferdinando", "S1，UVWXYZ.csv#0"),
            ("正文全名与身份称谓", "notaio Ferdinando Uccelli", "S2，附录3，p.391，L118"),
        ],
        "relation_ids": ["st-chp19-p391-smith-1770-picture-list"],
        "description_zh": (
            "本卡登记书后索引主条“Uccelli, Ferdinando”及附录3所称的公证人Ferdinando Uccelli。"
            "Haskell将其列为Smith去世时记录宫殿藏画的人；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Uccelli, Ferdinando” and the notary Ferdinando Uccelli named in Appendix 3. "
            "Haskell identifies him as the person who recorded pictures in Smith’s palace at Smith’s death; the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell称Smith于1770年去世时，公证人Uccelli记录其宫殿内有数百幅画；清单仅列主题而不列作者。"
            "该段未命名宫殿，Archivio di Stato记录及C. A. Levi的再版未独立查阅；关系候选留待S6。"
        ),
        "context_en": (
            "Haskell says that when Smith died in 1770, the notary Uccelli recorded several hundred pictures in his palace; the list gives subjects, not artists. "
            "The passage does not name the palace, and neither the Archivio di Stato record nor C. A. Levi’s reprint was independently consulted. "
            "The relation candidate remains for S6."
        ),
    },
]

if __name__ == "__main__":
    raise SystemExit(registrar.main())
