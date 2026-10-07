"""Controlled Chapter 18 S2 relation-endpoint audit.

Defaults to dry-run. Applying changes requires the reviewed source, segment,
candidate, statement-count, and open-endpoint preconditions to match.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE_NAME = "02-sources/02-Markdown/18_CHP-18Conclusion.md"
SOURCE_PATH = ROOT / SOURCE_NAME
EXPECTED_SOURCE_SHA256 = "a3d40952beead96ac48136610fa3fa15f1dcdfcd1a354ef9f2c2262343aeff14"
EXPECTED_SEGMENT_HASHES = {
    "chp-18:18_CHP-18Conclusion:l3-17": "82dcf7e4c5293e3898b5ce604330cd1b5b3237cc2b8c49592e743727880bf6da",
    "chp-18:18_CHP-18Conclusion:l19-23": "0dcce09dce75a62951299c736a8a20863cfd39be27e8ceed98773c7f5f71eee6",
}
EXPECTED_MAX_CANDIDATE = 11473
EXPECTED_STATEMENT_COUNT = 12233
EXPECTED_RELATION_COUNTS = (2313, 2294, 19)
EXPECTED_OPEN_ENDPOINTS = {
    "st-chp18-conclusion-p384-authorities-and-artists": (None, None),
    "st-chp18-conclusion-p384-artists-serving-patrons": (None, None),
    "st-chp18-conclusion-p385-culture-and-inherited-values": (None, None),
    "st-chp18-conclusion-p385-no-specific-pressure-or-doctrine": (None, None),
    "st-chp18-conclusion-p385-opportunities-and-patrons": (None, "cand-4129"),
    "st-chp18-conclusion-p385-social-collapse-and-adaptation": (None, None),
    "st-chp18-conclusion-p385-bourgeois-painting-and-parma-academy": ("cand-1838", None),
}
NEW_STATEMENT_ID = "st-chp18-conclusion-p385-bourgeois-painting-no-roots-in-italy"
NEW_QUOTE = "The ‘bourgeois’ painting of England and France had no real roots in Italy"
ACADEMY_QUOTE = "and the attempts made by bodies such as the Academy at Parma to promote a more modern and ‘enlightened’ type of art met with little success."

GROUP_ENDPOINT_TYPES = {
    "cand-10744": "term",
    "cand-10745": "term",
    "cand-4129": "term",
    "cand-10740": "term",
    "cand-10741": "term",
    "cand-10742": "term",
    "cand-1838": "institution",
    "cand-3461": "place",
    "cand-5317": "place",
    "cand-8983": "place",
}


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def encode_jsonl(rows):
    return "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)


def atomic_write(path: Path, text: str):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        f.write(text)
        temporary = Path(f.name)
    temporary.replace(path)


def relation_counts(rows):
    relations = [r for r in rows if r.get("qualifiers", {}).get("relation_candidate") is True]
    complete = sum(bool(r.get("subject_candidate_id") and r.get("object_candidate_id")) for r in relations)
    return len(relations), complete, len(relations) - complete


def require_literal(source_lines, line_start, line_end, quote, label):
    excerpt = "\n".join(source_lines[line_start - 1 : line_end])
    if quote not in excerpt:
        raise SystemExit(f"reviewed quote is not present in source lines for {label}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed changes; default is dry-run")
    parser.add_argument("--show-diff", action="store_true", help="print before/after rows in dry-run")
    args = parser.parse_args()

    candidate_path = TABLES / "entity-candidates.csv"
    mention_path = TABLES / "mentions.csv"
    statement_path = TABLES / "book-statements.jsonl"
    segment_path = TABLES / "segments.jsonl"
    if hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest() != EXPECTED_SOURCE_SHA256:
        raise SystemExit("Chapter 18 source asset changed")
    source_lines = SOURCE_PATH.read_text(encoding="utf-8-sig").splitlines()
    segment_by_id = {r["segment_id"]: r for r in read_jsonl(segment_path)}
    for segment_id, expected_hash in EXPECTED_SEGMENT_HASHES.items():
        meta = segment_by_id.get(segment_id)
        if (
            not meta
            or meta.get("source_file") != SOURCE_NAME
            or meta.get("sha256") != expected_hash
            or meta.get("asset_sha256") != EXPECTED_SOURCE_SHA256
        ):
            raise SystemExit(f"source segment manifest changed: {segment_id}")
        excerpt = "\n".join(source_lines[int(meta["line_start"]) - 1 : int(meta["line_end"])])
        if hashlib.sha256(excerpt.encode("utf-8")).hexdigest() != expected_hash:
            raise SystemExit(f"source segment hash mismatch: {segment_id}")
    require_literal(source_lines, 23, 23, NEW_QUOTE, "bourgeois painting and Italy")
    require_literal(source_lines, 23, 23, ACADEMY_QUOTE, "Parma Academy assessment")

    with candidate_path.open(encoding="utf-8-sig", newline="") as f:
        candidates = list(csv.DictReader(f))
    with mention_path.open(encoding="utf-8-sig", newline="") as f:
        mentions = list(csv.DictReader(f))
    statements = read_jsonl(statement_path)
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    statement_by_id = {r["statement_id"]: r for r in statements}
    if len(candidate_by_id) != len(candidates) or len(statement_by_id) != len(statements):
        raise SystemExit("duplicate identifiers in candidate or statement table")
    if max(int(r["candidate_id"].split("-")[-1]) for r in candidates) != EXPECTED_MAX_CANDIDATE:
        raise SystemExit("candidate sequence changed")
    if len(statements) != EXPECTED_STATEMENT_COUNT or relation_counts(statements) != EXPECTED_RELATION_COUNTS:
        raise SystemExit(f"table counts changed: statements={len(statements)}, relations={relation_counts(statements)}")

    open_ids = {
        r["statement_id"]: (r.get("subject_candidate_id"), r.get("object_candidate_id"))
        for r in statements
        if r["statement_id"].startswith("st-chp18-")
        and r.get("qualifiers", {}).get("relation_candidate") is True
        and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))
    }
    if open_ids != EXPECTED_OPEN_ENDPOINTS:
        raise SystemExit(f"Chapter 18 open endpoint set changed: {open_ids}")
    if NEW_STATEMENT_ID in statement_by_id:
        raise SystemExit("the planned split statement ID already exists")

    for candidate_id, expected_type in GROUP_ENDPOINT_TYPES.items():
        if candidate_by_id.get(candidate_id, {}).get("suggested_type") != expected_type:
            raise SystemExit(f"candidate type precondition changed: {candidate_id}")
    quote_row = statement_by_id["st-chp18-conclusion-p385-bourgeois-painting-and-parma-academy"]
    if (
        quote_row.get("subject_candidate_id") != "cand-1838"
        or NEW_QUOTE not in quote_row.get("original_quote", "")
        or ACADEMY_QUOTE not in quote_row.get("original_quote", "")
    ):
        raise SystemExit("the mixed bourgeois-painting/Parma-Academy statement changed")
    new_endpoint_mentions = {
        m["candidate_id"]
        for m in mentions
        if m.get("segment_id") == "chp-18:18_CHP-18Conclusion:l19-23"
    }
    if not {"cand-10742", "cand-3461", "cand-5317", "cand-8983", "cand-10741"} <= new_endpoint_mentions:
        raise SystemExit("one or more source mentions for the Chapter 18 split/endpoints are missing")

    before = copy.deepcopy(statement_by_id)

    group_relation_specs = {
        "st-chp18-conclusion-p384-authorities-and-artists": (
            "cand-10745",
            "cand-10744",
            "authorities_employed_leading_artists_to_project_power",
            ["cand-10733", "cand-10734", "cand-10744", "cand-10745", "cand-2719", "cand-4490"],
            "The source states a Rome/Venice authority-group to artist-group relationship. No government, office, individual official, named artist commission, or specific work is identified; retain this only as a group-level S2 candidate, not a concrete formal edge.",
        ),
        "st-chp18-conclusion-p384-artists-serving-patrons": (
            "cand-10744",
            "cand-4129",
            "artists_served_great_patrons_despite_unpromising_causes",
            ["cand-0295", "cand-0342", "cand-10744", "cand-2569", "cand-4129"],
            "The named artists exemplify Haskell's group-level claim that great artists served great patrons; the source does not map an artist to a named patron, commission, or work. This remains an S2 group candidate, not a concrete formal edge.",
        ),
        "st-chp18-conclusion-p385-culture-and-inherited-values": (
            "cand-10740",
            "cand-10741",
            "aristocracy_may_have_stifled_artistic_revolt_through_inherited_values",
            ["cand-10740", "cand-10741", "cand-10744", "cand-3461", "cand-4129"],
            "Haskell marks this as a tentative group-level social interpretation (‘may have’). It links no individual patron, artist, doctrine, or commission and is not a concrete formal edge.",
        ),
        "st-chp18-conclusion-p385-opportunities-and-patrons": (
            "cand-4129",
            "cand-10744",
            "liberal_patrons_gave_opportunities_and_encouragement_to_artists",
            ["cand-10744", "cand-3461", "cand-3462", "cand-4129"],
            "The source links opportunities and encouragement for the artist group with gratitude to liberal patrons, but names no patron/artist pair, commission, or work. Keep only this group-level S2 candidate, not a concrete formal edge.",
        ),
    }
    for statement_id, (subject_id, object_id, predicate, mentioned, qualification) in group_relation_specs.items():
        row = statement_by_id[statement_id]
        row["subject_candidate_id"] = subject_id
        row["object_candidate_id"] = object_id
        row["predicate"] = predicate
        row["qualifiers"]["mentioned_candidate_ids"] = mentioned
        row["qualifiers"]["qualification"] = qualification
        row["qualifiers"]["relation_candidate"] = True

    tentative = statement_by_id["st-chp18-conclusion-p385-culture-and-inherited-values"]
    tentative["qualifiers"]["claim"] = (
        "Haskell tentatively suggests that the traditional and upstart aristocracy of Baroque Italy may have stifled artistic revolt through inherited values."
    )

    nonrelations = {
        "st-chp18-conclusion-p385-no-specific-pressure-or-doctrine": (
            "This is Haskell's broad negative generalization about unnamed pressures, academies, and religious organizations. No specific endpoint is identified, so retain it as a source assertion."
        ),
        "st-chp18-conclusion-p385-social-collapse-and-adaptation": (
            "The claim concerns artists' adaptation to an unspecified patronage society and its collapsed foundations. The referent is not specific enough to map to the broader aristocracy candidate; retain it as a source assertion."
        ),
    }
    for statement_id, qualification in nonrelations.items():
        row = statement_by_id[statement_id]
        row["qualifiers"]["relation_candidate"] = False
        row["qualifiers"]["qualification"] = qualification
        row["qualifiers"].pop("relation_candidate_note", None)

    academy = quote_row
    academy["predicate"] = "parma_academy_attempts_to_promote_modern_enlightened_art_with_little_success"
    academy["original_quote"] = ACADEMY_QUOTE
    aq = academy["qualifiers"]
    aq["source_line_start"] = 23
    aq["source_line_end"] = 23
    aq["claim"] = "Haskell says attempts by bodies such as the Academy at Parma to promote a more modern and enlightened type of art met with little success."
    aq["qualification"] = (
        "The promoted art type is described generically and has no matching identifiable candidate; keep the Academy assessment as a source assertion. "
        "The adjacent claim about bourgeois painting and Italy is recorded separately."
    )
    aq["mentioned_candidate_ids"] = ["cand-1838"]
    aq["relation_candidate"] = False
    aq.pop("relation_candidate_note", None)

    added = copy.deepcopy(academy)
    added["statement_id"] = NEW_STATEMENT_ID
    added["subject_candidate_id"] = "cand-10742"
    added["object_candidate_id"] = "cand-3461"
    added["predicate"] = "had_no_real_roots_in_italy"
    added["original_quote"] = NEW_QUOTE
    nq = added["qualifiers"]
    nq["source_line_start"] = 23
    nq["source_line_end"] = 23
    nq["claim"] = "Haskell says bourgeois painting in England and France had no real roots in Italy."
    nq["text_layer"] = "authorial report"
    nq["qualification"] = (
        "This is Haskell's broad negative historical assessment of an artistic category, not a claim about a named school, artist, or work."
    )
    nq["relation_candidate_note"] = (
        "Negative category-to-place claim; no individual school, artist, or work is identified."
    )
    nq["mentioned_candidate_ids"] = ["cand-10742", "cand-8983", "cand-5317", "cand-3461"]
    nq["relation_candidate"] = True
    added["origin"] = "book"
    added["source_file"] = SOURCE_NAME
    statements.append(added)
    statement_by_id[NEW_STATEMENT_ID] = added

    candidate_ids = set(candidate_by_id)
    for row in statements:
        for candidate_id in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if candidate_id and candidate_id not in candidate_ids:
                raise SystemExit(f"missing statement endpoint candidate: {row['statement_id']} -> {candidate_id}")
        for candidate_id in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if candidate_id not in candidate_ids:
                raise SystemExit(f"missing mentioned candidate: {row['statement_id']} -> {candidate_id}")

    remaining = {
        row["statement_id"]
        for row in statements
        if row["statement_id"].startswith("st-chp18-")
        and row.get("qualifiers", {}).get("relation_candidate") is True
        and (not row.get("subject_candidate_id") or not row.get("object_candidate_id"))
    }
    if remaining:
        raise SystemExit(f"unexpected Chapter 18 unresolved endpoint set: {sorted(remaining)}")
    for statement_id in (*nonrelations.keys(), "st-chp18-conclusion-p385-bourgeois-painting-and-parma-academy"):
        if statement_by_id[statement_id]["qualifiers"].get("relation_candidate_note"):
            raise SystemExit(f"nonrelation retains stale relation-candidate note: {statement_id}")
    if statement_by_id[NEW_STATEMENT_ID]["qualifiers"].get("relation_candidate_note") != (
        "Negative category-to-place claim; no individual school, artist, or work is identified."
    ):
        raise SystemExit("the split painting-to-place relation note is missing or stale")
    expected_after = (2311, 2299, 12)
    if len(statements) != 12234 or relation_counts(statements) != expected_after:
        raise SystemExit(f"planned aggregate counts differ: statements={len(statements)}, relations={relation_counts(statements)}")

    print("Chapter 18 S2 relation-endpoint audit plan")
    print("open endpoint candidates: 7 -> 0; four explicit group-level relations retained as S2 candidates")
    print("two generalized assertions and the unnamed Parma art target remain assertions; split one explicit negative painting-to-place claim")
    print(f"statements: {EXPECTED_STATEMENT_COUNT} -> {len(statements)}")
    print(f"relation candidates (total/complete/open): {EXPECTED_RELATION_COUNTS} -> {relation_counts(statements)}")
    changed_ids = set(EXPECTED_OPEN_ENDPOINTS) | {NEW_STATEMENT_ID}
    for statement_id in sorted(changed_ids):
        row = statement_by_id[statement_id]
        q = row.get("qualifiers", {})
        print(f"{statement_id}: {row.get('subject_candidate_id') or '∅'} → {row.get('object_candidate_id') or '∅'}; relation={q.get('relation_candidate')}; {q.get('claim')}")
        if args.show_diff:
            if statement_id in before:
                print("  BEFORE", json.dumps(before[statement_id], ensure_ascii=False))
            print("  AFTER ", json.dumps(row, ensure_ascii=False))
    if not args.apply:
        print("DRY-RUN only; inspect this plan, then pass --apply to write.")
        return

    backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp18-s2-relation-audit-"))
    shutil.copy2(statement_path, backup_dir / statement_path.name)
    atomic_write(statement_path, encode_jsonl(statements))
    written = read_jsonl(statement_path)
    if len(written) != 12234 or relation_counts(written) != expected_after:
        raise SystemExit("post-write verification failed; recovery copy is available")
    written_ids = {row["statement_id"] for row in written}
    if NEW_STATEMENT_ID not in written_ids:
        raise SystemExit("planned bourgeois-painting statement is missing after write")
    print(f"APPLIED; recovery copy: {backup_dir}")


if __name__ == "__main__":
    main()
