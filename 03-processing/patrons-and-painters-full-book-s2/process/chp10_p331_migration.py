"""Controlled S2 migration for printed p.331; defaults to dry-run."""
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
PREVIOUS = "chp-10:10_CHP-10_sec_ii:l258-267"
BODY = "chp-10:10_CHP-10_sec_ii:l269-271"
NOTES = "chp-10:10_CHP-10_sec_ii:l273-349"
MARKDOWN_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
BODY_SHA = "4a5e13dba0a9c6f617b62b0a8c3b82d7cd38846fb568e307e86e331adc1f5794"
BACKUP_SUFFIX = ".bak-s2-chp10-p331-20261003"
OPEN_STATEMENT = "st-chp10-p330-venetian-exhibition-sites-open"
CONTINUATION_STATEMENT = "st-chp10-p331-piazza-display-completion"


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
parser.add_argument("--apply", action="store_true", help="write reviewed p.331 rows after making recovery copies")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != MARKDOWN_SHA:
    raise SystemExit("canonical source Markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body_lines = {n: source_lines[n - 1] for n in range(269, 272)}
segment_text = "\n".join(body_lines.values())
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != BODY_SHA:
    raise SystemExit("registered source segment changed: p.331")
if body_lines[269] != "[Page 331]" or not body_lines[270].endswith("could be discussed. '") or not body_lines[271].endswith("proved very happy."):
    raise SystemExit("p.331 source boundaries changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
mention_ids = {row["mention_id"] for row in mentions}
statement_ids = {row["statement_id"] for row in statements}
coverage = {row["segment_id"]: row for row in coverage_rows}
state = (
    len(candidates),
    max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions),
    len(statements),
)
if state != (9854, 9867, 20929, 9303):
    raise SystemExit(f"unexpected table pre-state: {state}")
if PREVIOUS not in coverage or BODY not in coverage or NOTES not in coverage:
    raise SystemExit("required coverage row missing")
if (coverage[PREVIOUS]["disposition"], coverage[PREVIOUS]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.330 is not reviewed/partial")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.331 is not queued/pending")
if (coverage[NOTES]["disposition"], coverage[NOTES]["migration_status"], coverage[NOTES]["source_line_ranges"]) != ("reviewed", "partial", "L325-349"):
    raise SystemExit("consolidated notes are not in the expected partial state")
if any(row["segment_id"] == BODY for row in mentions) or any(row["segment_id"] == BODY for row in statements):
    raise SystemExit("p.331 body rows already exist")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
for cid in ("cand-0005", "cand-0041", "cand-0137", "cand-0140", "cand-1547", "cand-2719", "cand-4056", "cand-8129", "cand-8587", "cand-8588", "cand-8728", "cand-9866", "cand-9856"):
    if cid not in candidate_by_id:
        raise SystemExit(f"expected existing candidate missing: {cid}")
if candidate_by_id["cand-8129"]["canonical_name"] != "Senate of Venice in Haskell's account":
    raise SystemExit("expected Senate of Venice candidate not found")
if candidate_by_id["cand-8728"]["canonical_name"] != "Doge of Venice as an institutional office in the Pietà refuge account":
    raise SystemExit("expected Doge of Venice office candidate not found")

new_candidates = []


def add_candidate(cid, name, kind, detail, line):
    if cid in candidate_ids or any(row["candidate_id"] == cid for row in new_candidates):
        raise SystemExit(f"candidate id already exists: {cid}")
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


add_candidate("cand-9868", "Church of S. Geminiano (Venice; landmark adjoining the p.330 display site)", "place", "Named as the landmark adjoining the Piazza S. Marco exhibition location. The passage does not say that painters displayed work inside the church.", 270)
add_candidate("cand-9869", "Francesco Algarotti's letter to Mariette on the S. Rocco exhibition (by 1751)", "archive", "Haskell reports that Algarotti wrote to Pierre-Jean Mariette by 1751 and quotes a comparison of the S. Rocco exhibition with the Paris Salon. The letter is not independently consulted and no exact date or title is supplied.", 270)
add_candidate("cand-9870", "Salon de Paris (comparison with the S. Rocco exhibition)", "event", "Recurring Paris exhibition invoked by Algarotti and Haskell as a comparison; this candidate records the source's comparison, not equivalence between the institutions or events.", 270)
add_candidate("cand-9871", "Annual Doge and Senate procession to S. Rocco on 16 August", "event", "Recurring civic procession to the church named as the probable informal origin of the annual artists' exhibition. Preserve Haskell's 'probably' and do not assert a definitive origin.", 270)
add_candidate("cand-9872", "Venetian Academy annual exhibition series in the Piazzetta (begun 1777; discontinued by 1787)", "event", "Official annual exhibition arrangement initiated in 1777 and discontinued by 1787 after complaints and crippling cost. The text does not give the exact final exhibition year; individual displays are not separately identified here.", 271)
add_candidate("cand-9873", "Piazzetta (Venice; site of the Academy exhibition stand)", "place", "Public square location named for the Venetian Academy's annual exhibition stand. Keep distinct from Giovanni Battista Piazzetta, the painter.", 271)
add_candidate("cand-9874", "Venetian State as the source of art interference in Haskell's p.331 account", "institution", "The passage attributes the ending of State interference in the arts to the discontinuation of the Academy shows. Preserve Haskell's evaluative framing; identity with other Republic of Venice candidates remains for S3.", 271)
add_candidate("cand-9875", "Unnamed nobles requesting annual Academy exhibitions in 1777", "term", "An unnamed group said to have asked the Academy's members to display works in the Piazzetta; individual identities and membership are not supplied.", 271)

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
new_mentions = []


def add_mention(line_no, surface, cid, note="", occurrence=0):
    if cid not in all_candidate_ids:
        raise SystemExit(f"unknown candidate for mention: {surface!r} {cid}")
    line = body_lines[line_no]
    starts = []
    cursor = 0
    while True:
        at = line.find(surface, cursor)
        if at < 0:
            break
        starts.append(at)
        cursor = at + 1
    if occurrence >= len(starts):
        raise SystemExit(f"mention text missing at L{line_no}: {surface!r} occurrence {occurrence}")
    start = sum(len(body_lines[n]) + 1 for n in range(269, line_no)) + starts[occurrence]
    if segment_text[start:start + len(surface)] != surface:
        raise SystemExit(f"mention span mismatch at L{line_no}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p331-{len(new_mentions) + 1:04d}",
        "segment_id": BODY,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    new_mentions.append(row)


add_mention(270, "church of S. Geminiano", "cand-9868")
add_mention(270, "painters", "cand-9866", "Generic painters; no individual artist is named.")
add_mention(270, "exhibitions", "cand-8587")
add_mention(270, "the Scuola di S. Rocco", "cand-8588")
add_mention(270, "the processions", "cand-9871")
add_mention(270, "the Doge", "cand-8728")
add_mention(270, "Senate", "cand-8129")
add_mention(270, "Plate 56", "cand-4056", "Cross-reference to the existing work candidate for Marieschi's picture exhibition at S. Rocco.")
add_mention(270, "artists", "cand-9866", "Annual participants are unnamed; this does not define an organization.")
add_mention(270, "Francesco Algarotti", "cand-0041")
add_mention(270, "Mariette", "cand-1547")
add_mention(270, "the exhibition", "cand-8587", occurrence=0)
add_mention(270, "the Salon in Paris", "cand-9870")
add_mention(270, "these exhibitions", "cand-8587")
add_mention(270, "the State", "cand-9874")
add_mention(271, "a number of nobles", "cand-9875")
add_mention(271, "the Academy", "cand-0005", occurrence=0)
add_mention(271, "a stand in the Piazzetta", "cand-9873")
add_mention(271, "a much more official type of exhibition", "cand-9872")
add_mention(271, "The artists", "cand-9866")
add_mention(271, "all the expenses", "cand-9872", "Costs are described as borne by the exhibiting artists; no amount is given.")
add_mention(271, "the Academy", "cand-0005", occurrence=1)
add_mention(271, "the shows", "cand-9872")
add_mention(271, "State interference in the arts", "cand-9874")

new_mentions.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
for left, right in zip(new_mentions, new_mentions[1:]):
    if int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping mention spans: {left['mention_id']} and {right['mention_id']}")
if any(row["mention_id"] in mention_ids for row in new_mentions):
    raise SystemExit("mention id already exists")

new_statements = []


def add_statement(sid, subject, obj, predicate, line_no, claim, quote, qualification, mentioned,
                  *, speaker="Haskell", layer="authorial narrative", extra=None):
    if sid in statement_ids or any(row["statement_id"] == sid for row in new_statements):
        raise SystemExit(f"statement id already exists: {sid}")
    if quote not in segment_text:
        raise SystemExit(f"statement quote is not anchored: {sid}")
    if any(cid not in all_candidate_ids for cid in mentioned):
        raise SystemExit(f"missing mentioned candidate in {sid}")
    for cid in (subject, obj):
        if cid and cid not in all_candidate_ids:
            raise SystemExit(f"missing endpoint candidate in {sid}: {cid}")
    qualifiers = {
        "source_line_start": line_no,
        "source_line_end": line_no,
        "printed_page": 331,
        "pdf_physical_page": 64,
        "claim": claim,
        "speaker": speaker,
        "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
    }
    if extra:
        qualifiers.update(extra)
    new_statements.append({
        "statement_id": sid,
        "segment_id": BODY,
        "subject_candidate_id": subject or None,
        "object_candidate_id": obj or None,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
    })


first_quote = "the church of S. Geminiano, painters sometimes chose to show their work to the public in a thoroughly casual way when other means were not available."
add_statement(
    CONTINUATION_STATEMENT, "cand-0137", "cand-9856", "casually_displayed_art_at_piazza_s_marco_site",
    270,
    "Haskell completes the p.330 location description: the Piazza S. Marco site adjoins the Church of S. Geminiano, where painters sometimes chose to show work publicly in a casual manner when other means were unavailable.",
    first_quote,
    "This closes the sentence begun on p.330 about the Piazza S. Marco site. The church is an adjoining landmark; the text does not say the display was inside it or identify an organized exhibition or particular painter.",
    ["cand-0137", "cand-9856", "cand-9868", "cand-9866"],
    extra={
        "continuation_from_segment_id": PREVIOUS,
        "continuation_from_statement_id": OPEN_STATEMENT,
        "continuation_prefix": "By the early years of the eighteenth century there were two spots in the city which were given over to art exhibitions. In the Piazza S. Marco, by the left-hand projecting wing of the Procuratie Nuove adjoining",
        "continuation_status": "closed",
        "relation_candidate": True,
    },
)
add_statement(
    "st-chp10-p331-s-rocco-exhibition-origin", "cand-8587", "cand-9871", "probably_grew_from_annual_processions",
    270,
    "Haskell says the more systematic S. Rocco exhibitions probably developed informally from the annual 16 August processions of the Doge and Senate to the church.",
    "But there were also far more systematic exhibitions at the Scuola di S. Rocco which probably grew up quite informally from the processions which the Doge and Senate made to the church each 16 August (Plate 56).",
    "The origin is explicitly probable, not established. The 16 August procession and the exhibition remain distinct events.",
    ["cand-8587", "cand-8588", "cand-9871", "cand-8728", "cand-8129", "cand-4056"],
    extra={"relation_candidate": True},
)
add_statement(
    "st-chp10-p331-s-rocco-annual-participation", "cand-8587", "cand-9866", "artists_participated_each_year",
    270,
    "Haskell describes the occasion as fixed and says a number of artists participated every year.",
    "The occasion was a fixed one and every year a number of artists took part.",
    "No participants are individually named and no exact annual count is supplied.",
    ["cand-8587", "cand-9866"],
    extra={"relation_candidate": True},
)
add_statement(
    "st-chp10-p331-algarotti-letter-and-salon-comparison", "cand-9869", "cand-9870", "compared_s_rocco_exhibition_to_paris_salon",
    270,
    "Haskell reports that by 1751 Francesco Algarotti could write to Mariette describing the S. Rocco exhibition as, in some ways, the tribunal of Venetian painting like the Paris Salon.",
    "By 1751 Francesco Algarotti could write to Mariette that the exhibition was ‘in some ways the tribunal of our painting like the Salon in Paris’.",
    "This is Haskell's report and quotation of a letter; the letter itself is not independently consulted. 'Could write by 1751' is retained without assigning an exact letter date.",
    ["cand-9869", "cand-0041", "cand-1547", "cand-8587", "cand-9870"],
    layer="reported correspondence and quotation",
    extra={"relation_candidate": True},
)
add_statement(
    "st-chp10-p331-s-rocco-not-salon-in-scale", "cand-8587", "cand-9870", "did_not_match_paris_salon_scale_or_attention",
    270,
    "Haskell says the S. Rocco showings never matched the Salon in Paris in organizational complexity or public attention.",
    "In fact, however, the S. Rocco showings never approached the Salon in complexity of organisation or the attention they attracted.",
    "A comparative assessment by Haskell; the comparison does not make the two exhibition systems equivalent.",
    ["cand-8587", "cand-9870"],
)
add_statement(
    "st-chp10-p331-limited-surviving-criticism", "cand-8587", None, "little_written_criticism_survives",
    270,
    "Haskell says scarcely any written criticism of the S. Rocco showings has survived and that their contemporary importance is difficult to estimate.",
    "Scarcely any written criticism has survived, and it is difficult to estimate how seriously they were taken.",
    "The passage marks the limits of surviving evidence; it does not establish that no criticism or contemporary discussion existed.",
    ["cand-8587"],
)
add_statement(
    "st-chp10-p331-exhibitions-as-public-forum", "cand-8587", "cand-9874", "brought_artists_and_public_together_and_enabled_value_debate",
    270,
    "Haskell argues that the exhibitions helped bring artists and the public together and offered a forum for discussing values beyond those established by the State and aristocracy.",
    "None the less, in a smaller way than in Paris but for the same reasons, these exhibitions did help to bring artist and public together, and did provide a forum where values other than those established by the State and the aristocracy could be discussed. '",
    "This is Haskell's interpretation of their social function. The OCR's stray final apostrophe is absent from the printed page.",
    ["cand-8587", "cand-9870", "cand-9874"],
    extra={"relation_candidate": True, "ocr_corrections": [{"source_line": 270, "ocr": "discussed. '", "print": "discussed."}]},
)
add_statement(
    "st-chp10-p331-academy-exhibition-series-started-1777", "cand-9875", "cand-9872", "requested_annual_academy_exhibitions_in_piazzetta",
    271,
    "Haskell says that in 1777 a group of nobles asked Academy members to exhibit their work each year at a stand in the Piazzetta.",
    "In 1777 a much more official type of exhibition was organised when a number of nobles asked the members of the Academy to display their work each year at a stand in the Piazzetta.",
    "The nobles are unnamed; this is a request followed by an exhibition arrangement, not proof that every Academy member participated.",
    ["cand-9875", "cand-9872", "cand-0005", "cand-9873"],
    extra={"relation_candidate": True},
)
add_statement(
    "st-chp10-p331-academy-exhibitors-bore-cost", "cand-9872", "cand-9866", "artists_bore_heavy_exhibition_expenses",
    271,
    "Haskell says the artists viewed the arrangements without enthusiasm because they had to meet the heavy expenses themselves.",
    "The artists viewed the arrangements without enthusiasm as they themselves were required to meet all the expenses, which were heavy.",
    "No amount or allocation among individual artists is given.",
    ["cand-9872", "cand-9866"],
    extra={"relation_candidate": True},
)
add_statement(
    "st-chp10-p331-academy-borrowed-pictures", "cand-0005", "cand-9872", "borrowed_pictures_to_complete_exhibition_numbers",
    271,
    "Haskell says that many artists lacked pictures for exhibition and the Academy resorted to loans to reach the required number.",
    "Many of them did not have pictures available for exhibition, and the Academy had to resort to loans to make up the required numbers.",
    "The lenders, number of pictures, and individual works are not identified.",
    ["cand-0005", "cand-9872", "cand-9866"],
    extra={"relation_candidate": True},
)
add_statement(
    "st-chp10-p331-academy-shows-ended-1787", "cand-9872", None, "discontinued_by_1787_after_complaints_and_cost",
    271,
    "Haskell says complaints were frequent, costs had become crippling by 1787, and the shows were discontinued.",
    "Complaints were frequently made and by 1787 the cost had become crippling and the shows were discontinued.",
    "The text supplies a terminus by 1787, not an exact closure date.",
    ["cand-9872"],
)
add_statement(
    "st-chp10-p331-state-interference-evaluation", "cand-9874", "cand-9872", "state_interference_ended_with_academy_shows",
    271,
    "Haskell concludes that discontinuation ended State interference in the arts and judges that interference had never been very successful.",
    "Thus ended State interference in the arts which had at no time proved very happy.",
    "This is Haskell's evaluative conclusion. 'Very happy' is retained as the author's wording, not converted into a broader judgment about all state policy.",
    ["cand-9874", "cand-9872"],
    extra={"relation_candidate": True},
)

if any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("statement id already exists")
all_statement_ids = statement_ids | {row["statement_id"] for row in new_statements}
if OPEN_STATEMENT not in all_statement_ids:
    raise SystemExit("p.330 open continuation statement missing")
previous_statement = next(row for row in statements if row["statement_id"] == OPEN_STATEMENT)
if previous_statement.get("qualifiers", {}).get("continuation_status") != "open":
    raise SystemExit("p.330 Piazza continuation is not open")
previous_statement["qualifiers"].update({
    "continuation_status": "closed",
    "continuation_closed_by_segment_id": BODY,
    "continuation_closed_by_statement_id": CONTINUATION_STATEMENT,
})

candidate_rows = candidates + new_candidates
mention_rows = mentions + new_mentions
statement_rows = statements + new_statements
coverage_rows[coverage_rows.index(coverage[PREVIOUS])].update({
    "migration_status": "complete",
    "source_line_ranges": "L258-267",
    "note": "p.330 exhibition-location sentence closes at p.331 L270; p.330 footnote 4 items are linked to the consolidated notes and body quotations.",
})
coverage_rows[coverage_rows.index(coverage[BODY])].update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L269-271",
    "note": "p.331 body complete; p.330 Piazza description closes at L270. No page-specific footnotes; the final OCR apostrophe after 'discussed.' is corrected in S2 only.",
})
candidate_rows.sort(key=lambda row: row["candidate_id"])
mention_rows.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
statement_rows.sort(key=lambda row: row["statement_id"])
coverage_rows.sort(key=lambda row: row["segment_id"])

print(f"p.331 preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("coverage: p.330 complete; p.331 complete; consolidated notes remain partial at L325-349")
print("S2 boundary: continuation closed; 1777-1787 Academy exhibitions kept distinct from the annual S. Rocco event")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

targets = [candidate_path, mention_path, statement_path, coverage_path]
for path in targets:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"recovery copy already exists: {backup.name}")
for path in targets:
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
write_csv(candidate_path, candidate_fields, candidate_rows)
write_csv(mention_path, mention_fields, mention_rows)
write_jsonl(statement_path, statement_rows)
write_csv(coverage_path, coverage_fields, coverage_rows)
print("applied; four recovery copies saved")
