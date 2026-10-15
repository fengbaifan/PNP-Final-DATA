from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp2-sec-i-l71-80-20261010"
SEGMENT_ID = "chp-2:02_CHP-2_sec_i:l71-80"
SOURCE_FILE = "02-sources/02-Markdown/02_CHP-2_sec_i.md"

EXPECTED_HASHES = {
    "04-knowledge/tables/book-statements.jsonl": "b034bfbb42c2c3a94844b23e50256712743b6102b4e7fa37214cf5a7a1639a70",
    "04-knowledge/tables/entity-candidates.csv": "b214ec44c825690db146c4efdcb96e1de4acbbc5d682104ec0c35535d53b2dae",
    "04-knowledge/tables/mentions.csv": "e6179e8cf85a5313d16bad9b24a2d7a529b6d368a39ff6339270181f084888ad",
    "04-knowledge/tables/s2-coverage.csv": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SOURCE_FILE: "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6",
}

DECISIONS = {
    "st-chp2-seci-l71-80-arpino-employed": (True, "Haskell directly says Scipione often employed d’Arpino; the contrast with the confiscation account is preserved without dates or contract detail."),
    "st-chp2-seci-l71-80-arpino-picture-seizure": (True, "Haskell reports that Scipione obtained the picture group by ordering confiscation from d’Arpino; keep the count and attribution as reported and retain no individual picture titles."),
    "st-chp2-seci-l71-80-bologna-legate": (True, "Haskell says Maffeo went to Bologna as Legate in 1611; preserve the source's evaluation of the post and do not infer appointing authority."),
    "st-chp2-seci-l71-80-collection-fragment": (True, "The sentence begins the account of Scipione accumulating a collection and continues in the next segment as 'a wonderful collection of paintings'; preserve the cross-segment completion and open collection identity."),
    "st-chp2-seci-l71-80-deposition-removal": (True, "Haskell reports Raphael’s Deposition was taken from the Baglioni chapel and removed to Scipione’s collection; this records the work’s reported destination, not later ownership or location. The order is attributed to Scipione in the quotation."),
    "st-chp2-seci-l71-80-domenichino-commission": (True, "Haskell directly reports Cardinal Aldobrandini commissioned the Hunt of Diana from Domenichino; retain the reported work attribution."),
    "st-chp2-seci-l71-80-domenichino-imprisonment": (True, "The source explicitly names Domenichino’s contract with Cardinal Aldobrandini and says he was imprisoned for honoring it; the contract relation is supported, but the jailer and cause beyond Haskell’s wording are not inferred."),
    "st-chp2-seci-l71-80-maderno-nave-continuation": (True, "The opening 'Carlo Maderno' completes the prior segment’s clause naming the proposer of the nave; preserve the cross-segment sentence and do not infer additional authorship."),
    "st-chp2-seci-l71-80-paul-scipione-spending": (False, "Paul V and Scipione are coordinated subjects said to spend on separate patronage activity; the source does not assert that they spent jointly or had a relation to one another."),
    "st-chp2-seci-l71-80-paul-v-art-periodization": (True, "Haskell places the abandonment of austere functionalism during Paul V’s pontificate; preserve this as authorial periodization, not as Paul V personally causing the change."),
    "st-chp2-seci-l71-80-resources-st-peters": (False, "The source says 'their main resources' after naming both Paul V and Scipione, while this statement has only Paul V as subject. It does not allocate the shared referent to him individually; preserve the group-level claim without a one-person edge."),
    "st-chp2-seci-l71-80-return-rome-1617": (True, "Haskell reports Maffeo’s 1617 return to Rome and residence there for the rest of his life; keep the lifetime-duration claim attributed."),
    "st-chp2-seci-l71-80-rome-atmosphere": (True, "Haskell directly compares Maffeo’s experience of Rome at this return with his earlier residence and repeated visits; retain the relative chronology."),
    "st-chp2-seci-l71-80-scipione-art-change": (False, "Paul V is the period context, not the object of Scipione’s role in encouraging the artistic changes. The phrase 'these changes' has no matching object endpoint here; do not turn the period reference into a person-to-person relation."),
    "st-chp2-seci-l71-80-scipione-covets-hunt": (True, "Haskell explicitly says Scipione coveted Domenichino’s Hunt of Diana; this does not establish ownership or a commission from Scipione."),
    "st-chp2-seci-l71-80-smm-family-chapel-comparison": (True, "Haskell directly compares the richness and colour of the two named chapels; preserve the claim as an attributed aesthetic comparison, not a measurement."),
    "st-chp2-seci-l71-80-spoleto-bishopric": (True, "Haskell reports that Maffeo moved to Spoleto and was made Bishop there; appointing authority and exact date remain unstated."),
    "st-chp2-seci-l71-80-zeno-scipione-learning": (False, "The quoted ambassadorial testimony characterizes Scipione but does not establish a social or institutional relation between Zeno and Scipione."),
}

EXPECTED_ROWS = {
    "st-chp2-seci-l71-80-arpino-employed": ("cand-0394", "cand-0121", "artist_employment_reported", 80, 80, "among the artists whom he himself often employed"),
    "st-chp2-seci-l71-80-arpino-picture-seizure": ("cand-0394", "cand-4278", "picture_confiscation_reported", 79, 79, "He obtained 105 pictures"),
    "st-chp2-seci-l71-80-bologna-legate": ("cand-3104", "cand-0381", "legate_post_reported", 73, 73, "to Bologna where he went as Legate"),
    "st-chp2-seci-l71-80-collection-fragment": ("cand-0394", "cand-11474", "collection_accumulation_fragment", 80, 80, "accumulate a wonderful"),
    "st-chp2-seci-l71-80-deposition-removal": ("cand-2099", "cand-11474", "ordered_theft_and_transfer_reported", 80, 80, "Raphael’s Deposition was, on his orders, stolen from the Baglioni family chapel in Perugia and removed by night to his collection"),
    "st-chp2-seci-l71-80-domenichino-commission": ("cand-0032", "cand-4030", "commission_from_cardinal_reported", 80, 80, "Cardinal Aldobrandini, who had commissioned from him a Hunt of Diana"),
    "st-chp2-seci-l71-80-domenichino-imprisonment": ("cand-0932", "cand-0032", "imprisoned_for_honoring_contract_reported", 80, 80, "Domenichino was imprisoned because he had the rashness to abide by his contract with Cardinal Aldobrandini"),
    "st-chp2-seci-l71-80-maderno-nave-continuation": ("cand-1477", "cand-3135", "nave_proposal_author_continued", 72, 72, "Carlo Maderno"),
    "st-chp2-seci-l71-80-paul-scipione-spending": ("cand-0393", "cand-0394", "joint_patronage_expenditure_reported", 75, 76, "Pope Paul V and his nephew Cardinal\nScipione Borghese were spending spectacular sums"),
    "st-chp2-seci-l71-80-paul-v-art-periodization": ("cand-0393", "cand-4281", "authorial_art_historical_periodization", 77, 77, "The essential change that had occurred in the arts during the pontificate of Paul V"),
    "st-chp2-seci-l71-80-resources-st-peters": ("cand-0393", "cand-3135", "resources_devoted_to_basilica", 76, 76, "Their main resources were devoted to St Peter’s"),
    "st-chp2-seci-l71-80-return-rome-1617": ("cand-3104", "cand-3126", "return_and_residence_reported", 73, 74, "he returned to\nRome in 1617 and stayed there for the rest of his hfe"),
    "st-chp2-seci-l71-80-rome-atmosphere": ("cand-3104", "cand-3126", "authorial_comparison_of_city_context", 75, 75, "In Rome, Cardinal Barberini found the atmosphere very different"),
    "st-chp2-seci-l71-80-scipione-art-change": ("cand-0394", "cand-0393", "patron_role_in_artistic_change_authorial", 77, 77, "No one played a greater part in the encouragement and enjoyment of these changes than Cardinal Scipione Borghese"),
    "st-chp2-seci-l71-80-scipione-covets-hunt": ("cand-0394", "cand-4030", "work_coveted_reported", 80, 80, "a Hunt of Diana which Scipione coveted"),
    "st-chp2-seci-l71-80-smm-family-chapel-comparison": ("cand-4276", "cand-4277", "chapel_richness_comparison", 76, 76, "S. Maria Maggiore where the family chapel outdid that of Sixtus V in richness and colour"),
    "st-chp2-seci-l71-80-spoleto-bishopric": ("cand-3104", "cand-4273", "move_and_bishopric_reported", 72, 73, "first to Spoleto of which he was made\nBishop"),
    "st-chp2-seci-l71-80-zeno-scipione-learning": ("cand-4265", "cand-0394", "ambassadorial_characterization", 78, 79, "the Venetian ambassador pointed out"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"PRECONDITION FAILED: {message}")


def load_rows() -> list[dict]:
    return [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]


def flag(row: dict):
    return row.get("qualifiers", {}).get("relation_candidate")


def bilateral(row: dict) -> bool:
    return bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))


def counts(rows: list[dict]) -> dict[str, int]:
    return {
        "statements": len(rows),
        "relation_true": sum(flag(row) is True for row in rows),
        "relation_false": sum(flag(row) is False for row in rows),
        "true_bilateral": sum(flag(row) is True and bilateral(row) for row in rows),
        "true_open": sum(flag(row) is True and not bilateral(row) for row in rows),
        "false_bilateral": sum(flag(row) is False and bilateral(row) for row in rows),
        "unclassified_bilateral": sum(bilateral(row) and flag(row) is None for row in rows),
    }


def preflight() -> tuple[list[dict], dict[str, int]]:
    for relative, expected_hash in EXPECTED_HASHES.items():
        path = ROOT / relative
        require(path.is_file(), f"missing input: {relative}")
        require(sha256(path) == expected_hash, f"input hash changed: {relative}")

    rows = load_rows()
    by_id = {row.get("statement_id"): row for row in rows}
    require(len(by_id) == len(rows), "statement IDs are not unique")
    require(set(DECISIONS) == set(EXPECTED_ROWS), "decision and target sets differ")
    require(set(DECISIONS) <= set(by_id), "one or more target statements are missing")

    for statement_id, (subject, object_id, predicate, line_start, line_end, quote_anchor) in EXPECTED_ROWS.items():
        row = by_id[statement_id]
        qualifiers = row.get("qualifiers", {})
        require(row.get("segment_id") == SEGMENT_ID, f"segment changed for {statement_id}")
        require(row.get("subject_candidate_id") == subject and row.get("object_candidate_id") == object_id,
                f"endpoint changed for {statement_id}")
        require(row.get("predicate") == predicate, f"predicate changed for {statement_id}")
        require(qualifiers.get("source_line_start") == line_start and qualifiers.get("source_line_end") == line_end,
                f"source line changed for {statement_id}")
        require(flag(row) is None, f"already classified: {statement_id}")
        require(quote_anchor in row.get("original_quote", ""), f"quote anchor changed for {statement_id}")

    with (TABLES / "s2-coverage.csv").open(encoding="utf-8-sig", newline="") as handle:
        coverage = [row for row in csv.DictReader(handle) if row.get("segment_id") == SEGMENT_ID]
    require(len(coverage) == 1 and coverage[0].get("disposition") == "reviewed"
            and coverage[0].get("migration_status") == "complete", "coverage is not reviewed/complete")

    with (TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="") as handle:
        mentions = list(csv.DictReader(handle))
    segment_candidates = {row.get("candidate_id") for row in mentions if row.get("segment_id") == SEGMENT_ID}
    endpoints = {value for row in EXPECTED_ROWS.values() for value in row[:2]}
    require(endpoints <= segment_candidates, "one or more statement endpoints lack a segment mention")

    source_lines = (ROOT / SOURCE_FILE).read_text(encoding="utf-8").splitlines()
    for statement_id, (_, _, _, line_start, line_end, quote_anchor) in EXPECTED_ROWS.items():
        excerpt = "\n".join(source_lines[line_start - 1:line_end])
        require(quote_anchor in excerpt, f"source anchor changed for {statement_id}")

    before = counts(rows)
    require(before == {
        "statements": 12700,
        "relation_true": 3940,
        "relation_false": 1810,
        "true_bilateral": 3913,
        "true_open": 27,
        "false_bilateral": 445,
        "unclassified_bilateral": 4139,
    }, "current statement totals changed")
    return rows, before


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify 18 pending bilateral statements in chapter 2 section i L71-80.")
    parser.add_argument("--apply", action="store_true", help="write the preflighted classifications")
    args = parser.parse_args()
    rows, before = preflight()

    updated = [dict(row) for row in rows]
    for row in updated:
        statement_id = row.get("statement_id")
        if statement_id in DECISIONS:
            value, note = DECISIONS[statement_id]
            row["qualifiers"] = dict(row.get("qualifiers", {}))
            row["qualifiers"]["relation_candidate"] = value
            row["qualifiers"]["relation_candidate_note"] = note

    after = counts(updated)
    print(f"PREVIEW: {SEGMENT_ID}")
    for statement_id, (value, _) in DECISIONS.items():
        print(f"  {statement_id}: relation_candidate={value}")
    print("  no endpoint, predicate, source quote, candidate, mention or statement-count changes")
    print("  counts before:", json.dumps(before, sort_keys=True))
    print("  counts after: ", json.dumps(after, sort_keys=True))
    if not args.apply:
        print("DRY RUN ONLY; no files written. Use --apply to apply the classifications.")
        return

    require(not BACKUP.exists(), f"backup already exists: {BACKUP.relative_to(ROOT)}")
    shutil.copy2(STATEMENTS, BACKUP)
    payload = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in updated) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=STATEMENTS.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, STATEMENTS)
    print(f"APPLIED; backup: {BACKUP.relative_to(ROOT)}")
    print(f"new SHA-256: {sha256(STATEMENTS)}")


if __name__ == "__main__":
    main()
