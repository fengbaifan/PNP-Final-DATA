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
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l42-50"
SEGMENT_SHA = "881c992c20baf865d4fa95f527b2d34f8e7daf96b9a3bc993154d5cfa122d355"
BACKUP_SUFFIX = ".bak-s2-chp2-secii-l42-50-20261012"
EXPECTED = {
    "book-statements.jsonl": "7d6d18e8ee098c937834011d19bded0616f5d0d36eee8eb6bba9c6b54b23d76a",
    "entity-candidates.csv": "46c40b4944db9fb937549e14b53eec02b9de0ac8471140d9edb0303411a5a6b4",
    "mentions.csv": "301a1d0665e857c2884a74b8aadc9c7088bb9fc1bf2822c04a37bb1877907a85",
    "s2-coverage.csv": "835b94fc81f09eb27e369e3f5fc68f42d46f30235c3a9bc672b9b6f2bab32561",
}
UNSET = {
    "st-chp2-secii-l42-50-artistic_success_and_visibility",
    "st-chp2-secii-l42-50-ginnasi_profile",
    "st-chp2-secii-l42-50-grumblings_followed_projects",
}
NEW_STATEMENTS = {
    "st-chp2-secii-l42-50-ginnasi_profile_partisan",
    "st-chp2-secii-l42-50-ginnasi_profile_papacy_aspiration",
}
GINNASI_MENTION_ID = "m-chp2-secii-l42-50-0061"


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


def set_relation(row: dict, value: bool, note: str, *, mentioned: list[str] | None = None, open_endpoint_reason: str | None = None) -> None:
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers["relation_candidate"] = value
    qualifiers["relation_candidate_note"] = note
    if mentioned is not None:
        qualifiers["mentioned_candidate_ids"] = mentioned
    if open_endpoint_reason:
        qualifiers["open_endpoint_reason"] = open_endpoint_reason
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
        raise SystemExit("protected p.35 source segment fingerprint changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[41:50])
    if "Spanish cause" not in source_text or "elected Pope" not in source_text or "tire pillars" not in source_text:
        raise SystemExit("protected p.35 passage changed; re-review before applying")

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
        raise SystemExit(f"unexpected p.35 unset statement set: {sorted(unset)}")
    if NEW_STATEMENTS & set(statement_by_id):
        raise SystemExit("planned split statement ID already exists")
    if GINNASI_MENTION_ID not in mention_by_id:
        raise SystemExit("expected Ginnasi ‘Pope’ mention is missing")
    for cid in ("cand-1171", "cand-4234", "cand-3135", "cand-4404", "cand-4223", "cand-3104", "cand-4401", "cand-4402"):
        if cid not in candidate_by_id:
            raise SystemExit(f"required p.35 candidate is missing: {cid}")

    for mention in mentions:
        if mention["segment_id"] != SEGMENT_ID:
            continue
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if source_text[start:end] != mention["surface_form"]:
            raise SystemExit(f"existing p.35 mention span changed or is invalid: {mention['mention_id']}")

    artistic = statement_by_id["st-chp2-secii-l42-50-artistic_success_and_visibility"]
    artistic.update({"subject_candidate_id": None, "object_candidate_id": "cand-4234", "predicate": "received_contemporary_attention_reported"})
    set_relation(
        artistic,
        True,
        "Haskell calls the baldacchino an immediate success and reports that contemporaries were struck by its visual effect. Preserve this as source-attributed reception; no contemporary is named.",
        mentioned=["cand-4234", "cand-3135"],
        open_endpoint_reason="The contemporaries whose response is reported are not individually identified.",
    )

    ginnasi_id = "st-chp2-secii-l42-50-ginnasi_profile"
    ginnasi = statement_by_id[ginnasi_id]
    partisan = copy.deepcopy(ginnasi)
    aspiration = copy.deepcopy(ginnasi)
    footnote_keys = ("footnote_marker", "footnote_segment", "linked_note_statement_ids")
    footnote = {key: copy.deepcopy(ginnasi["qualifiers"][key]) for key in footnote_keys if key in ginnasi["qualifiers"]}

    ginnasi["original_quote"] = "He was by now a very old man, of few gifts"
    ginnasi["qualifiers"]["claim"] = "Haskell describes Cardinal Ginnasi as very old and of few gifts."
    ginnasi["qualifiers"]["qualification"] = "Age and ability are Haskell’s characterizations, not independently verified measures."
    for key in footnote_keys + ("political_alignment_candidate_id",):
        ginnasi["qualifiers"].pop(key, None)
    set_relation(ginnasi, False, "This is Haskell’s evaluative description of Ginnasi’s age and abilities, not a relation between entities.", mentioned=["cand-1171"])

    partisan.update({
        "statement_id": "st-chp2-secii-l42-50-ginnasi_profile_partisan",
        "subject_candidate_id": "cand-1171",
        "object_candidate_id": "cand-4404",
        "predicate": "partisan_of_spanish_cause_reported",
        "original_quote": "one of the chief partisans in Rome of the Spanish cause",
        "qualifiers": copy.deepcopy(ginnasi["qualifiers"]),
    })
    partisan["qualifiers"].update({
        "claim": "Haskell describes Cardinal Ginnasi as one of Rome’s chief partisans of the Spanish cause.",
        "qualification": "This is Haskell’s political characterization; the Spanish cause remains the source-named alignment candidate, not a formally named organization.",
        "political_alignment_candidate_id": "cand-4404",
    })
    set_relation(partisan, True, "The source explicitly characterizes Ginnasi as a chief partisan in Rome of the Spanish cause; preserve the author’s wording and the open political-alignment candidate.", mentioned=["cand-1171", "cand-4404"])

    aspiration.update({
        "statement_id": "st-chp2-secii-l42-50-ginnasi_profile_papacy_aspiration",
        "subject_candidate_id": "cand-1171",
        "object_candidate_id": "cand-4223",
        "predicate": "hoped_to_be_elected_to_papacy_reported",
        "original_quote": "who had himself hoped to be elected Pope during the recent conclave.",
        "qualifiers": copy.deepcopy(ginnasi["qualifiers"]),
    })
    aspiration["qualifiers"].update(footnote)
    aspiration["qualifiers"].update({
        "claim": "Haskell says Cardinal Ginnasi had hoped to be elected Pope during the recent conclave.",
        "qualification": "This reports an aspiration, not an election; the conclave is described only as recent in this passage.",
    })
    aspiration["qualifiers"].pop("political_alignment_candidate_id", None)
    set_relation(aspiration, True, "The source reports Ginnasi’s hope of election to the papacy; retain the distinction between aspiration and election.", mentioned=["cand-1171", "cand-4223"])
    insert_at = statements.index(ginnasi)
    statements[insert_at + 1:insert_at + 1] = [partisan, aspiration]

    pope_mention = mention_by_id[GINNASI_MENTION_ID]
    if pope_mention.get("candidate_id") != "cand-0209" or pope_mention.get("surface_form") != "Pope":
        raise SystemExit("Ginnasi ‘Pope’ mention changed; review its referent before updating")
    pope_mention["candidate_id"] = "cand-4223"
    pope_mention["note"] = "The papal office Ginnasi hoped to be elected to; mapped to the Papacy candidate rather than Urban VIII as an individual."

    grumblings = statement_by_id["st-chp2-secii-l42-50-grumblings_followed_projects"]
    grumblings.update({"subject_candidate_id": "cand-4234", "object_candidate_id": "cand-3104", "predicate": "first_of_grumblings_accompanying_urban_enterprises_reported"})
    set_relation(
        grumblings,
        True,
        "Haskell treats the bronze removal and resulting epigram as the first of the complaints that would accompany many Urban VIII enterprises. Preserve the retrospective interpretation and the cited epigram context; do not infer the later complaints or projects.",
        mentioned=["cand-4234", "cand-3104", "cand-4401", "cand-4402"],
    )

    committee = statement_by_id["st-chp2-secii-l42-50-committee_decided_altars"]
    committee_note = "The printed p.35 scan reads ‘special altars in the niches of the pillars supporting the dome.’; the OCR source has ‘spécial’, ‘tire’, and a trailing question mark."
    committee_q = committee["qualifiers"].get("qualification", "").rstrip()
    if committee_note not in committee_q:
        committee["qualifiers"]["qualification"] = (committee_q + " " + committee_note).strip()
    peter = statement_by_id["st-chp2-secii-l42-50-references_to_peter_and_papacy"]
    peter_note = "The printed p.35 scan reads ‘References to St Peter’; the OCR source joins ‘toSt’."
    peter_q = peter["qualifiers"].get("qualification", "").rstrip()
    if peter_note not in peter_q:
        peter["qualifiers"]["qualification"] = (peter_q + " " + peter_note).strip()
    pillars_mention = mention_by_id.get("m-chp2-secii-l42-50-0065")
    if pillars_mention:
        pillars_mention["note"] = "The OCR surface ‘tire pillars’ corresponds to ‘the pillars’ in the printed scan; retain the source anchor and its entity mapping."

    if len({row["statement_id"] for row in statements}) != len(statements):
        raise SystemExit("split created duplicate statement IDs")
    remaining = [
        row["statement_id"] for row in statements
        if row["segment_id"] == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    ]
    if remaining:
        raise SystemExit(f"p.35 segment still has unset values: {remaining}")
    candidate_ids = {row["candidate_id"] for row in candidates}
    referenced = set()
    for row in statements:
        if row["segment_id"] != SEGMENT_ID:
            continue
        for key in ("subject_candidate_id", "object_candidate_id"):
            if row.get(key):
                referenced.add(row[key])
        referenced.update(row.get("qualifiers", {}).get("mentioned_candidate_ids", []))
    if referenced - candidate_ids:
        raise SystemExit(f"missing p.35 candidate foreign keys: {sorted(referenced - candidate_ids)}")
    if any(source_text[int(m["start_char"]):int(m["end_char"])] != m["surface_form"] for m in mentions if m["segment_id"] == SEGMENT_ID):
        raise SystemExit("p.35 mention span audit failed")
    coverage_rows = [row for row in coverage if row["segment_id"] == SEGMENT_ID]
    if len(coverage_rows) != 1:
        raise SystemExit("expected one p.35 coverage row")
    coverage_rows[0]["note"] = coverage_rows[0]["note"].rstrip() + (
        " S2 follow-up closed three unset statements; Ginnasi’s age/ability characterization, Spanish-cause partisanship, and papal-election aspiration are separate claims. "
        "The ‘Pope’ mention in the aspiration is mapped to the Papacy office candidate rather than Urban VIII. The baldacchino’s contemporary reception and the bronze-removal complaints retain their attributed audiences and scope. "
        "Printed p.35 was checked: it reads ‘References to St Peter’, ‘special altars in the niches of the pillars supporting the dome.’; the OCR spacing, spelling, and punctuation remain in the unchanged source asset."
    )

    updated = {
        "book-statements.jsonl": statements,
        "mentions.csv": mentions,
        "s2-coverage.csv": coverage,
    }
    result = {
        "mode": "apply" if args.apply else "preview",
        "source": "CHP-2 printed p.35 / normalized S0 L42-50",
        "classified_unset_ids": sorted(UNSET),
        "split_statements": sorted(NEW_STATEMENTS),
        "corrected_mention": {"mention_id": GINNASI_MENTION_ID, "from": "cand-0209", "to": "cand-4223"},
        "remaining_unset": remaining,
        "counts_delta": {"statements": 2, "candidates": 0, "mentions": 0},
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
        if any((written_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is None for sid in UNSET | NEW_STATEMENTS):
            raise SystemExit("a p.35 relation_candidate value was not persisted")
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
        "written_hashes": {name: digest(path) for name, path in paths.items() if name in updated},
        "statement_count": len(written),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
