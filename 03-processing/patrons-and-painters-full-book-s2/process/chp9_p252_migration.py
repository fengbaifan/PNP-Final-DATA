"""Controlled S2 migration for printed p.252; defaults to a read-only dry run."""
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
P252 = "chp-9:09_CHP-9_intro:l116-122"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
EXPECTED_HASH = "9d02deba0f0e66b5f17cf6a1d7cb45435a085ac2be3d503df55a76d8ea5844a3"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p252-20261001"


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
for sid in (P251, P252, NOTES):
    if sid not in segment_by_id:
        raise SystemExit(f"missing source segment: {sid}")
meta = segment_by_id[P252]
if meta["sha256"] != EXPECTED_HASH or meta["asset_sha256"] != EXPECTED_ASSET_HASH:
    raise SystemExit("p.252 source segment or source asset fingerprint changed")
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


offsets_by_segment = {sid: line_offsets(sid) for sid in (P251, P252, NOTES)}


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
    P251: ("reviewed", "partial", "L106-114"),
    P252: ("queued", "pending", ""),
    NOTES: ("reviewed", "partial", "L349-352"),
}
for sid, expected in expected_states.items():
    row = coverage_by_id.get(sid)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != expected:
        raise SystemExit(f"unexpected coverage state for {sid}: {row}")

candidate_ids = {r["candidate_id"] for r in candidates}
if len(candidate_ids) != len(candidates) or max(int(x.split("-")[1]) for x in candidate_ids) != 8240:
    raise SystemExit("candidate inventory changed; inspect before allocating IDs")
candidate_specs = [
    (8241, "Ten Roman-history canvases painted by Giambattista Tiepolo for the Dolfin family", "work", P252, 119,
     "The source identifies a group of ten large scenes selected from Florus and painted for the Dolfin; it does not enumerate each canvas here."),
    (8242, "Venetian wars with the Turks in the 1680s and 1715 as invoked by Haskell", "event", P252, 118,
     "Retain Haskell's broad references and dates; do not identify individual campaigns from this wording alone."),
    (8243, "Roman ancestry claimed by Venetian families in Tiepolo's patronage context", "term", P252, 118,
     "Collective claim attributed by Haskell to many Venetian families; only the Corner family is named in this passage."),
    (8244, "Violent, tense dramatic style attributed to Tiepolo in the 1720s", "term", P252, 118,
     "Haskell's stylistic description, not a verified or externally harmonized style label."),
    (8245, "Lucius Annaeus Florus", "person", P252, 119,
     "Named by Haskell as the Roman-history chronicler from whom the Dolfin cycle's subjects were selected."),
    (8246, "Will of Daniele III Dolfin, described by Haskell", "archive", P252, 119,
     "The will is quoted and summarized in the book; the document itself and its date are not supplied or independently consulted."),
    (8247, "Venetian Treasury mentioned in Daniele III's will", "institution", P252, 119,
     "Institutional office named in the quotation; its formal historical identity is not resolved in S2."),
    (8248, "Patriarchate of Aquileia", "institution", P252, 120,
     "Religious office/body named in the passage; keep distinct from the city of Aquileia."),
    (8249, "Dionisio Dolfin's library at Udine", "place", P252, 122,
     "Library built in 1708 according to Haskell; exact architectural identity and surviving fabric are not established here."),
    (8250, "Frescoes by Niccolo Bambini decorating Dionisio Dolfin's library at Udine", "work", P252, 122,
     "The source names Bambini and the library setting but gives no fresco title or individual scenes."),
    (8251, "Unidentified ceiling fresco in the room where Tiepolo's canvases once hung", "work", NOTES, 355,
     "Haskell says its artist and date remain mysterious and tentatively places it some years after Tiepolo's canvases."),
    (8252, "Unidentified family palace at Venice where Tiepolo had just finished work", "place", P252, 122,
     "The family and palace are not specifically named in this sentence; retain as an unresolved building reference."),
    (8253, "Palazzo Vendramin-Calergi", "place", NOTES, 357,
     "Named location of a separate cycle of Roman-history canvases in note 5."),
    (8254, "Unidentified Roman-history canvas cycle at Palazzo Vendramin-Calergi", "work", NOTES, 357,
     "The source reports that the cycle has been attributed to Niccolo Bambini; the attribution is not asserted as settled."),
    (8257, "A. Morassi", "person", NOTES, 355,
     "Author named in the p.252 note; the initial is retained as printed in the bibliography."),
    (8258, "G. B. Tiepolo (London, 1955)", "archive", NOTES, 355,
     "Bibliography identifies the publication cited as Morassi 1955, fig.11; the cited page/image was not consulted independently."),
    (8259, "Loeb edition of Lucius Annaeus Florus, page 33", "archive", NOTES, 355,
     "The note gives a Loeb-edition locator but does not identify the edition's editor or publication details."),
    (8260, "Bortolo Giovanni Dolfin", "person", NOTES, 356,
     "Author of I Dolfin as identified in the book bibliography."),
    (8261, "I Dolfin, patrizii veneziani nella storia di Venezia, second edition (Milan, 1924)", "archive", NOTES, 356,
     "Bibliography identifies the abbreviated Dolfin citation; the cited pages were not consulted independently."),
    (8262, "Biblioteca Correr", "institution", NOTES, 356,
     "Repository named in the note; the manuscript locator is retained separately as an archive candidate."),
    (8263, "Discendenze patrizie manuscript, Biblioteca Correr XI, E 2/6", "archive", NOTES, 356,
     "Specific manuscript locator as printed in the note; the manuscript itself was not consulted."),
    (8264, "N. Ivanov", "person", NOTES, 357,
     "Author's initial and surname as given in the bibliography."),
    (8265, "Una postilla tiepolesca (Ivanov, Ateneo Veneto, 1951, pp.1-3)", "archive", NOTES, 357,
     "Publication identified by the bibliography; this records Haskell's citation, not independent reading or verification."),
    (8266, "Conte Girolamo de Renaldis", "person", NOTES, 358,
     "Author identified from the bibliography entry for Memorie storiche; name and title follow that source."),
    (8267, "Memorie storiche dei tre ultimi secoli del patriarcato d'Aquileia (1411-1751), Udine, 1888", "archive", NOTES, 358,
     "Publication identified from the bibliography; the cited contents were not consulted independently."),
    (8268, "Niccolò Madrisio", "person", NOTES, 359,
     "Author identified from the bibliography entry for the 1711 oration."),
    (8269, "Madrisio's 1711 oration thanking Dionigi Delfino for the public library at Udine", "archive", NOTES, 359,
     "Publication title and date are identified from the book bibliography; the text was not consulted independently."),
    (8270, "Guglielmo Biasutti", "person", NOTES, 359,
     "Author identified from the bibliography entry cited as Biasutti, 1958."),
    (8271, "Storia e Guida del Palazzo Arcivescovile di Udine (Biasutti, 1958)", "archive", NOTES, 359,
     "Publication identified from the book bibliography; the cited contents were not consulted independently."),
    (8272, "Surviving early sketches and drawings by Tiepolo referenced in note 1", "work", NOTES, 353,
     "The note describes evidence generically without identifying or locating individual drawings."),
    (8273, "Court of Turin as an employer of Sebastiano Ricci", "institution", P252, 117,
     "The source names the court by its city but does not specify a ruler, office, or formal institution name."),
    (8274, "Church patronage as an employment context for Sebastiano Ricci", "term", P252, 117,
     "The plural churches are unnamed; this records a patronage context, not a single institution."),
    (8275, "Classical and allegorical subject group in the unidentified Dolfin-library ceiling fresco", "term", NOTES, 355,
     "The note lists a dolphin, ancient deities, Abundance, Arts and Sciences, Time, Fame and other symbolic figures; identities are not expanded."),
    (8276, "Venetian families claiming Roman ancestry in the Tiepolo passage", "term", P252, 118,
     "Unnamed collective group; the passage singles out the Corner family but does not list other members."),
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
    mid = f"m-chp9-p252-{suffix}"
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
    (P252, 117, "ricci-coreference", "cand-2154", "he", "Coreference to Sebastiano Ricci named in p.251 L114."),
    (P252, 117, "ricci-city", "cand-2719", "the city", "Venice, where Ricci had settled."),
    (P252, 117, "venetian-aristocracy", "cand-8108", "Venetian aristocracy", "Social estate; Haskell describes Ricci's relative employment there."),
    (P252, 117, "turin-court", "cand-8273", "court of Turin", "Unspecified court named as an employer of Ricci."),
    (P252, 117, "turin", "cand-2662", "Turin", "City named in the court reference."),
    (P252, 117, "church-employers", "cand-8274", "churches", "Unspecified plural church patrons."),
    (P252, 117, "smith", "cand-2440", "Joseph Smith", "Index candidate for the English businessman."),
    (P252, 118, "tiepolo", "cand-2569", "Tiepolo", "Giambattista Tiepolo."),
    (P252, 118, "career-1720s", "cand-2569", "immediately successful career", "Haskell's account of Tiepolo's early career."),
    (P252, 118, "violent-tense-style", "cand-8244", "violent, tense style", "Stylistic characterization attributed to Haskell."),
    (P252, 118, "battle-scenes", "cand-2587", "battle scenes", "Part of the indexed early subject range for Tiepolo."),
    (P252, 118, "triumphs", "cand-2587", "triumphs", "Part of the indexed early subject range for Tiepolo."),
    (P252, 118, "roman-history", "cand-8241", "Roman history", "Historical subject range of the Tiepolo canvases."),
    (P252, 118, "venetian-families", "cand-8276", "many Venetian families", "Unnamed collective group in Haskell's account."),
    (P252, 118, "roman-ancestry", "cand-8243", "Roman ancestry", "Claim attributed by Haskell to Venetian families."),
    (P252, 118, "corner-family", "cand-0848", "the Corner", "Indexed family subentry for Tiepolo patronage."),
    (P252, 118, "tiepolo-work-corner", "cand-2616", "worked before 1722", "The source says Tiepolo is known to have worked for the Corner before 1722."),
    (P252, 118, "dramatic-style", "cand-8244", "dramatic style", "Haskell's characterization, later in the same sentence."),
    (P252, 118, "venice-wars", "cand-8242", "great wars with the Turks", "Haskell's broad reference to Venetian wars."),
    (P252, 118, "venice", "cand-2719", "Venice", "City in the war reference."),
    (P252, 118, "turks", "cand-7153", "the Turks", "Collective political-military label; no particular force is identified."),
    (P252, 118, "1680s", "cand-8242", "1680s", "Source-given date range for one reference to the wars."),
    (P252, 118, "1715", "cand-8242", "1715", "Source-given date for the later war reference."),
    (P252, 119, "city", "cand-2719", "the city", "Venice, continued from the preceding line."),
    (P252, 119, "aristocracy", "cand-8108", "her aristocracy", "Venetian aristocracy; the pronoun refers to the city of Venice."),
    (P252, 119, "ten-dolfin-scenes", "cand-8241", "ten large and forceful scenes from Roman history", "The specific Dolfin cycle described by Haskell."),
    (P252, 119, "florus", "cand-8245", "L. Annaeus Florus", "Roman chronicler named as the source of the subjects."),
    (P252, 119, "tiepolo-dolfin", "cand-2617", "Tiepolo", "Giambattista Tiepolo; work for Dolfin index candidate."),
    (P252, 119, "dolfin", "cand-0931", "the Dolfin", "Dolfin family in the patronage context."),
    (P252, 119, "greatest-patrons", "cand-0931", "his greatest patrons of the 1720s", "Haskell's characterization of the Dolfin family."),
    (P252, 119, "tremendous-family", "cand-0931", "They were a tremendous family", "Anaphoric reference to the Dolfin family."),
    (P252, 119, "daniele-iii", "cand-0927", "Daniele III", "Indexed Dolfin family member."),
    (P252, 119, "state-service", "cand-8105", "the State", "Venetian governing entity in Haskell's account; distinguish from the city."),
    (P252, 119, "orator", "cand-0927", "one of the finest orators", "Haskell's assessment of Daniele III."),
    (P252, 119, "will", "cand-8246", "his will", "Daniele III's will, which Haskell quotes and summarizes."),
    (P252, 119, "treasury", "cand-8247", "the Treasury", "Office named in the will quotation."),
    (P252, 119, "economy-state", "cand-8105", "the economy of the State", "Political entity named in the quoted aspiration."),
    (P252, 119, "republic", "cand-8105", "the Republic", "The state as the conditional recipient of the estate; identity should still be handled at S3."),
    (P252, 119, "daniele-iv", "cand-0928", "Daniele IV", "Indexed Dolfin family member."),
    (P252, 119, "morosini", "cand-1705", "Morosini", "Francesco Morosini, named as the commander under whom Daniele IV served."),
    (P252, 119, "peloponnese", "cand-8117", "Peloponnese", "Named military theatre."),
    (P252, 119, "daniele-iv-1715", "cand-0928", "again in 1715", "The source's second date for Daniele IV's command in the Turkish wars."),
    (P252, 120, "dolfin-patriarchate", "cand-0931", "The Dolfin", "Collective family reference in the sentence about the patriarchate."),
    (P252, 120, "patriarchate", "cand-8248", "the patriarchate of Aquileia", "Office/body named in the text."),
    (P252, 120, "aquileia", "cand-8248", "Aquileia", "Part of the named patriarchate; not a separate city assertion here."),
    (P252, 120, "1698", "cand-0929", "1698", "Date introducing Dionisio's appointment and move to Udine."),
    (P252, 121, "dionisio", "cand-0929", "Dionisio", "Dolfin, younger brother of Daniele III and Daniele IV."),
    (P252, 121, "the-post", "cand-8248", "the post", "Contextually follows the Patriarchate of Aquileia; preserve the text's anaphora."),
    (P252, 122, "udine", "cand-2666", "Udine", "City where Dionisio went to live."),
    (P252, 122, "bishopric", "cand-8248", "the bishopric", "The text calls Udine the seat of a bishopric; its precise institutional identification is not further stated here."),
    (P252, 122, "austria-opposition", "cand-7284", "Austria", "Political-military actor in the opposition described by Haskell."),
    (P252, 122, "udine-city", "cand-2666", "the city", "Udine, the immediate antecedent in L121."),
    (P252, 122, "residence", "cand-0929", "thirty-six-year.residence", "OCR surface; the printed page reads 'thirty-six-year residence'."),
    (P252, 122, "1708", "cand-8249", "In 1708", "Date of the library construction as stated by Haskell."),
    (P252, 122, "library", "cand-8249", "library", "Dionisio's library at Udine."),
    (P252, 122, "bambini-frescoes", "cand-8250", "frescoes", "Unspecified frescoes decorating the library."),
    (P252, 122, "bambini", "cand-0171", "Niccolo Bambini", "Indexed painter named in the source."),
    (P252, 122, "eighteen-years-later", "cand-0929", "some eighteen years later", "Relative chronology as stated; no absolute year calculated."),
    (P252, 122, "summoned-tiepolo", "cand-2569", "summoned Tiepolo", "Tiepolo was summoned; the purpose continues on p.253."),
    (P252, 122, "family-palace", "cand-8252", "the family palace", "Exact palace and family are unresolved in this sentence."),
    (P252, 122, "venice-palace-location", "cand-2719", "Venice", "City of the unidentified family palace."),
    (NOTES, 353, "early-sketches", "cand-8272", "surviving sketches", "Generic surviving evidence; individual drawings are not identified."),
    (NOTES, 353, "early-drawings", "cand-8272", "drawings", "Generic surviving evidence; individual drawings are not identified."),
    (NOTES, 354, "da-canal", "cand-7781", "Da Canal", "Identified from the bibliography as Vincenzo da Canal."),
    (NOTES, 354, "da-canal-page32", "cand-6593", "p. 32", "Citation locator in Da Canal."),
    (NOTES, 355, "ibid", "cand-6593", "ibid.", "Refers to the immediately preceding Da Canal citation."),
    (NOTES, 355, "da-canal-page33", "cand-6593", "p. 33", "Citation locator in Da Canal."),
    (NOTES, 355, "tiepolo-pictures", "cand-8241", "The pictures", "Anaphoric reference to the Tiepolo Roman-history canvases."),
    (NOTES, 355, "leningrad", "cand-5796", "Leningrad", "Historical city name used in the 1980 text."),
    (NOTES, 355, "vienna", "cand-2772", "Vienna", "City location of part of the canvases."),
    (NOTES, 355, "vienna-canvas", "cand-2582", "one of the Vienna canvases", "The specific Tiepolo canvas discussed in the remainder of the note."),
    (NOTES, 355, "morassi", "cand-8257", "Morassi", "A. Morassi as named in the bibliography."),
    (NOTES, 355, "morassi-1955", "cand-8258", "1955", "Publication year in the Morassi citation."),
    (NOTES, 355, "morassi-fig11", "cand-8258", "fig. 11", "Figure locator in Morassi's cited publication."),
    (NOTES, 355, "misidentified-title", "cand-2582", "Eteocles and Polynices", "A title Haskell says had been applied to this canvas, then explicitly rejects."),
    (NOTES, 355, "corrected-subject", "cand-2582", "Brutus killing Arruns", "The subject Haskell identifies for the Vienna canvas."),
    (NOTES, 355, "florus-note3", "cand-8245", "L. Annaeus Florus", "Named source of the Brutus and Arruns subject."),
    (NOTES, 355, "loeb-edition", "cand-8259", "Loeb edition", "Edition named as the locator for Florus."),
    (NOTES, 355, "loeb-page33", "cand-8259", "p. 33", "Page locator in the Loeb edition.", 1),
    (NOTES, 355, "room", "cand-8249", "the room", "The room associated with the library/Tiepolo canvases; architectural identification remains contextual."),
    (NOTES, 355, "ceiling-fresco", "cand-8251", "a large ceiling fresco", "Fresco distinguished from Bambini's earlier library decoration."),
    (NOTES, 355, "dolphin-motif", "cand-8275", "a dolphin", "Depicted motif in the unidentified ceiling fresco."),
    (NOTES, 355, "ancient-gods", "cand-8275", "gods and goddesses of antiquity", "Depicted subject group; individuals are not identified."),
    (NOTES, 355, "abundance", "cand-8275", "Abundance", "One of the symbolic figures/meanings described in the fresco."),
    (NOTES, 355, "arts-and-sciences", "cand-8275", "Ans and Sciences", "S0 OCR surface; page image confirms the printed reading 'Arts and Sciences'."),
    (NOTES, 355, "time", "cand-8275", "Time", "One of the symbolic figures named in the fresco."),
    (NOTES, 355, "fame", "cand-8275", "Fame", "One of the symbolic figures named in the fresco."),
    (NOTES, 355, "bolognese-framework", "cand-8188", "Bolognese type", "Existing candidate for the architectural-framework type."),
    (NOTES, 355, "tiepolo-canvases-note3", "cand-8241", "Tiepolo", "The fresco is tentatively dated after the canvases by Haskell.", 1),
    (NOTES, 356, "dolfin-book-author", "cand-8260", "Dolfin", "Bortolo Giovanni Dolfin identified through the bibliography entry."),
    (NOTES, 356, "dolfin-page171", "cand-8261", "pp. 171 ff.", "Locator in I Dolfin."),
    (NOTES, 356, "correr-library", "cand-8262", "Biblioteca Correr", "Repository named in the manuscript reference."),
    (NOTES, 356, "correr-ms-shelf", "cand-8263", "XI, E 2/6", "Manuscript shelf locator."),
    (NOTES, 356, "discendenze", "cand-8263", "Disccndenze patrizie", "S0 OCR surface; page image confirms the manuscript title Discendenze patrizie."),
    (NOTES, 357, "other-cycle", "cand-8254", "The other great cycle of canvases", "A separate cycle from the Tiepolo canvases discussed in note 3."),
    (NOTES, 357, "vendramin", "cand-8253", "Palazzo Vendramin-Calergi", "Named location of the other cycle."),
    (NOTES, 357, "roman-history-other-cycle", "cand-8254", "Roman history", "Subject range of the separate cycle."),
    (NOTES, 357, "bambini-attribution", "cand-0171", "Niccolo Bambini", "The attribution is reported, not presented as certain."),
    (NOTES, 357, "ivanov", "cand-8264", "Ivanov", "N. Ivanov as identified in the bibliography."),
    (NOTES, 357, "ivanov-1951", "cand-8265", "1951", "Publication year in the citation."),
    (NOTES, 357, "ivanov-pages", "cand-8265", "pp. 1-3", "Page locator in Ivanov's article."),
    (NOTES, 358, "see-note4", "cand-8261", "the works quoted in note 4 above", "Cross-reference to the sources listed in note 4."),
    (NOTES, 358, "renaldis", "cand-8266", "de Renaldis", "Full identity and title resolved from the book bibliography."),
    (NOTES, 359, "madrisio", "cand-8268", "Niccold Madrisio", "S0 OCR surface; page image and bibliography identify Niccolò Madrisio."),
    (NOTES, 359, "madrisio-1711", "cand-8269", "1711", "Publication year in the citation."),
    (NOTES, 359, "biasutti", "cand-8270", "Biasutti", "Guglielmo Biasutti identified from the bibliography."),
    (NOTES, 359, "biasutti-1958", "cand-8271", "1958", "Publication year in the citation."),
]
for spec in MENTION_SPECS:
    mention(*spec)

new_statements = []
existing_statement_ids = {r["statement_id"] for r in statements}


def statement(suffix, segment_id, first, last, subject, obj, predicate, claim, qualification,
              mentioned, marker=None, note_start=None, note_end=None, speaker="Haskell",
              text_layer="body", extras=None):
    sid = f"st-chp9-p252-{suffix}"
    if sid in existing_statement_ids or any(r["statement_id"] == sid for r in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    m = segment_by_id[segment_id]
    if first < m["line_start"] or last > m["line_end"]:
        raise SystemExit(f"statement lines outside segment {segment_id}: {sid}")
    if any(cid and cid not in candidate_ids for cid in [subject, obj, *mentioned]):
        raise SystemExit(f"missing candidate in statement: {sid}")
    q = {"source_line_start": first, "source_line_end": last, "printed_page": 252,
         "pdf_physical_page": 14, "claim": claim, "speaker": speaker, "text_layer": text_layer,
         "qualification": qualification, "mentioned_candidate_ids": list(dict.fromkeys(x for x in mentioned if x))}
    if marker is not None:
        q["footnote_marker"] = marker
    if note_start is not None:
        q["cross_reference_segments"] = [{"segment_id": NOTES, "source_line_start": note_start,
                                           "source_line_end": note_end if note_end is not None else note_start}]
    if extras:
        q.update(extras)
    new_statements.append({"statement_id": sid, "segment_id": segment_id,
                           "subject_candidate_id": subject, "object_candidate_id": obj,
                           "predicate": predicate, "qualifiers": q,
                           "original_quote": quote(segment_id, first, last), "origin": "book",
                           "source_file": segment_by_id[segment_id]["source_file"]})


statement("ricci-employment-pattern", P252, 117, 117, "cand-2154", "cand-8273",
          "employment_distribution_after_settlement_in_venice",
          "After settling in Venice, Sebastiano Ricci worked surprisingly little for the Venetian aristocracy and was employed more by the court of Turin, churches, and the English businessman Joseph Smith.",
          "This is Haskell's relative account of employment; no number of commissions or individual church is specified.",
          ["cand-2154", "cand-2719", "cand-8108", "cand-8273", "cand-2662", "cand-8274", "cand-2440"],
          extras={"relation_candidate": True, "cross_reference_segments": [{"segment_id": P251, "source_line_start": 114, "source_line_end": 114}]})
statement("tiepolo-career-style", P252, 118, 118, "cand-2569", "cand-8244",
          "successful_career_and_violent_tense_style_in_1720s",
          "Haskell says Tiepolo's immediately successful career began in the 1720s and that his violent, tense style appealed at that time.",
          "The style description and assessment of success are Haskell's; 'career began' follows his wording 'first began ... career'.",
          ["cand-2569", "cand-8244"])
statement("tiepolo-required-subjects", P252, 118, 118, "cand-2569", "cand-2587",
          "required_to_paint_battles_and_triumphs_from_roman_history",
          "Haskell says Tiepolo was particularly required to paint battle scenes and triumphs, largely drawn from Roman history.",
          "The passage does not enumerate commissions or identify the people who required them.",
          ["cand-2569", "cand-2587", "cand-8241"], marker=1, note_start=353, extras={"relation_candidate": True})
statement("venetian-families-roman-ancestry", P252, 118, 118, "cand-8276", "cand-8243",
          "families_claimed_roman_ancestry",
          "Haskell says many Venetian families claimed Roman ancestry and names the Corner among them.",
          "This records the author's report of family claims, not proof of descent; the unnamed group remains open.",
          ["cand-8276", "cand-8243", "cand-0848"])
statement("tiepolo-work-for-corner", P252, 118, 118, "cand-2569", "cand-0848",
          "worked_for_corner_before_1722",
          "Haskell says Tiepolo is known to have worked for the Corner before 1722.",
          "The source does not identify an individual Corner patron or the specific work.",
          ["cand-2569", "cand-0848", "cand-2616"], marker=2, note_start=354, extras={"relation_candidate": True})
statement("tiepolo-wars-context", P252, 118, 119, "cand-2569", "cand-8242",
          "dramatic_style_and_subjects_reflect_venetian_wars",
          "Haskell interprets Tiepolo's dramatic style and subject matter as reflecting Venice's wars with the Turks in the 1680s and again in 1715, when the city and its aristocracy last left their mark on European history.",
          "This is Haskell's historical and stylistic interpretation; the text does not name particular campaigns.",
          ["cand-2569", "cand-8244", "cand-8242", "cand-2719", "cand-7153", "cand-8108"],
          extras={"ocr_corrections": [{"line": 118, "ocr": "subjectmatter", "reading": "subject-matter", "basis": "CHP-9.pdf physical p.14"},
                                      {"line": 118, "ocr": "Venice��s", "reading": "Venice's", "basis": "CHP-9.pdf physical p.14"},
                                      {"line": 119, "ocr": "��the last", "reading": "—the last", "basis": "CHP-9.pdf physical p.14"},
                                      {"line": 119, "ocr": "chronicler \"of", "reading": "chronicler of", "basis": "CHP-9.pdf physical p.14"},
                                      {"line": 119, "ocr": "the city, and her aristocracy", "reading": "the city and her aristocracy", "basis": "CHP-9.pdf physical p.14"}]})
statement("tiepolo-dolfin-cycle", P252, 119, 119, "cand-2569", "cand-8241",
          "painted_ten_florus_based_roman_history_scenes_for_dolfin",
          "Haskell identifies ten large Roman-history scenes, selected from L. Annaeus Florus, as the most notable example of these echoes and says Tiepolo painted them for the Dolfin, his greatest patrons of the 1720s.",
          "Keep the series as a group because this passage does not name its individual canvases; the source's superlative and patronage description are Haskell's.",
          ["cand-2569", "cand-8241", "cand-8245", "cand-0931"], marker=3, note_start=355,
          extras={"relation_candidate": True, "footnote_markers": [3, 5], "footnote_refs": [
              {"marker": 3, "segment_id": NOTES, "source_line": 355},
              {"marker": 5, "segment_id": NOTES, "source_line": 357}], "footnote_segment": NOTES})
statement("dolfin-old-family", P252, 119, 119, "cand-0931", None,
          "family_characterized_as_tremendous_and_old_style",
          "Haskell calls the Dolfin a tremendous family in the old style.",
          "The characterization is evaluative and attributed to Haskell.", ["cand-0931"], marker=4, note_start=356)
statement("daniele-iii-public-service", P252, 119, 119, "cand-0927", "cand-8105",
          "served_state_abroad_and_at_home",
          "Haskell says Daniele III served the State abroad and at home throughout his life and was considered one of the finest orators of his day.",
          "The assessment of his oratory is reported as Haskell's characterization.", ["cand-0927", "cand-8105"])
statement("daniele-iii-will-programme", P252, 119, 119, "cand-0927", "cand-8246",
          "will_expressed_desire_to_restore_state_economy",
          "In the words Haskell attributes to Daniele III's will, Daniele regretted that he could not see through ideas conceived while serving in the Treasury to restore the State's economy in peacetime and wished he might shed his blood to heal its wounds.",
          "Quotation and document contents are reported through Haskell; the will itself was not independently consulted.",
          ["cand-0927", "cand-8246", "cand-8247", "cand-8105"], text_layer="quoted source reported by Haskell",
          extras={"relation_candidate": True})
statement("daniele-iii-conditional-bequest", P252, 119, 119, "cand-0927", "cand-8105",
          "estate_left_to_republic_if_male_line_extinguished",
          "Haskell says Daniele III's will left his entire estate to the Republic if his male line became extinct.",
          "Retain the condition and the will as Haskell's reported source; do not convert the bequest into an unconditional transfer.",
          ["cand-0927", "cand-8246", "cand-8105"], text_layer="reported will content", extras={"relation_candidate": True})
statement("daniele-iv-brother-of-iii", P252, 119, 119, "cand-0928", "cand-0927",
          "brother_of", "Haskell identifies Daniele IV as Daniele III's brother.",
          "The source explicitly states kinship but gives no additional family-branch detail.",
          ["cand-0928", "cand-0927"], extras={"relation_candidate": True})
statement("dionisio-younger-brother-of-iii", P252, 120, 121, "cand-0929", "cand-0927",
          "younger_brother_of", "Haskell identifies Dionisio as a younger brother of Daniele III.",
          "This statement isolates one of the two Danieles named in the source.",
          ["cand-0929", "cand-0927", "cand-0928"], extras={"relation_candidate": True})
statement("dionisio-younger-brother-of-iv", P252, 120, 121, "cand-0929", "cand-0928",
          "younger_brother_of", "Haskell identifies Dionisio as a younger brother of Daniele IV.",
          "This statement isolates one of the two Danieles named in the source.",
          ["cand-0929", "cand-0927", "cand-0928"], extras={"relation_candidate": True})
statement("daniele-iv-command", P252, 119, 119, "cand-0928", "cand-1705",
          "served_as_commander_under_morosini_in_peloponnese_and_1715",
          "Haskell says Daniele IV, who died in the same year as Daniele III (1729), was one of the most heroic commanders in the Turkish wars, serving under Morosini in the Peloponnese and again in 1715.",
          "'Same year' refers to the immediately preceding 1729 death date; 'most heroic' is Haskell's judgment.",
          ["cand-0928", "cand-0927", "cand-1705", "cand-8117", "cand-7153"],
          extras={"relation_candidate": True})
statement("dolfin-patriarchate", P252, 120, 120, "cand-0931", "cand-8248",
          "family_reported_to_hold_virtual_monopoly_of_patriarchate",
          "Haskell says the Dolfin enjoyed a virtual monopoly of the Patriarchate of Aquileia.",
          "Preserve 'virtual' and the unspecified period; this is Haskell's account, not an independently established institutional tenure.",
          ["cand-0931", "cand-8248"], marker=6, note_start=358, extras={"relation_candidate": True,
          "ocr_corrections": [{"line": 120, "ocr": "2 virtual", "reading": "a virtual", "basis": "CHP-9.pdf physical p.14"}]})
statement("dionisio-appointed-and-moved", P252, 120, 122, "cand-0929", "cand-8248",
          "given_patriarchal_post_in_1698_and_moved_to_udine",
          "Haskell says that in 1698 Dionisio was given the post and went to live in Udine, which he describes as the seat of the bishopric.",
          "The post's identity follows the preceding Patriarchate of Aquileia sentence; the text's 'bishopric' wording is retained without further institutional resolution.",
          ["cand-0929", "cand-8248", "cand-2666"], extras={"relation_candidate": True})
statement("dionisio-authority-and-residence", P252, 121, 122, "cand-0929", "cand-2666",
          "established_authority_and_left_records_of_36_year_residence",
          "Despite what Haskell calls Austria's bitter opposition, Dionisio imposed his authority on Udine and left many permanent records of a thirty-six-year residence there.",
          "The characterization and residence duration are reported by Haskell; no terminal date is inferred from the duration.",
          ["cand-0929", "cand-7284", "cand-2666"], extras={"ocr_corrections": [{"line": 122, "ocr": "thirty-six-year.residence", "reading": "thirty-six-year residence", "basis": "CHP-9.pdf physical p.14"}]})
statement("dionisio-library-and-bambini", P252, 122, 122, "cand-0929", "cand-8249",
          "built_udine_library_in_1708_decorated_by_bambini",
          "Haskell says Dionisio built a sumptuous library in Udine in 1708 and that Niccolo Bambini decorated it with frescoes.",
          "No individual fresco is identified; this library decoration remains distinct from the later ceiling fresco discussed in note 3.",
          ["cand-0929", "cand-8249", "cand-2666", "cand-0171", "cand-8250"], marker=7, note_start=359,
          extras={"relation_candidate": True})
statement("summoned-tiepolo-pending-purpose", P252, 122, 122, "cand-0929", "cand-2569",
          "summoned_tiepolo_after_work_at_unidentified_venice_palace",
          "Some eighteen years after building the library, Dionisio summoned Tiepolo, who had just finished working in an unidentified family palace at Venice.",
          "The sentence continues on p.253 with the commission's purpose; this statement records only the complete clause on p.252 and leaves the continuation open.",
          ["cand-0929", "cand-2569", "cand-8249", "cand-8252", "cand-2719"],
          extras={"relation_candidate": True, "continuation_segment": "chp-9:09_CHP-9_intro:l124-132"})
statement("early-sketches-note", NOTES, 353, 353, "cand-2569", "cand-8272",
          "surviving_sketches_and_drawings_as_evidence_of_early_work",
          "The footnote says the preceding point is shown by many surviving sketches and drawings from Tiepolo's early years.",
          "The note gives no individual object, repository, or catalogue locator.", ["cand-2569", "cand-8272"],
          speaker="Haskell's footnote", text_layer="footnote", extras={"cross_reference_segments": [{"segment_id": P252, "source_line_start": 118, "source_line_end": 118}]})
statement("da-canal-citation-note2", NOTES, 354, 354, "cand-7781", "cand-6593",
          "cites_da_canal_page_32",
          "Note 2 cites Da Canal, page 32; an existing candidate identifies the work as Vincenzo da Canal's Vita di Gregorio Lazzarini, published in Venice in 1809.",
          "Bibliographic identification comes from this book's bibliography; the cited page was not read independently.", ["cand-7781", "cand-6593"],
          marker=2, speaker="Haskell's footnote", text_layer="footnote")
statement("tiepolo-canvases-locations-and-correction", NOTES, 355, 355, "cand-8241", "cand-2582",
          "canvases_distributed_and_vienna_subject_corrected",
          "Haskell says the canvases are divided between Leningrad and Vienna and corrects the subject of one Vienna canvas, described by Morassi and others as Eteocles and Polynices, to Brutus killing Arruns, also taken from Florus.",
          "The correction and attribution history are reported by Haskell; the canvas and cited sources were not independently examined.",
          ["cand-8241", "cand-5796", "cand-2772", "cand-2582", "cand-8257", "cand-8258", "cand-8245", "cand-8259"],
          marker=3, speaker="Haskell's footnote", text_layer="footnote")
statement("unidentified-ceiling-fresco", NOTES, 355, 355, "cand-8251", "cand-8249",
          "ceiling_fresco_with_symbolic_figures_and_unknown_authorship",
          "Haskell describes a large ceiling fresco in the room where the Tiepolo canvases once hung, with a dolphin, ancient deities, Abundance, Arts and Sciences, Time, Fame and other symbolic figures, within an elaborate Bolognese-type architectural framework.",
          "Haskell says the artist and date remain mysterious and only tentatively places the fresco some years after Tiepolo's canvases; it is not attributed to Bambini or Tiepolo here.",
          ["cand-8251", "cand-8249", "cand-8241", "cand-8275", "cand-8188"],
          speaker="Haskell's footnote", text_layer="footnote", extras={"relationship_candidates": ["located_in", "depicts", "framed_by"],
          "ocr_corrections": [{"line": 355, "ocr": "Ans and Sciences", "reading": "Arts and Sciences", "basis": "CHP-9.pdf physical p.14"},
                              {"line": 355, "ocr": "arc still very mysterious", "reading": "are still very mysterious", "basis": "CHP-9.pdf physical p.14"},
                              {"line": 355, "ocr": "Tiepolo��s canvases", "reading": "Tiepolo's canvases", "basis": "CHP-9.pdf physical p.14"},
                              {"line": 355, "ocr": "Arruns��also", "reading": "Arruns—also", "basis": "CHP-9.pdf physical p.14"}]})
statement("da-canal-ibid-note3", NOTES, 355, 355, "cand-7781", "cand-6593",
          "ibid_citation_continues_da_canal_page_33",
          "Note 3 continues the Da Canal reference at page 33; its 'ibid.' refers to the work cited in note 2.",
          "Internal citation resolution only; the page was not read independently.", ["cand-7781", "cand-6593"], marker=3,
          speaker="Haskell's footnote", text_layer="footnote")
statement("morassi-citation-note3", NOTES, 355, 355, "cand-8257", "cand-8258",
          "cites_morassi_1955_figure_11",
          "Haskell identifies Morassi (1955, figure 11) among those who described the Vienna canvas as Eteocles and Polynices; the bibliography identifies Morassi's cited book as G. B. Tiepolo, London, 1955.",
          "Citation and reported prior identification only; no independent source reading is claimed.", ["cand-8257", "cand-8258", "cand-2582"],
          marker=3, speaker="Haskell's footnote", text_layer="footnote")
statement("florus-loeb-citation-note3", NOTES, 355, 355, "cand-8245", "cand-8259",
          "cites_loeb_florus_page_33_for_brutus_subject",
          "The note says the Brutus killing Arruns subject is also taken from the Loeb edition of Florus, page 33.",
          "The edition is not further identified in the note and was not consulted independently.", ["cand-8245", "cand-8259", "cand-2582"],
          marker=3, speaker="Haskell's footnote", text_layer="footnote")
statement("dolfin-and-correr-citations-note4", NOTES, 356, 356, "cand-8260", "cand-8261",
          "cites_dolfin_history_and_correr_manuscript",
          "Note 4 cites Bortolo Giovanni Dolfin's I Dolfin, pages 171 ff., and a manuscript in Biblioteca Correr XI, E 2/6 titled Discendenze patrizie.",
          "The bibliography resolves the abbreviated Dolfin citation; neither the cited pages nor the manuscript were consulted independently.",
          ["cand-8260", "cand-8261", "cand-8262", "cand-8263"], marker=4,
          speaker="Haskell's footnote", text_layer="footnote", extras={"relationship_candidates": ["cites"],
          "ocr_corrections": [{"line": 356, "ocr": "Disccndenze patrizie", "reading": "Discendenze patrizie", "basis": "CHP-9.pdf physical p.14"}]})
statement("vendramin-cycle-attribution-note5", NOTES, 357, 357, "cand-8254", "cand-8253",
          "separate_roman_history_cycle_attributed_to_bambini",
          "Note 5 places a separate cycle of Roman-history canvases at Palazzo Vendramin-Calergi and says they have been attributed to Niccolo Bambini, citing Ivanov, 1951, pages 1-3.",
          "The attribution is expressly reported as an attribution, not stated as a settled authorship; the printed note number is 5 although S0 OCR reads 6.",
          ["cand-8254", "cand-8253", "cand-0171", "cand-8264", "cand-8265"], marker=5,
          speaker="Haskell's footnote", text_layer="footnote", extras={"relation_candidate": True,
          "ocr_corrections": [{"line": 357, "ocr": "6", "reading": "5", "basis": "CHP-9.pdf physical p.14"}]})
statement("ivanov-citation-note5", NOTES, 357, 357, "cand-8264", "cand-8265",
          "cites_ivanov_1951_pages_1_to_3",
          "The note cites N. Ivanov's 1951 article Una postilla tiepolesca, pages 1-3, as the source for the reported Bambini attribution.",
          "Bibliographic identification comes from the book bibliography; the article was not consulted independently.",
          ["cand-8264", "cand-8265"], marker=5, speaker="Haskell's footnote", text_layer="footnote")
statement("renaldis-citation-note6", NOTES, 358, 358, "cand-8266", "cand-8267",
          "cites_de_renaldis_history_of_aquileia_patriarchate",
          "Note 6 refers to de Renaldis; the bibliography identifies Conte Girolamo de Renaldis's Memorie storiche dei tre ultimi secoli del patriarcato d'Aquileia (1411-1751), Udine, 1888.",
          "Citation identification only; the cited publication was not consulted independently.", ["cand-8266", "cand-8267"], marker=6,
          speaker="Haskell's footnote", text_layer="footnote")
statement("madrisio-biasutti-citation-note7", NOTES, 359, 359, "cand-8268", "cand-8269",
          "cites_madrisio_1711_and_biasutti_1958",
          "Note 7 cites Niccolò Madrisio, 1711, and Biasutti, 1958; the bibliography identifies Madrisio's oration about Dionigi Delfino's public library at Udine and Biasutti's Storia e Guida del Palazzo Arcivescovile di Udine.",
          "Bibliographic identification only; neither publication was consulted independently.", ["cand-8268", "cand-8269", "cand-8270", "cand-8271"],
          marker=7, speaker="Haskell's footnote", text_layer="footnote", extras={"ocr_corrections": [{"line": 359, "ocr": "Niccold", "reading": "Niccolò", "basis": "CHP-9.pdf physical p.14"}]})

if len({r["mention_id"] for r in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("mention IDs are not unique")
if len({r["statement_id"] for r in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("statement IDs are not unique")
coverage_by_id[P251].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L106-114",
    "note": "Printed p.251 is complete: the sentence ending L114 is closed at p.252 L117. Its notes 1-4 are recorded at consolidated lines L349-352.",
})
coverage_by_id[P252].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L117-122",
    "note": "Printed p.252 (CHP-9.pdf physical p.14) reviewed against the page image. L117 closes p.251 L114. Notes 1-7 were processed at consolidated lines L353-359; the final body clause at L122 continues on p.253. S2-only OCR corrections: L118 subjectmatter→subject-matter; L119 removed spurious quote before 'of' and comma after 'city'; L120 '2 virtual'→'a virtual'; L122 'thirty-six-year.residence'→'thirty-six-year residence'.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L349-359",
    "note": "Consolidated footnotes through printed p.252 note 7 are semantically processed in source order at L349-359. Later notes in this composite segment remain unprocessed. The printed p.252 note 5 is OCR'd as 6 at L357; corrected against CHP-9.pdf physical p.14 in S2 only.",
})

summary = {"segments": {sid: [coverage_by_id[sid]["disposition"], coverage_by_id[sid]["migration_status"],
                               coverage_by_id[sid]["source_line_ranges"]] for sid in (P251, P252, NOTES)},
           "new_candidates": len(candidate_specs), "new_mentions": len(new_mentions),
           "new_statements": len(new_statements), "source_hash": meta["sha256"],
           "ocr_corrections_recorded": 14}
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
