from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.build_field_facts import assign_ids, extract_records  # noqa: E402

TABLES = ROOT / "04-knowledge" / "tables"
SOURCE_FILE = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
SOURCE_ID = "haskell-1980-rev-ed"
PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md"
    "#s3-s4-s5-s6-ch7-richelieu-policy-death-20261023"
)
ANCHOR = "s3-s4-s5-s6-ch7-richelieu-policy-death-20261023"

RICHELIEU = "units/persons/armand-jean-du-plessis-de-richelieu"
POLICY_CANDIDATE = "cand-2190"
POLICY_ALIGNMENT = "aln-2525"
POLICY_KU = "units/events/richelieu-attempt-to-recruit-italian-artists-paris"
POLICY_CARD = "04-knowledge/units/events/richelieu-attempt-to-recruit-italian-artists-paris.md"

DEATH_CANDIDATE = "cand-12433"
DEATH_ALIGNMENT = "aln-12724"
DEATH_GROUP = "sg3-event-richelieu-death-1642"
DEATH_KU = "units/events/death-of-cardinal-richelieu-haskell-1642"
DEATH_CARD = "04-knowledge/units/events/death-of-cardinal-richelieu-haskell-1642.md"

CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged edition "
    "(Yale University Press, 1980; this printing 2006)."
)

POLICY_CARD_TEXT = f'''---
title: "黎塞留招揽意大利艺术家赴巴黎的尝试（Richelieu's Attempt to Bring Leading Italian Artists to Paris）"
name_en: "Richelieu's Attempt to Bring Leading Italian Artists to Paris"
type: event
evidence_status: source_backed
sources:
  - citation: "{CITATION}"
    location: "Chapter 7, printed p. 175, line 70; PDF physical p. 9"
    sentence_summary: "Haskell says Richelieu began a policy of trying to bring leading artists from south of the Alps to Paris during the last years of his life."
    original_quotes:
      - source_span: "Chapter 7, printed p. 175, line 70"
        text: "during the last few years of his life he suddenly embarked on a new policy of trying to bring to Paris all the leading artists south of the Alps"
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: {SOURCE_FILE}
      source_span: "Chapter 7, printed p. 175, line 70; PDF physical p. 9"
  - citation: "{CITATION}"
    location: "Chapter 7, printed p. 176, lines 87–88; PDF physical p. 10"
    sentence_summary: "Haskell says Richelieu's death did not interrupt French plans and reports that the Surintendant informed an unnamed artist group that they continued."
    original_quotes:
      - source_span: "Chapter 7, printed p. 176, lines 87–88"
        text: "Richelieu's death in no way interfered with French plans"
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: {SOURCE_FILE}
      source_span: "Chapter 7, printed p. 176, lines 87–88; PDF physical p. 10"
created: '2026-10-23'
updated: '2026-10-23'
process_ref: {PROCESS_REF}
---

## 内容

### 描述

**中文：** 哈斯克尔称，黎塞留在生命最后几年开始一项新政策，试图把阿尔卑斯山以南的主要艺术家招至巴黎。本知识元记录的是原文所述招揽政策的启动与尝试，不表示目标艺术家实际迁往巴黎或接受法国委托。第7章 p.176 又称黎塞留去世没有中断法国方面的计划；该说法保留为哈斯克尔对计划延续的叙述，不据此推断具体成果。

**English:** Haskell says that, during the last few years of his life, Richelieu began a new policy of trying to bring the leading artists south of the Alps to Paris. This unit records the source-described launch and attempt, not an actual relocation or acceptance of French commissions. Chapter 7, p. 176 adds that Richelieu's death did not interrupt French plans; this remains Haskell's account of continuity and does not establish a specific outcome.

### 事件信息

| 项目 | 内容 | 依据 |
|---|---|---|
| 性质 | 黎塞留启动招揽意大利艺术家赴巴黎的尝试政策；尝试不等于实际迁居 | S1；第7章 p. 175 L70 |
| 时间 | 黎塞留生命最后几年；本段未给出确切起始年份 | S1；第7章 p. 175 L70 |
| 行动者与目标 | 行动者为黎塞留；目标被称作阿尔卑斯山以南的主要艺术家，未在本句逐一列名 | S1；第7章 p. 175 L70 |
| 计划延续 | 哈斯克尔称黎塞留去世没有中断法国计划；不据此断言所有计划均执行或成功 | S1；第7章 p. 176 L87–88 |

## 关系与证据

### 关系记录

本事件身份依据 Haskell 第7章 p.175–176 的来源局部叙述。招揽目标群的边界仍待 S3，政策事件与目标群之间也没有精确的受控关系谓词；裁决见[全书过程记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR})。
'''

DEATH_CARD_TEXT = f'''---
title: "黎塞留之死（哈斯克尔记于1642年）（Death of Richelieu (dated 1642 by Haskell)）"
name_en: "Death of Richelieu (dated 1642 by Haskell)"
type: event
evidence_status: source_backed
sources:
  - citation: "{CITATION}"
    location: "Chapter 7, printed p. 176, line 87; PDF physical p. 10"
    sentence_summary: "Haskell refers to Richelieu's death when describing the continuation of French artist-recruitment plans."
    original_quotes:
      - source_span: "Chapter 7, printed p. 176, line 87"
        text: "Richelieu's death in no way interfered with French plans"
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: {SOURCE_FILE}
      source_span: "Chapter 7, printed p. 176, line 87; PDF physical p. 10"
  - citation: "{CITATION}"
    location: "Chapter 7, printed p. 180, line 130; PDF physical p. 14"
    sentence_summary: "Haskell dates Richelieu's death to 1642 in the account of Mazarin taking over the government of France."
    original_quotes:
      - source_span: "Chapter 7, printed p. 180, line 130"
        text: "immediately on the death of Richelieu in 1642"
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: {SOURCE_FILE}
      source_span: "Chapter 7, printed p. 180, line 130; PDF physical p. 14"
created: '2026-10-23'
updated: '2026-10-23'
process_ref: {PROCESS_REF}
---

## 内容

### 描述

**中文：** 本知识元记录哈斯克尔所述黎塞留之死这一事件。哈斯克尔在第7章 p.180 将其记于1642年；此处只记录来源所报日期，不表示本轮另行核实该日期。第7章 p.176 还以该事件为时间背景叙述法国招揽艺术家计划的延续，但不因此推断死亡事件导致了该延续。

**English:** This unit records the death of Richelieu as an event reported by Haskell. On Chapter 7, p. 180, Haskell dates it to 1642; this records the source's date and does not claim independent verification. Chapter 7, p. 176 also uses the event as temporal context for the continuation of French artist-recruitment plans, without implying that the death caused that continuation.

### 事件信息

| 项目 | 内容 | 依据 |
|---|---|---|
| 性质 | 黎塞留之死；此处按哈斯克尔的来源叙述登记为独立事件 | S1；第7章 p. 176 L87、p. 180 L130 |
| 时间 | 1642年（哈斯克尔在第7章 p.180 的记载） | S1；第7章 p. 180 L130 |
| 时间语境 | 第7章 p.176 称其去世未中断法国招揽艺术家的计划；不将时间先后改写为因果关系 | S1；第7章 p. 176 L87 |

## 关系与证据

### 关系记录

事件与黎塞留人物 KU 的参与者关系依据 Haskell 对“Richelieu's death”的直接表述；关系范围限于该事件所指逝者。事件与招揽政策的负向延续关系仍 pending，见[全书过程记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR})。
'''


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool, str]:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader.fieldnames or []), list(reader), bom, newline


def render_csv(fields: list[str], rows: list[dict[str, str]], bom: bool, newline: str) -> bytes:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + handle.getvalue().encode("utf-8")


def render_jsonl(rows: list[dict], newline: str = "\n") -> bytes:
    return "".join(json.dumps(row, ensure_ascii=False) + newline for row in rows).encode("utf-8")


def atomic_write(path: Path, payload: bytes) -> None:
    temporary = path.with_name(path.name + ".codex-tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def accepted_with(card_paths: list[str]) -> bytes:
    path = ROOT / "04-knowledge" / "accepted.yml"
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "units:":
        raise ValueError("accepted.yml does not begin with units:")
    existing = {line.strip()[2:].strip() for line in lines if line.lstrip().startswith("-")}
    for card_path in card_paths:
        if card_path in existing:
            raise ValueError(f"accepted.yml already contains {card_path}")
        insert_at = next(
            (i for i, line in enumerate(lines) if line.lstrip().startswith("-") and line.strip()[2:].strip() > card_path),
            next((i for i, line in enumerate(lines) if line.strip() == "claims:"), len(lines)),
        )
        lines.insert(insert_at, f"- {card_path}{newline}")
        existing.add(card_path)
    return (b"\xef\xbb\xbf" if bom else b"") + "".join(lines).encode("utf-8")


def add_ids(values: list[str], *new_ids: str) -> list[str]:
    result = list(values)
    for value in new_ids:
        if value not in result:
            result.append(value)
    return result


def build_plan() -> tuple[dict[Path, bytes], dict[str, int], list[str]]:
    plans: dict[Path, bytes] = {}
    checks: list[str] = []

    candidate_path = TABLES / "entity-candidates.csv"
    c_fields, candidates, c_bom, c_eol = read_csv(candidate_path)
    if any(row["candidate_id"] == DEATH_CANDIDATE for row in candidates):
        raise ValueError(f"{DEATH_CANDIDATE} already exists")
    if any(row["card_path"] in {POLICY_CARD, DEATH_CARD} for row in read_csv(TABLES / "ku-manifest.csv")[1]):
        raise ValueError("one of the planned event card paths is already registered")

    candidate_numbers = [int(m.group(1)) for row in candidates if (m := re.fullmatch(r"cand-(\d+)", row["candidate_id"]))]
    if max(candidate_numbers, default=0) != 12432:
        raise ValueError("candidate ID baseline changed; re-plan the new candidate ID")
    candidates.append({
        "candidate_id": DEATH_CANDIDATE,
        "index_entry_id": "",
        "canonical_name": "Death of Cardinal Richelieu (dated 1642 by Haskell)",
        "index_page_range": "",
        "suggested_type": "event",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell refers to Richelieu's death on p.176 and dates it to 1642 on p.180. This is the death event, distinct from the person candidate cand-2189; the exact day and place are not supplied here.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-7:07_CHP-7_sec_i:l76-89#L87",
    })
    plans[candidate_path] = render_csv(c_fields, candidates, c_bom, c_eol)

    alignment_path = TABLES / "alignment.csv"
    a_fields, alignments, a_bom, a_eol = read_csv(alignment_path)
    if any(row["alignment_id"] == DEATH_ALIGNMENT for row in alignments):
        raise ValueError(f"{DEATH_ALIGNMENT} already exists")
    alignment_numbers = [int(m.group(1)) for row in alignments if (m := re.fullmatch(r"aln-(\d+)", row["alignment_id"]))]
    if max(alignment_numbers, default=0) != 12723:
        raise ValueError("alignment ID baseline changed; re-plan the new alignment ID")
    policy_rows = [row for row in alignments if row["candidate_id"] == POLICY_CANDIDATE and not row["external_source"]]
    if len(policy_rows) != 1 or policy_rows[0]["alignment_id"] != POLICY_ALIGNMENT or policy_rows[0]["decision"] != "new" or policy_rows[0]["ku_id"]:
        raise ValueError("Richelieu policy event S3 row changed; re-review before registration")
    policy_rows[0]["ku_id"] = POLICY_KU
    policy_rows[0]["process_ref"] = PROCESS_REF
    policy_rows[0]["resolution_note"] += (
        f" S4: registered this source-described policy-launch event as {POLICY_KU}; "
        "kept distinct from Mazarin's specific 1644 Bernini recruitment attempt and the separate 1648 Algardi attempt."
    )
    alignments.append({
        "alignment_id": DEATH_ALIGNMENT,
        "candidate_id": DEATH_CANDIDATE,
        "ku_id": DEATH_KU,
        "external_source": "",
        "external_id": "",
        "decision": "new",
        "accessed_date": "",
        "process_ref": PROCESS_REF,
        "legacy_ku_id": "",
        "resolution_note": (
            f"group={DEATH_GROUP}; source_refs=chp-7:07_CHP-7_sec_i:l76-89#L87,"
            "chp-7:07_CHP-7_sec_i:l128-138#L130; S3 source-level identity decision: "
            "the explicit references to Richelieu's death on pp.176 and 180 refer to the same event, "
            "not to the person candidate cand-2189. Haskell reports 1642 on p.180; no exact day or place is stated. "
            "No external event identifier is applicable or claimed. S4 registered the event to " + DEATH_KU + "."
        ),
    })
    plans[alignment_path] = render_csv(a_fields, alignments, a_bom, a_eol)

    statement_path = TABLES / "book-statements.jsonl"
    statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statements}
    required = {
        "st-chp7-p175-i21",
        "st-chp7-p175-i29",
        "st-chp7-p176-i26",
        "st-chp7-p176-i27",
        "st-chp7-p176-i28",
        "st-chp7-p180-i03",
    }
    if not required.issubset(statement_by_id):
        raise ValueError("one or more expected source statements are missing")
    if "st-chp7-p180-richelieu-death-event-person" in statement_by_id:
        raise ValueError("planned death-participant statement already exists")
    i21 = statement_by_id["st-chp7-p175-i21"]
    if i21["qualifiers"].get("relation_candidate") is not False or i21.get("subject_candidate_id") != "cand-2189" or i21.get("object_candidate_id") != "cand-1631":
        raise ValueError("p.175 i21 no longer matches the reviewed statement")
    i21["qualifiers"]["relation_candidate"] = True
    i21["qualifiers"]["relation_candidate_note"] = (
        "This records Haskell's explicit description of Richelieu as Marie de Medici's minister. "
        "Keep the role source-limited; the controlled relation vocabulary has no exact ministerial-role predicate."
    )
    i27 = statement_by_id["st-chp7-p176-i27"]
    if i27.get("subject_candidate_id") != "cand-2189" or i27.get("object_candidate_id") != POLICY_CANDIDATE:
        raise ValueError("p.176 i27 endpoints changed; re-review the source claim")
    i27["subject_candidate_id"] = DEATH_CANDIDATE
    i27["qualifiers"]["mentioned_candidate_ids"] = add_ids(
        i27["qualifiers"].get("mentioned_candidate_ids", []), DEATH_CANDIDATE, "cand-2189"
    )
    i27["qualifiers"]["relation_candidate_note"] = (
        "This records Haskell's negative continuity claim: Richelieu's death did not interrupt French artist-recruitment plans. "
        "The subject is the death event, not the person; no positive causal influence is inferred."
    )
    i26 = statement_by_id["st-chp7-p176-i26"]
    i26["qualifiers"]["mentioned_candidate_ids"] = add_ids(
        i26["qualifiers"].get("mentioned_candidate_ids", []), DEATH_CANDIDATE
    )
    i28 = statement_by_id["st-chp7-p176-i28"]
    i28["qualifiers"]["mentioned_candidate_ids"] = add_ids(
        i28["qualifiers"].get("mentioned_candidate_ids", []), DEATH_CANDIDATE
    )
    p180 = statement_by_id["st-chp7-p180-i03"]
    p180["qualifiers"]["mentioned_candidate_ids"] = add_ids(
        p180["qualifiers"].get("mentioned_candidate_ids", []), DEATH_CANDIDATE
    )
    new_death_participant_statement = {
        "statement_id": "st-chp7-p180-richelieu-death-event-person",
        "segment_id": "chp-7:07_CHP-7_sec_i:l128-138",
        "subject_candidate_id": DEATH_CANDIDATE,
        "object_candidate_id": "cand-2189",
        "predicate": "has_participant",
        "qualifiers": {
            "source_line_start": 130,
            "source_line_end": 130,
            "printed_page": 180,
            "pdf_physical_page": 14,
            "claim": "Haskell identifies Cardinal Richelieu as the person whose death he dates to 1642.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "qualification": "This records the source-reported event/person identity and date; it supplies no exact day or place and is not independent verification of the date.",
            "mentioned_candidate_ids": [DEATH_CANDIDATE, "cand-2189"],
            "relation_candidate": True,
            "relation_candidate_note": "Haskell's phrase 'the death of Richelieu in 1642' directly supports the event's decedent; the event and person remain distinct KU types.",
        },
        "original_quote": "the death of Richelieu in 1642",
        "origin": "book",
        "source_file": SOURCE_FILE,
    }
    statements.append(new_death_participant_statement)
    plans[statement_path] = render_jsonl(statements)

    mention_path = TABLES / "mentions.csv"
    m_fields, mentions, m_bom, m_eol = read_csv(mention_path)
    old_death_mention = next((row for row in mentions if row["mention_id"] == "m-chp7-p176-b-068"), None)
    if not old_death_mention or old_death_mention["candidate_id"] != "cand-2189" or old_death_mention["surface_form"] != "Richelieu’s death":
        raise ValueError("the p.176 Richelieu-death mention changed; re-review the anchor")
    old_death_mention["candidate_id"] = DEATH_CANDIDATE
    old_death_mention["note"] = "Richelieu's death event; distinct from person candidate cand-2189."
    for mention_id in ["m-chp7-p176-b-088", "m-chp7-p180-b-079"]:
        if any(row["mention_id"] == mention_id for row in mentions):
            raise ValueError(f"planned mention ID {mention_id} already exists")
    mentions.extend([
        {
            "mention_id": "m-chp7-p176-b-088",
            "segment_id": "chp-7:07_CHP-7_sec_i:l76-89",
            "candidate_id": DEATH_CANDIDATE,
            "surface_form": "the death of its subject",
            "start_char": "2464",
            "end_char": "2488",
            "note": "The Richelieu bust's subject; this is the death event, used only as a relative time reference."
        },
        {
            "mention_id": "m-chp7-p180-b-079",
            "segment_id": "chp-7:07_CHP-7_sec_i:l128-138",
            "candidate_id": DEATH_CANDIDATE,
            "surface_form": "death of Richelieu in 1642",
            "start_char": "585",
            "end_char": "611",
            "note": "Haskell's explicit cross-reference to the same death event; p.180 supplies the source-reported year 1642."
        },
    ])
    source_lines = (ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").splitlines()
    for start, end, phrase, expected in [
        (76, 89, "the death of its subject", (2464, 2488)),
        (128, 138, "death of Richelieu in 1642", (585, 611)),
    ]:
        segment_text = "\n".join(source_lines[start - 1:end])
        actual = segment_text.find(phrase)
        if (actual, actual + len(phrase)) != expected:
            raise ValueError(f"mention span mismatch for {phrase}: {(actual, actual + len(phrase))}")
    plans[mention_path] = render_csv(m_fields, mentions, m_bom, m_eol)

    manifest_path = TABLES / "ku-manifest.csv"
    k_fields, manifest, k_bom, k_eol = read_csv(manifest_path)
    for ku_id in [POLICY_KU, DEATH_KU]:
        if any(row["ku_id"] == ku_id for row in manifest):
            raise ValueError(f"{ku_id} already exists in ku-manifest.csv")
    if any(row["name_en"].casefold() == "richelieu's attempt to bring leading italian artists to paris" for row in manifest):
        raise ValueError("a same-title policy event already exists")
    if any(row["name_en"].casefold() == "death of richelieu (dated 1642 by haskell)" for row in manifest):
        raise ValueError("a same-title Richelieu death event already exists")
    manifest.extend([
        {
            "ku_id": POLICY_KU,
            "type": "event",
            "canonical_name": "黎塞留招揽意大利艺术家赴巴黎的尝试",
            "name_en": "Richelieu's Attempt to Bring Leading Italian Artists to Paris",
            "source_task": "patrons-and-painters-full-book-s2",
            "card_path": POLICY_CARD,
        },
        {
            "ku_id": DEATH_KU,
            "type": "event",
            "canonical_name": "黎塞留之死（哈斯克尔记于1642年）",
            "name_en": "Death of Richelieu (dated 1642 by Haskell)",
            "source_task": "patrons-and-painters-full-book-s2",
            "card_path": DEATH_CARD,
        },
    ])
    plans[manifest_path] = render_csv(k_fields, manifest, k_bom, k_eol)
    plans[ROOT / POLICY_CARD] = POLICY_CARD_TEXT.encode("utf-8")
    plans[ROOT / DEATH_CARD] = DEATH_CARD_TEXT.encode("utf-8")
    plans[ROOT / "04-knowledge" / "accepted.yml"] = accepted_with([POLICY_CARD, DEATH_CARD])

    for phrase in ["new policy of trying to bring", "Richelieu’s death in no way interfered", "death of Richelieu in 1642"]:
        if phrase not in "\n".join(source_lines):
            raise ValueError(f"expected source wording not found: {phrase}")

    enrichment_path = TABLES / "enrichment.jsonl"
    existing_enrichment = [json.loads(line) for line in enrichment_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    preview_cards = [(POLICY_CARD, POLICY_CARD_TEXT), (DEATH_CARD, DEATH_CARD_TEXT)]
    extracted: list[dict] = []
    all_sources: set[str] = set()
    warnings: list[str] = []
    tables_seen = 0
    for card_path, card_text in preview_cards:
        preview_path = ROOT / (card_path + ".preview")
        if preview_path.exists():
            raise FileExistsError(f"refusing to overwrite an existing preview file: {preview_path}")
        try:
            preview_path.write_text(card_text, encoding="utf-8", newline="\n")
            additions, source_registry, card_warnings, cards_with_tables = extract_records(
                [{"ku_id": POLICY_KU if card_path == POLICY_CARD else DEATH_KU, "card_path": card_path + ".preview"}]
            )
        finally:
            preview_path.unlink(missing_ok=True)
        if cards_with_tables != 1:
            raise ValueError(f"expected one source table in {card_path}, found {cards_with_tables}")
        tables_seen += cards_with_tables
        extracted.extend(additions)
        all_sources.update(source_registry)
        warnings.extend(card_warnings)
    if warnings or all_sources != {SOURCE_ID} or len(extracted) < 6:
        raise ValueError(f"field extraction check failed: sources={all_sources}, rows={len(extracted)}, warnings={warnings}")
    assign_ids(extracted, enrichment_path)
    old_occurrences = {row.get("occurrence_id") for row in existing_enrichment}
    if any(row.get("occurrence_id") in old_occurrences for row in extracted):
        raise ValueError("a new S5 row duplicates an existing occurrence")
    plans[enrichment_path] = enrichment_path.read_bytes() + render_jsonl(extracted)

    relations_path = TABLES / "relations.csv"
    r_fields, relations, r_bom, r_eol = read_csv(relations_path)
    relation_numbers = [int(m.group(1)) for row in relations if (m := re.fullmatch(r"rel-(\d+)", row["relation_id"]))]
    if max(relation_numbers, default=0) != 1602:
        raise ValueError("relation ID baseline changed; re-plan relation ID")
    relation = {
        "relation_id": "rel-1603",
        "subject_ku_id": DEATH_KU,
        "object_ku_id": RICHELIEU,
        "predicate": "has_participant",
        "time": "1642",
        "role": "逝者",
        "scope": "Haskell identifies Cardinal Richelieu as the person whose death he dates to 1642. This edge records only the person/event identity and source-reported year; no exact day, place, or cause is asserted.",
        "origin": "book",
        "status": "formal",
        "source_id": SOURCE_ID,
        "source_span": "Chapter 7, printed p. 180, line 130; PDF physical p. 14; statement=st-chp7-p180-richelieu-death-event-person",
        "source_file": SOURCE_FILE,
        "note": "The event KU is distinct from Richelieu's person KU; 1642 is Haskell's date, not an independently verified date.",
    }
    if any(
        row["subject_ku_id"] == relation["subject_ku_id"]
        and row["predicate"] == relation["predicate"]
        and row["object_ku_id"] == relation["object_ku_id"]
        and row["time"] == relation["time"]
        and row["scope"] == relation["scope"]
        for row in relations
    ):
        raise ValueError("a natural-key duplicate event/person relation already exists")
    vocab = yaml.safe_load((ROOT / ".agents" / "skills" / "ingest" / "references" / "relation-types.yml").read_text(encoding="utf-8"))
    matrix = yaml.safe_load((ROOT / "01-domain" / "relation-domain-range.yml").read_text(encoding="utf-8"))["domain_range"]
    if relation["predicate"] not in vocab["types"]:
        raise ValueError("has_participant is not a controlled relation type")
    types = {row["ku_id"]: row["type"] for row in manifest}
    allowed = matrix[relation["predicate"]]
    if types.get(DEATH_KU) not in allowed["domain"] or types.get(RICHELIEU) not in allowed["range"]:
        raise ValueError("event/person endpoints do not satisfy the relation domain/range")
    relations.append(relation)
    plans[relations_path] = render_csv(r_fields, relations, r_bom, r_eol)

    knowledge_path = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
    knowledge = knowledge_path.read_text(encoding="utf-8-sig")
    if ANCHOR in knowledge:
        raise ValueError("process anchor already exists")
    enrichment_ids = [row["enrichment_id"] for row in extracted]
    batch_record = f'''\n\n<a id="{ANCHOR}"></a>

### S2定向修订／S3／S4／S5／S6：第七章黎塞留招揽政策与死亡事件（2026-10-23）

**S2修订与来源边界。** 接续 `process/stages.md` 的第七章 p.175–176 独立核读问题：`st-chp7-p175-i21` 原标 `relation_candidate=false`，但原句 “her minister, Cardinal Richelieu” 明确断言人物角色，已改为 `true`；`st-chp7-p176-i27` 的主语原映射到人物 `cand-2189`，扫描与 S0 均明确写的是 “Richelieu’s death”，现将主语改为独立事件候选 `{DEATH_CANDIDATE}`。新增 `st-chp7-p180-richelieu-death-event-person`，将 p.180 对 “the death of Richelieu in 1642” 的明文定位转成事件—逝者候选。新增/修订不计入 S2 独立复核分子；p.181 将黎塞留与路易十三之死及马萨林艺术抱负合并的 statement 仍待单独原子化，未视作已解决。

**S3跨段身份与S4登记。** `cand-2190` 沿用 S3 `new` 身份组 `sg3-event-cand-2190`，登记为 `{POLICY_KU}`。事件粒度限于 Haskell 所述黎塞留在生命最后几年启动的招揽政策尝试；不与马萨林 1644 年招揽贝尔尼尼、1648 年招揽阿尔加迪两次具体行动合并。新增 `{DEATH_CANDIDATE}`，将 p.176 “Richelieu’s death” 与 p.180 “death of Richelieu in 1642” 判为同一死亡事件，S3 `new` 组 `{DEATH_GROUP}`，登记为 `{DEATH_KU}`。日期仅按 Haskell p.180 记录；未补具体日、地点、死因或外部事件标识。事件候选与黎塞留人物 KU 保持不同类型和身份。

**S5来源字段。** 两张事件卡从 Haskell 书内段落抽取 {len(extracted)} 条 source-backed 字段（`{enrichment_ids[0]}`–`{enrichment_ids[-1]}`）；无外部核验字段。招揽政策的时间只记为“黎塞留生命最后几年”，不推算年份；目标艺术家未作成员识别。

**S6逐候选裁决。** 本批覆盖六条既有关系候选及一条新增事件—人物候选：

| statement_id | 决定 | 去向 |
|---|---|---|
| `st-chp7-p180-richelieu-death-event-person` | formal `rel-1603 has_participant` | 死亡事件 → 黎塞留人物；角色限于逝者，1642为Haskell来源所报年份。 |
| `st-chp7-p175-i21` | pending | 书内明确为 minister 角色；受控词表没有精确谓词，不改写为 `employed_by` 或 `advised`。 |
| `st-chp7-p175-i29` | pending | 政策事件的招募目标仍连到 S3 `undecided` 的 `cand-6667`；“招募目标”没有精确受控谓词，不改用 `has_subject`。 |
| `st-chp7-p176-i27` | pending | 两个事件端点已登记，但“死亡没有中断计划”是负向延续陈述；不能改成正向 `influenced`。 |
| `st-chp7-p176-i28` | pending | 通知者仍未具名，`toute la troupe des vertueux` 不证明正式组织，且没有精确通知谓词。 |
| `st-chp7-p180-i03` | pending | 保留马萨林接掌法国政府的来源陈述；当前候选谓词不能精确表达“接管政府”，不以泛化组织关系替代。 |
| `st-chp7-p181-i17` | pending | 哈斯克尔把黎塞留与路易十三之死合并为马萨林艺术抱负的因果解释；路易十三事件及原子化仍缺，不把解释转成单一正式边。 |

**结果与核验。** S4两条直接新组均已登记；S6六项保留明确 pending，一项 formal。当前待续包括 `cand-6667` 的身份/类型边界、p.176 Duquesnoy 死亡事件与 p.181 双死亡陈述的 S2 原子化。定向表审计、关系一致性审计和两张卡关系视图预览结果见本记录末尾追加的核验段。
'''
    plans[knowledge_path] = (knowledge.rstrip() + batch_record + "\n").encode("utf-8")

    result_path = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
    result = result_path.read_text(encoding="utf-8-sig")
    old_batch_heading = "### S3身份分组／S4登记／S5来源字段／S6裁决：第七章 p.175 阿波罗与缪斯十幅画（2026-10-23）"
    if old_batch_heading not in result or result.count("### 本轮进度与后续工作（2026-10-23）") != 1:
        raise ValueError("current result header changed; rebase the result update")
    relation_candidates = sum(1 for row in statements if row.get("qualifiers", {}).get("relation_candidate") is True)
    s2_count = len(statements)
    candidate_count = len(candidates)
    main_alignments = [row for row in alignments if not row["external_source"]]
    main_decision_count = len({row["candidate_id"] for row in main_alignments if row["decision"]})
    same_count = sum(row["decision"] == "same" for row in main_alignments)
    new_rows = [row for row in main_alignments if row["decision"] == "new"]
    new_count = len(new_rows)
    group_rows: dict[str, list[dict]] = {}
    for row in new_rows:
        match = re.search(r"(?:^|;\s*)group=([^;]+)", row.get("resolution_note", ""))
        group_id = match.group(1) if match else row["candidate_id"]
        group_rows.setdefault(group_id, []).append(row)
    groups = set(group_rows)
    conflict_count = sum(row["decision"] == "conflict" for row in main_alignments)
    excluded_count = sum(row["decision"] == "excluded" for row in main_alignments)
    undecided_count = sum(row["decision"] == "undecided" for row in main_alignments)
    missing_decisions = candidate_count - main_decision_count
    registered_groups = sum(
        all(row["ku_id"] for row in rows) and len({row["ku_id"] for row in rows}) == 1
        for rows in group_rows.values()
    )
    registered_mappings = sum(bool(row["ku_id"]) for row in new_rows)
    s5_count = len(existing_enrichment) + len(extracted)
    unverified_count = sum(row.get("evidence_status") == "unverified" for row in existing_enrichment)
    decided_s6 = 620
    formal_s6 = 385
    pending_s6 = 168
    rejected_s6 = 67
    remaining_s6 = relation_candidates - decided_s6
    rel_formal = sum(row["status"] == "formal" for row in relations)
    rel_pending = sum(row["status"] == "pending" for row in relations)
    remaining_groups = len(groups) - registered_groups
    remaining_mappings = new_count - registered_mappings
    updated_intro = f'''# 《赞助人与画家》全书 S2 语义处理、S3 身份对齐与交接结果

### 本轮进度与后续工作（2026-10-23）

本轮完成第23批端点工作：登记黎塞留招揽意大利艺术家政策事件与黎塞留之死事件；修正 p.176 将死亡事件误映为人物的 S2 端点，并按 p.175 独立核读修正 minister 关系候选分类。两张事件卡新增 {len(extracted)} 条来源字段；相关 S6 候选逐条给出 1 条 formal、6 条 pending。S2 独立复核分子不变。

**当前全书状态。** S0有832个源段（678 complete、154 excluded）。S2共{s2_count:,}条statement；统一独立逐条复核9,573条（62.8%，尚未接收）；第七章1,146/1,265、第八章487/1,474；第3章1,173/1,183、第10–12章1,567/1,567、第16章206/210的独立章节记录仍分开报告，均未接收；统一复核台账仍待按statement ID与来源版本核平。S3主决定覆盖{main_decision_count:,}/{candidate_count:,}个候选，缺{missing_decisions}项；same={same_count:,}、new={new_count:,}（{len(groups):,}组）、conflict={conflict_count}、excluded={excluded_count}、undecided={undecided_count:,}；另22项跨来源决定不同。S4已登记{registered_groups:,}/{len(groups):,}组、{registered_mappings:,}/{new_count:,}条候选映射；待登记{remaining_groups:,}组／{remaining_mappings:,}条映射。S5共{s5_count:,}条字段，{unverified_count:,}条 `unverified`。relation_candidate=true共{relation_candidates:,}条；S6已裁决{decided_s6:,}/{relation_candidates:,}条（{formal_s6} formal、{pending_s6} pending、{rejected_s6} rejected），余{remaining_s6:,}条；`relations.csv`共{len(relations):,}条（{rel_formal:,} formal、{rel_pending} pending）。339条关系候选至少缺一个S2端点候选ID（subject-only 46、object-only 221、both 72）。`candidate-backlog.csv`仍为10条，9条完成、1条明确undecided、pending=0。

本批新增事件身份仅限 Haskell 书内所指事件；1642为书内所报年份，不声称外部核验。招揽政策与马萨林 1644 年贝尔尼尼行动、1648 年阿尔加迪行动分开。未将 `minister_to`、招募目标、负向“未中断”或作者因果解释强套进不精确的正式谓词。

**后续工作。**

1. 继续按关系解锁价值登记已有 S3 决定的直接端点，并在同批逐条完成正式、待证或否决裁决。
2. 处理黎塞留簇余项：`cand-6703` 的法兰西/佛兰德艺术家集合端点、`cand-6694` 的 Studiolo 作品边界，以及相应 S6 去向；不把待证对象强行合并或正式化。
3. 定向修复 Duquesnoy 死亡事件和第7章 p.181 将黎塞留、路易十三之死合并的 S2 断言；只对受影响的候选、端点及关系回退。
4. 先核平 S2 复核台账的 statement ID 与来源版本，再继续低覆盖章节的独立逐条审读；定向修订不计入复核分子。
5. 完成 S4/S5/S6 收口与全库核验后再准备 S7；知识发现与页面仍暂停。

### S2定向修订／S3／S4／S5／S6：第七章黎塞留招揽政策与死亡事件（2026-10-23）

沿用与本批相同的身份、端点和 S6 去向，详见[过程裁决](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR})。两项 S4 新登记分别为 `{POLICY_KU}`、`{DEATH_KU}`；死亡事件仅标注 Haskell 所报 1642 年。定向检查结果保存在同一过程记录。
'''
    old_intro_start = result.index("# 《赞助人与画家》全书 S2 语义处理、S3 身份对齐与交接结果")
    old_intro_end = result.index(old_batch_heading)
    plans[result_path] = (updated_intro.rstrip() + "\n\n" + result[old_intro_end:]).encode("utf-8")

    new_counts = {
        "candidate_count": candidate_count,
        "s2_count": s2_count,
        "main_decision_count": main_decision_count,
        "missing_decisions": missing_decisions,
        "new_count": new_count,
        "new_groups": len(groups),
        "registered_groups": registered_groups,
        "remaining_groups": remaining_groups,
        "registered_mappings": registered_mappings,
        "remaining_mappings": remaining_mappings,
        "s5_count": s5_count,
        "unverified_count": unverified_count,
        "relation_candidate_count": relation_candidates,
        "relations_rows": len(relations),
        "relations_formal": rel_formal,
        "relations_pending": rel_pending,
        "extracted_fields": len(extracted),
    }
    checks.extend([
        f"updated S2 statements: {s2_count}",
        f"new source-local event candidate: {DEATH_CANDIDATE} -> {DEATH_KU}",
        f"registered existing event candidate: {POLICY_CANDIDATE} -> {POLICY_KU}",
        f"extracted source-backed S5 fields: {len(extracted)} ({', '.join(enrichment_ids)})",
        "created one formal event has_participant relation: rel-1603",
        "recorded six adjacent S6 candidates as pending in the process log",
    ])
    return plans, new_counts, checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Ch.7 Richelieu recruitment/death endpoint batch.")
    parser.add_argument("--apply", action="store_true", help="write the prechecked batch; default is read-only dry-run")
    args = parser.parse_args()
    plans, counts, checks = build_plan()
    print("mode=apply" if args.apply else "mode=dry-run")
    for item in checks:
        print(f"- {item}")
    print("planned_files:")
    for path, payload in plans.items():
        rel = path.relative_to(ROOT)
        old_size = path.stat().st_size if path.exists() else 0
        print(f"  {rel}: {old_size} -> {len(payload)} bytes")
    print("counts:")
    for key, value in counts.items():
        print(f"  {key}={value}")
    if args.apply:
        for path, payload in plans.items():
            atomic_write(path, payload)
        print(f"applied {len(plans)} files")
    else:
        print("no files written; rerun with --apply to apply this exact plan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
