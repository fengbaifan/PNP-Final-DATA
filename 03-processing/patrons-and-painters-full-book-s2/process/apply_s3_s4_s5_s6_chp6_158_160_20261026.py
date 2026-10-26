#!/usr/bin/env python3
"""Apply the evidence-bounded Chapter 6 p.158–160 endpoint batch."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
UNITS = ROOT / "04-knowledge" / "units"
PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md"
    "#s3-s4-s5-s6-chp6-p158-160-endpoints-20261026"
)
TODAY = "2026-10-26"
HASKELL_ID = "haskell-1980-rev-ed"
HASKELL_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)."
)
SOURCE_FILES = {
    "ch6": "02-sources/02-Markdown/06_CHP-6_sec_iv.md",
    "ch21": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
}
URLS = {
    "internet_culturale": "https://www.internetculturale.it/it/41/collezioni-digitali/26172/mare-magnum",
    "marucelliana_inventory": "https://marucelliana.cultura.gov.it/wp-content/uploads/2025/01/Bibliografia_materiale_mss_al_31_dic_2024.pdf",
    "sbn_mare_magnum": "https://opacnow.provincia.rovigo.it/it/now/concordi/record/LO10478587",
    "sbn_schlosser": "https://opacnow.provincia.rovigo.it/it/now/concordi/record/EC00021521",
}
SOURCE_IDS = {key: "src-" + hashlib.sha256(url.encode("utf-8")).hexdigest()[:16] for key, url in URLS.items()}


def file_bytes(path: Path) -> bytes:
    return path.read_bytes()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool, str]:
    raw = file_bytes(path)
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    rows = list(csv.DictReader(io.StringIO(text, newline="")))
    header = list(rows[0].keys()) if rows else next(csv.reader(io.StringIO(text)))
    return header, rows, bom, newline


def encode_csv(header: list[str], rows: list[dict[str, str]], bom: bool, newline: str) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=header, extrasaction="ignore", lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    content = stream.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" if bom else b"") + content


def append_csv_bytes(path: Path, rows: list[dict[str, str]]) -> bytes:
    header, current, bom, newline = read_csv(path)
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=header, extrasaction="ignore", lineterminator=newline)
    writer.writerows(rows)
    prior = file_bytes(path)
    addition = stream.getvalue().encode("utf-8")
    if prior and not prior.endswith((b"\n", b"\r")):
        prior += newline.encode("ascii")
    return prior + addition


def patch_csv_bytes(path: Path, key_field: str, updates: dict[str, dict[str, str]],
                    appends: list[dict[str, str]] | None = None) -> bytes:
    header, current, bom, newline = read_csv(path)
    updated_rows = {row[key_field]: row for row in current}
    for key, values in updates.items():
        if key not in updated_rows:
            raise ValueError(f"{path.name}: missing row for {key_field}={key}")
        updated_rows[key].update(values)
    appended = appends or []
    duplicate_keys = set(updated_rows).intersection(row[key_field] for row in appended)
    if duplicate_keys:
        raise ValueError(f"{path.name}: duplicate appended {key_field}: {sorted(duplicate_keys)}")

    raw = file_bytes(path)
    text = raw.decode("utf-8-sig")
    endings = "\r\n" if "\r\n" in text else "\n"
    rewritten: list[str] = []
    for raw_line in text.splitlines(keepends=True):
        ending = "\r\n" if raw_line.endswith("\r\n") else "\n" if raw_line.endswith("\n") else ""
        line = raw_line[:-len(ending)] if ending else raw_line
        parsed = next(csv.reader([line]))
        row_key = parsed[0] if parsed else ""
        if row_key in updates:
            buffer = io.StringIO(newline="")
            csv.DictWriter(buffer, fieldnames=header, extrasaction="ignore", lineterminator=ending or endings).writerow(updated_rows[row_key])
            rewritten.append(buffer.getvalue())
        else:
            rewritten.append(raw_line)
    if appended:
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=header, extrasaction="ignore", lineterminator=endings)
        writer.writerows(appended)
        if rewritten and not rewritten[-1].endswith(("\n", "\r")):
            rewritten.append(endings)
        rewritten.append(buffer.getvalue())
    return (b"\xef\xbb\xbf" if bom else b"") + "".join(rewritten).encode("utf-8")


def append_text_bytes(path: Path, rows: list[dict] | list[str]) -> bytes:
    prior = file_bytes(path)
    newline = b"\r\n" if b"\r\n" in prior else b"\n"
    content = b"".join(
        (row if isinstance(row, str) else json.dumps(row, ensure_ascii=False, separators=(",", ":")))
        .encode("utf-8") + newline
        for row in rows
    )
    return prior + (b"" if not prior or prior.endswith((b"\n", b"\r")) else newline) + content


def stable_id(prefix: str, value: str, length: int = 16) -> str:
    return prefix + hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def source_item(label: str, url: str, summary: str, span: str) -> dict:
    return {
        "citation": f"{label}. {url}. Accessed {TODAY}.",
        "location": span,
        "sentence_summary": summary,
        "evidence_ref": {"doc_id": url, "source_file": url, "source_span": span},
    }


def book_item(location: str, summary: str, quote: str, span: str, source_file: str) -> dict:
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


def field(field_name: str, value: str, evidence: str, source_ids: list[str], citations: list[str],
          origin: str = "book", source_ref: str = "S1", urls: list[str] | None = None,
          dispute: bool | None = None) -> dict:
    return {
        "field": field_name,
        "value": value,
        "evidence": evidence,
        "source_ids": source_ids,
        "citations": citations,
        "origin": origin,
        "source_ref": source_ref,
        "urls": urls or [],
        "dispute": dispute,
        "status": "externally_verified" if origin == "external" else "source_backed",
    }


GROUPS = {
    "cand-6410": "archive-group-4a6631726b0f",
    "cand-6411": "new-person:biagi-guido-8e6ac6d855",
    "cand-6412": "archive-group-0eabccd3d92d",
    "cand-6440": "archive-group-1023c3ab5d82",
    "cand-6451": "archive-group-b86cf413bf12",
    "cand-6453": "archive-group-58020a154e06",
    "cand-0606": "new-person:castro-di-jacomo-125a7610a0",
    "cand-11394": "archive-group-e7faaaa88355",
    "cand-12452": "new-person:julius-von-schlosser-afd064fd1b",
}
KU = {
    "cand-6410": "units/archives/mare-magnum-manuscript-bibliography",
    "cand-6411": "units/persons/guido-biagi",
    "cand-6412": "units/archives/guido-biagi-introduction-to-mare-magnum",
    "cand-6440": "units/archives/la-letteratura-artistica-second-edition-1956",
    "cand-6451": "units/archives/avvisi-roma-xix-1941-gaulli-gesu",
    "cand-6453": "units/archives/jacomo-di-castro-letter-to-antonio-ruffo-1670-09-20",
    "cand-0606": "units/persons/jacomo-di-castro",
    "cand-11394": "units/archives/indice-del-mare-magnum-biagi-1888-catalog-record",
    "cand-12452": "units/persons/julius-von-schlosser",
}


def make_cards() -> tuple[dict[str, bytes], list[dict]]:
    ic = SOURCE_IDS["internet_culturale"]
    mi = SOURCE_IDS["marucelliana_inventory"]
    sm = SOURCE_IDS["sbn_mare_magnum"]
    ss = SOURCE_IDS["sbn_schlosser"]
    ch6, ch21 = SOURCE_FILES["ch6"], SOURCE_FILES["ch21"]
    specs = [
        {
            "candidate": "cand-6410", "type": "archive", "sub_type": "manuscript bibliography",
            "title": "《Mare Magnum》（Mare Magnum）", "name_en": "Mare Magnum",
            "desc_zh": "本知识元指 Francesco Marucelli 的书目手稿 Mare Magnum，与 1888 年印行的索引及 Haskell 所称 Guido Biagi 导论分别建模。",
            "desc_en": "This unit represents Francesco Marucelli’s manuscript bibliography, the Mare Magnum. It remains distinct from the printed index published in 1888 and from Haskell’s cited introduction by Guido Biagi.",
            "sources": [
                book_item("第6章，印刷页158注1，L59。", "Haskell names the Mare Magnum as the object to which Biagi’s introduction is attached.", "1 For the life of Marucelli see the introduction by Guido Biagi to his Mare Magnum.", "L59; printed p.158 n.1", ch6),
                source_item("Internet Culturale, “Mare magnum” (Biblioteca digitale italiana)", URLS["internet_culturale"], "Describes the Mare Magnum as a bibliography developed by Francesco and Alessandro Marucelli, preserved at the Biblioteca Marucelliana, and eventually bound in 111 parchment tomes by November 1751.", "Section “Mare magnum”, lines 65–69; accessed 2026-10-26"),
                source_item("Biblioteca Marucelliana, *Bibliografia materiale manoscritti al 31 dicembre 2024*", URLS["marucelliana_inventory"], "The inventory identifies the manuscript grouping as Ms. ACB (Mare Magnum) and lists the 1888 printed index separately.", "PDF p.31, lines 1798–1802; accessed 2026-10-26"),
            ],
            "group": GROUPS["cand-6410"],
            "fields": [
                field("题名形式", "Mare Magnum", "Haskell，第6章印刷页158注1，L59；Internet Culturale，“Mare magnum”，lines 65–69。", [HASKELL_ID, ic], [HASKELL_CITATION, "Internet Culturale, “Mare magnum” (Biblioteca digitale italiana)."], origin="external", source_ref="S5", urls=[URLS["internet_culturale"]]),
                field("文献形态", "书目手稿", "Internet Culturale，“Mare magnum”，lines 65–68。", [ic], ["Internet Culturale, “Mare magnum” (Biblioteca digitale italiana)."], origin="external", source_ref="S5", urls=[URLS["internet_culturale"]]),
                field("装订规模", "1751年11月时为111册羊皮纸装订本", "Internet Culturale，“Mare magnum”，lines 67–68。", [ic], ["Internet Culturale, “Mare magnum” (Biblioteca digitale italiana)."], origin="external", source_ref="S5", urls=[URLS["internet_culturale"]]),
                field("现藏机构", "Biblioteca Marucelliana, Firenze", "Internet Culturale，“Mare magnum”，lines 64、68；Biblioteca Marucelliana inventory，PDF p.31。", [ic, mi], ["Internet Culturale, “Mare magnum” (Biblioteca digitale italiana).", "Biblioteca Marucelliana, *Bibliografia materiale manoscritti al 31 dicembre 2024*."], origin="external", source_ref="S5", urls=[URLS["internet_culturale"], URLS["marucelliana_inventory"]]),
            ],
        },
        {
            "candidate": "cand-6411", "type": "person", "title": "圭多·比亚吉（Guido Biagi）", "name_en": "Guido Biagi",
            "desc_zh": "本卡仅登记 Haskell 所引 Marucelli 导论及 Mare Magnum 索引中的 Guido Biagi；不在当前来源范围外扩展传记。",
            "desc_en": "This card records Guido Biagi only in connection with Haskell’s cited Marucelli introduction and the printed index to the Mare Magnum. It does not extend into biography beyond the current sources.",
            "sources": [
                book_item("第6章，印刷页158注1，L59。", "Haskell names Guido Biagi as the author of the introduction to Marucelli’s Mare Magnum.", "1 For the life of Marucelli see the introduction by Guido Biagi to his Mare Magnum.", "L59; printed p.158 n.1", ch6),
                source_item("Internet Culturale, “Mare magnum” (Biblioteca digitale italiana)", URLS["internet_culturale"], "Identifies Guido Biagi as the librarian who published a printed index to the Mare Magnum in 1888.", "Section “Mare magnum”, line 68; accessed 2026-10-26"),
            ],
            "group": GROUPS["cand-6411"],
            "fields": [
                field("原书姓名形式", "Guido Biagi", "Haskell，第6章印刷页158注1，L59。", [HASKELL_ID], [HASKELL_CITATION]),
                field("目录所述出版角色", "1888年印行 Mare Magnum 索引的图书馆员", "Internet Culturale，“Mare magnum”，line 68。", [ic], ["Internet Culturale, “Mare magnum” (Biblioteca digitale italiana)."], origin="external", source_ref="S5", urls=[URLS["internet_culturale"]]),
            ],
        },
        {
            "candidate": "cand-6412", "type": "archive", "sub_type": "introduction",
            "title": "圭多·比亚吉为《Mare Magnum》撰写的导论（Guido Biagi’s Introduction to the Mare Magnum）",
            "name_en": "Guido Biagi’s Introduction to the Mare Magnum",
            "desc_zh": "本知识元指 Haskell 第6章注1明确提到的 Biagi 导论。注释没有给出该导论的书目页、版次或完整题名，因此继续与书目手稿和 1888 年索引分开，暂不登记其与索引的部分关系。",
            "desc_en": "This unit represents the introduction by Biagi explicitly named in Haskell’s chapter 6 note 1. The note supplies no bibliographic page, edition, or full title; the introduction remains distinct from the manuscript bibliography and the 1888 index, with its possible containment in the index unresolved.",
            "sources": [book_item("第6章，印刷页158注1，L59。", "Haskell cites an introduction by Guido Biagi to Marucelli’s Mare Magnum.", "1 For the life of Marucelli see the introduction by Guido Biagi to his Mare Magnum.", "L59; printed p.158 n.1", ch6)],
            "group": GROUPS["cand-6412"],
            "fields": [field("Haskell所述对象", "Guido Biagi 为 Mare Magnum 撰写的导论；完整书目身份未载", "Haskell，第6章印刷页158注1，L59。", [HASKELL_ID], [HASKELL_CITATION])],
        },
        {
            "candidate": "cand-11394", "type": "archive", "sub_type": "printed index",
            "title": "《Mare Magnum索引》（Index to the Mare Magnum）", "name_en": "Index to the Mare Magnum",
            "desc_zh": "本知识元指 Francesco Marucelli 的 Mare Magnum 索引印本。Haskell 第21章书目印作 Rome 1882；Biblioteca Marucelliana 的馆藏目录和 SBN 记录均著录为 Rome 1888。该年份差异保留为来源分歧，不改写 Haskell 原文，也不把它与 Mare Magnum 手稿或 Biagi 导论合并。",
            "desc_en": "This unit represents the printed index to Francesco Marucelli’s Mare Magnum. Haskell’s chapter 21 bibliography prints Rome 1882, while the Biblioteca Marucelliana inventory and the SBN record catalogue the publication as Rome 1888. The date discrepancy is preserved as a source disagreement; the index remains distinct from the manuscript and Biagi’s introduction.",
            "sources": [
                book_item("第21章书目，印刷页429，L775–776。", "Haskell lists the index under Francesco Marucelli, states that it was edited by Guido Biagi, and prints Rome 1882.", "Marucelli, Francesco: Indice del Mare Magnum pubblicata a cura del Prof. Dott. Guido Biagi,\nRoma 1882.", "L775–776; printed p.429", ch21),
                source_item("Biblioteca Marucelliana, *Bibliografia materiale manoscritti al 31 dicembre 2024*", URLS["marucelliana_inventory"], "Lists the printed index by Francesco Marucelli, edited by Guido Biagi, Rome 1888, and separately identifies the Ms. ACB Mare Magnum holdings.", "PDF p.31, lines 1798–1802; accessed 2026-10-26"),
                source_item("Biblioteca dell’Accademia dei Concordi, SBN record LO10478587", URLS["sbn_mare_magnum"], "Catalogues Indice del Mare magnum di Francesco Marucelli, published by Guido Biagi, Rome: presso i principali librai, 1888; record LO10478587.", "Record LO10478587, description and date fields; accessed 2026-10-26"),
            ],
            "group": GROUPS["cand-11394"],
            "fields": [
                field("Haskell书目题名", "Indice del Mare Magnum", "Haskell，第21章书目，印刷页429，L775–776。", [HASKELL_ID], [HASKELL_CITATION]),
                field("Haskell书目责任者", "Marucelli, Francesco", "Haskell，第21章书目，印刷页429，L775。", [HASKELL_ID], [HASKELL_CITATION]),
                field("编辑责任（Haskell著录）", "pubblicata a cura del Prof. Dott. Guido Biagi", "Haskell，第21章书目，印刷页429，L775–776。", [HASKELL_ID], [HASKELL_CITATION]),
                field("出版地（Haskell著录）", "Roma", "Haskell，第21章书目，印刷页429，L776。", [HASKELL_ID], [HASKELL_CITATION]),
                field("出版年（Haskell著录）", "1882", "Haskell，第21章书目，印刷页429，L776。", [HASKELL_ID], [HASKELL_CITATION], dispute=True),
                field("出版项（目录著录）", "Roma: presso i principali librai, 1888", "Biblioteca Marucelliana inventory，PDF p.31，lines 1800–1802；SBN LO10478587。", [mi, sm], ["Biblioteca Marucelliana, *Bibliografia materiale manoscritti al 31 dicembre 2024*.", "Biblioteca dell’Accademia dei Concordi, SBN record LO10478587."], origin="external", source_ref="S5", urls=[URLS["marucelliana_inventory"], URLS["sbn_mare_magnum"]], dispute=True),
                field("SBN目录号", "LO10478587", "Biblioteca dell’Accademia dei Concordi, SBN record LO10478587。", [sm], ["Biblioteca dell’Accademia dei Concordi, SBN record LO10478587."], origin="external", source_ref="S5", urls=[URLS["sbn_mare_magnum"]]),
            ],
        },
        {
            "candidate": "cand-6440", "type": "archive", "sub_type": "book",
            "title": "《艺术文献学》（La letteratura artistica）", "name_en": "La letteratura artistica",
            "desc_zh": "本知识元指 Haskell 第6章注1及第21章书目所引《La letteratura artistica》第二版（Firenze, 1956）。SBN 记录将主责任者规范为 Julius von Schlosser，并在题名责任说明中列 Julius Schlosser Magnino；此处只解决被引书的作者身份，不扩展其他生平。",
            "desc_en": "This unit represents the second edition of *La letteratura artistica* (Florence, 1956) cited in Haskell’s chapter 6 note and listed in chapter 21. The SBN record gives the authorized main-author form Julius von Schlosser and names Julius Schlosser Magnino in the title statement; the authority match resolves this book’s author only and adds no broader biography.",
            "sources": [
                book_item("第6章，印刷页159注1，L63；第21章书目，印刷页436，L1096。", "Haskell cites Schlosser-Magnino and lists the second edition in Florence, 1956.", "1 For the literature on Bellori’s critical theories see Schlosser Magnino.\nSchlosser-Magnino, J.: La letteratura artistica, seconda edizione, Firenze 1956.", "Chapter 6 L63; printed p.159 n.1; Chapter 21 L1096; printed p.436", ch6),
                source_item("Biblioteca dell’Accademia dei Concordi, SBN record EC00021521", URLS["sbn_schlosser"], "Records the full title, second edition, 1956 publication data, and the authority form Schlosser, Julius: von; the title statement gives Julius Schlosser Magnino.", "Record EC00021521, description and main-author authority fields; accessed 2026-10-26"),
            ],
            "group": GROUPS["cand-6440"],
            "fields": [
                field("Haskell书目题名", "La letteratura artistica", "Haskell，第21章书目，印刷页436，L1096。", [HASKELL_ID], [HASKELL_CITATION]),
                field("版本（Haskell著录）", "seconda edizione", "Haskell，第21章书目，印刷页436，L1096。", [HASKELL_ID], [HASKELL_CITATION]),
                field("出版地（Haskell著录）", "Firenze", "Haskell，第21章书目，印刷页436，L1096。", [HASKELL_ID], [HASKELL_CITATION]),
                field("出版年（Haskell著录）", "1956", "Haskell，第21章书目，印刷页436，L1096。", [HASKELL_ID], [HASKELL_CITATION]),
                field("完整题名（目录著录）", "La letteratura artistica: manuale delle fonti della storia dell’arte moderna", "SBN record EC00021521, description field。", [ss], ["Biblioteca dell’Accademia dei Concordi, SBN record EC00021521."], origin="external", source_ref="S5", urls=[URLS["sbn_schlosser"]]),
                field("作者规范形式（目录）", "Schlosser, Julius: von; record title statement: Julius Schlosser Magnino", "SBN record EC00021521, main-author authority and description fields。", [ss], ["Biblioteca dell’Accademia dei Concordi, SBN record EC00021521."], origin="external", source_ref="S5", urls=[URLS["sbn_schlosser"]]),
            ],
        },
        {
            "candidate": "cand-6451", "type": "archive", "sub_type": "periodical notice(s)",
            "title": "《Roma》第十九卷中的告示（Avvisi cited in Roma, vol. XIX）", "name_en": "Avvisi cited in Roma, vol. XIX",
            "desc_zh": "本知识元指 Haskell 第6章 p.160 注1所引的 avvisi；它们是独立于期刊卷册的被引材料，具体篇名、日期及作者未载。Haskell 给出 Roma 第十九卷（1941）第392页定位，未因此视为已查阅告示原文。",
            "desc_en": "This unit represents the avvisi cited in Haskell’s chapter 6, page 160, note 1. They are cited materials distinct from the periodical volume; their individual titles, dates, and authors are not supplied. Haskell gives a locator at page 392 of Roma, volume XIX (1941), but the notices themselves were not consulted.",
            "sources": [book_item("第6章，印刷页160注1，L66。", "Haskell points to avvisi published in Roma, volume XIX (1941), page 392.", "1 See the avvisi published in Roma, XIX, 1941, p. 392.", "L66; printed p.160 n.1", ch6)],
            "group": GROUPS["cand-6451"],
            "fields": [
                field("被引卷册", "Roma, vol. XIX (1941)", "Haskell，第6章印刷页160注1，L66。", [HASKELL_ID], [HASKELL_CITATION]),
                field("Haskell所给页码", "392", "Haskell，第6章印刷页160注1，L66。", [HASKELL_ID], [HASKELL_CITATION]),
            ],
        },
        {
            "candidate": "cand-6453", "type": "archive", "sub_type": "letter",
            "title": "雅科莫·迪·卡斯特罗致安东尼奥·鲁福的信（Letter from Jacomo di Castro to Don Antonio Ruffo）",
            "name_en": "Letter from Jacomo di Castro to Don Antonio Ruffo",
            "desc_zh": "本知识元指 Haskell 第6章 p.160 注2所列的 1670年9月20日书信。双语标题是描述性题名，不冒充原件题签；Haskell称信件刊于 V. Ruffo 1916 年出版物第290页，该信件及刊载页未独立查阅。",
            "desc_en": "This unit represents the letter dated 20 September 1670 cited in Haskell’s chapter 6, page 160, note 2. The bilingual title is descriptive, not an archival title. Haskell says the letter was published by V. Ruffo in 1916, page 290; neither the letter nor that publication page was independently consulted.",
            "sources": [book_item("第6章，印刷页160注2，L67。", "Haskell identifies a letter to Don Antonio Ruffo dated 20 September 1670 and locates its publication at V. Ruffo, 1916, page 290.", "2 In a letter to Don Antonio Ruffo of 20 September 1670 published by V. Ruffo, 1916, p. 290.", "L67; printed p.160 n.2", ch6)],
            "group": GROUPS["cand-6453"],
            "fields": [
                field("文献类型", "书信", "Haskell，第6章印刷页160注2，L67。", [HASKELL_ID], [HASKELL_CITATION]),
                field("发信人", "Jacomo di Castro", "Haskell，第6章印刷页160正文与注2，L43–44、L67。", [HASKELL_ID], [HASKELL_CITATION]),
                field("收信人", "Don Antonio Ruffo", "Haskell，第6章印刷页160注2，L67。", [HASKELL_ID], [HASKELL_CITATION]),
                field("书信日期", "1670-09-20", "Haskell，第6章印刷页160注2，L67。", [HASKELL_ID], [HASKELL_CITATION]),
                field("Haskell所给刊载定位", "V. Ruffo, 1916, p. 290", "Haskell，第6章印刷页160注2，L67；第21章书目印刷页436确认该书目条目为 V. Ruffo 1916。", [HASKELL_ID], [HASKELL_CITATION]),
            ],
        },
        {
            "candidate": "cand-0606", "type": "person", "title": "雅科莫·迪·卡斯特罗（Jacomo di Castro）", "name_en": "Jacomo di Castro",
            "desc_zh": "本卡仅登记 Haskell 在第6章 p.160 所称的 Jacomo di Castro；当前证据将其限定为该段引述的作者，不补充其他身份或生平。",
            "desc_en": "This card records only the Jacomo di Castro named in Haskell’s chapter 6, page 160. The current evidence identifies him as the author of the passage quoted there and adds no other identity or biographical claims.",
            "sources": [book_item("第6章，印刷页160正文L43–44及注2 L67。", "Haskell attributes the quoted statement to Jacomo di Castro in 1670 and cites his letter to Don Antonio Ruffo.", "‘All over Europe there is a shortage of good artists and even in Flanders there are no longer the painters that there once were’, wrote Jacomo di Castro in 1670, echoing a general feeling.", "L43–44; printed p.160", ch6)],
            "group": GROUPS["cand-0606"],
            "fields": [
                field("姓名形式", "Jacomo di Castro", "Haskell，第6章印刷页160正文L43–44及注2 L67。", [HASKELL_ID], [HASKELL_CITATION]),
                field("本书所述角色", "1670年引述文字的发言者；注2称其致 Don Antonio Ruffo 的信刊出该文字", "Haskell，第6章印刷页160正文L43–44及注2 L67。", [HASKELL_ID], [HASKELL_CITATION]),
            ],
        },
        {
            "candidate": "cand-12452", "type": "person", "title": "尤利乌斯·冯·施洛瑟（Julius von Schlosser）", "name_en": "Julius von Schlosser",
            "desc_zh": "本卡只记录 SBN 目录将《La letteratura artistica》作者规范为 Julius von Schlosser，并在题名责任说明中作 Julius Schlosser Magnino。该规范记录与 Haskell 的“Schlosser-Magnino, J.”相接；不扩展其他生平。",
            "desc_en": "This card records the SBN authority form Julius von Schlosser for the author of *La letteratura artistica*; the title statement gives Julius Schlosser Magnino. This authority record connects to Haskell’s form “Schlosser-Magnino, J.” and does not add broader biography.",
            "sources": [
                book_item("第21章书目，印刷页436，L1096。", "Haskell lists the author form Schlosser-Magnino, J. for La letteratura artistica.", "Schlosser-Magnino, J.: La letteratura artistica, seconda edizione, Firenze 1956.", "L1096; printed p.436", ch21),
                source_item("Biblioteca dell’Accademia dei Concordi, SBN record EC00021521", URLS["sbn_schlosser"], "The record gives the title statement Julius Schlosser Magnino and the authorized main-author form Schlosser, Julius: von.", "Record EC00021521, description and main-author authority fields; accessed 2026-10-26"),
            ],
            "group": GROUPS["cand-12452"],
            "fields": [
                field("书目姓名形式（Haskell）", "Schlosser-Magnino, J.", "Haskell，第21章书目，印刷页436，L1096。", [HASKELL_ID], [HASKELL_CITATION]),
                field("目录规范姓名形式", "Schlosser, Julius: von; 题名责任说明为 Julius Schlosser Magnino", "SBN record EC00021521, main-author authority and description fields。", [ss], ["Biblioteca dell’Accademia dei Concordi, SBN record EC00021521."], origin="external", source_ref="S5", urls=[URLS["sbn_schlosser"]]),
            ],
        },
    ]

    cards: dict[str, bytes] = {}
    enrichments: list[dict] = []
    header = ["字段", "值", "证据"]
    for spec in specs:
        candidate = spec["candidate"]
        ku_id = KU[candidate]
        rows = spec["fields"]
        section = "内容 / 基本信息"
        table_value = f"{ku_id}|{section}|1|{'|'.join(header)}"
        table_id = "tbl-" + hashlib.sha256(table_value.encode("utf-8")).hexdigest()[:16]
        for index, row in enumerate(rows, 1):
            source_ids = row["source_ids"]
            enrichments.append({
                "enrichment_id": f"enr-{18018 + len(enrichments) + 1:05d}",
                "ku_id": ku_id,
                "field": row["field"],
                "value": row["value"],
                "origin": row["origin"],
                "source_id": source_ids[0],
                "source_ids": source_ids,
                "source_ref": row["source_ref"],
                "source_citations": row["citations"],
                "source_urls": row["urls"],
                "evidence": row["evidence"],
                "evidence_status": row["status"],
                "dispute": row["dispute"],
                "accessed_date": TODAY if row["origin"] == "external" else "",
                "occurrence_id": stable_id("occ-", f"{ku_id}|{row['field']}|{index}"),
                "table_id": table_id,
                "table_section": section,
                "has_header": True,
                "table_header": header,
                "row_index": index,
                "cells": [row["field"], row["value"], row["evidence"]],
                "unit_evidence_status": row["status"],
            })
        fm = {
            "title": spec["title"],
            "name_en": spec["name_en"],
            "type": spec["type"],
            "evidence_status": "source_backed",
            "sources": spec["sources"],
            "created": TODAY,
            "updated": TODAY,
            "process_ref": PROCESS_REF,
        }
        if spec.get("sub_type"):
            fm["sub_type"] = spec["sub_type"]
        fm_text = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, default_flow_style=False, width=1000)
        body = (
            "## 内容\n\n### 描述\n\n"
            f"**中文：** {spec['desc_zh']}\n\n"
            f"**English:** {spec['desc_en']}\n\n"
            "### 基本信息\n\n"
            "| 字段 | 值 | 证据 |\n|---|---|---|\n"
            + "".join("| " + " | ".join(r["cells"]) + " |\n" for r in enrichments if r["ku_id"] == ku_id)
            + "\n## 关系与证据\n\n### 身份与外部链接\n\n"
            + f"S3身份组：`{spec['group']}`；候选：`{candidate}`。跨章对齐与本批决定见[过程记录](../../../{PROCESS_REF})。\n"
        )
        rel = UNITS / (ku_id.removeprefix("units/") + ".md")
        cards[rel] = ("---\n" + fm_text + "---\n\n" + body).encode("utf-8")
    return cards, enrichments


def make_new_sources() -> list[dict[str, str]]:
    definitions = [
        ("internet_culturale", "Internet Culturale, ‘Mare magnum’ (Biblioteca digitale italiana)", "Institutional digital collection profile"),
        ("marucelliana_inventory", "Biblioteca Marucelliana, Bibliografia materiale manoscritti al 31 dicembre 2024, PDF p.31", "Inventory current to 2024-12-31"),
        ("sbn_mare_magnum", "Biblioteca dell’Accademia dei Concordi, SBN record LO10478587", "SBN catalogue record LO10478587"),
        ("sbn_schlosser", "Biblioteca dell’Accademia dei Concordi, SBN record EC00021521", "SBN catalogue record EC00021521"),
    ]
    return [{
        "source_id": SOURCE_IDS[key], "kind": "external", "label": label,
        "version": version, "accessed_date": TODAY,
        "citation": f"{label}. {URLS[key]}. Accessed {TODAY}.", "url": URLS[key],
    } for key, label, version in definitions]


def make_statements() -> list[dict]:
    quote_schlosser = "Schlosser-Magnino, J.: La letteratura artistica, seconda edizione, Firenze 1956."
    quote_marucelli = "Marucelli, Francesco: Indice del Mare Magnum pubblicata a cura del Prof. Dott. Guido Biagi,\nRoma 1882."
    return [
        {
            "statement_id": "st-chp21-bib-pub-author-schlosser-1956",
            "segment_id": "chp-21:21_CHP-21Bibliography:l1059-1100",
            "subject_candidate_id": "cand-6440", "object_candidate_id": "cand-12452", "predicate": "authored_by",
            "qualifiers": {"source_line_start": 1096, "source_line_end": 1096, "claim": "Haskell’s bibliography lists La letteratura artistica under the author form Schlosser-Magnino, J.", "speaker": "Haskell’s bibliography", "text_layer": "bibliographic entry", "printed_page": "436", "qualification": "The official SBN authority record resolves this author form to Julius von Schlosser; the cited book was not independently consulted.", "mentioned_candidate_ids": ["cand-6440", "cand-12452"], "bibliographic_record": {"author_as_printed": "Schlosser-Magnino, J.", "title_as_printed": "La letteratura artistica", "publication_details_as_printed": "seconda edizione, Firenze 1956", "record_kind": "book", "printed_page": 436}, "relation_candidate": False, "relation_candidate_note": "Bibliographic responsibility statement; kept outside the S6 relation-candidate denominator."},
            "original_quote": quote_schlosser, "origin": "book", "source_file": SOURCE_FILES["ch21"],
        },
        {
            "statement_id": "st-chp21-bib-pub-author-indice-mare-magnum",
            "segment_id": "chp-21:21_CHP-21Bibliography:l756-806",
            "subject_candidate_id": "cand-11394", "object_candidate_id": "cand-1554", "predicate": "authored_by",
            "qualifiers": {"source_line_start": 775, "source_line_end": 776, "claim": "Haskell’s bibliography lists Francesco Marucelli as the author of the Indice del Mare Magnum.", "speaker": "Haskell’s bibliography", "text_layer": "bibliographic entry", "printed_page": "429", "qualification": "This records the bibliographic responsibility as printed; the catalogue gives the index title and publication data separately.", "mentioned_candidate_ids": ["cand-11394", "cand-1554"], "bibliographic_record": {"author_as_printed": "Marucelli, Francesco", "title_as_printed": "Indice del Mare Magnum", "publication_details_as_printed": "pubblicata a cura del Prof. Dott. Guido Biagi, Roma 1882", "record_kind": "book", "printed_page": 429}, "relation_candidate": False, "relation_candidate_note": "Bibliographic responsibility statement; kept outside the S6 relation-candidate denominator."},
            "original_quote": quote_marucelli, "origin": "book", "source_file": SOURCE_FILES["ch21"],
        },
        {
            "statement_id": "st-chp21-bib-pub-compiled-by-biagi-mare-magnum",
            "segment_id": "chp-21:21_CHP-21Bibliography:l756-806",
            "subject_candidate_id": "cand-11394", "object_candidate_id": "cand-6411", "predicate": "compiled_by",
            "qualifiers": {"source_line_start": 775, "source_line_end": 776, "claim": "Haskell’s bibliography says the Indice del Mare Magnum was published a cura of Guido Biagi.", "speaker": "Haskell’s bibliography", "text_layer": "bibliographic entry", "printed_page": "429", "qualification": "The relation records the bibliographic editorial responsibility expressed by a cura di; it does not merge Biagi’s introduction with the index.", "mentioned_candidate_ids": ["cand-11394", "cand-6411"], "bibliographic_record": {"author_as_printed": "Marucelli, Francesco", "title_as_printed": "Indice del Mare Magnum", "editor_as_printed": "Prof. Dott. Guido Biagi", "publication_details_as_printed": "Roma 1882", "record_kind": "book", "printed_page": 429}, "relation_candidate": False, "relation_candidate_note": "Bibliographic responsibility statement; kept outside the S6 relation-candidate denominator."},
            "original_quote": quote_marucelli, "origin": "book", "source_file": SOURCE_FILES["ch21"],
        },
    ]


def make_relations() -> list[dict[str, str]]:
    book = "units/archives/patrons-and-painters"
    return [
        {"subject_ku_id": book, "object_ku_id": KU["cand-6412"], "predicate": "cites", "time": "", "role": "第6章 p.158 注1引注", "scope": "Haskell’s in-book citation to Biagi’s introduction; the introduction itself was not consulted.", "origin": "book", "status": "formal", "source_id": HASKELL_ID, "source_span": "S2 statement: st-chp6-p158-notes-p158-n1-biagi-mare-magnum", "source_file": SOURCE_FILES["ch6"], "note": "Citation identity only; keep the introduction distinct from the manuscript and printed index."},
        {"subject_ku_id": KU["cand-6412"], "object_ku_id": KU["cand-6411"], "predicate": "authored_by", "time": "", "role": "導論作者", "scope": "Haskell explicitly calls it an introduction by Guido Biagi; bibliographic identity beyond that wording is not inferred.", "origin": "book", "status": "formal", "source_id": HASKELL_ID, "source_span": "S2 statement: st-chp6-p158-notes-p158-n1-biagi-mare-magnum", "source_file": SOURCE_FILES["ch6"], "note": "The cited introduction remains a distinct source object."},
        {"subject_ku_id": book, "object_ku_id": KU["cand-6440"], "predicate": "cites", "time": "", "role": "第6章 p.159 注1引注", "scope": "Haskell’s in-book citation; neither the cited book nor its pages were consulted.", "origin": "book", "status": "formal", "source_id": HASKELL_ID, "source_span": "S2 statement: st-chp6-p159-note1-schlosser-magnino", "source_file": SOURCE_FILES["ch6"], "note": "Citation identity is supported by the chapter 21 bibliography; cited content is not asserted."},
        {"subject_ku_id": KU["cand-6440"], "object_ku_id": KU["cand-12452"], "predicate": "authored_by", "time": "", "role": "作者", "scope": "Haskell’s author form is resolved to the SBN main-author authority; the cited book was not consulted.", "origin": "book", "status": "formal", "source_id": HASKELL_ID, "source_span": "S2 statement: st-chp21-bib-pub-author-schlosser-1956; SBN record EC00021521 resolves the author form.", "source_file": SOURCE_FILES["ch21"], "note": "Full name and authority form are supported by SBN record EC00021521; no biography is inferred."},
        {"subject_ku_id": book, "object_ku_id": KU["cand-6451"], "predicate": "cites", "time": "", "role": "第6章 p.160 注1引注", "scope": "Haskell cites the plural avvisi and gives Roma XIX (1941), p.392; neither the notices nor the volume were consulted in this batch.", "origin": "book", "status": "formal", "source_id": HASKELL_ID, "source_span": "S2 statement: st-chp6-p160-note1-avvisi-roma-1941", "source_file": SOURCE_FILES["ch6"], "note": "The notices remain distinct from the cited periodical volume."},
        {"subject_ku_id": KU["cand-6451"], "object_ku_id": "units/archives/roma-volume-xix-1941", "predicate": "part_of", "time": "", "role": "刊载于", "scope": "Haskell says these avvisi were published in Roma, XIX (1941), p.392; this is a source-reported locator only.", "origin": "book", "status": "formal", "source_id": HASKELL_ID, "source_span": "S2 statement: st-chp6-p160-note1-avvisi-roma-1941", "source_file": SOURCE_FILES["ch6"], "note": "The periodical volume KU is reused from the matching chapter 6 citation; the notice is not merged into the volume."},
        {"subject_ku_id": book, "object_ku_id": KU["cand-6453"], "predicate": "cites", "time": "", "role": "第6章 p.160 注2引注", "scope": "Haskell cites a letter dated 20 September 1670 and locates its publication at V. Ruffo, 1916, p.290; the cited letter and page were not consulted.", "origin": "book", "status": "formal", "source_id": HASKELL_ID, "source_span": "S2 statement: st-chp6-p160-note2-jacomo-letter-ruffo", "source_file": SOURCE_FILES["ch6"], "note": "The letter and the 1916 article are distinct archive objects."},
        {"subject_ku_id": KU["cand-6453"], "object_ku_id": KU["cand-0606"], "predicate": "authored_by", "time": "1670-09-20", "role": "發信人", "scope": "Haskell’s note names Jacomo di Castro as sender of the dated letter; the letter itself was not consulted.", "origin": "book", "status": "formal", "source_id": HASKELL_ID, "source_span": "S2 statement: st-chp6-p160-note2-jacomo-letter-ruffo", "source_file": SOURCE_FILES["ch6"], "note": "Source-reported authorship only."},
        {"subject_ku_id": KU["cand-6453"], "object_ku_id": "units/persons/antonio-ruffo", "predicate": "addressed_to", "time": "1670-09-20", "role": "收信人", "scope": "Haskell’s note explicitly says the letter is to Don Antonio Ruffo; the letter itself was not consulted.", "origin": "book", "status": "formal", "source_id": HASKELL_ID, "source_span": "S2 statement: st-chp6-p160-note2-jacomo-letter-ruffo", "source_file": SOURCE_FILES["ch6"], "note": "Recipient identity reuses the existing Don Antonio Ruffo person KU."},
        {"subject_ku_id": KU["cand-6453"], "object_ku_id": "units/archives/ruffo-galleria-1916", "predicate": "part_of", "time": "1670-09-20", "role": "刊载于", "scope": "Haskell says the letter was published by V. Ruffo in 1916, p.290; the article and page were not consulted.", "origin": "book", "status": "formal", "source_id": HASKELL_ID, "source_span": "S2 statement: st-chp6-p160-note2-jacomo-letter-ruffo", "source_file": SOURCE_FILES["ch6"], "note": "The 1916 article KU is reused; the letter remains a separate archive object."},
        {"subject_ku_id": KU["cand-11394"], "object_ku_id": "units/persons/francesco-marucelli", "predicate": "authored_by", "time": "", "role": "書目責任者", "scope": "Haskell’s bibliography names Marucelli, Francesco as author; external catalogues support the 1888 publication identity.", "origin": "book", "status": "formal", "source_id": HASKELL_ID, "source_span": "S2 statement: st-chp21-bib-pub-author-indice-mare-magnum", "source_file": SOURCE_FILES["ch21"], "note": "The publication-year discrepancy is preserved separately; this edge asserts bibliographic responsibility only."},
        {"subject_ku_id": KU["cand-11394"], "object_ku_id": KU["cand-6411"], "predicate": "compiled_by", "time": "", "role": "編集責任者", "scope": "Haskell’s bibliography says published a cura of Guido Biagi; the printed index and the cited introduction remain distinct.", "origin": "book", "status": "formal", "source_id": HASKELL_ID, "source_span": "S2 statement: st-chp21-bib-pub-compiled-by-biagi-mare-magnum", "source_file": SOURCE_FILES["ch21"], "note": "Editorial responsibility is expressed in Haskell’s bibliography and corroborated by the Marucelliana and SBN catalogue records."},
        {"subject_ku_id": KU["cand-6410"], "object_ku_id": "units/institutions/biblioteca-marucelliana", "predicate": "located_at", "time": "", "role": "現藏機構（來源所述）", "scope": "Internet Culturale describes the Mare Magnum as preserved at the Biblioteca Marucelliana; this records reported repository location, not ownership.", "origin": "external", "status": "formal", "source_id": SOURCE_IDS["internet_culturale"], "source_span": "Internet Culturale, “Mare magnum”, lines 64–69; accessed 2026-10-26", "source_file": URLS["internet_culturale"], "note": "Institution is an existing KU; the original manuscript remains distinct from the printed index."},
    ]


def make_new_mentions() -> list[dict[str, str]]:
    return [
        {"mention_id": "m-chp21-bib-l1059-1100-023-author", "segment_id": "chp-21:21_CHP-21Bibliography:l1059-1100", "candidate_id": "cand-12452", "surface_form": "Schlosser-Magnino, J.", "start_char": "2714", "end_char": "2735", "note": "Bibliography author form resolved to the SBN authority record EC00021521; identity remains scoped to this publication."},
        {"mention_id": "m-chp21-bib-l756-806-010-author", "segment_id": "chp-21:21_CHP-21Bibliography:l756-806", "candidate_id": "cand-1554", "surface_form": "Marucelli, Francesco", "start_char": "996", "end_char": "1016", "note": "Author sub-mention in the Indice del Mare Magnum bibliography entry."},
        {"mention_id": "m-chp21-bib-l756-806-010-editor", "segment_id": "chp-21:21_CHP-21Bibliography:l756-806", "candidate_id": "cand-6411", "surface_form": "Guido Biagi", "start_char": "1075", "end_char": "1086", "note": "Editorial responsibility sub-mention in the Indice del Mare Magnum bibliography entry."},
    ]


def candidate_new_row() -> dict[str, str]:
    return {
        "candidate_id": "cand-12452", "index_entry_id": "", "canonical_name": "Julius von Schlosser",
        "index_page_range": "", "suggested_type": "person", "status": "open", "index_source_file": "",
        "sub_entry": "", "detail": "SBN record EC00021521 resolves the chapter 21 bibliography form ‘Schlosser-Magnino, J.’ to the authority form Schlosser, Julius: von; do not expand beyond this publication identity.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": "chp-21:21_CHP-21Bibliography:l1059-1100#L1096",
    }


def update_alignment_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    for candidate, ku_id in KU.items():
        if candidate == "cand-12452":
            continue
        matches = [row for row in rows if row["candidate_id"] == candidate]
        if len(matches) != 1:
            raise ValueError(f"expected one alignment row for {candidate}; got {len(matches)}")
        row = matches[0]
        if row["decision"] != "new" or row["ku_id"]:
            raise ValueError(f"unexpected S3/S4 state for {candidate}: {row['decision']} -> {row['ku_id']}")
        row["ku_id"] = ku_id
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = row["resolution_note"].rstrip() + (
            f" S4 registration (2026-10-26): existing S3 new group {GROUPS[candidate]} mapped to {ku_id}; "
            f"card, source-backed fields, and affected relation decisions are documented at {PROCESS_REF}."
        )
    roma = [row for row in rows if row["candidate_id"] == "cand-6452"]
    if len(roma) != 1 or roma[0]["decision"] != "new" or roma[0]["ku_id"]:
        raise ValueError("cand-6452 is no longer the expected unmapped new candidate")
    roma[0]["decision"] = "same"
    roma[0]["ku_id"] = "units/archives/roma-volume-xix-1941"
    roma[0]["process_ref"] = PROCESS_REF
    roma[0]["resolution_note"] = (
        "Targeted S3 review (2026-10-26): same -> units/archives/roma-volume-xix-1941. "
        "The printed title, volume XIX, and year 1941 uniquely match existing candidate cand-6575 and its periodical-volume KU; p.392 is a locator, not a separate volume identity. "
        "The prior unmapped new group archive-group-6b9a2fe21a09 is retired after this comparison. "
        f"See {PROCESS_REF}."
    )
    new_note = (
        f"source_ref=candidate=cand-12452; candidate_source_ref=chp-21:21_CHP-21Bibliography:l1059-1100#L1096; "
        f"mention=m-chp21-bib-l1059-1100-023-author; group={GROUPS['cand-12452']}; "
        "SBN record EC00021521 gives the title-author form Julius Schlosser Magnino and main-author authority Schlosser, Julius: von, resolving Haskell’s ‘Schlosser-Magnino, J.’ for this publication. No existing person KU matched; identity is limited to this bibliographic authority record. "
        f"S4 mapped to {KU['cand-12452']}; see {PROCESS_REF}."
    )
    rows.append({
        "alignment_id": "aln-12780", "candidate_id": "cand-12452", "ku_id": KU["cand-12452"],
        "external_source": "Biblioteca dell’Accademia dei Concordi SBN", "external_id": "EC00021521",
        "decision": "new", "accessed_date": TODAY, "process_ref": PROCESS_REF,
        "legacy_ku_id": "", "resolution_note": new_note,
    })
    return rows


def update_book_statement_mentions(raw: bytes) -> bytes:
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    changed = []
    targets = {
        "st-chp21-bib-l1059-1100-entry-23": ["cand-12452"],
        "st-chp21-bib-l756-806-entry-10": ["cand-1554", "cand-6411"],
    }
    for raw_line in text.splitlines(keepends=True):
        line_ending = "\r\n" if raw_line.endswith("\r\n") else "\n" if raw_line.endswith("\n") else ""
        line = raw_line[:-len(line_ending)] if line_ending else raw_line
        if not line.strip():
            changed.append(raw_line)
            continue
        record = json.loads(line)
        additions = targets.get(record.get("statement_id"), [])
        if additions:
            mentioned = record.setdefault("qualifiers", {}).setdefault("mentioned_candidate_ids", [])
            for candidate in additions:
                if candidate not in mentioned:
                    mentioned.append(candidate)
            changed.append(json.dumps(record, ensure_ascii=False) + line_ending)
        else:
            changed.append(raw_line)
    out = "".join(changed).encode("utf-8")
    return (b"\xef\xbb\xbf" if bom else b"") + out


def build_changes() -> tuple[dict[Path, bytes], dict[str, int]]:
    changes: dict[Path, bytes] = {}
    cards, enrichments = make_cards()
    for path, content in cards.items():
        if path.exists():
            raise ValueError(f"refusing to overwrite existing unit card {path.relative_to(ROOT)}")
        changes[path] = content

    candidate_file = TABLES / "entity-candidates.csv"
    header, existing, _, _ = read_csv(candidate_file)
    if any(row["candidate_id"] == "cand-12452" for row in existing):
        raise ValueError("cand-12452 already exists")
    candidate_details = {
        "cand-6410": {"detail": "Haskell’s p.158 n.1 attaches Biagi’s introduction to this title. Internet Culturale describes the Mare Magnum manuscript bibliography and its 111-volume form; keep distinct from the printed index and Biagi introduction. The unidentified scholarly work in the adjacent narrative remains cand-6409."},
        "cand-6411": {"detail": "Named as author of Biagi’s introduction; mapped in S3 as a source-local person. Internet Culturale identifies the librarian Guido Biagi as publisher of an index in 1888; no broader biographical identity is asserted."},
        "cand-6412": {"detail": "Haskell p.158 n.1 identifies an introduction by Biagi to Mare Magnum. It remains distinct from the manuscript and printed index; its relation to the index is not formally asserted because the cited note gives no edition or page."},
        "cand-6440": {"detail": "Printed p.436 supplies title, second-edition statement, place, and year; SBN record EC00021521 resolves the form Schlosser-Magnino, J. to Julius von Schlosser. The cited publication and pages were not independently consulted."},
        "cand-6451": {"detail": "Plural avvisi cited at p.160 n.1; Roma XIX (1941), p.392 is mapped to an existing periodical-volume KU. Individual notices remain unnamed and undated."},
        "cand-11394": {"detail": "Haskell’s bibliography at p.429 prints Rome 1882; the Marucelliana inventory and SBN record identify the printed index as Rome 1888. Preserve the year discrepancy and keep this publication distinct from the manuscript and Biagi introduction."},
    }
    changes[candidate_file] = patch_csv_bytes(candidate_file, "candidate_id", candidate_details, [candidate_new_row()])

    mention_file = TABLES / "mentions.csv"
    _, mentions, _, _ = read_csv(mention_file)
    new_mentions = make_new_mentions()
    existing_mention_ids = {row["mention_id"] for row in mentions}
    if any(row["mention_id"] in existing_mention_ids for row in new_mentions):
        raise ValueError("one of the new mention IDs already exists")
    changes[mention_file] = append_csv_bytes(mention_file, new_mentions)

    alignment_file = TABLES / "alignment.csv"
    alignment_header, alignments, bom, newline = read_csv(alignment_file)
    updated_alignments = update_alignment_rows(alignments)
    alignment_updates = {row["alignment_id"]: row for row in updated_alignments if (row["candidate_id"] in set(KU) or row["candidate_id"] == "cand-6452") and row["alignment_id"] != "aln-12780"}
    new_alignment = [row for row in updated_alignments if row["alignment_id"] == "aln-12780"]
    changes[alignment_file] = patch_csv_bytes(alignment_file, "alignment_id", alignment_updates, new_alignment)

    manifest_file = TABLES / "ku-manifest.csv"
    _, manifest, _, _ = read_csv(manifest_file)
    existing_kus = {row["ku_id"] for row in manifest}
    if existing_kus.intersection(KU.values()):
        raise ValueError("at least one target KU already exists in the manifest")
    manifest_rows = []
    types = {"cand-6410": "archive", "cand-6411": "person", "cand-6412": "archive", "cand-6440": "archive", "cand-6451": "archive", "cand-6453": "archive", "cand-0606": "person", "cand-11394": "archive", "cand-12452": "person"}
    names = {"cand-6410": "Mare Magnum", "cand-6411": "Guido Biagi", "cand-6412": "Guido Biagi’s Introduction to the Mare Magnum", "cand-6440": "La letteratura artistica", "cand-6451": "Avvisi cited in Roma, vol. XIX", "cand-6453": "Letter from Jacomo di Castro to Don Antonio Ruffo", "cand-0606": "Jacomo di Castro", "cand-11394": "Index to the Mare Magnum", "cand-12452": "Julius von Schlosser"}
    zh_names = {"cand-6410": "《Mare Magnum》", "cand-6411": "圭多·比亚吉", "cand-6412": "圭多·比亚吉为《Mare Magnum》撰写的导论", "cand-6440": "《艺术文献学》", "cand-6451": "《Roma》第十九卷中的告示", "cand-6453": "雅科莫·迪·卡斯特罗致安东尼奥·鲁福的信", "cand-0606": "雅科莫·迪·卡斯特罗", "cand-11394": "《Mare Magnum索引》", "cand-12452": "尤利乌斯·冯·施洛瑟"}
    for candidate, ku_id in KU.items():
        relpath = "04-knowledge/units/" + ku_id.removeprefix("units/") + ".md"
        manifest_rows.append({"ku_id": ku_id, "type": types[candidate], "canonical_name": zh_names[candidate], "name_en": names[candidate], "source_task": "patrons-and-painters-full-book-s2", "card_path": relpath})
    changes[manifest_file] = append_csv_bytes(manifest_file, manifest_rows)

    accepted = ROOT / "04-knowledge" / "accepted.yml"
    accepted_raw = file_bytes(accepted)
    accepted_bom = accepted_raw.startswith(b"\xef\xbb\xbf")
    accepted_text = accepted_raw.decode("utf-8-sig")
    accepted_newline = "\r\n" if "\r\n" in accepted_text else "\n"
    accepted_lines = accepted_text.splitlines(keepends=True)
    new_unit_lines = {f"- {row['card_path']}" for row in manifest_rows}
    accepted_lines = [line for line in accepted_lines if line.rstrip("\r\n") not in new_unit_lines]
    claims_index = next((index for index, line in enumerate(accepted_lines) if line.rstrip("\r\n") == "claims:"), None)
    if claims_index is None:
        raise ValueError("accepted.yml has no claims section; refusing to append unit paths elsewhere")
    accepted_lines[claims_index:claims_index] = [f"- {row['card_path']}{accepted_newline}" for row in manifest_rows]
    changes[accepted] = (b"\xef\xbb\xbf" if accepted_bom else b"") + "".join(accepted_lines).encode("utf-8")

    enrichment_file = TABLES / "enrichment.jsonl"
    old_enrichment = [json.loads(x) for x in file_bytes(enrichment_file).decode("utf-8-sig").splitlines() if x.strip()]
    existing_enrichment_ids = {row["enrichment_id"] for row in old_enrichment}
    if any(row["enrichment_id"] in existing_enrichment_ids for row in enrichments):
        raise ValueError("one of the new enrichment IDs already exists")
    changes[enrichment_file] = append_text_bytes(enrichment_file, enrichments)

    statements = make_statements()
    statement_file = TABLES / "book-statements.jsonl"
    statement_raw = file_bytes(statement_file)
    existing_statement_ids = {json.loads(x)["statement_id"] for x in statement_raw.decode("utf-8-sig").splitlines() if x.strip()}
    if any(row["statement_id"] in existing_statement_ids for row in statements):
        raise ValueError("one of the new statement IDs already exists")
    changed_statements = update_book_statement_mentions(statement_raw)
    changes[statement_file] = append_text_bytes_from_bytes(changed_statements, statements)

    source_file = TABLES / "sources.csv"
    _, old_sources, _, _ = read_csv(source_file)
    old_source_ids = {row["source_id"] for row in old_sources}
    new_sources = make_new_sources()
    if any(row["source_id"] in old_source_ids for row in new_sources):
        raise ValueError("one of the new source IDs already exists")
    changes[source_file] = append_csv_bytes(source_file, new_sources)

    relation_file = TABLES / "relations.csv"
    _, old_relations, _, _ = read_csv(relation_file)
    new_relations = make_relations()
    old_relation_ids = {row["relation_id"] for row in old_relations}
    natural_keys = {(row["subject_ku_id"], row["object_ku_id"], row["predicate"], row.get("time", "")) for row in old_relations}
    if any(row["relation_id"] in old_relation_ids for row in [{"relation_id": f"rel-{i}", **r} for i, r in zip(range(2247, 2260), new_relations)]):
        raise ValueError("one of the new relation IDs already exists")
    for row in new_relations:
        key = (row["subject_ku_id"], row["object_ku_id"], row["predicate"], row.get("time", ""))
        if key in natural_keys:
            raise ValueError(f"duplicate relation natural key: {key}")
        natural_keys.add(key)
    numbered_relations = [{"relation_id": f"rel-{index}", **row} for index, row in zip(range(2247, 2260), new_relations)]
    changes[relation_file] = append_csv_bytes(relation_file, numbered_relations)

    # Preserve the existing JSONL lines except for the two statement links above.
    changes[statement_file] = changes[statement_file]

    # Cross-table target checks before any write.
    all_kus = existing_kus | set(KU.values())
    for row in numbered_relations:
        if row["subject_ku_id"] not in all_kus or row["object_ku_id"] not in all_kus:
            raise ValueError(f"missing relation endpoint in planned manifest: {row['relation_id']}")
    stats = {"cards": len(cards), "new_candidates": 1, "mapped_existing_new": 8, "new_person_mapping": 1,
             "reused_same": 1, "mentions": len(new_mentions), "statements": len(statements),
             "enrichment_rows": len(enrichments), "sources": len(new_sources), "relations": len(numbered_relations)}
    return changes, stats


def append_text_bytes_from_bytes(raw: bytes, rows: list[dict]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    content = b"".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + newline for row in rows)
    return raw + (b"" if not raw or raw.endswith((b"\n", b"\r")) else newline) + content


def apply(changes: dict[Path, bytes]) -> None:
    originals = {path: path.read_bytes() if path.exists() else None for path in changes}
    staged: dict[Path, Path] = {}
    replaced: list[Path] = []
    try:
        for index, (path, content) in enumerate(changes.items()):
            path.parent.mkdir(parents=True, exist_ok=True)
            temp = path.with_name(f".{path.name}.ch6-batch-{index}.tmp")
            temp.write_bytes(content)
            staged[path] = temp
        for path, temp in staged.items():
            temp.replace(path)
            replaced.append(path)
        for path, content in changes.items():
            if path.read_bytes() != content:
                raise RuntimeError(f"post-write byte check failed: {path.relative_to(ROOT)}")
    except BaseException:
        for path in reversed(replaced):
            original = originals[path]
            if original is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(original)
        for temp in staged.values():
            temp.unlink(missing_ok=True)
        raise
    for temp in staged.values():
        temp.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    changes, stats = build_changes()
    print(json.dumps({"planned": stats, "files": [str(path.relative_to(ROOT)) for path in changes]}, ensure_ascii=False, indent=2))
    if args.apply:
        apply(changes)
        print("apply complete; staged bytes verified")
    else:
        print("dry run only; no files written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
