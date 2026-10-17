from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = f"S3-S4-full-book-2026-10-17"
CARD_PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#s4-person-endpoints-20261017"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."

# Candidate-level S3 corrections: the original new group and its rationale remain
# in resolution_note as history; each target is a same-type accepted KU.
REUSES = [
    ("cand-0114", "units/institutions/arcadia", "The index society is the same Arcadia literary academy already represented by this institution KU."),
    ("cand-6127", "units/institutions/schildersbent", "The Roman painters' society named Schildersbent is the same organization; the separate Bentvueghels comparison remains separate."),
    ("cand-9423", "units/persons/francis-haskell", "The p.290 note names the author Francis Haskell; the title and copyright pages identify that same author as Francis James Herbert Haskell. The cited 1967 work remains unresolved."),
    ("cand-2822", "units/places/residenz-wurzburg", "The Würzburg Residenz place candidate denotes the same palace represented by the existing Residenz, Würzburg KU."),
    ("cand-4623", "units/places/berlin", "Berlin is the same city already represented by the existing place KU; this does not resolve which of two paintings is paired with it."),
    ("cand-4957", "units/places/palazzo-barberini", "Palazzo Barberini is the same named building; this mapping does not expand the source's tapestry-cartoon custody statement."),
    ("cand-5120", "units/places/spain", "Spain is the same geographic place; the political entity and geographic place remain distinct by type."),
    ("cand-5667", "units/places/spain", "Spain is the same geographic place named in the report; the reported event remains unverified."),
    ("cand-5696", "units/places/st-peters-basilica", "St Peter's Basilica is the same named building; the excavation context does not add an institutional identity."),
    ("cand-6232", "units/places/tuscany", "Tuscany is the same geographic region named in Rosa's letter."),
    ("cand-7200", "units/places/england", "England is the same geographic place named in Haskell's patronage comparison."),
    ("cand-7287", "units/places/versailles", "Versailles is the same place already represented by the existing place KU; the official style remains a distinct term."),
    ("cand-7473", "units/places/new-york", "New York is the same city named as the reported Metropolitan Museum location."),
    ("cand-9904", "units/places/venice", "Venice in the p.313 note is the same city as the existing place KU; the prior S3-deferred wording is superseded."),
    ("cand-10171", "units/places/tuscany", "Tuscany in Pasquali's quoted letter is the same region as the existing place KU; the prior S3-deferred wording is superseded."),
    ("cand-10318", "units/places/ca-rezzonico", "Cà Rezzonico is the same named place as the existing KU; the source's pairing of two titles with two locations remains unspecified."),
    ("cand-9114", "units/terms/bamboccianti", "Bamboccianti is the same art-historical group/style term already represented by the accepted term KU."),
    ("cand-4477", "units/works/pietro-da-cortona-rape-of-the-sabines", "The large Sacchetti canvas named by Haskell is the same Pietro da Cortona work as the existing plate-10a work KU; no additional version is implied."),
    ("cand-5991", "units/works/claude-view-of-delphi-with-a-procession", "The Claude Lorrain painting named in the source and identified as plate 19b is the same work as the existing KU."),
    ("cand-6026", "units/works/caravaggio-death-virgin", "The Caravaggio painting shown in 1607 is the same named work as the existing Death of the Virgin KU; the source-local display claim is not expanded."),
]

PERSON_TARGETS = [
    {
        "candidate": "cand-2512",
        "group": "new-person:cristoforo-storer-61583f1ac4",
        "ku": "units/persons/cristoforo-storer",
        "name_zh": "克里斯托福罗·斯托雷尔",
        "name_en": "Cristoforo Storer",
        "index_entry": "S.csv#201",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/S.csv",
        "body_source": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "sources": [
            {
                "location": "第8章；印刷页216；OCR L23–25",
                "summary": "Haskell称委员会最初选择 Swiss artist Cristoforo Storer，提及其师承及与贝加莫显要家族的密切联系，并记1654年委托他绘制《The Levites》。这些均为书内叙述。",
                "span": "lines 23–25; print p. 216",
                "quotes": [
                    ("lines 23–24", "Their first choice fell on a Swiss artist, Cristoforo Storer, a pupil of the Milanese\nErcole Proccaccini, who had already had close contacts with leading families in Bergamo."),
                    ("line 25", "In February 1654 he was commissioned to paint one of the thirteen pictures to be embedded in the stucco of the vault and lunettes above the cornice of the southern transept. The subject given was The Levites"),
                ],
            }
        ],
        "index_quote": "Storer, Cristoforo",
        "index_location": "全书索引 S.csv#201",
        "index_summary": "索引以 Storer, Cristoforo 列出人物主项。",
        "index_span": "S.csv#201",
        "description_zh": "Haskell称 Cristoforo Storer 是委员会最初选择的画家，并以“Swiss artist”称呼他，记其师从 Ercole Proccaccini、曾与贝加莫显要家族密切接触，且于1654年2月受委托绘制《The Levites》。这里仅记录书内识别和叙述；“Swiss artist”保留原文表述，不另推出生地或国籍。中文名为项目工作音译。",
        "description_en": "Haskell identifies Cristoforo Storer as the artist first chosen by the committee, calls him a “Swiss artist,” notes his pupilage under Ercole Proccaccini and close contacts with leading Bergamo families, and says he was commissioned in February 1654 to paint The Levites. This record is limited to the book's identification and account; “Swiss artist” is retained as the source's wording and is not expanded into a birthplace or nationality claim. The Chinese name is a project working transliteration.",
        "location": "第8章，印刷页216；OCR L23–25",
        "relation_ids": [
            "st-chp8-p216-storer-the-levites-commission",
            "st-chp8-p216-storer-first-choice",
            "st-chp8-p216-storer-pupil-proccaccini",
            "st-chp8-p216-storer-close-contacts-bergamo-families",
            "st-chp8-p216-storer-described-as-swiss",
            "st-chp8-p216-storer-delay-led-fresco-alternative",
        ],
        "source_fragments": ["Their first choice fell on a Swiss artist, Cristoforo Storer", "The subject given was The Levites"],
    },
    {
        "candidate": "cand-0911",
        "group": "new-person:david-ludovico-7f9314f137",
        "ku": "units/persons/ludovico-david",
        "name_zh": "卢多维科·达维德",
        "name_en": "Ludovico David",
        "index_entry": "D.csv#13",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/D.csv",
        "body_source": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "sources": [
            {
                "location": "第8章；印刷页220；OCR L106",
                "summary": "Haskell称在罗马的 Swiss painter Ludovico David 从同事处听说贝加莫所需的14幅画，并提出在两年半内绘制全部画作或参与分担项目。原文记为提议，不代表委员会接受。",
                "span": "line 106; print p. 220",
                "quotes": [
                    ("line 106", "In Rome meanwhile the Swiss painter Ludovico David heard ‘from a colleague and friend of mine’ about the fourteen pictures that were needed."),
                    ("line 106", "offered to paint all the pictures within two and a half years at a price of 3500 scudi—or alternatively to take a share of the scheme at a price to be agreed with other artists."),
                ],
            }
        ],
        "index_quote": "David, Ludovico",
        "index_location": "全书索引 D.csv#13；p.220",
        "index_summary": "索引以 David, Ludovico 列出人物及第220页定位。",
        "index_span": "D.csv#13",
        "description_zh": "Haskell称 Ludovico David 当时身在罗马，是一位“Swiss painter”；他从一位同事处听说贝加莫教堂所需的14幅画，并提出独自承担全部画作或与其他画家分担。原文记录的是 David 的提议，委员会没有采用其方案。中文名为项目工作音译；来源措辞不另行证明出生地或国籍。",
        "description_en": "Haskell describes Ludovico David as a “Swiss painter” then in Rome. After hearing from a colleague about the fourteen pictures needed for the Bergamo church, David offered either to paint them all or to share the scheme with other artists. The source records David's proposal, which the committee did not adopt. The Chinese name is a project working transliteration; the source wording does not independently establish birthplace or nationality.",
        "location": "第8章，印刷页220；OCR L106",
        "relation_ids": [
            "st-chp8-p220-david-competitive-scheme",
            "st-chp8-p220-david-guild-review",
            "st-chp8-p220-david-hears-about-project-from-colleague",
            "st-chp8-p220-david-offers-all-pictures",
            "st-chp8-p220-david-offers-share-with-artists",
            "st-chp8-p220-david-rejects-committee-terms",
        ],
        "source_fragments": ["the Swiss painter Ludovico David", "offered to paint all the pictures within two and a half years"],
    },
    {
        "candidate": "cand-1365",
        "group": "new-person:de-lattre-pierre-22a7f370a1",
        "ku": "units/persons/pierre-de-lattre",
        "name_zh": "皮埃尔·德·拉特尔",
        "name_en": "Pierre de Lattre",
        "index_entry": "L.csv#22",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/L.csv",
        "body_source": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
        "sources": [
            {
                "location": "第3章；印刷页74；OCR L121–122",
                "summary": "Haskell称 Pierre de Lattre 是来自 St Omer 的年轻法国人、耶稣会士，并记他于1626年进入 S. Andrea 初学院、两年后进入 Collegio Romano，留至1683年去世。保留原书转录形式。",
                "span": "lines 121–122; print p. 74",
                "quotes": [
                    ("line 121", "In this instance the artist was a young Frenchman, Pierre de Lattre, from St Omer who had entered the novitiate of S. Andrea in 1626."),
                    ("line 122", "Two years later he went to the Coliegio Romano, where he remained until his death in 1683."),
                ],
            }
        ],
        "index_quote": "Lattre, Pierre de",
        "index_location": "全书索引 L.csv#22；p.74",
        "index_summary": "索引以 Lattre, Pierre de 列出人物及第74页定位。",
        "index_span": "L.csv#22",
        "description_zh": "Haskell称 Pierre de Lattre 是来自 St Omer 的年轻法国人，也是耶稣会成员；他于1626年进入 S. Andrea 初学院，两年后前往 Collegio Romano，并在那里留至1683年去世。第二句按来源 OCR 转录为“Coliegio Romano”，本卡不将其表述为扫描页校勘。中文名为项目工作音译。",
        "description_en": "Haskell calls Pierre de Lattre a young Frenchman from St Omer and a member of the Society of Jesus. The book says that he entered the novitiate of S. Andrea in 1626, went to the Collegio Romano two years later, and remained there until his death in 1683. The OCR transcription “Coliegio Romano” is retained as transcribed and is not presented as a verified reading of the printed page. The Chinese name is a project working transliteration.",
        "location": "第3章，印刷页74；OCR L121–122",
        "relation_ids": [
            "st-chp3-secii-l115-123-account-record",
            "st-chp3-secii-l115-123-decoration-assigned",
            "st-chp3-secii-l115-123-lattre-collegio",
            "st-chp3-secii-l115-123-lattre-life",
            "st-chp3-secii-l115-123-lattre-works",
            "st-chp3-secii-l115-123-obituary",
        ],
        "source_fragments": ["Pierre de Lattre, from St Omer", "entered the novitiate of S. Andrea in 1626", "remained until his death in 1683"],
    },
    {
        "candidate": "cand-1636",
        "group": "new-person:melanconici-niccolo-ef1abca9c3",
        "ku": "units/persons/niccolo-melanconici",
        "name_zh": "尼科洛·梅兰科尼奇",
        "name_en": "Niccolò Melanconici",
        "index_entry": "M.csv#176",
        "index_file": "02-sources/03-Index/03-2-Index-CSV/M.csv",
        "body_source": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "sources": [
            {
                "location": "第8章；印刷页220；OCR L110",
                "summary": "Haskell称 Niccolò Melanconici 是 Luca Giordano 的学生，同意自费绘制《Abraham》作为试验。",
                "span": "line 110; print p. 220",
                "quotes": [("line 110", "To Naples, in fact—where a pupil of Luca Giordano, Niccolò Melanconici agreed to paint an Abraham at his own expense as an experiment.")],
            },
            {
                "location": "第8章；印刷页221；OCR L113",
                "summary": "Haskell称该试验获认可后，Melanconici 获得整项委托，费用为4,000 ducats（含旅行、食宿），并于1693年6月抵达贝加莫。",
                "span": "line 113; print p. 221",
                "quotes": [("line 113", "It was arranged that Melanconici should be given the entire commission for a fee of 4000 ducats, which was to include all his expenses for travel and for board and lodging."), ("line 113", "in June 1693 the artist himself arrived in Bergamo to undertake the frescoes.")],
            },
        ],
        "index_quote": "Melanconici, Niccolò",
        "index_location": "全书索引 M.csv#176；pp.220–221",
        "index_summary": "索引以 Melanconici, Niccolò 列出人物及第220–221页定位。",
        "index_span": "M.csv#176",
        "description_zh": "Haskell称 Niccolò Melanconici 是 Luca Giordano 的学生；他同意自费绘制《Abraham》作为试验。书中称该画获认可后，Melanconici 获得整项贝加莫教堂绘画委托，费用为4,000 ducats（含旅行与食宿），并于1693年6月抵达贝加莫。中文名为项目工作音译。",
        "description_en": "Haskell identifies Niccolò Melanconici as a pupil of Luca Giordano who agreed to paint an Abraham at his own expense as an experiment. After the painting met with approval, the book says Melanconici was given the entire Bergamo church commission for 4,000 ducats, including travel, board, and lodging, and arrived in Bergamo in June 1693. The Chinese name is a project working transliteration.",
        "location": "第8章，印刷页220–221；OCR L110、113",
        "relation_ids": [
            "st-chp8-p220-melanconici-pupil-of-giordano",
            "st-chp8-p220-melanconici-agrees-abraham-experiment",
            "st-chp8-p221-melanconici-entire-commission",
            "st-chp8-p221-melanconici-arrives-for-frescoes",
            "st-chp8-p221-melanconici-additional-pictures",
            "st-chp8-p221-melanconici-signature-permitted",
        ],
        "source_fragments": ["a pupil of Luca Giordano, Niccolò Melanconici", "the entire commission for a fee of 4000 ducats", "in June 1693 the artist himself arrived in Bergamo"],
    },
]


def text_bytes(path: Path, text: str) -> bytes:
    old = path.read_bytes() if path.exists() else b""
    bom = b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b""
    return bom + text.encode("utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def make_source(target: dict, item: dict) -> dict:
    return {
        "citation": BOOK_CITATION,
        "location": item["location"],
        "sentence_summary": item["summary"],
        "original_quotes": [
            {"source_span": span, "text": quote} for span, quote in item["quotes"]
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": target["body_source"],
            "source_span": item["span"],
        },
    }


def make_card(target: dict) -> str:
    sources = [make_source(target, item) for item in target["sources"]]
    sources.append({
        "citation": INDEX_CITATION,
        "location": target["index_location"],
        "sentence_summary": target["index_summary"],
        "original_quotes": [{"source_span": target["index_span"], "text": target["index_quote"]}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": target["index_file"],
            "source_span": target["index_span"],
        },
    })
    frontmatter = {
        "title": f"{target['name_zh']}（{target['name_en']}）",
        "name_en": target["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": CARD_PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    relation_ids = ", ".join(target["relation_ids"])
    body = f"""## 内容

### 描述

**中文：** {target['description_zh']}〔[{target['location']}](../../../{target['body_source']})〕

**English:** {target['description_en']} ([{target['location']}](../../../{target['body_source']}))

## 关系与证据

### 关系记录

目前没有登记在 `relations.csv` 中的正式关系。直接 S2 关系候选共 6 条（{relation_ids}），保留待 S6 审查；本卡登记不等于关系裁决。"""
    return f"---\n{fm}---\n\n{body}\n"


def insert_accepted(lines: list[str], card_rel: str) -> list[str]:
    entry = f"- {card_rel}"
    assert entry not in lines, f"accepted.yml already includes {entry}"
    units_index = lines.index("units:")
    claims_index = next((i for i in range(units_index + 1, len(lines)) if re.fullmatch(r"[A-Za-z0-9_-]+:", lines[i])), len(lines))
    unit_entries = [line for line in lines[units_index + 1:claims_index] if line.startswith("- ")]
    insert_index = claims_index
    for i in range(units_index + 1, claims_index):
        if lines[i].startswith("- ") and lines[i][2:] > card_rel:
            insert_index = i
            break
    lines.insert(insert_index, entry)
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve reviewed same-type S3 reuse and register four direct person endpoints in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment_rows = sync.read_csv(ALIGNMENT_PATH)
    candidate_fields, candidate_rows = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest_rows = sync.read_csv(MANIFEST_PATH)
    alignment_by_candidate = {row["candidate_id"]: row for row in alignment_rows if row.get("candidate_id") and not row.get("external_source")}
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    manifest_by_id = {row["ku_id"]: row for row in manifest_rows}
    accepted_lines = read_text(ACCEPTED_PATH).splitlines()
    statement_lines = STATEMENTS_PATH.read_bytes().splitlines(keepends=True)
    statements = {}
    statement_line_index = {}
    for i, raw in enumerate(statement_lines):
        data = json.loads(raw.decode("utf-8-sig"))
        statements[data["statement_id"]] = data
        statement_line_index[data["statement_id"]] = i

    new_alignment = [dict(row) for row in alignment_rows]
    new_by_candidate = {row["candidate_id"]: row for row in new_alignment if row.get("candidate_id") and not row.get("external_source")}
    new_manifest = [dict(row) for row in manifest_rows]
    new_manifest_by_id = {row["ku_id"]: row for row in new_manifest}
    new_candidate_rows = [dict(row) for row in candidate_rows]
    new_candidate_by_id = {row["candidate_id"]: row for row in new_candidate_rows}
    planned_cards: dict[Path, str] = {}

    for candidate_id, target_ku, rationale in REUSES:
        assert candidate_id in candidate_by_id and candidate_id in new_by_candidate
        c = candidate_by_id[candidate_id]
        a = new_by_candidate[candidate_id]
        assert a["decision"] == "new" and not a.get("ku_id"), f"reuse candidate is not pending new: {candidate_id}"
        group = sync.get_group(a.get("resolution_note", ""))
        members = [row["candidate_id"] for row in alignment_rows if row.get("candidate_id") and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == group]
        assert members == [candidate_id], f"reviewed reuse group changed: {candidate_id}: {members}"
        assert target_ku in manifest_by_id and target_ku in new_manifest_by_id
        target = manifest_by_id[target_ku]
        kind = c.get("suggested_type") or "unclassified"
        assert target["type"] == kind, f"type mismatch for {candidate_id}: {kind} -> {target['type']}"
        assert (ROOT / target["card_path"]).is_file(), f"target card missing: {target['card_path']}"
        a["decision"] = "same"
        a["ku_id"] = target_ku
        a["process_ref"] = PROCESS_REF
        a["resolution_note"] = (a.get("resolution_note", "").rstrip() +
            f" S3/S4 correction ({DATE}): same -> {target_ku}; {rationale} Original S3 new group and rationale are retained above as history.")

    for cid, suffix in {
        "cand-9904": "S3/S4 correction (2026-10-17): identity aligns to the existing Venice place KU units/places/venice; see current alignment decision and S3-S4-full-book-2026-10-17.",
        "cand-10171": "S3/S4 correction (2026-10-17): identity aligns to the existing Tuscany place KU units/places/tuscany; see current alignment decision and S3-S4-full-book-2026-10-17.",
    }.items():
        detail = new_candidate_by_id[cid].get("detail", "")
        assert "deferred to S3" in detail or "deferred to s3" in detail.lower(), f"expected stale detail missing for {cid}"
        new_candidate_by_id[cid]["detail"] = detail.rstrip() + " " + suffix

    relation_candidate_statement_ids = set()
    for target in PERSON_TARGETS:
        cid, group, ku_id = target["candidate"], target["group"], target["ku"]
        assert cid in candidate_by_id and cid in new_by_candidate
        c = candidate_by_id[cid]
        a = new_by_candidate[cid]
        assert c["suggested_type"] == "person"
        assert a["decision"] == "new" and not a.get("ku_id")
        assert sync.get_group(a.get("resolution_note", "")) == group
        members = [row["candidate_id"] for row in alignment_rows if row.get("candidate_id") and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == group]
        assert members == [cid], f"person group changed: {group}: {members}"
        assert ku_id not in manifest_by_id
        card_rel = f"04-knowledge/{ku_id}.md"
        card_path = ROOT / card_rel
        assert not card_path.exists(), f"card already exists: {card_rel}"
        assert not any(line == f"- {card_rel}" for line in accepted_lines)
        body_source_path = ROOT / target["body_source"]
        body_text = body_source_path.read_text(encoding="utf-8-sig")
        for fragment in target["source_fragments"]:
            assert fragment in body_text, f"source quote fragment not found for {cid}: {fragment}"
        index_path = ROOT / target["index_file"]
        assert index_path.is_file()
        assert target["index_entry"].split("#", 1)[0] == index_path.name
        assert target["index_quote"] in index_path.read_text(encoding="utf-8-sig"), f"index quote not found for {cid}: {target['index_entry']}"
        card_text = make_card(target)
        assert "**中文：**" in card_text and "**English:**" in card_text and "## 关系与证据" in card_text
        planned_cards[card_path] = card_text
        a["ku_id"] = ku_id
        a["process_ref"] = PROCESS_REF
        a["resolution_note"] = a.get("resolution_note", "").rstrip() + f" S4 registration ({DATE}): mapped {group} to {ku_id}; card records source-bounded identity and bilingual working name; relation candidates remain pending S6."
        new_manifest.append({
            "ku_id": ku_id,
            "type": "person",
            "canonical_name": f"{target['name_zh']}（{target['name_en']}）",
            "name_en": target["name_en"],
            "source_task": TASK,
            "card_path": card_rel,
        })
        new_manifest_by_id[ku_id] = new_manifest[-1]
        for statement_id in target["relation_ids"]:
            assert statement_id in statements, f"relation candidate statement missing: {statement_id}"
            statement = statements[statement_id]
            assert statement.get("qualifiers", {}).get("relation_candidate") is True
            assert cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id"))
            relation_candidate_statement_ids.add(statement_id)

    assert len(planned_cards) == 4
    assert len(relation_candidate_statement_ids) == 24
    assert all(len(t["relation_ids"]) == 6 for t in PERSON_TARGETS)

    # Luigi's endpoint was registered in the previous batch. Repair the stale S2
    # endpoint note while keeping the relation candidate itself pending S6.
    luigi_statement_id = "st-chp9-p269-n05"
    luigi = statements[luigi_statement_id]
    assert luigi.get("subject_candidate_id") is None
    assert luigi.get("object_candidate_id") == "cand-8789"
    luigi["subject_candidate_id"] = "cand-12425"
    q = luigi["qualifiers"]
    q["mentioned_candidate_ids"] = list(dict.fromkeys([*(q.get("mentioned_candidate_ids") or []), "cand-12425"]))
    q["qualification"] = (
        "Keep distinct from the 1762 pamphlet cited at p.272 note 1; neither pamphlet was independently consulted. "
        "The named publisher endpoint now maps to cand-12425 / units/persons/luigi-pavini; the source's bibliographic claim is unchanged, and the formal relation remains pending S6."
    )
    q["open_endpoint_reason"] = (
        "The named publisher Luigi Pavini is mapped to candidate cand-12425 and KU units/persons/luigi-pavini. "
        "The statement remains a relation candidate for S6 review; the separately cited Ferrari locator is not the publisher."
    )
    q["relation_candidate_note"] = (
        "The object is the identified 1734 pamphlet. The source-named publisher endpoint is cand-12425 / units/persons/luigi-pavini; "
        "the separately cited Ferrari locator is not the publisher. Keep the formal citation/publication relation pending S6 review."
    )
    luigi_bytes = json.dumps(luigi, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    old_luigi_line = statement_lines[statement_line_index[luigi_statement_id]]
    line_ending = b"\r\n" if old_luigi_line.endswith(b"\r\n") else (b"\n" if old_luigi_line.endswith(b"\n") else b"")
    statement_lines[statement_line_index[luigi_statement_id]] = luigi_bytes + line_ending

    luigi_card_path = ROOT / "04-knowledge/units/persons/luigi-pavini.md"
    luigi_card = read_text(luigi_card_path)
    assert "st-chp9-p269-n05" not in luigi_card
    assert "## 关系与证据" not in luigi_card
    assert "knowledge.md#s4-luigi-pavini" in luigi_card
    luigi_card += "\n## 关系与证据\n\n### 关系记录\n\n目前没有登记在 `relations.csv` 中的正式关系。出版者端点已映射至小册子对象候选；关系候选 `st-chp9-p269-n05` 保留待 S6 审查。\n"

    # The original process_ref already names this anchor; ensure it resolves.
    process_text = read_text(PROCESS_PATH)
    if '<a id="s4-luigi-pavini"></a>' not in process_text:
        marker = "### 首批：Luigi Pavini"
        assert marker in process_text
        process_text = process_text.replace(marker, '<a id="s4-luigi-pavini"></a>\n\n' + marker, 1)
    process_anchor = '<a id="s4-person-endpoints-20261017"></a>'
    assert process_anchor not in process_text
    process_section = [
        process_anchor,
        "",
        f"### S3 复用修正与 S4 person：四个直接关系端点登记（{DATE}）",
        "",
        "#### S3 same 复用修正",
        "",
        "下列20个单成员候选组经同类型既有 KU 及书内对象语境复核，由 `new` 更正为 `same`。原 `group=`、S3 理由及历史状态保留在各 alignment 行；本次写入既有 KU 映射，不重复建卡。",
        "",
    ]
    for candidate_id, target_ku, rationale in REUSES:
        process_section.append(f"- `{candidate_id}` → `{target_ku}`：{rationale}")
    process_section += [
        "",
        "`cand-9904` 与 `cand-10171` 的候选 detail 中“S3 deferred”措辞已追加当前复用去向；原说明保留。未改变其余 `conflict`、`undecided` 或 `excluded` 决定。",
        "",
        "#### S4 person 新登记",
        "",
        "四个 source-local person 组各登记一张 KU。姓名中文形式均为项目工作音译；卡片限于 Haskell 书内原文及索引，不补传记或外部身份事实。每组均有6条直接 S2 关系候选，卡片列明 statement ID；本批没有写入 `relations.csv`，所有关系仍待 S6。",
        "",
        "| 候选／身份组 | KU | 书内锚点 | S2 关系候选 |",
        "|---|---|---|---:|",
    ]
    for target in PERSON_TARGETS:
        process_section.append(
            f"| `{target['candidate']}` / `{target['group']}` | `{target['ku']}` | {target['location']} 与索引 {target['index_entry']} | {len(target['relation_ids'])} |"
        )
    process_section += [
        "",
        "四张卡包含双语规范标题与等义描述、书内来源摘录、精确行和印刷页，以及关系与证据段。Storer 的“Swiss artist”与 David 的“Swiss painter”仅作为 Haskell 原文称谓，不推定出生地或国籍；de Lattre 的 OCR “Coliegio”保留转录状态。",
        "",
        "#### Luigi Pavini 端点引用修正",
        "",
        "`st-chp9-p269-n05` 的 `subject_candidate_id` 现映射至 `cand-12425`，并将其纳入 `mentioned_candidate_ids`。原书中 Luigi Pavini 为小册子出版者的书目信息不变；旧的“无候选”说明从当前 statement 语义中移除，历史过程仍保留在本文件前文与 backlog 记录。该 statement 仍是 S2 关系候选，正式边待 S6；Luigi 卡片的 `process_ref` 锚点现已在本文件落位，并补上待审关系入口。backlog `bl-0001` 继续保持 completed。",
        "",
    ]
    process_text += "\n" + "\n".join(process_section)

    new_manifest.sort(key=lambda row: row["ku_id"])
    stats = sync.summarize_by_type(new_candidate_rows, new_alignment)
    type_table, totals = sync.build_type_table(stats)
    result_text = sync.update_result(read_text(RESULT_PATH), stats, totals, len(new_manifest))
    # The current S4 result section is refreshed by update_result; this batch note
    # is appended as the latest auditable record.
    reuse_by_type = defaultdict(int)
    for cid, _, _ in REUSES:
        kind = candidate_by_id[cid].get("suggested_type") or "unclassified"
        reuse_by_type[kind] += 1
    result_section = [
        "",
        f"### S3 复用修正与 S4 person：四个直接关系端点登记（{DATE}）",
        "",
        "20个单成员 `new` 候选组经同类型既有 KU 复核后改为 `same`；保留其 S3 历史理由并指向既有记录。复用分布：institution 2、person 1、place 13、term 1、work 3。四个单成员 person `new` 组另各登记一张 KU：",
        "",
    ]
    for target in PERSON_TARGETS:
        result_section.append(f"- `{target['candidate']}` → [{target['name_zh']}（{target['name_en']}）](../units/{target['ku']}.md)：{target['location']}；6条直接关系候选待 S6。")
    result_section += [
        "",
        "Luigi Pavini 已登记人物端点与 `st-chp9-p269-n05` 当前 statement 的映射已接通；该关系未提前转为正式边。以上批次不改变其他 conflict／undecided 对象。",
        "",
    ]
    result_text += "\n" + "\n".join(result_section)

    assert len(new_manifest) == len(manifest_rows) + 4
    assert sum(1 for row in new_alignment if row["candidate_id"] in [c for c, _, _ in REUSES] and row["decision"] == "same") == len(REUSES)
    assert all(new_by_candidate[t["candidate"]]["ku_id"] == t["ku"] for t in PERSON_TARGETS)
    assert totals["pending_groups"] + totals["registered_groups"] == totals["new_groups"]
    assert len([row for row in new_alignment if row.get("decision") == "new" and not row.get("ku_id")]) == totals["pending_members"] + 15
    assert "S4 已登记" in result_text and "S4 新组" in result_text

    planned_accepted = list(accepted_lines)
    for target in PERSON_TARGETS:
        planned_accepted = insert_accepted(planned_accepted, f"04-knowledge/{target['ku']}.md")
    assert len([line for line in planned_accepted if line.startswith("- 04-knowledge/")]) == len([line for line in accepted_lines if line.startswith("- 04-knowledge/")]) + 4

    if args.dry_run:
        print(f"DRY-RUN OK: same reuses={len(REUSES)}; new person groups={len(PERSON_TARGETS)}; cards={len(planned_cards)}; person relation candidates={len(relation_candidate_statement_ids)}")
        print(f"manifest: {len(manifest_rows):,}->{len(new_manifest):,}; registered new groups={totals['registered_groups']:,}; pending new groups={totals['pending_groups']:,}; pending candidate mappings={totals['pending_members']:,}")
        print(f"Luigi statement: subject_candidate_id={luigi['subject_candidate_id']}; backlog stays completed; formal relation pending S6")
        for target in PERSON_TARGETS:
            print(f"{target['candidate']} {target['group']} -> {target['ku']}")
        return

    # Write only after every identity, type, source quote, path, and statement check passed.
    for card_path, card_text in planned_cards.items():
        card_path.write_bytes(card_text.encode("utf-8"))
    luigi_card_path.write_bytes(text_bytes(luigi_card_path, luigi_card))
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, new_alignment)
    sync.write_csv(ENTITY_PATH, candidate_fields, new_candidate_rows)
    sync.write_csv(MANIFEST_PATH, manifest_fields, new_manifest)
    accepted_text = "\n".join(planned_accepted) + "\n"
    ACCEPTED_PATH.write_bytes(text_bytes(ACCEPTED_PATH, accepted_text))
    STATEMENTS_PATH.write_bytes(b"".join(statement_lines))
    PROCESS_PATH.write_bytes(text_bytes(PROCESS_PATH, process_text))
    RESULT_PATH.write_bytes(text_bytes(RESULT_PATH, result_text))
    print(f"APPLIED: same reuses={len(REUSES)}; new person KUs={len(PERSON_TARGETS)}; manifest={len(new_manifest):,}; pending groups={totals['pending_groups']:,}; pending candidate mappings={totals['pending_members']:,}")


if __name__ == "__main__":
    main()
