from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE_DIR = ROOT / "04-knowledge/tables"
STATEMENTS = TABLE_DIR / "book-statements.jsonl"
CANDIDATES = TABLE_DIR / "entity-candidates.csv"
MENTIONS = TABLE_DIR / "mentions.csv"
SOURCE = ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md"
SEGMENT_ID = "chp-10:10_CHP-10_intro:l3-13"
SEGMENT_SHA256 = "2b86f1b920d1aa7de55b2ba8f511e3c8ec71b8c546387f71da2113d40e197e92"
SOURCE_SHA256 = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_HASHES = {
    STATEMENTS: "0211041fe46e85aa82abaad2d6c244a79a7d2fd071819f88a3ff6868cd0be704",
    CANDIDATES: "b7bffdcd86caf069fd22fe621561e375cc4318195e2483d550ac7865f7953517",
    MENTIONS: "638c4703a373120ec0c4da67d68a7d08c4b409faafeb6f8827202abd8ca047ba",
}
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp10-p276-war-diplomacy-20261015"),
    CANDIDATES: CANDIDATES.with_name("entity-candidates.csv.bak-s2-chp10-p276-war-diplomacy-20261015"),
    MENTIONS: MENTIONS.with_name("mentions.csv.bak-s2-chp10-p276-war-diplomacy-20261015"),
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12406",
        "index_entry_id": "",
        "canonical_name": "Unspecified European war context in Haskell's p.276 account",
        "index_page_range": "",
        "suggested_type": "event",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "The source says Europe was at war while Venice remained neutral, but names no conflict. Do not identify it with a specific war or assume how many campaigns are included.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L9",
    },
    {
        "candidate_id": "cand-12407",
        "index_entry_id": "",
        "canonical_name": "Unnamed foreign embassies described as intriguing in Haskell's Venice account",
        "index_page_range": "",
        "suggested_type": "institution",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "A source-defined collective of foreign diplomatic missions. Haskell does not name the missions, their members, their target, or the precise location of the intrigue; do not merge them into one embassy.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L9",
    },
    {
        "candidate_id": "cand-12408",
        "index_entry_id": "",
        "canonical_name": "Unnamed foreign kings described as visiting Venice in Haskell's p.276 account",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell's unnamed plural group of rulers who came seeking Venice's alliance or relief from military campaigns. No rulers, membership, or visit dates are identified.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L9",
    },
    {
        "candidate_id": "cand-12409",
        "index_entry_id": "",
        "canonical_name": "Unspecified military campaigns exerting pressure on foreign kings (p.276)",
        "index_page_range": "",
        "suggested_type": "event",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Generic plural campaigns from whose pressure Haskell says foreign kings sought relief. The source does not identify them or equate them with the European war context in the preceding clause.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L9",
    },
]

NEW_MENTIONS = [
    {
        "mention_id": "m-chp10-p276-europe-war-context",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-12406",
        "surface_form": "at war",
        "start_char": "1317",
        "end_char": "1323",
        "note": "The unspecified war condition in the clause contrasting Europe at war with Venice's neutrality; no conflict is named.",
    },
    {
        "mention_id": "m-chp10-p276-foreign-embassies",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-12407",
        "surface_form": "Foreign embassies",
        "start_char": "1354",
        "end_char": "1371",
        "note": "Unnamed diplomatic missions as a plural institutional group; their intrigue target and location are not stated.",
    },
    {
        "mention_id": "m-chp10-p276-foreign-kings",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-12408",
        "surface_form": "foreign kings",
        "start_char": "1383",
        "end_char": "1396",
        "note": "Unnamed plural rulers; no membership or individual identity is inferred.",
    },
    {
        "mention_id": "m-chp10-p276-venice-her-alliance",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-8838",
        "surface_form": "her",
        "start_char": "1410",
        "end_char": "1413",
        "note": "Possessive pronoun referring to Venice as the political entity whose alliance the kings sought.",
    },
    {
        "mention_id": "m-chp10-p276-military-campaigns",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-12409",
        "surface_form": "military campaigns",
        "start_char": "1456",
        "end_char": "1474",
        "note": "Unspecified plural campaigns; kept distinct from the unnamed European war context.",
    },
]

NEW_STATEMENTS = [
    {
        "statement_id": "st-chp10-p276-foreign-embassies-intrigue",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-12407",
        "object_candidate_id": None,
        "predicate": "foreign_embassies_intrigued_unspecified_target",
        "qualifiers": {
            "source_line_start": 9,
            "source_line_end": 9,
            "printed_page": 276,
            "pdf_physical_page": 1,
            "claim": "Haskell says unnamed foreign embassies intrigued.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "qualification": "The statement does not identify an intrigue target or state its precise location; the surrounding Venice context is not used to invent either.",
            "mentioned_candidate_ids": ["cand-12407"],
            "relation_candidate": True,
            "relation_candidate_note": "The action is explicit, but the source gives no object for the intrigue.",
            "open_endpoint_reason": "The unnamed embassies are identified, but Haskell does not say whom or what they intrigued against or about, and the sentence does not explicitly locate the activity.",
        },
        "original_quote": "Foreign embassies intrigued",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
    },
    {
        "statement_id": "st-chp10-p276-foreign-kings-seek-venice-alliance",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-12408",
        "object_candidate_id": "cand-8838",
        "predicate": "foreign_kings_came_to_seek_venice_alliance",
        "qualifiers": {
            "source_line_start": 9,
            "source_line_end": 9,
            "printed_page": 276,
            "pdf_physical_page": 1,
            "claim": "Haskell says unnamed foreign kings came seeking the Republic of Venice's alliance.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "qualification": "The pronoun 'her' refers to Venice as a political actor; no ruler, alliance, or date is specified.",
            "mentioned_candidate_ids": ["cand-12408", "cand-8838"],
            "relation_candidate": True,
            "relation_candidate_note": "The target is Venice's political entity, explicitly identified by the possessive reference to her alliance.",
        },
        "original_quote": "foreign kings came to seek her alliance",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
    },
    {
        "statement_id": "st-chp10-p276-foreign-kings-seek-campaign-respite",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-12408",
        "object_candidate_id": "cand-12409",
        "predicate": "foreign_kings_sought_relief_from_military_campaigns",
        "qualifiers": {
            "source_line_start": 9,
            "source_line_end": 9,
            "printed_page": 276,
            "pdf_physical_page": 1,
            "claim": "Haskell says unnamed foreign kings came to relax from the pressure of military campaigns.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "qualification": "The campaigns are not identified and are not assumed to be the same event as the unnamed European war; Venice is the narrative context, not a campaign endpoint.",
            "mentioned_candidate_ids": ["cand-12408", "cand-12409"],
            "relation_candidate": True,
            "relation_candidate_note": "This separates the respite motive from the alliance-seeking claim and preserves the plural, unnamed campaign context.",
        },
        "original_quote": "to relax from the pressure of military campaigns",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
    },
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_open(row: dict) -> bool:
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def csv_bytes(rows: list[dict], fields: list[str], has_bom: bool) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8-sig" if has_bom else "utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if digest(raw[path]) != expected:
            raise ValueError(f"protected table changed: {path.name} ({digest(raw[path])})")
    if digest(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise ValueError("chapter 10 source asset changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[2:13])
    if digest(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise ValueError("reviewed p.276 source segment changed")
    for mention in NEW_MENTIONS:
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if segment_text[start:end] != mention["surface_form"]:
            raise ValueError(f"source span mismatch: {mention['mention_id']}")

    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    neutrality = by_id.get("st-chp10-p276-war-neutrality-and-visitors")
    if not neutrality:
        raise ValueError("expected p.276 war/diplomacy statement is missing")
    q = neutrality.get("qualifiers") or {}
    if neutrality.get("subject_candidate_id") or neutrality.get("object_candidate_id") or q.get("relation_candidate") is not True:
        raise ValueError("reviewed p.276 composite statement changed")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        candidate_fields = reader.fieldnames
        candidates = list(reader)
    with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        mention_fields = reader.fieldnames
        mentions = list(reader)
    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    for row in NEW_CANDIDATES:
        if row["candidate_id"] in candidate_ids:
            raise ValueError(f"candidate ID already exists: {row['candidate_id']}")
    for row in NEW_MENTIONS:
        if row["mention_id"] in mention_ids:
            raise ValueError(f"mention ID already exists: {row['mention_id']}")
    for row in NEW_STATEMENTS:
        if row["statement_id"] in by_id:
            raise ValueError(f"statement ID already exists: {row['statement_id']}")

    open_before = sum(is_open(row) for row in statements)
    no_reason_before = sum(
        is_open(row) and not (row.get("qualifiers") or {}).get("open_endpoint_reason") for row in statements
    )
    true_before = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements)
    false_before = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in statements)
    if (open_before, no_reason_before, true_before, false_before, len(statements)) != (377, 57, 10394, 4753, 15147):
        raise ValueError("unexpected pre-edit S2 statement counts")

    neutrality["subject_candidate_id"] = "cand-8838"
    neutrality["object_candidate_id"] = "cand-12406"
    neutrality["predicate"] = "venice_remained_neutral_during_european_war_context"
    neutrality["original_quote"] = "Europe was at war, but Venice remained neutral."
    neutrality_q = neutrality["qualifiers"]
    neutrality_q["claim"] = "Haskell says Europe was at war while Venice remained neutral."
    neutrality_q["qualification"] = "The war is unnamed; the statement does not identify it with a specific conflict."
    neutrality_q["mentioned_candidate_ids"] = ["cand-3462", "cand-8838", "cand-12406"]
    neutrality_q["relation_candidate_note"] = "The source directly contrasts the European war context with Venice's political neutrality; the conflict remains unidentified."
    neutrality_q.pop("open_endpoint_reason", None)

    for row in NEW_STATEMENTS:
        statements.append(row)
    candidates.extend(NEW_CANDIDATES)
    mentions.extend(NEW_MENTIONS)
    outputs = {
        STATEMENTS: "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in statements).encode("utf-8"),
        CANDIDATES: csv_bytes(candidates, candidate_fields, raw[CANDIDATES].startswith(b"\xef\xbb\xbf")),
        MENTIONS: csv_bytes(mentions, mention_fields, raw[MENTIONS].startswith(b"\xef\xbb\xbf")),
    }
    open_after = sum(is_open(row) for row in statements)
    no_reason_after = sum(
        is_open(row) and not (row.get("qualifiers") or {}).get("open_endpoint_reason") for row in statements
    )
    true_after = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements)
    if (open_after, no_reason_after, true_after, len(statements)) != (377, 56, 10397, 15150):
        raise ValueError(f"unexpected resulting S2 statement state: {(open_after, no_reason_after, true_after, len(statements))}")

    print("reviewed=chapter 10 p.276; split neutrality, embassy intrigue, alliance-seeking, and campaign respite claims")
    print("changes=4 source-bounded candidates, 5 exact mentions including the Venice pronoun, 3 atomic statements added")
    print("open=the embassy intrigue remains open because its target and precise location are not stated")
    print(f"open_endpoints={open_before}->{open_after}; open_without_reason={no_reason_before}->{no_reason_after}; relation_true={true_after}")
    for path, output in outputs.items():
        print(f"{path.name} sha256 {digest(raw[path])}->{digest(output)}")
    if args.preview:
        return 0

    for backup in BACKUPS.values():
        if backup.exists():
            raise FileExistsError(f"recovery copy already exists: {backup.name}")
    temps = {path: path.with_name(path.name + ".tmp-s2-chp10-p276-war-diplomacy-20261015") for path in outputs}
    if any(path.exists() for path in temps.values()):
        raise FileExistsError("protected temporary output already exists")
    for path, backup in BACKUPS.items():
        shutil.copy2(path, backup)
    try:
        for path, output in outputs.items():
            temps[path].write_bytes(output)
        for path in outputs:
            temps[path].replace(path)
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for path, backup in BACKUPS.items():
            shutil.copy2(backup, path)
        raise
    print("backups=" + ", ".join(path.name for path in BACKUPS.values()))
    print("applied_hashes=" + ", ".join(f"{path.name}:{digest(path.read_bytes())}" for path in outputs))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
