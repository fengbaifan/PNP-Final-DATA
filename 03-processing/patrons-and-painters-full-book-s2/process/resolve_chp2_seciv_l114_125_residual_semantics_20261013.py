from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l114-125"
SOURCE_SHA = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
SEGMENT_SHA = "9f19718c42f5753aa5b75f1317c40ad493602c9539fac022a1a681d37c2b4877"
EXPECTED_TABLES = {
    "book-statements.jsonl": "bb7da30caac080c30fdcb4f7e0c0ea920a1862e012527b22ac6bc592ad6e3dd6",
    "entity-candidates.csv": "871e0dc4ee93d34576548f989831c49343130cad503442330698989ec4a838d8",
    "mentions.csv": "e8ca2fa4868f030bfeeeec17d5f92ccca6c10c417739c3e49979e9837969a7b8",
}
BACKUP_SUFFIX = ".bak-s2-chp2-seciv-l114-125-semantic-residuals-20261013"
UNSET_IDS = {
    "st-chp2-seciv-l114-125-antonio-appearance",
    "st-chp2-seciv-l114-125-antonio-character-judgement",
    "st-chp2-seciv-l114-125-antonio-first-legate",
    "st-chp2-seciv-l114-125-antonio-income-from-posts",
    "st-chp2-seciv-l114-125-duke-heirless-son",
    "st-chp2-seciv-l114-125-francesco-scholarly-network",
    "st-chp2-seciv-l114-125-temperament-and-taste",
}
NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11891",
        "index_entry_id": "",
        "canonical_name": "Legate office assumed by Antonio Barberini after Urbino's transfer (exact scope unspecified)",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says Antonio followed Taddeo across the frontier and became the first Legate. The passage associates the office with the transfer of Urbino but does not name its exact jurisdiction, formal title, or appointment date.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L122",
    },
    {
        "candidate_id": "cand-11892",
        "index_entry_id": "",
        "canonical_name": "Unspecified official posts held by Cardinal Antonio Barberini (income source, p.54)",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell attributes Antonio's vast income to many official posts but does not itemize them. Do not assume this entire group is identical to the several French posts in cand-4925 or to the Legate office recorded separately in this passage.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L117",
    },
    {
        "candidate_id": "cand-11893",
        "index_entry_id": "",
        "canonical_name": "Unnamed heirless son of Francesco Maria della Rovere, Duke of Urbino",
        "index_page_range": "",
        "suggested_type": "person",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says the duke's unnamed son had no heir and died before his father. No personal name or identity is supplied; do not guess one.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L121",
    },
    {
        "candidate_id": "cand-11894",
        "index_entry_id": "",
        "canonical_name": "European scholars described as Cardinal Francesco's correspondents and friends (unnamed group)",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell calls Francesco a correspondent and friend of 'half the scholars of Europe'. Treat 'half' as rhetorical hyperbole, not a literal fraction or closed membership list; no scholars are named.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L117",
    },
]
NEW_MENTIONS = [
    ("m-chp2-seciv-l114-125-0063", "cand-11891", "the first Legate", 2174, 2190,
     "The office Antonio is said to assume after Taddeo crosses the frontier; exact jurisdiction remains unspecified."),
    ("m-chp2-seciv-l114-125-0064", "cand-11893", "heirless son", 1768, 1780,
     "Unnamed son of Francesco Maria della Rovere; the source says he had no heir and predeceased his father."),
]
REMAP_MENTIONS = {
    "m-chp2-seciv-l114-125-0002": (
        "cand-11894",
        "The unnamed scholars described hyperbolically as Francesco's correspondents and friends; no membership list or literal fraction is asserted.",
    ),
    "m-chp2-seciv-l114-125-0013": (
        "cand-11892",
        "The unspecified official posts to which Haskell attributes Antonio's income; the posts are not itemized.",
    ),
}
NEW_STATEMENTS = [
    {
        "statement_id": "st-chp2-seciv-l114-125-antonio-greed-appeased-by-income",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-0187",
        "object_candidate_id": None,
        "predicate": "authorial_psychological_characterization",
        "qualifiers": {
            "source_line_start": 117, "source_line_end": 117,
            "claim": "Haskell says Antonio's greed was to some extent appeased.",
            "speaker": "Haskell", "text_layer": "authorial evaluative characterization",
            "print_page": 54, "pdf_physical_page": 39,
            "qualification": "The source uses 'the former' to refer to greed; the source's separate statement about income from official posts is recorded independently.",
            "relation_candidate": False,
            "relation_candidate_note": "This is an authorial characterization of Antonio's disposition, not a relation candidate.",
            "mentioned_candidate_ids": ["cand-0187"],
            "related_statement_ids": ["st-chp2-seciv-l114-125-antonio-income-from-posts"],
        },
        "original_quote": "The former was to some extent appeased",
        "origin": "book", "source_file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
    },
    {
        "statement_id": "st-chp2-seciv-l114-125-francesco-characterized-as-learned",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-0203",
        "object_candidate_id": None,
        "predicate": "person_described_as_learned_by_author",
        "qualifiers": {
            "source_line_start": 117, "source_line_end": 117,
            "claim": "Haskell describes Cardinal Francesco as learned.",
            "speaker": "Haskell", "text_layer": "authorial characterization",
            "print_page": 54, "pdf_physical_page": 39,
            "relation_candidate": False,
            "relation_candidate_note": "This is an authorial description of Francesco's learning, not a relation candidate.",
            "mentioned_candidate_ids": ["cand-0203"],
            "related_statement_ids": ["st-chp2-seciv-l114-125-francesco-scholarly-network"],
        },
        "original_quote": "The learned Cardinal Francesco",
        "origin": "book", "source_file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
    },
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> tuple[list[dict], bytes]:
    raw = path.read_bytes()
    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    return rows, raw


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bytes]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader), raw


def serialize_jsonl(rows: list[dict], original: bytes) -> bytes:
    payload = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")
    return (b"\xef\xbb\xbf" + payload) if original.startswith(b"\xef\xbb\xbf") else payload


def serialize_csv(fieldnames: list[str], rows: list[dict[str, str]], original: bytes) -> bytes:
    buffer = io.StringIO(newline="")
    ending = "\r\n" if b"\r\n" in original else "\n"
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator=ending, extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    payload = buffer.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + payload) if original.startswith(b"\xef\xbb\xbf") else payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve residual semantics in CHP-2 p.54 after protected preview.")
    parser.add_argument("--apply", action="store_true", help="write after preview; default does not modify files")
    args = parser.parse_args()

    paths = {name: TABLES / name for name in EXPECTED_TABLES}
    raw = {name: path.read_bytes() for name, path in paths.items()}
    for name, expected in EXPECTED_TABLES.items():
        actual = digest(raw[name])
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE.read_bytes()) != SOURCE_SHA:
        raise SystemExit("protected S0 source asset changed")
    segments, _ = read_jsonl(TABLES / "segments.jsonl")
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected p.54 source segment fingerprint changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    if digest(segment_text.encode("utf-8")) != SEGMENT_SHA:
        raise SystemExit("p.54 segment content differs from its protected fingerprint")

    statements, statement_raw = read_jsonl(paths["book-statements.jsonl"])
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement IDs already exist")
    unset = {
        row["statement_id"] for row in statements
        if row.get("segment_id") == SEGMENT_ID and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    if unset != UNSET_IDS:
        raise SystemExit(f"unexpected p.54 unset set: {sorted(unset)}")
    planned_ids = {row["statement_id"] for row in NEW_STATEMENTS}
    if planned_ids & by_id.keys():
        raise SystemExit(f"planned statement IDs already exist: {sorted(planned_ids & by_id.keys())}")

    candidate_fields, candidates, candidate_raw = read_csv(paths["entity-candidates.csv"])
    mention_fields, mentions, mention_raw = read_csv(paths["mentions.csv"])
    with (TABLES / "s2-coverage.csv").open(encoding="utf-8-sig", newline="") as handle:
        coverage_rows = [row for row in csv.DictReader(handle) if row.get("segment_id") == SEGMENT_ID]
    if (len(coverage_rows) != 1 or coverage_rows[0].get("disposition") != "reviewed"
            or coverage_rows[0].get("migration_status") != "complete"
            or "L116-125" not in coverage_rows[0].get("source_line_ranges", "")):
        raise SystemExit("p.54 S2 coverage is missing or does not cover reviewed lines L116-L125")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    planned_candidate_ids = {row["candidate_id"] for row in NEW_CANDIDATES}
    if planned_candidate_ids & candidate_by_id.keys():
        raise SystemExit(f"planned candidate IDs already exist: {sorted(planned_candidate_ids & candidate_by_id.keys())}")
    numeric_ids = [int(row["candidate_id"][5:]) for row in candidates if row.get("candidate_id", "").startswith("cand-") and row["candidate_id"][5:].isdigit()]
    if max(numeric_ids, default=0) != 11890:
        raise SystemExit(f"unexpected candidate ID maximum: {max(numeric_ids, default=0)}")
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(mention_by_id) != len(mentions):
        raise SystemExit("duplicate mention IDs already exist")
    if {item[0] for item in NEW_MENTIONS} & mention_by_id.keys():
        raise SystemExit("a planned mention ID already exists")
    for mention_id, (candidate_id, note) in REMAP_MENTIONS.items():
        row = mention_by_id.get(mention_id)
        if not row or row.get("candidate_id") not in {"cand-0203", "cand-0187"}:
            raise SystemExit(f"unexpected existing mention state: {mention_id}")
        if segment_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
            raise SystemExit(f"existing mention span no longer matches the segment: {mention_id}")
        row["candidate_id"] = candidate_id
        row["note"] = note
    for mention_id, candidate_id, surface, start, end, note in NEW_MENTIONS:
        if segment_text[start:end] != surface:
            raise SystemExit(f"protected mention span mismatch: {surface!r} at {start}:{end}")
        mentions.append({
            "mention_id": mention_id, "segment_id": SEGMENT_ID, "candidate_id": candidate_id,
            "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
        })

    decisions = {
        "st-chp2-seciv-l114-125-antonio-appearance": (
            "This is Haskell's literary description of Antonio's appearance and manner, not a relation claim."
        ),
        "st-chp2-seciv-l114-125-antonio-character-judgement": (
            "This is Haskell's evaluative judgment about Antonio's qualifications and motives, not a relation claim or independently verified motive."
        ),
        "st-chp2-seciv-l114-125-temperament-and-taste": (
            "This is Haskell's broad generalization about temperament and aesthetic taste; neither term is asserted as a distinct relational endpoint."
        ),
    }
    for statement_id, note in decisions.items():
        row = by_id[statement_id]
        row["qualifiers"]["relation_candidate"] = False
        row["qualifiers"]["relation_candidate_note"] = note

    legate = by_id["st-chp2-seciv-l114-125-antonio-first-legate"]
    legate["object_candidate_id"] = "cand-11891"
    legate["predicate"] = "person_assumes_legatine_office_reported"
    legate_q = legate["qualifiers"]
    legate_q.update({
        "claim": "Haskell says Antonio followed Taddeo soon after and became the first Legate.",
        "time_relation": "Soon after Taddeo crossed the frontier in 1631; no exact date is supplied.",
        "qualification": "The immediate context is the transfer of Urbino to papal control, but the office's exact territorial scope is not stated.",
        "relation_candidate": True,
        "relation_candidate_note": "Haskell explicitly says Antonio became the first Legate; preserve the office as an open term candidate because its precise jurisdiction and formal title are not supplied.",
        "mentioned_candidate_ids": ["cand-0187", "cand-11891"],
    })

    income = by_id["st-chp2-seciv-l114-125-antonio-income-from-posts"]
    income["object_candidate_id"] = "cand-11892"
    income["predicate"] = "person_derives_income_from_official_posts"
    income["original_quote"] = "the vast income he derived from his many official posts"
    income_q = income["qualifiers"]
    income_q.update({
        "claim": "Haskell says Antonio derived a vast income from his many official posts.",
        "qualification": "The posts and income are not itemized or dated; keep this source-defined role group distinct from specific posts elsewhere until their overlap is established.",
        "relation_candidate": True,
        "relation_candidate_note": "The source explicitly attributes Antonio's income to many official posts. Preserve the relation to an open group of office terms; no individual office or grantor is inferred.",
        "mentioned_candidate_ids": ["cand-0187", "cand-11892"],
        "related_statement_ids": ["st-chp2-seciv-l114-125-antonio-greed-appeased-by-income"],
    })

    duke_son = by_id["st-chp2-seciv-l114-125-duke-heirless-son"]
    duke_son["object_candidate_id"] = "cand-11893"
    duke_son["predicate"] = "dukes_unnamed_son_predeceases_him_without_heir"
    son_q = duke_son["qualifiers"]
    son_q["qualification"] = "The son is represented by an open person candidate because the source supplies a distinct kinship and chronology but no personal name; do not guess an identity."
    son_q["relation_candidate"] = True
    son_q["relation_candidate_note"] = "The source explicitly identifies the duke's son as a distinct person who predeceased him and had no heir; his name remains unknown."
    son_q["mentioned_candidate_ids"] = ["cand-2671", "cand-11893"]

    network = by_id["st-chp2-seciv-l114-125-francesco-scholarly-network"]
    network["object_candidate_id"] = "cand-11894"
    network["predicate"] = "person_corresponded_with_and_was_friend_of_scholars"
    network["original_quote"] = "correspondent and friend of half the scholars of Europe"
    network_q = network["qualifiers"]
    network_q.update({
        "claim": "Haskell describes Cardinal Francesco as corresponding with and befriending an extensive, unnamed group of European scholars.",
        "qualification": "'Half the scholars of Europe' is rhetorical hyperbole, not a literal count or closed membership list; no individuals are supplied.",
        "relation_candidate": True,
        "relation_candidate_note": "The source explicitly characterizes Francesco as a correspondent and friend of a broad scholarly group; preserve that open group without inferring its members or literal size.",
        "mentioned_candidate_ids": ["cand-0203", "cand-11894"],
        "related_statement_ids": ["st-chp2-seciv-l114-125-francesco-characterized-as-learned"],
    })

    statements.extend(NEW_STATEMENTS)
    candidates.extend(NEW_CANDIDATES)

    # Confirm the new quotes are exact substrings of their cited source lines.
    for row in [*NEW_STATEMENTS, legate, income, duke_son, network]:
        qualifiers = row["qualifiers"]
        line_start = int(qualifiers["source_line_start"])
        line_end = int(qualifiers["source_line_end"])
        cited_text = " ".join(source_lines[line_start - 1:line_end])
        if " ".join(row["original_quote"].split()) not in " ".join(cited_text.split()):
            raise SystemExit(f"quote is not contained in cited source lines: {row['statement_id']}")

    outputs = {
        "book-statements.jsonl": serialize_jsonl(statements, statement_raw),
        "entity-candidates.csv": serialize_csv(candidate_fields, candidates, candidate_raw),
        "mentions.csv": serialize_csv(mention_fields, mentions, mention_raw),
    }
    print(f"segment={SEGMENT_ID}; source_lines=L116-L125; print_page=54; pdf_physical_page=39")
    print("classifications: 4 true relation candidates (two open term groups, one office term, one unnamed person); 5 false scalar/evaluative statements after two atomic splits")
    print("new_candidates=" + ",".join(row["candidate_id"] for row in NEW_CANDIDATES))
    print("new_mentions=" + ",".join(row[0] for row in NEW_MENTIONS) + "; remapped=2 existing mention candidates")
    print("new_statements=" + ",".join(row["statement_id"] for row in NEW_STATEMENTS))
    for name, data in outputs.items():
        print(f"{name}: {digest(raw[name])} -> {digest(data)}")
    if not args.apply:
        print("mode=preview; no files changed")
        return

    backups = {name: paths[name].with_name(paths[name].name + BACKUP_SUFFIX) for name in paths}
    present = [path for path in backups.values() if path.exists()]
    if present:
        raise SystemExit(f"backup already exists: {present[0]}")
    for name, path in paths.items():
        shutil.copy2(path, backups[name])
    temps: dict[str, Path] = {}
    for name, path in paths.items():
        tmp = path.with_name(path.name + ".tmp-s2-l114-125")
        tmp.write_bytes(outputs[name])
        temps[name] = tmp
    for name, path in paths.items():
        temps[name].replace(path)
    print("mode=apply; backups=" + ",".join(path.name for path in backups.values()))
    for name, path in paths.items():
        print(f"written {name}: {digest(path.read_bytes())}")


if __name__ == "__main__":
    main()
