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
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_i.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-7.pdf"
SEGMENT = "chp-7:07_CHP-7_sec_i:l282-291"
STATEMENT_BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p192-l282-291-relation-classification-20261013"
CANDIDATE_BACKUP = TABLES / "entity-candidates.csv.bak-s2-chp7-seci-p192-brigandage-endpoints-20261013"
MENTION_BACKUP = TABLES / "mentions.csv.bak-s2-chp7-seci-p192-brigandage-endpoints-20261013"

EXPECTED_HASHES = {
    STATEMENTS: "86417cefc83062e219ed30ef5914546d677263eb1c02887c703bacc7d508cc40",
    CANDIDATES: "d1068cdce1b60058ccd34806fce30deaf490e665b6371e321f67d429d7f80684",
    MENTIONS: "aea589cf44c63f6aea7a8383417d02a5037ecfed2fa2ef0efb392fe0b7440c71",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
    PDF: "eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212",
}

NEW_CANDIDATES = (
    {
        "candidate_id": "cand-12003",
        "index_entry_id": "",
        "canonical_name": "Brigandage described in Haskell’s account of Naples",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "A social practice that Haskell says was openly encouraged; no individual acts or actors are enumerated.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L283",
    },
    {
        "candidate_id": "cand-12004",
        "index_entry_id": "",
        "canonical_name": "Unnamed aristocracy described as encouraging brigandage",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell calls the collective an irresponsible aristocracy; the passage names no members or formal institution.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L283",
    },
)

TRUE_NOTES = {
    "st-chp7-p192-i01": "This preserves Haskell's interpretive claim linking Del Carpio's contribution to Neapolitan culture with the reforms described on p.192; it is not an independent finding.",
    "st-chp7-p192-i03": "This records Haskell's explicit claim that an unnamed aristocratic collective encouraged brigandage; neither individuals nor a formal body are identified.",
    "st-chp7-p192-i06": "This records the reform effort attributed to Del Carpio's brief administration; the individual measures and full scope of the problems are not itemized.",
    "st-chp7-p192-i07": "This records hostility from some sections of the nobility in response to Del Carpio's effort; it does not generalize to all nobles.",
    "st-chp7-p192-i08": "This preserves Haskell's claim that Del Carpio's actions laid foundations for a future 'new civilisation'; the forecast is not treated as an achieved outcome here.",
    "st-chp7-p192-i09": "This records an attempt to persuade painters to serve the King in Madrid; it does not say they accepted or moved.",
    "st-chp7-p192-i10": "The sentence's unnamed 'considerable Italian artist' is identified as Giordano by the next sentence; the source's qualifier 'considerable' is retained.",
    "st-chp7-p192-i11": "This records Italian pictures reaching the Alcazar before the artist's 1692 journey; the paintings are not individually identified.",
    "st-chp7-p192-i12": "This records Giordano's 1692 voyage and nearly ten-year stay in Spain as reported by Haskell.",
    "st-chp7-p192-i13": "This records the King's welcome and vast salary as Haskell reports them; the monarch's identity and salary amount remain unknown.",
    "st-chp7-p192-i14": "This records Haskell's claim that Giordano introduced an unnamed painting type into the Spanish buildings he decorated; no formal style name is supplied.",
    "st-chp7-p192-i15": "This records the source's claim that the painting type drew on devices learned from Baroque masters; the stylistic adjectives remain Haskell's evaluation.",
    "st-chp7-p192-i18": "This preserves Haskell's qualified claim that Giordano's influence may have weakened some local painters; the modal wording and evaluation are retained.",
    "st-chp7-p192-i19": "This records Haskell's account that Giordano's influence was later absorbed by Goya; it does not imply direct contact.",
    "st-chp7-p192-i22": "This records Giordano's stated admiration for Venetian art, without naming a particular work or institution.",
    "st-chp7-p192-i23": "This records Giordano's encounter with the Titian collection in unnamed royal palaces; the collection has no formal name or type in the source.",
    "st-chp7-p192-i24": "This records Haskell's account of the Titian collection's impact on Giordano's Neapolitan manner; the causal interpretation remains attributed to Haskell.",
    "st-chp7-p192-i25": "This records the source's claim that Giordano copied Rubens; no particular Rubens work or direct contact is identified.",
    "st-chp7-p192-i26": "This records Giordano's sincere appreciation of Velasquez as the means by which he pleased his hosts; no collaboration is inferred.",
}

FALSE_NOTES = {
    "st-chp7-p192-i02": "This is Haskell's broad diagnosis of Neapolitan political and social conditions; Monterey is one example among multiple rulers, not a single relation endpoint.",
    "st-chp7-p192-i04": "This is a general statement about justice and lawyers, not a relation between identified entities.",
    "st-chp7-p192-i05": "This is a broad social assessment of inequality, not a discrete relation candidate between identified entities.",
    "st-chp7-p192-i16": "This is Haskell's evaluative ranking of Giordano's visit, not a relation between distinct entities.",
    "st-chp7-p192-i17": "This sentence combines Giordano's effect on Spaniards with their later employment of two named decorators; the source-level parent is retained and split into atomic relations below.",
    "st-chp7-p192-i20": "This states the personal significance of Giordano's Madrid years, not a relation between distinct entities.",
    "st-chp7-p192-i21": "This is a comparison of Giordano's disposition with Bernini's, not a relation between the two artists.",
    "st-chp7-p192-i27": "This is biographical chronology after Giordano's return to Italy, not a relation candidate.",
    "st-chp7-p192-i28": "This is Haskell's evaluative ranking of Giordano at age 70; no comparator or separate relation is identified.",
}

ENDPOINT_FIXES = {
    "st-chp7-p192-i02": {"object_candidate_id": ("cand-1693", None)},
    "st-chp7-p192-i03": {
        "subject_candidate_id": ("cand-1722", "cand-12004"),
        "object_candidate_id": ("cand-6979", "cand-12003"),
    },
    "st-chp7-p192-i11": {
        "subject_candidate_id": ("cand-5120", "cand-6982"),
        "object_candidate_id": ("cand-6982", "cand-6983"),
    },
    "st-chp7-p192-i17": {
        "subject_candidate_id": ("cand-1172", None),
        "object_candidate_id": ("cand-1165", None),
    },
}

NEW_CHILD_IDS = (
    "st-chp7-p192-i17-spaniards-dazzled",
    "st-chp7-p192-i17-giaquinto-employment",
    "st-chp7-p192-i17-tiepolo-employment",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def read_csv(path: Path, raw: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    if reader.fieldnames is None:
        raise ValueError(f"missing CSV header: {path}")
    return reader.fieldnames, list(reader)


def csv_bytes(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows({field: row.get(field, "") for field in fields} for row in rows)
    output = buffer.getvalue()
    if raw.startswith(b"\xef\xbb\xbf"):
        output = "\ufeff" + output
    return output.encode("utf-8")


def build_child(parent: dict, statement_id: str, subject: str, obj: str, predicate: str, claim: str, quote: str, mentioned: list[str], qualification: str, note: str) -> dict:
    q = dict(parent["qualifiers"])
    q.update(
        {
            "source_line_start": 289,
            "source_line_end": 289,
            "claim": claim,
            "speaker": "Haskell",
            "text_layer": "body",
            "qualification": qualification,
            "mentioned_candidate_ids": mentioned,
            "decomposed_from_statement_id": parent["statement_id"],
            "relation_candidate": True,
            "relation_candidate_note": note,
        }
    )
    return {
        "statement_id": statement_id,
        "segment_id": parent["segment_id"],
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": q,
        "original_quote": quote,
        "origin": parent["origin"],
        "source_file": parent["source_file"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.192 S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification and endpoint corrections")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    required = [
        (282, "[Page 192]"),
        (283, "The misgovernment of rulers such as Monterey"),
        (283, "Brigandage was openly encouraged by an irresponsible aristocracy."),
        (283, "The inequalities between rich and poor"),
        (283, "Del Carpio’s brief administration made the first serious attempt"),
        (285, "When still in Rome Del Carpio had tried to persuade various painters"),
        (287, "It-was not, however, until 1692"),
        (288, "although quantities of Italian pictures were reaching the Alcazar"),
        (289, "Luca Giordano’s brilliance rightly dazzled the Spaniards"),
        (289, "led eventually to their employment of such master decorators as Corrado Giaquinto and Tiepolo"),
        (290, "under their impact he dropped most of the remaining vestiges"),
        (291, "‘advanced’ painter of his day"),
    ]
    if any(text not in source_lines[line_no - 1] for line_no, text in required):
        raise SystemExit("p.192 source line guards failed")

    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    page_ids = {f"st-chp7-p192-i{i:02}" for i in range(1, 29)}
    page_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    if {row["statement_id"] for row in page_rows} != page_ids or len(page_rows) != 28:
        raise SystemExit("p.192 statement set changed")
    if any((row.get("qualifiers") or {}).get("relation_candidate") is not None for row in page_rows):
        raise SystemExit("p.192 statements are no longer all unset")
    if any(sid in by_id for sid in NEW_CHILD_IDS):
        raise SystemExit("a decomposed p.192 statement ID already exists")

    candidate_fields, candidate_rows = read_csv(CANDIDATES, raw[CANDIDATES])
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    if any(row["candidate_id"] in candidates for row in NEW_CANDIDATES):
        raise SystemExit("a new p.192 candidate ID already exists")
    last_number = max(int(row["candidate_id"].removeprefix("cand-")) for row in candidate_rows)
    if [row["candidate_id"] for row in NEW_CANDIDATES] != [f"cand-{last_number + i:04d}" for i in (1, 2)]:
        raise SystemExit("p.192 candidate IDs are no longer sequential")
    required_candidates = {
        "cand-1693": "person", "cand-1722": "place", "cand-0571": "person", "cand-0573": "person",
        "cand-6977": "person", "cand-6978": "term", "cand-6979": "term", "cand-6980": "term",
        "cand-6981": "term", "cand-6982": "work", "cand-6983": "place", "cand-6984": "event",
        "cand-6985": "place", "cand-6986": "term", "cand-6987": "term", "cand-6988": "term",
        "cand-6989": "term", "cand-6990": "place", "cand-6992": "term", "cand-6993": "term",
        "cand-1172": "person", "cand-1165": "person", "cand-2569": "person", "cand-1216": "person",
        "cand-2293": "person", "cand-2709": "person",
    }
    for cid, expected_type in required_candidates.items():
        if cid not in candidates or candidates[cid]["suggested_type"] != expected_type:
            raise SystemExit(f"candidate type guard failed for {cid}")

    mention_fields, mention_rows = read_csv(MENTIONS, raw[MENTIONS])
    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    if len(mention_by_id) != len(mention_rows):
        raise SystemExit("duplicate mention IDs")
    page_mentions = [row for row in mention_rows if row["segment_id"] == SEGMENT]
    if len(page_mentions) != 53:
        raise SystemExit(f"unexpected p.192 mention count: {len(page_mentions)}")
    segment_text = "\n".join(source_lines[281:291])
    for mention in page_mentions:
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if segment_text[start:end] != mention["surface_form"]:
            raise SystemExit(f"p.192 mention span mismatch: {mention['mention_id']}")
    new_mention_specs = [
        ("m-chp7-p192-052", "cand-12003", "Brigandage", "Haskell's term for the social practice; the source names no specific acts."),
        ("m-chp7-p192-053", "cand-12004", "irresponsible aristocracy", "Unnamed collective described by Haskell; no individual members or formal body are identified."),
    ]
    for mention_id, candidate_id, surface, note in new_mention_specs:
        if mention_id in mention_by_id:
            raise SystemExit(f"new mention ID already exists: {mention_id}")
        start = segment_text.find(surface)
        if start < 0:
            raise SystemExit(f"new mention surface missing from p.192 source: {surface}")
        mention_rows.append({
            "mention_id": mention_id,
            "segment_id": SEGMENT,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(start + len(surface)),
            "note": note,
        })

    for sid, endpoints in ENDPOINT_FIXES.items():
        row = by_id[sid]
        for field, (old_value, new_value) in endpoints.items():
            if row.get(field) != old_value:
                raise SystemExit(f"endpoint changed for {sid}.{field}: expected {old_value!r}, got {row.get(field)!r}")
            if new_value and new_value not in candidates and new_value not in {item["candidate_id"] for item in NEW_CANDIDATES}:
                raise SystemExit(f"endpoint candidate missing for {sid}.{field}: {new_value}")
            row[field] = new_value

    for sid, note in {**TRUE_NOTES, **FALSE_NOTES}.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = sid in TRUE_NOTES
        q["relation_candidate_note"] = note

    by_id["st-chp7-p192-i03"]["predicate"] = "encouraged"
    by_id["st-chp7-p192-i03"]["qualifiers"]["claim"] = "Haskell says an unnamed aristocracy openly encouraged brigandage."
    by_id["st-chp7-p192-i03"]["qualifiers"]["qualification"] = "The source calls the collective an irresponsible aristocracy and names no members or formal institution."
    by_id["st-chp7-p192-i03"]["qualifiers"]["mentioned_candidate_ids"] = ["cand-12004", "cand-12003"]
    by_id["st-chp7-p192-i06"]["predicate"] = "undertook_reforms_to_address_governance_evils"
    by_id["st-chp7-p192-i06"]["qualifiers"]["claim"] = "Haskell says Del Carpio’s brief administration made the first serious reform effort to address the evils described in the preceding sentences."
    by_id["st-chp7-p192-i06"]["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys([*(by_id["st-chp7-p192-i06"]["qualifiers"].get("mentioned_candidate_ids", [])), "cand-6980"]))
    by_id["st-chp7-p192-i11"]["qualifiers"]["relation_candidate_note"] = "This records the pictures arriving at the Alcazar; the table endpoints now identify the work group and receiving place, with Spain retained as context."
    by_id["st-chp7-p192-i15"]["predicate"] = "draws_on_devices_from"
    by_id["st-chp7-p192-i17"]["qualifiers"]["decomposed_into_statement_ids"] = list(NEW_CHILD_IDS)

    children = [
        build_child(
            by_id["st-chp7-p192-i17"], NEW_CHILD_IDS[0], "cand-1172", "cand-6989", "dazzled_spanish_audience",
            "Haskell says Luca Giordano’s brilliance dazzled the Spaniards.",
            "Luca Giordano’s brilliance rightly dazzled the Spaniards", ["cand-1172", "cand-6989"],
            "The audience is a collective described as Spaniards; no individual observers are identified.",
            "This is the first atomic claim in the passage: Giordano's brilliance affected the Spanish audience.",
        ),
        build_child(
            by_id["st-chp7-p192-i17"], NEW_CHILD_IDS[1], "cand-6989", "cand-1165", "employed",
            "Haskell says the Spaniards later employed Corrado Giaquinto, linking this development to Giordano’s brilliance.",
            "led eventually to their employment of such master decorators as Corrado Giaquinto", ["cand-1172", "cand-6989", "cand-1165"],
            "The source does not identify a specific Spanish patron or institution that hired the artist.",
            "This preserves Haskell's causal account while recording the named decorator as the employment target.",
        ),
        build_child(
            by_id["st-chp7-p192-i17"], NEW_CHILD_IDS[2], "cand-6989", "cand-2569", "employed",
            "Haskell says the Spaniards later employed Tiepolo, linking this development to Giordano’s brilliance.",
            "led eventually to their employment of such master decorators as Corrado Giaquinto and Tiepolo", ["cand-1172", "cand-6989", "cand-2569"],
            "The source does not identify a specific Spanish patron or institution that hired the artist.",
            "This preserves Haskell's causal account while separating Tiepolo from the other named decorator.",
        ),
    ]
    quote_block = source_lines[288]
    if any(child["original_quote"] not in quote_block for child in children):
        raise SystemExit("decomposed p.192 quote does not match source L289")
    all_candidate_ids = set(candidates) | {row["candidate_id"] for row in NEW_CANDIDATES}
    for child in children:
        for cid in [child["subject_candidate_id"], child["object_candidate_id"], *child["qualifiers"]["mentioned_candidate_ids"]]:
            if cid not in all_candidate_ids:
                raise SystemExit(f"decomposed statement references missing candidate: {child['statement_id']} {cid}")

    result_statements = []
    for row in statements:
        result_statements.append(row)
        if row["statement_id"] == "st-chp7-p192-i17":
            result_statements.extend(children)
    result_candidates = candidate_rows + list(NEW_CANDIDATES)
    statement_bytes = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in result_statements) + "\n").encode("utf-8")
    candidate_bytes = csv_bytes(raw[CANDIDATES], candidate_fields, result_candidates)
    mention_bytes = csv_bytes(raw[MENTIONS], mention_fields, mention_rows)

    print(json.dumps({
        "mode": "apply" if args.apply else "dry_run",
        "segment": SEGMENT,
        "classified_unset": 28,
        "true_original": len(TRUE_NOTES),
        "false_original": len(FALSE_NOTES),
        "decomposed_true_children": len(children),
        "segment_total_after": {"true": len(TRUE_NOTES) + len(children), "false": len(FALSE_NOTES), "unset": 0, "statements": len(page_rows) + len(children)},
        "new_candidates": [row["candidate_id"] for row in NEW_CANDIDATES],
        "new_mentions": [mention_id for mention_id, *_ in new_mention_specs],
        "new_statements": list(NEW_CHILD_IDS),
        "endpoint_fixes": ENDPOINT_FIXES,
        "before_sha256": {path.name: digest(data) for path, data in raw.items()},
        "after_sha256": {STATEMENTS.name: digest(statement_bytes), CANDIDATES.name: digest(candidate_bytes), MENTIONS.name: digest(mention_bytes)},
    }, ensure_ascii=True, indent=2))

    if not args.apply:
        return
    backups = ((STATEMENTS, STATEMENT_BACKUP), (CANDIDATES, CANDIDATE_BACKUP), (MENTIONS, MENTION_BACKUP))
    if any(backup.exists() for _, backup in backups):
        raise SystemExit("a p.192 recovery backup already exists; refusing to overwrite")
    for original, backup in backups:
        shutil.copy2(original, backup)
    outputs = {STATEMENTS: statement_bytes, CANDIDATES: candidate_bytes, MENTIONS: mention_bytes}
    written: list[Path] = []
    try:
        for path, data in outputs.items():
            atomic_write(path, data)
            written.append(path)
    except Exception:
        for original, backup in backups:
            if original in written:
                shutil.copy2(backup, original)
        raise
    print("APPLIED; recovery copies:", ", ".join(str(backup.relative_to(ROOT)) for _, backup in backups))


if __name__ == "__main__":
    main()
