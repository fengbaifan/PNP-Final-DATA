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
TABLES = ROOT / "04-knowledge/tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
BACKUP_SUFFIX = "bak-s2-chp9-p258-endpoints-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "d3cd292639506c00bdcfddb7a4825ab52ab30975c64ae817deffe7a953a28984",
    "mentions.csv": "9bf59e1e27bdfab03e2c9dd33a62e24dbd58e9aae72217d11ba7d22e1792874c",
    "book-statements.jsonl": "c801756135ccbf5867ca4f68812b7ced2e03e4d7bba4ca80a007118874b985ae",
}
SEGMENT_ID = "chp-9:09_CHP-9_intro:l179-186"
SEGMENT_HASH = "641f4a86d91e032087e759e6f7d7e3cf356c4cf622a4821ecebc507953276658"
NEW_CANDIDATE = {
    "candidate_id": "cand-12393",
    "canonical_name": "Venetian literature and history as Marco Foscarini's intellectual interests",
    "suggested_type": "term",
    "detail": "The cultural fields Haskell says Marco Foscarini was passionately interested in and planned to study. This is a source-defined topic of intellectual interest, not a publication title or a geographic entity.",
    "candidate_source_ref": f"{SEGMENT_ID}#L186",
}
NEW_STATEMENTS = [
    {
        "statement_id": "st-chp9-p258-guardi-venice-career-relation",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-1245",
        "object_candidate_id": "cand-2719",
        "predicate": "guardi_had_a_relatively_insignificant_career_in_venice",
        "qualifiers": {
            "source_line_start": 180,
            "source_line_end": 181,
            "printed_page": 258,
            "pdf_physical_page": 20,
            "claim": "Haskell says Gian Antonio Guardi enjoyed a relatively insignificant career in Venice.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "qualification": "Authorial evaluation of Guardi's actual career in Venice; preserve 'relatively' and do not treat it as a measured comparison.",
            "mentioned_candidate_ids": ["cand-1245", "cand-2719"],
            "relation_candidate": True,
            "relation_candidate_note": "This row records the actual Venice career claim separately from Haskell's hypothetical Paris comparison.",
        },
        "original_quote": "enjoyed a relatively insignificant career",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
    },
    {
        "statement_id": "st-chp9-p258-guardi-paris-counterfactual",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-1245",
        "object_candidate_id": "cand-4653",
        "predicate": "haskell_hypothesizes_guardi_would_have_triumphated_in_paris",
        "qualifiers": {
            "source_line_start": 180,
            "source_line_end": 181,
            "printed_page": 258,
            "pdf_physical_page": 20,
            "claim": "Haskell says Gian Antonio Guardi would surely have had a triumphant success in Paris.",
            "speaker": "Haskell",
            "text_layer": "authorial counterfactual",
            "qualification": "This is a hypothetical judgment, not a documented Paris career or event; preserve Haskell's 'surely' wording.",
            "mentioned_candidate_ids": ["cand-1245", "cand-4653"],
            "relation_candidate": True,
            "relation_candidate_note": "The source explicitly names Paris as the counterfactual setting; do not convert the prediction into an actual success.",
        },
        "original_quote": "whereas in Paris he would surely have had a triumphant success.",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
    },
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return raw, list(reader.fieldnames or []), list(reader)


def append_rows(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline.decode("ascii"))
    writer.writerows(rows)
    if raw and not raw.endswith((b"\n", b"\r")):
        raw += newline
    return raw + stream.getvalue().encode("utf-8")


def rewrite_csv(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline.decode("ascii"))
    writer.writeheader()
    writer.writerows(rows)
    prefix = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    return prefix + stream.getvalue().encode("utf-8")


def is_open(row: dict[str, object]) -> bool:
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (not row.get("subject_candidate_id") or not row.get("object_candidate_id"))


def endpoint_counts(rows: list[dict[str, object]]) -> tuple[int, int, int, int]:
    opens = [row for row in rows if is_open(row)]
    object_only = sum(bool(row.get("subject_candidate_id")) and not row.get("object_candidate_id") for row in opens)
    subject_only = sum(not row.get("subject_candidate_id") and bool(row.get("object_candidate_id")) for row in opens)
    both = sum(not row.get("subject_candidate_id") and not row.get("object_candidate_id") for row in opens)
    return len(opens), object_only, subject_only, both


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_raw, candidate_fields, candidates = read_csv(CANDIDATES)
    mention_raw, mention_fields, mentions = read_csv(MENTIONS)
    statement_raw = STATEMENTS.read_bytes()
    for name, data in (
        ("entity-candidates.csv", candidate_raw),
        ("mentions.csv", mention_raw),
        ("book-statements.jsonl", statement_raw),
    ):
        if digest(data) != EXPECTED_HASHES[name]:
            raise ValueError(f"Input changed since p.258 review began: {name}")

    segment = next((json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines() if line.strip() and json.loads(line)["segment_id"] == SEGMENT_ID), None)
    if segment is None or segment.get("sha256") != SEGMENT_HASH:
        raise ValueError("The reviewed p.258 source segment changed")
    source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])

    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    if NEW_CANDIDATE["candidate_id"] in candidate_by_id:
        raise ValueError("p.258 literary-field candidate ID already exists")
    if any(
        row["canonical_name"].strip().casefold() == NEW_CANDIDATE["canonical_name"].strip().casefold()
        and row["suggested_type"].strip() == NEW_CANDIDATE["suggested_type"]
        for row in candidates
    ):
        raise ValueError("p.258 literary-field candidate natural key already exists")

    mention_by_id = {row["mention_id"]: row for row in mentions}
    field_mention = mention_by_id.get("m-chp9-p258-venetian-literature-history")
    if (
        field_mention is None
        or field_mention.get("candidate_id") != "cand-2719"
        or field_mention.get("surface_form") != "Venetian literature and history"
        or field_mention.get("start_char") != "2744"
        or field_mention.get("end_char") != "2775"
    ):
        raise ValueError("Expected p.258 cultural-field mention is absent or changed")
    if segment_text[int(field_mention["start_char"]) : int(field_mention["end_char"])] != field_mention["surface_form"]:
        raise ValueError("Existing p.258 field mention no longer matches the source span")

    rows = [json.loads(line) for line in statement_raw.decode("utf-8").splitlines() if line.strip()]
    before_counts = endpoint_counts(rows)
    if before_counts != (407, 254, 50, 103):
        raise ValueError(f"Unexpected pre-update endpoint counts: {before_counts}")
    statement_index = {row["statement_id"]: row for row in rows}
    expected = {
        "st-chp9-p258-funeral-orator-portrait-of-leonardo": ("cand-2689", None),
        "st-chp9-p258-guardi-venice-paris-career": ("cand-1245", None),
        "st-chp9-p258-marco-literary-history-interests-and-studies": ("cand-1053", None),
    }
    for statement_id, endpoints in expected.items():
        row = statement_index.get(statement_id)
        if row is None or not is_open(row) or (row.get("subject_candidate_id"), row.get("object_candidate_id")) != endpoints:
            raise ValueError(f"Reviewed p.258 statement changed: {statement_id}")
    for new_row in NEW_STATEMENTS:
        if new_row["statement_id"] in statement_index:
            raise ValueError(f"New p.258 statement ID already exists: {new_row['statement_id']}")

    funeral = statement_index["st-chp9-p258-funeral-orator-portrait-of-leonardo"]
    funeral["object_candidate_id"] = "cand-8454"
    funeral["predicate"] = "leonardo_character_described_in_funeral_oration"
    funeral["qualifiers"]["relation_candidate_note"] = (
        "The object is the 1765 funeral-oration locator cited in the adjacent footnote; the claim preserves Haskell's explicit warning "
        "that an oration is not an impartial character source."
    )
    funeral["qualifiers"].pop("open_endpoint_reason", None)

    guardi = statement_index["st-chp9-p258-guardi-venice-paris-career"]
    guardi["predicate"] = "haskell_characterizes_guardi_as_magical_and_unserious"
    guardi["qualifiers"]["claim"] = "Haskell characterizes Gian Antonio Guardi as an artist of magical but quite unserious qualities."
    guardi["qualifiers"]["mentioned_candidate_ids"] = ["cand-1245"]
    guardi["qualifiers"]["qualification"] = "Authorial evaluative characterization; the actual Venice career assessment and hypothetical Paris success are recorded separately."
    guardi["qualifiers"]["relation_candidate"] = False
    guardi["qualifiers"]["relation_candidate_note"] = "Nonrelational authorial characterization of the artist; no separate entity endpoint is asserted in this clause."
    guardi["qualifiers"].pop("open_endpoint_reason", None)

    marco = statement_index["st-chp9-p258-marco-literary-history-interests-and-studies"]
    marco["object_candidate_id"] = NEW_CANDIDATE["candidate_id"]
    marco["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(
        (marco["qualifiers"].get("mentioned_candidate_ids") or []) + [NEW_CANDIDATE["candidate_id"]]
    ))
    marco["qualifiers"]["relation_candidate_note"] = (
        "The object is the source-described intellectual field of Venetian literature and history. The individual planned studies remain unnamed; "
        "the row does not imply a complete publication list."
    )
    marco["qualifiers"].pop("open_endpoint_reason", None)

    for new_row in NEW_STATEMENTS:
        rows.append(new_row)
    after_counts = endpoint_counts(rows)
    if after_counts != (404, 251, 50, 103):
        raise ValueError(f"Unexpected post-update endpoint counts: {after_counts}")

    candidate_row = {
        "candidate_id": NEW_CANDIDATE["candidate_id"], "index_entry_id": "",
        "canonical_name": NEW_CANDIDATE["canonical_name"], "index_page_range": "",
        "suggested_type": NEW_CANDIDATE["suggested_type"], "status": "open", "index_source_file": "",
        "sub_entry": "", "detail": NEW_CANDIDATE["detail"], "exclude_reason": "",
        "candidate_origin": "body-mention", "candidate_source_ref": NEW_CANDIDATE["candidate_source_ref"],
    }
    candidate_after = append_rows(candidate_raw, candidate_fields, [candidate_row])
    updated_mentions = [dict(row) for row in mentions]
    for row in updated_mentions:
        if row["mention_id"] == "m-chp9-p258-venetian-literature-history":
            row["candidate_id"] = NEW_CANDIDATE["candidate_id"]
            row["note"] = "Cultural-field concept in Foscarini's reported intellectual interests; distinguish it from the city of Venice."
            break
    mention_after = rewrite_csv(mention_raw, mention_fields, updated_mentions)
    statement_after = ("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)).encode("utf-8")

    true_after = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in rows)
    false_after = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in rows)
    print("reviewed=p.258 Valmarana funeral-oration attribution, Guardi's evaluative/city claims, and Foscarini's literary interests")
    print("resolved=3 previous open rows; atomized Guardi's characterization from Venice career and Paris counterfactual")
    print(f"candidates={len(candidates)}->{len(candidates)+1}; mentions={len(mentions)} unchanged; statements={len(rows)-2}->{len(rows)}")
    print(f"relation_true_false={true_after}/{false_after}; open_endpoints={before_counts}->{after_counts}")
    for name, before, after in (
        ("entity-candidates.csv", candidate_raw, candidate_after),
        ("mentions.csv", mention_raw, mention_after),
        ("book-statements.jsonl", statement_raw, statement_after),
    ):
        print(f"{name} sha256 {digest(before)}->{digest(after)}")
    if args.preview:
        return 0

    outputs = (
        (CANDIDATES, candidate_after),
        (MENTIONS, mention_after),
        (STATEMENTS, statement_after),
    )
    pairs: list[tuple[Path, Path, Path, bytes]] = []
    for path, data in outputs:
        backup = path.with_name(f"{path.name}.{BACKUP_SUFFIX}")
        temporary = path.with_name(f"{path.name}.tmp-{BACKUP_SUFFIX}")
        if backup.exists() or temporary.exists():
            raise FileExistsError(f"Recovery or temporary file already exists: {path.name}")
        pairs.append((path, backup, temporary, data))
    for path, backup, _, _ in pairs:
        shutil.copy2(path, backup)
    replaced: list[tuple[Path, Path]] = []
    try:
        for _, _, temporary, data in pairs:
            temporary.write_bytes(data)
        for path, backup, temporary, _ in pairs:
            temporary.replace(path)
            replaced.append((path, backup))
    except Exception:
        for _, _, temporary, _ in pairs:
            if temporary.exists():
                temporary.unlink()
        for path, backup in replaced:
            shutil.copy2(backup, path)
        raise
    for path, backup, _, _ in pairs:
        print(f"backup={backup.relative_to(ROOT)}")
        print(f"applied_sha256={path.relative_to(ROOT)}:{digest(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
