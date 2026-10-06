"""Controlled S2 migration for p.338 footnotes; dry-run by default."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
BODY = "chp-13:13_CHP-13_intro:l61-68"
NOTES = "chp-13:13_CHP-13_intro:l179-251"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BACKUP_SUFFIX = ".bak-s2-chp13-p338-notes-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.338 footnote migration")
args = parser.parse_args()


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical chapter 13 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-13 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
expected_prefixes = {
    209: "1 Delle Commedie di Carlo Goldoni avvocato veneto, Vol. H, 1762, p. 1.",
    210: "2 See Lettera del Magnifico Signor Antonio Zatta",
}
for line_number, prefix in expected_prefixes.items():
    if not source_lines[line_number - 1].startswith(prefix):
        raise SystemExit(f"canonical source changed at L{line_number}")

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
    len(candidates), max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions), len(statements),
)
if state != (10163, 10176, 21976, 9819):
    raise SystemExit(f"unexpected table pre-state: {state}")
if BODY not in coverage or NOTES not in coverage:
    raise SystemExit("required coverage row missing")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.338 body is not reviewed/partial")
if (coverage[NOTES]["disposition"], coverage[NOTES]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("consolidated notes segment is not reviewed/partial")
if any(row["statement_id"].startswith("st-chp13-p338-note") for row in statements):
    raise SystemExit("p.338 note statements already exist")

body_ids = {
    "goldoni_frontispiece": "st-chp13-p338-goldoni-proposed-life-scenes-on-frontispieces",
    "false_vignola": "st-chp13-p338-pasquali-dedicated-vignola-edition-to-lodoli",
    "zatta_support": "st-chp13-p338-zatta-combatively-supported-jesuits",
    "false_zatta_publications": "st-chp13-p338-zatta-proposed-jesuit-polemical-publications",
}
if set(body_ids.values()) - set(statement_by_id):
    raise SystemExit("one or more expected p.338 body statements are missing")
for key, marker in (("goldoni_frontispiece", 1), ("false_vignola", 1), ("zatta_support", 2), ("false_zatta_publications", 2)):
    if statement_by_id[body_ids[key]]["qualifiers"].get("footnote_marker") != marker:
        raise SystemExit(f"expected p.338 footnote marker {marker} missing from {body_ids[key]}")

candidate_specs = [
    ("cand-10177", "Delle Commedie di Carlo Goldoni avvocato veneto, vol. II (1762), p.1", "archive",
     "Citation locator in p.338 note 1 for Goldoni’s frontispiece proposal. The note is cited by Haskell; the volume and page were not independently consulted.", 209),
    ("cand-10178", "Lettera del Magnifico Signor Antonio Zatta to an unnamed Duke (1761; imprint printed as Fiorenza, corrected by Haskell to Venice)", "archive",
     "Title is incomplete in Haskell’s note: the Duke’s name is omitted. The note prints Fiorenza and adds “[in fact, Venice]”; do not infer a named recipient or treat Florence as the actual place of publication.", 210),
    ("cand-10179", "Lettera Giustificativa di Antonio Zatta (Venice, 1761)", "archive",
     "Publication cited in p.338 note 2. The cited work was not independently consulted.", 210),
]
new_candidates = []
for candidate_id, name, kind, detail, line_number in candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if any(row["canonical_name"] == name for row in candidates):
        raise SystemExit(f"candidate name already exists: {name}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": candidate_id, "canonical_name": name, "suggested_type": kind,
        "status": "open", "detail": detail, "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES}#L{line_number}",
    })
    new_candidates.append(row)
all_candidate_ids = set(candidate_by_id) | {row["candidate_id"] for row in new_candidates}
for candidate_id in ("cand-1205", "cand-1851", "cand-2865", "cand-1321", "cand-3401"):
    if candidate_id not in all_candidate_ids:
        raise SystemExit(f"required reused candidate is missing: {candidate_id}")

def segment_text(start_line, end_line):
    return "\n".join(source_lines[start_line - 1:end_line])


mention_specs = [
    (209, "Delle Commedie di Carlo Goldoni avvocato veneto, Vol. H, 1762, p. 1", "cand-10177", "Citation locator follows canonical OCR; the print reads vol. II."),
    (209, "Carlo Goldoni", "cand-1205", "Author named in the citation; existing person candidate reused."),
    (210, "Lettera del Magnifico Signor Antonio Zatta a Sua Eccellenza il Signor Duca di...", "cand-10178", "First cited letter; the Duke is unnamed in the printed title."),
    (210, "Antonio Zatta", "cand-2865", "Author named in the first cited letter; identity alignment remains for S3."),
    (210, "Fiorenza [in fact, Venice]", "cand-3401", "Imprint location as printed and corrected by Haskell; map to Venice and preserve the correction, not Florence as the actual place."),
    (210, "Lettera Giustificativa di Antonio Zatta", "cand-10179", "Second cited letter, published in Venice in 1761."),
    (210, "Antonio Zatta", "cand-2865", "Author named again in the second cited letter; second occurrence on the source line."),
    (210, "Venezia", "cand-3401", "Publication place named for the second letter; existing Venice place candidate reused."),
    (210, "Jesuits", "cand-1321", "Religious order whose support is discussed in Haskell’s note."),
]
existing_mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}
new_mentions = []
line_occurrences = {}
for index, (line_number, surface, candidate_id, note) in enumerate(mention_specs, start=1):
    if candidate_id not in all_candidate_ids:
        raise SystemExit(f"candidate FK missing for mention {surface!r}: {candidate_id}")
    line_text = source_lines[line_number - 1]
    positions = []
    cursor = 0
    while True:
        position = line_text.find(surface, cursor)
        if position < 0:
            break
        positions.append(position)
        cursor = position + 1
    if not positions:
        raise SystemExit(f"mention text is not exact at L{line_number}: {surface!r}")
    occurrence_key = (line_number, surface)
    occurrence = line_occurrences.get(occurrence_key, 0)
    if occurrence >= len(positions):
        raise SystemExit(f"requested occurrence not found at L{line_number}: {surface!r}")
    line_occurrences[occurrence_key] = occurrence + 1
    local_lines = source_lines[178:251]
    offset = sum(len(line) + 1 for line in local_lines[:line_number - 179]) + positions[occurrence]
    end = offset + len(surface)
    text = segment_text(179, 251)
    if text[offset:end] != surface:
        raise SystemExit(f"mention offset mismatch at L{line_number}: {surface!r}")
    key = (NOTES, candidate_id, str(offset), str(end))
    if key in existing_mention_keys:
        raise SystemExit(f"mention already exists at L{line_number}: {surface!r} -> {candidate_id}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch13-p338-notes-{index:03d}", "segment_id": NOTES,
        "candidate_id": candidate_id, "surface_form": surface,
        "start_char": offset, "end_char": end, "note": note,
    })
    new_mentions.append(row)
    existing_mention_keys.add(key)

note_links = {
    1: [body_ids["goldoni_frontispiece"]],
    2: [body_ids["zatta_support"]],
}
ocr_209 = [{
    "source_line": 209, "ocr": "Vol. H", "print": "Vol. II",
    "basis": "CHP-13.pdf physical page 7; visual reading of the Roman numeral.",
}]

statement_specs = [
    {
        "id": "st-chp13-p338-note1-goldoni-volume2-page1-citation", "line": 209,
        "subject": "cand-10177", "object": "cand-1851", "predicate": "cites_goldoni_volume_two_page_one_for_frontispiece_proposal",
        "claim": "Printed note 1 cites volume II of Delle Commedie di Carlo Goldoni avvocato veneto (1762), page 1, for Goldoni’s frontispiece proposal.",
        "qualification": "Citation locator as reported by Haskell; the cited volume and page were not independently consulted.",
        "mentioned": ["cand-10177", "cand-1205", "cand-1851"], "linked": note_links[1],
        "number": 1, "layer": "bibliographic citation locator",
        "quote": "Delle Commedie di Carlo Goldoni avvocato veneto, Vol. H, 1762, p. 1.",
        "citations": [{"source_candidate_id": "cand-10177", "author_candidate_id": "cand-1205", "related_work_candidate_id": "cand-1851", "year": "1762", "volume": "II", "page": "1"}],
        "ocr_corrections": ocr_209,
    },
    {
        "id": "st-chp13-p338-note2-zatta-letter-to-unnamed-duke", "line": 210,
        "subject": "cand-2865", "object": "cand-10178", "predicate": "addressed_1761_letter_to_unidentified_duke",
        "claim": "Haskell cites a 1761 letter by Antonio Zatta addressed to an unnamed Duke; its imprint is printed as Fiorenza and corrected in brackets to Venice.",
        "qualification": "The title ends with an ellipsis, so the recipient cannot be identified. Preserve Haskell’s bracketed venue correction; the letter was not independently consulted.",
        "mentioned": ["cand-2865", "cand-10178", "cand-3401"], "linked": note_links[2],
        "number": 2, "layer": "bibliographic citation locator",
        "quote": "Lettera del Magnifico Signor Antonio Zatta a Sua Eccellenza il Signor Duca di... . In Fiorenza [in fact, Venice], 1761",
        "citations": [{"source_candidate_id": "cand-10178", "author_candidate_id": "cand-2865", "recipient_description": "unnamed Duke", "year": "1761", "imprint_as_printed": "Fiorenza", "imprint_correction": "Venice"}],
    },
    {
        "id": "st-chp13-p338-note2-zatta-justificatory-letter", "line": 210,
        "subject": "cand-2865", "object": "cand-10179", "predicate": "published_justificatory_letter_in_1761",
        "claim": "Haskell also cites Lettera Giustificativa di Antonio Zatta, published in Venice in 1761.",
        "qualification": "The cited work is identified from the printed note only and was not independently consulted.",
        "mentioned": ["cand-2865", "cand-10179", "cand-3401"], "linked": note_links[2],
        "number": 2, "layer": "bibliographic citation locator",
        "quote": "Lettera Giustificativa di Antonio Zatta, Venezia, 1761.",
        "citations": [{"source_candidate_id": "cand-10179", "author_candidate_id": "cand-2865", "year": "1761", "imprint": "Venezia"}],
    },
    {
        "id": "st-chp13-p338-note2-haskell-assesses-zatta-jesuit-support", "line": 210,
        "subject": "cand-2865", "object": "cand-1321", "predicate": "haskell_says_published_letters_showed_jesuit_support",
        "claim": "Haskell says earlier doubt about Zatta’s position on the Jesuits is resolved by the published material, which he reads as showing strong support for them.",
        "qualification": "This is Haskell’s interpretation and confidence statement, not an independent assessment of the letters or of the controversy.",
        "mentioned": ["cand-2865", "cand-1321", "cand-10178", "cand-10179"], "linked": note_links[2],
        "number": 2, "layer": "authorial interpretation in footnote",
        "quote": "Because of Zatta’s sarcasm and devious way of conducting an argument there has hitherto been some controversy about his position in relation to the Jesuits. The material published here makes it clear beyond doubt that he strongly supported them.",
        "relation_candidate": True,
    },
]

for spec in statement_specs:
    if spec["quote"] not in source_lines[spec["line"] - 1]:
        raise SystemExit(f"statement quote is not an exact source substring: {spec['id']}")

new_statements = []
for spec in statement_specs:
    if spec["id"] in statement_by_id:
        raise SystemExit(f"statement ID already exists: {spec['id']}")
    missing = [candidate_id for candidate_id in spec["mentioned"] if candidate_id not in all_candidate_ids]
    if missing:
        raise SystemExit(f"statement {spec['id']} has missing candidate references: {missing}")
    qualifiers = {
        "source_line_start": spec["line"], "source_line_end": spec["line"],
        "printed_page": 338, "pdf_physical_page": 7, "claim": spec["claim"],
        "speaker": "Haskell, printed footnote", "text_layer": spec["layer"],
        "qualification": spec["qualification"], "mentioned_candidate_ids": spec["mentioned"],
        "footnote_number": spec["number"], "linked_body_statement_ids": spec["linked"],
    }
    for optional in ("citations", "ocr_corrections"):
        if optional in spec:
            qualifiers[optional] = spec[optional]
    if spec.get("relation_candidate"):
        qualifiers["relation_candidate"] = True
    new_statements.append({
        "statement_id": spec["id"], "segment_id": NOTES,
        "subject_candidate_id": spec["subject"], "object_candidate_id": spec["object"],
        "predicate": spec["predicate"], "qualifiers": qualifiers,
        "original_quote": spec["quote"], "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
    })

for marker, linked_ids in note_links.items():
    for linked_id in linked_ids:
        if linked_id not in statement_by_id:
            raise SystemExit(f"footnote target statement missing: {linked_id}")
    note_ids = [row["statement_id"] for row in new_statements if row["qualifiers"]["footnote_number"] == marker]
    note_ref = {
        "footnote_marker": str(marker), "footnote_printed_page": 338,
        "footnote_text_pending": False, "footnote_segment": NOTES,
        "footnote_line_range": f"L{209 if marker == 1 else 210}",
        "footnote_body_link_status": "linked", "footnote_note_statement_ids": note_ids,
    }
    for linked_id in linked_ids:
        qualifiers = statement_by_id[linked_id].setdefault("qualifiers", {})
        qualifiers["footnote_text_pending"] = False
        qualifiers["footnote_body_link_status"] = "linked"
        qualifiers["footnote_note_statement_ids"] = sorted(set(qualifiers.get("footnote_note_statement_ids", [])) | set(note_ids))
        refs = qualifiers.setdefault("footnote_refs", [])
        if not any(item.get("footnote_marker") == str(marker) and item.get("footnote_printed_page") == 338 for item in refs):
            refs.append(note_ref)

# The print places note 1 after Goldoni's proposed life-scene frontispiece and
# note 2 after Zatta's stated support for the Jesuits. Remove same-line OCR carryover.
for key, explanation in {
    "false_vignola": "Printed p.338 note 1 follows Goldoni’s frontispiece proposal earlier on the page; it does not annotate the same-source-line Vignola dedication. Confirmed against CHP-13.pdf physical page 7.",
    "false_zatta_publications": "Printed p.338 note 2 follows the statement that Zatta strongly supported the Jesuits; it does not annotate the later, same-source-line claim about proposed polemical publications. Confirmed against CHP-13.pdf physical page 7.",
}.items():
    qualifiers = statement_by_id[body_ids[key]].setdefault("qualifiers", {})
    for field in (
        "footnote_marker", "footnote_printed_page", "footnote_text_pending", "footnote_segment",
        "footnote_body_link_status", "cross_reference_segments", "footnote_note_statement_ids", "footnote_refs",
    ):
        qualifiers.pop(field, None)
    qualifiers["footnote_scope_exclusion"] = explanation

coverage[NOTES]["source_line_ranges"] = "L180-210"
coverage[NOTES]["note"] = (
    "Notes L180-191 (pp.332-334), L192-202 (pp.335-336), and L203-210 (pp.337-338) are migrated. "
    "L211-246 and mirrored caption lines L247-248 remain to process or map; the composite segment remains partial."
)
coverage[BODY]["migration_status"] = "complete"
coverage[BODY]["source_line_ranges"] = "L61-68"
coverage[BODY]["note"] = (
    "Printed p.338 body and visible notes reviewed against CHP-13.pdf physical page 7. "
    "Footnote 1 links Goldoni’s frontispiece proposal to the cited volume II, page 1; footnote 2 links Zatta’s stated Jesuit support to the two cited letters and Haskell’s interpretation. "
    "Same-line OCR carryover markers were removed from the Vignola-dedication and proposed-publication statements. "
    "The Zatta cross-page sentence is closed by p.339 L71."
)

candidate_out = candidates + new_candidates
mention_out = mentions + new_mentions
statement_out = statements + new_statements
print(f"candidate rows: {len(candidates)} -> {len(candidate_out)} (+{len(new_candidates)})")
print(f"mention rows: {len(mentions)} -> {len(mention_out)} (+{len(new_mentions)})")
print(f"statement rows: {len(statements)} -> {len(statement_out)} (+{len(new_statements)})")
print("coverage changes: p.338 body partial -> complete; consolidated notes L180-210, still partial")
print("footnote targets:")
for marker, linked_ids in note_links.items():
    print(f"  {marker}: {', '.join(linked_ids)}")
print("false same-line markers removed: p.338 Vignola-dedication and Zatta-proposed-publications statements")
if not args.apply:
    print("dry-run only; pass --apply to write after reviewing this plan")
    raise SystemExit(0)

for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {backup}")
    shutil.copy2(path, backup)
write_csv(candidate_path, candidate_fields, candidate_out)
write_csv(mention_path, mention_fields, mention_out)
write_jsonl(statement_path, statements + new_statements)
write_csv(coverage_path, coverage_fields, coverage_rows)
print(f"applied; backups use suffix {BACKUP_SUFFIX}")
