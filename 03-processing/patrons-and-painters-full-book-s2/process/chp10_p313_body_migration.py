"""Controlled S2 migration for printed p.313 body text; dry-run unless --apply."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_sec_ii.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_sec_ii.md"
SEGMENT = "chp-10:10_CHP-10_sec_ii:l72-81"
PREVIOUS_SEGMENT = "chp-10:10_CHP-10_sec_ii:l17-32"
EXPECTED_ASSET_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
EXPECTED_SEGMENT_SHA = "33904e26e12604621ed232cec6d304fbd67037bf50e633717a375ba6e1f605e0"
BACKUP_SUFFIX = ".bak-s2-chp10-p313-body-20261003"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write reviewed p.313 rows after creating recovery copies")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[71:81]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA:
    raise SystemExit("S2 source segment changed")
if segment_lines[0] != "[Page 313]" or not segment_lines[-1].endswith("dramatic"):
    raise SystemExit("p.313 segment boundaries changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
if (len(candidates), max(int(row["candidate_id"].split("-")[1]) for row in candidates), len(mentions), len(statements)) != (9577, 9590, 20021, 8873):
    raise SystemExit("table state changed; re-read current table counts before migration")
REQUIRED = {
    "guardi": "cand-1245", "schulenburg": "cand-2401", "portraits": "cand-1247",
    "turkish_scenes": "cand-1251", "copyist_works": "cand-1252",
    "veronese": "cand-2755", "marriage_at_cana": "cand-2757", "madonna_and_child": "cand-2756",
    "tintoretto": "cand-2627", "temperance": "cand-2629", "fortitude": "cand-2628",
    "bassano": "cand-0257", "nativity": "cand-0258", "giorgio_maggiore": "cand-0732",
    "s_zaccaria": "cand-0743", "madonna_orto": "cand-0727", "sebastiano_ricci": "cand-2154",
    "piazzetta": "cand-3862", "carriera": "cand-0581", "van_mour": "cand-1712",
    "pittoni": "cand-3870", "pittoni_history": "cand-1953", "pittoni_german_patrons": "cand-1952",
    "piazzetta_pictures": "cand-1918", "tiepolo": "cand-3781",
}
for label, candidate_id in REQUIRED.items():
    if candidate_id not in candidate_ids:
        raise SystemExit(f"required candidate missing: {label}={candidate_id}")
coverage = {row["segment_id"]: row for row in coverage_rows}
if (coverage[SEGMENT]["disposition"], coverage[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"p.313 coverage state changed: {coverage[SEGMENT]}")
if coverage[PREVIOUS_SEGMENT]["migration_status"] != "partial":
    raise SystemExit("expected p.312 continuation segment to remain partial pending its notes")
if any(row["segment_id"] == SEGMENT for row in mentions) or any(row["segment_id"] == SEGMENT for row in statements):
    raise SystemExit("p.313 already has S2 mention or statement rows")

new_candidates = []


def add_candidate(candidate_id, canonical_name, suggested_type, detail, source_line):
    if candidate_id in candidate_ids or any(row["candidate_id"] == candidate_id for row in new_candidates):
        raise SystemExit(f"candidate id already exists: {candidate_id}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": candidate_id,
        "canonical_name": canonical_name,
        "suggested_type": suggested_type,
        "status": "open",
        "detail": detail,
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L{source_line}",
    })
    new_candidates.append(row)


add_candidate(
    "cand-9591",
    "Gian Antonio Guardi's 1737 history pictures (untitled group)",
    "work",
    "Haskell reports one 1737 occasion on which Guardi was commissioned to paint history pictures of his own; the works have no supplied titles or count. He was paid about ten zecchini for the lot. The commissioning party is not named in this sentence.",
    73,
)
add_candidate(
    "cand-9592",
    "Scipio (named figure in Pittoni's p.313 history-picture series; identity unresolved)",
    "person",
    "Named as a represented subject in Pittoni's series for Schulenburg; the source does not specify which Scipio.",
    78,
)
add_candidate(
    "cand-9593",
    "Alexander the Great (named figure in Pittoni's p.313 history-picture series)",
    "person",
    "Named as a represented subject in Pittoni's series for Schulenburg; cross-chapter alignment is deferred to S3.",
    78,
)
add_candidate(
    "cand-9594",
    "Polyxena (named mythological figure in Pittoni's p.313 history-picture series)",
    "",
    "Named as a represented subject; preserve as a source candidate without forcing mythological role into the person type.",
    78,
)
add_candidate(
    "cand-9595",
    "Iphigenia (named mythological figure in Pittoni's p.313 history-picture series)",
    "",
    "Named as a represented subject; preserve as a source candidate without forcing mythological role into the person type.",
    78,
)
candidate_ids.update(row["candidate_id"] for row in new_candidates)

new_mentions = []


def add_mention(line_no, surface, candidate_id, note="", occurrence=0):
    line = source_lines[line_no - 1]
    starts = []
    cursor = 0
    while True:
        at = line.find(surface, cursor)
        if at < 0:
            break
        starts.append(at)
        cursor = at + 1
    if occurrence >= len(starts):
        raise SystemExit(f"mention text not found on L{line_no}: {surface!r} occurrence {occurrence}")
    relative_line = line_no - 72
    start = sum(len(item) + 1 for item in segment_lines[:relative_line]) + starts[occurrence]
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p313-{len(new_mentions) + 1:04d}",
        "segment_id": SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    if segment_text[start:start + len(surface)] != surface:
        raise SystemExit(f"mention span mismatch: {surface!r}")
    new_mentions.append(row)


def add_span(surface, candidate_id, note="", occurrence=0):
    starts = []
    cursor = 0
    while True:
        at = segment_text.find(surface, cursor)
        if at < 0:
            break
        starts.append(at)
        cursor = at + 1
    if occurrence >= len(starts):
        raise SystemExit(f"cross-line mention text not found: {surface!r}")
    start = starts[occurrence]
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p313-{len(new_mentions) + 1:04d}",
        "segment_id": SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    if segment_text[start:start + len(surface)] != surface:
        raise SystemExit(f"cross-line mention span mismatch: {surface!r}")
    new_mentions.append(row)


# Coreference and named-entity mentions on p.313. OCR forms are retained exactly.
add_mention(73, "his own right", REQUIRED["guardi"], "Continuation of p.312 L26's 'not so much as an'; the antecedent is Guardi.")
add_mention(73, "his employment", REQUIRED["guardi"])
add_mention(73, "was he commissioned", REQUIRED["guardi"])
add_mention(73, "history pictures of his own", "cand-9591")
add_mention(73, "he was then paid", REQUIRED["guardi"])
add_mention(73, "the lot", "cand-9591")
add_mention(73, "they", "cand-9591", "Pronoun refers to the untitled history pictures.")
add_mention(73, "he was required", REQUIRED["guardi"])
add_mention(73, "Veronese", REQUIRED["veronese"])
add_mention(73, "Marriage at", REQUIRED["marriage_at_cana"], "Title continues with 'Cana' at the start of L74.")
add_mention(74, "Cana", REQUIRED["marriage_at_cana"], "Continuation of the work title split across source lines.")
add_mention(74, "S. Giorgio Maggiore", REQUIRED["giorgio_maggiore"])
add_mention(74, "Madonna and Child with Saints", REQUIRED["madonna_and_child"])
add_mention(74, "S. Zaccaria", REQUIRED["s_zaccaria"])
add_mention(74, "Tintoretto", REQUIRED["tintoretto"])
add_mention(74, "Temperance", REQUIRED["temperance"])
add_mention(74, "Fortitude", REQUIRED["fortitude"])
add_mention(74, "Madonna dell’Orto", REQUIRED["madonna_orto"])
add_mention(74, "Bassano", REQUIRED["bassano"])
add_mention(74, "Nativity", REQUIRED["nativity"])
add_mention(74, "S.", REQUIRED["giorgio_maggiore"], "Place name continues on L75.")
add_mention(75, "Giorgio Maggiore", REQUIRED["giorgio_maggiore"], "Continuation of the place name split across source lines.")
add_mention(75, "his own contemporaries", REQUIRED["guardi"])
add_mention(75, "Sebastiano Ricci", REQUIRED["sebastiano_ricci"])
add_mention(76, "Piazzetta", REQUIRED["piazzetta"])
add_mention(76, "Rosalba Camera", REQUIRED["carriera"], "S0 OCR reads Camera; CHP-10.pdf physical page 46 prints Carriera.")
add_mention(76, "His remaining time", REQUIRED["guardi"])
add_mention(76, "portraits", REQUIRED["portraits"])
add_mention(76, "Schulenburg himself", REQUIRED["schulenburg"])
add_mention(76, "his friends", REQUIRED["schulenburg"])
add_mention(76, "his own walls", REQUIRED["schulenburg"])
add_mention(76, "those that have survived", REQUIRED["portraits"], "Anaphoric reference to the portrait group just described.")
add_mention(76, "the Guardi magic", REQUIRED["guardi"])
add_mention(76, "little Turkish scenes", REQUIRED["turkish_scenes"])
add_mention(76, "Van Mour", REQUIRED["van_mour"])
add_mention(76, "the artist", REQUIRED["guardi"])
add_mention(76, "his talent", REQUIRED["guardi"])
add_mention(76, "Schulenburg", REQUIRED["schulenburg"])
add_mention(76, "Guardi", REQUIRED["guardi"])
add_mention(76, "his gifts", REQUIRED["guardi"])
add_mention(76, "he ordered", REQUIRED["schulenburg"])
add_mention(76, "him to paint", REQUIRED["guardi"])
add_mention(76, "these idyllic versions", REQUIRED["turkish_scenes"], "Corefers to the little Turkish scenes immediately preceding; do not create a second work group.")
add_mention(76, "his most ferocious enemies", REQUIRED["schulenburg"])
add_mention(77, "the Marshal’s tastes", REQUIRED["schulenburg"])
add_mention(77, "his collection", REQUIRED["schulenburg"])
add_mention(77, "Pittoni", REQUIRED["pittoni"])
add_mention(77, "Piazzetta", REQUIRED["piazzetta"])
add_mention(77, "Schulenburg", REQUIRED["schulenburg"])
add_mention(77, "him", REQUIRED["pittoni"], "In 'commissioning pictures from him', the pronoun refers to Pittoni.")
add_mention(77, "his fellow-citizens", REQUIRED["pittoni"])
add_mention(77, "he would be asked", REQUIRED["pittoni"])
add_mention(77, "he was already much in favour", REQUIRED["pittoni"])
add_mention(77, "German patrons", REQUIRED["pittoni_german_patrons"])
add_mention(77, "For Pittoni", REQUIRED["pittoni"])
add_mention(77, "his contemporaries", REQUIRED["pittoni"])
add_mention(77, "Tiepolo", REQUIRED["tiepolo"])
add_mention(77, "himself", REQUIRED["tiepolo"])
add_mention(77, "Pittoni", REQUIRED["pittoni"], occurrence=1)
add_mention(77, "he was therefore much in demand", REQUIRED["pittoni"])
add_mention(77, "For Schulenburg", REQUIRED["schulenburg"])
add_mention(77, "he produced", REQUIRED["pittoni"])
add_mention(78, "Scipio", "cand-9592")
add_mention(78, "Alexander the Great", "cand-9593")
add_mention(78, "Polyxena", "cand-9594")
add_mention(78, "Iphigenia", "cand-9595")
add_mention(79, "Piazzetta", REQUIRED["piazzetta"])
add_mention(79, "Schulenburg", REQUIRED["schulenburg"])
add_mention(79, "any other artist except", REQUIRED["guardi"], "Guardi is the explicit exception in the comparison.")
add_mention(80, "Gian Antonio Guardi", REQUIRED["guardi"])
add_mention(80, "his case", REQUIRED["piazzetta"])
add_mention(80, "this patronage", REQUIRED["schulenburg"])
add_mention(81, "the Marshal", REQUIRED["schulenburg"])
add_mention(81, "Piazzetta’s gifts", REQUIRED["piazzetta"], "Sentence continues at p.314 L84; no completed claim is asserted from this fragment.")

new_statements = []


def add_statement(statement_id, subject, object_id, predicate, line_start, line_end, claim, quote, qualification,
                  mentioned, relation_candidate=False, extra=None):
    if quote not in segment_text:
        raise SystemExit(f"statement quote is not anchored in the p.313 segment: {statement_id}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 313,
        "pdf_physical_page": 46,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial claim",
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
        "relation_candidate": relation_candidate,
    }
    if extra:
        qualifiers.update(extra)
    if any(cid not in candidate_ids for cid in qualifiers["mentioned_candidate_ids"]):
        raise SystemExit(f"missing mentioned candidate in {statement_id}")
    new_statements.append({
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    })


add_statement(
    "st-chp10-p313-guardi-copyist-role-continuation", REQUIRED["guardi"], None,
    "guardi_valued_as_copyist_and_hack_not_original_painter", 73, 73,
    "The p.312–313 sentence contrasts Guardi as a useful copyist and hack with an original painter in his own right.",
    "original painter in his own right as a useful copyistand hack.",
    "Continuation of st-chp10-p312-guardi-salary-and-role-fragment, whose p.312 fragment ends 'not so much as an'. Print has a space in 'copyist and'; S0 OCR is unchanged.",
    [REQUIRED["guardi"]], False,
    {"continuation_of_statement_id": "st-chp10-p312-guardi-salary-and-role-fragment", "ocr_print_correction": "copyistand -> copyist and"},
)
add_statement(
    "st-chp10-p313-guardi-history-pictures-1737", REQUIRED["guardi"], "cand-9591",
    "commissioned_once_to_paint_own_history_pictures_in_1737", 73, 73,
    "During his employment, Guardi was commissioned once, in 1737, to paint history pictures of his own; Haskell reports about ten zecchini for the lot and infers the pictures were small and of little consequence.",
    "During the whole period ofhis employment only once—in 1737—was he commissioned to paint history pictures of his own; and the miserable sum he was then paid (about ten zecchini for the lot) shows that they must have been small and of little consequence.",
    "The commissioner is not named in this sentence. 'About ten' and Haskell's inference about scale and significance remain qualified; OCR 'ofhis' is printed 'of his'.",
    [REQUIRED["guardi"], "cand-9591"], True,
    {"ocr_print_correction": "ofhis -> of his"},
)

copy_specs = [
    ("marriage-at-cana", "cand-2757", "Veronese’s Marriage at\nCana in S. Giorgio Maggiore", "Veronese", ["cand-2757", "cand-0732"], "Haskell says Guardi was required to copy Veronese’s Marriage at Cana in S. Giorgio Maggiore."),
    ("madonna-and-child", "cand-2756", "Madonna and Child with Saints in S. Zaccaria", "Veronese", ["cand-2756", "cand-0743"], "Haskell says Guardi was required to copy Veronese’s Madonna and Child with Saints in S. Zaccaria."),
    ("tintoretto-temperance", "cand-2629", "Tintoretto’s Temperance", "Tintoretto", ["cand-2629", "cand-0727"], "Haskell says Guardi was required to copy Tintoretto’s Temperance in the Madonna dell’Orto."),
    ("tintoretto-fortitude", "cand-2628", "Fortitude in the Madonna dell’Orto", "Tintoretto", ["cand-2628", "cand-0727"], "Haskell says Guardi was required to copy Tintoretto’s Fortitude in the Madonna dell’Orto."),
    ("bassano-nativity", "cand-0258", "Bassano’s Nativity in S.\nGiorgio Maggiore", "Bassano", ["cand-0258", "cand-0732"], "Haskell says Guardi was required to copy Bassano’s Nativity in S. Giorgio Maggiore."),
]
copy_quotes = {
    "marriage-at-cana": "Veronese’s Marriage at\nCana in S. Giorgio Maggiore",
    "madonna-and-child": "Madonna and Child with Saints in S. Zaccaria",
    "tintoretto-temperance": "Tintoretto’s Temperance",
    "tintoretto-fortitude": "Fortitude in the Madonna dell’Orto",
    "bassano-nativity": "Bassano’s Nativity in S.\nGiorgio Maggiore",
}
for slug, work_candidate, quote, artist, mentioned, claim in copy_specs:
    add_statement(
        f"st-chp10-p313-guardi-copied-{slug}", REQUIRED["guardi"], work_candidate,
        "required_to_copy_named_venetian_masterpiece", 73, 75 if "Nativity" in quote else 74,
        claim, copy_quotes[slug],
        "The source names the originals and sites but does not identify the specific copies made by Guardi or their dates.",
        [REQUIRED["guardi"], *mentioned], True,
    )

add_statement(
    "st-chp10-p313-guardi-copied-contemporary-pictures", REQUIRED["guardi"], "cand-1252",
    "required_to_copy_pictures_by_his_contemporary_artists", 75, 76,
    "Guardi was also required to copy pictures by his contemporaries Sebastiano Ricci, Piazzetta, and Rosalba Carriera.",
    "and even pictures by his own contemporaries, Sebastiano Ricci,\nPiazzetta and Rosalba Camera.",
    "No individual works or count are named. The OCR reads 'Camera'; p.313 print reads 'Carriera'.",
    [REQUIRED["guardi"], REQUIRED["copyist_works"], REQUIRED["sebastiano_ricci"], REQUIRED["piazzetta"], REQUIRED["carriera"]],
    True, {"ocr_print_correction": "Rosalba Camera -> Rosalba Carriera"},
)
add_statement(
    "st-chp10-p313-guardi-portraits-and-distribution", REQUIRED["guardi"], REQUIRED["portraits"],
    "painted_schulenburg_portraits_for_gifts_and_portraits_of_his_connections", 76, 76,
    "Guardi spent much of his remaining time producing portraits, sometimes as many as six a year: Schulenburg portraits were given to friends and royal admirers, while portraits of the Marshal’s connections were hung on his own walls.",
    "His remaining time was spent on churning out an endless succession of portraits, sometimes as many as six a year, of Schulenburg himself to be given to his friends and royal admirers, or of those grand connections to be hung on his own walls.",
    "'As many as six' is a maximum, not an annual total. The source names neither the connections nor individual portraits.",
    [REQUIRED["guardi"], REQUIRED["portraits"], REQUIRED["schulenburg"]], True,
)
add_statement(
    "st-chp10-p313-surviving-guardi-portraits-quality", REQUIRED["guardi"], REQUIRED["portraits"],
    "haskell_judges_surviving_portraits_generally_low_quality", 76, 76,
    "Haskell judges the surviving portraits generally low in quality and says only rarely did Guardi transform a pedestrian original into a work of beauty.",
    "It is not surprising that the quality of those that have survived is generally low1; only.rarely does the Guardi magic transform an obviously pedestrian original into a work of authentic beauty",
    "This is Haskell’s evaluative judgment, not a measured quality claim. Footnote marker 1 is pending at canonical note line 284; print spacing is 'only rarely'.",
    [REQUIRED["guardi"], REQUIRED["portraits"]], False,
    {"footnote_marker": 1, "pending_note_source_line": 284, "ocr_print_correction": "only.rarely -> only rarely"},
)
add_statement(
    "st-chp10-p313-guardi-turkish-scenes-after-van-mour", REQUIRED["guardi"], REQUIRED["turkish_scenes"],
    "copied_turkish_scenes_from_engravings_after_van_mour_in_1742_1743", 76, 76,
    "The Turkish scenes copied in 1742 and 1743 from engravings taken from Van Mour are the passage’s rare examples of Guardi’s artistic gift for delicate, sparkling fantasy.",
    "most conspicuously in the little Turkish scenes copied in 1742 and 1743 from engravings taken from Van Mour—here at last the artist was given the opportunity to display his talent for delicate and sparkling fantasy.2",
    "The source does not name the engraver or individual prints and does not state that Van Mour made the engravings. Footnote marker 2 is pending at canonical note line 285; print reads 'did not lie' earlier in this sentence, while OCR has 'did notdie'.",
    [REQUIRED["guardi"], REQUIRED["turkish_scenes"], REQUIRED["van_mour"]], True,
    {"footnote_marker": 2, "pending_note_source_line": 285},
)
add_statement(
    "st-chp10-p313-schulenburg-commissioned-idyllic-turkish-scenes", REQUIRED["schulenburg"], REQUIRED["turkish_scenes"],
    "ordered_guardi_to_paint_idyllic_versions_of_enemies_customs", 76, 76,
    "Schulenburg ordered Guardi to paint idyllic versions of the customs of his enemies; 'these idyllic versions' refers back to the Turkish scenes just described.",
    "Schulenburg, who was Guardi’s most persistent patron, wholly failed to appreciate the true nature ofhis gifts except on the one occasion when he ordered him to paint these idyllic versions of the customs of his most ferocious enemies.",
    "Coreference is resolved from the immediately preceding sentence; do not create a second work group. The sentence does not name the individual sitters or scenes; OCR 'ofhis' is printed 'of his'.",
    [REQUIRED["schulenburg"], REQUIRED["guardi"], REQUIRED["turkish_scenes"]], True,
    {"coreference_target_candidate_id": REQUIRED["turkish_scenes"], "ocr_print_correction": "ofhis -> of his"},
)
add_statement(
    "st-chp10-p313-schulenburg-patronage-judgment-on-guardi", REQUIRED["schulenburg"], REQUIRED["guardi"],
    "most_persistent_patron_but_failed_to_appreciate_guardis_gifts", 76, 76,
    "Haskell calls Schulenburg Guardi’s most persistent patron but says that he failed to appreciate the nature of Guardi’s gifts except in the commission for the Turkish scenes.",
    "Schulenburg, who was Guardi’s most persistent patron, wholly failed to appreciate the true nature ofhis gifts except on the one occasion",
    "This is Haskell’s characterization of the patronage relationship, not evidence of personal friendship. The exception is coreferential with the Turkish scene group.",
    [REQUIRED["schulenburg"], REQUIRED["guardi"], REQUIRED["turkish_scenes"]], True,
)
add_statement(
    "st-chp10-p313-schulenburg-collection-history-and-genre-paintings", REQUIRED["schulenburg"], None,
    "collection_nucleus_history_and_genre_paintings_by_pittoni_and_piazzetta", 77, 77,
    "The nucleus of Schulenburg’s collection consisted of history and genre paintings by Pittoni and Piazzetta.",
    "In fact, the Marshal’s tastes veered in a very different direction. The nucleus ofhis collection was made up oshistory and genre paintings by Pittoni and Piazzetta.3",
    "No individual collection items or counts are named. Print reads 'of his' and 'of history'; footnote marker 3 is pending at canonical note line 286.",
    [REQUIRED["schulenburg"], REQUIRED["pittoni"], REQUIRED["piazzetta"], REQUIRED["pittoni_history"], REQUIRED["piazzetta_pictures"]], True,
    {"footnote_marker": 3, "pending_note_source_line": 286, "ocr_print_correction": "oshistory -> of history; ofhis -> of his"},
)
add_statement(
    "st-chp10-p313-pittoni-schulenburg-commission-and-reputation", REQUIRED["schulenburg"], REQUIRED["pittoni_history"],
    "commissioned_pittoni_pictures_during_1730s", 77, 77,
    "During the 1730s Schulenburg commissioned pictures from Pittoni, who Haskell describes as one of Venice’s leading history painters and already favored by German patrons.",
    "During the ’thirties, when Schulenburg was commissioning pictures from him, Pittoni was considered to be one of the leading history painters in Venice. Almost alone among his fellow-citizens he would be asked to contribute a canvas when large-scale international commissions were being planned for some royal court, and he was already much in favour with German patrons.4",
    "The passage does not identify a specific international commission or German patron. Footnote marker 4 is pending at canonical note line 287.",
    [REQUIRED["schulenburg"], REQUIRED["pittoni"], REQUIRED["pittoni_history"], REQUIRED["pittoni_german_patrons"]], True,
    {"footnote_marker": 4, "pending_note_source_line": 287},
)
add_statement(
    "st-chp10-p313-pittoni-history-painting-style", REQUIRED["pittoni"], None,
    "pittoni_history_subjects_as_current_baroque_melodramas", 77, 77,
    "Haskell says Pittoni turned Greek, Roman, and Biblical history episodes into melodramas representing the most acceptable and up-to-date versions of older Baroque themes.",
    "For Pittoni turned the main episodes of Greek, Roman and Biblical history into melodramas which represented for his contemporaries the most acceptable and up-to-date versions of the old Baroque themes.",
    "This is Haskell’s interpretation of Pittoni’s style. The source transcription and printed page both read 'melodramas'; no OCR correction is needed.",
    [REQUIRED["pittoni"]], False,
)
add_statement(
    "st-chp10-p313-pittoni-easel-pictures-and-tiepolo-comparison", REQUIRED["pittoni"], REQUIRED["tiepolo"],
    "pittoni_painted_easel_pictures_whereas_tiepolo_largely_painted_frescoes", 77, 77,
    "Haskell contrasts Tiepolo’s largely fresco-based practice with Pittoni’s preference for easel pictures and says Pittoni was consequently in demand among collectors.",
    "Unlike Tiepolo who largely confined himself to frescoes, Pittoni rarely painted other than easel pictures and he was therefore much in demand among collectors.",
    "The contrast does not mean Tiepolo painted only frescoes or that Pittoni never painted another medium.",
    [REQUIRED["pittoni"], REQUIRED["tiepolo"]], False,
)
add_statement(
    "st-chp10-p313-pittoni-history-series-for-schulenburg", REQUIRED["pittoni"], REQUIRED["pittoni_history"],
    "produced_schulenburg_series_of_greek_and_roman_valour_sacrifice_pictures", 77, 78,
    "For Schulenburg, Pittoni produced a series of pictures showing Greek and Roman scenes of valour and sacrifice, including subjects named Scipio, Alexander the Great, Polyxena, and Iphigenia.",
    "For Schulenburg he produced a series of pictures illustrating scenes of high Greek and Roman valour and sacrifice—\nScipio and Alexander the Great, Polyxena and Iphigenia.",
    "The source does not give separate work titles or identify which Scipio. Named mythological figure candidates remain type-unresolved; do not split the series into four titled works.",
    [REQUIRED["pittoni"], REQUIRED["schulenburg"], REQUIRED["pittoni_history"], "cand-9592", "cand-9593", "cand-9594", "cand-9595"], True,
)
add_statement(
    "st-chp10-p313-piazzetta-closer-schulenburg-relationship", REQUIRED["piazzetta"], REQUIRED["schulenburg"],
    "closer_artist_patron_relationship_except_guardi_and_beneficial_patronage", 79, 80,
    "Haskell says Piazzetta had a closer relationship with Schulenburg than any artist except Guardi and describes the results of this patronage as wholly beneficial.",
    "Piazzetta enjoyed a closer relationship with Schulenburg than any other artist except\nGian Antonio Guardi, and in his case the results of this patronage were wholly beneficial.",
    "The comparison is not a claim of friendship. The next sentence about Piazzetta’s gifts continues at p.314 L84 and is left partial there.",
    [REQUIRED["piazzetta"], REQUIRED["schulenburg"], REQUIRED["guardi"]], True,
)

# Replace the p.312 truncated role interpretation with its completed salary-only
# claim; the p.313 continuation is stored above as a separate, line-anchored statement.
previous_statement_id = "st-chp10-p312-guardi-salary-and-role-fragment"
previous_statement = next((row for row in statements if row["statement_id"] == previous_statement_id), None)
if not previous_statement:
    raise SystemExit("p.312 continuation statement is missing")
if previous_statement["qualifiers"].get("claim") != "Haskell says Guardi received a monthly salary from Schulenburg and begins to contrast his role with that of an original painter.":
    raise SystemExit("p.312 continuation statement has changed; review before replacing its incomplete claim")
previous_statement["predicate"] = "guardi_received_monthly_salary_from_schulenburg"
previous_statement["qualifiers"]["claim"] = "Haskell says Guardi received a monthly salary from Schulenburg."
previous_statement["qualifiers"]["qualification"] = (
    "The salary claim ends on p.312 L26. The following role contrast continues at p.313 L73 and is recorded in "
    "st-chp10-p313-guardi-copyist-role-continuation; the p.312 and p.313 fragments are linked, not treated as duplicate claims."
)
previous_statement["qualifiers"]["continuation_statement_id"] = "st-chp10-p313-guardi-copyist-role-continuation"

previous_coverage = coverage[PREVIOUS_SEGMENT]
previous_coverage["note"] = (
    "Printed p.312 body L18-26 read against CHP-10.pdf physical p.41. L18 closes the p.311 will sentence. "
    "The p.312 L26 salary claim is recorded separately; its role contrast continues at p.313 L73 and is now linked "
    "to st-chp10-p313-guardi-copyist-role-continuation. Coverage remains partial because printed p.312 footnotes "
    "1-6 are confirmed but await canonical notes L279-283; L27-32 is duplicated/partial page-footer OCR and will "
    "not be migrated twice. Print supplies markers 5 and 6 missing from body OCR."
)
coverage[SEGMENT].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L73-81",
    "note": (
        "Read printed p.313 against CHP-10.pdf physical p.46. L73 completes the p.312 role sentence; p.313’s final "
        "Piazzetta sentence continues at p.314 L84, so it is not asserted as complete. Body statements, copy-work "
        "candidates, coreferences and OCR corrections are recorded; footnote markers 1-4 await canonical note lines "
        "L284-287. Print corrections recorded without changing S0: copyist and; of his; Carriera (OCR Camera); "
        "only rarely; did not lie; of history."
    ),
})

candidate_rows = candidates + new_candidates
mention_rows = mentions + new_mentions
statement_rows = statements + new_statements
if len({row["candidate_id"] for row in candidate_rows}) != len(candidate_rows):
    raise SystemExit("duplicate candidate id")
if len({row["mention_id"] for row in mention_rows}) != len(mention_rows):
    raise SystemExit("duplicate mention id")
if len({row["statement_id"] for row in statement_rows}) != len(statement_rows):
    raise SystemExit("duplicate statement id")
if any(row["candidate_id"] not in {c["candidate_id"] for c in candidate_rows} for row in new_mentions):
    raise SystemExit("missing mention candidate foreign key")

print(f"p.313 preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print(f"p.312 role-continuation statement linked and narrowed to the salary claim")
print(f"coverage: p.313 reviewed/partial, p.312 remains partial pending its notes; totals {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(statement_rows)} statements")
if not args.apply:
    raise SystemExit(0)

targets = [candidate_path, mention_path, statement_path, coverage_path]
for path in targets:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    shutil.copy2(path, backup)
write_csv(candidate_path, candidate_fields, candidate_rows)
write_csv(mention_path, mention_fields, mention_rows)
write_jsonl(statement_path, statement_rows)
write_csv(coverage_path, coverage_fields, coverage_rows)
print(f"applied; four recovery copies created with suffix {BACKUP_SUFFIX}")
