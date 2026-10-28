from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
TASK_REF = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-ch10-p316-endpoints-20261029"
SOURCE_ID = "haskell-1980-rev-ed"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_sec_ii.md"
SOURCE_CITATION = "Francis Haskell, Patrons and Painters, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)."
BOOK_KU = "units/archives/patrons-and-painters"
SEGMENT_ID = "chp-10:10_CHP-10_sec_ii:l108-117"

ITEMS = [
    {
        "candidate_id": "cand-9648",
        "ku_id": "units/works/canaletto-view-grand-canal-campo-s-sofia-rialto",
        "type": "work",
        "canonical_name": "大运河与里亚托的威尼斯景观",
        "name_en": "Canaletto view of the Grand Canal from Campo S. Sofia toward the Rialto",
        "description_zh": "哈斯克尔描述的第一幅施特赖特生活场景：从圣索菲亚广场望向里亚托的大运河全景。书中没有提供正式题名或现藏信息。",
        "description_en": "The first of the two life-related views described by Haskell: a sweep of the Grand Canal from Campo S. Sofia toward the Rialto. No formal title or present location is supplied.",
        "sub_type": "",
        "locations": ["Chapter 10, printed p.316, lines 109-110; PDF physical p.49"],
        "quotes": ["One portrayed a sweep of the Grand Canal looking south-east from the Campo S. Sofia to the Rialto. Well in the foreground is a gondola in which stands Streit himself, while behind can be seen the Palazzo Foscari in which he lived."],
        "evidence": "S2 st-chp10-p316-first-life-canaletto-view and st-chp10-p316-streit-in-gondola-in-first-view; printed p.316, lines 109-110.",
        "field_rows": [
            ("来源所述画面", "A sweep of the Grand Canal from Campo S. Sofia toward the Rialto, with Streit in a foreground gondola and Palazzo Foscari behind.", "Chapter 10, printed p.316, lines 109-110; S2 st-chp10-p316-first-life-canaletto-view"),
        ],
    },
    {
        "candidate_id": "cand-9651",
        "ku_id": "units/works/canaletto-view-campo-di-rialto-streit",
        "type": "work",
        "canonical_name": "里亚托广场景观",
        "name_en": "Canaletto view of Campo di Rialto connected with Sigismund Streit",
        "description_zh": "哈斯克尔所述两幅施特赖特生活场景中的另一幅，画面为里亚托广场。此处的描述性名称不是原作题名。",
        "description_en": "The other of the two life-related views described by Haskell, depicting Campo di Rialto. This descriptive label is not a supplied original title.",
        "sub_type": "",
        "locations": ["Chapter 10, printed p.316, line 110; PDF physical p.49"],
        "quotes": ["The other view was of the Campo di Rialto in which his business activities were carried out."],
        "evidence": "S2 st-chp10-p316-second-life-canaletto-view-at-campo-di-rialto; printed p.316, line 110.",
        "field_rows": [
            ("来源所述画面", "The other life-related view is described as a view of Campo di Rialto.", "Chapter 10, printed p.316, line 110; S2 st-chp10-p316-second-life-canaletto-view-at-campo-di-rialto"),
        ],
    },
    {
        "candidate_id": "cand-9649",
        "ku_id": "units/places/campo-s-sofia-venice",
        "type": "place",
        "canonical_name": "圣索菲亚广场",
        "name_en": "Campo S. Sofia, Venice",
        "description_zh": "哈斯克尔所述大运河景观的观景起点；原文只提供地名，不指定某一建筑或精确地址。",
        "description_en": "The viewpoint named for Haskell's Grand Canal scene; the source supplies the place name but no specific building or address.",
        "sub_type": "",
        "locations": ["Chapter 10, printed p.316, lines 109-110; PDF physical p.49"],
        "quotes": ["One portrayed a sweep of the Grand Canal looking south-east from the Campo S. Sofia to the Rialto."],
        "evidence": "S2 st-chp10-p316-first-life-canaletto-view; printed p.316, lines 109-110.",
        "field_rows": [
            ("书中所述空间角色", "The named viewpoint for the Grand Canal panorama.", "Chapter 10, printed p.316, lines 109-110; S2 st-chp10-p316-first-life-canaletto-view"),
        ],
    },
    {
        "candidate_id": "cand-9650",
        "ku_id": "units/places/palazzo-foscari-venice",
        "type": "place",
        "canonical_name": "福斯卡里宫",
        "name_en": "Palazzo Foscari in Venice",
        "description_zh": "哈斯克尔称其出现在第一幅景观的背景，并称施特赖特住在其中。本卡保留书中所指建筑，不合并其他福斯卡里宫，也不推定现代地址。",
        "description_en": "Haskell identifies the palace behind the gondola and says Streit lived there. This card retains the source-local building reference without merging other Foscari palaces or asserting a modern address.",
        "sub_type": "",
        "locations": ["Chapter 10, printed p.316, line 110; PDF physical p.49"],
        "quotes": ["while behind can be seen the Palazzo Foscari in which he lived."],
        "evidence": "S2 st-chp10-p316-streit-lived-in-palazzo-foscari; printed p.316, line 110.",
        "field_rows": [
            ("书中所述空间角色", "Palace visible behind the gondola; Haskell reports that Streit lived there.", "Chapter 10, printed p.316, line 110; S2 st-chp10-p316-streit-lived-in-palazzo-foscari"),
        ],
    },
    {
        "candidate_id": "cand-9652",
        "ku_id": "units/places/campo-di-rialto-venice",
        "type": "place",
        "canonical_name": "里亚托广场",
        "name_en": "Campo di Rialto, Venice",
        "description_zh": "哈斯克尔所述第二幅景观的画面地点，并称施特赖特的商业活动在此进行；与范围更广的里亚托地区分开。",
        "description_en": "The subject of Haskell's second view and the reported site of Streit's business activities; kept distinct from the broader Rialto area.",
        "sub_type": "",
        "locations": ["Chapter 10, printed p.316, line 110; PDF physical p.49"],
        "quotes": ["The other view was of the Campo di Rialto in which his business activities were carried out."],
        "evidence": "S2 st-chp10-p316-second-life-canaletto-view-at-campo-di-rialto; printed p.316, line 110.",
        "field_rows": [
            ("书中所述空间角色", "Depicted place in the second view; Haskell also reports Streit's business activities there.", "Chapter 10, printed p.316, line 110; S2 st-chp10-p316-second-life-canaletto-view-at-campo-di-rialto"),
        ],
    },
    {
        "candidate_id": "cand-8178",
        "ku_id": "units/places/grand-canal-venice",
        "type": "place",
        "canonical_name": "威尼斯大运河",
        "name_en": "Grand Canal, Venice",
        "description_zh": "哈斯克尔称为第一幅施特赖特生活场景的画面对象之一；本卡限于书中可确认的大运河地名与水道范围。",
        "description_en": "One of the described subjects of the first life-related scene in Streit's collection; this card records the source-identifiable canal and does not assert an exact painted location.",
        "sub_type": "",
        "locations": ["Chapter 10, printed p.316, lines 109-110; PDF physical p.49"],
        "quotes": ["One portrayed a sweep of the Grand Canal looking south-east from the Campo S. Sofia to the Rialto."],
        "evidence": "S2 st-chp10-p316-first-life-canaletto-view; printed p.316, lines 109-110.",
        "field_rows": [
            ("书中所述空间角色", "Waterway represented in the first described view.", "Chapter 10, printed p.316, lines 109-110; S2 st-chp10-p316-first-life-canaletto-view"),
        ],
    },
    {
        "candidate_id": "cand-9206",
        "ku_id": "units/places/rialto-area-venice",
        "type": "place",
        "canonical_name": "威尼斯里亚托地区",
        "name_en": "Rialto area, Venice",
        "description_zh": "第10章景观叙述中的宽泛里亚托地点；与具名的里亚托广场Campo di Rialto分开，不指定建筑或精确点位。",
        "description_en": "The broader Rialto locality named at the far end of the Chapter 10 panorama; distinct from the specifically named Campo di Rialto and not resolved to a building or exact point.",
        "sub_type": "",
        "locations": ["Chapter 10, printed p.316, lines 109-110; PDF physical p.49"],
        "quotes": ["One portrayed a sweep of the Grand Canal looking south-east from the Campo S. Sofia to the Rialto."],
        "evidence": "S2 st-chp10-p316-first-life-canaletto-view; printed p.316, lines 109-110; cross-chapter S3 group sg3-place-rialto-area also cites the p.362 locative reference.",
        "field_rows": [
            ("书中所述空间角色", "Broad locality named as the panorama's far end; not the Campo di Rialto.", "Chapter 10, printed p.316, lines 109-110; S2 st-chp10-p316-first-life-canaletto-view"),
        ],
    },
    {
        "candidate_id": "cand-9637",
        "ku_id": "units/archives/sigismund-streit-notes-about-his-pictures",
        "type": "archive",
        "canonical_name": "西吉斯蒙德·施特赖特关于其绘画的长篇笔记",
        "name_en": "Sigismund Streit's long notes about his pictures",
        "description_zh": "哈斯克尔称施特赖特曾就其绘画作长篇笔记，并指出两幅卡纳莱托景观与其生活有关。笔记原题、形成日期及原件保管处未给出。",
        "description_en": "Haskell says Streit made long notes about his pictures and pointed out the life-related connection of two Canaletto views. No original title, date, or repository is supplied.",
        "sub_type": "notes",
        "locations": ["Chapter 10, printed p.315, line 106; p.316, line 109; PDF physical pp.48-49"],
        "quotes": ["Of his four Canalettos, two showed scenes which were directly concerned with his own life, as he pointed out in the long notes which he made about his pictures."],
        "evidence": "S2 st-chp10-p315-four-canalettos-two-scenes-linked-to-streits-life-fragment and st-chp10-p316-two-life-scenes-noted-about-streits-pictures; printed pp.315-316.",
        "field_rows": [
            ("来源所述文献形态", "Streit's long notes about his pictures; original title, date, and repository are not supplied.", "Chapter 10, printed pp.315-316; S2 st-chp10-p315-four-canalettos-two-scenes-linked-to-streits-life-fragment"),
        ],
    },
    {
        "candidate_id": "cand-9912",
        "ku_id": "units/archives/zimmermann-streit-collection-article-1954",
        "type": "archive",
        "canonical_name": "H. Zimmermann关于施特赖特藏画的论文",
        "name_en": "H. Zimmermann, Über einige Bilder der Sammlung Streit im Grauen Kloster zu Berlin",
        "description_zh": "哈斯克尔第316页脚注及书目第441页著录的期刊论文。本文及其第197–224页未独立查阅；作者的个人身份仍未消歧。",
        "description_en": "The journal article cited in Haskell's Chapter 10 note and listed in the bibliography on p.441. The article and its cited pages were not independently consulted; the author's personal identity remains unresolved.",
        "sub_type": "journal article",
        "locations": ["Chapter 10, printed p.316, note 1, line 294; PDF physical p.49", "Chapter 21, printed p.441; PDF physical p.31"],
        "quotes": ["Streit's notes on his Canalettos have been published by Zimmermann, pp. 197-224.", "Zimmermann, H.: Über einige Bilder der Sammlung Streit im Grauen Kloster zu Berlin in Zeitschrift für Kunstwissenschaft, 1954, pp. 197-224."],
        "evidence": "S2 st-chp10-p316-n01-streit-notes-published-by-zimmermann and st-chp21-bib-l1261-1299-entry-23; Haskell's cited pages/article were not independently read.",
        "field_rows": [
            ("原书所载论文题名", "Über einige Bilder der Sammlung Streit im Grauen Kloster zu Berlin", "Chapter 21, printed p.441, bibliography entry 23; S2 st-chp21-bib-l1261-1299-entry-23"),
            ("原书所载刊物与页码", "Zeitschrift für Kunstwissenschaft, 1954, pp. 197-224.", "Chapter 21, printed p.441; Chapter 10, printed p.316 note 1"),
        ],
    },
    {
        "candidate_id": "cand-9914",
        "ku_id": "units/archives/constable-four-paintings-grauen-kloster-1956",
        "type": "archive",
        "canonical_name": "W. G. Constable关于修道院体育馆四幅绘画的论文",
        "name_en": "W. G. Constable, Four paintings by Antonio Canale in the Gymnasium zum Grauen Kloster, Berlin",
        "description_zh": "哈斯克尔第316页脚注引用并由书目第419页完整著录的论文。论文及被引页未独立查阅；其个人作者身份未在本批注册。",
        "description_en": "The essay cited in Haskell's Chapter 10 note and fully listed in the bibliography on p.419. The essay and cited pages were not independently consulted; no personal author identity is registered in this batch.",
        "sub_type": "essay in collected volume",
        "locations": ["Chapter 10, printed p.316, note 1, line 294; PDF physical p.49", "Chapter 21, printed p.419"],
        "quotes": ["The Canalettos have also been discussed by W. G. Constable, 1956, pp. 81-93, who rejects the attribution to Moretti or some other follower.", "Constable, W. G.: Four paintings by Antonio Canale in the Gymnasium zum Grauen Kloster, Berlin in Scritti di Storia dell'Arte in onore di Lionello Venturi, 1956, II, pp. 81-93."],
        "evidence": "S2 st-chp10-p316-n01-constable-rejected-moretti-attribution and st-chp21-bib-l336-374-entry-26; essay and cited pages not independently consulted.",
        "field_rows": [
            ("原书所载论文题名", "Four paintings by Antonio Canale in the Gymnasium zum Grauen Kloster, Berlin", "Chapter 21, printed p.419, bibliography entry 26; S2 st-chp21-bib-l336-374-entry-26"),
            ("原书所载文集与页码", "Scritti di Storia dell'Arte in onore di Lionello Venturi, 1956, vol. II, pp. 81-93.", "Chapter 21, printed p.419; Chapter 10, printed p.316 note 1"),
        ],
    },
]


def read_csv(name):
    path = TABLES / name
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return path, reader.fieldnames, list(reader)


def write_csv_atomic(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp_path = Path(stream.name)
    temp_path.replace(path)


def unique_by(rows, field, value):
    matches = [row for row in rows if row.get(field) == value]
    if len(matches) != 1:
        raise SystemExit(f"expected one {field}={value!r}; found {len(matches)}")
    return matches[0]


def stable_hash(value, length=16):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def make_card(item):
    is_article = item["candidate_id"] in {"cand-9912", "cand-9914"}
    if item["candidate_id"] == "cand-9912":
        bibliographic_sources = [
            (item["locations"][0], "Haskell says Streit's notes were published by Zimmermann.", item["quotes"][0], SOURCE_FILE, "line 294; printed p.316, note 1"),
            (item["locations"][1], "Haskell's bibliography supplies the article title, journal, year, and pages; the article itself was not consulted.", item["quotes"][1], "02-sources/02-Markdown/21_CHP-21Bibliography.md", "lines 1297-1298; printed p.441; PDF physical p.31"),
        ]
    elif item["candidate_id"] == "cand-9914":
        bibliographic_sources = [
            (item["locations"][0], "Haskell reports the citation and Constable's rejection of an attribution to Moretti or another follower; cited pages were not read.", item["quotes"][0], SOURCE_FILE, "line 294; printed p.316, note 1"),
            (item["locations"][1], "Haskell's bibliography supplies the essay title, collected volume, year, and pages; the essay itself was not consulted.", item["quotes"][1], "02-sources/02-Markdown/21_CHP-21Bibliography.md", "lines 371-372; printed p.419"),
        ]
    else:
        bibliography_sources = []
        for location, quote in zip(item["locations"], item["quotes"]):
            span = "lines 109-110; printed p.316" if "p.316" in location else "line 106; printed p.315"
            bibliography_sources.append((location, item["evidence"], quote, SOURCE_FILE, span))
        bibliographic_sources = bibliography_sources

    sources = []
    for location, summary, quote, source_file, span in bibliographic_sources:
        sources.append({
            "citation": SOURCE_CITATION,
            "location": location,
            "sentence_summary": summary,
            "original_quotes": [{"source_span": span, "text": quote}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": source_file,
                "source_span": span,
            },
        })
    meta = {
        "title": f"{item['canonical_name']}（{item['name_en']}）",
        "name_en": item["name_en"],
        "type": item["type"],
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-29",
        "updated": "2026-10-29",
        "process_ref": TASK_REF,
    }
    if item["sub_type"]:
        meta["sub_type"] = item["sub_type"]
    front = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=110).rstrip()
    table_rows = "\n".join(
        "| " + " | ".join(str(value).replace("|", "\\|") for value in row) + " |"
        for row in item["field_rows"]
    )
    content = (
        "## 内容\n\n"
        "### 描述\n\n"
        f"**中文：** {item['description_zh']}\n\n"
        f"**English:** {item['description_en']}\n\n"
        "### 基本信息\n\n"
        "| 字段 | 值 | 证据 |\n"
        "|---|---|---|\n"
        + table_rows + "\n\n"
        "## 关系与证据\n\n"
        "### 身份与外部链接\n\n"
        "本批依据《赞助人与画家》的正文和书目建立来源限定记录，未查阅外部目录或所引文献原件。\n"
    )
    return "---\n" + front + "\n---\n" + content


def natural_key(row):
    return tuple(row.get(key, "") for key in ("subject_ku_id", "predicate", "object_ku_id", "time", "role", "scope"))


def relation(subject, obj, predicate, status, span, role, scope, note=""):
    return {
        "relation_id": "",
        "subject_ku_id": subject,
        "object_ku_id": obj,
        "predicate": predicate,
        "time": "",
        "role": role,
        "scope": scope,
        "origin": "book",
        "status": status,
        "source_id": SOURCE_ID,
        "source_span": span,
        "source_file": SOURCE_FILE,
        "note": note,
    }


parser = argparse.ArgumentParser(description="Register the reviewed Chapter 10 p.316 direct source endpoints.")
parser.add_argument("--apply", action="store_true", help="write the reviewed S4/S5/S6 batch")
args = parser.parse_args()

manifest_path, manifest_fields, manifest = read_csv("ku-manifest.csv")
alignment_path, alignment_fields, alignments = read_csv("alignment.csv")
backlog_path, backlog_fields, backlog = read_csv("candidate-backlog.csv")
relations_path, relation_fields, relations = read_csv("relations.csv")
enrichment_path = TABLES / "enrichment.jsonl"
accepted_path = ROOT / "04-knowledge" / "accepted.yml"

existing_manifest = {row["ku_id"] for row in manifest}
existing_paths = {row["card_path"] for row in manifest}
for item in ITEMS:
    candidate_alignments = [row for row in alignments if row["candidate_id"] == item["candidate_id"]]
    if not candidate_alignments or any(row["decision"] != "new" or row["ku_id"] for row in candidate_alignments):
        raise SystemExit(f"unexpected S3/S4 state for {item['candidate_id']}: {candidate_alignments}")
    if item["ku_id"] in existing_manifest or f"04-knowledge/{item['ku_id']}.md" in existing_paths:
        raise SystemExit(f"manifest path already registered: {item['ku_id']}")
    if (ROOT / "04-knowledge" / f"{item['ku_id']}.md").exists():
        raise SystemExit(f"card already exists: {item['ku_id']}")

source_rows = list(csv.DictReader((TABLES / "sources.csv").open(encoding="utf-8-sig", newline="")))
if SOURCE_ID not in {row["source_id"] for row in source_rows}:
    raise SystemExit(f"missing source record {SOURCE_ID}")

manifest_additions = []
for item in ITEMS:
    manifest_additions.append({
        "ku_id": item["ku_id"],
        "type": item["type"],
        "canonical_name": item["canonical_name"],
        "name_en": item["name_en"],
        "source_task": "patrons-and-painters-full-book-s2",
        "card_path": f"04-knowledge/{item['ku_id']}.md",
    })

enrichments = [json.loads(line) for line in enrichment_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
next_enrichment = max(int(row["enrichment_id"].removeprefix("enr-")) for row in enrichments) + 1
addition_rows = []
for item in ITEMS:
    header = ["字段", "值", "证据"]
    section = "内容 / 基本信息"
    table_id = "tbl-" + stable_hash(f"{item['ku_id']}|{section}|1|{'|'.join(header)}")
    for row_index, (field, value, evidence) in enumerate(item["field_rows"], 1):
        enrichment_id = f"enr-{next_enrichment:05d}"
        next_enrichment += 1
        addition_rows.append({
            "enrichment_id": enrichment_id,
            "ku_id": item["ku_id"],
            "field": field,
            "value": value,
            "origin": "book",
            "source_id": SOURCE_ID,
            "source_ids": [SOURCE_ID],
            "source_ref": item["evidence"],
            "source_citations": [SOURCE_CITATION],
            "source_urls": [],
            "evidence": evidence,
            "evidence_status": "source_backed",
            "dispute": None,
            "accessed_date": "",
            "occurrence_id": "occ-ch10-p316-" + stable_hash(item["ku_id"] + "|" + field + "|" + value, 16),
            "table_id": table_id,
            "table_section": section,
            "has_header": True,
            "table_header": header,
            "row_index": row_index,
            "cells": [field, value, evidence],
            "unit_evidence_status": "source_backed",
        })

relation_drafts = []
work1 = "units/works/canaletto-view-grand-canal-campo-s-sofia-rialto"
work2 = "units/works/canaletto-view-campo-di-rialto-streit"
sofia = "units/places/campo-s-sofia-venice"
palazzo = "units/places/palazzo-foscari-venice"
campo_rialto = "units/places/campo-di-rialto-venice"
grand_canal = "units/places/grand-canal-venice"
rialto_area = "units/places/rialto-area-venice"
notes = "units/archives/sigismund-streit-notes-about-his-pictures"
zimmermann = "units/archives/zimmermann-streit-collection-article-1954"
constable = "units/archives/constable-four-paintings-grauen-kloster-1956"
streit = "units/persons/sigismund-streit"
canaletto = "units/persons/canaletto"
book_span = "Chapter 10, printed p.316, line 110; PDF physical p.49"

relation_drafts.extend([
    relation(work1, canaletto, "created_by", "formal", "Chapter 10, printed pp.315-316, lines 106 and 109-110; S2 st-chp10-p315-four-canalettos-two-scenes-linked-to-streits-life-fragment; st-chp10-p316-first-life-canaletto-view", "Haskell's source-reported attribution", "Haskell includes the scene among Streit's four Canalettos and identifies the first life-related view. Records the book's attribution only; not an external authorship verification.", "The p.316 note reports Constable rejected an attribution to Moretti or another follower; the cited essay was not consulted."),
    relation(work2, canaletto, "created_by", "formal", "Chapter 10, printed pp.315-316, lines 106 and 110; S2 st-chp10-p315-four-canalettos-two-scenes-linked-to-streits-life-fragment; st-chp10-p316-second-life-canaletto-view-at-campo-di-rialto", "Haskell's source-reported attribution", "The other view is the second of the two scenes Haskell identifies among Streit's four Canalettos. Records the book's attribution only; not an external authorship verification.", "The cited Constable essay was not consulted."),
    relation(work1, streit, "owned_by", "formal", "Chapter 10, printed pp.315-316, lines 106 and 109-110; S2 st-chp10-p315-four-canalettos-two-scenes-linked-to-streits-life-fragment; st-chp10-p316-first-life-canaletto-view", "Painting in Streit's collection", "The two life-related scenes are introduced as two of Streit's four Canalettos; p.316 describes the first scene. No acquisition date is inferred."),
    relation(work2, streit, "owned_by", "formal", "Chapter 10, printed pp.315-316, lines 106 and 110; S2 st-chp10-p315-four-canalettos-two-scenes-linked-to-streits-life-fragment; st-chp10-p316-second-life-canaletto-view-at-campo-di-rialto", "Painting in Streit's collection", "The second life-related scene is part of the four Canalettos Haskell attributes to Streit's collection. No acquisition date is inferred."),
    relation(work1, streit, "has_subject", "formal", book_span + "; S2 st-chp10-p316-streit-in-gondola-in-first-view", "Depicted person", "Haskell describes Streit standing in the foreground gondola; this records the depicted figure, not a historical event."),
    relation(work1, palazzo, "has_subject", "formal", book_span + "; S2 st-chp10-p316-streit-lived-in-palazzo-foscari", "Visible building", "Haskell says Palazzo Foscari is visible behind the gondola; the exact modern building identity is not asserted."),
    relation(work1, grand_canal, "has_subject", "formal", "Chapter 10, printed p.316, lines 109-110; S2 st-chp10-p316-first-life-canaletto-view", "Depicted waterway", "Haskell describes a sweep of the Grand Canal in the view."),
    relation(work1, rialto_area, "has_subject", "formal", "Chapter 10, printed p.316, lines 109-110; S2 st-chp10-p316-first-life-canaletto-view", "Panorama terminus", "The source describes the panorama as looking from Campo S. Sofia toward the broader Rialto locality, not toward the separate Campo di Rialto."),
    relation(work2, campo_rialto, "has_subject", "formal", book_span + "; S2 st-chp10-p316-second-life-canaletto-view-at-campo-di-rialto", "Depicted place", "Haskell says the other view was of Campo di Rialto; it is distinct from the broader Rialto-area candidate."),
    relation(notes, streit, "authored_by", "formal", "Chapter 10, printed p.315, line 106; printed p.316, line 109; S2 st-chp10-p315-four-canalettos-two-scenes-linked-to-streits-life-fragment; st-chp10-p316-two-life-scenes-noted-about-streits-pictures", "Writer of the notes", "Haskell says Streit made long notes about his pictures. The original notes, title, date, and repository were not independently consulted."),
    relation(BOOK_KU, zimmermann, "cites", "formal", "Chapter 10, printed p.316, note 1, line 294; Chapter 21, printed p.441; S2 st-chp10-p316-n01-streit-notes-published-by-zimmermann; st-chp21-bib-l1261-1299-entry-23", "Bibliographic citation", "Records Haskell's citation to the article and pages 197-224; does not assert that the article or cited pages were consulted."),
    relation(BOOK_KU, constable, "cites", "formal", "Chapter 10, printed p.316, note 1, line 294; Chapter 21, printed p.419; S2 st-chp10-p316-n01-constable-rejected-moretti-attribution; st-chp21-bib-l336-374-entry-26", "Bibliographic citation", "Records Haskell's citation to Constable's 1956 essay and pp.81-93; does not assert that the essay or cited pages were consulted."),
    relation(streit, palazzo, "located_at", "pending", book_span + "; S2 st-chp10-p316-streit-lived-in-palazzo-foscari", "Reported residence", "Haskell says Streit lived in the named palace; exact dates and modern building identity are not supplied.", "The controlled located_at predicate is marked needs_split and no faithful residence predicate is currently available."),
    relation(streit, campo_rialto, "located_at", "pending", book_span + "; S2 st-chp10-p316-second-life-canaletto-view-at-campo-di-rialto", "Reported business site", "Haskell says Streit's business activities were carried out at Campo di Rialto; the business and dates are unspecified.", "The controlled located_at predicate is marked needs_split and does not distinguish a business site from a person's physical location."),
])

new_manifest = manifest + manifest_additions
manifest_ids = {row["ku_id"] for row in new_manifest}
manifest_types = {row["ku_id"]: row["type"] for row in new_manifest}
relation_types = yaml.safe_load((ROOT / ".agents" / "skills" / "ingest" / "references" / "relation-types.yml").read_text(encoding="utf-8"))["types"]
domain_range = yaml.safe_load((ROOT / "01-domain" / "relation-domain-range.yml").read_text(encoding="utf-8"))["domain_range"]
if any(row["subject_ku_id"] not in manifest_ids or row["object_ku_id"] not in manifest_ids for row in relation_drafts):
    raise SystemExit("relation draft has an endpoint without a KU")
existing_keys = {natural_key(row) for row in relations}
for row in relation_drafts:
    if row["predicate"] not in relation_types:
        raise SystemExit(f"uncontrolled relation type: {row['predicate']}")
    if natural_key(row) in existing_keys:
        raise SystemExit(f"duplicate relation natural key: {natural_key(row)}")
    existing_keys.add(natural_key(row))
    constraint = domain_range.get(row["predicate"])
    if constraint and (
        manifest_types[row["subject_ku_id"]] not in constraint["domain"]
        or manifest_types[row["object_ku_id"]] not in constraint["range"]
    ):
        raise SystemExit(f"domain/range mismatch: {row['predicate']} {row['subject_ku_id']} -> {row['object_ku_id']}")
next_relation = max(int(row["relation_id"].removeprefix("rel-")) for row in relations) + 1
for offset, row in enumerate(relation_drafts):
    row["relation_id"] = f"rel-{next_relation + offset:04d}"

backlog_additions = [
    {"backlog_id": "bl-0086", "canonical_name": "Four Canaletto paintings in Streit’s collection as a collective group", "suggested_type": "", "status": "undecided", "source_id": SOURCE_ID, "source_ref": "chp-10:10_CHP-10_sec_ii:l95-106#L106", "statement_id": "st-chp10-p315-four-canalettos-two-scenes-linked-to-streits-life-fragment", "endpoint_role": "object", "candidate_id": "cand-9633", "ku_id": "", "decision_note": "The four source-mentioned paintings are a collective set, not an identified individual work or established KU type. Keep separate from the two individual views registered in this batch.", "process_ref": TASK_REF},
    {"backlog_id": "bl-0087", "canonical_name": "Two Canaletto scenes directly concerned with Streit’s life as a collective subset", "suggested_type": "", "status": "undecided", "source_id": SOURCE_ID, "source_ref": "chp-10:10_CHP-10_sec_ii:l95-106#L106; continuation l108-117#L109-110", "statement_id": "st-chp10-p315-four-canalettos-two-scenes-linked-to-streits-life-fragment", "endpoint_role": "object", "candidate_id": "cand-9634", "ku_id": "", "decision_note": "Two individual works are separately identified, but the collective subset has no independent type or single-work identity; do not merge it into either view.", "process_ref": TASK_REF},
    {"backlog_id": "bl-0088", "canonical_name": "H. Zimmermann, author identity unresolved", "suggested_type": "person", "status": "undecided", "source_id": SOURCE_ID, "source_ref": "chp-10:10_CHP-10_sec_ii:l273-349#L294; chp-21:21_CHP-21Bibliography:l1261-1299#L1297-1298", "statement_id": "st-chp10-p316-n01-streit-notes-published-by-zimmermann", "endpoint_role": "author", "candidate_id": "cand-9911", "ku_id": "", "decision_note": "The bibliographic entry gives only the initial H. Zimmermann; do not select among people with similar names or create a person KU without identity evidence.", "process_ref": TASK_REF},
    {"backlog_id": "bl-0089", "canonical_name": "W. G. Constable, author identity unresolved", "suggested_type": "person", "status": "undecided", "source_id": SOURCE_ID, "source_ref": "chp-10:10_CHP-10_sec_ii:l273-349#L294; chp-21:21_CHP-21Bibliography:l336-374#L371-372", "statement_id": "st-chp10-p316-n01-constable-rejected-moretti-attribution", "endpoint_role": "author", "candidate_id": "cand-9913", "ku_id": "", "decision_note": "The book supplies initials and surname only; cited essay identity is registered separately from the author's unresolved personal identity.", "process_ref": TASK_REF},
]
for row in backlog_additions:
    if any(old["backlog_id"] == row["backlog_id"] for old in backlog):
        raise SystemExit(f"backlog ID already exists: {row['backlog_id']}")

alignment_updates = []
for item in ITEMS:
    for row in [row for row in alignments if row["candidate_id"] == item["candidate_id"]]:
        row["ku_id"] = item["ku_id"]
        row["process_ref"] = TASK_REF
        row["resolution_note"] += f" S4 registration: {item['ku_id']}; source-local identity only, no external identity claim."
        alignment_updates.append(item["candidate_id"])

accepted_raw = accepted_path.read_text(encoding="utf-8")
if accepted_raw.count("claims:") != 1:
    raise SystemExit("accepted.yml claims section is not unique")
accepted_lines = [f"- 04-knowledge/{item['ku_id']}.md" for item in ITEMS]
accepted_additions = "".join(line + "\n" for line in accepted_lines)

cards = {ROOT / "04-knowledge" / f"{item['ku_id']}.md": make_card(item) for item in ITEMS}
if any(path.exists() for path in cards):
    raise SystemExit("a target card appeared after S4 preflight")

for item in ITEMS:
    mention_rows = list(csv.DictReader((TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="")))
    if item["candidate_id"] not in {row["candidate_id"] for row in mention_rows}:
        raise SystemExit(f"candidate has no current mention anchor: {item['candidate_id']}")

preview = {
    "mode": "apply" if args.apply else "dry-run",
    "S3_decisions_preserved": {item["candidate_id"]: "new" for item in ITEMS},
    "S4_mappings": {item["candidate_id"]: item["ku_id"] for item in ITEMS},
    "new_cards": [{"path": str(path.relative_to(ROOT)), "type": next(x["type"] for x in ITEMS if ROOT / "04-knowledge" / f"{x['ku_id']}.md" == path)} for path in cards],
    "S5_source_backed_fields": len(addition_rows),
    "S6_decisions": {"formal": sum(row["status"] == "formal" for row in relation_drafts), "pending": sum(row["status"] == "pending" for row in relation_drafts), "rejected_positive_attribution": "logged in process; no positive Moretti/follower edge"},
    "backlog_additions": [row["backlog_id"] for row in backlog_additions],
    "accepted_additions": accepted_lines,
}
print(json.dumps(preview, ensure_ascii=False, indent=2))
if not args.apply:
    print("Preview only; no files written. Re-run with --apply after reviewing this plan.")
    raise SystemExit(0)

for item in ITEMS:
    for row in [row for row in alignments if row["candidate_id"] == item["candidate_id"]]:
        row["ku_id"] = item["ku_id"]
for item in ITEMS:
    for row in [row for row in alignments if row["candidate_id"] == item["candidate_id"]]:
        row["process_ref"] = TASK_REF
        if "S4 registration:" not in row["resolution_note"]:
            row["resolution_note"] += f" S4 registration: {item['ku_id']}; source-local identity only, no external identity claim."

manifest.extend(manifest_additions)
relations.extend(relation_drafts)
backlog.extend(backlog_additions)
enrichments.extend(addition_rows)

accepted_text = accepted_raw.replace("claims:", accepted_additions + "claims:", 1)
write_csv_atomic(alignment_path, alignment_fields, alignments)
write_csv_atomic(manifest_path, manifest_fields, manifest)
write_csv_atomic(relations_path, relation_fields, relations)
write_csv_atomic(backlog_path, backlog_fields, backlog)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=enrichment_path.parent, delete=False, suffix=".tmp") as stream:
    for row in enrichments:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    temp_path = Path(stream.name)
temp_path.replace(enrichment_path)
accepted_path.write_text(accepted_text, encoding="utf-8", newline="\n")
for path, card_text in cards.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(card_text, encoding="utf-8", newline="\n")
print("Applied S4/S5/S6 tables, accepted registry entries, and 10 source-backed endpoint cards.")
