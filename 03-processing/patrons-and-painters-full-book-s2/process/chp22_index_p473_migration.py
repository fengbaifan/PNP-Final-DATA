#!/usr/bin/env python3
"""Classify p.473 index entries and reconcile their explicit body relation leads."""

import argparse
import csv
import hashlib
import io
import json
import os
import re
import shutil
import tempfile
from collections import Counter
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
MARKER_SEGMENT = "chp-22:22_CHP-22Index:l3407-3408"
LEFT_SEGMENT = "chp-22:22_CHP-22Index:l3410-3463"
RIGHT_SEGMENT = "chp-22:22_CHP-22Index:l3465-3515"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p473-l3407-3515-20261007-retry1"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv": "19a9e5db94a3da83c673a7fa03b003ed501317de161e4664ca572b0f0d6d5e21",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/08_CHP-8_sec_ii.md": "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    "02-sources/02-Markdown/10_CHP-10_intro.md": "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
    "02-sources/02-Markdown/13_CHP-13_intro.md": "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8",
    "04-knowledge/tables/entity-candidates.csv": "44dcd85574a82b34d3bccd4adff61e56b02307488f8648393c78bb1b147ba14e",
    "04-knowledge/tables/s2-coverage.csv": "8c3c15812036ab69f26b632e7889dd376b6637d9c1c40470e8103247737633df",
    "04-knowledge/tables/book-statements.jsonl": "2e00f3324f1a12fac107fe10759da39035837a4bd1a08d21df26d7030598e700",
    "04-knowledge/tables/mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
}

EXPECTED_SEGMENT_HASHES = {
    MARKER_SEGMENT: "83752c34bb18db65f03793c6b843410dfbc8131010cd4ce02243658986d3e3c0",
    LEFT_SEGMENT: "f24f5976820b98b676ec16f16273ef9dcf23a6f12240dfd41cd83e086213cce5",
    RIGHT_SEGMENT: "287efd6d5d1727f59c40aea3105c9dd13641de1911698bf33fb1512a04082a3a",
}

PENDING_BY_ENTRY = {
    "UVWXYZ.csv#101": (
        "Index subentry says only 'collection' below Vianello; it gives no collection title or boundary. "
        "The taxonomy has no collection/group type, so the type remains pending."
    ),
    "UVWXYZ.csv#185": (
        "The index groups medals and gems as a body of objects without identifying individual objects or a "
        "bounded collection. The taxonomy has no general object or collection type, so the type remains pending."
    ),
    "UVWXYZ.csv#186": (
        "The index groups paintings and caricatures under Zanetti without naming individual works or defining a "
        "bounded corpus. Retain the grouped oeuvre as type-pending rather than treating it as one work."
    ),
    "UVWXYZ.csv#187": (
        "The index identifies a print collection, not a single work; the taxonomy has no collection type. "
        "Retain the type as pending."
    ),
}

TYPE_BY_ENTRY = {
    f"UVWXYZ.csv#{index}": "person"
    for index in range(100, 191)
    if index not in {101, 124, 185, 186, 187}
}
for index, entity_type in {
    102: "archive",
    105: "place",
    107: "archive",
    108: "place",
    114: "archive",
    115: "work",
    116: "institution",
    120: "work",
    121: "work",
    130: "work",
    136: "archive",
    138: "term",
    143: "archive",
    147: "event",
    148: "place",
    149: "family",
    150: "place",
    159: "place",
    162: "archive",
    165: "archive",
    169: "family",
    172: "work",
    173: "work",
    174: "event",
    182: "archive",
    183: "archive",
    188: "event",
    189: "procedure",
    190: "work",
}.items():
    TYPE_BY_ENTRY[f"UVWXYZ.csv#{index}"] = entity_type

PREEXISTING_TYPES = {"UVWXYZ.csv#135": "person"}

DETAIL_UPDATES = {
    "cand-2778": (
        "The Aeneid is the literary text named as the theme for Buonaccorsi palace paintings; classify the text "
        "as archive and keep the paintings as separate work contexts."
    ),
    "cand-2779": (
        "The index says only 'portrait of' Virgil at p.201; classify the referent as a work while leaving the "
        "specific portrait identity and version unresolved for S3."
    ),
    "cand-2784": (
        "The index names Visentini engravings after Canaletto's Grand Canal paintings; classify the engravings "
        "as work candidates, distinct from the underlying Canaletto paintings."
    ),
    "cand-2785": (
        "The Palladian overdoors are architectural decorative works; the index does not identify the building "
        "they adorn."
    ),
    "cand-2801": (
        "The index refers broadly to late-seventeenth-century wars as an influence on art patronage; this is a "
        "historical theme, not one event."
    ),
    "cand-2809": (
        "'Work for Johann Wilhelm' is an index person-context for Adrian van der Werff. The p.283 body statements "
        "carry the explicit employment and gallery relation candidates."
    ),
    "cand-2825": (
        "The account of Querini's villa at Alticchiero is a textual account and is classified as archive; its "
        "publication identity remains unresolved."
    ),
    "cand-2835": (
        "The index names Moses striking the Rock at pp.218-219. Keep this index work candidate separate from body "
        "candidate cand-7670 until S3 identity alignment."
    ),
    "cand-2836": (
        "The index points to a work in S. Maria Maggiore, Bergamo; classify the work separately from the church "
        "place and leave body-candidate alignment to S3."
    ),
    "cand-2839": (
        "The 'and Crozat' subentry is person-context. The direct friendship evidence is recorded in body statement "
        "st-chp13-p341-crozat_friendship_with_zanetti."
    ),
    "cand-2840": (
        "The 'and Joseph Smith' subentry is person-context. P.341 body statement st-chp13-p341-zanetti_in_touch_"
        "with_smith_and_schulenburg isolates the Smith endpoint; this index lead remains separate for S3."
    ),
    "cand-2841": (
        "The 'and Marshal Schulenburg' subentry is person-context. The p.341 body relation candidate isolates "
        "Schulenburg as an endpoint; this index lead remains separate for S3."
    ),
    "cand-2842": (
        "The Regent de France subentry is person-context. The p.341 body statement records the Regent's "
        "entrustment of picture purchases to Zanetti."
    ),
    "cand-2843": (
        "The index groups Sebastiano and Marco Ricci under Zanetti. Body statements separately record Marco's "
        "friendship and Sebastiano's contact; this index lead remains separate for S3."
    ),
    "cand-2844": (
        "The intermediary subentry describes Zanetti's role, not a separate endpoint. Body statement "
        "st-chp13-p342-zanetti_intermediary_between_venice_and_europe records Haskell's summary."
    ),
    "cand-2847": (
        "The employment of Gaetano Zompini is person-context for Zanetti. The p.344 body statement records the "
        "employment claim; this index lead does not add a new relation."
    ),
    "cand-2851": (
        "The subentry denotes Zanetti's purchase of Lord Arundel's Parmigianino drawings. The purchase event "
        "remains distinct from the drawings and is aligned to body evidence at S3."
    ),
    "cand-2852": (
        "The rediscovery of the colour-woodcut process is classified as a procedure; body statement "
        "st-chp13-p343-zanetti_rediscovered_chiaroscuro_woodcut_process records the source claim."
    ),
    "cand-2853": (
        "The woodcuts from Parmigianino drawings are a grouped work candidate; individual sheets are not titled "
        "in the index entry."
    ),
}

LOCATOR_CORRECTION = {
    "candidate_id": "cand-2838",
    "field": "index_page_range",
    "before": "266, 284, 293n, 300, 303, 306, 320, 328, 337, 341, 342, 343, 344, 361, 371, 407, 408",
    "after": "266, 284, 293n, 300, 303, 306, 320, 328, 337, 341, 342, 343, 344, 345, 346, 361, 371, 407, 408",
    "detail": (
        "The printed p.473 main entry gives 341-6; the candidate locator omitted 345 and 346. Candidate follows "
        "the printed inclusive range; S0 and UVWXYZ.csv remain unchanged."
    ),
}

RELATION_EXPECTATIONS = {
    "st-chp10-p283-werff-paintings-entered-gallery": (
        "cand-2808", "cand-1325", "many_van_der_werff_paintings_entered_wilhelms_gallery"
    ),
    "st-chp8-p218-zanchi-canvas-accepted": (
        "cand-2834", "cand-7670", "painting_execution_and_acceptance"
    ),
    "st-chp13-p341-arundel_drawings_influenced_zanettis_taste": (
        "cand-10066", "cand-2838", "were_to_exert_great_influence_on_zanettis_taste"
    ),
    "st-chp13-p342-older_works_acquired_abroad_were_influential": (
        "cand-10086", "cand-2838", "some_older_works_acquired_in_france_and_england_were_significant_and_influential"
    ),
    "st-chp13-p342-zanetti_brought_medals_and_gems_from_european_cities": (
        "cand-2838", "cand-2848", "brought_medals_and_gems_back_from_london_paris_rotterdam_and_vienna"
    ),
    "st-chp13-p342-zanetti_had_large_print_collection": (
        "cand-2838", "cand-2850", "had_a_large_collection_of_prints"
    ),
    "st-chp13-p342-zanetti_owned_brand_and_dietrich_pictures": (
        "cand-2838", "cand-10085", "owned_pictures_by_brand_and_dietrich"
    ),
    "st-chp13-p342-zanetti_owned_carriera_pastels_and_miniatures": (
        "cand-2838", "cand-10089", "owned_pastels_and_miniatures_by_rosalba_carriera"
    ),
    "st-chp13-p342-zanetti_owned_three_sebastiano_history_paintings": (
        "cand-2838", "cand-10087", "owned_three_history_paintings_by_sebastiano"
    ),
    "st-chp13-p343-zanetti_rediscovered_chiaroscuro_woodcut_process": (
        "cand-2838", "cand-2852", "considered_rediscovery_of_multicolour_chiaroscuro_woodcuts_his_most_important_achievement"
    ),
    "st-chp13-p343-zanetti_revived_technique_and_made_about_fifty_cuts": (
        "cand-2838", "cand-2853", "revived_technique_in_london_and_made_about_fifty_cuts"
    ),
    "st-chp13-p341-zanetti_in_touch_with_smith_and_schulenburg": (
        "cand-2838", "cand-10073", "was_in_touch_with_the_leading_foreign_collectors_smith_and_schulenburg"
    ),
}

SMITH_SPLIT = {
    "statement_id": "st-chp13-p341-zanetti_in_touch_with_smith_and_schulenburg",
    "new_statement_id": "st-chp13-p341-zanetti_in_touch_with_schulenburg",
    "before_object": "cand-10073",
    "before_predicate": "was_in_touch_with_the_leading_foreign_collectors_smith_and_schulenburg",
    "smith_object": "cand-2440",
    "schulenburg_object": "cand-2401",
    "mention_ids": ["cand-2838", "cand-2840", "cand-2440", "cand-2841", "cand-2401", "cand-10073"],
    "quote": "In Venice itself Zanetti was in touch with Joseph Smith and Schulenburg, the two leading foreign collectors",
}

NEW_ENDPOINT_STATEMENTS = {
    "st-chp13-p341-zanetti_friendship_with_carriera": {
        "base_statement_id": "st-chp13-p341-paris_visit_with_carriera_and_pellegrini",
        "object_candidate_id": "cand-0581",
        "predicate": "was_a_friend_of_rosalba_carriera",
        "claim": "Haskell identifies Rosalba Carriera as Zanetti's friend while describing their concurrent stay in Paris.",
        "qualification": (
            "The source explicitly identifies the friendship and also reports their concurrent Paris stay; it does "
            "not specify the relationship's duration."
        ),
        "mentioned_candidate_ids": ["cand-2838", "cand-0581", "cand-1862", "cand-10075"],
        "source_line": 92,
    },
    "st-chp13-p341-zanetti_contact_with_sebastiano_ricci": {
        "base_statement_id": "st-chp13-p341-zanetti_contact_with_leading_artists",
        "object_candidate_id": "cand-2154",
        "predicate": "was_in_contact_with_sebastiano_ricci",
        "claim": "Haskell says Zanetti was in contact with Sebastiano Ricci among the leading artists.",
        "qualification": (
            "The source characterizes the contact without specifying collaboration, patronage, or its duration."
        ),
        "mentioned_candidate_ids": ["cand-2838", "cand-2154", "cand-2149", "cand-0581", "cand-10063", "cand-2843"],
        "source_line": 91,
    },
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    return raw.startswith(b"\xef\xbb\xbf"), "\r\n" if "\r\n" in text else "\n", list(csv.DictReader(io.StringIO(text, newline="")))


def write_csv(path, rows, bom, line_ending):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator=line_ending)
    writer.writeheader()
    writer.writerows(rows)
    payload = output.getvalue().encode("utf-8")
    if bom:
        payload = b"\xef\xbb\xbf" + payload
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
    os.replace(temporary, path)


def read_jsonl(path):
    raw = path.read_bytes()
    return raw.startswith(b"\xef\xbb\xbf"), raw.decode("utf-8-sig").splitlines(keepends=True)


def write_jsonl(path, lines, bom):
    payload = "".join(lines).encode("utf-8")
    if bom:
        payload = b"\xef\xbb\xbf" + payload
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
    os.replace(temporary, path)


def serialize_jsonl(row, newline):
    return json.dumps(row, ensure_ascii=False, separators=(",", ":")) + newline


def make_endpoint_statement(base, statement_id, object_candidate_id, predicate, claim, qualification, mention_ids, source_line):
    row = deepcopy(base)
    row["statement_id"] = statement_id
    row["object_candidate_id"] = object_candidate_id
    row["predicate"] = predicate
    qualifiers = row["qualifiers"]
    qualifiers["source_line_start"] = source_line
    qualifiers["source_line_end"] = source_line
    qualifiers["claim"] = claim
    qualifiers["qualification"] = qualification
    qualifiers["mentioned_candidate_ids"] = mention_ids
    qualifiers["relation_candidate"] = True
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write the guarded migration; default is dry-run.")
    args = parser.parse_args()

    for relative, expected in EXPECTED_HASHES.items():
        path = ROOT / relative
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"preflight hash mismatch: {relative}")

    source_path = ROOT / "02-sources/02-Markdown/22_CHP-22Index.md"
    manifest = [
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    segment_by_id = {row["segment_id"]: row for row in manifest}
    expected_ranges = {
        MARKER_SEGMENT: (3407, 3408),
        LEFT_SEGMENT: (3410, 3463),
        RIGHT_SEGMENT: (3465, 3515),
    }
    source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
    for segment_id, expected_hash in EXPECTED_SEGMENT_HASHES.items():
        segment = segment_by_id.get(segment_id)
        if not segment or segment.get("sha256") != expected_hash:
            raise SystemExit(f"segment manifest changed: {segment_id}")
        if segment.get("source_file") != "02-sources/02-Markdown/22_CHP-22Index.md":
            raise SystemExit(f"unexpected S0 source: {segment_id}")
        if (segment.get("line_start"), segment.get("line_end")) != expected_ranges[segment_id]:
            raise SystemExit(f"unexpected S0 line range: {segment_id}")
        text = "\n".join(source_lines[segment["line_start"] - 1 : segment["line_end"]])
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != expected_hash:
            raise SystemExit(f"segment source text changed: {segment_id}")

    candidate_path = TABLES / "entity-candidates.csv"
    coverage_path = TABLES / "s2-coverage.csv"
    statement_path = TABLES / "book-statements.jsonl"
    candidate_bom, candidate_eol, candidates = read_csv(candidate_path)
    coverage_bom, coverage_eol, coverage = read_csv(coverage_path)
    statement_bom, statement_lines = read_jsonl(statement_path)
    candidate_by_entry = {row["index_entry_id"]: row for row in candidates if row["index_entry_id"]}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    p473_rows_before = [
        row for row in candidates
        if re.fullmatch(r"UVWXYZ\.csv#(1[0-8][0-9]|190)", row["index_entry_id"] or "")
    ]
    p473_open_untyped_before = sum(
        row["status"] == "open" and not row["suggested_type"] for row in p473_rows_before
    )
    index_untyped_before = sum(
        bool(row["index_entry_id"]) and row["status"] == "open" and not row["suggested_type"]
        for row in candidates
    )

    if len(TYPE_BY_ENTRY) != 86 or len(PENDING_BY_ENTRY) != 4:
        raise SystemExit("the p.473 classification map is incomplete")
    page_entries = {
        f"UVWXYZ.csv#{index}"
        for index in range(100, 191)
    }
    if len(page_entries) != 91 or page_entries - set(candidate_by_entry):
        raise SystemExit("p.473 index-entry range is incomplete")
    alias = candidate_by_entry.get("UVWXYZ.csv#124")
    if not alias or alias["candidate_id"] != "cand-2930" or alias["status"] != "excluded":
        raise SystemExit("the p.473 Vivant-Denon see-under row changed")
    if alias["exclude_reason"] != "索引交叉引用：see under Non, Dominique De":
        raise SystemExit("the p.473 see-under exclusion reason changed")
    for entry_id, entity_type in TYPE_BY_ENTRY.items():
        row = candidate_by_entry.get(entry_id)
        if not row or row["status"] != "open":
            raise SystemExit(f"unexpected or missing p.473 candidate: {entry_id}")
        expected_type = PREEXISTING_TYPES.get(entry_id)
        if expected_type:
            if row["suggested_type"] != expected_type:
                raise SystemExit(f"pre-existing candidate type changed: {entry_id}")
        elif row["suggested_type"]:
            raise SystemExit(f"candidate already typed unexpectedly: {entry_id}")
    for entry_id in PENDING_BY_ENTRY:
        row = candidate_by_entry.get(entry_id)
        if not row or row["status"] != "open" or row["suggested_type"] or row["detail"]:
            raise SystemExit(f"unexpected type-pending candidate state: {entry_id}")
    for candidate_id, detail in DETAIL_UPDATES.items():
        row = candidate_by_id.get(candidate_id)
        if not row or row["detail"]:
            raise SystemExit(f"unexpected candidate detail prestate: {candidate_id}")
    locator_row = candidate_by_id.get(LOCATOR_CORRECTION["candidate_id"])
    if (
        not locator_row
        or locator_row[LOCATOR_CORRECTION["field"]] != LOCATOR_CORRECTION["before"]
        or locator_row["detail"]
    ):
        raise SystemExit("the p.473 Zanetti locator prestate changed")

    for entry_id, entity_type in TYPE_BY_ENTRY.items():
        candidate_by_entry[entry_id]["suggested_type"] = entity_type
    for entry_id, detail in PENDING_BY_ENTRY.items():
        candidate_by_entry[entry_id]["detail"] = detail
    for candidate_id, detail in DETAIL_UPDATES.items():
        candidate_by_id[candidate_id]["detail"] = detail
    locator_row[LOCATOR_CORRECTION["field"]] = LOCATOR_CORRECTION["after"]
    locator_row["detail"] = LOCATOR_CORRECTION["detail"]

    coverage_by_id = {row["segment_id"]: row for row in coverage}
    coverage_specs = (
        (MARKER_SEGMENT, "excluded", "L3407-3408"),
        (LEFT_SEGMENT, "reviewed", "L3410-3463"),
        (RIGHT_SEGMENT, "reviewed", "L3465-3515"),
    )
    segment_counts = {}
    for segment_id, disposition, line_range in coverage_specs:
        row = coverage_by_id.get(segment_id)
        if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"], row["note"]) != (
            "queued", "pending", "", "",
        ):
            raise SystemExit(f"p.473 coverage is not queued/pending: {segment_id}")

    for segment_id, entry_ids in (
        (LEFT_SEGMENT, [f"UVWXYZ.csv#{i}" for i in range(100, 147)]),
        (RIGHT_SEGMENT, [f"UVWXYZ.csv#{i}" for i in range(147, 191)]),
    ):
        counts = Counter(TYPE_BY_ENTRY[entry_id] for entry_id in entry_ids if entry_id in TYPE_BY_ENTRY)
        segment_counts[segment_id] = dict(sorted(counts.items()))

    coverage_notes = {
        MARKER_SEGMENT: (
            "no_semantic_content: S0 L3407-3408 [Page 473] and INDEX are generated navigation/header text, "
            "confirmed on CHP-22Index.pdf physical p.31; they are not an indexed object or factual claim."
        ),
        LEFT_SEGMENT: (
            "no_semantic_content: index-navigation-only. Index-seed classification only. CHP-22Index.pdf "
            "physical p.31 prints p.473. The segment contains UVWXYZ.csv#100-146 (47 rows): #124 is the "
            "already excluded Vivant-Denon see-under cross-reference; 45 entries have types (including the "
            "pre-existing person type for #135), and #101 collection remains type-pending. Types: "
            + ", ".join(f"{kind} {count}" for kind, count in segment_counts[LEFT_SEGMENT].items())
            + ". Printed page number/footer L3463 carries no index entity. Body relation leads are linked to "
            "their p.218, p.283 and p.341-344 statements; the index itself adds no mentions or statements."
        ),
        RIGHT_SEGMENT: (
            "no_semantic_content: index-navigation-only. Index-seed classification only. CHP-22Index.pdf "
            "physical p.31 prints p.473. The segment contains UVWXYZ.csv#147-190 (44 rows): 41 entries have "
            "types and the grouped medals/gems, paintings/caricatures and print collection at #185-187 remain "
            "type-pending. Types: "
            + ", ".join(f"{kind} {count}" for kind, count in segment_counts[RIGHT_SEGMENT].items())
            + ". Index person-contexts do not independently establish the listed relationships; body evidence "
            "is retained in endpoint-specific S2 statements for S6 review."
        ),
    }
    for segment_id, disposition, line_range in coverage_specs:
        coverage_by_id[segment_id].update({
            "disposition": disposition,
            "migration_status": "complete",
            "source_line_ranges": line_range,
            "note": coverage_notes[segment_id],
        })

    parsed = {}
    for line in statement_lines:
        body = line.rstrip("\r\n")
        if not body.strip():
            continue
        record = json.loads(body)
        statement_id = record.get("statement_id")
        if statement_id in parsed:
            raise SystemExit(f"duplicate statement ID before migration: {statement_id}")
        parsed[statement_id] = record
    new_ids = set(NEW_ENDPOINT_STATEMENTS) | {SMITH_SPLIT["new_statement_id"]}
    if new_ids & set(parsed):
        raise SystemExit("a planned p.473 endpoint-specific statement ID already exists")
    for statement_id, expected in RELATION_EXPECTATIONS.items():
        row = parsed.get(statement_id)
        if not row or (
            row.get("subject_candidate_id"), row.get("object_candidate_id"), row.get("predicate")
        ) != expected:
            raise SystemExit(f"relation statement identity changed or missing: {statement_id}")
        if row.get("qualifiers", {}).get("relation_candidate") is not None:
            raise SystemExit(f"unexpected relation-candidate prestate: {statement_id}")
    smith = parsed[SMITH_SPLIT["statement_id"]]
    if smith.get("original_quote") != SMITH_SPLIT["quote"]:
        raise SystemExit("the p.341 Joseph Smith/Schulenburg source quote changed")
    for statement_id, spec in NEW_ENDPOINT_STATEMENTS.items():
        base = parsed.get(spec["base_statement_id"])
        if not base or base.get("qualifiers", {}).get("source_line_start") != spec["source_line"]:
            raise SystemExit(f"source anchor changed for new relation statement: {statement_id}")
    required_candidates = {
        "cand-2838", "cand-2440", "cand-2401", "cand-0581", "cand-2154",
        "cand-2149", "cand-1862", "cand-10075", "cand-10063",
    }
    if required_candidates - set(candidate_by_id):
        raise SystemExit("one or more relation endpoints or context candidates are missing")

    rewritten_lines = []
    statement_updates = []
    statement_additions = []
    for line in statement_lines:
        newline = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        body = line.rstrip("\r\n")
        if not body.strip():
            rewritten_lines.append(line)
            continue
        row = json.loads(body)
        statement_id = row.get("statement_id")
        if statement_id in RELATION_EXPECTATIONS:
            row["qualifiers"]["relation_candidate"] = True
            statement_updates.append(statement_id)
            if statement_id == SMITH_SPLIT["statement_id"]:
                row["object_candidate_id"] = SMITH_SPLIT["smith_object"]
                row["predicate"] = "was_in_touch_with_joseph_smith"
                row["qualifiers"]["claim"] = "Haskell says Zanetti was in touch with Joseph Smith in Venice."
                row["qualifiers"]["qualification"] = (
                    "Haskell describes Smith and Schulenburg collectively as the two leading foreign collectors; "
                    "that ranking is Haskell's and is not independently verified."
                )
                row["qualifiers"]["mentioned_candidate_ids"] = SMITH_SPLIT["mention_ids"]
                rewritten_lines.append(serialize_jsonl(row, newline))
                schulenburg = deepcopy(row)
                schulenburg["statement_id"] = SMITH_SPLIT["new_statement_id"]
                schulenburg["object_candidate_id"] = SMITH_SPLIT["schulenburg_object"]
                schulenburg["predicate"] = "was_in_touch_with_schulenburg_in_venice"
                schulenburg["qualifiers"]["claim"] = "Haskell says Zanetti was in touch with Schulenburg in Venice."
                rewritten_lines.append(serialize_jsonl(schulenburg, newline))
                statement_additions.append(schulenburg["statement_id"])
                continue
        rewritten_lines.append(serialize_jsonl(row, newline) if statement_id in RELATION_EXPECTATIONS else line)
        if statement_id == "st-chp13-p341-paris_visit_with_carriera_and_pellegrini":
            spec = NEW_ENDPOINT_STATEMENTS["st-chp13-p341-zanetti_friendship_with_carriera"]
            new_row = make_endpoint_statement(
                row, "st-chp13-p341-zanetti_friendship_with_carriera", spec["object_candidate_id"],
                spec["predicate"], spec["claim"], spec["qualification"], spec["mentioned_candidate_ids"],
                spec["source_line"],
            )
            rewritten_lines.append(serialize_jsonl(new_row, newline))
            statement_additions.append(new_row["statement_id"])
        if statement_id == "st-chp13-p341-zanetti_contact_with_leading_artists":
            spec = NEW_ENDPOINT_STATEMENTS["st-chp13-p341-zanetti_contact_with_sebastiano_ricci"]
            new_row = make_endpoint_statement(
                row, "st-chp13-p341-zanetti_contact_with_sebastiano_ricci", spec["object_candidate_id"],
                spec["predicate"], spec["claim"], spec["qualification"], spec["mentioned_candidate_ids"],
                spec["source_line"],
            )
            rewritten_lines.append(serialize_jsonl(new_row, newline))
            statement_additions.append(new_row["statement_id"])

    if set(statement_updates) != set(RELATION_EXPECTATIONS):
        raise SystemExit("one or more relation-candidate statements were not updated")
    if set(statement_additions) != new_ids:
        raise SystemExit("one or more endpoint-specific p.473 statements were not created")

    p473_rows = [
        row for row in candidates
        if re.fullmatch(r"UVWXYZ\.csv#(1[0-8][0-9]|190)", row["index_entry_id"] or "")
    ]
    p473_open_untyped_after = sum(
        row["status"] == "open" and not row["suggested_type"] for row in p473_rows
    )
    index_untyped_after = sum(
        bool(row["index_entry_id"]) and row["status"] == "open" and not row["suggested_type"]
        for row in candidates
    )
    statement_count_before = sum(bool(line.strip()) for line in statement_lines)
    statement_count_after = statement_count_before + len(statement_additions)
    type_counts = dict(sorted(Counter(TYPE_BY_ENTRY.values()).items()))
    type_pending_entries = sorted(PENDING_BY_ENTRY)
    summary = {
        "segments": {
            MARKER_SEGMENT: "excluded/complete",
            LEFT_SEGMENT: "reviewed/complete",
            RIGHT_SEGMENT: "reviewed/complete",
        },
        "index_rows": {"total": 91, "open": 90, "excluded_alias": "UVWXYZ.csv#124 Vivant-Denon"},
        "classified_open_candidates": len(TYPE_BY_ENTRY),
        "preexisting_type_preserved": PREEXISTING_TYPES,
        "classified_types": type_counts,
        "segment_type_counts": segment_counts,
        "type_pending": type_pending_entries,
        "candidate_detail_updates": len(DETAIL_UPDATES) + len(PENDING_BY_ENTRY) + 1,
        "candidate_locator_correction": {
            "candidate_id": LOCATOR_CORRECTION["candidate_id"],
            "before": LOCATOR_CORRECTION["before"],
            "after": LOCATOR_CORRECTION["after"],
        },
        "relation_candidate_statements_marked": len(statement_updates) + len(statement_additions),
        "existing_relation_statements_updated": sorted(statement_updates),
        "new_endpoint_specific_statements": sorted(statement_additions),
        "candidate_count": len(candidates),
        "mentions_changed": False,
        "formal_relations_changed": False,
        "p473_open_untyped_before": p473_open_untyped_before,
        "p473_open_untyped_after": p473_open_untyped_after,
        "index_open_untyped_before": index_untyped_before,
        "index_open_untyped_after": index_untyped_after,
        "statement_count_before": statement_count_before,
        "statement_count_after": statement_count_after,
        "apply": args.apply,
    }

    if args.apply:
        backup_paths = [
            candidate_path.with_name(candidate_path.name + BACKUP_SUFFIX),
            coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX),
            statement_path.with_name(statement_path.name + BACKUP_SUFFIX),
        ]
        if any(path.exists() for path in backup_paths):
            raise SystemExit("a backup with this p.473 task suffix already exists")
        for original, backup in zip((candidate_path, coverage_path, statement_path), backup_paths):
            shutil.copy2(original, backup)
        write_csv(candidate_path, candidates, candidate_bom, candidate_eol)
        write_csv(coverage_path, coverage, coverage_bom, coverage_eol)
        write_jsonl(statement_path, rewritten_lines, statement_bom)
        summary["backups"] = [str(path.relative_to(ROOT)) for path in backup_paths]

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
