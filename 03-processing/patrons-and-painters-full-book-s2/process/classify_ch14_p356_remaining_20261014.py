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
    "statements": "129623ae3d36f9a324a267c68cd73fd30fa2aa6d3f8d36c6b9292025c2f9ffab",
    "mentions": "ff924bd52323fd956742b507b71758d603f161d62ea2538a08782833e500e5ca",
    "candidates": "7aaf5f670b43ebd1e094b42aa08a31cc210eaf6a77007c7716136ccfbcc58066",
}
BACKUP_TAG = ".bak-s2-ch14-p356-semantic-review-20261014"
BODY = "chp-14:14_CHP-14_intro:l97-105"
NOTES = "chp-14:14_CHP-14_intro:l168-220"

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
    "st-chp14-p356-promoted-italian-venetian-art-abroad":
        "Haskell describes Algarotti's promotion of Italian, especially Venetian, art abroad as a distinct activity and attributes patriotism as one motive. The art tradition is represented by a source-defined term candidate; no individual work or completed transfer is inferred.",
    "st-chp14-p356-expensive-presents-to-influential-people":
        "Haskell describes Algarotti's disposition toward expensive gifts to people he considered suitable. The recipient class remains unnamed and is kept separate from the named Walpole and Pitt examples.",
    "st-chp14-p356-kept-in-touch-with-venetian-market":
        "The first clause explicitly states Algarotti remained in touch with the Venetian art market. The following search for pictures for new patrons is split into a separate candidate relation.",
    "st-chp14-p356-algarotti-saw-neo-palladianism-in-england":
        "Haskell says Algarotti had encountered neo-Palladianism in England some years earlier. The source gives no exact date or building, and the term remains the p.356 source-defined concept.",
    "st-chp14-p356-letter-to-acquaintances-for-supply-partial":
        "The sentence begins on p.356 and continues on p.357, where Haskell identifies the requested prints as views of Genoese palaces, churches, and country houses. The prints remain an unnamed work group; no individual views are inferred.",
    "st-chp14-p356-note1-bonomo-canaletto-price-time":
        "Haskell's note quotes Bonomo reporting that Canaletto would ask a considerable price and several years to complete paintings because commissions pressed him. The cited manuscript was not independently consulted and the antecedent of farli remains unresolved.",
    "st-chp14-p356-note4-carcassonne-letter":
        "Haskell quotes Algarotti's conditional proposal to Bonomo to acquire the unidentified Veronese painting if its price were moderate, as a gift for Horace Walpole in England. This is a proposal, not evidence of purchase or delivery; the letter is the cited source.",
    "st-chp14-p356-note5-treat-diderot-quotation":
        "Haskell reproduces through Treat a passage attributed to Diderot, in which Diderot characterizes Algarotti's testamentary gifts as a public display of friendship with great men and vanity. The secondary quotation chain is preserved and neither Treat nor the underlying source was independently consulted.",
}
false_notes = {
    "st-chp14-p356-prestige-through-successful-coup":
        "This is Haskell's generalized interpretation of Algarotti's prestige and success, without a separately identified event or mapped endpoint. Preserve it as an attributed assertion rather than forcing an unnamed event into the graph.",
    "st-chp14-p356-saw-opportunities-for-financial-gain":
        "This is Haskell's interpretation of Algarotti's motive; the cited December 1742 letters are only located, not described or independently consulted, so no distinct transaction endpoint is established here.",
    "st-chp14-p356-note2-letters-1749":
        "The note is a locator for four separately dated archive candidates. It gives no senders, recipients, or contents, so it adds no independently supported relationship edge.",
    "st-chp14-p356-note3-letters-1750-1752":
        "The note is a locator for two separately dated archive candidates. It gives no senders, recipients, or contents, so it adds no independently supported relationship edge.",
    "st-chp14-p356-note6-letters-december-1742":
        "The note locates letters by month and manuscript collection but supplies no individual date, sender, recipient, or content; it is retained as a bibliographic assertion, not a relationship edge.",
    "st-chp14-p356-note7-frederick-letters":
        "This existing row is retained as the bibliographic locator for Opere XV. The two explicitly addressed letters are represented separately below, without assuming their authorship or contents.",
}

for sid, note in {**true_notes, **false_notes}.items():
    if sid not in statement_by_id:
        raise SystemExit(f"missing expected p356 statement: {sid}")
    qualifiers = statement_by_id[sid].setdefault("qualifiers", {})
    if qualifiers.get("relation_candidate") is not None:
        raise SystemExit(f"unexpected pre-classified p356 statement: {sid}")
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
if max(int(cid.split("-")[1]) for cid in candidate_by_id) != 12201:
    raise SystemExit("candidate ID sequence changed")
if max(int(mid.rsplit("-", 1)[1]) for mid in mention_by_id if mid.startswith("m-chp14-p356-")) != 72:
    raise SystemExit("p356 mention ID sequence changed")

new_candidates = [
    ["cand-12202", "", "Italian and especially Venetian art promoted abroad (p.356)", "", "term", "open", "", "", "Haskell names a broad art tradition Algarotti sought to promote abroad; this candidate records the source's concept use, not a list of individual works or a completed transfer.", "", "body-mention", "chp-14:14_CHP-14_intro:l97-105#L101"],
    ["cand-12203", "", "People considered suitable recipients of Algarotti's expensive presents (unnamed role group, p.356)", "", "term", "open", "", "", "Haskell's unnamed recipient class; do not identify it with Horace Walpole, William Pitt, or other named recipients without separate evidence.", "", "body-mention", "chp-14:14_CHP-14_intro:l97-105#L102"],
    ["cand-12204", "", "Venetian art market in Algarotti's account (p.356)", "", "term", "open", "", "", "The market is an economic and cultural context in Haskell's account, not a named organization or building.", "", "body-mention", "chp-14:14_CHP-14_intro:l97-105#L102"],
    ["cand-12205", "", "Unidentified pictures Algarotti sought for his new patrons (p.356)", "", "work", "open", "", "", "Haskell describes pictures Algarotti looked for because he thought they might appeal to new patrons; the works are not individually identified and are distinct from the suitable examples sought for disposal abroad.", "", "body-mention", "chp-14:14_CHP-14_intro:l97-105#L102"],
    ["cand-12206", "", "Algarotti's new patrons referred to on p.356 (unnamed role group)", "", "term", "open", "", "", "The source does not name or enumerate the patrons; do not equate them with the Dresden or Berlin patrons without further evidence.", "", "body-mention", "chp-14:14_CHP-14_intro:l97-105#L102"],
    ["cand-12207", "", "King of Prussia referred to in the Diderot passage about Algarotti's will (p.356 n.5; identity unresolved)", "", "person", "open", "", "", "The French quotation says roi de Prusse but does not name the king. Keep the identity open; do not merge with Frederick the Great from context alone.", "", "body-mention", "chp-14:14_CHP-14_intro:l168-220#L198"],
]
if any(row[0] in candidate_by_id for row in new_candidates):
    raise SystemExit("a new candidate ID already exists")
candidates.extend(dict(zip(candidate_fields, row)) for row in new_candidates)
candidate_ids = {row[0] for row in new_candidates}

new_mentions = [
    ["m-chp14-p356-0073", BODY, "cand-12202", "Italian (and especially Venetian) art abroad", "708", "752", "Source-defined art tradition; no specific works enumerated."],
    ["m-chp14-p356-0074", BODY, "cand-12203", "the right people", "1484", "1500", "Unnamed intended-recipient class; not aligned to the named examples."],
    ["m-chp14-p356-0075", BODY, "cand-12204", "the Venetian art market", "1924", "1947", "Economic and cultural context, not a named institution."],
    ["m-chp14-p356-0076", BODY, "cand-12205", "pictures that he thought might appeal", "1967", "2004", "Unidentified work group, distinct from pictures sought for disposal abroad."],
    ["m-chp14-p356-0077", BODY, "cand-12206", "his new patrons", "2008", "2023", "Unnamed patron class; identity and membership unresolved."],
    ["m-chp14-p356-0078", NOTES, "cand-0057", "son testament", "4476", "4489", "Coreference in the Diderot passage quoted via Treat; the pronoun refers to Algarotti in the note's context."],
]
if any(row[0] in mention_by_id for row in new_mentions):
    raise SystemExit("a new mention ID already exists")
mentions.extend(dict(zip(mention_fields, row)) for row in new_mentions)

# Correct two source-anchored endpoint assignments supported by the printed page.
for mention_id, expected_candidate, replacement in [
    ("m-chp14-p356-0059", "cand-2755", "cand-10331"),
    ("m-chp14-p356-0064", "cand-10246", "cand-12207"),
]:
    row = mention_by_id.get(mention_id)
    if row is None or row["candidate_id"] != expected_candidate:
        raise SystemExit(f"unexpected mention mapping: {mention_id}")
    row["candidate_id"] = replacement

# Add the source-defined endpoints to their statements.
by = statement_by_id
row = by["st-chp14-p356-promoted-italian-venetian-art-abroad"]
row["object_candidate_id"] = "cand-12202"
row["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(row["qualifiers"].get("mentioned_candidate_ids", []) + ["cand-12202"]))
row["qualifiers"]["relation_candidate_note"] = true_notes[row["statement_id"]]

row = by["st-chp14-p356-expensive-presents-to-influential-people"]
row["object_candidate_id"] = "cand-12203"
row["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(row["qualifiers"].get("mentioned_candidate_ids", []) + ["cand-12203"]))

row = by["st-chp14-p356-kept-in-touch-with-venetian-market"]
row["object_candidate_id"] = "cand-12204"
row["predicate"] = "kept_in_touch_with_venetian_art_market"
row["original_quote"] = "and he kept fully in touch with the Venetian art market"
row["qualifiers"]["claim"] = "Haskell says Algarotti kept fully in touch with the Venetian art market."
row["qualifiers"]["qualification"] = "The following clause about seeking pictures that might appeal to new patrons is recorded separately. This is Haskell's account of continued contact, not proof of purchases or specific transactions."
row["qualifiers"]["mentioned_candidate_ids"] = ["cand-0063", "cand-12204"]

row = by["st-chp14-p356-algarotti-saw-neo-palladianism-in-england"]
row["qualifiers"]["relation_candidate_note"] = true_notes[row["statement_id"]]

row = by["st-chp14-p356-letter-to-acquaintances-for-supply-partial"]
row["qualifiers"]["cross_reference_segments"] = ["chp-14:14_CHP-14_intro:l107-116"]
row["qualifiers"]["cross_reference_text"] = "p.357 L108 closes the p.356 sentence by specifying prints of Genoese palaces, churches, and country houses."

# Keep the note's conditions and the actual work and intended recipient as endpoints.
row = by["st-chp14-p356-note4-carcassonne-letter"]
row["subject_candidate_id"] = "cand-0057"
row["object_candidate_id"] = "cand-10331"
row["predicate"] = "conditionally_proposed_to_acquire_veronese_for_walpole"
row["qualifiers"]["claim"] = "P.356 note 4 quotes Algarotti's conditional proposal to Bonomo to acquire the unidentified Veronese painting if its price were moderate, as a gift for Horace Walpole in England, to facilitate an unspecified idea."
row["qualifiers"]["speaker"] = "Haskell quoting Algarotti through a bibliographic note"
row["qualifiers"]["text_layer"] = "authorial bibliographic note quoting a letter"
row["qualifiers"]["qualification"] = "The proposal is conditional and establishes neither purchase nor delivery. The cited manuscript was not independently consulted; Walpole is the intended recipient, while the Veronese work is the direct object."
row["qualifiers"]["mentioned_candidate_ids"] = ["cand-0057", "cand-10338", "cand-0040", "cand-10331", "cand-2798"]

# Recast the note 5 quotation as Diderot's attributed comment and keep its chain.
row = by["st-chp14-p356-note5-treat-diderot-quotation"]
row["subject_candidate_id"] = "cand-0919"
row["object_candidate_id"] = "cand-0057"
row["predicate"] = "characterized_algarotti_bequests_as_public_display_of_friendship_and_vanity"
row["qualifiers"]["claim"] = "Haskell reproduces through Treat a passage attributed to Diderot, in which Diderot characterizes Algarotti's testamentary gifts as a public display of friendship with great men and vanity."
row["qualifiers"]["speaker"] = "Diderot as attributed by Haskell through Treat"
row["qualifiers"]["text_layer"] = "authorial bibliographic note; secondary quotation attributed to Diderot"
row["qualifiers"]["qualification"] = "Haskell cites Treat p.209 and does not identify a primary Diderot source here. Neither Treat nor the underlying source was independently consulted. The King of Prussia is retained as an unnamed person candidate in a separate statement."
row["qualifiers"]["mentioned_candidate_ids"] = ["cand-0919", "cand-0057", "cand-10345", "cand-10231", "cand-12207", "cand-1947"]
row["qualifiers"]["cross_reference_segments"] = [BODY]
row["qualifiers"]["cross_reference_text"] = "The preceding p.356 body text identifies Diderot as the commentator whose remark is quoted in this note."

# The p.356/p.357 sentence contains two distinct relational clauses; preserve both.
new_statements = [
    {
        "statement_id": "st-chp14-p356-sought-pictures-for-new-patrons",
        "segment_id": BODY,
        "subject_candidate_id": "cand-0063",
        "object_candidate_id": "cand-12205",
        "predicate": "sought_pictures_likely_to_appeal_to_new_patrons",
        "qualifiers": {
            "source_line_start": 102, "source_line_end": 102,
            "printed_page": 356, "pdf_physical_page": 10,
            "claim": "Haskell says Algarotti looked out for pictures that he thought might appeal to his new patrons.",
            "speaker": "Haskell", "text_layer": "authorial report",
            "qualification": "The pictures and patrons are unnamed; this is a search, not evidence of acquisition. It is distinct from the suitable examples sought for disposal abroad.",
            "mentioned_candidate_ids": ["cand-0063", "cand-12205", "cand-12206"],
            "relation_candidate": True,
            "relation_candidate_note": "The sentence explicitly connects Algarotti's search to a source-defined group of pictures and says why he sought them; unknown works and patrons remain open.",
        },
        "original_quote": "and looked out for pictures that he thought might appeal to his new patrons.",
        "origin": "book", "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
    },
    {
        "statement_id": "st-chp14-p356-note7-letter-1751-08-04-to-frederick",
        "segment_id": NOTES,
        "subject_candidate_id": "cand-10340", "object_candidate_id": "cand-1080",
        "predicate": "letter_addressed_to",
        "qualifiers": {
            "source_line_start": 200, "source_line_end": 200,
            "printed_page": 356, "pdf_physical_page": 10,
            "claim": "Haskell identifies a letter dated 4 August 1751 as addressed to Frederick the Great and published in Opere, volume XV, pages 153–155.",
            "speaker": "Haskell", "text_layer": "authorial bibliographic note",
            "qualification": "The letter and edition were not independently consulted; this note does not identify the sender or state the letter's contents.",
            "mentioned_candidate_ids": ["cand-10340", "cand-1080", "cand-10229"],
            "relation_candidate": True,
            "relation_candidate_note": "The note explicitly identifies this dated letter as addressed to Frederick; no sender or contents are inferred.",
        },
        "original_quote": "letters to Frederick the Great of 4 August",
        "origin": "book", "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
    },
    {
        "statement_id": "st-chp14-p356-note7-letter-1751-12-13-to-frederick",
        "segment_id": NOTES,
        "subject_candidate_id": "cand-10350", "object_candidate_id": "cand-1080",
        "predicate": "letter_addressed_to",
        "qualifiers": {
            "source_line_start": 200, "source_line_end": 200,
            "printed_page": 356, "pdf_physical_page": 10,
            "claim": "Haskell identifies a letter dated 13 December 1751 as addressed to Frederick the Great and published in Opere, volume XV, pages 153–155.",
            "speaker": "Haskell", "text_layer": "authorial bibliographic note",
            "qualification": "The letter and edition were not independently consulted; this note does not identify the sender or state the letter's contents.",
            "mentioned_candidate_ids": ["cand-10350", "cand-1080", "cand-10229"],
            "relation_candidate": True,
            "relation_candidate_note": "The note explicitly identifies this dated letter as addressed to Frederick; no sender or contents are inferred.",
        },
        "original_quote": "and 13 December 1751",
        "origin": "book", "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
    },
    {
        "statement_id": "st-chp14-p356-note5-diderot-prussian-king-bequest",
        "segment_id": NOTES,
        "subject_candidate_id": "cand-0057", "object_candidate_id": "cand-12207",
        "predicate": "bequeathed_remembrance_to_king_of_prussia_as_reported_by_diderot",
        "qualifiers": {
            "source_line_start": 198, "source_line_end": 198,
            "printed_page": 356, "pdf_physical_page": 10,
            "claim": "In the passage attributed to Diderot and quoted by Treat, Algarotti left a testamentary remembrance to the King of Prussia.",
            "speaker": "Diderot as attributed by Haskell through Treat",
            "text_layer": "secondary quotation reproduced in an authorial bibliographic note",
            "qualification": "The recipient is identified only as roi de Prusse; identity remains unresolved. The quote describes a remembrance, not an identified artwork or other object. This statement is mediated through Treat and has not been independently checked.",
            "mentioned_candidate_ids": ["cand-0057", "cand-12207", "cand-0919", "cand-10231", "cand-10345"],
            "cross_reference_segments": [BODY],
            "cross_reference_text": "The p.356 body identifies Diderot as commentator; note 5 supplies the attributed quoted passage.",
            "relation_candidate": True,
            "relation_candidate_note": "The attributed passage explicitly connects Algarotti's testamentary remembrance to the King of Prussia; the recipient's identity and the object remain unresolved.",
        },
        "original_quote": "une marque de souvenir au roi de Prusse",
        "origin": "book", "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
    },
]
existing_statement_ids = set(statement_by_id)
if any(row["statement_id"] in existing_statement_ids for row in new_statements):
    raise SystemExit("new statement ID already exists")
statements.extend(new_statements)

# Resolve every new text anchor against the exact S0 segment text.
segments = {
    row["segment_id"]: row
    for row in (
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    )
}
segment_text = {}
for mention in new_mentions:
    segment = segments[mention[1]]
    lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    segment_text.setdefault(mention[1], "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"])]))
    if segment_text[mention[1]][int(mention[4]):int(mention[5])] != mention[3]:
        raise SystemExit(f"source span mismatch: {mention[0]}")

for row in new_statements:
    segment = segments[row["segment_id"]]
    lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"] )])
    if row["original_quote"] not in text:
        raise SystemExit(f"statement quote is not in source segment: {row['statement_id']}")

# Confirm the endpoint and mention mappings used by these p.356 statements.
candidate_ids.update(row["candidate_id"] for row in candidates)
for row in statements:
    if row["statement_id"].startswith("st-chp14-p356-"):
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint and endpoint not in candidate_ids:
                raise SystemExit(f"unknown p356 endpoint {endpoint} in {row['statement_id']}")
        for endpoint in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if endpoint not in candidate_ids:
                raise SystemExit(f"unknown p356 mention endpoint {endpoint} in {row['statement_id']}")

p356 = [row for row in statements if row["statement_id"].startswith("st-chp14-p356-")]
counts = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in p356)
if len(p356) != 34 or counts[True] != 25 or counts[False] != 9 or counts[None] != 0:
    raise SystemExit(f"unexpected p356 closure: {len(p356)} {counts}")

# Nested source anchors are allowed; crossing spans and exact duplicate spans are not.
by_segment = {}
for mention in mentions:
    by_segment.setdefault(mention["segment_id"], []).append(
        (int(mention["start_char"]), int(mention["end_char"]), mention["mention_id"])
    )
for segment_id, spans in by_segment.items():
    spans.sort()
    for index, first in enumerate(spans):
        for second in spans[index + 1:]:
            if second[0] >= first[1]:
                break
            nested = (first[0] <= second[0] and second[1] <= first[1]) or (second[0] <= first[0] and first[1] <= second[1])
            if first[:2] == second[:2] or not nested:
                raise SystemExit(f"crossing or duplicate mention spans in {segment_id}: {first[2]} / {second[2]}")


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
    "p356": {"statements": len(p356), "true": counts[True], "false": counts[False], "unset": counts[None]},
    "new_candidates": [row[0] for row in new_candidates],
    "new_mentions": len(new_mentions),
    "corrected_mentions": {"Veronese painting": "m-chp14-p356-0059", "King of Prussia identity unresolved": "m-chp14-p356-0064"},
    "new_statements": [row["statement_id"] for row in new_statements],
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
