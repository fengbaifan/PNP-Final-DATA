from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_REF = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp7-p183-note3-endpoints-20261024"
TASK = "S3-S4-S5-S6-chp7-p183-note3-20261024"
SOURCE_ID = "haskell-1980-rev-ed"
SOURCE_7 = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
SOURCE_21 = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
PDF_7 = "02-sources/01-book/CHP-7.pdf"
PDF_21 = "02-sources/01-book/CHP-21Bibliography.pdf"

EXPECTED_HASHES = {
    "04-knowledge/tables/entity-candidates.csv": "ff614f5f140ca77f4f8563b1deb61f5353f70f5f3d559949db28321ad341e606",
    "04-knowledge/tables/alignment.csv": "324fa57df7e3a7b6fb577e16e5b9662c092be283e5607dcfdeb8975d04823b79",
    "04-knowledge/tables/mentions.csv": "ca67fef8354dd1c4408524dfcd211171d70a3f0d832918cb837d922200456501",
    "04-knowledge/tables/book-statements.jsonl": "4822c273cbe53b22de26d75f8f28fa7ed6583e50beb3c5292e3ba7603d39e453",
    "04-knowledge/tables/ku-manifest.csv": "81bdef6205fa34c8716154074d15c171df316ed3f197f806364ff19a4b1359c5",
    "04-knowledge/tables/enrichment.jsonl": "e4a2381ecd1faa5dcf7ff9c5a2fcb3e956f96383db0e02d9e8041f9f9840850f",
    "04-knowledge/tables/relations.csv": "bb32f9f6b81f6f642aba668e0f12b5d75bb4d5867c756ca25bf885ba0b4ffb1e",
    "04-knowledge/tables/candidate-backlog.csv": "1ab0385757864db5aa47b3eea74e1090184bc049463ac9e93c584effd76aa485",
    "04-knowledge/accepted.yml": "b607bd00f46014966bd4c43cac28ceabe30a09ed4bb2d0f4fee85c548a8f7c35",
    SOURCE_7: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
    SOURCE_21: "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3",
    PDF_7: "eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212",
    PDF_21: "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512",
    "04-knowledge/units/archives/patrons-and-painters.md": "863e5925ece3f1101fee9df38fff4ad8c7a6505b7b9cf784178b5b17c636cd3f",
    "04-knowledge/units/persons/paolo-maccarani.md": "70237cf1779215096f986f852062ff15a26989fc2f434dc42c836dfb99f30224",
    "04-knowledge/units/persons/mazarin.md": "ee40c406f1651b06a261993853afB6e2ab2e156660ae1acd557a3d06204d2dd8".lower(),
}

FIELDS = {
    "units/persons/elpidio-benedetti": {
        "type": "person", "canonical_name": "埃尔皮迪奥·贝内代蒂（Elpidio Benedetti）", "name_en": "Elpidio Benedetti",
        "card_path": "04-knowledge/units/persons/elpidio-benedetti.md", "sub_type": "",
        "description_zh": "本卡记录哈斯克尔书目所列的 Elpidio Benedetti。第7章 p.183 注3 引其1661年葬礼出版物第5页；第21章书目列其为该书责任者。出版物及所引页未独立查阅，本卡不补写生平或外部身份。",
        "description_en": "This card records Elpidio Benedetti as named in Haskell’s bibliography. Chapter 7, p.183 n.3 cites p.5 of his 1661 funeral publication, and Chapter 21 lists him as its responsible author. Neither the publication nor the cited page was independently consulted; no biography or external identity is added.",
        "sources": [
            ("第7章，印刷页183，注3；Markdown L350；PDF physical page 17。", "注3列出 Elpidio Benedetti 及其1661年出版物第5页。", "3 In 1646—see avviso published in Roma, 1938, p. 477. See also Elpidio Benedetti, p. 5, Mazarin: Epistolario inedito, p. 119 (letter of 3 June 1650 to Maccarani: ‘mi piace riesca di Sua sodisfazione, perchè non può essere, se non bella . . .’), and Mazarin: Lettres pendant son ministère, IX, p. 693 (letter of 6 March 1661 to Maccarani).", SOURCE_7, "line 350; printed p.183 n.3; PDF physical page 17"),
            ("第21章书目，印刷页414；Markdown L144；PDF physical page 4。", "书目将 Benedetti 列在葬礼出版物责任者位置，出版地为 Roma，年份为1661。", "Benedetti, Elpidio: Pompa funebre Nell’Esequie celebrate in Roma al Cardinal Mazarini nella Chiesa di S.S. Vincenzo Anastasio, In Roma 1661.", SOURCE_21, "line 144; printed p.414; PDF physical page 4"),
        ],
        "enrichment": [],
    },
    "units/archives/benedetti-pompa-funebre-mazarin-1661": {
        "type": "archive", "canonical_name": "《马扎林葬礼出版物》（Pompa funebre nell’esequie celebrate in Roma al Cardinal Mazarini nella Chiesa di S.S. Vincenzo Anastasio）", "name_en": "Pompa funebre nell’esequie celebrate in Roma al Cardinal Mazarini nella Chiesa di S.S. Vincenzo Anastasio",
        "card_path": "04-knowledge/units/archives/benedetti-pompa-funebre-mazarin-1661.md", "sub_type": "book; Haskell bibliography record",
        "description_zh": "本卡登记哈斯克尔第21章书目所列的1661年罗马出版物；书目将 Elpidio Benedetti 列为责任者。第7章 p.183 注3 引用第5页。原书及所引页未独立查阅，卡片只记录哈斯克尔的书目信息与引注。",
        "description_en": "This card records the 1661 Rome publication listed in Haskell’s Chapter 21 bibliography, which names Elpidio Benedetti as responsible author. Chapter 7, p.183 n.3 cites p.5. The publication and cited page were not independently consulted; the card records Haskell’s bibliographic entry and citation only.",
        "sources": [
            ("第21章书目，印刷页414；Markdown L144；PDF physical page 4。", "书目列出原题名、责任者形式、Roma与1661年。", "Benedetti, Elpidio: Pompa funebre Nell’Esequie celebrate in Roma al Cardinal Mazarini nella Chiesa di S.S. Vincenzo Anastasio, In Roma 1661.", SOURCE_21, "line 144; printed p.414; PDF physical page 4"),
            ("第7章，印刷页183，注3；Markdown L350；PDF physical page 17。", "注3将 p.5 列为引注位置；未独立查阅该页。", "3 In 1646—see avviso published in Roma, 1938, p. 477. See also Elpidio Benedetti, p. 5, Mazarin: Epistolario inedito, p. 119 (letter of 3 June 1650 to Maccarani: ‘mi piace riesca di Sua sodisfazione, perchè non può essere, se non bella . . .’), and Mazarin: Lettres pendant son ministère, IX, p. 693 (letter of 6 March 1661 to Maccarani).", SOURCE_7, "line 350; printed p.183 n.3; PDF physical page 17"),
        ],
        "enrichment": [
            ("原题名", "Pompa funebre nell’esequie celebrate in Roma al Cardinal Mazarini nella Chiesa di S.S. Vincenzo Anastasio", "S1", "第21章书目题名；此处保留来源拼写。", "bibliography"),
            ("文献类型", "葬礼出版物（书目记录）", "S1", "Haskell 将其列为1661年罗马出版物；原书未查阅。", "bibliography"),
            ("责任者（书目作者）", "埃尔皮迪奥·贝内代蒂／Elpidio Benedetti", "S1", "书目列名 Benedetti, Elpidio；仅记录 Haskell 的责任者归属。", "bibliography"),
            ("出版地及出版年", "Roma, 1661", "S1", "书目原文列 In Roma 1661。", "bibliography"),
            ("哈斯克尔所引位置", "第7章 p.183 注3，引该书 p.5；所引页未独立查阅。", "S2", "第7章注3给出 p.5 定位，不表示该页已阅读。", "footnote"),
        ],
    },
    "units/archives/mazarin-epistolario-inedito-morbio-1842": {
        "type": "archive", "canonical_name": "《马扎林未刊书信集》（Epistolario inedito）", "name_en": "Epistolario inedito",
        "card_path": "04-knowledge/units/archives/mazarin-epistolario-inedito-morbio-1842.md", "sub_type": "edited correspondence; Haskell bibliography record",
        "description_zh": "本卡登记哈斯克尔第21章书目所列的《Epistolario inedito》：书目列 Mazarin, G. 为责任者，并称由 Carlo Morbio 编刊，Milano 1842。第7章 p.183 注3 引第119页，称该处为1650年6月3日致 Maccarani 的信。该书与第119页未独立查阅。",
        "description_en": "This card records *Epistolario inedito* as listed in Haskell’s Chapter 21 bibliography: the entry names Mazarin, G. as responsible author and says it was published by Carlo Morbio, Milano 1842. Chapter 7, p.183 n.3 cites p.119 for a letter to Maccarani dated 3 June 1650. Neither the edition nor p.119 was independently consulted.",
        "sources": [
            ("第21章书目，印刷页429；Markdown L783；PDF physical page 19。", "页图核实书目列 Mazarin, G.、Carlo Morbio、Milano 1842。", "Mazarin, G.: Epistolario inedito pubblicato da Carlo Morbio, Milano 1842.", SOURCE_21, "line 783; printed p.429; PDF physical page 19"),
            ("第7章，印刷页183，注3；Markdown L350；PDF physical page 17。", "注3引第119页，并称其为1650年6月3日致 Maccarani 的信；该页未独立查阅。", "3 In 1646—see avviso published in Roma, 1938, p. 477. See also Elpidio Benedetti, p. 5, Mazarin: Epistolario inedito, p. 119 (letter of 3 June 1650 to Maccarani: ‘mi piace riesca di Sua sodisfazione, perchè non può essere, se non bella . . .’), and Mazarin: Lettres pendant son ministère, IX, p. 693 (letter of 6 March 1661 to Maccarani).", SOURCE_7, "line 350; printed p.183 n.3; PDF physical page 17"),
        ],
        "enrichment": [
            ("原题名", "Epistolario inedito", "S1", "第21章书目原题名。", "bibliography"),
            ("文献类型", "书信集（书目记录）", "S1", "Haskell 将其列为 Mazarin 的书信集；原书未查阅。", "bibliography"),
            ("责任者（书目作者）", "Mazarin, G.（哈斯克尔书目责任形式）", "S1", "书目条目以 Mazarin, G. 起首；该字段只记录书目归属。", "bibliography"),
            ("编刊／出版责任", "Carlo Morbio（书目原文：pubblicato da）", "S1", "书目明记 pubblicato da Carlo Morbio；关系只记录来源所列责任。", "bibliography"),
            ("出版信息", "Milano, 1842", "S1", "第21章书目原文。", "bibliography"),
            ("哈斯克尔所引位置", "第7章 p.183 注3，引 p.119；称该处为1650年6月3日致 Maccarani 的信；所引页未独立查阅。", "S2", "仅记录 Haskell 的引注定位与说明，不声称已查阅该版或书信。", "footnote"),
        ],
    },
    "units/persons/carlo-morbio": {
        "type": "person", "canonical_name": "卡洛·莫尔比奥（Carlo Morbio）", "name_en": "Carlo Morbio",
        "card_path": "04-knowledge/units/persons/carlo-morbio.md", "sub_type": "",
        "description_zh": "本卡仅记录哈斯克尔第21章书目将 Carlo Morbio 列为《Epistolario inedito》的 pubblicato da。该责任说明来自书目页；不补写生平或外部身份。",
        "description_en": "This card records only that Haskell’s Chapter 21 bibliography names Carlo Morbio as the *pubblicato da* for *Epistolario inedito*. This responsibility statement comes from the bibliography; no biography or external identity is added.",
        "sources": [("第21章书目，印刷页429；Markdown L783；PDF physical page 19。", "页图核实书目明记 pubblicato da Carlo Morbio。", "Mazarin, G.: Epistolario inedito pubblicato da Carlo Morbio, Milano 1842.", SOURCE_21, "line 783; printed p.429; PDF physical page 19")],
        "enrichment": [],
    },
    "units/archives/mazarin-lettres-pendant-son-ministere-cheruel-1872": {
        "type": "archive", "canonical_name": "《马扎林任职期间书信集》（Lettres pendant son ministère）", "name_en": "Lettres pendant son ministère",
        "card_path": "04-knowledge/units/archives/mazarin-lettres-pendant-son-ministere-cheruel-1872.md", "sub_type": "nine-volume edited correspondence; Haskell bibliography record",
        "description_zh": "本卡登记哈斯克尔第21章书目所列的《Lettres pendant son ministère》：书目列 Mazarin, G.，称由 M. A. Chéruel 汇编并刊行，共9卷，Paris 1872–1906。第7章 p.183 注3 引第IX卷第693页，称其为1661年3月6日致 Maccarani 的信。该书与所引页未独立查阅。",
        "description_en": "This card records *Lettres pendant son ministère* as listed in Haskell’s Chapter 21 bibliography: the entry names Mazarin, G., says M. A. Chéruel collected and published it, and lists nine volumes, Paris 1872–1906. Chapter 7, p.183 n.3 cites vol. IX, p.693 for a letter to Maccarani dated 6 March 1661. Neither the edition nor the cited page was independently consulted.",
        "sources": [
            ("第21章书目，印刷页429；Markdown L784–785；PDF physical page 19。", "页图核实书目列 Mazarin, G.，M. A. Chéruel，9卷，Paris 1872–1906。", "Mazarin, G.: Lettres pendant son ministère recueillies et publiées par M. A. Chéruel, 9 vols., Paris 1872–1906.", SOURCE_21, "lines 784–785; printed p.429; PDF physical page 19"),
            ("第7章，印刷页183，注3；Markdown L350；PDF physical page 17。", "注3引第IX卷第693页，并称该处为1661年3月6日致 Maccarani 的信；该页未独立查阅。", "3 In 1646—see avviso published in Roma, 1938, p. 477. See also Elpidio Benedetti, p. 5, Mazarin: Epistolario inedito, p. 119 (letter of 3 June 1650 to Maccarani: ‘mi piace riesca di Sua sodisfazione, perchè non può essere, se non bella . . .’), and Mazarin: Lettres pendant son ministère, IX, p. 693 (letter of 6 March 1661 to Maccarani).", SOURCE_7, "line 350; printed p.183 n.3; PDF physical page 17"),
        ],
        "enrichment": [
            ("原题名", "Lettres pendant son ministère", "S1", "第21章书目原题名。", "bibliography"),
            ("文献类型", "九卷本书信集（书目记录）", "S1", "Haskell 书目列九卷；原书未查阅。", "bibliography"),
            ("责任者（书目作者）", "Mazarin, G.（哈斯克尔书目责任形式）", "S1", "书目条目以 Mazarin, G. 起首；该字段只记录书目归属。", "bibliography"),
            ("编者／汇编者", "M. A. Chéruel（书目原文：recueillies par）", "S1", "书目称其 recueillies；保留来源列名和责任范围。", "bibliography"),
            ("刊行责任", "M. A. Chéruel（书目原文：publiées par）", "S1", "书目称其 publiées；保留来源列名和责任范围。", "bibliography"),
            ("卷数", "9 vols.", "S1", "第21章书目列出九卷。", "bibliography"),
            ("出版信息", "Paris, 1872–1906", "S1", "第21章书目原文。", "bibliography"),
            ("哈斯克尔所引位置", "第7章 p.183 注3，引第IX卷 p.693；称该处为1661年3月6日致 Maccarani 的信；所引页未独立查阅。", "S2", "仅记录 Haskell 的引注定位与说明，不声称已查阅该版或书信。", "footnote"),
        ],
    },
    "units/persons/m-a-cheruel": {
        "type": "person", "canonical_name": "M. A. 谢吕尔（M. A. Chéruel）", "name_en": "M. A. Chéruel",
        "card_path": "04-knowledge/units/persons/m-a-cheruel.md", "sub_type": "",
        "description_zh": "本卡仅记录哈斯克尔第21章书目将 M. A. Chéruel 列为《Lettres pendant son ministère》的汇编者与刊行责任者。书目仅列首字母，卡片保留来源形式，不扩写姓名或生平。",
        "description_en": "This card records only that Haskell’s Chapter 21 bibliography names M. A. Chéruel as collector and publishing agent for *Lettres pendant son ministère*. The bibliography gives initials only; this card preserves that form without expanding the name or adding a biography.",
        "sources": [("第21章书目，印刷页429；Markdown L784–785；PDF physical page 19。", "页图核实书目原文为 recueillies et publiées par M. A. Chéruel。", "Mazarin, G.: Lettres pendant son ministère recueillies et publiées par M. A. Chéruel, 9 vols., Paris 1872–1906.", SOURCE_21, "lines 784–785; printed p.429; PDF physical page 19")],
        "enrichment": [],
    },
    "units/archives/mazarin-letter-to-maccarani-1661-03-06": {
        "type": "archive", "canonical_name": "马扎林致保罗·马卡拉尼的书信（1661年3月6日）（Mazarin letter to Paolo Maccarani, 6 March 1661）", "name_en": "Mazarin letter to Paolo Maccarani, 6 March 1661",
        "card_path": "04-knowledge/units/archives/mazarin-letter-to-maccarani-1661-03-06.md", "sub_type": "letter; known through Haskell’s citation",
        "description_zh": "本卡对应既有候选 cand-6798。哈斯克尔第7章 p.183 正文引述 Mazarin 写给 Maccarani 的信，注3将其定位为1661年3月6日、收于《Lettres pendant son ministère》第IX卷第693页。书信及该页未独立查阅；正式关系仅记录书内所述作者、收信人和引注定位。",
        "description_en": "This card registers the existing candidate cand-6798. Haskell’s Chapter 7, p.183 quotes a letter Mazarin wrote to Maccarani; note 3 identifies it as dated 6 March 1661 and locates it at p.693 of vol. IX of *Lettres pendant son ministère*. Neither the letter nor that page was independently consulted; relations record only Haskell’s account and locator.",
        "sources": [
            ("第7章，印刷页183，正文 L164；PDF physical page 17。", "正文称 Mazarin 在1661年写信给 Maccarani；原信未独立查阅。", "‘We are always talking about building,’ he wrote to Maccarani shortly before his death in 1661, ‘and yet it might be better to think of building for ourselves a certain and everlasting room in Paradise.’", SOURCE_7, "line 164; printed p.183; PDF physical page 17"),
            ("第7章，印刷页183，注3，L350；PDF physical page 17。", "注3将上述书信定位为1661年3月6日、vol. IX, p.693；页码所指书信未独立查阅。", "3 In 1646—see avviso published in Roma, 1938, p.477. See also Elpidio Benedetti, p.5, Mazarin: Epistolario inedito, p.119 (letter of 3 June 1650 to Maccarani), and Mazarin: Lettres pendant son ministère, IX, p.693 (letter of 6 March 1661 to Maccarani).", SOURCE_7, "line 350; printed p.183 n.3; PDF physical page 17"),
        ],
        "enrichment": [
            ("文献类型", "书信（哈斯克尔引注所指）", "S2", "哈斯克尔正文和注3共同指向一封特定书信；原信未独立查阅。", "footnote"),
            ("日期", "1661-03-06", "S2", "日期依据哈斯克尔注3对所引书信的识别；原信未独立查阅。", "footnote"),
            ("收信人", "保罗·马卡拉尼／Paolo Maccarani", "S2", "正文称 Mazarin 写信给 Maccarani；注3对应同一书信。", "footnote"),
            ("刊录与转引", "Lettres pendant son ministère, vol. IX, p.693；所引页未独立查阅。", "S2", "仅记录哈斯克尔注3的刊本定位，不声称已查阅该卷或该页。", "footnote"),
        ],
    },
    "units/archives/mazarin-letter-to-maccarani-1650-06-03": {
        "type": "archive", "canonical_name": "1650年6月3日致保罗·马卡拉尼的书信（Letter to Paolo Maccarani, 3 June 1650）", "name_en": "Letter to Paolo Maccarani, 3 June 1650",
        "card_path": "04-knowledge/units/archives/mazarin-letter-to-maccarani-1650-06-03.md", "sub_type": "letter; known through Haskell’s citation",
        "description_zh": "本卡登记哈斯克尔第7章 p.183 注3所指的1650年6月3日致 Paolo Maccarani 的书信；注3将第119页定位到《Epistolario inedito》。书信及所引页未独立查阅；发信人和引文所赞扬事物的具体所指不在本卡扩定。",
        "description_en": "This card records the letter dated 3 June 1650 to Paolo Maccarani identified in Haskell’s Chapter 7, p.183 n.3; the note locates it at p.119 of *Epistolario inedito*. The letter and cited page were not independently consulted. The card does not expand the sender or the precise referent of the quoted praise.",
        "sources": [("第7章，印刷页183，注3；Markdown L350；PDF physical page 17。", "注3称1650年6月3日致 Maccarani 的信见《Epistolario inedito》第119页；原信及该页未查阅。", "3 In 1646—see avviso published in Roma, 1938, p. 477. See also Elpidio Benedetti, p. 5, Mazarin: Epistolario inedito, p. 119 (letter of 3 June 1650 to Maccarani: ‘mi piace riesca di Sua sodisfazione, perchè non può essere, se non bella . . .’), and Mazarin: Lettres pendant son ministère, IX, p. 693 (letter of 6 March 1661 to Maccarani).", SOURCE_7, "line 350; printed p.183 n.3; PDF physical page 17")],
        "enrichment": [
            ("文献类型", "书信（哈斯克尔引注所指）", "S2", "哈斯克尔注3指明一封1650年6月3日致 Maccarani 的书信。", "footnote"),
            ("日期", "1650-06-03", "S2", "日期来自哈斯克尔注3；原信未独立查阅。", "footnote"),
            ("收信人", "保罗·马卡拉尼／Paolo Maccarani", "S2", "哈斯克尔注3明称 letter ... to Maccarani。", "footnote"),
            ("刊录与转引", "哈斯克尔注3引《Epistolario inedito》p.119；所引页及信件未独立查阅。", "S2", "仅记录 Haskell 的转引路径和页码。", "footnote"),
        ],
    },
}

NEW_PERSON_CANDIDATES = [
    {
        "candidate_id": "cand-12439", "canonical_name": "Carlo Morbio", "type": "person",
        "source_ref": "chp-21:21_CHP-21Bibliography:l756-806#L783", "mention_id": "m-chp21-bib-l756-806-morbio-20261024",
        "mention_surface": "Carlo Morbio", "mention_start": 1556, "mention_end": 1568,
        "group": "new-person:carlo-morbio-haskell-bibliography-20261024", "ku": "units/persons/carlo-morbio",
        "statement_id": "st-chp21-bib-l756-806-entry-16-published-by-morbio",
        "detail": "Haskell’s Chapter 21 bibliography names Carlo Morbio as pubblicato da for Epistolario inedito, Milano 1842. The bibliographic responsibility is source-local; no external identity is asserted.",
        "role": "Epistolario inedito 的书目刊行责任者",
    },
    {
        "candidate_id": "cand-12440", "canonical_name": "M. A. Chéruel", "type": "person",
        "source_ref": "chp-21:21_CHP-21Bibliography:l756-806#L784", "mention_id": "m-chp21-bib-l756-806-cheruel-20261024",
        "mention_surface": "M. A. Chéruel", "mention_start": 1654, "mention_end": 1667,
        "group": "new-person:m-a-cheruel-haskell-bibliography-20261024", "ku": "units/persons/m-a-cheruel",
        "statement_id": "st-chp21-bib-l756-806-entry-17-compiled-by-cheruel",
        "detail": "Haskell’s Chapter 21 bibliography names M. A. Chéruel as collecting and publishing Lettres pendant son ministère. Preserve initials as printed; no full name or external identity is asserted.",
        "role": "Lettres pendant son ministère 的汇编及刊行责任者",
    },
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def encode_csv(rows: list[dict[str, str]], fields: list[str]) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("utf-8")


def encode_jsonl(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def q(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def table_id(ku_id: str, section: str, index: int, header: list[str]) -> str:
    value = f"{ku_id}|{section}|{index}|{'|'.join(header)}"
    return "tbl-" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def stable_id(prefix: str, value: str) -> str:
    return prefix + "-" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def source_record(location: str, summary: str, quote: str, file: str, span: str) -> dict:
    return {
        "citation": "Francis Haskell, Patrons and Painters, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006).",
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span, "text": quote}],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": file, "source_span": span},
    }


def build_card(ku_id: str, spec: dict) -> bytes:
    title = spec["canonical_name"]
    name_en = spec["name_en"]
    lines = [
        "---", f"title: {q(title)}", f"name_en: {q(name_en)}", f"type: {spec['type']}",
    ]
    if spec.get("sub_type"):
        lines.append(f"sub_type: {q(spec['sub_type'])}")
    lines.extend(["evidence_status: source_backed", "created: '2026-10-24'", "updated: '2026-10-24'", f"process_ref: {q(PROCESS_REF)}", "sources:"])
    for source in spec["sources"]:
        # Batch specifications keep these five source fields compactly as tuples;
        # normalize them through the shared source-record constructor before YAML output.
        record = source_record(*source) if isinstance(source, tuple) else source
        lines.extend([
            f"- citation: {q(record['citation'])}", f"  location: {q(record['location'])}",
            f"  sentence_summary: {q(record['sentence_summary'])}", "  original_quotes:",
        ])
        for quote in record["original_quotes"]:
            lines.extend([f"  - source_span: {q(quote['source_span'])}", f"    text: {q(quote['text'])}"])
        lines.extend([
            "  evidence_ref:", f"    doc_id: {q(record['evidence_ref']['doc_id'])}",
            f"    source_file: {q(record['evidence_ref']['source_file'])}",
            f"    source_span: {q(record['evidence_ref']['source_span'])}",
        ])
    lines.extend(["---", "", "## 内容", "", "### 描述", "", f"**中文：** {spec['description_zh']}", "", f"**English:** {spec['description_en']}"])
    if spec["type"] == "archive":
        lines.extend(["", "### 文献书目信息", "", "| 字段 | 内容 | 依据 |", "| --- | --- | --- |"])
        for field, value, _source_ref, evidence, _origin in spec["enrichment"]:
            lines.append(f"| {field} | {value} | {evidence} |")
    else:
        lines.extend(["", "### 身份边界", "", "身份仅限哈斯克尔书目中可追溯的责任者形式；未做外部身份核验。"])
    lines.extend(["", "## 关系与证据", ""])
    return ("\n".join(lines) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply the reviewed, guarded data update")
    args = parser.parse_args()

    before: dict[Path, bytes] = {}
    for rel, expected in EXPECTED_HASHES.items():
        path = ROOT / rel
        if not path.exists():
            raise SystemExit(f"required input is missing: {rel}")
        raw = path.read_bytes()
        if sha256(raw).lower() != expected.lower():
            raise SystemExit(f"input changed since review: {rel} ({sha256(raw)})")
        before[path] = raw

    source7_lines = (ROOT / SOURCE_7).read_text(encoding="utf-8-sig").splitlines()
    source21_lines = (ROOT / SOURCE_21).read_text(encoding="utf-8-sig").splitlines()
    guards = {
        350: "3 In 1646",
    }
    for line_no, text in guards.items():
        if text not in source7_lines[line_no - 1]:
            raise SystemExit(f"p.183 source guard failed at L{line_no}")
    if "everlasting room in Paradise" not in source7_lines[163]:
        raise SystemExit("p.183 body quotation source guard failed at L164")
    for line_no, prefix in {
        144: "Benedetti, Elpidio:",
        784: "Mazarin, G.: Lettres pendant son minist",
    }.items():
        if not source21_lines[line_no - 1].startswith(prefix):
            raise SystemExit(f"bibliography source guard failed at L{line_no}: {source21_lines[line_no - 1]!r}")
    for line_no, text in {
        783: "Mazarin, G.: Epistolario inedito pubblicato da Carlo Morbio, Milano 1842.",
        785: "Paris 1872-1906. .",
    }.items():
        if source21_lines[line_no - 1] != text:
            raise SystemExit(f"bibliography source guard failed at L{line_no}: {source21_lines[line_no - 1]!r}")

    relation_types = (ROOT / ".agents/skills/ingest/references/relation-types.yml").read_text(encoding="utf-8")
    matrix = (ROOT / "01-domain/relation-domain-range.yml").read_text(encoding="utf-8")
    predicates = ["cites", "addressed_to", "authored_by", "published_by", "compiled_by", "part_of"]
    for predicate in predicates:
        if not re.search(rf"^  - {re.escape(predicate)}$", relation_types, re.MULTILINE):
            raise SystemExit(f"predicate absent from controlled vocabulary: {predicate}")
        if not re.search(rf"^  {re.escape(predicate)}:\s", matrix, re.MULTILINE):
            raise SystemExit(f"predicate absent from relation domain/range matrix: {predicate}")

    table_paths = {name: ROOT / name for name in EXPECTED_HASHES if name.startswith("04-knowledge/tables/")}
    candidates, candidate_fields = read_csv(table_paths["04-knowledge/tables/entity-candidates.csv"])
    alignment, alignment_fields = read_csv(table_paths["04-knowledge/tables/alignment.csv"])
    mentions, mention_fields = read_csv(table_paths["04-knowledge/tables/mentions.csv"])
    manifest, manifest_fields = read_csv(table_paths["04-knowledge/tables/ku-manifest.csv"])
    enrichments = [json.loads(line) for line in before[table_paths["04-knowledge/tables/enrichment.jsonl"]].decode("utf-8-sig").splitlines() if line.strip()]
    relations, relation_fields = read_csv(table_paths["04-knowledge/tables/relations.csv"])
    backlog, backlog_fields = read_csv(table_paths["04-knowledge/tables/candidate-backlog.csv"])
    statements = [json.loads(line) for line in before[table_paths["04-knowledge/tables/book-statements.jsonl"]].decode("utf-8-sig").splitlines() if line.strip()]

    by_candidate = {row["candidate_id"]: row for row in candidates}
    by_alignment = {row["candidate_id"]: row for row in alignment if row.get("candidate_id")}
    expected_states = {
        "cand-7080": ("new", "person"), "cand-7081": ("new", "archive"),
        "cand-7082": ("new", "archive"), "cand-7083": ("new", "archive"),
        "cand-7084": ("new", "archive"), "cand-6798": ("new", "archive"), "cand-7079": ("undecided", "archive"),
        "cand-7085": ("undecided", ""),
    }
    for candidate_id, (decision, entity_type) in expected_states.items():
        if candidate_id not in by_candidate or by_candidate[candidate_id].get("suggested_type", "") != entity_type:
            raise SystemExit(f"candidate/type precondition failed: {candidate_id}")
        row = by_alignment.get(candidate_id)
        if row is None or row.get("decision") != decision:
            raise SystemExit(f"S3 decision precondition failed: {candidate_id}")
    for spec in NEW_PERSON_CANDIDATES:
        if spec["candidate_id"] in by_candidate or spec["candidate_id"] in by_alignment:
            raise SystemExit(f"new endpoint candidate ID already exists: {spec['candidate_id']}")
    statement_by_id = {row["statement_id"]: row for row in statements}
    required_existing_statements = [
        "st-chp7-p183-i11",
        "st-chp7-p183-n3-cite-avviso", "st-chp7-p183-n3-cite-benedetti",
        "st-chp7-p183-n3-cite-epistolario", "st-chp7-p183-n3-cite-lettres",
        "st-chp7-p183-n3-cite-spon-wheler", "st-chp7-p183-n3-facade-inscription",
        "st-chp7-p183-n3-maccarani-gallery-1675", "st-chp7-p183-n3-letter-1650-to-maccarani",
        "st-chp21-bib-l129-163-entry-13", "st-chp21-bib-l756-806-entry-16", "st-chp21-bib-l756-806-entry-17",
    ]
    if not set(required_existing_statements).issubset(statement_by_id):
        raise SystemExit("one or more expected S2 source statements are missing")
    if len(statement_by_id) != len(statements):
        raise SystemExit("statement IDs are not unique")

    p183_segment = "\n".join(source7_lines[292:389])
    p21_a_segment = "\n".join(source21_lines[128:163])
    p21_b_segment = "\n".join(source21_lines[755:806])
    cheruel_offset = p21_b_segment.find("M. A. ")
    if cheruel_offset < 0:
        raise SystemExit("bibliography responsibility anchor for M. A. Chéruel is missing")
    cheruel_end = p21_b_segment.find(",", cheruel_offset)
    if cheruel_end < 0:
        raise SystemExit("bibliography responsibility anchor for M. A. Chéruel has no boundary")
    cheruel_surface = p21_b_segment[cheruel_offset:cheruel_end]
    mention_specs = [
        ("m-chp7-p183-n3-epistolario", "chp-7:07_CHP-7_sec_i:l293-389", "cand-7082", p183_segment, "Mazarin: Epistolario inedito", 0, "Cited edition and locator in Haskell’s p.183 n.3."),
        ("m-chp7-p183-n3-mazarin", "chp-7:07_CHP-7_sec_i:l293-389", "cand-1588", p183_segment, "Mazarin", p183_segment.find("Mazarin: Epistolario inedito"), "Name attached to the correspondence entry in Haskell’s p.183 n.3."),
        ("m-chp7-p183-n3-letter-1650", "chp-7:07_CHP-7_sec_i:l293-389", "cand-7084", p183_segment, "letter of 3 June 1650 to Maccarani", 0, "Specific letter named in Haskell’s p.183 n.3."),
        ("m-chp7-p183-n3-maccarani-1650", "chp-7:07_CHP-7_sec_i:l293-389", "cand-1463", p183_segment, "Maccarani", p183_segment.find("letter of 3 June 1650 to Maccarani"), "Recipient named for the 1650 letter in Haskell’s p.183 n.3."),
        ("m-chp7-p183-n3-lettres", "chp-7:07_CHP-7_sec_i:l293-389", "cand-7083", p183_segment, "Mazarin: Lettres pendant son ministère", 0, "Cited edition and locator in Haskell’s p.183 n.3."),
        ("m-chp7-p183-n3-maccarani-1661", "chp-7:07_CHP-7_sec_i:l293-389", "cand-1463", p183_segment, "Maccarani", p183_segment.find("p. 693"), "Recipient named for the 1661 letter in Haskell’s p.183 n.3; the scan confirms the date and text-layer OCR is corrupt."),
        ("m-chp7-p183-n3-letter-1661-20261024", "chp-7:07_CHP-7_sec_i:l293-389", "cand-6798", p183_segment, "p. 693", 0, "Haskell’s locator for the 6 March 1661 letter; the printed scan confirms the adjacent text-layer OCR correction."),
        ("m-chp21-bib-l129-163-benedetti-person-20261024", "chp-21:21_CHP-21Bibliography:l129-163", "cand-7080", p21_a_segment, "Benedetti, Elpidio", 0, "Author responsibility form in Haskell’s bibliography entry."),
        ("m-chp21-bib-l756-806-morbio-20261024", "chp-21:21_CHP-21Bibliography:l756-806", "cand-12439", p21_b_segment, "Carlo Morbio", 0, "Named publishing responsibility in Haskell’s bibliography."),
        ("m-chp21-bib-l756-806-mazarin-epistolario-20261024", "chp-21:21_CHP-21Bibliography:l756-806", "cand-1588", p21_b_segment, "Mazarin, G.", 0, "Principal bibliographic responsibility form in the Epistolario entry."),
        ("m-chp21-bib-l756-806-cheruel-20261024", "chp-21:21_CHP-21Bibliography:l756-806", "cand-12440", p21_b_segment, cheruel_surface, cheruel_offset, "The source text layer contains replacement characters; the physical page image confirms M. A. Chéruel."),
        ("m-chp21-bib-l756-806-mazarin-lettres-20261024", "chp-21:21_CHP-21Bibliography:l756-806", "cand-1588", p21_b_segment, "Mazarin, G.", p21_b_segment.find("Mazarin, G.: Lettres pendant"), "Principal bibliographic responsibility form in the Lettres entry."),
    ]
    existing_mention_ids = {row["mention_id"] for row in mentions}
    new_mentions: list[dict[str, str]] = []
    for mention_id, segment_id, candidate_id, content, surface, offset, note in mention_specs:
        if mention_id in existing_mention_ids:
            raise SystemExit(f"mention ID already exists: {mention_id}")
        start = content.find(surface, offset)
        if start < 0 or content[start:start + len(surface)] != surface:
            raise SystemExit(f"mention anchor does not match source: {mention_id} {surface!r}")
        new_mentions.append({
            "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
            "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)), "note": note,
        })
    mentions.extend(new_mentions)

    candidate_rows_new = []
    alignment_rows_new = []
    for spec in NEW_PERSON_CANDIDATES:
        candidate_rows_new.append({
            "candidate_id": spec["candidate_id"], "index_entry_id": "", "canonical_name": spec["canonical_name"],
            "index_page_range": "", "suggested_type": "person", "status": "open", "index_source_file": "",
            "sub_entry": "", "detail": spec["detail"], "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": spec["source_ref"],
        })
        alignment_rows_new.append({
            "alignment_id": "aln-12756" if spec["candidate_id"] == "cand-12439" else "aln-12757",
            "candidate_id": spec["candidate_id"], "ku_id": "", "external_source": "", "external_id": "",
            "decision": "new", "accessed_date": "", "process_ref": PROCESS_REF, "legacy_ku_id": "",
            "resolution_note": (
                f"source_ref={spec['source_ref']} | mention={spec['mention_id']} | group={spec['group']}; "
                "Haskell’s printed bibliography names this source-local person in a specific editorial or publishing responsibility. "
                "No matching person KU was found in the current manifest; retain the source form without expanding biography or external identity. "
                f"S4 registered as {spec['ku']} in the p.183 note 3 endpoint batch."
            ),
        })
    candidates.extend(candidate_rows_new)
    alignment.extend(alignment_rows_new)

    ku_map = {
        "cand-7080": "units/persons/elpidio-benedetti",
        "cand-7081": "units/archives/benedetti-pompa-funebre-mazarin-1661",
        "cand-7082": "units/archives/mazarin-epistolario-inedito-morbio-1842",
        "cand-7083": "units/archives/mazarin-lettres-pendant-son-ministere-cheruel-1872",
        "cand-7084": "units/archives/mazarin-letter-to-maccarani-1650-06-03",
        "cand-6798": "units/archives/mazarin-letter-to-maccarani-1661-03-06",
    }
    for spec in NEW_PERSON_CANDIDATES:
        ku_map[spec["candidate_id"]] = spec["ku"]
    existing_manifest_ids = {row["ku_id"] for row in manifest}
    if any(ku in existing_manifest_ids for ku in ku_map.values()):
        raise SystemExit("a planned KU ID already exists in the manifest")
    for row in alignment:
        candidate_id = row.get("candidate_id", "")
        if candidate_id in ku_map:
            if row.get("decision") != "new" or row.get("ku_id"):
                raise SystemExit(f"existing S3 new row is not ready for S4 mapping: {candidate_id}")
            row["ku_id"] = ku_map[candidate_id]
            row["resolution_note"] = (row.get("resolution_note", "") + f"; S4 registered as {ku_map[candidate_id]} under {TASK}.").strip("; ")

    manifest_names = {
        "units/persons/elpidio-benedetti": ("埃尔皮迪奥·贝内代蒂（Elpidio Benedetti）", "Elpidio Benedetti", "persons/elpidio-benedetti.md"),
        "units/archives/benedetti-pompa-funebre-mazarin-1661": ("《马扎林葬礼出版物》（Pompa funebre nell’esequie celebrate in Roma al Cardinal Mazarini nella Chiesa di S.S. Vincenzo Anastasio）", "Pompa funebre nell’esequie celebrate in Roma al Cardinal Mazarini nella Chiesa di S.S. Vincenzo Anastasio", "archives/benedetti-pompa-funebre-mazarin-1661.md"),
        "units/archives/mazarin-epistolario-inedito-morbio-1842": ("《马扎林未刊书信集》（Epistolario inedito）", "Epistolario inedito", "archives/mazarin-epistolario-inedito-morbio-1842.md"),
        "units/persons/carlo-morbio": ("卡洛·莫尔比奥（Carlo Morbio）", "Carlo Morbio", "persons/carlo-morbio.md"),
        "units/archives/mazarin-lettres-pendant-son-ministere-cheruel-1872": ("《马扎林任职期间书信集》（Lettres pendant son ministère）", "Lettres pendant son ministère", "archives/mazarin-lettres-pendant-son-ministere-cheruel-1872.md"),
        "units/persons/m-a-cheruel": ("M. A. 谢吕尔（M. A. Chéruel）", "M. A. Chéruel", "persons/m-a-cheruel.md"),
        "units/archives/mazarin-letter-to-maccarani-1661-03-06": ("马扎林致保罗·马卡拉尼的书信（1661年3月6日）（Mazarin letter to Paolo Maccarani, 6 March 1661）", "Mazarin letter to Paolo Maccarani, 6 March 1661", "archives/mazarin-letter-to-maccarani-1661-03-06.md"),
        "units/archives/mazarin-letter-to-maccarani-1650-06-03": ("1650年6月3日致保罗·马卡拉尼的书信（Letter to Paolo Maccarani, 3 June 1650）", "Letter to Paolo Maccarani, 3 June 1650", "archives/mazarin-letter-to-maccarani-1650-06-03.md"),
    }
    for ku_id, (canonical_name, name_en, card_rel) in manifest_names.items():
        spec = FIELDS[ku_id]
        if (spec["canonical_name"], spec["name_en"], spec["card_path"]) != (canonical_name, name_en, f"04-knowledge/units/{card_rel}"):
            raise SystemExit(f"manifest/card identity mismatch for {ku_id}")
        manifest.append({"ku_id": ku_id, "type": spec["type"], "canonical_name": canonical_name, "name_en": name_en, "source_task": TASK, "card_path": f"04-knowledge/units/{card_rel}"})

    headers = ["字段", "内容", "依据"]
    existing_enrichment_ids = {row["enrichment_id"] for row in enrichments}
    existing_natural_keys = {(row["ku_id"], row["field"], row["value"], row.get("source_id", "")) for row in enrichments}
    enrichment_number = max(int(re.search(r"(\d+)$", row["enrichment_id"]).group(1)) for row in enrichments) + 1
    new_enrichments = []
    for ku_id, spec in FIELDS.items():
        if not spec["enrichment"]:
            continue
        tid = table_id(ku_id, "内容 / 文献书目信息", 1, headers)
        for index, (field, value, source_ref, evidence, source_kind) in enumerate(spec["enrichment"], 1):
            natural_key = (ku_id, field, value, SOURCE_ID)
            if natural_key in existing_natural_keys:
                raise SystemExit(f"duplicate enrichment natural key: {natural_key}")
            row = {
                "enrichment_id": f"enr-{enrichment_number:05d}", "ku_id": ku_id, "field": field, "value": value,
                "origin": "book", "source_id": SOURCE_ID, "source_ids": [SOURCE_ID], "source_ref": source_ref,
                "source_citations": ["Francis Haskell, Patrons and Painters, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)."],
                "source_urls": [], "evidence": evidence, "evidence_status": "source_backed", "dispute": None,
                "accessed_date": "", "occurrence_id": stable_id("occ", f"{ku_id}|{field}|{source_ref}|{index}"), "table_id": tid,
                "table_section": "内容 / 文献书目信息", "has_header": True, "table_header": headers, "row_index": index,
                "cells": [field, value, evidence], "unit_evidence_status": "source_backed",
            }
            if row["enrichment_id"] in existing_enrichment_ids:
                raise SystemExit(f"enrichment ID collision: {row['enrichment_id']}")
            new_enrichments.append(row)
            existing_enrichment_ids.add(row["enrichment_id"])
            existing_natural_keys.add(natural_key)
            enrichment_number += 1
    enrichments.extend(new_enrichments)

    source_line_144 = source21_lines[143]
    source_line_783 = source21_lines[782]
    source_lines_784_785 = "\n".join(source21_lines[783:785])
    source_line_164 = source7_lines[163]
    source_line_350 = source7_lines[349]
    new_statement_specs = [
        ("st-chp7-p183-i11-letter-authored-by-mazarin", "chp-7:07_CHP-7_sec_i:l160-168", "cand-6798", "cand-1588", "authored_by", 164, 164, 183, 17, "Haskell attributes the quoted letter to Mazarin, who wrote to Maccarani shortly before his death in 1661.", "Mazarin", ["cand-6798", "cand-1588"], "This records Haskell’s attribution only; the letter itself was not independently consulted."),
        ("st-chp7-p183-i11-letter-addressed-to-maccarani", "chp-7:07_CHP-7_sec_i:l160-168", "cand-6798", "cand-1463", "addressed_to", 164, 164, 183, 17, "Haskell states that Mazarin wrote the quoted letter to Maccarani shortly before his death in 1661.", "Maccarani", ["cand-6798", "cand-1463"], "This records the recipient as stated by Haskell; the letter itself was not independently consulted."),
        ("st-chp7-p183-n3-letter-1661-part-of-lettres", "chp-7:07_CHP-7_sec_i:l293-389", "cand-6798", "cand-7083", "part_of", 350, 350, 183, 17, "Haskell’s note 3 identifies the cited text as the 6 March 1661 letter at vol. IX, p.693 of Lettres pendant son ministère.", "letter of 6 March 1661 to Maccarani", ["cand-6798", "cand-7083", "cand-1463"], "This records Haskell’s locator only; the cited volume and page were not independently consulted."),
        ("st-chp21-bib-l129-163-entry-13-authored-by-benedetti", "chp-21:21_CHP-21Bibliography:l129-163", "cand-7081", "cand-7080", "authored_by", 144, 144, 414, 4, "Haskell’s bibliography attributes the Pompa funebre entry to Elpidio Benedetti.", "Benedetti, Elpidio", ["cand-7081", "cand-7080"], "This records the source-local author attribution in Haskell’s bibliography; the publication was not independently consulted."),
        ("st-chp21-bib-l756-806-entry-16-authored-by-mazarin", "chp-21:21_CHP-21Bibliography:l756-806", "cand-7082", "cand-1588", "authored_by", 783, 783, 429, 19, "Haskell’s bibliography lists Mazarin, G. as the responsible author of Epistolario inedito.", "Mazarin, G.", ["cand-7082", "cand-1588"], "This records the bibliography’s responsibility form only; the edition was not independently consulted."),
        ("st-chp21-bib-l756-806-entry-16-published-by-morbio", "chp-21:21_CHP-21Bibliography:l756-806", "cand-7082", "cand-12439", "published_by", 783, 783, 429, 19, "Haskell’s bibliography states that Epistolario inedito was pubblicato da Carlo Morbio.", "Carlo Morbio", ["cand-7082", "cand-12439"], "The Italian bibliographic responsibility is recorded as printed; it does not add an external identity claim."),
        ("st-chp21-bib-l756-806-entry-17-authored-by-mazarin", "chp-21:21_CHP-21Bibliography:l756-806", "cand-7083", "cand-1588", "authored_by", 784, 785, 429, 19, "Haskell’s bibliography lists Mazarin, G. as the responsible author of Lettres pendant son ministère.", "Mazarin, G.", ["cand-7083", "cand-1588"], "This records the bibliography’s responsibility form only; the edition was not independently consulted."),
        ("st-chp21-bib-l756-806-entry-17-compiled-by-cheruel", "chp-21:21_CHP-21Bibliography:l756-806", "cand-7083", "cand-12440", "compiled_by", 784, 785, 429, 19, "Haskell’s bibliography states that M. A. Chéruel collected Lettres pendant son ministère.", "M. A. Chéruel", ["cand-7083", "cand-12440"], "The source prints initials only; retain the source form without expanding the identity."),
        ("st-chp21-bib-l756-806-entry-17-published-by-cheruel", "chp-21:21_CHP-21Bibliography:l756-806", "cand-7083", "cand-12440", "published_by", 784, 785, 429, 19, "Haskell’s bibliography states that Lettres pendant son ministère was published by M. A. Chéruel.", "M. A. Chéruel", ["cand-7083", "cand-12440"], "The source prints initials only; retain the source form without expanding the identity."),
        ("st-chp7-p183-n3-letter-part-of-epistolario", "chp-7:07_CHP-7_sec_i:l293-389", "cand-7084", "cand-7082", "part_of", 350, 350, 183, 17, "Haskell locates the letter of 3 June 1650 to Maccarani at p.119 of Epistolario inedito.", "letter of 3 June 1650 to Maccarani", ["cand-7084", "cand-7082"], "This records Haskell’s printed edition locator; neither the letter nor the cited page was independently consulted."),
    ]
    statement_ids = {row["statement_id"] for row in statements}
    source_quotes = {
        164: source_line_164,
        144: source_line_144,
        783: source_line_783,
        784: source_lines_784_785,
        350: source_line_350,
    }
    for statement_id, segment_id, subject, obj, predicate, line_start, line_end, printed_page, pdf_page, claim, person_form, mentioned, qualification in new_statement_specs:
        if statement_id in statement_ids:
            raise SystemExit(f"statement ID collision: {statement_id}")
        quote_text = source_quotes[line_start]
        qualifiers = {
            "source_line_start": line_start, "source_line_end": line_end, "printed_page": printed_page,
            "pdf_physical_page": pdf_page, "page_image_source": f"{PDF_21 if segment_id.startswith('chp-21:') else PDF_7}, physical page {pdf_page}",
            "speaker": "Haskell’s printed bibliography" if segment_id.startswith("chp-21:") else "Haskell footnote",
            "text_layer": "bibliographic responsibility statement" if segment_id.startswith("chp-21:") else "authorial footnote",
            "origin": "book", "claim": claim, "qualification": qualification,
            "mentioned_candidate_ids": mentioned, "relation_candidate": True,
            "relation_candidate_note": "S6 candidate: source-local responsibility or document containment is stated in Haskell’s printed source; no claim is made that the cited edition or document was independently inspected.",
            "citation_publication_candidate_id": obj if predicate == "part_of" else subject,
        }
        if line_start == 144:
            qualifiers["bibliographic_record"] = {"author_as_printed": "Benedetti, Elpidio", "printed_page": 414, "pdf_physical_page": 4}
            qualifiers["page_image_transcription"] = "Benedetti, Elpidio: Pompa funebre Nell’Esequie celebrate in Roma al Cardinal Mazarini nella Chiesa di S.S. Vincenzo Anastasio, In Roma 1661."
        elif line_start == 783:
            qualifiers["bibliographic_record"] = {"author_as_printed": "Mazarin, G.", "responsibility_as_printed": "pubblicato da Carlo Morbio", "printed_page": 429, "pdf_physical_page": 19}
            qualifiers["page_image_transcription"] = source_line_783
        elif line_start == 784:
            qualifiers["bibliographic_record"] = {"author_as_printed": "Mazarin, G.", "responsibility_as_printed": "recueillies et publiées par M. A. Chéruel", "volume_count": 9, "publication_details_as_printed": "Paris 1872–1906", "printed_page": 429, "pdf_physical_page": 19}
            qualifiers["page_image_transcription"] = "Mazarin, G.: Lettres pendant son ministère recueillies et publiées par M. A. Chéruel, 9 vols., Paris 1872–1906."
        elif line_start == 164:
            qualifiers.update({"speaker": "Haskell’s narrative", "text_layer": "authorial prose with embedded quotation", "footnote_marker": 3, "footnote_number": 3, "footnote_segment": "chp-7:07_CHP-7_sec_i:l293-389", "citation_publication_candidate_id": "cand-7083", "citation_locator": "Lettres pendant son ministère, vol. IX, p.693", "cited_material_not_independently_consulted": True, "related_body_statement_ids": ["st-chp7-p183-i11"], "page_image_transcription": "letter of 6 March 1661 to Maccarani", "transcription_note": "The Markdown OCR around this span is corrupt; the printed page image was checked."})
        elif line_start == 350 and subject == "cand-6798":
            qualifiers.update({"footnote_marker": 3, "footnote_number": 3, "footnote_segment": segment_id, "citation_publication_candidate_id": "cand-7083", "citation_locator": "Lettres pendant son ministère, vol. IX, p.693", "cited_material_not_independently_consulted": True, "page_image_transcription": "letter of 6 March 1661 to Maccarani", "transcription_note": "The Markdown OCR around this span is corrupt; the printed page image was checked."})
        else:
            qualifiers.update({"footnote_marker": 3, "footnote_number": 3, "footnote_segment": segment_id, "citation_publication_candidate_id": "cand-7082", "citation_locator": "Epistolario inedito, p.119", "cited_material_not_independently_consulted": True})
        if predicate == "published_by" and obj == "cand-12439":
            qualifiers["mentioned_candidate_ids"] = ["cand-7082", "cand-12439"]
        statements.append({
            "statement_id": statement_id, "segment_id": segment_id, "subject_candidate_id": subject,
            "object_candidate_id": obj, "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": quote_text, "origin": "book", "source_file": SOURCE_21 if segment_id.startswith("chp-21:") else SOURCE_7,
        })
        statement_ids.add(statement_id)

    # Attach the newly resolved responsible people to the already-existing bibliographic entry statements.
    for statement_id, extra_ids in {
        "st-chp21-bib-l129-163-entry-13": ["cand-7080"],
        "st-chp21-bib-l756-806-entry-16": ["cand-1588", "cand-12439"],
        "st-chp21-bib-l756-806-entry-17": ["cand-1588", "cand-12440"],
    }.items():
        row = statement_by_id[statement_id]
        qualifiers = row.setdefault("qualifiers", {})
        values = qualifiers.setdefault("mentioned_candidate_ids", [])
        for candidate_id in extra_ids:
            if candidate_id not in values:
                values.append(candidate_id)

    relation_rows_new = [
        ("units/archives/mazarin-letter-to-maccarani-1661-03-06", "units/persons/mazarin", "authored_by", "1661-03-06", "Haskell-attributed letter author", "Haskell’s p.183 narrative attributes the quoted letter to Mazarin; the letter was not independently consulted.", "line 164; printed p.183; PDF physical page 17; st-chp7-p183-i11", "st-chp7-p183-i11-letter-authored-by-mazarin"),
        ("units/archives/mazarin-letter-to-maccarani-1661-03-06", "units/persons/paolo-maccarani", "addressed_to", "1661-03-06", "Haskell-identified recipient", "Haskell says Mazarin wrote to Maccarani; note 3 identifies the letter as dated 6 March 1661.", "lines 164, 350; printed p.183 n.3; PDF physical page 17", "st-chp7-p183-i11-letter-addressed-to-maccarani"),
        ("units/archives/mazarin-letter-to-maccarani-1661-03-06", "units/archives/mazarin-lettres-pendant-son-ministere-cheruel-1872", "part_of", "", "Haskell citation locator", "Haskell locates the letter at vol. IX, p.693; the volume and cited page were not independently consulted.", "line 350; printed p.183 n.3; PDF physical page 17", "st-chp7-p183-n3-letter-1661-part-of-lettres"),
        ("units/archives/patrons-and-painters", "units/archives/benedetti-pompa-funebre-mazarin-1661", "cites", "", "第7章注3书目引文定位", "p.5；仅记录哈斯克尔的引注，所引页未独立查阅。", "line 350; printed p.183 n.3; PDF physical page 17", "st-chp7-p183-n3-cite-benedetti"),
        ("units/archives/patrons-and-painters", "units/archives/mazarin-epistolario-inedito-morbio-1842", "cites", "", "第7章注3书目引文定位", "p.119（称为1650年6月3日致 Maccarani 的信）；该版与该页未独立查阅。", "line 350; printed p.183 n.3; PDF physical page 17", "st-chp7-p183-n3-cite-epistolario"),
        ("units/archives/patrons-and-painters", "units/archives/mazarin-lettres-pendant-son-ministere-cheruel-1872", "cites", "", "第7章注3书目引文定位", "vol. IX, p.693（称为1661年3月6日致 Maccarani 的信）；该版与该页未独立查阅。", "line 350; printed p.183 n.3; PDF physical page 17", "st-chp7-p183-n3-cite-lettres"),
        ("units/archives/mazarin-letter-to-maccarani-1650-06-03", "units/persons/paolo-maccarani", "addressed_to", "1650-06-03", "收信人", "哈斯克尔注3识别此信为1650年6月3日致 Paolo Maccarani；书信未独立查阅。", "line 350; printed p.183 n.3; PDF physical page 17", "st-chp7-p183-n3-letter-1650-to-maccarani"),
        ("units/archives/benedetti-pompa-funebre-mazarin-1661", "units/persons/elpidio-benedetti", "authored_by", "1661", "Haskell’s bibliography author attribution", "第21章书目列 Benedetti, Elpidio 为责任者；出版物未独立查阅。", "line 144; printed p.414; PDF physical page 4", "st-chp21-bib-l129-163-entry-13-authored-by-benedetti"),
        ("units/archives/mazarin-epistolario-inedito-morbio-1842", "units/persons/mazarin", "authored_by", "", "Haskell’s bibliography author attribution", "书目条目以 Mazarin, G. 起首；只记录来源的责任形式。", "line 783; printed p.429; PDF physical page 19", "st-chp21-bib-l756-806-entry-16-authored-by-mazarin"),
        ("units/archives/mazarin-epistolario-inedito-morbio-1842", "units/persons/carlo-morbio", "published_by", "1842", "Haskell’s bibliography: pubblicato da", "书目明记 pubblicato da Carlo Morbio；原书未独立查阅。", "line 783; printed p.429; PDF physical page 19", "st-chp21-bib-l756-806-entry-16-published-by-morbio"),
        ("units/archives/mazarin-lettres-pendant-son-ministere-cheruel-1872", "units/persons/mazarin", "authored_by", "", "Haskell’s bibliography author attribution", "书目条目以 Mazarin, G. 起首；只记录来源的责任形式。", "lines 784–785; printed p.429; PDF physical page 19", "st-chp21-bib-l756-806-entry-17-authored-by-mazarin"),
        ("units/archives/mazarin-lettres-pendant-son-ministere-cheruel-1872", "units/persons/m-a-cheruel", "compiled_by", "", "Haskell’s bibliography: recueillies par", "书目称 M. A. Chéruel 汇编；仅保留书目所列姓名形式。", "lines 784–785; printed p.429; PDF physical page 19", "st-chp21-bib-l756-806-entry-17-compiled-by-cheruel"),
        ("units/archives/mazarin-lettres-pendant-son-ministere-cheruel-1872", "units/persons/m-a-cheruel", "published_by", "1872–1906", "Haskell’s bibliography: publiées par", "书目称 M. A. Chéruel 刊行该九卷本；仅记录来源责任归属。", "lines 784–785; printed p.429; PDF physical page 19", "st-chp21-bib-l756-806-entry-17-published-by-cheruel"),
        ("units/archives/mazarin-letter-to-maccarani-1650-06-03", "units/archives/mazarin-epistolario-inedito-morbio-1842", "part_of", "", "哈斯克尔所引刊本定位", "哈斯克尔将该信定位于 Epistolario inedito p.119；关系表示书目所引刊本中的文本定位，未声称查阅原信。", "line 350; printed p.183 n.3; PDF physical page 17", "st-chp7-p183-n3-letter-part-of-epistolario"),
    ]
    used_relation_ids = {row["relation_id"] for row in relations}
    used_natural_keys = {(row["subject_ku_id"], row["predicate"], row["object_ku_id"], row.get("time", ""), row.get("role", ""), row.get("scope", "")) for row in relations}
    next_relation = max(int(re.search(r"(\d+)$", value).group(1)) for value in used_relation_ids) + 1
    for index, item in enumerate(relation_rows_new):
        subject, obj, predicate, time, role, scope, source_span, statement_id = item
        natural = (subject, predicate, obj, time, role, scope)
        if natural in used_natural_keys:
            raise SystemExit(f"duplicate relation natural key: {natural}")
        relation_id = f"rel-{next_relation + index:04d}"
        if relation_id in used_relation_ids:
            raise SystemExit(f"relation ID collision: {relation_id}")
        relations.append({
            "relation_id": relation_id, "subject_ku_id": subject, "object_ku_id": obj, "predicate": predicate,
            "time": time, "role": role, "scope": scope, "origin": "book", "status": "formal",
            "source_id": SOURCE_ID, "source_span": source_span, "source_file": SOURCE_21 if "printed p.429" in source_span or "printed p.414" in source_span else SOURCE_7,
            "note": f"S2 relation candidate: {statement_id}; cited material and editions remain source-limited as stated.",
        })
        used_relation_ids.add(relation_id)
        used_natural_keys.add(natural)

    next_backlog = max(int(re.search(r"(\d+)$", row["backlog_id"]).group(1)) for row in backlog) + 1
    backlog_rows_new = [
        {"backlog_id": f"bl-{next_backlog:04d}", "canonical_name": "Unidentified 1646 avviso on the Mazarin facade project", "suggested_type": "archive", "status": "undecided", "source_id": SOURCE_ID, "source_ref": "chp-7:07_CHP-7_sec_i:l293-389#L350", "statement_id": "st-chp7-p183-n3-cite-avviso", "endpoint_role": "cited notice", "candidate_id": "cand-7079", "ku_id": "", "decision_note": "Retain S3 undecided and S6 pending: Haskell identifies an avviso at Roma (1938), p.477, but the underlying notice’s identity/granularity remains unresolved. Revisit when the notice or exact issue is independently identified; do not substitute the containing publication without an explicit identity decision.", "process_ref": PROCESS_REF},
        {"backlog_id": f"bl-{next_backlog + 1:04d}", "canonical_name": "Maccarani’s gallery of statues and paintings (reported for 1675)", "suggested_type": "", "status": "undecided", "source_id": SOURCE_ID, "source_ref": "chp-7:07_CHP-7_sec_i:l293-389#L350", "statement_id": "st-chp7-p183-n3-maccarani-gallery-1675", "endpoint_role": "object of reported ownership", "candidate_id": "cand-7085", "ku_id": "", "decision_note": "Retain as untyped and keep its S6 candidate pending: the current taxonomy has no collection type, and Haskell reports ownership through Spon and Wheler, whose cited page was not independently consulted. Revisit after an applicable type boundary or further direct evidence is available.", "process_ref": PROCESS_REF},
        {"backlog_id": f"bl-{next_backlog + 2:04d}", "canonical_name": "Carlo Morbio", "suggested_type": "person", "status": "completed", "source_id": SOURCE_ID, "source_ref": "chp-21:21_CHP-21Bibliography:l756-806#L783", "statement_id": "st-chp21-bib-l756-806-entry-16-published-by-morbio", "endpoint_role": "publishing responsibility", "candidate_id": "cand-12439", "ku_id": "units/persons/carlo-morbio", "decision_note": "S1 candidate cand-12439 and S3 source-local new identity were registered in S4 as units/persons/carlo-morbio. The relationship records Haskell’s bibliographic wording only; no biography or external identity is asserted.", "process_ref": PROCESS_REF},
        {"backlog_id": f"bl-{next_backlog + 3:04d}", "canonical_name": "M. A. Chéruel", "suggested_type": "person", "status": "completed", "source_id": SOURCE_ID, "source_ref": "chp-21:21_CHP-21Bibliography:l756-806#L784", "statement_id": "st-chp21-bib-l756-806-entry-17-compiled-by-cheruel", "endpoint_role": "compiler and publishing responsibility", "candidate_id": "cand-12440", "ku_id": "units/persons/m-a-cheruel", "decision_note": "S1 candidate cand-12440 and S3 source-local new identity were registered in S4 as units/persons/m-a-cheruel. Preserve initials as printed and do not expand biography or external identity.", "process_ref": PROCESS_REF},
    ]
    backlog.extend(backlog_rows_new)

    accepted = before[ROOT / "04-knowledge/accepted.yml"].decode("utf-8-sig")
    accepted_paths = [spec["card_path"] for spec in FIELDS.values()]
    if any(path in accepted for path in accepted_paths):
        raise SystemExit("one or more planned cards are already listed in accepted.yml")
    insertion = "\nclaims:\n"
    if accepted.count(insertion) != 1:
        raise SystemExit("accepted.yml units/claims boundary changed")
    accepted_additions = "\n".join(f"- {path}" for path in accepted_paths) + "\n"
    accepted = accepted.replace(insertion, "\n" + accepted_additions + "claims:\n", 1)

    outputs: dict[Path, bytes] = {
        table_paths["04-knowledge/tables/entity-candidates.csv"]: encode_csv(candidates, candidate_fields),
        table_paths["04-knowledge/tables/alignment.csv"]: encode_csv(alignment, alignment_fields),
        table_paths["04-knowledge/tables/mentions.csv"]: encode_csv(mentions, mention_fields),
        table_paths["04-knowledge/tables/book-statements.jsonl"]: encode_jsonl(statements),
        table_paths["04-knowledge/tables/ku-manifest.csv"]: encode_csv(manifest, manifest_fields),
        table_paths["04-knowledge/tables/enrichment.jsonl"]: encode_jsonl(enrichments),
        table_paths["04-knowledge/tables/relations.csv"]: encode_csv(relations, relation_fields),
        table_paths["04-knowledge/tables/candidate-backlog.csv"]: encode_csv(backlog, backlog_fields),
        ROOT / "04-knowledge/accepted.yml": accepted.encode("utf-8"),
    }
    new_cards: dict[Path, bytes] = {}
    for ku_id, spec in FIELDS.items():
        path = ROOT / spec["card_path"]
        if path.exists():
            raise SystemExit(f"planned card path already exists: {spec['card_path']}")
        new_cards[path] = build_card(ku_id, spec)
    outputs.update(new_cards)

    # Require all new relation endpoints to resolve before any write.
    manifest_ids_after = {row["ku_id"] for row in manifest}
    for row in relations:
        if row.get("status") == "formal" and (row.get("subject_ku_id") not in manifest_ids_after or row.get("object_ku_id") not in manifest_ids_after):
            raise SystemExit(f"formal relation has an unresolved endpoint: {row.get('relation_id')}")

    report = {
        "mode": "apply" if args.apply else "dry_run",
        "new_candidates": [spec["candidate_id"] for spec in NEW_PERSON_CANDIDATES],
        "S4_new_ku_mappings": len(ku_map), "new_cards": len(new_cards),
        "new_mentions": len(new_mentions), "new_S2_statements": len(new_statement_specs),
        "new_S5_fields": len(new_enrichments), "new_formal_S6_relations": len(relation_rows_new),
        "new_backlog_rows": len(backlog_rows_new), "touched_files": [p.relative_to(ROOT).as_posix() for p in outputs],
        "before_sha256": {p.relative_to(ROOT).as_posix(): sha256(raw) for p, raw in before.items() if p in outputs},
        "output_sha256": {p.relative_to(ROOT).as_posix(): sha256(raw) for p, raw in outputs.items()},
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print("dry-run only; no files written")
        return

    recovery = ROOT / "06-runtime/recovery" / "s3-s4-s5-s6-chp7-p183-note3-endpoints-20261024"
    if recovery.exists():
        raise SystemExit(f"recovery directory already exists: {recovery}")
    recovery.mkdir(parents=True)
    backup_manifest = {}
    for path, raw in before.items():
        if path in outputs:
            rel = path.relative_to(ROOT)
            backup = recovery / "original" / rel
            backup.parent.mkdir(parents=True, exist_ok=True)
            backup.write_bytes(raw)
            backup_manifest[rel.as_posix()] = sha256(raw)
    (recovery / "backup-manifest.json").write_text(json.dumps(backup_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    created: list[Path] = []
    written: list[Path] = []
    try:
        for path, raw in outputs.items():
            if path.exists() and path not in before:
                raise RuntimeError(f"target appeared after dry-run: {path}")
            if not path.exists():
                created.append(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
                handle.write(raw)
                temp_path = Path(handle.name)
            temp_path.replace(path)
            written.append(path)
            if sha256(path.read_bytes()) != sha256(raw):
                raise RuntimeError(f"post-write hash mismatch: {path}")
    except Exception:
        for path in reversed(written):
            if path in before:
                path.write_bytes(before[path])
            elif path.exists():
                path.unlink()
        for path in created:
            if path.exists():
                path.unlink()
        raise
    print(f"apply complete: {len(written)} files; recovery copy: {recovery.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
