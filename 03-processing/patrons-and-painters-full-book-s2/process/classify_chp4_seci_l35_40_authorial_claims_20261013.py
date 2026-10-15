from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SEGMENT_ID = "chp-4:04_CHP-4_sec_i:l35-40"
EXPECTED_STATEMENTS_SHA256 = "535ebc57ab4f762c5495d5e39714f3390555f41c34755ca15ef75e172802a048"
SEGMENT_SHA256 = "8e3a7da945fdf1bf1c6b7e800ae342287eafe7e3537e5a630cc9952d61095537"
CLASSIFICATIONS = {
    "st-chp4-sec-i-l35-40-arts-affected": {
        "predicate": "arts_affected_by_patronage",
        "quote": "it is easier to show that the arts themselves were affected by such patronage.",
        "note": "Nonrelation: Haskell states a broad social-history assessment of patronage's effect on the arts; no bounded artwork or specific patronage instance is linked as an entity edge.",
    },
    "st-chp4-sec-i-l35-40-arts-entered-aristocratic-life": {
        "predicate": "arts_entered_fabric_of_aristocratic_life_through_patronage",
        "quote": "Through men like Paolo Giordano, whose ancestors only a couple of generations earlier had been engaged in murderous blood feuds3 and who themselves retained the most exalted ideas of their status, the arts entered into the very fabric of aristocratic life.",
        "note": "Nonrelation: this is Haskell's general interpretation of how art entered aristocratic life through patrons like Paolo, expressed as broad social spheres and a historical mechanism rather than a discrete entity-to-entity relation.",
    },
    "st-chp4-sec-i-l35-40-exalted-status": {
        "predicate": "retained_exalted_ideas_of_status",
        "quote": "and who themselves retained the most exalted ideas of their status",
        "note": "Nonrelation: this is a social characterization of Paolo and comparable men, not a relation to a second independently identified endpoint.",
    },
    "st-chp4-sec-i-l35-40-manners-softened": {
        "predicate": "manners_softened_through_arts",
        "quote": "No doubt manners were softened thereby",
        "note": "Nonrelation: Haskell's hedged causal speculation about manners; no bounded entities or specific relation endpoints are stated.",
    },
    "st-chp4-sec-i-l35-40-sculpture-assessment": {
        "predicate": "described_sculpture_as_in_better_condition",
        "quote": "Sculpture was in a much better way— apart from minor figures there were two most excellent masters",
        "note": "Nonrelation: this records Paolo's comparative assessment of sculpture and painting, a medium-level evaluation rather than a relation between identified entities.",
    },
}
BACKUP = STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp4-seci-l35-40-authorial-claims-20261013")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify five residual chapter 4 social and evaluative claims.")
    parser.add_argument("--apply", action="store_true", help="write after protected preview checks")
    args = parser.parse_args()

    raw = STATEMENTS.read_bytes()
    if sha256(raw) != EXPECTED_STATEMENTS_SHA256:
        raise SystemExit("protected statement table changed")
    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("protected S0 segment metadata changed")
    source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    if sha256(source_text.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("protected S0 source segment changed")

    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row.get("statement_id"): row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row.get("statement_id") for row in rows
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != set(CLASSIFICATIONS):
        raise SystemExit(f"protected segment unset set changed: {sorted(unset)}")
    for statement_id, expected in CLASSIFICATIONS.items():
        row = by_id[statement_id]
        if row.get("predicate") != expected["predicate"] or row.get("original_quote") != expected["quote"]:
            raise SystemExit(f"protected statement content changed: {statement_id}")
        row["qualifiers"]["relation_candidate"] = False
        row["qualifiers"]["relation_candidate_note"] = expected["note"]

    rendered = ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")
    if raw.startswith(b"\xef\xbb\xbf"):
        rendered = b"\xef\xbb\xbf" + rendered
    print("Chapter 4 section I L35-40 residual preview:")
    for statement_id in CLASSIFICATIONS:
        print(f"{statement_id}: nonrelation")
    print(f"book-statements.jsonl: {sha256(raw)} -> {sha256(rendered)}")
    if not args.apply:
        print("mode=preview; no files changed")
        return
    if BACKUP.exists():
        raise SystemExit(f"protected backup already exists: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    temporary = STATEMENTS.with_name(STATEMENTS.name + ".tmp-s2-chp4-seci-l35-40-claims")
    temporary.write_bytes(rendered)
    temporary.replace(STATEMENTS)
    print(f"mode=apply; backup={BACKUP.name}")


if __name__ == "__main__":
    main()
