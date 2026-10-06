"""Controlled S2 migration for the full printed p.322 segment; dry-run unless --apply."""
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
PDF = ROOT / "02-sources" / "01-book" / "CHP-10.pdf"
SEGMENT = "chp-10:10_CHP-10_sec_ii:l175-184"
PREVIOUS_SEGMENT = "chp-10:10_CHP-10_sec_ii:l165-173"
PREVIOUS_STATEMENT = "st-chp10-p321-lodoli-originally-welcomed-algarotti-interest-fragment"
LEGACY_NEXT_SEGMENT = "chp-10:10_CHP-10_sec_ii:l175-178"
EXPECTED_MARKDOWN_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
EXPECTED_PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
EXPECTED_SEGMENT_SHA = "3b47bcb64e4f5e59b60c3630f772b20315f83009b796cae57f77fca0ad7acf39"
BACKUP_SUFFIX = ".bak-s2-chp10-p322-20261003"


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
parser.add_argument("--apply", action="store_true", help="write reviewed p.322 rows after creating recovery copies")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_MARKDOWN_SHA:
    raise SystemExit("canonical source markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != EXPECTED_PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[174:184]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA:
    raise SystemExit("p.322 S2 source segment changed")
if segment_lines[0] != "[Page 22]" or not segment_lines[-1].endswith("Pietro."):
    raise SystemExit("p.322 segment boundaries changed")
line_text = {number: source_lines[number - 1] for number in range(176, 185)}

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
table_state = (
    len(candidates),
    max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions),
    len(statements),
)
if table_state != (9745, 9758, 20564, 9105):
    raise SystemExit(f"table state changed; re-read current table counts before migration: {table_state}")

coverage = {row["segment_id"]: row for row in coverage_rows}
if (coverage[SEGMENT]["disposition"], coverage[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"p.322 coverage state changed: {coverage[SEGMENT]}")
if coverage[PREVIOUS_SEGMENT]["migration_status"] != "partial":
    raise SystemExit("expected p.321 to remain partial pending its notes")
if any(row["segment_id"] == SEGMENT for row in mentions) or any(row["segment_id"] == SEGMENT for row in statements):
    raise SystemExit("p.322 already has S2 mention or statement rows")

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


add_candidate("cand-9759", "Unidentified satirical sonnet about Carlo Lodoli and Francesco Algarotti", "archive", "Haskell says the two men were satirised together as wishing to weigh the moon; the title and author are not given in the body. Footnote 2 points to a Correr manuscript, still pending in canonical notes L315.", 179)
add_candidate("cand-9760", "Unidentified contemporary painters with whom Lodoli was said to interact", "", "Haskell reports extensive but unspecified dealings, commissions, reciprocal pictures, and studio visits; no painters are named as members of this group.", 180)
add_candidate("cand-9761", "Unidentified clients decorating town and country houses who received Lodoli's advice", "", "The text explicitly says the painters and clients are not identified; no individual client or house is named.", 180)
add_candidate("cand-9762", "Unidentified picture sellers described as Jews in Haskell's account of Lodoli", "", "Preserve the source's seller category without inferring identities, religion of particular dealers, transactions, or dates.", 180)
add_candidate("cand-9763", "Unidentified second-hand picture dealers from whom Lodoli acquired pictures", "", "No dealer or transaction is individually identified in the passage.", 180)
add_candidate("cand-9764", "Other Venetian history painters contrasted with Lodoli's reported taste", "term", "Haskell says it is very hard to believe Lodoli admired Tiepolo, Piazzetta, and the other Venetian 'history painters'; the group is not enumerated.", 181)
add_candidate("cand-9765", "Unidentified engraving after Alessandro Longhi's Carlo Lodoli portrait", "work", "The painting is said to have been engraved soon afterward; the print and its engraver are not separately identified. Keep this print distinct from the Plate 48c painting.", 182)
add_candidate("cand-9766", "Unnamed opponents who interpreted Lodoli's portrait text as destructive", "", "Haskell attributes this interpretation to Lodoli's opponents without naming them.", 182)
add_candidate("cand-9767", "Unnamed disciples who defended Lodoli through a Socratic analogy", "", "Haskell attributes the reply to Lodoli's disciples without naming them; the analogy is not proof of direct transmission.", 183)
add_candidate("cand-9768", "Austere approach to painting attributed to Lodoli", "term", "Haskell contrasts this stated standpoint with Conti's sympathy with fantasy; retain it as the author's characterization.", 179)
add_candidate("cand-9769", "Greeks glossed as Byzantines in Lodoli's gallery sequence", "", "The text itself parenthetically equates 'the Greeks' with 'the Byzantines'; retain this source-level gloss without external historical normalization.", 179)
add_candidate("cand-9770", "The unnamed moderns at the endpoint of Lodoli's gallery sequence", "", "A collective endpoint in the described progress of the arts; no individual artists or works are specified.", 179)

new_mentions = []


def add_mention(line_no, surface, candidate_id, note, occurrence=0):
    if candidate_id not in candidate_ids and not any(row["candidate_id"] == candidate_id for row in new_candidates):
        raise SystemExit(f"missing candidate for mention {surface!r}: {candidate_id}")
    line = line_text[line_no]
    positions = []
    cursor = 0
    while True:
        at = line.find(surface, cursor)
        if at < 0:
            break
        positions.append(at)
        cursor = at + 1
    if occurrence >= len(positions):
        raise SystemExit(f"mention text not found on L{line_no}: {surface!r} occurrence {occurrence}")
    line_offset = sum(len(source_lines[index]) + 1 for index in range(174, line_no - 1))
    start = line_offset + positions[occurrence]
    if segment_text[start:start + len(surface)] != surface:
        raise SystemExit(f"mention span mismatch on L{line_no}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "segment_id": SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    new_mentions.append(row)


MENTIONS = [
    (176, "Lodoli’s", "cand-1411", "The admired subject named at the start of the p.322 paragraph."),
    (176, "Andrea Memmo", "cand-1642", "One of the three people Haskell names as Lodoli's keenest admirers."),
    (176, "Angelo", "cand-2075", "First half of the line-broken name Angelo Querini; L177 completes the surname."),
    (177, "Querini", "cand-2075", "Completes the line-broken name Angelo Querini from L176."),
    (177, "Filippo Farsetti", "cand-1002", "One of the three people Haskell names as Lodoli's keenest admirers."),
    (177, "that very classicism", "cand-9748", "Anaphoric reference to the classicism described at p.321 L168; identity of concepts remains for later alignment."),
    (178, "Lodoli", "cand-1411", "Named as the person whose views this passage discusses."),
    (179, "Lodoli’s", "cand-1411", "Named as the subject of the views on painting."),
    (179, "sonnet", "cand-9759", "The unnamed satirical poem cited in the sentence; footnote 2 awaits canonical note L315."),
    (179, "Conti’s", "cand-0826", "Refers to Antonio Conti in the discussion of fantasy in painting."),
    (179, "fantasy", "cand-0829", "Uses the indexed Conti subentry for his defence/sympathy with fantasy in painting."),
    (179, "Smith’s", "cand-2440", "Joseph Smith, Consul Smith in the surrounding chapter context."),
    (179, "Abate Facciolati", "cand-0986", "Named as Smith's other friend and Lodoli's close contact."),
    (179, "Padua", "cand-1803", "Location attached to Facciolati in this passage."),
    (179, "his gallery", "cand-9181", "Lodoli's unidentified collection/gallery, reusing the earlier chapter 10 candidate from p.301."),
    (179, "the Greeks", "cand-9769", "The source's starting label for the art-historical sequence; parenthetical gloss follows."),
    (179, "the Byzantines", "cand-9769", "Explicitly glossed by Haskell as 'the Greeks'; do not normalize beyond the source gloss."),
    (179, "the moderns", "cand-9770", "Collective endpoint of the gallery's art-historical sequence; no members specified."),
    (180, "pictures", "cand-9181", "Pictures acquired for Lodoli's collection/gallery described immediately afterward."),
    (180, "Jews", "cand-9762", "Source's generic seller category; no individual or specific transaction identified."),
    (180, "second-hand dealers", "cand-9763", "Generic picture sellers, not individually named."),
    (180, "his relations", "cand-1411", "Refers to Lodoli's reported relations with contemporary painters."),
    (180, "contemporary painters", "cand-9760", "Unnamed group whose interactions with Lodoli are reported but not specified."),
    (180, "they", "cand-9760", "Corefers to the contemporary painters."),
    (180, "leading artists", "cand-9760", "Subset of the unnamed contemporary painters Lodoli reportedly watched at work."),
    (180, "them", "cand-9760", "Artists for whom Lodoli reportedly obtained commissions.", 0),
    (180, "them", "cand-9760", "Artists said to give Lodoli pictures in return.", 1),
    (180, "people who were decorating their town and country houses", "cand-9761", "Unnamed clients who received Lodoli's reported advice."),
    (180, "these painters", "cand-9760", "The painter group whose members Haskell says he cannot identify."),
    (180, "clients", "cand-9761", "The client group whose members Haskell says he cannot identify."),
    (180, "Lodoli", "cand-1411", "Named in Haskell's qualified inference about his artistic preferences."),
    (180, "Tiepolo", "cand-2569", "Artist named in Haskell's qualified statement about whom Lodoli may not have admired."),
    (181, "Piazzetta", "cand-1901", "Artist named in Haskell's qualified statement; retain candidate identity for later global alignment."),
    (181, "other Venetian ‘history painters’", "cand-9764", "An unspecified collective category contrasted with the named painters."),
    (181, "Canaletto", "cand-0498", "Named as a possible close contact and source of familiar work."),
    (181, "Visentini", "cand-2783", "Named as a possible close contact and source of familiar work."),
    (181, "Consul Smith", "cand-2440", "Joseph Smith is named as the route through which Lodoli knew their work."),
    (181, "Bartolommeo", "cand-1727", "First half of Bartolommeo Nazari's line-broken name; L182 completes it."),
    (182, "Nazari", "cand-1727", "Completes Bartolommeo Nazari's line-broken name; his portrait is indexed separately."),
    (182, "Alessandro Longhi", "cand-1424", "The painter explicitly associated with the latter portrait, Plate 48c."),
    (182, "him", "cand-1411", "The sitter in both portraits is Lodoli."),
    (182, "latter picture", "cand-1425", "The Longhi portrait candidate from the index subentry; the next phrase identifies it as Plate 48c."),
    (182, "Plate 48c", "cand-3998", "Direct cross-reference to the previously processed List of Plates candidate for Alessandro Longhi's Carlo Lodoli portrait."),
    (182, "Pietro Moscheni", "cand-1708", "Named as Lodoli's friend and the portrait's commissioner."),
    (182, "Lodoli’s", "cand-1411", "Named as Moscheni's friend and the portrait sitter."),
    (182, "The painting", "cand-1425", "Corefers to the Longhi portrait identified as Plate 48c."),
    (182, "the print", "cand-9765", "The separate, unidentified engraving made after the painting."),
    (182, "Carlo de Co:ti Lodoli", "cand-1411", "The sitter named in the printed Italian inscription; retain the spelling as printed/OCR-transcribed."),
    (182, "Socrate", "cand-6398", "Italian form in the inscription; the text likens Lodoli to Socrates rather than identifying a separate person."),
    (182, "Lodoli himself", "cand-1411", "Subject of the reported choice of decorative border."),
    (182, "his portrait", "cand-9765", "The portrait image as described within the print composition."),
    (182, "Vitruvius", "cand-2786", "Named as the source of words inscribed on the circular frieze."),
    (182, "his disciple Andrea Memmo", "cand-1642", "Memmo is explicitly identified as Lodoli's disciple in the account."),
    (182, "the portrait", "cand-9765", "Refers to the depicted portrait in the printed composition."),
    (182, "Jeremiah", "cand-5193", "Biblical prophet cited as the source of the text on the two tablets."),
    (182, "his opponents", "cand-9766", "Unnamed opponents to whom Haskell attributes the destructive interpretation."),
    (183, "his disciples", "cand-9767", "Unnamed disciples who answer the opponents' reading."),
    (183, "Socrates", "cand-6398", "Named as the source of the disciples' analogy about removing prejudice before truth."),
    (184, "Lodoli", "cand-1411", "Subject of the tentative closing inference."),
    (184, "Alessandro’s father, Pietro", "cand-1429", "The passage names Pietro as Alessandro Longhi's father; the relation remains a source claim for later review."),
]

for item in MENTIONS:
    add_mention(*item)
new_mentions.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"]), row["candidate_id"]))
for left, right in zip(new_mentions, new_mentions[1:]):
    if int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping p.322 mention spans: {left['surface_form']} and {right['surface_form']}")
for index, row in enumerate(new_mentions, 1):
    row["mention_id"] = f"m-s2-ch10-p322-{index:04d}"

candidate_ids_all = candidate_ids | {row["candidate_id"] for row in new_candidates}
new_statements = []


def add_statement(statement_id, subject, object_id, predicate, line_start, line_end,
                  claim, quote, qualification, mentioned, speaker="Haskell",
                  text_layer="authorial claim", relation_candidate=False, extra=None):
    if quote not in segment_text:
        raise SystemExit(f"statement quote is not anchored in p.322: {statement_id}")
    if any(cid not in candidate_ids_all for cid in mentioned):
        raise SystemExit(f"missing mentioned candidate in {statement_id}")
    if subject and subject not in candidate_ids_all:
        raise SystemExit(f"missing subject candidate in {statement_id}: {subject}")
    if object_id and object_id not in candidate_ids_all:
        raise SystemExit(f"missing object candidate in {statement_id}: {object_id}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 322,
        "pdf_physical_page": 55,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation_candidate,
    }
    if extra:
        qualifiers.update(extra)
    new_statements.append({
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
    })


SUPPORT_QUOTE = "\n".join(line_text[n] for n in (176, 177, 178))
add_statement(
    "st-chp10-p322-memmo-supports-classicism-questioned-by-lodoli", "cand-1642", "cand-9748", "became-strong-supporter-of-classicism-questioned-by-lodoli",
    176, 178,
    "Haskell names Andrea Memmo as one of Lodoli's keenest admirers and says he became a strong supporter of the classicism Lodoli had questioned.",
    SUPPORT_QUOTE,
    "'All' applies collectively to Memmo, Querini, and Farsetti. 'That very classicism' resolves to the specifically described emerging classicism at p.321 L168; it does not mean they agreed with Lodoli.",
    ["cand-1411", "cand-1642", "cand-9748"], relation_candidate=True,
    extra={"cross_reference_segments": [{"segment_id": "chp-10:10_CHP-10_sec_ii:l165-173", "source_line_start": 168, "source_line_end": 168}]},
)
add_statement(
    "st-chp10-p322-querini-supports-classicism-questioned-by-lodoli", "cand-2075", "cand-9748", "became-strong-supporter-of-classicism-questioned-by-lodoli",
    176, 178,
    "Haskell names Angelo Querini as one of Lodoli's keenest admirers and says he became a strong supporter of the classicism Lodoli had questioned.",
    SUPPORT_QUOTE,
    "'All' applies collectively to Memmo, Querini, and Farsetti. 'That very classicism' resolves to the specifically described emerging classicism at p.321 L168; it does not mean they agreed with Lodoli.",
    ["cand-1411", "cand-2075", "cand-9748"], relation_candidate=True,
    extra={"cross_reference_segments": [{"segment_id": "chp-10:10_CHP-10_sec_ii:l165-173", "source_line_start": 168, "source_line_end": 168}]},
)
add_statement(
    "st-chp10-p322-farsetti-supports-classicism-questioned-by-lodoli", "cand-1002", "cand-9748", "became-strong-supporter-of-classicism-questioned-by-lodoli",
    176, 178,
    "Haskell names Filippo Farsetti as one of Lodoli's keenest admirers and says he became a strong supporter of the classicism Lodoli had questioned.",
    SUPPORT_QUOTE,
    "'All' applies collectively to Memmo, Querini, and Farsetti. 'That very classicism' resolves to the specifically described emerging classicism at p.321 L168; it does not mean they agreed with Lodoli.",
    ["cand-1411", "cand-1002", "cand-9748"], relation_candidate=True,
    extra={"cross_reference_segments": [{"segment_id": "chp-10:10_CHP-10_sec_ii:l165-173", "source_line_start": 168, "source_line_end": 168}]},
)
add_statement(
    "st-chp10-p322-lodoli-views-on-painting-exceptional", "cand-1411", "cand-1421", "views-on-painting-described-as-exceptional",
    179, 179, "Haskell describes Lodoli's views on painting as exceptional.",
    "Lodoli’s views on painting were also exceptional.",
    "This is Haskell's evaluation, not a self-description by Lodoli.", ["cand-1411", "cand-1421"],
)
add_statement(
    "st-chp10-p322-sonnet-satirised-lodoli-and-algarotti", "cand-9759", None, "satirised-lodoli-and-algarotti-as-wishing-to-weigh-the-moon",
    179, 179,
    "Haskell says an unnamed bitter, 'reactionary' sonnet satirised Lodoli and Algarotti together as wishing to weigh the moon.",
    "Although the two men were satirised together in a bitter and ‘reactionary’ sonnet which accused them of wanting to weigh the moon’,2",
    "The local context identifies the two men as Lodoli and Francesco Algarotti. 'Reactionary' and the charge are the sonnet's attributed characterization. Footnote 2 awaits canonical note L315.",
    ["cand-1411", "cand-0048", "cand-9759"], text_layer="reported literary content",
    extra={"footnote_marker": 2, "pending_note_source_line": 315, "footnote_text_pending": True},
)
add_statement(
    "st-chp10-p322-lodoli-rejected-conti-fantasy", "cand-1411", "cand-0829", "rejected-contis-sympathy-with-fantasy-in-painting",
    179, 179, "Haskell says Lodoli wholly rejected Conti's sympathy with fantasy in painting.",
    "he wholly rejected Conti’s sympathy with fantasy",
    "'He' refers to Lodoli. This preserves Haskell's account of Conti's position and does not identify a separate work or artistic school.",
    ["cand-1411", "cand-0826", "cand-0829"], relation_candidate=True,
)
add_statement(
    "st-chp10-p322-lodoli-adopted-austere-painting-standpoint", "cand-1411", "cand-9768", "adopted-a-more-austere-standpoint-on-painting",
    179, 179, "Haskell says Lodoli adopted a far more austere standpoint on painting.",
    "and adopted a far more austere standpoint.",
    "The comparative 'far more' is retained; this is Haskell's characterization.", ["cand-1411", "cand-9768"], relation_candidate=True,
)
add_statement(
    "st-chp10-p322-smith-was-facciolatis-friend", "cand-2440", "cand-0986", "friend-of",
    179, 179, "Haskell identifies Abate Facciolati as another friend of Joseph Smith.",
    "Like Smith’s other friend, the Abate Facciolati in Padua",
    "The source says 'other friend'; retain that wording without inferring when or how the friendship began.",
    ["cand-2440", "cand-0986", "cand-1803"], relation_candidate=True,
)
add_statement(
    "st-chp10-p322-lodoli-was-close-to-facciolati", "cand-1411", "cand-0986", "was-in-close-touch-with",
    179, 179, "Haskell says Lodoli was also in close touch with Abate Facciolati.",
    "with whom he too was in close touch",
    "'He' refers to Lodoli; the wording establishes closeness but gives no dates or specific activities.",
    ["cand-1411", "cand-0986"], relation_candidate=True,
)
add_statement(
    "st-chp10-p322-lodoli-gallery-didactic-art-history-sequence", "cand-1411", "cand-9181", "arranged-gallery-to-show-progress-of-the-arts",
    179, 179,
    "Haskell says Lodoli arranged his gallery on didactic lines to show progress in the arts from the Greeks, glossed as Byzantines, to the moderns.",
    "he arranged his gallery on didactic lines so as to show the progress of the arts from the Greeks (Le. the Byzantines) until the moderns.3",
    "The scan confirms OCR 'Le.' should read 'i.e.' and the printed page is 322, not OCR '[Page 22]'. The source-level parenthetical equivalence is preserved. The gallery reuses the p.301 collection candidate; compare st-chp10-p301-facciolati-picture-collection without asserting the collections are identical. Footnote 3 awaits canonical note L316.",
    ["cand-1411", "cand-9181", "cand-9769", "cand-9770"], relation_candidate=True,
    extra={"footnote_marker": 3, "pending_note_source_line": 316, "footnote_text_pending": True,
           "cross_reference_segments": ["chp-10:10_CHP-10_intro:l382-389"]},
)
SELLER_QUOTE = "He acquired so many pictures from Jews and second-hand dealers that they not only covered his walls but were stacked on the floor as well."
add_statement(
    "st-chp10-p322-lodoli-acquired-pictures-from-jewish-sellers", "cand-1411", "cand-9762", "acquired-many-pictures-from-sellers-described-as-jews",
    180, 180, "Haskell says Lodoli acquired many pictures from sellers described generically as Jews.",
    SELLER_QUOTE,
    "The source gives no individual sellers, transaction, date, or evidence beyond this narrative. Preserve the source category without generalizing it to named people.",
    ["cand-1411", "cand-9762"], relation_candidate=True,
)
add_statement(
    "st-chp10-p322-lodoli-acquired-pictures-from-secondhand-dealers", "cand-1411", "cand-9763", "acquired-many-pictures-from-secondhand-dealers",
    180, 180, "Haskell says Lodoli acquired many pictures from second-hand dealers.",
    SELLER_QUOTE,
    "No dealer, transaction, date, or individual picture is identified.", ["cand-1411", "cand-9763"], relation_candidate=True,
)
add_statement(
    "st-chp10-p322-lodoli-picture-collection-filled-walls-and-floor", "cand-1411", "cand-9181", "many-pictures-covered-walls-and-were-stacked-on-floor",
    180, 180, "Haskell says Lodoli had so many pictures that they covered the walls and were stacked on the floor.",
    "that they not only covered his walls but were stacked on the floor as well",
    "This is Haskell's qualitative account; the passage supplies no count or inventory.", ["cand-1411", "cand-9181"],
)
add_statement(
    "st-chp10-p322-lodoli-painter-relations-reported-as-extensive", "cand-1411", "cand-9760", "painter-relations-said-to-be-extensive-but-unspecified",
    180, 180, "Haskell says Lodoli's relations with contemporary painters were reported as extensive, while admitting that almost nothing precise is known.",
    "Unfortunately, we know almost nothing precise about his relations with contemporary painters. We are told that they were extensive;",
    "'We are told' marks this as reported information, and Haskell explicitly limits what can be identified.",
    ["cand-1411", "cand-9760"], relation_candidate=True,
)
add_statement(
    "st-chp10-p322-lodoli-watched-leading-artists-work", "cand-1411", "cand-9760", "used-to-watch-leading-artists-at-work",
    180, 180, "Haskell reports that Lodoli used to go and watch leading artists at work.",
    "that he used to go and watch the leading artists at work;",
    "The habitual 'used to' is retained; the artists are not named.", ["cand-1411", "cand-9760"], relation_candidate=True,
)
add_statement(
    "st-chp10-p322-lodoli-obtained-commissions-for-artists", "cand-1411", "cand-9760", "would-obtain-commissions-for-painters",
    180, 180, "Haskell reports that Lodoli would obtain commissions for the painters.",
    "that he would obtain commissions for them",
    "The source uses a habitual conditional 'would'; no commission, patron, or artist is identified.", ["cand-1411", "cand-9760"], relation_candidate=True,
)
add_statement(
    "st-chp10-p322-painters-gave-pictures-to-lodoli-in-return", "cand-9760", "cand-1411", "would-give-pictures-to-lodoli-in-return",
    180, 180, "Haskell reports that the painters would give Lodoli pictures in return.",
    "and be given pictures by them in return",
    "The source uses a habitual conditional 'would'; no particular picture or painter is identified.", ["cand-9760", "cand-1411"], relation_candidate=True,
)
add_statement(
    "st-chp10-p322-lodoli-advised-unnamed-house-decorators", "cand-1411", "cand-9761", "would-give-advice-to-house-decorators",
    180, 180, "Haskell reports that Lodoli would advise people decorating town and country houses.",
    "that he would give advice to people who were decorating their town and country houses.",
    "The source gives no clients, houses, advice content, or dates.", ["cand-1411", "cand-9761"], relation_candidate=True,
)
add_statement(
    "st-chp10-p322-painters-and-clients-not-identified", None, None, "artists-and-clients-not-identified-in-account",
    180, 180, "Haskell says he has no idea who the painters and clients were.",
    "But we have no idea who these painters and clients were.",
    "This is an explicit limit on identification, not a claim that the painters or clients did not exist.",
    ["cand-9760", "cand-9761"], text_layer="authorial knowledge limit",
)
TASTE_QUOTE = "From what we know of his love of reason and authenticity it is very hard to believe that Lodoli can have admired Tiepolo,\nPiazzetta and the other Venetian ‘history painters’."
add_statement(
    "st-chp10-p322-haskell-doubts-lodoli-admired-history-painters", "cand-1411", "cand-9764", "haskell-finds-it-hard-to-believe-lodoli-admired-venetian-history-painters",
    180, 181,
    "Haskell says it is very hard to believe Lodoli admired Tiepolo, Piazzetta, or the other Venetian history painters, given his stated love of reason and authenticity.",
    TASTE_QUOTE,
    "This is an explicitly hedged inference ('very hard to believe' and 'can have admired'), not a categorical denial or direct testimony from Lodoli.",
    ["cand-1411", "cand-2569", "cand-1901", "cand-9764"], relation_candidate=True,
)
CONTACT_QUOTE = "It seems more likely that he may have been in close touch with artists like Canaletto and Visentini"
add_statement(
    "st-chp10-p322-lodoli-may-have-been-close-to-canaletto", "cand-1411", "cand-0498", "may-have-been-in-close-touch-with",
    181, 181, "Haskell says it seems more likely that Lodoli may have been in close touch with Canaletto.",
    CONTACT_QUOTE,
    "Both 'seems more likely' and 'may have been' are retained as Haskell's inference, not a confirmed personal relationship.",
    ["cand-1411", "cand-0498"], relation_candidate=True,
)
add_statement(
    "st-chp10-p322-lodoli-may-have-been-close-to-visentini", "cand-1411", "cand-2783", "may-have-been-in-close-touch-with",
    181, 181, "Haskell says it seems more likely that Lodoli may have been in close touch with Visentini.",
    CONTACT_QUOTE,
    "Both 'seems more likely' and 'may have been' are retained as Haskell's inference, not a confirmed personal relationship.",
    ["cand-1411", "cand-2783"], relation_candidate=True,
)
add_statement(
    "st-chp10-p322-lodoli-familiar-with-canaletto-visentini-work-through-smith", "cand-1411", "cand-2440", "work-familiarity-inferred-through-consul-smith",
    181, 181, "Haskell says Lodoli must have been very familiar with Canaletto's and Visentini's work through Consul Smith.",
    "with whose work he must have been very familiar through Consul Smith.",
    "'Must have been' is retained as Haskell's inference; the passage does not say Smith arranged a meeting between the artists and Lodoli.",
    ["cand-1411", "cand-0498", "cand-2783", "cand-2440"], relation_candidate=True,
)
PORTRAIT_CLAUSE = "Certainly he knew Bartolommeo\nNazari and Alessandro Longhi, both of whom painted portraits of him.4"
add_statement(
    "st-chp10-p322-lodoli-knew-nazari-who-painted-his-portrait", "cand-1411", "cand-1727", "knew-painter-who-painted-portrait-of-him",
    181, 182, "Haskell says Lodoli certainly knew Bartolommeo Nazari, who painted a portrait of him.",
    PORTRAIT_CLAUSE,
    "The source names the painter and sitter but gives no date or commission here. The indexed Nazari portrait is retained as a candidate work, not yet aligned to another version.",
    ["cand-1411", "cand-1727", "cand-1728"], relation_candidate=True,
)
add_statement(
    "st-chp10-p322-lodoli-knew-longhi-who-painted-plate48c-portrait", "cand-1411", "cand-1424", "knew-painter-who-painted-portrait-of-him",
    181, 182, "Haskell says Lodoli certainly knew Alessandro Longhi, who painted a portrait of him; the latter picture is identified as Plate 48c.",
    PORTRAIT_CLAUSE,
    "The p.322 body identifies the latter picture as Plate 48c. The List of Plates separately captions Plate 48c as Alessandro Longhi: Carlo Lodoli; the image caption for c was not independently legible in the earlier plate scan. The indexed portrait candidate and front-matter candidate remain distinct for S3.",
    ["cand-1411", "cand-1424", "cand-1425", "cand-3998"], relation_candidate=True,
    extra={"footnote_marker": 4, "pending_note_source_line": 317, "footnote_text_pending": True,
           "cross_reference_segments": ["front-matter:00_05_List_of_Plates:l123-138"],
           "cross_reference_candidate_ids": ["cand-3998"]},
)
add_statement(
    "st-chp10-p322-moscheni-friend-of-lodoli", "cand-1708", "cand-1411", "friend-of",
    182, 182, "Haskell identifies Pietro Moscheni as a friend of Lodoli.",
    "The latter picture (Plate 48c) was commissioned by a friend of Lodoli’s, Pietro Moscheni,",
    "The wording makes the friendship the basis for identifying the commissioner; it supplies no further biographical detail.",
    ["cand-1708", "cand-1411", "cand-1425", "cand-3998"], relation_candidate=True,
    extra={"cross_reference_segments": ["front-matter:00_05_List_of_Plates:l123-138"], "cross_reference_candidate_ids": ["cand-3998"]},
)
add_statement(
    "st-chp10-p322-moscheni-commissioned-longhi-portrait", "cand-1708", "cand-1425", "commissioned-portrait-of-carlo-lodoli-by-alessandro-longhi",
    182, 182, "Haskell says Pietro Moscheni commissioned Alessandro Longhi's portrait of Carlo Lodoli, Plate 48c.",
    "The latter picture (Plate 48c) was commissioned by a friend of Lodoli’s, Pietro Moscheni,",
    "The plate-number cross-reference is explicit. This source does not give the commission date; the List of Plates candidate remains a separate candidate pending S3.",
    ["cand-1708", "cand-1424", "cand-1411", "cand-1425", "cand-3998"], relation_candidate=True,
    extra={"cross_reference_segments": ["front-matter:00_05_List_of_Plates:l123-138"], "cross_reference_candidate_ids": ["cand-3998"]},
)
add_statement(
    "st-chp10-p322-longhi-portrait-described-as-penetrating-study", "cand-1425", None, "described-as-one-of-few-penetrating-studies-of-venetian-eighteenth-century",
    182, 182, "Haskell calls the Longhi portrait one of the very few penetrating studies of the Venetian eighteenth century.",
    "and it is one of the very few penetrating studies of the Venetian eighteenth century",
    "This is Haskell's evaluative description; it is not an external catalogue assessment.", ["cand-1425", "cand-3998"],
    extra={"cross_reference_candidate_ids": ["cand-3998"]},
)
add_statement(
    "st-chp10-p322-longhi-portrait-not-idealized", "cand-1425", "cand-1411", "portrait-described-as-not-beautifying-sitters-features",
    182, 182, "Haskell says no attempt is made to beautify Lodoli's coarse head and describes its nose, eyes, and hair.",
    "no attempt is made to beautify the rather coarse head with its large bulbous nose, lively eyes and straggling hair.",
    "Retain Haskell's visual description as his account of the portrait; it is not a verified physical description of Lodoli outside the image.",
    ["cand-1425", "cand-1411", "cand-3998"], extra={"cross_reference_candidate_ids": ["cand-3998"]},
)
add_statement(
    "st-chp10-p322-longhi-painting-engraved-as-separate-print", "cand-1425", "cand-9765", "painting-was-engraved-as-separate-print",
    182, 182, "Haskell says the Longhi painting was soon engraved and that words were added at the base of the print.",
    "The painting was soon engraved and at the base of the print were added the words:",
    "The painting and the later engraving are distinct work candidates; the engraver and print identity are not supplied.",
    ["cand-1425", "cand-3998", "cand-9765"], relation_candidate=True,
    extra={"cross_reference_candidate_ids": ["cand-3998"]},
)
add_statement(
    "st-chp10-p322-longhi-portrait-print-inscription", "cand-9765", "cand-1411", "print-inscribed-with-portrait-caption",
    182, 182, "Haskell transcribes the print's inscription as 'P. Carlo de Co:ti Lodoli Veneziano forse il Socrate Architetto'.",
    "‘P. Carlo de Co:ti Lodoli Veneziano forse il Socrate Architetto’",
    "This is the printed inscription as transcribed by Haskell; 'forse' is retained as the inscription's own qualification. The Italian wording is not silently translated or corrected.",
    ["cand-9765", "cand-1411", "cand-6398"], speaker="portrait print inscription", text_layer="reported inscription",
)
add_statement(
    "st-chp10-p322-lodoli-chose-print-portrait-border", "cand-1411", "cand-9765", "chose-decorative-border-for-portrait-print",
    182, 182, "Haskell says Lodoli chose the decorative border for his portrait and that this caused considerable controversy.",
    "Lodoli himself chose the decorative border and this caused a good deal of controversy.",
    "The passage does not identify the critics or date the controversy.", ["cand-1411", "cand-9765"], relation_candidate=True,
)
add_statement(
    "st-chp10-p322-print-portrait-had-architectural-attributes-and-circular-frieze", "cand-9765", None, "portrait-print-included-architectural-attributes-and-circular-frieze",
    182, 182, "Haskell says the portrait print included customary architectural attributes and a circular frieze around Lodoli's portrait.",
    "Apart from the usual attributes of the architect—plans, rulers, compasses, etc.—he had his portrait surrounded by a circular frieze",
    "This describes the print's composition; the listed attributes are not separate works or proven architectural instruments owned by Lodoli.",
    ["cand-9765", "cand-1411"],
)
add_statement(
    "st-chp10-p322-print-frieze-bears-words-derived-from-vitruvius", "cand-9765", "cand-2786", "circular-frieze-bears-words-derived-from-vitruvius",
    182, 182, "Haskell says the circular frieze carried words derived from Vitruvius.",
    "on which was written devonsi unir e fabrica e RAGiONE—e siA FUNZiON la rappresent azIone—words derived from Vitruvius",
    "Retain Haskell's transcribed Latin as printed in the source; no translation or textual emendation is introduced here.",
    ["cand-9765", "cand-2786"], relation_candidate=True,
)
add_statement(
    "st-chp10-p322-memmo-said-frieze-words-hard-to-understand", "cand-1642", "cand-9765", "disciple-admitted-vitruvian-words-difficult-to-understand",
    182, 182, "Haskell says Lodoli's disciple Andrea Memmo admitted that the words on the frieze were difficult for most people to understand.",
    "words derived from Vitruvius which his disciple Andrea Memmo admitted were difficult for most people to understand.",
    "The sentence identifies Memmo as Lodoli's disciple and reports his admission; it does not establish that the inscription was his own wording.",
    ["cand-1642", "cand-1411", "cand-9765", "cand-2786"], relation_candidate=True,
)
add_statement(
    "st-chp10-p322-print-tablets-bear-jeremiah-text", "cand-9765", "cand-5193", "portrait-tablets-bear-text-from-jeremiah",
    182, 182, "Haskell says two tablets at the base of the portrait bore a text from Jeremiah and supplies an English translation.",
    "At the base of the portrait were two tablets bearing a text from Jeremiah: ut eruas et destruas ut Plantes et AEDIFICES (See, I have this day set thee over the nations and over the kingdoms, to root out, and to pull down, and to destroy, and to throw down, to build and to plant)",
    "The Latin is the text Haskell transcribes, followed by his English rendering. This statement does not decide whether the tablets belonged to the painting or the print beyond the passage's local description.",
    ["cand-9765", "cand-5193", "cand-1411"], relation_candidate=True,
)
add_statement(
    "st-chp10-p322-opponents-read-tablet-text-as-destructive", "cand-9766", "cand-1411", "opponents-said-portrait-text-proved-destructive-interest",
    182, 182, "Haskell attributes to unnamed opponents the claim that the text proved Lodoli was only interested in destroying.",
    "—proof, said his opponents, that he was only interested in destroying.",
    "This is the opponents' interpretation as reported by Haskell, not an endorsed fact about Lodoli's motives.",
    ["cand-9766", "cand-1411", "cand-9765"], speaker="Lodoli's unnamed opponents (reported by Haskell)", text_layer="reported interpretation",
)
add_statement(
    "st-chp10-p322-disciples-defended-lodoli-through-socrates", "cand-9767", "cand-6398", "disciples-defended-lodoli-through-socratic-analogy",
    183, 183,
    "Haskell says Lodoli's unnamed disciples replied that he was following Socrates' belief that prejudice must be uprooted before truth could be appreciated.",
    "On the contrary, replied his disciples, he was merely following Socrates who believed that prejudice must be uprooted before truth could be appreciated.",
    "This is the disciples' reported defense by analogy, not evidence of a documented direct relationship or textual transmission from Socrates to Lodoli.",
    ["cand-9767", "cand-1411", "cand-6398"], speaker="Lodoli's unnamed disciples (reported by Haskell)", text_layer="reported interpretation",
    relation_candidate=True,
)
add_statement(
    "st-chp10-p322-lodoli-may-have-admired-pietro-longhi", "cand-1411", "cand-1429", "may-have-admired-pietro-longhi",
    184, 184, "Haskell says it is tempting to assume Lodoli may have admired Alessandro Longhi's father, Pietro.",
    "It is tempting to assume that Lodoli may have admired Alessandro’s father, Pietro.",
    "Both 'tempting to assume' and 'may have' are preserved; this is not established admiration or a confirmed biographical relationship.",
    ["cand-1411", "cand-1424", "cand-1429"], relation_candidate=True,
)

previous_hits = [row for row in statements if row.get("statement_id") == PREVIOUS_STATEMENT]
if len(previous_hits) != 1:
    raise SystemExit(f"expected one p.321 continuing statement, found {len(previous_hits)}")
previous_statement = previous_hits[0]
previous_qualifiers = previous_statement.get("qualifiers", {})
if (previous_statement.get("segment_id") != PREVIOUS_SEGMENT
        or previous_qualifiers.get("statement_continues") is not True
        or previous_qualifiers.get("continuation_segment_id") != LEGACY_NEXT_SEGMENT
        or not previous_statement.get("original_quote", "").endswith("had been")):
    raise SystemExit("p.321 final sentence continuation state changed")
previous_statement_updated = json.loads(json.dumps(previous_statement))
previous_statement_updated["qualifiers"]["statement_continues"] = False
previous_statement_updated["qualifiers"]["continuation_segment_id"] = SEGMENT
previous_statement_updated["qualifiers"]["continuation_completion_quote"] = "friendly."
previous_statement_updated["qualifiers"]["continuation_completed_by_segment_id"] = SEGMENT
previous_statement_updated["qualifiers"]["claim"] = (
    "Haskell says Lodoli had originally welcomed Algarotti's interest and says that the intention had been friendly."
)
previous_statement_updated["qualifiers"]["qualification"] = (
    "The phrase 'the intention had been friendly' is not assigned a more specific actor or object than the text provides. "
    "Footnote 1, attached to 'friendly', awaits canonical note L314."
)
previous_statement_updated["qualifiers"]["footnote_marker"] = 1
previous_statement_updated["qualifiers"]["pending_note_source_line"] = 314
previous_statement_updated["qualifiers"]["footnote_text_pending"] = True

statement_ids = {row["statement_id"] for row in statements}
if any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("p.322 statement ID already exists")
candidate_rows = candidates + new_candidates
mention_rows = mentions + new_mentions
statement_rows = [previous_statement_updated if row is previous_statement else row for row in statements] + new_statements

previous_note = coverage[PREVIOUS_SEGMENT].get("note", "")
old_continuation = "The final clause at L173 continues at " + LEGACY_NEXT_SEGMENT + "; coverage remains partial pending that continuation and the notes."
if previous_note.count(old_continuation) != 1:
    raise SystemExit("p.321 coverage note does not contain the expected p.322 continuation")
coverage[PREVIOUS_SEGMENT]["note"] = previous_note.replace(
    old_continuation,
    "The L173 clause now closes with 'friendly.' at p.322 L176. Footnotes 1–3 await canonical notes L311–313; "
    "footnote 1 attached to the completed clause awaits canonical note L314.",
)

coverage[SEGMENT].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L176-184",
    "note": (
        "Read the complete S0 segment L175–184 against CHP-10.pdf physical p.55, printed p.322. The OCR page marker '[Page 22]' "
        "is wrong. L176 closes the p.321 sentence ('friendly.') and names Lodoli's three keenest admirers; all three became "
        "supporters of the classicism Lodoli questioned. L179 records his painting views, the sonnet about Lodoli and Algarotti, "
        "Conti's fantasy position, Facciolati friendship, and Lodoli's didactic gallery. L180–181 preserves the source's limits and "
        "hedges about unnamed painter relations, Tiepolo/Piazzetta, Canaletto, and Visentini. L182–184 distinguishes Nazari and "
        "Longhi portraits, the Plate 48c painting from its later engraving, Moscheni's friendship/commission, the printed inscription, "
        "the decorative border, Vitruvian frieze, Jeremiah text, opponents' and disciples' interpretations, and Haskell's tentative "
        "Pietro Longhi inference. Reuse the previously processed Plate 48c List of Plates candidate and link its segment. The scan "
        "corrects '[Page 22]' to printed p.322 and OCR 'Le.' to 'i.e.'; S0 remains unchanged. Added "
        f"{len(new_candidates)} candidates, {len(new_mentions)} exact mentions, and {len(new_statements)} statements. "
        "Footnotes 1–4 await canonical notes L314–317; footnote 4's note about the portrait location must be compared with the "
        "List of Plates caption (Accademia versus Museo Correr) without resolving the conflict here."
    ),
})

print(f"p.322 preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements; close the p.321 continuation")
print(f"coverage: p.321 remains partial pending notes; p.322 reviewed/partial; totals {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(statement_rows)} statements")
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
