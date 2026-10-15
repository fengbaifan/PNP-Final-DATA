from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_sec_ii.md"
SEGMENT = "chp-10:10_CHP-10_sec_ii:l273-349"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp10-notes-l325-349-20261014")
EXPECTED = {
    TABLE.name: "76b98e2cd5ccd0d1e75b1baf707958c083b52c373c8c61260b4bf38d77f86806",
    SOURCE.name: "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9",
}

EXPECTED_IDS = {
    "st-chp10-p324-n1-pascoli-citation",
    "st-chp10-p324-n2-osservatore-citation",
    "st-chp10-p324-n3-dedication-compares-goldoni-and-longhi",
    "st-chp10-p324-n3-levey-affinity-citation",
    "st-chp10-p324-n4-gozzi-fable-source",
    "st-chp10-p325-n1-magggiotto-source-citations",
    "st-chp10-p325-n2-gozzi-letter-citation",
    "st-chp10-p325-n3-chapter-cross-reference",
    "st-chp10-p325-n4-grimaldo-citation",
    "st-chp10-p326-n01-pamphlet-titles",
    "st-chp10-p326-n02-molmenti-reference",
    "st-chp10-p326-n03-haskell-explanation",
    "st-chp10-p327-n01-grimaldo-balbi-citation",
    "st-chp10-p327-n02-zannandreis-citation",
    "st-chp10-p327-n03-moschini-citation",
    "st-chp10-p328-n01-la-harpe-ode-imprint",
    "st-chp10-p328-n02-zanetti-letter-citation",
    "st-chp10-p328-n03-baretti-locator",
    "st-chp10-p328-n04-venturi-locator",
    "st-chp10-p328-n05-biffi-letter-citation",
    "st-chp10-p328-n06-venturi-locator",
    "st-chp10-p328-n07-gazzetta-citation",
    "st-chp10-p329-n01-della-pittura-preface",
    "st-chp10-p329-n02-relazione-in-sagredo",
    "st-chp10-p329-n03-bassi-academy-study",
    "st-chp10-p329-n03-fogolari-academy-study",
    "st-chp10-p330-n01-memmo-sheet-appendix",
    "st-chp10-p330-n02-canaletto-hypothesis",
    "st-chp10-p330-n03-vasari-life",
    "st-chp10-p330-n04-haskell-levey",
    "st-chp10-p330-n04-i-nunzio-report",
}

UNSET_IDS = {
    "st-chp10-p324-n1-pascoli-citation",
    "st-chp10-p324-n2-osservatore-citation",
    "st-chp10-p324-n3-levey-affinity-citation",
    "st-chp10-p324-n4-gozzi-fable-source",
    "st-chp10-p325-n1-magggiotto-source-citations",
    "st-chp10-p325-n2-gozzi-letter-citation",
    "st-chp10-p325-n3-chapter-cross-reference",
    "st-chp10-p325-n4-grimaldo-citation",
    "st-chp10-p326-n01-pamphlet-titles",
    "st-chp10-p326-n02-molmenti-reference",
    "st-chp10-p327-n01-grimaldo-balbi-citation",
    "st-chp10-p327-n02-zannandreis-citation",
    "st-chp10-p328-n01-la-harpe-ode-imprint",
    "st-chp10-p328-n02-zanetti-letter-citation",
    "st-chp10-p328-n03-baretti-locator",
    "st-chp10-p328-n04-venturi-locator",
    "st-chp10-p328-n05-biffi-letter-citation",
    "st-chp10-p328-n06-venturi-locator",
    "st-chp10-p328-n07-gazzetta-citation",
    "st-chp10-p329-n01-della-pittura-preface",
    "st-chp10-p329-n02-relazione-in-sagredo",
    "st-chp10-p330-n01-memmo-sheet-appendix",
    "st-chp10-p330-n02-canaletto-hypothesis",
    "st-chp10-p330-n03-vasari-life",
    "st-chp10-p330-n04-haskell-levey",
    "st-chp10-p330-n04-i-nunzio-report",
}

CLASSIFICATIONS = {
    "st-chp10-p324-n1-pascoli-citation": False,
    "st-chp10-p324-n2-osservatore-citation": False,
    "st-chp10-p324-n3-levey-affinity-citation": False,
    "st-chp10-p324-n4-gozzi-fable-source": False,
    "st-chp10-p325-n1-magggiotto-source-citations": False,
    "st-chp10-p325-n2-gozzi-letter-citation": False,
    "st-chp10-p325-n3-chapter-cross-reference": False,
    "st-chp10-p325-n4-grimaldo-citation": False,
    "st-chp10-p326-n01-pamphlet-titles": True,
    "st-chp10-p326-n02-molmenti-reference": False,
    "st-chp10-p327-n01-grimaldo-balbi-citation": False,
    "st-chp10-p327-n02-zannandreis-citation": False,
    "st-chp10-p328-n01-la-harpe-ode-imprint": False,
    "st-chp10-p328-n02-zanetti-letter-citation": False,
    "st-chp10-p328-n03-baretti-locator": False,
    "st-chp10-p328-n04-venturi-locator": False,
    "st-chp10-p328-n05-biffi-letter-citation": False,
    "st-chp10-p328-n06-venturi-locator": False,
    "st-chp10-p328-n07-gazzetta-citation": False,
    "st-chp10-p329-n01-della-pittura-preface": False,
    "st-chp10-p329-n02-relazione-in-sagredo": True,
    "st-chp10-p330-n01-memmo-sheet-appendix": True,
    "st-chp10-p330-n02-canaletto-hypothesis": False,
    "st-chp10-p330-n03-vasari-life": True,
    "st-chp10-p330-n04-haskell-levey": False,
    "st-chp10-p330-n04-i-nunzio-report": False,
}

EDGE_FIXES = {
    "st-chp10-p326-n01-pamphlet-titles": {
        "subject_candidate_id": "cand-9794",
        "predicate": "has_subject",
        "object_candidate_id": "cand-9792",
        "qualification": "The pamphlet title identifies the poems as occasioned by Giorgio Pisani's solemn entry; model the publication as having that event as its subject. The full bibliographic entry continues beyond this OCR line.",
    },
    "st-chp10-p329-n02-relazione-in-sagredo": {
        "subject_candidate_id": "cand-9838",
        "predicate": "cited_by",
        "object_candidate_id": "cand-9840",
        "qualification": "Haskell says the 18 August 1772 Relazione was quoted by Sagredo in 1857. The direction records the source document as cited by the later publication.",
    },
    "st-chp10-p330-n01-memmo-sheet-appendix": {
        "subject_candidate_id": "cand-2962",
        "predicate": "contains",
        "object_candidate_id": "cand-9857",
        "qualification": "Haskell says the book's Appendix 6 publishes Memmo's preparatory query sheet in full; the book contains the reproduced archival item.",
    },
    "st-chp10-p330-n03-vasari-life": {
        "subject_candidate_id": "cand-9864",
        "predicate": "has_subject",
        "object_candidate_id": "cand-0004",
        "qualification": "Haskell says Vasari's Life contains an account of the formation of the Accademia del Disegno; the text has the Academy as a subject.",
    },
}

NEW_RELATIONS = [
    {
        "id": "st-chp10-p328-n01-ode-authored-by-la-harpe",
        "base": "st-chp10-p328-n01-la-harpe-ode-imprint",
        "subject": "cand-9829",
        "predicate": "authored_by",
        "object": "cand-1345",
        "claim": "The cited title attributes Il Filosofo dell'Alpi to de la Harpe.",
        "qualification": "Authorship is stated in Haskell's transcribed title; the poem itself was not independently consulted.",
    },
    {
        "id": "st-chp10-p328-n01-ode-translated-by-fossati",
        "base": "st-chp10-p328-n01-la-harpe-ode-imprint",
        "subject": "cand-9829",
        "predicate": "contributed_by",
        "object": "cand-9830",
        "claim": "The title credits Giuseppe Fossati with freely rendering the ode into Italian verse.",
        "qualification": "The contribution role is translator; Haskell's transcribed title is the evidence, and the poem itself was not independently consulted.",
        "extra": {"role": "translator"},
    },
    {
        "id": "st-chp10-p328-n01-ode-published-by-storti",
        "base": "st-chp10-p328-n01-la-harpe-ode-imprint",
        "subject": "cand-9829",
        "predicate": "published_by",
        "object": "cand-9835",
        "claim": "The imprint names Giacomo Storti as publisher in Venice in 1780.",
        "qualification": "Publisher, place, and year are transcribed from Haskell's note; the poem itself was not independently consulted.",
        "extra": {"time": "1780", "place": "Venice"},
    },
    {
        "id": "st-chp10-p328-n02-letter-authored-by-zanetti",
        "base": "st-chp10-p328-n02-zanetti-letter-citation",
        "subject": "cand-9831",
        "predicate": "authored_by",
        "object": "cand-2857",
        "claim": "Haskell identifies the cited 23 August 1738 letter as a letter from A. M. Zanetti.",
        "qualification": "The letter heading as transcribed by Haskell identifies the sender; the manuscript itself was not independently consulted.",
    },
    {
        "id": "st-chp10-p328-n02-letter-addressed-to-gori",
        "base": "st-chp10-p328-n02-zanetti-letter-citation",
        "subject": "cand-9831",
        "predicate": "addressed_to",
        "object": "cand-1214",
        "claim": "Haskell identifies A. F. Gori as the addressee of the 23 August 1738 letter.",
        "qualification": "The letter heading as transcribed by Haskell identifies the addressee; the manuscript itself was not independently consulted.",
    },
    {
        "id": "st-chp10-p328-n02-letter-held-by-marucelliana",
        "base": "st-chp10-p328-n02-zanetti-letter-citation",
        "subject": "cand-9831",
        "predicate": "held_by",
        "object": "cand-9493",
        "claim": "Haskell locates the 23 August 1738 letter in Biblioteca Marucelliana, Florence.",
        "qualification": "Repository and shelfmark are transcribed from Haskell's note; the manuscript itself was not independently consulted.",
    },
    {
        "id": "st-chp10-p328-n05-letter-authored-by-biffi",
        "base": "st-chp10-p328-n05-biffi-letter-citation",
        "subject": "cand-9832",
        "predicate": "authored_by",
        "object": "cand-0373",
        "claim": "Haskell identifies the 1773 unpublished letter as written by Giambattista Biffi.",
        "qualification": "The letter description as transcribed by Haskell identifies the author; the manuscript itself was not independently consulted.",
    },
    {
        "id": "st-chp10-p328-n05-letter-addressed-to-vacchelli",
        "base": "st-chp10-p328-n05-biffi-letter-citation",
        "subject": "cand-9832",
        "predicate": "addressed_to",
        "object": "cand-2674",
        "claim": "Haskell identifies Signor Vacchelli as the addressee of Biffi's 1773 letter.",
        "qualification": "The letter description as transcribed by Haskell identifies the addressee; the manuscript itself was not independently consulted.",
    },
    {
        "id": "st-chp10-p328-n05-letter-held-by-cremona-library",
        "base": "st-chp10-p328-n05-biffi-letter-citation",
        "subject": "cand-9832",
        "predicate": "held_by",
        "object": "cand-8556",
        "claim": "Haskell locates Biffi's 1773 letter at Biblioteca Governativa, Cremona, shelfmark MSS. aa.I.4.",
        "qualification": "Repository and shelfmark are transcribed from Haskell's note; the manuscript itself was not independently consulted.",
    },
    {
        "id": "st-chp10-p328-n05-letter-has-subject-zuccarelli",
        "base": "st-chp10-p328-n05-biffi-letter-citation",
        "subject": "cand-9832",
        "predicate": "has_subject",
        "object": "cand-2879",
        "claim": "Biffi's quoted letter praises Francesco Zuccarelli's landscape painting.",
        "qualification": "The praise is directly quoted in Haskell's note; the archival letter itself was not independently consulted.",
    },
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify and atomize p.324-330 footnote statements")
    parser.add_argument("--apply", action="store_true", help="write after hash, row-set, and source-quote preflight")
    args = parser.parse_args()

    actual = {p.name: sha(p) for p in (TABLE, SOURCE)}
    if actual != EXPECTED:
        raise SystemExit(f"preflight hash mismatch; no writes made: {actual}")

    rows = [json.loads(line) for line in TABLE.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement_id in source table")
    target = [
        r for r in rows
        if r.get("segment_id") == SEGMENT
        and 325 <= r.get("qualifiers", {}).get("source_line_start", 0) <= 349
    ]
    if {r["statement_id"] for r in target} != EXPECTED_IDS:
        raise SystemExit("target segment statement set changed; no writes made")
    unset = {r["statement_id"] for r in target if "relation_candidate" not in r.get("qualifiers", {})}
    if unset != UNSET_IDS or set(CLASSIFICATIONS) != UNSET_IDS:
        raise SystemExit("unset row set changed; no writes made")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    for row in target:
        q = row["qualifiers"]
        start, end = q["source_line_start"], q["source_line_end"]
        block = "\n".join(source_lines[start - 1:end])
        if not row.get("original_quote") or row["original_quote"] not in block:
            raise SystemExit(f"source quote mismatch: {row['statement_id']}")

    for sid, value in CLASSIFICATIONS.items():
        row = by_id[sid]
        row["qualifiers"]["relation_candidate"] = value
        if value:
            row["qualifiers"]["qualification"] = EDGE_FIXES[sid]["qualification"]
        elif sid == "st-chp10-p324-n3-levey-affinity-citation":
            row["qualifiers"]["qualification"] = "This records a critic's qualified comparison of two people, not a specific historical relation; the note is a citation locator for the interpretive claim."
        elif sid == "st-chp10-p330-n02-canaletto-hypothesis":
            row["qualifiers"]["qualification"] = "Haskell's identification of painter C. with Canaletto is explicitly qualified as almost certain and sits beside a chronology problem; it remains an attributed hypothesis, not a resolved same_as relation."
        elif sid == "st-chp10-p330-n04-i-nunzio-report":
            row["qualifiers"]["qualification"] = "The archival report describes displayed paintings and a crowd, but this item does not identify the venue; it cannot be attached to the specific S. Rocco exhibition event without resolving that endpoint."
        else:
            row["qualifiers"]["qualification"] = "This is a bibliographic locator, cross-reference, or evidentiary note; it does not assert a distinct formal entity relation in this statement."

    for sid, values in EDGE_FIXES.items():
        row = by_id[sid]
        row["subject_candidate_id"] = values["subject_candidate_id"]
        row["predicate"] = values["predicate"]
        row["object_candidate_id"] = values["object_candidate_id"]

    additions = []
    for spec in NEW_RELATIONS:
        if spec["id"] in by_id:
            raise SystemExit(f"new statement id already exists: {spec['id']}")
        base = by_id[spec["base"]]
        row = copy.deepcopy(base)
        row["statement_id"] = spec["id"]
        row["subject_candidate_id"] = spec["subject"]
        row["predicate"] = spec["predicate"]
        row["object_candidate_id"] = spec["object"]
        q = row["qualifiers"]
        q["claim"] = spec["claim"]
        q["relation_candidate"] = True
        q["qualification"] = spec["qualification"]
        for key, value in spec.get("extra", {}).items():
            q[key] = value
        mentioned = q.get("mentioned_candidate_ids", [])
        for candidate_id in (spec["subject"], spec["object"]):
            if candidate_id not in mentioned:
                mentioned.append(candidate_id)
        q["mentioned_candidate_ids"] = mentioned
        q.pop("linked_body_statement_ids", None)
        start, end = q["source_line_start"], q["source_line_end"]
        block = "\n".join(source_lines[start - 1:end])
        if not row.get("original_quote") or row["original_quote"] not in block:
            raise SystemExit(f"new row source quote mismatch: {spec['id']}")
        additions.append(row)

    rows.extend(additions)
    segment_rows = [
        r for r in rows
        if r.get("segment_id") == SEGMENT
        and 325 <= r.get("qualifiers", {}).get("source_line_start", 0) <= 349
    ]
    counts = {
        "true": sum(r["qualifiers"].get("relation_candidate") is True for r in segment_rows),
        "false": sum(r["qualifiers"].get("relation_candidate") is False for r in segment_rows),
        "unset": sum("relation_candidate" not in r["qualifiers"] for r in segment_rows),
    }
    if counts != {"true": 17, "false": 24, "unset": 0}:
        raise SystemExit(f"unexpected target segment counts: {counts}")

    output = ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")
    print(f"Existing note rows classified: {len(UNSET_IDS)}; new atomic relation statements: {len(additions)}")
    print(f"Segment total after write: {len(segment_rows)}; relation_candidate true/false/unset: {counts['true']}/{counts['false']}/{counts['unset']}")
    print("Direction/type repairs: pamphlet→Pisani entry (has_subject); Relazione→Sagredo publication (cited_by); book→Memmo sheet (contains); Vasari Life→Accademia del Disegno (has_subject).")
    print("Unresolved Canaletto identity and unnamed exhibition venue remain non-relations.")
    print("Planned table hash:", hashlib.sha256(output).hexdigest())
    if not args.apply:
        print("preview only; no files written")
        return 0
    if BACKUP.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {BACKUP.name}")
    shutil.copy2(TABLE, BACKUP)
    TABLE.write_bytes(output)
    print("applied; backup:", BACKUP.name)
    print("written table hash:", sha(TABLE))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
