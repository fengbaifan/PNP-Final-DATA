"""Controlled S2 migration for Appendix I, printed p.389 and p.388 closure."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "19_CHP-19Appendix.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-19Appendix.pdf"
EXPECTED_HASHES = {
    SOURCE: "725dc16a2983bec379ce2a8b608542ab3defe348d2b2f2a336632ac4905388f1",
    PDF: "2a1c29e6c2864527482d231a85c4252e55524b436ae4dff5b0d55d9d5a67a9eb",
}
P388 = "chp-19:19_CHP-19Appendix:l43-63"
P389 = "chp-19:19_CHP-19Appendix:l65-84"
BACKUP_SUFFIX = ".bak-s2-chp19-p389-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed S2 migration")
args = parser.parse_args()


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


for path, expected in EXPECTED_HASHES.items():
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit(f"registered input changed: {path.relative_to(ROOT)}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
coverage_fields, coverage = read_csv(coverage_path)
segments = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segment_by_id = {row["segment_id"]: row for row in segments}
candidate_by_id = {row["candidate_id"]: row for row in candidates}
coverage_by_id = {row["segment_id"]: row for row in coverage}

for sid in (P388, P389):
    if sid not in segment_by_id or sid not in coverage_by_id:
        raise SystemExit(f"missing S0 or S2 row: {sid}")
if (coverage_by_id[P388]["disposition"], coverage_by_id[P388]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit(f"p.388 must be reviewed/partial before its continuation is read: {coverage_by_id[P388]}")
if (coverage_by_id[P389]["disposition"], coverage_by_id[P389]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"p.389 must be queued/pending before migration: {coverage_by_id[P389]}")


def read_segment(sid: str):
    row = segment_by_id[sid]
    lines = (ROOT / row["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(lines[row["line_start"] - 1:row["line_end"]])
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != row["sha256"]:
        raise SystemExit(f"segment hash mismatch: {sid}")
    return text, lines


texts = {sid: read_segment(sid)[0] for sid in (P388, P389)}
source_lines = read_segment(P389)[1]


def quote(first_line: int, last_line: int) -> str:
    return "\n".join(source_lines[first_line - 1:last_line])


new_candidate_specs = [
    ("cand-10792", "Tona [sic] (probable Latona in Franceschini's proposed subject)", "person", 81,
     "The printed p.389 quote explicitly reads ‘Tona [sic]’. The surrounding birth of Febo and Diana and threat from Giunone suggest Latona, but the printed form is preserved and no external identity is asserted."),
    ("cand-10793", "Cain (biblical figure in Franceschini's proposed subject)", "person", 81,
     "Named in the p.389 letter as one of Eve's children in a proposed subject; source-local figure candidate, not an external identity alignment."),
    ("cand-10794", "Abel (biblical figure in Franceschini's proposed subject)", "person", 81,
     "Named in the p.389 letter as one of Eve's children in a proposed subject; source-local figure candidate, not an external identity alignment."),
    ("cand-10795", "Priam (king of Troy named in the Torelli letter)", "person", 84,
     "Named in the p.389 letter as Polyxena's father and king of Troy; no external identity alignment is made at S2."),
    ("cand-10796", "Federighi (person entrusted with handling the horse model)", "person", 72,
     "Tacca says he gave this person instructions for carefully unpacking and repacking the model. Only a surname is supplied; identity remains unresolved."),
    ("cand-10797", "Letter from Giuseppe Torelli to Alessandro Marchesini (24 February 1705; MS 3299)", "archive", 82,
     "Haskell's Appendix 3 caption identifies the date, writer, recipient and manuscript reference. The archival manuscript itself was not independently consulted."),
]
existing_keys = {
    ((row.get("canonical_name") or "").strip().casefold(), (row.get("suggested_type") or "").strip().casefold())
    for row in candidates
}
for cid, name, kind, line, detail in new_candidate_specs:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    key = (name.strip().casefold(), kind.casefold())
    if key in existing_keys:
        raise SystemExit(f"candidate natural key already exists: {name} / {kind}")
    row = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{P389}#L{line}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row
    existing_keys.add(key)

# Type the index-seeded candidates whose source roles are explicit on p.389.
for cid, kind in {
    "cand-0319": "person", "cand-0434": "person", "cand-0834": "person",
    "cand-1014": "person", "cand-1070": "person", "cand-1540": "person",
    "cand-2538": "person", "cand-2646": "person", "cand-2648": "person",
    "cand-4667": "person", "cand-4321": "person", "cand-4171": "person",
    "cand-3432": "person", "cand-3397": "place",
}.items():
    row = candidate_by_id.get(cid)
    if not row:
        raise SystemExit(f"expected candidate missing: {cid}")
    if row.get("suggested_type") and row["suggested_type"] != kind:
        raise SystemExit(f"candidate type conflict for {cid}: {row['suggested_type']} != {kind}")
    row["suggested_type"] = kind

# The p.389 signature closes c.463 and identifies the same local correspondent
# already read as Fedini on p.388. Keep the index candidate separate for S3.
fedini = candidate_by_id.get("cand-10766")
anonymous = candidate_by_id.get("cand-10791")
if not fedini or not anonymous:
    raise SystemExit("expected local Fedini and c.463 writer candidates")
fedini["detail"] = (
    "The p.388 and p.389 printed signatures both read Domenico/Dom.o Fedini. "
    "Canonical OCR line 48 on p.388 and line 68 on p.389 reads Pedini and merges/misreads the name. "
    "Keep this local reading distinct from indexed cand-1014 (Fedini, Domenico) until S3 alignment."
)
fedini["suggested_type"] = "person"
anonymous["status"] = "excluded"
anonymous["exclude_reason"] = (
    "The c.463 letter's printed p.389 signature reads Dom.o Fedini, matching the local person candidate "
    "cand-10766 from p.388. This was not a second person; the request statement now points to cand-10766. "
    "Alignment with indexed cand-1014 remains for S3."
)
anonymous["detail"] = "Retired after p.389 signature inspection; retained as a traceable migration record, not a separate person."

letter_463 = next((row for row in statements if row.get("statement_id") == "st-chp19-p388-c463-baldi-recommendation"), None)
if not letter_463:
    raise SystemExit("expected p.388 c.463 statement missing")
q = letter_463["qualifiers"]
if q.get("speaker") != "Unidentified writer of Fondo Orsini 175, c.463":
    raise SystemExit("p.388 c.463 attribution changed before p.389 signature repair")
q["speaker"] = "Domenico Fedini (printed p.389 signature: Dom.o Fedini; p.388 signature also reads Fedini)"
q["qualification"] = (
    "The printed p.389 signature reads Dom.o Fedini and matches the p.388 Fedini signature; "
    "the canonical OCR reads Pedini. The request to accompany Baldi is not recorded as completed."
)
q.pop("migration_qualification", None)
q["continuation_status"] = "closed"
q["continuation_closed_by_statement_id"] = "st-chp19-p389-c463-fedini-signature"
q["cross_reference_segments"] = [P389]
q["mentioned_candidate_ids"] = [
    "cand-0295", "cand-10777", "cand-10788", "cand-10789", "cand-10766"
]

archive_463 = candidate_by_id.get("cand-10788")
if archive_463:
    archive_463["detail"] = (
        "Fondo Orsini 175, c.463: p.388 records Bernini's request concerning Gioì Paolo Baldi; "
        "p.389 closes the letter with a signature read as Dom.o Fedini. The OCR reads Pedini; "
        "the indexed Fedini candidate remains for S3 alignment."
    )

for cid in ("cand-10791",):
    if cid in letter_463["qualifiers"]["mentioned_candidate_ids"]:
        raise SystemExit("duplicate writer endpoint remains after attribution update")

# Reuse the exact p.227 candidates for the same two letters explicitly cited
# by Appendix 3; do not mint duplicate paintings or mythological figures.
candidate_updates = {
    "cand-7801": "The 17 February 1705 letter from Marcantonio Franceschini to Alessandro Marchesini, cited in Chapter 8 p.227 note 1 and reproduced in Appendix 3 p.389, MS 3299. The manuscript was not independently consulted.",
    "cand-7798": "The Trojan-history painting proposed by Felice Torelli. The p.389 letter of 24 February 1705 specifies Pyrrhus killing Polyxena and related figures; Haskell's p.227 account says a picture later arrived but leaves its exact identity uncertain.",
    "cand-5616": "The Pietro Tacca letter cited in Chapter 4 note 6 is the Appendix 2 item 172, c.306 reproduced on p.389 and dated Florence, 30 December 1624. It discusses a horse model and conditional bronze fittings; the manuscript was not independently consulted.",
}
for cid, detail in candidate_updates.items():
    if cid not in candidate_by_id:
        raise SystemExit(f"expected reusable candidate missing: {cid}")
    candidate_by_id[cid]["detail"] = detail

new_mentions = []
mention_ids = {row["mention_id"] for row in mentions}


def add_mention(mid, cid, surface, note="", occurrence=0):
    if mid in mention_ids:
        raise SystemExit(f"mention ID already exists: {mid}")
    if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
        raise SystemExit(f"mention targets missing or excluded candidate: {cid}")
    text = texts[P389]
    start = -1
    cursor = 0
    for _ in range(occurrence + 1):
        start = text.find(surface, cursor)
        if start < 0:
            raise SystemExit(f"surface not found in p.389 segment: {surface!r}")
        cursor = start + 1
    end = start + len(surface)
    if text[start:end] != surface:
        raise SystemExit(f"span mismatch for {mid}")
    new_mentions.append({
        "mention_id": mid, "segment_id": P389, "candidate_id": cid,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    mention_ids.add(mid)


mention_specs = [
    ("001", "cand-10766", "Dom.o Pedini", "Canonical OCR form at the p.389 closing; the printed signature reads Dom.o Fedini, matching p.388."),
    ("002", "cand-4490", "Roma", "City in the c.463 dateline; the writer says Rome, 12 July 1626."),
    ("003", "cand-5616", "172, c. 306", "Appendix 2 archival locator for the Pietro Tacca letter; the item is identified as Paolo Giordano II's letter in Chapter 4 note 6."),
    ("004", "cand-2538", "Pietro Tacca", "Writer named in the Appendix 2 letter heading and signature."),
    ("005", "cand-5555", "modello del Cavallo", "The horse model sent in the letter; reuse the existing source-specific model candidate from Chapter 4."),
    ("006", "cand-10796", "sig.r Federighi", "Only the surname is supplied; Tacca says he gave him unpacking/repacking instructions."),
    ("007", "cand-0434", "Ill.mo et Ecc.mo mio sig.re et Pron Col.mo", "Honorific salutation in the Tacca letter; the Chapter 4 note identifies this published letter as addressed to Paolo Giordano II."),
    ("008", "cand-3397", "firenze", "Place in the 30 December 1624 dateline; use the existing Florence place candidate."),
    ("009", "cand-0834", "Stefano Conti", "Commissioner named in the Appendix 3 heading; use the page-389 index candidate."),
    ("010", "cand-7803", "Biblioteca Governativa", "Repository named in the Appendix 3 heading for MS 3299."),
    ("011", "cand-1454", "Lucca", "City in the repository name and Appendix 3 heading."),
    ("012", "cand-1070", "Marcantonio Franceschini", "Artist named as a recipient of Conti's commission in Appendix 3 and as the writer of the 17 February letter."),
    ("013", "cand-2646", "Felice Torelli", "Artist named in the Appendix 3 heading as a recipient of Conti's commission."),
    ("014", "cand-7801", "Letter from Marcantonio Franceschini to Alessandro Marchesini of 17 February 1705", "The Appendix 3 heading identifies the same letter cited at Chapter 8 p.227 note 1."),
    ("015", "cand-1540", "Alessandro Marchesini", "Named recipient of the 17 February letter; reused from the Chapter 8 p.227 context."),
    ("016", "cand-1540", "cotesto Cav.re", "Franceschini's reference to his addressee as the gentleman/knight; the letter heading names Marchesini."),
    ("017", "cand-7815", "Arianna", "Italian source form for the proposed Ariadne subject; reuse the p.227 Ariadne candidate."),
    ("018", "cand-7814", "Bacco", "Italian source form for Bacchus, a possible subject."),
    ("019", "cand-4321", "Amore", "Cupid named as a figure that could be introduced into the possible subject."),
    ("020", "cand-4171", "Venere", "Venus named as a figure that could be introduced into the possible subject."),
    ("021", "cand-10792", "Tona [sic]", "Printed form preserved; probable Latona is an inference from the birth of Febo/Diana and Juno's threat."),
    ("022", "cand-4667", "Febo", "Source form for Phoebus/Apollo; kept as a local mention pending global alignment."),
    ("023", "cand-4136", "Diana", "Named alongside Febo as a child of Tona [sic]."),
    ("024", "cand-3432", "Giunone", "Juno is described as threatening Tona [sic]."),
    ("025", "cand-7813", "Eva", "Eve named in another proposed subject."),
    ("026", "cand-10793", "Caino", "Cain named as Eve's child in the proposed subject."),
    ("027", "cand-10794", "Abele", "Abel named as Eve's child in the proposed subject."),
    ("028", "cand-7812", "Adamo", "Adam named as working the earth in the proposed subject."),
    ("029", "cand-2648", "Giuseppe Torelli", "Writer named in the 24 February 1705 letter heading."),
    ("030", "cand-10797", "Letter from Giuseppe Torelli to Alessandro .Marchesini of 24 February 1705", "The OCR heading inserts a period before Marchesini; the page image reads Alessandro Marchesini."),
    ("031", "cand-1540", ".Marchesini", "Recipient named in the 24 February letter heading; OCR inserts a period before the name, absent in print."),
    ("032", "cand-2646", "Felice", "Giuseppe's brother, said to have found the subject for the known painting."),
    ("033", "cand-7798", "Istoria di Troja", "Trojan-history subject of the proposed Conti commission; reuse the p.227 painting candidate."),
    ("034", "cand-7816", "Pirro", "Pyrrhus, the killer of Polyxena in the proposed scene."),
    ("035", "cand-7817", "Polissena", "Polyxena, the figure killed in the proposed scene."),
    ("036", "cand-7818", "Calcante Mago", "Italian form/epithet for the soothsayer rendered Chalchas in the p.227 account; preserve the letter's form."),
    ("037", "cand-4164", "Enea", "Aeneas named among the heads/figures in the proposed scene."),
    ("038", "cand-7820", "Antinoro", "Printed Italian name in the p.389 letter; p.227 paraphrase uses Antinorus. Do not normalize externally at S2."),
    ("039", "cand-7821", "Achile", "Achilles named as Pyrrhus's father and the tomb's referent; preserve the Italian spelling in the letter."),
    ("040", "cand-10795", "Priamo", "Priam named as Polyxena's father and king of Troy."),
]
for spec in mention_specs:
    ordinal, cid, surface, note, *rest = spec
    occurrence = rest[0] if rest else 0
    add_mention(f"m-chp19-p389-{ordinal}", cid, surface, note, occurrence)

new_statements = [
    {
        "statement_id": "st-chp19-p389-c463-fedini-signature", "segment_id": P389,
        "subject_candidate_id": "cand-10766", "object_candidate_id": "cand-10788",
        "predicate": "fondo_orsini_c463_letter_signed_and_dated_by_domenico_fedini",
        "qualifiers": {
            "source_line_start": 66, "source_line_end": 68, "printed_page": 389,
            "pdf_physical_page": 4,
            "claim": "The c.463 letter closes in Rome on 12 July 1626 and its printed signature reads Dom.o Fedini.",
            "speaker": "Printed letter signature/dateline",
            "text_layer": "quoted archival letter and signature",
            "qualification": "The canonical OCR reads Pedini; the print reads Fedini, consistent with the previous p.388 signature. Alignment with indexed cand-1014 is deferred to S3.",
            "date": "1626-07-12", "mentioned_candidate_ids": ["cand-10766", "cand-10788", "cand-4490"],
            "relation_candidate": False, "cited_material_not_independently_consulted": True,
            "cross_reference_segments": [P388],
        },
        "original_quote": quote(66, 68), "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md", "origin": "book",
    },
    {
        "statement_id": "st-chp19-p389-tacca-model-shipping", "segment_id": P389,
        "subject_candidate_id": "cand-2538", "object_candidate_id": "cand-5555",
        "predicate": "tacca_sent_the_horse_model_in_a_crate_and_requested_careful_repacking",
        "qualifiers": {
            "source_line_start": 71, "source_line_end": 75, "printed_page": 389,
            "pdf_physical_page": 4,
            "claim": "Tacca says he has packed and sent the horse model in a crate and asks that it be unpacked carefully and repacked according to Federighi's instructions so it can return safely.",
            "speaker": "Pietro Tacca", "text_layer": "quoted archival letter, Fondo Orsini 172 c.306",
            "qualification": "The Duke's salutation and Chapter 4 note 6 identify the letter as addressed to Paolo Giordano II. The manuscript was not independently consulted.",
            "date": "1624-12-30", "raw_date": "di Firenze li 30 di Xbre 1624",
            "mentioned_candidate_ids": ["cand-2538", "cand-5555", "cand-10796", "cand-0434", "cand-5616", "cand-4490"],
            "relation_candidate": True, "cited_material_not_independently_consulted": True,
        },
        "original_quote": quote(71, 75), "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md", "origin": "book",
    },
    {
        "statement_id": "st-chp19-p389-tacca-conditional-bronze-fittings", "segment_id": P389,
        "subject_candidate_id": "cand-2538", "object_candidate_id": "cand-5555",
        "predicate": "tacca_described_fittings_conditional_on_bronze_execution",
        "qualifiers": {
            "source_line_start": 72, "source_line_end": 73, "printed_page": 389,
            "pdf_physical_page": 4,
            "claim": "If the Duke decides to have the horse model made in bronze, Tacca says additional adornments not shown in the model would be made, naming the testiera, pettorale, groppiera and statua, and mentioning further Spanish-style fittings.",
            "speaker": "Pietro Tacca", "text_layer": "quoted archival letter, Fondo Orsini 172 c.306",
            "qualification": "This is conditional planning, not a report that the bronze monument or fittings were executed. The OCR phrase around the optional Spanish-style fittings remains uncertain; the source terms are preserved.",
            "date": "1624-12-30", "mentioned_candidate_ids": ["cand-2538", "cand-5555", "cand-0434", "cand-5616"],
            "relation_candidate": True, "cited_material_not_independently_consulted": True,
        },
        "original_quote": quote(72, 73), "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md", "origin": "book",
    },
    {
        "statement_id": "st-chp19-p389-appendix3-conti-franceschini", "segment_id": P389,
        "subject_candidate_id": "cand-0834", "object_candidate_id": "cand-1070",
        "predicate": "appendix_documents_described_as_relating_to_conti_commissions_to_franceschini",
        "qualifiers": {
            "source_line_start": 76, "source_line_end": 77, "printed_page": 389,
            "pdf_physical_page": 4,
            "claim": "The Appendix 3 heading names Marcantonio Franceschini as one of the painters whose commission documents are presented for Stefano Conti at Biblioteca Governativa, Lucca, MS 3299.",
            "speaker": "Haskell's appendix heading", "text_layer": "editorial document caption",
            "qualification": "The caption describes the documents as relating to commissions; it does not establish completion of every commission.",
            "mentioned_candidate_ids": ["cand-0834", "cand-1070", "cand-2646", "cand-7803", "cand-1454"],
            "relation_candidate": True, "cited_material_not_independently_consulted": True,
            "cross_reference_chapter": "Chapter 8, p.227, notes 1 and 2",
        },
        "original_quote": quote(76, 77), "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md", "origin": "book",
    },
    {
        "statement_id": "st-chp19-p389-appendix3-conti-felice-torelli", "segment_id": P389,
        "subject_candidate_id": "cand-0834", "object_candidate_id": "cand-2646",
        "predicate": "appendix_documents_described_as_relating_to_conti_commissions_to_felice_torelli",
        "qualifiers": {
            "source_line_start": 76, "source_line_end": 77, "printed_page": 389,
            "pdf_physical_page": 4,
            "claim": "The Appendix 3 heading names Felice Torelli as one of the painters whose commission documents are presented for Stefano Conti at Biblioteca Governativa, Lucca, MS 3299.",
            "speaker": "Haskell's appendix heading", "text_layer": "editorial document caption",
            "qualification": "The caption describes the documents as relating to commissions; it does not establish completion of every commission.",
            "mentioned_candidate_ids": ["cand-0834", "cand-1070", "cand-2646", "cand-7803", "cand-1454"],
            "relation_candidate": True, "cited_material_not_independently_consulted": True,
            "cross_reference_chapter": "Chapter 8, p.227, notes 1 and 2",
        },
        "original_quote": quote(76, 77), "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md", "origin": "book",
    },
    {
        "statement_id": "st-chp19-p389-franceschini-subject-options", "segment_id": P389,
        "subject_candidate_id": "cand-1070", "object_candidate_id": "cand-7801",
        "predicate": "franceschini_reported_difficulty_and_proposed_alternative_subjects_in_letter",
        "qualifiers": {
            "source_line_start": 78, "source_line_end": 81, "printed_page": 389,
            "pdf_physical_page": 4,
            "claim": "Franceschini says finding a history or fable for two figures and putti is difficult, prefers the recipient to choose, and offers several alternatives: Arianna and Bacco with Amore and possibly Venere; Tona [sic] giving birth under a tree to Febo and Diana while Giunone threatens her; or Eva with Caino and Abele while Adamo works the earth.",
            "speaker": "Marcantonio Franceschini", "text_layer": "quoted archival letter, MS 3299",
            "qualification": "These are alternative subject proposals in an excerpt; the letter does not state here that any of these listed subjects was selected or completed. ‘Tona [sic]’ is retained, with Latona only a contextual possibility.",
            "date": "1705-02-17", "reported_addressee": "Alessandro Marchesini",
            "mentioned_candidate_ids": ["cand-1070", "cand-1540", "cand-7801", "cand-7815", "cand-7814", "cand-4321", "cand-4171", "cand-10792", "cand-4667", "cand-4136", "cand-3432", "cand-7813", "cand-10793", "cand-10794", "cand-7812"],
            "relation_candidate": True, "cited_material_not_independently_consulted": True,
        },
        "original_quote": quote(78, 81), "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md", "origin": "book",
    },
    {
        "statement_id": "st-chp19-p389-giuseppe-reports-felice-trojan-subject", "segment_id": P389,
        "subject_candidate_id": "cand-2648", "object_candidate_id": "cand-7798",
        "predicate": "giuseppe_torelli_reported_felice_selected_trojan_history_subject_for_conti_commission",
        "qualifiers": {
            "source_line_start": 82, "source_line_end": 84, "printed_page": 389,
            "pdf_physical_page": 4,
            "claim": "Giuseppe Torelli reports to Alessandro Marchesini that his brother Felice has found a subject for the known painting: Pyrrhus killing Polyxena in a temple, with Calchas, other half-length figures or heads representing Aeneas and Antenor, and Achilles's tomb; he says the expressions, ideas and drapery will make the picture demanding because Polyxena is Priam's daughter and Pyrrhus Achilles's son.",
            "speaker": "Giuseppe Torelli", "reported_speaker": "Felice Torelli",
            "text_layer": "quoted archival letter, MS 3299",
            "qualification": "The letter reports subject selection and anticipated difficulty, not completion. The page image reads Felice where the OCR has ‘Febee’; the diagram-like marks after all’in sù are retained as non-text and not interpreted.",
            "date": "1705-02-24", "reported_addressee": "Alessandro Marchesini",
            "mentioned_candidate_ids": ["cand-2648", "cand-1540", "cand-2646", "cand-10797", "cand-7798", "cand-7816", "cand-7817", "cand-7818", "cand-4164", "cand-7820", "cand-7821", "cand-10795"],
            "relation_candidate": True, "cited_material_not_independently_consulted": True,
            "cross_reference_segments": ["chp-8:08_CHP-8_sec_ii:l190-204"],
        },
        "original_quote": quote(82, 84), "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md", "origin": "book",
    },
]

existing_statement_ids = {row["statement_id"] for row in statements}
for row in new_statements:
    if row["statement_id"] in existing_statement_ids:
        raise SystemExit(f"statement ID already exists: {row['statement_id']}")
    existing_statement_ids.add(row["statement_id"])
    for cid in row["qualifiers"].get("mentioned_candidate_ids", []):
        if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
            raise SystemExit(f"statement {row['statement_id']} references unavailable candidate {cid}")
    start = row["qualifiers"]["source_line_start"]
    end = row["qualifiers"]["source_line_end"]
    seg_text = texts[P389]
    if row["original_quote"] not in seg_text:
        raise SystemExit(f"statement quote not contained in p.389 segment: {row['statement_id']}")
    if start < 65 or end > 84:
        raise SystemExit(f"statement range outside p.389: {row['statement_id']}")

mentions.extend(new_mentions)
statements.extend(new_statements)
coverage_by_id[P388]["migration_status"] = "complete"
coverage_by_id[P388]["note"] = (
    "Printed p.388 (PDF physical page 3) read against CHP-19Appendix.pdf. Closes Fondo Orsini 171 c.I letter; "
    "processes c.140 and 173 c.2 letters signed Domenico Pedini; begins c.463 letter concerning Gioì Paolo Baldi. "
    "The c.463 request closes on p.389 and its printed signature reads Dom.o Fedini; the OCR reads Pedini. "
    "Use local candidate cand-10766, distinct from indexed cand-1014 pending S3."
)
coverage_by_id[P389]["disposition"] = "reviewed"
coverage_by_id[P389]["migration_status"] = "complete"
coverage_by_id[P389]["source_line_ranges"] = "L66-84"
coverage_by_id[P389]["note"] = (
    "Printed p.389 (PDF physical page 4) read against CHP-19Appendix.pdf. Closes the p.388 c.463 letter with a "
    "signature read as Dom.o Fedini; records the c.306 Pietro Tacca horse-model letter; reads the Appendix 3 heading "
    "and two 1705 letters. The image confirms ‘Felice’ where OCR reads ‘Febee’, preserves printed ‘Tona [sic]’, and "
    "shows diagram-like marks after all’in sù; no OCR/PDF source asset was changed. Both Appendix 3 letters are linked "
    "to the matching p.227 account; manuscript citations were not independently consulted."
)

files_to_backup = [candidate_path, mention_path, statement_path, coverage_path]
if args.apply:
    for path in files_to_backup:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing overwrite: {backup.name}")
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
    print("applied p.389 S2 migration; backups:")
    for path in files_to_backup:
        print(f"  {path.name}{BACKUP_SUFFIX}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates: {len(new_candidate_specs)}; mentions: {len(new_mentions)}; statements: {len(new_statements)}")
    print("p.388: reviewed/partial -> reviewed/complete; p.389: queued/pending -> reviewed/complete")
    print("candidate cand-10791: duplicate unnamed c.463 writer -> excluded with signature evidence")
