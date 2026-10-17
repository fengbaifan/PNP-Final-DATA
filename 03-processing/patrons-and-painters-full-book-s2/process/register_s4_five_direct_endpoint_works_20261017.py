from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import register_s4_valmarana_cluster_batch_20261015 as card_writer


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
PROCESS_ANCHOR = "s4-five-direct-endpoint-works-20261017"


RECORDS = [
    {
        "candidate_id": "cand-6676",
        "group": "workgrp-b1a186cf103e3c",
        "ku_id": "units/works/henri-iv-equestrian-statue-marie-de-medici-commission",
        "card_path": "04-knowledge/units/works/henri-iv-equestrian-statue-marie-de-medici-commission.md",
        "title_zh": "马里·德·美第奇推动委托的亨利四世骑马像",
        "name_en": "Equestrian Statue of Henri IV Commissioned at Marie de Medici’s Urging",
        "description_zh": (
            "本卡对应哈斯克尔第7章所述亨利四世骑马纪念像。作者称 Marie de Medici 于1604年说服叔父斐迪南大公委托 Giambologna 制作该像，计划安置在 Pont Neuf；纪念像后来由 Pietro Tacca 与 Francavilla 完成，约十年后才运抵。书下注称该纪念像于1792年被毁。"
            "这些时间与制作细节均按哈斯克尔的书内记述保存。"
        ),
        "description_en": (
            "This card represents the equestrian monument of Henri IV discussed in Chapter 7. Haskell says that in 1604 Marie de Medici persuaded her uncle, Grand Duke Ferdinando, to commission Giambologna to make it for the Pont Neuf; the monument was later completed by Pietro Tacca and Francavilla and arrived about ten years later. A note says it was destroyed in 1792. "
            "These dates and production details are retained as Haskell’s account."
        ),
        "scope": (
            "**作品身份与范围：** 原书以 Henri IV、Giambologna、Marie 的委托及预定安置地点识别这件骑马纪念像；后续制作参与者和抵达时间由同段补充。作品现状只记书下注明的毁坏年份。"
        ),
        "boundary": (
            "**身份边界：** 本卡对应为 Henri IV 制作的纪念像。叙述同时提到 Marie 曾请求斐迪南将为自己制作的骑马像转交给她，该请求未获准；该自用骑马像与本卡对象分别处理。Pont Neuf 是原文所述的计划安置地，不据此补写安装史或后续流传。"
        ),
        "locator": "第7章 p.174 及注2。",
        "sources": [
            {"chapter": "7", "page": "174", "file": "07_CHP-7_sec_i.md", "lines": "50–52", "quote": "She persuaded her uncle the Grand Duke to commission an equestrian statue of Henri", "summary": "第7章称 Marie 于1604年说服叔父斐迪南大公委托制作 Henri IV 骑马像；原句续行列出 Giambologna。"},
            {"chapter": "7", "page": "174", "file": "07_CHP-7_sec_i.md", "lines": "54", "quote": "the monument, which was completed by Pietro Tacca and Francavilla, did not arrive for another ten years", "summary": "哈斯克尔记载该纪念像的完成者及其延迟约十年抵达；不扩写为安装或流传史。"},
            {"chapter": "7", "page": "174", "file": "07_CHP-7_sec_i.md", "lines": "310", "quote": "The monument was destroyed in 1792.", "summary": "书下注称纪念像于1792年被毁；该信息按 Haskell 引用的注释来源记录。"},
        ],
        "relations": [
            "st-chp7-p174-i12", "st-chp7-p174-i13", "st-chp7-p174-i16",
            "st-chp7-p174-i17", "st-chp7-p174-i18", "st-chp7-p174-n2-monument-destroyed",
        ],
        "external_note": "本次依据本书正文及其注释登记作品身份；未新增外部作品目录或现状核验。",
    },
    {
        "candidate_id": "cand-10554",
        "group": "workgrp-a758d643d80f43",
        "ku_id": "units/works/alticchiero-garden-shrines-sculpture-programme",
        "card_path": "04-knowledge/units/works/alticchiero-garden-shrines-sculpture-programme.md",
        "title_zh": "阿尔蒂奇耶罗园林的神龛与雕塑配置",
        "name_en": "Shrines and Sculpture Programme in the Alticchiero Garden",
        "description_zh": (
            "本卡记录哈斯克尔对 Angelo Querini 在阿尔蒂奇耶罗园林中安排的一组神龛与雕塑的描述。作者将园林的主要构想概括为哲学家生活方式的寓意，并提及友谊祭坛、古代雕塑及现代仿作，以及宁静、田园生活、幸运和阿波罗等主题。"
            "这是一组分布于园林中的装饰配置，卡片不为未具名雕塑补造名称。"
        ),
        "description_en": (
            "This card records Haskell’s account of a group of shrines and sculptures arranged by Angelo Querini in the Alticchiero garden. The author describes the garden’s main conception as an allegory of the philosopher’s way of life and mentions the Altar of Friendship, ancient sculpture and modern imitations, and themes such as Tranquillity, Country Life, Fortune, and Apollo. "
            "This is a distributed decorative programme; the card supplies no names for unspecified sculptures."
        ),
        "scope": (
            "**作品范围：** 第15章 p.370 将园林中的神龛和雕塑作为一组设计安排叙述，并以友谊祭坛及其他祭坛举例；后续页另谈花园中具名纪念像、浮雕和收藏品。"
        ),
        "boundary": (
            "**对象边界：** 本卡记录园林中的群组性装饰配置，不是阿尔蒂奇耶罗庄园本身，也不是一件单独雕塑或完整馆藏清单。原文分别具名的祭坛、雕塑和纪念像仍可由各自候选承接；群组与园林地点、单件作品之间的正式关系留待 S6。"
        ),
        "locator": "第15章 p.370。",
        "sources": [
            {"chapter": "15", "page": "370", "file": "15_CHP-15_sec_ii.md", "lines": "64", "quote": "a number of shrines and carefully chosen pieces of antique and modern sculpture distributed in the grounds", "summary": "哈斯克尔以复数神龛和古今雕塑概括散布在园林中的设计安排。"},
            {"chapter": "15", "page": "370", "file": "15_CHP-15_sec_ii.md", "lines": "65–66", "quote": "Other altars, formed of real antique sculpture or of modern imitations", "summary": "作者说明其他祭坛使用古代雕塑或现代仿作，并列举宁静、田园生活、幸运和阿波罗等主题。"},
        ],
        "relations": [
            "st-chp15-p370-other-altars-material", "st-chp15-p370-garden-sculpture-programme-located-in-grounds",
            "st-chp15-p370-altar-ideal-tranquillity", "st-chp15-p370-altar-ideal-country-life",
            "st-chp15-p370-altar-ideal-fortune", "st-chp15-p370-altar-ideal-apollo",
        ],
        "external_note": "本次只登记书内明确描述的园林装饰配置；未作外部场地或雕塑对象比对。",
    },
    {
        "candidate_id": "cand-5272",
        "group": "workgrp-5ea1e2fb75fd5a",
        "ku_id": "units/works/gaulli-gesu-nave-fresco",
        "card_path": "04-knowledge/units/works/gaulli-gesu-nave-fresco.md",
        "title_zh": "盖乌利耶稣堂中殿壁画",
        "name_en": "Gaulli’s Nave Fresco at the Gesù",
        "description_zh": (
            "本卡对应哈斯克尔第3章称为耶稣堂最醒目特征的 Gaulli 中殿壁画。作者说该壁画原本只是祭坛区高潮的前奏，并将其图像构想置于耶稣会宣教信息的语境中；由于中殿拱顶比穹顶更便于公众观看，叙述强调其象征表达较为直接。"
            "原书此处未给该壁画正式作品名，本卡使用描述性题名。"
        ),
        "description_en": (
            "This card represents the Gaulli fresco in the nave that Haskell calls the most striking feature of the Gesù. The author says it was originally intended as a prelude to the climax in the tribune and places its imagery in the context of the Jesuits’ missionary message; because the nave vault was more accessible to the public than the dome, the passage stresses a more direct symbolism. "
            "The text does not supply a formal title here, so the card uses a descriptive title."
        ),
        "scope": (
            "**作品身份与范围：** 仅指第3章 p.83 所述的耶稣堂中殿单幅壁画及该段直接讨论的构图与观看语境；不把全教堂装饰或其他拱顶、祭坛区作品收并进来。"
        ),
        "boundary": (
            "**与既有项目卡的关系：** 既有[Gaulli 耶稣堂拱顶壁画工程卡](gaulli-gesu-vaults.md)记录中殿及横翼拱顶工程整体；本卡限定为第3章 p.83 所指的中殿单幅壁画。它与该较广工程、穹顶及祭坛区方案的组成关系留待 S6 逐条裁决，本次不建立正式 `part_of` 边。"
        ),
        "locator": "第3章 p.83。",
        "sources": [
            {"chapter": "3", "page": "83", "file": "03_CHP-3_sec_iv.md", "lines": "71–72", "quote": "Gaulli’s fresco in the nave", "summary": "哈斯克尔识别耶稣堂中殿的 Gaulli 壁画，并称其为教堂最醒目的特征。"},
            {"chapter": "3", "page": "83", "file": "03_CHP-3_sec_iv.md", "lines": "72", "quote": "a prelude to the climax of the tribune", "summary": "第3章说明中殿壁画最初被设想为祭坛区高潮的前奏；此为书内方案表述。"},
            {"chapter": "3", "page": "83", "file": "03_CHP-3_sec_iv.md", "lines": "72", "quote": "the vault was much more accessible to the general public than the dome", "summary": "作者以观看可及性解释中殿拱顶象征表达的简化。"},
        ],
        "relations": [
            "st-chp3-seciv-l69-73-central-iconographic-groups", "st-chp3-seciv-l69-73-ihs-radiance",
            "st-chp3-seciv-l69-73-light-strikes-damned-and-heretics", "st-chp3-seciv-l69-73-nave-fresco-prominent",
            "st-chp3-seciv-l69-73-prelude-to-tribune", "st-chp3-seciv-l69-73-vault-public-access-simpler-symbolism",
        ],
        "external_note": "本次没有为该壁画补入外部正式题名或作品目录身份；身份卡范围依哈斯克尔的描述限定。",
    },
    {
        "candidate_id": "cand-10013",
        "group": "workgrp-48c8f5fcc77fe0",
        "ku_id": "units/works/novelli-goldoni-pasquali-illustration-programme",
        "card_path": "04-knowledge/units/works/novelli-goldoni-pasquali-illustration-programme.md",
        "title_zh": "诺韦利为帕斯夸利版戈尔多尼作品所作插图系列",
        "name_en": "Novelli’s Illustration Programme for Pasquali’s Goldoni Edition",
        "description_zh": (
            "本卡记录哈斯克尔第13章关于 Pietro Antonio Novelli 为 Pasquali 出版的 Goldoni 作品设计的一组插图：原书称需要一百多幅图稿，由不同版画家复制；卷首图表现 Goldoni 生平片段，剧作插图则延续其亲密、面向公众的呈现方式。"
            "本卡登记整组插图方案，不逐件命名未识别图稿。"
        ),
        "description_en": (
            "This card records Haskell’s account in Chapter 13 of a body of illustrations Pietro Antonio Novelli designed for Pasquali’s edition of Goldoni’s works. The text says more than one hundred drawings were needed and that various engravers reproduced them; frontispieces depicted episodes from Goldoni’s life, while the play illustrations extended the undertaking’s intimate address to readers. "
            "The card records the programme as a group and does not name unidentified individual designs."
        ),
        "scope": (
            "**作品范围：** 第13章 p.338 同时讨论 Goldoni 生平题材的各卷卷首图和 Novelli 为剧作设计的插图版画；出版者、设计者、图稿数量及复制方式均按 Haskell 的叙述限定。"
        ),
        "boundary": (
            "**与单件作品的区别：** 已有[第二卷卷首图卡](pietro-antonio-novelli-frontispiece-to-vol-2-of-goldoni-opere.md)对应图版57b这一件具体图像；本卡对应逾百幅图稿及其系列方案，二者保持不同对象粒度。未逐一确认的卷首图、版画家和作品成员不补入名单；系列与第二卷单幅图之间的正式组成关系留待 S6。"
        ),
        "locator": "第13章 p.338。",
        "sources": [
            {"chapter": "13", "page": "338", "file": "13_CHP-13_intro.md", "lines": "63", "quote": "Over a hundred drawings were required and these were reproduced by various engravers.", "summary": "哈斯克尔称该出版方案需要一百多幅图稿，并由不同版画家复制。"},
            {"chapter": "13", "page": "338", "file": "13_CHP-13_intro.md", "lines": "64", "quote": "the frontispiece to each volume should represent a scene from his own life", "summary": "Goldoni 对该版插图方案的解释称，每卷卷首图拟表现其本人生活场景；这是书中转述的作者声明。"},
            {"chapter": "13", "page": "338", "file": "13_CHP-13_intro.md", "lines": "65", "quote": "the plates that Novelli designed to illustrate the plays themselves", "summary": "哈斯克尔将 Novelli 为剧作设计的插图版画与各卷卷首图并列讨论。"},
        ],
        "relations": [
            "st-chp13-p338-goldoni-biographical-episodes-in-illustrations",
            "st-chp13-p338-goldoni-proposed-life-scenes-on-frontispieces",
            "st-chp13-p338-haskell-longhi-comparison-and-vivid-period-impression",
            "st-chp13-p338-illustrated-intimacy-affected-play-plates",
            "st-chp13-p338-novelli-over-hundred-drawings-reproduced",
            "st-chp13-p338-novelli-scenes-depict-venetian-professional-world",
        ],
        "external_note": "本次仅依据本书章节叙述登记插图系列；未新增外部版本核验或成员清单。",
    },
    {
        "candidate_id": "cand-10586",
        "group": "workgrp-32819d9dcd5818",
        "ku_id": "units/works/canova-bust-paolo-renier-querini-commission",
        "card_path": "04-knowledge/units/works/canova-bust-paolo-renier-querini-commission.md",
        "title_zh": "奎里尼委托卡诺瓦制作的保罗·雷尼耶胸像",
        "name_en": "Bust of Paolo Renier Commissioned by Angelo Querini from Canova",
        "description_zh": (
            "本卡对应哈斯克尔所述 Angelo Querini 委托 Antonio Canova 为其友人 Paolo Renier 制作的胸像。作者称 Renier 于1779年成为总督后，后来与自己曾反对的势力妥协，Querini 因失望而把胸像砸向园中复仇女神祭坛。书下注又转述一件可能为此胸像的陶土像据称存于帕多瓦市立博物馆，并提到其后续用途的传闻；这些识别与保管说法在本项目中未核实。"
        ),
        "description_en": (
            "This card represents the bust Angelo Querini commissioned from Antonio Canova of his friend Paolo Renier. Haskell says that after Renier became Doge in 1779 and later compromised with forces he had once opposed, Querini, disappointed, flung the bust against the Altar of Furies in his garden. A note then reports that a terracotta bust thought to be this object was said to survive in the Museo Civico at Padua and mentions a story about its later use; these identifications and custody claims remain unverified in this project."
        ),
        "scope": (
            "**作品身份与范围：** 第15章 pp.371–372 将胸像的委托人、创作者、被表现者及 Querini 的失望行为联系起来；原书未提供可确认这件作品现存状态的独立目录记录。"
        ),
        "boundary": (
            "**待证内容：** p.372 注1以“what must be the bust”表述对帕多瓦陶土胸像的推定，并说曾有人提出它被置于仆役盥洗处。此处只作为 Haskell 转述的注释及未证身份线索保留，不把馆藏归属、作品保存状态或传闻当作已核事实；本次不建立作品现存地关系。"
        ),
        "locator": "第15章 pp.371–372，尤其 p.372 注1。",
        "sources": [
            {"chapter": "15", "page": "371", "file": "15_CHP-15_sec_ii.md", "lines": "83", "quote": "he had commissioned Canova to make him a bust of this friend", "summary": "哈斯克尔称 Querini 曾委托 Canova 制作其友人 Paolo Renier 的胸像。"},
            {"chapter": "15", "page": "372", "file": "15_CHP-15_sec_ii.md", "lines": "86", "quote": "Querini flung the bust in a rage of disappointment", "summary": "第15章称 Querini 后来因 Renier 的政治妥协而愤怒地把胸像砸向园中复仇女神祭坛。"},
            {"chapter": "15", "page": "372", "file": "15_CHP-15_sec_ii.md", "lines": "113", "quote": "what must be the bust (in terracotta) survives in the Museo Civico at Padua", "summary": "书下注引用1951年研究对一件陶土胸像作出推定性识别；本卡保留作者的限定语，不视作已核馆藏身份。"},
            {"chapter": "15", "page": "372", "file": "15_CHP-15_sec_ii.md", "lines": "113", "quote": "it has been suggested that Querini kept it in the servants’ lavatories", "summary": "注释将胸像后续用途明确作为传闻保留；本卡不把该说法记为事实。"},
        ],
        "relations": [
            "st-chp15-p371-querini-renier-canova-bust-commission-partial",
            "st-chp15-p372-querini-threw-renier-bust-at-furies-altar",
            "st-chp15-p372-note1-bust-at-museo-civico-padua",
            "st-chp15-p372-note1-suggested-servants-lavatories",
            "st-chp15-p371-renier-bust-commissioned-from-canova",
            "st-chp15-p371-renier-bust-portrayed-paolo-renier",
        ],
        "external_note": "本次未查验 Canova 作品目录或帕多瓦馆藏；脚注中的对象识别与保管说法仍待证。",
    },
]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def get_group(note: str):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"expected one {label} anchor; found {count}")
    return text.replace(old, new, 1)


def make_sources(record):
    rows = []
    for item in record["sources"]:
        rows.append({
            "citation": card_writer.BOOK_CITATION,
            "location": f"第{item['chapter']}章，印刷页{item['page']}；OCR L{item['lines']}",
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"lines {item['lines']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{item['file']}",
                "source_span": f"lines {item['lines']}; print p. {item['page']}",
            },
        })
    return rows


def make_card(record):
    frontmatter = {
        "title": f"{record['title_zh']}（{record['name_en']}）",
        "name_en": record["name_en"],
        "type": "work",
        "evidence_status": "source_backed",
        "sources": make_sources(record),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = card_writer.yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    relation_ids = "、".join(f"`{item}`" for item in record["relations"])
    body = f"""## 内容

### 描述

**中文：** {record['description_zh']}

**English:** {record['description_en']}

### 名称与身份边界

{record['scope']}

{record['boundary']}

**候选定位：** `{record['candidate_id']}`；S3 身份组 `{record['group']}`。{record['locator']}

## 关系与证据

### 关系记录

未建立正式关系。该候选有 {len(record['relations'])} 条 `relation_candidate=true` 的直接 S2 关系候选：{relation_ids}。这些候选均保留待 S6 逐条审查；本次只完成 S4 身份登记，没有写入 `relations.csv`。

### 身份与外部链接

{record['external_note']}
"""
    return f"---\n{fm}---\n\n{body}"


def count_groups(rows):
    groups = defaultdict(list)
    for row in rows:
        if row.get("decision") == "new" and not row.get("external_source"):
            group = get_group(row.get("resolution_note", ""))
            assert group, f"new decision lacks group: {row.get('candidate_id')}"
            groups[group].append(row)
    registered, pending = {}, {}
    for group, members in groups.items():
        mapped = [row for row in members if row.get("ku_id")]
        if mapped:
            assert len(mapped) == len(members) and len({row["ku_id"] for row in mapped}) == 1, group
            registered[group] = members
        else:
            pending[group] = members
    return groups, registered, pending


def update_process(text: str) -> str:
    text = replace_once(
        text,
        "| work | 2,397 | 234 | 482 / 497 | 5 | 29 | 1,632 | 41 / 46 | 441 / 451 |",
        "| work | 2,397 | 234 | 482 / 497 | 5 | 29 | 1,632 | 46 / 51 | 436 / 446 |",
        "process work S4 row",
    )
    text = replace_once(
        text,
        "| **合计** | **12,407** | **1,886** | **4,792 / 4,972** | **8** | **100** | **5,441** | **620 / 767** | **4,172 / 4,205** |",
        "| **合计** | **12,407** | **1,886** | **4,792 / 4,972** | **8** | **100** | **5,441** | **625 / 772** | **4,167 / 4,200** |",
        "process total S4 row",
    )
    if f'<a id="{PROCESS_ANCHOR}"></a>' in text:
        raise AssertionError(f"process anchor already exists: {PROCESS_ANCHOR}")
    bullets = []
    for record in RECORDS:
        bullets.append(
            f"- `{record['candidate_id']}`（`{record['group']}`）保持 S3 `new`，登记为[{record['title_zh']}作品卡](../../../{record['card_path']})（`{record['ku_id']}`）。"
            f"{record['boundary']} {len(record['relations'])} 条直接关系候选留待 S6。"
        )
    entry = f"""

<a id="{PROCESS_ANCHOR}"></a>

### S4 work：五组直接关系端点登记（2026-10-17）

本批登记五个已有 S3 `new` work 身份组；每组一个 KU，所有直接关系候选保持待 S6：

{chr(10).join(bullets)}

五组新增5个 work KU 与5条候选映射，合计30条直接 S2 关系候选仍待 S6；未新增正式关系、外部作品身份核验或 S5 enrichment。

S4累计登记625组/772条候选映射；待登记4,167组/4,200条；KU总数1,644。
"""
    return text.rstrip() + entry


def update_result(text: str) -> str:
    text = replace_once(text,
        "S4 已登记620组、映射767条成员候选；尚待登记4,172组、4,205条映射。",
        "S4 已登记625组、映射772条成员候选；尚待登记4,167组、4,200条映射。", "current S4 count")
    text = replace_once(text,
        "| [KU 登记](../tables/ku-manifest.csv) | 1,639 KU",
        "| [KU 登记](../tables/ku-manifest.csv) | 1,644 KU", "current manifest count")
    text = replace_once(text,
        "当前审计提示4,220条待登记 `decision=new` alignment 行，其中4,205条是4,172个未登记身份组的候选映射，另15条是外部身份记录。",
        "当前审计提示4,215条待登记 `decision=new` alignment 行，其中4,200条是4,167个未登记身份组的候选映射，另15条是外部身份记录。", "current strict-stage pending rows")
    text = replace_once(text,
        "| work | 234→218 | 497／482 | 41／441；451 | 5 | 29 | 1,632 |",
        "| work | 234→218 | 497／482 | 46／436；446 | 5 | 29 | 1,632 |", "result work S4 row")
    text = replace_once(text,
        "| **合计** | **1,886→1,040** | **4,972／4,792** | **620／4,172；4,205** | **8** | **100** | **5,441** |",
        "| **合计** | **1,886→1,040** | **4,972／4,792** | **625／4,167；4,200** | **8** | **100** | **5,441** |", "result total S4 row")
    text = replace_once(text,
        "2026-10-17 两批 term 登记见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-terms-20261017)及[第二批记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017)；共新增7个KU与7条候选映射，57条直接关系候选继续待S6。",
        "2026-10-17 三批 S4 登记见[term批次一](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-terms-20261017)、[term批次二](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017)及[work批次](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-works-20261017)；共新增12个KU与12条候选映射，87条直接关系候选继续待S6。", "current S4 batch note")
    return text


def main():
    parser = argparse.ArgumentParser(description="Register five source-backed work groups that are direct S2 relation endpoints")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    manifest_by_id = {row["ku_id"]: row for row in manifest}

    assert len(manifest) == 1639, f"unexpected manifest count: {len(manifest)}"
    assert all(not (ROOT / item["card_path"]).exists() for item in RECORDS)
    for record in RECORDS:
        cid = record["candidate_id"]
        assert candidate_by_id[cid]["suggested_type"] == "work"
        row = alignment_by_id[cid]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert get_group(row.get("resolution_note", "")) == record["group"]
        members = [
            item for item in alignments
            if not item.get("external_source") and item.get("decision") == "new"
            and get_group(item.get("resolution_note", "")) == record["group"]
        ]
        assert [item["candidate_id"] for item in members] == [cid]
        assert record["ku_id"] not in manifest_by_id and record["card_path"] not in accepted_text
        exact_duplicate = [
            item for item in manifest if item["type"] == "work"
            and (item["name_en"].casefold() == record["name_en"].casefold()
                 or item["canonical_name"].casefold() == record["title_zh"].casefold())
        ]
        assert not exact_duplicate, (cid, exact_duplicate)

    relation_ids = {item for record in RECORDS for item in record["relations"]}
    statements = {}
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("statement_id") in relation_ids:
                statements[statement["statement_id"]] = statement
    assert set(statements) == relation_ids
    for record in RECORDS:
        for statement_id in record["relations"]:
            statement = statements[statement_id]
            assert record["candidate_id"] in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")), statement_id
            assert (statement.get("qualifiers") or {}).get("relation_candidate") is True, statement_id
        for source in record["sources"]:
            text = (ROOT / "02-sources" / "02-Markdown" / source["file"]).read_text(encoding="utf-8-sig")
            assert source["quote"] in text, (record["candidate_id"], source["quote"])

    groups, registered, pending = count_groups(alignments)
    assert (len(groups), sum(map(len, groups.values()))) == (4792, 4972)
    assert (len(registered), sum(map(len, registered.values()))) == (620, 767)
    assert (len(pending), sum(map(len, pending.values()))) == (4172, 4205)
    work_registered = [members for members in registered.values() if all(candidate_by_id[r["candidate_id"]]["suggested_type"] == "work" for r in members)]
    work_pending = [members for members in pending.values() if all(candidate_by_id[r["candidate_id"]]["suggested_type"] == "work" for r in members)]
    assert (len(work_registered), sum(map(len, work_registered))) == (41, 46)
    assert (len(work_pending), sum(map(len, work_pending))) == (441, 451)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_manifest = list(manifest)
    for record in RECORDS:
        row = planned_by_id[record["candidate_id"]]
        row["ku_id"] = record["ku_id"]
        row["resolution_note"] += f" S4 registration: mapped {record['group']} to {record['ku_id']}; {len(record['relations'])} direct relation candidates remain pending S6."
        planned_manifest.append({
            "ku_id": record["ku_id"], "type": "work", "canonical_name": record["title_zh"],
            "name_en": record["name_en"], "source_task": TASK, "card_path": record["card_path"],
        })
    assert len(planned_manifest) == 1644
    _, registered_after, pending_after = count_groups(planned_alignment)
    assert (len(registered_after), sum(map(len, registered_after.values()))) == (625, 772)
    assert (len(pending_after), sum(map(len, pending_after.values()))) == (4167, 4200)

    accepted_lines = accepted_text.splitlines()
    for record in sorted(RECORDS, key=lambda item: item["card_path"]):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > record["card_path"]),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {record['card_path']}")
    planned_accepted = "\n".join(accepted_lines) + "\n"
    process_text = update_process(PROCESS_PATH.read_text(encoding="utf-8-sig"))
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"))
    card_texts = {record["card_path"]: make_card(record) for record in RECORDS}

    if args.dry_run:
        print("dry-run passed: groups=5 candidates=5 direct_relation_candidates=30 registered_groups_after=625 mapped_candidates_after=772 pending_groups_after=4167 pending_candidates_after=4200 manifest_after=1644 cards=5")
        return 0

    for record in RECORDS:
        (ROOT / record["card_path"]).write_text(card_texts[record["card_path"]], encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print("applied: groups=5 candidates=5 direct_relation_candidates=30 registered_groups=625 mapped_candidates=772 pending_groups=4167 pending_candidates=4200 manifest=1644 cards=5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
