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
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
PDF = ROOT / "02-sources/01-book/CHP-3.pdf"
PAGE_75 = ROOT / ".tmp_s2_ch3_phys17.png"
PAGE_76 = ROOT / ".tmp_s2_ch3_phys18-18.png"
SEGMENT = "chp-3:03_CHP-3_sec_ii:l125-135"
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
NEW_CANDIDATE_ID = "cand-11593"
NEW_STATEMENT_ID = "st-chp3-secii-l125-135-borromini-employment-bernini"
NEW_MENTION_IDS = (
    "m-chp3-secii-l125-135-0060",
    "m-chp3-secii-l125-135-0061",
)
SUFFIX = ".bak-s2-chp3-sec-ii-l125-135-relations-20261010"
BACKUPS = {
    TABLE: TABLE.with_name(TABLE.name + SUFFIX),
    CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + SUFFIX),
    MENTIONS: MENTIONS.with_name(MENTIONS.name + SUFFIX),
}
EXPECTED_HASHES = {
    TABLE: "97184cf0124a9aa9dbd8726dda0514d74210192277f61d644fc2afdf7f9b622f",
    CANDIDATES: "4aacfca90eb210a517a4bd374250c76162dbed3891ba41dd9a9a3189e3b83e43",
    MENTIONS: "527b4072e654da5a424c1d26e445b0be69bd0a7e113fc1cc8e069ebbf3561df2",
    COVERAGE: "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
    PAGE_75: "f5ab2ab11db16c7426ca25ed88b2636ffed304257a2c837834c42b5f85f6c6dd",
    PAGE_76: "b8c9b0696003334ddc7ba7779fb6f8aeee8af50324df9ce2111faeb1fe84b09f",
}

TRUE_NOTES = {
    "st-chp3-secii-l125-135-alterations-by-borromini": "Haskell says Borromini was to carry out the specified palace alterations; the work remains an unnamed group of alterations.",
    "st-chp3-secii-l125-135-bernardino-legate": "The passage says Cardinal Bernardino Spada served as legate in Bologna from 1627 to 1631.",
    "st-chp3-secii-l125-135-bernardino-protege": "Haskell describes Cardinal Bernardino Spada as a protege of Urban VIII.",
    "st-chp3-secii-l125-135-borromini-choice": "Haskell says Borromini was chosen as architect for the Oratorio; Virgilio Spada is retained as the chooser in the claim.",
    "st-chp3-secii-l125-135-borromini-dispute": "Haskell says Borromini's personality and principles made a dispute with the unnamed Barberini architect inevitable; keep that group endpoint unresolved.",
    "st-chp3-secii-l125-135-borromini-employment": "Haskell describes Virgilio Spada as a special admirer of Borromini.",
    "st-chp3-secii-l125-135-colonnade": "Haskell attributes construction of the illusionistic garden colonnade to Borromini.",
    "st-chp3-secii-l125-135-court-influence": "Haskell infers Oratorian influence at Urban VIII's papal court from Pietro da Cortona being allowed to leave the Barberini ceiling; the inference remains attributed to Haskell.",
    "st-chp3-secii-l125-135-fresco-significance": "Haskell says the two frescoes began Pietro da Cortona's close association with the Oratorians; his assessment of their future significance and the later transformation remains attributed.",
    "st-chp3-secii-l125-135-jesuit-outdistanced": "The passage explicitly says the Jesuits were outdistanced by unnamed rivals; do not resolve the group to the Oratorians from the following paragraph alone.",
    "st-chp3-secii-l125-135-oratorio-commission": "The Oratorians commissioned Borromini to design the building adjoining Chiesa Nuova, later called the Oratorio.",
    "st-chp3-secii-l125-135-palace-from-mignanelli": "Haskell says Cardinal Bernardino acquired the palace from the Mignanelli family in 1632.",
    "st-chp3-secii-l125-135-picture-collection": "The passage says the palace held Cardinal Bernardino's rich picture collection; the claim about many pictures being from Bologna remains source-attributed and semantically unresolved.",
    "st-chp3-secii-l125-135-pietro-interruption": "Haskell says Pietro da Cortona interrupted work on the Barberini ceiling to fulfil obligations to Chiesa Nuova.",
    "st-chp3-secii-l125-135-trinitarian-church-commission": "Haskell says Borromini was entrusted with building a church for the Discalced Trinitarians.",
    "st-chp3-secii-l125-135-trinitarian-commission": "Haskell says Borromini was entrusted with building a monastery for the Discalced Trinitarians.",
    "st-chp3-secii-l125-135-trinitarian-left-base": "The passage says the Discalced Trinitarians left their original base in Spain.",
    "st-chp3-secii-l125-135-trinitarian-migration": "The passage says the Discalced Trinitarians settled in Rome at the beginning of the century.",
    "st-chp3-secii-l125-135-virgilio-chapel": "Haskell says Virgilio Spada helped design the family chapel at S. Girolamo della Carita.",
    "st-chp3-secii-l125-135-virgilio-protege": "Haskell describes Virgilio Spada as a protege of Urban VIII.",
    "st-chp3-secii-l125-135-works-baroque-consequence": "Haskell assesses the Oratorian commissions of a fresco and a building as consequential for the development of Baroque art.",
}
FALSE_NOTES = {
    "st-chp3-secii-l125-135-jesuit-bare": "The sentence describes the S. Ignazio church's unfinished condition and chronology, not a relation between entities.",
    "st-chp3-secii-l125-135-official-commissions": "The statement records Borromini's career status and time limit; no specific commission or responsible actor is identified.",
    "st-chp3-secii-l125-135-pietro-status": "Fashionable and powerful are Haskell's time-specific assessments of Pietro da Cortona, not inter-entity relations.",
    "st-chp3-secii-l125-135-site-limits": "Small and inconvenient are physical attributes of the Trinitarian site.",
    "st-chp3-secii-l125-135-spadas-connoisseurs": "This is a shared attribute of Virgilio and Cardinal Bernardino Spada, not a relation between the two men.",
    "st-chp3-secii-l125-135-virgilio-architecture": "Architecture-oriented interest and dilettante status are Haskell's characterizations of Virgilio Spada.",
}
SINGLE_TRUE_IDS = {
    "st-chp3-secii-l125-135-borromini-early-employment",
    "st-chp3-secii-l125-135-court-influence",
    "st-chp3-secii-l125-135-jesuit-outdistanced",
}
BILATERAL_TRUE_IDS = set(TRUE_NOTES) - {
    "st-chp3-secii-l125-135-court-influence",
    "st-chp3-secii-l125-135-jesuit-outdistanced",
}
EARLY_EMPLOYMENT_NOTE = "The passage says Borromini was employed on comparatively minor tasks under Carlo Maderno for many years."
BERNINI_EMPLOYMENT_NOTE = "The same passage separately says Borromini was employed on comparatively minor tasks under Gian Lorenzo Bernini for many years."
ALREADY_TRUE = {
    "st-chp3-secii-l125-135-alterations-for-spada",
    "st-chp3-secii-l125-135-angels-fresco",
    "st-chp3-secii-l125-135-church-site",
    "st-chp3-secii-l125-135-colonnade-for-spada",
    "st-chp3-secii-l125-135-construction-site",
    "st-chp3-secii-l125-135-fresco-commission",
    "st-chp3-secii-l125-135-oratorian-fresco",
    "st-chp3-secii-l125-135-oratorio-commissioned-by",
    "st-chp3-secii-l125-135-oratorio-start",
    "st-chp3-secii-l125-135-palace-acquisition",
    "st-chp3-secii-l125-135-philip-fresco",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def normalized(value: str) -> str:
    return " ".join(value.split())


def encode_jsonl(rows: list[dict], raw: bytes) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    prefix = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    return prefix + b"".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + newline for row in rows
    )


def encode_csv(rows: list[dict], raw: bytes, fieldnames: list[str]) -> bytes:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator=newline, extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    prefix = "\ufeff" if raw.startswith(b"\xef\xbb\xbf") else ""
    return (prefix + stream.getvalue()).encode("utf-8")


def atomic_write(path: Path, payload: bytes) -> None:
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
            handle.write(payload)
            temp_path = Path(handle.name)
        os.replace(temp_path, path)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply reviewed S2 relation classifications")
    args = parser.parse_args()
    for path, expected in EXPECTED_HASHES.items():
        require(path.exists() and digest(path) == expected, f"preflight hash changed for {path.relative_to(ROOT)}")
    require(all(not backup.exists() for backup in BACKUPS.values()), "a recovery backup already exists")

    raw_table, raw_candidates, raw_mentions = TABLE.read_bytes(), CANDIDATES.read_bytes(), MENTIONS.read_bytes()
    statements = read_jsonl(TABLE)
    require(len(statements) == 12749 and len({r["statement_id"] for r in statements}) == len(statements), "statement table state changed")
    by_id = {row["statement_id"]: row for row in statements}
    segment_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    require(len(segment_rows) == 39, "L125–135 statement count changed")
    pending_ids = {r["statement_id"] for r in segment_rows if (r.get("qualifiers") or {}).get("relation_candidate") is None}
    expected_pending = set(TRUE_NOTES) | set(FALSE_NOTES) | SINGLE_TRUE_IDS
    require(pending_ids == expected_pending, "pending L125–135 statement set changed")
    already_true = {r["statement_id"] for r in segment_rows if (r.get("qualifiers") or {}).get("relation_candidate") is True}
    require(already_true == ALREADY_TRUE, "already-classified L125–135 statement set changed")
    require(NEW_STATEMENT_ID not in by_id, "new statement ID already exists")
    bilateral_pending = {
        r["statement_id"] for r in segment_rows
        if r.get("subject_candidate_id") and r.get("object_candidate_id")
        and (r.get("qualifiers") or {}).get("relation_candidate") is None
    }
    require(bilateral_pending == BILATERAL_TRUE_IDS | {"st-chp3-secii-l125-135-spadas-connoisseurs"}, "pending bilateral set changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[124:135])
    require(segment_text[163:169] == "rivals" and segment_text[1255:1260] == "court", "source mention spans changed")
    manifest = {r["segment_id"]: r for r in read_jsonl(SEGMENTS)}.get(SEGMENT)
    require(
        manifest is not None and (manifest.get("source_file"), manifest.get("line_start"), manifest.get("line_end"))
        == (SOURCE_FILE, 125, 135),
        "S0 segment boundary changed",
    )
    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        coverage_rows = list(csv.DictReader(handle))
    coverage = next((r for r in coverage_rows if r["segment_id"] == SEGMENT), None)
    require(coverage and (coverage["disposition"], coverage["migration_status"]) == ("reviewed", "complete"), "coverage is not complete")

    candidate_rows = list(csv.DictReader(CANDIDATES.open(encoding="utf-8-sig", newline="")))
    candidate_fields = list(candidate_rows[0])
    candidate_by_id = {r["candidate_id"]: r for r in candidate_rows}
    require(len(candidate_rows) == 11570 and NEW_CANDIDATE_ID not in candidate_by_id, "candidate table state changed")
    require(max(int(r["candidate_id"].split("-")[1]) for r in candidate_rows) == 11592, "candidate ID sequence changed")
    require(candidate_by_id["cand-4730"]["suggested_type"] == "institution", "Urban VIII court candidate changed")
    require("Urban VIII" in candidate_by_id["cand-4730"]["canonical_name"], "court candidate scope changed")
    require(candidate_by_id["cand-1477"]["canonical_name"] == "Maderno, Carlo", "Maderno candidate changed")
    require(candidate_by_id["cand-0295"]["canonical_name"] == "Bernini, Gian Lorenzo", "Bernini candidate changed")

    mention_rows = list(csv.DictReader(MENTIONS.open(encoding="utf-8-sig", newline="")))
    mention_fields = list(mention_rows[0])
    mention_by_id = {r["mention_id"]: r for r in mention_rows}
    require(len(mention_rows) == 27509 and all(mid not in mention_by_id for mid in NEW_MENTION_IDS), "mention table state changed")
    require(any(r["mention_id"] == "m-chp3-secii-l125-135-0046" and r["candidate_id"] == "cand-1477" for r in mention_rows), "Maderno mention missing")
    require(any(r["mention_id"] == "m-chp3-secii-l125-135-0047" and r["candidate_id"] == "cand-0295" for r in mention_rows), "Bernini mention missing")
    for statement_id in pending_ids:
        row = by_id[statement_id]
        require(normalized(row.get("original_quote", "")) in normalized(segment_text), f"source quote mismatch: {statement_id}")
    require(by_id["st-chp3-secii-l125-135-borromini-early-employment"].get("subject_candidate_id") == "cand-0404", "Borromini endpoint changed")
    require(by_id["st-chp3-secii-l125-135-court-influence"].get("subject_candidate_id") == "cand-3402", "Oratorian endpoint changed")
    require(by_id["st-chp3-secii-l125-135-jesuit-outdistanced"].get("subject_candidate_id") == "cand-3403", "Jesuit endpoint changed")

    candidate = {
        "candidate_id": NEW_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Unnamed rivals who outdistanced the Jesuits",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell says the Jesuits were outdistanced by their rivals but does not name the rival order or group. "
            "The following Oratorian discussion does not by itself identify the referent."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L126",
    }
    require(list(candidate) == candidate_fields, "candidate schema changed")
    new_mentions = [
        {
            "mention_id": NEW_MENTION_IDS[0],
            "segment_id": SEGMENT,
            "candidate_id": "cand-4730",
            "surface_form": "court",
            "start_char": "1255",
            "end_char": "1260",
            "note": "Mapped to the existing Urban VIII papal-court candidate in the paragraph's immediate reign context; the influence claim remains Haskell's inference.",
        },
        {
            "mention_id": NEW_MENTION_IDS[1],
            "segment_id": SEGMENT,
            "candidate_id": NEW_CANDIDATE_ID,
            "surface_form": "rivals",
            "start_char": "163",
            "end_char": "169",
            "note": "Plural group explicitly named by role but not identified; do not assume the Oratorians are the referent.",
        },
    ]
    require(all(list(r) == mention_fields for r in new_mentions), "mention schema changed")

    for statement_id, note in TRUE_NOTES.items():
        row = by_id[statement_id]
        q = dict(row.get("qualifiers") or {})
        q.update(relation_candidate=True, relation_candidate_note=note)
        row["qualifiers"] = q
    for statement_id, note in FALSE_NOTES.items():
        row = by_id[statement_id]
        q = dict(row.get("qualifiers") or {})
        q.update(relation_candidate=False, relation_candidate_note=note)
        row["qualifiers"] = q

    early = by_id["st-chp3-secii-l125-135-borromini-early-employment"]
    early["object_candidate_id"] = "cand-1477"
    early_q = dict(early.get("qualifiers") or {})
    early_q.pop("other_architect_candidates", None)
    early_q["claim"] = EARLY_EMPLOYMENT_NOTE
    early_q.update(
        relation_candidate=True,
        relation_candidate_note=EARLY_EMPLOYMENT_NOTE,
    )
    early["qualifiers"] = early_q

    court = by_id["st-chp3-secii-l125-135-court-influence"]
    court["object_candidate_id"] = "cand-4730"
    q = dict(court.get("qualifiers") or {})
    q.update(relation_candidate=True, relation_candidate_note=TRUE_NOTES["st-chp3-secii-l125-135-court-influence"])
    court["qualifiers"] = q

    rivals = by_id["st-chp3-secii-l125-135-jesuit-outdistanced"]
    rivals["object_candidate_id"] = NEW_CANDIDATE_ID
    q = dict(rivals.get("qualifiers") or {})
    q["claim"] = "Haskell says the Jesuits had once again been outdistanced by an unnamed group of rivals."
    q["referent_note"] = "The following Oratorian discussion does not prove that the Oratorians are the rivals meant here."
    q.update(relation_candidate=True, relation_candidate_note=TRUE_NOTES["st-chp3-secii-l125-135-jesuit-outdistanced"])
    rivals["qualifiers"] = q

    new_statement = {
        "statement_id": NEW_STATEMENT_ID,
        "segment_id": SEGMENT,
        "subject_candidate_id": "cand-0404",
        "object_candidate_id": "cand-0295",
        "predicate": "employed_under",
        "qualifiers": {
            "source_line_start": 133,
            "source_line_end": 133,
            "claim": "Haskell says Borromini was employed on comparatively minor tasks under Gian Lorenzo Bernini for many years.",
            "speaker": "Haskell",
            "text_layer": "body",
            "print_page": 75,
            "pdf_physical_page": 17,
            "duration": "many years",
            "scope": "comparatively minor tasks",
            "relation_candidate": True,
            "relation_candidate_note": BERNINI_EMPLOYMENT_NOTE,
        },
        "original_quote": by_id["st-chp3-secii-l125-135-borromini-early-employment"]["original_quote"],
        "origin": "book",
        "source_file": SOURCE_FILE,
    }
    require(list(new_statement) == list(statements[0]), "statement schema changed")
    require(normalized(new_statement["original_quote"]) in normalized(segment_text), "new employment statement quote mismatch")
    statements.append(new_statement)
    candidate_rows.append(candidate)
    mention_rows.extend(new_mentions)

    bilateral = [r for r in statements if r.get("subject_candidate_id") and r.get("object_candidate_id")]
    b_true = sum((r.get("qualifiers") or {}).get("relation_candidate") is True for r in bilateral)
    b_false = sum((r.get("qualifiers") or {}).get("relation_candidate") is False for r in bilateral)
    b_pending = sum((r.get("qualifiers") or {}).get("relation_candidate") is None for r in bilateral)
    relation_total = sum((r.get("qualifiers") or {}).get("relation_candidate") is True for r in statements)
    relation_open = sum(
        (r.get("qualifiers") or {}).get("relation_candidate") is True
        and not (r.get("subject_candidate_id") and r.get("object_candidate_id")) for r in statements
    )
    segment_after = [r for r in statements if r.get("segment_id") == SEGMENT]
    seg_true = sum((r.get("qualifiers") or {}).get("relation_candidate") is True for r in segment_after)
    seg_false = sum((r.get("qualifiers") or {}).get("relation_candidate") is False for r in segment_after)
    seg_pending = sum((r.get("qualifiers") or {}).get("relation_candidate") is None for r in segment_after)
    require((len(statements), len(candidate_rows), len(mention_rows)) == (12750, 11571, 27511), "projected table totals differ")
    require((len(bilateral), b_true, b_false, b_pending, relation_total, relation_open) == (8543, 4766, 474, 3303, 4815, 49), "projected whole-book totals differ")
    require((len(segment_after), seg_true, seg_false, seg_pending) == (40, 34, 6, 0), "projected segment totals differ")

    encoded = {
        TABLE: encode_jsonl(statements, raw_table),
        CANDIDATES: encode_csv(candidate_rows, raw_candidates, candidate_fields),
        MENTIONS: encode_csv(mention_rows, raw_mentions, mention_fields),
    }
    report = {
        "action": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT,
        "pending_bilateral_classified": len(BILATERAL_TRUE_IDS) + 1,
        "scalar_nonrelations_classified": len(FALSE_NOTES),
        "employment_split": NEW_STATEMENT_ID,
        "new_candidate": NEW_CANDIDATE_ID,
        "new_mentions": list(NEW_MENTION_IDS),
        "segment_after": {"statements": len(segment_after), "relation_candidates": seg_true, "nonrelations": seg_false, "unclassified": seg_pending},
        "bilateral_after": {"total": len(bilateral), "relation_candidates": b_true, "nonrelations": b_false, "unclassified": b_pending},
        "relation_candidates_total": relation_total,
        "relation_candidates_open": relation_open,
        "post_write_hashes": {str(path.relative_to(ROOT)): hashlib.sha256(payload).hexdigest() for path, payload in encoded.items()},
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print("Dry run only. Pass --apply to write.")
        return

    for path, backup in BACKUPS.items():
        shutil.copy2(path, backup)
    try:
        for path, payload in encoded.items():
            atomic_write(path, payload)
        saved = read_jsonl(TABLE)
        saved_by_id = {r["statement_id"]: r for r in saved}
        saved_candidates = list(csv.DictReader(CANDIDATES.open(encoding="utf-8-sig", newline="")))
        saved_mentions = list(csv.DictReader(MENTIONS.open(encoding="utf-8-sig", newline="")))
        require(len(saved) == 12750 and len(saved_candidates) == 11571 and len(saved_mentions) == 27511, "post-write table counts differ")
        require(all((saved_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is True for sid in TRUE_NOTES), "post-write true classifications differ")
        require(all((saved_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is False for sid in FALSE_NOTES), "post-write false classifications differ")
        require(saved_by_id["st-chp3-secii-l125-135-court-influence"].get("object_candidate_id") == "cand-4730", "court endpoint readback differs")
        require(saved_by_id["st-chp3-secii-l125-135-jesuit-outdistanced"].get("object_candidate_id") == NEW_CANDIDATE_ID, "rival-group endpoint readback differs")
        require(NEW_STATEMENT_ID in saved_by_id and saved_by_id[NEW_STATEMENT_ID].get("object_candidate_id") == "cand-0295", "Bernini employment split missing")
        require(all(digest(path) == hashlib.sha256(payload).hexdigest() for path, payload in encoded.items()), "post-write hashes differ")
    except Exception:
        for path, backup in BACKUPS.items():
            if backup.exists():
                shutil.copy2(backup, path)
        raise
    report["result"] = "applied"
    report["backups"] = [str(path.relative_to(ROOT)) for path in BACKUPS.values()]
    report["sha256_after"] = {str(path.relative_to(ROOT)): digest(path) for path in encoded}
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
