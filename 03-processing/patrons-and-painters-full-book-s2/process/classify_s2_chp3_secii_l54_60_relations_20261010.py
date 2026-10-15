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
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-3.pdf"
SEGMENT = "chp-3:03_CHP-3_sec_ii:l54-60"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp3-sec-ii-l54-60-relations-20261010"

HASHES = {
    STATEMENTS: "a8209160e11c53df3a79ec9838ffd7ba5f3eddfe027c420c0b77b6406fef2f2f",
    CANDIDATES: "c8be066459de9f9819989899c04a85e6b86287843b3c67751b469daa3dc812ca",
    MENTIONS: "136c4227f382f12d0156a92d34c5572072be0ee6a5ccdcda0a1a9cac4947c0f8",
    COVERAGE: "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SOURCE: "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
}

TRUE_NOTES = {
    "st-chp3-secii-l54-60-animuccia-first-book-intent":
        "Animuccia says he published the first Laudi book for Oratory attendees; this records a publication and audience relation.",
    "st-chp3-secii-l54-60-animuccia-oratory-growth-and-second-book":
        "Animuccia links growth in Oratory attendance to his decision to develop harmonies and variety in the second book; preserve the quoted attribution and causal sequence.",
    "st-chp3-secii-l54-60-cesi-promised-high-altar-decoration":
        "Haskell says Cardinal Angelo Cesi promised decoration for the High Altar; same-person identity alignment remains for S3.",
    "st-chp3-secii-l54-60-conditional-300-scudi-offer":
        "Serra's proposed 300-scudi contribution was conditional on assigning the altarpiece to Rubens; neither acceptance nor payment is inferred here.",
    "st-chp3-secii-l54-60-conflict-society-and-church-decoration":
        "Haskell explicitly describes a conflict between the Congregation and fashionable society and says it appeared in church decoration; the unnamed group remains bounded to this passage.",
    "st-chp3-secii-l54-60-decoration-funds-absorbed-by-facade-costs":
        "Haskell reports that funds set aside for High Altar decoration were absorbed by unexpected façade costs; retain the provisional antecedent and do not infer a transfer mechanism.",
    "st-chp3-secii-l54-60-haskell-musical-shift":
        "Haskell interprets the attendance of prelates and distinguished gentlemen as influencing Animuccia's musical approach; map the subject to that exact unnamed group, not to the Oratorians.",
    "st-chp3-secii-l54-60-high-altar-nativity-dedication":
        "Haskell identifies the High Altar's original dedication as the Nativity; this is a place-to-dedication relation.",
    "st-chp3-secii-l54-60-oratorians-cautious-about-rubens":
        "Haskell reports the Oratorians' reluctance about assigning the main commission to a Flemish artist; this is their reported stance, not a final refusal.",
    "st-chp3-secii-l54-60-oratorians-decided-to-move-image":
        "Haskell reports a decision to move the preserved image to the High Altar; the decision is not treated as proof that the move was completed.",
    "st-chp3-secii-l54-60-oratorians-possibly-welcomed-entombment":
        "Haskell says the Oratorians may have welcomed the Entombment; retain the explicit possibility and do not equate it with a formal commission or approval.",
    "st-chp3-secii-l54-60-serra-anxious-to-promote-rubens":
        "Haskell says Serra was particularly anxious to promote Rubens; footnote 3 separately notes Serra's patronage of Guercino and does not independently verify this claim.",
    "st-chp3-secii-l54-60-serra-approached-oratorians-in-crisis":
        "Haskell says Serra approached the Oratorians during the crisis; retain this as a reported contact in the source narrative.",
    "st-chp3-secii-l54-60-vittrice-commissioned-entombment":
        "Haskell says Vittrice commissioned Caravaggio's Entombment for his family chapel about 1601; the chapel and commission circumstances remain limited as stated.",
    "st-chp3-secii-l54-60-vittrice-nephew-of-philip-friend":
        "Haskell identifies Vittrice as nephew of one unnamed close friend of Philip Neri; do not convert this into a direct kinship relation to Philip.",
}

FALSE_NOTES = {
    "st-chp3-secii-l54-60-angelo-cesi-died-1606":
        "This is a person's death-date attribute, not an inter-entity relation; retain the provisional candidate mapping for identity alignment.",
    "st-chp3-secii-l54-60-animuccia-first-book-simple-devotional-style":
        "This records the quoted composer's stated stylistic aim for the work, not a relation between distinct entities.",
    "st-chp3-secii-l54-60-animuccia-variety-and-avoidance-of-complexity":
        "This describes compositional features and choices in the second book; it is not a separate entity-to-entity relation.",
    "st-chp3-secii-l54-60-caravaggio-orthodox-treatment":
        "This is Haskell's qualified stylistic assessment of Caravaggio's treatment of the work, not an inter-entity relation.",
    "st-chp3-secii-l54-60-commission-circumstances-not-clarified":
        "This reports Haskell's state-of-knowledge caveat about a commission; it does not assert a historical relation beyond the separately recorded commission claim.",
    "st-chp3-secii-l54-60-next-picture-pressure-on-oratorians":
        "This is Haskell's interpretive characterization of how the picture entered the church, not a distinct entity relation; the commission and reception claims are recorded separately.",
}

ANCHORS = {
    "st-chp3-secii-l54-60-angelo-cesi-died-1606": "In 1606 Cardinal Cesi died",
    "st-chp3-secii-l54-60-animuccia-first-book-intent": "I published my first book of Landi for the consolation",
    "st-chp3-secii-l54-60-animuccia-first-book-simple-devotional-style": "I tried to maintain a certain simplicity",
    "st-chp3-secii-l54-60-animuccia-oratory-growth-and-second-book": "Oratory having, by the grace of God, steadily grown",
    "st-chp3-secii-l54-60-animuccia-variety-and-avoidance-of-complexity": "I have refrained as far as I can from the complications",
    "st-chp3-secii-l54-60-caravaggio-orthodox-treatment": "special trouble to produce a somewhat more orthodox treatment",
    "st-chp3-secii-l54-60-cesi-promised-high-altar-decoration": "decoration had been promised by Cardinal Angelo Cesi",
    "st-chp3-secii-l54-60-commission-circumstances-not-clarified": "commission have not yet been clarified",
    "st-chp3-secii-l54-60-conditional-300-scudi-offer": "Serra would pay 300 scudi towards its cost",
    "st-chp3-secii-l54-60-conflict-society-and-church-decoration": "conflict between the Congregation itself and the fashionable society",
    "st-chp3-secii-l54-60-decoration-funds-absorbed-by-facade-costs": "money set aside for its decoration was found to have been absorbed",
    "st-chp3-secii-l54-60-haskell-musical-shift": "presence of ‘prelates and most distinguished gentlemen’ led to the artist",
    "st-chp3-secii-l54-60-high-altar-nativity-dedication": "High Altar had been originally dedicated to the Nativity",
    "st-chp3-secii-l54-60-next-picture-pressure-on-oratorians": "way in which the next great picture entered the church",
    "st-chp3-secii-l54-60-oratorians-cautious-about-rubens": "And yet the Oratorians were cautious",
    "st-chp3-secii-l54-60-oratorians-decided-to-move-image": "A majority of the Oratorians, after much debating, decided to move",
    "st-chp3-secii-l54-60-oratorians-possibly-welcomed-entombment": "possible that the Oratorians welcomed the picture",
    "st-chp3-secii-l54-60-serra-anxious-to-promote-rubens": "particularly anxious to promote,,a young Flemish painter",
    "st-chp3-secii-l54-60-serra-approached-oratorians-in-crisis": "approached by a highly influential cleric, Monsignor Giacomo",
    "st-chp3-secii-l54-60-vittrice-commissioned-entombment": "commissioned a picture from Caravaggio of The Entombment",
    "st-chp3-secii-l54-60-vittrice-nephew-of-philip-friend": "nephew of one of St Philip’s closest friends",
}

EXPECTED_BEFORE = {
    "statements": 12713,
    "candidates": 11567,
    "mentions": 27506,
    "bilateral": 8509,
    "bilateral_true": 4632,
    "bilateral_false": 460,
    "bilateral_pending": 3417,
    "relation_candidates_total": 4679,
    "relation_candidates_open": 47,
}

EXPECTED_AFTER = {
    "statements": 12713,
    "candidates": 11567,
    "mentions": 27506,
    "bilateral": 8509,
    "bilateral_true": 4647,
    "bilateral_false": 465,
    "bilateral_pending": 3397,
    "relation_candidates_total": 4694,
    "relation_candidates_open": 47,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(value: str) -> str:
    return " ".join(value.split())


def parse_jsonl(raw: bytes):
    parsed = []
    offset = 0
    for line in raw.splitlines(keepends=True):
        if line.strip():
            parsed.append((json.loads(line), offset, offset + len(line), line))
        offset += len(line)
    return parsed


def has_endpoint(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def csv_rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def stats(statements, candidates, mentions):
    bilateral = [
        row for row in statements
        if has_endpoint(row.get("subject_candidate_id")) and has_endpoint(row.get("object_candidate_id"))
    ]

    def flag(row):
        return (row.get("qualifiers") or {}).get("relation_candidate")

    return {
        "statements": len(statements),
        "candidates": len(candidates),
        "mentions": len(mentions),
        "bilateral": len(bilateral),
        "bilateral_true": sum(flag(row) is True for row in bilateral),
        "bilateral_false": sum(flag(row) is False for row in bilateral),
        "bilateral_pending": sum(flag(row) is None for row in bilateral),
        "relation_candidates_total": sum(flag(row) is True for row in statements),
        "relation_candidates_open": sum(
            flag(row) is True
            and not (has_endpoint(row.get("subject_candidate_id")) and has_endpoint(row.get("object_candidate_id")))
            for row in statements
        ),
    }


def atomic_replace(path: Path, data: bytes):
    fd, temp_name = tempfile.mkstemp(prefix=f"{path.stem}.s2-l54-60.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


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

    coverage = [row for row in csv_rows(COVERAGE) if row["segment_id"] == SEGMENT]
    if len(coverage) != 1 or (
        coverage[0]["disposition"], coverage[0]["migration_status"], coverage[0]["source_line_ranges"]
    ) != ("reviewed", "complete", "L55-60"):
        raise SystemExit(f"unexpected coverage row: {coverage}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[53:60])
    statement_raw = STATEMENTS.read_bytes()
    parsed = parse_jsonl(statement_raw)
    rows = [row for row, _, _, _ in parsed]
    segment_rows = [row for row in rows if row.get("segment_id") == SEGMENT]
    targets = {row["statement_id"]: row for row in segment_rows}
    expected_ids = set(TRUE_NOTES) | set(FALSE_NOTES)
    if len(segment_rows) != 21 or set(targets) != expected_ids:
        raise SystemExit(f"unexpected target statements: rows={len(segment_rows)} ids={len(targets)}")
    if any((row.get("qualifiers") or {}).get("relation_candidate") is not None for row in segment_rows):
        raise SystemExit("one or more target statements already have a relation decision")
    if sum(has_endpoint(row.get("subject_candidate_id")) and has_endpoint(row.get("object_candidate_id")) for row in segment_rows) != 20:
        raise SystemExit("expected exactly 20 bilateral statements")
    single = [row for row in segment_rows if not has_endpoint(row.get("subject_candidate_id")) or not has_endpoint(row.get("object_candidate_id"))]
    if len(single) != 1 or single[0]["statement_id"] != "st-chp3-secii-l54-60-angelo-cesi-died-1606":
        raise SystemExit(f"unexpected single-end statement: {[row['statement_id'] for row in single]}")

    source_text = normalize("\n".join(source_lines[53:60]))
    for statement_id, anchor in ANCHORS.items():
        row = targets[statement_id]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start > end:
            raise SystemExit(f"invalid locator for {statement_id}: {q}")
        if normalize(anchor) not in normalize(row.get("original_quote", "")):
            raise SystemExit(f"anchor absent from original_quote: {statement_id}")
        if normalize(anchor) not in normalize("\n".join(source_lines[start - 1:end])):
            raise SystemExit(f"anchor absent from cited S0 lines: {statement_id}")
    if "Landi" not in source_text or "Serra was also a patron" not in "\n".join(source_lines[143:158]):
        raise SystemExit("source context changed")

    candidates = csv_rows(CANDIDATES)
    mentions = csv_rows(MENTIONS)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if candidate_by_id.get("cand-5056", {}).get("canonical_name") != "Prelates and distinguished gentlemen attending the Oratory (unnamed group)":
        raise SystemExit("the exact named attendee-group candidate changed")
    exact_group_mention = mention_by_id.get("m-chp3-secii-l54-60-0009")
    if not exact_group_mention or (
        exact_group_mention["candidate_id"], exact_group_mention["surface_form"]
    ) != ("cand-5056", "prelates and most distinguished gentlemen"):
        raise SystemExit("the Haskell-paraphrase group mention changed")
    if segment_text[int(exact_group_mention["start_char"]):int(exact_group_mention["end_char"])] != exact_group_mention["surface_form"]:
        raise SystemExit("the exact group mention span does not match the segment")

    note_links = {row["statement_id"]: (row.get("qualifiers") or {}).get("linked_body_statement_ids", []) for row in rows}
    required_note_links = {
        "st-chp3-secii-p69-p70-note1-friedlaender": {"st-chp3-secii-l54-60-commission-circumstances-not-clarified"},
        "st-chp3-secii-p69-p70-note1-cozzi": {"st-chp3-secii-l54-60-commission-circumstances-not-clarified"},
        "st-chp3-secii-p70-note2-jaffe": {
            "st-chp3-secii-l54-60-oratorians-decided-to-move-image",
            "st-chp3-secii-l54-60-decoration-funds-absorbed-by-facade-costs",
        },
        "st-chp3-secii-p70-note3-mahon-citation": {"st-chp3-secii-l54-60-serra-anxious-to-promote-rubens"},
        "st-chp3-secii-p70-note3-serra-guercino-patronage": {"st-chp3-secii-l54-60-serra-anxious-to-promote-rubens"},
    }
    for note_id, expected_body_ids in required_note_links.items():
        if not expected_body_ids.issubset(set(note_links.get(note_id, []))):
            raise SystemExit(f"required p.70 note back-links missing for {note_id}")

    before = stats(rows, candidates, mentions)
    if before != EXPECTED_BEFORE:
        raise SystemExit(f"unexpected pre-write counts: {before}")

    replacements = {}
    for statement_id, note in {**TRUE_NOTES, **FALSE_NOTES}.items():
        updated = dict(targets[statement_id])
        q = dict(updated.get("qualifiers", {}))
        q["relation_candidate"] = statement_id in TRUE_NOTES
        q["relation_candidate_note"] = note
        updated["qualifiers"] = q
        replacements[statement_id] = updated

    musical_id = "st-chp3-secii-l54-60-haskell-musical-shift"
    replacements[musical_id]["subject_candidate_id"] = "cand-5056"
    replacements[musical_id]["qualifiers"]["group_candidate_id"] = "cand-5056"

    serra_id = "st-chp3-secii-l54-60-serra-anxious-to-promote-rubens"
    serra_q = replacements[serra_id]["qualifiers"]
    corrections = list(serra_q.get("ocr_corrections", []))
    correction = {
        "source_file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
        "source_line": 60,
        "ocr": "promote,,a young",
        "print": "promote, a young",
        "basis": "CHP-3.pdf physical page 8, printed page 70",
    }
    if correction not in corrections:
        corrections.append(correction)
    serra_q["ocr_corrections"] = corrections

    pieces = []
    for row, _, _, raw_line in parsed:
        statement_id = row.get("statement_id")
        if statement_id in replacements:
            pieces.append(json.dumps(replacements[statement_id], ensure_ascii=False, separators=(",", ":")).encode("utf-8") + (b"\r\n" if raw_line.endswith(b"\r\n") else b"\n"))
        else:
            pieces.append(raw_line)
    projected_bytes = b"".join(pieces)
    projected_rows = [row for row, _, _, _ in parse_jsonl(projected_bytes)]
    if len({row["statement_id"] for row in projected_rows}) != len(projected_rows):
        raise SystemExit("statement IDs are not unique after projection")
    projected_segment = [row for row in projected_rows if row.get("segment_id") == SEGMENT]
    if len(projected_segment) != 21:
        raise SystemExit("target segment row count changed")
    final_stats = stats(projected_rows, candidates, mentions)
    if final_stats != EXPECTED_AFTER:
        raise SystemExit(f"unexpected projected counts: {final_stats}")
    target_true = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in projected_segment)
    target_false = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in projected_segment)
    if (target_true, target_false) != (15, 6):
        raise SystemExit(f"unexpected target classification: true={target_true}, false={target_false}")

    print(json.dumps({
        "mode": "dry-run" if args.dry_run else "apply",
        "segment_id": SEGMENT,
        "print_page": 70,
        "physical_pdf_page": 8,
        "classified_statements": {"relation_candidates": target_true, "nonrelations": target_false},
        "endpoint_correction": {"statement_id": musical_id, "subject_candidate_id": "cand-5056"},
        "ocr_correction_recorded": correction,
        "validated_note_links": sorted(required_note_links),
        "before": before,
        "after": final_stats,
        "backup": str(BACKUP.relative_to(ROOT)) if args.apply else None,
    }, ensure_ascii=False, indent=2))

    if args.dry_run:
        return

    shutil.copy2(STATEMENTS, BACKUP)
    atomic_replace(STATEMENTS, projected_bytes)
    written = [row for row, _, _, _ in parse_jsonl(STATEMENTS.read_bytes())]
    written_stats = stats(written, candidates, mentions)
    actual_segment = [row for row in written if row.get("segment_id") == SEGMENT]
    if written_stats != EXPECTED_AFTER or sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in actual_segment) != 15:
        raise SystemExit(f"post-write verification failed; backup retained: {written_stats}")
    print(json.dumps({
        "post_write_sha256": sha256(STATEMENTS),
        "post_write_counts": written_stats,
        "recovery_backup_retained": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
