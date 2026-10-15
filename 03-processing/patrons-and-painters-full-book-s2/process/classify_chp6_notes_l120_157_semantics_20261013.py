from __future__ import annotations

import argparse
import copy
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
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_i.md"
SOURCE_FILE = "02-sources/02-Markdown/06_CHP-6_sec_i.md"
SEGMENT = "chp-6:06_CHP-6_sec_i:l120-157"
BACKUP_SUFFIX = ".bak-s2-chp6-notes-l120-157-semantics-20261013"

EXPECTED_HASHES = {
    SOURCE: "e1bf27cf13961032d4587a1787a1b89f00a9076cf7a8c9dd4434000e84add42d",
    STATEMENTS: "b5be82b2920324a96108dd5fe9e0862d8445816b191e8349b5e3588dcffd3c6e",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    MENTIONS: "ed0edfb746adaded101c78185735a3834ca66d70ebada9e2568cb424084501bc",
    COVERAGE: "0176fff22149231bd9631a2aeb0247ede5fb485755ac088ae94e2a400faa4734",
}

TARGETS = {
    "st-chp6-notes-l121-p147-n1",
    "st-chp6-notes-l122-p148-n1",
    "st-chp6-notes-l124-p149-n2",
    "st-chp6-notes-l125-p149-n3",
    "st-chp6-notes-l126-p149-n4",
    "st-chp6-notes-l127-p149-n5",
    "st-chp6-notes-l129-p149-n7",
    "st-chp6-notes-l130-p150-n1",
    "st-chp6-notes-l131-p150-n2",
    "st-chp6-notes-l132-p150-n3",
    "st-chp6-notes-l133-p150-n4",
    "st-chp6-notes-l134-p150-n5",
    "st-chp6-notes-l135-p150-n6",
    "st-chp6-notes-l136-p151-n1",
    "st-chp6-notes-l137-p151-n2",
    "st-chp6-notes-l138-p151-n3",
    "st-chp6-notes-l139-p151-n4",
    "st-chp6-notes-l140-p152-n1",
    "st-chp6-notes-l141-p152-n2",
    "st-chp6-notes-l142-p152-n3",
    "st-chp6-notes-l143-p152-n4",
    "st-chp6-notes-l144-p152-n5",
    "st-chp6-notes-l146-p153-n2",
    "st-chp6-notes-l156-p156-n1-1",
    "st-chp6-notes-l157-p156-n2",
}

TRUE_NOTE = (
    "Haskell explicitly cites this archive from his book. This records a "
    "bibliographic candidate and does not verify the cited content."
)
FALSE_NOTE = (
    "This preserves quoted wording or contextual commentary in a footnote; "
    "it is not a specific historical relation candidate."
)
CITATION_QUALIFICATION = (
    "Citation locator only; the cited work has not been independently consulted."
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path):
    raw = path.read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader), raw.startswith(b"\xef\xbb\xbf")


def csv_bytes(fields, rows, bom):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\r\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + stream.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes):
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def source_line(lines, line_number):
    if line_number < 1 or line_number > len(lines):
        raise SystemExit(f"source line outside file: L{line_number}")
    return lines[line_number - 1]


def set_citation(row, *, object_id, claim, locator, mentioned, relation_note=None, text_layer="bibliographic citation"):
    row["subject_candidate_id"] = "cand-2962"
    row["object_candidate_id"] = object_id
    row["predicate"] = "cites"
    q = row.setdefault("qualifiers", {})
    q.update({
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": text_layer,
        "qualification": CITATION_QUALIFICATION,
        "mentioned_candidate_ids": mentioned,
        "citation_locator": locator,
        "relation_candidate": True,
        "relation_candidate_note": relation_note or TRUE_NOTE,
    })
    q.pop("open_endpoint_reason", None)
    return row


def split_citation(base, statement_id, **kwargs):
    row = copy.deepcopy(base)
    row["statement_id"] = statement_id
    return set_citation(row, **kwargs)


def build_outputs():
    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if sha256(raw[path]) != expected:
            raise SystemExit(f"input SHA mismatch: {path.relative_to(ROOT)}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {
        sid for sid, row in by_id.items()
        if row.get("segment_id") == SEGMENT and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != TARGETS:
        raise SystemExit(f"unset footnote target set changed: {sorted(unset ^ TARGETS)}")

    candidate_fields, candidates, _ = read_csv(CANDIDATES)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    required_archives = {
        "cand-2962", "cand-4836", "cand-11286", "cand-11266", "cand-4557", "cand-6352",
        "cand-6006", "cand-4376", "cand-6355", "cand-6356", "cand-6359", "cand-6360",
        "cand-6361", "cand-4835", "cand-6363", "cand-4548", "cand-6364", "cand-6366",
        "cand-6368", "cand-6338", "cand-6370", "cand-6377", "cand-4577", "cand-6388",
        "cand-6385", "cand-6387", "cand-4805", "cand-5975",
    }
    missing_candidates = required_archives - set(candidate_by_id)
    if missing_candidates:
        raise SystemExit(f"required cited-source candidate missing: {sorted(missing_candidates)}")
    non_archive = [cid for cid in required_archives if candidate_by_id[cid]["suggested_type"] != "archive"]
    if non_archive:
        raise SystemExit(f"citation target is not typed archive: {sorted(non_archive)}")

    mention_fields, mentions, mention_bom = read_csv(MENTIONS)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    mention_updates = {
        "m-chp6-note-9470": "Print p.151 reads Alexander VII’s; S0 OCR reads Alexander Vil’s. S0 is unchanged.",
        "m-chp6-note-9476": "Print p.151 reads 1960; S0 OCR reads i960. S0 is unchanged.",
        "m-chp6-note-9512": "Print p.156 reads Röthlisberger; S0 OCR reads Rothlisberger. S0 is unchanged.",
    }
    for mid, note in mention_updates.items():
        if mid not in mention_by_id or mention_by_id[mid]["segment_id"] != SEGMENT:
            raise SystemExit(f"required footnote mention missing or moved: {mid}")
        mention_by_id[mid]["note"] = note

    coverage_fields, coverage, coverage_bom = read_csv(COVERAGE)
    cov = next((row for row in coverage if row["segment_id"] == SEGMENT), None)
    if not cov or (cov["disposition"], cov["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit(f"unexpected footnote coverage state: {cov}")

    for sid in TARGETS:
        row = by_id[sid]
        q = row.get("qualifiers", {})
        start = int(q["source_line_start"])
        if q["source_line_end"] != start or row["original_quote"] != source_line(source_lines, start):
            raise SystemExit(f"footnote source anchor changed: {sid}")

    additions = []

    def base(sid):
        return by_id[sid]

    def add_after(sid, new_row):
        if new_row["statement_id"] in by_id or any(r["statement_id"] == new_row["statement_id"] for _, r in additions):
            raise SystemExit(f"new footnote statement ID already exists: {new_row['statement_id']}")
        additions.append((sid, new_row))

    # p.147 n.1: one note cites three separate archives.
    row = base("st-chp6-notes-l121-p147-n1")
    set_citation(row, object_id="cand-4836", claim="Footnote 1 cites Pastor, volume XIV.", locator="volume XIV", mentioned=["cand-4836"])
    for suffix, object_id, claim, locator, mentioned in [
        ("ciampi-citation", "cand-11286", "Footnote 1 directs readers to Ciampi’s Innocenzo X Pamfili e la sua corte.", "no page locator", ["cand-6348", "cand-11286"]),
        ("brigante-colonna-citation", "cand-11266", "Footnote 1 directs readers to Brigante Colonna’s Olimpia Pamfili.", "no page locator", ["cand-6349", "cand-11266"]),
    ]:
        add_after(row["statement_id"], split_citation(row, f"{row['statement_id']}-{suffix}", object_id=object_id, claim=claim, locator=locator, mentioned=mentioned))

    # p.148 n.1: Wittkower and Portoghesi are separate cited works.
    row = base("st-chp6-notes-l122-p148-n1")
    set_citation(row, object_id="cand-4557", claim="Footnote 1 cites Wittkower’s Art and Architecture in Italy 1600–1750 (1958).", locator="1958 edition", mentioned=["cand-2818", "cand-4557"])
    add_after(row["statement_id"], split_citation(row, f"{row['statement_id']}-portoghesi-citation", object_id="cand-6352", claim="Footnote 1 also cites Portoghesi’s 1955 study of the Lateran basilica.", locator="1955 publication", mentioned=["cand-4325", "cand-6352"]))

    single_citations = {
        "st-chp6-notes-l124-p149-n2": ("cand-6006", "Footnote 2 cites Barozzi e Berchet, volume II, pages 71 and 98.", "volume II, pp. 71 and 98", ["cand-6006"]),
        "st-chp6-notes-l125-p149-n3": ("cand-4376", "Footnote 3 cites Passeri, page 337.", "p. 337", ["cand-1856", "cand-4376"]),
        "st-chp6-notes-l129-p149-n7": ("cand-6359", "Footnote 7 cites Cipolla (1952), pages 178–187, for a general outline of the economic situation.", "1952, pp. 178–187", ["cand-6358", "cand-6359"]),
        "st-chp6-notes-l130-p150-n1": ("cand-6006", "Footnote 1 cites Barozzi e Berchet, volume II, page 214.", "volume II, p. 214", ["cand-6006"]),
        "st-chp6-notes-l131-p150-n2": ("cand-6360", "Footnote 2 cites Gigli, page 233.", "p. 233", ["cand-1168", "cand-6360"]),
        "st-chp6-notes-l132-p150-n3": ("cand-6361", "Footnote 3 cites Missirini, page 116.", "p. 116", ["cand-3538", "cand-6361"]),
        "st-chp6-notes-l133-p150-n4": ("cand-4835", "Footnote 4 cites de Dominici, volume IV, page 19.", "volume IV, p. 19", ["cand-0942", "cand-4835"]),
        "st-chp6-notes-l134-p150-n5": ("cand-4836", "Footnote 5 cites Pastor, volume XIV, page 37.", "volume XIV, p. 37", ["cand-4836"]),
        "st-chp6-notes-l135-p150-n6": ("cand-6363", "Footnote 6 cites Cugnoni (1879–81).", "1879–1881", ["cand-6362", "cand-6363"]),
        "st-chp6-notes-l136-p151-n1": ("cand-4548", "Footnote 1 cites Baldinucci (1948), page 107.", "1948, p. 107", ["cand-0166", "cand-4548"]),
        "st-chp6-notes-l138-p151-n3": ("cand-6366", "Footnote 3 cites Ozzola (1908), page 6.", "1908, p. 6", ["cand-6365", "cand-6366"]),
        "st-chp6-notes-l139-p151-n4": ("cand-6368", "Footnote 4 cites Wibiral (1960), pages 123–165.", "1960, pp. 123–165", ["cand-6367", "cand-6368"]),
        "st-chp6-notes-l141-p152-n2": ("cand-6006", "Footnote 2 cites Barozzi e Berchet, volume II, page 245.", "volume II, p. 245", ["cand-6006"]),
        "st-chp6-notes-l142-p152-n3": ("cand-6006", "Footnote 3 cites Barozzi e Berchet, volume II, page 320.", "volume II, p. 320", ["cand-6006"]),
        "st-chp6-notes-l143-p152-n4": ("cand-6338", "Footnote 4 cites Bellori (1942), page 82.", "1942, p. 82", ["cand-3535", "cand-6338"]),
        "st-chp6-notes-l144-p152-n5": ("cand-6370", "Footnote 5 cites de Rinaldis (1939), pages 150 and 161–162.", "1939, pp. 150 and 161–162", ["cand-6369", "cand-6370"]),
        "st-chp6-notes-l146-p153-n2": ("cand-6377", "Footnote 2 cites Spini and Limentani (1961) for examples of anti-papal satire.", "1961; cited pages unspecified", ["cand-6375", "cand-6376", "cand-6377"]),
        "st-chp6-notes-l156-p156-n1-1": ("cand-4577", "Footnote 1 says Haskell closely followed Röthlisberger (1961), page 374, for Lorenzo Onofrio and Claude.", "1961, p. 374", ["cand-3502", "cand-4577"]),
    }
    for sid, (object_id, claim, locator, mentioned) in single_citations.items():
        set_citation(base(sid), object_id=object_id, claim=claim, locator=locator, mentioned=mentioned)

    # p.149 n.4 and n.5 each cite two works.
    row = base("st-chp6-notes-l126-p149-n4")
    set_citation(row, object_id="cand-4376", claim="Footnote 4 cites Passeri, page 371.", locator="p. 371", mentioned=["cand-1856", "cand-4376"])
    add_after(row["statement_id"], split_citation(row, f"{row['statement_id']}-montalto-citation", object_id="cand-6355", claim="Footnote 4 also cites Montalto, pages 267–302.", locator="pp. 267–302", mentioned=["cand-6355"]))

    row = base("st-chp6-notes-l127-p149-n5")
    set_citation(row, object_id="cand-4376", claim="Footnote 5 cites Passeri, page 337.", locator="p. 337", mentioned=["cand-1856", "cand-4376"])
    add_after(row["statement_id"], split_citation(row, f"{row['statement_id']}-golzio-citation", object_id="cand-6356", claim="Footnote 5 also cites Golzio (1933–34), page 304.", locator="1933–34, p. 304", mentioned=["cand-3501", "cand-6356"]))

    # p.151 n.2 lists three separate sources.
    row = base("st-chp6-notes-l137-p151-n2")
    set_citation(row, object_id="cand-6364", claim="Footnote 2 cites P. Sforza Pallavicino, Libro V, chapter 5, for Alexander VII’s patronage.", locator="Libro V, chapter 5", mentioned=["cand-1810", "cand-6364"])
    add_after(row["statement_id"], split_citation(row, f"{row['statement_id']}-pastor-citation", object_id="cand-4836", claim="Footnote 2 also cites Pastor, volume XIV, pages 506 ff.", locator="volume XIV, pp. 506 ff.", mentioned=["cand-4836"]))
    add_after(row["statement_id"], split_citation(row, f"{row['statement_id']}-ozzola-citation", object_id="cand-6366", claim="Footnote 2 also cites Ozzola (1908), pages 5–91.", locator="1908, pp. 5–91", mentioned=["cand-6365", "cand-6366"]))

    # p.152 n.1 preserves the quoted wording and records the citation as its own edge.
    row = base("st-chp6-notes-l140-p152-n1")
    row["subject_candidate_id"] = "cand-0665"
    row["object_candidate_id"] = ""
    row["predicate"] = "footnote_quote"
    q = row.setdefault("qualifiers", {})
    q.update({
        "claim": "The footnote reproduces a phrase from Barozzi e Berchet, volume II, page 247, as a complaint attributed in Haskell’s text to Alexander VII.",
        "text_layer": "quotation excerpt in authorial footnote",
        "qualification": "The wording is preserved as Haskell’s quotation and attribution; the cited source and utterance were not independently examined.",
        "mentioned_candidate_ids": ["cand-0665", "cand-6006"],
        "relation_candidate": False,
        "relation_candidate_note": FALSE_NOTE,
        "citation_locator": "volume II, p. 247",
    })
    add_after(row["statement_id"], split_citation(
        row, f"{row['statement_id']}-citation", object_id="cand-6006",
        claim="Footnote 1 cites Barozzi e Berchet, volume II, page 247, for the quoted wording attributed to Alexander VII.",
        locator="volume II, p. 247", mentioned=["cand-0665", "cand-6006"],
    ))

    # p.156 n.2 has five source pointers and is linked to the already processed sec_iv body.
    row = base("st-chp6-notes-l157-p156-n2")
    p156_sources = [
        ("cand-6388", "st-chp6-notes-l157-p156-n2", "Footnote 2 directs readers to multiple unspecified Moroni references concerning Antonio degli Effetti.", "Moroni references; volume and pages unspecified", ["cand-5974", "cand-5954", "cand-6388"], "moroni-citation"),
        ("cand-6385", "st-chp6-notes-l157-p156-n2-orbaan-citation", "Footnote 2 also cites Orbaan (1914), page 46.", "1914, p. 46", ["cand-6384", "cand-6385"], "orbaan-citation"),
        ("cand-6387", "st-chp6-notes-l157-p156-n2-vaes-citation", "Footnote 2 also cites Vaes (1925), page 171.", "1925, p. 171", ["cand-6386", "cand-6387"], "vaes-citation"),
        ("cand-4805", "st-chp6-notes-l157-p156-n2-bellori-citation", "Footnote 2 also cites Bellori’s Nota dei Musei.", "Nota dei Musei; no page locator", ["cand-3535", "cand-4805"], "bellori-citation"),
        ("cand-5975", "st-chp6-notes-l157-p156-n2-inventory-citation", "Footnote 2 especially cites the manuscript account and inventory of Antonio degli Effetti’s collection at Biblioteca Casanatense, Rome, MS. 2372.", "Biblioteca Casanatense, Rome, MS. 2372", ["cand-5974", "cand-3409", "cand-5975", "cand-6389"], "inventory-citation"),
    ]
    object_id, _, claim, locator, mentioned, _ = p156_sources[0]
    set_citation(row, object_id=object_id, claim=claim, locator=locator, mentioned=mentioned, text_layer="bibliographic and archival citation")
    for object_id, new_id, claim, locator, mentioned, _suffix in p156_sources[1:]:
        add_after(row["statement_id"], split_citation(row, new_id, object_id=object_id, claim=claim, locator=locator, mentioned=mentioned, text_layer="bibliographic and archival citation"))

    # Record only verified print/OCR differences; keep S0 source text unchanged.
    q = base("st-chp6-notes-l127-p149-n5")["qualifiers"]
    q["printed_footnote_label"] = 5
    q["ocr_correction"] = "S0 L127 shows marker 6 and a stray trailing comma; print p.149 shows marker 5 and no trailing comma. S0 is unchanged."
    base("st-chp6-notes-l129-p149-n7")["qualifiers"]["ocr_correction"] = "S0 reads 'situarion'; print p.149 reads 'situation'. S0 is unchanged."
    base("st-chp6-notes-l137-p151-n2")["qualifiers"]["ocr_correction"] = "S0 reads 'Alexander Vil' and 'pp. 5-91-'; print p.151 reads 'Alexander VII' and 'pp. 5–91'. S0 is unchanged."
    base("st-chp6-notes-l139-p151-n4")["qualifiers"]["ocr_correction"] = "S0 reads 'i960'; print p.151 reads '1960'. S0 is unchanged."
    base("st-chp6-notes-l144-p152-n5")["qualifiers"]["printed_footnote_label"] = 5
    base("st-chp6-notes-l144-p152-n5")["qualifiers"]["ocr_correction"] = "S0 reads marker 3; print p.152 shows marker 5. S0 is unchanged."
    base("st-chp6-notes-l156-p156-n1-1")["qualifiers"]["ocr_correction"] = "S0 reads 'Rothlisberger'; print p.156 reads 'Röthlisberger'. S0 is unchanged."

    # Insert each split row immediately after its source note, keeping source order stable.
    additions_by_source = {}
    for source_id, new_row in additions:
        additions_by_source.setdefault(source_id, []).append(new_row)
    ordered = []
    for row in statements:
        ordered.append(row)
        ordered.extend(additions_by_source.get(row["statement_id"], []))
    statements = ordered
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement ID after footnote split")

    # Maintain reciprocal body-to-footnote references for each bibliographic citation row.
    linked_citation_rows = 0
    backlink_updates = []
    for row in statements:
        if row.get("segment_id") != SEGMENT or row.get("predicate") != "cites":
            continue
        q = row.get("qualifiers", {})
        body_ids = q.get("citation_body_statement_ids") or q.get("linked_body_statement_ids") or []
        for body_id in body_ids:
            if body_id not in by_id:
                raise SystemExit(f"citation points to missing body statement: {row['statement_id']} -> {body_id}")
            body_q = by_id[body_id].setdefault("qualifiers", {})
            refs = body_q.setdefault("footnote_citation_statement_ids", [])
            if row["statement_id"] not in refs:
                refs.append(row["statement_id"])
                backlink_updates.append({"body_statement_id": body_id, "citation_statement_id": row["statement_id"]})
        linked_citation_rows += 1

    # The p.156 second footnote is already linked to its later-listed sec_iv content; retain the reciprocal link.
    seciv_ids = {
        "st-chp6-p156-seciv-effetti-characterization",
        "st-chp6-p156-seciv-effetti-pictures-disappeared",
        "st-chp6-p156-seciv-effetti-taste-fragment",
    }
    if not seciv_ids <= set(by_id):
        raise SystemExit("p.156 note 2 body targets are absent")
    for body_id in seciv_ids:
        body_q = by_id[body_id]["qualifiers"]
        if body_q.get("footnote_link_status") != "linked" or body_q.get("footnote_pending") is not False:
            raise SystemExit(f"p.156 note 2 body backlink is not complete: {body_id}")

    # Update the segment's current-state note: p.156 n.2 now has verified, reciprocal sec_iv links.
    cov["note"] = (
        "逐条处理合并注释L121–157，拆分多来源脚注并记录书目引文候选；引文回链覆盖印刷页147–156，"
        "含p.156注2至sec_iv L3–5。印本校记L127、L129、L137、L139、L144、L156的OCR差异；"
        "L155正文/注释编号差异沿用既有记录。原始S0转录未改，引用来源内容未独立核验。"
    )

    valid_candidates = set(candidate_by_id)
    segment_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    for row in segment_rows:
        q = row.get("qualifiers", {})
        if q.get("relation_candidate") not in (True, False):
            raise SystemExit(f"footnote statement remains unclassified: {row['statement_id']}")
        refs = set(q.get("mentioned_candidate_ids", []))
        endpoints = {row.get("subject_candidate_id"), row.get("object_candidate_id")} - {None, ""}
        if not (refs | endpoints) <= valid_candidates:
            raise SystemExit(f"candidate reference missing: {row['statement_id']}")
    if not all(base(sid)["qualifiers"].get("relation_candidate") is not None for sid in TARGETS):
        raise SystemExit("an original unset statement remains")

    outputs = {
        STATEMENTS: ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8"),
        MENTIONS: csv_bytes(mention_fields, mentions, mention_bom),
        COVERAGE: csv_bytes(coverage_fields, coverage, coverage_bom),
    }
    true_count = sum(row["qualifiers"].get("relation_candidate") is True for row in segment_rows)
    false_count = sum(row["qualifiers"].get("relation_candidate") is False for row in segment_rows)
    unset_count = sum(row["qualifiers"].get("relation_candidate") is None for row in segment_rows)
    if (len(segment_rows), true_count, false_count, unset_count) != (54, 51, 3, 0):
        raise SystemExit(f"unexpected footnote-segment totals: {(len(segment_rows), true_count, false_count, unset_count)}")

    summary = {
        "segment": SEGMENT,
        "previously_unset_classified": len(TARGETS),
        "new_split_statements": len(additions),
        "new_citation_rows": [
            {
                "statement_id": row["statement_id"],
                "object_candidate_id": row["object_candidate_id"],
                "citation_locator": row["qualifiers"].get("citation_locator"),
                "claim": row["qualifiers"].get("claim"),
            }
            for _, row in additions
        ],
        "converted_statement_ids": sorted(TARGETS),
        "body_backlink_updates": backlink_updates,
        "citation_rows_linked_to_body": linked_citation_rows,
        "segment_statement_count_after": len(segment_rows),
        "relation_candidates_after": true_count,
        "non_relational_after": false_count,
        "unset_after": unset_count,
        "mention_notes_updated": sorted(mention_updates),
        "ocr_corrections_recorded": ["L127", "L129", "L137", "L139", "L144", "L156"],
        "mode": "dry-run",
    }
    return outputs, summary


def main():
    parser = argparse.ArgumentParser(description="Classify and split chapter 6 footnote S2 statements.")
    parser.add_argument("--apply", action="store_true", help="Back up and apply the reviewed footnote batch.")
    args = parser.parse_args()
    outputs, summary = build_outputs()
    summary["mode"] = "apply" if args.apply else "dry-run"
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not args.apply:
        return
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in outputs}
    if any(path.exists() for path in backups.values()):
        raise SystemExit("backup already exists; refusing to overwrite")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    for path, data in outputs.items():
        atomic_write(path, data)
    print("APPLIED; backups:")
    for backup in backups.values():
        print(backup.relative_to(ROOT))


if __name__ == "__main__":
    main()
