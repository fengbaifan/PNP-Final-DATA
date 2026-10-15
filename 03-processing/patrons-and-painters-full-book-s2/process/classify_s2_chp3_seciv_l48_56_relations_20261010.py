from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
PDF = ROOT / "02-sources/01-book/CHP-3.pdf"
PAGE80 = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/.tmp_chp3_p80_phys22_20261010.png"
PAGE81 = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/.tmp_chp3_p81_phys23_20261010.png"
SEGMENT = "chp-3:03_CHP-3_sec_iv:l48-56"

EXPECTED = {
    TABLE: "2ff381fa6b8ab70b67cdc352ea68f835500cd55c24373fb105faa53b82f55765",
    CANDIDATES: "4522bd1e657e35b1ce5080de1cc966ddc6ebe35ffcb641e5b18a05cdd49277de",
    MENTIONS: "a9d36031a66d3161aa1e1a2ae1916875c06f6fda5f70c32393af86214743b582",
    COVERAGE: "e9c4b793d40f00d6d5cb0952413aae2e7c55787a5a820bfe9dcc27e9159b66cc",
    SOURCE: "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
    PAGE80: "4771b6ae63677a9357e6f1d51aecc40c27e9487d468b2e9cf512a4b2b123703c",
    PAGE81: "9eaecbbb9be2701cbdd62450c83c4c701203bf5903ab4565f0f6bd02a1c6dcd0",
}

BACKUPS = {
    TABLE: TABLE.with_name(TABLE.name + ".bak-s2-chp3-sec-iv-l48-56-relations-20261010"),
    CANDIDATES: CANDIDATES.with_name(
        CANDIDATES.name + ".bak-s2-chp3-sec-iv-l48-56-following-virtuosi-work-20261010"
    ),
    MENTIONS: MENTIONS.with_name(
        MENTIONS.name + ".bak-s2-chp3-sec-iv-l48-56-following-virtuosi-work-20261010"
    ),
}

KEEP_TRUE = {"st-chp3-seciv-l48-56-apse-conch-painted"}

DECISIONS: dict[str, tuple[bool, str]] = {
    "st-chp3-seciv-l48-56-avviso-attribution": (
        True,
        "The quoted 1675 avviso reports design and execution roles for the newly painted dome; retain the source-to-work report and split the two artist-to-work attributions below.",
    ),
    "st-chp3-seciv-l48-56-avviso-citation-locator": (
        True,
        "Haskell explicitly locates the unidentified 1675 avviso in Roma, volume XVIII (1940), page 238; the OCR page-number spacing remains recorded.",
    ),
    "st-chp3-seciv-l48-56-avviso-dome-unveiling": (
        True,
        "The avviso reports Jesuit fathers unveiling the newly painted Gesù dome; keep the event distinct from the architectural dome and the painting.",
    ),
    "st-chp3-seciv-l48-56-bernini-role-accepted": (
        True,
        "Haskell reports that Bernini's role in the Gesù fresco undertaking was emphasized and accepted by historians; this records his account of historiography, not an independent attribution ruling.",
    ),
    "st-chp3-seciv-l48-56-controversy-motives-caution": (
        False,
        "This is Haskell's general caution about distinguishing principle from jealousy in controversies, not a claim that assigns a motive to the Molinos controversy.",
    ),
    "st-chp3-seciv-l48-56-daily-communion-doctrine": (
        True,
        "Haskell attributes the reported daily-Communion view to Molinos; preserve the request condition and the author's report status.",
    ),
    "st-chp3-seciv-l48-56-enggass-citation": (
        True,
        "Haskell cites Enggass (1957) for a modern examination of the dome-attribution problem; the bibliography resolves the article identity, but the article was not independently consulted.",
    ),
    "st-chp3-seciv-l48-56-fresco-shares-unknown": (
        False,
        "This reports that individual contributions are unknown; the named participants remain in qualifiers without asserting a specific contribution relation.",
    ),
    "st-chp3-seciv-l48-56-gaulli-proposed-for-tribune": (
        True,
        "Haskell says Oliva scarcely dared to propose Gaulli for the further tribune task; preserve the hesitation and do not imply that this proposal was carried out.",
    ),
    "st-chp3-seciv-l48-56-jesuit-opposition": (
        True,
        "The sentence makes two claims: both doctrines conflict with Jesuit views, and the Jesuits then react strongly. This row is narrowed to the reaction; two doctrine-to-Jesuit statements are added.",
    ),
    "st-chp3-seciv-l48-56-jesuits-and-oliva-implicated": (
        True,
        "The Society of Jesus is explicitly described as centrally implicated; Oliva is a separate appositional participant and receives a companion statement.",
    ),
    "st-chp3-seciv-l48-56-left-transept-1685": (
        True,
        "Haskell explicitly attributes the 1685 left-transept painting above the St Ignatius altar to Gaulli; retain the date and location qualifier.",
    ),
    "st-chp3-seciv-l48-56-letter-foundation-claim": (
        True,
        "This is the continuing September 1679 letter as a document describing the Gesù church and tribune; retain Oliva and the Duke as author and recipient, and do not treat the letter's rhetoric as independently verified fact.",
    ),
    "st-chp3-seciv-l48-56-molinos-arrived-1664": (
        True,
        "The clause says the controversy began soon after Molinos's 1664 arrival; model the temporal relation between the two events and leave the destination unstated.",
    ),
    "st-chp3-seciv-l48-56-molinos-gained-following": (
        True,
        "The passage explicitly says Molinos acquired a wide and influential following. Add a source-limited open group candidate because its members and organization are unspecified.",
    ),
    "st-chp3-seciv-l48-56-molinos-prestige-clause": (
        True,
        "Haskell infers that the Jesuits could not have viewed Molinos's growing prestige favorably; preserve the modal inference without converting it into a claim of jealousy.",
    ),
    "st-chp3-seciv-l48-56-no-programme-found": (
        False,
        "This is an epistemic status report that no programme had come to light, not a relation between two entities.",
    ),
    "st-chp3-seciv-l48-56-oliva-share-inferred": (
        True,
        "Haskell says Oliva's share can be inferred from iconographic complexity; retain the inferential status and do not assert a documented programme.",
    ),
    "st-chp3-seciv-l48-56-oral-arrangements-probable": (
        True,
        "Haskell presents oral arrangements among Oliva, Bernini, and Gaulli as probable. Preserve all three participants and do not infer pairwise collaboration or a documented plan.",
    ),
    "st-chp3-seciv-l48-56-passive-contemplation-doctrine": (
        True,
        "Haskell attributes the reported preference for passive contemplation over active meditation to Molinos; retain the contrast and report status.",
    ),
    "st-chp3-seciv-l48-56-ranuccio-offer": (
        True,
        "Ranuccio agreed to employ Gaulli for the proposed task; separate the distinct offer of 3000 scudi into a companion statement and do not mark payment as made.",
    ),
    "st-chp3-seciv-l48-56-roman-church-controversy": (
        True,
        "Haskell describes the Roman Church as shaken by the controversy in the 1670s; the linked note is a bibliographic pointer, not independent verification.",
    ),
    "st-chp3-seciv-l48-56-small-vault-area-painted": (
        True,
        "Haskell says Gaulli painted only a small fraction of the tribune vault; keep this distinct from the separate apse-conch painting statement.",
    ),
    "st-chp3-seciv-l48-56-tribune-and-high-altar-bare": (
        False,
        "The coordinated phrase reports the bare state of two spaces, not a relation between them. Split it into two scalar status statements.",
    ),
    "st-chp3-seciv-l48-56-virtuosi-critical": (
        True,
        "The avviso reports that an unnamed group of virtuosi did not highly praise the dome design/work. Add a source-limited group and a distinct work candidate; distinguish the dome painting from the architectural dome.",
    ),
    "st-chp3-seciv-l48-56-xavier-chapel-other-artist": (
        True,
        "Haskell says an unidentified artist decorated the Chapel of St Francis Xavier after further difficulties; preserve the unidentified artist and sequence.",
    ),
}

NEW_CANDIDATES = {
    "cand-11604": "Unnamed followers acquired by Miguel de Molinos",
    "cand-11605": "Virtuosi who commented on the newly painted Gesù dome in 1675",
    "cand-11606": "Newly painted decoration of the Gesù dome reported in the 1675 avviso",
}

NEW_MENTIONS = {
    "m-chp3-seciv-l48-56-0059": ("cand-11604", "a wide and exceedingly influential following"),
    "m-chp3-seciv-l48-56-0060": ("cand-11605", "molti virtuosi"),
    "m-chp3-seciv-l48-56-0061": (
        "cand-11606",
        "la cuppola della loro Chiesa . .. dipinta da nuovo",
    ),
}

NEW_STATEMENT_IDS = {
    "st-chp3-seciv-l48-56-bernini-designed-dome-painting",
    "st-chp3-seciv-l48-56-gaulli-executed-dome-painting",
    "st-chp3-seciv-l48-56-oliva-implicated",
    "st-chp3-seciv-l48-56-jesuits-opposed-daily-communion",
    "st-chp3-seciv-l48-56-jesuits-opposed-passive-contemplation",
    "st-chp3-seciv-l48-56-ranuccio-offered-payment",
    "st-chp3-seciv-l48-56-high-altar-remained-bare",
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str], bytes]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader), list(reader.fieldnames or []), raw


def encode_jsonl(rows: list[dict], raw: bytes) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    prefix = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    return prefix + b"".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + newline
        for row in rows
    )


def encode_csv(rows: list[dict[str, str]], fields: list[str], raw: bytes) -> bytes:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    prefix = "\ufeff" if raw.startswith(b"\xef\xbb\xbf") else ""
    return (prefix + stream.getvalue()).encode("utf-8")


def atomic_write(path: Path, payload: bytes) -> None:
    temp: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as stream:
            stream.write(payload)
            temp = Path(stream.name)
        os.replace(temp, path)
    finally:
        if temp and temp.exists():
            temp.unlink()


def normalized(text: str) -> str:
    return " ".join(text.split())


def mark_relation(row: dict, flag: bool, note: str) -> None:
    qualifiers = dict(row.get("qualifiers") or {})
    qualifiers["relation_candidate"] = flag
    qualifiers["relation_candidate_note"] = note
    row["qualifiers"] = qualifiers


def new_statement(
    statement_id: str,
    subject: str | None,
    predicate: str,
    object_id: str | None,
    quote: str,
    start_line: int,
    end_line: int,
    claim: str,
    qualifiers: dict,
    relation: bool,
    relation_note: str,
) -> dict:
    q = {
        "source_line_start": start_line,
        "source_line_end": end_line,
        "claim": claim,
        "speaker": "Haskell reporting the unidentified 1675 avviso",
        "text_layer": "quoted contemporary report",
        "print_page": 81,
        "pdf_physical_page": 23,
        "footnote_number": 1,
        "footnote_page": 81,
        "footnote_segment": SEGMENT,
        "footnote_source_line": 55,
        "footnote_pending": False,
        **qualifiers,
        "relation_candidate": relation,
        "relation_candidate_note": relation_note,
    }
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": q,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify and atomize S2 statements for printed p.81, L49-56.")
    parser.add_argument("--apply", action="store_true", help="Write only after fixed preflight checks pass; default is dry-run.")
    args = parser.parse_args()

    for path, expected in EXPECTED.items():
        require(path.exists() and digest(path) == expected, f"preflight hash changed: {path.relative_to(ROOT)}")
    require(all(not path.exists() for path in BACKUPS.values()), "one or more recovery backups already exist")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_rows = [row for row in read_jsonl(SEGMENTS) if row.get("segment_id") == SEGMENT]
    require(len(segment_rows) == 1, "source segment is missing or duplicated")
    start_line, end_line = segment_rows[0].get("line_start"), segment_rows[0].get("line_end")
    require((start_line, end_line) == (48, 56), "source segment line range changed")
    segment_text = "\n".join(source_lines[start_line - 1 : end_line])

    raw_table = TABLE.read_bytes()
    statements = read_jsonl(TABLE)
    require(len(statements) == 12780, "statement count changed")
    require(len({row["statement_id"] for row in statements}) == len(statements), "statement IDs are not unique")
    by_id = {row["statement_id"]: row for row in statements}
    segment_statements = [row for row in statements if row.get("segment_id") == SEGMENT]
    target_ids = set(DECISIONS) | KEEP_TRUE
    require(len(segment_statements) == 27, "segment statement count changed")
    require({row["statement_id"] for row in segment_statements} == target_ids, "segment statement set changed")
    require(
        {row["statement_id"] for row in segment_statements if (row.get("qualifiers") or {}).get("relation_candidate") is True} == KEEP_TRUE,
        "preclassified relation statements changed",
    )
    require(
        all((by_id[sid].get("qualifiers") or {}).get("relation_candidate") is None for sid in DECISIONS),
        "one or more target statements already has a decision",
    )
    for sid in target_ids:
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        first, last = q.get("source_line_start"), q.get("source_line_end")
        require(isinstance(first, int) and isinstance(last, int), f"source line anchor missing: {sid}")
        source_span = "\n".join(source_lines[first - 1 : last])
        require(normalized(row.get("original_quote", "")) in normalized(source_span), f"quote/source mismatch: {sid}")

    candidates, candidate_fields, raw_candidates = read_csv(CANDIDATES)
    mentions, mention_fields, raw_mentions = read_csv(MENTIONS)
    require(len(candidates) == 11581 and len(mentions) == 27522, "candidate or mention row count changed")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    require(max(int(row["candidate_id"].split("-")[1]) for row in candidates) == 11603, "candidate ID cursor changed")
    segment_mentions = [row for row in mentions if row["segment_id"] == SEGMENT]
    require(max(int(row["mention_id"].rsplit("-", 1)[1]) for row in segment_mentions) == 58, "mention ID cursor changed")
    require(not (set(NEW_CANDIDATES) & candidate_by_id.keys()), "a planned candidate ID already exists")
    require(not (set(NEW_MENTIONS) & mention_by_id.keys()), "a planned mention ID already exists")
    require(not (NEW_STATEMENT_IDS & by_id.keys()), "a planned statement ID already exists")
    require(
        not any(row["canonical_name"] in set(NEW_CANDIDATES.values()) for row in candidates),
        "a planned source-specific candidate already exists",
    )

    cov_rows, _, _ = read_csv(COVERAGE)
    cov = next((row for row in cov_rows if row["segment_id"] == SEGMENT), None)
    require(
        cov is not None
        and cov["disposition"] == "reviewed"
        and cov["migration_status"] == "complete"
        and cov["source_line_ranges"] == "L49-56",
        "coverage disposition or source range changed",
    )

    candidate_additions = [
        {
            "candidate_id": "cand-11604",
            "index_entry_id": "",
            "canonical_name": "Unnamed followers acquired by Miguel de Molinos",
            "index_page_range": "",
            "suggested_type": "",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell says Molinos rapidly acquired a wide and influential following by preaching two appealing doctrines. Members, size, organization, and boundaries are unspecified; do not identify the followers with a particular religious order or the Jesuits.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT}#L54",
        },
        {
            "candidate_id": "cand-11605",
            "index_entry_id": "",
            "canonical_name": "Virtuosi who commented on the newly painted Gesù dome in 1675",
            "index_page_range": "",
            "suggested_type": "",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "The quoted 1675 avviso says many virtuosi did not highly praise Bernini's invention or Baccici's work. Their names, membership, and any institutional affiliation are not supplied; do not identify them with Congregazione dei Virtuosi.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT}#L56",
        },
        {
            "candidate_id": "cand-11606",
            "index_entry_id": "",
            "canonical_name": "Newly painted decoration of the Gesù dome reported in the 1675 avviso",
            "index_page_range": "",
            "suggested_type": "work",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Source-bounded painted decoration of the Gesù dome, distinct from the architectural space cand-5218 and the broader Gesù fresco group cand-5244. The 1675 avviso quoted by Haskell attributes its design to Bernini and execution to 'Baccici Fiorentino [sic]'; neither attribution is independently verified here.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT}#L56",
        },
    ]
    candidates.extend(candidate_additions)
    for mention_id, (candidate_id, surface) in NEW_MENTIONS.items():
        require(segment_text.count(surface) == 1, f"planned mention surface is missing or repeated: {mention_id}")
        start = segment_text.index(surface)
        mentions.append({
            "mention_id": mention_id,
            "segment_id": SEGMENT,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(start + len(surface)),
            "note": {
                "cand-11604": "The unnamed following acquired by Molinos; membership and organization are not supplied.",
                "cand-11605": "The unnamed group of virtuosi referred to by the 1675 avviso; not the named Congregazione dei Virtuosi.",
                "cand-11606": "The newly painted surface/work of the Gesù dome, nested with the separate architectural dome mention.",
            }[candidate_id],
        })

    for sid, (is_relation, note) in DECISIONS.items():
        mark_relation(by_id[sid], is_relation, note)

    # Preserve the archive's report, while giving the artwork and its two attributed makers explicit endpoints.
    attribution = by_id["st-chp3-seciv-l48-56-avviso-attribution"]
    attribution["object_candidate_id"] = "cand-11606"
    attribution["predicate"] = "reported_dome_painting_design_and_execution_attribution"
    attribution_q = dict(attribution["qualifiers"])
    attribution_q.update({
        "claim": "The unidentified 1675 avviso reports that the newly painted Gesù dome had a design by Bernini and execution by 'Baccici Fiorentino [sic]'.",
        "work_candidate_id": "cand-11606",
        "designer_candidate_id": "cand-0295",
        "artist_candidate_id": "cand-1117",
        "relation_candidate_note": DECISIONS[attribution["statement_id"]][1],
    })
    attribution["qualifiers"] = attribution_q

    unveiling = by_id["st-chp3-seciv-l48-56-avviso-dome-unveiling"]
    unveiling_q = dict(unveiling["qualifiers"])
    unveiling_q.update({
        "reported_actor_candidate_id": "cand-3403",
        "reported_work_candidate_id": "cand-11606",
        "relation_candidate_note": DECISIONS[unveiling["statement_id"]][1],
    })
    unveiling["qualifiers"] = unveiling_q

    bernini_role = by_id["st-chp3-seciv-l48-56-bernini-role-accepted"]
    bernini_q = dict(bernini_role["qualifiers"])
    bernini_q["relation_candidate_note"] = DECISIONS[bernini_role["statement_id"]][1]
    bernini_role["qualifiers"] = bernini_q

    caution = by_id["st-chp3-seciv-l48-56-controversy-motives-caution"]
    caution["subject_candidate_id"] = None
    caution["object_candidate_id"] = None
    caution["predicate"] = "author_caution_on_motive_attribution_in_controversies"
    caution_q = dict(caution["qualifiers"])
    caution_q["context_candidate_id"] = "cand-5253"
    caution_q["relation_candidate_note"] = DECISIONS[caution["statement_id"]][1]
    caution["qualifiers"] = caution_q

    daily = by_id["st-chp3-seciv-l48-56-daily-communion-doctrine"]
    daily_q = dict(daily["qualifiers"])
    daily_q["relation_candidate_note"] = DECISIONS[daily["statement_id"]][1]
    daily["qualifiers"] = daily_q

    enggass = by_id["st-chp3-seciv-l48-56-enggass-citation"]
    enggass["object_candidate_id"] = "cand-11606"
    enggass["predicate"] = "cited_for_modern_attribution_study_of"
    enggass_q = dict(enggass["qualifiers"])
    enggass_q.update({
        "claim": "Haskell directs readers to Enggass (1957), pages 303-305, for a modern examination of the Gesù dome-attribution problem.",
        "work_candidate_id": "cand-11606",
        "print_correction": {"ocr": "modem", "printed": "modern", "source": "CHP-3.pdf, printed p.81"},
        "relation_candidate_note": DECISIONS[enggass["statement_id"]][1],
    })
    enggass["qualifiers"] = enggass_q

    shares = by_id["st-chp3-seciv-l48-56-fresco-shares-unknown"]
    shares_q = dict(shares["qualifiers"])
    shares_q["relation_candidate_note"] = DECISIONS[shares["statement_id"]][1]
    shares["qualifiers"] = shares_q

    proposed = by_id["st-chp3-seciv-l48-56-gaulli-proposed-for-tribune"]
    proposed_q = dict(proposed["qualifiers"])
    proposed_q["relation_candidate_note"] = DECISIONS[proposed["statement_id"]][1]
    proposed["qualifiers"] = proposed_q

    opposition = by_id["st-chp3-seciv-l48-56-jesuit-opposition"]
    opposition["predicate"] = "reacted_strongly_to_doctrinal_dispute"
    opposition["original_quote"] = "who soon reacted strongly with all the intellectual and political weapons , at their command"
    opposition_q = dict(opposition["qualifiers"])
    opposition_q.update({
        "claim": "Haskell says the Jesuits soon reacted strongly to the doctrinal dispute, using intellectual and political means.",
        "related_doctrine_candidate_ids": ["cand-5248", "cand-5249"],
        "relation_candidate_note": DECISIONS[opposition["statement_id"]][1],
    })
    opposition["qualifiers"] = opposition_q

    implicated = by_id["st-chp3-seciv-l48-56-jesuits-and-oliva-implicated"]
    implicated["predicate"] = "centrally_implicated_in"
    implicated_q = dict(implicated["qualifiers"])
    implicated_q.pop("person_candidate_id", None)
    implicated_q.update({
        "co_implicated_person_candidate_id": "cand-1771",
        "related_statement_ids": ["st-chp3-seciv-l48-56-oliva-implicated"],
        "relation_candidate_note": DECISIONS[implicated["statement_id"]][1],
    })
    implicated["qualifiers"] = implicated_q

    left_transept = by_id["st-chp3-seciv-l48-56-left-transept-1685"]
    left_q = dict(left_transept["qualifiers"])
    left_q["relation_candidate_note"] = DECISIONS[left_transept["statement_id"]][1]
    left_transept["qualifiers"] = left_q

    letter = by_id["st-chp3-seciv-l48-56-letter-foundation-claim"]
    letter["subject_candidate_id"] = "cand-5238"
    letter["object_candidate_id"] = "cand-5200"
    letter["predicate"] = "describes_church_foundation_and_tribune"
    letter_q = dict(letter["qualifiers"])
    letter_q.update({
        "claim": "Oliva's September 1679 letter describes the Gesù's claimed foundation, the unfinished tribune, and appeals for the Duke's support.",
        "author_candidate_id": "cand-1771",
        "recipient_candidate_id": "cand-0997",
        "relation_candidate_note": DECISIONS[letter["statement_id"]][1],
    })
    letter["qualifiers"] = letter_q

    arrival = by_id["st-chp3-seciv-l48-56-molinos-arrived-1664"]
    arrival["subject_candidate_id"] = "cand-5253"
    arrival["object_candidate_id"] = "cand-5250"
    arrival["predicate"] = "began_soon_after"
    arrival_q = dict(arrival["qualifiers"])
    arrival_q.update({
        "claim": "Haskell says the Molinos controversy began soon after Miguel de Molinos's arrival in 1664.",
        "person_candidate_id": "cand-1680",
        "event_year": 1664,
        "qualification": "The destination of Molinos's arrival is not stated in this passage.",
        "relation_candidate_note": DECISIONS[arrival["statement_id"]][1],
    })
    arrival["qualifiers"] = arrival_q

    following = by_id["st-chp3-seciv-l48-56-molinos-gained-following"]
    following["object_candidate_id"] = "cand-11604"
    following["predicate"] = "acquired_influential_following"
    following_q = dict(following["qualifiers"])
    following_q.update({
        "group_membership": "unspecified",
        "relation_candidate_note": DECISIONS[following["statement_id"]][1],
    })
    following["qualifiers"] = following_q

    prestige = by_id["st-chp3-seciv-l48-56-molinos-prestige-clause"]
    prestige["predicate"] = "could_not_view_growth_of_prestige_with_enthusiasm"
    prestige_q = dict(prestige["qualifiers"])
    prestige_q["relation_candidate_note"] = DECISIONS[prestige["statement_id"]][1]
    prestige["qualifiers"] = prestige_q

    no_programme = by_id["st-chp3-seciv-l48-56-no-programme-found"]
    no_programme_q = dict(no_programme["qualifiers"])
    no_programme_q["relation_candidate_note"] = DECISIONS[no_programme["statement_id"]][1]
    no_programme["qualifiers"] = no_programme_q

    oliva_share = by_id["st-chp3-seciv-l48-56-oliva-share-inferred"]
    oliva_q = dict(oliva_share["qualifiers"])
    oliva_q["relation_candidate_note"] = DECISIONS[oliva_share["statement_id"]][1]
    oliva_share["qualifiers"] = oliva_q

    oral = by_id["st-chp3-seciv-l48-56-oral-arrangements-probable"]
    oral_q = dict(oral["qualifiers"])
    oral_q["claim"] = "Haskell considers it probable that arrangements among Oliva, Bernini, and Gaulli for the Gesù frescoes were made more orally than in writing."
    oral_q["relation_candidate_note"] = DECISIONS[oral["statement_id"]][1]
    oral["qualifiers"] = oral_q

    passive = by_id["st-chp3-seciv-l48-56-passive-contemplation-doctrine"]
    passive_q = dict(passive["qualifiers"])
    passive_q["relation_candidate_note"] = DECISIONS[passive["statement_id"]][1]
    passive["qualifiers"] = passive_q

    ranuccio = by_id["st-chp3-seciv-l48-56-ranuccio-offer"]
    ranuccio["predicate"] = "agreed_to_employ_artist_for_task"
    ranuccio["original_quote"] = "He agreed to the employment of Gaulli"
    ranuccio_q = dict(ranuccio["qualifiers"])
    ranuccio_q.update({
        "claim": "Ranuccio agreed to employ Gaulli for the proposed tribune task.",
        "qualification": "Agreement to employ is reported; the proposed decoration was not carried out as offered.",
        "relation_candidate_note": DECISIONS[ranuccio["statement_id"]][1],
    })
    for key in ("amount_offered_scudi", "stated_fraction_of_requested_amount", "payment_status"):
        ranuccio_q.pop(key, None)
    ranuccio["qualifiers"] = ranuccio_q

    roman = by_id["st-chp3-seciv-l48-56-roman-church-controversy"]
    roman_q = dict(roman["qualifiers"])
    roman_q.update({
        "qualification": "Footnote 2 is recorded at L200-L201 and linked to this statement; its cited works are bibliographic pointers and do not independently verify the controversy claim.",
        "relation_candidate_note": DECISIONS[roman["statement_id"]][1],
    })
    roman["qualifiers"] = roman_q

    small_vault = by_id["st-chp3-seciv-l48-56-small-vault-area-painted"]
    small_q = dict(small_vault["qualifiers"])
    small_q["relation_candidate_note"] = DECISIONS[small_vault["statement_id"]][1]
    small_vault["qualifiers"] = small_q

    bare = by_id["st-chp3-seciv-l48-56-tribune-and-high-altar-bare"]
    bare["object_candidate_id"] = None
    bare["predicate"] = "remained_bare_after_offer"
    bare_q = dict(bare["qualifiers"])
    bare_q.update({
        "claim": "After the proposed payment, the tribune remained bare.",
        "related_statement_ids": ["st-chp3-seciv-l48-56-high-altar-remained-bare"],
        "relation_candidate_note": DECISIONS[bare["statement_id"]][1],
    })
    bare["qualifiers"] = bare_q

    critical = by_id["st-chp3-seciv-l48-56-virtuosi-critical"]
    critical["subject_candidate_id"] = "cand-11606"
    critical["object_candidate_id"] = "cand-11605"
    critical["predicate"] = "not_highly_praised_by"
    critical_q = dict(critical["qualifiers"])
    critical_q.update({
        "claim": "The avviso reports that many unnamed virtuosi did not highly praise the dome painting's invention and workmanship, respectively associated with Bernini and Gaulli.",
        "reporting_source_candidate_id": "cand-5241",
        "designer_candidate_id": "cand-0295",
        "execution_artist_candidate_id": "cand-1117",
        "work_candidate_id": "cand-11606",
        "qualification": "The Italian phrase means the design and work were not highly praised; it does not establish universal rejection or identify the critics.",
        "relation_candidate_note": DECISIONS[critical["statement_id"]][1],
    })
    critical["qualifiers"] = critical_q

    xavier = by_id["st-chp3-seciv-l48-56-xavier-chapel-other-artist"]
    xavier_q = dict(xavier["qualifiers"])
    xavier_q["relation_candidate_note"] = DECISIONS[xavier["statement_id"]][1]
    xavier["qualifiers"] = xavier_q

    additions = [
        new_statement(
            "st-chp3-seciv-l48-56-bernini-designed-dome-painting",
            "cand-0295",
            "designed",
            "cand-11606",
            "con disegno del Cavalier Bernini",
            56,
            56,
            "The unidentified 1675 avviso attributes the design of the newly painted Gesù dome to Bernini.",
            {"source_candidate_id": "cand-5241", "designer_role": "design", "qualification": "Reported by the unidentified avviso quoted by Haskell; not independently verified."},
            True,
            "The contemporary report explicitly credits Bernini with the design; retain the source attribution rather than treating it as independently established.",
        ),
        new_statement(
            "st-chp3-seciv-l48-56-gaulli-executed-dome-painting",
            "cand-1117",
            "executed",
            "cand-11606",
            "a fattura d’un tale Baccici Fiorentino [sic]",
            56,
            56,
            "The unidentified 1675 avviso attributes execution of the newly painted Gesù dome to 'Baccici Fiorentino [sic]', locally mapped by Haskell to Gaulli.",
            {"source_candidate_id": "cand-5241", "reported_name": "Baccici Fiorentino [sic]", "qualification": "The identification with Gaulli follows Haskell's local context; the avviso is not independently inspected."},
            True,
            "The avviso explicitly assigns the work to the printed name Baccici Fiorentino; preserve [sic] and the source-limited mapping to Gaulli.",
        ),
        new_statement(
            "st-chp3-seciv-l48-56-oliva-implicated",
            "cand-1771",
            "centrally_implicated_in",
            "cand-5253",
            "and, in particular, its General, Oliva",
            53,
            54,
            "Haskell identifies Oliva, as General of the Society of Jesus, as particularly centrally implicated in the controversy.",
            {"institution_candidate_id": "cand-3403", "role": "General of the Society of Jesus", "qualification": "Companion to the Society of Jesus statement; preserve Haskell's framing."},
            True,
            "The apposition explicitly singles out Oliva as the Society's General; record his involvement separately from the institutional endpoint.",
        ),
        new_statement(
            "st-chp3-seciv-l48-56-jesuits-opposed-daily-communion",
            "cand-5248",
            "was_directly_opposed_to_jesuit_positions",
            "cand-3403",
            "Both of these views—and particularly the latter—were directly opposed to those of the Jesuits",
            54,
            54,
            "Haskell says the view permitting daily Communion on request was directly opposed to Jesuit views.",
            {"referred_view_candidate_id": "cand-5248", "paired_view_candidate_id": "cand-5249", "qualification": "The source says both views were opposed, with particular emphasis on the second."},
            True,
            "The phrase 'both of these views' resolves to the two preceding Molinos doctrine candidates; this row records the daily-Communion view.",
        ),
        new_statement(
            "st-chp3-seciv-l48-56-jesuits-opposed-passive-contemplation",
            "cand-5249",
            "was_directly_opposed_to_jesuit_positions",
            "cand-3403",
            "Both of these views—and particularly the latter—were directly opposed to those of the Jesuits",
            54,
            54,
            "Haskell says Molinos's preference for passive contemplation over active meditation was particularly opposed to Jesuit views.",
            {"referred_view_candidate_id": "cand-5249", "paired_view_candidate_id": "cand-5248", "qualification": "The source says both views were opposed, with particular emphasis on this second view."},
            True,
            "The phrase 'particularly the latter' identifies the passive-contemplation view; preserve Haskell's contrast and attribution.",
        ),
        new_statement(
            "st-chp3-seciv-l48-56-ranuccio-offered-payment",
            "cand-0997",
            "offered_payment_for_proposed_task",
            "cand-5240",
            "offered to pay 3000 scudi—exactly one-tenth of what had been asked for.",
            49,
            49,
            "Ranuccio offered 3000 scudi for Gaulli's proposed tribune task, described by Haskell as one-tenth of the amount requested.",
            {"artist_candidate_id": "cand-1117", "amount_offered_scudi": 3000, "stated_fraction_of_requested_amount": "one-tenth", "payment_status": "offered; payment is not established", "qualification": "Distinct from the 1672 commission and from payment actually made."},
            True,
            "The source reports an offer, not a completed payment; keep the amount and fraction attached to the proposed 1679 task.",
        ),
        new_statement(
            "st-chp3-seciv-l48-56-high-altar-remained-bare",
            "cand-4999",
            "remained_bare_after_offer",
            None,
            "the tribune and High Altar remained bare",
            49,
            49,
            "After the proposed payment, the High Altar remained bare.",
            {"context_candidate_id": "cand-5240", "qualification": "Scalar status split from the coordinated tribune-and-High-Altar clause."},
            False,
            "This is a status of the High Altar, not a relation between it and the tribune.",
        ),
    ]
    require({row["statement_id"] for row in additions} == NEW_STATEMENT_IDS, "new statement plan changed")
    for row in additions:
        require(normalized(row["original_quote"]) in normalized(segment_text), f"new quote is not in target segment: {row['statement_id']}")
    statements.extend(additions)
    by_id = {row["statement_id"]: row for row in statements}

    after_segment = [row for row in statements if row.get("segment_id") == SEGMENT]
    require(len(after_segment) == 34, "planned atomization did not produce 34 segment statements")
    require(
        sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in after_segment) == 29
        and sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in after_segment) == 5
        and all((row.get("qualifiers") or {}).get("relation_candidate") is not None for row in after_segment),
        "segment decisions do not close at 29 relation candidates and 5 nonrelations",
    )
    require(
        by_id["st-chp3-seciv-l48-56-molinos-gained-following"]["object_candidate_id"] == "cand-11604"
        and by_id["st-chp3-seciv-l48-56-virtuosi-critical"]["subject_candidate_id"] == "cand-11606"
        and by_id["st-chp3-seciv-l48-56-virtuosi-critical"]["object_candidate_id"] == "cand-11605",
        "new group and artwork endpoints are incomplete",
    )
    require(
        by_id["st-chp3-seciv-l48-56-letter-foundation-claim"]["subject_candidate_id"] == "cand-5238"
        and by_id["st-chp3-seciv-l48-56-letter-foundation-claim"]["object_candidate_id"] == "cand-5200"
        and by_id["st-chp3-seciv-l48-56-molinos-arrived-1664"]["subject_candidate_id"] == "cand-5253"
        and by_id["st-chp3-seciv-l48-56-molinos-arrived-1664"]["object_candidate_id"] == "cand-5250",
        "corrected document or event endpoints are inconsistent",
    )
    require(
        by_id["st-chp3-seciv-l48-56-tribune-and-high-altar-bare"]["object_candidate_id"] is None
        and by_id["st-chp3-seciv-l48-56-high-altar-remained-bare"]["object_candidate_id"] is None,
        "scalar architectural statuses retain a false cross-endpoint",
    )

    bilateral = [row for row in statements if row.get("subject_candidate_id") and row.get("object_candidate_id")]
    relation_total = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements)
    bilateral_relations = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in bilateral)
    bilateral_nonrelations = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in bilateral)
    bilateral_pending = sum((row.get("qualifiers") or {}).get("relation_candidate") is None for row in bilateral)
    open_relations = relation_total - bilateral_relations
    require(
        (len(statements), len(candidates), len(mentions), len(bilateral), relation_total, bilateral_relations, bilateral_nonrelations, bilateral_pending, open_relations)
        == (12787, 11584, 27525, 8580, 4985, 4933, 479, 3168, 52),
        "planned global counts do not match the reviewed decisions",
    )

    payloads = {
        TABLE: encode_jsonl(statements, raw_table),
        CANDIDATES: encode_csv(candidates, candidate_fields, raw_candidates),
        MENTIONS: encode_csv(mentions, mention_fields, raw_mentions),
    }
    print("APPLY" if args.apply else "DRY_RUN", "segment_statements=34 relation_candidates=29 nonrelations=5 unresolved=0")
    print("new_candidates=3 new_mentions=3 new_statements=7 scalarized_statuses=2 split_relations=3")
    print(
        f"all_statements={len(statements)} candidates={len(candidates)} mentions={len(mentions)} bilateral={len(bilateral)} "
        f"bilateral_relations={bilateral_relations} bilateral_nonrelations={bilateral_nonrelations} "
        f"bilateral_pending={bilateral_pending} total_relation_candidates={relation_total} open_endpoint_relations={open_relations}"
    )
    for mention_id, (candidate_id, surface) in NEW_MENTIONS.items():
        row = next(item for item in mentions if item["mention_id"] == mention_id)
        print(f"  {mention_id} -> {candidate_id} {surface!r} at {row['start_char']}:{row['end_char']}")
    print("source_print_correction=modem -> modern (printed p.81); S0 and original quote preserved")
    print("footnote_2=linked to processed L200-201; stale pending wording corrected")

    if not args.apply:
        return

    for path, backup in BACKUPS.items():
        shutil.copy2(path, backup)
    for path, payload in payloads.items():
        atomic_write(path, payload)

    written_statements = read_jsonl(TABLE)
    written_by_id = {row["statement_id"]: row for row in written_statements}
    written_candidates, _, _ = read_csv(CANDIDATES)
    written_mentions, _, _ = read_csv(MENTIONS)
    written_segment = [row for row in written_statements if row.get("segment_id") == SEGMENT]
    require(
        len(written_statements) == 12787 and len(written_candidates) == 11584 and len(written_mentions) == 27525,
        "postwrite table row count mismatch",
    )
    require(len(written_segment) == 34, "postwrite segment statement count mismatch")
    require(
        all((written_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is not None for sid in target_ids | NEW_STATEMENT_IDS),
        "postwrite segment has an unresolved relation decision",
    )
    for mention_id, (candidate_id, surface) in NEW_MENTIONS.items():
        row = next(item for item in written_mentions if item["mention_id"] == mention_id)
        begin, end = int(row["start_char"]), int(row["end_char"])
        require(row["candidate_id"] == candidate_id and segment_text[begin:end] == surface, f"postwrite mention mismatch: {mention_id}")
    require(all(digest(backup) == EXPECTED[path] for path, backup in BACKUPS.items()), "one or more recovery backup hashes mismatch")
    print("postwrite=passed")
    for path, backup in BACKUPS.items():
        print(f"backup={backup.relative_to(ROOT).as_posix()} sha256={digest(backup)}")
    for path in (TABLE, CANDIDATES, MENTIONS):
        print(f"sha256 {path.relative_to(ROOT).as_posix()}={digest(path)}")


if __name__ == "__main__":
    main()
