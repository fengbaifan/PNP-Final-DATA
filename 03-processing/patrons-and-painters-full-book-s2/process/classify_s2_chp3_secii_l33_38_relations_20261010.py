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
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-3.pdf"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp3-sec-ii-l33-38-relations-20261010"
SEGMENT = "chp-3:03_CHP-3_sec_ii:l33-38"
SPLIT_ID = "st-chp3-secii-l33-38-philip-attracted-cultivated-people-and-decorated-church"
NEW_ID = "st-chp3-secii-l33-38-philip-personally-interested-in-church-decoration"

HASHES = {
    STATEMENTS: "348f0b4c11943b0a3534364184714afa338cb29f50e559fe65d46b54319c3fe3",
    CANDIDATES: "1de62da6b601a36870a3c59f6f892d11fcd67eff0adcaf732d3eed4470b61a92",
    COVERAGE: "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SOURCE: "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
}

# flag, note, line start, line end, subject, object, source quotation anchor
TARGETS = {
    "st-chp3-secii-l33-38-chiesa-nuova-built-on-general-lines-of-gesu": (True, "Haskell says Chiesa Nuova followed the same general lines as the Gesu; no exact design copying is asserted.", 38, 38, "cand-0710", "cand-3112", "church was built on the same general lines"),
    "st-chp3-secii-l33-38-chiesa-nuova-construction-circumstances-differed-from-gesu": (True, "Haskell compares the construction circumstances of Chiesa Nuova and the Gesu; the following passage supplies contrast, not an inferred cause.", 37, 37, "cand-0710", "cand-3112", "circumstances of its construction were very different"),
    "st-chp3-secii-l33-38-early-biographers-report-public-contributions": (True, "The biographical story says Romans rewarded Neri's faith with contributions; retain the reported-story qualification and named recipient.", 38, 38, "cand-5028", "cand-1898", "flooded him with generous contributions"),
    "st-chp3-secii-l33-38-early-biographers-story-of-neri-and-providence": (True, "Haskell reports early biographers' account of Neri ordering the old church demolished without knowing how to fund its successor; the account is immediately qualified.", 38, 38, "cand-1898", "cand-0710", "ordered the destruction of the old church"),
    "st-chp3-secii-l33-38-early-construction-proceeded-quickly": (False, "This is a temporal attribute of construction progress; the financial interruption continues in the next segment.", 38, 38, "cand-0710", "", "at first work proceeded quickly"),
    "st-chp3-secii-l33-38-farnese-obstructed-chiesa-nuova-as-potential-rival": (True, "Haskell reports Farnese's obstruction and attributes it to jealousy of Chiesa Nuova as a rival; motive remains Haskell's explanation.", 38, 38, "cand-0995", "cand-0710", "was obstructive"),
    "st-chp3-secii-l33-38-foundation-stone-laid-by-alessandro-de-medici": (True, "Haskell says Alessandro de' Medici laid the foundation stone in 1575; do not infer the unnamed Grand Duke or Alessandro's later papal identity.", 38, 38, "cand-0710", "cand-5025", "foundation stone was laid in 1575 by Alessandro"),
    "st-chp3-secii-l33-38-haskell-calls-richeome-last-lonely-voice": (True, "This preserves Haskell's characterization of Richeome as a last, lonely voice of a harsher Counter Reformation period; it does not mean the only writer.", 35, 36, "cand-2192", "cand-3396", "a last, lonely voice from the harsher days"),
    "st-chp3-secii-l33-38-haskell-qualifies-biographical-story-financial-difficulties": (False, "This is Haskell's appraisal of the biographical story's accuracy and a qualification about financial difficulty, not an entity relation.", 38, 38, "cand-0710", "", "This attractive story is not wholly accurate"),
    "st-chp3-secii-l33-38-haskell-says-simplicity-doctrine-unlikely-under-urban": (True, "Haskell says Richeome's argument was unlikely to be followed in Urban VIII's more prosperous and relaxed age; retain the qualified evaluation.", 36, 36, "cand-2192", "cand-3104", "at all likely to be followed in the more prosperous"),
    "st-chp3-secii-l33-38-jesuit-leaders-lacked-subtle-appreciation": (False, "This is Haskell's general aesthetic assessment of Jesuit leaders, not a relation to a separately identified object.", 37, 37, "cand-1321", "", "none of the Jesuit leaders showed any subtlety"),
    "st-chp3-secii-l33-38-new-church-not-dependent-on-one-patron": (True, "Haskell says Chiesa Nuova construction and decoration did not depend entirely on one all-powerful patron; keep negation scope and leave the unnamed patron endpoint open.", 38, 38, "cand-0710", "", "did not depend for its construction and decoration entirely"),
    "st-chp3-secii-l33-38-oratorian-contribution-outweighed-jesuits": (True, "Haskell compares the Oratorians' and Jesuits' artistic contributions in Rome during the first twenty years of the seventeenth century.", 37, 37, "cand-3402", "cand-1321", "very much more impressive than that of the Jesuits"),
    "st-chp3-secii-l33-38-oratorians-pioneers-through-taste-and-inspiration": (True, "Haskell links the Oratorians' artist selection and inspiration to their long-standing pioneer role; retain this authorial assessment.", 37, 37, "cand-3402", "cand-3396", "true pioneers among the"),
    "st-chp3-secii-l33-38-original-church-assigned-to-philip-1575": (True, "Haskell says Pope Gregory XIII assigned the original, smaller S. Maria della Vallicella to Philip Neri in 1575; keep it distinct from Chiesa Nuova.", 38, 38, "cand-5027", "cand-1898", "was assigned to him in 1575 by Pope Gregory XIII"),
    "st-chp3-secii-l33-38-original-church-in-fashionable-rome": (True, "Haskell places the original church in the heart of fashionable and cultivated Rome; the evaluative wording remains his.", 38, 38, "cand-5027", "cand-4490", "very heart of fashionable and cultivated Rome"),
    "st-chp3-secii-l33-38-original-church-small-and-replaced-by-chiesa-nuova": (True, "Haskell says the original church was demolished and replaced by a larger same-named building; preserve the two distinct church candidates.", 38, 38, "cand-5027", "cand-0710", "was pulled down to be replaced by a larger"),
    SPLIT_ID: (True, "Haskell says Philip Neri attracted many cultivated spirits; the unnamed group remains an open object endpoint.", 37, 37, "cand-1898", "cand-0710", "He naturally attracted to himself many"),
    "st-chp3-secii-l33-38-philip-neri-aesthetic-sensibility": (False, "This is Haskell's characterization of Neri's aesthetic sensibility and response to art and music, not an entity relation.", 37, 37, "cand-1898", "", "profoundest aesthetic sensibility"),
    "st-chp3-secii-l33-38-philip-worked-with-oratorian-chosen-matteo": (True, "Haskell says Philip Neri worked in close cooperation with Matteo da Castello, whom the Oratorians had chosen.", 38, 38, "cand-1898", "cand-0766", "worked in close co-operation with the architect Matteo da Castello"),
    "st-chp3-secii-l33-38-richeome-book-topic-paintings": (True, "Haskell says Richeome's 1611 book concerns paintings in S. Andrea and S. Vitale; the painting group endpoint is not modeled.", 34, 34, "cand-5024", "", "paintings in S. Andrea and S. Vitale"),
    "st-chp3-secii-l33-38-richeome-focused-devotion-on-fresco-subject": (True, "Haskell reports Richeome's prescription to focus devotion on fresco subjects read as sermons; keep the normative claim attributed and its object open.", 35, 35, "cand-2192", "", "subject-matter of the frescoes, which should be read like a sermon"),
    "st-chp3-secii-l33-38-richeome-rejected-extravagant-ornament": (True, "As quoted by Haskell, Richeome rejects extravagant ornament as irrelevant to devotion; the referenced ornament group remains open.", 34, 35, "cand-2192", "", "Extravagant pomp, he said, was nothing"),
}

EXPECTED_BEFORE = {
    "bilateral": 8499,
    "bilateral_true": 4575,
    "bilateral_false": 460,
    "bilateral_pending": 3464,
    "relation_candidates_total": 4617,
    "relation_candidates_open": 42,
}
EXPECTED_AFTER = {
    "bilateral": 8499,
    "bilateral_true": 4590,
    "bilateral_false": 460,
    "bilateral_pending": 3449,
    "relation_candidates_total": 4637,
    "relation_candidates_open": 47,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_jsonl(raw: bytes):
    parsed = []
    offset = 0
    for line in raw.splitlines(keepends=True):
        if line.strip():
            parsed.append((json.loads(line), offset, offset + len(line)))
        offset += len(line)
    return parsed


def has_endpoint(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def stats(rows):
    bilateral = [r for r in rows if has_endpoint(r.get("subject_candidate_id")) and has_endpoint(r.get("object_candidate_id"))]
    def flag(row):
        q = row.get("qualifiers", {})
        return q.get("relation_candidate") if isinstance(q, dict) else None
    return {
        "bilateral": len(bilateral),
        "bilateral_true": sum(flag(r) is True for r in bilateral),
        "bilateral_false": sum(flag(r) is False for r in bilateral),
        "bilateral_pending": sum(flag(r) is None for r in bilateral),
        "relation_candidates_total": sum(flag(r) is True for r in rows),
        "relation_candidates_open": sum(
            flag(r) is True and not (has_endpoint(r.get("subject_candidate_id")) and has_endpoint(r.get("object_candidate_id")))
            for r in rows
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    for path, expected in HASHES.items():
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"SHA mismatch for {path.relative_to(ROOT)}: {actual}")
    if BACKUP.exists():
        raise SystemExit(f"recovery backup already exists: {BACKUP}")

    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        coverage = [r for r in csv.DictReader(handle) if r["segment_id"] == SEGMENT]
    if len(coverage) != 1 or (
        coverage[0]["disposition"],
        coverage[0]["migration_status"],
        coverage[0]["source_line_ranges"],
    ) != ("reviewed", "complete", "L34-38"):
        raise SystemExit(f"unexpected coverage row: {coverage}")
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        candidate_ids = {r["candidate_id"] for r in csv.DictReader(handle)}

    raw = STATEMENTS.read_bytes()
    parsed = parse_jsonl(raw)
    rows = [r for r, _, _ in parsed]
    segment_rows = [r for r in rows if r.get("segment_id") == SEGMENT]
    targets = {r["statement_id"]: r for r in segment_rows if r.get("statement_id") in TARGETS}
    if len(segment_rows) != 23 or set(targets) != set(TARGETS):
        raise SystemExit(f"unexpected segment records: rows={len(segment_rows)}, target_ids={len(targets)}")
    if sum(1 for r in rows for value in r.values() if isinstance(value, str) and value == SPLIT_ID) != 1:
        raise SystemExit("the compound statement ID has unexpected references")
    if any(r.get("statement_id") == NEW_ID for r in rows):
        raise SystemExit(f"new split statement already exists: {NEW_ID}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for statement_id, (flag, note, start, end, subject, obj, anchor) in TARGETS.items():
        row = targets[statement_id]
        q = row.get("qualifiers", {})
        if "relation_candidate" in q:
            raise SystemExit(f"target already classified: {statement_id}")
        if (q.get("source_line_start"), q.get("source_line_end")) != (start, end):
            raise SystemExit(f"source locator changed for {statement_id}: {q}")
        if (row.get("subject_candidate_id"), row.get("object_candidate_id")) != (subject, obj):
            raise SystemExit(f"endpoint changed for {statement_id}: {row}")
        if anchor not in " ".join(row.get("original_quote", "").split()):
            raise SystemExit(f"quotation anchor changed for {statement_id}")
        if anchor not in " ".join(source_lines[start - 1:end]):
            raise SystemExit(f"source no longer contains {anchor!r} for {statement_id}")
        if (subject and subject not in candidate_ids) or (obj and obj not in candidate_ids):
            raise SystemExit(f"unresolved endpoint for {statement_id}")

    before = stats(rows)
    if before != EXPECTED_BEFORE:
        raise SystemExit(f"unexpected pre-write counts: {before}")

    replacements = {}
    for row, _, _ in parsed:
        statement_id = row.get("statement_id")
        if statement_id not in TARGETS:
            continue
        flag, note, *_ = TARGETS[statement_id]
        updated = dict(row)
        q = dict(row.get("qualifiers", {}))
        q["relation_candidate"] = flag
        q["relation_candidate_note"] = note
        if statement_id == SPLIT_ID:
            q["claim"] = "Haskell says Philip Neri naturally attracted many of the most cultivated spirits of the time."
            q["qualification"] = "The cultivated group is unnamed and not individually identified; preserve many."
            updated["object_candidate_id"] = ""
            updated["predicate"] = "attracted_many_cultivated_spirits"
            updated["original_quote"] = "He naturally attracted to himself many of the most cultivated spirits of the time."
        updated["qualifiers"] = q
        replacements[statement_id] = updated

    split_row = {
        "statement_id": NEW_ID,
        "segment_id": SEGMENT,
        "subject_candidate_id": "cand-1898",
        "object_candidate_id": "cand-0710",
        "predicate": "personally_interested_in_church_decoration",
        "qualifiers": {
            "source_line_start": 37,
            "source_line_end": 37,
            "claim": "Haskell says Philip Neri personally took an enthusiastic interest in decorating his church.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "print_page": 68,
            "pdf_physical_page": 6,
            "qualification": "This is the church-decoration clause; the adjacent claim about attracting cultivated spirits is recorded separately.",
            "relation_candidate": True,
            "relation_candidate_note": "Haskell reports Philip Neri's personal interest in decorating Chiesa Nuova; keep this distinct from the unnamed cultivated group he attracted.",
        },
        "original_quote": "he personally took an enthusiastic interest in the decoration of his church.",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
    }
    split_bytes = json.dumps(split_row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    pieces = []
    inserted = False
    for row, start, end in parsed:
        statement_id = row.get("statement_id")
        newline = b"\r\n" if raw[start:end].endswith(b"\r\n") else b"\n"
        if statement_id == SPLIT_ID:
            pieces.append(json.dumps(replacements[statement_id], ensure_ascii=False, separators=(",", ":")).encode("utf-8") + newline)
            pieces.append(split_bytes + newline)
            inserted = True
        elif statement_id in replacements:
            pieces.append(json.dumps(replacements[statement_id], ensure_ascii=False, separators=(",", ":")).encode("utf-8") + newline)
        else:
            pieces.append(raw[start:end])
    if not inserted:
        raise SystemExit("failed to locate compound statement for split")
    projected = b"".join(pieces)
    projected_rows = [r for r, _, _ in parse_jsonl(projected)]
    after = stats(projected_rows)
    if len(projected_rows) != 12704 or after != EXPECTED_AFTER:
        raise SystemExit(f"unexpected projected result: statements={len(projected_rows)}, stats={after}")
    ids = [r["statement_id"] for r in projected_rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("projected statement IDs are not unique")

    print(json.dumps({
        "mode": "dry-run" if args.dry_run else "apply",
        "segment_id": SEGMENT,
        "printed_page": 68,
        "source_statements_before": len(segment_rows),
        "source_statements_after": len([r for r in projected_rows if r.get("segment_id") == SEGMENT]),
        "split_compound_statement": SPLIT_ID,
        "new_statement_id": NEW_ID,
        "new_relation_candidates_including_split": sum(spec[0] for spec in TARGETS.values()) + 1,
        "new_nonrelations": sum(not spec[0] for spec in TARGETS.values()),
        "new_open_endpoint_candidates": sum(
            spec[0] and not (has_endpoint(spec[4]) and has_endpoint(spec[5]))
            for spec in TARGETS.values()
        ) + 1,
        "before": before,
        "after": after,
        "backup": str(BACKUP.relative_to(ROOT)) if args.apply else None,
    }, ensure_ascii=False, indent=2))
    if args.dry_run:
        return

    shutil.copy2(STATEMENTS, BACKUP)
    fd, temp_name = tempfile.mkstemp(prefix="book-statements.s2-chp3-secii-l33-38.", suffix=".tmp", dir=TABLES)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(projected)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, STATEMENTS)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise

    written = [r for r, _, _ in parse_jsonl(STATEMENTS.read_bytes())]
    written_stats = stats(written)
    if len(written) != 12704 or written_stats != EXPECTED_AFTER:
        raise SystemExit(f"post-write mismatch: statements={len(written)}, stats={written_stats}; backup retained")
    for row in written:
        if row.get("statement_id") not in TARGETS:
            continue
        flag, note, *_ = TARGETS[row["statement_id"]]
        q = row.get("qualifiers", {})
        if q.get("relation_candidate") is not flag or q.get("relation_candidate_note") != note:
            raise SystemExit(f"post-write classification mismatch: {row['statement_id']}; backup retained")
    new = next(r for r in written if r.get("statement_id") == NEW_ID)
    if new["qualifiers"].get("relation_candidate") is not True:
        raise SystemExit("split statement classification mismatch; backup retained")
    print(f"post_write_sha256={sha256(STATEMENTS)}")


if __name__ == "__main__":
    main()
