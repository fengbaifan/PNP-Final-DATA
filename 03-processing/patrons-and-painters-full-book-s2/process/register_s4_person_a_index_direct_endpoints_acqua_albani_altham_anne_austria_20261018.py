from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_s_index_endpoints_schut_segala_serlio_skala_20261018 as registrar  # noqa: E402

registrar.ANCHOR = "s4-acqua-albani-altham-anne-austria-person-endpoints-20261018"
registrar.PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    "s4-acqua-albani-altham-anne-austria-person-endpoints-20261018"
)
registrar.BATCH_TITLE = "Acqua、Albani、Altham与Anne of Austria四组人物端点"
registrar.BATCH_PROCESS_NOTE = (
    "四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和8条source_backed姓名字段。"
    "Cristoforo dall’Acqua仅依索引及第10章p.327的具名与版画记述登记；Haskell转述的Moschini说法及版画年代论证不视为独立查证，也不把未涉Pisani失势扩成正式关系。"
    "Albani仅按索引全名及第6章脚注中的姓氏登记；脚注说d’Adda在Gozzadini和Albani支持下未能邀Viani赴罗马，不改写为Albani独立发起。"
    "James Altham依据索引、正文与脚注登记；脚注归属和日期仍为Haskell的记述，不将三位游客、城市与图版作一一对应。"
    "Anne of Austria仅按索引及第7章p.182的regent称谓登记，保留Haskell对Mazarin nominal dependence的原有限定，不扩展为宪制判断。"
    "六条相关S2关系候选留待S6；无外部来源、正式关系或backlog写入。"
)
registrar.BATCH_RESULT_NOTE = (
    "；dall’Acqua的两条版画陈述、Albani参与支持d’Adda邀Viani、Altham肖像／游客陈述及Anne of Austria语境关系均留待S6；"
    "不新增外部来源或正式关系。"
)
registrar.TARGETS = [
    {
        "candidate": "cand-0010",
        "group": "new-person:acqua-cristoforo-dall-b6b5d0c035",
        "ku": "units/persons/cristoforo-dall-acqua",
        "card": "04-knowledge/units/persons/cristoforo-dall-acqua.md",
        "name_zh": "克里斯托福罗·达尔阿夸",
        "name_en": "Cristoforo dall’Acqua",
        "index_entry": "A.csv#9",
        "index_name": "Acqua, Cristoforo dall'",
        "index_page": "327",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "第10章第II节，印刷页327，行235",
                "line 235; print p. 327",
                "Cristoforo dall’Acqua, the engraver of the emblematic pictures",
                "Haskell称Cristoforo dall’Acqua为寓意画的雕刻师，并转述他未涉Pisani失势的说法。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "第10章第II节，印刷页327，行237",
                "line 237; print p. 327",
                "Not only are the prints by Cristoforo dall’Acqua",
                "Haskell称dall’Acqua的版画早于1780年，并转述Moschini将其与Giorgio Pisani的入城仪式相联系；Moschini原页未独立查阅。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Acqua, Cristoforo dall'", "S1，A.csv#9"),
            ("正文全名", "Cristoforo dall’Acqua", "S2，第10章第II节，p.327，L235、L237"),
        ],
        "relation_ids": [
            "st-chp10-p327-n03-prints-predate-election",
            "st-chp10-p327-n03-moschini-prints-at-entry",
        ],
        "description_zh": (
            "本卡登记书后索引主条“Acqua, Cristoforo dall'”及第10章第327页正文具名的Cristoforo dall’Acqua；"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Acqua, Cristoforo dall'” and Cristoforo dall’Acqua named in Chapter 10 on page 327; "
            "the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell称他为寓意画的雕刻师，并在讨论Pisani入城仪式时提及其版画；版画年代与Moschini转述均按原书归因保留。"
            "Haskell另称他未涉Pisani失势，不将该否定陈述转成其他关系。"
        ),
        "context_en": (
            "Haskell identifies him as the engraver of emblematic pictures and discusses his prints in the account of Pisani’s entry; "
            "the dating claim and Moschini report remain attributed to Haskell. Haskell also says dall’Acqua was not involved in Pisani’s downfall; "
            "that negative statement is not converted into another relation."
        ),
    },
    {
        "candidate": "cand-0020",
        "group": "new-person:albani-annibale-f7a833163c",
        "ku": "units/persons/annibale-albani",
        "card": "04-knowledge/units/persons/annibale-albani.md",
        "name_zh": "安尼巴莱·阿尔巴尼",
        "name_en": "Annibale Albani",
        "index_entry": "A.csv#19",
        "index_name": "Albani, Cardinal Annibale",
        "index_page": "166n",
        "source_file": "02-sources/02-Markdown/06_CHP-6_sec_v.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/06_CHP-6_sec_v.md",
            "第6章第V节脚注2，印刷页166，行70",
            "line 70; print p. 166, note 2",
            "Cardinal d’Adda, seconded by Cardinals Gozzadini and Albani, was unsuccessful in getting the Bolognese painter Domenico Maria Viani to come to Rome",
            "Haskell脚注称d’Adda在Gozzadini和Albani支持下，未能邀画家Domenico Maria Viani赴罗马。",
        ),
        "name_rows": [
            ("索引姓名与称号", "Albani, Cardinal Annibale", "S1，A.csv#19"),
            ("脚注称名", "Albani", "S2，第6章第V节，p.166注2，L70"),
        ],
        "relation_ids": ["st-chp6-p166-n2-viani"],
        "description_zh": (
            "本卡登记书后索引主条“Albani, Cardinal Annibale”及第6章第166页脚注中的Albani；"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Albani, Cardinal Annibale” and Albani named in a Chapter 6 footnote on page 166; "
            "the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell称d’Adda在Gozzadini与Albani支持下，未能邀请Viani赴罗马；原文没有说Albani独立发起该行动。"
        ),
        "context_en": (
            "Haskell says d’Adda, supported by Gozzadini and Albani, failed to bring Viani to Rome; the passage does not say Albani initiated the effort independently."
        ),
    },
    {
        "candidate": "cand-0085",
        "group": "new-person:altham-james-93ba925b1e",
        "ku": "units/persons/james-altham",
        "card": "04-knowledge/units/persons/james-altham.md",
        "name_zh": "詹姆斯·阿尔瑟姆",
        "name_en": "James Altham",
        "index_entry": "A.csv#86",
        "index_name": "Altham, James",
        "index_page": "197",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
                "第7章第IV节，印刷页197，行65",
                "line 65; print p. 197",
                "James Altham, an artist",
                "Haskell将James Altham列入赴意大利的英国游客，并称他为artist；正文说这组游客各自拥有由重要画家绘制的肖像，但未逐人分配城市或图版。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
                "第7章第IV节脚注2，印刷页197，行109",
                "line 109; print p. 197, note 2",
                "James Altham as a hermit by Salvator Rosa in 1665 (Bankes Collection)",
                "Haskell脚注将Altham的隐士肖像归于Salvator Rosa并定于1665年，注明Bankes Collection；所引出版物未独立查阅。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Altham, James", "S1，A.csv#86"),
            ("正文及脚注姓名", "James Altham", "S2，第7章第IV节，p.197正文L65、注2 L109"),
        ],
        "relation_ids": [
            "st-chp7-p197-tourist-portrait-examples",
            "st-chp7-p197-n2-altham-portrait",
        ],
        "description_zh": (
            "本卡登记书后索引主条“Altham, James”及第7章第197页正文和脚注中的James Altham；"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Altham, James” and James Altham named in the body and footnote of Chapter 7 on page 197; "
            "the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "正文将Altham列为artist及游客肖像组成员，未把其对应到特定城市或图版；脚注将一幅隐士肖像归于Salvator Rosa并定于1665年。"
            "Bankes Collection为Haskell当时的记载，不据此推断现藏情况。"
        ),
        "context_en": (
            "The body calls Altham an artist and includes him among tourist portrait sitters without assigning a particular city or plate. "
            "The footnote attributes a hermit portrait to Salvator Rosa and dates it to 1665. Bankes Collection is Haskell’s report, "
            "not evidence of the portrait’s present location."
        ),
    },
    {
        "candidate": "cand-0109",
        "group": "new-person:anne-austria-france-of-of-regent-4d8cb859b3",
        "ku": "units/persons/anne-of-austria-regent-france",
        "card": "04-knowledge/units/persons/anne-of-austria-regent-france.md",
        "name_zh": "奥地利的安娜",
        "name_en": "Anne of Austria",
        "index_entry": "A.csv#110",
        "index_name": "Anne of Austria, Regent of France",
        "index_page": "182",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/07_CHP-7_sec_i.md",
            "第7章第I节，印刷页182，行152",
            "line 152; print p. 182",
            "Glorification of Mazarin was out of the question in view of his nominal dependence on the boy King Louis XIV and the Regent Anne of Austria",
            "Haskell将Mazarin对Louis XIV及摄政者Anne of Austria的nominal dependence作为其不宜被颂扬的语境。",
        ),
        "name_rows": [
            ("索引姓名与称号", "Anne of Austria, Regent of France", "S1，A.csv#110"),
            ("正文全名与称号", "the Regent Anne of Austria", "S2，第7章第I节，p.182，L152"),
        ],
        "relation_ids": ["st-chp7-p182-i03"],
        "description_zh": (
            "本卡登记书后索引主条“Anne of Austria, Regent of France”及第7章第182页正文称名；中文显示名沿用奥地利的安娜。"
        ),
        "description_en": (
            "This card records the index entry “Anne of Austria, Regent of France” and the name used in Chapter 7 on page 182; "
            "the Chinese display name follows the established form 奥地利的安娜."
        ),
        "context_zh": (
            "Haskell在Mazarin的绘画赞颂语境中称她为摄政者，并说Mazarin名义上依赖她与少年国王Louis XIV；不扩展为宪制判断。"
        ),
        "context_en": (
            "In the discussion of glorifying Mazarin, Haskell calls her a regent and says Mazarin nominally depended on her and the boy King Louis XIV; "
            "no broader constitutional conclusion is added."
        ),
    },
]

if __name__ == "__main__":
    raise SystemExit(registrar.main())
