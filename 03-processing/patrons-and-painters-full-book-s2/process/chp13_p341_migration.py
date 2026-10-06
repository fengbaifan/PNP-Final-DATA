"""Controlled S2 migration for printed p.341; dry-run by default."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
BODY = "chp-13:13_CHP-13_intro:l90-96"
PREVIOUS = "chp-13:13_CHP-13_intro:l79-88"
NEXT = "chp-13:13_CHP-13_intro:l98-105"
NOTES = "chp-13:13_CHP-13_intro:l179-251"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BODY_SHA = "2aedb9d5ab3791a325d38e6b2a6b963d39fe6faab03ddf8930abde4740e74a95"
BACKUP_SUFFIX = ".bak-s2-chp13-p341-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.341 S2 migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical chapter 13 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-13 PDF asset changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if source_lines[89] != "[Page 341]":
    raise SystemExit("p.341 page anchor changed")
if hashlib.sha256("\n".join(source_lines[89:96]).encode("utf-8")).hexdigest() != BODY_SHA:
    raise SystemExit("p.341 source segment changed")
for line, required in {
    91: "Antonio Maria Zanetti the Elder",
    92: "Crozat came to Venice in 1716",
    93: "he succeeded in buying Lord Arundel",
    94: "Prince Eugene",
    95: "Count Tessin",
    96: "peu d’anciens",
}.items():
    if required not in source_lines[line - 1]:
        raise SystemExit(f"required p.341 text missing at L{line}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage = {row["segment_id"]: row for row in coverage_rows}

state = (
    len(candidates),
    max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions),
    len(statements),
)
if state != (10045, 10058, 21537, 9620):
    raise SystemExit(f"unexpected table pre-state: {state}")
for segment_id in (BODY, PREVIOUS, NEXT, NOTES):
    if segment_id not in coverage:
        raise SystemExit(f"required coverage row missing: {segment_id}")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.341 is not queued/pending")
if (coverage[PREVIOUS]["disposition"], coverage[PREVIOUS]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.340 is not reviewed/partial")
if (coverage[NOTES]["disposition"], coverage[NOTES]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("chapter 13 notes are not queued/pending")
if any(row["segment_id"] == BODY for row in mentions) or any(row["segment_id"] == BODY for row in statements):
    raise SystemExit("p.341 rows already exist")

new_candidates = []
new_mentions = []
new_statements = []
new_ids = {f"cand-{number}" for number in range(10059, 10077)}
if new_ids & set(candidate_by_id):
    raise SystemExit(f"p.341 candidate IDs already exist: {sorted(new_ids & set(candidate_by_id))}")
if any(row["mention_id"].startswith("m-s2-ch13-p341-") for row in mentions):
    raise SystemExit("p.341 mention IDs already exist")
if any(row["statement_id"].startswith("st-chp13-p341-") for row in statements):
    raise SystemExit("p.341 statement IDs already exist")

body_lines = {number: source_lines[number - 1] for number in range(90, 97)}
segment_text = "\n".join(body_lines[number] for number in range(90, 97))
line_offsets = {}
offset = 0
for number in range(90, 97):
    line_offsets[number] = offset
    offset += len(body_lines[number]) + 1


def add_candidate(cid, name, kind, detail, line):
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": cid,
        "canonical_name": name,
        "suggested_type": kind,
        "status": "open",
        "detail": detail,
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY}#L{line}",
    })
    new_candidates.append(row)


candidate_specs = [
    ("cand-10059", "Plate 58a (illustration referenced alongside Antonio Maria Zanetti the Elder)", "work",
     "The body associates Plate 58a with Zanetti. The depicted object, medium, maker, and relation to any separately indexed work must be checked against the plate segment.", 91),
    ("cand-10060", "Unnamed print sellers and publishers whose patronage diversified the Venetian scene", "term",
     "A group of men around print sellers and publishers who sometimes worked in both activities. No members are named here; the anaphoric link to p.340 remains contextual.", 91),
    ("cand-10061", "Cosmopolitan circle of connoisseurs in early eighteenth-century Venice", "term",
     "Haskell describes this social world as characteristic of Venice. Preserve the authorial characterization rather than treating it as a registered institution.", 91),
    ("cand-10062", "Unnamed leading collectors visited by Zanetti in London", "term",
     "The passage names no collectors in this group; do not infer individual identities.", 93),
    ("cand-10063", "Principal Venetian artists with whom Zanetti was in contact or acted as agent", "term",
     "The passage says virtually all principal artists but identifies only some elsewhere. Do not expand the unnamed group.", 91),
    ("cand-10064", "Unidentified pictures Zanetti was entrusted to purchase for the Regent's gallery", "work",
     "No titles, makers, number, or acquisition outcome are supplied in this passage.", 93),
    ("cand-10065", "Regent's own indecent illustrations for an edition of Daphnis and Chloe", "work",
     "The passage says the Regent sent Zanetti his own illustrations for an edition; it does not establish that the edition was published.", 93),
    ("cand-10066", "Parmigianino drawings from Lord Arundel's collection bought by Zanetti", "work",
     "The passage gives no titles or number. Retain Haskell's claim that these drawings influenced Zanetti's taste.", 93),
    ("cand-10067", "Pictures acquired by Zanetti from the heirs of Prince Eugene in Vienna in 1736", "work",
     "A group including an unidentified Poussin, an unidentified Castiglione, and a pastoral by Crespi; preserve the later note's pending qualification.", 93),
    ("cand-10068", "Unidentified heirs of Prince Eugene who sold pictures to Zanetti", "term",
     "The passage names no heir. This descriptive group is not a family identity or individual seller.", 93),
    ("cand-10069", "Unidentified Poussin picture bought from the heirs of Prince Eugene", "work",
     "The body identifies it only as 'a Poussin'. Keep the index-based candidate mapping and identity decision pending S3.", 94),
    ("cand-10070", "Unidentified Castiglione picture with animals and figures bought by Zanetti", "work",
     "The passage supplies no title; the surname-to-person mapping follows the index candidate provisionally and remains for S3.", 94),
    ("cand-10071", "Unidentified pastoral picture by Crespi bought from the heirs of Prince Eugene", "work",
     "No title is given. The body says only Crespi; retain the S1 index candidate as provisional for S3.", 94),
    ("cand-10072", "Rotterdam", "place",
     "Named only as a place Zanetti passed through on his 1720 journey toward Paris.", 92),
    ("cand-10073", "Joseph Smith and Marshal Schulenburg as leading foreign collectors in Venice", "term",
     "The source identifies the two individuals and describes them as the leading foreign collectors; no broader category is inferred.", 95),
    ("cand-10074", "Count Tessin's preference for rococo and graceful, lighthearted subjects", "term",
     "Retain the French quotation and Haskell's framing. The associated sentence continues onto p.342.", 95),
    ("cand-10075", "Rosalba Carriera and Giovanni Antonio Pellegrini as visitors welcomed in Paris", "term",
     "This descriptive group records the joint pronoun 'they' in the Paris sentence, not a formal institution or association.", 92),
    ("cand-10076", "Paris connoisseurs who welcomed Zanetti, Carriera, and Pellegrini", "term",
     "The passage names no members or institution; this is a descriptive audience group.", 92),
]
for spec in candidate_specs:
    add_candidate(*spec)
all_candidate_ids = set(candidate_by_id) | {row["candidate_id"] for row in new_candidates}


def add_mention(line, surface, cid, note="", occurrence=0):
    raw_line = body_lines[line]
    positions, cursor = [], 0
    while True:
        at = raw_line.find(surface, cursor)
        if at < 0:
            break
        positions.append(at)
        cursor = at + 1
    if occurrence >= len(positions):
        raise SystemExit(f"mention text missing at L{line}: {surface!r} occurrence {occurrence}")
    start = line_offsets[line] + positions[occurrence]
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch13-p341-{len(new_mentions) + 1:03d}",
        "segment_id": BODY,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    if cid not in all_candidate_ids:
        raise SystemExit(f"mention FK missing: {cid}")
    new_mentions.append(row)


mention_specs = [
    (91, "these printsellers and publishers", "cand-10060", "Anaphoric reference to the print sellers and publishers discussed on p.340."),
    (91, "a number.of men", "cand-10060", "OCR punctuation is corrected against the print in S2 only."),
    (91, "both activities", "cand-10060"),
    (91, "whose patronage", "cand-10060"),
    (91, "the Venetian scene", "cand-10061"),
    (91, "Antonio Maria Zanetti the Elder", "cand-2838"),
    (91, "Plate 58a", "cand-10059", "Cross-reference; the plate image remains to be reviewed in its source segment."),
    (91, "He was himself", "cand-2838", "Anaphoric reference to Zanetti."),
    (91, "a draughtsman and engraver", "cand-2838", "Role description of Zanetti."),
    (91, "an influential collector", "cand-2838"),
    (91, "he lived", "cand-2838"),
    (91, "that cosmopolitan world of connoisseurs", "cand-10061"),
    (91, "Venice", "cand-2719", "", 0),
    (91, "He was born in 1679", "cand-2838"),
    (91, "painting in Venice", "cand-2719"),
    (91, "Bologna", "cand-3398"),
    (91, "he was already in contact", "cand-2838"),
    (91, "most of the leading artists", "cand-10063"),
    (91, "Sebastiano", "cand-2154", "S1 index candidate covers p.341; preserve the source's abbreviated naming."),
    (91, "Marco Ricci", "cand-2149"),
    (91, "whose particular friend he was", "cand-2149", "The relative pronoun refers to Marco Ricci; 'he' refers to Zanetti."),
    (91, "Rosalba Carriera", "cand-0581"),
    (91, "he soon became known", "cand-2838"),
    (91, "one of the chief connoisseurs and collectors", "cand-2838"),
    (92, "Crozat", "cand-0894", "The prose gives the surname; S3 will resolve the indexed identity."),
    (92, "to Venice", "cand-2719"),
    (92, "he formed a close friendship", "cand-0894", "Anaphoric reference to Crozat."),
    (92, "with Zanetti", "cand-2839", "Uses the p.341 index subentry 'and Crozat' as a candidate locator."),
    (92, "who in turn set out for Paris", "cand-2838", "Relative pronoun refers to Zanetti."),
    (92, "Paris", "cand-4653"),
    (92, "Rotterdam", "cand-10072"),
    (92, "He stayed in Paris", "cand-2838"),
    (92, "his friend Rosalba Carriera", "cand-0581", "The possessive identifies Carriera as Zanetti's friend."),
    (92, "her brother-in-law Giovanni Antonio Pellegrini", "cand-1862"),
    (92, "he shared the welcome", "cand-2838"),
    (92, "they received", "cand-10075", "Joint reference to Carriera and Pellegrini."),
    (92, "the connoisseurs of the city", "cand-10076", "The city is Paris."),
    (92, "He met", "cand-2838"),
    (93, "Mariette", "cand-1547"),
    (93, "with whom", "cand-1547"),
    (93, "he corresponded", "cand-2838"),
    (93, "the end of his life", "cand-2838"),
    (93, "he was introduced", "cand-2838"),
    (93, "the Regent", "cand-1786", "The source uses only the title; S1's identity candidate remains for S3."),
    (93, "who entrusted him", "cand-1786", "The Regent is the subject; Zanetti is the recipient."),
    (93, "with the purchase of pictures", "cand-10064"),
    (93, "for his gallery", "cand-10064", "The gallery belongs to the Regent; collection type is not inferred."),
    (93, "sent him", "cand-1786", "The Regent is the subject of 'sent'."),
    (93, "his own indecent illustrations", "cand-10065", "The illustrations are described as the Regent's own."),
    (93, "an edition of Daphnis and Chloe", "cand-0901"),
    (93, "From Paris", "cand-4653"),
    (93, "he went to London", "cand-2838"),
    (93, "London", "cand-1422"),
    (93, "the leading collectors", "cand-10062"),
    (93, "he succeeded in buying", "cand-2851", "Uses the p.341 index subentry for Zanetti's purchase of Lord Arundel's drawings."),
    (93, "Lord Arundel’s Parmigianino drawings", "cand-10066"),
    (93, "Lord Arundel", "cand-0142"),
    (93, "Parmigianino", "cand-1839"),
    (93, "which were to exert great influence", "cand-10066"),
    (93, "his taste", "cand-2838"),
    (93, "his return to Venice", "cand-2838"),
    (93, "Venice", "cand-2719"),
    (93, "he seems to have gone to Vienna", "cand-2838"),
    (93, "Vienna", "cand-2772"),
    (93, "he certainly returned there in 1736", "cand-2838"),
    (93, "there", "cand-2772", "Anaphoric reference to Vienna."),
    (93, "he bought pictures from the heirs of", "cand-10067"),
    (93, "the heirs of", "cand-10068"),
    (94, "Prince Eugene", "cand-2384"),
    (94, "a Poussin", "cand-10069"),
    (94, "Poussin", "cand-1984", "The prose gives the surname only; index mapping is provisional pending S3."),
    (94, "a Castiglione", "cand-10070"),
    (94, "Castiglione", "cand-0602", "The prose gives the surname only; index mapping is provisional pending S3."),
    (94, "a pastoral by Crespi", "cand-10071"),
    (94, "Crespi", "cand-0871", "The prose gives the surname only; index mapping is provisional pending S3."),
    (94, "one of the finest things he ever painted", "cand-10071", "The assessment is attributed by the prose to the pastoral; the later note is still pending."),
    (95, "In Venice itself", "cand-2719"),
    (95, "Zanetti", "cand-2840", "Uses the p.341 index subentry 'and Joseph Smith' as a candidate locator."),
    (95, "Joseph Smith", "cand-2440"),
    (95, "Schulenburg", "cand-2401"),
    (95, "the two leading foreign collectors", "cand-10073"),
    (95, "virtually all the principal artists", "cand-10063"),
    (95, "for whom he sometimes acted as agent", "cand-2838", "Zanetti is the agent; the artists remain an unnamed group."),
    (95, "Count Tessin", "cand-2554"),
    (95, "his especial friend", "cand-2838", "The phrase describes Tessin's friendship with Zanetti."),
    (95, "Tessin had a particular fondness", "cand-2554"),
    (95, "the rococo and the lighthearted", "cand-10074"),
    (96, "peu d’anciens, mais l’élite des modernes et tous sujets gracieux et rians", "cand-10074", "French quotation in Haskell's narrative; source and speaker context await p.342 note 1."),
    (96, "he made", "cand-2554", "Sentence continues on p.342 L99; do not infer the object of 'made use' yet."),
]
for spec in mention_specs:
    add_mention(*spec)

corrections = [
    {"source_line": 91, "ocr": "number.of men", "print": "number of men", "basis": "CHP-13.pdf physical page 10."},
    {"source_line": 91, "ocr": "ani he soon", "print": "and he soon", "basis": "CHP-13.pdf physical page 10."},
]


def excerpt(first, last, start_text, end_text):
    local = "\n".join(body_lines[number] for number in range(first, last + 1))
    start = local.find(start_text)
    if start < 0:
        raise SystemExit(f"statement opening text missing: {start_text!r}")
    end = local.find(end_text, start)
    if end < 0:
        raise SystemExit(f"statement closing text missing: {end_text!r}")
    return local[start:end + len(end_text)]


note_lines = {1: "L223", 2: "L224", 3: "L225", 4: "L226"}


def note_ref(marker):
    return {
        "footnote_marker": str(marker),
        "footnote_printed_page": 341,
        "footnote_text_pending": True,
        "footnote_segment": NOTES,
        "footnote_line_range": note_lines[marker],
        "footnote_body_link_status": "pending",
    }


def add_statement(suffix, subject, obj, predicate, first, last, qfirst, qlast, claim,
                  qualification, mentioned, *, speaker="Haskell",
                  layer="authorial narrative", notes=(), relation_candidate=False,
                  cross_refs=()):
    sid = f"st-chp13-p341-{suffix}"
    if sid in statement_by_id:
        raise SystemExit(f"duplicate statement ID: {sid}")
    quote = excerpt(first, last, qfirst, qlast)
    ids = list(dict.fromkeys(mentioned + [candidate for candidate in (subject, obj) if candidate]))
    if any(cid not in all_candidate_ids for cid in ids):
        raise SystemExit(f"missing candidate FK: {sid}")
    qualifiers = {
        "source_line_start": first,
        "source_line_end": last,
        "printed_page": 341,
        "pdf_physical_page": 10,
        "claim": claim,
        "speaker": speaker,
        "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": ids,
        "ocr_corrections": [row for row in corrections if first <= row["source_line"] <= last],
    }
    if relation_candidate:
        qualifiers["relation_candidate"] = True
    if notes:
        refs = [note_ref(marker) for marker in notes]
        qualifiers["footnote_refs"] = refs
        qualifiers["footnote_marker"] = refs[0]["footnote_marker"] if len(refs) == 1 else [row["footnote_marker"] for row in refs]
        qualifiers["footnote_printed_page"] = 341
        qualifiers["footnote_text_pending"] = True
        qualifiers["footnote_body_link_status"] = "pending"
        qualifiers["cross_reference_segments"] = [NOTES]
    if cross_refs:
        qualifiers["cross_reference_segments"] = list(dict.fromkeys(
            qualifiers.get("cross_reference_segments", []) + list(cross_refs)
        ))
    new_statements.append({
        "statement_id": sid,
        "segment_id": BODY,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
    })


add_statement("unnamed_print_trade_patronage", "cand-10060", "cand-10061",
              "patronage_diversified_the_venetian_scene", 91, 91,
              "Around these printsellers", "the Venetian scene.",
              "Haskell describes a group around print sellers and publishers who sometimes engaged in both activities and whose patronage diversified the Venetian scene.",
              "The group is unnamed and anaphoric to the preceding p.340 discussion; no individual patron is inferred.",
              ["cand-10060", "cand-10061"], cross_refs=(PREVIOUS,))
add_statement("zanetti_portrait_reference_and_authorial_interest", "cand-2838", "cand-10059",
              "introduced_as_the_most_interesting_man_and_plate_58a", 91, 91,
              "By far the most interesting", "Plate 58a).",
              "Haskell identifies Antonio Maria Zanetti the Elder as the most interesting figure in the group and points to Plate 58a.",
              "The superlative is Haskell's evaluation. The plate's depicted object remains to be checked against its visual source segment.",
              ["cand-2838", "cand-10059"], notes=(1,))
add_statement("zanetti_draughtsman_engraver_collector", "cand-2838", None,
              "was_a_talented_draughtsman_engraver_and_influential_collector", 91, 91,
              "He was himself a draughtsman", "influential collector",
              "Zanetti was a draughtsman and engraver described as talented and an influential collector.",
              "These are Haskell's characterizations, not externally verified qualifications.",
              ["cand-2838"])
add_statement("zanetti_in_venetian_connoisseur_world", "cand-2838", "cand-10061",
              "lived_in_the_cosmopolitan_connoisseur_world_of_venice", 91, 91,
              "he lived in the very centre", "first part of the century",
              "Haskell places Zanetti at the centre of a cosmopolitan connoisseur world characteristic of Venice in the first part of the eighteenth century.",
              "Preserve the author's broad social characterization and period wording.",
              ["cand-2838", "cand-10061"])
add_statement("zanetti_birth_and_painting_study", "cand-2838", None,
              "born_in_1679_and_studied_painting_in_venice_and_bologna", 91, 91,
              "He was born in 1679", "later Bologna",
              "Haskell gives Zanetti's birth year as 1679 and says he studied painting in Venice and later Bologna.",
              "No exact dates or external identity claims are added.",
              ["cand-2838", "cand-2719", "cand-3398"])
add_statement("zanetti_contact_with_leading_artists", "cand-2838", "cand-10063",
              "was_in_contact_with_leading_artists_by_the_early_eighteenth_century", 91, 91,
              "Early in the eighteenth century", "Rosalba Carriera",
              "By the early eighteenth century Zanetti was in contact with leading artists, especially Sebastiano and Marco Ricci and Rosalba Carriera.",
              "The passage names these examples but does not enumerate all leading artists.",
              ["cand-2838", "cand-10063", "cand-2154", "cand-2149", "cand-0581"])
add_statement("zanetti_friendship_with_marco_ricci", "cand-2838", "cand-2149",
              "was_a_particular_friend_of_marco_ricci", 91, 91,
              "Marco Ricci", "whose particular friend he was)",
              "Haskell says Zanetti was a particular friend of Marco Ricci.",
              "The relative clause attaches the friendship to Marco Ricci; note 2 remains pending.",
              ["cand-2838", "cand-2149"], notes=(2,), relation_candidate=True)
add_statement("zanetti_known_as_connoisseur_and_collector", "cand-2838", None,
              "became_known_as_a_leading_connoisseur_and_collector_of_gems", 91, 91,
              "he soon became known", "especially of gems",
              "Zanetti became known as one of the chief connoisseurs and collectors, especially of gems.",
              "Preserve Haskell's reported reputation rather than treating it as a measured ranking.",
              ["cand-2838"])
add_statement("crozat_friendship_with_zanetti", "cand-0894", "cand-2838",
              "formed_a_close_friendship_with", 91, 92,
              "When", "with Zanetti",
              "Crozat came to Venice in 1716 and formed a close friendship with Zanetti.",
              "The source gives Crozat by surname; identity remains subject to S3.",
              ["cand-0894", "cand-2838", "cand-2719"], relation_candidate=True)
add_statement("zanetti_1720_journey_to_paris", "cand-2838", "cand-4653",
              "travelled_to_paris_via_rotterdam_in_1720", 92, 92,
              "who in turn set out for Paris in 1720", "Rotterdam",
              "Zanetti set out for Paris in 1720 after passing through Rotterdam.",
              "The page records only the stated route and year.",
              ["cand-2838", "cand-4653", "cand-10072"])
add_statement("paris_visit_with_carriera_and_pellegrini", "cand-2838", "cand-10075",
              "stayed_in_paris_with_carriera_and_pellegrini_and_shared_their_welcome", 92, 92,
              "He stayed in Paris at the same time", "the connoisseurs of the city",
              "Zanetti stayed in Paris at the same time as Rosalba Carriera and Giovanni Antonio Pellegrini and shared the welcome they received from the city's connoisseurs.",
              "The city is Paris; the visitors are not treated as a formal association.",
              ["cand-2838", "cand-0581", "cand-1862", "cand-10075", "cand-10076", "cand-4653"])
add_statement("pellegrini_brother_in_law_of_carriera", "cand-1862", "cand-0581",
              "was_the_brother_in_law_of", 92, 92,
              "her brother-in-law Giovanni Antonio Pellegrini", "her brother-in-law Giovanni Antonio Pellegrini",
              "Haskell identifies Giovanni Antonio Pellegrini as Rosalba Carriera's brother-in-law.",
              "The kinship is explicit in the passage; its exact family basis is not expanded.",
              ["cand-1862", "cand-0581"], relation_candidate=True)
add_statement("zanetti_met_and_corresponded_with_mariette", "cand-2838", "cand-1547",
              "met_and_corresponded_with_mariette_until_the_end_of_his_life", 92, 93,
              "He met", "the end of his life",
              "Zanetti met Mariette and corresponded with him until the end of his life.",
              "The cited footnote remains pending; the underlying correspondence is not independently checked.",
              ["cand-2838", "cand-1547"], notes=(3,), relation_candidate=True)
add_statement("regent_entrusted_zanetti_with_picture_purchases", "cand-1786", "cand-2838",
              "entrusted_zanetti_with_purchasing_pictures_for_his_gallery", 93, 93,
              "he was introduced to the Regent", "for his gallery",
              "After Zanetti was introduced to the Regent, the Regent entrusted him with buying pictures for the Regent's gallery.",
              "The source uses only 'the Regent'; the identity suggested by the index is not settled here. The pictures are unidentified.",
              ["cand-2838", "cand-1786", "cand-10064"], relation_candidate=True)
add_statement("regent_sent_illustrations_for_daphnis_and_chloe", "cand-1786", "cand-10065",
              "sent_zanetti_his_own_illustrations_for_an_edition_of_daphnis_and_chloe", 93, 93,
              "and sent him his own indecent illustrations", "Daphnis and Chloe",
              "The Regent sent Zanetti his own indecent illustrations for an edition of Daphnis and Chloe.",
              "This records the reported act of sending illustrations, not proof that the edition was published.",
              ["cand-1786", "cand-2838", "cand-10065", "cand-0901"], relation_candidate=True)
add_statement("zanetti_visited_london_collectors", "cand-2838", "cand-10062",
              "visited_leading_collectors_in_london", 93, 93,
              "From Paris he went to London", "the leading collectors",
              "From Paris Zanetti went to London, where he visited leading collectors.",
              "The collectors are unnamed.",
              ["cand-2838", "cand-4653", "cand-1422", "cand-10062"])
add_statement("zanetti_bought_arundel_parmigianino_drawings", "cand-2838", "cand-0142",
              "bought_drawings_from_lord_arundel", 93, 93,
              "he succeeded in buying Lord Arundel’s Parmigianino drawings", "Parmigianino drawings",
              "Zanetti succeeded in buying Lord Arundel's Parmigianino drawings in London.",
              "The number and titles are not stated; the source's ownership wording and index-based identity remain candidates.",
              ["cand-2838", "cand-2851", "cand-0142", "cand-1839", "cand-10066"], relation_candidate=True)
add_statement("arundel_drawings_influenced_zanettis_taste", "cand-10066", "cand-2838",
              "were_to_exert_great_influence_on_zanettis_taste", 93, 93,
              "which were to exert great influence", "his taste",
              "The Parmigianino drawings were expected to exert great influence on Zanetti's taste.",
              "The future-oriented wording is preserved; it is not rewritten as a measured outcome.",
              ["cand-10066", "cand-2838"])
add_statement("zanetti_returned_to_venice_and_went_to_vienna", "cand-2838", "cand-2772",
              "seems_to_have_gone_to_vienna_after_returning_to_venice_in_1722", 93, 93,
              "Soon after his return to Venice in 1722", "gone to Vienna",
              "Soon after returning to Venice in 1722, Zanetti seems to have gone to Vienna.",
              "The author explicitly qualifies the Vienna journey with 'seems'.",
              ["cand-2838", "cand-2719", "cand-2772"])
add_statement("zanetti_returned_to_vienna_in_1736", "cand-2838", "cand-2772",
              "certainly_returned_to_vienna_in_1736", 93, 93,
              "he certainly returned there in 1736", "there in 1736",
              "Haskell says Zanetti certainly returned to Vienna in 1736.",
              "Preserve the contrast between the qualified earlier visit and the definite 1736 return.",
              ["cand-2838", "cand-2772"])
add_statement("zanetti_1736_acquisitions_from_eugene_heirs", "cand-2838", "cand-10068",
              "bought_pictures_from_the_heirs_of_prince_eugene", 93, 94,
              "On this visit he bought pictures from the heirs of", "a pastoral by Crespi",
              "On the 1736 Vienna visit Zanetti bought pictures from the heirs of Prince Eugene, including a Poussin, a Castiglione, and a pastoral by Crespi.",
              "The note attached to the Crespi passage has not yet been semantically processed; identities and title-level work matches remain open.",
              ["cand-2838", "cand-10067", "cand-10068", "cand-2384", "cand-10069", "cand-1984",
               "cand-10070", "cand-0602", "cand-10071", "cand-0871"], notes=(4,), relation_candidate=True)
add_statement("crespi_pastoral_praised", "cand-10071", "cand-0871",
              "was_called_one_of_the_finest_things_crespi_ever_painted", 94, 94,
              "a pastoral by Crespi", "one of the finest things he ever painted’.",
              "The pastoral by Crespi is described as one of the finest things he ever painted.",
              "This is a qualitative judgment in Haskell's text; the referent of 'he' is Crespi and the cited note remains pending.",
              ["cand-10071", "cand-0871"], notes=(4,))
add_statement("zanetti_in_touch_with_smith_and_schulenburg", "cand-2838", "cand-10073",
              "was_in_touch_with_the_leading_foreign_collectors_smith_and_schulenburg", 95, 95,
              "In Venice itself Zanetti was in touch", "two leading foreign collectors",
              "In Venice Zanetti was in touch with Joseph Smith and Schulenburg, described as the two leading foreign collectors.",
              "The ranking is Haskell's description and is not independently verified.",
              ["cand-2838", "cand-2840", "cand-2440", "cand-2841", "cand-2401", "cand-10073"])
add_statement("zanetti_acted_as_agent_for_artists", "cand-2838", "cand-10063",
              "sometimes_acted_as_agent_for_principal_artists", 95, 95,
              "as well as with virtually all the principal artists", "acted as agent",
              "Zanetti was in contact with virtually all the principal artists and sometimes acted as their agent.",
              "The artists are not enumerated; the passage does not identify a specific transaction.",
              ["cand-2838", "cand-10063"], relation_candidate=True)
add_statement("tessin_was_zanettis_especial_friend", "cand-2554", "cand-2838",
              "was_zanettis_especial_friend", 95, 95,
              "Among foreign visitors", "his especial friend",
              "Haskell says the Swedish Count Tessin was Zanetti's especial friend.",
              "The source's spelling and title are retained; no further identity or relationship context is added.",
              ["cand-2554", "cand-2838"], relation_candidate=True)
add_statement("tessin_fondness_for_rococo_and_graceful_subjects", "cand-2554", "cand-10074",
              "favoured_rococo_and_lighthearted_graceful_subjects", 95, 96,
              "Tessin had a particular fondness", "rians’",
              "Tessin had a particular fondness for the rococo and lighthearted subjects, described in French as 'peu d’anciens, mais l’élite des modernes et tous sujets gracieux et rians'.",
              "The quotation is presented within Haskell's narrative; its precise source is pending p.342 note 1. The sentence continues on p.342 L99 with an unfinished clause.",
              ["cand-2554", "cand-10074"], speaker="Haskell (with a French quotation attributed in the narrative)",
              layer="authorial narrative with embedded quotation", cross_refs=(NEXT,))

all_candidates = sorted(candidates + new_candidates, key=lambda row: row["candidate_id"])
all_mentions = sorted(
    mentions + new_mentions,
    key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]),
)
all_statements = sorted(statements + new_statements, key=lambda row: row["statement_id"])
for key, rows in (("candidate_id", all_candidates), ("mention_id", all_mentions), ("statement_id", all_statements)):
    values = [row[key] for row in rows]
    if len(values) != len(set(values)):
        raise SystemExit(f"duplicate {key}")
for row in new_mentions:
    start, end = int(row["start_char"]), int(row["end_char"])
    if segment_text[start:end] != row["surface_form"]:
        raise SystemExit(f"mention span mismatch: {row['mention_id']}: {row['surface_form']!r}")
for row in new_statements:
    if row["segment_id"] != BODY or row["origin"] != "book":
        raise SystemExit(f"invalid statement metadata: {row['statement_id']}")
    q = row["qualifiers"]
    if not (90 <= q["source_line_start"] <= q["source_line_end"] <= 96):
        raise SystemExit(f"invalid source line range: {row['statement_id']}")
    if any(cid not in all_candidate_ids for cid in q["mentioned_candidate_ids"]):
        raise SystemExit(f"statement candidate FK missing: {row['statement_id']}")

correction_text = {item["source_line"]: (item["ocr"], item["print"]) for item in corrections}
coverage[BODY].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L90-96",
    "note": "Printed p.341 body reviewed against CHP-13.pdf physical page 10. Notes 1–4 map to consolidated notes L223–226 and remain pending in source order. The final sentence fragment ends 'and he made' and continues on p.342 L99; preserve the forward reference. Plate 58a is recorded as a cross-reference candidate pending review of its visual segment. OCR corrections are recorded in S2 only.",
})
coverage_rows = [coverage[row["segment_id"]] for row in coverage_rows]

print(f"p.341 dry-run: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("candidate additions:")
for row in new_candidates:
    print(f"  {row['candidate_id']} [{row['suggested_type']}] {row['canonical_name']}")
print("statement additions:")
for row in new_statements:
    q = row["qualifiers"]
    quote = row["original_quote"].replace("\n", " ↵ ")
    print(f"  {row['statement_id']} L{q['source_line_start']}-{q['source_line_end']} "
          f"{row['predicate']} [{row['subject_candidate_id']} -> {row['object_candidate_id'] or '—'}]: {quote}")
print("mention counts by candidate: " + ", ".join(
    f"{cid}={count}" for cid, count in sorted(Counter(row["candidate_id"] for row in new_mentions).items())
))
print("coverage: p.341 -> reviewed/partial; notes 1–4 await L223–226; sentence continues on p.342 L99")
print(f"totals: {len(all_candidates)} candidates, {len(all_mentions)} mentions, {len(all_statements)} statements")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

paths = [candidate_path, mention_path, statement_path, coverage_path]
for path in paths:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"recovery copy already exists: {backup.name}")
for path in paths:
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
write_csv(candidate_path, candidate_fields, all_candidates)
write_csv(mention_path, mention_fields, all_mentions)
write_jsonl(statement_path, all_statements)
write_csv(coverage_path, coverage_fields, coverage_rows)
print(f"applied; four recovery copies created with suffix {BACKUP_SUFFIX}")
