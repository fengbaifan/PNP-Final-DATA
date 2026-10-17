from __future__ import annotations

import argparse
import csv
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
ALIGNMENT = TABLES / "alignment.csv"
ENTITY = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ENRICHMENT = TABLES / "enrichment.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-18"
ANCHOR = "s4-person-direct-endpoints-h-section-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
HASKELL_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."


def source(location: str, summary: str, quote: str, file: str, span: str) -> dict:
    return {"location": location, "summary": summary, "quote": quote, "file": file, "span": span}


TARGETS = [
    {
        "primary": "cand-1287", "entry": "H.csv#2", "index_name": "Hamen, Juan van der",
        "canonical_name": "Hamen, Juan van der", "pages": "400",
        "group": "new-person:der-hamen-juan-van-98401ebaa1", "ku": "units/persons/juan-van-der-hamen",
        "name_zh": "胡安·范德尔·哈门", "name_en": "Juan van der Hamen",
        "name_rows": [("索引名", "Hamen, Juan van der", "S1（索引H.csv#2）"), ("正文姓名形式", "Juan van der Hamen", "S2（第20章后记p.400）")],
        "sources": [source("第20章后记；印刷页400", "Haskell转述一篇关于Cassiano 1626年西班牙旅行的文章，比较两幅已佚肖像，并称Cassiano更喜欢Juan van der Hamen所作的一幅。被引文章未独立查阅。", "one (also lost) by Juan van der Hamen", "02-sources/02-Markdown/20_CHP-20Postscript.md", "line 56; print p.400")],
        "zh": "本卡登记索引H.csv#2所列Juan van der Hamen。第20章后记p.400将他列为一幅已佚肖像的画家；相关Harris文章仅由Haskell转述，未独立查阅。",
        "en": "This card registers Juan van der Hamen under index H.csv#2. Chapter 20, p.400, names him as the painter of one now-lost portrait; Haskell’s cited Harris article was not independently consulted.",
        "context_zh": "Haskell转述Cassiano在1626年西班牙旅行期间比较Velasquez与van der Hamen所作的两幅已佚肖像，并称Cassiano更喜欢后者。作品候选cand-10952保持独立。",
        "context_en": "Haskell reports that during Cassiano’s 1626 journey in Spain, he compared two now-lost portraits, by Velasquez and van der Hamen, and preferred the latter. Work candidate cand-10952 remains separate.",
        "relations": [], "endpoints": {}, "external": None,
    },
    {
        "primary": "cand-1288", "entry": "H.csv#3", "index_name": "Handel, George Frederick",
        "canonical_name": "Handel, George Frederick", "pages": "281",
        "group": "new-person:frederick-george-handel-b7a9ead66a", "ku": "units/persons/george-frederick-handel",
        "name_zh": "乔治·弗雷德里克·亨德尔", "name_en": "George Frederick Handel",
        "name_rows": [("索引名", "Handel, George Frederick", "S1（索引H.csv#3）"), ("正文姓名形式", "Handel", "S2（第10章p.281）")],
        "sources": [source("第10章导论；印刷页281", "Haskell提到Handel在Canons为家主安排音乐会；姓名全形来自同页索引。", "concerts organised by Handel", "02-sources/02-Markdown/10_CHP-10_intro.md", "line 129; print p.281")],
        "zh": "本卡按索引H.csv#3登记George Frederick Handel。第10章p.281称Canons的音乐会由Handel组织；正文仅用姓氏，卡片不据此补写其他传记信息。",
        "en": "This card registers George Frederick Handel under index H.csv#3. Chapter 10, p.281, says Handel organized concerts at Canons; the body uses only his surname, and no further biography is added.",
        "context_zh": "Haskell在介绍Canons音乐会时以姓氏Handel指称此人。此项为书内身份登记，不独立核实音乐会组织情况。",
        "context_en": "Haskell names Handel by surname in the account of concerts at Canons. This is a source-local identity registration and does not independently verify the concert account.",
        "relations": [], "endpoints": {}, "external": None,
    },
    {
        "primary": "cand-1291", "entry": "H.csv#7", "index_name": "Harrach, Count",
        "canonical_name": "Harrach, Count", "pages": "200",
        "group": "new-person:aloys-thomas-raimund-harrach-20261018", "ku": "units/persons/aloys-thomas-raimund-harrach",
        "name_zh": "阿洛伊斯·托马斯·赖蒙德·哈拉赫", "name_en": "Aloys Thomas Raimund Harrach",
        "name_rows": [("索引名", "Harrach, Count", "S1（索引H.csv#7）"), ("正文称谓", "Count Harrach", "S2（第7章p.200）")],
        "sources": [
            source("第7章第V节；印刷页200", "Haskell称这一过程在1728年后由Count Harrach继续推进，并以奥地利总督作评价。", "after 1728 by the most cultivated of all the Austrian viceroys, Count Harrach", "02-sources/02-Markdown/07_CHP-7_sec_v.md", "line 16; print p.200"),
            source("第7章第V节注7；印刷页200", "Haskell称Count Harrach是那不勒斯艺术最热心的奥地利赞助人，并以其收藏为例。", "Harrach was the most enthusiastic Austrian patron of Neapolitan art", "02-sources/02-Markdown/07_CHP-7_sec_v.md", "line 68; print p.200 n.7"),
        ],
        "zh": "本书以Count Harrach称呼此人；S3将该身份与Aloys Thomas Raimund Harrach的权威记录相对齐。Haskell在第7章p.200讨论其那不勒斯艺术赞助语境。",
        "en": "The book calls this person Count Harrach; S3 aligns that identity with the authority record for Aloys Thomas Raimund Harrach. Haskell discusses him in the context of Neapolitan art patronage in chapter 7, p.200.",
        "context_zh": "正文称Count Harrach在1728年后继续推进相关过程；注7将他称作那不勒斯艺术的奥地利赞助人。两条S2关系候选中的作者评价与收藏语境均保留待S6裁决。",
        "context_en": "The body says Count Harrach continued the process after 1728; footnote 7 characterizes him as an Austrian patron of Neapolitan art. The author’s evaluation and collection context in both S2 candidates remain for S6 review.",
        "relations": ["st-chp7-p200-v-harrach-continues-process-after-1728", "st-chp7-p200-n7-harrach-patronage"],
        "endpoints": {
            "st-chp7-p200-v-harrach-continues-process-after-1728": ("cand-1291", "cand-1729", "continued_process_after_1728"),
            "st-chp7-p200-n7-harrach-patronage": ("cand-1291", "cand-7356", "described_as_most_enthusiastic_austrian_patron_of"),
        },
        "external": {"source": "Deutsche Biographie / GND", "id": "132626748", "label": "Aloys Thomas Raimund Graf von Harrach", "url": "https://www.deutsche-biographie.de/sfz26099.html", "scope": "身份消歧；该记录的姓名变体和GND号匹配书内Count Harrach。"},
    },
    {
        "primary": "cand-1293", "entry": "H.csv#9", "index_name": "Helmbrecker, Theodor",
        "canonical_name": "Helmbrecker, Theodor", "pages": "158",
        "group": "new-person:helmbrecker-theodor-5737710433", "ku": "units/persons/theodor-helmbreker",
        "name_zh": "特奥多尔·赫尔姆布雷克", "name_en": "Theodor Helmbreker",
        "name_rows": [("索引名", "Helmbrecker, Theodor", "S1（索引H.csv#9）"), ("正文姓名形式", "Theodor Helmbrecker", "S2（第6章p.158）")],
        "sources": [source("第6章第IV节；印刷页158", "Haskell称Marucelli是画家Theodor Helmbrecker最热心的欣赏者，并说画家为他作了十六幅画。", "Theodor Helmbrecker whose most enthusiastic admirer he was and who painted sixteen pictures for him", "02-sources/02-Markdown/06_CHP-6_sec_iv.md", "line 15; print p.158")],
        "zh": "本书索引及第6章p.158将画家写作Theodor Helmbrecker。S3按Uffizi的身份记录采用Theodor Helmbreker作为规范展示名，原书拼写保留在名称表。",
        "en": "The index and chapter 6, p.158, spell the painter’s name Theodor Helmbrecker. S3 uses Theodor Helmbreker, the form in the Uffizi identity record, as the display name while preserving the book’s spelling in the name table.",
        "context_zh": "Haskell称Marucelli是Helmbrecker最热心的欣赏者，并说Helmbrecker为其作了十六幅画；画作数量及赞助关系均按Haskell原文语气保留。",
        "context_en": "Haskell calls Marucelli Helmbrecker’s most enthusiastic admirer and says Helmbrecker painted sixteen pictures for him; both the count and patronage account remain attributed to Haskell.",
        "relations": ["st-chp6-p158-helmbrecker-admired", "st-chp6-p158-helmbrecker-pictures-for-marucelli"],
        "endpoints": {
            "st-chp6-p158-helmbrecker-admired": ("cand-1554", "cand-1293", "described_as_enthusiastically_admired_by_collector"),
            "st-chp6-p158-helmbrecker-pictures-for-marucelli": ("cand-1293", "cand-1554", "painted_pictures_for_patron"),
        },
        "external": {"source": "Uffizi Galleries", "id": "https://www.uffizi.it/en/artworks/rustic-scene", "label": "Rustic scene — Theodor Helmbreker", "url": "https://www.uffizi.it/en/artworks/rustic-scene", "scope": "身份消歧；记录将Theodor Helmbreker称为Monsù Teodoro，并列出Marucelli为该画捐赠者。"},
    },
    {
        "primary": "cand-1294", "entry": "H.csv#10", "index_name": "Henri III of France",
        "canonical_name": "Henri III of France", "pages": "255",
        "group": "new-person:france-henri-iii-of-6f746d232e", "ku": "units/persons/henri-iii-of-france",
        "name_zh": "法国国王亨利三世", "name_en": "Henri III of France",
        "name_rows": [("索引名", "Henri III of France", "S1（索引H.csv#10）"), ("正文姓名形式", "Henri III of France", "S2（第9章p.255）")],
        "sources": [source("第9章导论；印刷页255", "Haskell称Tiepolo描绘Contarini家族于1574年在Mira迎接Henri III的场景。", "the welcome they gave in 1574 to Henri III of France", "02-sources/02-Markdown/09_CHP-9_intro.md", "line 153; print p.255")],
        "zh": "本卡登记索引H.csv#10所列法国国王Henri III。第9章p.255在Contarini家族的1574年迎宾场景中提及他。",
        "en": "This card registers Henri III of France under index H.csv#10. Chapter 9, p.255, mentions him in the Contarini family’s 1574 welcome scene.",
        "context_zh": "Haskell称Tiepolo描绘了Contarini家族在Mira迎接Henri III的场面；与该人物同段出现的作品、事件和地点候选分别保留，不在S4登记关系。",
        "context_en": "Haskell says Tiepolo depicted the Contarini family welcoming Henri III at Mira; the co-mentioned work, event, and place candidates remain separate, and no relation is registered at S4.",
        "relations": [], "endpoints": {}, "external": None,
    },
    {
        "primary": "cand-1296", "entry": "H.csv#12", "index_name": "Henrietta Maria, Queen of England",
        "canonical_name": "Henrietta Maria, Queen of England", "pages": "179",
        "group": "new-person:england-henrietta-maria-of-b9baa37f48", "ku": "units/persons/henrietta-maria",
        "name_zh": "亨利埃塔·玛丽亚", "name_en": "Henrietta Maria",
        "name_rows": [("索引名", "Henrietta Maria, Queen of England", "S1（索引H.csv#12）"), ("正文指称", "the Queen", "S2（第7章p.179；Charles的王后语境）")],
        "sources": [source("第7章第I节；印刷页179", "Haskell称Cardinal Barberini送给王后许多画作，并称Bernini为王后制作的胸像后来取消。", "Cardinal Barberini sent the Queen so many pictures", "02-sources/02-Markdown/07_CHP-7_sec_i.md", "line 122; print p.179"), source("第7章第I节；印刷页179", "Haskell称Bernini的王后胸像必须取消。", "Bernini’s bust of the Queen had to be cancelled", "02-sources/02-Markdown/07_CHP-7_sec_i.md", "line 122; print p.179")],
        "zh": "本卡登记索引H.csv#12所列Henrietta Maria。第7章p.179在Charles的王后语境中以the Queen称呼她，并叙述向她送画及计划中的胸像取消。",
        "en": "This card registers Henrietta Maria under index H.csv#12. Chapter 7, p.179, refers to her as ‘the Queen’ in the context of Charles’s consort and recounts pictures sent to her and the cancellation of a planned bust.",
        "context_zh": "Haskell称Cardinal Barberini送给王后许多画作，Bernini的胸像计划后来取消。两项均作为作者叙述保留；Cardinal Barberini身份仍未具名。",
        "context_en": "Haskell says Cardinal Barberini sent the Queen many pictures and that Bernini’s bust commission was later cancelled. Both remain attributed to the author; Cardinal Barberini is unidentified.",
        "relations": ["st-chp7-p179-i17"],
        "endpoints": {"st-chp7-p179-i17": ("cand-6757", "cand-1296", "sent_pictures_for_display_in_queens_private_chapel")},
        "external": None,
    },
    {
        "primary": "cand-1297", "entry": "H.csv#13", "index_name": "Hervey, Sir Robert",
        "canonical_name": "Hervey, Sir Robert", "pages": "305",
        "group": "new-person:hervey-robert-b62bf2d0f9", "ku": "units/persons/robert-hervey",
        "name_zh": "罗伯特·赫维爵士", "name_en": "Sir Robert Hervey",
        "name_rows": [("索引名", "Hervey, Sir Robert", "S1（索引H.csv#13）"), ("正文姓名形式", "Sir Robert Hervey", "S2（第10章p.305）")],
        "sources": [source("第10章导论；印刷页305", "Haskell称Canaletto在1730年代后半为Sir Robert Hervey绘制了另一组二十幅威尼斯景观。", "another series of twenty for Sir Robert Hervey", "02-sources/02-Markdown/10_CHP-10_intro.md", "line 432; print p.305")],
        "zh": "本卡登记索引H.csv#13所列Sir Robert Hervey。第10章p.305将他置于Canaletto晚1730年代绘制二十幅景观的叙述中；对应work候选cand-9220仍待身份裁决。",
        "en": "This card registers Sir Robert Hervey under index H.csv#13. Chapter 10, p.305, places him in Haskell’s account of twenty views painted by Canaletto in the late 1730s; work candidate cand-9220 remains undecided.",
        "context_zh": "书中称Sir Robert Hervey为Canaletto另一组二十幅景观的对象；该组尚无稳定作品身份，人物与work候选保持分开。与p.349的Lord Hervey不因同姓合并。",
        "context_en": "The book names Sir Robert Hervey as the patron of another group of twenty Canaletto views; the group lacks a settled work identity, so the person and work candidate remain separate. He is not merged with Lord Hervey from p.349 on surname alone.",
        "relations": [], "endpoints": {}, "external": None,
        "mention_note": "第10章p.305的S2陈述将Canaletto与work候选cand-9220相连，Sir Robert Hervey只列为限定中的具名人物；该work仍待证，未创建正式关系。",
    },
    {
        "primary": "cand-1298", "entry": "H.csv#14", "index_name": "Hervey, Lord",
        "canonical_name": "Hervey, Lord", "pages": "349",
        "group": "new-person:john-hervey-2nd-baron-hervey-20261018", "ku": "units/persons/john-hervey-2nd-baron-hervey",
        "name_zh": "约翰·赫维（第二代赫维男爵）", "name_en": "John Hervey, 2nd Baron Hervey of Ickworth",
        "name_rows": [("索引名", "Hervey, Lord", "S1（索引H.csv#14）"), ("正文称谓", "Lord Hervey", "S2（第14章p.349）")],
        "sources": [source("第14章导论；印刷页349", "Haskell称Algarotti在伦敦期间应对Lord Hervey和Lady Mary Wortley Montagu的追求。", "the advances of Lord Hervey", "02-sources/02-Markdown/14_CHP-14_intro.md", "line 25; print p.349")],
        "zh": "本书第14章p.349称Lord Hervey；S3依据Westminster School Archive & Collections身份记录将其对齐为John Hervey, 2nd Baron Hervey of Ickworth。",
        "en": "Chapter 14, p.349, calls him Lord Hervey; S3 aligns this titleholder with John Hervey, 2nd Baron Hervey of Ickworth, using the Westminster School Archive & Collections authority record.",
        "context_zh": "Haskell称Algarotti在伦敦时应对Lord Hervey与Lady Mary Wortley Montagu的追求；这是Haskell的社会关系描写，不作外部事实核实。",
        "context_en": "Haskell says Algarotti played off Lord Hervey’s advances and Lady Mary Wortley Montagu’s; this remains Haskell’s characterization and is not independently verified here.",
        "relations": ["st-chp14-p349-social-advances-hervey"],
        "endpoints": {"st-chp14-p349-social-advances-hervey": ("cand-0080", "cand-1298", "played_off_social_advances_from")},
        "external": {"source": "Westminster School Archive & Collections", "id": "GB-2014-WSA-00767", "label": "John Hervey, 2nd Baron Hervey of Ickworth", "url": "https://collections.westminster.org.uk/index.php/hervey-john-hervey-baron-1696-1743", "scope": "身份消歧；记录规范名、1696–1743年及1723年起称Lord Hervey。"},
    },
    {
        "primary": "cand-1299", "entry": "H.csv#15", "index_name": "Hildebrandt, Lucas von",
        "canonical_name": "Hildebrandt, Lucas von", "pages": "201",
        "group": "new-person:hildebrandt-lucas-von-425ee5c0e1", "ku": "units/persons/lucas-von-hildebrandt",
        "name_zh": "约翰·卢卡斯·冯·希尔德布兰特", "name_en": "Johann Lucas von Hildebrandt",
        "name_rows": [("索引名", "Hildebrandt, Lucas von", "S1（索引H.csv#15）"), ("正文姓名形式", "Lucas von Hildebrandt", "S2（第7章p.201）")],
        "sources": [source("第7章第V节；印刷页201", "Haskell把两座Belvederes归于Lucas von Hildebrandt；两座建筑作为一对保留。", "Lucas von Hildebrandt", "02-sources/02-Markdown/07_CHP-7_sec_v.md", "lines 46-47; print p.201")],
        "zh": "本书索引和第7章p.201称Lucas von Hildebrandt；S3依据MAK Collection Online规范记录将该人物规范展示为Johann Lucas von Hildebrandt。",
        "en": "The index and chapter 7, p.201, use Lucas von Hildebrandt; S3 uses the MAK Collection Online authority form Johann Lucas von Hildebrandt as the display name.",
        "context_zh": "Haskell将两座Belvederes整体归于Hildebrandt，没有在这段中区分各自建筑或施工阶段。该归属陈述留待S6关系裁决。",
        "context_en": "Haskell attributes the two Belvederes collectively to Hildebrandt and does not distinguish the buildings or construction phases in this passage. The attribution remains for S6 relation review.",
        "relations": ["st-chp7-p201-v-belvederes-by-hildebrandt"],
        "endpoints": {"st-chp7-p201-v-belvederes-by-hildebrandt": ("cand-7307", "cand-1299", "buildings_attributed_to_architect")},
        "external": {"source": "MAK Collection Online", "id": "https://sammlung.mak.at/en/artist/hildebrandt-johann-lucas-von_30775", "label": "Johann Lucas von Hildebrandt", "url": "https://sammlung.mak.at/en/artist/hildebrandt-johann-lucas-von_30775", "scope": "身份消歧；人物规范名为Johann Lucas von Hildebrandt。"},
    },
    {
        "primary": "cand-1300", "entry": "H.csv#16", "index_name": "Hill, Samuel",
        "canonical_name": "Hill, Samuel", "pages": "290n, 304n",
        "group": "new-person:hill-samuel-3c347d356a", "ku": "units/persons/samuel-hill",
        "name_zh": "塞缪尔·希尔", "name_en": "Samuel Hill",
        "name_rows": [("索引名", "Hill, Samuel", "S1（索引H.csv#16）"), ("正文姓名形式", "Samuel Hill", "S2（第10章pp.290、304注）")],
        "sources": [
            source("第10章注5；印刷页290", "Haskell引Joseph Smith于1729年11月26日致Samuel Hill的信；刊录材料由Chaloner发表，未独立查阅。", "letter from Joseph Smith to Samuel Hill of 26 November 1729", "02-sources/02-Markdown/10_CHP-10_intro.md", "line 549; print p.290 n.5"),
            source("第10章注2；印刷页304", "Haskell称Smith于1729年11月把Piazzetta作品送给Samuel Hill；所引Chaloner材料未独立查阅。", "Smith sent works by Piazzetta to Samuel Hill in November 1729", "02-sources/02-Markdown/10_CHP-10_intro.md", "line 606; print p.304 n.2"),
            source("第10章注5；印刷页304", "Haskell引Smith于1730年7月17日致Samuel Hill的信；刊录材料由Chaloner发表，未独立查阅。", "Letter from Smith to Samuel Hill of 17 July 1730", "02-sources/02-Markdown/10_CHP-10_intro.md", "line 609; print p.304 n.5"),
        ],
        "zh": "本卡登记索引H.csv#16所列Samuel Hill。第10章pp.290、304的三处注释将该姓名用于Smith信件及其送给Hill的Piazzetta作品叙述；Chaloner刊录未独立查阅。",
        "en": "This card registers Samuel Hill under index H.csv#16. Three notes in chapter 10, pp.290 and 304, use the name in connection with Smith’s letters and Piazzetta works sent to Hill; the cited Chaloner publication was not independently consulted.",
        "context_zh": "第10章注2称Smith于1729年11月将Piazzetta作品送给Hill；其他两注引用Smith致Hill的信。S2关系候选保留其转引和未独立查阅限定。",
        "context_en": "Chapter 10, note 2, says Smith sent Piazzetta works to Hill in November 1729; two other notes cite letters from Smith to Hill. The S2 candidate retains the nested citation and non-consultation qualification.",
        "relations": ["st-chp10-p304-note2-piazzetta-works-to-hill"],
        "endpoints": {"st-chp10-p304-note2-piazzetta-works-to-hill": ("cand-2440", "cand-1300", "sent_work_group_to_person")},
        "external": None,
    },
    {
        "primary": "cand-1301", "entry": "H.csv#17", "index_name": "Hogarth, William",
        "canonical_name": "Hogarth, William", "pages": "279",
        "group": "new-person:hogarth-william-51254bc070", "ku": "units/persons/william-hogarth",
        "name_zh": "威廉·霍加斯", "name_en": "William Hogarth",
        "name_rows": [("索引名", "Hogarth, William", "S1（索引H.csv#17）"), ("正文姓名形式", "Hogarth", "S2（第10章p.279）")],
        "sources": [source("第10章导论；印刷页279", "Haskell称Marco Ricci的一些半讽刺音乐群像必定令Hogarth着迷。", "must certainly have fascinated Hogarth", "02-sources/02-Markdown/10_CHP-10_intro.md", "line 48; print p.279")],
        "zh": "本卡登记索引H.csv#17所列William Hogarth。第10章p.279称Marco Ricci的一些音乐群像必定令Hogarth着迷；这是Haskell的推断。",
        "en": "This card registers William Hogarth under index H.csv#17. Chapter 10, p.279, says some of Marco Ricci’s musical groups must have fascinated Hogarth; this remains Haskell’s inference.",
        "context_zh": "该段把Hogarth放在Marco Ricci音乐群像的接受语境中，不据此建立影响或师承关系。",
        "context_en": "The passage places Hogarth in the reception context of Marco Ricci’s musical groups; no influence or teaching relation is inferred.",
        "relations": [], "endpoints": {}, "external": None,
    },
    {
        "primary": "cand-1302", "entry": "H.csv#18", "index_name": "Honthorst, Gerrit van",
        "canonical_name": "Honthorst, Gerrit van", "pages": "95",
        "group": "new-person:gerrit-honthorst-van-1acc9537ec", "ku": "units/persons/gerrit-van-honthorst",
        "name_zh": "赫里特·范·洪特霍斯特", "name_en": "Gerrit van Honthorst",
        "name_rows": [("索引名", "Honthorst, Gerrit van", "S1（索引H.csv#18）"), ("正文姓名形式", "Honthorst", "S2（第4章p.95）")],
        "sources": [source("第4章第I节；印刷页95", "Haskell转述Giustiniani的观点，将Honthorst列入直接使用模特作画者之中。", "Honthorst, Ribera, the Flemish above all", "02-sources/02-Markdown/04_CHP-4_sec_i.md", "line 8; print p.95")],
        "zh": "本卡登记索引H.csv#18所列Gerrit van Honthorst。第4章p.95在Giustiniani对绘画方法的比较中以姓氏提到他。",
        "en": "This card registers Gerrit van Honthorst under index H.csv#18. Chapter 4, p.95, names him by surname in Giustiniani’s comparison of painting methods.",
        "context_zh": "Haskell转述Giustiniani把Honthorst列入直接利用模特作画的画家；此处不作为该方法关系的独立证实。",
        "context_en": "Haskell reports that Giustiniani listed Honthorst among painters who used models directly; the passage is not independent verification of the method claim.",
        "relations": [], "endpoints": {}, "external": None,
    },
    {
        "primary": "cand-1303", "entry": "H.csv#19", "index_name": "Horace",
        "canonical_name": "Horace", "pages": "360",
        "group": "new-person:horace-roman-poet-20261018", "ku": "units/persons/horace",
        "name_zh": "贺拉斯", "name_en": "Horace",
        "name_rows": [("索引名", "Horace", "S1（索引H.csv#19）"), ("正文姓名形式", "Horace", "S2（第13章p.333；第14章p.360）")],
        "sources": [source("第14章导论；印刷页360", "Haskell称Algarotti墓志铭采用Horace的Non omnis moriar一语；原书OCR中的mortar已按纸本校为moriar。", "the proud adaptation of Horace’s Non omnis mortar", "02-sources/02-Markdown/14_CHP-14_intro.md", "line 146; print p.360")],
        "zh": "本卡登记索引H.csv#19所列Horace，即第13章p.333和第14章p.360语境中的罗马诗人；与Horace Walpole人物KU保持分立。",
        "en": "This card registers Horace under index H.csv#19 as the Roman poet named in chapters 13, p.333, and 14, p.360; he remains distinct from the Horace Walpole KU.",
        "context_zh": "第14章称Algarotti墓志铭改写Horace的Non omnis moriar；原文是Haskell对铭文的报告，OCR校正记录保留在S2过程。",
        "context_en": "Chapter 14 says Algarotti’s memorial inscription adapts Horace’s Non omnis moriar; this is Haskell’s report of the inscription, and the OCR correction remains documented in the S2 process record.",
        "relations": ["st-chp14-p360-inscription-adapts-horace"],
        "endpoints": {"st-chp14-p360-inscription-adapts-horace": ("cand-11523", "cand-1303", "memorial_inscription_adapted_from_horace")},
        "external": None,
    },
]

for target in TARGETS:
    target["card"] = f"04-knowledge/{target['ku']}.md"


def make_card(target: dict) -> str:
    index_file = target["entry"].split("#", 1)[0]
    index_pages = target["pages"]
    index_summary = (
        f"索引以“{target['index_name']}”列出此人并定位至第{index_pages}页。"
        if index_pages else f"索引以“{target['index_name']}”列出此人，但该项未列页码。"
    )
    sources = [{
        "citation": INDEX_CITATION, "location": f"全书索引 {target['entry']}",
        "sentence_summary": index_summary,
        "original_quotes": [{"source_span": target["entry"], "text": target["index_name"]}],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": f"02-sources/03-Index/03-2-Index-CSV/{index_file}", "source_span": target["entry"]},
    }]
    for item in target["sources"]:
        sources.append({
            "citation": HASKELL_CITATION, "location": item["location"], "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": item["span"], "text": item["quote"]}],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": item["file"], "source_span": item["span"]},
        })
    fm = yaml.safe_dump({
        "title": f"{target['name_zh']}（{target['name_en']}）", "name_en": target["name_en"], "type": "person",
        "evidence_status": "source_backed", "sources": sources, "created": DATE, "updated": DATE, "process_ref": PROCESS_REF,
    }, allow_unicode=True, sort_keys=False, width=1000).rstrip()
    name_rows = "\n".join(f"| {field} | {value} | {evidence} |" for field, value, evidence in target["name_rows"])
    external = target.get("external")
    if external:
        external_links = (
            "| 身份记录 | 标识／链接 | 状态与范围 |\n|---|---|---|\n"
            f"| {external['source']} | [{external.get('label', external['id'])}]({external['url']}) | {external['scope']} |\n"
        )
    else:
        external_links = "本批未在卡内添加外部身份链接；书内名称依据见上表及索引/正文来源。\n"
    relations = ", ".join(target["relations"])
    if target["relations"]:
        relation_context_zh = f"直接S2关系候选{relations}仍待S6逐条裁决；本次登记不建立正式边。"
        relation_context_en = f"Direct S2 relation candidates {relations} remain for individual S6 review; this registration creates no formal edges."
        relation_display = f"直接S2候选（待S6）：{relations}。"
    else:
        relation_context_zh = "S2当前未将此人物映射为直接关系候选端点；本次不登记正式关系。"
        relation_context_en = "S2 does not currently map this person as a direct relation-candidate endpoint; no formal relation is registered here."
        relation_display = "当前未有直接S2关系候选映射到此人物端点。"
    if target.get("mention_note"):
        relation_display += f" {target['mention_note']}"
    return (
        f"---\n{fm}\n---\n\n## 内容\n\n### 描述\n\n**中文：** {target['zh']}\n\n**English:** {target['en']}\n\n"
        f"### 名称\n\n| 字段 | 值 | 证据 |\n|---|---|---|\n{name_rows}\n\n"
        f"### 本书语境\n\n**中文：** {target['context_zh']} {relation_context_zh}\n\n"
        f"**English:** {target['context_en']} {relation_context_en}\n\n"
        "## 关系与证据\n\n### 身份与外部链接\n\n"
        f"{external_links}\n### 关系记录\n\n当前没有正式关系。正文中的导航与线索不自动形成关系边。\n\n"
        f"**中文：** {relation_display}\n\n**English:** {relation_display}\n"
    )


def extract_card_fields(cards: dict[str, str]) -> tuple[list[dict], int]:
    from scripts import build_field_facts
    from scripts.build_field_facts import extract_records
    with tempfile.TemporaryDirectory(prefix="pnp-s4-h-person-endpoints-") as temp_root:
        temp_base = Path(temp_root)
        rows = []
        for target in TARGETS:
            card = temp_base / target["card"]
            card.parent.mkdir(parents=True, exist_ok=True)
            card.write_text(cards[target["card"]], encoding="utf-8")
            rows.append({"ku_id": target["ku"], "card_path": target["card"]})
        previous_base = build_field_facts.BASE
        build_field_facts.BASE = temp_base
        try:
            additions, _registry, warnings, cards_with_tables = extract_records(rows)
            assert not warnings, warnings
            return additions, cards_with_tables
        finally:
            build_field_facts.BASE = previous_base


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False) as handle:
        tmp = Path(handle.name)
        handle.write(content)
    try:
        tmp.replace(path)
    finally:
        if tmp.exists():
            tmp.unlink()


def with_bom(text: str, original: bytes | None = None) -> bytes:
    raw = text.encode("utf-8")
    return b"\xef\xbb\xbf" + raw if original is None or original.startswith(b"\xef\xbb\xbf") else raw


def main() -> int:
    parser = argparse.ArgumentParser(description="Register thirteen H-section S3 new person groups and map their external identity rows.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    base = helper.base
    sync = base.sync
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    _, candidates = sync.read_csv(ENTITY)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    main_alignment_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    accepted_lines = ACCEPTED.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statements}
    cards = {target["card"]: make_card(target) for target in TARGETS}
    card_paths = {target["card"]: ROOT / target["card"] for target in TARGETS}

    for target in TARGETS:
        candidate, alignment = candidate_by_id[target["primary"]], main_alignment_by_id[target["primary"]]
        assert candidate.get("suggested_type") == "person" and alignment.get("decision") == "new"
        assert candidate.get("canonical_name") == target["canonical_name"]
        assert candidate.get("index_entry_id") == target["entry"] and candidate.get("index_page_range") == target["pages"]
        assert base.sync.get_group(alignment.get("resolution_note", "")) == target["group"]
        if alignment.get("ku_id"):
            assert alignment.get("ku_id") == target["ku"]
        else:
            assert target["ku"] not in manifest_by_ku
            assert target["card"] not in accepted_paths and not card_paths[target["card"]].exists()
        group_members = [
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
            and base.sync.get_group(row.get("resolution_note", "")) == target["group"]
        ]
        assert group_members == [target["primary"]], (target["group"], group_members)
        index_file, index_id = target["entry"].split("#", 1)
        index_lines = (ROOT / "02-sources/03-Index/03-2-Index-CSV" / index_file).read_text(encoding="utf-8-sig").splitlines()
        index_row = next(csv.reader([index_lines[int(index_id) + 1]]))
        assert index_row[0] == target["index_name"] and target["pages"] in index_row[-1]
        direct = {
            row["statement_id"] for row in statements
            if (row.get("qualifiers") or {}).get("relation_candidate") is True
            and (row.get("subject_candidate_id") == target["primary"] or row.get("object_candidate_id") == target["primary"])
        }
        assert direct == set(target["endpoints"]), (target["primary"], sorted(direct), sorted(target["endpoints"]))
        for statement_id, expected in target["endpoints"].items():
            row = statement_by_id[statement_id]
            assert (row.get("subject_candidate_id"), row.get("object_candidate_id"), row.get("predicate")) == expected
        for item in target["sources"]:
            text = (ROOT / item["file"]).read_text(encoding="utf-8-sig")
            assert re.sub(r"\s+", " ", item["quote"]) in re.sub(r"\s+", " ", text), (target["primary"], item["span"])
        external_rows = [row for row in alignments if row.get("candidate_id") == target["primary"] and row.get("external_source")]
        if target.get("external"):
            assert len(external_rows) == 1
            assert external_rows[0].get("external_id") in {
                target["external"]["id"], target["external"].get("alignment_id", ""),
                target["external"].get("url", ""),
            }
            assert external_rows[0].get("decision") == "new"
            if alignment.get("ku_id"):
                assert external_rows[0].get("ku_id") == target["ku"]
        else:
            assert not external_rows

    pending = [target for target in TARGETS if not main_alignment_by_id[target["primary"]].get("ku_id")]
    if not pending:
        for target in TARGETS:
            assert main_alignment_by_id[target["primary"]].get("ku_id") == target["ku"]
            assert card_paths[target["card"]].read_text(encoding="utf-8-sig") == cards[target["card"]]
            assert target["card"] in accepted_paths and manifest_by_ku[target["ku"]].get("card_path") == target["card"]
        print("ALREADY REGISTERED: all thirteen H-section person groups and their external identity rows are present.")
        return 0
    assert len(pending) == len(TARGETS), "partial S4 state needs explicit reconciliation before this batch can continue"

    before_stats = sync.summarize_by_type(candidates, alignments)
    planned_alignments = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    planned_accepted = list(accepted_lines)
    for target in TARGETS:
        row = next(item for item in planned_alignments if item.get("candidate_id") == target["primary"] and not item.get("external_source"))
        row["ku_id"] = target["ku"]
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] += (
            f" S4 registration ({DATE}): group {target['group']} -> {target['ku']}; "
            "source-backed person registration only; direct S2 relation candidates remain for S6."
        )
        planned_manifest.append({"ku_id": target["ku"], "type": "person", "canonical_name": target["name_zh"], "name_en": target["name_en"], "source_task": TASK, "card_path": target["card"]})
        planned_accepted = base.insert_accepted(planned_accepted, target["card"])
        if target.get("external"):
            external_row = next(item for item in planned_alignments if item.get("candidate_id") == target["primary"] and item.get("external_source"))
            external_row["ku_id"] = target["ku"]
            external_row["process_ref"] = PROCESS_REF
            external_row["resolution_note"] += f" S4 registration maps this authority identity row to {target['ku']} under {target['group']}."
    planned_manifest.sort(key=lambda row: row["ku_id"])
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {key: sum(row[key] for row in before_stats.values()) for key in next(iter(before_stats.values()))}
    count = len(TARGETS)
    assert totals["registered_groups"] == before_totals["registered_groups"] + count
    assert totals["registered_members"] == before_totals["registered_members"] + count
    assert totals["pending_groups"] == before_totals["pending_groups"] - count
    assert totals["pending_members"] == before_totals["pending_members"] - count
    assert len(planned_manifest) == len(manifest) + count

    additions, cards_with_tables = extract_card_fields(cards)
    expected_name_fields = sum(len(target["name_rows"]) for target in TARGETS)
    external_count = sum(1 for target in TARGETS if target.get("external"))
    assert cards_with_tables == count and len(additions) == expected_name_fields + external_count
    assert sum(row.get("evidence_status") == "source_backed" for row in additions) == expected_name_fields
    assert sum(row.get("evidence_status") == "unverified" for row in additions) == external_count
    assert all(row.get("evidence_status") in {"source_backed", "unverified"} for row in additions)
    enrichment_text = ENRICHMENT.read_text(encoding="utf-8-sig")
    existing_enrichment = [json.loads(line) for line in enrichment_text.splitlines() if line.strip()]
    natural_keys = {(row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id", "")) for row in existing_enrichment}
    existing_ids = {row.get("enrichment_id", "") for row in existing_enrichment}
    max_id = max((int(match.group(1)) for value in existing_ids if (match := re.fullmatch(r"enr-(\d+)", value))), default=0)
    for number, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_id + number:05d}"
        assert (row["ku_id"], row["field"], row["value"], row.get("source_id", "")) not in natural_keys
        assert row["enrichment_id"] not in existing_ids
    planned_enrichment = enrichment_text.rstrip("\n") + "\n" + "\n".join(json.dumps(row, ensure_ascii=False) for row in additions) + "\n"

    process_text = helper.base.process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物登记：H段跨章身份组（{DATE}）\n\n"
    for target in TARGETS:
        rel = ",".join(target["relations"]) if target["relations"] else "无直接S2关系候选"
        identity = f"；外部身份入口：{target['external']['source']}（{target['external']['id']}）" if target.get("external") else ""
        process_text += (
            f"- {target['primary']}（{target['group']}）→ [{target['name_zh']}（{target['name_en']}）]"
            f"(../../../04-knowledge/{target['ku']}.md)。索引{target['entry']}与所列章节页段构成书内身份依据{identity}；"
            f"直接S2关系候选：{rel}；关系均留待S6。无正式关系写入。\n"
        )
    relation_count = sum(len(target["relations"]) for target in TARGETS)
    process_text += (
        f"\n本批登记{count}个S3 new人物组、{count}条候选映射和{expected_name_fields}条source_backed名称字段；"
        f"另保留{external_count}条外部身份导航行；对应稳定标识仅在alignment.csv，未写入enrichment.jsonl；"
        f"{relation_count}条直接S2关系候选留待S6，{external_count}条外部身份记录映射至相应KU。"
        "cand-9220作品候选继续独立待证；本批未新增正式关系或扩大S2断言。\n\n"
        f"登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、"
        f"{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物登记：H段跨章身份组（{DATE}）\n\n"
        "登记Juan van der Hamen、George Frederick Handel、Aloys Thomas Raimund Harrach、Theodor Helmbreker、Henri III、Henrietta Maria、Sir Robert Hervey、John Hervey, 2nd Baron Hervey、Johann Lucas von Hildebrandt、Samuel Hill、William Hogarth、Gerrit van Honthorst与Horace共13个人物组。"
        f"九条直接S2关系候选仍待S6；四条外部身份行映射到相应KU。Canaletto为Sir Robert Hervey绘制的二十幅景观候选cand-9220保持独立待证；本批未新增正式关系。"
        f"KU={len(planned_manifest)}，名称字段={expected_name_fields}，外部身份导航行={external_count}。详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    with tempfile.TemporaryDirectory(prefix="pnp-s4-h-person-endpoints-") as temp_name:
        temp_dir = Path(temp_name)
        alignment_stage, manifest_stage = temp_dir / "alignment.csv", temp_dir / "ku-manifest.csv"
        sync.write_csv(alignment_stage, alignment_fields, planned_alignments)
        sync.write_csv(manifest_stage, manifest_fields, planned_manifest)
        writes = {
            ALIGNMENT: alignment_stage.read_bytes(), MANIFEST: manifest_stage.read_bytes(),
            ENRICHMENT: with_bom(planned_enrichment, ENRICHMENT.read_bytes()),
            ACCEPTED: with_bom("\n".join(planned_accepted) + "\n", ACCEPTED.read_bytes()),
            PROCESS: with_bom(process_text + "\n", PROCESS.read_bytes()),
            RESULT: with_bom(result_text + "\n", RESULT.read_bytes()),
        }
        for target in TARGETS:
            writes[ROOT / target["card"]] = with_bom(cards[target["card"]])

    if args.dry_run:
        print(f"S4 dry-run passed: groups={count}; candidate_mappings={count}; name_fields={expected_name_fields}; external_identity_navigation_rows={external_count}; direct_relation_candidates={relation_count}; external_identity_alignment_rows={external_count}.")
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
    print(f"applied: groups={count}; candidate_mappings={count}; name_fields={expected_name_fields}; external_identity_navigation_rows={external_count}; relation_candidates={relation_count}; external_identity_alignment_rows={external_count}; KU={len(planned_manifest)}; formal_relations_added=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
