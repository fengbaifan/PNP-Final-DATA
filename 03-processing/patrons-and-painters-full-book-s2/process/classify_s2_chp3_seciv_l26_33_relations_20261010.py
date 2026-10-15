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
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
PDF = ROOT / "02-sources/01-book/CHP-3.pdf"
PAGE = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/.tmp_chp3_p79_phys21_20261010.png"
SEGMENT = "chp-3:03_CHP-3_sec_iv:l26-33"

EXPECTED = {
    TABLE: "72f98288a1048a6564c99c652da70be98906f9d2cac8a373282ff108f13bac56",
    CANDIDATES: "7bf1eddb481a0382ef5dddc42d9cf0e04adef1e7c3c66d7ebc6d582ca0902864",
    MENTIONS: "e4ee1dc533f4a8ea417f9aefc7a2260954e44b297552ab69a19ace208bbe97ce",
    COVERAGE: "e9c4b793d40f00d6d5cb0952413aae2e7c55787a5a820bfe9dcc27e9159b66cc",
    SOURCE: "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
    PAGE: "f5ebf3b50fd65e8b1f47716bbbf4afe5c16ab42921c938ce4e7a9aee7c13f998",
}

BACKUPS = {
    TABLE: TABLE.with_name(TABLE.name + ".bak-s2-chp3-sec-iv-l26-33-relations-20261010"),
    CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + ".bak-s2-chp3-sec-iv-l26-33-event-endpoint-20261010"),
    MENTIONS: MENTIONS.with_name(MENTIONS.name + ".bak-s2-chp3-sec-iv-l26-33-event-endpoint-20261010"),
}

KEEP_TRUE = {
    "st-chp3-seciv-l26-33-courtois-paints-for-oliva",
    "st-chp3-seciv-l26-33-guglielmo-paints-for-oliva",
}

DECISIONS: dict[str, tuple[bool, str]] = {
    "st-chp3-seciv-l26-33-affair-stalled": (
        True,
        "This refers to Courtois's death in 1676. The death event is the cause and the intended Gesu tribune project is the affected object; the passage says the project stalled, not that it was completed.",
    ),
    "st-chp3-seciv-l26-33-courtois-death-before-project": (
        True,
        "Connects Courtois to the intended tribune project through the explicitly stated death before execution; the preliminary sketches are not identified with the Joshua drawings.",
    ),
    "st-chp3-seciv-l26-33-duchess-favours-artist": (
        True,
        "The Duchess states a preference for her own unnamed artist to paint the vault; preserve the proposed role and do not infer that the artist executed it.",
    ),
    "st-chp3-seciv-l26-33-duchess-rejects-plans": (
        True,
        "Records the Duchess's reported negative response to the Jesuit sketches; this is her reaction to the plans, not evidence that they were adopted.",
    ),
    "st-chp3-seciv-l26-33-duke-delays-over-dome": (
        True,
        "Records Ranuccio's delay and his reported safety objection concerning the Gesu dome; the engineering claim remains attributed to him.",
    ),
    "st-chp3-seciv-l26-33-duke-implied-damage": (
        True,
        "Records Haskell's account of what Ranuccio implied about Jesuit conduct and Cardinal Alessandro's memory; it is not an established fact about damage or disrespect.",
    ),
    "st-chp3-seciv-l26-33-duke-painter-cost-counterfactual": (
        True,
        "Connects the Duke's reluctance to the hypothetical additional painter's fee; Haskell presents this as counterfactual reasoning, not an actual payment.",
    ),
    "st-chp3-seciv-l26-33-duke-professed-anxiety": (
        True,
        "Links Ranuccio's professed wish for decoration to his repeated deferral; preserve the difference between stated concern and readiness to act.",
    ),
    "st-chp3-seciv-l26-33-duke-spending-agreement": (
        True,
        "Records Ranuccio's reluctant agreement to spend 30,000 scudi on the tribune; agreement does not establish payment or execution.",
    ),
    "st-chp3-seciv-l26-33-duke-support-required": (
        True,
        "States that permission and financial support from Ranuccio were essential to the intended project; it does not claim the required support was fully given.",
    ),
    "st-chp3-seciv-l26-33-duke-vacillation": (
        False,
        "Haskell's characterization of the Duke's indecisiveness is an attributed personal assessment, not a relation between two entities.",
    ),
    "st-chp3-seciv-l26-33-earnings-to-society": (
        True,
        "Records the reported encouragement for Courtois to transfer painting earnings to the Jesuit Society; no actual transfer or amount is asserted.",
    ),
    "st-chp3-seciv-l26-33-ignatius-remains-proposed-relocation": (
        True,
        "Records the Jesuits' proposed relocation of the remains as a negotiation proposal; the remains stay an untyped material-object candidate and no transfer is claimed.",
    ),
    "st-chp3-seciv-l26-33-jesuit-belief-in-courtois": (
        True,
        "Records the Jesuits' attributed belief that Courtois could carry out the intended work; it is not an objective claim that no other artist could.",
    ),
    "st-chp3-seciv-l26-33-jesuit-decoration-plans": (
        True,
        "Connects the Jesuits to the plans they sent to persuade Ranuccio; the plans leave the tribune bare and are not evidence of approval or execution.",
    ),
    "st-chp3-seciv-l26-33-jesuit-policy-historical-interpretation": (
        True,
        "Preserves Haskell's interpretation linking the advocacy to a Jesuit arts policy; no named decree or formal policy instrument is identified.",
    ),
    "st-chp3-seciv-l26-33-jesuit-project-intention": (
        True,
        "Records the Jesuits' stated intention to have Courtois decorate the Gesu tribune; the work remained unrealized in this account.",
    ),
    "st-chp3-seciv-l26-33-jesuit-triumph-satisfaction": (
        True,
        "Preserves Haskell's characterization of Jesuit satisfaction and the project's glorifying purpose without treating the intended work as completed.",
    ),
    "st-chp3-seciv-l26-33-jesuits-seek-obligation-release": (
        True,
        "Records the Jesuits' conditional request that Ranuccio release them from obligations if he would not approve the tribune decoration; no release is said to have occurred.",
    ),
    "st-chp3-seciv-l26-33-negotiations-1671": (
        True,
        "Records the Jesuits' 1671 negotiations with Ranuccio. Footnote 1 cites Pecchiai (1952), p. 109, for these and subsequent negotiations; the cited text was not independently checked.",
    ),
    "st-chp3-seciv-l26-33-oliva-advocacy-in-letters": (
        True,
        "Records Haskell's report that Oliva and his emissaries repeatedly advocated Courtois's employment in their letters; the individual letters and emissaries remain unidentified.",
    ),
    "st-chp3-seciv-l26-33-oliva-employment-advocacy": (
        True,
        "Records Oliva's direct advocacy for employing Courtois, preserving the quoted 'our brother' wording and the fact that the work was not executed.",
    ),
    "st-chp3-seciv-l26-33-oliva-encourages-joshua-drawings": (
        True,
        "Records Oliva's encouragement to draw the Joshua subject. Footnote 2 says the subject matches one chosen for Carlone at the Jesuit church in Perugia; it does not establish completion of these drawings.",
    ),
    "st-chp3-seciv-l26-33-private-patron-painting": (
        True,
        "This is a relational claim about encouraging Courtois to continue painting for private patrons, but the encourager and individual patrons are unnamed and no specific commission is asserted; keep the missing endpoint open.",
    ),
    "st-chp3-seciv-l26-33-project-remained-inactive": (
        False,
        "Summarizes the passage of time without progress as a status of the proposed project; it does not assert a separate relation between entities.",
    ),
    "st-chp3-seciv-l26-33-series-battle-content": (
        True,
        "Connects Courtois's Casa Professa painting activity to the explicitly mentioned group of Christian battle scenes; number and titles remain unspecified.",
    ),
    "st-chp3-seciv-l26-33-series-virgin-content": (
        True,
        "Connects Courtois's Casa Professa series to its stated Virgin-glorifying subject; retain the distinction from the battle-scene group.",
    ),
    "st-chp3-seciv-l26-33-tribune-masterpiece": (
        True,
        "Connects Courtois to the intended Gesu tribune decoration as his planned masterpiece; this remains an intention rather than a completed work.",
    ),
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify S2 statements for printed p.79, L27-33.")
    parser.add_argument("--apply", action="store_true", help="Write only after fixed preflight checks pass; default is dry-run.")
    args = parser.parse_args()

    for path, expected in EXPECTED.items():
        require(path.exists() and digest(path) == expected, f"preflight hash changed: {path.relative_to(ROOT)}")
    require(all(not path.exists() for path in BACKUPS.values()), "one or more recovery backups already exist")

    raw_table = TABLE.read_bytes()
    statements = read_jsonl(TABLE)
    require(len(statements) == 12777, "book statement count changed")
    require(len({row["statement_id"] for row in statements}) == len(statements), "statement IDs are not unique")
    by_id = {row["statement_id"]: row for row in statements}
    segment_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    expected_ids = KEEP_TRUE | set(DECISIONS)
    require(len(segment_rows) == 30, "segment statement count changed")
    require({row["statement_id"] for row in segment_rows} == expected_ids, "segment statement set changed")
    require(
        {row["statement_id"] for row in segment_rows if (row.get("qualifiers") or {}).get("relation_candidate") is True} == KEEP_TRUE,
        "preclassified relation statements changed",
    )
    require(
        all((by_id[sid].get("qualifiers") or {}).get("relation_candidate") is None for sid in DECISIONS),
        "one or more target statements already has a decision",
    )

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[25:33])
    for sid in expected_ids:
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        require(isinstance(start, int) and isinstance(end, int), f"source line anchor missing: {sid}")
        span = "\n".join(source_lines[start - 1:end])
        require(normalized(row.get("original_quote", "")) in normalized(span), f"quote/source mismatch: {sid}")

    relation_row = by_id["st-chp3-seciv-l26-33-affair-stalled"]
    require(
        relation_row.get("subject_candidate_id") == "cand-5209" and not relation_row.get("object_candidate_id"),
        "affair-stalled endpoints changed",
    )
    negotiation = by_id["st-chp3-seciv-l26-33-negotiations-1671"]["qualifiers"]
    joshua = by_id["st-chp3-seciv-l26-33-oliva-encourages-joshua-drawings"]["qualifiers"]
    require(
        negotiation.get("footnote_pending") is False
        and negotiation.get("footnote_citation_statement_ids") == ["st-chp3-seciv-notes-l189-204-p79-n1-pecchiai"],
        "footnote 1 linkage changed",
    )
    require(
        joshua.get("footnote_pending") is False
        and joshua.get("footnote_citation_statement_ids") == ["st-chp3-seciv-notes-l189-204-p79-n2-perugia-comparison"],
        "footnote 2 linkage changed",
    )

    candidates, candidate_fields, raw_candidates = read_csv(CANDIDATES)
    mentions, mention_fields, raw_mentions = read_csv(MENTIONS)
    require(len(candidates) == 11578 and len(mentions) == 27518, "candidate or mention row count changed")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    require(max(int(row["candidate_id"].split("-")[1]) for row in candidates) == 11600, "candidate ID cursor changed")
    segment_mentions = [row for row in mentions if row["segment_id"] == SEGMENT]
    require(max(int(row["mention_id"].rsplit("-", 1)[1]) for row in segment_mentions) == 61, "segment mention ID cursor changed")
    event_id = "cand-11601"
    new_mention_ids = {
        "m-chp3-seciv-l26-33-0062",
        "m-chp3-seciv-l26-33-0063",
    }
    require(event_id not in candidate_by_id, "event candidate ID already exists")
    require(not (new_mention_ids & mention_by_id.keys()), "one or more event mention IDs already exist")
    require(all(event_id not in row.values() for row in mentions), "event candidate already has a mention")

    coverage, _, _ = read_csv(COVERAGE)
    cov = next((row for row in coverage if row["segment_id"] == SEGMENT), None)
    require(
        cov is not None
        and cov["disposition"] == "reviewed"
        and cov["migration_status"] == "complete"
        and cov["source_line_ranges"] == "L27-33"
        and "Footnotes 1-2 are migrated and linked to notes L195-196." in cov["note"],
        "coverage status or footnote linkage changed",
    )

    candidate_add = {
        "candidate_id": event_id,
        "index_entry_id": "",
        "canonical_name": "Death of Jacques Courtois (1676)",
        "index_page_range": "",
        "suggested_type": "event",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell states that Courtois died in 1676 after preliminary sketches existed. The next sentence's 'This' attributes the Gesu tribune affair's stoppage to that death. Keep the event distinct from the person and do not infer project completion.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L31",
    }
    candidates.append(candidate_add)

    mention_add = []
    for mention_id, surface, search_text, note in [
        (
            "m-chp3-seciv-l26-33-0062",
            "Borgognone died",
            "In 1676, with the preliminary sketches made but with no opportunity to achieve his masterpiece, Borgognone died.",
            "Lexical mention of the 1676 death event, distinct from the existing person mention.",
        ),
        (
            "m-chp3-seciv-l26-33-0063",
            "This",
            "This brought the affair to a standstill.",
            "Pronoun resolved to Courtois's death in the preceding sentence; it is the cause of the stated project stoppage.",
        ),
    ]:
        start = segment_text.index(search_text)
        surface_start = start + search_text.index(surface)
        mention_add.append({
            "mention_id": mention_id,
            "segment_id": SEGMENT,
            "candidate_id": event_id,
            "surface_form": surface,
            "start_char": str(surface_start),
            "end_char": str(surface_start + len(surface)),
            "note": note,
        })
    mentions.extend(mention_add)

    for sid, (is_relation, note) in DECISIONS.items():
        row = by_id[sid]
        q = dict(row.get("qualifiers") or {})
        q["relation_candidate"] = is_relation
        q["relation_candidate_note"] = note
        row["qualifiers"] = q

    relation_row["subject_candidate_id"] = event_id
    relation_row["object_candidate_id"] = "cand-5209"
    relation_row["predicate"] = "brought_to_standstill"
    affair_q = dict(relation_row.get("qualifiers") or {})
    affair_q["claim"] = "Courtois's death in 1676 brought the Gesu tribune decoration affair to a standstill."
    affair_q["relation_candidate"] = True
    affair_q["relation_candidate_note"] = DECISIONS["st-chp3-seciv-l26-33-affair-stalled"][1]
    affair_q["referent"] = "“This” refers to the death event cand-11601 in the preceding sentence."
    relation_row["qualifiers"] = affair_q

    negotiation_row = by_id["st-chp3-seciv-l26-33-negotiations-1671"]
    negotiation_q = dict(negotiation_row.get("qualifiers") or {})
    negotiation_q["qualification"] = (
        "Footnote 1 cites Pecchiai (1952), p. 109, for these and subsequent negotiations; the cited text was not independently checked."
    )
    negotiation_row["qualifiers"] = negotiation_q

    joshua_row = by_id["st-chp3-seciv-l26-33-oliva-encourages-joshua-drawings"]
    joshua_q = dict(joshua_row.get("qualifiers") or {})
    joshua_q["qualification"] = (
        "Encouragement is stated, but these drawings' completion is not. Footnote 2 says the subject matches one chosen for Carlone at the Jesuit church in Perugia; Carlone's personal identity remains unresolved in this passage."
    )
    joshua_row["qualifiers"] = joshua_q

    after_segment = [row for row in statements if row.get("segment_id") == SEGMENT]
    require(
        sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in after_segment) == 28
        and sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in after_segment) == 2
        and all((row.get("qualifiers") or {}).get("relation_candidate") is not None for row in after_segment),
        "planned segment decisions do not close all 30 statements",
    )
    require(
        sum(bool(row.get("subject_candidate_id")) and bool(row.get("object_candidate_id")) for row in after_segment) == 27,
        "planned endpoint mapping is unexpected",
    )

    payloads = {
        TABLE: encode_jsonl(statements, raw_table),
        CANDIDATES: encode_csv(candidates, candidate_fields, raw_candidates),
        MENTIONS: encode_csv(mentions, mention_fields, raw_mentions),
    }
    all_after = [row for row in statements]
    bilateral = [row for row in all_after if row.get("subject_candidate_id") and row.get("object_candidate_id")]
    total_relations = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in all_after)
    bilateral_relations = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in bilateral)
    bilateral_nonrelations = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in bilateral)
    bilateral_pending = sum((row.get("qualifiers") or {}).get("relation_candidate") is None for row in bilateral)
    open_relations = total_relations - bilateral_relations

    print(
        "DRY_RUN" if not args.apply else "APPLY",
        f"segment_statements={len(after_segment)} relation_candidates=28 nonrelations=2 unresolved=0",
    )
    print(f"new_candidates=1 new_mentions=2 bilateral={len(bilateral)} bilateral_relations={bilateral_relations} bilateral_nonrelations={bilateral_nonrelations} bilateral_pending={bilateral_pending}")
    print(f"total_relation_candidates={total_relations} open_endpoint_relation_candidates={open_relations}")
    print("statement_updates=28 endpoint_repair=1 footnote_qualification_repairs=2")
    for sid, (flag, note) in DECISIONS.items():
        print(f"  {sid}: relation_candidate={str(flag).lower()} | {note}")

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
    require(len(written_statements) == 12777 and len(written_candidates) == 11579 and len(written_mentions) == 27520, "postwrite row count mismatch")
    require(
        sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in written_segment) == 28
        and sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in written_segment) == 2,
        "postwrite segment classification mismatch",
    )
    require(
        written_by_id["st-chp3-seciv-l26-33-affair-stalled"]["subject_candidate_id"] == event_id
        and written_by_id["st-chp3-seciv-l26-33-affair-stalled"]["object_candidate_id"] == "cand-5209",
        "postwrite affair endpoints mismatch",
    )
    require(
        all(digest(backup) for backup in BACKUPS.values()),
        "a recovery backup is missing",
    )
    print("POSTWRITE_OK", "statements=12777 candidates=11579 mentions=27520")
    for path in (TABLE, CANDIDATES, MENTIONS):
        print("SHA256", digest(path), path.relative_to(ROOT))


if __name__ == "__main__":
    main()
