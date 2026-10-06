"""Controlled S2 migration for Appendix I, printed pp.386-387 receipt and p.387 contents."""
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
CANONICAL = ROOT / "02-sources" / "02-Markdown" / "19_CHP-19Appendix.md"
VISUAL = ROOT / "02-sources" / "02-Markdown" / "19_CHP-19Appendix_p386_receipt_visual-transcription.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-19Appendix.pdf"
EXPECTED_HASHES = {
    CANONICAL: "725dc16a2983bec379ce2a8b608542ab3defe348d2b2f2a336632ac4905388f1",
    VISUAL: "4fa4f3d98471fbdaff06490217fee4a416e71ee8b1df9385c5b279846c3be550",
    PDF: "2a1c29e6c2864527482d231a85c4252e55524b436ae4dff5b0d55d9d5a67a9eb",
}
P386_RECEIPT = "chp-19:19_CHP-19Appendix_p386_receipt_visual-transcription:l4-4"
P387 = "chp-19:19_CHP-19Appendix:l22-41"
P388 = "chp-19:19_CHP-19Appendix:l43-63"
BACKUP_SUFFIX = ".bak-s2-chp19-p387-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
parser.add_argument("--repair-model-reference", action="store_true")
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

if args.repair_model_reference:
    if coverage_by_id.get(P387, {}).get("disposition") != "reviewed" or coverage_by_id[P387].get("migration_status") != "partial":
        raise SystemExit("model-reference repair requires the reviewed/partial p.387 segment")
    candidate_id = "cand-10780"
    mention_id = "m-chp19-p387-043"
    statement_id = "st-chp19-p387-orsini-letter-model-handle"
    if candidate_id in candidate_by_id or any(row.get("mention_id") == mention_id for row in mentions):
        raise SystemExit("model-reference repair IDs already exist")
    p387_row = segment_by_id[P387]
    p387_source_lines = (ROOT / p387_row["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    model_text = "\n".join(p387_source_lines[p387_row["line_start"] - 1:p387_row["line_end"]])
    if hashlib.sha256(model_text.encode("utf-8")).hexdigest() != p387_row["sha256"]:
        raise SystemExit("p.387 segment hash changed before model-reference repair")
    surface = "il modello della gioia"
    if model_text.count(surface) != 1:
        raise SystemExit("expected one exact 'il modello della gioia' span in p.387")
    existing = next((row for row in statements if row.get("statement_id") == "st-chp19-p387-orsini-letter-jewel-and-handle"), None)
    if not existing or existing.get("predicate") != "giacomo_antonio_wanted_to_form_jewel_in_writer_presence_with_suitable_mixture_and_model_handle" or existing.get("qualifiers", {}).get("source_line_start") != 39:
        raise SystemExit("existing jewel statement no longer matches repair target")
    natural_key = ("modello della gioia in fondo orsini 171, c. i", "work")
    if any(((row.get("canonical_name") or "").strip().casefold(), (row.get("suggested_type") or "").strip().casefold()) == natural_key for row in candidates):
        raise SystemExit("model-of-jewel candidate natural key already exists")
    start = model_text.index(surface)
    mention_key = (P387, start, start + len(surface))
    if mention_key in {(row["segment_id"], int(row["start_char"]), int(row["end_char"])) for row in mentions}:
        raise SystemExit("model-of-jewel mention span already exists")
    line39 = (ROOT / segment_by_id[P387]["source_file"]).read_text(encoding="utf-8-sig").splitlines()[38]
    if "il modello della gioia" not in line39:
        raise SystemExit("model-of-jewel quote no longer lies on source line 39")
    new_candidate = {
        "candidate_id": candidate_id, "index_entry_id": "",
        "canonical_name": "Modello della gioia in Fondo Orsini 171, c. I",
        "index_page_range": "", "suggested_type": "work", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "The letter requires a Manichetto/Manichette to attach this model for holding by hand. Whether it is one of the four models mentioned earlier is unresolved.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{P387}#L39",
    }
    new_mention = {
        "mention_id": mention_id, "segment_id": P387, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)),
        "note": "Specific model of the gioia; do not conflate with Bernini's Madonna model or the group of four models.",
    }
    existing["predicate"] = "giacomo_antonio_wanted_to_form_jewel_from_suitable_mixture_because_silver_was_too_crude"
    existing["qualifiers"]["claim"] = "giacomo_antonio_wanted_to_form_jewel_in_writer_presence_from_suitable_mixture_because_silver_was_too_crude"
    existing["qualifiers"]["qualification"] = "This statement records the planned jewel and the writer's report that silver was too crude; the model/handle is recorded separately."
    existing["qualifiers"]["mentioned_candidate_ids"] = ["cand-10766", "cand-10768", "cand-10770", "cand-10779"]
    statements.append({
        "statement_id": statement_id, "segment_id": P387,
        "subject_candidate_id": "cand-10768", "object_candidate_id": candidate_id,
        "predicate": "jewel_model_needed_attachment_to_handle_for_holding",
        "qualifiers": {
            "source_line_start": 39, "source_line_end": 39,
            "printed_page": 387, "pdf_physical_page": 2,
            "claim": "giacomo_antonio_said_a_handle_was_needed_to_attach_the_jewel_model_for_holding",
            "speaker": "Unidentified writer of Fondo Orsini 171, c. I",
            "text_layer": "quoted archival letter",
            "qualification": "OCR reads Manichette; the printed page appears to read Manichetto. The source says this fitting would hold the jewel model by hand; the model's relation to the four earlier models is unresolved.",
            "mentioned_candidate_ids": ["cand-10766", "cand-10768", "cand-10770", candidate_id, "cand-10778"],
            "relation_candidate": True,
            "cited_material_not_independently_consulted": True,
        },
        "original_quote": line39,
        "source_file": segment_by_id[P387]["source_file"], "origin": "book",
    })
    if args.apply:
        paths = [candidate_path, mention_path, statement_path]
        for path in paths:
            backup = Path(str(path) + ".bak-s2-chp19-p387-modelref-20261004")
            if backup.exists():
                raise SystemExit(f"backup already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
        candidates.append(new_candidate)
        mentions.append(new_mention)
        write_csv(candidate_path, candidate_fields, candidates)
        write_csv(mention_path, mention_fields, mentions)
        write_jsonl(statement_path, statements)
        print("applied model-reference repair: +1 candidate, +1 mention, +1 split statement")
    else:
        print("dry-run model-reference repair")
        print("add work candidate for il modello della gioia; map the heuristic surface; split jewel and model/handle claims")
    raise SystemExit(0)

for sid in (P386_RECEIPT, P387, P388):
    if sid not in segment_by_id or sid not in coverage_by_id:
        raise SystemExit(f"missing S0 or S2 row: {sid}")
for sid in (P386_RECEIPT, P387):
    row = coverage_by_id[sid]
    if row["disposition"] != "queued" or row["migration_status"] != "pending":
        raise SystemExit(f"coverage precondition changed: {sid}")
if coverage_by_id[P388]["disposition"] != "queued":
    raise SystemExit("p.388 continuation must remain queued for its own reading")


def segment_text(sid: str) -> str:
    row = segment_by_id[sid]
    lines = (ROOT / row["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(lines[row["line_start"] - 1:row["line_end"]])
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != row["sha256"]:
        raise SystemExit(f"segment hash mismatch: {sid}")
    return text


texts = {sid: segment_text(sid) for sid in (P386_RECEIPT, P387)}

new_candidate_specs = [
    ("cand-10751", "Paolo Ottolini (vice procurator named in Brandi's 1682 receipt)", "person", P386_RECEIPT, 4,
     "The receipt says he paid 200 scudi on Domenico Brunacci's order. Full identity and the expansion of C. di G. are not established here."),
    ("cand-10752", "C. di G. (unexpanded abbreviation in Brandi's 1682 receipt)", "", P386_RECEIPT, 4,
     "Institutional/religious affiliation abbreviation after Paolo Ottolini's title; do not expand or merge with Casa di Gesù without evidence."),
    ("cand-10753", "Domenico Brunacci (vice rector named in Brandi's 1682 receipt)", "person", P386_RECEIPT, 4,
     "Named as the person on whose order Paolo Ottolini paid. Identity remains for S3."),
    ("cand-10754", "Casa di Probatione di S. Andrea (as named in the 1682 and 1679 receipts)", "institution", P386_RECEIPT, 4,
     "The named house is a paying/administrative body in these receipts. Keep its institutional identity distinct from the novitiate place candidate pending alignment."),
    ("cand-10755", "Receipt signed by Giacinto Brandi for the Chapel of the Passion works (28 March 1682)", "archive", P386_RECEIPT, 4,
     "Individually locatable receipt continued on printed p.387 and signed there by Brandi; the OCR opening is visually transcribed on printed p.386."),
    ("cand-10756", "Three paintings, vault work, and retouchings at the Chapel of the Passion (Brandi receipt, 1682)", "work", P386_RECEIPT, 4,
     "The receipt names tre Quadri, Volta, other retouchings, and painter's expenses, including work Brandi did or had done. It gives no individual titles. Possible relation to cand-5344–cand-5346 remains for S3."),
    ("cand-10757", "Receipt signed by Carlo Maratti for 100 scudi toward a Chapel of B. Stanislao painting (22 September 1679)", "archive", P387, 26,
     "A distinct signed receipt/undertaking. It promises a painting within one year subject to stated refund and incapacity conditions; no completion is claimed in this document."),
    ("cand-10758", "Receipt signed by Carlo Maratti for the Chapel of B. Stanislao painting (19 September 1687)", "archive", P387, 30,
     "A second, distinct receipt. It says the 300 scudi plus the 100 scudi received on 22 September 1679 formed the price of a painting Maratti had made."),
    ("cand-10759", "Severino Vittori (procurator named in Maratti's 1679 receipt)", "person", P387, 26,
     "Named as procurator of Casa di Probatione di S. Andrea and intermediary for the 100-scudi payment. Identity remains for S3."),
    ("cand-10760", "Chapel of B. Stanislao at S. Andrea (as named in Maratti's receipts)", "place", P387, 28,
     "Architectural space named as the intended location of the painting; do not equate it with another chapel or identify its dedication beyond the wording here."),
    ("cand-10761", "Unidentified painting promised and later reported made by Carlo Maratti for the Chapel of B. Stanislao", "work", P387, 28,
     "The 1679 and 1687 receipts locally concern one painting. Its identity with indexed or existing St Stanislaus works, including cand-1536/cand-5352, is deferred to S3."),
    ("cand-10762", "Casa di Gesù (as named in Maratti's 1687 receipt)", "institution", P387, 30,
     "A house identified as the affiliation of Giuseppe Tonini. It is not expanded or merged with the abbreviated C. di G. in Brandi's receipt."),
    ("cand-10763", "Giuseppe Tonini (intermediary named in Maratti's 1687 receipt)", "person", P387, 30,
     "Named as the person through whose hand the 300-scudi payment passed. Identity remains for S3."),
    ("cand-10764", "Unidentified person known to Giuseppe Tonini (Maratti's 1687 receipt)", "person", P387, 30,
     "The receipt says the 300 scudi came from a person known to Tonini; the payer is not named."),
    ("cand-10765", "Fondo Orsini, 171, c. I (letter printed in Appendix 2)", "archive", P387, 36,
     "Specific archival locator printed for the Appendix 2 letter. Its author and addressee are not identified by this excerpt."),
    ("cand-10766", "Unidentified writer of Fondo Orsini 171, c. I", "person", P387, 38,
     "First-person narrator of the letter; the excerpt does not name the writer. Do not infer that the writer is Paolo Giordano Orsini."),
    ("cand-10767", "Model of the Madonna brought from Bernini to Giacomo Ant:o (Fondo Orsini 171, c. I)", "work", P387, 38,
     "The letter says a model of the Madonna was received from Cavalier Bernino and taken to Giacomo Ant:o; no exact object or completed commission is identified."),
    ("cand-10768", "Giacomo Ant:o (recipient of a model in Fondo Orsini 171, c. I)", "person", P387, 38,
     "Name is abbreviated in the printed letter. Do not merge with Giacomo Antonio Boni or another indexed person before S3."),
    ("cand-10769", "Four differing models discussed in Fondo Orsini 171, c. I", "work", P387, 39,
     "The letter reports four models differing in thickness and height; their exact designs and relation to the Madonna model remain unclear."),
    ("cand-10770", "Jewel (gioia) discussed in Fondo Orsini 171, c. I", "work", P387, 39,
     "The letter describes forming a gioia from a suitable mixture and a model attached to a handle; exact form and relation among the models are unresolved."),
    ("cand-10771", "Unidentified German clean-casting specialist in Fondo Orsini 171, c. I", "person", P387, 40,
     "The letter calls him Il Tedesco and says he possessed a secret for clean casting and had died; no identity is supplied."),
    ("cand-10772", "Unnamed wife of the German clean-casting specialist in Fondo Orsini 171, c. I", "person", P387, 40,
     "The letter reports that she remarried two of her husband's apprentices in succession; no identity is supplied."),
    ("cand-10773", "First unnamed apprentice of the German specialist (Fondo Orsini 171, c. I)", "person", P387, 40,
     "The letter says the specialist's wife remarried one of his apprentices, who later also died; no identity is supplied."),
    ("cand-10774", "Second unnamed apprentice who married the specialist's widow (Fondo Orsini 171, c. I)", "person", P387, 40,
     "The letter says the widow later remarried another apprentice; no identity is supplied."),
    ("cand-10775", "Reported powder preparation for clean casting in Fondo Orsini 171, c. I", "procedure", P387, 40,
     "The letter reports a powder made from a word OCR reads dalco, apparently talco in the print, very well burnt and finely sifted. The precise material reading remains flagged for later source review."),
    ("cand-10776", "Four sapphires discussed in Fondo Orsini 171, c. I", "", P387, 41,
     "The letter asks whether any of four sapphires pleased the recipient; their ownership, identity, and appropriate object type are unresolved."),
    ("cand-10777", "Unidentified addressee addressed as V.E. in Fondo Orsini 171, c. I", "person", P387, 40,
     "The honorific V.E. is preserved, but the addressee is not identified or equated with the Duke of Bracciano."),
    ("cand-10778", "Manichetto/Manichette (handle fitting named in Fondo Orsini 171, c. I)", "", P387, 39,
     "OCR reads Manichette; the printed page appears to read singular Manichetto. The letter describes a fitting/handle for holding the jewel's model; type remains open."),
    ("cand-10779", "Silver described as too crude for the jewel in Fondo Orsini 171, c. I", "term", P387, 39,
     "Material mentioned in a technical description; this candidate records the source's wording and is not a separate metal object."),
]

existing_candidate_keys = {
    ((row.get("canonical_name") or "").strip().casefold(), (row.get("suggested_type") or "").strip().casefold())
    for row in candidates
}
for cid, name, kind, sid, line, detail in new_candidate_specs:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    key = (name.strip().casefold(), kind.strip().casefold())
    if key in existing_candidate_keys:
        raise SystemExit(f"candidate natural key already exists: {name} / {kind}")
    row = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{sid}#L{line}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row
    existing_candidate_keys.add(key)

new_mention_specs = [
    ("m-chp19-p387-001", P386_RECEIPT, "cand-10751", "P. Paolo Ottolini", 0, "Named payer in the receipt opening; identity remains open."),
    ("m-chp19-p387-002", P386_RECEIPT, "cand-10752", "C. di G.", 0, "Abbreviation is retained without expansion."),
    ("m-chp19-p387-003", P386_RECEIPT, "cand-10753", "P. Domenico Brunacci", 0, "Named as the person ordering the payment."),
    ("m-chp19-p387-004", P386_RECEIPT, "cand-10754", "Casa di Probatione di S. Andrea", 0, "House named in the receipt."),
    ("m-chp19-p387-005", P386_RECEIPT, "cand-10756", "tre Quadri", 0, "Three paintings are named collectively; no titles are supplied."),
    ("m-chp19-p387-006", P386_RECEIPT, "cand-10756", "Volta", 0, "Separate wording in the list of work paid for; whether it means vault decoration remains qualified."),
    ("m-chp19-p387-007", P386_RECEIPT, "cand-10756", "ritocchamenti", 0, "Other retouching named in the receipt."),
    ("m-chp19-p387-008", P387, "cand-5343", "Cappella della Passione", 0, "Site of the Brandi works in the receipt continuation."),
    ("m-chp19-p387-009", P387, "cand-0447", "Giacinto Brandi", 0, "Signature on the receipt continuation."),
    ("m-chp19-p387-010", P387, "cand-10754", "Casa di Probatione di S. Andrea", 0, "Paying house in the 1679 Maratti receipt."),
    ("m-chp19-p387-011", P387, "cand-10759", "P. Severino Vittori", 0, "Procurator/intermediary in the 1679 receipt."),
    ("m-chp19-p387-012", P387, "cand-1533", "Carlo Maratti", 0, "Signature on the 1679 receipt; index payment candidate used provisionally."),
    ("m-chp19-p387-013", P387, "cand-10760", "Cappella del B. Stanislao", 0, "Intended location of the promised painting."),
    ("m-chp19-p387-014", P387, "cand-1533", "Carlo Maratti", 1, "Signature on the 1687 receipt; locally the same person as the 1679 signer."),
    ("m-chp19-p387-015", P387, "cand-10763", "P. Giuseppe Tonini", 0, "Named intermediary in the 1687 receipt."),
    ("m-chp19-p387-016", P387, "cand-10762", "Casa di Gesù", 0, "House named as Tonini's affiliation; not expanded."),
    ("m-chp19-p387-017", P387, "cand-10764", "Persona a lui nota", 0, "Unnamed payer whom the receipt says was known to Tonini."),
    ("m-chp19-p387-018", P387, "cand-10760", "Cappella del B. Stanislao", 1, "Location named again in the 1687 receipt."),
    ("m-chp19-p387-019", P387, "cand-0428", "Paolo Giordano Orsini, duke of Bracciano", 0, "Name and title in the Appendix 2 heading; exact cross-index identity remains for S3."),
    ("m-chp19-p387-020", P387, "cand-0295", "Bernini", 0, "Artist named in the Appendix 2 heading."),
    ("m-chp19-p387-021", P387, "cand-2538", "Tacca", 0, "Artist named in the Appendix 2 heading; specific index subentry candidate reused provisionally."),
    ("m-chp19-p387-022", P387, "cand-5606", "Fondo Orsini", 0, "Archival fonds in the Appendix 2 heading."),
    ("m-chp19-p387-023", P387, "cand-5605", "Biblioteca Vallicelliana", 0, "Repository named in the Appendix 2 heading."),
    ("m-chp19-p387-024", P387, "cand-4490", "Rome", 0, "City named in the source locator."),
    ("m-chp19-p387-025", P387, "cand-10765", "171, c. I", 0, "Exact archival locator for the letter beginning below."),
    ("m-chp19-p387-026", P387, "cand-0295", "Caval.re Bernino", 0, "Variant form in the letter for the person named Bernini in the heading."),
    ("m-chp19-p387-027", P387, "cand-10767", "Modello della Mad.a", 0, "Model received from Bernini according to the unnamed letter writer."),
    ("m-chp19-p387-028", P387, "cand-10768", "Giacomo Ant:o", 0, "Abbreviated name in the letter; not merged with Boni."),
    ("m-chp19-p387-029", P387, "cand-10769", "tutti quattro i modelli", 0, "Four models shown by Giacomo Ant:o; their exact relation to the Madonna model is unresolved."),
    ("m-chp19-p387-030", P387, "cand-10770", "la gioia", 0, "Jewel/object as named in the letter."),
    ("m-chp19-p387-031", P387, "cand-10779", "l’Argento", 0, "Silver mentioned as too crude; print correction remains in the process record."),
    ("m-chp19-p387-032", P387, "cand-10778", "Manichette", 0, "OCR form; print appears to read Manichetto."),
    ("m-chp19-p387-033", P387, "cand-10770", "della gioia", 0, "Second reference to the jewel's model."),
    ("m-chp19-p387-034", P387, "cand-10771", "Il Tedesco", 0, "Unnamed German specialist said to have known a clean-casting secret."),
    ("m-chp19-p387-035", P387, "cand-10772", "la moglie", 0, "Unnamed wife of the specialist."),
    ("m-chp19-p387-036", P387, "cand-10773", "un suo garzone", 0, "First unnamed apprentice, later said to have died."),
    ("m-chp19-p387-037", P387, "cand-10773", "questo", 1, "Local pronoun referring to the first apprentice; occurrence 0 is questo giorno in the preceding Brandi receipt."),
    ("m-chp19-p387-038", P387, "cand-10774", "un altro suo garzone", 0, "Second unnamed apprentice in the reported remarriage."),
    ("m-chp19-p387-039", P387, "cand-10775", "la Polvere", 0, "Powder in the reported casting procedure."),
    ("m-chp19-p387-040", P387, "cand-10775", "dalco", 0, "OCR reads dalco; the print appears to read talco, not silently normalized."),
    ("m-chp19-p387-041", P387, "cand-10777", "V.E.", 0, "Honorific for an unidentified addressee; not assumed to be Paolo Giordano Orsini."),
    ("m-chp19-p387-042", P387, "cand-10776", "quattro zaffiri", 0, "Four sapphires; the sentence continues onto p.388."),
]

mention_keys = {(row["segment_id"], int(row["start_char"]), int(row["end_char"])) for row in mentions}
for mid, sid, cid, surface, occurrence, note in new_mention_specs:
    if any(row.get("mention_id") == mid for row in mentions):
        raise SystemExit(f"mention ID already exists: {mid}")
    text = texts[sid]
    starts = []
    pos = 0
    while True:
        pos = text.find(surface, pos)
        if pos < 0:
            break
        starts.append(pos)
        pos += len(surface)
    if occurrence >= len(starts):
        raise SystemExit(f"surface not found for {mid}: {surface!r}")
    start = starts[occurrence]
    end = start + len(surface)
    key = (sid, start, end)
    if key in mention_keys:
        raise SystemExit(f"mention natural key already exists: {sid} {start}:{end} {surface!r}")
    if cid not in candidate_by_id:
        raise SystemExit(f"mention foreign key missing: {mid} -> {cid}")
    mentions.append({
        "mention_id": mid, "segment_id": sid, "candidate_id": cid,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    mention_keys.add(key)


def quote_for(sid: str, start_line: int, end_line: int) -> str:
    row = segment_by_id[sid]
    source_lines = (ROOT / row["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    quote = "\n".join(source_lines[start_line - 1:end_line])
    if quote not in texts[sid]:
        raise SystemExit(f"quote does not reproduce in segment {sid}: L{start_line}-L{end_line}")
    return quote


def make_statement(statement_id, sid, source_start, source_end, predicate, subject, obj, claim,
                   speaker, text_layer, qualification, candidate_ids, relation_candidate, cross_refs=None,
                   migration_qualification="complete"):
    if any(row.get("statement_id") == statement_id for row in statements):
        raise SystemExit(f"statement ID already exists: {statement_id}")
    if any(row.get("segment_id") == sid and row.get("qualifiers", {}).get("claim", "").strip().casefold() == claim.strip().casefold() for row in statements):
        raise SystemExit(f"statement natural key already exists: {sid} / {claim}")
    missing = [cid for cid in candidate_ids if cid not in candidate_by_id]
    if missing:
        raise SystemExit(f"statement candidate foreign keys missing: {statement_id}: {missing}")
    segment_row = segment_by_id[sid]
    quote = quote_for(sid, source_start, source_end)
    qualifiers = {
        "source_line_start": source_start, "source_line_end": source_end,
        "printed_page": 386 if sid == P386_RECEIPT else 387,
        "pdf_physical_page": 1 if sid == P386_RECEIPT else 2,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": candidate_ids,
        "relation_candidate": relation_candidate,
        "cited_material_not_independently_consulted": True,
    }
    if cross_refs:
        qualifiers["cross_reference_segments"] = cross_refs
    if migration_qualification != "complete":
        qualifiers["migration_qualification"] = migration_qualification
    statements.append({
        "statement_id": statement_id, "segment_id": sid,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote, "source_file": segment_row["source_file"],
        "origin": "book",
    })


new_statement_specs = [
    ("st-chp19-p386-brandi-1682-receipt-opening", P386_RECEIPT, 4, 4,
     "brandi_acknowledged_200_scudi_full_payment_for_chapel_of_passion_work_group",
     "cand-0447", "cand-10756",
     "In the receipt opening, Giacinto Brandi says Paolo Ottolini paid him 200 scudi on Domenico Brunacci's order as full payment for three paintings, the vault, and other retouchings at the Chapel of the Passion.",
     "Giacinto Brandi, signature linked at p.387 L24", "quoted receipt opening",
     "C. di G. is left unexpanded. The receipt continues at p.387 L23-L24, where the painter's expenses, date, amount, and signature close the document. The three paintings are not identified with cand-5344–cand-5346 here.",
     ["cand-0447", "cand-10751", "cand-10752", "cand-10753", "cand-10754", "cand-10755", "cand-10756", "cand-5343"], True, [P387]),
    ("st-chp19-p387-brandi-1682-receipt-closing", P387, 23, 24,
     "brandi_declared_himself_paid_in_full_for_chapel_of_passion_work_by_28_march_1682",
     "cand-0447", "cand-10756",
     "Brandi states that he was fully satisfied through 28 March 1682 for 200 scudi for the painter's work and expenses he had done or had done in the Chapel of the Passion; he signs the receipt.",
     "Giacinto Brandi", "quoted receipt closing and signature",
     "The first part of this receipt is the visual transcription on printed p.386. fatti, o fatti fare preserves that Brandi either did the work himself or had it done; no authorship is assigned to every component.",
     ["cand-0447", "cand-10755", "cand-10756", "cand-5343"], True, [P386_RECEIPT]),
    ("st-chp19-p387-maratti-1679-advance", P387, 26, 29,
     "maratti_received_100_scudi_through_severino_vittori_from_casa_di_probatione_for_chapel_painting",
     "cand-1533", "cand-10761",
     "Carlo Maratti acknowledges 100 scudi from the Casa di Probatione di S. Andrea through its procurator Severino Vittori as an installment for a painting he promised for the Chapel of B. Stanislao.",
     "Carlo Maratti", "quoted receipt/undertaking dated 22 September 1679",
     "The receipt records an undertaking, not completion. Casa di Probatione is preserved as an institution distinct from the novitiate place candidate pending alignment.",
     ["cand-1533", "cand-10754", "cand-10757", "cand-10759", "cand-10760", "cand-10761"], True, None),
    ("st-chp19-p387-maratti-1679-promise-and-refund-terms", P387, 27, 28,
     "maratti_promised_chapel_painting_within_one_year_and_stated_conditional_refund_terms",
     "cand-1533", "cand-10761",
     "Maratti says he will make the painting within the next year and must return the 100 scudi or any other amount received if he fails, except where illness or another fortuitous accident prevents completion under the stated conditions.",
     "Carlo Maratti", "quoted receipt/undertaking dated 22 September 1679",
     "The exception is retained as written and is not generalized into a modern contract rule.",
     ["cand-1533", "cand-10757", "cand-10760", "cand-10761"], True, None),
    ("st-chp19-p387-maratti-1687-final-payment", P387, 30, 32,
     "maratti_reported_completed_chapel_painting_and_full_400_scudi_price_after_final_300_scudi_payment",
     "cand-1533", "cand-10761",
     "Maratti says the 300 scudi passed through Giuseppe Tonini from a person known to Tonini, together with 100 scudi received on 22 September 1679, constituted the price of the painting he had made for the Chapel of B. Stanislao, and declares himself fully paid.",
     "Carlo Maratti", "quoted receipt dated 19 September 1687",
     "The payer remains unnamed. This is a separate receipt from the 1679 undertaking but locally refers to the same painting and earlier 100-scudi installment.",
     ["cand-1533", "cand-10758", "cand-10760", "cand-10761", "cand-10762", "cand-10763", "cand-10764"], True, None),
    ("st-chp19-p387-appendix2-archive-locator", P387, 34, 36,
     "appendix2_heading_locates_documents_about_orsini_commissions_in_fondo_orsini",
     "cand-10765", "cand-5606",
     "The Appendix 2 heading describes documents relating to commissions from Paolo Giordano Orsini, Duke of Bracciano, to Bernini and Tacca, located in the Fondo Orsini at the Biblioteca Vallicelliana in Rome; item 171, c. I follows.",
     "Appendix heading", "editorial source locator",
     "The heading identifies the documentary subject and repository; it does not establish that the particular commission described in the following letter was completed. The letter author and addressee remain unidentified.",
     ["cand-10765", "cand-0428", "cand-0295", "cand-2538", "cand-5605", "cand-5606", "cand-4490"], True, None),
    ("st-chp19-p387-orsini-letter-model-transfer", P387, 38, 38,
     "unidentified_writer_received_madonna_model_from_bernini_and_took_it_to_giacomo_antonio",
     "cand-10766", "cand-10767",
     "The unidentified writer says he received a model of the Madonna from Cavalier Bernino on Friday evening and took it to Giacomo Ant:o the following morning, leaving it with him under a prior understanding.",
     "Unidentified writer of Fondo Orsini 171, c. I", "quoted archival letter",
     "The heading places the letter in the Orsini commission dossier but does not identify its writer or addressee. Giacomo Ant:o is not merged with Giacomo Antonio Boni.",
     ["cand-10766", "cand-10767", "cand-0295", "cand-10768"], True, None),
    ("st-chp19-p387-orsini-letter-four-models", P387, 39, 39,
     "giacomo_antonio_showed_four_models_that_differed_in_thickness_and_height",
     "cand-10768", "cand-10769",
     "The writer reports that Giacomo Ant:o showed four models differing in thickness and height, and that small differences mattered greatly at small scale.",
     "Unidentified writer of Fondo Orsini 171, c. I", "quoted archival letter",
     "The four models' exact designs and whether they are the Madonna model or jewel models are unresolved.",
     ["cand-10766", "cand-10768", "cand-10769"], True, None),
    ("st-chp19-p387-orsini-letter-jewel-and-handle", P387, 39, 39,
     "giacomo_antonio_wanted_to_form_jewel_in_writer_presence_with_suitable_mixture_and_model_handle",
     "cand-10768", "cand-10770",
     "The writer says Giacomo Ant:o wanted to form the gioia in his presence from a suitable mixture because the silver was too crude, and that a Manichette/Manichetto was needed to hold the jewel's model by hand.",
     "Unidentified writer of Fondo Orsini 171, c. I", "quoted archival letter",
     "OCR reads Manichette; the print appears to read Manichetto. The terms gioia and the relationship between the jewel and models are preserved without further identification.",
     ["cand-10766", "cand-10768", "cand-10770", "cand-10778", "cand-10779"], True, None),
    ("st-chp19-p387-orsini-letter-german-caster-death", P387, 40, 40,
     "unnamed_german_specialist_who_had_clean_casting_secret_was_reported_dead",
     "cand-10771", None,
     "The letter reports that the German specialist who knew the secret of clean casting had died.",
     "Unidentified writer of Fondo Orsini 171, c. I", "quoted archival letter",
     "This is the writer's report, not an independently verified biographical fact.",
     ["cand-10766", "cand-10771"], False, None),
    ("st-chp19-p387-orsini-letter-widow-first-remarriage", P387, 40, 40,
     "unnamed_widow_remarried_first_apprentice_who_was_reported_dead",
     "cand-10772", "cand-10773",
     "The letter reports that the specialist's wife remarried one of his apprentices and that this apprentice also died.",
     "Unidentified writer of Fondo Orsini 171, c. I", "quoted archival letter",
     "All identities are unnamed and remain local to this letter.",
     ["cand-10766", "cand-10771", "cand-10772", "cand-10773"], True, None),
    ("st-chp19-p387-orsini-letter-widow-second-remarriage", P387, 40, 40,
     "unnamed_widow_later_remarried_another_apprentice_of_the_german_specialist",
     "cand-10772", "cand-10774",
     "The letter reports that the widow later remarried another of the German specialist's apprentices.",
     "Unidentified writer of Fondo Orsini 171, c. I", "quoted archival letter",
     "All identities are unnamed and remain local to this letter.",
     ["cand-10766", "cand-10771", "cand-10772", "cand-10774"], True, None),
    ("st-chp19-p387-orsini-letter-powder-report", P387, 40, 40,
     "writer_reported_clean_casting_powder_was_burnt_dalco_or_talco_then_finely_sifted",
     "cand-10766", "cand-10775",
     "The writer says it had been found that the powder was made from a material OCR reads dalco, apparently talco in print, very well burnt and then sifted very finely; he would report further information if learned.",
     "Unidentified writer of Fondo Orsini 171, c. I", "quoted archival letter",
     "The source spelling and possible print reading remain explicitly provisional. This report does not verify the historical casting process.",
     ["cand-10766", "cand-10775"], False, None),
    ("st-chp19-p387-orsini-letter-four-sapphires", P387, 41, 41,
     "writer_asked_recipient_to_return_unselected_sapphires_and_say_if_payment_was_due",
     "cand-10766", "cand-10776",
     "The writer asks whether any of the four sapphires pleased the recipient, requests the others be returned, and asks to be told whether he should pay.",
     "Unidentified writer of Fondo Orsini 171, c. I", "quoted archival letter",
     "The final sentence continues onto printed p.388; V.E. is preserved as an unidentified addressee and not equated with Paolo Giordano Orsini.",
     ["cand-10766", "cand-10776", "cand-10777"], True, [P388], "partial"),
]

for spec in new_statement_specs:
    make_statement(*spec)

coverage_by_id[P386_RECEIPT].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L4-4",
    "note": "Receipt opening read against CHP-19Appendix.pdf physical page 1, printed p.386, and joined to its p.387 continuation and Brandi signature. The 200-scudi payment is for three paintings, the vault, and retouchings; individual paintings are not identified.",
})
coverage_by_id[P387].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L23-41",
    "note": "Printed p.387 (PDF physical page 2) read against CHP-19Appendix.pdf: closes Brandi's 28 March 1682 receipt; processes two distinct Carlo Maratti receipts dated 22 September 1679 and 19 September 1687; records Appendix 2 locator and Fondo Orsini 171, c. I letter. The final sapphires sentence at L41 continues on p.388; retain cross-reference and partial status until adjacent segment is read.",
})

if args.apply:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    for path in paths:
        backup = Path(str(path) + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing overwrite: {backup.name}")
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
    print("applied p.386-p.387 S2 migration; backups created for four tables")
else:
    print("dry-run p.386-p.387 S2 migration")
    print(f"candidates +{len(new_candidate_specs)}; mentions +{len(new_mention_specs)}; statements +{len(new_statement_specs)}")
    print("coverage: p.386 receipt complete; p.387 reviewed/partial pending p.388 sentence closure")
