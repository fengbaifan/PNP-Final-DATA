"""Controlled S2 migration for printed p.329 and consolidated notes L343-345."""
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
PREVIOUS = "chp-10:10_CHP-10_sec_ii:l241-246"
BODY = "chp-10:10_CHP-10_sec_ii:l248-256"
NEXT = "chp-10:10_CHP-10_sec_ii:l258-267"
NOTES = "chp-10:10_CHP-10_sec_ii:l273-349"
MARKDOWN_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
BODY_SHA = "48eaa06ae40f6f2e7fb9e5f16db088ec34a8b2f6972e972d877ec3d475303ac5"
NOTE_SHA = "9f976048bc1289516d1d212d39cdc812bdd5151a16d7ce292e5a58a754c575fb"
BACKUP_SUFFIX = ".bak-s2-chp10-p329-20261003"


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
parser.add_argument("--apply", action="store_true", help="write reviewed p.329 rows after making recovery copies")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != MARKDOWN_SHA:
    raise SystemExit("canonical source Markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body_lines = {n: source_lines[n - 1] for n in range(248, 257)}
note_lines = {n: source_lines[n - 1] for n in range(273, 350)}
segment_text = {
    BODY: "\n".join(body_lines.values()),
    NOTES: "\n".join(note_lines.values()),
}
if hashlib.sha256(segment_text[BODY].encode("utf-8")).hexdigest() != BODY_SHA:
    raise SystemExit("registered source segment changed: p.329")
note_slice = "\n".join(note_lines[n] for n in range(343, 346))
if hashlib.sha256(note_slice.encode("utf-8")).hexdigest() != NOTE_SHA:
    raise SystemExit("registered note range changed: p.329 notes L343-345")
if body_lines[248] != "[Page 329]" or not body_lines[256].startswith("Very shortly after the institution of the Academy"):
    raise SystemExit("p.329 source boundaries changed")
if not all(token in note_slice for token in ("Della Pittura Veneziana", "Agostino Sagredo", "Fogolari")):
    raise SystemExit("p.329 footnote range L343-345 changed")

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
if state != (9823, 9836, 20845, 9266):
    raise SystemExit(f"unexpected table pre-state: {state}")
for sid in (PREVIOUS, BODY, NEXT, NOTES):
    if sid not in coverage:
        raise SystemExit(f"required coverage row missing: {sid}")
if (coverage[PREVIOUS]["disposition"], coverage[PREVIOUS]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.328 is not reviewed/partial")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.329 is not queued/pending")
if (coverage[NEXT]["disposition"], coverage[NEXT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.330 is not queued/pending")
if (coverage[NOTES]["disposition"], coverage[NOTES]["migration_status"], coverage[NOTES]["source_line_ranges"]) != ("reviewed", "partial", "L325-342"):
    raise SystemExit("consolidated notes are not in the expected p.324-328 partial state")
if any(row["segment_id"] == BODY for row in mentions) or any(row["segment_id"] == BODY for row in statements):
    raise SystemExit("p.329 body rows already exist")
if any(row["segment_id"] == NOTES and 343 <= int(row.get("qualifiers", {}).get("source_line_start", 0)) <= 345 for row in statements):
    raise SystemExit("p.329 footnote statements already exist")

new_candidates = []


def add_candidate(cid, name, kind, detail, segment, line):
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
        "candidate_source_ref": f"{segment}#L{line}",
    })
    new_candidates.append(row)


# Citation candidates are resolved only to titles present in the book's local bibliography.
add_candidate("cand-9837", "Della Pittura Veneziana (Venezia, 1771)", "archive", "Cited by Haskell at p.329 n.1 as the source for Zanetti's view that painting is one of the useful arts. The local bibliography attributes the 1771 title to A. M. Zanetti; the work was not independently consulted.", NOTES, 343)
add_candidate("cand-9838", "Relazione per le riforme (18 August 1772)", "archive", "Report cited in p.329 n.2 and quoted through Agostino Sagredo, 1857, p.208. The page image reads riforme; the OCR has risorme. The report was not independently consulted.", NOTES, 344)
add_candidate("cand-9839", "Agostino Sagredo", "person", "Named in p.329 n.2 as the intermediary for the 1772 report quotation. The local bibliography lists A. Sagredo's 1857 publication; identity is not externally aligned.", NOTES, 344)
add_candidate("cand-9840", "Sulle consorterie delle Arti edificatorie in Venezia (Venezia, 1857)", "archive", "The local bibliography identifies the 1857 Sagredo work cited in p.329 n.2. The publication was not independently consulted.", NOTES, 344)
add_candidate("cand-9841", "Elena Bassi", "person", "Identified from the bibliography entry matching p.329 n.3's Bassi, 1941 citation; identity is not externally aligned.", NOTES, 345)
add_candidate("cand-9842", "La Regia Accademia di Belle Arti di Venezia (Firenze, 1941)", "archive", "The local bibliography identifies Bassi's 1941 work cited in p.329 n.3. The publication was not independently consulted.", NOTES, 345)
add_candidate("cand-9843", "Gino Fogolari", "person", "Named in p.329 n.3; the local bibliography includes several works by Fogolari, and the 1913 Academy article is the matching citation. Identity is not externally aligned.", NOTES, 345)
add_candidate("cand-9844", "L’Accademia Veneziana di Pittura e Scoltura del Settecento (1913)", "archive", "The local bibliography identifies Fogolari's 1913 article cited in p.329 n.3. The article was not independently consulted.", NOTES, 345)
add_candidate("cand-9845", "Diletto ed utile (pleasure and usefulness) as a theory of painting", "term", "Haskell's characterization at p.329 of the older theory that painting gives both delight and utility; retain the Italian phrase as printed.", BODY, 250)
add_candidate("cand-9846", "The useful-arts argument for painting and its patronage", "term", "Eighteenth-century argument in p.329 that painting and its patronage contribute to commerce by attracting foreign buyers and paid commissions; preserve Haskell's and Zanetti's attributions.", BODY, 249)
add_candidate("cand-9847", "Didactic function of painting", "term", "The older theory summarized on p.329: sacred and heroic subjects inspire sacred and heroic deeds.", BODY, 249)
add_candidate("cand-9848", "View painting as a genre", "term", "P.329 identifies view painting as a subordinate branch in the Academy's hierarchy of subjects; this candidate is contextual and awaits S3 alignment.", BODY, 255)
add_candidate("cand-9849", "Unidentified Venetian official committee on the general economic situation (1772)", "institution", "P.329 says an official committee was set up in 1772 to consider the general economic situation and issued a report echoing the useful-arts argument; no formal name is given.", BODY, 253)
add_candidate("cand-9850", "Liberal arts in the eighteenth-century Venetian economic argument", "term", "Named by the 1772 committee in its argument that the arts attract foreigners and confer pleasure and reputation on the State; keep this historical category distinct from the useful-arts theory of painting.", BODY, 253)

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
new_mentions = []


def add_mention(segment, line_no, surface, cid, note="", occurrence=0):
    line_map = body_lines if segment == BODY else note_lines
    if segment not in segment_text or cid not in all_candidate_ids:
        raise SystemExit(f"invalid mention segment/candidate: {segment} {surface!r} {cid}")
    line = line_map[line_no]
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
    first_line = min(line_map)
    start = sum(len(line_map[n]) + 1 for n in range(first_line, line_no)) + starts[occurrence]
    if segment_text[segment][start:start + len(surface)] != surface:
        raise SystemExit(f"mention span mismatch at L{line_no}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p329-{len(new_mentions) + 1:04d}",
        "segment_id": segment,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    new_mentions.append(row)


# Main-text actors, concepts, places, and cited institutional roles.
add_mention(BODY, 249, "Gozzi", "cand-1222")
add_mention(BODY, 249, "social value", "cand-1805")
add_mention(BODY, 249, "A. M. Zanetti the Younger", "cand-2857")
add_mention(BODY, 249, "painting", "cand-1805")
add_mention(BODY, 249, "useful arts", "cand-9846")
add_mention(BODY, 249, "didactic function of painting", "cand-9847")
add_mention(BODY, 250, "diletto ed utile", "cand-9845")
add_mention(BODY, 250, "Zanetti", "cand-2857")
add_mention(BODY, 251, "utilitarian", "cand-9846")
add_mention(BODY, 251, "painting", "cand-1805", occurrence=0)
add_mention(BODY, 251, "its patronage", "cand-9846")
add_mention(BODY, 251, "Italy", "cand-3461")
add_mention(BODY, 251, "Painting", "cand-1805")
add_mention(BODY, 251, "Venetian", "cand-3678", "The phrase refers to the Venetian economy; candidate is the Venetian polity, pending global S3 identity review.")
add_mention(BODY, 251, "England", "cand-4439")
add_mention(BODY, 252, "Spain", "cand-4591")
add_mention(BODY, 252, "Germany", "cand-5529")
add_mention(BODY, 252, "Russia", "cand-9161")
add_mention(BODY, 253, "an official committee", "cand-9849")
add_mention(BODY, 253, "liberal arts", "cand-9850")
add_mention(BODY, 254, "State", "cand-3678")
add_mention(BODY, 255, "the State", "cand-3678")
add_mention(BODY, 255, "Academy of Painting and Sculpture", "cand-0005")
add_mention(BODY, 255, "Venetian territory", "cand-3678", "Political-territorial wording in the Academy's 1724 plan; no boundary is inferred.")
add_mention(BODY, 255, "Florence", "cand-1041")
add_mention(BODY, 255, "Bologna", "cand-3398")
add_mention(BODY, 255, "Rome", "cand-4490")
add_mention(BODY, 255, "the Academy", "cand-0005")
add_mention(BODY, 255, "Italy", "cand-3461")
add_mention(BODY, 255, "Europe", "cand-3462")
add_mention(BODY, 255, "the Senate", "cand-8129")
add_mention(BODY, 255, "value ofpaintings", "cand-1805", "OCR joins the words; p.329 image reads 'value of paintings'.")
add_mention(BODY, 255, "history painting", "cand-6179")
add_mention(BODY, 255, "view painting", "cand-9848")
add_mention(BODY, 255, "neo-classicists", "cand-6439", "The surface names proponents; candidate denotes the artistic tendency pending S3 alignment.")
add_mention(BODY, 256, "the Academy", "cand-0005")
add_mention(BODY, 256, "the position of the artist in society", "cand-0140")

# Notes: OCR spans are retained; printed readings are recorded in candidate details and qualifiers.
add_mention(NOTES, 343, "Della Pittura Veneziana", "cand-9837")
add_mention(NOTES, 344, "Relazione per le risorme", "cand-9838", "OCR reads risorme; p.329 image reads riforme.")
add_mention(NOTES, 344, "Agostino Sagredo", "cand-9839")
add_mention(NOTES, 345, "E. Bassi", "cand-9841", "Resolved against the local bibliography entry for Elena Bassi's 1941 work.")
add_mention(NOTES, 345, "Fogolari", "cand-9843", "Resolved against the local bibliography entry for Gino Fogolari's 1913 Academy article.")

new_mentions.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
for left, right in zip(new_mentions, new_mentions[1:]):
    if left["segment_id"] == right["segment_id"] and int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping mention spans: {left['mention_id']} and {right['mention_id']}")
if any(row["mention_id"] in mention_ids for row in new_mentions):
    raise SystemExit("mention id already exists")

new_statements = []


def add_statement(sid, segment, subject, obj, predicate, start, end, page, physical, claim, quote,
                  qualification, mentioned, *, speaker="Haskell", layer="authorial narrative", extra=None):
    if sid in statement_ids or any(row["statement_id"] == sid for row in new_statements):
        raise SystemExit(f"statement id already exists: {sid}")
    if quote not in segment_text[segment]:
        raise SystemExit(f"statement quote is not anchored: {sid}")
    if any(cid not in all_candidate_ids for cid in mentioned):
        raise SystemExit(f"missing mentioned candidate in {sid}")
    if subject and subject not in all_candidate_ids:
        raise SystemExit(f"missing subject candidate in {sid}")
    if obj and obj not in all_candidate_ids:
        raise SystemExit(f"missing object candidate in {sid}")
    qualifiers = {
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": page,
        "pdf_physical_page": physical,
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
        "segment_id": segment,
        "subject_candidate_id": subject or None,
        "object_candidate_id": obj or None,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
    })


F1 = [{"marker": 1, "segment_id": NOTES, "source_line": 343}]
F2 = [{"marker": 2, "segment_id": NOTES, "source_line": 344}]
F3 = [{"marker": 3, "segment_id": NOTES, "source_line": 345}]


def body_extra(marker, note_ids):
    return {
        "footnote_marker": marker,
        "footnote_segment": NOTES,
        "footnote_refs": {1: F1, 2: F2, 3: F3}[marker],
        "footnote_statement_ids": note_ids,
        "footnote_body_link_status": "linked",
    }


# Close the unfinished p.328 sentence with the source text at the start of p.329.
add_statement(
    "st-chp10-p329-gozzi-social-value", BODY, "cand-1222", "cand-1805", "advanced_tentative_social_value_argument_for",
    249, 249, 329, 62,
    "Haskell says Gozzi tentatively treated the arts' social value as a claim to national glory: they employ people, circulate money and keep families alive.",
    "the finest claim to glory of the country that produces them, he refers almost tentatively to their social value. The arts employ people; consequently money circulates and families are kept alive.",
    "Continues the unfinished p.328 sentence after 'After making the traditional reply that these represent'. The antecedent of 'them' is supplied by the preceding page; the argument remains attributed to Gozzi as characterized by Haskell.",
    ["cand-1222", "cand-1805"],
    extra={"continuation_from_segment_id": PREVIOUS, "continuation_prefix": "After making the traditional reply that these represent", "continuation_status": "closed"},
)
add_statement(
    "st-chp10-p329-gozzi-political-economists", BODY, "cand-1222", "cand-1805", "implicitly_answered_political_economists",
    249, 249, 329, 62,
    "Haskell interprets Gozzi's social-value argument as an implicit answer to charges by the new political economists.",
    "It is plain that Gozzi is here implicitly answering charges by the new political economists.",
    "This is Haskell's interpretation of Gozzi's argument, not a direct statement by the political economists.",
    ["cand-1222", "cand-1805"],
)
add_statement(
    "st-chp10-p329-zanetti-useful-arts", BODY, "cand-2857", "cand-9846", "argued_painting_was_a_useful_art",
    249, 249, 329, 62,
    "Haskell says A. M. Zanetti the Younger, eleven years after Gozzi's 1760 argument, developed a more considered view of painting as one of the useful arts.",
    "Eleven years later A. M. Zanetti the Younger obviously feels that a more considered reply is needed, and he develops at some length the view that painting must be thought of as one of the useful arts.1",
    "The chronology is Haskell's relative dating; the source passage is a paraphrase rather than a direct quotation from Zanetti.",
    ["cand-2857", "cand-9846"],
    extra=body_extra(1, ["st-chp10-p329-n01-della-pittura-preface"]),
)
add_statement(
    "st-chp10-p329-didactic-function", BODY, "cand-2857", "cand-9847", "used_old_didactic_theory_of_painting",
    249, 249, 329, 62,
    "Haskell says Zanetti begins from the accepted didactic theory that sacred and heroic subjects inspire sacred and heroic deeds.",
    "He too begins with the old, accepted theory of the didactic function of painting: sacred and heroic subjects inspire sacred and heroic deeds.",
    "Haskell's account of Zanetti's argument; it does not establish the theory as an independently verified effect.",
    ["cand-2857", "cand-9847"],
)
add_statement(
    "st-chp10-p329-painting-teaches-and-relaxes", BODY, "cand-2857", "cand-1805", "described_painting_as_teaching_and_relaxation",
    249, 249, 329, 62,
    "Haskell says Zanetti updated the older theory by arguing that painting both teaches and provides mental relaxation.",
    "But he then brings the theory up to date with a notable concession to the art of his city and century. Painting not only teaches; it also provides mental relaxation.",
    "Paraphrased by Haskell as Zanetti's view.",
    ["cand-2857", "cand-1805"],
)
add_statement(
    "st-chp10-p329-diletto-ed-utile", BODY, "cand-9845", "cand-1805", "characterized_as_older_painting_theory",
    250, 250, 329, 62,
    "Haskell characterizes the teaching-and-relaxation argument as a fashionable adaptation of the older theory of diletto ed utile.",
    "Even this, however, is merely a fashionable adaptation of the old theory of ‘diletto ed utile’",
    "The characterization and evaluative wording are Haskell's.",
    ["cand-9845", "cand-1805"],
)
add_statement(
    "st-chp10-p329-utilitarian-patronage-defense", BODY, "cand-2857", "cand-9846", "justified_painting_patronage_on_utilitarian_grounds",
    250, 251, 329, 62,
    "Haskell says Zanetti later joined a more modern utilitarian discussion and justified painting, or its patronage, on different grounds.",
    "Zanetti feels bound to take part in the more modern\n'utilitarian' discussion and justify painting, or rather its patronage, on rather different grounds.",
    "The argument is attributed to Zanetti through Haskell's paraphrase.",
    ["cand-2857", "cand-9846", "cand-1805"],
)
add_statement(
    "st-chp10-p329-foreign-market-chain", BODY, "cand-9846", None, "linked_artists_schools_to_foreign_picture_buying",
    251, 251, 329, 62,
    "In Haskell's paraphrase of Zanetti, successful artists attract foreign students, whose return purchases encourage foreign princes to buy Italian pictures.",
    "Flourishing artists attract foreigners to their schools; these foreigners take back works of their masters to their own countries where they are noticed and encourage foreign princes to buy Italian pictures.",
    "This is a reported economic argument, not evidence that the stated market effect occurred in every instance.",
    ["cand-9846", "cand-1805"],
)
add_statement(
    "st-chp10-p329-princely-commissions-and-trade", BODY, "cand-9846", "cand-3461", "linked_foreign_commissions_to_money_returning_to_italy",
    251, 251, 329, 62,
    "Haskell says Zanetti argued that foreign princes invited and well paid Italian artists, who returned to Italy with money; Zanetti concluded that painting contributed to trade.",
    "Even more, these princes often invite Italian artists to come and work in their own countries, where they are extremely well paid; consequently when these artists return to Italy they bring large sums of money with them. ‘And so,’ he concludes, ‘we cannot doubt that Painting has its part to play in trade.’",
    "The economic causal chain and conclusion are attributed to Zanetti via Haskell's account.",
    ["cand-9846", "cand-3461", "cand-1805"],
)
add_statement(
    "st-chp10-p329-venetian-economic-caveat", BODY, "cand-3678", None, "qualified_artist_remittances_as_economic_contribution",
    251, 252, 329, 62,
    "Haskell rejects the returned sums from Venetian artists abroad as the explanation for what helped the Venetian economy at that stage, naming England, Spain, Germany and Russia.",
    "Alas, whatever else might help the Venetian economy at this stage, it was certainly not the sums—however great—brought back by her artists from England,\nSpain, Germany and Russia.",
    "This is Haskell's evaluative caveat, not an independently measured economic finding.",
    ["cand-3678", "cand-4439", "cand-4591", "cand-5529", "cand-9161"],
)
add_statement(
    "st-chp10-p329-committee-report-economic-argument", BODY, "cand-9849", "cand-3678", "reported_liberal_arts_economic_argument",
    252, 254, 329, 62,
    "Haskell says a 1772 official committee echoed the argument that the liberal arts attract foreigners and give the State pleasure and reputation.",
    "None the less, the same sort of argument was echoed in\n1772 by an official committee set up to consider the general economic situation: the liberal arts, it concluded, provide attractions and pleasures and a certain reputation to the\nState, for they encourage foreigners to come here.2",
    "The committee is unnamed. Its conclusion is reported by Haskell and cited in note 2 through Sagredo; the report and intermediary publication were not independently consulted.",
    ["cand-9849", "cand-3678", "cand-9846", "cand-9850"],
    extra=body_extra(2, ["st-chp10-p329-n02-relazione-in-sagredo"]),
)
add_statement(
    "st-chp10-p329-academy-1724-plan", BODY, "cand-3678", "cand-0005", "planned_academy_to_attract_foreign_passersby",
    254, 255, 329, 62,
    "Haskell says these ideas led the State to plan an Academy of Painting and Sculpture in 1724 to attract foreigners travelling through Venetian territory toward Florence, Bologna and Rome.",
    "It was ideas of this kind that persuaded the State to make its single important venture into the realm of art patronage. As early as 1724 it had been planned to found an Academy of Painting and Sculpture ‘so as to attract and encourage to remain here those foreigners who have to pass Venetian territory on their way to Florence, Bologna and Rome’.3",
    "The plan is dated 1724; this passage does not say that it was implemented in that year.",
    ["cand-3678", "cand-0005", "cand-1041", "cand-3398", "cand-4490"],
    extra=body_extra(3, ["st-chp10-p329-n03-bassi-academy-study", "st-chp10-p329-n03-fogolari-academy-study"]),
)
add_statement(
    "st-chp10-p329-academy-established-1756", BODY, "cand-0005", None, "established_in_1756",
    255, 255, 329, 62,
    "Haskell dates the Academy's establishment to 1756 and says similar institutions had already appeared in other Italian and European towns.",
    "When in 1756 the Academy was finally established (after a number of similar institutions in other towns of Italy and Europe)",
    "The comparative scope is limited to Haskell's statement; no other academy is identified here.",
    ["cand-0005", "cand-3461", "cand-3462"],
    extra=body_extra(3, ["st-chp10-p329-n03-bassi-academy-study", "st-chp10-p329-n03-fogolari-academy-study"]),
)
add_statement(
    "st-chp10-p329-senate-commercial-benefit", BODY, "cand-8129", "cand-3678", "hoped_academy_would_produce_commercial_benefit",
    255, 255, 329, 62,
    "Haskell says the Senate hoped the Academy would bring commercial benefit and characterizes its calculation as mixed with naïveté.",
    "the Senate hoped, with a mixture of shrewd calculation and naïveté which is characteristic of much of its legislation at this period, to gain some commercial benefit from the arrangement.",
    "The judgement about calculation and naïveté is Haskell's characterization of Senate policy.",
    ["cand-8129", "cand-3678", "cand-0005"],
    extra=body_extra(3, ["st-chp10-p329-n03-bassi-academy-study", "st-chp10-p329-n03-fogolari-academy-study"]),
)
add_statement(
    "st-chp10-p329-academy-subject-hierarchy", BODY, "cand-0005", "cand-9848", "organized_painting_by_hierarchical_subjects",
    255, 255, 329, 62,
    "Haskell says the Academy's organization retained a rigid subject hierarchy, with history painting supreme and view painting subordinate.",
    "for the rigid stratification of subjectmatter, based on the absolute supremacy of history painting and the complete subordination of such inferior branches as view painting",
    "The OCR joins 'subjectmatter'; the p.329 image shows 'subject-matter'. The hierarchy is Haskell's description of the Academy's organization.",
    ["cand-0005", "cand-6179", "cand-9848"],
    extra=body_extra(3, ["st-chp10-p329-n03-bassi-academy-study", "st-chp10-p329-n03-fogolari-academy-study"]),
)
add_statement(
    "st-chp10-p329-academy-hierarchy-chronology", BODY, "cand-0005", "cand-6439", "looked_back_rather_than_anticipating_neoclassicist_opinions",
    255, 255, 329, 62,
    "Haskell argues that the hierarchy looked back to an earlier period rather than anticipating the opinions of the neo-classicists.",
    "looked back to a much earlier period rather than anticipated the opinions of the neo-classicists.",
    "A comparative art-historical judgement attributed to Haskell.",
    ["cand-0005", "cand-6439", "cand-6179", "cand-9848"],
    extra=body_extra(3, ["st-chp10-p329-n03-bassi-academy-study", "st-chp10-p329-n03-fogolari-academy-study"]),
)
add_statement(
    "st-chp10-p329-artists-graded-by-subject", BODY, "cand-0005", None, "graded_artists_by_painted_subjects",
    255, 255, 329, 62,
    "Haskell says artists were firmly ranked according to the subjects they painted.",
    "And the artists themselves were firmly graded in a hierarchy according to the subjects that they painted.",
    "The statement concerns the Academy's subject hierarchy, not a named individual artist.",
    ["cand-0005"],
    extra=body_extra(3, ["st-chp10-p329-n03-bassi-academy-study", "st-chp10-p329-n03-fogolari-academy-study"]),
)
add_statement(
    "st-chp10-p329-artist-status-debate-open", BODY, "cand-0140", "cand-0005", "debated_after_academy_institution",
    256, 256, 329, 62,
    "Haskell begins a new discussion, saying that the artist's position in society was debated again shortly after the Academy was instituted.",
    "Very shortly after the institution of the Academy the position of the artist in society",
    "The sentence continues on p.330; this statement remains open until that segment is reviewed.",
    ["cand-0140", "cand-0005"],
    extra={"continuation_to_segment_id": NEXT, "continuation_status": "open"},
)

# P.329 footnotes, with the cited items resolved against the local bibliography only.
add_statement(
    "st-chp10-p329-n01-della-pittura-preface", NOTES, "cand-2857", "cand-9837", "cited_preface_for_useful_arts_argument",
    343, 343, 329, 62,
    "Haskell's note cites the preface to Della Pittura Veneziana (1771), p.xiii, for Zanetti's useful-arts argument.",
    note_lines[343],
    "The title is matched to the local bibliography entry for A. M. Zanetti, 1771; the book was not independently consulted.",
    ["cand-2857", "cand-9837"], speaker="Haskell's note", layer="bibliographic citation",
    extra={"footnote_marker": 1, "cited_source_independently_consulted": False},
)
add_statement(
    "st-chp10-p329-n02-relazione-in-sagredo", NOTES, "cand-9838", "cand-9840", "quoted_in_cited_secondary_work",
    344, 344, 329, 62,
    "Haskell's note identifies the 18 August 1772 Relazione per le riforme as quoted by Agostino Sagredo in 1857, p.208.",
    note_lines[344],
    "The p.329 scan reads riforme, correcting the OCR risorme. The local bibliography identifies Sagredo's 1857 work as Sulle consorterie delle Arti edificatorie in Venezia; neither text was independently consulted.",
    ["cand-9838", "cand-9839", "cand-9840"], speaker="Haskell's note", layer="bibliographic citation",
    extra={"footnote_marker": 2, "cited_source_independently_consulted": False, "ocr_corrections": [{"source_line": 344, "ocr": "risorme", "print": "riforme"}]},
)
add_statement(
    "st-chp10-p329-n03-bassi-academy-study", NOTES, "cand-0005", "cand-9842", "cited_for_academy_history",
    345, 345, 329, 62,
    "Haskell's note cites E. Bassi (1941) in the discussion of the Venetian Academy.",
    note_lines[345],
    "The local bibliography identifies the matching publication as Elena Bassi's La Regia Accademia di Belle Arti di Venezia; it was not independently consulted.",
    ["cand-0005", "cand-9841", "cand-9842"], speaker="Haskell's note", layer="bibliographic citation",
    extra={"footnote_marker": 3, "cited_source_independently_consulted": False},
)
add_statement(
    "st-chp10-p329-n03-fogolari-academy-study", NOTES, "cand-0005", "cand-9844", "cited_for_academy_history",
    345, 345, 329, 62,
    "Haskell's note cites Fogolari (1913) in the discussion of the Venetian Academy.",
    note_lines[345],
    "The local bibliography identifies the matching publication as Gino Fogolari's article L’Accademia Veneziana di Pittura e Scoltura del Settecento; it was not independently consulted.",
    ["cand-0005", "cand-9843", "cand-9844"], speaker="Haskell's note", layer="bibliographic citation",
    extra={"footnote_marker": 3, "cited_source_independently_consulted": False},
)

if any(row["mention_id"] in mention_ids for row in new_mentions):
    raise SystemExit("mention id already exists")
if any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("statement id already exists")
all_statement_ids = statement_ids | {row["statement_id"] for row in new_statements}
for row in new_statements:
    qualifiers = row.get("qualifiers", {})
    for cid in qualifiers.get("mentioned_candidate_ids", []):
        if cid not in all_candidate_ids:
            raise SystemExit(f"missing mentioned candidate in {row['statement_id']}: {cid}")
    for field in ("subject_candidate_id", "object_candidate_id"):
        cid = row.get(field)
        if cid and cid not in all_candidate_ids:
            raise SystemExit(f"missing {field} in {row['statement_id']}: {cid}")
    for sid in qualifiers.get("footnote_statement_ids", []):
        if sid not in all_statement_ids:
            raise SystemExit(f"dangling footnote statement reference in {row['statement_id']}: {sid}")

candidate_rows = candidates + new_candidates
mention_rows = mentions + new_mentions
statement_rows = statements + new_statements
coverage_rows[coverage_rows.index(coverage[PREVIOUS])].update({
    "migration_status": "complete",
    "source_line_ranges": "L241-246",
    "note": "p.328 unfinished Gozzi argument closes at p.329 L249; p.328 notes linked.",
})
coverage_rows[coverage_rows.index(coverage[BODY])].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L248-256",
    "note": "p.328 sentence closes at L249; p.329 final sentence continues at p.330; footnotes 1-3 linked.",
})
coverage_rows[coverage_rows.index(coverage[NOTES])].update({
    "migration_status": "partial",
    "source_line_ranges": "L325-345",
    "note": "p.324-329 footnotes linked; continue with p.330 notes L346 onward.",
})
candidate_rows.sort(key=lambda row: row["candidate_id"])
mention_rows.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
statement_rows.sort(key=lambda row: row["statement_id"])
coverage_rows.sort(key=lambda row: row["segment_id"])

print(f"p.329 preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("coverage: p.328 complete; p.329 partial; notes L325-345 partial")
print("continuations: p.328 Gozzi sentence closed; p.329 artist-status sentence remains open to p.330")
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
