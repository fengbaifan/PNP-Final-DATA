#!/usr/bin/env python3
"""Controlled S2 semantic refinement for Chapter 3, section IV, lines 75-81.

Default mode is dry-run. Use --apply only after reviewing the planned changes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_iv.md"
SEGMENTS = TABLES / "segments.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENT_ID = "chp-3:03_CHP-3_sec_iv:l75-81"
SOURCE_SHA256 = "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed"
SEGMENT_SHA256 = "ca3918cad3d1cb136990435e0f88b5ae190063146c4692673fba1399a9103c32"
EXPECTED_FILE_SHA256 = {
    STATEMENTS: "91618d5af6cfc2deacc5d07a870fcdb38381ce479cd9b04d9d25e51676c31553",
    CANDIDATES: "ca85aa43d331b781ba67b855fcda8685763f202bc47f4976680014432655c3f5",
    MENTIONS: "47be7931df51220a6d7c6eac93c0f0607ebc05f829bbbcea2f91f3b3d42f7e61",
}

NONRELATION_STATEMENTS = {
    "st-chp3-seciv-l75-81-farnese-medieval-echoes",
    "st-chp3-seciv-l75-81-negroni-profile",
    "st-chp3-seciv-l75-81-society-not-master",
}
EXPECTED_EXISTING_STATEMENTS = {
    "st-chp3-seciv-l75-81-ancient-maggiore-mosaic",
    "st-chp3-seciv-l75-81-ancient-prassede-mosaic",
    "st-chp3-seciv-l75-81-apse-after-oliva",
    "st-chp3-seciv-l75-81-baglione-altarpiece",
    "st-chp3-seciv-l75-81-baroque-transfer-judgment",
    "st-chp3-seciv-l75-81-chapel-dedication-sequence",
    "st-chp3-seciv-l75-81-christ-suffering-theme",
    "st-chp3-seciv-l75-81-contract-uncompleted",
    "st-chp3-seciv-l75-81-cortona-altar-drawings",
    "st-chp3-seciv-l75-81-farnese-medieval-echoes",
    "st-chp3-seciv-l75-81-farnese-pressures",
    "st-chp3-seciv-l75-81-farnese-tribune-mosaic-intention",
    "st-chp3-seciv-l75-81-gaulli-exceeded-expectations",
    "st-chp3-seciv-l75-81-iconographic-elements",
    "st-chp3-seciv-l75-81-jesuit-patronage-chapel",
    "st-chp3-seciv-l75-81-negroni-final-arbiter",
    "st-chp3-seciv-l75-81-negroni-patronage",
    "st-chp3-seciv-l75-81-negroni-profile",
    "st-chp3-seciv-l75-81-oliva-patience",
    "st-chp3-seciv-l75-81-oliva-rewarded-gaulli",
    "st-chp3-seciv-l75-81-pediment-cornice",
    "st-chp3-seciv-l75-81-possible-farnese-concession",
    "st-chp3-seciv-l75-81-ranuccio-architectural-complaint",
    "st-chp3-seciv-l75-81-return-to-dome-theology",
    "st-chp3-seciv-l75-81-revived-lamb-subject",
    "st-chp3-seciv-l75-81-society-not-master",
    "st-chp3-seciv-l75-81-theme-in-oliva-writings",
    "st-chp3-seciv-l75-81-triumphant-tone",
    "st-chp3-seciv-l75-81-xavier-dedication-and-picture",
}
NEW_STATEMENT_IDS = {
    "st-chp3-seciv-l75-81-chapel-dedicated-to-resurrection",
    "st-chp3-seciv-l75-81-xavier-picture-painted-by-van-dyck",
    "st-chp3-seciv-l75-81-xavier-picture-placed-in-chapel",
    "st-chp3-seciv-l75-81-negroni-intended-ignore-oliva-plans",
}
NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11609",
        "canonical_name": "The Resurrection (dedication title of the right transept chapel of the Ges\u00f9)",
        "suggested_type": "term",
        "candidate_source_ref": SEGMENT_ID + "#L79",
        "detail": "A dedication title in Haskell's account; distinct from Giovanni Baglione's painting titled The Resurrection (cand-5013). No date is supplied.",
    },
    {
        "candidate_id": "cand-11610",
        "canonical_name": "Projected pediment of Negroni's proposed grand altar in the Ges\u00f9 chapel",
        "suggested_type": "work",
        "candidate_source_ref": SEGMENT_ID + "#L80",
        "detail": "The proposed altar component described as so high that the chapel cornice had to be broken; no surviving physical state is independently identified.",
    },
    {
        "candidate_id": "cand-11611",
        "canonical_name": "Cornice of the right transept chapel of the Ges\u00f9",
        "suggested_type": "work",
        "candidate_source_ref": SEGMENT_ID + "#L80",
        "detail": "Architectural component which Haskell says had to be broken because of the projected altar pediment.",
    },
    {
        "candidate_id": "cand-11612",
        "canonical_name": "Unidentified rival architects who wrote to Duke Ranuccio about Negroni's altar design",
        "suggested_type": "",
        "candidate_source_ref": SEGMENT_ID + "#L80",
        "detail": "A source-bounded anonymous group in Haskell's account. Members, number, institutional affiliation, and identity are not supplied; do not merge with other unnamed architects.",
    },
    {
        "candidate_id": "cand-11613",
        "canonical_name": "Oliva's plans for the rest of the Ges\u00f9 church",
        "suggested_type": "work",
        "candidate_source_ref": SEGMENT_ID + "#L80",
        "detail": "Plans which Haskell says Negroni intended to ignore; the passage does not identify individual components or a separate surviving document.",
    },
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("PREFLIGHT FAILED: " + message)


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    ids = [row["statement_id"] for row in rows]
    require(len(ids) == len(set(ids)), f"duplicate statement_id in {path.name}")
    return rows


def load_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def find_statement(rows: list[dict], statement_id: str) -> dict:
    matches = [row for row in rows if row["statement_id"] == statement_id]
    require(len(matches) == 1, f"expected one statement {statement_id}, found {len(matches)}")
    return matches[0]


def find_mention(rows: list[dict], mention_id: str) -> dict:
    matches = [row for row in rows if row["mention_id"] == mention_id]
    require(len(matches) == 1, f"expected one mention {mention_id}, found {len(matches)}")
    return matches[0]


def quote(text: str, phrase: str) -> str:
    start = text.find(phrase)
    require(start >= 0, f"source phrase not found: {phrase!r}")
    return text[start:start + len(phrase)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the preflighted changes")
    args = parser.parse_args()

    require(digest(SOURCE) == SOURCE_SHA256, "source file SHA-256 changed")
    for path, expected in EXPECTED_FILE_SHA256.items():
        require(digest(path) == expected, f"{path.name} SHA-256 changed")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    text = "\n".join(source_lines[74:81])
    segment_rows = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    segment = [row for row in segment_rows if row.get("segment_id") == SEGMENT_ID]
    require(len(segment) == 1, "expected one S0 segment")
    require(segment[0].get("sha256") == SEGMENT_SHA256, "S0 segment hash changed")
    require(hashlib.sha256(text.encode("utf-8")).hexdigest() == SEGMENT_SHA256, "reconstructed segment text hash mismatch")
    require(len(text) == 3221, "unexpected reconstructed segment length")

    statement_rows = load_jsonl(STATEMENTS)
    candidate_fields, candidate_rows = load_csv(CANDIDATES)
    mention_fields, mention_rows = load_csv(MENTIONS)
    segment_statements = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    require({row["statement_id"] for row in segment_statements} == EXPECTED_EXISTING_STATEMENTS,
            "segment statement set changed")
    require(len(segment_statements) == 29, "expected 29 existing statements")
    require(all("relation_candidate" not in row.get("qualifiers", {}) for row in segment_statements),
            "a segment statement was already classified")

    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    require(max(int(cid[5:]) for cid in candidate_ids) == 11608, "candidate ID high-water mark changed")
    require(not (candidate_ids & {row["candidate_id"] for row in NEW_CANDIDATES}),
            "one or more planned candidate IDs already exist")

    mention_ids = {row["mention_id"] for row in mention_rows}
    planned_mention_ids = {
        "m-chp3-seciv-l75-81-0051",
        "m-chp3-seciv-l75-81-0052",
        "m-chp3-seciv-l75-81-0053",
        "m-chp3-seciv-l75-81-0054",
    }
    require(not (mention_ids & planned_mention_ids), "one or more planned mention IDs already exist")
    require(max(int(row["mention_id"].rsplit("-", 1)[1]) for row in mention_rows
                if row["mention_id"].startswith("m-chp3-seciv-l75-81-")) == 50,
            "segment mention ID high-water mark changed")

    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    for candidate_id, expected_type in {
        "cand-0712": "place",
        "cand-0719": "place",
        "cand-0958": "person",
        "cand-2826": "person",
        "cand-4910": "person",
        "cand-5291": "term",
        "cand-5298": "work",
        "cand-5300": "place",
    }.items():
        require(candidate_id in candidate_by_id and candidate_by_id[candidate_id]["suggested_type"] == expected_type,
                f"expected {candidate_id} to remain a {expected_type} candidate")

    false_surface_id = "m-s2-chp3-surface-f9ac9f72e91ecb2b"
    false_surface = find_mention(mention_rows, false_surface_id)
    require(false_surface["segment_id"] == SEGMENT_ID and false_surface["surface_form"] == "subject"
            and false_surface["candidate_id"] == "cand-0840"
            and false_surface["start_char"] == "209" and false_surface["end_char"] == "216",
            "unexpected stale surface mention")

    mention_preconditions = {
        "m-chp3-seciv-l75-81-0005": ("cand-5287", "The Adoration of the Lamb", "220", "245"),
        "m-chp3-seciv-l75-81-0032": ("cand-5300", "the Saviour", "2184", "2195"),
        "m-chp3-seciv-l75-81-0033": ("cand-5300", "the Resurrection", "2208", "2224"),
        "m-chp3-seciv-l75-81-0039": ("cand-0960", "Van Dyck", "2422", "2430"),
        "m-chp3-seciv-l75-81-0047": ("cand-5299", "the projected pediment", "2922", "2944"),
    }
    mention_updates = {
        "m-chp3-seciv-l75-81-0005": "cand-5291",
        "m-chp3-seciv-l75-81-0032": "cand-4910",
        "m-chp3-seciv-l75-81-0033": "cand-11609",
        "m-chp3-seciv-l75-81-0039": "cand-0958",
        "m-chp3-seciv-l75-81-0047": "cand-11610",
    }
    for mention_id, expected in mention_preconditions.items():
        row = find_mention(mention_rows, mention_id)
        require((row["candidate_id"], row["surface_form"], row["start_char"], row["end_char"]) == expected,
                f"unexpected mention mapping or span for {mention_id}")
    maria_work_mention = find_mention(mention_rows, "m-chp3-seciv-l75-81-0010")
    require((maria_work_mention["candidate_id"], maria_work_mention["surface_form"],
             maria_work_mention["start_char"], maria_work_mention["end_char"]) ==
            ("cand-5289", "S. Maria Maggiore", "318", "335"),
            "unexpected S. Maria Maggiore mosaic mention")

    additions = [
        ("m-chp3-seciv-l75-81-0051", "cand-0712", 318, 335, "S. Maria Maggiore", ""),
        ("m-chp3-seciv-l75-81-0052", "cand-11611", 2950, 2961, "the cornice", ""),
        ("m-chp3-seciv-l75-81-0053", "cand-11612", 3001, 3017, "rival architects", ""),
        ("m-chp3-seciv-l75-81-0054", "cand-11613", 2754, 2794,
         "Oliva\u2019s plans for the rest of the church", ""),
    ]
    for mention_id, candidate_id, start, end, expected_surface, _ in additions:
        surface = text[start:end]
        require(surface == expected_surface, f"unexpected source span for {mention_id}: {surface!r}")
        require(mention_id in planned_mention_ids and candidate_id, "invalid planned mention")

    new_statement_map = {row["statement_id"]: row for row in statement_rows}
    require(not (set(new_statement_map) & NEW_STATEMENT_IDS), "one or more planned statement IDs already exist")
    n3 = find_statement(statement_rows, "st-chp3-seciv-notes-l205-243-p84-n3-pecchiai")
    require(set(n3["qualifiers"].get("linked_body_statement_ids", [])) == {
        "st-chp3-seciv-l75-81-chapel-dedication-sequence",
        "st-chp3-seciv-l75-81-baglione-altarpiece",
    }, "unexpected p.84 note 3 links")

    statements_by_id = {row["statement_id"]: row for row in segment_statements}
    updates = {
        "st-chp3-seciv-l75-81-baroque-transfer-judgment": {
            "object_candidate_id": "cand-5291",
            "original_quote": quote(text, "the transference into Baroque terms of imagery,"),
        },
        "st-chp3-seciv-l75-81-chapel-dedication-sequence": {
            "object_candidate_id": "cand-4910",
            "predicate": "dedicated_to",
            "original_quote": quote(text, "It had originally been dedicated to the Saviour"),
        },
        "st-chp3-seciv-l75-81-negroni-final-arbiter": {
            "object_candidate_id": "cand-5300",
            "predicate": "considered_himself_final_arbiter_in",
            "original_quote": quote(text, "From the first, Negroni showed that he considered himself the final arbiter in his own chapel"),
        },
        "st-chp3-seciv-l75-81-pediment-cornice": {
            "subject_candidate_id": "cand-11610",
            "object_candidate_id": "cand-11611",
            "original_quote": quote(text, "so high was the projected pediment that the cornice had to be broken"),
        },
        "st-chp3-seciv-l75-81-ranuccio-architectural-complaint": {
            "subject_candidate_id": "cand-11612",
            "original_quote": quote(text, "After Pietro\u2019s death rival architects were soon writing to Duke Ranuccio at Parma that this was ruining the architecture designed by his great ancestor."),
        },
        "st-chp3-seciv-l75-81-xavier-dedication-and-picture": {
            "subject_candidate_id": "cand-5300",
            "object_candidate_id": "cand-2826",
            "predicate": "dedicated_to",
            "original_quote": quote(text, "On his canonisation in 1623 the chapel was dedicated to St Francis Xavier"),
        },
    }
    for statement_id, fields in updates.items():
        row = statements_by_id[statement_id]
        row.update({key: value for key, value in fields.items() if key not in {"original_quote"}})
        if "original_quote" in fields:
            row["original_quote"] = fields["original_quote"]

    chapel_dedication = statements_by_id["st-chp3-seciv-l75-81-chapel-dedication-sequence"]
    q = chapel_dedication["qualifiers"]
    q["claim"] = "Haskell says the chapel was first dedicated to the Saviour."
    q["qualification"] = "No date is supplied; this is the earlier dedication in the sequence Haskell describes."
    for key in ("footnote_markers", "footnote_source_lines", "footnote_segment_id", "footnote_pending", "footnote_statement_ids"):
        q.pop(key, None)

    arbiter = statements_by_id["st-chp3-seciv-l75-81-negroni-final-arbiter"]
    arbiter["qualifiers"]["claim"] = "Haskell says Negroni considered himself the final arbiter in his own chapel."
    arbiter["qualifiers"]["qualification"] = "This is Haskell's account of Negroni's view, not an independent legal determination."

    xavier = statements_by_id["st-chp3-seciv-l75-81-xavier-dedication-and-picture"]
    xavier["qualifiers"]["claim"] = "Haskell says the chapel was dedicated to St Francis Xavier in connection with his canonisation, which Haskell dates to 1623."
    xavier["qualifiers"]["qualification"] = "Preserve Haskell's source-specific date; the picture placement and Van Dyck authorship are recorded separately."

    note_qualifiers = n3["qualifiers"]
    note_qualifiers["linked_body_statement_ids"] = ["st-chp3-seciv-l75-81-baglione-altarpiece"]

    def new_statement(statement_id: str, subject: str, predicate: str, obj: str,
                      source_line: int, claim: str, source_quote: str, qualification: str) -> dict:
        return {
            "statement_id": statement_id,
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": subject,
            "object_candidate_id": obj,
            "predicate": predicate,
            "qualifiers": {
                "source_line_start": source_line,
                "source_line_end": source_line,
                "claim": claim,
                "speaker": "Haskell",
                "text_layer": "authorial narrative",
                "print_page": 84,
                "pdf_physical_page": 26,
                "qualification": qualification,
                "relation_candidate": True,
            },
            "original_quote": source_quote,
            "origin": "book",
            "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
        }

    new_statements = [
        new_statement(
            "st-chp3-seciv-l75-81-chapel-dedicated-to-resurrection",
            "cand-5300", "dedicated_to", "cand-11609", 79,
            "Haskell says the chapel was then dedicated to the Resurrection after its earlier dedication to the Saviour.",
            quote(text, "and then to the Resurrection"),
            "No date is supplied; the dedication title is distinct from Baglione's painting titled The Resurrection.",
        ),
        new_statement(
            "st-chp3-seciv-l75-81-xavier-picture-painted-by-van-dyck",
            "cand-0958", "painted", "cand-5298", 79,
            "Haskell says Van Dyck painted the picture of St Francis Xavier placed in the chapel.",
            quote(text, "which had been painted by Van Dyck"),
            "The painting's title, version, and present location are not supplied; authorship is attributed to Haskell's account.",
        ),
        new_statement(
            "st-chp3-seciv-l75-81-xavier-picture-placed-in-chapel",
            "cand-5298", "placed_in", "cand-5300", 79,
            "Haskell says the picture of St Francis Xavier was placed in the chapel on the dedication associated with his canonisation.",
            quote(text, "and in it was placed a picture of the saint"),
            "No title, version, or present location is supplied.",
        ),
        new_statement(
            "st-chp3-seciv-l75-81-negroni-intended-ignore-oliva-plans",
            "cand-1732", "intended_to_ignore_plans_of", "cand-11613", 80,
            "Haskell says Negroni intended to ignore Oliva's plans for the rest of the church.",
            quote(text, "and that he intended to ignore Oliva\u2019s plans for the rest of the church."),
            "Preserve Haskell's attribution and the stated intention; do not infer which individual plans were ignored.",
        ),
    ]
    for row in segment_statements:
        q = row.setdefault("qualifiers", {})
        q["relation_candidate"] = row["statement_id"] not in NONRELATION_STATEMENTS
    ordered_segment = sorted(
        segment_statements + new_statements,
        key=lambda row: row["statement_id"],
    )
    first = min(i for i, row in enumerate(statement_rows) if row.get("segment_id") == SEGMENT_ID)
    last = max(i for i, row in enumerate(statement_rows) if row.get("segment_id") == SEGMENT_ID)
    require(last - first + 1 == len(segment_statements), "segment statements are not contiguous")
    statement_rows[first:last + 1] = ordered_segment

    for row in NEW_CANDIDATES:
        candidate_rows.append({
            "candidate_id": row["candidate_id"],
            "index_entry_id": "",
            "canonical_name": row["canonical_name"],
            "index_page_range": "",
            "suggested_type": row["suggested_type"],
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": row["detail"],
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": row["candidate_source_ref"],
        })

    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    for mention_id, candidate_id in mention_updates.items():
        row = mention_by_id[mention_id]
        row["candidate_id"] = candidate_id
        if mention_id.endswith("0005"):
            row["note"] = "Iconographic subject, distinct from Gaulli's fresco."
        elif mention_id.endswith("0039"):
            row["note"] = "Person candidate; the index's paintings subentry remains a separate work candidate."
        elif mention_id.endswith("0047"):
            row["note"] = "The projected architectural component, distinct from Pietro da Cortona's drawings."
    maria_work_mention["note"] = "Elliptical continuation of the shared head 'mosaics'; the church itself is separately mapped to cand-0712."
    mention_rows.remove(false_surface)
    for mention_id, candidate_id, start, end, expected_surface, note in additions:
        surface = text[start:end]
        mention_rows.append({
            "mention_id": mention_id,
            "segment_id": SEGMENT_ID,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": note,
        })

    expected_candidate_total = 11591
    expected_mention_total = 27527
    expected_statement_total = 12795
    require(len(candidate_rows) == expected_candidate_total, "unexpected candidate total after plan")
    require(len(mention_rows) == expected_mention_total, "unexpected mention total after plan")
    require(len(statement_rows) == expected_statement_total, "unexpected statement total after plan")

    print("mode:", "apply" if args.apply else "dry-run")
    print("segment:", SEGMENT_ID, "source_sha256:", SOURCE_SHA256, "segment_sha256:", SEGMENT_SHA256)
    print("statements: 29 existing classified (26 relation candidates, 3 nonrelations); 4 atomic statements added")
    print("candidates: 5 added; mentions: 5 remapped, 4 added, 1 false surface mention removed")
    print("post-plan totals: candidates=11591 mentions=27527 statements=12795")
    print("candidate IDs:", ", ".join(row["candidate_id"] for row in NEW_CANDIDATES))
    print("new statement IDs:", ", ".join(sorted(NEW_STATEMENT_IDS)))
    if not args.apply:
        print("No files were written. Re-run with --apply to create recovery copies and write.")
        return

    backups = {
        STATEMENTS: STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp3-sec-iv-l75-81-semantic-20261011"),
        CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + ".bak-s2-chp3-sec-iv-l75-81-semantic-20261011"),
        MENTIONS: MENTIONS.with_name(MENTIONS.name + ".bak-s2-chp3-sec-iv-l75-81-semantic-20261011"),
    }
    require(all(not backup.exists() for backup in backups.values()), "a recovery-copy path already exists")

    payloads: dict[Path, bytes] = {}
    payloads[STATEMENTS] = b"".join(
        (json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
        for row in statement_rows
    )
    for path, fields, rows in (
        (CANDIDATES, candidate_fields, candidate_rows),
        (MENTIONS, mention_fields, mention_rows),
    ):
        from io import StringIO
        buffer = StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        payloads[path] = b"\xef\xbb\xbf" + buffer.getvalue().encode("utf-8")

    temp_paths: dict[Path, Path] = {}
    try:
        for path, payload in payloads.items():
            fd, name = tempfile.mkstemp(prefix=path.name + ".tmp-", dir=path.parent)
            os.close(fd)
            temp = Path(name)
            temp.write_bytes(payload)
            temp_paths[path] = temp
        for path, backup in backups.items():
            shutil.copy2(path, backup)
        for path, temp in temp_paths.items():
            os.replace(temp, path)
        require(len(load_jsonl(STATEMENTS)) == expected_statement_total, "post-write statement count mismatch")
        require(len(load_csv(CANDIDATES)[1]) == expected_candidate_total, "post-write candidate count mismatch")
        require(len(load_csv(MENTIONS)[1]) == expected_mention_total, "post-write mention count mismatch")
        print("apply complete; recovery copies:")
        for path, backup in backups.items():
            print(" ", backup.relative_to(ROOT))
            print("   pre-write sha256:", EXPECTED_FILE_SHA256[path])
            print("   post-write sha256:", digest(path))
    finally:
        for temp in temp_paths.values():
            temp.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
