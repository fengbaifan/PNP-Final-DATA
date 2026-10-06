"""Controlled S2 migration for printed p.277; dry-run by default."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SEGMENT = "chp-10:10_CHP-10_intro:l15-24"
NEXT = "chp-10:10_CHP-10_intro:l26-41"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
SEGMENT_SHA = "805e94a2f007dadc0e072f08626951f78aa77c3f304e43af0768aff09c9746ed"
MAX_CANDIDATE = 8840
BACKUP_SUFFIX = ".bak-s2-chp10-p277-20261002"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


source_bytes = SOURCE.read_bytes()
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if hashlib.sha256(source_bytes).hexdigest() != ASSET_SHA:
    raise SystemExit("Chapter 10 intro source asset changed")

segment_rows = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segment_rows}
segment_meta = segment_by_id.get(SEGMENT)
if not segment_meta or segment_meta.get("sha256") != SEGMENT_SHA or segment_meta.get("asset_sha256") != ASSET_SHA:
    raise SystemExit("p.277 source segment missing or changed")
segment_text = "\n".join(source_lines[segment_meta["line_start"] - 1 : segment_meta["line_end"]])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("p.277 source segment content hash mismatch")
if source_lines[14].strip() != "[Page 277]" or "Maximilian of Bavaria" not in source_lines[15]:
    raise SystemExit("expected p.277 source text changed")
if "not-an. impoverished Republic" not in source_lines[19] or not source_lines[20].startswith("’ easily appreciated"):
    raise SystemExit("expected p.277 OCR surface changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
mention_ids = {row["mention_id"] for row in mentions}
statement_ids = {row["statement_id"] for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if maximum != MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {MAX_CANDIDATE}, found {maximum}")
for segment_id in (SEGMENT, NEXT):
    row = coverage_by_id.get(segment_id)
    expected = ("queued", "pending")
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"unexpected coverage state for {segment_id}: {row}")

E = {
    "maximilian": "cand-1587",
    "christian_louis": "cand-1605",
    "elector_pal": "cand-1325",
    "frederick": "cand-1078",
    "carriera": "cand-0581",
    "carlevarijs": "cand-0554",
    "carlevarijs_regatta_index": "cand-0558",
    "augustus": "cand-0148",
    "venice": "cand-2719",
    "republic": "cand-8838",
    "nobility": "cand-8677",
    "dresden": "cand-0947",
    "crozat": "cand-0894",
    "paris": "cand-4653",
    "versailles": "cand-3985",
    "watteau": "cand-2804",
    "canaletto": "cand-0504",
    "england": "cand-7200",
    "france": "cand-5317",
    "germany": "cand-5529",
    "sweden": "cand-6036",
    "europe": "cand-3462",
}
for key, candidate_id in E.items():
    if candidate_id not in candidate_ids:
        raise SystemExit(f"required existing candidate missing: {key}={candidate_id}")

CANDIDATE_SPECS = [
    ("german_princes", "German princes commissioning portraits and seeking Rosalba's work in Haskell's p.277 account (unnamed collective)", "term", "Collective framing for the German princes introduced on p.277; Maximilian, Christian Louis, and the Palatine Elector are named or indexed separately. Do not treat the group as a formal institution.", 16),
    ("max_portrait", "Unidentified portrait of Maximilian of Bavaria by Rosalba Carriera (commissioned in 1704)", "work", "Haskell reports that Maximilian commissioned his portrait from Rosalba in 1704; no title, present location, or independent catalogue identity is supplied here.", 16),
    ("max_women_portraits", "Unidentified portraits of women in Venice commissioned by Maximilian of Bavaria from Rosalba (1704)", "work", "The source describes portraits of the most beautiful women in Venice as a group; it does not name sitters or identify individual portraits.", 16),
    ("frederick_pastels", "Twelve pastel portraits commissioned by Frederick IV of Denmark from Rosalba Carriera (1709)", "work", "The source gives a count, medium, artist, patron, and year but no titles or sitter names; printed footnote 1 remains to be processed from the canonical note block.", 18),
    ("regatta_picture", "Unidentified Luca Carlevarijs painting of the regatta offered in honour of Frederick IV of Denmark (1709)", "work", "The source says Carlevarijs painted the regatta for Frederick. It does not say Frederick commissioned the picture. Printed footnote 2, including its location locator, remains pending.", 18),
    ("crozat_house", "Unidentified Paris house of Pierre Crozat described as a centre for young artists (p.277)", "place", "Haskell refers to Crozat's house in Paris and characterizes it as a centre for young artists. The building is not named or independently identified here.", 22),
    ("watteau_painting", "Unidentified painting by Watteau promised by Pierre Crozat to Rosalba Carriera in exchange for her work", "work", "Haskell reports a promise of exchange, not its completion. The painting has no title or other identification in this passage; printed footnote 4 remains pending.", 22),
    ("courtesans", "Venetian courtesans as a group in Haskell's p.277 description", "term", "A collective social category in Haskell's characterization of Venice; no individual courtesan is named.", 21),
    ("foreign_visitors", "English, French, and German visitors to Venice who admired Rosalba's work (unnamed collective, p.277)", "term", "Haskell's unnamed visitor groups are described collectively; the passage does not identify individuals or establish that every visitor shared the opinion.", 23),
    ("ambassadors", "English, French, and German ambassadors who might employ Venetian-entry painters (unnamed collective, p.277)", "term", "A possible collective patron group in Haskell's modal statement. Preserve 'might'; this is not evidence of a specific commission or formal organization.", 23),
    ("augustus_collection", "Collection of Rosalba Carriera's work amassed by Augustus III in Dresden (type unresolved, p.277)", "", "Haskell identifies a large collection of Rosalba's work amassed by Augustus III in Dresden. The project taxonomy has no collection type; leave the type pending rather than forcing it into archive, place, or work.", 19),
]

new_candidates = []
C = {}
for offset, (key, name, kind, detail, source_line) in enumerate(CANDIDATE_SPECS, 1):
    candidate_id = f"cand-{MAX_CANDIDATE + offset:04d}"
    if candidate_id in candidate_ids or any(row["canonical_name"] == name and row["suggested_type"] == kind for row in candidates):
        raise SystemExit(f"candidate ID/natural key exists: {candidate_id} {name}")
    C[key] = candidate_id
    new_candidates.append({
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
        "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L{source_line}",
    })


def e(key):
    return E[key]


def c(key):
    return C[key]


line_offsets = {}
offset = 0
for line_no in range(segment_meta["line_start"], segment_meta["line_end"] + 1):
    line_offsets[line_no] = offset
    offset += len(source_lines[line_no - 1]) + 1

new_mentions = []


def add_mention(local_id, line_no, surface, candidate_id, note, occurrence=0):
    mention_id = f"m-chp10-p277-{local_id}"
    if mention_id in mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids and candidate_id not in {row["candidate_id"] for row in new_candidates}:
        raise SystemExit(f"mention references missing candidate: {mention_id} -> {candidate_id}")
    line = source_lines[line_no - 1]
    positions, start = [], 0
    while True:
        at = line.find(surface, start)
        if at < 0:
            break
        positions.append(at)
        start = at + 1
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent at L{line_no}: {surface!r}")
    start_char = line_offsets[line_no] + positions[occurrence]
    end_char = start_char + len(surface)
    if segment_text[start_char:end_char] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": SEGMENT, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start_char), "end_char": str(end_char), "note": note,
    })


MENTION_SPECS = [
    ("german_princes", 16, "German princes", "german_princes", "Collective framing for the named and indexed German patrons on this page.", 0),
    ("maximilian", 16, "Maximilian of Bavaria", "maximilian", "Reuse the p.277 index candidate for Maximilian, Prince, Elector of Bavaria.", 0),
    ("max_him", 16, "him", "maximilian", "Pronoun refers to Maximilian in the clause about the disasters of 1704.", 0),
    ("rosalba_max", 16, "Rosalba", "carriera", "Artist named as recipient of Maximilian's portrait commissions.", 0),
    ("max_portrait", 16, "his portrait", "max_portrait", "One unidentified portrait in the 1704 commission.", 0),
    ("max_women_portraits", 16, "those of the most beautiful women in Venice", "max_women_portraits", "Unidentified portrait subjects described as a group; Venice is separately marked as a city.", 0),
    ("venice_women", 16, "Venice", "venice", "City named as the location of the portrait sitters.", 0),
    ("max_he_followed", 16, "He", "maximilian", "Pronoun refers to Maximilian before the following patrons are named.", 0),
    ("christian_louis", 16, "Duke Christian Louis", "christian_louis", "Person named in the p.277 index; the source line breaks before 'Mecklenburg'.", 0),
    ("christian_mecklenburg", 17, "Mecklenburg", "christian_louis", "Continuation of Duke Christian Louis's name across the OCR line break.", 0),
    ("palatine_elector", 17, "the Elector Palatinate", "elector_pal", "The body gives the title only; the p.277 index candidate names Johann Wilhelm. Retain that crosswalk as provisional for global S3 review.", 0),
    ("germany", 18, "Germany", "germany", "Destination named in the invitations; no individual court is specified.", 0),
    ("frederick", 18, "Frederick IV of Denmark", "frederick", "Reuse the p.277 index candidate.", 0),
    ("sweden", 18, "Sweden", "sweden", "Country named in the account of Frederick's war.", 0),
    ("venice_visit", 18, "Venice", "venice", "City visited by Frederick IV in 1709.", 0),
    ("frederick_he", 18, "he too", "frederick", "Pronoun refers to Frederick IV after the report about his impression of Venetian women.", 0),
    ("venetian_women", 18, "Venetian women", "frederick_pastels", "Subjects of the twelve pastels are described collectively; individual sitters remain unidentified.", 0),
    ("rosalba_frederick", 18, "Rosalba", "carriera", "Artist commissioned to record the sitters' beauty.", 0),
    ("twelve_pastels", 18, "twelve pastels", "frederick_pastels", "Work group specified by count and medium; footnote 1 remains pending.", 0),
    ("carlevarijs_regatta", 18, "Luca Carlevarijs", "carlevarijs_regatta_index", "Use the page-277n index candidate associated with the regatta entry.", 0),
    ("regatta", 18, "the regatta", "regatta_picture", "Unidentified picture painted by Carlevarijs; do not convert 'painted for him' into a commission by Frederick.", 0),
    ("frederick_honour", 18, "his honour", "frederick", "Pronoun refers to Frederick IV.", 0),
    ("saxon_elector", 19, "the Prince Elector of Saxony", "augustus", "The following clause explicitly says he was later Augustus III of Poland.", 0),
    ("augustus", 19, "Augustus III of Poland", "augustus", "Source explicitly equates the Prince Elector of Saxony with the later Augustus III of Poland.", 0),
    ("venice_augustus", 19, "Venice", "venice", "City visited by Augustus III three times.", 0),
    ("rosalba_art", 19, "Rosalba’s art", "carriera", "Artist whose work is described as admired by Augustus III.", 0),
    ("collection_her_work", 19, "her work", "carriera", "Pronoun refers to Rosalba Carriera; the collection itself is not assigned a type here.", 0),
    ("dresden", 19, "Dresden", "dresden", "City where Haskell says Augustus III amassed the collection.", 0),
    ("collection_object", 19, "huge collection of her work", "augustus_collection", "Source-level art collection; leave its taxonomy type unresolved.", 0),
    ("venice_republic_city", 20, "Venice", "venice", "The passage shifts between personified Venice, the Republic, its inhabitants, and the city; keep those roles distinct.", 0),
    ("republic", 20, "Republic", "republic", "Political entity in the phrase about preserving former status; distinct from Venice as a city.", 0),
    ("venetian_nobles", 20, "nobles", "nobility", "Haskell rejects a stereotype about inhabitants as haughty nobles; this is not a claim about every noble.", 0),
    ("venice_city_haven", 20, "city", "venice", "Venice is explicitly recast as a city in the next clause.", 0),
    ("venice_europe_comparison", 20, "Europe", "europe", "Geographic comparison for the palaces' contents.", 0),
    ("courtesans", 21, "courtesans", "courtesans", "Unnamed social group in Haskell's description; no individual is identified.", 0),
    ("collectors_them", 21, "they", "german_princes", "Collective reference to the visiting men discussed above and others like them; the set is broader than the named German princes.", 0),
    ("venice_wished_recorded", 21, "city", "venice", "The city is one of the subjects the northern visitors wanted recorded.", 0),
    ("north_kingdoms", 21, "kingdoms in the North", "europe", "Unspecified northern kingdoms; this mention does not identify a particular state.", 0),
    ("europe_french", 22, "Europe", "europe", "Peace in Europe is the chronological frame in Haskell's transition to French collectors.", 0),
    ("french_collectors", 22, "the French", "france", "Collective national label in Haskell's account; no individual other than Crozat is specified.", 0),
    ("crozat", 22, "Pierre Crozat", "crozat", "French banker and collector named by Haskell.", 0),
    ("crozat_house", 22, "house in Paris", "crozat_house", "Unidentified physical residence associated with Crozat; building identity remains open.", 0),
    ("paris_house", 22, "Paris", "paris", "City where Crozat's house is located.", 0),
    ("versailles", 22, "Versailles", "versailles", "Used as a comparison for the house's cultural role; do not infer a literal transfer of institutions.", 0),
    ("rosalba_pastels", 22, "Rosalba’s pastels", "carriera", "Pastel works viewed by Crozat; no individual work is identified here.", 0),
    ("crozat_he_saw", 22, "he saw", "crozat", "Pronoun refers to Crozat during his 1715 visit.", 0),
    ("crozat_he_found", 22, "he found", "crozat", "Pronoun refers to Crozat's response to the pastels.", 0),
    ("crozat_rosalba_letter", 22, "he wrote to her", "crozat", "He is Crozat; 'her' refers to Rosalba. The letter is reported by Haskell, not independently consulted.", 0),
    ("rosalba_her", 22, "her work", "carriera", "Pronoun refers to Rosalba Carriera.", 0),
    ("watteau", 22, "Watteau", "watteau", "Artist whose painting Crozat promised; reuse p.277 index candidate.", 0),
    ("watteau_painting", 22, "a painting by Watteau", "watteau_painting", "Unidentified painting promised in exchange; promise does not prove delivery.", 0),
    ("crozat_artist", 22, "this artist", "watteau", "Pronoun phrase refers to Watteau, whom Crozat reportedly met in France.", 0),
    ("france_return", 22, "France", "france", "Place of Crozat's return from meeting Watteau.", 0),
    ("rosalba_you", 22, "you", "carriera", "Addressed to Rosalba in Haskell's report of Crozat's letter.", 0),
    ("crozat_visit_him", 22, "him", "crozat", "Pronoun refers to Crozat, whom Rosalba was persuaded to visit.", 0),
    ("paris_visit", 22, "Paris", "paris", "City Crozat persuaded Rosalba to visit in 1721.", 1),
    ("rosalba_foreigners", 22, "Rosalba", "carriera", "Artist described as working mainly for foreigners before the 1721 visit.", 0),
    ("english_visitors", 23, "English", "england", "National adjective modifying unnamed visitors.", 0),
    ("french_visitors", 23, "French", "france", "National adjective modifying unnamed visitors.", 0),
    ("german_visitors", 23, "German", "germany", "National adjective modifying unnamed visitors.", 0),
    ("visitors", 23, "visitors", "foreign_visitors", "Unnamed visitor groups described collectively by Haskell.", 0),
    ("carriera_visitors", 23, "her work", "carriera", "Pronoun refers to Rosalba's art.", 0),
    ("ambassadors", 23, "ambassadors", "ambassadors", "Unnamed possible patrons from the three named nations.", 0),
    ("carlevarijs_entries", 23, "Carlevarijs", "carlevarijs", "Artist in the modal statement about recording ambassadors' entries; footnote 5 remains pending.", 0),
    ("canaletto", 24, "Canaletto", "canaletto", "Artist in the modal statement; use the p.277n index candidate. Footnote 5's individual works remain pending.", 0),
    ("venice_entries", 24, "Venice", "venice", "Destination of the entries the painters might record.", 0),
]
for local_id, line_no, surface, key, note, occurrence in MENTION_SPECS:
    candidate_id = C[key] if key in C else E[key]
    add_mention(local_id, line_no, surface, candidate_id, note, occurrence)

new_statements = []


def quote_between(first: str, last: str):
    start = segment_text.find(first)
    if start < 0:
        raise SystemExit(f"quote start absent: {first!r}")
    end_start = segment_text.find(last, start)
    if end_start < 0:
        raise SystemExit(f"quote end absent after {first!r}: {last!r}")
    return segment_text[start : end_start + len(last)]


def add_statement(sid, line_start, line_end, subject, obj, predicate, quote, claim, qualification,
                  refs=(), relation=False, footnote=None, cross=(), text_layer="authorial narrative", ocr=()):
    if sid in statement_ids or any(row["statement_id"] == sid for row in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    if quote not in segment_text:
        raise SystemExit(f"quote not anchored in source segment: {sid}")
    linked = set(refs) | {value for value in (subject, obj) if value}
    known = candidate_ids | {row["candidate_id"] for row in new_candidates}
    if not linked <= known:
        raise SystemExit(f"unknown candidate in {sid}: {sorted(linked - known)}")
    qualifiers = {
        "source_line_start": line_start, "source_line_end": line_end, "printed_page": 277,
        "pdf_physical_page": 2, "claim": claim, "speaker": "Haskell", "text_layer": text_layer,
        "qualification": qualification, "mentioned_candidate_ids": sorted(linked),
    }
    if relation:
        qualifiers["relation_candidate"] = True
    if footnote is not None:
        qualifiers.update({"footnote_marker": footnote, "footnote_text_pending": True,
                           "footnote_link_status": "pending_source_migration"})
    if cross:
        qualifiers["cross_reference_segments"] = [
            {"segment_id": NEXT, "source_line_start": start, "source_line_end": end}
            for start, end in cross
        ]
    if ocr:
        qualifiers["ocr_corrections"] = [
            {"source_file": SOURCE_FILE, "source_line": line_no, "ocr": raw, "print": printed,
             "basis": "CHP-10.pdf physical page 2."}
            for line_no, raw, printed in ocr
        ]
    new_statements.append({
        "statement_id": sid, "segment_id": SEGMENT, "subject_candidate_id": subject,
        "object_candidate_id": obj, "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote, "source_file": SOURCE_FILE, "origin": "book",
    })


add_statement("st-chp10-p277-maximilian-carriera-portrait-commissions", 16, 16, e("maximilian"), e("carriera"),
              "maximilian_commissioned_his_portrait_and_portraits_of_venetian_women_from_rosalba_in_1704",
              quote_between("And the German princes came in force:", "women in Venice."),
              "Haskell says Maximilian of Bavaria commissioned Rosalba in 1704 to paint his portrait and portraits of women in Venice.",
              "The print calls Maximilian 'of Bavaria'; the index supplies the fuller princely title. The women and individual portraits are unnamed. The nearby printed period/hyphen in 'not-an.' is retained as printed, not silently normalized.",
              [c("german_princes"), c("max_portrait"), c("max_women_portraits"), e("venice")], True)
add_statement("st-chp10-p277-christian-louis-rosalba-commissions", 16, 18, e("christian_louis"), e("carriera"),
              "christian_louis_made_similar_commissions_and_invited_rosalba_to_germany",
              quote_between("He was followed by Duke Christian Louis of", "Germany."),
              "Haskell says Duke Christian Louis of Mecklenburg followed Maximilian with similar commissions and invitations to Germany.",
              "The sentence applies the plural 'similar commissions and invitations' to Christian Louis and the following Palatine Elector; it does not specify the number or title of works.",
              [e("germany"), c("german_princes")], True)
add_statement("st-chp10-p277-elector-pal-rosalba-commissions", 17, 18, e("elector_pal"), e("carriera"),
              "elector_pal_followed_with_similar_commissions_and_invitations_to_germany",
              quote_between("and the Elector Palatinate with similar commissions", "Germany."),
              "Haskell says the Elector Palatinate followed with similar commissions and invitations to Germany.",
              "The body gives only the title. The index identifies Johann Wilhelm at p.277; preserve this as an index crosswalk, not a resolved external identity, for S3.",
              [e("germany"), c("german_princes")], True)
add_statement("st-chp10-p277-frederick-holiday-visit", 18, 18, e("frederick"), e("venice"),
              "frederick_iv_took_a_holiday_in_venice_during_his_war_with_sweden_in_1709",
              quote_between("In 1709 Frederick IV of Denmark", "lavishly entertained"),
              "Haskell says Frederick IV of Denmark took a holiday in Venice in 1709 during his war with Sweden and was lavishly entertained.",
              "This is Haskell's narrative; the passage names no host or specific entertainment. Preserve the stated conflict without identifying its course or participants beyond Frederick and Sweden.",
              [e("sweden")], True)
add_statement("st-chp10-p277-frederick-carriera-pastels", 18, 18, e("frederick"), c("frederick_pastels"),
              "frederick_iv_commissioned_twelve_pastels_from_rosalba_in_1709",
              quote_between("so impressed by Venetian women", "twelve pastels,1"),
              "Haskell says Frederick was so impressed by Venetian women that he commissioned Rosalba to record their beauty in twelve pastels.",
              "Printed footnote 1 is a locator/source trail and remains pending in the canonical note segment; the individual sitters and pastel titles are not named.",
              [e("carriera"), c("frederick_pastels")], True, 1)
add_statement("st-chp10-p277-carlevarijs-regatta", 18, 18, e("carlevarijs_regatta_index"), c("regatta_picture"),
              "carlevarijs_painted_the_regatta_offered_in_fredericks_honour",
              quote_between("while Luca Carlevarijs painted", "his honour.2"),
              "Haskell says Luca Carlevarijs painted for Frederick the regatta offered in his honour.",
              "Do not infer that Frederick commissioned the painting: the sentence says it was painted for him after the regatta was offered in his honour. Printed footnote 2 remains pending; its location locator will be assessed with the note segment.",
              [e("frederick")], True, 2)
add_statement("st-chp10-p277-augustus-venice-visits", 19, 19, e("augustus"), e("venice"),
              "augustus_iii_visited_venice_three_times_in_the_first_two_decades_of_the_eighteenth_century",
              quote_between("Above all there was the Prince Elector of Saxony", "eighteenth century"),
              "Haskell says the Prince Elector of Saxony, later Augustus III of Poland, visited Venice three times during the first two decades of the eighteenth century.",
              "The source explicitly equates the two titles. Preserve the approximate period as phrased; do not invent exact visit years.",
              [c("german_princes")], True)
add_statement("st-chp10-p277-augustus-rosalba-collection", 19, 19, e("augustus"), c("augustus_collection"),
              "augustus_amassed_a_huge_dresden_collection_of_rosalbas_work",
              quote_between("whose admiration for Rosalba’s art", "amass in Dresden.3"),
              "Haskell says Augustus's admiration for Rosalba's art was limitless and points to the huge collection of her work he amassed in Dresden as testimony.",
              "The size and admiration are Haskell's characterization. The collection is a substantive object but 'collection' has no defined KU type; keep its candidate type blank pending taxonomy review. Printed footnote 3 remains pending.",
              [e("carriera"), e("dresden"), c("augustus_collection")], True, 3)
add_statement("st-chp10-p277-republic-not-impoverished", 20, 20, e("republic"), None,
              "haskell_rejects_the_view_that_venice_was_an_impoverished_republic_desperately_preserving_former_status",
              quote_between("For these men and others like them Venice was", "her former status in the world;"),
              "Haskell rejects a description of Venice as an impoverished Republic desperately trying to maintain its former status.",
              "The scan appears to print the unusual string 'not-an. impoverished'; retain that source reading and interpret the syntax as a denial, not a claim that the Republic was impoverished. Political status belongs to the Republic candidate; keep it distinct from the city candidate.",
              [e("venice"), c("german_princes")])
add_statement("st-chp10-p277-venetian-inhabitants-stereotype", 20, 20, None, None,
              "haskell_rejects_a_stereotype_of_venetian_inhabitants_as_haughty_nobles",
              quote_between("her inhabitants were not haughty nobles", "threatened to swamp them."),
              "Haskell says Venice's inhabitants were not haughty nobles asserting aristocratic claims against upstarts.",
              "This is the author's rejection of a stereotype, not a claim that Venice had no nobles or that all inhabitants shared one disposition.",
              [e("venice"), e("nobility"), c("german_princes")])
add_statement("st-chp10-p277-venice-peaceful-government", 20, 20, e("venice"), e("republic"),
              "venice_described_as_a_rich_peaceful_haven_whose_government_encouraged_entertainment_to_gain_friends",
              quote_between("Rather, she was a haven of peace", "win as many friends as possible;"),
              "Haskell presents Venice as peaceful and very rich, with a government encouraging visitors' entertainment to win friends.",
              "Authorial characterization. The passage personifies Venice and shifts between city and government; preserve the city/place and Republic/institution candidates separately.",
              [c("german_princes")], True)
add_statement("st-chp10-p277-venetian-palaces-art", 20, 21, e("venice"), None,
              "haskell_says_venices_palaces_were_filled_with_sensuous_masterpieces",
              quote_between("a city whose palaces were filled", "sensuous beauty"),
              "Haskell says Venice's palaces contained masterpieces of sensuous beauty, as nowhere else in Europe.",
              "Aesthetic and comparative authorial characterization; no particular palace or artwork is identified.",
              [e("europe")], ocr=[(21, "’ easily appreciated", "easily appreciated")])
add_statement("st-chp10-p277-courtesans-reputation", 21, 21, None, c("courtesans"),
              "venetian_courtesans_were_renowned_for_their_charms_in_haskells_account",
              quote_between("whose courtesans were renowned", "their charms."),
              "Haskell says Venice's courtesans were renowned for their charms.",
              "Authorial generalization about an unnamed social group; no individual courtesan is identified.")
add_statement("st-chp10-p277-northern-visitors-wanted-records", 21, 21, None, None,
              "northern_visitors_wanted_the_city_and_its_women_recorded_to_take_home",
              quote_between("It is hardly surprising that they wished", "in the North."),
              "Haskell says the visitors wanted both the city and its women recorded so they could take those images back to their northern kingdoms.",
              "The pronoun 'they' refers to the visitors discussed above and others like them; the source does not assign this wish to every named ruler individually. Preserve 'kingdoms in the North' as an unspecified group.",
              [e("venice"), c("max_women_portraits"), c("german_princes")], True)
add_statement("st-chp10-p277-french-collector-crozat", 22, 22, None, e("crozat"),
              "crozat_symbolized_a_new_type_of_french_collector_after_peace_in_europe",
              quote_between("With peace in Europe came the French", "by Pierre Crozat,"),
              "Haskell presents Pierre Crozat as emblematic of a new type of French collector emerging with peace in Europe.",
              "Typological authorial framing; Crozat is the named example, not proof that all French collectors had the same profile.",
              [e("europe"), e("france")])
add_statement("st-chp10-p277-crozat-house-versailles", 22, 22, e("crozat"), c("crozat_house"),
              "crozats_paris_house_had_replaced_versailles_as_a_centre_for_young_artists",
              quote_between("the fabulously rich banker whose house in Paris", "young artists."),
              "Haskell says Crozat was a fabulously rich banker whose Paris house had already replaced Versailles as a centre for young artists.",
              "This is Haskell's account of the house's cultural role. The building is unidentified; 'replaced Versailles' is a comparison of cultural functions, not a claim that the Palace of Versailles moved or closed.",
              [e("paris"), e("versailles")], True)
add_statement("st-chp10-p277-crozat-visited-carriera-pastels", 22, 22, e("crozat"), e("carriera"),
              "crozat_saw_rosalbas_pastels_in_venice_in_1715_and_found_them_suited_to_his_search",
              quote_between("In Rosalba’s pastels which he saw during his visit of 1715", "what he was looking for;"),
              "Haskell says Crozat saw Rosalba's pastels during a 1715 visit and found them exactly what he was looking for.",
              "The passage does not identify individual pastels or say that Crozat acquired them at that time. 'Exactly what he was looking for' is Haskell's characterization.",
              [e("paris")], True)
add_statement("st-chp10-p277-crozat-promised-watteau-exchange", 22, 22, e("crozat"), c("watteau_painting"),
              "crozat_promised_rosalba_a_watteau_painting_in_exchange_for_her_work",
              quote_between("he wrote to her later and promised her a painting by Watteau", "in exchange for her work,"),
              "Haskell says Crozat later wrote to Rosalba and promised a Watteau painting in exchange for her work.",
              "This records a promise, not a completed transfer. The promised painting is unidentified. Printed footnote 4 remains pending in the canonical note segment.",
              [e("watteau"), e("carriera")], True, 4)
add_statement("st-chp10-p277-crozat-description-of-watteau", 22, 22, e("crozat"), e("watteau"),
              "crozat_reportedly_described_watteau_as_the_only_artist_able_to_make_something_worthy_of_rosalba",
              quote_between("as this artist whom he met on his return to France", "worthy of you’"),
              "Haskell reports Crozat's explanation that Watteau, whom he met on returning to France, was the only man able to produce something worthy of Rosalba.",
              "Nested quotation as transmitted by Haskell; do not attribute the compliment to Watteau himself or claim the letter has been consulted.",
              [e("france"), e("carriera")], False, 4, text_layer="nested letter quotation reported by Haskell")
add_statement("st-chp10-p277-crozat-persuaded-carriera-paris", 22, 22, e("crozat"), e("carriera"),
              "crozat_persuaded_rosalba_to_visit_him_in_paris_in_1721",
              quote_between("and he was not satisfied until in 1721", "visit him in Paris.4"),
              "Haskell says Crozat was not satisfied until he persuaded Rosalba to visit him in Paris in 1721.",
              "Printed footnote 4 remains pending; retain the stated persuasion and date without inferring the details of the visit.",
              [e("paris")], True, 4)
add_statement("st-chp10-p277-carriera-foreign-work", 22, 22, e("carriera"), None,
              "rosalba_had_been_working_mainly_for_foreigners_before_the_1721_visit",
              quote_between("But for years before this visit", "mainly for foreigners."),
              "Haskell says Rosalba had already been working mainly for foreigners for years before the 1721 visit to Crozat.",
              "Broad authorial summary; the passage gives no proportion, exhaustive client list, or exact start date.",
              [e("crozat"), c("foreign_visitors")])
add_statement("st-chp10-p277-visitors-agree-carriera-merits", 23, 23, c("foreign_visitors"), e("carriera"),
              "english_french_and_german_visitors_agreed_about_the_merits_of_rosalbas_work",
              quote_between("English, French and German visitors", "the merits of her work,"),
              "Haskell says English, French, and German visitors could agree enthusiastically about the merits of Rosalba's work.",
              "The collective statement does not establish that every visitor held this view.",
              [e("england"), e("france"), e("germany")])
add_statement("st-chp10-p277-ambassadors-carlevarijs-entry-pictures", 23, 24, c("ambassadors"), e("carlevarijs"),
              "ambassadors_might_employ_carlevarijs_to_record_their_entries_into_venice",
              quote_between("and ambassadors from all these nations might employ Carlevarijs", "their entries into Venice,5"),
              "Haskell says ambassadors from England, France, and Germany might employ Carlevarijs to record their entries into Venice.",
              "Preserve the modal 'might'; no named ambassador or specific commission is asserted here. Printed footnote 5's examples remain pending. The following 'but for other and more important' contrast continues on p.278.",
              [e("england"), e("france"), e("germany"), e("venice")], True, 5, [(27, 27)])
add_statement("st-chp10-p277-ambassadors-canaletto-entry-pictures", 23, 24, c("ambassadors"), e("canaletto"),
              "ambassadors_might_employ_canaletto_to_record_their_entries_into_venice",
              quote_between("and ambassadors from all these nations might employ Carlevarijs", "their entries into Venice,5"),
              "Haskell says ambassadors might later employ Canaletto to record their entries into Venice.",
              "Preserve 'later' and 'might'; no named ambassador or specific commission is asserted in the body. Printed footnote 5's examples remain pending. The sentence's contrasting clause continues on p.278.",
              [e("england"), e("france"), e("germany"), e("venice")], True, 5, [(27, 27)])
add_statement("st-chp10-p277-incomplete-commission-contrast", 24, 24, None, None,
              "unfinished_contrast_about_other_and_more_important_commissions",
              "but for other and more important",
              "The p.277 sentence begins a contrast about other, more important commissions, but its content is incomplete in this segment.",
              "Do not infer the nature of the divergence until the next source segment is processed.",
              cross=[(27, 27)], text_layer="unfinished source clause")

coverage_by_id[SEGMENT].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L15-24",
    "note": "Printed p.277 body read against CHP-10.pdf physical page 2. Processed the German-prince commissions, Frederick IV's visit/pastels and Carlevarijs regatta, Augustus III's visits/collection, Haskell's Venice characterization, Crozat's collecting and Rosalba exchange, and the modal ambassador-painter account. L24's contrast ('but for other and more important') continues at p.278 L27; linked as partial pending the next segment. Printed notes 1-5 are consolidated at canonical L495-499 and remain pending. Scan confirms the unusual 'not-an.' punctuation is printed; preserve it. Remove the stray OCR apostrophe before 'easily' at L21 in S2 reading only; S0 remains unchanged. The Palatine title is linked to the p.277 index candidate Johann Wilhelm with identity judgment deferred to S3; Venice city and Republic remain distinct."
})

if len({row["candidate_id"] for row in candidates + new_candidates}) != len(candidates) + len(new_candidates):
    raise SystemExit("duplicate candidate ID")
if len({row["mention_id"] for row in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("duplicate mention ID")
if len({row["statement_id"] for row in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("duplicate statement ID")

summary = {
    "segment": SEGMENT, "next": NEXT, "status": "reviewed/partial",
    "new_candidates": len(new_candidates), "candidate_ids": [row["candidate_id"] for row in new_candidates],
    "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "notes_pending": "printed footnotes 1-5 are in canonical L495-499",
    "cross_page": "L24 incomplete contrast continues at p.278 L27",
    "counts_after": {
        "candidates": len(candidates) + len(new_candidates),
        "mentions": len(mentions) + len(new_mentions),
        "statements": len(statements) + len(new_statements), "coverage_rows": len(coverage),
    },
}
print(json.dumps(summary, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
if args.apply:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("recovery backup already exists; inspect before retrying")
    for source, backup in zip(paths, backups):
        shutil.copy2(source, backup)
    try:
        write_csv_atomic(candidate_path, candidate_fields, candidates + new_candidates)
        write_csv_atomic(mention_path, mention_fields, mentions + new_mentions)
        write_jsonl_atomic(statement_path, statements + new_statements)
        write_csv_atomic(coverage_path, coverage_fields, coverage)
    except Exception:
        for target, backup in zip(paths, backups):
            shutil.copy2(backup, target)
        raise
    print("APPLIED; recovery backups retained: " + ", ".join(path.name for path in backups))
else:
    print("DRY RUN: no S2 table rows written")
