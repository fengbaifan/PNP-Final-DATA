from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
PDF = ROOT / "02-sources/01-book/CHP-3.pdf"
SEGMENT = "chp-3:03_CHP-3_sec_ii:l62-72"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp3-sec-ii-l62-72-relations-20261010")

HASHES = {
    TABLE: "7e1b352415dbea429e879b9128987d0196f5e7ab915fc22f4d03c962e1e83b1c",
    CANDIDATES: "c8be066459de9f9819989899c04a85e6b86287843b3c67751b469daa3dc812ca",
    MENTIONS: "136c4227f382f12d0156a92d34c5572072be0ee6a5ccdcda0a1a9cac4947c0f8",
    COVERAGE: "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SOURCE: "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
}

EXISTING_IDS = {
    "chiesa": "st-chp3-secii-l62-72-chiesa-nuova-cradle-of-baroque",
    "palace": "st-chp3-secii-l62-72-costanza-legacy-palace-and-church",
    "gesualdo_build": "st-chp3-secii-l62-72-gesualdo-agreed-to-build-theatine-church",
    "architects": "st-chp3-secii-l62-72-gesualdo-appointed-own-architects",
    "death_delay": "st-chp3-secii-l62-72-gesualdo-death-delay-incomplete-church",
    "st_andrew": "st-chp3-secii-l62-72-legacy-obliged-theatines-to-found-st-andrew-church",
    "maderno": "st-chp3-secii-l62-72-maderno-brought-in-work-proceeded",
    "delighted": "st-chp3-secii-l62-72-oratorians-delighted-with-result",
    "assimilated": "st-chp3-secii-l62-72-order-assimilated-three-masterpieces",
    "taste": "st-chp3-secii-l62-72-order-no-specific-individual-taste",
    "pathos": "st-chp3-secii-l62-72-pathos-influenced-bernin-and-cortona",
    "peretti": "st-chp3-secii-l62-72-peretti-montalto-took-over-and-funded-church",
    "reni_algardi": "st-chp3-secii-l62-72-reni-algardi-raised-church-stature",
    "colour": "st-chp3-secii-l62-72-rubens-colour-and-pathos",
    "baronio": "st-chp3-secii-l62-72-rubens-followed-probable-baronio-instructions",
    "style": "st-chp3-secii-l62-72-rubens-picture-spirit-and-style",
    "pressure": "st-chp3-secii-l62-72-social-pressure-altered-church",
    "nickname": "st-chp3-secii-l62-72-theatines-austerity-nickname",
    "support": "st-chp3-secii-l62-72-theatines-princely-support",
}

DECISIONS = {
    "chiesa": (True, "Haskell's metaphor places Chiesa Nuova among the cradles of the Baroque; retain this as an attributed interpretive relation."),
    "palace": (True, "The 1582 legacy is explicitly said to give the unnamed palace to the Theatines; the adjacent S. Sebastiano church is split into its own scalar row."),
    "gesualdo_build": (True, "Haskell reports Gesualdo's agreement to build a large church for the Theatines; no exact year is inferred."),
    "architects": (True, "The source says the named architect had complete authority over the person proposed by the Theatines; Gesualdo remains the actor who insisted on this arrangement."),
    "death_delay": (False, "This is a chronological construction-status statement after Gesualdo's death, not a direct relation between the person and church; retain the person and year as context."),
    "st_andrew": (True, "The legacy explicitly obliged the Theatines to found a church dedicated to St Andrew; the building's later identity remains unresolved."),
    "maderno": (True, "Haskell says Peretti-Montalto brought Maderno into the Theatine church project; the construction-progress clause continues at L75 and is represented in the linked next-segment statement."),
    "delighted": (True, "This is an explicitly qualified response relation: Haskell says there is every reason to believe the Oratorians were delighted with the result; retain the inference and the slate-proposal referent."),
    "assimilated": (False, "The aggregate sentence combines three works and functions as context for Haskell's evaluative conclusion. Three scalar work relations are recorded separately, with the fifteen-year span and work-identity limits preserved."),
    "taste": (False, "This is Haskell's evaluative conclusion about institutional taste, not a relation between bounded entities."),
    "pathos": (True, "Haskell interprets the painting's pathos as crucial to Bernini's development; the separate Cortona endpoint is recorded in a scalar statement."),
    "peretti": (True, "Haskell reports Peretti-Montalto taking charge of the building project in 1608; the separately stated funding guarantee is recorded in its own scalar statement."),
    "reni_algardi": (False, "The parent sentence combines named and unnamed contributors with an implicit interpretation of who the 'real patrons' were. Scalar rows separately record only the two named artists' contributions; the inferred patron referent remains qualified."),
    "colour": (False, "This is an aesthetic description of the painting, not an inter-entity relation."),
    "baronio": (True, "Haskell says Rubens probably received instructions from Baronio and faithfully interpreted them; the probability qualification is retained."),
    "style": (False, "This is Haskell's comparative stylistic assessment of the painting, not an inter-entity relation."),
    "pressure": (True, "Haskell attributes a change in the church's character to pressure from the bounded but unnamed group of prelates and distinguished gentlemen."),
    "nickname": (False, "This is an attributed institutional-name and austerity characterization, not a relation between distinct entities."),
    "support": (True, "Haskell describes the Theatines' church-building and decoration as shaped by advantages and drawbacks of princely support; no particular prince or church identity is inferred."),
}

NEW_SPECS = [
    {
        "id": "st-chp3-secii-l62-72-costanza-legacy-s-sebastiano",
        "parent": "palace", "subject": "cand-1927", "object": "cand-0721",
        "predicate": "legacy_gave_adjacent_church_to_theatines",
        "start": 67, "end": 68,
        "claim": "Haskell says the 1582 legacy from Donna Costanza gave the Theatines the little adjoining church of S. Sebastiano.",
        "extras": {"recipient_candidate_id": "cand-3404", "approximate_place_candidate_id": "cand-4490", "qualification": "The indexed S. Sebastiano candidate is reused; no ownership beyond the bequest is inferred."},
        "note": "The source explicitly includes S. Sebastiano among the property given to the Theatines; use the exact indexed church candidate and keep it separate from the unnamed palace.",
    },
    {
        "id": "st-chp3-secii-l62-72-olivieri-authority-over-proposed-person",
        "parent": "architects", "subject": "cand-1779", "object": "cand-5063",
        "predicate": "had_complete_authority_over_theatines_proposed_commissionee",
        "start": 69, "end": 69,
        "claim": "Haskell says Pietro Paolo Olivieri, following Della Porta, was to have complete authority over the person proposed by the Theatines.",
        "extras": {"commission_actor_candidate_id": "cand-1149", "architect_sequence": "second", "proposed_person_candidate_id": "cand-5063", "qualification": "The proposed person is unnamed and distinct from both of Gesualdo's architects."},
        "note": "The source names Olivieri as the second architect in the authority arrangement; retain the unnamed Theatine nominee as the object and Gesualdo as the insisting actor in qualifiers.",
    },
    {
        "id": "st-chp3-secii-l62-72-order-assimilated-barocci-masterpiece",
        "parent": "assimilated", "subject": "cand-3402", "object": "cand-5039",
        "predicate": "assimilated_masterpiece_by_artist_within_fifteen_years",
        "start": 65, "end": 65,
        "claim": "Haskell says the Oratorian order assimilated the Barocci masterpiece in the church context within the fifteen-year span he describes.",
        "extras": {"artist_candidate_id": "cand-0247", "time_span_years": 15, "work_candidate_id": "cand-5039", "qualification": "Retain Haskell's word 'assimilate'; no title, acquisition method, ownership, or start/end year is inferred."},
        "note": "This scalar row links the passage's Barocci masterpiece to its existing candidate; the source does not supply a title or acquisition mechanism.",
    },
    {
        "id": "st-chp3-secii-l62-72-order-assimilated-caravaggio-masterpiece",
        "parent": "assimilated", "subject": "cand-3402", "object": "cand-4018",
        "predicate": "assimilated_masterpiece_by_artist_within_fifteen_years",
        "start": 65, "end": 65,
        "claim": "Haskell says the Oratorian order assimilated the Caravaggio masterpiece in the church context within the fifteen-year span he describes.",
        "extras": {"artist_candidate_id": "cand-0549", "time_span_years": 15, "work_candidate_id": "cand-4018", "qualification": "Retain Haskell's word 'assimilate'; no title, acquisition method, ownership, or start/end year is inferred."},
        "note": "This scalar row links the passage's Caravaggio masterpiece to its existing candidate; the source does not supply a title or acquisition mechanism.",
    },
    {
        "id": "st-chp3-secii-l62-72-order-assimilated-rubens-masterpiece",
        "parent": "assimilated", "subject": "cand-3402", "object": "cand-3206",
        "predicate": "assimilated_masterpiece_by_artist_within_fifteen_years",
        "start": 65, "end": 65,
        "claim": "Haskell says the Oratorian order assimilated the Rubens masterpiece in the church context within the fifteen-year span he describes.",
        "extras": {"artist_candidate_id": "cand-3093", "time_span_years": 15, "work_candidate_id": "cand-3206", "qualification": "Retain Haskell's word 'assimilate'; no title, acquisition method, ownership, or start/end year is inferred. The earlier canvas and later slate proposal remain distinct."},
        "note": "This scalar row uses the earlier Rubens painting candidate in local context and preserves the unresolved relation to the later slate proposal for S3.",
    },
    {
        "id": "st-chp3-secii-l62-72-pathos-influenced-cortona",
        "parent": "pathos", "subject": "cand-3206", "object": "cand-0342",
        "predicate": "pathos_later_crucial_for_artist_development",
        "start": 64, "end": 64,
        "claim": "Haskell interprets the painting's exuberant pathos as later crucial to Pietro da Cortona's development.",
        "extras": {"artist_candidate_id": "cand-0342", "qualification": "This is Haskell's art-historical interpretation, not an independently verified causal relation.", "version_identity_note": "The stylistic discussion follows the newly accepted slate proposal at L159, while 'the painting' may still refer to the earlier canvas cand-3206. Preserve this ambiguity for S3."},
        "note": "The source names Pietro da Cortona as a second artist whose development the painting's pathos influenced; retain the interpretive and version qualifications.",
    },
    {
        "id": "st-chp3-secii-l62-72-peretti-montalto-guaranteed-funding",
        "parent": "peretti", "subject": "cand-2992", "object": "cand-5061",
        "predicate": "guaranteed_funding_for_building_project",
        "start": 71, "end": 71,
        "claim": "Haskell says Peretti-Montalto guaranteed 160,000 gold scudi for the Theatine church building project.",
        "extras": {"year": 1608, "amount": 160000, "currency": "gold scudi", "funding_project_candidate_id": "cand-5061", "qualification": "A guarantee is reported; the passage does not establish that the amount was disbursed."},
        "note": "The guarantee and amount are explicit, but a guarantee is not treated as proof of payment or completed expenditure.",
    },
    {
        "id": "st-chp3-secii-l62-72-reni-contribution-to-church",
        "parent": "reni_algardi", "subject": "cand-2124", "object": "cand-0710",
        "predicate": "contributed_to_church_stature",
        "start": 66, "end": 66,
        "claim": "Haskell says Guido Reni's contribution added to the stature of Chiesa Nuova.",
        "extras": {"qualification": "This records only the named artist's contribution; the work and commission mechanism are unspecified."},
        "note": "Haskell explicitly names Reni among contributors to the church's stature; no specific work or commission is inferred.",
    },
    {
        "id": "st-chp3-secii-l62-72-algardi-contribution-to-church",
        "parent": "reni_algardi", "subject": "cand-0034", "object": "cand-0710",
        "predicate": "contributed_to_church_stature",
        "start": 66, "end": 66,
        "claim": "Haskell says Alessandro Algardi's contribution added to the stature of Chiesa Nuova.",
        "extras": {"qualification": "This records only the named artist's contribution; the work and commission mechanism are unspecified."},
        "note": "Haskell explicitly names Algardi among contributors to the church's stature; no specific work or commission is inferred.",
    },
]

EXPECTED_BEFORE = {
    "statements": 12713, "candidates": 11567, "mentions": 27506,
    "bilateral": 8509, "bilateral_true": 4647, "bilateral_false": 465,
    "bilateral_pending": 3397, "relation_candidates_total": 4694,
    "relation_candidates_open": 47,
}
EXPECTED_AFTER = {
    "statements": 12722, "candidates": 11567, "mentions": 27506,
    "bilateral": 8517, "bilateral_true": 4668, "bilateral_false": 466,
    "bilateral_pending": 3383, "relation_candidates_total": 4715,
    "relation_candidates_open": 47,
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def has_id(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def flag(row):
    return (row.get("qualifiers") or {}).get("relation_candidate")


def stats(rows, candidate_count, mention_count):
    bilateral = [r for r in rows if has_id(r.get("subject_candidate_id")) and has_id(r.get("object_candidate_id"))]
    return {
        "statements": len(rows), "candidates": candidate_count, "mentions": mention_count,
        "bilateral": len(bilateral),
        "bilateral_true": sum(flag(r) is True for r in bilateral),
        "bilateral_false": sum(flag(r) is False for r in bilateral),
        "bilateral_pending": sum(flag(r) is None for r in bilateral),
        "relation_candidates_total": sum(flag(r) is True for r in rows),
        "relation_candidates_open": sum(flag(r) is True and not (has_id(r.get("subject_candidate_id")) and has_id(r.get("object_candidate_id"))) for r in rows),
    }


def atomic_replace(path: Path, payload: bytes):
    fd, name = tempfile.mkstemp(prefix="book-statements.s2-l62-72.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    except Exception:
        try:
            os.unlink(name)
        except FileNotFoundError:
            pass
        raise


def apply_decision(row, key):
    value, note = DECISIONS[key]
    row.setdefault("qualifiers", {})["relation_candidate"] = value
    row["qualifiers"]["relation_candidate_note"] = note


def make_child(spec, parent, source_lines):
    q = parent["qualifiers"]
    qualifiers = {
        "source_line_start": spec["start"], "source_line_end": spec["end"],
        "claim": spec["claim"], "speaker": q.get("speaker", "Haskell"),
        "text_layer": q.get("text_layer", "authorial narrative"),
        "print_page": 71, "pdf_physical_page": 9,
        "relation_candidate": True, "relation_candidate_note": spec["note"],
    }
    qualifiers.update(spec["extras"])
    return {
        "statement_id": spec["id"], "segment_id": SEGMENT,
        "subject_candidate_id": spec["subject"], "object_candidate_id": spec["object"],
        "predicate": spec["predicate"], "qualifiers": qualifiers,
        "original_quote": "\n".join(source_lines[spec["start"] - 1:spec["end"]]),
        "origin": "book", "source_file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
    }


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    for path, expected in HASHES.items():
        actual = digest(path)
        if actual != expected:
            raise SystemExit(f"SHA mismatch: {path.relative_to(ROOT)} expected {expected}, found {actual}")
    if args.apply and BACKUP.exists():
        raise SystemExit(f"Recovery backup already exists: {BACKUP}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    rows = read_jsonl(TABLE)
    candidates = {r["candidate_id"] for r in __import__("csv").DictReader(CANDIDATES.open(encoding="utf-8-sig", newline=""))}
    mentions = list(__import__("csv").DictReader(MENTIONS.open(encoding="utf-8-sig", newline="")))
    mention_index = {r["mention_id"]: r for r in mentions}
    target = {r["statement_id"]: r for r in rows if r.get("segment_id") == SEGMENT}
    if len(target) != 19 or set(target) != set(EXISTING_IDS.values()):
        raise SystemExit(f"Unexpected target statement set: count={len(target)}")
    if any("relation_candidate" in (r.get("qualifiers") or {}) for r in target.values()):
        raise SystemExit("At least one target statement already has a relation_candidate decision")
    before = stats(rows, len(candidates), len(mentions))
    if before != EXPECTED_BEFORE:
        raise SystemExit(f"Unexpected pre-write counts: {before}")

    coverage_rows = [json.loads(json.dumps(r)) for r in __import__("csv").DictReader(COVERAGE.open(encoding="utf-8-sig", newline="")) if r["segment_id"] == SEGMENT]
    if len(coverage_rows) != 1 or (coverage_rows[0]["disposition"], coverage_rows[0]["migration_status"], coverage_rows[0]["source_line_ranges"]) != ("reviewed", "complete", "L63-72"):
        raise SystemExit(f"Unexpected coverage status: {coverage_rows}")

    # Confirm exact reused mention anchors for the split endpoints.
    for mention_id, candidate_id in (("m-chp3-secii-l62-72-0031", "cand-0721"), ("m-chp3-secii-l62-72-0043", "cand-1779")):
        mention = mention_index.get(mention_id)
        if not mention or mention["candidate_id"] != candidate_id:
            raise SystemExit(f"Missing or changed mention anchor: {mention_id}")

    # The printed page-71 notes point to the sentences they annotate.
    note_targets = {
        "st-chp3-secii-p71-note1-cozzi": EXISTING_IDS["nickname"],
        "st-chp3-secii-p71-note1-ponnelle-bordet": EXISTING_IDS["nickname"],
        "st-chp3-secii-p71-note2-hibbard": EXISTING_IDS["support"],
        "st-chp3-secii-p71-note2-ortolani": EXISTING_IDS["support"],
    }
    for note_id, expected_body in note_targets.items():
        note = next((r for r in rows if r["statement_id"] == note_id), None)
        if not note or expected_body not in note.get("qualifiers", {}).get("linked_body_statement_ids", []):
            raise SystemExit(f"Footnote backlink mismatch: {note_id}")

    staged = {key: copy.deepcopy(target[statement_id]) for key, statement_id in EXISTING_IDS.items()}
    for key, row in staged.items():
        apply_decision(row, key)

    # Narrow composite claims and correct endpoint direction before adding scalar children.
    staged["palace"]["predicate"] = "legacy_gave_palace_to_theatines"
    staged["palace"]["qualifiers"]["claim"] = "Haskell says the 1582 legacy from Donna Costanza gave the Theatines an unnamed palace in central Rome."
    staged["palace"]["qualifiers"].pop("additional_property_candidate_id", None)

    architects = staged["architects"]
    architects["subject_candidate_id"] = "cand-1976"
    architects["object_candidate_id"] = "cand-5063"
    architects["predicate"] = "had_complete_authority_over_theatines_proposed_commissionee"
    architects["qualifiers"]["claim"] = "Haskell says Giacomo della Porta, the first architect insisted upon by Gesualdo, was to have complete authority over the person proposed by the Theatines."
    architects["qualifiers"]["commission_actor_candidate_id"] = "cand-1149"
    architects["qualifiers"]["architect_sequence"] = "first"
    architects["qualifiers"]["proposed_person_candidate_id"] = "cand-5063"
    architects["qualifiers"].pop("additional_architect_candidate_id", None)

    death = staged["death_delay"]
    death["subject_candidate_id"] = "cand-5061"
    death["object_candidate_id"] = None
    death["predicate"] = "church_remained_incomplete_after_gesualdo_death"
    death["qualifiers"]["claim"] = "Haskell says the usual delay followed Gesualdo's death in 1603 and the Theatine church remained far from complete."
    death["qualifiers"]["event_person_candidate_id"] = "cand-1149"
    death["qualifiers"]["event_year"] = 1603

    maderno = staged["maderno"]
    maderno["predicate"] = "brought_architect_into_project"
    maderno["qualifiers"]["claim"] = "Haskell says Peretti-Montalto brought Carlo Maderno into the Theatine church project."

    assimilated = staged["assimilated"]
    assimilated["qualifiers"]["claim"] = "Haskell says the Oratorian order could assimilate masterpieces by Barocci, Caravaggio and Rubens within fifteen years."

    pathos = staged["pathos"]
    pathos["predicate"] = "pathos_later_crucial_for_artist_development"
    pathos["qualifiers"]["claim"] = "Haskell interprets the painting's exuberant pathos as later crucial to Bernini's development."
    pathos["qualifiers"].pop("additional_artist_candidate_id", None)

    peretti = staged["peretti"]
    peretti["predicate"] = "took_charge_of_building_project"
    peretti["qualifiers"]["claim"] = "Haskell says Peretti-Montalto took the Theatine church building in hand in 1608 despite advice against continuing a building begun by others."
    peretti["qualifiers"].pop("amount", None)
    peretti["qualifiers"].pop("currency", None)

    reni = staged["reni_algardi"]
    reni["subject_candidate_id"] = "cand-0710"
    reni["object_candidate_id"] = None
    reni["qualifiers"]["claim"] = "Haskell interprets the contributions of named and unnamed later artists as raising the church's stature and revealing who its real patrons were."

    for key, row in staged.items():
        target[row["statement_id"]].update(row)

    new_rows = [make_child(spec, staged[spec["parent"]], source_lines) for spec in NEW_SPECS]
    existing_ids = {r["statement_id"] for r in rows}
    for row in new_rows:
        if row["statement_id"] in existing_ids:
            raise SystemExit(f"Statement ID collision: {row['statement_id']}")
        for endpoint in (row["subject_candidate_id"], row["object_candidate_id"]):
            if endpoint not in candidates:
                raise SystemExit(f"Unknown endpoint {endpoint} in {row['statement_id']}")
        q = row["qualifiers"]
        anchor = "\n".join(source_lines[q["source_line_start"] - 1:q["source_line_end"]])
        if row["original_quote"] != anchor:
            raise SystemExit(f"Quote range mismatch: {row['statement_id']}")
        if not row["qualifiers"]["relation_candidate"]:
            raise SystemExit(f"New scalar row is not a relation candidate: {row['statement_id']}")

    # Verify every source object referenced in qualifiers is an existing candidate.
    for row in list(staged.values()) + new_rows:
        q = row.get("qualifiers", {})
        for key, value in q.items():
            if key.endswith("candidate_id") and value and value not in candidates:
                raise SystemExit(f"Unknown qualifier endpoint {key}={value} in {row['statement_id']}")
            if key.endswith("candidate_ids") and isinstance(value, list):
                if any(item not in candidates for item in value):
                    raise SystemExit(f"Unknown qualifier endpoint in {key} for {row['statement_id']}")

    by_id = {r["statement_id"]: r for r in rows}
    for row in new_rows:
        by_id[row["statement_id"]] = row
    final_rows = [by_id[r["statement_id"]] for r in rows] + new_rows
    after = stats(final_rows, len(candidates), len(mentions))
    if after != EXPECTED_AFTER:
        raise SystemExit(f"Unexpected post-write counts: {after}")
    segment_rows = [r for r in final_rows if r.get("segment_id") == SEGMENT]
    if len(segment_rows) != 28 or any(flag(r) is None for r in segment_rows):
        raise SystemExit(f"Segment classification incomplete: rows={len(segment_rows)}")
    if sum(flag(r) is True for r in segment_rows) != 21 or sum(flag(r) is False for r in segment_rows) != 7:
        raise SystemExit("Unexpected segment true/false classification totals")

    print(f"PREVIEW segment={SEGMENT} reviewed_rows=19 added_scalar_rows={len(new_rows)} final_segment_rows={len(segment_rows)}")
    print(f"PREVIEW true={sum(flag(r) is True for r in segment_rows)} false={sum(flag(r) is False for r in segment_rows)}")
    print(f"COUNTS before={before}")
    print(f"COUNTS after={after}")
    for row in new_rows:
        print(f"ADD {row['statement_id']} | {row['subject_candidate_id']} -> {row['object_candidate_id']} | {row['predicate']}")
    if not args.apply:
        print("Dry run only; no files written.")
        return

    if digest(TABLE) != HASHES[TABLE]:
        raise SystemExit("Statement table changed after preflight; refusing to apply.")
    import shutil
    shutil.copy2(TABLE, BACKUP)
    payload = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in final_rows).encode("utf-8")
    try:
        atomic_replace(TABLE, payload)
    except Exception:
        shutil.copy2(BACKUP, TABLE)
        raise
    written = read_jsonl(TABLE)
    if stats(written, len(candidates), len(mentions)) != EXPECTED_AFTER:
        shutil.copy2(BACKUP, TABLE)
        raise SystemExit("Post-write count mismatch; statement table restored from backup.")
    print(f"APPLIED sha256={digest(TABLE)} backup={BACKUP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
