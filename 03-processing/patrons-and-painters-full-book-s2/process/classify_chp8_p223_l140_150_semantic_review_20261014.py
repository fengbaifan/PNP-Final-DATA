"""Guarded S2 semantic review for printed p.223, body lines 140-150."""
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
SEGMENT = "chp-8:08_CHP-8_sec_ii:l140-150"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p223_review.png"
BACKUP_SUFFIX = ".bak-s2-chp8-p223-l140-150-semantic-review-20261014"
EXPECTED = {
    STATEMENTS: "9898daf8fb7fda130e623ae1d859ebc91c8f32ef665866bb405fd8bf82431b57",
    CANDIDATES: "6c2c6eeee85a3314c399a1b6645b703ba6a62c358fdf528a067fb45dac6f3a9f",
    MENTIONS: "5f981841ba915d413f6bef6c38c3a98a1050244d275877d728cfd205b8bb5e22",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PAGE_IMAGE: "53e868519a85851c4f7e264695975594b6bcdb546ce2d25f2b690ffad4c43605",
}

CLASSIFICATIONS = {
    "st-chp8-p223-buonaccorsi-palace-and-patronage": (False,
        "This is Haskell's interpretation of the decoration as evidence of patronage; it does not assert a specific commission or maker."),
    "st-chp8-p223-family-church-connection": (False,
        "The source calls the family's connection with the Church close but does not specify a relation type or institutional scope."),
    "st-chp8-p223-francesca-eighteen-children": (False,
        "This is a source-reported count and date; the passage identifies only Simone and supplies no child-group endpoint."),
    "st-chp8-p223-n2-zanotti-citation": (False,
        "This is a bibliographic locator for the preceding claim, not a historical relation; retain it as citation metadata."),
    "st-chp8-p223-palace-superlative-open": (False,
        "This is Haskell's evaluative comparison of the palace; its continuation is linked to p.224."),
    "st-chp8-p223-palazzo-cibo-gallery-characterization": (False,
        "This is Haskell's retrospective stylistic inference about the gallery, not a relation between distinct entities."),
    "st-chp8-p223-raimondo-born-into-family": (True,
        "The source explicitly says Raimondo was born into this unidentified family; preserve the family as an open group."),
    "st-chp8-p223-raimondo-characterization-from-limited-letters": (False,
        "This is Haskell's explicitly tentative personality sketch based on sparse letters mediated by later writers."),
    "st-chp8-p223-raimondo-died": (False,
        "This is a biographical date claim, not a relation between entities."),
    "st-chp8-p223-raimondo-lived-macerata": (True,
        "The source explicitly locates Raimondo's residence in Macerata."),
    "st-chp8-p223-raimondo-patron-range": (True,
        "The source directly describes Raimondo's picture-seeking activity across Italy; retain Haskell's broad geographic scope."),
    "st-chp8-p223-ruffo-affinity-for-creti": (True,
        "This isolates Ruffo's reported arrangement for Creti to receive an honor; p.222 separately records the reported patron-artist affinity and attendance."),
    "st-chp8-p223-ruffo-neapolitan-attachment": (False,
        "This is Haskell's characterization of Ruffo's cultural attachment, not a specified affiliation or residence relation."),
    "st-chp8-p223-ruffo-opinion-of-roman-artists": (False,
        "This reports Ruffo's attributed evaluation of a broad artist group, not a formal relation."),
    "st-chp8-p223-ruffo-retirement-to-rome": (True,
        "The source explicitly says Ruffo retired to Rome; the separate turn to compatriots is recorded below."),
    "st-chp8-p223-simone-cardinal": (False,
        "This preserves a future biographical status claim; the taxonomy does not treat a title by itself as an entity endpoint."),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line]


def write_jsonl(rows):
    return ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def csv_bytes(path: Path, rows):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        headers = next(csv.reader(f))
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=headers, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
        temp = Path(f.name)
        f.write(data)
    temp.replace(path)


def verify_inputs():
    for path, expected in EXPECTED.items():
        actual = sha(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"input changed: {path.relative_to(ROOT)} sha256={actual}")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    for start, end, quote in [
        (141, 141, "had him created Cavaliere dello speron d'oro"),
        (144, 144, "and when he retired to Rome"),
        (144, 144, "to his compatriots that he turned"),
        (145, 145, "Lorenzo in Damaso was decorated by Sebastiano Cbnca"),
        (142, 142, "Russo commissioned religious paintings and histories"),
    ]:
        excerpt = "\n".join(source_lines[start - 1:end])
        if quote not in excerpt:
            raise SystemExit(f"source excerpt mismatch at L{start}-{end}: {quote}")


def plan():
    statements = read_jsonl(STATEMENTS)
    candidates = read_csv(CANDIDATES)
    mentions = read_csv(MENTIONS)
    by_id = {r["statement_id"]: r for r in statements}
    seg_rows = [r for r in statements if r.get("segment_id") == SEGMENT]
    unset = {r["statement_id"] for r in seg_rows
             if "relation_candidate" not in r.get("qualifiers", {})}
    if len(seg_rows) != 35 or unset != set(CLASSIFICATIONS):
        raise SystemExit(f"unexpected p223 statement state: rows={len(seg_rows)} unset={sorted(unset)}")
    if "cand-12082" in {r["candidate_id"] for r in candidates}:
        raise SystemExit("candidate cand-12082 already exists")
    if "m-chp8-p223-neapolitan-compatriots" in {r["mention_id"] for r in mentions}:
        raise SystemExit("Neapolitan compatriots mention already exists")
    if "st-chp8-p223-ruffo-turns-to-neapolitan-compatriots" in by_id:
        raise SystemExit("compatriots statement already exists")

    for statement_id, (is_relation, note) in CLASSIFICATIONS.items():
        q = by_id[statement_id]["qualifiers"]
        q["relation_candidate"] = is_relation
        q["relation_candidate_note"] = note

    # Resolve clear source-reading errors against CHP-8.pdf physical page 25.
    by_id["st-chp8-p223-raimondo-characterization-from-limited-letters"]["qualifiers"]["ocr_corrections"] = [
        {"source_file": SOURCE_REL, "source_line": 148, "ocr": "also-ambitious", "print": "also ambitious",
         "basis": "CHP-8.pdf physical page 25."}
    ]
    by_id["st-chp8-p223-family-church-connection"]["qualifiers"]["ocr_corrections"] = [
        {"source_file": SOURCE_REL, "source_line": 147, "ocr": "Church?", "print": "Church",
         "basis": "CHP-8.pdf physical page 25; superscript note marker 4 follows."}
    ]
    for sid in ["st-chp8-p223-ruffo-commissions-cignani",
                "st-chp8-p223-ruffo-commissions-franceschini",
                "st-chp8-p223-ruffo-commissions-dal-sole",
                "st-chp8-p223-ruffo-commissions-gambarini"]:
        by_id[sid]["qualifiers"]["ocr_corrections"] = [
            {"source_file": SOURCE_REL, "source_line": 142, "ocr": "Russo", "print": "Ruffo",
             "basis": "CHP-8.pdf physical page 25."}
        ]
    for sid in ["st-chp8-p223-giaquinto-decorated-chapel",
                "st-chp8-p223-conca-other-pictures-for-ruffo"]:
        by_id[sid]["qualifiers"]["ocr_corrections"] = [
            {"source_file": SOURCE_REL, "source_line": 145, "ocr": "Cbnca", "print": "Conca",
             "basis": "CHP-8.pdf physical page 25."}
        ]

    conca = by_id["st-chp8-p223-conca-decorated-chapel"]
    conca["qualifiers"]["claim"] = "Haskell names Sebastiano Conca as one of the artists who decorated Ruffo's chapel at S. Lorenzo in Damaso."
    conca["qualifiers"]["ocr_corrections"] = [
        {"source_file": SOURCE_REL, "source_line": 145, "ocr": "Cbnca", "print": "Conca",
         "basis": "CHP-8.pdf physical page 25."}
    ]
    conca["original_quote"] = "Lorenzo in Damaso was decorated by Sebastiano Cbnca"

    dance = by_id["st-chp8-p223-creti-dance-of-nymphs"]
    dance["original_quote"] = "He owned at least two paintings by him of scenes from the life of Solomon and a Dance of Nymphs described by the artist’s biographer as a capriccio pittoresco with twenty-four figures."
    solomon = by_id["st-chp8-p223-creti-solomon-paintings"]
    solomon["original_quote"] = "He owned at least two paintings by him of scenes from the life of Solomon"

    honor = by_id["st-chp8-p223-ruffo-affinity-for-creti"]
    honor["predicate"] = "arranged_for_artist_to_receive_honor"
    honor["qualifiers"]["claim"] = "Haskell says Ruffo arranged for Donato Creti to receive the title Cavaliere dello speron d'oro."
    honor["qualifiers"]["qualification"] = "The honor's conferring authority and date are not stated; this row isolates the title arrangement from p.222's report of Ruffo watching Creti work."
    honor["qualifiers"]["relation_candidate"] = True
    honor["qualifiers"]["relation_candidate_note"] = "This is an explicit patron-to-artist action concerning an honor; do not infer the conferring authority or date."
    honor["original_quote"] = "had him created Cavaliere dello speron d'oro"

    retire = by_id["st-chp8-p223-ruffo-retirement-to-rome"]
    retire["predicate"] = "retired_to"
    retire["qualifiers"]["claim"] = "Haskell says that Ruffo retired to Rome."
    retire["qualifiers"]["mentioned_candidate_ids"] = ["cand-2304", "cand-4490"]
    retire["qualifiers"]["relation_candidate"] = True
    retire["qualifiers"]["relation_candidate_note"] = CLASSIFICATIONS["st-chp8-p223-ruffo-retirement-to-rome"][1]
    retire["original_quote"] = "and when he retired to Rome"

    italy = next(r for r in candidates if r["candidate_id"] == "cand-3461")
    italy["suggested_type"] = "place"
    italy["detail"] = "Geographic area Haskell says Raimondo Buonaccorsi ranged over while seeking pictures; the passage does not enumerate journeys or works."
    family = next(r for r in candidates if r["candidate_id"] == "cand-7729")
    family["suggested_type"] = "family"

    candidate = {
        "candidate_id": "cand-12082", "index_entry_id": "",
        "canonical_name": "Ruffo's Neapolitan compatriots (unnamed group)",
        "index_page_range": "", "suggested_type": "", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "The passage says that after retiring to Rome Ruffo again turned to his Neapolitan compatriots; it names no members and does not define the full group.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L144",
    }
    candidates.append(candidate)

    source_text = "\n".join(SOURCE.read_text(encoding="utf-8-sig").splitlines()[139:150])
    start, end = 930, 941
    if source_text[start:end] != "compatriots":
        raise SystemExit("compatriots mention span no longer matches source")
    mentions.append({
        "mention_id": "m-chp8-p223-neapolitan-compatriots", "segment_id": SEGMENT,
        "candidate_id": "cand-12082", "surface_form": "compatriots",
        "start_char": str(start), "end_char": str(end),
        "note": "Unnamed Neapolitan compatriot group Ruffo turned to after retiring to Rome; members are not identified.",
    })

    new_statement = {
        "statement_id": "st-chp8-p223-ruffo-turns-to-neapolitan-compatriots",
        "segment_id": SEGMENT, "subject_candidate_id": "cand-2304",
        "object_candidate_id": "cand-12082", "predicate": "turned_to_compatriot_group_after_retirement",
        "qualifiers": {
            "source_line_start": 144, "source_line_end": 144, "printed_page": 223,
            "pdf_physical_page": 25,
            "claim": "Haskell says that after retiring to Rome Ruffo again turned to his Neapolitan compatriots.",
            "speaker": "Haskell", "text_layer": "body",
            "qualification": "The group is unnamed; the sentence does not specify which commissions or people were involved.",
            "mentioned_candidate_ids": ["cand-2304", "cand-12082"],
            "relation_candidate": True,
            "relation_candidate_note": "The source explicitly describes Ruffo turning to this unnamed compatriot group; preserve it as an open collective endpoint.",
        },
        "original_quote": "to his compatriots that he turned", "origin": "book", "source_file": SOURCE_REL,
    }
    statements.append(new_statement)

    excerpt_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    for sid in ["st-chp8-p223-ruffo-affinity-for-creti",
                "st-chp8-p223-ruffo-retirement-to-rome",
                "st-chp8-p223-conca-decorated-chapel",
                "st-chp8-p223-creti-dance-of-nymphs",
                "st-chp8-p223-creti-solomon-paintings"]:
        r = by_id[sid]
        q = r["qualifiers"]
        excerpt = "\n".join(excerpt_lines[q["source_line_start"] - 1:q["source_line_end"]])
        if r["original_quote"] not in excerpt:
            raise SystemExit(f"exact source quote check failed: {sid}")
    if new_statement["original_quote"] not in excerpt_lines[143]:
        raise SystemExit("compatriots quote not found on L144")

    final = [r for r in statements if r.get("segment_id") == SEGMENT]
    summary = {
        "p223_original_rows": len(seg_rows), "new_statements": 1,
        "new_candidates": 1, "new_mentions": 1,
        "classified_previously_unset": len(CLASSIFICATIONS),
        "p223_final_statements": len(final),
        "p223_final_true": sum(r["qualifiers"].get("relation_candidate") is True for r in final),
        "p223_final_false": sum(r["qualifiers"].get("relation_candidate") is False for r in final),
        "p223_final_unset": sum("relation_candidate" not in r.get("qualifiers", {}) for r in final),
    }
    if (summary["p223_final_statements"], summary["p223_final_true"],
            summary["p223_final_false"], summary["p223_final_unset"]) != (36, 25, 11, 0):
        raise SystemExit(f"unexpected p223 plan totals: {summary}")
    return write_jsonl(statements), csv_bytes(CANDIDATES, candidates), csv_bytes(MENTIONS, mentions), summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write guarded plan; default dry-run")
    args = parser.parse_args()
    verify_inputs()
    statement_bytes, candidate_bytes, mention_bytes, summary = plan()
    print(json.dumps({"mode": "apply" if args.apply else "dry-run", **summary}, ensure_ascii=False, indent=2))
    if not args.apply:
        return
    verify_inputs()
    outputs = {STATEMENTS: statement_bytes, CANDIDATES: candidate_bytes, MENTIONS: mention_bytes}
    for path in outputs:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            if backup.read_bytes() != path.read_bytes():
                raise SystemExit(f"existing backup differs: {backup.name}")
        else:
            shutil.copy2(path, backup)
        if sha(backup.read_bytes()) != EXPECTED[path]:
            raise SystemExit(f"backup hash mismatch: {backup.name}")
    for path, data in outputs.items():
        atomic_write(path, data)
    print("written_sha256=" + json.dumps({p.name: sha(p.read_bytes()) for p in outputs}, ensure_ascii=False))


if __name__ == "__main__":
    main()
