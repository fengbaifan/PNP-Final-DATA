from __future__ import annotations

import argparse
import csv
import difflib
import io
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
ENTRY = ROOT / "AGENTS.md"
CANDIDATES = TABLES / "entity-candidates.csv"
ALIGNMENT = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
CARD = ROOT / "04-knowledge" / "units" / "persons" / "giovanni-previtali.md"

ANCHOR = "s3-s4-person-previtali-cross-chapter-group-20261019"
PROCESS_REF = f"03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR}"
GROUP = "new-person:giovanni-previtali-b5258f2c7f"
KU = "units/persons/giovanni-previtali"
CARD_PATH = "04-knowledge/units/persons/giovanni-previtali.md"
SIUSA = "https://siusa-archivi.cultura.gov.it/cgi-bin/siusa/pagina.pl?Chiave=61723&RicLin=en&RicProgetto=personalita&TipoPag=prodpersona"
POP = "https://pop.culture.gouv.fr/notice/joconde/01370014172"
ALN_EXTERNAL = "aln-12713"

PERSON_CARD = """---
title: "乔瓦尼·普雷维塔利（Giovanni Previtali）"
name_en: "Giovanni Previtali"
type: person
evidence_status: source_backed
sources:
  - citation: "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)."
    location: "第20章 p.402；OCR line 101"
    sentence_summary: "Haskell以全名Giovanni Previtali称呼批评版《现代画家、雕塑家与建筑师传》的导言作者。此处只记录书内称名和角色，不核实导言内容。"
    original_quotes:
      - source_span: "line 101; printed p. 402"
        text: >-
          There have been some important contributions to our understanding of Bellori, most of which are discussed in Giovanni Previtali’s spirited and polemical introduction to a superb new critical edition of the Lives and are not therefore mentioned here.3
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: "02-sources/02-Markdown/20_CHP-20Postscript.md"
      source_span: "line 101; printed p. 402"
  - citation: "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)."
    location: "第21章书目 p.414；OCR line 139"
    sentence_summary: "书目称Bellori 1976年版由Evelina Borea编辑、导言作者为Giovanni Previtali。该记录支持书内全名形式，不表示本项目已查阅该版。"
    original_quotes:
      - source_span: "line 139; printed p. 414"
        text: >-
          Bellori, G. P.: Le Vite de’ Pittori, Scultori e Architetti Moderni (a cura di Evelina Borea— introduzione di Giovanni Previtali), Torino 1976.
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: "02-sources/02-Markdown/21_CHP-21Bibliography.md"
      source_span: "line 139; printed p. 414"
  - citation: "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)."
    location: "第10章 p.301 注3；OCR line 590"
    sentence_summary: "注3只写See Previtali，没有题名或页码；该短引文的具体书目对象未定。"
    original_quotes:
      - source_span: "line 590; printed p. 301, note 3"
        text: "3 See Previtali."
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: "02-sources/02-Markdown/10_CHP-10_intro.md"
      source_span: "line 590; printed p. 301"
  - citation: "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)."
    location: "第10章 p.322 注3；OCR line 316"
    sentence_summary: "注3只列Previtali姓氏，未给题名或页码；具体所指作品未定。"
    original_quotes:
      - source_span: "line 316; printed p. 322, note 3"
        text: "3 Previtali."
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: "02-sources/02-Markdown/10_CHP-10_sec_ii.md"
      source_span: "line 316; printed p. 322"
  - citation: "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)."
    location: "第20章 p.410 注1；OCR line 276"
    sentence_summary: "注1写Previtali 1964并给出页码；它不提供作品题名，也不表示本项目已查阅被引原书或所引页。"
    original_quotes:
      - source_span: "line 276; printed p. 410, note 1"
        text: "1 Previtali, 1964, pp. 153-8."
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: "02-sources/02-Markdown/20_CHP-20Postscript.md"
      source_span: "line 276; printed p. 410"
  - citation: "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)."
    location: "第21章书目 p.434；OCR lines 1009-1010"
    sentence_summary: "书目列有作者形式Previtali, G.的1959年文章和1964年著作；两项出版物均未在本次独立查阅。"
    original_quotes:
      - source_span: "lines 1009-1010; printed p. 434"
        text: >-
          Previtali, G.: ‘Collezionisti di primitivi nel Settecento’ in Paragone, 1959, 113, pp. 3-32.
          Previtali, G.: La Fortuna dei Primitivi dal Vasari ai Neoclassici’, Torino 1964
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: "02-sources/02-Markdown/21_CHP-21Bibliography.md"
      source_span: "lines 1009-1010; printed p. 434"
    process_ref: "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-person-previtali-cross-chapter-group-20261019"
  - citation: "SIUSA, Sistema Informativo Unificato per le Soprintendenze Archivistiche, person record “Previtali Giovanni,” Chiave 61723."
    url: "https://siusa-archivi.cultura.gov.it/cgi-bin/siusa/pagina.pl?Chiave=61723&RicLin=en&RicProgetto=personalita&TipoPag=prodpersona"
    accessed_date: "2026-10-19"
    location: "Person authority heading and publication list"
    sentence_summary: "SIUSA以Previtali Giovanni为人物规范标题，并将La fortuna dei primitivi列为其1964年出版物；用于比对书目缩写Previtali, G.与全名，不将未涉及的生平字段写入本卡。"
    original_quotes: []
  - citation: "Ministère de la Culture, POP, Collections des musées de France (Joconde), notice 01370014172."
    url: "https://pop.culture.gouv.fr/notice/joconde/01370014172"
    accessed_date: "2026-10-19"
    location: "Bibliographie, notice lines 153-155"
    sentence_summary: "法国文化部馆藏记录将Collezionisti di Primitivi nel Settecento列作Previtali (Giovanni)在Paragone第113期、1959年发表的文章；用作书目作者缩写的交叉核对，不支持本文所引内容。"
    original_quotes: []
created: "2026-10-19"
updated: "2026-10-19"
process_ref: "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-person-previtali-cross-chapter-group-20261019"
---

## 内容

### 描述

**中文：** 本卡归并第20章全名“Giovanni Previtali”与第10章短引文、第21章书目中的“Previtali”及“Previtali, G.”形式。SIUSA记录和法国文化部馆藏书目分别将1964年著作及1959年文章对应至Giovanni Previtali。第10章两条短引文没有题名，具体指向哪一项出版物仍未确定；相关书籍、文章及引文页均未在本次独立查阅。本卡只记录人物身份，不核实Haskell对导言或被引研究内容的叙述。中文显示名为项目工作音译。

**English:** This card groups the full name “Giovanni Previtali” in Chapter 20 with the short citation forms “Previtali” and “Previtali, G.” in Chapters 10 and 21. SIUSA and the French Ministry of Culture catalogue associate the 1964 book and 1959 article, respectively, with Giovanni Previtali. The two Chapter 10 short citations give no title, so their exact publication remains unresolved; the cited book, article, and pages have not been independently consulted here. This card records the person’s identity only and does not verify Haskell’s account of the introduction or cited scholarship. The Chinese display name is a project working transliteration.

### 姓名与引文形式

- **规范姓名：** Giovanni Previtali（S2，第20章 p.402 line 101；S3，SIUSA person record）
- **书内全名形式：** Giovanni Previtali（第20章 p.402；第21章书目 p.414）
- **短引文形式：** Previtali（第10章 p.301 注3、p.322 注3；具体出版物未定）
- **书目作者形式：** Previtali, G.（第21章书目 p.434，列1959年文章及1964年著作）

## 关系与证据

### 身份入口

- **S3身份组：** new-person:giovanni-previtali-b5258f2c7f；候选 cand-10982、cand-9508；KU units/persons/giovanni-previtali。
- **人物规范记录：** [SIUSA：Previtali Giovanni，Chiave 61723](https://siusa-archivi.cultura.gov.it/cgi-bin/siusa/pagina.pl?Chiave=61723&RicLin=en&RicProgetto=personalita&TipoPag=prodpersona)。用于人物名称和作者身份对齐，不表示卡内登记了其生平。
- **书目交叉记录：** [法国文化部 POP/Joconde notice 01370014172](https://pop.culture.gouv.fr/notice/joconde/01370014172)将1959年Paragone文章作者写作“Previtali (Giovanni)”；该记录只用于姓名／书目比对。

### 关系记录

当前没有正式关系。st-chp20-p402-previtali-bellori-edition仍是S2关系候选；其archive端点cand-10981尚未登记，本卡不据此写入关系边。p.301与p.322的短引文仍未映射到某一具体出版物。
"""


def read_text(path: Path) -> tuple[str, bool]:
    raw = path.read_bytes()
    bom = raw.startswith(bytes.fromhex("efbbbf"))
    return raw[3:].decode("utf-8") if bom else raw.decode("utf-8"), bom


def csv_data(path: Path) -> tuple[list[str], list[dict[str, str]], bool]:
    text, bom = read_text(path)
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader.fieldnames or []), list(reader), bom


def render_csv(headers: list[str], rows: list[dict[str, str]], bom: bool) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=headers, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return ("\ufeff" if bom else "") + output.getvalue()


def find_one(rows: list[dict[str, str]], key: str, value: str) -> dict[str, str]:
    found = [row for row in rows if row.get(key) == value]
    if len(found) != 1:
        raise ValueError(f"expected one {key}={value}, found {len(found)}")
    return found[0]


def replace_line(text: str, prefix: str, new_line: str, label: str) -> str:
    lines = text.splitlines()
    found = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    if len(found) != 1:
        raise ValueError(f"{label}: expected one line beginning {prefix!r}, found {len(found)}")
    lines[found[0]] = new_line
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f"{label}: expected one exact occurrence, found {text.count(old)}")
    return text.replace(old, new, 1)


def current_status_line() -> str:
    return (
        "**当前状态：全书 S2 内部语义处理已完成，尚未独立语义验收；S3 为12,407个候选记录了现行决定及可追溯去向，"
        "9项冲突与5,304项待证对象仍未解决；S4 KU 登记处理中；S5、S6尚未全书收口。"
        "** 当前S3决定为same=1,973（指向1,052个既有KU）、new=5,021（4,811个身份组）、conflict=9、excluded=100、undecided=5,304（含622项未分类）。"
        "S4已登记1,182组、映射1,371条成员候选；尚待登记3,629组、3,650条映射，其中直接关系端点待登记队列为1,874组／1,874条候选映射。"
        "S2有10,399条statement标记relation_candidate=true；S6关系表有1,227条记录（1,225 formal、2 pending），两者是不同数据集，现有关系行数不是S2候选的逐条裁决覆盖数；"
        "330条S2候选至少缺一个端点。S5字段表11,693条、1,627条unverified；S6关系表45条缺结构化source_id（44条formal、1条pending）。"
        "以下当前统计以结构化表为准；按日期记录的批次段落是历史快照，不累计替代当前数。"
    )


def current_audit_line() -> str:
    return (
        "2026-10-19 最新 strict-stage 表审计通过：KU=2,201；candidates=12,407；alignments=12,710（12,407条候选决定、303条外部身份记录）、unlinked=0；"
        "enrichment=11,693（1,627条unverified）；sources=1,752；S4待登记new候选映射3,650条；errors=[]、s2_missing=[]。"
        "当前S3去向统计为same=1,973（1,052个既有KU）、new=5,021（4,811个类型内身份组）、conflict=9、excluded=100、undecided=5,304（含622项未分类）；"
        "S4已登记1,182组／1,371条候选映射，待登记3,629组／3,650条，其中直接关系端点队列1,874组／1,874条。"
        "S2有10,399条relation_candidate=true statement；S6关系表另有1,225条formal和2条pending，行数不表示这些S2候选已逐条裁决。"
        "S6关系表45条缺结构化source_id（44条formal、1条pending）；330条S2候选仍至少缺一个端点。"
        "new组无部分登记，same均指向有效且类型相符的KU，各候选决定均有理由记录。逐类型裁决及组信息见[过程记录的S3统计表](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#按类型决定数)。"
        "保留的warning为既有enrichment来源定位问题（enr-06678、enr-06937）及S2语义质量提示；结构检查不替代独立语义验收。303条独立外部身份记录单独保存。"
    )


def make_process_note() -> str:
    return f"""

<a id="{ANCHOR}"></a>
### S3–S4 person：Previtali跨章姓名形式归并与登记（2026-10-19）

cand-9508由undecided改为new，归入既有组{GROUP}，与cand-10982共同映射至[乔瓦尼·普雷维塔利人物卡](../../../04-knowledge/units/persons/giovanni-previtali.md)。本批只裁人物身份和KU映射，不裁具体短引文所指的出版物，也不新增正式关系或S5字段事实。

| 候选 | 书内形式与定位 | S3/S4去向 |
|---|---|---|
| cand-10982 | Giovanni Previtali；第20章 p.402 line 101，另见第21章 p.414 line 139 | new，组{GROUP} → {KU} |
| cand-9508 | 第10章 p.301 注3与p.322 注3写Previtali；第21章 p.434书目列两项Previtali, G.著作 | undecided改new，加入组{GROUP} → {KU} |

**身份依据。** Haskell第20章以全名称呼《Lives》批评版导言作者；第21章 p.414书目也将导言作者写为Giovanni Previtali。第21章 p.434另列Previtali, G.的1959年文章和1964年书，第20章 p.410 注1给出Previtali, 1964, pp. 153-8。[SIUSA人物记录“Previtali Giovanni”（Chiave 61723）]({SIUSA})以全名标识人物，并列出1964年《La fortuna dei primitivi》（访问日期2026-10-19）。[法国文化部POP/Joconde馆藏记录（notice 01370014172）]({POP})将同题1959年Paragone第113期文章的作者写作“Previtali (Giovanni)”（访问日期2026-10-19）。这些记录分别支持书目缩写与全名的对应；没有将外部生平字段移入卡片。

**保留的边界。** 第10章 p.301和p.322两条短注均未给题名；其所指可能为书目列出的1959年文章或1964年著作，具体映射继续待证。相关出版物及被引页未独立查阅。archive候选cand-9509仍为undecided；cand-11212和cand-11424仍各自保持独立archive候选，未因作者身份归并。S2 statement st-chp20-p402-previtali-bellori-edition仍待S6，archive端点cand-10981未登记，因此不建立formal relation。

本批新增1条外部身份记录。S3现为same=1,973（1,052个既有KU）、new=5,021／4,811组、conflict=9、excluded=100、undecided=5,304；S4现为1,182组／1,371条候选映射已登记，3,629组／3,650条待登记。人物类型new成员增至1,167；S4 person为765组／864条已登记、301组／303条待登记。直接关系端点队列为1,874组／1,874条，其中person 30／30。KU=2,201；alignment行数=12,710（12,407条候选决定、303条外部身份记录）。关系表、source_id缺失数和字段表未变化；330条S2关系候选至少缺一个端点，因为本组关联的archive端点仍未登记。本批未新增formal relation或enrichment。
"""


def updates_for_prestate() -> dict[Path, str]:
    candidate_headers, candidates, candidate_bom = csv_data(CANDIDATES)
    alignment_headers, alignments, alignment_bom = csv_data(ALIGNMENT)
    manifest_headers, manifest, manifest_bom = csv_data(MANIFEST)

    person_candidate = find_one(candidates, "candidate_id", "cand-9508")
    full_name_candidate = find_one(candidates, "candidate_id", "cand-10982")
    if person_candidate["canonical_name"] != "Previtali, G. (author named in p.301 note 3; full identity unresolved)":
        raise ValueError("cand-9508 candidate source changed")
    if full_name_candidate["canonical_name"] != "Giovanni Previtali":
        raise ValueError("cand-10982 candidate source changed")
    person_candidate["canonical_name"] = "Previtali, G. (author cited in Chapter 10 notes; work unresolved)"
    person_candidate["detail"] = (
        "Chapter 10 notes give only Previtali and do not identify a title. The full author identity is aligned with "
        "Giovanni Previtali using the same-book full-name anchor and external identity/bibliographic records; "
        "the exact p.301/p.322 cited work remains unresolved and has not been consulted."
    )
    full_name_candidate["detail"] = (
        "Named as the author of the critical edition's introduction; cross-chapter identity grouping with the "
        "Previtali, G. citation forms is recorded in S3. The reported introduction contents remain unverified."
    )

    short_alignment = find_one(alignments, "alignment_id", "aln-9680")
    full_alignment = find_one(alignments, "alignment_id", "aln-11150")
    edition_alignment = find_one(alignments, "candidate_id", "cand-10981")
    if short_alignment["decision"] != "undecided" or short_alignment["ku_id"]:
        raise ValueError("cand-9508 alignment is not in the expected S3-pending state")
    if full_alignment["decision"] != "new" or full_alignment["ku_id"]:
        raise ValueError("cand-10982 alignment is not in the expected S4-pending state")
    if GROUP not in full_alignment["resolution_note"]:
        raise ValueError("cand-10982 no longer points to the expected S3 group")
    if edition_alignment["decision"] != "new" or edition_alignment["ku_id"]:
        raise ValueError("Bellori edition archive endpoint changed; recompute the S6 endpoint count")

    short_alignment["decision"] = "new"
    short_alignment["ku_id"] = KU
    short_alignment["process_ref"] = PROCESS_REF
    short_alignment["resolution_note"] = (
        "source_ref=candidate=cand-9508; candidate_source_ref=chp-10:10_CHP-10_intro:l491-634#L590; "
        "statements=st-chp10-p301-note3-previtali-short-citation,st-chp10-p320-323-n03-previtali-gallery-citation,"
        "st-chp20-p410-n01-citation; group=" + GROUP + ". Initial S3 decision (2026-10-15): undecided because the "
        "short notes give no title and the local bibliography lists both a 1959 article and a 1964 book; that "
        "reason remains valid for the cited-work mapping. S3 ruling (2026-10-19): the person is Giovanni Previtali. "
        "The same book names Giovanni Previtali at ch.20 p.402 and identifies him as the Bellori edition's "
        "introduction author at ch.21 p.414; SIUSA person record Chiave 61723 links Giovanni Previtali to the "
        "1964 La fortuna dei primitivi, and Ministère de la Culture POP/Joconde notice 01370014172 cites "
        "Previtali (Giovanni) for the matching 1959 Paragone no.113 article. No existing person KU matches. "
        "Exact p.301/p.322 work remains unresolved; cited works and pages were not consulted. S4 registered "
        + KU + " with cand-10982; see " + PROCESS_REF + "."
    )

    full_alignment["ku_id"] = KU
    full_alignment["process_ref"] = PROCESS_REF
    full_alignment["resolution_note"] += (
        " S3 cross-chapter update (2026-10-19): cand-9508 joins this group; SIUSA person record Chiave 61723 and "
        "Ministère de la Culture POP/Joconde notice 01370014172 support the full-name/initials alignment. The "
        "earlier note that no external identity source had been accessed describes the initial S3 pass. "
        "S4 registered both members to " + KU + "; the S2 relation candidate remains for S6."
    )

    if any(row["alignment_id"] == ALN_EXTERNAL for row in alignments):
        raise ValueError(f"{ALN_EXTERNAL} already exists")
    alignment_ids = [row["alignment_id"] for row in alignments]
    alignment_numbers = [
        int(value[4:]) for value in alignment_ids
        if value.startswith("aln-") and value[4:].isdigit()
    ]
    if (
        len(candidates) != 12407
        or len(alignments) != 12709
        or max(alignment_numbers, default=0) != 12712
        or len(manifest) != 2200
    ):
        raise ValueError("authoritative baseline counts changed; re-audit before applying this batch")
    alignments.append({
        "alignment_id": ALN_EXTERNAL,
        "candidate_id": "cand-9508",
        "ku_id": "",
        "external_source": "SIUSA, person authority record “Previtali Giovanni”",
        "external_id": SIUSA,
        "decision": "new",
        "accessed_date": "2026-10-19",
        "process_ref": PROCESS_REF,
        "legacy_ku_id": "",
        "resolution_note": (
            "Identity source only: SIUSA record Chiave 61723 identifies the person as Previtali Giovanni and "
            "links the full name Giovanni Previtali to the 1964 title La fortuna dei primitivi, matching the "
            "book's abbreviated Previtali, G. bibliography entry. It does not determine which work the Chapter 10 "
            "short notes cite or verify the cited pages."
        ),
    })

    if any(row["ku_id"] == KU for row in manifest):
        raise ValueError(f"{KU} already exists in the manifest")
    manifest.append({
        "ku_id": KU,
        "type": "person",
        "canonical_name": "乔瓦尼·普雷维塔利（Giovanni Previtali）",
        "name_en": "Giovanni Previtali",
        "source_task": "patrons-and-painters-full-book-s2",
        "card_path": CARD_PATH,
    })

    accepted, accepted_bom = read_text(ACCEPTED)
    if CARD_PATH in accepted:
        raise ValueError(f"{CARD_PATH} already appears in accepted.yml")
    accepted = replace_once(accepted, "\n\nclaims:", f"\n- {CARD_PATH}\n\nclaims:", "accepted.yml")

    process_text, _ = read_text(PROCESS)
    if f'<a id="{ANCHOR}"></a>' in process_text:
        raise ValueError(f"process anchor {ANCHOR} already exists")
    old_person_row = "| person | 3,464 | 1,156 | 1,066 / 1,166 | 4 | 7 | 1,131 | 764 / 862 | 302 / 304 |"
    new_person_row = "| person | 3,464 | 1,156 | 1,066 / 1,167 | 4 | 7 | 1,130 | 765 / 864 | 301 / 303 |"
    process_text = replace_once(process_text, old_person_row, new_person_row, "S3 person type row")
    old_total_row = "| **合计** | **12,407** | **1,973** | **4,811 / 5,020** | **9** | **100** | **5,305** | **1,181 / 1,369** | **3,630 / 3,651** |"
    new_total_row = "| **合计** | **12,407** | **1,973** | **4,811 / 5,021** | **9** | **100** | **5,304** | **1,182 / 1,371** | **3,629 / 3,650** |"
    process_text = replace_once(process_text, old_total_row, new_total_row, "S3 total row")
    process_text = process_text.rstrip() + make_process_note()

    entry_text, _ = read_text(ENTRY)
    new_entry = (
        "项目版本为初始化阶段的 0.1.0；全书 S2 内部处理已完成，尚未独立语义验收。S3 已为12,407个候选记录现行决定及可追溯去向："
        "same=1,973（指向1,052个既有 KU）、new=5,021（4,811个身份组）、conflict=9、excluded=100、undecided=5,304（其中622项未分类）；"
        "这表示决定记录覆盖齐全，不表示冲突与待证身份已解决。S4 已登记1,182／4,811个新增身份组（1,371条候选映射），"
        "3,629组／3,650条映射待登记；直接关系端点待登队列为1,874组／1,874条候选映射。"
        "S2 有10,399条关系候选（relation_candidate=true）；S6关系表有1,227条记录（1,225 formal、2 pending），"
        "二者是不同数据集，现有关系行数不能代表S2候选的逐条裁决覆盖。330条S2关系候选至少缺一个端点。"
        "S5字段表11,693条、其中1,627条unverified；S6关系表45条缺结构化 source_id（44条formal、1条pending）。"
        "S5、S6尚未收口。覆盖、计数与未决项以[全书当前结果](04-knowledge/results/patrons-and-painters-full-book-s2.md)及其结构化表为准；"
        "其中按日期记录的批次段落是历史快照，不作为当前累计数。[第一章结果](04-knowledge/results/patrons-and-painters-chp-1.md)"
        "仅说明独立的历史任务，不由规则版本或文件数量推导全书完成。知识发现与页面暂停。有效对象见 [accepted.yml](04-knowledge/accepted.yml)；"
        "遗留文件与未处理来源不自动成为成果。"
    )
    entry_text = replace_line(entry_text, "项目版本为初始化阶段的 0.1.0；", new_entry, "AGENTS.md")

    result_text, _ = read_text(RESULT)
    result_text = replace_line(result_text, "**当前状态：", current_status_line(), "result current status")
    result_text = replace_line(
        result_text,
        "| [全书对齐]",
        "| [全书对齐](../tables/alignment.csv) | 12,710 条：12,407 条候选决定记录及 303 条外部身份记录；候选决定数见下表 |",
        "result alignment count",
    )
    result_text = replace_line(
        result_text,
        "2026-10-19 最新 strict-stage 表审计通过：",
        current_audit_line(),
        "result current audit",
    )
    current_queue = next(
        line for line in result_text.splitlines()
        if line.startswith("直接关系端点待登队列按类型")
    )
    current_queue = current_queue.replace("person 31／31", "person 30／30")
    current_queue = current_queue.replace("1,875组／1,875条", "1,874组／1,874条")
    current_queue = current_queue.replace("2,200张卡", "2,201张卡")
    current_queue = current_queue.replace("471张卡受关系视图影响", "472张卡受关系视图影响")
    current_queue = current_queue.replace("481个文件待渲染", "482个文件待渲染")
    result_text = replace_line(result_text, "直接关系端点待登队列按类型", current_queue, "result direct endpoint queue")
    result_text = replace_line(
        result_text,
        "| new |",
        "| new | 5,021 | 按 4,811 个当前身份组进入 S4；每组登记一个 KU |",
        "result S3 new count",
    )
    result_text = replace_line(
        result_text,
        "| undecided |",
        "| undecided | 5,304 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |",
        "result S3 undecided count",
    )

    if CARD.exists():
        raise ValueError(f"card already exists: {CARD}")
    return {
        CANDIDATES: render_csv(candidate_headers, candidates, candidate_bom),
        ALIGNMENT: render_csv(alignment_headers, alignments, alignment_bom),
        MANIFEST: render_csv(manifest_headers, manifest, manifest_bom),
        ACCEPTED: ("\ufeff" if accepted_bom else "") + accepted,
        CARD: PERSON_CARD,
        PROCESS: process_text,
        ENTRY: entry_text,
        RESULT: result_text,
    }


def already_applied() -> bool:
    _, candidates, _ = csv_data(CANDIDATES)
    _, alignments, _ = csv_data(ALIGNMENT)
    _, manifest, _ = csv_data(MANIFEST)
    person_candidate = find_one(candidates, "candidate_id", "cand-9508")
    short_alignment = find_one(alignments, "alignment_id", "aln-9680")
    full_alignment = find_one(alignments, "alignment_id", "aln-11150")
    return (
        person_candidate["canonical_name"] == "Previtali, G. (author cited in Chapter 10 notes; work unresolved)"
        and short_alignment["decision"] == "new"
        and short_alignment["ku_id"] == KU
        and full_alignment["ku_id"] == KU
        and any(row["ku_id"] == KU for row in manifest)
        and any(row["alignment_id"] == ALN_EXTERNAL for row in alignments)
        and CARD.exists()
        and f'<a id="{ANCHOR}"></a>' in PROCESS.read_text(encoding="utf-8-sig")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve and register the Previtali cross-chapter person group.")
    parser.add_argument("--apply", action="store_true", help="write the reviewed S3/S4 batch")
    args = parser.parse_args()

    try:
        updates = updates_for_prestate()
    except ValueError:
        if already_applied():
            print("no_delta: Previtali S3/S4 group is already applied")
            return 0
        raise

    originals = {path: path.read_bytes() if path.exists() else None for path in updates}
    rendered = {}
    for path, text in updates.items():
        bom = path in {CANDIDATES, ACCEPTED} and text.startswith("\ufeff")
        rendered[path] = (bytes.fromhex("efbbbf") if bom else b"") + text.removeprefix("\ufeff").encode("utf-8")

    print("S3: cand-9508 undecided -> new; group=" + GROUP)
    print("S4: " + KU + " <- cand-10982, cand-9508")
    print("S4 totals: registered=1,182 groups/1,371 mappings; pending=3,629 groups/3,650 mappings")
    print("direct relation endpoints pending=1,874 groups/1,874 candidates; person=30/30")
    print("S2 relation candidates remain 10,399; missing-endpoint candidates remain 330 because archive cand-10981 is pending")
    print("No S5 fields or formal relations are added.")
    for path, content in updates.items():
        old_text = path.read_text(encoding="utf-8-sig") if path.exists() else ""
        diff = list(difflib.unified_diff(
            old_text.splitlines(), content.splitlines(),
            fromfile=str(path.relative_to(ROOT)), tofile=str(path.relative_to(ROOT)) + " (proposed)",
            lineterm="",
        ))
        print(f"planned {path.relative_to(ROOT)}: {len(diff)} diff lines")

    if not args.apply:
        print("preview only; pass --apply to write")
        return 0

    temp_paths: list[tuple[Path, Path]] = []
    try:
        for path, data in rendered.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".", suffix=".tmp", delete=False) as handle:
                handle.write(data)
                temp_paths.append((path, Path(handle.name)))
        for path, temp in temp_paths:
            os.replace(temp, path)
    except Exception:
        for path, original in originals.items():
            if original is None:
                if path.exists():
                    path.unlink()
            else:
                path.write_bytes(original)
        for _, temp in temp_paths:
            if temp.exists():
                temp.unlink()
        raise
    print(f"applied: {len(rendered)} files; process_ref={PROCESS_REF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
