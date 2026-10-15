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
PATHS = {
    "statements": TABLES / "book-statements.jsonl",
    "mentions": TABLES / "mentions.csv",
    "candidates": TABLES / "entity-candidates.csv",
}
EXPECTED = {
    "statements": "834e25d626b720329d08caa1baa4504cf8bf96994aaa181ca8666a4dee0d58d3",
    "mentions": "23ec2216cb365c02bdab9281388dd63dbf07cfcf2b56a69904cc46bb846b52e5",
    "candidates": "890f84fad93f3512f68f8a9330191ef87973eb41e59c7546eb519ac50a511066",
}
BACKUP_TAG = ".bak-s2-ch15-p362-semantic-review-20261015"
BODY = "chp-15:15_CHP-15_sec_i:l16-25"
PRECEDING = "chp-15:15_CHP-15_sec_i:l3-14"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()


def sha(data):
    return hashlib.sha256(data).hexdigest()


before = {key: path.read_bytes() for key, path in PATHS.items()}
for key, data in before.items():
    if sha(data) != EXPECTED[key]:
        raise SystemExit(f"unexpected pre-write hash {key}")

statements = [
    json.loads(line)
    for line in before["statements"].decode("utf-8-sig").splitlines()
    if line.strip()
]
statement_by_id = {row["statement_id"]: row for row in statements}
if len(statement_by_id) != len(statements):
    raise SystemExit("duplicate statement IDs")

true_notes = {
    "st-chp15-p362-men-turn-away-from-painting":
        "The pronoun refers to the few distinguished men introduced at p.361 L13–14; membership remains unenumerated. Haskell explicitly says they tended to turn away from painting, so the group and the practice are recorded as open term endpoints.",
    "st-chp15-p362-farsetti-family-rich-and-patrician-status-1664":
        "Haskell attributes the wealth and the 1664 acquisition of patrician standing to Farsetti's birth family; the family is distinct from Filippo as an individual.",
    "st-chp15-p362-farsetti-travelled-and-wider-cultural-range":
        "Haskell links Farsetti's extensive travel with a cultural range wider than was usual among the Venetian nobility. The comparison is the source's generalization; no unlisted destinations are inferred.",
    "st-chp15-p362-farsetti-became-abate-to-avoid-political-responsibilities":
        "Haskell explicitly connects Farsetti's becoming an abate with avoiding the political responsibilities attached to his status. The role is represented as a term; no named office or formal appointment is inferred.",
    "st-chp15-p362-farsetti-devoted-resources-to-arts":
        "Haskell says most of Farsetti's time, energy, and money were devoted to the arts. The broad domain is retained as a term; no specific project or expenditure is inferred.",
    "st-chp15-p362-farsetti-considered-most-significant-patron":
        "Haskell attributes the judgment to Farsetti's contemporaries and successors and identifies him as the person they considered the city's most significant patron. The unnamed judging group remains open.",
    "st-chp15-p362-casts-from-antiquity-europe-and-rome":
        "Haskell says Farsetti's casts were taken from antique statues across Europe, especially Rome. The source statues remain an unnamed work group; no individual originals are identified.",
    "st-chp15-p362-farsetti-assurance-in-rome":
        "The passage places Farsetti in Rome and characterizes his manner with a simile. It does not claim English nationality, title, or status.",
    "st-chp15-p362-few-contemporaries-in-paintings":
        "Haskell says few contemporary painters were represented in Farsetti's small painting collection apart from Zuccarelli; this does not identify particular paintings by Zuccarelli.",
    "st-chp15-p362-farsetti-enthusiastic-for-dutch-flemish":
        "Haskell explicitly attributes enthusiasm for Dutch and Flemish art to Farsetti; no individual artists or works are supplied here.",
    "st-chp15-p362-farsetti-owned-pictures-attributed-to-italian-masters":
        "Haskell reports ownership of pictures attributed to a wide range of seventeenth-century Italian masters. The attribution qualification is retained, and no artist is promoted to confirmed authorship.",
    "st-chp15-p362-country-villa-design-description":
        "This row now records only the explicit comparison with standard Venetian villa prototypes. The same sentence's collection purpose is covered by the two existing collection relations, and its Austrian-pattern comparison is recorded separately.",
    "st-chp15-p362-country-villa-central-convex-bay":
        "The source describes a distinct central convex bay projecting from the villa's main block; both architectural components are represented separately as open work candidates.",
    "st-chp15-p362-country-villa-wings-and-pavilions":
        "Haskell describes the main block as joined by the lower two-storey wings to small square pavilions. The source does not supply dimensions beyond the stated storey count and shape.",
}
false_notes = {
    "st-chp15-p362-farsetti-born-1703":
        "This is a biographical birth-date assertion with no separate relation endpoint; retain it as a claim rather than inventing a date entity.",
    "st-chp15-p362-farsetti-collecting-chronology-not-known":
        "This records Haskell's stated evidentiary limit about assessing Farsetti's taste, not a directed relation or proof that chronology is unavailable elsewhere.",
    "st-chp15-p362-rezzonico-became-pope-clement-xiii-1758":
        "The statement records Carlo Rezzonico's accession/name as Pope Clement XIII. The papal name is the same person, not a second endpoint; the identity relation is already resolved in the mention note.",
    "st-chp15-p362-farsetti-selected-four-modern-sculptures":
        "This is Haskell's evaluative inference about Farsetti's taste. The four individual selection relations are already recorded in separate statements, so this umbrella interpretation is retained as an assertion without a duplicate graph edge.",
    "st-chp15-p362-farsetti-cosmopolitan-outlook":
        "This is Haskell's interpretation of Farsetti's combined choices, not a distinct relation. The adjective 'Venetian' here describes a cultural outlook, not the city as a place.",
    "st-chp15-p362-this-surpassed-venetian-collections-referent-unresolved":
        "This is Haskell's evaluative comparison of the villa's extravagance with several collections; the plural does not identify one collection endpoint, so the comparison remains an attributed assertion.",
}

for sid, note in {**true_notes, **false_notes}.items():
    if sid not in statement_by_id:
        raise SystemExit(f"missing expected p362 statement: {sid}")
    qualifiers = statement_by_id[sid].setdefault("qualifiers", {})
    if qualifiers.get("relation_candidate") is not None:
        raise SystemExit(f"unexpected pre-classified p362 statement: {sid}")
    qualifiers["relation_candidate"] = sid in true_notes
    qualifiers["relation_candidate_note"] = note


def read_csv(key):
    with PATHS[key].open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


candidate_fields, candidates = read_csv("candidates")
mention_fields, mentions = read_csv("mentions")
candidate_by_id = {row["candidate_id"]: row for row in candidates}
mention_by_id = {row["mention_id"]: row for row in mentions}
if len(candidate_by_id) != len(candidates) or len(mention_by_id) != len(mentions):
    raise SystemExit("duplicate candidate or mention IDs")
if max(int(cid.split("-")[1]) for cid in candidate_by_id) != 12207:
    raise SystemExit("candidate ID sequence changed")
if max(int(mid.rsplit("-", 1)[1]) for mid in mention_by_id if mid.startswith("m-chp15-p362-")) != 87:
    raise SystemExit("p362 mention ID sequence changed")

new_candidates = [
    ["cand-12208", "", "Few distinguished men introduced at the close of p.361 (unnamed group)", "", "term", "open", "", "", "Haskell refers to a few men of great distinction and uses they on p.362. Membership is not enumerated; do not assume every person named in the chapter belongs to this group.", "", "body-mention", "chp-15:15_CHP-15_sec_i:l3-14#L13"],
    ["cand-12209", "", "Painting as an artistic practice from which the distinguished men tended to turn (p.362)", "", "term", "open", "", "", "This is the practice named in Haskell's sentence, not a particular painting or an artist group.", "", "body-mention", "chp-15:15_CHP-15_sec_i:l16-25#L17"],
    ["cand-12210", "", "Abate status adopted by Filippo Farsetti (p.362)", "", "term", "open", "", "", "Haskell says Farsetti became an abate to avoid political responsibilities; no formal appointment or specific clerical office is supplied.", "", "body-mention", "chp-15:15_CHP-15_sec_i:l16-25#L17"],
    ["cand-12211", "", "The arts to which Farsetti devoted most of his time, energy, and money (p.362)", "", "term", "open", "", "", "A broad source-defined domain; no particular artistic project or expenditure is identified.", "", "body-mention", "chp-15:15_CHP-15_sec_i:l16-25#L17"],
    ["cand-12212", "", "Farsetti's unnamed contemporaries and successors who judged his patronage (p.362)", "", "term", "open", "", "", "Haskell gives no names or count for the contemporaries and successors who regarded Farsetti as the city's most significant patron.", "", "body-mention", "chp-15:15_CHP-15_sec_i:l16-25#L18"],
    ["cand-12213", "", "Antique statues represented by casts in Farsetti's collection (unnamed group, p.362)", "", "work", "open", "", "", "The source says the originals came from across Europe, especially Rome, but names no individual statues.", "", "body-mention", "chp-15:15_CHP-15_sec_i:l16-25#L18"],
    ["cand-12214", "", "Modern sculpture as the category represented by Farsetti's four selected statues (p.362)", "", "term", "open", "", "", "Haskell's category for the four named statues; this is distinct from the Venetian neo-classical movement candidate.", "", "body-mention", "chp-15:15_CHP-15_sec_i:l16-25#L20"],
    ["cand-12215", "", "Standard Venetian villa prototypes used as the architectural comparator for Farsetti's villa (p.362)", "", "term", "open", "", "", "The source names a general architectural norm, not a particular building and not the city of Venice as the endpoint.", "", "body-mention", "chp-15:15_CHP-15_sec_i:l16-25#L24"],
    ["cand-12216", "", "Austrian architectural pattern used as the comparator for Farsetti's villa (p.362)", "", "term", "open", "", "", "Haskell says the villa was in some ways closer to this pattern; no specific Austrian building is identified.", "", "body-mention", "chp-15:15_CHP-15_sec_i:l16-25#L24"],
    ["cand-12217", "", "Central convex bay projecting from the main block of Farsetti's villa (p.362)", "", "work", "open", "", "", "A separately described architectural component of the Farsetti country house; not a separate building.", "", "body-mention", "chp-15:15_CHP-15_sec_i:l16-25#L24"],
    ["cand-12218", "", "Main block of Farsetti's country villa at S. Maria di Sala (p.362)", "", "work", "open", "", "", "Architectural component distinguished from the villa as a whole; the source describes the bay and wings in relation to it.", "", "body-mention", "chp-15:15_CHP-15_sec_i:l16-25#L24"],
    ["cand-12219", "", "Lower two-storey wings of Farsetti's country villa (p.362)", "", "work", "open", "", "", "Architectural components connecting the main block to the end pavilions; no measured dimensions beyond two storeys are given.", "", "body-mention", "chp-15:15_CHP-15_sec_i:l16-25#L24"],
    ["cand-12220", "", "Small square pavilions at the ends of Farsetti's country villa (p.362)", "", "place", "open", "", "", "The source describes small pavilions at each end, joined to the main block by lower wings.", "", "body-mention", "chp-15:15_CHP-15_sec_i:l16-25#L24"],
    ["cand-12221", "", "Venetian outlook as a cultural orientation contrasted with Farsetti's cosmopolitan choices (p.362)", "", "term", "open", "", "", "In this sentence Venetian describes a cultural outlook, not the geographical city or political entity.", "", "body-mention", "chp-15:15_CHP-15_sec_i:l16-25#L22"],
]
if any(row[0] in candidate_by_id for row in new_candidates):
    raise SystemExit("a new candidate ID already exists")
candidates.extend(dict(zip(candidate_fields, row)) for row in new_candidates)
candidate_ids = set(candidate_by_id) | {row[0] for row in new_candidates}

new_mentions = [
    ["m-chp15-p362-0088", BODY, "cand-12208", "they", "31", "35", "Pronoun continues the few distinguished men introduced at p.361 L13–14; group membership remains open."],
    ["m-chp15-p362-0089", BODY, "cand-12209", "painting", "61", "69", "Artistic practice from which the unnamed p.361 group tended to turn."],
    ["m-chp15-p362-0090", BODY, "cand-12210", "abate", "651", "656", "Role/status Farsetti adopted according to Haskell; exact office not supplied."],
    ["m-chp15-p362-0091", BODY, "cand-12211", "the arts", "712", "720", "Broad artistic domain; no particular activity is named."],
    ["m-chp15-p362-0092", BODY, "cand-12212", "his contemporaries, and then his successors", "1001", "1044", "Unnamed group credited with judging Farsetti's significance as a patron."],
    ["m-chp15-p362-0093", BODY, "cand-12213", "antique statues", "1247", "1262", "Nested within the existing casts phrase; source does not name individual originals."],
    ["m-chp15-p362-0094", BODY, "cand-12214", "modern sculpture", "1810", "1826", "Category represented by the four named sculptures; distinct from neo-classicism."],
    ["m-chp15-p362-0095", BODY, "cand-12215", "standard Venetian prototypes", "2789", "2817", "Generic architectural comparator, not Venice as a place."],
    ["m-chp15-p362-0096", BODY, "cand-12216", "Austrian pattern", "2859", "2875", "Generic architectural comparator; no Austrian building is identified."],
]
if any(row[0] in mention_by_id for row in new_mentions):
    raise SystemExit("a new mention ID already exists")

# Remove a pronoun fragment that was incorrectly anchored inside the word “they”.
for mention_id, surface, start, end in [
    ("m-chp15-p362-0005", "he", "32", "34"),
    ("m-chp15-p362-0063", "Venetian", "2798", "2806"),
]:
    row = mention_by_id.get(mention_id)
    if row is None or (row["surface_form"], row["start_char"], row["end_char"]) != (surface, start, end):
        raise SystemExit(f"unexpected mention selected for removal: {mention_id}")
    mentions.remove(row)
    del mention_by_id[mention_id]

# Correct index-seed types and promote the architectural components to their own candidates.
remaps = {
    "m-chp15-p362-0036": ("cand-1661", "cand-1660"),
    "m-chp15-p362-0039": ("cand-2355", "cand-2354"),
    "m-chp15-p362-0064": ("cand-10432", "cand-12217"),
    "m-chp15-p362-0065": ("cand-10432", "cand-12218"),
    "m-chp15-p362-0066": ("cand-10432", "cand-12219"),
    "m-chp15-p362-0067": ("cand-10432", "cand-12220"),
    "m-chp15-p362-0050": ("cand-3401", "cand-12221"),
}
for mention_id, (old, new) in remaps.items():
    row = mention_by_id.get(mention_id)
    if row is None or row["candidate_id"] != old:
        raise SystemExit(f"unexpected existing mapping: {mention_id}")
    row["candidate_id"] = new

mentions.extend(dict(zip(mention_fields, row)) for row in new_mentions)

def set_relation(sid, decision, note):
    row = statement_by_id[sid]
    q = row.setdefault("qualifiers", {})
    q["relation_candidate"] = decision
    q["relation_candidate_note"] = note


# Fill endpoints for the newly explicit group, practice, status, and art domain.
row = statement_by_id["st-chp15-p362-men-turn-away-from-painting"]
row["subject_candidate_id"] = "cand-12208"
row["object_candidate_id"] = "cand-12209"
row["qualifiers"]["mentioned_candidate_ids"] = ["cand-12208", "cand-12209"]
row["qualifiers"]["cross_reference_segments"] = [PRECEDING]
row["qualifiers"]["cross_reference_text"] = "P.361 L13–14 introduces the few distinguished men to which p.362 'they' refers."
row["qualifiers"]["relation_candidate_note"] = true_notes[row["statement_id"]]

row = statement_by_id["st-chp15-p362-farsetti-became-abate-to-avoid-political-responsibilities"]
row["object_candidate_id"] = "cand-12210"
row["qualifiers"]["mentioned_candidate_ids"] = ["cand-1002", "cand-12210"]
row["qualifiers"]["relation_candidate_note"] = true_notes[row["statement_id"]]

row = statement_by_id["st-chp15-p362-farsetti-devoted-resources-to-arts"]
row["object_candidate_id"] = "cand-12211"
row["qualifiers"]["mentioned_candidate_ids"] = ["cand-1002", "cand-12211"]
row["qualifiers"]["relation_candidate_note"] = true_notes[row["statement_id"]]

row = statement_by_id["st-chp15-p362-farsetti-considered-most-significant-patron"]
row["subject_candidate_id"] = "cand-12212"
row["object_candidate_id"] = "cand-1002"
row["qualifiers"]["mentioned_candidate_ids"] = ["cand-12212", "cand-1002", "cand-3401"]
row["qualifiers"]["relation_candidate_note"] = true_notes[row["statement_id"]]

row = statement_by_id["st-chp15-p362-casts-from-antiquity-europe-and-rome"]
row["object_candidate_id"] = "cand-12213"
row["qualifiers"]["mentioned_candidate_ids"] = ["cand-1005", "cand-12213", "cand-3462", "cand-4490"]
row["qualifiers"]["relation_candidate_note"] = true_notes[row["statement_id"]]

# Preserve the four named sculpture relations and connect them to the exact category term.
row = statement_by_id["st-chp15-p362-farsetti-selected-four-modern-sculptures"]
row["qualifiers"]["mentioned_candidate_ids"] = ["cand-1002", "cand-12214", "cand-10437", "cand-10439", "cand-10440", "cand-10441"]
row["qualifiers"]["relation_candidate_note"] = false_notes[row["statement_id"]]
sculpture_rows = [
    "st-chp15-p362-risen-christ-selected",
    "st-chp15-p362-bacchus-selected",
    "st-chp15-p362-mercury-selected",
    "st-chp15-p362-neptune-selected",
]
for sid in sculpture_rows:
    q = statement_by_id[sid]["qualifiers"]
    ids = [x for x in q.get("mentioned_candidate_ids", []) if x not in {"cand-1661", "cand-2355", "cand-10448"}]
    ids.extend(["cand-12214"])
    q["mentioned_candidate_ids"] = list(dict.fromkeys(ids))
    q["relation_candidate_note"] = "This is one of the four named works Haskell says Farsetti selected to represent modern sculpture; candidate category remains source-bound and the artwork identity is not independently verified here."

# The Venice adjective in the cosmopolitan sentence names an outlook, not the city.
row = statement_by_id["st-chp15-p362-farsetti-cosmopolitan-outlook"]
row["qualifiers"]["mentioned_candidate_ids"] = ["cand-1002", "cand-1006", "cand-1005", "cand-10432", "cand-12221"]
row["qualifiers"]["relation_candidate_note"] = false_notes[row["statement_id"]]

# Split the villa's two architectural comparisons; collection purpose is already recorded twice.
row = statement_by_id["st-chp15-p362-country-villa-design-description"]
row["object_candidate_id"] = "cand-12215"
row["predicate"] = "differed_from_standard_venetian_villa_prototypes"
row["original_quote"] = "The villa, designed to hold his expanding collections, was wholly unlike the standard Venetian prototypes"
row["qualifiers"]["claim"] = "Haskell says the villa was wholly unlike standard Venetian prototypes."
row["qualifiers"]["qualification"] = "The same sentence says it was designed to hold Farsetti's expanding collections and was in some ways closer to the Austrian pattern; the collection relations are already recorded separately and the Austrian comparison is split into its own statement."
row["qualifiers"]["mentioned_candidate_ids"] = ["cand-10432", "cand-12215", "cand-1005", "cand-1006"]
row["qualifiers"]["relation_candidate_note"] = true_notes[row["statement_id"]]

row = statement_by_id["st-chp15-p362-country-villa-central-convex-bay"]
row["subject_candidate_id"] = "cand-12217"
row["object_candidate_id"] = "cand-12218"
row["predicate"] = "central_convex_bay_projects_from_main_block"
row["qualifiers"]["mentioned_candidate_ids"] = ["cand-12217", "cand-12218", "cand-10432"]
row["qualifiers"]["relation_candidate_note"] = true_notes[row["statement_id"]]

row = statement_by_id["st-chp15-p362-country-villa-wings-and-pavilions"]
row["subject_candidate_id"] = "cand-12218"
row["object_candidate_id"] = "cand-12220"
row["predicate"] = "main_block_joined_by_wings_to_end_pavilions"
row["qualifiers"]["mentioned_candidate_ids"] = ["cand-12218", "cand-12219", "cand-12220", "cand-10432"]
row["qualifiers"]["relation_candidate_note"] = true_notes[row["statement_id"]]

# Classifications that need no endpoint changes beyond the reasons stored above.
for sid, note in true_notes.items():
    set_relation(sid, True, note)
for sid, note in false_notes.items():
    set_relation(sid, False, note)

new_statements = [
    {
        "statement_id": "st-chp15-p362-country-villa-closer-to-austrian-pattern",
        "segment_id": BODY,
        "subject_candidate_id": "cand-10432",
        "object_candidate_id": "cand-12216",
        "predicate": "closer_to_austrian_architectural_pattern_in_some_respects",
        "qualifiers": {
            "source_line_start": 24, "source_line_end": 24,
            "printed_page": 362, "pdf_physical_page": 2,
            "claim": "Haskell says the villa was in some ways much closer to the Austrian pattern.",
            "speaker": "Haskell", "text_layer": "authorial architectural comparison",
            "qualification": "The comparison is qualified by 'in some ways'; the source names no specific Austrian building or design.",
            "mentioned_candidate_ids": ["cand-10432", "cand-12216"],
            "relation_candidate": True,
            "relation_candidate_note": "The source directly compares the villa with an architectural pattern; the comparator remains a generic term rather than a guessed building.",
        },
        "original_quote": "The villa, designed to hold his expanding collections, was wholly unlike the standard Venetian prototypes, and was in some ways much closer to the Austrian pattern.",
        "origin": "book", "source_file": "02-sources/02-Markdown/15_CHP-15_sec_i.md",
    }
]
if any(row["statement_id"] in statement_by_id for row in new_statements):
    raise SystemExit("new statement ID already exists")
statements.extend(new_statements)

# Validate all new spans and the new statement quote against S0.
segments = {
    row["segment_id"]: row
    for row in (
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    )
}
segment = segments[BODY]
source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
source_text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
for row in new_mentions:
    if source_text[int(row[4]):int(row[5])] != row[3]:
        raise SystemExit(f"source span mismatch: {row[0]}")
if new_statements[0]["original_quote"] not in source_text:
    raise SystemExit("Austrian-pattern statement quote is not in the source")

candidate_ids.update(row["candidate_id"] for row in candidates)
for row in statements:
    if row["statement_id"].startswith("st-chp15-p362-"):
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint and endpoint not in candidate_ids:
                raise SystemExit(f"unknown p362 endpoint {endpoint} in {row['statement_id']}")
        for endpoint in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if endpoint not in candidate_ids:
                raise SystemExit(f"unknown p362 mention endpoint {endpoint} in {row['statement_id']}")

p362 = [row for row in statements if row.get("segment_id") == BODY]
counts = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in p362)
if len(p362) != 48 or counts[True] != 41 or counts[False] != 7 or counts[None] != 0:
    raise SystemExit(f"unexpected p362 closure: {len(p362)} {counts}")

# Verify segment-local candidate references and preserve the non-crossing span contract.
id_to_candidate = {row["candidate_id"] for row in candidates}
for row in mentions:
    if row["candidate_id"] not in id_to_candidate:
        raise SystemExit(f"unknown candidate in {row['mention_id']}")
by_segment = {}
for row in mentions:
    by_segment.setdefault(row["segment_id"], []).append(
        (int(row["start_char"]), int(row["end_char"]), row["mention_id"])
    )
for segment_id, spans in by_segment.items():
    spans.sort()
    for index, first in enumerate(spans):
        for second in spans[index + 1:]:
            if second[0] >= first[1]:
                break
            nested = (first[0] <= second[0] and second[1] <= first[1]) or (second[0] <= first[0] and first[1] <= second[1])
            if first[:2] == second[:2] or not nested:
                raise SystemExit(f"crossing or duplicate spans in {segment_id}: {first[2]} / {second[2]}")


def csv_bytes(fields, rows):
    from io import StringIO

    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


outputs = {
    PATHS["statements"]: ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8"),
    PATHS["mentions"]: csv_bytes(mention_fields, mentions),
    PATHS["candidates"]: csv_bytes(candidate_fields, candidates),
}
print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "p362": {"statements": len(p362), "true": counts[True], "false": counts[False], "unset": counts[None]},
    "new_candidates": len(new_candidates),
    "new_mentions": len(new_mentions),
    "removed_bad_or_misleading_mentions": ["m-chp15-p362-0005", "m-chp15-p362-0063"],
    "corrected_mentions": remaps,
    "new_statement": new_statements[0]["statement_id"],
    "validated_new_spans": len(new_mentions),
    "crossings": 0,
    "after_sha256": {str(path.relative_to(ROOT)): sha(data) for path, data in outputs.items()},
}, ensure_ascii=False, indent=2))

if args.apply:
    temporary = {}
    for path, data in outputs.items():
        backup = path.with_name(path.name + BACKUP_TAG)
        key = next(name for name, current in PATHS.items() if current == path)
        if backup.exists():
            if sha(backup.read_bytes()) != EXPECTED[key]:
                raise SystemExit(f"backup differs: {backup.name}")
        else:
            shutil.copy2(path, backup)
        with tempfile.NamedTemporaryFile("wb", delete=False, dir=path.parent) as handle:
            handle.write(data)
            temporary[path] = Path(handle.name)
    for path, temp_path in temporary.items():
        temp_path.replace(path)
    print(json.dumps({"written_sha256": {str(path.relative_to(ROOT)): sha(path.read_bytes()) for path in outputs}}, indent=2))
