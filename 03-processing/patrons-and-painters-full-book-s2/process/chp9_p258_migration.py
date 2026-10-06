"""Controlled S2 migration for printed p.258; defaults to a read-only dry run."""
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
P257 = "chp-9:09_CHP-9_intro:l167-177"
P258 = "chp-9:09_CHP-9_intro:l179-186"
P259 = "chp-9:09_CHP-9_intro:l188-200"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
EXPECTED_HASH = "641f4a86d91e032087e759e6f7d7e3cf356c4cf622a4821ecebc507953276658"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p258-20261001"


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
for sid in (P257, P258, P259, NOTES):
    if sid not in segment_by_id:
        raise SystemExit(f"missing source segment: {sid}")
meta = segment_by_id[P258]
if meta["sha256"] != EXPECTED_HASH or meta["asset_sha256"] != EXPECTED_ASSET_HASH:
    raise SystemExit("p.258 source segment or source asset fingerprint changed")
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


offsets_by_segment = {sid: line_offsets(sid) for sid in (P258, NOTES)}


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
    P257: ("reviewed", "partial", "L168-177"),
    P258: ("queued", "pending", ""),
    NOTES: ("reviewed", "partial", "L349-386; p.255 L155 continuation"),
}
for sid, expected in expected_states.items():
    row = coverage_by_id.get(sid)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != expected:
        raise SystemExit(f"unexpected coverage state for {sid}: {row}")

candidate_ids = {r["candidate_id"] for r in candidates}
if len(candidate_ids) != len(candidates) or max(int(x.split("-")[1]) for x in candidate_ids) != 8436:
    raise SystemExit("candidate inventory changed; inspect before allocating IDs")
candidate_specs = [
    (8437, "French artists as the stylistic comparison group on p.258", "term", P258, 180,
     "Unnamed French painters invoked in the continuation of Haskell's comparison; no individual is inferred."),
    (8438, "Bathsheba bathing as an erotic painting subject in Haskell's comparison", "term", P258, 180,
     "A general subject type, not a particular painting or identified version."),
    (8439, "Susanna and the Elders as an erotic painting subject in Haskell's comparison", "term", P258, 180,
     "A general subject type, not a particular painting or identified version."),
    (8440, "Aurora and Flora as mythological painting subjects in Haskell's comparison", "term", P258, 180,
     "Named as general mythological subjects; no specific work or version is identified."),
    (8441, "Roman and Greek history as painting subjects in Haskell's comparison", "term", P258, 180,
     "Historical subject category contrasted with mythological subjects; keep distinct from the history-painting genre."),
    (8442, "Homer (named source of romantic subjects in the Valmarana fresco cycle)", "person", P258, 182,
     "Source-level author candidate; no external identity work is added."),
    (8443, "Unidentified son of Giambattista Tiepolo (source role only)", "person", P258, 184,
     "Named only as Tiepolo's son; do not infer a personal name or match to a separate candidate at S2."),
    (8444, "Villa Valmarana at Vicenza in Haskell's p.258 account", "place", P258, 183,
     "The villa named as the setting of the fresco cycle; no precise architectural complex is inferred."),
    (8445, "Foresteria at Villa Valmarana", "place", P258, 184,
     "The guesthouse space named as the location of rustic frescoes; no fuller building identity is supplied."),
    (8446, "Unidentified rustic frescoes by Tiepolo's son in the Villa Valmarana foresteria", "work", P258, 184,
     "Specific decorative works are mentioned but not titled or described individually."),
    (8447, "Unidentified patrons of Tiepolo's Villa Valmarana fresco cycle", "term", P258, 183,
     "Haskell says too little is known about the patrons to explain the commission; no patron identity is supplied."),
    (8448, "Official historiographer of the Venetian Republic (office)", "term", P258, 186,
     "Office named in Haskell's account of Marco Foscarini's 1734 appointment."),
    (8449, "Procuratore di San Marco (Venetian office)", "term", P258, 186,
     "Office named in Haskell's account; not an institution or a personal name."),
    (8450, "Doge of Venice (office in Haskell's Marco Foscarini account)", "term", P258, 186,
     "Office named in Haskell's account; the source gives only a few months of tenure before Foscarini's death."),
    (8451, "Conservative causes in Haskell's account of Marco Foscarini", "term", P258, 186,
     "Political orientation described by Haskell; no specific cause or organization is named on this page."),
    (8452, "Parenzo named in the 1765 Valmarana funeral oration title", "place", NOTES, 388,
     "Place as printed in the title; no modern geographic alignment is added here."),
    (8453, "Levey, Journal of Warburg Institute, 1957, pages 298–317 (citation locator)", "archive", NOTES, 387,
     "Citation locator for the Tiepolo/Valmarana discussion; not independently consulted."),
    (8454, "Ne' Solenni funerali for Leonardo Count Valmarana, Parenzo, 27 April 1765 (citation title)", "archive", NOTES, 388,
     "Funeral oration quoted by Haskell for Leonardo Valmarana's character; bibliographic text was not independently consulted."),
    (8455, "Tommaso Gar (citation form in p.258 note 3)", "person", NOTES, 388,
     "Author named by Haskell as a useful general account; no first or middle name is inferred."),
    (8456, "Tommaso Gar, 1843, general account of Marco Foscarini (citation locator)", "archive", NOTES, 388,
     "Title and publication details are not supplied in the note; citation not independently consulted."),
    (8457, "Emilio Morpurgo (citation form in p.258 note 3)", "person", NOTES, 388,
     "Author named by Haskell; no further identity is inferred."),
]
natural_keys = {(r["canonical_name"], r["suggested_type"]) for r in candidates}
for n, name, kind, source_segment, line_no, detail in candidate_specs:
    cid = f"cand-{n:04d}"
    if cid in candidate_ids or (name, kind) in natural_keys:
        raise SystemExit(f"candidate ID or natural-key collision: {cid} {name} / {kind}")
    candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open", "index_source_file": "",
        "sub_entry": "", "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{source_segment}#L{line_no}",
    })
    candidate_ids.add(cid)
    natural_keys.add((name, kind))

existing_mention_ids = {r["mention_id"] for r in mentions}
existing_spans = {(r["segment_id"], r["start_char"], r["end_char"]) for r in mentions}
new_mentions = []


def mention(segment_id, first_line, suffix, cid, surface, note="", last_line=None, occurrence=0):
    mid = f"m-chp9-p258-{suffix}"
    if mid in existing_mention_ids or any(r["mention_id"] == mid for r in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mid}")
    last_line = first_line if last_line is None else last_line
    search_text = "\n".join(source_lines[n - 1] for n in range(first_line, last_line + 1))
    start_at = 0
    pos = -1
    for _ in range(occurrence + 1):
        pos = search_text.find(surface, start_at)
        if pos < 0:
            raise SystemExit(f"surface not found at L{first_line}-{last_line}: {surface!r}")
        start_at = pos + len(surface)
    start = offsets_by_segment[segment_id][first_line] + pos
    end = start + len(surface)
    span = (segment_id, str(start), str(end))
    if span in existing_spans or any((r["segment_id"], r["start_char"], r["end_char"]) == span for r in new_mentions):
        raise SystemExit(f"duplicate mention span: {mid}")
    if cid not in candidate_ids:
        raise SystemExit(f"missing candidate for mention {mid}: {cid}")
    new_mentions.append({"mention_id": mid, "segment_id": segment_id, "candidate_id": cid,
                         "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


MENTION_SPECS = [
    (P258, 180, "french-artists-comparison", "cand-8437", "the French", "Artistic comparison group continuing p.257's Boucher/Fragonard comparison."),
    (P258, 180, "pellegrini", "cand-1862", "Pellegrini", "Existing indexed person candidate reused."),
    (P258, 180, "rosalba-carriera", "cand-0581", "Rosalba Carriera", "Existing indexed person candidate reused."),
    (P258, 180, "bathsheba-subject", "cand-8438", "Bathsheba bathing", "General subject, not a particular work."),
    (P258, 180, "susanna-elders-subject", "cand-8439", "Susanna and the Elders", "General subject, not a particular work."),
    (P258, 180, "eroticism", "cand-8424", "eroticism", "Concept in the source's historical comparison."),
    (P258, 180, "mythological-subjects", "cand-8440", "mythologies such as Aurora, Flora", "General mythological subject category and its examples."),
    (P258, 180, "roman-greek-history-subjects", "cand-8441", "scenes from Roman and-Greek history", "As printed in the OCR; the hyphen is visible in the scan."),
    (P258, 180, "guardi-name", "cand-1245", "Gian\nAntonio Guardi", "Name crosses the OCR line boundary; existing indexed candidate reused.", 181),
    (P258, 181, "paris", "cand-4653", "Paris", "Place where Haskell says Guardi would have succeeded."),
    (P258, 182, "tiepolo", "cand-2569", "Tiepolo", "Existing person candidate reused."),
    (P258, 182, "valmarana-fresco-series", "cand-2594", "beautiful series of frescoes", "Existing index candidate for the Homer/Virgil/Tasso/Ariosto cycle reused."),
    (P258, 182, "homer", "cand-8442", "Homer", "Named source author for the cycle's romantic subjects."),
    (P258, 182, "virgil", "cand-2777", "Virgil", "Existing indexed person candidate reused."),
    (P258, 182, "tasso", "cand-2544", "Tasso", "Existing indexed person candidate reused."),
    (P258, 182, "ariosto", "cand-0116", "Ariosto", "Existing indexed person candidate reused."),
    (P258, 183, "valmarana-family", "cand-2688", "Valmarana family", "Existing indexed family candidate reused."),
    (P258, 183, "vicenza", "cand-2769", "Vicenza", "Existing locality candidate reused."),
    (P258, 183, "commission-patrons", "cand-8447", "its patrons", "Unidentified patrons of the fresco commission."),
    (P258, 183, "leonardo-valmarana", "cand-2689", "Leonardo Valmarana", "Existing indexed person candidate reused."),
    (P258, 183, "family-head", "cand-2688", "the head of the family", "Valmarana family in the qualified 1757 report."),
    (P258, 183, "frescoes-1757", "cand-2594", "the frescoes", "The Valmarana series described in the previous line."),
    (P258, 184, "funeral-oration-reference", "cand-8454", "a funeral oration", "Source type stated by Haskell; the full citation is in note 2."),
    (P258, 184, "tiepolo-villa-work", "cand-2569", "Tiepolo’s work", "Tiepolo's work at the named Villa Valmarana."),
    (P258, 184, "villa-valmarana", "cand-8444", "Villa Valmarana", "Place named as the site of Tiepolo's work."),
    (P258, 184, "tiepolo-son", "cand-8443", "his son", "The immediate antecedent is Tiepolo; no name is inferred."),
    (P258, 184, "foresteria", "cand-8445", "the foresteria", "Guesthouse space at the villa."),
    (P258, 184, "son-rustic-frescoes", "cand-8446", "rustic frescoes", "Unspecified works by Tiepolo's unnamed son."),
    (P258, 185, "patricians", "cand-8108", "patricians", "Venetian patricians in Haskell's context."),
    (P258, 185, "marco-foscarini", "cand-1053", "Marco Foscarini", "Existing indexed person candidate reused."),
    (P258, 185, "venice-descent", "cand-2719", "Venice", "Place in the Foscarini family descent claim."),
    (P258, 185, "foscarini-family", "cand-1057", "one of the oldest families", "Foscarini family in the descent claim."),
    (P258, 185, "bologna-education", "cand-3398", "Bologna", "City where Foscarini was educated; typed locality candidate reused."),
    (P258, 185, "paris-travel", "cand-4653", "Paris", "City in Foscarini's travels."),
    (P258, 185, "vienna-travel", "cand-2772", "Vienna", "City in Foscarini's travels and diplomatic service."),
    (P258, 186, "rome-travel", "cand-4490", "Rome", "City in Foscarini's travels and diplomatic service; sentence carries over from printed p.258 line 185."),
    (P258, 186, "historiographer-office", "cand-8448", "official historiographer", "Office held by Foscarini from 1734."),
    (P258, 186, "republic", "cand-8105", "the RepubHc", "Raw OCR mention of the Venetian political entity; corrected to Republic in the statement metadata."),
    (P258, 186, "venetian-literature-history", "cand-2719", "Venetian literature and history", "Venetian cultural subjects in the account of Foscarini's interests."),
    (P258, 186, "venice-political-thought", "cand-2719", "Venice", "Ancient glories of Venice in the account of Foscarini's political thinking."),
    (P258, 186, "procuratore-office", "cand-8449", "Procuratore di San Marco", "Venetian office named by Haskell."),
    (P258, 186, "doge-office", "cand-8450", "Doge", "Venetian office named by Haskell."),
    (P258, 186, "conservative-causes", "cand-8451", "conservative causes", "Political orientation described by Haskell."),
    (P258, 186, "angelo-querini-first-name", "cand-2075", "Angelo", "First part of the name split at the p.258/p.259 source boundary."),
    (NOTES, 387, "levey-note-author", "cand-3843", "Levey", "Existing person candidate reused."),
    (NOTES, 387, "levey-article", "cand-8453", "Journal of Warburg Institute, 1957, pp. 298-317", "Citation locator as printed."),
    (NOTES, 388, "parenzo-in-title", "cand-8452", "Parenzo", "Place named in the funeral-oratation title."),
    (NOTES, 388, "funeral-oration-title", "cand-8454", "Ne’ Solenni funerali celebrati nella Cartedrale Chiesa di Parenzo if di 27 Aprile 1765", "Raw OCR title surface; scan corrects Cattedrale/il dì."),
    (NOTES, 388, "leonardo-in-title", "cand-2689", "Leonardo Co: Valmarana", "Person named in the funeral-oratation title."),
    (NOTES, 388, "venezia-publication-place", "cand-2719", "In Venezia", "Publication place in the title."),
    (NOTES, 388, "gar-author", "cand-8455", "Tommaso Gar", "Author named in note 3."),
    (NOTES, 388, "gar-publication", "cand-8456", "Tommaso Gar, 1843", "Citation locator; title is not supplied."),
    (NOTES, 388, "morpurgo-author", "cand-8457", "Emilio Morpurgo", "Author named in note 3."),
]
for spec in MENTION_SPECS:
    mention(*spec)

new_statements = []
existing_statement_ids = {r["statement_id"] for r in statements}


def statement(suffix, segment_id, first, last, subject, obj, predicate, claim, qualification,
              mentioned, marker=None, speaker="Haskell", text_layer="body", extras=None):
    sid = f"st-chp9-p258-{suffix}"
    if sid in existing_statement_ids or any(r["statement_id"] == sid for r in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    m = segment_by_id[segment_id]
    if first < m["line_start"] or last > m["line_end"]:
        raise SystemExit(f"statement lines outside segment {segment_id}: {sid}")
    if any(cid and cid not in candidate_ids for cid in [subject, obj, *mentioned]):
        raise SystemExit(f"missing candidate in statement: {sid}")
    q = {"source_line_start": first, "source_line_end": last, "printed_page": 258,
         "pdf_physical_page": 20, "claim": claim, "speaker": speaker, "text_layer": text_layer,
         "qualification": qualification,
         "mentioned_candidate_ids": list(dict.fromkeys(x for x in mentioned if x))}
    if marker is not None:
        q["footnote_marker"] = marker
    if extras:
        q.update(extras)
    new_statements.append({"statement_id": sid, "segment_id": segment_id,
                           "subject_candidate_id": subject, "object_candidate_id": obj,
                           "predicate": predicate, "qualifiers": q,
                           "original_quote": quote(segment_id, first, last), "origin": "book",
                           "source_file": segment_by_id[segment_id]["source_file"]})


statement("pellegrini-carriera-more-success-abroad", P258, 180, 180, "cand-1862", "cand-0581",
          "artists_closest_to_french_comparison_succeeded_more_abroad_than_venice",
          "Haskell says the artists who most nearly approached the French from this point of view, Pellegrini and Rosalba Carriera, appear to have had more success abroad than in Venice.",
          "Preserve 'appear to have'; the comparison continues p.257's Boucher/Fragonard point and does not quantify success.",
          ["cand-8437", "cand-1862", "cand-0581", "cand-0421", "cand-1063"],
          extras={"cross_reference_segments": [{"segment_id": P257, "source_line_start": 177, "source_line_end": 177}]})
statement("erotic-subjects-less-common-later", P258, 180, 180, "cand-8438", "cand-8439",
          "biblical_subjects_used_as_erotic_pretexts_became_rarer",
          "Haskell says Bathsheba bathing and Susanna and the Elders, once enormously popular as pretexts for eroticism toward the end of the seventeenth century, later became much rarer.",
          "This is Haskell's qualitative account; the passage names no specific paintings or quantitative evidence.",
          ["cand-8438", "cand-8439", "cand-8424"],
          extras={"ocr_corrections": [{"source_line": 180, "ocr": "seventeenthcentury", "print": "seventeenth-century", "basis": "CHP-9.pdf physical page 20; word broken at the printed line end."}]})
statement("mythologies-less-demanded-than-classical-history", P258, 180, 180, "cand-8440", "cand-8441",
          "mythological_subjects_less_in_demand_than_roman_greek_history",
          "Haskell says subjects such as Aurora and Flora were less in demand than scenes from Roman and Greek history.",
          "The comparison is about subject demand, not the relative quality or number of surviving works.",
          ["cand-8440", "cand-8441"])
statement("guardi-venice-paris-career", P258, 180, 181, "cand-1245", None,
          "magical_but_unserious_guardi_had_small_venice_career_and_would_succeed_in_paris",
          "Haskell characterizes Gian Antonio Guardi as magical but quite unserious, says his career in Venice was relatively insignificant, and says he would surely have triumphed in Paris.",
          "Preserve the author's evaluative adjectives and 'surely'; Paris success is a counterfactual judgment, not an event.",
          ["cand-1245", "cand-2719", "cand-4653"])
statement("tiepolo-rarely-left-grandeur", P258, 182, 182, "cand-2569", None,
          "rarely_strayed_from_grandeur_to_pure_enchantment",
          "Haskell says Tiepolo only very rarely strayed from dreams of grandeur into pure enchantment.",
          "Authorial characterization that introduces the Valmarana fresco cycle as the most striking instance.",
          ["cand-2569"])
statement("tiepolo-painted-valmarana-fresco-cycle", P258, 182, 183, "cand-2569", "cand-2594",
          "painted_romantic_fresco_series_for_valmarana_family_at_vicenza",
          "Haskell says Tiepolo painted a beautiful series of frescoes for the Valmarana family at Vicenza, illustrating romantic scenes from Homer, Virgil, Tasso and Ariosto.",
          "Reuse the exact page-specific index work candidate; do not turn the named literary sources into identified scenes or individual fresco titles.",
          ["cand-2569", "cand-2594", "cand-2688", "cand-2769", "cand-8444", "cand-8442", "cand-2777", "cand-2544", "cand-0116", "cand-3843", "cand-8453"],
          marker=1, extras={"relation_candidate": True, "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 387, "source_line_end": 387}]})
statement("valmarana-commission-circumstances-unknown", P258, 183, 183, "cand-2594", "cand-8447",
          "circumstances_and_patrons_too_little_known_to_explain_interlude",
          "Haskell says too little is known about the circumstances of the Valmarana commission and its patrons to explain this interlude in Tiepolo's career.",
          "The patrons remain unidentified; do not infer the family collectively commissioned the cycle unless the source says so.",
          ["cand-2594", "cand-8447", "cand-2569"])
statement("leonardo-valmarana-seems-family-head-in-1757", P258, 183, 183, "cand-2689", "cand-2688",
          "seems_to_have_been_head_of_family_when_frescoes_painted_1757",
          "Haskell says Leonardo Valmarana seems to have been the head of the family when the frescoes were painted in 1757.",
          "Nested report: Haskell says 'we are told' and retains 'seems'; do not state the role or date as independently established.",
          ["cand-2689", "cand-2688", "cand-2594"], marker=2,
          extras={"relation_candidate": True, "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 388, "source_line_end": 388}]})
statement("funeral-orator-portrait-of-leonardo", P258, 183, 184, "cand-2689", None,
          "funeral_oration_describes_leonardo_as_gentle_humble_and_unostentatious",
          "The funeral oration quoted by Haskell describes Leonardo Valmarana as sweet-tempered, agreeable, free from display and pride, humble, and mindful that true nobility is not boasting of ancestors.",
          "This is a funeral oration's character portrait, not an impartial biography; preserve Haskell's caveat and do not assert each attributed quality as verified fact.",
          ["cand-2689", "cand-8454", "cand-8452"], marker=2, speaker="Funeral oration as quoted by Haskell",
          extras={"cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 388, "source_line_end": 388}]})
statement("haskell-weighs-funeral-oration-and-virtue", P258, 184, 184, "cand-8454", None,
          "funeral_oration_not_impartial_but_virtue_emphasis_is_noteworthy",
          "Haskell says the funeral oration is not the most reliable source for an impartial estimate of Leonardo's character, but its emphasis on a virtue rarely praised in eighteenth-century Venetian orations is worth bearing in mind.",
          "Keep Haskell's explicit source criticism and interpretive qualification; the oration was not independently consulted.",
          ["cand-8454", "cand-2689"],
          extras={"ocr_corrections": [{"source_line": 184, "ocr": "reHable", "print": "reliable", "basis": "CHP-9.pdf physical page 20."}]})
statement("valmarana-virtue-helps-explain-decorations", P258, 184, 184, "cand-2689", "cand-2594",
          "reported_virtue_worth_considering_for_tiepolo_and_sons_valmarana_decorations",
          "Haskell says the reported virtue is worth bearing in mind when explaining the exceptional nature of Tiepolo's Villa Valmarana work and the rustic frescoes by his son in the foresteria.",
          "This is Haskell's interpretive link; it does not establish Leonardo's direct patronage or the son's identity.",
          ["cand-2689", "cand-2569", "cand-2594", "cand-8443", "cand-8444", "cand-8445", "cand-8446"],
          extras={"relation_candidate": True})
statement("marco-foscarini-stands-out-among-patricians", P258, 185, 185, "cand-1053", "cand-8108",
          "struck_contemporaries_for_rectitude_intellectual_authority_and_political_stature",
          "Haskell presents Marco Foscarini as one man among the decorating patricians who especially struck his contemporaries for rectitude, intellectual authority and political stature.",
          "This is Haskell's characterization of contemporaries' view, not an independently verified assessment.",
          ["cand-1053", "cand-8108"])
statement("marco-foscarini-descended-from-old-family", P258, 185, 185, "cand-1053", "cand-1057",
          "descended_from_one_of_oldest_families_in_venice",
          "Haskell says Marco Foscarini descended from one of the oldest families in Venice.",
          "Retain the author's family-history claim as sourced; formal family membership and identity remain subject to S3 alignment.",
          ["cand-1053", "cand-1057", "cand-2719"], marker=3,
          extras={"relation_candidate": True, "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 388, "source_line_end": 388}]})
statement("marco-education-travel-and-ambassadorship", P258, 185, 186, "cand-1053", None,
          "educated_in_bologna_travelled_europe_and_served_as_ambassador_in_vienna_and_rome",
          "Haskell says Foscarini was educated in Bologna, travelled to Paris, Vienna and Rome, and served as ambassador in the latter two cities.",
          "This is the source's biographical account; it does not specify the dates or mission details of the ambassadorships.",
          ["cand-1053", "cand-3398", "cand-4653", "cand-2772", "cand-4490"], extras={"relation_candidate": True})
statement("marco-appointed-historiographer-1734", P258, 186, 186, "cand-1053", "cand-8448",
          "appointed_official_historiographer_of_republic_in_1734",
          "Haskell says Marco Foscarini was appointed official historiographer of the Republic in 1734.",
          "The sentence adds that he never wrote the volumes expected of him; the appointment is reported by Haskell, not externally checked here.",
          ["cand-1053", "cand-8448", "cand-8105"], extras={"relation_candidate": True,
          "ocr_corrections": [{"source_line": 186, "ocr": "RepubHc", "print": "Republic", "basis": "CHP-9.pdf physical page 20."}]})
statement("marco-literary-history-interests-and-studies", P258, 186, 186, "cand-1053", None,
          "passionately_interested_in_venetian_literature_history_and_planned_studies",
          "Haskell says Foscarini remained passionately interested in Venetian literature and history, planned several studies, and published only some during his lifetime.",
          "The individual studies are not named; do not create titles or infer a complete bibliography.",
          ["cand-1053", "cand-2719"])
statement("ancient-glories-shaped-foscarini-politics", P258, 186, 186, "cand-1053", "cand-2719",
          "love_of_venices_past_and_ancient_glories_affected_political_thinking",
          "Haskell says Foscarini's love of the past and dwelling on Venice's ancient glories deeply affected his political thinking.",
          "This is Haskell's explanation of Foscarini's political thinking, not an independently reconstructed causal account.",
          ["cand-1053", "cand-2719"])
statement("marco-held-procuratore-and-doge-offices", P258, 186, 186, "cand-1053", None,
          "procuratore_from_1741_then_doge_for_few_months_before_1763_death",
          "Haskell says Foscarini served as Procuratore di San Marco from 1741 and later as Doge for a few months before his death in 1763.",
          "Preserve the source's relative chronology and short tenure; no exact Doge dates are supplied.",
          ["cand-1053", "cand-8449", "cand-8450"], extras={"relation_candidate": True})
statement("marco-increasingly-identified-with-conservatism", P258, 186, 186, "cand-1053", "cand-8451",
          "increasingly_identified_with_conservative_causes",
          "Haskell says Foscarini became increasingly identified with conservative causes.",
          "The source does not specify a party or list the causes here.", ["cand-1053", "cand-8451"])
statement("marco-strongest-stand-against-querini", P258, 186, 186, "cand-1053", "cand-2075",
          "took_strongest_stand_against_angelo_querini",
          "Haskell says Foscarini took the strongest stand against Angelo Querini.",
          "The surname crosses the page/source-segment boundary and closes at p.259 L188; preserve this as a relation candidate, not a formal relation.",
          ["cand-1053", "cand-2075"], extras={"relation_candidate": True,
          "cross_reference_segments": [{"segment_id": P259, "source_line_start": 188, "source_line_end": 188}]})

statement("note1-levey-article-citation", NOTES, 387, 387, "cand-3843", "cand-8453",
          "citation_locator_levey_journal_of_warburg_institute_1957_pages_298_to_317",
          "Haskell's note 1 cites Levey in the Journal of Warburg Institute, 1957, pages 298–317.",
          "Citation locator only; the article was not independently consulted.",
          ["cand-3843", "cand-8453", "cand-2594"], marker=1, speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"cross_reference_segments": [{"segment_id": P258, "source_line_start": 182, "source_line_end": 183}]})
statement("note2-valmarana-funeral-oration-citation", NOTES, 388, 388, None, "cand-8454",
          "citation_locator_1765_parenzo_funeral_oration_for_leonardo_valmarana",
          "Haskell's note 2 cites a 1765 funeral oration for Leonardo Count Valmarana, delivered at Parenzo and printed in Venice.",
          "Citation locator only; the oration was not independently consulted. Page image corrects the OCR title forms 'Cartedrale' and 'if di'.",
          ["cand-8454", "cand-2689", "cand-8452", "cand-2719"], marker=2, speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"ocr_corrections": [{"line": 388, "ocr": "Cartedrale ... if di", "reading": "Cattedrale ... il dì", "basis": "CHP-9.pdf physical p.20"}],
                  "cross_reference_segments": [{"segment_id": P258, "source_line_start": 183, "source_line_end": 184}]})
statement("note3-general-foscarini-accounts-citation", NOTES, 388, 388, "cand-1053", None,
          "useful_general_accounts_by_gar_1843_and_morpurgo",
          "Haskell's note 3 says many works address Marco Foscarini's political and literary careers and names Tommaso Gar, 1843, and Emilio Morpurgo as the most useful general accounts.",
          "Citation pointers only; titles and full publication details are not supplied or independently checked.",
          ["cand-1053", "cand-8455", "cand-8456", "cand-8457"], marker=3,
          speaker="Haskell's footnote", text_layer="footnote citation",
          extras={"cross_reference_segments": [{"segment_id": P258, "source_line_start": 185, "source_line_end": 185}]})

if len({r["mention_id"] for r in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("mention IDs are not unique")
if len({r["statement_id"] for r in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("statement IDs are not unique")

for cid, detail in {
    "cand-1053": "Haskell's p.258 account presents Marco Foscarini as a Venetian statesman and writer, covering family descent, education, diplomatic service, historiography, political interests and offices; this is source-reported biography, not external verification.",
    "cand-1057": "Named as Marco Foscarini's family in Haskell's p.258 descent statement; this remains source-reported pending broader family/identity alignment.",
    "cand-2688": "Named as the family for whom Tiepolo painted a romantic fresco cycle at Vicenza; Leonardo Valmarana is said to have been its head in 1757, with the qualification and funeral-oration source preserved at p.258.",
    "cand-2689": "Haskell reports that Leonardo Valmarana seems to have headed the family when Tiepolo's frescoes were painted in 1757; his character portrait is quoted from a funeral oration, not independently verified.",
}.items():
    matches = [r for r in candidates if r["candidate_id"] == cid]
    if len(matches) != 1:
        raise SystemExit(f"expected one candidate to update: {cid}")
    matches[0]["detail"] = detail

prior = [r for r in statements if r.get("statement_id") == "st-chp9-p257-no-venetian-equivalent-to-boucher-fragonard"]
if len(prior) != 1:
    raise SystemExit("expected one p.257 final comparison statement")
prior[0]["qualifiers"]["qualification"] = "P.258 L180 completes the sentence by naming Pellegrini and Rosalba Carriera as the Venetian artists who most nearly approached the French comparison; the source's 'appear to have' remains qualified."

coverage_by_id[P257].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L168-177",
    "note": "Printed p.257 (CHP-9.pdf physical p.19) reviewed against the scan. L177's final clause continues and closes in p.258 L180; printed notes 1-7 are processed at consolidated L380-386.",
})
coverage_by_id[P258].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L180-186",
    "note": "Printed p.258 (CHP-9.pdf physical p.20) reviewed against the scan. L180 closes p.257 L177; L186 ends at the first name 'Angelo' and continues at p.259 L188 with 'Querini', so retain partial. Notes 1-3 are consolidated at L387-388.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L349-388; p.255 L155 continuation",
    "note": "Consolidated notes through p.258 notes 1-3 are processed at L349-388; p.255 note 1 continuation at L155 remains cross-linked to L370. Later notes from L389 remain queued; citations are locators, not independent verification.",
})

summary = {"segments": {sid: [coverage_by_id[sid]["disposition"], coverage_by_id[sid]["migration_status"],
                               coverage_by_id[sid]["source_line_ranges"]] for sid in (P257, P258, NOTES)},
           "new_candidates": len(candidate_specs), "new_mentions": len(new_mentions),
           "new_statements": len(new_statements), "source_hash": meta["sha256"],
           "next_body_segment": f"{P259}#L188 closes p.258 L186"}
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
