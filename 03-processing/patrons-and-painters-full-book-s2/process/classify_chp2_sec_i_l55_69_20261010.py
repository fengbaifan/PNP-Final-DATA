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
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp2-sec-i-l55-69-20261010"
SEGMENT_ID = "chp-2:02_CHP-2_sec_i:l55-69"
SOURCE_FILE = "02-sources/02-Markdown/02_CHP-2_sec_i.md"

EXPECTED_HASHES = {
    "04-knowledge/tables/book-statements.jsonl": "f731566ab90fa1390bc941bf86f067f10da4615b9449a79b01375ae6c9f0bd3a",
    "04-knowledge/tables/entity-candidates.csv": "b214ec44c825690db146c4efdcb96e1de4acbbc5d682104ec0c35535d53b2dae",
    "04-knowledge/tables/mentions.csv": "e6179e8cf85a5313d16bad9b24a2d7a529b6d368a39ff6339270181f084888ad",
    "04-knowledge/tables/s2-coverage.csv": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SOURCE_FILE: "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6",
}

DECISIONS = {
    "st-chp2-seci-l55-69-barocci-altarpiece": (False, "This is Haskell's attributed account of Maffeo's assessment that Barocci was too old for an altarpiece; the passage does not state that an altarpiece was commissioned. The separate request for a private-apartment picture is recorded independently."),
    "st-chp2-seci-l55-69-barocci-picture-request": (True, "Maffeo explicitly implores Barocci to send a picture for his private apartments; preserve this as a request, not evidence that a picture was sent or painted."),
    "st-chp2-seci-l55-69-bees-emblem": (True, "Haskell directly says Maffeo used bees as his emblem and attributes them to the French royal arms; the heraldic origin remains this book's claim."),
    "st-chp2-seci-l55-69-chapel-fashion": (True, "The passage directly associates Maffeo with the early adoption of the described chapel fashion; retain the comparison and evaluative wording as Haskell's account."),
    "st-chp2-seci-l55-69-chapel-work-continued": (True, "Haskell directly reports that Maffeo continued decorating his chapel while in Paris; no completion date is inferred."),
    "st-chp2-seci-l55-69-clement-special-patron": (True, "Haskell explicitly calls Clement VIII Maffeo's special patron; the passage does not say Clement made the later cardinal appointment."),
    "st-chp2-seci-l55-69-cupola-fresco-commission": (True, "The passive wording says Passignani was commissioned to paint the named cupola frescoes; the commissioning agent remains unnamed."),
    "st-chp2-seci-l55-69-cupola-proposal": (True, "Passignani directly proposed the cupola's mosaic and gilt-stucco scheme; preserve that it was a proposal and do not infer execution."),
    "st-chp2-seci-l55-69-decoration-assessment": (True, "The passage directly says Maffeo took a personal interest in his chapel decoration; preserve Haskell's later quality and colour assessments as attributed evaluation."),
    "st-chp2-seci-l55-69-french-backing-cardinal": (True, "Haskell attributes strong backing for Maffeo's cardinal promotion to an unspecified French collective; do not resolve its members or treat it as a named institution."),
    "st-chp2-seci-l55-69-henri-silver-service": (True, "The embedded quotation attributes a silver-gilt service to Henri IV's gift to Maffeo; retain the approximate weight and transmitted-quotation status."),
    "st-chp2-seci-l55-69-henri-visit": (True, "Haskell directly reports Maffeo's earlier visit to congratulate Henri IV; preserve the relative date and unidentified son."),
    "st-chp2-seci-l55-69-joint-palace-purchase": (True, "The source says Maffeo joined his brother Carlo in buying and furnishing the palace; retain Carlo as co-actor and keep this building distinct from the nearby Farnese reference."),
    "st-chp2-seci-l55-69-lunette-scenes": (True, "Haskell directly attributes the lunette canvases and frescoes to Passignani; 'his masterpieces' remains the author's evaluation."),
    "st-chp2-seci-l55-69-nuncio-appointment": (True, "The source directly reports Maffeo's appointment as Apostolic Nunzio in Paris; the appointing authority is unnamed and Paris remains the candidate's stated location."),
    "st-chp2-seci-l55-69-paris-political-outlook": (True, "Haskell explicitly attributes Maffeo's political outlook to his three years in Paris; retain this as an authorial causal interpretation of the Paris stay, not an independently verified effect of the city as an actor."),
    "st-chp2-seci-l55-69-passignani-selected": (True, "After the Barocci passage, Haskell says Maffeo turned instead to his compatriot Passignani; preserve this as a reported artist-selection relation, not proof every proposed decoration was executed."),
    "st-chp2-seci-l55-69-paul-michelangelo-plan": (True, "Haskell says Maffeo argued against Paul V's intention to alter Michelangelo's plan for St Peter's; preserve the argument and unfinished cross-segment sentence without inferring who proposed the nave."),
    "st-chp2-seci-l55-69-rome-return-wealth": (True, "The source reports Maffeo's return to Rome with great riches and gives a quoted gift account; keep Haskell's generalization about nuncios separate from the individual claim."),
    "st-chp2-seci-l55-69-style-continuation": (True, "The opening 'basilica' completes the prior segment's statement that Paul V adopted the marble practice at S. Maria Maggiore; retain the cross-segment link without treating it as a second independent event."),
    "st-chp2-seci-l55-69-welcome-in-france": (True, "The source locates the reported welcome on Maffeo's return in France; preserve France as event location only and do not infer unnamed welcoming agents."),
    "st-chp2-seci-l55-69-zeno-testimony": (False, "This records Renier Zeno's quoted characterization of Maffeo, not a direct social or institutional relation between the ambassador and Maffeo. Preserve the testimony and its source attribution."),
}

EXPECTED_ROWS = {
    "st-chp2-seci-l55-69-barocci-altarpiece": ("cand-3104", "cand-0247", "altarpiece_considered", 56, 57, "reluctantly compelled to admit that Federico"),
    "st-chp2-seci-l55-69-barocci-picture-request": ("cand-3104", "cand-0247", "picture_requested_subject_unspecified", 57, 58, "implored the artist to send him a picture"),
    "st-chp2-seci-l55-69-bees-emblem": ("cand-3104", "cand-4262", "emblem_adoption_and_origin_claimed", 66, 66, "as his emblem, the bees from the French royal coat of arms"),
    "st-chp2-seci-l55-69-chapel-fashion": ("cand-3104", "cand-4252", "chapel_style_adoption_and_scale", 56, 56, "among the first to follow the fashion"),
    "st-chp2-seci-l55-69-chapel-work-continued": ("cand-3104", "cand-4252", "chapel_decoration_continued_from_paris", 68, 68, "continued, while in Paris, with the decoration of his chapel"),
    "st-chp2-seci-l55-69-clement-special-patron": ("cand-0031", "cand-3104", "special_patron_reported", 65, 66, "his special patron Clement VIII"),
    "st-chp2-seci-l55-69-cupola-fresco-commission": ("cand-1857", "cand-4259", "commissioned_to_paint_reported", 60, 61, "commissioned to cover it with frescoes"),
    "st-chp2-seci-l55-69-cupola-proposal": ("cand-1857", "cand-4258", "decoration_proposed", 59, 59, "Passignani proposed that the cupola should be adorned"),
    "st-chp2-seci-l55-69-decoration-assessment": ("cand-3104", "cand-4252", "personal_interest_and_authorial_assessment", 56, 56, "Barberini took a deep personal interest in the decoration"),
    "st-chp2-seci-l55-69-french-backing-cardinal": ("cand-4267", "cand-3104", "backing_for_cardinal_promotion_reported", 65, 65, "strong backing from the French"),
    "st-chp2-seci-l55-69-henri-silver-service": ("cand-1295", "cand-4261", "silver_service_gift_reported", 66, 66, "quatte cens marcs, duquel nous [Henri IV] luy avoirs faict dons"),
    "st-chp2-seci-l55-69-henri-visit": ("cand-3104", "cand-1295", "short_visit_to_congratulate", 63, 64, "paid a short visit some years earlier to congratulate"),
    "st-chp2-seci-l55-69-joint-palace-purchase": ("cand-3104", "cand-4272", "joint_purchase_and_furnishing_reported", 68, 68, "joined with his brother Carlo in buying and furnishing a palace"),
    "st-chp2-seci-l55-69-lunette-scenes": ("cand-1857", "cand-4260", "painted_lunette_cycle_reported", 61, 61, "painted the canvases and frescoes in the lunettes"),
    "st-chp2-seci-l55-69-nuncio-appointment": ("cand-3104", "cand-3955", "appointed_to_diplomatic_post", 62, 63, "was appointed Apostolic"),
    "st-chp2-seci-l55-69-paris-political-outlook": ("cand-3104", "cand-3955", "authorial_causal_interpretation", 65, 65, "three years there proved immensely important"),
    "st-chp2-seci-l55-69-passignani-selected": ("cand-3104", "cand-1857", "artist_selected_for_chapel", 58, 59, "turned to his compatriot, Domenico Passignani"),
    "st-chp2-seci-l55-69-paul-michelangelo-plan": ("cand-3104", "cand-3135", "opposition_to_proposed_plan_change", 68, 69, "argued with the greatest cogency against Paul"),
    "st-chp2-seci-l55-69-rome-return-wealth": ("cand-3104", "cand-3126", "return_and_wealth_reported", 66, 66, "he returned to Rome a year later"),
    "st-chp2-seci-l55-69-style-continuation": ("cand-0393", "cand-3131", "style_adoption_site_continued", 56, 56, "basilica. Maffeo Barberini was"),
    "st-chp2-seci-l55-69-welcome-in-france": ("cand-3104", "cand-4266", "return_welcomed", 64, 64, "his return was warmly welcomed in France"),
    "st-chp2-seci-l55-69-zeno-testimony": ("cand-4265", "cand-3104", "ambassadorial_characterization", 66, 67, "a Venetian ambassador was to write"),
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
        "relation_true": 3920,
        "relation_false": 1808,
        "true_bilateral": 3893,
        "true_open": 27,
        "false_bilateral": 443,
        "unclassified_bilateral": 4161,
    }, "current statement totals changed")
    return rows, before


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify 22 bilateral statements in chapter 2 section i L55-69.")
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
