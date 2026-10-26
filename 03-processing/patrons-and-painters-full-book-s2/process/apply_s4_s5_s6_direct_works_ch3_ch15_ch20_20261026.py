#!/usr/bin/env python3
"""Register four source-local S4 endpoints and their traceable S6 decisions.

Default mode is a read-only preflight. Use --apply only after reviewing the
source-bounded card text, mappings, statements, and relation rows below.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
UNITS = ROOT / "04-knowledge" / "units"
PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md"
    "#s4-s5-s6-direct-works-ch3-ch15-ch20-20261026"
)
TASK = "patrons-and-painters-full-book-s2"
TODAY = "2026-10-26"
HASKELL_ID = "haskell-1980-rev-ed"
HASKELL_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)."
)


def file_bytes(path: Path) -> bytes:
    return path.read_bytes()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool, str]:
    raw = file_bytes(path)
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    rows = list(csv.DictReader(io.StringIO(text, newline="")))
    header = list(rows[0]) if rows else next(csv.reader(io.StringIO(text)))
    return header, rows, bom, newline


def append_csv(path: Path, rows: list[dict[str, str]]) -> bytes:
    header, _, _, newline = read_csv(path)
    stream = io.StringIO(newline="")
    csv.DictWriter(stream, fieldnames=header, extrasaction="ignore", lineterminator=newline).writerows(rows)
    prior = file_bytes(path)
    addition = stream.getvalue().encode("utf-8")
    if prior and not prior.endswith((b"\n", b"\r")):
        prior += newline.encode("ascii")
    return prior + addition


def patch_csv(path: Path, key_field: str, updates: dict[str, dict[str, str]],
              appends: list[dict[str, str]] | None = None) -> bytes:
    header, rows, bom, newline = read_csv(path)
    by_key = {row[key_field]: row for row in rows}
    missing = set(updates) - set(by_key)
    if missing:
        raise ValueError(f"{path.name}: missing {key_field} values {sorted(missing)}")
    for key, values in updates.items():
        by_key[key].update(values)
    appends = appends or []
    append_keys = [row[key_field] for row in appends]
    if len(append_keys) != len(set(append_keys)) or set(append_keys) & set(by_key):
        raise ValueError(f"{path.name}: duplicate appended {key_field}")
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=header, extrasaction="ignore", lineterminator=newline)
    writer.writeheader()
    for row in rows:
        writer.writerow(by_key[row[key_field]])
    writer.writerows(appends)
    return (b"\xef\xbb\xbf" if bom else b"") + stream.getvalue().encode("utf-8")


def append_jsonl(path: Path, records: list[dict]) -> bytes:
    prior = file_bytes(path)
    newline = b"\r\n" if b"\r\n" in prior else b"\n"
    content = b"".join(
        json.dumps(record, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + newline
        for record in records
    )
    return prior + (b"" if not prior or prior.endswith((b"\n", b"\r")) else newline) + content


def write_atomic(path: Path, content: bytes) -> None:
    temp = path.with_name(path.name + ".codex-tmp")
    temp.write_bytes(content)
    os.replace(temp, path)


def source(source_file: str, location: str, summary: str, quote: str, span: str) -> dict:
    return {
        "citation": HASKELL_CITATION,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span, "text": quote}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": source_file,
            "source_span": span,
        },
    }


def card(title: str, name_en: str, card_type: str, source_data: dict,
         description_zh: str, description_en: str,
         sections: list[tuple[str, list[tuple[str, str, str]]]]) -> bytes:
    front = {
        "title": f"{title}（{name_en}）",
        "name_en": name_en,
        "type": card_type,
        "evidence_status": "source_backed",
        "sources": [source_data],
        "created": TODAY,
        "updated": TODAY,
        "process_ref": PROCESS_REF,
    }
    text = [
        "---", yaml.safe_dump(front, sort_keys=False, allow_unicode=True, width=110).rstrip(), "---", "",
        "## 内容", "", "### 描述", "",
        f"**中文：** {description_zh}", "", f"**English:** {description_en}", "",
    ]
    for heading, rows in sections:
        text.extend([f"### {heading}", "", "| 字段 | 值 | 证据 |", "|---|---|---|"])
        text.extend(f"| {field} | {value} | {evidence} |" for field, value, evidence in rows)
        text.append("")
    text.extend([
        "## 关系与证据", "", "### 关系记录", "",
        "正式关系由 `relations.csv` 记录并生成；本卡保留的来源关系候选及范围说明见[过程记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-direct-works-ch3-ch15-ch20-20261026)。", "",
    ])
    return ("\n".join(text) + "\n").encode("utf-8")


def build() -> tuple[dict[Path, bytes], list[dict], list[dict]]:
    source3 = "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
    source15 = "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
    source20 = "02-sources/02-Markdown/20_CHP-20Postscript.md"
    ev3 = "S1；第3章，印刷页81 L49；PDF物理页23"
    ev15 = "S1；第15章，印刷页368 L41；PDF物理页8"
    ev20 = "S1；第20章后记，印刷页409 L197；PDF物理页18"

    cards = {
        "units/works/painted-conch-gesu-apse.md": card(
            "耶稣堂后殿半穹顶绘饰", "Painted Conch of the Gesù Apse", "work",
            source(source3, "第3章，印刷页81 L49；PDF物理页23",
                   "Haskell称Gaulli只绘制了上方拱顶的一小部分及后殿conch。",
                   "Gaulli merely painted a small fraction of the vault above it and the conch of the apse.",
                   "line 49; print p. 81; PDF physical p. 23"),
            "本卡指哈斯克尔所述耶稣堂后殿的 conch（后殿半穹顶内表面）绘饰。原文仅称 Gaulli 绘制了上方拱顶的一小部分及后殿 conch；未说明此处的具体图像、材料、完成时间或存世情况。描述性名称不视为原作题名。",
            "This unit refers to the painted conch (the semi-dome surface) of the Gesù apse, as described by Haskell. The source says only that Gaulli painted a small fraction of the vault above and the apse conch; it does not specify the imagery, material, completion date, or survival of this part. The descriptive name is not treated as an original title.",
            [("名称", [("描述性名称", "Painted Conch of the Gesù Apse；来源未提供正式题名", ev3)]),
             ("基本信息", [("作品类型", "耶稣堂后殿半穹顶内表面绘饰；原文未说明更具体的媒介或材质", ev3),
                           ("书中位置", "耶稣堂后殿 conch", ev3)])],
        ),
        "units/works/memmo-palace-frescoed-gallery-classical-figures.md": card(
            "Memmo家族宫邸古典人物壁画廊饰",
            "Frescoed Gallery of Classical Orators, Poets and Philosophers in the Memmo Family Palace",
            "work", source(source15, "第15章，印刷页368 L41；PDF物理页8",
                           "Haskell称Andrea Memmo曾使家族宫邸装饰有一处壁画廊，绘有古典演说家、诗人与哲学家，人物姓名题写于基座。",
                           "He had had the family palace decorated with a frescoed gallery of classical orators, poets and philosophers, the name of each carefully inscribed on the pedestal.",
                           "line 41; print p. 368; PDF physical p. 8"),
            "本卡记录哈斯克尔所述Memmo家族宫邸中的壁画廊饰项目：以古典演说家、诗人与哲学家为表现对象，并在各自基座上题写姓名。来源将装饰行为归于Andrea Memmo，但未指明画家、确切年代或现存状况。本卡指装饰作品，不把宫邸空间本身合并为作品。",
            "This unit records the frescoed gallery decoration in the Memmo family palace described by Haskell. Its subjects are classical orators, poets, and philosophers, with each name inscribed on a pedestal. The source attributes the act of having the palace decorated to Andrea Memmo but names no painter or exact date and gives no survival status. This unit denotes the decorative work, not the palace space itself.",
            [("名称", [("描述性名称", "Frescoed Gallery of Classical Orators, Poets and Philosophers in the Memmo Family Palace；来源未提供正式题名", ev15)]),
             ("基本信息", [("作品类型", "家族宫邸中的壁画廊饰项目", ev15),
                           ("表现对象", "古典演说家、诗人与哲学家；各人物姓名题写于基座", ev15)])],
        ),
        "units/works/schmidt-etching-felice-salimbeni-for-algarotti-1753.md": card(
            "施密特为阿尔加罗蒂蚀刻的费利切·萨利姆贝尼像",
            "Georg Friedrich Schmidt's Etching of Felice Salimbeni for Algarotti (1753)",
            "work", source(source20, "第20章后记，印刷页409 L197；PDF物理页18",
                           "Haskell称Schmidt为Algarotti蚀刻了歌手Felice Salimbeni的肖像，并以相对叙述置于1752年版画之后一年。",
                           "Georg Friedrich Schmidt in 1752, a year after the same artist had etched for Algarotti the rather epicene features of a singer called Felice Salimbeni.",
                           "line 197; print p. 409; PDF physical p. 18"),
            "本卡记录哈斯克尔称Georg Friedrich Schmidt为Francesco Algarotti蚀刻的Felice Salimbeni肖像。来源称Salimbeni为歌手；1753年是依“1752年之后一年”的措辞推算，并非本段另给的明确年月。本卡不据此推定正式委托合同、现存状态或外部归属已核。",
            "This unit records the portrait etching that Haskell says Georg Friedrich Schmidt made for Francesco Algarotti, depicting Felice Salimbeni. Haskell calls Salimbeni a singer. The date 1753 is derived from the wording “a year after” the 1752 print; it is not separately stated as an explicit year in this clause. This card does not infer a formal commission contract or claim that survival or external attribution has been verified.",
            [("名称", [("描述性名称", "Schmidt's Etching of Felice Salimbeni for Algarotti；依据来源描述编制", ev20)]),
             ("基本信息", [("作品类型", "蚀刻像", ev20),
                           ("表现对象", "歌手Felice Salimbeni；Haskell称其面貌由Schmidt蚀刻", ev20),
                           ("日期", "约1753年；据Haskell“1752年之后一年”的相对叙述推算", ev20)])],
        ),
        "units/persons/felice-salimbeni.md": card(
            "费利切·萨利姆贝尼", "Felice Salimbeni", "person",
            source(source20, "第20章后记，印刷页409 L197；PDF物理页18",
                   "Haskell称Felice Salimbeni为歌手，并将其置于Schmidt为Algarotti蚀刻的肖像语境。",
                   "the rather epicene features of a singer called Felice Salimbeni",
                   "line 197; print p. 409; PDF physical p. 18"),
            "本卡只登记哈斯克尔在第20章后记提到的Felice Salimbeni；作者称其为歌手，并称Schmidt曾为Algarotti蚀刻其肖像。本卡保留书内身份边界，不补入未由本书段落支持的生平或外部身份配对。",
            "This card registers only the Felice Salimbeni mentioned in Chapter 20's postscript. Haskell calls him a singer and says Schmidt etched his portrait for Algarotti. The card stays within the book's identification and adds no biography or external identity match unsupported by this passage.",
            [("身份", [("职业身份", "歌手（Haskell在此处的称谓）", ev20)])],
        ),
    }

    new_statements = [
        {
            "statement_id": "st-chp20-p409-schmidt-salimbeni-etching-subject",
            "segment_id": "chp-20:20_CHP-20Postscript:l187-199",
            "subject_candidate_id": "cand-11136",
            "object_candidate_id": "cand-2345",
            "predicate": "has_subject",
            "qualifiers": {
                "source_line_start": 197, "source_line_end": 197,
                "printed_page": 409, "pdf_physical_page": 18,
                "claim": "Haskell's clause describes the etching as depicting the singer Felice Salimbeni.",
                "speaker": "Haskell", "text_layer": "authorial report of a portrait subject",
                "qualification": "The claim is limited to Haskell's description; no external sitter identification was consulted.",
                "mentioned_candidate_ids": ["cand-11136", "cand-2345"],
                "relation_candidate": True,
                "relation_candidate_note": "The phrase 'the features of a singer called Felice Salimbeni' identifies the person depicted by this etching.",
            },
            "original_quote": "the rather epicene features of a singer called Felice Salimbeni",
            "origin": "book", "source_file": source20,
        },
        {
            "statement_id": "st-chp20-p409-algarotti-etching-recipient",
            "segment_id": "chp-20:20_CHP-20Postscript:l187-199",
            "subject_candidate_id": "cand-11136",
            "object_candidate_id": "cand-0041",
            "predicate": "etched_for",
            "qualifiers": {
                "source_line_start": 197, "source_line_end": 197,
                "printed_page": 409, "pdf_physical_page": 18,
                "claim": "Haskell says Schmidt etched the portrait for Francesco Algarotti.",
                "speaker": "Haskell", "text_layer": "authorial report of a work recipient",
                "qualification": "'For Algarotti' is retained as the source's recipient wording; it does not establish a formal contract or transfer of ownership.",
                "mentioned_candidate_ids": ["cand-0041", "cand-11136"],
                "relation_candidate": True,
                "relation_candidate_note": "The S2 predicate preserves Haskell's wording that the etching was made 'for Algarotti'; no controlled S6 type currently expresses a generic recipient role without implying a gift or commission.",
            },
            "original_quote": "the same artist had etched for Algarotti the rather epicene features of a singer called Felice Salimbeni",
            "origin": "book", "source_file": source20,
        },
    ]

    relations = [
        {"relation_id": "rel-2312", "subject_ku_id": "units/persons/giovan-battista-gaulli", "object_ku_id": "units/works/painted-conch-gesu-apse", "predicate": "creator_of", "time": "", "role": "创作者（Haskell书内报告）", "scope": "第3章所述耶稣堂后殿 conch 绘饰；来源未说明该部分的图像、材料、日期或现存状况。", "origin": "book", "status": "formal", "source_id": HASKELL_ID, "source_span": "Chapter 3, printed p.81 line 49; PDF physical p.23; statement=st-chp3-seciv-l48-56-apse-conch-painted", "source_file": source3, "note": "仅记录Haskell的创作陈述；不扩大为整座后殿或上方拱顶全部装饰，也未作外部作品目录核验。"},
        {"relation_id": "rel-2313", "subject_ku_id": "units/works/memmo-palace-frescoed-gallery-classical-figures", "object_ku_id": "units/persons/andrea-memmo", "predicate": "commissioned_by", "time": "", "role": "委托／促成装饰者（由Haskell因果措辞支持）", "scope": "第15章印刷页368所述Memmo家族宫邸壁画廊饰；不包括对宫邸建筑本身的委托。", "origin": "book", "status": "formal", "source_id": HASKELL_ID, "source_span": "Chapter 15, printed p.368 line 41; PDF physical p.8; statement=st-chp15-p368-memmo-palace-frescoed-gallery", "source_file": source15, "note": "依据‘He had had the family palace decorated’记录书内委托关系；未指明画家、合同或日期，不表示外部独立核验。"},
        {"relation_id": "rel-2314", "subject_ku_id": "units/works/schmidt-etching-felice-salimbeni-for-algarotti-1753", "object_ku_id": "units/persons/georg-friedrich-schmidt", "predicate": "created_by", "time": "", "role": "蚀刻创作者（Haskell书内报告）", "scope": "第20章后记印刷页409所述为Algarotti制作的Felice Salimbeni蚀刻像。", "origin": "book", "status": "formal", "source_id": HASKELL_ID, "source_span": "Chapter 20 postscript, printed p.409 line 197; PDF physical p.18; statement=st-chp20-p409-schmidt-salimbeni-etching", "source_file": source20, "note": "仅记录Haskell的书内创作陈述；未作外部作品目录核验；日期由相对语句推算，故关系time留空。"},
        {"relation_id": "rel-2315", "subject_ku_id": "units/works/schmidt-etching-felice-salimbeni-for-algarotti-1753", "object_ku_id": "units/persons/felice-salimbeni", "predicate": "has_subject", "time": "", "role": "表现对象（Haskell称其为歌手）", "scope": "第20章后记印刷页409所述Schmidt蚀刻像；人物身份仅按Haskell本段识别。", "origin": "book", "status": "formal", "source_id": HASKELL_ID, "source_span": "Chapter 20 postscript, printed p.409 line 197; PDF physical p.18; statement=st-chp20-p409-schmidt-salimbeni-etching-subject", "source_file": source20, "note": "按‘features of a singer called Felice Salimbeni’记录；不声称外部身份消歧已完成。"},
    ]

    manifest_rows = [
        {"ku_id": "units/works/painted-conch-gesu-apse", "type": "work", "canonical_name": "耶稣堂后殿半穹顶绘饰", "name_en": "Painted Conch of the Gesù Apse", "source_task": TASK, "card_path": "04-knowledge/units/works/painted-conch-gesu-apse.md"},
        {"ku_id": "units/works/memmo-palace-frescoed-gallery-classical-figures", "type": "work", "canonical_name": "Memmo家族宫邸古典人物壁画廊饰", "name_en": "Frescoed Gallery of Classical Orators, Poets and Philosophers in the Memmo Family Palace", "source_task": TASK, "card_path": "04-knowledge/units/works/memmo-palace-frescoed-gallery-classical-figures.md"},
        {"ku_id": "units/works/schmidt-etching-felice-salimbeni-for-algarotti-1753", "type": "work", "canonical_name": "施密特为阿尔加罗蒂蚀刻的费利切·萨利姆贝尼像", "name_en": "Georg Friedrich Schmidt's Etching of Felice Salimbeni for Algarotti (1753)", "source_task": TASK, "card_path": "04-knowledge/units/works/schmidt-etching-felice-salimbeni-for-algarotti-1753.md"},
        {"ku_id": "units/persons/felice-salimbeni", "type": "person", "canonical_name": "费利切·萨利姆贝尼", "name_en": "Felice Salimbeni", "source_task": TASK, "card_path": "04-knowledge/units/persons/felice-salimbeni.md"},
    ]
    alignment_updates = {
        "cand-5245": {"ku_id": "units/works/painted-conch-gesu-apse", "process_ref": PROCESS_REF,
                      "resolution_note": "S4沿用S3 new组workgrp-3948aef67b38df登记为耶稣堂后殿conch绘饰；与后殿建筑空间区分，来源未给作品题名、图像、材料或年代。"},
        "cand-10518": {"ku_id": "units/works/memmo-palace-frescoed-gallery-classical-figures", "process_ref": PROCESS_REF,
                       "resolution_note": "S4沿用S3 new组workgrp-c862b229caeec4登记为壁画廊饰作品，不与Memmo家族宫邸空间合并；脚注‘These’的毁坏指代仍待证。"},
        "cand-11136": {"ku_id": "units/works/schmidt-etching-felice-salimbeni-for-algarotti-1753", "process_ref": PROCESS_REF,
                       "resolution_note": "S4沿用S3 new组workgrp-cbc08f62b55de8登记为Schmidt为Algarotti制作的Felice Salimbeni蚀刻像；1753为相对措辞推算，未作外部作品核验。"},
        "cand-2345": {"ku_id": "units/persons/felice-salimbeni", "process_ref": PROCESS_REF,
                      "resolution_note": "S4沿用S3 new组new-person:felice-salimbeni-ea3c867c8e登记为书内所称歌手Felice Salimbeni；未作外部同名身份配对。"},
    }

    paths = {ROOT / "04-knowledge" / name: content for name, content in cards.items()}
    alignment_path = TABLES / "alignment.csv"
    manifest_path = TABLES / "ku-manifest.csv"
    relations_path = TABLES / "relations.csv"
    statements_path = TABLES / "book-statements.jsonl"
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"

    # Validate all source and identity assumptions before constructing writes.
    alignment_header, alignment_rows, _, _ = read_csv(alignment_path)
    alignment_by_candidate = {row["candidate_id"]: row for row in alignment_rows}
    for candidate_id, update in alignment_updates.items():
        row = alignment_by_candidate[candidate_id]
        if row["decision"] != "new" or row["ku_id"]:
            raise ValueError(f"unexpected current S3/S4 state for {candidate_id}: {row}")
        update["resolution_note"] = f"{row['resolution_note']} S4: {update['resolution_note']}"
        if update["ku_id"] in {item["ku_id"] for item in read_csv(manifest_path)[1]}:
            raise ValueError(f"manifest already has {update['ku_id']}")
    for path in paths:
        if path.exists():
            raise ValueError(f"card already exists: {path.relative_to(ROOT)}")

    statement_rows = [json.loads(line) for line in statements_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statements_by_id = {row["statement_id"]: row for row in statement_rows}
    expected_existing = {
        "st-chp3-seciv-l48-56-apse-conch-painted": ("cand-1117", "creator_of", "cand-5245"),
        "st-chp15-p368-memmo-palace-frescoed-gallery": ("cand-10518", "commissioned_by", "cand-1642"),
        "st-chp20-p409-schmidt-salimbeni-etching": ("cand-11136", "created_by", "cand-2396"),
    }
    for statement_id, (subject, predicate, obj) in expected_existing.items():
        row = statements_by_id[statement_id]
        if (row["subject_candidate_id"], row["predicate"], row["object_candidate_id"]) != (subject, predicate, obj):
            raise ValueError(f"source statement changed: {statement_id}")
    new_ids = {row["statement_id"] for row in new_statements}
    if new_ids & statements_by_id.keys():
        raise ValueError(f"new statement IDs already exist: {sorted(new_ids & statements_by_id.keys())}")
    if "m-chp20-p409-034" not in alignment_by_candidate["cand-2345"]["resolution_note"]:
        raise ValueError("Felice candidate's source mention anchor is missing")
    endpoint_targets = {"cand-1642": "units/persons/andrea-memmo",
                       "cand-2396": "units/persons/georg-friedrich-schmidt",
                       "cand-0041": "units/persons/francesco-algarotti",
                       "cand-1117": "units/persons/giovan-battista-gaulli"}
    for candidate_id, expected_ku in endpoint_targets.items():
        if alignment_by_candidate[candidate_id]["ku_id"] != expected_ku:
            raise ValueError(f"existing relation endpoint mapping changed: {candidate_id}")

    _, current_relations, _, _ = read_csv(relations_path)
    if [row["relation_id"] for row in current_relations[-1:]] != ["rel-2311"]:
        raise ValueError("relations.csv boundary moved; review relation IDs before applying")
    _, current_manifest, _, _ = read_csv(manifest_path)
    existing_ku_ids = {row["ku_id"] for row in current_manifest}
    if any(row["ku_id"] in existing_ku_ids for row in manifest_rows):
        raise ValueError("one or more new KUs already exist in the manifest")
    accepted_raw = accepted_path.read_bytes()
    accepted_bom = accepted_raw.startswith(b"\xef\xbb\xbf")
    accepted_text = accepted_raw.decode("utf-8-sig")
    accepted_paths = {row["card_path"] for row in current_manifest}
    if any(row["card_path"] in accepted_paths for row in manifest_rows):
        raise ValueError("one or more new cards already appear in the manifest")
    if any(row["card_path"] in accepted_text for row in manifest_rows):
        raise ValueError("one or more new cards already appear in accepted.yml")
    claims_token = "claims:\r\n" if "claims:\r\n" in accepted_text else "claims:\n"
    if claims_token not in accepted_text:
        raise ValueError("accepted.yml insertion boundary changed")

    alignment_ids = {
        "cand-5245": "aln-5428",
        "cand-10518": "aln-10688",
        "cand-11136": "aln-11299",
        "cand-2345": "aln-2680",
    }
    alignment_updates_by_id = {
        alignment_ids[candidate_id]: values
        for candidate_id, values in alignment_updates.items()
    }

    files = {
        **paths,
        alignment_path: patch_csv(alignment_path, "alignment_id", alignment_updates_by_id),
        manifest_path: append_csv(manifest_path, manifest_rows),
        relations_path: append_csv(relations_path, relations),
        statements_path: append_jsonl(statements_path, new_statements),
        accepted_path: (accepted_text.replace(
            claims_token,
            "".join(f"- {row['card_path']}" + ("\r\n" if claims_token.endswith("\r\n") else "\n") for row in manifest_rows) + claims_token,
            1,
        )).encode("utf-8"),
    }
    if accepted_bom:
        files[accepted_path] = b"\xef\xbb\xbf" + files[accepted_path]
    return files, new_statements, relations


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the preflighted batch")
    args = parser.parse_args()
    files, statements, relations = build()
    print(f"cards={sum(path.suffix == '.md' and 'units' in path.parts for path in files)}")
    print(f"new_statements={len(statements)}; relation_rows={len(relations)}; source_backed_field_rows=11")
    for path in files:
        print(f"{'WRITE' if args.apply else 'PREVIEW'} {path.relative_to(ROOT)}")
    if args.apply:
        for path, content in files.items():
            write_atomic(path, content)
        print("apply=complete")
    else:
        print("apply=not-run")


if __name__ == "__main__":
    main()
