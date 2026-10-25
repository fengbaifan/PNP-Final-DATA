from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
BACKUP = ROOT / "06-runtime" / "recovery" / "s3-s4-s5-s6-malvasia-edition-20261025"
PROCESS_REF = "S3-S4-S5-S6-ch7-malvasia-1841-edition-20261025"
EDITION_KU = "units/archives/felsina-pittrice-bologna-1841-edition"
EDITION_CARD = "04-knowledge/units/archives/felsina-pittrice-bologna-1841-edition.md"
GROUP_ID = "archive-group-27687f35cb8d5962"
TABLE_ID = "tbl-" + hashlib.sha256(
    f"{EDITION_KU}|内容 / 基本信息|1|字段|值|证据".encode("utf-8")
).hexdigest()[:16]
SOURCE_ID = "haskell-1980-rev-ed"
SOURCE_FILE_CH21 = "02-sources/02-Markdown/21_CHP-21Bibliography.md"


def serialized_record(row: list[str], newline: str) -> str:
    buffer = io.StringIO(newline="")
    csv.writer(buffer, lineterminator=newline).writerow(row)
    return buffer.getvalue()


def update_csv(
    path: Path,
    key_column: str,
    edits: dict[str, dict[str, str]],
    appends: list[dict[str, str]] | None = None,
    apply: bool = True,
) -> None:
    raw = path.read_bytes()
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    text = raw[len(bom):].decode("utf-8")
    physical_lines = text.splitlines(keepends=True)
    reader = csv.reader(io.StringIO(text, newline=""))
    headers = next(reader)
    if key_column not in headers:
        raise ValueError(f"{path}: missing key column {key_column}")
    changed: set[str] = set()
    output: list[str] = []
    cursor = reader.line_num
    output.extend(physical_lines[:cursor])
    for row in reader:
        end = reader.line_num
        raw_record = "".join(physical_lines[cursor:end])
        cursor = end
        if len(row) != len(headers):
            raise ValueError(f"{path}: malformed CSV record at physical line {end}")
        record = dict(zip(headers, row))
        key = record.get(key_column, "")
        changes = edits.get(key)
        if changes:
            if key in changed:
                raise ValueError(f"{path}: duplicate key {key}")
            changed.add(key)
            for column, value in changes.items():
                if column not in record:
                    raise ValueError(f"{path}: missing column {column}")
                record[column] = value
            ending = "\r\n" if raw_record.endswith("\r\n") else "\n" if raw_record.endswith("\n") else ""
            output.append(serialized_record([record[h] for h in headers], ending))
        else:
            output.append(raw_record)
    missing = set(edits) - changed
    if missing:
        raise ValueError(f"{path}: expected row(s) not found: {sorted(missing)}")
    if cursor < len(physical_lines):
        output.extend(physical_lines[cursor:])
    if appends:
        newline = "\r\n" if b"\r\n" in raw else "\n"
        if output and not output[-1].endswith(("\r\n", "\n")):
            output.append(newline)
        for record in appends:
            output.append(serialized_record([record.get(h, "") for h in headers], newline))
    if apply:
        path.write_bytes(bom + "".join(output).encode("utf-8"))


def update_statements(apply: bool) -> None:
    path = TABLES / "book-statements.jsonl"
    changed_ids = {
        "st-chp7-p176-n5-cite-malvasia": ("rel-2090", 176, 5, 264),
        "st-chp7-p178-n1-cite-malvasia": ("rel-2091", 178, 1, 261),
        "st-chp7-p182-n3-cite-malvasia": ("rel-2092", 182, 3, 264),
        "st-chp7-p182-n4-cite-malvasia": ("rel-2093", 182, 4, 327),
        "st-chp8-p203-n3-bologna-citations": ("rel-2094", 203, 3, None),
        "st-chp1-secii-l657-n1-cites-malvasia-vol2-p27": ("rel-2095", 16, 1, 27),
    }
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    found: set[str] = set()
    output: list[str] = []
    for line in lines:
        record = json.loads(line)
        statement_id = record.get("statement_id")
        if statement_id not in changed_ids:
            output.append(line)
            continue
        relation_id, printed_page, note_number, locator_page = changed_ids[statement_id]
        qualifiers = record["qualifiers"]
        if statement_id != "st-chp1-secii-l657-n1-cites-malvasia-vol2-p27":
            if record.get("object_candidate_id") != "cand-6933":
                raise ValueError(f"{statement_id}: unexpected citation target")
            record["object_candidate_id"] = "cand-11384"
            qualifiers["citation_publication_candidate_id"] = "cand-11384"
            qualifiers["mentioned_candidate_ids"] = [
                "cand-11384" if value == "cand-6933" else value
                for value in qualifiers.get("mentioned_candidate_ids", [])
            ]
            for citation in qualifiers.get("citations", []):
                if citation.get("publication_candidate_id") == "cand-6933":
                    citation["publication_candidate_id"] = "cand-11384"
            if statement_id == "st-chp8-p203-n3-bologna-citations":
                qualifiers["claim"] = (
                    "Haskell's p.203 footnote 3 cites Malvasia and Zanotti, passim, as general references for the Bologna family collections; "
                    "the Malvasia reference maps to the two-volume Bologna 1841 edition listed in the bibliography."
                )
            else:
                locator = qualifiers.get("citation_locator", "")
                qualifiers["claim"] = (
                    f"Haskell's book cites Malvasia's Felsina Pittrice at {locator} in footnote {note_number}; "
                    "the Haskell bibliography identifies the cited publication as the two-volume Bologna 1841 edition."
                )
        relation_note = (
            f"S6 formal as {relation_id} (cites). This records Haskell's citation to the bibliography-listed Bologna 1841 edition; "
            "the cited printing and page were not independently consulted."
        )
        qualifiers["relation_candidate_note"] = relation_note
        found.add(statement_id)
        output.append(json.dumps(record, ensure_ascii=False) + ("\n" if line.endswith("\n") else ""))
    if found != set(changed_ids):
        raise ValueError(f"book-statements.jsonl: missing statement(s) {sorted(set(changed_ids) - found)}")
    if apply:
        path.write_text("".join(output), encoding="utf-8", newline="")


def make_enrichment_rows() -> list[dict[str, object]]:
    fields = [
        ("题名（书目形式）", "Felsina Pittrice"),
        ("责任者（书目形式）", "Carlo Cesare Malvasia"),
        ("卷数", "2 vols."),
        ("出版地", "Bologna"),
        ("出版年", "1841"),
    ]
    evidence = "S2：Haskell，第21章书目，印刷页428，L743。"
    citation = (
        "Francis Haskell, Patrons and Painters, revised and enlarged ed. "
        "(New Haven and London: Yale University Press, 1980; this printing 2006), "
        "ch. 21, printed p. 428, bibliography L743."
    )
    rows = []
    for index, (field, value) in enumerate(fields, start=1):
        digest = hashlib.sha256(f"{TABLE_ID}|{field}|{value}".encode("utf-8")).hexdigest()[:16]
        rows.append({
            "enrichment_id": f"enr-{17462 + index:05d}",
            "ku_id": EDITION_KU,
            "field": field,
            "value": value,
            "origin": "book",
            "source_id": SOURCE_ID,
            "source_ids": [SOURCE_ID],
            "source_ref": "S2",
            "source_citations": [citation],
            "source_urls": [],
            "evidence": evidence,
            "evidence_status": "source_backed",
            "dispute": None,
            "accessed_date": "",
            "occurrence_id": f"occ-{digest}",
            "table_id": TABLE_ID,
            "table_section": "内容 / 基本信息",
            "has_header": True,
            "table_header": ["字段", "值", "证据"],
            "row_index": index,
            "cells": [field, value, evidence],
            "unit_evidence_status": "source_backed",
        })
    return rows


def make_relation_rows() -> list[dict[str, str]]:
    specs = [
        ("rel-2090", "st-chp7-p176-n5-cite-malvasia", "Chapter 7, printed p.176, note 5, L316", "Haskell第7章印刷页176注5引用 Malvasia, II, p.264。", "第7章脚注书目引文", "Malvasia, II, p.264"),
        ("rel-2091", "st-chp7-p178-n1-cite-malvasia", "Chapter 7, printed p.178, note 1, L324", "Haskell第7章印刷页178注1引用 Malvasia, II, p.261。", "第7章脚注书目引文", "Malvasia, II, p.261"),
        ("rel-2092", "st-chp7-p182-n3-cite-malvasia", "Chapter 7, printed p.182, note 3, L345", "Haskell第7章印刷页182注3引用 Malvasia, II, p.264。", "第7章脚注书目引文", "Malvasia, II, p.264"),
        ("rel-2093", "st-chp7-p182-n4-cite-malvasia", "Chapter 7, printed p.182, note 4, L346", "Haskell第7章印刷页182注4以 ibid. 引用 Malvasia, II, p.327。", "第7章脚注书目引文", "Malvasia, II, p.327"),
        ("rel-2094", "st-chp8-p203-n3-bologna-citations", "Chapter 8, printed p.203, note 3, L9", "Haskell第8章印刷页203注3泛引 Malvasia 与 Zanotti, passim。", "第8章泛引书目引文", "passim"),
        ("rel-2095", "st-chp1-secii-l657-n1-cites-malvasia-vol2-p27", "Chapter 1, printed p.16, note 1, L657-658", "Haskell第1章印刷页16注1引用 Malvasia, II, p.27。", "第1章脚注书目引文", "Malvasia, II, p.27"),
    ]
    rows: list[dict[str, str]] = []
    for relation_id, statement_id, span, chinese_scope, role, locator in specs:
        chapter = "01_CHP-1.md" if statement_id.startswith("st-chp1") else "08_CHP-8_intro.md" if statement_id.startswith("st-chp8") else "07_CHP-7_sec_i.md"
        note = (
            "Haskell's footnote or general note gives this citation pointer; Chapter 21, printed p.428, L743 identifies "
            "the cited Malvasia publication as Felsina Pittrice, two volumes, Bologna 1841. "
            "This formal edge records Haskell's citation only; the cited printing and content were not independently consulted."
        )
        if statement_id.startswith("st-chp8"):
            note = (
                "Haskell's note gives a general passim reference; Chapter 21, printed p.428, L743 identifies the Malvasia "
                "publication as Felsina Pittrice, two volumes, Bologna 1841. The cited publication and pages were not independently consulted."
            )
        rows.append({
            "relation_id": relation_id,
            "subject_ku_id": "units/archives/patrons-and-painters",
            "object_ku_id": EDITION_KU,
            "predicate": "cites",
            "time": "",
            "role": role,
            "scope": f"{chinese_scope} 本边仅记录 Haskell 的书内引注，定位为 {locator}；第21章书目 L743 指向1841年版，不表示已查阅被引页面。",
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": f"{span}; statement={statement_id}; bibliography: Chapter 21, printed p.428, L743",
            "source_file": f"02-sources/02-Markdown/{chapter}",
            "note": note,
        })
    rows.append({
        "relation_id": "rel-2096",
        "subject_ku_id": EDITION_KU,
        "object_ku_id": "units/persons/carlo-cesare-malvasia",
        "predicate": "authored_by",
        "time": "",
        "role": "书目责任者归属",
        "scope": "Haskell第21章印刷页428书目 L743 以“Malvasia, Carlo Cesare”著录《Felsina Pittrice》两卷本 Bologna 1841 年版。本边仅表达书内书目责任者归属。",
        "origin": "book",
        "status": "formal",
        "source_id": SOURCE_ID,
        "source_span": "Chapter 21, printed p.428, bibliography L743; statement=st-chp21-bib-l701-754-entry-25",
        "source_file": SOURCE_FILE_CH21,
        "note": "Bibliographic authorship is structural and is not an S2 relation-candidate adjudication; the edition and its title page were not independently consulted.",
    })
    return rows


def apply_all(apply: bool) -> None:
    with (TABLES / "ku-manifest.csv").open(encoding="utf-8-sig", newline="") as handle:
        manifest_rows = list(csv.DictReader(handle))
    if any(row["ku_id"] == EDITION_KU or row["card_path"] == EDITION_CARD for row in manifest_rows):
        raise ValueError("ku-manifest.csv: edition KU or card path already exists")
    with (TABLES / "alignment.csv").open(encoding="utf-8-sig", newline="") as handle:
        alignments = {row["candidate_id"]: row for row in csv.DictReader(handle)}
    if alignments["cand-11384"]["decision"] != "undecided" or alignments["cand-11384"]["ku_id"]:
        raise ValueError("alignment.csv: cand-11384 is no longer in the expected undecided state")
    if alignments["cand-6933"]["ku_id"] != "units/archives/felsina-pittrice-1678-work":
        raise ValueError("alignment.csv: the 1678 work mapping changed")
    with (TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
        candidate_rows = {row["candidate_id"]: row for row in csv.DictReader(handle)}
    if candidate_rows["cand-11384"]["suggested_type"] != "archive":
        raise ValueError("entity-candidates.csv: cand-11384 type changed")
    if (ROOT / EDITION_CARD).exists():
        raise ValueError(f"edition card already exists: {EDITION_CARD}")

    edits = {
        "cand-6933": {
            "detail": "第7章p.189称《Felsina Pittrice》发表于1678年并题献Louis XIV，作为作品身份单独登记。第21章书目另列1841年Bologna两卷本 cand-11384；第1章p.16、第7章pp.176/178/182及第8章p.203的缩略引注据该唯一书目项映射至1841年版，不归到本候选。被引卷页未查阅。"
        },
        "cand-11384": {
            "detail": "第21章印刷页428书目L743明确列 Carlo Cesare Malvasia, Felsina Pittrice, 2 vols., Bologna 1841。该书目出版物区别于第7章p.189明记为1678年的作品候选 cand-6933。第1章p.16、第7章pp.176/178/182、第8章p.203的短式引注据同一书目项映射本版；只记录Haskell引注定位，未独立查阅印本或被引卷页。"
        },
    }
    update_csv(TABLES / "entity-candidates.csv", "candidate_id", edits, apply=apply)

    alignment_edits = {
        "cand-6933": {
            "process_ref": PROCESS_REF,
            "resolution_note": (
                "source_ref=candidate_ref=chp-7:07_CHP-7_sec_i:l243-257#L253 | mentions=m-chp7-p189-051 | "
                "statements=st-chp7-p189-i21; group=archive-group-04dd83a032f3; S3保留1678年作品身份，依据第7章p.189对题名、年代與题献的明确表述。"
                "第21章书目另列1841年版，四条卷页引注及第8章passim已归属cand-11384，不再计入本作品候选。"
                "本候选已于S4映射units/archives/felsina-pittrice-1678-work。"
            ),
        },
        "cand-11384": {
            "ku_id": EDITION_KU,
            "decision": "new",
            "process_ref": PROCESS_REF,
            "resolution_note": (
                "source_ref=candidate_ref=chp-21:21_CHP-21Bibliography:l701-754#L743 | "
                "mentions=m-chp21-bib-l701-754-025,m-chp8-p203-004 | "
                "statements=st-chp21-bib-l701-754-entry-25,st-chp1-secii-l657-n1-cites-malvasia-vol2-p27,"
                "st-chp7-p176-n5-cite-malvasia,st-chp7-p178-n1-cite-malvasia,st-chp7-p182-n3-cite-malvasia,"
                "st-chp7-p182-n4-cite-malvasia,st-chp8-p203-n3-bologna-citations; "
                f"group={GROUP_ID}; S3于2026-10-25由undecided改为new：第21章印刷页428书目L743明确列出题名、责任者、两卷、Bologna与1841年，"
                "构成与第7章p.189所述1678年作品不同的特定书目出版物身份。第1、7、8章短式引注依唯一书目项映射本版。"
                "被引印本与卷页未独立查阅。S4 registration: mapped to " + EDITION_KU + "."
            ),
        },
    }
    update_csv(TABLES / "alignment.csv", "candidate_id", alignment_edits, apply=apply)

    update_csv(
        TABLES / "mentions.csv",
        "mention_id",
        {"m-chp8-p203-004": {"candidate_id": "cand-11384", "note": "Citation to the bibliography-listed Bologna 1841 edition of Felsina Pittrice; general reference only."}},
        apply=apply,
    )

    update_csv(
        TABLES / "ku-manifest.csv",
        "ku_id",
        {},
        [{
            "ku_id": EDITION_KU,
            "type": "archive",
            "canonical_name": "《博洛尼亚画家传》1841年版",
            "name_en": "Felsina Pittrice (Bologna 1841 two-volume edition)",
            "source_task": "patrons-and-painters-full-book-s2",
            "card_path": EDITION_CARD,
        }],
        apply=apply,
    )

    accepted = ROOT / "04-knowledge" / "accepted.yml"
    accepted_text = accepted.read_text(encoding="utf-8-sig")
    new_path_line = f"- {EDITION_CARD}\n"
    old_path_line = "- 04-knowledge/units/archives/felsina-pittrice-1678-work.md\n"
    if new_path_line not in accepted_text:
        if old_path_line not in accepted_text:
            raise ValueError("accepted.yml: expected 1678 work card entry not found")
        accepted_text = accepted_text.replace(old_path_line, old_path_line + new_path_line, 1)
        if apply:
            accepted.write_text(accepted_text, encoding="utf-8-sig", newline="")

    update_statements(apply=apply)

    enrichment_path = TABLES / "enrichment.jsonl"
    existing_enrichment = [json.loads(line) for line in enrichment_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if any(row.get("ku_id") == EDITION_KU for row in existing_enrichment):
        raise ValueError("enrichment.jsonl: edition fields already exist")
    new_enrichment = make_enrichment_rows()
    existing_enrichment_ids = {row.get("enrichment_id") for row in existing_enrichment}
    if any(row["enrichment_id"] in existing_enrichment_ids for row in new_enrichment):
        raise ValueError("enrichment.jsonl: generated enrichment ID already exists")
    if apply:
        with enrichment_path.open("a", encoding="utf-8", newline="") as handle:
            for row in new_enrichment:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    relation_path = TABLES / "relations.csv"
    with relation_path.open(encoding="utf-8-sig", newline="") as handle:
        existing_relations = list(csv.DictReader(handle))
    new_relations = make_relation_rows()
    existing_ids = {row["relation_id"] for row in existing_relations}
    natural_keys = {
        (row["subject_ku_id"], row["predicate"], row["object_ku_id"], row["time"], row["role"], row["scope"])
        for row in existing_relations
    }
    if any(row["relation_id"] in existing_ids for row in new_relations):
        raise ValueError("relations.csv: generated relation ID already exists")
    if any((row["subject_ku_id"], row["predicate"], row["object_ku_id"], row["time"], row["role"], row["scope"]) in natural_keys for row in new_relations):
        raise ValueError("relations.csv: duplicate natural key")
    update_csv(relation_path, "relation_id", {}, new_relations, apply=apply)


def main() -> int:
    parser = argparse.ArgumentParser(description="Register and align Malvasia's bibliography-listed 1841 edition.")
    parser.add_argument("--apply", action="store_true", help="apply the guarded table updates")
    args = parser.parse_args()
    if not BACKUP.is_dir():
        raise SystemExit(f"Required recovery snapshot missing: {BACKUP}")
    if not (BACKUP / "04-knowledge/tables/alignment.csv").is_file():
        raise SystemExit("Required pre-change alignment backup missing")
    print("candidate: cand-11384 undecided -> new; map to", EDITION_KU)
    print("same/new work boundary: cand-6933 remains mapped to units/archives/felsina-pittrice-1678-work")
    print("reclassify 5 citation statement targets and one p.203 mention to cand-11384")
    print("append 5 source-backed S5 fields, 6 formal S2 cites edges, 1 structural authored_by edge")
    print("relation candidate outcomes: 6 formal citations; dedication edge rejected by controlled domain/range")
    if args.apply:
        apply_all(apply=False)
        apply_all(apply=True)
        print("Applied guarded S3-S6 table updates.")
    else:
        apply_all(apply=False)
        print("Dry run preflight passed; no files changed. Use --apply to write the planned table updates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
