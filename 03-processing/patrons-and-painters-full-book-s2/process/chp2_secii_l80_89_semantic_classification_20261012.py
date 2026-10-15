from __future__ import annotations

import argparse
import copy
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
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l80-89"
SEGMENT_SHA = "e1d901252d516f1c9a17a7024d6fb2ecefd1346c48f25c13aa87e1c48e8a8bf3"
BACKUP_SUFFIX = ".bak-s2-chp2-secii-l80-89-20261012"
EXPECTED = {
    "book-statements.jsonl": "7bd8eadc0162e1f328646899d542629a9743471f6b326b739708bf30d71f04d1",
    "entity-candidates.csv": "168052abd79d9a7c72735690564aaa538fd8e048993aaac9971d77aee3f4baaf",
    "mentions.csv": "948ffdc32c6d07f5b84dbf0c695223eeec60da9f347464b6bd5c0a14d6dc4b87",
    "s2-coverage.csv": "1c51aef816d517b52bd5c0b609a30da5bab3da3893cb66f6b924cc5eec40774b",
}
UNSET = {
    "st-chp2-secii-l80-89-copying-as-training-generalization",
    "st-chp2-secii-l80-89-marcello-learned-poet-patron",
    "st-chp2-secii-l80-89-sacchetti-position-changed",
    "st-chp2-secii-l80-89-urban-became-pope",
}
NEW_STATEMENT_ID = "st-chp2-secii-l80-89-marcello-welcomes-pietro"
NEW_CANDIDATE = {
    "candidate_id": "cand-11885",
    "index_entry_id": "",
    "canonical_name": "Artists required to undergo similar copying training (unnamed class)",
    "index_page_range": "",
    "suggested_type": "term",
    "status": "open",
    "index_source_file": "",
    "sub_entry": "",
    "detail": "Haskell generalizes that every artist thereafter was required to undergo training like Pietro's copying of Raphael and Titian. No individual artists or imposing authority are named; retain the universal scope as the author's assertion.",
    "exclude_reason": "",
    "candidate_origin": "body-mention",
    "candidate_source_ref": f"{SEGMENT_ID}#L81",
}
NEW_MENTION = {
    "mention_id": "m-chp2-secii-l80-89-0084",
    "segment_id": SEGMENT_ID,
    "candidate_id": "cand-11885",
    "surface_form": "every artist",
    "start_char": "400",
    "end_char": "412",
    "note": "Haskell's universal professional class in the claim about similar copying training; no individual artists are specified.",
}


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


def set_relation(
    row: dict,
    value: bool,
    note: str,
    mentioned: list[str],
    open_reason: str | None = None,
) -> None:
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
        raise SystemExit("protected p.39 source segment fingerprint changed")

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
        raise SystemExit(f"unexpected p.39 unset statement set: {sorted(unset)}")
    if NEW_STATEMENT_ID in statement_by_id:
        raise SystemExit("planned split statement ID already exists")
    if NEW_CANDIDATE["candidate_id"] in candidate_by_id:
        raise SystemExit("planned p.39 candidate ID already exists")
    if NEW_MENTION["mention_id"] in mention_by_id:
        raise SystemExit("planned p.39 mention ID already exists")
    for cid in ("cand-0295", "cand-0342", "cand-2316", "cand-2317", "cand-0209", "cand-4223", "cand-4476", "cand-2098", "cand-2630", "cand-4452"):
        if cid not in candidate_by_id:
            raise SystemExit(f"required p.39 candidate is missing: {cid}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[79:89])
    for phrase in (
        "Thereafter every artist was required to undergo similar training.",
        "to whom the eager young Pietro was especially welcome.",
        "By this time Urban VIII had become Pope",
    ):
        if phrase not in source_text:
            raise SystemExit(f"protected p.39 passage changed; re-review before applying: {phrase}")
    if source_text[400:412] != "every artist":
        raise SystemExit("protected p.39 mention span changed")

    for mention in mentions:
        if mention["segment_id"] != SEGMENT_ID:
            continue
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if source_text[start:end] != mention["surface_form"]:
            raise SystemExit(f"existing p.39 mention span changed or is invalid: {mention['mention_id']}")
    pope_mention = mention_by_id.get("m-chp2-secii-l80-89-0041")
    if not pope_mention or pope_mention.get("candidate_id") != "cand-0209" or pope_mention.get("surface_form") != "Pope":
        raise SystemExit("expected Urban VIII's office-title mention changed; re-review before correcting")

    training = statement_by_id["st-chp2-secii-l80-89-copying-as-training-generalization"]
    training["subject_candidate_id"] = "cand-11885"
    training["original_quote"] = "Thereafter every artist was required to undergo similar training."
    training["qualifiers"]["claim"] = "Haskell says every artist thereafter was required to undergo training similar to Pietro's copying of Raphael and Titian."
    set_relation(
        training,
        True,
        "This is Haskell's source-attributed generalization linking the artist class to a copying-based training practice; retain the universal wording as his claim.",
        ["cand-11885", "cand-4476", "cand-2098", "cand-2630"],
        "The source names no individual artists or authority imposing the requirement; preserve only the source-defined professional class and training practice.",
    )
    training["qualifiers"]["model_artist_candidate_ids"] = ["cand-2098", "cand-2630"]

    profile = statement_by_id["st-chp2-secii-l80-89-marcello-learned-poet-patron"]
    welcoming = copy.deepcopy(profile)
    profile["original_quote"] = "He was a learned man, steeped in classical culture, and a poet, a new type of patron"
    profile["qualifiers"]["claim"] = "Haskell describes Marcello as learned, steeped in classical culture, and a poet, and characterizes him as a new type of patron."
    profile["qualifiers"].pop("artist_candidate_id", None)
    set_relation(
        profile,
        False,
        "This statement records Haskell's attributed profile and social characterization of Marcello; the explicit welcome relation to Pietro is separated into its own statement.",
        ["cand-2317", "cand-2314"],
    )

    welcoming.update({
        "statement_id": NEW_STATEMENT_ID,
        "subject_candidate_id": "cand-2316",
        "object_candidate_id": "cand-0342",
        "predicate": "artist_welcomed_by_patron_reported",
        "original_quote": "to whom the eager young Pietro was especially welcome.",
        "qualifiers": copy.deepcopy(profile["qualifiers"]),
    })
    welcoming["qualifiers"]["claim"] = "Haskell says the eager young Pietro was especially welcome to Marcello, whom he presents as a new type of patron."
    welcoming["qualifiers"]["artist_candidate_id"] = "cand-0342"
    set_relation(
        welcoming,
        True,
        "The source explicitly says Pietro was especially welcome to Marcello in his role as a new type of patron; keep this relational claim separate from Marcello's personal profile.",
        ["cand-2316", "cand-0342"],
    )
    statements.insert(statements.index(profile) + 1, welcoming)

    position = statement_by_id["st-chp2-secii-l80-89-sacchetti-position-changed"]
    position["qualifiers"]["qualification"] = (
        "This is Haskell's collective transition summary; the following clauses specify Giulio's Church career and Marcello's offices and privileges separately. "
        "It does not attribute the change causally to Urban VIII's accession."
    )
    set_relation(
        position,
        False,
        "The sentence is a broad authorial transition summary; its concrete status changes are recorded in adjacent claims, and no separate entity endpoint for 'position' is named.",
        ["cand-4452", "cand-0209"],
    )

    accession = statement_by_id["st-chp2-secii-l80-89-urban-became-pope"]
    accession["object_candidate_id"] = "cand-4223"
    set_relation(
        accession,
        True,
        "The source reports Urban VIII's accession to the papal office by this point in the narrative; preserve the relative timing and distinguish the office from the person.",
        ["cand-0209", "cand-4223"],
    )
    pope_mention["candidate_id"] = "cand-4223"
    pope_mention["note"] = "The office Urban VIII had assumed; mapped to the Papacy candidate rather than to Urban VIII as an individual."

    candidates.append(NEW_CANDIDATE)
    segment_indices = [i for i, row in enumerate(mentions) if row["segment_id"] == SEGMENT_ID]
    if not segment_indices:
        raise SystemExit("p.39 mention rows are missing")
    insertion_candidates = [
        i for i, row in enumerate(mentions)
        if row["segment_id"] == SEGMENT_ID and int(row["start_char"]) > int(NEW_MENTION["start_char"])
    ]
    insert_at = min(insertion_candidates) if insertion_candidates else max(segment_indices) + 1
    mentions.insert(insert_at, NEW_MENTION)

    coverage_rows = [row for row in coverage if row["segment_id"] == SEGMENT_ID]
    if len(coverage_rows) != 1:
        raise SystemExit("expected one p.39 coverage row")
    coverage_note = (
        " S2 follow-up classified the universal copying-training claim as a source-attributed relation candidate; split Marcello's personal profile from the explicit claim that Pietro was especially welcome to him. "
        "The Sacchetti position-change sentence remains a non-relational transition summary because the specific offices and privileges are separately recorded; Urban VIII's accession is linked to the Papacy office candidate. "
        "Printed p.39 reads 'fables of ancient Rome and Greece' where S0 OCR reads 'sables'; the correction is retained in the affected statement qualification, with the source asset unchanged."
    )
    if coverage_note.strip() not in coverage_rows[0]["note"]:
        coverage_rows[0]["note"] = coverage_rows[0]["note"].rstrip() + coverage_note

    candidate_ids = {row["candidate_id"] for row in candidates}
    if len(candidate_ids) != len(candidates):
        raise SystemExit("candidate IDs are not unique after write preparation")
    if len({row["statement_id"] for row in statements}) != len(statements):
        raise SystemExit("statement IDs are not unique after write preparation")
    if any(source_text[int(m["start_char"]):int(m["end_char"])] != m["surface_form"] for m in mentions if m["segment_id"] == SEGMENT_ID):
        raise SystemExit("p.39 mention span audit failed")
    remaining = [
        row["statement_id"] for row in statements
        if row["segment_id"] == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    ]
    if remaining:
        raise SystemExit(f"p.39 segment still has unset relation_candidate values: {remaining}")
    for row in statements:
        if row["segment_id"] != SEGMENT_ID:
            continue
        for key in ("subject_candidate_id", "object_candidate_id"):
            if row.get(key) and row[key] not in candidate_ids:
                raise SystemExit(f"p.39 statement has missing {key}: {row['statement_id']} -> {row[key]}")
        referenced = row.get("qualifiers", {}).get("mentioned_candidate_ids", [])
        if set(referenced) - candidate_ids:
            raise SystemExit(f"p.39 statement has missing mentioned candidates: {row['statement_id']}")

    updated = {
        "book-statements.jsonl": statements,
        "entity-candidates.csv": candidates,
        "mentions.csv": mentions,
        "s2-coverage.csv": coverage,
    }
    result = {
        "mode": "apply" if args.apply else "preview",
        "source": "CHP-2 printed p.39 / normalized S0 L80-89",
        "classified_unset_ids": sorted(UNSET),
        "split_statement": NEW_STATEMENT_ID,
        "new_candidate": NEW_CANDIDATE["candidate_id"],
        "new_mention": NEW_MENTION["mention_id"],
        "corrected_office_mention": {"mention_id": pope_mention["mention_id"], "candidate_id": "cand-4223"},
        "remaining_unset": remaining,
        "counts_delta": {"statements": 1, "candidates": 1, "mentions": 1},
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
        if any(written_by_id[sid].get("qualifiers", {}).get("relation_candidate") is None for sid in UNSET | {NEW_STATEMENT_ID}):
            raise SystemExit("a p.39 relation_candidate value was not persisted")
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
