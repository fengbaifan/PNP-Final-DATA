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
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l3-8"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_ii.md"
SOURCE_SHA = "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9"
SEGMENT_SHA = "19d1dca3c2e6fa9afdc3423e99d0b149a6b1598fd851288c4652b9dd27f7f6c7"
BACKUP_SUFFIX = ".bak-s2-chp2-secii-l3-8-20261012"
EXPECTED = {
    "book-statements.jsonl": "e64e224e2bb899476c76b14938662cb81b9c7c2a1c95e4fee5822320c174cff6",
    "entity-candidates.csv": "5ec5a3c6b47230063fa994f5220ed53a05f2ba9a1287e63aa0e3dfb7b6e80153",
    "mentions.csv": "9b1b0b6cf70fe0c110749ad60baef0f8e6ada0b44077cfde9fece28a60cb2cfa",
    "s2-coverage.csv": "1b661937161fa3fe7a3e3722de06bf7056c68c0871cb766139bdc9cf442168b1",
}
UNSET = {
    "st-chp2-sec-ii-l3-8-election-1623",
    "st-chp2-sec-ii-l3-8-family-art-patronage",
    "st-chp2-sec-ii-l3-8-family-wealth",
    "st-chp2-sec-ii-l3-8-feudal-clans",
    "st-chp2-sec-ii-l3-8-rome-autonomy",
    "st-chp2-sec-ii-l3-8-sovereignty",
    "st-chp2-sec-ii-l3-8-taddeo-fortunes",
    "st-chp2-sec-ii-l3-8-treasury-income",
    "st-chp2-sec-ii-l3-8-urban-excess-reputation",
    "st-chp2-sec-ii-l3-8-witchcraft-plot",
}
NEW_CANDIDATE_ID = "cand-11876"
NEW_MENTIONS = {
    "m-chp2-secii-l3-8-0029": ("cand-1831", "the state"),
    "m-chp2-secii-l3-8-0030": (NEW_CANDIDATE_ID, "great feudal clans"),
    "m-chp2-secii-l3-8-0031": ("cand-4241", "papal court"),
}
NEW_STATEMENTS = {
    "st-chp2-sec-ii-l3-8-taddeo-political-posts",
    "st-chp2-sec-ii-l3-8-taddeo-wealth",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


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
    *,
    mentioned: list[str] | None = None,
    open_endpoint_reason: str | None = None,
) -> None:
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
        raise SystemExit("protected p.31 source segment fingerprint changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[2:8])
    if len(source_lines) < 8 or "onepapabile" not in source_text or "participating in. the great" not in source_text:
        raise SystemExit("expected OCR artifacts are absent; re-review source before applying this script")

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
        raise SystemExit(f"unexpected p.31 unset statement set: {sorted(unset)}")
    if NEW_CANDIDATE_ID in candidate_by_id or set(NEW_MENTIONS) & set(mention_by_id):
        raise SystemExit("planned candidate or mention ID already exists")
    if NEW_STATEMENTS & set(statement_by_id):
        raise SystemExit("planned split statement ID already exists")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 11875:
        raise SystemExit("candidate ID sequence changed; refusing to allocate cand-11876")
    if "term" not in {row["suggested_type"] for row in candidates}:
        raise SystemExit("the candidate taxonomy no longer contains the source-defined collective type")
    if candidate_by_id.get("cand-1831", {}).get("canonical_name") != "Papal states":
        raise SystemExit("expected open Papal States candidate is missing")
    if candidate_by_id.get("cand-4241", {}).get("canonical_name") != "Papal court (institutional setting in Maffeo’s account)":
        raise SystemExit("expected open Papal court candidate is missing")

    for mention in mentions:
        if mention["segment_id"] != SEGMENT_ID:
            continue
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if source_text[start:end] != mention["surface_form"]:
            raise SystemExit(f"existing mention span changed or is invalid: {mention['mention_id']}")

    new_candidate = {
        "candidate_id": NEW_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Rome’s great feudal clans (unnamed collective)",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell’s source-defined collective for the old clans said to have tyrannised Rome; the passage does not identify their membership as a complete list. Orsini and Colonna sales follow as examples, but are not assigned as the full membership of this collective.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L7",
    }
    candidates.append(new_candidate)

    for mention_id, (candidate_id, surface) in NEW_MENTIONS.items():
        starts = [index for index in range(len(source_text)) if source_text.startswith(surface, index)]
        if len(starts) != 1:
            raise SystemExit(f"expected one exact source anchor for {surface!r}, found {starts}")
        start = starts[0]
        mentions.append({
            "mention_id": mention_id,
            "segment_id": SEGMENT_ID,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(start + len(surface)),
            "note": {
                "the state": "Contextual reference to the state governed by Urban VIII; Papal States identity remains an open index candidate.",
                "great feudal clans": "Haskell’s unnamed collective actor; do not infer that the following Orsini and Colonna examples exhaust its membership.",
                "papal court": "Court receiving the wealth in Haskell’s account; mapped provisionally to the existing open institutional candidate.",
            }[surface],
        })

    false_decisions = {
        "st-chp2-sec-ii-l3-8-election-1623": "This reports Maffeo Barberini’s election, regnal identity, age, and health. It is an office/status event about Urban VIII, not a relation to a distinct identified entity; do not split Maffeo and Urban VIII into separate people.",
        "st-chp2-sec-ii-l3-8-family-wealth": "This is Haskell’s broad account of wealth, status, and the perceived desirability of family enrichment. No particular transfer or relation between identified entities is asserted in this statement.",
        "st-chp2-sec-ii-l3-8-rome-autonomy": "This reports a change in Rome’s civic status and self-government. No distinct governing entity or actor is identified as the endpoint of a binary relation.",
        "st-chp2-sec-ii-l3-8-treasury-income": "This is a general claim about how contemporaries distinguished papal treasury funds from a pope’s personal income; no particular accounting actors or transfer are identified.",
    }
    for statement_id, note in false_decisions.items():
        set_relation(statement_by_id[statement_id], False, note)

    art = statement_by_id["st-chp2-sec-ii-l3-8-family-art-patronage"]
    art.update({"subject_candidate_id": None, "object_candidate_id": "cand-3126", "predicate": "patronage_attributed_with_artistic_contribution_to_rome"})
    set_relation(
        art,
        True,
        "Haskell directly attributes some of Rome’s greatest achievements to the patronage of most of the men just named. Preserve the majority quantifier and the author’s attribution; no particular work or individual contribution is identified.",
        mentioned=["cand-3035", "cand-0186", "cand-1488", "cand-3001", "cand-0239", "cand-3126"],
        open_endpoint_reason="The antecedent is the male relations named immediately before, but Haskell says ‘most’ without identifying which members of that group; the exact patron subset is unresolved.",
    )

    clans = statement_by_id["st-chp2-sec-ii-l3-8-feudal-clans"]
    clans.update({"subject_candidate_id": NEW_CANDIDATE_ID, "object_candidate_id": "cand-4241", "predicate": "declined_unable_to_compete_with_papal_court_wealth_reported"})
    set_relation(
        clans,
        True,
        "Haskell attributes the unnamed clans’ decline partly to their estate-based incomes and inability to compete with wealth flowing to the papal court. The scanned page confirms ‘participating in the great European wars’ and ‘for a long time’; retain the OCR source quote and this correction note.",
        mentioned=[NEW_CANDIDATE_ID, "cand-4241"],
    )

    sovereignty = statement_by_id["st-chp2-sec-ii-l3-8-sovereignty"]
    sovereignty.update({"subject_candidate_id": "cand-3104", "object_candidate_id": "cand-1831", "predicate": "asserted_supreme_power_over_state_reported"})
    set_relation(
        sovereignty,
        True,
        "Haskell says Urban VIII made clear that he would hold supreme power in the state, then embeds a Venetian ambassador’s criticism of cardinals as a grandiose crown. Preserve both speech layers; map ‘the state’ provisionally to the open Papal States candidate.",
        mentioned=["cand-3104", "cand-1831"],
    )

    taddeo_id = "st-chp2-sec-ii-l3-8-taddeo-fortunes"
    taddeo = statement_by_id[taddeo_id]
    posts = copy.deepcopy(taddeo)
    wealth = copy.deepcopy(taddeo)
    quote = taddeo["original_quote"]
    posts.update({
        "statement_id": "st-chp2-sec-ii-l3-8-taddeo-political-posts",
        "subject_candidate_id": "cand-0239",
        "object_candidate_id": None,
        "predicate": "received_political_posts_from_unidentified_authority",
        "qualifiers": copy.deepcopy(taddeo["qualifiers"]),
        "original_quote": quote,
    })
    posts["qualifiers"].update({
        "claim": "Haskell says Taddeo was given important political posts.",
        "qualification": "The passive wording does not identify the grantor or name the posts.",
    })
    set_relation(posts, True, "The source explicitly reports that Taddeo was given political posts, but does not name the appointing authority or the offices.", mentioned=["cand-0239"], open_endpoint_reason="The grantor and the particular political posts are unnamed in this passage.")
    wealth.update({
        "statement_id": "st-chp2-sec-ii-l3-8-taddeo-wealth",
        "subject_candidate_id": "cand-0239",
        "object_candidate_id": None,
        "predicate": "received_wealth_from_unidentified_source",
        "qualifiers": copy.deepcopy(taddeo["qualifiers"]),
        "original_quote": quote,
    })
    wealth["qualifiers"].update({
        "claim": "Haskell says Taddeo was given great wealth.",
        "qualification": "The source does not name the giver, source, amount, or form of the wealth.",
    })
    set_relation(wealth, True, "The passive wording explicitly describes wealth being given to Taddeo, while leaving the giver, amount, and source unspecified.", mentioned=["cand-0239"], open_endpoint_reason="The giver and the wealth’s source are not named in this passage.")

    taddeo["qualifiers"]["claim"] = "Haskell says Taddeo had the prospect of a rich and aristocratic wife."
    taddeo["predicate"] = "prospect_of_aristocratic_marriage_reported"
    taddeo["qualifiers"].update({
        "qualification": "This is a prospective marriage, not a completed marriage. The following segment names Anna Colonna as the bride selected for Taddeo; this row preserves the earlier prospective wording.",
    })
    set_relation(
        taddeo,
        True,
        "The source explicitly records a marital prospect for Taddeo, not a completed marriage. The wife is unnamed in this segment; a following segment reports Anna Colonna’s selection as bride.",
        mentioned=["cand-0239"],
        open_endpoint_reason="The prospective wife is unnamed in L3-8; keep this endpoint open and preserve the later selection statement separately.",
    )
    insert_at = statements.index(taddeo)
    statements[insert_at + 1:insert_at + 1] = [posts, wealth]

    reputation = statement_by_id["st-chp2-sec-ii-l3-8-urban-excess-reputation"]
    reputation.update({"subject_candidate_id": None, "object_candidate_id": "cand-3104", "predicate": "held_to_exceed_reasonable_limits_by_unidentified_audience"})
    set_relation(
        reputation,
        True,
        "Haskell reports a judgment attributed to Urban VIII’s contemporaries and successors; this records reported opinion, not an independently established measure of excess.",
        mentioned=["cand-3104"],
        open_endpoint_reason="The contemporaries and successors who held this view are not identified in the passage.",
    )

    plot = statement_by_id["st-chp2-sec-ii-l3-8-witchcraft-plot"]
    plot.update({"subject_candidate_id": None, "object_candidate_id": "cand-3104", "predicate": "reported_attempt_to_remove"})
    set_relation(
        plot,
        True,
        "Haskell reports an alleged 1635 witchcraft plot against Urban VIII. Preserve the account as reported rather than verified; the image confirms the phrase ‘one papabile cardinal’ while the OCR source joins the words.",
        mentioned=["cand-3104"],
        open_endpoint_reason="The ambitious nephew and papabile cardinal are unnamed; do not infer an identity from the account.",
    )

    if len({row["statement_id"] for row in statements}) != len(statements):
        raise SystemExit("split created duplicate statement IDs")
    expected_remaining = [
        row["statement_id"] for row in statements
        if row["segment_id"] == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    ]
    if expected_remaining:
        raise SystemExit(f"p.31 segment still has unset values: {expected_remaining}")
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
        raise SystemExit(f"missing p.31 candidate foreign keys: {sorted(referenced - candidate_ids)}")
    coverage_rows = [row for row in coverage if row["segment_id"] == SEGMENT_ID]
    if len(coverage_rows) != 1:
        raise SystemExit("expected one p.31 coverage row")
    coverage_rows[0]["note"] = coverage_rows[0]["note"].rstrip() + (
        " S2 follow-up closed the ten previously unset statements; Taddeo’s combined sentence is split into separate claims about posts, wealth, and prospective marriage. "
        "The majority patronage claim remains open as to which men; the feudal-clan collective is a source-bounded term linked provisionally to the existing papal-court candidate. "
        "The state in Urban VIII’s power claim is linked to the open Papal States candidate. The alleged witchcraft plot and reported reputation retain their unnamed actors/audiences. "
        "Printed p.31 was checked: the scan reads ‘one papabile’, ‘self-government’, ‘participating in the great European wars’, and ‘for a long time’; the OCR source asset remains unchanged."
    )

    updated = {
        "book-statements.jsonl": statements,
        "entity-candidates.csv": candidates,
        "mentions.csv": mentions,
        "s2-coverage.csv": coverage,
    }
    result = {
        "mode": "apply" if args.apply else "preview",
        "source": "CHP-2 printed p.31 / normalized S0 L3-8",
        "classified_original_unset_ids": sorted(UNSET),
        "split_statements": sorted(NEW_STATEMENTS),
        "new_candidate": {"id": NEW_CANDIDATE_ID, "type": new_candidate["suggested_type"], "name": new_candidate["canonical_name"]},
        "new_mentions": {key: {"candidate_id": value[0], "surface_form": value[1], "span": [int(next(m["start_char"] for m in mentions if m["mention_id"] == key)), int(next(m["end_char"] for m in mentions if m["mention_id"] == key))]} for key, value in NEW_MENTIONS.items()},
        "remaining_unset": expected_remaining,
        "counts_delta": {"statements": 2, "candidates": 1, "mentions": 3},
        "source_unchanged": True,
        "coverage": {"disposition": coverage_rows[0]["disposition"], "migration_status": coverage_rows[0]["migration_status"]},
        "payload_sha256": {name: hashlib.sha256(serialize(name, rows)).hexdigest() for name, rows in updated.items()},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temps: dict[str, Path] = {}
    try:
        for name, path in paths.items():
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
            backups[name] = backup
        for name, rows in updated.items():
            path = paths[name]
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
                temp = Path(handle.name)
                handle.write(serialize(name, rows))
            temps[name] = temp
        for name, temp in temps.items():
            os.replace(temp, paths[name])
        written = read_jsonl(paths["book-statements.jsonl"])
        written_by_id = {row["statement_id"]: row for row in written}
        if any((written_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is None for sid in UNSET | NEW_STATEMENTS):
            raise SystemExit("a p.31 relation_candidate value was not persisted")
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
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
