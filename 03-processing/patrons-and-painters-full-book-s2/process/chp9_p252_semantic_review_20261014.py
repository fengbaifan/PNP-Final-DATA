"""Controlled p.252 S2 semantic repair; default mode is a read-only preflight."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
BODY = "chp-9:09_CHP-9_intro:l116-122"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
BASELINE_REV = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_BODY_HASH = "9d02deba0f0e66b5f17cf6a1d7cb45435a085ac2be3d503df55a76d8ea5844a3"
EXPECTED_NOTES_HASH = "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p252-semantic-review-20261014"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the preflighted S2 repair")
args = parser.parse_args()


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def atomic_write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(stream.name)
    tmp.replace(path)


def atomic_write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(stream.name)
    tmp.replace(path)


def baseline_csv(path: str):
    result = subprocess.run(
        ["git", "show", f"{BASELINE_REV}:{path}"], cwd=ROOT,
        capture_output=True, check=True,
    )
    return list(csv.DictReader(io.StringIO(result.stdout.decode("utf-8-sig"))))


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segments}
if BODY not in segment_by_id or NOTES not in segment_by_id:
    raise SystemExit("required S0 segment is absent")
if segment_by_id[BODY]["sha256"] != EXPECTED_BODY_HASH:
    raise SystemExit("p.252 body segment hash changed")
if segment_by_id[NOTES]["sha256"] != EXPECTED_NOTES_HASH:
    raise SystemExit("consolidated notes segment hash changed")
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_HASH:
    raise SystemExit("source asset hash changed; S0 remains read-only")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()


def segment_text(segment_id):
    meta = segment_by_id[segment_id]
    return "\n".join(source_lines[n - 1] for n in range(meta["line_start"], meta["line_end"] + 1))


def segment_offset(segment_id, line_number):
    meta = segment_by_id[segment_id]
    return sum(len(source_lines[n - 1]) + 1 for n in range(meta["line_start"], line_number))


def quote(first, last):
    return "\n".join(source_lines[n - 1] for n in range(first, last + 1))


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
if len(statement_by_id) != len(statements):
    raise SystemExit("duplicate statement IDs exist before the repair")

coverage_fields, coverage = read_csv(TABLES / "s2-coverage.csv")
coverage_by_id = {row["segment_id"]: row for row in coverage}
if coverage_by_id.get(BODY, {}).get("migration_status") != "complete":
    raise SystemExit("unexpected p.252 body coverage state")
if coverage_by_id.get(NOTES, {}).get("migration_status") != "complete":
    raise SystemExit("unexpected consolidated-notes coverage state")

expected_body_ids = {
    "st-chp9-p252-daniele-iii-conditional-bequest",
    "st-chp9-p252-daniele-iii-public-service",
    "st-chp9-p252-daniele-iii-will-programme",
    "st-chp9-p252-daniele-iv-brother-of-iii",
    "st-chp9-p252-daniele-iv-command",
    "st-chp9-p252-dionisio-appointed-and-moved",
    "st-chp9-p252-dionisio-authority-and-residence",
    "st-chp9-p252-dionisio-library-and-bambini",
    "st-chp9-p252-dionisio-younger-brother-of-iii",
    "st-chp9-p252-dionisio-younger-brother-of-iv",
    "st-chp9-p252-dolfin-old-family",
    "st-chp9-p252-dolfin-patriarchate",
    "st-chp9-p252-ricci-employment-pattern",
    "st-chp9-p252-summoned-tiepolo-pending-purpose",
    "st-chp9-p252-tiepolo-career-style",
    "st-chp9-p252-tiepolo-dolfin-cycle",
    "st-chp9-p252-tiepolo-required-subjects",
    "st-chp9-p252-tiepolo-wars-context",
    "st-chp9-p252-tiepolo-work-for-corner",
    "st-chp9-p252-venetian-families-roman-ancestry",
}
actual_body_ids = {row["statement_id"] for row in statements if row["segment_id"] == BODY}
if actual_body_ids != expected_body_ids:
    raise SystemExit(f"p.252 body statement inventory changed: {sorted(actual_body_ids ^ expected_body_ids)}")
if candidate_by_id.get("cand-8275", {}).get("canonical_name") != "Classical and allegorical subject group in the unidentified Dolfin-library ceiling fresco":
    raise SystemExit("candidate cand-8275 changed; inspect its current identity before applying the scoped correction")

baseline_mentions = baseline_csv("04-knowledge/tables/mentions.csv")
body_mentions = [row for row in baseline_mentions if row["segment_id"] == BODY]
note_mentions = [
    row for row in baseline_mentions
    if row["segment_id"] == NOTES and row["mention_id"].startswith("m-chp9-p252-")
]
if len(body_mentions) != 61 or len(note_mentions) != 46:
    raise SystemExit(f"unexpected pinned p.252 mention baseline: body={len(body_mentions)}, notes={len(note_mentions)}")

# This generic room is not independently identified in note 3. Its pinned mapping
# to Dionisio's separate library at Udine is unsupported, so do not restore it.
excluded_note_mention_id = "m-chp9-p252-room"
note_mentions = [row for row in note_mentions if row["mention_id"] != excluded_note_mention_id]

existing_mention_ids = {row["mention_id"] for row in mentions}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mentions}
new_mentions = body_mentions + note_mentions
new_ids = [row["mention_id"] for row in new_mentions]
if len(new_ids) != len(set(new_ids)) or existing_mention_ids.intersection(new_ids):
    raise SystemExit("mention ID collision detected")
body_text = segment_text(BODY)
notes_text = segment_text(NOTES)
for row in new_mentions:
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"missing candidate for {row['mention_id']}: {row['candidate_id']}")
    span = (row["segment_id"], row["start_char"], row["end_char"])
    if span in existing_spans:
        raise SystemExit(f"duplicate mention span: {row['mention_id']}")
    text = body_text if row["segment_id"] == BODY else notes_text
    if text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
        raise SystemExit(f"source span mismatch: {row['mention_id']}")
    if row["segment_id"] == BODY:
        start = segment_offset(BODY, 117)
        end = segment_offset(BODY, 123)
        if not (start <= int(row["start_char"]) < int(row["end_char"]) <= end):
            raise SystemExit(f"body mention outside printed p.252 lines 117-122: {row['mention_id']}")
    else:
        start = segment_offset(NOTES, 353)
        end = segment_offset(NOTES, 360)
        if not (start <= int(row["start_char"]) < int(row["end_char"]) <= end):
            raise SystemExit(f"note mention outside p.252 notes 1-7: {row['mention_id']}")


REVIEW = "2026-10-14 S2 source-order review: p.252 scan, exact spans, candidate endpoints, and speaker attribution checked"
BODY_OCR = [
    {"line": 118, "ocr": "subjectmatter", "reading": "subject-matter", "basis": "CHP-9.pdf physical p.14"},
    {"line": 118, "ocr": 'chronicler \"of', "reading": "chronicler of", "basis": "CHP-9.pdf physical p.14"},
    {"line": 120, "ocr": "2 virtual monopoly", "reading": "a virtual monopoly", "basis": "CHP-9.pdf physical p.14"},
    {"line": 122, "ocr": "thirty-six-year.residence", "reading": "thirty-six-year residence", "basis": "CHP-9.pdf physical p.14"},
    {"line": 122, "ocr": "Niccolo Bambini", "reading": "Niccolò Bambini", "basis": "CHP-9.pdf physical p.14"},
]
NOTE3_OCR = [
    {"line": 355, "ocr": "Ans and Sciences", "reading": "Arts and Sciences", "basis": "CHP-9.pdf physical p.14"},
    {"line": 355, "ocr": "fresco arc still", "reading": "fresco are still", "basis": "CHP-9.pdf physical p.14"},
]


NO_CHANGE = object()


def update_statement(statement_id, *, subject=NO_CHANGE, object_=NO_CHANGE, predicate=None,
                     claim=None, relation_candidate=None, first=None, last=None,
                     mention_ids=None, qualification=None, speaker=None,
                     text_layer=None, ocr=None, add_qualifiers=None,
                     remove_qualifier_keys=()):
    row = statement_by_id[statement_id]
    q = row["qualifiers"]
    if subject is not NO_CHANGE:
        row["subject_candidate_id"] = subject
    if object_ is not NO_CHANGE:
        row["object_candidate_id"] = object_
    if predicate is not None:
        row["predicate"] = predicate
    if first is None:
        first = q["source_line_start"]
    if last is None:
        last = q["source_line_end"]
    q["source_line_start"], q["source_line_end"] = first, last
    row["original_quote"] = quote(first, last)
    if claim is not None:
        q["claim"] = claim
    if relation_candidate is not None:
        q["relation_candidate"] = relation_candidate
    if mention_ids is not None:
        q["mentioned_candidate_ids"] = mention_ids
    if qualification is not None:
        q["qualification"] = qualification
    if speaker is not None:
        q["speaker"] = speaker
    if text_layer is not None:
        q["text_layer"] = text_layer
    for key in remove_qualifier_keys:
        q.pop(key, None)
    if ocr is not None:
        q["ocr_corrections"] = ocr
    if add_qualifiers:
        q.update(add_qualifiers)
    q["semantic_review"] = REVIEW


def add_statement(statement_id, subject, object_, predicate, first, last, claim,
                  relation_candidate, mention_ids, qualification, *,
                  speaker="Haskell", text_layer="body", ocr=None,
                  footnote_marker=None, cross_reference_segments=None):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID collision: {statement_id}")
    q = {
        "source_line_start": first,
        "source_line_end": last,
        "printed_page": 252,
        "pdf_physical_page": 14,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mention_ids,
        "relation_candidate": relation_candidate,
        "semantic_review": REVIEW,
    }
    if ocr:
        q["ocr_corrections"] = ocr
    if footnote_marker is not None:
        q["footnote_marker"] = footnote_marker
    if cross_reference_segments:
        q["cross_reference_segments"] = cross_reference_segments
    row = {
        "statement_id": statement_id,
        "segment_id": BODY if text_layer != "footnote" else NOTES,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": q,
        "original_quote": quote(first, last),
        "origin": "book",
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
    }
    statement_by_id[statement_id] = row
    statements.append(row)


def apply_semantic_decisions():
    # Ricci's comparative employment statement has four distinct endpoints.
    update_statement(
        "st-chp9-p252-ricci-employment-pattern", subject="cand-2154", object_="cand-8108",
        predicate="worked_little_for_venetian_aristocracy_after_settling_in_venice",
        claim="After settling in Venice, Sebastiano Ricci worked surprisingly little for the Venetian aristocracy.",
        relation_candidate=True, first=117, last=117,
        mention_ids=["cand-2154", "cand-2719", "cand-8108"],
        qualification="Retain Haskell's relative wording 'surprisingly little'; this is one side of his employment comparison.",
        add_qualifiers={"cross_reference_segments": [{"segment_id": "chp-9:09_CHP-9_intro:l106-114", "source_line_start": 114, "source_line_end": 114}]},
    )
    for suffix, obj, pred, label in [
        ("turin-court", "cand-8273", "employed_by_court_of_turin_more_than_venetian_aristocracy", "the court of Turin"),
        ("churches", "cand-8274", "employed_by_unnamed_churches_more_than_venetian_aristocracy", "churches"),
        ("joseph-smith", "cand-2440", "employed_by_joseph_smith_more_than_venetian_aristocracy", "the English businessman Joseph Smith"),
    ]:
        add_statement(
            f"st-chp9-p252-ricci-employment-{suffix}", "cand-2154", obj, pred, 117, 117,
            f"Haskell says Ricci was far more employed by {label} than by the Venetian aristocracy.",
            True, ["cand-2154", obj, "cand-8108"],
            "The comparative 'far more' is retained; the source gives no number of commissions.",
        )

    update_statement(
        "st-chp9-p252-tiepolo-career-style", subject="cand-2569", object_=None,
        predicate="career_began_immediately_successfully_in_1720s",
        claim="Haskell says Tiepolo first began his immediately successful career in the 1720s.",
        relation_candidate=False, first=118, last=118,
        mention_ids=["cand-2569"],
        qualification="This is Haskell's career-period and success characterization, not a relation between two entities.",
    )
    add_statement(
        "st-chp9-p252-tiepolo-style-appeal", "cand-2569", "cand-8244", "violent_tense_style_appealed",
        118, 118, "Haskell says Tiepolo's violent, tense style appealed in the 1720s.", False,
        ["cand-2569", "cand-8244"],
        "No audience or patron is specified as the recipient of the appeal; preserve this as an attributed characterization.",
        ocr=BODY_OCR[:2],
    )

    update_statement(
        "st-chp9-p252-tiepolo-wars-context", subject="cand-8244", object_="cand-8242",
        predicate="dramatic_style_and_subject_matter_reflect_venetian_wars",
        claim="Haskell interprets Tiepolo's dramatic style and subject matter in other cases as clearly reflecting Venice's wars with the Turks in the 1680s and again in 1715.",
        relation_candidate=True, first=118, last=119,
        mention_ids=["cand-8244", "cand-8242", "cand-2719", "cand-7153"],
        qualification="This is Haskell's explicit interpretation. The event candidate retains only the broad wars and dates named; no individual campaign is inferred.",
        ocr=BODY_OCR[:2],
    )
    add_statement(
        "st-chp9-p252-venice-aristocracy-historical-mark", "cand-2719", None,
        "city_and_aristocracy_last_mark_on_european_history", 119, 119,
        "Haskell characterizes the 1715 war as the last occasion when Venice and its aristocracy left their mark on European history.",
        False, ["cand-2719", "cand-8108", "cand-8242"],
        "Preserve the author's historical judgment and the source's reference to the city and its aristocracy; no 'European history' entity is inferred.",
    )
    update_statement(
        "st-chp9-p252-venetian-families-roman-ancestry", subject="cand-8276", object_="cand-8243",
        predicate="families_claimed_roman_ancestry_including_corner",
        claim="Haskell says many Venetian families claimed Roman ancestry and names the Corner among them.",
        relation_candidate=True, first=118, last=118,
        mention_ids=["cand-8276", "cand-8243", "cand-0848"],
        qualification="Record this as Haskell's account of a claimed ancestry, not as independently established Roman descent.",
        ocr=BODY_OCR[:2],
    )
    update_statement(
        "st-chp9-p252-tiepolo-dolfin-cycle", subject="cand-2569", object_="cand-8241",
        predicate="painted_ten_roman_history_scenes_selected_from_florus",
        claim="Haskell identifies ten large Roman-history scenes, chosen from L. Annaeus Florus, as the most notable example of the echoes and says Tiepolo painted them.",
        relation_candidate=True, first=119, last=119,
        mention_ids=["cand-2569", "cand-8241", "cand-8245"],
        qualification="The source does not enumerate individual canvases; the Dolfin patronage claim is recorded separately.",
        ocr=BODY_OCR[:2], add_qualifiers={"footnote_marker": 3},
    )
    add_statement(
        "st-chp9-p252-tiepolo-dolfin-patronage", "cand-2569", "cand-0931",
        "patronized_by_dolfin_family_in_1720s", 119, 119,
        "Haskell calls the Dolfin Tiepolo's greatest patrons of the 1720s.", True,
        ["cand-2569", "cand-0931"],
        "Retain Haskell's superlative and the 1720s time scope.",
    )
    add_statement(
        "st-chp9-p252-tiepolo-cycle-painted-for-dolfin", "cand-8241", "cand-0931",
        "painted_for_dolfin_family", 119, 119,
        "Haskell says Tiepolo painted the ten-scene cycle for the Dolfin family.", True,
        ["cand-2569", "cand-8241", "cand-0931"],
        "The family is not resolved to individual patrons in this sentence.",
        footnote_marker=3,
    )

    update_statement(
        "st-chp9-p252-daniele-iii-conditional-bequest", subject="cand-8246", object_="cand-8105",
        predicate="will_bequeathed_estate_to_republic_if_male_line_extinguished",
        claim="Haskell says Daniele III's will left his entire estate to the Republic if his male line became extinct.",
        relation_candidate=True, first=119, last=119,
        mention_ids=["cand-0927", "cand-8246", "cand-8105"],
        qualification="The will is the source of the conditional bequest; keep the male-line condition and the Republic as recipient.",
        text_layer="reported will content",
    )
    update_statement(
        "st-chp9-p252-daniele-iii-public-service", subject="cand-0927", object_="cand-8105",
        predicate="served_venetian_state_abroad_and_at_home",
        claim="Haskell says Daniele III served the State abroad and at home throughout his life.",
        relation_candidate=True, first=119, last=119,
        mention_ids=["cand-0927", "cand-8105"],
        qualification="The source gives no specific office or title; retain the broad service wording.",
    )
    add_statement(
        "st-chp9-p252-daniele-iii-oratory", "cand-0927", None, "considered_one_of_finest_orators",
        119, 119, "Haskell says Daniele III was considered one of the finest orators of his day.", False,
        ["cand-0927"], "This is Haskell's evaluative biographical characterization.",
    )
    update_statement(
        "st-chp9-p252-daniele-iii-will-programme", subject="cand-0927", object_="cand-8105",
        predicate="will_regretted_unfulfilled_plan_to_restore_state_economy_in_peacetime",
        claim="In the words Haskell attributes to Daniele III's will, Daniele regretted not seeing fulfilled ideas conceived while serving in the Treasury to restore the State's economy in peacetime.",
        relation_candidate=True, first=119, last=119,
        mention_ids=["cand-0927", "cand-8246", "cand-8247", "cand-8105"],
        qualification="The quotation and document contents are reported through Haskell; the will itself was not independently consulted.",
        text_layer="quoted source reported by Haskell",
    )
    add_statement(
        "st-chp9-p252-daniele-iii-will-shed-blood", "cand-0927", "cand-8105",
        "will_expressed_wish_to_shed_blood_to_heal_state_wounds", 119, 119,
        "In the words Haskell attributes to Daniele III's will, Daniele wished he might shed his blood to heal the State's wounds.",
        True, ["cand-0927", "cand-8246", "cand-8105"],
        "The wish is reported through Haskell's quotation of the will; it is not an account of an action performed.",
        speaker="Haskell quoting Daniele III's will", text_layer="quoted source reported by Haskell",
    )
    update_statement(
        "st-chp9-p252-daniele-iv-brother-of-iii", subject="cand-0928", object_="cand-0927",
        predicate="brother_of", claim="Haskell identifies Daniele IV as Daniele III's brother.",
        relation_candidate=True, first=119, last=119,
        mention_ids=["cand-0928", "cand-0927"],
        qualification="The kinship is explicit; Daniele IV's death date is recorded separately.",
    )
    update_statement(
        "st-chp9-p252-daniele-iv-command", subject="cand-0928", object_="cand-1705",
        predicate="commanded_under_morosini_in_peloponnese", claim="Haskell says Daniele IV served as a commander under Morosini in the Peloponnese during the Turkish wars.",
        relation_candidate=True, first=119, last=119,
        mention_ids=["cand-0928", "cand-1705", "cand-8117"],
        qualification="The text ties Morosini to the Peloponnese service; it does not say Morosini commanded Daniele IV again in 1715.",
    )
    add_statement(
        "st-chp9-p252-daniele-iv-heroic-assessment", "cand-0928", None,
        "called_one_of_most_heroic_commanders", 119, 119,
        "Haskell characterizes Daniele IV as one of the most heroic commanders in the Turkish wars.", False,
        ["cand-0928"], "This is Haskell's evaluative characterization, separate from the service details.",
    )
    add_statement(
        "st-chp9-p252-daniele-iv-1715-service", "cand-0928", "cand-8242",
        "served_again_in_turkish_war_of_1715", 119, 119,
        "Haskell says Daniele IV served again in the Turkish wars in 1715.", True,
        ["cand-0928", "cand-8242", "cand-7153"],
        "The source gives 1715 for the later service but does not name Morosini as the commander on that occasion.",
    )

    update_statement(
        "st-chp9-p252-dolfin-old-family", subject="cand-0931", object_=None,
        predicate="family_described_as_tremendous_and_old_style",
        claim="Haskell calls the Dolfin a tremendous family in the old style.",
        relation_candidate=False, first=119, last=119,
        mention_ids=["cand-0931"],
        qualification="The phrase is an evaluative description attributed to Haskell, not a separately identified entity relation.",
    )
    update_statement(
        "st-chp9-p252-dolfin-patriarchate", subject="cand-0931", object_="cand-8248",
        predicate="family_reported_to_hold_virtual_monopoly_of_patriarchate",
        claim="Haskell says the Dolfin enjoyed a virtual monopoly of the Patriarchate of Aquileia.",
        relation_candidate=True, first=120, last=120,
        mention_ids=["cand-0931", "cand-8248"],
        qualification="Preserve 'virtual' and the unspecified period; this remains Haskell's account.",
        ocr=[{"line": 120, "ocr": "2 virtual monopoly", "reading": "a virtual monopoly", "basis": "CHP-9.pdf physical p.14"}],
        add_qualifiers={"footnote_marker": 6},
    )

    update_statement(
        "st-chp9-p252-dionisio-appointed-and-moved", subject="cand-0929", object_="cand-8248",
        predicate="appointed_to_patriarchate_of_aquileia_in_1698",
        claim="Haskell says Dionisio was given the Patriarchate of Aquileia in 1698.",
        relation_candidate=True, first=120, last=121,
        mention_ids=["cand-0929", "cand-8248"],
        qualification="The post is anaphorically identified from the preceding sentence about the Patriarchate of Aquileia.",
        ocr=[{"line": 120, "ocr": "2 virtual monopoly", "reading": "a virtual monopoly", "basis": "CHP-9.pdf physical p.14"}],
        add_qualifiers={"footnote_marker": 6},
    )
    add_statement(
        "st-chp9-p252-dionisio-moved-to-udine", "cand-0929", "cand-2666", "moved_to_live_in_udine",
        121, 122, "Haskell says Dionisio went to live in Udine after receiving the post in 1698.", True,
        ["cand-0929", "cand-2666"], "The move and residence are stated by Haskell; Udine is the city, not the bishopric.",
    )
    update_statement(
        "st-chp9-p252-dionisio-authority-and-residence", subject="cand-0929", object_="cand-2666",
        predicate="imposed_personality_on_udine_despite_austrian_opposition",
        claim="Despite what Haskell calls Austria's bitter opposition, Dionisio imposed his astute, authoritative and ambitious personality on Udine.",
        relation_candidate=False, first=121, last=122,
        mention_ids=["cand-0929", "cand-7284", "cand-2666"],
        qualification="Retain Haskell's evaluative language; it does not specify a formal office or jurisdiction over the city.",
        remove_qualifier_keys=("ocr_corrections",),
    )
    add_statement(
        "st-chp9-p252-dionisio-residence-records", "cand-0929", "cand-2666",
        "left_records_of_thirty_six_year_residence_in_udine", 122, 122,
        "Haskell says Dionisio left many permanent records of a thirty-six-year residence in Udine.", True,
        ["cand-0929", "cand-2666"],
        "The duration is retained as Haskell reports it; no terminal year is calculated.",
        ocr=[{"line": 122, "ocr": "thirty-six-year.residence", "reading": "thirty-six-year residence", "basis": "CHP-9.pdf physical p.14"}],
    )
    update_statement(
        "st-chp9-p252-dionisio-library-and-bambini", subject="cand-0929", object_="cand-8249",
        predicate="built_sumptuous_library_in_udine_in_1708",
        claim="Haskell says Dionisio built a sumptuous library in Udine in 1708.",
        relation_candidate=True, first=122, last=122,
        mention_ids=["cand-0929", "cand-8249", "cand-2666"],
        qualification="The source describes the library as built by Dionisio; it does not establish the building's later identity or surviving fabric.",
        remove_qualifier_keys=("footnote_marker", "cross_reference_segments"),
    )
    add_statement(
        "st-chp9-p252-bambini-painted-library-frescoes", "cand-0171", "cand-8250",
        "painted_frescoes_for_dionisio_library", 122, 122,
        "Haskell identifies Niccolò Bambini as the painter of the frescoes decorating Dionisio's library.", True,
        ["cand-0171", "cand-8250", "cand-8249"],
        "No individual fresco title or scene is identified; the source's attribution is preserved.",
        ocr=[{"line": 122, "ocr": "Niccolo Bambini", "reading": "Niccolò Bambini", "basis": "CHP-9.pdf physical p.14"}],
        footnote_marker=7,
    )
    add_statement(
        "st-chp9-p252-library-decorated-with-bambini-frescoes", "cand-8250", "cand-8249",
        "frescoes_decorated_library_at_udine", 122, 122,
        "Haskell says the library was decorated with frescoes by Niccolò Bambini.", True,
        ["cand-8250", "cand-8249", "cand-0171"],
        "This records the location/decorative relation; the painter attribution remains Haskell's statement.",
        ocr=[{"line": 122, "ocr": "Niccolo Bambini", "reading": "Niccolò Bambini", "basis": "CHP-9.pdf physical p.14"}],
        footnote_marker=7,
    )

    # Classification and relation endpoints for the note statements already in S2.
    note_false_ids = [
        "st-chp9-p252-da-canal-citation-note2", "st-chp9-p252-da-canal-ibid-note3",
        "st-chp9-p252-early-sketches-note", "st-chp9-p252-florus-loeb-citation-note3",
        "st-chp9-p252-ivanov-citation-note5", "st-chp9-p252-morassi-citation-note3",
        "st-chp9-p252-renaldis-citation-note6",
    ]
    for sid in note_false_ids:
        row = statement_by_id[sid]
        row["qualifiers"]["relation_candidate"] = False
        row["qualifiers"]["semantic_review"] = REVIEW
        first = row["qualifiers"]["source_line_start"]
        last = row["qualifiers"]["source_line_end"]
        row["original_quote"] = quote(first, last)
    update_statement(
        "st-chp9-p252-dolfin-and-correr-citations-note4", subject="cand-8260", object_="cand-8261",
        predicate="cites_dolfin_history_i_dolfin", claim="Note 4 cites Bortolo Giovanni Dolfin's I Dolfin, pages 171 ff.",
        relation_candidate=False, first=356, last=356,
        mention_ids=["cand-8260", "cand-8261"],
        qualification="The bibliography resolves the abbreviated citation; the cited pages were not consulted independently.",
        remove_qualifier_keys=("ocr_corrections",),
    )
    add_statement(
        "st-chp9-p252-correr-manuscript-citation-note4", "cand-8263", "cand-8262",
        "manuscript_cited_at_biblioteca_correr", 356, 356,
        "Note 4 also cites a manuscript in Biblioteca Correr XI, E 2/6 titled Discendenze patrizie.", True,
        ["cand-8263", "cand-8262"],
        "This records Haskell's manuscript locator and repository wording; the manuscript was not independently consulted.",
        speaker="Haskell's footnote", text_layer="footnote",
        ocr=[{"line": 356, "ocr": "Disccndenze patrizie", "reading": "Discendenze patrizie", "basis": "CHP-9.pdf physical p.14"}],
        footnote_marker=4,
    )
    update_statement(
        "st-chp9-p252-tiepolo-canvases-locations-and-correction", subject="cand-2582", object_=None,
        predicate="haskell_corrects_prior_vienna_canvas_subject_identification",
        claim="Haskell says a Vienna canvas described by Morassi and others as Eteocles and Polynices is Brutus killing Arruns, also taken from Florus.",
        relation_candidate=False, first=355, last=355,
        mention_ids=["cand-8241", "cand-2582", "cand-8257", "cand-8258", "cand-8245", "cand-8259"],
        qualification="The correction and prior identification are reported by Haskell; the canvas and cited sources were not independently examined.",
        add_qualifiers={"footnote_marker": 3},
    )
    add_statement(
        "st-chp9-p252-tiepolo-cycle-partly-in-leningrad", "cand-8241", "cand-5796",
        "some_canvases_now_in_leningrad", 355, 355,
        "Haskell's note says the Tiepolo pictures are now divided between Leningrad and Vienna, so some are in Leningrad.", True,
        ["cand-8241", "cand-5796", "cand-2772"],
        "The note gives no individual allocation or count for the canvases in either city.",
        speaker="Haskell's footnote", text_layer="footnote", footnote_marker=3,
    )
    add_statement(
        "st-chp9-p252-tiepolo-cycle-partly-in-vienna", "cand-8241", "cand-2772",
        "some_canvases_now_in_vienna", 355, 355,
        "Haskell's note says the Tiepolo pictures are now divided between Leningrad and Vienna, so some are in Vienna.", True,
        ["cand-8241", "cand-5796", "cand-2772"],
        "The note gives no individual allocation or count for the canvases in either city.",
        speaker="Haskell's footnote", text_layer="footnote", footnote_marker=3,
    )
    update_statement(
        "st-chp9-p252-unidentified-ceiling-fresco", subject="cand-8251", object_=None,
        predicate="fresco_described_with_symbolic_figures_and_uncertain_author_date",
        claim="Haskell describes an unidentified ceiling fresco with a dolphin, ancient deities, Abundance, Arts and Sciences, Time, Fame and other symbolic figures within a Bolognese-type architectural framework; he says its artist and date remain mysterious and tentatively places it some years after Tiepolo's canvases.",
        relation_candidate=False, first=355, last=355,
        mention_ids=["cand-8251", "cand-8275", "cand-8188", "cand-8241"],
        qualification="The room is not independently identified in this note and is not linked here to Dionisio's separate library at Udine.",
        ocr=NOTE3_OCR,
        add_qualifiers={"footnote_marker": 3},
    )
    candidate_by_id["cand-8275"]["canonical_name"] = "Classical and allegorical subject group in an unidentified ceiling fresco"
    update_statement(
        "st-chp9-p252-vendramin-cycle-attribution-note5", subject="cand-8254", object_="cand-8253",
        predicate="separate_roman_history_cycle_located_at_palazzo_vendramin_calergi",
        claim="Note 5 places a separate cycle of canvases with Roman-history subjects at Palazzo Vendramin-Calergi.",
        relation_candidate=True, first=357, last=357,
        mention_ids=["cand-8254", "cand-8253"],
        qualification="This cycle is distinct from the Tiepolo cycle discussed in note 3.",
        remove_qualifier_keys=("ocr_corrections",),
        add_qualifiers={"footnote_marker": 5},
    )
    add_statement(
        "st-chp9-p252-vendramin-cycle-attributed-to-bambini", "cand-8254", "cand-0171",
        "cycle_attributed_to_niccolo_bambini", 357, 357,
        "Note 5 says the separate Palazzo Vendramin-Calergi cycle has been attributed to Niccolò Bambini.", True,
        ["cand-8254", "cand-8253", "cand-0171", "cand-8264", "cand-8265"],
        "Preserve the reported attribution as an attribution, not a settled authorship; the note cites Ivanov (1951, pages 1-3).",
        speaker="Haskell's footnote", text_layer="footnote", footnote_marker=5,
        ocr=[{"line": 357, "ocr": "6 The other great cycle", "reading": "5 The other great cycle", "basis": "CHP-9.pdf physical p.14"}, {"line": 357, "ocr": "Niccolo Bambini", "reading": "Niccolò Bambini", "basis": "CHP-9.pdf physical p.14"}],
    )
    update_statement(
        "st-chp9-p252-madrisio-biasutti-citation-note7", subject="cand-8268", object_="cand-8269",
        predicate="cites_madrisio_1711", claim="Note 7 cites Niccolò Madrisio, 1711.",
        relation_candidate=False, first=359, last=359,
        mention_ids=["cand-8268", "cand-8269"],
        qualification="The bibliography identifies the cited item as Madrisio's oration about Dionigi Delfino's public library; the oration was not consulted independently.",
        ocr=[{"line": 359, "ocr": "Niccold", "reading": "Niccolò", "basis": "CHP-9.pdf physical p.14"}],
        add_qualifiers={"footnote_marker": 7},
    )
    add_statement(
        "st-chp9-p252-biasutti-citation-note7", "cand-8270", "cand-8271", "cites_biasutti_1958",
        359, 359, "Note 7 also cites Biasutti, 1958.", False,
        ["cand-8270", "cand-8271"],
        "The bibliography identifies the work as Storia e Guida del Palazzo Arcivescovile di Udine; it was not consulted independently.",
        speaker="Haskell's footnote", text_layer="footnote", footnote_marker=7,
    )

    # Preserve exact source quotes and mark all existing p.252 body rows reviewed,
    # including the unchanged kinship, Corner, required-subject, and summons claims.
    for row in statements:
        if row["segment_id"] == BODY:
            q = row["qualifiers"]
            row["original_quote"] = quote(q["source_line_start"], q["source_line_end"])
            q["semantic_review"] = REVIEW


if not args.apply:
    print(f"DRY RUN OK: p.252 source/segment fingerprints verified; {len(body_mentions)} body mentions and {len(note_mentions)} note mentions have exact source spans and valid candidates.")
    print(f"p.252 body statements: {len(expected_body_ids)} reviewed; existing classification gaps: 6; planned new statements are deterministic.")
    print("No files written. The generic note-3 room mention is excluded because its pinned mapping to the Udine library is unsupported.")
    raise SystemExit(0)

targets = [candidate_path, mention_path, statement_path]
for path in targets:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; inspect before applying: {backup.name}")

before_statement_count = len(statements)
apply_semantic_decisions()
new_classifications = [
    row for row in statements
    if row["segment_id"] == BODY and row["qualifiers"].get("relation_candidate") is None
]
if new_classifications:
    raise SystemExit(f"unclassified p.252 body statements remain: {[row['statement_id'] for row in new_classifications]}")
if len({row["statement_id"] for row in statements}) != len(statements):
    raise SystemExit("duplicate statement IDs after planned changes")
for row in statements:
    if row.get("qualifiers", {}).get("semantic_review") == REVIEW:
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint not in (None, "") and endpoint not in candidate_ids:
                raise SystemExit(f"reviewed p.252 statement has an invalid candidate endpoint: {row['statement_id']} -> {endpoint}")

mentions.extend(new_mentions)
for path in targets:
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
atomic_write_csv(candidate_path, candidate_fields, candidates)
atomic_write_csv(mention_path, mention_fields, mentions)
atomic_write_jsonl(statement_path, statements)
print(f"APPLIED: restored {len(body_mentions)} p.252 body mentions and {len(note_mentions)} p.252 note mentions.")
print(f"APPLIED: statements {before_statement_count} -> {len(statements)}; all p.252 body statements classified.")
print(f"BACKUPS: *{BACKUP_SUFFIX}")
