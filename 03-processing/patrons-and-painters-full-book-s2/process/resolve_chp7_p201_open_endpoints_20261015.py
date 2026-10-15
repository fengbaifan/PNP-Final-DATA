from __future__ import annotations

import argparse
import copy
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
SOURCE = ROOT / "02-sources/02-Markdown/07_CHP-7_sec_v.md"
SEGMENT_ID = "chp-7:07_CHP-7_sec_v:l42-55"
BACKUP_SUFFIX = "bak-s2-chp7-p201-open-endpoints-20261015"
EXPECTED_INPUT_HASHES = {
    "entity-candidates.csv": "2560801eebc4b50477b7f566aa05a4d2927b9e2f92932093a43696805c6d20e5",
    "mentions.csv": "503e04c6415dea82402bbf73d63646434370ec7f00f2c426a042f2f0edc4de8d",
    "book-statements.jsonl": "c44e54fae9e43db03a634351f20186f781398c9975372f65442a3bb4c9cc5cfa",
}

CANDIDATES_TO_ADD = [
    {
        "candidate_id": "cand-12344",
        "canonical_name": "The lighter manner associated with Venetian painters in Haskell's account (p. 201)",
        "suggested_type": "term",
        "detail": "Haskell says Eugene seems to have shown no interest in this stylistic manner. It is distinct from the group of Venetian painters; no specific artist or work is identified.",
        "line": 52,
    },
    {
        "candidate_id": "cand-12345",
        "canonical_name": "Unspecified theatrical spectacles produced by Ferdinando Galli-Bibiena (p. 201)",
        "suggested_type": "event",
        "detail": "Haskell calls the spectacles marvellous but names no individual production, date, venue, or specific performance.",
        "line": 54,
    },
    {
        "candidate_id": "cand-12346",
        "canonical_name": "Delivery from the Turks and victory against the French cited for Vienna (p. 201)",
        "suggested_type": "event",
        "detail": "Haskell presents relief from the Turks followed by victory against the French as establishing Vienna's status as a great European capital. No specific battle, date, or force is named here.",
        "line": 53,
    },
    {
        "candidate_id": "cand-12347",
        "canonical_name": "Dispersal of Prince Eugene's picture collection (reported p. 201)",
        "suggested_type": "event",
        "detail": "Haskell says the collection has been dispersed. Footnote 2 says much of it was bought by Carlo Emanuele III, but the complete process, date, participants, and destinations are not supplied here.",
        "line": 48,
    },
]

MENTIONS_TO_ADD = [
    {
        "mention_id": "m-chp7-p201-v-lighter-manner",
        "candidate_id": "cand-12344",
        "surface_form": "lighter manner",
        "note": "The stylistic category from which Haskell says Eugene seems to have shown no interest.",
    },
    {
        "mention_id": "m-chp7-p201-v-galli-spectacles",
        "candidate_id": "cand-12345",
        "surface_form": "theatrical spectacles",
        "note": "The unspecified performances attributed to Ferdinando Galli-Bibiena; no individual production is named.",
    },
    {
        "mention_id": "m-chp7-p201-v-vienna-victory",
        "candidate_id": "cand-12346",
        "surface_form": "victory against",
        "note": "Part of the two military outcomes Haskell cites as context for Vienna's rise; the exact conflict is not named.",
    },
    {
        "mention_id": "m-chp7-p201-v-collection-dispersal",
        "candidate_id": "cand-12347",
        "surface_form": "has been dispersed",
        "note": "The reported event affecting Prince Eugene's picture collection; footnote 2 supplies only a partial buyer attribution.",
    },
]

NEW_STATEMENT_ID = "st-chp7-p201-v-parodi-made-statues-for-hall-and-gardens"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return raw, list(reader.fieldnames or []), list(reader)


def append_csv(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline.decode("ascii"), extrasaction="raise")
    writer.writerows(rows)
    if raw and not raw.endswith((b"\n", b"\r")):
        raw += newline
    return raw + stream.getvalue().encode("utf-8")


def is_open_true(row: dict[str, object]) -> bool:
    return (row.get("qualifiers") or {}).get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_raw, candidate_fields, candidate_rows = read_csv(CANDIDATES)
    mention_raw, mention_fields, mention_rows = read_csv(MENTIONS)
    statement_raw = STATEMENTS.read_bytes()
    raw_by_name = {
        "entity-candidates.csv": candidate_raw,
        "mentions.csv": mention_raw,
        "book-statements.jsonl": statement_raw,
    }
    for name, expected in EXPECTED_INPUT_HASHES.items():
        if digest(raw_by_name[name]) != expected:
            raise ValueError(f"Input table changed since preview: {name}")

    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    mention_ids = {row["mention_id"] for row in mention_rows}
    if max(int(cid.removeprefix("cand-")) for cid in candidate_ids) != 12343:
        raise ValueError("Candidate sequence changed")
    if {c["candidate_id"] for c in CANDIDATES_TO_ADD} & candidate_ids:
        raise ValueError("A planned candidate ID already exists")
    if {m["mention_id"] for m in MENTIONS_TO_ADD} & mention_ids:
        raise ValueError("A planned mention ID already exists")

    segment = next(
        json.loads(line) for line in SEGMENTS.open(encoding="utf-8")
        if json.loads(line).get("segment_id") == SEGMENT_ID
    )
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    text = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])
    added_mentions: list[dict[str, str]] = []
    spans: list[tuple[int, int, str]] = []
    for mention in MENTIONS_TO_ADD:
        start = text.find(mention["surface_form"])
        if start < 0 or text.find(mention["surface_form"], start + 1) >= 0:
            raise ValueError(f"Source phrase missing or repeated: {mention['mention_id']}")
        end = start + len(mention["surface_form"])
        if any(start < old_end and old_start < end for old_start, old_end, _ in spans):
            raise ValueError(f"Planned mentions overlap: {mention['mention_id']}")
        spans.append((start, end, mention["mention_id"]))
        for old in mention_rows:
            if old["segment_id"] != SEGMENT_ID:
                continue
            old_start, old_end = int(old["start_char"]), int(old["end_char"])
            if start < old_end and old_start < end:
                raise ValueError(f"New mention overlaps existing mention {old['mention_id']}")
        added_mentions.append({
            "mention_id": mention["mention_id"], "segment_id": SEGMENT_ID,
            "candidate_id": mention["candidate_id"], "surface_form": mention["surface_form"],
            "start_char": str(start), "end_char": str(end), "note": mention["note"],
        })

    rows = [json.loads(line) for line in statement_raw.decode("utf-8").splitlines()]
    index = {row["statement_id"]: i for i, row in enumerate(rows)}
    expected = {
        "st-chp7-p201-v-eugene-no-interest-in-venetian-manner": ("cand-2386", None),
        "st-chp7-p201-v-eugene-private-patron": ("cand-2385", None),
        "st-chp7-p201-v-galli-bibiena-theatrical-spectacles": ("cand-1112", None),
        "st-chp7-p201-v-mattielli-parodi-statues": (None, "cand-7312"),
        "st-chp7-p201-v-picture-collection-dispersed": ("cand-7309", None),
        "st-chp7-p201-v-vienna-rise-after-military-victories": ("cand-2772", None),
    }
    if not set(expected) <= index.keys() or NEW_STATEMENT_ID in index:
        raise ValueError("A target or planned statement ID is missing or already exists")
    for sid, (subject, obj) in expected.items():
        row = rows[index[sid]]
        if row.get("segment_id") != SEGMENT_ID or row.get("subject_candidate_id") != subject or row.get("object_candidate_id") != obj or not is_open_true(row):
            raise ValueError(f"Target statement identity or open endpoint changed: {sid}")

    before_open = sum(1 for row in rows if is_open_true(row))
    if before_open != 466:
        raise ValueError(f"Open endpoint count changed: expected 466, got {before_open}")

    style = rows[index["st-chp7-p201-v-eugene-no-interest-in-venetian-manner"]]
    style["object_candidate_id"] = "cand-12344"
    style_q = style["qualifiers"]
    style_q["mentioned_candidate_ids"] = list(dict.fromkeys(style_q.get("mentioned_candidate_ids", []) + ["cand-12344"]))
    style_q["relation_candidate_note"] = "The object is the explicitly named lighter Venetian manner; it remains distinct from the Venetian painters who worked in Vienna. Preserve Haskell's 'seems' qualification."
    style_q.pop("open_endpoint_reason", None)

    patron = rows[index["st-chp7-p201-v-eugene-private-patron"]]
    patron["object_candidate_id"] = "cand-3462"
    patron["predicate"] = "described_as_most_grandiose_influential_private_patron_in"
    patron_q = patron["qualifiers"]
    patron_q["mentioned_candidate_ids"] = list(dict.fromkeys(patron_q.get("mentioned_candidate_ids", []) + ["cand-3462"]))
    patron_q["relation_candidate_note"] = "Europe is the explicit geographic scope. The superlative remains Haskell's qualitative judgment; the comparison set is not enumerated."
    patron_q.pop("open_endpoint_reason", None)

    spectacles = rows[index["st-chp7-p201-v-galli-bibiena-theatrical-spectacles"]]
    spectacles["object_candidate_id"] = "cand-12345"
    spectacles_q = spectacles["qualifiers"]
    spectacles_q["mentioned_candidate_ids"] = list(dict.fromkeys(spectacles_q.get("mentioned_candidate_ids", []) + ["cand-12345"]))
    spectacles_q["relation_candidate_note"] = "The object is the source-named group of theatrical performances; no individual production, date, venue, or work is inferred."
    spectacles_q.pop("open_endpoint_reason", None)

    statues_template = copy.deepcopy(rows[index["st-chp7-p201-v-mattielli-parodi-statues"]])
    mattielli = rows[index["st-chp7-p201-v-mattielli-parodi-statues"]]
    mattielli["subject_candidate_id"] = "cand-1584"
    mattielli["qualifiers"]["claim"] = "Haskell says Lorenzo Mattielli made statues for the hall and gardens."
    mattielli["qualifiers"]["qualification"] = "Haskell names Mattielli and Parodi together as makers but does not assign individual statues or exact sites to either."
    mattielli["qualifiers"]["relation_candidate_note"] = "This records Mattielli as one of the two named makers of the unspecified statue group; it does not assign a particular statue to him."
    mattielli["qualifiers"].pop("open_endpoint_reason", None)
    parodi = statues_template
    parodi["statement_id"] = NEW_STATEMENT_ID
    parodi["subject_candidate_id"] = "cand-1841"
    parodi["object_candidate_id"] = "cand-7312"
    parodi["qualifiers"]["claim"] = "Haskell says Domenico Antonio Parodi made statues for the hall and gardens."
    parodi["qualifiers"]["qualification"] = "Haskell names Mattielli and Parodi together as makers but does not assign individual statues or exact sites to either."
    parodi["qualifiers"]["relation_candidate_note"] = "This records Parodi as one of the two named makers of the unspecified statue group; it does not assign a particular statue to him."
    parodi["qualifiers"].pop("open_endpoint_reason", None)

    collection = rows[index["st-chp7-p201-v-picture-collection-dispersed"]]
    collection["object_candidate_id"] = "cand-12347"
    collection_q = collection["qualifiers"]
    collection_q["mentioned_candidate_ids"] = list(dict.fromkeys(collection_q.get("mentioned_candidate_ids", []) + ["cand-12347"]))
    collection_q["relation_candidate_note"] = "The object is the reported dispersal event. Footnote 2 says much of the collection was bought by Carlo Emanuele III, but this is only a partial destination and does not enumerate the entire process."
    collection_q["related_statement_ids"] = ["st-chp7-p201-n2-eugene-collection-acquired"]
    collection_q.pop("open_endpoint_reason", None)

    vienna = rows[index["st-chp7-p201-v-vienna-rise-after-military-victories"]]
    vienna["object_candidate_id"] = "cand-12346"
    vienna_q = vienna["qualifiers"]
    vienna_q["mentioned_candidate_ids"] = list(dict.fromkeys(vienna_q.get("mentioned_candidate_ids", []) + ["cand-12346"]))
    vienna_q["relation_candidate_note"] = "The object is the source-described sequence of relief from the Turks and victory against the French. Exact battles, dates, and forces remain unspecified; 'new Rome' is not treated as identity."
    vienna_q["related_statement_ids"] = ["st-chp7-p199-vienna-saved-1683"]
    vienna_q.pop("open_endpoint_reason", None)

    added_candidates = [
        {
            "candidate_id": c["candidate_id"], "index_entry_id": "",
            "canonical_name": c["canonical_name"], "index_page_range": "",
            "suggested_type": c["suggested_type"], "status": "open",
            "index_source_file": "", "sub_entry": "", "detail": c["detail"],
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L{c['line']}",
        }
        for c in CANDIDATES_TO_ADD
    ]
    candidate_after = append_csv(candidate_raw, candidate_fields, added_candidates)
    mention_after = append_csv(mention_raw, mention_fields, added_mentions)
    statement_after = ("".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
        for row in rows + [parodi]
    )).encode("utf-8")
    paths = {CANDIDATES: candidate_after, MENTIONS: mention_after, STATEMENTS: statement_after}
    after_rows = [json.loads(line) for line in statement_after.decode("utf-8").splitlines()]
    after_open = sum(1 for row in after_rows if is_open_true(row))
    segment_open = [row["statement_id"] for row in after_rows if row.get("segment_id") == SEGMENT_ID and is_open_true(row)]
    if after_open != 460 or segment_open:
        raise ValueError(f"Unexpected post-update open state: {after_open}, {segment_open}")

    print(f"candidate_rows={len(candidate_rows)}->{len(candidate_rows) + len(added_candidates)}")
    print(f"mention_rows={len(mention_rows)}->{len(mention_rows) + len(added_mentions)}")
    print(f"statement_rows={len(rows)}->{len(rows) + 1}")
    print(f"open_endpoints={before_open}->{after_open}")
    print(f"segment_open={segment_open}")
    for candidate in added_candidates:
        print(f"planned_candidate={candidate['candidate_id']}|{candidate['suggested_type']}|{candidate['canonical_name']}")
    for mention in added_mentions:
        print(f"planned_mention={mention['mention_id']}|{mention['candidate_id']}|[{mention['start_char']},{mention['end_char']}) {mention['surface_form']}")
    for sid, (subject, _) in expected.items():
        updated_row = after_rows[index[sid]]
        print(f"planned_endpoint={sid}|{updated_row.get('subject_candidate_id')}->{updated_row.get('object_candidate_id')}")
    print(f"planned_statement={NEW_STATEMENT_ID}|cand-1841->cand-7312")
    for path, data in paths.items():
        print(f"{path.relative_to(ROOT)} {digest(path.read_bytes())}->{digest(data)}")
    if args.preview:
        return 0

    backups = {path: path.with_name(f"{path.name}.{BACKUP_SUFFIX}") for path in paths}
    if any(backup.exists() for backup in backups.values()):
        raise FileExistsError("A recovery copy already exists; refusing to overwrite it")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    temps: dict[Path, Path] = {}
    try:
        for path, data in paths.items():
            temp = path.with_name(f"{path.name}.tmp-{BACKUP_SUFFIX}")
            if temp.exists():
                raise FileExistsError(f"Temporary file already exists: {temp}")
            temp.write_bytes(data)
            temps[path] = temp
        for path, temp in temps.items():
            temp.replace(path)
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        raise
    for path, backup in backups.items():
        print(f"backup={backup.relative_to(ROOT)}")
        print(f"applied_sha256={path.relative_to(ROOT)}:{digest(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
