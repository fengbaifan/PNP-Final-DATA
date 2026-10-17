from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
ALIGNMENT = TABLES / "alignment.csv"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
PERSON = "cand-2208"
EVENT = "cand-2209"
SEGMENT = "chp-2:02_CHP-2_sec_iv:l106-112"
EVENT_MENTION = "m-chp2-seciv-l106-112-0051"
EVENT_PHRASE = "In 1638 he was made Principe"
APPOINTMENT_STATEMENT = "st-chp2-seciv-l106-112-romanelli-academy-prince-1638"
PERSON_MENTIONS = {
    "m-chp2-seciv-l106-112-0035",
    "m-chp2-seciv-l106-112-0036",
    "m-chp2-seciv-l106-112-0040",
    "m-chp2-seciv-l106-112-0048",
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def statement_lines(path: Path):
    raw = path.read_text(encoding="utf-8-sig")
    return raw.splitlines(keepends=True)


def main():
    parser = argparse.ArgumentParser(
        description="Separate Romanelli person mentions/assertions from the 1638 appointment event candidate"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    mention_fields, mentions = read_csv(MENTIONS)
    alignment_fields, alignment = read_csv(ALIGNMENT)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    assert set(PERSON_MENTIONS).issubset(mention_by_id)
    assert all(mention_by_id[mid]["candidate_id"] == EVENT for mid in PERSON_MENTIONS)
    assert EVENT_MENTION not in mention_by_id
    assert {
        row["mention_id"] for row in mentions if row["candidate_id"] == EVENT
    } == PERSON_MENTIONS

    source = (ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md").read_text(encoding="utf-8-sig")
    lines = source.splitlines()
    raw_segment = r"\n".join(lines[105:112])
    assert raw_segment.startswith("[Page ")
    segment_text = raw_segment[len("[Page "):]
    event_start = segment_text.find(EVENT_PHRASE)
    assert event_start >= 0 and segment_text[event_start:event_start + len(EVENT_PHRASE)] == EVENT_PHRASE
    assert event_start == 2507, event_start
    for mid in PERSON_MENTIONS:
        mention = mention_by_id[mid]
        start, end = int(mention["start_char"]), int(mention["end_char"])
        assert 0 <= start < end <= len(segment_text), mid

    planned_mentions = [dict(row) for row in mentions]
    for row in planned_mentions:
        if row["mention_id"] in PERSON_MENTIONS:
            row["candidate_id"] = PERSON
    planned_mentions.append({
        "mention_id": EVENT_MENTION,
        "segment_id": SEGMENT,
        "candidate_id": EVENT,
        "surface_form": EVENT_PHRASE,
        "start_char": str(event_start),
        "end_char": str(event_start + len(EVENT_PHRASE)),
        "note": "Event: Romanelli's 1638 appointment as Principe of Accademia di S. Luca.",
    })

    lines = statement_lines(STATEMENTS)
    planned_statement_lines = []
    statement_ids = set()
    affected_statements = set()
    for raw in lines:
        if not raw.strip():
            planned_statement_lines.append(raw)
            continue
        item = json.loads(raw)
        sid = item.get("statement_id")
        assert sid not in statement_ids, sid
        statement_ids.add(sid)
        if EVENT in {item.get("subject_candidate_id"), item.get("object_candidate_id")}:
            affected_statements.add(sid)
            for endpoint in ("subject_candidate_id", "object_candidate_id"):
                if item.get(endpoint) == EVENT:
                    item[endpoint] = PERSON
            if sid == APPOINTMENT_STATEMENT:
                qualifiers = item.setdefault("qualifiers", {})
                mentioned = qualifiers.setdefault("mentioned_candidate_ids", [])
                assert EVENT not in mentioned
                mentioned.append(EVENT)
            planned_statement_lines.append(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
        else:
            planned_statement_lines.append(raw)
    assert APPOINTMENT_STATEMENT in affected_statements
    assert len(affected_statements) == 9, len(affected_statements)

    planned_alignment = [dict(row) for row in alignment]
    event_rows = [row for row in planned_alignment if row.get("candidate_id") == EVENT and not row.get("external_source")]
    person_rows = [row for row in planned_alignment if row.get("candidate_id") == PERSON and not row.get("external_source")]
    assert len(event_rows) == 1 and event_rows[0]["decision"] == "new"
    assert len(person_rows) == 1 and person_rows[0]["decision"] == "same"
    event_alignment = event_rows[0]
    assert "group=sg3-event-cand-2209" in event_alignment["resolution_note"]
    prior_anchor = "source_ref=chp-2:02_CHP-2_sec_iv:l106-112#m-chp2-seciv-l106-112-0035"
    assert prior_anchor in event_alignment["resolution_note"]
    event_alignment["resolution_note"] = event_alignment["resolution_note"].replace(
        prior_anchor,
        f"source_ref={SEGMENT}#{EVENT_MENTION}; prior_source_ref={SEGMENT}#m-chp2-seciv-l106-112-0035",
        1,
    )
    event_alignment["resolution_note"] += (
        " S2 anchor reconciliation: the four p.53 person mentions and nine person assertions map to cand-2208; "
        "this event candidate is anchored to the exact 1638 appointment phrase and its index sub-entry."
    )

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_entry = (
        "\n\n### S2/S3 锚点更正：Romanelli 人物与 1638 年任命事件分开（2026-10-17）\n\n"
        "复核 `cand-2209`（Q-R.csv#136，`appointment to Accademia di S. Luca`）时发现，原有 S2 段落锚点 `m-chp2-seciv-l106-112-0035` "
        "是人物代词“his leading pupil”，而非事件提及；同段4条人物提及及9条人物断言曾误挂到事件候选。现将这4条提及和9条断言端点改挂到已由 S3 裁决为 `same` 的人物候选 `cand-2208`（`units/persons/romanelli`）。"
        "将同段“In 1638 he was made Principe”登记为事件提及 `m-chp2-seciv-l106-112-0051`，并在任命断言的提及候选中保留 `cand-2209`；该候选仍为独立事件组 `sg3-event-cand-2209`，没有并入人物 KU。"
        "对齐行的现行 source_ref 改指任命短语，旧锚点作为历史注释保留。原文、职位名和1638年限定未改；本次未新增正式关系。"
    )
    assert "S2/S3 锚点更正：Romanelli 人物与 1638 年任命事件分开" not in process_text
    process_text += process_entry

    if args.dry_run:
        print(
            f"dry-run passed: person_mentions={len(PERSON_MENTIONS)}; "
            f"person_assertion_endpoints={len(affected_statements)}; event_mention={EVENT_MENTION}; "
            f"event_anchor={event_start}:{event_start + len(EVENT_PHRASE)}"
        )
        print("event remains sg3-event-cand-2209; person remains units/persons/romanelli; no formal relations added")
        print("no files changed")
        return 0

    write_csv(MENTIONS, mention_fields, planned_mentions)
    write_csv(ALIGNMENT, alignment_fields, planned_alignment)
    STATEMENTS.write_text("".join(planned_statement_lines), encoding="utf-8-sig", newline="")
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: person_mentions={len(PERSON_MENTIONS)}; person_assertion_endpoints={len(affected_statements)}; "
        f"event_mention={EVENT_MENTION}; no formal relations added"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
