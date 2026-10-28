#!/usr/bin/env python3
"""Preview/apply the bounded p.57 Dance of Human Life S2/S4/S6 update."""
from __future__ import annotations

import argparse
import csv
import difflib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
TASK = "patrons-and-painters-full-book-s2"
PROCESS_REF = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-ch2-p57-poussin-dance-wallace-20261028"
SOURCE_ID = "haskell-1980-rev-ed"
SOURCE_FILE = "02-sources/02-Markdown/02_CHP-2_sec_iv.md"
SEGMENT = "chp-2:02_CHP-2_sec_iv:l190-245"
STATEMENT_ID = "st-chp2-seciv-l190-245-dance-of-human-life-held-by-wallace"
WORK_CANDIDATE = "cand-4798"
WALLACE_CANDIDATE = "cand-4894"
WORK_KU = "units/works/dance-of-human-life-poussin"
WALLACE_KU = "units/institutions/wallace-collection"
WORK_CARD = "04-knowledge/units/works/dance-of-human-life-poussin.md"
WALLACE_CARD = "04-knowledge/units/institutions/wallace-collection.md"


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def csv_bytes(path: Path, fields, rows) -> bytes:
    import io
    buffer = io.StringIO(newline="")
    line_ending = "\r\n" if b"\r\n" in path.read_bytes() else "\n"
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator=line_ending)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed fixed batch")
    args = parser.parse_args()

    paths = {
        "alignment": TABLES / "alignment.csv",
        "manifest": TABLES / "ku-manifest.csv",
        "relations": TABLES / "relations.csv",
        "statements": TABLES / "book-statements.jsonl",
        "accepted": ROOT / "04-knowledge" / "accepted.yml",
    }
    align_fields, alignments = read_csv(paths["alignment"])
    manifest_fields, manifest = read_csv(paths["manifest"])
    relation_fields, relations = read_csv(paths["relations"])
    statements = [json.loads(line) for line in paths["statements"].read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    accepted = paths["accepted"].read_text(encoding="utf-8-sig")

    for candidate, ku_id in [(WORK_CANDIDATE, WORK_KU), (WALLACE_CANDIDATE, WALLACE_KU)]:
        matches = [r for r in alignments if r["candidate_id"] == candidate and r["external_source"] == ""]
        if len(matches) != 1 or matches[0]["decision"] != "new" or matches[0]["ku_id"]:
            raise ValueError(f"S3/S4 precondition failed for {candidate}: {matches}")
        if any(r["ku_id"] == ku_id for r in manifest):
            raise ValueError(f"KU already registered: {ku_id}")
    if any(row["statement_id"] == STATEMENT_ID for row in statements):
        raise ValueError(f"S2 statement already exists: {STATEMENT_ID}")
    if not Path(ROOT / WORK_CARD).exists() or not Path(ROOT / WALLACE_CARD).exists():
        raise ValueError("create and inspect both target cards before applying table registration")
    if WORK_CARD in accepted or WALLACE_CARD in accepted:
        raise ValueError("accepted.yml already lists a target card")
    if "\nclaims:\n" not in accepted:
        raise ValueError("accepted.yml claims section not found")
    existing_mentions = {r["candidate_id"] for r in read_csv(TABLES / "mentions.csv")[1] if r["segment_id"] == SEGMENT}
    if WORK_CANDIDATE not in existing_mentions or WALLACE_CANDIDATE not in existing_mentions:
        raise ValueError("source mention anchors for both endpoints must already exist")

    statement = {
        "statement_id": STATEMENT_ID,
        "segment_id": SEGMENT,
        "subject_candidate_id": WORK_CANDIDATE,
        "object_candidate_id": WALLACE_CANDIDATE,
        "predicate": "held_by",
        "qualifiers": {
            "source_line_start": 242,
            "source_line_end": 242,
            "claim": "Haskell reports The Dance of Human Life in the Wallace Collection.",
            "speaker": "Haskell's footnote",
            "text_layer": "substantive footnote",
            "print_page": 57,
            "pdf_physical_page": 46,
            "qualification": "Source-reported collection location; no current location or legal ownership is asserted.",
            "footnote_marker": 3,
            "footnote_segment": SEGMENT,
            "work_candidate_ids": [WORK_CANDIDATE],
            "location_pairs": [[WORK_CANDIDATE, WALLACE_CANDIDATE]],
            "relation_candidate": True,
            "relation_candidate_note": "The footnote directly states that The Dance of Human Life is in the Wallace Collection; this is separate from the rejected aggregate statement about three paintings, engravings, and dedication claims.",
        },
        "original_quote": "The Dance of Human Life is in the Wallace Collection",
        "origin": "book",
        "source_file": SOURCE_FILE,
    }
    statements.append(statement)

    s4_notes = {
        WORK_CANDIDATE: "Maps the existing S3 new work group workgrp-a5567f81356ec5 to its source-bounded KU; no external identity is asserted.",
        WALLACE_CANDIDATE: "Maps the existing S3 new institution group sg3-institution-cand-4894 to a source-bounded collection KU; no current institutional identity or location is asserted.",
    }
    for row in alignments:
        candidate = row["candidate_id"]
        if candidate in s4_notes and row["external_source"] == "":
            row["ku_id"] = WORK_KU if candidate == WORK_CANDIDATE else WALLACE_KU
            row["process_ref"] = PROCESS_REF
            row["resolution_note"] = row["resolution_note"].rstrip() + f" S4 registration (2026-10-28): {s4_notes[candidate]} process_ref={PROCESS_REF}."

    manifest.extend([
        {"ku_id": WORK_KU, "type": "work", "canonical_name": "人生之舞", "name_en": "The Dance of Human Life", "source_task": TASK, "card_path": WORK_CARD},
        {"ku_id": WALLACE_KU, "type": "institution", "canonical_name": "华莱士收藏", "name_en": "Wallace Collection", "source_task": TASK, "card_path": WALLACE_CARD},
    ])

    relation_specs = [
        {
            "subject_ku_id": WORK_KU,
            "object_ku_id": "units/persons/nicolas-poussin",
            "predicate": "created_by",
            "time": "",
            "role": "画家",
            "scope": "仅记录Haskell称Poussin绘制此画；该画是否受Rospigliosi委托仍不确定，不据此作外部归属判断。",
            "source_span": "Chapter 2, printed p.57, lines 175–176; statement=st-chp2-seciv-l171-179-poussin-painted-dance-of-human-life",
            "source_file": SOURCE_FILE,
            "note": "Haskell directly lists The Dance of Human Life among three paintings by Poussin.",
        },
        {
            "subject_ku_id": WORK_KU,
            "object_ku_id": WALLACE_KU,
            "predicate": "held_by",
            "time": "Reported in Haskell's 1980 revised edition; exact holding date unstated",
            "role": "collection holding",
            "scope": "仅记录Haskell所报作品在Wallace Collection；不推断法律所有权、入藏日期或当前保管状态。",
            "source_span": "Chapter 2, printed p.57 n.3, line 242; statement=" + STATEMENT_ID,
            "source_file": SOURCE_FILE,
            "note": "Haskell reports a collection location; no external collection or object record was consulted.",
        },
    ]
    last_relation = max(int(r["relation_id"].split("-")[1]) for r in relations)
    for i, spec in enumerate(relation_specs, 1):
        natural = (spec["subject_ku_id"], spec["predicate"], spec["object_ku_id"], spec["time"], spec["role"], spec["scope"])
        if any((r["subject_ku_id"], r["predicate"], r["object_ku_id"], r["time"], r["role"], r["scope"]) == natural for r in relations):
            raise ValueError(f"duplicate formal relation: {natural}")
        relations.append({"relation_id": f"rel-{last_relation+i:04d}", **spec, "origin": "book", "status": "formal", "source_id": SOURCE_ID})

    accepted = accepted.replace("\nclaims:\n", f"\n- {WORK_CARD}\n- {WALLACE_CARD}\nclaims:\n", 1)
    outputs = {
        paths["alignment"]: csv_bytes(paths["alignment"], align_fields, alignments),
        paths["manifest"]: csv_bytes(paths["manifest"], manifest_fields, manifest),
        paths["relations"]: csv_bytes(paths["relations"], relation_fields, relations),
        paths["statements"]: ("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in statements)).encode("utf-8"),
        paths["accepted"]: accepted.encode("utf-8"),
    }

    print("PREVIEW" if not args.apply else "APPLY")
    print("S2: +1 exact Dance → Wallace Collection location statement; the earlier aggregate S6 rejection remains.")
    print(f"S4: 2 existing S3 new decisions mapped to {WORK_KU} and {WALLACE_KU}.")
    print("S6: +2 formal edges: Dance created_by Poussin; Dance held_by Wallace Collection.")
    for path, data in outputs.items():
        before = path.read_bytes()
        if before == data:
            continue
        old_lines = before.decode("utf-8-sig").splitlines(keepends=True)
        new_lines = data.decode("utf-8-sig").splitlines(keepends=True)
        diff = difflib.unified_diff(old_lines, new_lines, fromfile="before", tofile="after")
        print(f"--- {path.relative_to(ROOT)}")
        print("".join(diff), end="")
    if not args.apply:
        return

    originals = {path: path.read_bytes() for path in outputs}
    try:
        for path, data in outputs.items():
            path.write_bytes(data)
    except Exception:
        for path, data in originals.items():
            path.write_bytes(data)
        raise
    print(f"Applied {len(outputs)} table/governance files; rollback snapshot retained in memory until all writes succeeded.")


if __name__ == "__main__":
    main()
