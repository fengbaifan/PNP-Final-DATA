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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_v.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-7.pdf"
SEGMENT = "chp-7:07_CHP-7_sec_v:l9-18"
BODY = "st-chp7-p200-v-daun-first-viceroy-and-patronage"
NOTES_LINE = 18
BACKUP = STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp7-p200-sec-v-l9-18-20261013")

EXPECTED_HASHES = {
    STATEMENTS.name: "46a82c632c079978b0fc559c11a3344e793f2b9d058540730f6f9535c9f0f723",
    CANDIDATES.name: "9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d",
    SOURCE.name: "956054d03a849749a1f7a0dbf0eade81c5cb1252a284cc26d024a7f9f134b432",
    PDF.name: "eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212",
}

TRUE_NOTES = {
    "st-chp7-p200-v-austrians-conquer-lombardy":
        "This records Haskell’s source-attributed statement that Austria conquered Lombardy; it does not independently verify the campaign.",
    "st-chp7-p200-v-austrians-seize-naples-from-spaniards":
        "This records Haskell’s source-attributed statement that Austria seized Naples from Spain; keep the political actors distinct from the geographic place.",
    "st-chp7-p200-v-chiarini-frescoes-daun-palace":
        "This records Haskell’s attribution of the fresco decoration of Daun’s Viennese palace to Chiarini; no date, room or fresco subject is supplied.",
    "st-chp7-p200-v-commanders-commission-local-artists":
        "This retains Haskell’s collective account of commanders commissioning local artists between campaigns; no individual commander-to-artist or city assignment is inferred.",
    "st-chp7-p200-v-contemporary-painting-interest-at-versailles":
        "This preserves Haskell’s attributed claim that the occasion stimulated interest among some younger art lovers tiring of the style he calls official.",
    "st-chp7-p200-v-daun-appointment-and-return":
        "This records the source’s appointment and return chronology for Daun while preserving the approximate duration and avoiding inferred exact dates.",
    "st-chp7-p200-v-daun-first-viceroy-and-patronage":
        "This retains Haskell’s account of Daun’s 1707 viceroyalty and comparative patronage; the regime and predecessors remain unnamed and ‘rivalled’ remains evaluative.",
    "st-chp7-p200-v-daun-neapolitan-painting-central-europe":
        "This records Haskell’s account of Daun’s role in introducing Neapolitan painting into Central Europe; no complete route or work list is inferred.",
    "st-chp7-p200-v-daun-responsible-for-naples-capture":
        "This preserves Haskell’s attribution of responsibility for the capture of Naples to Daun without generalizing to the full military operation.",
    "st-chp7-p200-v-destrees-introduces-paolo-to-nobles-bankers":
        "This records d’Estrées’s introduction of de Matteis to an unnamed group of influential nobles and bankers; no resulting commission is asserted.",
    "st-chp7-p200-v-destrees-takes-paolo-to-paris":
        "This records d’Estrées taking de Matteis to Paris and does not convert the journey into a claim that de Matteis settled there.",
    "st-chp7-p200-v-destrees-visits-naples-with-philip-v":
        "This retains Haskell’s description of Philip V as the French candidate for the Spanish throne without independently resolving the succession claim.",
    "st-chp7-p200-v-harrach-continues-process-after-1728":
        "This records the continuation of the diffusion process after 1728 by Harrach; ‘most cultivated’ remains Haskell’s evaluation and the S2 OCR correction is retained.",
    "st-chp7-p200-v-italian-commanders-open-continuation":
        "This records the source-described intention of Italian-origin commanders serving in the Imperial army to furnish their Viennese palaces with pictures from their native land; it is not a completed purchase.",
    "st-chp7-p200-v-naples-captured-after-paolos-return":
        "This preserves the source sequence in which Naples was conquered after de Matteis returned; the opposing forces and exact date remain unspecified.",
    "st-chp7-p200-v-noailles-secures-de-ferrari-at-marseilles":
        "This records Noailles persuading de Ferrari to paint pictures for him at Marseilles; the works remain unidentified and ‘soon after’ is not assigned a year.",
    "st-chp7-p200-v-note6-cite-de-dominici":
        "Haskell’s p.200 note 6 cites de Dominici, vol. IV, pp. 295, 332, 435–437 and 444. The cited pages were not independently consulted.",
    "st-chp7-p200-v-note6-cite-pascoli":
        "Haskell’s p.200 note 6 cites Pascoli, vol. II, p. 102. The printed volume numeral is II; the cited page was not independently consulted.",
    "st-chp7-p200-v-note6-cite-tassi":
        "Haskell’s p.200 note 6 cites Tassi, vol. II, p. 64. The cited page was not independently consulted.",
    "st-chp7-p200-v-note6-cite-zanotti":
        "Haskell’s p.200 note 6 cites Zanotti, vol. I, p. 277. The cited page was not independently consulted.",
    "st-chp7-p200-v-note6-daun-commissioned-ghislandi-portrait":
        "This retains Haskell’s footnote report that Daun commissioned a portrait from Ghislandi in Bergamo; the work is unidentified and cited pages were not independently consulted.",
    "st-chp7-p200-v-painters-make-canvases-for-daun-palace":
        "This records Haskell’s collective report that Solimena, del Po and de Matteis produced canvases for Daun’s palace; no title or artist-to-canvas assignment is inferred.",
    "st-chp7-p200-v-paolo-works-for-binchs-and-daun":
        "This preserves Haskell’s report that de Matteis worked for the English Admiral ‘Binchs’ and Daun after the capture; it does not infer formal commissions.",
    "st-chp7-p200-v-parodi-trip-to-england-failed":
        "This records Pekemburgh’s unsuccessful attempt to take Parodi to England; preserve the failed outcome and do not imply a completed move.",
    "st-chp7-p200-v-pekemburgh-arrives-genoa":
        "This records the source’s report that Pekemburgh arrived in Genoa with English ships before 1703; preserve the printed name and approximate date.",
    "st-chp7-p200-v-pekemburgh-commissions-parodi-bust":
        "This records Pekemburgh’s commission of an unidentified bust from Parodi; title, date and location remain unspecified.",
    "st-chp7-p200-v-treaties-confirm-changes-and-patronage-counterpart":
        "This preserves Haskell’s interpretation that the treaties confirmed political changes that had counterparts in patronage; the treaties are not said to cause a commission.",
    "st-chp7-p200-v-victor-amadeus-breaks-from-louis-xiv":
        "This records Haskell’s political characterization of Victor Amadeus’s break from Louis XIV’s tutelage and emergence as Italy’s leading independent ruler.",
}

CITATIONS = {
    "st-chp7-p200-v-note6-cite-de-dominici": {
        "publication": "cand-4835",
        "locator": "vol. IV, pp. 295, 332, 435–437, 444",
        "claim": "Haskell’s p.200 note 6 cites de Dominici, vol. IV, pp. 295, 332, 435–437 and 444.",
        "qualifier": "Ibid. resolves through the preceding note to de Dominici, vol. IV; these pages were not independently read.",
        "linked_body_ids": [BODY, "st-chp7-p200-v-note6-daun-commissioned-ghislandi-portrait"],
    },
    "st-chp7-p200-v-note6-cite-pascoli": {
        "publication": "cand-4552",
        "locator": "vol. II, p. 102",
        "claim": "Haskell’s p.200 note 6 cites Pascoli, vol. II, p. 102.",
        "qualifier": "The printed volume numeral is II; this bibliographic locator does not independently establish the cited claim, and the page was not consulted.",
        "ocr_corrections": [{
            "source_line": 18, "ocr": "Pascoli, H", "reading": "Pascoli, II",
            "basis": "CHP-7.pdf physical page 38.",
        }],
        "linked_body_ids": [BODY, "st-chp7-p200-v-note6-daun-commissioned-ghislandi-portrait"],
    },
    "st-chp7-p200-v-note6-cite-tassi": {
        "publication": "cand-6590",
        "locator": "vol. II, p. 64",
        "claim": "Haskell’s p.200 note 6 cites Tassi, vol. II, p. 64.",
        "qualifier": "This bibliographic locator does not independently establish the cited claim; the page was not consulted.",
        "linked_body_ids": [BODY, "st-chp7-p200-v-note6-daun-commissioned-ghislandi-portrait"],
    },
    "st-chp7-p200-v-note6-cite-zanotti": {
        "publication": "cand-7115",
        "locator": "vol. I, p. 277",
        "claim": "Haskell’s p.200 note 6 cites Zanotti, vol. I, p. 277.",
        "qualifier": "This bibliographic locator does not independently establish the cited claim; the page was not consulted.",
        "linked_body_ids": [BODY, "st-chp7-p200-v-note6-daun-commissioned-ghislandi-portrait"],
    },
}

EXPECTED_ROWS = {
    "st-chp7-p200-v-austrians-conquer-lombardy": (10, 10),
    "st-chp7-p200-v-austrians-seize-naples-from-spaniards": (10, 10),
    "st-chp7-p200-v-chiarini-frescoes-daun-palace": (14, 14),
    "st-chp7-p200-v-commanders-commission-local-artists": (11, 11),
    "st-chp7-p200-v-contemporary-painting-interest-at-versailles": (12, 13),
    "st-chp7-p200-v-daun-appointment-and-return": (15, 15),
    "st-chp7-p200-v-daun-first-viceroy-and-patronage": (13, 13),
    "st-chp7-p200-v-daun-neapolitan-painting-central-europe": (15, 15),
    "st-chp7-p200-v-daun-responsible-for-naples-capture": (13, 13),
    "st-chp7-p200-v-destrees-introduces-paolo-to-nobles-bankers": (13, 13),
    "st-chp7-p200-v-destrees-takes-paolo-to-paris": (12, 13),
    "st-chp7-p200-v-destrees-visits-naples-with-philip-v": (11, 12),
    "st-chp7-p200-v-harrach-continues-process-after-1728": (15, 16),
    "st-chp7-p200-v-italian-commanders-open-continuation": (17, 17),
    "st-chp7-p200-v-naples-captured-after-paolos-return": (13, 13),
    "st-chp7-p200-v-noailles-secures-de-ferrari-at-marseilles": (11, 11),
    "st-chp7-p200-v-note6-cite-de-dominici": (18, 18),
    "st-chp7-p200-v-note6-cite-pascoli": (18, 18),
    "st-chp7-p200-v-note6-cite-tassi": (18, 18),
    "st-chp7-p200-v-note6-cite-zanotti": (18, 18),
    "st-chp7-p200-v-note6-daun-commissioned-ghislandi-portrait": (18, 18),
    "st-chp7-p200-v-painters-make-canvases-for-daun-palace": (14, 14),
    "st-chp7-p200-v-paolo-works-for-binchs-and-daun": (13, 13),
    "st-chp7-p200-v-parodi-trip-to-england-failed": (11, 11),
    "st-chp7-p200-v-pekemburgh-arrives-genoa": (11, 11),
    "st-chp7-p200-v-pekemburgh-commissions-parodi-bust": (11, 11),
    "st-chp7-p200-v-treaties-confirm-changes-and-patronage-counterpart": (10, 10),
    "st-chp7-p200-v-victor-amadeus-breaks-from-louis-xiv": (10, 10),
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in (STATEMENTS, CANDIDATES, SOURCE, PDF)}
    hashes = {path.name: sha256(data) for path, data in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f"input hashes changed: {hashes}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    if "Count Harrach.7" not in source_lines[15] or "Pascoli, H, p. 102" not in source_lines[17]:
        raise SystemExit("p.200 source/footnote guard failed")
    candidates = {r["candidate_id"]: r for r in csv.DictReader(
        io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")
    )}
    for candidate_id in {"cand-2962", "cand-4835", "cand-4552", "cand-6590", "cand-7115"}:
        if candidates.get(candidate_id, {}).get("suggested_type") != "archive":
            raise SystemExit(f"citation candidate missing or mistyped: {candidate_id}")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("statement IDs are not unique")
    actual_segment_ids = {r["statement_id"] for r in rows if r.get("segment_id") == SEGMENT}
    if actual_segment_ids != set(TRUE_NOTES):
        raise SystemExit(f"segment statement set changed: {sorted(actual_segment_ids ^ set(TRUE_NOTES))}")
    actual_unset = {
        sid for sid in actual_segment_ids
        if (by_id[sid].get("qualifiers") or {}).get("relation_candidate") is None
    }
    if actual_unset != set(TRUE_NOTES):
        raise SystemExit(f"segment unset set changed: {sorted(actual_unset ^ set(TRUE_NOTES))}")

    portrait_id = "st-chp7-p200-v-note6-daun-commissioned-ghislandi-portrait"
    primary = by_id[BODY]
    if (primary.get("segment_id") != SEGMENT
            or (primary.get("qualifiers") or {}).get("footnote_marker") != 6
            or primary.get("qualifiers", {}).get("source_line_start") != 13):
        raise SystemExit("p.200 note 6 body anchor changed")
    for sid, info in CITATIONS.items():
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        if (row.get("predicate") != "footnote_citation" or row.get("subject_candidate_id") is not None
                or row.get("object_candidate_id") != info["publication"]
                or q.get("source_line_start") != NOTES_LINE or q.get("footnote_marker") != 6):
            raise SystemExit(f"citation row changed since review: {sid}")
        if portrait_id not in info["linked_body_ids"] or BODY not in info["linked_body_ids"]:
            raise SystemExit(f"citation/body association missing in plan: {sid}")
        if any(target not in by_id for target in info["linked_body_ids"]):
            raise SystemExit(f"citation target missing: {sid}")

    output = []
    for original in rows:
        sid = original["statement_id"]
        if sid not in TRUE_NOTES:
            output.append(original)
            continue
        row = dict(original)
        q = dict(row.get("qualifiers") or {})
        if (row.get("segment_id") != SEGMENT
                or q.get("source_line_start") != EXPECTED_ROWS[sid][0]
                or q.get("source_line_end") != EXPECTED_ROWS[sid][1]):
            raise SystemExit(f"statement segment/line changed: {sid}")
        q["relation_candidate"] = True
        q["relation_candidate_note"] = TRUE_NOTES[sid]
        if sid in CITATIONS:
            info = CITATIONS[sid]
            publication_id = info["publication"]
            locator = info["locator"]
            row["subject_candidate_id"] = "cand-2962"
            row["object_candidate_id"] = publication_id
            row["predicate"] = "cites"
            q.update({
                "claim": info["claim"],
                "qualification": info["qualifier"],
                "speaker": "Haskell footnote",
                "text_layer": "bibliographic citation to publication",
                "citation_publication_candidate_id": publication_id,
                "citation_locator": locator,
                "citations": [{
                    "source_candidate_id": "cand-2962",
                    "publication_candidate_id": publication_id,
                    "locator": locator,
                }],
                "cited_material_not_independently_consulted": True,
            })
            mentions = list(q.get("mentioned_candidate_ids") or [])
            for candidate_id in ("cand-2962", publication_id):
                append_unique(mentions, candidate_id)
            q["mentioned_candidate_ids"] = mentions
            q["linked_body_statement_ids"] = list(info["linked_body_ids"])
            q["related_body_statement_ids"] = list(info["linked_body_ids"])
            q["footnote_number"] = 6
            q["footnote_segment"] = SEGMENT
            q["footnote_refs"] = [{
                "marker": 6, "segment_id": SEGMENT, "source_line": NOTES_LINE,
                "statement_ids": [BODY],
            }]
            q["footnote_link_status"] = "linked"
            q["footnote_body_link_status"] = "linked"
            q["footnote_text_pending"] = False
            if "ocr_corrections" in info:
                q["ocr_corrections"] = info["ocr_corrections"]
        row["qualifiers"] = q
        output.append(row)

    # Add the marker-6 backlink to the body anchor, preserving any prior note references.
    out_by_id = {row["statement_id"]: row for row in output}
    body_row = out_by_id[BODY]
    bq = dict(body_row.get("qualifiers") or {})
    note_ids = list(bq.get("footnote_statement_ids") or [])
    for sid in TRUE_NOTES:
        if sid.startswith("st-chp7-p200-v-note6-"):
            append_unique(note_ids, sid)
    refs = list(bq.get("footnote_refs") or [])
    body_ref = {"marker": 6, "segment_id": SEGMENT, "source_line": NOTES_LINE}
    if body_ref not in refs:
        refs.append(body_ref)
    bq.update({
        "footnote_statement_ids": note_ids,
        "footnote_refs": refs,
        "footnote_body_link_status": "linked",
    })
    body_row["qualifiers"] = bq

    counts = {
        "statements": len(output),
        "True": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in output),
        "False": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in output),
        "unset": sum(row.get("qualifiers", {}).get("relation_candidate") is None for row in output),
    }
    if counts != {"statements": 14193, "True": 8768, "False": 3433, "unset": 1992}:
        raise SystemExit(f"unexpected post-counts: {counts}")

    for sid, info in CITATIONS.items():
        row = out_by_id[sid]
        q = row["qualifiers"]
        if row["predicate"] != "cites" or row["subject_candidate_id"] != "cand-2962" or row["object_candidate_id"] != info["publication"]:
            raise SystemExit(f"citation normalization failed: {sid}")
        if q.get("citation_locator") != info["locator"] or not q.get("cited_material_not_independently_consulted"):
            raise SystemExit(f"citation metadata failed: {sid}")
    if not set(sid for sid in TRUE_NOTES if sid.startswith("st-chp7-p200-v-note6-")) <= set(bq.get("footnote_statement_ids", [])):
        raise SystemExit("body footnote backlinks incomplete")

    after = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in output) + "\n").encode("utf-8")
    after_hash = sha256(after)
    report = {
        "mode": "apply" if args.apply else "dry_run",
        "segment": SEGMENT,
        "classified_true": len(TRUE_NOTES),
        "classified_false": 0,
        "normalized_citations": len(CITATIONS),
        "ocr_corrections_recorded": 1,
        "footnote_body_backlinks": len(CITATIONS) + 1,
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
