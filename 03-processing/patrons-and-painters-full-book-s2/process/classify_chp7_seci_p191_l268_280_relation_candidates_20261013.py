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
SEGMENT = "chp-7:07_CHP-7_sec_i:l268-280"
STATEMENT_BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p191-l268-280-relation-classification-20261013"
CANDIDATE_BACKUP = TABLES / "entity-candidates.csv.bak-s2-chp7-seci-p191-small-fountain-endpoint-20261013"
MENTION_BACKUP = TABLES / "mentions.csv.bak-s2-chp7-seci-p191-small-fountain-endpoint-20261013"

EXPECTED_HASHES = {
    STATEMENTS: "2f6b88ea002bddb1b547a2236bab9653b4825e0d5b15f1583790f20b18f22577",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    MENTIONS: "0f16fdd7787638da331f0e716051d62964a7fb17b126d8891a0b76e0a6bdf52b",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
    PDF: "eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212",
}

NEW_CANDIDATE_ID = "cand-12002"
NEW_CHILD_IDS = (
    "st-chp7-p191-i28-naples-lost-father",
    "st-chp7-p191-i28-artists-lost-support",
)

TRUE_NOTES = {
    "st-chp7-p191-i01": "This preserves an aesthetic affinity between Del Carpio's and Massimi's tastes; the passage does not establish personal contact, friendship, or collaboration.",
    "st-chp7-p191-i02": "This records Del Carpio's collection of thirty drawing volumes; the source-defined collection remains untyped.",
    "st-chp7-p191-i03": "This records Del Carpio's stated artistic preference for Carlo Maratta; it does not imply a commission.",
    "st-chp7-p191-i04": "This records Haskell's statement of Del Carpio's admiration for Bernini; admiration is not treated as collaboration or employment.",
    "st-chp7-p191-i06": "This records ownership and valuation of the small version as a distinct work; Piazza Navona locates the original fountain, not the owned version.",
    "st-chp7-p191-i07": "The acquired drawing is the subject, Domenico is the named source, and Del Carpio is the acquirer; no title or date is supplied.",
    "st-chp7-p191-i08": "The page explicitly identifies Domenico as Gian Lorenzo Bernini's son.",
    "st-chp7-p191-i09": "This preserves the offer as a rumour reported by Haskell; it does not assert a completed purchase or independently confirmed offer.",
    "st-chp7-p191-i10": "This records Haskell's statement that the reported offer was not accepted; the recipient is not identified.",
    "st-chp7-p191-i11": "This records Haskell's claim that period documents register Del Carpio's interest in contemporary Roman painting; the claimed document coverage has not been independently examined.",
    "st-chp7-p191-i12": "This records repeated visits to the named painters' studios as stated by Haskell; it does not infer additional meetings or commissions.",
    "st-chp7-p191-i13": "This records Berrettoni's pupil relationship to Maratta as stated in the source; final identity alignment remains S3.",
    "st-chp7-p191-i14": "This records Ghezzi's later office as permanent secretary at the Accademia di S. Luca; the date is not stated.",
    "st-chp7-p191-i16": "This records Del Carpio's move to Naples at the end of 1682, with the date and place as stated.",
    "st-chp7-p191-i17": "This is the reported relation of the unnamed painters to Del Carpio as a great lover and protector; the quoted source is unidentified.",
    "st-chp7-p191-i19": "This records Del Carpio's role in launching Paolo de Matteis's career; no particular commission or later work is inferred.",
    "st-chp7-p191-i20": "This records continued patronage in Naples; no specific artist or work is supplied in this sentence.",
    "st-chp7-p191-i21": "This records the reported growth of Del Carpio's painting collection from 1,100 to 1,800; the count is Haskell's claim and is not independently verified.",
    "st-chp7-p191-i22": "This records Pinacci's responsibility for Del Carpio's painting collection; the passage calls him an expert restorer but does not say he restored works in this collection.",
    "st-chp7-p191-i24": "This records that Del Carpio had met Giordano in Rome; the date and circumstances are not supplied.",
    "st-chp7-p191-i25": "This records Giordano's succession to Maratta as Del Carpio's chief painter; the exact appointment date is not stated.",
    "st-chp7-p191-i26": "This records Giordano decorating churches and the palace for Del Carpio; the individual churches and commissions are unidentified.",
    "st-chp7-p191-i30": "This records Haskell's report of shipments from Naples to descendants' collections in Madrid; the manuscript cited in note 11 has not been independently consulted.",
    "st-chp7-p191-i32": "This preserves Haskell's interpretive claim about Del Carpio's contribution to Neapolitan culture; the sentence continues on p.192 L283 and is not an independent finding.",
}

FALSE_NOTES = {
    "st-chp7-p191-i05": "This establishes temporal overlap between Bernini's death and Del Carpio's term of office, not a relationship between the two people.",
    "st-chp7-p191-i15": "This is an occupational description of Grimaldi, not a relation between distinct entities.",
    "st-chp7-p191-i18": "This is Haskell's broad negative comparison about unnamed Italian artists, not a relation between identified entities.",
    "st-chp7-p191-i23": "This is Haskell's evaluative description of the palace's effect on unspecified visitors; Naples is contextual location, not the second relation endpoint.",
    "st-chp7-p191-i27": "This is a biographical death statement with a year and office context, not a relation between distinct entities.",
    "st-chp7-p191-i28": "This quoted judgement combines two distinct relations, split into the Naples and artists claims below; the source of the judgement remains unnamed.",
    "st-chp7-p191-i29": "This is Haskell's endorsement of the two reported judgements, not an additional entity-to-entity relation.",
    "st-chp7-p191-i31": "This is a broad comparative assessment of Naples's condition, not a relation between identified entities.",
}

ENDPOINT_FIXES = {
    "st-chp7-p191-i06": {
        "object_candidate_id": ("cand-0318", NEW_CANDIDATE_ID),
    },
    "st-chp7-p191-i07": {
        "subject_candidate_id": ("cand-0573", "cand-6958"),
        "object_candidate_id": ("cand-6958", "cand-0294"),
    },
    "st-chp7-p191-i23": {
        "object_candidate_id": ("cand-1722", None),
    },
    "st-chp7-p191-i25": {
        "object_candidate_id": ("cand-0571", "cand-1526"),
    },
    "st-chp7-p191-i26": {
        "object_candidate_id": ("cand-6967", "cand-0571"),
    },
    "st-chp7-p191-i28": {
        "subject_candidate_id": ("cand-1722", None),
        "object_candidate_id": ("cand-6962", None),
    },
    "st-chp7-p191-i29": {
        "subject_candidate_id": ("cand-1722", None),
        "object_candidate_id": ("cand-6962", None),
    },
}

MENTION_FIXES = {
    "m-chp7-p191-014": ("cand-0318", NEW_CANDIDATE_ID),
    "m-chp7-p191-016": ("cand-0318", NEW_CANDIDATE_ID),
}


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


def csv_bytes(path: Path, raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows({field: row.get(field, "") for field in fields} for row in rows)
    text = buffer.getvalue()
    if raw.startswith(b"\xef\xbb\xbf"):
        text = "\ufeff" + text
    return text.encode("utf-8")


def build_child(parent: dict, statement_id: str, subject: str, quote: str, predicate: str, claim: str, mentioned: list[str], note: str) -> dict:
    q = dict(parent["qualifiers"])
    q.update(
        {
            "claim": claim,
            "qualification": "The speaker is not identified; Haskell reports this as a judgement made at Del Carpio's death.",
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
        "object_candidate_id": "cand-0571",
        "predicate": predicate,
        "qualifiers": q,
        "original_quote": quote,
        "origin": parent["origin"],
        "source_file": parent["source_file"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.191 S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification and endpoint corrections")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    required = {
        268: "[Page 191]",
        269: "felt an affinity between Massimi’s classical taste and his own",
        270: "He owned a small version of the Fountain of the Four Rivers",
        271: "acquire one of his self-portrait drawings from his son",
        272: "this offer was not accepted",
        273: "there was no native Italian to show such discriminating enthusiasm",
        274: "increased his collection of paintings from 1100 to 1800/",
        275: "Luca Giordano, whom he had already met in Rome, replaced Carlo",
        276: "Maratta as his chief painter and decorated churches and the palace for him.",
        277: "Naples had lost a loving father and her artists a great support",
        278: "For Del Carpio’s contribution to Neapolitan culture must be gauged",
    }
    if any(text not in source_lines[line_no - 1] for line_no, text in required.items()):
        raise SystemExit("p.191 source line guards failed")
    pdf = raw[PDF]
    if digest(pdf) != EXPECTED_HASHES[PDF]:
        raise SystemExit("p.191 print source hash changed")

    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    page_ids = {f"st-chp7-p191-i{i:02}" for i in range(1, 33)}
    page_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    if {row["statement_id"] for row in page_rows} != page_ids or len(page_rows) != 32:
        raise SystemExit("p.191 statement set changed")
    prior_true = {"st-chp7-p191-i07", "st-chp7-p191-i13"}
    if {row["statement_id"] for row in page_rows if (row.get("qualifiers") or {}).get("relation_candidate") is True} != prior_true:
        raise SystemExit("the two previously classified p.191 rows changed")
    unset = {row["statement_id"] for row in page_rows if (row.get("qualifiers") or {}).get("relation_candidate") is None}
    expected_unset = (set(TRUE_NOTES) | set(FALSE_NOTES)) - prior_true
    if unset != expected_unset or len(unset) != 30:
        raise SystemExit(f"p.191 unset statement set changed: {sorted(unset ^ expected_unset)}")
    if any(sid in by_id for sid in NEW_CHILD_IDS):
        raise SystemExit("a decomposed p.191 statement ID already exists")

    candidate_fields, candidate_rows = read_csv(CANDIDATES, raw[CANDIDATES])
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    if NEW_CANDIDATE_ID in candidates:
        raise SystemExit(f"new candidate ID already exists: {NEW_CANDIDATE_ID}")
    expected_types = {"cand-0318": "person", "cand-6958": "work", "cand-0294": "person", "cand-0573": "person", "cand-1526": "person", "cand-1722": "place", "cand-0571": "person", "cand-1172": "person", "cand-6966": "place", "cand-6967": "place", "cand-6975": "term"}
    for cid, expected_type in expected_types.items():
        if cid not in candidates or candidates[cid]["suggested_type"] != expected_type:
            raise SystemExit(f"candidate type guard failed for {cid}")
    last_number = max(int(row["candidate_id"].removeprefix("cand-")) for row in candidate_rows)
    if NEW_CANDIDATE_ID != f"cand-{last_number + 1:04d}":
        raise SystemExit("candidate ID is no longer the next sequential ID")
    new_candidate = {
        "candidate_id": NEW_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Unidentified small version of the Fountain of the Four Rivers in Del Carpio’s collection",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "The source identifies a small version owned by Del Carpio but gives no title, maker, date, or present location. Keep it distinct from the Fountain of the Four Rivers in Piazza Navona.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L270",
    }

    mention_fields, mention_rows = read_csv(MENTIONS, raw[MENTIONS])
    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    if len(mention_by_id) != len(mention_rows):
        raise SystemExit("duplicate mention IDs")
    page_mentions = [row for row in mention_rows if row["segment_id"] == SEGMENT]
    if len(page_mentions) != 87:
        raise SystemExit(f"unexpected p.191 mention count: {len(page_mentions)}")
    segment_text = "\n".join(source_lines[267:280])
    for mention in page_mentions:
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if segment_text[start:end] != mention["surface_form"]:
            raise SystemExit(f"p.191 mention span mismatch: {mention['mention_id']}")
    for mid, (old_candidate, new_candidate_id) in MENTION_FIXES.items():
        mention = mention_by_id.get(mid)
        if not mention or mention["candidate_id"] != old_candidate:
            raise SystemExit(f"fountain mention mapping changed: {mid}")
        mention["candidate_id"] = new_candidate_id
    location_mention = mention_by_id.get("m-chp7-p191-015")
    if not location_mention or location_mention["candidate_id"] != "cand-3455":
        raise SystemExit("Piazza Navona mention changed")
    location_mention["note"] = "The phrase locates the original Fountain of the Four Rivers; the small version in Del Carpio’s collection is not said to have been in the piazza."

    for sid, endpoints in ENDPOINT_FIXES.items():
        row = by_id[sid]
        for field, (old_value, new_value) in endpoints.items():
            if row.get(field) != old_value:
                raise SystemExit(f"endpoint changed for {sid}.{field}: expected {old_value!r}, got {row.get(field)!r}")
            if new_value and new_value not in candidates and new_value != NEW_CANDIDATE_ID:
                raise SystemExit(f"endpoint candidate missing for {sid}.{field}: {new_value}")
            row[field] = new_value

    for sid, note in {**TRUE_NOTES, **FALSE_NOTES}.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = sid in TRUE_NOTES
        q["relation_candidate_note"] = note

    by_id["st-chp7-p191-i01"]["qualifiers"]["claim"] = "Haskell says Del Carpio felt an affinity between Massimi’s classical taste and his own."
    by_id["st-chp7-p191-i07"]["qualifiers"]["actor_candidate_id"] = "cand-0573"
    by_id["st-chp7-p191-i22"]["predicate"] = "in_charge_of"
    by_id["st-chp7-p191-i22"]["qualifiers"]["claim"] = "Haskell says Giuseppe Pinacci was put in charge of Del Carpio’s paintings and describes him as an expert restorer."
    by_id["st-chp7-p191-i22"]["qualifiers"]["qualification"] = "The relation is Pinacci’s responsibility for the collection; the text does not say he restored paintings in it."
    by_id["st-chp7-p191-i06"]["qualifiers"]["mentioned_candidate_ids"] = [NEW_CANDIDATE_ID if cid == "cand-0318" else cid for cid in by_id["st-chp7-p191-i06"]["qualifiers"].get("mentioned_candidate_ids", [])]
    by_id["st-chp7-p191-i06"]["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(by_id["st-chp7-p191-i06"]["qualifiers"]["mentioned_candidate_ids"]))
    by_id["st-chp7-p191-i07"]["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(by_id["st-chp7-p191-i07"]["qualifiers"].get("mentioned_candidate_ids", [])))
    by_id["st-chp7-p191-i28"]["qualifiers"]["decomposed_into_statement_ids"] = list(NEW_CHILD_IDS)

    children = [
        build_child(
            by_id["st-chp7-p191-i28"],
            NEW_CHILD_IDS[0],
            "cand-1722",
            "Naples had lost a loving father",
            "reported_lost_as_loving_father",
            "An unnamed judgement quoted by Haskell said Naples had lost a loving father when Del Carpio died.",
            ["cand-1722", "cand-0571"],
            "This is the city part of the unnamed judgement reported by Haskell; it is not independent evidence of a community consensus.",
        ),
        build_child(
            by_id["st-chp7-p191-i28"],
            NEW_CHILD_IDS[1],
            "cand-6962",
            "her artists a great support",
            "reported_lost_as_great_support",
            "An unnamed judgement quoted by Haskell said Naples’s artists had lost a great support when Del Carpio died.",
            ["cand-6962", "cand-0571"],
            "The preceding clause’s verb ‘had lost’ governs this coordinated phrase; the judgement’s source is unnamed.",
        ),
    ]
    source_block = "\n".join(source_lines[276:277])
    if any(child["original_quote"] not in source_block for child in children):
        raise SystemExit("decomposed p.191 quote does not match source L277")
    for child in children:
        for cid in [child["subject_candidate_id"], child["object_candidate_id"], *child["qualifiers"]["mentioned_candidate_ids"]]:
            if cid not in candidates:
                raise SystemExit(f"decomposed statement references missing candidate: {child['statement_id']} {cid}")

    result_statements = []
    for row in statements:
        result_statements.append(row)
        if row["statement_id"] == "st-chp7-p191-i28":
            result_statements.extend(children)
    result_candidates = candidate_rows + [new_candidate]

    statement_bytes = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in result_statements) + "\n").encode("utf-8")
    if not isinstance(result_candidates, list) or any(not isinstance(row, dict) for row in result_candidates):
        raise SystemExit(f"candidate serialization input has unexpected shape: {type(result_candidates).__name__}, {type(result_candidates[0]).__name__}")
    candidate_bytes = csv_bytes(CANDIDATES, raw[CANDIDATES], candidate_fields, result_candidates)
    mention_bytes = csv_bytes(MENTIONS, raw[MENTIONS], mention_fields, mention_rows)
    print(json.dumps({
        "mode": "apply" if args.apply else "dry_run",
        "segment": SEGMENT,
        "classified_unset": len(unset),
        "new_true": sum(1 for sid in unset if sid in TRUE_NOTES),
        "new_false": sum(1 for sid in unset if sid in FALSE_NOTES),
        "previous_true_retained": len(prior_true),
        "new_true_after_decomposition": len(children),
        "segment_total_after": {"true": len(TRUE_NOTES) + len(children), "false": len(FALSE_NOTES), "unset": 0, "statements": len(page_rows) + len(children)},
        "new_candidate": NEW_CANDIDATE_ID,
        "new_statements": list(NEW_CHILD_IDS),
        "endpoint_fixes": ENDPOINT_FIXES,
        "mention_fixes": MENTION_FIXES,
        "before_sha256": {path.name: digest(data) for path, data in raw.items()},
        "after_sha256": {STATEMENTS.name: digest(statement_bytes), CANDIDATES.name: digest(candidate_bytes), MENTIONS.name: digest(mention_bytes)},
    }, ensure_ascii=True, indent=2))

    if not args.apply:
        return
    backups = ((STATEMENTS, STATEMENT_BACKUP), (CANDIDATES, CANDIDATE_BACKUP), (MENTIONS, MENTION_BACKUP))
    if any(backup.exists() for _, backup in backups):
        raise SystemExit("a p.191 recovery backup already exists; refusing to overwrite")
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
