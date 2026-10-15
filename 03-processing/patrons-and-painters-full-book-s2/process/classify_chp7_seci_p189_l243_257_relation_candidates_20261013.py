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
SEGMENT = "chp-7:07_CHP-7_sec_i:l243-257"
STATEMENT_BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p189-l243-257-relation-classification-20261013"
MENTION_BACKUP = TABLES / "mentions.csv.bak-s2-chp7-seci-p189-l243-257-entity-endpoint-repair-20261013"
EXPECTED = {
    STATEMENTS: "1ba4f4ffd48ad98e3d2dbaca9354cdc0be047e212742a0ec2b15e04fddfb94ad",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    MENTIONS: "9068b3b680e284e9b3cb9c43a6a211f0de80ec32043358f2a192d1c3fccc307b",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TRUE_NOTES = {
    "st-chp7-p189-i01": "This completes the p.188 sentence: Louis XIV established the French Academy in Rome in 1666 with Bernini's support.",
    "st-chp7-p189-i02": "This records the Academy's declared educational and competitive purpose; the eventual replacement of Italian artists is a goal, not an accomplished result.",
    "st-chp7-p189-i03": "This preserves Haskell's comparative assessment of the limited Italian participation in Versailles; the contributing artists and works are not enumerated here.",
    "st-chp7-p189-i04": "This records that Louis XIV's practice of seeking artists in Italy persisted beyond the Versailles project.",
    "st-chp7-p189-i05": "This records Francesco Borzone's employment by Louis XIV through 1679 after being summoned to Paris.",
    "st-chp7-p189-i06": "This records Louis XIV selecting Domenico Guidi, the sculptor, to make one of the Versailles garden groups; the separate group work is retained in mentions.",
    "st-chp7-p189-i07": "This records the sculptured group as planned to be based on drawings supplied by Le Brun; it does not assert that the design was completed or executed.",
    "st-chp7-p189-i08": "This records the allegorical subject of Guidi's group: Fame inscribing Louis XIV's glory on Time's shoulders.",
    "st-chp7-p189-i09": "This records the group's eventual arrival in France after difficulties; it does not specify which difficulties.",
    "st-chp7-p189-i10": "This records the use of Guidi's group in place of Bernini's equestrian statue.",
    "st-chp7-p189-i11": "This preserves Louis XIV's reported assessment of the group's drapery as too rich.",
    "st-chp7-p189-i12": "This records Carlo Maratta's commission to paint the large Apollo and Daphne picture; the commissioning patron is not named in this sentence.",
    "st-chp7-p189-i13": "This records the reported payment and royal title associated with Maratta's Apollo and Daphne commission; the source does not identify who conferred the title.",
    "st-chp7-p189-i14": "This records the unnamed director of the French Academy in Rome asking whether Carlo Cignani would go to Paris; an inquiry is not treated as a completed invitation or move.",
    "st-chp7-p189-i15": "This records Cignani's two otherwise unidentified paintings for Louis XIV.",
    "st-chp7-p189-i16": "This preserves Haskell's account that the Paris matter was not pursued because Cignani's draughtsmanship was considered too weak; the decision-maker and proposed journey are not identified.",
    "st-chp7-p189-i17": "This preserves Haskell's comparison between Louis XIV's Italian artist patronage and artists' expectations without inventing quantities.",
    "st-chp7-p189-i18": "This records Italian painters looking to Paris for support after papal employment declined, often without success.",
    "st-chp7-p189-i20": "This records Bellori's 1672 book being dedicated to Colbert.",
    "st-chp7-p189-i21": "This records Malvasia's 1678 book being dedicated to Louis XIV.",
    "st-chp7-p189-i22": "This records Haskell's account of Bolognese artists' interest in attracting French attention; the precise membership of the wider group remains open.",
    "st-chp7-p189-i24": "This preserves Haskell's explicitly skeptical inference that the named artists' admiration may not have been wholly disinterested; the material motive is unspecified.",
    "st-chp7-p189-i25": "This records Preti making a portrait of Louis XIV intended as a gift; intention is not confused with delivery.",
    "st-chp7-p189-i26": "This records Haskell's causal account linking France-Spain hostilities and Preti's Malta situation to the imprudence of the intended gift.",
    "st-chp7-p189-i27": "This records Preti selling the portrait elsewhere after deciding the gift was imprudent; the buyer and destination are not identified.",
    "st-chp7-p189-i28": "This records Haskell's claim that Spain continued to welcome Italian painters and their works.",
}

FALSE_NOTES = {
    "st-chp7-p189-i19": "This is Haskell's rhetorical assessment that the painters' hints were broad enough, not a separate relation between identified entities.",
    "st-chp7-p189-i23": "This aggregate list sentence is decomposed into four person-to-Louis XIV relation candidates; it is retained as the source-level parent record.",
}

OPEN_ENDPOINTS = {
    "st-chp7-p189-i03": "The source gives no list of the individual Italian participants or their works in the Versailles enterprise.",
    "st-chp7-p189-i12": "The source uses a passive commission and does not identify the commissioning patron.",
    "st-chp7-p189-i13": "The source does not identify who conferred the title peintre du roi; the statement also preserves the payment claim for the named painting.",
    "st-chp7-p189-i14": "The director's personal identity is unknown, and the inquiry does not establish whether Cignani accepted or travelled.",
    "st-chp7-p189-i16": "The proposed Paris journey and the person who decided not to press the matter are not separately identified.",
    "st-chp7-p189-i17": "Neither the scope of Louis XIV's patronage examples nor the artists' expectations is quantified.",
    "st-chp7-p189-i18": "The painters are a broad source-defined group and the cases of unsuccessful support are not individually listed.",
    "st-chp7-p189-i22": "The Bolognese collective is only partly specified; the four named artists are recorded separately in the decomposed following statement.",
    "st-chp7-p189-i24": "The suspected material interest is not identified; the statement remains Haskell's inference, not a confirmed motive.",
    "st-chp7-p189-i26": "The France-Spain hostilities are undated and not identified as a particular conflict.",
    "st-chp7-p189-i27": "The source says only that Preti sold the picture elsewhere; buyer and destination are unnamed.",
}

ENDPOINT_FIXES = {
    "st-chp7-p189-i06": {"object": ("cand-1280", "cand-1277")},
    "st-chp7-p189-i07": {"object": ("cand-1376", "cand-11487")},
    "st-chp7-p189-i26": {"object": ("cand-6938", "cand-6937")},
}

DECOMPOSED = {
    "st-chp7-p189-i23": [
        ("st-chp7-p189-i23-cignani", "cand-0748", "Carlo Cignani"),
        ("st-chp7-p189-i23-gennari", "cand-1127", "Benedetto Gennari"),
        ("st-chp7-p189-i23-quaini", "cand-2073", "Luigi Quaini"),
        ("st-chp7-p189-i23-crete", "cand-0889", "Donato Creti"),
    ]
}

MENTION_FIX = {
    "mention_id": "m-chp7-p189-015",
    "candidate_id_before": "cand-1280",
    "candidate_id_after": "cand-1277",
    "surface_form": "Domenico Guidi",
    "start_char": "707",
    "end_char": "721",
    "note": "Domenico Guidi, the sculptor selected by Louis XIV; keep distinct from the index work candidate for his Versailles groups.",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def build_person_relation(parent: dict, statement_id: str, person_id: str, person_name: str) -> dict:
    q = parent["qualifiers"]
    claim = f"Haskell reports {person_name} as one of the Bolognese artists who was a keen admirer of Louis XIV."
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": person_id,
        "object_candidate_id": "cand-1447",
        "predicate": "bolognese_artist_was_reported_as_keen_admirer_of_louis_xiv",
        "qualifiers": {
            "source_line_start": q["source_line_start"],
            "source_line_end": q["source_line_end"],
            "printed_page": q["printed_page"],
            "pdf_physical_page": q["pdf_physical_page"],
            "claim": claim,
            "speaker": "Haskell, reporting an unnamed source",
            "text_layer": "body reported claim",
            "qualification": "The source says 'We are told'; the report is attributed and is not independently corroborated here.",
            "mentioned_candidate_ids": [person_id, "cand-1447"],
            "decomposed_from_statement_id": parent["statement_id"],
            "relation_candidate": True,
            "relation_candidate_note": "This is one atomic person-to-Louis XIV relation from the four-name list in the parent source sentence.",
        },
        "original_quote": parent["original_quote"],
        "origin": parent["origin"],
        "source_file": parent["source_file"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.189 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    required_source = (
        (243, "[Page 189]"),
        (244, "Louis established in 1666 the French Academy in Rome"),
        (245, "Italian participation in Versailles"),
        (246, "A Roman sculptor of classicising tendencies, Domenico Guidi"),
        (246, "based on drawings provided by Le Brun"),
        (246, "Meanwhile Carlo Maratta had been commissioned"),
        (247, "Academy in Rome was making enquiries"),
        (249, "But the matter was not pressed as Cignani"),
        (251, "Again and again we come across instances of Italian painters"),
        (252, "Bellori’s Le Vite de’ Pittori"),
        (253, "The Bolognese, especially"),
        (255, "not being excessively cynical to suspect"),
        (256, "hostilities broke out between France and Spain"),
        (257, "Spain however retained a welcome interest"),
    )
    if any(text not in source_lines[index - 1] for index, text in required_source):
        raise SystemExit("p.189 source-line guards failed")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    expected_targets = set(TRUE_NOTES) | set(FALSE_NOTES)
    if unset != expected_targets or len(unset) != 28:
        raise SystemExit(f"p.189 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 244 or end > 257 or start > end:
            raise SystemExit(f"invalid p.189 source anchor: {sid} {start}-{end}")
        refs = [row.get("subject_candidate_id"), row.get("object_candidate_id")] + q.get("mentioned_candidate_ids", [])
        missing_refs = sorted({cid for cid in refs if cid and cid not in candidate_ids})
        if missing_refs:
            raise SystemExit(f"candidate reference missing for {sid}: {missing_refs}")

    parent = by_id["st-chp7-p188-i34"]
    parent_q = parent.get("qualifiers") or {}
    opening = by_id["st-chp7-p189-i01"]
    opening_q = opening.get("qualifiers") or {}
    if opening_q.get("continuation_of_statement_id") != parent["statement_id"]:
        raise SystemExit("p.188 quotation continuation target changed")
    if parent_q.get("continuation_to_segment_id") != SEGMENT or parent_q.get("continuation_source_line_start") != 244:
        raise SystemExit("p.188 to p.189 continuation link changed")

    mention_rows = list(csv.DictReader(io.StringIO(raw[MENTIONS].decode("utf-8-sig"), newline="")))
    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    if len(mention_by_id) != len(mention_rows):
        raise SystemExit("duplicate mention IDs")
    mention = mention_by_id.get(MENTION_FIX["mention_id"])
    for field in ("candidate_id", "surface_form", "start_char", "end_char"):
        expected = MENTION_FIX["candidate_id_before"] if field == "candidate_id" else MENTION_FIX[field]
        if not mention or mention.get(field) != expected:
            raise SystemExit(f"Guidi mention changed: {field} expected {expected!r}")
    if mention.get("segment_id") != SEGMENT:
        raise SystemExit("Guidi mention segment changed")

    new_ids = [sid for entries in DECOMPOSED.values() for sid, _, _ in entries]
    if any(sid in by_id for sid in new_ids):
        raise SystemExit("a decomposed statement ID already exists")
    for sid, person_id, _ in [entry for entries in DECOMPOSED.values() for entry in entries]:
        if person_id not in candidate_ids or "cand-1447" not in candidate_ids:
            raise SystemExit(f"decomposed relation references missing candidate: {sid}")

    for sid, note in {**TRUE_NOTES, **FALSE_NOTES}.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = sid in TRUE_NOTES
        q["relation_candidate_note"] = note
        if sid in OPEN_ENDPOINTS:
            q["open_endpoint_reason"] = OPEN_ENDPOINTS[sid]
    for sid, endpoints in ENDPOINT_FIXES.items():
        row = by_id[sid]
        for endpoint, (expected_old, new_value) in endpoints.items():
            field = f"{endpoint}_candidate_id"
            if row.get(field) != expected_old:
                raise SystemExit(f"{sid} {field} changed: expected {expected_old!r}, got {row.get(field)!r}")
            if new_value not in candidate_ids:
                raise SystemExit(f"{sid} references missing {new_value}")
            row[field] = new_value

    guidid = by_id["st-chp7-p189-i06"]
    guidid_q = guidid.setdefault("qualifiers", {})
    mentioned = guidid_q.get("mentioned_candidate_ids", [])
    if "cand-1280" not in mentioned or "cand-1277" in mentioned:
        raise SystemExit("Guidi statement mention candidates changed")
    guidid_q["mentioned_candidate_ids"] = [cid for cid in mentioned if cid != "cand-1280"] + ["cand-1277"]
    for sid, endpoints in ENDPOINT_FIXES.items():
        q = by_id[sid].get("qualifiers") or {}
        for endpoint, (_, new_value) in endpoints.items():
            if new_value not in q.get("mentioned_candidate_ids", []):
                raise SystemExit(f"{sid} repaired endpoint {new_value} is not present in its mention set")
    grouped = by_id["st-chp7-p189-i23"]
    grouped_q = grouped.setdefault("qualifiers", {})
    grouped_q["decomposed_into_statement_ids"] = new_ids

    opening_q["continuation_from_segment_id"] = "chp-7:07_CHP-7_sec_i:l232-241"
    opening_q["continuation_status"] = "closed"

    for row in mention_rows:
        if row["mention_id"] == MENTION_FIX["mention_id"]:
            row["candidate_id"] = MENTION_FIX["candidate_id_after"]
            row["note"] = MENTION_FIX["note"]
            break
    else:
        raise SystemExit("Guidi mention row missing")

    additions = [
        build_person_relation(grouped, sid, person_id, name)
        for sid, person_id, name in DECOMPOSED["st-chp7-p189-i23"]
    ]
    expanded_rows: list[dict] = []
    for row in rows:
        expanded_rows.append(row)
        if row["statement_id"] == grouped["statement_id"]:
            expanded_rows.extend(additions)
    rows = expanded_rows

    output_statements = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n"
    output_mentions = io.StringIO(newline="")
    writer = csv.DictWriter(output_mentions, fieldnames=list(mention_rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(mention_rows)
    result_statements = output_statements.encode("utf-8")
    result_mentions = output_mentions.getvalue().encode("utf-8")

    print(json.dumps({
        "mode": "apply" if args.apply else "dry_run",
        "segment": SEGMENT,
        "classified_existing": len(unset),
        "relation_candidate_true_existing": len(TRUE_NOTES),
        "relation_candidate_false_existing": len(FALSE_NOTES),
        "decomposed_person_relations_added": len(additions),
        "total_true_after_decomposition": len(TRUE_NOTES) + len(additions),
        "total_false_after_decomposition": len(FALSE_NOTES),
        "unset_in_segment": 0,
        "endpoint_fixes": ENDPOINT_FIXES,
        "mention_fix": MENTION_FIX["mention_id"],
        "continuation_link": "st-chp7-p188-i34 -> st-chp7-p189-i01",
        "before_sha256": {path.name: digest(raw[path]) for path in raw},
        "after_sha256": {STATEMENTS.name: digest(result_statements), MENTIONS.name: digest(result_mentions)},
    }, ensure_ascii=True))
    if not args.apply:
        return
    if STATEMENT_BACKUP.exists() or MENTION_BACKUP.exists():
        raise SystemExit("a p.189 recovery backup already exists; refusing to overwrite")
    shutil.copy2(STATEMENTS, STATEMENT_BACKUP)
    shutil.copy2(MENTIONS, MENTION_BACKUP)
    atomic_write(STATEMENTS, result_statements)
    atomic_write(MENTIONS, result_mentions)
    print(f"statement_backup={STATEMENT_BACKUP.relative_to(ROOT)}")
    print(f"mention_backup={MENTION_BACKUP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
