#!/usr/bin/env python3
"""Register the cross-chapter 1762 Joseph Smith sale event.

Default mode is a read-only, preconditioned preview. Apply only after inspecting
the proposed row changes with --apply.
"""
from __future__ import annotations

import argparse
import csv
import difflib
import io
import json
import os
import re
import sys
import uuid
from pathlib import Path


BASE = Path(__file__).resolve().parents[3]
TABLES = BASE / "04-knowledge" / "tables"
CARD_REL = Path("04-knowledge/units/events/joseph-smith-1762-sale-to-george-iii.md")
KU_ID = "units/events/joseph-smith-1762-sale-to-george-iii"
GROUP_ID = "sg3-event-cand-9278"
PROCESS_REF = (
    "patrons-and-painters-full-book-s2#"
    "s3-s4-s5-s6-ch10-p310-smith-sale-20261024"
)
HASKELL_CITATION = (
    "Francis Haskell, Patrons and Painters, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCE_10 = "02-sources/02-Markdown/10_CHP-10_intro.md"
SOURCE_19 = "02-sources/02-Markdown/19_CHP-19Appendix.md"
SEGMENT_19 = "chp-19:19_CHP-19Appendix:l109-124"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool, str]:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    line_ending = "\r\n" if "\r\n" in text else "\n"
    rows = list(csv.DictReader(io.StringIO(text, newline="")))
    if not rows:
        raise ValueError(f"Expected a non-empty CSV: {path}")
    return list(rows[0]), rows, bom, line_ending


def serialize_csv(
    fieldnames: list[str], rows: list[dict[str, str]], bom: bool, line_ending: str
) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream,
        fieldnames=fieldnames,
        extrasaction="ignore",
        lineterminator=line_ending,
    )
    writer.writeheader()
    writer.writerows(rows)
    body = stream.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + body) if bom else body


def jsonl_rows(path: Path) -> tuple[list[str], list[dict], list[str]]:
    raw_lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    rows = [json.loads(line) for line in raw_lines if line.strip()]
    return raw_lines, rows, [str(row["statement_id"]) for row in rows]


def atomic_write(path: Path, data: bytes) -> None:
    temp = path.with_name(path.name + f".{uuid.uuid4().hex}.tmp")
    try:
        temp.write_bytes(data)
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="write the reviewed event registration and S2 endpoint repair",
    )
    args = parser.parse_args()

    paths = {
        name: TABLES / name
        for name in (
            "alignment.csv",
            "book-statements.jsonl",
            "mentions.csv",
            "ku-manifest.csv",
            "relations.csv",
        )
    }
    alignment_cols, alignment, alignment_bom, alignment_eol = read_csv(paths["alignment.csv"])
    mention_cols, mentions, mention_bom, mention_eol = read_csv(paths["mentions.csv"])
    manifest_cols, manifest, manifest_bom, manifest_eol = read_csv(paths["ku-manifest.csv"])
    relation_cols, relations, relation_bom, relation_eol = read_csv(paths["relations.csv"])
    statement_raw, statements, statement_ids = jsonl_rows(paths["book-statements.jsonl"])

    require(len(statements) == 15307, "book-statements baseline changed")
    require(len(mentions) == 26773, "mentions baseline changed")
    require(len(manifest) == 2739, "KU manifest baseline changed")
    require(len(relations) == 1840, "relations baseline changed")
    require(KU_ID not in {row["ku_id"] for row in manifest}, "target KU already exists")
    require((BASE / CARD_REL).is_file(), "prepared event card is missing")
    require(not any(row.get("candidate_id") == "cand-2471" and row.get("external_source") for row in alignment),
            "unexpected external alignment for cand-2471")
    require(not any(row.get("candidate_id") == "cand-9278" and row.get("external_source") for row in alignment),
            "unexpected external alignment for cand-9278")

    primary = {
        row["candidate_id"]: row
        for row in alignment
        if not row.get("external_source")
    }
    c2471 = primary["cand-2471"]
    c9278 = primary["cand-9278"]
    require(c2471["decision"] == "new" and not c2471["ku_id"], "cand-2471 is no longer pending S4")
    require(c9278["decision"] == "new" and not c9278["ku_id"], "cand-9278 is no longer pending S4")

    by_statement = {row["statement_id"]: row for row in statements}
    sale_10_id = "st-chp10-p310-1762-sale-to-george-iii"
    sale_19_id = "st-chp19-p391-smith-1762-sale-to-george-iii"
    will_sale_id = "st-chp19-p391-smith-1761-expectation-and-1762-sale"
    selection_id = "st-chp19-p392-artists-in-1762-sale-selection-inference"
    require(all(sid in by_statement for sid in (sale_10_id, sale_19_id, will_sale_id, selection_id)),
            "one or more source statements changed")
    require("st-chp19-p391-sold-works-in-royal-collection" not in by_statement,
            "new collection statement ID already exists")
    require("st-chp19-p391-smith-catalogued-sold-works" not in by_statement,
            "new catalogue statement ID already exists")
    require("st-chp19-p391-sold-works-most-recognisable-or-traceable" not in by_statement,
            "new traceability statement ID already exists")
    require("rel-1841" not in {row["relation_id"] for row in relations}, "rel-1841 already exists")
    require("rel-1842" not in {row["relation_id"] for row in relations}, "rel-1842 already exists")

    source10_lines = (BASE / SOURCE_10).read_text(encoding="utf-8").splitlines()
    source19_lines = (BASE / SOURCE_19).read_text(encoding="utf-8").splitlines()
    p310_line = source10_lines[487]
    p391_line = source19_lines[116]
    p392_line = source19_lines[117]
    require("in 1762" in p310_line and "King George III" in p310_line, "p.310 source text changed")
    require("Smith sold to George III" in p391_line and "Royal Collection" in p391_line,
            "Appendix 5 p.391 source text changed")
    require("These were" in p391_line and "logued by him" in p392_line,
            "Appendix 5 catalogue source text changed")

    segment_text = "\n".join(source19_lines[108:124])
    paint_start = segment_text.find("paintings and drawings")
    require(paint_start >= 0, "could not locate the p.391 sold-works mention")
    these_start = segment_text.find("These were", paint_start)
    him_start = segment_text.find("him", segment_text.find("logued by him", paint_start))
    recognisable_start = segment_text.find("most of them are recognisable or traceable", paint_start)
    require(these_start >= 0 and him_start >= 0 and recognisable_start >= 0,
            "could not locate exact mention anchors")
    mention_012 = next(row for row in mentions if row["mention_id"] == "m-chp19-p391-012")
    mention_014 = next(row for row in mentions if row["mention_id"] == "m-chp19-p391-014")
    require(mention_012["start_char"] == str(paint_start)
            and mention_012["surface_form"] == "paintings and drawings",
            "p.391 segment character-offset basis changed")
    require(mention_014["candidate_id"] == "cand-2471"
            and mention_014["surface_form"] == "logued by him",
            "catalogue mention was already revised")
    new_mention_id = "m-chp19-p391-041-smith-cataloguer"
    require(new_mention_id not in {row["mention_id"] for row in mentions},
            "new Smith mention ID already exists")

    sale_19 = by_statement[sale_19_id]
    sale_19["subject_candidate_id"] = "cand-2471"
    sale_19["object_candidate_id"] = "cand-1141"
    sale_19["predicate"] = "sale_event_included_george_iii_as_buyer"
    sale_19["qualifiers"] = {
        "source_line_start": 117,
        "source_line_end": 117,
        "printed_page": 391,
        "pdf_physical_page": 6,
        "claim": (
            "Haskell reports that in 1762 Smith sold a very large number of "
            "paintings and drawings to George III."
        ),
        "speaker": "Haskell",
        "text_layer": "authorial report",
        "qualification": (
            "The source gives no exact count and identifies no individual works. "
            "This is the same transaction described at Chapter 10 p.310 and again "
            "at Appendix 5 p.391 L123-124, not a second sale."
        ),
        "mentioned_candidate_ids": ["cand-2471", "cand-1141"],
        "relation_candidate": True,
        "date": "1762",
    }
    sale_19["original_quote"] = (
        "The problem is this: in 1762 Smith sold to George III a very large number "
        "of paintings and drawings"
    )

    new_statements = [
        {
            **sale_19,
            "statement_id": "st-chp19-p391-sold-works-in-royal-collection",
            "subject_candidate_id": "cand-10807",
            "object_candidate_id": "cand-2292",
            "predicate": "sold_works_remained_in_royal_collection",
            "qualifiers": {
                "source_line_start": 117,
                "source_line_end": 117,
                "printed_page": 391,
                "pdf_physical_page": 6,
                "claim": (
                    "Haskell says the paintings and drawings sold in 1762 still "
                    "form one of the chief glories of the Royal Collection."
                ),
                "speaker": "Haskell",
                "text_layer": "authorial report",
                "qualification": (
                    "The source describes an aggregate of works without an exact "
                    "count or identified individual items. The work-group candidate "
                    "and Royal Collection type remain unresolved; this is not a "
                    "location relation from the sale event."
                ),
                "mentioned_candidate_ids": ["cand-10807", "cand-2292", "cand-2471"],
                "relation_candidate": True,
                "date": "1762",
            },
            "original_quote": p391_line[
                p391_line.index("paintings and drawings"):
                p391_line.index(" which still form") + len(
                    " which still form one of the chief glories of the Royal Collection."
                )
            ],
        },
        {
            **sale_19,
            "statement_id": "st-chp19-p391-smith-catalogued-sold-works",
            "subject_candidate_id": "cand-10807",
            "object_candidate_id": "cand-2447",
            "predicate": "smith_catalogued_the_sold_paintings_and_drawings",
            "qualifiers": {
                "source_line_start": 117,
                "source_line_end": 118,
                "printed_page": 391,
                "pdf_physical_page": 6,
                "claim": "Haskell says Joseph Smith catalogued the paintings and drawings sold to George III.",
                "speaker": "Haskell",
                "text_layer": "authorial report",
                "qualification": (
                    "The catalogue object or version is not identified in this passage. "
                    "The source states cataloguing, not artistic authorship."
                ),
                "mentioned_candidate_ids": ["cand-10807", "cand-2447"],
                "relation_candidate": True,
                "date": "1762",
            },
            "original_quote": "These were cata\u00ad\n. logued by him;",
        },
        {
            **sale_19,
            "statement_id": "st-chp19-p391-sold-works-most-recognisable-or-traceable",
            "subject_candidate_id": "cand-10807",
            "object_candidate_id": None,
            "predicate": "most_sold_works_recognisable_or_traceable",
            "qualifiers": {
                "source_line_start": 118,
                "source_line_end": 118,
                "printed_page": 391,
                "pdf_physical_page": 6,
                "claim": (
                    "Haskell says most of the sold paintings and drawings are "
                    "recognisable or traceable and bases his estimate of Smith as a "
                    "collector on them."
                ),
                "speaker": "Haskell",
                "text_layer": "authorial evaluation",
                "qualification": (
                    "This is Haskell's assessment of the aggregate works, not an "
                    "identification of each work."
                ),
                "mentioned_candidate_ids": ["cand-10807"],
                "relation_candidate": False,
                "date": "1762",
            },
            "original_quote": (
                "most of them are recognisable or traceable, and on them is "
                "necessarily based our main estimate of Smith as a collector."
            ),
        },
    ]

    updated_mentions = []
    for row in mentions:
        if row["mention_id"] == "m-chp19-p391-014":
            row = dict(row)
            row.update(
                candidate_id="cand-10807",
                surface_form="These",
                start_char=str(these_start),
                end_char=str(these_start + len("These")),
                note="Anaphoric subject of the catalogue and traceability sentences; refers to the sold paintings and drawings.",
            )
        updated_mentions.append(row)
    updated_mentions.append({
        "mention_id": new_mention_id,
        "segment_id": SEGMENT_19,
        "candidate_id": "cand-2447",
        "surface_form": "him",
        "start_char": str(him_start),
        "end_char": str(him_start + len("him")),
        "note": "Haskell's pronoun in the catalogue sentence refers to Joseph Smith.",
    })

    updated_alignment = []
    for row in alignment:
        if row is c2471:
            row = dict(row)
            row["ku_id"] = KU_ID
            row["process_ref"] = PROCESS_REF
            row["resolution_note"] = (
                "group=sg3-event-cand-9278; source_ref=entity-candidates.csv#cand-2471;"
                "index_entry=S.csv#160;sub_entry=sale of library and pictures to George III;"
                "mention=m-chp19-p391-010; paired_identity=cand-9278;"
                "Appendix 5 p.391 L117-118 and L123-124 explicitly describe the same 1762 sale "
                "as Chapter 10 p.310 L488; Chapter 10 note 6 points to Appendix 5. "
                "This is one sale event, while the aggregate sold works and the Royal Collection "
                "remain separate unresolved candidates. Both candidates retain decision=new and "
                "map to one event KU."
            )
        elif row is c9278:
            row = dict(row)
            row["ku_id"] = KU_ID
            row["process_ref"] = PROCESS_REF
            row["resolution_note"] = (
                "group=sg3-event-cand-9278; source_ref=chp-10:10_CHP-10_intro:l481-489#L488;"
                "cross_reference=st-chp10-p310-note6-appendix-reference;"
                "paired_identity=cand-2471; Appendix 5 p.391 L117-118 and L123-124 explicitly "
                "describe the same 1762 sale. Haskell reports most of Smith's best pictures, books, "
                "drawings and gems, and elsewhere a very large number of paintings and drawings; "
                "do not infer a sale of the entire collection. The aggregate works group, collection "
                "type, and 1761 will remain separate candidates."
            )
        updated_alignment.append(row)

    manifest_row = {
        "ku_id": KU_ID,
        "type": "event",
        "canonical_name": "约瑟夫·史密斯向乔治三世出售藏品（1762）",
        "name_en": "Joseph Smith's 1762 Sale of Collections to George III",
        "source_task": "patrons-and-painters-full-book-s2",
        "card_path": CARD_REL.as_posix(),
    }
    updated_manifest = manifest + [manifest_row]

    relation_rows = [
        {
            "relation_id": "rel-1841",
            "subject_ku_id": KU_ID,
            "object_ku_id": "units/persons/joseph-smith-venice",
            "predicate": "has_participant",
            "time": "1762",
            "role": "卖方",
            "scope": (
                "Haskell称Smith售出其最佳藏品中的大部分绘画、书籍、素描和宝石；"
                "不据此认定全部收藏均已出售。"
            ),
            "origin": "book",
            "status": "formal",
            "source_id": "haskell-1980-rev-ed",
            "source_span": (
                "Chapter 10, printed p.310 L488; "
                f"statement={sale_10_id}"
            ),
            "source_file": SOURCE_10,
            "note": (
                "方向归一为事件→参与者；只记录Smith作为卖方参与1762年交易，"
                "保留来源对售出范围的限定。"
            ),
        },
        {
            "relation_id": "rel-1842",
            "subject_ku_id": KU_ID,
            "object_ku_id": "units/persons/george-iii",
            "predicate": "has_participant",
            "time": "1762",
            "role": "买方",
            "scope": (
                "Haskell称该笔交易向George III出售大量绘画和素描；"
                "没有给出精确件数或逐件清单。"
            ),
            "origin": "book",
            "status": "formal",
            "source_id": "haskell-1980-rev-ed",
            "source_span": (
                "Appendix 5, printed p.391 L117; "
                f"statement={sale_19_id}"
            ),
            "source_file": SOURCE_19,
            "note": (
                "方向为事件→参与者；只记录George III作为买方，不表示Royal Collection"
                "在交易时已是该事件的地点或参与者。"
            ),
        },
    ]
    updated_relations = relations + relation_rows

    sale_10 = by_statement[sale_10_id]
    require(sale_10.get("subject_candidate_id") == "cand-2440"
            and sale_10.get("object_candidate_id") == "cand-9278",
            "p.310 seller/event endpoints changed")
    will_sale = by_statement[will_sale_id]
    require(will_sale.get("qualifiers", {}).get("relation_candidate") is True,
            "p.391 will/sale candidate changed")
    selection = by_statement[selection_id]
    require(selection.get("subject_candidate_id") == "cand-2471"
            and selection.get("object_candidate_id") == "cand-9278",
            "p.392 selection candidate endpoints changed")
    require("cand-2471" in sale_19["qualifiers"]["mentioned_candidate_ids"],
            "p.391 sale mention not linked")

    statement_lines = []
    additions_by_id = {row["statement_id"]: row for row in new_statements}
    for line in statement_raw:
        row = json.loads(line)
        sid = row["statement_id"]
        if sid == sale_19_id:
            statement_lines.append(json.dumps(sale_19, ensure_ascii=False) + "\n")
        elif sid in additions_by_id:
            raise ValueError(f"Unexpected statement ID collision: {sid}")
        else:
            statement_lines.append(line)
    statement_lines.extend(json.dumps(row, ensure_ascii=False) + "\n" for row in new_statements)
    updated_statements_bytes = "".join(statement_lines).encode("utf-8")

    updated_alignment_bytes = serialize_csv(
        alignment_cols, updated_alignment, alignment_bom, alignment_eol
    )
    updated_mentions_bytes = serialize_csv(
        mention_cols, updated_mentions, mention_bom, mention_eol
    )
    updated_manifest_bytes = serialize_csv(
        manifest_cols, updated_manifest, manifest_bom, manifest_eol
    )
    updated_relations_bytes = serialize_csv(
        relation_cols, updated_relations, relation_bom, relation_eol
    )

    accepted_path = BASE / "04-knowledge" / "accepted.yml"
    accepted_before = accepted_path.read_bytes()
    accepted_text = accepted_before.decode("utf-8")
    require(CARD_REL.as_posix() not in accepted_text, "event card already appears in accepted.yml")
    require("\nclaims:\n" in accepted_text, "accepted.yml units/claims separator changed")
    accepted_after = accepted_text.replace(
        "\nclaims:\n",
        f"\n- {CARD_REL.as_posix()}\n\nclaims:\n",
        1,
    ).encode("utf-8")

    outputs = {
        paths["alignment.csv"]: updated_alignment_bytes,
        paths["book-statements.jsonl"]: updated_statements_bytes,
        paths["mentions.csv"]: updated_mentions_bytes,
        paths["ku-manifest.csv"]: updated_manifest_bytes,
        paths["relations.csv"]: updated_relations_bytes,
        accepted_path: accepted_after,
    }
    old_bytes = {
        paths["alignment.csv"]: paths["alignment.csv"].read_bytes(),
        paths["book-statements.jsonl"]: paths["book-statements.jsonl"].read_bytes(),
        paths["mentions.csv"]: paths["mentions.csv"].read_bytes(),
        paths["ku-manifest.csv"]: paths["ku-manifest.csv"].read_bytes(),
        paths["relations.csv"]: paths["relations.csv"].read_bytes(),
        accepted_path: accepted_before,
    }

    print("DRY-RUN EVENT REGISTRATION")
    print("S3: cand-2471 and cand-9278 remain new and share one event identity group.")
    print(f"S4: two candidate mappings -> {KU_ID}; one event KU.")
    print("S2: revise one compound Appendix 5 statement into event/buyer endpoints; add three atomic statements.")
    print("S2 mentions: repair the anaphoric works mention and add the Smith cataloguer pronoun.")
    print("S6 expected: 2 formal has_participant edges; 2 pending; 2 rejected; no endpoint inferred for Royal Collection.")
    print("S5: four source-backed event fields will be extracted from the card after this apply.")
    for path in outputs:
        print(f"  {path.relative_to(BASE).as_posix()}: {len(old_bytes[path])} -> {len(outputs[path])} bytes")
    for row in new_statements:
        print("  ADD S2", row["statement_id"], row["subject_candidate_id"], row["predicate"], row["object_candidate_id"])
    for row in relation_rows:
        print("  ADD REL", row["relation_id"], row["subject_ku_id"], row["predicate"], row["object_ku_id"], row["role"])
    print("  S3 group", c2471["decision"], "cand-2471 + cand-9278 ->", GROUP_ID)
    print("  Event card", CARD_REL.as_posix())

    print("\nPROPOSED TEXT DIFFS")
    for path, data in outputs.items():
        before = old_bytes[path].decode("utf-8-sig")
        after = data.decode("utf-8-sig")
        diff = difflib.unified_diff(
            before.splitlines(),
            after.splitlines(),
            fromfile=f"before/{path.relative_to(BASE).as_posix()}",
            tofile=f"after/{path.relative_to(BASE).as_posix()}",
            lineterm="",
        )
        lines = list(diff)
        if lines:
            print("\n".join(lines))
        else:
            print(f"  NO CHANGE {path.relative_to(BASE).as_posix()}")

    if not args.apply:
        print("No files written. Re-run with --apply to apply this reviewed plan.")
        return 0

    card_path = BASE / CARD_REL
    require(card_path.is_file(), "event card must exist before table registration")
    for path, data in outputs.items():
        atomic_write(path, data)
    print("Applied structured S2/S3/S4/S6 changes.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
