from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
SEGMENTS = TABLES / "segments.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
CHP17_PDF = ROOT / "02-sources/01-book/CHP-17.pdf"
CHP18_PDF = ROOT / "02-sources/01-book/CHP-18Conclusion.pdf"
CHP20_PDF = ROOT / "02-sources/01-book/CHP-20Postscript.pdf"

EXPECTED_HASHES = {
    "statements": "3832d46c7beabdc2af58ef4d312c5657e0dd0165b0a0c92f20b9689f6a5861e9",
    "mentions": "5969d813e470280f273466e7f5f8c4843c6d00b329bc3ff1fc43611301b96ed5",
    "candidates": "47fbb9b37fe5fc480001521cb70f23f3e76d2196b6be78969d7b3fea828b93ed",
}
EXPECTED_PDFS = {
    CHP17_PDF: "fa9c9a4ebc484c481d13b0afb46f96bf94fe0631c65f0b742d0b0b9d9e0b7465",
    CHP18_PDF: "750ba8a4f4e7dc72e032746f7f3b15c3c70ef97a4220491fc3aa250a91ce2e29",
    CHP20_PDF: "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788",
}
SEGMENTS_TO_CHECK = {
    "chp-17:17_CHP-17_sec_i:l8-20": "4f3a9cd680dade7a13248a16b40639912ff4102640ab23f823e1bf72f20c2f83",
    "chp-17:17_CHP-17_sec_i:l26-35": "b7ee0285d3a437cbf212342c2367ffaef8a3419d6472837e7c35c8e5fe393784",
    "chp-17:17_CHP-17_sec_ii:l19-22": "4ef9f0d9870a51255d3704380b45e3c0bf47992d7f81510a14cc29d6de59130d",
    "chp-18:18_CHP-18Conclusion:l3-17": "82dcf7e4c5293e3898b5ce604330cd1b5b3237cc2b8c49592e743727880bf6da",
    "chp-20:20_CHP-20Postscript:l110-121": "7bc5e518a943cfa45d60c928cbff4ae1a8be817201c0d88fb9d8c4d00c5fe81b",
    "chp-20:20_CHP-20Postscript:l174-185": "f89e7f29219a2e744feed8dcbec55161f6cff0e71cb6c5059fe4be68314b1fa7",
}
EXPECTED_ASSETS = {
    "chp-17:17_CHP-17_sec_i:l8-20": "cbcb4e8f0eb163564f0b0c8e060c79f1a48981db45072a772c3ea16642ad3ca4",
    "chp-17:17_CHP-17_sec_i:l26-35": "cbcb4e8f0eb163564f0b0c8e060c79f1a48981db45072a772c3ea16642ad3ca4",
    "chp-17:17_CHP-17_sec_ii:l19-22": "d23af9f50ab9ac84fb250f5c7c5c260908096616ca83773a647977b8e07f4ff3",
    "chp-18:18_CHP-18Conclusion:l3-17": "a3d40952beead96ac48136610fa3fa15f1dcdfcd1a354ef9f2c2262343aeff14",
    "chp-20:20_CHP-20Postscript:l110-121": "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90",
    "chp-20:20_CHP-20Postscript:l174-185": "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90",
}
UNREASONED_IDS = {
    "st-chp17-p380-gallery-apparent-historical-survey",
    "st-chp17-p381-note2-catalogue-references",
    "st-chp17-p383-revolution-and-paintings-market",
    "st-chp17-p383-correr-kept-collecting-into-nineteenth-century",
    "st-chp18-conclusion-p384-lodoli",
    "st-chp18-conclusion-p384-patron-comparison-question",
    "st-chp20-p403-alazard-commissioned-franceschini-picture",
    "st-chp20-p408-venetian-enlightenment-recent-scholarship",
}
NEW_STATEMENTS = {
    "st-chp20-p408-venetian-enlightenment-attention-torcellan",
    "st-chp20-p408-venturi-attention-to-lodoli",
    "st-chp20-p408-torcellan-counterfactual-assessment",
}
NEW_CANDIDATES = {"cand-12423", "cand-12424"}
NEW_MENTIONS = {
    "m-s2-chp17-p380-manfrin-gallery-history-of-painting",
    "m-s2-chp17-p383-pictures-to-market-event",
}
BACKUP_SUFFIX = ".bak-s2-chp17-chp20-open-endpoints-20261015"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_jsonl(raw: bytes) -> list[dict]:
    return [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]


def parse_csv(raw: bytes) -> tuple[bool, list[str], list[dict[str, str]]]:
    bom = raw.startswith(b"\xef\xbb\xbf")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return bom, list(reader.fieldnames or []), list(reader)


def append_csv_record(raw: bytes, key: str, addition: dict[str, str]) -> bytes:
    bom, fields, parsed = parse_csv(raw)
    ids = [row.get(key, "") for row in parsed]
    if not fields or len(ids) != len(set(ids)) or set(addition) != set(fields):
        raise ValueError(f"Invalid {key} table schema or duplicate IDs.")
    if addition[key] in set(ids):
        raise ValueError(f"Planned {key} ID already exists: {addition[key]}")
    text = raw.decode("utf-8-sig")
    physical = text.splitlines(keepends=True)
    newline = "\r\n" if b"\r\n" in raw else "\n"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if reader.fieldnames != fields:
        raise ValueError("CSV header could not be mapped to physical lines.")
    previous_line = reader.line_num
    output = [physical[0]]
    for _row in reader:
        end_line = reader.line_num
        chunk = "".join(physical[previous_line:end_line])
        if not chunk:
            raise ValueError("Could not map CSV record to physical lines.")
        output.append(chunk)
        previous_line = end_line
    stream = io.StringIO(newline="")
    csv.DictWriter(stream, fieldnames=fields, lineterminator=newline).writerow(addition)
    output.append(stream.getvalue())
    return (("\ufeff" if bom else "") + "".join(output)).encode("utf-8")


def make_statement(statement_id: str, subject: str | None, obj: str | None, predicate: str,
                   claim: str, source_line_start: int, source_line_end: int,
                   quote: str, qualifiers: dict) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": "chp-20:20_CHP-20Postscript:l174-185",
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": source_line_start,
            "source_line_end": source_line_end,
            "printed_page": 408,
            "pdf_physical_page": 17,
            "claim": claim,
            **qualifiers,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve or justify the final eight S2 open endpoints reviewed in source order.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    segment_rows = read_jsonl(SEGMENTS.read_bytes())
    selected = {r["segment_id"]: r for r in segment_rows if r.get("segment_id") in SEGMENTS_TO_CHECK}
    if set(selected) != set(SEGMENTS_TO_CHECK):
        raise ValueError("A source segment under review is missing or duplicated.")
    texts: dict[str, str] = {}
    for segment_id, expected_hash in SEGMENTS_TO_CHECK.items():
        segment = selected[segment_id]
        if segment.get("sha256") != expected_hash or segment.get("asset_sha256") != EXPECTED_ASSETS[segment_id]:
            raise ValueError(f"Reviewed segment metadata changed: {segment_id}")
        source = ROOT / segment["source_file"]
        lines = source.read_text(encoding="utf-8-sig").splitlines()
        content = "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
        if sha(content.encode("utf-8")) != expected_hash:
            raise ValueError(f"Reviewed source text changed: {segment_id}")
        texts[segment_id] = content

    # Verify the physical scans used for the final p.380, p.383, p.384, p.403, and p.408 decisions.
    if not CHP17_PDF.exists() or not CHP18_PDF.exists() or not CHP20_PDF.exists():
        raise ValueError("One of the reviewed source PDFs is missing.")
    for path, expected in EXPECTED_PDFS.items():
        if sha(path.read_bytes()) != expected:
            raise ValueError(f"Reviewed PDF changed: {path.name}")

    raw = {
        "statements": STATEMENTS.read_bytes(),
        "mentions": MENTIONS.read_bytes(),
        "candidates": CANDIDATES.read_bytes(),
    }
    actual = {name: sha(data) for name, data in raw.items()}
    if actual != EXPECTED_HASHES:
        raise ValueError(f"Protected table snapshot changed: {actual}")

    statements = read_jsonl(raw["statements"])
    if len(statements) != 15158:
        raise ValueError("Unexpected statement inventory.")
    by_id = {r["statement_id"]: r for r in statements}
    if len(by_id) != len(statements):
        raise ValueError("Duplicate statement IDs.")
    _, candidate_fields, candidates = parse_csv(raw["candidates"])
    _, mention_fields, mentions = parse_csv(raw["mentions"])
    candidate_ids = {r["candidate_id"] for r in candidates}
    mention_ids = {r["mention_id"] for r in mentions}
    if NEW_CANDIDATES & candidate_ids or NEW_MENTIONS & mention_ids or NEW_STATEMENTS & set(by_id):
        raise ValueError("A planned candidate, mention, or statement ID already exists.")

    missing_reason_rows = {
        r["statement_id"] for r in statements
        if (r.get("qualifiers") or {}).get("relation_candidate") is True
        and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))
        and not (r.get("qualifiers") or {}).get("open_endpoint_reason")
    }
    if missing_reason_rows != UNREASONED_IDS:
        raise ValueError(f"The unreasoned open-endpoint queue changed: {sorted(missing_reason_rows)}")

    replacements: dict[str, dict] = {}
    for sid in UNREASONED_IDS:
        if sid not in by_id:
            raise ValueError(f"Required statement is missing: {sid}")
        replacements[sid] = json.loads(json.dumps(by_id[sid], ensure_ascii=False))

    # P.380: the named painting-history scope is an explicit conceptual object of the gallery's qualified program.
    p380 = replacements["st-chp17-p380-gallery-apparent-historical-survey"]
    p380q = p380.get("qualifiers") or {}
    if p380.get("subject_candidate_id") != "cand-1513" or p380.get("object_candidate_id") or p380q.get("relation_candidate") is not True:
        raise ValueError("The p.380 gallery statement no longer matches the reviewed open state.")
    phrase380 = "history of Italian (and, to some extent,\nFlemish) painting"
    start380 = texts[p380["segment_id"]].find(phrase380)
    if start380 < 0 or texts[p380["segment_id"]].count(phrase380) != 1:
        raise ValueError("The p.380 conceptual endpoint phrase is missing or ambiguous.")
    p380["object_candidate_id"] = "cand-12423"
    p380q["mentioned_candidate_ids"] = list(dict.fromkeys(p380q.get("mentioned_candidate_ids", []) + ["cand-12423"]))
    p380q["qualification"] = (
        "Haskell's 'apparently' and 'to some extent' remain in force. The endpoint names only the broad historical scope stated in the sentence."
    )
    p380q["relation_candidate_note"] = (
        "Haskell describes the gallery as apparently intended to give a general view of the history of Italian and, to some extent, Flemish painting. The source-defined term is the stated subject scope, not a verified curatorial program."
    )
    p380["qualifiers"] = p380q

    # P.381: this is a multi-source bibliographic pointer, not one identifiable work endpoint.
    p381 = replacements["st-chp17-p381-note2-catalogue-references"]
    p381q = p381.get("qualifiers") or {}
    if p381.get("subject_candidate_id") != "cand-3661" or p381.get("object_candidate_id") or p381q.get("relation_candidate") is not True:
        raise ValueError("The p.381 note statement no longer matches the reviewed open state.")
    p381q["open_endpoint_reason"] = (
        "The note aggregates V. Lazari and two Museo Correr catalogues as reading leads. Mariacher's and Pignatti's catalogue candidates are identified, but Lazari's cited work is not specified; the list has no single source endpoint and the author must not be merged with the catalogues."
    )
    p381["qualifiers"] = p381q

    # P.383: the named outcome is a source-defined market event; Correr's habitual buying remains a standalone activity claim.
    p383market = replacements["st-chp17-p383-revolution-and-paintings-market"]
    p383mq = p383market.get("qualifiers") or {}
    if p383market.get("subject_candidate_id") != "cand-10726" or p383market.get("object_candidate_id") or p383mq.get("relation_candidate") is not True:
        raise ValueError("The p.383 market statement no longer matches the reviewed open state.")
    phrase383 = "many pictures coming on to the market"
    start383 = texts[p383market["segment_id"]].find(phrase383)
    if start383 < 0 or texts[p383market["segment_id"]].count(phrase383) != 1:
        raise ValueError("The p.383 market-event phrase is missing or ambiguous.")
    p383market["object_candidate_id"] = "cand-12424"
    p383mq["mentioned_candidate_ids"] = list(dict.fromkeys(p383mq.get("mentioned_candidate_ids", []) + ["cand-12424"]))
    p383mq["qualification"] = (
        "Haskell attributes the market event to the upheaval, but identifies no individual pictures, collections, transactions, or market location."
    )
    p383mq["relation_candidate_note"] = (
        "The outcome is the explicitly stated arrival of many pictures on the market. It is represented as a bounded source-defined event endpoint; no specific works, sellers, collections, or place are inferred."
    )
    p383market["qualifiers"] = p383mq

    p383buying = replacements["st-chp17-p383-correr-kept-collecting-into-nineteenth-century"]
    p383bq = p383buying.get("qualifiers") or {}
    if p383buying.get("subject_candidate_id") != "cand-0857" or p383buying.get("object_candidate_id") or p383bq.get("relation_candidate") is not True:
        raise ValueError("The p.383 Correr activity statement no longer matches the reviewed open state.")
    p383bq["relation_candidate"] = False
    p383bq["relation_candidate_note"] = (
        "This is Haskell's open-ended biographical report that Correr continued buying into the nineteenth century. The passage names no acquired work, seller, transaction, or bounded activity event; retain the claim without inventing a second entity endpoint."
    )
    p383buying["qualifiers"] = p383bq

    # P.384: the generic office remains unidentified; rhetorical questions do not assert comparative facts.
    p384lodoli = replacements["st-chp18-conclusion-p384-lodoli"]
    p384lq = p384lodoli.get("qualifiers") or {}
    if p384lodoli.get("subject_candidate_id") != "cand-1411" or p384lodoli.get("object_candidate_id") or p384lq.get("relation_candidate") is not True:
        raise ValueError("The p.384 Lodoli statement no longer matches the reviewed open state.")
    p384lq["open_endpoint_reason"] = (
        "Haskell names only an 'official government post'; neither the office nor the appointing government is identified. The generic role is not treated as a specific institution, position, or appointment event."
    )
    p384lodoli["qualifiers"] = p384lq

    p384comparison = replacements["st-chp18-conclusion-p384-patron-comparison-question"]
    p384cq = p384comparison.get("qualifiers") or {}
    if p384comparison.get("subject_candidate_id") or p384comparison.get("object_candidate_id") or p384cq.get("relation_candidate") is not True:
        raise ValueError("The p.384 comparison statement no longer matches the reviewed open state.")
    p384cq["relation_candidate"] = False
    p384cq["relation_candidate_note"] = (
        "The passage consists of rhetorical questions about comparative tolerance and education. It does not assert an answer, ranking, or factual relation among the named patrons; the question and all named candidates remain recorded."
    )
    p384comparison["qualifiers"] = p384cq

    # P.403: the source identifies intermediaries and artist, but not the commissioner.
    p403 = replacements["st-chp20-p403-alazard-commissioned-franceschini-picture"]
    p403q = p403.get("qualifiers") or {}
    if p403.get("subject_candidate_id") or p403.get("object_candidate_id") != "cand-6888" or p403q.get("relation_candidate") is not True:
        raise ValueError("The p.403 commission statement no longer matches the reviewed open state.")
    p403q["open_endpoint_reason"] = (
        "Haskell says the picture was commissioned through Colbert and Abate Luigi Strozzi from Franceschini, but does not name the commissioner. The intermediaries are not promoted to commissioners, and the nearby Louis XIV context and Plate 66 title do not identify the commissioning party."
    )
    p403["qualifiers"] = p403q

    # P.408: atomize the three supported relation claims and preserve the counterfactual as non-relational.
    p408 = replacements["st-chp20-p408-venetian-enlightenment-recent-scholarship"]
    p408q = p408.get("qualifiers") or {}
    if p408.get("subject_candidate_id") != "cand-11108" or p408.get("object_candidate_id") or p408q.get("relation_candidate") is not True:
        raise ValueError("The p.408 scholarship statement no longer matches the reviewed open state.")
    if not {"cand-2751", "cand-2644", "cand-1411"}.issubset(set(p408q.get("mentioned_candidate_ids", []))):
        raise ValueError("The p.408 scholar or Lodoli mentions changed.")
    p408["object_candidate_id"] = "cand-2751"
    p408["predicate"] = "receives_serious_recent_attention_from"
    p408q.update({
        "source_line_start": 176,
        "source_line_end": 177,
        "claim": "Haskell reports that the Venetian Enlightenment had received serious recent attention from Franco Venturi.",
        "qualification": "The cited Venturi publications are citation leads and have not been independently consulted; no broader intellectual lineage is inferred.",
        "mentioned_candidate_ids": ["cand-11108", "cand-2751"],
        "footnote_markers": [1],
        "footnote_text_pending": False,
        "footnote_segment": "chp-20:20_CHP-20Postscript:l211-280",
        "footnote_refs": [{"marker": 1, "segment_id": "chp-20:20_CHP-20Postscript:l211-280", "source_line": 267}],
        "footnote_statement_ids": ["st-chp20-p408-n01a-citation", "st-chp20-p408-n01b-citation"],
        "footnote_body_link_status": "linked",
        "cited_material_not_independently_consulted": True,
        "relation_candidate_note": "Haskell attributes serious recent attention to the Venetian Enlightenment to Franco Venturi. The two cited publications remain citation leads and were not independently consulted.",
    })
    p408q.pop("ocr_corrections", None)
    p408["original_quote"] = "The Venetian Enlightenment has received serious attention in recent years from Franco Venturi"
    p408["qualifiers"], p408["object_candidate_id"] = p408q, "cand-2751"

    quote_group = (
        "The Venetian Enlightenment has received serious attention in recent years from\n"
        "Franco Venturi1 (who pays much attention to the significance oiLodoli)2 and Gianfranco\n"
        "Torcellan3 (but for whose tragic death at the age of twenty-eight this book would have begji much improved)."
    )
    venturi_ref = make_statement(
        "st-chp20-p408-venetian-enlightenment-attention-torcellan",
        "cand-11108", "cand-2644", "receives_serious_recent_attention_from",
        "Haskell reports that the Venetian Enlightenment had received serious recent attention from Gianfranco Torcellan.",
        176, 178, quote_group,
        {
            "speaker": "Haskell",
            "text_layer": "authorial retrospective and report of scholarship",
            "qualification": "The citation identifies Torcellan's publication but it was not independently consulted; his identity remains for S3 alignment.",
            "mentioned_candidate_ids": ["cand-11108", "cand-2644"],
            "footnote_markers": [3],
            "footnote_text_pending": False,
            "footnote_segment": "chp-20:20_CHP-20Postscript:l211-280",
            "footnote_refs": [{"marker": 3, "segment_id": "chp-20:20_CHP-20Postscript:l211-280", "source_line": 268}],
            "footnote_statement_ids": ["st-chp20-p408-n03-citation"],
            "footnote_body_link_status": "linked",
            "cited_material_not_independently_consulted": True,
            "relation_candidate": True,
            "relation_candidate_note": "Haskell attributes serious recent attention to the Venetian Enlightenment to Gianfranco Torcellan. The cited publication remains a citation lead and was not independently consulted.",
        },
    )
    lodoli_ref = make_statement(
        "st-chp20-p408-venturi-attention-to-lodoli",
        "cand-2751", "cand-1411", "pays_attention_to_significance_of",
        "Haskell says Franco Venturi pays much attention to the significance of Padre Lodoli.",
        177, 177, "Franco Venturi1 (who pays much attention to the significance oiLodoli)2",
        {
            "speaker": "Haskell",
            "text_layer": "authorial report of scholarship",
            "qualification": "Footnote 2 cites Venturi, 1969, pp. 295–299; that cited passage was not independently consulted.",
            "mentioned_candidate_ids": ["cand-2751", "cand-1411"],
            "footnote_markers": [2],
            "footnote_text_pending": False,
            "footnote_segment": "chp-20:20_CHP-20Postscript:l211-280",
            "footnote_refs": [{"marker": 2, "segment_id": "chp-20:20_CHP-20Postscript:l211-280", "source_line": 267}],
            "footnote_statement_ids": ["st-chp20-p408-n02-citation"],
            "footnote_body_link_status": "linked",
            "cited_material_not_independently_consulted": True,
            "ocr_corrections": [{"source_line": 177, "ocr": "oiLodoli", "print": "of Lodoli", "basis": "CHP-20Postscript.pdf physical page 17, printed p.408."}],
            "relation_candidate": True,
            "relation_candidate_note": "This is Haskell's report of Venturi's scholarly attention to Lodoli; it does not independently verify Venturi's analysis.",
        },
    )
    torcellan_aside = make_statement(
        "st-chp20-p408-torcellan-counterfactual-assessment",
        "cand-2644", None, "counterfactual_assessment_of_book_after_torcellan_death",
        "Haskell says that but for Gianfranco Torcellan's tragic death at age twenty-eight, this book would have been much improved.",
        178, 178, "but for whose tragic death at the age of twenty-eight this book would have begji much improved",
        {
            "speaker": "Haskell",
            "text_layer": "authorial counterfactual evaluation",
            "qualification": "This is an unrealized counterfactual about the book, not an asserted factual relation or actual improvement event. The statement preserves Haskell's assessment; Torcellan's biography remains a source-reported claim.",
            "mentioned_candidate_ids": ["cand-2644"],
            "footnote_markers": [3],
            "footnote_text_pending": False,
            "footnote_segment": "chp-20:20_CHP-20Postscript:l211-280",
            "footnote_refs": [{"marker": 3, "segment_id": "chp-20:20_CHP-20Postscript:l211-280", "source_line": 268}],
            "footnote_statement_ids": ["st-chp20-p408-n03-citation"],
            "footnote_body_link_status": "linked",
            "cited_material_not_independently_consulted": True,
            "ocr_corrections": [{"source_line": 178, "ocr": "begji", "print": "been", "basis": "CHP-20Postscript.pdf physical page 17, printed p.408."}],
            "relation_candidate": False,
            "relation_candidate_note": "The clause is a counterfactual editorial assessment, not a fact about a relation between Torcellan and a bounded work or event. Keep it as a non-relational statement.",
        },
    )

    # Add only two candidates: a named conceptual scope and a named market outcome event.
    def candidate(candidate_id: str, name: str, kind: str, detail: str, source_ref: str) -> dict[str, str]:
        values = {key: "" for key in candidate_fields}
        values.update({
            "candidate_id": candidate_id,
            "canonical_name": name,
            "suggested_type": kind,
            "status": "open",
            "detail": detail,
            "candidate_origin": "body-mention",
            "candidate_source_ref": source_ref,
        })
        return values

    candidate_rows = [
        candidate(
            "cand-12423",
            "History of Italian and some Flemish painting described as the subject of Manfrin's gallery",
            "term",
            "Haskell says Manfrin's vast gallery was apparently designed to give a general view of this history. Preserve the qualifications 'apparently' and 'to some extent'; this term records the stated scope and does not verify curatorial intent.",
            "chp-17:17_CHP-17_sec_i:l8-20#L11",
        ),
        candidate(
            "cand-12424",
            "Many pictures coming onto the market after the 1797 upheaval",
            "event",
            "Haskell attributes the arrival of many pictures on the market to the break-up of aristocratic life and collections after the revolution and ensuing occupation. No individual work, collection, transaction, or market location is named.",
            "chp-17:17_CHP-17_sec_ii:l19-22#L22",
        ),
    ]
    mention_rows = [
        {
            "mention_id": "m-s2-ch17-p380-manfrin-gallery-history-of-painting",
            "segment_id": "chp-17:17_CHP-17_sec_i:l8-20",
            "candidate_id": "cand-12423",
            "surface_form": phrase380,
            "start_char": str(start380),
            "end_char": str(start380 + len(phrase380)),
            "note": "Broad conceptual subject of the gallery's qualified historical survey; the phrase crosses the source line break.",
        },
        {
            "mention_id": "m-s2-ch17-p383-pictures-to-market-event",
            "segment_id": "chp-17:17_CHP-17_sec_ii:l19-22",
            "candidate_id": "cand-12424",
            "surface_form": phrase383,
            "start_char": str(start383),
            "end_char": str(start383 + len(phrase383)),
            "note": "Collective market event stated by Haskell; individual pictures and transactions remain unidentified.",
        },
    ]
    candidate_out, mention_out = raw["candidates"], raw["mentions"]
    for row in candidate_rows:
        candidate_out = append_csv_record(candidate_out, "candidate_id", row)
    for row in mention_rows:
        mention_out = append_csv_record(mention_out, "mention_id", row)

    # Rewrite reviewed rows in place and insert the three atomized p.408 statements after their source row.
    additions = [lodoli_ref, venturi_ref, torcellan_aside]
    bom = raw["statements"].startswith(b"\xef\xbb\xbf")
    output: list[str] = []
    seen: set[str] = set()
    for line in raw["statements"].decode("utf-8-sig").splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        row = json.loads(body)
        sid = row.get("statement_id")
        if sid in replacements:
            output.append(json.dumps(replacements[sid], ensure_ascii=False, separators=(",", ":")) + ending)
            seen.add(sid)
            if sid == "st-chp20-p408-venetian-enlightenment-recent-scholarship":
                for addition in additions:
                    output.append(json.dumps(addition, ensure_ascii=False, separators=(",", ":")) + ending)
        else:
            output.append(line)
    if seen != set(replacements):
        raise ValueError(f"Not all reviewed statements were rewritten exactly once: {seen}")
    statement_out = (("\ufeff" if bom else "") + "".join(output)).encode("utf-8")

    after_statements = read_jsonl(statement_out)
    after_candidates = parse_csv(candidate_out)[2]
    after_mentions = parse_csv(mention_out)[2]
    if len(after_statements) != 15161 or len(after_candidates) != 12402 or len(after_mentions) != 26616:
        raise ValueError("Unexpected post-write inventory preview.")
    if {r["statement_id"] for r in after_statements}.__len__() != len(after_statements):
        raise ValueError("Post-write statement IDs are not unique.")
    if {r["candidate_id"] for r in after_candidates}.__len__() != len(after_candidates):
        raise ValueError("Post-write candidate IDs are not unique.")
    if {r["mention_id"] for r in after_mentions}.__len__() != len(after_mentions):
        raise ValueError("Post-write mention IDs are not unique.")

    open_after = [
        r for r in after_statements
        if (r.get("qualifiers") or {}).get("relation_candidate") is True
        and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))
    ]
    no_reason_after = [r["statement_id"] for r in open_after if not (r.get("qualifiers") or {}).get("open_endpoint_reason")]
    if len(open_after) != 331 or no_reason_after:
        raise ValueError(f"Unexpected open-endpoint state after plan: open={len(open_after)}, no_reason={no_reason_after}")

    plan = {
        "files": {
            "statements": {"before": sha(raw["statements"]), "after": sha(statement_out)},
            "mentions": {"before": sha(raw["mentions"]), "after": sha(mention_out)},
            "candidates": {"before": sha(raw["candidates"]), "after": sha(candidate_out)},
        },
        "reviewed_open_queue": sorted(UNREASONED_IDS),
        "decisions": {
            "resolved_with_source_defined_endpoint": [
                "st-chp17-p380-gallery-apparent-historical-survey",
                "st-chp17-p383-revolution-and-paintings-market",
                "st-chp20-p408-venetian-enlightenment-recent-scholarship",
            ],
            "reclassified_as_nonrelational": [
                "st-chp17-p383-correr-kept-collecting-into-nineteenth-century",
                "st-chp18-conclusion-p384-patron-comparison-question",
                "st-chp20-p408-torcellan-counterfactual-assessment",
            ],
            "retained_open_with_reason": [
                "st-chp17-p381-note2-catalogue-references",
                "st-chp18-conclusion-p384-lodoli",
                "st-chp20-p403-alazard-commissioned-franceschini-picture",
            ],
        },
        "inventory_after": {"candidates": 12402, "mentions": 26616, "statements": 15161, "open_true_relations": 331, "open_without_reason": 0},
    }
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    if args.preview:
        return 0

    targets = [STATEMENTS, MENTIONS, CANDIDATES]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in targets]
    if any(path.exists() for path in backups):
        raise ValueError("A planned recovery backup already exists.")
    temps = [path.with_name(path.name + ".tmp-s2-chp17-chp20-open-endpoints-20261015") for path in targets]
    if any(path.exists() for path in temps):
        raise ValueError("A planned temporary output already exists.")
    for path, content in zip(temps, [statement_out, mention_out, candidate_out]):
        path.write_bytes(content)
    for path, temp in zip(targets, temps):
        shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
        temp.replace(path)
    print("APPLIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
