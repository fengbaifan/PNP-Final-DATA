from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_iv.md"
SEGMENTS = TABLES / "segments.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SEGMENT_ID = "chp-3:03_CHP-3_sec_iv:l118-128"
SOURCE_SHA = "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed"
SEGMENT_SHA = "b0a7eafc09652842025f6c147dc288c7750ffb7ef2f5af0b8ee0ec1963980746"
PRE_HASHES = {
    STATEMENTS.name: "4221567c2174b9a8acef76857a4854db11af2ac3a170b34e66e08a16b486e71a",
    CANDIDATES.name: "eea883489b7d37451a404cdb35497e79ac10822e5aef95e9f652723ebb2e84d1",
    MENTIONS.name: "624a7e0369c5c2653e560796acc0fa322458e93ed1c99c4469c0e5635ec56f08",
}
BACKUP_SUFFIX = ".bak-s2-chp3-seciv-l118-128-relations-20261011"


RELATION_NOTES = {
    "biographical-story-collected-alms": "The attributed anecdote says Pozzo went through Rome collecting alms; no date or individual alms recipient is inferred.",
    "biographical-story-forty-hours-preparations": "The biographers' anecdote connects Jesuit superiors' planned Forty Hours spectacle with the proposed economy in stage sets; it is not treated as an independently verified event.",
    "biographical-story-humble-duties": "The attributed account says Pozzo accepted ordinary lay duties assigned by his Jesuit superiors; no specific office or task is supplied.",
    "biographical-story-pozzo-offered-apparatus": "The attributed anecdote says Pozzo offered to construct the stage apparatus from rags and used canvas; the story is not independently verified.",
    "brandi-christ-veronica-proposed": "Records negotiations over the proposed Christ and St Veronica picture; it does not establish execution or installation.",
    "brandi-flagellation-proposed": "Records negotiations over the proposed Flagellation picture; it does not establish execution or installation.",
    "brandi-negotiations-prolonged": "Haskell says Brandi's negotiations to decorate the Chapel of the Passion were prolonged and difficult; no agreement or completed work is inferred.",
    "brandi-pieta-proposed": "Records negotiations over the proposed Pietà picture; it does not establish execution or installation.",
    "cardinal-ottoboni-nephew-of-alexander-viii": "The source explicitly identifies Cardinal Ottoboni as Pope Alexander VIII's nephew; the two Ottoboni candidates remain distinct.",
    "death-altarpiece-for-dedicated-altar": "The source says the altarpiece was painted for the altar dedicated to St Francis Xavier; this does not establish its surviving or current installation.",
    "gaulli-painted-death-of-xavier-1676": "Records Haskell's attribution of the 1676 painting to Gaulli; the separately cited archival item has not been independently consulted.",
    "gaulli-painted-two-further-scenes": "Haskell reports two further scenes by Gaulli for the same chapel after financial disputes; neither titles nor individual subjects are supplied.",
    "heirs-reserved-and-exercised-right-to-change-decor": "Haskell reports that the unidentified heirs reserved and later exercised the right to change the chapel decoration; no broader ownership claim is inferred.",
    "jesuit-document-complained-affatto-rustica": "Haskell attributes the 1691 'affatto rustica' complaint to an unidentified Jesuit document; the archival document has not been independently consulted.",
    "madonna-chapel-last-to-be-adorned": "Records the chapel's reported dedication to the Madonna and its place as the last chapel to be adorned; no title or current condition is inferred.",
    "maratta-delivered-stanislas-altarpiece": "Haskell says Carlo Maratta took eight years to deliver the altarpiece; no commission date or exact delivery date is inferred.",
    "oliva-showed-pozzo-paintings-to-maratta": "Records Oliva's reported showing of Pozzo's unidentified paintings to Carlo Maratta; no specific titles are inferred.",
    "oliva-summoned-pozzo-to-rome-1680": "Haskell says Oliva summoned Pozzo to Rome in 1680 to address S. Ignazio's condition; the reported purpose is retained without inferring a commission for a particular work.",
    "ottoboni-commissioned-three-david-altarpieces": "Records Cardinal Ottoboni's commission from Ludovico David for three named altarpieces; completion and present location are not asserted.",
    "ottoboni-paid-from-prince-funds": "Haskell says Ottoboni paid for the three altarpieces from funds left by Prince Pamfili; this does not assert a direct payment by the deceased Prince or identify the legal recipient of the funds.",
    "ottoboni-took-over-madonna-chapel": "Records Haskell's statement that Cardinal Ottoboni took over the Madonna chapel; the precise legal or administrative status is not specified.",
    "pozzo-arrived-after-unhurried-journey-oliva-dead": "The preceding sentence places Pozzo's order in Rome; Haskell says he arrived after an unhurried journey. This records the destination without linking Pozzo to Oliva as an actor.",
    "pozzo-born-in-trent": "The source explicitly gives Trent as Pozzo's birthplace; geographic normalization is left to S3.",
    "pozzo-decorated-jesuit-churches-turin-mondovi": "Haskell says Pozzo decorated an unspecified group of Jesuit churches, notably in Turin and Mondovi; individual churches and their count are unknown.",
    "pozzo-described-as-talented-jesuit": "The sentence explicitly identifies Pozzo as a Jesuit while evaluating his talent; the appraisal remains Haskell's, and the institutional membership is also stated in the following claim.",
    "pozzo-entered-jesuits-as-laybrother-at-22": "Records the source's statement that Pozzo entered the Society as a laybrother at age 22; no exact calendar year is inferred.",
    "pozzo-ordered-to-rome-on-maratta-advice": "Haskell says Pozzo was ordered to Rome on Maratta's advice; the ordering authority is not named and is not supplied as an endpoint.",
    "pozzo-paintings-reached-oliva": "Haskell reports that some unidentified Pozzo paintings had reached Oliva; this does not establish acquisition or ownership.",
    "s-ignazio-remaining-large-problem": "Haskell frames S. Ignazio's decorative state as a remaining problem facing the Jesuits; this is an authorial project association, not proof of a formal commission.",
}

NONRELATION_NOTES = {
    "biographers-recounted-pozzo-story": "This evaluates the story's appeal to eighteenth-century biographers; no specific biographer, source, or entity-to-entity relation is identified.",
    "church-opened-twenty-one-years-before-1691": "This is a single-place chronological claim about the church's public opening, not a relation between two entities.",
    "gaulli-equally-obvious-choice": "This is Haskell's evaluative description of Gaulli as a choice, with no identified choosing actor or distinct commission relation.",
    "gaulli-paid-100-scudi": "This reports a scalar payment amount without naming the payer; the amount is retained in the claim and is not treated as an entity relation.",
    "jesuit-church-decoration-status": "The sentence coordinates the decoration status of the Gesù and S. Andrea; it does not state a relation between the two churches.",
    "oliva-ambitions-must-have-seemed-fulfilled": "This is Haskell's qualified inference about Oliva's apparent ambitions, not an established relation between Oliva and Pozzo.",
    "pozzo-compared_to_new_borgognone": "This is a metaphorical comparison, not a historical relation between Pozzo and Borgognone.",
    "pozzo-faced-many-difficulties": "This is a single-person status claim and supplies no counterpart for a relation.",
    "pozzo-perspective-effects": "This is a descriptive appraisal of perspective effects without an identified artwork or building endpoint.",
    "pozzo-success-in-north-italy": "This is a broad evaluative claim about success in a region, not a specific relation to North Italy.",
    "s-ignazio-open-since-1642": "This is a date/status claim about one church, not a directed relation.",
    "s-ignazio-white-mausoleum-evaluation": "This is Haskell's architectural evaluation of one church, not a relation to the other churches used for comparison.",
    "success-story-compared-to-fairy-tales": "This is an explicit literary comparison, not a historical relation between Pozzo and fairy tales.",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> tuple[list[dict], bytes]:
    raw = path.read_bytes()
    return [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()], raw


def read_csv(path: Path) -> tuple[list[str], list[dict], str, bool, bytes]:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in text else "\n"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader.fieldnames or []), list(reader), eol, bom, raw


def encode_jsonl(rows: list[dict], eol: str, bom: bool) -> bytes:
    text = eol.join(json.dumps(row, ensure_ascii=False) for row in rows) + eol
    return (("\ufeff" if bom else "") + text).encode("utf-8")


def encode_csv(fields: list[str], rows: list[dict], eol: str, bom: bool) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="raise", lineterminator=eol)
    writer.writeheader()
    writer.writerows(rows)
    return (("\ufeff" if bom else "") + output.getvalue()).encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after the dry-run preconditions pass")
    args = parser.parse_args()

    source_bytes = SOURCE.read_bytes()
    if sha(source_bytes) != SOURCE_SHA:
        raise SystemExit("source file hash changed")
    segment_rows = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = [x for x in segment_rows if x.get("segment_id") == SEGMENT_ID]
    if len(segment) != 1 or segment[0].get("sha256") != SEGMENT_SHA:
        raise SystemExit("normalized segment hash changed or is ambiguous")
    coverage_rows = list(csv.DictReader(COVERAGE.open(encoding="utf-8-sig", newline="")))
    coverage = [x for x in coverage_rows if x.get("segment_id") == SEGMENT_ID]
    if len(coverage) != 1 or coverage[0].get("disposition") != "reviewed" or coverage[0].get("migration_status") != "complete":
        raise SystemExit("unexpected segment coverage state")

    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        actual = sha(path.read_bytes())
        expected = PRE_HASHES[path.name]
        if actual != expected:
            raise SystemExit(f"unexpected {path.name} hash: {actual} != {expected}")

    statement_rows, statement_raw = read_jsonl(STATEMENTS)
    candidate_fields, candidate_rows, candidate_eol, candidate_bom, _ = read_csv(CANDIDATES)
    mention_fields, mention_rows, mention_eol, mention_bom, _ = read_csv(MENTIONS)
    expected_ids = {
        "biographers-recounted-pozzo-story", "biographical-story-collected-alms",
        "biographical-story-forty-hours-preparations", "biographical-story-humble-duties",
        "biographical-story-pozzo-offered-apparatus", "brandi-christ-veronica-proposed",
        "brandi-flagellation-proposed", "brandi-negotiations-prolonged", "brandi-pieta-proposed",
        "cardinal-ottoboni-nephew-of-alexander-viii", "church-opened-twenty-one-years-before-1691",
        "death-altarpiece-for-dedicated-altar", "gaulli-equally-obvious-choice", "gaulli-paid-100-scudi",
        "gaulli-painted-death-of-xavier-1676", "gaulli-painted-two-further-scenes",
        "heirs-reserved-and-exercised-right-to-change-decor", "jesuit-church-decoration-status",
        "jesuit-document-complained-affatto-rustica", "madonna-chapel-last-to-be-adorned",
        "maratta-delivered-stanislas-altarpiece", "oliva-ambitions-must-have-seemed-fulfilled",
        "oliva-showed-pozzo-paintings-to-maratta", "oliva-summoned-pozzo-to-rome-1680",
        "ottoboni-commissioned-three-david-altarpieces", "ottoboni-paid-from-prince-funds",
        "ottoboni-took-over-madonna-chapel", "pozzo-arrived-after-unhurried-journey-oliva-dead",
        "pozzo-born-in-trent", "pozzo-compared_to_new_borgognone",
        "pozzo-decorated-jesuit-churches-turin-mondovi", "pozzo-described-as-talented-jesuit",
        "pozzo-entered-jesuits-as-laybrother-at-22", "pozzo-faced-many-difficulties",
        "pozzo-ordered-to-rome-on-maratta-advice", "pozzo-paintings-reached-oliva",
        "pozzo-perspective-effects", "pozzo-success-in-north-italy", "s-ignazio-open-since-1642",
        "s-ignazio-remaining-large-problem", "s-ignazio-white-mausoleum-evaluation",
        "success-story-compared-to-fairy-tales",
    }
    target_prefix = "st-chp3-seciv-l118-128-"
    segment_statements = [x for x in statement_rows if x.get("segment_id") == SEGMENT_ID]
    found_ids = {x["statement_id"][len(target_prefix):] for x in segment_statements if x["statement_id"].startswith(target_prefix)}
    if len(segment_statements) != 42 or found_ids != expected_ids:
        raise SystemExit(f"unexpected segment statements: {len(segment_statements)} rows; missing={sorted(expected_ids-found_ids)} extra={sorted(found_ids-expected_ids)}")
    if set(RELATION_NOTES) & set(NONRELATION_NOTES) or set(RELATION_NOTES) | set(NONRELATION_NOTES) != expected_ids:
        raise SystemExit("classification maps do not cover the segment exactly once")
    if any(x.get("qualifiers", {}).get("relation_candidate") is not None for x in segment_statements if x["statement_id"].endswith("cardinal-ottoboni-nephew-of-alexander-viii") is False and x["statement_id"].endswith("pozzo-born-in-trent") is False):
        raise SystemExit("a statement in the target segment has already been classified")

    candidate_ids = {x.get("candidate_id") for x in candidate_rows}
    if "cand-11619" in candidate_ids:
        raise SystemExit("candidate cand-11619 already exists")
    all_statement_ids = {x.get("statement_id") for x in statement_rows}
    new_oliva_id = "st-chp3-seciv-l118-128-oliva-dead-by-pozzo-arrival"
    if new_oliva_id in all_statement_ids:
        raise SystemExit(f"new statement id already exists: {new_oliva_id}")
    if any(x.get("mention_id") == "m-chp3-seciv-l118-128-0058" for x in mention_rows):
        raise SystemExit("mention id m-chp3-seciv-l118-128-0058 already exists")

    for row in segment_statements:
        suffix = row["statement_id"][len(target_prefix):]
        q = row.setdefault("qualifiers", {})
        if suffix in RELATION_NOTES:
            q["relation_candidate"] = True
            q["relation_candidate_note"] = RELATION_NOTES[suffix]
        else:
            q["relation_candidate"] = False
            q["relation_candidate_note"] = NONRELATION_NOTES[suffix]

    statement_map = {x["statement_id"]: x for x in segment_statements}
    maratta = statement_map["st-chp3-seciv-l118-128-maratta-delivered-stanislas-altarpiece"]
    maratta["subject_candidate_id"] = "cand-1526"
    arrival_id = "st-chp3-seciv-l118-128-pozzo-arrived-after-unhurried-journey-oliva-dead"
    arrival = statement_map[arrival_id]
    arrival["object_candidate_id"] = "cand-4490"
    arrival["predicate"] = "arrived_in_rome_after_unhurried_journey"
    arrival["qualifiers"]["claim"] = "Haskell says Pozzo arrived in Rome after an unhurried journey; the preceding sentence says he had been ordered to Rome."
    arrival["qualifiers"]["qualification"] = "The sentence gives no ordering authority and does not state when Oliva died; Oliva's death is recorded separately as a temporal status claim."
    arrival["qualifiers"]["linked_body_statement_ids"] = ["st-chp3-seciv-l118-128-pozzo-ordered-to-rome-on-maratta-advice"]
    arrival["qualifiers"]["relation_candidate_note"] = RELATION_NOTES["pozzo-arrived-after-unhurried-journey-oliva-dead"]

    paintings = statement_map["st-chp3-seciv-l118-128-pozzo-paintings-reached-oliva"]
    paintings["subject_candidate_id"] = "cand-5360"
    paintings["object_candidate_id"] = "cand-1775"
    paintings["predicate"] = "unidentified_pozzo_paintings_reached_oliva"
    paintings["qualifiers"]["claim"] = "Haskell says some of Pozzo's unidentified paintings had reached Oliva, who showed them to Carlo Maratta."
    paintings["qualifiers"]["relation_candidate_note"] = RELATION_NOTES["pozzo-paintings-reached-oliva"]

    churches_id = "st-chp3-seciv-l118-128-pozzo-decorated-jesuit-churches-turin-mondovi"
    churches = statement_map[churches_id]
    churches["object_candidate_id"] = "cand-11619"
    churches["predicate"] = "decorated_unspecified_jesuit_church_group_at_turin_and_mondovi"
    churches["qualifiers"]["claim"] = "Haskell says Pozzo decorated several Jesuit churches, notably at Turin and Mondovi, with spectacular perspective effects."
    churches["qualifiers"]["qualification"] = "The source does not name the individual churches or give their count; Turin and Mondovi are the stated locations."
    churches["qualifiers"]["relation_candidate_note"] = RELATION_NOTES["pozzo-decorated-jesuit-churches-turin-mondovi"]

    mention_map = {x["mention_id"]: x for x in mention_rows}
    maratta_mention = mention_map.get("m-chp3-seciv-l118-128-0017")
    if not maratta_mention or maratta_mention.get("candidate_id") != "cand-1536" or maratta_mention.get("surface_form") != "Carlo Maratta":
        raise SystemExit("unexpected Carlo Maratta mention mapping")
    maratta_mention["candidate_id"] = "cand-1526"

    new_candidate = {
        "candidate_id": "cand-11619", "index_entry_id": "",
        "canonical_name": "Unspecified Jesuit churches decorated by Andrea Pozzo at Turin and Mondovi",
        "index_page_range": "", "suggested_type": "place", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Haskell reports that Pozzo decorated several Jesuit churches, notably at Turin and Mondovi, but identifies no individual church or count. This source-bounded group remains distinct from the Jesuit order; the named locations do not identify the specific buildings.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L126",
    }
    candidate_rows.append(new_candidate)
    new_mention = {
        "mention_id": "m-chp3-seciv-l118-128-0058", "segment_id": SEGMENT_ID,
        "candidate_id": "cand-11619", "surface_form": "several Jesuit churches",
        "start_char": "1895", "end_char": "1918",
        "note": "Source-bounded group of unnamed churches; Turin and Mondovi are locations, while individual identities and count remain unspecified.",
    }
    mention_rows.append(new_mention)

    new_oliva_death = {
        "statement_id": new_oliva_id, "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-1775", "object_candidate_id": None,
        "predicate": "reported_dead_when_pozzo_arrived_in_rome",
        "qualifiers": {
            "source_line_start": 126, "source_line_end": 126,
            "claim": "Haskell says Oliva was dead when Pozzo arrived in Rome after an unhurried journey.",
            "speaker": "Haskell", "text_layer": "authorial narrative",
            "print_page": 88, "pdf_physical_page": 30,
            "qualification": "This records the temporal status given by Haskell; the passage does not date Oliva's death or identify the authority that ordered Pozzo to Rome.",
            "linked_body_statement_ids": [arrival_id],
            "relation_candidate": False,
            "relation_candidate_note": "This is a single-person temporal status claim, not a relation between Oliva and Pozzo.",
        },
        "original_quote": "When he arrived after an unhurried journey, Oliva was dead.",
        "origin": "book", "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }
    statement_rows.append(new_oliva_death)

    if len(statement_rows) != 12810 or len(candidate_rows) != 11597 or len(mention_rows) != 27532:
        raise SystemExit("unexpected post-write table row counts")
    segment_after = [x for x in statement_rows if x.get("segment_id") == SEGMENT_ID]
    if len(segment_after) != 43 or any(x.get("qualifiers", {}).get("relation_candidate") is None for x in segment_after):
        raise SystemExit("segment classification completeness check failed")
    global_relations = sum(x.get("qualifiers", {}).get("relation_candidate") is True for x in statement_rows)
    bilateral = [x for x in statement_rows if x.get("subject_candidate_id") and x.get("object_candidate_id")]
    bilateral_rel = sum(x.get("qualifiers", {}).get("relation_candidate") is True for x in bilateral)
    bilateral_non = sum(x.get("qualifiers", {}).get("relation_candidate") is False for x in bilateral)
    bilateral_unclassified = len(bilateral) - bilateral_rel - bilateral_non
    if (len(bilateral), bilateral_rel, bilateral_non, bilateral_unclassified, global_relations) != (8608, 5107, 489, 3012, 5159):
        raise SystemExit("unexpected post-write relation classification totals")

    statement_eol = "\r\n" if b"\r\n" in statement_raw else "\n"
    statement_bom = statement_raw.startswith(b"\xef\xbb\xbf")
    prepared = {
        STATEMENTS: encode_jsonl(statement_rows, statement_eol, statement_bom),
        CANDIDATES: encode_csv(candidate_fields, candidate_rows, candidate_eol, candidate_bom),
        MENTIONS: encode_csv(mention_fields, mention_rows, mention_eol, mention_bom),
    }
    print("segment: 42 existing statements classified; 1 temporal claim split out")
    print("classification: 29 relation candidates; 14 nonrelations; 0 unclassified")
    print("endpoint corrections: Maratta person; Pozzo paintings -> Oliva; Pozzo -> unnamed church group; arrival -> Rome")
    print("candidates: 1 place group added; mentions: 1 added, 1 corrected")
    print(f"post totals: statements={len(statement_rows)} candidates={len(candidate_rows)} mentions={len(mention_rows)}")
    print(f"bilateral: total={len(bilateral)} relation={bilateral_rel} nonrelation={bilateral_non} unclassified={bilateral_unclassified}")
    print(f"relation_candidates_total={global_relations}")
    if not args.apply:
        print("DRY-RUN PASS; no files written")
        return

    backup_paths = {
        STATEMENTS: STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX),
        CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + BACKUP_SUFFIX),
        MENTIONS: MENTIONS.with_name(MENTIONS.name + BACKUP_SUFFIX),
    }
    if any(path.exists() for path in backup_paths.values()):
        raise SystemExit("a recovery copy already exists; refusing to overwrite")
    for path, backup in backup_paths.items():
        shutil.copy2(path, backup)
    temps: list[tuple[Path, Path]] = []
    try:
        for path, data in prepared.items():
            temp = path.with_name(path.name + ".tmp-write")
            if temp.exists():
                raise SystemExit(f"temporary output already exists: {temp.name}")
            temp.write_bytes(data)
            temps.append((temp, path))
        for temp, path in temps:
            os.replace(temp, path)
    except Exception:
        for temp, _ in temps:
            if temp.exists():
                temp.unlink()
        for path, backup in backup_paths.items():
            if backup.exists():
                shutil.copy2(backup, path)
        raise
    print("APPLY PASS")
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        print(f"post_sha256 {path.name} {sha(path.read_bytes())}")
    print("recovery copies:")
    for backup in backup_paths.values():
        print(backup.name)


if __name__ == "__main__":
    main()
