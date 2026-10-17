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
PROCESS_ANCHOR = "s4-five-direct-endpoint-terms-20261017"


RECORDS = [
    {
        "candidate_id": "cand-4131",
        "group": "sg3-term-cand-4131",
        "ku_id": "units/terms/italian-art",
        "card_path": "04-knowledge/units/terms/italian-art.md",
        "title_zh": "意大利艺术",
        "name_en": "Italian art",
        "description_zh": (
            "本术语登记哈斯克尔书中“意大利艺术”这一宽泛主题性用法。书前编目区以“Art, Italian”列出主题词；正文则在不同历史段落中将意大利艺术作为传播、赞助、收藏与评价的对象。"
            "本卡记录这些书内用法，不把它们归并为边界固定的艺术风格或制度。"
        ),
        "description_en": (
            "This term records Haskell’s broad use of “Italian art” as a subject in the book. The front-matter cataloguing block lists “Art, Italian” as a subject heading, while the text discusses Italian art in distinct historical contexts of circulation, patronage, collecting, and reception. "
            "The unit records these uses in the book and does not treat them as one formally bounded style or institution."
        ),
        "scope": (
            "**原书与编目用法：** 书前编目区保留原词形“Art, Italian”；正文第7章把意大利艺术置于战后需求、法国传播及欧洲赞助语境中。不同段落有各自的时间、地域和论述对象。"
        ),
        "boundary": (
            "**对象边界：** 本卡是书内主题术语，不是地域实体、艺术家群体或艺术制度；它不等同于“意大利巴洛克”“意大利艺术赞助”或某一国别风格，也不把正文中所有意大利艺术家、作品及收藏活动自动视为同一关系。书前的“Art, Italian”仅作为原编目词形保留。"
        ),
        "locator": "书前编目区；第7章 pp.180、182、187。",
        "sources": [
            {"chapter": "书前材料", "page": "2", "file": "00_01_Title_Copyright.md", "lines": "25", "quote": "I. Art, Italian. 2. Art, Baroque—Italy.", "summary": "书前编目区列出“Art, Italian”及“Art, Baroque—Italy”两个分别书写的主题词；本卡只保留前者作为书内术语词形。"},
            {"chapter": "7", "page": "180", "file": "07_CHP-7_sec_i.md", "lines": "129", "quote": "a new demand for Italian art", "summary": "第7章将战后欧洲对意大利艺术的新需求置于17世纪中叶的传播背景中。"},
            {"chapter": "7", "page": "182", "file": "07_CHP-7_sec_i.md", "lines": "154", "quote": "the diffusion of Italian art", "summary": "第7章把 Mazarin 执政初期与意大利艺术在巴黎的传播相联系。"},
            {"chapter": "7", "page": "187", "file": "07_CHP-7_sec_i.md", "lines": "225", "quote": "enthusiastic collectors of Italian art", "summary": "第7章称 Fouquet 与 Colbert 都是意大利艺术的热情收藏者。"},
        ],
        "relations": [
            "st-chp7-p180-i01", "st-chp7-p182-i08", "st-chp7-p182-i09", "st-chp7-p186-i05",
            "st-chp7-p187-i01", "st-chp7-p187-i02", "st-chp7-p200-n4-orleans-patronage",
            "st-chp7-p200-v-contemporary-painting-interest-at-versailles",
            "st-chp7-p200-v-treaties-confirm-changes-and-patronage-counterpart",
            "st-chp7-p201-v-vienna-many-nobles-patronize-italian-art", "st-fm-title-catalog-subject-italian-art",
        ],
        "external_note": "本次依据本书编目区与正文登记术语用法，未新增外部身份或术语数据库记录。",
    },
    {
        "candidate_id": "cand-8134",
        "group": "sg3-term-cand-8134",
        "ku_id": "units/terms/new-families-admitted-venetian-nobility",
        "card_path": "04-knowledge/units/terms/new-families-admitted-venetian-nobility.md",
        "title_zh": "新近获准进入威尼斯贵族阶层的家族",
        "name_en": "New families admitted into Venetian nobility",
        "description_zh": (
            "本术语记录哈斯克尔对威尼斯共和国后期新获准进入贵族阶层的家族及其社会处境的讨论。第9章称，国家财政受战争压力时元老院准许更多家族进入贵族阶层；作者又讨论这些新贵族与旧贵族、行政职位、商业出身及艺术收藏之间的关系。"
            "本卡指书中的群体性类别，不代表一个统一家族或正式组织。"
        ),
        "description_en": (
            "This term records Haskell’s discussion of families newly admitted to the Venetian nobility and their social position in the later Republic. Chapter 9 says that, under fiscal pressure from war, the Senate admitted more families to the nobility; it also discusses these new nobles in relation to the older aristocracy, administrative office, mercantile origins, and art collecting. "
            "The unit denotes a collective category in the book, not one family or a formal organization."
        ),
        "scope": (
            "**原书用法：** 第9章 p.247 称元老院在国家资源耗竭时准许“more and more new families”进入贵族阶层；p.248 讨论富裕家族在获准进入后开始积累收藏。相关段落是哈斯克尔对威尼斯贵族社会及其艺术赞助背景的叙述。"
        ),
        "boundary": (
            "**对象边界：** 此术语不指某个具名家族，也不把所有较晚进入贵族阶层的家庭合并成一个组织。它与原有的 Venetian nobility social estate 术语卡范围不同；不能据此推定每个新贵族家族的财富、政治行为、收藏实践或统一身份。第9章的社会评价和因果解释均保留为哈斯克尔的论述。"
        ),
        "locator": "第9章 pp.247–248；相关索引及正文还见 p.262。",
        "sources": [
            {"chapter": "9", "page": "247", "file": "09_CHP-9_intro.md", "lines": "28", "quote": "admit more and more new families, who were allowed to buy themselves into the nobility", "summary": "哈斯克尔称，战争导致国家资源耗竭时，元老院准许更多新家族购买进入贵族阶层。"},
            {"chapter": "9", "page": "247", "file": "09_CHP-9_intro.md", "lines": "28", "quote": "treated with contempt by the older aristocracy", "summary": "作者称新近贵族常受旧贵族轻视；此处保留为书内社会描述。"},
            {"chapter": "9", "page": "248", "file": "09_CHP-9_intro.md", "lines": "39", "quote": "families who began to amass their collections only upon their reception into the nobility", "summary": "第9章举出在获准进入贵族阶层后才开始积累收藏的富裕家族。"},
        ],
        "relations": [
            "st-chp9-p247-new-nobles-exclusion", "st-chp9-p247-new-nobles-integration",
            "st-chp9-p247-senate-admission", "st-chp9-p248-collections-after-nobility",
            "st-chp9-p262-new-nobles-enrolment", "st-chp9-p247-new-nobles-contempt",
            "st-chp9-p247-new-families-purchase-nobility", "st-chp9-p247-new-nobles-disguise-mercantile-origins",
        ],
        "external_note": "本次仅登记哈斯克尔书内的社会类别与叙述范围，未新增外部身份或家族谱系记录。",
    },
    {
        "candidate_id": "cand-3396",
        "group": "sg3-term-cand-3396",
        "ku_id": "units/terms/counter-reformation",
        "card_path": "04-knowledge/units/terms/counter-reformation.md",
        "title_zh": "反宗教改革",
        "name_en": "Counter Reformation",
        "description_zh": (
            "本术语记录哈斯克尔在书中使用“Counter Reformation”一词时所指的历史宗教语境及其与艺术委托、宗教团体和感受方式的联系。书中从17世纪初的罗马叙述延伸至第9章关于18世纪宗教团体委托的论述。"
            "卡片保留作者的具体时间判断与评价，不将其扩写为完整的宗教史定义。"
        ),
        "description_en": (
            "This term records the historical religious context Haskell denotes by “Counter Reformation” and its connection in the book to artistic commissions, religious communities, and sensibility. The discussion ranges from early seventeenth-century Rome to Chapter 9’s account of commissions by religious communities in the eighteenth century. "
            "The card retains the author’s specific chronology and evaluation without expanding the term into a comprehensive definition of religious history."
        ),
        "scope": (
            "**原书用法：** 第2、3章把该词用于罗马宗教改革背景、宗教团体及相应的艺术感受方式；第9章 p.271 则把相关宗教团体之间的委托竞争称为这一历史进程延续到18世纪的表现。书中用法随章节论题变化。"
        ),
        "boundary": (
            "**对象边界：** 本卡保存哈斯克尔的用词及其叙述，不是天主教会机构卡，不等同于耶稣会或其他修会，也不提供该术语在学界的穷尽定义或统一分期。p.271 关于“延续至18世纪”的判断明确作为作者表述保留。"
        ),
        "locator": "第2章 p.33；第3章 p.76；第9章 p.271。",
        "sources": [
            {"chapter": "2", "page": "33", "file": "02_CHP-2_sec_ii.md", "lines": "27", "quote": "The severity of the Counter Reformation had uprooted the gravest evils of the city", "summary": "哈斯克尔以 Counter Reformation 描述罗马宗教改革语境，并在同段讨论其放松后的精神危机。"},
            {"chapter": "3", "page": "76", "file": "03_CHP-3_sec_ii.md", "lines": "142", "quote": "that particular strain of Counter Reformation sensibility", "summary": "第3章以该词描述 Oratorians 所体现的一种宗教感受方式；此处是作者的艺术史解释。"},
            {"chapter": "9", "page": "271", "file": "09_CHP-9_sec_ii.md", "lines": "49", "quote": "This extraordinary prolongation of the Counter Reformation well into the eighteenth century", "summary": "哈斯克尔把宗教团体在18世纪的委托竞争称为 Counter Reformation 延续的显著表现；该时期判断保留为作者观点。"},
        ],
        "relations": [
            "st-chp1-l21-24-context", "st-chp2-sec-ii-l20-28-counter-reformation-and-spiritual-crisis",
            "st-chp2-secii-l62-69-bibiana-statue-aesthetic-interpretation",
            "st-chp3-secii-l137-142-oratorian-sensibility-contribution",
            "st-chp3-secii-l33-38-haskell-calls-richeome-last-lonely-voice",
            "st-chp3-secii-l33-38-oratorians-pioneers-through-taste-and-inspiration",
            "st-chp9-p271-counter-reformation-competition", "st-chp5-p126-congregazione-counter-reformation-context",
        ],
        "external_note": "本次未使用外部宗教史或术语数据库；卡片不将哈斯克尔的历史判断标为外部验证。",
    },
    {
        "candidate_id": "cand-2068",
        "group": "sg3-term-cand-2068",
        "ku_id": "units/terms/publishers-in-venice",
        "card_path": "04-knowledge/units/terms/publishers-in-venice.md",
        "title_zh": "威尼斯出版商群体",
        "name_en": "Publishers in Venice",
        "description_zh": (
            "本术语记录第13章对威尼斯书籍出版商这一职业群体的概述，重点为18世纪插图书生产及出版商与版画家、艺术家、赞助人和读者市场之间的联系。哈斯克尔以 Albrizzi、Pasquali 和 Zatta 等人说明群体内部的不同实践。"
            "卡片表示书内的群体性类别，不推定所有出版商都采取同一种经营或赞助方式。"
        ),
        "description_en": (
            "This term records Chapter 13’s account of book publishers in Venice, with emphasis on eighteenth-century illustrated books and publishers’ connections with printmakers, artists, patrons, and readerships. Haskell uses figures such as Albrizzi, Pasquali, and Zatta to illustrate different practices within the group. "
            "The card denotes a collective category in the book and does not assume that all publishers followed the same commercial or patronage practices."
        ),
        "scope": (
            "**原书用法：** 第13章先把出版商置于威尼斯经济、欧洲联系与插图书市场中，再分述版画制作、委托绘图或绘画、书店及印刷所经营、出版商自身赞助和对外部赞助的依赖。哈斯克尔重点讨论若干出版者个案。"
        ),
        "boundary": (
            "**对象边界：** 本卡不是威尼斯正式出版行会或机构，也不是所有书商、印刷工和版画家的合并名单。出版商可兼任书商、收藏者或赞助人，但这些角色须按具体人物和原书证据分别记录；本卡不把群体层面的概述推及每一位出版者。"
        ),
        "locator": "第13章 pp.332–339，尤其 pp.332–334、338–339。",
        "sources": [
            {"chapter": "13", "page": "332", "file": "13_CHP-13_intro.md", "lines": "7", "quote": "book publishers had played an important rôle in the Venetian economy", "summary": "第13章将书籍出版商置于威尼斯经济史与共和国后期维持出版地位的努力中。"},
            {"chapter": "13", "page": "333", "file": "13_CHP-13_intro.md", "lines": "17", "quote": "they employed the print makers and commissioned drawings or sometimes paintings from the artists they found suitable", "summary": "哈斯克尔说明出版商雇用版画家，并委托合适艺术家制作图稿或绘画；这是段落中的出版实践概述。"},
            {"chapter": "13", "page": "333", "file": "13_CHP-13_intro.md", "lines": "17", "quote": "they themselves depended on patronage to make it possible", "summary": "第13章指出，较昂贵的出版计划有时仍依赖赞助支持。"},
            {"chapter": "13", "page": "334", "file": "13_CHP-13_intro.md", "lines": "25", "quote": "Three publishers stand out above all the others for the enterprise and quality of their patronage", "summary": "哈斯克尔特别列出 Albrizzi、Pasquali 和 Zatta 三位出版者，并以其赞助实践作比较。"},
            {"chapter": "13", "page": "339", "file": "13_CHP-13_intro.md", "lines": "75", "quote": "Zatta was the most prolific publisher in eighteenth-century Venice", "summary": "第13章以 Zatta 的出版活动说明威尼斯18世纪出版者个案；该评价属于哈斯克尔。"},
        ],
        "relations": [
            "st-chp13-p333-pamphlet-format-and-commissioned-design",
            "st-chp13-p333-publishers-as-patrons-and-reliance-on-patronage",
            "st-chp13-p338-zatta-third-greater-venetian-publisher",
            "st-chp13-p339-zatta-range-of-illustrated-books",
            "st-chp13-p333-publishers-employed-printmakers",
            "st-chp13-p333-publishers-commissioned-suitable-artists",
            "st-chp13-p333-publishers-patronized-printmakers",
            "st-chp13-p333-publishers-depended-on-patronage-for-expensive-ventures",
        ],
        "external_note": "本次依据第13章书内群体描述登记术语；未新增出版史或行业组织的外部身份记录。",
    },
    {
        "candidate_id": "cand-11543",
        "group": "sg3-term-cand-11543",
        "ku_id": "units/terms/venetian-art-tradition-haskell-account",
        "card_path": "04-knowledge/units/terms/venetian-art-tradition-haskell-account.md",
        "title_zh": "哈斯克尔所述的威尼斯艺术传统",
        "name_en": "Venetian art tradition in Haskell’s account",
        "description_zh": (
            "本术语记录哈斯克尔第16章对一条威尼斯绘画传统的特定叙述：他称 Francesco Guardi 为其“最后一位伟大大师”，并说该传统由社会地位较低、当时较少受关注的画家延续；后文又将收藏者和画商对色彩与幻想的偏好置于这一艺术环境中。"
            "这是作者书内的解释性概念，不作为客观分期或固定风格分类。"
        ),
        "description_en": (
            "This term records Haskell’s specific account in Chapter 16 of a Venetian painting tradition: he calls Francesco Guardi its “last great master” and says it was carried on by painters of lower social position who attracted little attention in their own day; later he places collectors’ and dealers’ taste for colour and fantasy within this artistic atmosphere. "
            "This is an interpretive concept in the book, not an objective periodization or a fixed stylistic classification."
        ),
        "scope": (
            "**原书用法：** 第16章 p.373 将该传统与 Guardi、较少受当时关注的画家及新兴赞助人趣味区分开来；pp.374–375 讨论 Sasso、della Lena 等画商的收藏与趣味，并将 Guardi 的创作置于相应氛围中。以上均是哈斯克尔的论述。"
        ),
        "boundary": (
            "**对象边界：** 本卡不把“威尼斯艺术传统”设为正式学科分类、机构、家族或一组成员固定的画家组织，也不据“最后一位伟大大师”等评价推导客观终结年代或连续谱系。它与 Venice 地点卡及具体的威尼斯艺术家、作品和收藏活动分开；后续关系仍须逐条依据对应证据裁决。"
        ),
        "locator": "第16章 pp.373–375。",
        "sources": [
            {"chapter": "16", "page": "373", "file": "16_CHP-16_intro.md", "lines": "8", "quote": "the most fruitful tradition of Venetian art", "summary": "哈斯克尔区分新近赞助人趣味与此前的威尼斯艺术传统，并在同段以 Guardi 与较少受关注的画家展开叙述。"},
            {"chapter": "16", "page": "375", "file": "16_CHP-16_intro.md", "lines": "30", "quote": "whose tastes helped to keep alive a love of colour and fantasy in Venetian art", "summary": "哈斯克尔称若干画商的趣味延续了对威尼斯艺术中颜色与幻想的偏好。"},
            {"chapter": "16", "page": "375", "file": "16_CHP-16_intro.md", "lines": "36", "quote": "Francesco Guardi, with his disregard for ‘truth’, could flourish", "summary": "第16章以 Guardi 的创作说明哈斯克尔所述艺术氛围；评价保留为作者观点。"},
        ],
        "relations": [
            "st-chp16-p373-venetian-tradition-last-great-master-guardi",
            "st-chp16-p373-venetian-tradition-carried-by-lower-status-men",
            "st-chp16-p374-venetian-dealers-retain-painting-heritage",
            "st-chp16-p374-refine-strange-venetian-colour-preference",
            "st-chp16-p374-refine-sasso-earlier-painter-virtuosity",
            "st-chp16-p374-refine-haskell-interprets-modello-rumour",
            "st-chp16-p375-similar-dealers-sustain-venetian-art-tradition",
            "st-chp16-p375-guardi-flourishes-in-della-lena-world",
        ],
        "external_note": "本卡仅记录哈斯克尔的解释性用法；本次未新增外部艺术史核验，也未建立风格层级。",
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
        if item["chapter"] == "书前材料":
            location = f"书前材料，印刷页{item['page']}；OCR L{item['lines']}"
        else:
            location = f"第{item['chapter']}章，印刷页{item['page']}；OCR L{item['lines']}"
        rows.append({
            "citation": card_writer.BOOK_CITATION,
            "location": location,
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
        "type": "term",
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

### 术语范围与边界

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
    registered = {}
    pending = {}
    for group, members in groups.items():
        mapped = [row for row in members if row.get("ku_id")]
        if mapped:
            assert len(mapped) == len(members), f"partially mapped group: {group}"
            assert len({row["ku_id"] for row in mapped}) == 1, f"multiple KU targets: {group}"
            registered[group] = members
        else:
            pending[group] = members
    return groups, registered, pending


def update_process(text: str) -> str:
    text = replace_once(
        text,
        "| term | 1,640 | 42 | 929 / 941 | 0 | 2 | 655 | 18 / 27 | 911 / 914 |",
        "| term | 1,640 | 42 | 929 / 941 | 0 | 2 | 655 | 23 / 32 | 906 / 909 |",
        "process term S4 row",
    )
    text = replace_once(
        text,
        "| **合计** | **12,407** | **1,886** | **4,792 / 4,972** | **8** | **100** | **5,441** | **613 / 760** | **4,179 / 4,212** |",
        "| **合计** | **12,407** | **1,886** | **4,792 / 4,972** | **8** | **100** | **5,441** | **618 / 765** | **4,174 / 4,207** |",
        "process total S4 row",
    )
    if f'<a id="{PROCESS_ANCHOR}"></a>' in text:
        raise AssertionError(f"process anchor already exists: {PROCESS_ANCHOR}")
    bullets = []
    for record in RECORDS:
        rel = len(record["relations"])
        bullets.append(
            f"- `{record['candidate_id']}`（`{record['group']}`）保持 S3 `new` 决定，"
            f"映射至[{record['title_zh']}术语卡](../../../{record['card_path']})（`{record['ku_id']}`）。"
            f"{record['boundary']} 直接关系候选 {rel} 条，全部留待 S6。"
        )
    entry = f"""

<a id="{PROCESS_ANCHOR}"></a>

### S4 term：五组直接关系端点登记（2026-10-17）

本批按待登记直接关系端点优先级登记五个已有 S3 `new` 单成员身份组。逐组裁决、来源引文、边界和逐条关系候选见对应知识卡。

{chr(10).join(bullets)}

五组各登记一个 term KU，并将唯一成员候选映射至该卡；候选决定保持 `new`，未改动 S3 分组或身份判断。五组共 {sum(len(r['relations']) for r in RECORDS)} 条直接 S2 关系候选仍待 S6；没有新增正式关系、外部术语验证或 S5 enrichment。

S4累计登记618组/765条候选映射；待登记4,174组/4,207条；KU总数1,637。
"""
    return text.rstrip() + entry


def update_result(text: str) -> str:
    text = replace_once(
        text,
        "S4 已登记613组、映射760条成员候选；尚待登记4,179组、4,212条映射。",
        "S4 已登记618组、映射765条成员候选；尚待登记4,174组、4,207条映射。",
        "current S4 count",
    )
    text = replace_once(
        text,
        "| [KU 登记](../tables/ku-manifest.csv) | 1,632 KU",
        "| [KU 登记](../tables/ku-manifest.csv) | 1,637 KU",
        "current manifest count",
    )
    text = replace_once(
        text,
        "当前审计提示4,227条待登记 `decision=new` alignment 行，其中4,212条是4,179个未登记身份组的候选映射，另15条是外部身份记录。",
        "当前审计提示4,222条待登记 `decision=new` alignment 行，其中4,207条是4,174个未登记身份组的候选映射，另15条是外部身份记录。",
        "current strict-stage pending rows",
    )
    text = replace_once(
        text,
        "| term | 42→35 | 941／929 | 18／911；914 | 0 | 2 | 655 |",
        "| term | 42→35 | 941／929 | 23／906；909 | 0 | 2 | 655 |",
        "result term S4 row",
    )
    text = replace_once(
        text,
        "| **合计** | **1,886→1,040** | **4,972／4,792** | **613／4,179；4,212** | **8** | **100** | **5,441** |",
        "| **合计** | **1,886→1,040** | **4,972／4,792** | **618／4,174；4,207** | **8** | **100** | **5,441** |",
        "result total S4 row",
    )
    marker = "本轮新增的 archive 身份组包括："
    if text.count(marker) != 1:
        raise AssertionError(f"expected one insertion marker; found {text.count(marker)}")
    text = text.replace(
        marker,
        f"本轮 term 登记批次见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR})；五组共增加5个KU与5条候选映射，43条直接关系候选继续待S6。\n\n{marker}",
        1,
    )
    return text


def main():
    parser = argparse.ArgumentParser(description="Register five S3 term groups that are direct S2 relation endpoints")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    manifest_by_id = {row["ku_id"]: row for row in manifest}
    all_registered = all(
        record["ku_id"] in manifest_by_id
        and (ROOT / record["card_path"]).exists()
        and record["card_path"] in accepted_text
        and alignment_by_id.get(record["candidate_id"], {}).get("ku_id") == record["ku_id"]
        for record in RECORDS
    )
    if all_registered:
        assert len(manifest) == 1637
        print("ALREADY REGISTERED: five direct-endpoint term groups; manifest=1637")
        return 0

    assert len(manifest) == 1632, f"unexpected manifest count: {len(manifest)}"
    assert len(alignments) == 12642, f"unexpected alignment count: {len(alignments)}"
    assert len(candidate_by_id) == 12407, f"unexpected candidate count: {len(candidate_by_id)}"
    assert len(accepted_text.splitlines()) > 0
    assert all((ROOT / record["card_path"]).is_file() is False for record in RECORDS)
    assert all(record["candidate_id"] in candidate_by_id and record["candidate_id"] in alignment_by_id for record in RECORDS)
    assert all(candidate_by_id[r["candidate_id"]]["suggested_type"] == "term" for r in RECORDS)
    for record in RECORDS:
        row = alignment_by_id[record["candidate_id"]]
        assert row["decision"] == "new" and not row.get("ku_id"), record["candidate_id"]
        assert get_group(row.get("resolution_note", "")) == record["group"], record["candidate_id"]
        group_rows = [
            item for item in alignments
            if not item.get("external_source") and item.get("decision") == "new"
            and get_group(item.get("resolution_note", "")) == record["group"]
        ]
        assert [item["candidate_id"] for item in group_rows] == [record["candidate_id"]], record["group"]
        assert record["ku_id"] not in manifest_by_id
        assert record["card_path"] not in accepted_text

    direct_relation_ids = {item for record in RECORDS for item in record["relations"]}
    statements = {}
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("statement_id") in direct_relation_ids:
                statements[statement["statement_id"]] = statement
    assert set(statements) == direct_relation_ids
    for record in RECORDS:
        for statement_id in record["relations"]:
            row = statements[statement_id]
            assert record["candidate_id"] in (row.get("subject_candidate_id"), row.get("object_candidate_id")), statement_id
            assert (row.get("qualifiers") or {}).get("relation_candidate") is True, statement_id
    for record in RECORDS:
        for item in record["sources"]:
            source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
            assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    groups, registered, pending = count_groups(alignments)
    assert (len(groups), sum(map(len, groups.values()))) == (4792, 4972)
    assert (len(registered), sum(map(len, registered.values()))) == (613, 760)
    assert (len(pending), sum(map(len, pending.values()))) == (4179, 4212)
    term_pending = [members for members in pending.values() if all(candidate_by_id[row["candidate_id"]]["suggested_type"] == "term" for row in members)]
    term_registered = [members for members in registered.values() if all(candidate_by_id[row["candidate_id"]]["suggested_type"] == "term" for row in members)]
    assert (len(term_registered), sum(map(len, term_registered))) == (18, 27)
    assert (len(term_pending), sum(map(len, term_pending))) == (911, 914)

    planned_manifest = list(manifest)
    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    for record in RECORDS:
        planned_by_id[record["candidate_id"]]["ku_id"] = record["ku_id"]
        planned_by_id[record["candidate_id"]]["resolution_note"] += (
            f" S4 registration: mapped {record['group']} to {record['ku_id']}; "
            f"{len(record['relations'])} direct relation candidates remain pending S6."
        )
        planned_manifest.append({
            "ku_id": record["ku_id"], "type": "term", "canonical_name": record["title_zh"],
            "name_en": record["name_en"], "source_task": TASK, "card_path": record["card_path"],
        })
    assert len(planned_manifest) == 1637
    planned_groups, planned_registered, planned_pending = count_groups(planned_alignment)
    assert (len(planned_registered), sum(map(len, planned_registered.values()))) == (618, 765)
    assert (len(planned_pending), sum(map(len, planned_pending.values()))) == (4174, 4207)

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
        print(
            "dry-run passed: groups=5 candidates=5 direct_relation_candidates=43 "
            "registered_groups_after=618 mapped_candidates_after=765 pending_groups_after=4174 "
            "pending_candidates_after=4207 manifest_after=1637 cards=5"
        )
        return 0

    for record in RECORDS:
        path = ROOT / record["card_path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(card_texts[record["card_path"]], encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        "applied: groups=5 candidates=5 direct_relation_candidates=43 registered_groups=618 "
        "mapped_candidates=765 pending_groups=4174 pending_candidates=4207 manifest=1637 cards=5"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
