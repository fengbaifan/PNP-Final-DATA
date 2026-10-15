"""Review p.350 S2 statements and restore exact entity mention anchors.

Default execution is a no-write preview. Pass --apply to write after reviewing
the source and table hashes, quotations, classifications, and mention spans.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-14.pdf"
SEGMENT_ID = "chp-14:14_CHP-14_intro:l35-44"
SEGMENT_SHA256 = "0635d34a1ddf42d11780ea7d9b7dfc5fb3517d98014efd29485a68a47acf0cd5"
SOURCE_SHA256 = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
PDF_SHA256 = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"
STATEMENTS_SHA256 = "5c0eee6300f8a2cb4d1940d02cf9b7ea7f1ba42598b67a6cf9bf26ff014f7a8b"
CANDIDATES_SHA256 = "04d46ce85e3134b651fda1c796fa32678c73259d565c2f2a733865449621a32b"
MENTIONS_SHA256 = "f6b8386c87c9de9a0bc6ec6738abdad7285d6d9a9880d8cc87ffb12cfe9816a8"
BACKUP_SUFFIX = ".bak-s2-ch14-p350-semantic-review-20261014"
SOURCE_FILE = "02-sources/02-Markdown/14_CHP-14_intro.md"

NEW_CANDIDATES = [
    ("cand-12186", "Artists whose work was more appreciated in northern Europe than Venice (unnamed p.350 group)", "", "Haskell says indications suggest Algarotti drew inspiration from artists more appreciated in northern Europe than in his native city; the artists are not named.", 36),
    ("cand-12187", "Living artists in Venice during Algarotti's 1737 visit (unnamed group)", "", "Source-defined group scoped to Haskell's statement that there is no evidence of particular contact during the Venice visit beyond looking at their works.", 36),
    ("cand-12188", "Eighteenth-century collections of early-Italian artists' works discussed on p.350", "", "Haskell describes collections of early-Italian works as historical evidence and precursors of the Renaissance; individual collections and works are not identified here.", 40),
    ("cand-12189", "Scholarly historical approach to organizing an art gallery", "term", "The approach described by Haskell: represent the history of painting and its schools rather than organize a gallery solely around a collector's personal taste.", 39),
    ("cand-12190", "Works proposed for commission from living artists in the Dresden gallery scheme", "work", "An unspecified number of works proposed in Algarotti's plan; neither the works nor their creators are named, and the text does not say the commissions were executed.", 43),
    ("cand-12191", "Pictures containing many animals (Castiglione subject-type example)", "term", "A generalized subject type used by Haskell as an example of matching commissions to artists' specializations; no individual painting is identified.", 44),
    ("cand-12192", "Landscape pictures (Claude subject-type example)", "term", "A generalized subject type used by Haskell as an example of matching commissions to artists' specializations; no individual painting is identified.", 44),
    ("cand-12193", "Different Venetian artists appraised by Algarotti (unnamed group)", "", "Haskell refers collectively to the different Venetian artists whose work Algarotti appraised; the group is not enumerated on p.350.", 44),
    ("cand-12194", "Historical principles applied to large-scale art collecting", "term", "The historical method which Haskell says Algarotti applied to collecting art on a large scale; this is a source-specific conceptual object.", 41),
]

# surface form, candidate id, occurrence index in the assembled segment, note
MENTION_SPECS = [
    ("artists who were appreciated more in the north of Europe", "cand-12186", 0, "Unnamed source-defined group; the passage does not identify its members."),
    ("north of Europe", "cand-3594", 0, "Geographic phrase within Haskell's account of the unnamed artists."),
    ("his native city", "cand-2719", 0, "Haskell's contextual reference to Venice."),
    ("Berlin", "cand-9073", 0, "City named as the setting of the 1741 letter."),
    ("a portrait being painted of him", "cand-10264", 0, "Unidentified portrait; maker and location are not given."),
    ("Rembrandt", "cand-2117", 0, "Named as a comparison in Algarotti's reported letter."),
    ("Giorgione", "cand-1188", 0, "Named as a comparison in Algarotti's reported letter."),
    ("Venice", "cand-2719", 0, "City of the 1737 visit."),
    ("living artists", "cand-12187", 0, "Unnamed group scoped to the 1737 Venice visit."),
    ("Newtonianismo", "cand-10258", 0, "Short title mention of Newtonianismo per le Dame."),
    ("Voltaire", "cand-2791", 0, "Named friend."),
    ("London", "cand-1422", 0, "Place named in Haskell's social-success assessment."),
    ("Paris", "cand-4653", 0, "Place named in Haskell's social-success assessment."),
    ("Venice", "cand-2719", 1, "Place in which Haskell says Algarotti was not yet well known."),
    ("Dresden", "cand-0947", 0, "Location of the 1742 gallery plan."),
    ("Augustus of Saxony", "cand-0151", 0, "The ruler named as forming the gallery; same-identity alignment across local candidates remains for S3."),
    ("art gallery", "cand-9091", 0, "The Dresden Gallery identified in the adjacent plan statements; cross-page identity remains an S3 matter."),
    ("Algarotti", "cand-0075", 0, "Explicit subject of the proposal to replace personal taste with a historical outlook."),
    ("scholarly approach to art", "cand-12189", 0, "Haskell's description of the proposal's method."),
    ("first rediscovery of the primitives", "cand-10267", 0, "Haskell's interpretive label; the claim is not attributed to Algarotti himself."),
    ("those collections of the works of early-Italian artists", "cand-12188", 0, "Unnamed collections are retained as a source-defined group."),
    ("Romantics", "cand-10268", 0, "Later comparator in Haskell's explanation."),
    ("Renaissance", "cand-3578", 0, "Historical period named as the collections' precursor context."),
    ("Padre Lodoli", "cand-1411", 0, "Named owner of a comparable collection."),
    ("just such a collection", "cand-10269", 0, "The source refers to Lodoli's collection without listing its works on this page."),
    ("Algarotti", "cand-0075", 1, "Explicit subject of the Muratori and art-collecting claims."),
    ("Muratori", "cand-1717", 0, "Named historical example; no specific text or collaboration is stated."),
    ("a number of works by living artists", "cand-12190", 0, "Proposed works; execution is not asserted."),
    ("living artists", "cand-10270", 1, "Unnamed artists considered in the Dresden scheme; distinct from artists in Venice in 1737."),
    ("the artists concerned", "cand-10270", 0, "Unnamed artists within the gallery scheme."),
    ("Castiglione", "cand-0602", 0, "Named artist in a general subject-specialization example."),
    ("many animals", "cand-12191", 0, "Generalized subject type, not an identified painting."),
    ("Claude", "cand-0767", 0, "Named artist in a general subject-specialization example."),
    ("landscape", "cand-12192", 0, "Generalized subject type, not an identified painting."),
    ("Algarotti", "cand-0056", 2, "Explicit subject of the appraisal of Venetian artists; local identity remains separate pending S3."),
    ("different Venetian artists", "cand-12193", 0, "Unnamed group; no membership is inferred."),
]

EXPECTED_UNSET = {
    "st-chp14-p350-rococo-influence-context",
    "st-chp14-p350-no-evidence-of-living-artist-contact",
    "st-chp14-p350-importance-from-1742",
    "st-chp14-p350-scholarly-historical-approach",
    "st-chp14-p350-rediscovery-of-primitives",
    "st-chp14-p350-detailed-subjects-and-style-awareness",
    "st-chp14-p350-patron-subject-specialization",
    "st-chp14-p350-appraisal-of-venetian-artists",
}

NEW_STATEMENTS = [
    ("st-chp14-p350-social-success-london-paris", "Haskell describes Algarotti as a social success in London and Paris before his 1737 Venice visit.", "Haskell's assessment of social reception; it is not a relation to either city.", "social success in London and Paris", 36, False, "Algarotti", None, "social_reception_assessed", ["cand-0056", "cand-1422", "cand-4653"], "authorial biographical assessment"),
    ("st-chp14-p350-not-yet-published", "During the 1737 Venice visit, Haskell says Algarotti's Newtonianismo had not yet been published.", "The text gives publication status at this point in the narrative but no specific publication date.", "his Newtonianismo had not yet been published", 36, False, "Algarotti", None, "publication_status", ["cand-0056", "cand-10258"], "authorial biographical synthesis"),
    ("st-chp14-p350-not-known-in-venice", "During the 1737 Venice visit, Haskell says Algarotti was not well known in Venice.", "This is Haskell's assessment at this point in the narrative.", "he was not well known in\nVenice", 36, False, "Algarotti", None, "reputation_assessed_in_place", ["cand-0056", "cand-2719"], "authorial biographical synthesis"),
    ("st-chp14-p350-associations-not-yet-formed", "During the 1737 Venice visit, Haskell says Algarotti had not yet formed the powerful associations that later characterized and helped his career.", "The associates and institutions are unnamed; no people or organizations are inferred.", "he had not yet formed any of those powerful associations which were later to prove such a feature of his career and to be so very useful to him.", 37, False, "Algarotti", None, "career_context", ["cand-0056"], "authorial biographical synthesis"),
    ("st-chp14-p350-documentary-visibility-from-1742", "Haskell says Algarotti's activities as patron and critic are well documented from 1742 onward.", "This is Haskell's statement about documentary visibility, separate from his assessment of Algarotti's importance.", "from now on we are well informed about his activities as patron and critic.", 38, False, "Algarotti", None, "documentary_visibility", ["cand-0056"], "authorial periodization"),
    ("st-chp14-p350-proposal-interest-assessed", "Haskell calls Algarotti's proposals remarkably interesting.", "A critical evaluation by Haskell, not a relation between entities.", "His proposals are remarkably interesting.", 39, False, "Algarotti", None, "proposal_assessed", ["cand-0075"], "authorial evaluation"),
    ("st-chp14-p350-scholarly-approach-characteristic", "Haskell says the plan reveals a scholarly approach to art that would characterize Algarotti and his century.", "This is Haskell's interpretation; the century is not expanded into a separate entity.", "they reveal that scholarly approach to art which was to remain characteristic of him and his century.", 39, False, "Algarotti", None, "historical_approach_characterized", ["cand-0075", "cand-12189"], "authorial interpretation"),
    ("st-chp14-p350-collections-precursors-of-renaissance", "Haskell says the eighteenth-century collections of early-Italian works were regarded as valuable evidence and as precursors of the Renaissance.", "The passage refers to an unnamed class of collections; it does not list specific artists or works.", "because they were looked upon as valuable evidence and as precursors of the Renaissance.", 40, True, "Unnamed collections", "Renaissance", "regarded_as_evidence_and_precursors_of", ["cand-12188", "cand-3578"], "authorial historical interpretation"),
    ("st-chp14-p350-applied-historical-principles-large-scale", "Haskell says Algarotti was among the first to apply historians' principles to large-scale art collecting.", "The comparative priority claim is Haskell's; it does not identify a single text or a specific collection.", "he was among the first to apply their principles to the collecting of art on a large scale.", 41, True, "Algarotti", "historical principles applied to large-scale art collecting", "applied_historical_principles_to", ["cand-0075", "cand-12194"], "authorial interpretation"),
    ("st-chp14-p350-royal-master-saw-scheme-differently", "Haskell says the scheme's most interesting part to later readers was not how it appeared to Algarotti's royal master.", "The source does not state which part the royal master considered most important or why.", "though this is not how it appeared to his royal master", 42, False, "Dresden gallery scheme", "Augustus III", "royal_assessment_not_specified", ["cand-0072", "cand-0151"], "authorial interpretation of a plan"),
    ("st-chp14-p350-ahead-of-critical-opinion", "Haskell says Algarotti's proposed commissions were ahead of much critical opinion in his day.", "This is Haskell's comparative assessment, not evidence that the works were commissioned or completed.", "For here too he was in advance of much critical opinion in his day.", 43, False, "Algarotti", None, "critical_position_assessed", ["cand-0072", "cand-10270"], "authorial interpretation of a plan"),
    ("st-chp14-p350-stressed-literary-painter-contact", "Haskell says Algarotti stressed the importance of contact between the literary man and the painter.", "This is a statement about the importance Algarotti assigned to a mode of collaboration; no particular pair or collaboration is named.", "was always to stress the importance of contacts between the literary man and the painter", 43, False, "Algarotti", None, "collaboration_principle", ["cand-0072", "cand-10270"], "authorial interpretation of a plan"),
    ("st-chp14-p350-style-awareness-more-than-patrons", "Haskell says Algarotti showed greater awareness than most patrons of the artists' different styles.", "A comparative assessment of Algarotti's critical sensitivity.", "he showed far greater awareness than most patrons of their different styles", 43, False, "Algarotti", None, "style_awareness_assessed", ["cand-0072", "cand-10270"], "authorial interpretation of a plan"),
    ("st-chp14-p350-style-differences-guided-approach", "Haskell says differences among the artists' styles determined Algarotti's approach to the scheme.", "The statement concerns the proposed scheme and does not assert that each proposal was executed.", "these differences determined his approach.", 43, True, "Algarotti", "unnamed artists considered for the scheme", "tailored_approach_to_artists_styles", ["cand-0072", "cand-10270"], "authorial interpretation of a plan"),
    ("st-chp14-p350-pictures-for-castiglione", "Haskell gives pictures containing many animals as suitable subjects for Castiglione.", "A general subject-specialization example; no individual picture or commission is identified.", "a picture which could include many animals was suitable for Castiglione", 44, True, "Castiglione", "pictures containing many animals", "associated_with_subject_type", ["cand-0602", "cand-12191"], "authorial generalization with example"),
    ("st-chp14-p350-landscape-for-claude", "Haskell says landscape was essential to any picture ordered from Claude.", "A general subject-specialization example; no individual picture or commission is identified.", "landscape was an essential ingredient of any picture ordered from Claude.", 44, True, "Claude", "landscape pictures", "associated_with_subject_type", ["cand-0767", "cand-12192"], "authorial generalization with example"),
    ("st-chp14-p350-algarotti-appraised-venetian-artists", "Haskell says Algarotti appraised the different Venetian artists.", "The group is unnamed and not enumerated on this page; the assessment of its quality is recorded separately.", "appraisal of the different Venetian artists", 44, True, "Algarotti", "different Venetian artists", "appraised", ["cand-0056", "cand-12193"], "authorial interpretation"),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    return [json.loads(line) for line in lines if line.strip()], lines


def write_jsonl(path: Path, original_lines: list[str], rows: list[dict], changed: set[str]) -> bytes:
    by_id = {r["statement_id"]: r for r in rows}
    out, seen = [], set()
    for line in original_lines:
        if not line.strip():
            out.append(line)
            continue
        old = json.loads(line)
        sid = old["statement_id"]
        out.append(json.dumps(by_id[sid], ensure_ascii=False, separators=(",", ":")) if sid in changed else line)
        seen.add(sid)
    out.extend(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in rows if r["statement_id"] not in seen)
    return ("\n".join(out) + "\n").encode("utf-8")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader), raw.startswith(b"\xef\xbb\xbf")


def csv_bytes(fields: list[str], rows: list[dict[str, str]], bom: bool) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader(); writer.writerows(rows)
    data = out.getvalue().encode("utf-8")
    return b"\xef\xbb\xbf" + data if bom else data


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    expected_hashes = ((STATEMENTS, STATEMENTS_SHA256), (CANDIDATES, CANDIDATES_SHA256),
                       (MENTIONS, MENTIONS_SHA256), (SOURCE, SOURCE_SHA256), (PDF, PDF_SHA256))
    for path, expected in expected_hashes:
        actual = sha(path)
        if actual != expected:
            raise SystemExit(f"precondition failed: {path.relative_to(ROOT)} {actual} != {expected}")

    segment_rows = [json.loads(x) for x in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
    segment = next((x for x in segment_rows if x["segment_id"] == SEGMENT_ID), None)
    if segment is None:
        raise SystemExit(f"missing segment {SEGMENT_ID}")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    body = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if segment.get("sha256") != SEGMENT_SHA256 or hashlib.sha256(body.encode("utf-8")).hexdigest() != SEGMENT_SHA256:
        raise SystemExit("p.350 S0 segment hash mismatch")

    statement_rows, original_statement_lines = read_jsonl(STATEMENTS)
    by_id = {r["statement_id"]: r for r in statement_rows}
    if len(by_id) != len(statement_rows):
        raise SystemExit("statement IDs are not unique")
    page_rows = [r for r in statement_rows if r["segment_id"] == SEGMENT_ID]
    if len(page_rows) != 18:
        raise SystemExit(f"expected 18 existing p.350 statements, found {len(page_rows)}")
    if {sid for sid in EXPECTED_UNSET if sid in by_id and "relation_candidate" not in (by_id[sid].get("qualifiers") or {})} != EXPECTED_UNSET:
        raise SystemExit("the expected p.350 unset statement set changed")

    candidate_fields, candidate_rows, candidate_bom = read_csv(CANDIDATES)
    mention_fields, mention_rows, mention_bom = read_csv(MENTIONS)
    if any(r["segment_id"] == SEGMENT_ID for r in mention_rows):
        raise SystemExit("p.350 already has mention rows; review the changed state before applying")
    candidate_by_id = {r["candidate_id"]: r for r in candidate_rows}
    new_ids = [item[0] for item in NEW_CANDIDATES]
    if len(set(new_ids)) != len(new_ids) or any(cid in candidate_by_id for cid in new_ids):
        raise SystemExit("candidate IDs collide or repeat")

    new_candidates = []
    for cid, label, typ, detail, line in NEW_CANDIDATES:
        row = {k: "" for k in candidate_fields}
        row.update({
            "candidate_id": cid, "index_entry_id": "", "canonical_name": label,
            "suggested_type": typ, "status": "open", "detail": detail,
            "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT_ID}#L{line}",
        })
        new_candidates.append(row)
    candidate_rows.extend(new_candidates)
    candidate_ids = {r["candidate_id"] for r in candidate_rows}

    new_mentions = []
    for i, (surface, candidate_id, occurrence, note) in enumerate(MENTION_SPECS, 1):
        if candidate_id not in candidate_ids:
            raise SystemExit(f"unknown mention candidate: {candidate_id}")
        starts, cursor = [], 0
        while True:
            pos = body.find(surface, cursor)
            if pos < 0: break
            starts.append(pos); cursor = pos + 1
        if occurrence >= len(starts):
            raise SystemExit(f"mention span missing: {surface!r} occurrence={occurrence}; found={len(starts)}")
        start = starts[occurrence]
        new_mentions.append({
            "mention_id": f"m-s2-ch14-p350-20261014-{i:03d}", "segment_id": SEGMENT_ID,
            "candidate_id": candidate_id, "surface_form": surface,
            "start_char": str(start), "end_char": str(start + len(surface)), "note": note,
        })
    mention_rows.extend(new_mentions)

    changed: set[str] = set()
    def update(sid: str, *, claim: str | None = None, qualification: str | None = None,
               relation: bool | None = None, subject: str | None = None,
               object_: str | None | object = ..., predicate: str | None = None,
               quote: str | None = None, mentions: list[str] | None = None,
               extra: dict | None = None) -> None:
        row = by_id[sid]
        q = copy.deepcopy(row.get("qualifiers") or {})
        if claim is not None: q["claim"] = claim
        if qualification is not None: q["qualification"] = qualification
        if relation is not None: q["relation_candidate"] = relation
        if mentions is not None: q["mentioned_candidate_ids"] = mentions
        if extra: q.update(copy.deepcopy(extra))
        row["qualifiers"] = q
        if subject is not None: row["subject_candidate_id"] = subject
        if object_ is not ...: row["object_candidate_id"] = object_
        if predicate is not None: row["predicate"] = predicate
        if quote is not None: row["original_quote"] = quote
        changed.add(sid)

    update("st-chp14-p350-rococo-influence-context", predicate="drew_inspiration_from", object_="cand-12186", relation=True,
           claim="Haskell says many indications suggest Algarotti drew inspiration from artists more appreciated in northern Europe than in Venice.",
           qualification="The source says 'many indications'; preserve this as Haskell's inference and do not identify the artists.",
           mentions=["cand-0056", "cand-12186", "cand-3594", "cand-2719"],
           extra={"relation_candidate_note": "The object is an unnamed source-defined artist group; the inference remains attributed to Haskell."})
    update("st-chp14-p350-no-evidence-of-living-artist-contact", relation=False,
           qualification="Preserves Haskell's 'no evidence' wording; it does not prove that no contact occurred. The unnamed group is scoped only to this visit.",
           mentions=["cand-0056", "cand-2719", "cand-12187"],
           extra={"relation_candidate_note": "Negative evidence statement; not recorded as a positive contact relation."})
    update("st-chp14-p350-made-friends-with-voltaire", quote="and though he had already made friends with Voltaire",
           claim="Before the 1737 Venice visit, Haskell says Algarotti had already made friends with Voltaire.",
           qualification="The sentence separately assesses Algarotti's social success in London and Paris; no date is given for when the friendship began.",
           mentions=["cand-0056", "cand-2791"])
    update("st-chp14-p350-youth-status-and-associations", quote="He was still only a young man of 25;",
           claim="During the 1737 Venice visit, Haskell describes Algarotti as a young man of 25.",
           qualification="The age is stated for this point in Haskell's narrative.", mentions=["cand-0056"])
    update("st-chp14-p350-not-known-in-venice-and-associations", quote="he was not very rich,",
           claim="During the 1737 Venice visit, Haskell says Algarotti was not very rich.",
           qualification="This is Haskell's assessment at this point in the narrative.", mentions=["cand-0056"])
    update("st-chp14-p350-importance-from-1742", quote="It is in 1742 that he first assumes real importance as a figure in the international art world",
           claim="Haskell marks 1742 as the point when Algarotti first became important as a figure in the international art world.",
           qualification="This is Haskell's assessment of historical importance, separate from documentary visibility.", relation=False,
           mentions=["cand-0056"], extra={"relation_candidate_note": "Historical importance is an authorial assessment, not a formal relation."})
    update("st-chp14-p350-scholarly-historical-approach", predicate="adopted_historical_approach_in_gallery_scheme", subject="cand-0075", object_="cand-12189", relation=True,
           quote="Algarotti rejects this conception and substitutes for it the outlook of the historian.",
           claim="In the Dresden gallery proposal, Algarotti rejected organization by a collector's personal taste and substituted a historian's outlook.",
           qualification="This records the proposed organizing principle, not proof that the gallery was ultimately arranged this way.",
           mentions=["cand-0075", "cand-12189", "cand-9091"],
           extra={"relation_candidate_note": "The statement explicitly describes the organizing approach proposed for the gallery."})
    update("st-chp14-p350-rediscovery-of-primitives", relation=False, quote="It is evident that such an approach inevitably led",
           claim="Haskell interprets evidence-oriented collecting as leading to what he calls the 'first rediscovery of the primitives,' while expressly excluding Algarotti himself from that later development.",
           qualification="This is Haskell's historical interpretation and label, not an event attributed to Algarotti.",
           mentions=["cand-0075", "cand-10267"],
           extra={"relation_candidate_note": "Historical interpretation without a formal relation endpoint."})
    update("st-chp14-p350-followed-historians", quote="Algarotti was in fact following in the footsteps of historians such as\nMuratori,",
           claim="Haskell says Algarotti followed historians such as Muratori.",
           qualification="Muratori is given as an example; no particular text or direct collaboration is stated.",
           mentions=["cand-0075", "cand-1717"])
    update("st-chp14-p350-proposed-living-artist-commissions", subject="cand-0072", object_="cand-12190",
           quote="the commissioning 'of a number of works by living artists.",
           claim="Algarotti's gallery scheme proposed commissioning a number of works by living artists.",
           qualification="The source describes a proposal and does not establish that any commission was executed. The work group and artist group are kept distinct.",
           relation=True, mentions=["cand-0072", "cand-12190", "cand-10270", "cand-0151"],
           extra={"relation_candidate_note": "Plan-stage relation: proposed works, not completed commissions."})
    update("st-chp14-p350-detailed-subjects-and-style-awareness", predicate="specified_subjects_to_artists", subject="cand-0072", object_="cand-10270",
           quote="Though he still insisted on giving the subjects in great detail to the artists concerned",
           claim="Haskell says Algarotti specified subjects in great detail to the artists considered for the gallery scheme.",
           qualification="The artists are unnamed and the statement concerns the proposed scheme.", relation=True,
           mentions=["cand-0072", "cand-10270"],
           extra={"relation_candidate_note": "A source-reported plan-stage instruction to an unnamed artist group."})
    update("st-chp14-p350-patron-subject-specialization", relation=False,
           quote="Patrons had always recognised that certain artists specialised in particular subjects and had regulated their commissions accordingly:",
           claim="Haskell generalizes that patrons matched commissions to artists' subject specializations.",
           qualification="This introduces a general principle; the two named examples are recorded separately.", mentions=[],
           extra={"relation_candidate_note": "General historical proposition without a specific endpoint pair."})
    update("st-chp14-p350-appraisal-of-venetian-artists", relation=False,
           claim="Haskell judges Algarotti's appraisal of the Venetian artists more subtle, sensitive, and deep than the general practice just described.",
           qualification="This is an evaluative comparison by Haskell; the fact of appraisal is recorded separately.",
           mentions=["cand-0056", "cand-12193"],
           extra={"relation_candidate_note": "Authorial assessment, not itself a relation."})

    # Separate already-classified but compound assertions into source-bounded records.
    new_row_ids = []
    for spec in NEW_STATEMENTS:
        sid, claim, qualification, quote, line, relation, subject_label, object_label, predicate, mention_ids, layer = spec
        if sid in by_id:
            raise SystemExit(f"new statement ID already exists: {sid}")
        subject_id = {
            "Algarotti": "cand-0056", "Dresden gallery scheme": "cand-0072", "Castiglione": "cand-0602",
            "Claude": "cand-0767", "Unnamed collections": "cand-12188",
        }.get(subject_label)
        object_id = {
            "Renaissance": "cand-3578", "Augustus III": "cand-0151",
            "historical principles applied to large-scale art collecting": "cand-12194",
            "unnamed artists considered for the scheme": "cand-10270",
            "pictures containing many animals": "cand-12191", "landscape pictures": "cand-12192",
            "different Venetian artists": "cand-12193",
        }.get(object_label)
        # Some false/evaluative statements deliberately have no relation endpoint.
        row = {
            "statement_id": sid, "segment_id": SEGMENT_ID,
            "subject_candidate_id": subject_id, "object_candidate_id": object_id,
            "predicate": predicate,
            "qualifiers": {
                "source_line_start": line, "source_line_end": line,
                "printed_page": 350, "pdf_physical_page": 4,
                "claim": claim, "speaker": "Haskell", "text_layer": layer,
                "qualification": qualification, "mentioned_candidate_ids": mention_ids,
                "relation_candidate": relation,
            },
            "original_quote": quote, "origin": "book", "source_file": SOURCE_FILE,
        }
        statement_rows.append(row); by_id[sid] = row; changed.add(sid); new_row_ids.append(sid)

    # Preserve existing cross-page references while atomizing the p.350 sentence units.
    update("st-chp14-p350-dresden-gallery-plan", mentions=["cand-0071", "cand-0947", "cand-0151", "cand-10256", "cand-9091", "cand-10266"])
    update("st-chp14-p350-gallery-represent-history-and-schools", mentions=["cand-0075", "cand-9091"])
    update("st-chp14-p350-lodoli-collection", mentions=["cand-1411", "cand-10269"])
    update("st-chp14-p350-followed-historians", mentions=["cand-0075", "cand-1717", "cand-12194"])

    # Verify all current p.350 statements are classified and all cited IDs exist.
    all_candidate_ids = {r["candidate_id"] for r in candidate_rows}
    page_after = [r for r in statement_rows if r["segment_id"] == SEGMENT_ID]
    if any((r.get("qualifiers") or {}).get("relation_candidate") not in (True, False) for r in page_after):
        raise SystemExit("one or more p.350 statements remain unclassified")
    for r in page_after:
        q = r.get("qualifiers") or {}
        for cid in (r.get("subject_candidate_id"), r.get("object_candidate_id"), *(q.get("mentioned_candidate_ids") or [])):
            if cid and cid not in all_candidate_ids:
                raise SystemExit(f"unknown candidate {cid} referenced by {r['statement_id']}")
        quote = r.get("original_quote", "")
        if r["statement_id"] in changed and quote and quote not in body:
            raise SystemExit(f"changed statement quote is not an exact segment substring: {r['statement_id']}")
    intervals = sorted((int(r["start_char"]), int(r["end_char"]), r["mention_id"]) for r in new_mentions)
    for i, left in enumerate(intervals):
        for right in intervals[i + 1:]:
            if right[0] >= left[1]: break
            nested = (left[0] <= right[0] and right[1] <= left[1]) or (right[0] <= left[0] and left[1] <= right[1])
            if left[:2] == right[:2] or not nested:
                raise SystemExit(f"duplicate or crossing mention spans: {left[2]} / {right[2]}")

    statement_payload = write_jsonl(STATEMENTS, original_statement_lines, statement_rows, changed)
    candidate_payload = csv_bytes(candidate_fields, candidate_rows, candidate_bom)
    mention_payload = csv_bytes(mention_fields, mention_rows, mention_bom)
    print(f"p350_existing_statements={len(page_rows)}; p350_final_statements={len(page_after)}")
    print(f"new_statements={len(new_row_ids)}; new_candidates={len(new_candidates)}; exact_mentions={len(new_mentions)}")
    print(f"p350_relation_candidate=true:{sum((r['qualifiers'].get('relation_candidate') is True) for r in page_after)}; false:{sum((r['qualifiers'].get('relation_candidate') is False) for r in page_after)}; unset:0")
    print(f"statement_sha256={hashlib.sha256(statement_payload).hexdigest()}; candidate_sha256={hashlib.sha256(candidate_payload).hexdigest()}; mentions_sha256={hashlib.sha256(mention_payload).hexdigest()}")
    print("all changed quotes and mention spans are exact; nested spans are source-contained; p.350 classifications are complete")
    if not args.apply:
        print("dry_run=true; no files written")
        return 0

    files = ((STATEMENTS, statement_payload), (CANDIDATES, candidate_payload), (MENTIONS, mention_payload))
    backups = [(p, p.with_name(p.name + BACKUP_SUFFIX)) for p, _ in files]
    if any(b.exists() for _, b in backups):
        raise SystemExit("a p.350 backup already exists; inspect before applying")
    for original, backup in backups: shutil.copy2(original, backup)
    try:
        for path, payload in files: path.write_bytes(payload)
        for path, payload in files:
            if sha(path) != hashlib.sha256(payload).hexdigest():
                raise OSError(f"post-write hash mismatch: {path.name}")
    except Exception:
        for original, backup in backups: shutil.copy2(backup, original)
        raise
    print("applied=true")
    for original, backup in backups: print(f"backup={backup.name}; written_sha256={sha(original)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
