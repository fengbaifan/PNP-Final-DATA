from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_s_index_endpoints_schut_segala_serlio_skala_20261018 as registrar  # noqa: E402

registrar.ANCHOR = "s4-zambelli-zanotti-zen-zucchi-person-endpoints-20261018"
registrar.PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    "s4-zambelli-zanotti-zen-zucchi-person-endpoints-20261018"
)
registrar.BATCH_TITLE = "Zambelli、Zanotti、Zen与Zucchi四组人物端点"
registrar.BATCH_PROCESS_NOTE = (
    "四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和8条source_backed姓名字段。"
    "Paola Zambelli只在Haskell致谢中作为Archivio di Stato档案协助者出现。"
    "Eustachio Zanotti仅在p.348和p.354脚注的书信书目定位中具名；所引书信和版本均未独立查阅，不记录通信内容或额外关系。"
    "Procurator Alessandro Zen只依索引及Haskell转述的1761年死亡报告登记；不外推继任情况。"
    "Andrea Zucchi依据索引与Tiepolo为该雕刻师绘制Corradini雕像图像的叙述登记；同段Zaccaria Sagredo版画题献不归入Zucchi关系。"
    "唯一直接S2关系候选留待S6；其余三组无可归属于各自身份组的S2关系候选。无外部来源、正式关系或backlog写入。"
)
registrar.BATCH_RESULT_NOTE = (
    "；仅Andrea Zucchi关联1条直接S2关系候选并留待S6；Paola Zambelli致谢、Eustachio Zanotti书信定位、"
    "Alessandro Zen死亡报告均不扩写成正式关系；同段题献给Zaccaria Sagredo的版画不归给Andrea Zucchi。"
    "无外部来源、正式关系或backlog写入。"
)
registrar.TARGETS = [
    {
        "candidate": "cand-2833",
        "group": "new-person:dottoressa-paola-zambelli-paola-zambelli-82f8913498",
        "ku": "units/persons/paola-zambelli",
        "card": "04-knowledge/units/persons/paola-zambelli.md",
        "name_zh": "保拉·赞贝利",
        "name_en": "Paola Zambelli",
        "index_entry": "UVWXYZ.csv#170",
        "index_name": "Zambelli, Dr Paola",
        "index_page": "211n",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i_notes_p211_visual-transcription.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/08_CHP-8_sec_i_notes_p211_visual-transcription.md",
            "第8章第I节脚注，印刷页211，行1",
            "line 1; print p. 211, note 1",
            "I am most grateful to Dottoressa Paola Zambelli of the Archivio di Stato for her help.",
            "Haskell在关于 del Rosso 家族收藏的脚注中感谢Archivio di Stato的Dottoressa Paola Zambelli提供协助。",
        ),
        "name_rows": [
            ("索引姓名", "Zambelli, Dr Paola", "S1，UVWXYZ.csv#170"),
            ("脚注姓名与称谓", "Dottoressa Paola Zambelli", "S2，第8章第I节脚注，p.211，L1"),
        ],
        "relation_ids": [],
        "description_zh": (
            "本卡登记书后索引主条“Zambelli, Dr Paola”及第8章第211页脚注具名的Dottoressa Paola Zambelli。"
            "Haskell感谢她提供档案协助；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Paola Zambelli, indexed as “Zambelli, Dr Paola” and named in a Chapter 8 footnote on page 211. "
            "Haskell thanks her for archival assistance; the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "来源只说明她为Archivio di Stato人员并向Haskell提供协助，不扩写其生平、具体档案发现或其他关系。"
        ),
        "context_en": (
            "The source only identifies her as an Archivio di Stato staff member who assisted Haskell; no biography, specific archival finding, or other relation is added."
        ),
    },
    {
        "candidate": "cand-2863",
        "group": "new-person:eustachio-zanotti-e0dbfd3b49",
        "ku": "units/persons/eustachio-zanotti",
        "card": "04-knowledge/units/persons/eustachio-zanotti.md",
        "name_zh": "尤斯塔基奥·扎诺蒂",
        "name_en": "Eustachio Zanotti",
        "index_entry": "UVWXYZ.csv#200",
        "index_name": "Zanotti, Eustachio",
        "index_page": "347, 354n",
        "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/14_CHP-14_intro.md",
                "第14章引言脚注，印刷页348，行173",
                "line 173; print p. 348, note 3",
                "See letters to F. M. and Eustachio Zanotti and Antonio Conti from Rome between February and June 1734 published in Opere, X and XII.",
                "脚注3列出1734年2月至6月Algarotti从Rome寄给F. M. Zanotti、Eustachio Zanotti及Antonio Conti的书信出版定位；书信和版本未独立查阅。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/14_CHP-14_intro.md",
                "第14章引言脚注，印刷页354，行188",
                "line 188; print p. 354, note 3",
                "a letter to Eustachio Zanotti of 13 May 1756",
                "脚注3另引Algarotti于1756年5月13日致Eustachio Zanotti的信及Opere卷页；原信和出版页未独立查阅。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Zanotti, Eustachio", "S1，UVWXYZ.csv#200"),
            ("脚注姓名", "Eustachio Zanotti", "S2，第14章引言脚注，p.348，L173；p.354，L188"),
        ],
        "relation_ids": [],
        "description_zh": (
            "本卡登记书后索引主条“Zanotti, Eustachio”及第14章第348、354页脚注中的Eustachio Zanotti。"
            "两处脚注仅提供Algarotti书信的书目定位；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Eustachio Zanotti, indexed as “Zanotti, Eustachio” and named in Chapter 14 footnotes on pages 348 and 354. "
            "Both notes provide bibliographic locators for Algarotti's letters; the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "书信内容及Opere卷册未独立查阅；本卡只保留脚注的姓名和书目定位，不转写通信内容，也不据此新增正式关系。"
        ),
        "context_en": (
            "The letters and cited Opere volumes were not independently consulted. This card records only the names and bibliographic locators in the notes, "
            "adds no letter content, and creates no formal relation."
        ),
    },
    {
        "candidate": "cand-2868",
        "group": "new-person:alessandro-procurator-zen-b85892daa8",
        "ku": "units/persons/alessandro-zen",
        "card": "04-knowledge/units/persons/alessandro-zen.md",
        "name_zh": "亚历山德罗·泽恩",
        "name_en": "Alessandro Zen",
        "index_entry": "UVWXYZ.csv#205",
        "index_name": "Zen, Procurator Alessandro",
        "index_page": "253",
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/09_CHP-9_intro.md",
            "第9章引言，印刷页253，行131",
            "line 131; print p. 253",
            "In 1761 the British Resident, reporting the death of the Procurator Alessandro Zen, added:",
            "Haskell转述英国Resident于1761年报告Procurator Alessandro Zen去世，并引述当时尚无人提出继任候选的说法。",
        ),
        "name_rows": [
            ("索引姓名与职衔", "Zen, Procurator Alessandro", "S1，UVWXYZ.csv#205"),
            ("正文姓名与职衔", "Procurator Alessandro Zen", "S2，第9章引言，p.253，L131"),
        ],
        "relation_ids": [],
        "description_zh": (
            "本卡登记书后索引主条“Zen, Procurator Alessandro”及第9章第253页提到的Procurator Alessandro Zen。"
            "Haskell转述英国Resident在1761年的报告；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Alessandro Zen, indexed as “Zen, Procurator Alessandro” and mentioned on page 253 of Chapter 9 as a Procurator. "
            "Haskell reports the British Resident's account from 1761; the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "此处只记录Haskell转述的死亡报告和官职称谓；引文中关于尚无人提出继任候选的内容不外推为后续继任结果。"
        ),
        "context_en": (
            "The card records only Haskell's report of Zen's death and the office title. The quotation that no successor candidate had yet been offered "
            "is not extended into a claim about the later succession."
        ),
    },
    {
        "candidate": "cand-2886",
        "group": "new-person:andrea-zucchi-a8e76e789e",
        "ku": "units/persons/andrea-zucchi",
        "card": "04-knowledge/units/persons/andrea-zucchi.md",
        "name_zh": "安德烈亚·祖基",
        "name_en": "Andrea Zucchi",
        "index_entry": "UVWXYZ.csv#223",
        "index_name": "Zucchi, Andrea",
        "index_page": "265",
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/09_CHP-9_intro.md",
            "第9章引言，印刷页265，行293–294",
            "lines 293–294; print p. 265",
            "Furthermore, sometime after 1721 Tiepolo drew for the engraver Andrea Zucchi the statue of\nVirginity by the sculptor Antonio Corradini",
            "Haskell称Tiepolo在1721年后为雕刻师Andrea Zucchi绘制Corradini的Virginity雕像图像；此处说的是绘图，不是Tiepolo制作雕像。",
        ),
        "name_rows": [
            ("索引姓名", "Zucchi, Andrea", "S1，UVWXYZ.csv#223"),
            ("正文全名与角色", "engraver Andrea Zucchi", "S2，第9章引言，p.265，L293"),
        ],
        "relation_ids": ["st-chp9-p265-tiepolo-drew-virginity-for-zucchi"],
        "description_zh": (
            "本卡登记书后索引主条“Zucchi, Andrea”及第9章第265页具名的engraver Andrea Zucchi。"
            "Haskell称Tiepolo在1721年后为他绘制Antonio Corradini的Virginity雕像图像；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Andrea Zucchi, indexed as “Zucchi, Andrea” and named on page 265 of Chapter 9 as an engraver. "
            "Haskell says Tiepolo drew Corradini's statue of Virginity for him sometime after 1721; the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "原文区分Corradini所作雕像与Tiepolo为雕刻师Zucchi绘制的图像，不将雕像归于Tiepolo。"
            "同段另称一幅版画题献给Zaccaria Sagredo；该题献候选不归入Andrea Zucchi组。相关绘图关系候选留待S6。"
        ),
        "context_en": (
            "The passage distinguishes Corradini's statue from Tiepolo's drawing of it for the engraver Zucchi; the statue is not attributed to Tiepolo. "
            "The same paragraph separately says a print was dedicated to Zaccaria Sagredo; that dedication candidate is not assigned to Andrea Zucchi. "
            "The drawing relation candidate remains for S6."
        ),
    },
]

if __name__ == "__main__":
    raise SystemExit(registrar.main())
