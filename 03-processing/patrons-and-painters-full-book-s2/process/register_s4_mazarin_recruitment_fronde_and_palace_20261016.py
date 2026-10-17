from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path

import yaml


ROOT = Path.cwd()
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
KNOWLEDGE = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
SOURCE_PATH = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
SOURCE = ROOT / SOURCE_PATH
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md"
BACKUP_SUFFIX = ".bak-s4-mazarin-events-palace-20261016"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool]:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader), has_bom


def encode_csv(fields: list[str], rows: list[dict[str, str]], has_bom: bool) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    text = stream.getvalue()
    return ("\ufeff" + text if has_bom else text).encode("utf-8")


def group_of(note: str) -> str:
    match = re.search(r"group=([^;|\s]+)", note)
    return match.group(1) if match else ""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def text_bytes(path: Path, text: str) -> bytes:
    has_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    return ("\ufeff" + text if has_bom else text).encode("utf-8")


def source_item(page: str, lines: str, quote: str, summary: str, location_note: str = "") -> dict:
    location = f"第7章；印刷页{page}；OCR L{lines}"
    if location_note:
        location += f"；{location_note}"
    span = f"lines {lines}; print p. {page}"
    if location_note:
        span += f"; {location_note}"
    return {
        "citation": BOOK_CITATION,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": f"lines {lines}", "text": quote}],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": SOURCE_PATH, "source_span": span},
    }


EVIDENCE_176 = "[第7章 p.176](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L89）"
EVIDENCE_177 = "[第7章 p.177](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L93）"
EVIDENCE_181 = "[第7章 p.181](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L144）"
EVIDENCE_182 = "[第7章 p.182](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L157–158）"
EVIDENCE_183_161 = "[第7章 p.183](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L161）"
EVIDENCE_183_162 = "[第7章 p.183](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L162）"
EVIDENCE_183_165 = "[第7章 p.183](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L165）"
EVIDENCE_183_N2 = "[第7章 p.183 注2](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（注释转录 L349）"


CARDS = [
    {
        "ku_id": "units/events/mazarin-1644-bernini-recruitment-attempt",
        "type": "event",
        "canonical_name": "马萨林1644年劝贝尔尼尼定居法国的尝试",
        "name_en": "Mazarin's 1644 Attempt to Persuade Bernini to Settle in France",
        "path": "04-knowledge/units/events/mazarin-1644-bernini-recruitment-attempt.md",
        "group": "sg3-event-cand-1594",
        "candidates": ["cand-1594"],
        "sources": [
            source_item("176", "89", "Early in 1644 he made a determined effort to get Bernini himself to settle in France by offering him a huge salary.", "Haskell称 Mazarin 于1644年初以金额未载的高额薪俸劝 Bernini 定居法国。"),
            source_item("177", "93", "‘You are made for Rome and Rome is made for you’, he is reported to have told him— words powerful enough to detain Bernini even when this munificent patron died and bad days followed.", "Haskell转述 Urban VIII 劝 Bernini 留在罗马的话，并称这番话有力到足以留住 Bernini。", "reported speech in Haskell's account"),
            source_item("181", "144", "It has already been pointed out that Mazarin’s earliest attempts to attract Italian artists to France, made while Urban VIII was still alive, met with no success.", "Haskell回顾称 Urban VIII 在世时 Mazarin 最早的招揽意大利艺术家的努力均未成功；该概括不精确分配到单次行动。"),
        ],
        "description_zh": (
            "本卡记录哈斯克尔所述1644年初的一次招揽尝试：[马萨林（Jules Mazarin）](../persons/mazarin.md) "
            "以金额未载的高额薪俸劝[贝尔尼尼（Gian Lorenzo Bernini）](../persons/gian-lorenzo-bernini.md)定居法国。"
            "第7章 p.177 将 Urban VIII 劝留 Bernini 的话明确写作转述；p.181 对早期招揽的失败作总体回顾，"
            "本卡不把该回顾强行分配给单次行动，也不据此称 Bernini 接受、迁居或领取了薪俸。"
        ),
        "description_en": (
            "This unit records Haskell’s account of an early-1644 recruitment effort: "
            "[Jules Mazarin](../persons/mazarin.md) offered an unspecified large salary to persuade "
            "[Gian Lorenzo Bernini](../persons/gian-lorenzo-bernini.md) to settle in France. On p.177, "
            "Haskell presents Urban VIII’s reported words to Bernini as reported speech. Page 181 gives a "
            "general retrospective account of the early recruitment efforts’ failure; this unit does not assign "
            "that summary to this single attempt or claim that Bernini accepted, moved, or received a salary."
        ),
        "body": f"""## 内容

### 描述

**中文：** {{description_zh}}

**English:** {{description_en}}

### 事件信息

| 项目 | 内容 | 依据 |
|---|---|---|
| 性质 | 招揽 Bernini 定居法国的尝试；不是已完成迁居 | S1；{EVIDENCE_176} |
| 时间 | 1644年初 | S1；{EVIDENCE_176} |
| 行动者与对象 | Mazarin 发起；Bernini 为被招揽者 | S1；{EVIDENCE_176} |
| 提议条件 | 高额薪俸；原文未给金额 | S1；{EVIDENCE_176} |
| 相关语境 | Haskell 报告 Urban VIII 的劝留话语；其历史归属仍按转述表达 | S2；{EVIDENCE_177} |
| 结果限定 | p.181 总括早期招揽未成功，但没有逐次列出结果；不据此补写 Bernini 的接受或拒绝过程 | S3；{EVIDENCE_181} |

## 关系与证据

### 关系记录

尚无正式关系记录。本卡只登记这次招揽尝试的事件身份；原文行动关系留待 S6 逐条审查。
""",
    },
    {
        "ku_id": "units/events/mazarin-1648-algardi-recruitment-attempt",
        "type": "event",
        "canonical_name": "马萨林1648年劝阿尔加迪赴法的尝试",
        "name_en": "Mazarin's 1648 Attempt to Persuade Algardi to Come to France",
        "path": "04-knowledge/units/events/mazarin-1648-algardi-recruitment-attempt.md",
        "group": "sg3-event-cand-1595",
        "candidates": ["cand-1595"],
        "sources": [
            source_item("182", "157", "In 1648 he wrote personally to Algardi and tried, through the most generous offers, to persuade him to reverse his refusal 0's some six years earlier. So advantageous were the terms proposed that the sculptor was on the point of departing when once again papal policy interfered.", "Haskell称 Mazarin 于1648年亲自致函 Algardi，以优厚条件劝他改变约六年前的拒绝；Algardi 几乎动身时教廷政策再次介入。"),
            source_item("182", "158", "However mean Innocent X and his nephew might be, they could scarcely allow their principal artist to leave Rome, and so ‘they made him so many offers, so many promises,", "Haskell开启一段关于 Innocent X 与其侄子向 Algardi 提出条件的引述；原文跨页续接。"),
            source_item("183", "161", "plied him with so much flattery and aroused in him so many hopes that they made him change his mind and cancel all his contracts [with the French]’.1", "Haskell续引该段叙述，称 Algardi 改变主意并取消与法国方面的合同；注1指向 Passeri。", "continuation of the quotation begun on p.182; cited Passeri p.210 not independently read"),
        ],
        "description_zh": (
            "本卡记录哈斯克尔所述1648年招揽尝试：Mazarin 亲自致函 [阿尔加迪（Alessandro Algardi）](../persons/alessandro-algardi.md)，"
            "以优厚条件劝他改变约六年前的拒绝。原文称 Algardi 几乎动身赴法时，"
            "教廷政策再次介入；哈斯克尔随后引述他改变主意并取消法国合同的说法。原文未把早先拒绝定为确切年份，"
            "也未说明干预的具体机制；所引 Passeri 页码未在本轮独立查阅。"
        ),
        "description_en": (
            "This unit records Haskell’s account of a 1648 recruitment effort: Mazarin wrote personally to "
            "[Alessandro Algardi](../persons/alessandro-algardi.md) and made generous offers to reverse a refusal "
            "from about six years earlier. Haskell says Algardi was close to departing for France when papal policy "
            "intervened again, and then quotes an account in which Algardi changed his mind and cancelled his French "
            "contracts. The earlier refusal is not assigned an exact year, the intervention’s mechanism is not stated, "
            "and the cited Passeri page has not been independently read."
        ),
        "body": f"""## 内容

### 描述

**中文：** {{description_zh}}

**English:** {{description_en}}

### 事件信息

| 项目 | 内容 | 依据 |
|---|---|---|
| 性质 | Mazarin 劝 Algardi 赴法的招揽尝试 | S1；{EVIDENCE_182} |
| 时间 | 1648年；早先拒绝约在六年前，确切年份未定 | S1；{EVIDENCE_182} |
| 行动者与对象 | Mazarin 亲自致函并提出条件；Algardi 为被招揽者 | S1；{EVIDENCE_182} |
| 提议条件 | 原文称 offers 和 proposed terms 极为优厚，未列具体金额 | S1；{EVIDENCE_182} |
| 结果 | Haskell称教廷政策介入，Algardi 最终取消法国合同；这是经 Haskell 转引的叙述 | S1、S3；{EVIDENCE_182} {EVIDENCE_183_161} |

## 关系与证据

### 关系记录

尚无正式关系记录。本卡只登记1648年招揽尝试的事件身份；书信、邀请及干预关系留待 S6 逐条审查。
""",
    },
    {
        "ku_id": "units/events/first-fronde-mazarin-patronage-setback-1649",
        "type": "event",
        "canonical_name": "第一次投石党运动及马萨林意大利艺术赞助受挫（1649）",
        "name_en": "The First Fronde and the 1649 Setback to Mazarin's Patronage of Italian Artists",
        "path": "04-knowledge/units/events/first-fronde-mazarin-patronage-setback-1649.md",
        "group": "sg3-event-cand-6799",
        "candidates": ["cand-1598", "cand-6799"],
        "sources": [
            source_item("183", "165", "In 1649 Mazarin’s patronage of Italian artists met with a disastrous, though temporary, set-back. The first Fronde—that strange and shifting alliance of aristocratic and bourgeois factions—turned against the Cardinal with great violence.", "Haskell称1649年第一次投石党运动猛烈反对 Mazarin，使其对意大利艺术家的赞助遭遇灾难性但暂时的挫折。"),
        ],
        "description_zh": (
            "本卡记录哈斯克尔对1649年第一次投石党运动及其艺术赞助语境的叙述：他称第一次投石党运动猛烈反对 "
            "Mazarin，使其对意大利艺术家的赞助遭遇灾难性但暂时的挫折。该措辞保留为哈斯克尔的判断；本卡不扩展为完整政治事件史，"
            "也不推定联盟成员或将所有同时期冲突并入此组。"
        ),
        "description_en": (
            "This unit records Haskell’s account of the First Fronde in 1649 and its patronage context: he describes "
            "the First Fronde as turning violently against Mazarin and causing a disastrous but temporary setback to "
            "his patronage of Italian artists. The evaluation remains attributed to Haskell. This unit does not expand "
            "the account into a complete political history, identify the alliance’s members, or absorb every conflict "
            "of the period into this event group."
        ),
        "body": f"""## 内容

### 描述

**中文：** {{description_zh}}

**English:** {{description_en}}

### 事件信息

| 项目 | 内容 | 依据 |
|---|---|---|
| 性质 | Haskell 所述第一次投石党运动反对 Mazarin，并影响其意大利艺术赞助 | S1；{EVIDENCE_183_165} |
| 时间 | 1649年 | S1；{EVIDENCE_183_165} |
| 参与者 | 第一次投石党运动；原文概括为贵族与市民阶层组成的变动联盟，未列成员 | S1；{EVIDENCE_183_165} |
| Haskell 对结果的描述 | 对意大利艺术家的赞助遭遇灾难性但暂时的挫折 | S1；{EVIDENCE_183_165} |

## 关系与证据

### 关系记录

尚无正式关系记录。事件组的参与者、受影响的赞助对象及具体后果留待 S6 逐条审查。
""",
    },
    {
        "ku_id": "units/events/mazarin-bentivoglio-palace-purchase-before-1647",
        "type": "event",
        "canonical_name": "马萨林购买罗马本蒂沃利奥宫殿（1647年前；确切日期未定）",
        "name_en": "Mazarin's Purchase of the Bentivoglio Palace in Rome (before 1647; exact date uncertain)",
        "path": "04-knowledge/units/events/mazarin-bentivoglio-palace-purchase-before-1647.md",
        "group": "sg3-event-cand-1599",
        "candidates": ["cand-1599"],
        "sources": [
            source_item("183", "162", "Soon after 1644 he bought the great palace of his one-time patrons, the Bentivoglio, and planned to use it for distinguished French visitors to the city.", "Haskell称 Mazarin 于1644年后不久买下其昔日赞助者 Bentivoglio 家族的宫殿，并计划供杰出法国访客赴罗马时使用。"),
            source_item("183", "349", "2 Mazarin bought the palace from the Lante family which had acquired it from the Bentivoglio.", "第7章注2称 Mazarin 从 Lante 家族购入该宫殿；Lante 家族此前从 Bentivoglio 家族取得该建筑。", "footnote transcription"),
            source_item("183", "168", "The exact-date of the transaction is not certain, but it must have been before 1647—d’Aumale, p. 8. See also Callari, p. 298.", "第7章正文称交易确切日期不定，但在1647年前；所引 d’Aumale 与 Callari 页码未独立查阅。", "note 2"),
        ],
        "description_zh": (
            "本卡记录哈斯克尔所述马萨林购入罗马宫殿的交易。正文称他在1644年后不久买下其昔日赞助者 Bentivoglio 家族的宫殿；"
            "注2说明该建筑经 Lante 家族转手，交易确切日期未定但早于1647年。此事件与被购入的宫殿地点实体分开；"
            "不把“soon after 1644”改写成确切年份。"
        ),
        "description_en": (
            "This unit records Haskell’s account of Mazarin’s purchase of a palace in Rome. The narrative says he bought "
            "the palace of his former Bentivoglio patrons soon after 1644; note 2 says the building passed through the "
            "Lante family and that the transaction’s exact date is uncertain but before 1647. The purchase event is "
            "distinct from the palace as a place. “Soon after 1644” is not converted into an exact year."
        ),
        "body": f"""## 内容

### 描述

**中文：** {{description_zh}}

**English:** {{description_en}}

### 事件信息

| 项目 | 内容 | 依据 |
|---|---|---|
| 性质 | 购买宫殿的交易；不等同于宫殿地点本身 | S1；{EVIDENCE_183_162} |
| 时间 | 1644年后不久；注2称确切日期不定、早于1647年 | S1、S3；{EVIDENCE_183_162} {EVIDENCE_183_N2} |
| 买方 | [马萨林（Jules Mazarin）](../persons/mazarin.md) | S1；{EVIDENCE_183_162} |
| 交易对象 | [罗马本蒂沃利奥宫殿](../places/mazarin-bentivoglio-palace-rome.md)；名称为描述性工作名 | S1；{EVIDENCE_183_162} |
| 转让脉络 | 注2称 Lante 家族此前从 Bentivoglio 家族取得宫殿，Mazarin 后从 Lante 购入 | S2；{EVIDENCE_183_N2} |

## 关系与证据

### 关系记录

尚无正式关系记录。本卡登记交易身份；所有权转移与具体地点关系留待 S6 审查。
""",
    },
    {
        "ku_id": "units/places/mazarin-bentivoglio-palace-rome",
        "type": "place",
        "canonical_name": "马萨林购得的罗马本蒂沃利奥宫殿",
        "name_en": "The Bentivoglio Palace in Rome Acquired by Mazarin",
        "path": "04-knowledge/units/places/mazarin-bentivoglio-palace-rome.md",
        "group": "sg3-place-cand-6796",
        "candidates": ["cand-6796"],
        "sources": [
            source_item("183", "162", "Soon after 1644 he bought the great palace of his one-time patrons, the Bentivoglio, and planned to use it for distinguished French visitors to the city.2 Though he himself never returned to see once again the rooms where he had been received as an obscure and ambitious young diplomat, the thought that he owned the vast palace, whose casino contained the world-famous fresco of Aurora painted by Guido Reni for Scipione Borghese, must have given him intense satisfaction.", "Haskell称马萨林购入其昔日 Bentivoglio 赞助者的罗马宫殿，计划供法国贵宾到访时使用，并叙述其早年曾在此受接待及赌场内 Aurora 壁画。"),
            source_item("183", "349", "2 Mazarin bought the palace from the Lante family which had acquired it from the Bentivoglio.", "第7章注2给出宫殿经 Lante 家族转手的叙述。", "footnote transcription"),
        ],
        "description_zh": (
            "本卡以描述性工作名标识哈斯克尔所称马萨林购入的罗马宫殿：正文称其为昔日赞助者 Bentivoglio 家族的宏大宫殿，"
            "注2说明其后由 Lante 家族持有、再售予 Mazarin。原书未给出正式宫名或精确现代地址；本标题不是经核实的官方建筑名称。"
        ),
        "description_en": (
            "This unit uses a descriptive working name for the Roman palace Haskell says Mazarin acquired: the narrative "
            "calls it the great palace of his former Bentivoglio patrons, and note 2 says it passed through the Lante family "
            "before Mazarin bought it. The source supplies neither an official palace name nor a precise modern address; "
            "the title is not presented as a verified official name."
        ),
        "body": f"""## 内容

### 描述

**中文：** {{description_zh}}

**English:** {{description_en}}

### 名称与基本信息

| 项目 | 内容 | 依据 |
|---|---|---|
| 名称性质 | 根据原书描述拟定的工作名；非已核实官方宫名 | S1；{EVIDENCE_183_162} |
| 地点类型 | 罗马的宫殿建筑（place）；与购买事件分开 | S1；{EVIDENCE_183_162} |
| 地理位置 | Rome；原文未给具体街道或现代地址 | S1；{EVIDENCE_183_162} |
| 过户脉络 | Bentivoglio 家族 → Lante 家族 → Mazarin；据 Haskell 注2转述 | S2；{EVIDENCE_183_N2} |
| Mazarin 的计划用途 | 接待到访罗马的杰出法国访客 | S1；{EVIDENCE_183_162} |
| 内部空间与作品 | Haskell称赌场内有 Guido Reni 为 Scipione Borghese 绘制的 Aurora 壁画；单独作品身份与版本尚待身份对齐裁决 | S1；{EVIDENCE_183_162} |

### 本章相关内容

Haskell称 Mazarin 年轻时曾作为一名默默无闻而有抱负的外交官在宫殿房间受接待，后来没有再回访；他认为拥有这座宫殿可能令 Mazarin 感到满足。该判断保留为 Haskell 的解释，不作为可直接观察的心理事实。{EVIDENCE_183_162}

## 关系与证据

### 关系记录

尚无正式关系记录。所有权、计划用途、内部空间和作品联系留待 S6 按端点身份与具体证据逐条审查。
""",
    },
]


def make_card(record: dict) -> str:
    frontmatter = {
        "title": f"{record['canonical_name']}（{record['name_en']}）",
        "name_en": record["name_en"],
        "type": record["type"],
        "evidence_status": "source_backed",
        "sources": record["sources"],
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": PROCESS_REF,
    }
    text = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = record["body"].replace("{{description_zh}}", record["description_zh"]).replace("{{description_en}}", record["description_en"])
    return f"---\n{text}---\n\n{body.strip()}\n"


def count_groups(rows: list[dict[str, str]]) -> tuple[int, int, int, int]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new":
            group = group_of(row["resolution_note"])
            if not group:
                raise SystemExit(f"new decision lacks group token: {row['candidate_id']}")
            groups[group].append(row)
    registered = {group: members for group, members in groups.items() if any(row.get("ku_id") for row in members)}
    mapped = sum(bool(row.get("ku_id")) for members in registered.values() for row in members)
    pending_members = [row for row in rows if row.get("decision") == "new" and not row.get("ku_id") and not row.get("external_source")]
    return len(registered), mapped, len(groups) - len(registered), len(pending_members)


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one result occurrence of {old!r}, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the new Mazarin event and place groups for S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not (ROOT / "04-knowledge" / "accepted.yml").exists() or not SOURCE.exists():
        raise SystemExit("Run this script from the project root; expected project files are missing.")

    source_text = SOURCE.read_text(encoding="utf-8-sig")
    for card in CARDS:
        if not card["sources"]:
            raise SystemExit(f"No source evidence supplied for {card['ku_id']}.")
        for source in card["sources"]:
            quote = source["original_quotes"][0]["text"]
            if quote not in source_text:
                raise SystemExit(f"Quoted source text not found for {card['ku_id']}: {quote[:100]}")
        if not card["description_zh"].strip() or not card["description_en"].strip():
            raise SystemExit(f"Bilingual description missing for {card['ku_id']}.")
        if card["path"].startswith("04-knowledge/units/") is False:
            raise SystemExit(f"Unexpected card path: {card['path']}")

    alignment_fields, alignments, alignment_bom = read_csv(ALIGNMENT)
    manifest_fields, manifest_rows, manifest_bom = read_csv(MANIFEST)
    candidate_rows = list(csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline="")))
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    alignment_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    manifest_by_id = {row["ku_id"]: row for row in manifest_rows}
    accepted_text = ACCEPTED.read_text(encoding="utf-8-sig")
    accepted_lines = accepted_text.splitlines()
    source_statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in source_statements}
    expected_statement_ids = {
        "st-chp7-p176-i32", "st-chp7-p177-i01", "st-chp7-p181-i18",
        "st-chp7-p182-i20", "st-chp7-p182-i21", "st-chp7-p182-i24",
        "st-chp7-p183-i02", "st-chp7-p183-i13", "st-chp7-p183-i20",
    }
    if not expected_statement_ids.issubset(statement_by_id):
        raise SystemExit(f"Missing S2 statement evidence: {sorted(expected_statement_ids - set(statement_by_id))}")

    expected_types = {
        "cand-1594": "event", "cand-1595": "event", "cand-1598": "event",
        "cand-6799": "event", "cand-1599": "event", "cand-6796": "place",
    }
    for cid, kind in expected_types.items():
        if cid not in candidate_by_id or cid not in alignment_by_id:
            raise SystemExit(f"Missing candidate or alignment row: {cid}")
        if candidate_by_id[cid]["suggested_type"] != kind:
            raise SystemExit(f"Unexpected type for {cid}: {candidate_by_id[cid]['suggested_type']}")
        row = alignment_by_id[cid]
        if row["decision"] != "new" or row["ku_id"]:
            raise SystemExit(f"{cid} is no longer an unmapped new candidate.")

    target_card_ids = {card["ku_id"] for card in CARDS}
    target_card_paths = {card["path"] for card in CARDS}
    if len(target_card_ids) != len(CARDS) or len(target_card_paths) != len(CARDS):
        raise SystemExit("Duplicate S4 target KU ID or card path in batch.")
    for card in CARDS:
        if card["ku_id"] in manifest_by_id or card["path"] in accepted_text or (ROOT / card["path"]).exists():
            raise SystemExit(f"S4 target already exists; inspect before registering {card['ku_id']}.")

    group_candidate_ids: dict[str, list[str]] = defaultdict(list)
    for card in CARDS:
        group_candidate_ids[card["group"]].extend(card["candidates"])
    for group, expected_ids in group_candidate_ids.items():
        members = [
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
            and group_of(row["resolution_note"]) == group
        ]
        if sorted(members) != sorted(expected_ids):
            raise SystemExit(f"Unexpected S3 members for {group}: {members}")
    if len(CARDS) != 5 or len(group_candidate_ids) != 5:
        raise SystemExit("Unexpected batch size; this script expects five S4 identity groups.")

    before = count_groups(alignments)
    if before != (281, 352, 4559, 4669) or len(manifest_rows) != 1300:
        raise SystemExit(f"Unexpected S4 baseline: groups/mappings/pending={before}, manifest={len(manifest_rows)}")

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    for card in CARDS:
        for cid in card["candidates"]:
            row = planned_by_id[cid]
            row["ku_id"] = card["ku_id"]
            row["resolution_note"] += f" S4 registration: mapped {card['group']} to {card['ku_id']}."

    planned_manifest = list(manifest_rows)
    for card in CARDS:
        planned_manifest.append({
            "ku_id": card["ku_id"],
            "type": card["type"],
            "canonical_name": card["canonical_name"],
            "name_en": card["name_en"],
            "source_task": TASK,
            "card_path": card["path"],
        })
    planned_manifest.sort(key=lambda row: row["ku_id"])
    after = count_groups(planned_alignment)
    if after != (286, 358, 4554, 4663) or len(planned_manifest) != 1305:
        raise SystemExit(f"Unexpected S4 post-registration counts: groups/mappings/pending={after}, manifest={len(planned_manifest)}")

    new_accepted_lines = list(accepted_lines)
    for card in sorted(CARDS, key=lambda row: row["path"]):
        if any(line == f"- {card['path']}" for line in new_accepted_lines):
            raise SystemExit(f"Accepted path already exists: {card['path']}")
        insert_at = next(
            (i for i, line in enumerate(new_accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > card["path"]),
            next((i for i, line in enumerate(new_accepted_lines) if line == "claims:"), len(new_accepted_lines)),
        )
        new_accepted_lines.insert(insert_at, f"- {card['path']}")
    planned_accepted = "\n".join(new_accepted_lines) + "\n"

    result_text = RESULT.read_text(encoding="utf-8-sig")
    result_text = replace_once(
        result_text,
        "| [KU 登记](../tables/ku-manifest.csv) | 1,300 KU；新组登记与待登记分类型统计见下表 |",
        "| [KU 登记](../tables/ku-manifest.csv) | 1,305 KU；新组登记与待登记分类型统计见下表 |",
    )
    result_text = replace_once(
        result_text,
        "S4 已登记281组、映射352条成员候选；尚待登记4,559组、4,669条映射。",
        "S4 已登记286组、映射358条成员候选；尚待登记4,554组、4,663条映射。",
    )
    result_text = replace_once(
        result_text,
        "| event | 7→7 | 235／231 | 10／221；225 | 0 | 0 | 115 |",
        "| event | 7→7 | 235／231 | 14／217；220 | 0 | 0 | 115 |",
    )
    result_text = replace_once(
        result_text,
        "| place | 207→152 | 585／576 | 9／567；572 | 0 | 0 | 317 |",
        "| place | 207→152 | 585／576 | 10／566；571 | 0 | 0 | 317 |",
    )
    if "### S4 event/place：Mazarin 招揽、Fronde、购置事件与宫殿地点登记" in result_text:
        raise SystemExit("The S4 batch result section already exists.")
    result_section = (
        "### S4 event/place：Mazarin 招揽、Fronde、购置事件与宫殿地点登记（2026-10-16）\n\n"
        "- 新增4张 event 卡及1张 place 卡，登记5个 S3 new 身份组：Mazarin 1644年招揽 Bernini、1648年招揽 Algardi、1649年 First Fronde 赞助受挫、购买 Bentivoglio 宫殿，以及该宫殿地点。候选 `cand-1598` 与 `cand-6799` 共映射至 First Fronde 事件卡；其余候选各映射至对应组卡。\n"
        "- 卡片保存双语名称、语义对应描述、具体章页原文摘录及证据范围；结构化字段按字段表接口登记26条与卡片表格逐行对应的来源支持行。宫殿地点采用描述性工作名；购买事件与建筑 place 分开。未新增外部身份、外部事实补足或正式关系；直接关系候选留待 S6。\n"
        "- S4 当前累计登记286组、358条候选映射；待登记4,554组、4,663条映射。event 类型为14组已登记、217组/220条成员待登记；place 类型为10组已登记、566组/571条成员待登记。\n\n"
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", result_section + "## 未解决项与交接限制")

    process_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    process_section = (
        "\n\n### S4 event/place：Mazarin 招揽、Fronde、购置事件与宫殿地点登记（2026-10-16）\n\n"
        "- Event `sg3-event-cand-1594`（`cand-1594`）登记至 `units/events/mazarin-1644-bernini-recruitment-attempt`。第7章 p.176 L89 支持1644年初以金额未载的高额薪俸招揽 Bernini；p.177 L93 是 Haskell 的转述；p.181 L144 对早期招揽作总体回顾，不将总体失败结论强配给该单次行动。\n"
        "- Event `sg3-event-cand-1595`（`cand-1595`）登记至 `units/events/mazarin-1648-algardi-recruitment-attempt`。p.182 L157–158 与 p.183 L161 记载1648年致函、优厚条件、教廷介入及取消法国合同的转引叙述；早先拒绝只保留“约六年前”，Passeri p.210 未独立查阅。\n"
        "- Event `sg3-event-cand-6799` 的 `cand-6799` 与索引候选 `cand-1598` 一同映射至 `units/events/first-fronde-mazarin-patronage-setback-1649`。p.183 L165 支持1649年 First Fronde 转向反对 Mazarin 及其对意大利艺术赞助造成暂时挫折；保留 Haskell 的范围和评价，不扩写为完整政治事件史。\n"
        "- Event `sg3-event-cand-1599`（`cand-1599`）登记至 `units/events/mazarin-bentivoglio-palace-purchase-before-1647`；place `sg3-place-cand-6796`（`cand-6796`）登记至 `units/places/mazarin-bentivoglio-palace-rome`。p.183 L162 与注2转录 L349 支持交易、Lante–Bentivoglio 转手脉络及确切日期不定但早于1647年的限定。购买事件与宫殿地点分开；place 标题注明为描述性工作名，不宣称官方宫名或现代地址。\n"
        "- 五组登记共写入5张双语卡、`ku-manifest.csv` 5条、alignment 6条候选映射、`enrichment.jsonl` 26条字段行，并将5条路径加入 `accepted.yml`。place 卡保留原书关于赌场 Aurora 壁画的叙述，但相关 work 候选仍 undecided，不建立对象边；Mazarin—Bernini、Mazarin—Algardi、Fronde—Mazarin、所有权及建筑用途等正式边仍待 S6。未新增 `relations.csv`、S5 外部补足或外部身份。\n"
        "- 字段表写入使用 `build_field_facts.py` 的只读预检与 apply；`sources.csv` 同步补登记15条已被既有 KU 引用、此前缺少目录行的来源记录，不包含本批新增外部采集。\n- S4 计数：新增登记5组/6条映射；累计286组/358条映射，待登记4,554组/4,663条映射；KU 总数1,305。\n"
    )
    if "### S4 event/place：Mazarin 招揽、Fronde、购置事件与宫殿地点登记" in process_text:
        raise SystemExit("The S4 batch process section already exists.")
    process_text += process_section

    planned_card_bytes = {ROOT / card["path"]: make_card(card).encode("utf-8-sig") for card in CARDS}
    for path, content in planned_card_bytes.items():
        if path.exists():
            raise SystemExit(f"Card appeared during preflight: {path}")
        frontmatter_text = make_card(next(card for card in CARDS if ROOT / card["path"] == path)).split("---\n", 2)[1]
        frontmatter = yaml.safe_load(frontmatter_text)
        if frontmatter["type"] not in {"event", "place"} or not frontmatter["sources"]:
            raise SystemExit(f"Card frontmatter failed validation: {path}")

    updates = {
        ALIGNMENT: encode_csv(alignment_fields, planned_alignment, alignment_bom),
        MANIFEST: encode_csv(manifest_fields, planned_manifest, manifest_bom),
        ACCEPTED: text_bytes(ACCEPTED, planned_accepted),
        RESULT: text_bytes(RESULT, result_text),
        KNOWLEDGE: text_bytes(KNOWLEDGE, process_text),
        **planned_card_bytes,
    }
    print("DRY-RUN" if args.dry_run else "APPLY")
    for path, content in updates.items():
        old_hash = digest(path.read_bytes()) if path.exists() else "absent"
        print(f"  {path.relative_to(ROOT)}: {old_hash} -> {digest(content)}")
    print("  groups=5; candidates=6; new cards=5; sources and bilingual descriptions checked")
    print(f"  S4: {before[0]:,} groups/{before[1]:,} mappings -> {after[0]:,}/{after[1]:,}; pending={after[2]:,} groups/{after[3]:,} mappings")
    print(f"  event: registered 10 -> 14 groups; place: registered 9 -> 10 groups; manifest={len(manifest_rows):,} -> {len(planned_manifest):,}")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backup_targets = [ALIGNMENT, MANIFEST, ACCEPTED, RESULT, KNOWLEDGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in backup_targets]
    existing = [path for path in backups if path.exists()]
    if existing:
        raise SystemExit(f"Recovery copy already exists: {existing[0]}")
    for original, backup in zip(backup_targets, backups):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s4-mazarin-registration-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied five S4 registrations and retained recovery copies.")


if __name__ == "__main__":
    main()
