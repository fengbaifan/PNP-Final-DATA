#!/usr/bin/env python3
"""Preview/apply the p.224 fresco identity, endpoint, and S6 batch."""
from __future__ import annotations

import argparse
import csv
import difflib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_REF = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp8-p224-apotheosis-gallery"
TASK = "patrons-and-painters-full-book-s2"
SOURCE_ID = "haskell-1980-rev-ed"
SOURCE_FILE = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
GALLERY = "units/places/gallery-palazzo-buonaccorsi"
FRESCO = "units/works/apotheosis-of-aeneas-buonaccorsi-vault"
RAMBALDI = "units/persons/carlo-antonio-rambaldi"
DARDANI = "units/persons/antonio-dardani"

NEW_KUS = {
    "cand-7750": (FRESCO, "work", "埃涅阿斯神化拱顶壁画", "Apotheosis of Aeneas Vault Fresco", "04-knowledge/units/works/apotheosis-of-aeneas-buonaccorsi-vault.md"),
    "cand-2094": (RAMBALDI, "person", "卡洛·安东尼奥·兰巴尔迪", "Carlo Antonio Rambaldi", "04-knowledge/units/persons/carlo-antonio-rambaldi.md"),
    "cand-0902": (DARDANI, "person", "安东尼奥·达尔达尼", "Antonio Dardani", "04-knowledge/units/persons/antonio-dardani.md"),
}
SAME_MAPPINGS = {
    "cand-7749": GALLERY,
    "cand-0903": FRESCO,
    "cand-2095": FRESCO,
}
FORMAL_SPECS = [
    ("st-chp8-p224-apotheosis-fresco-located-at-gallery", FRESCO, "located_at", GALLERY,
     "", "长廊低桶形拱顶壁画所在空间", "仅记录Haskell将该作品称为《埃涅阿斯神化》壁画并置于雷蒙多画廊的拱顶；不表示当前存续状况或独立核验完成情况。",
     "第8章 p.224 L156–157称《埃涅阿斯神化》壁画位于Raimondo画廊的拱顶。"),
    ("st-chp8-p224-rambaldi-dardani-apotheosis", FRESCO, "commissioned_by", "units/persons/raimondo-buonaccorsi",
     "1707", "召集画家绘制该壁画的委托者", "只记录Haskell所述Raimondo于1707年召两位画家绘制指定壁画；不推断合同条款或作品由谁实际完成。",
     "第8章 p.224 L156–157称Raimondo召Carlo Antonio Rambaldi与Antonio Dardani绘制该壁画。"),
]
NEW_STATEMENTS = [
    {
        "statement_id": "st-chp8-p224-apotheosis-fresco-located-at-gallery",
        "segment_id": "chp-8:08_CHP-8_sec_ii:l152-161",
        "subject_candidate_id": "cand-7750", "object_candidate_id": "cand-7749", "predicate": "located_at",
        "qualifiers": {
            "source_line_start": 156, "source_line_end": 157, "printed_page": 224, "pdf_physical_page": 26,
            "claim": "Haskell identifies the work as the Apotheosis of Aeneas fresco and places it on the vault of Raimondo's gallery.",
            "speaker": "Haskell", "text_layer": "body",
            "qualification": "This records Haskell's narrative identification and location; it is not an independent condition or completion check.",
            "mentioned_candidate_ids": ["cand-7750", "cand-7749"], "relation_candidate": True,
            "relation_candidate_note": "Directly locates the named fresco at the gallery vault; encode work → physical place with located_at. Do not infer present survival or a completion date.",
        },
        "original_quote": "In 1707 Raimondo Buonaccorsi summoned two Bolognese artists. Carlo Antonio\nRambaldi and Antonio Dardani, to paint the fresco of the Apotheosis of Aeneas on the vault\nof his gallery,2",
        "origin": "book", "source_file": SOURCE_FILE,
    },
    {
        "statement_id": "st-chp8-p224-rambaldi-summoned-to-paint-apotheosis",
        "segment_id": "chp-8:08_CHP-8_sec_ii:l152-161",
        "subject_candidate_id": "cand-2094", "object_candidate_id": "cand-7750", "predicate": "summoned_to_paint",
        "qualifiers": {
            "source_line_start": 156, "source_line_end": 157, "printed_page": 224, "pdf_physical_page": 26,
            "claim": "Haskell says Carlo Antonio Rambaldi was one of two Bolognese artists whom Raimondo summoned in 1707 to paint the Apotheosis of Aeneas fresco.",
            "speaker": "Haskell", "text_layer": "body",
            "qualification": "This records the painter's assigned task; it does not state that Rambaldi completed the fresco.",
            "mentioned_candidate_ids": ["cand-2094", "cand-0902", "cand-0467", "cand-7750"],
            "relation_candidate": True,
            "relation_candidate_note": "Named artist and work are direct endpoints of the reported assignment. The controlled vocabulary has no exact relation for an artist summoned to paint without asserting completed authorship; retain as process-only pending.",
        },
        "original_quote": "In 1707 Raimondo Buonaccorsi summoned two Bolognese artists. Carlo Antonio\nRambaldi and Antonio Dardani, to paint the fresco of the Apotheosis of Aeneas on the vault\nof his gallery,2",
        "origin": "book", "source_file": SOURCE_FILE,
    },
    {
        "statement_id": "st-chp8-p224-dardani-summoned-to-paint-apotheosis",
        "segment_id": "chp-8:08_CHP-8_sec_ii:l152-161",
        "subject_candidate_id": "cand-0902", "object_candidate_id": "cand-7750", "predicate": "summoned_to_paint",
        "qualifiers": {
            "source_line_start": 156, "source_line_end": 157, "printed_page": 224, "pdf_physical_page": 26,
            "claim": "Haskell says Antonio Dardani was one of two Bolognese artists whom Raimondo summoned in 1707 to paint the Apotheosis of Aeneas fresco.",
            "speaker": "Haskell", "text_layer": "body",
            "qualification": "This records the painter's assigned task; it does not state that Dardani completed the fresco.",
            "mentioned_candidate_ids": ["cand-0902", "cand-2094", "cand-0467", "cand-7750"],
            "relation_candidate": True,
            "relation_candidate_note": "Named artist and work are direct endpoints of the reported assignment. The controlled vocabulary has no exact relation for an artist summoned to paint without asserting completed authorship; retain as process-only pending.",
        },
        "original_quote": "In 1707 Raimondo Buonaccorsi summoned two Bolognese artists. Carlo Antonio\nRambaldi and Antonio Dardani, to paint the fresco of the Apotheosis of Aeneas on the vault\nof his gallery,2",
        "origin": "book", "source_file": SOURCE_FILE,
    },
]


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def csv_bytes(path: Path, fields, rows) -> bytes:
    buffer = io.StringIO(newline="")
    line_ending = "\r\n" if b"\r\n" in path.read_bytes() else "\n"
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator=line_ending)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def repair_existing_location_evidence(paths: dict[str, Path], apply: bool) -> None:
    statement_path = paths["statements"]
    raw_lines = [line for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    rows = [json.loads(line) for line in raw_lines]
    raw_by_id = {json.loads(line)["statement_id"]: line for line in raw_lines}
    original_by_id = {row["statement_id"]: json.loads(json.dumps(row, ensure_ascii=False)) for row in rows}
    expected = NEW_STATEMENTS[0]
    target = next((row for row in rows if row["statement_id"] == expected["statement_id"]), None)
    if target is None:
        raise ValueError("location statement has not yet been registered")
    if (target.get("subject_candidate_id"), target.get("object_candidate_id")) != (expected["subject_candidate_id"], expected["object_candidate_id"]):
        raise ValueError("unexpected location statement endpoints")
    for key in ("predicate", "qualifiers", "original_quote"):
        target[key] = expected[key]
    artist_statement = next((row for row in rows if row["statement_id"] == "st-chp8-p224-rambaldi-dardani-apotheosis"), None)
    if artist_statement is None:
        raise ValueError("artist/commission statement is missing")
    artist_statement["qualifiers"]["ocr_corrections"] = [{
        "source_file": SOURCE_FILE,
        "source_line": 156,
        "ocr": "artists.",
        "print": "artists,",
        "basis": "CHP-8.pdf physical page 26.",
    }]
    statement_output = ("\n".join(
        raw_by_id[row["statement_id"]]
        if row["statement_id"] in raw_by_id and row == original_by_id[row["statement_id"]]
        else json.dumps(row, ensure_ascii=False)
        for row in rows
    ) + "\n").encode("utf-8")
    relation_fields, relation_rows = read_csv(paths["relations"])
    linked = [row for row in relation_rows if f"statement={expected['statement_id']}" in row["source_span"]]
    if len(linked) != 1:
        raise ValueError(f"expected one formal relation for the location statement, found {len(linked)}")
    _statement_id, _subject, _predicate, _object, _time, role, scope, note = FORMAL_SPECS[0]
    linked[0]["role"] = role
    linked[0]["scope"] = scope
    linked[0]["source_span"] = "Chapter 8, printed p. 224, lines 156–157; statement=st-chp8-p224-apotheosis-fresco-located-at-gallery"
    linked[0]["note"] = note
    alignment_fields, alignment_rows = read_csv(paths["alignment"])
    gallery_alignment = [row for row in alignment_rows if row["candidate_id"] == "cand-7749" and not row["external_source"]]
    if len(gallery_alignment) != 1:
        raise ValueError(f"expected one main alignment for cand-7749, found {len(gallery_alignment)}")
    gallery_alignment[0]["resolution_note"] = gallery_alignment[0]["resolution_note"].replace(
        "prior_decision=new; prior_group=sg3-place-cand-7749; ",
        "group=sg3-place-cand-7749; prior_decision=new; ",
    )
    outputs = {
        statement_path: statement_output,
        paths["relations"]: csv_bytes(paths["relations"], relation_fields, relation_rows),
        paths["alignment"]: csv_bytes(paths["alignment"], alignment_fields, alignment_rows),
    }
    changed = {}
    for path, data in outputs.items():
        before = path.read_bytes()
        if before == data:
            continue
        changed[path] = (before, data)
        diff = difflib.unified_diff(before.decode("utf-8-sig").splitlines(keepends=True), data.decode("utf-8-sig").splitlines(keepends=True), fromfile=f"{path.relative_to(ROOT)} (before)", tofile=f"{path.relative_to(ROOT)} (after)")
        print("".join(diff), end="")
    if not apply:
        print(f"PREVIEW evidence repair: {len(changed)} files")
        return
    originals = {path: before for path, (before, _data) in changed.items()}
    try:
        for path, (_before, data) in changed.items():
            path.write_bytes(data)
    except Exception:
        for path, before in originals.items():
            path.write_bytes(before)
        raise
    print(f"Applied evidence repair to {len(changed)} files transactionally.")


def insert_sorted_unit_paths(accepted: str, card_paths: list[str]) -> str:
    marker = "claims:\n"
    if marker not in accepted:
        raise ValueError("accepted.yml claims section not found")
    units_text, rest = accepted.split(marker, 1)
    lines = units_text.splitlines(keepends=True)
    for card_path in card_paths:
        if any(line.rstrip("\r\n") == f"- {card_path}" for line in lines):
            continue
        insert_at = next((i for i, line in enumerate(lines)
                          if line.startswith("- 04-knowledge/units/") and line[2:].strip() > card_path), len(lines))
        lines.insert(insert_at, f"- {card_path}\n")
    return "".join(lines) + marker + rest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed p.224 batch")
    parser.add_argument("--repair-existing-evidence", action="store_true", help="repair the registered p.224 location quote after registration")
    args = parser.parse_args()
    paths = {
        "alignment": TABLES / "alignment.csv",
        "manifest": TABLES / "ku-manifest.csv",
        "relations": TABLES / "relations.csv",
        "mentions": TABLES / "mentions.csv",
        "statements": TABLES / "book-statements.jsonl",
        "accepted": ROOT / "04-knowledge" / "accepted.yml",
    }
    if args.repair_existing_evidence:
        repair_existing_location_evidence(paths, args.apply)
        return
    align_fields, alignments = read_csv(paths["alignment"])
    manifest_fields, manifest = read_csv(paths["manifest"])
    relation_fields, relations = read_csv(paths["relations"])
    mention_fields, mentions = read_csv(paths["mentions"])
    raw_statement_lines = [line for line in paths["statements"].read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statements = [json.loads(line) for line in raw_statement_lines]
    raw_statement_by_id = {json.loads(line)["statement_id"]: line for line in raw_statement_lines}
    original_statement_by_id = {row["statement_id"]: json.loads(json.dumps(row, ensure_ascii=False)) for row in statements}
    accepted = paths["accepted"].read_text(encoding="utf-8-sig")

    by_candidate = {}
    for row in alignments:
        by_candidate.setdefault(row["candidate_id"], []).append(row)
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    card_paths = [spec[4] for spec in NEW_KUS.values()]
    for card_path in card_paths:
        if not (ROOT / card_path).is_file():
            raise ValueError(f"create and inspect target card before applying: {card_path}")
    for candidate, (ku_id, kind, zh, en, card_path) in NEW_KUS.items():
        rows = [row for row in by_candidate.get(candidate, []) if not row["external_source"]]
        if len(rows) != 1 or rows[0]["decision"] not in {"new", "undecided"} or rows[0]["ku_id"]:
            raise ValueError(f"new-KU S3 precondition failed for {candidate}: {rows}")
        if ku_id in manifest_by_ku:
            raise ValueError(f"new KU is already in manifest: {ku_id}")
    for candidate, ku_id in SAME_MAPPINGS.items():
        rows = [row for row in by_candidate.get(candidate, []) if not row["external_source"]]
        if len(rows) != 1 or rows[0]["decision"] not in {"new", "undecided"} or rows[0]["ku_id"]:
            raise ValueError(f"same-mapping S3 precondition failed for {candidate}: {rows}")
        if candidate == "cand-7749" and ku_id not in manifest_by_ku:
            raise ValueError(f"reused gallery KU missing from manifest: {ku_id}")

    statement_by_id = {row["statement_id"]: row for row in statements}
    required_old = {
        "st-chp8-p224-gallery-survival-and-vault-fresco",
        "st-chp8-p224-rambaldi-dardani-apotheosis",
        "st-chp8-p224-gallery-decoration-start",
    }
    if not required_old.issubset(statement_by_id):
        raise ValueError(f"missing expected p.224 statements: {required_old - statement_by_id.keys()}")
    if any(row["statement_id"] in statement_by_id for row in NEW_STATEMENTS):
        raise ValueError("a new S2 statement ID already exists")
    if statement_by_id["st-chp8-p224-gallery-survival-and-vault-fresco"]["object_candidate_id"] != "cand-7750":
        raise ValueError("unexpected existing gallery/fresco endpoint mapping")
    existing_artist_statement = statement_by_id["st-chp8-p224-rambaldi-dardani-apotheosis"]
    if (existing_artist_statement.get("subject_candidate_id"), existing_artist_statement.get("object_candidate_id")) != ("cand-0467", "cand-7750"):
        raise ValueError("unexpected existing Rambaldi/Dardani statement endpoints")
    expected_m = {
        "m-chp8-p224-rambaldi-first": ("cand-2095", "cand-2094"),
        "m-chp8-p224-rambaldi": ("cand-2095", "cand-2094"),
        "m-chp8-p224-dardani": ("cand-0903", "cand-0902"),
    }
    mention_by_id = {row["mention_id"]: row for row in mentions}
    for mention_id, (old_candidate, _new_candidate) in expected_m.items():
        if mention_id not in mention_by_id or mention_by_id[mention_id]["candidate_id"] != old_candidate:
            raise ValueError(f"unexpected current mention mapping: {mention_id}")

    for row in alignments:
        if row["external_source"]:
            continue
        cid = row["candidate_id"]
        if cid == "cand-7749":
            row.update({"ku_id": GALLERY, "decision": "same", "process_ref": PROCESS_REF,
                        "resolution_note": "group=sg3-place-cand-7749; prior_decision=new; S3复核（2026-10-28）：第8章p.224 L154–157所述含低桶形拱顶与《埃涅阿斯纪》装饰的长廊，对应已有图版33b空间KU“Gallery of Palazzo Buonaccorsi”，其已有原语别名为Galleria dell’Eneide；复用既有place KU，避免重复建卡。身份范围仍限本书长廊，不补边界或当前保存状态。"})
        elif cid == "cand-7750":
            row.update({"ku_id": FRESCO, "process_ref": PROCESS_REF,
                        "resolution_note": row["resolution_note"].rstrip() + " S4登记（2026-10-28）：沿用workgrp-55ac0401a0d98e，登记来源限定的拱顶壁画KU；名称为描述性暂题，保留Raimondo于1707年召画家绘制与实际完成情况未载的区别。"})
        elif cid == "cand-0902":
            row.update({"ku_id": DARDANI, "decision": "new", "process_ref": PROCESS_REF,
                        "resolution_note": "prior_decision=undecided; prior_reason=无可核S2人物提及；该段姓名曾误挂作品索引子项。S2更正后mention=m-chp8-p224-dardani（Antonio Dardani），来源为第8章p.224 L156–157；candidate D.csv#4同名人物项。未发现同名既有person KU。group=sg3-person-cand-0902; 仅建立书内人物身份，不推定生卒或外部身份。S4登记至units/persons/antonio-dardani。"})
        elif cid == "cand-2094":
            row.update({"ku_id": RAMBALDI, "decision": "new", "process_ref": PROCESS_REF,
                        "resolution_note": "prior_decision=undecided; prior_reason=无可核S2人物提及；该段姓名曾误挂作品索引子项。S2更正后mentions=m-chp8-p224-rambaldi-first,m-chp8-p224-rambaldi，合读为Carlo Antonio Rambaldi，来源为第8章p.224 L156–157；candidate Q-R.csv#21同名人物项。未发现同名既有person KU。group=sg3-person-cand-2094; 仅建立书内人物身份，不推定生卒或外部身份。S4登记至units/persons/carlo-antonio-rambaldi。"})
        elif cid == "cand-0903":
            row.update({"ku_id": FRESCO, "decision": "same", "process_ref": PROCESS_REF,
                        "resolution_note": "prior_decision=undecided; prior_reason=该索引work子项没有可核S2锚点，曾误连至人物提及。S2校正后，D.csv#5子项“Apotheosis of Aeneas (with Rambaldi)”与Q-R.csv#22及正文唯一一幅“the fresco of the Apotheosis of Aeneas”均指向同一壁画。same→units/works/apotheosis-of-aeneas-buonaccorsi-vault；不表示Dardani身份或完成归属已外部核验。group=workgrp-55ac0401a0d98e。"})
        elif cid == "cand-2095":
            row.update({"ku_id": FRESCO, "decision": "same", "process_ref": PROCESS_REF,
                        "resolution_note": "prior_decision=undecided; prior_reason=该索引work子项没有可核S2锚点，曾误连至人物提及。S2校正后，Q-R.csv#22子项“Apotheosis of Aeneas (with Dardani)”与D.csv#5及正文唯一一幅“the fresco of the Apotheosis of Aeneas”均指向同一壁画。same→units/works/apotheosis-of-aeneas-buonaccorsi-vault；不表示Rambaldi身份或完成归属已外部核验。group=workgrp-55ac0401a0d98e。"})
    manifest.extend(
        {"ku_id": ku_id, "type": kind, "canonical_name": zh, "name_en": en,
         "source_task": TASK, "card_path": card_path}
        for ku_id, kind, zh, en, card_path in NEW_KUS.values()
    )

    mention_updates = {
        "m-chp8-p224-rambaldi-first": ("cand-2094", "Given-name segment of Carlo Antonio Rambaldi; surname continues in m-chp8-p224-rambaldi."),
        "m-chp8-p224-rambaldi": ("cand-2094", "Surname continuation of Carlo Antonio Rambaldi across the print line break."),
        "m-chp8-p224-dardani": ("cand-0902", "Named Bolognese artist Antonio Dardani; do not map to the index work subentry."),
    }
    for row in mentions:
        if row["mention_id"] in mention_updates:
            row["candidate_id"], row["note"] = mention_updates[row["mention_id"]]

    old_survival = statement_by_id["st-chp8-p224-gallery-survival-and-vault-fresco"]
    old_survival["subject_candidate_id"] = "cand-7749"
    old_survival["object_candidate_id"] = None
    old_survival["predicate"] = "survives_intact_at_haskell_writing"
    old_survival["qualifiers"].update({
        "source_line_start": 154, "source_line_end": 154,
        "claim": "Haskell says the long gallery survived intact at the time he wrote.",
        "qualification": "‘Today’ is relative to Haskell's publication; this is not a current-condition check.",
        "mentioned_candidate_ids": ["cand-7749"], "relation_candidate": False,
        "temporal_reference": "at time of Haskell's writing",
    })
    old_survival["qualifiers"].pop("relation_candidate_note", None)
    old_survival["original_quote"] = "This survives intact today (Plate 33b)."

    existing_artist_statement["subject_candidate_id"] = "cand-7750"
    existing_artist_statement["object_candidate_id"] = "cand-0467"
    existing_artist_statement["predicate"] = "commissioned_by"
    existing_artist_statement["qualifiers"].update({
        "claim": "Haskell reports that Raimondo summoned Carlo Antonio Rambaldi and Antonio Dardani in 1707 to paint the Apotheosis of Aeneas fresco on the gallery vault.",
        "qualification": "The source records the reported assignment/commission; it does not independently verify either painter's completed contribution.",
        "mentioned_candidate_ids": ["cand-0467", "cand-2094", "cand-0902", "cand-7750"],
        "artist_candidate_ids": ["cand-2094", "cand-0902"],
        "ocr_corrections": [{
            "source_file": SOURCE_FILE, "source_line": 156,
            "ocr": "artists.", "print": "artists,",
            "basis": "CHP-8.pdf physical page 26.",
        }],
    })
    existing_artist_statement["original_quote"] = "In 1707 Raimondo Buonaccorsi summoned two Bolognese artists. Carlo Antonio\nRambaldi and Antonio Dardani, to paint the fresco of the Apotheosis of Aeneas on the vault\nof his gallery,2"
    existing_artist_statement["qualifiers"]["artist_candidate_ids"] = ["cand-2094", "cand-0902"]

    location_row = NEW_STATEMENTS[0]
    if location_row["statement_id"] not in statement_by_id:
        # Place the location edge beside the source statement it atomizes.
        insert_after = "st-chp8-p224-gallery-survival-and-vault-fresco"
    updated_statements = []
    for row in statements:
        updated_statements.append(row)
        if row["statement_id"] == insert_after:
            updated_statements.append(location_row)
        if row["statement_id"] == "st-chp8-p224-rambaldi-dardani-apotheosis":
            updated_statements.extend(NEW_STATEMENTS[1:])

    next_relation = max(int(row["relation_id"].split("-")[1]) for row in relations) + 1
    for spec in FORMAL_SPECS:
        statement_id, subject, predicate, object_, time, role, scope, note = spec
        evidence = [row for row in relations if f"statement={statement_id}" in row["source_span"]]
        if evidence:
            raise ValueError(f"S6 evidence already has a relation row: {statement_id}")
        if any((row["subject_ku_id"], row["predicate"], row["object_ku_id"], row["time"], row["role"], row["scope"]) ==
               (subject, predicate, object_, time, role, scope) for row in relations):
            raise ValueError(f"duplicate S6 natural key for {statement_id}")
        relations.append({
            "relation_id": f"rel-{next_relation:04d}", "subject_ku_id": subject, "object_ku_id": object_,
            "predicate": predicate, "time": time, "role": role, "scope": scope, "origin": "book", "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": f"Chapter 8, printed p. 224, lines 156–157; statement={statement_id}",
            "source_file": SOURCE_FILE, "note": note,
        })
        next_relation += 1

    accepted_paths = [spec[4] for spec in NEW_KUS.values()]
    accepted = insert_sorted_unit_paths(accepted, accepted_paths)
    outputs = {
        paths["alignment"]: csv_bytes(paths["alignment"], align_fields, alignments),
        paths["manifest"]: csv_bytes(paths["manifest"], manifest_fields, manifest),
        paths["relations"]: csv_bytes(paths["relations"], relation_fields, relations),
        paths["mentions"]: csv_bytes(paths["mentions"], mention_fields, mentions),
        paths["statements"]: ("\n".join(
            raw_statement_by_id[row["statement_id"]]
            if row["statement_id"] in raw_statement_by_id and row == original_statement_by_id[row["statement_id"]]
            else json.dumps(row, ensure_ascii=False)
            for row in updated_statements
        ) + "\n").encode("utf-8"),
        paths["accepted"]: accepted.encode("utf-8"),
    }
    print("APPLY" if args.apply else "PREVIEW")
    print("S3/S4: reuse the existing gallery KU; map two work index subentries to one fresco; register one work and two named person KUs.")
    print("S2: correct three artist mention mappings; separate gallery survival from the fresco-location statement; add two source-bounded artist-task statements.")
    print("S6: add two formal rows; record the gallery-decoration and two summoned-artist relation candidates as process-only pending in knowledge.md.")
    changed = {}
    for path, data in outputs.items():
        before = path.read_bytes()
        if before == data:
            continue
        changed[path] = (before, data)
        diff = difflib.unified_diff(before.decode("utf-8-sig").splitlines(keepends=True), data.decode("utf-8-sig").splitlines(keepends=True), fromfile=f"{path.relative_to(ROOT)} (before)", tofile=f"{path.relative_to(ROOT)} (after)")
        print("".join(diff), end="")
    if not args.apply:
        return
    originals = {path: before for path, (before, _data) in changed.items()}
    try:
        for path, (_before, data) in changed.items():
            path.write_bytes(data)
    except Exception:
        for path, before in originals.items():
            path.write_bytes(before)
        raise
    print(f"Applied {len(changed)} files transactionally.")


if __name__ == "__main__":
    main()
