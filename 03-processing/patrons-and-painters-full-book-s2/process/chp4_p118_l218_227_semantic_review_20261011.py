#!/usr/bin/env python3
"""Review p.118 statements, candidates, and mention mappings with guarded writes."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
SOURCE_REL = "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l218-227"
NOTE_SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l232-308"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
SEGMENT_SHA256 = "3922ec038be7e6611d566a5b7b754e3cb72a922269fed175f675842adb3b3456"
NOTE_SEGMENT_SHA256 = "792d95e61aab35b3bfb639af2364220365d26076eeafb93e545526ccf302ca7e"
EXPECTED_SHA256 = {
    "book-statements.jsonl": "d94d24e2260e4c40c53b2de4126a65b19646518a05869b38d1cb7277b9cc2fb3",
    "entity-candidates.csv": "39046c5e01513d61313ccd0ff66761b1e804909362d664f5cdbd50fe781ecd8e",
    "mentions.csv": "aa4aaae721509c9bd6f3ab6eab16e56ce9b2aeb494ec0ee82192bd72786e5a5a",
}
BACKUP_SUFFIX = "bak-s2-chp4-p118-semantic-20261011"

BODY_IDS = {
    "st-chp4-sec-ii-p118-altieri-palace-supervision",
    "st-chp4-sec-ii-p118-apollo-daphne-title",
    "st-chp4-sec-ii-p118-bartoli-copied-illustrations",
    "st-chp4-sec-ii-p118-bartoli-copy-enterprise",
    "st-chp4-sec-ii-p118-brother-inherited-estate",
    "st-chp4-sec-ii-p118-brother-liquidated-collections",
    "st-chp4-sec-ii-p118-claude-two-paintings",
    "st-chp4-sec-ii-p118-claude-work-access",
    "st-chp4-sec-ii-p118-clement-x-appointments",
    "st-chp4-sec-ii-p118-coast-view-title",
    "st-chp4-sec-ii-p118-collectors-increasingly-rare",
    "st-chp4-sec-ii-p118-delphi-chosen-for-massimi",
    "st-chp4-sec-ii-p118-delphi-work-source",
    "st-chp4-sec-ii-p118-fresco-papal-allusion",
    "st-chp4-sec-ii-p118-grimani-praise",
    "st-chp4-sec-ii-p118-king-france-purchase",
    "st-chp4-sec-ii-p118-last-service-and-death",
    "st-chp4-sec-ii-p118-leading-patrons-characterization",
    "st-chp4-sec-ii-p118-maratta-fresco-opportunity",
    "st-chp4-sec-ii-p118-maratta-other-commissions",
    "st-chp4-sec-ii-p118-maratta-portrait",
    "st-chp4-sec-ii-p118-massimi-fortunes-1670",
    "st-chp4-sec-ii-p118-massimi-owned-poussin-drawing",
    "st-chp4-sec-ii-p118-mead-purchase",
    "st-chp4-sec-ii-p118-poussin-drawing-depicts-coast-view",
    "st-chp4-sec-ii-p118-poussin-drawing-volume",
    "st-chp4-sec-ii-p118-transaction-symbolic",
    "st-chp4-sec-ii-p118-umoristi-reorganized",
    "st-chp4-sec-ii-p118-viceroy-naples-purchase",
}
NOTE_IDS = {
    "st-chp4-sec-ii-p118note-fn1-bellori",
    "st-chp4-sec-ii-p118note-fn1-blunt",
    "st-chp4-sec-ii-p118note-fn2-grimani-citation",
    "st-chp4-sec-ii-p118note-fn3-chapter6-crossref",
    "st-chp4-sec-ii-p118note-fn4-giustiniani",
    "st-chp4-sec-ii-p118note-fn5-cortona-origin",
    "st-chp4-sec-ii-p118note-fn5-locations",
    "st-chp4-sec-ii-p118note-fn5-rothlisberger",
    "st-chp4-sec-ii-p118note-fn6-denolhac",
    "st-chp4-sec-ii-p118note-fn6-plates-history",
}

TRUE_RELATIONS = {
    "st-chp4-sec-ii-p118-altieri-palace-supervision": "Altieri family requested a defined supervisory role from Massimi.",
    "st-chp4-sec-ii-p118-apollo-daphne-title": "Connects Poussin to his named unfinished work.",
    "st-chp4-sec-ii-p118-bartoli-copied-illustrations": "Records the creator of the source-bounded copy set.",
    "st-chp4-sec-ii-p118-bartoli-copy-enterprise": "Records Massimi as commissioner of the copy set.",
    "st-chp4-sec-ii-p118-brother-inherited-estate": "Records inheritance from Massimi to his unnamed brother.",
    "st-chp4-sec-ii-p118-brother-liquidated-collections": "Records disposal of the inherited collections to meet debts.",
    "st-chp4-sec-ii-p118-claude-two-paintings": "Records the two-work group’s creator.",
    "st-chp4-sec-ii-p118-claude-work-access": "Records the explicitly described opportunity to obtain further work from Claude.",
    "st-chp4-sec-ii-p118-clement-x-appointments": "Records Massimi’s appointments by Clement X.",
    "st-chp4-sec-ii-p118-coast-view-title": "Identifies Claude as creator of the named painting.",
    "st-chp4-sec-ii-p118-delphi-chosen-for-massimi": "Records the patron’s selection of the Delphi painting.",
    "st-chp4-sec-ii-p118-delphi-work-source": "Records the painting’s literary source in Justinus.",
    "st-chp4-sec-ii-p118-fresco-papal-allusion": "Records the fresco’s stated allusion to Clement X’s assumed name.",
    "st-chp4-sec-ii-p118-grimani-praise": "Records Grimani’s attributed praise of Massimi.",
    "st-chp4-sec-ii-p118-king-france-purchase": "Records a named purchaser and the source-bounded estate-object group.",
    "st-chp4-sec-ii-p118-maratta-fresco-opportunity": "Records Massimi’s role in obtaining the fresco opportunity for Maratta.",
    "st-chp4-sec-ii-p118-maratta-other-commissions": "Records the commission of an unnamed group of Maratta works.",
    "st-chp4-sec-ii-p118-maratta-portrait": "Records Maratta as creator of Massimi’s portrait.",
    "st-chp4-sec-ii-p118-massimi-owned-poussin-drawing": "Records Massimi’s ownership of the Poussin drawing.",
    "st-chp4-sec-ii-p118-mead-purchase": "Records a named purchaser and the source-bounded estate-object group.",
    "st-chp4-sec-ii-p118-poussin-drawing-depicts-coast-view": "Records the drawing’s mythological subject, not a depiction of Claude’s painting.",
    "st-chp4-sec-ii-p118-poussin-drawing-volume": "Records Massimi’s acquisition of the volume from Marino’s successors.",
    "st-chp4-sec-ii-p118-umoristi-reorganized": "Records Massimi’s reorganization of the academy.",
    "st-chp4-sec-ii-p118-viceroy-naples-purchase": "Records a named purchaser and the source-bounded estate-object group.",
    "st-chp4-sec-ii-p118note-fn5-cortona-origin": "Records Cassiano’s earlier ownership of the Cortona painting.",
    "st-chp4-sec-ii-p118note-fn5-locations": "Records a group-level current-location claim without assigning either painting to either repository.",
}
FALSE_RELATIONS = {
    "st-chp4-sec-ii-p118-collectors-increasingly-rare": "Scalar historical characterization of a group; no inter-entity relation is asserted.",
    "st-chp4-sec-ii-p118-last-service-and-death": "Chronology and authorial characterization, not an inter-entity relation.",
    "st-chp4-sec-ii-p118-leading-patrons-characterization": "Scalar historical characterization of a patron group, completed by p.119.",
    "st-chp4-sec-ii-p118-massimi-fortunes-1670": "Scalar biographical chronology.",
    "st-chp4-sec-ii-p118-transaction-symbolic": "Authorial interpretation of an event, not an inter-entity relation.",
    "st-chp4-sec-ii-p118note-fn1-bellori": "Bibliographic citation locator only.",
    "st-chp4-sec-ii-p118note-fn1-blunt": "Bibliographic citation locator only.",
    "st-chp4-sec-ii-p118note-fn2-grimani-citation": "Citation locator for the attributed quotation; not a domain relation.",
    "st-chp4-sec-ii-p118note-fn3-chapter6-crossref": "Internal chapter cross-reference only.",
    "st-chp4-sec-ii-p118note-fn4-giustiniani": "Bibliographic citation locator only.",
    "st-chp4-sec-ii-p118note-fn5-rothlisberger": "Bibliographic citation locator only.",
    "st-chp4-sec-ii-p118note-fn6-denolhac": "Bibliographic citation locator only.",
    "st-chp4-sec-ii-p118note-fn6-plates-history": "Scalar publication chronology; the Bottari text authorship is split into its own relation statement.",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def norm(text: str) -> str:
    return " ".join(text.split())


def unique_span(text: str, needle: str) -> tuple[int, int]:
    start = text.find(needle)
    if start < 0 or text.find(needle, start + 1) >= 0:
        raise SystemExit(f"source phrase absent or ambiguous: {needle!r}")
    return start, start + len(needle)


def quote(text: str, phrase: str) -> str:
    unique_span(text, phrase)
    return phrase


def excerpt(text: str, start: str, end: str) -> str:
    left = text.find(start)
    if left < 0 or text.find(start, left + 1) >= 0:
        raise SystemExit(f"source excerpt start absent or ambiguous: {start!r}")
    right = text.find(end, left + len(start))
    if right < 0:
        raise SystemExit(f"source excerpt end absent: {end!r}")
    return text[left:right + len(end)]


def make_candidate(cid: int, name: str, typ: str, detail: str, ref: str) -> dict[str, str]:
    return {
        "candidate_id": f"cand-{cid}", "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": typ, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": ref,
    }


def make_statement(
    sid: str, segment_id: str, subject: str | None, obj: str | None,
    predicate: str, quote: str, start: int, end: int, claim: str,
    relation: bool, relation_note: str, mentioned: list[str], *,
    note_marker: int | None = None, note_line: int | None = None,
    note_ids: list[str] | None = None, extra: dict | None = None,
) -> dict:
    is_body = segment_id == SEGMENT_ID
    qualifiers = {
        "source_line_start": start, "source_line_end": end,
        "pdf_physical_page": 29, "printed_page_locator": "p.118",
        "claim": claim, "speaker": "Haskell" if is_body else "Haskell's footnote",
        "text_layer": "authorial narrative" if is_body else "authorial footnote claim",
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation, "relation_candidate_note": relation_note,
    }
    if note_marker is not None:
        qualifiers.update({
            "footnote_marker": note_marker, "footnote_segment": NOTE_SEGMENT_ID,
            "footnote_source_line": note_line, "footnote_link_status": "linked",
        })
    if note_ids:
        qualifiers["footnote_statement_ids"] = note_ids
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": sid, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote, "origin": "book", "source_file": SOURCE_REL,
    }


def transform_statements(original: bytes, updates: dict[str, dict], additions: list[dict], eol: bytes) -> bytes:
    output: list[bytes] = []
    found: set[str] = set()
    for raw in original.splitlines(keepends=True):
        line = raw.rstrip(b"\r\n")
        if not line:
            output.append(raw)
            continue
        row = json.loads(line.decode("utf-8"))
        sid = row["statement_id"]
        if sid in updates:
            if sid in found:
                raise SystemExit(f"duplicate statement ID: {sid}")
            patch = updates[sid]
            for key, value in patch.items():
                if key == "qualifiers":
                    row["qualifiers"].update(value)
                else:
                    row[key] = value
            output.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + (raw[len(line):] or eol))
            found.add(sid)
        else:
            output.append(raw)
    if found != set(updates):
        raise SystemExit(f"statements missing: {sorted(set(updates) - found)}")
    if output and not output[-1].endswith((b"\n", b"\r")):
        output[-1] += eol
    output.extend(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + eol for row in additions)
    return b"".join(output)


def append_csv(original: bytes, rows: list[dict]) -> bytes:
    if not rows:
        return original
    headers = next(csv.reader(io.StringIO(original.decode("utf-8-sig"), newline="")))
    eol = "\r\n" if b"\r\n" in original else "\n"
    buffer = io.StringIO(newline="")
    csv.DictWriter(buffer, fieldnames=headers, extrasaction="raise", lineterminator=eol).writerows(rows)
    if not original.endswith((b"\n", b"\r")):
        original += eol.encode("ascii")
    return original + buffer.getvalue().encode("utf-8")


def transform_candidates(original: bytes, updates: dict[str, dict], additions: list[dict]) -> bytes:
    eol_text = "\r\n" if b"\r\n" in original else "\n"
    lines = original.decode("utf-8-sig").splitlines(keepends=True)
    header_line = lines[0]
    header = next(csv.reader([header_line.rstrip("\r\n")]))
    output = [original.splitlines(keepends=True)[0]]
    found: set[str] = set()
    for raw in lines[1:]:
        ending = "\r\n" if raw.endswith("\r\n") else ("\n" if raw.endswith("\n") else "")
        values = next(csv.reader([raw.rstrip("\r\n")]))
        row = dict(zip(header, values))
        cid = row["candidate_id"]
        if cid in updates:
            if cid in found:
                raise SystemExit(f"duplicate candidate ID: {cid}")
            patch = updates[cid]
            for key, expected in patch["expected"].items():
                if row.get(key) != expected:
                    raise SystemExit(f"unexpected {cid}.{key}: {row.get(key)!r}")
            row.update(patch["set"])
            buffer = io.StringIO(newline="")
            csv.DictWriter(buffer, fieldnames=header, extrasaction="raise", lineterminator=ending or eol_text).writerow(row)
            output.append(buffer.getvalue().encode("utf-8"))
            found.add(cid)
        else:
            output.append(raw.encode("utf-8"))
    if found != set(updates):
        raise SystemExit(f"candidate rows missing: {sorted(set(updates) - found)}")
    return append_csv(b"".join(output), additions)


def transform_mentions(original: bytes, replacements: dict[str, tuple[str, str]], note_updates: dict[str, str], removals: set[str], additions: list[dict]) -> bytes:
    eol = b"\r\n" if b"\r\n" in original else b"\n"
    text = original.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    header = next(csv.reader([lines[0].rstrip("\r\n")]))
    id_i, candidate_i, note_i = header.index("mention_id"), header.index("candidate_id"), header.index("note")
    found: set[str] = set()
    output: list[bytes] = [lines[0].encode("utf-8")]
    for raw in lines[1:]:
        ending = "\r\n" if raw.endswith("\r\n") else ("\n" if raw.endswith("\n") else "")
        values = next(csv.reader([raw.rstrip("\r\n")]))
        mid = values[id_i]
        if mid in removals:
            if mid in found:
                raise SystemExit(f"duplicate mention ID: {mid}")
            found.add(mid)
            continue
        changed = False
        if mid in replacements:
            old, new = replacements[mid]
            if values[candidate_i] != old:
                raise SystemExit(f"unexpected candidate for {mid}: {values[candidate_i]}")
            values[candidate_i] = new
            found.add(mid)
            changed = True
        if mid in note_updates:
            values[note_i] = note_updates[mid]
            found.add(mid)
            changed = True
        if changed:
            buffer = io.StringIO(newline="")
            csv.writer(buffer, lineterminator=ending).writerow(values)
            output.append(buffer.getvalue().encode("utf-8"))
        else:
            output.append(raw.encode("utf-8"))
    expected = set(replacements) | set(note_updates) | removals
    if found != expected:
        raise SystemExit(f"mention rows missing/duplicated: {sorted(expected ^ found)}")
    buf = io.StringIO(newline="")
    csv.DictWriter(buf, fieldnames=header, extrasaction="raise", lineterminator=eol.decode("ascii")).writerows(additions)
    if additions:
        if output and not output[-1].endswith((b"\n", b"\r")):
            output[-1] += eol
        output.append(buf.getvalue().encode("utf-8"))
    return b"".join(output)


def prepare() -> tuple[dict[str, Path], dict[str, bytes], dict[str, bytes], dict]:
    paths = {
        "book-statements.jsonl": TABLES / "book-statements.jsonl",
        "entity-candidates.csv": TABLES / "entity-candidates.csv",
        "mentions.csv": TABLES / "mentions.csv",
    }
    original = {name: path.read_bytes() for name, path in paths.items()}
    for name, expected in EXPECTED_SHA256.items():
        actual = digest(original[name])
        if actual != expected:
            raise SystemExit(f"{name}: SHA-256 changed; expected {expected}, got {actual}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    body = "\n".join(source_lines[217:227])
    note = "\n".join(source_lines[231:308])
    if digest(SOURCE.read_bytes()) != SOURCE_SHA256 or digest(body.encode("utf-8")) != SEGMENT_SHA256 or digest(note.encode("utf-8")) != NOTE_SEGMENT_SHA256:
        raise SystemExit("source or p.118/note segment changed")

    with (TABLES / "s2-coverage.csv").open(encoding="utf-8-sig", newline="") as f:
        coverage = {row["segment_id"]: row for row in csv.DictReader(f)}
    if coverage.get(SEGMENT_ID, {}).get("disposition") != "reviewed" or coverage.get(NOTE_SEGMENT_ID, {}).get("migration_status") != "complete":
        raise SystemExit("p.118 body or linked footnote segment is not available as reviewed input")

    current_rows = [json.loads(x) for x in original["book-statements.jsonl"].decode("utf-8").splitlines() if x]
    body_rows = [r for r in current_rows if r.get("segment_id") == SEGMENT_ID]
    note_rows = [r for r in current_rows if r.get("segment_id") == NOTE_SEGMENT_ID and r.get("statement_id", "").startswith("st-chp4-sec-ii-p118note-")]
    if {r["statement_id"] for r in body_rows} != BODY_IDS or {r["statement_id"] for r in note_rows} != NOTE_IDS:
        raise SystemExit("p.118 statement set changed")
    if set(TRUE_RELATIONS) | set(FALSE_RELATIONS) != BODY_IDS | NOTE_IDS or set(TRUE_RELATIONS) & set(FALSE_RELATIONS):
        raise SystemExit("classification map does not cover p.118 body and linked-note statements exactly")

    updates: dict[str, dict] = {}
    for sid, note_text in TRUE_RELATIONS.items():
        updates[sid] = {"qualifiers": {"relation_candidate": True, "relation_candidate_note": note_text}}
    for sid, note_text in FALSE_RELATIONS.items():
        updates[sid] = {"qualifiers": {"relation_candidate": False, "relation_candidate_note": note_text}}

    def upd(sid: str, **fields: object) -> None:
        patch = updates.setdefault(sid, {})
        for key, value in fields.items():
            if key == "qualifiers":
                patch.setdefault("qualifiers", {}).update(value)  # type: ignore[arg-type]
            else:
                patch[key] = value

    note1 = ["st-chp4-sec-ii-p118note-fn1-bellori", "st-chp4-sec-ii-p118note-fn1-blunt"]
    note2 = ["st-chp4-sec-ii-p118note-fn2-grimani-citation"]
    note3 = ["st-chp4-sec-ii-p118note-fn3-chapter6-crossref"]
    note4 = ["st-chp4-sec-ii-p118note-fn4-giustiniani"]
    note5 = ["st-chp4-sec-ii-p118note-fn5-cortona-origin", "st-chp4-sec-ii-p118note-fn5-locations", "st-chp4-sec-ii-p118note-fn5-rothlisberger"]
    note6 = ["st-chp4-sec-ii-p118note-fn6-plates-history", "st-chp4-sec-ii-p118note-fn6-denolhac"]

    # Repair source-bounded mappings and represent the supported relation direction.
    upd("st-chp4-sec-ii-p118-altieri-palace-supervision",
        subject_candidate_id="cand-6461",
        original_quote=excerpt(body, "he was asked by the Altieri", "nearly half a century earlier"),
        qualifiers={"claim": "The Altieri family asked Massimi to superintend their new palace decoration; Haskell compares this kind of post with Cardinal Bentivoglio’s role nearly half a century earlier.", "mentioned_candidate_ids": ["cand-6461", "cand-1564", "cand-0090", "cand-0291"]})
    upd("st-chp4-sec-ii-p118-apollo-daphne-title",
        qualifiers={"claim": "The unfinished Poussin work discussed across p.117–118 is identified as Apollo and Daphne.", "mentioned_candidate_ids": ["cand-1984", "cand-5988", "cand-11669"], "footnote_marker": 1, "footnote_segment": NOTE_SEGMENT_ID, "footnote_source_line": 303, "footnote_link_status": "linked", "footnote_statement_ids": note1, "ocr_corrections": [{"source_line": 219, "source_form": "os", "print_form": "of"}]})
    upd("st-chp4-sec-ii-p118-clement-x-appointments",
        subject_candidate_id="cand-1564", object_candidate_id="cand-0087", predicate="appointed_by",
        qualifiers={"claim": "In 1670 Pope Clement X appointed Massimi both Cardinal and Maestro di Camera.", "mentioned_candidate_ids": ["cand-1564", "cand-0087"], "role": ["Cardinal", "Maestro di Camera"]})
    upd("st-chp4-sec-ii-p118-maratta-other-commissions",
        subject_candidate_id="cand-11675", object_candidate_id="cand-1564", predicate="commissioned_by",
        original_quote=excerpt(body, "He commissioned several other works", "his favourite"),
        qualifiers={"claim": "Massimi commissioned several otherwise unidentified works by Carlo Maratta, who was then his favourite artist.", "mentioned_candidate_ids": ["cand-11675", "cand-1564", "cand-1526"]})
    upd("st-chp4-sec-ii-p118-maratta-portrait",
        subject_candidate_id="cand-5989", object_candidate_id="cand-1526", predicate="created_by",
        qualifiers={"claim": "Carlo Maratta painted Massimi’s portrait on the occasion of his appointments.", "mentioned_candidate_ids": ["cand-5989", "cand-1526", "cand-1564"], "footnote_marker": 2, "footnote_segment": NOTE_SEGMENT_ID, "footnote_source_line": 304, "footnote_link_status": "linked", "footnote_statement_ids": note2})
    upd("st-chp4-sec-ii-p118-delphi-work-source",
        subject_candidate_id="cand-5991", object_candidate_id="cand-1337", predicate="derived_from",
        qualifiers={"claim": "The subject of Claude’s View of Delphi with a Procession is taken from the historian Justinus.", "mentioned_candidate_ids": ["cand-5991", "cand-1337"]})
    upd("st-chp4-sec-ii-p118-fresco-papal-allusion",
        original_quote=excerpt(body, "This decoration, based on a punning allusion", "name assumed by the Pope"),
        qualifiers={"claim": "The fresco is based on a punning allusion to the name assumed by Pope Clement X.", "mentioned_candidate_ids": ["cand-5990", "cand-0087"], "footnote_marker": 3, "footnote_segment": NOTE_SEGMENT_ID, "footnote_source_line": 305, "footnote_link_status": "linked", "footnote_statement_ids": note3})
    upd("st-chp4-sec-ii-p118-maratta-fresco-opportunity",
        qualifiers={"mentioned_candidate_ids": ["cand-1564", "cand-1526", "cand-5990"], "footnote_marker": 3, "footnote_segment": NOTE_SEGMENT_ID, "footnote_source_line": 305, "footnote_link_status": "linked", "footnote_statement_ids": note3, "ocr_corrections": [{"source_line": 221, "source_form": "ceding", "print_form": "ceiling"}]})
    upd("st-chp4-sec-ii-p118-grimani-praise",
        qualifiers={"mentioned_candidate_ids": ["cand-6003", "cand-1564"], "footnote_marker": 2, "footnote_segment": NOTE_SEGMENT_ID, "footnote_source_line": 304, "footnote_link_status": "linked", "footnote_statement_ids": note2})
    upd("st-chp4-sec-ii-p118-claude-two-paintings",
        subject_candidate_id="cand-11670", object_candidate_id="cand-0767", predicate="created_by",
        qualifiers={"claim": "Claude painted the two source-named pictures in 1673 and 1674; Haskell says they continued his practice of choosing pagan subjects for Massimi.", "mentioned_candidate_ids": ["cand-11670", "cand-0767", "cand-1564", "cand-5991", "cand-5992"], "footnote_marker": 5, "footnote_segment": NOTE_SEGMENT_ID, "footnote_source_line": 307, "footnote_link_status": "linked", "footnote_statement_ids": note5})
    upd("st-chp4-sec-ii-p118-coast-view-title",
        subject_candidate_id="cand-5992", object_candidate_id="cand-0767", predicate="created_by",
        qualifiers={"claim": "The second painting named in the pair is Claude’s A Coast View with Perseus and the Origin of Coral.", "mentioned_candidate_ids": ["cand-5992", "cand-0767", "cand-1564", "cand-11673"], "source_line_start": 222, "source_line_end": 223, "footnote_marker": 5, "footnote_segment": NOTE_SEGMENT_ID, "footnote_source_line": 307, "footnote_link_status": "linked", "footnote_statement_ids": note5})
    upd("st-chp4-sec-ii-p118-delphi-chosen-for-massimi",
        qualifiers={"mentioned_candidate_ids": ["cand-1564", "cand-5991"], "footnote_marker": 5, "footnote_segment": NOTE_SEGMENT_ID, "footnote_source_line": 307, "footnote_link_status": "linked", "footnote_statement_ids": note5})
    upd("st-chp4-sec-ii-p118-bartoli-copied-illustrations",
        subject_candidate_id="cand-11672", object_candidate_id="cand-0251", predicate="created_by",
        qualifiers={"claim": "Pietro Santo Bartoli made the source-bounded set of copies of illustrations from the late antique Virgil manuscript.", "mentioned_candidate_ids": ["cand-11672", "cand-0251", "cand-5995", "cand-4380", "cand-2777"], "footnote_marker": 6, "footnote_segment": NOTE_SEGMENT_ID, "footnote_source_line": 308, "footnote_link_status": "linked", "footnote_statement_ids": note6})
    upd("st-chp4-sec-ii-p118-bartoli-copy-enterprise",
        subject_candidate_id="cand-11672", object_candidate_id="cand-1564", predicate="commissioned_by",
        qualifiers={"claim": "Massimi arranged for Bartoli to make copies of illustrations from the late antique Virgil manuscript in 1677.", "mentioned_candidate_ids": ["cand-11672", "cand-1564", "cand-0251", "cand-5995", "cand-4380", "cand-2777"], "footnote_marker": 6, "footnote_segment": NOTE_SEGMENT_ID, "footnote_source_line": 308, "footnote_link_status": "linked", "footnote_statement_ids": note6, "ocr_corrections": [{"source_line": 226, "source_form": "fllustrations", "print_form": "illustrations"}, {"source_line": 226, "source_form": "one of the-oldest", "print_form": "one of the oldest"}]})
    upd("st-chp4-sec-ii-p118-brother-inherited-estate",
        qualifiers={"mentioned_candidate_ids": ["cand-5996", "cand-1564", "cand-5997"]})
    upd("st-chp4-sec-ii-p118-brother-liquidated-collections",
        qualifiers={"mentioned_candidate_ids": ["cand-5996", "cand-5997", "cand-1564"]})
    upd("st-chp4-sec-ii-p118-last-service-and-death",
        qualifiers={"mentioned_candidate_ids": ["cand-1564", "cand-11672"], "footnote_marker": 6, "footnote_segment": NOTE_SEGMENT_ID, "footnote_source_line": 308, "footnote_link_status": "linked", "footnote_statement_ids": note6})
    upd("st-chp4-sec-ii-p118-poussin-drawing-depicts-coast-view",
        subject_candidate_id="cand-5993", object_candidate_id="cand-11673", predicate="has_subject",
        qualifiers={"claim": "The Poussin drawing depicts the Origin of Coral subject shared with Claude’s Coast View; it does not depict Claude’s painting.", "mentioned_candidate_ids": ["cand-5993", "cand-5992", "cand-11673"], "footnote_marker": 5, "footnote_segment": NOTE_SEGMENT_ID, "footnote_source_line": 307, "footnote_link_status": "linked", "footnote_statement_ids": note5})
    upd("st-chp4-sec-ii-p118-poussin-drawing-volume",
        qualifiers={"claim": "Massimi acquired the volume containing the Poussin drawing from Marino’s successors; their identities are not supplied.", "mentioned_candidate_ids": ["cand-1564", "cand-5993", "cand-5994", "cand-1548"], "footnote_marker": 5, "footnote_segment": NOTE_SEGMENT_ID, "footnote_source_line": 307, "footnote_link_status": "linked", "footnote_statement_ids": note5})
    upd("st-chp4-sec-ii-p118-collectors-increasingly-rare",
        subject_candidate_id="cand-11676", predicate="becoming_increasingly_rare",
        qualifiers={"claim": "Haskell says other important collectors remained in Rome, but were becoming increasingly rare.", "mentioned_candidate_ids": ["cand-11676", "cand-4490"], "ocr_corrections": [{"source_line": 227, "source_form": "--they", "print_form": "they"}]})
    upd("st-chp4-sec-ii-p118-leading-patrons-characterization",
        subject_candidate_id="cand-11677", predicate="distinctive_combination_did_not_survive_massimi",
        qualifiers={"claim": "Haskell says the combination of wealth, enthusiasm, catholicity of taste, and discrimination that marked leading Italian patrons in the seventeenth century did not really survive Massimi; a largely new tradition had to be forged in the neo-classical period.", "mentioned_candidate_ids": ["cand-11677", "cand-1564"], "contextual_continuation_source_line": 230})
    upd("st-chp4-sec-ii-p118note-fn1-blunt",
        qualifiers={"ocr_corrections": [{"source_line": 303, "source_form": "IF.", "print_form": "ff."}]})
    upd("st-chp4-sec-ii-p118note-fn5-locations",
        subject_candidate_id="cand-11670", object_candidate_id="cand-11671", predicate="located_at",
        qualifiers={"claim": "Haskell reports that the two Claude paintings were then in the Chicago Art Institute and Lord Leicester Collection, without mapping either individual painting to one repository.", "mentioned_candidate_ids": ["cand-11670", "cand-11671", "cand-6002", "cand-5971"], "allocation_unspecified": True, "time_scope": "reported as current in Haskell’s account; exact date not supplied"})
    upd("st-chp4-sec-ii-p118note-fn6-plates-history",
        subject_candidate_id="cand-6007", object_candidate_id=None, predicate="first_published_in_1725",
        original_quote=quote(note, "6 The plates were not published until 1725"),
        qualifiers={"claim": "Haskell’s note says the Bartoli plates were first published in 1725.", "mentioned_candidate_ids": ["cand-6007"]})
    upd("st-chp4-sec-ii-p118note-fn6-denolhac",
        qualifiers={"mentioned_candidate_ids": ["cand-6007", "cand-6008"]})

    body_note_ids = [*note1, *note2, *note3, *note4, *note5, *note6]
    additions: list[dict] = []
    def add_body(sid: str, subject: str | None, obj: str | None, predicate: str,
                 quote: str, line_start: int, line_end: int, claim: str,
                 relation: bool, reason: str, mentioned: list[str],
                 marker: int | None = None, note_line: int | None = None,
                 note_ids: list[str] | None = None, extra: dict | None = None) -> None:
        additions.append(make_statement(sid, SEGMENT_ID, subject, obj, predicate, quote,
                                        line_start, line_end, claim, relation, reason,
                                        mentioned, note_marker=marker, note_line=note_line,
                                        note_ids=note_ids, extra=extra))

    add_body("st-chp4-sec-ii-p118-apollo-theme", "cand-5988", "cand-11669", "has_subject",
             quote(body, "the conflict between fertility and sterility"), 219, 219,
             "Poussin’s Apollo and Daphne summarizes the conflict between fertility and sterility.", True,
             "Links the work to its explicitly named theme.", ["cand-5988", "cand-11669"], 1, 303, note1)
    add_body("st-chp4-sec-ii-p118-poussin-fascinated-theme", "cand-1984", "cand-11669", "interested_in",
             quote(body, "a theme that had long fascinated him: the conflict between fertility and sterility"), 219, 219,
             "Haskell says the fertility/sterility theme had long fascinated Poussin.", True,
             "Records the explicitly attributed artist–theme connection.", ["cand-1984", "cand-11669"], 1, 303, note1)
    add_body("st-chp4-sec-ii-p118-massimi-social-centrality", "cand-1564", None, "social_position_at_rome",
             quote(body, "Massimi was now at the very centre of social life"), 222, 222,
             "Haskell characterizes Massimi as being at the centre of Roman social life at this point.", False,
             "Scalar authorial characterization.", ["cand-1564", "cand-4490"])
    add_body("st-chp4-sec-ii-p118-connoisseurship-recognised", "cand-1564", "cand-3567", "connoisseurship_officially_recognised",
             quote(body, "when his connoisseurship was officially recognised"), 221, 221,
             "Haskell says Massimi’s connoisseurship was officially recognized; the recognizing authority is not named.", False,
             "Attribute/recognition statement with no supported authority endpoint.", ["cand-1564", "cand-3567"])
    add_body("st-chp4-sec-ii-p118-massimi-favoured-maratta", "cand-1564", "cand-1526", "favoured_artist",
             quote(body, "this artist who was now his favourite"), 221, 221,
             "Carlo Maratta was then Massimi’s favourite artist.", True,
             "Records an explicit patron preference.", ["cand-1564", "cand-1526"])
    add_body("st-chp4-sec-ii-p118-fresco-created-by-maratta", "cand-5990", "cand-1526", "created_by",
             excerpt(body, "he obtained for him the most important and influential opportunity in Rome", "Allegory of Clemency"), 221, 221,
             "Massimi obtained for Maratta the opportunity to paint the principal ceiling fresco of the Allegory of Clemency.", True,
             "The source explicitly attributes the fresco opportunity to Maratta.", ["cand-5990", "cand-1526", "cand-1564", "cand-0087"], 3, 305, note3,
             {"ocr_corrections": [{"source_line": 221, "source_form": "ceding", "print_form": "ceiling"}]})
    add_body("st-chp4-sec-ii-p118-fresco-subject-clemency", "cand-5990", "cand-6468", "has_subject",
             quote(body, "depicting the Allegory of Clemency"), 221, 221,
             "The Altieri palace ceiling fresco depicts the personification of Clemency.", True,
             "Links the named work to its explicitly identified allegorical subject.", ["cand-5990", "cand-6468"], 3, 305, note3)
    add_body("st-chp4-sec-ii-p118-fresco-court-art-model", "cand-5990", "cand-11674", "became_model_for",
             quote(body, "became a model for court art all over Europe"), 221, 221,
             "Haskell says the fresco became a model for court art across Europe.", True,
             "Records the stated work-to-practice influence; Europe remains the source-given scope.", ["cand-5990", "cand-11674", "cand-3462"], 3, 305, note3,
             {"geographic_scope_candidate_id": "cand-3462"})
    add_body("st-chp4-sec-ii-p118-maratta-favourite-works-group-creator", "cand-11675", "cand-1526", "created_by",
             excerpt(body, "He commissioned several other works by this artist", "his favourite"), 221, 221,
             "Carlo Maratta created the otherwise unidentified group of several other works commissioned by Massimi.", True,
             "Records the group’s creator, distinct from Massimi’s commission.", ["cand-11675", "cand-1526", "cand-1564"])
    add_body("st-chp4-sec-ii-p118-portrait-sitter", "cand-5989", "cand-1564", "has_subject",
             quote(body, "his portrait painted by Carlo Maratta"), 221, 221,
             "The portrait is of Camillo Massimi.", True,
             "Records the portrait sitter explicitly identified by the possessive and context.", ["cand-5989", "cand-1564", "cand-1526"], 2, 304, note2)
    add_body("st-chp4-sec-ii-p118-portrait-commissioner", "cand-5989", "cand-1564", "commissioned_by",
             quote(body, "by having his portrait painted by Carlo Maratta"), 221, 221,
             "Massimi had his portrait painted to celebrate his appointments.", True,
             "The source states that Massimi had the portrait painted.", ["cand-5989", "cand-1564", "cand-1526"], 2, 304, note2)
    add_body("st-chp4-sec-ii-p118-claude-pair-patron", "cand-11670", "cand-1564", "patronized_by",
             excerpt(body, "that artist painted two large pictures for him", "A Coast View with Perseus and the Origin of Coral"), 222, 223,
             "The two Claude paintings were made for Massimi.", True,
             "Records Massimi’s patron role for the bounded pair of paintings.", ["cand-11670", "cand-1564", "cand-0767", "cand-5991", "cand-5992"], 5, 307, note5)
    add_body("st-chp4-sec-ii-p118-claude-pair-delphi-member", "cand-11670", "cand-5991", "includes_unit",
             excerpt(body, "A View of\nDelphi with a Procession", "Plate 19b"), 222, 223,
             "The two-work Claude group includes A View of Delphi with a Procession.", True,
             "Makes the explicitly named work a member of the source-bounded group.", ["cand-11670", "cand-5991"], 5, 307, note5)
    add_body("st-chp4-sec-ii-p118-claude-pair-coast-view-member", "cand-11670", "cand-5992", "includes_unit",
             quote(body, "A Coast View with Perseus and the Origin of Coral"), 223, 223,
             "The two-work Claude group includes A Coast View with Perseus and the Origin of Coral.", True,
             "Makes the explicitly named work a member of the source-bounded group.", ["cand-11670", "cand-5992"], 5, 307, note5)
    add_body("st-chp4-sec-ii-p118-coast-view-origin-subject", "cand-5992", "cand-11673", "has_subject",
             quote(body, "the Origin of Coral"), 223, 223,
             "Claude’s Coast View depicts the mythological subject Origin of Coral.", True,
             "Links the named painting to its title’s stated subject.", ["cand-5992", "cand-11673"], 5, 307, note5)
    add_body("st-chp4-sec-ii-p118-coast-view-evaluation", "cand-5992", None, "authorial_aesthetic_assessment",
             quote(body, "possibly the most magical painting in the whole range"), 223, 224,
             "Haskell tentatively calls the Coast View possibly the most magical painting in Claude’s œuvre.", False,
             "Attributed evaluative judgment, not an inter-entity relation.", ["cand-5992", "cand-0767"], 5, 307, note5)
    add_body("st-chp4-sec-ii-p118-several-maratta-works-group-patron", "cand-11675", "cand-1564", "commissioned_by",
             excerpt(body, "He commissioned several other works", "his favourite"), 221, 221,
             "Massimi commissioned the otherwise unidentified group of several other works by Maratta.", True,
             "Records Massimi’s commission of the group.", ["cand-11675", "cand-1564", "cand-1526"])
    add_body("st-chp4-sec-ii-p118-volume-contains-drawing", "cand-5993", "cand-5994", "located_in_volume",
             quote(body, "a drawing of it by\nPoussin in the volume"), 224, 225,
             "The Poussin drawing was in the volume acquired by Massimi.", True,
             "Records the drawing-to-volume containment/location claim.", ["cand-5993", "cand-5994", "cand-1564"], 5, 307, note5)
    add_body("st-chp4-sec-ii-p118-copy-project-impact", "cand-11672", None, "struck_contemporaries_imagination",
             quote(body, "Massimi undertook the enterprise which most struck the imagination of his contemporaries"), 226, 226,
             "Haskell says Massimi’s 1677 Bartoli copying enterprise particularly struck contemporaries’ imagination.", False,
             "Scalar authorial characterization of the enterprise.", ["cand-1564", "cand-11672", "cand-0251"], 6, 308, note6)
    add_body("st-chp4-sec-ii-p118-copy-set-derived-from-manuscript", "cand-11672", "cand-5995", "derived_from",
             excerpt(body, "copies made by Pietro Santo Bartoli of the fllustrations", "late antique edition of Virgil"), 226, 226,
             "Bartoli’s copies derive from illustrations in the late antique Virgil manuscript.", True,
             "Records the explicit source relationship between the copies and manuscript.", ["cand-11672", "cand-5995", "cand-0251", "cand-4380", "cand-2777"], 6, 308, note6,
             {"ocr_corrections": [{"source_line": 226, "source_form": "fllustrations", "print_form": "illustrations"}, {"source_line": 226, "source_form": "one of the-oldest", "print_form": "one of the oldest"}]})
    note_additions = [
        make_statement("st-chp4-sec-ii-p118note-fn5-cortona-origin-subject", NOTE_SEGMENT_ID,
                       "cand-5724", "cand-11673", "has_subject",
                       quote(note, "painting by Pietro da Cortona of the Origin of Coral"),
                       307, 307, "Cassiano’s Pietro da Cortona painting depicts the Origin of Coral subject.", True,
                       "Links the specific painting to its stated subject; it remains distinct from Claude’s painting.",
                       ["cand-5724", "cand-11673", "cand-2036"]),
        make_statement("st-chp4-sec-ii-p118note-fn6-bottari-text", NOTE_SEGMENT_ID,
                       "cand-6007", "cand-3507", "text_authored_by",
                       quote(note, "republished with a text by Bottari in 1741"),
                       308, 308, "The 1741 republication of Bartoli’s plates included a text authored by Bottari.", True,
                       "Records the explicitly stated authorship of the accompanying text.",
                       ["cand-6007", "cand-3507"]),
    ]
    additions.extend(note_additions)

    candidates = [
        make_candidate(11669, "Conflict between fertility and sterility (Poussin theme)", "term",
                       "Theme explicitly named in Haskell’s account of Apollo and Daphne; retain the source’s interpretive framing.", f"{SEGMENT_ID}#L219"),
        make_candidate(11670, "Two Claude paintings made for Massimi in 1673–1674 (A View of Delphi; A Coast View with Perseus)", "work",
                       "Source-bounded pair. It comprises the two individually named paintings; do not infer pendant status.", f"{SEGMENT_ID}#L222"),
        make_candidate(11671, "Chicago Art Institute and Lord Leicester Collection as the reported locations of the two Claude paintings", "",
                       "Mixed group of one institution and one named collection. Haskell does not assign either individual painting to either repository.", f"{NOTE_SEGMENT_ID}#L307"),
        make_candidate(11672, "Pietro Santo Bartoli’s copies of illustrations in the late antique Virgil manuscript (set unspecified)", "work",
                       "Source-bounded group commissioned by Massimi in 1677 and created by Bartoli; no individual copy is named. The note calls the later published material plates; retain the copying group separately from the manuscript and citation record.", f"{SEGMENT_ID}#L226"),
        make_candidate(11673, "Origin of Coral (mythological subject)", "term",
                       "Subject named in the titles/descriptions of the Claude and Cortona paintings and the Poussin drawing; do not merge with any of those work candidates.", f"{SEGMENT_ID}#L223"),
        make_candidate(11674, "Court art (practice modeled by the Altieri palace fresco)", "term",
                       "Source-bounded artistic practice named as the scope for the fresco’s influence; Europe is preserved separately as geographic scope.", f"{SEGMENT_ID}#L221"),
        make_candidate(11675, "Several otherwise unidentified works by Carlo Maratta commissioned by Massimi", "work",
                       "Plural group only; the source does not name its members or quantity beyond several.", f"{SEGMENT_ID}#L221"),
        make_candidate(11676, "Other important collectors in Rome at the time (unnamed group)", "",
                       "Haskell says the group remained but was becoming increasingly rare. No individual collectors are named.", f"{SEGMENT_ID}#L226"),
        make_candidate(11677, "Leading Italian patrons of the seventeenth century in Haskell’s historical characterization (unnamed group)", "",
                       "The p.118 sentence continues on p.119. The group is characterized collectively; no members are supplied.", f"{SEGMENT_ID}#L227"),
    ]

    with (TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline="") as f:
        current_candidates = list(csv.DictReader(f))
    numeric_ids = [int(r["candidate_id"].removeprefix("cand-")) for r in current_candidates if r["candidate_id"].startswith("cand-") and r["candidate_id"][5:].isdigit()]
    if max(numeric_ids) != 11668 or any(r["candidate_id"] in {x["candidate_id"] for x in candidates} for r in current_candidates):
        raise SystemExit("candidate ID state changed; expected max cand-11668 and unused p.118 IDs")
    with (TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="") as f:
        old_mentions = list(csv.DictReader(f))
    target_statement_ids = BODY_IDS | NOTE_IDS
    outside_statement_refs = [r["statement_id"] for r in current_rows
                              if r["statement_id"] not in target_statement_ids
                              and (r.get("subject_candidate_id") == "cand-1572"
                                   or r.get("object_candidate_id") == "cand-1572"
                                   or "cand-1572" in r.get("qualifiers", {}).get("mentioned_candidate_ids", []))]
    outside_mention_refs = [m["mention_id"] for m in old_mentions
                            if m["candidate_id"] == "cand-1572" and m["segment_id"] != SEGMENT_ID]
    if outside_statement_refs or outside_mention_refs:
        raise SystemExit(f"cand-1572 is referenced outside p.118: statements={outside_statement_refs}, mentions={outside_mention_refs}")
    candidate_updates = {
        "cand-1572": {
            "expected": {"index_entry_id": "M.csv#111", "canonical_name": "Massimi, Cardinal Camillo (Carlo)", "suggested_type": "work", "sub_entry": "copies of illustrations of late antique Virgil manuscript"},
            "set": {"suggested_type": "person", "detail": "Index-entry candidate for Camillo Massimi; its subentry describes the p.118 copying episode, not a separate work. Keep as a person candidate pending alignment with cand-1564. The p.118 mention of the copied illustrations is mapped to the separate work group cand-11672."},
        }
    }
    body_mentions = [r for r in old_mentions if r["segment_id"] == SEGMENT_ID]
    note_mentions = [r for r in old_mentions if r["segment_id"] == NOTE_SEGMENT_ID]
    for mention in body_mentions:
        a, b = int(mention["start_char"]), int(mention["end_char"])
        if body[a:b] != mention["surface_form"]:
            raise SystemExit(f"existing p.118 mention span mismatch: {mention['mention_id']}")
    for mention in note_mentions:
        a, b = int(mention["start_char"]), int(mention["end_char"])
        if note[a:b] != mention["surface_form"]:
            raise SystemExit(f"existing linked-note mention span mismatch: {mention['mention_id']}")

    def mention(mid: str, segment: str, text: str, candidate: int, body_text: str, note_text: str, line_no: int) -> dict[str, str]:
        first_line = 218 if segment == SEGMENT_ID else 232
        seg_text = body if segment == SEGMENT_ID else note
        line_text = source_lines[line_no - 1]
        local = line_text.find(text)
        if local < 0 or line_text.find(text, local + 1) >= 0:
            raise SystemExit(f"new mention phrase absent or ambiguous on L{line_no}: {text!r}")
        prefix = sum(len(x) + 1 for x in source_lines[first_line - 1:line_no - 1])
        start, end = prefix + local, prefix + local + len(text)
        if seg_text[start:end] != text:
            raise SystemExit(f"new mention span mismatch: {mid}")
        return {"mention_id": mid, "segment_id": segment, "candidate_id": f"cand-{candidate}",
                "surface_form": text, "start_char": str(start), "end_char": str(end), "note": note_text}

    new_mentions = [
        mention("m-chp4-sec-ii-p118-0040", SEGMENT_ID, "two large pictures", 11670, body, "Source-bounded pair; its two named members are recorded separately.", 222),
        mention("m-chp4-sec-ii-p118-0041", SEGMENT_ID, "conflict between fertility and sterility", 11669, body, "Theme named in the sentence completing the p.117 discussion of Apollo and Daphne.", 219),
        mention("m-chp4-sec-ii-p118-0042", SEGMENT_ID, "Clemency", 6468, body, "Nested mention of the allegorical subject of the Altieri palace fresco.", 221),
        mention("m-chp4-sec-ii-p118-0043", SEGMENT_ID, "court art", 11674, body, "Practice Haskell says was modeled by the fresco.", 221),
        mention("m-chp4-sec-ii-p118-0044", SEGMENT_ID, "Origin of Coral", 11673, body, "Mythological subject named within the Claude painting title.", 223),
        mention("m-chp4-sec-ii-p118-0045", SEGMENT_ID, "several other works", 11675, body, "Unspecified group of works by Maratta commissioned by Massimi.", 221),
        mention("m-chp4-sec-ii-p118-0046", SEGMENT_ID, "other important collectors", 11676, body, "Unnamed Roman collector group; no members inferred.", 226),
        mention("m-chp4-sec-ii-p118-0047", SEGMENT_ID, "leading Italian patrons", 11677, body, "Unnamed seventeenth-century group; sentence continues at p.119 L230.", 227),
        mention("m-chp4-sec-ii-p118note-painting-group", NOTE_SEGMENT_ID, "The pictures", 11670, note, "Footnote refers to the two Claude paintings named on p.118; individual repository mapping is unspecified.", 307),
        mention("m-chp4-sec-ii-p118note-location-group", NOTE_SEGMENT_ID, "the Chicago Art Institute and Lord Leicester Collection", 11671, note, "Joint location group; exact painting-to-repository assignment is not stated.", 307),
        mention("m-chp4-sec-ii-p118note-origin-subject", NOTE_SEGMENT_ID, "Origin of Coral", 11673, note, "Nested mention of the subject of Cassiano’s distinct Cortona painting.", 307),
    ]
    new_ids = {m["mention_id"] for m in new_mentions}
    if new_ids & {m["mention_id"] for m in old_mentions}:
        raise SystemExit("one or more p.118 mention IDs already exist")
    replacements = {
        "m-chp4-sec-ii-p118-0013": ("cand-4651", "cand-6461"),
        "m-chp4-sec-ii-p118-0028": ("cand-1572", "cand-11672"),
    }
    note_updates = {
        "m-chp4-sec-ii-p118note-0012": "One of the two reported repositories; exact painting assignment is unspecified.",
        "m-chp4-sec-ii-p118note-0013": "One of the two reported repositories; exact painting assignment is unspecified.",
        "m-chp4-sec-ii-p118-0015": "OCR reads 'ceding'; the scan reads 'ceiling'.",
    }
    removals = {"m-s2-chp4-surface-3975471a12395f9a"}
    existing_mention_ids = {m["mention_id"] for m in old_mentions}
    mention_targets = set(replacements) | set(note_updates) | removals
    if not mention_targets <= existing_mention_ids:
        raise SystemExit("one or more p.118 mention repair targets are missing")

    # Every existing statement remains tied to its source quote; new quotes are checked too.
    for row in body_rows + note_rows:
        q = row["qualifiers"]
        a, b = int(q["source_line_start"]), int(q["source_line_end"])
        text = "\n".join(source_lines[a - 1:b])
        if norm(row["original_quote"]) not in norm(text):
            raise SystemExit(f"existing quote is not on its cited source lines: {row['statement_id']}")
    for row in additions:
        q = row["qualifiers"]
        a, b = int(q["source_line_start"]), int(q["source_line_end"])
        text = "\n".join(source_lines[a - 1:b])
        if norm(row["original_quote"]) not in norm(text):
            raise SystemExit(f"new quote is not on its cited source lines: {row['statement_id']}")

    eol = b"\r\n" if b"\r\n" in original["book-statements.jsonl"] else b"\n"
    outputs = {
        "book-statements.jsonl": transform_statements(original["book-statements.jsonl"], updates, additions, eol),
        "entity-candidates.csv": transform_candidates(original["entity-candidates.csv"], candidate_updates, candidates),
        "mentions.csv": transform_mentions(original["mentions.csv"], replacements, note_updates, removals, new_mentions),
    }
    for name, path in paths.items():
        backup = path.with_name(path.name + "." + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"recovery backup already exists: {backup.name}")

    plan = {
        "body_statements_classified": len(BODY_IDS),
        "linked_footnote_statements_classified": len(NOTE_IDS),
        "new_statements": [r["statement_id"] for r in additions],
        "new_candidates": [r["candidate_id"] for r in candidates],
        "candidate_repairs": {"cand-1572": "type work -> person; index entry is Massimi, while its subentry names the copying episode"},
        "new_mentions": [r["mention_id"] for r in new_mentions],
        "mention_repairs": {**replacements, **{k: v for k, v in note_updates.items()}},
        "removed_false_positive_mentions": sorted(removals),
        "source_corrections_recorded": ["L219 os/of", "L221 ceding/ceiling", "L226 fllustrations/illustrations", "L226 the-oldest/the oldest", "L227 --they/they", "L303 IF./ff."],
        "prewrite_sha256": {name: digest(data) for name, data in original.items()},
        "postwrite_sha256": {name: digest(data) for name, data in outputs.items()},
    }
    return paths, original, outputs, plan


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the validated p.118 semantic review")
    args = parser.parse_args()
    paths, original, outputs, plan = prepare()
    print(json.dumps({"mode": "apply" if args.apply else "dry-run", **plan}, ensure_ascii=False, indent=2))
    if not args.apply:
        return
    for name, path in paths.items():
        backup = path.with_name(path.name + "." + BACKUP_SUFFIX)
        shutil.copy2(path, backup)
        if backup.read_bytes() != original[name]:
            raise SystemExit(f"recovery backup verification failed: {backup.name}")
        path.write_bytes(outputs[name])
    for name, path in paths.items():
        if digest(path.read_bytes()) != plan["postwrite_sha256"][name]:
            raise SystemExit(f"postwrite digest mismatch: {name}")
    print("applied p.118 writeback; verified recovery copies and postwrite hashes")


if __name__ == "__main__":
    main()
