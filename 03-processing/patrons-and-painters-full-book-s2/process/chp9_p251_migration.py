"""Controlled S2 migration for printed p.251; defaults to a read-only dry run."""
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
P251 = "chp-9:09_CHP-9_intro:l106-114"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
EXPECTED_HASH = "8d3a506cd567873e58c704496c286086bb86b701fcc0b32bc9e5fdd2b2547eae"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p251-20261001"


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
for sid in (P251, NOTES):
    if sid not in segment_by_id:
        raise SystemExit(f"missing source segment: {sid}")
meta = segment_by_id[P251]
if meta["sha256"] != EXPECTED_HASH or meta["asset_sha256"] != EXPECTED_ASSET_HASH:
    raise SystemExit("p.251 source segment or source asset fingerprint changed")
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


offsets_by_segment = {sid: line_offsets(sid) for sid in (P251, NOTES)}
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
    P251: ("queued", "pending", ""),
    NOTES: ("queued", "pending", ""),
}
for sid, expected in expected_states.items():
    row = coverage_by_id.get(sid)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != expected:
        raise SystemExit(f"unexpected coverage state for {sid}: {row}")

candidate_ids = {r["candidate_id"] for r in candidates}
if len(candidate_ids) != len(candidates) or max(int(x.split("-")[1]) for x in candidate_ids) != 8216:
    raise SystemExit("candidate inventory changed; inspect before allocating IDs")
candidate_specs = [
    (8217, "Passeriano", "place", P251, 107, "Named site of the Manin country house; keep distinct from the building."),
    (8218, "Bernini's porticos for St Peter's (architectural model cited for the Passeriano wings)", "work", P251, 107, "The source says the two colonnaded wings were adapted from Bernini's porticos; it does not identify a specific design or surviving feature."),
    (8219, "Old Testament tapestries in Palazzo Manin derived from Raphael", "work", P251, 108, "Tapestry series described in the anonymous correspondent's 1708 account; scenes and individual designs are unspecified."),
    (8220, "Mirror fashion introduced from France and ultimately traced to Persia", "term", P251, 108, "Haskell's account of the fashion and its reported origin; not an independently verified provenance."),
    (8221, "Unidentified bronzes by Giambologna in the Palazzo Manin gallery", "work", P251, 108, "The source names the artist but gives no subjects or individual object identities."),
    (8222, "Unidentified bronzes by Jacopo Sansovino in the Palazzo Manin gallery", "work", P251, 108, "The source names the artist but gives no subjects or individual object identities."),
    (8223, "Unidentified pictures by Giovanni da Udine in the Palazzo Manin gallery", "work", P251, 108, "The source gives no titles or individual picture identities."),
    (8224, "Unidentified pictures by Andrea del Sarto in the Palazzo Manin gallery", "work", P251, 108, "The source gives no titles or individual picture identities."),
    (8225, "Two unidentified pictures by Carlo Cignani in the Palazzo Manin", "work", P251, 110, "The source supplies the number and painter only."),
    (8226, "Marble Venus by Giuseppe Mazza in the Palazzo Manin", "work", P251, 110, "Sculpture described as marble; no further title, date or object identification is supplied."),
    (8227, "Rialto landmark adjoining Palazzo Manin (exact referent unresolved)", "place", P251, 108, "The 1708 account compares the palace with a 'marvel of the Rialto' said to adjoin it; retain the landmark's identity as unresolved."),
    (8228, "Daniele Florio", "person", NOTES, 350, "Named in the page note as the poet cited for the comparison with St Peter's; identity is recorded as given in the source."),
    (8229, "Le Grazie (Daniele Florio; Venice, 1766)", "archive", NOTES, 350, "Work cited at p. xli for a verse about the Manin villa; title spelling corrected against the page image, without independent bibliographic verification."),
    (8230, "Lettera on wedding festivities at Palazzo Manin (1708; author and addressee unnamed)", "archive", NOTES, 351, "A letter/account cited through La Galleria di Minerva, VI, p. 83; the original was not independently consulted."),
    (8231, "La Galleria di Minerva, volume VI (Venice, 1708)", "archive", NOTES, 351, "Publication identified by the p.251 note; article-level citation only."),
    (8232, "Unidentified correspondent describing Palazzo Manin in 1708", "person", P251, 108, "Unnamed correspondent quoted by Haskell; retain as an unidentified speaker rather than infer a name from the cited title."),
    (8233, "Unidentified Marchesa addressed by the 1708 Palazzo Manin letter", "person", NOTES, 351, "Recipient is identified only by the title's N.N. placeholder and title."),
    (8234, "Manin style of coloured marble or stucco cut to imitate hanging draperies", "term", P251, 112, "Haskell's local stylistic designation and description of a decorative finish."),
    (8235, "Udine Cathedral", "place", P251, 112, "Named building whose choir is cited as a location for the Manin-style finish."),
    (8236, "Persia", "place", P251, 108, "Geographical region named as the ultimate origin of the mirror fashion in Haskell's account."),
    (8237, "Friuli", "place", P251, 107, "Region of origin named for the Manin family; no more precise locality is specified."),
    (8238, "Haskell's open group of successful Venetian painters linked to seventeenth-century taste", "term", P251, 114, "The passage names Zanchi, Lazzarini, Balestra, Dorigny, Bambini and others; membership is expressly open."),
    (8239, "Pellegrini, Amigoni and Sebastiano Ricci as more adventurous painters", "term", P251, 114, "The three named painters in Haskell's comparison; retain the source's distinction from the preceding successful group."),
    (8240, "Seventeenth-century artistic taste in Venice", "term", P251, 114, "Periodizing category used by Haskell to characterize the group of most successful artists."),
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

existing_mention_ids = {r["mention_id"] for r in mentions}
existing_spans = {(r["segment_id"], r["start_char"], r["end_char"]) for r in mentions}
new_mentions = []


def mention(segment_id, line_no, suffix, cid, surface, note="", occurrence=0):
    mid = f"m-chp9-p251-{suffix}"
    if mid in existing_mention_ids or any(r["mention_id"] == mid for r in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mid}")
    line = source_lines[line_no - 1]
    start_at = 0
    pos = -1
    for _ in range(occurrence + 1):
        pos = line.find(surface, start_at)
        if pos < 0:
            raise SystemExit(f"surface not found at L{line_no}: {surface!r}")
        start_at = pos + len(surface)
    start = offsets_by_segment[segment_id][line_no] + pos
    end = start + len(surface)
    span = (segment_id, str(start), str(end))
    if span in existing_spans or any((r["segment_id"], r["start_char"], r["end_char"]) == span for r in new_mentions):
        raise SystemExit(f"duplicate mention span: {mid}")
    if cid not in candidate_ids:
        raise SystemExit(f"missing candidate for mention {mid}: {cid}")
    new_mentions.append({"mention_id": mid, "segment_id": segment_id, "candidate_id": cid,
                         "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


MENTION_SPECS = [
    (P251, 107, "manin-family", "cand-1519", "Manin", "Manin family candidate from the index."),
    (P251, 107, "friuli", "cand-8237", "Friuli", "Region of origin as stated by Haskell."),
    (P251, 107, "venice", "cand-2719", "Venice", "City and setting."),
    (P251, 107, "lodovico", "cand-1517", "Lodovico", "Lodovico Manin, the indexed person."),
    (P251, 107, "manin-country-house", "cand-1518", "country house", "Manin country house at Passeriano."),
    (P251, 107, "passeriano", "cand-8217", "Passeriano", "Place, distinct from the country house."),
    (P251, 107, "country-house-wings", "cand-1518", "two colonnaded wings", "Architectural parts of the Manin country house."),
    (P251, 108, "bernini-porticos", "cand-8218", "Bernini", "Porticos are the cited model."),
    (P251, 108, "st-peters", "cand-6960", "St Peter", "Basilica named as location of Bernini's porticos."),
    (P251, 108, "manin-palace", "cand-1520", "Their palace", "Palazzo Manin."),
    (P251, 108, "grand-canal", "cand-8178", "Grand Canal", "Waterway location."),
    (P251, 108, "anonymous-correspondent", "cand-8232", "correspondent", "Unnamed source quoted as writing in 1708."),
    (P251, 108, "rialto", "cand-8227", "Rialto", "Exact adjoining landmark remains unresolved."),
    (P251, 108, "manin-tapestries", "cand-8219", "tapestries", "Unspecified series derived from Raphael."),
    (P251, 108, "raphael", "cand-2098", "Raphael", "Named as the source of the tapestry designs."),
    (P251, 108, "old-testament", "cand-7677", "Old Testament", "Subject range of the tapestry scenes."),
    (P251, 108, "mirror-fashion", "cand-8220", "mirrors", "Decorative fashion described by Haskell."),
    (P251, 108, "france", "cand-5317", "France", "Place named as the immediate source of the fashion."),
    (P251, 108, "persia", "cand-8236", "Persia", "Place named as the ultimate origin of the fashion."),
    (P251, 108, "giambologna-bronzes", "cand-8221", "Giambologna", "Artist of unidentified bronzes in the gallery."),
    (P251, 108, "sansovino-bronzes", "cand-2354", "Sansovino", "Jacopo Sansovino; works mentioned as bronzes."),
    (P251, 108, "giovanni-udine-pictures", "cand-2667", "Giovanni da Udine", "Artist named for pictures in the gallery."),
    (P251, 109, "andrea-del-sarto-pictures", "cand-2361", "Andrea del Sarto", "Artist named for pictures in the gallery."),
    (P251, 109, "manin-gallery-owners", "cand-1519", "the Manin", "Manin family as owners/patrons."),
    (P251, 110, "cignani", "cand-0748", "Cignani", "Carlo Cignani; indexed person."),
    (P251, 110, "cignani-pictures", "cand-8225", "two pictures", "Unidentified pair by Cignani."),
    (P251, 110, "italy", "cand-3461", "Italy", "Geographical scope of Haskell's superlative."),
    (P251, 110, "marble-venus-marble", "cand-8226", "marble", "Material description of the sculpture; the title continues on L111."),
    (P251, 111, "marble-venus-venus", "cand-8226", "Venus", "Subject/title element continuing from L110."),
    (P251, 111, "mazza", "cand-1602", "Giuseppe Mazza", "Indexed sculptor."),
    (P251, 111, "bologna", "cand-3398", "Bologna", "City in Mazza's quoted sobriquet."),
    (P251, 111, "rossi", "cand-2270", "Domenico Rossi", "Architect named as part of the Manin team."),
    (P251, 111, "dorigny", "cand-0944", "Luigi Dorigny", "Index candidate for Louis Dorigny reused."),
    (P251, 111, "local-poet", "cand-8228", "local poet", "Footnote 4 identifies the cited poet as Daniele Florio."),
    (P251, 111, "manin-country-house-poem", "cand-1518", "their country house", "Manin country house described by the poet."),
    (P251, 111, "manin-style", "cand-8234", "Manin style", "Haskell's characterization of the decorative finish."),
    (P251, 111, "udine-city", "cand-2666", "Udine", "City; the building is separately represented below."),
    (P251, 112, "udine-cathedral", "cand-8235", "Cathedral", "Continuation of 'Udine Cathedral' across the source line break."),
    (P251, 112, "jesuit-church", "cand-0734", "Jesuit church", "Indexed S. Maria Assunta (Jesuit church); Venice."),
    (P251, 112, "manin-palace-style-location", "cand-1520", "their palace", "Palazzo Manin."),
    (P251, 112, "manin-country-house-style-location", "cand-1518", "country house", "Manin country house."),
    (P251, 113, "old-and-new-families", "cand-8176", "old and new families", "Collective family groups; membership is not expanded."),
    (P251, 113, "same-contemporary", "cand-8232", "the same contemporary", "The anonymous correspondent referenced at L108."),
    (P251, 114, "zanchi", "cand-2834", "Zanchi", "Antonio Zanchi, index candidate."),
    (P251, 114, "successful-artists-group", "cand-8238", "The artists with the greatest success", "Haskell's open group; the list ends 'and others'."),
    (P251, 114, "seventeenth-century-taste", "cand-8240", "seventeenth-century taste", "Stylistic/period category used by Haskell."),
    (P251, 114, "lazzarini", "cand-1368", "Lazzarini", "Gregorio Lazzarini, index candidate."),
    (P251, 114, "balestra", "cand-0168", "Balestra", "Antonio Balestra, index candidate."),
    (P251, 114, "dorigny-artists-list", "cand-0944", "Dorigny", "Louis Dorigny, repeated reference."),
    (P251, 114, "bambini", "cand-0171", "Bambini", "Niccolo Bambini, index candidate."),
    (P251, 114, "pellegrini", "cand-1862", "Pellegrini", "Giovanni Antonio Pellegrini, index candidate."),
    (P251, 114, "amigoni", "cand-0094", "Amigoni", "Jacopo Amigoni, index candidate."),
    (P251, 114, "ricci", "cand-2154", "Sebastiano Ricci", "Index candidate reused; final sentence remains incomplete at the page break."),
    (P251, 114, "adventurous-painters-group", "cand-8239", "more adventurous painters", "The three artists named immediately after this group reference."),
    (P251, 114, "venice-artists", "cand-2719", "Venice", "City from which the painters were said to be better known outside."),
    (NOTES, 350, "villa-restoration", "cand-1518", "the villa", "Footnote refers to the Manin country house."),
    (NOTES, 350, "st-peters-influence", "cand-6960", "St Peter", "Influence reported by the footnote, not independently established."),
    (NOTES, 350, "florio-author", "cand-8228", "Daniele Florio", "Named author of the cited verse."),
    (NOTES, 350, "florio-book", "cand-8229", "Le Crazie", "OCR reading; page image confirms the printed title Le Grazie."),
    (NOTES, 350, "venezia", "cand-2719", "Venezia", "Publication place in the citation."),
    (NOTES, 351, "wedding-letter", "cand-8230", "Lettera del Co: di N.N. A Madama la Marchesa di N.N. a Parigi, in cui si da conto delle solenni Pompe Nuziali vedute nel Palazzo di S.E. il Signor Co: Manin in Venezia", "Title transcribed as printed; author and addressee remain unnamed."),
    (NOTES, 351, "letter-author", "cand-8232", "N.N.", "Unidentified Count/correspondent in the cited title.", 0),
    (NOTES, 351, "letter-recipient", "cand-8233", "N.N.", "Unidentified Marchesa in the cited title.", 1),
    (NOTES, 351, "manin-palace-citation", "cand-1520", "Manin", "Palazzo Manin named in the title."),
    (NOTES, 351, "galleria-periodical", "cand-8231", "La Galleria di Minerva", "Publication carrying the cited letter/account."),
    (NOTES, 352, "florio-author-note4", "cand-8228", "Daniele Florio", "The page reference corroborates note 2's named poet."),
]
for spec in MENTION_SPECS:
    mention(*spec)


def quote(segment_id, first, last):
    return "\n".join(source_lines[first - 1:last])


new_statements = []
existing_statement_ids = {r["statement_id"] for r in statements}


def statement(suffix, segment_id, first, last, subject, obj, predicate, claim, qualification,
              mentioned, marker=None, note_line=None, speaker="Haskell", text_layer="body", extras=None):
    sid = f"st-chp9-p251-{suffix}"
    if sid in existing_statement_ids or any(r["statement_id"] == sid for r in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    m = segment_by_id[segment_id]
    if first < m["line_start"] or last > m["line_end"]:
        raise SystemExit(f"statement lines outside segment {segment_id}: {sid}")
    if any(cid and cid not in candidate_ids for cid in [subject, obj, *mentioned]):
        raise SystemExit(f"missing candidate in statement: {sid}")
    q = {"source_line_start": first, "source_line_end": last, "printed_page": 251,
         "pdf_physical_page": 13, "claim": claim, "speaker": speaker, "text_layer": text_layer,
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


statement("manin-venice-patronage", P251, 107, 107, "cand-1519", "cand-2719",
          "decorated_estates_and_churches_around_venice",
          "The Manin family was active in decorating palaces, country houses and churches in and around Venice; Haskell says its spending brought a reputation for nobility of soul.",
          "Retain Haskell's evaluation and broad geographic scope; the named sites are not an exhaustive list.",
          ["cand-1519", "cand-2719", "cand-1518", "cand-1520"], marker=1, note_line=349, extras={"relation_candidate": True})
statement("lodovico-last-doge", P251, 107, 107, "cand-1519", "cand-1517",
          "expenditure_linked_to_election_of_last_doge",
          "Haskell links the Manin family's expenditure to the eventual election of Lodovico as the last Doge.",
          "Preserve the author's stated causal framing and his description of Lodovico as futile; no external validation is implied.",
          ["cand-1519", "cand-1517"], extras={"relation_candidate": True})
statement("passeriano-wings", P251, 107, 108, "cand-1518", "cand-8218",
          "country_house_approach_adapted_from_bernini_porticos",
          "The Manin country house at Passeriano was approached through two colonnaded wings adapted from Bernini's porticos for St Peter's.",
          "The note says the villa was later restored; retain 'adapted from' as the source's comparison, not an identity claim.",
          ["cand-1518", "cand-8217", "cand-8218", "cand-6960"], marker=2, note_line=350, extras={"relation_candidate": True})
statement("1708-palace-description", P251, 108, 108, "cand-8232", "cand-1520",
          "described_manin_palace_as_comparable_to_rialto_marvel",
          "An unidentified correspondent writing in 1708 described the Palazzo Manin on the Grand Canal as majestic and comparable in grandeur to a famous adjoining marvel of the Rialto; its decorative value and splendour surpassed expectations.",
          "The precise Rialto referent is unresolved; this is a reported contemporary description, not an objective measure.",
          ["cand-8232", "cand-1520", "cand-8178", "cand-8227"], marker=3, note_line=351, extras={"relation_candidate": True})
statement("palace-hangings-tapestries", P251, 108, 108, "cand-8232", "cand-8219",
          "reported_rich_hangings_and_raphael_derived_tapestries",
          "The correspondent's account says the palace walls had rich hangings and tapestries derived from Raphael showing Old Testament scenes.",
          "No individual tapestry, Raphael design or scene is identified.",
          ["cand-8232", "cand-1520", "cand-8219", "cand-2098", "cand-7677"], marker=3, note_line=351)
statement("mirror-fashion-origin", P251, 108, 108, "cand-8232", "cand-8220",
          "mirror_fashion_introduced_from_france_and_traced_to_persia",
          "The account describes glistening mirrors as a new fashion recently introduced from France and ultimately springing from Persia.",
          "This is the book's stated cultural-origin claim; it is not independently verified.",
          ["cand-8232", "cand-8220", "cand-5317", "cand-8236"], marker=3, note_line=351)
statement("gallery-works", P251, 108, 109, "cand-8232", "cand-1520",
          "reported_gallery_bronzes_and_pictures",
          "The correspondent's account lists bronzes by Giambologna and Sansovino and pictures by Giovanni da Udine and Andrea del Sarto in the palace gallery.",
          "The individual works and their present locations are not given.",
          ["cand-8232", "cand-1520", "cand-8221", "cand-1160", "cand-8222", "cand-2354", "cand-8223", "cand-2667", "cand-8224", "cand-2361"], marker=3, note_line=351, extras={"relation_candidate": True})
statement("cignani-and-mazza", P251, 110, 111, "cand-1520", "cand-8225",
          "held_two_cignani_pictures_and_mazza_marble_venus",
          "The Manin palace held two pictures by Carlo Cignani, whom Haskell calls Italy's most expensive artist, and a marble Venus by Giuseppe Mazza, nicknamed the Phidias of Bologna.",
          "No Cignani picture titles or further Venus object details are supplied; retain both epithets as Haskell's wording.",
          ["cand-1520", "cand-8225", "cand-0748", "cand-3461", "cand-8226", "cand-1602", "cand-3398"], extras={"relation_candidate": True})
statement("consistent-taste-and-team", P251, 111, 111, "cand-1519", "cand-2270",
          "used_consistent_taste_and_repeated_architect_artist_team",
          "Haskell characterizes Manin taste as more consistent and extravagant than that of other families and says the family used architect Domenico Rossi and painter Luigi Dorigny on many enterprises.",
          "The comparative evaluation is Haskell's; 'many' remains unquantified.",
          ["cand-1519", "cand-2270", "cand-0944"], extras={"relation_candidate": True})
statement("florio-country-house-verse", P251, 111, 111, "cand-8228", "cand-1518",
          "poetic_description_of_manin_country_house_in_le_grazie",
          "A local poet, identified by note 4 as Daniele Florio, describes the Manin country-house rooms as adorned with smooth, shiny marble of fine colours rather than gold friezes.",
          "The identification follows the book's note; the cited page of Le Grazie was not independently consulted.",
          ["cand-8228", "cand-8229", "cand-1518"], marker=4, note_line=352, extras={"relation_candidate": True})
statement("manin-style-sites", P251, 111, 112, "cand-8234", "cand-1520",
          "coloured_marble_or_stucco_drapery_finish_at_named_sites",
          "Haskell calls coloured marble or stucco cut to imitate hanging draperies a hallmark of the Manin style, found in the choir of Udine Cathedral, especially the Venetian Jesuit church, and in the palace and country house.",
          "The church is represented by the indexed S. Maria Assunta (Jesuit church); the source's 'above all' emphasis is retained.",
          ["cand-8234", "cand-8235", "cand-2666", "cand-0734", "cand-1520", "cand-1518"], extras={"relation_candidate": True})
statement("old-new-shared-display", P251, 113, 113, "cand-8176", "cand-2719",
          "old_and_new_families_shared_splendour_and_display",
          "Haskell says old and new families shared splendour and display; the same contemporary correspondent states that richness is the body of nobility and ancient lineage and virtue its soul.",
          "Keep the quoted social maxim attributed to the unnamed correspondent, not as a general fact.",
          ["cand-8176", "cand-2719", "cand-8232"], note_line=351, extras={"relation_candidate": True})
statement("artists-seventeenth-century-taste", P251, 114, 114, "cand-8238", "cand-8240",
          "successful_artists_remained_linked_to_seventeenth_century_taste",
          "Haskell says the artists he regarded as most successful were chiefly those closest to seventeenth-century taste, and their prestige lasted after more adventurous painters moved in new directions.",
          "This is Haskell's periodizing evaluation; 'and others' leaves the artist list open.",
          ["cand-8238", "cand-2834", "cand-1368", "cand-0168", "cand-0944", "cand-0171", "cand-8240"],
          extras={"relation_candidate": True})
statement("avant-painters-outside-venice", P251, 114, 114, "cand-8239", "cand-2719",
          "three_adventurous_painters_scarcely_employed_in_venetian_palaces",
          "Haskell says Pellegrini, Amigoni and Sebastiano Ricci were scarcely employed in great Venetian palace decoration and became better known outside Venice.",
          "The sentence is complete; the following sentence about Ricci continues onto p.252 and is not asserted here.",
          ["cand-8239", "cand-1862", "cand-0094", "cand-2154", "cand-2719"],
          extras={"relation_candidate": True})
statement("p251-note1-page-reference", NOTES, 349, 349, None, None,
          "printed_page_note_cross_reference",
          "Printed p.251 note 1 directs readers to p.268 note 5.",
          "Resolve this internal pointer to the corresponding source segment when p.268 is semantically processed.",
          [], speaker="Haskell's footnote", text_layer="footnote",
          extras={"printed_target_page": 268, "printed_target_note": 5, "resolution_status": "pending_link_to_source_segment"})
statement("villa-restoration-note", NOTES, 350, 350, "cand-1518", None,
          "villa_restored_after_long_period_of_decay",
          "The footnote says the Manin villa had been restored after a long period of decay.",
          "The restoration statement is the footnote's report; no independent source is cited or checked.",
          ["cand-1518"], marker=2, speaker="Haskell's footnote", text_layer="footnote")
statement("st-peters-poetic-influence-note", NOTES, 350, 350, "cand-6960", "cand-1518",
          "st_peters_influence_noted_by_eighteenth_century_poets",
          "The footnote says eighteenth-century poets noted the influence of St Peter's on the Manin villa and cites Daniele Florio's Le Grazie, Venice, 1766, p. xli.",
          "Retain the note's attribution and citation; the original poem was not independently checked.",
          ["cand-6960", "cand-1518", "cand-8228", "cand-8229"], marker=2,
          speaker="Haskell's footnote", text_layer="footnote")
statement("anonymous-1708-source-citation", NOTES, 351, 351, "cand-8230", "cand-8231",
          "letter_account_published_in_galleria_di_minerva",
          "The note identifies an anonymous letter/account about wedding festivities at Palazzo Manin and locates it in La Galleria di Minerva, volume VI, Venice, 1708, p. 83.",
          "Citation locator only; neither the letter nor its publication was independently consulted.",
          ["cand-8230", "cand-8231", "cand-8232", "cand-8233", "cand-1520"], marker=3,
          speaker="Haskell's footnote", text_layer="footnote", extras={"relation_candidate": True})
statement("florio-citation-note4", NOTES, 352, 352, "cand-8228", "cand-8229",
          "florio_cited_for_p251_poem_at_page_xli",
          "Note 4 identifies Daniele Florio, p. xli, as the source for the preceding country-house verse.",
          "The cited page is not independently consulted; note 2 gives the title and publication details.",
          ["cand-8228", "cand-8229"], marker=4, speaker="Haskell's footnote", text_layer="footnote")

if len({r["mention_id"] for r in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("mention IDs are not unique")
if len({r["statement_id"] for r in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("statement IDs are not unique")
coverage_by_id[P251].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L106-114",
    "note": "Printed p.251 (CHP-9.pdf physical p.13) reviewed against the page image. L114 ends mid-sentence ('despite the admiration') and continues at p.252 L117; retain reviewed/partial. Body notes 1-4 link to consolidated notes L349-352. OCR title 'Le Crazie' in L350 is corrected to printed 'Le Grazie' in S2 only; S0 unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L349-352",
    "note": "The p.251 footnotes at consolidated lines L349-352 were semantically processed with the p.251 body. The remaining consolidated notes still require source-order review; page-level links do not imply full coverage of this merged segment.",
})

summary = {"segment": P251, "notes_referenced": "L349-352", "new_candidates": len(candidate_specs),
           "new_mentions": len(new_mentions), "new_statements": len(new_statements),
           "coverage": [coverage_by_id[P251]["disposition"], coverage_by_id[P251]["migration_status"]]}
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
