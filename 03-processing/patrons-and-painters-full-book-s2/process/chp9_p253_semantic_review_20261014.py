"""Controlled p.253 S2 review; defaults to a read-only semantic/data preflight."""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
LEGACY_MIGRATION = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "chp9_p253_migration.py"
BODY = "chp-9:09_CHP-9_intro:l124-132"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
LEGACY_MIGRATION_HASH = "1e69fc00c68a5f3a5d813d7169498de06a99b979be07cfece79c739ea17420f3"
EXPECTED_BODY_HASH = "bdcf1ec70bda8a3346f427787148673220496aeed2c647ad5260fcff41744e9a"
EXPECTED_NOTES_HASH = "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p253-semantic-review-20261014"
REVIEW = "2026-10-14 S2 source-order review: p.253 physical page 15, exact spans, endpoints, and reported speech checked"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the preflighted p.253 S2 repair")
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


def extract_pinned_mention_specs():
    raw = LEGACY_MIGRATION.read_bytes()
    if hashlib.sha256(raw).hexdigest() != LEGACY_MIGRATION_HASH:
        raise SystemExit("p.253 migration spec source changed; inspect before using its mention list")
    tree = ast.parse(raw.decode("utf-8-sig"))
    assignment = next(
        node for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "MENTION_SPECS" for target in node.targets)
    )

    class ResolveSegmentNames(ast.NodeTransformer):
        values = {
            "P253": BODY,
            "NOTES": NOTES,
        }

        def visit_Name(self, node):
            if node.id in self.values:
                return ast.copy_location(ast.Constant(self.values[node.id]), node)
            return node

    return ast.literal_eval(ResolveSegmentNames().visit(assignment.value))


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segments}
for sid in (BODY, NOTES):
    if sid not in segment_by_id:
        raise SystemExit(f"missing source segment: {sid}")
if segment_by_id[BODY]["sha256"] != EXPECTED_BODY_HASH:
    raise SystemExit("p.253 body segment hash changed")
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
_, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
if len(statement_by_id) != len(statements):
    raise SystemExit("duplicate statement IDs exist before p.253 review")

coverage = {row["segment_id"]: row for row in read_csv(TABLES / "s2-coverage.csv")[1]}
if coverage.get(BODY, {}).get("migration_status") != "complete":
    raise SystemExit("unexpected p.253 coverage state")

expected_body_ids = {
    "st-chp9-p253-aristocracy-work-and-fragmentation",
    "st-chp9-p253-barbaro-dolfin-roman-epics",
    "st-chp9-p253-candidate-absence-becoming-commonplace",
    "st-chp9-p253-commission-to-palace-and-cathedral",
    "st-chp9-p253-dionisio-domain-and-patronage",
    "st-chp9-p253-dionisio-saw-tiepolo-masterpieces",
    "st-chp9-p253-tiepolo-break-and-travel",
    "st-chp9-p253-tiepolo-demand-and-artistic-gifts",
    "st-chp9-p253-tiepolo-patronage-ideal",
    "st-chp9-p253-two-dolfin-members-imprisoned-or-exiled",
    "st-chp9-p253-udine-fresco-sites-and-works",
    "st-chp9-p253-udine-style-transition",
    "st-chp9-p253-venice-neutrality",
    "st-chp9-p253-zen-resident-report",
}
actual_body_ids = {row["statement_id"] for row in statements if row["segment_id"] == BODY}
if actual_body_ids != expected_body_ids:
    raise SystemExit(f"p.253 body statement inventory changed: {sorted(actual_body_ids ^ expected_body_ids)}")
expected_note_ids = {
    "st-chp9-p253-note1-later-recall-and-chapel",
    "st-chp9-p253-note2-press-report-and-italian-quote",
    "st-chp9-p253-note3-state-papers-locator",
    "st-chp9-p253-note4-provincial-nobles-berengo",
}
actual_note_ids = {
    row["statement_id"] for row in statements
    if row["segment_id"] == NOTES and 360 <= row["qualifiers"].get("source_line_start", 0) <= 363
}
if actual_note_ids != expected_note_ids:
    raise SystemExit(f"p.253 note statement inventory changed: {sorted(actual_note_ids ^ expected_note_ids)}")
if any(row["mention_id"].startswith("m-chp9-p253-") for row in mentions):
    raise SystemExit("p.253 mention IDs already exist; inspect before restoring")

mention_specs = extract_pinned_mention_specs()
if len(mention_specs) != 68:
    raise SystemExit(f"unexpected p.253 pinned mention spec count: {len(mention_specs)}")
existing_mention_ids = {row["mention_id"] for row in mentions}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mentions}
new_mentions = []
body_text = segment_text(BODY)
notes_text = segment_text(NOTES)
for spec in mention_specs:
    segment_id, line_no, suffix, candidate_id, surface, note, *rest = spec
    occurrence = rest[0] if rest else 0
    mention_id = f"m-chp9-p253-{suffix}"
    if mention_id in existing_mention_ids:
        raise SystemExit(f"mention ID collision: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"missing candidate for {mention_id}: {candidate_id}")
    if "\n" in surface:
        search_text = "\n".join(source_lines[n - 1] for n in range(line_no, segment_by_id[segment_id]["line_end"] + 1))
    else:
        search_text = source_lines[line_no - 1]
    start_at, pos = 0, -1
    for _ in range(occurrence + 1):
        pos = search_text.find(surface, start_at)
        if pos < 0:
            break
        start_at = pos + len(surface)
    if pos < 0:
        raise SystemExit(f"surface not found at L{line_no}: {mention_id} {surface!r}")
    start = segment_offset(segment_id, line_no) + pos
    end = start + len(surface)
    span = (segment_id, str(start), str(end))
    if span in existing_spans or any((row["segment_id"], row["start_char"], row["end_char"]) == span for row in new_mentions):
        raise SystemExit(f"duplicate mention span: {mention_id}")
    actual = (body_text if segment_id == BODY else notes_text)[start:end]
    if actual != surface:
        raise SystemExit(f"exact S0 span mismatch: {mention_id}; found {actual!r}")
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": segment_id,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })


NO_CHANGE = object()


def update_statement(statement_id, *, subject=NO_CHANGE, object_=NO_CHANGE, predicate=None,
                     claim=None, relation_candidate=None, first=None, last=None,
                     mention_ids=None, qualification=None, speaker=None, text_layer=None,
                     ocr=NO_CHANGE, extra=None, remove=()):
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
    if ocr is not NO_CHANGE:
        if ocr:
            q["ocr_corrections"] = ocr
        else:
            q.pop("ocr_corrections", None)
    for key in remove:
        q.pop(key, None)
    if extra:
        q.update(extra)
    q["semantic_review"] = REVIEW


def add_statement(suffix, segment_id, subject, object_, predicate, first, last, claim,
                  relation_candidate, mention_ids, qualification, *, speaker="Haskell",
                  text_layer="body", marker=None, note_line=None, ocr=None):
    sid = f"st-chp9-p253-{suffix}"
    if sid in statement_by_id:
        raise SystemExit(f"statement ID collision: {sid}")
    q = {
        "source_line_start": first,
        "source_line_end": last,
        "printed_page": 253,
        "pdf_physical_page": 15,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mention_ids,
        "relation_candidate": relation_candidate,
        "semantic_review": REVIEW,
    }
    if marker is not None:
        q["footnote_marker"] = marker
    if note_line is not None:
        q["cross_reference_segments"] = [{"segment_id": NOTES, "source_line_start": note_line, "source_line_end": note_line}]
    if ocr:
        q["ocr_corrections"] = ocr
    row = {
        "statement_id": sid,
        "segment_id": segment_id,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": q,
        "original_quote": quote(first, last),
        "origin": "book",
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
    }
    statements.append(row)
    statement_by_id[sid] = row


def apply_semantic_decisions():
    update_statement(
        "st-chp9-p253-commission-to-palace-and-cathedral", subject="cand-0929", object_="cand-2569",
        predicate="summoned_tiepolo_to_paint_frescoes_in_udine_cathedral_and_new_palace",
        claim="The p.252 sentence continues: Dionisio summoned Tiepolo to paint frescoes in Udine Cathedral and Dionisio's new Archiepiscopal Palace.",
        relation_candidate=True, first=125, last=125,
        mention_ids=["cand-0929", "cand-2569", "cand-8235", "cand-8277"],
        qualification="The destination is resolved by the immediately preceding Udine context; this is distinct from the 1759 recall by Daniele Dolfin in note 1.",
        extra={"cross_reference_segments": [{"segment_id": "chp-9:09_CHP-9_intro:l116-122", "source_line_start": 122, "source_line_end": 122}]},
    )
    update_statement(
        "st-chp9-p253-udine-fresco-sites-and-works", subject="cand-2569", object_="cand-8281",
        predicate="painted_staircase_ceiling_fresco_at_udine_palace",
        claim="Haskell says Tiepolo made a rather melodramatic start on the ceiling of the staircase.",
        relation_candidate=True, first=125, last=125,
        mention_ids=["cand-2569", "cand-8281", "cand-8278", "cand-8277"],
        qualification="The judgment 'melodramatic' is Haskell's; the work is not separately titled.",
        extra={"cross_reference_segments": [{"segment_id": "chp-9:09_CHP-9_intro:l116-122", "source_line_start": 122, "source_line_end": 122}]},
    )
    add_statement("staircase-fresco-location", BODY, "cand-8281", "cand-8278", "located_on_palace_staircase_ceiling", 125, 125,
                  "Haskell locates the untitled Tiepolo fresco on the staircase ceiling of Dionisio's new Archiepiscopal Palace at Udine.", True,
                  ["cand-8281", "cand-8278", "cand-8277", "cand-0929"],
                  "The work's title and individual subject are not supplied.")
    add_statement("abraham-scenes-work", BODY, "cand-2569", "cand-8282", "painted_scenes_from_life_of_abraham", 125, 126,
                  "Haskell says Tiepolo painted scenes from the life of Abraham in the palace gallery.", True,
                  ["cand-2569", "cand-8282", "cand-8279", "cand-8277"],
                  "The scenes are retained as a group; no individual episodes are named.")
    add_statement("abraham-scenes-location", BODY, "cand-8282", "cand-8279", "located_in_palace_gallery", 125, 126,
                  "Haskell places the Abraham scenes in the gallery of Dionisio's new palace at Udine.", True,
                  ["cand-8282", "cand-8279", "cand-8277", "cand-0929"],
                  "The gallery is a separately identified interior space in the source-derived candidate set.")
    add_statement("justice-solomon-work", BODY, "cand-2569", "cand-8283", "painted_the_justice_of_solomon", 125, 126,
                  "Haskell identifies The Justice of Solomon as another Tiepolo work in the palace.", True,
                  ["cand-2569", "cand-8283", "cand-8280", "cand-8277"],
                  "The printed title is preserved; its identity with the index subentry 'Judgment of Solomon' remains for S3.")
    add_statement("justice-solomon-location", BODY, "cand-8283", "cand-8280", "located_in_tribunal_hall", 125, 126,
                  "Haskell places The Justice of Solomon in the hall of the tribunal.", True,
                  ["cand-8283", "cand-8280", "cand-8277"],
                  "The location is described as the tribunal hall in Dionisio's palace at Udine.")
    update_statement(
        "st-chp9-p253-udine-style-transition", subject="cand-2569", object_="cand-8284",
        predicate="earlier_heaviness_replaced_by_incisive_line_and_lighter_palette",
        claim="Haskell says Tiepolo's earlier dark, lumpish heaviness gave way to aristocratic incisiveness of line and a lighter palette of sparkling blues, pinks and greens against an airy background.",
        relation_candidate=False, first=125, last=126,
        mention_ids=["cand-2569", "cand-8284"],
        qualification="This is Haskell's stylistic assessment, not an externally verified style classification.", ocr=[],
    )
    update_statement(
        "st-chp9-p253-dionisio-domain-and-patronage", subject="cand-0929", object_=None,
        predicate="ruled_petty_state_like_medieval_feudal_bishop",
        claim="Haskell says Dionisio ruled his petty state like a medieval feudal bishop.",
        relation_candidate=False, first=127, last=127,
        mention_ids=["cand-0929", "cand-8248"],
        qualification="The simile and 'petty state' wording are Haskell's; the passage does not resolve a distinct territorial or constitutional entity.",
        extra={"footnote_marker": 1},
    )
    add_statement("dionisio-patron-characterization", BODY, "cand-0929", "cand-2569", "described_as_patron_type_congenial_to_tiepolo", 127, 127,
                  "Haskell calls Dionisio the type of patron most congenial to Tiepolo.", False,
                  ["cand-0929", "cand-2569"],
                  "This is Haskell's characterization, not a separate commission or evidence of artistic preference.", marker=1, note_line=360)
    update_statement(
        "st-chp9-p253-dionisio-saw-tiepolo-masterpieces", subject="cand-0929", object_=None,
        predicate="saw_tiepolo_first_masterpieces_shortly_before_dying",
        claim="Haskell says Dionisio had the privilege of seeing Tiepolo's first masterpieces shortly before dying.",
        relation_candidate=True, first=127, last=127,
        mention_ids=["cand-0929", "cand-2569", "cand-8281", "cand-8282", "cand-8283"],
        qualification="The source asserts a direct viewing relation but does not identify which of the newly described works constitutes the 'first masterpieces'.",
        extra={"footnote_marker": 1, "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 360, "source_line_end": 360}]},
    )
    update_statement(
        "st-chp9-p253-tiepolo-break-and-travel", subject="cand-2569", object_=None,
        predicate="final_break_with_seventeenth_century_style_not_possible_in_conservative_venice",
        claim="Haskell argues that Tiepolo's final break with the heavy seventeenth-century style did not, perhaps could not, come in his conservative native Venice.",
        relation_candidate=False, first=128, last=128,
        mention_ids=["cand-2569", "cand-2719", "cand-8284"],
        qualification="Preserve Haskell's qualification 'perhaps could not'; this is an interpretation of artistic change and place.", ocr=[],
    )
    add_statement("tiepolo-summoned-outside-venice", BODY, "cand-2569", None, "frequently_summoned_outside_venice_in_early_1730s", 128, 129,
                  "Haskell says Tiepolo was frequently summoned outside Venice in the early 1730s.", True,
                  ["cand-2569", "cand-2719"],
                  "The source does not name the commissioners or destinations; preserve the open relation endpoint.")
    add_statement("tiepolo-returned-palette-and-subjects-changed", BODY, "cand-2569", "cand-8284", "palette_lightened_and_subjects_changed_after_return", 129, 129,
                  "Haskell says that by the time Tiepolo returned, his palette had lightened further and his subjects had changed.", False,
                  ["cand-2569", "cand-8284", "cand-2719"],
                  "This summarizes Haskell's account of artistic change; no destination or particular new subjects are supplied.")
    update_statement(
        "st-chp9-p253-barbaro-dolfin-roman-epics", subject="cand-8241", object_="cand-0184",
        predicate="roman_epics_commemorated_antonio_barbaro",
        claim="Haskell says Tiepolo's Roman epics commemorated Antonio Barbaro.",
        relation_candidate=True, first=129, last=129,
        mention_ids=["cand-2569", "cand-8241", "cand-0184"],
        qualification="The statement separates the work's commemorative subject from Haskell's comment that Barbaro's heroic days seemed remote.",
    )
    add_statement("roman-epics-commemorate-daniele-dolfin", BODY, "cand-8241", "cand-0927", "roman_epics_commemorated_a_daniele_dolfin", 129, 129,
                  "Haskell says Tiepolo's Roman epics also commemorated a Daniele Dolfin.", True,
                  ["cand-8241", "cand-0927", "cand-2569"],
                  "The source gives no ordinal; the candidate's identity with Daniele III remains unresolved and must not be treated as confirmed.")
    add_statement("heroic-days-seemed-remote", BODY, None, None, "heroic_days_of_barbaro_and_daniele_dolfin_seemed_remote", 129, 129,
                  "Haskell says the heroic days of an Antonio Barbaro and a Daniele Dolfin must have seemed remote.", False,
                  ["cand-0184", "cand-0927"],
                  "This is Haskell's historical interpretation; the source does not supply an ordinal for Daniele Dolfin.")
    update_statement(
        "st-chp9-p253-two-dolfin-members-imprisoned-or-exiled", subject="cand-8296", object_="cand-8105",
        predicate="two_unnamed_dolfin_members_imprisoned_or_exiled_for_breaking_state_laws",
        claim="Haskell says two unnamed members of the Dolfin family were soon imprisoned or exiled for breaking the State's most fundamental laws.",
        relation_candidate=True, first=129, last=129,
        mention_ids=["cand-8296", "cand-0931", "cand-8105"],
        qualification="The individuals and which one was imprisoned or exiled are not identified; this remains Haskell's reported account.",
    )
    update_statement(
        "st-chp9-p253-venice-neutrality", subject="cand-2719", object_=None,
        predicate="venice_reported_firmly_neutral", claim="Haskell says Venice herself was firmly neutral.",
        relation_candidate=False, first=129, last=129,
        mention_ids=["cand-2719"],
        qualification="This is Haskell's political characterization; the city is not silently substituted for the Venetian government candidate.",
    )
    update_statement(
        "st-chp9-p253-tiepolo-demand-and-artistic-gifts", subject="cand-2569", object_=None,
        predicate="artistic_gifts_and_execution_interpreted_as_creating_demand", claim="Haskell says Tiepolo remained in demand and suggests that his gifts and brilliance of execution created a need for his art as much as they satisfied it.",
        relation_candidate=False, first=130, last=130,
        mention_ids=["cand-2569"],
        qualification="This is explicitly Haskell's interpretive conclusion, not an independently measured market claim.",
    )
    update_statement(
        "st-chp9-p253-tiepolo-patronage-ideal", subject="cand-2569", object_="cand-8295",
        predicate="quoted_advice_to_painters_on_large_scale_work_and_artistic_ideals",
        claim="Haskell reports Tiepolo saying that painters should make large-scale works pleasing to the rich and nobility, who make artists' fortunes, and that a painter's spirit should reach for the sublime, heroic and perfect.",
        relation_candidate=False, first=130, last=130,
        mention_ids=["cand-2569", "cand-8295", "cand-8299", "cand-8108"],
        qualification="This is a translated quotation reported by Haskell; the Italian press version appears separately in note 2.",
        text_layer="quotation reported by Haskell", ocr=[], extra={"footnote_marker": 2, "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 361, "source_line_end": 361}]},
    )
    add_statement("tiepolo-aimed-at-rich-noble-patrons", BODY, "cand-2569", "cand-8299", "deliberately_aimed_at_special_class_of_rich_noble_patron", 130, 130,
                  "Haskell says Tiepolo deliberately aimed at a special class of patron, the rich and nobility.", True,
                  ["cand-2569", "cand-8299"],
                  "The relation is Haskell's account of Tiepolo's intended audience, not evidence that all such patrons commissioned him.")
    update_statement(
        "st-chp9-p253-aristocracy-work-and-fragmentation", subject="cand-2569", object_="cand-8108",
        predicate="worked_incessantly_for_aristocracy_over_next_two_decades",
        claim="Haskell says Tiepolo worked incessantly for the aristocracy over the next two decades.",
        relation_candidate=True, first=131, last=131,
        mention_ids=["cand-2569", "cand-8108"],
        qualification="Keep the two-decade duration and Haskell's characterization 'incessantly'; the aristocracy's fragmentation and ambitions are separate claims.",
        ocr=[{"line": 131, "ocr": "military— and", "reading": "military—and", "basis": "CHP-9.pdf physical p.15"}],
    )
    add_statement("aristocracy-fragmented", BODY, "cand-8108", None, "aristocracy_fragmented_into_individual_components", 131, 131,
                  "Haskell says the Venetian aristocracy was breaking up further into individual components than at the beginning of the century.", False,
                  ["cand-8108"], "This is Haskell's social-historical characterization.")
    add_statement("aristocracy-ambitions-no-longer-military-political", BODY, "cand-8108", None,
                  "aristocratic_ambitions_no_longer_military_and_scarcely_political", 131, 131,
                  "Haskell says the aristocracy's ambitions were no longer military and would soon be scarcely political.", False,
                  ["cand-8108"], "Preserve the source's temporal qualification 'soon'.")
    update_statement(
        "st-chp9-p253-zen-resident-report", subject=None, object_=None,
        predicate="resident_reported_no_candidate_to_succeed_alessandro_zen_as_procurator",
        claim="An unidentified British Resident reporting in 1761 on Procurator Alessandro Zen's death said it was unusual that no candidate had offered to succeed him.",
        relation_candidate=False, first=131, last=132,
        mention_ids=["cand-8287", "cand-2868", "cand-8288", "cand-8105"],
        qualification="The Resident is unnamed; the quotation is reproduced by Haskell and linked to State Papers—Venice 99/68, which was not independently consulted.",
        speaker="Unidentified British Resident (quoted by Haskell)", text_layer="quotation reported by Haskell", ocr=[],
        extra={"footnote_marker": 3, "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 362, "source_line_end": 362}]},
    )
    update_statement(
        "st-chp9-p253-candidate-absence-becoming-commonplace", subject=None, object_=None,
        predicate="absence_of_successor_candidate_said_to_become_more_commonplace",
        claim="Haskell says the absence of a candidate to succeed Procurator Alessandro Zen would become more commonplace.",
        relation_candidate=False, first=132, last=132,
        mention_ids=["cand-8287", "cand-2868", "cand-8288"],
        qualification="'This situation' refers to the absence of an offer to succeed Zen; p.254 L135 completes the contrast, which is linked here.",
        extra={"footnote_marker": 4, "cross_reference_segments": [{"segment_id": "chp-9:09_CHP-9_intro:l134-146", "source_line_start": 135, "source_line_end": 135}]},
    )

    # Notes on the same printed page are covered with the body segment's review.
    update_statement(
        "st-chp9-p253-note1-later-recall-and-chapel", relation_candidate=True,
        claim="Note 1 says that in 1759 the new patriarch Daniele Dolfin, Dionisio's nephew, recalled Tiepolo and his son Gian Domenico to Udine to decorate the Cappella della Purità near the Cathedral.",
        first=360, last=360,
        qualification="This is a separate later commission from Dionisio's earlier Udine Cathedral and Archiepiscopal Palace commission; Haskell's note was not independently verified.",
        mention_ids=["cand-0926", "cand-0929", "cand-2569", "cand-2624", "cand-2666", "cand-8285", "cand-8235"],
    )
    update_statement(
        "st-chp9-p253-note2-press-report-and-italian-quote", subject="cand-2569", object_="cand-8286",
        predicate="italian_press_report_of_tiepolo_statement_published_1762",
        claim="Note 2 says a statement attributed to Tiepolo, made before he left for Spain, was published in the Nuova Veneta Gazzetta on 20 March 1762.",
        relation_candidate=False, first=361, last=361,
        mention_ids=["cand-2569", "cand-8286"],
        qualification="The newspaper issue and Tiepolo's statement are reported through Haskell; neither was independently consulted.",
        speaker="Haskell's footnote", text_layer="footnote",
        ocr=[{"line": 361, "ocr": "Ho udito dite", "reading": "Ho udito dire", "basis": "CHP-9.pdf physical p.15"}],
        extra={"footnote_marker": 2},
    )
    add_statement(
        "note2-italian-advice-to-young-artists", NOTES, "cand-2569", "cand-8297",
        "reported_advice_to_young_artists_to_continue_study_and_seek_sublime", 361, 361,
        "Note 2's Italian press report attributes to Tiepolo advice that young artists, including his pupils, continue studying and pursue large-scale works for wealthy nobles and the sublime, heroic and perfect.",
        True, ["cand-2569", "cand-8297", "cand-8298", "cand-8299", "cand-8295"],
        "This is a newspaper report reproduced by Haskell; preserve it as mediated speech, not independent verification.",
        speaker="Tiepolo as reported in Nuova Veneta Gazzetta via Haskell", text_layer="reported Italian quotation",
        marker=2,
        ocr=[{"line": 361, "ocr": "Ho udito dite", "reading": "Ho udito dire", "basis": "CHP-9.pdf physical p.15"}],
    )
    update_statement(
        "st-chp9-p253-note3-state-papers-locator", relation_candidate=False,
        claim="Note 3 cites the Public Record Office, State Papers—Venice 99/68, page 233, for the British Resident's report.",
        first=362, last=362,
        mention_ids=["cand-8287", "cand-8289", "cand-8290"],
        qualification="This is a source locator; the archival record was not independently consulted.",
    )
    update_statement(
        "st-chp9-p253-note4-provincial-nobles-berengo", subject="cand-8293", object_="cand-8294",
        predicate="provincial_nobles_declined_venetian_patrician_status_in_1775",
        claim="Note 4 says provincial nobles turned down the chance to acquire Venetian patrician status in 1775.",
        relation_candidate=True, first=363, last=363,
        mention_ids=["cand-8293", "cand-8294", "cand-8291", "cand-8292"],
        qualification="Haskell cites Berengo (1955, page 14); the cited page was not independently read.",
        speaker="Haskell's footnote", text_layer="footnote",
        ocr=[{"line": 363, "ocr": "i$>55. P-14-", "reading": "1955, p. 14", "basis": "CHP-9.pdf physical p.15"}],
        extra={"footnote_marker": 4},
    )

    for row in statements:
        q = row.get("qualifiers", {})
        if row["segment_id"] == BODY or (row["segment_id"] == NOTES and 360 <= q.get("source_line_start", 0) <= 363):
            row["original_quote"] = quote(q["source_line_start"], q["source_line_end"])
            q["semantic_review"] = REVIEW


if not args.apply:
    print(f"DRY RUN OK: p.253 physical page 15 confirmed; {len(mention_specs)} pinned mention specs have exact S0 spans and valid candidates.")
    print("14 existing body statements and 4 p.253 note statements are in the expected inventory; 10 body rows and 3 note rows were previously unclassified.")
    print("No files written. Source OCR remains unchanged; note 2's mediated Italian report and note 4's citation remain attributed to Haskell.")
    raise SystemExit(0)

targets = [mention_path, statement_path]
for path in targets:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; inspect before applying: {backup.name}")

before_count = len(statements)
apply_semantic_decisions()
mentions.extend(new_mentions)
if len({row["statement_id"] for row in statements}) != len(statements):
    raise SystemExit("duplicate statement IDs after p.253 review")
reviewed_rows = [row for row in statements if row.get("qualifiers", {}).get("semantic_review") == REVIEW]
for row in reviewed_rows:
    q = row["qualifiers"]
    if q.get("relation_candidate") is None:
        raise SystemExit(f"reviewed statement remains unclassified: {row['statement_id']}")
    for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
        if endpoint not in (None, "") and endpoint not in candidate_ids:
            raise SystemExit(f"invalid candidate endpoint: {row['statement_id']} -> {endpoint}")

for path in targets:
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
atomic_write_csv(mention_path, read_csv(mention_path)[0], mentions)
atomic_write_jsonl(statement_path, statements)
body_rows = [row for row in statements if row["segment_id"] == BODY]
print(f"APPLIED: restored {len(new_mentions)} mentions (46 body, 22 p.253 note); statements {before_count} -> {len(statements)}.")
print(f"p.253 body after review: {len(body_rows)} statements; all body and p.253 note statements classified.")
print(f"BACKUPS: *{BACKUP_SUFFIX}")
