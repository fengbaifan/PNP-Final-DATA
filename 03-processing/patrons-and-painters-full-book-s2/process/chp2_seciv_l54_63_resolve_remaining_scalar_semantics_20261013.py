from __future__ import annotations

import argparse
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l54-63"
SEGMENT_SHA = "a045f0601ca2ce9cd4099916aa0cb20b60a811eafd3996f3849b2d7a422389e7"
SOURCE_SHA = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
BACKUP_SUFFIX = ".bak-s2-chp2-seciv-l54-63-scalar-semantics-20261013"
EXPECTED = {
    "book-statements.jsonl": "5fe4487804a0e157838d70aa976766426d2a7c06e02cd81826e62f23c923a65b",
    "s2-coverage.csv": "0439e723ba62672af1228dc0fe7a5b7a626a0a350f9b47e64cccf521ce5d5164",
}
UNSET_IDS = {
    "st-chp2-seciv-l54-63-barberini-palace-country-house-character",
    "st-chp2-seciv-l54-63-barberini-palace-departure-from-tradition",
    "st-chp2-seciv-l54-63-enzo-fond-of-art-and-adventurous-taste",
    "st-chp2-seciv-l54-63-enzo-post-created-by-pope",
    "st-chp2-seciv-l54-63-guido-fond-of-art-and-adventurous-taste",
    "st-chp2-seciv-l54-63-guido-made-cardinal-1621",
    "st-chp2-seciv-l54-63-guido-missions-shape-taste-and-writings",
    "st-chp2-seciv-l54-63-guido-nuncio-service-flanders-paris",
    "st-chp2-seciv-l54-63-guido-relative-austerity-life",
    "st-chp2-seciv-l54-63-new-era-periodization",
    "st-chp2-seciv-l54-63-palace-nearly-complete-1633",
    "st-chp2-seciv-l54-63-taddeo-disinterest-in-arts",
}
NEW_IDS = {
    "st-chp2-seciv-l54-63-guido-nuncio-service-paris",
    "st-chp2-seciv-l54-63-palace-decoration-underway-1633",
    "st-chp2-seciv-l54-63-taddeo-no-special-favourites",
    "st-chp2-seciv-l54-63-palace-facade-and-forecourt-description",
}
NEW_PARIS_ID = "st-chp2-seciv-l54-63-guido-nuncio-service-paris"
NEW_DECORATION_ID = "st-chp2-seciv-l54-63-palace-decoration-underway-1633"
NEW_TADDEO_FAVOURITES_ID = "st-chp2-seciv-l54-63-taddeo-no-special-favourites"
NEW_FACADE_ID = "st-chp2-seciv-l54-63-palace-facade-and-forecourt-description"
COUNTRY_HOUSE_QUOTE = (
    "From being a grim fortress, however grandiose, of the traditional type, the palace now turned into a light, "
    "welcoming country-house"
)
P47_DESIGN_PREFIX = "Maderno or—more likely—some brilliant collaborator or adviser departed completely from the"
DESIGN_QUOTE = (
    "Maderno or—more likely—some brilliant collaborator or adviser departed completely from the\n"
    "tradition of the sixteenth-century Roman palace."
)
FACADE_QUOTE = (
    "The courtyard was abandoned and replaced by a deep forecourt so that the main façade is approached through "
    "projecting wings at each end. This façade was then split up into seven bays of arcades three storeys high of "
    "which the bottom one forms an open loggia (Plate 9)."
)
ART_TASTE_QUOTE = "Both men were extremely fond of art, and showed a fine and adventurous taste."
ENZO_POST_QUOTE = (
    "Enzo served for a time as ‘ambassador’ from Ferrara to\n"
    "Rome—a post specially created by the Pope to satisfy local sensibilities."
)
CARDINAL_QUOTE = "In 1621 he was made Cardinal"
NUNCIO_QUOTE = "served as Nunzio in\nFlanders and Paris over the previous fourteen years"
MISSIONS_QUOTE = (
    "missions which strongly influenced his tastes and political sympathies and provided him with the material for "
    "his very popular historical writings."
)
AUSTERITY_QUOTE = "Indeed he surprised his friends at Court by the relative austerity of his Use"
NEW_ERA_QUOTE = "A new era had dawned."
COMPLETE_QUOTE = "By 1633—an astonishingly short time—the palace was virtually complete."
DECORATION_QUOTE = "Already the decoration was well under way."
TADDEO_ART_QUOTE = "Of all the Barberini, Taddeo was least interested in the arts."
TADDEO_FAVOURITES_QUOTE = (
    "Unlike his uncle and brothers he had no special favourites among the talented group of painters, sculptors and "
    "architects who were creating the new Baroque style."
)


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


def add_unique(values: list[str], additions: list[str]) -> list[str]:
    return list(dict.fromkeys([*values, *additions]))


def classify(row: dict, value: bool, note: str) -> dict:
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers["relation_candidate"] = value
    qualifiers["relation_candidate_note"] = note
    return qualifiers


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resolve the remaining one-endpoint and evaluative statements in CHP-2 section IV L54-63."
    )
    parser.add_argument("--apply", action="store_true", help="write after protected checks; default is preview")
    args = parser.parse_args()
    paths = {name: TABLES / name for name in EXPECTED}
    for name, expected in EXPECTED.items():
        actual = digest(paths[name])
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE) != SOURCE_SHA:
        raise SystemExit("protected section source asset changed")

    segment_by_id = {row["segment_id"]: row for row in read_jsonl(TABLES / "segments.jsonl")}
    segment = segment_by_id.get(SEGMENT_ID)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected print-p.48 source segment fingerprint changed")

    statements = read_jsonl(paths["book-statements.jsonl"])
    coverage = read_csv(paths["s2-coverage.csv"])
    statement_by_id = {row["statement_id"]: row for row in statements}
    if len(statement_by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"]
        for row in statements
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != UNSET_IDS:
        raise SystemExit(f"unexpected L54-63 unset statement set: {sorted(unset)}")
    if NEW_IDS & statement_by_id.keys():
        raise SystemExit(f"planned statement IDs already exist: {sorted(NEW_IDS & statement_by_id.keys())}")
    required = {
        "st-chp2-seciv-l54-63-enzo-ferrara-rome-ambassador",
        "st-chp2-seciv-l54-63-guido-career-in-church",
        "st-chp2-seciv-l54-63-guido-nuncio-service-flanders-paris",
        "st-chp2-seciv-l54-63-guido-missions-shape-taste-and-writings",
        "st-chp2-seciv-l54-63-guido-relative-austerity-life",
        "st-chp2-seciv-l54-63-barberini-supremacy-symbolized",
    }
    if required - statement_by_id.keys():
        raise SystemExit(f"required existing statements missing: {sorted(required - statement_by_id.keys())}")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    # The design sentence begins on p.47 L52 and resumes after the p.48 page marker at L55.
    if P47_DESIGN_PREFIX not in source_lines[51] or "tradition of the sixteenth-century Roman palace." not in source_lines[54]:
        raise SystemExit("protected cross-page palace-design quotation changed")
    for quote in (
        COUNTRY_HOUSE_QUOTE, FACADE_QUOTE, ART_TASTE_QUOTE, CARDINAL_QUOTE,
        MISSIONS_QUOTE, AUSTERITY_QUOTE, NEW_ERA_QUOTE, COMPLETE_QUOTE,
        DECORATION_QUOTE, TADDEO_ART_QUOTE, TADDEO_FAVOURITES_QUOTE,
    ):
        if quote not in "\n".join(source_lines):
            raise SystemExit(f"protected S0 quote no longer matches the source: {quote}")
    if NUNCIO_QUOTE not in "\n".join(source_lines) or ENZO_POST_QUOTE not in "\n".join(source_lines):
        raise SystemExit("protected cross-line diplomatic-service quotations changed")
    coverage_rows = [row for row in coverage if row.get("segment_id") == SEGMENT_ID]
    if len(coverage_rows) != 1:
        raise SystemExit("expected exactly one L54-63 coverage row")
    candidate_ids = {"cand-0240", "cand-0198", "cand-0290", "cand-0291", "cand-1479", "cand-4500", "cand-4652", "cand-4653", "cand-4656"}
    candidates = {row["candidate_id"] for row in read_csv(TABLES / "entity-candidates.csv")}
    if candidate_ids - candidates:
        raise SystemExit(f"required candidate IDs missing: {sorted(candidate_ids - candidates)}")

    country = statement_by_id["st-chp2-seciv-l54-63-barberini-palace-country-house-character"]
    country["original_quote"] = COUNTRY_HOUSE_QUOTE
    q = classify(country, False, "This is Haskell's architectural characterization of one building, not a relation to a separately identified entity.")
    q["claim"] = "Haskell describes the redesigned Barberini palace as a light, welcoming country house, contrasting it with a traditional grim fortress."
    q["qualification"] = "The contrast and welcoming character are Haskell's interpretation. The palace's size and the Roman-villa precedent are recorded in separate statements."
    q["mentioned_candidate_ids"] = ["cand-0240"]

    design = statement_by_id["st-chp2-seciv-l54-63-barberini-palace-departure-from-tradition"]
    design["original_quote"] = DESIGN_QUOTE
    dq = classify(design, False, "The attribution and departure from architectural tradition are Haskell's design assessment, not a supported relation between two identified entities.")
    dq["claim"] = "Haskell attributes the departure from sixteenth-century Roman palace tradition to Maderno or, more likely, an unnamed collaborator or adviser."
    dq["source_line_start"] = 52
    dq["source_line_end"] = 55
    dq["qualification"] = "The page break falls between 'the' and 'tradition'; the scan confirms the sentence continues on p.48. The source considers Maderno less likely and does not identify the collaborator. Physical design features are recorded separately."
    dq["mentioned_candidate_ids"] = ["cand-0240", "cand-1479"]
    dq["related_statement_ids"] = add_unique(dq.get("related_statement_ids", []), ["st-chp2-seciv-l45-52-barberini-new-palace-plan"])

    facade = {
        "statement_id": NEW_FACADE_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-0240",
        "object_candidate_id": None,
        "predicate": "architectural_features_reported",
        "qualifiers": {
            "source_line_start": 55, "source_line_end": 55,
            "claim": "Haskell says the palace replaced its courtyard with a deep forecourt and projecting wings; its three-storey arcade facade had seven bays and an open loggia on the lowest level.",
            "speaker": "Haskell", "text_layer": "authorial narrative",
            "print_page": 48, "pdf_physical_page": 33,
            "qualification": "These are architectural features of the Barberini palace, not separately identified entities.",
            "relation_candidate": False,
            "relation_candidate_note": "The statement describes attributes of a single building.",
            "mentioned_candidate_ids": ["cand-0240"],
        },
        "original_quote": FACADE_QUOTE,
        "origin": "book", "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }

    enzo_taste = statement_by_id["st-chp2-seciv-l54-63-enzo-fond-of-art-and-adventurous-taste"]
    enzo_taste["original_quote"] = ART_TASTE_QUOTE
    etq = classify(enzo_taste, False, "This records Haskell's characterization of Enzo's preferences, not a relation to an identified artwork or artist.")
    etq["claim"] = "Haskell says Enzo was extremely fond of art and had a fine, adventurous taste."
    etq["mentioned_candidate_ids"] = ["cand-0290"]

    post = statement_by_id["st-chp2-seciv-l54-63-enzo-post-created-by-pope"]
    post["object_candidate_id"] = None
    post["original_quote"] = ENZO_POST_QUOTE
    pq = classify(post, True, "Haskell explicitly says an unnamed Pope created the post Enzo served; retain the office as an open endpoint and do not infer the Pope's identity.")
    pq["claim"] = "Haskell says an unnamed Pope specially created the Ferrara-to-Rome ambassador post held by Enzo to satisfy local sensibilities."
    pq["source_line_start"] = 60
    pq["source_line_end"] = 61
    pq["open_endpoint_reason"] = "The created post is described through Enzo's Ferrara-to-Rome ambassadorship but is not given an independent entity record; the Pope remains cand-4656 and is not identified with cand-4655."
    pq["mentioned_candidate_ids"] = ["cand-0290", "cand-4656"]
    pq["related_statement_ids"] = add_unique(pq.get("related_statement_ids", []), ["st-chp2-seciv-l54-63-enzo-ferrara-rome-ambassador"])
    amb = statement_by_id["st-chp2-seciv-l54-63-enzo-ferrara-rome-ambassador"]
    aq = amb.setdefault("qualifiers", {})
    aq["related_statement_ids"] = add_unique(aq.get("related_statement_ids", []), [post["statement_id"]])

    guido_taste = statement_by_id["st-chp2-seciv-l54-63-guido-fond-of-art-and-adventurous-taste"]
    guido_taste["original_quote"] = ART_TASTE_QUOTE
    gtq = classify(guido_taste, False, "This records Haskell's characterization of Guido's preferences, not a relation to an identified artwork or artist.")
    gtq["claim"] = "Haskell says Guido was extremely fond of art and had a fine, adventurous taste."
    gtq["mentioned_candidate_ids"] = ["cand-0291"]

    cardinal = statement_by_id["st-chp2-seciv-l54-63-guido-made-cardinal-1621"]
    cardinal["original_quote"] = CARDINAL_QUOTE
    cq = classify(cardinal, True, "The source explicitly reports Guido's elevation to Cardinal; preserve the appointment as a relation candidate while leaving the unnamed authority and role endpoint open.")
    cq["claim"] = "Haskell says Guido was made Cardinal in 1621."
    cq["date"] = "1621"
    cq["open_endpoint_reason"] = "The passive sentence does not name the appointing authority, and Cardinal is a role rather than an independently identified entity here. Do not infer a Pope or a specific institution as endpoint."
    cq["mentioned_candidate_ids"] = ["cand-0291"]
    cq["related_statement_ids"] = add_unique(cq.get("related_statement_ids", []), ["st-chp2-seciv-l54-63-guido-career-in-church"])

    missions = statement_by_id["st-chp2-seciv-l54-63-guido-missions-shape-taste-and-writings"]
    missions["original_quote"] = MISSIONS_QUOTE
    mq = classify(missions, True, "Haskell explicitly attributes effects on Guido's tastes, political sympathies, and writings to his missions; keep the causal relation open because the individual missions and writings are not separately identified.")
    mq["claim"] = "Haskell says Guido's missions influenced his tastes and political sympathies and provided material for his historical writings."
    mq["open_endpoint_reason"] = "The claim refers collectively to the Flanders and Paris missions and to unnamed historical writings; no individual work or mission event is identified."
    mq["mentioned_candidate_ids"] = ["cand-0291", "cand-4652", "cand-4653"]
    mq["related_statement_ids"] = add_unique(mq.get("related_statement_ids", []), ["st-chp2-seciv-l54-63-guido-nuncio-service-flanders-paris", NEW_PARIS_ID])

    nunzio = statement_by_id["st-chp2-seciv-l54-63-guido-nuncio-service-flanders-paris"]
    nunzio["object_candidate_id"] = "cand-4652"
    nunzio["original_quote"] = NUNCIO_QUOTE
    nq = classify(nunzio, True, "The passage explicitly names Guido's Nunzio service in Flanders; the place and person are both represented by existing candidates.")
    nq["claim"] = "Haskell says Guido served as Nunzio in Flanders within the fourteen years before his elevation to Cardinal in 1621."
    nq["source_line_start"] = 59
    nq["source_line_end"] = 60
    nq["time_relation"] = "Within the fourteen years before the 1621 elevation; no separate dates or durations are given for the Flanders and Paris service."
    nq["mentioned_candidate_ids"] = ["cand-0291", "cand-4652"]
    paris = {
        "statement_id": NEW_PARIS_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-0291",
        "object_candidate_id": "cand-4653",
        "predicate": "nunciature_service_reported",
        "qualifiers": {
            "source_line_start": 59, "source_line_end": 60,
            "claim": "Haskell says Guido served as Nunzio in Paris within the fourteen years before his elevation to Cardinal in 1621.",
            "speaker": "Haskell", "text_layer": "authorial narrative",
            "print_page": 48, "pdf_physical_page": 33,
            "time_relation": "Within the fourteen years before the 1621 elevation; no separate dates or durations are given for the Flanders and Paris service.",
            "qualification": "The source uses the title 'Nunzio' and gives the two destinations together; it does not state separate appointment dates.",
            "relation_candidate": True,
            "relation_candidate_note": "The passage explicitly names Guido's Nunzio service in Paris; the place and person are both represented by existing candidates.",
            "mentioned_candidate_ids": ["cand-0291", "cand-4653"],
            "related_statement_ids": [nunzio["statement_id"], missions["statement_id"]],
        },
        "original_quote": NUNCIO_QUOTE,
        "origin": "book", "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }
    nq["related_statement_ids"] = add_unique(nq.get("related_statement_ids", []), [paris["statement_id"], missions["statement_id"]])
    mq["related_statement_ids"] = add_unique(mq.get("related_statement_ids", []), [nunzio["statement_id"], paris["statement_id"]])

    austerity = statement_by_id["st-chp2-seciv-l54-63-guido-relative-austerity-life"]
    austerity["original_quote"] = AUSTERITY_QUOTE
    aq = classify(austerity, False, "This is Haskell's characterization of Guido's lifestyle, not a relation to his unnamed friends or a separately identified work.")
    aq["claim"] = "Haskell says Guido surprised his friends at Court with the relative austerity of his life."
    aq["qualification"] = "The printed page reads 'life'; S0 OCR reads 'Use'. The sentence continues in the next segment, where Haskell explains the relative austerity."
    aq["mentioned_candidate_ids"] = ["cand-0291"]
    corrections = aq.setdefault("page_image_ocr_corrections", [])
    correction = {"source_line": 63, "ocr": "Use", "print": "life"}
    if correction not in corrections:
        corrections.append(correction)

    period = statement_by_id["st-chp2-seciv-l54-63-new-era-periodization"]
    period["subject_candidate_id"] = None
    period["original_quote"] = NEW_ERA_QUOTE
    eq = classify(period, False, "This is Haskell's rhetorical periodization; it does not identify a bounded event or a relation between entities.")
    eq["claim"] = "Haskell concludes, rhetorically, that a new era had dawned after describing the palace and Barberini supremacy."
    eq["related_statement_ids"] = add_unique(eq.get("related_statement_ids", []), ["st-chp2-seciv-l54-63-barberini-supremacy-symbolized"])

    complete = statement_by_id["st-chp2-seciv-l54-63-palace-nearly-complete-1633"]
    complete["original_quote"] = COMPLETE_QUOTE
    pcq = classify(complete, False, "This is a dated construction-status attribute of one building, not a relation between two entities.")
    pcq["claim"] = "Haskell says the Barberini palace was virtually complete by 1633."
    pcq["date"] = "1633"
    pcq["qualification"] = "The source says 'virtually complete', not fully complete; decoration was already well under way and is recorded separately."
    pcq["mentioned_candidate_ids"] = ["cand-0240"]
    pcq["related_statement_ids"] = add_unique(pcq.get("related_statement_ids", []), [NEW_DECORATION_ID])
    decoration = {
        "statement_id": NEW_DECORATION_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-0240", "object_candidate_id": None,
        "predicate": "decoration_progress_reported",
        "qualifiers": {
            "source_line_start": 56, "source_line_end": 56,
            "claim": "Haskell says the palace decoration was already well under way by the time the palace was virtually complete in 1633.",
            "speaker": "Haskell", "text_layer": "authorial narrative",
            "print_page": 48, "pdf_physical_page": 33, "date": "1633",
            "qualification": "The date is inherited from the immediately preceding sentence; no start date or completion date for the decoration is supplied.",
            "relation_candidate": False,
            "relation_candidate_note": "This is a dated progress attribute of the palace, not a relation to a separately identified decoration event or entity.",
            "mentioned_candidate_ids": ["cand-0240"],
            "related_statement_ids": [complete["statement_id"]],
        },
        "original_quote": DECORATION_QUOTE,
        "origin": "book", "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }
    pcq["related_statement_ids"] = add_unique(pcq.get("related_statement_ids", []), [decoration["statement_id"]])

    taddeo = statement_by_id["st-chp2-seciv-l54-63-taddeo-disinterest-in-arts"]
    taddeo["original_quote"] = TADDEO_ART_QUOTE
    tq = classify(taddeo, False, "This is Haskell's comparative characterization of Taddeo's interests, not an entity relation.")
    tq["claim"] = "Haskell says Taddeo was the least interested in the arts among the Barberini."
    tq["mentioned_candidate_ids"] = ["cand-0239"]
    no_favourites = {
        "statement_id": NEW_TADDEO_FAVOURITES_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-0239", "object_candidate_id": None,
        "predicate": "no_special_artist_favourites_reported",
        "qualifiers": {
            "source_line_start": 57, "source_line_end": 57,
            "claim": "Haskell says Taddeo had no special favourites among the painters, sculptors, and architects creating the new Baroque style.",
            "speaker": "Haskell", "text_layer": "authorial narrative",
            "print_page": 48, "pdf_physical_page": 33,
            "qualification": "This is Haskell's characterization. The artists are an unnamed group; the Baroque-style candidate is contextual, not a named group endpoint.",
            "relation_candidate": False,
            "relation_candidate_note": "The statement reports Taddeo's stated lack of artistic favourites but identifies no particular artist as an endpoint.",
            "mentioned_candidate_ids": ["cand-0239", "cand-4500"],
            "related_statement_ids": [taddeo["statement_id"]],
        },
        "original_quote": TADDEO_FAVOURITES_QUOTE,
        "origin": "book", "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }
    tq["related_statement_ids"] = add_unique(tq.get("related_statement_ids", []), [no_favourites["statement_id"]])

    statements.extend([facade, paris, decoration, no_favourites])
    remaining = {
        row["statement_id"] for row in statements
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if remaining:
        raise SystemExit(f"section IV L54-63 still has unset relation_candidate values: {sorted(remaining)}")

    coverage_row = coverage_rows[0]
    note = (
        " 本轮闭合12条旧unset，并细分四项：立面/前庭特征、Paris使节任职、装饰进度、Taddeo无特别偏爱的群体。"
        "Guido晋升Cardinal、外交任职经历对其兴趣与写作的影响、未具名Pope创设Enzo所任岗位均保留为关系候选；缺失的任命者、使命/作品或岗位端点明确留空。"
        "艺术偏好、建筑属性、建造状态及作者时代判断标为非关系。页图确认L63 OCR 'Use'应读作'life'；S0未改，脚注1-4的正文回链仍指向L210-213。"
    )
    if note.strip() not in coverage_row["note"]:
        coverage_row["note"] = coverage_row["note"].rstrip() + note

    updated = {"book-statements.jsonl": statements, "s2-coverage.csv": coverage}
    payloads = {name: serialize(name, data) for name, data in updated.items()}
    result = {
        "mode": "apply" if args.apply else "preview",
        "segment": SEGMENT_ID,
        "closed_unset_ids": sorted(UNSET_IDS),
        "classification_counts": {"true": 5, "false": 11},
        "new_statements": sorted(NEW_IDS),
        "new_candidates": 0, "new_mentions": 0,
        "open_endpoint_statements": [
            "st-chp2-seciv-l54-63-enzo-post-created-by-pope",
            "st-chp2-seciv-l54-63-guido-made-cardinal-1621",
            "st-chp2-seciv-l54-63-guido-missions-shape-taste-and-writings",
        ],
        "source_asset_unchanged": True,
        "remaining_unset_in_segment": [],
        "payload_sha256": {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temps: dict[str, Path] = {}
    try:
        for name, payload in payloads.items():
            path = paths[name]
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
            backups[name] = backup
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
                temp = Path(handle.name)
                handle.write(payload)
            temps[name] = temp
        for name, temp in temps.items():
            os.replace(temp, paths[name])
        written = read_jsonl(paths["book-statements.jsonl"])
        written_by_id = {row["statement_id"]: row for row in written}
        if written_by_id[NEW_PARIS_ID].get("segment_id") != SEGMENT_ID:
            raise SystemExit("a planned statement was not persisted")
        if written_by_id["st-chp2-seciv-l54-63-guido-nuncio-service-paris"].get("object_candidate_id") != "cand-4653":
            raise SystemExit("the Paris nunciature relation was not persisted")
        if written_by_id["st-chp2-seciv-l54-63-guido-made-cardinal-1621"].get("qualifiers", {}).get("open_endpoint_reason") is None:
            raise SystemExit("the open Cardinal-appointment endpoint was not persisted")
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
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
