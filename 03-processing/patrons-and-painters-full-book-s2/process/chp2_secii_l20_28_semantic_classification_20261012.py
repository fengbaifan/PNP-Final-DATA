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
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l20-28"
SEGMENT_SHA = "4efb9a12a647376ce9e3a41a32ce451a52921c8e9b9236101e6eaa6eb8298dd6"
BACKUP_SUFFIX = ".bak-s2-chp2-secii-l20-28-20261012"
EXPECTED = {
    "book-statements.jsonl": "66b10770f240165b8d3423d2df3434912dafc7a0c35981ddbed229bc01fbaf3a",
    "entity-candidates.csv": "33a1e380824ebe9abc8e4296d6d23eeed8d05d896cb493dade25e2e0e71972bd",
    "mentions.csv": "5a3bc5bcec5275375aaba0e94327a6ff93be58b2dbaa63617408d88ab6cd0a3d",
    "s2-coverage.csv": "8f110c9e4e05b2f6bd4db0a8878e065e9b2aba58e4407b5df83bb24086d94f51",
}
UNSET = {
    "st-chp2-sec-ii-l20-28-analytic-method",
    "st-chp2-sec-ii-l20-28-baroque-triumph-and-victories",
    "st-chp2-sec-ii-l20-28-france-hapsburg-rivalry",
    "st-chp2-sec-ii-l20-28-orthodox-forms-as-religious-strategy",
    "st-chp2-sec-ii-l20-28-persecution-and-indulgence",
    "st-chp2-sec-ii-l20-28-protestant-advance-and-events",
    "st-chp2-sec-ii-l20-28-role-tensions",
    "st-chp2-sec-ii-l20-28-rome-local-complexity",
}
NEW_CANDIDATES = {
    "cand-11879": {
        "candidate_id": "cand-11879",
        "index_entry_id": "",
        "canonical_name": "Reconciliation of Henri IV in 1593 (as described by Haskell)",
        "index_page_range": "",
        "suggested_type": "event",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell names this reconciliation as one of two events that had proved effective barriers to the Protestant advance; preserve the author's causal characterization and do not treat it as independently verified here.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L23",
    },
    "cand-11880": {
        "candidate_id": "cand-11880",
        "index_entry_id": "",
        "canonical_name": "Henri IV’s reconciliation and the Battle of the White Hill (victory set in Haskell’s account)",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "The source's plural anaphor ‘these overwhelming victories’ refers to the reconciliation of Henri IV in 1593 and the Battle of the White Hill in 1621. Keep the two events distinct; this candidate records only the source-defined set used in Haskell's interpretation of mature Baroque style.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L23",
    },
}
NEW_MENTIONS = {
    "m-chp2-secii-l20-28-0034": ("cand-11879", "reconciliation of Henri IV in 1593"),
    "m-chp2-secii-l20-28-0035": ("cand-11880", "these overwhelming victories"),
}
NEW_STATEMENT_ID = "st-chp2-sec-ii-l20-28-protestant-advance-battle-barrier"


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


def set_relation(row: dict, value: bool, note: str, *, mentioned: list[str] | None = None) -> None:
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers["relation_candidate"] = value
    qualifiers["relation_candidate_note"] = note
    if mentioned is not None:
        qualifiers["mentioned_candidate_ids"] = mentioned
    qualifiers.pop("open_endpoint_reason", None)


def make_mention(mention_id: str, candidate_id: str, surface: str, source_text: str, note: str) -> dict[str, str]:
    starts = [index for index in range(len(source_text)) if source_text.startswith(surface, index)]
    if len(starts) != 1:
        raise SystemExit(f"expected one exact source anchor for {surface!r}, found {starts}")
    start = starts[0]
    return {
        "mention_id": mention_id,
        "segment_id": SEGMENT_ID,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    }


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
        raise SystemExit("protected p.33 source segment fingerprint changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[19:28])
    if "reconciliation of Henri IV in 1593" not in source_text or "these overwhelming victories" not in source_text:
        raise SystemExit("protected event passage changed; re-review before applying")

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
        raise SystemExit(f"unexpected p.33 unset statement set: {sorted(unset)}")
    if set(NEW_CANDIDATES) & set(candidate_by_id) or set(NEW_MENTIONS) & set(mention_by_id) or NEW_STATEMENT_ID in statement_by_id:
        raise SystemExit("a planned candidate, mention, or statement ID already exists")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 11878:
        raise SystemExit("candidate ID sequence changed; refusing to allocate cand-11879/11880")
    if "event" not in {row["suggested_type"] for row in candidates} or "term" not in {row["suggested_type"] for row in candidates}:
        raise SystemExit("candidate taxonomy no longer contains event and term types")

    for mention in mentions:
        if mention["segment_id"] != SEGMENT_ID:
            continue
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if source_text[start:end] != mention["surface_form"]:
            raise SystemExit(f"existing p.33 mention span changed or is invalid: {mention['mention_id']}")

    candidates.extend(NEW_CANDIDATES.values())
    mentions.extend([
        make_mention(
            "m-chp2-secii-l20-28-0034", "cand-11879", "reconciliation of Henri IV in 1593", source_text,
            "Source-named political reconciliation, distinguished from Henri IV as a person and from the Battle of the White Hill.",
        ),
        make_mention(
            "m-chp2-secii-l20-28-0035", "cand-11880", "these overwhelming victories", source_text,
            "Anaphoric set comprising the previously named reconciliation and Battle; retain both events as distinct.",
        ),
    ])

    false_decisions = {
        "st-chp2-sec-ii-l20-28-analytic-method": "This is Haskell’s qualified methodological recommendation about how to interpret Urban VIII’s patronage; it is not a relation between entities.",
        "st-chp2-sec-ii-l20-28-orthodox-forms-as-religious-strategy": "This reports an unattributed belief about the possible effect of outward religious forms. No holder, actor, or particular practice is identified; retain it as an attributed belief rather than a formal relation.",
        "st-chp2-sec-ii-l20-28-persecution-and-indulgence": "This is Haskell’s generalized description of a reaction, with no identified actor or particular episode; it is not a formal relation candidate.",
        "st-chp2-sec-ii-l20-28-role-tensions": "This continues Haskell’s interpretation that Urban VIII’s roles overlapped and created tensions affecting patronage. It is an authorial synthesis of roles, not a relation between separately identified entities.",
        "st-chp2-sec-ii-l20-28-rome-local-complexity": "This is a transition describing the situation within Rome as complex; it does not assert an entity relation.",
    }
    for statement_id, note in false_decisions.items():
        set_relation(statement_by_id[statement_id], False, note)

    rivalry = statement_by_id["st-chp2-sec-ii-l20-28-france-hapsburg-rivalry"]
    rivalry.update({"subject_candidate_id": "cand-4221", "object_candidate_id": "cand-4222", "predicate": "traditional_enmity_with_reported"})
    set_relation(
        rivalry,
        True,
        "Haskell identifies traditional enmity between France and the Hapsburg Empire; the same sentence says their maneuvering threatened Italy’s peace and Papal States’ security. Preserve the source spelling and broad political characterization.",
        mentioned=["cand-4221", "cand-4222", "cand-3114", "cand-1831"],
    )

    baroque = statement_by_id["st-chp2-sec-ii-l20-28-baroque-triumph-and-victories"]
    baroque.update({"subject_candidate_id": "cand-3993", "object_candidate_id": "cand-11880", "predicate": "reflected_impact_of_reported"})
    baroque["qualifiers"]["claim"] = "Haskell infers that the triumphal quality noted in mature Baroque style reflected the combined impact of the reconciliation of Henri IV and the Battle of the White Hill."
    set_relation(
        baroque,
        True,
        "Haskell’s ‘no doubt’ marks this as his interpretation. The plural referent is preserved as a source-defined set containing two distinct events, not collapsed into one event.",
        mentioned=["cand-3993", "cand-11880", "cand-11879", "cand-2810"],
    )

    barriers_id = "st-chp2-sec-ii-l20-28-protestant-advance-and-events"
    barriers = statement_by_id[barriers_id]
    battle_barrier = copy.deepcopy(barriers)
    barriers.update({"subject_candidate_id": "cand-11879", "object_candidate_id": "cand-4225", "predicate": "proved_effective_barrier_to_reported"})
    barriers["qualifiers"]["claim"] = "Haskell says the reconciliation of Henri IV in 1593 proved an effective barrier to the Protestant advance."
    barriers["qualifiers"]["qualification"] = "The source states that this and the Battle of the White Hill in 1621 proved effective barriers; the printed dates and causal characterization are not independently verified here."
    set_relation(
        barriers,
        True,
        "The source explicitly names Henri IV’s 1593 reconciliation as one of two effective barriers to the Protestant advance; preserve Haskell’s historical interpretation.",
        mentioned=["cand-11879", "cand-1295", "cand-2810", "cand-4225"],
    )
    battle_barrier.update({
        "statement_id": NEW_STATEMENT_ID,
        "subject_candidate_id": "cand-2810",
        "object_candidate_id": "cand-4225",
        "predicate": "proved_effective_barrier_to_reported",
        "qualifiers": copy.deepcopy(barriers["qualifiers"]),
    })
    battle_barrier["qualifiers"]["claim"] = "Haskell says the Battle of the White Hill in 1621 proved an effective barrier to the Protestant advance."
    set_relation(
        battle_barrier,
        True,
        "The source explicitly names the Battle of the White Hill in 1621 as one of two effective barriers to the Protestant advance; preserve Haskell’s historical interpretation.",
        mentioned=["cand-11879", "cand-1295", "cand-2810", "cand-4225"],
    )
    insert_at = statements.index(barriers)
    statements.insert(insert_at + 1, battle_barrier)

    if len({row["statement_id"] for row in statements}) != len(statements):
        raise SystemExit("split created duplicate statement IDs")
    remaining = [
        row["statement_id"] for row in statements
        if row["segment_id"] == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    ]
    if remaining:
        raise SystemExit(f"p.33 segment still has unset values: {remaining}")
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
        raise SystemExit(f"missing p.33 candidate foreign keys: {sorted(referenced - candidate_ids)}")
    if any(source_text[int(m["start_char"]):int(m["end_char"])] != m["surface_form"] for m in mentions if m["segment_id"] == SEGMENT_ID):
        raise SystemExit("p.33 mention span audit failed")
    coverage_rows = [row for row in coverage if row["segment_id"] == SEGMENT_ID]
    if len(coverage_rows) != 1:
        raise SystemExit("expected one p.33 coverage row")
    coverage_rows[0]["note"] = coverage_rows[0]["note"].rstrip() + (
        " S2 follow-up closed eight previously unset statements. France–Hapsburg enmity is anchored between the two named political candidates; its reported effects on Italy and the Papal States remain in the same source-qualified claim. "
        "The 1593 reconciliation and 1621 Battle of the White Hill are separate event candidates and separate barriers to the Protestant advance; Haskell’s Baroque interpretation points to their source-defined combined set. "
        "Methodological, transition, generalized belief, and generalized reaction statements remain non-relational. The printed p.33 scan confirms ‘the’ where the OCR reads ‘tire’; the source asset remains unchanged."
    )

    updated = {
        "book-statements.jsonl": statements,
        "entity-candidates.csv": candidates,
        "mentions.csv": mentions,
        "s2-coverage.csv": coverage,
    }
    result = {
        "mode": "apply" if args.apply else "preview",
        "source": "CHP-2 printed p.33 / normalized S0 L20-28",
        "classified_unset_ids": sorted(UNSET),
        "new_statement": NEW_STATEMENT_ID,
        "new_candidates": sorted(NEW_CANDIDATES),
        "new_mentions": sorted(NEW_MENTIONS),
        "remaining_unset": remaining,
        "counts_delta": {"statements": 1, "candidates": 2, "mentions": 2},
        "source_unchanged": True,
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
        if any((written_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is None for sid in UNSET | {NEW_STATEMENT_ID}):
            raise SystemExit("a p.33 relation_candidate value was not persisted")
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
