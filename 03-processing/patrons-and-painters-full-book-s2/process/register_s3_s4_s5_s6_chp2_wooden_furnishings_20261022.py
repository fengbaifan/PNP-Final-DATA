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
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(ROOT))
import scripts.build_field_facts as field_facts

TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
RELATIONS = TABLES / "relations.csv"
ENRICHMENT = TABLES / "enrichment.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
AGENTS = ROOT / "AGENTS.md"
SOURCE_FILE = "02-sources/02-Markdown/02_CHP-2_sec_ii.md"
SOURCE_ID = "haskell-1980-rev-ed"
DATE = "2026-10-22"
ANCHOR = "s4-s5-s6-chp2-wooden-candlesticks-crucifixes-20261022"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

ITEMS = [
    {
        "candidate_id": "cand-4537",
        "group": "workgrp-f8ffd77be43521",
        "ku_id": "units/works/dozen-wooden-candlesticks",
        "card_path": "04-knowledge/units/works/dozen-wooden-candlesticks.md",
        "canonical_name": "Dozen wooden candlesticks sent to S. Maria della Concezione",
        "title": "十二支木制烛台（A Dozen Wooden Candlesticks）",
        "name_en": "A Dozen Wooden Candlesticks",
        "object_type": "一组木制烛台；来源未给出独立正式题名",
        "quantity": "12支",
        "description_zh": (
            "Haskell记载，枢机S. Onofrio订置一打木制烛台并送到该教堂。"
            "Capuchin修士将烛台退回；随后Urban VIII坚持接收，原文称烛台被接受。"
            "接受不证明完成安装或现存地点；本书此处未给制造者或独立正式题名。"
        ),
        "description_en": (
            "Haskell reports that Cardinal S. Onofrio ordered a dozen wooden candlesticks "
            "and sent them to the church. The Capuchin monks returned the candlesticks; "
            "Urban VIII then insisted, and the text says they were accepted. Acceptance "
            "does not establish installation or a present location. This passage gives no maker or formal individual title."
        ),
        "formal_statement": "st-chp2-secii-l141-145-s-onofrio-orders-candlesticks",
        "return_statement": "st-chp2-secii-l141-145-capuchin-reject-and-return-wooden-furnishings",
        "acceptance_statement": "st-chp2-secii-l141-145-urban-insists-candlesticks-accepted",
        "relation_id": "rel-1390",
    },
    {
        "candidate_id": "cand-4538",
        "group": "workgrp-93d64b0d557676",
        "ku_id": "units/works/two-wooden-crucifixes",
        "card_path": "04-knowledge/units/works/two-wooden-crucifixes.md",
        "canonical_name": "Two wooden crucifixes sent to S. Maria della Concezione",
        "title": "两件木制十字架（Two Wooden Crucifixes）",
        "name_en": "Two Wooden Crucifixes",
        "object_type": "一组木制十字架；来源未给出独立正式题名",
        "quantity": "2件",
        "description_zh": (
            "Haskell在同一句中记载枢机S. Onofrio订置十二支烛台和两件木制十字架，"
            "并将它们送往该教堂。Capuchin修士将物件退回。后文只明确烛台被接受，"
            "没有说明十字架后续去向；不推定其制造者、安装或现存地点。"
        ),
        "description_en": (
            "In the same sentence, Haskell reports that Cardinal S. Onofrio ordered "
            "a dozen candlesticks and two wooden crucifixes and sent them to the church. "
            "The Capuchin monks returned the objects. The later acceptance is stated only "
            "for the candlesticks; the passage does not give the crucifixes' later location. "
            "No maker, installation, or present location is inferred."
        ),
        "formal_statement": "st-chp2-secii-l141-145-s-onofrio-orders-crucifixes",
        "return_statement": "st-chp2-secii-l141-145-capuchin-return-crucifixes",
        "acceptance_statement": "",
        "relation_id": "rel-1391",
    },
]

QUOTE_REPLACEMENTS = {
    "st-chp2-secii-l141-145-s-onofrio-orders-candlesticks": (
        "Cardinal S. Onofrio ordered a dozen candlesticks and two crucifixes, all of wood, and sent them to the church."
    ),
    "st-chp2-secii-l141-145-s-onofrio-orders-crucifixes": (
        "Cardinal S. Onofrio ordered a dozen candlesticks and two crucifixes, all of wood, and sent them to the church."
    ),
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    old = path.read_bytes() if path.exists() else b""
    encoding = "utf-8-sig" if old.startswith(b"\xef\xbb\xbf") else "utf-8"
    newline = "\r\n" if b"\r\n" in old else "\n"
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding=encoding, newline="") as handle:
        handle.write(text.replace("\n", newline))
    temp.replace(path)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    old = path.read_bytes()
    encoding = "utf-8-sig" if old.startswith(b"\xef\xbb\xbf") else "utf-8"
    newline = "\r\n" if b"\r\n" in old else "\n"
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding=encoding, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator=newline)
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(path)


def make_card(item: dict) -> str:
    is_candlesticks = item["candidate_id"] == "cand-4537"
    source_quotes = [
        {
            "source_span": "L131; printed p. 43; PDF physical p. 28",
            "text": (
                "The strange confusions inherent in Urban VIII’s patronage of religious foundations "
                "are even more obvious in his dealings with the church of S. Maria della Concezione."
            ),
        },
        {
            "source_span": "L143; printed p. 43; PDF physical p. 28",
            "text": QUOTE_REPLACEMENTS[item["formal_statement"]],
        },
        {
            "source_span": "L143; printed p. 43; PDF physical p. 28",
            "text": "they sent them back.",
        },
    ]
    if is_candlesticks:
        source_quotes.append(
            {
                "source_span": "L143; printed p. 43; PDF physical p. 28",
                "text": "The Pope insisted; and the candlesticks were accepted.",
            }
        )
    frontmatter = {
        "title": item["title"],
        "name_en": item["name_en"],
        "type": "work",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第二章；印刷页43；Markdown L131、L143；PDF物理页28。",
                "sentence_summary": (
                    "Haskell称该教堂为S. Maria della Concezione，并记枢机S. Onofrio订置并送达木制陈设；"
                    "Capuchin修士退回物件，后文只明确烛台在Urban VIII坚持后被接受。"
                ),
                "original_quotes": source_quotes,
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": "L131、L143；printed p. 43; PDF physical p. 28",
                },
            }
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    frontmatter_text = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=110)
    basics = [
        ("作品类型", item["object_type"]),
        ("数量", item["quantity"]),
        ("材质", "木"),
    ]
    basic_rows = "\n".join(
        f"| {field} | {value} | S1；Haskell第2章，印刷页43，L143。 |"
        for field, value in basics
    )
    if is_candlesticks:
        relation_text = (
            "- S6待证：Capuchin修士退回该组烛台，以及Urban VIII坚持后烛台被接受；两项事实暂缺准确的受控关系谓词，未生成正式边。"
        )
    else:
        relation_text = (
            "- S6待证：Capuchin修士退回这组十字架；当前关系类型不能准确表达该次退还，未生成正式边。"
        )
    body = f"""## 内容

### 描述

**中文：** {item['description_zh']}

**English:** {item['description_en']}

### 基本信息

| 字段 | 值 | 依据 |
|---|---|---|
{basic_rows}

## 关系与证据

### 关系记录

{relation_text}

逐条裁决和待证理由见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})；本书来源见[第二章原文](../../../02-sources/02-Markdown/02_CHP-2_sec_ii.md#L143)。
"""
    return "---\n" + frontmatter_text + "---\n\n" + body


def extract_fields(card_texts: dict[str, str], planned_manifest: list[dict[str, str]]) -> list[dict]:
    old_base = field_facts.BASE
    with tempfile.TemporaryDirectory(prefix="pnp-chp2-wooden-furnishings-") as temp_name:
        field_facts.BASE = Path(temp_name)
        for item in ITEMS:
            path = field_facts.BASE / item["card_path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(card_texts[item["ku_id"]], encoding="utf-8", newline="\n")
        try:
            rows, _, warnings, count = field_facts.extract_records(
                [row for row in planned_manifest if row["ku_id"] in {item["ku_id"] for item in ITEMS}]
            )
        finally:
            field_facts.BASE = old_base
    assert not warnings, warnings
    assert count == 2 and len(rows) == 6, (count, len(rows))
    assert all(row["source_ids"] == [SOURCE_ID] for row in rows)
    assert all(row["evidence_status"] == "source_backed" and row["origin"] == "book" for row in rows)
    field_facts.assign_ids(rows, ENRICHMENT)
    return rows


def update_jsonl_quotes(path: Path, targets: dict[str, str]) -> tuple[str, int]:
    raw = path.read_bytes()
    encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
    text = raw.decode(encoding)
    newline = "\n"
    lines = text.splitlines()
    seen: set[str] = set()
    output: list[str] = []
    for line in lines:
        if not line.strip():
            output.append(line)
            continue
        record = json.loads(line)
        statement_id = record.get("statement_id", "")
        if statement_id in targets:
            expected = "Cardinal S. Onofrio ordered a dozen candlesticks and two crucifixes, all of wood, and sent them to"
            assert record.get("original_quote") == expected, (statement_id, record.get("original_quote"))
            record["original_quote"] = targets[statement_id]
            seen.add(statement_id)
            output.append(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
        else:
            output.append(line)
    assert seen == set(targets), (seen, set(targets))
    return newline.join(output) + newline, len(seen)


def add_accepted_entries(text: str, paths: list[str]) -> str:
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    assert lines and lines[0].strip() == "units:"
    current = [line[2:].strip() for line in lines[1:] if line.startswith("- ")]
    assert not any(path in current for path in paths)
    index = max(i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/")) + 1
    for path in sorted(paths):
        lines.insert(index, f"- {path}")
        index += 1
    return newline.join(lines) + newline


def build_process_entry(fields: list[dict]) -> str:
    field_rows = "\n".join(
        f"| {row['ku_id']} | {row['field']} | {row['value']} | {row['evidence']} |"
        for row in fields
    )
    return f"""<a id="{ANCHOR}"></a>
### S2引文修订与S4/S5/S6：木制烛台、十字架端点批次（{DATE}）

**S2定点修订。** 第2章印刷页43、PDF物理页28的独立复核发现，两条Cardinal S. Onofrio订置物件的statement引文都截断在“sent them to”，未包括原文“the church”。已将 `st-chp2-secii-l141-145-s-onofrio-orders-candlesticks` 与 `st-chp2-secii-l141-145-s-onofrio-orders-crucifixes` 的 `original_quote` 延伸至完整句末“the church”。来源L143逐字支持新跨度；不新增或删除statement，不改变S2统一复核分子。该段此前的逐条复核记录见[s2-independent-review-chp1-2-4-20261020.md](s2-independent-review-chp1-2-4-20261020.md)。

**S3/S4登记。** 未重开S3。保留现有两个互相区分的 `new` 身份组：`{ITEMS[0]['group']}` → `{ITEMS[0]['ku_id']}`（`cand-4537`，十二支烛台）与 `{ITEMS[1]['group']}` → `{ITEMS[1]['ku_id']}`（`cand-4538`，两件十字架）。两个组均只含本组候选；不把同句出现的两个对象合并。新卡仅记录Haskell支持的对象类别、数量、材质和上下文，不补创作者、独立题名、安装状态或现存地点。

**S5字段。** 每张卡新增作品类型、数量、材质三项字段。字段均由Haskell第2章L143直接支持；书内送达、退回及烛台获接收的信息在卡内按来源限定描述，不作为所有权、安装或现存地点字段。

| KU | 字段 | 值 | 证据 |
|---|---|---|---|
{field_rows}

**S6逐条裁决。** 两条“Cardinal S. Onofrio订置并送达”的候选裁为formal `supplied_by`，方向为作品→提供者；原文明确其订置并发送两组物件，但不据此推定制造者或创作者。三条退还／接收候选裁为pending：Haskell明确记载这些事件，但受控关系类型没有准确表达“退还”或“坚持接收”的谓词；`held_by`会错误表示当前保管，`owned_by`会错误表示所有权。没有为这些事件生成正式边。

| S2 statement | S6决定 | 正式关系／待证理由 |
|---|---|---|
| `{ITEMS[0]['formal_statement']}` | formal | `{ITEMS[0]['relation_id']}`，作品→Cardinal Antonio Barberini，`supplied_by`。 |
| `{ITEMS[1]['formal_statement']}` | formal | `{ITEMS[1]['relation_id']}`，作品→Cardinal Antonio Barberini，`supplied_by`。 |
| `{ITEMS[0]['return_statement']}` | pending | Capuchin修士退回烛台；当前没有准确的退还谓词，且不表示现有保管。 |
| `{ITEMS[1]['return_statement']}` | pending | Capuchin修士退回十字架；当前没有准确的退还谓词，且不表示现有保管。 |
| `{ITEMS[0]['acceptance_statement']}` | pending | Urban VIII坚持后烛台被接受；当前没有准确的接收／施压谓词，不推定所有权或安装。 |

正式边来源均为 `{SOURCE_ID}`，Haskell第2章L143、印刷页43（PDF物理页28）。只记录书中报告；不表示另行查阅了引文所述的原始账目或档案。

**本批后状态变化：** S4新增2组、2条候选映射；S5新增6条source-backed字段；S6新增5条逐项裁决（2 formal、3 pending），relations.csv新增2条formal `supplied_by`。全书S2计数不变，S3决定行及各类身份决定不变。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register two source-backed direct work endpoints and their itemized S6 decisions.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment_rows = read_csv(ALIGNMENT)
    candidate_fields, candidate_rows = read_csv(CANDIDATES)
    manifest_fields, manifest_rows = read_csv(MANIFEST)
    relation_fields, relation_rows = read_csv(RELATIONS)
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    manifest_by_id = {row["ku_id"]: row for row in manifest_rows}
    alignment_by_candidate: dict[str, dict] = {}
    for row in alignment_rows:
        if not row.get("external_source"):
            candidate_id = row.get("candidate_id", "")
            assert candidate_id not in alignment_by_candidate, f"duplicate main alignment row: {candidate_id}"
            alignment_by_candidate[candidate_id] = row

    process_text = read_text(PROCESS)
    result_text = read_text(RESULT)
    agents_text = read_text(AGENTS)
    accepted_text = read_text(ACCEPTED)
    source_text = read_text(ROOT / SOURCE_FILE)
    assert SOURCE_ID in {row["source_id"] for row in read_csv(TABLES / "sources.csv")[1]}
    assert "the church of S. Maria della Concezione" in source_text
    assert "Cardinal S. Onofrio ordered a dozen candlesticks and two crucifixes, all of wood, and sent them to the church." in source_text
    assert ANCHOR not in process_text and ANCHOR not in result_text
    assert "## 当前全书阶段总览（2026-10-22）" in result_text
    assert "S4已登记1,388/4,789组、1,595/5,017条候选映射" in agents_text
    assert "S4：** 已登记1,388/4,789组、1,595/5,017条候选映射" in result_text
    assert "S6逐项裁决累计逐条裁决248/10,417" not in result_text
    assert len([row for row in relation_rows if row["status"] == "formal"]) == 1386
    assert len([row for row in relation_rows if row["status"] == "pending"]) == 3
    assert sum(1 for line in read_text(ENRICHMENT).splitlines() if line.strip()) == 12024

    for item in ITEMS:
        candidate = candidate_by_id[item["candidate_id"]]
        align = alignment_by_candidate[item["candidate_id"]]
        assert candidate["suggested_type"] == "work", candidate
        assert align["decision"] == "new" and not align["ku_id"], align
        assert f"group={item['group']}" in align["resolution_note"]
        assert item["ku_id"] not in manifest_by_id
        assert not (ROOT / item["card_path"]).exists()
        assert not any(row["card_path"] == item["card_path"] for row in manifest_rows)
        assert item["card_path"] not in accepted_text

    statement_rows = [json.loads(line) for line in read_text(STATEMENTS).splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statement_rows}
    expected_endpoints = {
        ITEMS[0]["formal_statement"]: ("cand-0186", "cand-4537"),
        ITEMS[1]["formal_statement"]: ("cand-0186", "cand-4538"),
        ITEMS[0]["return_statement"]: ("cand-3405", "cand-4537"),
        ITEMS[1]["return_statement"]: ("cand-3405", "cand-4538"),
        ITEMS[0]["acceptance_statement"]: ("cand-0213", "cand-4537"),
    }
    for statement_id, endpoints in expected_endpoints.items():
        statement = statement_by_id[statement_id]
        assert statement["qualifiers"].get("relation_candidate") is True, statement_id
        assert (statement["subject_candidate_id"], statement["object_candidate_id"]) == endpoints
        assert statement["source_file"] == SOURCE_FILE
        assert statement_id not in process_text, f"S6 candidate already itemized: {statement_id}"
    for candidate_id, ku_id in {
        "cand-0186": "units/persons/antonio-barberini",
        "cand-0213": "units/persons/urbano-viii",
        "cand-3405": "units/institutions/capuchins",
    }.items():
        assert alignment_by_candidate[candidate_id]["ku_id"] == ku_id
        assert ku_id in manifest_by_id

    updated_statements, quote_count = update_jsonl_quotes(STATEMENTS, QUOTE_REPLACEMENTS)
    assert quote_count == 2
    for statement_id, quote in QUOTE_REPLACEMENTS.items():
        assert statement_by_id[statement_id]["original_quote"].endswith("sent them to")
        assert quote in source_text

    # The formal predicate is supported by the recorded act of ordering and sending.
    with (ROOT / "01-domain" / "relation-domain-range.yml").open("r", encoding="utf-8") as handle:
        domain_range = yaml.safe_load(handle)["domain_range"]
    assert "work" in domain_range["supplied_by"]["domain"]
    assert "person" in domain_range["supplied_by"]["range"]
    for item in ITEMS:
        assert manifest_by_id["units/persons/antonio-barberini"]["type"] == "person"

    card_texts = {item["ku_id"]: make_card(item) for item in ITEMS}
    planned_alignment = [dict(row) for row in alignment_rows]
    planned_manifest = [dict(row) for row in manifest_rows]
    planned_relations = [dict(row) for row in relation_rows]
    for item in ITEMS:
        align = next(row for row in planned_alignment if row["candidate_id"] == item["candidate_id"] and not row.get("external_source"))
        align["ku_id"] = item["ku_id"]
        align["process_ref"] = PROCESS_REF
        align["resolution_note"] += f" S4 registration 2026-10-22: {item['group']} mapped to {item['ku_id']} from Haskell ch. 2 p. 43 L143; the descriptive unit remains distinct from the paired object group."
        planned_manifest.append({
            "ku_id": item["ku_id"],
            "type": "work",
            "canonical_name": item["canonical_name"],
            "name_en": item["name_en"],
            "source_task": TASK,
            "card_path": item["card_path"],
        })

    new_fields = extract_fields(card_texts, planned_manifest)
    assert len(new_fields) == 6

    endpoints = {
        "units/persons/antonio-barberini": {"type": "person"},
    }
    relation_rows_new = []
    for item in ITEMS:
        natural_key = (item["ku_id"], "supplied_by", "units/persons/antonio-barberini", "")
        assert not any((r["subject_ku_id"], r["predicate"], r["object_ku_id"], r["time"]) == natural_key for r in relation_rows)
        relation_rows_new.append({
            "relation_id": item["relation_id"],
            "subject_ku_id": item["ku_id"],
            "object_ku_id": "units/persons/antonio-barberini",
            "predicate": "supplied_by",
            "time": "",
            "role": "Haskell所述订置并送达该组物件的提供者",
            "scope": "Haskell称Cardinal S. Onofrio订置并将物件送往the church；只记录来源所述的提供关系，不推定制造者、创作者或安装状态。",
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": "L143; printed p. 43; PDF physical p. 28",
            "source_file": SOURCE_FILE,
            "note": f"S2 statement: {item['formal_statement']}",
        })
    planned_relations.extend(relation_rows_new)

    new_accepted = add_accepted_entries(accepted_text, [item["card_path"] for item in ITEMS])
    current_enrichment = read_text(ENRICHMENT)
    additions = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in new_fields)
    planned_enrichment = current_enrichment.rstrip("\r\n") + "\n" + additions + "\n"

    process_entry = build_process_entry(new_fields)
    planned_process = process_text.rstrip() + "\n\n" + process_entry

    def replace_once(text: str, old: str, new: str, label: str) -> str:
        assert text.count(old) == 1, f"expected one {label}; found {text.count(old)}"
        return text.replace(old, new, 1)

    planned_result = result_text.replace(
        "## 当前全书阶段总览（2026-10-22）",
        f"""### S2/S4/S5/S6：第2章木制烛台与十字架直接端点（2026-10-22）

第2章印刷页43、PDF物理页28的独立复核指出，两条Cardinal S. Onofrio订置陈设的statement引文截断于“sent them to”。已修正两条 `original_quote`，纳入来源L143中的“the church”；不增删statement，不改变S2统一复核计数。保留现有S3新组，分别登记十二支木制烛台和两件木制十字架，未重开S3。两张卡各新增三条直接有据的S5字段（类型、数量、材质）。

S6逐项裁决五条候选：两条订置并送达候选以作品→提供者 `supplied_by` 裁为formal（rel-1390、rel-1391）；Capuchin修士退回两组物件的两条候选，以及Urban VIII坚持接收烛台的一条候选均裁为pending。来源虽然支持退还／接收事件，但当前受控谓词不能准确表达这些事实；不以`held_by`或`owned_by`替代。逐条理由见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。

## 当前全书阶段总览（2026-10-22）""",
        1,
    )
    planned_result = replace_once(
        planned_result,
        "- **S4：** 已登记1,388/4,789组、1,595/5,017条候选映射；待登记3,401组／3,422条映射，直接端点1,656组／1,671条组成员映射。",
        "- **S4：** 已登记1,390/4,789组、1,597/5,017条候选映射；待登记3,399组／3,420条映射，其中直接关系端点1,654组／1,669条组成员映射，非直接1,745组／1,751条。",
        "result S4 snapshot",
    )
    planned_result = replace_once(
        planned_result,
        "- **S5：** 字段表12,024条，其中1,634条为 unverified；未核字段按证据逐项处理。",
        "- **S5：** 字段表12,030条，其中1,634条为 unverified；本批新增6条source-backed字段。",
        "result S5 snapshot",
    )
    planned_result = replace_once(
        planned_result,
        "- **S6：** 关系表1,389条（1,386 formal、3 pending）；过程记录累计逐条裁决248/10,417条S2关系候选（168 formal、66 pending、14 rejected），其余10,169条待逐项裁决。",
        "- **S6：** 关系表1,391条（1,388 formal、3 pending）；过程记录累计逐条裁决253/10,417条S2关系候选（170 formal、69 pending、14 rejected），其余10,164条待逐项裁决。",
        "result S6 snapshot",
    )
    old_plan = "- **后续顺序：** ① 先逐项补齐20条缺少alignment裁决的候选（person 16、archive 2、institution 2），根据来源和跨章身份证据写入same/new/conflict/excluded/undecided及理由；不按类型或姓名默认决定。② 复核622条类型未定候选与9条冲突，再按类型进行全书跨章分组，建议先person、work、archive，再term、place、institution、event、family、procedure；每项明确复用对象、新身份组、冲突处置、排除依据或待证条件。③ S4按正式关系端点及证据完整度登记直接端点（当前1,657组／1,672条成员映射），逐批与S6候选裁决联动；pending/rejected保留理由。④ S2从第七章p.202复合脚注 `chp-7:07_CHP-7_sec_v:l62-76` 继续，再完成本章余下140条和第八章余下975条；之后按章节推进，并以statement ID核对第3章及第10–12章的独立复核是否并入口径。⑤ S5优先处理直接关系端点卡的关键字段，再按证据处理余下1,634条unverified字段；S6先裁S4直接端点，再按章节／关系类型分批处理剩余10,174条。S2尚未独立验收、S3尚有缺行／未决、S4–S6未收口；完成相应门禁后再准备S7。知识发现与页面仍等待用户明确启动。"
    new_plan = "- **后续顺序：** ① 按关系解锁价值和证据完整度批次登记S4直接端点，并在同批逐条完成相应S6裁决；谓词不准确时保留pending。② 为已登记端点补入来源明确的S5关键字段。③ 按证据追踪335条缺少S2端点ID的关系候选；具名端点通过candidate-backlog按S1→S3→S4处理，端点未就绪的边保持pending。④ 继续分章S2独立语义审读和问题修订，并按statement ID核对独立复核记录，不自动合并不同口径。⑤ 仅当登记或新证据触发时定点重开S3，不批量重复既有决定。⑥ 直接端点完成后继续非直接S4、S5未验证字段和其余S6候选。满足S2独立验收与S3–S6收口门槛后准备S7；知识发现与页面仍等待用户明确启动。"
    planned_result = replace_once(planned_result, old_plan, new_plan, "result next-step plan")

    old_s4_agents = "S4已登记1,388/4,789组、1,595/5,017条候选映射；待登记3,401组／3,422条映射，其中直接关系端点1,656组／1,671条组成员映射，非直接1,745组／1,751条。"
    new_s4_agents = "S4已登记1,390/4,789组、1,597/5,017条候选映射；待登记3,399组／3,420条映射，其中直接关系端点1,654组／1,669条组成员映射，非直接1,745组／1,751条。"
    planned_agents = replace_once(agents_text, old_s4_agents, new_s4_agents, "AGENTS S4 snapshot")
    planned_agents = replace_once(planned_agents, "S5字段表12,024条、其中1,634条unverified。", "S5字段表12,030条、其中1,634条unverified。", "AGENTS S5 snapshot")
    planned_agents = replace_once(
        planned_agents,
        "S6关系表1,389条（1,386 formal、3 pending），过程记录累计逐条裁决248/10,417条S2关系候选（168 formal、66 pending、14 rejected）；其余10,169条待逐项裁决，全部关系均有结构化source_id。",
        "S6关系表1,391条（1,388 formal、3 pending），过程记录累计逐条裁决253/10,417条S2关系候选（170 formal、69 pending、14 rejected）；其余10,164条待逐项裁决，全部关系均有结构化source_id。",
        "AGENTS S6 snapshot",
    )

    planned_candidates = list(candidate_rows)
    planned_statements = updated_statements
    print("candidate groups: 2 new work groups, both mapped to new KU cards")
    print("S2 quote corrections: 2; statements added or removed: 0")
    print("S5 fields: 6 source-backed; formal S6 edges: 2 supplied_by")
    print("S6 itemized decisions: 5 (2 formal, 3 pending)")
    print("expected snapshot: S4 registered 1390/4789 groups; S6 253/10417 decisions")
    if args.dry_run:
        print("dry-run passed: group membership, source spans, endpoint mappings, type range, and staged counts verified")
        return 0

    write_text(STATEMENTS, planned_statements)
    for item in ITEMS:
        write_text(ROOT / item["card_path"], card_texts[item["ku_id"]])
    write_csv(ALIGNMENT, alignment_fields, planned_alignment)
    write_csv(MANIFEST, manifest_fields, planned_manifest)
    write_csv(RELATIONS, relation_fields, planned_relations)
    write_text(ENRICHMENT, planned_enrichment)
    write_text(ACCEPTED, new_accepted)
    write_text(PROCESS, planned_process)
    write_text(RESULT, planned_result.rstrip() + "\n")
    write_text(AGENTS, planned_agents)
    print("applied S2/S4/S5/S6 batch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
