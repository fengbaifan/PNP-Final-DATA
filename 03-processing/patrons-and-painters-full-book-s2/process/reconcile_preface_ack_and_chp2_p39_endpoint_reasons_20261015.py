from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
TABLE = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
PREFACE = ROOT / "02-sources" / "02-Markdown" / "00_03_Preface_1st_Ed.md"
CHP2 = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_ii.md"
EXPECTED_TABLE_SHA256 = "8994eb060b707af139d20d411b89dbee329a77667da149a431ca34453751cc9a"
SOURCE_HASHES = {
    "front-matter:00_03_Preface_1st_Ed:l19-29": {
        "segment": "e6cf252331b6e5f64eaf1518f9de020715a229a9a040834f1d0214f4b1ab73f0",
        "asset": "e793793f71fc5e9b9ba97a1c12fa50d497ec4de89f3c19f247c4a93228618c4a",
    },
    "chp-2:02_CHP-2_sec_ii:l80-89": {
        "segment": "e1d901252d516f1c9a17a7024d6fb2ecefd1346c48f25c13aa87e1c48e8a8bf3",
        "asset": "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9",
    },
}
PREFACE_SEGMENT = "front-matter:00_03_Preface_1st_Ed:l19-29"
CHP2_SEGMENT = "chp-2:02_CHP-2_sec_ii:l80-89"
PREFACE_STATEMENT = "st-fm-c-preface-italian-colleagues-acknowledged"
PREFACE_PEOPLE = [
    ("cand-3712", "bettagno", "Alessandro Bettagno", "Dr Alessandro Bettagno"),
    ("cand-3784", "torcellan", "Gianfranco Torcellan", "Dr Gianfranco Torcellan"),
    ("cand-3771", "venturi", "Franco Venturi", "Professors Franco Venturi"),
    ("cand-3778", "cozzi", "Gaetano Cozzi", "Gaetano Cozzi"),
    ("cand-3714", "marabottini", "Alessandro Marabottini Marabotti", "Professor Alessandro,Marabottini Marabotti"),
]
PREFACE_NEW_IDS = {
    "torcellan": "st-fm-c-preface-torcellan-acknowledged",
    "venturi": "st-fm-c-preface-venturi-acknowledged",
    "cozzi": "st-fm-c-preface-cozzi-acknowledged",
    "marabottini": "st-fm-c-preface-marabottini-acknowledged",
}
CHP2_REASONS = {
    "st-chp2-secii-l80-89-giulio-made-cardinal": (
        "The passage says Giulio was made a cardinal in 1626 but does not name the granting authority. Urban VIII's papacy is mentioned in the preceding context, without explicitly attributing this promotion to him; do not infer the appointing person."
    ),
    "st-chp2-secii-l80-89-marcello-papal-treasurer": (
        "The passage reports that Marcello became papal treasurer but supplies no exact date, tenure, or appointing authority. Urban VIII is contextual, not an explicitly named appointer; retain the office as a role description and do not invent an office entity."
    ),
    "st-chp2-secii-l80-89-sacchetti-influence-on-taste": (
        "Haskell's broad claim about the Sacchettis' influence in matters of taste names no specific object or scope. The following 'any artist' quotation concerns protection and does not identify the target of this general taste judgment."
    ),
}
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-preface-chp2-p39-reconcile-20261015")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def is_open(row: dict) -> bool:
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def open_counts(rows: list[dict]) -> tuple[int, int, int, int]:
    opened = [row for row in rows if is_open(row)]
    obj_only = sum(bool(row.get("subject_candidate_id")) and not row.get("object_candidate_id") for row in opened)
    subj_only = sum(not row.get("subject_candidate_id") and bool(row.get("object_candidate_id")) for row in opened)
    both = sum(not row.get("subject_candidate_id") and not row.get("object_candidate_id") for row in opened)
    return len(opened), obj_only, subj_only, both


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    if digest(raw) != EXPECTED_TABLE_SHA256:
        raise ValueError(f"statement table changed: {digest(raw)}")
    segments = {
        row["segment_id"]: row
        for row in (json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip())
    }
    for segment_id, expected in SOURCE_HASHES.items():
        row = segments.get(segment_id)
        if not row or row.get("sha256") != expected["segment"] or row.get("asset_sha256") != expected["asset"]:
            raise ValueError(f"source segment fingerprint changed: {segment_id}")
    if digest(PREFACE.read_bytes()) != SOURCE_HASHES[PREFACE_SEGMENT]["asset"]:
        raise ValueError("preface S0 asset changed")
    if digest(CHP2.read_bytes()) != SOURCE_HASHES[CHP2_SEGMENT]["asset"]:
        raise ValueError("chapter 2 S0 asset changed")

    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError("duplicate statement IDs in input")
    preface_row = by_id.get(PREFACE_STATEMENT)
    if not preface_row or preface_row.get("segment_id") != PREFACE_SEGMENT or not is_open(preface_row):
        raise ValueError("the reviewed preface acknowledgment row is missing or changed")
    if open_counts(rows) != (391, 245, 46, 100):
        raise ValueError(f"unexpected open-endpoint state: {open_counts(rows)}")
    if any(statement_id in by_id for statement_id in PREFACE_NEW_IDS.values()):
        raise ValueError("a planned preface statement ID already exists")
    for statement_id in CHP2_REASONS:
        row = by_id.get(statement_id)
        if not row or row.get("segment_id") != CHP2_SEGMENT or not is_open(row):
            raise ValueError(f"reviewed chapter 2 open statement changed: {statement_id}")

    preface_lines = PREFACE.read_text(encoding="utf-8-sig").splitlines()
    preface_text = "\n".join(preface_lines[18:29])
    mentions = read_csv(MENTIONS)
    candidates = {row["candidate_id"] for row in read_csv(CANDIDATES)}
    mention_rows = {
        row["candidate_id"]: row
        for row in mentions
        if row["segment_id"] == PREFACE_SEGMENT and row["candidate_id"] in {person[0] for person in PREFACE_PEOPLE}
    }
    original_quote = preface_row["original_quote"]
    for candidate_id, _, _, surface in PREFACE_PEOPLE:
        if candidate_id not in candidates:
            raise ValueError(f"preface person candidate is missing: {candidate_id}")
        mention = mention_rows.get(candidate_id)
        if not mention or mention["surface_form"] != surface:
            raise ValueError(f"preface person mention is missing or changed: {candidate_id}")
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if preface_text[start:end] != surface or surface not in original_quote:
            raise ValueError(f"preface evidence span changed: {candidate_id}")

    h = preface_row["qualifiers"]
    h.pop("open_endpoint_reason", None)
    h["claim"] = "Haskell acknowledges Alessandro Bettagno among the Italian people he wishes to single out."
    h["qualification"] = "The shared preface clause 'In Italy I would like to single out especially' governs this named person. No individual contribution is inferred from the acknowledgment alone."
    h["mentioned_candidate_ids"] = ["cand-3770", "cand-3712"]
    h["relation_candidate"] = True
    h["relation_candidate_note"] = "The shared Italian acknowledgment list explicitly names Bettagno; this row records acknowledgment only and does not assign a specific contribution."
    preface_row["subject_candidate_id"] = "cand-3770"
    preface_row["object_candidate_id"] = "cand-3712"
    preface_row["predicate"] = "acknowledged_colleague"
    preface_row["original_quote"] = "Dr Alessandro Bettagno"

    new_rows = []
    for candidate_id, slug, display_name, surface in PREFACE_PEOPLE[1:]:
        claim_name = display_name
        row = json.loads(json.dumps(preface_row, ensure_ascii=False))
        row["statement_id"] = PREFACE_NEW_IDS[slug]
        row["subject_candidate_id"] = "cand-3770"
        row["object_candidate_id"] = candidate_id
        row["predicate"] = "acknowledged_colleague"
        row["original_quote"] = surface
        row["qualifiers"]["claim"] = f"Haskell acknowledges {claim_name} among the Italian people he wishes to single out."
        row["qualifiers"]["mentioned_candidate_ids"] = ["cand-3770", candidate_id]
        if slug == "marabottini":
            row["qualifiers"]["qualification"] = "The shared preface clause 'In Italy I would like to single out especially' governs this named person. His separately stated hospitality and shared viewing of works remain in their own statements."
            row["qualifiers"]["relation_candidate_note"] = "The preface explicitly singles out Marabottini Marabotti, with the phrase 'above all'; this row records acknowledgment only. His hospitality and shared viewing of works are recorded separately."
        else:
            row["qualifiers"]["relation_candidate_note"] = f"The shared Italian acknowledgment list explicitly names {claim_name}; this row records acknowledgment only and does not assign a specific contribution."
        new_rows.append(row)

    for statement_id, reason in CHP2_REASONS.items():
        by_id[statement_id]["qualifiers"]["open_endpoint_reason"] = reason

    insert_at = rows.index(preface_row) + 1
    rows[insert_at:insert_at] = new_rows
    after_counts = open_counts(rows)
    if after_counts != (390, 244, 46, 100):
        raise ValueError(f"unexpected post-reconciliation open-endpoint state: {after_counts}")
    if len({row["statement_id"] for row in rows}) != len(rows):
        raise ValueError("duplicate statement IDs after preparation")
    output = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows).encode("utf-8")

    print("preface=split the collective Italian acknowledgment into five person-level statements with existing evidence spans")
    print("chapter2_p39=added table-level reasons for three already-reviewed open endpoints")
    print(f"statements={len(rows)-4}->{len(rows)}; open_endpoints=(391,245,46,100)->{after_counts}")
    print(f"book-statements.jsonl sha256 {digest(raw)}->{digest(output)}")
    if args.preview:
        return 0
    if BACKUP.exists():
        raise FileExistsError(f"recovery copy already exists: {BACKUP.name}")
    temp = TABLE.with_name("book-statements.jsonl.tmp-s2-preface-chp2-p39-20261015")
    if temp.exists():
        raise FileExistsError(f"temporary file already exists: {temp.name}")
    shutil.copy2(TABLE, BACKUP)
    try:
        temp.write_bytes(output)
        temp.replace(TABLE)
    except Exception:
        if temp.exists():
            temp.unlink()
        shutil.copy2(BACKUP, TABLE)
        raise
    print(f"backup={BACKUP.relative_to(ROOT)}")
    print(f"applied_sha256={digest(TABLE.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
