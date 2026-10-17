from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import register_s4_person_endpoints_assereto_barelli_baretti_bartoli_basadonna_bassi_20261017 as helper  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ENRICHMENT_PATH = TABLES / "enrichment.jsonl"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
S3_ANCHOR = "s3-almoro-academy-crosschapter-boundaries-20261017"
S4_ANCHOR = "s4-almoro-academy-crosschapter-endpoints-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{S4_ANCHOR}"
HASKELL_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."
ALBRIZZI_URL = "https://www.treccani.it/enciclopedia/almoro-albrizzi_(Dizionario-Biografico)/"
LONGHI_URL = "https://www.treccani.it/enciclopedia/pietro-longhi_(Dizionario-Biografico)/"
DBI_SOURCE = "Treccani, Dizionario Biografico degli Italiani"

TARGETS = [
    {
        "candidate": "cand-0024",
        "group": "new-person:albrizzi-almoro-ac00ba2f26",
        "type": "person",
        "ku": "units/persons/almoro-albrizzi",
        "card": "04-knowledge/units/persons/almoro-albrizzi.md",
        "name_zh": "阿尔莫罗·阿尔布里齐",
        "name_en": "Almorò Albrizzi",
        "name_rows": [
            ("索引名", "Albrizzi, Almorò", "S1（索引 A.csv#23）"),
            ("正文姓名形式", "Almorò（印本；OCR作 Almord）", "S2（第13章 p.334；据页面图像校正）"),
        ],
        "book_sources": [
            {
                "citation": INDEX_CITATION,
                "location": "全书索引 A.csv#23；列页334",
                "summary": "索引将 Almorò 列于 Albrizzi 姓下，页码指向第13章 p.334。",
                "quote": "Albrizzi, Almorò",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/A.csv",
                "source_span": "A.csv#23",
                "doc_id": "patrons-and-painters",
            },
            {
                "citation": HASKELL_CITATION,
                "location": "第13章；印刷页334；OCR L26",
                "summary": "Haskell称 Albrizzi 的兄弟 Almorò 组织了 Accademia Albrizziana；S2依据页面图像将OCR Almord校为印本Almorò。",
                "quote": "His brother Almord organised a society, the Accademia Albrizziana",
                "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
                "source_span": "line 26; print p. 334; OCR Almord corrected to printed Almorò",
                "doc_id": "patrons-and-painters",
            },
            {
                "citation": f"Giorgio E. Ferrari, ‘ALBRIZZI, Almorò,’ *Dizionario Biografico degli Italiani*, vol. 2 (1960), Treccani. {ALBRIZZI_URL} Accessed {DATE}.",
                "location": "人物名及创办 Accademia Albrizziana 的段落",
                "summary": "Treccani条目将人物列作Almorò（Ermolao）Albrizzi，并称其于1724年创办同名学院、主持至1744年；本条用于身份比较，不验证Haskell的关系断言。",
                "quote": "dette vita ... alla famosa Accademia Albrizziana",
                "source_file": ALBRIZZI_URL,
                "source_span": "entry heading and academy paragraph",
                "doc_id": "treccani-dbi-almoro-albrizzi-1960",
            },
        ],
        "description_zh": "本卡指索引所列、并在第13章 p.334 被称为 Albrizzi 之兄的 Almorò Albrizzi。Treccani《意大利人传记辞典》以 Almorò（Ermolao）Albrizzi 为条目名，并记载他创办 Accademia Albrizziana。该身份与第9章所述 Pisani 家族之子 Almorò 不同；不因同名而合并。",
        "description_en": "This card identifies the Almorò indexed under Albrizzi and described on p.334 as Albrizzi’s brother. Treccani’s *Dizionario Biografico degli Italiani* gives the entry name Almorò (Ermolao) Albrizzi and records his founding of the Accademia Albrizziana. He is distinct from the Pisani family’s son Almorò discussed in Chapter 9; the shared given name does not imply identity.",
        "context_zh": "第13章称 Almorò 组织了 Accademia Albrizziana，并将其描述为关注文学与科学的学会。Treccani记载同名学院于1724年创办、由Almorò主持至1744年。S2候选 st-chp13-p334-almoro-organized-academy 保留待S6；该句不据此扩写成员或关系。",
        "context_en": "Chapter 13 says Almorò organised the Accademia Albrizziana, described as a society concerned with literary and scientific matters. Treccani records the same-named academy as founded in 1724 and governed by Almorò until 1744. S2 candidate st-chp13-p334-almoro-organized-academy remains for S6; no membership or additional relationship is inferred.",
        "identity_zh": f"[Treccani DBI：Almorò Albrizzi]({ALBRIZZI_URL.replace('(', '%28').replace(')', '%29')})：条目名为 Almorò（Ermolao）Albrizzi，记其创办 Accademia Albrizziana。与 cand-1941 的 Almorò Pisani 分开；此来源支持身份比较，不验证 Haskell 的学会组织关系。",
        "identity_en": f"[Treccani DBI: Almorò Albrizzi]({ALBRIZZI_URL.replace('(', '%28').replace(')', '%29')}) identifies the entry as Almorò (Ermolao) Albrizzi and records his founding of the Accademia Albrizziana. He remains distinct from cand-1941, Almorò Pisani; this source supports identity comparison, not Haskell’s organizational claim.",
        "relation_ids": ["st-chp13-p334-almoro-organized-academy"],
        "relation_zh": "该 S2 候选仍待 S6，不在本次 S4 登记中建立正式关系。",
        "relation_en": "This S2 candidate remains for S6; this S4 registration creates no formal relation.",
        "expected_endpoints": {
            "st-chp13-p334-almoro-organized-academy": ("cand-0024", "cand-0001", "organized_literary_and_scientific_society")
        },
    },
    {
        "candidate": "cand-1941",
        "group": "new-person:almoro-pisani-44c6067e62",
        "type": "person",
        "ku": "units/persons/almoro-pisani",
        "card": "04-knowledge/units/persons/almoro-pisani.md",
        "name_zh": "阿尔莫罗·皮萨尼",
        "name_en": "Almorò Pisani",
        "name_rows": [
            ("索引名", "Pisani, Almorò", "S1（索引 P.csv#142）"),
            ("正文姓名形式", "Almorò（印本；OCR Almorô／Almord）", "S2–S4（第9章 pp.255、260–261；据页面图像校正）"),
        ],
        "book_sources": [
            {
                "citation": INDEX_CITATION,
                "location": "全书索引 P.csv#142；列页260–261",
                "summary": "索引将 Almorò 列于 Pisani 姓下，页码指向第9章 pp.260–261。",
                "quote": "Pisani, Almorò",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/P.csv",
                "source_span": "P.csv#142",
                "doc_id": "patrons-and-painters",
            },
            {
                "citation": HASKELL_CITATION,
                "location": "第9章；印刷页255；OCR L149–150",
                "summary": "Haskell称Almorò为Pisani家族最年幼的儿子，并将其置于家族寓意壁画的在世成员之中。",
                "quote": "its youngest son, Almorô, seated in his mother’s lap",
                "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "source_span": "lines 149–150; print p. 255; OCR Almorô corrected to printed Almorò",
                "doc_id": "patrons-and-painters",
            },
            {
                "citation": HASKELL_CITATION,
                "location": "第9章；印刷页260；OCR L208",
                "summary": "Haskell称Pisani家族组织私人学院，由Pietro Longhi主持；学院似乎主要为其子Almorò提供绘画课，并在他去世时结束。",
                "quote": "the Pisani organised a private academy with Pietro Longhi in charge",
                "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "source_span": "line 208; print p. 260; OCR Almord corrected to printed Almorò",
                "doc_id": "patrons-and-painters",
            },
            {
                "citation": HASKELL_CITATION,
                "location": "第9章；印刷页261；OCR L214",
                "summary": "Haskell称Pisani家族在Almorò的青年时期（1740–66）曾赞助风景画家Giuseppe Zais，并称Almorò本人为业余艺术家；该时间范围照录，不视为其生卒年。",
                "quote": "during the youth of Almord (1740-66), himself an amateur artist",
                "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "source_span": "line 214; print p. 261; OCR Almord corrected to printed Almorò",
                "doc_id": "patrons-and-painters",
            },
            {
                "citation": f"Francesco Sorce, ‘LONGHI, Pietro,’ *Dizionario Biografico degli Italiani*, vol. 65 (2005), Treccani. {LONGHI_URL} Accessed {DATE}.",
                "location": "Pietro Longhi人物条目中Sagredo家族画像及Pisani学院段落",
                "summary": "Treccani在Longhi条目中称Marina Sagredo之子为Almorò Pisani，并称Longhi于1763年主持为该子设立的绘画与雕刻学院，至年轻Almorò于1766年去世。该为交叉身份依据，非Almorò本人的外部标识。",
                "quote": "per il figlio Almorò Pisani",
                "source_file": LONGHI_URL,
                "source_span": "paras. on the Sagredo family portrait and the academy",
                "doc_id": "treccani-dbi-pietro-longhi-2005",
            },
        ],
        "description_zh": "本卡指第9章称为 Pisani 家族最年幼儿子、并在索引列作 Almorò Pisani 的人物。Treccani 的 Pietro Longhi 条目也将 Marina Sagredo 之子称为 Almorò Pisani，并记载其于1766年去世。第13章的 Almorò Albrizzi 是另一人；姓氏、家族角色和外部记载均支持分组。",
        "description_en": "This card identifies the person called the Pisani family’s youngest son in Chapter 9 and indexed as Almorò Pisani. Treccani’s Pietro Longhi entry also names Marina Sagredo’s son as Almorò Pisani and records his death in 1766. The Almorò Albrizzi in Chapter 13 is a different person; the surnames, family roles, and external account support separate identity groups.",
        "context_zh": "第9章 p.255 将 Almorò 置于Pisani家族寓意壁画的在世成员中；p.260称他是私人学院绘画课的对象，并称学院在其去世时结束；p.261称他为业余艺术家。p.261括号中的1740–66按Haskell原文保留为青年时期语境，不作为生卒年。相关关系候选 st-chp9-p260-academy-lessons-end 留待S6。",
        "context_en": "On p.255, Chapter 9 places Almorò among the living members represented in a Pisani family allegory. Page 260 describes him as the subject of drawing lessons at a private academy and says it ended at his death; p.261 calls him an amateur artist. The parenthetical 1740–66 on p.261 is retained as Haskell’s context for his youth, not treated as birth and death dates. Relation candidate st-chp9-p260-academy-lessons-end remains for S6.",
        "identity_zh": f"[Treccani DBI：Pietro Longhi]({LONGHI_URL.replace('(', '%28').replace(')', '%29')})在画像及学院语境中将Marina Sagredo之子称作Almorò Pisani，并记年轻Almorò于1766年去世。该条目主题是Longhi，故仅用于姓名与语境比较，不把其URL当作Almorò本人的外部标识。与Almorò Albrizzi分开。",
        "identity_en": f"[Treccani DBI: Pietro Longhi]({LONGHI_URL.replace('(', '%28').replace(')', '%29')}) names Marina Sagredo’s son as Almorò Pisani in its portrait and academy context and records the young Almorò’s death in 1766. The entry is about Longhi, so it is used only for name and context comparison; its URL is not treated as an external identifier for Almorò. He remains distinct from Almorò Albrizzi.",
        "relation_ids": ["st-chp9-p260-academy-lessons-end"],
        "relation_zh": "该S2关系候选保留待S6；本卡不登记Almorò与学院的正式关系。",
        "relation_en": "This S2 relation candidate remains for S6; this card registers no formal relation between Almorò and the academy.",
        "expected_endpoints": {
            "st-chp9-p260-academy-lessons-end": ("cand-8496", "cand-1941", "academy_limited_to_drawing_lessons_and_ended_at_sons_death")
        },
    },
    {
        "candidate": "cand-0001",
        "group": "sg3-institution-cand-0001",
        "type": "institution",
        "ku": "units/institutions/accademia-albrizziana",
        "card": "04-knowledge/units/institutions/accademia-albrizziana.md",
        "name_zh": "阿尔布里齐学会",
        "name_en": "Accademia Albrizziana",
        "name_rows": [("书内名称", "Accademia Albrizziana", "S1（索引 A.csv#0）；S2（第13章 p.334）")],
        "book_sources": [
            {
                "citation": INDEX_CITATION,
                "location": "全书索引 A.csv#0；列页334",
                "summary": "索引将Accademia Albrizziana列为第13章p.334的机构项。",
                "quote": "Accademia Albrizziana",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/A.csv",
                "source_span": "A.csv#0",
                "doc_id": "patrons-and-painters",
            },
            {
                "citation": HASKELL_CITATION,
                "location": "第13章；印刷页334；OCR L26",
                "summary": "Haskell称Almorò Albrizzi组织该学会，并说其关注文学与科学现象。",
                "quote": "the Accademia Albrizziana, which concerned itself with literary and scientific phenomena",
                "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
                "source_span": "line 26; print p. 334",
                "doc_id": "patrons-and-painters",
            },
            {
                "citation": f"Giorgio E. Ferrari, ‘ALBRIZZI, Almorò,’ *Dizionario Biografico degli Italiani*, vol. 2 (1960), Treccani. {ALBRIZZI_URL} Accessed {DATE}.",
                "location": "人物条目中Accademia Albrizziana的创办与主持段落",
                "summary": "Treccani称Almorò于1724年创办Accademia Albrizziana，并主持至1744年；作为名称及身份交叉核对，不借用人物条目作机构标识。",
                "quote": "alla famosa Accademia Albrizziana",
                "source_file": ALBRIZZI_URL,
                "source_span": "academy paragraph",
                "doc_id": "treccani-dbi-almoro-albrizzi-1960",
            },
        ],
        "description_zh": "本卡登记第13章 p.334 和索引明确命名的 Accademia Albrizziana。Haskell将其描述为关注文学与科学的学会，并称Almorò Albrizzi组织该学会；Treccani记录Almorò于1724年创办同名学院。中文名称为工作译名。",
        "description_en": "This card records the Accademia Albrizziana named in Chapter 13, p.334, and in the index. Haskell describes it as a society concerned with literary and scientific matters and says Almorò Albrizzi organised it; Treccani records his founding of the same-named academy in 1724. The Chinese rendering is a working translation.",
        "context_zh": "本卡指文学与科学学会，不是既有Albrizziana印刷所 units/institutions/albrizziana-printing-house-venice。它也不同于Pisani家族为Almorò设立、由Pietro Longhi主持的私人绘画学院，以及佛罗伦萨的Accademia del Disegno。候选 st-chp13-p334-almoro-organized-academy 留待S6。",
        "context_en": "This card refers to the literary and scientific society, not the existing Albrizziana printing house, units/institutions/albrizziana-printing-house-venice. It is also distinct from the private drawing academy established for the Pisani family’s Almorò under Pietro Longhi and from Florence’s Accademia del Disegno. Candidate st-chp13-p334-almoro-organized-academy remains for S6.",
        "identity_zh": f"[Treccani DBI：Almorò Albrizzi]({ALBRIZZI_URL.replace('(', '%28').replace(')', '%29')})记载他创办同名学院。该人物条目支持本机构名称与创办者的交叉辨认，不提供本机构的独立规范标识。",
        "identity_en": f"[Treccani DBI: Almorò Albrizzi]({ALBRIZZI_URL.replace('(', '%28').replace(')', '%29')}) records his founding of the same-named academy. The person entry supports cross-identification of the institution name and founder but does not supply an independent institutional identifier.",
        "relation_ids": ["st-chp13-p334-almoro-organized-academy"],
        "relation_zh": "S2记载的组织关系留待S6，本批不写入正式关系表。",
        "relation_en": "The organizational claim recorded in S2 remains for S6 and is not written to the formal relation table in this batch.",
        "expected_endpoints": {
            "st-chp13-p334-almoro-organized-academy": ("cand-0024", "cand-0001", "organized_literary_and_scientific_society")
        },
    },
    {
        "candidate": "cand-8496",
        "group": "sg3-institution-cand-8496",
        "type": "institution",
        "ku": "units/institutions/pisani-private-academy",
        "card": "04-knowledge/units/institutions/pisani-private-academy.md",
        "name_zh": "皮萨尼家族私人学院",
        "name_en": "Pisani family private academy under Pietro Longhi",
        "name_rows": [("来源称谓", "a private academy", "S1（第9章 p.260）")],
        "book_sources": [
            {
                "citation": HASKELL_CITATION,
                "location": "第9章；印刷页260；OCR L208",
                "summary": "Haskell称Pisani家族组织了一所由Pietro Longhi主持的私人学院；该学院似乎主要为家族之子Almorò提供绘画课，并在其去世时结束。",
                "quote": "the Pisani organised a private academy with Pietro Longhi in charge",
                "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "source_span": "line 208; print p. 260",
                "doc_id": "patrons-and-painters",
            },
            {
                "citation": f"Francesco Sorce, ‘LONGHI, Pietro,’ *Dizionario Biografico degli Italiani*, vol. 65 (2005), Treccani. {LONGHI_URL} Accessed {DATE}.",
                "location": "Longhi任Pisani家族学院负责人的段落",
                "summary": "Treccani称Marina Sagredo为儿子Almorò Pisani设立绘画与雕刻学院，并记Longhi于1763年受命主持至1766年Almorò去世；用于与Haskell匿名私人学院的身份比较，不作为机构专属标识。",
                "quote": "Accademia di disegno e incisione, istituita da Marina Sagredo per il figlio Almorò Pisani",
                "source_file": LONGHI_URL,
                "source_span": "academy paragraph",
                "doc_id": "treccani-dbi-pietro-longhi-2005",
            },
        ],
        "description_zh": "本卡登记Haskell在第9章 p.260 描述的Pisani家族私人学院。原书未给出专名；中文与英文标题均为描述性暂名。Haskell称Pietro Longhi负责该院，学院似乎主要向Pisani之子Almorò提供绘画课，并在其去世时结束。",
        "description_en": "This card records the Pisani family’s private academy described by Haskell in Chapter 9, p.260. The source supplies no proper name; both display titles are descriptive labels. Haskell says Pietro Longhi was in charge, that the academy seems to have mainly provided drawing lessons to the Pisani’s son Almorò, and that it ended at his death.",
        "context_zh": "Treccani的Pietro Longhi条目记载，Marina Sagredo为儿子Almorò Pisani设立绘画与雕刻学院，Longhi于1763年受命主持，并任至Almorò于1766年去世。该交叉语境支持本候选对应这所私人学院；原书“seems”仍保留，不扩大其活动范围。它与Accademia Albrizziana及佛罗伦萨Accademia del Disegno分别登记。",
        "context_en": "Treccani’s Pietro Longhi entry says Marina Sagredo established an academy of drawing and engraving for her son Almorò Pisani, that Longhi was appointed director in 1763, and that he held the post until Almorò died in 1766. This context supports identifying the candidate with that private academy; Haskell’s “seems” is retained and the institution’s activity is not expanded. It remains distinct from the Accademia Albrizziana and Florence’s Accademia del Disegno.",
        "identity_zh": f"[Treccani DBI：Pietro Longhi]({LONGHI_URL.replace('(', '%28').replace(')', '%29')})记载为Almorò Pisani设立的绘画与雕刻学院及Longhi任职年份。该条目主题为Longhi，不把URL当作机构标识；Haskell所称私人学院与该记载按创办者、受教者及负责人相互核对。",
        "identity_en": f"[Treccani DBI: Pietro Longhi]({LONGHI_URL.replace('(', '%28').replace(')', '%29')}) records the academy of drawing and engraving established for Almorò Pisani and Longhi’s term. The entry is about Longhi, so its URL is not treated as an institutional identifier; the Haskell reference is compared with it by founder, pupil, and director.",
        "relation_ids": ["st-chp9-p260-pisani-private-academy", "st-chp9-p260-academy-lessons-end"],
        "relation_zh": "Pisani家族组织学院及学院向Almorò授课、在其去世时结束两项S2候选均留待S6；本批没有新增正式边。",
        "relation_en": "Both S2 candidates, concerning the Pisani family’s organization of the academy and its lessons for Almorò and ending at his death, remain for S6; this batch adds no formal edge.",
        "expected_endpoints": {
            "st-chp9-p260-pisani-private-academy": ("cand-8500", "cand-8496", "pisani_organized_private_academy_with_longhi_in_charge"),
            "st-chp9-p260-academy-lessons-end": ("cand-8496", "cand-1941", "academy_limited_to_drawing_lessons_and_ended_at_sons_death"),
        },
    },
    {
        "candidate": "cand-0004",
        "group": "sg3-institution-cand-0004",
        "type": "institution",
        "ku": "units/institutions/accademia-del-disegno-florence",
        "card": "04-knowledge/units/institutions/accademia-del-disegno-florence.md",
        "name_zh": "佛罗伦萨设计学院",
        "name_en": "Accademia del Disegno in Florence",
        "name_rows": [
            ("索引名", "Accademia del Disegno", "S1（索引 A.csv#3）"),
            ("地点辨识称谓", "Accademia di Disegno in Florence", "S3（第10章 p.330 注3）"),
        ],
        "book_sources": [
            {
                "citation": INDEX_CITATION,
                "location": "全书索引 A.csv#3；列页241",
                "summary": "索引列Accademia del Disegno，页码指向佛罗伦萨展览及学院叙述。",
                "quote": "Accademia del Disegno",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/A.csv",
                "source_span": "A.csv#3",
                "doc_id": "patrons-and-painters",
            },
            {
                "citation": HASKELL_CITATION,
                "location": "第8章第II节；印刷页241；OCR L367",
                "summary": "Haskell称该Accademia del Disegno为1706年展览提供名义支持；费迪南德患病后学院恢复先前的不活跃状态。",
                "quote": "the Accademia del Disegno, under whose auspices it had been organised",
                "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "source_span": "line 367; print p. 241",
                "doc_id": "patrons-and-painters",
            },
            {
                "citation": HASKELL_CITATION,
                "location": "第10章第II节；印刷页330；注3；OCR L348",
                "summary": "Haskell注3说明Vasari的Life记载佛罗伦萨Accademia di Disegno的形成；该注与第8章p.241共同限定本候选地点。",
                "quote": "the formation of the Accademia di Disegno in Florence",
                "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "source_span": "line 348; print p. 330, n. 3",
                "doc_id": "patrons-and-painters",
            },
        ],
        "description_zh": "本卡登记第8章 p.241 称为 Accademia del Disegno、并由第10章 p.330 注3明确定位在佛罗伦萨的机构。中文名为描述性译名。此为佛罗伦萨机构，不与威尼斯的Accademia Albrizziana或Pisani家族私人学院合并。",
        "description_en": "This card records the institution called the Accademia del Disegno on p.241 of Chapter 8 and located in Florence by Chapter 10, p.330 n.3. The Chinese rendering is descriptive. This is the Florentine institution, distinct from the Venetian Accademia Albrizziana and the Pisani family’s private academy.",
        "context_zh": "第8章 p.241 称1706年展览在该院名义支持下举办，费迪南德患病后学院回到此前的不活跃状态。第10章 p.330 注3称Vasari的Life记载佛罗伦萨Accademia di Disegno的形成，作为跨章身份锚点。展览候选 st-chp8-p241-academy-organized-exhibition 及书目候选 st-chp10-p330-n03-vasari-life 仍待S6；相关对端仍未全部登记。",
        "context_en": "Chapter 8, p.241, says the 1706 exhibition was held under the academy’s auspices and that the academy returned to its prior inactivity after Ferdinand fell ill. Chapter 10, p.330 n.3, says Vasari’s Life describes the formation of the Accademia di Disegno in Florence and serves as a cross-chapter identity anchor. Candidates st-chp8-p241-academy-organized-exhibition and st-chp10-p330-n03-vasari-life remain for S6; their other endpoints are not all registered.",
        "identity_zh": "第8章 p.241 的展览语境与第10章 p.330 注3对佛罗伦萨的明确定位共同支持跨章同一机构组；不与威尼斯两所学院合并。",
        "identity_en": "The exhibition context on p.241 of Chapter 8 and the explicit Florentine location in Chapter 10, p.330 n.3, support one cross-chapter institution group; it is not merged with either Venetian academy.",
        "relation_ids": ["st-chp8-p241-academy-organized-exhibition", "st-chp10-p330-n03-vasari-life"],
        "relation_zh": "前者的展览对象cand-7977为S3 undecided；后者的Vasari文献cand-9864尚待S4。两项均不在本批登记正式关系。",
        "relation_en": "The exhibition object cand-7977 in the first candidate remains S3 undecided; the Vasari source cand-9864 in the second awaits S4. Neither is registered as a formal relation in this batch.",
        "expected_endpoints": {
            "st-chp8-p241-academy-organized-exhibition": ("cand-0004", "cand-7977", "organized_exhibition_under_its_auspices"),
            "st-chp10-p330-n03-vasari-life": ("cand-9864", "cand-0004", "has_subject"),
        },
    },
]


def make_card(t: dict) -> str:
    sources = []
    for source in t["book_sources"]:
        sources.append(
            {
                "citation": source["citation"],
                "location": source["location"],
                "sentence_summary": source["summary"],
                "original_quotes": [{"source_span": source["source_span"], "text": source["quote"]}],
                "evidence_ref": {
                    "doc_id": source["doc_id"],
                    "source_file": source["source_file"],
                    "source_span": source["source_span"],
                },
            }
        )
    frontmatter = {
        "title": f"{t['name_zh']}（{t['name_en']}）",
        "name_en": t["name_en"],
        "type": t["type"],
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000).rstrip()
    name_rows = "\n".join(f"| {field} | {value} | {evidence} |" for field, value, evidence in t["name_rows"])
    identity_section = ""
    if t.get("identity_zh"):
        identity_section = (
            "\n\n### 身份与外部链接\n\n"
            f"**中文：** {t['identity_zh']}\n\n**English:** {t['identity_en']}"
        )
    return (
        f"---\n{fm}\n---\n\n## 内容\n\n### 描述\n\n"
        f"**中文：** {t['description_zh']}\n\n**English:** {t['description_en']}\n\n"
        f"### 名称\n\n| 字段 | 值 | 证据 |\n|---|---|---|\n{name_rows}\n\n"
        f"### 本书语境\n\n**中文：** {t['context_zh']}\n\n**English:** {t['context_en']}\n\n"
        f"## 关系与证据{identity_section}\n\n### 关系记录\n\n"
        "当前没有正式关系。正文中的导航与线索不自动形成关系边。\n\n"
        f"**中文：** {t['relation_zh']}\n\n**English:** {t['relation_en']}\n"
    )


def extract_card_fields(cards: dict[str, str]) -> tuple[list[dict], dict, list[str], int]:
    from scripts import build_field_facts
    from scripts.build_field_facts import extract_records

    with tempfile.TemporaryDirectory(prefix="pnp-s4-almoro-academy-") as temp_root:
        temp_base = Path(temp_root)
        rows = []
        for t in TARGETS:
            temp_card = temp_base / t["card"]
            temp_card.parent.mkdir(parents=True, exist_ok=True)
            temp_card.write_text(cards[t["card"]], encoding="utf-8")
            rows.append({"ku_id": t["ku"], "card_path": t["card"]})
        previous_base = build_field_facts.BASE
        build_field_facts.BASE = temp_base
        try:
            return extract_records(rows)
        finally:
            build_field_facts.BASE = previous_base


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False) as handle:
        temp_path = Path(handle.name)
        handle.write(content)
    try:
        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def with_bom(text: str, original: bytes | None = None) -> bytes:
    encoded = text.encode("utf-8")
    if original is None or original.startswith(b"\xef\xbb\xbf"):
        return b"\xef\xbb\xbf" + encoded
    return encoded


def main() -> int:
    parser = argparse.ArgumentParser(description="Register five cross-chapter academy/person S3 groups in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    base = helper.base
    sync = base.sync
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_lines = accepted.splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [
        json.loads(line)
        for line in STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    statement_by_id = {row["statement_id"]: row for row in statements}
    cards = {t["card"]: make_card(t) for t in TARGETS}
    card_paths = {t["card"]: ROOT / t["card"] for t in TARGETS}

    for t in TARGETS:
        candidate = candidate_by_id[t["candidate"]]
        alignment = alignment_by_id[t["candidate"]]
        assert candidate.get("suggested_type") == t["type"], (t["candidate"], candidate.get("suggested_type"))
        assert alignment.get("decision") == "new", (t["candidate"], alignment.get("decision"))
        assert base.sync.get_group(alignment.get("resolution_note", "")) == t["group"]
        members = [
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new"
            and base.sync.get_group(row.get("resolution_note", "")) == t["group"]
        ]
        assert members == [t["candidate"]], (t["group"], members)
        direct = {
            row["statement_id"] for row in statements
            if (row.get("qualifiers") or {}).get("relation_candidate") is True
            and (row.get("subject_candidate_id") == t["candidate"] or row.get("object_candidate_id") == t["candidate"])
        }
        assert direct == set(t["expected_endpoints"]), (t["candidate"], direct)
        for sid, (subject, obj, predicate) in t["expected_endpoints"].items():
            statement = statement_by_id[sid]
            assert statement.get("subject_candidate_id") == subject
            assert statement.get("object_candidate_id") == obj
            assert statement.get("predicate") == predicate
        if t["candidate"] == "cand-0024":
            assert candidate.get("index_entry_id") == "A.csv#23"
            assert candidate.get("canonical_name") == "Albrizzi, Almorò"
        elif t["candidate"] == "cand-1941":
            assert candidate.get("index_entry_id") == "P.csv#142"
            assert candidate.get("canonical_name") == "Pisani, Almorò"
        elif t["candidate"] == "cand-0001":
            assert candidate.get("index_entry_id") == "A.csv#0"
            assert candidate.get("canonical_name") == "Accademia Albrizziana"
        elif t["candidate"] == "cand-8496":
            assert "Pisani" in candidate.get("canonical_name", "")
            assert "no formal name" in " ".join(s["summary"] for s in t["book_sources"]).lower() or "private academy" in candidate.get("canonical_name", "").lower()
        elif t["candidate"] == "cand-0004":
            assert candidate.get("index_entry_id") == "A.csv#3"
            assert candidate.get("canonical_name") == "Accademia del Disegno"
        if alignment.get("ku_id"):
            assert alignment.get("ku_id") == t["ku"]
        else:
            assert t["ku"] not in manifest_by_ku
            assert t["card"] not in accepted_paths and not card_paths[t["card"]].exists()

    # Verify the source excerpts used in the new cards against the preserved source files.
    for t in TARGETS:
        for source in t["book_sources"]:
            if source["source_file"].startswith("https://"):
                continue
            if source["source_file"].endswith(".csv"):
                continue
            source_text = (ROOT / source["source_file"]).read_text(encoding="utf-8-sig")
            normalized_source = re.sub(r"\s+", " ", source_text)
            normalized_quote = re.sub(r"\s+", " ", source["quote"])
            assert normalized_quote in normalized_source, (t["candidate"], source["source_span"])

    # All five groups must be either wholly pending or wholly registered; partial state is reconciled manually.
    pending = [t for t in TARGETS if not alignment_by_id[t["candidate"]].get("ku_id")]
    if not pending:
        for t in TARGETS:
            assert alignment_by_id[t["candidate"]].get("ku_id") == t["ku"]
            assert card_paths[t["card"]].read_text(encoding="utf-8-sig") == cards[t["card"]]
            assert t["card"] in accepted_paths
            assert manifest_by_ku[t["ku"]].get("card_path") == t["card"]
        external = [
            row for row in alignments
            if row.get("candidate_id") == "cand-0024"
            and row.get("external_source") == DBI_SOURCE
            and row.get("external_id") == ALBRIZZI_URL
        ]
        assert len(external) == 1 and external[0].get("ku_id") == "units/persons/almoro-albrizzi"
        print("ALREADY REGISTERED: five S3 groups, five KU mappings, and the Albrizzi identity row are present.")
        return 0
    assert len(pending) == len(TARGETS), [t["candidate"] for t in pending]

    before_stats = sync.summarize_by_type(candidates, alignments)
    planned_alignments = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    planned_accepted = list(accepted_lines)
    for t in TARGETS:
        alignment = next(
            row for row in planned_alignments
            if row.get("candidate_id") == t["candidate"] and not row.get("external_source")
        )
        alignment["ku_id"] = t["ku"]
        alignment["process_ref"] = PROCESS_REF
        if t["candidate"] == "cand-0024":
            alignment["resolution_note"] = (
                "source_ref=A.csv#23;S2=chp-13:p.334;group=new-person:albrizzi-almoro-ac00ba2f26; "
                "S3 cross-chapter comparison 2026-10-17: Treccani DBI identifies Almorò (Ermolao) Albrizzi and records his founding of the Accademia Albrizziana; "
                "the source-local candidate is distinct from the Pisani family’s Almorò (cand-1941), whose son/student context and 1766 death are corroborated by the separate Treccani Longhi entry. "
                "New relative to existing KUs; same given name does not merge the two people. S4 mapped to units/persons/almoro-albrizzi."
            )
        elif t["candidate"] == "cand-1941":
            alignment["resolution_note"] = (
                "source_ref=P.csv#142;S2=chp-9:pp.255,260-261;group=new-person:almoro-pisani-44c6067e62; "
                "S3 cross-chapter comparison 2026-10-17: Haskell identifies the Pisani family’s son Almorò; Treccani DBI’s Longhi entry names Marina Sagredo’s son Almorò Pisani and records his death in 1766. "
                "Keep distinct from Almorò Albrizzi (cand-0024), whose Treccani person entry gives a different family identity and a 1764 death. The Longhi article is comparative evidence, not an external identifier for this person. "
                "New source-local person group mapped in S4 to units/persons/almoro-pisani."
            )
        elif t["candidate"] == "cand-0001":
            alignment["resolution_note"] = (
                "source_ref=A.csv#0;S2=chp-13:p.334;group=sg3-institution-cand-0001; "
                "S3 cross-chapter type review 2026-10-17: Haskell names the Accademia Albrizziana as a literary and scientific society organized by Almorò Albrizzi; Treccani records the same-named academy as founded by him in 1724. "
                "Separate from the Albrizziana printing house (different institutional activity), the Pisani private drawing academy (different family, director, and purpose), and Florence’s Accademia del Disegno. New institution group mapped in S4 to units/institutions/accademia-albrizziana."
            )
        elif t["candidate"] == "cand-8496":
            alignment["resolution_note"] = (
                "source_ref=chp-9:p.260;group=sg3-institution-cand-8496; "
                "S3 cross-chapter type review 2026-10-17: Haskell describes an unnamed private academy organized by the Pisani with Pietro Longhi in charge; Treccani’s Longhi entry describes the drawing and engraving academy established for Almorò Pisani and Longhi’s 1763-1766 directorship, matching the same family, pupil, and director context. "
                "Keep distinct from the named Accademia Albrizziana and Florence’s Accademia del Disegno. Descriptive KU title is not a source-provided proper name. New institution group mapped in S4 to units/institutions/pisani-private-academy."
            )
        else:
            alignment["resolution_note"] = (
                "source_ref=A.csv#3;S2=chp-8:p.241, chp-10:p.330 n.3;group=sg3-institution-cand-0004; "
                "S3 cross-chapter review 2026-10-17: Chapter 8’s exhibition and inactivity account, together with Chapter 10’s explicit Florentine location for the Accademia di Disegno, identifies this as the Florentine academy. "
                "It is separate from the Venetian Accademia Albrizziana and the unnamed Pisani private academy. New institution group mapped in S4 to units/institutions/accademia-del-disegno-florence; related event and archive candidates remain unresolved."
            )
        alignment["resolution_note"] += f" S4 registration: {t['group']} -> {t['ku']}."
        planned_manifest.append(
            {
                "ku_id": t["ku"],
                "type": t["type"],
                "canonical_name": t["name_zh"],
                "name_en": t["name_en"],
                "source_task": TASK,
                "card_path": t["card"],
            }
        )
        planned_accepted = helper.base.insert_accepted(planned_accepted, t["card"])
    planned_manifest.sort(key=lambda row: row["ku_id"])

    max_alignment_id = max(
        (int(match.group(1)) for row in alignments if (match := re.fullmatch(r"aln-(\d+)", row.get("alignment_id", "")))),
        default=0,
    )
    assert not any(
        row.get("candidate_id") == "cand-0024" and row.get("external_source") == DBI_SOURCE and row.get("external_id") == ALBRIZZI_URL
        for row in alignments
    )
    external_row = {
        "alignment_id": f"aln-{max_alignment_id + 1:05d}",
        "candidate_id": "cand-0024",
        "ku_id": "units/persons/almoro-albrizzi",
        "external_source": DBI_SOURCE,
        "external_id": ALBRIZZI_URL,
        "decision": "same",
        "accessed_date": DATE,
        "process_ref": PROCESS_REF,
        "legacy_ku_id": "",
        "resolution_note": (
            "Identity comparison only: Giorgio E. Ferrari, ‘ALBRIZZI, Almorò,’ Dizionario Biografico degli Italiani, vol. 2 (1960), "
            "identifies Almorò (Ermolao) Albrizzi and records the Accademia Albrizziana as his foundation. Compared with Haskell index A.csv#23 and ch.13 p.334. "
            "Does not validate the book’s organizational relation claim."
        ),
    }
    planned_alignments.append(external_row)

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {key: sum(row[key] for row in before_stats.values()) for key in next(iter(before_stats.values()))}
    assert totals["registered_groups"] == before_totals["registered_groups"] + len(TARGETS)
    assert totals["registered_members"] == before_totals["registered_members"] + len(TARGETS)
    assert totals["pending_groups"] == before_totals["pending_groups"] - len(TARGETS)
    assert totals["pending_members"] == before_totals["pending_members"] - len(TARGETS)
    assert len(planned_manifest) == len(manifest) + len(TARGETS)

    additions, source_registry, warnings, cards_with_tables = extract_card_fields(cards)
    assert cards_with_tables == len(TARGETS) and len(additions) == 8, (cards_with_tables, len(additions))
    assert all(row.get("evidence_status") == "source_backed" for row in additions)
    assert not warnings, warnings
    existing_enrichment_text = ENRICHMENT_PATH.read_text(encoding="utf-8-sig")
    existing_enrichment = [json.loads(line) for line in existing_enrichment_text.splitlines() if line.strip()]
    natural_keys = {
        (row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id", ""))
        for row in existing_enrichment
    }
    existing_enrichment_ids = {row.get("enrichment_id", "") for row in existing_enrichment}
    max_enrichment_id = max(
        (int(match.group(1)) for value in existing_enrichment_ids if (match := re.fullmatch(r"enr-(\d+)", value))),
        default=0,
    )
    for offset, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_enrichment_id + offset:05d}"
        key = (row["ku_id"], row["field"], row["value"], row.get("source_id", ""))
        assert key not in natural_keys and row["enrichment_id"] not in existing_enrichment_ids
    planned_enrichment = existing_enrichment_text.rstrip("\n") + "\n" + "\n".join(
        json.dumps(row, ensure_ascii=False) for row in additions
    ) + "\n"

    process_text = helper.base.process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{S3_ANCHOR}"></a>' not in process_text
    assert f'<a id="{S4_ANCHOR}"></a>' not in process_text
    process_text += (
        f"\n\n<a id=\"{S3_ANCHOR}\"></a>\n\n### S3跨章复核：Almorò身份与三所学院区分（{DATE}）\n\n"
        f"- cand-0024为Almorò Albrizzi：索引A.csv#23及第13章p.334的Almorò与[Treccani DBI人物条目]({ALBRIZZI_URL.replace('(', '%28').replace(')', '%29')})相合（访问日期：{DATE}）；不与cand-1941混同。\n"
        f"- cand-1941为Pisani家族之子Almorò：第9章p.255、260–261的家族语境与[Treccani DBI的Longhi条目]({LONGHI_URL.replace('(', '%28').replace(')', '%29')})相合（访问日期：{DATE}）。该Longhi条目明确称Almorò Pisani，但不是其本人规范记录，故不借用其URL作为人物外部标识。p.261的1740–66不作生卒年。\n"
        "- cand-0001 Accademia Albrizziana与既有Albrizziana印刷所分开；其为文学与科学学会。cand-8496是为Pisani之子提供绘画课、由Longhi主持的私人学院；cand-0004由第8章展览语境及第10章p.330注3定位为佛罗伦萨Accademia del Disegno。三所机构的名称、组织者／受教者、用途或地点不同，不合并。cand-8500已same至Pisani di Santo Stefano家族卡，cand-1429已映射Pietro Longhi。\n"
        "- cand-7977仍为S3 undecided；Vasari文献cand-9864仍待S4。相关关系继续待S6。\n"
        f"\n\n<a id=\"{S4_ANCHOR}\"></a>\n\n### S4跨章学院与直接端点身份组登记（{DATE}）\n\n"
        "- cand-0024（new-person:albrizzi-almoro-ac00ba2f26）→ [阿尔莫罗·阿尔布里齐（Almorò Albrizzi）](../../../04-knowledge/units/persons/almoro-albrizzi.md)。Treccani DBI外部身份行仅支持该人物身份；组织学院的S2候选留待S6。\n"
        "- cand-1941（new-person:almoro-pisani-44c6067e62）→ [阿尔莫罗·皮萨尼（Almorò Pisani）](../../../04-knowledge/units/persons/almoro-pisani.md)。以来源支持的姓氏、家族角色和Treccani Longhi条目分开Albrizzi同名人物；学院授课候选留待S6。\n"
        "- cand-0001（sg3-institution-cand-0001）→ [阿尔布里齐学会（Accademia Albrizziana）](../../../04-knowledge/units/institutions/accademia-albrizziana.md)。不并入印刷所KU。\n"
        "- cand-8496（sg3-institution-cand-8496）→ [皮萨尼家族私人学院（Pisani family private academy under Pietro Longhi）](../../../04-knowledge/units/institutions/pisani-private-academy.md)。标题为描述性暂名，不冒充原书专名。\n"
        "- cand-0004（sg3-institution-cand-0004）→ [佛罗伦萨设计学院（Accademia del Disegno in Florence）](../../../04-knowledge/units/institutions/accademia-del-disegno-florence.md)。展览端点cand-7977待决，Vasari文献cand-9864待S4。\n\n"
        f"本批登记5个S3 new身份组、5条候选映射和1条Albrizzi外部身份行；抽取8条source_backed名称字段，不改sources.csv、candidate-backlog.csv或relations.csv，不新增正式关系。\n\n"
        f"登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"institution类型为{sync.fmt(stats['institution']['registered_groups'])}组/{sync.fmt(stats['institution']['registered_members'])}条已登记、{sync.fmt(stats['institution']['pending_groups'])}组/{sync.fmt(stats['institution']['pending_members'])}条待登记；"
        f"全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text += (
        f"\n\n### S3/S4跨章身份组登记：Almorò与三所学院（{DATE}）\n\n"
        "已区分Almorò Albrizzi与Almorò Pisani，并将Accademia Albrizziana、Pisani家族私人学院、佛罗伦萨Accademia del Disegno分别登记。"
        "cand-8500复用Pisani di Santo Stefano家族KU；cand-1429复用Pietro Longhi KU。cand-0024新增Treccani DBI外部身份行；Longhi条目用于cand-1941与Pisani学院的交叉比对，不借作实体标识。\n\n"
        "Albrizzi组织学会、Pisani学院与Almorò的授课／终止、佛罗伦萨学院与展览及Vasari文献等S2候选均留待S6；cand-7977仍S3 undecided，cand-9864仍待S4。未新增正式关系。"
        f"本批5组/5条候选映射；KU={len(planned_manifest)}，名称字段={len(existing_enrichment) + len(additions)}。详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{S4_ANCHOR})。"
    )

    # Stage every write in memory, then replace files atomically; restore all original bytes on any failure.
    temp_dir = Path(tempfile.mkdtemp(prefix="pnp-s4-almoro-csv-"))
    try:
        alignment_stage = temp_dir / "alignment.csv"
        manifest_stage = temp_dir / "ku-manifest.csv"
        sync.write_csv(alignment_stage, alignment_fields, planned_alignments)
        sync.write_csv(manifest_stage, manifest_fields, planned_manifest)
        staged = {
            alignment_stage: ALIGNMENT_PATH,
            manifest_stage: MANIFEST_PATH,
        }
        writes = {
            ALIGNMENT_PATH: alignment_stage.read_bytes(),
            MANIFEST_PATH: manifest_stage.read_bytes(),
            ENRICHMENT_PATH: with_bom(planned_enrichment, ENRICHMENT_PATH.read_bytes()),
            ACCEPTED_PATH: with_bom("\n".join(planned_accepted) + "\n", ACCEPTED_PATH.read_bytes()),
            PROCESS_PATH: with_bom(process_text + "\n", PROCESS_PATH.read_bytes()),
            RESULT_PATH: with_bom(result_text + "\n", RESULT_PATH.read_bytes()),
        }
        for t in TARGETS:
            writes[card_paths[t["card"]]] = with_bom(cards[t["card"]])
    finally:
        for path in temp_dir.glob("*"):
            path.unlink()
        temp_dir.rmdir()

    if args.dry_run:
        print("S3/S4 dry-run passed: five singleton groups, two person groups, three distinct institution groups.")
        print("candidate_mappings=5; external_identity_rows=1 (Albrizzi person); source_backed_name_fields=8")
        print("relations_pending=st-chp13-p334-almoro-organized-academy,st-chp9-p260-pisani-private-academy,st-chp9-p260-academy-lessons-end,st-chp8-p241-academy-organized-exhibition,st-chp10-p330-n03-vasari-life")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; KU={len(planned_manifest)}")
        print("formal_relations_added=0; candidate_backlog_changed=0; sources_registry_changed=0; no files changed")
        return 0

    originals = {path: path.read_bytes() if path.exists() else None for path in writes}
    try:
        for path, content in writes.items():
            atomic_write(path, content)
    except Exception:
        for path, content in originals.items():
            if content is None:
                if path.exists():
                    path.unlink()
            else:
                atomic_write(path, content)
        raise
    print(
        f"applied: groups=5; candidate_mappings=5; external_identity_rows=1; name_fields={len(additions)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; KU={len(planned_manifest)}; formal_relations_added=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
