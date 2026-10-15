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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_ii.md"
SOURCE_SHA = "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9"
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l91-104"
SEGMENT_SHA = "716087759fa887391584b7f7ba1c97d9b5abd70acc8bb895e07045a70d5c04d7"
BACKUP_SUFFIX = ".bak-s2-chp2-secii-l91-104-20261012"
EXPECTED = {
    "book-statements.jsonl": "39a2707af8ebd0594b624b9f6083aa632f16dadbf6e693c51cbea7fddcb0ec88",
    "entity-candidates.csv": "1b4048bf335af8270925c3c59d09936fcd55452c4e845b95e70bc71129b50290",
    "mentions.csv": "95d94c9f669cf128e2ac8a9fb37873648c92d8b3299bf7c06cd3629b561157b5",
    "s2-coverage.csv": "e619ed5e9842616762ab48e255d677a19ffe0cfb3d46f040572ae76f134987c7",
}
UNSET = {
    "st-chp2-secii-l91-104-pietro-fresco-classical-detail-continuation",
    "st-chp2-secii-l91-104-urban-character-and-temperament",
    "st-chp2-secii-l91-104-urban-efficiency-and-knowledge",
    "st-chp2-secii-l91-104-urban-religion-superstition-and-astrology",
    "st-chp2-secii-l91-104-urban-rule-and-papacy-aggrandizement",
    "st-chp2-secii-l91-104-urban-society-and-patronage-evaluation",
    "st-chp2-secii-l91-104-urban-vanity-ambition-and-will",
    "st-chp2-secii-l91-104-pietro-success-assured",
    "st-chp2-secii-l91-104-urban-company-of-poets",
}
GROUPS = [
    {
        "candidate_id": "cand-11886",
        "index_entry_id": "",
        "canonical_name": "Connoisseurs delighted by the classical detail of Pietro da Cortona's S. Bibiana frescoes (unnamed group)",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says the classical detail in Pietro's S. Bibiana frescoes delighted connoisseurs. No individuals or membership boundary are supplied; keep distinct from connoisseur groups in other chapters.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L92",
    },
    {
        "candidate_id": "cand-11887",
        "index_entry_id": "",
        "canonical_name": "Poets whose company Urban VIII valued (unnamed group)",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell attributes a lifelong love of the company of poets to Urban VIII but names no members or formal group. Keep distinct from the unnamed friends he encouraged to abandon pagan mythological themes.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L96",
    },
]
NEW_MENTIONS = [
    {
        "mention_id": "m-chp2-secii-l91-104-0090",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-11886",
        "surface_form": "the connoisseurs",
        "start_char": "77",
        "end_char": "93",
        "note": "Unnamed audience whom Haskell says the classical detail of Pietro's S. Bibiana frescoes delighted; no individual connoisseurs are identified.",
    },
    {
        "mention_id": "m-chp2-secii-l91-104-0091",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-11887",
        "surface_form": "company of poets",
        "start_char": "380",
        "end_char": "396",
        "note": "Source-defined, unnamed social group whose company Urban VIII valued; distinct from the unnamed friends mentioned in the next sentence.",
    },
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def serialize(name: str, rows: list[dict]) -> bytes:
    if name.endswith(".jsonl"):
        return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return ("\ufeff" + buffer.getvalue()).encode("utf-8")


def set_classification(row: dict, value: bool, note: str, mentioned: list[str], open_reason: str | None = None) -> None:
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers["relation_candidate"] = value
    qualifiers["relation_candidate_note"] = note
    qualifiers["mentioned_candidate_ids"] = mentioned
    if open_reason:
        qualifiers["open_endpoint_reason"] = open_reason
    else:
        qualifiers.pop("open_endpoint_reason", None)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after protected checks; default is preview")
    args = parser.parse_args()
    paths = {name: TABLES / name for name in EXPECTED}
    for name, expected in EXPECTED.items():
        actual = digest(paths[name])
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE) != SOURCE_SHA:
        raise SystemExit("protected section source asset changed")
    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected p.40 source segment fingerprint changed")

    statements = read_jsonl(paths["book-statements.jsonl"])
    candidates = read_csv(paths["entity-candidates.csv"])
    mentions = read_csv(paths["mentions.csv"])
    coverage = read_csv(paths["s2-coverage.csv"])
    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(statement_by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"] for row in statements
        if row["segment_id"] == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != UNSET:
        raise SystemExit(f"unexpected p.40 unset statement set: {sorted(unset)}")
    for candidate in GROUPS:
        if candidate["candidate_id"] in candidate_by_id:
            raise SystemExit(f"planned candidate ID already exists: {candidate['candidate_id']}")
    for mention in NEW_MENTIONS:
        if mention["mention_id"] in mention_by_id:
            raise SystemExit(f"planned mention ID already exists: {mention['mention_id']}")
    for cid in ("cand-0220", "cand-0230", "cand-0342", "cand-4448", "cand-4494", "cand-11558"):
        if cid not in candidate_by_id:
            raise SystemExit(f"required p.40 candidate is missing: {cid}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[90:104])
    if "the attention to classical detail which so delighted the connoisseurs" not in source_text:
        raise SystemExit("protected p.40 fresco passage changed")
    if "the company of poets" not in source_text:
        raise SystemExit("protected p.40 poetry passage changed")
    for mention in mentions:
        if mention["segment_id"] != SEGMENT_ID:
            continue
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if source_text[start:end] != mention["surface_form"]:
            raise SystemExit(f"existing p.40 mention span changed or is invalid: {mention['mention_id']}")
    for mention in NEW_MENTIONS:
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if source_text[start:end] != mention["surface_form"]:
            raise SystemExit(f"planned p.40 mention span is invalid: {mention['mention_id']}")

    fresco = statement_by_id["st-chp2-secii-l91-104-pietro-fresco-classical-detail-continuation"]
    fresco["subject_candidate_id"] = "cand-4448"
    fresco["object_candidate_id"] = "cand-11886"
    fresco["predicate"] = "aesthetic_detail_reception_reported"
    fresco["qualifiers"]["claim"] = "Haskell says the classical detail in Pietro da Cortona's S. Bibiana frescoes delighted connoisseurs."
    fresco["qualifiers"]["qualification"] = "Completes the sentence begun at L88-89 and applies to Pietro's S. Bibiana fresco group; the connoisseurs are unnamed."
    set_classification(
        fresco,
        True,
        "The source directly says the classical detail in Pietro's S. Bibiana frescoes delighted connoisseurs; keep the response as author-attributed reception, not as a claim about named viewers.",
        ["cand-4448", "cand-11886"],
        "No individual connoisseurs or bounded membership list is supplied; the source-defined group candidate preserves the audience class without inventing members.",
    )

    false_notes = {
        "st-chp2-secii-l91-104-urban-character-and-temperament": "Haskell's characterization of Urban VIII's appearance and temperament; it does not assert a relation between entities.",
        "st-chp2-secii-l91-104-urban-efficiency-and-knowledge": "Haskell's summary of Urban VIII's personal qualities; it does not identify a separate relation endpoint.",
        "st-chp2-secii-l91-104-urban-religion-superstition-and-astrology": "This is Haskell's combined characterization of Urban VIII's religious feeling and superstition; the separate astrology claim is already recorded in its own statement.",
        "st-chp2-secii-l91-104-urban-rule-and-papacy-aggrandizement": "This row records Haskell's evaluation of petty meanness; his separate claim that Urban failed to aggrandize the papacy remains in the adjacent relation statement.",
        "st-chp2-secii-l91-104-urban-society-and-patronage-evaluation": "This is Haskell's broad interpretive argument about society, character defects, and unspecified monuments; it supplies no bounded entity endpoints for a relation candidate.",
        "st-chp2-secii-l91-104-urban-vanity-ambition-and-will": "Haskell's evaluative characterization of Urban VIII's leading traits; it does not assert an entity-to-entity relation.",
        "st-chp2-secii-l91-104-pietro-success-assured": "Haskell's evaluative forecast about Pietro's career, not a relation to a named endpoint or an independently verified outcome.",
    }
    for sid, note in false_notes.items():
        row = statement_by_id[sid]
        sub = row.get("subject_candidate_id")
        set_classification(row, False, note, [sub] if sub else [])

    company = statement_by_id["st-chp2-secii-l91-104-urban-company-of-poets"]
    company["object_candidate_id"] = "cand-11887"
    company["predicate"] = "valued_company_of_poets_reported"
    company["qualifiers"]["claim"] = "Haskell says Urban VIII retained throughout his life a deep love of the company of poets."
    company["qualifiers"]["qualification"] = "The poets are unnamed; this source-defined group is not a formal institution and is distinct from Urban VIII's unnamed friends mentioned in the next sentence."
    set_classification(
        company,
        True,
        "The source attributes a lifelong social interest in poets to Urban VIII; preserve the unnamed group and do not equate it with the separate friends he advised about pagan themes.",
        ["cand-0230", "cand-11887"],
        "No individual poets or membership list is supplied; the group candidate records only the source-defined company.",
    )

    candidates.extend(GROUPS)
    for new_mention in NEW_MENTIONS:
        later = [
            i for i, row in enumerate(mentions)
            if row["segment_id"] == SEGMENT_ID and int(row["start_char"]) > int(new_mention["start_char"])
        ]
        existing = [i for i, row in enumerate(mentions) if row["segment_id"] == SEGMENT_ID]
        if not existing:
            raise SystemExit("p.40 mention rows are missing")
        insert_at = min(later) if later else max(existing) + 1
        mentions.insert(insert_at, new_mention)

    coverage_rows = [row for row in coverage if row["segment_id"] == SEGMENT_ID]
    if len(coverage_rows) != 1:
        raise SystemExit("expected one p.40 coverage row")
    coverage_note = (
        " S2 follow-up classified the fresco-detail reception and Urban VIII's company of poets as relation candidates with separate unnamed group endpoints. "
        "Seven remaining authorial characterizations, career forecasts, and broad unbounded interpretation are retained as non-relational claims; the explicit papal-aggrandizement relation and astrology claim remain separately recorded. "
        "The printed p.40 page was checked; existing OCR corrections for 'his career' and the leading dash before 'portray' remain in their statement qualifiers, with S0 unchanged."
    )
    if coverage_note.strip() not in coverage_rows[0]["note"]:
        coverage_rows[0]["note"] = coverage_rows[0]["note"].rstrip() + coverage_note

    candidate_ids = {row["candidate_id"] for row in candidates}
    if len(candidate_ids) != len(candidates):
        raise SystemExit("candidate IDs are not unique after write preparation")
    if any(source_text[int(m["start_char"]):int(m["end_char"])] != m["surface_form"] for m in mentions if m["segment_id"] == SEGMENT_ID):
        raise SystemExit("p.40 mention span audit failed")
    remaining = [
        row["statement_id"] for row in statements
        if row["segment_id"] == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    ]
    if remaining:
        raise SystemExit(f"p.40 segment still has unset relation_candidate values: {remaining}")
    for row in statements:
        if row["segment_id"] != SEGMENT_ID:
            continue
        for key in ("subject_candidate_id", "object_candidate_id"):
            if row.get(key) and row[key] not in candidate_ids:
                raise SystemExit(f"p.40 statement has missing {key}: {row['statement_id']} -> {row[key]}")
        referenced = row.get("qualifiers", {}).get("mentioned_candidate_ids", [])
        if set(referenced) - candidate_ids:
            raise SystemExit(f"p.40 statement has missing mentioned candidates: {row['statement_id']}")

    updated = {
        "book-statements.jsonl": statements,
        "entity-candidates.csv": candidates,
        "mentions.csv": mentions,
        "s2-coverage.csv": coverage,
    }
    result = {
        "mode": "apply" if args.apply else "preview",
        "source": "CHP-2 printed p.40 / normalized S0 L91-104",
        "classified_unset_ids": sorted(UNSET),
        "true_relation_candidates": [
            "st-chp2-secii-l91-104-pietro-fresco-classical-detail-continuation",
            "st-chp2-secii-l91-104-urban-company-of-poets",
        ],
        "false_nonrelations": sorted(false_notes),
        "new_candidates": [row["candidate_id"] for row in GROUPS],
        "new_mentions": [row["mention_id"] for row in NEW_MENTIONS],
        "remaining_unset": remaining,
        "counts_delta": {"statements": 0, "candidates": 2, "mentions": 2},
        "source_unchanged": True,
        "payload_sha256": {name: hashlib.sha256(serialize(name, rows)).hexdigest() for name, rows in updated.items()},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temps: dict[str, Path] = {}
    try:
        for name, rows in updated.items():
            path = paths[name]
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
            backups[name] = backup
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
                temp = Path(handle.name)
                handle.write(serialize(name, rows))
            temps[name] = temp
        for name, temp in temps.items():
            os.replace(temp, paths[name])
        written = read_jsonl(paths["book-statements.jsonl"])
        written_by_id = {row["statement_id"]: row for row in written}
        if any(written_by_id[sid].get("qualifiers", {}).get("relation_candidate") is None for sid in UNSET):
            raise SystemExit("a p.40 relation_candidate value was not persisted")
        if digest(SOURCE) != SOURCE_SHA:
            raise SystemExit("source asset changed during write")
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for name, backup in backups.items():
            shutil.copy2(backup, paths[name])
        raise
    print(json.dumps({
        "result": "applied",
        "backups": {name: backup.name for name, backup in backups.items()},
        "written_hashes": {name: digest(path) for name, path in paths.items()},
        "statement_count": len(written),
        "candidate_count": len(candidates),
        "mention_count": len(mentions),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
