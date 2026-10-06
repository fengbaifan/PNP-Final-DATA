"""Controlled S2 migration for printed p.340 footnotes; dry-run by default."""
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
BODY = "chp-13:13_CHP-13_intro:l79-88"
NOTES = "chp-13:13_CHP-13_intro:l179-251"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BACKUP_SUFFIX = ".bak-s2-chp13-p340-notes-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.340 footnote migration")
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
for number, prefix in {
    217: "1 Morelli, V, p. 348.",
    218: "2 Bercngo, 1957, and also Mostra dei Remondini, 1958.",
    219: "3 See the seven letters from Pietro Longhi to Remondini between 1748 and 1752 published by A.",
    220: "4 G. A. Moschini, 1924, p. 132.",
    221: "5 Gallo, 1948, p. 184, and G. A. Moschini, 1924, p. 132.",
    222: "6 Gallo, 1948, pp. 158 and 186.",
}.items():
    if not source_lines[number - 1].startswith(prefix):
        raise SystemExit(f"canonical source changed at L{number}")
if source_lines[87] != "Rava, 1911.":
    raise SystemExit("p.340 note 3 continuation at L88 changed")

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

table_state = (
    len(candidates), max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions), len(statements),
)
if table_state != (10174, 10187, 22001, 9830):
    raise SystemExit(f"unexpected table pre-state: {table_state}")
for segment_id in (BODY, NOTES):
    if segment_id not in coverage:
        raise SystemExit(f"required coverage row missing: {segment_id}")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.340 body is not reviewed/partial")
if (coverage[NOTES]["disposition"], coverage[NOTES]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("consolidated notes segment is not reviewed/partial")
if coverage[NOTES]["source_line_ranges"] != "L180-216":
    raise SystemExit("consolidated notes coverage cursor changed")

candidate_specs = [
    ("cand-10188", "Morelli, volume V, p.348 (title unspecified in p.340 note 1)", "archive",
     "Short-form reference cited after the reported dispersal of Maffeo Pinelli's library and picture collection. Title and edition are not supplied here; the cited page has not been consulted.", 217),
    ("cand-10189", "Mostra dei Remondini (1958)", "archive",
     "Exhibition/catalogue reference cited in p.340 note 2. No curator, publisher, or edition details are supplied in this note.", 218),
    ("cand-10190", "Seven letters from Pietro Longhi to Remondini (1748-1752)", "archive",
     "A group of seven letters named in p.340 note 3. S0 splits the printed note: L219 ends with 'published by A.' and body-segment L88 continues 'Rava, 1911.' The letters themselves have not been consulted.", 219),
    ("cand-10191", "G. A. Moschini, 1924, p.132 (citation locator)", "archive",
     "Short-form citation reused for p.340 notes 4 and 5. The title and cited page have not been independently consulted; other Moschini 1924 locators remain separate pending S3 alignment.", 220),
]
new_candidates = []
for candidate_id, name, kind, detail, line_number in candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if any(row["canonical_name"].casefold() == name.casefold() for row in candidates):
        raise SystemExit(f"candidate name already exists: {name}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": candidate_id,
        "canonical_name": name,
        "suggested_type": kind,
        "status": "open",
        "detail": detail,
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES}#L{line_number}",
    })
    new_candidates.append(row)
all_candidate_ids = set(candidate_by_id) | {row["candidate_id"] for row in new_candidates}
required_existing = ("cand-10136", "cand-10138", "cand-10054", "cand-1429", "cand-1709", "cand-2123", "cand-2773", "cand-2796", "cand-8514", "cand-1092", "cand-1932", "cand-0498", "cand-0463")
for candidate_id in required_existing:
    if candidate_id not in all_candidate_ids:
        raise SystemExit(f"required reused candidate is missing: {candidate_id}")

notes_text = "\n".join(source_lines[178:251])
notes_line_offsets = {}
offset = 0
for line_number in range(179, 252):
    notes_line_offsets[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1
body_text = "\n".join(source_lines[78:88])
body_line_offset = sum(len(line) + 1 for line in source_lines[78:87])

new_mentions = []
existing_mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}


def add_mention(line_number, surface, candidate_id, note="", occurrence=0):
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
    if occurrence >= len(positions):
        raise SystemExit(f"mention text missing at L{line_number}: {surface!r}")
    start = notes_line_offsets[line_number] + positions[occurrence]
    end = start + len(surface)
    if notes_text[start:end] != surface:
        raise SystemExit(f"mention offset mismatch at L{line_number}: {surface!r}")
    key = (NOTES, candidate_id, str(start), str(end))
    if key in existing_mention_keys or any(
        (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"])) == key
        for row in new_mentions
    ):
        raise SystemExit(f"duplicate mention at L{line_number}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch13-p340-notes-{len(new_mentions) + 1:03d}",
        "segment_id": NOTES,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": end,
        "note": note,
    })
    new_mentions.append(row)


add_mention(217, "Morelli, V, p. 348", "cand-10188", "Short-form bibliographic locator; title unresolved.")
add_mention(218, "Bercngo, 1957", "cand-10136", "S0 OCR spelling; print reads Berengo. Reuse the existing short-form citation candidate from p.332 note 4; full bibliography identity remains for S3.")
add_mention(218, "Bercngo", "cand-8291", "S0 OCR spelling for printed Berengo; the scan preserves the bibliographic reading.")
add_mention(218, "Mostra dei Remondini, 1958", "cand-10189", "Exhibition/catalogue citation named in p.340 note 2.")
add_mention(218, "Remondini", "cand-2123", "Named in the exhibition title; reuse the firm candidate used in the p.340 body.")
add_mention(219, "the seven letters from Pietro Longhi to Remondini between 1748 and 1752", "cand-10190",
            "The note continues at p.340 body-segment L88 with the publication citation tail.")
add_mention(219, "Pietro Longhi", "cand-1429", "Letter writer; reuse the p.340 body candidate.")
add_mention(219, "Remondini", "cand-2123", "Letters' recipient, named in the note.")
add_mention(219, "A.", "cand-10054", "Initial at the end of L219; L88 continues the same citation as Rava, 1911.")
add_mention(220, "G. A. Moschini, 1924, p. 132", "cand-10191", "Citation locator for p.340 note 4; the same locator is reused in note 5.")
add_mention(220, "G. A. Moschini", "cand-1709", "Cited author; reuse the existing Moschini person candidate.")
add_mention(221, "Gallo, 1948, p. 184", "cand-10138", "Page 184 falls within the existing Gallo 1948 pages 153-214 citation candidate.")
add_mention(221, "Gallo", "cand-8514", "Cited author; reuse the existing Gallo person candidate.")
add_mention(221, "G. A. Moschini, 1924, p. 132", "cand-10191", "Reuse the p.340 note 4 citation candidate for the same volume/page locator.")
add_mention(221, "G. A. Moschini", "cand-1709", "Cited author; reuse the existing Moschini person candidate.")
add_mention(222, "Gallo, 1948, pp. 158 and 186", "cand-10138", "Both cited pages fall within the existing Gallo 1948 pages 153-214 citation candidate.")
add_mention(222, "Gallo", "cand-8514", "Cited author; second note occurrence.")

note_links = {
    "1": [
        "st-chp13-p340-pinelli-collection-dispersal-distressed-contemporaries",
        "st-chp13-p340-pinelli-library-dispersed-after-death",
        "st-chp13-p340-pinelli-picture-collection-dispersed-after-death",
    ],
    "2": ["st-chp13-p340-remondini-established-at-bassano", "st-chp13-p340-remondini-had-venice-branch"],
    "3": [
        "st-chp13-p340-remondini-popularised-piazzetta",
        "st-chp13-p340-remondini-popularised-amigoni",
        "st-chp13-p340-remondini-popularised-guarana",
        "st-chp13-p340-remondini-popularised-pietro-longhi",
        "st-chp13-p340-printed-note-three-rava-citation-tail",
    ],
    "4": ["st-chp13-p340-wagner-seems-to-have-commissioned-little-original-work"],
    "5": ["st-chp13-p340-viero-printer-opened-shop-1754", "st-chp13-p340-viero-same-limited-original-commissioning-applies"],
    "6": [
        "st-chp13-p340-furnaletto-commissioned-twelve-canaletto-drawings-in-1766",
        "st-chp13-p340-canaletto-drawings-depicted-principal-ducale-ceremonies",
        "st-chp13-p340-canaletto-drawings-intended-for-engraving-by-brustolon",
    ],
}
for marker, body_ids in note_links.items():
    for body_id in body_ids:
        if body_id not in statement_by_id:
            raise SystemExit(f"footnote {marker} target statement missing: {body_id}")

wrong_marker_scope = {
    "st-chp13-p340-wagner-german-and-opened-shop-1742": "Printed note 4 follows Wagner's claim about commissioning little original work; it does not follow his nationality or shop-opening date.",
    "st-chp13-p340-wagner-shop-significant-to-printers": "Printed note 4 follows Wagner's claim about commissioning little original work; the preceding shop-significance clause has no separate marker.",
}
for statement_id in wrong_marker_scope:
    refs = statement_by_id.get(statement_id, {}).get("qualifiers", {}).get("footnote_refs", [])
    if not any(ref.get("footnote_marker") == "4" and ref.get("footnote_printed_page") == 340 for ref in refs):
        raise SystemExit(f"expected same-line footnote 4 carryover missing from {statement_id}")

note_specs = [
    {
        "id": "st-chp13-p340-note1-morelli-pinelli-dispersal",
        "marker": "1", "line_start": 217, "line_end": 217,
        "subject": "cand-1932", "object": "cand-10188",
        "predicate": "footnote_cites_morelli_volume_five_page_348_for_pinelli_collection_dispersal",
        "claim": "Printed p.340 note 1 cites Morelli, volume V, page 348, after the reported dispersal of Pinelli’s library and picture collection.",
        "qualification": "This records Haskell’s citation locator, not an independent claim about what Morelli's cited page states.",
        "quote": source_lines[216],
        "mentioned": ["cand-1932", "cand-10188"],
        "linked": note_links["1"],
        "citations": [{"source_candidate_id": "cand-10188", "volume": "V", "page": "348"}],
    },
    {
        "id": "st-chp13-p340-note2-remondini-sources",
        "marker": "2", "line_start": 218, "line_end": 218,
        "subject": "cand-2123", "object": "cand-10189",
        "predicate": "footnote_cites_berengo_and_remondini_exhibition_catalogue",
        "claim": "Printed p.340 note 2 cites Berengo (1957) and Mostra dei Remondini (1958) after the account of the firm’s Bassano establishment and Venice branch.",
        "qualification": "Both items are recorded as Haskell’s citations; neither source has been independently consulted. S0’s Bercngo OCR is corrected only in this S2 reading.",
        "quote": source_lines[217],
        "mentioned": ["cand-2123", "cand-10136", "cand-10189"],
        "linked": note_links["2"],
        "citations": [
            {"source_candidate_id": "cand-10136", "author_as_printed": "Berengo", "year": "1957"},
            {"source_candidate_id": "cand-10189", "title_as_printed": "Mostra dei Remondini", "year": "1958"},
        ],
        "ocr_corrections": [
            {"source_line": 218, "ocr": "Bercngo", "print": "Berengo", "basis": "CHP-13.pdf physical page 9."},
            {"source_line": 218, "ocr": "1958. \"", "print": "1958.", "basis": "CHP-13.pdf physical page 9; remove trailing OCR quote mark."},
        ],
    },
    {
        "id": "st-chp13-p340-note3-longhi-letters-rava-publication",
        "marker": "3", "line_start": 219, "line_end": 219,
        "subject": "cand-1429", "object": "cand-2123",
        "predicate": "seven_longhi_letters_to_remondini_published_by_rava_1911",
        "claim": "Printed p.340 note 3 identifies seven letters from Pietro Longhi to Remondini, dated between 1748 and 1752, as published by A. Rava in 1911.",
        "qualification": "The note is split in S0: L219 ends with “published by A.” and p.340 body-segment L88 supplies “Rava, 1911.” Keep both page-local anchors; the letters and Rava publication have not been consulted.",
        "quote": source_lines[218],
        "mentioned": ["cand-1429", "cand-2123", "cand-10190", "cand-10054"],
        "linked": note_links["3"],
        "citations": [{"source_candidate_id": "cand-10190", "published_in_candidate_id": "cand-10054", "date_range": "1748-1752", "publisher_as_printed": "A. Rava", "publication_year": "1911"}],
        "speaker": "Haskell, printed footnote with continuation at body L88",
        "layer": "document citation with split source anchor",
        "cross_reference_segments": [NOTES, BODY],
        "citation_tail": {"segment_id": BODY, "source_line_start": 88, "source_line_end": 88, "original_quote": "Rava, 1911."},
        "relation_candidate": True,
    },
    {
        "id": "st-chp13-p340-note4-moschini-wagner-locator",
        "marker": "4", "line_start": 220, "line_end": 220,
        "subject": "cand-2796", "object": "cand-10191",
        "predicate": "footnote_cites_moschini_1924_page_132_for_wagner_commissioning_claim",
        "claim": "Printed p.340 note 4 cites G. A. Moschini (1924), page 132, after Haskell’s statement that Wagner seems to have commissioned little original work.",
        "qualification": "The citation is recorded as printed; the cited page and the work’s title have not been independently consulted.",
        "quote": source_lines[219],
        "mentioned": ["cand-2796", "cand-1709", "cand-10191"],
        "linked": note_links["4"],
        "citations": [{"source_candidate_id": "cand-10191", "author_candidate_id": "cand-1709", "year": "1924", "page": "132"}],
    },
    {
        "id": "st-chp13-p340-note5-gallo-moschini-viero-locators",
        "marker": "5", "line_start": 221, "line_end": 221,
        "subject": "cand-2773", "object": "cand-10138",
        "predicate": "footnote_cites_gallo_and_moschini_for_viero_statement",
        "claim": "Printed p.340 note 5 cites Gallo (1948), page 184, and Moschini (1924), page 132, after the statement about Viero’s shop and the parallel assessment of his original commissions.",
        "qualification": "The p.184 locator reuses the existing Gallo 1948 pp.153-214 candidate; sources have not been independently consulted.",
        "quote": source_lines[220],
        "mentioned": ["cand-2773", "cand-8514", "cand-10138", "cand-1709", "cand-10191"],
        "linked": note_links["5"],
        "citations": [
            {"source_candidate_id": "cand-10138", "author_candidate_id": "cand-8514", "year": "1948", "cited_page": "184"},
            {"source_candidate_id": "cand-10191", "author_candidate_id": "cand-1709", "year": "1924", "page": "132"},
        ],
    },
    {
        "id": "st-chp13-p340-note6-gallo-furnaletto-locators",
        "marker": "6", "line_start": 222, "line_end": 222,
        "subject": "cand-1092", "object": "cand-10138",
        "predicate": "footnote_cites_gallo_pages_158_and_186_for_furnaletto_commission",
        "claim": "Printed p.340 note 6 cites Gallo (1948), pages 158 and 186, after the account of Furnaletto’s Canaletto drawing commission and intended engravings by Brustolon.",
        "qualification": "Both locators fall within the existing Gallo 1948 pp.153-214 citation candidate; the cited pages have not been independently consulted.",
        "quote": source_lines[221],
        "mentioned": ["cand-1092", "cand-0498", "cand-0463", "cand-10138", "cand-8514"],
        "linked": note_links["6"],
        "citations": [{"source_candidate_id": "cand-10138", "author_candidate_id": "cand-8514", "year": "1948", "pages": ["158", "186"]}],
    },
]

new_statements = []
note_statement_ids_by_marker = {}
for spec in note_specs:
    if spec["id"] in statement_by_id:
        raise SystemExit(f"note statement already exists: {spec['id']}")
    missing = [candidate_id for candidate_id in spec["mentioned"] if candidate_id not in all_candidate_ids]
    if missing:
        raise SystemExit(f"missing candidate FK in {spec['id']}: {missing}")
    if spec["quote"] not in notes_text:
        raise SystemExit(f"note quote is not anchored in S0: {spec['id']}")
    qualifiers = {
        "source_line_start": spec["line_start"],
        "source_line_end": spec["line_end"],
        "printed_page": 340,
        "pdf_physical_page": 9,
        "claim": spec["claim"],
        "speaker": spec.get("speaker", "Haskell, printed footnote"),
        "text_layer": spec.get("layer", "bibliographic citation"),
        "qualification": spec["qualification"],
        "mentioned_candidate_ids": spec["mentioned"],
        "footnote_number": spec["marker"],
        "linked_body_statement_ids": spec["linked"],
        "citations": spec["citations"],
    }
    for optional in ("ocr_corrections", "cross_reference_segments", "citation_tail"):
        if spec.get(optional):
            qualifiers[optional] = spec[optional]
    if spec.get("relation_candidate"):
        qualifiers["relation_candidate"] = True
    new_statements.append({
        "statement_id": spec["id"],
        "segment_id": NOTES,
        "subject_candidate_id": spec["subject"],
        "object_candidate_id": spec["object"],
        "predicate": spec["predicate"],
        "qualifiers": qualifiers,
        "original_quote": spec["quote"],
        "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
    })
    note_statement_ids_by_marker.setdefault(spec["marker"], []).append(spec["id"])


def link_body_statement(statement_id, marker, note_ids):
    qualifiers = statement_by_id[statement_id].setdefault("qualifiers", {})
    refs = qualifiers.get("footnote_refs", [])
    matching = [ref for ref in refs if ref.get("footnote_marker") == marker and ref.get("footnote_printed_page") == 340]
    if not matching:
        raise SystemExit(f"pending p.340 note {marker} missing from {statement_id}")
    for ref in matching:
        ref["footnote_text_pending"] = False
        ref["footnote_body_link_status"] = "linked"
        ref["footnote_note_statement_ids"] = note_ids
    qualifiers["footnote_note_statement_ids"] = sorted(set(qualifiers.get("footnote_note_statement_ids", [])) | set(note_ids))
    qualifiers["footnote_text_pending"] = False
    qualifiers["footnote_body_link_status"] = "linked"


for marker, body_ids in note_links.items():
    for body_id in body_ids:
        link_body_statement(body_id, marker, note_statement_ids_by_marker[marker])

# Remove note 4 from two earlier clauses: the printed marker follows only the
# clause about Wagner's limited original commissions.
for statement_id, explanation in wrong_marker_scope.items():
    qualifiers = statement_by_id[statement_id]["qualifiers"]
    qualifiers["footnote_refs"] = [
        ref for ref in qualifiers.get("footnote_refs", [])
        if not (ref.get("footnote_marker") == "4" and ref.get("footnote_printed_page") == 340)
    ]
    if not qualifiers["footnote_refs"]:
        qualifiers.pop("footnote_refs", None)
        for field in (
            "footnote_marker", "footnote_printed_page", "footnote_text_pending", "footnote_segment",
            "footnote_body_link_status", "footnote_note_statement_ids",
        ):
            qualifiers.pop(field, None)
        if qualifiers.get("cross_reference_segments") == [NOTES]:
            qualifiers.pop("cross_reference_segments", None)
    qualifiers["footnote_scope_exclusion"] = explanation + " Confirmed against CHP-13.pdf physical page 9."

# Complete the split source citation for A. Rava and preserve its second anchor.
rava_candidate = candidate_by_id["cand-10054"]
rava_candidate["detail"] = (
    "Printed p.340 note 3 is split in S0: notes-segment L219 ends with 'published by A.' and p.340 body-segment L88 continues 'Rava, 1911.' "
    "Together these identify the cited publication as A. Rava, 1911; the title and work remain unverified."
)
rava_tail = statement_by_id["st-chp13-p340-printed-note-three-rava-citation-tail"]
rava_tail["qualifiers"]["claim"] = "This body segment carries the terminal citation fragment “Rava, 1911.” from printed p.340 note 3, whose first fragment is in the consolidated notes segment L219."
rava_tail["qualifiers"]["qualification"] = "Keep the citation's L219 and L88 anchors separate; the note is linked as one citation without moving text across source segments."
rava_tail["qualifiers"]["cross_reference_segments"] = [NOTES, BODY]

coverage[NOTES]["source_line_ranges"] = "L180-222"
coverage[NOTES]["note"] = (
    "Notes L180-216 (pp.332-339) and p.340 notes 1-6 at L217-222 are migrated. "
    "L223-246 and mirrored caption lines L247-248 remain to process or map; the composite segment remains partial."
)
coverage[BODY]["migration_status"] = "complete"
coverage[BODY]["source_line_ranges"] = "L79-88"
coverage[BODY]["note"] = (
    "Printed p.340 body and notes 1-6 were checked against CHP-13.pdf physical page 9. "
    "The split citation in note 3 is linked across notes-segment L219 and body-segment L88 without combining their source-local anchors. "
    "Note 4 is linked only to Wagner's limited-commission claim; all six note markers now have statement links. OCR corrections are recorded in S2 only."
)

candidate_out = candidates + new_candidates
mention_out = mentions + new_mentions
statement_out = statements + new_statements
if len({row["candidate_id"] for row in candidate_out}) != len(candidate_out):
    raise SystemExit("candidate IDs are not unique after migration")
if len({row["mention_id"] for row in mention_out}) != len(mention_out):
    raise SystemExit("mention IDs are not unique after migration")
if len({row["statement_id"] for row in statement_out}) != len(statement_out):
    raise SystemExit("statement IDs are not unique after migration")
for row in new_mentions:
    if notes_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
        raise SystemExit(f"final mention span failed: {row['mention_id']}")
for statement in new_statements:
    if statement["original_quote"] not in notes_text:
        raise SystemExit(f"final statement quote failed: {statement['statement_id']}")

print(f"candidate rows: {len(candidates)} -> {len(candidate_out)} (+{len(new_candidates)})")
print(f"mention rows: {len(mentions)} -> {len(mention_out)} (+{len(new_mentions)})")
print(f"statement rows: {len(statements)} -> {len(statement_out)} (+{len(new_statements)})")
print("coverage: p.340 body partial -> complete; consolidated notes range L180-216 -> L180-222, still partial")
print("footnote links: 1-6 linked to the exact p.340 claims; note 3 keeps L219/L88 as separate anchors")
print("scope correction: note 4 removed from Wagner nationality/shop-date and shop-significance clauses")

if not args.apply:
    print("dry-run only; rerun with --apply after reviewing this delta")
    raise SystemExit(0)

targets = [candidate_path, mention_path, statement_path, coverage_path]
backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in targets]
if any(path.exists() for path in backups):
    raise SystemExit("one or more migration backup paths already exist")
for original, backup in zip(targets, backups):
    shutil.copy2(original, backup)

write_csv(candidate_path, candidate_fields, candidate_out)
write_csv(mention_path, mention_fields, mention_out)
write_jsonl(statement_path, statement_out)
write_csv(coverage_path, coverage_fields, coverage_rows)
print("applied with four table backups:")
for path in backups:
    print(f"  {path.relative_to(ROOT)}")
