#!/usr/bin/env python3
"""Classify p.100 S2 claims with guarded, recoverable statement-table edits."""

from __future__ import annotations

import hashlib
import csv
import json
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l232-308"
SOURCE_REL = Path("02-sources/02-Markdown/04_CHP-4_sec_ii.md")
STATEMENTS_REL = Path("04-knowledge/tables/book-statements.jsonl")
CANDIDATES_REL = Path("04-knowledge/tables/entity-candidates.csv")
MENTIONS_REL = Path("04-knowledge/tables/mentions.csv")
BACKUP_TAG = "s2-chp4-p100-relations-20261011"

EXPECTED_SHA256 = {
    SOURCE_REL: "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575",
    STATEMENTS_REL: "494749e91e20736d787ac5810be5ed1fad9f9c3a7f8a500c1cc286cc98c15aef",
    CANDIDATES_REL: "008176568d37d51db72fcc7393bb72711d8c0c7e9dcd1b4cccd1c018ac29a85d",
    MENTIONS_REL: "056f1ec87a9271eaadf34bdf31cbed181455dafa8c6896f833d3a84dd1ff4020",
}

TARGET_IDS = {
    "st-chp4-sec-ii-p100-frontispiece",
    "st-chp4-sec-ii-p100-inventory-portrait",
    "st-chp4-sec-ii-p100-leoni-hypothesis",
    "st-chp4-sec-ii-p100-munich-drawing",
    "st-chp4-sec-ii-p100-muntz-reference",
    "st-chp4-sec-ii-p100-no-leoni-drawing",
    "st-chp4-sec-ii-p100-peiresc-locator",
    "st-chp4-sec-ii-p100-varotari-assumption",
}

RELATION_NOTES = {
    "st-chp4-sec-ii-p100-frontispiece":
        "Haskell explicitly says this unidentified portrait forms the frontispiece to Carlo Dati's panegyric; keep it distinct from the inventory portrait and Munich drawing.",
    "st-chp4-sec-ii-p100-inventory-portrait":
        "Haskell reports that the Haskell and Rinehart inventory contains this portrait entry; its identity with Dati's panegyric frontispiece is not established.",
    "st-chp4-sec-ii-p100-leoni-hypothesis":
        "Haskell's 'more likely' wording makes this a tentative identification of the Padov.no label with Leoni, not a settled identity.",
    "st-chp4-sec-ii-p100-munich-drawing":
        "Haskell reports Marabottini's attribution of the Munich drawing to Testa; the reported authorship remains distinct from the possible sitter identification.",
    "st-chp4-sec-ii-p100-muntz-reference":
        "The footnote explicitly cites Müntz and Molinier from Haskell's book; the page scan reads 1885 while S0 OCR reads 188$; the article was not independently consulted.",
    "st-chp4-sec-ii-p100-no-leoni-drawing":
        "This is Haskell's scoped negative observation that he knows of no Leoni drawing matching Cassiano's features; it is not proof that none exists.",
    "st-chp4-sec-ii-p100-peiresc-locator":
        "The footnote explicitly cites Peiresc, volume IV, page 107 from Haskell's book; the cited page was not independently consulted.",
    "st-chp4-sec-ii-p100-varotari-assumption":
        "Haskell reports the inventory authors' assumption that the label refers to Varotari; retain the assumption and its approximate contextual details without treating it as an identification.",
}

CITATIONS = {
    "st-chp4-sec-ii-p100-peiresc-locator": (1, "Peiresc, IV, p. 107"),
    "st-chp4-sec-ii-p100-muntz-reference": (3, "Müntz and Molinier, 1885"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> tuple[list[dict], str]:
    raw = path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    return rows, newline


def jsonl_bytes(rows: list[dict], newline: str) -> bytes:
    return (newline.join(json.dumps(row, ensure_ascii=False) for row in rows) + newline).encode("utf-8")


def add_id(values: list[str], candidate_id: str) -> list[str]:
    result = list(values)
    if candidate_id not in result:
        result.append(candidate_id)
    return result


def flag(record: dict, value: bool, note: str) -> None:
    q = record.setdefault("qualifiers", {})
    q["relation_candidate"] = value
    q["relation_candidate_note"] = note


def scalar(statement_id: str, predicate: str, quote: str, claim: str, qualification: str) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-1395",
        "object_candidate_id": None,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": 240,
            "source_line_end": 240,
            "claim": claim,
            "speaker": "Haskell",
            "text_layer": "authorial characterization",
            "pdf_physical_page": 7,
            "printed_page_locator": "p.100",
            "mentioned_candidate_ids": ["cand-1395"],
            "qualification": qualification,
            "relation_candidate": False,
            "relation_candidate_note": "This is a scalar characterization of Leoni, not a relation between entities.",
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_REL.as_posix(),
    }


def relation(statement_id: str, subject: str, obj: str, predicate: str, quote: str, claim: str, note: str, speaker: str, text_layer: str, qualification: str, mentioned: list[str]) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": 240,
            "source_line_end": 240,
            "claim": claim,
            "speaker": speaker,
            "text_layer": text_layer,
            "pdf_physical_page": 7,
            "printed_page_locator": "p.100",
            "mentioned_candidate_ids": mentioned,
            "qualification": qualification,
            "relation_candidate": True,
            "relation_candidate_note": note,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_REL.as_posix(),
    }


def atomic_write(path: Path, data: bytes) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".tmp-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the prevalidated S2 edits; default is dry-run")
    args = parser.parse_args()
    if not (ROOT / ".agents" / "pipeline.md").exists():
        raise SystemExit(f"Run from the repository checkout; resolved root={ROOT}")

    paths = {rel: ROOT / rel for rel in EXPECTED_SHA256}
    for rel, expected in EXPECTED_SHA256.items():
        actual = sha256(paths[rel].read_bytes())
        if actual != expected:
            raise SystemExit(f"Precondition hash mismatch for {rel}: expected {expected}, found {actual}")

    source_bytes = paths[SOURCE_REL].read_bytes()
    source_lines = source_bytes.decode("utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[231:308])
    segments = [json.loads(line) for line in (ROOT / "04-knowledge/tables/segments.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    segment = next((x for x in segments if x.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != "792d95e61aab35b3bfb639af2364220365d26076eeafb93e545526ccf302ca7e":
        raise SystemExit("The target S0 segment hash changed")

    statements, newline = read_jsonl(paths[STATEMENTS_REL])
    rows = {x["statement_id"]: x for x in statements}
    with (ROOT / "04-knowledge/tables/entity-candidates.csv").open(encoding="utf-8-sig", newline="") as stream:
        candidates = list(csv.DictReader(stream))
    candidate_ids = {x.get("candidate_id") for x in candidates}
    target_set = {
        x["statement_id"]
        for x in statements
        if x.get("segment_id") == SEGMENT_ID and x.get("qualifiers", {}).get("printed_page_locator") == "p.100"
    }
    if target_set != TARGET_IDS:
        raise SystemExit(f"The p.100 target set changed: expected {len(TARGET_IDS)}, found {len(target_set)}")
    if any(rows[sid].get("qualifiers", {}).get("relation_candidate") is not None for sid in TARGET_IDS):
        raise SystemExit("A p.100 target statement is already classified")
    if max(int(value.split("-")[1]) for value in candidate_ids) != 11680:
        raise SystemExit("Candidate set changed; review endpoint IDs before applying")

    new_relations = [
        relation(
            "st-chp4-sec-ii-p100-haskell-rinehart-citation", "cand-2962", "cand-5658", "cites",
            "Haskell and Rinehart, i960.",
            "Haskell's book cites the Haskell and Rinehart article on the dal Pozzo collection in footnote 2.",
            "The footnote explicitly cites this article; the printed scan reads 1960 while S0 OCR reads i960, and the article was not independently consulted.",
            "Haskell footnote", "bibliographic citation",
            "This records a bibliographic link only; it does not independently verify the cited inventory.",
            ["cand-2962", "cand-5658"],
        ),
        relation(
            "st-chp4-sec-ii-p100-portrait-attribution-label", "cand-5659", "cand-5661", "attributed_to_label",
            "a portrait of Cassiano (and others of unnamed figures) attributed to ‘Padov.no’",
            "The inventory entry attributes this portrait to the label Padov.no.",
            "The inventory attribution is to a label, not to an identified person; Haskell's alternative readings are recorded separately.",
            "Haskell reporting the Haskell and Rinehart inventory", "reported attribution",
            "Keep the portrait entry, the Dati frontispiece, and the attribution label distinct.",
            ["cand-5659", "cand-5661"],
        ),
        relation(
            "st-chp4-sec-ii-p100-leoni-alias", "cand-1395", "cand-5661", "also_known_as",
            "who is frequently called ‘Padovano’ in seventeenth-century literature",
            "Haskell says Ottavio Leoni was frequently called Padovano in seventeenth-century literature.",
            "This records Haskell's reported name usage; it does not establish that every Padovano attribution refers to Leoni.",
            "Haskell", "authorial characterization",
            "The label candidate remains distinct from Leoni's person identity.",
            ["cand-1395", "cand-5661"],
        ),
        relation(
            "st-chp4-sec-ii-p100-munich-drawing-may-portray-cassiano", "cand-5660", "cand-2036", "may_portray",
            "which may well portray Cassiano.",
            "Haskell says the Munich drawing attributed to Testa may portray Cassiano.",
            "The wording is explicitly tentative; the drawing's identity as a portrait of Cassiano is not established.",
            "Haskell reporting Marabottini", "reported attribution",
            "Keep the possible sitter claim separate from Marabottini's attribution of the drawing to Testa.",
            ["cand-5660", "cand-2036"],
        ),
    ]
    new_scalars = [
        scalar(
            "st-chp4-sec-ii-p100-leoni-profession", "described_as_portrait_draughtsman_and_engraver",
            "the well-known portrait draughtsman and engraver",
            "Haskell describes Ottavio Leoni as a well-known portrait draughtsman and engraver.",
            "This is Haskell's characterization of Leoni's professional role.",
        ),
        scalar(
            "st-chp4-sec-ii-p100-leoni-portrait-specialty", "famous_for_portraits_of_virtuosi",
            "He was above all famous for his portraits of virtuosi",
            "Haskell says Leoni was especially famous for portraits of virtuosi.",
            "This is Haskell's assessment of Leoni's portrait practice; the source does not identify the sitters as a complete group.",
        ),
    ]
    new_rows = new_relations + new_scalars
    for row in new_rows:
        if row["statement_id"] in rows:
            raise SystemExit(f"New statement ID already exists: {row['statement_id']}")
        if row["original_quote"] not in segment_text:
            raise SystemExit(f"New quote is not an exact source substring: {row['statement_id']}")

    for statement_id, note in RELATION_NOTES.items():
        q = rows[statement_id].setdefault("qualifiers", {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note

    frontispiece = rows["st-chp4-sec-ii-p100-frontispiece"]
    frontispiece["subject_candidate_id"] = "cand-5656"
    frontispiece["object_candidate_id"] = "cand-5657"
    frontispiece["predicate"] = "serves_as_frontispiece_to"
    frontispiece["qualifiers"]["claim"] = "Haskell says this unidentified portrait forms the frontispiece to Carlo Dati's panegyric."
    frontispiece["qualifiers"]["mentioned_candidate_ids"] = ["cand-5656", "cand-5657", "cand-0905"]

    inventory = rows["st-chp4-sec-ii-p100-inventory-portrait"]
    inventory["predicate"] = "inventory_lists_portrait"
    inventory["qualifiers"]["claim"] = "Haskell reports that the Haskell and Rinehart inventory lists a portrait of Cassiano and other unnamed figures, with the attribution label Padov.no."

    leoni = rows["st-chp4-sec-ii-p100-leoni-hypothesis"]
    leoni["subject_candidate_id"] = "cand-5661"
    leoni["object_candidate_id"] = "cand-1395"
    leoni["qualifiers"]["claim"] = "Haskell considers Ottavio Leoni a more likely referent for the inventory's Padov.no label and argues from Leoni's portrait practice."
    leoni["qualifiers"]["mentioned_candidate_ids"] = ["cand-5659", "cand-1395", "cand-5661"]
    leoni["qualifiers"]["qualification"] = "Haskell's phrase 'seems far more likely' is a hypothesis, not a settled identification. The label remains a separate candidate; profession, alias, and reputation claims are recorded separately."

    munich = rows["st-chp4-sec-ii-p100-munich-drawing"]
    munich["subject_candidate_id"] = "cand-5660"
    munich["object_candidate_id"] = "cand-2556"
    munich["predicate"] = "attributed_to"
    munich["qualifiers"]["claim"] = "Haskell reports that Marabottini attributes the Munich drawing to Pietro Testa."
    munich["qualifiers"]["mentioned_candidate_ids"] = ["cand-5660", "cand-2556", "cand-3714"]
    munich["qualifiers"]["qualification"] = "This is Marabottini's attribution as reported by Haskell; it remains separate from the tentative claim that the drawing may portray Cassiano."

    varotari = rows["st-chp4-sec-ii-p100-varotari-assumption"]
    varotari["subject_candidate_id"] = "cand-5661"
    varotari["object_candidate_id"] = "cand-2701"
    varotari["qualifiers"]["claim"] = "Haskell says the inventory authors assumed the Padov.no label referred to Alessandro Varotari, adding his approximate Rome visit and Venetian affiliations as context."
    varotari["qualifiers"]["mentioned_candidate_ids"] = ["cand-5659", "cand-5661", "cand-2701", "cand-4490", "cand-2719", "cand-2036"]

    for statement_id, (marker, locator) in CITATIONS.items():
        row = rows[statement_id]
        target = row.get("object_candidate_id")
        row["subject_candidate_id"] = "cand-2962"
        row["predicate"] = "cites"
        q = row["qualifiers"]
        q["claim"] = f"Haskell's book cites {locator} in this footnote."
        q["speaker"] = "Haskell footnote"
        q["text_layer"] = "bibliographic citation"
        q["citation_locator"] = locator
        q["footnote_marker"] = marker
        q["cited_material_not_independently_consulted"] = True
        q["qualification"] = "This records a bibliographic locator only; the cited item was not independently consulted and the citation does not verify adjacent claims."
        q["mentioned_candidate_ids"] = add_id(q.get("mentioned_candidate_ids", []), "cand-2962")
        if target:
            q["mentioned_candidate_ids"] = add_id(q["mentioned_candidate_ids"], target)

    out = []
    inserted = False
    for row in statements:
        out.append(row)
        if row["statement_id"] == "st-chp4-sec-ii-p100-varotari-assumption":
            out.extend(new_rows)
            inserted = True
    if not inserted:
        raise SystemExit("Could not place additions after the p.100 attribution claims")

    out_p100 = [x for x in out if x.get("segment_id") == SEGMENT_ID and x.get("qualifiers", {}).get("printed_page_locator") == "p.100"]
    if len(out_p100) != 14:
        raise SystemExit(f"Expected 14 p.100 statements after atomization, found {len(out_p100)}")
    if sum(x.get("qualifiers", {}).get("relation_candidate") is True for x in out_p100) != 12:
        raise SystemExit("Expected 12 p.100 relation candidates")
    if sum(x.get("qualifiers", {}).get("relation_candidate") is False for x in out_p100) != 2:
        raise SystemExit("Expected 2 p.100 scalar non-relations")
    for row in out_p100:
        q = row.get("qualifiers", {})
        if q.get("relation_candidate") is True:
            endpoints = (row.get("subject_candidate_id"), row.get("object_candidate_id"))
            if not all(endpoints):
                raise SystemExit(f"p.100 relation candidate has an open endpoint: {row['statement_id']}")
            if not set(endpoints).issubset(set(q.get("mentioned_candidate_ids", []))):
                raise SystemExit(f"p.100 relation endpoint absent from mentioned_candidate_ids: {row['statement_id']}")
            if not set(endpoints).issubset(candidate_ids):
                raise SystemExit(f"p.100 relation references a missing candidate: {row['statement_id']}")

    proposed = jsonl_bytes(out, newline)
    print("PREVIEW: p.100 output statements=14; relation candidates=12; scalar non-relations=2")
    print("PREVIEW: 8 existing statements classified; 6 atomic statements added; candidates/mentions unchanged; no S6 formal relations")
    for row in out_p100:
        q = row.get("qualifiers", {})
        print(f"REVIEW: {row['statement_id']} | {q.get('relation_candidate')} | {row.get('predicate')} | {row.get('subject_candidate_id')} -> {row.get('object_candidate_id')} | {row.get('original_quote', '')[:90]}")
    print(f"PREVIEW: {STATEMENTS_REL.as_posix()} {sha256(paths[STATEMENTS_REL].read_bytes())} -> {sha256(proposed)} bytes={len(proposed)}")
    if not args.apply:
        print("DRY RUN ONLY. Re-run with --apply to write the prevalidated changes.")
        return 0

    path = paths[STATEMENTS_REL]
    backup = path.with_name(path.name + ".bak-" + BACKUP_TAG)
    if backup.exists():
        raise SystemExit(f"Backup already exists; refusing to overwrite: {backup}")
    with backup.open("xb") as stream:
        stream.write(path.read_bytes())
        stream.flush()
        os.fsync(stream.fileno())
    atomic_write(path, proposed)
    print(f"BACKUP: {backup.relative_to(ROOT).as_posix()} sha256={sha256(backup.read_bytes())}")
    print(f"WRITTEN: {STATEMENTS_REL.as_posix()} sha256={sha256(path.read_bytes())}")
    print("APPLY COMPLETE. S0 source, candidates, mentions, and formal S6 relations were not modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
