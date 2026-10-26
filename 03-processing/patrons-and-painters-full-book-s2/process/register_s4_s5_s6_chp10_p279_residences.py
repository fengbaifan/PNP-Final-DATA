from __future__ import annotations

import argparse
import csv
import io
import json
import re
import shutil
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
TABLES = ROOT / "04-knowledge" / "tables"
DATE = "2026-10-26"
ANCHOR = "s3-s4-s5-s6-chp10-p279-residences-20261026"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
SEGMENT_ID = "chp-10:10_CHP-10_intro:l43-49"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

KU_DATA = [
    {
        "candidate_id": "cand-8884",
        "alignment_id": "aln-9057",
        "group": "sg3-place-cand-8884",
        "ku_id": "units/places/lord-manchester-arlington-street-residence",
        "card_path": "04-knowledge/units/places/lord-manchester-arlington-street-residence.md",
        "canonical_name": "曼彻斯特勋爵的阿灵顿街宅邸",
        "name_en": "Lord Manchester’s Arlington Street Residence",
        "title_zh": "曼彻斯特勋爵的阿灵顿街宅邸",
        "description_zh": (
            "哈斯克尔第10章 p.279 将其称为 Lord Manchester 位于 Arlington Street 的一处宅邸，"
            "并称 Pellegrini 与 Marco Ricci 受命装饰他的宅邸。原书没有给出正式建筑名或门牌；"
            "具体画家与宅邸的对应关系仍待证。"
        ),
        "description_en": (
            "In chapter 10, p. 279, Haskell refers to a residence of Lord Manchester on Arlington Street "
            "and says Pellegrini and Marco Ricci were set to decorate his mansions. The book gives no "
            "formal building name or street number; the artist-to-residence assignments remain unresolved."
        ),
        "quote": "decorate his mansions in Arlington Street and at Kimbolton in Huntingdonshire, rebuilt for him by Vanbrugh.1",
        "fields": [
            ("书中指称", "one of Lord Manchester’s mansions in Arlington Street", "S1"),
            ("对象类别", "residence / mansion; no formal building name or number is supplied", "S1"),
        ],
    },
    {
        "candidate_id": "cand-8885",
        "alignment_id": "aln-9058",
        "group": "sg3-place-cand-8885",
        "ku_id": "units/places/lord-manchester-kimbolton-residence",
        "card_path": "04-knowledge/units/places/lord-manchester-kimbolton-residence.md",
        "canonical_name": "曼彻斯特勋爵的金博尔顿宅邸",
        "name_en": "Lord Manchester’s Kimbolton Residence",
        "title_zh": "曼彻斯特勋爵的金博尔顿宅邸",
        "description_zh": (
            "哈斯克尔第10章 p.279 将其称为 Lord Manchester 位于 Huntingdonshire 金博尔顿的一处宅邸，"
            "并说 Vanbrugh 为他重建了该宅邸。原书未给正式建筑名或重建年份；本卡只指这处宅邸，"
            "不与金博尔顿城镇或两处宅邸的集合称呼合并。"
        ),
        "description_en": (
            "In chapter 10, p. 279, Haskell identifies a residence of Lord Manchester at Kimbolton in "
            "Huntingdonshire and says Vanbrugh rebuilt it for him. The book gives no formal building name "
            "or rebuilding date; this card represents that residence alone, not the town of Kimbolton or "
            "the collective reference to both mansions."
        ),
        "quote": "decorate his mansions in Arlington Street and at Kimbolton in Huntingdonshire, rebuilt for him by Vanbrugh.1",
        "fields": [
            ("书中指称", "a mansion of Lord Manchester at Kimbolton", "S1"),
            ("位置", "Kimbolton, Huntingdonshire", "S1"),
        ],
    },
    {
        "candidate_id": "cand-8890",
        "alignment_id": "aln-9063",
        "group": "sg3-place-cand-8890",
        "ku_id": "units/places/narford-hall",
        "card_path": "04-knowledge/units/places/narford-hall.md",
        "canonical_name": "纳福德堂",
        "name_en": "Narford Hall",
        "title_zh": "纳福德堂",
        "description_zh": (
            "哈斯克尔第10章 p.279 将 Narford Hall 称为 Sir Andrew Fountaine 的乡间居所，"
            "并把它记作 Pellegrini 与 Marco Ricci 从 Castle Howard 前往的地点。此卡保留书内地点身份和语境；"
            "不补写现存状态、精确位置或未由该段记载的建筑沿革。"
        ),
        "description_en": (
            "In chapter 10, p. 279, Haskell describes Narford Hall as Sir Andrew Fountaine’s country seat "
            "and as the destination to which Pellegrini and Marco Ricci moved from Castle Howard. This card "
            "preserves the place identity and context in the book; it adds no survival status, precise address, "
            "or building history absent from the passage."
        ),
        "quote": "the two Venetian artists who from Castle Howard then moved to Narford Hall in Norfolk, the country seat of the most interesting of all their English patrons, Sir Andrew Fountaine",
        "fields": [
            ("书中名称", "Narford Hall", "S1"),
            ("位置", "Norfolk", "S1"),
        ],
    },
]

NEW_STATEMENTS = [
    {
        "statement_id": "st-chp10-p279-arlington-mansion-owned-by-manchester",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-8884",
        "object_candidate_id": "cand-1504",
        "predicate": "haskell_identifies_arlington_street_residence_as_manchesters_mansion",
        "qualifiers": {
            "source_line_start": 44,
            "source_line_end": 44,
            "printed_page": 279,
            "pdf_physical_page": 4,
            "claim": "Haskell refers to the Arlington Street residence as one of Lord Manchester’s mansions.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "qualification": "The possessive referent is resolved from p.278, lines 40–41. This records Haskell’s source attribution; no independent legal title or ownership period is asserted.",
            "mentioned_candidate_ids": ["cand-1504", "cand-8884"],
            "relation_candidate": True,
            "cross_reference_segments": [{
                "segment_id": "chp-10:10_CHP-10_intro:l26-41",
                "source_line_start": 40,
                "source_line_end": 41,
            }],
        },
        "original_quote": "decorate his mansions in Arlington Street",
        "source_file": SOURCE_FILE,
        "origin": "book",
    },
    {
        "statement_id": "st-chp10-p279-kimbolton-mansion-owned-by-manchester",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-8885",
        "object_candidate_id": "cand-1504",
        "predicate": "haskell_identifies_kimbolton_residence_as_manchesters_mansion",
        "qualifiers": {
            "source_line_start": 44,
            "source_line_end": 44,
            "printed_page": 279,
            "pdf_physical_page": 4,
            "claim": "Haskell refers to the Kimbolton residence as one of Lord Manchester’s mansions.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "qualification": "The possessive referent is resolved from p.278, lines 40–41. This records Haskell’s source attribution; no independent legal title or ownership period is asserted.",
            "mentioned_candidate_ids": ["cand-1504", "cand-8885"],
            "relation_candidate": True,
            "cross_reference_segments": [{
                "segment_id": "chp-10:10_CHP-10_intro:l26-41",
                "source_line_start": 40,
                "source_line_end": 41,
            }],
        },
        "original_quote": "at Kimbolton in Huntingdonshire, rebuilt for him by Vanbrugh",
        "source_file": SOURCE_FILE,
        "origin": "book",
    },
    {
        "statement_id": "st-chp10-p279-kimbolton-residence-rebuilt-by-vanbrugh",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-8885",
        "object_candidate_id": "cand-2690",
        "predicate": "kimbolton_residence_rebuilt_by_vanbrugh_for_lord_manchester",
        "qualifiers": {
            "source_line_start": 44,
            "source_line_end": 44,
            "printed_page": 279,
            "pdf_physical_page": 4,
            "claim": "Haskell says Vanbrugh rebuilt Lord Manchester’s Kimbolton residence for him.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "qualification": "‘Him’ is Lord Manchester, resolved from p.278, lines 40–41. The claim concerns rebuilding, not original construction; no date is supplied.",
            "mentioned_candidate_ids": ["cand-1504", "cand-2690", "cand-8885"],
            "relation_candidate": True,
            "cross_reference_segments": [{
                "segment_id": "chp-10:10_CHP-10_intro:l26-41",
                "source_line_start": 40,
                "source_line_end": 41,
            }],
        },
        "original_quote": "at Kimbolton in Huntingdonshire, rebuilt for him by Vanbrugh",
        "source_file": SOURCE_FILE,
        "origin": "book",
    },
]

PENDING_STATEMENTS = {
    "st-chp10-p279-marco-ricci-manchester-decorate-mansions": (
        "process-only pending: the source jointly assigns the two named artists to two residences but does not specify artist-to-residence pairings or completed decoration; no controlled predicate captures this assignment without overclaiming."
    ),
    "st-chp10-p279-pellegrini-manchester-decorate-mansions": (
        "process-only pending: the source jointly assigns the two named artists to two residences but does not specify artist-to-residence pairings or completed decoration; no controlled predicate captures this assignment without overclaiming."
    ),
    "st-chp10-p279-both-artists-leave-england": (
        "process-only pending: ‘both left England’ is a group-level departure statement with unresolved temporal/location semantics; the source-local group is not a standalone KU and cand-4439 denotes England as a political realm in another context, so no formal edge is created here."
    ),
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool]:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader), has_bom


def csv_bytes(fieldnames: list[str], rows: list[dict[str, str]], has_bom: bool) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    payload = buffer.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" if has_bom else b"") + payload


def frontmatter(text: str) -> tuple[dict, str, str]:
    match = re.match(r"\A(?:\ufeff)?---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if not match:
        raise ValueError("card has invalid YAML frontmatter")
    data = yaml.safe_load(match.group(1)) or {}
    return data, match.group(0), text[match.end():]


def source_record(quote: str, span: str) -> dict:
    return {
        "citation": BOOK_CITATION,
        "location": "第10章，印刷页279，OCR L44–45，PDF物理页4",
        "sentence_summary": "Haskell identifies the residences and the artists’ movements in the p.279 narrative; the source-local scope and unresolved assignments are preserved.",
        "original_quotes": [{"source_span": span, "text": quote}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": SOURCE_FILE,
            "source_span": span,
        },
    }


def make_card(item: dict) -> str:
    source_span = "L44–45; print p.279; PDF physical p.4"
    fm = {
        "title": f"{item['title_zh']}（{item['name_en']}）",
        "name_en": item["name_en"],
        "type": "place",
        "evidence_status": "source_backed",
        "sources": [source_record(item["quote"], source_span)],
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    yaml_text = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000).rstrip()
    field_rows = "\n".join(f"| {field} | {value} | {evidence} |" for field, value, evidence in item["fields"])
    body = f"""## 内容

### 描述

**中文：** {item['description_zh']}

**English:** {item['description_en']}

### 名称与对象

| 字段 | 值 | 依据 |
|---|---|---|
{field_rows}

## 关系与证据

### 关系记录

书内正式关系由 `relations.csv` 维护并定向渲染；未映射的集合关系及其待证理由见过程记录。
"""
    return f"---\n{yaml_text}\n---\n\n{body}"


def update_castle_howard(text: str) -> str:
    fm, old_header, body = frontmatter(text)
    sources = fm.setdefault("sources", [])
    if any(source.get("citation") == BOOK_CITATION for source in sources if isinstance(source, dict)):
        raise ValueError("Castle Howard card already has the p.279 source")
    sources.append(source_record(
        "The same architect had for some years been erecting in Yorkshire a country house as palatial as any German imitation of Versailles for Lord Carlisle, a young man who had already embarked on a career to be more noted for its dazzling social prestige than for any real political achievement. He, too, extensively employed the two Venetian artists who from Castle Howard then moved to Narford Hall in Norfolk",
        "L44–45; print p.279; PDF physical p.4",
    ))
    yaml_text = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000).rstrip()
    row = "| 第10章地点身份 / Chapter 10 place identification | Haskell’s local narrative identifies the Yorkshire country house for Lord Carlisle as Castle Howard | S2 |"
    marker = "| 对象类别 | 乡间宅邸／Country house | S1 |"
    if marker not in body or row in body:
        raise ValueError("Castle Howard identity table does not match the reviewed baseline")
    body = body.replace(marker, marker + "\n" + row, 1)
    return f"---\n{yaml_text}\n---\n{body}"


def insert_accepted(text: str, card_paths: list[str]) -> str:
    lines = text.splitlines()
    for card_path in card_paths:
        line = f"- {card_path}"
        if line in lines:
            raise ValueError(f"accepted.yml already contains {card_path}")
        insert_at = next(
            (i for i, existing in enumerate(lines) if existing.startswith("- 04-knowledge/units/") and existing[2:] > card_path),
            next((i for i, existing in enumerate(lines) if existing == "claims:"), len(lines)),
        )
        lines.insert(insert_at, line)
    return "\n".join(lines) + "\n"


def add_statement_lines(path: Path, new_rows: list[dict]) -> bytes:
    original = path.read_bytes()
    original_text = original.decode("utf-8-sig")
    line_ending = "\r\n" if "\r\n" in original_text else "\n"
    existing_ids = {
        json.loads(line)["statement_id"]
        for line in original_text.splitlines()
        if line.strip()
    }
    overlap = existing_ids.intersection(row["statement_id"] for row in new_rows)
    if overlap:
        raise ValueError(f"statement IDs already exist: {sorted(overlap)}")
    base = original_text.rstrip("\r\n")
    added = line_ending.join(json.dumps(row, ensure_ascii=False) for row in new_rows)
    return (base + line_ending + added + line_ending).encode("utf-8")


def relation_specs() -> list[dict[str, str]]:
    return [
        {
            "subject_ku_id": "units/places/castle-howard",
            "object_ku_id": "units/persons/sir-john-vanbrugh",
            "predicate": "erected_by",
            "time": "Haskell p.279 says ‘for some years’; calendar years are not stated",
            "role": "builder",
            "scope": "Haskell says Vanbrugh had been erecting Lord Carlisle’s Yorkshire country house and then names Castle Howard as the artists’ point of departure. This records Haskell’s local identification; no construction dates or wider architectural history are inferred.",
            "statement_id": "st-chp10-p279-vanbrugh-carlisle-castle-howard",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "p.279, OCR L44; PDF physical p.4",
        },
        {
            "subject_ku_id": "units/persons/marco-ricci",
            "object_ku_id": "units/persons/earl-of-carlisle",
            "predicate": "employed_by",
            "time": "时间未载",
            "role": "artist",
            "scope": "Haskell says Lord Carlisle extensively employed Marco Ricci. Specific commissions, works, and dates are not supplied and are not inferred.",
            "statement_id": "st-chp10-p279-carlisle-employs-marco-ricci",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "p.279, OCR L44; PDF physical p.4",
        },
        {
            "subject_ku_id": "units/persons/pellegrini",
            "object_ku_id": "units/persons/earl-of-carlisle",
            "predicate": "employed_by",
            "time": "时间未载",
            "role": "artist",
            "scope": "Haskell says Lord Carlisle extensively employed Pellegrini. Specific commissions, works, and dates are not supplied and are not inferred.",
            "statement_id": "st-chp10-p279-carlisle-employs-pellegrini",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "p.279, OCR L44; PDF physical p.4",
        },
        {
            "subject_ku_id": "units/persons/marco-ricci",
            "object_ku_id": "units/places/castle-howard",
            "predicate": "located_at",
            "time": "时间未载；仅知来源叙述先后",
            "role": "reported point of departure",
            "scope": "Haskell says the two artists moved from Castle Howard to Narford Hall; Marco Ricci is one of the two artists named in the preceding p.278 context. The exact date and length of stay are not supplied.",
            "statement_id": "st-chp10-p279-venetian-artists-move-castle-howard-narford",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "p.279, OCR L44–45; PDF physical p.4",
        },
        {
            "subject_ku_id": "units/persons/marco-ricci",
            "object_ku_id": "units/places/narford-hall",
            "predicate": "located_at",
            "time": "时间未载；仅知来源叙述先后",
            "role": "reported destination of move",
            "scope": "Haskell says the two artists moved from Castle Howard to Narford Hall; Marco Ricci is one of the two artists named in the preceding p.278 context. This does not claim a date or permanent residence.",
            "statement_id": "st-chp10-p279-venetian-artists-move-castle-howard-narford",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "p.279, OCR L44–45; PDF physical p.4",
        },
        {
            "subject_ku_id": "units/persons/pellegrini",
            "object_ku_id": "units/places/castle-howard",
            "predicate": "located_at",
            "time": "时间未载；仅知来源叙述先后",
            "role": "reported point of departure",
            "scope": "Haskell says the two artists moved from Castle Howard to Narford Hall; Pellegrini is one of the two artists named in the preceding p.278 context. The exact date and length of stay are not supplied.",
            "statement_id": "st-chp10-p279-venetian-artists-move-castle-howard-narford",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "p.279, OCR L44–45; PDF physical p.4",
        },
        {
            "subject_ku_id": "units/persons/pellegrini",
            "object_ku_id": "units/places/narford-hall",
            "predicate": "located_at",
            "time": "时间未载；仅知来源叙述先后",
            "role": "reported destination of move",
            "scope": "Haskell says the two artists moved from Castle Howard to Narford Hall; Pellegrini is one of the two artists named in the preceding p.278 context. This does not claim a date or permanent residence.",
            "statement_id": "st-chp10-p279-venetian-artists-move-castle-howard-narford",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "p.279, OCR L44–45; PDF physical p.4",
        },
        {
            "subject_ku_id": "units/persons/andrew-fountaine",
            "object_ku_id": "units/places/narford-hall",
            "predicate": "located_at",
            "time": "时间未载",
            "role": "country seat, as described by Haskell",
            "scope": "Haskell calls Narford Hall the country seat of Sir Andrew Fountaine. This preserves the source-local relationship; it does not independently verify legal title or present-day use.",
            "statement_id": "st-chp10-p279-narford-seat-fountaine",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "p.279, OCR L45–46; PDF physical p.4",
        },
        {
            "subject_ku_id": "units/places/lord-manchester-arlington-street-residence",
            "object_ku_id": "units/persons/charles-montagu-first-duke-of-manchester",
            "predicate": "owned_by",
            "time": "时间未载",
            "role": "owner as identified by Haskell’s possessive wording",
            "scope": "Haskell refers to this as one of Lord Manchester’s mansions; p.278 resolves the possessive referent to Charles Montagu. This records the book’s attribution only, without an independently verified legal title or ownership period.",
            "statement_id": "st-chp10-p279-arlington-mansion-owned-by-manchester",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "p.279, OCR L44, read with p.278 L40–41; PDF physical p.4",
        },
        {
            "subject_ku_id": "units/places/lord-manchester-kimbolton-residence",
            "object_ku_id": "units/persons/charles-montagu-first-duke-of-manchester",
            "predicate": "owned_by",
            "time": "时间未载",
            "role": "owner as identified by Haskell’s possessive wording",
            "scope": "Haskell refers to this as one of Lord Manchester’s mansions; p.278 resolves the possessive referent to Charles Montagu. This records the book’s attribution only, without an independently verified legal title or ownership period.",
            "statement_id": "st-chp10-p279-kimbolton-mansion-owned-by-manchester",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "p.279, OCR L44, read with p.278 L40–41; PDF physical p.4",
        },
        {
            "subject_ku_id": "units/places/lord-manchester-kimbolton-residence",
            "object_ku_id": "units/persons/sir-john-vanbrugh",
            "predicate": "erected_by",
            "time": "时间未载",
            "role": "rebuilder",
            "scope": "Haskell says the Kimbolton residence was rebuilt for Lord Manchester by Vanbrugh. This records rebuilding only, not the original construction; no date is supplied.",
            "statement_id": "st-chp10-p279-kimbolton-residence-rebuilt-by-vanbrugh",
            "source_id": "haskell-1980-rev-ed",
            "source_span": "p.279, OCR L44; PDF physical p.4",
        },
    ]


def build_plan() -> tuple[dict[Path, bytes], dict[str, str], list[str]]:
    paths = {
        "alignment": TABLES / "alignment.csv",
        "candidates": TABLES / "entity-candidates.csv",
        "manifest": TABLES / "ku-manifest.csv",
        "relations": TABLES / "relations.csv",
        "sources": TABLES / "sources.csv",
        "statements": TABLES / "book-statements.jsonl",
        "accepted": ROOT / "04-knowledge" / "accepted.yml",
        "castle": ROOT / "04-knowledge" / "units" / "places" / "castle-howard.md",
        "process": PROCESS_DIR / "knowledge.md",
    }
    tables: dict[str, tuple[list[str], list[dict[str, str]], bool]] = {
        key: read_csv(paths[key]) for key in ("alignment", "candidates", "manifest", "relations", "sources")
    }
    alignment_fields, alignments, alignment_bom = tables["alignment"]
    candidate_fields, candidates, candidate_bom = tables["candidates"]
    manifest_fields, manifest, manifest_bom = tables["manifest"]
    relation_fields, relations, relation_bom = tables["relations"]
    _, source_rows, _ = tables["sources"]
    source_ids = {row["source_id"] for row in source_rows}

    alignment_by_candidate = {row["candidate_id"]: row for row in alignments}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    manifest_ids = {row["ku_id"] for row in manifest}
    expected = {item["candidate_id"] for item in KU_DATA} | {"cand-8888", "cand-8891", "cand-8902"}
    if not expected.issubset(alignment_by_candidate) or not expected.issubset(candidate_by_id):
        raise ValueError("required S3 candidates are missing")
    for item in KU_DATA:
        row = alignment_by_candidate[item["candidate_id"]]
        if row["decision"] != "new" or row["ku_id"]:
            raise ValueError(f"{item['candidate_id']} is no longer an unmapped new candidate")
        if item["ku_id"] in manifest_ids or (ROOT / item["card_path"]).exists():
            raise ValueError(f"new KU path already exists: {item['ku_id']}")
    if alignment_by_candidate["cand-8888"]["decision"] != "new":
        raise ValueError("cand-8888 baseline decision changed")
    if alignment_by_candidate["cand-8891"]["decision"] != "new":
        raise ValueError("cand-8891 baseline decision changed")
    if alignment_by_candidate["cand-8902"]["decision"] != "new":
        raise ValueError("cand-8902 baseline decision changed")
    if f"{PROCESS_REF}" in paths["process"].read_text(encoding="utf-8-sig"):
        raise ValueError("batch anchor already exists")

    added_relation_ids: dict[str, str] = {}
    next_relation_number = max(int(row["relation_id"].split("-")[1]) for row in relations) + 1
    planned_relation_rows = []
    natural_keys = {
        (row["subject_ku_id"], row["object_ku_id"], row["predicate"], row["source_id"])
        for row in relations
    }
    for offset, spec in enumerate(relation_specs()):
        relation_id = f"rel-{next_relation_number + offset:04d}"
        key = (spec["subject_ku_id"], spec["object_ku_id"], spec["predicate"], spec["source_id"])
        if key in natural_keys:
            raise ValueError(f"duplicate relation natural key: {key}")
        natural_keys.add(key)
        added_relation_ids[f"{spec['statement_id']}|{spec['subject_ku_id']}|{spec['object_ku_id']}|{spec['predicate']}"] = relation_id
        planned_relation_rows.append({
            "relation_id": relation_id,
            **spec,
            "origin": "book",
            "status": "formal",
            "source_file": SOURCE_FILE,
            "note": f"S2 statement={spec['statement_id']}",
        })
    relations.extend(planned_relation_rows)

    for item in KU_DATA:
        row = alignment_by_candidate[item["candidate_id"]]
        row["ku_id"] = item["ku_id"]
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"group={item['group']}; source_ref=chp-10:10_CHP-10_intro:l43-49#L44-45; "
            f"S4 registration ({DATE}) maps this source-limited place group to {item['ku_id']}. "
            "No formal building title, exact street number, or current survival status is added."
        )

    castle_row = alignment_by_candidate["cand-8888"]
    castle_row["decision"] = "same"
    castle_row["ku_id"] = "units/places/castle-howard"
    castle_row["process_ref"] = PROCESS_REF
    castle_row["resolution_note"] = (
        "prior_decision=new (S3-full-book-2026-10-15); S3 identity review triggered by the p.279 S4 mapping. "
        "Haskell describes Vanbrugh’s Yorkshire country house for Lord Carlisle and, in the same sentence, "
        "names Castle Howard as the artists’ point of departure; this is the existing exact place KU "
        "units/places/castle-howard, so reuse it rather than create a second Castle Howard."
    )
    candidate_by_id["cand-8888"]["detail"] = (
        "The p.279 local narrative identifies the country house being erected for Lord Carlisle as Castle Howard; "
        "S3 now maps this candidate to the existing Castle Howard place KU."
    )

    for candidate_id, reason in {
        "cand-8891": (
            "S3 identity/type review triggered by registering its two constituent places. The phrase refers "
            "collectively to the Arlington Street and Kimbolton residences, not to one independent place; "
            "cand-8884 and cand-8885 are registered separately. No aggregate place KU is created."
        ),
        "cand-8902": (
            "S3 type review triggered by S4 endpoint registration. ‘The two Venetian artists’ is a source-local "
            "collective reference to the already mapped persons Pellegrini and Marco Ricci, not an independent "
            "term or entity under the current taxonomy. The Narford movement is represented through the two "
            "named person KUs; the separate ‘both left England’ candidate remains process-only pending."
        ),
    }.items():
        row = alignment_by_candidate[candidate_id]
        row["decision"] = "excluded"
        row["ku_id"] = ""
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = reason
        candidate = candidate_by_id[candidate_id]
        candidate["status"] = "excluded"
        candidate["exclude_reason"] = reason

    new_manifest_rows = [{
        "ku_id": item["ku_id"],
        "type": "place",
        "canonical_name": item["canonical_name"],
        "name_en": item["name_en"],
        "source_task": TASK,
        "card_path": item["card_path"],
    } for item in KU_DATA]
    manifest.extend(new_manifest_rows)

    existing_statement_ids = set()
    existing_statements = {}
    statement_path = paths["statements"]
    for line in statement_path.read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            statement = json.loads(line)
            existing_statement_ids.add(statement["statement_id"])
            existing_statements[statement["statement_id"]] = statement
    if existing_statement_ids.intersection(row["statement_id"] for row in NEW_STATEMENTS):
        raise ValueError("one or more S2 statement IDs already exist")
    all_candidate_ids = set(candidate_by_id)
    for statement in NEW_STATEMENTS:
        for candidate_id in (
            statement["subject_candidate_id"],
            statement["object_candidate_id"],
            *statement["qualifiers"]["mentioned_candidate_ids"],
        ):
            if candidate_id not in all_candidate_ids:
                raise ValueError(f"{statement['statement_id']} references unknown candidate {candidate_id}")
    source_statement_ids = set(existing_statements) | {row["statement_id"] for row in NEW_STATEMENTS}
    planned_ku_ids = manifest_ids | {item["ku_id"] for item in KU_DATA}
    for relation in planned_relation_rows:
        if relation["statement_id"] not in source_statement_ids:
            raise ValueError(f"relation cites unknown S2 statement {relation['statement_id']}")
        if relation["source_id"] not in source_ids:
            raise ValueError(f"relation cites unregistered source {relation['source_id']}")
        if relation["subject_ku_id"] not in planned_ku_ids or relation["object_ku_id"] not in planned_ku_ids:
            raise ValueError(f"relation has an unregistered KU endpoint: {relation}")

    accepted_path = paths["accepted"]
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")
    updated_accepted = insert_accepted(accepted_text, [item["card_path"] for item in KU_DATA])

    castle_text = paths["castle"].read_bytes().decode("utf-8")
    updated_castle = update_castle_howard(castle_text)

    process_path = paths["process"]
    process_text = process_path.read_bytes().decode("utf-8-sig").rstrip()
    id_by_source = {}
    for row in planned_relation_rows:
        id_by_source.setdefault(row["statement_id"], []).append(row["relation_id"])
    formal_list = []
    for source_id, ids in id_by_source.items():
        formal_list.append(f"- `{source_id}`：formal，`{', '.join(ids)}`。")
    pending_list = [f"- `{statement_id}`：{reason}" for statement_id, reason in PENDING_STATEMENTS.items()]
    process_entry = f"""

<a id="{ANCHOR}"></a>

### S3–S6：第10章 p.279 住所、Castle Howard 与 Narford Hall 端点（{DATE}）

#### S3 身份去向

- `cand-8888`：因本批 S4 登记触发身份复核。Haskell先称 Vanbrugh 为 Lord Carlisle 在 Yorkshire 营建乡间宅邸，紧接着写两位画家从 Castle Howard 前往 Narford Hall；结合同句语境，该候选复用既有 [Castle Howard](../../../04-knowledge/units/places/castle-howard.md)，由 `new` 改为 `same`，不重复建卡。
- `cand-8884`、`cand-8885`、`cand-8890`：沿用既有 `new` 组，分别登记阿灵顿街宅邸、金博尔顿宅邸和 Narford Hall。
- `cand-8891`：改为 `excluded`。它是两处住所的集合称呼，不是单一建筑；两个组成地点分别保留为 `cand-8884`、`cand-8885`。
- `cand-8902`：改为 `excluded`。‘the two Venetian artists’指 Pellegrini 和 Marco Ricci 的集合称呼，不是独立术语或实体；两人的移动关系通过既有人物 KU 记录。‘Both left England’仍保留为一个未正式映射的 S2 关系候选，理由见下。

#### S4 / S5 登记与来源字段

新增三个来源限定地点 KU：

- [曼彻斯特勋爵的阿灵顿街宅邸](../../../04-knowledge/units/places/lord-manchester-arlington-street-residence.md)（`cand-8884`）
- [曼彻斯特勋爵的金博尔顿宅邸](../../../04-knowledge/units/places/lord-manchester-kimbolton-residence.md)（`cand-8885`）
- [纳福德堂（Narford Hall）](../../../04-knowledge/units/places/narford-hall.md)（`cand-8890`）

Castle Howard 卡补入第10章 p.279 的身份依据。七条新增字段限定名称、对象性质和原文所给地点；不补写精确门牌、现存状态或未给出的建造年代。Vanbrugh 重建 Kimbolton 宅邸及两处宅邸归 Lord Manchester 的断言只限于 Haskell 的 possessive / rebuilding 表述。

#### S6 逐项裁决

**formal：**
{chr(10).join(formal_list)}

两名画家从 Castle Howard 前往 Narford Hall 的复数表述拆解为 Marco Ricci 与 Pellegrini 各自的出发地点、到达地点四条 `located_at` 边；来源不提供迁移年份或停留时长。Carlisle 对两人的一般雇佣关系使用受控类型 `employed_by`，不附会具体合同、作品或日期。两处住所的 `owned_by` 只记录 Haskell 的‘his mansions’说法，不宣称另有产权文书。

**process-only pending：**
{chr(10).join(pending_list)}

以上三项不写入 `relations.csv`，因为当前受控关系表不能在不猜测艺术家与具体住所配对、完工状态或离英事件端点的情况下忠实表达。无正式边不否定原书说法。

S2 新增三条 statement（两处宅邸的 source-local possessive attribution、一条 Vanbrugh 重建）；没有新增 mention，且未计入统一 S2 独立复核分子。第10章 p.279 其余正文未在本批宣称完成独立语义接收。
""".strip()
    if ANCHOR in process_text:
        raise ValueError("process anchor already exists")
    process_text += "\n\n" + process_entry + "\n"

    planned: dict[Path, bytes] = {
        paths["alignment"]: csv_bytes(alignment_fields, alignments, alignment_bom),
        paths["candidates"]: csv_bytes(candidate_fields, candidates, candidate_bom),
        paths["manifest"]: csv_bytes(manifest_fields, manifest, manifest_bom),
        paths["relations"]: csv_bytes(relation_fields, relations, relation_bom),
        paths["statements"]: add_statement_lines(statement_path, NEW_STATEMENTS),
        accepted_path: updated_accepted.encode("utf-8"),
        paths["castle"]: (b"\xef\xbb\xbf" if paths["castle"].read_bytes().startswith(b"\xef\xbb\xbf") else b"") + updated_castle.encode("utf-8"),
        process_path: (b"\xef\xbb\xbf" if process_path.read_bytes().startswith(b"\xef\xbb\xbf") else b"") + process_text.encode("utf-8"),
    }
    for item in KU_DATA:
        planned[ROOT / item["card_path"]] = b"\xef\xbb\xbf" + make_card(item).encode("utf-8")

    summaries = {
        "S4_KUs": ", ".join(item["ku_id"] for item in KU_DATA),
        "new_statements": ", ".join(row["statement_id"] for row in NEW_STATEMENTS),
        "new_relation_ids": ", ".join(row["relation_id"] for row in planned_relation_rows),
        "pending": "; ".join(f"{key}: {value}" for key, value in PENDING_STATEMENTS.items()),
    }
    return planned, summaries, [str(path.relative_to(ROOT)) for path in planned]


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the p.279 residence endpoint batch across S3–S6.")
    parser.add_argument("--apply", action="store_true", help="write after reviewing the default read-only plan")
    args = parser.parse_args()
    planned, summaries, paths = build_plan()
    print(f"mode={'apply' if args.apply else 'dry-run'}; planned files={len(planned)}")
    print("S3: cand-8888 new→same Castle Howard; cand-8891 and cand-8902 new→excluded with reasons")
    print(f"S4 KUs: {summaries['S4_KUs']}")
    print(f"S2 statements: {summaries['new_statements']}")
    print(f"Formal relation rows: {summaries['new_relation_ids']}")
    print(f"Process-only pending: {summaries['pending']}")
    print("Planned paths:")
    for path in paths:
        print(f"  {path}")
    if not args.apply:
        return 0

    backup_dir = Path(tempfile.mkdtemp(prefix="pnp-ch10-p279-recovery-"))
    for path in planned:
        if path.exists():
            relative = path.relative_to(ROOT)
            backup_path = backup_dir / relative
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup_path)
    print(f"Recovery copies: {backup_dir}")
    for path, payload in planned.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + ".p279.tmp")
        temporary.write_bytes(payload)
        temporary.replace(path)
    print("applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
