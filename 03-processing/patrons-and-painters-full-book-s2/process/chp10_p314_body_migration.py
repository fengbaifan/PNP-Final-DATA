"""Controlled S2 migration for printed p.314 body; dry-run unless --apply."""
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
SEGMENT = "chp-10:10_CHP-10_sec_ii:l83-93"
PREVIOUS_SEGMENT = "chp-10:10_CHP-10_sec_ii:l72-81"
EXPECTED_ASSET_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
EXPECTED_SEGMENT_SHA = "aff0d4d1ae3dfe47510086a0cd9524cf53a7a585e0a681200b08d1b2a909b478"
BACKUP_SUFFIX = ".bak-s2-chp10-p314-body-20261003"


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
parser.add_argument("--apply", action="store_true", help="write reviewed p.314 rows after creating recovery copies")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[82:93]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA:
    raise SystemExit("S2 source segment changed")
if segment_lines[0] != "[Page 314]" or not segment_lines[-1].endswith("estates in"):
    raise SystemExit("p.314 segment boundaries changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
table_state = (len(candidates), max(int(row["candidate_id"].split("-")[1]) for row in candidates), len(mentions), len(statements))
if table_state != (9582, 9595, 20095, 8892):
    raise SystemExit(f"table state changed; re-read current table counts before migration: {table_state}")

REQUIRED = {
    "schulenburg": "cand-2401", "smith": "cand-2440", "piazzetta": "cand-3862",
    "pittoni": "cand-3870", "canaletto": "cand-3738", "marieschi": "cand-1546",
    "carlevarijs": "cand-0554", "cimaroli": "cand-3748", "joli": "cand-1334",
    "marco_ricci": "cand-3831", "zuccarelli": "cand-2879", "nazari": "cand-1727",
    "nogari": "cand-1743", "rembrandt": "cand-3471", "ceruti": "cand-0637",
    "colgne": "cand-6300", "chicago": "cand-4624", "venice": "cand-3401",
    "plate54_idyll": "cand-4076", "palazzo_loredan": "cand-9571",
}
for label, candidate_id in REQUIRED.items():
    if candidate_id not in candidate_ids:
        raise SystemExit(f"required candidate missing: {label}={candidate_id}")

coverage = {row["segment_id"]: row for row in coverage_rows}
if (coverage[SEGMENT]["disposition"], coverage[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"p.314 coverage state changed: {coverage[SEGMENT]}")
if coverage[PREVIOUS_SEGMENT]["migration_status"] != "partial":
    raise SystemExit("expected p.313 segment to remain partial pending its notes")
if any(row["segment_id"] == SEGMENT for row in mentions) or any(row["segment_id"] == SEGMENT for row in statements):
    raise SystemExit("p.314 already has S2 mention or statement rows")

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


add_candidate("cand-9596", "Unidentified Piazzetta drawing described as ‘des animaux et figures à la flamande’", "work", "Haskell says Schulenburg owned a drawing by Piazzetta and gives this French description; no formal title or exact identity is supplied.", 86)
add_candidate("cand-9597", "About twenty heads of men and women by Bartolommeo Nazari and Giuseppe Nogari in Schulenburg’s collection", "work", "The source describes a group of about twenty heads, places them in a genre looking back to Rembrandt, and does not individuate titles.", 86)
add_candidate("cand-9598", "Piazzetta picture of a beggar holding a rosary for Schulenburg", "work", "Named as a subject painted by Piazzetta for Schulenburg; the wording may be descriptive rather than a formal title.", 87)
add_candidate("cand-9599", "Piazzetta picture of a girl with a basket of chickens for Schulenburg", "work", "Named as a subject painted by Piazzetta for Schulenburg; the wording may be descriptive rather than a formal title.", 87)
add_candidate("cand-9600", "Two large Piazzetta pastorals or idylls reported at Cologne and Chicago", "work", "Haskell refers to plural pictures and gives the two cities without mapping an individual inventory description to either city. Possible overlap with the separately indexed Plate 54 Idyll is unresolved.", 88)
add_candidate("cand-9601", "First inventory-described Piazzetta pastoral: seated woman, boy, grapes, dogs, duck, and two men", "work", "The first French inventory description is quoted in Haskell; its correspondence to Cologne/Chicago and to Plate 54 is not settled here.", 88)
add_candidate("cand-9602", "Second inventory-described Piazzetta pastoral: woman with parasol, servant, peasant, sleeping boy, and ox head", "work", "The second French inventory description is quoted in Haskell; its correspondence to Cologne/Chicago and to Plate 54 is not settled here.", 88)
add_candidate("cand-9603", "Undated inventory of Schulenburg’s collection drawn up by Piazzetta", "archive", "Haskell says Piazzetta drew up the inventory and quotes two descriptions; the document is not independently identified in the body passage.", 88)
add_candidate("cand-9604", "Seven pictures by Giacomo Ceruti in Schulenburg’s collection", "work", "Haskell says some portrayed beggars and others animals; individual works are not named in this sentence.", 88)
add_candidate("cand-9605", "Dutch and Flemish painting as a collecting preference in Schulenburg’s account", "term", "A collecting taste that Haskell says shaped the kinds of pictures patronized and owned; this source-specific concept remains distinct from individual Dutch/Flemish works.", 86)
add_candidate("cand-9606", "Genre painting as a category for pictures of ordinary people and animals", "term", "Used for the heads, other works in Schulenburg’s gallery, and the contrast with histories and mythologies.", 87)
add_candidate("cand-9607", "Vedutisti and landscape painters as a group patronized by Schulenburg", "term", "Haskell compares Schulenburg with Smith and names the artists represented in the following lines; not a claim that every listed artist has the same identity or role.", 89)
add_candidate("cand-9608", "View and landscape pictures by Michele Marieschi in Schulenburg’s collection", "work", "Haskell reports one view and a number of landscapes; p.314 note 4 supplies the count and is pending later source-order processing.", 90)
add_candidate("cand-9609", "Landscape pictures by Luca Carlevarijs in Schulenburg’s collection", "work", "P.314 note 4 supplies the count and is pending later source-order processing.", 91)
add_candidate("cand-9610", "Landscape pictures by Giovan Battista Cimaroli in Schulenburg’s collection", "work", "P.314 note 4 supplies the count and is pending later source-order processing.", 91)
add_candidate("cand-9611", "Landscape pictures by Antonio Joli in Schulenburg’s collection", "work", "P.314 note 4 supplies the count and is pending later source-order processing.", 91)
add_candidate("cand-9612", "Landscape pictures by Marco Ricci in Schulenburg’s collection", "work", "Haskell particularly emphasizes Ricci; p.314 note 4 supplies the count and is pending later source-order processing.", 91)
add_candidate("cand-9613", "Landscape pictures by Francesco Zuccarelli in Schulenburg’s collection", "work", "Haskell particularly emphasizes Zuccarelli; p.314 note 4 supplies the count and is pending later source-order processing.", 91)
add_candidate("cand-9614", "Unspecified Dutch and Flemish masters represented in Schulenburg’s gallery", "term", "An unnamed group in Haskell’s hypothetical comparison of what visitors would see hanging together.", 88)
add_candidate("cand-9615", "Unspecified English associates with whom Canaletto had close relations", "term", "Haskell names no individual and does not say that these English associates lived in Venice.", 89)
add_candidate("cand-9616", "Unspecified Flemish pictures considered or purchased for Schulenburg through Piazzetta", "work", "The market-purchase group is not equated with the separately mentioned Piazzetta drawing or other pictures. Footnote 1 may document recommended pictures and remains pending.", 85)
add_candidate("cand-9617", "Social-satire interpretation proposed for the first inventory-described Piazzetta pastoral", "term", "An unnamed suggestion that Haskell describes as almost certainly wrong; retain only as a qualified interpretive claim.", 88)
add_candidate("cand-9618", "Certain unnamed Venetian artists patronized in relation to Schulenburg’s Dutch and Flemish taste", "term", "The group is not enumerated in this sentence; named artists in adjacent sentences are recorded separately.", 86)
add_candidate("cand-9619", "Piazzetta pictures in Schulenburg’s collection (group, not individually enumerated)", "work", "Plural works invoked in Haskell’s hypothetical gallery description; includes but is not restricted to the two pastorals in cand-9600.", 88)
add_candidate("cand-9620", "Other unnamed residents in Venice whose access to Canaletto pictures was difficult", "term", "Haskell says Canaletto’s close English relations made acquisition difficult for other Venice residents; no individuals are named.", 89)
add_candidate("cand-9621", "Naturalistic painting and a taste for naturalism in Schulenburg’s account", "term", "Source-specific use in the p.314 patronage passage; relation to the separate chapter-four naturalism candidate is deferred to S3.", 87)
add_candidate("cand-9622", "Schulenburg’s picture collection referred to as his gallery", "", "Haskell uses both ‘collection’ and ‘gallery’ for this body of pictures; the taxonomy has no collection type, so keep type unresolved and distinct from Schulenburg and Palazzo Loredan.", 88)
add_candidate("cand-9623", "Unspecified estates to which Schulenburg sent picture crates", "place", "Plural property destinations named as ‘his estates’; the sentence continues at p.315 with ‘Germany’, and no individual estate is identified.", 93)
add_candidate("cand-9624", "Histories and mythologies as the picture repertoire familiar to Schulenburg’s visitors", "term", "Haskell contrasts the visitors’ familiarity with histories and mythologies against the imagined mixed display; no particular paintings are identified by this phrase.", 88)
add_candidate("cand-9625", "Unspecified pictures sent in crates from Schulenburg’s collection to his estates", "work", "A group of pictures referred to as ‘them’ in the shipping sentence; no individual works are identified, and the sentence continues at p.315.", 93)

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
    relative_line = line_no - 83
    start = sum(len(item) + 1 for item in segment_lines[:relative_line]) + starts[occurrence]
    if segment_text[start:start + len(surface)] != surface:
        raise SystemExit(f"mention span mismatch on L{line_no}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p314-{len(new_mentions) + 1:04d}",
        "segment_id": SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    new_mentions.append(row)


MENTIONS = [
    (84, "Pittoni", "cand-3870", "Named as the painter of dramatic action."),
    (84, "he", "cand-2401", "Corefers to Schulenburg."),
    (84, "him", "cand-3862", "Corefers to Piazzetta."),
    (84, "this painter’s talents", "cand-3862", "Corefers to Piazzetta."),
    (85, "Piazzetta", "cand-3862", "Named as Schulenburg’s agent."),
    (85, "Schulenburg’s", "cand-2401", "Marshal Johann Matthias Schulenburg."),
    (85, "chief agent", "cand-3862", "Role described by Haskell; formal relationship review is deferred."),
    (85, "interesting pictures", "cand-9616", "Generic market purchases; not identified with the separately named Piazzetta drawing or pictures below."),
    (85, "usually Flemish", "cand-9616", "Qualifies the unnamed market pictures, not the collecting preference."),
    (85, "the old Marshal", "cand-2401"),
    (86, "Dutch and Flemish painting", "cand-9605"),
    (86, "Venetian artists", "cand-9618", "Generic group; no complete member set is asserted here."),
    (86, "he", "cand-2401", "Corefers to Schulenburg."),
    (86, "a drawing", "cand-9596"),
    (86, "Piazzetta", "cand-3862"),
    (86, "des animaux et figures à la flamande", "cand-9596", "French description of the drawing, not a formal title."),
    (86, "some twenty heads", "cand-9597", "Approximate quantity is retained."),
    (86, "Bartolommeo", "cand-1727", "Continues as Bartolommeo Nazari on L87."),
    (87, "Nazari", "cand-1727"),
    (87, "Giuseppe Nogari", "cand-1743"),
    (87, "a genre", "cand-9606"),
    (87, "Rembrandt", "cand-3471"),
    (87, "this taste for Flemish art", "cand-9605"),
    (87, "the Marshal", "cand-2401"),
    (87, "naturalistic painting", "cand-9621"),
    (87, "Piazzetta", "cand-3862"),
    (87, "him", "cand-2401", "Corefers to Schulenburg."),
    (87, "a Beggar holding a Rosary", "cand-9598", "Subject wording, not confirmed as a formal title."),
    (88, "Girl with a Basket of Chickens", "cand-9599", "Subject wording, not confirmed as a formal title."),
    (88, "the great pastorals or idylls", "cand-9600"),
    (88, "Cologne", "cand-6300", "City named as one of two locations; no institution or individual work mapping is supplied."),
    (88, "Chicago", "cand-4624", "City named as one of two locations; no institution or individual work mapping is supplied."),
    (88, "these pictures", "cand-9600", "Refers to the preceding group of pastorals/idylls."),
    (88, "Piazzetta himself", "cand-3862"),
    (88, "the inventory", "cand-9603"),
    (88, "them", "cand-9600", "Refers to the two pastorals/idylls.", 0),
    (88, "représentant une femme assise au naturel", "cand-9601", "First quoted inventory description; not assigned to Cologne or Chicago."),
    (88, "Une femme avec un parasol", "cand-9602", "Second quoted inventory description; not assigned to Cologne or Chicago."),
    (88, "Plate 54", "cand-4076", "Piazzetta Idyll is mentioned as an illustration; exact identity with either described picture remains unresolved."),
    (88, "the former picture", "cand-9601", "Corefers to the first inventory-described picture."),
    (88, "social satire", "cand-9617"),
    (88, "the pictures", "cand-9600", "Refers to the pastorals/idylls.", 0),
    (88, "realistic", "cand-9621", "Quoted evaluation of perceived effect; the source says 'probably'."),
    (88, "Venice", "cand-3401", "City, not the Venetian State."),
    (88, "Piazzetta himself", "cand-3862", "Occasional exception in Haskell’s comparison.", 1),
    (88, "a taste for naturalism", "cand-9621"),
    (88, "the Marshal", "cand-2401"),
    (88, "his gallery", "cand-9622", "Refers to Schulenburg’s picture collection; no collection type exists in the current taxonomy."),
    (88, "Schulenburg’s collection", "cand-9622", "Collection as a group, distinct from Schulenburg and the palace."),
    (88, "genre pictures", "cand-9606"),
    (88, "Giacomo Ceruti", "cand-0637"),
    (88, "seven", "cand-9604", "Count of Ceruti pictures in the collection."),
    (88, "These pictures", "cand-9604", "Refers to the seven works by Ceruti."),
    (88, "Venice", "cand-3401", "", 1),
    (88, "his Piazzettas", "cand-9619", "Plural works in the Marshal’s collection; not reduced to the pastorals alone."),
    (88, "Dutch and Flemish masters", "cand-9614"),
    (88, "his palace", "cand-9571", "Corefers to Palazzo Loredan, identified as Schulenburg’s residence on p.311."),
    (88, "histories and mythologies", "cand-9624"),
    (89, "Smith", "cand-2440", "Joseph Smith, used as the comparison in this chapter."),
    (89, "Schulenburg", "cand-2401"),
    (89, "vedutisti and landscape painters", "cand-9607"),
    (89, "Canaletto", "cand-3738", "The claim allows one or two exceptions."),
    (89, "the English", "cand-9615", "Unspecified English associates; not stated to live in Venice."),
    (89, "other residents", "cand-9620", "Unspecified people living in Venice."),
    (89, "Venice", "cand-3401", "City in which the unnamed residents lived."),
    (89, "his work", "cand-3738", "Canaletto’s work."),
    (90, "he", "cand-2401", "Corefers to Schulenburg."),
    (90, "a view and a number of landscapes", "cand-9608", "The source gives no count in the body; note 4 is pending."),
    (90, "Marieschi", "cand-1546"),
    (91, "Carlevarijs", "cand-0554"),
    (91, "Cimaroli", "cand-3748"),
    (91, "Joli", "cand-1334"),
    (91, "Marco Ricci", "cand-3831"),
    (91, "Zuccarelli", "cand-2879"),
    (92, "Schulenburg’s collection of pictures", "cand-9622"),
    (93, "Smith’s", "cand-2440"),
    (93, "he", "cand-2401", "Corefers to Schulenburg."),
    (93, "them", "cand-9625", "Pictures sent in crates; the sentence continues at p.315."),
    (93, "his estates", "cand-9623", "Destination phrase continues at p.315 with ‘Germany’."),
]
for item in MENTIONS:
    add_mention(*item)

mention_by_id = {row["mention_id"]: row for row in mentions}
prev_fragment_mention = mention_by_id.get("m-s2-ch10-p313-0074")
if not prev_fragment_mention or prev_fragment_mention["note"] != "Sentence continues at p.314 L84; no completed claim is asserted from this fragment.":
    raise SystemExit("expected p.313 Piazzetta-gifts continuation mention changed")
prev_fragment_mention["note"] = "Cross-page sentence fragment; completed by st-chp10-p314-piazzetta-alternative-picture-type at p.314 L84."

new_statements = []


def add_statement(statement_id, segment_id, subject, object_id, predicate, line_start, line_end,
                  claim, quote, qualification, mentioned, relation_candidate=False, extra=None):
    anchor_text = segment_text if segment_id == SEGMENT else "\n".join(source_lines[71:81])
    if quote not in anchor_text:
        raise SystemExit(f"statement quote is not anchored: {statement_id}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 314 if segment_id == SEGMENT else 313,
        "pdf_physical_page": 47 if segment_id == SEGMENT else 46,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial claim",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation_candidate,
    }
    if extra:
        qualifiers.update(extra)
    if any(cid not in candidate_ids for cid in mentioned):
        raise SystemExit(f"missing mentioned candidate in {statement_id}")
    new_statements.append({
        "statement_id": statement_id,
        "segment_id": segment_id,
        "subject_candidate_id": subject,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
    })


add_statement(
    "st-chp10-p314-piazzetta-alternative-picture-type", SEGMENT,
    "cand-2401", "cand-3862", "employed-piazzetta-on-different-picture-type-to-show-his-talents",
    84, 84,
    "Completing the p.313 sentence, Haskell says Schulenburg employed Piazzetta on a different type of picture from dramatic action scenes painted by Pittoni, bringing out Piazzetta’s talents.",
    "action of the kind painted by Pittoni, and he therefore employed him on a totally different type of picture which brought out the very best of this painter’s talents.",
    "The opening clause is on p.313 L81 in st-chp10-p313-piazzetta-gifts-dramatic-action-fragment; 'he' is Schulenburg and 'him/this painter' is Piazzetta.",
    ["cand-2401", "cand-3862", "cand-3870"], True,
    {"continuation_of_statement_id": "st-chp10-p313-piazzetta-gifts-dramatic-action-fragment"},
)
add_statement(
    "st-chp10-p314-piazzetta-chief-agent-for-schulenburg", SEGMENT,
    "cand-3862", "cand-2401", "acted-as-schulenburgs-chief-agent-in-picture-purchases",
    84, 85,
    "Haskell says Piazzetta also acted as Schulenburg’s chief agent in buying interesting pictures on the market, usually Flemish.",
    "It was\nPiazzetta also who acted as Schulenburg’s chief agent in the purchase of interesting pictures on the market—usually Flemish.",
    "The sentence begins with 'It was' at the end of L84; 'usually' qualifies the market pictures. Footnote 1 awaits canonical note L288.",
    ["cand-3862", "cand-2401", "cand-9605", "cand-9616"], True,
    {"footnote_marker": 1, "pending_note_source_line": 288},
)
add_statement(
    "st-chp10-p314-schulenburg-dutch-flemish-taste", SEGMENT,
    "cand-2401", "cand-9605", "preferred-dutch-and-flemish-painting-and-patronized-related-venetian-artists",
    85, 86,
    "Haskell says Schulenburg particularly liked Dutch and Flemish painting and that this taste was reflected in the patronage he gave to certain Venetian artists.",
    "For the old Marshal was particularly fond of\nDutch and Flemish painting—a taste that was reflected in the type of patronage he afforded to Certain Venetian artists.",
    "The unnamed 'certain Venetian artists' are not expanded beyond those identified in the surrounding passage.",
    ["cand-2401", "cand-9605", "cand-9618"], False,
)
add_statement(
    "st-chp10-p314-schulenburg-owned-piazzetta-drawing", SEGMENT,
    "cand-2401", "cand-9596", "owned-drawing-by-piazzetta-described-as-flemish-animals-and-figures",
    86, 86,
    "Haskell says Schulenburg owned a Piazzetta drawing described as animals and figures in the Flemish manner.",
    "He owned a drawing by Piazzetta of ‘des animaux et figures à la flamande’",
    "The French phrase is an inventory description, not a supplied formal title.",
    ["cand-2401", "cand-3862", "cand-9596"], True,
)
add_statement(
    "st-chp10-p314-schulenburg-owned-nazari-nogari-heads", SEGMENT,
    "cand-2401", "cand-9597", "owned-about-twenty-heads-by-nazari-and-nogari",
    86, 87,
    "Haskell says Schulenburg owned about twenty heads of men and women by Bartolommeo Nazari and Giuseppe Nogari, in a genre that ultimately looked back to Rembrandt.",
    "and some twenty heads of men and women by Bartolommeo\nNazari and Giuseppe Nogari in a genre that ultimately looked back to Rembrandt.",
    "'Some twenty' is approximate; the text does not individuate the pictures.",
    ["cand-2401", "cand-9597", "cand-1727", "cand-1743", "cand-9606", "cand-3471"], True,
)
add_statement(
    "st-chp10-p314-schulenburg-flemish-taste-and-naturalistic-commission", SEGMENT,
    "cand-2401", "cand-9621", "flemish-taste-encouraged-schulenburg-to-commission-naturalistic-painting",
    87, 87,
    "Haskell links Schulenburg’s taste for Flemish art to his commissioning of naturalistic painting.",
    "It was this taste for Flemish art that encouraged the Marshal to commission naturalistic painting.",
    "This is Haskell’s causal interpretation; it does not identify a single commission.",
    ["cand-2401", "cand-9605", "cand-9621"], False,
)
add_statement(
    "st-chp10-p314-piazzetta-subject-pictures-for-schulenburg", SEGMENT,
    "cand-3862", "cand-9600", "painted-beggar-girl-and-pastoral-subjects-for-schulenburg",
    87, 88,
    "Haskell says Piazzetta painted for Schulenburg subjects including a beggar with a rosary, a girl with chickens, and especially two large pastorals or idylls now in Cologne and Chicago.",
    "Thus Piazzetta painted for him subjects such as a Beggar holding a Rosary, a\nGirl with a Basket of Chickens and, above all, the great pastorals or idylls, now in Cologne and Chicago.",
    "'Him' is Schulenburg. Cologne and Chicago are given as cities; exact institutions and individual work-to-city mapping are not supplied.",
    ["cand-3862", "cand-2401", "cand-9598", "cand-9599", "cand-9600", "cand-6300", "cand-4624"], True,
)
add_statement(
    "st-chp10-p314-meaning-of-pastorals-unclear", SEGMENT,
    "cand-3862", "cand-9600", "significance-of-the-pastoral-pictures-is-unclear",
    88, 88,
    "Haskell says the significance of the two pastorals or idylls is not clear.",
    "The significance of these pictures is not clear.",
    "'These pictures' refers to the preceding pastorals or idylls.",
    ["cand-3862", "cand-9600"], False,
)
add_statement(
    "st-chp10-p314-piazzetta-drew-schulenburg-inventory", SEGMENT,
    "cand-3862", "cand-9603", "drew-inventory-of-schulenburgs-collection",
    88, 88,
    "Haskell says Piazzetta drew up the inventory of Schulenburg’s collection.",
    "Piazzetta himself who drew up the inventory of Schulenburg’s collection",
    "The inventory is separately represented as an unidentified archive candidate.",
    ["cand-3862", "cand-2401", "cand-9603"], True,
)
add_statement(
    "st-chp10-p314-piazzetta-valued-pastorals-highly", SEGMENT,
    "cand-3862", "cand-9600", "valued-pastoral-pictures-highly",
    88, 88,
    "Haskell says Piazzetta valued the two pastorals highly.",
    "naturally valued them very highly",
    "'Naturally' frames this as Haskell’s inference from Piazzetta’s role in drawing up the inventory.",
    ["cand-3862", "cand-9600"], False,
)
add_statement(
    "st-chp10-p314-inventory-descriptions-of-two-pastorals", SEGMENT,
    "cand-9603", "cand-9600", "inventory-described-two-pastoral-pictures",
    88, 88,
    "Haskell quotes two descriptions from the inventory: a seated woman with a boy, grapes, dogs, a duck, and two men; and a woman with a parasol, servant, peasant, sleeping boy, and ox head.",
    "described them merely as ‘représentant une femme assise au naturel, avec un garçon entre les Jambes, un panier de raisins en main, des chiens, qui aperçoivent un canard dans l’eau et deux hommes en distance’ and ‘Une femme avec un parasol, une servante, un paysans, un garçon qui dort, et la tête d’un bœuf’",
    "These are descriptions rather than formal titles; they are not assigned to Cologne or Chicago or merged with Plate 54.",
    ["cand-9603", "cand-9600", "cand-9601", "cand-9602"], False,
)
add_statement(
    "st-chp10-p314-social-satire-interpretation-qualified", SEGMENT,
    "cand-9601", "cand-9617", "social-satire-reading-suggested-and-rejected-as-almost-certainly-wrong",
    88, 88,
    "An unnamed interpretation suggests that the first inventory-described picture hints at social satire; Haskell says this is almost certainly wrong.",
    "It has been suggested that the former picture contains a hint of social satire.2 While this is almost certainly wrong",
    "Attribution is to an unnamed suggester, and the author’s rejection remains probabilistic, not categorical. Footnote 2 is attached to this discussion and awaits L289.",
    ["cand-9601", "cand-9617"], False,
    {"footnote_marker": 2, "pending_note_source_line": 289},
)
add_statement(
    "st-chp10-p314-pastorals-probably-seen-as-realistic", SEGMENT,
    "cand-9600", "cand-9621", "probably-perceived-as-more-realistic-than-current-appreciation",
    88, 88,
    "Haskell says the pictures were probably taken to be more realistic than present appreciation of their poetic qualities allows.",
    "it does at least make the point that the pictures were probably taken to be far more ‘realistic’ than our present appreciation of their poetic qualities allows.",
    "Preserve 'probably'; this is Haskell’s interpretive inference.",
    ["cand-9600", "cand-9621"], False,
)
add_statement(
    "st-chp10-p314-rare-large-ordinary-figure-paintings", SEGMENT,
    "cand-3862", None, "no-comparable-large-ordinary-figure-pictures-in-eighteenth-century-venice-except-piazzetta",
    88, 88,
    "Haskell says no comparable-size pictures showing ordinary people were painted in eighteenth-century Venice except occasionally by Piazzetta.",
    "No pictures of comparable size showing ordinary people were painted during the eighteenth century in Venice except on occasion by Piazzetta himself.",
    "Retain the source’s exception and scope; this is a broad authorial generalization.",
    ["cand-3862", "cand-3401", "cand-9606"], False,
)
add_statement(
    "st-chp10-p314-naturalism-inferred-from-schulenburg-genre-gallery", SEGMENT,
    "cand-9600", "cand-9621", "pastorals-perhaps-appealed-to-schulenburgs-naturalistic-taste",
    88, 88,
    "Haskell suggests the two pastorals may have appealed to Schulenburg’s taste for naturalism because his gallery contained many other genre pictures.",
    "But perhaps the best reason for believing that they appealed to a taste for naturalism in the Marshal is that his gallery contained so many other genre pictures.",
    "'Perhaps' marks Haskell’s inference; the gallery is Schulenburg’s picture collection, whose type remains unresolved.",
    ["cand-2401", "cand-9600", "cand-9621", "cand-9606", "cand-9622"], False,
)
add_statement(
    "st-chp10-p314-schulenburg-owned-seven-ceruti-pictures", SEGMENT,
    "cand-2401", "cand-9604", "owned-seven-pictures-by-ceruti-including-beggars-and-animals",
    88, 88,
    "Haskell says Schulenburg owned seven pictures by Giacomo Ceruti, some depicting beggars and others animals.",
    "In particular he owned seven by the provincial realist Giacomo Ceruti, some of which portrayed beggars and others animals.",
    "Individual titles are not given. Footnote 3 awaits canonical note L290.",
    ["cand-2401", "cand-9604", "cand-0637"], True,
    {"footnote_marker": 3, "pending_note_source_line": 290},
)
add_statement(
    "st-chp10-p314-ceruti-works-would-make-collection-unique", SEGMENT,
    "cand-9604", "cand-9622", "ceruti-pictures-would-suffice-to-make-schulenburgs-collection-unique-in-venice",
    88, 88,
    "Haskell says the seven Ceruti pictures alone would suffice to make Schulenburg’s collection unique in Venice.",
    "These pictures alone would suffice to make Schulenburg’s collection unique in Venice",
    "'Would suffice' is a counterfactual/evaluative formulation, not a measured comparison.",
    ["cand-9604", "cand-2401", "cand-9622", "cand-3401"], False,
)
add_statement(
    "st-chp10-p314-hypothetical-gallery-visitor-effect", SEGMENT,
    "cand-9604", None, "hypothetical-mixed-display-would-seem-strange-to-visitors-raised-on-histories-and-mythologies",
    88, 88,
    "Haskell imagines the Ceruti pictures hanging with Piazzetta and Dutch/Flemish masters and says the effect would seem strange to visitors largely raised on histories and mythologies.",
    "and if we imagine them hanging in his palace along with his Piazzettas and his various Dutch and Flemish masters, we can see that the effect must have been strange enough to his visitors brought up so largely on histories and mythologies.",
    "The source explicitly frames this as an imagined display and inferred visitor response.",
    ["cand-2401", "cand-9604", "cand-9619", "cand-3862", "cand-9614", "cand-9571", "cand-9624"], False,
)
add_statement(
    "st-chp10-p314-schulenburg-patronized-view-and-landscape-painters", SEGMENT,
    "cand-2401", "cand-9607", "patronized-vedutisti-and-landscape-painters-like-smith",
    89, 89,
    "Haskell says Schulenburg, like Smith, patronized view painters and landscape painters.",
    "Like Smith, Schulenburg patronised the vedutisti and landscape painters",
    "'Like Smith' is a comparison, not a claim that their holdings were identical.",
    ["cand-2401", "cand-2440", "cand-9607"], True,
)
add_statement(
    "st-chp10-p314-schulenburg-owned-almost-no-canaletto", SEGMENT,
    "cand-2401", "cand-3738", "owned-nothing-by-canaletto-with-one-or-two-important-exceptions",
    89, 89,
    "Haskell says Schulenburg owned nothing by Canaletto except one or two important exceptions and explains that Canaletto’s close English relations made acquisition difficult for other Venice residents.",
    "but with one or two important exceptions he owned nothing by Canaletto whose close relations with the English made it difficult for other residents in Venice to acquire his work.",
    "The exceptions remain unenumerated; the stated reason is Haskell’s explanation, not a separately verified causal fact.",
    ["cand-2401", "cand-3738", "cand-9615", "cand-9620", "cand-3401"], True,
)
add_statement(
    "st-chp10-p314-schulenburg-owned-views-and-landscapes-by-six-artists", SEGMENT,
    "cand-2401", "cand-9608", "owned-view-and-landscape-pictures-by-marieschi-carlevarijs-cimaroli-joli-ricci-zuccarelli",
    90, 91,
    "Haskell says Schulenburg owned a view and several landscapes by Marieschi, plus pictures by Carlevarijs, Cimaroli, Joli, especially Marco Ricci and Zuccarelli.",
    "Instead he owned a view and a number of landscapes by Marieschi, and others by\nCarlevarijs, Cimaroli, Joli and especially Marco Ricci and Zuccarelli.",
    "The artist-specific groups are separate candidates; exact counts in footnote 4 await canonical note L291.",
    ["cand-2401", "cand-1546", "cand-0554", "cand-3748", "cand-1334", "cand-3831", "cand-2879", "cand-9608", "cand-9609", "cand-9610", "cand-9611", "cand-9612", "cand-9613"], True,
    {"footnote_marker": 4, "pending_note_source_line": 291},
)
add_statement(
    "st-chp10-p314-schulenburg-collection-less-traveller-attention", SEGMENT,
    "cand-9622", None, "collection-attracted-less-traveller-attention-than-smiths",
    92, 93,
    "Haskell says Schulenburg’s picture collection attracted less traveller attention than Smith’s collection.",
    "Schulenburg’s collection of pictures attracted less attention from travellers than did\nSmith’s",
    "The sentence continues with Haskell’s explanation on p.314 L93; Smith’s comparison refers to Joseph Smith’s collection, not to the person alone.",
    ["cand-9622", "cand-2440"], False,
)
add_statement(
    "st-chp10-p314-schulenburg-picture-shipping-to-estates-fragment", SEGMENT,
    "cand-2401", "cand-9623", "sent-picture-crates-to-estates-fragment",
    93, 93,
    "Haskell says Schulenburg was constantly sending crates of pictures back to his estates; the destination phrase continues at p.315.",
    "he was constantly sendingcrates of them back to his estates in",
    "The sentence continues at p.315 L95 with ‘Germany’. The OCR joins ‘sendingcrates’; the scan reads ‘sending crates’.",
    ["cand-2401", "cand-9622", "cand-9623", "cand-9625"], True,
    {"continuation_segment_id": "chp-10:10_CHP-10_sec_ii:l95-106", "ocr_print_correction": "sendingcrates -> sending crates"},
)

previous_statement_id = "st-chp10-p313-piazzetta-gifts-dramatic-action-fragment"
if any(row["statement_id"] == previous_statement_id for row in statements + new_statements):
    raise SystemExit("p.313 fragment statement id already exists")
previous_segment_text = "\n".join(source_lines[71:81])
previous_quote = "For the Marshal must have seen that Piazzetta’s gifts did notdie in scenes of dramatic"
if previous_quote not in previous_segment_text:
    raise SystemExit("p.313 continuation quote changed")
previous_statement = {
    "statement_id": previous_statement_id,
    "segment_id": PREVIOUS_SEGMENT,
    "subject_candidate_id": "cand-2401",
    "object_candidate_id": "cand-3862",
    "predicate": "schulenburg-recognized-piazzetta-not-suited-to-dramatic-action-fragment",
    "qualifiers": {
        "source_line_start": 81,
        "source_line_end": 81,
        "printed_page": 313,
        "pdf_physical_page": 46,
        "claim": "Haskell begins the explanation that Schulenburg recognized Piazzetta’s gifts did not lie in dramatic action; the sentence continues on p.314.",
        "speaker": "Haskell",
        "text_layer": "authorial claim",
        "qualification": "Incomplete source fragment only. It is not treated as a separate completed claim; p.314 L84 completes it.",
        "mentioned_candidate_ids": ["cand-2401", "cand-3862", "cand-3870"],
        "relation_candidate": False,
        "continuation_segment_id": SEGMENT,
        "continuation_statement_id": "st-chp10-p314-piazzetta-alternative-picture-type",
    },
    "original_quote": previous_quote,
    "origin": "book",
    "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
}
new_statements.append(previous_statement)

coverage[PREVIOUS_SEGMENT]["note"] = (
    "Read printed p.313 against CHP-10.pdf physical p.46. L73 completes the p.312 role sentence; the p.313 L81 "
    "fragment is now recorded as st-chp10-p313-piazzetta-gifts-dramatic-action-fragment and completed by "
    "st-chp10-p314-piazzetta-alternative-picture-type at p.314 L84. Coverage remains partial because footnotes "
    "1-4 await canonical notes L284-287. Print corrections recorded without changing S0: copyist and; of his; "
    "Carriera (OCR Camera); only rarely; did not lie; of history. The source and scan both read 'melodramas'."
)
coverage[SEGMENT].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L84-93",
    "note": (
        "Read printed p.314 against CHP-10.pdf physical p.47. The L84 opening completes the p.313 sentence; "
        "L84-91 records Piazzetta’s patronage/works, the collection’s genre and naturalist profile, and the view/landscape "
        "painters. The ending at L93 continues at p.315; its destination is not inferred. Footnotes 1-4 await canonical "
        "notes L288-291. Print corrections recorded without changing S0: Certain -> certain; sendingcrates -> sending crates."
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
candidate_id_set = {row["candidate_id"] for row in candidate_rows}
if any(row["candidate_id"] not in candidate_id_set for row in new_mentions):
    raise SystemExit("missing mention candidate foreign key")
if any(cid not in candidate_id_set for row in new_statements for cid in row["qualifiers"]["mentioned_candidate_ids"]):
    raise SystemExit("missing statement candidate reference")

print(f"p.314 preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("p.313 dramatic-action fragment linked to the p.314 continuation; p.313 coverage remains partial for notes")
print(f"coverage: p.314 reviewed/partial; next full-book cursor follows; totals {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(statement_rows)} statements")
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
