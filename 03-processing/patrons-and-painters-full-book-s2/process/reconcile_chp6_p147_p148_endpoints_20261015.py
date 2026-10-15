from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE_DIR = ROOT / "04-knowledge/tables"
STATEMENTS = TABLE_DIR / "book-statements.jsonl"
CANDIDATES = TABLE_DIR / "entity-candidates.csv"
MENTIONS = TABLE_DIR / "mentions.csv"
SEGMENTS = TABLE_DIR / "segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/06_CHP-6_sec_i.md"
EXPECTED_HASHES = {
    STATEMENTS: "99187a939f60f6b09953fd3bb372385bbf9fad527142549f551aac57c6572182",
    CANDIDATES: "541bf5d25db59875b0f2c60c28e6e4eeefcdbdd3662dd819f7b237f110cae52c",
    MENTIONS: "eb85670ed2b6b0592d2d4486bd4d561abc6301b4ce5fcbb989a82ff72066555d",
}
SOURCE_SHA256 = "e1bf27cf13961032d4587a1787a1b89f00a9076cf7a8c9dd4434000e84add42d"
SEGMENT_HASHES = {
    "chp-6:06_CHP-6_sec_i:l13-24": "0a569417f685dd10ec46e87e4344c0866bed38be4c414f121b5c6766f9a1fee6",
    "chp-6:06_CHP-6_sec_i:l26-36": "87347777bd77eaf594e5793119fc62b237f3108377c16f7a01725bd93d351872",
    "chp-6:06_CHP-6_sec_i:l38-46": "06c7abb4964adff60a27ef32f3569d5fcf93a453262cf7b41021359e35326c0f",
}
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp6-p147-p148-endpoints-reconciled-20261015"),
    CANDIDATES: CANDIDATES.with_name("entity-candidates.csv.bak-s2-chp6-p147-p148-endpoints-reconciled-20261015"),
    MENTIONS: MENTIONS.with_name("mentions.csv.bak-s2-chp6-p147-p148-endpoints-reconciled-20261015"),
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12396",
        "index_entry_id": "",
        "canonical_name": "Threatened investigation of the Barberini family's income",
        "index_page_range": "",
        "suggested_type": "event",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says an investigation of the Barberini family's income was threatened before the family fled. The passage does not say that the investigation began, and does not identify its authority, date, or scope; retain the threatened status.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-6:06_CHP-6_sec_i:l13-24#L17",
    },
    {
        "candidate_id": "cand-12397",
        "index_entry_id": "",
        "canonical_name": "Unidentified public and private projects undertaken by Camillo Pamfili (p. 148)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "A source-defined set of additional projects that Haskell says Camillo undertook after returning to Rome. The projects are not listed or individually identified; the taxonomy has no generic project-group type, so leave type open.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-6:06_CHP-6_sec_i:l26-36#L36",
    },
    {
        "candidate_id": "cand-12398",
        "index_entry_id": "",
        "canonical_name": "Innocent X's planned family palace and ecclesiastical building programme",
        "index_page_range": "",
        "suggested_type": "event",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell describes an intended construction programme, not a completed event. The passage names building types but does not identify all structures; do not assign the adjacent Piazza Navona palace or later buildings without evidence.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-6:06_CHP-6_sec_i:l13-24#L19",
    },
    {
        "candidate_id": "cand-12399",
        "index_entry_id": "",
        "canonical_name": "Financial troubles during Innocent X's reign (Haskell's source-defined condition)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell identifies financial troubles as the condition that prevented the planned Lateran ceiling replacement. This passage does not define a discrete event or a separately named concept, so retain the source-bounded condition with type open.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-6:06_CHP-6_sec_i:l26-36#L29",
    },
    {
        "candidate_id": "cand-12400",
        "index_entry_id": "",
        "canonical_name": "Planned vault for replacing St John Lateran's sixteenth-century wooden ceiling",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "The planned architectural work is the vault intended to replace the Lateran's sixteenth-century wooden ceiling. It is distinct from cand-6277, the complete remodelling project; the planner's identity, design, and execution are not established here, and Haskell says the replacement did not occur.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-6:06_CHP-6_sec_i:l26-36#L29",
    },
]

NEW_MENTIONS = [
    {
        "mention_id": "m-chp6-p147-income-investigation-threatened",
        "segment_id": "chp-6:06_CHP-6_sec_i:l13-24",
        "candidate_id": "cand-12396",
        "surface_form": "an investigation of their incomes",
        "start_char": "1772",
        "end_char": "1805",
        "note": "The threatened investigation is the event context for the Barberini family's flight; the source does not say it began.",
    },
    {
        "mention_id": "m-chp6-p147-innocent-building-program",
        "segment_id": "chp-6:06_CHP-6_sec_i:l13-24",
        "candidate_id": "cand-12398",
        "surface_form": "the usual great family palace and ecclesiastical buildings",
        "start_char": "2112",
        "end_char": "2170",
        "note": "The object of Innocent X's stated intention to erect; the passage does not identify the complete set of buildings.",
    },
    {
        "mention_id": "m-chp6-p148-financial-troubles",
        "segment_id": "chp-6:06_CHP-6_sec_i:l26-36",
        "candidate_id": "cand-12399",
        "surface_form": "the financial troubles which afflicted Innocent’s reign",
        "start_char": "762",
        "end_char": "817",
        "note": "Haskell's source-bounded condition, stated as the cause of the unrealized ceiling replacement.",
    },
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_open(row: dict) -> bool:
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def append_unique(values: list[str], value: str) -> list[str]:
    return values if value in values else values + [value]


def csv_bytes(rows: list[dict], fields: list[str], has_bom: bool) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8-sig" if has_bom else "utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if digest(raw[path]) != expected:
            raise ValueError(f"protected table changed: {path.name} ({digest(raw[path])})")
    if digest(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise ValueError("chapter 6 source asset changed")

    segments = {
        row["segment_id"]: row
        for row in (
            json.loads(line)
            for line in (TABLE_DIR / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        )
    }
    for segment_id, expected in SEGMENT_HASHES.items():
        segment = segments.get(segment_id)
        if not segment or segment.get("sha256") != expected or segment.get("asset_sha256") != SOURCE_SHA256:
            raise ValueError(f"reviewed segment changed: {segment_id}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = {
        "chp-6:06_CHP-6_sec_i:l13-24": "\n".join(source_lines[12:24]),
        "chp-6:06_CHP-6_sec_i:l26-36": "\n".join(source_lines[25:36]),
        "chp-6:06_CHP-6_sec_i:l38-46": "\n".join(source_lines[37:46]),
    }
    for mention in NEW_MENTIONS:
        text = segment_text[mention["segment_id"]]
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if text[start:end] != mention["surface_form"]:
            raise ValueError(f"source span mismatch for {mention['mention_id']}: {text[start:end]!r}")

    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statements}
    if len(statement_by_id) != len(statements):
        raise ValueError("duplicate statement IDs")
    before_open = sum(is_open(row) for row in statements)
    before_no_reason = sum(
        is_open(row) and not (row.get("qualifiers") or {}).get("open_endpoint_reason")
        for row in statements
    )
    if (before_open, before_no_reason) != (388, 71):
        raise ValueError(f"unexpected initial open-endpoint state: {(before_open, before_no_reason)}")
    candidate_reader = csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline=""))
    candidate_fields = candidate_reader.fieldnames
    candidates = list(candidate_reader)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_reader = csv.DictReader(io.StringIO(raw[MENTIONS].decode("utf-8-sig"), newline=""))
    mention_fields = mention_reader.fieldnames
    mentions = list(mention_reader)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(candidate_by_id) != len(candidates) or len(mention_by_id) != len(mentions):
        raise ValueError("duplicate candidate or mention IDs")

    target_ids = {
        "st-chp6-p147-barberini-family-flees",
        "st-chp6-p147-camillo-military-appointments",
        "st-chp6-p147-camillo-resigns-cardinalate",
        "st-chp6-p147-innocent-building-intention",
        "st-chp6-p148-artistic-life-revival-partial",
        "st-chp6-p148-artistic-life-revived-after-camillo-return",
        "st-chp6-p148-camillo-other-projects",
        "st-chp6-p148-cortona-first-commission",
        "st-chp6-p148-cortona-palace-gallery-commission",
        "st-chp6-p148-financial-ceiling-constraint",
    }
    for statement_id in target_ids:
        if statement_id not in statement_by_id:
            raise ValueError(f"missing expected statement: {statement_id}")
    for cid in (row["candidate_id"] for row in NEW_CANDIDATES):
        if cid in candidate_by_id:
            raise ValueError(f"candidate ID already exists: {cid}")
    for mid in (row["mention_id"] for row in NEW_MENTIONS):
        if mid in mention_by_id:
            raise ValueError(f"mention ID already exists: {mid}")

    def require_state(statement_id: str, subject: str | None, object_: str | None) -> dict:
        row = statement_by_id[statement_id]
        if row.get("subject_candidate_id") != subject or row.get("object_candidate_id") != object_:
            raise ValueError(f"unexpected endpoint state for {statement_id}")
        q = row.get("qualifiers") or {}
        if q.get("relation_candidate") is not True or q.get("open_endpoint_reason"):
            raise ValueError(f"unexpected classification or endpoint reason for {statement_id}")
        return row

    require_state("st-chp6-p147-barberini-family-flees", "cand-3464", None)
    require_state("st-chp6-p147-camillo-military-appointments", None, "cand-1814")
    require_state("st-chp6-p147-camillo-resigns-cardinalate", "cand-1814", None)
    require_state("st-chp6-p147-innocent-building-intention", "cand-1819", None)
    require_state("st-chp6-p148-artistic-life-revival-partial", "cand-4500", None)
    require_state("st-chp6-p148-artistic-life-revived-after-camillo-return", "cand-1814", None)
    require_state("st-chp6-p148-camillo-other-projects", "cand-1814", None)
    require_state("st-chp6-p148-cortona-first-commission", "cand-0342", None)
    require_state("st-chp6-p148-cortona-palace-gallery-commission", "cand-0342", "cand-0353")
    require_state("st-chp6-p148-financial-ceiling-constraint", None, "cand-6277")
    if candidate_by_id["cand-0353"]["suggested_type"] != "person" or candidate_by_id["cand-11957"]["suggested_type"] != "work":
        raise ValueError("expected artist/work candidate types changed")
    expected_mentions = {
        "m-chp6-p148-017": "cand-6277",
        "m-chp6-p148-039": "cand-0353",
        "m-chp6-p148-061": "cand-1814",
    }
    for mention_id, candidate_id in expected_mentions.items():
        if mention_by_id[mention_id]["candidate_id"] != candidate_id:
            raise ValueError(f"expected mention mapping changed: {mention_id}")
    if "cand-12395" not in candidate_by_id:
        raise ValueError("candidate sequence changed; reassess new IDs")

    for row in NEW_CANDIDATES:
        candidates.append(row)
    for row in NEW_MENTIONS:
        mentions.append(row)
    candidate_by_id.update({row["candidate_id"]: row for row in NEW_CANDIDATES})
    mention_by_id.update({row["mention_id"]: row for row in NEW_MENTIONS})

    mention_by_id["m-chp6-p148-017"]["candidate_id"] = "cand-12400"
    mention_by_id["m-chp6-p148-017"]["note"] = "The planned vault is the intended replacement work; it is distinct from the complete Lateran remodelling project and was not carried out in this account."
    mention_by_id["m-chp6-p148-061"]["candidate_id"] = "cand-12397"
    mention_by_id["m-chp6-p148-061"]["note"] = "The source-defined set of additional public and private projects; individual projects are not listed."

    barberini = statement_by_id["st-chp6-p147-barberini-family-flees"]
    barberini["object_candidate_id"] = "cand-12396"
    barberini["qualifiers"]["mentioned_candidate_ids"] = append_unique(barberini["qualifiers"]["mentioned_candidate_ids"], "cand-12396")
    barberini["qualifiers"]["relation_candidate_note"] = "Haskell explicitly reports that the Barberini family fled when an investigation of their income was threatened. The threatened investigation is preserved as a prospective event; the passage does not identify its authority or say it began."
    barberini["qualifiers"].pop("open_endpoint_reason", None)

    military = statement_by_id["st-chp6-p147-camillo-military-appointments"]
    military["qualifiers"]["open_endpoint_reason"] = "The passive wording names Camillo as appointee but does not identify the person or body that made the appointments. The Pope's role in the surrounding passage is insufficient to infer the appointing agent."
    cardinalate = statement_by_id["st-chp6-p147-camillo-resigns-cardinalate"]
    cardinalate["qualifiers"]["open_endpoint_reason"] = "The passage identifies Camillo's cardinalate as the role he resigned, but does not identify a separately modeled office entity. Preserve the role in the claim and leave the object open rather than creating an unsupported role candidate."

    building = statement_by_id["st-chp6-p147-innocent-building-intention"]
    building["object_candidate_id"] = "cand-12398"
    building["qualifiers"]["mentioned_candidate_ids"] = append_unique(building["qualifiers"]["mentioned_candidate_ids"], "cand-12398")
    building["qualifiers"]["relation_candidate_note"] = "The source explicitly attributes an intended construction programme to Innocent X. It names a family palace and ecclesiastical buildings but does not enumerate every structure; no adjacent or later building is assigned without evidence."
    building["qualifiers"].pop("open_endpoint_reason", None)

    partial = statement_by_id["st-chp6-p148-artistic-life-revival-partial"]
    partial["qualifiers"]["relation_candidate"] = False
    partial["qualifiers"]["relation_candidate_note"] = "This is Haskell's evaluative temporal summary, completed by the examples on p. 149. Preserve 'most beautiful and familiar' as the author's assessment; creator-to-work claims are recorded separately, and this statement does not assert a relation between the represented entities."
    partial["qualifiers"].pop("open_endpoint_reason", None)

    revival = statement_by_id["st-chp6-p148-artistic-life-revived-after-camillo-return"]
    revival["qualifiers"]["open_endpoint_reason"] = "Haskell describes Roman artistic life as reviving after Camillo's return but does not identify a bounded revival event or specific target. Preserve the temporal association without treating the return as its cause or using Rome as the object."

    projects = statement_by_id["st-chp6-p148-camillo-other-projects"]
    projects["object_candidate_id"] = "cand-12397"
    projects["qualifiers"]["mentioned_candidate_ids"] = append_unique(projects["qualifiers"]["mentioned_candidate_ids"], "cand-12397")
    projects["qualifiers"]["relation_candidate_note"] = "The source defines a set of additional public and private projects undertaken by Camillo; individual projects are not listed, so the group remains untyped and source-bounded."
    projects["qualifiers"].pop("open_endpoint_reason", None)

    commission = statement_by_id["st-chp6-p148-cortona-first-commission"]
    commission["object_candidate_id"] = "cand-11957"
    commission["qualifiers"]["mentioned_candidate_ids"] = append_unique(commission["qualifiers"]["mentioned_candidate_ids"], "cand-11957")
    commission["qualifiers"]["relation_candidate_note"] = "Haskell dates Cortona's first official commission to the end of 1651; p. 149 identifies the commissioned work as the Aeneid fresco group. The source does not name who assigned the commission."
    commission["qualifiers"].pop("open_endpoint_reason", None)

    gallery = statement_by_id["st-chp6-p148-cortona-palace-gallery-commission"]
    gallery["object_candidate_id"] = "cand-11957"
    gallery["qualifiers"]["mentioned_candidate_ids"] = [cid for cid in gallery["qualifiers"]["mentioned_candidate_ids"] if cid != "cand-0353"]
    gallery["qualifiers"]["mentioned_candidate_ids"] = append_unique(gallery["qualifiers"]["mentioned_candidate_ids"], "cand-11957")
    gallery["qualifiers"]["relation_candidate_note"] = "P. 148 identifies the commission's purpose and site; p. 149 names its object as Cortona's Scenes from the Aeneid fresco group (cand-11957). The gallery-ceiling phrase is not an artist identity."
    mention_by_id["m-chp6-p148-039"]["candidate_id"] = "cand-11957"
    mention_by_id["m-chp6-p148-039"]["note"] = "The gallery ceiling is the site of Cortona's commission; p. 149 identifies the commissioned Aeneid fresco group as cand-11957."

    financial = statement_by_id["st-chp6-p148-financial-ceiling-constraint"]
    financial["subject_candidate_id"] = "cand-12399"
    financial["object_candidate_id"] = "cand-12400"
    financial["qualifiers"]["mentioned_candidate_ids"] = append_unique(financial["qualifiers"]["mentioned_candidate_ids"], "cand-12399")
    financial["qualifiers"]["mentioned_candidate_ids"] = append_unique(financial["qualifiers"]["mentioned_candidate_ids"], "cand-12400")
    financial["qualifiers"]["relation_candidate_note"] = "Haskell attributes the unrealized Lateran ceiling replacement to financial troubles during Innocent X's reign. The source-defined condition and planned vault are now separate endpoints; the planner's identity remains unresolved, and the vault is distinct from the complete remodelling project cand-6277."
    financial["qualifiers"].pop("open_endpoint_reason", None)

    statement_output = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in statements).encode("utf-8")
    candidate_output = csv_bytes(candidates, candidate_fields, raw[CANDIDATES].startswith(b"\xef\xbb\xbf"))
    mention_output = csv_bytes(mentions, mention_fields, raw[MENTIONS].startswith(b"\xef\xbb\xbf"))
    outputs = {STATEMENTS: statement_output, CANDIDATES: candidate_output, MENTIONS: mention_output}

    after_open = sum(is_open(row) for row in statements)
    no_reason = sum(
        is_open(row) and not (row.get("qualifiers") or {}).get("open_endpoint_reason")
        for row in statements
    )
    if (before_open, after_open, no_reason) != (388, 382, 62):
        raise ValueError(f"unexpected open endpoint transition: {before_open}->{after_open}, no_reason={no_reason}")
    if len(NEW_CANDIDATES) != 5 or len(NEW_MENTIONS) != 3:
        raise ValueError("unexpected candidate or mention batch size")

    print("reviewed=chapter 6 pp.147-149 cross-page endpoint semantics")
    print("changes=5 source-bounded candidates, 3 new exact mentions, 2 existing mentions remapped, 1 relation flag correction, 5 relation rows completed, 3 explicit open reasons, 1 artist-to-work mention correction")
    print(f"open_endpoints={before_open}->{after_open}; open_without_reason={before_no_reason}->{no_reason}")
    for path, output in outputs.items():
        print(f"{path.name} sha256 {digest(raw[path])}->{digest(output)}")
    if args.preview:
        return 0

    for backup in BACKUPS.values():
        if backup.exists():
            raise FileExistsError(f"recovery copy already exists: {backup.name}")
    temps = {path: path.with_name(path.name + ".tmp-s2-chp6-p147-p148-endpoints-reconciled-20261015") for path in outputs}
    if any(path.exists() for path in temps.values()):
        raise FileExistsError("a protected temporary output already exists")
    for path, backup in BACKUPS.items():
        shutil.copy2(path, backup)
    try:
        for path, output in outputs.items():
            temps[path].write_bytes(output)
        for path in outputs:
            temps[path].replace(path)
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for path, backup in BACKUPS.items():
            shutil.copy2(backup, path)
        raise
    print("backups=" + ", ".join(path.name for path in BACKUPS.values()))
    print("applied_hashes=" + ", ".join(f"{path.name}:{digest(path.read_bytes())}" for path in outputs))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
