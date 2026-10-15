from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_iv.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-7.pdf"
NOTES = "chp-7:07_CHP-7_sec_iv:l97-119"
BODY_197 = "chp-7:07_CHP-7_sec_iv:l63-75"
BODY_198 = "chp-7:07_CHP-7_sec_iv:l77-87"
SOURCE_BOOK = "cand-2962"

EXPECTED_HASHES = {
    STATEMENTS.name: "98163ba1df1b88b51f126c836fd678ef69bbab234ef7f3a507ca89075f6cdf19",
    CANDIDATES.name: "9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d",
    SOURCE.name: "d620659a2f3567ea9a1d91b7657390e9824768c320c3cf534bd30069d6c72077",
    PDF.name: "eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212",
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp7-p197_198-notes-20261013")

UNSET_IDS = {
    "st-chp7-p197-n1-cassana-date-conflict",
    "st-chp7-p197-n2-portrait-attributions",
    "st-chp7-p197-n4-isham-pictures-lamport",
    "st-chp7-p197-n5-exeter-pictures-burghley",
    "st-chp7-p198-n2-biographical-citations",
}
P197_N2_KILLIGREW = "st-chp7-p197-n2-killigrew-portrait"
P197_N2_ALTHAM = "st-chp7-p197-n2-altham-portrait"
P198_N2_CITATIONS = (
    "st-chp7-p198-n2-cite-pascoli",
    "st-chp7-p198-n2-cite-baldinucci",
    "st-chp7-p198-n2-cite-de-dominici",
)
NEW_IDS = {P197_N2_KILLIGREW, P197_N2_ALTHAM, *P198_N2_CITATIONS}

BODY_LINKS = {
    "st-chp7-p197-n1-cassana-date-conflict": [
        ("st-chp7-p197-queen-anne-employs-cassana", 1, 108, BODY_197),
    ],
    "st-chp7-p197-n2-portrait-attributions": [
        ("st-chp7-p197-tourist-portrait-examples", 2, 109, BODY_197),
    ],
    P197_N2_KILLIGREW: [
        ("st-chp7-p197-tourist-portrait-examples", 2, 109, BODY_197),
    ],
    P197_N2_ALTHAM: [
        ("st-chp7-p197-tourist-portrait-examples", 2, 109, BODY_197),
    ],
    "st-chp7-p197-n4-isham-pictures-lamport": [
        ("st-chp7-p197-isham-acquired-paintings-with-advice", 4, 110, BODY_197),
        ("st-chp7-p197-isham-commissions-in-rome", 4, 110, BODY_197),
        ("st-chp7-p197-isham-mythological-pictures", 4, 110, BODY_197),
        ("st-chp7-p197-isham-portrait-maratta", 4, 110, BODY_197),
    ],
    "st-chp7-p197-n5-exeter-pictures-burghley": [
        ("st-chp7-p197-exeter-ordered-nine-dolci", 5, 111, BODY_197),
        ("st-chp7-p197-exeter-ordered-fifteen-giordano", 5, 111, BODY_197),
        ("st-chp7-p197-exeter-collected-maratta-rome", 5, 111, BODY_197),
    ],
}
for note_id in P198_N2_CITATIONS:
    BODY_LINKS[note_id] = [
        ("st-chp7-p198-exeter-introduced-maratta", 2, 114, BODY_198),
        ("st-chp7-p198-english-tourist-collecting", 2, 114, BODY_198),
    ]

PORTRAITS = {
    P197_N2_KILLIGREW: {
        "work": "cand-7269", "sitter": "cand-1342", "artist": "cand-0530",
        "publication": "cand-7255", "locator": "vol. I, p. 114",
        "claim": "Haskell’s p.197 note 2 attributes Thomas Killigrew’s portrait to Giovanni Angelo Canini and dates it to 1651.",
        "reported_date": "1651",
        "mentioned": ["cand-1342", "cand-0530", "cand-7269", "cand-7255"],
    },
    P197_N2_ALTHAM: {
        "work": "cand-7270", "sitter": "cand-0085", "artist": "cand-2236",
        "publication": "cand-7256", "locator": "p. 20",
        "claim": "Haskell’s p.197 note 2 attributes the portrait of James Altham as a hermit to Salvator Rosa and dates it to 1665.",
        "reported_date": "1665", "depicted_as": "hermit",
        "reported_collection_candidate_id": "cand-7271",
        "mentioned": ["cand-0085", "cand-2236", "cand-7270", "cand-7271", "cand-7256"],
    },
    "st-chp7-p197-n2-portrait-attributions": {
        "work": "cand-4024", "sitter": "cand-0162", "artist": "cand-0923",
        "publication": "cand-7256", "locator": "p. 19",
        "claim": "Haskell’s p.197 note 2 attributes Sir Thomas Baines’s portrait to Carlo Dolci and dates it between 1665 and 1670; it names the Fitzwilliam Museum, Cambridge.",
        "reported_date_range": "1665–1670",
        "reported_location_candidate_id": "cand-4893",
        "mentioned": ["cand-0162", "cand-0923", "cand-4024", "cand-4893", "cand-7256"],
    },
}

CITATION_ROWS = {
    P198_N2_CITATIONS[0]: {
        "publication": "cand-4834",
        "locator": "vol. I, pp. 140, 215, 226",
        "claim": "Haskell’s p.198 note 2 cites Pascoli, Vite de’ Pittori, Scultori ed Architetti moderni, vol. I, pp. 140, 215 and 226, as examples connected with Exeter’s collecting and Italian biographical accounts.",
        "quote": "2 See, for instance, Pascoli, l, pp. 140,215,226; Baldinucci, VI, 1728, p. 503; de Dominici, IV, p. 292.",
        "ocr_corrections": [{
            "source_line": 114, "ocr": "Pascoli, l", "reading": "Pascoli, I",
            "basis": "PDF physical page 36.",
        }],
    },
    P198_N2_CITATIONS[1]: {
        "publication": "cand-4846",
        "locator": "vol. VI (1728), p. 503",
        "claim": "Haskell’s p.198 note 2 cites Baldinucci, vol. VI (1728), p. 503, as an example connected with Exeter’s collecting and Italian biographical accounts.",
        "quote": "2 See, for instance, Pascoli, l, pp. 140,215,226; Baldinucci, VI, 1728, p. 503; de Dominici, IV, p. 292.",
    },
    P198_N2_CITATIONS[2]: {
        "publication": "cand-4835",
        "locator": "vol. IV, p. 292",
        "claim": "Haskell’s p.198 note 2 cites de Dominici, vol. IV, p. 292, as an example connected with Exeter’s collecting and Italian biographical accounts.",
        "quote": "2 See, for instance, Pascoli, l, pp. 140,215,226; Baldinucci, VI, 1728, p. 503; de Dominici, IV, p. 292.",
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temp = Path(handle.name)
    temp.replace(path)


def append_unique(items: list, value: object) -> None:
    if value not in items:
        items.append(value)


def make_citation(publication_id: str, locator: str) -> dict:
    return {
        "source_candidate_id": SOURCE_BOOK,
        "publication_candidate_id": publication_id,
        "locator": locator,
    }


def set_true(row: dict, note: str) -> None:
    q = dict(row.get("qualifiers") or {})
    q["relation_candidate"] = True
    q["relation_candidate_note"] = note
    row["qualifiers"] = q


def add_note_links(note_row: dict, body_rows: dict[str, dict], links: list[tuple[str, int, int, str]]) -> None:
    nq = dict(note_row.get("qualifiers") or {})
    body_ids = []
    refs = []
    for body_id, marker, source_line, _body_segment in links:
        body_ids.append(body_id)
        refs.append({
            "marker": marker, "segment_id": NOTES, "source_line": source_line,
            "statement_ids": [body_id],
        })
        body = body_rows[body_id]
        bq = dict(body.get("qualifiers") or {})
        body_refs = list(bq.get("footnote_refs") or [])
        bref = {"marker": marker, "segment_id": NOTES, "source_line": source_line}
        if bref not in body_refs:
            body_refs.append(bref)
        note_ids = list(bq.get("footnote_statement_ids") or [])
        append_unique(note_ids, note_row["statement_id"])
        linked_ids = list(bq.get("linked_footnote_statement_ids") or [])
        append_unique(linked_ids, note_row["statement_id"])
        bq.update({
            "footnote_refs": body_refs,
            "footnote_statement_ids": note_ids,
            "linked_footnote_statement_ids": linked_ids,
            "footnote_body_link_status": "linked",
        })
        body["qualifiers"] = bq

    nq.update({
        "footnote_number": links[0][1],
        "footnote_segment": NOTES,
        "footnote_refs": refs,
        "related_body_statement_ids": body_ids,
        "linked_body_statement_ids": body_ids,
        "footnote_link_status": "linked",
        "footnote_body_link_status": "linked",
        "footnote_text_pending": False,
    })
    note_row["qualifiers"] = nq


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in (STATEMENTS, CANDIDATES, SOURCE, PDF)}
    hashes = {path.name: sha256(data) for path, data in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f"input hashes changed: {hashes}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    guards = {
        107: "Ratti (Soprani/Ratti, II, p. 15)",
        108: "Killigrew by Canini in 1651",
        109: "Burden, pp. 1-25",
        110: "mostly still at Burghley",
        113: "Pascoli, l",
    }
    for index, guard in guards.items():
        if guard not in source_lines[index]:
            raise SystemExit(f"source guard failed at line {index + 1}: {guard}")

    candidates = {
        row["candidate_id"]: row
        for row in csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline=""))
    }
    required_candidates = {
        SOURCE_BOOK, "cand-0593", "cand-5160", "cand-7261",
        "cand-1342", "cand-0530", "cand-7269", "cand-0085", "cand-2236",
        "cand-7270", "cand-7271", "cand-0162", "cand-0923", "cand-4024",
        "cand-4893", "cand-7255", "cand-7256", "cand-7257", "cand-7258",
        "cand-0984", "cand-7237", "cand-7259", "cand-4831", "cand-4834",
        "cand-4846", "cand-4835",
    }
    missing = required_candidates - candidates.keys()
    if missing:
        raise SystemExit(f"required candidates missing: {sorted(missing)}")
    for candidate_id, expected_type in {
        SOURCE_BOOK: "archive", "cand-0593": "person", "cand-5160": "archive",
        "cand-1342": "person", "cand-0530": "person", "cand-7269": "work",
        "cand-0085": "person", "cand-2236": "person", "cand-7270": "work",
        "cand-0162": "person", "cand-0923": "person", "cand-4024": "work",
        "cand-4893": "institution", "cand-0984": "person", "cand-7237": "place",
        "cand-7255": "archive", "cand-7256": "archive", "cand-7257": "archive",
        "cand-7258": "place", "cand-7259": "archive", "cand-4831": "archive",
        "cand-4834": "archive", "cand-4846": "archive", "cand-4835": "archive",
    }.items():
        if candidates[candidate_id].get("suggested_type") != expected_type:
            raise SystemExit(f"candidate type changed: {candidate_id}")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("statement IDs are not unique")
    if NEW_IDS & by_id.keys():
        raise SystemExit(f"new statement IDs already exist: {sorted(NEW_IDS & by_id.keys())}")
    actual_unset = {
        row["statement_id"] for row in rows
        if row.get("segment_id") == NOTES
        and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    if actual_unset != UNSET_IDS:
        raise SystemExit(f"footnote segment unset set differs: {sorted(actual_unset ^ UNSET_IDS)}")

    expected_note_meta = {
        "st-chp7-p197-n1-cassana-date-conflict": (108, 1, ["st-chp7-p197-queen-anne-employs-cassana"]),
        "st-chp7-p197-n2-portrait-attributions": (109, 2, ["st-chp7-p197-tourist-portrait-examples"]),
        "st-chp7-p197-n4-isham-pictures-lamport": (110, 4, [
            "st-chp7-p197-isham-acquired-paintings-with-advice",
            "st-chp7-p197-isham-commissions-in-rome",
            "st-chp7-p197-isham-mythological-pictures",
            "st-chp7-p197-isham-portrait-maratta",
        ]),
        "st-chp7-p197-n5-exeter-pictures-burghley": (111, 5, [
            "st-chp7-p197-exeter-ordered-nine-dolci",
            "st-chp7-p197-exeter-ordered-fifteen-giordano",
            "st-chp7-p197-exeter-collected-maratta-rome",
        ]),
        "st-chp7-p198-n2-biographical-citations": (114, 2, [
            "st-chp7-p198-exeter-introduced-maratta",
            "st-chp7-p198-english-tourist-collecting",
        ]),
    }
    for note_id, (line, marker, body_ids) in expected_note_meta.items():
        row = by_id[note_id]
        q = row.get("qualifiers") or {}
        if row.get("segment_id") != NOTES or q.get("source_line_start") != line or q.get("footnote_marker") != marker:
            raise SystemExit(f"note location changed: {note_id}")
        if q.get("linked_body_statement_ids") != body_ids:
            raise SystemExit(f"reviewed body links changed: {note_id}")
        for body_id in body_ids:
            if body_id not in by_id or by_id[body_id].get("segment_id") not in {BODY_197, BODY_198}:
                raise SystemExit(f"linked body row missing or moved: {note_id} -> {body_id}")
            body_marker = (by_id[body_id].get("qualifiers") or {}).get("footnote_marker")
            if body_marker is not None and body_marker != marker:
                raise SystemExit(f"body footnote marker changed: {body_id}")

    note_rows = {}
    for row in rows:
        sid = row["statement_id"]
        if sid not in UNSET_IDS:
            continue
        note_rows[sid] = dict(row)
        note_rows[sid]["qualifiers"] = dict(row.get("qualifiers") or {})

    # Preserve the existing Cassana conflict, adding normalized bibliography references.
    cassana = note_rows["st-chp7-p197-n1-cassana-date-conflict"]
    cq = dict(cassana["qualifiers"])
    cq.update({
        "citations": [
            make_citation("cand-7261", "printed at end of book after imprimatur"),
            make_citation("cand-5160", "vol. II, p. 15"),
        ],
        "citation_publication_candidate_id": "cand-5160",
        "citation_locator": "Soprani/Ratti, vol. II, p. 15; Agnelli printed at end of book after imprimatur",
        "cited_material_not_independently_consulted": True,
        "relation_candidate": True,
        "relation_candidate_note": "This records Haskell’s footnote report of Ratti’s 1713 date and its conflict with the body’s 1714 date. Preserve both claims and the unknown arrival date/place of death; the cited pages were not independently consulted and no S6 edge is created.",
    })
    cassana["qualifiers"] = cq
    add_note_links(cassana, by_id, BODY_LINKS[cassana["statement_id"]])

    # Split the compound portrait note into work-to-artist attributions; retain the old ID for Baines.
    portrait_template = note_rows["st-chp7-p197-n2-portrait-attributions"]
    portrait_template["subject_candidate_id"] = "cand-4024"
    portrait_template["object_candidate_id"] = "cand-0923"
    portrait_template["predicate"] = "attributed_to"
    for sid, info in PORTRAITS.items():
        row = dict(portrait_template if sid == "st-chp7-p197-n2-portrait-attributions" else portrait_template)
        row["statement_id"] = sid
        row["subject_candidate_id"] = info["work"]
        row["object_candidate_id"] = info["artist"]
        row["predicate"] = "attributed_to"
        q = dict(portrait_template["qualifiers"])
        q.update({
            "claim": info["claim"],
            "qualification": "This is Haskell’s footnote attribution and date. Vertue or Italian Art and Britain is cited but the cited page and collection or museum record were not independently checked. No one-to-one mapping is inferred between the three sitters and body Plate references 30a, 30b and 31a.",
            "speaker": "Haskell",
            "text_layer": "authorial footnote attribution",
            "sitter_candidate_id": info["sitter"],
            "citation_publication_candidate_id": info["publication"],
            "citation_locator": info["locator"],
            "citations": [make_citation(info["publication"], info["locator"])],
            "cited_material_not_independently_consulted": True,
            "mentioned_candidate_ids": info["mentioned"],
            "relation_candidate": True,
            "relation_candidate_note": "Haskell explicitly attributes this portrait to the named artist in p.197 note 2. Attribution, date and sitter are retained as the footnote’s claim; no formal S6 edge is created.",
        })
        for key in ("reported_date", "reported_date_range", "depicted_as",
                    "reported_collection_candidate_id", "reported_location_candidate_id"):
            if key in info:
                q[key] = info[key]
        row["qualifiers"] = q
        note_rows[sid] = row
        add_note_links(row, by_id, BODY_LINKS[sid])

    # Preserve the Lamport and Burghley scope statements and normalize their citations.
    ish = note_rows["st-chp7-p197-n4-isham-pictures-lamport"]
    iq = dict(ish["qualifiers"])
    iq.update({
        "citations": [make_citation("cand-7257", "pp. 1–25")],
        "citation_publication_candidate_id": "cand-7257",
        "citation_locator": "Burden, pp. 1–25",
        "cited_material_not_independently_consulted": True,
        "relation_candidate": True,
        "relation_candidate_note": "This retains the footnote’s collective statement that the pictures discussed for Isham are at Lamport Hall; individual objects and current records remain unidentified, and Burden was not independently consulted.",
    })
    ish["qualifiers"] = iq
    add_note_links(ish, by_id, BODY_LINKS[ish["statement_id"]])

    exeter = note_rows["st-chp7-p197-n5-exeter-pictures-burghley"]
    eq = dict(exeter["qualifiers"])
    eq.update({
        "citations": [
            make_citation("cand-7259", "p. 57"),
            make_citation("cand-4831", "p. 98"),
        ],
        "citation_locator": "Waterhouse (1960), p. 57; Bellori (1942), p. 98",
        "cited_material_not_independently_consulted": True,
        "relation_candidate": True,
        "relation_candidate_note": "This retains Haskell’s qualified report that Exeter’s pictures are mostly still at Burghley. The note does not identify each picture or establish a current inventory; cited works were not independently consulted.",
    })
    exeter["qualifiers"] = eq
    add_note_links(exeter, by_id, BODY_LINKS[exeter["statement_id"]])

    # Split p.198 note 2 into one book-to-publication citation per cited biography.
    citation_template = note_rows["st-chp7-p198-n2-biographical-citations"]
    original_quote = citation_template.get("original_quote")
    for sid, info in CITATION_ROWS.items():
        row = dict(citation_template)
        row["statement_id"] = sid
        row["subject_candidate_id"] = SOURCE_BOOK
        row["object_candidate_id"] = info["publication"]
        row["predicate"] = "cites"
        row["original_quote"] = info["quote"]
        q = dict(citation_template["qualifiers"])
        q.update({
            "claim": info["claim"],
            "qualification": "This records the locator printed in Haskell’s footnote; the cited passage was not independently consulted and the citation does not validate the biographical claim.",
            "speaker": "Haskell footnote",
            "text_layer": "bibliographic citation to publication",
            "citation_candidate_id": None,
            "citation_publication_candidate_id": info["publication"],
            "citation_locator": info["locator"],
            "citations": [make_citation(info["publication"], info["locator"])],
            "cited_material_not_independently_consulted": True,
            "mentioned_candidate_ids": [SOURCE_BOOK, "cand-0984", info["publication"]],
            "relation_candidate": True,
            "relation_candidate_note": "Haskell’s note explicitly cites this publication and locator. The cited material was not independently consulted; no S6 edge is created.",
        })
        if "ocr_corrections" in info:
            q["ocr_corrections"] = info["ocr_corrections"]
        else:
            q.pop("ocr_corrections", None)
        row["qualifiers"] = q
        note_rows[sid] = row
        add_note_links(row, by_id, BODY_LINKS[sid])

    # Apply classifications and backlinks to original rows, replacing the two compounds with atomized rows.
    additions = [note_rows[sid] for sid in NEW_IDS]
    emitted = []
    for source_row in rows:
        sid = source_row["statement_id"]
        if sid in UNSET_IDS:
            if sid == "st-chp7-p198-n2-biographical-citations":
                emitted.extend(note_rows[citation_id] for citation_id in P198_N2_CITATIONS)
                continue
            emitted.append(note_rows[sid])
        elif sid in by_id and sid in {body_id for links in BODY_LINKS.values() for body_id, *_ in links}:
            emitted.append(by_id[sid])
        else:
            emitted.append(source_row)
    # The two new portrait rows and three split citations are placed after their preserved source rows.
    insertion_after = {
        "st-chp7-p197-n2-portrait-attributions": [P197_N2_KILLIGREW, P197_N2_ALTHAM],
    }
    final_rows = []
    for row in emitted:
        final_rows.append(row)
        final_rows.extend(note_rows[sid] for sid in insertion_after.get(row["statement_id"], []))

    counts = {
        "statements": len(final_rows),
        "True": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in final_rows),
        "False": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in final_rows),
        "unset": sum(row.get("qualifiers", {}).get("relation_candidate") is None for row in final_rows),
    }
    expected_counts = {"statements": 14193, "True": 8728, "False": 3431, "unset": 2034}
    if counts != expected_counts:
        raise SystemExit(f"unexpected post-counts: {counts}")

    final_by_id = {row["statement_id"]: row for row in final_rows}
    for note_id, links in BODY_LINKS.items():
        note = final_by_id[note_id]
        nq = note.get("qualifiers") or {}
        if nq.get("relation_candidate") is not True or nq.get("footnote_body_link_status") != "linked":
            raise SystemExit(f"note classification/link status failed: {note_id}")
        for body_id, marker, source_line, _segment in links:
            bq = final_by_id[body_id].get("qualifiers") or {}
            if note_id not in bq.get("footnote_statement_ids", []):
                raise SystemExit(f"body backlink missing: {body_id} -> {note_id}")
            if not any(ref.get("marker") == marker and ref.get("segment_id") == NOTES
                       and ref.get("source_line") == source_line for ref in bq.get("footnote_refs", [])):
                raise SystemExit(f"body footnote reference missing: {body_id} -> {note_id}")
    for sid in NEW_IDS:
        if final_by_id[sid]["qualifiers"].get("relation_candidate") is not True:
            raise SystemExit(f"new statement not classified true: {sid}")
    for sid, info in PORTRAITS.items():
        row = final_by_id[sid]
        if row.get("predicate") != "attributed_to" or row.get("subject_candidate_id") != info["work"] or row.get("object_candidate_id") != info["artist"]:
            raise SystemExit(f"portrait atomization validation failed: {sid}")
    for sid, info in CITATION_ROWS.items():
        row = final_by_id[sid]
        if row.get("predicate") != "cites" or row.get("subject_candidate_id") != SOURCE_BOOK or row.get("object_candidate_id") != info["publication"]:
            raise SystemExit(f"citation atomization validation failed: {sid}")

    after = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in final_rows) + "\n").encode("utf-8")
    after_hash = sha256(after)
    report = {
        "mode": "apply" if args.apply else "dry_run",
        "segment": NOTES,
        "classified_true": 9,
        "classified_false": 0,
        "split_compound_statements": 2,
        "new_statement_ids": sorted(NEW_IDS),
        "post_counts": counts,
        "before_sha256": hashes,
        "after_statement_sha256": after_hash,
        "backup": str(BACKUP.relative_to(ROOT)),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print("dry-run only; no files changed")
        return
    if BACKUP.exists():
        raise SystemExit(f"recovery copy already exists: {BACKUP}")
    BACKUP.write_bytes(raw[STATEMENTS])
    atomic_write(STATEMENTS, after)
    if sha256(STATEMENTS.read_bytes()) != after_hash:
        raise SystemExit("post-write statement hash mismatch")
    print("applied; recovery copy written; statement hash verified")


if __name__ == "__main__":
    main()
