"""Apply the reviewed Chapter 15 referent corrections; dry-run unless --apply."""
import argparse
import csv
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_REF = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#chapter15-current-referent-correction-20261029"


def load_csv(name):
    path = TABLES / name
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    return path, list(csv.DictReader(io.StringIO(text, newline=""))), bom, newline


def dump_csv(path, rows, bom, newline):
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=list(rows[0]), lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    data = buf.getvalue().encode("utf-8")
    path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + data)


def load_jsonl(name):
    path = TABLES / name
    return path, [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def dump_jsonl(path, rows):
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8", newline="\n")


def require_unique(rows, key, value):
    matches = [row for row in rows if row.get(key) == value]
    if len(matches) != 1:
        raise ValueError(f"Expected one {key}={value!r}; found {len(matches)}")
    return matches[0]


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed changes")
args = parser.parse_args()

statement_path, statements = load_jsonl("book-statements.jsonl")
by_statement = {row["statement_id"]: row for row in statements}
ids = {
    "eligibility": "st-chp15-p365-memmo-representation-eligibility-partial",
    "progress": "st-chp15-p366-1777-progress-and-ambassadorship",
    "rome": "st-chp15-p366-another-six-in-rome-ambiguous",
    "committee": "st-chp15-p366-committee-appointed-for-quality",
    "expense": "st-chp15-p366-councillors-objected-to-expense",
    "variation": "st-chp15-p367-patronage-and-speed-caused-variation",
    "results": "st-chp15-p367-results-difficult-to-assess",
}
for value in ids.values():
    if value not in by_statement:
        raise ValueError(f"Missing statement {value}")
if any(row["statement_id"] == ids["rome"] for row in statements) is False:
    raise ValueError("Unexpected statement state")

# The saved S0 OCR segment supplies the reviewed character offsets.
source = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_ii.md"
source_lines = source.read_text(encoding="utf-8").splitlines()
segments = {
    (6, 12): "\n".join(source_lines[5:12]),
    (14, 28): "\n".join(source_lines[13:28]),
    (30, 36): "\n".join(source_lines[29:36]),
}
glory = "men who had brought particular glory to the"
quality = "A certain standard of quality"
work_phrase = "the work"
if segments[(6, 12)][3214:3257] != glory:
    raise ValueError("Reviewed p.365 mention span no longer matches S0")
if segments[(14, 28)][562:591] != quality:
    raise ValueError("Reviewed p.366 mention span no longer matches S0")
work_start = segments[(30, 36)].find(work_phrase, 1000)
if work_start < 0 or segments[(30, 36)][work_start:work_start + len(work_phrase)] != work_phrase:
    raise ValueError("Reviewed p.367 work mention no longer matches S0")

e = by_statement[ids["eligibility"]]
e["object_candidate_id"] = None
e["qualifiers"]["mentioned_candidate_ids"] = ["cand-12456", "cand-12230", "cand-12457", "cand-3944"]
e["qualifiers"]["relation_candidate_note"] = "This is an eligibility rule, not an enacted person-work relation. The two generic classes are tracked separately; do not infer named eligible persons or formal edges."
e["qualifiers"]["open_endpoint_reason"] = "The second generic class now has its own source-backed candidate cand-12457. Neither class enumerates individual persons, and the second candidate remains untyped and undecided."

p = by_statement[ids["progress"]]
p["qualifiers"]["claim"] = "Haskell says that 19 statues were in place in 1777 when Memmo left for a four-year ambassadorship in Constantinople."
p["qualifiers"]["qualification"] = "The source states the count and year; it does not call this a progress report. Memmo's subsequent stay in Rome is recorded separately."
p["qualifiers"]["mentioned_candidate_ids"] = ["cand-12456", "cand-1642"]
p["original_quote"] = "In 1777, with 19 statues in place, Memmo left for four years as Ambassador in Constantinople"

r = by_statement[ids["rome"]]
r["subject_candidate_id"] = "cand-1642"
r["object_candidate_id"] = "cand-4490"
r["predicate"] = "memmo_spent_another_six_years_in_rome_after_ambassador_service"
r["qualifiers"]["claim"] = "Haskell says that after four years as Ambassador in Constantinople, Memmo spent another six years in Rome."
r["qualifiers"]["qualification"] = "The syntax is compressed, but another six refers to years, not six statues: it follows the four-year ambassadorship, and p.367 says Memmo returned to Venice in 1787 after referring to his last year in Rome. The source does not give exact dates for the Roman stay."
r["qualifiers"]["mentioned_candidate_ids"] = ["cand-1642", "cand-4490"]
r["qualifiers"]["predicate_status"] = "qualified"
r["qualifiers"]["relation_candidate_note"] = "The source reports Memmo's stay in Rome. The controlled located_at predicate is marked needs_split, so retain the relation as pending."
r["qualifiers"]["open_endpoint_reason"] = "Both person and place resolve to existing candidates/KUs; S6 remains pending because the controlled predicate does not faithfully encode the reported residence."
r["original_quote"] = "Memmo left for four years as Ambassador in Constantinople to be followed immediately by another six in Rome"

c = by_statement[ids["committee"]]
c["object_candidate_id"] = "cand-12458"
c["original_quote"] = "A certain standard of quality was insisted on and a committee was appointed to see that it was adhered to."
c["qualifiers"]["claim"] = "Haskell says a committee was appointed to ensure that the stated standard of quality was followed."
c["qualifiers"]["mentioned_candidate_ids"] = ["cand-12234", "cand-12458"]
c["qualifiers"]["qualification"] = "The pronoun it refers to the immediately preceding standard of quality, not the whole statue programme. The standard now has a separate source-backed candidate; its type remains undecided."
c["qualifiers"]["relation_candidate_note"] = "Haskell reports an appointment to enforce a quality standard. Keep pending until the committee identity and a faithful controlled predicate are available."
c["qualifiers"]["open_endpoint_reason"] = "The committee remains unidentified and the standard candidate cand-12458 is untyped; no faithful controlled relation predicate is established."

x = by_statement[ids["expense"]]
x["object_candidate_id"] = None
x["qualifiers"]["claim"] = "Haskell reports that the councillors objected to the expense, but the scope of that expense is unspecified."
x["qualifiers"]["mentioned_candidate_ids"] = ["cand-11529"]
x["qualifiers"]["open_endpoint_reason"] = "The councillors remain unidentified and the phrase the expense has no established object or scope. Do not attach it to the urban plan or statue programme without evidence."

v = by_statement[ids["variation"]]
v["qualifiers"]["mentioned_candidate_ids"] = ["cand-12456"]
v["qualifiers"]["qualification"] += " The exact phrase the work refers to the Prà statue programme in context; this is recorded as a mention, not a separate individual work."

z = by_statement[ids["results"]]
z["qualifiers"]["qualification"] = "S0 OCR reads Prato della Valle; the inspected print page reads Prà della Valle. The evaluative claim is unchanged, and its subject remains the physical place candidate cand-3960."

mentions_path, mentions, mentions_bom, mentions_nl = load_csv("mentions.csv")
for mid in ["m-chp15-p365-glory-eligibility-class", "m-chp15-p366-quality-standard", "m-chp15-p367-pra-work-reference"]:
    if any(row["mention_id"] == mid for row in mentions):
        raise ValueError(f"Mention ID already exists: {mid}")
mentions = [row for row in mentions if row["mention_id"] != "m-chp15-p366-memmo-0038"]
mentions.extend([
    {"mention_id": "m-chp15-p365-glory-eligibility-class", "segment_id": "chp-15:15_CHP-15_sec_ii:l6-12", "candidate_id": "cand-12457", "surface_form": glory, "start_char": "3214", "end_char": "3257", "note": "Second generic class in the p.365-366 representation rule; not an identified person or a claim that the class is exclusively Paduan."},
    {"mention_id": "m-chp15-p366-quality-standard", "segment_id": "chp-15:15_CHP-15_sec_ii:l14-28", "candidate_id": "cand-12458", "surface_form": quality, "start_char": "562", "end_char": "591", "note": "The antecedent of it in the committee statement; type and scope remain undecided."},
    {"mention_id": "m-chp15-p367-pra-work-reference", "segment_id": "chp-15:15_CHP-15_sec_ii:l30-36", "candidate_id": "cand-12456", "surface_form": work_phrase, "start_char": str(work_start), "end_char": str(work_start + len(work_phrase)), "note": "In the p.367 quality-variation sentence, the work refers to the Prà della Valle statue programme."},
])

candidate_path, candidates, candidate_bom, candidate_nl = load_csv("entity-candidates.csv")
for cid in ["cand-12457", "cand-12458"]:
    if any(row["candidate_id"] == cid for row in candidates):
        raise ValueError(f"Candidate ID already exists: {cid}")
old_work = require_unique(candidates, "candidate_id", "cand-10498")
old_work["status"] = "excluded"
old_work["exclude_reason"] = "Referent correction: in context another six means another six years in Rome after four years as Ambassador in Constantinople; it is a duration, not a group of six statue works."
old_work["detail"] += " Prior work interpretation rejected after rereading the complete sentence and p.367 chronology."
candidates.extend([
    {"candidate_id": "cand-12457", "index_entry_id": "", "canonical_name": "Men credited with particular glory to the city in Memmo's eligibility rule (p.365-366)", "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "", "sub_entry": "", "detail": "A generic source-defined eligibility class; no individuals or regional boundary are specified. Keep separate from the nobility class.", "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": "chp-15:15_CHP-15_sec_ii:l6-12#L11; continuation l14-28#L15"},
    {"candidate_id": "cand-12458", "index_entry_id": "", "canonical_name": "Unspecified standard of quality for Memmo's statue programme (p.366)", "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "", "sub_entry": "", "detail": "The standard to which the appointed committee was to adhere; no formal name, measurement, or taxonomy type is stated.", "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": "chp-15:15_CHP-15_sec_ii:l14-28#L16"},
])

alignment_path, alignments, alignment_bom, alignment_nl = load_csv("alignment.csv")
old_alignment = require_unique(alignments, "candidate_id", "cand-10498")
prior = old_alignment["resolution_note"]
old_alignment["decision"] = "excluded"
old_alignment["process_ref"] = PROCESS_REF
old_alignment["resolution_note"] = "source_ref=entity-candidates.csv#cand-10498; source_ref=chp-15:15_CHP-15_sec_ii:l14-28#L20; S3 correction: another six denotes years in Rome after the four-year Constantinople ambassadorship, not six statue works; exclude as a mistaken entity candidate. prior_resolution_note=" + prior
alignments.extend([
    {"alignment_id": "aln-12788", "candidate_id": "cand-12457", "ku_id": "", "external_source": "", "external_id": "", "decision": "undecided", "accessed_date": "", "process_ref": PROCESS_REF, "legacy_ku_id": "", "resolution_note": "group=sg3-untyped-cand-12457; source_ref=chp-15:15_CHP-15_sec_ii:l6-12#L11 and l14-28#L15; source defines a generic eligibility class but no individuals or regional boundary; no supported type; do not merge with nobility or named persons."},
    {"alignment_id": "aln-12789", "candidate_id": "cand-12458", "ku_id": "", "external_source": "", "external_id": "", "decision": "undecided", "accessed_date": "", "process_ref": PROCESS_REF, "legacy_ku_id": "", "resolution_note": "group=sg3-untyped-cand-12458; source_ref=chp-15:15_CHP-15_sec_ii:l14-28#L16; exact antecedent is the stated quality standard; no supported taxonomy type, formal identity, or external match; retain as a distinct untyped candidate."},
])

backlog_path, backlog, backlog_bom, backlog_nl = load_csv("candidate-backlog.csv")
old_backlog = require_unique(backlog, "backlog_id", "bl-0075")
old_backlog["status"] = "completed"
old_backlog["decision_note"] = "Closed after referent correction: another six means years in Rome following the four-year ambassadorship, not a statue group. Candidate cand-10498 is excluded in S3; the corrected person-to-Rome relation remains pending under located_at because that predicate needs split."
backlog.extend([
    {"backlog_id": "bl-0083", "canonical_name": "Men credited with particular glory to the city in Memmo's eligibility rule (p.365-366)", "suggested_type": "", "status": "undecided", "source_id": "haskell-1980-rev-ed", "source_ref": "chp-15:15_CHP-15_sec_ii:l6-12#L11; continuation l14-28#L15", "statement_id": ids["eligibility"], "endpoint_role": "object", "candidate_id": "cand-12457", "ku_id": "", "decision_note": "Generic class is source-backed but has no supported type or identified members. The rule is not a formal person-work relation.", "process_ref": PROCESS_REF},
    {"backlog_id": "bl-0084", "canonical_name": "Unspecified standard of quality for Memmo's statue programme (p.366)", "suggested_type": "", "status": "undecided", "source_id": "haskell-1980-rev-ed", "source_ref": "chp-15:15_CHP-15_sec_ii:l14-28#L16", "statement_id": ids["committee"], "endpoint_role": "object", "candidate_id": "cand-12458", "ku_id": "", "decision_note": "Exact antecedent is clear, but type and formal identity are not. The committee relation remains pending until endpoints and a faithful predicate are available.", "process_ref": PROCESS_REF},
    {"backlog_id": "bl-0085", "canonical_name": "Unspecified expense objected to by the councillors (p.366)", "suggested_type": "", "status": "undecided", "source_id": "haskell-1980-rev-ed", "source_ref": "chp-15:15_CHP-15_sec_ii:l14-28#L20", "statement_id": ids["expense"], "endpoint_role": "object", "candidate_id": "", "ku_id": "", "decision_note": "The scope of the expense is not stated. Do not infer that it is the urban plan or the statue programme.", "process_ref": PROCESS_REF},
])

coverage_path, coverage, coverage_bom, coverage_nl = load_csv("s2-coverage.csv")
for segment_id in ["chp-15:15_CHP-15_sec_ii:l6-12", "chp-15:15_CHP-15_sec_ii:l14-28", "chp-15:15_CHP-15_sec_ii:l30-36"]:
    row = require_unique(coverage, "segment_id", segment_id)
    note = " Independent review of 40 Chapter 15 statements found 34 passing and six requiring revision; current revised statement/mention versions remain unreviewed and are not added to the 9,622-item ledger."
    if note.strip() not in row["note"]:
        row["note"] += note

relations_path, relations, relations_bom, relations_nl = load_csv("relations.csv")
if any(row["source_span"].find(ids["rome"]) >= 0 for row in relations):
    raise ValueError("A relation already exists for the corrected Rome statement")
next_rel = max(int(row["relation_id"].split("-")[1]) for row in relations) + 1
relations.append({
    "relation_id": f"rel-{next_rel:04d}",
    "subject_ku_id": "units/persons/andrea-memmo",
    "object_ku_id": "units/places/rome",
    "predicate": "located_at",
    "time": "",
    "role": "Reported stay in Rome",
    "scope": "Haskell reports another six years in Rome after Memmo's four-year Constantinople ambassadorship. The source does not give exact dates for the stay; p.367 says he returned to Venice in 1787 after referring to his last year in Rome.",
    "origin": "book",
    "status": "pending",
    "source_id": "haskell-1980-rev-ed",
    "source_span": "Chapter 15, printed p.366, line 20; statement=" + ids["rome"] + "; printed p.367 chronology checked",
    "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
    "note": "Keep pending because the controlled located_at predicate is marked needs_split; this records Haskell's source claim and does not assert verified continuous residence or infer exact dates.",
})

print("Dry-run summary: 7 statements revised; mentions +3/-1; 2 untyped candidates/alignment rows and 3 backlog rows added; bl-0075 closed; cand-10498 excluded; 1 pending location relation added.")
print("Exact new S0 mention spans verified: p.365 3214:3257; p.366 562:591; p.367 " + str(work_start) + ":" + str(work_start + len(work_phrase)))
if args.apply:
    dump_jsonl(statement_path, statements)
    dump_csv(mentions_path, mentions, mentions_bom, mentions_nl)
    dump_csv(candidate_path, candidates, candidate_bom, candidate_nl)
    dump_csv(alignment_path, alignments, alignment_bom, alignment_nl)
    dump_csv(backlog_path, backlog, backlog_bom, backlog_nl)
    dump_csv(coverage_path, coverage, coverage_bom, coverage_nl)
    dump_csv(relations_path, relations, relations_bom, relations_nl)
    print("Applied reviewed Chapter 15 data changes.")
else:
    print("No files written. Re-run with --apply to write.")
