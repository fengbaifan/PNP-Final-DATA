#!/usr/bin/env python3
"""Resolve the scoped S3/S4/S6 batch for Haskell, chapter 8, p. 231."""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
from pathlib import Path


BASE = Path(__file__).resolve().parents[3]
TABLES = BASE / "04-knowledge" / "tables"
PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md"
    "#s3-s4-s5-s6-chp8-p231-la-burla-20261023"
)
WORK = "units/works/baldassare-franceschini-la-burla-del-piovano-arlotto"
FERDINAND = "units/persons/ferdinand-grand-prince-tuscany"
FRANCESCHINI = "units/persons/baldassare-franceschini"
ARLOTTO = "units/persons/arlotto-mainardi"
HASKELL = "units/archives/patrons-and-painters"
PITTI = "units/places/palazzo-pitti"
GIGLIOLI = "units/archives/giglioli-volterrano-uffizi-1908"
STEINBART = "units/archives/steinbart-gemalten-schwaenke-arlotto-1936"
TUSCAN = "units/terms/tuscan-narrative-tradition-fifteenth-century-haskell-p231"
SOURCE_ID = "haskell-1980-rev-ed"
CH8 = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
PLATES = "02-sources/02-Markdown/00_05_List_of_Plates.md"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool, str]:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    rows = list(reader)
    return list(reader.fieldnames or []), rows, bom, newline


def render_csv(fields: list[str], rows: list[dict[str, str]], bom: bool, newline: str) -> bytes:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + handle.getvalue().encode("utf-8")


def read_jsonl(path: Path) -> tuple[list[str], list[dict]]:
    lines = path.read_bytes().splitlines(keepends=True)
    rows = []
    endings = []
    for line in lines:
        if not line.strip():
            continue
        rows.append(json.loads(line.decode("utf-8-sig")))
        endings.append(b"\r\n" if line.endswith(b"\r\n") else b"\n")
    return ["\r\n"] if endings and endings[0] == b"\r\n" else ["\n"], rows


def render_jsonl(path: Path, rows: list[dict]) -> bytes:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    body = b"".join(json.dumps(row, ensure_ascii=False).encode("utf-8") + newline for row in rows)
    return (b"\xef\xbb\xbf" if bom else b"") + body


def atomic_write(path: Path, payload: bytes) -> None:
    temp = path.with_name(path.name + ".tmp-p231")
    temp.write_bytes(payload)
    os.replace(temp, path)


def one(rows: list[dict], key: str, value: str) -> dict:
    matches = [row for row in rows if row.get(key) == value]
    if len(matches) != 1:
        raise ValueError(f"expected one {key}={value}, found {len(matches)}")
    return matches[0]


def set_cell(row: dict, key: str, value: str) -> None:
    if key not in row:
        raise ValueError(f"missing CSV field {key}")
    row[key] = value


def add_manifest_row(row: dict[str, str]) -> None:
    fields, rows, bom, newline = read_csv(TABLES / "ku-manifest.csv")
    if any(old["ku_id"] == row["ku_id"] for old in rows):
        raise ValueError(f"manifest already contains {row['ku_id']}")
    rows.append(row)
    plans["04-knowledge/tables/ku-manifest.csv"] = render_csv(fields, rows, bom, newline)


def accepted_with(paths: list[str]) -> bytes:
    path = BASE / "04-knowledge" / "accepted.yml"
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "units:":
        raise ValueError("accepted.yml does not have the expected units list")
    existing = {line.strip()[2:].strip() for line in lines if line.lstrip().startswith("-")}
    for new_path in sorted(set(paths) - existing):
        insertion = len(lines)
        for index, line in enumerate(lines):
            if line.lstrip().startswith("-"):
                current = line.strip()[2:].strip()
                if current > new_path:
                    insertion = index
                    break
        lines.insert(insertion, f"- {new_path}{newline}")
    return (b"\xef\xbb\xbf" if bom else b"") + "".join(lines).encode("utf-8")


def candidate_alignment(rows: list[dict[str, str]], candidate_id: str) -> dict[str, str]:
    return one(rows, "candidate_id", candidate_id)


plans: dict[str, bytes] = {}


def prepare() -> None:
    # All existing edits are explicit and checked before any file is written.
    alignment_path = TABLES / "alignment.csv"
    fields, alignments, bom, newline = read_csv(alignment_path)
    if len(alignments) != 12720:
        raise ValueError(f"alignment baseline changed: {len(alignments)}")
    update_rows = {
        "cand-1068": {
            "decision": "same", "ku_id": WORK, "external_source": "", "external_id": "",
            "accessed_date": "", "process_ref": PROCESS_REF,
            "resolution_note": (
                "S3 same→existing KU: F.csv#83 是挂在 Franceschini 名下的作品子目，"
                "不是人物候选；子目题名与正文 cand-7860、图版 cand-4006 所指同一 La Burla，"
                f"三者统一到 {WORK}。索引页码仅作定位，身份由同名作品的跨源锚点确认。"
            ),
        },
        "cand-7860": {
            "decision": "same", "ku_id": WORK, "external_source": "", "external_id": "",
            "accessed_date": "", "process_ref": PROCESS_REF,
            "resolution_note": (
                "S3 same→existing KU：Haskell第8章p.231正文作品名与图版37c题名相同；"
                f"图版候选 cand-4006 已映射到 {WORK}，故不另建同一作品卡。"
                "外部Treccani条目也将Piovano Arlotto题材的Franceschini/Volterrano蛋彩画列于Pitti；"
                "不据此消解Haskell同卷图版目录与脚注的Uffizi/Pitti差异。"
                "prior_new_group=workgrp-ec3d0288dc6bb2"
            ),
        },
        "cand-7866": {
            "decision": "new", "ku_id": GIGLIOLI,
            "external_source": "Ministero della Cultura, Bollettino d’Arte VII (1908); Treccani, Volterrano (1937)",
            "external_id": (
                "https://bollettinodarte.cultura.gov.it/wp-content/uploads/Importer/"
                "1349785796180_6_-_Odoardo_H._Giglioli_p._355.pdf; "
                "https://www.treccani.it/enciclopedia/volterrano_(Enciclopedia-Italiana)/"
            ),
            "accessed_date": "2026-10-23", "process_ref": PROCESS_REF,
            "resolution_note": (
                "S3 new→archive-group-giglioli-volterrano-uffizi-1908：p.231注2的Giglioli 1908"
                "与第21章书目L526–527唯一的Giglioli 1908文章相符；官方期刊扫描与Treccani"
                "确认文章题名及VII卷、印刷页355–358。Haskell书目页码335–358与外部书目不一致，"
                "差异保留。此身份决定只确认被引文章，不据其前页内容确认某一件实物画的同一性。"
            ),
        },
        "cand-7867": {
            "decision": "new", "ku_id": STEINBART, "external_source": "", "external_id": "",
            "accessed_date": "", "process_ref": PROCESS_REF,
            "resolution_note": (
                "S4登记：沿用既有S3 new组 archive-group-7dc45d864705，"
                f"映射到 {STEINBART}；只据Haskell注2和书目确认书目身份，文章正文未查。"
            ),
        },
        "cand-12095": {
            "decision": "new", "ku_id": TUSCAN, "external_source": "", "external_id": "",
            "accessed_date": "", "process_ref": PROCESS_REF,
            "resolution_note": (
                "S4登记：沿用既有S3 new组 sg3-term-cand-12095，"
                f"映射到 {TUSCAN}。术语仅限定为Haskell p.231的来源局部风格及题材判断，"
                "不定义整个托斯卡纳叙事传统或其成员。"
            ),
        },
    }
    for candidate_id, values in update_rows.items():
        row = candidate_alignment(alignments, candidate_id)
        old_id = row["alignment_id"]
        old_resolution_note = row["resolution_note"]
        if candidate_id == "cand-1068" and old_id != "aln-1403":
            raise ValueError("cand-1068 alignment id changed")
        if candidate_id == "cand-7860" and old_id != "aln-8035":
            raise ValueError("cand-7860 alignment id changed")
        if candidate_id == "cand-7866" and old_id != "aln-8041":
            raise ValueError("cand-7866 alignment id changed")
        if candidate_id == "cand-7867" and old_id != "aln-8042":
            raise ValueError("cand-7867 alignment id changed")
        if candidate_id == "cand-12095" and old_id != "aln-12258":
            raise ValueError("cand-12095 alignment id changed")
        if candidate_id == "cand-1068" and row["decision"] != "undecided":
            raise ValueError("cand-1068 is no longer undecided")
        if candidate_id == "cand-7860" and row["decision"] != "new":
            raise ValueError("cand-7860 is no longer new")
        if candidate_id == "cand-7866" and row["decision"] != "undecided":
            raise ValueError("cand-7866 is no longer undecided")
        if candidate_id in {"cand-7867", "cand-12095"} and row["decision"] != "new":
            raise ValueError(f"{candidate_id} is no longer new")
        for key, value in values.items():
            if key == "resolution_note":
                continue
            set_cell(row, key, value)
        if candidate_id in {"cand-1068", "cand-7860", "cand-7866"}:
            row["resolution_note"] = (
                values["resolution_note"] + " | prior_s3_resolution=" + old_resolution_note
            )
        else:
            row["resolution_note"] = (
                old_resolution_note + " | " + values["resolution_note"]
            )
    plans["04-knowledge/tables/alignment.csv"] = render_csv(fields, alignments, bom, newline)

    candidate_path = TABLES / "entity-candidates.csv"
    fields, candidates, bom, newline = read_csv(candidate_path)
    candidate = one(candidates, "candidate_id", "cand-7866")
    candidate["detail"] = (
        "Haskell p.231 note 2 cites Giglioli 1908; this corresponds to the unique 1908 Giglioli article "
        "listed at p.423, lines 526–527. External bibliographic sources identify Bollettino d’Arte VII, "
        "pp.355–358; Haskell gives pp.335–358, retained as a pagination discrepancy. The cited article "
        "was not fully read, and this candidate does not identify a particular physical painting."
    )
    plans["04-knowledge/tables/entity-candidates.csv"] = render_csv(fields, candidates, bom, newline)

    manifest_rows = [
        {"ku_id": GIGLIOLI, "type": "archive", "canonical_name": "《乌菲齐美术馆中的沃尔泰拉诺画作：此前误归乔瓦尼·达·圣乔瓦尼》（A Painting by Volterrano in the Uffizi Gallery, Previously Attributed to Giovanni da San Giovanni）", "name_en": "A Painting by Volterrano in the Uffizi Gallery, Previously Attributed to Giovanni da San Giovanni", "source_task": "patrons-and-painters-full-book-s2", "card_path": f"04-knowledge/{GIGLIOLI}.md"},
        {"ku_id": STEINBART, "type": "archive", "canonical_name": "《阿尔洛托教区神父的绘画笑谈》（Painted Comic Tales of the Parish Priest Arlotto）", "name_en": "Painted Comic Tales of the Parish Priest Arlotto", "source_task": "patrons-and-painters-full-book-s2", "card_path": f"04-knowledge/{STEINBART}.md"},
        {"ku_id": TUSCAN, "type": "term", "canonical_name": "哈斯克尔所述的十五世纪托斯卡纳叙事传统（Fifteenth-Century Tuscan Narrative Tradition in Haskell’s Comparison）", "name_en": "Fifteenth-Century Tuscan Narrative Tradition in Haskell’s Comparison", "source_task": "patrons-and-painters-full-book-s2", "card_path": f"04-knowledge/{TUSCAN}.md"},
    ]
    fields, manifest, bom, newline = read_csv(TABLES / "ku-manifest.csv")
    known = {row["ku_id"] for row in manifest}
    for row in manifest_rows:
        if row["ku_id"] in known or not (BASE / row["card_path"]).is_file():
            raise ValueError(f"new manifest card already registered or missing: {row['ku_id']}")
        manifest.append(row)
    plans["04-knowledge/tables/ku-manifest.csv"] = render_csv(fields, manifest, bom, newline)
    accepted_paths = [row["card_path"] for row in manifest_rows]
    plans["04-knowledge/accepted.yml"] = accepted_with(accepted_paths)

    # Preserve the source-line record while separating acquisition, creation,
    # location, and each citation into independent claims.
    statements_path = TABLES / "book-statements.jsonl"
    _, statements = read_jsonl(statements_path)
    purchase = one(statements, "statement_id", "st-chp8-p231-la-burla-purchase-and-making")
    note2 = one(statements, "statement_id", "st-chp8-p231-note2-la-burla-location-history")
    if any(row.get("statement_id") in {
        "st-chp8-p231-la-burla-created-by",
        "st-chp8-p231-note2-cites-giglioli-1908",
        "st-chp8-p231-note2-cites-steinbart-1936",
    } for row in statements):
        raise ValueError("one or more planned p.231 statement ids already exist")
    full_purchase_quote = purchase["original_quote"]
    full_note_quote = note2["original_quote"]
    purchase_q = purchase["qualifiers"]
    purchase["predicate"] = "ferdinand_bought_la_burla_before_1693"
    purchase_q["claim"] = "Haskell reports that Ferdinand bought La Burla del Pievano Arlotto some time before 1693."
    purchase_q["qualification"] = "This is Haskell’s report of buyer and date; it does not identify the unnamed earlier private citizen or independently confirm the purchase date."
    purchase_q["mentioned_candidate_ids"] = ["cand-1609", "cand-7860"]
    purchase_q["relation_candidate"] = True

    creator = json.loads(json.dumps(purchase, ensure_ascii=False))
    creator["statement_id"] = "st-chp8-p231-la-burla-created-by"
    creator["subject_candidate_id"] = "cand-7860"
    creator["object_candidate_id"] = "cand-1066"
    creator["predicate"] = "franceschini_painted_la_burla_in_tempera_for_private_citizen"
    creator["qualifiers"] = {
        "source_line_start": 243, "source_line_end": 244, "printed_page": 231,
        "pdf_physical_page": 33,
        "claim": "Haskell reports that Baldassare Franceschini had painted La Burla in tempera many years earlier for an unnamed private citizen.",
        "speaker": "Haskell", "text_layer": "body",
        "qualification": "The creator, tempera medium, relative chronology, and unnamed private-citizen context follow Haskell’s report; no exact creation year, commission edge, or person identity is inferred.",
        "mentioned_candidate_ids": ["cand-7860", "cand-1066"],
        "relation_candidate": True,
    }
    creator["original_quote"] = full_purchase_quote
    note2["predicate"] = "footnote_reports_la_burla_at_pitti_no_582"
    note2_q = note2["qualifiers"]
    note2_q["claim"] = "Haskell’s p.231 note 2 reports La Burla at the Pitti, no. 582."
    note2_q["qualification"] = "The OCR reads ‘Pitri’; the page image reads ‘Pitti’. This conflicts within the same volume with the plate-list caption ‘Uffizi, Florence’; keep the location candidate pending. No. 582 is preserved as Haskell’s locator, not asserted to be a current inventory number."
    note2_q["mentioned_candidate_ids"] = ["cand-7860", "cand-1949"]
    note2_q["relation_candidate"] = True
    note2_q["linked_body_statement_ids"] = [
        "st-chp8-p231-la-burla-purchase-and-making",
        "st-chp8-p231-la-burla-created-by",
    ]
    note2_q["ocr_corrections"] = [
        {"source_line": 410, "ocr": "Pitri", "print": "Pitti", "basis": "CHP-8.pdf physical page 33"}
    ]
    note2["original_quote"] = "2 Now in the Pitri, No. 582."
    cites_giglioli = json.loads(json.dumps(note2, ensure_ascii=False))
    cites_giglioli["statement_id"] = "st-chp8-p231-note2-cites-giglioli-1908"
    cites_giglioli["subject_candidate_id"] = "cand-2962"
    cites_giglioli["object_candidate_id"] = "cand-7866"
    cites_giglioli["predicate"] = "haskell_note2_cites_giglioli_1908_for_history"
    cites_giglioli["qualifiers"] = {
        "source_line_start": 410, "source_line_end": 410, "printed_page": 231,
        "pdf_physical_page": 33,
        "claim": "Haskell’s p.231 note 2 cites Giglioli (1908) for the history of La Burla.",
        "speaker": "Haskell", "text_layer": "footnote citation",
        "qualification": "The article identity is aligned with the unique Giglioli 1908 bibliography item in Chapter 21. Haskell’s pages 335–358 conflict with Treccani and the official scan (pp.355–358); the article’s full text and the identity of the specific painting were not established here.",
        "mentioned_candidate_ids": ["cand-2962", "cand-7860", "cand-7866"],
        "relation_candidate": True,
        "linked_body_statement_ids": ["st-chp8-p231-la-burla-purchase-and-making"],
    }
    cites_giglioli["qualifiers"].pop("ocr_corrections", None)
    cites_giglioli["original_quote"] = full_note_quote
    cites_steinbart = json.loads(json.dumps(cites_giglioli, ensure_ascii=False))
    cites_steinbart["statement_id"] = "st-chp8-p231-note2-cites-steinbart-1936"
    cites_steinbart["object_candidate_id"] = "cand-7867"
    cites_steinbart["predicate"] = "haskell_note2_cites_steinbart_1936_for_history"
    cites_steinbart["qualifiers"]["claim"] = "Haskell’s p.231 note 2 cites Steinbart (1936) for the history of La Burla."
    cites_steinbart["qualifiers"]["qualification"] = "The page image reads ‘Steinbart’; the OCR transcript has ‘Steinhart’. Haskell’s Chapter 21 bibliography gives the article title and pp.233–234. The article was not independently consulted."
    cites_steinbart["qualifiers"]["mentioned_candidate_ids"] = ["cand-2962", "cand-7860", "cand-7867"]
    cites_steinbart["qualifiers"]["ocr_corrections"] = [
        {"source_line": 410, "ocr": "Steinhart", "print": "Steinbart", "basis": "CHP-8.pdf physical page 33 and Chapter 21 bibliography"}
    ]
    statements.extend([creator, cites_giglioli, cites_steinbart])
    plans["04-knowledge/tables/book-statements.jsonl"] = render_jsonl(statements_path, statements)

    mentions_path = TABLES / "mentions.csv"
    fields, mentions, bom, newline = read_csv(mentions_path)
    new_mentions = [
        {"mention_id": "m-chp8-p231-note2-pitti", "segment_id": "chp-8:08_CHP-8_sec_ii:l372-461", "candidate_id": "cand-1949", "surface_form": "Pitri", "start_char": "4967", "end_char": "4972", "note": "OCR surface; page image reads Pitti. Location statement remains pending against the plate-list Uffizi caption."},
        {"mention_id": "m-chp8-p231-note2-la-burla-coref", "segment_id": "chp-8:08_CHP-8_sec_ii:l372-461", "candidate_id": "cand-7860", "surface_form": "its", "start_char": "4987", "end_char": "4990", "note": "Coreference to La Burla named in the preceding paragraph."},
        {"mention_id": "m-chp8-p231-note2-giglioli", "segment_id": "chp-8:08_CHP-8_sec_ii:l372-461", "candidate_id": "cand-7866", "surface_form": "Giglioli, 1908", "start_char": "5003", "end_char": "5017", "note": "Short citation matched to the unique Giglioli 1908 bibliography item; page-range discrepancy retained."},
        {"mention_id": "m-chp8-p231-note2-steinbart", "segment_id": "chp-8:08_CHP-8_sec_ii:l372-461", "candidate_id": "cand-7867", "surface_form": "Steinhart, 1936", "start_char": "5023", "end_char": "5038", "note": "OCR surface; page image and bibliography read Steinbart."},
    ]
    current_mentions = {row["mention_id"] for row in mentions}
    if any(row["mention_id"] in current_mentions for row in new_mentions):
        raise ValueError("one or more planned p.231 mention ids already exist")
    mentions.extend(new_mentions)
    plans["04-knowledge/tables/mentions.csv"] = render_csv(fields, mentions, bom, newline)

    relation_path = TABLES / "relations.csv"
    fields, relations, bom, newline = read_csv(relation_path)
    expected_ids = [f"rel-{n:04d}" for n in range(1573, 1580)]
    if any(row["relation_id"] in {r["relation_id"] for r in relations} for row in [{"relation_id": x} for x in expected_ids]):
        raise ValueError("one or more planned p.231 relation ids already exist")
    new_relations = [
        {"relation_id": "rel-1573", "subject_ku_id": WORK, "object_ku_id": FERDINAND, "predicate": "acquired_by", "time": "before 1693", "role": "买受者", "scope": "Haskell reports that Ferdinand bought La Burla some time before 1693. This edge records the book’s acquisition report only; it does not identify the earlier private citizen or independently confirm the date.", "origin": "book", "status": "formal", "source_id": SOURCE_ID, "source_span": "printed p. 231, lines 243–244; statement=st-chp8-p231-la-burla-purchase-and-making", "source_file": CH8, "note": "The purchase is separated from the creator and unnamed earlier private-citizen context."},
        {"relation_id": "rel-1574", "subject_ku_id": WORK, "object_ku_id": ARLOTTO, "predicate": "has_subject", "time": "", "role": "题名所指人物", "scope": "The plate-list title names Piovano Arlotto as the painting’s subject. The personal identity is aligned to Arlotto Mainardi through the existing S3 decision; this edge concerns iconographic subject, not sitter status.", "origin": "book", "status": "formal", "source_id": SOURCE_ID, "source_span": "printed p. xiv, lines 105–106; statement=st-fm-pl-p37c-figure", "source_file": PLATES, "note": "S3 identity is reused; no sitter claim is inferred."},
        {"relation_id": "rel-1575", "subject_ku_id": HASKELL, "object_ku_id": GIGLIOLI, "predicate": "cites", "time": "", "role": "被引文章", "scope": "Haskell’s p.231 note 2 cites the identified Giglioli 1908 article for La Burla’s history. The edge records the citation, not that the full article has been read or that it proves the identity/location of a particular painting.", "origin": "book", "status": "formal", "source_id": SOURCE_ID, "source_span": "printed p. 231, note 2, line 410; statement=st-chp8-p231-note2-cites-giglioli-1908", "source_file": CH8, "note": "Haskell’s bibliography pagination pp.335–358 conflicts with external pp.355–358 and remains recorded on the article card."},
        {"relation_id": "rel-1576", "subject_ku_id": HASKELL, "object_ku_id": STEINBART, "predicate": "cites", "time": "", "role": "被引文章", "scope": "Haskell’s p.231 note 2 cites Steinbart (1936) for La Burla’s history. The edge records the citation only; article contents were not independently consulted.", "origin": "book", "status": "formal", "source_id": SOURCE_ID, "source_span": "printed p. 231, note 2, line 410; statement=st-chp8-p231-note2-cites-steinbart-1936", "source_file": CH8, "note": "Page image reads Steinbart; OCR transcript reads Steinhart."},
        {"relation_id": "rel-1577", "subject_ku_id": WORK, "object_ku_id": PITTI, "predicate": "located_at", "time": "", "role": "Haskell注2所称现藏地", "scope": "Haskell’s p.231 note 2 reports Pitti, no.582, but the same volume’s plate-list caption for Plate 37c says Uffizi, Florence. Treccani also places a Volterrano/Piovano Arlotto tempera painting at Pitti, but does not resolve the identity of Haskell’s particular item. Preserve as pending.", "origin": "book", "status": "pending", "source_id": SOURCE_ID, "source_span": "printed p. 231, note 2, line 410; statement=st-chp8-p231-note2-la-burla-location-history", "source_file": CH8, "note": "Contradictory in-volume location evidence; do not overwrite existing Uffizi/Florence edges."},
        {"relation_id": "rel-1578", "subject_ku_id": WORK, "object_ku_id": TUSCAN, "predicate": "influenced_by", "time": "", "role": "风格来源判断", "scope": "Haskell judges that the work’s homely, archaic simplicity owed more in style to fifteenth-century Tuscan narrative than to contemporary experiments in naturalism elsewhere in Italy. This is an attributed comparative interpretation, not independently verified influence history.", "origin": "book", "status": "formal", "source_id": SOURCE_ID, "source_span": "printed p. 231, line 245; statement=st-chp8-p231-la-burla-style-and-subject", "source_file": CH8, "note": "The negative comparison candidate is not treated as a positive influence endpoint."},
        {"relation_id": "rel-1579", "subject_ku_id": WORK, "object_ku_id": TUSCAN, "predicate": "influenced_by", "time": "", "role": "题材灵感判断", "scope": "Haskell separately judges that the subject inspiration owed more to fifteenth-century Tuscan narrative than to contemporary experiments in naturalism elsewhere in Italy. This is an attributed comparative interpretation, not an independently verified influence history.", "origin": "book", "status": "formal", "source_id": SOURCE_ID, "source_span": "printed p. 231, line 245; statement=st-chp8-p231-la-burla-subject-inspiration", "source_file": CH8, "note": "Kept distinct from the stylistic judgment; the negative comparison candidate is not a positive influence endpoint."},
    ]
    relations.extend(new_relations)
    plans["04-knowledge/tables/relations.csv"] = render_csv(fields, relations, bom, newline)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the reviewed p.231 batch")
    args = parser.parse_args()
    prepare()
    for relative, payload in plans.items():
        path = BASE / relative
        old = path.read_bytes()
        print(f"{relative}: {len(old)} -> {len(payload)} bytes; changed={old != payload}")
    print("planned: S3 3 candidate decisions; S4 3 new KU registrations; S2 +3 statements and +4 mentions; S6 +8 candidate decisions, 7 new relation rows (6 formal, 1 pending); S5 card-field extraction is a separate targeted step.")
    if not args.apply:
        print("preview only; pass --apply after reviewing this scoped batch")
        return 0
    for relative, payload in plans.items():
        atomic_write(BASE / relative, payload)
    print("applied p.231 scoped S3/S4/S6 batch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
