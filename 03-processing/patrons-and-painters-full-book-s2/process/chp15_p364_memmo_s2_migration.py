"""Controlled S2 migration for Andrea Memmo's opening paragraph on printed p.364."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-15.pdf"
SOURCE_SHA = "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f"
PDF_SHA = "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885"
SOURCE_FILE = "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
BODY = "chp-15:15_CHP-15_sec_ii:l3-4"
BODY_NEXT = "chp-15:15_CHP-15_sec_ii:l6-12"
NOTES = "chp-15:15_CHP-15_sec_i:l43-56"
BACKUP_SUFFIX = ".bak-s2-chp15-p364-memmo-apply-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.364 Andrea Memmo S2 migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(handle.name)
    temp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(handle.name)
    temp.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("chapter 15 sec_ii source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-15 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
note_lines = (ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_i.md").read_text(encoding="utf-8-sig").splitlines()
for line_number, required in [
    (4, "Andrea Memmo, whom we have already encountered in another capacity,3"),
    (4, "in whose library, as he later declared, he first learnt to appreciate ‘chaste’ architecture.6"),
    (4, "the main influence on his life was that of Carlo Lodoli"),
    (4, "increasingly to French culture and ideas for his intellectual formation.6"),
    (4, "thé many pleasures that were open to the aristocracy"),
    (4, "the ubiquitous Giustiniana Wynne, then being wooed by Consul Smith, and he"),
]:
    if required not in source_lines[line_number - 1]:
        raise SystemExit(f"required source text changed at L{line_number}")
for line_number, required in [
    (53, "3 See Chapter 12."),
    (54, "P. Molmenti"),
    (55, "5 See Chapter 11."),
    (56, "Tabacco, pp. 32 if."),
]:
    if required not in note_lines[line_number - 1]:
        raise SystemExit(f"required note text changed at L{line_number}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}

for segment_id in (BODY, BODY_NEXT, NOTES):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing S2 coverage row: {segment_id}")
if (
    coverage_by_id[BODY]["migration_status"] != "pending"
    or coverage_by_id[BODY_NEXT]["migration_status"] != "pending"
    or coverage_by_id[NOTES]["migration_status"] != "partial"
    or coverage_by_id[NOTES]["source_line_ranges"] != "L44-52"
):
    raise SystemExit("S2 coverage preconditions changed")
if max(int(cid.split("-")[1]) for cid in candidate_by_id) != 10467:
    raise SystemExit("candidate sequence changed; expected max cand-10467")
for cid in ("cand-1642", "cand-1643", "cand-1648", "cand-1411", "cand-2440", "cand-2824", "cand-0591", "cand-9714", "cand-2644", "cand-10467"):
    if cid not in candidate_by_id:
        raise SystemExit(f"required existing candidate missing: {cid}")

new_candidates = [
    ("cand-10468", "‘Chaste’ architecture as appreciated by Andrea Memmo in Consul Smith’s library (p.364)", "term", BODY, 4,
     "The phrase is quoted in Haskell’s account of Memmo’s later declaration. Its meaning is not defined here and is not equated with Lodoli’s separately indexed architectural positions."),
    ("cand-10469", "Political reform as an object of Andrea Memmo’s enthusiasm (p.364)", "term", BODY, 4,
     "A concept named in Haskell’s account of Memmo. The passage gives no particular reform proposal in this paragraph."),
    ("cand-10470", "French culture and ideas in Andrea Memmo’s intellectual formation (p.364)", "term", BODY, 4,
     "A source-specific concept in Haskell’s account. It is not treated as a single movement, institution or program."),
    ("cand-10471", "Unidentified Consul Smith library where Andrea Memmo learned about ‘chaste’ architecture (p.364)", "place", BODY, 4,
     "The passage identifies the library through Consul Smith but gives no location or physical description. It may be the library candidate cand-9714; cross-chapter identity is reserved for S3."),
    ("cand-10472", "Unidentified great patrician family of Andrea Memmo (p.364)", "family", BODY, 4,
     "Haskell says Memmo was born into one of the great patrician families but does not name the lineage. Do not infer the family from his surname."),
    ("cand-10473", "Venetian aristocracy and fellow nobles in Haskell’s account of Andrea Memmo (p.364)", "term", BODY, 4,
     "An unnamed social group in this passage. Do not equate it with the older aristocracy candidate cand-8137 or the new mercantile entrants cand-8179."),
    ("cand-10474", "P. Molmenti, author cited for Andrea Memmo’s biography (p.364 note 4)", "person", NOTES, 54,
     "Only the initials and surname are supplied in the note; no full name is inferred."),
    ("cand-10475", "P. Molmenti, ‘Un nobil huomo veneziano del secolo XVIII’, n.d. (p.364 note 4 citation locator)", "archive", NOTES, 54,
     "Citation as printed in Haskell’s note, offered for a brief general biography of Andrea Memmo. Publication details and source text were not independently checked."),
    ("cand-10476", "Torcellan, 1963, biographical source on Andrea Memmo (p.364 note 4 citation locator)", "archive", NOTES, 54,
     "Haskell calls this the principal biography but gives no title here. The cited work was not independently consulted; author mention can be compared with index candidate cand-2644 at S3."),
    ("cand-10477", "Tabacco, pp.32 ff. (p.364 note 6 citation locator; work unspecified)", "archive", NOTES, 56,
     "Short-form citation only; exact title, edition and cited pages were not independently checked. Keep separate from the different Tabacco locators already in the candidate table."),
]
for cid, name, suggested_type, segment_id, source_line, detail in new_candidates:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    row = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": suggested_type, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{segment_id}#L{source_line}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row

segment_bounds = {BODY: (3, 4), NOTES: (43, 56)}
segment_lines = {
    BODY: {number: source_lines[number - 1] for number in range(3, 5)},
    NOTES: {number: note_lines[number - 1] for number in range(43, 57)},
}
segment_offsets = {}
for sid, (first, last) in segment_bounds.items():
    offset = 0
    segment_offsets[sid] = {}
    for number in range(first, last + 1):
        segment_offsets[sid][number] = offset
        offset += len(segment_lines[sid][number]) + 1

planned_mentions = []
mention_counter = 1


def add_mention(segment_id, candidate_id, surface, source_line, note=""):
    global mention_counter
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"mention candidate missing: {candidate_id}")
    line = segment_lines[segment_id][source_line]
    line_offset = segment_offsets[segment_id][source_line]
    occupied = [
        (int(row["start_char"]), int(row["end_char"]))
        for row in mentions + planned_mentions
        if row["segment_id"] == segment_id and line_offset <= int(row["start_char"]) < line_offset + len(line)
    ]
    search_from = 0
    while True:
        pos = line.find(surface, search_from)
        if pos < 0:
            raise SystemExit(f"surface not found on {segment_id} L{source_line}: {surface!r}")
        start = line_offset + pos
        end = start + len(surface)
        if not any(start < old_end and old_start < end for old_start, old_end in occupied):
            break
        search_from = pos + 1
    mention_id = f"m-chp15-p364-memmo-{mention_counter:04d}"
    if any(row["mention_id"] == mention_id for row in mentions + planned_mentions):
        raise SystemExit(f"mention ID already exists: {mention_id}")
    planned_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id,
        "candidate_id": candidate_id, "surface_form": surface,
        "start_char": str(start), "end_char": str(end), "note": note,
    })
    mention_counter += 1


def quote(segment_id, line_start, line_end):
    first, last = segment_bounds[segment_id]
    if not first <= line_start <= line_end <= last:
        raise SystemExit(f"quote span outside segment {segment_id}: L{line_start}-{line_end}")
    return "\n".join(segment_lines[segment_id][n] for n in range(line_start, line_end + 1))


def footnote(marker, note_line, body_line, statement_ids):
    return {
        "footnote_marker": str(marker), "footnote_segment": NOTES,
        "footnote_line_range": f"L{note_line}", "footnote_text_pending": False,
        "footnote_body_link_status": "linked", "footnote_body_line_range": f"L{body_line}",
        "footnote_note_statement_ids": list(statement_ids),
    }


def add_statement(statement_id, segment_id, subject, obj, predicate, line_start, line_end,
                  claim, text_layer="authorial report", speaker="Haskell", qualification="",
                  mentioned=(), **extra):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    qualifiers = {
        "source_line_start": line_start, "source_line_end": line_end,
        "printed_page": 364, "pdf_physical_page": 4,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    qualifiers.update(extra)
    row = {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote(segment_id, line_start, line_end),
        "origin": "book", "source_file": SOURCE_FILE if segment_id == BODY else "02-sources/02-Markdown/15_CHP-15_sec_i.md",
    }
    statements.append(row)
    statement_by_id[statement_id] = row


# Exact name, relevant pronouns and source concepts in the one-column body line.
add_mention(BODY, "cand-1642", "Andrea Memmo", 4)
add_mention(BODY, "cand-10472", "one of the great patrician families", 4, "The family is left unnamed by Haskell.")
add_mention(BODY, "cand-1642", "He", 4, "Pronoun refers to Andrea Memmo.")
add_mention(BODY, "cand-2440", "Consul Smith", 4)
add_mention(BODY, "cand-10471", "whose library", 4, "Possible identity with the earlier library candidate cand-9714 is unresolved.")
add_mention(BODY, "cand-10468", "‘chaste’ architecture", 4, "The phrase is quoted; its meaning is not defined in this passage.")
add_mention(BODY, "cand-1411", "Carlo Lodoli", 4)
add_mention(BODY, "cand-1643", "Memmo", 4, "Index subentry ‘and Carlo Lodoli’; identity with main Andrea Memmo candidate cand-1642 is deferred to S3.")
add_mention(BODY, "cand-1411", "his ideas", 4, "‘His’ refers to Carlo Lodoli.")
add_mention(BODY, "cand-1411", "his master", 4, "‘His master’ refers to Lodoli in Memmo’s account.")
add_mention(BODY, "cand-1642", "he became", 4, "Pronoun refers to Andrea Memmo.")
add_mention(BODY, "cand-10473", "Venetian aristocracy", 4)
add_mention(BODY, "cand-10470", "French culture and ideas", 4)
add_mention(BODY, "cand-1648", "He showed an enthusiasm", 4, "Index subentry is ‘enthusiasm for political reform’; candidate identity alignment remains for S3.")
add_mention(BODY, "cand-10469", "political reform", 4)
add_mention(BODY, "cand-1642", "he made repeated efforts", 4, "Pronoun refers to Andrea Memmo.")
add_mention(BODY, "cand-10473", "his fellow-nobles", 4, "The people are unnamed; group scope is not expanded.")
add_mention(BODY, "cand-1642", "He also took full advantage", 4, "Pronoun refers to Andrea Memmo.")
add_mention(BODY, "cand-10473", "the aristocracy of his day", 4, "Same source-described social context; membership is not specified.")
add_mention(BODY, "cand-0591", "Casanova", 4)
add_mention(BODY, "cand-1642", "As a young man he", 4, "Pronoun refers to Andrea Memmo.")
add_mention(BODY, "cand-2824", "Giustiniana Wynne", 4)
add_mention(BODY, "cand-2440", "Consul Smith", 4, "The second occurrence concerns his courtship of Giustiniana Wynne.")
add_mention(BODY, "cand-1642", "and he", 4, "The clause continues onto printed p.365; no continuation is inferred here.")

# Citation mentions in the consolidated p.364 notes.
add_mention(NOTES, "cand-10474", "P. Molmenti", 54)
add_mention(NOTES, "cand-10475", "Un nobil huomo veneziano del secolo XVIII", 54)
add_mention(NOTES, "cand-10475", "n.d.", 54)
add_mention(NOTES, "cand-2644", "Torcellan", 54, "Author form matches an index candidate; citation work remains separately identified and unverified.")
add_mention(NOTES, "cand-10476", "1963", 54)
add_mention(NOTES, "cand-10477", "Tabacco", 56)
add_mention(NOTES, "cand-10477", "pp. 32 if.", 56, "OCR reads ‘if’; p.364 page image reads ‘ff.’.")

N3 = "st-chp15-p364-memmo-note3-chapter12-crossref"
N4M = "st-chp15-p364-memmo-note4-molmenti-biography"
N4T = "st-chp15-p364-memmo-note4-torcellan-biography"
N5 = "st-chp15-p364-memmo-note5-chapter11-crossref"
N6 = "st-chp15-p364-memmo-note6-tabacco"

add_statement(
    "st-chp15-p364-memmo-prior-capacity", BODY, "cand-1642", None,
    "previously_encountered_in_another_capacity", 4, 4,
    "Haskell refers to Andrea Memmo as someone encountered earlier in another capacity; p.364 note 3 directs the reader to Chapter 12.",
    qualification="Internal cross-reference only; the prior chapter’s context is not reinterpreted here.",
    mentioned=["cand-1642"], **footnote(3, 53, 4, [N3]))
add_statement(
    "st-chp15-p364-memmo-more-interesting-patron", BODY, "cand-1642", None,
    "described_as_a_much_more_interesting_patron", 4, 4,
    "Haskell calls Memmo a much more interesting patron.",
    qualification="This is Haskell’s assessment; the comparative context is not expanded beyond the passage.",
    mentioned=["cand-1642"])
add_statement(
    "st-chp15-p364-memmo-born-1729-patrician-family", BODY, "cand-1642", "cand-10472",
    "born_1729_into_one_of_great_patrician_families", 4, 4,
    "Haskell states that Andrea Memmo was born in 1729 into one of the great patrician families.",
    qualification="The family is not named; no specific lineage is inferred.", mentioned=["cand-1642", "cand-10472"],
    relation_candidate=True, **footnote(4, 54, 4, [N4M, N4T]))
add_statement(
    "st-chp15-p364-memmo-frequenter-of-smith", BODY, "cand-1642", "cand-2440",
    "close_frequenter_of_consul_smith_in_youth", 4, 4,
    "Haskell says Memmo was a close frequenter of Consul Smith in his younger days.",
    qualification="No exact frequency, dates or additional personal tie are specified.",
    mentioned=["cand-1642", "cand-2440"], relation_candidate=True)
add_statement(
    "st-chp15-p364-memmo-learned-chaste-architecture", BODY, "cand-1642", "cand-10468",
    "first_learned_to_appreciate_chaste_architecture_in_smith_library", 4, 4,
    "Haskell reports that Memmo later declared he first learned to appreciate ‘chaste’ architecture in Consul Smith’s library.",
    text_layer="reported self-report", speaker="Andrea Memmo, as reported by Haskell",
    qualification="The print has footnote 5 after ‘architecture’; OCR reads 6. The library candidate’s exact identity/location remains unresolved, and ‘chaste’ is not defined here.",
    mentioned=["cand-1642", "cand-2440", "cand-10471", "cand-10468"],
    **footnote(5, 55, 4, [N5]))
add_statement(
    "st-chp15-p364-memmo-lodoli-influence-and-debt", BODY, "cand-1642", "cand-1411",
    "lodoli_was_main_influence_memmo_propagated_his_ideas_and_owed_debt", 4, 4,
    "Haskell identifies Carlo Lodoli as the main influence on Memmo’s life and says Memmo propagated Lodoli’s ideas and proclaimed his debt to his master.",
    qualification="The passage does not list the ideas or establish a formal teaching arrangement beyond its use of ‘master’.",
    mentioned=["cand-1642", "cand-1643", "cand-1411"], relation_candidate=True)
add_statement(
    "st-chp15-p364-memmo-most-enlightened-member", BODY, "cand-1642", "cand-10473",
    "described_as_most_enlightened_member_of_venetian_aristocracy", 4, 4,
    "Haskell calls Memmo the most ‘enlightened’ member of the Venetian aristocracy.",
    qualification="Quotation marks and superlative are retained as Haskell’s evaluation, not treated as a formal title.",
    mentioned=["cand-1642", "cand-10473"])
add_statement(
    "st-chp15-p364-memmo-french-intellectual-formation", BODY, "cand-1642", "cand-10470",
    "increasingly_looked_to_french_culture_and_ideas_for_intellectual_formation", 4, 4,
    "Haskell says Memmo increasingly looked to French culture and ideas for his intellectual formation.",
    qualification="The cited support is Haskell’s note 6 to Tabacco, pp.32 ff.; that work was not independently consulted.",
    mentioned=["cand-1642", "cand-10470"], **footnote(6, 56, 4, [N6]))
add_statement(
    "st-chp15-p364-memmo-political-reform-and-noble-isolation", BODY, "cand-1648", "cand-10469",
    "exceptional_enthusiasm_for_reform_and_efforts_to_break_noble_isolation", 4, 4,
    "Haskell characterizes Memmo’s enthusiasm for political reform as altogether exceptional and says he repeatedly tried to break down the isolation of his fellow nobles.",
    qualification="The passage names no proposal, fellow noble or institutional outcome; cand-1648 is the index subentry and remains distinct from main candidate cand-1642 pending S3.",
    mentioned=["cand-1642", "cand-1648", "cand-10469", "cand-10473"])
add_statement(
    "st-chp15-p364-memmo-aristocratic-pleasures", BODY, "cand-1642", "cand-10473",
    "took_full_advantage_of_pleasures_open_to_aristocracy_of_his_day", 4, 4,
    "Haskell says Memmo took full advantage of the many pleasures open to the aristocracy of his day.",
    qualification="No specific pleasure beyond the following reference to Casanova is itemized here.",
    mentioned=["cand-1642", "cand-10473"])
add_statement(
    "st-chp15-p364-memmo-close-friend-casanova", BODY, "cand-1642", "cand-0591",
    "close_friend_of_casanova", 4, 4,
    "Haskell’s phrase ‘he was not the close friend of Casanova for nothing’ presents Memmo as a close friend of Casanova.",
    qualification="The statement is phrased rhetorically; no dates or particular shared activities are specified.",
    mentioned=["cand-1642", "cand-0591"], relation_candidate=True)
add_statement(
    "st-chp15-p364-memmo-involved-with-wynne", BODY, "cand-1642", "cand-2824",
    "became_involved_with_giustiniana_wynne_as_a_young_man", 4, 4,
    "Haskell says that as a young man Memmo became involved with Giustiniana Wynne.",
    qualification="The nature and dates of the involvement are not specified.",
    mentioned=["cand-1642", "cand-2824"], relation_candidate=True)
add_statement(
    "st-chp15-p364-memmo-smith-wooing-wynne", BODY, "cand-2440", "cand-2824",
    "was_wooing_giustiniana_wynne_when_memmo_became_involved", 4, 4,
    "Haskell says Giustiniana Wynne was then being wooed by Consul Smith when the narrative describes Memmo becoming involved with her.",
    qualification="The text does not state the outcome of Smith’s courtship or give a precise date.",
    mentioned=["cand-2440", "cand-2824"], relation_candidate=True)
add_statement(
    "st-chp15-p364-memmo-love-affairs-continuation-partial", BODY, "cand-1642", None,
    "continued_to_enjoy_and_write_about_a_series_of_love_affairs_partial", 4, 4,
    "P.364 ends the sentence with ‘and he’; the continuation is on the next printed page and is not completed in this segment.",
    qualification="Only the continuing subject is known here; the next clause is pending review against p.365.",
    mentioned=["cand-1642"], predicate_status="partial",
    cross_reference_segments=[BODY_NEXT],
    cross_reference_text="P.364 L4 ends ‘and he’; continuation is in p.365 L7.",
    cross_reference_text_pending=True)

add_statement(
    N3, NOTES, None, None, "note_cross_references_chapter12", 53, 53,
    "P.364 note 3 directs the reader to Chapter 12.", speaker="Haskell’s note", text_layer="citation trail",
    qualification="Internal cross-reference only; no separate source is identified or independently consulted.",
    cited_source_independently_consulted=False)
add_statement(
    N4M, NOTES, "cand-1642", "cand-10475", "note_cites_molmenti_biographical_source", 54, 54,
    "P.364 note 4 cites P. Molmenti’s undated ‘Un nobil huomo veneziano del secolo XVIII’ for a brief general biography of Andrea Memmo.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The article and its publication details were not independently checked.",
    mentioned=["cand-1642", "cand-10474", "cand-10475"], cited_source_independently_consulted=False)
add_statement(
    N4T, NOTES, "cand-1642", "cand-10476", "note_cites_torcellan_1963_biography", 54, 54,
    "P.364 note 4 cites Torcellan (1963), described there as the principal source for a brief general biography of Andrea Memmo.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The work’s full title and cited contents were not independently checked.",
    mentioned=["cand-1642", "cand-2644", "cand-10476"], cited_source_independently_consulted=False)
add_statement(
    N5, NOTES, None, None, "note_cross_references_chapter11", 55, 55,
    "P.364 note 5 directs the reader to Chapter 11.", speaker="Haskell’s note", text_layer="citation trail",
    qualification="Internal cross-reference only; Chapter 11 is not reinterpreted by this note statement.",
    cited_source_independently_consulted=False)
add_statement(
    N6, NOTES, "cand-1642", "cand-10477", "note_cites_tabacco_pages_32_ff", 56, 56,
    "P.364 note 6 cites Tabacco, pages 32 and following.", speaker="Haskell’s note", text_layer="citation trail",
    qualification="The OCR reads ‘if’; the page image reads ‘ff.’. The cited work was not independently consulted.",
    mentioned=["cand-1642", "cand-10477"], cited_source_independently_consulted=False)

new_statement_ids = {row["statement_id"] for row in statements if row["statement_id"].startswith("st-chp15-p364-memmo-")}
expected_statement_count = 19
if len(new_statement_ids) != expected_statement_count:
    raise SystemExit(f"expected {expected_statement_count} new p.364 Memmo statements, got {len(new_statement_ids)}")

coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L3-4",
    "note": "Printed p.364 checked against CHP-15.pdf physical p.4. Andrea Memmo’s opening paragraph and notes 3–6 are processed. The page ends with ‘and he’; continuation at p.365 L7 remains open in a partial statement. Printed note marker after ‘chaste architecture’ is 5 although OCR reads 6; note 6 after ‘intellectual formation’ links to Tabacco. OCR corrections are recorded only in S2; S0 unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L44-56",
    "note": "P.362 notes 1–2, p.363 notes 1, 3–6, p.364 Farsetti notes 1–2 and Andrea Memmo notes 3–6 are migrated. The p.364 cross-references to Chapters 11–12 and citations to Molmenti, Torcellan and Tabacco are recorded as citation trails; cited works were not independently consulted.",
})

result = {
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": SOURCE_SHA,
    "pdf_sha256": PDF_SHA,
    "new_candidates": len(new_candidates),
    "new_mentions": len(planned_mentions),
    "new_statements": len(new_statement_ids),
    "coverage_updates": {sid: coverage_by_id[sid] for sid in (BODY, NOTES)},
    "printed_page": 364,
    "pdf_physical_page": 4,
    "open_cross_page_statement": "st-chp15-p364-memmo-love-affairs-continuation-partial",
}
if args.apply:
    touched = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [(path, path.with_name(path.name + BACKUP_SUFFIX)) for path in touched]
    collision = next((backup for _, backup in backups if backup.exists()), None)
    if collision:
        raise SystemExit(f"backup already exists: {collision.name}")
    for path, backup in backups:
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions + planned_mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
print(json.dumps(result, ensure_ascii=False, indent=2))
