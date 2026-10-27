from __future__ import annotations

import argparse
import csv
import difflib
import io
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_REF = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-ch8-p203-b109-citation-endpoints-20261027"
SOURCE_ID = "haskell-1980-rev-ed"
PARENT_KU = "units/archives/patrons-and-painters"
BOLOGNA_KU = "units/places/bologna"

CARDS = {
    "cand-7261": {
        "ku_id": "units/archives/agnelli-galleria-pitture-card-tomm-ruffo-1734",
        "type": "archive",
        "canonical_name": "J. Agnelli, Galleria di pitture del Card. Tomm. Ruffo vescovo di Ferrara (Ferrara, 1734)",
        "name_en": "Galleria di pitture del Card. Tomm. Ruffo vescovo di Ferrara",
        "card_path": "04-knowledge/units/archives/agnelli-galleria-pitture-card-tomm-ruffo-1734.md",
        "sub_type": "printed_book",
        "title": "《费拉拉主教托马索·鲁福枢机绘画集》（Galleria di pitture del Card. Tomm. Ruffo vescovo di Ferrara）",
        "description_zh": "Haskell书目著录J. Agnelli于1734年在费拉拉出版的《Galleria di pitture del Card. Tomm. Ruffo vescovo di Ferrara》。第8章注4以Ruffo为短引，指向该书第122–123页；第8章注2还称Ruffo的画作清单与J. Agnelli的诗体评注一同刊行。此卡记录书内书目和引文定位，未核读该书内容；作者身份仍仅有首字母。",
        "description_en": "Haskell’s bibliography lists J. Agnelli’s Galleria di pitture del Card. Tomm. Ruffo vescovo di Ferrara, published at Ferrara in 1734. Chapter 8 note 4 resolves the short form Ruffo to this publication and gives pages 122–123; note 2 says the list of Ruffo’s pictures was published with verse commentaries by J. Agnelli. This card records the book bibliography and citation locator only; the publication itself was not read, and the contributor’s identity remains at initial level.",
        "source_location": "第21章书目，印刷页412，Markdown行54；第8章印刷页203注4，行10；第8章印刷页222注2，行383。",
        "source_summary": "Haskell书目列出Agnelli的1734年出版物；第8章注4引其第122–123页，第8章注2称其附有诗体评注。",
        "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
        "quotes": [
            ("第21章印刷页412，Markdown行54", "Agnelli, J.: Galleria di pitture del Card. Tomm. Ruffo vescovo di Ferrara, Ferrara 1734."),
            ("第8章印刷页203注4，Markdown行10", "4 Ruffo, pp. 122-3."),
            ("第8章印刷页222注2，Markdown行383", "2 The list of Russo’s pictures was published with verse commentaries by J. Agnelli."),
        ],
        "rows": [
            ("原书书目题名", "Galleria di pitture del Card. Tomm. Ruffo vescovo di Ferrara", "S1；第21章印刷页412，L54；statement=st-chp21-bib-l47-85-entry-05"),
            ("责任者形式（原书所列）", "Agnelli, J.；第8章注2作 J. Agnelli", "S1；第21章印刷页412，L54；S3；第8章印刷页222注2，L383；statement=st-chp21-bib-l47-85-entry-05"),
            ("出版地与年份（书目所列）", "Ferrara，1734", "S1；第21章印刷页412，L54；statement=st-chp21-bib-l47-85-entry-05"),
            ("第8章注4引文页码", "pp. 122–123", "S2；第8章印刷页203注4，L10；statement=st-chp8-p203-n4-ruffo-citation"),
        ],
        "caveat": "书内书目和引文定位不证明被引页内容；J. Agnelli的身份未据首字母扩展。",
    },
    "cand-7388": {
        "ku_id": "units/archives/maresca-il-museo-del-duca-di-martina-1893",
        "type": "archive",
        "canonical_name": "A. Maresca di Serracapriola, Il museo del duca di Martina (Napoli Nobilissima, 1893)",
        "name_en": "Il museo del duca di Martina",
        "card_path": "04-knowledge/units/archives/maresca-il-museo-del-duca-di-martina-1893.md",
        "sub_type": "journal_article",
        "title": "《马蒂纳公爵的博物馆》（Il museo del duca di Martina）",
        "description_zh": "Haskell第21章书目将《Il museo del duca di Martina》列为A. Maresca di Serracapriola的文章，刊于Napoli Nobilissima，1893年，并列出三组页码。第8章印刷页203注2引该文第49页。此卡仅记录Haskell所列书目与引文，不表示已查阅文章；作者身份仍未从缩写A.解决。",
        "description_en": "Haskell’s bibliography lists Il museo del duca di Martina as an article by A. Maresca di Serracapriola in Napoli Nobilissima (1893), with three page ranges. Chapter 8, printed p.203 note 2 cites p.49. This card records Haskell’s bibliography and citation only; the article was not consulted, and the author’s identity has not been resolved beyond the initial A.",
        "source_location": "第21章书目，印刷页429，Markdown行758–760；第8章印刷页203注2，Markdown行8。",
        "source_summary": "Haskell书目著录文章责任者、题名、期刊、年份及页码；第8章注2引用第49页。",
        "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
        "quotes": [
            ("第21章印刷页429，Markdown行758–760", "Napoli Nobilissima,\nMaresca di Serracapriola, A.: ‘Il museo del duca di Martina’ in 1893, pp.\n49-52, 74-77 and 109-111."),
            ("第8章印刷页203注2，Markdown行8", "2 See de Dominici, passim, and Maresca di Serracapriola, p. 49."),
        ],
        "rows": [
            ("原书书目题名", "Il museo del duca di Martina", "S1；第21章印刷页429，L758–760；statement=st-chp21-bib-l756-806-entry-02"),
            ("责任者形式（原书所列）", "Maresca di Serracapriola, A.", "S1；第21章印刷页429，L759；statement=st-chp21-bib-l756-806-author-maresca"),
            ("期刊与年份（书目所列）", "Napoli Nobilissima，1893", "S1；第21章印刷页429，L758–760；statement=st-chp21-bib-l756-806-entry-02"),
            ("书目所列页码", "49–52、74–77、109–111", "S1；第21章印刷页429，L759–760；statement=st-chp21-bib-l756-806-entry-02"),
            ("第8章注2引文页码", "p. 49", "S2；第8章印刷页203注2，L8；statement=st-chp8-p203-n2-cite-maresca"),
        ],
        "caveat": "书目条目和引文页码不证明文章内容；作者关系待A. Maresca di Serracapriola的人物身份解决后再形成正式边。",
    },
    "cand-7387": {
        "ku_id": "units/archives/oretti-descrizione-pitture-bologna-ms-b109",
        "type": "archive",
        "canonical_name": "Marcello Oretti, Descrizione delle Pitture che ornano le Case de’ Cittadini della Città di Bologna (manuscript B.109)",
        "name_en": "Descrizione delle Pitture che ornano le Case de’ Cittadini della Città di Bologna (manuscript B.109)",
        "card_path": "04-knowledge/units/archives/oretti-descrizione-pitture-bologna-ms-b109.md",
        "sub_type": "manuscript",
        "title": "《博洛尼亚市民住宅绘画录》（Descrizione delle Pitture che ornano le Case de’ Cittadini della Città di Bologna）（手稿 B.109）",
        "description_zh": "Haskell第8章印刷页203注5称，博洛尼亚市立图书馆藏手稿B.109是有关Belloni、Bellucci及博洛尼亚家族收藏的来源，并把题名归于Marcello Oretti。扫描页确认题名中的“che”与“Città”；Markdown OCR转录有误。此卡记录Haskell对手稿的描述，不表示已查阅手稿，也不据“essential”断言其内容完整。",
        "description_en": "Haskell’s Chapter 8, printed p.203 note 5 describes manuscript B.109 in the Biblioteca Comunale, Bologna as a source for the collections of Belloni, Bellucci, and Bolognese families, and attributes the title to Marcello Oretti. The page image confirms “che” and “Città” in the title where the Markdown OCR is faulty. This card records Haskell’s description only; the manuscript was not consulted, and “essential” is not treated as an independent completeness claim.",
        "source_location": "第8章印刷页203注5，Markdown行10–12；PDF物理页1。",
        "source_summary": "注5记载手稿B.109的题名、责任者、书内所称保管机构及所述收藏范围；题名据扫描页校读。",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "quotes": [
            ("第8章印刷页203注5，Markdown行10–12；PDF物理页1", "5 Zanotti, I, p. 389. The essential source for the collections of Belloni, Bellucci and, indeed, all the Bolognese families is the manuscript B.109 in the Biblioteca Comunale, Bologna—Descrizione delle Pitture che ornano le Case de’ Cittadini della Città di Bologna—Opera di Marcello Oretti Bolognese."),
        ],
        "rows": [
            ("原书所列题名（据扫描页校读）", "Descrizione delle Pitture che ornano le Case de’ Cittadini della Città di Bologna", "S1；第8章印刷页203注5，L11–12；PDF物理页1；statement=st-chp8-p203-n5-zanotti-and-b109"),
            ("手稿编号", "B.109", "S1；第8章印刷页203注5，L11；statement=st-chp8-p203-n5-zanotti-and-b109"),
            ("Haskell所列保管机构与城市", "Biblioteca Comunale, Bologna", "S1；第8章印刷页203注5，L11；statement=st-chp8-p203-b109-repository"),
            ("Haskell所述主题范围", "Belloni、Bellucci及博洛尼亚家族的收藏；成员范围与完整性未定", "S1；第8章印刷页203注5，L10–12；statement=st-chp8-p203-n5-zanotti-and-b109"),
        ],
        "caveat": "题名责任、保管地点和主题范围均为Haskell书内记载；手稿及其目录未独立查阅。",
    },
    "cand-7385": {
        "ku_id": "units/persons/marcello-oretti",
        "type": "person",
        "canonical_name": "Marcello Oretti",
        "name_en": "Marcello Oretti",
        "card_path": "04-knowledge/units/persons/marcello-oretti.md",
        "sub_type": "",
        "title": "马尔切洛·奥雷蒂（Marcello Oretti）",
        "description_zh": "Haskell第8章印刷页203注5在手稿题名后署“Opera di Marcello Oretti Bolognese”。本卡仅记录该姓名及其在来源中的题名责任归属；未据此补写生平或外部身份。",
        "description_en": "In Chapter 8, printed p.203 note 5, Haskell attributes the manuscript title to “Marcello Oretti Bolognese.” This card records the name and source-stated title responsibility only; no biography or external identity is inferred.",
        "source_location": "第8章印刷页203注5，Markdown行12；PDF物理页1。",
        "source_summary": "Haskell在手稿题名末尾署名Marcello Oretti。",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "quotes": [("第8章印刷页203注5，Markdown行12；PDF物理页1", "Opera di Marcello Oretti Bolognese.")],
        "rows": [("姓名（原文拼写）", "Marcello Oretti", "S1；第8章印刷页203注5，L12；PDF物理页1；statement=st-chp8-p203-b109-authored-by-oretti")],
        "caveat": "来源中的姓名与题名责任是当前身份范围；生卒、职业和外部规范记录尚未核查。",
    },
    "cand-7386": {
        "ku_id": "units/institutions/biblioteca-comunale-bologna-source-form",
        "type": "institution",
        "canonical_name": "Biblioteca Comunale, Bologna (Haskell source form)",
        "name_en": "Biblioteca Comunale, Bologna (Haskell source form)",
        "card_path": "04-knowledge/units/institutions/biblioteca-comunale-bologna-source-form.md",
        "sub_type": "",
        "title": "博洛尼亚 Biblioteca Comunale（Biblioteca Comunale, Bologna）",
        "description_zh": "本卡记录Haskell书内以“Biblioteca Comunale, Bologna”标示的图书馆机构。第8章p.203将其列为手稿B.109的所在机构；第8章p.225、第14章p.358、第19章p.392及第21章书目也出现博洛尼亚的同一书内名称形式。此身份分组限于书内地点与名称线索，不映射到未经核验的当代机构名称，也不宣称目前保管状态。",
        "description_en": "This card records the library institution named in Haskell as “Biblioteca Comunale, Bologna.” Chapter 8 p.203 gives it as the location of manuscript B.109; Chapter 8 p.225, Chapter 14 p.358, Chapter 19 p.392, and the Chapter 21 repository list also use the Bologna library form. The identity grouping is limited to the name and locality in the book; it is not mapped to an unchecked present-day institution name and makes no claim about current custody.",
        "source_location": "第8章印刷页203注5、p.225注3；第14章印刷页358注3；第19章印刷页392；第21章书目仓储机构表，PDF物理页1。",
        "source_summary": "Haskell多处将Biblioteca Comunale与Bologna相连；仅按书内名称和地点归入同一来源限定机构组。",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "quotes": [
            ("第8章印刷页203注5，Markdown行11", "in the Biblioteca Comunale, Bologna"),
            ("第8章印刷页225注3，Markdown行177", "Biblioteca Comunale, Bologna—MS. B.4067"),
            ("第14章印刷页358注3，Markdown行210", "MSS. at Bologna, Biblioteca Comunale, MSS. Hercolani 207"),
            ("第19章印刷页392，Markdown行134–135", "Biblioteca Comunale, Bologna—MS. B.153, No. 92"),
            ("第21章书目仓储机构表，PDF物理页1，Markdown行22–24", "Bologna: Biblioteca Vaticana / Biblioteca Comunale"),
        ],
        "rows": [
            ("原书名称形式", "Biblioteca Comunale", "S1、S2、S3、S4、S5；第8章印刷页203注5、p.225注3；第14章p.358注3；第19章p.392；第21章书目；statement=st-chp8-p203-b109-repository"),
            ("书内地点限定", "Bologna", "S1、S3、S4、S5；第8章印刷页203注5；第14章p.358注3；第19章p.392；第21章书目Bologna栏；statement=st-chp8-p203-library-located-bologna"),
        ],
        "caveat": "书内同名与城市线索支持本项目的来源限定身份组；现行机构全名、沿革及当代馆藏未核查。",
    },
    "cand-7390": {
        "ku_id": "units/terms/bolognese-family-collections-ms-b109-scope",
        "type": "term",
        "canonical_name": "Bolognese family collections described in manuscript B.109 (source-defined scope)",
        "name_en": "Bolognese family collections described in manuscript B.109 (source-defined scope)",
        "card_path": "04-knowledge/units/terms/bolognese-family-collections-ms-b109-scope.md",
        "sub_type": "",
        "title": "B.109所涉博洛尼亚家族收藏范围（Bolognese family-collection scope in B.109）",
        "description_zh": "本术语记录Haskell第8章p.203注5中“Belloni、Bellucci以及博洛尼亚家族的收藏”这一来源限定的复数范围。它是手稿主题的集合性表述，不是一个具体家族，不给出完整成员名单，也不证明B.109穷尽记录所有相关收藏。",
        "description_en": "This term records the source-defined plural scope in Haskell’s Chapter 8 p.203 note 5: collections associated with Belloni, Bellucci, and Bolognese families. It is a collective description of the manuscript’s subject, not a particular family. It supplies no complete membership list and does not establish that B.109 exhaustively records all relevant collections.",
        "source_location": "第8章印刷页203注5，Markdown行10–12；PDF物理页1。",
        "source_summary": "Haskell把B.109描述为涉及Belloni、Bellucci及博洛尼亚家族收藏的来源。",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "quotes": [("第8章印刷页203注5，Markdown行10–12；PDF物理页1", "The essential source for the collections of Belloni, Bellucci and, indeed, all the Bolognese families")],
        "rows": [("来源限定的集合范围", "Belloni、Bellucci及博洛尼亚家族收藏；不是单一家族或完整成员表", "S1；第8章印刷页203注5，L10–12；statement=st-chp8-p203-n5-zanotti-and-b109")],
        "caveat": "术语只表达Haskell原文中的集合范围，不把相关家族合并，也不推定其完整名单。",
    },
}


def read_csv(name: str) -> tuple[list[str], list[dict[str, str]], bytes]:
    path = TABLES / name
    raw = path.read_bytes()
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    with io.StringIO(raw.decode("utf-8-sig"), newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader), bom


def render_csv(columns: list[str], rows: list[dict[str, str]], bom: bytes = b"") -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return bom + stream.getvalue().encode("utf-8")


def yaml_scalar(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def source_file_for_span(span: str, fallback: str) -> str:
    if "第21章" in span:
        return "02-sources/02-Markdown/21_CHP-21Bibliography.md"
    if "第19章" in span:
        return "02-sources/02-Markdown/19_CHP-19Appendix.md"
    if "第14章" in span:
        return "02-sources/02-Markdown/14_CHP-14_intro.md"
    if "第8章印刷页222" in span or "第8章印刷页225" in span:
        return "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
    if "第8章印刷页203注2" in span or "第8章印刷页203注4" in span:
        return "02-sources/02-Markdown/08_CHP-8_intro.md"
    return fallback


def make_card(meta: dict) -> str:
    sources_by_file: dict[str, list[tuple[str, str]]] = {}
    for span, quote in meta["quotes"]:
        source_file = source_file_for_span(span, meta["source_file"])
        sources_by_file.setdefault(source_file, []).append((span, quote))
    lines = [
        "---",
        f"title: {yaml_scalar(meta['title'])}",
        f"name_en: {yaml_scalar(meta['name_en'])}",
        f"type: {meta['type']}",
    ]
    if meta.get("sub_type"):
        lines.append(f"sub_type: {meta['sub_type']}")
    lines.extend(["evidence_status: source_backed", "sources:"])
    source_number_by_file: dict[str, int] = {}
    for source_number, (source_file, source_quotes) in enumerate(sources_by_file.items(), 1):
        source_number_by_file[source_file] = source_number
        lines.extend([
            "- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006).'",
            f"  location: {yaml_scalar('; '.join(span for span, _ in source_quotes))}",
            f"  sentence_summary: {yaml_scalar(meta['source_summary'])}",
            "  original_quotes:",
        ])
        for span, quote in source_quotes:
            lines.extend([f"  - source_span: {yaml_scalar(span)}", f"    text: {yaml_scalar(quote)}"])
        lines.extend([
            "  evidence_ref:",
            "    doc_id: patrons-and-painters",
            f"    source_file: {source_file}",
            f"    source_span: {yaml_scalar('; '.join(span for span, _ in source_quotes))}",
        ])
    lines.extend([
        "created: '2026-10-27'",
        "updated: '2026-10-27'",
        f"process_ref: {PROCESS_REF}",
        "---",
        "",
        "## 内容",
        "",
        "### 描述",
        f"**中文：** {meta['description_zh']}",
        "",
        f"**English:** {meta['description_en']}",
        "",
        "### 基本信息",
        "| 字段 | 值 | 证据 |",
        "|---|---|---|",
    ])
    for field, value, evidence in meta["rows"]:
        lines.append(f"| {field} | {value} | {evidence} |")
    lines.extend([
        "",
        "## 关系与证据",
        "",
        "### 身份与外部链接",
        "",
        meta["caveat"],
        "",
        "### 关系记录",
        "",
        "| 方向与关系 | 关联知识元 | 语境与证据 |",
        "|---|---|---|",
        "",
    ])
    return "\n".join(lines)


def make_statement(
    statement_id: str,
    segment_id: str,
    subject: str,
    predicate: str,
    object_id: str,
    line_start: int,
    line_end: int,
    page: int,
    claim: str,
    qualification: str,
    mentioned: list[str],
    quote: str,
    source_file: str,
    note: str,
    speaker: str = "Haskell",
) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": segment_id,
        "subject_candidate_id": subject,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": line_start,
            "source_line_end": line_end,
            "printed_page": page,
            "claim": claim,
            "speaker": speaker,
            "text_layer": "source-attributed relationship candidate",
            "qualification": qualification,
            "mentioned_candidate_ids": mentioned,
            "relation_candidate": True,
            "relation_candidate_note": note,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": source_file,
    }


def insert_after(rows: list[dict], anchor: str, additions: list[dict]) -> None:
    index = next((i for i, row in enumerate(rows) if row.get("statement_id") == anchor), None)
    assert index is not None, f"missing statement anchor: {anchor}"
    rows[index + 1:index + 1] = additions


def render_jsonl(rows: list[dict], original_lines: list[str]) -> bytes:
    original_by_id = {
        parsed["statement_id"]: (parsed, line)
        for line in original_lines
        if line.strip()
        for parsed in [json.loads(line)]
    }
    rendered = []
    for row in rows:
        original = original_by_id.get(row["statement_id"])
        if original and row == original[0]:
            rendered.append(original[1])
        else:
            rendered.append(json.dumps(row, ensure_ascii=False))
    return ("\n".join(rendered) + "\n").encode("utf-8")


def render_mentions_append(columns: list[str], mentions: list[dict[str, str]], bom: bytes) -> bytes:
    return render_csv(columns, mentions, bom)


def prepare() -> dict[Path, bytes]:
    files: dict[Path, bytes] = {}
    card_ids = {meta["ku_id"] for meta in CARDS.values()}
    card_paths = {meta["card_path"] for meta in CARDS.values()}

    align_cols, alignments, align_bom = read_csv("alignment.csv")
    align_by_candidate = {row["candidate_id"]: row for row in alignments}
    for candidate_id in CARDS:
        row = align_by_candidate[candidate_id]
        assert row["decision"] == "new", f"expected S3 new: {candidate_id}: {row['decision']}"
        assert not row["ku_id"], f"candidate already mapped: {candidate_id} -> {row['ku_id']}"
        row["ku_id"] = CARDS[candidate_id]["ku_id"]
        row["process_ref"] = "S3-S4-S5-S6-full-book-2026-10-27"
        row["resolution_note"] += f" | S4 registration: mapped to {row['ku_id']}; existing source-local identity group retained."

    # S4 registration triggers a targeted cross-chapter identity check for the library group.
    library_alignment = align_by_candidate["cand-7386"]
    library_alignment["resolution_note"] += (
        " S3 triggered review for S4: Chapter 8 pp.203/225, Chapter 14 p.358, "
        "Chapter 19 p.392, and the Chapter 21 repository list consistently pair Biblioteca Comunale with Bologna. "
        "This supports one source-local institution group only; current institutional identity and custody are unverified."
    )
    # The linked author forms remain unresolved; the bibliography adds no full forename.
    for candidate_id, note in {
        "cand-7389": " S2 bibliography entry st-chp21-bib-l756-806-entry-02 confirms the printed byline A. Maresca di Serracapriola but supplies no forename; S3 remains undecided and no KU is assigned.",
        "cand-7709": " The p.222 note still provides only J. Agnelli; no identity evidence resolves the forename, so S3 remains undecided and no KU is assigned.",
        "cand-2307": " S3 was rechecked because the linked publication endpoint is being registered: the picture collection remains untyped under the current taxonomy; retain undecided until an appropriate type or more specific object evidence is available.",
    }.items():
        align_by_candidate[candidate_id]["resolution_note"] += note
        align_by_candidate[candidate_id]["process_ref"] = "S3-S4-S5-S6-full-book-2026-10-27"
    files[TABLES / "alignment.csv"] = render_csv(align_cols, alignments, align_bom)

    manifest_cols, manifest, manifest_bom = read_csv("ku-manifest.csv")
    current_ku_ids = {row["ku_id"] for row in manifest}
    assert not current_ku_ids.intersection(card_ids), "one or more new KU ids already exist"
    current_card_paths = {row["card_path"] for row in manifest}
    assert not current_card_paths.intersection(card_paths), "one or more card paths already exist"
    for candidate_id, meta in CARDS.items():
        manifest.append({
            "ku_id": meta["ku_id"],
            "type": meta["type"],
            "canonical_name": meta["canonical_name"],
            "name_en": meta["name_en"],
            "source_task": "patrons-and-painters-full-book-s2",
            "card_path": meta["card_path"],
        })
        card_path = ROOT / meta["card_path"]
        assert not card_path.exists(), f"refusing to overwrite existing card: {card_path}"
        files[card_path] = make_card(meta).encode("utf-8")
    files[TABLES / "ku-manifest.csv"] = render_csv(manifest_cols, manifest, manifest_bom)

    statement_path = TABLES / "book-statements.jsonl"
    original_statement_lines = statement_path.read_text(encoding="utf-8").splitlines()
    statements = [json.loads(line) for line in original_statement_lines if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statements}
    new_statement_ids = {
        "st-chp8-p203-b109-authored-by-oretti",
        "st-chp8-p203-b109-repository",
        "st-chp8-p203-library-located-bologna",
        "st-chp8-p222-n2-agnelli-contributed-commentaries",
        "st-chp21-bib-l756-806-author-maresca",
    }
    assert not new_statement_ids.intersection(statement_by_id), "one or more S2 statement IDs already exist"

    statement_by_id["st-chp8-p203-n2-cite-maresca"]["qualifiers"]["relation_candidate_note"] = (
        "S6 formal: rel-2397 records Haskell's citation to p.49 only; the article and cited page were not independently consulted."
    )
    statement_by_id["st-chp8-p203-n4-ruffo-citation"]["qualifiers"]["relation_candidate_note"] = (
        "S6 formal: rel-2396 records Haskell's citation locator pp.122–123 only; the publication pages were not independently read."
    )
    statement_by_id["st-chp8-p203-n5-zanotti-and-b109"]["qualifiers"]["relation_candidate_note"] = (
        "S6 formal: rel-2398 maps the manuscript's source-described subject to the source-defined collective-scope term; it does not establish a complete family list or manuscript contents beyond Haskell's statement."
    )
    statement_by_id["st-chp8-p222-n2-agnelli-publication"]["qualifiers"]["relation_candidate_note"] = (
        "S6 pending: the source-defined picture-collection endpoint cand-2307 remains S3 undecided because the current taxonomy has no supported collection type; the composite publication/commentary claim cannot yet be represented as a formal relation. Reopen after a supported type or more specific object evidence is available."
    )

    bib_statement = statement_by_id["st-chp21-bib-l756-806-entry-02"]
    mentioned = bib_statement["qualifiers"].setdefault("mentioned_candidate_ids", [])
    if "cand-7389" not in mentioned:
        mentioned.append("cand-7389")

    authored_by_oretti = make_statement(
        "st-chp8-p203-b109-authored-by-oretti",
        "chp-8:08_CHP-8_sec_i:l3-12",
        "cand-7387", "authored_by", "cand-7385", 12, 12, 203,
        "Haskell's manuscript-title line attributes the work to Marcello Oretti.",
        "Records the attribution printed in Haskell's title line only; manuscript authorship was not independently checked.",
        ["cand-7387", "cand-7385"], "Opera di Marcello Oretti Bolognese.",
        "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "S6 formal: source-stated title attribution; no biography or independent manuscript verification is inferred.",
        "Haskell's note 5",
    )
    manuscript_repository = make_statement(
        "st-chp8-p203-b109-repository",
        "chp-8:08_CHP-8_sec_i:l3-12",
        "cand-7387", "located_at", "cand-7386", 11, 11, 203,
        "Haskell locates manuscript B.109 in the Biblioteca Comunale, Bologna.",
        "This is Haskell's printed repository locator, not a claim about present-day custody.",
        ["cand-7387", "cand-7386", "cand-0381"], "the manuscript B.109 in the Biblioteca Comunale, Bologna",
        "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "S6 formal: source-reported manuscript location only; present custody was not checked.",
        "Haskell's note 5",
    )
    library_location = make_statement(
        "st-chp8-p203-library-located-bologna",
        "chp-8:08_CHP-8_sec_i:l3-12",
        "cand-7386", "located_at", "cand-0381", 11, 11, 203,
        "Haskell identifies the Biblioteca Comunale repository with Bologna.",
        "The source-local institution is linked to the named city; this does not identify a contemporary institutional successor.",
        ["cand-7386", "cand-0381"], "Biblioteca Comunale, Bologna",
        "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "S6 formal: printed locality only; current institutional continuity is not asserted.",
        "Haskell's note 5",
    )
    agnelli_contribution = make_statement(
        "st-chp8-p222-n2-agnelli-contributed-commentaries",
        "chp-8:08_CHP-8_sec_ii:l372-461",
        "cand-7261", "contributed_by", "cand-7709", 383, 383, 222,
        "Haskell attributes the accompanying verse commentaries in the publication to J. Agnelli.",
        "The source provides only the initial J.; the person identity remains unresolved and no forename is inferred.",
        ["cand-7261", "cand-7709"], "The list of Russo’s pictures was published with verse commentaries by J. Agnelli.",
        "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "S6 pending: c7709 remains S3 undecided on an initial-only name; no person KU or formal edge is created. Reopen if a full name or unique authority record resolves the identity.",
        "Haskell's note 2",
    )
    maresca_authorship = make_statement(
        "st-chp21-bib-l756-806-author-maresca",
        "chp-21:21_CHP-21Bibliography:l756-806",
        "cand-7388", "authored_by", "cand-7389", 759, 759, 429,
        "Haskell's bibliography prints Maresca di Serracapriola, A. as the responsibility form for Il museo del duca di Martina.",
        "Records the printed author form only; the forename and person identity are not established.",
        ["cand-7388", "cand-7389"], "Maresca di Serracapriola, A.",
        "02-sources/02-Markdown/21_CHP-21Bibliography.md",
        "S6 pending: c7389 remains S3 undecided because the bibliography gives only initial A.; no person KU or formal edge is created. Reopen if a full name or unique authority record resolves the identity.",
        "Haskell's bibliography",
    )
    insert_after(statements, "st-chp8-p203-n5-zanotti-and-b109", [authored_by_oretti, manuscript_repository, library_location])
    insert_after(statements, "st-chp8-p222-n2-agnelli-publication", [agnelli_contribution])
    insert_after(statements, "st-chp21-bib-l756-806-entry-02", [maresca_authorship])
    files[statement_path] = render_jsonl(statements, original_statement_lines)

    mention_cols, mentions, mention_bom = read_csv("mentions.csv")
    mention_ids = {row["mention_id"] for row in mentions}
    new_mentions = [
        {
            "mention_id": "m-chp8-p222-n2-agnelli-person",
            "segment_id": "chp-8:08_CHP-8_sec_ii:l372-461",
            "candidate_id": "cand-7709",
            "surface_form": "J. Agnelli",
            "start_char": "1942",
            "end_char": "1952",
            "note": "Verse-commentary contributor form in Haskell's p.222 note 2; the initial does not resolve the person's forename.",
        },
        {
            "mention_id": "m-chp21-bib-l756-806-maresca-author",
            "segment_id": "chp-21:21_CHP-21Bibliography:l756-806",
            "candidate_id": "cand-7389",
            "surface_form": "Maresca di Serracapriola, A.",
            "start_char": "97",
            "end_char": "125",
            "note": "Author form in Haskell's p.429 bibliography entry; only initial A. is printed.",
        },
    ]
    assert not mention_ids.intersection(row["mention_id"] for row in new_mentions)
    mentions.extend(new_mentions)
    files[TABLES / "mentions.csv"] = render_csv(mention_cols, mentions, mention_bom)

    relation_cols, relations, relation_bom = read_csv("relations.csv")
    existing_relation_ids = {row["relation_id"] for row in relations}
    existing_spans = {row["source_span"] for row in relations}
    relation_rows = [
        {
            "relation_id": "rel-2396", "subject_ku_id": PARENT_KU, "object_ku_id": CARDS["cand-7261"]["ku_id"],
            "predicate": "cites", "time": "", "role": "第8章注4书目引文", "scope": "Haskell's note 4 cites Ruffo, pp.122–123, for the Malpighi and Reni passage. This edge records the citation locator only; the cited publication pages were not independently read.",
            "origin": "book", "status": "formal", "source_id": SOURCE_ID, "source_span": "Chapter 8, printed p.203 note 4 L10; statement=st-chp8-p203-n4-ruffo-citation",
            "source_file": "02-sources/02-Markdown/08_CHP-8_intro.md", "note": "S6 formal; the citation identity is resolved through Haskell's bibliography; no cited-page content is asserted."
        },
        {
            "relation_id": "rel-2397", "subject_ku_id": PARENT_KU, "object_ku_id": CARDS["cand-7388"]["ku_id"],
            "predicate": "cites", "time": "", "role": "第8章注2书目引文", "scope": "Haskell's note 2 cites Maresca di Serracapriola, p.49, in connection with the Naples account. This edge records the citation only; neither the article nor cited page was independently consulted.",
            "origin": "book", "status": "formal", "source_id": SOURCE_ID, "source_span": "Chapter 8, printed p.203 note 2 L8; statement=st-chp8-p203-n2-cite-maresca",
            "source_file": "02-sources/02-Markdown/08_CHP-8_intro.md", "note": "S6 formal; bibliography supplies the article locator; it does not support claims about article contents."
        },
        {
            "relation_id": "rel-2398", "subject_ku_id": CARDS["cand-7387"]["ku_id"], "object_ku_id": CARDS["cand-7390"]["ku_id"],
            "predicate": "has_subject", "time": "", "role": "Haskell所述手稿主题范围", "scope": "Haskell describes manuscript B.109 as a source for collections associated with Belloni, Bellucci, and Bolognese families. The term represents this source-defined plural scope only; it is not a complete family list, a single family, or proof of the manuscript's contents beyond Haskell's statement.",
            "origin": "book", "status": "formal", "source_id": SOURCE_ID, "source_span": "Chapter 8, printed p.203 note 5 L10–12; statement=st-chp8-p203-n5-zanotti-and-b109",
            "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md", "note": "S6 formal under archive→term has_subject; the manuscript was not independently consulted."
        },
        {
            "relation_id": "rel-2399", "subject_ku_id": CARDS["cand-7387"]["ku_id"], "object_ku_id": CARDS["cand-7385"]["ku_id"],
            "predicate": "authored_by", "time": "", "role": "题名署名", "scope": "Haskell's p.203 note 5 ends the manuscript title with 'Opera di Marcello Oretti Bolognese.' This records Haskell's source-stated title attribution only; the manuscript was not independently inspected.",
            "origin": "book", "status": "formal", "source_id": SOURCE_ID, "source_span": "Chapter 8, printed p.203 note 5 L12; statement=st-chp8-p203-b109-authored-by-oretti",
            "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md", "note": "S6 formal for the attribution printed by Haskell; no biography or external identity is inferred."
        },
        {
            "relation_id": "rel-2400", "subject_ku_id": CARDS["cand-7387"]["ku_id"], "object_ku_id": CARDS["cand-7386"]["ku_id"],
            "predicate": "located_at", "time": "", "role": "Haskell所列手稿保管机构", "scope": "Haskell locates manuscript B.109 in the Biblioteca Comunale, Bologna. This is a source-reported repository locator and does not assert present-day custody.",
            "origin": "book", "status": "formal", "source_id": SOURCE_ID, "source_span": "Chapter 8, printed p.203 note 5 L11; statement=st-chp8-p203-b109-repository",
            "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md", "note": "S6 formal as a source-qualified location; it is not a current custody claim."
        },
        {
            "relation_id": "rel-2401", "subject_ku_id": CARDS["cand-7386"]["ku_id"], "object_ku_id": BOLOGNA_KU,
            "predicate": "located_at", "time": "", "role": "Haskell所列机构的书内城市定位", "scope": "Haskell names the repository as Biblioteca Comunale, Bologna. This edge records the locality stated in the book and makes no claim about the institution's present name or continuity.",
            "origin": "book", "status": "formal", "source_id": SOURCE_ID, "source_span": "Chapter 8, printed p.203 note 5 L11; statement=st-chp8-p203-library-located-bologna",
            "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md", "note": "S6 formal for the source-stated locality only."
        },
    ]
    assert not existing_relation_ids.intersection(row["relation_id"] for row in relation_rows)
    assert not existing_spans.intersection(row["source_span"] for row in relation_rows)
    expected_next = max(int(match.group(1)) for relation in relations if (match := re.fullmatch(r"rel-(\d+)", relation["relation_id"]))) + 1
    assert expected_next == 2396, f"unexpected relation ID sequence: {expected_next}"
    relations.extend(relation_rows)
    files[TABLES / "relations.csv"] = render_csv(relation_cols, relations, relation_bom)

    backlog_cols, backlog, backlog_bom = read_csv("candidate-backlog.csv")
    backlog_ids = {row["backlog_id"] for row in backlog}
    backlog_candidates = {row["candidate_id"] for row in backlog}
    assert not {"cand-2307", "cand-7389", "cand-7709"}.intersection(backlog_candidates)
    assert not {"bl-0050", "bl-0051", "bl-0052"}.intersection(backlog_ids)
    backlog.extend([
        {
            "backlog_id": "bl-0050", "canonical_name": "Cardinal Tommaso Ruffo's picture collection", "suggested_type": "", "status": "undecided",
            "source_id": SOURCE_ID, "source_ref": "chp-8:08_CHP-8_sec_ii:l372-461#L383", "statement_id": "st-chp8-p222-n2-agnelli-publication",
            "endpoint_role": "untyped picture-collection endpoint in the publication/commentary statement", "candidate_id": "cand-2307", "ku_id": "",
            "decision_note": "S3 remains undecided: the source distinguishes Cardinal Tommaso Ruffo's picture collection, but the current taxonomy has no suitable type for this collection as a set. No KU or formal S6 edge is created; the related statement remains pending. Reopen if a supported type or evidence clarifies the collection object.", "process_ref": PROCESS_REF,
        },
        {
            "backlog_id": "bl-0051", "canonical_name": "A. Maresca di Serracapriola", "suggested_type": "person", "status": "undecided",
            "source_id": SOURCE_ID, "source_ref": "chp-21:21_CHP-21Bibliography:l756-806#L759", "statement_id": "st-chp21-bib-l756-806-author-maresca",
            "endpoint_role": f"author of {CARDS['cand-7388']['ku_id']}", "candidate_id": "cand-7389", "ku_id": "",
            "decision_note": "S3 remains undecided: Haskell prints only the initial A. The S6 authored_by candidate is pending; do not create a person KU or expand the forename. Reopen when a full name or unique authoritative identity is available.", "process_ref": PROCESS_REF,
        },
        {
            "backlog_id": "bl-0052", "canonical_name": "J. Agnelli (verse-commentary contributor form)", "suggested_type": "person", "status": "undecided",
            "source_id": SOURCE_ID, "source_ref": "chp-8:08_CHP-8_sec_ii:l372-461#L383", "statement_id": "st-chp8-p222-n2-agnelli-contributed-commentaries",
            "endpoint_role": f"contributor of verse commentaries in {CARDS['cand-7261']['ku_id']}", "candidate_id": "cand-7709", "ku_id": "",
            "decision_note": "S3 remains undecided: Haskell gives only J. Agnelli. The S6 contributed_by candidate is pending; do not create a person KU or expand the forename. Reopen when a full name or unique authoritative identity is available.", "process_ref": PROCESS_REF,
        },
    ])
    files[TABLES / "candidate-backlog.csv"] = render_csv(backlog_cols, backlog, backlog_bom)

    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    accepted_lines = accepted_path.read_text(encoding="utf-8-sig").splitlines()
    unit_start = next((i for i, line in enumerate(accepted_lines) if line.strip() == "units:"), None)
    assert unit_start is not None
    claims_start = next((i for i, line in enumerate(accepted_lines) if line.strip() == "claims:"), len(accepted_lines))
    unit_lines = accepted_lines[unit_start + 1:claims_start]
    new_entries = [f"- {path}" for path in sorted(card_paths)]
    assert not set(new_entries).intersection(unit_lines)
    unit_lines.extend(new_entries)
    accepted_lines[unit_start + 1:claims_start] = unit_lines
    files[accepted_path] = ("\n".join(accepted_lines) + "\n").encode("utf-8")

    return files


def unified(path: Path, before: bytes, after: bytes) -> str:
    old = before.decode("utf-8-sig").splitlines(keepends=True) if before else []
    new = after.decode("utf-8-sig").splitlines(keepends=True)
    relative = path.relative_to(ROOT).as_posix()
    return "".join(difflib.unified_diff(old, new, fromfile=relative, tofile=relative + ".proposed"))


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Register the p.203 citation and manuscript endpoint batch; adjudicate supported S6 relations.")
    parser.add_argument("--apply", action="store_true", help="write after reviewing the default dry-run diff")
    args = parser.parse_args()
    files = prepare()
    print("Batch: Chapter 8 p.203 citations and manuscript B.109; map six existing S3 new groups, add five atomic S2 relation statements, six formal S6 edges, and three traceable undecided endpoint backlog rows.")
    for path, after in files.items():
        before = path.read_bytes() if path.exists() else b""
        diff = unified(path, before, after)
        if diff and not args.apply:
            print(diff, end="")
    if not args.apply:
        print("DRY RUN ONLY; no files written.")
        return
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + ".s4s6-tmp")
        temporary.write_bytes(content)
    written: list[tuple[Path, bytes | None]] = []
    try:
        for path in files:
            before = path.read_bytes() if path.exists() else None
            path.with_name(path.name + ".s4s6-tmp").replace(path)
            written.append((path, before))
        for path, expected in files.items():
            assert path.read_bytes() == expected, f"post-write bytes differ: {path}"
    except Exception:
        for path, before in reversed(written):
            if before is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(before)
        raise
    print(f"Applied {len(files)} files; post-write bytes verified:")
    for path in files:
        print(f"  {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
