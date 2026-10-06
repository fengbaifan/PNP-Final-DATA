"""Controlled S2 migration for printed p.253; defaults to a read-only dry run."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
P252 = "chp-9:09_CHP-9_intro:l116-122"
P253 = "chp-9:09_CHP-9_intro:l124-132"
P254 = "chp-9:09_CHP-9_intro:l134-146"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
EXPECTED_HASH = "bdcf1ec70bda8a3346f427787148673220496aeed2c647ad5260fcff41744e9a"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p253-offsetfix-20261001"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segments}
for sid in (P252, P253, P254, NOTES):
    if sid not in segment_by_id:
        raise SystemExit(f"missing source segment: {sid}")
meta = segment_by_id[P253]
if meta["sha256"] != EXPECTED_HASH or meta["asset_sha256"] != EXPECTED_ASSET_HASH:
    raise SystemExit("p.253 source segment or source asset fingerprint changed")
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_HASH:
    raise SystemExit("source asset hash changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()


def line_offsets(segment_id):
    m = segment_by_id[segment_id]
    offsets, offset = {}, 0
    for n in range(m["line_start"], m["line_end"] + 1):
        offsets[n] = offset
        offset += len(source_lines[n - 1]) + 1
    return offsets


offsets_by_segment = {sid: line_offsets(sid) for sid in (P252, P253, NOTES)}


def quote(segment_id, first, last):
    return "\n".join(source_lines[n - 1] for n in range(first, last + 1))


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
coverage_by_id = {r["segment_id"]: r for r in coverage}
expected_states = {
    P252: ("reviewed", "partial", "L117-122"),
    P253: ("queued", "pending", ""),
    NOTES: ("reviewed", "partial", "L349-359"),
}
for sid, expected in expected_states.items():
    row = coverage_by_id.get(sid)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != expected:
        raise SystemExit(f"unexpected coverage state for {sid}: {row}")

candidate_ids = {r["candidate_id"] for r in candidates}
if len(candidate_ids) != len(candidates) or max(int(x.split("-")[1]) for x in candidate_ids) != 8276:
    raise SystemExit("candidate inventory changed; inspect before allocating IDs")
candidate_specs = [
    (8277, "Dionisio Dolfin's new Archiepiscopal Palace at Udine", "place", P253, 125,
     "The palace is named only as the setting of Tiepolo's frescoes; its exact formal title and surviving fabric are not established here."),
    (8278, "Staircase in Dionisio Dolfin's new Archiepiscopal Palace at Udine", "place", P253, 125,
     "Interior space named as the first location of Tiepolo's work; no specific architectural description is supplied."),
    (8279, "Gallery in Dionisio Dolfin's new Archiepiscopal Palace at Udine", "place", P253, 125,
     "Interior space in which Haskell places Tiepolo's Abraham scenes."),
    (8280, "Tribunal hall in Dionisio Dolfin's new Archiepiscopal Palace at Udine", "place", P253, 126,
     "Interior space named as the location of The Justice of Solomon."),
    (8281, "Unidentified Tiepolo fresco on the palace staircase ceiling at Udine", "work", P253, 125,
     "Haskell calls its beginning rather melodramatic but gives no title or individual scene."),
    (8282, "Tiepolo's scenes from the life of Abraham in the palace gallery at Udine", "work", P253, 125,
     "The text describes a group of frescoes/scenes, without enumerating or naming individual episodes."),
    (8283, "The Justice of Solomon in the tribunal hall at Udine", "work", P253, 125,
     "Title as printed in the body; the index has a Tiepolo subentry 'Judgment of Solomon', whose identity with this title is deferred to S3."),
    (8284, "Tiepolo's stylistic transition from dark heaviness to incisive line and lighter colour at Udine", "term", P253, 126,
     "Haskell's account of a stylistic change; the palette and evaluative language remain attributed to him."),
    (8285, "Cappella della Purità near Udine Cathedral", "place", NOTES, 360,
     "Named chapel decorated by Tiepolo and Gian Domenico in the 1759 event reported by Haskell's note."),
    (8286, "Nuova Veneta Gazzetta issue of 20 March 1762", "archive", NOTES, 361,
     "Newspaper issue cited as the publication venue for a press statement attributed to Tiepolo; the issue was not independently consulted."),
    (8287, "Unidentified British Resident reporting in Venice in 1761", "person", P253, 131,
     "The source identifies the speaker by diplomatic office only; no personal name is supplied."),
    (8288, "Office of Procurator held by Alessandro Zen", "institution", P253, 131,
     "Office title as given by Haskell; no fuller institutional designation is supplied in this passage."),
    (8289, "Public Record Office", "institution", NOTES, 362,
     "Repository name as printed in the source note; present-day institutional identity is not substituted."),
    (8290, "State Papers—Venice 99/68, page 233", "archive", NOTES, 362,
     "Archival locator cited by Haskell for the British Resident quotation; the record was not independently consulted."),
    (8291, "Marino Berengo", "person", NOTES, 363,
     "Author identified from the book bibliography for the 1955 citation."),
    (8292, "La società Veneta alla fine del '700 (Berengo, Florence, 1955)", "archive", NOTES, 363,
     "Publication identified from the book bibliography; cited page 14 was not independently read."),
    (8293, "Provincial nobles said to have declined Venetian patrician status in 1775", "term", NOTES, 363,
     "Collective group in the note; no individuals or exact number are identified."),
    (8294, "Venetian patrician status as an acquired standing", "term", NOTES, 363,
     "Status named in the note as something provincial nobles could acquire; keep distinct from already established Venetian patrician families."),
    (8295, "Tiepolo's stated ideal of large-scale art for wealthy and noble patrons", "term", P253, 130,
     "Concept conveyed in Haskell's translated quotation and the Italian press report; retain as a reported artistic position."),
    (8296, "Two unnamed Dolfin family members said to have been imprisoned or exiled", "term", P253, 129,
     "The source reports two members of the family collectively but does not name them or specify which member was imprisoned versus exiled."),
    (8297, "Young artists addressed in Tiepolo's reported advice", "term", NOTES, 361,
     "Collective audience in the Italian report; no individuals are identified."),
    (8298, "Tiepolo's unnamed pupils referred to in the Italian report", "term", NOTES, 361,
     "Collective group in the Italian report; no pupils are named."),
    (8299, "Wealthy and noble patrons in Tiepolo's reported advice", "term", P253, 130,
     "Audience described in the quotation; not equated with the specifically Venetian aristocracy elsewhere in the chapter."),
]
existing_natural_keys = {(r["canonical_name"], r["suggested_type"]) for r in candidates}
for n, name, kind, source_segment, line_no, detail in candidate_specs:
    if f"cand-{n:04d}" in candidate_ids or (name, kind) in existing_natural_keys:
        raise SystemExit(f"candidate ID or natural-key collision: {n} {name} / {kind}")
    candidates.append({
        "candidate_id": f"cand-{n:04d}", "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open", "index_source_file": "",
        "sub_entry": "", "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{source_segment}#L{line_no}",
    })
    candidate_ids.add(f"cand-{n:04d}")
    existing_natural_keys.add((name, kind))

existing_mention_ids = {r["mention_id"] for r in mentions}
existing_spans = {(r["segment_id"], r["start_char"], r["end_char"]) for r in mentions}
new_mentions = []


def mention(segment_id, line_no, suffix, cid, surface, note="", occurrence=0):
    mid = f"m-chp9-p253-{suffix}"
    if mid in existing_mention_ids or any(r["mention_id"] == mid for r in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mid}")
    if "\n" in surface:
        line_end = segment_by_id[segment_id]["line_end"]
        search_text = quote(segment_id, line_no, line_end)
        # offsets_by_segment already points to the first character of line_no.
        base_offset = 0
    else:
        search_text = source_lines[line_no - 1]
        base_offset = 0
    start_at = 0
    pos = -1
    for _ in range(occurrence + 1):
        pos = search_text.find(surface, start_at)
        if pos < 0:
            raise SystemExit(f"surface not found at L{line_no}: {surface!r}")
        start_at = pos + len(surface)
    start = offsets_by_segment[segment_id][line_no] + base_offset + pos
    end = start + len(surface)
    span = (segment_id, str(start), str(end))
    if span in existing_spans or any((r["segment_id"], r["start_char"], r["end_char"]) == span for r in new_mentions):
        raise SystemExit(f"duplicate mention span: {mid}")
    if cid not in candidate_ids:
        raise SystemExit(f"missing candidate for mention {mid}: {cid}")
    new_mentions.append({"mention_id": mid, "segment_id": segment_id, "candidate_id": cid,
                         "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


MENTION_SPECS = [
    (P253, 125, "cathedral", "cand-8235", "the Cathedral", "Udine Cathedral, already registered as a place candidate."),
    (P253, 125, "archiepiscopal-palace", "cand-8277", "his new Archiepiscopal Palace", "The pronoun refers to Dionisio in the p.252 continuation, not Daniele Dolfin in note 1."),
    (P253, 125, "palace-staircase", "cand-8278", "the ceiling of the staircase", "Staircase space in Dionisio's new palace."),
    (P253, 125, "artist-coreference", "cand-2569", "the artist", "Giambattista Tiepolo, continued from p.252 L122."),
    (P253, 125, "abraham-scenes", "cand-8282", "scenes from the life of Abraham", "Unidentified scenes in the palace gallery."),
    (P253, 125, "palace-gallery", "cand-8279", "the gallery", "Interior space in the palace."),
    (P253, 125, "justice-of-solomon", "cand-8283", "The Justice of\nSolomon", "Printed p.253 title crosses the OCR line break; index subentry cand-2595 says 'Judgment of Solomon', identity deferred to S3."),
    (P253, 126, "tribunal-hall", "cand-8280", "the hall of the tribunal", "Interior space in Dionisio's palace."),
    (P253, 126, "early-work-style", "cand-8284", "dark and lumpish heaviness", "Haskell's description of Tiepolo's earlier work."),
    (P253, 126, "aristocratic-line", "cand-8284", "aristocratic incisiveness of line", "Haskell's description of the changed style."),
    (P253, 126, "magical-colours", "cand-8284", "magical colours", "The phrase introduces sparkling blues, pinks and greens."),
    (P253, 126, "sparkling-palette", "cand-8284", "sparkling blues and pinks and greens", "Colours named by Haskell as part of the stylistic change."),
    (P253, 126, "airy-background", "cand-8284", "a light airy background", "Haskell's visual description."),
    (P253, 127, "dionisio", "cand-0929", "Dionisio Dolfin", "Dolfin, the patriarch from the preceding pages."),
    (P253, 127, "petty-state", "cand-8248", "his petty state", "Haskell's description of Dionisio's domain; do not treat 'petty state' as a formal constitutional name."),
    (P253, 127, "feudal-bishop", "cand-0929", "some feudal bishop of the Middle Ages", "Simile used by Haskell, not a literal title."),
    (P253, 127, "tiepolo", "cand-2569", "Tiepolo", "Giambattista Tiepolo."),
    (P253, 127, "greatest-painter", "cand-2569", "the greatest painter of the century", "Haskell's evaluation of Tiepolo."),
    (P253, 128, "tiepolo-final-break", "cand-2569", "for Tiepolo", "Tiepolo is the subject of Haskell's interpretation of the stylistic break."),
    (P253, 128, "seventeenth-century-style", "cand-8284", "the heavy style of the seventeenth century", "Period/style category in Haskell's interpretation."),
    (P253, 128, "native-city", "cand-2719", "his native city", "Venice, the antecedent established in context."),
    (P253, 128, "outside-venice", "cand-2719", "outside\nVenice", "The phrase crosses the OCR line break; Venice is the city outside which Tiepolo was summoned."),
    (P253, 129, "antonio-barbaro", "cand-0184", "Antonio Barbaro", "Indexed person candidate; source supplies no further identification here."),
    (P253, 129, "daniele-dolfin-unspecified", "cand-0927", "a Daniele Dolfin", "Index has Daniele III for p.253; name/ordinal identity remains for S3 review."),
    (P253, 129, "roman-epics", "cand-8241", "the Roman epics", "Anaphoric allusion to Tiepolo's Roman-history canvases for the Dolfin."),
    (P253, 129, "latter-family", "cand-0931", "the latter family", "Dolfin family, named immediately before."),
    (P253, 129, "two-dolfin-members", "cand-8296", "two members of the latter family", "Distinct unnamed collective group; do not infer which family members."),
    (P253, 129, "state-laws", "cand-8105", "the State", "Venetian government as the law-making/political entity; distinct from Venice as a city."),
    (P253, 129, "venice-neutrality", "cand-2719", "Venice herself was firmly neutral", "Haskell's metonymic political characterization; retain the named place candidate without converting it into a separate formal state."),
    (P253, 130, "tiepolo-demand", "cand-2569", "Tiepolo", "Subject of Haskell's account of continued demand."),
    (P253, 130, "marvellous-gifts", "cand-2569", "his marvellous gifts and brilliance of execution", "Haskell's assessment."),
    (P253, 130, "special-class-patron", "cand-8299", "a special class of patron", "Tiepolo's stated target audience as reported by Haskell."),
    (P253, 130, "large-scale-works", "cand-8295", "large-scale works", "Scale and audience in the quoted artistic advice."),
    (P253, 130, "rich-and-nobility", "cand-8299", "the rich and the nobility", "Audience named in Tiepolo's reported words."),
    (P253, 130, "sublime-heroic-perfect", "cand-8295", "the sublime, the heroic, the perfect", "Aesthetic ideals in the translated quotation."),
    (P253, 131, "tiepolo-aristocracy-work", "cand-2569", "Tiepolo", "Artist said to work incessantly for the aristocracy."),
    (P253, 131, "aristocracy-fragment", "cand-8108", "an aristocracy that was now breaking up still further into individual components", "Haskell's description of social fragmentation."),
    (P253, 131, "military-ambitions", "cand-8108", "military", "Political/social ambition qualifier for the aristocracy."),
    (P253, 131, "political-ambitions", "cand-8108", "political", "Political/social ambition qualifier for the aristocracy."),
    (P253, 131, "british-resident", "cand-8287", "the British Resident", "Unnamed diplomatic source of the 1761 report."),
    (P253, 131, "procurator-office", "cand-8288", "the Procurator", "Office held by Alessandro Zen."),
    (P253, 131, "alessandro-zen", "cand-2868", "Alessandro Zen", "Indexed procurator named by Haskell."),
    (P253, 131, "resident-quote", "cand-8287", "what is very unusual, and without a precedent", "Part of the Resident's reported quotation."),
    (P253, 131, "candidate-successor", "cand-8288", "a Candidate to succeed him", "The quoted account says no candidate had yet offered."),
    (P253, 132, "republick", "cand-8105", "this Republick", "Archaic spelling retained from the book's quotation."),
    (P253, 132, "situation-commonplace", "cand-8287", "This situation", "Refers to the lack of a candidate to succeed Zen; the next-page contrast remains to be read."),
    (NOTES, 360, "note1-tiepolo", "cand-2569", "Tiepolo", "Tiepolo was recalled to Udine in 1759 in the note's separate later event."),
    (NOTES, 360, "note1-son", "cand-2624", "his son Gian Domenico", "Tiepolo's son, indexed as Gian Domenico Tiepolo."),
    (NOTES, 360, "note1-udine", "cand-2666", "Udine", "Destination of the 1759 recall."),
    (NOTES, 360, "note1-new-patriarch", "cand-0926", "a new patriarch, Daniele Dolfin", "Distinct from Dionisio; index identifies Daniele Dolfin as Archbishop of Udine."),
    (NOTES, 360, "note1-dionisio-nephew", "cand-0929", "nephew of Dionisio", "Explicit kinship in the footnote."),
    (NOTES, 360, "note1-chapel", "cand-8285", "the Cappella della Purità", "The source text preserves the accented name; page image confirms the reading."),
    (NOTES, 360, "note1-cathedral", "cand-8235", "the Cathedral", "Udine Cathedral, separately registered as a place."),
    (NOTES, 361, "note2-press", "cand-8286", "published in the Nuova Veneta Gazzetta", "Newspaper cited as publication venue for the statement."),
    (NOTES, 361, "note2-date", "cand-8286", "20 March 1762", "Publication date in the footnote."),
    (NOTES, 361, "note2-tiepolo-first", "cand-2569", "Tiepolo", "First occurrence: before Tiepolo left for Spain.", 0),
    (NOTES, 361, "note2-tiepolo-speaker", "cand-2569", "Signor Tiepolo", "The speaker is named explicitly in the Italian report."),
    (NOTES, 361, "note2-young-artists", "cand-8297", "molti giovani", "Young artists named in the Italian report; individuals are not identified."),
    (NOTES, 361, "note2-pupils", "cand-8298", "suoi allievi", "Tiepolo's pupils as a collective group."),
    (NOTES, 361, "note2-nobles-rich", "cand-8108", "Signori Nobili, e ricchi", "Audience named in the reported Italian statement."),
    (NOTES, 362, "note3-repository", "cand-8289", "Public Record Office", "Repository named in the citation."),
    (NOTES, 362, "note3-file", "cand-8290", "State Papers—Venice 99/68", "Citation locator; source text and page image preserve the em dash."),
    (NOTES, 362, "note3-page", "cand-8290", "p. 233", "Page locator in State Papers—Venice 99/68."),
    (NOTES, 363, "note4-provincial-nobles", "cand-8293", "provincial nobles", "Collective group; individual nobles are unnamed."),
    (NOTES, 363, "note4-status", "cand-8294", "Venetian patrician status", "Social status they reportedly declined to acquire."),
    (NOTES, 363, "note4-berengo", "cand-8291", "Berengo", "Marino Berengo identified from the book bibliography."),
    (NOTES, 363, "note4-year", "cand-8292", "i$>55", "OCR surface normalized to 1955 against the page image."),
    (NOTES, 363, "note4-page", "cand-8292", "P-14-", "OCR surface normalized to p. 14 against the page image."),
]
for spec in MENTION_SPECS:
    mention(*spec)

new_statements = []
existing_statement_ids = {r["statement_id"] for r in statements}


def statement(suffix, segment_id, first, last, subject, obj, predicate, claim, qualification,
              mentioned, marker=None, note_line=None, speaker="Haskell", text_layer="body", extras=None):
    sid = f"st-chp9-p253-{suffix}"
    if sid in existing_statement_ids or any(r["statement_id"] == sid for r in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    m = segment_by_id[segment_id]
    if first < m["line_start"] or last > m["line_end"]:
        raise SystemExit(f"statement lines outside segment {segment_id}: {sid}")
    if any(cid and cid not in candidate_ids for cid in [subject, obj, *mentioned]):
        raise SystemExit(f"missing candidate in statement: {sid}")
    q = {"source_line_start": first, "source_line_end": last, "printed_page": 253,
         "pdf_physical_page": 15, "claim": claim, "speaker": speaker, "text_layer": text_layer,
         "qualification": qualification, "mentioned_candidate_ids": list(dict.fromkeys(x for x in mentioned if x))}
    if marker is not None:
        q["footnote_marker"] = marker
    if note_line is not None:
        q["cross_reference_segments"] = [{"segment_id": NOTES, "source_line_start": note_line, "source_line_end": note_line}]
    if extras:
        q.update(extras)
    new_statements.append({"statement_id": sid, "segment_id": segment_id,
                           "subject_candidate_id": subject, "object_candidate_id": obj,
                           "predicate": predicate, "qualifiers": q,
                           "original_quote": quote(segment_id, first, last), "origin": "book",
                           "source_file": segment_by_id[segment_id]["source_file"]})


statement("commission-to-palace-and-cathedral", P253, 125, 125, "cand-0929", "cand-2569",
          "summoned_tiepolo_to_paint_frescoes_in_udine_cathedral_and_new_palace",
          "The p.252 sentence continues: Dionisio summoned Tiepolo to paint frescoes in the Cathedral and Dionisio's new Archiepiscopal Palace at Udine.",
          "The destination is resolved by the immediately preceding Udine context; do not merge this earlier commission with the separate 1759 recall by Daniele Dolfin in note 1.",
          ["cand-0929", "cand-2569", "cand-8235", "cand-8277", "cand-2592"],
          extras={"relation_candidate": True, "cross_reference_segments": [{"segment_id": P252, "source_line_start": 122, "source_line_end": 122}]})
statement("udine-fresco-sites-and-works", P253, 125, 126, "cand-2569", "cand-8281",
          "painted_staircase_ceiling_then_abraham_scenes_and_justice_of_solomon",
          "Haskell says Tiepolo made a melodramatic start on the palace staircase ceiling, then painted scenes from Abraham's life in the gallery and The Justice of Solomon in the tribunal hall.",
          "The works are kept distinct by setting and description. The printed title 'Justice' differs from index subentry cand-2595 'Judgment'; their identity remains for S3.",
          ["cand-2569", "cand-8281", "cand-8282", "cand-8283", "cand-8278", "cand-8279", "cand-8280", "cand-2592", "cand-2595"],
          extras={"relationship_candidates": ["located_in", "painted_by"]})
statement("udine-style-transition", P253, 125, 126, "cand-2569", "cand-8284",
          "earlier_dark_heaviness_replaced_by_incisive_line_and_light_palette",
          "Haskell says Tiepolo's earlier dark, lumpish heaviness gave way to aristocratic incisiveness of line and magical sparkling blues, pinks and greens against a light, airy background.",
          "This is Haskell's visual assessment of the work at Udine, not an externally verified style classification.",
          ["cand-2569", "cand-8284"], extras={"ocr_corrections": [
              {"line": 126, "ocr": "colours��sparkling", "reading": "colours—sparkling", "basis": "CHP-9.pdf physical p.15"},
              {"line": 126, "ocr": "greens��set", "reading": "greens—set", "basis": "CHP-9.pdf physical p.15"}]})
statement("dionisio-domain-and-patronage", P253, 127, 127, "cand-0929", "cand-2569",
          "feudal_bishop_simile_and_patron_type_congenial_to_tiepolo",
          "Haskell says Dionisio ruled his small domain like a medieval feudal bishop and was the type of patron most congenial to Tiepolo.",
          "The simile and patron judgment are Haskell's characterization, not a literal title or constitutional description.",
          ["cand-0929", "cand-2569", "cand-8248"], extras={"relation_candidate": True})
statement("dionisio-saw-tiepolo-masterpieces", P253, 127, 127, "cand-0929", "cand-2569",
          "saw_first_masterpieces_shortly_before_dying",
          "Haskell says Dionisio had the privilege of seeing the first masterpieces of the greatest painter of the century shortly before dying.",
          "The statement is Haskell's evaluative framing; note 1 describes a distinct 1759 recall of Tiepolo and his son by Daniele Dolfin.",
          ["cand-0929", "cand-2569", "cand-0926"], marker=1, note_line=360)
statement("tiepolo-break-and-travel", P253, 128, 129, "cand-2569", "cand-2719",
          "final_break_with_heavy_seventeenth_century_style_occurred_outside_venice",
          "Haskell argues that Tiepolo's final break with the heavy seventeenth-century style could not come in his conservative native Venice; in the early 1730s he was frequently summoned outside the city, and by his return his palette had lightened and subjects changed.",
          "This is Haskell's interpretive account of style and travel; the passage does not name all journeys or commissions.",
          ["cand-2569", "cand-8284", "cand-2719"], extras={"ocr_corrections": [
              {"line": 128, "ocr": "did not��perhaps", "reading": "did not—perhaps", "basis": "CHP-9.pdf physical p.15"},
              {"line": 128, "ocr": "could not��come", "reading": "could not—come", "basis": "CHP-9.pdf physical p.15"}]})
statement("barbaro-dolfin-roman-epics", P253, 129, 129, "cand-2569", "cand-8241",
          "roman_epics_commemorated_heroic_days_of_barbaro_and_daniele_dolfin",
          "Haskell says the days of Antonio Barbaro and a Daniele Dolfin seemed remote, like the Roman epics with which Tiepolo had commemorated them.",
          "The Daniele Dolfin referent and the exact scope of the plural 'them' remain unresolved; no individual identity or commission is inferred beyond the passage.",
          ["cand-2569", "cand-0184", "cand-0927", "cand-8241"])
statement("two-dolfin-members-imprisoned-or-exiled", P253, 129, 129, "cand-8296", "cand-8105",
          "two_unnamed_dolfin_members_imprisoned_or_exiled_for_breaking_state_laws",
          "Haskell says two unnamed members of the Dolfin family were soon in prison or exile for breaking the State's fundamental laws.",
          "The individuals and which one was imprisoned or exiled are not identified; this remains a source assertion and relation candidate.",
          ["cand-8296", "cand-0931", "cand-8105"], extras={"relation_candidate": True})
statement("venice-neutrality", P253, 129, 129, "cand-2719", None,
          "venice_remained_firmly_neutral",
          "Haskell says Venice herself was firmly neutral.",
          "This is the author's political characterization of Venice in this passage; the city and governing entity remain distinct candidates.",
          ["cand-8105", "cand-2719"])
statement("tiepolo-demand-and-artistic-gifts", P253, 130, 130, "cand-2569", None,
          "gifts_and_execution_created_demand_for_tiepolo_art",
          "Haskell says Tiepolo remained in demand and suggests that his gifts and brilliance of execution created a need for his art as much as they satisfied it.",
          "This is explicitly Haskell's interpretive conclusion, not an independently measured market claim.", ["cand-2569"])
statement("tiepolo-patronage-ideal", P253, 130, 130, "cand-2569", "cand-8295",
          "aimed_at_large_scale_work_for_rich_and_noble_patrons",
          "Haskell reports that Tiepolo deliberately aimed at a special class of patron and quotes him saying painters should make large-scale works pleasing to the rich and nobility, who make artists' fortunes, while striving for the sublime, heroic and perfect.",
          "The English quotation is Haskell's rendering; note 2 supplies a separate Italian press version, mediated through Haskell.",
          ["cand-2569", "cand-8295", "cand-8299"], marker=2, note_line=361,
          text_layer="quotation reported by Haskell", extras={"ocr_corrections": [
              {"line": 130, "ocr": "that ��painters", "reading": "that 'painters", "basis": "CHP-9.pdf physical p.15"},
              {"line": 130, "ocr": "painter��s spirit", "reading": "painter's spirit", "basis": "CHP-9.pdf physical p.15"},
              {"line": 130, "ocr": "Perfection.��", "reading": "Perfection.'", "basis": "CHP-9.pdf physical p.15"}]})
statement("aristocracy-work-and-fragmentation", P253, 131, 131, "cand-2569", "cand-8108",
          "worked_incessantly_for_fragmenting_aristocracy",
          "Haskell says Tiepolo worked incessantly for the aristocracy over the next two decades as it fragmented further into individual components; its ambitions were no longer military and soon scarcely political.",
          "This is Haskell's account of the aristocracy's composition and ambitions.",
          ["cand-2569", "cand-8108"], extras={"ocr_corrections": [
              {"line": 131, "ocr": "military�� and", "reading": "military—and", "basis": "CHP-9.pdf physical p.15"}]})
statement("zen-resident-report", P253, 131, 132, "cand-8287", "cand-2868",
          "resident_reported_no_candidate_after_zen_death",
          "A British Resident reporting in 1761 on Procurator Alessandro Zen's death said it was highly unusual that no candidate had yet offered to succeed him, despite the office's high dignity in the Republic.",
          "The Resident is unnamed; the quotation is a report reproduced by Haskell and tied to State Papers—Venice 99/68, not independently verified.",
          ["cand-8287", "cand-2868", "cand-8288", "cand-8105"], marker=3, note_line=362,
          speaker="Unidentified British Resident (quoted by Haskell)", text_layer="quotation reported by Haskell",
          extras={"relation_candidate": True, "ocr_corrections": [
              {"line": 131, "ocr": "added: ��what", "reading": "added: 'what", "basis": "CHP-9.pdf physical p.15"},
              {"line": 131, "ocr": "tho��", "reading": "tho'", "basis": "CHP-9.pdf physical p.15"},
              {"line": 132, "ocr": "Republick . . .��.", "reading": "Republick . . .'.", "basis": "CHP-9.pdf physical p.15"}]})
statement("candidate-absence-becoming-commonplace", P253, 132, 132, None, None,
          "lack_of_candidate_said_to_become_more_commonplace",
          "Haskell says this situation would become more commonplace.",
          "The sentence continues on p.254 L135 with a contrast; do not infer the full historical explanation before reading that continuation.",
          ["cand-8287", "cand-2868"], marker=4, note_line=363,
          extras={"cross_reference_segments": [{"segment_id": P254, "source_line_start": 135, "source_line_end": 135}]})
statement("note1-later-recall-and-chapel", NOTES, 360, 360, "cand-0926", "cand-8285",
          "recalled_tiepolo_and_gian_domenico_to_decorate_chapel_in_1759",
          "Note 1 says that in 1759 new patriarch Daniele Dolfin, nephew of Dionisio, recalled Tiepolo and his son Gian Domenico to Udine to decorate Cappella della Purità near the Cathedral.",
          "This is a separate later commission from Dionisio's earlier Cathedral and Archiepiscopal Palace commission; it is Haskell's note, not independently verified.",
          ["cand-0926", "cand-0929", "cand-2569", "cand-2624", "cand-2666", "cand-8285", "cand-8235"],
          speaker="Haskell's footnote", text_layer="footnote", extras={"relation_candidate": True,
          "cross_reference_segments": [{"segment_id": P253, "source_line_start": 127, "source_line_end": 127}]})
statement("note2-press-report-and-italian-quote", NOTES, 361, 361, "cand-2569", "cand-8286",
          "italian_press_reported_tiepolo_advice_on_study_and_patronage",
          "Note 2 says a statement made before Tiepolo left for Spain was published in Nuova Veneta Gazzetta on 20 March 1762; it reports Tiepolo urging young artists, including pupils, to continue studying, produce large works pleasing to wealthy nobles, and aspire to the sublime, heroic and perfect.",
          "The Italian quotation is a newspaper report reproduced by Haskell; neither the issue nor the statement was independently consulted.",
          ["cand-2569", "cand-8286", "cand-8295", "cand-8297", "cand-8298", "cand-8299"], marker=2,
          speaker="Tiepolo as reported in Nuova Veneta Gazzetta via Haskell", text_layer="reported Italian quotation",
          extras={"ocr_corrections": [
              {"line": 361, "ocr": "Ho udito dite", "reading": "Ho udito dire", "basis": "CHP-9.pdf physical p.15"},
              {"line": 361, "ocr": "pi��", "reading": "più", "basis": "CHP-9.pdf physical p.15"},
              {"line": 361, "ocr": "pu��", "reading": "può", "basis": "CHP-9.pdf physical p.15"},
              {"line": 361, "ocr": "gi��", "reading": "già", "basis": "CHP-9.pdf physical p.15"}]})
statement("note3-state-papers-locator", NOTES, 362, 362, "cand-8287", "cand-8290",
          "state_papers_venice_99_68_page_233_cited_for_resident_report",
          "Note 3 cites Public Record Office, State Papers—Venice 99/68, page 233, for the British Resident report.",
          "Archival locator only; no independent consultation is claimed.", ["cand-8287", "cand-8289", "cand-8290"],
          marker=3, speaker="Haskell's footnote", text_layer="footnote")
statement("note4-provincial-nobles-berengo", NOTES, 363, 363, "cand-8293", "cand-8294",
          "provincial_nobles_declined_patrician_status_in_1775",
          "Note 4 says provincial nobles turned down the chance to acquire Venetian patrician status in 1775 and cites Berengo, 1955, page 14; the bibliography identifies Marino Berengo's La società Veneta alla fine del '700.",
          "The claim is reported through Haskell's citation; the cited page was not independently read.",
          ["cand-8293", "cand-8294", "cand-8291", "cand-8292"], marker=4,
          speaker="Haskell's footnote", text_layer="footnote", extras={"ocr_corrections": [
              {"line": 363, "ocr": "i$>55. P-14-", "reading": "1955, p. 14", "basis": "CHP-9.pdf physical p.15"}]})

target_id = "st-chp9-p252-summoned-tiepolo-pending-purpose"
prior = [r for r in statements if r.get("statement_id") == target_id]
if len(prior) != 1:
    raise SystemExit(f"expected one existing p.252 continuation statement, found {len(prior)}")
pq = prior[0]["qualifiers"]
if pq.get("continuation_segment") != P253:
    raise SystemExit(f"unexpected old continuation pointer: {pq.get('continuation_segment')}")
pq["qualification"] = "The following page supplies the fresco commission's destination; the exact Venice family palace remains unidentified."
pq.pop("continuation_segment", None)
pq["cross_reference_segments"] = [{"segment_id": P253, "source_line_start": 125, "source_line_end": 125}]

if len({r["mention_id"] for r in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("mention IDs are not unique")
if len({r["statement_id"] for r in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("statement IDs are not unique")
coverage_by_id[P252].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L117-122",
    "note": "Printed p.252 L117 closes p.251 L114. The final body clause continues at p.253 L125, where its Udine fresco destinations are now recorded; p.252 is complete. Notes 1-7 are recorded at consolidated lines L353-359.",
})
coverage_by_id[P253].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L125-132",
    "note": "Printed p.253 (CHP-9.pdf physical p.15) reviewed against the page image. L125 completes p.252's Tiepolo commission. L132 ends 'This situation was to become more commonplace' and continues on p.254 L135; keep partial. Note 1's 1759 recall by Daniele Dolfin is distinct from Dionisio's earlier commission. The indexed 'Judgment of Solomon' subentry differs from the printed title 'The Justice of Solomon'; defer identity to S3. S2-only OCR corrections are recorded in statements, S0 unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L349-363",
    "note": "Consolidated notes through p.253 note 4 are now semantically processed in source order at L349-363. Later notes remain unprocessed; citation locators are not independent source verification.",
})

summary = {"segments": {sid: [coverage_by_id[sid]["disposition"], coverage_by_id[sid]["migration_status"],
                               coverage_by_id[sid]["source_line_ranges"]] for sid in (P252, P253, NOTES)},
           "new_candidates": len(candidate_specs), "new_mentions": len(new_mentions),
           "new_statements": len(new_statements), "source_hash": meta["sha256"],
           "next_continuation": f"{P254}#L135"}
print(json.dumps(summary, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the preflighted migration")
args = parser.parse_args()
if args.apply:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = []
    for path in paths:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path, backup)
        backups.append(backup)
    try:
        write_csv(candidate_path, candidate_fields, candidates)
        write_csv(mention_path, mention_fields, mentions + new_mentions)
        write_jsonl(statement_path, statements + new_statements)
        write_csv(coverage_path, coverage_fields, list(coverage_by_id.values()))
    except Exception:
        for path, backup in zip(paths, backups):
            shutil.copy2(backup, path)
        raise
    print("applied; backups: " + ", ".join(str(x.relative_to(ROOT)) for x in backups))
else:
    print("dry-run only; no files written")
