"""Controlled S2 migration for printed p.312; dry-run unless --apply."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_sec_ii.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_sec_ii.md"
SEGMENT = "chp-10:10_CHP-10_sec_ii:l17-32"
PREVIOUS_SEGMENT = "chp-10:10_CHP-10_sec_ii:l7-15"
EXPECTED_ASSET_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
EXPECTED_SEGMENT_SHA = "2957e600499466b5cd0525022e699abc6f6b92fcc9e2add47b5b836319d52dd0"
BACKUP_SUFFIX = ".bak-s2-chp10-p312-20261003"
WILL_STATEMENT_ID = "st-chp10-p311-will-asserted-authority-no-children"


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
parser.add_argument("--apply", action="store_true", help="write the reviewed S2 rows after making backups")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[16:32]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA:
    raise SystemExit("S2 source segment changed")
if not segment_lines or segment_lines[0] != "[Page 312]" or "Gian Antonio Guardi" not in segment_text:
    raise SystemExit("p.312 OCR segment does not match the reviewed source")

candidate_path, mention_path, statement_path, coverage_path = [TABLES / name for name in (
    "entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv"
)]
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
mention_ids = {row["mention_id"] for row in mentions}
statement_ids = {row["statement_id"] for row in statements}
coverage = {row["segment_id"]: row for row in coverage_rows}
maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if (len(candidates), maximum, len(mentions), len(statements)) != (9571, 9584, 19934, 8850):
    raise SystemExit(f"table state changed: candidates={len(candidates)}/{maximum}, mentions={len(mentions)}, statements={len(statements)}")
if (coverage[SEGMENT]["disposition"], coverage[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"p.312 coverage state changed: {coverage[SEGMENT]}")
if (coverage[PREVIOUS_SEGMENT]["disposition"], coverage[PREVIOUS_SEGMENT]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit(f"p.311 coverage state changed: {coverage[PREVIOUS_SEGMENT]}")
if any(row["segment_id"] == SEGMENT for row in mentions) or any(row["segment_id"] == SEGMENT for row in statements):
    raise SystemExit("p.312 already has S2 mention or statement rows")

EXISTING = {
    "schulenburg": "cand-2401", "piazzetta": "cand-1901", "piazzetta_schulenburg_works": "cand-1918",
    "nazari": "cand-1727", "nogari": "cand-1743", "ceruti": "cand-0637", "guardi": "cand-1245",
    "simonini": "cand-2435", "corradini": "cand-0849", "morlaiter": "cand-1703", "pitteri": "cand-1948",
    "canaletto": "cand-0498", "canaletto_corfu_view": "cand-0525", "corfu": "cand-8118",
    "rota": "cand-2287", "rota_purchase": "cand-2411", "ferdinando_carlo_gonzaga": "cand-1524",
    "padua": "cand-1803", "puget": "cand-2070", "puget_assumption": "cand-2071", "raphael": "cand-2098",
    "correggio": "cand-0852", "giorgione": "cand-1188", "giulio_romano": "cand-1194",
    "castiglione": "cand-0602", "castiglione_pictures": "cand-8632", "gonzaga_family": "cand-6669",
    "bertos": "cand-0368", "republic_venice": "cand-8838", "venice": "cand-2719",
    "statue": "cand-9581", "giotto": "cand-1191",
}
for key, cid in EXISTING.items():
    if cid not in candidate_ids:
        raise SystemExit(f"required candidate missing: {key}={cid}")
if WILL_STATEMENT_ID not in statement_ids:
    raise SystemExit("p.311 will statement missing")

NEW_CANDIDATES = [
    ("cand-9585", "Paintings of Schulenburg’s principal battles by Francesco Simonini", "work",
     "Haskell identifies the principal battles as a group of paintings by Simonini but gives no titles or locations.", 20),
    ("cand-9586", "Bertos bronzes in Schulenburg’s collection (group)", "work",
     "Haskell describes a large group of bronzes by Bertos among works Schulenburg bought from other collectors or sometimes commissioned; individual objects are not enumerated here.", 24),
    ("cand-9587", "Bertos’s equestrian portrait of Marshal Johann Matthias Schulenburg", "work",
     "Identified as one bronze included in the group by Bertos; the passage gives no title, date, or present location.", 24),
    ("cand-9588", "Marble modello by Antonio Corradini for Schulenburg’s statue on Corfu", "work",
     "Haskell says Schulenburg’s marbles by Corradini included a modello of the statue commissioned by the Republic for Corfu. Keep the modello distinct from the statue itself.", 25),
    ("cand-9589", "Unidentified painting claimed to be by Giotto in Schulenburg’s purchases", "work",
     "The work is unnamed and the attribution is explicitly reported as a claim; do not treat the attribution as accepted.", 25),
]
new_candidate_rows = []
for cid, name, kind, detail, line_no in NEW_CANDIDATES:
    if cid in candidate_ids:
        raise SystemExit(f"new candidate id already exists: {cid}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": cid, "canonical_name": name, "suggested_type": kind, "status": "open",
        "detail": detail, "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L{line_no}",
    })
    new_candidate_rows.append(row)
    candidate_ids.add(cid)

new_mentions = []
mention_counter = 0


def add_mention(line_no, surface, cid, note="", occurrence=1):
    global mention_counter
    line = source_lines[line_no - 1]
    at = -1
    search_from = 0
    for _ in range(occurrence):
        at = line.find(surface, search_from)
        if at < 0:
            raise SystemExit(f"mention text not found on L{line_no}: {surface!r}")
        search_from = at + len(surface)
    relative = sum(len(source_lines[i]) + 1 for i in range(16, line_no - 1)) + at
    mention_counter += 1
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p312-{mention_counter:04d}", "segment_id": SEGMENT,
        "candidate_id": cid, "surface_form": surface, "start_char": relative,
        "end_char": relative + len(surface), "note": note,
    })
    new_mentions.append(row)


# Names and explicit coreferences in the body; embedded page-footer OCR at L27-32 is
# deferred to the canonical chapter notes segment L279-283 to avoid double-counting.
add_mention(18, "his", EXISTING["schulenburg"], "coreference: Schulenburg")
add_mention(18, "Schulenburg", EXISTING["schulenburg"])
add_mention(18, "his", EXISTING["schulenburg"], "coreference: Schulenburg", occurrence=2)
add_mention(19, "Piazzetta", EXISTING["piazzetta"])
add_mention(19, "Piazzetta drew him several times (Plate 53a)", EXISTING["piazzetta_schulenburg_works"], "Piazzetta portrait group; Plate 53a is an internal cross-reference")
add_mention(19, "him", EXISTING["schulenburg"], "coreference: Schulenburg")
add_mention(19, "he", EXISTING["schulenburg"], "coreference: Schulenburg")
add_mention(19, "Bartolommeo Nazari", EXISTING["nazari"])
add_mention(20, "Giuseppe Nogari", EXISTING["nogari"])
add_mention(20, "Giacomo Ceruti", EXISTING["ceruti"])
add_mention(20, "Gian Antonio Guardi", EXISTING["guardi"])
add_mention(20, "Francesco Simonini", EXISTING["simonini"])
add_mention(20, "Corradini", EXISTING["corradini"])
add_mention(20, "Morlaiter", EXISTING["morlaiter"])
add_mention(20, "Pitteri", EXISTING["pitteri"])
add_mention(20, "His", EXISTING["schulenburg"], "coreference: Schulenburg")
add_mention(20, "His principal battles", "cand-9585", "unnamed group of paintings")
add_mention(20, "Simonini", EXISTING["simonini"])
add_mention(20, "he", EXISTING["schulenburg"], "coreference: Schulenburg")
add_mention(20, "he", EXISTING["schulenburg"], "coreference: Schulenburg", occurrence=2)
add_mention(20, "he", EXISTING["schulenburg"], "coreference: Schulenburg", occurrence=3)
add_mention(20, "his", EXISTING["schulenburg"], "coreference: Schulenburg")
add_mention(20, "whom", EXISTING["simonini"], "relative pronoun: Simonini")
add_mention(20, "him", EXISTING["schulenburg"], "coreference: Schulenburg")
add_mention(20, "Canaletto", EXISTING["canaletto"])
add_mention(20, "a view (probably taken from a print) of Corfu", EXISTING["canaletto_corfu_view"], "work candidate; print source is qualified as probable; OCR spelling checked against print")
add_mention(20, "Corfu", EXISTING["corfu"])
add_mention(20, "his", EXISTING["schulenburg"], "coreference: Schulenburg", occurrence=2)
add_mention(21, "Schulenburg’s", EXISTING["schulenburg"])
add_mention(21, "a large purchase of old master paintings and sculpture from a lawyer, Giovanni Battista Rota", EXISTING["rota_purchase"], "index candidate for the purchase episode")
add_mention(21, "Giovanni Battista Rota", EXISTING["rota"])
add_mention(21, "who", EXISTING["rota"], "relative pronoun: Rota")
add_mention(21, "the last Duke of Mantua", EXISTING["ferdinando_carlo_gonzaga"])
add_mention(22, "Ferdinando Carlo Gonzaga", EXISTING["ferdinando_carlo_gonzaga"])
add_mention(22, "whose", EXISTING["ferdinando_carlo_gonzaga"], "relative pronoun: Ferdinando Carlo Gonzaga")
add_mention(22, "his", EXISTING["ferdinando_carlo_gonzaga"], "coreference: Ferdinando Carlo Gonzaga")
add_mention(22, "his", EXISTING["ferdinando_carlo_gonzaga"], "coreference: Ferdinando Carlo Gonzaga", occurrence=2)
add_mention(22, "Padua", EXISTING["padua"])
add_mention(22, "Puget", EXISTING["puget"])
add_mention(22, "a bas-relief by Puget of the Assumption of the Virgin", EXISTING["puget_assumption"], "specific work indexed under Puget")
add_mention(22, "Raphael", EXISTING["raphael"])
add_mention(23, "Correggio", EXISTING["correggio"])
add_mention(23, "Giorgione", EXISTING["giorgione"])
add_mention(23, "Giulio Romano", EXISTING["giulio_romano"])
add_mention(23, "Castiglione", EXISTING["castiglione"])
add_mention(23, "the Gonzaga", EXISTING["gonzaga_family"])
add_mention(24, "Schulenburg", EXISTING["schulenburg"])
add_mention(24, "he", EXISTING["schulenburg"], "coreference: Schulenburg")
add_mention(24, "a large group of bronzes by Bertos", "cand-9586", "group of works")
add_mention(24, "Bertos", EXISTING["bertos"])
add_mention(24, "an equestrian portrait of himself", "cand-9587", "specific bronze within the Bertos group")
add_mention(24, "himself", EXISTING["schulenburg"], "coreference: Schulenburg")
add_mention(25, "Corradini", EXISTING["corradini"])
add_mention(25, "a modello of the statue of himself which the Republic had commissioned for the island of Corfu", "cand-9588", "modello kept distinct from the statue; OCR spelling checked against print")
add_mention(25, "himself", EXISTING["schulenburg"], "coreference: Schulenburg")
add_mention(25, "the Republic", EXISTING["republic_venice"])
add_mention(25, "the island of Corfu", EXISTING["corfu"], "OCR spelling checked against print")
add_mention(25, "his", EXISTING["schulenburg"], "coreference: Schulenburg")
add_mention(25, "a picture claimed to be by Giotto", "cand-9589", "unnamed work; attribution explicitly reported as a claim")
add_mention(25, "Giotto", EXISTING["giotto"])
add_mention(26, "His", EXISTING["schulenburg"], "coreference: Schulenburg")
add_mention(26, "he", EXISTING["schulenburg"], "coreference: Schulenburg")
add_mention(26, "whom", EXISTING["guardi"], "relative pronoun: Guardi")
add_mention(26, "Gian Antonio Guardi", EXISTING["guardi"])
add_mention(26, "him", EXISTING["schulenburg"], "coreference: Schulenburg")
add_mention(26, "Guardi", EXISTING["guardi"])
add_mention(26, "Schulenburg", EXISTING["schulenburg"])
add_mention(26, "him", EXISTING["schulenburg"], "coreference: Schulenburg", occurrence=2)


def source_quote(start_line, end_line=None, substring=None):
    if substring is not None:
        if substring not in segment_text:
            raise SystemExit(f"statement quote missing from segment: {substring!r}")
        return substring
    end_line = end_line or start_line
    return "\n".join(source_lines[start_line - 1:end_line])


def statement(statement_id, predicate, start_line, end_line, claim, mentioned, *, subject="cand-2401", obj=None,
              qualification="", relation_candidate=False, text_layer="authorial claim", footnote=None,
              footnote_pending=False, continuation_of=None, continues_to=None):
    if statement_id in statement_ids:
        raise SystemExit(f"statement id already exists: {statement_id}")
    qualifiers = {
        "source_line_start": start_line, "source_line_end": end_line, "printed_page": 312,
        "pdf_physical_page": 41, "claim": claim, "speaker": "Haskell", "text_layer": text_layer,
        "qualification": qualification, "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation_candidate,
    }
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
        qualifiers["footnote_text_pending"] = footnote_pending
    if continuation_of:
        qualifiers["continuation_of"] = continuation_of
    if continues_to:
        qualifiers["continuation"] = continues_to
    statement_ids.add(statement_id)
    return {
        "statement_id": statement_id, "segment_id": SEGMENT, "subject_candidate_id": subject,
        "object_candidate_id": obj, "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": source_quote(start_line, end_line), "origin": "book", "source_file": SOURCE_FILE,
    }


new_statements = [
    statement("st-chp10-p312-will-maintain-family-noble-status", "will_sought_to_maintain_family_noble_status", 18, 18,
              "Continuing the p.311 sentence, Haskell says Schulenburg’s 1740 will was determined to maintain the noble status of his family.",
              ["cand-2401"], qualification="This closes the p.311 fragment 'determined to maintain'. Footnote 1 remains pending in the canonical notes segment; the will has not been independently consulted.",
              text_layer="authorial interpretation of an archival document", footnote=1, footnote_pending=True,
              continuation_of=WILL_STATEMENT_ID),
    statement("st-chp10-p312-employed-artists-recorded-dropsical-features", "commissioned_employed_artists_to_record_portraits", 18, 18,
              "Haskell says that nearly all artists employed by Schulenburg were at one time or another commissioned to record his dropsical features.",
              ["cand-2401", "cand-1901", "cand-1727", "cand-1743", "cand-0637", "cand-1245", "cand-2435", "cand-0849", "cand-1703", "cand-1948"],
              qualification="The printed page carries marker 6, absent from this OCR line; footnote text is deferred to the canonical notes segment.",
              relation_candidate=True, footnote=6, footnote_pending=True),
    statement("st-chp10-p312-portrait-sculpture-engraving-artists", "portraits_sculptures_and_engraving_for_schulenburg", 19, 20,
              "Haskell lists Piazzetta, Nazari, Nogari, Ceruti, Guardi, Simonini, Corradini, Morlaiter, and Pitteri among artists who painted, sculpted, or engraved Schulenburg’s features.",
              ["cand-2401", "cand-1901", "cand-1918", "cand-1727", "cand-1743", "cand-0637", "cand-1245", "cand-2435", "cand-0849", "cand-1703", "cand-1948"],
              qualification="The sentence says 'many others' beyond the named artists; the list is not exhaustive. Printed marker 5 after the Piazzetta portrait reference is not present in OCR and awaits footnote linking.",
              relation_candidate=True, footnote=5, footnote_pending=True),
    statement("st-chp10-p312-simonini-battles-and-campaigns", "simonini_painted_battles_and_may_have_joined_campaigns", 20, 20,
              "Haskell says Simonini painted Schulenburg’s principal battles and apparently accompanied him on campaigns.",
              ["cand-2401", "cand-2435", "cand-9585"], qualification="Haskell marks Simonini’s presence on campaigns as apparent, not certain.",
              relation_candidate=True),
    statement("st-chp10-p312-canaletto-corfu-view-1726", "employed_canaletto_for_corfu_view", 20, 20,
              "Haskell says Schulenburg employed Canaletto in 1726 to paint a view of Corfu, probably taken from a print.",
              ["cand-2401", "cand-0498", "cand-0525", "cand-8118"], obj="cand-0525",
              qualification="The source explicitly qualifies the print as probable. Printed footnote 2 awaits linkage.",
              relation_candidate=True, footnote=2, footnote_pending=True,
              text_layer="authorial claim with an explicit probability qualifier"),
    statement("st-chp10-p312-royal-generosity-to-artists", "treated_artists_with_royal_generosity", 20, 20,
              "Haskell characterizes Schulenburg’s treatment of these artists as one of royal generosity.",
              ["cand-2401", "cand-1901", "cand-1727", "cand-1743", "cand-0637", "cand-1245", "cand-2435", "cand-0849", "cand-1703", "cand-1948"],
              qualification="The collective antecedent is the artist group just listed. Printed footnote 3 awaits linkage.",
              relation_candidate=True, footnote=3, footnote_pending=True),
    statement("st-chp10-p312-1724-purchase-from-rota", "purchased_paintings_and_sculpture_from_rota", 21, 21,
              "Haskell says Schulenburg’s collecting began suddenly in 1724 with a large purchase of old-master paintings and sculpture from lawyer and art dealer Giovanni Battista Rota.",
              ["cand-2401", "cand-2411", "cand-2287"], obj="cand-2287",
              qualification="Printed footnote 4 cites collection inventories and a later account; details await processing of the canonical notes segment.",
              relation_candidate=True, footnote=4, footnote_pending=True),
    statement("st-chp10-p312-works-from-gonzaga-gallery", "most-purchased-works-came-from-gonzaga-gallery", 21, 22,
              "Haskell says most of the works in this purchase came from the gallery of the last Duke of Mantua, Ferdinando Carlo Gonzaga.",
              ["cand-2401", "cand-2411", "cand-1524"], obj="cand-1524",
              qualification="The source says 'most', not all; the collection and the duke are not collapsed into the same object.",
              relation_candidate=True),
    statement("st-chp10-p312-gonzaga-belongings-venetian-market", "gonzaga-belongings-entered-venetian-market-after-exile-death", 22, 22,
              "Haskell says many of Ferdinando Carlo Gonzaga’s belongings appeared on the Venetian art market after his exile and death in Padua, following the Austrian occupation of his state in 1706.",
              ["cand-1524", "cand-2719", "cand-1803"], qualification="The passage does not identify the specific objects or name the occupied state separately.",
              relation_candidate=False),
    statement("st-chp10-p312-puget-relief-and-attributed-paintings", "collection-included-valued-relief-and-attributed-paintings", 22, 23,
              "Haskell says the sculptures included a highly valued Puget bas-relief of the Assumption of the Virgin, while pictures included works attributed to Raphael, Correggio, Giorgione, Giulio Romano, and Castiglione.",
              ["cand-2401", "cand-2070", "cand-2071", "cand-2098", "cand-0852", "cand-1188", "cand-1194", "cand-0602", "cand-8632"],
              qualification="The source’s wording 'attributed to' is retained; the individual paintings are unnamed. The specific Puget relief remains distinct from the attributed painting group.",
              relation_candidate=False),
    statement("st-chp10-p312-gonzaga-employed-romano-and-castiglione", "gonzaga-employed-romano-and-castiglione", 23, 23,
              "Haskell says Giulio Romano and Castiglione had both been much employed by the Gonzaga in earlier, more prosperous times.",
              ["cand-1194", "cand-0602", "cand-6669"], subject="cand-6669",
              qualification="The passage identifies the patronal group as 'the Gonzaga'; retain family/group scope and leave endpoint identity review to S3.",
              relation_candidate=True),
    statement("st-chp10-p312-contemporary-venetian-sculpture", "showed-interest-in-contemporary-venetian-sculpture", 24, 25,
              "Haskell contrasts Schulenburg with Smith by noting his interest in contemporary Venetian sculpture.",
              ["cand-2401"], qualification="This is a comparative characterization of taste, not a formal relation."),
    statement("st-chp10-p312-bertos-bronzes-and-equestrian-portrait", "collection-included-bertos-bronzes", 24, 24,
              "Haskell says a large group of Bertos bronzes among Schulenburg’s works included an equestrian portrait of Schulenburg himself.",
              ["cand-2401", "cand-0368", "cand-9586", "cand-9587"], obj="cand-9586",
              qualification="The sentence places the bronzes among works bought from collectors or sometimes commissioned; it does not assign one acquisition route to each bronze.",
              relation_candidate=True),
    statement("st-chp10-p312-corradini-modello-for-corfu-statue", "marbles-included-modello-for-venetian-commissioned-statue", 24, 25,
              "Haskell says Schulenburg’s marbles by Corradini included a modello for the statue of Schulenburg that the Republic had commissioned for Corfu.",
              ["cand-2401", "cand-0849", "cand-9588", "cand-9581", "cand-8838", "cand-8118"], obj="cand-9588",
              qualification="The modello is a distinct work from the statue identified on p.311; the page does not say when or where the modello was made.",
              relation_candidate=True),
    statement("st-chp10-p312-conventional-old-master-taste-giotto-claim", "old-master-taste-conventional-except-claimed-giotto-picture", 25, 25,
              "Haskell describes Schulenburg’s old-master taste as conventional as far as the purchase list shows, except for one picture claimed to be by Giotto.",
              ["cand-2401", "cand-1191", "cand-9589"], obj="cand-9589",
              qualification="Both the limitation to the purchase list and the reported attribution claim are retained."),
    statement("st-chp10-p312-guardi-first-contact-and-tenure", "first-contemporary-artist-contact-seems-to-be-guardi", 26, 26,
              "Haskell says Schulenburg’s first contact with a contemporary artist seems to have been Gian Antonio Guardi, who worked for him for about fifteen years from before 1730 until 1745.",
              ["cand-2401", "cand-1245"], obj="cand-1245",
              qualification="'Seems' and 'some fifteen years' are retained; the date range begins 'before 1730' and is not converted into a precise start year.",
              relation_candidate=True),
    statement("st-chp10-p312-guardi-salary-and-role-fragment", "guardi-received-monthly-salary-and-role-description-fragment", 26, 26,
              "Haskell says Guardi received a monthly salary from Schulenburg and begins to contrast his role with that of an original painter.",
              ["cand-2401", "cand-1245"], subject="cand-1245", obj="cand-2401",
              qualification="The sentence stops at 'not so much as an' and continues at p.313 L73; do not supply the missing role description until that segment is processed.",
              relation_candidate=True, continues_to="chp-10:10_CHP-10_sec_ii:l72-81"),
]

for row in new_mentions:
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"mention points to missing candidate: {row['mention_id']} -> {row['candidate_id']}")
for row in new_statements:
    if row["subject_candidate_id"] and row["subject_candidate_id"] not in candidate_ids:
        raise SystemExit(f"statement subject candidate missing: {row['statement_id']}")
    if row["object_candidate_id"] and row["object_candidate_id"] not in candidate_ids:
        raise SystemExit(f"statement object candidate missing: {row['statement_id']}")
    if any(cid not in candidate_ids for cid in row["qualifiers"]["mentioned_candidate_ids"]):
        raise SystemExit(f"statement mentions missing candidate: {row['statement_id']}")
    source_text = "\n".join(source_lines[row["qualifiers"]["source_line_start"] - 1:row["qualifiers"]["source_line_end"]])
    normalize = lambda value: " ".join(value.split())
    if normalize(row["original_quote"]) not in normalize(source_text):
        raise SystemExit(f"statement quote does not match cited source: {row['statement_id']}")

for row in new_mentions:
    start, end = int(row["start_char"]), int(row["end_char"])
    if segment_text[start:end] != row["surface_form"]:
        raise SystemExit(f"mention span mismatch: {row['mention_id']}")
new_intervals = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in new_mentions)
for index, left in enumerate(new_intervals):
    for right in new_intervals[index + 1:]:
        if right[0] >= left[1]:
            break
        exact_duplicate = left[:2] == right[:2]
        strictly_nested = ((left[0] <= right[0] and right[1] <= left[1]) or
                           (right[0] <= left[0] and left[1] <= right[1]))
        if exact_duplicate or not strictly_nested:
            raise SystemExit(f"duplicate or crossing mention spans: {left[2]} and {right[2]}")

previous_will = next(row for row in statements if row["statement_id"] == WILL_STATEMENT_ID)
previous_will["qualifiers"]["qualification"] = (
    "Its sentence continuation is now located and closed at p.312 L18; the continuation records the intended preservation "
    "of family nobility. The will itself has not been independently consulted, and p.311 footnotes remain pending."
)
previous_will["qualifiers"]["continuation"] = "closed by st-chp10-p312-will-maintain-family-noble-status at p.312 L18"

previous_coverage = coverage[PREVIOUS_SEGMENT]
previous_coverage["note"] = previous_coverage["note"].rstrip() + (
    " Printed p.311 sentence now closes at p.312 L18. Footnotes 1-6 remain pending in canonical note block L274-278; "
    "print confirms a note 6 marker after 'clapt', and the OCR joins footnotes 5 and 6 on L278."
)
current_coverage = coverage[SEGMENT]
current_coverage.update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L18-26",
    "note": (
        "Printed p.312 body L18-26 read against CHP-10.pdf physical p.41. L18 closes the p.311 will sentence; "
        "L26 ends 'not so much as an' and continues at p.313 L73 after Plates 53-56. Printed footnotes 1-6 are confirmed; "
        "L27-32 contains only duplicated/partial page-footer OCR, so note content will be anchored once in canonical "
        "notes segment L273-349 (p.312 notes at L279-283) and not counted twice. Print supplies note markers 5 and 6 missing from body OCR."
    ),
})

candidate_rows = candidates + new_candidate_rows
mention_rows = mentions + new_mentions
statement_rows = statements + new_statements
if len({row["mention_id"] for row in mention_rows}) != len(mention_rows):
    raise SystemExit("duplicate mention id")
if len({row["statement_id"] for row in statement_rows}) != len(statement_rows):
    raise SystemExit("duplicate statement id")
if len({row["candidate_id"] for row in candidate_rows}) != len(candidate_rows):
    raise SystemExit("duplicate candidate id")

print(f"p.312 dry-run/apply preview: +{len(new_candidate_rows)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("coverage: p.311 stays partial pending its notes; p.312 is reviewed/partial pending p.313 continuation and canonical note links")
print(f"resulting totals: candidates={len(candidate_rows)}, mentions={len(mention_rows)}, statements={len(statement_rows)}")
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
