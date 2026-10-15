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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l91-94"
SEGMENT_SHA = "9d24f560848d29aca7437cce39e501eba7b6b5352e2ddce942c713418d352fe1"
SOURCE_SHA = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
BACKUP_SUFFIX = ".bak-s2-chp2-seciv-l91-94-scalar-semantics-20261013"
EXPECTED = {
    "book-statements.jsonl": "18f6f12220381d1577b81ab073fa671de8862683035da6b2b281fbe9f01248e1",
    "entity-candidates.csv": "d7183a4482d3580242b3a0154b5a6a3681c124b2d7fca63facd9aee0b7be37f4",
    "mentions.csv": "2953ae92c215f10d6e66e51d87d6ad0b712b38928ca56829e9c242667258b838",
    "s2-coverage.csv": "6cc036fdec1a72d99f1f88c6f8dd04a86444c411e56e45646f9ba159087e1341",
}
UNSET_IDS = {
    "st-chp2-seciv-l91-94-barberini-at-peak-of-fortunes",
    "st-chp2-seciv-l91-94-bracciolini-character-judged-mean-and-bad-poet",
    "st-chp2-seciv-l91-94-camassei-failure-qualified-by-minor-commissions",
    "st-chp2-seciv-l91-94-cortona-position-established",
    "st-chp2-seciv-l91-94-decoration-begins-in-larger-reception-room",
    "st-chp2-seciv-l91-94-fresco-covers-ceiling-without-illusionistic-scene",
    "st-chp2-seciv-l91-94-fresco-implications-rarely-understood",
    "st-chp2-seciv-l91-94-great-hall-proposals-described-as-grandiose",
    "st-chp2-seciv-l91-94-sacchi-finds-conventional-flattery-difficult",
}
NEW_CANDIDATE = {
    "candidate_id": "cand-11890",
    "canonical_name": "Unspecified group of minor commissions continually awarded to Andrea Camassei",
    "suggested_type": "work",
    "detail": "Haskell says Camassei was continually given minor commissions, but supplies no titles, number, dates, subjects, or locations. Keep this source-defined group distinct from his earlier small-room works and the proposed great-hall decoration.",
}
NEW_STATEMENTS = {
    "st-chp2-seciv-l91-94-camassei-continues-to-receive-minor-commissions",
    "st-chp2-seciv-l91-94-divine-wisdom-fresco-not-illusionistic",
}
NEW_MENTIONS = [
    ("m-chp2-seciv-l91-94-0079", "cand-11889", "the decoration of a much vaster setting", 1759, 1798,
     "The immediately preceding p.50 reference to a larger decorative scheme; p.51 identifies the setting as the principal reception-room."),
    ("m-chp2-seciv-l91-94-0080", "cand-4668", "The whole ceiling", 910, 927,
     "The ceiling of the earlier unnamed room in which the Divine Wisdom fresco was installed; this is not the later principal reception-room."),
    ("m-chp2-seciv-l91-94-0081", "cand-11890", "minor commissions", 2486, 2503,
     "The unspecified group of continuing minor commissions received by Camassei."),
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bytes]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader), raw


def serialize_jsonl(rows: list[dict], original: bytes) -> bytes:
    payload = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")
    return (b"\xef\xbb\xbf" + payload) if original.startswith(b"\xef\xbb\xbf") else payload


def serialize_csv(fieldnames: list[str], rows: list[dict[str, str]], original: bytes) -> bytes:
    buffer = io.StringIO(newline="")
    line_ending = "\r\n" if b"\r\n" in original else "\n"
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator=line_ending, extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    payload = buffer.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + payload) if original.startswith(b"\xef\xbb\xbf") else payload


def add_unique(values: list[str], additions: list[str]) -> list[str]:
    return list(dict.fromkeys([*values, *additions]))


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve the remaining scalar and embedded relation claims in CHP-2 p.51.")
    parser.add_argument("--apply", action="store_true", help="write after protected preview; default is preview")
    args = parser.parse_args()
    paths = {name: TABLES / name for name in EXPECTED}
    raw_by_name = {name: path.read_bytes() for name, path in paths.items()}
    for name, expected in EXPECTED.items():
        actual = hashlib.sha256(raw_by_name[name]).hexdigest()
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE) != SOURCE_SHA:
        raise SystemExit("protected S0 source asset changed")

    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected p.51 source segment fingerprint changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    if hashlib.sha256(source_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
        raise SystemExit("p.51 source segment content changed")

    statements = read_jsonl(paths["book-statements.jsonl"])
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"] for row in statements
        if row.get("segment_id") == SEGMENT_ID and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    if unset != UNSET_IDS:
        raise SystemExit(f"unexpected p.51 unset set: {sorted(unset)}")
    if NEW_STATEMENTS & by_id.keys():
        raise SystemExit(f"planned statement IDs already exist: {sorted(NEW_STATEMENTS & by_id.keys())}")

    candidate_fields, candidates, candidate_raw = read_csv(paths["entity-candidates.csv"])
    mention_fields, mentions, mention_raw = read_csv(paths["mentions.csv"])
    coverage_fields, coverage, coverage_raw = read_csv(paths["s2-coverage.csv"])
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    if NEW_CANDIDATE["candidate_id"] in candidate_by_id:
        raise SystemExit("planned Camassei commission candidate ID already exists")
    required_candidates = {"cand-0484", "cand-4003", "cand-4668", "cand-4685", "cand-4686", "cand-4687", "cand-11889"}
    if required_candidates - candidate_by_id.keys():
        raise SystemExit(f"required S2 candidates missing: {sorted(required_candidates - candidate_by_id.keys())}")
    expected_scheme_detail = (
        "Haskell says themes in Camassei's paired ceiling frescoes foreshadow a much larger decorative scheme to follow. "
        "The scheme has no title or identified scope here; keep distinct from the two small-room frescoes and the separate Divine Wisdom fresco."
    )
    if candidate_by_id["cand-11889"].get("detail") != expected_scheme_detail:
        raise SystemExit("the p.50 decorative-scheme candidate changed; review before extending it")
    mention_ids = {row["mention_id"] for row in mentions}
    if mention_ids & {item[0] for item in NEW_MENTIONS}:
        raise SystemExit("a planned p.51 mention ID already exists")
    coverage_rows = [row for row in coverage if row.get("segment_id") == SEGMENT_ID]
    if len(coverage_rows) != 1 or "L92-94" not in coverage_rows[0].get("source_line_ranges", ""):
        raise SystemExit("p.51 coverage row is missing or has an unexpected source range")

    for _, _, surface, start, end, _ in NEW_MENTIONS:
        if source_text[start:end] != surface:
            raise SystemExit(f"protected mention span mismatch: {surface!r} at {start}:{end}")

    decisions = {
        "st-chp2-seciv-l91-94-barberini-at-peak-of-fortunes": "This is Haskell's contextual assessment of the family's fortunes, with no relation endpoint asserted.",
        "st-chp2-seciv-l91-94-bracciolini-character-judged-mean-and-bad-poet": "This is Haskell's biographical and literary evaluation of Bracciolini, not a relation claim.",
        "st-chp2-seciv-l91-94-cortona-position-established": "This is Haskell's comparative assessment of Cortona's artistic standing; the peers are not identified as relation endpoints.",
        "st-chp2-seciv-l91-94-fresco-implications-rarely-understood": "This is Haskell's reception judgment about the fresco's implications; no reader or group is identified as an endpoint.",
        "st-chp2-seciv-l91-94-great-hall-proposals-described-as-grandiose": "This is an authorial evaluation of the proposals' scale and spectacle, not a relation between entities.",
        "st-chp2-seciv-l91-94-sacchi-finds-conventional-flattery-difficult": "This is Haskell's characterization of Sacchi's disposition toward conventional flattery, not a relation claim.",
    }
    for statement_id, note in decisions.items():
        row = by_id[statement_id]
        row.setdefault("qualifiers", {})["relation_candidate"] = False
        row["qualifiers"]["relation_candidate_note"] = note

    failure_id = "st-chp2-seciv-l91-94-camassei-failure-qualified-by-minor-commissions"
    failure = by_id[failure_id]
    failure_q = failure["qualifiers"]
    failure_q["claim"] = "Haskell qualifies Camassei's failure to secure the principal reception-room as only relative."
    failure_q["relation_candidate"] = False
    failure_q["relation_candidate_note"] = "This is Haskell's evaluation of Camassei's position; the specific supporting fact about continuing minor commissions is recorded as a separate relation candidate."
    failure_q["related_statement_ids"] = add_unique(failure_q.get("related_statement_ids", []), ["st-chp2-seciv-l91-94-camassei-continues-to-receive-minor-commissions"])
    failure["original_quote"] = "With the relative failure of Camassei"

    scheme_location_id = "st-chp2-seciv-l91-94-decoration-begins-in-larger-reception-room"
    scheme_location = by_id[scheme_location_id]
    scheme_location["subject_candidate_id"] = "cand-11889"
    scheme_location["object_candidate_id"] = "cand-4685"
    scheme_location["predicate"] = "located_at"
    slq = scheme_location["qualifiers"]
    slq["claim"] = "In the immediate sequence following the forecast of a larger scheme to come, Haskell says work began on decoration of a much vaster setting, identified as the principal reception-room."
    slq["relation_candidate"] = True
    slq["relation_candidate_note"] = "The adjacent p.50–51 passage links the larger decorative scheme to the principal reception-room; retain it as an open work candidate located in the named room, without assigning a title or equating it with an individual ceiling fresco."
    slq["qualification"] = "The p.50 sentence calls this the much larger scheme of decoration to follow; p.51 identifies the setting as the principal reception-room. The source gives no formal title and does not expressly identify it with Bracciolini's iconographic programme (cand-4686) or Cortona's great ceiling fresco (cand-4687)."
    slq["mentioned_candidate_ids"] = add_unique(slq.get("mentioned_candidate_ids", []), ["cand-11889", "cand-4685", "cand-4003"])
    scheme_location["original_quote"] = (
        "Scarcely had the scaffolding been taken down than work was begun on the decoration of a much vaster setting—"
        "the principal reception-room of the palace."
    )

    fresco_id = "st-chp2-seciv-l91-94-fresco-covers-ceiling-without-illusionistic-scene"
    fresco = by_id[fresco_id]
    fresco["object_candidate_id"] = "cand-4668"
    fresco["predicate"] = "covers_entire_ceiling_of_room"
    fq = fresco["qualifiers"]
    fq["claim"] = "Haskell says Sacchi's Divine Wisdom fresco covered the whole ceiling of the earlier, unidentified room in which it was installed."
    fq["relation_candidate"] = True
    fq["relation_candidate_note"] = "The source explicitly connects the Divine Wisdom fresco to the ceiling of the room in which Sacchi had been assigned to paint; keep this room distinct from the later principal reception-room."
    fq["qualification"] = "The description of the fresco's non-illusionistic treatment is recorded separately."
    fq["mentioned_candidate_ids"] = add_unique(fq.get("mentioned_candidate_ids", []), ["cand-4003", "cand-4668"])
    fresco["original_quote"] = "The whole ceiling is covered with the fresco."

    commission_id = "st-chp2-seciv-l91-94-camassei-continues-to-receive-minor-commissions"
    commission = {
        "statement_id": commission_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-0484",
        "object_candidate_id": "cand-11890",
        "predicate": "artist_received_minor_commissions_reported",
        "qualifiers": {
            "source_line_start": 93, "source_line_end": 93,
            "claim": "Haskell says Camassei was continually given minor commissions, which makes the reported failure to secure the great-hall decoration only relative.",
            "speaker": "Haskell", "text_layer": "authorial narrative",
            "print_page": 51, "pdf_physical_page": 36,
            "time_relation": "Continually, as characterized by Haskell; no dates or duration are supplied.",
            "qualification": "The source names no individual minor commission, subject, count, or commissioner.",
            "relation_candidate": True,
            "relation_candidate_note": "The sentence explicitly says Camassei was continually given minor commissions; preserve the artist-to-commission-group relation with an open work candidate.",
            "mentioned_candidate_ids": ["cand-0484", "cand-11890"],
            "related_statement_ids": [failure_id],
        },
        "original_quote": "he was continually given minor commissions",
        "origin": "book", "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }
    illusionism = {
        "statement_id": "st-chp2-seciv-l91-94-divine-wisdom-fresco-not-illusionistic",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-4003", "object_candidate_id": None,
        "predicate": "scene_representation_mode_described",
        "qualifiers": {
            "source_line_start": 92, "source_line_end": 92,
            "claim": "Haskell says the fresco makes no attempt to represent its scene illusionistically.",
            "speaker": "Haskell", "text_layer": "authorial visual description",
            "print_page": 51, "pdf_physical_page": 36,
            "relation_candidate": False,
            "relation_candidate_note": "This describes the fresco's mode of representation, not a relation to another entity.",
        },
        "original_quote": "no attempt is made to represent the scene illusionistically",
        "origin": "book", "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }
    statements.extend([commission, illusionism])

    candidate_by_id["cand-11889"]["detail"] = (
        "Haskell says themes in Camassei's paired ceiling frescoes foreshadow a much larger decorative scheme to follow. "
        "The immediately following passage identifies the setting as the principal reception-room; this locates the open scheme "
        "without supplying a title or proving identity with Cortona's individual ceiling fresco or Bracciolini's iconographic programme."
    )
    candidates.append({
        "candidate_id": NEW_CANDIDATE["candidate_id"], "index_entry_id": "", "canonical_name": NEW_CANDIDATE["canonical_name"],
        "index_page_range": "", "suggested_type": NEW_CANDIDATE["suggested_type"], "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": NEW_CANDIDATE["detail"],
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L93",
    })
    for mention_id, candidate_id, surface, start, end, note in NEW_MENTIONS:
        mentions.append({
            "mention_id": mention_id, "segment_id": SEGMENT_ID, "candidate_id": candidate_id,
            "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
        })

    coverage_row = coverage_rows[0]
    note = (
        " 本轮闭合9条旧unset：家族兴盛、Bracciolini品性、Cortona地位、作品接受/解释、方案评价和Sacchi创作性格均保留为非关系判断；"
        "把Sacchi壁画覆盖原主接待室整个天花板单列为作品—空间关系，并将非幻景式表现拆为属性。p.50开放装饰方案cand-11889按紧邻叙述定位于本页主接待厅，"
        "但不与Cortona单件壁画或Bracciolini图像方案合并。Camassei相对失败的评价与持续接收未名小型委托拆开，后者新增开放作品组候选cand-11890。新增2条statement和3条精确mention。"
    )
    if note.strip() not in coverage_row.get("note", ""):
        coverage_row["note"] = coverage_row.get("note", "").rstrip() + note

    payloads = {
        "book-statements.jsonl": serialize_jsonl(statements, raw_by_name["book-statements.jsonl"]),
        "entity-candidates.csv": serialize_csv(candidate_fields, candidates, candidate_raw),
        "mentions.csv": serialize_csv(mention_fields, mentions, mention_raw),
        "s2-coverage.csv": serialize_csv(coverage_fields, coverage, coverage_raw),
    }
    true_count = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements if row.get("segment_id") == SEGMENT_ID)
    false_count = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in statements if row.get("segment_id") == SEGMENT_ID)
    result = {
        "mode": "apply" if args.apply else "preview",
        "segment": SEGMENT_ID,
        "closed_unset_ids": sorted(UNSET_IDS),
        "new_classification_counts_for_unset_rows": {"true": 2, "false": 7},
        "new_statements": sorted(NEW_STATEMENTS),
        "new_candidates": [NEW_CANDIDATE["candidate_id"]],
        "new_mentions": [{"id": item[0], "candidate_id": item[1], "surface": item[2], "span": [item[3], item[4]]} for item in NEW_MENTIONS],
        "segment_total_after": {"true": true_count, "false": false_count, "unset": 0},
        "source_asset_unchanged": True,
        "payload_sha256": {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temps: dict[str, Path] = {}
    try:
        for name, payload in payloads.items():
            path = paths[name]
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
            backups[name] = backup
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
                temp = Path(handle.name)
                handle.write(payload)
            temps[name] = temp
        for name, temp in temps.items():
            os.replace(temp, paths[name])
        if digest(SOURCE) != SOURCE_SHA:
            raise SystemExit("S0 source asset changed during write")
        written = read_jsonl(paths["book-statements.jsonl"])
        written_by_id = {row["statement_id"]: row for row in written}
        if any((written_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is None for sid in UNSET_IDS):
            raise SystemExit("a p.51 classification did not persist")
        if written_by_id[commission_id].get("object_candidate_id") != "cand-11890":
            raise SystemExit("the Camassei commission relation did not persist")
        print(json.dumps({
            "result": "applied",
            "backups": {name: backup.name for name, backup in backups.items()},
            "written_hashes": {name: digest(path) for name, path in paths.items()},
        }, ensure_ascii=False, indent=2))
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for name, backup in backups.items():
            shutil.copy2(backup, paths[name])
        raise


if __name__ == "__main__":
    main()
