from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_s_index_endpoints_schut_segala_serlio_skala_20261018 as registrar  # noqa: E402

registrar.ANCHOR = "s4-torelli-torresani-triva-tron-person-endpoints-20261018"
registrar.PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    "s4-torelli-torresani-triva-tron-person-endpoints-20261018"
)
registrar.BATCH_TITLE = "Torelli、Torresani、Triva与Tron四组人物端点"
registrar.BATCH_PROCESS_NOTE = (
    "四组均为S3 new单候选人物身份组，共登记4张KU卡、4条候选映射和8条source_backed姓名字段。"
    "Giuseppe Torelli依据附录书信题头和索引登记；书信内容报告其兄弟Felice选定画题及预期绘制难点，不证明作品完成，"
    "OCR的Febee按S2页图校读记录为Felice。Andrea Torresani依据第9章及索引登记；Haskell转引Moschini的句子中，"
    "印刷页图读作100 views，OCR转录为too views，Moschini原文及单幅作品未独立查阅。"
    "Antonio Triva仅按Haskell列举为慕尼黑受聘意大利画家之一登记，保留“best known”非穷尽和相对年代限定。"
    "Caterina Dolfin Tron保留Haskell的might/perhaps语气；可能讨论不记作已发生事件，威尼斯状态 quo 的判断仍归于作者。"
    "四条S2关系候选留待S6；不新增外部来源、正式关系或backlog项目。"
)
registrar.BATCH_RESULT_NOTE = (
    "；4条S2关系候选继续待S6；Torelli书信未证明作品完成，Torresani数量保留OCR与页图读数差异，"
    "Tron相关讨论保留可能语气；未新增正式关系或外部来源。"
)
registrar.TARGETS = [
    {
        "candidate": "cand-2648",
        "group": "new-person:giuseppe-torelli-a6692bccd5",
        "ku": "units/persons/giuseppe-torelli",
        "card": "04-knowledge/units/persons/giuseppe-torelli.md",
        "name_zh": "朱塞佩·托雷利",
        "name_en": "Giuseppe Torelli",
        "index_entry": "T.csv#111",
        "index_name": "Torelli, Giuseppe",
        "index_page": "389",
        "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/19_CHP-19Appendix.md",
            "附录3，印刷页389，行82–84",
            "lines 82-84; print p. 389",
            "Letter from Giuseppe Torelli to Alessandro .Marchesini of 24 February 1705:\n"
            ".   Ho letto la v.ra lettera a Felice mio fratello il quale ha di già trovata l’Istoria da far nel quadro consaputo, et è L’Istoria di Troja, cioè Pirro che ammazza Polissena nel Tempio, dove vi farà Calcante Mago et altre mezze figure, overo Teste che dinotteranno Enea et Antinoro et in Somma ciò che fata di sibogno in tal historia, e vi sarà il Sepolchro d’Achile Padre di\n"
            "Pirro, e sarà L’historia espressa nel tempio come dissi di sopra, il quadro sarà all’in sù | | cosi, e dice Febee che sarà un quadro di qualche fatica prima per le espressioni e poi per le Idee, e per le pieghe essendo Polissena persona di Stirpe Reggia perche figlia di Priamo Rè di Troja, e poi Pirro altra persona di alto grado perche figlio di Achile. ...'",
            "Haskell刊出一封题为Giuseppe Torelli致Alessandro Marchesini、日期为1705年2月24日的信；信中称其兄弟Felice已找到画题，并说明预期绘制难点。书内OCR作Febee，S2记录页图校读为Felice。",
        ),
        "name_rows": [
            ("索引姓名", "Torelli, Giuseppe", "S1，T.csv#111"),
            ("书信题头姓名", "Giuseppe Torelli", "S2，附录3，p.389，L82"),
        ],
        "relation_ids": ["st-chp19-p389-giuseppe-reports-felice-trojan-subject"],
        "description_zh": (
            "本卡登记书后索引主条“Torelli, Giuseppe”及附录3书信题头中的Giuseppe Torelli。"
            "Haskell将该信标为Giuseppe Torelli致Alessandro Marchesini，日期为1705年2月24日；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Torelli, Giuseppe” and Giuseppe Torelli named in a letter heading in Appendix 3. "
            "Haskell labels the letter as from Giuseppe Torelli to Alessandro Marchesini and dates it 24 February 1705. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "信中称Torelli的兄弟Felice已为一幅已知绘画找到特洛伊题材，并提及Pyrrhus杀害Polyxena及其他构图人物；"
            "信件报告题材选择和预期绘制难点，不证明绘画已经完成。原书OCR将Felice转录为“Febee”，S2据页图校读为Felice。"
            "该信的原始档案材料未独立查阅；关系候选留待S6。"
        ),
        "context_en": (
            "The letter says Torelli’s brother Felice had found a Trojan subject for a known painting and mentions Pyrrhus killing Polyxena "
            "and other figures in the composition. It reports a subject choice and anticipated difficulty, not completion of the painting. "
            "The book OCR transcribes Felice as “Febee”; S2 records a reading of Felice from the page image. "
            "The archival original was not independently consulted; the relation candidate remains for S6."
        ),
    },
    {
        "candidate": "cand-2649",
        "group": "new-person:andrea-torresani-a049f34c67",
        "ku": "units/persons/andrea-torresani",
        "card": "04-knowledge/units/persons/andrea-torresani.md",
        "name_zh": "安德烈亚·托雷萨尼",
        "name_en": "Andrea Torresani",
        "index_entry": "T.csv#112",
        "index_name": "Torresani, Andrea",
        "index_page": "266",
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/09_CHP-9_intro.md",
            "第9章引言，印刷页266，行305–306",
            "lines 305-306; print p. 266",
            "From Moschini we learn that Sagredo commissioned too views in pen and ink from the Brescian artist\nAndrea Torresani",
            "Haskell转引Moschini称Sagredo委托布雷西亚艺术家Andrea Torresani绘制views；印刷页图读作100，OCR作too，转引及单幅作品未独立查阅。",
        ),
        "name_rows": [
            ("索引姓名", "Torresani, Andrea", "S1，T.csv#112"),
            ("正文全名", "Andrea Torresani", "S2，第9章引言，p.266，L305–306"),
        ],
        "relation_ids": ["st-chp9-p266-torresani-views"],
        "description_zh": (
            "本卡登记书后索引主条“Torresani, Andrea”及第9章第266页具名的Andrea Torresani。"
            "Haskell称其为布雷西亚艺术家，并转引Moschini叙述Sagredo委托绘制views；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Torresani, Andrea” and Andrea Torresani named on page 266 of Chapter 9. "
            "Haskell identifies him as a Brescian artist and cites Moschini for an account of Sagredo commissioning views from him. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "该句经Haskell转引Moschini，称Sagredo委托Torresani以笔墨绘制100幅views；印刷页图读数为“100”，书本文本OCR为“too”。"
            "Moschini原文与单幅作品未独立查阅，数量及委托关系候选留待S6裁决。"
        ),
        "context_en": (
            "Through a citation to Moschini, Haskell says Sagredo commissioned 100 pen-and-ink views from Torresani; the printed page image "
            "is read as “100,” while the book text OCR says “too.” Moschini’s passage and the individual views were not independently consulted; "
            "the quantity and commission candidate remain for S6."
        ),
    },
    {
        "candidate": "cand-2654",
        "group": "new-person:antonio-triva-0ffbc63d0f",
        "ku": "units/persons/antonio-triva",
        "card": "04-knowledge/units/persons/antonio-triva.md",
        "name_zh": "安东尼奥·特里瓦",
        "name_en": "Antonio Triva",
        "index_entry": "T.csv#117",
        "index_name": "Triva, Antonio",
        "index_page": "193",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
            "第7章第IV节，印刷页193，行18–19",
            "lines 18-19; print p. 193",
            "A number of Italian painters, of whom the best known are Pietro Liberi,\nAntonio Triva and Pietro Bellotti, were also employed at Munich during the three decades that followed the end of the Thirty Years War.",
            "Haskell将Antonio Triva列入在三十年战争结束后约三十年间受聘于慕尼黑的意大利画家；“best known”名单并非穷尽，时间不换算为精确起止年。",
        ),
        "name_rows": [
            ("索引姓名", "Triva, Antonio", "S1，T.csv#117"),
            ("正文全名", "Antonio Triva", "S2，第7章第IV节，p.193，L18–19"),
        ],
        "relation_ids": ["st-chp7-p193-munich-italian-painters"],
        "description_zh": (
            "本卡登记书后索引主条“Triva, Antonio”及第7章第IV节第193页具名的Antonio Triva。"
            "Haskell将他列为一组受聘于慕尼黑的意大利画家之一；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Triva, Antonio” and Antonio Triva named on page 193 of Chapter 7, section IV. "
            "Haskell includes him among a number of Italian painters employed at Munich; the Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell说一组意大利画家在三十年战争结束后的三十年间受聘于慕尼黑，并列出Pietro Liberi、Antonio Triva、Pietro Bellotti为其中最知名者；"
            "该名单不表示穷尽，原文相对年代不转写成精确任职日期。关系候选留待S6。"
        ),
        "context_en": (
            "Haskell says a number of Italian painters were employed at Munich during the three decades following the Thirty Years War and names "
            "Pietro Liberi, Antonio Triva, and Pietro Bellotti as the best known among them. The list is not exhaustive, and the relative period "
            "is not converted into exact dates. The relation candidate remains for S6."
        ),
    },
    {
        "candidate": "cand-2655",
        "group": "new-person:caterina-dolfin-tron-dd7c35da12",
        "ku": "units/persons/caterina-dolfin-tron",
        "card": "04-knowledge/units/persons/caterina-dolfin-tron.md",
        "name_zh": "卡泰丽娜·多尔芬·特龙",
        "name_en": "Caterina Dolfin Tron",
        "index_entry": "T.csv#118",
        "index_name": "Tron, Caterina Dolfin",
        "index_page": "318",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
            "第10章第II节，印刷页318，行138–139",
            "lines 138-139; print p. 318",
            "In these changes Venice had played little direct part. Though the ideas might filter through the censorship without too much difficulty and be discussed perhaps in Consul\nSmith’s library or by Caterina Dolfin Tron and her intellectual friends, Venetian interest in maintaining the status quo was too powerful for the Republic to become the originator of any of the doctrines of the ‘Enlightenment’—it was indeed a Venetian who proved to be the most vigorous opponent of Beccaria—nearly all of which presupposed the abolition of rule by aristocracy.",
            "Haskell以might和perhaps提出启蒙思想可能传播或被讨论，并将Caterina Dolfin Tron列为可能的讨论者之一；威尼斯共和国未成为相关学说发源地是作者的历史判断。",
        ),
        "name_rows": [
            ("索引姓名", "Tron, Caterina Dolfin", "S1，T.csv#118"),
            ("正文全名", "Caterina Dolfin Tron", "S2，第10章第II节，p.318，L139"),
        ],
        "relation_ids": ["st-chp10-p318-venetian-status-quo-limited-doctrine-origin"],
        "description_zh": (
            "本卡登记书后索引主条“Tron, Caterina Dolfin”及第10章第II节第318页具名的Caterina Dolfin Tron。"
            "Haskell只说相关思想或许会在她及其知识界朋友中讨论；这不是已发生讨论的记载。中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Tron, Caterina Dolfin” and Caterina Dolfin Tron named on page 318 of Chapter 10, section II. "
            "Haskell says only that the ideas might perhaps have been discussed among her and her intellectual friends; this is not a report "
            "of a confirmed discussion. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell称启蒙思想可能较容易通过审查，并可能在Consul Smith的图书馆或Caterina Dolfin Tron及其知识界朋友中讨论；"
            "作者随后把威尼斯维护现状的利益视为共和国未成为启蒙学说发源地的原因。might／perhaps限定均保留；"
            "不据此断言Tron实际参加讨论，威尼斯政治文化判断仍归于Haskell。关系候选留待S6。"
        ),
        "context_en": (
            "Haskell says Enlightenment ideas might pass censorship relatively easily and might perhaps be discussed in Consul Smith’s library "
            "or by Caterina Dolfin Tron and her intellectual friends. He then attributes the Republic’s not originating Enlightenment doctrines "
            "to Venetian interests in maintaining the status quo. The qualifications “might” and “perhaps” are retained; no actual discussion "
            "by Tron is asserted, and the broader judgment remains attributed to Haskell. The relation candidate remains for S6."
        ),
    },
]

if __name__ == "__main__":
    raise SystemExit(registrar.main())
