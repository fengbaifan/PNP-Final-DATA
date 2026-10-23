from __future__ import annotations

import argparse
import csv
import difflib
import io
import json
import os
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.build_field_facts import assign_ids, extract_records  # noqa: E402

TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
SOURCE_ID = "haskell-1980-rev-ed"
SRC4 = "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
SRC6 = "02-sources/02-Markdown/06_CHP-6_intro.md"
SRC7 = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
ANCHOR = "s4-s5-s6-ch7-p176-poussin-letter-20261023"
PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#" + ANCHOR
)
CANDIDATE = "cand-6707"
ALIGNMENT = "aln-6884"
GROUP = "archive-group-d09186f7edd3"
KU = "units/archives/poussin-letter-to-jean-lemaire-early-1639"
CARD = "04-knowledge/units/archives/poussin-letter-to-jean-lemaire-early-1639.md"
POUSSIN = "units/persons/nicolas-poussin"
LEMAIRE = "units/persons/jean-lemaire"
HASKELL = "units/archives/patrons-and-painters"
EDITION = "units/archives/poussin-correspondance-jouanny-1911"
CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def read_csv(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader.fieldnames or []), list(reader), bom, newline


def render_csv(fields, rows, bom, newline):
    handle = io.StringIO(newline="")
    output = csv.DictWriter(handle, fieldnames=fields, lineterminator=newline)
    output.writeheader()
    output.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + handle.getvalue().encode("utf-8")


def render_jsonl(rows):
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")


def atomic_write(path: Path, payload: bytes):
    temp = path.with_name(path.name + ".codex-tmp")
    temp.write_bytes(payload)
    os.replace(temp, path)


def replace_once(text, old, new, label):
    if text.count(old) != 1:
        raise ValueError(f"{label}: expected exactly one matching block")
    return text.replace(old, new, 1)


def accepted_with(card_path):
    path = ROOT / "04-knowledge" / "accepted.yml"
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "units:":
        raise ValueError("accepted.yml does not begin with units:")
    existing = {line.strip()[2:].strip() for line in lines if line.lstrip().startswith("-")}
    if card_path in existing:
        raise ValueError(f"accepted.yml already contains {card_path}")
    insert_at = next(
        (i for i, line in enumerate(lines) if line.lstrip().startswith("-") and line.strip()[2:].strip() > card_path),
        next((i for i, line in enumerate(lines) if line.strip() == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {card_path}{newline}")
    return (b"\xef\xbb\xbf" if bom else b"") + "".join(lines).encode("utf-8")


def group_id(row):
    match = re.search(r"(?:^|;\s*)group=([^;]+)", row.get("resolution_note", ""))
    return match.group(1) if match else row["candidate_id"]


def card_text():
    return f'''---
title: "普桑致让·勒梅尔的书信（Letter from Nicolas Poussin to Jean Lemaire, reported for early 1639）"
name_en: "Letter from Nicolas Poussin to Jean Lemaire, reported for early 1639"
type: archive
sub_type: "individual letter reported by Haskell; original and cited edition not consulted"
evidence_status: source_backed
sources:
  - citation: "{CITATION}"
    location: "Chapter 7, printed p. 176, line 81; PDF physical p. 10"
    sentence_summary: "Haskell reports that Poussin wrote to Jean Lemaire in early 1639 and was worried by French recruitment developments."
    original_quotes:
      - source_span: "Chapter 7, printed p. 176, line 81; PDF physical p. 10"
        text: "Early in 1639 Poussin wrote to his friend Jean Lemaire that he was worried by these developments."
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: {SRC7}
      source_span: "line 81; printed p. 176; PDF physical p. 10"
  - citation: "{CITATION}"
    location: "Chapter 7, printed p. 176, footnote 2, line 314; PDF physical p. 10"
    sentence_summary: "Footnote 2 identifies Poussin, Correspondance, p. 15 as the citation for the account of this letter."
    original_quotes:
      - source_span: "Chapter 7, printed p. 176, footnote 2, line 314; PDF physical p. 10"
        text: "2 Correspondance, p. 15."
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: {SRC7}
      source_span: "footnote 2, line 314; printed p. 176; PDF physical p. 10"
created: '2026-10-23'
updated: '2026-10-23'
process_ref: {PROCESS_REF}
---

## 内容

### 描述

**中文：** 本卡登记 Haskell 第7章 p.176 所报告的一封书信：Poussin 于1639年初写给 Jean Lemaire，并对法国方面招揽意大利画家的发展感到担忧。此为 Haskell 的转述，不是信件原文引文。脚注2将该叙述指向 Poussin, Correspondance, p.15；本项目已有独立的 1911 年版书信集知识元，但本次未查阅该版或原信。卡名为描述性暂题，不是原信题名；书信的具体日期、原件、刊本内容及保管地点均未在本批核实。

**English:** This card records a letter reported in Haskell’s Chapter 7, p. 176: Poussin wrote to Jean Lemaire in early 1639 and was worried by French efforts to attract Italian painters. This is Haskell’s report, not a quotation from the letter. Footnote 2 points to Poussin, Correspondance, p. 15; the project separately records the 1911 correspondence edition, but neither that edition nor the original letter was consulted in this batch. The card title is descriptive, not an original title. The exact date, original, published text, and repository are not established here.

### 文献信息

| 项目 | 内容 | 依据 |
|---|---|---|
| 文献类型 | Haskell 所报告的一封书信；原信未查阅 | S1 |
| 作者 | Nicolas Poussin（据 Haskell 叙述） | S1 |
| 收信人 | Jean Lemaire（据 Haskell 叙述） | S1 |
| 时间 | 1639年初（Haskell 的约略记述，未给出日月） | S1 |
| 内容摘要 | Poussin 对法国招揽意大利画家的发展感到担忧；此为 Haskell 转述，不是信件原文引文 | S1 |
| Haskell 脚注定位 | 第7章 p.176 注2指向 Poussin, Correspondance, p.15；该页未独立查阅 | S1 |

### 身份边界

S3 新组 {GROUP} 仅含候选 {CANDIDATE}，登记范围限于 Haskell 所报告的这封书信。它与已登记的 Jouanny 1911年 Correspondance 书信集是不同 archive 对象；书信不并入出版物本身。当前证据不识别手稿、原件或具体刊本页内文本，也不扩展为 Poussin 对所有意大利画家的普遍判断。

## 关系与证据

### 关系候选入口

作者、收信人及 Haskell 的书内引注按 S6 逐项裁决。p.176 的两项画家群体评价因对象边界与受控谓词未定，保留待证。裁决与证据范围见[全书过程记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR})。
'''


def make_relation(rid, subject, object_, predicate, time, role, scope, span, source_file, note):
    return {
        "relation_id": rid,
        "subject_ku_id": subject,
        "object_ku_id": object_,
        "predicate": predicate,
        "time": time,
        "role": role,
        "scope": scope,
        "origin": "book",
        "status": "formal",
        "source_id": SOURCE_ID,
        "source_span": span,
        "source_file": source_file,
        "note": note,
    }


def build_plan():
    plans = {}
    candidates = read_csv(TABLES / "entity-candidates.csv")[1]
    if sum(row["candidate_id"] == CANDIDATE for row in candidates) != 1:
        raise ValueError("cand-6707 is missing or duplicated")
    alignment_fields, alignments, alignment_bom, alignment_nl = read_csv(TABLES / "alignment.csv")
    rows = [row for row in alignments if row["candidate_id"] == CANDIDATE and not row["external_source"]]
    if len(rows) != 1 or rows[0]["alignment_id"] != ALIGNMENT or rows[0]["decision"] != "new" or rows[0]["ku_id"] or group_id(rows[0]) != GROUP:
        raise ValueError("cand-6707 S3 decision/group changed; re-review before registration")
    manifest_fields, manifest, manifest_bom, manifest_nl = read_csv(TABLES / "ku-manifest.csv")
    if any(row["ku_id"] == KU or row["card_path"] == CARD for row in manifest) or (ROOT / CARD).exists():
        raise FileExistsError("letter KU or card path already exists")
    if ANCHOR in PROCESS_PATH.read_text(encoding="utf-8-sig"):
        raise ValueError("process anchor already exists")

    statements = {
        row["statement_id"]: row
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
        for row in [json.loads(line)]
    }
    s6_ids = [
        "st-chp7-p176-i06",
        "st-chp7-p176-i07",
        "st-chp7-p176-i08",
        "st-chp7-p176-n2-cite-correspondance",
        "st-chp7-p176-n3-cite-correspondance",
        "st-chp7-p176-n4-cite-correspondance",
        "st-chp7-p176-n8-cite-poussin-correspondance",
        "st-chp4-sec-ii-l80-89-poussin-friend-of-jean-lemaire",
        "st-chp4-sec-ii-l80-89-lemaire-created-capricci",
        "st-chp4-sec-ii-notes-l255-259-fn258-letter-citation",
        "st-chp4-sec-ii-notes-p112-fn4-poussin-correspondance",
        "st-chp6-p146-note1-correspondance",
    ]
    for sid in s6_ids:
        if sid not in statements or statements[sid].get("qualifiers", {}).get("relation_candidate") is not True:
            raise ValueError(f"missing or changed S6 candidate: {sid}")
    for path, phrases in [
        (SRC7, ["Early in 1639 Poussin wrote to his friend Jean Lemaire", "2 Correspondance, p. 15.", "3 ibid., p. 31, note 2.", "4 ibid., pp. 36 and 37;"]),
        (SRC4, ["On 4 April 1642—see Poussin Correspondance, p. 130.", "4 Poussin: Correspondance, p. 34."]),
        (SRC6, ["CorresponJance, p. 316."]),
    ]:
        content = (ROOT / path).read_text(encoding="utf-8-sig")
        if any(phrase not in content for phrase in phrases):
            raise ValueError(f"source wording changed in {path}")

    manifest_by_id = {row["ku_id"]: row for row in manifest}
    expected_types = {
        POUSSIN: "person",
        LEMAIRE: "person",
        HASKELL: "archive",
        EDITION: "archive",
    }
    for ku_id, expected_type in expected_types.items():
        if ku_id not in manifest_by_id or manifest_by_id[ku_id]["type"] != expected_type:
            raise ValueError(f"missing or changed endpoint card/type: {ku_id}")
    for candidate_id, expected_ku in [
        ("cand-1984", POUSSIN),
        ("cand-1385", LEMAIRE),
        ("cand-2962", HASKELL),
        ("cand-4634", EDITION),
    ]:
        mapped = [row["ku_id"] for row in alignments if row["candidate_id"] == candidate_id and not row["external_source"]]
        if expected_ku not in mapped:
            raise ValueError(f"existing candidate mapping changed: {candidate_id}")
    for candidate_id in ["cand-6667", "cand-6708", "cand-5755"]:
        mapped = [row for row in alignments if row["candidate_id"] == candidate_id and not row["external_source"]]
        if not mapped or any(row["ku_id"] for row in mapped) or not any(row["decision"] == "undecided" for row in mapped):
            raise ValueError(f"pending endpoint changed; re-review S6: {candidate_id}")

    rows[0]["ku_id"] = KU
    rows[0]["process_ref"] = PROCESS_REF
    rows[0]["resolution_note"] += (
        f" S4 registration: mapped {GROUP} to {KU}. The archive card is limited to Haskell's report of one letter, "
        "distinct from the 1911 Correspondance edition; original and cited page not consulted."
    )
    plans[TABLES / "alignment.csv"] = render_csv(alignment_fields, alignments, alignment_bom, alignment_nl)
    manifest.append({
        "ku_id": KU,
        "type": "archive",
        "canonical_name": "普桑致让·勒梅尔的书信（1639年初，据哈斯克尔转述）",
        "name_en": "Letter from Nicolas Poussin to Jean Lemaire, reported for early 1639",
        "source_task": "patrons-and-painters-full-book-s2",
        "card_path": CARD,
    })
    plans[TABLES / "ku-manifest.csv"] = render_csv(manifest_fields, manifest, manifest_bom, manifest_nl)
    card = card_text()
    plans[ROOT / CARD] = card.encode("utf-8")
    plans[ROOT / "04-knowledge" / "accepted.yml"] = accepted_with(CARD)

    enrichment_path = TABLES / "enrichment.jsonl"
    existing = [json.loads(line) for line in enrichment_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    preview_path = ROOT / (CARD + ".preview")
    if preview_path.exists():
        raise FileExistsError(f"refusing to overwrite existing preview {preview_path}")
    try:
        preview_path.write_text(card, encoding="utf-8", newline="\n")
        fields, source_registry, warnings, table_count = extract_records([{"ku_id": KU, "card_path": CARD + ".preview"}])
    finally:
        preview_path.unlink(missing_ok=True)
    if warnings or table_count != 1 or len(fields) != 6 or set(source_registry) != {SOURCE_ID}:
        raise ValueError(f"S5 extraction failed: tables={table_count}, fields={len(fields)}, warnings={warnings}")
    if any(row["evidence_status"] != "source_backed" for row in fields):
        raise ValueError("new S5 field is not source_backed")
    assign_ids(fields, enrichment_path)
    old_ids = {row.get("enrichment_id") for row in existing}
    old_occurrences = {row.get("occurrence_id") for row in existing}
    if any(row.get("enrichment_id") in old_ids or row.get("occurrence_id") in old_occurrences for row in fields):
        raise ValueError("S5 ID or occurrence collision")
    old_bytes = enrichment_path.read_bytes()
    if old_bytes and not old_bytes.endswith(b"\n"):
        old_bytes += b"\n"
    plans[enrichment_path] = old_bytes + render_jsonl(fields)

    relation_path = TABLES / "relations.csv"
    relation_fields, relations, relation_bom, relation_nl = read_csv(relation_path)
    numeric_ids = [int(match.group(1)) for row in relations if (match := re.fullmatch(r"rel-(\d+)", row["relation_id"]))]
    if max(numeric_ids, default=0) != 1603:
        raise ValueError("relation ID baseline changed")
    if any(any(sid in row.get("source_span", "") for sid in s6_ids) for row in relations):
        raise ValueError("one or more target S6 candidates already have relation rows")
    if any(row["subject_ku_id"] == HASKELL and row["object_ku_id"] == EDITION and row["predicate"] == "cites" for row in relations):
        raise ValueError("Haskell-to-Correspondance cites relation already exists")

    vocabulary = yaml.safe_load((ROOT / ".agents" / "skills" / "ingest" / "references" / "relation-types.yml").read_text(encoding="utf-8"))
    ranges = yaml.safe_load((ROOT / "01-domain" / "relation-domain-range.yml").read_text(encoding="utf-8"))["domain_range"]
    types = {row["ku_id"]: row["type"] for row in manifest}
    new_relations = [
        make_relation(
            "rel-1604", KU, POUSSIN, "authored_by", "early 1639", "author",
            "Haskell reports Poussin as the writer of this letter in early 1639. This records Haskell's attribution only; neither the letter nor the cited Correspondance page was consulted.",
            "Chapter 7, printed p. 176, line 81; PDF physical p. 10; statement=st-chp7-p176-i06",
            SRC7,
            "The archive KU is source-limited; exact date, manuscript identity, and repository are not established.",
        ),
        make_relation(
            "rel-1605", KU, LEMAIRE, "addressed_to", "early 1639", "addressee",
            "Haskell says Poussin wrote to his friend Jean Lemaire in early 1639. This records the reported addressee only; the letter and cited page were not consulted.",
            "Chapter 7, printed p. 176, line 81; PDF physical p. 10; statement=st-chp7-p176-i06",
            SRC7,
            "The sentence supports authorship and addressee; it does not support a subject relation to the recruitment effort.",
        ),
        make_relation(
            "rel-1606", POUSSIN, LEMAIRE, "friend_of", "", "friend",
            "Haskell explicitly identifies Jean Lemaire as Poussin's friend; no date or further particulars are supplied.",
            "Chapter 4, printed p. 105, line 81; PDF physical p. 16; statement=st-chp4-sec-ii-l80-89-poussin-friend-of-jean-lemaire",
            SRC4,
            "Haskell repeats the friendship wording in Chapter 7, printed p. 176, line 81; Chapter 4 is the direct S2 relation candidate.",
        ),
    ]
    citation_specs = [
        ("st-chp4-sec-ii-notes-l255-259-fn258-letter-citation", SRC4, "Chapter 4, printed p. 106, line 258; PDF physical p. 17", "p. 130; letter dated 4 April 1642", "Haskell's note cites the Correspondance edition at p. 130 for a letter dated 4 April 1642."),
        ("st-chp4-sec-ii-notes-p112-fn4-poussin-correspondance", SRC4, "Chapter 4, printed p. 112, footnote 4, line 283; PDF physical p. 23", "p. 34", "Haskell's footnote identifies Correspondance p. 34 as the source cited for an assessment attributed to M. de Noyers."),
        ("st-chp6-p146-note1-correspondance", SRC6, "Chapter 6, printed p. 146, footnote 1, line 8; PDF physical p. 1", "p. 316", "Haskell's footnote cites Correspondance p. 316 for the letter quoted in the body; OCR spelling is preserved."),
        ("st-chp7-p176-n2-cite-correspondance", SRC7, "Chapter 7, printed p. 176, footnote 2, line 314; PDF physical p. 10", "p. 15", "Haskell's footnote cites Correspondance p. 15 for the account of Poussin's 1639 letter to Jean Lemaire."),
        ("st-chp7-p176-n3-cite-correspondance", SRC7, "Chapter 7, printed p. 176, footnote 3, line 315; PDF physical p. 10", "p. 31, note 2", "Ibid. in footnote 3 resolves to Correspondance, named in the immediately preceding footnote 2."),
        ("st-chp7-p176-n4-cite-correspondance", SRC7, "Chapter 7, printed p. 176, footnote 4, line 315; PDF physical p. 10", "pp. 36–37", "Ibid. in footnote 4 resolves to Correspondance, named in footnote 2."),
        ("st-chp7-p176-n8-cite-poussin-correspondance", SRC7, "Chapter 7, printed p. 176, footnote 8, line 317; PDF physical p. 10", "p. 188", "Haskell's footnote explicitly cites Poussin: Correspondance p. 188."),
    ]
    for offset, (sid, source_file, span, locator, explanation) in enumerate(citation_specs, start=1607):
        new_relations.append(make_relation(
            f"rel-{offset}", HASKELL, EDITION, "cites", "", "in-book citation",
            f"{explanation} This records Haskell's citation only; the cited edition and page were not independently consulted.",
            f"{span}; statement={sid}",
            source_file,
            f"Candidate maps to the existing Jouanny 1911 Correspondance KU. Locator: {locator}.",
        ))
    if len(new_relations) != 10:
        raise ValueError("expected ten formal relation rows")
    for row in new_relations:
        if row["predicate"] not in vocabulary["types"]:
            raise ValueError(f"uncontrolled predicate: {row['predicate']}")
        allowed = ranges.get(row["predicate"])
        if allowed and (
            types[row["subject_ku_id"]] not in allowed["domain"]
            or types[row["object_ku_id"]] not in allowed["range"]
        ):
            raise ValueError(f"domain/range mismatch in {row['relation_id']}")
        natural = (row["subject_ku_id"], row["object_ku_id"], row["predicate"], row["time"], row["role"], row["scope"])
        if any(
            (old["subject_ku_id"], old["object_ku_id"], old["predicate"], old["time"], old["role"], old["scope"]) == natural
            for old in relations
        ):
            raise ValueError(f"natural-key duplicate: {row['relation_id']}")
    relations.extend(new_relations)
    plans[relation_path] = render_csv(relation_fields, relations, relation_bom, relation_nl)

    lemma_path = ROOT / "04-knowledge" / "units" / "persons" / "jean-lemaire.md"
    lemma = lemma_path.read_text(encoding="utf-8-sig")
    old = re.compile(r"本任务未新增正式关系。直接S2关系候选.*?留待S6逐条裁决。", re.DOTALL)
    if len(old.findall(lemma)) != 1:
        raise ValueError("Jean Lemaire relation note changed")
    new_note = (
        "S2候选 st-chp4-sec-ii-l80-89-poussin-friend-of-jean-lemaire 已裁为正式 friend_of，"
        "依据 Haskell 第4章 p.105 L81。候选 st-chp4-sec-ii-l80-89-lemaire-created-capricci "
        "仍为 pending：cand-5755 指向尚未识别的复数 capricci 作品组，S3保留 undecided，"
        "本批不登记猜测性的单件作品。详见[全书过程记录](../../../03-processing/"
        "patrons-and-painters-full-book-s2/process/knowledge.md#" + ANCHOR + ")。"
    )
    lemma = old.sub(new_note, lemma, count=1)
    plans[lemma_path] = lemma.encode("utf-8")

    edition_path = ROOT / "04-knowledge" / "units" / "archives" / "poussin-correspondance-jouanny-1911.md"
    edition = edition_path.read_text(encoding="utf-8-sig")
    old = re.compile(r"当前没有登记正式关系。S2 中八条关于 Haskell 引用该1911年版的关系候选留待 S6 核对端点、引用方向、各自书信语境及证据范围。")
    if len(old.findall(edition)) != 1:
        raise ValueError("Correspondance card relation note changed")
    new_note = (
        "七条 S2 relation-candidate 记录均对应 Haskell 对本1911年版的具体书内引注，已在本批逐条裁为 formal cites。"
        "第21章书目条目本身只识别出版物，不另建自引关系。这些边仅记录 Haskell 的引用，不表示已查阅本版、所引页或个别书信。"
        "被引的1639年书信仍作为独立 archive 对象。详见[全书过程记录](../../../03-processing/"
        "patrons-and-painters-full-book-s2/process/knowledge.md#" + ANCHOR + ")。"
    )
    edition = old.sub(new_note, edition, count=1)
    plans[edition_path] = edition.encode("utf-8")

    decisions = [
        ("st-chp7-p176-i06", "formal", "rel-1604 authored_by Poussin; rel-1605 addressed_to Jean Lemaire."),
        ("st-chp4-sec-ii-l80-89-poussin-friend-of-jean-lemaire", "formal", "rel-1606 friend_of; Haskell explicitly states the relationship."),
        ("st-chp4-sec-ii-notes-l255-259-fn258-letter-citation", "formal", "rel-1607 cites the 1911 edition at p. 130."),
        ("st-chp4-sec-ii-notes-p112-fn4-poussin-correspondance", "formal", "rel-1608 cites the 1911 edition at p. 34."),
        ("st-chp6-p146-note1-correspondance", "formal", "rel-1609 cites the 1911 edition at p. 316."),
        ("st-chp7-p176-n2-cite-correspondance", "formal", "rel-1610 cites the 1911 edition at p. 15."),
        ("st-chp7-p176-n3-cite-correspondance", "formal", "rel-1611 cites the 1911 edition at p. 31 n. 2; ibid. resolves to note 2."),
        ("st-chp7-p176-n4-cite-correspondance", "formal", "rel-1612 cites the 1911 edition at pp. 36–37; ibid. resolves to note 2."),
        ("st-chp7-p176-n8-cite-poussin-correspondance", "formal", "rel-1613 cites the 1911 edition at p. 188."),
        ("st-chp7-p176-i07", "pending", "cand-6667 remains S3 undecided; opinion target and controlled predicate unresolved."),
        ("st-chp7-p176-i08", "pending", "cand-6708 remains S3 undecided; group endpoint and controlled predicate unresolved."),
        ("st-chp4-sec-ii-l80-89-lemaire-created-capricci", "pending", "cand-5755 is an unidentified plural work group and remains S3 undecided."),
    ]
    table = "\n".join(f"| {sid} | {status} | {note} |" for sid, status, note in decisions)
    process = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_record = f'''

<a id="{ANCHOR}"></a>

### S3沿用／S4／S5／S6：第七章 p.176 Poussin 致 Jean Lemaire 书信与 Correspondance 引注（2026-10-23）

**S3 与 S4。** 沿用 cand-6707 的既有 S3 new 决定和身份组 {GROUP}，将一封 Haskell 报告的1639年初书信登记为 archive KU {KU}。依据为第7章 p.176 L81及注2；该书信与已登记的 Jouanny 1911年 Correspondance 书信集是不同对象。新卡将题名标为描述性暂题，不声称已查阅原信或刊本，也不补确切日期、手稿身份或保管地点。未重开 S3。

**S5。** 新卡增加6条 Haskell 原书支持字段（{fields[0]['enrichment_id']}–{fields[-1]['enrichment_id']}）：文献类型、作者、收信人、约略时间、内容摘要和 Haskell 引注定位。均为 source_backed；没有把书信内容转述标成原信引文。

**S6 逐项裁决。** 本批处理与书信端点、相同 Correspondance 版本及 Poussin—Lemaire 关系直接相关的12条 relation candidates。9条 formal 决定生成10条正式关系；3条保留 pending，不在 relations.csv 中创建无有效端点或无受控谓词的占位边。

| statement_id | 决定 | 去向 |
|---|---|---|
{table}

第7章 p.176 的 i07、i08 仅记录 Haskell 转述的 Poussin 对艺术家群体的评价；群体边界与谓词均未解决，因此不生成替代边。第4章的 cand-5755 仍为既有 S3 undecided；本批不重开身份决定。第21章书目列出该1911年版，但 bibliography_lists_publication 不作为 cites relation-candidate。

**S2 边界。** 未改动 statement 或 mention；本次逐页核对及定向归属不计入统一 S2 独立复核分子。原始书信和 Correspondance p.15、34、130、316、31 n.2、36–37、188均未独立查阅。
'''
    if ANCHOR in process:
        raise ValueError("process anchor already exists")
    plans[PROCESS_PATH] = (process.rstrip() + process_record).encode("utf-8")

    result = (ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md").read_text(encoding="utf-8-sig")
    if "S6已裁决620/10,480条（385 formal、168 pending、67 rejected）" not in result:
        raise ValueError("S6 baseline changed; rebase result counts before applying")

    counts = {
        "new_archive_KU": KU,
        "new_source_backed_fields": len(fields),
        "formal_relations": len(new_relations),
        "S6_candidates_decided": len(decisions),
        "S6_formal": sum(status == "formal" for _, status, _ in decisions),
        "S6_pending": sum(status == "pending" for _, status, _ in decisions),
    }
    checks = [
        f"mapped existing S3 new group {GROUP} to a source-limited archive KU",
        "extracted six source-backed S5 rows",
        "added ten controlled formal relations after domain/range and natural-key checks",
        "decided twelve S6 candidates: nine formal and three pending",
        "left S2 statements, mentions, and independent-review numerator unchanged",
        "updated the Jean Lemaire and Correspondance card notes to match S6 decisions",
    ]
    return plans, counts, checks


def write_stdout(value):
    sys.stdout.buffer.write(value.encode("utf-8", errors="replace"))


def main():
    parser = argparse.ArgumentParser(description="Register the Poussin letter endpoint and linked S6 decisions.")
    parser.add_argument("--apply", action="store_true", help="write the prechecked plan; default is read-only")
    args = parser.parse_args()
    plans, counts, checks = build_plan()
    write_stdout("mode=apply\n" if args.apply else "mode=dry-run\n")
    for check in checks:
        write_stdout(f"- {check}\n")
    write_stdout("counts:\n")
    for key, value in counts.items():
        write_stdout(f"  {key}={value}\n")
    write_stdout("planned files and exact diff:\n")
    for path, payload in plans.items():
        old = path.read_bytes().decode("utf-8-sig") if path.exists() else ""
        new = payload.decode("utf-8-sig")
        write_stdout(f"\n--- {path.relative_to(ROOT).as_posix()} ---\n")
        write_stdout("".join(difflib.unified_diff(
            old.splitlines(keepends=True), new.splitlines(keepends=True),
            fromfile="before", tofile="after",
        )))
    if args.apply:
        for path, payload in plans.items():
            atomic_write(path, payload)
        write_stdout(f"\napplied {len(plans)} files\n")
    else:
        write_stdout("\nno files written; inspect the diff, then rerun with --apply\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
