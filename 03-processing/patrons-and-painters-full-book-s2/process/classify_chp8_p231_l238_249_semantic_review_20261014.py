"""Guarded S2 semantic review for printed p.231, body lines 238-249."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p231_review.png"
SEGMENT = "chp-8:08_CHP-8_sec_ii:l238-249"
BACKUP_SUFFIX = ".bak-s2-chp8-p231-l238-249-semantic-review-20261014"
EXPECTED = {
    STATEMENTS: "3b72ed85d9092737303fbb93cf39ea98775e6b4c0a4d0bf2c73a0d590ad91bc5",
    CANDIDATES: "cef58d5f14f19f8ecf91813e872d269b54d813e102ad9656f341b824c7660693",
    MENTIONS: "beeb069f1c8907e9d9eaed835740042c04e9cefbc0203ed43cf0a6b478cbf60c",
    COVERAGE: "607342f702dafa6672481b4d0e71703a0427fc2e898242d816f13ad4465117f1",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PAGE_IMAGE: "f1b8df685028b48d946ea28456dcf6efc40283f6bf58c0521760dc33766b48cd",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def jsonl_bytes(rows):
    return ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")


def csv_bytes(fields, rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(data)
    temporary.replace(path)


def new_statement(statement_id, subject, object_, predicate, lines, claim, quote, *, note, mentioned):
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": lines[0],
            "source_line_end": lines[1],
            "printed_page": 231,
            "pdf_physical_page": 33,
            "claim": claim,
            "speaker": "Haskell",
            "text_layer": "body",
            "qualification": note,
            "mentioned_candidate_ids": mentioned,
            "relation_candidate": True,
            "relation_candidate_note": note,
            "speaker_judgment": True,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_REL,
    }


def plan():
    for path, expected in EXPECTED.items():
        actual = sha(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"input changed: {path.relative_to(ROOT)} sha256={actual}")

    segments = read_jsonl(SEGMENTS)
    meta = {row["segment_id"]: row for row in segments}.get(SEGMENT)
    if not meta or (meta["line_start"], meta["line_end"]) != (238, 249):
        raise SystemExit("unexpected p.231 segment metadata")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    if sha("\n".join(source_lines[237:249]).encode("utf-8")) != meta["sha256"]:
        raise SystemExit("p.231 source segment hash mismatch")

    candidate_fields, candidates = read_csv(CANDIDATES)
    mention_fields, mentions = read_csv(MENTIONS)
    statements = read_jsonl(STATEMENTS)
    coverage_fields, coverage = read_csv(COVERAGE)
    by_id = {row["statement_id"]: row for row in statements}
    target_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    if len(target_rows) != 18:
        raise SystemExit(f"expected 18 migrated p.231 statements; got {len(target_rows)}")
    expected_unset = {
        "st-chp8-p231-ferdinand-seduced-by-venetian-tradition",
        "st-chp8-p231-hosts-titian-veronese-bassano",
        "st-chp8-p231-la-burla-style-and-subject",
    }
    for statement_id in expected_unset:
        if statement_id not in by_id or by_id[statement_id]["qualifiers"].get("relation_candidate") is not None:
            raise SystemExit(f"unexpected status or missing statement: {statement_id}")
    coverage_row = next((row for row in coverage if row["segment_id"] == SEGMENT), None)
    if not coverage_row or (coverage_row["disposition"], coverage_row["migration_status"], coverage_row["source_line_ranges"]) != ("reviewed", "complete", "L238-249"):
        raise SystemExit(f"unexpected p.231 coverage state: {coverage_row}")

    lines = {i + 1: line for i, line in enumerate(source_lines)}
    l241, l242, l245 = lines[241], lines[242], lines[245]
    marker = " which had long been considered"
    if marker not in l241 or not l242.startswith("Florentine Renaissance."):
        raise SystemExit("unexpected p.231 antithesis sentence")
    q_perception = l241[:l241.index(marker)].rstrip()
    q_antithesis = l241[l241.index(marker) + 1:].rstrip() + "\n" + l242[:l242.index(" Ferdinand,")].rstrip()
    q_seduced = l242[l242.index("Ferdinand,"):].rstrip()
    comparison_end = " It was, however, not very long before"
    if comparison_end not in l245:
        raise SystemExit("unexpected p.231 La Burla comparison sentence")
    q_burla = l245[:l245.index(comparison_end)].rstrip()

    # Candidate numbering is guarded so a changed table cannot receive stale IDs.
    numeric_ids = [int(row["candidate_id"][5:]) for row in candidates if row["candidate_id"].startswith("cand-")]
    if max(numeric_ids) != 12093:
        raise SystemExit(f"unexpected maximum candidate ID: {max(numeric_ids)}")
    new_ids = [f"cand-{n:04d}" for n in (12094, 12095, 12096)]
    if any(row["candidate_id"] in new_ids for row in candidates):
        raise SystemExit("planned candidate ID already exists")
    new_candidates = [
        {
            "candidate_id": new_ids[0], "index_entry_id": "",
            "canonical_name": "Florentine Renaissance in Haskell's comparison with Venetian painting",
            "index_page_range": "", "suggested_type": "term", "status": "open",
            "index_source_file": "", "sub_entry": "",
            "detail": "Art-historical tradition named as the counterpart to the Venetian sixteenth-century painting tradition; Haskell says it had long been considered the latter's antithesis. Preserve this source framing and distinguish it from the geographic city of Florence and the generic Renaissance candidate.",
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT}#L242",
        },
        {
            "candidate_id": new_ids[1], "index_entry_id": "",
            "canonical_name": "Fifteenth-century Tuscan narrative tradition in Haskell's p.231 comparison",
            "index_page_range": "", "suggested_type": "term", "status": "open",
            "index_source_file": "", "sub_entry": "",
            "detail": "The regional narrative tradition that Haskell says informed La Burla del Pievano Arlotto in both style and subject inspiration; keep this source-local concept distinct from the geographic region Tuscany pending S3 alignment.",
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT}#L245",
        },
        {
            "candidate_id": new_ids[2], "index_entry_id": "",
            "canonical_name": "Contemporary experiments in naturalism in Haskell's p.231 comparison",
            "index_page_range": "", "suggested_type": "term", "status": "open",
            "index_source_file": "", "sub_entry": "",
            "detail": "Naturalistic experiments Haskell identifies as being made elsewhere in Italy at the time of the p.231 comparison; keep distinct from other naturalism candidates pending S3 alignment.",
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT}#L245",
        },
    ]

    classifications = {
        "st-chp8-p231-ferdinand-seduced-by-venetian-tradition": (
            True,
            "Haskell explicitly attributes Ferdinand's attraction to the Venetian tradition and wish to revive it; retain the person-to-tradition claim as an S2 relation candidate.",
        ),
    }
    for statement_id, (value, note) in classifications.items():
        row = by_id[statement_id]
        q = row["qualifiers"]
        q["relation_candidate"] = value
        q["relation_candidate_note"] = note
        row["original_quote"] = q_seduced
        q["source_line_start"] = 242
        q["source_line_end"] = 242
        q["claim"] = "Haskell says Ferdinand was seduced by the Venetian painting tradition and longed to make it live again."
        q["qualification"] = "This is Haskell's interpretation of Ferdinand's taste, not evidence of a specific completed commission."
        q["mentioned_candidate_ids"] = ["cand-1609", "cand-7875"]

    hosts = by_id["st-chp8-p231-hosts-titian-veronese-bassano"]
    hosts["original_quote"] = q_perception
    hosts["predicate"] = "recognized_venetian_painting_tradition_in_hosts_palace_masterpieces"
    hosts["qualifiers"].update({
        "source_line_start": 241, "source_line_end": 241,
        "claim": "Haskell says Ferdinand saw a Venetian painting tradition in masterpieces by Titian, Veronese and Bassano in his hosts' palaces.",
        "qualification": "The tradition is Haskell's account of Ferdinand's perception; the hosts' palaces and particular paintings are not identified.",
        "mentioned_candidate_ids": ["cand-1609", "cand-2630", "cand-2755", "cand-0257", "cand-7875"],
        "relation_candidate": True,
        "relation_candidate_note": "The source explicitly links Ferdinand's perception to a named art-historical tradition; retain as an attributed S2 relation candidate.",
        "speaker_judgment": True,
    })

    burla = by_id["st-chp8-p231-la-burla-style-and-subject"]
    burla["object_candidate_id"] = new_ids[1]
    burla["predicate"] = "painting_style_drew_more_on_tuscan_narrative_than_contemporary_naturalistic_experiments"
    burla["original_quote"] = q_burla
    burla["qualifiers"].update({
        "claim": "Haskell says La Burla's homely, archaic simplicity owed more in style to fifteenth-century Tuscan narrative than to contemporary experiments in naturalism elsewhere in Italy.",
        "qualification": "This is Haskell's comparative stylistic interpretation. The naturalistic experiments are the stated alternative, not the affirmative object of this relation; both concepts remain source-local pending later alignment.",
        "mentioned_candidate_ids": ["cand-7860", new_ids[1], new_ids[2], "cand-3461"],
        "relation_candidate": True,
        "relation_candidate_note": "A source-attributed work-to-style claim; the page's combined sentence is split so style and subject inspiration can be reviewed separately.",
        "speaker_judgment": True,
        "ocr_corrections": [{"source_line": 245, "ocr": "than.to", "print": "than to", "basis": "CHP-8.pdf physical page 33"}],
    })

    additions = [
        new_statement(
            "st-chp8-p231-venetian-tradition-antithesis-florentine-renaissance",
            "cand-7875", new_ids[0], "long_considered_antithesis_to_florentine_renaissance", (241, 242),
            "Haskell says the Venetian painting tradition had long been considered the antithesis to the Florentine Renaissance.",
            q_antithesis,
            note="The people who held this view are not identified; preserve Haskell's historical framing and keep the specific Florentine Renaissance concept distinct from generic Renaissance and Florence entries.",
            mentioned=["cand-7875", new_ids[0]],
        ),
        new_statement(
            "st-chp8-p231-la-burla-subject-inspiration",
            "cand-7860", new_ids[1], "subject_inspiration_drew_more_on_tuscan_narrative_than_contemporary_naturalistic_experiments", (245, 245),
            "Haskell says the inspiration of La Burla's subject owed more to fifteenth-century Tuscan narrative than to contemporary experiments in naturalism elsewhere in Italy.",
            q_burla,
            note="This is Haskell's comparative subject-inspiration interpretation. The naturalistic experiments are the stated alternative; both concepts remain source-local pending later alignment.",
            mentioned=["cand-7860", new_ids[1], new_ids[2], "cand-3461"],
        ),
    ]
    statement_ids = {row["statement_id"] for row in statements}
    for row in additions:
        if row["statement_id"] in statement_ids:
            raise SystemExit(f"statement ID already exists: {row['statement_id']}")
        statement_ids.add(row["statement_id"])

    candidates.extend(new_candidates)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    expected_mentions = {
        "m-chp8-p231-florentine": ("cand-3397", "Florentine"),
        "m-chp8-p231-renaissance-1": ("cand-3578", "Renaissance"),
        "m-chp8-p231-tuscan": ("cand-6232", "Tuscan"),
        "m-chp8-p231-naturalism": ("cand-5739", "naturalism"),
    }
    for mention_id, (candidate_id, surface) in expected_mentions.items():
        row = mention_by_id.get(mention_id)
        if not row or (row["candidate_id"], row["surface_form"]) != (candidate_id, surface):
            raise SystemExit(f"unexpected or missing mention: {mention_id}")

    offsets = {}
    offset = 0
    for line_no in range(meta["line_start"], meta["line_end"] + 1):
        offsets[line_no] = offset
        offset += len(lines[line_no]) + 1

    def set_mention(mention_id, candidate_id, surface, line_no):
        row = mention_by_id[mention_id]
        position = lines[line_no].find(surface)
        if position < 0 or lines[line_no].find(surface, position + 1) >= 0:
            raise SystemExit(f"source mention missing or ambiguous: {surface!r}")
        row.update({
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(offsets[line_no] + position),
            "end_char": str(offsets[line_no] + position + len(surface)),
        })

    set_mention("m-chp8-p231-florentine", new_ids[0], "Florentine Renaissance", 242)
    set_mention("m-chp8-p231-tuscan", new_ids[1], "Tuscan narrative of the fifteenth century", 245)
    set_mention("m-chp8-p231-naturalism", new_ids[2], "experiments in naturalism", 245)
    mentions = [row for row in mentions if row["mention_id"] != "m-chp8-p231-renaissance-1"]

    totals = {"true": 0, "false": 0, "unset": 0}
    for row in statements + additions:
        if row.get("segment_id") != SEGMENT:
            continue
        value = row.get("qualifiers", {}).get("relation_candidate")
        totals["true" if value is True else "false" if value is False else "unset"] += 1
    if totals["unset"]:
        raise SystemExit(f"p.231 remains unclassified: {totals}")

    coverage_row["note"] = (
        "p.231 body and notes L409-414 reviewed against CHP-8.pdf physical page 33; "
        "semantic review 2026-10-14 rechecked 18 existing statements, added 2 atomic statements "
        "and 3 source-local term candidates, corrected the Tuscan-narrative and naturalism mentions, "
        "and confirmed the final sentence closes at p.232 L252-253."
    )
    preview = {
        "mode": "dry-run", "segment": SEGMENT, "page_image": PAGE_IMAGE.relative_to(ROOT).as_posix(),
        "existing_statements_reviewed": len(target_rows),
        "new_statements": [row["statement_id"] for row in additions],
        "new_candidates": [row["candidate_id"] for row in new_candidates],
        "removed_duplicate_component_mention": "m-chp8-p231-renaissance-1",
        "final_statement_counts": totals,
        "semantic_fixes": [
            "split Ferdinand's recognition of the Venetian tradition from its historiographical contrast with the Florentine Renaissance",
            "narrow the seduction claim to its own sentence and preserve it as an attributed person-to-tradition candidate",
            "split La Burla's stylistic basis from its subject inspiration",
            "replace the incorrect Tuscany place mapping with source-local narrative and naturalism concepts",
        ],
    }
    payload = {
        STATEMENTS: jsonl_bytes(statements + additions),
        CANDIDATES: csv_bytes(candidate_fields, candidates),
        MENTIONS: csv_bytes(mention_fields, mentions),
        COVERAGE: csv_bytes(coverage_fields, coverage),
    }
    return preview, payload


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the preflighted p.231 S2 review")
args = parser.parse_args()
preview, payload = plan()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)
for path in (STATEMENTS, CANDIDATES, MENTIONS, COVERAGE):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)
for path, data in payload.items():
    atomic_write(path, data)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
