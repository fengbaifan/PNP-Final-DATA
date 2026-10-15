from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
PDF = ROOT / "02-sources/01-book/CHP-3.pdf"
PAGE_IMAGE = ROOT / ".tmp_s2_ch3_phys16_hi.png"
PROCESS = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/stages.md"
SEGMENT = "chp-3:03_CHP-3_sec_ii:l115-123"
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
NEW_CANDIDATE_ID = "cand-11592"
NEW_STATEMENT_ID = "st-chp3-secii-l115-123-gesu-model-for-others"
NEW_MENTION_IDS = ("m-chp3-secii-l115-123-0053", "m-chp3-secii-l115-123-0054")
SUFFIX = ".bak-s2-chp3-sec-ii-l115-123-relations-20261010"
BACKUPS = {
    TABLE: TABLE.with_name(TABLE.name + SUFFIX),
    CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + SUFFIX),
    MENTIONS: MENTIONS.with_name(MENTIONS.name + SUFFIX),
}
EXPECTED_HASHES = {
    TABLE: "1b90d2ea6f958b4f1111153d4d1c3c97ad996536232f6be035551d7cb89140c8",
    CANDIDATES: "badce6cd43479d2e8a6aabcbfb2c11fb0d5103856c1f109459c8923067ae9374",
    MENTIONS: "deb6dd3f795348cce8c5fd79f87e808acd8e3c28b16e5dbe4cdecabe225fb366",
    COVERAGE: "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
    PAGE_IMAGE: "63765c5d71f5952b219fcd7d0dbaab7c83c7b1ddf69c42fa825219fec3a42e31",
}

TRUE_NOTES = {
    "st-chp3-secii-l115-123-account-record": "The passage says de Lattre's name appears in the church account books from 1638 and recurs for about twelve years.",
    "st-chp3-secii-l115-123-bellori-jesuit-design": "Haskell's quoted report says some Jesuits wanted the S. Ignazio project to follow the Gesu design.",
    "st-chp3-secii-l115-123-chapel-patronage": "The passage says the Jesuits assumed patronage of the side chapels rather than entrusting it to Roman patrician families.",
    "st-chp3-secii-l115-123-church-audience": "The passage identifies Collegio Romano students as the intended users of the church.",
    "st-chp3-secii-l115-123-decoration-assigned": "The Society turned to its member Pierre de Lattre to continue decorating the S. Ignazio church.",
    "st-chp3-secii-l115-123-domenico-reply": "Bellori's quoted account says Domenico proposed an alternative after the two-model dispute.",
    "st-chp3-secii-l115-123-eighteenth-century-account": "An eighteenth-century account attributes Domenichino's withdrawal to Grassi's combination of the two submitted designs.",
    "st-chp3-secii-l115-123-grassi-appointment": "The passage says Orazio Grassi was appointed to the S. Ignazio project.",
    "st-chp3-secii-l115-123-grassi-galileo": "Haskell identifies Grassi through his controversy with Galileo; retain this source-described connection.",
    "st-chp3-secii-l115-123-heirs-expenditure": "The passage says Ludovisi's heirs were reluctant to continue expenditure for the church after his death.",
    "st-chp3-secii-l115-123-jesuit-design-control": "The passage says the Jesuits retained control to reproduce essential elements of the Gesu on a larger scale.",
    "st-chp3-secii-l115-123-jesuit-source-plan": "Haskell reports that Jesuit sources say Ludovisi chose Grassi's plan from several proposals; the sources remain unidentified.",
    "st-chp3-secii-l115-123-lattre-collegio": "The passage says de Lattre went to the Collegio Romano and remained there until his death.",
    "st-chp3-secii-l115-123-lattre-life": "Haskell identifies de Lattre as a Frenchman from St Omer who entered the S. Andrea novitiate.",
    "st-chp3-secii-l115-123-lattre-works": "The passage attributes the sacristy fresco, six side-chapel pictures and imitation altar to de Lattre at S. Ignazio.",
    "st-chp3-secii-l115-123-ludovisi-bequest": "The passage says Ludovisi left the Society a further 100,000 ducats.",
    "st-chp3-secii-l115-123-ludovisi-interest": "The passage says Ludovisi continued to show interest in construction of the S. Ignazio church.",
    "st-chp3-secii-l115-123-obituary": "The passage attributes claims about de Lattre's life and works to his obituary.",
    "st-chp3-secii-l115-123-review-committee": "The passage says Ludovisi insisted on an architects' committee to examine Grassi's plans.",
}
FALSE_NOTES = {
    "st-chp3-secii-l115-123-bellori-gesu-description": "The retained clause is an evaluative description of the Gesu; the separate model-for claim is recorded as its own statement.",
    "st-chp3-secii-l115-123-economy": "Economising is a general policy or circumstance, with no distinct second entity asserted in this statement.",
    "st-chp3-secii-l115-123-lattre-assessment": "The surviving-work judgement is Haskell's assessment of de Lattre, not a relation between identified entities.",
    "st-chp3-secii-l115-123-mass-vault": "The 1640 first-mass date and missing vault describe the church's chronology and state.",
    "st-chp3-secii-l115-123-pressure": "Haskell infers considerable pressure but does not identify its source or a distinct endpoint.",
    "st-chp3-secii-l115-123-public-opening": "The opening date and unfinished state describe the church's chronology and condition.",
}
PROMOTED_ID = "st-chp3-secii-l115-123-ludovisi-control"
ALREADY_TRUE = {"st-chp3-secii-l115-123-bellori-drawings"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def normalized(value: str) -> str:
    return " ".join(value.split())


def encode_jsonl(rows: list[dict], raw: bytes) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    prefix = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    return prefix + b"".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + newline for row in rows
    )


def encode_csv(rows: list[dict], raw: bytes, fieldnames: list[str]) -> bytes:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator=newline, extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    prefix = "\ufeff" if raw.startswith(b"\xef\xbb\xbf") else ""
    return (prefix + stream.getvalue()).encode("utf-8")


def atomic_write(path: Path, payload: bytes) -> None:
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
            handle.write(payload)
            temp_path = Path(handle.name)
        os.replace(temp_path, path)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply reviewed S2 relation classifications")
    args = parser.parse_args()
    for path, expected in EXPECTED_HASHES.items():
        require(path.exists() and digest(path) == expected, f"preflight hash changed for {path.relative_to(ROOT)}")
    require(all(not backup.exists() for backup in BACKUPS.values()), "a recovery backup already exists")

    raw_table, raw_candidates, raw_mentions = TABLE.read_bytes(), CANDIDATES.read_bytes(), MENTIONS.read_bytes()
    statements = read_jsonl(TABLE)
    require(len(statements) == 12748 and len({r["statement_id"] for r in statements}) == len(statements), "statement table state changed")
    by_id = {row["statement_id"]: row for row in statements}
    segment_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    require(len(segment_rows) == 27, "L115–123 statement count changed")
    pending_ids = {r["statement_id"] for r in segment_rows if (r.get("qualifiers") or {}).get("relation_candidate") is None}
    require(pending_ids == set(TRUE_NOTES) | set(FALSE_NOTES) | {PROMOTED_ID}, "pending statement set changed")
    already_true = {r["statement_id"] for r in segment_rows if (r.get("qualifiers") or {}).get("relation_candidate") is True}
    require(already_true == ALREADY_TRUE, "already-classified statement set changed")
    require(NEW_STATEMENT_ID not in by_id, "new statement ID already exists")
    bilateral_pending = {
        r["statement_id"] for r in segment_rows
        if r.get("subject_candidate_id") and r.get("object_candidate_id")
        and (r.get("qualifiers") or {}).get("relation_candidate") is None
    }
    require(bilateral_pending == set(TRUE_NOTES), "expected 19 pending bilateral statements")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[114:123])
    require(segment_text[290:296] == "others" and segment_text[1104:1120] == "the construction", "source mention spans changed")
    manifest = {r["segment_id"]: r for r in read_jsonl(SEGMENTS)}.get(SEGMENT)
    require(
        manifest is not None and (manifest.get("source_file"), manifest.get("line_start"), manifest.get("line_end"))
        == (SOURCE_FILE, 115, 123),
        "S0 segment boundary changed",
    )
    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        coverage_rows = list(csv.DictReader(handle))
    coverage = next((r for r in coverage_rows if r["segment_id"] == SEGMENT), None)
    require(coverage and (coverage["disposition"], coverage["migration_status"]) == ("reviewed", "complete"), "coverage is not complete")
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    require("L115–123核对" in process_text and "CHP-3.pdf" in process_text and "物理页16" in process_text, "page-image review is not recorded")

    candidate_rows = list(csv.DictReader(CANDIDATES.open(encoding="utf-8-sig", newline="")))
    candidate_fields = list(candidate_rows[0])
    candidate_by_id = {r["candidate_id"]: r for r in candidate_rows}
    require(len(candidate_rows) == 11569 and NEW_CANDIDATE_ID not in candidate_by_id, "candidate table state changed")
    require(max(int(r["candidate_id"].split("-")[1]) for r in candidate_rows) == 11591, "candidate ID sequence changed")
    require(candidate_by_id["cand-3112"]["suggested_type"] == "place" and candidate_by_id["cand-3967"]["suggested_type"] == "place", "church endpoint mappings changed")
    for cid in ("cand-10918", "cand-5397"):
        require(cid in candidate_by_id and candidate_by_id[cid]["candidate_source_ref"] != f"{SEGMENT}#L116", "existing group candidate state changed")

    mention_rows = list(csv.DictReader(MENTIONS.open(encoding="utf-8-sig", newline="")))
    mention_fields = list(mention_rows[0])
    mention_by_id = {r["mention_id"]: r for r in mention_rows}
    require(len(mention_rows) == 27507 and all(mid not in mention_by_id for mid in NEW_MENTION_IDS), "mention table state changed")
    require(
        not any(r["segment_id"] == SEGMENT and r["candidate_id"] == "cand-3967" and r["surface_form"] == "the construction" for r in mention_rows),
        "construction mention already exists",
    )
    for statement_id in pending_ids:
        row = by_id[statement_id]
        require(normalized(row.get("original_quote", "")) in normalized(segment_text), f"source quote mismatch: {statement_id}")
    control = by_id[PROMOTED_ID]
    require(control.get("subject_candidate_id") == "cand-3073" and not control.get("object_candidate_id"), "limited-patronage endpoints changed")
    require(control.get("predicate") == "described_as_patron_with_limited_control", "limited-patronage predicate changed")
    require((control.get("qualifiers") or {}).get("epistemic_status") == "author assessment", "limited-patronage epistemic status changed")
    description = by_id["st-chp3-secii-l115-123-bellori-gesu-description"]
    require(description.get("subject_candidate_id") == "cand-3112" and description.get("qualifiers", {}).get("quoted_speaker") == "Bellori", "Bellori description mapping changed")

    candidate = {
        "candidate_id": NEW_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Other churches modeled on the Gesù (unnamed group)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell's quotation of Bellori says the Gesù served as a model for 'others'. "
            "The local phrase 'their churches' suggests Jesuit churches, but group membership and scope are unspecified. "
            "Do not equate it with the three principal Roman churches or all Jesuit churches discussed in chapter 3."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L116",
    }
    require(list(candidate) == candidate_fields, "candidate schema changed")
    new_mentions = [
        {
            "mention_id": NEW_MENTION_IDS[0],
            "segment_id": SEGMENT,
            "candidate_id": NEW_CANDIDATE_ID,
            "surface_form": "others",
            "start_char": "290",
            "end_char": "296",
            "note": "Plural model-target group; members and scope are not identified.",
        },
        {
            "mention_id": NEW_MENTION_IDS[1],
            "segment_id": SEGMENT,
            "candidate_id": "cand-3967",
            "surface_form": "the construction",
            "start_char": "1104",
            "end_char": "1120",
            "note": "Anaphoric reference to the S. Ignazio church project; linked to its existing building candidate.",
        },
    ]
    require(all(list(r) == mention_fields for r in new_mentions), "mention schema changed")

    for statement_id, note in TRUE_NOTES.items():
        row = by_id[statement_id]
        q = dict(row.get("qualifiers") or {})
        q.update(relation_candidate=True, relation_candidate_note=note)
        row["qualifiers"] = q
    for statement_id, note in FALSE_NOTES.items():
        row = by_id[statement_id]
        q = dict(row.get("qualifiers") or {})
        q.update(relation_candidate=False, relation_candidate_note=note)
        if statement_id == "st-chp3-secii-l115-123-bellori-gesu-description":
            q["claim"] = "In the Haskell-quoted Bellori account, the Gesù is described as the first and most beautiful of the Jesuit churches."
            row["original_quote"] = "This was the first and most beautiful of their churches"
        row["qualifiers"] = q

    control["object_candidate_id"] = "cand-3967"
    q = dict(control.get("qualifiers") or {})
    q.update(
        relation_candidate=True,
        relation_candidate_note=(
            "The source assesses Ludovisi's patronage in relation to the S. Ignazio construction; "
            "the page context identifies the construction as the church project."
        ),
    )
    control["qualifiers"] = q
    new_statement = {
        "statement_id": NEW_STATEMENT_ID,
        "segment_id": SEGMENT,
        "subject_candidate_id": "cand-3112",
        "object_candidate_id": NEW_CANDIDATE_ID,
        "predicate": "model_for",
        "qualifiers": {
            "source_line_start": 116,
            "source_line_end": 116,
            "claim": "In the Haskell-quoted Bellori account, the Gesù had served as a model for other churches; the referenced group is not identified.",
            "speaker": "Haskell",
            "text_layer": "body",
            "print_page": 74,
            "pdf_physical_page": 16,
            "reported_source_candidate_id": "cand-3056",
            "quoted_speaker": "Bellori",
            "reported_source_layer": "Bellori as quoted by Haskell",
            "relation_candidate": True,
            "relation_candidate_note": "The sentence explicitly states a model-for relation but names no individual target churches; retain the open, untyped group endpoint.",
        },
        "original_quote": "This was the first and most beautiful of their churches and had served as a model for others.",
        "origin": "book",
        "source_file": SOURCE_FILE,
    }
    require(list(new_statement) == list(statements[0]), "statement schema changed")
    require(normalized(new_statement["original_quote"]) in normalized(segment_text), "new statement quote mismatch")
    statements.append(new_statement)
    candidate_rows.append(candidate)
    mention_rows.extend(new_mentions)

    bilateral = [r for r in statements if r.get("subject_candidate_id") and r.get("object_candidate_id")]
    b_true = sum((r.get("qualifiers") or {}).get("relation_candidate") is True for r in bilateral)
    b_false = sum((r.get("qualifiers") or {}).get("relation_candidate") is False for r in bilateral)
    b_pending = sum((r.get("qualifiers") or {}).get("relation_candidate") is None for r in bilateral)
    relation_total = sum((r.get("qualifiers") or {}).get("relation_candidate") is True for r in statements)
    relation_open = sum(
        (r.get("qualifiers") or {}).get("relation_candidate") is True
        and not (r.get("subject_candidate_id") and r.get("object_candidate_id")) for r in statements
    )
    segment_after = [r for r in statements if r.get("segment_id") == SEGMENT]
    seg_true = sum((r.get("qualifiers") or {}).get("relation_candidate") is True for r in segment_after)
    seg_false = sum((r.get("qualifiers") or {}).get("relation_candidate") is False for r in segment_after)
    seg_pending = sum((r.get("qualifiers") or {}).get("relation_candidate") is None for r in segment_after)
    require((len(statements), len(candidate_rows), len(mention_rows)) == (12749, 11570, 27509), "projected table totals differ")
    require((len(bilateral), b_true, b_false, b_pending, relation_total, relation_open) == (8539, 4743, 473, 3323, 4792, 49), "projected whole-book totals differ")
    require((len(segment_after), seg_true, seg_false, seg_pending) == (28, 22, 6, 0), "projected segment totals differ")

    encoded = {
        TABLE: encode_jsonl(statements, raw_table),
        CANDIDATES: encode_csv(candidate_rows, raw_candidates, candidate_fields),
        MENTIONS: encode_csv(mention_rows, raw_mentions, mention_fields),
    }
    report = {
        "action": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT,
        "pending_bilateral_classified": len(TRUE_NOTES),
        "scalar_nonrelations_classified": len(FALSE_NOTES),
        "promoted_with_endpoint": PROMOTED_ID,
        "new_statement": NEW_STATEMENT_ID,
        "new_candidate": NEW_CANDIDATE_ID,
        "new_mentions": list(NEW_MENTION_IDS),
        "segment_after": {"statements": len(segment_after), "relation_candidates": seg_true, "nonrelations": seg_false, "unclassified": seg_pending},
        "bilateral_after": {"total": len(bilateral), "relation_candidates": b_true, "nonrelations": b_false, "unclassified": b_pending},
        "relation_candidates_total": relation_total,
        "relation_candidates_open": relation_open,
        "post_write_hashes": {str(path.relative_to(ROOT)): hashlib.sha256(payload).hexdigest() for path, payload in encoded.items()},
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print("Dry run only. Pass --apply to write.")
        return

    for path, backup in BACKUPS.items():
        shutil.copy2(path, backup)
    try:
        for path, payload in encoded.items():
            atomic_write(path, payload)
        saved = read_jsonl(TABLE)
        saved_by_id = {r["statement_id"]: r for r in saved}
        saved_candidates = list(csv.DictReader(CANDIDATES.open(encoding="utf-8-sig", newline="")))
        saved_mentions = list(csv.DictReader(MENTIONS.open(encoding="utf-8-sig", newline="")))
        require(len(saved) == 12749 and len(saved_candidates) == 11570 and len(saved_mentions) == 27509, "post-write table counts differ")
        require(all((saved_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is True for sid in TRUE_NOTES), "post-write true flags differ")
        require(all((saved_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is False for sid in FALSE_NOTES), "post-write false flags differ")
        require(saved_by_id[PROMOTED_ID].get("object_candidate_id") == "cand-3967", "post-write endpoint differs")
        require(NEW_STATEMENT_ID in saved_by_id and saved_by_id[NEW_STATEMENT_ID].get("object_candidate_id") == NEW_CANDIDATE_ID, "post-write split statement missing")
        require(all(digest(path) == hashlib.sha256(payload).hexdigest() for path, payload in encoded.items()), "post-write hashes differ")
    except Exception:
        for path, backup in BACKUPS.items():
            if backup.exists():
                shutil.copy2(backup, path)
        raise
    report["result"] = "applied"
    report["backups"] = [str(path.relative_to(ROOT)) for path in BACKUPS.values()]
    report["sha256_after"] = {str(path.relative_to(ROOT)): digest(path) for path in encoded}
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
