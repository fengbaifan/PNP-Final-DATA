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
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l10-18"
SEGMENT_SHA = "0a46b10c1bcb3a23d57c50b5053b86851882c588cdfd8490148a9aac1b42376f"
PREVIOUS_SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l3-8"
BACKUP_SUFFIX = ".bak-s2-chp2-secii-l10-18-20261012"
EXPECTED = {
    "book-statements.jsonl": "6caa560a8cb15854c5410d4a1e50ab925729413dec3e12484ddd7522d84a25db",
    "entity-candidates.csv": "4a6a5d876877eaf099ca9d83c3ba522231fe9e1f67218b731e1d945ac65d24e4",
    "mentions.csv": "47af4974c670d2dc4ef4379b1ec7e33a36190a1525febc885a63e405b53c5f41",
    "s2-coverage.csv": "c59e4b3e4ab62b3205f66c7392e4cd3e6e4fbb6d16b743cc75d4654ecb60e34e",
}
UNSET = {
    "st-chp2-sec-ii-l10-18-duty-to-continue-beautification",
    "st-chp2-sec-ii-l10-18-feudal-families-social-role",
    "st-chp2-sec-ii-l10-18-gregory-xiii-building-charity-quotation",
    "st-chp2-sec-ii-l10-18-important-posts-sold",
    "st-chp2-sec-ii-l10-18-papal-states-wealth-at-accession",
    "st-chp2-sec-ii-l10-18-patronage-scope-fragment",
    "st-chp2-sec-ii-l10-18-rome-beautification-momentum",
    "st-chp2-sec-ii-l10-18-rome-self-supporting-description",
    "st-chp2-sec-ii-l10-18-urban-anticipated-benefits",
    "st-chp2-sec-ii-l10-18-urban-criticism-of-predecessor-spending",
    "st-chp2-sec-ii-l10-18-urban-desire-to-stop-building",
    "st-chp2-sec-ii-l10-18-urban-followed-predecessors-example",
    "st-chp2-sec-ii-l10-18-urban-three-roles",
    "st-chp2-sec-ii-l10-18-venetian-income-estimate",
}
NEW_CANDIDATES = {
    "cand-11877": {
        "candidate_id": "cand-11877",
        "index_entry_id": "",
        "canonical_name": "Upstarts who replaced Rome’s old feudal families in government (unnamed collective)",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell’s unnamed collective for people who had taken the old families’ place in Rome’s government; membership and institutional boundaries are unspecified.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L11",
    },
    "cand-11878": {
        "candidate_id": "cand-11878",
        "index_entry_id": "",
        "canonical_name": "Urban VIII’s predecessors accused of consuming Church inheritance (unnamed subset)",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Unnamed subset of Urban VIII’s papal predecessors in a Venetian ambassador’s report of Urban’s criticism; do not infer specific popes or independently confirm the accusation.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L14",
    },
}
NEW_MENTIONS = {
    "m-chp2-secii-l3-8-0032": (PREVIOUS_SEGMENT_ID, "cand-0805", "a rich and aristocratic wife"),
    "m-chp2-secii-l10-18-0037": (SEGMENT_ID, "cand-11876", "Their"),
    "m-chp2-secii-l10-18-0038": (SEGMENT_ID, "cand-11877", "upstarts"),
    "m-chp2-secii-l10-18-0039": (SEGMENT_ID, "cand-11878", "his predecessors who have consumed the inheritance of the Church in buildings and other things of the kind"),
}
NEW_STATEMENTS = {
    "st-chp2-sec-ii-l10-18-urban-role-absolute-monarch",
    "st-chp2-sec-ii-l10-18-urban-role-head-of-family",
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


def make_mention(mention_id: str, segment_id: str, candidate_id: str, surface: str, text: str, note: str) -> dict[str, str]:
    starts = [index for index in range(len(text)) if text.startswith(surface, index)]
    if len(starts) != 1:
        raise SystemExit(f"expected one exact source anchor for {surface!r}, found {starts}")
    start = starts[0]
    return {
        "mention_id": mention_id,
        "segment_id": segment_id,
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

    segments = {row["segment_id"]: row for row in read_jsonl(TABLES / "segments.jsonl")}
    if segments.get(SEGMENT_ID, {}).get("sha256") != SEGMENT_SHA or segments[SEGMENT_ID].get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected p.32 source segment fingerprint changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    previous_text = "\n".join(source_lines[2:8])
    source_text = "\n".join(source_lines[9:18])
    if "Anna Colonna" not in source_text or "Their only purpose" not in source_text or "absolute monarch" not in source_text:
        raise SystemExit("protected p.32 clauses changed; re-review before applying")

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
        raise SystemExit(f"unexpected p.32 unset statement set: {sorted(unset)}")
    if set(NEW_CANDIDATES) & set(candidate_by_id) or set(NEW_MENTIONS) & set(mention_by_id) or NEW_STATEMENTS & set(statement_by_id):
        raise SystemExit("a planned candidate, mention, or split statement ID already exists")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 11876:
        raise SystemExit("candidate ID sequence changed; refusing to allocate cand-11877/11878")
    if "term" not in {row["suggested_type"] for row in candidates}:
        raise SystemExit("candidate taxonomy no longer contains the source-defined collective type")

    for mention in mentions:
        if mention["segment_id"] == PREVIOUS_SEGMENT_ID:
            text = previous_text
        elif mention["segment_id"] == SEGMENT_ID:
            text = source_text
        else:
            continue
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if text[start:end] != mention["surface_form"]:
            raise SystemExit(f"existing mention span changed or is invalid: {mention['mention_id']}")

    # Resolve p.31's prospective wife from the immediately following p.32 sentence.
    marriage_id = "st-chp2-sec-ii-l3-8-taddeo-fortunes"
    marriage = statement_by_id[marriage_id]
    if marriage.get("segment_id") != PREVIOUS_SEGMENT_ID or marriage.get("subject_candidate_id") != "cand-0239":
        raise SystemExit("expected p.31 Taddeo marriage-prospect statement changed")
    if marriage.get("claim") != "Haskell says Taddeo had the prospect of a rich and aristocratic wife.":
        raise SystemExit("the p.31 statement-level claim cleanup is not in the expected state")
    marriage.pop("claim", None)
    marriage["object_candidate_id"] = "cand-0805"
    marriage["predicate"] = "prospect_of_marriage_to_reported"
    marriage["qualifiers"]["claim"] = "Haskell says Taddeo had the prospect of a rich and aristocratic wife."
    marriage["qualifiers"]["qualification"] = "This is a prospective marriage, not a completed marriage. The immediately following sentence on printed p.32 names Anna Colonna as the bride chosen for Don Taddeo; retain the earlier prospective wording separately from the later selection."
    set_relation(
        marriage,
        True,
        "The unnamed wife in the p.31 prospect resolves to Anna Colonna in the immediately following sentence, which names her as Don Taddeo’s chosen bride. This row records the earlier prospect; the p.32 row records the selection event.",
        mentioned=["cand-0239", "cand-0805"],
    )
    mentions.append(make_mention(
        "m-chp2-secii-l3-8-0032", PREVIOUS_SEGMENT_ID, "cand-0805", "a rich and aristocratic wife", previous_text,
        "Resolved to Anna Colonna by the immediately following p.32 sentence naming her as Taddeo’s chosen bride; the p.31 phrase remains prospective.",
    ))

    candidates.extend(NEW_CANDIDATES.values())
    mentions.append(make_mention(
        "m-chp2-secii-l10-18-0037", SEGMENT_ID, "cand-11876", "Their", source_text,
        "Anaphoric reference to the great feudal clans described at the end of the preceding segment.",
    ))
    mentions.append(make_mention(
        "m-chp2-secii-l10-18-0038", SEGMENT_ID, "cand-11877", "upstarts", source_text,
        "Unnamed collective described as having replaced the old feudal families in Rome’s government.",
    ))
    mentions.append(make_mention(
        "m-chp2-secii-l10-18-0039", SEGMENT_ID, "cand-11878",
        "his predecessors who have consumed the inheritance of the Church in buildings and other things of the kind",
        source_text,
        "The unnamed subset accused in the ambassador-mediated report of Urban VIII’s criticism; no individual pope is inferred.",
    ))

    false_decisions = {
        "st-chp2-sec-ii-l10-18-duty-to-continue-beautification": "This is Haskell’s rhetorical question about continuing Rome’s beautification, not a relation between entities or an objective duty claim.",
        "st-chp2-sec-ii-l10-18-gregory-xiii-building-charity-quotation": "This mediated quotation preserves Gregory XIII’s general normative rationale for building. It names no particular building, patronage transaction, or recipient entity; retain it as an attributed argument, not a formal relation.",
        "st-chp2-sec-ii-l10-18-papal-states-wealth-at-accession": "This is a relative description of the Papal States’ wealth at Urban VIII’s accession, not a relation between entities.",
        "st-chp2-sec-ii-l10-18-patronage-scope-fragment": "This incomplete authorial interpretation continues in the next segment as a claim about tensions among Urban VIII’s roles; it does not assert a relation between distinct entities.",
        "st-chp2-sec-ii-l10-18-rome-beautification-momentum": "This is Haskell’s interpretation of Rome’s beautification as a process with its own momentum, not an entity relation.",
        "st-chp2-sec-ii-l10-18-urban-anticipated-benefits": "This is Haskell’s interpretation of Urban VIII’s anticipated motives and benefits from unnamed planned works, not a source-stated relation to an identified work or beneficiary.",
        "st-chp2-sec-ii-l10-18-urban-desire-to-stop-building": "This is Haskell’s conjecture about Urban VIII’s will and desire to stop construction, not a direct relation claim; the ambassador remains unidentified.",
        "st-chp2-sec-ii-l10-18-important-posts-sold": "This describes a generalized office-sale practice without identifying any particular posts, sellers, buyers, or transaction. Retain the claim for later source-specific follow-up; it is not a formal relation candidate in its current form.",
    }
    for statement_id, note in false_decisions.items():
        set_relation(statement_by_id[statement_id], False, note)

    social_role = statement_by_id["st-chp2-sec-ii-l10-18-feudal-families-social-role"]
    social_role.update({"subject_candidate_id": "cand-11876", "object_candidate_id": "cand-11877", "predicate": "provided_aristocratic_wives_for_reported"})
    set_relation(
        social_role,
        True,
        "Haskell characterizes the displaced old feudal families as serving to provide aristocratic wives for the unnamed people who replaced them in Rome’s government. Preserve this as a broad social-role claim; do not infer that every marriage followed it.",
        mentioned=["cand-11876", "cand-11877"],
    )

    sale = statement_by_id["st-chp2-sec-ii-l10-18-important-posts-sold"]
    sale.update({"subject_candidate_id": None, "object_candidate_id": None, "predicate": "sold_to_highest_bidder_in_papal_office_practice_reported"})
    set_relation(
        sale,
        True,
        "Haskell explicitly says important posts could be and were sold to the highest bidder at large profits. Keep the pattern-level transaction as a relation candidate without inferring the offices, sellers, or buyers.",
        open_endpoint_reason="No particular posts, seller, or purchaser is named; this general practice remains pending source-specific endpoints.",
    )

    self_support = statement_by_id["st-chp2-sec-ii-l10-18-rome-self-supporting-description"]
    self_support.update({"subject_candidate_id": "cand-4217", "object_candidate_id": "cand-3126", "predicate": "reported_ambassadorial_characterization"})
    set_relation(
        self_support,
        True,
        "The unnamed Venetian ambassadors are explicitly credited with describing Rome as almost self-supporting; preserve the attribution and the qualifier ‘almost’.",
        mentioned=["cand-4217", "cand-3126"],
    )

    criticism = statement_by_id["st-chp2-sec-ii-l10-18-urban-criticism-of-predecessor-spending"]
    criticism.update({"subject_candidate_id": "cand-3104", "object_candidate_id": "cand-11878", "predicate": "criticized_predecessors_reported"})
    set_relation(
        criticism,
        True,
        "An unnamed Venetian ambassador reports Urban VIII blaming a subset of his predecessors for spending Church inheritance on buildings and similar things. Preserve the nested attribution and do not verify the accusation.",
        mentioned=["cand-3104", "cand-11878"],
    )

    followed = statement_by_id["st-chp2-sec-ii-l10-18-urban-followed-predecessors-example"]
    followed.update({"subject_candidate_id": "cand-3104", "object_candidate_id": "cand-11878", "predicate": "followed_predecessors_building_example_reported"})
    set_relation(
        followed,
        True,
        "Haskell says Urban VIII soon followed his predecessors’ building example on a vast scale. Preserve the author’s characterization and do not infer which predecessor or specific work supplied the example.",
        mentioned=["cand-3104", "cand-11878"],
    )

    income = statement_by_id["st-chp2-sec-ii-l10-18-venetian-income-estimate"]
    income.update({"subject_candidate_id": "cand-4217", "object_candidate_id": "cand-1831", "predicate": "estimated_annual_income_of_reported"})
    set_relation(
        income,
        True,
        "The Venetian ambassadors are explicitly credited with estimating the Papal States’ annual income; retain it as an attributed estimate, not a verified budget figure.",
        mentioned=["cand-4217", "cand-1831"],
    )

    roles_id = "st-chp2-sec-ii-l10-18-urban-three-roles"
    roles = statement_by_id[roles_id]
    role_two = copy.deepcopy(roles)
    role_three = copy.deepcopy(roles)
    roles.update({
        "subject_candidate_id": "cand-3104",
        "object_candidate_id": "cand-4219",
        "predicate": "spiritual_director_of",
        "original_quote": "He was the spiritual director of the Catholic world whose centre was Rome;",
    })
    roles["qualifiers"].update({
        "claim": "Haskell presents Urban VIII as the spiritual director of the Catholic world centered on Rome.",
        "qualification": "One of three roles stated in a single source sentence; the monarch and family-head roles are recorded separately.",
    })
    set_relation(roles, True, "This is one of three explicit roles Haskell assigns to Urban VIII; the Catholic world is the stated institutional-cultural object, with Rome as its center.", mentioned=["cand-3104", "cand-4219", "cand-3126"])

    role_two.update({
        "statement_id": "st-chp2-sec-ii-l10-18-urban-role-absolute-monarch",
        "subject_candidate_id": "cand-3104",
        "object_candidate_id": "cand-1831",
        "predicate": "absolute_monarch_of",
        "original_quote": "he was the absolute monarch of one of the richest states in Italy;",
    })
    role_two["qualifiers"].update({
        "claim": "Haskell presents Urban VIII as the absolute monarch of one of the richest states in Italy.",
        "qualification": "This is one of three roles stated in a single source sentence; the state is mapped provisionally to the existing open Papal States candidate.",
    })
    set_relation(role_two, True, "This is one of three explicit roles Haskell assigns to Urban VIII; the Papal States are the provisional state referent, still awaiting S3 identity alignment.", mentioned=["cand-3104", "cand-1831"])

    role_three.update({
        "statement_id": "st-chp2-sec-ii-l10-18-urban-role-head-of-family",
        "subject_candidate_id": "cand-3104",
        "object_candidate_id": "cand-0198",
        "predicate": "head_of_family",
        "original_quote": "and he was the proud head of an ambitious family.",
    })
    role_three["qualifiers"].update({
        "claim": "Haskell presents Urban VIII as the proud head of an ambitious family.",
        "qualification": "This is one of three roles stated in a single source sentence; the family is identified elsewhere in the passage as the Barberini family.",
    })
    set_relation(role_three, True, "This is one of three explicit roles Haskell assigns to Urban VIII; the immediately contextual Barberini family is the stated family referent.", mentioned=["cand-3104", "cand-0198"])

    insert_at = statements.index(roles)
    statements[insert_at:insert_at] = [role_two, role_three]

    if len({row["statement_id"] for row in statements}) != len(statements):
        raise SystemExit("split created duplicate statement IDs")
    remaining = [
        row["statement_id"] for row in statements
        if row["segment_id"] == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    ]
    if remaining:
        raise SystemExit(f"p.32 segment still has unset values: {remaining}")
    candidate_ids = {row["candidate_id"] for row in candidates}
    referenced = set()
    for row in statements:
        if row["segment_id"] not in (SEGMENT_ID, PREVIOUS_SEGMENT_ID):
            continue
        for key in ("subject_candidate_id", "object_candidate_id"):
            if row.get(key):
                referenced.add(row[key])
        referenced.update(row.get("qualifiers", {}).get("mentioned_candidate_ids", []))
    if referenced - candidate_ids:
        raise SystemExit(f"missing p.31–32 candidate foreign keys: {sorted(referenced - candidate_ids)}")

    for mention in mentions:
        if mention["segment_id"] not in (SEGMENT_ID, PREVIOUS_SEGMENT_ID):
            continue
        text = previous_text if mention["segment_id"] == PREVIOUS_SEGMENT_ID else source_text
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if text[start:end] != mention["surface_form"]:
            raise SystemExit(f"new or existing mention anchor failed: {mention['mention_id']}")

    coverage_by_id: dict[str, list[dict[str, str]]] = {}
    for row in coverage:
        coverage_by_id.setdefault(row["segment_id"], []).append(row)
    for segment_id in (PREVIOUS_SEGMENT_ID, SEGMENT_ID):
        if len(coverage_by_id.get(segment_id, [])) != 1:
            raise SystemExit(f"expected one coverage row for {segment_id}")
    coverage_by_id[PREVIOUS_SEGMENT_ID][0]["note"] = coverage_by_id[PREVIOUS_SEGMENT_ID][0]["note"].rstrip() + (
        " Adjacent-segment resolution: p.31’s ‘a rich and aristocratic wife’ is anchored to Anna Colonna because the immediate p.32 sentence names her as the bride chosen for Taddeo. "
        "The p.31 statement retains prospective modality; p.32 separately records the selection event."
    )
    coverage_by_id[SEGMENT_ID][0]["note"] = coverage_by_id[SEGMENT_ID][0]["note"].rstrip() + (
        " S2 follow-up closed 14 previously unset statements. Haskell’s broad role for the old feudal families is linked to an unnamed upstarts collective; the general office-sale claim is retained without a formal edge because the posts, sellers, and buyers are unnamed. "
        "The ambassadors’ city description and income estimate remain explicitly attributed. Urban VIII’s three roles were split into separate links to the Catholic world, Papal States, and Barberini family. "
        "His criticism of predecessors and later imitation remain attributed claims; unnamed predecessors are kept as an open collective. Printed p.32 was visually checked against the OCR source."
    )

    updated = {
        "book-statements.jsonl": statements,
        "entity-candidates.csv": candidates,
        "mentions.csv": mentions,
        "s2-coverage.csv": coverage,
    }
    result = {
        "mode": "apply" if args.apply else "preview",
        "source": "CHP-2 printed p.32 / normalized S0 L10-18",
        "classified_unset_ids": sorted(UNSET),
        "split_role_statement_ids": sorted(NEW_STATEMENTS),
        "new_candidates": sorted(NEW_CANDIDATES),
        "new_mentions": sorted(NEW_MENTIONS),
        "p31_marriage_referent": {"statement_id": marriage_id, "object_candidate_id": "cand-0805", "relation_candidate": True},
        "remaining_unset": remaining,
        "counts_delta": {"statements": 2, "candidates": 2, "mentions": 4},
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
        if any((written_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is None for sid in UNSET | NEW_STATEMENTS):
            raise SystemExit("a p.32 relation_candidate value was not persisted")
        if written_by_id[marriage_id].get("object_candidate_id") != "cand-0805" or "claim" in written_by_id[marriage_id]:
            raise SystemExit("p.31 marriage referent or claim-field repair was not persisted")
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
