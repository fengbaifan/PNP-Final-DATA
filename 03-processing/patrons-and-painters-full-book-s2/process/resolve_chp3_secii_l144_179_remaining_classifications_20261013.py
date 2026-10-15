from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_ii.md"
SEGMENTS = TABLES / "segments.jsonl"
SEGMENT_ID = "chp-3:03_CHP-3_sec_ii:l144-179"
EXPECTED_HASHES = {
    STATEMENTS: "aed4176dbb6e3a58eeb99c67745022ae9cb796452e0e26c9f7924009e37bf6e5",
    CANDIDATES: "e55377108d52e28efbd476ee007a87dd4573cb9badedd452083e5958c8854c83",
    MENTIONS: "11a1e76b287da9698a7784062c12b87c01743f824e703ba0b731f6deae6e5b10",
}
SOURCE_SHA256 = "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6"
SEGMENT_SHA256 = "de9a241370fb7fd1dddc4751917b783158af200ed44c64ab9749fa14cc6325e4"
AUDIENCE_CANDIDATE_ID = "cand-11901"
OTHER_CHURCHES_CANDIDATE_ID = "cand-11902"
OTHER_CHURCHES_MENTION_ID = "m-chp3-p74p76notes-0040"
AUDIENCE_MENTION_ID = "m-chp3-p68note-0002"
OTHER_CHURCHES_SPAN = "other churches belonging to the Orders with frescoes by leading seventeenth-century artists"
FOOTNOTE_IDS = {
    "st-chp3-secii-p66-note1-archive", "st-chp3-secii-p66-note1-baglione", "st-chp3-secii-p66-note1-ugo",
    "st-chp3-secii-p66-note2-review", "st-chp3-secii-p66-note2-zeri", "st-chp3-secii-p66-note3-pecchiai",
    "st-chp3-secii-p67-note1-armellini", "st-chp3-secii-p67-note2-anonymous-life", "st-chp3-secii-p67-note2-necrology",
    "st-chp3-secii-p67-note3-huetter-golzio", "st-chp3-secii-p67-note4-letter", "st-chp3-secii-p67-note4-pirri-publication",
    "st-chp3-secii-p67-note5-novaroli", "st-chp3-secii-p67-note6-med22", "st-chp3-secii-p68-note1-richeome",
    "st-chp3-secii-p68-note2-ponnelle-bordet", "st-chp3-secii-p68-note2-strong", "st-chp3-secii-p69-p70-note1-cozzi",
    "st-chp3-secii-p69-p70-note1-friedlaender", "st-chp3-secii-p70-note2-jaffe", "st-chp3-secii-p70-note3-mahon-citation",
    "st-chp3-secii-p71-note1-cozzi", "st-chp3-secii-p71-note1-ponnelle-bordet", "st-chp3-secii-p71-note2-hibbard",
    "st-chp3-secii-p71-note2-ortolani", "st-chp3-secii-p72-note1-avviso", "st-chp3-secii-p72-note1-orbaan",
    "st-chp3-secii-p72-note2-passeri", "st-chp3-secii-p72-note3-pastor", "st-chp3-secii-p73-note1-felici",
    "st-chp3-secii-p73-note1-pastor", "st-chp3-secii-p73-note2-jesuit-archive", "st-chp3-secii-p73-note5-bellori-citation",
    "st-chp3-secii-p73-note5-pope-hennessy-citation", "st-chp3-secii-p74-note1-soprani", "st-chp3-secii-p74-note2-bricarelli",
    "st-chp3-secii-p74-note2-nappi-ms", "st-chp3-secii-p74-note3-hibbard-1971", "st-chp3-secii-p74-note3-libro-mastro",
    "st-chp3-secii-p74-note3-pollak", "st-chp3-secii-p74-note4-galassi-paluzzi", "st-chp3-secii-p74-note4-libro-mastro-galassi",
    "st-chp3-secii-p75-note1-notizie-storiche", "st-chp3-secii-p75-note2-briganti-date", "st-chp3-secii-p75-note2-pollak-date",
    "st-chp3-secii-p75-note3-passeri", "st-chp3-secii-p75-note4-zeri", "st-chp3-secii-p75-note5-blunt-1979",
    "st-chp3-secii-p75-note5-ehrle", "st-chp3-secii-p76-note1-relatione", "st-chp3-secii-p76-note2-wittkower",
}
NON_CITATION_CLASSIFICATIONS = {
    "st-chp3-secii-p68-note1-andrea-audience": True,
    "st-chp3-secii-p68-note1-vitale-audience": True,
    "st-chp3-secii-p68-note2-source-basis": False,
    "st-chp3-secii-p76-note3-catinari-significance": True,
    "st-chp3-secii-p76-note3-other-order-churches": False,
    "st-chp3-secii-p76-note3-scope-clarification": False,
}
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp3-secii-l144-179-classifications-20261013"),
    CANDIDATES: CANDIDATES.with_name("entity-candidates.csv.bak-s2-chp3-secii-l144-179-open-groups-20261013"),
    MENTIONS: MENTIONS.with_name("mentions.csv.bak-s2-chp3-secii-l144-179-open-groups-20261013"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_csv(raw: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader)


def render_csv(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator=newline, extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    result = output.getvalue().encode("utf-8")
    return b"\xef\xbb\xbf" + result if raw.startswith(b"\xef\xbb\xbf") else result


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify chapter 3 section II footnote residuals and preserve two source-defined groups.")
    parser.add_argument("--apply", action="store_true", help="write changes after protected preview checks")
    args = parser.parse_args()

    raw_by_path = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(raw_by_path[path])
        if actual != expected:
            raise SystemExit(f"protected table changed: {path.name}; expected {expected}, found {actual}")
    if sha256(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise SystemExit("protected S0 source changed")
    segment_rows = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("protected segment metadata changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    if sha256(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("protected source segment changed")
    other_start = segment_text.find(OTHER_CHURCHES_SPAN)
    if other_start != 4120 or segment_text.find(OTHER_CHURCHES_SPAN, other_start + 1) >= 0:
        raise SystemExit(f"protected other-churches mention span changed: {other_start}")
    if segment_text[1451:1465] != "Jesuit novices":
        raise SystemExit("protected Jesuit novices mention span changed")

    statement_rows = [json.loads(line) for line in raw_by_path[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    statement_map = {row.get("statement_id"): row for row in statement_rows}
    expected_ids = FOOTNOTE_IDS | set(NON_CITATION_CLASSIFICATIONS)
    if len(statement_map) != len(statement_rows) or not expected_ids.issubset(statement_map):
        raise SystemExit("target statement set changed")
    segment_unset = {row.get("statement_id") for row in statement_rows if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None}
    if segment_unset != expected_ids:
        raise SystemExit(f"segment unset set changed: expected {len(expected_ids)}, found {len(segment_unset)}")
    for statement_id in expected_ids:
        row = statement_map[statement_id]
        if row.get("segment_id") != SEGMENT_ID:
            raise SystemExit(f"unexpected segment for {statement_id}")
        q = row.get("qualifiers", {})
        cited = " ".join(" ".join(source_lines[int(q["source_line_start"]) - 1:int(q["source_line_end"])]).split())
        quote = " ".join(row.get("original_quote", "").split())
        if quote not in cited:
            raise SystemExit(f"quote does not match cited source lines: {statement_id}")
    for statement_id in FOOTNOTE_IDS:
        row = statement_map[statement_id]
        if row.get("predicate") != "footnote_citation" or not row.get("object_candidate_id"):
            raise SystemExit(f"not a source-only footnote locator: {statement_id}")

    candidate_fields, candidate_rows = load_csv(raw_by_path[CANDIDATES])
    mention_fields, mention_rows = load_csv(raw_by_path[MENTIONS])
    candidate_ids = {row.get("candidate_id") for row in candidate_rows}
    if candidate_ids.intersection({AUDIENCE_CANDIDATE_ID, OTHER_CHURCHES_CANDIDATE_ID}):
        raise SystemExit("one or more new candidate IDs already exist")
    if "cand-5016" not in candidate_ids or "cand-5172" not in candidate_ids:
        raise SystemExit("expected existing novice or S. Carlo candidate is missing")
    mention_ids = {row.get("mention_id") for row in mention_rows}
    if OTHER_CHURCHES_MENTION_ID in mention_ids:
        raise SystemExit("other-churches mention ID already exists")
    audience_mention = next((row for row in mention_rows if row.get("mention_id") == AUDIENCE_MENTION_ID), None)
    if not audience_mention or audience_mention.get("surface_form") != "Jesuit novices" or audience_mention.get("candidate_id") != "cand-5016":
        raise SystemExit("expected existing novices mention mapping changed")

    new_candidates = [
        {
            "candidate_id": AUDIENCE_CANDIDATE_ID,
            "index_entry_id": "",
            "canonical_name": "Jesuit novices as intended audience of S. Andrea al Quirinale and S. Vitale (membership unspecified)",
            "index_page_range": "",
            "suggested_type": "term",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell says the two churches were intended for Jesuit novices rather than the general public. The statement concerns intended audience, not actual access; individual novices and institutional membership are unspecified. Keep distinct from the S. Stefano Rotondo novice group in cand-5016.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": "chp-3:03_CHP-3_sec_ii:l144-179#L154",
        },
        {
            "candidate_id": OTHER_CHURCHES_CANDIDATE_ID,
            "index_entry_id": "",
            "canonical_name": "Other religious-Order churches with frescoes by leading seventeenth-century artists (unnamed group)",
            "index_page_range": "",
            "suggested_type": "term",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell distinguishes these other Order churches from the comparable churches discussed in the body and identifies S. Carlo ai Catinari as the most significant example. The remaining churches and frescoes are not enumerated.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": "chp-3:03_CHP-3_sec_ii:l144-179#L179",
        },
    ]
    if any(set(row) != set(candidate_fields) for row in new_candidates):
        raise SystemExit("candidate schema changed; refusing to append")
    candidate_rows.extend(new_candidates)

    new_mention = {
        "mention_id": OTHER_CHURCHES_MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": OTHER_CHURCHES_CANDIDATE_ID,
        "surface_form": OTHER_CHURCHES_SPAN,
        "start_char": str(other_start),
        "end_char": str(other_start + len(OTHER_CHURCHES_SPAN)),
        "note": "Source-defined unnamed group of other religious-Order churches with frescoes by leading seventeenth-century artists; S. Carlo ai Catinari is then named as the most significant example.",
    }
    if set(new_mention) != set(mention_fields):
        raise SystemExit("mention schema changed; refusing to append")
    mention_rows.append(new_mention)
    audience_mention["candidate_id"] = AUDIENCE_CANDIDATE_ID
    audience_mention["note"] = "Source's stated audience for S. Andrea al Quirinale and S. Vitale; distinct from the particular novice group associated with S. Stefano Rotondo."

    citation_note = "Bibliographic source locator retained through its cited-source candidate and footnote reference; it does not assert a historical or domain relation between distinct entities."
    for statement_id in FOOTNOTE_IDS:
        q = statement_map[statement_id]["qualifiers"]
        q["relation_candidate"] = False
        q["relation_candidate_note"] = citation_note

    for statement_id, is_relation in NON_CITATION_CLASSIFICATIONS.items():
        q = statement_map[statement_id]["qualifiers"]
        q["relation_candidate"] = is_relation

    for statement_id in ["st-chp3-secii-p68-note1-andrea-audience", "st-chp3-secii-p68-note1-vitale-audience"]:
        row = statement_map[statement_id]
        row["object_candidate_id"] = AUDIENCE_CANDIDATE_ID
        row["qualifiers"]["relation_candidate_note"] = "Haskell explicitly distinguishes the intended novice audience from the general public. The audience group is open, and this does not claim actual exclusion or access practice."
        mentioned = row["qualifiers"].setdefault("mentioned_candidate_ids", [])
        for candidate_id in [row["subject_candidate_id"], AUDIENCE_CANDIDATE_ID]:
            if candidate_id and candidate_id not in mentioned:
                mentioned.append(candidate_id)

    source_basis = statement_map["st-chp3-secii-p68-note2-source-basis"]
    source_basis["qualifiers"]["relation_candidate_note"] = "This footnote describes Haskell's method and named source basis; the two cited works remain separately represented as bibliographic locators, not asserted as a historical relation."

    group_description = statement_map["st-chp3-secii-p76-note3-other-order-churches"]
    group_description["subject_candidate_id"] = OTHER_CHURCHES_CANDIDATE_ID
    group_description["qualifiers"]["relation_candidate_note"] = "This footnote describes the source-defined group of other Order churches and their frescoes; no particular church-to-work or church-to-artist edge is asserted in this row."
    mentioned = group_description["qualifiers"].setdefault("mentioned_candidate_ids", [])
    if OTHER_CHURCHES_CANDIDATE_ID not in mentioned:
        mentioned.append(OTHER_CHURCHES_CANDIDATE_ID)
    linked = group_description["qualifiers"].get("linked_body_statement_ids")
    if isinstance(linked, list):
        group_description["qualifiers"]["linked_body_statement_ids"] = list(dict.fromkeys(linked))

    catinari = statement_map["st-chp3-secii-p76-note3-catinari-significance"]
    catinari["object_candidate_id"] = OTHER_CHURCHES_CANDIDATE_ID
    catinari["qualifiers"]["relation_candidate_note"] = "Haskell names S. Carlo ai Catinari as the most significant example in this group of other Order churches with frescoes by leading seventeenth-century artists; 'significant' is limited by the note's comparable-importance clarification."
    mentioned = catinari["qualifiers"].setdefault("mentioned_candidate_ids", [])
    for candidate_id in ["cand-5172", OTHER_CHURCHES_CANDIDATE_ID]:
        if candidate_id not in mentioned:
            mentioned.append(candidate_id)

    scope = statement_map["st-chp3-secii-p76-note3-scope-clarification"]
    scope["qualifiers"]["relation_candidate_note"] = "This is a footnote-level clarification of the comparison's scope, not a separate historical relation."
    linked = scope["qualifiers"].get("linked_body_statement_ids")
    if isinstance(linked, list):
        scope["qualifiers"]["linked_body_statement_ids"] = list(dict.fromkeys(linked))

    statements_rendered = ("\n".join(json.dumps(row, ensure_ascii=False) for row in statement_rows) + "\n").encode("utf-8")
    if raw_by_path[STATEMENTS].startswith(b"\xef\xbb\xbf"):
        statements_rendered = b"\xef\xbb\xbf" + statements_rendered
    rendered = {
        STATEMENTS: statements_rendered,
        CANDIDATES: render_csv(raw_by_path[CANDIDATES], candidate_fields, candidate_rows),
        MENTIONS: render_csv(raw_by_path[MENTIONS], mention_fields, mention_rows),
    }

    print(f"Chapter 3 section II L144–179 preview: {len(FOOTNOTE_IDS)} bibliographic locators -> false")
    for statement_id, is_relation in NON_CITATION_CLASSIFICATIONS.items():
        row = statement_map[statement_id]
        endpoint = f" endpoints={row.get('subject_candidate_id')},{row.get('object_candidate_id')}" if is_relation else ""
        print(f"{statement_id}: {'true' if is_relation else 'false'}{endpoint}")
    for row in new_candidates:
        print(f"candidate: {row['candidate_id']} — {row['canonical_name']} (status=open)")
    print(f"mention remap: {AUDIENCE_MENTION_ID} 'Jesuit novices' -> {AUDIENCE_CANDIDATE_ID}")
    print(f"mention: {OTHER_CHURCHES_MENTION_ID} — [{other_start},{other_start + len(OTHER_CHURCHES_SPAN)})")
    for path, output in rendered.items():
        print(f"{path.relative_to(ROOT)}: {sha256(raw_by_path[path])} -> {sha256(output)}")
    if not args.apply:
        print("mode=preview; no files changed")
        return
    if any(path.exists() for path in BACKUPS.values()):
        raise SystemExit("one or more protected backups already exist")
    for path, output in rendered.items():
        shutil.copy2(path, BACKUPS[path])
        tmp = path.with_name(path.name + ".tmp-s2-chp3-secii-l144-179")
        tmp.write_bytes(output)
        tmp.replace(path)
    print("mode=apply; backups=" + ", ".join(path.name for path in BACKUPS.values()))


if __name__ == "__main__":
    main()
